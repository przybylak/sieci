#!/usr/bin/env python3
"""The headlamp's lens in the Headlamp slot's colours (since the 2026-11-21a build, art build B): front_glow's materials
for the four options after "Warm (as it came)" (which stays front_glow.bgsm itself).

    <dds python> -I look_lamp.py --base <Data> --out <Data-like tree> [--lens-glass tinted|clear]
    <dds python> -I look_lamp.py --check --base <Data> --out <tree> [--lens-glass tinted|clear]
    python3 -I look_lamp.py --table              (the colours: each option's chromaticity, its 8-bit RGB, the lens's emit)

--base is a Data folder holding the shipped Materials\\CMB\\Bike\\front_glow.bgsm, front_glow_worn.bgsm and
Textures\\CMB\\Bike\\front_glow_d.dds (2026-11-10a's package). Writes, under --out:

  Materials\\CMB\\Bike\\front_glow_<key>_worn.bgsm   the riding bike's lit lens: front_glow_worn.bgsm with its emit colour
                                                   the option's (the multiplier 6.0 as it is); with --lens-glass tinted
                                                   also its diffuse the option's tinted lens texture (below)
  Materials\\CMB\\Bike\\front_glow_<key>.bgsm        the parked bike's lens: front_glow.bgsm (emit off, as the stock: the
                                                   parked lamp is never lit), with --lens-glass tinted its diffuse the
                                                   tinted lens texture (a coloured bulb shows its colour unlit, so the
                                                   field kit's preview, which turns the parked bike, shows the choice);
                                                   --lens-glass clear: front_glow.bgsm byte for byte
  Textures\\CMB\\Bike\\front_glow_<key>_d.dds         (--lens-glass tinted; not for a clear bulb, CLEAR_BULBS) the stock lens
                                                   texture (BC1 256, 9 mips) times the bulb's glass: 0.25 + 0.75 x the
                                                   option's colour

for the keys coolwhite, amber, selectiveyellow and bluewhite (SP/t63/contract.md's Headlamp slot) and, since the
2026-11-22a build, halogen, daylight, iceblue, red, green and purple (SP/t64/contract.md 4; white bulbs, CLEAR_BULBS:
coolwhite, halogen and daylight, have no tinted texture, their parked file front_glow.bgsm's bytes). The colours (LAMPS):
each a chromaticity from the lamp standards' own boxes or the CIE daylight locus, turned into 8-bit sRGB (the brightest
channel 255; a channel under 0 clipped). The same 8-bit RGB serves the beam's light record (the ESP's LIGH colour, as
the warm 255/241/224 does today) and, over 255, the lens's emit colour, so the beam matches the lens.

--check: every file there and read back byte for byte (bgsm.py); each material equal to its stock one but in the
fields named above; the emit colour the option's; the parked ones with emit off; the textures BC1 256 with 9 mips,
their mean colour the stock's times the glass; no other file under --out's Materials\\CMB\\Bike named front_glow_*
(but front_glow.bgsm and front_glow_worn.bgsm themselves).
"""
import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bgsm  # noqa: E402

MAT = ("Materials", "CMB", "Bike")
TEX = ("Textures", "CMB", "Bike")
# key: (name, chromaticity x, y, where it comes from). Warm (as it came) is the shipped lamp: LIGH 255/241/224, the lens
# 1.0/0.95/0.90 x 6 (about x 0.333, y 0.346: a 5,500 K blackbody's colour).
LAMPS = {
    "coolwhite": ("Cool white", 0.3127, 0.3290, "6500 K: CIE daylight at 6504 K (D65), the cool white of daylight lamps"),
    "amber": ("Amber", 0.578, 0.416, "signal amber: inside the turn signals' amber box (ECE R6/R48: y 0.398-0.429, "
                                     "z 0.007 or less), about 591 nm"),
    "selectiveyellow": ("Selective yellow", 0.502, 0.477, "the middle of the selective yellow headlamps' box (ECE R19: "
                                                          "between y = 0.138 + 0.580x, y = 1.29x - 0.100, y = 0.966 - x "
                                                          "and y = 0.992 - x)"),
    "bluewhite": ("Blue-white", 0.2938, 0.3092, "a little blue: CIE daylight at 8000 K"),
    # since 2026-11-22a (test 58: "colors themselves are fine, but larger selection is needed"; SP/t64/contract.md 4)
    "halogen": ("Halogen", 0.4225, 0.3998, "a halogen bulb: the Planckian locus at 3200 K"),
    "daylight": ("Daylight", 0.3457, 0.3585, "about 5000 K, neutral: CIE daylight at 5003 K (D50)"),
    "iceblue": ("Ice blue", 0.245, 0.290, "a pale icy blue: between daylight and about 480 nm"),
    "red": ("Red", 0.640, 0.330, "red as deep as the screen shows (the sRGB red; ECE's red box lies beyond it)"),
    "green": ("Green", 0.200, 0.600, "a signal green, about 524 nm with a little white"),
    "purple": ("Purple", 0.250, 0.120, "a black-light violet: violet with a little red"),
}
CLEAR_BULBS = ("coolwhite", "halogen", "daylight")     # white bulbs: the unlit lens is the stock one
EMIT_MULT = 6.0                    # front_glow_worn.bgsm's, kept
GLASS = (0.25, 0.75)               # the unlit lens: the stock texture x (0.25 + 0.75 x the option's colour)
SRGB = np.array([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]])


def rgb8(x, y):
    """A chromaticity's 8-bit sRGB (D65 white), the brightest channel 255, the out-of-gamut ones clipped at 0."""
    lin = SRGB @ np.array([x / y, 1.0, (1.0 - x - y) / y])
    lin = np.clip(lin, 0.0, None)
    lin = lin / lin.max()
    enc = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
    return tuple(int(v) for v in np.round(enc * 255))


def luminance_vs_warm(key):
    """The option's 8-bit colour's luminance against the shipped warm 255/241/224's (the beam's strength at one
    FadeValue: the LIGH colour times FadeValue is what the game lights with)."""
    def lin(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    def lum(rgb):
        return 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])
    return lum(rgb8(*LAMPS[key][1:3])) / lum((255, 241, 224))


def emit_of(key):
    return [round(c / 255.0, 4) for c in rgb8(*LAMPS[key][1:3])]


def glass_of(key):
    """The unlit bulb's filter over the stock lens texture, or None (a clear bulb)."""
    if key in CLEAR_BULBS:
        return None
    return np.array([GLASS[0] + GLASS[1] * c / 255.0 for c in rgb8(*LAMPS[key][1:3])])


def lens_texture(base, key):
    """The stock lens texture (level 0, decoded) times the bulb's glass: (256, 256, 4) uint8."""
    import write_dds
    _, faces = write_dds.read_dds(Path(base, *TEX, "front_glow_d.dds"))
    im = faces[0][0].astype(np.float64)
    im[..., :3] = im[..., :3] * glass_of(key)[None, None, :]
    return np.clip(np.round(im), 0, 255).astype(np.uint8)


def tex_name(key):
    return f"CMB\\Bike\\front_glow_{key}_d.dds"


def materials(base, glass):
    """{file name: material dict} of the eight files."""
    parked = bgsm.loads(Path(base, *MAT, "front_glow.bgsm").read_bytes())
    worn = bgsm.loads(Path(base, *MAT, "front_glow_worn.bgsm").read_bytes())
    out = {}
    for key in LAMPS:
        p, w = dict(parked, textures=dict(parked["textures"])), dict(worn, textures=dict(worn["textures"]))
        w["emittance_color"] = emit_of(key)
        if glass == "tinted" and glass_of(key) is not None:
            p["textures"]["diffuse"] = w["textures"]["diffuse"] = tex_name(key)
        out[f"front_glow_{key}.bgsm"] = p
        out[f"front_glow_{key}_worn.bgsm"] = w
    return out


def write(args):
    import write_dds
    mat, tex = Path(args.out, *MAT), Path(args.out, *TEX)
    mat.mkdir(parents=True, exist_ok=True)
    for name, m in materials(args.base, args.lens_glass).items():
        bgsm.write(mat / name, m)
        print(f"{mat / name}: emit {'on ' + str(m.get('emittance_color')) + ' x %.1f' % m['emittance_mult'] if m['emit_enabled'] else 'off'}, "
              f"diffuse {m['textures']['diffuse']}")
    if args.lens_glass == "tinted":
        tex.mkdir(parents=True, exist_ok=True)
        for key in LAMPS:
            if glass_of(key) is None:
                continue
            p = tex / f"front_glow_{key}_d.dds"
            p.write_bytes(write_dds.build([lens_texture(args.base, key)], "bc1", gamma_mips=True))
            print(f"{p}: bc1 256x256, glass {np.round(glass_of(key), 3).tolist()}")
    return 0


def check(args):
    import write_dds
    fails = 0

    def rep(ok, what, detail=""):
        nonlocal fails
        fails += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {what}{(': ' + detail) if detail else ''}")
    base_p = bgsm.loads(Path(args.base, *MAT, "front_glow.bgsm").read_bytes())
    base_w = bgsm.loads(Path(args.base, *MAT, "front_glow_worn.bgsm").read_bytes())
    want = materials(args.base, args.lens_glass)
    bad, diff = [], []
    for name, m in want.items():
        p = Path(args.out, *MAT, name)
        if not p.exists():
            bad.append(f"{name} missing")
            continue
        data = p.read_bytes()
        got = bgsm.loads(data)
        if bgsm.dumps(got) != data or data != bgsm.dumps(m):
            bad.append(f"{name}: not the expected bytes")
        stock = base_w if name.endswith("_worn.bgsm") else base_p
        changed = sorted(k for k in set(got) | set(stock) if k != "textures" and not k.startswith("_raw")
                         and got.get(k) != stock.get(k))
        changed += [f"textures.{k}" for k in stock["textures"] if got["textures"].get(k) != stock["textures"][k]]
        diff.append(f"{name} {','.join(changed) or 'none'}")
        allowed = ({"emittance_color"} if name.endswith("_worn.bgsm") else set()) | {"textures.diffuse"}
        if set(changed) - allowed:
            bad.append(f"{name}: changed {changed}")
        if name.endswith("_worn.bgsm"):
            key = name[len("front_glow_"):-len("_worn.bgsm")]
            if not got["emit_enabled"] or max(abs(a - b) for a, b in zip(got["emittance_color"], emit_of(key))) > 1e-6 \
                    or got["emittance_mult"] != EMIT_MULT:
                bad.append(f"{name}: emit {got['emit_enabled']} {got.get('emittance_color')} x {got['emittance_mult']}")
        elif got["emit_enabled"]:
            bad.append(f"{name}: lit on the parked bike")
    rep(not bad, f"the {len(want)} lens materials: read back byte for byte, the stock's but the emit colour (worn) and "
                 f"the diffuse (--lens-glass {args.lens_glass}); the parked ones unlit", "; ".join(bad) or "; ".join(diff))
    tbad, tinfo = [], []
    stock_im = write_dds.read_dds(Path(args.base, *TEX, "front_glow_d.dds"))[1][0][0][..., :3].reshape(-1, 3).mean(0)
    for key in LAMPS:
        p = Path(args.out, *TEX, f"front_glow_{key}_d.dds")
        if args.lens_glass != "tinted" or glass_of(key) is None:
            if p.exists():
                tbad.append(f"{p.name} there but not wanted")
            continue
        if not p.exists():
            tbad.append(f"{p.name} missing")
            continue
        info, faces = write_dds.read_dds(p)
        if (info["format"], info["w"], info["h"], info["mips"]) != ("bc1", 256, 256, 9):
            tbad.append(f"{p.name}: {info}")
        mean = faces[0][0][..., :3].reshape(-1, 3).mean(0)
        exp = stock_im * glass_of(key)
        if np.abs(mean - exp).max() > 3.0:
            tbad.append(f"{p.name}: mean {np.round(mean, 1).tolist()} not {np.round(exp, 1).tolist()}")
        tinfo.append(f"{key} {np.round(mean).astype(int).tolist()}")
    rep(not tbad, "the tinted lens textures: BC1 256 with 9 mips, the stock's mean colour times the glass "
                  f"(the stock {np.round(stock_im).astype(int).tolist()})", "; ".join(tbad) or ", ".join(tinfo))
    stock = {"front_glow.bgsm", "front_glow_worn.bgsm"}
    extra = sorted(q.name for q in Path(args.out, *MAT).glob("front_glow_*") if q.name not in want and q.name not in stock)
    rep(not extra, "no other front_glow_* material under --out (but the stock two)", ", ".join(extra))
    print("all checks passed" if not fails else f"{fails} check(s) failed")
    return 1 if fails else 0


def table():
    print("key              name               x       y      8-bit RGB (LIGH colour)   lens emit (x 6.0)          "
          "luminance/warm  from")
    for key, (name, x, y, what) in LAMPS.items():
        print(f"{key:16s} {name:18s} {x:.4f}  {y:.4f}  {str(rgb8(x, y)):25s} {str(emit_of(key)):26s} "
              f"{luminance_vs_warm(key):.2f}            {what}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", type=Path, help="a Data folder with the shipped front_glow.bgsm, _worn and front_glow_d.dds")
    ap.add_argument("--out", type=Path, help="a Data folder's layout to write into (or --check)")
    ap.add_argument("--lens-glass", choices=("tinted", "clear"), default="tinted",
                    help="the unlit lens: tinted (the default) the bulb's colour on the stock texture, clear the stock "
                         "texture (the parked files front_glow.bgsm byte for byte, no texture written)")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--table", action="store_true")
    args = ap.parse_args()
    if args.table:
        return table()
    if not args.base or not args.out:
        ap.error("--base and --out are needed")
    return check(args) if args.check else write(args)


if __name__ == "__main__":
    sys.exit(main())
