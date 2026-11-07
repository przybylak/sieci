#!/usr/bin/env python3
"""The second customisation build's (2026-11-08a, C2) materials files of the new shapes' own (harley_meshes.py
--look-rims 1 --look-plate 1): each is the swap source a slot's options swap from, so with every slot on its stock option
the bike looks as 2026-11-07a's.

What it writes into --data (Materials\\CMB\\Bike):

  the plate          static_plate(.bgsm, _worn.bgsm): 2026-11-07a's static_black(.bgsm, _worn.bgsm) (from --base) with the
                     diffuse, normal and smoothspec renamed to static_plate_d/_n/_s.dds (art-plates' look_plates.py
                     re-samples them from static_black's texels through the plate's old UVs: the same look); every other
                     field static_black's
  the text overlay   static_plateText(.bgsm, _worn.bgsm): invisible (bike_materials.json's "static_plateText": alpha test
                     255 over off_d.dds's alpha 0, material alpha 0, no shadows) with decal on (the depth bias a text
                     material keeps), as static_badgeFender's
  the rim styles     wheelF_rim<Style>(.bgsm, _worn.bgsm) and wheelR_rim<Style>(...) for the seven styles (harley_meshes.
                     RIM_STYLE_LABELS): invisible, no decal, no shadows; a Rims option swaps a style's for a finish's
                     (art-wheels' rimF_<finish> / rimR_<finish>) and the cast rim's for off.bgsm

The invisible files are look_paint.off_material's (imported). off.bgsm and off_d/_n/_s.dds are 2026-11-07a's, already
in the tree.

--check (after a build, or alone on a built tree): the 32 files there; static_plate's the base's static_black's but the
three texture names; the invisible ones alpha test 255, alpha 0, no shadows, off's textures, no environment map, decal
on the text's and off the rims'.

    <python with numpy, Pillow, quicktex, texture2ddecoder> -I tools/rider/look_shapes.py --data <Data> \\
        --base <2026-11-07a's Data> [--materials ...] [--check]
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bgsm as B  # noqa: E402
from harley_meshes import RIM_STYLE_LABELS, PLATE_LABEL, PLATE_TEXT  # noqa: E402
from look_paint import off_material  # noqa: E402   (C1's; it imports the DDS writer: run with the DDS tools' Python)

PLATE_TEXTURES = {"diffuse": "CMB\\Bike\\static_plate_d.dds", "normal": "CMB\\Bike\\static_plate_n.dds",
                  "smoothspec": "CMB\\Bike\\static_plate_s.dds"}
WORN = ("", "_worn")


def invisible():
    """[(file stem, bike_materials.json material, decal)] of the invisible files."""
    out = [(PLATE_TEXT + w, PLATE_TEXT, True) for w in WORN]
    out += [(label + w, label, False) for label, _ in RIM_STYLE_LABELS for w in WORN]
    return out


def build(args, mats):
    mdir = args.data / "Materials" / "CMB" / "Bike"
    bm = args.base / "Materials" / "CMB" / "Bike"
    mdir.mkdir(parents=True, exist_ok=True)
    n = 0
    for w in WORN:
        m = B.read(bm / f"static_black{w}.bgsm")
        m["textures"].update(PLATE_TEXTURES)
        B.write(mdir / f"{PLATE_LABEL}{w}.bgsm", m)
        n += 1
    for stem, mat, decal in invisible():
        B.write(mdir / f"{stem}.bgsm", off_material(mats[mat], decal))
        n += 1
    print(f"wrote {n} materials files into {mdir}: {PLATE_LABEL}(.bgsm, _worn) as static_black's over its own textures, "
          f"{PLATE_TEXT}(...) and the 14 rim styles' invisible")
    return 0


def check(args, mats):
    ok = True

    def rep(good, what, detail=""):
        nonlocal ok
        ok &= bool(good)
        print(f"{'PASS' if good else 'FAIL'}  {what}{': ' + detail if detail else ''}")

    mdir = args.data / "Materials" / "CMB" / "Bike"
    bm = args.base / "Materials" / "CMB" / "Bike"
    bad = []
    for w in WORN:
        p = mdir / f"{PLATE_LABEL}{w}.bgsm"
        if not p.exists():
            bad.append(f"{p.name} missing")
            continue
        m, ref = B.read(p), B.read(bm / f"static_black{w}.bgsm")
        tex = dict(ref["textures"])
        tex.update(PLATE_TEXTURES)
        if m["textures"] != tex:
            bad.append(f"{p.name}: textures {m['textures']}")
        m2, r2 = dict(m), dict(ref)
        m2.pop("textures"), r2.pop("textures")
        diff = sorted(k for k in set(m2) | set(r2) if not k.startswith("_") and m2.get(k) != r2.get(k))   # (_raw_tex: the names)
        if diff:
            bad.append(f"{p.name}: {', '.join(diff)} not static_black's")
    rep(not bad, f"{PLATE_LABEL}(.bgsm, _worn): 2026-11-07a's static_black's but the textures, "
                 f"{', '.join(v.split(chr(92))[-1] for v in PLATE_TEXTURES.values())}", "; ".join(bad))
    bad = []
    for stem, mat, decal in invisible():
        p = mdir / f"{stem}.bgsm"
        if not p.exists():
            bad.append(f"{stem}.bgsm missing")
            continue
        m = B.read(p)
        if not (m["alpha_test"] and m["alpha_test_ref"] == 255 and m["alpha"] == 0.0 and not m["cast_shadows"]
                and m["textures"]["diffuse"] == "CMB\\Bike\\off_d.dds" and not m["environment_mapping"]
                and bool(m["decal"]) == decal):
            bad.append(f"{stem}: alpha test {m['alpha_test']} ref {m['alpha_test_ref']} alpha {m['alpha']} shadows "
                       f"{m['cast_shadows']} diffuse {m['textures']['diffuse']} decal {m['decal']}")
    rep(not bad, f"{len(invisible())} invisible materials files (alpha test 255, alpha 0, no shadow, off's textures; "
                 f"decal on {PLATE_TEXT}'s, off the rims')", "; ".join(bad))
    print("look_shapes --check: " + ("all passed" if ok else "FAILED"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, required=True, help="the Data tree to write (Materials)")
    ap.add_argument("--base", type=Path, required=True, help="2026-11-07a's Data tree (read only): static_black's files")
    ap.add_argument("--materials", type=Path, default=HERE / "bike_materials.json")
    ap.add_argument("--check", action="store_true", help="check a built tree (and nothing written)")
    args = ap.parse_args()
    mats = json.loads(args.materials.read_text())["materials"]
    if args.data.resolve() == args.base.resolve():
        ap.error("--data and --base must differ (the base is read only)")
    return check(args, mats) if args.check else build(args, mats)


if __name__ == "__main__":
    sys.exit(main())
