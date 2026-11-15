#!/usr/bin/env python3
"""Self-test of the Linux PyNifly install (Commonwealth Motorbike asset tools).

Writes a nif of the game's (FO4) with one triangle shape through PyNifly's Python API, imported the way the repository's
tools do (tools/rider/harley_meshes.py: sys.path.insert(0, <io_scene_nifly>); from pyn.pynifly import NifFile,
TransformBuf), reads it back and compares. With --skin it also writes a second nif whose shape is skinned to one
bone (as build_bike_meshes.py's write_worn does) and reads the weights back.

    <python with numpy> -I nifly_selftest.py --pynifly /opt/cmb/pynifly/io_scene_nifly --out <folder>

Exit 0 and a last line "ok" when everything matched.
"""
import argparse
import struct
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pynifly", type=Path, required=True, help="PyNifly's io_scene_nifly folder")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(args.pynifly))
    from pyn.pynifly import NifFile, TransformBuf  # noqa: E402
    from pyn.nifdefs import PynBufferTypes  # noqa: E402
    from pyn import niflydll  # noqa: E402
    from pyn.niflydll import nifly  # noqa: E402
    print("library:", niflydll.nifly_path, "version", tuple(nifly.getVersion()[i] for i in range(3)))

    verts = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (0.0, 10.0, 2.5)]
    tris = [(0, 1, 2)]
    uvs = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    normals = [(0.0, -0.2425356, 0.9701425)] * 3
    bad = 0

    def near(a, b, tol):
        return all(abs(x - y) <= tol for p, q in zip(a, b) for x, y in zip(p, q))

    def check(what, ok):
        nonlocal bad
        print(("  ok   " if ok else "  FAIL ") + what)
        bad += 0 if ok else 1

    # 1. a static triangle
    path = args.out / "selftest_tri.nif"
    out = NifFile()
    out.initialize("FO4", str(path), "NiNode", "selftest")
    # the tools pass the vanilla motorcycle's shape type (a BSTriShape) as use_type; PyNifly's own choice for
    # the game is a BSSubIndexTriShape (the skinned test below)
    shape = out.createShapeFromData("CMB_Selftest", verts, tris, uvs, normals,
                                    use_type=PynBufferTypes.BSTriShapeBufType)
    shape.shader.name = "Materials\\CMB\\Bike\\selftest.BGSM"
    shape.save_shader_attributes()
    out.save()
    raw = path.read_bytes()
    check(f"{path.name}: {len(raw)} bytes, a Gamebryo header", raw.startswith(b"Gamebryo File Format, Version 20.2.0.7"))
    back = NifFile(str(path))
    check(f"game {back.game}", back.game == "FO4")
    check(f"root {back.rootName!r}", back.rootName == "selftest")
    check(f"shapes {[s.name for s in back.shapes]}", [s.name for s in back.shapes] == ["CMB_Selftest"])
    s = back.shapes[0]
    check(f"block {s.blockname}", s.blockname == "BSTriShape")
    check(f"verts {[tuple(round(c, 4) for c in v) for v in s.verts]}", len(s.verts) == 3 and near(s.verts, verts, 1e-6))
    check(f"tris {[tuple(t) for t in s.tris]}", [tuple(t) for t in s.tris] == tris)
    check(f"uvs {[tuple(round(c, 4) for c in u) for u in s.uvs]}", near(s.uvs, uvs, 1e-3))
    check(f"normals {[tuple(round(c, 3) for c in n) for n in s.normals]}", near(s.normals, normals, 0.02))
    check(f"material {s.shader.name!r}", s.shader.name == "Materials\\CMB\\Bike\\selftest.BGSM")

    # 2. the same, skinned to one bone (the worn bike's way)
    path2 = args.out / "selftest_skin.nif"
    out = NifFile()
    out.initialize("FO4", str(path2), "NiNode", "selftest_skin")
    shape = out.createShapeFromData("CMB_SelftestWorn", verts, tris, uvs, normals)
    identity = TransformBuf()
    identity.set_identity()
    shape.skin()
    shape.set_global_to_skin(identity)
    shape.add_bone("AnimObjectA", identity)
    shape.set_skin_to_bone_xform("AnimObjectA", identity)
    shape.setShapeWeights("AnimObjectA", [(i, 1.0) for i in range(len(verts))])
    out.save()
    s = NifFile(str(path2)).shapes[0]
    weights = {b: sorted(w) for b, w in s.bone_weights.items()}
    check(f"{path2.name}: bones {weights}", list(weights) == ["AnimObjectA"]
          and [i for i, _ in weights["AnimObjectA"]] == [0, 1, 2]
          and all(abs(w - 1.0) < 1e-3 for _, w in weights["AnimObjectA"]))
    check(f"block {s.blockname}", s.blockname == "BSSubIndexTriShape")
    check(f"verts kept ({len(s.verts)})", len(s.verts) == 3 and near(s.verts, verts, 1e-2))

    print("ok" if not bad else f"{bad} check(s) failed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
