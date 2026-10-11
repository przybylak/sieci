#!/usr/bin/env python3
"""Builds the bike meshes from the game's own motorcycle model.

  CMB_BikeParked.nif      unmodified copy of the vanilla motorcycle (keeps its collision)
  CMB_BikeWorn.nif        the same geometry as a wearable armor mesh:
                          - turned 180 degrees so it faces +Y like a character,
                          - moved so the rider's seat sits over the character's origin,
                          - every vertex weighted 100% to the AnimObjectA bone.
  CMB_BikeWornRider.nif   the same, hanging off the rider's COM bone instead (with
  CMB_BikeWornRiderF.nif  --seat; F for the female rider, who sits a little higher).

Why AnimObjectA: it sits at the ground origin, walking/running clips never move
it, and it can only rotate (Fallout 4 locks bone translation for every bone but
Root and COM). So without the rider pose the bike stays planted, and the riding
animations can lean it around the ground line in turns.

Why COM as well: the game twists the body away from the root while turning on the
spot or talking (BSRootTwistModifier), so a bike on AnimObjectA stays put while the
rider turns on it. On COM the bike turns with the rider. Its bind pose is COM's
seated transform, which riding_anims.py writes next to the clips (CMB_RiderSeat.json),
so in the riding clips it sits exactly where the AnimObjectA bike does.

Needs PyNifly (https://github.com/BadDogSkyrim/PyNifly): pass its io_scene_nifly
folder. Run on your own copy of the game files; the output is derived from
Bethesda's model, so it isn't committed to the repository.

  python build_bike_meshes.py --pynifly <io_scene_nifly> \
      --model <...>/meshes/setdressing/vehicles/motorcycle/motorcycle_clean.nif \
      --out <Data>/Meshes/CMB [--seat <Data>/Meshes/Actors/Character/Animations/MT/CMB_Rider]
"""

import argparse
import json
import math
import shutil
import struct
import sys
from pathlib import Path

# Rider seat centre on the vanilla model is at y = +17 (the model faces -Y).
# After turning it around, shifting by this puts the seat over the origin.
SEAT_SHIFT = 17.0
BIKE_BONE = "AnimObjectA"
SEAT_FILE = "CMB_RiderSeat.json"


def turn_and_shift(v):
    x, y, z = v
    return (-x, -y + SEAT_SHIFT, z)


def turn(n):
    x, y, z = n
    return (-x, -y, z)


def _block_offsets(data: bytes):
    """Start offset and type name of every block in a Fallout 4 (20.2.0.7, bsver 130) nif."""
    i = data.index(b"\n") + 1 + 9  # header line, version, endian, user version
    nblocks = struct.unpack_from("<I", data, i)[0]
    i += 8  # block count, bs version
    for _ in range(4):  # author, process script, export script, max filepath
        i += 1 + data[i]
    ntypes = struct.unpack_from("<H", data, i)[0]
    i += 2
    types = []
    for _ in range(ntypes):
        n = struct.unpack_from("<I", data, i)[0]
        types.append(data[i + 4:i + 4 + n].decode())
        i += 4 + n
    type_idx = struct.unpack_from(f"<{nblocks}H", data, i)
    i += 2 * nblocks
    sizes = struct.unpack_from(f"<{nblocks}I", data, i)
    i += 4 * nblocks
    nstrings = struct.unpack_from("<I", data, i)[0]
    i += 8
    for _ in range(nstrings):
        i += 4 + struct.unpack_from("<I", data, i)[0]
    i += 4 + 4 * struct.unpack_from("<I", data, i)[0]  # groups
    blocks = []
    for t, size in zip(type_idx, sizes):
        blocks.append((i, types[t & 0x7FFF]))
        i += size
    return blocks


def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def rigid_inverse(m):
    """Inverse of a 4x4 rotation + translation (rows of the rotation, translation in column 3)."""
    r = [[m[j][i] for j in range(3)] for i in range(3)]
    t = [-sum(r[i][k] * m[k][3] for k in range(3)) for i in range(3)]
    return [r[0] + [t[0]], r[1] + [t[1]], r[2] + [t[2]], [0.0, 0.0, 0.0, 1.0]]


def apply(m, v):
    return tuple(sum(m[i][k] * v[k] for k in range(3)) + m[i][3] for i in range(3))


def fix_bone_bounds(path: Path, verts, skin_to_bone=None) -> tuple:
    """Write a bounding sphere that encloses every vertex into BSSkin::BoneData.

    The game culls skinned meshes with this sphere; nifly's own estimate is too
    small for a mesh this long, which would make the bike pop out at screen edges.
    The sphere is in bone space: the verts (model space) go through the bike's only
    bone's skin-to-bone transform (identity for AnimObjectA).
    """
    lo = [min(v[i] for v in verts) for i in range(3)]
    hi = [max(v[i] for v in verts) for i in range(3)]
    centre = [(a + b) / 2 for a, b in zip(lo, hi)]
    radius = max(math.dist(centre, v) for v in verts) + 1.0
    if skin_to_bone:
        centre = list(apply(skin_to_bone, centre))
    data = bytearray(path.read_bytes())
    offset = next(off for off, name in _block_offsets(data) if name == "BSSkin::BoneData")
    if struct.unpack_from("<I", data, offset)[0] != 1:
        raise ValueError("expected exactly one bone in BSSkin::BoneData")
    struct.pack_into("<4f", data, offset + 4, *centre, radius)
    path.write_bytes(bytes(data))
    return centre, radius


def write_worn(NifFile, TransformBuf, shape, path: Path, bone: str, bind=None):
    """The bike as armor, weighted 100% to `bone`. `bind` is the bone's model-space
    transform the mesh is authored at (4x4 rows; identity when None)."""
    out = NifFile()
    out.initialize("FO4", str(path), "NiNode", path.stem)

    props = shape.properties.copy()
    props.nameID = props.conrollerID = props.collisionID = -1
    props.skinInstanceID = props.shaderPropertyID = props.alphaPropertyID = -1
    verts = [turn_and_shift(v) for v in shape.verts]
    new = out.createShapeFromData(
        path.stem,
        verts,
        shape.tris,
        shape.uvs,
        [turn(n) for n in shape.normals],
        props=props,
        use_type=shape.properties.bufType,
    )
    if shape.colors:
        new.set_colors(shape.colors)

    def buf(m):
        b = TransformBuf()
        b.store([m[0][3], m[1][3], m[2][3]], [m[0][:3], m[1][:3], m[2][:3]], [1.0, 1.0, 1.0])
        return b

    identity = TransformBuf()
    identity.set_identity()
    skin_to_bone = rigid_inverse(bind) if bind else None
    new.set_global_to_skin(identity)
    new.add_bone(bone, buf(bind) if bind else identity)
    new.set_skin_to_bone_xform(bone, buf(skin_to_bone) if bind else identity)
    new.setShapeWeights(bone, [(i, 1.0) for i in range(len(verts))])

    # Same shader block and material (.bgsm) as the vanilla model.
    new.shader.name = shape.shader.name
    new.shader._properties = shape.shader.properties.copy()
    new.save_shader_attributes()
    out.save()
    centre, radius = fix_bone_bounds(path, verts, skin_to_bone)

    check = NifFile(str(path)).shapes[0]
    vs = check.verts
    lo = [min(v[i] for v in vs) for i in range(3)]
    hi = [max(v[i] for v in vs) for i in range(3)]
    print(f"wrote {path}: {len(vs)} verts, bones {list(check.bone_weights)}, material {check.shader.name}")
    print(f"  bounds x[{lo[0]:.1f},{hi[0]:.1f}] y[{lo[1]:.1f},{hi[1]:.1f}] z[{lo[2]:.1f},{hi[2]:.1f}]")
    print(f"  culling sphere centre ({centre[0]:.1f},{centre[1]:.1f},{centre[2]:.1f}) radius {radius:.1f} (bone space)")
    if bind:
        # Read the skin back and pose it at the bind transform: it must land where it's
        # stored (verts are half floats, so compare with the stored ones).
        r = check.get_shape_skin_to_bone(bone)
        s2b = [list(r.rotation[i]) + [r.translation[i]] for i in range(3)] + [[0.0, 0.0, 0.0, 1.0]]
        m = mat_mul(bind, s2b)
        err = max(math.dist(apply(m, v), v) for v in vs)
        print(f"  seated on {bone} at z {bind[2][3]:.1f}: posed mesh within {err:.4f} of the model")
        if err > 0.01:
            raise ValueError(f"{path}: skin-to-bone round trip off by {err}")


def read_seat(folder: Path):
    p = folder / SEAT_FILE
    if not p.exists():
        return None
    data = json.loads(p.read_text())
    return data["bone"], data["transform"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pynifly", type=Path, required=True, help="PyNifly's io_scene_nifly folder")
    ap.add_argument("--model", type=Path, required=True, help="vanilla motorcycle_clean.nif or motorcycle_dirty.nif")
    ap.add_argument("--out", type=Path, required=True, help="output folder, normally <Data>/Meshes/CMB")
    ap.add_argument("--seat", type=Path,
                    help="the riding clips folder (MT\\CMB_Rider, with " + SEAT_FILE + " from riding_anims.py): "
                         "also writes the bike that hangs off the rider's COM")
    args = ap.parse_args()

    sys.path.insert(0, str(args.pynifly))
    from pyn.pynifly import NifFile, TransformBuf  # noqa: E402  (needs the path above)

    args.out.mkdir(parents=True, exist_ok=True)
    parked = args.out / "CMB_BikeParked.nif"
    shutil.copyfile(args.model, parked)
    print(f"wrote {parked}")

    src = NifFile(str(args.model))
    if len(src.shapes) != 1:
        print(f"expected one shape in {args.model}, found {len(src.shapes)}", file=sys.stderr)
        return 1
    shape = src.shapes[0]
    write_worn(NifFile, TransformBuf, shape, args.out / "CMB_BikeWorn.nif", BIKE_BONE)

    if args.seat:
        male = read_seat(args.seat)
        if male is None:
            print(f"no {SEAT_FILE} in {args.seat}: run riding_anims.py first", file=sys.stderr)
            return 1
        female = read_seat(args.seat / "Female")
        if female is None:
            print(f"no Female\\{SEAT_FILE}: the female rider uses the male seat height", file=sys.stderr)
            female = male
        for (bone, bind), name in ((male, "CMB_BikeWornRider.nif"), (female, "CMB_BikeWornRiderF.nif")):
            write_worn(NifFile, TransformBuf, shape, args.out / name, bone, bind)
    return 0


if __name__ == "__main__":
    sys.exit(main())
