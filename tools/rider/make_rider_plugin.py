#!/usr/bin/env python3
"""Builds CMB_RiderPose.esp and its AnimTextData: what makes the game play the
seated riding clips while you ride. No Creation Kit needed.

While you ride, the controller script puts the CMB_AnimFlavorRider keyword on
the player (ChangeAnimFlavor). The plugin's additive race adds subgraph entries
to HumanRaceSubGraphData, the way the DLCs and other mods add theirs: a copy of
every third-person MT (weapon holstered) entry for the player, taken from
HumanRaceSubGraphData and from every additive race in your load order (the
Unofficial Patch adds crippled-limb ones), each with the keyword added and the
riding clips searched first:

    Actors\\Character\\Animations\\MT\\CMB_Rider          (CMB_Rider\\Female first for female entries)
    ...then the entry's own folders

The game uses the entry whose keywords all match and that matches the most of
them, so with the keyword on, a copy always beats the entry it copies. HumanRace
itself isn't edited, so race mods such as LooksMenu Customization Compendium
don't conflict.

The game also needs AnimTextData for every entry (normally made by the Creation
Kit's -GenerateAnimInfo). Each copy's files are the copied entry's own vanilla
files, read from your game, with our clips swapped in (see animtextdata.py).
They go to Meshes\\AnimTextData next to the plugin.

Run it again after adding, removing or updating a mod that adds animation
entries for the player (the Unofficial Patch, for example).

Mod Organizer 2 (reads the profile's load order and finds files in mods\\):
  python make_rider_plugin.py --mo2 "C:\\Modding\\MO2" --profile Default \\
      --data "C:\\Steam\\steamapps\\common\\Fallout 4\\Data" --out "C:\\Modding\\MO2\\mods\\Commonwealth Motorbike\\CMB_RiderPose.esp"

Plain Data folder (plugins.txt is in %LOCALAPPDATA%\\Fallout4):
  python make_rider_plugin.py --data "<Fallout 4>\\Data" --plugins-txt "%LOCALAPPDATA%\\Fallout4\\plugins.txt" --out "<Fallout 4>\\Data\\CMB_RiderPose.esp"

Standard library only.
"""

import argparse
import functools
import json
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import animtextdata as T  # noqa: E402

PLUGIN_NAME = "CMB_RiderPose.esp"
FLAVOR_EDID = "CMB_AnimFlavorRider"
PLACEHOLDER_GRAPH = b"CMB_TEMPLATE_PLACEHOLDER\0"
RIDER_FOLDER = "Actors\\Character\\Animations\\MT\\CMB_Rider"
CLIPS_FOLDER = "Meshes\\Actors\\Character\\Animations\\MT\\CMB_Rider"
CLIP_DATA_FILE = "CMB_RiderClips.json"

FALLOUT4 = "fallout4.esm"
HUMAN_RACE = (FALLOUT4, 0x013746)
ANIM_ARCHETYPE_PLAYER = (FALLOUT4, 0x06B508)
KEYWORD_TYPE_ANIM_GENDER = 14

# Always loaded first, in this order, whether or not plugins.txt lists them.
BASE_MASTERS = ["Fallout4.esm", "DLCRobot.esm", "DLCworkshop01.esm", "DLCCoast.esm",
                "DLCworkshop02.esm", "DLCworkshop03.esm", "DLCNukaWorld.esm",
                "DLCUltraHighResolution.esm"]

SUBGRAPH_TYPES = {b"SAKD", b"SGNM", b"SAPT", b"STKD", b"SRAF"}
FLAG_COMPRESSED = 0x40000


# --------------------------------------------------------------------------
# Plugins
# --------------------------------------------------------------------------

def subrecords(data: bytes):
    """Record data -> [(type, bytes)], resolving XXXX size overrides."""
    out, i, big = [], 0, None
    while i < len(data):
        t = data[i:i + 4]
        size = struct.unpack_from("<H", data, i + 4)[0]
        i += 6
        if t == b"XXXX":
            big = struct.unpack_from("<I", data, i)[0]
            i += size
            continue
        if big is not None:
            size, big = big, None
        out.append((t, data[i:i + size]))
        i += size
    return out


def pack_subrecords(subs) -> bytes:
    out = bytearray()
    for t, d in subs:
        if len(d) > 0xFFFF:
            out += b"XXXX" + struct.pack("<HI", 4, len(d)) + t + struct.pack("<H", 0)
        else:
            out += t + struct.pack("<H", len(d))
        out += d
    return bytes(out)


def u32(b: bytes) -> int:
    return struct.unpack("<I", b)[0]


def cstr(b: bytes) -> str:
    return b.rstrip(b"\0").decode("cp1252")


class Plugin:
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        with open(path, "rb") as f:
            head = f.read(24)
            if head[:4] != b"TES4":
                raise SystemExit(f"{path} is not a Fallout 4 plugin")
            size, self.flags = struct.unpack_from("<II", head, 4)
            self.header = head + f.read(size)
        self.masters = [cstr(d) for t, d in subrecords(self.header[24:]) if t == b"MAST"]

    def resolve(self, form_id: int):
        """In-file form ID -> (lowercase owning plugin, object ID)."""
        idx = form_id >> 24
        owner = self.masters[idx] if idx < len(self.masters) else self.name
        return owner.lower(), form_id & 0xFFFFFF

    def groups(self):
        with open(self.path, "rb") as f:
            f.seek(len(self.header))
            while True:
                gh = f.read(24)
                if len(gh) < 24:
                    return
                size = struct.unpack_from("<I", gh, 4)[0]
                yield gh[8:12], gh, f, size

    def records(self, rtype: bytes):
        """(header, decompressed data) for every record in the top-level group `rtype`."""
        for label, gh, f, size in self.groups():
            if label != rtype:
                f.seek(size - 24, 1)
                continue
            group = gh + f.read(size - 24)
            i = 24
            while i < len(group):
                if group[i:i + 4] == b"GRUP":
                    i += struct.unpack_from("<I", group, i + 4)[0]
                    continue
                rsize, flags = struct.unpack_from("<II", group, i + 4)
                data = group[i + 24:i + 24 + rsize]
                if flags & FLAG_COMPRESSED:
                    data = zlib.decompress(data[4:])
                yield group[i:i + 24], data
                i += 24 + rsize
            return

    def form_id(self, header: bytes) -> int:
        return struct.unpack_from("<I", header, 12)[0]


# --------------------------------------------------------------------------
# Load order and files (Mod Organizer 2 or a plain Data folder)
# --------------------------------------------------------------------------

def read_list(path: Path):
    if not path.exists():
        return []
    return [l.strip() for l in path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
            if l.strip() and not l.strip().startswith("#")]


@functools.lru_cache(maxsize=None)
def listing(folder: Path):
    """{lowercase name: path} for a folder, read once. Finding ~150 plugins across
    ~130 mod folders would otherwise list the same folders thousands of times."""
    try:
        return {p.name.lower(): p for p in folder.iterdir()}
    except OSError:
        return {}


def ci_child(folder: Path, name: str):
    """Case-insensitive lookup of one path component (Windows behaviour everywhere)."""
    return listing(folder).get(name.lower())


def ci_path(base: Path, rel: str):
    p = base
    for part in rel.replace("/", "\\").split("\\"):
        if not part:
            continue
        p = ci_child(p, part)
        if p is None:
            return None
    return p


def mo2_directories(instance: Path):
    """mods/profiles/overwrite folders of an MO2 instance (ModOrganizer.ini can move them)."""
    settings = {}
    ini = instance / "ModOrganizer.ini"
    if ini.exists():
        section = None
        for line in ini.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("["):
                section = line.strip("[]").lower()
            elif section == "settings" and "=" in line:
                key, value = line.split("=", 1)
                value = value.strip()
                if value.startswith("@ByteArray(") and value.endswith(")"):
                    value = value[len("@ByteArray("):-1]
                settings[key.strip().lower()] = value.replace("\\\\", "\\")
    base = Path(settings.get("base_directory") or instance)
    dirs = {}
    for name, key in (("mods", "mod_directory"), ("profiles", "profiles_directory"), ("overwrite", "overwrite_directory")):
        value = settings.get(key)
        dirs[name] = Path(value.replace("%BASE_DIR%", str(base))) if value else base / name
    return dirs


class Setup:
    """Active plugins in load order, and the folders that make up the Data folder
    (highest priority first: MO2's overwrite and mods, then the real Data)."""

    def __init__(self, args):
        self.data = args.data
        ccc = read_list(args.data.parent / "Fallout4.ccc") if args.data else []
        if args.mo2:
            dirs = mo2_directories(args.mo2)
            pdir = dirs["profiles"] / args.profile
            if not (pdir / "modlist.txt").exists():
                raise SystemExit(f"no MO2 profile at {pdir}")
            active = {p[1:].lower() for p in read_list(pdir / "plugins.txt") if p.startswith("*")}
            order = read_list(pdir / "loadorder.txt") or [p.lstrip("*") for p in read_list(pdir / "plugins.txt")]
            # modlist.txt: highest priority first; "+" enabled, "-" disabled, "*" unmanaged
            mods = [m[1:] for m in read_list(pdir / "modlist.txt") if m.startswith("+")]
            self.folders = [dirs["overwrite"]] + [dirs["mods"] / m for m in mods] + [args.data]
        else:
            plugins_txt = read_list(args.plugins_txt) if args.plugins_txt else []
            active = {p[1:].lower() for p in plugins_txt if p.startswith("*")}
            order = [p.lstrip("*") for p in plugins_txt]
            self.folders = [args.data]
        # Checked once here: every file lookup walks this list.
        self.folders = [f for f in self.folders if f and f.is_dir()]
        always = BASE_MASTERS + ccc
        always_lower = {m.lower() for m in always}
        names, seen = [], set()
        for n in always + order:
            if n.lower() in seen or n.lower() == PLUGIN_NAME.lower():
                continue
            if n.lower() in active or n.lower() in always_lower:
                seen.add(n.lower())
                names.append(n)
        self.plugins = []
        for n in names:
            path = self.find(n)
            if path:
                self.plugins.append(Plugin(path))
        if not any(p.name.lower() == FALLOUT4 for p in self.plugins):
            raise SystemExit("Fallout4.esm not found; check --data")
        self.order = [p.name.lower() for p in self.plugins]

    def find(self, rel: str):
        for folder in self.folders:
            hit = ci_path(folder, rel)
            if hit:
                return hit
        return None

    def archives(self):
        """BA2 archives in the Data folders, mods' before the game's own."""
        found = []
        for folder in self.folders:
            found += sorted(p for name, p in listing(folder).items() if name.endswith(".ba2"))
        return sorted(found, key=lambda p: p.name.lower().startswith(("fallout4 - ", "dlc")))


# --------------------------------------------------------------------------
# The entries to copy
# --------------------------------------------------------------------------

def entry_ranges(subs):
    ranges, start = [], None
    for i, (t, _) in enumerate(subs):
        if t in SUBGRAPH_TYPES and start is None:
            start = i
        if t == b"SRAF" and start is not None:
            ranges.append((start, i + 1))
            start = None
    return ranges


def winning(plugins, rtype: bytes):
    """{(owner, object id): (plugin, header, data)} for the last plugin with each record."""
    out = {}
    for p in plugins:
        for h, d in p.records(rtype):
            out[p.resolve(p.form_id(h))] = (p, h, d)
    return out


def collect(setup: Setup):
    races = winning(setup.plugins, b"RACE")
    if HUMAN_RACE not in races:
        raise SystemExit("HumanRace not found")
    _, _, human = races[HUMAN_RACE]
    hp = races[HUMAN_RACE][0]
    srac = next((u32(d) for t, d in subrecords(human) if t == b"SRAC"), None)
    target = hp.resolve(srac) if srac else HUMAN_RACE
    sources = []
    for key, (p, h, d) in races.items():
        subs = subrecords(d)
        sadd = next((p.resolve(u32(v)) for t, v in subs if t == b"SADD"), None)
        if key == target or sadd == target:
            edid = next((cstr(v) for t, v in subs if t == b"EDID"), f"{key[1]:06X}")
            sources.append((key != target, setup.order.index(key[0]) if key[0] in setup.order else 0, edid, p, subs))
    sources.sort(key=lambda s: (s[0], s[1]))
    entries = []
    for additive, _, edid, p, subs in sources:
        for a, b in entry_ranges(subs):
            raw = subs[a:b]
            role, persp = struct.unpack_from("<HH", next(d for t, d in raw if t == b"SRAF"))
            kws = [p.resolve(u32(d)) for t, d in raw if t == b"SAKD"]
            if role != 0 or persp != 0 or ANIM_ARCHETYPE_PLAYER not in kws:
                continue
            entries.append(dict(race=edid, plugin=p, raw=raw, keywords=kws,
                                graph=next((cstr(d) for t, d in raw if t == b"SGNM"), ""),
                                paths=[cstr(d) for t, d in raw if t == b"SAPT"]))
    return target, entries


def keyword_info(setup: Setup, keys):
    """{(owner, id): (editor id, type)} for the given keywords (winning versions)."""
    want, out = set(keys), {}
    for p in setup.plugins:
        if not any(k[0] in (p.name.lower(), *[m.lower() for m in p.masters]) for k in want):
            continue
        for h, d in p.records(b"KYWD"):
            key = p.resolve(p.form_id(h))
            if key in want:
                subs = subrecords(d)
                out[key] = (next((cstr(v) for t, v in subs if t == b"EDID"), "?"),
                            next((u32(v) for t, v in subs if t == b"TNAM"), 0))
    return out


# --------------------------------------------------------------------------
# Building the plugin
# --------------------------------------------------------------------------

def rider_paths(paths, female):
    style = paths[0] if paths else RIDER_FOLDER
    low = style.lower()
    lead = style[:low.find("actors\\")] if "actors\\" in low else ""
    tail = "\\" if style.endswith("\\") else ""
    first = [lead + RIDER_FOLDER + "\\Female" + tail] if female else []
    return first + [lead + RIDER_FOLDER + tail]


def build(setup: Setup, template: Path, target, entries, kw_types):
    tpl = Plugin(template)
    if [m.lower() for m in tpl.masters] != [FALLOUT4]:
        raise SystemExit(f"unexpected template masters {tpl.masters}")
    # Masters: the template's Fallout4.esm, plus whatever plugins the copied keywords come from.
    needed = {target[0]} | {k[0] for e in entries for k in e["keywords"]}
    needed |= {e["plugin"].resolve(u32(d))[0] for e in entries for t, d in e["raw"] if t == b"STKD"}
    masters = ["Fallout4.esm"] + [p.name for p in setup.plugins
                                  if p.name.lower() in needed and p.name.lower() != FALLOUT4]
    lower = [m.lower() for m in masters]
    own = len(masters)

    def fid(key):
        return (lower.index(key[0]) << 24) | key[1]

    flavor = next(tpl.resolve(tpl.form_id(h))[1] for h, d in tpl.records(b"KYWD")
                  if any(t == b"EDID" and cstr(v) == FLAVOR_EDID for t, v in subrecords(d)))
    flavor_id = (own << 24) | flavor

    copies, report = [], []
    for e in entries:
        female = any(kw_types.get(k, ("", 0))[1] == KEYWORD_TYPE_ANIM_GENDER for k in e["keywords"])
        new_paths = rider_paths(e["paths"], female) + e["paths"]
        out, added_paths = [], False
        last_kw = max(i for i, (t, _) in enumerate(e["raw"]) if t == b"SAKD")
        for i, (t, d) in enumerate(e["raw"]):
            if t in (b"SAPT", b"SRAF") and not added_paths:
                out += [(b"SAPT", p.encode("cp1252") + b"\0") for p in rider_paths(e["paths"], female)]
                added_paths = True
            if t in (b"SAKD", b"STKD"):
                d = struct.pack("<I", fid(e["plugin"].resolve(u32(d))))
            out.append((t, d))
            if i == last_kw:
                out.append((b"SAKD", struct.pack("<I", flavor_id)))
        copies += out
        report.append(dict(entry=e, female=female, new_paths=new_paths,
                           source_id=T.entry_id(e["graph"], e["paths"]),
                           new_id=T.entry_id(e["graph"], new_paths)))

    # TES4: the template's header with the new master list.
    hsubs = [(t, d) for t, d in subrecords(tpl.header[24:]) if t not in (b"MAST", b"DATA")]
    for m in masters:
        hsubs += [(b"MAST", m.encode("cp1252") + b"\0"), (b"DATA", bytes(8))]
    hdata = pack_subrecords(hsubs)
    out = bytearray(tpl.header[:4] + struct.pack("<I", len(hdata)) + tpl.header[8:24] + hdata)

    for label, gh, f, size in tpl.groups():
        group = gh + f.read(size - 24)
        body, i = bytearray(), 24
        while i < len(group):
            rsize = struct.unpack_from("<I", group, i + 4)[0]
            head, data = bytearray(group[i:i + 24]), group[i + 24:i + 24 + rsize]
            struct.pack_into("<I", head, 12, (own << 24) | (tpl.form_id(head) & 0xFFFFFF))
            if label == b"RACE":
                subs = subrecords(data)
                ranges = entry_ranges(subs)
                if len(ranges) != 1 or not any(d == PLACEHOLDER_GRAPH for t, d in subs[ranges[0][0]:ranges[0][1]]):
                    raise SystemExit("the template's race should hold exactly one placeholder subgraph entry")
                a, b = ranges[0]
                subs = subs[:a] + copies + subs[b:]
                subs = [(t, struct.pack("<I", fid(target)) if t == b"SADD" else d) for t, d in subs]
                data = pack_subrecords(subs)
                struct.pack_into("<I", head, 4, len(data))
            body += head + data
            i += 24 + rsize
        out += gh[:4] + struct.pack("<I", 24 + len(body)) + gh[8:24] + body
    return bytes(out), masters, report


# --------------------------------------------------------------------------
# AnimTextData
# --------------------------------------------------------------------------

class AnimTextSource:
    """Finds the game's AnimTextData files: extracted folders given on the command
    line, then loose files in the Data folders, then BA2 archives."""

    def __init__(self, setup: Setup, extracted):
        self.setup, self.extracted, self._archives = setup, extracted, None

    def _archive_list(self):
        if self._archives is None:
            self._archives = []
            for path in self.setup.archives():
                try:
                    self._archives.append(T.BA2(path))
                except (ValueError, OSError, struct.error):
                    pass
        return self._archives

    def get(self, folder: str, file_id: int):
        name = f"{file_id}.txt"
        for base in self.extracted:
            for rel in (f"{folder}\\{name}", f"meshes\\animtextdata\\{folder}\\{name}"):
                hit = ci_path(base, rel)
                if hit:
                    return hit.read_bytes()
        hit = self.setup.find(f"Meshes\\AnimTextData\\{folder}\\{name}")
        if hit:
            return hit.read_bytes()
        key = f"meshes\\animtextdata\\{folder}\\{name}".lower()
        for archive in self._archive_list():
            if key in archive.files:
                return archive.read(key)
        return None


def write_animtextdata(report, source: AnimTextSource, clips, out_dir: Path):
    written, missing = {}, []
    for r in report:
        if r["new_id"] in written:
            continue
        files = {f: source.get(f, r["source_id"]) for f in T.FOLDERS}
        files = {f: d for f, d in files.items() if d is not None}
        if "AnimationFileData" not in files or "AnimationOffsets" not in files:
            missing.append(r)
            continue
        new = T.riding_entry_files(files, r["new_id"], r["new_paths"][0], clips["female" if r["female"] else "male"])
        used = new.pop("_used")
        for folder, data in new.items():
            path = out_dir / "Meshes" / "AnimTextData" / folder / f"{r['new_id']}.txt"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        written[r["new_id"]] = len(used)
    return written, missing


def load_clips(setup: Setup, clips_dir):
    out = {}
    for sex, sub in (("male", ""), ("female", "\\Female")):
        if clips_dir:
            path = ci_path(clips_dir, (sub.strip("\\") + "\\" if sub else "") + CLIP_DATA_FILE)
        else:
            path = setup.find(f"{CLIPS_FOLDER}{sub}\\{CLIP_DATA_FILE}")
        if not path:
            raise SystemExit(f"{CLIPS_FOLDER}{sub}\\{CLIP_DATA_FILE} not found: install the riding clips first")
        out[sex] = {k.lower(): v for k, v in json.loads(path.read_text()).items()}
    return out


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, required=True, help="the game's Data folder")
    ap.add_argument("--out", type=Path, required=True, help=f"where to write {PLUGIN_NAME} (AnimTextData goes next to it)")
    ap.add_argument("--mo2", type=Path, help="Mod Organizer 2 instance folder (has mods\\ and profiles\\)")
    ap.add_argument("--profile", default="Default", help="MO2 profile name")
    ap.add_argument("--plugins-txt", type=Path, help="plugins.txt, for installs without MO2")
    ap.add_argument("--clips", type=Path, help="the CMB_Rider clip folder (found in the Data folders if omitted)")
    ap.add_argument("--animtextdata", type=Path, nargs="*", default=[],
                    help="folders with extracted vanilla AnimTextData (otherwise read from the BA2 archives)")
    ap.add_argument("--template", type=Path, default=Path(__file__).resolve().parent / "template" / PLUGIN_NAME)
    args = ap.parse_args()
    if args.out.name.lower() != PLUGIN_NAME.lower():
        raise SystemExit(f"the plugin must be called {PLUGIN_NAME} (the controller script looks for that name)")
    if not args.mo2 and not args.plugins_txt:
        print("no --mo2 or --plugins-txt: only the base game and DLC are read")

    setup = Setup(args)
    print(f"{len(setup.plugins)} active plugins")
    target, entries = collect(setup)
    if not entries:
        raise SystemExit("no third-person player MT entries found; nothing to build")
    kw = keyword_info(setup, {k for e in entries for k in e["keywords"]})
    patch, masters, report = build(setup, args.template, target, entries, kw)
    clips = load_clips(setup, args.clips)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(patch)
    print(f"wrote {args.out}  (masters: {', '.join(masters)})")
    for r in report:
        e = r["entry"]
        names = ", ".join(kw.get(k, (f"{k[0]}:{k[1]:06X}", 0))[0] for k in e["keywords"])
        print(f"  + {e['race']} ({e['plugin'].name}): [{names}] + {FLAVOR_EDID}"
              f"{'  female' if r['female'] else ''}  {e['graph'].rsplit(chr(92), 1)[-1]}")

    written, missing = write_animtextdata(report, AnimTextSource(setup, args.animtextdata), clips, args.out.parent)
    print(f"wrote AnimTextData for {len(written)} entries to {args.out.parent / 'Meshes' / 'AnimTextData'}")
    for file_id, used in written.items():
        print(f"  {file_id}.txt  ({used} riding clips)")
    if missing:
        print("MISSING vanilla AnimTextData for these entries (they won't use the riding clips):")
        for r in missing:
            print(f"  Meshes\\AnimTextData\\AnimationFileData\\{r['source_id']}.txt  ({r['entry']['race']}, {r['entry']['graph']})")
        print("Extract Meshes\\AnimTextData from Fallout4 - Animations.ba2 (or the mod that adds the entry) and run")
        print("again with --animtextdata <the folder you extracted it to>.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
