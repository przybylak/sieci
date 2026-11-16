#!/usr/bin/env python3
"""The seat's colour (build 2026-11-16a, C3 item 3.4): the shipped seat re-sampled into a palette index map, the seat
palette and a materials file pair per colour. No bake: everything comes from the shipped files and the parked nif.

What it writes into --data (Textures\\CMB\\Bike, Materials\\CMB\\Bike; every name from look_options.json's
seat_palette and Seat slot):

  static_seat_i_d.dds  1024 BC1, the index map: the shipped static_seat_d.dds re-sampled per texel. A texel's grey is
                       a U of the palette; its level is the texel's shade, its luminance over the stock leather's
                       (seat_palette.leather) in the shipped diffuse. Three parts, each in its own U band
                       (seat_palette.u): the body (the seat piece's leather) U 56-127, the piping (the parked nif's
                       576-triangle piece, the welt, rasterised in UV: its texels exactly) U 136-207, and the wear
                       patches U 0-47 (the body's texels the shipped bake wore: its _s smoothness, green, is the
                       leather's 0.4 blended toward the wear's 0.5, bike_materials.json's surface_types.leather; a
                       blend of WEAR_FROM or more is a wear texel). The bands run as a V: the wear's shade rises to
                       U 47, the body's falls from U 56 (its brightest) to 127, the piping's rises from 136, so each
                       guard joins like tones (the wear's and the body's light ends, the body's and the piping's dark
                       ends) and a texture sample across a part's border passes through like shades, not through black.
                       The shade is denoised first (--denoise 1, the default): the shipped diffuse is BC1 at about
                       sRGB 35, so its shading steps in 7-15 % jumps that a light colour (Cream) would
                       show as contour lines; an edge-keeping (bilateral) filter within each part, DENOISE = (4 texels,
                       0.15 in log shade), turns the steps back into the bake's smooth mottling and keeps the
                       creases' occlusion. --denoise 0: the per-texel re-sample as it is. The texels no triangle
                       covers take their nearest covered texel's part and level (ring by ring). The mips are made per
                       part (look_paint.py's index_levels' rule, weighted, and its index_bc1, imported: an index can't
                       be averaged): a mip texel is the piping from a quarter of its level-0 footprint's seat texels
                       (so the welt stays at mips 1-3; the gutter's dilated texels weigh GUTTER, so the welt's gutter
                       never takes a mip texel over body texels), else the majority of the body and the wear, at that
                       part's mean U; BC1 blocks that would decode a texel into a band not its part's are re-encoded
                       inside their parts' bands.
  seat_p.dds           256 x 16 A8R8G8B8, one mip (a lookup must not blur rows): row r = seat_palette.rows[r] (rows
                       0-13 the options' colours, 14 the stock leather, the proof's only), row 15 spare (row 14's).
                       Each band is its colour times the shade ramp (SHADE, the body and piping; WEAR_SHADE, the wear);
                       the guards blend their neighbours; U 208-255 the piping's top. The body band is `body`, the
                       piping's `piping`; a contrasting welt (a row whose piping isn't its body) is lifted PIPE_GAIN
                       (2: the welt sits in the bake's shadow, median shade 0.50 against the body's 0.93), so it shows
                       its swatch's lightness; a self-coloured welt, the stock row's too, keeps the bake's shadow.
                       The wear band is the row's worn tone: worn_tone() adds to the body colour
                       the step the stock wear patch (seat_palette.wear_patch) takes from the stock leather in OKLab
                       (lighter and a little warmer: the crust under the finish), scaled by the colour's lightness
                       headroom ((1 - L) over the leather's), the chroma pulled in if it leaves sRGB; so the stock
                       leather's worn tone is the stock wear patch, a dark colour's patches are lighter and a light
                       colour's barely change. The band shows WEAR_MIX of the worn tone over the body (the wear
                       texels' mean blend in the shipped bake), normalised as the stock's to the leather's luminance,
                       so a shade reads alike in the wear and body bands.
  materials            static_seat_<key>.bgsm and static_seat_<key>_worn.bgsm for the 14 keys of the Seat slot's
                       palette options: the shipped static_seat.bgsm / static_seat_worn.bgsm with the diffuse the index
                       map, the greyscale slot seat_p.dds, grayscale_to_palette_color on and grayscale_to_palette_scale
                       V = (row + 0.5) / 16 (the option's cnam), _n and _s the shipped ones: 28 files. A seat darker
                       than the stock leather (Black and its two piped versions) has DARK_SPEC (0.5) of the shipped
                       specular_mult: the shipped sheen would otherwise lift it to the stock seat's look. Option 0, "as it
                       came", is no row: the identity swap, the shipped files (this tool never writes them).

--check (after a build, or alone on a built tree) checks the formats, sizes and mips; seat_p.dds the table's rows; the
28 materials files; the proof: the stock row (14) through the index map as written (BC1 decoded, R or G as U, level 0)
gives the shipped diffuse back at PROOF_DB or better over the seat's texels (and per part); the index map's mips per
part (no texel's U in a band none of its level-0 footprint's parts has, at any mip); the piping mask: the level-0
texels in the piping band are the piping piece's UV texels exactly, and at mips 1-3 its area is at least PIPE_KEEP of
level 0's; every row's colours: per part, the mean OKLab lightness, chroma and hue of the seat as written (index map,
palette file, the material's V) against the row's colour at the shipped seat's own shading, and the texels at their
own shade against the row's colour itself; every two options apart as the shader colours the seat (DE_MIN in OKLab
between the seats' area-weighted means in linear light, before lighting, option 0 the shipped seat itself; two
options of one seat colour, a plain one and its piped version, by their welts); every contrasting welt at its
swatch's lightness (PIPE_DL) and PIPE_DE from its seat; every Seat swap's source in the base and target in --data;
the worn and view nifs' seat UVs the parked one's (one index map serves every bike); the shipped seat files not
overwritten (option 0 is the shipped seat, byte for byte).

    <python with numpy, Pillow, quicktex, texture2ddecoder> -I tools/rider/look_seat.py --data <out Data> \\
        --base <2026-11-10a's Data> [--base <2026-11-15b's Data> ...] --pynifly <io_scene_nifly> \\
        [--options look_options.json] [--materials bike_materials.json] [--denoise 1|0] [--check]

--base: the asset base, read only; later folders over earlier ones (the package's Data, then a build's meshes over it).
Fallout 4 semantics as look_paint.py's: no diffuse tint for lit materials; grayscale_to_palette_color with the greyscale
slot and grayscale_to_palette_scale (V) is the one per-material colour, F4SE's MSWP colorIndex the same V. Nothing from
the files read is executed.
"""
import argparse
import itertools
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
from look_wheels import raster  # noqa: E402

TEX = "CMB\\Bike\\"
ROWS = 16
SIZE = 1024
PIPING_TRIS, SEAT_TRIS = 576, 851      # the shipped seat's two pieces (c3.md section 2)
SHADE = (0.0, 1.5)                     # the body's and the piping's shade ramp (luminance over the stock leather)
WEAR_SHADE = (0.3, 1.5)                # the wear band's ramp (its top the body's top: the guard joins like tones)
WEAR_FROM = 0.15                       # a body texel's wear blend from the _s green at or over this: a wear texel
WEAR_MIX = 0.2                         # the wear band's share of the worn tone (the wear texels' mean blend: about 0.19)
DENOISE = (4.0, 0.15)                  # the bilateral filter: spatial sigma (texels), range sigma (log shade)
PROOF_DB = 35.0
GUTTER = 1e-3                          # the mips: an uncovered texel's weight (a covered one's 1)
PIPE_KEEP = 0.5                        # --check: the piping's area at mips 1-3 at least this share of level 0's
MEAN_DL, MEAN_DC, MEAN_DH, MEAN_DE = 0.015, 0.012, 4.0, 0.015   # --check: a part's mean against its ideal (OKLab)
HUE_MIN_C = 0.03                       # hue compared only from this chroma (a near-grey's hue is noise)
LIT = (0.95, 1.05)                     # the texels at the leather's own shade
LIT_DE = 0.02                          # their mean against the row's colour itself (OKLab distance)
PIPE_GAIN = 2.0                        # a contrasting welt's shade gain: 1 over the welt's median shade (0.502) in the
                                       # shipped bake, so the welt shows its swatch's lightness (a self-coloured welt 1)
DE_MIN = 0.08                          # --check: every two options at least this far apart (OKLab), as coloured
PIPE_DE = 0.15                         # --check: a contrasting welt at least this far from its seat (OKLab), as coloured
PIPE_DL = 0.05                         # --check: a contrasting welt's median lightness within this of its swatch's
DARK_SPEC = 0.5                        # a seat darker than the stock leather: its materials' specular_mult times this
                                       # (the shipped sheen lifts a black seat to the stock's lightness in the renders:
                                       # Black / stock 0.011 apart in OKLab at 1, 0.096 at 0.5; the grain's sheen stays)
PARTS = ("body", "wear", "piping")     # index_levels' parts 0, 1, 2 (look_paint's keys tank, fenders, coachline)
NIFS = ("CMB_BikeParked", "CMB_BikeWorn", "CMB_BikeWornRider", "CMB_BikeWornRiderF", "CMB_BikeView")


# --- colour ------------------------------------------------------------------------------------------------------

_M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566],
                [0.0883024619, 0.2817188376, 0.6299787005]])
_M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099],
                [0.0259040371, 0.7827717662, -0.8086757660]])


def oklab(lin):
    """Linear sRGB (..., 3) -> OKLab (..., 3)."""
    return np.cbrt(np.asarray(lin, np.float64) @ _M1.T) @ _M2.T


def from_oklab(lab):
    return (np.asarray(lab, np.float64) @ np.linalg.inv(_M2).T) ** 3 @ np.linalg.inv(_M1).T


def lch(lab):
    lab = np.asarray(lab, np.float64)
    return lab[..., 0], np.hypot(lab[..., 1], lab[..., 2]), np.degrees(np.arctan2(lab[..., 2], lab[..., 1])) % 360.0


def worn_tone(body, leather, wear):
    """The worn tone (linear) of a body colour (linear): the body plus the step the stock wear patch takes from the stock
    leather in OKLab (a lightening with a little warmth: the crust under the finish), the step scaled by the body's
    lightness headroom k = (1 - L_body) / (1 - L_leather); a colour outside sRGB has its chroma pulled in (same
    lightness and hue). worn_tone(leather) is the wear patch."""
    ob = oklab(body)
    lab = ob + (oklab(wear) - oklab(leather)) * (1.0 - ob[0]) / (1.0 - oklab(leather)[0])
    lab[0] = min(lab[0], 1.0)

    def inside(x):
        c = from_oklab(x)
        return bool(np.all((c >= -1e-9) & (c <= 1 + 1e-9)))
    if not inside(lab):
        lo, hi = 0.0, 1.0
        for _ in range(40):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if inside(np.array([lab[0], lab[1] * mid, lab[2] * mid])) else (lo, mid)
        lab = np.array([lab[0], lab[1] * lo, lab[2] * lo])
    return np.clip(from_oklab(lab), 0, 1)


# --- the table ---------------------------------------------------------------------------------------------------

def seat_table(opts):
    """(seat_palette, its rows by row, the Seat slot); the rows 0.. in order, at most ROWS."""
    sp = opts["seat_palette"]
    rows = sorted(sp["rows"], key=lambda r: r["row"])
    if [r["row"] for r in rows] != list(range(len(rows))) or len(rows) > ROWS or tuple(sp["size"]) != (256, ROWS):
        raise ValueError("look_options.json: seat_palette's rows aren't rows 0.. in order, or its size isn't 256 x 16")
    slot = next(s for s in opts["slots"] if s["key"] == "Seat")
    return sp, rows, slot


def segments(sp):
    """look_paint's segment keys for the seat's bands: part 0 the body (tank), 1 the wear (fenders), 2 the piping
    (coachline, the part kept thin at the mips), and a band no part uses (primer: a texel decoding there is astray)."""
    u = sp["u"]
    return {"tank": tuple(u["body"]), "fenders": tuple(u["wear"]), "coachline": tuple(u["piping"]), "primer": (216, 255)}


def stock(sp):
    """(the stock leather, its wear patch, the wear band's tone normalisation): linear colours, and the factor that
    puts the stock wear tone (WEAR_MIX of the patch over the leather) at the leather's luminance."""
    lea, wp = LP.hexlin(sp["leather"]), LP.hexlin(sp["wear_patch"])
    ref = lea * (1 - WEAR_MIX) + wp * WEAR_MIX
    return lea, wp, LP.lum(lea) / LP.lum(ref)


def pipe_gain(body, piping):
    """The welt's shade gain in a row: PIPE_GAIN for a contrasting welt (its colour not the body's), else 1 (the
    welt in the bake's shadow, as the shipped seat's: the stock row's too)."""
    return PIPE_GAIN if piping.lower() != body.lower() else 1.0


def dark_seat(sp, body):
    """True for a seat darker than the stock leather (its OKLab lightness below the leather's): its materials get
    DARK_SPEC of the shipped specular, so the sheen doesn't lift it to the stock's look."""
    return bool(oklab(LP.hexlin(body))[0] < oklab(LP.hexlin(sp["leather"]))[0])


def seat_row(seg, sp, body, piping):
    """One seat_p row (256, 3) linear: the wear band (its shade rising), the body's (falling), the piping's (rising,
    times pipe_gain), the guards blending their neighbours, past the piping its top."""
    lea, wp, norm = stock(sp)
    gain = pipe_gain(body, piping)
    b, p = LP.hexlin(body), LP.hexlin(piping)
    tone = (b * (1 - WEAR_MIX) + worn_tone(b, lea, wp) * WEAR_MIX) * norm
    row = np.zeros((256, 3))
    w0, w1 = seg["fenders"]
    b0, b1 = seg["tank"]
    p0, p1 = seg["coachline"]
    t = np.arange(w0, w1 + 1) - w0
    row[w0:w1 + 1] = tone * (WEAR_SHADE[0] + (WEAR_SHADE[1] - WEAR_SHADE[0]) * t / (w1 - w0))[:, None]
    t = np.arange(b0, b1 + 1) - b0
    row[b0:b1 + 1] = b * (SHADE[1] - (SHADE[1] - SHADE[0]) * t / (b1 - b0))[:, None]
    t = np.arange(p0, p1 + 1) - p0
    row[p0:p1 + 1] = p * gain * (SHADE[0] + (SHADE[1] - SHADE[0]) * t / (p1 - p0))[:, None]
    for g0, g1 in ((w1, b0), (b1, p0)):
        for i in range(g0 + 1, g1):
            f = (i - g0) / (g1 - g0)
            row[i] = row[g0] * (1 - f) + row[g1] * f
    row[p1 + 1:] = row[p1]
    return row


def palette_image(opts):
    sp, rows, _ = seat_table(opts)
    seg = segments(sp)
    img = np.zeros((ROWS, 256, 4), np.uint8)
    img[..., 3] = 255
    for r in rows:
        img[r["row"], :, :3] = LP.to_u8(seat_row(seg, sp, r["body"], r["piping"]))
    for i in range(len(rows), ROWS):
        img[i] = img[len(rows) - 1]
    return img


def seat_targets(opts):
    """{bgsm file name: (worn, the option)} of the Seat slot's palette options' MSWP targets (the identity's are the
    shipped files)."""
    _, _, slot = seat_table(opts)
    out = {}
    for o in slot["options"]:
        if o["kind"] != "seat":
            continue
        for src, tgt in o["swap"]:
            out[tgt.split("\\")[-1]] = (src.split("\\")[-1].lower().endswith("_worn.bgsm"), o)
    return out


# --- the inputs --------------------------------------------------------------------------------------------------

def find(bases, rel):
    """A file under the asset base (the last --base that has it), else None."""
    for b in reversed(bases):
        p = b / rel
        if p.exists():
            return p
    return None


def seat_piece(pynifly, path):
    """The seat shape of a nif: (per-corner UVs (tris, 3, 2), per triangle True for the piping, the two pieces'
    triangle counts, per triangle its surface per texel at SIZE). The pieces are the shape's position-welded
    components; the piping is the smaller."""
    sys.path.insert(0, str(pynifly))
    from pyn import pynifly as P
    f = P.NifFile(str(path))
    s = next((s for s in f.shapes if s.name.lower().endswith("_static_seat")), None)
    if s is None:
        raise ValueError(f"{path.name}: no static_seat shape")
    v = np.asarray(s.verts, np.float64)
    uv = np.asarray(s.uvs, np.float64)
    tri = np.asarray(s.tris, np.int64)
    _, inv = np.unique(np.round(v, 4), axis=0, return_inverse=True)
    inv = inv.ravel()
    par = np.arange(inv.max() + 1)

    def root(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    for a, b, c in inv[tri]:
        ra = root(a)
        par[root(b)] = ra
        par[root(c)] = ra
    comp = np.array([root(a) for a in inv[tri[:, 0]]])
    keys, counts = np.unique(comp, return_counts=True)
    pip = comp == keys[counts.argmin()]
    a3 = 0.5 * np.linalg.norm(np.cross(v[tri[:, 1]] - v[tri[:, 0]], v[tri[:, 2]] - v[tri[:, 0]]), axis=1)
    u = uv[tri] * SIZE
    e1, e2 = u[:, 1] - u[:, 0], u[:, 2] - u[:, 0]
    a2 = 0.5 * np.abs(e1[:, 0] * e2[:, 1] - e2[:, 0] * e1[:, 1])
    return uv[tri], pip, sorted(counts.tolist(), reverse=True), a3 / np.maximum(a2, 1e-12)


def shipped(bases):
    """The shipped seat's diffuse (sRGB uint8, level 0) and _s (uint8, level 0)."""
    out = []
    for n in ("static_seat_d.dds", "static_seat_s.dds"):
        p = find(bases, Path("Textures/CMB/Bike") / n)
        if p is None:
            raise SystemExit(f"--base: no Textures/CMB/Bike/{n}")
        out.append(W.read_dds(p)[1][0][0])
    return out[0][..., :3], out[1]


def wear_blend(spec, mats):
    """The shipped bake's wear blend per texel from the _s green (smoothness): the leather's smoothness blended toward
    the wear's (bike_materials.json's surface_types.leather)."""
    lt = mats["surface_types"]["leather"]
    s0, s1 = float(lt["smooth"]), float(lt["wear"]["smooth"])
    return (spec[..., 1].astype(np.float64) / 255.0 - s0) / (s1 - s0)


# --- the index map -----------------------------------------------------------------------------------------------

def bilateral(x, part, cov, ss, sr):
    """x (shade) filtered in log space with a Gaussian of ss texels and a range Gaussian of sr, over the covered texels
    of the same part only; the others as they are."""
    lx = np.log(np.maximum(x, 1e-4))
    r = int(math.ceil(2.5 * ss))
    H, Wd = x.shape
    pad = np.pad(lx, r, mode="edge")
    pp = np.pad(np.where(cov, part, -1), r, constant_values=-1)
    num, den = np.zeros_like(lx), np.zeros_like(lx)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            ws = math.exp(-(dx * dx + dy * dy) / (2 * ss * ss))
            if ws < 0.01:
                continue
            nb = pad[r + dy:r + dy + H, r + dx:r + dx + Wd]
            same = pp[r + dy:r + dy + H, r + dx:r + dx + Wd] == part
            w = ws * np.exp(-((nb - lx) ** 2) / (2 * sr * sr)) * same
            num += w * nb
            den += w
    return np.where(cov & (den > 0), np.exp(num / np.maximum(den, 1e-12)), x)


def u_of(part, s, seg):
    """The U of a shade per part (0 body falling, 1 wear rising, 2 piping rising)."""
    b0, b1 = seg["tank"]
    w0, w1 = seg["fenders"]
    p0, p1 = seg["coachline"]
    sb = np.clip(s, *SHADE)
    sw = np.clip(s, *WEAR_SHADE)
    ub = b0 + (SHADE[1] - sb) / (SHADE[1] - SHADE[0]) * (b1 - b0)
    uw = w0 + (sw - WEAR_SHADE[0]) / (WEAR_SHADE[1] - WEAR_SHADE[0]) * (w1 - w0)
    upp = p0 + (sb - SHADE[0]) / (SHADE[1] - SHADE[0]) * (p1 - p0)
    return np.choose(part, [ub, uw, upp])


def parts_of(tid, pip, blend):
    """Per texel: the part (0 body, 1 wear, 2 piping; -1 no triangle) and the covered mask."""
    cov = tid >= 0
    piping = cov & pip[np.clip(tid, 0, None)]
    part = np.full(tid.shape, -1, np.int64)
    part[cov] = 0
    part[cov & ~piping & (blend >= WEAR_FROM)] = 1
    part[piping] = 2
    return part, cov


def index_map(d_srgb, spec, uvc, pip, sp, mats, denoise=True):
    """The index map (H, W) uint8, its parts (every texel), the covered texels and a report."""
    seg = segments(sp)
    H, Wd = d_srgb.shape[:2]
    tid, _ = raster(uvc, H, Wd)
    blend = wear_blend(spec, mats)
    part, cov = parts_of(tid, pip, blend)
    shade = LP.lum(LP.lin(d_srgb.astype(np.float64) / 255.0)) / LP.lum(LP.hexlin(sp["leather"]))
    sm = bilateral(shade, part, cov, *DENOISE) if denoise else shade
    u = np.clip(np.rint(u_of(np.clip(part, 0, 2), sm, seg)), 0, 255)
    # the texels no triangle covers: their nearest covered texel's part and U
    src = LP.dilate(np.where(cov, np.arange(cov.size).reshape(cov.shape), -1), rounds=4096)
    src[src < 0] = int(np.flatnonzero(part.ravel() == 0)[0])
    full_part = part.ravel()[src]
    g = u.ravel()[src].astype(np.uint8)
    rep = dict(covered=int(cov.sum()), body=int((part == 0).sum()), wear=int((part == 1).sum()),
               piping=int((part == 2).sum()),
               wear_blend_mean=round(float(blend[part == 1].mean()), 3) if (part == 1).any() else None,
               shade=dict((PARTS[p], [round(float(x), 3) for x in np.percentile(shade[part == p], [1, 50, 99])])
                          for p in range(3) if (part == p).any()),
               denoise_rms_log=round(float(np.sqrt(np.mean(
                   np.log(np.maximum(sm, 1e-4) / np.maximum(shade, 1e-4))[cov] ** 2))), 4))
    return g, full_part, cov, part, shade, rep


def seat_levels(g, part, cov):
    """The index map's mip chain per part ([levels], [their parts]), down to 1 x 1: look_paint's index_levels with the
    covered texels weighing 1 and the others GUTTER (their parts are only the dilation's), so a mip texel over seat
    texels takes a part its seat texels have: the piping when it is COACH_COVER or more of the seat texels' weight,
    else the larger of the body and the wear (the body on a tie), at that part's weighted mean U."""
    h, w = g.shape
    wt = np.where(cov, 1.0, GUTTER)
    cov_p = [wt * (part == p) for p in range(3)]
    mean = [g.astype(np.float64) / 255.0 * (part == p) for p in range(3)]
    levels, parts = [g], [part]
    for _ in range(1, 1 + int(np.floor(np.log2(max(h, w))))):
        sums = [W.half(c * m) for c, m in zip(cov_p, mean)]
        cov_p = [W.half(c) for c in cov_p]
        mean = [np.where(c > 0, s / np.where(c > 0, c, 1.0), 0.0) for s, c in zip(sums, cov_p)]
        tot = cov_p[0] + cov_p[1] + cov_p[2]
        p = np.where(cov_p[2] >= LP.COACH_COVER * tot, 2, np.where(cov_p[1] > cov_p[0], 1, 0))
        levels.append(np.clip(np.rint(np.choose(p, mean) * 255.0), 0, 255).astype(np.uint8))
        parts.append(p)
    return levels, parts


def seat_dds(g, part, cov, seg):
    """The index map's DDS (BC1, legacy header, seat_levels' mips, each level's blocks kept in their parts' bands by
    look_paint's index_bc1) and the texels left astray per level."""
    levels, parts = seat_levels(g, part, cov)
    body, left = b"", []
    for lv, pt in zip(levels, parts):
        b, n = LP.index_bc1(lv, pt, seg)
        body += b
        left.append(n)
    return W.header("bc1", g.shape[1], g.shape[0], len(levels), False, False, False, False) + body, left


def piping_overlap(uvc, pip, H, Wd):
    """Texels the piping's and the seat piece's triangles both cover (they would be the last drawn's)."""
    a = raster(uvc[pip], H, Wd)[0] >= 0
    b = raster(uvc[~pip], H, Wd)[0] >= 0
    return int((a & b).sum())


# --- build -------------------------------------------------------------------------------------------------------

def build(args, opts, mats):
    sp, rows, slot = seat_table(opts)
    body_of = {r["key"]: r["body"] for r in rows}
    seg = segments(sp)
    mdir = args.data / "Materials" / "CMB" / "Bike"
    tdir = args.data / "Textures" / "CMB" / "Bike"
    mdir.mkdir(parents=True, exist_ok=True)
    tdir.mkdir(parents=True, exist_ok=True)
    d, spec = shipped(args.base)
    nif = find(args.base, Path("Meshes/CMB/CMB_BikeParked.nif"))
    uvc, pip, counts, _ = seat_piece(args.pynifly, nif)
    if counts != [SEAT_TRIS, PIPING_TRIS]:
        print(f"WARNING: the parked nif's seat pieces have {counts} triangles, not [{SEAT_TRIS}, {PIPING_TRIS}]: the "
              f"smaller is taken as the piping")
    g, part, cov, part0, shade, rep = index_map(d, spec, uvc, pip, sp, mats, bool(args.denoise))
    data, left = seat_dds(g, part, cov, seg)
    name_i = sp["index_map"].split("\\")[-1]
    name_p = sp["texture"].split("\\")[-1]
    (tdir / name_i).write_bytes(data)
    print(f"{name_i}: {g.shape[1]}x{g.shape[0]} BC1, seat texels {rep['covered']} (body {rep['body']}, wear {rep['wear']}, "
          f"piping {rep['piping']}), {len(left)} mips per part, texels decoding outside their part's band {sum(left)}; "
          f"shade p1/p50/p99 {rep['shade']}; the wear texels' mean blend {rep['wear_blend_mean']} (WEAR_MIX {WEAR_MIX}); "
          f"denoise {'on' if args.denoise else 'off'} (rms change {rep['denoise_rms_log']} in log shade)")
    (tdir / name_p).write_bytes(W.build([palette_image(opts)], "rgba8", mips=1))
    lea, wp, _ = stock(sp)
    print(f"{name_p}: 256 x {ROWS} A8R8G8B8, one mip, rows 0-{len(rows) - 1} the table's, {ROWS - len(rows)} spare")
    for r in rows:
        wt = worn_tone(LP.hexlin(r["body"]), lea, wp)
        print(f"  row {r['row']:2d} {r['key']:<14} body {r['body']} piping {r['piping']} worn tone "
              f"{''.join(f'{x:02x}' for x in LP.to_u8(wt))} welt gain {pipe_gain(r['body'], r['piping']):g}")
    base_m = {False: B.read(find(args.base, Path("Materials/CMB/Bike/static_seat.bgsm"))),
              True: B.read(find(args.base, Path("Materials/CMB/Bike/static_seat_worn.bgsm")))}
    n = 0
    for name, (worn, o) in sorted(seat_targets(opts).items()):
        m = dict(base_m[worn])
        m["textures"] = dict(base_m[worn]["textures"])
        m["textures"]["diffuse"] = sp["index_map"]
        m["textures"]["greyscale"] = sp["texture"]
        m["textures"]["normal"] = sp["normal"]
        m["textures"]["smoothspec"] = sp["smoothspec"]
        m["grayscale_to_palette_color"] = True
        m["grayscale_to_palette_scale"] = (int(o["row"]) + 0.5) / ROWS
        if dark_seat(sp, body_of[o["key"]]):
            m["specular_mult"] = base_m[worn]["specular_mult"] * DARK_SPEC
        B.write(mdir / name, m)
        n += 1
    print(f"wrote {name_i}, {name_p} and {n} materials files into {args.data}")
    return 0


# --- check -------------------------------------------------------------------------------------------------------

def check(args, opts, mats):
    ok = True

    def rep(good, what, detail=""):
        nonlocal ok
        ok &= bool(good)
        print(f"{'PASS' if good else 'FAIL'}  {what}{': ' + detail if detail else ''}")

    sp, rows, slot = seat_table(opts)
    body_of = {r["key"]: r["body"] for r in rows}
    seg = segments(sp)
    mdir = args.data / "Materials" / "CMB" / "Bike"
    tdir = args.data / "Textures" / "CMB" / "Bike"
    name_i = sp["index_map"].split("\\")[-1]
    name_p = sp["texture"].split("\\")[-1]
    # the textures' formats
    pi, pp = tdir / name_i, tdir / name_p
    if not (pi.exists() and pp.exists()):
        rep(False, f"{name_i} and {name_p} in {tdir}")
        print("look_seat: FAILED")
        return 1
    ii, fi = W.read_dds(pi)
    ip, fp = W.read_dds(pp)
    levels = fi[0]
    rep(ii["format"] == "bc1" and (ii["w"], ii["h"]) == (SIZE, SIZE) and len(levels) == 11,
        f"{name_i}: BC1 {SIZE} x {SIZE}, every mip", f"{ii['format']} {ii['w']}x{ii['h']}, {len(levels)} mips")
    raw = pp.read_bytes()
    masks = tuple(int.from_bytes(raw[o:o + 4], "little") for o in (92, 96, 100, 104))
    rep(ip["format"] == "rgba8" and (ip["w"], ip["h"]) == (256, ROWS) and len(fp[0]) == 1 and len(raw) == 128 + 256 * ROWS * 4
        and masks == (0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000),
        f"{name_p}: A8R8G8B8 256 x {ROWS}, one mip (a lookup must not blur rows)",
        f"{ip['format']} {ip['w']}x{ip['h']}, {len(fp[0])} mips, {len(raw)} bytes, masks {[hex(m) for m in masks]}")
    pal = fp[0][0]
    want = palette_image(opts)
    rep(np.array_equal(pal, want), f"{name_p}: rows 0-{len(rows) - 1} the table's seat_palette rows (worn tone, body, "
                                   f"piping bands), row {ROWS - 1} spare (row {len(rows) - 1}'s)")
    # the 28 materials files
    targets = seat_targets(opts)
    bad, n_dark = [], 0
    base_m = {False: B.read(find(args.base, Path("Materials/CMB/Bike/static_seat.bgsm"))),
              True: B.read(find(args.base, Path("Materials/CMB/Bike/static_seat_worn.bgsm")))}
    for name, (worn, o) in sorted(targets.items()):
        p = mdir / name
        if not p.exists():
            bad.append(f"{name} missing")
            continue
        m, base = B.read(p), base_m[worn]
        v = (int(o["row"]) + 0.5) / ROWS
        if (abs(m["grayscale_to_palette_scale"] - v) > 1e-7 or abs(v - float(o["cnam"])) > 1e-7
                or not m["grayscale_to_palette_color"]):
            bad.append(f"{name}: V {m['grayscale_to_palette_scale']} for row {o['row']} (cnam {o['cnam']})")
        tx = m["textures"]
        names = (sp["index_map"], sp["texture"], sp["normal"], sp["smoothspec"])
        if (tx["diffuse"], tx["greyscale"], tx["normal"], tx["smoothspec"]) != names:
            bad.append(f"{name}: textures {tx['diffuse']}, {tx['greyscale']}, {tx['normal']}, {tx['smoothspec']}")
        if (base["textures"]["normal"], base["textures"]["smoothspec"]) != (sp["normal"], sp["smoothspec"]):
            bad.append(f"the shipped static_seat{'_worn' if worn else ''}.bgsm names other _n/_s than the table's")
        dark = dark_seat(sp, body_of[o["key"]])
        if dark:
            n_dark += 1
            if abs(m["specular_mult"] - base["specular_mult"] * DARK_SPEC) > 1e-6:
                bad.append(f"{name}: specular_mult {m['specular_mult']}, a dark seat's {base['specular_mult'] * DARK_SPEC}")
        for k in base:
            if k.startswith("_") or k in ("textures", "grayscale_to_palette_color", "grayscale_to_palette_scale"):
                continue
            if k == "specular_mult" and dark:
                continue
            if base[k] != m[k]:
                bad.append(f"{name}: {k} {m[k]!r}, the shipped {base[k]!r}")
        for k, t in base["textures"].items():
            if k not in ("diffuse", "greyscale") and t != tx[k]:
                bad.append(f"{name}: texture {k} {tx[k]!r}")
    rep(not bad and len(targets) == 28, f"the {len(targets)} materials files: the shipped static_seat(_worn).bgsm's values, "
                                        f"diffuse {name_i}, greyscale {name_p}, grayscale_to_palette_color on, "
                                        f"grayscale_to_palette_scale the option's cnam (row + 0.5) / {ROWS}; the "
                                        f"{n_dark} files of the seats darker than the stock leather with specular_mult x {DARK_SPEC:g}",
        "; ".join(bad[:8]))
    # the shipped seat and the parked nif's pieces
    d, spec = shipped(args.base)
    nif = find(args.base, Path("Meshes/CMB/CMB_BikeParked.nif"))
    uvc, pip, counts, dens = seat_piece(args.pynifly, nif)
    rep(counts == [SEAT_TRIS, PIPING_TRIS], f"the parked nif's static_seat: two pieces, the seat {SEAT_TRIS} and the "
                                            f"piping {PIPING_TRIS} triangles", f"{counts}")
    tid, _ = raster(uvc, SIZE, SIZE)
    part, cov = parts_of(tid, pip, wear_blend(spec, mats))
    ov = piping_overlap(uvc, pip, SIZE, SIZE)
    rep(ov == 0, "the piping's and the seat piece's UV texels apart (no texel both cover)", f"{ov} texels")
    # the stock proof
    stock_row = int(sp["stock_row"])
    fac = pal[stock_row, :, :3].astype(np.float64) / 255.0
    ref = d.astype(np.float64) / 255.0
    lines, good = [], True
    for c, cn in ((0, "R"), (1, "G")):
        rec = fac[levels[0][..., c].astype(np.int64)]
        mse = float(((rec - ref)[cov] ** 2).mean())
        db = 10 * np.log10(1.0 / max(mse, 1e-12))
        good &= db >= PROOF_DB
        per = []
        for p in range(3):
            sel = part == p
            m_ = float(((rec - ref)[sel] ** 2).mean())
            per.append(f"{PARTS[p]} {10 * np.log10(1.0 / max(m_, 1e-12)):.1f}")
        lines.append(f"{cn} as U {db:.1f} dB ({', '.join(per)})")
    rep(good, f"the proof: the stock row ({stock_row}, {sp['leather']} with its wear {sp['wear_patch']}) through {name_i} "
              f"(BC1, level 0) gives the shipped static_seat_d.dds back at {PROOF_DB:g} dB or more over the "
              f"{int(cov.sum())} seat texels", "; ".join(lines))
    de = np.linalg.norm(oklab(LP.lin(fac[levels[0][..., 1].astype(np.int64)]))[cov] - oklab(LP.lin(ref))[cov], axis=-1)
    print(f"INFO  the proof per texel in OKLab (a dark texture flatters a PSNR): distance mean {de.mean():.4f}, 95th "
          f"percentile {np.percentile(de, 95):.4f}, 99th {np.percentile(de, 99):.4f} (about 0.02 is a just-visible step)")
    _, fd = W.read_dds(find(args.base, Path("Textures/CMB/Bike/static_seat_d.dds")))
    # the mips per part, the piping kept, the stock row at mips 1-3 against the shipped mips
    has, pt = np.stack([part == p for p in range(3)]), cov
    astray, area, dbs = [], [], []
    for k, lv in enumerate(levels):
        if k:
            has, pt = LP.any2(has), LP.any2(pt)
        if lv.shape[:2] != pt.shape:
            astray.append(-1)
            break
        n = 0
        for c in (0, 1):
            s_ = LP.seg_of(lv[..., c], seg)
            own = np.zeros(pt.shape, bool)
            for p in range(3):
                own |= (s_ == p) & has[p]
            n = max(n, int((pt & ~own).sum()))
        astray.append(n)
        area.append(int(((LP.seg_of(lv[..., 1], seg) == 2) & pt).sum()) * 4 ** k)
        if 1 <= k <= 3:
            rec = fac[lv[..., 1].astype(np.int64)]
            mse = float(((rec - fd[0][k][..., :3].astype(np.float64) / 255.0)[pt] ** 2).mean())
            dbs.append(f"mip {k} {10 * np.log10(1.0 / max(mse, 1e-12)):.1f} dB")
    rep(astray and min(astray) == 0 and max(astray) == 0,
        f"{name_i}, all {len(levels)} mips: no seat texel's U (R or G) in a band none of its level-0 footprint's parts "
        f"has (the index map's mips per part)", "texels per mip " + ", ".join(map(str, astray)))
    for c, cn in ((0, "R"), (1, "G")):
        got = (LP.seg_of(levels[0][..., c], seg) == 2) & cov
        want_p = part == 2
        rep(np.array_equal(got, want_p), f"the piping mask ({cn} as U): the level-0 seat texels in the piping band are the "
                                         f"parked nif's {PIPING_TRIS}-triangle piece's UV texels exactly ({int(want_p.sum())})",
            f"{int((got & ~want_p).sum())} extra, {int((want_p & ~got).sum())} missing")
    keep = [a / area[0] for a in area[1:4]] if area and area[0] else []
    rep(len(keep) == 3 and min(keep) >= PIPE_KEEP, f"the piping at mips 1-3 (two-tone at distance): its area at least "
                                                   f"{PIPE_KEEP:g} of level 0's ({area[0] if area else 0} texels)",
        ", ".join(f"{x:.2f}" for x in keep))
    print(f"INFO  the stock row through {name_i}'s mips (G as U) against the shipped diffuse's own mips: {'; '.join(dbs)}")
    # every row's colours, per part, as written (the index map, the palette file, each material's V)
    shade = LP.lum(LP.lin(ref)) / LP.lum(LP.hexlin(sp["leather"]))
    lea, wp, norm = stock(sp)
    u0 = levels[0][..., 1].astype(np.int64)
    vrow = {}
    for name, (worn, o) in targets.items():
        if (mdir / name).exists():
            vrow.setdefault(o["key"], int(math.floor(B.read(mdir / name)["grayscale_to_palette_scale"] * ROWS)))
    vrow["stock"] = stock_row
    wt = np.where(cov, dens[np.clip(tid, 0, None)], 0.0)        # each seat texel's surface on the bike
    leather, welt = (part == 0) | (part == 1), part == 2

    def seen(col, m):
        """The seat's area-weighted mean colour over m, as seen (linear light averaged, then OKLab)."""
        return oklab((np.clip(col[m], 0, 1) * wt[m][:, None]).sum(0) / wt[m].sum())
    welt_med = float(np.median(shade[welt]))
    bad, table, avg, piped = [], [], {}, []
    for r in rows:
        key, rr = r["key"], vrow.get(r["key"])
        if rr is None:
            bad.append(f"{key}: no material names row {r['row']}")
            continue
        if rr != r["row"]:
            bad.append(f"{key}: its materials read row {rr}, not {r['row']}")
        dec = LP.lin(pal[rr, :, :3].astype(np.float64) / 255.0)[u0]
        b, p = LP.hexlin(r["body"]), LP.hexlin(r["piping"])
        gain = pipe_gain(r["body"], r["piping"])
        tone = (b * (1 - WEAR_MIX) + worn_tone(b, lea, wp) * WEAR_MIX) * norm
        ideal = np.choose(np.clip(part, 0, 2)[..., None], [b, tone, p * gain]) * shade[..., None]
        if key != "stock":
            avg[key] = (r["body"].lower(), seen(dec, leather), seen(dec, welt))
        cells = []
        for q, colour in ((0, b), (2, p), (1, tone)):
            sel = part == q
            if not sel.any():
                continue
            a_, i_ = lch(oklab(np.clip(dec[sel], 0, 1)).mean(0)), lch(oklab(np.clip(ideal[sel], 0, 1)).mean(0))
            dl, dc = a_[0] - i_[0], a_[1] - i_[1]
            dh = ((a_[2] - i_[2] + 180) % 360) - 180
            de = float(np.linalg.norm(oklab(np.clip(dec[sel], 0, 1)).mean(0) - oklab(np.clip(ideal[sel], 0, 1)).mean(0)))
            hue_ok = i_[1] < HUE_MIN_C or abs(dh) <= MEAN_DH
            if not (abs(dl) <= MEAN_DL and abs(dc) <= MEAN_DC and hue_ok and de <= MEAN_DE):
                bad.append(f"{key} {PARTS[q]}: mean dL {dl:+.4f} dC {dc:+.4f} dh {dh:+.1f} dE {de:.4f}")
            cells.append(f"{PARTS[q]} dL {dl:+.3f} dh {dh:+.1f}" + ("" if i_[1] >= HUE_MIN_C else "(grey)"))
            if q != 1:
                g_ = gain if q == 2 else 1.0
                ls = sel & cov & (shade * g_ >= LIT[0]) & (shade * g_ <= LIT[1])
                if ls.sum() >= 50:
                    m_ = oklab(np.clip(dec[ls], 0, 1)).mean(0)
                    de_t = float(np.linalg.norm(m_ - oklab(colour)))
                    if de_t > LIT_DE:
                        bad.append(f"{key} {PARTS[q]}: its texels at their own shade {de_t:.4f} from "
                                   f"{r['body' if q == 0 else 'piping']}")
                    cells[-1] += f", lit {''.join(f'{x:02x}' for x in LP.to_u8(from_oklab(m_)))} dE {de_t:.3f}"
        if gain != 1.0:
            piped.append((key, r, float(np.median(oklab(np.clip(dec[welt], 0, 1))[:, 0])),
                          float(np.linalg.norm(seen(dec, welt) - seen(dec, leather)))))
        table.append(f"  row {r['row']:2d} {key:<14} " + "; ".join(cells))
    rep(not bad, f"every row's colours as written (index map, {name_p}, the materials' V), per part: the mean OKLab "
                 f"lightness within {MEAN_DL}, chroma {MEAN_DC}, hue {MEAN_DH:g} degrees (from chroma {HUE_MIN_C}) and "
                 f"distance {MEAN_DE} of the row's colour at the shipped seat's own shading (a contrasting welt's times "
                 f"{PIPE_GAIN:g}); the body's and the welt's texels at their own shade ({LIT[0]}-{LIT[1]}) within "
                 f"{LIT_DE} of the row's colour itself", "; ".join(bad[:8]))
    print("\n".join(table))
    # every two options apart, as rendered: option 0 the shipped seat itself, the others through their rows
    avg["stock (option 0)"] = (sp["leather"].lower(), seen(LP.lin(ref), leather), seen(LP.lin(ref), welt))
    pairs = []
    for (ka, (ba, la, wa)), (kb, (bb, lb, wb)) in itertools.combinations(sorted(avg.items()), 2):
        if ba == bb:
            pairs.append((float(np.linalg.norm(wa - wb)), ka, kb, "welt (the same seat colour)"))
        else:
            pairs.append((float(np.linalg.norm(la - lb)), ka, kb, "seat"))
    pairs.sort()
    seat_p_ = [x for x in pairs if x[3] == "seat"]
    welt_p_ = [x for x in pairs if x[3] != "seat"]
    rep(pairs and pairs[0][0] >= DE_MIN,
        f"every two of the {len(avg)} options at least {DE_MIN} apart in OKLab as the shader colours the seat (index "
        f"map through the palette, the bake's shading, before lighting; the leather's area-weighted mean in linear light; "
        f"two options of one seat colour by their welts): {len(pairs)} pairs",
        f"smallest by the seat {seat_p_[0][1]} / {seat_p_[0][2]} {seat_p_[0][0]:.3f}"
        + (f", by the welt {welt_p_[0][1]} / {welt_p_[0][2]} {welt_p_[0][0]:.3f}" if welt_p_ else "")
        + "".join(f"; {k1} / {k2} {d_:.3f} ({w_})" for d_, k1, k2, w_ in pairs if d_ < DE_MIN))
    print("INFO  the closest pairs: " + "; ".join(f"{k1} / {k2} {d_:.3f} ({w_})" for d_, k1, k2, w_ in pairs[:6]))
    # the contrasting welts: shown at their swatch's lightness, apart from their seat
    bad = [f"{k}: welt median L {ml:.3f} for its swatch's {oklab(LP.hexlin(r['piping']))[0]:.3f}, {de_:.3f} from its seat"
           for k, r, ml, de_ in piped if abs(ml - oklab(LP.hexlin(r["piping"]))[0]) > PIPE_DL or de_ < PIPE_DE]
    rep(piped and not bad, f"the {len(piped)} contrasting welts as the shader colours them: the welt's median OKLab lightness within "
                           f"{PIPE_DL} of its swatch's (the welt's shade {welt_med:.3f} in the shipped bake, times "
                           f"{PIPE_GAIN:g}), and the welt at least {PIPE_DE} from its seat (area-weighted means)",
        "; ".join(bad) if bad else ", ".join(f"{k} L {ml:.3f}/{oklab(LP.hexlin(r['piping']))[0]:.3f} apart {de_:.3f}"
                                            for k, r, ml, de_ in piped))
    # the swaps' sources and targets
    missing = []
    for o in slot["options"]:
        for src, tgt in o["swap"] or []:
            if find(args.base, Path("Materials") / src.replace("\\", "/")) is None:
                missing.append(f"source {src}")
            if o["kind"] == "seat" and not (args.data / "Materials" / tgt.replace("\\", "/")).exists():
                missing.append(f"target {tgt}")
            if o["kind"] == "identity" and src != tgt:
                missing.append(f"option {o['index']} isn't the identity")
    rep(not missing and len(slot["options"]) == 15, f"the Seat slot's {len(slot['options'])} options: every swap source in the "
                                                    f"base, every palette option's target here, option 0 the identity",
        ", ".join(missing[:8]))
    # one index map for every bike: the other nifs' seat UVs are the parked one's
    diffs = []
    for stem in NIFS[1:]:
        p = find(args.base, Path("Meshes/CMB") / f"{stem}.nif")
        if p is None:
            diffs.append(f"{stem} not in the base")
            continue
        uv2, pip2, _, _ = seat_piece(args.pynifly, p)
        if uv2.shape != uvc.shape or np.abs(uv2 - uvc).max() > 1e-6 or not np.array_equal(pip2, pip):
            diffs.append(f"{stem}: UVs differ by {np.abs(uv2 - uvc).max() if uv2.shape == uvc.shape else uv2.shape}")
    rep(not diffs, f"the seat's UVs and pieces in the {len(NIFS) - 1} worn and view nifs the parked nif's (one index map "
                   f"serves every bike)", "; ".join(diffs))
    # option 0: the shipped seat untouched. --data is an overlay (the shipped files not in it) or a whole tree (the
    # package's Data: there, each one the base's bytes)
    over = []
    for p in (mdir / "static_seat.bgsm", mdir / "static_seat_worn.bgsm", tdir / "static_seat_d.dds",
              tdir / "static_seat_n.dds", tdir / "static_seat_s.dds"):
        if p.exists():
            b = find(args.base, p.relative_to(args.data))
            if b is None or b.read_bytes() != p.read_bytes():
                over.append(p.name)
    rep(not over, "the shipped seat's files not in --data, or there the base's bytes (option 0, \"as it came\", is the "
                  "shipped seat byte for byte)", ", ".join(over))
    extra = sorted(str(p.relative_to(args.data)) for p in args.data.rglob("*") if p.is_file()
                   and p.name not in set(targets) | {name_i, name_p})
    print(f"INFO  --data holds {len(targets)} materials files and the 2 textures" +
          (f", and {len(extra)} other files ({', '.join(extra[:6])})" if extra else ", nothing else"))
    print(f"INFO  the parts: body {int((part == 0).sum())}, wear {int((part == 1).sum())}, piping {int((part == 2).sum())} "
          f"texels of {int(cov.sum())}")
    print("look_seat: all checks passed" if ok else "look_seat: FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, required=True, help="the Data tree to write (Materials, Textures)")
    ap.add_argument("--base", type=Path, action="append", required=True,
                    help="the asset base's Data (read only; repeat: later folders over earlier ones)")
    ap.add_argument("--pynifly", type=Path, required=True, help="PyNifly's io_scene_nifly (the nifs' seat pieces)")
    ap.add_argument("--options", type=Path, default=HERE.parent / "esp-generator" / "look_options.json")
    ap.add_argument("--materials", type=Path, default=HERE / "bike_materials.json")
    ap.add_argument("--denoise", type=int, default=1, choices=(0, 1),
                    help="1: the shade smoothed within each part (BC1's steps out); 0: the per-texel re-sample as it is")
    ap.add_argument("--check", action="store_true", help="check a built tree (and nothing written)")
    args = ap.parse_args()
    opts = json.loads(args.options.read_text())
    mats = json.loads(args.materials.read_text())
    if any(args.data.resolve() == b.resolve() for b in args.base):
        ap.error("--data must not be a --base (the base is read only)")
    return check(args, opts, mats) if args.check else build(args, opts, mats)


if __name__ == "__main__":
    sys.exit(main())
