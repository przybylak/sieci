"""Fallout 4 AnimTextData: reading, writing, and building it for new subgraph entries.

The game doesn't search animation folders at run time. For every race subgraph
entry, Meshes\\AnimTextData holds what the Creation Kit worked out ahead of
time (-GenerateAnimInfo), in files named after the entry:

  id = (BSCRC32(lowercase "|".join(animation paths)) << 32) | BSCRC32(lowercase behaviour graph)

BSCRC32 is the standard CRC-32 table with a zero start value and no final xor.
(Checked against all 8 entries of a CK-built mod and 110 vanilla entries.)

  AnimationFileData\\<id>.txt    text: the behaviour graphs and the clip file each name resolves to
  AnimationOffsets\\<id>.txt     binary "V4": per clip length, root-motion keys, rotation keys, events
  AnimationSpeedInfo\\<id>.txt   binary: walk/jog/run speed contours of the graph's nodes
  AnimationStanceData\\<id>.txt  binary: head/chest transforms per stance
  DynamicIdleData\\<id>.txt      text: idle and dialogue clips

A riding entry is a copy of a vanilla entry with the riding folder first, so its
files are the vanilla entry's files with every clip we provide pointed at our
copy and given our clip's root motion and events. Speed and stance data don't
name clips and are copied (our loops keep the vanilla root motion).
"""

import math
import struct
import zlib

# --------------------------------------------------------------------------
# IDs
# --------------------------------------------------------------------------

_TABLE = []
for _n in range(256):
    _c = _n
    for _ in range(8):
        _c = (_c >> 1) ^ 0xEDB88320 if _c & 1 else _c >> 1
    _TABLE.append(_c)


def bscrc32(text: str) -> int:
    c = 0
    for b in text.lower().encode("cp1252"):
        c = _TABLE[(c ^ b) & 0xFF] ^ (c >> 8)
    return c


def entry_id(graph: str, paths) -> int:
    return (bscrc32("|".join(paths)) << 32) | bscrc32(graph)


# --------------------------------------------------------------------------
# AnimationOffsets (V4)
# --------------------------------------------------------------------------

class _Reader:
    def __init__(self, data):
        self.d, self.i = data, 0

    def u32(self):
        v = struct.unpack_from("<I", self.d, self.i)[0]
        self.i += 4
        return v

    def floats(self, n):
        v = struct.unpack_from(f"<{n}f", self.d, self.i)
        self.i += 4 * n
        return list(v)

    def string(self):
        n = self.d[self.i]
        v = self.d[self.i + 1:self.i + 1 + n]
        self.i += 1 + n
        if not v.endswith(b"\0"):
            raise ValueError(f"bad string at {self.i}")
        return v[:-1].decode("cp1252")


def parse_offsets(data: bytes):
    """-> [{graph, mapping: [(name, path)], clips: [{path, duration, translations, rotations, events}]}]

    translations: [t, x, y, z]; rotations: [t, qx, qy, qz, qw]; events: [(t, name)].
    Paths have no extension. Key lists start after t = 0 (the start is implied).
    """
    if not data.startswith(b"V4\n"):
        raise ValueError("not a V4 AnimationOffsets file")
    r = _Reader(data)
    r.i = 3
    sections = []
    while r.i < len(data):
        graph = r.string()
        mapping = [(r.string(), r.string()) for _ in range(r.u32())]
        clips = []
        for _ in range(r.u32()):
            path = r.string()
            duration = r.floats(1)[0]
            trans = [r.floats(4) for _ in range(r.u32())]
            rots = [r.floats(5) for _ in range(r.u32())]
            events = [(r.floats(1)[0], r.string()) for _ in range(r.u32())]
            clips.append(dict(path=path, duration=duration, translations=trans, rotations=rots, events=events))
        sections.append(dict(graph=graph, mapping=mapping, clips=clips))
    return sections


def _string(s: str) -> bytes:
    b = s.encode("cp1252") + b"\0"
    if len(b) > 255:
        raise ValueError(f"path too long for AnimTextData: {s}")
    return bytes([len(b)]) + b


def write_offsets(sections) -> bytes:
    out = bytearray(b"V4\n")
    for s in sections:
        out += _string(s["graph"])
        out += struct.pack("<I", len(s["mapping"]))
        for name, path in s["mapping"]:
            out += _string(name) + _string(path)
        out += struct.pack("<I", len(s["clips"]))
        for c in s["clips"]:
            out += _string(c["path"]) + struct.pack("<f", c["duration"])
            out += struct.pack("<I", len(c["translations"]))
            for k in c["translations"]:
                out += struct.pack("<4f", *k)
            out += struct.pack("<I", len(c["rotations"]))
            for k in c["rotations"]:
                out += struct.pack("<5f", *k)
            out += struct.pack("<I", len(c["events"]))
            for t, name in c["events"]:
                out += struct.pack("<f", t) + _string(name)
    return bytes(out)


# --------------------------------------------------------------------------
# AnimationFileData and DynamicIdleData (text)
# --------------------------------------------------------------------------

def parse_filedata(text: str):
    """-> (version lines, id, [file paths]); the header is '3', '1', id, count."""
    lines = text.split("\n")
    count = int(lines[3])
    return lines[:2], int(lines[2]), lines[4:4 + count]


def write_filedata(header, file_id: int, files) -> str:
    return "\n".join(header + [str(file_id), str(len(files))] + list(files)) + "\n"


def parse_dynamic_idles(text: str):
    lines = text.split("\n")
    if not lines[0].startswith("Version"):
        raise ValueError("not a DynamicIdleData file")
    return lines[0], [l for l in lines[1:] if l]


def write_dynamic_idles(version: str, paths) -> str:
    return "\n".join([version] + list(paths)) + "\n"


# --------------------------------------------------------------------------
# Root motion keys from a clip
# --------------------------------------------------------------------------

def _lerp(a, b, u):
    return [x + (y - x) * u for x, y in zip(a, b)]


def _reduce(times, values, tolerance):
    """Keep the fewest keys (always the last) so that linear interpolation from an
    implied zero at t = 0 stays within `tolerance` of every sample."""
    pts = [(0.0, [0.0] * len(values[0]))] + list(zip(times, values))
    keep = [0, len(pts) - 1]

    def worst(a, b):
        (ta, va), (tb, vb) = pts[a], pts[b]
        best, at = 0.0, None
        for k in range(a + 1, b):
            tk, vk = pts[k]
            u = (tk - ta) / (tb - ta) if tb > ta else 0.0
            err = max(abs(x - y) for x, y in zip(_lerp(va, vb, u), vk))
            if err > best:
                best, at = err, k
        return best, at

    changed = True
    while changed:
        changed = False
        keep.sort()
        for a, b in zip(keep, keep[1:]):
            err, at = worst(a, b)
            if at is not None and err > tolerance:
                keep.append(at)
                changed = True
                break
    keep.sort()
    return [pts[k] for k in keep[1:]]


def clip_record(path: str, duration: float, samples, events, position_tolerance=1.0, rotation_tolerance=0.004):
    """An AnimationOffsets record from root-motion samples [(x, y, z, yaw)] spread
    evenly over the clip (first sample at t = 0), the way the Creation Kit writes it:
    translation keys (t, x, y, z) and yaw as quaternion keys (t, 0, 0, sin, cos), each
    reduced to what linear interpolation needs, always ending on a key at the end."""
    n = len(samples)
    times = [duration * k / (n - 1) for k in range(1, n)] if n > 1 else [duration]
    rest = samples[1:] if n > 1 else samples
    trans = _reduce(times, [list(s[:3]) for s in rest], position_tolerance)
    # Unwrap the yaw so a turn through 180 degrees doesn't jump by a full circle,
    # then reduce the quaternion components the engine interpolates.
    yaw, prev = [], samples[0][3]
    for s in rest:
        y = s[3]
        while y - prev > math.pi:
            y -= 2 * math.pi
        while y - prev < -math.pi:
            y += 2 * math.pi
        yaw.append(y)
        prev = y
    quats = _reduce(times, [[math.sin(y / 2), math.cos(y / 2) - 1.0] for y in yaw], rotation_tolerance)
    rots = []
    for t, (z, w) in quats:
        w += 1.0
        norm = math.hypot(z, w) or 1.0
        rots.append([t, 0.0, 0.0, z / norm, w / norm])
    return dict(path=path, duration=duration,
                translations=[[t] + list(v) for t, v in trans], rotations=rots,
                events=[(t, name) for t, name in events])


# --------------------------------------------------------------------------
# Files for a riding entry
# --------------------------------------------------------------------------

FOLDERS = ("AnimationFileData", "AnimationOffsets", "AnimationSpeedInfo", "AnimationStanceData", "DynamicIdleData")


def _swap(path: str, folder: str, clips, with_extension: bool):
    """`path` pointed at the riding folder if it names one of our clips, else unchanged."""
    name = path.replace("/", "\\").rsplit("\\", 1)[-1]
    stem = name[:-4] if with_extension and name.lower().endswith(".hkx") else name
    if stem.lower() not in clips:
        return path, None
    return folder + "\\" + name, stem.lower()


def riding_entry_files(source: dict, new_id: int, rider_folder: str, clips: dict) -> dict:
    """AnimTextData for a riding copy of a vanilla entry.

    source: {folder name: bytes} of the vanilla entry (AnimationFileData and
            AnimationOffsets required, the rest copied when present).
    rider_folder: where our clips are, as written in the entry's paths
            (e.g. Actors\\Character\\Animations\\MT\\CMB_Rider).
    clips: {lowercase clip name: record from CMB_RiderClips.json}.
    Returns {folder name: bytes} for the new id.
    """
    out = {}
    header, _, files = parse_filedata(source["AnimationFileData"].decode("cp1252"))
    used = set()
    new_files = []
    for f in files:
        if "\\behaviors\\" in f.lower():
            new_files.append(f)
            continue
        swapped, name = _swap(f, rider_folder, clips, True)
        new_files.append(swapped)
        if name:
            used.add(name)
    out["AnimationFileData"] = write_filedata(header, new_id, new_files).encode("cp1252")

    sections = parse_offsets(source["AnimationOffsets"])
    # The Creation Kit writes event names the way the behaviour graph spells them
    # (startAllowRotation in a clip becomes StartAllowRotation).
    spelling = {}
    for s in sections:
        for c in s["clips"]:
            for _, ev in c["events"]:
                spelling.setdefault(ev.lower(), ev)
    for s in sections:
        s["mapping"] = [(name, _swap(path, rider_folder, clips, False)[0]) for name, path in s["mapping"]]
        for c in s["clips"]:
            path, name = _swap(c["path"], rider_folder, clips, False)
            if not name:
                continue
            rec = clips[name]
            used.add(name)
            c.update(path=path, duration=rec["duration"], translations=rec["translations"],
                     rotations=rec["rotations"],
                     events=[(t, spelling.get(ev.lower(), ev)) for t, ev in rec["events"]])
    out["AnimationOffsets"] = write_offsets(sections)

    if "DynamicIdleData" in source:
        version, paths = parse_dynamic_idles(source["DynamicIdleData"].decode("cp1252"))
        new_paths = []
        for p in paths:
            swapped, name = _swap(p, rider_folder, clips, False)
            new_paths.append(swapped)
            if name:
                used.add(name)
        out["DynamicIdleData"] = write_dynamic_idles(version, new_paths).encode("cp1252")
    for folder in ("AnimationSpeedInfo", "AnimationStanceData"):
        if folder in source:
            out[folder] = source[folder]
    out["_used"] = used
    return out


# --------------------------------------------------------------------------
# BA2 archives (general type), to read the game's own AnimTextData
# --------------------------------------------------------------------------

class BA2:
    """Read-only access to a Fallout 4 'GNRL' BA2 (versions 1, 7 and 8 share a layout)."""

    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            head = f.read(24)
            magic, version, kind, count, names_at = struct.unpack("<4sI4sIQ", head)
            if magic != b"BTDX" or kind != b"GNRL":
                raise ValueError(f"{path}: not a general BA2")
            extra = {2: 8, 3: 12}.get(version, 0)  # Starfield-era headers are longer
            f.seek(24 + extra)
            entries = [struct.unpack("<I4sIIQIII", f.read(36)) for _ in range(count)]
            f.seek(names_at)
            names = []
            for _ in range(count):
                n = struct.unpack("<H", f.read(2))[0]
                names.append(f.read(n).decode("cp1252").replace("/", "\\").lower())
        self.files = {name: (e[4], e[5], e[6]) for name, e in zip(names, entries)}

    def read(self, name):
        offset, packed, size = self.files[name.replace("/", "\\").lower()]
        with open(self.path, "rb") as f:
            f.seek(offset)
            data = f.read(packed or size)
        return zlib.decompress(data) if packed else data
