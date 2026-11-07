#!/usr/bin/env python3
"""The licence plate's textures and materials (since the 2026-11-08a build), from bike_art.py --plates' index maps.

    <dds python> -I look_plates.py --art <stage>/art_plates --out <Data-like tree> [--look-options <json>]
        [--old-stage <2026-11-07a's stage>] [--stage <this build's stage>]
    <dds python> -I look_plates.py --check --art <stage>/art_plates --out <tree> [--old-stage ...] [--stage ...]
    <dds python> -I look_plates.py --sheet <folder> --art <stage>/art_plates --out <tree>

Writes, under --out (a Data folder's layout; Textures\\CMB\\Bike, Materials\\CMB\\Bike):

  plates_d.dds        BC1 2048 x 1024, the 12 designs' index map (4 x 4 cells of 512 x 256, each face 496 x 226 at
                      (8, 8)): a texel's grey is the U of its palette row. The mips are made per part (an index can't
                      be averaged: a legend and base mix would land in another segment): a mip texel is the legend or
                      the accent when that part covers a quarter of its level-0 footprint or more (so a 1-unit legend
                      lasts to mip 3), else the part with most of it, at the mean U of that part's texels only; BC1
                      blocks that would decode a texel (R or G) into another part's segment are re-encoded on grey
                      endpoints in their parts' segments (look_paint.py's way, for N parts)
  plates_n.dds        BC5 1024 x 512: the beads, the embossed legends and borders, bolts, welds (from plates_h.png)
  plates_s.dds        BC5 512 x 256: R specular, G smoothness
  plate_text_d.dds    BC3 2048: the 60 texts (4 x 16 cells of 512 x 128, each drawn 496 x 112 at (8, 8)): RGB the U of
                      the ink's row (the stamped character's shade baked in: light-from-above 1.15, away 0.75), A the
                      characters for the alpha test at 128; the alpha mips keep each cell's share of texels at 128 or
                      more as level 0's (a box-filtered alpha thins and breaks the characters with distance)
  plate_text_n.dds    BC5 1024: the characters' 3-px cosine bevel, 0.12 units high
  plate_text_s.dds    BC5 512
  plate_p.dds         RGBA8 256 x 256, one mip: row (design - 1) x 16 + background (192 used, 192-255 row 191's): U 0-47
                      the fixed colours (the same in every row), 56-159 the background x 0.4-1.4, 168-215 the design's
                      legend colour x 0.6-1.3 (swapped for the letters' colour, then black or white, where it would fall
                      under 3:1 against the background), 224-255 the accent x 0.6-1.3; the guards between blend
  plate_text_p.dds    RGBA8 256 x 16, one mip: row = ink: U 0-63 the ink x 0.5-0.85, 72-255 x 0.6-1.2
  static_plate_d/_n/_s.dds  256 x 128 (BC1, BC5, BC5): the stock plate, 2026-11-07a's static_black texels re-sampled
                      through the face's old UVs onto static_plate's own (the face read true from behind over the whole
                      texture); _n through object space (decoded in the old tangent frame, encoded in the new). With
                      --stage holding shapes/ and uv/static_plate.npz the new UVs are the export's; else the face's
                      box (u to the viewer's right, v down) stands in
  plate_<key>.bgsm    12: static_black.bgsm's values, the design atlas, the greyscale slot plate_p.dds with
                      grayscale_to_palette_color on and its scale the design's own row's centre, tiles clamped, the UV
                      transform taking the shape's 0-1 to the cell's drawn face (look_badges.cell_transform)
  text_<key>.bgsm     60: a fender badge's material (alpha test 128, decal, two-sided) without the chrome cube, the
                      text atlas, plate_text_p.dds at the text's preview ink, clamped, the cell's transform

--check: formats, sizes, full mips; the per-part mips (no texel in a part its level-0 footprint lacks, R or G; the legends
kept at mips 1-3); alpha coverage per cell within 5 % of level 0's down to mip 4; the 8-px margins clear to mip 3 (the
text's alpha 0, the designs' base); every text inside its drawn area and 480 px; the palettes' rows; the palette proof
(the designs and the texts in their own colours through the DDS at 33 dB or more against the art's own colours); the
stock re-sample within 2 levels mean of static_black's texels; every material read back; the text list (5-7
characters, the set, unique, the crude flag); the brand and real-plate scan over every legend, text and name (the
brand words, the US states, their plates' slogans); no game texture under --out.

--sheet <folder>: designs.png (every design with its own text and colours, lit, and at the riding view's mips 2 and 3),
texts.png (every text on the standard plate), backgrounds.png (every design on every background: no legend vanishes),
legibility.png (the 16 x 16 ink and background grid, pairs under 3:1 flagged).

Fallout 4 semantics (DESIGN.md): no diffuse tint for lit materials; the palette lookup is the one per-material colour.
Nothing from the files read is executed.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bgsm  # noqa: E402
import write_dds as W  # noqa: E402
from look_badges import brand_words, cell_transform  # noqa: E402
from look_paint import hexlin, lum, to_u8  # noqa: E402

TEX = ("Textures", "CMB", "Bike")
MAT = ("Materials", "CMB", "Bike")
COVER = 0.25          # a mip texel is the legend or the accent from this share of its level-0 footprint up
THIN = (1, 2)         # those parts (bike_art: BASE 0, LEGEND 1, ACCENT 2, the fixed colours 3-8)
LEGEND_KEEP = 0.5     # --check: the legend's area at mips 1-3 at least this share of level 0's
ALPHA_KEEP = 0.05     # --check: each text cell's alpha coverage within this share of level 0's, to mip 4
PROOF_DB = 33.0
LEGALISED_MAX = 400   # --check: level-0 texels of the designs BC1 can't show in their own part (of 2,097,152)
RESAMPLE_LEVELS = 2.0
CONTRAST = 3.0
STOCK = (256, 128)
# the real-plate scan (besides check_bike_meshes' brand words): the US states and slogans their plates carry
STATES = ("alabama alaska arizona arkansas california colorado connecticut delaware florida georgia hawaii idaho "
          "illinois indiana iowa kansas kentucky louisiana maine maryland massachusetts michigan minnesota mississippi "
          "missouri montana nebraska nevada new hampshire new jersey new mexico new york north carolina north dakota "
          "ohio oklahoma oregon pennsylvania rhode island south carolina south dakota tennessee texas utah vermont "
          "virginia washington west virginia wisconsin wyoming")
STATE_NAMES = ["new hampshire", "new jersey", "new mexico", "new york", "north carolina", "north dakota", "rhode island",
               "south carolina", "south dakota", "west virginia"]
SLOGANS = ("spirit of america", "live free or die", "empire state", "garden state", "land of lincoln", "famous potatoes",
           "sunshine state", "first in flight", "first state", "show me state", "grand canyon state", "lone star state",
           "great lakes", "pure michigan", "vacationland", "ocean state", "green mountain state", "constitution state",
           "keystone state", "wild wonderful", "evergreen state", "golden state", "peach state", "heart of dixie",
           "natural state", "centennial state", "colorful colorado", "life elevated", "big sky country", "aloha state",
           "last frontier", "land of enchantment", "sportsman's paradise", "volunteer state", "america's dairyland",
           "10,000 lakes", "silver state", "cornhusker state", "treasure state", "peace garden state",
           "great faces great places", "hoosier state", "crossroads of america", "bluegrass state", "unbridled spirit",
           "birthplace of aviation", "native america", "virginia is for lovers", "palmetto state", "magnolia state",
           "pacific wonderland", "old line state", "the commonwealth of")


def state_words():
    names = set(STATE_NAMES)
    one = STATES
    for n in STATE_NAMES:
        one = one.replace(n, " ")
    names.update(one.split())
    return sorted(names)


# --- colour ---------------------------------------------------------------------------------------------------

def rel_lum(h):
    return float(lum(hexlin(h)))


def contrast(a, b):
    la, lb = rel_lum(a), rel_lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def colours(opts):
    return {c["index"]: c["srgb"] for c in opts["plate_colours"]}


def swapped(want, bg, own, cols):
    """A legend's colour index on background bg: its own if 3:1 or better, else the letters' own, else black or white."""
    for c in (want, own):
        if contrast(cols[c], cols[bg]) >= CONTRAST:
            return c
    black, white = 2, 0
    return black if contrast(cols[black], cols[bg]) >= contrast(cols[white], cols[bg]) else white


def design_colours(d, bg, meta, cols):
    """(legend sRGB, accent linear RGB) of design d on background bg."""
    legend = d["legend"] if d["legend"] is not None else d["own_ink"]
    lg = swapped(legend, bg, d["own_ink"], cols)
    acc = meta["designs"][d["key"]]["accent"]
    if acc is None:
        a = hexlin(cols[lg])
    elif acc[0] == "tint":
        a = hexlin(cols[bg]) * (1 - acc[2]) + hexlin(acc[1]) * acc[2]
    else:
        a = hexlin(cols[swapped(acc[1], bg, d["own_ink"], cols)])
    return cols[lg], a


def _ramp(row, seg, col, s0, s1):
    u0, u1 = seg
    t = (np.arange(u0, u1 + 1) - u0) / (u1 - u0)
    row[u0:u1 + 1] = np.asarray(col)[None, :] * (s0 + (s1 - s0) * t)[:, None]


def _guards(row, segs):
    """Blend the gaps between the segments (sorted by U) from one's top to the next's foot."""
    segs = sorted(segs)
    for (a0, a1), (b0, b1) in zip(segs[:-1], segs[1:]):
        for i in range(a1 + 1, b0):
            t = (i - a1) / (b0 - a1)
            row[i] = row[a1] * (1 - t) + row[b0] * t


def fixed_segments(meta):
    """Each fixed colour's U range: from halfway to its neighbours (the first from 0, the last to the fixed top)."""
    us = [f[1] for f in meta["fixed"]]
    out = []
    for i, u in enumerate(us):
        lo = 0 if i == 0 else (us[i - 1] + u) // 2 + 1
        hi = 47 if i == len(us) - 1 else (u + us[i + 1]) // 2
        out.append((lo, hi))
    return out


def plate_row(d, bg, meta, pal, cols):
    row = np.zeros((256, 3))
    for (lo, hi), (_, _, h) in zip(fixed_segments(meta), meta["fixed"]):
        row[lo:hi + 1] = hexlin(h)
    lg, ac = design_colours(d, bg, meta, cols)
    u = pal["u"]
    _ramp(row, u["base"], hexlin(cols[bg]), *pal["base_shade"])
    _ramp(row, u["legend"], hexlin(lg), *pal["legend_shade"])
    _ramp(row, u["accent"], ac, *pal["legend_shade"])
    _guards(row, [tuple(u["fixed"]), tuple(u["base"]), tuple(u["legend"]), tuple(u["accent"])])
    return row


def plate_palette(opts, meta):
    pal = opts["plate_palette"]["plate"]
    cols = colours(opts)
    W_, H_ = pal["size"]
    img = np.zeros((H_, W_, 4), np.uint8)
    img[..., 3] = 255
    last = 0
    for d in opts["plates"]:
        if d["cell"] is None:
            continue
        for bg in range(16):
            r = (d["index"] - 1) * 16 + bg
            img[r, :, :3] = to_u8(plate_row(d, bg, meta, pal, cols))
            last = max(last, r)
    img[last + 1:] = img[last]
    return img


def text_palette(opts):
    pal = opts["plate_palette"]["text"]
    cols = colours(opts)
    W_, H_ = pal["size"]
    img = np.zeros((H_, W_, 4), np.uint8)
    img[..., 3] = 255
    for i in range(H_):
        row = np.zeros((256, 3))
        c = hexlin(cols[i])
        _ramp(row, pal["u"]["bevel"], c, *pal["bevel_shade"])
        _ramp(row, pal["u"]["ink"], c, *pal["ink_shade"])
        _guards(row, [tuple(pal["u"]["bevel"]), tuple(pal["u"]["ink"])])
        img[i, :, :3] = to_u8(row)
    return img


def design_row(d):
    return (d["index"] - 1) * 16 + d["own_back"]


# --- index maps: the mips per part and the BC1 / BC3 colour blocks ---------------------------------------------------

def part_segments(opts, meta):
    u = opts["plate_palette"]["plate"]["u"]
    return [tuple(u["base"]), tuple(u["legend"]), tuple(u["accent"])] + fixed_segments(meta)


def seg_of(u, segs):
    """The part each U belongs to: its nearest segment (a guard's U goes to its nearer side)."""
    u = np.asarray(u, np.int64)
    return np.stack([np.maximum(0, np.maximum(a - u, u - b)) for a, b in segs]).argmin(0)


def index_levels(g, part, nparts):
    """The index map's mip chain per part ([levels], [their parts]), down to 1 x 1: each level's per-part share and mean
    U are the 2 x 2 box of the level above's (so a level's are its level-0 footprint's); a texel is the legend or the
    accent when that share is COVER or more (the larger; the legend on a tie), else the part with the largest share (the
    lowest part on a tie), at that part's mean U. look_paint.index_levels for N parts."""
    h, w = g.shape
    cov = [(part == p).astype(np.float64) for p in range(nparts)]
    tot = [g.astype(np.float64) * c for c in cov]
    levels, parts = [g], [part.astype(np.int64)]
    for _ in range(1, 1 + int(np.floor(np.log2(max(h, w))))):
        tot = [W.half(t) for t in tot]
        cov = [W.half(c) for c in cov]
        C = np.stack(cov)
        th = [q for q in THIN if q < nparts]
        p = C.argmax(0)
        if th:
            thin = C[th]
            p = np.where(thin.max(0) >= COVER, np.asarray(th)[thin.argmax(0)], p)
        T = np.take_along_axis(np.stack(tot), p[None], 0)[0]
        Cp = np.take_along_axis(C, p[None], 0)[0]
        levels.append(np.clip(np.rint(T / np.maximum(Cp, 1e-12)), 0, 255).astype(np.uint8))
        parts.append(p)
    return levels, parts


def _grey565(v):
    r, g_ = int(round(v * 31 / 255)), int(round(v * 63 / 255))
    return (r << 11) | (g_ << 5) | r, ((r << 3) | (r >> 2), (g_ << 2) | (g_ >> 4))


def decode(fmt, buf, w, h):
    import texture2ddecoder as t2d
    dec = {"bc1": t2d.decode_bc1, "bc3": t2d.decode_bc3}[fmt]
    return np.frombuffer(dec(bytes(buf), w, h), np.uint8).reshape(h, w, 4)[..., [2, 1, 0, 3]]


def reencode(data, fmt, u, part, segs, care=None, allowed=None, loose=None):
    """Re-encode the colour blocks of one level (bytes, BC1 or BC3) that decode a texel's U (R or G) into a segment none
    of its allowed parts has (allowed: (parts, h, w) bool, its level-0 footprint's; default its own part only; texels
    where `care` is False don't count): of every pair of grey endpoints from the block's U and its parts' means, the
    one leaving the fewest texels without an entry in an allowed segment (R and G both), then the least error, each
    texel on its nearest entry in its own part's segment, else an allowed one. `loose` (default `allowed`): parts a
    texel BC1 can't serve otherwise may take (a neighbour's), counted after the lost ones. Returns (bytes, the mask of
    texels outside `allowed`)."""
    data = bytearray(data)
    bb, co = (8, 0) if fmt == "bc1" else (16, 8)
    npart = len(segs)
    if allowed is None:
        allowed = np.stack([part == q for q in range(npart)])
    up = W.pad4(u[..., None])[..., 0].astype(np.float64)
    pp = W.pad4(part[..., None])[..., 0]
    if loose is None:
        loose = allowed
    al = np.stack([W.pad4(a[..., None].astype(np.uint8))[..., 0].astype(bool) for a in allowed])
    lo_ = np.stack([W.pad4(a[..., None].astype(np.uint8))[..., 0].astype(bool) for a in loose])
    cc = W.pad4((np.ones(u.shape, bool) if care is None else care)[..., None].astype(np.uint8))[..., 0].astype(bool)
    H, Wd = up.shape

    def astray(buf):
        px = decode(fmt, buf, Wd, H)
        r, g = seg_of(px[..., 0], segs), seg_of(px[..., 1], segs)
        ok = (r == g) & np.take_along_axis(al, g[None], 0)[0]
        return ~ok & cc

    bad = astray(data).reshape(H // 4, 4, Wd // 4, 4).any(axis=(1, 3))
    for by, bx in zip(*np.nonzero(bad)):
        sl = (slice(by * 4, by * 4 + 4), slice(bx * 4, bx * 4 + 4))
        tu, tp, tc = up[sl].ravel(), pp[sl].ravel(), cc[sl].ravel()
        ta = al[(slice(None),) + sl].reshape(npart, 16)
        tl = lo_[(slice(None),) + sl].reshape(npart, 16)
        means = [tu[tp == q].mean() for q in np.unique(tp)]
        extra = [v for a_ in means for b_ in means if a_ != b_ for v in (3 * b_ - 2 * a_, (3 * b_ - a_) / 2)]
        codes = dict(_grey565(v) for v in np.concatenate([tu, means, np.clip(extra, 0, 255)]))   # an endpoint beyond
        # a part's mean puts an interpolated entry on it (a fixed colour between two others)
        pairs = [(a, b) for a in codes for b in codes if a > b or (a == b and fmt == "bc3")] or [(a, a) for a in codes]
        e0 = np.array([codes[a] for a, _ in pairs], np.float64)
        e1 = np.array([codes[b] for _, b in pairs], np.float64)
        ent = np.stack([e0, e1, (2 * e0 + e1) / 3, (e0 + 2 * e1) / 3], 1)
        if fmt == "bc1":                              # a == b in BC1 is the three-colour mode: entry 3 is black
            same = np.array([a == b for a, b in pairs])
            ent[same, 2] = e0[same]
            ent[same, 3] = 0.0
        es = seg_of(np.floor(ent), segs)                                    # (pairs, 4, R G)
        hi_ = seg_of(np.ceil(ent), segs)                                    # decoders round a third either way
        agree = (es[..., 0] == es[..., 1]) & (hi_[..., 0] == es[..., 0]) & (hi_[..., 1] == es[..., 0])   # (pairs, 4)
        ok = agree[:, None, :] & ta.T[np.arange(16)[None, :, None], es[:, None, :, 1]]   # (pairs, 16, 4)
        okl = agree[:, None, :] & tl.T[np.arange(16)[None, :, None], es[:, None, :, 1]]
        mine = ok & (es[:, None, :, 1] == tp[None, :, None])
        dist = np.abs(ent[:, None, :, 1] - tu[None, :, None])
        d_mine = np.where(mine, dist, np.inf).min(2)
        d_ok = np.where(ok, dist, np.inf).min(2)
        d_okl = np.where(okl, dist, np.inf).min(2)
        lost = np.isinf(d_ok) & tc[None, :]
        lostl = np.isinf(d_okl) & tc[None, :]
        err = np.where(np.isfinite(d_mine), d_mine, np.where(np.isfinite(d_ok), d_ok + 32.0,
                                                             np.where(np.isfinite(d_okl), d_okl + 64.0, dist.min(2) + 96.0)))
        cost = lostl.sum(1) * 1e9 + lost.sum(1) * 1e6 + (err * tc[None, :]).sum(1)
        i = int(cost.argmin())
        c0, c1 = pairs[i]
        pick = lambda m: np.where(m[i], dist[i], np.inf).argmin(1)
        idx = np.where(np.isfinite(d_mine[i]), pick(mine), np.where(np.isfinite(d_ok[i]), pick(ok),
                                                                    np.where(np.isfinite(d_okl[i]), pick(okl), dist[i].argmin(1))))
        bits = int(sum(int(j) << (2 * k) for k, j in enumerate(idx)))
        o = (by * (Wd // 4) + bx) * bb + co
        data[o:o + 8] = int(c0).to_bytes(2, "little") + int(c1).to_bytes(2, "little") + bits.to_bytes(4, "little")
    return bytes(data), astray(data)[:u.shape[0], :u.shape[1]]


def grey_rgba(g, a=None):
    return np.dstack([g, g, g, np.full_like(g, 255) if a is None else a])


def dilate(presence):
    """(parts, h, w) bool: each texel's and its eight neighbours' parts."""
    out = presence.copy()
    pad = np.pad(presence, ((0, 0), (1, 1), (1, 1)), mode="edge")
    h, w = presence.shape[1:]
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            out |= pad[:, dy:dy + h, dx:dx + w]
    return out


def index_dds(g, part, segs):
    """The design atlas' DDS (BC1, the per-part mips). A 4 x 4 block of four parts or more may have no endpoint pair
    serving them all: a texel left without an entry in its own part (at a mip: in a part of its level-0 footprint)
    takes a part one of its eight neighbours has (a small emblem's edge), and level 0 as shown is the mips' source.
    Returns (bytes, ([texels moved at level 0], [texels outside their footprint per level]))."""
    n = len(segs)
    own = np.stack([part == q for q in range(n)])
    data0, bad0 = reencode(W.compress(grey_rgba(g), "bc1", "auto", opaque=True), "bc1", g, part, segs, loose=dilate(own))
    H4, W4 = W.pad4(g[..., None]).shape[:2]
    px = decode("bc1", data0, W4, H4)[:g.shape[0], :g.shape[1]]
    shown = seg_of(px[..., 1], segs)
    g, part = np.where(bad0, px[..., 1], g).astype(np.uint8), np.where(bad0, shown, part)
    levels, parts = index_levels(g, part, n)
    body, left = data0, [int(bad0.sum())]
    allowed = np.stack([part == q for q in range(n)])
    for lv, pt in zip(levels[1:], parts[1:]):
        allowed = np.stack([W.half(a.astype(np.float64)) > 0 for a in allowed])
        b, bad = reencode(W.compress(grey_rgba(lv), "bc1", "auto", opaque=True), "bc1", lv, pt, segs, allowed=allowed,
                          loose=dilate(allowed))
        body += b
        left.append(int(bad.sum()))
    return W.header("bc1", g.shape[1], g.shape[0], len(levels), False, False, False, False) + body, left


THR = 127.5 / 255.0
GUARD = 10.0 / 255.0  # a mip's alpha kept this far off the alpha test's threshold


def cell_shares(a, sw, sh):
    """Each cell's share of texels at the alpha test's 128 or more (a float 0-1 or uint8 level)."""
    on = a >= (THR if a.dtype != np.uint8 else 128)
    H, Wd = on.shape
    return on.reshape(H // sh, sh, Wd // sw, sw).mean(axis=(1, 3))


def scale_cells(cur, sw, sh, target, seed=128):
    """cur scaled per cell (sw x sh) so that each cell's share at the threshold is as near its target as can be; a fixed
    dither of under half a level (seeded) keeps texels of one value from crossing the threshold all at once."""
    out = cur.copy()
    jit = np.random.default_rng(seed).uniform(-0.45, 0.45, cur.shape) / 255.0
    for r in range(target.shape[0]):
        for c in range(target.shape[1]):
            t = target[r, c]
            sl = (slice(r * sh, (r + 1) * sh), slice(c * sw, (c + 1) * sw))
            blk = cur[sl] + jit[sl] * (cur[sl] > 0)
            if t <= 0 or blk.max() <= 0:
                continue
            lo, hi = 0.0, 4.0 / max(blk.max(), 1e-6)
            for _ in range(40):
                mid = (lo + hi) / 2
                if (blk * mid >= THR).mean() < t:
                    lo = mid
                else:
                    hi = mid
            s_lo, s_hi = (blk * lo >= THR).mean(), (blk * hi >= THR).mean()
            out[sl] = np.clip(blk * (hi if abs(s_hi - t) <= abs(s_lo - t) else lo), 0, 1)
    near = (np.abs(out - THR) < GUARD) & (cur > 0)        # off the threshold by GUARD, so BC3's alpha error rarely
    out[near] = np.where(out[near] >= THR, THR + GUARD, THR - GUARD)   # flips a texel across it
    return out


def text_dds(rgba, cell, seg):
    """The text atlas' DDS (BC3): the colour (one part, the ink) box-filtered; the alpha's mips coverage-preserving: each
    level the box filter of level 0, scaled per cell (while a cell is a texel or more) so that its share of texels at
    128 or more, as BC3 decodes it, is level 0's (the scale's target corrected by what the encoding gave, a few times).
    Returns (bytes, texels astray per level)."""
    cw, ch = cell
    g = rgba[..., 0]
    glevels = index_levels(g, np.zeros(g.shape, np.int64), 1)[0]
    zeros = lambda x: np.zeros(x.shape, np.int64)

    def enc(gl, a8):
        b, bad = reencode(W.compress(grey_rgba(gl, a8), "bc3", "auto"), "bc3", gl, zeros(gl), [seg], care=a8 >= 128)
        H4, W4 = W.pad4(gl[..., None]).shape[:2]
        return b, int(bad.sum()), decode("bc3", b, W4, H4)[:gl.shape[0], :gl.shape[1], 3]

    body, left, share0 = b"", [], None
    cur = rgba[..., 3].astype(np.float64) / 255.0
    for k, gl in enumerate(glevels):
        if k:
            cur = W.half(cur)
        sw, sh = cw >> k, ch >> k
        cells = k > 0 and sw >= 1 and sh >= 1
        target = share0.copy() if cells else None
        a8 = np.clip(np.rint((scale_cells(cur, sw, sh, target) if cells else cur) * 255), 0, 255).astype(np.uint8)
        b, n, dec = enc(gl, a8)
        if k == 0:
            share0 = cell_shares(dec, cw, ch)
        elif cells:                                # each cell's best try kept (no BC3 block straddles two cells)
            best_err = np.full(share0.shape, np.inf)
            best = a8.copy()
            for it in range(14):
                err = share0 - cell_shares(dec, sw, sh)
                rel = np.where(share0 > 0, np.abs(err) / np.maximum(share0, 1e-9), 0.0)
                for r, c in zip(*np.nonzero(rel < best_err)):
                    sl = (slice(r * sh, (r + 1) * sh), slice(c * sw, (c + 1) * sw))
                    best[sl], best_err[r, c] = a8[sl], rel[r, c]
                if best_err.max() <= 0.02:
                    break
                target = np.clip(target + 0.7 * err, 0, 1)
                a8 = np.clip(np.rint(scale_cells(cur, sw, sh, target, 129 + it) * 255), 0, 255).astype(np.uint8)
                b, n, dec = enc(gl, a8)
            b, n, dec = enc(gl, best)
        body += b
        left.append(n)
    return W.header("bc3", g.shape[1], g.shape[0], len(glevels), False, False, False, True) + body, left


# --- normal and specular maps ------------------------------------------------------------------------------------

def box_down(a, f):
    h, w = a.shape[:2]
    return a.reshape(h // f, f, w // f, f, *a.shape[2:]).mean(axis=(1, 3))


def normals(h_units, px_per_unit):
    """Direct3D tangent space (R +u, G +v down the image, B out) from a height field in units at px_per_unit."""
    gy, gx = np.gradient(h_units)
    n = np.stack([-gx * px_per_unit, -gy * px_per_unit, np.ones_like(h_units)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    out = np.clip(np.rint((n * 0.5 + 0.5) * 255), 0, 255).astype(np.uint8)
    return np.dstack([out, np.full(h_units.shape, 255, np.uint8)])


def spec_rgba(s8, f):
    s = box_down(s8[..., :2].astype(np.float64), f)
    out = np.zeros(s.shape[:2] + (4,), np.uint8)
    out[..., :2] = np.clip(np.rint(s), 0, 255)
    out[..., 3] = 255
    return out


# --- the stock re-sample -----------------------------------------------------------------------------------------

def face_tris(old_stage):
    """2026-11-07a's static_black: mesh 24's rear face (normal +y) as (positions (n, 3, 3), old UVs (n, 3, 2))."""
    z = np.load(Path(old_stage, "shapes", "static_black.npz"))
    u = np.load(Path(old_stage, "uv", "static_black.npz"))["uv"].astype(np.float64)
    m = z["src"] == 24
    P = z["pos"][z["tri"][m]]
    nrm = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
    face = nrm[:, 1] > 0.9
    return P[face], u[m][face], P[:, :, 1][face].mean()


def new_face_uv(P, stage):
    """The new UVs of those triangles (per corner): the export's static_plate (its shapes npz's uv_fixed, else uv/; the
    triangles matched by their corners' positions) or, without it, the face's box read true from behind (u to the
    viewer's right = parked -x, v down = -z)."""
    if stage is not None and Path(stage, "shapes", "static_plate.npz").exists():
        z = np.load(Path(stage, "shapes", "static_plate.npz"))
        if "uv_fixed" in z.files:                      # a FIXED_UV label's corners (as static_badge's)
            uv = z["uv_fixed"].astype(np.float64)
        else:
            uv = np.load(Path(stage, "uv", "static_plate.npz"))["uv"].astype(np.float64)
        Q = z["pos"][z["tri"]]
        key = {}
        for i, t in enumerate(Q):
            key[tuple(sorted(tuple(np.round(p, 3)) for p in t))] = i
        out = np.zeros(P.shape[:2] + (2,))
        for i, t in enumerate(P):
            j = key[tuple(sorted(tuple(np.round(p, 3)) for p in t))]
            for a in range(3):
                b = int(np.argmin(np.linalg.norm(Q[j] - t[a], axis=1)))
                out[i, a] = uv[j, b]
        return out, "the export's static_plate UVs"
    x0, x1 = P[..., 0].min(), P[..., 0].max()
    z0, z1 = P[..., 2].min(), P[..., 2].max()
    return np.stack([(x1 - P[..., 0]) / (x1 - x0), (z1 - P[..., 2]) / (z1 - z0)], -1), \
        f"the stand-in: the face's box x {x0:.2f}..{x1:.2f} z {z0:.2f}..{z1:.2f}"


def frame(P, uv):
    """Per triangle: unit (T = dP/du, B = dP/dv, N), T and B made orthogonal to N."""
    e1, e2 = P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]
    d1, d2 = uv[:, 1] - uv[:, 0], uv[:, 2] - uv[:, 0]
    det = d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1]
    T = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2]) / det[:, None]
    B = (e2 * d1[:, 0:1] - e1 * d2[:, 0:1]) / det[:, None]
    N = np.cross(e1, e2)
    N /= np.linalg.norm(N, axis=1, keepdims=True)
    T -= N * (T * N).sum(1, keepdims=True)
    B -= N * (B * N).sum(1, keepdims=True)
    return T / np.linalg.norm(T, axis=1, keepdims=True), B / np.linalg.norm(B, axis=1, keepdims=True), N


def bilinear(img, u, v):
    """img (H, W, C) float sampled at UVs (texel centres at (i + 0.5) / size), wrapped."""
    H, Wd = img.shape[:2]
    x, y = u * Wd - 0.5, v * H - 0.5
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = (x - x0)[..., None], (y - y0)[..., None]
    g = lambda yy, xx: img[yy % H, xx % Wd]
    return (g(y0, x0) * (1 - fx) + g(y0, x0 + 1) * fx) * (1 - fy) + (g(y0 + 1, x0) * (1 - fx) + g(y0 + 1, x0 + 1) * fx) * fy


def resample_stock(out, old_stage, stage):
    """The stock plate's three maps (uint8 RGBA, 128 x 256) and how: each new texel's triangle (in the new UVs) and its
    barycentric place give the old UV, read bilinearly; the texels outside every triangle (the rounded corners) take
    the nearest triangle's plane (the face is flat and its old UVs linear)."""
    P, uv_old, _ = face_tris(old_stage)
    uv_new, how = new_face_uv(P, stage)
    Wd, H = STOCK
    yy, xx = np.mgrid[0:H, 0:Wd]
    s, t = (xx + 0.5) / Wd, (yy + 0.5) / H
    tri = np.full((H, Wd), -1)
    bary = np.zeros((H, Wd, 3))
    best = np.full((H, Wd), -np.inf)
    for i in range(len(P)):
        a, b, c = uv_new[i]
        den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-14:
            continue
        l0 = ((b[1] - c[1]) * (s - c[0]) + (c[0] - b[0]) * (t - c[1])) / den
        l1 = ((c[1] - a[1]) * (s - c[0]) + (a[0] - c[0]) * (t - c[1])) / den
        l2 = 1 - l0 - l1
        m = np.minimum(np.minimum(l0, l1), l2)
        take = m > best
        best[take], tri[take] = m[take], i
        bary[take] = np.stack([l0, l1, l2], -1)[take]
    inside = best >= -1e-6
    uvo = (bary[..., :, None] * uv_old[tri]).sum(-2)
    tex = Path(out, *TEX)
    d = W.read_dds(tex / "static_black_d.dds")[1][0][0].astype(np.float64)
    sp = W.read_dds(tex / "static_black_s.dds")[1][0][0].astype(np.float64)
    nm = W.read_dds(tex / "static_black_n.dds")[1][0][0].astype(np.float64)
    dd = bilinear(d, uvo[..., 0], uvo[..., 1])
    ss = bilinear(sp, uvo[..., 0], uvo[..., 1])
    nn = bilinear(nm, uvo[..., 0], uvo[..., 1])[..., :2] / 255.0 * 2 - 1
    nz = np.sqrt(np.clip(1 - (nn ** 2).sum(-1), 0, 1))
    To, Bo, No = frame(P, uv_old)
    Tn, Bn, Nn = frame(P, uv_new)
    obj = nn[..., 0:1] * To[tri] + nn[..., 1:2] * Bo[tri] + nz[..., None] * No[tri]
    new = np.stack([(obj * Tn[tri]).sum(-1), (obj * Bn[tri]).sum(-1), (obj * Nn[tri]).sum(-1)], -1)
    new /= np.linalg.norm(new, axis=-1, keepdims=True)

    def rgba(x):
        o = np.zeros((H, Wd, 4), np.uint8)
        o[..., :3] = np.clip(np.rint(x[..., :3]), 0, 255)
        o[..., 3] = 255
        return o

    n8 = rgba(np.dstack([(new * 0.5 + 0.5) * 255]))
    return rgba(dd), n8, rgba(ss), dict(how=how, inside=int(inside.sum()), texels=H * Wd,
                                        flips=[float(np.median((To[:, 0] * Tn[:, 0]).sum())), float(np.median((Bo * Bn).sum(1)))],
                                        uv_old=uvo)


# --- the materials -----------------------------------------------------------------------------------------------

def tex_rel(name):
    return "CMB\\Bike\\" + name


def transform(at, cell):
    """look_badges.cell_transform with this atlas: the shape's 0-1 onto the cell's drawn area at its offset."""
    (cw, ch), (dw, dh), (ox, oy) = at["cell"], at["draw"], at["offset"]
    t = dict(size=at["size"], cell=at["cell"], draw=at["cell"],
             plate_rect=[-ox / dw, -oy / dh, (cw - ox) / dw, (ch - oy) / dh])
    return cell_transform(t, cell)


def text_template(opts, out):
    for b in opts["badges"]:
        if b["art"] == "ours" and "Fender" in b["slots"]:
            return Path(out, "Materials", *b["material"].split("\\")), b["key"]
    raise SystemExit("no fender badge of ours in the table")


def design_material(tmpl, opts, d):
    at = opts["plate_atlas"]["designs"]
    pal = opts["plate_palette"]["plate"]
    m = bgsm.loads(tmpl)
    m.pop("_raw_tex", None)
    m.pop("_raw_strings", None)
    su, sv, ou, ov = transform(at, d["cell"])
    m["textures"].update(diffuse=at["diffuse"], normal=at["normal"], smoothspec=at["smoothspec"],
                         greyscale=pal["texture"])
    m.update(tile_flags=0, uv_scale_u=su, uv_scale_v=sv, uv_offset_u=ou, uv_offset_v=ov,
             grayscale_to_palette_color=True, grayscale_to_palette_scale=(design_row(d) + 0.5) / pal["size"][1])
    return m


def text_material(tmpl, opts, t):
    at = opts["plate_atlas"]["texts"]
    pal = opts["plate_palette"]["text"]
    m = bgsm.loads(tmpl)
    m.pop("_raw_tex", None)
    m.pop("_raw_strings", None)
    su, sv, ou, ov = transform(at, t["cell"])
    m["textures"].update(diffuse=at["diffuse"], normal=at["normal"], smoothspec=at["smoothspec"],
                         greyscale=pal["texture"], envmap="")
    m.update(tile_flags=0, uv_scale_u=su, uv_scale_v=sv, uv_offset_u=ou, uv_offset_v=ov, alpha_test=True,
             alpha_test_ref=128, decal=True, environment_mapping=False, env_map_mask_scale=1.0,
             grayscale_to_palette_color=True, grayscale_to_palette_scale=(t["preview_ink"] + 0.5) / pal["size"][1])
    return m


# --- writing -----------------------------------------------------------------------------------------------------

def load_png(path):
    from PIL import Image
    im = Image.open(path)
    im.load()
    return np.asarray(im, dtype=np.uint8).copy()


def heights(art, meta, stem, key):
    h = meta["height"][key]
    return h["zero"] + load_png(Path(art, stem)).astype(np.float64) * h["span"] / 255.0


def write(args, opts):
    meta = json.loads(Path(args.art, "plates.json").read_text())
    tex = Path(args.out, *TEX)
    mat = Path(args.out, *MAT)
    tex.mkdir(parents=True, exist_ok=True)
    mat.mkdir(parents=True, exist_ok=True)
    dat, tat = opts["plate_atlas"]["designs"], opts["plate_atlas"]["texts"]
    files = {}
    segs = part_segments(opts, meta)
    g, part = load_png(Path(args.art, "plates_d.png")), load_png(Path(args.art, "plates_part.png"))
    files["plates_d.dds"], left = index_dds(g, part, segs)
    print(f"plates_d.dds: BC1 {g.shape[1]}x{g.shape[0]}, per-part mips; texels BC1 can't show in their own part (blocks "
          f"of four parts or more) shown in a neighbour's, per level: {left}")
    hd = box_down(heights(args.art, meta, "plates_h.png", "designs"), 2)
    files["plates_n.dds"] = W.build([normals(hd, meta["face"]["px_a_unit"] / 2)], "bc5", normal=True)
    files["plates_s.dds"] = W.build([spec_rgba(load_png(Path(args.art, "plates_s.png")), 4)], "bc5")
    rgba = load_png(Path(args.art, "plate_text_d.png"))
    files["plate_text_d.dds"], left = text_dds(rgba, tat["cell"], tuple(opts["plate_palette"]["text"]["u"]["ink"]))
    print(f"plate_text_d.dds: BC3 {rgba.shape[1]}x{rgba.shape[0]}, coverage-preserving alpha mips; texels astray {left}")
    ht = box_down(heights(args.art, meta, "plate_text_h.png", "texts"), 2)
    files["plate_text_n.dds"] = W.build([normals(ht, tat["draw"][0] / opts["plate_atlas"]["face"]["overlay"][0] / 2)],
                                        "bc5", normal=True)
    files["plate_text_s.dds"] = W.build([spec_rgba(load_png(Path(args.art, "plate_text_s.png")), 4)], "bc5")
    files["plate_p.dds"] = W.build([plate_palette(opts, meta)], "rgba8", mips=1)
    files["plate_text_p.dds"] = W.build([text_palette(opts)], "rgba8", mips=1)
    sd, sn, ss, info = resample_stock(args.out, args.old_stage, args.stage)
    files["static_plate_d.dds"] = W.build([sd], "bc1", gamma_mips=True)
    files["static_plate_n.dds"] = W.build([sn], "bc5", normal=True)
    files["static_plate_s.dds"] = W.build([ss], "bc5")
    print(f"static_plate_d/_n/_s.dds {STOCK[0]}x{STOCK[1]}: re-sampled through {info['how']}; {info['inside']} of "
          f"{info['texels']} texels inside the face's triangles (the rest on their plane)")
    total = 0
    for name, data in files.items():
        (tex / name).write_bytes(data)
        total += len(data)
        print(f"{tex / name}: {len(data)} bytes")
    print(f"textures: {len(files)} files, {total} bytes ({total / 1048576:.2f} MB)")
    tmpl = Path(args.out, *MAT, "static_black.bgsm").read_bytes()
    n = 0
    for d in opts["plates"]:
        if d["material"]:
            bgsm.write(Path(args.out, "Materials", *d["material"].split("\\")), design_material(tmpl, opts, d))
            n += 1
    tp, tkey = text_template(opts, args.out)
    tt = tp.read_bytes()
    for t in opts["plate_texts"]:
        bgsm.write(Path(args.out, "Materials", *t["material"].split("\\")), text_material(tt, opts, t))
        n += 1
    print(f"materials: {n} (12 designs over static_black.bgsm's values, 60 texts over badge_{tkey}.bgsm's)")
    return 0


# --- the check ---------------------------------------------------------------------------------------------------

class Report:
    def __init__(self):
        self.fails = 0
        self.n = 0

    def check(self, ok, what, detail=""):
        self.fails += not ok
        self.n += 1
        print(f"{'ok  ' if ok else 'FAIL'} {what}{(': ' + detail) if detail else ''}")


def dds(path):
    return W.read_dds(path) if Path(path).exists() else (None, None)


def any2(a):
    """A boolean map's 2 x 2 any (a level's footprint), odd sides kept."""
    return W.half(a.astype(np.float64)) > 0


def check(args, opts):
    rep = Report()
    meta = json.loads(Path(args.art, "plates.json").read_text())
    tex = Path(args.out, *TEX)
    dat, tat = opts["plate_atlas"]["designs"], opts["plate_atlas"]["texts"]
    cols = colours(opts)
    want = {"plates_d.dds": ("bc1", 2048, 1024), "plates_n.dds": ("bc5", 1024, 512), "plates_s.dds": ("bc5", 512, 256),
            "plate_text_d.dds": ("bc3", 2048, 2048), "plate_text_n.dds": ("bc5", 1024, 1024),
            "plate_text_s.dds": ("bc5", 512, 512), "plate_p.dds": ("rgba8", 256, 256), "plate_text_p.dds": ("rgba8", 256, 16),
            "static_plate_d.dds": ("bc1", 256, 128), "static_plate_n.dds": ("bc5", 256, 128),
            "static_plate_s.dds": ("bc5", 256, 128)}
    dec, total, bad = {}, 0, []
    for name, (fmt, w, h) in want.items():
        info, faces = dds(tex / name)
        if info is None:
            bad.append(f"{name} missing")
            continue
        full = 1 if fmt == "rgba8" else 1 + int(np.log2(max(w, h)))
        if (info["format"], info["w"], info["h"], info["mips"]) != (fmt, w, h, full):
            bad.append(f"{name}: {info['format']} {info['w']}x{info['h']} {info['mips']} mips, not {fmt} {w}x{h} {full}")
        dec[name] = faces[0]
        total += (tex / name).stat().st_size
    rep.check(not bad, f"the {len(want)} textures: formats, sizes and full mips (the palettes one mip)", "; ".join(bad))
    rep.check(9.0e6 <= total <= 11.0e6, "about 10.0 MB in 11 files", f"{total} bytes ({total / 1048576:.2f} MB)")
    segs = part_segments(opts, meta)
    part = load_png(Path(args.art, "plates_part.png")).astype(np.int64)
    g0 = load_png(Path(args.art, "plates_d.png"))
    (W_, H_), (cw, ch), (ox, oy), (dw, dh) = dat["size"], dat["cell"], dat["offset"], dat["draw"]
    if "plates_d.dds" in dec:
        levels = dec["plates_d.dds"]
        # each level against its footprint (level 0: the art's part; a mip: the parts of its level-0 footprint as shown):
        # a texel BC1 can't serve there (a block of four parts or more) may show a part one of its eight neighbours has,
        # LEGALISED_MAX texels a level at most; none may show a part beyond that
        has = np.stack([part == p for p in range(len(segs))])
        outside, foreign, legend = [], [], []
        for k, lv in enumerate(levels):
            if k == 1:
                g_0 = seg_of(levels[0][..., 1], segs)
                has = np.stack([any2(g_0 == p) for p in range(len(segs))])
            elif k > 1:
                has = np.stack([any2(x) for x in has])
            r_, g_ = seg_of(lv[..., 0], segs), seg_of(lv[..., 1], segs)
            inn = (r_ == g_) & np.take_along_axis(has, g_[None], 0)[0]
            near = (r_ == g_) & np.take_along_axis(dilate(has), g_[None], 0)[0]
            outside.append(int((~inn).sum()))
            foreign.append(int((~near).sum()))
            legend.append(int((g_ == 1).sum()) * 4 ** k)
        rep.check(max(foreign) == 0 and max(outside) <= LEGALISED_MAX,
                  f"plates_d.dds, all {len(levels)} mips: every texel's U (R and G) in a part of its level-0 footprint (the "
                  f"mips per part), but at most {LEGALISED_MAX} a level BC1 can't serve (blocks of four parts or more), "
                  f"those in a neighbour's part", f"outside per level {outside}; beyond a neighbour's {foreign}")
        keep = [x / legend[0] for x in legend[1:4]]
        rep.check(min(keep) >= LEGEND_KEEP, f"plates_d.dds: the legends' area at mips 1-3 at least {LEGEND_KEEP:g} of level "
                                            f"0's ({legend[0]} texels)", ", ".join(f"{x:.2f}" for x in keep))
        # the margins and the rows below the face: base at every mip they are a texel or more wide
        mb = []
        for k, lv in enumerate(levels[:4]):
            s = 1 << k
            for d in opts["plates"]:
                if d["cell"] is None:
                    continue
                c, r = d["cell"]
                cell = lv[r * ch // s:(r + 1) * ch // s, c * cw // s:(c + 1) * cw // s, 1]
                ring = np.ones(cell.shape, bool)
                ring[oy // s:-(-(oy + dh) // s), ox // s:-(-(ox + dw) // s)] = False
                if (seg_of(cell[ring], segs) != 0).any():
                    mb.append(f"{d['key']} mip {k}")
        rep.check(not mb, "plates_d.dds: each cell's margin and the rows below its face base colour, mips 0-3", "; ".join(mb))
    # the texts
    if "plate_text_d.dds" in dec:
        levels = dec["plate_text_d.dds"]
        (TW, TH), (tcw, tch), (tox, toy), (tdw, tdh) = tat["size"], tat["cell"], tat["offset"], tat["draw"]
        a0 = levels[0][..., 3]
        cov_bad, margin_bad, inside_bad = [], [], []
        used = {tuple(t["cell"]) for t in opts["plate_texts"]}
        for t in opts["plate_texts"]:
            c, r = t["cell"]
            base = (a0[r * tch:(r + 1) * tch, c * tcw:(c + 1) * tcw] >= 128).mean()
            for k in range(1, 5):
                lv = levels[k][..., 3]
                sw, sh = tcw >> k, tch >> k
                cov = (lv[r * sh:(r + 1) * sh, c * sw:(c + 1) * sw] >= 128).mean()
                if abs(cov - base) > ALPHA_KEEP * base:
                    cov_bad.append(f"{t['key']} mip {k} {cov:.3f}/{base:.3f}")
            for k in range(4):
                lv = levels[k][..., 3]
                m = tox >> k
                sw, sh = tcw >> k, tch >> k
                cc = lv[r * sh:(r + 1) * sh, c * sw:(c + 1) * sw]
                band = np.ones(cc.shape, bool)
                band[m:-m, m:-m] = False
                if cc[band].max(initial=0) > 0:
                    margin_bad.append(f"{t['key']} mip {k}")
            box = meta["texts"][t["key"]]["box"]
            cell = a0[r * tch:(r + 1) * tch, c * tcw:(c + 1) * tcw]
            ys, xs = np.nonzero(cell >= 128)
            if not len(xs) or xs.min() < tox or xs.max() >= tox + tdw or ys.min() < toy or ys.max() >= toy + tdh or \
                    xs.max() + 1 - xs.min() > 480 + 16 or box[2] - box[0] > 480 + 16:
                inside_bad.append(f"{t['key']} {[int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1] if len(xs) else 'empty'}")
        spare = [(c, r) for c in range(TW // tcw) for r in range(TH // tch) if (c, r) not in used]
        sp = max((int(a0[r * tch:(r + 1) * tch, c * tcw:(c + 1) * tcw].max()) for c, r in spare), default=0)
        rep.check(not cov_bad, f"plate_text_d.dds: each text's alpha coverage at mips 1-4 within {ALPHA_KEEP:.0%} of "
                               f"level 0's (coverage-preserving mips)", "; ".join(cov_bad[:8]))
        rep.check(not margin_bad, f"plate_text_d.dds: the {tox}-px margins' alpha 0 at mips 0-3 (clear to mip 4)",
                  "; ".join(margin_bad[:8]))
        rep.check(not inside_bad, f"every text inside its drawn {tdw} x {tdh} and {480} px wide (the ink's box)",
                  "; ".join(inside_bad))
        rep.check(sp == 0, f"the {len(spare)} spare text cells empty", f"alpha up to {sp}")
        ink = tuple(opts["plate_palette"]["text"]["u"]["ink"])
        astr = []
        for k, lv in enumerate(levels):
            on = lv[..., 3] >= 128
            for c in (0, 1):
                n = int((on & ((lv[..., c] < ink[0]) | (lv[..., c] > ink[1]))).sum())
                if n:
                    astr.append(f"mip {k} {'RG'[c]} {n}")
        rep.check(not astr, "plate_text_d.dds: every shown texel's U (R or G) in the ink's segment, every mip", "; ".join(astr))
    # the palettes
    if "plate_p.dds" in dec:
        rep.check(np.array_equal(dec["plate_p.dds"][0], plate_palette(opts, meta)),
                  "plate_p.dds: rows (design - 1) x 16 + background from the table's colours (legends swapped under 3:1)")
        rep.check(np.array_equal(dec["plate_text_p.dds"][0], text_palette(opts)), "plate_text_p.dds: one row per ink")
        vanish = []
        pal = opts["plate_palette"]["plate"]
        for d in opts["plates"]:
            if d["cell"] is None or d["legend"] is None:
                continue
            for bg in range(16):
                lg, _ = design_colours(d, bg, meta, cols)
                if contrast(lg, cols[bg]) < CONTRAST:
                    vanish.append(f"{d['key']}/{cols[bg]}")
        rep.check(not vanish, f"every legend at {CONTRAST:g}:1 or more on every background (192 rows)", "; ".join(vanish))
        own = {d["key"]: contrast(cols[d["own_ink"]], cols[d["own_back"]]) for d in opts["plates"] if d["cell"] is not None}
        print("INFO  the designs' own letters on their own backgrounds (the table's colours): "
              + ", ".join(f"{k} {v:.1f}" for k, v in own.items()))
        sw = [f"{d['key']} {cols[d['legend']]} -> {design_colours(d, d['own_back'], meta, cols)[0]}" for d in opts["plates"]
              if d["cell"] is not None and d["legend"] is not None and design_colours(d, d["own_back"], meta, cols)[0] != cols[d["legend"]]]
        print("INFO  legends swapped on their design's own row (under 3:1): " + ("; ".join(sw) or "none"))
        # the proof: the designs' own rows and the texts' inks through the DDS (level 0, R and G as U) against the art's
        # own colours (each part's colour x its shade, computed in linear light from the PNGs)
        lines, good = [], True
        P_img = dec["plate_p.dds"][0][..., :3].astype(np.float64) / 255
        sh = {0: pal["base_shade"], 1: pal["legend_shade"], 2: pal["legend_shade"]}
        for c_ in (0, 1):
            errs = []
            for d in opts["plates"]:
                if d["cell"] is None:
                    continue
                c, r = d["cell"]
                sl = (slice(r * ch + oy, r * ch + oy + dh), slice(c * cw + ox, c * cw + ox + dw))
                row = P_img[design_row(d)]
                got = row[np.clip(dec["plates_d.dds"][0][sl][..., c_].astype(int), 0, 255)]
                exact = row[g0[sl].astype(int)]          # the art's own U, unquantised by BC1
                errs.append(((got - exact) ** 2).mean())
            db = 10 * np.log10(1 / max(np.mean(errs), 1e-12))
            good &= db >= PROOF_DB
            lines.append(f"designs {'RG'[c_]} as U {db:.1f} dB")
        TP = dec["plate_text_p.dds"][0][..., :3].astype(np.float64) / 255
        trgba = load_png(Path(args.art, "plate_text_d.png"))
        on = trgba[..., 3] >= 128
        for c_ in (0, 1):
            errs = []
            for i in range(16):
                got = TP[i][dec["plate_text_d.dds"][0][..., c_].astype(int)][on]
                exact = TP[i][trgba[..., 0].astype(int)][on]
                errs.append(((got - exact) ** 2).mean())
            db = 10 * np.log10(1 / max(np.mean(errs), 1e-12))
            good &= db >= PROOF_DB
            lines.append(f"texts {'RG'[c_]} as U {db:.1f} dB")
        rep.check(good, f"the palette proof: every design in its own row and every text in each of the 16 inks, through "
                        f"the DDS (level 0) against the art's own index, {PROOF_DB:g} dB or more", "; ".join(lines))
    # the stock re-sample
    if all(k in dec for k in ("static_plate_d.dds", "static_plate_n.dds", "static_plate_s.dds")):
        sd, sn, ss, info = resample_stock(args.out, args.old_stage, args.stage)
        P, uv_old, _ = face_tris(args.old_stage)
        uvo = info["uv_old"]
        msgs, good = [], True
        for name, stem in (("static_plate_d.dds", "static_black_d.dds"), ("static_plate_s.dds", "static_black_s.dds")):
            old = W.read_dds(tex / stem)[1][0][0].astype(np.float64)
            Ho, Wo = old.shape[:2]
            near = old[np.clip((uvo[..., 1] * Ho).astype(int), 0, Ho - 1), np.clip((uvo[..., 0] * Wo).astype(int), 0, Wo - 1)]
            got = dec[name][0].astype(np.float64)
            nch = 3 if name.endswith("_d.dds") else 2
            diff = float(np.abs(got[..., :nch] - near[..., :nch]).mean())
            good &= diff <= RESAMPLE_LEVELS
            msgs.append(f"{name} {diff:.2f}")
        rep.check(good, f"the stock re-sample ({info['how']}) within {RESAMPLE_LEVELS:g} levels mean of static_black's "
                        f"texels at the old UVs", "; ".join(msgs))
        nn = dec["static_plate_n.dds"][0][..., :2].astype(np.float64) / 255 * 2 - 1
        old = W.read_dds(tex / "static_black_n.dds")[1][0][0][..., :2].astype(np.float64) / 255 * 2 - 1
        Ho, Wo = old.shape[:2]
        near = old[np.clip((uvo[..., 1] * Ho).astype(int), 0, Ho - 1), np.clip((uvo[..., 0] * Wo).astype(int), 0, Wo - 1)]
        flip = np.array([np.sign(info["flips"][0]), np.sign(info["flips"][1])])
        diff = float(np.abs(nn - near * flip).mean() * 127.5)
        rep.check(diff <= RESAMPLE_LEVELS * 2, "static_plate_n.dds: the old normals turned into the new frame (here "
                  f"u {'kept' if flip[0] > 0 else 'flipped'}, v {'kept' if flip[1] > 0 else 'flipped'}), within "
                  f"{RESAMPLE_LEVELS * 2:g} levels mean", f"{diff:.2f}")
    # the materials
    bad = []
    tmpl = bgsm.loads(Path(args.out, *MAT, "static_black.bgsm").read_bytes())
    tp, tkey = text_template(opts, args.out)
    ttmpl = bgsm.loads(tp.read_bytes())
    names = []
    for kind, items in (("design", [d for d in opts["plates"] if d["material"]]), ("text", opts["plate_texts"])):
        for it in items:
            p = Path(args.out, "Materials", *it["material"].split("\\"))
            names.append(p.name)
            if not p.exists():
                bad.append(f"{p.name} missing")
                continue
            data = p.read_bytes()
            m = bgsm.loads(data)
            if bgsm.dumps(m) != data:
                bad.append(f"{p.name}: not byte for byte through bgsm.py")
            at = dat if kind == "design" else tat
            pal = opts["plate_palette"]["plate" if kind == "design" else "text"]
            row = design_row(it) if kind == "design" else it["preview_ink"]
            su, sv, ou, ov = transform(at, it["cell"])
            c, r = it["cell"]
            (Wt, Ht), (cw_, ch_), (ox_, oy_), (dw_, dh_) = at["size"], at["cell"], at["offset"], at["draw"]
            corner = [0 * m["uv_scale_u"] + m["uv_offset_u"], 0 * m["uv_scale_v"] + m["uv_offset_v"],
                      m["uv_scale_u"] + m["uv_offset_u"], m["uv_scale_v"] + m["uv_offset_v"]]
            wantc = [(c * cw_ + ox_) / Wt, (r * ch_ + oy_) / Ht, (c * cw_ + ox_ + dw_) / Wt, (r * ch_ + oy_ + dh_) / Ht]
            if max(abs(x - y) for x, y in zip(corner, wantc)) > 1e-6:
                bad.append(f"{p.name}: 0-1 maps to {corner}, not the drawn cell {wantc}")
            if abs(m["grayscale_to_palette_scale"] * pal["size"][1] - 0.5 - row) > 1e-4 or not m["grayscale_to_palette_color"] \
                    or m["textures"]["greyscale"] != pal["texture"]:
                bad.append(f"{p.name}: palette {m['grayscale_to_palette_color']} {m['textures']['greyscale']} row "
                           f"{m['grayscale_to_palette_scale'] * pal['size'][1] - 0.5:.4f}, not {row}")
            if (m["textures"]["diffuse"], m["textures"]["normal"], m["textures"]["smoothspec"]) != \
                    (at["diffuse"], at["normal"], at["smoothspec"]) or m["tile_flags"] != 0:
                bad.append(f"{p.name}: textures {m['textures']} tiles {m['tile_flags']}")
            ref = tmpl if kind == "design" else ttmpl
            skip = {"textures", "tile_flags", "uv_scale_u", "uv_scale_v", "uv_offset_u", "uv_offset_v",
                    "grayscale_to_palette_color", "grayscale_to_palette_scale"}
            if kind == "text":
                skip |= {"environment_mapping", "env_map_mask_scale", "alpha_test", "alpha_test_ref", "decal"}
                if not (m["alpha_test"] and m["alpha_test_ref"] == 128 and m["decal"] and not m["environment_mapping"]
                        and m["textures"]["envmap"] == ""):
                    bad.append(f"{p.name}: alpha test {m['alpha_test']} {m['alpha_test_ref']} decal {m['decal']} env "
                               f"{m['environment_mapping']} {m['textures']['envmap']!r}")
            elif m["alpha_test"] or m["decal"] or m["environment_mapping"]:
                bad.append(f"{p.name}: alpha test, decal or env map on")
            diff = [k for k in ref if not k.startswith("_") and k not in skip and ref[k] != m[k]]
            if diff:
                bad.append(f"{p.name}: differs from its template in {diff}")
    rep.check(not bad and len(names) == 72, f"the {len(names)} materials (12 designs over static_black.bgsm, 60 texts over "
                                            f"badge_{tkey}.bgsm): read back byte for byte, the cell's transform, the "
                                            f"palette at its row's centre, clamped; the texts alpha test 128, decal, no "
                                            f"chrome cube", "; ".join(bad[:8]))
    targets = sorted({t for s in opts["slots"] if s["key"] in ("Plate", "PlateText") for o in s["options"]
                      for _, t in (o["swap"] or []) if t.split("\\")[-1].startswith(("plate_", "text_"))})
    missing = [t for t in targets if not Path(args.out, "Materials", *t.split("\\")).exists()]
    rep.check(not missing and len(targets) == 72, f"every plate and text target of look_options.json's swaps there "
                                                  f"({len(targets)})", "; ".join(missing))
    # the text list
    texts = opts["plate_texts"]
    chars = meta["font"]["chars"]
    bad = [t["key"] for t in texts if not 5 <= len(t["text"]) <= 7 or any(ch not in chars for ch in t["text"])]
    sets = {s: [t["index"] for t in texts if t["set"] == s] for s in ("themed", "funny", "crude")}
    slot = next(s for s in opts["slots"] if s["key"] == "PlateText")
    crude = [o["index"] for o in slot["options"] if o.get("crude")]
    ok = (not bad and len(texts) == 60 and len({t["text"] for t in texts}) == 60 and len({t["key"] for t in texts}) == 60
          and [len(sets[k]) for k in ("themed", "funny", "crude")] == [32, 14, 14] and crude == sets["crude"]
          and crude == list(range(48, 62)) and all(meta["texts"][t["key"]]["text"] == t["text"] for t in texts))
    rep.check(ok, "the 60 texts: 5-7 characters each, in the plate font's set, unique, 32 themed, 14 funny and 14 crude "
                  "(slot options 48-61 flagged crude), plates.json's strings the table's",
              f"{bad} {[len(v) for v in sets.values()]} crude {crude[:3]}...")
    # the scan: brand words, US state names, their plates' slogans
    words = brand_words()
    states = state_words()
    corpus = []
    for d in opts["plates"]:
        corpus += [d["name"], d["key"]] + [str(d.get(k) or "") for k in ("art", "border", "top", "bottom", "emblem", "sticker")]
    corpus += [t["text"] for t in texts] + [t["name"] for t in texts] + [t["key"] for t in texts]
    corpus += [o["name"] for s in opts["slots"] if s["key"].startswith("Plate") for o in s["options"]]
    src = (HERE / "bike_art.py").read_text()
    sec = src[src.index("# --- the 12 designs"):src.index("PLATE_DRAW = {")]
    legends = [x for x in re.findall(r'"([^"\n]*)"', sec) if re.search(r"[A-Za-z]{2}", x)]
    corpus += legends
    text = " | ".join(corpus).lower()
    hits = [w for w in words if w in text] + [s for s in states if re.search(r"\b" + re.escape(s) + r"\b", text)] + \
           [s for s in SLOGANS if s in text]
    rep.check(not hits and len(legends) >= 30, f"the scan over {len(corpus)} names, legends and texts ({len(legends)} strings of "
                                               f"the designs' code): no brand word, US state name or state plate slogan",
              ", ".join(hits))
    found = [p.name for p in Path(args.out, "Textures").rglob("*") if p.is_file() and not str(p).replace("\\", "/").split(
        "Textures/")[-1].lower().startswith("cmb/")]
    rep.check(not found, "the guard: nothing under --out's Textures but CMB's own (no game texture copied)", ", ".join(found[:5]))
    print(f"look_plates: {rep.n} checks, {'all passed' if not rep.fails else f'{rep.fails} FAILED'}")
    return 1 if rep.fails else 0


# --- the sheets --------------------------------------------------------------------------------------------------

def lit(rgb, n, s=None):
    """A flat preview: diffuse x (ambient + a light from above-left) + a little specular."""
    L = np.array([-0.35, -0.55, 0.76])
    L /= np.linalg.norm(L)
    d = np.clip((n * L).sum(-1), 0, 1)[..., None]
    out = rgb * (0.45 + 0.65 * d)
    if s is not None:
        Hh = L + np.array([0, 0, 1.0])
        Hh /= np.linalg.norm(Hh)
        sp = np.clip((n * Hh).sum(-1), 0, 1) ** (4 + 40 * s[..., 1:2][..., 0]) * s[..., 0]
        out = out + 0.35 * sp[..., None]
    return np.clip(out, 0, 1)


def up(img, w, h):
    """Bilinear resize (numpy) of (H, W, C) float."""
    yy, xx = np.mgrid[0:h, 0:w]
    return bilinear(img, (xx + 0.5) / w, (yy + 0.5) / h)


def unpack_n(img):
    n = img[..., :2].astype(np.float64) / 255 * 2 - 1
    return np.dstack([n, np.sqrt(np.clip(1 - (n ** 2).sum(-1), 0, 1))])


class Atlases:
    def __init__(self, out, opts, level=0):
        tex = Path(out, *TEX)
        r = lambda n, k=level: W.read_dds(tex / n)[1][0][min(k, W.read_dds(tex / n)[0]["mips"] - 1)]
        self.d, self.n, self.s = r("plates_d.dds"), r("plates_n.dds"), r("plates_s.dds")
        self.td, self.tn, self.ts = r("plate_text_d.dds"), r("plate_text_n.dds"), r("plate_text_s.dds")
        self.pp = W.read_dds(tex / "plate_p.dds")[1][0][0][..., :3].astype(np.float64) / 255
        self.tp = W.read_dds(tex / "plate_text_p.dds")[1][0][0][..., :3].astype(np.float64) / 255
        self.level = level
        self.opts = opts
        self.n_up = unpack_n(up(self.n.astype(np.float64), self.d.shape[1], self.d.shape[0]))
        self.s_up = up(self.s.astype(np.float64) / 255, self.d.shape[1], self.d.shape[0])
        self.tn_up = unpack_n(up(self.tn.astype(np.float64), self.td.shape[1], self.td.shape[0]))
        self.ts_up = up(self.ts.astype(np.float64) / 255, self.td.shape[1], self.td.shape[0])
        self.cache = {}

    def plate(self, d, bg, text, ink, scale=1.0):
        """The face (226 x 496 at level 0, scaled by `scale`) of design d on background bg with text (a plate_texts
        entry or None) in ink, lit flat."""
        o = self.opts
        dat, tat, face = o["plate_atlas"]["designs"], o["plate_atlas"]["texts"], o["plate_atlas"]["face"]
        k = 1 << self.level
        c, r = d["cell"]
        (cw, ch), (ox, oy), (dw, dh) = dat["cell"], dat["offset"], dat["draw"]
        sl = (slice((r * ch + oy) // k, (r * ch + oy + dh) // k), slice((c * cw + ox) // k, (c * cw + ox + dw) // k))
        u = self.d[sl][..., 1].astype(int)
        rgb = self.pp[(d["index"] - 1) * 16 + bg][u]
        img = lit(rgb, self.n_up[sl], self.s_up[sl])
        if text is not None:
            tc, tr = text["cell"]
            (tcw, tch), (tox, toy), (tdw, tdh) = tat["cell"], tat["offset"], tat["draw"]
            tsl = (slice((tr * tch + toy) // k, (tr * tch + toy + tdh) // k), slice((tc * tcw + tox) // k, (tc * tcw + tox + tdw) // k))
            (u0, u1), (v0, v1) = face["text_band_u"], face["text_band_v"]
            H, Wd = img.shape[:2]
            x0, x1, y0, y1 = int(round(u0 * Wd)), int(round(u1 * Wd)), int(round(v0 * H)), int(round(v1 * H))
            key = (text["key"], x1 - x0, y1 - y0)
            if key not in self.cache:
                self.cache[key] = (up(self.td[tsl].astype(np.float64), x1 - x0, y1 - y0),
                                   up(self.tn_up[tsl], x1 - x0, y1 - y0), up(self.ts_up[tsl], x1 - x0, y1 - y0))
            cell, tn, ts = self.cache[key]
            trgb = lit(self.tp[ink][np.clip(np.rint(cell[..., 1]), 0, 255).astype(int)], tn, ts)
            a = (cell[..., 3] >= 127.5)[..., None]
            img[y0:y1, x0:x1] = np.where(a, trgb, img[y0:y1, x0:x1])
        if scale != 1.0:
            img = up(img, int(round(img.shape[1] * scale)), int(round(img.shape[0] * scale)))
        return img


def to8(img):
    """A preview (display values 0-1, the palettes' sRGB) as uint8."""
    return np.clip(np.rint(img * 255), 0, 255).astype(np.uint8)


def label(img, text, x=4, y=4, scale=2, colour=(255, 255, 255)):
    from look_render import draw_text
    draw_text(img, x, y, text.encode("ascii", "replace").decode(), scale, colour)


def grid(tiles, cols, pad=8, bg=24):
    th, tw = tiles[0].shape[:2]
    rows = (len(tiles) + cols - 1) // cols
    out = np.full((rows * (th + pad) + pad, cols * (tw + pad) + pad, 3), bg, np.uint8)
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        out[pad + r * (th + pad):pad + r * (th + pad) + t.shape[0], pad + c * (tw + pad):pad + c * (tw + pad) + t.shape[1]] = t
    return out


def save(img, path):
    from PIL import Image
    Image.fromarray(img).save(path)
    print(f"{path}: {img.shape[1]}x{img.shape[0]}")


def with_title(img, text):
    head = np.full((26, img.shape[1], 3), 24, np.uint8)
    label(head, text, 6, 6)
    return np.concatenate([head, img], 0)


def sheet(args, opts):
    out = Path(args.sheet)
    out.mkdir(parents=True, exist_ok=True)
    A = [Atlases(args.out, opts, k) for k in (0, 2, 3)]
    texts = {t["index"]: t for t in opts["plate_texts"]}
    cols = colours(opts)
    designs = [d for d in opts["plates"] if d["cell"] is not None]
    # 1: every design with its own text and colours, and at the riding view's mips 2 and 3 (nearest, x4 and x8)
    tiles = []
    for d in designs:
        t = texts.get(d["own_text"])
        a = to8(A[0].plate(d, d["own_back"], t, d["own_ink"]))
        b2 = to8(A[1].plate(d, d["own_back"], t, d["own_ink"]))
        b3 = to8(A[2].plate(d, d["own_back"], t, d["own_ink"]))
        b2 = np.repeat(np.repeat(b2, 2, 0), 2, 1)
        b3 = np.repeat(np.repeat(b3, 4, 0), 4, 1)
        small = np.concatenate([b2, np.full((b2.shape[0], 8, 3), 24, np.uint8),
                                np.pad(b3, ((0, b2.shape[0] - b3.shape[0]), (0, 0), (0, 0)), constant_values=24)], 1)
        tile = np.full((a.shape[0] + small.shape[0] + 34, max(a.shape[1], small.shape[1]), 3), 24, np.uint8)
        tile[26:26 + a.shape[0], :a.shape[1]] = a
        tile[34 + a.shape[0]:34 + a.shape[0] + small.shape[0], :small.shape[1]] = small
        label(tile, f"{d['index']} {d['name']}: {cols[d['own_back']]} / ink {cols[d['own_ink']]} / "
                    f"{t['text'].replace(chr(0x2665), '<3') if t else 'no text'}", 4, 6)
        tiles.append(tile)
    save(with_title(grid(tiles, 2), "THE 12 DESIGNS, OWN TEXT AND COLOURS (LEVEL 0; BELOW: MIP 2 AT X2 AND MIP 3 AT X4, "
                                    "THE RIDING VIEW'S TEXELS)"), out / "designs.png")
    # 2: every text on the standard plate in the standard's own colours, and on its theme's design in its preview ink
    # (its material's), both at half size; below them the theme's at mip 2 (x2)
    std = designs[0]
    by_key = {d["key"]: d for d in designs}
    tiles = []
    for t in opts["plate_texts"]:
        th = by_key[t["theme"]]
        a = to8(A[0].plate(std, std["own_back"], t, std["own_ink"], 0.5))
        b = to8(A[0].plate(th, th["own_back"], t, t["preview_ink"], 0.5))
        c = to8(A[1].plate(th, th["own_back"], t, t["preview_ink"]))
        c = np.repeat(np.repeat(c, 2, 0), 2, 1)[:a.shape[0], :a.shape[1]]
        tile = np.full((a.shape[0] * 2 + 30, a.shape[1] * 2 + 6, 3), 24, np.uint8)
        tile[24:24 + a.shape[0], :a.shape[1]] = a
        tile[24:24 + b.shape[0], a.shape[1] + 6:a.shape[1] + 6 + b.shape[1]] = b
        tile[28 + a.shape[0]:28 + a.shape[0] + c.shape[0], a.shape[1] + 6:a.shape[1] + 6 + c.shape[1]] = c
        label(tile, f"{t['index']} {t['text'].replace(chr(0x2665), '<3')} ({t['set']}; {t['theme']}, ink "
                    f"{cols[t['preview_ink']]})", 4, 5)
        tiles.append(tile)
    save(with_title(grid(tiles, 3), "THE 60 TEXTS: ON THE COMMONWEALTH STANDARD IN ITS OWN INK (LEFT), ON THEIR THEME'S "
                                    "DESIGN IN THEIR PREVIEW INK (RIGHT; BELOW IT MIP 2 AT X2)"), out / "texts.png")
    # 3: every design on every background, its own text in its own ink (the legends swapped where needed)
    rows = []
    for d in designs:
        t = texts.get(d["own_text"]) or texts[2]
        tiles = [to8(A[0].plate(d, bg, t, d["own_ink"], 0.25)) for bg in range(16)]
        row = grid(tiles, 16, pad=4)
        head = np.full((row.shape[0], 150, 3), 24, np.uint8)
        label(head, d["key"].upper(), 4, row.shape[0] // 2 - 6)
        rows.append(np.concatenate([head, row], 1))
    save(with_title(np.concatenate(rows, 0), "EVERY DESIGN ON EVERY BACKGROUND (COLUMNS 0-15), ITS OWN TEXT AND INK"),
         out / "backgrounds.png")
    # 4: the 16 x 16 legibility grid: ink (rows) on background (columns), under 3:1 crossed
    tiles = []
    for ink in range(16):
        for bg in range(16):
            tile = to8(A[0].plate(designs[2], bg, texts[2], ink, 0.25))
            cr = contrast(cols[ink], cols[bg])
            if cr < CONTRAST:
                for i in range(tile.shape[0]):
                    j = int(i * tile.shape[1] / tile.shape[0])
                    tile[i, max(0, j - 1):j + 2] = (255, 0, 255)
            label(tile, f"{cr:.1f}", 3, 3, 1, (255, 0, 255) if cr < CONTRAST else (128, 128, 128))
            tiles.append(tile)
    names = ", ".join(f"{i} {c['name']}" for i, c in enumerate(opts["plate_colours"]))
    img = with_title(grid(tiles, 16, pad=4), "LEGIBILITY: INK (ROWS 0-15) ON BACKGROUND (COLUMNS 0-15) ON THE BLANK PLATE; "
                                            "CROSSED UNDER 3:1")
    foot = np.full((24, img.shape[1], 3), 24, np.uint8)
    label(foot, names, 6, 6, 1)
    save(np.concatenate([img, foot], 0), out / "legibility.png")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--art", type=Path, required=True, help="bike_art.py --plates' output")
    ap.add_argument("--out", type=Path, required=True, help="a Data folder's layout (Textures, Materials)")
    ap.add_argument("--look-options", type=Path, default=HERE.parent / "esp-generator" / "look_options.json")
    ap.add_argument("--old-stage", type=Path, help="2026-11-07a's stage (shapes/ and uv/static_black.npz)")
    ap.add_argument("--stage", type=Path, help="this build's stage (shapes/ and uv/static_plate.npz), when exported")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--sheet", type=Path, help="write the contact sheets into this folder")
    args = ap.parse_args()
    opts = json.loads(args.look_options.read_text())
    if args.sheet:
        return sheet(args, opts)
    if not args.old_stage:
        ap.error("--old-stage is needed (the stock re-sample)")
    if args.check:
        return check(args, opts)
    return write(args, opts)


if __name__ == "__main__":
    sys.exit(main())
