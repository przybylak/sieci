#!/usr/bin/env python3
"""The 2026-11-08a build's (C2) wheel and hue materials: no bake (C1's way: re-sampled and procedural texels).

What it writes into --data (Textures\\CMB\\Bike, Materials\\CMB\\Bike), every name in look_options.json:

  the rim atlas      one atlas for the 14 rim-style shapes (wheelF_rimLaced ... wheelR_rimScrap, each in its
                     rim_atlas cell, the mesh unit's UVs): rims_d.dds (2048, BC1) the index map of the five palette
                     finishes (U 56-127 the finish's shade 0.2-1.6, from a facing and radial occlusion term; 216-255 the
                     trims; 0-47 the Scrap plate's rust, from 3D value noise), its mips per part (look_paint.py's
                     index_levels and index_bc1, imported: no mip texel in a part its level-0 footprint lacks);
                     rims_chrome_d.dds (1024, BC1) the chrome finish's own diffuse (no palette: safe if the palette
                     fails on env-mapped materials): 0.8 x the bike's chrome shade times the same occlusion, the rust
                     in its own colours; rims_n.dds (1024, BC5) from a height field (rivets and weld beads on the Scrap
                     plate (the modelled ones, the mesh unit's steel part, hammered and rippled; drawn along the
                     plates' edges only for a shape without them), rolled lips round the Pre-war vents, rounded
                     feature edges, a fine grain); rims_s.dds
                     (1024, BC5) R specular, G smoothness per part
  rim_p.dds          256 x 8 RGBA8, one mip: rows 0-3 satin black, gloss black, bronze, gunmetal (rim_palette), 4-7
                     spare (row 3's); U 0-47 rust to bare steel, 56-127 the finish x 0.2-1.6, 216-255 the trims (a
                     silver ramp, log-spaced shade 0.02-1.4, so the cast rim's dark chrome, its machined edges fading
                     out of the black and its bright machined faces all fit), the guards blended
  the cast maps      castF_i_d.dds, castR_i_d.dds (1024, BC1): the stock cast rims' index maps re-sampled from
                     2026-11-07a's shipped wheel?_rim_d.dds and the bake's surface per texel (black_m's rim -> 56-127 at
                     its shade over the rim colour; the chrome, the machined faces and the rim's bright machined edges
                     -> 216-255 on the trim ramp), mips per part; they keep 2026-11-07a's _n and _s
  paint_p.dds        row 43 Factory (look_options.json's paint_rows; for body-colour rims; rows 0-42 byte for byte
                     2026-11-07a's: checked), the spare rows 44-63 row 43's (look_paint.py's palette_image, so its
                     --check agrees)
  paint_hue_p.dds    256 x 1024 RGBA8, one mip: row shade x 256 + h (h 0-255 = round(hue x 255 / 359)), the tank and
                     fenders the hue at the shade's (s, v), the coachline cream (hue_palette)
  the tyres          wheelF_tyre_ww_d.dds, wheelF_tyre_rl_d.dds, wheelR_... (1024, BC1): 2026-11-07a's shipped
                     tyre diffuse with a white band (whitewall) or a red ring (red line) on both sidewalls by radius from
                     the axle (tyre_bands), on the rubber's texels only (the low triangle's gum), an antialiased edge
                     0.15 wide, the rubber's own shading kept (its luminance over the tyre colour), the tread untouched
  the materials      rimF_<f>, rimR_<f> (7 finishes: chrome satin gloss bronze gunmetal body bodyhue) and castF_<f>,
                     castR_<f> (6: the same but chrome), each (.bgsm, _worn.bgsm) on 2026-11-07a's wheelF_rim/wheelR_rim
                     files (their shadows, two-sided, wetness): the finish's cube, env scale, smoothness and specular
                     (rim_finishes), the palette rim_p.dds at the finish's row centre, or paint_p.dds at Factory's
                     (body), or paint_hue_p.dds at the default hue's (bodyhue: Compose renames body to it with Free
                     colour; the colour index sets the row); chrome: rims_chrome_d, no palette. 8 tyre files (2026-
                     11-07a's tyre files, the diffuse renamed); static_paint_hue(.bgsm, _worn) and fork_paint_hue(...)
                     (C1's row files, the greyscale paint_hue_p.dds at the default's V): 64 in all

The rim shapes are read from --rim-stage (default --stage): shapes/<label>.npz (pos in the parked frame, tri, and per
triangle `part` 0 body, 1 trim, 2 steel (rusted: U 0-47), or else `mat`, the manifest's piece materials: chrome and silver trims, the
rest body) and uv/<label>.npz (uv per corner, (tris, 3, 2), v down; else the shape file's own `uv_fixed`). --standin <dir> writes a stand-in set there first
(simple procedural discs in the atlas cells, for exercising the writers until the mesh unit's shapes exist).

--check checks a built tree: formats, sizes, mips; the index maps' mips per part; the palette proof (2026-11-07a's own
cast rim through castF/R_i_d at PROOF_DB or more; every finish row through the BC1 index maps against the uncompressed
index at PROOF_DB or more); rim_p and paint_hue_p one mip, every BGSM's row at its row's centre; paint_p rows 0-42
2026-11-07a's; every BGSM read back; the tyre bands' radii from their texels within BAND_TOL and on the rubber only;
2026-11-07a's own files unchanged; nothing under the output's Textures but CMB's.

    <python with numpy, Pillow, quicktex, texture2ddecoder> -I tools/rider/look_wheels.py --data <Data> \\
        --base <2026-11-07a's Data> --stage <the stage folder> [--rim-stage <the mesh unit's stage>] \\
        [--standin <dir>] [--options look_options.json] [--check]

Fallout 4 semantics as look_paint.py's (no diffuse tint for lit materials; grayscale_to_palette_color, the greyscale
slot, grayscale_to_palette_scale the V, F4SE's MSWP colorIndex the same). Nothing from the files read is executed.
"""
import argparse
import colorsys
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bgsm as B  # noqa: E402
import look_paint as LP  # noqa: E402
import write_dds as W  # noqa: E402

CUBES = {"CH": "Shared\\Cubemaps\\MetalChrome01Cube_e.dds", "DI": "Shared\\Cubemaps\\mipblur_DefaultOutside1_dielectric.dds"}
TEX = "CMB\\Bike\\"
RIMS_D, RIMS_CHROME, RIMS_N, RIMS_S = 2048, 1024, 1024, 1024   # plan 2.3's sizes (the C2 texture budget)
CHROME = (0.36, 0.36, 0.38)          # bike_art.py's chrome diffuse (the cube gives the shine)
CHROME_K = 0.8
RUST = ("2e170c", "6e3418", "9a5428", "8a7a6a", "8a8d92")   # U 0 .. 47: deep rust, rust, light rust, scale, bare steel
TRIM_SHADE = (0.02, 1.4)             # rim_p's trim ramp, log-spaced: from the finish ramp's top on a black finish (the
                                     # cast rim's machined edges fade out of its black) to bright silver (its machined faces 1.0)
FINISH_SHADE = LP.BODY_SHADE         # 0.2-1.6, as the paint's body (the same U reads paint_p's rows on a body rim)
CAST_EDGE = 1.6                      # a cast rim texel past the finish ramp (x its rim colour's luminance) is a machined edge
PROOF_DB = 33.0
BAND_AA = 0.15                       # the tyre band's antialiased edge, units
BAND_TOL = 0.1                       # --check: the band's texels' radii within this of the table's
PARTS = ("body", "steel", "trim")    # index_levels' parts 0, 1, 2: the finish, the rust/steel, the trims (kept thin)
GUM = "gum"
FINISH_ROWS = 8


def seg_rim(opts):
    """index_bc1's segments for a rim index map: part 0 the finish, 1 the steel, 2 the trims (look_paint's keys:
    tank, fenders, coachline), primer a range no part uses (a BC1 texel decoding there is astray)."""
    u = opts["rim_palette"]["u"]
    return {"tank": tuple(u["finish"]), "fenders": tuple(u["steel"]), "coachline": tuple(u["trim"]), "primer": (136, 207)}


def trim_u(shade, seg):
    u0, u1 = seg["coachline"]
    t = np.log(np.clip(shade, *TRIM_SHADE) / TRIM_SHADE[0]) / math.log(TRIM_SHADE[1] / TRIM_SHADE[0])
    return u0 + (u1 - u0) * t


def finish_u(shade, seg):
    u0, u1 = seg["tank"]
    return u0 + (u1 - u0) * np.clip((shade - FINISH_SHADE[0]) / (FINISH_SHADE[1] - FINISH_SHADE[0]), 0, 1)


def rust_ramp(n):
    """(n, 3) linear: the steel segment's colours, deep rust to bare steel."""
    keys = np.array([LP.hexlin(h) for h in RUST])
    t = np.linspace(0, len(RUST) - 1, n)
    i = np.minimum(t.astype(int), len(RUST) - 2)
    f = (t - i)[:, None]
    return keys[i] * (1 - f) + keys[i + 1] * f


def rim_row(seg, finish, trim):
    """One rim_p row (256, 3) linear."""
    row = np.zeros((256, 3))
    s0, s1 = seg["fenders"]
    row[s0:s1 + 1] = rust_ramp(s1 - s0 + 1)
    u0, u1 = seg["tank"]
    t = (np.arange(u0, u1 + 1) - u0) / (u1 - u0)
    row[u0:u1 + 1] = LP.hexlin(finish) * (FINISH_SHADE[0] + (FINISH_SHADE[1] - FINISH_SHADE[0]) * t)[:, None]
    c0, c1 = seg["coachline"]
    t = (np.arange(c0, c1 + 1) - c0) / (c1 - c0)
    row[c0:c1 + 1] = LP.hexlin(trim) * (TRIM_SHADE[0] * (TRIM_SHADE[1] / TRIM_SHADE[0]) ** t)[:, None]
    for g0, g1 in ((s1, u0), (u1, c0)):          # the guards: blend the neighbours
        for i in range(g0 + 1, g1):
            f = (i - g0) / (g1 - g0)
            row[i] = row[g0] * (1 - f) + row[g1] * f
    return row


def rim_palette_image(opts):
    rp = opts["rim_palette"]
    seg = seg_rim(opts)
    img = np.zeros((FINISH_ROWS, 256, 4), np.uint8)
    img[..., 3] = 255
    rows = sorted(rp["rows"], key=lambda r: r["row"])
    for r in rows:
        img[r["row"], :, :3] = LP.to_u8(rim_row(seg, r["colour"], rp["trim_colour"]))
    for i in range(len(rows), FINISH_ROWS):
        img[i] = img[len(rows) - 1]
    return img


def hue_row(hp, shade, h):
    """The hue palette's row for shade 0-3 and h 0-255."""
    _, s, v = hp["shades"][shade]
    r, g, b = colorsys.hsv_to_rgb((h * 359.0 / 255.0) / 360.0, s, v)
    return "%02x%02x%02x" % tuple(int(round(c * 255)) for c in (r, g, b))


def hue_palette_image(opts):
    hp = opts["hue_palette"]
    seg = {k: tuple(v) for k, v in hp["u"].items()}
    w, h = hp["size"]
    img = np.zeros((h, w, 4), np.uint8)
    img[..., 3] = 255
    for sh in range(len(hp["shades"])):
        for k in range(256):
            a = hue_row(hp, sh, k)
            img[sh * 256 + k, :, :3] = LP.to_u8(LP.palette_row(seg, a, a, hp["coachline"]))
    return img


def hue_v(hue, shade):
    """V of the hue palette's row (look_options.json's hue_palette: (shade x 256 + round(hue x 255 / 359) + 0.5) / 1024)."""
    return (shade * 256 + int(round(hue * 255 / 359)) + 0.5) / 1024


def finish_v(opts, f):
    """The materials file's grayscale_to_palette_scale and palette for a finish key (body: Factory's paint_p row;
    bodyhue: the default hue's), or (None, None) for chrome."""
    if f == "bodyhue":
        return opts["hue_palette"]["texture"], hue_v(*opts["hue_palette"]["default"])
    fin = next(x for x in opts["rim_finishes"] if x["key"] == f)
    if fin["palette"] is None:
        return None, None
    if fin["palette"] == "body":
        return opts["palette"]["texture"], (43 + 0.5) / opts["palette"]["size"][1]
    return opts["rim_palette"]["texture"], (fin["palette"] + 0.5) / FINISH_ROWS


# --- geometry ----------------------------------------------------------------------------------------------------

def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _hash(ix, iy, iz, seed):
    v = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (seed * 2654435761)
    v &= 0xFFFFFFFF
    v ^= v >> 13
    v = (v * 1274126177) & 0xFFFFFFFF
    v ^= v >> 16
    return v / 4294967295.0 * 2.0 - 1.0


def noise3(P, scale, seed):
    """Smooth value noise in -1..1 at points P (n, 3), features about `scale` units (a hashed lattice, trilinear; the
    3D form of bike_art.py's hash_noise, so a feature runs on across UV seams)."""
    q = np.asarray(P, np.float64) / scale
    i = np.floor(q).astype(np.int64)
    f = q - i
    f = f * f * (3 - 2 * f)
    out = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * (f[:, 2] if dz else 1 - f[:, 2])
                out = out + w * _hash(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz, seed)
    return out


def raster(uv, H, Wd):
    """Rasterise per-corner UVs (n, 3, 2; v down, texel centres at +0.5) at H x Wd: (tid (H, Wd) int32, -1 empty;
    bary (H, Wd, 2) the corners 1 and 2's weights). A texel takes the last triangle covering its centre."""
    tid = np.full((H, Wd), -1, np.int32)
    bary = np.zeros((H, Wd, 2), np.float32)
    P = uv.astype(np.float64) * np.array([Wd, H])
    for t in range(len(P)):
        a, b, c = P[t]
        x0, x1 = int(max(0, math.floor(min(a[0], b[0], c[0]) - 0.5))), int(min(Wd - 1, math.ceil(max(a[0], b[0], c[0]))))
        y0, y1 = int(max(0, math.floor(min(a[1], b[1], c[1]) - 0.5))), int(min(H - 1, math.ceil(max(a[1], b[1], c[1]))))
        if x1 < x0 or y1 < y0:
            continue
        d = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
        if abs(d) < 1e-12:
            continue
        xs = np.arange(x0, x1 + 1) + 0.5
        ys = np.arange(y0, y1 + 1)[:, None] + 0.5
        l1 = ((xs - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (ys - a[1])) / d
        l2 = ((b[0] - a[0]) * (ys - a[1]) - (xs - a[0]) * (b[1] - a[1])) / d
        inside = (l1 >= -1e-6) & (l2 >= -1e-6) & (l1 + l2 <= 1 + 1e-6)
        if not inside.any():
            continue
        yy, xx = np.nonzero(inside)
        tid[y0 + yy, x0 + xx] = t
        bary[y0 + yy, x0 + xx, 0] = l1[inside]
        bary[y0 + yy, x0 + xx, 1] = l2[inside]
    return tid, bary


def axles(stage):
    """{F, R: the axle (parked frame)} from the tyres' texture stage."""
    return {w: np.array(json.loads((stage / "tex_cache" / f"wheel{w}_tyre" / "author.json").read_text())["axle"])
            for w in "FR"}


def tri_parts(shp, man):
    """Per triangle: 0 body, 1 rust (the steel segment), 2 trim; from the shape's `part` (0 body, 1 trim, 2 rust),
    else its piece materials (chrome, silver: trims)."""
    if "part" in shp:
        p = np.asarray(shp["part"]).astype(np.int64)
        return np.choose(np.clip(p, 0, 2), [0, 2, 1])
    if "mat" in shp:
        names = man["materials"]
        trim = np.array([n in ("chrome", "silver") for n in names])
        rust = np.array(["rust" in n for n in names])
        m = np.asarray(shp["mat"]).astype(np.int64)
        return np.where(trim[m], 2, np.where(rust[m], 1, 0))
    return np.zeros(len(shp["tri"]), np.int64)


def load_rim(rim_stage, label):
    """A rim-style shape from a stage: shapes/<label>.npz, its UVs from uv/<label>.npz or else its own `uv_fixed`
    (the mesh unit's fixed-UV labels carry them in the shape file)."""
    s = rim_stage / "shapes" / f"{label}.npz"
    u = rim_stage / "uv" / f"{label}.npz"
    if not s.exists():
        return None
    with np.load(s) as z:
        shp = {k: z[k] for k in z.files}
    if u.exists():
        with np.load(u) as z:
            shp["uv"] = z["uv"].astype(np.float64)
    elif "uv_fixed" in shp:
        shp["uv"] = shp["uv_fixed"].astype(np.float64)
    else:
        return None
    if shp["uv"].shape != (len(shp["tri"]), 3, 2):
        raise ValueError(f"{label}: uv {shp['uv'].shape} for {len(shp['tri'])} triangles")
    return shp


# --- the stand-in rim shapes (until the mesh unit's) --------------------------------------------------------------

def standin_mask(style, r, th, hub, hoop):
    """Solid or not at (r, theta deg) between the hub and the hoop, per style (a rough 2D look of each)."""
    if r < hub + 1.5:
        return True
    if style == "laced":
        return (th % 9.0) < 1.6
    if style == "disc":
        return True
    if style == "star":
        return ((th % 72.0) - 36.0) ** 2 < (np.degrees(1.75 / max(r, 1)) + 2) ** 2
    if style == "turbine":
        return ((th - 25.0 * r / hoop) % 30.0) < 14.0
    if style == "prewar":
        c = [(12.0 * math.cos(math.radians(45 * k + 22.5)), 12.0 * math.sin(math.radians(45 * k + 22.5))) for k in range(8)]
        x, y = r * math.cos(math.radians(th)), r * math.sin(math.radians(th))
        return all((x - cx) ** 2 + (y - cy) ** 2 > 2.4 ** 2 for cx, cy in c)
    if style == "atomic":
        if ((th % 120.0) - 60.0) ** 2 < (np.degrees(1.3 / max(r, 1)) + 1.5) ** 2:
            return True
        x, y = r * math.cos(math.radians(th)), r * math.sin(math.radians(th))
        for a in (30.0, 150.0):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            xe, ye = x * ca + y * sa, -x * sa + y * ca
            if abs(math.hypot(xe / (hoop * 0.8), ye / (hoop * 0.35)) - 1.0) < 0.06:
                return True
        return False
    if style == "scrap":
        return min(th % 120.0, 120.0 - th % 120.0) > 1.2
    raise ValueError(style)


def write_standin(opts, stage, out):
    """Stand-in rim shapes into out/shapes, out/uv (parked frame): per (style, wheel) a hoop band at the bead seat,
    its two flanges, and the style's 2D pattern as two faces at x +-2.6 (+-3.4 at the hub) in the envelope, planar UVs
    into the style's atlas cell (face +x the left half, -x the right, the hoop's strip along the bottom). Parts by
    radius (the flanges and the hub cap trims; on the Scrap plate every eleventh cell rust), in the mesh unit's
    convention (`part` 0 body, 1 trim, 2 rust)."""
    ax = axles(stage)
    env = opts["rim_envelope"]
    cells = opts["rim_atlas"]["cells"]
    size = opts["rim_atlas"]["size"][0]
    beads = {"F": env["measured"]["front"]["tyre_bead_r"], "R": env["measured"]["rear"]["tyre_bead_r"]}
    (out / "shapes").mkdir(parents=True, exist_ok=True)
    (out / "uv").mkdir(parents=True, exist_ok=True)
    made = []
    for st in opts["rim_styles"]:
        for w, label in zip("FR", st["shapes"]):
            A = ax[w]
            hoop = env["hoop_r_min"][0 if w == "F" else 1]
            bead = beads[w] - 0.15
            hub = 2.2
            cx, cy, cw, ch = cells[f"{st['key']}_{w}"]
            m = opts["rim_atlas"]["margin"]
            ucell = lambda fu, fv: ((cx + m + fu * (cw - 2 * m)) / size, (cy + m + fv * (ch - 2 * m)) / size)
            V, T, UV, PT = [], [], [], []

            def quad(p, uvs, part):
                n0 = len(V)
                V.extend(p)
                T.append((n0, n0 + 1, n0 + 2))
                T.append((n0, n0 + 2, n0 + 3))
                UV.append((uvs[0], uvs[1], uvs[2]))
                UV.append((uvs[0], uvs[2], uvs[3]))
                PT.extend([part, part])

            def pt(x, r, th):
                return (A[0] + x, A[1] + r * math.cos(math.radians(th)), A[2] + r * math.sin(math.radians(th)))

            nr, nt = 22, 160
            rs = np.linspace(hub, hoop, nr + 1)
            ths = np.linspace(0, 360, nt + 1)
            for side, sgn, cu in ((0, 1.0, 0.25), (1, -1.0, 0.75)):
                xof = lambda r: sgn * (3.4 - 0.8 * smoothstep(hub, 8.0, r))
                for i in range(nr):
                    for j in range(nt):
                        r0, r1, t0, t1 = rs[i], rs[i + 1], ths[j], ths[j + 1]
                        if not standin_mask(st["key"], (r0 + r1) / 2, (t0 + t1) / 2, hub, hoop):
                            continue
                        corners = [(r0, t0), (r1, t0), (r1, t1), (r0, t1)]
                        if sgn < 0:
                            corners = corners[::-1]
                        p = [pt(xof(r), r, t) for r, t in corners]
                        uvs = [ucell(cu + 0.23 * r / bead * math.cos(math.radians(t)) * (1 if sgn > 0 else -1),
                                     0.4 + 0.23 * r / bead * math.sin(math.radians(t))) for r, t in corners]
                        part = 1 if (r0 < hub + 1.2) or (st["key"] == "prewar" and r1 <= 9.0) else 0
                        if st["key"] == "scrap" and (i * 7 + j * 3) % 11 == 0:
                            part = 2
                        quad(p, uvs, part)
                # the flange from the hoop to the bead seat
                for j in range(nt):
                    t0, t1 = ths[j], ths[j + 1]
                    corners = [(hoop, t0), (bead, t0), (bead, t1), (hoop, t1)]
                    if sgn < 0:
                        corners = corners[::-1]
                    p = [pt(sgn * 4.4, r, t) for r, t in corners]
                    uvs = [ucell(cu + 0.23 * r / bead * math.cos(math.radians(t)) * (1 if sgn > 0 else -1),
                                 0.4 + 0.23 * r / bead * math.sin(math.radians(t))) for r, t in corners]
                    quad(p, uvs, 1)
            # the hoop band (the bead seat), outward
            for j in range(nt):
                t0, t1 = ths[j], ths[j + 1]
                p = [pt(-4.4, bead, t0), pt(4.4, bead, t0), pt(4.4, bead, t1), pt(-4.4, bead, t1)]
                uvs = [ucell(t0 / 360, 0.80), ucell(t0 / 360, 0.98), ucell(t1 / 360, 0.98), ucell(t1 / 360, 0.80)]
                quad(p, uvs, 0)
            V = np.array(V)
            T = np.array(T, np.int32)
            np.savez(out / "shapes" / f"{label}.npz", pos=V, tri=T, part=np.array(PT, np.int8))
            np.savez(out / "uv" / f"{label}.npz", uv=np.array(UV, np.float32))
            made.append(f"{label} {len(T)}")
    print("stand-in rim shapes: " + ", ".join(made))


# --- the rim atlas -----------------------------------------------------------------------------------------------

def feature_edges(tri, pos, crease_deg=80.0):
    """[(face, corner a, corner b, sign, open)]: the mesh's open edges and its creases sharper than crease_deg (convex
    +1, concave -1; an open edge +1), once for each face they bound (80 degrees: a 5-sided round bar's edges aren't
    creases, a blade's or a plate's square edges are). Vertices are welded by position first (a shape
    split at its UV seams has no open edge there)."""
    _, weld = np.unique(np.round(pos / 1e-4).astype(np.int64), axis=0, return_inverse=True)
    weld = weld.ravel()
    e = {}
    for f, t in enumerate(tri):
        for k in range(3):
            a, b = int(weld[t[k]]), int(weld[t[(k + 1) % 3]])
            if a != b:
                e.setdefault((min(a, b), max(a, b)), []).append((f, k, (k + 1) % 3))
    fn = unit(np.cross(pos[tri[:, 1]] - pos[tri[:, 0]], pos[tri[:, 2]] - pos[tri[:, 0]]))
    cosc = math.cos(math.radians(crease_deg))
    out = []
    for fs in e.values():
        if len(fs) == 1:
            out.append(fs[0] + (1, True))
        elif len(fs) == 2:
            (f1, a1, b1), (f2, a2, b2) = fs
            if float(fn[f1] @ fn[f2]) < cosc:
                c2 = pos[tri[f2, 3 - a2 - b2]]
                sign = -1 if float((c2 - pos[tri[f1, a1]]) @ fn[f1]) > 0 else 1
                out.append((f1, a1, b1, sign, False))
                out.append((f2, a2, b2, sign, False))
    return out


def edge_field(edges, shp, tid, uvpx, upt, reach):
    """Per texel: the least distance (units) to a feature edge, on the side of the edge its face lies (in UV), within
    reach units; its sign (+1 convex or open, -1 concave) and whether it is an open edge; inf where none."""
    H, Wd = tid.shape
    dist = np.full((H, Wd), np.inf)
    sign = np.zeros((H, Wd))
    opened = np.zeros((H, Wd), bool)
    for f, ka, kb, sg, bnd in edges:
        p0, p1, pc = uvpx[f, ka], uvpx[f, kb], uvpx[f, 3 - ka - kb]
        rpx = reach / max(upt[f], 1e-6)
        x0, x1 = int(max(0, math.floor(min(p0[0], p1[0]) - rpx))), int(min(Wd - 1, math.ceil(max(p0[0], p1[0]) + rpx)))
        y0, y1 = int(max(0, math.floor(min(p0[1], p1[1]) - rpx))), int(min(H - 1, math.ceil(max(p0[1], p1[1]) + rpx)))
        if x1 < x0 or y1 < y0:
            continue
        xs = np.arange(x0, x1 + 1) + 0.5
        ys = np.arange(y0, y1 + 1)[:, None] + 0.5
        d = p1 - p0
        L2 = max(float(d @ d), 1e-12)
        side_c = d[0] * (pc[1] - p0[1]) - d[1] * (pc[0] - p0[0])
        side = d[0] * (ys - p0[1]) - d[1] * (xs - p0[0])
        t = np.clip(((xs - p0[0]) * d[0] + (ys - p0[1]) * d[1]) / L2, 0, 1)
        dd = np.hypot(xs - (p0[0] + t * d[0]), ys - (p0[1] + t * d[1])) * upt[f]
        cur = dist[y0:y1 + 1, x0:x1 + 1]
        take = (tid[y0:y1 + 1, x0:x1 + 1] >= 0) & (side * side_c >= 0) & (dd < cur) & (dd < reach)
        cur[take] = dd[take]
        sign[y0:y1 + 1, x0:x1 + 1][take] = sg
        opened[y0:y1 + 1, x0:x1 + 1][take] = bnd
    return dist, sign, opened


def rivet_points(edges, shp, spacing, inset):
    """Rivet centres (3D) along the feature edges, inset into their face, at least spacing x 0.8 apart."""
    pos, tri = shp["pos"].astype(np.float64), shp["tri"]
    pts = []
    for f, ka, kb, sg, bnd in edges:
        pa, pb, c = pos[tri[f, ka]], pos[tri[f, kb]], pos[tri[f, 3 - ka - kb]]
        L = float(np.linalg.norm(pb - pa))
        if L < 1e-6:
            continue
        d = (pb - pa) / L
        inward = c - pa - d * float((c - pa) @ d)
        inward = inward / max(float(np.linalg.norm(inward)), 1e-9)
        for k in range(int(L // spacing) + 1):
            pts.append(pa + d * min(L, (k + 0.5) * spacing) + inward * inset)
    keep = []
    for p in pts:
        if all(np.linalg.norm(p - q) > spacing * 0.8 for q in keep):
            keep.append(p)
    return np.array(keep).reshape(-1, 3)


def rim_texels(opts, stage, rim_stage, man):
    """The atlas at RIMS_D: per texel the shape (-1 empty), its part, the U, the chrome colour (linear), the height
    (units) and spec/smoothness, plus the units per texel; and per shape what was found."""
    S = RIMS_D
    seg = seg_rim(opts)
    ax = axles(stage)
    env = opts["rim_envelope"]
    shape_of = np.full((S, S), -1, np.int32)
    part = np.full((S, S), -1, np.int64)
    U = np.zeros((S, S))
    chrome = np.zeros((S, S, 3))
    height = np.zeros((S, S))
    spec = np.zeros((S, S, 2))
    upt_img = np.zeros((S, S))
    report = []
    labels = [(st, w, lab) for st in opts["rim_styles"] for w, lab in zip("FR", st["shapes"])]
    rust_lin = rust_ramp(48)
    for si, (st, w, label) in enumerate(labels):
        shp = load_rim(rim_stage, label)
        if shp is None:
            raise SystemExit(f"look_wheels: {label}'s shape or uv not in {rim_stage} (the mesh unit's stage; --standin)")
        pos, tri, uv = shp["pos"].astype(np.float64), shp["tri"].astype(np.int64), shp["uv"]
        tid, bary = raster(uv, S, S)
        cov = tid >= 0
        if not cov.any():
            raise SystemExit(f"look_wheels: {label} covers no texel")
        cell = opts["rim_atlas"]["cells"][f"{st['key']}_{w}"]
        uvpx = uv * S
        out_cell = ((uvpx[..., 0] < cell[0] - 0.5) | (uvpx[..., 0] > cell[0] + cell[2] + 0.5) |
                    (uvpx[..., 1] < cell[1] - 0.5) | (uvpx[..., 1] > cell[1] + cell[3] + 0.5)).any(1)
        # units per texel per triangle
        a3 = np.linalg.norm(np.cross(pos[tri[:, 1]] - pos[tri[:, 0]], pos[tri[:, 2]] - pos[tri[:, 0]]), axis=1) / 2
        e1, e2 = uvpx[:, 1] - uvpx[:, 0], uvpx[:, 2] - uvpx[:, 0]
        a2 = np.abs(e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]) / 2
        upt = np.sqrt(a3 / np.maximum(a2, 1e-9))
        ys, xs = np.nonzero(cov)
        t = tid[ys, xs].astype(np.int64)
        l1, l2 = bary[ys, xs, 0].astype(np.float64), bary[ys, xs, 1].astype(np.float64)
        wts = np.stack([1 - l1 - l2, l1, l2], 1)
        P = (wts[:, :, None] * pos[tri[t]]).sum(1)
        if "nrm" in shp:
            N = unit((wts[:, :, None] * shp["nrm"].astype(np.float64)[tri[t]]).sum(1))
        else:
            N = unit(np.cross(pos[tri[t, 1]] - pos[tri[t, 0]], pos[tri[t, 2]] - pos[tri[t, 0]]))
        A = ax[w]
        dy, dz = P[:, 1] - A[1], P[:, 2] - A[2]
        r = np.hypot(dy, dz)
        er = np.stack([np.zeros_like(r), dy, dz], 1) / np.maximum(r, 1e-6)[:, None]
        hoop = env["hoop_r_min"][0 if w == "F" else 1]
        tp = tri_parts(shp, man)[t]
        # occlusion: the hub's and the hoop's well darker, faces turned along the rim darker than the side faces
        inward = np.clip(-(N * er).sum(1), 0, 1)
        occ = (1 - 0.25 * np.exp(-np.maximum(r - 2.0, 0) / 2.0))
        occ *= 1 - 0.35 * smoothstep(0.3, 0.9, inward) * smoothstep(hoop - 4.0, hoop, r)
        occ *= 0.8 + 0.2 * np.abs(N[:, 0])
        occ *= 1 + 0.03 * noise3(P, 2.5, 11 + si)
        # the Scrap plate's rust: patches from 3D noise on its body, all of a tagged rust part
        rust_a = np.zeros(len(t))
        if st["key"] == "scrap":
            n = 0.65 * noise3(P, 3.0, 101) + 0.35 * noise3(P, 0.9, 102)
            rust_a = smoothstep(0.25, 0.6, n)
            tp = np.where((tp == 0) & (rust_a > 0.5), 1, tp)
        rust_a = np.where(tp == 1, np.maximum(rust_a, 0.55), rust_a)
        u = np.where(tp == 2, trim_u(0.95 * occ, seg), finish_u(occ, seg))
        su0, su1 = seg["fenders"]
        u = np.where(tp == 1, su0 + (su1 - su0) * np.clip(1.15 - rust_a, 0, 1) * np.clip(occ, 0.6, 1.0), u)
        # the chrome finish's own diffuse
        ch = np.array(CHROME) * CHROME_K
        ch_lin = LP.lin(ch)[None, :] * occ[:, None] ** 1.5
        ridx = np.clip(np.rint(u - su0), 0, 47).astype(int)
        ch_lin = np.where((tp == 1)[:, None], rust_lin[ridx], ch_lin)
        # spec (R) and smoothness (G)
        sp = np.where(tp[:, None] == 2, [0.95, 0.9], np.where(tp[:, None] == 1, [0.12, 0.3], [0.75, 0.85]))
        sp = sp * np.stack([0.6 + 0.4 * occ, np.ones_like(occ)], 1)
        # the height: grain, and later the edges and the Scrap's rivets
        h = 0.004 * noise3(P, 0.25, 7 + si)
        h = np.where(tp == 1, h + 0.02 * noise3(P, 0.35, 9), h)
        shape_of[ys, xs] = si
        part[ys, xs] = tp
        U[ys, xs] = u
        chrome[ys, xs] = ch_lin
        height[ys, xs] = h
        spec[ys, xs] = sp
        upt_img[ys, xs] = upt[t]
        # feature edges: rounded (convex), filleted (concave), the Pre-war vents' rolled lips; the Scrap's welds/rivets
        edges = feature_edges(tri, pos)
        reach = 0.45
        d, sg, bnd = edge_field(edges, shp, tid, uvpx, upt, reach)
        near = np.isfinite(d) & cov
        prof = np.where(near, (1 - np.clip(d / reach, 0, 1)) ** 2, 0.0)
        rolled = st["key"] == "prewar"
        hh = np.where(bnd & rolled, 0.10 * np.sqrt(np.clip(1 - np.abs(d / reach * 2 - 1), 0, 1)), -0.06 * sg * prof)
        height += np.where(near, hh, 0.0)
        n_rivets = 0
        has_steel = bool((tri_parts(shp, man) == 1).any())
        if has_steel:
            # the modelled rivets and weld beads (the steel part): a hammered, rippled surface
            k = tp == 1
            height[ys[k], xs[k]] += 0.015 * noise3(P[k], 0.12, 31) + 0.01 * np.sin(P[k, 1] * 22.0 + P[k, 2] * 22.0)
        elif st["key"] == "scrap":
            Pimg = np.zeros((S, S, 3))
            Pimg[ys, xs] = P
            # weld beads along the creases near the hub and the hoop, rivets along the rest
            rr = lambda e: float(np.hypot(*(pos[tri[e[0], [e[1], e[2]]]].mean(0)[1:] - A[1:])))
            at_ring = [rr(e) < 5.0 or rr(e) > hoop - 2.0 for e in edges]
            weld = [e for e, z in zip(edges, at_ring) if z]
            riv = [e for e, z in zip(edges, at_ring) if not z]
            dw, _, _ = edge_field(weld, shp, tid, uvpx, upt, 0.35)
            wz = np.isfinite(dw) & cov
            ripple = 0.75 + 0.25 * np.sin(Pimg[..., 1] * 18.0 + Pimg[..., 2] * 18.0)
            height += np.where(wz, 0.12 * np.clip(1 - (dw / 0.35) ** 2, 0, 1) * ripple, 0.0)
            rp = rivet_points(riv, shp, 2.2, 0.9)
            n_rivets = len(rp)
            rpx = 0.4 / max(float(np.median(upt)), 1e-6) + 2
            for c in rp:
                # the rivet's texels: its nearest covered texel's neighbourhood, by 3D distance
                k = np.argmin(((P - c) ** 2).sum(1))
                cy_, cx_ = ys[k], xs[k]
                y0, y1 = max(0, int(cy_ - rpx)), min(S, int(cy_ + rpx + 1))
                x0, x1 = max(0, int(cx_ - rpx)), min(S, int(cx_ + rpx + 1))
                sub = Pimg[y0:y1, x0:x1]
                dd = np.linalg.norm(sub - c, axis=-1)
                m = (shape_of[y0:y1, x0:x1] == si) & (dd < 0.38)
                height[y0:y1, x0:x1] += np.where(m, 0.14 * np.sqrt(np.clip(1 - (dd / 0.38) ** 2, 0, 1)), 0.0)
                part[y0:y1, x0:x1][m] = 2
                U[y0:y1, x0:x1][m] = trim_u(0.9, seg)
                spec[y0:y1, x0:x1][m] = (0.9, 0.85)
        report.append(dict(label=label, tris=int(len(tri)), texels=int(cov.sum()), units_per_texel=round(float(np.median(upt)), 4),
                           parts={PARTS[p]: int((tp == p).sum()) for p in range(3)}, outside_cell=int(out_cell.sum()),
                           feature_edges=len(edges), rivets=n_rivets))
    return dict(shape=shape_of, part=part, U=U, chrome=chrome, height=height, spec=spec, upt=upt_img, report=report)


def dilate_from(cov, *imgs, rounds=96):
    """Empty texels take their nearest covered texel's values (look_paint.dilate on the texel index)."""
    H, Wd = cov.shape
    lab = np.where(cov, np.arange(H * Wd).reshape(H, Wd), -1)
    lab = LP.dilate(lab, rounds)
    got = lab >= 0
    out = []
    for im in imgs:
        o = im.copy()
        flat = im.reshape(H * Wd, *im.shape[2:])
        o[got] = flat[lab[got]]
        out.append(o)
    return got, out


def down(img, f):
    """Box-filter an (H, W[, C]) image by an integer factor."""
    if f == 1:
        return img
    H, Wd = img.shape[:2]
    return img.reshape(H // f, f, Wd // f, f, *img.shape[2:]).mean(axis=(1, 3))


def normals_from_height(h, strength=1.0):
    """A Direct3D tangent-space normal map (R +u, G +v down the image, B out) from a height field in texel units (as
    bike_art.py's)."""
    gy, gx = np.gradient(h)
    n = np.stack([-gx * strength, -gy * strength, np.ones_like(h)], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return np.clip(np.rint((n * 0.5 + 0.5) * 255), 0, 255).astype(np.uint8)


def rim_atlas(opts, stage, rim_stage, man):
    """The atlas's four images: (rims_d's index (2048) and its parts, rims_chrome_d RGBA, rims_n RGBA, rims_s RGBA,
    the report)."""
    tx = rim_texels(opts, stage, rim_stage, man)
    cov = tx["shape"] >= 0
    got, (part, U, ch, hgt, spec, upt) = dilate_from(cov, tx["part"], tx["U"], tx["chrome"], tx["height"], tx["spec"], tx["upt"])
    part = np.where(part < 0, 0, part)
    U = np.where(got, U, finish_u(np.ones_like(U), seg_rim(opts)))
    g = np.clip(np.rint(U), 0, 255).astype(np.uint8)
    # the 1024 maps
    f = RIMS_D // RIMS_CHROME
    ch1 = LP.to_u8(down(np.where(got[..., None], ch, LP.lin(np.array(CHROME) * CHROME_K)), f))
    chrome_rgba = np.dstack([ch1, np.full(ch1.shape[:2], 255, np.uint8)])
    f = RIMS_D // RIMS_N
    upt1 = down(np.where(got, upt, 0.0), f) * f
    h1 = down(np.where(got, hgt, 0.0), f) / np.maximum(upt1, 1e-6)
    n1 = normals_from_height(np.where(down(got.astype(float), f) > 0, h1, 0.0))
    normal_rgba = np.dstack([n1, np.full(n1.shape[:2], 255, np.uint8)])
    f = RIMS_D // RIMS_S
    s1 = down(np.where(got[..., None], spec, 0.5), f)
    s8 = np.clip(np.rint(s1 * 255), 0, 255).astype(np.uint8)
    spec_rgba = np.dstack([s8[..., 0], s8[..., 1], np.zeros_like(s8[..., 0]), np.full(s8.shape[:2], 255, np.uint8)])
    return g, part, chrome_rgba, normal_rgba, spec_rgba, tx["report"], cov


# --- the cast rims' index maps -----------------------------------------------------------------------------------

def cast_surfaces(stage, label, man, mats):
    """Per texel of the cast rim's 1024 map: its surface (bike_textures.py's rule: the low triangle's piece material,
    the high mesh's override), and covered."""
    with np.load(stage / "tex_cache" / label / "bake.npz") as z:
        tid, hid = z["tid"].astype(np.int64), z["hid"].astype(np.int64)
    with np.load(stage / "shapes" / f"{label}.npz") as z:
        mat = z["mat"].astype(np.int64)
    surf_of_piece = mats["materials"][label]["surfaces"]
    names = man["materials"]
    cov = tid >= 0
    low = np.where(cov, mat[np.clip(tid, 0, None)], -1)
    surf = np.full(tid.shape, "", object)
    for k, n in enumerate(names):
        if n in surf_of_piece:
            surf[low == k] = surf_of_piece[n]
    for h, s in mats["surface_overrides"].items():
        surf[cov & (hid == int(h))] = s
    return surf, cov


def cast_index(d_srgb, surf, cov, opts, mats):
    """The cast rim's index map (H, W) uint8 from its shipped diffuse and surfaces, its parts (0 the finish, 2 the
    trims) and covered texels."""
    seg = seg_rim(opts)
    st = mats["surface_types"]
    L = LP.lum(LP.lin(d_srgb.astype(np.float64) / 255.0))
    rim_l = LP.lum(LP.hexlin(st["rim"]["colour"]))
    trim_l = LP.lum(LP.hexlin(opts["rim_palette"]["trim_colour"]))
    is_rim = surf == "rim"
    trim = cov & (~is_rim | (L / rim_l > CAST_EDGE))
    part = np.where(trim, 2, np.where(cov, 0, -1))
    part = LP.dilate(part)
    part[part < 0] = 0
    u = np.where(part == 2, trim_u(L / trim_l, seg), finish_u(L / rim_l, seg))
    return np.clip(np.rint(u), 0, 255).astype(np.uint8), part


# --- the tyres ---------------------------------------------------------------------------------------------------

def uv_islands(tri, uv, faces):
    """Union-find of the given faces into islands joined by edges shared in UV too: {face: root}."""
    par = {int(f): int(f) for f in faces}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    seen = {}
    for f in faces:
        for k in range(3):
            a_, b_ = int(tri[f, k]), int(tri[f, (k + 1) % 3])
            ua, ub = tuple(np.round(uv[f, k] * 8192).astype(int)), tuple(np.round(uv[f, (k + 1) % 3] * 8192).astype(int))
            key = (a_, ua, b_, ub) if a_ < b_ else (b_, ub, a_, ua)
            if key in seen:
                par[find(int(f))] = find(seen[key])
            else:
                seen[key] = int(f)
    return {f: find(f) for f in par}


def ring_fit(cu, cr, c0, r_max):
    """r = a + b rho + k rho^2 with rho = |uv - c| fitted to corners (uv, r) with r < r_max, the centre refined from c0
    (Gauss-Newton): (c, (a, b, k), rms)."""
    sel = cr < r_max
    u, r = cu[sel], cr[sel]
    c = np.array(c0, np.float64)
    coef = np.zeros(3)
    for _ in range(12):
        d = u - c
        rho = np.maximum(np.linalg.norm(d, axis=1), 1e-9)
        M = np.c_[np.ones_like(rho), rho, rho * rho]
        coef = np.linalg.lstsq(M, r, rcond=None)[0]
        res = r - M @ coef
        drho = -(d / rho[:, None]) * (coef[1] + 2 * coef[2] * rho)[:, None]
        step = np.linalg.lstsq(drho, res, rcond=None)[0]
        c = c + step
        if np.abs(step).max() < 1e-7:
            break
    rho = np.linalg.norm(u - c, axis=1)
    res = r - (coef[0] + coef[1] * rho + coef[2] * rho * rho)
    return c, coef, float(np.sqrt((res ** 2).mean()))


RING_FIT_RMS = 0.15     # a sidewall island's UV radius stands for the radius when its fit is this good (units)


def tyre_radius(stage, label, man, w):
    """Per texel of the tyre's 1024 map: its radius from the axle, the rubber mask, covered, and a report. On a
    sidewall ring island (a UV island of the gum going all round), the radius is the island's UV radius fitted to its
    vertices' true radii (the sidewall's UVs are a side projection of the round tyre; its low triangles span many
    degrees, so their flat interiors would draw the band jagged); elsewhere the low triangle's own point's."""
    with np.load(stage / "tex_cache" / label / "bake.npz") as z:
        tid, bary = z["tid"].astype(np.int64), z["bary"].astype(np.float64)
    with np.load(stage / "shapes" / f"{label}.npz") as z:
        pos, tri, mat = z["pos"].astype(np.float64), z["tri"].astype(np.int64), z["mat"].astype(np.int64)
    with np.load(stage / "uv" / f"{label}.npz") as z:
        uv = z["uv"].astype(np.float64)
    A = axles(stage)[w]
    H, Wd = tid.shape
    cov = tid >= 0
    t = np.clip(tid, 0, None)
    l1, l2 = bary[..., 0], bary[..., 1]
    P = pos[tri[t, 0]] * (1 - l1 - l2)[..., None] + pos[tri[t, 1]] * l1[..., None] + pos[tri[t, 2]] * l2[..., None]
    r = np.hypot(P[..., 1] - A[1], P[..., 2] - A[2])
    gum_t = mat == man["materials"].index(GUM)
    gum = cov & gum_t[t]
    rv = np.hypot(pos[:, 1] - A[1], pos[:, 2] - A[2])
    faces = np.nonzero(gum_t)[0]
    isl = uv_islands(tri, uv, faces)
    root = np.full(len(tri), -1, np.int64)
    root[list(isl.keys())] = list(isl.values())
    rings = []
    tex_uv = np.stack(np.meshgrid((np.arange(Wd) + 0.5) / Wd, (np.arange(H) + 0.5) / H), -1)
    troot = np.where(cov, root[t], -1)
    for rt in np.unique(root[root >= 0]):
        fs = np.nonzero(root == rt)[0]
        cu, cr = uv[fs].reshape(-1, 2), rv[tri[fs]].ravel()
        ang = np.degrees(np.arctan2(*(cu - cu.mean(0)).T[::-1]))
        hist = np.histogram(ang, bins=36, range=(-180, 180))[0]
        if len(fs) < 50 or (hist > 0).sum() < 33 or cr.min() > 26.0 or cr.max() < 22.0:
            continue
        e1, e2 = uv[fs, 1] - uv[fs, 0], uv[fs, 2] - uv[fs, 0]
        a2 = np.abs(e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0])
        c0 = (uv[fs].mean(1) * a2[:, None]).sum(0) / max(a2.sum(), 1e-12)
        c, coef, rms = ring_fit(cu, cr, c0, 28.0)
        ok = rms <= RING_FIT_RMS
        if ok:
            sel = troot == rt
            rho = np.linalg.norm(tex_uv[sel] - c, axis=1)
            r[sel] = coef[0] + coef[1] * rho + coef[2] * rho * rho
        rings.append(dict(tris=int(len(fs)), r=[round(float(cr.min()), 2), round(float(cr.max()), 2)], rms=round(rms, 3), used=ok))
    return r, gum, cov, rings


def tyre_band(stage, label, man, mats, opts, w, band):
    """(coverage (H, W) of the band, radius per texel, rubber mask, covered, the ring fits) for a tyre and a band key.
    The coverage is on the rubber's covered texels, then carried into the empty texels round them (each its nearest
    covered texel's), so a seam's gutter doesn't draw a dark line through the band."""
    r, gum, cov, rings = tyre_radius(stage, label, man, w)
    r0, r1 = opts["tyre_bands"][band][0 if w == "F" else 1]
    c = np.clip((r - r0) / BAND_AA + 0.5, 0, 1) * np.clip((r1 - r) / BAND_AA + 0.5, 0, 1)
    c = np.where(gum, c, 0.0)
    got, (c,) = dilate_from(cov, c, rounds=8)
    return np.where(cov | got, c, 0.0), r, gum, cov, rings


def tyre_diffuse(d_srgb, c, colour, mats):
    """The tyre's diffuse with the band: the band colour at the rubber's own shade (its luminance over the tyre
    colour), blended by the coverage."""
    L = LP.lin(d_srgb.astype(np.float64) / 255.0)
    tl = LP.lum(LP.hexlin(mats["surface_types"]["tyre"]["colour"]))
    shade = np.clip(LP.lum(L) / tl, 0.55, 1.15)
    band = LP.hexlin(colour)[None, None, :] * (0.25 + 0.75 * shade)[..., None]
    out = L * (1 - c[..., None]) + band * c[..., None]
    return LP.to_u8(out)


# --- the materials files -----------------------------------------------------------------------------------------

def finish_keys(opts, cast):
    keys = [f["key"] for f in opts["rim_finishes"] if not (cast and f["palette"] is None)]
    return keys + ["bodyhue"]


def rim_material(opts, base, f, diffuse, normal=None, smoothspec=None):
    """A rim's materials file for finish f on a template (2026-11-07a's wheel?_rim(_worn).bgsm): its diffuse (an index
    map, or chrome's own), the finish's palette and row, cube, env scale, smoothness and specular."""
    m = dict(base)
    m["textures"] = dict(base["textures"])
    fin = next(x for x in opts["rim_finishes"] if x["key"] == ("body" if f == "bodyhue" else f))
    pal, v = finish_v(opts, f)
    m["textures"]["diffuse"] = diffuse
    if normal:
        m["textures"]["normal"] = normal
        m["textures"]["smoothspec"] = smoothspec
    m["textures"]["envmap"] = CUBES[fin["cube"]]
    m["textures"]["greyscale"] = pal or ""
    m["grayscale_to_palette_color"] = bool(pal)
    m["grayscale_to_palette_scale"] = float(v) if pal else 1.0
    m["environment_mapping"] = True
    m["env_map_mask_scale"] = float(fin["env_scale"])
    m["smoothness"] = float(fin["smoothness"])
    m["specular_mult"] = float(fin["spec_mult"])
    return m


def material_plan(opts):
    """{file name: (template label, worn, kind, finish or band)} of every materials file written here."""
    out = {}
    for w in "FR":
        for f in finish_keys(opts, False):
            for worn in ("", "_worn"):
                out[f"rim{w}_{f}{worn}.bgsm"] = (f"wheel{w}_rim", worn, "rim", f)
        for f in finish_keys(opts, True):
            for worn in ("", "_worn"):
                out[f"cast{w}_{f}{worn}.bgsm"] = (f"wheel{w}_rim", worn, "cast", f)
        for band, suf in opts["tyre_bands"]["files"].items():
            for worn in ("", "_worn"):
                out[f"wheel{w}_tyre{suf}{worn}.bgsm"] = (f"wheel{w}_tyre", worn, "tyre", suf)
    for label in ("static_paint", "fork_paint"):
        for worn in ("", "_worn"):
            out[f"{label}_hue{worn}.bgsm"] = (label, worn, "hue", None)
    return out


def make_material(opts, bm, name, spec):
    label, worn, kind, f = spec
    if kind == "hue":
        m = B.read(bm / f"{label}_rf00{worn}.bgsm")
        m["textures"]["greyscale"] = opts["hue_palette"]["texture"]
        m["grayscale_to_palette_color"] = True
        m["grayscale_to_palette_scale"] = hue_v(*opts["hue_palette"]["default"])
        return m
    base = B.read(bm / f"{label}{worn}.bgsm")
    if kind == "tyre":
        m = dict(base)
        m["textures"] = dict(base["textures"])
        m["textures"]["diffuse"] = TEX + f"{label}{f}_d.dds"
        return m
    w = label[5]
    if kind == "cast":
        return rim_material(opts, base, f, TEX + f"cast{w}_i_d.dds")
    return rim_material(opts, base, f, TEX + ("rims_chrome_d.dds" if f == "chrome" else "rims_d.dds"), TEX + "rims_n.dds",
                        TEX + "rims_s.dds")


# --- build -------------------------------------------------------------------------------------------------------

def shipped_d(bt, label):
    _, faces = W.read_dds(bt / f"{label}_d.dds")
    return faces[0][0][..., :3]


def build(args, opts, mats, man):
    mdir = args.data / "Materials" / "CMB" / "Bike"
    tdir = args.data / "Textures" / "CMB" / "Bike"
    bm = args.base / "Materials" / "CMB" / "Bike"
    bt = args.base / "Textures" / "CMB" / "Bike"
    mdir.mkdir(parents=True, exist_ok=True)
    tdir.mkdir(parents=True, exist_ok=True)
    seg = seg_rim(opts)
    written = []
    if args.standin:
        write_standin(opts, args.stage, args.standin)
    rim_stage = args.standin or args.rim_stage or args.stage
    # (a) the rim atlas
    g, part, chrome_rgba, normal_rgba, spec_rgba, report, cov = rim_atlas(opts, args.stage, rim_stage, man)
    data, left = LP.index_dds(g, part, seg)
    (tdir / "rims_d.dds").write_bytes(data)
    (tdir / "rims_chrome_d.dds").write_bytes(W.build([chrome_rgba], "bc1", gamma_mips=True))
    (tdir / "rims_n.dds").write_bytes(W.build([normal_rgba], "bc5", normal=True))
    (tdir / "rims_s.dds").write_bytes(W.build([spec_rgba], "bc5"))
    written += ["rims_d.dds", "rims_chrome_d.dds", "rims_n.dds", "rims_s.dds"]
    for rp in report:
        print(f"  {rp['label']}: {rp['tris']} tris, {rp['texels']} texels at {RIMS_D} ({rp['units_per_texel']} units a texel), "
              f"parts {rp['parts']}, feature edges {rp['feature_edges']}, rivets {rp['rivets']}"
              + (f", {rp['outside_cell']} triangles outside its cell" if rp["outside_cell"] else ""))
    print(f"rims_d.dds: {RIMS_D}, {int(cov.sum())} texels (body {int(((part == 0) & cov).sum())}, steel/rust "
          f"{int(((part == 1) & cov).sum())}, trims {int(((part == 2) & cov).sum())}), {len(left)} mips per part, texels "
          f"decoding outside their part's segment {sum(left)} (from {rim_stage})")
    # (b) the rim palette
    (tdir / "rim_p.dds").write_bytes(W.build([rim_palette_image(opts)], "rgba8", mips=1))
    written.append("rim_p.dds")
    # (c) the cast rims' index maps
    for w in "FR":
        label = f"wheel{w}_rim"
        surf, cv = cast_surfaces(args.stage, label, man, mats)
        d = shipped_d(bt, label)
        gi, pi = cast_index(d, surf, cv, opts, mats)
        data, left = LP.index_dds(gi, pi, seg)
        (tdir / f"cast{w}_i_d.dds").write_bytes(data)
        written.append(f"cast{w}_i_d.dds")
        print(f"cast{w}_i_d.dds: {gi.shape[1]}x{gi.shape[0]}, covered {int(cv.sum())} (finish {int(((pi == 0) & cv).sum())}, "
              f"trims {int(((pi == 2) & cv).sum())}), {len(left)} mips per part, astray {sum(left)}")
    # (d) the paint palettes
    (tdir / "paint_p.dds").write_bytes(W.build([LP.palette_image(opts, LP.segments(opts))], "rgba8", mips=1))
    (tdir / "paint_hue_p.dds").write_bytes(W.build([hue_palette_image(opts)], "rgba8", mips=1))
    written += ["paint_p.dds (row 43)", "paint_hue_p.dds"]
    # (e) the tyres
    for w in "FR":
        label = f"wheel{w}_tyre"
        d = shipped_d(bt, label)
        for band, suf in opts["tyre_bands"]["files"].items():
            c, r, gum, cov, rings = tyre_band(args.stage, label, man, mats, opts, w, band)
            col = opts["tyre_bands"]["white" if band == "whitewall" else "red"]
            img = tyre_diffuse(d, c, col, mats)
            (tdir / f"{label}{suf}_d.dds").write_bytes(W.build([np.dstack([img, np.full(img.shape[:2], 255, np.uint8)])],
                                                                "bc1", gamma_mips=True))
            written.append(f"{label}{suf}_d.dds")
            print(f"{label}{suf}_d.dds: {band} on {int((c > 0.5).sum())} texels (rubber {int(gum.sum())}); sidewall rings "
                  + ", ".join(f"{x['tris']} tris r {x['r'][0]}-{x['r'][1]} fit {x['rms']}{'' if x['used'] else ' (not used)'}" for x in rings))
    # (f) the materials files
    plan = material_plan(opts)
    for name, spec in sorted(plan.items()):
        B.write(mdir / name, make_material(opts, bm, name, spec))
    written.append(f"{len(plan)} materials files")
    print("wrote " + ", ".join(written))
    return 0


# --- check -------------------------------------------------------------------------------------------------------

def same_value(a, b):
    """Equal, floats to float32's precision (a materials file stores 32-bit floats)."""
    if isinstance(b, float) or isinstance(a, float):
        return a is not None and abs(float(a) - float(b)) <= 1e-6 * max(1.0, abs(float(b)))
    if isinstance(b, (list, tuple)):
        return isinstance(a, (list, tuple)) and len(a) == len(b) and all(same_value(x, y) for x, y in zip(a, b))
    return a == b


def psnr(a, b, mask=None):
    e = (a - b) ** 2
    e = e[mask] if mask is not None else e
    mse = float(e.mean()) if e.size else 0.0
    return 10 * np.log10(1.0 / max(mse, 1e-12))


def check(args, opts, mats, man):
    ok = True

    def rep(good, what, detail=""):
        nonlocal ok
        ok &= bool(good)
        print(f"{'PASS' if good else 'FAIL'}  {what}{': ' + detail if detail else ''}")

    mdir = args.data / "Materials" / "CMB" / "Bike"
    tdir = args.data / "Textures" / "CMB" / "Bike"
    bm = args.base / "Materials" / "CMB" / "Bike"
    bt = args.base / "Textures" / "CMB" / "Bike"
    seg = seg_rim(opts)

    def dds(name):
        p = tdir / name
        if not p.exists():
            return None, []
        info, faces = W.read_dds(p)
        return info, faces[0]

    # formats, sizes, mips
    want = {"rims_d.dds": ("bc1", RIMS_D, RIMS_D, 0), "rims_chrome_d.dds": ("bc1", RIMS_CHROME, RIMS_CHROME, 0),
            "rims_n.dds": ("bc5", RIMS_N, RIMS_N, 0), "rims_s.dds": ("bc5", RIMS_S, RIMS_S, 0),
            "rim_p.dds": ("rgba8", 256, FINISH_ROWS, 1), "paint_hue_p.dds": ("rgba8", 256, 1024, 1),
            "paint_p.dds": ("rgba8", 256, 64, 1)}
    for w in "FR":
        want[f"cast{w}_i_d.dds"] = ("bc1", 1024, 1024, 0)
        for suf in opts["tyre_bands"]["files"].values():
            want[f"wheel{w}_tyre{suf}_d.dds"] = ("bc1", 1024, 1024, 0)
    bad, levels = [], {}
    for name, (fmt, w_, h_, mips) in want.items():
        info, lv = dds(name)
        full = 1 + int(math.log2(max(w_, h_)))
        if info is None:
            bad.append(f"{name} missing")
            continue
        levels[name] = lv
        if info["format"] != fmt or (info["w"], info["h"]) != (w_, h_) or len(lv) != (mips or full):
            bad.append(f"{name}: {info['format']} {info['w']}x{info['h']} {len(lv)} mips (want {fmt} {w_}x{h_} "
                       f"{mips or full})")
    rep(not bad, f"the {len(want)} textures: formats, sizes and mips (the palettes one mip, the rest full chains)", "; ".join(bad))
    # nothing under the output's Textures but ours
    other = [str(p.relative_to(args.data)) for p in (args.data / "Textures").rglob("*")
             if p.is_file() and not str(p.relative_to(args.data / "Textures")).lower().startswith("cmb")]
    rep(not other, "nothing under the output's Textures but Textures\\CMB (no game texture copied)", ", ".join(other[:5]))
    # 2026-11-07a's own files unchanged (the stock look), paint_p's rows 0-42 too
    same, n = [], 0
    fams = ("wheel", "static_paint", "fork_paint", "paint_p")
    for d0, d1 in ((bm, mdir), (bt, tdir)):
        for f in sorted(d0.iterdir()):
            if f.name.startswith(fams) and f.name != "paint_p.dds":
                n += 1
                if not (d1 / f.name).exists() or (d1 / f.name).read_bytes() != f.read_bytes():
                    same.append(f.name)
    rep(not same and n, f"2026-11-07a's own wheel and paint files ({n}: materials files and textures, paint_p.dds aside) "
                        f"byte for byte: the stock look", ", ".join(same[:8]))
    old = W.read_dds(bt / "paint_p.dds")[1][0][0]
    new = levels.get("paint_p.dds", [np.zeros_like(old)])[0]
    rows = len(LP.rows_of(opts))
    rep(np.array_equal(old[:43], new[:43]) and np.array_equal(new, LP.palette_image(opts, LP.segments(opts))),
        f"paint_p.dds rows 0-42 2026-11-07a's byte for byte, row 43 Factory, the spare rows {rows}-63 row 43's "
        f"(look_paint.py's palette_image)")
    rep("rim_p.dds" in levels and np.array_equal(levels["rim_p.dds"][0], rim_palette_image(opts)),
        "rim_p.dds: rows 0-3 the rim_palette's finishes (4-7 row 3's), U 0-47 rust to steel, 56-127 the finish, 216-255 the trims")
    hp = hue_palette_image(opts)
    rep("paint_hue_p.dds" in levels and np.array_equal(levels["paint_hue_p.dds"][0], hp),
        "paint_hue_p.dds: 4 shades x 256 hue rows, A = B the hue, the coachline cream")
    # the hue rows' neighbours never bleed: one mip, V at a row's centre, adjacent rows distinct
    rr = hp[:, 100, :3].astype(int)
    steps = np.abs(np.diff(rr, axis=0)).max(1)
    d_def = hue_v(*opts["hue_palette"]["default"]) * 1024 - 0.5
    rep(len(levels.get("paint_hue_p.dds", [])) == 1 and abs(d_def - round(d_def)) < 1e-9 and (steps[np.arange(1023) % 256 != 255] <= 12).all(),
        f"the hue palette: one mip, the default's V ({hue_v(*opts['hue_palette']['default']):.6f}) a row's centre, neighbour rows "
        f"a hue step apart (largest {int(steps[np.arange(1023) % 256 != 255].max())}/255)")
    # the index maps: per-part mips, and the palette proof through BC1
    pal_rim = rim_palette_image(opts)[..., :3].astype(np.float64) / 255.0
    pal_paint = LP.palette_image(opts, LP.segments(opts))[..., :3].astype(np.float64) / 255.0
    rim_stage = args.standin or args.rim_stage or args.stage
    maps = {}
    if "rims_d.dds" in levels:
        g, part, *_, cov = rim_atlas(opts, args.stage, rim_stage, man)
        maps["rims_d.dds"] = (g, part, cov)
    for w in "FR":
        if f"cast{w}_i_d.dds" in levels:
            surf, cv = cast_surfaces(args.stage, f"wheel{w}_rim", man, mats)
            gi, pi = cast_index(shipped_d(bt, f"wheel{w}_rim"), surf, cv, opts, mats)
            maps[f"cast{w}_i_d.dds"] = (gi, pi, cv)
    for name, (g, part, cov) in maps.items():
        lv = levels[name]
        has = np.stack([part == p for p in range(3)])
        pt = cov.copy()
        astray = []
        for k, L_ in enumerate(lv):
            if k:
                has, pt = LP.any2(has), LP.any2(pt)
            n = 0
            for c in (0, 1):
                s_ = LP.seg_of(L_[..., c], seg)
                own = np.zeros(pt.shape, bool)
                for p in range(3):
                    own |= (s_ == p) & has[p]
                n = max(n, int((pt & ~own).sum()))
            astray.append(n)
        rep(max(astray) == 0, f"{name}, all {len(lv)} mips: no covered texel's U (R or G) in a segment none of its level-0 "
                              f"footprint's parts has (mips per part)", "texels per mip " + ", ".join(map(str, astray)))
        dec = lv[0][..., 1].astype(np.int64)
        lines, good = [], True
        rows_ = [(r["key"], pal_rim[r["row"]]) for r in opts["rim_palette"]["rows"]] + [("body (Factory)", pal_paint[43])]
        for key, row in rows_:
            db = psnr(row[dec], row[g.astype(np.int64)], cov)
            good &= db >= PROOF_DB
            lines.append(f"{key} {db:.1f}")
        rep(good, f"{name}: every finish's colour through the BC1 index (level 0, G as U) against the index as made, "
                  f"{PROOF_DB:g} dB or more over the {int(cov.sum())} covered texels", "dB " + ", ".join(lines))
    # the cast maps give 2026-11-07a's own rims back
    for w in "FR":
        name = f"cast{w}_i_d.dds"
        if name not in levels:
            continue
        st = mats["surface_types"]
        own = LP.to_u8(rim_row(seg, st["rim"]["colour"], opts["rim_palette"]["trim_colour"])).astype(np.float64) / 255.0
        d = shipped_d(bt, f"wheel{w}_rim").astype(np.float64) / 255.0
        cv = maps[name][2]
        dbs = [psnr(own[levels[name][0][..., c].astype(np.int64)], d, cv) for c in (0, 1)]
        rep(min(dbs) >= PROOF_DB, f"palette proof, {name}: 2026-11-07a's rim colour and the trim ramp through it (BC1, "
                                  f"level 0) give wheel{w}_rim_d.dds back at {PROOF_DB:g} dB or more over the "
                                  f"{int(cv.sum())} covered texels", f"R as U {dbs[0]:.1f} dB, G as U {dbs[1]:.1f} dB")
    # the tyres: the band where the table says, on the rubber only, both sidewalls
    for w in "FR":
        label = f"wheel{w}_tyre"
        d0 = shipped_d(bt, label).astype(np.int64)
        for band, suf in opts["tyre_bands"]["files"].items():
            name = f"{label}{suf}_d.dds"
            if name not in levels:
                continue
            c, r, gum, cov, rings = tyre_band(args.stage, label, man, mats, opts, w, band)
            d1 = levels[name][0][..., :3].astype(np.int64)
            changed = np.abs(d1 - d0).max(-1) > 24
            r0, r1 = opts["tyre_bands"][band][0 if w == "F" else 1]
            core = changed & (c > 0.99) & gum
            off = changed & cov & ~gum
            with np.load(args.stage / "tex_cache" / label / "bake.npz") as z:
                tid, bary = z["tid"].astype(np.int64), z["bary"].astype(np.float64)
            with np.load(args.stage / "shapes" / f"{label}.npz") as z:
                pos, tri = z["pos"], z["tri"]
            A = axles(args.stage)[w]
            x = (pos[tri[np.clip(tid, 0, None)]].mean(-2)[..., 0] - A[0])
            sides = [int((core & (x < 0)).sum()), int((core & (x > 0)).sum())]
            lo, hi = (float(r[core].min()), float(r[core].max())) if core.any() else (0.0, 0.0)
            good = (core.any() and abs(lo - r0) <= BAND_TOL + BAND_AA and abs(hi - r1) <= BAND_TOL + BAND_AA
                    and not off.any() and min(sides) > 1000)
            rep(good, f"{name}: the {band} band's texels at r {lo:.2f}..{hi:.2f} (the table's {r0}..{r1}, within "
                      f"{BAND_TOL} past the {BAND_AA} edge), on both sidewalls ({sides[0]}, {sides[1]} texels), none off the rubber",
                f"{int(off.sum())} off the rubber" if off.any() else "")
    # every materials file read back
    plan = material_plan(opts)
    bad = []
    for name, spec in sorted(plan.items()):
        p = mdir / name
        if not p.exists():
            bad.append(f"{name} missing")
            continue
        m, want_m = B.read(p), make_material(opts, bm, name, spec)
        diff = [k for k in want_m if not k.startswith("_") and not same_value(m.get(k), want_m[k])]
        if diff:
            bad.append(f"{name}: {', '.join(diff)}")
        label, worn, kind, f = spec
        if kind in ("rim", "cast"):
            pal, v = finish_v(opts, f)
            if pal:
                rows = 1024 if "hue" in pal else (64 if "paint_p" in pal else FINISH_ROWS)
                x = m["grayscale_to_palette_scale"] * rows - 0.5
                if abs(x - round(x)) > 1e-4 or not m["grayscale_to_palette_color"]:
                    bad.append(f"{name}: V {m['grayscale_to_palette_scale']} not a row's centre of {pal}")
            elif m["grayscale_to_palette_color"]:
                bad.append(f"{name}: chrome with a palette")
            base = B.read(bm / f"{label}{worn}.bgsm")
            if m["cast_shadows"] != base["cast_shadows"] or m["two_sided"] != base["two_sided"]:
                bad.append(f"{name}: shadows/two-sided not {label}{worn}'s")
    rep(not bad and len(plan) == 64, f"the {len(plan)} materials files read back: textures, palette and row centre, cube, "
                                     f"env scale, smoothness, specular per finish; templates' shadows", "; ".join(bad[:8]))
    # our MSWP targets all here
    names = {p.name.lower() for p in mdir.glob("*.bgsm")}
    missing = set()
    for s in opts["slots"]:
        if s["key"] not in ("Rims", "Tyres", "Paint"):
            continue
        for o in s["options"]:
            for _, tgt in o["swap"] or []:
                leaf = tgt.split("\\")[-1]
                mine = leaf.startswith(("rim", "cast")) or "_hue" in leaf or "_tyre_" in leaf
                if mine and leaf.lower() not in names:
                    missing.add(leaf)
    for a, b in opts["rim_body_targets"]:
        if b.split("\\")[-1].lower() not in names:
            missing.add(b.split("\\")[-1])
    rep(not missing, "every Rims, Tyres and Free colour MSWP target of ours (and the 8 bodyhue twins) here",
        ", ".join(sorted(missing)[:10]))
    print("look_wheels: all checks passed" if ok else "look_wheels: FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, required=True, help="the Data tree to write (Materials, Textures)")
    ap.add_argument("--base", type=Path, required=True, help="2026-11-07a's Data tree (read only)")
    ap.add_argument("--stage", type=Path, required=True, help="the stage folder (manifest, shapes, tex_cache)")
    ap.add_argument("--rim-stage", type=Path, help="where the rim-style shapes are (shapes/, uv/; default --stage)")
    ap.add_argument("--standin", type=Path, help="write stand-in rim shapes here and use them")
    ap.add_argument("--options", type=Path, default=HERE.parent / "esp-generator" / "look_options.json")
    ap.add_argument("--materials", type=Path, default=HERE / "bike_materials.json")
    ap.add_argument("--check", action="store_true", help="check a built tree (and nothing written)")
    args = ap.parse_args()
    opts = json.loads(args.options.read_text())
    mats = json.loads(args.materials.read_text())
    man = json.loads((args.stage / "manifest.json").read_text())
    if args.data.resolve() == args.base.resolve():
        ap.error("--data and --base must differ (the base is read only)")
    if args.check and args.standin and not (args.standin / "shapes").exists():
        ap.error("--standin: no stand-in shapes there to check against")
    if args.check:
        return check(args, opts, mats, man)
    return build(args, opts, mats, man)


if __name__ == "__main__":
    sys.exit(main())
