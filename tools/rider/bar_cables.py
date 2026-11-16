#!/usr/bin/env python3
"""The bars' cables (build 2026-11-15b; test 53's wish (c): "cables that should be attached to handlebar on the right
side weren't, those are just floating, left side was fine").

The cause, read off the built nifs (2026-11-10a's, unchanged since): harley_meshes.role_of gives each connected piece of
the model one role by its centre, and the right-hand cables' centres lie on the frame, so the whole of each cable went
into the fixed shape static_black while its end is clamped to the right bar. The plugin turns the bar assembly (the
shapes named *_front_*) about SteerAxis and leaves static_black where it is: the cable's bar end stays behind in the air
as the bars turn (the right switch housing is 25-28 from the steering axis: 7.8 at 16 degrees, 9.8 at BarAngle 20), in
the worn nifs (third person, where the hand and the distance hide it) and in the view nif (first person, in front of the
eye). The left cable lies whole in front_black and turns with the bars. Three pieces of static_black hang from the
bars, all on the right: the two throttle cables from under the right switch housing (forward round the steering head,
then back along the frame to the throttle body) and the wire from the right bar's riser (down the front of the frame and
under the engine).

The fix, on the built nifs (no glTF needed, so no new UVs, bakes or textures): each such cable is cut where it passes
nearest the steering axis (6.7-8.7 from it, in front of the steering head, behind the headlamp shell), the bar side moved out
of static_black into a new shape <stem>_front_cables ("_front_": the plugin's bar assembly by its name, [Parts]
RolesByName, and by its culling sphere ahead of FrontMinY with RolesByName=0), the far side left where it is. The new
shape is static_black's own vertices (their records copied byte for byte: position, UV, normal, tangent, skin weights)
under static_black's materials file, so its UVs stay valid on static_black's texture atlas (every shape has its own
baked atlas: moving the triangles into front_black would have sampled the wrong texels). It gets its own copies of
static_black's shader property and texture set and, in the worn nifs, of its skin instance and bone data (one bone, as
every bike shape: the plugin moves a shape by its own bone data), a culling sphere of its own (harley_meshes.sphere_of,
through static_black's skin-to-bone map) and a model bound. static_black keeps its whole vertex list (the moved part's
vertices stay in it unused) and loses the moved triangles. At the cut both sides share their ring of vertices, so with
the bars straight nothing changes on screen; turned, the cut opens by 2 r sin(angle/2) with r its distance from the
axis (at most 2.6 at 16 degrees, 3.2 at BarAngle 20), out of sight behind the headlamp, where a real cable flexes.

Which nifs: the three worn nifs (CMB_BikeWorn, CMB_BikeWornRider, CMB_BikeWornRiderF) and the view nif (CMB_BikeView),
the ones whose bars the plugin turns. The parked nif is left as it is (the plugin never moves the parked bike), and
CMB_BikeParts.ini is not touched (no key moves). Every block of a nif but static_black's shape and the node that holds
the shapes is written back byte for byte; the new blocks go after the last one and the new name after the last string.

  python bar_cables.py --data <Data> --out <folder> [--bar-cables 1|0] [--pynifly <io_scene_nifly>]

--data is a built Data tree (its Meshes/CMB: the four nifs and CMB_BikeParts.ini); the fixed nifs are written to --out
(a folder of their own, e.g. a package overlay's Data/Meshes/CMB, or Meshes/CMB itself: a nif already split is left
as it is). The cables are found on the view nif (full-precision positions) and the same triangles are moved in every
nif, whose static_black must be the view nif's (the same triangles, every vertex within its half-float rounding).
--bar-cables 0 writes the four nifs as they are (2026-11-15a's, byte for byte). --pynifly also reads each output back
through PyNifly (the shapes, their names and order, the moved triangles' corners and UVs). Exit status 1 when a check
fails or the cables found are not the three expected (--expect).
"""

import argparse
import hashlib
import math
import os
import struct
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harley_meshes as H  # noqa: E402
from nearest import TriangleGrid  # noqa: E402

LABEL = "front_cables"      # the new shape's label: "_front_" turns it with the bars (CMB_Slope.c g_roleTags)
SOURCE = "static_black"     # the fixed shape the cables are cut out of (and whose materials file the new shape names)
NIFS = ("CMB_BikeWorn", "CMB_BikeWornRider", "CMB_BikeWornRiderF", H.VIEW_NODE)   # the bikes the plugin turns the bars of
FIND_IN = H.VIEW_NODE       # the cables are found on this nif's full-precision positions
# A bar cable: a piece of a fixed shape with a bar end (ATTACH or nearer to the bar assembly's surface, at least R_END
# from the steering axis, at least MIN_SEEDS such vertices), long and thin (MIN_LENGTH along its surface from the bar
# end, its cross-section's median radius MAX_RADIUS or less) and fixed at its far end (FAR_GAP or more from the bar
# assembly). Measured on the 2026-11-10a nifs: the three cables' bar ends (20-86 vertices each) 0.00-0.04 from the
# bars and 17.4-28.1 from the axis, 92-152 long, radius 0.20-0.62, their far ends 37-70 from the bars; the only other
# pieces with such a vertex (a frame tube by the lower clamp, a wiring loop round the steering head) have one each,
# 12.5-13 from the axis, and are thick (radius 2.1, 8.8) or short (29.5, its far end 5 from the bars).
ATTACH = 0.5
R_END = 12.0
MIN_SEEDS = 3
MIN_LENGTH = 40.0
MAX_RADIUS = 1.5
FAR_GAP = 10.0
SLICE = 1.0                 # the cut's search: slices this long along the cable
CUT_MARGIN = 3.0            # the cut at least this much nearer the axis than the bar end (else nothing to gain)
EXPECT = 3                  # the cables the 2026-11-10a nifs have (--expect)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_file(path: Path, data: bytes):
    """Through a new file in the same folder, then renamed over the old name: a link there is replaced, never written
    through (a tree of links to a package's files keeps them as they are), and a run cut short leaves no half file."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        mask = os.umask(0)
        os.umask(mask)
        os.chmod(tmp, 0o666 & ~mask)   # as a plain write would leave it (mkstemp's is 0600)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


# --- a Fallout 4 nif (20.2.0.7, bsver 130), as blocks of bytes ------------------------------------------------------

class Nif:
    """The header's lists, the blocks as bytes and the footer; write() gives the same bytes back for a nif not edited."""

    def __init__(self, data: bytes):
        i = data.index(b"\n") + 1
        version, endian, user = struct.unpack_from("<IBI", data, i)
        if version != 0x14020007 or endian != 1 or user != 12:
            raise ValueError(f"not a Fallout 4 nif (version {version:#x}, user version {user})")
        i += 9
        self.prefix = data[:i]
        nblocks, self.bsver = struct.unpack_from("<II", data, i)
        if self.bsver != 130:
            raise ValueError(f"not a Fallout 4 nif (bs version {self.bsver})")
        i += 8
        j = i
        for _ in range(4):   # author, process script, export script, max filepath
            j += 1 + data[j]
        self.bs_strings = data[i:j]
        i = j
        ntypes = struct.unpack_from("<H", data, i)[0]
        i += 2
        self.types = []
        for _ in range(ntypes):
            n = struct.unpack_from("<I", data, i)[0]
            self.types.append(data[i + 4:i + 4 + n].decode("ascii"))
            i += 4 + n
        self.type_idx = list(struct.unpack_from(f"<{nblocks}H", data, i))
        i += 2 * nblocks
        sizes = struct.unpack_from(f"<{nblocks}I", data, i)
        i += 4 * nblocks
        nstrings, self.max_len = struct.unpack_from("<II", data, i)
        i += 8
        self.strings = []
        for _ in range(nstrings):
            n = struct.unpack_from("<I", data, i)[0]
            self.strings.append(data[i + 4:i + 4 + n])
            i += 4 + n
        ngroups = struct.unpack_from("<I", data, i)[0]
        self.groups = data[i:i + 4 + 4 * ngroups]
        i += 4 + 4 * ngroups
        self.blocks = []
        for size in sizes:
            self.blocks.append(data[i:i + size])
            i += size
        self.footer = data[i:]
        if len(self.blocks[-1]) != sizes[-1]:
            raise ValueError("the blocks run past the end of the file")

    def write(self) -> bytes:
        out = [self.prefix, struct.pack("<II", len(self.blocks), self.bsver), self.bs_strings,
               struct.pack("<H", len(self.types))]
        out += [struct.pack("<I", len(t)) + t.encode("ascii") for t in self.types]
        out.append(struct.pack(f"<{len(self.type_idx)}H", *self.type_idx))
        out.append(struct.pack(f"<{len(self.blocks)}I", *(len(b) for b in self.blocks)))
        out.append(struct.pack("<II", len(self.strings), self.max_len))
        out += [struct.pack("<I", len(s)) + s for s in self.strings]
        out += [self.groups] + self.blocks + [self.footer]
        return b"".join(out)

    def type_of(self, k):
        return self.types[self.type_idx[k] & 0x7FFF]

    def add_block(self, type_name, data):
        if type_name not in self.types:
            raise ValueError(f"no {type_name} block in the nif to copy")
        self.type_idx.append(self.types.index(type_name))
        self.blocks.append(bytes(data))
        return len(self.blocks) - 1

    def add_string(self, s: str):
        b = s.encode("ascii")
        if b in self.strings:
            raise ValueError(f"the string {s!r} is in the nif already")
        self.strings.append(b)
        self.max_len = max(self.max_len, len(b))
        return len(self.strings) - 1

    def name_of(self, k):   # NiObjectNET's name (a string index) at the block's start
        idx = struct.unpack_from("<i", self.blocks[k], 0)[0]
        return self.strings[idx].decode("ascii") if 0 <= idx < len(self.strings) else None

    def shapes(self):
        return [k for k in range(len(self.blocks)) if self.type_of(k) == "BSTriShape"]

    def shape_named(self, name):
        hits = [k for k in self.shapes() if self.name_of(k) == name]
        return hits[0] if len(hits) == 1 else None


def node_children(block: bytes):
    """A Fallout 4 NiNode's (or BSFadeNode's) children: (the offset of the count, the refs). No effects list at bsver 130."""
    n_extra = struct.unpack_from("<I", block, 4)[0]
    at = 72 + 4 * n_extra
    n = struct.unpack_from("<I", block, at)[0]
    if len(block) != at + 4 + 4 * n:
        raise ValueError("an NiNode of an unexpected size")
    return at, list(struct.unpack_from(f"<{n}i", block, at + 4))


def with_child(block: bytes, child: int) -> bytes:
    at, kids = node_children(block)
    kids.append(child)
    return block[:at] + struct.pack(f"<I{len(kids)}i", len(kids), *kids)


class TriShape:
    """A Fallout 4 BSTriShape's fields: NiAVObject (72 bytes, no extra data), the bound, the three refs, the vertex
    description, the counts, the vertex records and the triangles."""

    def __init__(self, block: bytes):
        if struct.unpack_from("<I", block, 4)[0] != 0:
            raise ValueError("a BSTriShape with extra data")
        self.head = block[:72]
        self.bound = struct.unpack_from("<4f", block, 72)
        self.skin, self.shader, self.alpha = struct.unpack_from("<3i", block, 88)
        self.desc = struct.unpack_from("<Q", block, 100)[0]
        ntris = struct.unpack_from("<I", block, 108)[0]
        nverts = struct.unpack_from("<H", block, 112)[0]
        size = struct.unpack_from("<I", block, 114)[0]
        self.vsize = (self.desc & 0xF) * 4
        if size != nverts * self.vsize + 6 * ntris or len(block) != 118 + size:
            raise ValueError("a BSTriShape of an unexpected size")
        self.records = np.frombuffer(block, np.uint8, nverts * self.vsize, 118).reshape(nverts, self.vsize)
        self.tris = np.frombuffer(block, "<u2", 3 * ntris, 118 + nverts * self.vsize).reshape(ntris, 3).astype(np.int64)
        self.full = bool((self.desc >> 44) & 0x400)

    def positions(self, records=None):
        r = self.records if records is None else records
        if self.full:
            return np.ascontiguousarray(r[:, :12]).view("<f4").astype(np.float64)
        return np.ascontiguousarray(r[:, :6]).view("<f2").astype(np.float64)

    def uvs(self):
        at = ((self.desc >> 8) & 0xF) * 4
        return np.ascontiguousarray(self.records[:, at:at + 4]).view("<f2").astype(np.float64)

    def pack(self, head=None, bound=None, refs=None, records=None, tris=None) -> bytes:
        head = self.head if head is None else head
        bound = self.bound if bound is None else bound
        skin, shader, alpha = (self.skin, self.shader, self.alpha) if refs is None else refs
        records = self.records if records is None else records
        tris = self.tris if tris is None else tris
        if len(records) > 0xFFFF or (len(tris) and tris.max() >= len(records)):
            raise ValueError("vertex indices out of range")
        body = records.tobytes() + np.asarray(tris, "<u2").tobytes()
        return (head + struct.pack("<4f3iQIHI", *bound, skin, shader, alpha, self.desc, len(tris), len(records), len(body))
                + body)


def shape_geometry(nif: Nif, name: str):
    k = nif.shape_named(name)
    if k is None:
        return None
    s = TriShape(nif.blocks[k])
    return s.positions(), s.tris


# --- finding the cables -------------------------------------------------------------------------------------------

def parts_file(path: Path):
    keys = {}
    for line in path.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith(";"):
            k, v = line.split("=", 1)
            keys[k.strip()] = v.strip()
    sp = np.array([float(x) for x in keys["SteerPoint"].split(",")])
    ax = H.unit(np.array([float(x) for x in keys["SteerAxis"].split(",")]))
    return sp, ax, float(keys.get("BarAngle", "20"))


def axis_distance(p, sp, ax):
    r = np.asarray(p, np.float64) - sp
    return np.linalg.norm(r - np.outer(r @ ax, ax), axis=1)


def kink(r, deg):
    """How far a point r from the steering axis moves when the bars turn deg."""
    return 2.0 * np.asarray(r) * math.sin(math.radians(abs(deg)) / 2.0)


def geodesic(points, tris, seeds):
    """The shortest distance along the mesh's edges from the seed vertices to every vertex (Dijkstra)."""
    import heapq
    e = np.vstack([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]])
    e = np.unique(np.sort(e, axis=1), axis=0)
    w = np.linalg.norm(points[e[:, 0]] - points[e[:, 1]], axis=1)
    adj = [[] for _ in range(len(points))]
    for (a, b), d in zip(e.tolist(), w.tolist()):
        adj[a].append((b, d))
        adj[b].append((a, d))
    dist = np.full(len(points), np.inf)
    heap = []
    for i in seeds:
        dist[i] = 0.0
        heap.append((0.0, int(i)))
    heapq.heapify(heap)
    while heap:
        d, i = heapq.heappop(heap)
        if d > dist[i]:
            continue
        for j, wj in adj[i]:
            nd = d + wj
            if nd < dist[j]:
                dist[j] = nd
                heapq.heappush(heap, (nd, j))
    return dist


def near_surface(grid, points, limit):
    """The distance from each point to the grid's triangles where it is limit or less, else inf. Only the points with
    a filed cell within limit are searched (TriangleGrid.closest widens its box till it finds a triangle, which costs
    a search of most of the grid for a point far from all of them)."""
    p = np.asarray(points, np.float64)
    out = np.full(len(p), np.inf)
    if not len(p):
        return out
    lo, hi = grid._cells(p - limit), grid._cells(p + limit)
    _, cx, cy, cz = grid._expand(lo, hi)
    box = np.repeat(np.arange(len(p)), (hi - lo + 1).prod(axis=1))
    filed = np.isin(grid._key(cx, cy, cz), grid.keys)
    inside = np.all((p >= grid.origin - limit) & (p <= grid.origin + grid.dims * grid.cell + limit), axis=1)
    cand = np.zeros(len(p), bool)
    cand[box[filed]] = True
    cand &= inside
    if cand.any():
        d = grid.closest(p[cand], reach=max(limit, grid.cell))[2]
        out[np.where(cand)[0][d <= limit]] = d[d <= limit]
    return out


def find_bar_cables(v, t, bar_tris, sp, ax, bar_angle, verbose=True, name=SOURCE):
    """The bar cables among a fixed shape's pieces (v (n,3) full precision, t (m,3)), the bar assembly's triangles
    (k,3,3). Returns a list of dicts: the piece's triangles, the moved ones (the bar side of the cut) and the numbers."""
    key = np.round(np.asarray(v, np.float64) * 1024.0).astype(np.int64)   # weld the UV seams' copies
    uniq, first, weld = np.unique(key, axis=0, return_index=True, return_inverse=True)
    weld = weld.reshape(-1)
    P = np.asarray(v, np.float64)[first]
    tw = weld[t]
    count, lab = H.components(len(P), tw)
    tri_lab = lab[tw[:, 0]]
    bar_grid = TriangleGrid(bar_tris, 2.0)
    bar_points = np.unique(bar_tris.reshape(-1, 3), axis=0)
    blo, bhi = bar_tris.min(axis=(0, 1)) - ATTACH, bar_tris.max(axis=(0, 1)) + ATTACH
    out = []
    for c in range(count):
        ti = np.where(tri_lab == c)[0]
        if not len(ti):
            continue
        vi = np.unique(tw[ti])
        p = P[vi]
        if not np.all((p.max(axis=0) >= blo) & (p.min(axis=0) <= bhi)):
            continue
        d_bar = near_surface(bar_grid, p, ATTACH)
        r = axis_distance(p, sp, ax)
        seeds = np.where((d_bar <= ATTACH) & (r >= R_END))[0]
        if not len(seeds):
            continue
        lt = np.searchsorted(vi, tw[ti])   # the piece's own vertex numbers
        s = geodesic(p, lt, seeds)
        length = float(s[np.isfinite(s)].max())
        bins = np.floor(s / 2.0).astype(np.int64)
        radii = []
        for b in np.unique(bins):
            q = p[bins == b]
            if len(q) >= 3:
                radii.append(float(np.linalg.norm(q - q.mean(axis=0), axis=1).max()))
        radius = float(np.median(radii)) if radii else math.inf
        far = s >= length - 2.0
        far_gap = float(np.sqrt(((p[far][:, None, :] - bar_points[None]) ** 2).sum(axis=2).min()))
        info = dict(piece=c, tris=ti, seeds=len(seeds), seed_r=(float(r[seeds].min()), float(r[seeds].max())),
                    seed_x=float(p[seeds, 0].mean()),
                    length=length, radius=radius, far_gap=far_gap, far=p[far].mean(axis=0))
        reasons = []
        if len(seeds) < MIN_SEEDS:
            reasons.append(f"{len(seeds)} bar-end vertices (fewer than {MIN_SEEDS})")
        if length < MIN_LENGTH:
            reasons.append(f"{length:.1f} long (under {MIN_LENGTH:g})")
        if radius > MAX_RADIUS:
            reasons.append(f"radius {radius:.2f} (over {MAX_RADIUS:g})")
        if far_gap < FAR_GAP:
            reasons.append(f"its far end {far_gap:.1f} from the bars (under {FAR_GAP:g})")
        # the cut: the slice whose centre passes nearest the steering axis
        sb = np.floor(s / SLICE).astype(np.int64)
        best = None
        for b in np.unique(sb):
            q = p[sb == b]
            rc = float(axis_distance(q.mean(axis=0)[None], sp, ax)[0])
            if best is None or rc < best[1]:
                best = (b, rc)
        cut_s = (best[0] + 0.5) * SLICE
        if best[1] > info["seed_r"][0] - CUT_MARGIN:
            reasons.append(f"nearest the axis {best[1]:.1f} at {cut_s:.1f} along it: no nearer than its bar end")
        moved = s[lt].mean(axis=1) < cut_s
        ring = np.unique(lt[moved])
        ring = np.intersect1d(ring, np.unique(lt[~moved]))   # the vertices both sides share
        info.update(cut_s=cut_s, cut_r=best[1], cut_at=p[sb == best[0]].mean(axis=0), moved=ti[moved],
                    ring_r=float(axis_distance(p[ring], sp, ax).max()) if len(ring) else 0.0, ring=len(ring),
                    bar_gap=float(kink(r[seeds], bar_angle).max()), reasons=reasons,
                    near_bar=float(d_bar.min()))
        if verbose:
            print(f"  {name} piece {c}: {len(ti)} triangles, {len(seeds)} vertices at the bars ({info['near_bar']:.2f} from "
                  f"them, {info['seed_r'][0]:.1f}-{info['seed_r'][1]:.1f} from the steering axis), {length:.1f} long, "
                  f"radius {radius:.2f}, its far end {far_gap:.1f} from the bars at ({info['far'][0]:.1f}, {info['far'][1]:.1f}, "
                  f"{info['far'][2]:.1f}): " + ("NOT a bar cable: " + "; ".join(reasons) if reasons else "a bar cable"))
        if not reasons:
            out.append(info)
    return out


# --- the split ----------------------------------------------------------------------------------------------------

def clearances(v, t, cables, fixed, bar_tris, sp, ax, bar, step=2.0, limit=3.0):
    """With the bars anywhere within BarAngle (every step degrees): the moved part against each fixed shape (the cut
    cables' fixed rest aside: at the cut they part by the kink), and, for comparison, the bar assembly against the
    same cables left whole and fixed (2026-11-15a). Printed; gaps over limit read "clear"."""
    angles = np.unique(np.r_[np.arange(-bar, bar, step), bar])
    rest = np.ones(len(t), bool)
    for _, c in cables:
        rest[c["tris"]] = False
    pts = v[np.unique(t[np.concatenate([c["moved"] for _, c in cables])])]
    turned = [(deg, (pts - sp) @ H.axis_rotation(ax, deg).T + sp) for deg in angles]
    lines = []
    for label, (fv, ft) in fixed.items():
        tris = fv[ft[rest]] if label == SOURCE else fv[ft]
        near = np.all((tris.max(axis=1) > pts.min(axis=0) - 30) & (tris.min(axis=1) < pts.max(axis=0) + 30), axis=1)
        if not near.any():
            continue
        grid = TriangleGrid(tris[near], 2.0)
        best = (np.inf, 0.0)
        for deg, q in turned:
            d = near_surface(grid, q, limit).min()
            best = min(best, (d, deg))
        if np.isfinite(best[0]):
            lines.append(f"{label} {best[0]:.2f} (at {best[1]:+.0f})")
    print("the moved part with the bars within BarAngle, its least gap to each fixed shape within " + f"{limit:g}: "
          + ("; ".join(lines) if lines else "none") + f" (the cut cables' fixed rest aside: at the cut they part by the kink)")
    old = []
    for _, c in cables:
        grid = TriangleGrid(v[t[c["tris"]]], 2.0)
        best = (np.inf, 0.0)
        for deg in angles:
            q = (bar_tris.reshape(-1, 3) - sp) @ H.axis_rotation(ax, deg).T + sp
            best = min(best, (near_surface(grid, q, limit).min(), deg))
        old.append(f"piece {c['piece']} {best[0]:.2f} (at {best[1]:+.0f})")
    print("for comparison, the same cables left whole and fixed (2026-11-15a): the bar assembly turned within BarAngle comes "
          "within " + "; ".join(old) + " of them (it passes through them)")


def sphere_of(points):
    return H.sphere_of(np.asarray(points, np.float64))


def bound_of(points):
    """A model bound round the points: the box's centre, the farthest point's distance (float32)."""
    p = np.asarray(points, np.float64)
    c = (p.min(axis=0) + p.max(axis=0)) / 2.0
    return (*np.float32(c).tolist(), float(np.float32(np.linalg.norm(p - c, axis=1).max() * (1 + 1e-6))))


def split(data: bytes, stem: str, moved_tris: np.ndarray, bound):
    """The nif with static_black's moved triangles in a new shape <stem>_front_cables. Returns (bytes, report)."""
    nif = Nif(data)
    if nif.write() != data:
        raise ValueError(f"{stem}: the nif doesn't read back to its own bytes")
    if nif.shape_named(f"{stem}_{LABEL}") is not None:
        return data, "already split: left as it is"
    k = nif.shape_named(f"{stem}_{SOURCE}")
    if k is None:
        raise ValueError(f"{stem}: no {stem}_{SOURCE}")
    parents = [b for b in range(len(nif.blocks)) if nif.type_of(b) in ("NiNode", "BSFadeNode") and k in node_children(nif.blocks[b])[1]]
    if len(parents) != 1:
        raise ValueError(f"{stem}: {SOURCE} under {len(parents)} nodes")
    parent = parents[0]
    s = TriShape(nif.blocks[k])
    keep = np.ones(len(s.tris), bool)
    keep[moved_tris] = False
    used = np.unique(s.tris[moved_tris])
    remap = np.full(len(s.records), -1, np.int64)
    remap[used] = np.arange(len(used))
    new_tris = remap[s.tris[moved_tris]]
    records = s.records[used]
    # the source's shader property and texture set (and its alpha property, if it had one), copied
    shader = nif.blocks[s.shader]
    tex_ref = struct.unpack_from("<i", shader, 40)[0]
    if nif.type_of(s.shader) != "BSLightingShaderProperty" or not (0 <= tex_ref < len(nif.blocks)) \
            or nif.type_of(tex_ref) != "BSShaderTextureSet" or struct.unpack_from("<I", shader, 8)[0] != 0:
        raise ValueError(f"{stem}: {SOURCE}'s shader property isn't laid out as expected")
    name_idx = nif.add_string(f"{stem}_{LABEL}")
    head = struct.pack("<i", name_idx) + s.head[4:]
    order = []   # the new blocks, in harley_meshes' order: the shape, its skin, its shader, its texture set
    shape_k = len(nif.blocks)
    skin_k = data_k = -1
    n_new = 1 + (2 if s.skin >= 0 else 0) + 2 + (1 if s.alpha >= 0 else 0)
    next_k = shape_k + 1
    if s.skin >= 0:
        skin_k, data_k = next_k, next_k + 1
        next_k += 2
    shader_k, tex_k = next_k, next_k + 1
    next_k += 2
    alpha_k = next_k if s.alpha >= 0 else -1
    lines = []
    shape_block = s.pack(head=head, bound=bound, refs=(skin_k, shader_k, alpha_k), records=records, tris=new_tris)
    order.append(("BSTriShape", shape_block))
    if s.skin >= 0:
        inst = bytearray(nif.blocks[s.skin])
        root, dref, nbones = struct.unpack_from("<iiI", inst, 0)
        if nif.type_of(s.skin) != "BSSkin::Instance" or nbones != 1 or nif.type_of(dref) != "BSSkin::BoneData":
            raise ValueError(f"{stem}: {SOURCE}'s skin isn't one bone")
        struct.pack_into("<i", inst, 4, data_k)
        bone = bytearray(nif.blocks[dref])
        if struct.unpack_from("<I", bone, 0)[0] != 1 or len(bone) != 72:
            raise ValueError(f"{stem}: {SOURCE}'s bone data isn't one bone")
        rot = np.array(struct.unpack_from("<9f", bone, 20), np.float64).reshape(3, 3)
        trans = np.array(struct.unpack_from("<3f", bone, 56), np.float64)
        centre, radius = sphere_of(s.positions(records))
        struct.pack_into("<4f", bone, 4, *(rot @ centre + trans), radius)
        order += [("BSSkin::Instance", inst), ("BSSkin::BoneData", bone)]
        lines.append(f"culling sphere ({centre[0]:.1f}, {centre[1]:.1f}, {centre[2]:.1f}) r {radius:.1f} in the bike's space")
    shader2 = bytearray(shader)
    struct.pack_into("<i", shader2, 40, tex_k)
    order += [("BSLightingShaderProperty", shader2), ("BSShaderTextureSet", nif.blocks[tex_ref])]
    if s.alpha >= 0:
        order.append(("NiAlphaProperty", nif.blocks[s.alpha]))
    for i, (tn, b) in enumerate(order):
        if nif.add_block(tn, b) != shape_k + i:
            raise AssertionError("block numbering")
    assert len(order) == n_new
    nif.blocks[k] = s.pack(tris=s.tris[keep])
    nif.blocks[parent] = with_child(nif.blocks[parent], shape_k)
    out = nif.write()
    mat = nif.strings[struct.unpack_from("<i", shader, 4)[0]].decode("ascii")
    report = (f"{SOURCE} {len(s.tris)} -> {int(keep.sum())} triangles (its {len(s.records)} vertices kept); {LABEL} "
              f"{len(new_tris)} triangles, {len(records)} vertices, blocks {shape_k}-{shape_k + n_new - 1} under block "
              f"{parent}, materials file {mat}" + ("; " + "; ".join(lines) if lines else ""))
    return out, report


def verify(before: bytes, after: bytes, stem: str, moved_tris):
    """Byte-level checks of a split nif against its source. Returns a list of problems."""
    bad = []
    a, b = Nif(before), Nif(after)
    if b.write() != after:
        bad.append("the output doesn't read back to its own bytes")
    k = a.shape_named(f"{stem}_{SOURCE}")
    kn = b.shape_named(f"{stem}_{LABEL}")
    if kn is None or b.shape_named(f"{stem}_{SOURCE}") != k:
        return bad + ["the shapes aren't where they should be"]
    parent = [p for p in range(len(a.blocks)) if a.type_of(p) in ("NiNode", "BSFadeNode") and k in node_children(a.blocks[p])[1]][0]
    for i in range(len(a.blocks)):
        if i not in (k, parent) and a.blocks[i] != b.blocks[i]:
            bad.append(f"block {i} ({a.type_of(i)}) changed")
        if a.type_of(i) != b.type_of(i):
            bad.append(f"block {i}'s type changed")
    if b.strings[:len(a.strings)] != a.strings or len(b.strings) != len(a.strings) + 1:
        bad.append("the string table")
    if node_children(b.blocks[parent])[1] != node_children(a.blocks[parent])[1] + [kn]:
        bad.append("the node's children")
    sa, sb_, sn = TriShape(a.blocks[k]), TriShape(b.blocks[k]), TriShape(b.blocks[kn])
    keep = np.ones(len(sa.tris), bool)
    keep[moved_tris] = False
    if not (np.array_equal(sb_.records, sa.records) and np.array_equal(sb_.tris, sa.tris[keep]) and sb_.desc == sa.desc
            and sb_.head == sa.head and sb_.bound == sa.bound and (sb_.skin, sb_.shader, sb_.alpha) == (sa.skin, sa.shader, sa.alpha)):
        bad.append(f"{SOURCE}: not its vertices and the kept triangles")
    # the new shape's triangles, corner by corner, the moved ones' records byte for byte (positions, UVs, normals, skin)
    if not np.array_equal(sn.records[sn.tris], sa.records[sa.tris[moved_tris]]) or sn.desc != sa.desc:
        bad.append(f"{LABEL}: its corners aren't the moved triangles' vertex records")
    if sn.head[4:] != sa.head[4:]:
        bad.append(f"{LABEL}: its flags or transform differ from {SOURCE}'s")
    # the bound is the full-precision vertices' (as harley_meshes' nifs: the worn nifs' half floats stick out of their
    # shapes' bounds by up to their rounding, 0.031 on the 2026-11-10a nifs)
    pos = sn.positions()
    c, r = np.array(sn.bound[:3]), sn.bound[3]
    if np.linalg.norm(pos - c, axis=1).max() > r + 1e-4 + (0.0 if sn.full else np.abs(pos).max() * 2.0 ** -11):
        bad.append(f"{LABEL}: its bound doesn't hold its vertices")
    if b.type_of(sn.shader) != "BSLightingShaderProperty" or b.blocks[sn.shader][:40] != a.blocks[sa.shader][:40] \
            or b.blocks[sn.shader][44:] != a.blocks[sa.shader][44:]:
        bad.append(f"{LABEL}: its shader property isn't {SOURCE}'s copy")
    tex_a, tex_b = struct.unpack_from("<i", a.blocks[sa.shader], 40)[0], struct.unpack_from("<i", b.blocks[sn.shader], 40)[0]
    if tex_b == tex_a or b.blocks[tex_b] != a.blocks[tex_a]:
        bad.append(f"{LABEL}: its texture set isn't its own copy of {SOURCE}'s")
    if sa.skin >= 0:
        ia, ib = a.blocks[sa.skin], b.blocks[sn.skin]
        da, db = struct.unpack_from("<i", ia, 4)[0], struct.unpack_from("<i", ib, 4)[0]
        if ia[:4] != ib[:4] or ia[8:] != ib[8:] or da == db or a.blocks[da][20:] != b.blocks[db][20:]:
            bad.append(f"{LABEL}: its skin isn't its own copy of {SOURCE}'s (the same bone and bind)")
        rot = np.array(struct.unpack_from("<9f", b.blocks[db], 20)).reshape(3, 3)
        trans = np.array(struct.unpack_from("<3f", b.blocks[db], 56))
        cs = np.array(struct.unpack_from("<3f", b.blocks[db], 4))
        rs = struct.unpack_from("<f", b.blocks[db], 16)[0]
        world = rot.T @ (cs - trans)   # back into the bike's space
        if np.linalg.norm(sn.positions() - world, axis=1).max() > rs + 1e-3:
            bad.append(f"{LABEL}: its culling sphere doesn't hold its vertices")
    elif sn.skin != -1:
        bad.append(f"{LABEL}: skinned in an unskinned nif")
    return bad


def pynifly_check(path: Path, stem: str, before: Path, moved_tris, pynifly: Path):
    """Read the output back through PyNifly: the shapes' names and order, the new shape last; the moved triangles'
    corners and UVs, static_black's kept ones."""
    sys.path.insert(0, str(pynifly))
    import logging
    logging.disable(logging.WARNING)
    from pyn.pynifly import NifFile
    bad = []
    a, b = NifFile(str(before)), NifFile(str(path))
    na, nb = [s.name for s in a.shapes], [s.name for s in b.shapes]
    if nb != na + [f"{stem}_{LABEL}"]:
        bad.append(f"shapes {len(nb)}: not the source's {len(na)} and {stem}_{LABEL} last")
    sa = next(s for s in a.shapes if s.name == f"{stem}_{SOURCE}")
    sb_ = next(s for s in b.shapes if s.name == f"{stem}_{SOURCE}")
    sn = next((s for s in b.shapes if s.name == f"{stem}_{LABEL}"), None)
    if sn is None:
        return bad + ["no new shape"]
    va, ta, ua = np.asarray(sa.verts), np.asarray(sa.tris), np.asarray(sa.uvs)
    vn, tn, un = np.asarray(sn.verts), np.asarray(sn.tris), np.asarray(sn.uvs)
    keep = np.ones(len(ta), bool)
    keep[moved_tris] = False
    if not (np.array_equal(vn[tn], va[ta[moved_tris]]) and np.array_equal(un[tn], ua[ta[moved_tris]])):
        bad.append(f"{LABEL}: its corners or UVs aren't the moved triangles'")
    if not (np.array_equal(np.asarray(sb_.tris), ta[keep]) and np.array_equal(np.asarray(sb_.verts), va)):
        bad.append(f"{SOURCE}: not its vertices and the kept triangles")
    if (sn.shader.name or "") != (sa.shader.name or ""):
        bad.append(f"{LABEL}: materials file {sn.shader.name!r}, {SOURCE}'s {sa.shader.name!r}")
    if sn.has_skin_instance != sa.has_skin_instance:
        bad.append(f"{LABEL}: skinned {sn.has_skin_instance}, {SOURCE} {sa.has_skin_instance}")
    if sa.has_skin_instance and list(sn.bone_names) != list(sa.bone_names):
        bad.append(f"{LABEL}: bones {list(sn.bone_names)}, {SOURCE}'s {list(sa.bone_names)}")
    if (sn.parent.name if sn.parent else None) != (sa.parent.name if sa.parent else None):
        bad.append(f"{LABEL}: under {sn.parent.name if sn.parent else None}")
    a.close()
    b.close()
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, required=True, help="a built Data tree (its Meshes/CMB is read)")
    ap.add_argument("--out", type=Path, required=True, help="where the fixed nifs go (a folder; may be Meshes/CMB itself)")
    ap.add_argument("--bar-cables", type=int, choices=(0, 1), default=1,
                    help="1 (2026-11-15b): the bars' cables cut and turned with the bars; 0: the nifs as they are")
    ap.add_argument("--expect", type=int, default=EXPECT, help="how many bar cables must be found (-1: any number)")
    ap.add_argument("--pynifly", type=Path, help="PyNifly's io_scene_nifly: read every output back through it")
    args = ap.parse_args()
    meshes = args.data / "Meshes" / "CMB"
    sources = {stem: (meshes / f"{stem}.nif").read_bytes() for stem in NIFS}
    args.out.mkdir(parents=True, exist_ok=True)
    if not args.bar_cables:
        for stem, data in sources.items():
            write_file(args.out / f"{stem}.nif", data)
            print(f"{stem}.nif as it was (--bar-cables 0): sha256 {sha256(data)}")
        return 0
    sp, ax, bar = parts_file(meshes / "CMB_BikeParts.ini")
    view = Nif(sources[FIND_IN])
    if view.shape_named(f"{FIND_IN}_{LABEL}") is not None:
        print(f"{FIND_IN}.nif has {FIND_IN}_{LABEL} already: the nifs are copied as they are")
        for stem, data in sources.items():
            if args.out.resolve() != meshes.resolve():
                write_file(args.out / f"{stem}.nif", data)
        return 0
    v, t = shape_geometry(view, f"{FIND_IN}_{SOURCE}")
    bar_tris = []
    fixed = {}
    for k in view.shapes():
        label = view.name_of(k)[len(FIND_IN) + 1:]
        g = TriShape(view.blocks[k])
        if label.startswith("front_"):
            bar_tris.append(g.positions()[g.tris])
        elif label.startswith(("static_", "rear_")):
            fixed[label] = (g.positions(), g.tris)
    bar_tris = np.vstack(bar_tris)
    print(f"the steering axis through ({sp[0]:g}, {sp[1]:g}, {sp[2]:g}) along ({ax[0]:.4f}, {ax[1]:.4f}, {ax[2]:.4f}), "
          f"BarAngle {bar:g} (CMB_BikeParts.ini); the bar assembly: {len(bar_tris)} triangles of {FIND_IN}'s front_* shapes")
    print(f"pieces of the fixed shapes with a bar end ({ATTACH:g} or nearer to the bar assembly, {R_END:g} or more from the axis):")
    cables, others = [], []
    for label, (fv, ft) in fixed.items():
        found = find_bar_cables(fv, ft, bar_tris, sp, ax, bar, name=label)
        (cables if label == SOURCE else others).extend((label, c) for c in found)
    if others:
        print(f"bar cables in {sorted(set(lb for lb, _ in others))}: only {SOURCE}'s are cut (none expected elsewhere)", file=sys.stderr)
        return 1
    if args.expect >= 0 and len(cables) != args.expect:
        print(f"{len(cables)} bar cables found, {args.expect} expected (--expect): the model isn't the one measured", file=sys.stderr)
        return 1
    moved = np.unique(np.concatenate([c["moved"] for _, c in cables])) if cables else np.zeros(0, np.int64)
    for _, c in cables:
        print(f"  cut piece {c['piece']} (its bar end on the bike's {'right' if c['seed_x'] > 0 else 'left'}): "
              f"{len(c['moved'])} of its {len(c['tris'])} triangles move with the bars, cut "
              f"{c['cut_s']:.1f} along it at ({c['cut_at'][0]:.1f}, {c['cut_at'][1]:.1f}, {c['cut_at'][2]:.1f}), "
              f"{c['cut_r']:.1f} from the axis ({c['ring']} vertices both sides share, up to {c['ring_r']:.1f} from it): "
              f"the cut opens {kink(c['ring_r'], 16):.1f} at 16 degrees, {kink(c['ring_r'], bar):.1f} at BarAngle; "
              f"the bar end, left fixed, would leave the bars by {kink(c['seed_r'][1], 16):.1f} and {c['bar_gap']:.1f}")
    if not len(moved):
        print("no bar cable: the nifs are copied as they are")
    if len(moved):
        clearances(v, t, cables, fixed, bar_tris, sp, ax, bar)
    bound = bound_of(v[np.unique(t[moved])]) if len(moved) else None
    bad = []
    for stem, data in sources.items():
        nif = Nif(data)
        k = nif.shape_named(f"{stem}_{SOURCE}")
        if k is None:
            bad.append(f"{stem}: no {SOURCE}")
            continue
        g = TriShape(nif.blocks[k])
        pv = g.positions()
        if not np.array_equal(g.tris, t) or len(pv) != len(v) or (np.abs(pv - v) > 1e-4 + np.abs(v) * 2.0 ** -11).any():
            bad.append(f"{stem}: its {SOURCE} isn't {FIND_IN}'s (triangles or vertices)")
            continue
        if not len(moved):
            out, rep = data, "as it was"
        else:
            out, rep = split(data, stem, moved, bound)
            problems = verify(data, out, stem, moved) if out is not data else [f"{rep} (its {FIND_IN} not)"]
            if problems:
                bad += [f"{stem}: {p}" for p in problems]
        path = args.out / f"{stem}.nif"
        write_file(path, out)
        print(f"wrote {path}: {len(out)} bytes (was {len(data)}), sha256 {sha256(out)}; {rep}")
        if args.pynifly and len(moved) and out is not data:
            with tempfile.TemporaryDirectory() as tmp:
                src = Path(tmp) / f"{stem}.nif"
                src.write_bytes(data)
                problems = pynifly_check(path, stem, src, moved, args.pynifly)
            bad += [f"{stem} (PyNifly): {p}" for p in problems]
            print(f"  read back through PyNifly: {'as written' if not problems else '; '.join(problems)}")
    for line in bad:
        print(f"FAIL {line}", file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
