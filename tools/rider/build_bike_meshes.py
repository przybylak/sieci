#!/usr/bin/env python3
"""Builds the two bike meshes from the game's own motorcycle model.

  CMB_BikeParked.nif  unmodified copy of the vanilla motorcycle (keeps its collision)
  CMB_BikeWorn.nif    the same geometry as a wearable armor mesh:
                      - turned 180 degrees so it faces +Y like a character,
                      - moved so the rider's seat sits over the character's origin,
                      - every vertex weighted 100% to the AnimObjectA bone.

Why AnimObjectA: it sits at the ground origin, walking/running clips never move
it, and it can only rotate (Fallout 4 locks bone translation for every bone but
Root and COM). So without the rider pose the bike stays planted, and the riding
animations can lean it around the ground line in turns.

Needs PyNifly (https://github.com/BadDogSkyrim/PyNifly): pass its io_scene_nifly
folder. Run on your own copy of the game files; the output is derived from
Bethesda's model, so it isn't committed to the repository.

  python build_bike_meshes.py --pynifly <io_scene_nifly> \
      --model <...>/meshes/setdressing/vehicles/motorcycle/motorcycle_clean.nif \
      --out <Data>/Meshes/CMB
"""

import argparse
import math
import shutil
import struct
import sys
from pathlib import Path

# Rider seat centre on the vanilla model is at y = +17 (the model faces -Y).
# After turning it around, shifting by this puts the seat over the origin.
SEAT_SHIFT = 17.0
BIKE_BONE = "AnimObjectA"


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


def fix_bone_bounds(path: Path, verts) -> tuple:
    """Write a bounding sphere that encloses every vertex into BSSkin::BoneData.

    The game culls skinned meshes with this sphere; nifly's own estimate is too
    small for a mesh this long, which would make the bike pop out at screen edges.
    The bike's only bone has an identity skin transform, so model space = bone space.
    """
    lo = [min(v[i] for v in verts) for i in range(3)]
    hi = [max(v[i] for v in verts) for i in range(3)]
    centre = [(a + b) / 2 for a, b in zip(lo, hi)]
    radius = max(math.dist(centre, v) for v in verts) + 1.0
    data = bytearray(path.read_bytes())
    offset = next(off for off, name in _block_offsets(data) if name == "BSSkin::BoneData")
    if struct.unpack_from("<I", data, offset)[0] != 1:
        raise ValueError("expected exactly one bone in BSSkin::BoneData")
    struct.pack_into("<4f", data, offset + 4, *centre, radius)
    path.write_bytes(bytes(data))
    return centre, radius


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pynifly", type=Path, required=True, help="PyNifly's io_scene_nifly folder")
    ap.add_argument("--model", type=Path, required=True, help="vanilla motorcycle_clean.nif or motorcycle_dirty.nif")
    ap.add_argument("--out", type=Path, required=True, help="output folder, normally <Data>/Meshes/CMB")
    args = ap.parse_args()

    sys.path.insert(0, str(args.pynifly))
    from pyn.pynifly import NifFile, TransformBuf  # noqa: E402  (needs the path above)

    args.out.mkdir(parents=True, exist_ok=True)
    parked = args.out / "CMB_BikeParked.nif"
    worn = args.out / "CMB_BikeWorn.nif"

    shutil.copyfile(args.model, parked)

    src = NifFile(str(args.model))
    if len(src.shapes) != 1:
        print(f"expected one shape in {args.model}, found {len(src.shapes)}", file=sys.stderr)
        return 1
    shape = src.shapes[0]

    out = NifFile()
    out.initialize("FO4", str(worn), "NiNode", "CMB_BikeWorn")

    props = shape.properties.copy()
    props.nameID = props.conrollerID = props.collisionID = -1
    props.skinInstanceID = props.shaderPropertyID = props.alphaPropertyID = -1
    new = out.createShapeFromData(
        "CMB_BikeWorn",
        [turn_and_shift(v) for v in shape.verts],
        shape.tris,
        shape.uvs,
        [turn(n) for n in shape.normals],
        props=props,
        use_type=shape.properties.bufType,
    )
    if shape.colors:
        new.set_colors(shape.colors)

    identity = TransformBuf()
    identity.set_identity()
    new.set_global_to_skin(identity)
    new.add_bone(BIKE_BONE, identity)
    new.set_skin_to_bone_xform(BIKE_BONE, identity)
    new.setShapeWeights(BIKE_BONE, [(i, 1.0) for i in range(len(shape.verts))])

    # Same shader block and material (.bgsm) as the vanilla model.
    new.shader.name = shape.shader.name
    new.shader._properties = shape.shader.properties.copy()
    new.save_shader_attributes()
    out.save()
    centre, radius = fix_bone_bounds(worn, [turn_and_shift(v) for v in shape.verts])

    check = NifFile(str(worn)).shapes[0]
    vs = check.verts
    lo = [min(v[i] for v in vs) for i in range(3)]
    hi = [max(v[i] for v in vs) for i in range(3)]
    print(f"wrote {parked}")
    print(f"wrote {worn}: {len(vs)} verts, bones {list(check.bone_weights)}, material {check.shader.name}")
    print(f"  bounds x[{lo[0]:.1f},{hi[0]:.1f}] y[{lo[1]:.1f},{hi[1]:.1f}] z[{lo[2]:.1f},{hi[2]:.1f}]")
    print(f"  culling sphere centre ({centre[0]:.1f},{centre[1]:.1f},{centre[2]:.1f}) radius {radius:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
