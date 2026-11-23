#!/usr/bin/env python3
"""The parked bike's side stand down (build 2026-11-22a, test 58's wish: "it would be cool if bike was leaning a bit on
sidestand/kickstand"): the model's own stand leg turned down to the ground about its pivot bolt, in the parked nif only.

The model has a side stand (its glTF mesh 46: a leg, the pivot bolt, the spring and two brackets), folded back along
the frame under the left footpeg, low and out of sight. The build puts it in static_black of every nif, folded. The
parked bike (CMB_BikeParked.nif) gets the leg turned down about the bolt's own axis by STAND_TURN, so with the bike
leaning to its left (+x, the stand's side) by the stand's lean its foot meets the ground; the ridden and first-person
nifs keep it folded, as the model has it (nothing changes in them). CMB_Slope.dll's [Room] ParkStand is the foot this
prints (its default is the 2026-11-22a nif's), and the plugin's ParkFit leans the parked bike till that foot is on the
ground under it.

How: the parked nif's static_black is read with bar_cables.py's byte-level reader (imported, not edited), its
triangles split into connected pieces by welded positions, and the stand's pieces found in the folded stand's box
(STAND_BOX): the leg (the one piece running LEG_MIN_RUN or more along y) and the pivot bolt (the small one, its long
principal axis the pivot's). The leg's vertex records get their positions turned about the bolt's centre and their
normals, tangents and bitangents turned with them (the records' own byte encodings); every other record and every
other block byte for byte, static_black's triangles and culling sphere too (the sphere holds the leg down; grown if it
ever doesn't). A nif whose leg is down already (none in the folded box, one in the deployed one) is left as it is.

  python look_stand.py --data <Data> [--data <overlay Data> ...] --out <Data>/Meshes/CMB [--stand 1|0]
      [--turn -90] [--pynifly <io_scene_nifly>] [--report <json>]

--data: a built Data tree (Meshes/CMB/CMB_BikeParked.nif); given more than once, a later tree's file wins (the
package tree, then overlays such as the shells unit's). Only CMB_BikeParked.nif is read and written. --stand 0 writes
it as it is (2026-11-21a's, or the overlay's, byte for byte). Checks run on the output (every block but static_black's
byte for byte; in it every record but the leg's; the leg's positions the turned ones; its normals within the byte
encoding's step; the foot on the leaned ground), and with --pynifly the nif is read back through PyNifly. Exit status 1
when a check fails. --report writes the numbers (the pivot, the axis, the turn, the foot, the lean, sha256) as JSON.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bar_cables as BC  # noqa: E402

STEM, SHAPE = "CMB_BikeParked", "CMB_Bike_static_black"
STAND_BOX = ((4.0, 1.0, 12.5), (12.5, 21.0, 18.0))     # the folded stand's pieces (the parked frame: +x the bike's left,
                                                       # -y its front, z up, the ground at 0)
DOWN_BOX = ((4.0, -6.0, 0.0), (20.0, 12.0, 18.0))       # where the leg is once down
LEG_MIN_RUN = 12.0      # the leg: the stand's piece running this far along y folded (16.6; the spring 7.1, the bolt 1.2)
BOLT_MAX_RUN = 2.0      # the pivot bolt: the stand's small piece (y 1.2, x 2.6, z 1.7)
BOLT_MAX_VERTS = 200
STAND_TURN = -90.0      # degrees about the bolt's long axis (pointing out, +x): folded back -> down, out and a little ahead
WELD = 4                # decimals the positions are welded at for the pieces
NORMAL_STEP = 2.0 / 255.0


def pieces(v, t):
    """The triangles' connected pieces by welded positions: [(vertex indices, triangle rows)]."""
    _, inv = np.unique(np.round(v, WELD), axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    parent = np.arange(inv.max() + 1)

    def find(a):
        r = a
        while parent[r] != r:
            r = parent[r]
        while parent[a] != r:
            parent[a], a = r, parent[a]
        return r

    for a, b, c in inv[t]:
        ra = find(a)
        for x in (b, c):
            rx = find(x)
            if rx != ra:
                parent[rx] = ra
    root = np.array([find(i) for i in range(len(parent))])
    troot = root[inv[t[:, 0]]]
    out = []
    for r in np.unique(troot):
        rows = np.flatnonzero(troot == r)
        out.append((np.unique(t[rows]), rows))
    return out


def inside(p, box):
    lo, hi = np.array(box[0]), np.array(box[1])
    return bool((p.min(axis=0) >= lo).all() and (p.max(axis=0) <= hi).all())


def find_stand(v, t):
    """(the leg's vertex indices, the bolt's centre, its axis pointing out, 'folded' | 'down') or a reason (str)."""
    folded = [(vi, rows) for vi, rows in pieces(v, t) if inside(v[vi], STAND_BOX)]
    legs = [vi for vi, _ in folded if np.ptp(v[vi][:, 1]) >= LEG_MIN_RUN]
    bolts = [vi for vi, _ in folded if np.ptp(v[vi][:, 1]) <= BOLT_MAX_RUN and len(vi) <= BOLT_MAX_VERTS]
    state = "folded"
    if not legs:
        down = [vi for vi, _ in pieces(v, t) if inside(v[vi], DOWN_BOX) and not inside(v[vi], STAND_BOX)
                and np.ptp(v[vi][:, 2]) >= 8.0]
        if len(down) == 1 and len(bolts) == 1:
            legs, state = down, "down"
        else:
            return f"no folded leg in the stand's box ({len(folded)} pieces there) and no single leg down ({len(down)})"
    if len(legs) != 1 or len(bolts) != 1:
        return f"{len(legs)} leg(s) and {len(bolts)} bolt(s) in the stand's box, one each expected"
    b = v[bolts[0]]
    centre = (b.min(axis=0) + b.max(axis=0)) / 2
    c = b - b.mean(axis=0)
    w, vec = np.linalg.eigh(c.T @ c)
    axis = vec[:, np.argmax(w)]
    if axis[0] < 0:
        axis = -axis
    return legs[0], centre, axis, state


def rotation(axis, deg):
    a = np.radians(deg)
    x, y, z = axis / np.linalg.norm(axis)
    K = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return np.eye(3) + np.sin(a) * K + (1.0 - np.cos(a)) * (K @ K)


def foot_of(p):
    """The leg's vertex that meets the ground first as the bike leans to its left (+x down): the least atan2(z, x) over
    the vertices out on the left; (its index, the lean in degrees)."""
    ang = np.where(p[:, 0] > 0.0, np.degrees(np.arctan2(p[:, 2], p[:, 0])), 1e9)
    i = int(np.argmin(ang))
    return i, float(ang[i])


def decode_bytes(b):
    return np.asarray(b, np.float64) / 255.0 * 2.0 - 1.0


def encode_bytes(x):
    return np.clip(np.round((np.asarray(x, np.float64) + 1.0) / 2.0 * 255.0), 0, 255).astype(np.uint8)


def turned_records(s, idx, R, centre):
    """static_black's records with the leg's (idx) positions turned about centre by R and their normals, tangents and
    bitangents with them; every other byte as it was."""
    if not s.full:
        raise ValueError("static_black isn't full precision (the parked nif's should be)")
    r = np.array(s.records, copy=True)
    pos = s.positions()
    nat = ((s.desc >> 16) & 0xF) * 4
    tat = ((s.desc >> 20) & 0xF) * 4
    flags = s.desc >> 44
    if not (flags & 0x8) or not (flags & 0x10):
        raise ValueError(f"static_black's records have no normals or tangents (flags {flags:#x})")
    new = (pos[idx] - centre) @ R.T + centre
    r[idx, :12] = np.ascontiguousarray(new.astype("<f4")).view(np.uint8).reshape(len(idx), 12)
    n = decode_bytes(r[idx, nat:nat + 3])
    tg = decode_bytes(r[idx, tat:tat + 3])
    bx = np.ascontiguousarray(r[idx, 12:16]).view("<f4").reshape(-1).astype(np.float64)
    bt = np.column_stack([bx, decode_bytes(r[idx, nat + 3]), decode_bytes(r[idx, tat + 3])])
    n2, t2, b2 = n @ R.T, tg @ R.T, bt @ R.T
    r[idx, nat:nat + 3] = encode_bytes(n2)
    r[idx, tat:tat + 3] = encode_bytes(t2)
    r[idx, 12:16] = np.ascontiguousarray(b2[:, 0].astype("<f4")).view(np.uint8).reshape(len(idx), 4)
    r[idx, nat + 3] = encode_bytes(b2[:, 1])
    r[idx, tat + 3] = encode_bytes(b2[:, 2])
    return r, new, (n2, t2, b2)


def bound_holding(bound, pts):
    c, rad = np.array(bound[:3], np.float64), float(bound[3])
    far = float(np.linalg.norm(pts - c, axis=1).max())
    return bound if far <= rad else (*bound[:3], far + 0.01)


def stand_down(src: bytes, turn: float):
    """(the patched nif's bytes, the numbers) or (None, a reason / the numbers of a nif already down)."""
    nif = BC.Nif(src)
    k = nif.shape_named(SHAPE)
    if k is None:
        return None, f"no {SHAPE} in the nif"
    s = BC.TriShape(nif.blocks[k])
    v = s.positions()
    found = find_stand(v, s.tris)
    if isinstance(found, str):
        return None, found
    idx, centre, axis, state = found
    if state == "down":
        i, lean = foot_of(v[idx])
        return None, dict(state="down", foot=v[idx][i].tolist(), lean=lean, leg_vertices=int(len(idx)))
    R = rotation(axis, turn)
    records, new, vecs = turned_records(s, idx, R, centre)
    bound = bound_holding(s.bound, new)
    nif.blocks[k] = s.pack(records=records, bound=bound)
    i, lean = foot_of(new)
    numbers = dict(state="folded", pivot=centre.tolist(), axis=axis.tolist(), turn=turn, leg_vertices=int(len(idx)),
                   leg_triangles=int(np.isin(s.tris, idx).all(axis=1).sum()), foot=new[i].tolist(), lean=lean,
                   lowest=float(new[:, 2].min()), reach_x=float(new[:, 0].max()), bound=list(s.bound),
                   bound_after=list(bound), folded_tip=v[idx][np.argmax(np.linalg.norm(v[idx] - centre, axis=1))].tolist())
    return nif.write(), dict(numbers, idx=idx, R=R, centre=centre, new=new, vecs=vecs)


def verify(before: bytes, after: bytes, x):
    """Every block but static_black's byte for byte; in it every record but the leg's, the triangles, the leg's
    positions the turned ones (float32), its vectors within the byte step; the foot on the leaned ground."""
    bad = []
    a, b = BC.Nif(before), BC.Nif(after)
    if len(a.blocks) != len(b.blocks) or a.strings != b.strings or a.types != b.types:
        return ["the block list, the strings or the types changed"]
    k = a.shape_named(SHAPE)
    for j in range(len(a.blocks)):
        if j != k and a.blocks[j] != b.blocks[j]:
            bad.append(f"block {j} ({a.type_of(j)}) changed")
    sa, sb = BC.TriShape(a.blocks[k]), BC.TriShape(b.blocks[k])
    if not np.array_equal(sa.tris, sb.tris):
        bad.append("static_black's triangles changed")
    if sa.desc != sb.desc or sa.head != sb.head or (sa.skin, sa.shader, sa.alpha) != (sb.skin, sb.shader, sb.alpha):
        bad.append("static_black's head, refs or vertex description changed")
    idx = x["idx"]
    others = np.setdiff1d(np.arange(len(sa.records)), idx)
    if not np.array_equal(sa.records[others], sb.records[others]):
        bad.append("a record that isn't the leg's changed")
    pos = sb.positions()[idx]
    want = x["new"].astype(np.float32).astype(np.float64)
    if np.abs(pos - want).max() > 1e-6:
        bad.append(f"the leg's positions {np.abs(pos - want).max():.2e} off the turned ones")
    back = (pos - x["centre"]) @ x["R"] + x["centre"]
    if np.abs(back - sa.positions()[idx]).max() > 1e-4:
        bad.append("the leg turned back isn't the folded one")
    nat = ((sb.desc >> 16) & 0xF) * 4
    n = decode_bytes(sb.records[idx, nat:nat + 3])
    if np.abs(n - x["vecs"][0]).max() > NORMAL_STEP:
        bad.append("the leg's normals off their turned values by more than the byte step")
    if np.abs(np.linalg.norm(n, axis=1) - 1.0).max() > 0.03:
        bad.append("the leg's normals not unit length")
    lean = np.radians(x["lean"])
    zl = pos[:, 2] * np.cos(lean) - pos[:, 0] * np.sin(lean)   # leaned left by the lean (+x down)
    if abs(zl.min()) > 1e-3:
        bad.append(f"the leg's lowest point {zl.min():.4f} off the ground leaned {x['lean']:.2f} deg")
    c, rad = np.array(sb.bound[:3]), sb.bound[3]
    if np.linalg.norm(pos - c, axis=1).max() > rad + 1e-4:
        bad.append("static_black's sphere doesn't hold the leg")
    return bad


def pynifly_check(path: Path, before: bytes, x, pynifly: Path):
    """PyNifly reads the patched nif: static_black's vertices the written ones, every other shape's as before."""
    sys.path.insert(0, str(pynifly))
    import logging
    import tempfile
    logging.disable(logging.WARNING)
    from pyn.pynifly import NifFile
    bad = []
    with tempfile.TemporaryDirectory() as tmp:
        old = Path(tmp) / "before.nif"
        old.write_bytes(before)
        fa, fb = NifFile(str(old)), NifFile(str(path))
        sa = {s.name: s for s in fa.shapes}
        sb = {s.name: s for s in fb.shapes}
        if list(sa) != list(sb):
            return ["the shapes' names or order changed"]
        for name in sa:
            va, vb = np.asarray(sa[name].verts), np.asarray(sb[name].verts)
            if name != SHAPE:
                if va.shape != vb.shape or (len(va) and np.abs(va - vb).max() > 0):
                    bad.append(f"{name}'s vertices changed")
                continue
            if np.abs(vb[x["idx"]] - x["new"]).max() > 1e-4:
                bad.append("static_black's leg isn't where it was written")
            others = np.setdiff1d(np.arange(len(va)), x["idx"])
            if np.abs(vb[others] - va[others]).max() > 0:
                bad.append("static_black's other vertices moved")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, action="append", required=True,
                    help="a built Data tree (its Meshes/CMB/CMB_BikeParked.nif); more than one: a later tree's file wins")
    ap.add_argument("--out", type=Path, required=True, help="where the patched CMB_BikeParked.nif goes (a folder)")
    ap.add_argument("--stand", type=int, choices=(0, 1), default=1,
                    help="1 (2026-11-22a): the stand leg down in the parked nif; 0: the nif as it is (byte for byte)")
    ap.add_argument("--turn", type=float, default=STAND_TURN,
                    help=f"degrees about the bolt's axis, folded to down (default {STAND_TURN:g})")
    ap.add_argument("--pynifly", type=Path, help="PyNifly's io_scene_nifly (the read-back check)")
    ap.add_argument("--report", type=Path, help="write the numbers as JSON")
    args = ap.parse_args()
    src_path = None
    for d in args.data:
        p = d / "Meshes" / "CMB" / f"{STEM}.nif"
        if p.exists():
            src_path = p
    if src_path is None:
        print(f"{STEM}.nif in none of {[str(d) for d in args.data]}", file=sys.stderr)
        return 1
    src = src_path.read_bytes()
    args.out.mkdir(parents=True, exist_ok=True)
    out_path = args.out / f"{STEM}.nif"
    report = dict(stand=args.stand, source=str(src_path), was=BC.sha256(src))
    bad = []
    if not args.stand:
        if out_path.resolve() != src_path.resolve():
            BC.write_file(out_path, src)
        print(f"{STEM}.nif as it was (--stand 0): sha256 {BC.sha256(src)}")
        report.update(sha256=BC.sha256(src), patched=False)
    else:
        out, x = stand_down(src, args.turn)
        if out is None and isinstance(x, dict):
            if out_path.resolve() != src_path.resolve():
                BC.write_file(out_path, src)
            print(f"{STEM}.nif: the stand is down already (the foot ({x['foot'][0]:.2f}, {x['foot'][1]:.2f}, {x['foot'][2]:.2f}), "
                  f"the lean {x['lean']:.2f} deg): left as it is")
            report.update(sha256=BC.sha256(src), patched=False, note="the stand is down already", foot=x["foot"], lean=x["lean"])
        elif out is None:
            bad.append(f"{STEM}: {x}")
        else:
            bad += [f"{STEM}: {p}" for p in verify(src, out, x)]
            BC.write_file(out_path, out)
            f = x["foot"]
            print(f"{STEM}.nif: static_black's stand: the leg ({x['leg_vertices']} vertices, {x['leg_triangles']} triangles) "
                  f"turned {x['turn']:g} deg about the pivot bolt's axis ({x['axis'][0]:.3f}, {x['axis'][1]:.3f}, {x['axis'][2]:.3f}) "
                  f"through ({x['pivot'][0]:.3f}, {x['pivot'][1]:.3f}, {x['pivot'][2]:.3f}); its tip was at "
                  f"({x['folded_tip'][0]:.2f}, {x['folded_tip'][1]:.2f}, {x['folded_tip'][2]:.2f})")
            print(f"  the foot ({f[0]:.2f}, {f[1]:.2f}, {f[2]:.2f}) in the parked frame (+x the bike's left, -y its front): "
                  f"on the ground with the bike leaning {x['lean']:.2f} deg to its left ([Room] ParkStand={f[0]:.2f},{f[1]:.2f},{f[2]:.2f}); "
                  f"the leg's lowest point upright z {x['lowest']:.2f}, out to x {x['reach_x']:.2f}")
            print(f"  static_black's sphere {'as it was' if x['bound'] == x['bound_after'] else 'grown to ' + str(x['bound_after'])}")
            print(f"  wrote {out_path}: {len(out)} bytes (was {len(src)}), sha256 {BC.sha256(out)}")
            if args.pynifly:
                problems = pynifly_check(out_path, src, x, args.pynifly)
                bad += [f"{STEM} (PyNifly): {p}" for p in problems]
                print(f"  read back through PyNifly: {'as written' if not problems else '; '.join(problems)}")
            report.update(sha256=BC.sha256(out), bytes=len(out), patched=True,
                          **{key: x[key] for key in ("pivot", "axis", "turn", "leg_vertices", "leg_triangles", "foot", "lean",
                                                     "lowest", "reach_x", "bound", "bound_after", "folded_tip")})
    if args.report:
        args.report.write_text(json.dumps(report, indent=1, default=float) + "\n")
    for line in bad:
        print(f"FAIL {line}", file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
