#!/usr/bin/env python3
"""Art build B's new shapes in the built nifs (build 2026-11-21a, c3.md 3.5/3.6 and 3.8): the two wear shells and the
front mudguard's badge patch, added to each of the five bike nifs in place, as look_emblems.py added the helmets in
2026-11-16a and bar_cables.py the bars' cables in 2026-11-15b.

The shapes (shell_pieces.py builds their geometry in the parked frame, full precision), appended in this order after
every shape the nif has:
- static_wear: a shell of static_paint, its vertex records copied (UVs, normals, tangents, skin weights: the wear art
  is drawn in the paint's own texture space) with the positions lifted 0.32 along the normal averaged per position
  (shell_pieces.shell_positions: the shell closed at the hard edges, a concave corner's lift lengthened, every vertex
  fitted into the worn nifs' half floats), the triangles with a vertex inside another shape (the frame, the seat, the
  chrome trim, the helmets) left out with the vertices only they used; its source's skin instance and bone data
  copied (the plugin holds every shape by its own bone data; the same bone, bind and culling sphere), in the worn nifs.
- fork_wear: the same of fork_paint ("_fork": the plugin turns it with the bars and moves it with the front wheel's
  travel, as fork_paint).
- fork_badgeFront: the front mudguard's badge patch (shell_pieces.front_badge_patch: the rear patch's grid cast onto
  fork_paint's crown, read from in front, its UVs the badge atlas' plate rectangle), written by the model converter's
  shape writer into a donor nif through PyNifly (look_emblems.py's way: the vertex encoding, half floats in the worn
  nifs), its skin fork_paint's copied.
Each names its own materials file (Materials\\CMB\\Bike\\<label>.bgsm in the parked nif, <label>_worn.bgsm in the others),
invisible until a look option's material swap names another: the shells' a copy of the rim styles' own invisible file
(alpha test 255 over off_d/_n/_s, alpha 0, no shadows) one-sided, the patch's the rear patch's static_badgeFender.bgsm
byte for byte; the shells' shader blocks are the rim styles' (wheelF_rimLaced) with Double_Sided off, the patch's the rear
patch's; each its own alpha property and texture set (copies). "_static_" and "_fork" give the plugin's roles by name;
no name ends with a colour writer's tag.

And the rear fender patch (static_badgeFender, 2026-11-07a's) raised shell_pieces.FENDER_RAISE along its own normals
(to 0.48 over the fender, as the front patch's FRONT_PATCH_LIFT), so a badge on it stays over the wear shell's 0.32 in
the half floats (--fender-raise 0 leaves it as it is).

Since 2026-11-22a (round t64, test 58's wishes), after those (a step of its own over 2026-11-21a's nifs, or straight
after the first over older ones):
- static_paintwear and fork_paintwear (--paintwear): the paint condition shells, made as the wear shells but
  shell_pieces.PAINTWEAR_LIFT (0.16) over the paint, under static_wear;
- static_exhaust_wear, static_engine_wear and fork_black_wear (--parts): the wear on more parts, shells
  shell_pieces.SHELL_LIFT over the whole exhaust, the engine's five outer covers (shell_pieces.ENGINE_COVERS) and the
  fork lowers (shell_pieces.PART_SHELLS);
- static_wear rebuilt (--badge-lift): over the badge sheets' footprints (shell_pieces.BADGE_SHEETS: the tank plates, the
  rear roundel, the rear patch) it rises to BADGE_OVER over the sheet (shell_pieces.badge_lifts), so the grime can be
  drawn over the badges; the helmets (alternatives, invisible until chosen) no longer cut it out.
- every overlay shell (static_wear, fork_wear and the five new) blends (--overlay-blend): its NiAlphaProperty the glass's
  (blending on, test GREATER 0) and its own materials file blending at alpha 0 (blended_invisible), so the game's swap at
  a 3D's load shows the wear (test 58: the wear showed only where F4SE swapped at runtime; the apply unit's finding).
Each new one names its own invisible materials file (<label>.bgsm, <label>_worn.bgsm). The inside test leaves out the
open sheets, the helmets and the shells. --paintwear 0 --parts 0 --badge-lift 0 --overlay-blend 0 give 2026-11-21a's
nifs and materials files byte for byte.

  python look_shells.py --data <Data> [--data <overlay Data> ...] --out <Data>/Meshes/CMB --pynifly <io_scene_nifly>
      [--shells 1|0] [--paintwear 1|0] [--parts 1|0] [--badge-lift 1|0] [--overlay-blend 1|0] [--bgsm-out <Data>]
      [--fender-raise 0.16]
      [--materials bike_materials.json] [--report <json>]

--data: a built Data tree (Meshes/CMB: the five nifs and CMB_BikeParts.ini; Materials/CMB/Bike: the rim styles' and the
rear patch's own files, the templates of the six new ones); given more than once, a later tree's file wins. The patched
nifs go to --out; --bgsm-out <Data> writes the six materials files under its Materials\\CMB\\Bike. --shells 0 writes the
five nifs as they are (2026-11-17a's, byte for byte) and no materials file; a nif that has the shapes already is left as
it is. Checks on every output: every original block byte for byte (but the node that holds the shapes and, raised, the
rear patch's shape), the strings appended, the new shapes' names and order, each shell's records its source's but the
positions, the positions the parked ones through the fitted transform (the worn nifs' half floats exactly the fitted
ones'), the skins copies of their sources', and PyNifly reads each back. Exit status 1 when a check fails.
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
import bgsm as BG  # noqa: E402
import bike_pieces as BP  # noqa: E402
import harley_meshes as H  # noqa: E402
import emblem_pieces as EP  # noqa: E402
import look_emblems as LE  # noqa: E402
import shell_pieces as SP  # noqa: E402

NIFS = LE.NIFS
SHELLS = (("static_wear", "static_paint"), ("fork_wear", "fork_paint"))   # (label, its source)
PATCH, PATCH_ON = "fork_badgeFront", "fork_paint"
LABELS = tuple(lb for lb, _ in SHELLS) + (PATCH,)
RIM = "wheelF_rimLaced"     # the rim styles' invisible own blocks: the shells' shader, alpha and texture set made as them
FENDER = H.FENDER_BADGE     # the rear patch: the front patch's blocks made as its, and raised
# the open sheets (badge plates, patches, the plate's text): no inside to be in (their winding number is about 0.5 near them)
SHEETS = H.BADGE_SPLIT + (FENDER, H.PLATE_TEXT, PATCH)
SF2_DOUBLE_SIDED = 0x10


def material_name(label, kind):
    return f"Materials\\CMB\\Bike\\{label}{'' if kind == 'parked' else '_worn'}.bgsm"


def geometry(nif, name):
    """(positions, triangles, decoded normals, TriShape) of a nif's shape."""
    k = nif.shape_named(name)
    if k is None:
        raise ValueError(f"no {name}")
    s = BC.TriShape(nif.blocks[k])
    return s.positions(), s.tris, LE.normals_of(s), s


def with_positions(s, records, pos):
    """The records with their positions replaced (float32 in a full-precision nif, half floats in the others); every
    other byte as it was (the bitangent's x in the fourth slot among them)."""
    r = np.array(records, copy=True)
    if s.full:
        r[:, :12] = np.ascontiguousarray(np.asarray(pos, "<f4")).view(np.uint8).reshape(len(r), 12)
    else:
        r[:, :6] = np.ascontiguousarray(np.asarray(pos, np.float64).astype("<f2")).view(np.uint8).reshape(len(r), 6)
    return r


def frames(data):
    """Per nif the rigid transform from the parked frame (look_emblems.fit_rigid on static_paint's vertices; a half-float
    nif takes a full-precision nif's transform where it fits within the rounding)."""
    pk = BC.Nif(data["CMB_BikeParked"])
    a = geometry(pk, "CMB_Bike_static_paint")[0]
    out, exact = {}, {}
    for stem, nm, kind in NIFS:
        nif = BC.Nif(data[stem])
        b, _, _, s = geometry(nif, f"{nm}_static_paint")
        R, t = LE.fit_rigid(a, b)
        if s.full:
            exact[stem] = (R, t)
        out[stem] = [R, t, s.full, b]
    for stem, (R, t, full, b) in out.items():
        tol = 1e-4 + (0.0 if full else np.abs(b).max() * 2.0 ** -11)
        resid = float(np.abs(a @ R.T + t - b).max())
        if not full:
            for other, (R2, t2) in exact.items():
                r2 = float(np.abs(a @ R2.T + t2 - b).max())
                if r2 <= tol:
                    R, t, resid = R2, t2, r2
                    break
        out[stem] = (R, t, resid, tol, full)
    return out


def solids(nif, nm, skip=()):
    """{label: (positions, triangles)} of a nif's shapes the inside test looks at (every shape but the master's hidden
    one, the open sheets and `skip`)."""
    out = {}
    for k in nif.shapes():
        name = nif.name_of(k)
        if not name.startswith(nm + "_"):
            continue
        label = name[len(nm) + 1:]
        if label in SHEETS or label in skip:
            continue
        s = BC.TriShape(nif.blocks[k])
        out[label] = (s.positions(), s.tris)
    return out


def build_shapes(data, fr, log):
    """The new shapes' geometry in the parked frame: {label: dict} and the rear patch raised."""
    pk = BC.Nif(data["CMB_BikeParked"])
    wn = BC.Nif(data["CMB_BikeWorn"])
    R, t = fr["CMB_BikeWorn"][:2]
    out = {}
    pk_solids = solids(pk, "CMB_Bike")
    wn_solids = solids(wn, "CMB_BikeWorn")
    for label, src in SHELLS:
        v, f, n, _ = geometry(pk, f"CMB_Bike_{src}")
        vw = geometry(wn, f"CMB_BikeWorn_{src}")[0]
        for stem, nm, kind in NIFS:   # the three worn nifs' sources the same half floats
            if kind == "worn" and not np.array_equal(geometry(BC.Nif(data[stem]), f"{nm}_{src}")[0], vw):
                raise ValueError(f"{stem}_{src}: not CMB_BikeWorn's positions")
        log(f"  {label}: a shell of {src} ({len(v)} vertices, {len(f)} triangles)")
        q, na, num = SP.shell_positions(v, f, n, worn=(R, t, vw), log=log)
        # inside another shape: in full precision (the parked nif's shapes) and in the worn half floats (the worn nif's)
        in_p = SP.inside_shapes(q, pk_solids)
        in_w = SP.inside_shapes(SP.half(q @ R.T + t), wn_solids)
        inside = (in_p != None) | (in_w != None)  # noqa: E711
        keep, used, nf = SP.keep_outside(f, inside)
        why = {}
        for h in list(in_p) + list(in_w):
            if h is not None:
                why[h] = why.get(h, 0) + 1
        log(f"    {int(inside.sum())} vertices inside another shape ({', '.join(f'{k} {c}' for k, c in sorted(why.items()))}): "
            f"{int((~keep).sum())} triangles left out, {len(f) - int((~keep).sum())} kept on {len(used)} vertices")
        out[label] = dict(src=src, used=used, f=nf, q=q[used], numbers=num, inside=why,
                          dropped=int((~keep).sum()), vertices=len(used), triangles=len(nf))
    # the front patch on fork_paint's crown, in the parked frame; the axle from CMB_BikeParts.ini (the worn frame)
    v, f, n, _ = geometry(pk, f"CMB_Bike_{PATCH_ON}")
    Rv, tv = fr[H.VIEW_NODE][:2]
    axle_w = np.array([float(x) for x in data["parts"]["FrontAxle"].split(",")])
    axle = (axle_w - tv) @ Rv
    V, F, N, UV, num = SP.front_badge_patch((v, f, n), axle)
    log(f"  {PATCH}: {len(V)} vertices, {len(F)} triangles, {SP.FRONT_PATCH_SIZE[0]:g} x {SP.FRONT_PATCH_SIZE[1]:g} on "
        f"{PATCH_ON}'s crown at {num['degs'][0]:.2f}..{num['degs'][1]:.2f} degrees round the front axle (crown radius "
        f"{num['r_crown']:.2f}, centred at parked x {num['x0']:.2f}), lifted {SP.FRONT_PATCH_LIFT:g}; the crown "
        f"{num['margin']:.2f} wider than the patch each side at its narrowest row")
    out[PATCH] = dict(v=V, f=F, n=N, uv=UV, numbers=num, vertices=len(V), triangles=len(F))
    return out


def raised_fender(pk, by):
    v, _, n, _ = geometry(pk, f"CMB_Bike_{FENDER}")
    return SP.raise_patch(v, n, by)


def donor_patch(path, stem, kind, x, R, t, base, spec, textures):
    """The front patch in a nif of its own through PyNifly and the model converter's shape writer, in this nif's frame."""
    from pyn.pynifly import NifFile, TransformBuf
    out = NifFile()
    out.initialize("FO4", str(path), "BSFadeNode" if kind == "view" else "NiNode", path.stem)
    parent = None
    if kind == "view":
        identity = TransformBuf()
        identity.set_identity()
        parent = out.add_node(H.VIEW_NODE, identity, out.rootNode)
    skinned = kind == "worn"
    H.add_shape(out, f"{stem}_{PATCH}", H.rows(x["v"] @ R.T + t), H.rows(x["f"]), H.rows(x["uv"]), H.rows(x["n"] @ R.T),
                base, base.use_type, spec, skinned, kind != "parked", textures, material_name(PATCH, kind),
                H.BIKE_BONE if skinned else None, None, TransformBuf, parent=parent)
    out.save()
    return path.read_bytes()


def skin_copy(nif, s, data_k, positions, stem, label):
    """Copies of a shape's one-bone skin instance (pointing at the new bone data) and bone data, the culling sphere grown
    if the new positions stick out of it. Returns ([(type, bytes)], note)."""
    inst = bytearray(nif.blocks[s.skin])
    _, dref, nbones = struct.unpack_from("<iiI", inst, 0)
    if nif.type_of(s.skin) != "BSSkin::Instance" or nbones != 1 or nif.type_of(dref) != "BSSkin::BoneData":
        raise ValueError(f"{stem}: {label}'s skin isn't one bone")
    struct.pack_into("<i", inst, 4, data_k)
    bone = bytearray(nif.blocks[dref])
    if struct.unpack_from("<I", bone, 0)[0] != 1 or len(bone) != 72:
        raise ValueError(f"{stem}: {label}'s bone data isn't one bone")
    rot = np.array(struct.unpack_from("<9f", bone, 20), np.float64).reshape(3, 3)
    trans = np.array(struct.unpack_from("<3f", bone, 56), np.float64)
    cs = np.array(struct.unpack_from("<3f", bone, 4), np.float64)
    rs = struct.unpack_from("<f", bone, 16)[0]
    centre = rot.T @ (cs - trans)
    reach = float(np.linalg.norm(np.asarray(positions, np.float64) - centre, axis=1).max())
    note = f"its culling sphere {label}'s (r {rs:.2f}, holding it to {reach:.2f})"
    if reach > rs:
        struct.pack_into("<f", bone, 16, float(np.float32(reach * (1 + 1e-6) + 1e-3)))
        note = f"its culling sphere {label}'s grown from r {rs:.2f} to {reach:.2f}"
    return [("BSSkin::Instance", bytes(inst)), ("BSSkin::BoneData", bytes(bone))], note


def add_shell(nif, stem, nm, kind, label, src_label, x, R, t, parent, rim, alpha=None):
    """A shell of src_label appended to the nif (in place): its source's vertex records with the positions x["q"] (parked
    frame) through (R, t), x["f"] its triangles over x["used"] of them; its source's skin and bone data copied (the
    sphere grown if it must), the rim styles' invisible shader block with its own materials file's name and
    Double_Sided off, their texture set and alpha property copied (or `alpha`'s bytes: 2026-11-22a's blending one);
    under `parent`. Returns the report line."""
    k = nif.shape_named(f"{nm}_{src_label}")
    s = BC.TriShape(nif.blocks[k])
    if s.alpha >= 0 or nif.blocks[k][4:8] != b"\0\0\0\0":
        raise ValueError(f"{stem}_{src_label}: an alpha property or extra data")
    pos = x["q"] @ R.T + t
    records = with_positions(s, s.records[x["used"]], pos)
    shape_k = len(nif.blocks)
    nxt = shape_k + 1
    skin_k = data_k = -1
    if s.skin >= 0:
        skin_k, data_k = nxt, nxt + 1
        nxt += 2
    shader_k, tex_k, alpha_k = nxt, nxt + 1, nxt + 2
    name_idx = LE.string_index(nif, f"{nm}_{label}".encode("ascii"))
    head = struct.pack("<i", name_idx) + s.head[4:]
    order = [("BSTriShape", s.pack(head=head, bound=BC.bound_of(pos), refs=(skin_k, shader_k, alpha_k),
                                   records=records, tris=x["f"]))]
    note = ""
    if s.skin >= 0:
        blocks, note = skin_copy(nif, s, data_k, pos, stem, src_label)
        order += blocks
    sh = bytearray(nif.blocks[rim.shader])
    struct.pack_into("<i", sh, 4, LE.string_index(nif, material_name(label, kind).encode("ascii")))
    struct.pack_into("<i", sh, 40, tex_k)
    f2 = struct.unpack_from("<I", sh, 20)[0]
    struct.pack_into("<I", sh, 20, f2 & ~SF2_DOUBLE_SIDED)   # one-sided
    tex = struct.unpack_from("<i", nif.blocks[rim.shader], 40)[0]
    order += [("BSLightingShaderProperty", bytes(sh)), ("BSShaderTextureSet", nif.blocks[tex]),
              ("NiAlphaProperty", nif.blocks[rim.alpha] if alpha is None else alpha)]
    for i, (tn, b) in enumerate(order):
        if nif.add_block(tn, b) != shape_k + i:
            raise AssertionError("block numbering")
    nif.blocks[parent] = BC.with_child(nif.blocks[parent], shape_k)
    return (f"{nm}_{label}: blocks {shape_k}-{shape_k + len(order) - 1}, {len(records)} of {src_label}'s "
            f"{len(s.records)} vertices, {len(x['f'])} of its {len(s.tris)} triangles, materials file "
            f"{material_name(label, kind)}, one-sided" + (f"; {note}" if note else ""))


def patch_nif(src: bytes, stem: str, nm: str, kind: str, shapes, R, t, fender_v, donor: bytes):
    """The nif with the three new shapes (and the rear patch raised when fender_v is given): (bytes, report lines,
    the node that holds them)."""
    nif = BC.Nif(src)
    if nif.write() != src:
        raise ValueError(f"{stem}: the nif doesn't read back to its own bytes")
    kp = nif.shape_named(f"{nm}_static_paint")
    parents = [b for b in range(len(nif.blocks)) if nif.type_of(b) in ("NiNode", "BSFadeNode")
               and kp in BC.node_children(nif.blocks[b])[1]]
    if len(parents) != 1:
        raise ValueError(f"{stem}: static_paint under {len(parents)} nodes")
    parent = parents[0]
    kr, kf = nif.shape_named(f"{nm}_{RIM}"), nif.shape_named(f"{nm}_{FENDER}")
    if kr is None or kf is None:
        raise ValueError(f"{stem}: no {RIM} or {FENDER} (the invisible shapes the new ones are made as)")
    rim, fen = BC.TriShape(nif.blocks[kr]), BC.TriShape(nif.blocks[kf])
    lines = []
    for label, src_label in SHELLS:
        lines.append(add_shell(nif, stem, nm, kind, label, src_label, shapes[label], R, t, parent, rim))
    # the front patch: the donor's shape block, fork_paint's skin copied, the rear patch's shader, texture set and alpha
    dn = BC.Nif(donor)
    kd = dn.shape_named(f"{nm}_{PATCH}")
    if kd is None:
        raise ValueError(f"{stem}: the donor has no {nm}_{PATCH}")
    ds = BC.TriShape(dn.blocks[kd])
    ps = BC.TriShape(nif.blocks[nif.shape_named(f"{nm}_{PATCH_ON}")])
    if ds.desc != ps.desc:
        raise ValueError(f"{stem}_{PATCH}: the donor's vertex format {ds.desc:#018x}, {PATCH_ON}'s {ps.desc:#018x}")
    if ds.head[12:16] != ps.head[12:16] or ds.head[16:72] != ps.head[16:72]:
        raise ValueError(f"{stem}_{PATCH}: the donor's flags or transform aren't {PATCH_ON}'s")
    if (ds.skin >= 0) != (ps.skin >= 0) or ds.alpha < 0:
        raise ValueError(f"{stem}_{PATCH}: skinned {ds.skin >= 0} ({PATCH_ON} {ps.skin >= 0}), alpha {ds.alpha}")
    dsh = dn.blocks[ds.shader]
    fsh = nif.blocks[fen.shader]
    # the donor's shader as the rear patch's but the materials file's name (and its own texture set's ref)
    if dn.type_of(ds.shader) != "BSLightingShaderProperty" or dsh[:4] + dsh[8:40] + dsh[44:60] + dsh[64:] != \
            fsh[:4] + fsh[8:40] + fsh[44:60] + fsh[64:]:
        raise ValueError(f"{stem}_{PATCH}: the donor's shader property isn't {FENDER}'s but the materials file's name")
    if dn.blocks[struct.unpack_from("<i", dsh, 40)[0]] != nif.blocks[struct.unpack_from("<i", fsh, 40)[0]]:
        raise ValueError(f"{stem}_{PATCH}: the donor's texture set isn't {FENDER}'s")
    if dn.blocks[ds.alpha][4:] != nif.blocks[fen.alpha][4:]:
        raise ValueError(f"{stem}_{PATCH}: the donor's alpha property isn't {FENDER}'s")
    shape_k = len(nif.blocks)
    nxt = shape_k + 1
    skin_k = data_k = -1
    if ps.skin >= 0:
        skin_k, data_k = nxt, nxt + 1
        nxt += 2
    shader_k, tex_k, alpha_k = nxt, nxt + 1, nxt + 2
    name_idx = LE.string_index(nif, f"{nm}_{PATCH}".encode("ascii"))
    order = [("BSTriShape", ds.pack(head=struct.pack("<i", name_idx) + ds.head[4:], refs=(skin_k, shader_k, alpha_k)))]
    note = ""
    if ps.skin >= 0:
        blocks, note = skin_copy(nif, ps, data_k, ds.positions(), stem, PATCH_ON)
        order += blocks
        at = ((ds.desc >> 28) & 0xF) * 4
        if not (ds.records[:, at:at + 12] == ps.records[0, at:at + 12]).all():
            raise ValueError(f"{stem}_{PATCH}: the donor's skin weights aren't one bone at 1 as {PATCH_ON}'s")
    sh = bytearray(fsh)
    struct.pack_into("<i", sh, 4, LE.string_index(nif, material_name(PATCH, kind).encode("ascii")))
    struct.pack_into("<i", sh, 40, tex_k)
    order += [("BSLightingShaderProperty", bytes(sh)), ("BSShaderTextureSet", nif.blocks[struct.unpack_from("<i", fsh, 40)[0]]),
              ("NiAlphaProperty", nif.blocks[fen.alpha])]
    for i, (tn, b) in enumerate(order):
        if nif.add_block(tn, b) != shape_k + i:
            raise AssertionError("block numbering")
    nif.blocks[parent] = BC.with_child(nif.blocks[parent], shape_k)
    lines.append(f"{nm}_{PATCH}: blocks {shape_k}-{shape_k + len(order) - 1}, {len(ds.records)} vertices, {len(ds.tris)} "
                 f"triangles, materials file {material_name(PATCH, kind)}" + (f"; {note}" if note else ""))
    # the rear patch raised along its own normals
    if fender_v is not None:
        pos = fender_v @ R.T + t
        nif.blocks[kf] = fen.pack(bound=BC.bound_of(pos), records=with_positions(fen, fen.records, pos))
        lines.append(f"{nm}_{FENDER}: raised {SP.FENDER_RAISE:g} along its normals (its positions alone)")
        if fen.skin >= 0:
            bone = nif.blocks[struct.unpack_from("<i", nif.blocks[fen.skin], 4)[0]]
            rot = np.array(struct.unpack_from("<9f", bone, 20)).reshape(3, 3)
            cs = np.array(struct.unpack_from("<3f", bone, 4))
            centre = rot.T @ (cs - np.array(struct.unpack_from("<3f", bone, 56)))
            if np.linalg.norm(pos - centre, axis=1).max() > struct.unpack_from("<f", bone, 16)[0]:
                raise ValueError(f"{stem}_{FENDER}: raised, it leaves its culling sphere")
    return nif.write(), lines, parent


def verify(before: bytes, after: bytes, stem: str, nm: str, kind: str, shapes, R, t, fender_v):
    """Byte-level checks of a patched nif against its source. Returns (problems, the worst position error)."""
    bad = []
    a, b = BC.Nif(before), BC.Nif(after)
    if b.write() != after:
        bad.append("the output doesn't read back to its own bytes")
    names = [b.name_of(k) for k in b.shapes()]
    want = [a.name_of(k) for k in a.shapes()] + [f"{nm}_{label}" for label in LABELS]
    if names != want:
        bad.append(f"shapes {names[len(a.shapes()):]}: not the source's and the three in order")
    kf = a.shape_named(f"{nm}_{FENDER}")
    parents = [p for p in range(len(a.blocks)) if a.type_of(p) in ("NiNode", "BSFadeNode")
               and BC.node_children(a.blocks[p])[1] != BC.node_children(b.blocks[p])[1]]
    if len(parents) != 1:
        return bad + [f"{len(parents)} nodes changed"], np.inf
    parent = parents[0]
    for i in range(len(a.blocks)):
        if a.type_of(i) != b.type_of(i):
            bad.append(f"block {i}'s type changed")
        if i == parent or (i == kf and fender_v is not None):
            continue
        if a.blocks[i] != b.blocks[i]:
            bad.append(f"block {i} ({a.type_of(i)}) changed")
    if b.strings[:len(a.strings)] != a.strings:
        bad.append("the string table: the source's strings not kept in place")
    kids_a, kids_b = BC.node_children(a.blocks[parent])[1], BC.node_children(b.blocks[parent])[1]
    if kids_b[:len(kids_a)] != kids_a or [b.name_of(k) for k in kids_b[len(kids_a):]] != [f"{nm}_{lb}" for lb in LABELS]:
        bad.append("the node's children: not the source's and the three after them")
    worst = 0.0

    def tol_of(s, p):
        return 1e-4 + (0.0 if s.full else np.abs(p).max() * 2.0 ** -11)

    for label, src in SHELLS:
        s = BC.TriShape(b.blocks[b.shape_named(f"{nm}_{label}")])
        so = BC.TriShape(a.blocks[a.shape_named(f"{nm}_{src}")])
        x = shapes[label]
        want_p = x["q"] @ R.T + t
        got = s.positions()
        d = float(np.abs(got - want_p).max())
        worst = max(worst, d)
        if d > tol_of(s, want_p) or (not s.full and not np.array_equal(got, SP.half(want_p))):
            bad.append(f"{label}: its positions {d:.5f} off the fitted ones")
        # every record byte its source vertex's but the position (the half floats' first 6 bytes, the floats' first 12)
        cut = 12 if s.full else 6
        if s.desc != so.desc or not np.array_equal(s.records[:, cut:], so.records[x["used"], cut:]):
            bad.append(f"{label}: its records aren't {src}'s but the positions")
        if not np.array_equal(s.tris, x["f"]) or s.head[4:] != so.head[4:]:
            bad.append(f"{label}: its triangles, flags or transform")
        sh = b.blocks[s.shader]
        if b.strings[struct.unpack_from("<i", sh, 4)[0]].decode() != material_name(label, kind) \
                or struct.unpack_from("<I", sh, 20)[0] & SF2_DOUBLE_SIDED:
            bad.append(f"{label}: its materials file or two-sidedness")
        if kind == "worn":
            ia, ib = a.blocks[so.skin], b.blocks[s.skin]
            da, db = struct.unpack_from("<i", ia, 4)[0], struct.unpack_from("<i", ib, 4)[0]
            if b.type_of(s.skin) != "BSSkin::Instance" or ia[:4] != ib[:4] or ia[8:] != ib[8:] or da == db \
                    or a.blocks[da][20:] != b.blocks[db][20:] or a.blocks[da][:16] != b.blocks[db][:16]:
                bad.append(f"{label}: its skin isn't its own copy of {src}'s (the same bone, bind and sphere's centre)")
        elif s.skin != -1:
            bad.append(f"{label}: skinned in an unskinned nif")
    s = BC.TriShape(b.blocks[b.shape_named(f"{nm}_{PATCH}")])
    x = shapes[PATCH]
    want_p = x["v"] @ R.T + t
    d = float(np.abs(s.positions() - want_p).max())
    worst = max(worst, d)
    if d > tol_of(s, want_p) or not np.array_equal(s.tris, x["f"]):
        bad.append(f"{PATCH}: its positions {d:.5f} off, or its triangles")
    if np.abs(s.uvs() - x["uv"]).max() > 2.0 ** -11 + 1e-6:
        bad.append(f"{PATCH}: its UVs")
    if fender_v is not None:
        s = BC.TriShape(b.blocks[kf])
        so = BC.TriShape(a.blocks[kf])
        want_p = fender_v @ R.T + t
        cut = 12 if s.full else 6
        if float(np.abs(s.positions() - want_p).max()) > tol_of(s, want_p) or \
                not np.array_equal(s.records[:, cut:], so.records[:, cut:]) or not np.array_equal(s.tris, so.tris):
            bad.append(f"{FENDER}: not its own vertices raised (the rest of each record as it was)")
    return bad, worst


def pynifly_check(path: Path, before: Path, nm: str, kind: str, shapes, R, t, pynifly: Path):
    """Read the output back through PyNifly: the shapes' names and order, the three last; the patch's vertices, UVs and
    triangles, each new shape's materials file, skinned to its source's bone in the worn nifs, under its source's node."""
    sys.path.insert(0, str(pynifly))
    import logging
    logging.disable(logging.WARNING)
    from pyn.pynifly import NifFile
    bad = []
    a, b = NifFile(str(before)), NifFile(str(path))
    na, nb = [s.name for s in a.shapes], [s.name for s in b.shapes]
    if nb != na + [f"{nm}_{label}" for label in LABELS]:
        bad.append(f"shapes {len(nb)}: not the source's {len(na)} and the three last")
    by = {s.name: s for s in b.shapes}
    for label in LABELS:
        s = by.get(f"{nm}_{label}")
        src = by.get(f"{nm}_{dict(SHELLS).get(label, PATCH_ON)}")
        if s is None or src is None:
            bad.append(f"{label}: missing")
            continue
        if (s.shader.name or "") != material_name(label, kind):
            bad.append(f"{label}: materials file {s.shader.name!r}")
        if s.has_skin_instance != (kind == "worn") or (kind == "worn" and list(s.bone_names) != list(src.bone_names)):
            bad.append(f"{label}: skinned {s.has_skin_instance}")
        if (s.parent.name if s.parent else None) != (src.parent.name if src.parent else None):
            bad.append(f"{label}: under {s.parent.name if s.parent else None}")
        if label in dict(SHELLS):
            x = shapes[label]
            if len(s.verts) != len(x["q"]) or np.abs(np.asarray(s.uvs) - np.asarray(src.uvs)[x["used"]]).max() > 1e-6:
                bad.append(f"{label}: its UVs aren't its source vertices'")
    x = shapes[PATCH]
    s = by.get(f"{nm}_{PATCH}")
    if s is not None:
        want = x["v"] @ R.T + t
        tol = 1e-4 + (0.0 if kind != "worn" else np.abs(want).max() * 2.0 ** -11)
        if np.asarray(s.verts).shape != want.shape or np.abs(np.asarray(s.verts) - want).max() > tol \
                or not np.array_equal(np.asarray(s.tris), x["f"]) or np.abs(np.asarray(s.uvs) - x["uv"]).max() > 2.0 ** -11 + 1e-6:
            bad.append(f"{PATCH}: its vertices, triangles or UVs")
    a.close()
    b.close()
    return bad


# --- 2026-11-22a (round t64): the paint condition shells, the wear on more parts, static_wear over the badges --------

PAINTWEAR = SP.PAINTWEAR_SHELLS
PARTS = SP.PART_SHELLS
B_LABELS = tuple(lb for lb, _ in PAINTWEAR) + tuple(lb for lb, _, _ in PARTS)
B_SOURCES = dict(list(PAINTWEAR) + [(lb, src) for lb, src, _ in PARTS])
HELMETS = tuple(label for label, _, _ in EP.SHAPES)   # 2026-11-16a's 3D helmets: alternatives, shown only when chosen
# the look's alternatives drawn only when chosen (invisible by default): the helmets, the rim styles, the under-bar
# mirrors; a shell inside one is seen whenever it isn't chosen (and hidden inside it when it is), so not cut there
ALTERNATIVES = HELMETS + tuple(lb for lb, _ in H.RIM_STYLE_LABELS) + H.PARKED_OFF


def b_wanted(args):
    """The 2026-11-22a labels the flags ask for, in their order."""
    return tuple(lb for lb, _ in PAINTWEAR if args.paintwear) + tuple(lb for lb, _, _ in PARTS if args.parts)


def build_shapes_b(data, fr, args, log):
    """The 2026-11-22a geometry in the parked frame: {label: dict} for static_wear (rebuilt over the badges, with
    --badge-lift) and each new shell the flags ask for."""
    pk = BC.Nif(data["CMB_BikeParked"])
    wn = BC.Nif(data["CMB_BikeWorn"])
    R, t = fr["CMB_BikeWorn"][:2]
    # the inside test: every shape but the open sheets, the alternatives (the helmets, the rim styles, the under-bar
    # mirrors: grime under an unchosen one is seen) and the shells themselves
    skip = ALTERNATIVES + LABELS + B_LABELS
    pk_solids = solids(pk, "CMB_Bike", skip)
    wn_solids = solids(wn, "CMB_BikeWorn", skip)
    out = {}

    def make(label, src, lift, keep, tri_mask=None, extra=None, by_piece=False):
        v, f, n, _ = geometry(pk, f"CMB_Bike_{src}")
        vw = geometry(wn, f"CMB_BikeWorn_{src}")[0]
        for stem, nm, kind in NIFS:   # the three worn nifs' sources the same half floats
            if kind == "worn" and not np.array_equal(geometry(BC.Nif(data[stem]), f"{nm}_{src}")[0], vw):
                raise ValueError(f"{stem}_{src}: not CMB_BikeWorn's positions")
        fs = f if tri_mask is None else f[tri_mask]
        log(f"  {label}: a shell of {src} ({len(v)} vertices, {len(fs)} of its {len(f)} triangles), "
            + (f"{lift:g} over it" if np.ndim(lift) == 0 else f"{SP.SHELL_LIFT:g} over it, up to {float(np.max(lift)):.3f} over the badges"))
        q, na, num = SP.shell_positions(v, fs, n, worn=(R, t, vw), lift=lift, log=log, keep=SP.SHELL_FIT_KEEP,
                                        by_piece=by_piece)
        used_by = np.zeros(len(v), bool)
        used_by[np.unique(fs)] = True
        in_p = np.full(len(v), None, dtype=object)
        in_w = np.full(len(v), None, dtype=object)
        ub = np.where(used_by)[0]
        in_p[ub] = SP.inside_shapes(q[ub], pk_solids)
        in_w[ub] = SP.inside_shapes(SP.half(q[ub] @ R.T + t), wn_solids)
        if by_piece:   # a piece's shell nearer another piece of the source than the band (overlapping pieces: a
            # muffler inside its pipe's sleeve, a clamp round a pipe), or off the band over its own piece where the half
            # floats' step leaves no point in it: out as well
            qw = SP.half(q @ R.T + t)
            dp = SP.surface_distance(q[ub], v[fs], reach=0.7)
            dw = SP.surface_distance(qw[ub], vw[fs], reach=0.7)
            near = (dp < SP.SHELL_BAND[0]) | (dw < SP.SHELL_BAND[0] - 0.003)
            pos, _ = SP.weld_positions(v)
            lab = BP.islands(int(pos.max()) + 1, pos[fs])
            own_out = np.zeros(len(v), bool)
            for k in range(int(lab.max()) + 1):
                fk = fs[lab == k]
                vk = np.unique(fk)
                ok_ = SP.surface_distance(q[vk], v[fk], reach=0.7)
                ow_ = SP.surface_distance(qw[vk], vw[fk], reach=0.7)
                own_out[vk] = (ok_ > SP.SHELL_BAND[1]) | (ow_ > SP.SHELL_BAND[1] + 0.003)
            for i in ub[near | own_out[ub]]:
                if in_p[i] is None and in_w[i] is None:
                    in_p[i] = f"{src} (off {SP.SHELL_BAND[0]:g}-{SP.SHELL_BAND[1]:g} from its surface)"
        inside = (in_p != None) | (in_w != None)  # noqa: E711
        keep_t, used, nf = SP.keep_outside(fs, inside)
        dips = 0
        if by_piece:   # a part shell's triangle whose inside comes under SHELL_FLOOR (and a little) of the source (a chord
            # over a sharp fold of a thin part), in full precision or the half floats: out as well
            smp, _ = SP.triangle_samples(q, fs)
            ds = SP.surface_distance(smp.reshape(-1, 3), v[fs], reach=0.7).reshape(len(fs), -1).min(axis=1)
            smw, _ = SP.triangle_samples(SP.half(q @ R.T + t), fs)
            dw = SP.surface_distance(smw.reshape(-1, 3), vw[fs], reach=0.7).reshape(len(fs), -1).min(axis=1)
            dip = (ds < SP.SHELL_FLOOR + 0.01) | (dw < SP.SHELL_FLOOR + 0.01)
            dips = int((dip & keep_t).sum())
            keep_t = keep_t & ~dip
            used = np.unique(fs[keep_t])
            remap = np.full(len(v), -1, np.int64)
            remap[used] = np.arange(len(used))
            nf = remap[fs[keep_t]]
        why = {}
        for h in set(np.where(inside & used_by)[0].tolist()):
            lb = in_p[h] if in_p[h] is not None else in_w[h]
            why[lb] = why.get(lb, 0) + 1
        log(f"    {int((inside & used_by).sum())} of its vertices inside another shape "
            f"({', '.join(f'{k} {c}' for k, c in sorted(why.items())) or 'none'})"
            + (f", {dips} more triangles dipping under {SP.SHELL_FLOOR + 0.01:g} of it" if dips else "")
            + f": {int((~keep_t).sum())} triangles left out, {int(keep_t.sum())} kept on {len(used)} vertices")
        x = dict(src=src, used=used, f=nf, q=q[used], numbers=num, inside=why, dropped=int((~keep_t).sum()),
                 vertices=len(used), triangles=int(keep_t.sum()))
        if np.ndim(lift):
            x["lift"] = np.asarray(lift)[used]
        if extra:
            x.update(extra)
        out[label] = x

    if args.badge_lift:   # static_wear rebuilt: over the badges' footprints, and the helmets no longer cut out
        v, f, n, _ = geometry(pk, "CMB_Bike_static_paint")
        pos, _ = SP.weld_positions(v)
        na = SP.averaged_normals(n, pos)[pos]
        sheets = {lb: geometry(pk, f"CMB_Bike_{lb}")[:2] for lb in SP.BADGE_SHEETS}
        lift, count = SP.badge_lifts(v, na, v[f], sheets, f=f)
        log(f"  static_wear over the badges: {', '.join(f'{k} {c}' for k, c in count.items())} vertices lifted (up to "
            f"{lift.max():.3f} over the paint, {SP.BADGE_OVER:g} over each sheet on {SP.BADGE_MARGIN:g} round it, ramped "
            f"back to {SP.SHELL_LIFT:g} over {SP.BADGE_RAMP:g})")
        make("static_wear", "static_paint", lift, SP.SHELL_FIT_KEEP, extra=dict(badges=count))
    for label, src in PAINTWEAR:
        if args.paintwear:
            make(label, src, SP.PAINTWEAR_LIFT, SP.SHELL_FIT_KEEP)
    total = 0
    for label, src, covers in PARTS:
        if not args.parts:
            continue
        mask, found = None, None
        if covers:
            v, f, _, _ = geometry(pk, f"CMB_Bike_{src}")
            mask, found = SP.select_pieces(v, f, covers)
            log(f"  {label}: {src}'s pieces " + ", ".join(f"{n} triangles (area {a:.1f})" for n, a in found))
        total += int(mask.sum()) if mask is not None else len(geometry(pk, f"CMB_Bike_{src}")[1])
        make(label, src, SP.SHELL_LIFT, SP.SHELL_FIT_KEEP, tri_mask=mask, extra=dict(pieces=found), by_piece=True)
    if args.parts and total > SP.PART_TRIS_MAX:
        raise ValueError(f"the part shells cover {total} triangles, over PART_TRIS_MAX {SP.PART_TRIS_MAX}")
    return out


GLASS = "static_glass"    # its NiAlphaProperty blends (0x12ED, threshold 0): the overlay shells' since 2026-11-22a
OVERLAYS_A = tuple(lb for lb, _ in SHELLS)   # 21a's two wear shells (fork_badgeFront is a badge patch, not an overlay)


def blend_alpha(nif, nm):
    """The bytes of the nif's glass's NiAlphaProperty (blending on, test GREATER 0: the apply unit's finding, test 58:
    a material swap at the 3D's load turns blending on only where the shape's own property and file already blend)."""
    kg = nif.shape_named(f"{nm}_{GLASS}")
    g = BC.TriShape(nif.blocks[kg]) if kg is not None else None
    if g is None or g.alpha < 0 or nif.type_of(g.alpha) != "NiAlphaProperty":
        raise ValueError(f"{nm}: no {GLASS} with an alpha property to make the overlays' as")
    b = nif.blocks[g.alpha]
    flags, thr = struct.unpack_from("<HB", b, 12)
    if not flags & 1 or thr != 0:
        raise ValueError(f"{nm}_{GLASS}'s alpha property: flags {flags:#06x} threshold {thr} (blending on, threshold 0 expected)")
    return b


def patch_nif_b(src: bytes, stem: str, nm: str, kind: str, shapes, R, t, labels, blend=False):
    """The nif (21a's shapes in it) with static_wear rebuilt (when shapes has it), the shells `labels` appended and, with
    blend, every overlay shell's alpha property the glass's (21a's two rewritten in place): (bytes, report lines, the
    node that holds them, the other blocks changed in place)."""
    nif = BC.Nif(src)
    if nif.write() != src:
        raise ValueError(f"{stem}: the nif doesn't read back to its own bytes")
    kp = nif.shape_named(f"{nm}_static_paint")
    parents = [b for b in range(len(nif.blocks)) if nif.type_of(b) in ("NiNode", "BSFadeNode")
               and kp in BC.node_children(nif.blocks[b])[1]]
    if len(parents) != 1:
        raise ValueError(f"{stem}: static_paint under {len(parents)} nodes")
    parent = parents[0]
    kr = nif.shape_named(f"{nm}_{RIM}")
    if kr is None:
        raise ValueError(f"{stem}: no {RIM} (the invisible shape the new ones are made as)")
    rim = BC.TriShape(nif.blocks[kr])
    lines, grown = [], None
    if "static_wear" in shapes:
        x = shapes["static_wear"]
        kw = nif.shape_named(f"{nm}_static_wear")
        if kw is None:
            raise ValueError(f"{stem}: no static_wear to rebuild (2026-11-21a's shapes first: --shells 1)")
        sw, sp_ = BC.TriShape(nif.blocks[kw]), BC.TriShape(nif.blocks[kp])
        pos = x["q"] @ R.T + t
        nif.blocks[kw] = sw.pack(bound=BC.bound_of(pos), records=with_positions(sp_, sp_.records[x["used"]], pos),
                                 tris=x["f"])
        note = ""
        if sw.skin >= 0:
            dref = struct.unpack_from("<i", nif.blocks[sw.skin], 4)[0]
            bone = bytearray(nif.blocks[dref])
            rot = np.array(struct.unpack_from("<9f", bone, 20), np.float64).reshape(3, 3)
            centre = rot.T @ (np.array(struct.unpack_from("<3f", bone, 4)) - np.array(struct.unpack_from("<3f", bone, 56)))
            rs = struct.unpack_from("<f", bone, 16)[0]
            reach = float(np.linalg.norm(pos - centre, axis=1).max())
            note = f"; its culling sphere holds it (r {rs:.2f}, to {reach:.2f})"
            if reach > rs:
                struct.pack_into("<f", bone, 16, float(np.float32(reach * (1 + 1e-6) + 1e-3)))
                nif.blocks[dref] = bytes(bone)
                grown = dref
                note = f"; its culling sphere grown from r {rs:.2f} to {reach:.2f}"
        lines.append(f"{nm}_static_wear rebuilt: {len(x['used'])} vertices, {len(x['f'])} triangles, over the badges"
                     + note)
    changed = set() if grown is None else {grown}
    alpha = blend_alpha(nif, nm) if blend else None
    if blend:
        for label in OVERLAYS_A:
            k = nif.shape_named(f"{nm}_{label}")
            s_ = BC.TriShape(nif.blocks[k])
            if s_.alpha < 0 or nif.type_of(s_.alpha) != "NiAlphaProperty":
                raise ValueError(f"{stem}_{label}: no alpha property of its own")
            if nif.blocks[s_.alpha] != alpha:
                nif.blocks[s_.alpha] = alpha
                changed.add(s_.alpha)
            lines.append(f"{nm}_{label}: its alpha property blends (the glass's: {struct.unpack_from('<H', alpha, 12)[0]:#06x}, "
                         f"threshold {alpha[14]})")
    for label in labels:
        lines.append(add_shell(nif, stem, nm, kind, label, B_SOURCES[label], shapes[label], R, t, parent, rim, alpha))
    return nif.write(), lines, parent, changed


def verify_b(before: bytes, after: bytes, stem: str, nm: str, kind: str, shapes, R, t, labels, grown, blend=False):
    """Byte-level checks of a 2026-11-22a nif against its 2026-11-21a source (grown: the other blocks changed in place:
    a grown culling sphere, 21a's shells' alpha properties). Returns (problems, the worst error)."""
    bad = []
    a, b = BC.Nif(before), BC.Nif(after)
    if b.write() != after:
        bad.append("the output doesn't read back to its own bytes")
    names = [b.name_of(k) for k in b.shapes()]
    want = [a.name_of(k) for k in a.shapes()] + [f"{nm}_{label}" for label in labels]
    if names != want:
        bad.append(f"shapes {names[len(a.shapes()):]}: not the source's and the new ones in order")
    kw = a.shape_named(f"{nm}_static_wear")
    changed = {kw} if "static_wear" in shapes else set()
    changed |= set(grown or ())
    if blend:   # every overlay shell's alpha property the glass's, 21a's two rewritten in place (and only those)
        glass = blend_alpha(b, nm)
        for label in OVERLAYS_A + tuple(labels):
            s_ = BC.TriShape(b.blocks[b.shape_named(f"{nm}_{label}")])
            if b.blocks[s_.alpha] != glass:
                bad.append(f"{label}: its alpha property isn't the glass's (blending)")
    allowed = {BC.TriShape(a.blocks[a.shape_named(f"{nm}_{lb}")]).alpha for lb in OVERLAYS_A} if blend else set()
    sw_a = BC.TriShape(a.blocks[kw])
    if sw_a.skin >= 0:
        allowed.add(struct.unpack_from("<i", a.blocks[sw_a.skin], 4)[0])   # static_wear's bone data (its sphere)
    if set(grown or ()) - allowed:
        bad.append(f"blocks {sorted(set(grown) - allowed)} changed in place beyond static_wear's sphere and the two shells' "
                   f"alpha properties")
    parents = [p for p in range(len(a.blocks)) if a.type_of(p) in ("NiNode", "BSFadeNode")
               and BC.node_children(a.blocks[p])[1] != BC.node_children(b.blocks[p])[1]]
    if len(parents) != (1 if labels else 0):
        return bad + [f"{len(parents)} nodes changed"], np.inf
    for i in range(len(a.blocks)):
        if a.type_of(i) != b.type_of(i):
            bad.append(f"block {i}'s type changed")
        if i in parents or i in changed:
            continue
        if a.blocks[i] != b.blocks[i]:
            bad.append(f"block {i} ({a.type_of(i)}) changed")
    if b.strings[:len(a.strings)] != a.strings:
        bad.append("the string table: the source's strings not kept in place")
    worst = 0.0
    todo = (["static_wear"] if "static_wear" in shapes else []) + list(labels)
    for label in todo:
        x = shapes[label]
        src = x["src"]
        s = BC.TriShape(b.blocks[b.shape_named(f"{nm}_{label}")])
        so = BC.TriShape(a.blocks[a.shape_named(f"{nm}_{src}")])
        want_p = x["q"] @ R.T + t
        got = s.positions()
        d = float(np.abs(got - want_p).max())
        worst = max(worst, d)
        tol = 1e-4 + (0.0 if s.full else np.abs(want_p).max() * 2.0 ** -11)
        if d > tol or (not s.full and not np.array_equal(got, SP.half(want_p))):
            bad.append(f"{label}: its positions {d:.5f} off the fitted ones")
        cut = 12 if s.full else 6
        if s.desc != so.desc or not np.array_equal(s.records[:, cut:], so.records[x["used"], cut:]):
            bad.append(f"{label}: its records aren't {src}'s but the positions")
        if not np.array_equal(s.tris, x["f"]) or s.head[4:] != so.head[4:]:
            bad.append(f"{label}: its triangles, flags or transform")
        sh = b.blocks[s.shader]
        if b.strings[struct.unpack_from("<i", sh, 4)[0]].decode() != material_name(label, kind) \
                or struct.unpack_from("<I", sh, 20)[0] & SF2_DOUBLE_SIDED:
            bad.append(f"{label}: its materials file or two-sidedness")
        if kind == "worn":
            ia, ib = a.blocks[so.skin], b.blocks[s.skin]
            da, db = struct.unpack_from("<i", ia, 4)[0], struct.unpack_from("<i", ib, 4)[0]
            if b.type_of(s.skin) != "BSSkin::Instance" or ia[:4] != ib[:4] or ia[8:] != ib[8:] or da == db \
                    or a.blocks[da][20:] != b.blocks[db][20:] or a.blocks[da][:16] != b.blocks[db][:16]:
                bad.append(f"{label}: its skin isn't its own copy of {src}'s (the same bone, bind and sphere's centre)")
        elif s.skin != -1:
            bad.append(f"{label}: skinned in an unskinned nif")
    return bad, worst


def pynifly_check_b(path: Path, before: Path, nm: str, kind: str, shapes, labels, pynifly: Path):
    """Read a 2026-11-22a output back through PyNifly: the new shapes last, in order; each one's materials file, skin,
    parent and UVs (its source vertices')."""
    sys.path.insert(0, str(pynifly))
    import logging
    logging.disable(logging.WARNING)
    from pyn.pynifly import NifFile
    bad = []
    a, b = NifFile(str(before)), NifFile(str(path))
    na, nb = [s.name for s in a.shapes], [s.name for s in b.shapes]
    if nb != na + [f"{nm}_{label}" for label in labels]:
        bad.append(f"shapes {len(nb)}: not the source's {len(na)} and the new ones last")
    by = {s.name: s for s in b.shapes}
    for label in (["static_wear"] if "static_wear" in shapes else []) + list(labels):
        x = shapes[label]
        s, src = by.get(f"{nm}_{label}"), by.get(f"{nm}_{x['src']}")
        if s is None or src is None:
            bad.append(f"{label}: missing")
            continue
        if (s.shader.name or "") != material_name(label, kind):
            bad.append(f"{label}: materials file {s.shader.name!r}")
        if s.has_skin_instance != (kind == "worn") or (kind == "worn" and list(s.bone_names) != list(src.bone_names)):
            bad.append(f"{label}: skinned {s.has_skin_instance}")
        if (s.parent.name if s.parent else None) != (src.parent.name if src.parent else None):
            bad.append(f"{label}: under {s.parent.name if s.parent else None}")
        if len(s.verts) != len(x["q"]) or np.abs(np.asarray(s.uvs) - np.asarray(src.uvs)[x["used"]]).max() > 1e-6:
            bad.append(f"{label}: its UVs aren't its source vertices'")
    a.close()
    b.close()
    return bad


def blended_invisible(m):
    """An own materials file made to blend (2026-11-22a, --overlay-blend 1): alpha 0 (nothing drawn), blending on
    (source alpha, inverse source alpha), the alpha test kept at reference 0 (an alpha-0 texel discarded), no depth
    write: the blend state of the wear's own materials, so a swap at the 3D's load shows them."""
    m = dict(m)
    m.update(alpha=0.0, alpha_blend=1, alpha_blend_src=6, alpha_blend_dst=7, alpha_test=True, alpha_test_ref=0,
             zbuffer_write=False, two_sided=False)
    return m


def write_materials(datas, out: Path, log, b_labels=(), blend=False):
    """The own materials files: the shells' the rim styles' invisible wheelF_rimLaced.bgsm (parked and _worn, the
    same bytes) with two_sided off (2026-11-22a's b_labels too; with blend, made to blend: blended_invisible), the front
    patch's the rear patch's static_badgeFender(_worn).bgsm byte for byte."""
    def find(name):
        path = None
        for d in datas:
            p = d / "Materials" / "CMB" / "Bike" / name
            if p.exists():
                path = p
        if path is None:
            raise FileNotFoundError(f"Materials/CMB/Bike/{name} in none of the --data trees")
        return path
    folder = out / "Materials" / "CMB" / "Bike"
    folder.mkdir(parents=True, exist_ok=True)
    made = {}
    for w in ("", "_worn"):
        m = BG.read(find(f"{RIM}{w}.bgsm"))
        m["two_sided"] = False
        body = BG.dumps(m)
        if blend:
            body = BG.dumps(blended_invisible(m))
        if BG.dumps(BG.loads(find(f"{RIM}{w}.bgsm").read_bytes())) != find(f"{RIM}{w}.bgsm").read_bytes():
            raise ValueError(f"{RIM}{w}.bgsm doesn't read back to its own bytes")
        for label, _ in SHELLS:
            made[f"{label}{w}.bgsm"] = body
        made[f"{PATCH}{w}.bgsm"] = find(f"{FENDER}{w}.bgsm").read_bytes()
        for label in b_labels:
            made[f"{label}{w}.bgsm"] = body
    for name, body in made.items():
        BC.write_file(folder / name, body)
        log(f"  wrote {folder / name}: {len(body)} bytes, sha256 {BC.sha256(body)}")
    return {name: BC.sha256(body) for name, body in made.items()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, action="append", required=True,
                    help="a built Data tree (its Meshes/CMB is read); more than one: a later tree's file wins")
    ap.add_argument("--out", type=Path, required=True, help="where the patched nifs go (a folder; may be Meshes/CMB itself)")
    ap.add_argument("--shells", type=int, choices=(0, 1), default=1,
                    help="1 (2026-11-21a): the wear shells and the front patch added, the rear patch raised; 0: the nifs "
                         "as they are (2026-11-17a's) and no materials file (the 2026-11-22a flags then do nothing)")
    ap.add_argument("--fender-raise", type=float, default=SP.FENDER_RAISE,
                    help=f"how much the rear fender patch is raised along its normals (default {SP.FENDER_RAISE:g}; 0 leaves it)")
    ap.add_argument("--paintwear", type=int, choices=(0, 1), default=1,
                    help="1 (2026-11-22a): the paint condition shells static_paintwear and fork_paintwear; 0: none (2026-11-21a)")
    ap.add_argument("--parts", type=int, choices=(0, 1), default=1,
                    help="1 (2026-11-22a): the wear shells on the exhaust, the engine's covers and the fork lowers; 0: none")
    ap.add_argument("--badge-lift", type=int, choices=(0, 1), default=1,
                    help="1 (2026-11-22a): static_wear rebuilt over the badges' footprints (and no longer cut out under the "
                         "helmets); 0: 2026-11-21a's static_wear")
    ap.add_argument("--overlay-blend", type=int, choices=(0, 1), default=1,
                    help="1 (2026-11-22a): every overlay shell's alpha property blends (the glass's) and its own file blends "
                         "at alpha 0, so a swap at the 3D's load shows the wear; 0: 2026-11-21a's (alpha test 255)")
    ap.add_argument("--bgsm-out", type=Path, help="a Data tree to write the own materials files into (Materials/CMB/Bike)")
    ap.add_argument("--pynifly", type=Path, required=True, help="PyNifly's io_scene_nifly (the donor nif, the read-back)")
    ap.add_argument("--materials", type=Path, default=HERE / "bike_materials.json")
    ap.add_argument("--report", type=Path, help="write the numbers as JSON")
    args = ap.parse_args()
    sources = {stem: LE.resolve(args.data, stem) for stem, _, _ in NIFS}
    data = {stem: p.read_bytes() for stem, p in sources.items()}
    args.out.mkdir(parents=True, exist_ok=True)
    report = dict(shells=args.shells, paintwear=args.paintwear, parts=args.parts, badge_lift=args.badge_lift,
                  overlay_blend=args.overlay_blend,
                  sources={stem: str(p) for stem, p in sources.items()}, nifs={})
    if not args.shells:
        for stem, _, _ in NIFS:
            BC.write_file(args.out / f"{stem}.nif", data[stem])
            print(f"{stem}.nif as it was (--shells 0): sha256 {BC.sha256(data[stem])}")
            report["nifs"][stem] = dict(sha256=BC.sha256(data[stem]), patched=False)
        if args.report:
            args.report.write_text(json.dumps(report, indent=1) + "\n")
        return 0
    todo = [(stem, nm, kind) for stem, nm, kind in NIFS if BC.Nif(data[stem]).shape_named(f"{nm}_{LABELS[0]}") is None]
    if todo and len(todo) != len(NIFS):
        print("some nifs have the shells and some don't: the five must be patched together", file=sys.stderr)
        return 1
    wanted = b_wanted(args)
    have_b = {stem: [lb for lb in B_LABELS if BC.Nif(data[stem]).shape_named(f"{nm}_{lb}") is not None] for stem, nm, _ in NIFS}
    if any(have_b.values()) and any(have_b[stem] != list(wanted) for stem in have_b):
        print(f"the nifs have the 2026-11-22a shells {sorted(set(sum(have_b.values(), [])))}, the flags ask for "
              f"{list(wanted)}: start from 2026-11-21a's nifs", file=sys.stderr)
        return 1
    do_b = bool(wanted or args.badge_lift or args.overlay_blend) and not any(have_b.values())
    if not todo and not do_b:
        for stem, nm, kind in NIFS:
            if args.out.resolve() != sources[stem].parent.resolve():
                BC.write_file(args.out / f"{stem}.nif", data[stem])
            print(f"{stem}.nif: has the shells already: left as it is")
            report["nifs"][stem] = dict(sha256=BC.sha256(data[stem]), patched=False, note="has the shells already")
    bad = []
    out_data = dict(data)
    if todo or do_b:
        sys.path.insert(0, str(args.pynifly))
        import logging
        logging.disable(logging.WARNING)
        from pyn.pynifly import NifFile
        ini = None
        for d in args.data:
            p = d / "Meshes" / "CMB" / "CMB_BikeParts.ini"
            if p.exists():
                ini = p
        if ini is None:
            raise FileNotFoundError("CMB_BikeParts.ini in none of the --data trees")
        data["parts"] = {k: v for k, v in (line.split("=", 1) for line in ini.read_text().splitlines()
                                           if "=" in line and not line.lstrip().startswith(";"))}
        fr = frames(data)
        for stem, (R, t, resid, tol, full) in fr.items():
            print(f"{stem}.nif: the parked frame to its frame R {R.astype(int).tolist() if np.all(R == np.round(R)) else R.round(6).tolist()}, "
                  f"t ({t[0]:.4f}, {t[1]:.4f}, {t[2]:.4f}); static_paint's vertices within {resid:.5f} (tolerance {tol:.5f})")
            if resid > tol:
                bad.append(f"{stem}: static_paint doesn't fit the parked one by a rigid transform ({resid:.5f})")
        if bad:
            for line in bad:
                print(f"FAIL {line}", file=sys.stderr)
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        if todo:   # 2026-11-21a's shapes
            print("the new shapes (shell_pieces.py), in the parked frame:")
            shapes = build_shapes(data, fr, print)
            pk = BC.Nif(data["CMB_BikeParked"])
            fender_v = raised_fender(pk, args.fender_raise) if args.fender_raise else None
            report["shapes"] = {label: {k: x[k] for k in ("vertices", "triangles")} | dict(numbers=x["numbers"],
                                **({"dropped": x["dropped"], "inside": x["inside"]} if label != PATCH else {}))
                                for label, x in shapes.items()}
            report["fender_raise"] = args.fender_raise
            spec_all, _ = H.load_shaders(args.materials if args.materials and args.materials.exists() else None)
            spec = spec_all[FENDER]
            pkf = NifFile(str(sources["CMB_BikeParked"]))
            base = H.Base(pkf.shapes[0])
            base.props.flags = base.props.flags & ~1   # the master's shape, which the parked nif hides: ours are shown
            for stem, nm, kind in NIFS:
                R, t = fr[stem][:2]
                src = data[stem]
                textures = H.texture_paths(spec, H.OFF_MAT if not spec.get("textures_of") else spec["textures_of"],
                                           kind != "parked", False)
                donor = donor_patch(Path(tmp) / f"{stem}_donor.nif", nm, kind, shapes[PATCH], R, t, base, spec, textures)
                out, lines, parent = patch_nif(src, stem, nm, kind, shapes, R, t, fender_v, donor)
                problems, worst = verify(src, out, stem, nm, kind, shapes, R, t, fender_v)
                print(f"{stem}.nif (2026-11-21a's shapes):")
                for line in lines:
                    print(f"  {line}")
                print(f"  under block {parent}; the new positions at most {worst:.5f} off the fitted ones")
                bad += [f"{stem}: {p}" for p in problems]
                path = Path(tmp) / f"{stem}_a.nif"
                path.write_bytes(out)
                before = Path(tmp) / f"{stem}.nif"
                before.write_bytes(src)
                problems = pynifly_check(path, before, nm, kind, shapes, R, t, args.pynifly)
                bad += [f"{stem} (PyNifly): {p}" for p in problems]
                print(f"  read back through PyNifly: {'as written' if not problems else '; '.join(problems)}")
                out_data[stem] = out
        if do_b:   # 2026-11-22a's
            data_a = {stem: out_data[stem] for stem, _, _ in NIFS}
            data_a["parts"] = data["parts"]
            print("2026-11-22a's shapes (shell_pieces.py), in the parked frame:")
            shapes_b = build_shapes_b(data_a, fr, args, print)
            report["shapes_b"] = {label: {k: x[k] for k in ("vertices", "triangles", "dropped", "inside")}
                                  | dict(numbers=x["numbers"], **{k: x[k] for k in ("badges", "pieces") if k in x})
                                  for label, x in shapes_b.items()}
            for stem, nm, kind in NIFS:
                R, t = fr[stem][:2]
                src = data_a[stem]
                out, lines, parent, grown = patch_nif_b(src, stem, nm, kind, shapes_b, R, t, wanted, args.overlay_blend)
                problems, worst = verify_b(src, out, stem, nm, kind, shapes_b, R, t, wanted, grown, args.overlay_blend)
                print(f"{stem}.nif (2026-11-22a's):")
                for line in lines:
                    print(f"  {line}")
                print(f"  under block {parent}; the new positions at most {worst:.5f} off the fitted ones")
                bad += [f"{stem}: {p}" for p in problems]
                path = Path(tmp) / f"{stem}_b.nif"
                path.write_bytes(out)
                before = Path(tmp) / f"{stem}_b_src.nif"
                before.write_bytes(src)
                problems = pynifly_check_b(path, before, nm, kind, shapes_b, wanted, args.pynifly)
                bad += [f"{stem} (PyNifly): {p}" for p in problems]
                print(f"  read back through PyNifly: {'as written' if not problems else '; '.join(problems)}")
                out_data[stem] = out
    if todo or do_b:
        for stem, nm, kind in NIFS:
            out = out_data[stem]
            path = args.out / f"{stem}.nif"
            BC.write_file(path, out)
            print(f"wrote {path}: {len(out)} bytes (was {len(data[stem])}), {len(BC.Nif(out).shapes())} shapes, "
                  f"sha256 {BC.sha256(out)}")
            report["nifs"][stem] = dict(sha256=BC.sha256(out), bytes=len(out), was=BC.sha256(data[stem]), patched=True,
                                        shapes=len(BC.Nif(out).shapes()))
    if args.bgsm_out:
        report["materials"] = write_materials(args.data, args.bgsm_out, print, wanted, bool(args.overlay_blend))
    if args.report:
        args.report.write_text(json.dumps(report, indent=1, default=float) + "\n")
    for line in bad:
        print(f"FAIL {line}", file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
