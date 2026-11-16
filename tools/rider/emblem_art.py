#!/usr/bin/env python3
"""The 3D helmet emblems' textures and materials files (build 2026-11-16a, C3 item 3.1).

Drawn from the same primitives as the geometry (emblem_pieces.field, evaluated at each texel of the helmet's cell), so
every colour region sits on its relief: no picture is read, traced or sampled.

  Textures\\CMB\\Bike\\helms_d.dds   BC1 1024 x 512   colour: a 512 cell a helmet (Enclave (0, 0), Brotherhood (1, 0))
  Textures\\CMB\\Bike\\helms_n.dds   BC5 1024 x 512   the fine detail only (rivets, ribbing, seams, grille holes: under
                                                     about 0.15 units, which the worn nifs' half floats would blur)
  Textures\\CMB\\Bike\\helms_s.dds   BC5 512 x 256    R specular, G smoothness (half-size cells)
  Textures\\CMB\\Bike\\helms_g.dds   BC1 512 x 256    the Enclave's eyes (the glow map; the Brotherhood's cell black)

  Materials\\CMB\\Bike\\helm_enclave.bgsm   the glow shader over helms_d/_n/_s with helms_g, no environment map (the
                                           master's shader can't have both); one file for the parked and worn bikes
  Materials\\CMB\\Bike\\helm_bos.bgsm       environment map Shared\\Cubemaps\\MetalChrome01Cube_e.dds (by path, as our
                                           badges) at 0.8, no glow
  Materials\\CMB\\Bike\\static_helm<Enclave|Bos><L|R>(_worn).bgsm   the shapes' own, invisible: the rim styles' own files
                                           (look_paint.off_material over bike_materials.json's wheelF_rimLaced: off_d/
                                           _n/_s, alpha test 255, alpha 0, no shadows), 8 files

The two emblem materials cast shadows, as the tank plates' and the badges' files do (the contract's note 8: c3.md's
"no shadows, as the plates'" read the plates wrong; the own files cast none, as the rim styles').

    <DDS python> -I tools/rider/emblem_art.py --data <Data> [--png <folder>] [--check]

--data: where Textures\\CMB\\Bike and Materials\\CMB\\Bike are written (an overlay's Data). --png also writes each map
as PNG (and the two cells' colour over their relief, shaded) for a look. --check reads a tree back: the 4 textures'
formats, sizes and full mip chains, the 10 files' values, and the own files byte for byte the rim styles' rule.
"""

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bgsm as B  # noqa: E402
import emblem_pieces as EP  # noqa: E402

CELL = 512
TEX = {"d": ("helms_d", "bc1", 1024, 512), "n": ("helms_n", "bc5", 1024, 512), "s": ("helms_s", "bc5", 512, 256),
       "g": ("helms_g", "bc1", 512, 256)}
TEX_PATH = {k: f"CMB\\Bike\\{v[0]}.dds" for k, v in TEX.items()}
ENV = "Shared\\Cubemaps\\MetalChrome01Cube_e.dds"
ENV_SCALE = 0.8
GLOW = dict(colour=(1.0, 1.0, 1.0), mult=1.5)     # the glow map carries the amber; white x 1.5 lights it
OWN_SPEC = "wheelF_rimLaced"                       # bike_materials.json: the rim styles' invisible own files


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float64) / 255.0


# the colours (sRGB) per helmet and region; the table's emblems.items colours are the anchors
PALETTE = {
    "enclave": {EP.METAL: ("1d1f22", "3a3d40"), EP.TRIM: ("3c4044", "62676c"), EP.LENS: ("b06a10", "ffb030"),
                EP.HOSE: ("141517", "2a2c2f"), EP.RECESS: ("0c0d0e", "17181a"), EP.CAN: ("1f2124", "3a3d40"),
                EP.PANEL: ("25282b", "44484c"), EP.BOLT: ("3c4044", "5a5e62")},
    "bos": {EP.METAL: ("6c7076", "a8adb3"), EP.TRIM: ("6a6e74", "9a9fa5"), EP.RECESS: ("1c1d20", "2a2c30"),
            EP.HOSE: ("1e1f22", "3a3c40"), EP.GLASS: ("b8bcc0", "e8e6dc"), EP.BOLT: ("80858b", "c0c5cb"),
            EP.LENS: ("2a2c30", "40444a")},
}
# R specular, G smoothness (linear 0..1) per region
FINISH = {
    "enclave": {EP.METAL: (0.42, 0.55), EP.TRIM: (0.60, 0.62), EP.LENS: (0.95, 0.92), EP.HOSE: (0.15, 0.30),
                EP.RECESS: (0.10, 0.20), EP.CAN: (0.40, 0.50), EP.PANEL: (0.45, 0.55), EP.BOLT: (0.55, 0.60)},
    "bos": {EP.METAL: (0.80, 0.72), EP.TRIM: (0.70, 0.66), EP.RECESS: (0.12, 0.25), EP.HOSE: (0.18, 0.35),
            EP.GLASS: (0.95, 0.95), EP.BOLT: (0.85, 0.75), EP.LENS: (0.90, 0.90)},
}


def box_blur(a, r):
    """A separable box blur of radius r texels (edges clamped)."""
    if r < 1:
        return a
    k = 2 * r + 1
    for axis in (0, 1):
        pad = [(0, 0)] * a.ndim
        pad[axis] = (r + 1, r)
        c = np.cumsum(np.pad(a, pad, mode="edge"), axis=axis)
        hi = np.take(c, np.arange(k, c.shape[axis]), axis=axis)
        lo = np.take(c, np.arange(0, c.shape[axis] - k), axis=axis)
        a = (hi - lo) / k
    return a


def hash_noise(X, Y, scale, seed):
    """Value noise (our own hash) at `scale` units, -1..1."""
    gx, gy = X / scale, Y / scale
    ix, iy = np.floor(gx).astype(np.int64), np.floor(gy).astype(np.int64)
    fx, fy = gx - ix, gy - iy

    def h(i, j):
        n = (i * 374761393 + j * 668265263 + seed * 1442695041) & 0xFFFFFFFF
        n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
        return ((n ^ (n >> 16)) & 0xFFFF) / 32767.5 - 1.0
    sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = h(ix, iy) * (1 - sx) + h(ix + 1, iy) * sx
    b = h(ix, iy + 1) * (1 - sx) + h(ix + 1, iy + 1) * sx
    return a * (1 - sy) + b * sy


def cell_maps(name, size=CELL):
    """One helmet's cell: colour (size, size, 3) sRGB 0..1, normal (size, size, 3) unit, specular (size, size, 2),
    glow (size, size, 3) sRGB 0..1."""
    X, Y = EP.texture_lattice(size)
    F = EP.field(name, X, Y)
    px = EP.CELL_BOX / size
    h = F.h
    inside = h > EP.SKIRT + 1e-6
    # the relief's light and shade, baked faintly (the game lights the geometry; this is the cast metal's cavity)
    r = max(1, int(round(0.18 / px)))
    cavity = h - box_blur(h, r)                      # + on ridges and edges, - in creases
    region = F.region.copy()
    # outside the footprint: the nearest region's colour (dilated), so mips and the skirt's texels don't bleed dark
    filled = region.copy()
    empty = filled == EP.NONE
    for _ in range(12):
        if not empty.any():
            break
        grown = filled.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh = np.roll(filled, (dy, dx), axis=(0, 1))
            take = (grown == EP.NONE) & (sh != EP.NONE)
            grown[take] = sh[take]
        filled = grown
        empty = filled == EP.NONE
    filled[filled == EP.NONE] = EP.METAL
    pal, fin = PALETTE[name], FINISH[name]
    lo = np.zeros(X.shape + (3,))
    hi = np.zeros(X.shape + (3,))
    spec = np.zeros(X.shape + (2,))
    for k, (a, b) in pal.items():
        m = filled == k
        lo[m], hi[m] = hexrgb(a), hexrgb(b)
    for k, sv in fin.items():
        spec[filled == k] = sv
    # the shade between each region's two colours: raised and edges lighter, creases darker, a little mottling
    noise = 0.5 * hash_noise(X, Y, 0.35, 11) + 0.25 * hash_noise(X, Y, 0.12, 12)
    if name == "bos":
        noise = 0.35 * hash_noise(X * 0.25, Y * 6.0, 0.2, 13) + 0.2 * noise     # brushed across
    t = np.clip((0.78 if name == "enclave" else 0.62) + 2.6 * cavity + 0.10 * noise + 0.04 * F.detail / 0.05, 0.0, 1.0)
    colour = lo + (hi - lo) * t[..., None]
    # the rivets and ribs (the detail): a lit top and a dark foot
    dd = F.detail
    colour *= (1.0 + np.clip(dd, -0.06, 0.06)[..., None] * 3.0)
    # the Enclave's lenses: deep amber at the rim, hot near the middle, a specular glint baked high on each
    glow = np.zeros(X.shape + (3,))
    if name == "enclave":
        lens = filled == EP.LENS
        core = np.clip(F.glow, 0, 1)
        amber, hot = hexrgb("ffb030"), hexrgb("ffd27a")
        shade = np.clip((h - 0.62) / 0.36, 0, 1)
        colour[lens] = (hexrgb("a35f0c") + (amber - hexrgb("a35f0c")) * shade[lens][:, None]
                        + (hot - amber) * np.clip(shade[lens] - 0.75, 0, 1)[:, None] * 2.0)
        glow[lens] = (amber[None] * (0.55 + 0.45 * shade[lens][:, None])) * core[lens][:, None]
    colour = np.clip(colour, 0.0, 1.0)
    # the normal map: the detail's slopes (v down the image)
    gy, gx = np.gradient(F.detail, px)
    n = np.stack([-gx, -gy, np.ones_like(h)], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return colour, n, spec, glow, F


def to8(a):
    return np.clip(np.round(a * 255.0), 0, 255).astype(np.uint8)


def rgba(rgb, a=255):
    out = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    out[..., :3] = rgb
    out[..., 3] = a
    return out


def half(a):
    return 0.25 * (a[0::2, 0::2] + a[1::2, 0::2] + a[0::2, 1::2] + a[1::2, 1::2])


def draw():
    """The four atlases as RGBA8 images: {'d', 'n', 's', 'g'}."""
    W = CELL * 2
    d = np.zeros((CELL, W, 3))
    n = np.zeros((CELL, W, 3))
    s = np.zeros((CELL, W, 2))
    g = np.zeros((CELL, W, 3))
    for name in EP.HELMETS:
        col, row = EP.CELLS[name]
        c, nn, sp, gl, _ = cell_maps(name)
        sl = (slice(row * CELL, (row + 1) * CELL), slice(col * CELL, (col + 1) * CELL))
        d[sl], n[sl], s[sl], g[sl] = c, nn, sp, gl
    imgs = {"d": rgba(to8(d)), "n": rgba(to8(n * 0.5 + 0.5))}
    s2 = half(s)
    imgs["s"] = rgba(np.dstack([to8(s2[..., 0]), to8(s2[..., 1]), np.zeros(s2.shape[:2], np.uint8)]))
    imgs["g"] = rgba(to8(half(g)))
    return imgs


def materials(mats):
    """{file stem: bgsm dict} of the ten materials files."""
    sys.path.insert(0, str(HERE))
    from look_paint import off_material   # C1's (imported: the rim styles' invisible files are made by it)
    tex = {"diffuse": TEX_PATH["d"], "normal": TEX_PATH["n"], "smoothspec": TEX_PATH["s"]}
    out = {
        "helm_enclave": B.new_bgsm(textures={**tex, "glow": TEX_PATH["g"]}, two_sided=True, environment_mapping=False,
                                   glowmap=True, emit_enabled=True, emittance_color=list(GLOW["colour"]),
                                   emittance_mult=GLOW["mult"], cast_shadows=True, receive_shadows=True,
                                   specular_enabled=True, smoothness=1.0, specular_mult=1.0),
        "helm_bos": B.new_bgsm(textures={**tex, "envmap": ENV}, two_sided=True, environment_mapping=True,
                               env_map_mask_scale=ENV_SCALE, cast_shadows=True, receive_shadows=True,
                               specular_enabled=True, smoothness=1.0, specular_mult=1.0),
    }
    for label, _, _ in EP.SHAPES:
        for w in ("", "_worn"):
            out[f"{label}{w}"] = off_material(mats[OWN_SPEC], False)
    return out


def write(args):
    import write_dds
    tdir = args.data / "Textures" / "CMB" / "Bike"
    mdir = args.data / "Materials" / "CMB" / "Bike"
    tdir.mkdir(parents=True, exist_ok=True)
    mdir.mkdir(parents=True, exist_ok=True)
    imgs = draw()
    opts = {"d": dict(gamma_mips=True), "n": dict(normal=True), "s": {}, "g": dict(gamma_mips=True)}
    for k, (stem, fmt, w, h) in TEX.items():
        im = imgs[k]
        if im.shape[:2] != (h, w):
            raise AssertionError(f"{stem}: {im.shape}")
        data = write_dds.build([im], fmt, **opts[k])
        (tdir / f"{stem}.dds").write_bytes(data)
        print(f"wrote {tdir / (stem + '.dds')}: {fmt} {w}x{h}, {len(data)} bytes")
    mats = json.loads(args.materials.read_text())["materials"]
    for stem, m in materials(mats).items():
        B.write(mdir / f"{stem}.bgsm", m)
    print(f"wrote 10 materials files into {mdir}: helm_enclave (glow, helms_g), helm_bos (env {ENV_SCALE:g}), the shapes' "
          f"8 own invisible ones")
    if args.png:
        png(args.png, imgs)
    return 0


def png(folder: Path, imgs):
    from PIL import Image
    folder.mkdir(parents=True, exist_ok=True)
    for k, im in imgs.items():
        Image.fromarray(im[..., :3]).save(folder / f"{TEX[k][0]}.png")
    # each cell's colour lit by its relief and detail, for a look
    for name in EP.HELMETS:
        c, nn, sp, gl, F = cell_maps(name)
        sh = EP.shade(F.h + F.detail, EP.CELL_BOX / CELL)
        lit = np.clip(c * (0.25 + 0.95 * sh[..., None]) + gl * 0.6, 0, 1)
        lit[F.h <= EP.SKIRT + 1e-6] = 0.12
        Image.fromarray(to8(lit)).save(folder / f"{name}_lit.png")
    print(f"wrote PNGs into {folder}")


def check(args):
    import write_dds
    ok = True

    def rep(good, what, detail=""):
        nonlocal ok
        ok &= bool(good)
        print(f"{'PASS' if good else 'FAIL'}  {what}{': ' + detail if detail else ''}")

    tdir = args.data / "Textures" / "CMB" / "Bike"
    mdir = args.data / "Materials" / "CMB" / "Bike"
    bad = []
    for k, (stem, fmt, w, h) in TEX.items():
        p = tdir / f"{stem}.dds"
        if not p.exists():
            bad.append(f"{stem}.dds missing")
            continue
        info, faces = write_dds.read_dds(p)
        line = write_dds.info(p)
        want = {"bc1": "DXT1", "bc5": "ATI2"}[fmt]
        mips = int(math.log2(max(w, h))) + 1
        if f"{w}x{h} {want} mips {mips}" not in line:
            bad.append(line)
    rep(not bad, "textures: helms_d BC1 1024x512, helms_n BC5 1024x512, helms_s BC5 512x256, helms_g BC1 512x256, each "
                 "with its full mip chain", "; ".join(bad))
    mats = json.loads(args.materials.read_text())["materials"]
    want = materials(mats)
    bad = []
    for stem, m in want.items():
        p = mdir / f"{stem}.bgsm"
        if not p.exists():
            bad.append(f"{stem}.bgsm missing")
            continue
        if p.read_bytes() != B.dumps(m):
            bad.append(f"{stem}.bgsm not as emblem_art.py writes it")
    rep(not bad, f"materials files: the {len(want)} there, as written (helm_enclave glow over helms_g, no cube; helm_bos "
                 f"{ENV} at {ENV_SCALE:g}; the 8 own files the rim styles' invisible rule)", "; ".join(bad))
    if args.reference:
        ref = args.reference / "Materials" / "CMB" / "Bike" / f"{OWN_SPEC}.bgsm"
        same = [stem for stem in want if stem.startswith("static_helm") and (mdir / f"{stem}.bgsm").exists()
                and (mdir / f"{stem}.bgsm").read_bytes() == ref.read_bytes()]
        rep(len(same) == 8, f"the 8 own files byte for byte the shipped {OWN_SPEC}.bgsm (the rim styles' own)",
            f"{len(same)} of 8")
    m = B.read(mdir / "helm_enclave.bgsm") if (mdir / "helm_enclave.bgsm").exists() else None
    if m:
        rep(m["glowmap"] and m["emit_enabled"] and not m["environment_mapping"] and m["textures"]["glow"] == TEX_PATH["g"]
            and not m["textures"]["envmap"], "helm_enclave.bgsm: the glow shader with helms_g, no environment map")
    m = B.read(mdir / "helm_bos.bgsm") if (mdir / "helm_bos.bgsm").exists() else None
    if m:
        rep(m["environment_mapping"] and abs(m["env_map_mask_scale"] - ENV_SCALE) < 1e-6 and m["textures"]["envmap"] == ENV
            and not m["glowmap"], f"helm_bos.bgsm: {ENV} at {ENV_SCALE:g}, no glow")
    print("emblem_art --check: " + ("all passed" if ok else "FAILED"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, required=True, help="the Data tree written (Textures, Materials)")
    ap.add_argument("--materials", type=Path, default=HERE / "bike_materials.json")
    ap.add_argument("--png", type=Path, help="also write the maps as PNG here")
    ap.add_argument("--check", action="store_true", help="check a written tree (nothing written)")
    ap.add_argument("--reference", type=Path, help="with --check: a Data tree with the shipped rim styles' own files")
    args = ap.parse_args()
    return check(args) if args.check else write(args)


if __name__ == "__main__":
    sys.exit(main())
