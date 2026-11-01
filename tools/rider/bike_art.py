#!/usr/bin/env python3
"""The bike's own art: the speedometer's face and needle, the tail and brake lenses' pattern, the
tank badge (a winged wheel, no text), the brake discs and the mirrors' sky. Drawn here from shapes, so no source
image or font file is needed (the numerals are a stroke font of our own), and laid out to the UV
layouts bike_pieces.py gives the pieces (its DIAL_*, NEEDLE_PATCH, LENS_*, BADGE_* constants).

  python3 -I bike_art.py --out <stage>/art [--size-dial 512] [--size-lens 256] [--size-badge 512] [--size-cube 512]
      [--size-disc 1024]

Writes PNGs (8-bit, numpy and zlib only) and art.json, which says for each file what its channels
hold. The texture stage (bike_textures.py) turns them into DDS and the materials point at them:

  front_dial_d.png        the face: black, cream numerals 0-80 every 10 mph, major (10) medium (5) and
                          minor (1) ticks on an arc, "MPH"; the hub cap's colours in the middle and
                          the needle's in the top right corner (front_dial, front_needle; front_dialglow
                          shares it)
  front_dial_s.png        R specular, G smoothness (the face semi-gloss, as if behind a lens)
  front_dial_n.png        flat (the face is printed, not embossed)
  front_dialglow_g.png    the glow map of the lit copy: the numerals, ticks, arc and MPH only
  front_dial_g.png        (optional) a glow map lighting only the needle's patch, for a lit needle
  static_badge_d.png      RGBA: a chrome winged wheel with black enamel, alpha its outline (for an
                          alpha-tested badge; the RGB outside is the stock paint, for a material
                          without alpha), and a roundel for the rear fender's small emblem
  static_badge_n.png      its relief (chrome raised, enamel sunk)
  static_badge_s.png      R specular, G smoothness
  rear_tail_d/g.png       the running light's lens: Fresnel rings round LED cells, its glow map
  rear_brake_d/g.png      the brake light's, brighter and fuller
  wheel_disc_d/n/s.png    (since the 2026-11-01a build) the brake discs, both: machined steel band with a
                          polished pad track and a faint heat ring, a satin carrier, a bright chamfer
                          round every hole, the rim and the bore; concentric turning grooves in _n
  mirror_cube_<f>.png     the mirrors' sky (f = px nx py ny pz nz: the six faces in Direct3D order and
                          orientation, +Y up): a clear sky, a sun with its glare, hazy hills on the
                          horizon, dark ground; continuous across the faces
  mirror_cube_zup_<f>.png the same sky with +Z up (a one-file swap if the game shows it sideways)
  cube.json               the cube's conventions

Normal maps are tangent space in Fallout 4's (Direct3D) convention: red along +u, green along +v
(down the image), blue out of the surface; written as they are (no green flip). Colours are 8-bit
as displayed; specular/smoothness maps are linear values.
"""

import argparse
import json
import math
import struct
import sys
import zlib
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bike_pieces as bp  # noqa: E402

# --- PNG ------------------------------------------------------------------------------------------


def write_png(path, img):
    """An 8-bit PNG from uint8 (h, w) grey, (h, w, 3) RGB or (h, w, 4) RGBA."""
    a = np.ascontiguousarray(img, dtype=np.uint8)
    if a.ndim == 2:
        a = a[:, :, None]
    h, w, c = a.shape
    ctype = {1: 0, 3: 2, 4: 6}[c]
    raw = b"".join(b"\x00" + a[y].tobytes() for y in range(h))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    Path(path).write_bytes(png)


def to8(x):
    return np.clip(np.round(np.asarray(x) * 255.0), 0, 255).astype(np.uint8)


# --- drawing: coverage from signed distances (anti-aliased over about a pixel) -------------------------


class Canvas:
    """Pixel grid helpers: coordinates in pixels, x right, y down, pixel centres at +0.5."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.x = np.arange(w)[None, :] + 0.5
        self.y = np.arange(h)[:, None] + 0.5

    def window(self, x0, y0, x1, y1):
        """Slices of the grid covering the box (clamped), and its coordinate arrays."""
        i0, i1 = max(0, int(math.floor(y0)) - 2), min(self.h, int(math.ceil(y1)) + 2)
        j0, j1 = max(0, int(math.floor(x0)) - 2), min(self.w, int(math.ceil(x1)) + 2)
        return (slice(i0, i1), slice(j0, j1)), self.x[:, j0:j1], self.y[i0:i1, :]


def coverage(d, aa=0.8):
    """Signed distance (negative inside) -> coverage."""
    return np.clip(0.5 - d / aa, 0.0, 1.0)


def seg_dist(x, y, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = np.clip(((x - ax) * dx + (y - ay) * dy) / max(L2, 1e-12), 0.0, 1.0)
    return np.hypot(x - ax - t * dx, y - ay - t * dy)


def polyline_cov(cv, pts, width, closed=False, aa=0.8):
    """Coverage of a stroke of `width` along a polyline (round joins and caps), full canvas."""
    pts = np.asarray(pts, dtype=np.float64)
    out = np.zeros((cv.h, cv.w))
    r = width / 2
    segs = list(zip(pts[:-1], pts[1:])) + ([(pts[-1], pts[0])] if closed else [])
    lo, hi = pts.min(0) - r - 2, pts.max(0) + r + 2
    sl, x, y = cv.window(lo[0], lo[1], hi[0], hi[1])
    d = np.full((sl[0].stop - sl[0].start, sl[1].stop - sl[1].start), np.inf)
    for a, b in segs:
        d = np.minimum(d, seg_dist(x, y, a, b))
    out[sl] = coverage(d - r, aa)
    return out


def polygon_sdf(cv, poly):
    """Signed distance to a closed polygon (negative inside), full canvas (inf far outside its box)."""
    p = np.asarray(poly, dtype=np.float64)
    lo, hi = p.min(0) - 12, p.max(0) + 12
    sl, x, y = cv.window(lo[0], lo[1], hi[0], hi[1])
    d = np.full((sl[0].stop - sl[0].start, sl[1].stop - sl[1].start), np.inf)
    inside = np.zeros(d.shape, dtype=bool)
    n = len(p)
    for k in range(n):
        a, b = p[k], p[(k + 1) % n]
        d = np.minimum(d, seg_dist(x, y, a, b))
        cond = ((a[1] > y) != (b[1] > y))
        xint = a[0] + (y - a[1]) * (b[0] - a[0]) / np.where(b[1] != a[1], b[1] - a[1], 1e-12)
        inside ^= cond & (x < xint)
    full = np.full((cv.h, cv.w), 1e3)
    full[sl] = np.where(inside, -d, d)
    return full


def blend(img, cov, colour):
    c = np.asarray(colour, dtype=np.float64).reshape(1, 1, -1)
    img[:] = img * (1.0 - cov[..., None]) + c * cov[..., None]


def box_blur(a, r):
    """Separable box blur of radius r (pixels), edges clamped."""
    if r < 1:
        return a
    r = int(r)
    out = a.astype(np.float64)
    for axis in (0, 1):
        pad = [(0, 0)] * out.ndim
        pad[axis] = (r + 1, r)
        p = np.pad(out, pad, mode="edge")
        c = np.cumsum(p, axis=axis)
        hi = np.take(c, np.arange(2 * r + 1, p.shape[axis]), axis=axis)
        lo = np.take(c, np.arange(0, p.shape[axis] - 2 * r - 1), axis=axis)
        out = (hi - lo) / (2 * r + 1)
    return out


def normals_from_height(h, strength):
    """A Direct3D tangent-space normal map (R +u, G +v down the image, B out) from a height field."""
    gy, gx = np.gradient(h)
    n = np.stack([-gx * strength, -gy * strength, np.ones_like(h)], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return to8(n * 0.5 + 0.5)


# --- a stroke font: numerals, M, P, H (a unit-height box, y down; strokes are polylines) -------------------


def _arc(cx, cy, r, a0, a1, n=None):
    """Points on an arc, angles in degrees measured from +x toward +y (down): increasing = clockwise on screen."""
    n = n or max(6, int(abs(a1 - a0) / 9))
    t = np.radians(np.linspace(a0, a1, n + 1))
    return list(zip(cx + r * np.cos(t), cy + r * np.sin(t)))


def _glyphs():
    g = {}
    g["0"] = (0.60, [_arc(0.30, 0.30, 0.30, 180, 360) + [(0.60, 0.70)] + _arc(0.30, 0.70, 0.30, 0, 180) + [(0.0, 0.30)]])
    g["1"] = (0.46, [[(0.08, 0.20), (0.34, 0.0), (0.34, 1.0)]])
    g["2"] = (0.60, [_arc(0.30, 0.29, 0.29, 195, 385) + [(0.02, 1.0), (0.60, 1.0)]])
    g["3"] = (0.60, [[(0.04, 0.0), (0.56, 0.0), (0.26, 0.40)] + _arc(0.29, 0.69, 0.30, 280, 520)])
    g["4"] = (0.62, [[(0.46, 1.0), (0.46, 0.0), (0.0, 0.70), (0.62, 0.70)]])
    g["5"] = (0.60, [[(0.56, 0.0), (0.09, 0.0), (0.05, 0.44)] + _arc(0.30, 0.68, 0.31, 230, 500)])
    g["6"] = (0.60, [_arc(0.31, 0.30, 0.30, 315, 180) + [(0.0, 0.70)] + _arc(0.30, 0.70, 0.30, 180, 540)])
    g["7"] = (0.60, [[(0.0, 0.0), (0.60, 0.0), (0.20, 1.0)]])
    g["8"] = (0.60, [_arc(0.30, 0.255, 0.255, 0, 360), _arc(0.30, 0.725, 0.275, 0, 360)])
    six = g["6"][1]
    g["9"] = (0.60, [[(0.60 - x, 1.0 - y) for x, y in line] for line in six])
    g["M"] = (0.72, [[(0.0, 1.0), (0.0, 0.0), (0.36, 0.62), (0.72, 0.0), (0.72, 1.0)]])
    g["P"] = (0.56, [[(0.0, 1.0), (0.0, 0.0), (0.28, 0.0)] + _arc(0.28, 0.26, 0.26, 270, 450) + [(0.0, 0.52)]])
    g["H"] = (0.58, [[(0.0, 0.0), (0.0, 1.0)], [(0.58, 0.0), (0.58, 1.0)], [(0.0, 0.5), (0.58, 0.5)]])
    return g


GLYPHS = _glyphs()


def text_cov(cv, text, cx, cy, height, stroke, spacing=0.22):
    """Coverage of `text` centred at (cx, cy), cap height `height` px, stroke width `stroke` px."""
    widths = [GLYPHS[ch][0] for ch in text]
    total = (sum(widths) + spacing * (len(text) - 1)) * height
    x = cx - total / 2
    out = np.zeros((cv.h, cv.w))
    for ch, wdt in zip(text, widths):
        for line in GLYPHS[ch][1]:
            pts = [(x + px * height, cy - height / 2 + py * height) for px, py in line]
            out = np.maximum(out, polyline_cov(cv, pts, stroke))
        x += (wdt + spacing) * height
    return out


# --- the speedometer ------------------------------------------------------------------------------------

CREAM = (0.95, 0.91, 0.80)
# The numerals: every 10 mph, centred NUMERAL_R of the face's radius out, NUMERAL_H tall (the dial is
# about 7.4 units across, 180-240 pixels on screen from the rider's head at 1080p-1440p: they come out
# 14-17 pixels tall, with 20 pixels or more between 30, 40 and 50 at the top)
NUMERAL_R = 0.575
NUMERAL_H = 0.150
FACE = (0.045, 0.045, 0.052)


def dial_layout(size):
    """Positions in pixels: centre, the face's radius."""
    return size / 2, size / 2, bp.DIAL_ART_R * size


def mph_angle(mph):
    """Clockwise from up, degrees, as the rider sees the dial."""
    return bp.DIAL_ZERO + bp.DIAL_PER_MPH * mph


def dial_marks(cv, size):
    """Coverage of the ticks, arc, numerals and MPH (each a separate map) on the dial."""
    cx, cy, R = dial_layout(size)
    ticks = np.zeros((cv.h, cv.w))
    minor = np.zeros((cv.h, cv.w))
    for mph in range(0, bp.DIAL_TOP + 1):
        a = math.radians(mph_angle(mph))
        s, c = math.sin(a), -math.cos(a)
        if mph % 10 == 0:
            r0, r1, w, tgt = 0.715, 0.905, 0.040, ticks
        elif mph % 5 == 0:
            r0, r1, w, tgt = 0.785, 0.905, 0.026, ticks
        else:
            r0, r1, w, tgt = 0.845, 0.905, 0.012, minor
        cov = polyline_cov(cv, [(cx + s * r0 * R, cy + c * r0 * R), (cx + s * r1 * R, cy + c * r1 * R)], w * R, aa=0.9)
        np.maximum(tgt, cov, out=tgt)
    arc = [(cx + math.sin(math.radians(t)) * 0.912 * R, cy - math.cos(math.radians(t)) * 0.912 * R)
           for t in np.linspace(mph_angle(0), mph_angle(bp.DIAL_TOP), 121)]
    np.maximum(ticks, polyline_cov(cv, arc, 0.016 * R), out=ticks)
    nums = np.zeros((cv.h, cv.w))
    for mph in range(0, bp.DIAL_TOP + 1, 10):
        a = math.radians(mph_angle(mph))
        r = NUMERAL_R * R
        np.maximum(nums, text_cov(cv, str(mph), cx + math.sin(a) * r, cy - math.cos(a) * r, NUMERAL_H * R, 0.031 * R), out=nums)
    label = text_cov(cv, "MPH", cx, cy + 0.40 * R, 0.068 * R, 0.0125 * R, spacing=0.28)
    return ticks, minor, nums, label


def needle_patch_px(size):
    u0, v0, u1, v1 = bp.NEEDLE_PATCH
    return u0 * size, v0 * size, u1 * size, v1 * size


def draw_dial(size):
    cv = Canvas(size, size)
    cx, cy, R = dial_layout(size)
    r = np.hypot(cv.x - cx, cv.y - cy) / R
    img = np.zeros((size, size, 3))
    # the face: near black, a touch lighter toward the middle, darker under the bezel
    base = np.array(FACE)
    img[:] = base * (1.0 + 0.35 * np.clip(1 - r, 0, 1) ** 1.5)[..., None]
    blend(img, coverage((0.955 - r) * R), (0.02, 0.02, 0.022))
    ticks, minor, nums, label = dial_marks(cv, size)
    blend(img, minor, tuple(0.78 * c for c in CREAM))
    blend(img, ticks, CREAM)
    blend(img, nums, CREAM)
    blend(img, label, tuple(0.85 * c for c in CREAM))
    # the hub cap's colours: satin black with a bright rim
    rh = bp.HUB_R / bp.DIAL_R_MODEL
    blend(img, coverage((r - rh * 1.08) * R), (0.10, 0.10, 0.11))
    blend(img, coverage((r - rh * 0.86) * R), (0.06, 0.06, 0.065))
    ring = coverage(np.abs(r - rh * 0.95) * R - 0.035 / bp.DIAL_R_MODEL * R)
    blend(img, ring, (0.55, 0.55, 0.58))
    # spec/smoothness
    spec = np.zeros((size, size, 3))
    spec[..., 0], spec[..., 1] = 0.24, 0.60
    marks = np.maximum.reduce([ticks, minor, nums, label])
    blend(spec, marks, (0.16, 0.45, 0.0))
    blend(spec, coverage((r - rh * 1.08) * R), (0.45, 0.75, 0.0))
    blend(spec, ring, (0.80, 0.85, 0.0))
    # the needle's patch, top right: u along it (counterweight .. tip), v across
    x0, y0, x1, y1 = needle_patch_px(size)
    fu = np.clip((cv.x - x0) / (x1 - x0), 0, 1) * np.ones_like(cv.y)
    fv = np.clip((cv.y - y0) / (y1 - y0), 0, 1) * np.ones_like(cv.x)
    pad_u = 0.06
    fu_n = (fu - pad_u) / (1 - 2 * pad_u)   # 0 at the counterweight's end, 1 at the tip
    s = -bp.NEEDLE_TAIL * bp.DIAL_R_MODEL + fu_n * (bp.NEEDLE_LEN + bp.NEEDLE_TAIL) * bp.DIAL_R_MODEL
    across = np.abs(fv - 0.5) * 2   # 0 on the centre line, 1 at the widest
    blade = np.array([0.93, 0.25, 0.06])
    col = blade[None, None, :] * (1.0 - 0.35 * across[..., None] ** 2)
    col = col + np.array([0.07, 0.25, 0.18])[None, None, :] * np.clip(1 - across / 0.16, 0, 1)[..., None]   # the ridge's light
    tail = np.clip((-0.10 - s) / 0.12, 0, 1)[..., None]   # the counterweight: satin black
    col = col * (1 - tail) + np.array([0.07, 0.07, 0.075])[None, None, :] * tail
    inpatch = (cv.x >= x0 - 3) & (cv.x <= x1 + 3) & (cv.y >= y0 - 3) & (cv.y <= y1 + 3)
    img[inpatch] = col[inpatch]
    spec[inpatch] = (0.50, 0.75, 0.0)
    glow_needle = np.zeros((size, size))
    glow_needle[inpatch] = (1 - tail[..., 0])[inpatch] * (0.75 + 0.25 * (1 - across))[inpatch]
    # the lit copy's glow map: the marks, with a faint halo as if lit from behind
    g = np.maximum.reduce([ticks, nums, label, 0.85 * minor])
    halo = box_blur(box_blur(g, 3), 3)
    glow = np.clip(g + 0.22 * halo, 0, 1)
    flat = np.zeros((size, size, 3), dtype=np.uint8)
    flat[...] = (128, 128, 255)
    return to8(img), to8(spec), flat, to8(glow), to8(glow_needle)


# --- the tail and brake lenses ----------------------------------------------------------------------------


def draw_lens(size, brake):
    cv = Canvas(size, size)
    base = np.array([0.62, 0.05, 0.04]) if brake else np.array([0.45, 0.03, 0.03])
    img = np.zeros((size, size, 3)) + base * 0.8
    glow = np.zeros((size, size)) + (0.75 if brake else 0.55)

    def cell(cx, cy, rad, period):
        r = np.hypot(cv.x - cx, cv.y - cy)
        inside = coverage(r - rad)
        rings = 0.5 + 0.5 * np.cos(2 * math.pi * r / period)
        led = np.exp(-(r / (0.22 * rad)) ** 2)
        return inside, rings, led

    def apply(box, cells):
        u0, v0, u1, v1 = box
        x0, y0, x1, y1 = u0 * size, v0 * size, u1 * size, v1 * size
        inbox = coverage(polygon_sdf(cv, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]))
        edge = np.clip(np.minimum(np.minimum(cv.x - x0, x1 - cv.x), np.minimum(cv.y - y0, y1 - cv.y)) / (0.08 * size), 0, 1)
        lum = np.zeros((size, size))
        bright = np.zeros((size, size))
        for cx, cy, rad in cells:
            inside, rings, led = cell(cx, cy, rad, 0.055 * rad + 3.0)
            lum = np.maximum(lum, inside * (0.55 + 0.45 * rings))
            bright = np.maximum(bright, inside * led)
        lum = np.maximum(lum, 0.45 * inbox)
        col = base[None, None, :] * (0.65 + 0.55 * lum[..., None]) + np.array([0.35, 0.18, 0.12])[None, None, :] * bright[..., None]
        col *= (0.75 + 0.25 * edge)[..., None]
        img[:] = img * (1 - inbox[..., None]) + col * inbox[..., None]
        g = (0.60 if not brake else 0.82) + (0.22 if not brake else 0.12) * lum + 0.25 * bright
        g *= (0.85 + 0.15 * edge)
        glow[:] = glow * (1 - inbox) + np.clip(g, 0, 1) * inbox

    u0, v0, u1, v1 = bp.LENS_TAIL_BOX
    w, h = (u1 - u0) * size, (v1 - v0) * size
    cells = [(u0 * size + w * (k + 0.5) / 3, v0 * size + h / 2, min(w / 6, h / 2) * 0.92) for k in range(3)]
    apply(bp.LENS_TAIL_BOX, cells)
    u0, v0, u1, v1 = bp.LENS_ROUND_BOX
    apply(bp.LENS_ROUND_BOX, [((u0 + u1) / 2 * size, (v0 + v1) / 2 * size, (u1 - u0) / 2 * size * 0.94)])
    return to8(img), to8(glow)


# --- the badge --------------------------------------------------------------------------------------------

PAINT = (0x7A / 255, 0x11 / 255, 0x18 / 255)
CHROME = (0.36, 0.36, 0.38)     # dark diffuse: the chrome cube map gives the shine
ENAMEL = (0.035, 0.035, 0.04)


def feather(cx, cy, side, k, size):
    """The k-th feather (0 top) of the wing on `side` (+1 right, -1 left) as a polygon (pixels)."""
    S = size / 512
    L = [154, 145, 130, 110, 86][k] * S
    lift = [30, 20, 12, 6, 2][k] * S
    root_y = cy + (-34 + 16.5 * k) * S
    root_x = cx + side * 52 * S
    th0 = [12, 11.5, 11, 10.5, 10][k] * S
    pts_top, pts_bot = [], []
    n = 24
    for i in range(n + 1):
        t = i / n
        x = root_x + side * L * t
        y = root_y - lift * t ** 1.6
        th = th0 * (1 - 0.45 * t)
        pts_top.append((x, y - th))
        pts_bot.append((x, y + th))
    tip_x = root_x + side * (L + 12 * S)
    tip_y = root_y - lift - 6 * S
    # an angled tip: the top edge runs out to the point, the bottom edge cuts back up to it
    poly = pts_top + [(tip_x, tip_y)] + pts_bot[::-1]
    return poly


def draw_badge(size):
    cv = Canvas(size, size)
    S = size / 512
    cx, cy = size / 2, size / 2 + 12 * S   # a little under the middle: the tank panels' top edge arches down to their ends
    chrome_sdf = np.full((size, size), 1e3)
    groove = np.zeros((size, size))   # 1 where the enamel shows inside the chrome
    height = np.zeros((size, size))
    for side in (-1, 1):
        for k in range(5):
            sd = polygon_sdf(cv, feather(cx, cy, side, k, size))
            chrome_sdf = np.minimum(chrome_sdf, sd)
            inlay = coverage(sd + 3.6 * S)
            groove = np.maximum(groove, inlay)
            height = np.maximum(height, np.clip(-sd / (2.2 * S), 0, 1) * (1 - 0.55 * inlay))
    # a bar behind the wheel joining the wings' roots
    bar = polygon_sdf(cv, [(cx - 70 * S, cy - 40 * S), (cx + 70 * S, cy - 40 * S), (cx + 70 * S, cy + 40 * S), (cx - 70 * S, cy + 40 * S)])
    chrome_sdf = np.minimum(chrome_sdf, bar)
    # the wheel on top: a dark gap ring round it, the chrome rim, black field, spokes, hub
    wr = bp.BADGE_WHEEL_R * size
    rr = np.hypot(cv.x - cx, cv.y - cy)
    gap = coverage(rr - (wr + 4 * S)) * (1 - coverage(rr - wr))
    wheel_rim = coverage(rr - wr) * (1 - coverage(rr - (wr - 11 * S)))
    field = coverage(rr - (wr - 11 * S))
    spokes = np.zeros((size, size))
    for k in range(10):
        a = 2 * math.pi * k / 10 + math.pi / 10
        spokes = np.maximum(spokes, polyline_cov(cv, [(cx + math.cos(a) * 13 * S, cy + math.sin(a) * 13 * S),
                                                       (cx + math.cos(a) * (wr - 10 * S), cy + math.sin(a) * (wr - 10 * S))], 5.0 * S))
    hub = coverage(rr - 15 * S)
    hub_dot = coverage(rr - 5 * S)
    # the roundel for the rear fender's emblem
    ru, rv, rrad = bp.BADGE_ROUNDEL
    rcx, rcy, R2 = ru * size, rv * size, rrad * size
    r2 = np.hypot(cv.x - rcx, cv.y - rcy)
    roundel = coverage(r2 - R2)
    r_ring = roundel * (1 - coverage(r2 - (R2 - 8 * S)))
    r_rim = coverage(r2 - 0.70 * R2) * (1 - coverage(r2 - 0.58 * R2))
    r_spokes = np.zeros((size, size))
    for k in range(8):
        a = 2 * math.pi * k / 8
        r_spokes = np.maximum(r_spokes, polyline_cov(cv, [(rcx + math.cos(a) * 0.14 * R2, rcy + math.sin(a) * 0.14 * R2),
                                                           (rcx + math.cos(a) * 0.60 * R2, rcy + math.sin(a) * 0.60 * R2)], 3.6 * S))
    r_hub = coverage(r2 - 0.17 * R2)
    # the colour, alpha, height
    wing = coverage(chrome_sdf)
    alpha = np.maximum.reduce([wing, coverage(rr - (wr + 4 * S)), roundel])
    img = np.zeros((size, size, 3)) + np.array(PAINT)
    blend(img, wing, CHROME)
    blend(img, groove * wing, ENAMEL)
    blend(img, gap, ENAMEL)
    blend(img, field, ENAMEL)
    blend(img, wheel_rim, CHROME)
    blend(img, spokes * field, CHROME)
    blend(img, hub, CHROME)
    blend(img, hub_dot, ENAMEL)
    blend(img, roundel, ENAMEL)
    blend(img, r_ring, CHROME)
    blend(img, r_rim, CHROME)
    blend(img, r_spokes, CHROME)
    blend(img, r_hub, CHROME)
    metal = np.maximum.reduce([wing * (1 - groove), wheel_rim, spokes * field, hub * (1 - hub_dot), r_ring, r_rim, r_spokes, r_hub])
    # height: chrome raised (the rims most), enamel low
    h = 0.35 * alpha + 0.65 * metal
    h = h + 0.25 * wheel_rim + 0.2 * r_ring + 0.2 * hub
    h = box_blur(h, max(1, int(round(1.2 * S))))
    nrm = normals_from_height(h, 2.2)
    spec = np.zeros((size, size, 3))
    blend(spec, alpha, (0.30, 0.78, 0.0))     # glossy enamel
    blend(spec, metal, (0.92, 0.92, 0.0))     # polished chrome
    rgba = np.dstack([to8(img), to8(alpha)])
    return rgba, nrm, to8(spec)


# --- the mirrors' sky ------------------------------------------------------------------------------------

# --- the brake discs (since the 2026-11-01a build) -----------------------------------------------------------------
# One art for both discs (bike_pieces.disc_pieces: the layout scales with the outer radius; the faces' UVs planar over
# DISC_ART_R of it each way). Sizes below in units of the outer radius unless named units (DISC_UNIT: the two discs'
# mean outer radius, 13.04 game units, turns those into the art's).
DISC_UNIT = 13.04
DISC_STEEL = (0x8A / 255, 0x8D / 255, 0x92 / 255)    # the friction band: machined steel
DISC_CARRIER = (0x4A / 255, 0x4C / 255, 0x50 / 255)  # the carrier: satin
DISC_PAD = (0.15, 0.85, 0.06)          # the polished pad track across the band (from, to) and its extra brightness
DISC_HEAT = (0.10, 0.08)               # the heat ring's place across the band and its strength at most (blue-straw)
DISC_CHAMFER = 0.06                    # units: the bright chamfer round every hole, the rim and the bore (+12 %)
DISC_GROOVE = (0.18, 4.0)              # units, degrees: the concentric turning grooves' pitch and slope
DISC_SPEC = {"band": (0.80, 0.62), "pad": (0.80, 0.72), "carrier": (0.40, 0.45)}   # _s R specular, G smoothness


def draw_disc(size):
    """The discs' _d (RGB), _n (tangent space, Direct3D) and _s (R specular, G smoothness) at size x size."""
    R = bp.DISC_ART_R
    u = (np.arange(size) + 0.5) / size
    dy = np.broadcast_to((u[None, :] - 0.5) * 2 * R, (size, size))      # u = 0.5 + dy / (2 R_art)
    dz = np.broadcast_to(-(u[:, None] - 0.5) * 2 * R, (size, size))     # v = 0.5 - dz / (2 R_art), v down the image
    r = np.hypot(dy, dz)
    band0, hub = bp.DISC_BAND, bp.DISC_HUB_REF
    px = 2 * R / size                                   # one pixel, in outer radii
    ch = DISC_CHAMFER / DISC_UNIT
    across = np.clip((r - band0) / (1 - band0), 0, 1)
    band = r >= band0
    # the distance to the nearest edge a chamfer runs along (holes, windows, the rim, the bore) and the way to it
    edge = np.minimum(np.abs(1.0 - r), np.abs(r - hub))
    toward = np.where((np.abs(1.0 - r) < np.abs(r - hub))[..., None],
                      np.stack([dy, dz], -1) / np.maximum(r, 1e-9)[..., None],
                      -np.stack([dy, dz], -1) / np.maximum(r, 1e-9)[..., None])
    inside = (r > 1.0) | (r < hub)                      # off the face (the rim's and the bore's walls)
    for kind, ang, rr, rho in bp.disc_layout(1.0):
        hy, hz = rr * math.cos(ang), rr * math.sin(ang)
        d = np.hypot(dy - hy, dz - hz)
        e = np.abs(d - rho)
        nearer = e < edge
        dirs = np.stack([hy - dy, hz - dz], -1) / np.maximum(d, 1e-9)[..., None]   # toward the hole's centre
        toward = np.where(nearer[..., None], dirs, toward)
        edge = np.where(nearer, e, edge)
        inside |= d < rho
    # _d
    base = np.where(band[..., None], np.array(DISC_STEEL), np.array(DISC_CARRIER))
    pad = band & (across >= DISC_PAD[0]) & (across <= DISC_PAD[1])
    soft = smooth01((across - DISC_PAD[0]) / 0.04) * smooth01((DISC_PAD[1] - across) / 0.04) * band
    col = base * (1 + DISC_PAD[2] * soft[..., None])
    heat = np.exp(-0.5 * ((across - DISC_HEAT[0]) / 0.05) ** 2) * band * DISC_HEAT[1]
    straw_blue = np.array([0.62, 0.55, 0.78])
    col = col * (1 - heat[..., None]) + straw_blue * heat[..., None] * col.mean(-1, keepdims=True) / straw_blue.mean()
    cham = np.clip((ch - edge) / px + 0.5, 0, 1) * ~inside
    col = col * (1 + 0.12 * cham[..., None])
    col = np.where(inside[..., None], np.array(DISC_STEEL) * 0.82, col)   # the walls: the drilled steel, darker
    # _n: concentric grooves (a sine of the radius) on the faces, the chamfer a bevel toward its edge
    pitch, slope = DISC_GROOVE[0] / DISC_UNIT, math.tan(math.radians(DISC_GROOVE[1]))
    g = slope * np.cos(2 * math.pi * r / pitch) * ~inside                 # dh/dr over the slope's amplitude
    ny_, nz_ = -g * dy / np.maximum(r, 1e-9), -g * dz / np.maximum(r, 1e-9)
    bevel = math.tan(math.radians(30.0)) * cham
    ny_ = ny_ + bevel * toward[..., 0]
    nz_ = nz_ + bevel * toward[..., 1]
    # tangent space: +u along +dy, +v (down the image) along -dz; a normal tilted toward +dz leans toward -v
    n = np.stack([ny_, -nz_, np.ones_like(r)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    # _s
    spec = np.where(band, DISC_SPEC["band"][0], DISC_SPEC["carrier"][0])
    smooth = np.where(band, DISC_SPEC["band"][1], DISC_SPEC["carrier"][1])
    smooth = smooth + (DISC_SPEC["pad"][1] - DISC_SPEC["band"][1]) * soft
    s = np.stack([spec, smooth, np.zeros_like(r)], -1)
    return to8(np.clip(col, 0, 1)), to8(n * 0.5 + 0.5), to8(s), int(pad.sum())


def smooth01(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


SUN = (35.0, 40.0)   # elevation, azimuth (degrees; azimuth from the first horizontal axis toward the second)


def _hash3(ix, iy, iz):
    h = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791)
    h = (h ^ (h >> 13)) * 1274126177
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def noise3(p):
    """Smooth value noise in 3-D (continuous, so continuous across the cube's faces)."""
    p = np.asarray(p)
    i = np.floor(p).astype(np.int64)
    f = p - i
    u = f * f * (3 - 2 * f)
    out = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (u[..., 0] if dx else 1 - u[..., 0]) * (u[..., 1] if dy else 1 - u[..., 1]) * (u[..., 2] if dz else 1 - u[..., 2])
                out = out + w * _hash3(i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz)
    return out


def fbm(p, octaves=5):
    total, amp, norm = 0.0, 0.5, 0.0
    for _ in range(octaves):
        total = total + amp * noise3(p)
        norm += amp
        p = p * 2.03 + 17.1
        amp *= 0.5
    return total / norm


def sky_colour(up, e1, e2):
    """The environment's colour for unit directions given by their components along the up axis
    and the two horizontal axes, (..., ) arrays -> (..., 3) in 0..1."""
    el = np.arcsin(np.clip(up, -1, 1))
    az = np.arctan2(e2, e1)
    d = np.stack([e1, e2, up], axis=-1)
    se, sa = math.radians(SUN[0]), math.radians(SUN[1])
    sun = np.array([math.cos(se) * math.cos(sa), math.cos(se) * math.sin(sa), math.sin(se)])
    cosang = np.clip(d @ sun, -1, 1)
    ang = np.degrees(np.arccos(cosang))
    t = np.clip(el / (math.pi / 2), 0, 1)
    zenith = np.array([0.16, 0.36, 0.72])
    horizon = np.array([0.78, 0.82, 0.86])
    sky = horizon + (zenith - horizon) * (t[..., None] ** 0.42)
    # clouds: soft, low and in the middle of the sky, none at the zenith
    cl = fbm(d * np.array([3.0, 3.0, 7.0]) + 3.3)
    dens = np.clip((cl - 0.52) / 0.16, 0, 1) * np.clip(el / 0.06, 0, 1) * np.clip((1.1 - t) / 0.6, 0, 1)
    cloud_col = np.array([0.93, 0.93, 0.95]) * (0.85 + 0.15 * np.clip(cosang, 0, 1))[..., None]
    sky = sky * (1 - 0.85 * dens[..., None]) + cloud_col * (0.85 * dens[..., None])
    # the sun and its glare
    glare = 0.65 * np.exp(-ang / 3.0) + 0.22 * np.exp(-ang / 14.0)
    sky = sky + np.array([1.0, 0.93, 0.80]) * glare[..., None]
    disc = coverage((ang - 0.9) * 6.0)
    sky = sky * (1 - disc[..., None]) + np.array([1.0, 1.0, 0.97]) * disc[..., None]
    # hills on the horizon: a height from noise round the horizon (periodic in azimuth)
    hz = np.stack([np.cos(az) * 2.2, np.sin(az) * 2.2, np.zeros_like(az)], axis=-1)
    hill = math.radians(1.0) + math.radians(2.6) * fbm(hz + 11.0, 4) ** 1.5
    in_hill = (el >= 0) & (el < hill)
    hill_col = np.array([0.34, 0.37, 0.37]) * 0.75 + horizon * 0.25
    # ground: dark, a haze band under the horizon, patches
    g = np.clip(-el / (math.pi / 2), 0, 1)
    gpatch = fbm(d * 9.0 + 5.0, 4)
    ground = np.array([0.20, 0.18, 0.15]) * (1 - g[..., None]) ** 1.2 + np.array([0.05, 0.045, 0.04]) * g[..., None]
    ground = ground * (0.8 + 0.4 * gpatch[..., None])
    haze = np.exp(-(-el) / math.radians(2.5))
    ground = ground * (1 - 0.6 * haze[..., None]) + horizon * 0.62 * (0.6 * haze[..., None])
    out = np.where((el >= 0)[..., None], sky, ground)
    out = np.where(in_hill[..., None], hill_col * (0.9 + 0.2 * fbm(d * 30.0, 3)[..., None]), out)
    return np.clip(out, 0, 1)


FACES = ("px", "nx", "py", "ny", "pz", "nz")


def face_dirs(face, size):
    """Unit directions through each texel's centre of a Direct3D cube face (row 0 at the top)."""
    c = (np.arange(size) + 0.5) / size * 2 - 1
    uc = np.broadcast_to(c[None, :], (size, size))
    vc = np.broadcast_to(c[:, None], (size, size))
    one = np.ones((size, size))
    d = {"px": (one, -vc, -uc), "nx": (-one, -vc, uc), "py": (uc, one, vc),
         "ny": (uc, -one, -vc), "pz": (uc, -vc, one), "nz": (-uc, -vc, -one)}[face]
    d = np.stack(d, axis=-1)
    return d / np.linalg.norm(d, axis=-1, keepdims=True)


def cube_lookup(d, faces):
    """Sample a set of D3D faces (dict face -> (s, s, 3)) at directions d (n, 3), nearest texel."""
    d = np.asarray(d)
    ax = np.argmax(np.abs(d), axis=1)
    out = np.zeros((len(d), 3))
    size = next(iter(faces.values())).shape[0]
    for i in range(len(d)):
        x, y, z = d[i]
        a = ax[i]
        if a == 0:
            f, sc, tc, ma = ("px", -z, -y, x) if x > 0 else ("nx", z, -y, -x)
        elif a == 1:
            f, sc, tc, ma = ("py", x, z, y) if y > 0 else ("ny", x, -z, -y)
        else:
            f, sc, tc, ma = ("pz", x, -y, z) if z > 0 else ("nz", -x, -y, -z)
        u = (sc / ma + 1) / 2
        v = (tc / ma + 1) / 2
        out[i] = faces[f][min(size - 1, int(v * size)), min(size - 1, int(u * size))]
    return out


def draw_cube(size, up_axis):
    """Six faces; the world's up is +Y (Direct3D's usual) or +Z."""
    faces = {}
    for f in FACES:
        d = face_dirs(f, size)
        if up_axis == "y":   # up +Y, horizontal +X and -Z
            col = sky_colour(d[..., 1], d[..., 0], -d[..., 2])
        else:                # up +Z, horizontal +X and +Y (the Y-up set turned 90 degrees about X)
            col = sky_colour(d[..., 2], d[..., 0], d[..., 1])
        faces[f] = to8(col)
    return faces


def cube_seams(faces):
    """How continuous the faces are: the mean step across each face's border (to the neighbouring
    face's texel one texel out) against the mean step between neighbouring texels inside."""
    size = faces["px"].shape[0]
    across, inside = [], []
    f32 = {k: v.astype(np.float64) for k, v in faces.items()}
    for f in FACES:
        d = face_dirs(f, size)
        img = f32[f]
        for sl, step in (((0, slice(None)), (-1, 0)), ((size - 1, slice(None)), (1, 0)),
                         ((slice(None), 0), (0, -1)), ((slice(None), size - 1), (0, 1))):
            dd = d[sl]
            # one texel out of the face: the next row/column's direction, extrapolated
            if step[0]:
                nb = d[(sl[0] - step[0], sl[1])]
            else:
                nb = d[(sl[0], sl[1] - step[1])]
            out_dir = dd + (dd - nb)
            idx = np.arange(0, size, 16)
            samp = cube_lookup(out_dir[idx], faces)
            across.append(np.abs(samp - img[sl][idx]).mean())
            inside.append(np.abs(img[sl][idx] - f32[f][(sl[0] - step[0], sl[1]) if step[0] else (sl[0], sl[1] - step[1])][idx]).mean())
    return float(np.mean(across)), float(np.mean(inside))


# --- main ---------------------------------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--size-dial", type=int, default=512)
    ap.add_argument("--size-lens", type=int, default=256)
    ap.add_argument("--size-badge", type=int, default=512)
    ap.add_argument("--size-cube", type=int, default=512)
    ap.add_argument("--size-disc", type=int, default=1024)
    args = ap.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    files = {}

    def put(name, img, use, channels, labels):
        write_png(out / name, img)
        files[name] = dict(size=list(img.shape[1::-1]), use=use, channels=channels, labels=labels)

    d, s, n, g, gn = draw_dial(args.size_dial)
    dl = ["front_dial", "front_dialglow", "front_needle"]
    put("front_dial_d.png", d, "diffuse", "RGB colour", dl)
    put("front_dial_s.png", s, "specular/smoothness", "R specular, G smoothness, B unused (linear)", dl)
    put("front_dial_n.png", n, "normal", "tangent space, Direct3D (G toward +v), flat", dl)
    put("front_dialglow_g.png", g, "glow", "grey: the lit marks", ["front_dialglow"])
    put("front_dial_g.png", gn, "glow (optional)", "grey: the needle's blade only", ["front_dial", "front_needle"])
    for brake in (False, True):
        ld, lg = draw_lens(args.size_lens, brake)
        stem = "rear_brake" if brake else "rear_tail"
        put(f"{stem}_d.png", ld, "diffuse", "RGB colour", [stem])
        put(f"{stem}_g.png", lg, "glow", "grey: emission strength", [stem])
    bd, bn, bs = draw_badge(args.size_badge)
    put("static_badge_d.png", bd, "diffuse", "RGB colour, A the emblem's outline (alpha test at 128)", ["static_badge"])
    put("static_badge_n.png", bn, "normal", "tangent space, Direct3D (G toward +v)", ["static_badge"])
    put("static_badge_s.png", bs, "specular/smoothness", "R specular, G smoothness, B unused (linear)", ["static_badge"])
    dd, dn, ds, _ = draw_disc(args.size_disc)
    disc_labels = ["wheelF_disc", "wheelR_disc"]
    put("wheel_disc_d.png", dd, "diffuse", "RGB colour", disc_labels)
    put("wheel_disc_n.png", dn, "normal", "tangent space, Direct3D (G toward +v): the turning grooves, the chamfers", disc_labels)
    put("wheel_disc_s.png", ds, "specular/smoothness", "R specular, G smoothness, B unused (linear)", disc_labels)
    seams = {}
    for up_axis, stem in (("y", "mirror_cube"), ("z", "mirror_cube_zup")):
        faces = draw_cube(args.size_cube, up_axis)
        for f in FACES:
            put(f"{stem}_{f}.png", faces[f], "cube face", "RGB colour", ["front_mirrorStock", "front_mirrorUnderEgg", "front_mirrorUnderD"])
        seams[stem] = cube_seams(faces)
    cube = {
        "faces": {stem: [f"{stem}_{f}.png" for f in FACES] for stem in ("mirror_cube", "mirror_cube_zup")},
        "order": "+X -X +Y -Y +Z -Z (px nx py ny pz nz), the DDS cube order",
        "orientation": "Direct3D: a face's first row is its top; +X: right -Z, down -Y; -X: right +Z, down -Y; "
                       "+Y: right +X, down +Z; -Y: right +X, down -Z; +Z: right +X, down -Y; -Z: right -X, down -Y",
        "up": {"mirror_cube": "+Y (sky on the +Y face, the horizon across the middle of the four side faces)",
               "mirror_cube_zup": "+Z (sky on the +Z face): the same sky turned 90 degrees about X, for a one-file "
                                  "swap if the game shows mirror_cube's sky sideways"},
        "sun": {"elevation_deg": SUN[0], "azimuth_deg": SUN[1],
                "azimuth_from": "+X toward -Z (mirror_cube) / +X toward +Y (mirror_cube_zup)"},
        "seams": {k: {"mean_step_across_faces": round(v[0], 2), "mean_step_inside": round(v[1], 2)} for k, v in seams.items()},
    }
    (out / "cube.json").write_text(json.dumps(cube, indent=1) + "\n")
    manifest = {"version": 1, "normal_convention": "Direct3D tangent space: R +u, G +v (down the image), B out; no green flip",
                "colour": "8-bit as displayed; specular and smoothness linear", "files": files,
                "layout": {"dial": {"DIAL_ART_R": bp.DIAL_ART_R, "NEEDLE_PATCH": bp.NEEDLE_PATCH, "DIAL_ZERO": bp.DIAL_ZERO,
                                    "DIAL_MAX": bp.DIAL_MAX, "DIAL_PER_MPH": bp.DIAL_PER_MPH},
                           "lens": {"LENS_TAIL_BOX": bp.LENS_TAIL_BOX, "LENS_ROUND_BOX": bp.LENS_ROUND_BOX},
                           "badge": {"BADGE_BAND_W": bp.BADGE_BAND_W, "BADGE_ROUNDEL": bp.BADGE_ROUNDEL},
                           "disc": {"DISC_ART_R": bp.DISC_ART_R, "DISC_BAND": bp.DISC_BAND, "DISC_HUB_REF": bp.DISC_HUB_REF,
                                    "holes": [[k, round(a, 6), round(r, 6), round(h, 6)] for k, a, r, h in bp.disc_layout(1.0)]}}}
    (out / "art.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"wrote {len(files)} images and art.json, cube.json to {out}; cube seams (mean step across / inside, 0-255): "
          + ", ".join(f"{k} {v[0]:.2f}/{v[1]:.2f}" for k, v in seams.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
