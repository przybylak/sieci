#!/usr/bin/env python3
"""The 3D helmet emblems in the built nifs (build 2026-11-16a, C3 item 3.1): four shapes added to each of the five
bike nifs in place, as bar_cables.py added the bars' cables in 2026-11-15b.

The shapes (emblem_pieces.py builds them in the parked frame from the parked nif's tank plates, full precision):
static_helmEnclaveL, static_helmEnclaveR, static_helmBosL, static_helmBosR (the table's emblems.shape_order), each a
helmet standing square with its side's plate (static_badgeTankL / static_badgeTankR). Each is hidden on its own
materials file (Materials\\CMB\\Bike\\<shape>.bgsm in the parked nif, <shape>_worn.bgsm in the others: off_d/_n/_s,
alpha test 255, alpha 0, no shadows, as the rim styles' own files; emblem_art.py writes them) until a tank option's
material swap shows it (helm_enclave.bgsm or helm_bos.bgsm). "_static_" in the names gives the plugin's fixed role;
none ends with a colour writer's tag.

How (c3.md 3.1's method): per target nif a small donor nif is written through PyNifly with the model converter's own
shape writer (the model converter's add_shape: its vertex encoding, half floats in the worn nifs, the shader block of the
invisible spec, the alpha property), then its blocks are grafted into the shipped nif with bar_cables.py's byte-level
reader (imported, not edited): the new blocks after the last, the new strings after the last, the new shapes appended
to the node that holds the plates, every other block byte for byte. The skinned nifs (the three worn ones) give each
new shape its own BSSkin::Instance and one-bone BSSkin::BoneData, copies of its plate's (the same bone and bind, the
plates' union culling sphere: a static shape's own sphere would move FrontMinY and, with [Parts] RolesByName=0, turn it
with the bars). Per nif the rigid transform from the parked frame is fitted on the two plates' vertices (residual within
the half floats' rounding), not assumed; the shapes' vertices are the parked ones through it.

  python look_emblems.py --data <Data> [--data <overlay Data> ...] --out <Data>/Meshes/CMB --pynifly <io_scene_nifly>
      [--emblems 1|0] [--ground-field <unit B's badges.json>] [--materials bike_materials.json] [--report <json>]

Each helmet stands square with its plate in its ground's enamel field (unit B's badge_hg_enclave / badge_hg_bos: the area
both plates show, inside the chrome bevel): turned to the field's own axis, centred on it, as large as fits inset
emblem_pieces.FIELD_INSET (the outline recorded in emblem_pieces.GROUND_FIELD_UV, or --ground-field's badges.json, which
bike_art.py --badges writes). The bar assembly swept through BarAngle (bar_sweep: the under-bar mirrors pass close over
the right plate at full lock) keeps emblem_pieces.MIRROR_CLEAR from each helmet: by a shallower relief, then a smaller
helmet about the same centre.

--data: a built Data tree (Meshes/CMB: the five nifs); given more than once, a later tree's file wins (the package
tree, then an overlay such as 2026-11-15b's four nifs). The patched nifs go to --out (a folder of their own, e.g. a
package overlay's Data/Meshes/CMB, or Meshes/CMB itself). --emblems 0 writes the five nifs as they are (2026-11-15b's,
byte for byte); a nif that has the shapes already is left as it is. Checks run on every output: every original block
byte for byte (but the node that holds the shapes), the strings appended, the new shapes' names and order, their
vertices the parked ones through the fitted transform (within the half floats' rounding), one bone and the plates'
sphere in the worn nifs, and PyNifly reads each back (names, order, vertices, UVs, materials files). Exit status 1 when
a check fails. --report writes the numbers (placement, triangles, errors, transforms, sha256) as JSON.
"""

import argparse
import json
import struct
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bar_cables as BC  # noqa: E402
import emblem_pieces as EP  # noqa: E402
import harley_meshes as H  # noqa: E402

# (nif stem, the shapes' name stem, kind): kind parked = unskinned, full precision, <shape>.bgsm; worn = skinned to the
# plate's bone, <shape>_worn.bgsm; view = unskinned, full precision, under the NiNode CMB_BikeView, <shape>_worn.bgsm
NIFS = (("CMB_BikeParked", "CMB_Bike", "parked"), ("CMB_BikeWorn", "CMB_BikeWorn", "worn"),
        ("CMB_BikeWornRider", "CMB_BikeWornRider", "worn"), ("CMB_BikeWornRiderF", "CMB_BikeWornRiderF", "worn"),
        (H.VIEW_NODE, H.VIEW_NODE, "view"))
LABELS = tuple(label for label, _, _ in EP.SHAPES)
MAT_SPEC = "wheelF_rimLaced"   # the invisible own files' shader values: the rim styles' (bike_materials.json)


def material_name(label, kind):
    return f"Materials\\CMB\\Bike\\{label}{'' if kind == 'parked' else '_worn'}.bgsm"


def plate_records(nif, stem):
    """{side: TriShape} of the tank plates in a nif."""
    out = {}
    for side, label in EP.PLATES.items():
        k = nif.shape_named(f"{stem}_{label}")
        if k is None:
            raise ValueError(f"{stem}: no {stem}_{label}")
        out[side] = (k, BC.TriShape(nif.blocks[k]))
    return out


def normals_of(s):
    at = ((s.desc >> 16) & 0xF) * 4
    return s.records[:, at:at + 3].astype(np.float64) / 255.0 * 2.0 - 1.0


SNAP = 2e-3   # a fitted rotation this near a signed axis permutation is that permutation (the half floats' noise
              # tilts the worn nifs' fit by about 1e-4: the frames are the parked one turned half round about z)


def fit_rigid(a, b):
    """The rotation R and translation t with R a + t nearest b (Kabsch); R snapped to a signed axis permutation when
    within SNAP of one, t then the residual's mean."""
    ca, cb = a.mean(axis=0), b.mean(axis=0)
    U, _, Vt = np.linalg.svd((a - ca).T @ (b - cb))
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1.0, 1.0, d]) @ U.T
    snap = np.round(R)
    if np.abs(R - snap).max() < SNAP and abs(np.linalg.det(snap) - 1.0) < 1e-9:
        R = snap
    t = (b - a @ R.T).mean(axis=0)
    return R, t


GROUNDS = {"enclave": "hg_enclave", "bos": "hg_bos"}   # each helmet's ground (the table's emblems.items[].ground)


def ground_fields(path):
    """{helmet: its ground's enamel field in the plate's UVs}: from unit B's badges.json, or the recorded outline."""
    if path is None:
        return {name: EP.GROUND_FIELD_UV for name in EP.HELMETS}
    badges = json.loads(Path(path).read_text())["badges"]
    out = {}
    for name in EP.HELMETS:
        out[name] = tuple(tuple(p) for p in badges[GROUNDS[name]]["field"]["outline_plate_uv"])
        if out[name] != EP.GROUND_FIELD_UV:
            print(f"  {GROUNDS[name]}: its field in {path} differs from emblem_pieces.GROUND_FIELD_UV (the file's used)")
    return out


def bar_sweep(datas, data, pp, step=0.5):
    """The bar assembly's points (the view nif's front_* and fork* shapes, every mirror variant among them, full
    precision) turned about SteerAxis through SteerPoint from -BarAngle to +BarAngle every `step` degrees, as the plugin
    turns them (CMB_BikeParts.ini), those near the tank plates, in the parked frame (the view nif's fitted transform
    undone)."""
    ini = None
    for d in datas:
        p = d / "Meshes" / "CMB" / "CMB_BikeParts.ini"
        if p.exists():
            ini = p
    if ini is None:
        raise FileNotFoundError("CMB_BikeParts.ini in none of the --data trees")
    sp, ax, bar = BC.parts_file(ini)
    view = BC.Nif(data[H.VIEW_NODE])
    vp = plate_records(view, H.VIEW_NODE)
    a = np.vstack([pp[s][1].positions() for s in "LR"])
    b = np.vstack([vp[s][1].positions() for s in "LR"])
    R, t = fit_rigid(a, b)
    lo, hi = b.min(axis=0) - 4.0, b.max(axis=0) + 4.0
    pts = []
    for k in view.shapes():
        name = view.name_of(k).lower()
        if "_front_" not in name and "_fork" not in name:
            continue
        v = BC.TriShape(view.blocks[k]).positions()
        for deg in np.unique(np.r_[np.arange(-bar, bar, step), bar]):
            q = (v - sp) @ H.axis_rotation(ax, deg).T + sp
            pts.append(q[np.all((q >= lo) & (q <= hi), axis=1)])
    pts = np.vstack(pts) if pts else np.zeros((0, 3))
    print(f"  the bar assembly turned within BarAngle {bar:g} ({ini}): {len(pts)} points near the tank plates")
    return (pts - t) @ R          # into the parked frame (R orthonormal: R^T applied to rows)


def resolve(datas, stem):
    path = None
    for d in datas:
        p = d / "Meshes" / "CMB" / f"{stem}.nif"
        if p.exists():
            path = p
    if path is None:
        raise FileNotFoundError(f"{stem}.nif in none of {[str(d) for d in datas]}")
    return path


def donor_nif(path, stem, kind, shapes, R, t, base, spec, textures):
    """The four shapes in a nif of their own through PyNifly and the model converter's shape writer, in this nif's frame."""
    from pyn.pynifly import NifFile, TransformBuf
    out = NifFile()
    out.initialize("FO4", str(path), "BSFadeNode" if kind == "view" else "NiNode", path.stem)
    parent = None
    if kind == "view":
        identity = TransformBuf()
        identity.set_identity()
        parent = out.add_node(H.VIEW_NODE, identity, out.rootNode)
    skinned = kind == "worn"
    for label in LABELS:
        x = shapes[label]
        v = x["v"] @ R.T + t
        n = x["n"] @ R.T
        H.add_shape(out, f"{stem}_{label}", H.rows(v), H.rows(x["f"]), H.rows(x["uv"]), H.rows(n), base, base.use_type,
                    spec, skinned, kind != "parked", textures, material_name(label, kind),
                    H.BIKE_BONE if skinned else None, None, TransformBuf, parent=parent)
    out.save()
    return path.read_bytes()


def string_index(nif, s: bytes):
    if s in nif.strings:
        return nif.strings.index(s)
    nif.strings.append(s)
    nif.max_len = max(nif.max_len, len(s))
    return len(nif.strings) - 1


def graft(data: bytes, donor: bytes, stem: str, kind: str):
    """The donor's four shapes in the nif `data` (bytes): (new bytes, report lines, {label: block}). The donor's shape,
    shader, texture set and alpha blocks are copied (their string and block references renumbered); in a skinned nif
    each shape's skin instance and bone data are copies of its side's plate's."""
    nif, dn = BC.Nif(data), BC.Nif(donor)
    if nif.write() != data or dn.write() != donor:
        raise ValueError(f"{stem}: a nif doesn't read back to its own bytes")
    plates = plate_records(nif, stem)
    parents = [b for b in range(len(nif.blocks)) if nif.type_of(b) in ("NiNode", "BSFadeNode")
               and plates["L"][0] in BC.node_children(nif.blocks[b])[1]]
    if len(parents) != 1 or plates["R"][0] not in BC.node_children(nif.blocks[parents[0]])[1]:
        raise ValueError(f"{stem}: the plates aren't under one node")
    parent = parents[0]
    kr = nif.shape_named(f"{stem}_{MAT_SPEC}")
    if kr is None:
        raise ValueError(f"{stem}: no {stem}_{MAT_SPEC} (the rim styles' invisible shape the new ones are made as)")
    ref = BC.TriShape(nif.blocks[kr])
    lines, made = [], {}
    for label in LABELS:
        side = next(s for lb, _, s in EP.SHAPES if lb == label)
        kd = dn.shape_named(f"{stem}_{label}")
        if kd is None:
            raise ValueError(f"{stem}: the donor has no {stem}_{label}")
        ds = BC.TriShape(dn.blocks[kd])
        pk, ps = plates[side]
        if ds.desc != ps.desc:
            raise ValueError(f"{stem}_{label}: the donor's vertex format {ds.desc:#018x}, the plate's {ps.desc:#018x}")
        if struct.unpack_from("<I", ds.head, 12) != struct.unpack_from("<I", ps.head, 12) or ds.head[16:72] != ps.head[16:72]:
            raise ValueError(f"{stem}_{label}: the donor's flags or transform aren't the plate's")
        if (ds.skin >= 0) != (ps.skin >= 0) or ds.alpha < 0:
            raise ValueError(f"{stem}_{label}: skinned {ds.skin >= 0} (the plate {ps.skin >= 0}), alpha {ds.alpha}")
        shape_k = len(nif.blocks)
        nxt = shape_k + 1
        skin_k = data_k = -1
        if ps.skin >= 0:
            skin_k, data_k = nxt, nxt + 1
            nxt += 2
        shader_k, tex_k, alpha_k = nxt, nxt + 1, nxt + 2
        name_idx = string_index(nif, f"{stem}_{label}".encode("ascii"))
        head = struct.pack("<i", name_idx) + ds.head[4:]
        order = [("BSTriShape", ds.pack(head=head, refs=(skin_k, shader_k, alpha_k)))]
        if ps.skin >= 0:
            inst = bytearray(nif.blocks[ps.skin])
            root, dref, nbones = struct.unpack_from("<iiI", inst, 0)
            if nif.type_of(ps.skin) != "BSSkin::Instance" or nbones != 1 or nif.type_of(dref) != "BSSkin::BoneData":
                raise ValueError(f"{stem}: {EP.PLATES[side]}'s skin isn't one bone")
            struct.pack_into("<i", inst, 4, data_k)
            order += [("BSSkin::Instance", bytes(inst)), ("BSSkin::BoneData", nif.blocks[dref])]
        dsh = bytearray(dn.blocks[ds.shader])
        if dn.type_of(ds.shader) != "BSLightingShaderProperty" or struct.unpack_from("<I", dsh, 8)[0] != 0:
            raise ValueError(f"{stem}_{label}: the donor's shader property isn't laid out as expected")
        mat = dn.strings[struct.unpack_from("<i", dsh, 4)[0]]
        struct.pack_into("<i", dsh, 4, string_index(nif, mat))
        dtex = struct.unpack_from("<i", dsh, 40)[0]
        if dn.type_of(dtex) != "BSShaderTextureSet":
            raise ValueError(f"{stem}_{label}: the donor's texture set")
        struct.pack_into("<i", dsh, 40, tex_k)
        dal = bytearray(dn.blocks[ds.alpha])
        if dn.type_of(ds.alpha) != "NiAlphaProperty":
            raise ValueError(f"{stem}_{label}: the donor's alpha property")
        # the empty names as this nif's own invisible shape has them (the parked nif, opened from the master's,
        # names them by its empty string; the others write none): the root material and the alpha property's name
        struct.pack_into("<i", dsh, 60, struct.unpack_from("<i", nif.blocks[ref.shader], 60)[0])
        struct.pack_into("<i", dal, 0, struct.unpack_from("<i", nif.blocks[ref.alpha], 0)[0])
        if dsh[:4] + dsh[8:40] + dsh[44:] != nif.blocks[ref.shader][:4] + nif.blocks[ref.shader][8:40] + nif.blocks[ref.shader][44:] \
                or bytes(dal) != nif.blocks[ref.alpha] or dn.blocks[dtex] != nif.blocks[struct.unpack_from("<i", nif.blocks[ref.shader], 40)[0]]:
            raise ValueError(f"{stem}_{label}: the donor's shader, alpha or texture set isn't {stem}_{MAT_SPEC}'s (the rim "
                             f"styles' invisible own blocks) but the materials file's name")
        order += [("BSLightingShaderProperty", bytes(dsh)), ("BSShaderTextureSet", dn.blocks[dtex]),
                  ("NiAlphaProperty", bytes(dal))]
        for i, (tn, b) in enumerate(order):
            if nif.add_block(tn, b) != shape_k + i:
                raise AssertionError("block numbering")
        nif.blocks[parent] = BC.with_child(nif.blocks[parent], shape_k)
        made[label] = shape_k
        lines.append(f"{stem}_{label}: blocks {shape_k}-{shape_k + len(order) - 1}, {len(ds.records)} vertices, "
                     f"{len(ds.tris)} triangles, materials file {mat.decode()}")
    return nif.write(), lines, made, parent


def verify(before: bytes, after: bytes, stem: str, kind: str, shapes, R, t):
    """Byte-level checks of a patched nif against its source. Returns a list of problems."""
    bad = []
    a, b = BC.Nif(before), BC.Nif(after)
    if b.write() != after:
        bad.append("the output doesn't read back to its own bytes")
    nshapes = len(a.shapes())
    names = [b.name_of(k) for k in b.shapes()]
    want = [a.name_of(k) for k in a.shapes()] + [f"{stem}_{label}" for label in LABELS]
    if names != want:
        bad.append(f"shapes {names[nshapes:]}: not the source's and the four in order")
    parents = [p for p in range(len(a.blocks)) if a.type_of(p) in ("NiNode", "BSFadeNode")
               and BC.node_children(a.blocks[p])[1] != BC.node_children(b.blocks[p])[1]]
    if len(parents) != 1:
        return bad + [f"{len(parents)} nodes changed"]
    parent = parents[0]
    for i in range(len(a.blocks)):
        if i != parent and a.blocks[i] != b.blocks[i]:
            bad.append(f"block {i} ({a.type_of(i)}) changed")
        if a.type_of(i) != b.type_of(i):
            bad.append(f"block {i}'s type changed")
    if b.strings[:len(a.strings)] != a.strings:
        bad.append("the string table: the source's strings not kept in place")
    new_kids = BC.node_children(b.blocks[parent])[1][len(BC.node_children(a.blocks[parent])[1]):]
    if BC.node_children(b.blocks[parent])[1][:len(BC.node_children(a.blocks[parent])[1])] != BC.node_children(a.blocks[parent])[1] \
            or [b.name_of(k) for k in new_kids] != [f"{stem}_{label}" for label in LABELS]:
        bad.append("the node's children: not the source's and the four after them")
    plates = plate_records(a, stem)
    worst = 0.0
    for label in LABELS:
        side = next(s for lb, _, s in EP.SHAPES if lb == label)
        k = b.shape_named(f"{stem}_{label}")
        s = BC.TriShape(b.blocks[k])
        want_v = shapes[label]["v"] @ R.T + t
        got = s.positions()
        tol = 1e-4 + (0.0 if s.full else np.abs(want_v).max() * 2.0 ** -11)
        d = float(np.abs(got - want_v).max()) if len(got) == len(want_v) else np.inf
        worst = max(worst, d)
        if d > tol:
            bad.append(f"{label}: its vertices {d:.4f} off the parked ones through the fitted transform (tolerance {tol:.4f})")
        if not np.array_equal(s.tris, shapes[label]["f"]):
            bad.append(f"{label}: its triangles")
        uv = s.uvs()
        if np.abs(uv - shapes[label]["uv"]).max() > 2.0 ** -11 + 1e-6:
            bad.append(f"{label}: its UVs {np.abs(uv - shapes[label]['uv']).max():.5f} off")
        ps = plates[side][1]
        if s.desc != ps.desc:
            bad.append(f"{label}: its vertex format {s.desc:#x}, the plate's {ps.desc:#x}")
        if kind == "worn":
            ia, ib = a.blocks[ps.skin], b.blocks[s.skin]
            da, db = struct.unpack_from("<i", ia, 4)[0], struct.unpack_from("<i", ib, 4)[0]
            if b.type_of(s.skin) != "BSSkin::Instance" or ia[:4] != ib[:4] or ia[8:] != ib[8:] or da == db \
                    or a.blocks[da] != b.blocks[db] or s.skin == ps.skin:
                bad.append(f"{label}: its skin isn't its own copy of its plate's (the same bone, bind and sphere)")
            rot = np.array(struct.unpack_from("<9f", b.blocks[db], 20)).reshape(3, 3)
            trans = np.array(struct.unpack_from("<3f", b.blocks[db], 56))
            cs = np.array(struct.unpack_from("<3f", b.blocks[db], 4))
            rs = struct.unpack_from("<f", b.blocks[db], 16)[0]
            centre = rot.T @ (cs - trans)
            if np.linalg.norm(got - centre, axis=1).max() > rs:
                bad.append(f"{label}: the plates' sphere doesn't hold it")
            # one bone, weight 1 on bone 0: the skin bytes of every vertex the plate's first vertex's
            at = ((s.desc >> 28) & 0xF) * 4
            if not (s.records[:, at:at + 12] == ps.records[0, at:at + 12]).all():
                bad.append(f"{label}: its skin weights aren't one bone at 1")
        elif s.skin != -1:
            bad.append(f"{label}: skinned in an unskinned nif")
        c, r = np.array(s.bound[:3]), s.bound[3]
        if np.linalg.norm(got - c, axis=1).max() > r + 1e-4 + (0.0 if s.full else np.abs(got).max() * 2.0 ** -11):
            bad.append(f"{label}: its bound doesn't hold its vertices")
    return bad, worst


def pynifly_check(path: Path, before: Path, stem: str, kind: str, shapes, R, t, pynifly: Path):
    """Read the output back through PyNifly: the shapes' names and order, the new ones last; their vertices, triangles,
    UVs and materials files; skinned (one bone, the plate's) in the worn nifs; the view nif's under CMB_BikeView."""
    sys.path.insert(0, str(pynifly))
    import logging
    logging.disable(logging.WARNING)
    from pyn.pynifly import NifFile
    bad = []
    a, b = NifFile(str(before)), NifFile(str(path))
    na, nb = [s.name for s in a.shapes], [s.name for s in b.shapes]
    if nb != na + [f"{stem}_{label}" for label in LABELS]:
        bad.append(f"shapes {len(nb)}: not the source's {len(na)} and the four last")
    by = {s.name: s for s in b.shapes}
    for label in LABELS:
        side = next(s for lb, _, s in EP.SHAPES if lb == label)
        s = by.get(f"{stem}_{label}")
        plate = by.get(f"{stem}_{EP.PLATES[side]}")
        if s is None or plate is None:
            bad.append(f"{label}: missing")
            continue
        v = np.asarray(s.verts)
        want = shapes[label]["v"] @ R.T + t
        tol = 1e-4 + (0.0 if kind != "worn" else np.abs(want).max() * 2.0 ** -11)
        if v.shape != want.shape or np.abs(v - want).max() > tol:
            bad.append(f"{label}: its vertices")
        if not np.array_equal(np.asarray(s.tris), shapes[label]["f"]):
            bad.append(f"{label}: its triangles")
        if np.abs(np.asarray(s.uvs) - shapes[label]["uv"]).max() > 2.0 ** -11 + 1e-6:
            bad.append(f"{label}: its UVs")
        if (s.shader.name or "") != material_name(label, kind):
            bad.append(f"{label}: materials file {s.shader.name!r}")
        if s.has_skin_instance != (kind == "worn") or (kind == "worn" and list(s.bone_names) != list(plate.bone_names)):
            bad.append(f"{label}: skinned {s.has_skin_instance}, bones {list(s.bone_names) if s.has_skin_instance else []} "
                       f"(the plate's {list(plate.bone_names) if plate.has_skin_instance else []})")
        if (s.parent.name if s.parent else None) != (plate.parent.name if plate.parent else None):
            bad.append(f"{label}: under {s.parent.name if s.parent else None}, the plate under "
                       f"{plate.parent.name if plate.parent else None}")
    a.close()
    b.close()
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, action="append", required=True,
                    help="a built Data tree (its Meshes/CMB is read); more than one: a later tree's file wins")
    ap.add_argument("--out", type=Path, required=True, help="where the patched nifs go (a folder; may be Meshes/CMB itself)")
    ap.add_argument("--emblems", type=int, choices=(0, 1), default=1,
                    help="1 (2026-11-16a): the four helmet shapes added; 0: the nifs as they are (2026-11-15b's)")
    ap.add_argument("--pynifly", type=Path, required=True, help="PyNifly's io_scene_nifly (the donor nifs, the read-back)")
    ap.add_argument("--materials", type=Path, default=HERE / "bike_materials.json")
    ap.add_argument("--ground-field", type=Path,
                    help="unit B's badges.json (bike_art.py --badges): each helmet fits inside its ground's "
                         "hg_<helmet>.field.outline_plate_uv; default the outline recorded in emblem_pieces.GROUND_FIELD_UV")
    ap.add_argument("--report", type=Path, help="write the numbers as JSON")
    args = ap.parse_args()
    sources = {stem: resolve(args.data, stem) for stem, _, _ in NIFS}
    data = {stem: p.read_bytes() for stem, p in sources.items()}
    args.out.mkdir(parents=True, exist_ok=True)
    report = dict(emblems=args.emblems, sources={stem: str(p) for stem, p in sources.items()}, nifs={},
                  ground_field=str(args.ground_field) if args.ground_field else "emblem_pieces.GROUND_FIELD_UV")
    if not args.emblems:
        for stem, _, _ in NIFS:
            BC.write_file(args.out / f"{stem}.nif", data[stem])
            print(f"{stem}.nif as it was (--emblems 0): sha256 {BC.sha256(data[stem])}")
            report["nifs"][stem] = dict(sha256=BC.sha256(data[stem]), patched=False)
        if args.report:
            args.report.write_text(json.dumps(report, indent=1) + "\n")
        return 0
    sys.path.insert(0, str(args.pynifly))
    import logging
    logging.disable(logging.WARNING)
    from pyn.pynifly import NifFile

    # the plates in the parked nif (full precision), the shapes on them
    parked = BC.Nif(data["CMB_BikeParked"])
    pp = plate_records(parked, "CMB_Bike")
    plates = {side: (s.positions(), s.tris, normals_of(s), s.uvs()) for side, (_, s) in pp.items()}
    fields = ground_fields(args.ground_field)
    print("the helmets (emblem_pieces.py), each inside its ground's enamel field "
          + (f"from {args.ground_field}" if args.ground_field else "(emblem_pieces.GROUND_FIELD_UV, unit B's 5918ddf)") + ":")
    sweep = bar_sweep(args.data, data, pp)
    shapes = EP.build(plates, log=print, fields=fields, sweep=sweep)
    report["shapes"] = {label: dict(helmet=x["helmet"], side=x["side"], vertices=len(x["v"]), triangles=len(x["f"]),
                                    scale=x["scale"], centre=x["centre"], margin=x["margin"],
                                    error=dict(zip(("max", "p99", "verts_max"), x["error"])),
                                    height_max=float(x["design"][:, 2].max()), width=x["width"], height=x["height"],
                                    field_margin=x["field_margin"], angle=x["angle"], relief=x["relief"],
                                    sweep_clearance=x["clearance"])
                        for label, x in shapes.items()}
    # the invisible spec and its textures (the rim styles'), the vanilla shape's buffer and shader properties
    spec_all, _ = H.load_shaders(args.materials if args.materials and args.materials.exists() else None)
    spec = spec_all[MAT_SPEC]
    pk = NifFile(str(sources["CMB_BikeParked"]))
    base = H.Base(pk.shapes[0])
    base.props.flags = base.props.flags & ~1   # the master's shape, which the parked nif hides: ours are shown
    bad = []
    a = np.vstack([pp[s][1].positions() for s in "LR"])
    exact = {}   # the full-precision nifs' fitted transforms (parked, view)
    for stem, name_stem, kind in NIFS:
        nif = BC.Nif(data[stem])
        tp = plate_records(nif, name_stem)
        if tp["L"][1].full:
            exact[stem] = fit_rigid(a, np.vstack([tp[s][1].positions() for s in "LR"]))
    with tempfile.TemporaryDirectory() as tmp:
        for stem, name_stem, kind in NIFS:
            src = data[stem]
            nif = BC.Nif(src)
            if nif.shape_named(f"{name_stem}_{LABELS[0]}") is not None:
                out, rep = src, "has the helmets already: left as it is"
                if args.out.resolve() != sources[stem].parent.resolve():
                    BC.write_file(args.out / f"{stem}.nif", out)
                print(f"{stem}.nif: {rep}")
                report["nifs"][stem] = dict(sha256=BC.sha256(out), patched=False, note=rep)
                continue
            tp = plate_records(nif, name_stem)
            b = np.vstack([tp[s][1].positions() for s in "LR"])
            R, t = fit_rigid(a, b)
            resid = float(np.abs(a @ R.T + t - b).max())
            full = tp["L"][1].full
            tol = 1e-4 + (0.0 if full else np.abs(b).max() * 2.0 ** -11)
            how = "fitted"
            if not full:   # a full-precision nif's transform where it fits these plates within their rounding (the
                for other, (R2, t2) in exact.items():   # half floats' fit leans by their rounding's bias)
                    r2 = float(np.abs(a @ R2.T + t2 - b).max())
                    if r2 <= tol:
                        R, t, resid, how = R2, t2, r2, f"{other}.nif's (full precision), which fits its plates"
                        break
            print(f"{stem}.nif: the parked frame to its frame ({how}): R {R.astype(int).tolist() if np.all(R == np.round(R)) else R.round(6).tolist()}, "
                  f"t ({t[0]:.4f}, {t[1]:.4f}, {t[2]:.4f}); the plates' {len(a)} vertices within {resid:.5f} "
                  f"(tolerance {tol:.5f}: {'full precision' if full else 'half floats'})")
            if resid > tol:
                bad.append(f"{stem}: the plates don't fit the parked ones by a rigid transform ({resid:.5f})")
                continue
            textures = H.texture_paths(spec, H.OFF_MAT if not spec.get("textures_of") else spec["textures_of"],
                                       kind != "parked", False)
            donor = donor_nif(Path(tmp) / f"{stem}_donor.nif", name_stem, kind, shapes, R, t, base, spec, textures)
            out, lines, _, parent = graft(src, donor, name_stem, kind)
            problems, worst = verify(src, out, name_stem, kind, shapes, R, t)
            for line in lines:
                print(f"  {line}")
            print(f"  under block {parent} ({nif.name_of(parent)}); the new vertices at most {worst:.5f} off the parked ones "
                  f"through the transform")
            bad += [f"{stem}: {p}" for p in problems]
            path = args.out / f"{stem}.nif"
            BC.write_file(path, out)
            print(f"  wrote {path}: {len(out)} bytes (was {len(src)}), {len(BC.Nif(out).shapes())} shapes, sha256 {BC.sha256(out)}")
            before = Path(tmp) / f"{stem}.nif"
            before.write_bytes(src)
            problems = pynifly_check(path, before, name_stem, kind, shapes, R, t, args.pynifly)
            bad += [f"{stem} (PyNifly): {p}" for p in problems]
            print(f"  read back through PyNifly: {'as written' if not problems else '; '.join(problems)}")
            report["nifs"][stem] = dict(sha256=BC.sha256(out), bytes=len(out), was=BC.sha256(src), patched=True,
                                        shapes=len(BC.Nif(out).shapes()), R=R.tolist(), t=t.tolist(), plate_residual=resid,
                                        worst=worst)
    if args.report:
        args.report.write_text(json.dumps(report, indent=1) + "\n")
    for line in bad:
        print(f"FAIL {line}", file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
