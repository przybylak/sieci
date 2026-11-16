#!/usr/bin/env python3
"""The 3D helmet emblems' geometry (build 2026-11-16a, C3 item 3.1): the Enclave's and the Brotherhood of Steel's helmets
as raised emblems standing upright on the tank's badge plates, our own models after a written feature list (no picture
is read by this code; the comments describe features, never pixels).

Each helmet is a bas-relief: a height h(x, y) over the emblem's plane, x to the viewer's right, y up, in units (the
bike's), the helmet's design centred on (0, 0) about 7.5 wide and 8.2 tall at scale 1. The heights come from a few dozen primitives
(2D signed distances: circles, ellipses, almonds, polygons, strokes along curves) combined by raising (max), embossing
(a step over what is there) and carving (a recess with a rounded wall), so a feature's outline, its height and its
colour region are the same numbers: emblem_art.py evaluates the same field at the texture's resolution for the colour,
normal, specular and glow maps. Fine detail under about 0.15 units (rivets, ribbing, seams, grille holes) is only in
the field's "detail" (the normal map): the worn nifs' half floats move a vertex by up to 1/32 unit.

Where nothing stands, h is SKIRT (0.15 under the plate's surface): every wall runs down into the plate, so no gap and no
coplanar face shows (real geometry, no decal flag), and the triangles wholly at that depth are dropped.

The mesh: the field sampled on a GRID-unit lattice, the sunk triangles dropped, cut down with quadric edge collapse
(fast_simplification) to TARGET triangles (the error measured against the field, ERROR_CAP the aim), then cast onto
each side's plate: the plate's frame from the parked nif (full precision): n its outward normal (the area-weighted
mean of its faces), up the world's z on the plate's plane, right = up x n (the relief reads true from outside on both
sides: the same, not mirrored, as the badges). In that frame each helmet is turned square with the plate: its up along
the ground field's own axis (the plate's UV v, the flat badges' up: -12.5 degrees on the left plate, +12.5 on the right;
the author's pick after the first renders, revising c3.md's upright).
Each (x, y) is cast along -n onto the plate's triangles (bike_pieces._cast_down's method turned to the plate's
normal) and lifted h along the plate's interpolated vertex normal there, so the emblem's foot follows the plate's
curvature. Normals per face of the cast mesh, a vertex split where its corners part by more than SPLIT_DEG.

The footprint: the helmet's (every sample over SKIRT) inside its ground's enamel field inset FIELD_INSET (measured on
the cast vertices), centred on the field's axis, at the largest scale up to SCALE_MAX (the same on both sides). The bar
assembly swept through BarAngle (the under-bar mirrors pass close over the right plate at full lock) keeps MIRROR_CLEAR
from each helmet: where it doesn't, that helmet's relief is made shallower (down to RELIEF_MIN), then it is made
smaller about the same centre. The
ground (unit B's badge_hg_enclave / badge_hg_bos) is one material on both tank plates with the same, unmirrored UVs, so
its enamel field inside the chrome bevel is the area both plates show: GROUND_FIELD_UV, in the plate's own UVs, from
badges.json's hg_*.field.outline_plate_uv (bike_art.draw_ground), mapped through each plate's triangles into its frame
(about 7.5 units tall at the plate's middle, 5 at its ends). Without a field (ground None) the plate's own outline
inset INSET on its forward half, the first fit.

UVs: the design's (x, y) planar into the helmet's 512 cell of helms_*.dds: CELL_BOX units square about (0, 0), u to
the right, v down (Enclave cell (0, 0), Brotherhood (1, 0)).

  python emblem_pieces.py --preview <out folder> [--grid 0.05]     (a shaded height map per helmet, PNG, no nif needed)
"""

import argparse
import math
import sys
from pathlib import Path

import numpy as np

SKIRT = -0.15       # where nothing stands: under the plate's surface
FOOT = 0.04         # a wall's foot runs from SKIRT this far outside the outline up to 0 at it
GRID = 0.025        # the field's lattice for the mesh (units)
TARGET = 3500       # triangles a helmet after the simplifier (c3.md: 2,500-3,500)
TARGET_MAX = 3500
ERROR_CAP = 0.02    # the aim for the simplified surface's distance from the lattice's, 99th percentile (units)
SPLIT_DEG = 50.0    # normals split where a vertex's corners part by more than this
INSET = 0.4         # without a ground field: the footprint inside the plate's own outline inset this much
FIELD_INSET = 0.2   # the footprint inside its ground's enamel field inset this much (clear of the chrome bevel); measured
                    # on the cast vertices (the lift along the plate's normals leans the tall parts out a little)
SCALE_MAX = 1.0     # the design's nominal size (7.5 x 8.2) at most
MIRROR_CLEAR = 0.3  # the bar assembly (the under-bar mirrors among it) turned within BarAngle at least this clear of a
MIRROR_SPARE = 0.05 # helmet (the author's minimum), with this to spare at the build's 0.5-degree steps
RELIEF_MIN = 0.6    # where the sweep comes nearer: the relief made shallower down to this, then the helmet smaller
                    # (the under-bar mirrors cross the right plate over the helmets' upper rear: depth, not size, is what
                    # keeps them clear there; a smaller helmet about the same centre barely moves that region)
# The helmets' ground (unit B, t60-b 5918ddf: bike_art.draw_ground; badges.json's hg_enclave and hg_bos
# field.outline_plate_uv, the same for both): the enamel field inside the stock badge's chrome bevel in the tank plate's
# own UVs (u to the viewer's right, v down: the plate's UV rectangle 0.02-0.98 x 0.299-0.701). look_emblems.py
# --ground-field <badges.json> reads it from B's output instead.
GROUND_FIELD_UV = ((0.5, 0.32291), (0.89699, 0.39133), (0.9275, 0.55681), (0.9275, 0.61496), (0.5, 0.64902),
                   (0.0725, 0.61496), (0.0725, 0.55681), (0.10301, 0.39133))
CELL_BOX = 8.4      # design units across a helmet's texture cell
HEIGHT_MAX = 1.8    # the relief's height over the plate at most (tubes and the lamp; the bas-relief 1.6)
DESIGN_W, DESIGN_H = 7.5, 8.2   # the nominal footprint (c3.md 3.1)

HELMETS = ("enclave", "bos")
CELLS = {"enclave": (0, 0), "bos": (1, 0)}                    # [column, row] in helms_*.dds (512 cells, 1024 x 512)
SHAPES = (("static_helmEnclaveL", "enclave", "L"), ("static_helmEnclaveR", "enclave", "R"),
          ("static_helmBosL", "bos", "L"), ("static_helmBosR", "bos", "R"))   # the table's emblems.shape_order
PLATES = {"L": "static_badgeTankL", "R": "static_badgeTankR"}

# colour regions (emblem_art.py's palette keys)
NONE, METAL, LENS, HOSE, TRIM, RECESS, CAN, PANEL, GLASS, BOLT, RUBBER = range(11)
REGION_NAMES = ("none", "metal", "lens", "hose", "trim", "recess", "can", "panel", "glass", "bolt", "rubber")


# --- 2D signed distances (negative inside), on arrays X, Y ------------------------------------------------------------

def _rot(X, Y, cx, cy, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    dx, dy = X - cx, Y - cy
    return c * dx + s * dy, -s * dx + c * dy


def sd_circle(X, Y, cx, cy, r):
    return np.hypot(X - cx, Y - cy) - r


def sd_ellipse(X, Y, cx, cy, a, b, deg=0.0, p=2.0):
    """A (super)ellipse's distance, near enough: the normalised radius's excess times the smaller half-axis
    (exact on the axes, a little short elsewhere; the walls stay steep). p > 2 squares it off."""
    u, v = _rot(X, Y, cx, cy, deg)
    r = (np.abs(u / a) ** p + np.abs(v / b) ** p) ** (1.0 / p)
    return (r - 1.0) * min(a, b)


def sd_almond(X, Y, cx, cy, half_len, half_h, deg):
    """A pointed almond (two circles' lens), its long axis at deg from +x."""
    u, v = _rot(X, Y, cx, cy, deg)
    R = (half_len ** 2 + half_h ** 2) / (2.0 * half_h)
    off = R - half_h
    return np.maximum(np.hypot(u, v + off), np.hypot(u, v - off)) - R


def sd_box(X, Y, cx, cy, hw, hh, r=0.0, deg=0.0):
    u, v = _rot(X, Y, cx, cy, deg)
    qx, qy = np.abs(u) - (hw - r), np.abs(v) - (hh - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def sd_poly(X, Y, pts):
    """A simple polygon's exact distance (pts (n, 2), either winding)."""
    P = np.asarray(pts, np.float64)
    d2 = np.full(X.shape, np.inf)
    inside = np.zeros(X.shape, bool)
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        e = b - a
        wx, wy = X - a[0], Y - a[1]
        t = np.clip((wx * e[0] + wy * e[1]) / (e @ e), 0.0, 1.0)
        d2 = np.minimum(d2, (wx - t * e[0]) ** 2 + (wy - t * e[1]) ** 2)
        c1 = Y >= a[1]
        c2 = Y < b[1]
        c3 = e[0] * wy > e[1] * wx
        flip = (c1 & c2 & c3) | (~c1 & ~c2 & ~c3)
        inside ^= flip
    return np.where(inside, -1.0, 1.0) * np.sqrt(d2)


def polyline(X, Y, pts):
    """The distance to a polyline and the arc length at the closest point (for ribs along a hose)."""
    P = np.asarray(pts, np.float64)
    best = np.full(X.shape, np.inf)
    along = np.zeros(X.shape)
    s0 = 0.0
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        e = b - a
        L = float(np.hypot(*e))
        wx, wy = X - a[0], Y - a[1]
        t = np.clip((wx * e[0] + wy * e[1]) / max(L * L, 1e-12), 0.0, 1.0)
        d = np.hypot(wx - t * e[0], wy - t * e[1])
        m = d < best
        best = np.where(m, d, best)
        along = np.where(m, s0 + t * L, along)
        s0 += L
    return best, along, s0


def bezier(p0, p1, p2, p3, n=40):
    t = np.linspace(0.0, 1.0, n)[:, None]
    p0, p1, p2, p3 = (np.asarray(p, np.float64) for p in (p0, p1, p2, p3))
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def mirror(pts):
    return [(-x, y) for x, y in pts]


def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def roundover(d, w):
    """0 at the outline (d = 0, inside distance) to 1 at w in, a quarter ellipse: a steep wall rounding over."""
    t = np.clip(d / max(w, 1e-9), 0.0, 1.0)
    return np.sqrt(1.0 - (1.0 - t) ** 2)


# --- the field ---------------------------------------------------------------------------------------------------------

class Field:
    """h (units over the plate), region (colour key), detail (fine relief for the normal map, units) on a grid."""

    def __init__(self, X, Y):
        self.X, self.Y = X, Y
        self.h = np.full(X.shape, SKIRT)
        self.region = np.zeros(X.shape, np.uint8)
        self.detail = np.zeros(X.shape)
        self.glow = np.zeros(X.shape)    # 0..1, the glow map's share
        self.px = float(X[0, 1] - X[0, 0]) if X.shape[1] > 1 else 1.0

    def raise_(self, sd, height, region, wall=0.1):
        """A solid whose top is `height` (an array or a number) inside sd < 0, its wall rounding over in `wall`, its
        foot down to SKIRT just outside: the higher of it and what is there."""
        d = -sd
        top = np.broadcast_to(np.asarray(height, np.float64), self.h.shape)
        prof = np.where(d >= 0, top * roundover(d, wall), SKIRT + (0.0 - SKIRT) * np.clip(1.0 + d / FOOT, 0.0, 1.0))
        prof = np.where(d < -FOOT, SKIRT, prof)
        m = prof > self.h
        self.h = np.where(m, prof, self.h)
        self.region = np.where(m & (d >= -0.5 * self.px), np.uint8(region), self.region)
        return m

    def emboss(self, sd, dh, region=None, wall=0.06):
        """A step dh over what is there inside sd < 0, its edge rounded over in `wall`."""
        d = -sd
        inside = d > 0
        add = dh * roundover(np.maximum(d, 0.0), wall)
        self.h = np.where(inside & (self.h > SKIRT + 1e-6), self.h + add, self.h)
        if region is not None:
            self.region = np.where(inside & (d >= 0.5 * self.px), np.uint8(region), self.region)

    def carve(self, sd, floor, region=None, wall=0.08):
        """A recess inside sd < 0 down to `floor` (absolute height), its wall rounding in `wall`."""
        d = -sd
        inside = d > 0
        t = roundover(np.maximum(d, 0.0), wall)
        target = self.h - (self.h - floor) * t
        self.h = np.where(inside & (self.h > floor), np.minimum(self.h, target), self.h)
        if region is not None:
            self.region = np.where(inside & (d >= 0.5 * self.px), np.uint8(region), self.region)

    def tube(self, pts, r, axis_h, region, ribs=None, wall=0.0):
        """A hose lying along pts: a half round of radius r (an array along the curve is allowed by axis_h's
        callable) over the axis at axis_h; ribs = (pitch, depth) in the detail map."""
        dist, s, total = polyline(self.X, self.Y, pts)
        ah = axis_h(s / total) if callable(axis_h) else axis_h
        rr = r(s / total) if callable(r) else r
        inside = dist < rr
        top = ah + np.sqrt(np.maximum(rr * rr - dist * dist, 0.0))
        # its foot: from SKIRT just outside the radius
        prof = np.where(inside, top, np.where(dist < rr + FOOT, SKIRT + (ah - SKIRT) * (1 - (dist - rr) / FOOT), SKIRT))
        m = prof > self.h
        self.h = np.where(m, prof, self.h)
        self.region = np.where(m & inside, np.uint8(region), self.region)
        if ribs is not None:
            pitch, depth = ribs
            rib = depth * (0.5 + 0.5 * np.cos(2 * math.pi * s / pitch))
            self.detail = np.where(m & inside, self.detail - rib, self.detail)
        return m & inside

    def rivet(self, cx, cy, r=0.09, dh=0.05):
        d = np.hypot(self.X - cx, self.Y - cy)
        self.detail += np.where(d < r, dh * np.sqrt(np.maximum(1 - (d / r) ** 2, 0.0)), 0.0)

    def groove(self, pts, w=0.04, depth=0.04):
        dist, _, _ = polyline(self.X, self.Y, pts)
        self.detail -= np.where(dist < w, depth * (1 - (dist / w) ** 2), 0.0)


def _ramp(y, knots):
    """Piecewise linear in y through (y, value) knots (any order)."""
    k = sorted(knots)
    return np.interp(y, [a for a, _ in k], [b for _, b in k])


# --- the Enclave helmet ------------------------------------------------------------------------------------------------
# Features (the author's brief, c3.md 3.1): a dark gunmetal dome, broad at the brow; two large slanted almond eye lenses
# in deep sockets, glowing amber; a riveted vertical seam from the crown down a long, tapering, beak-like respirator
# snout that hangs below the chin, framed by a thin raised trim, with two pairs of short vertical vent slots low on its
# sides; two ribbed hoses leaving the temples and curving up and back like horns; a ribbed breather can on one cheek
# and a small raised panel on the other.

def enclave(F):
    X, Y = F.X, F.Y
    # the horns first (the dome stands over their roots): from the temples up, out and back down
    for sx in (-1.0, 1.0):
        pts = bezier((sx * 2.05, 2.25), (sx * 2.25, 3.55), (sx * 3.0, 3.85), (sx * 3.32, 2.70), 48)
        F.tube(pts, lambda t: 0.38 - 0.08 * t, lambda t: 0.55 - 0.15 * t, HOSE, ribs=(0.20, 0.05))
        # a collar where each hose leaves the head
        F.raise_(sd_circle(X, Y, sx * 2.10, 2.45, 0.36), 1.02, TRIM, wall=0.08)
    # the skull: a dome broad at the brow, narrowing to the crown
    skull = np.minimum(sd_ellipse(X, Y, 0.0, 1.15, 2.62, 2.80, p=2.3), sd_ellipse(X, Y, 0.0, -0.05, 2.42, 1.75, p=2.4))
    dome = 0.55 + 0.62 * np.sqrt(np.clip(1.0 - (X / 2.8) ** 2 - ((Y - 1.0) / 3.1) ** 2, 0.0, 1.0))
    F.raise_(skull, dome, METAL, wall=0.30)
    # the cheeks under the eyes, a little fuller
    for sx in (-1.0, 1.0):
        F.emboss(sd_ellipse(X, Y, sx * 1.55, -0.75, 0.85, 0.75), 0.12, wall=0.35)
    # the respirator plate between the cheeks, round the snout, framed by its trim (a raised wire on its outline)
    resp = [(-1.05, -0.05), (-1.62, -0.70), (-1.50, -2.35), (-1.10, -3.35), (-0.35, -3.95), (0.35, -3.95), (1.10, -3.35),
            (1.50, -2.35), (1.62, -0.70), (1.05, -0.05)]
    sd_resp = sd_poly(X, Y, resp)
    F.raise_(sd_resp, 0.86, METAL, wall=0.12)
    trim, _, _ = polyline(X, Y, resp + [resp[0]])      # a soft bead, wide enough to stay smooth through the simplifier
    F.emboss(trim - 0.13, 0.12, TRIM, wall=0.13)
    # two pairs of short vertical vent slots low on its sides
    for sx in (-1.0, 1.0):
        for cy in (-2.35, -2.95):
            F.carve(sd_box(X, Y, sx * 0.98, cy, 0.11, 0.24, r=0.1), 0.45, RECESS, wall=0.05)
    # the snout: a long tapering beak from between the eyes to below the chin, highest at the nose
    snout = [(-0.42, 0.55), (-0.62, -0.30), (-0.78, -1.25), (-0.66, -2.35), (-0.42, -3.35), (-0.16, -4.08), (0.16, -4.08),
             (0.42, -3.35), (0.66, -2.35), (0.78, -1.25), (0.62, -0.30), (0.42, 0.55)]
    ridge = _ramp(Y, [(0.6, 1.22), (-0.4, 1.45), (-1.4, 1.58), (-2.6, 1.45), (-4.1, 1.12)])
    sd_snout = sd_poly(X, Y, snout)
    F.raise_(sd_snout, ridge, METAL, wall=0.55)
    # its keel, a soft crease down the middle
    F.emboss(sd_box(X, Y, 0.0, -1.7, 0.10, 2.2, r=0.1), 0.04, wall=0.10)
    # the eye sockets: deep, the lenses' rims under the brow, the lenses convex in them
    for sx in (-1.0, 1.0):
        deg = 24.0 if sx > 0 else -24.0
        cx, cy = sx * 1.30, 0.50
        F.emboss(sd_almond(X, Y, cx, cy + 0.06, 1.24, 0.72, deg), 0.10, wall=0.18)       # the brow's swell round it
        F.carve(sd_almond(X, Y, cx, cy, 1.13, 0.61, deg), 0.42, RECESS, wall=0.10)
        lens = sd_almond(X, Y, cx, cy, 1.00, 0.51, deg)
        u, v = _rot(X, Y, cx, cy, deg)
        bulge = 0.62 + 0.36 * np.sqrt(np.clip(1.0 - (u / 1.0) ** 2 - (v / 0.51) ** 2, 0.0, 1.0))
        m = F.raise_(lens, bulge, LENS, wall=0.06)
        F.glow = np.maximum(F.glow, np.where(lens < 0, np.clip(-lens / 0.06, 0, 1), 0.0))
    # the breather can on the viewer's left cheek: a ribbed cylinder angled down and out, capped
    can_a, can_b = (-1.80, -0.75), (-2.62, -1.80)
    dist, s, total = polyline(X, Y, [can_a, can_b])
    can = dist - 0.44
    F.raise_(can, 0.78 + np.sqrt(np.maximum(0.44 ** 2 - dist ** 2, 0.0)) * 0.9, CAN, wall=0.08)
    for k in range(4):     # three bands in the geometry, fine ribs in the detail
        t = 0.18 + 0.22 * k
        p = np.array(can_a) + t * (np.array(can_b) - np.array(can_a))
        band = sd_box(X, Y, p[0], p[1], 0.47, 0.05, r=0.04, deg=math.degrees(math.atan2(can_b[1] - can_a[1], can_b[0] - can_a[0])) + 90)
        F.emboss(np.maximum(band, can), 0.06, TRIM, wall=0.03)
    F.detail -= np.where(can < 0, 0.025 * (0.5 + 0.5 * np.cos(2 * math.pi * s / 0.11)), 0.0)
    # the small raised panel on the other cheek, riveted
    F.emboss(sd_box(X, Y, 1.92, -1.05, 0.40, 0.55, r=0.12, deg=-14.0), 0.16, PANEL, wall=0.06)
    for du, dv in ((-0.27, -0.42), (0.27, -0.42), (-0.27, 0.42), (0.27, 0.42)):
        u, v = _rot(np.array([[du]]), np.array([[dv]]), 0, 0, 14.0)
        F.rivet(1.92 + float(u[0, 0]), -1.05 + float(v[0, 0]))
    # the riveted seam from the crown down the snout (detail only)
    seam = [(0.0, 3.95), (0.0, 0.70), (0.0, -4.0)]
    F.groove(seam, 0.035, 0.05)
    for y in np.arange(3.6, 0.9, -0.42):
        F.rivet(-0.13, y, 0.07, 0.045)
        F.rivet(0.13, y, 0.07, 0.045)
    for y in np.arange(-0.4, -3.8, -0.48):
        F.rivet(-0.17, y, 0.06, 0.04)
        F.rivet(0.17, y, 0.06, 0.04)
    # rivets along the trim, a seam round the brow
    F.groove(bezier((-2.45, 0.95), (-1.5, 1.55), (1.5, 1.55), (2.45, 0.95), 24), 0.03, 0.035)
    for x in (-2.0, -1.0, 1.0, 2.0):
        F.rivet(x, 1.25 + 0.1 * (2 - abs(x)), 0.07, 0.04)


# --- the Brotherhood of Steel helmet -----------------------------------------------------------------------------------
# Features: a brushed-steel dome with a raised centre strip over the crown, bolted at its corners; a horizontal brow
# ridge; two angular dark eye openings either side of a vertical nose ridge (a frowning mask); rounded cheek bulges
# with two short valve studs pointing out and down; a round filter at the mouth with six radial slots; a cylinder lamp
# on a bracket at one temple and a round lens with concentric rings at the other; short ribbed hose stubs curving down
# outside the jaw.

def bos(F):
    X, Y = F.X, F.Y
    # the hose stubs outside the jaw, under everything else
    for sx in (-1.0, 1.0):
        pts = bezier((sx * 2.05, 0.35), (sx * 2.95, -0.35), (sx * 3.10, -1.75), (sx * 2.45, -2.75), 40)
        F.tube(pts, 0.44, 0.50, HOSE, ribs=(0.24, 0.06))
        F.raise_(sd_circle(X, Y, sx * 2.47, -2.72, 0.47), 0.95, TRIM, wall=0.06)     # its collar at the jaw
    # the head: a boxy dome over a face narrowing to the jaw
    head = np.minimum(sd_ellipse(X, Y, 0.0, 1.30, 2.55, 2.70, p=2.6),
                      sd_poly(X, Y, [(-2.42, 1.0), (2.42, 1.0), (2.15, -1.65), (1.45, -3.05), (-1.45, -3.05), (-2.15, -1.65)]))
    dome = 0.55 + 0.55 * np.sqrt(np.clip(1.0 - (X / 2.8) ** 2 - ((Y - 0.9) / 3.3) ** 2, 0.0, 1.0))
    F.raise_(head, dome, METAL, wall=0.28)
    # the raised centre strip over the crown, bolted at its corners
    strip = sd_poly(X, Y, [(-0.62, 4.2), (0.62, 4.2), (0.80, 1.05), (-0.80, 1.05)])
    F.emboss(np.maximum(strip, head + 0.05), 0.20, wall=0.07)
    for bx, by in ((-0.46, 3.55), (0.46, 3.55), (-0.60, 1.35), (0.60, 1.35)):
        F.rivet(bx, by, 0.10, 0.06)
    for bx in (-0.28, 0.28):     # the two round bolts at its foot, in the geometry
        F.emboss(sd_circle(X, Y, bx, 1.32, 0.17), 0.10, BOLT, wall=0.06)
    # side grooves along the dome (panel lines)
    for sx in (-1.0, 1.0):
        F.groove(bezier((sx * 1.55, 3.55), (sx * 1.95, 2.9), (sx * 2.1, 2.2), (sx * 2.15, 1.3), 20), 0.035, 0.04)
    # the face: a mask from the brow to the jaw, the cheeks bulging
    face = sd_poly(X, Y, [(-2.30, 0.95), (2.30, 0.95), (2.05, -1.55), (1.40, -2.95), (-1.40, -2.95), (-2.05, -1.55)])
    F.raise_(face, 1.08, METAL, wall=0.30)
    for sx in (-1.0, 1.0):
        F.emboss(sd_ellipse(X, Y, sx * 1.30, -1.12, 0.78, 0.72), 0.24, wall=0.35)
        F.emboss(sd_circle(X, Y, sx * 1.30, -1.12, 0.26), 0.06, BOLT, wall=0.05)    # a round socket on each bulge
        F.carve(sd_circle(X, Y, sx * 1.30, -1.12, 0.13), 1.24, RECESS, wall=0.03)
        # a valve stud pointing out and down
        dist, _, _ = polyline(X, Y, [(sx * 1.62, -1.52), (sx * 2.0, -1.98)])
        F.raise_(dist - 0.17, 1.42, BOLT, wall=0.10)
    # the brow ridge: a frown, low over the nose, rising to the temples
    brow = [(-2.40, 1.05), (-1.30, 0.80), (-0.35, 0.50), (0.0, 0.56), (0.35, 0.50), (1.30, 0.80), (2.40, 1.05)]
    bd, _, _ = polyline(X, Y, brow)
    F.raise_(bd - 0.26, 1.32, METAL, wall=0.16)
    # the eye openings: angular, dark, either side of the nose ridge
    for sx in (-1.0, 1.0):
        eye = [(sx * 0.32, 0.18), (sx * 1.30, 0.42), (sx * 2.18, 0.70), (sx * 2.30, 0.18), (sx * 1.85, -0.30),
               (sx * 0.62, -0.36)]
        F.carve(sd_poly(X, Y, eye if sx > 0 else eye[::-1]), 0.30, RECESS, wall=0.10)
    # the nose ridge, from the brow down to the filter
    nose = sd_poly(X, Y, [(-0.17, 0.62), (0.17, 0.62), (0.26, -1.75), (-0.26, -1.75)])
    F.raise_(nose, _ramp(Y, [(0.6, 1.42), (-1.75, 1.36)]), METAL, wall=0.12)
    # the round filter at the mouth: a rim, a face, six radial slots, a hub
    fx, fy = 0.0, -2.42
    F.raise_(sd_circle(X, Y, fx, fy, 0.82), 1.50, METAL, wall=0.10)
    F.carve(sd_circle(X, Y, fx, fy, 0.66), 1.40, wall=0.05)
    for k in range(6):
        a = math.radians(90 + 60 * k)
        p0 = (fx + 0.20 * math.cos(a), fy + 0.20 * math.sin(a))
        p1 = (fx + 0.52 * math.cos(a), fy + 0.52 * math.sin(a))
        dist, _, _ = polyline(X, Y, [p0, p1])
        F.carve(dist - 0.085, 1.10, RECESS, wall=0.03)
    F.emboss(sd_circle(X, Y, fx, fy, 0.13), 0.05, BOLT, wall=0.04)
    # the lamp at the viewer's left temple: a clamp on the dome, a bracket, the round lamp head and its lens
    F.raise_(sd_box(X, Y, -2.30, 2.40, 0.22, 0.30, r=0.06, deg=-30), 1.18, BOLT, wall=0.06)
    dist, _, _ = polyline(X, Y, [(-2.30, 2.40), (-2.92, 2.92)])
    F.raise_(dist - 0.15, 1.12, METAL, wall=0.08)
    F.raise_(sd_circle(X, Y, -3.05, 3.05, 0.58), 1.58, METAL, wall=0.12)
    F.carve(sd_circle(X, Y, -3.05, 3.05, 0.44), 1.48, wall=0.04)
    d = np.hypot(X + 3.05, Y - 3.05)
    F.raise_(sd_circle(X, Y, -3.05, 3.05, 0.40), 1.50 + 0.25 * np.sqrt(np.clip(1 - (d / 0.40) ** 2, 0, 1)), GLASS, wall=0.03)
    # the round lens with concentric rings at the other temple
    lx, ly = 2.78, 2.78
    F.raise_(sd_circle(X, Y, lx, ly, 0.80), 1.48, METAL, wall=0.10)
    for r, hgt in ((0.62, 1.40), (0.46, 1.33), (0.30, 1.26)):
        F.carve(sd_circle(X, Y, lx, ly, r), hgt, RECESS if r < 0.5 else None, wall=0.04)
    F.raise_(sd_circle(X, Y, lx, ly, 0.17), 1.36, GLASS, wall=0.05)
    dist, _, _ = polyline(X, Y, [(2.10, 2.20), (2.38, 2.45)])     # its mount on the dome
    F.raise_(dist - 0.16, 1.14, BOLT, wall=0.06)
    # bolts round the face plate (detail)
    for bx, by in ((-2.0, 0.75), (2.0, 0.75), (-1.75, -1.95), (1.75, -1.95), (-1.05, -2.75), (1.05, -2.75)):
        F.rivet(bx, by, 0.09, 0.05)


DESIGNS = {"enclave": enclave, "bos": bos}


def field(name, X, Y):
    F = Field(X, Y)
    DESIGNS[name](F)
    F.h = np.minimum(F.h, HEIGHT_MAX)
    return F


def lattice(step=GRID, box=CELL_BOX):
    """The design's square about (0, 0), CELL_BOX across, sampled every `step` (row 0 the top)."""
    n = int(round(box / step)) + 1
    xs = np.linspace(-box / 2, box / 2, n)
    X, Y = np.meshgrid(xs, xs[::-1])
    return X, Y


def texture_lattice(size, box=CELL_BOX):
    """A cell's texel centres (size x size, row 0 the top: v down)."""
    c = (np.arange(size) + 0.5) / size * box - box / 2
    X, Y = np.meshgrid(c, -c)
    return X, Y


def uv_of(name, xy):
    """The helmet's design (x, y) -> its cell's UV (u right, v down)."""
    col, row = CELLS[name]
    u = (col + (xy[:, 0] + CELL_BOX / 2) / CELL_BOX) * 0.5
    v = row + (CELL_BOX / 2 - xy[:, 1]) / CELL_BOX
    return np.column_stack([u, v])


# --- the mesh ---------------------------------------------------------------------------------------------------------

def grid_mesh(name, step=GRID):
    """The field on the lattice as triangles, the wholly sunk ones dropped: (points (n, 3) as x, y, h; tris (m, 3),
    counter-clockwise seen from +h)."""
    X, Y = lattice(step)
    F = field(name, X, Y)
    rows, cols = X.shape
    idx = np.arange(rows * cols).reshape(rows, cols)
    a, b, c, d = idx[:-1, :-1], idx[:-1, 1:], idx[1:, :-1], idx[1:, 1:]   # row 0 the top: a top-left, c below it
    # two triangles a cell, the diagonal alternating (no grain): seen from +h (x right, y up) both counter-clockwise
    flip = ((np.arange(rows - 1)[:, None] + np.arange(cols - 1)[None, :]) % 2).astype(bool)
    t1 = np.where(flip[..., None], np.stack([a, c, b], -1), np.stack([a, c, d], -1))
    t2 = np.where(flip[..., None], np.stack([b, c, d], -1), np.stack([a, d, b], -1))
    tris = np.concatenate([t1.reshape(-1, 3), t2.reshape(-1, 3)])
    h = F.h.reshape(-1)
    keep = ~np.all(h[tris] <= SKIRT + 1e-9, axis=1)
    tris = tris[keep]
    used = np.unique(tris)
    remap = np.full(len(h), -1)
    remap[used] = np.arange(len(used))
    P = np.column_stack([X.reshape(-1), Y.reshape(-1), h])[used]
    return P, remap[tris], F


def signed_area_xy(P, f):
    a, b, c = P[f[:, 0], :2], P[f[:, 1], :2], P[f[:, 2], :2]
    return 0.5 * ((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0]))


def field_error(name, P, f, samples=6):
    """The simplified mesh's height error against the field: at each triangle's barycentric sample points (and its
    corners), |mesh h - field h|. Returns (max, 99th percentile, mean)."""
    w = []
    for i in range(samples + 1):
        for j in range(samples + 1 - i):
            w.append((i / samples, j / samples, 1 - (i + j) / samples))
    w = np.array(w)
    tri = P[f]                                   # (m, 3, 3)
    pts = np.einsum("kc,mcd->mkd", w, tri).reshape(-1, 3)
    F = field(name, pts[:, 0:1], pts[:, 1:2])
    err = np.abs(pts[:, 2] - F.h[:, 0])
    return float(err.max()), float(np.percentile(err, 99)), float(err.mean())


def surface_error(P0, f0, P, f):
    """The simplified surface's distance from the lattice's (both ways, 3D: a wall's height error says nothing):
    (lattice points to the simplified triangles: max, 99th percentile; the simplified points to the lattice's: max)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from nearest import TriangleGrid
    d = TriangleGrid(P[f], 0.3).closest(P0, reach=0.3)[2]
    d2 = TriangleGrid(P0[f0], 0.1).closest(P, reach=0.3)[2]
    return float(d.max()), float(np.percentile(d, 99)), float(d2.max())


def simplified(name, step=GRID, target=TARGET, target_max=TARGET_MAX, cap=ERROR_CAP, agg=7.0, log=print):
    """The helmet's relief cut down to `target` triangles (more, up to target_max, while the error's 99th percentile is
    over cap). Returns (points (n, 3) x, y, h; tris, counter-clockwise from +h; the error). Every triangle is kept: on
    the near-vertical walls a few lean a little past upright after the collapse (none folds over: folds counted)."""
    import fast_simplification as fs
    P0, f0, _ = grid_mesh(name, step)
    best = None
    for tgt in sorted({target, target_max}):
        P, f = fs.simplify(P0, f0.astype(np.int32), target_count=tgt, agg=agg)
        f = np.asarray(f, np.int64)
        fn = unit(np.cross(P[f[:, 1]] - P[f[:, 0]], P[f[:, 2]] - P[f[:, 0]]))
        err = surface_error(P0, f0, P, f)
        folds = int((fn[:, 2] < -0.6).sum())
        log(f"  {name}: lattice {len(P0)} points, {len(f0)} triangles -> {len(P)} points, {len(f)} triangles; its distance "
            f"from the lattice's surface max {err[0]:.3f}, 99% {err[1]:.3f} (cap {cap:g}); {int((fn[:, 2] < -0.2).sum())} "
            f"wall triangles leaning past upright, {folds} folded over")
        if folds:
            raise ValueError(f"{name}: {folds} triangles folded over by the simplifier")
        best = (P, f, err)
        if err[1] <= cap:
            break
    return best


# --- the plate --------------------------------------------------------------------------------------------------------

def plate_frame(v, f, vn, uv=None):
    """A tank plate (parked nif, full precision: verts, tris, vertex normals, UVs): its emblem frame and outline."""
    v = np.asarray(v, np.float64)
    fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    n = fn.sum(axis=0)
    n /= np.linalg.norm(n)
    up = np.array([0.0, 0.0, 1.0]) - n[2] * n
    up /= np.linalg.norm(up)
    right = np.cross(up, n)
    origin = v.mean(axis=0)
    rel = v - origin
    xy = np.column_stack([rel @ right, rel @ up])
    w = rel @ n
    # the outline: the boundary edges chained into a loop, counter-clockwise in (x, y)
    e = np.sort(np.vstack([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]), axis=1)
    u, cnt = np.unique(e, axis=0, return_counts=True)
    adj = {}
    for a, b in u[cnt == 1]:
        adj.setdefault(int(a), []).append(int(b))
        adj.setdefault(int(b), []).append(int(a))
    start = min(adj)
    loop, prev = [start], None
    while True:
        nxt = [k for k in adj[loop[-1]] if k != prev]
        prev = loop[-1]
        if nxt[0] == start:
            break
        loop.append(nxt[0])
    outline = xy[loop]
    if signed_area_xy(np.column_stack([outline, np.zeros(len(outline))]),
                      np.array([[0, i, i + 1] for i in range(1, len(outline) - 1)])).sum() < 0:
        outline = outline[::-1]
    vn = np.asarray(vn, np.float64)
    vn = vn / np.linalg.norm(vn, axis=1, keepdims=True)
    vn[(vn @ n) < 0] *= -1.0
    return dict(origin=origin, n=n, up=up, right=right, xy=xy, w=w, tris=np.asarray(f, np.int64), vn=vn, outline=outline,
                verts=v, uv=None if uv is None else np.asarray(uv, np.float64))


def uv_to_frame(fr, uv):
    """Points given in the plate's own UVs -> its frame's (x, y), through its triangles (barycentric in UV space; a
    point on no triangle takes the nearest's, clamped)."""
    U, tris = fr["uv"], fr["tris"]
    a, b, c = U[tris[:, 0]], U[tris[:, 1]], U[tris[:, 2]]
    den = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
    out = []
    for px, py in np.asarray(uv, np.float64):
        w0 = ((b[:, 1] - c[:, 1]) * (px - c[:, 0]) + (c[:, 0] - b[:, 0]) * (py - c[:, 1])) / den
        w1 = ((c[:, 1] - a[:, 1]) * (px - c[:, 0]) + (a[:, 0] - c[:, 0]) * (py - c[:, 1])) / den
        w2 = 1.0 - w0 - w1
        W = np.column_stack([w0, w1, w2])
        k = int(np.argmax(W.min(axis=1)))          # the triangle it is deepest in (or nearest outside)
        w = np.clip(W[k], 0.0, None)
        w /= w.sum()
        out.append(w @ fr["xy"][tris[k]])
    return np.array(out)


def field_outline(fr, field_uv, per_edge=1):
    """A ground's field outline (plate UVs) in the plate's frame, counter-clockwise; per_edge > 1 adds points along
    each edge (the map is affine per plate triangle: the dense outline for the checks)."""
    P = np.asarray(field_uv, np.float64)
    pts = []
    for i in range(len(P)):
        for t in np.arange(per_edge) / per_edge:
            pts.append(P[i] + t * (P[(i + 1) % len(P)] - P[i]))
    xy = uv_to_frame(fr, pts)
    area = 0.5 * np.sum(xy[:, 0] * np.roll(xy[:, 1], -1) - np.roll(xy[:, 0], -1) * xy[:, 1])
    return xy if area > 0 else xy[::-1]


def is_convex(poly):
    P = np.asarray(poly, np.float64)
    e = np.roll(P, -1, axis=0) - P
    cross = e[:, 0] * np.roll(e[:, 1], -1) - e[:, 1] * np.roll(e[:, 0], -1)
    return bool((cross > -1e-9).all())


def sd_polygon(poly, pts):
    """The signed distance (negative inside) of points to any simple polygon."""
    return sd_poly(np.asarray(pts)[:, 0], np.asarray(pts)[:, 1], poly)


def inset_polygon(poly, d):
    """A convex counter-clockwise polygon moved in by d (each edge's line moved, neighbours intersected)."""
    P = np.asarray(poly, np.float64)
    n = len(P)
    lines = []
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]
        e = (b - a) / np.linalg.norm(b - a)
        nrm = np.array([-e[1], e[0]])      # inward for a counter-clockwise polygon
        lines.append((a + d * nrm, e))
    out = []
    for i in range(n):
        (p1, e1), (p2, e2) = lines[i - 1], lines[i]
        den = e1[0] * e2[1] - e1[1] * e2[0]
        if abs(den) < 1e-9:
            out.append(p2)
            continue
        t = ((p2[0] - p1[0]) * e2[1] - (p2[1] - p1[1]) * e2[0]) / den
        out.append(p1 + t * e1)
    return np.array(out)


def inside_convex(poly, pts):
    """The least signed distance of each point inside a convex counter-clockwise polygon (negative: outside)."""
    P = np.asarray(poly, np.float64)
    best = np.full(len(pts), np.inf)
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        e = (b - a) / np.linalg.norm(b - a)
        nrm = np.array([-e[1], e[0]])
        best = np.minimum(best, (pts - a) @ nrm)
    return best


def footprint(name, step=0.04):
    """The helmet's footprint (every lattice point over SKIRT) as its convex hull's points."""
    X, Y = lattice(step)
    F = field(name, X, Y)
    pts = np.column_stack([X[F.h > SKIRT + 1e-6], Y[F.h > SKIRT + 1e-6]])
    return hull(pts)


def hull(pts):
    """Andrew's monotone chain: the convex hull, counter-clockwise."""
    p = np.unique(np.round(pts, 9), axis=0)
    p = p[np.lexsort((p[:, 1], p[:, 0]))]

    def half(seq):
        out = []
        for q in seq:
            while len(out) >= 2 and ((out[-1][0] - out[-2][0]) * (q[1] - out[-2][1])
                                     - (out[-1][1] - out[-2][1]) * (q[0] - out[-2][0])) <= 0:
                out.pop()
            out.append(tuple(q))
        return out
    lower, upper = half(p), half(p[::-1])
    return np.array(lower[:-1] + upper[:-1])


def _margins(poly, fp, s, cx, cy):
    """For a convex counter-clockwise polygon: the least distance inside it of the footprint fp scaled by s and moved to
    each centre (cx, cy) (arrays of one shape): per edge the margin is linear in the centre, so all at once."""
    P = np.asarray(poly, np.float64)
    best = np.full(np.shape(cx), np.inf)
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        e = (b - a) / np.linalg.norm(b - a)
        nrm = np.array([-e[1], e[0]])
        best = np.minimum(best, s * float((fp @ nrm).min()) + cx * nrm[0] + cy * nrm[1] - float(a @ nrm))
    return best


def placement(name, frames, inset=INSET, log=print, field_uv=None, field_inset=FIELD_INSET):
    """The scale (at most 1, the same both sides) and each side's centre in its plate frame where the helmet's
    footprint fits: inside its ground's field (field_uv, the plate's UVs) inset field_inset, or without one inside the
    plate's own outline inset `inset` on its forward half. {side: (scale, (cx, cy), margin)}. The largest scale that
    fits both sides; then on each side the centre with the most room (to 0.001), the most forward of those."""
    fp = footprint(name)
    xs = np.arange(-10.0, 10.0001, 0.025)
    ys = np.arange(-4.0, 4.0001, 0.025)
    CX, CY = np.meshgrid(xs, ys)
    fwd = {side: (-1.0 if side == "L" else 1.0) for side in frames}     # the plate's front in its frame (L: -x, R: +x)
    if field_uv is not None:
        polys = {}
        for side, fr in frames.items():
            poly = field_outline(fr, field_uv)
            if not is_convex(poly):
                raise ValueError(f"{name}: the ground's field isn't convex in the {side} plate's frame")
            polys[side] = inset_polygon(poly, field_inset)
        inset, what, half = field_inset, "its ground's enamel field", False
    else:
        polys = {side: inset_polygon(fr["outline"], inset) for side, fr in frames.items()}
        what, half = "the plate's outline", True

    def room(side, s):
        m = _margins(polys[side], fp, s, CX, CY)
        return np.where(CX * fwd[side] >= 0, m, -np.inf) if half else m

    lo, hi = 0.5, 1.0
    if all(room(side, hi).max() >= 0 for side in frames):
        s = hi
    else:
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            if all(room(side, mid).max() >= 0 for side in frames):
                lo = mid
            else:
                hi = mid
        s = math.floor(lo * 1000) / 1000
        if not all(room(side, s).max() >= 0 for side in frames):
            raise ValueError(f"{name}: no placement fits {what} inset {inset}")
    out = {}
    for side in frames:
        m = room(side, s)
        top = np.round(m, 3) >= np.round(m.max(), 3)
        k = np.argmax(np.where(top, CX * fwd[side], -np.inf))
        cx, cy, mm = float(CX.flat[k]), float(CY.flat[k]), float(m.flat[k])
        out[side] = (float(s), (cx, cy), mm)
        log(f"  {name} on the {side} plate: scale {s:.3f} ({DESIGN_W * s:.2f} x {DESIGN_H * s:.2f} nominal), centre "
            f"({cx:+.3f}, {cy:+.3f}) in its frame, {mm:.3f} clear of {what} inset {inset:.3f}")
    return out


def rotate(xy, deg):
    """Points (n, 2) turned deg counter-clockwise about the origin."""
    a = math.radians(deg)
    c, sn = math.cos(a), math.sin(a)
    xy = np.asarray(xy, np.float64)
    return np.column_stack([c * xy[:, 0] - sn * xy[:, 1], sn * xy[:, 0] + c * xy[:, 1]])


def field_axis(fr, field_uv):
    """A ground field's own axis in the plate's frame: its middle line in the plate's UVs (u at the field's middle, from
    its bottom apex to its top) mapped through the plate. Returns (the angle in degrees from the frame's up,
    counter-clockwise; the bottom and top points). The plate's UV axes map square to each other, so this is also square
    with the plate's slant (the flat badges' own up)."""
    P = np.asarray(field_uv, np.float64)
    um = 0.5 * (P[:, 0].min() + P[:, 0].max())
    bot, top = uv_to_frame(fr, [(um, P[:, 1].max()), (um, P[:, 1].min())])   # v down: the larger v is the bottom
    up = (top - bot) / np.linalg.norm(top - bot)
    return math.degrees(math.atan2(-up[0], up[1])), bot, top


def placement_aligned(name, frames, field_uv, field_inset=FIELD_INSET, log=print):
    """Each helmet square with its plate in its ground's field (the author's pick, revising "upright"): turned to the
    field's own axis and centred on it (its centre on the axis line, from bottom apex to top, wherever it has the most
    room: the field is the plate's shape mirrored about its middle, so on the axis is the middle), at the largest scale up
    to SCALE_MAX that fits the field inset field_inset; the same scale both sides (the fields are mirror images).
    {side: (scale, (cx, cy), angle, margin)}."""
    fp = footprint(name)
    t = np.linspace(0.25, 0.75, 501)
    axes, polys = {}, {}
    for side, fr in frames.items():
        poly = field_outline(fr, field_uv)
        if not is_convex(poly):
            raise ValueError(f"{name}: the ground's field isn't convex in the {side} plate's frame")
        polys[side] = inset_polygon(poly, field_inset)
        axes[side] = field_axis(fr, field_uv)

    def room(side, s):
        ang, bot, top = axes[side]
        c = bot[None, :] + t[:, None] * (top - bot)[None, :]
        return _margins(polys[side], rotate(fp, ang), s, c[:, 0], c[:, 1]), c

    def fits(s):
        return all(room(side, s)[0].max() >= 0 for side in frames)

    if fits(SCALE_MAX):
        s = SCALE_MAX
    else:
        lo, hi = 0.3, SCALE_MAX
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if fits(mid) else (lo, mid)
        s = math.floor(lo * 1000) / 1000
        if not fits(s):
            raise ValueError(f"{name}: no centred placement fits its ground's field inset {field_inset}")
    out = {}
    for side in frames:
        m, c = room(side, s)
        best = np.round(m, 3) >= np.round(m.max(), 3)
        k = np.flatnonzero(best)[np.argmin(np.abs(t[best] - 0.5))]   # of the roomiest, the nearest the middle
        ang = axes[side][0]
        out[side] = (float(s), (float(c[k, 0]), float(c[k, 1])), float(ang), float(m[k]))
        log(f"  {name} on the {side} plate: square with it ({ang:+.2f} degrees from upright, the field's own axis), scale "
            f"{s:.3f} ({DESIGN_W * s:.2f} x {DESIGN_H * s:.2f} nominal), centre ({c[k, 0]:+.3f}, {c[k, 1]:+.3f}) in its frame "
            f"({t[k]:.3f} up the field's axis), {m[k]:.3f} clear of its field inset {field_inset:.3f}")
    return out


def cast_on_plate(fr, xy):
    """(x, y) in the plate's frame cast along -n onto its triangles: (w the surface's height along n, the
    interpolated vertex normal there, hit)."""
    pxy, tris, w, vn = fr["xy"], fr["tris"], fr["w"], fr["vn"]
    a, b, c = pxy[tris[:, 0]], pxy[tris[:, 1]], pxy[tris[:, 2]]
    den = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
    k = len(xy)
    W = np.full(k, np.nan)
    N = np.zeros((k, 3))
    hit = np.zeros(k, bool)
    for s in range(0, k, 256):
        px, py = xy[s:s + 256, 0:1], xy[s:s + 256, 1:2]
        w0 = ((b[:, 1] - c[:, 1]) * (px - c[:, 0]) + (c[:, 0] - b[:, 0]) * (py - c[:, 1])) / den
        w1 = ((c[:, 1] - a[:, 1]) * (px - c[:, 0]) + (a[:, 0] - c[:, 0]) * (py - c[:, 1])) / den
        w2 = 1.0 - w0 - w1
        inside = (w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9)
        z = np.where(inside, w0 * w[tris[:, 0]] + w1 * w[tris[:, 1]] + w2 * w[tris[:, 2]], -np.inf)
        j = np.argmax(z, axis=1)
        r = np.arange(len(j))
        got = np.isfinite(z[r, j])
        idx = np.arange(s, s + len(j))[got]
        jj, rr = j[got], r[got]
        bw = np.column_stack([w0[rr, jj], w1[rr, jj], w2[rr, jj]])
        W[idx] = z[rr, jj]
        nn = np.einsum("ij,ijk->ik", bw, vn[tris[jj]])
        N[idx] = nn / np.linalg.norm(nn, axis=1, keepdims=True)
        hit[idx] = True
    return W, N, hit


def unit(a):
    return a / np.maximum(np.linalg.norm(a, axis=-1, keepdims=True), 1e-12)


def split_normals(v, f, deg=SPLIT_DEG):
    """Face normals (area-weighted) at each corner, a vertex split where its corners part by more than deg:
    (verts, tris, normals, source vertex of each)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import harley_meshes as H
    fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    cn = np.repeat(unit(fn), 3, axis=0)
    idx = np.arange(len(v), dtype=np.float64)
    vv, ff, nn = H.split_corners(np.column_stack([v, idx]), f, cn, deg)
    # the area-weighted mean within each group (split_corners' is the plain mean of its corners' unit normals)
    acc = np.zeros((len(vv), 3))
    np.add.at(acc, ff.reshape(-1), np.repeat(fn, 3, axis=0))
    nn = np.where(np.linalg.norm(acc, axis=1, keepdims=True) > 1e-12, unit(acc), nn)
    return vv[:, :3], ff, nn, vv[:, 3].astype(np.int64)


def on_plate(P, fr, scale, centre, angle=0.0):
    """Design points (x, y, h) -> the parked frame: scaled, turned `angle` degrees (counter-clockwise in the plate's
    frame) and placed in it, cast onto the plate, lifted h along its normal there."""
    xy = rotate(P[:, :2] * scale, angle) + np.asarray(centre)
    W, N, hit = cast_on_plate(fr, xy)
    if not hit.all():
        raise ValueError(f"{int((~hit).sum())} points off the plate")
    base = fr["origin"] + xy[:, 0:1] * fr["right"] + xy[:, 1:2] * fr["up"] + W[:, None] * fr["n"]
    return base + P[:, 2:3] * N


def sweep_clearance(v, f, sweep):
    """The least distance from the bar assembly's swept points (parked frame) to a shape's triangles."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from nearest import TriangleGrid
    tris = v[f]
    lo, hi = tris.min(axis=(0, 1)) - 3.0, tris.max(axis=(0, 1)) + 3.0
    q = sweep[np.all((sweep >= lo) & (sweep <= hi), axis=1)]
    if not len(q):
        return np.inf
    return float(TriangleGrid(tris, 1.0).closest(q, reach=1.0)[2].min())


def relief(P, k):
    """The relief k times as deep (the skirt stays under the plate)."""
    Q = P.copy()
    Q[:, 2] = np.where(P[:, 2] > 0.0, P[:, 2] * k, P[:, 2])
    return Q


def build(plates, log=print, step=GRID, target=TARGET, fields="recorded", sweep=None):
    """The four shapes in the parked frame from the parked nif's plates {"L": (v, f, vn, uv), "R": ...}: {label: dict(v,
    f, n, uv, helmet, side, design (the simplified relief (x, y, h)), scale, centre, angle, relief, clearance, error,
    height, width, field_margin)}.
    fields: {helmet: its ground's field outline in the plate's UVs} ("recorded": GROUND_FIELD_UV for both): each helmet
    square with its plate, centred in its field and filling it (placement_aligned), the field's inset measured on the
    cast vertices and tightened until they keep it; None: upright in the plate's own outline (the first fit). sweep: the
    bar assembly's points turned through its range (parked frame): where they come nearer a helmet than MIRROR_CLEAR, its
    relief is made shallower (down to RELIEF_MIN), then the helmet smaller about its centre (never moved)."""
    frames = {side: plate_frame(*plates[side]) for side in ("L", "R")}
    if fields == "recorded":
        fields = {name: GROUND_FIELD_UV for name in HELMETS}
    out = {}
    for name in HELMETS:
        P, f, err = simplified(name, step, target, log=log)
        field_uv = None if fields is None else fields[name]
        if field_uv is None:
            place = {side: (*v[:2], 0.0, v[2]) for side, v in placement(name, frames, log=log).items()}
        else:
            extra = 0.0
            for attempt in range(6):
                place = placement_aligned(name, frames, field_uv, FIELD_INSET + extra, log=log)
                worst = np.inf
                for side, fr in frames.items():
                    s_, centre_, ang_, _ = place[side]
                    rel = on_plate(P, fr, s_, centre_, ang_) - fr["origin"]
                    xy3 = np.column_stack([rel @ fr["right"], rel @ fr["up"]])
                    worst = min(worst, -float(sd_polygon(field_outline(fr, field_uv, 16), xy3).max()))
                if worst >= FIELD_INSET - 0.005:
                    break
                extra += FIELD_INSET - worst + 0.005
                log(f"  {name}: the cast vertices {worst:.3f} inside the field (the lift leans them out): inset "
                    f"{FIELD_INSET + extra:.3f}")
        for label, helmet, side in SHAPES:
            if helmet != name:
                continue
            s, centre, ang, margin = place[side]
            fr = frames[side]
            k, shrinks = 1.0, 0
            while True:
                Pk = relief(P, k)
                v3 = on_plate(Pk, fr, s, centre, ang)
                clear = np.inf if sweep is None else sweep_clearance(v3, f, sweep)
                if clear >= MIRROR_CLEAR + MIRROR_SPARE:
                    break
                if k > RELIEF_MIN + 1e-9:
                    k = round(k - 0.05, 2)
                    log(f"  {label}: the bars' sweep {clear:.2f} from it: its relief x{k:.2f}")
                elif shrinks < 10:
                    shrinks += 1
                    s = math.floor(s * 0.98 * 1000) / 1000
                    log(f"  {label}: the bars' sweep {clear:.2f} from it at the shallowest relief: scale {s:.3f}")
                else:
                    raise ValueError(f"{label}: the bars' sweep {clear:.2f} from it at relief x{k:.2f}, scale {s:.3f}")
            vv, ff, nn, src = split_normals(v3, f)
            uv = uv_of(name, P[src, :2])
            rel = v3 - fr["origin"]
            xy = np.column_stack([rel @ fr["right"], rel @ fr["up"]])   # the cast vertices
            dense = None if field_uv is None else -float(sd_polygon(field_outline(fr, field_uv, 16), xy).max())
            along = rotate(xy - np.asarray(centre), -ang)                # in the helmet's own (turned) frame
            height, width = float(np.ptp(along[:, 1])), float(np.ptp(along[:, 0]))
            out[label] = dict(v=vv, f=ff, n=nn, uv=uv, helmet=name, side=side, design=Pk, design_f=f, src=src,
                              scale=s, centre=centre, angle=ang, relief=k, clearance=clear, margin=margin, error=err,
                              frame=fr, height=height, width=width, field_margin=dense,
                              relief_max=float(Pk[:, 2].max()))
            log(f"  {label}: {len(vv)} vertices (normals split at {SPLIT_DEG:g} degrees), {len(ff)} triangles; scale {s:.3f}, "
                f"{ang:+.2f} degrees, {width:.2f} wide and {height:.2f} tall along its own axes (its skirt's foot), relief "
                f"x{k:.2f} ({Pk[:, 2].max():.2f} over the plate at most)"
                + ("" if dense is None else f", every point (the skirt too) {dense:.3f} inside the ground's field")
                + ("" if sweep is None else f", the bars' sweep {clear:.2f} from it"))
    return out


# --- a preview (no nif needed) -------------------------------------------------------------------------------------------

def shade(h, px, light=(-0.55, 0.65, 0.53)):
    gy, gx = np.gradient(h, px)
    n = np.stack([-gx, gy, np.ones_like(h)], -1)     # row 0 the top: +y is up the image, gradient rows go down
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    L = np.asarray(light) / np.linalg.norm(light)
    return np.clip(n @ L, 0, 1)


def preview(out: Path, step):
    from PIL import Image
    out.mkdir(parents=True, exist_ok=True)
    for name in HELMETS:
        X, Y = lattice(step)
        F = field(name, X, Y)
        s = shade(F.h + F.detail, step)
        img = (np.clip(0.15 + 0.85 * s, 0, 1) * 255).astype(np.uint8)
        img[F.h <= SKIRT + 1e-6] = 40
        Image.fromarray(img).save(out / f"{name}_relief.png")
        hh = np.clip((F.h - SKIRT) / (HEIGHT_MAX - SKIRT), 0, 1)
        Image.fromarray((hh * 255).astype(np.uint8)).save(out / f"{name}_height.png")
        print(f"{name}: h {F.h[F.h > SKIRT].min():.2f}..{F.h.max():.2f}, regions {np.bincount(F.region.reshape(-1))}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preview", type=Path, required=True)
    ap.add_argument("--grid", type=float, default=0.02)
    args = ap.parse_args()
    preview(args.preview, args.grid)
    return 0


if __name__ == "__main__":
    sys.exit(main())
