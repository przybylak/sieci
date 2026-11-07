#!/usr/bin/env python3
"""The bike's pieces of our own: the speedometer's face, needle and hub, the tail and brake
light shells, the under-bar mirrors, and the helpers the mesh build checks them with.

harley_meshes.py builds the bike from the glTF; this module makes the parts the model doesn't
have (or has only as a blank disc), the way headlamp_pieces() makes the headlamp. Every
function takes the worn bike's frame (+Y forward, +X the bike's right, z up, the ground at 0,
the plugin's bike space) and gives pieces in the parked model's frame (front at -Y, +X the
bike's left: parked = (-x, seat_at - y, z), a half turn about z, so a triangle's winding holds),
each a tuple

    (material, label, verts (n, 3) float64, tris (m, 3) int64, normals (n, 3) | None, uvs (m, 3, 2) | None)

material: the per-triangle material id (the 14 palette names, or mirror, dial, needle,
tail_led, brake_led); label: the shape it goes into (<stem>_<label>, harley_meshes.LABELS);
normals: per vertex, outward (None: the build averages them); uvs: per triangle corner, in the
nif's convention (v runs down the image), 0..1 - given only for the labels whose texture is our
own art laid out for them (front_dial, front_dialglow, front_needle, rear_tail, rear_brake;
static_badge through badge_uvs()); None for the labels the texture stage unwraps.

Winding: every triangle winds counter-clockwise seen from outside (its normal by the right-hand
rule points out, as the glTF's and lathe()'s do). With flip (the vanilla nif winding against its
normals) a piece comes pre-flipped, because harley_meshes' shape loop flips every piece to the
vanilla's winding and ours is right already (headlamp_pieces() does the same).

The art the fixed-UV pieces point at comes from bike_art.py, which reads the layout constants
below (DIAL_*, NEEDLE_PATCH, LENS_*, BADGE_*), so the two can't drift apart.

  speedo_pieces(dial_tris_worn, seat_at, flip) -> (pieces, parts_keys)
  lamp_shells(lens_tris_worn, brake_extra_tris_worn, seat_at, flip) -> pieces
  mirror_under_pieces(style, grip, grip_r, clamp, seat_at, flip) -> pieces
  bend_convex(verts, normals, centre, normal, radius) -> normals
  clearance(turning, static, steer_point, steer_axis, bar_angle) -> the least gap
  badge_uvs(verts, tris) -> uvs (m, 3, 2)
  fender_badge_patch(fender, flip) -> (verts, tris, normals, uvs), the rear fender's badge patch (2026-11-07a), parked
      frame in and out
  disc_pieces(centre_yz, x0, x1, r_out, r_hub, flip, bore) -> (verts, tris, normals, uvs), the brake discs (bore "shared"
      at DISC_HUB_REF of the outer radius, art and geometry alike; "bolts" the 2026-11-01a build's, at r_hub)
  plate_uvs(verts, tris) -> uvs (m, 3, 2), static_plate's own (2026-11-08a), parked frame
  plate_text_overlay(face_tris, flip) -> (verts, tris, normals, uvs), static_plateText over the plate's face (2026-11-08a)
  rim_style_pieces(style, wheel, axle, flip) -> [(material, verts, tris, normals, uvs, part)], a rim style's wheel
      (2026-11-08a: RIM_STYLES, parked frame about the axle); rim_check(...) its envelope, hoop, winding and cell

Run it (python3 -I bike_pieces.py) for a self-test of the geometry on synthetic inputs.
"""

import math

import numpy as np

# --- The speedometer --------------------------------------------------------------------------
# The dial reads 0-80 mph over 240 degrees, the zero at the lower left (8 o'clock) and 80 at the
# lower right (4 o'clock), 40 straight up, as the rider sees it. Angles are clockwise from the
# dial's up as the rider sees it (the face's up is world z laid into the dial's plane).
DIAL_ZERO = -120.0     # where 0 mph is (degrees clockwise from up); the needle is modelled pointing here
DIAL_MAX = 240.0       # the sweep from 0 to the top of the scale (degrees)
DIAL_PER_MPH = 3.0     # degrees per mph
DIAL_TOP = 80          # the scale's top (mph) = DIAL_MAX / DIAL_PER_MPH
# The plugin turns the needle by theta = NeedleZero + min(NeedleMax, NeedlePerMph x [Speedo] Scale x
# 0.0319563 x speed) about NeedleAxis (toward the rider), clockwise as the rider sees it. The needle
# is modelled at the zero mark, so NeedleZero is 0.
NEEDLE_ZERO_KEY = 0.0

# Heights over the dial's plane (along its normal, toward the rider). The worn nifs store positions
# as half floats, 0.0625 apart between 64 and 128 (the dial sits at y 65, z 99), so every overlay
# keeps at least 0.25 off what it covers as built (harley_meshes.overlay_gaps checks 0.9 of that as built and
# 0.4 in the half floats).
DIAL_GLOW_H = 0.25     # the lit copy of the face
NEEDLE_H = 0.50        # the needle's underside (its skirt's foot)
NEEDLE_TOP_H = 0.58    # its top edges
NEEDLE_RIDGE_H = 0.64  # its top's centre line
HUB_H = 0.68           # the hub cap's skirt foot (over the needle's root)
HUB_TOP_H = 0.92       # the hub cap's crown
HUB_R = 0.42           # the hub cap's radius

DIAL_SEGMENTS = 48
DIAL_GLOW_R = 3.60     # the lit copy stops where the bezel's chamfer rises over 0.25 (r 3.62 on this model)
NEEDLE_LEN = 0.80      # the blade, pivot to tip, as a fraction of the dial's radius
NEEDLE_TAIL = 0.25     # the counterweight behind the pivot, as a fraction of the radius
NEEDLE_ROOT_W = 0.35   # the blade's width at the pivot (units)
NEEDLE_TIP_W = 0.07    # its width just short of the point
NEEDLE_TAIL_W = 0.48   # the counterweight's width

# The dial's texture (front_dial_d/s/n.png, 512): the face is a disc of radius DIAL_ART_R (a fraction
# of the texture's width) about the middle; the needle's colours sit in a patch in the top right
# corner, outside the disc: u along the needle (counterweight end at u0, tip at u1), v across it.
DIAL_ART_R = 0.49
DIAL_R_MODEL = 3.719   # this model's dial radius (glTF mesh 9), which the art's hub and needle patch are drawn for
NEEDLE_PATCH = (0.855, 0.020, 0.980, 0.145)   # u0, v0, u1, v1

# --- The tail and brake lights ------------------------------------------------------------------
TAIL_OFFSET = 0.25     # the running light's shell over the lens
BRAKE_OFFSET = 0.50    # the brake shell over the lens (over the running light's)
BRAKE_GROW = 1.02      # and grown about each lens's middle, so it covers the running light's edge
LENS_SIDE_DEPTH = 0.6  # a lens's side wall is shelled this far back from its front (the rest is inside its bezel)
LENS_SLIVER = 5.0      # tail lens triangles whose middle is farther than this from the lens's are the stray sliver
# rear_tail / rear_brake textures (256): the tail lens (7.3 x 2.4) in a band across the top, the
# round signal lenses in the square at the bottom left (both share it); u0, v0, u1, v1
LENS_TAIL_BOX = (0.02, 0.02, 0.98, 0.33)
LENS_ROUND_BOX = (0.02, 0.50, 0.48, 0.96)

# --- The mirrors --------------------------------------------------------------------------------
MIRROR_CONVEX_R = 36.0   # the glass's normals as a sphere of this radius behind it (the stock mirror's too)
# The under-bar heads (customisation_design.md section 5, measured on three ride videos, in this
# model's units): a glass 13.5 x 8 in a cup 15 x 9.5 with a rolled 0.6 lip, 3 deep at the inboard
# end and 2 at the outboard, the glass bulging 0.45 (about a sphere of radius 40); a thin rod (1.2)
# from under the switch housing down and out to a ball joint (2) at the head's inboard upper back.
MIRROR_GLASS = (13.5, 8.0)
MIRROR_EGG_TAPER = 0.85          # the egg's outboard end is this much of its inboard end's height
MIRROR_LIP = 0.75                # the cup's outline outside the glass's
MIRROR_DEPTH = (3.0, 2.0)        # the cup's depth at the inboard and outboard ends
MIRROR_SAG = 0.45                # the glass's bulge at its middle
# The +X head's glass faces back, turned 15 degrees in toward the rider and tipped 18 up (the stock
# mirror's faces 23 in): from the rider's eye (about 0, 3, 121) the reflection off its middle then
# runs straight back along the bike's side, 6 degrees under the horizon, so the cube map shows the
# horizon across the glass with sky above and ground below (at the videos' 10 up it showed only ground)
MIRROR_NORMAL = (-0.25, -0.92, 0.30)
MIRROR_SEGMENTS = 36
# Placement, relative to the +X grip's centre (Grip in CMB_BikeParts.ini: 29.4, 38.39, 96.0): the
# head's middle sits under the grip and a little behind it, outboard of the stalk, then lowered
# until the cup's highest point is MIRROR_TOP (the fingers wrapped round the grip reach z 91.7).
# It is 2 further outboard than the videos' measure (x 33, not 31): at 31 the inner mirror comes
# within about 1 of the tank's flank at full lock (BarAngle 20), at 33 the least gap is 1.9-2.1.
# The stalk leaves the switch housing's underside (the clamp point) inboard of the grip's end, so
# it clears the grip's underside by 0.6 or more.
MIRROR_HEAD_OFFSET = (3.6, -1.4, -11.5)
MIRROR_CLAMP_OFFSET = (-7.2, 3.1, -1.9)   # (22.2, 41.5, 94.1) on this model
MIRROR_TOP = 89.0
MIRROR_BALL_AT = (0.55, 0.85, 30.0)   # the ball: the rim point furthest along (-x, y) by these weights, this far round the back (deg)
MIRROR_STALK_R = 0.6
MIRROR_BALL_R = 1.0
MIRROR_STYLES = {"egg": "front_mirrorUnderEgg", "d": "front_mirrorUnderD"}
# [Look] Mirrors -> the label shown (0: none; the rest hidden, by the plugin's speck)
MIRROR_VARIANTS = {1: "front_mirrorStock", 2: "front_mirrorUnderEgg", 3: "front_mirrorUnderD"}

# --- The badge ----------------------------------------------------------------------------------
# static_badge (512): a winged wheel across the middle band for the long tank panels, a roundel
# (the wheel alone) at the bottom for the small rear emblem. An island wider than BADGE_LONG times
# its height is a tank panel.
BADGE_LONG = 1.4
BADGE_BAND_W = 0.96              # a tank panel's width spans this much of the texture (one scale both ways)
BADGE_ROUNDEL = (0.5, 0.83, 0.105)    # u, v, radius of the roundel
BADGE_WHEEL_R = 0.125            # the winged wheel's wheel (radius, texture widths), centred


# --- small geometry helpers ------------------------------------------------------------------------

def unit(a):
    a = np.asarray(a, dtype=np.float64)
    length = np.linalg.norm(a, axis=-1, keepdims=True)
    return a / np.maximum(length, 1e-12)


def to_parked(v, seat_at):
    """Worn -> parked: a half turn about z and the seat's shift."""
    v = np.asarray(v, dtype=np.float64)
    return np.column_stack([-v[:, 0], seat_at - v[:, 1], v[:, 2]])


def normals_to_parked(n):
    n = np.asarray(n, dtype=np.float64)
    return np.column_stack([-n[:, 0], -n[:, 1], n[:, 2]])


def face_normals(v, f):
    t = v[f]
    return np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])


def tri_areas(v, f):
    return 0.5 * np.linalg.norm(face_normals(v, f), axis=1)


def smooth_normals(v, f):
    """Area-weighted vertex normals (by winding)."""
    n = np.zeros_like(v)
    fn = face_normals(v, f)
    for k in range(3):
        np.add.at(n, f[:, k], fn)
    return unit(n)


def mirror_x(v, f, n=None):
    """The other side's copy: x negated, the winding reversed (a reflection turns it inside out)."""
    v2 = v * np.array([-1.0, 1.0, 1.0])
    f2 = f[:, [0, 2, 1]]
    n2 = None if n is None else n * np.array([-1.0, 1.0, 1.0])
    return v2, f2, n2


def grid_strip(rings, closed=True):
    """Triangles joining consecutive rings of vertex indices (each ring a list, all the same
    length), (a[s], b[s], b[s+1]), (a[s], b[s+1], a[s+1]): with the rings running the way that
    makes (ring direction) x (along the strip) point out, these wind outward."""
    tris = []
    for a, b in zip(rings[:-1], rings[1:]):
        m = len(a)
        for s in range(m if closed else m - 1):
            s2 = (s + 1) % m
            tris.append((a[s], b[s], b[s2]))
            tris.append((a[s], b[s2], a[s2]))
    return tris


def orient_outward(v, f, inside):
    """Flip the triangles whose winding normal points toward `inside` (a point within the part)."""
    fn = face_normals(v, f)
    c = v[f].mean(axis=1)
    bad = np.einsum("ij,ij->i", fn, c - inside) < 0
    f = f.copy()
    f[bad] = f[bad][:, [0, 2, 1]]
    return f


def drop_degenerate(v, f, eps=1e-7):
    keep = (tri_areas(v, f) > eps) & (f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])
    return f[keep]


def piece(material, label, v_worn, f, n_worn, uvs, seat_at, flip):
    """Worn-frame geometry -> one parked-frame piece tuple."""
    f = np.asarray(f, dtype=np.int64)
    if flip:
        f = f[:, [0, 2, 1]]
        if uvs is not None:
            uvs = uvs[:, [0, 2, 1]]
    return (material, label, to_parked(v_worn, seat_at), f,
            None if n_worn is None else normals_to_parked(unit(n_worn)),
            None if uvs is None else np.asarray(uvs, dtype=np.float32))


def flat_split(v, f):
    """Every triangle its own three vertices, each with the triangle's normal (hard edges)."""
    v2 = v[f].reshape(-1, 3)
    f2 = np.arange(len(v2)).reshape(-1, 3)
    n2 = np.repeat(unit(face_normals(v, f)), 3, axis=0)
    return v2, f2, n2


def corner_split(v, f, split_deg=45.0):
    """Vertex normals that average only the faces within split_deg of each other at a vertex
    (smoothing groups): a vertex split once per group. Returns (v, f, n, corner index map)."""
    fn = unit(face_normals(v, f))
    area = tri_areas(v, f)
    cos_lim = math.cos(math.radians(split_deg))
    corner_n = np.zeros((len(f), 3, 3))
    by_vertex = [[] for _ in range(len(v))]
    for t in range(len(f)):
        for k in range(3):
            by_vertex[f[t, k]].append(t)
    for vi, ts in enumerate(by_vertex):
        if not ts:
            continue
        ts = np.array(ts)
        dots = fn[ts] @ fn[ts].T
        for j, t in enumerate(ts):
            near = ts[dots[j] >= cos_lim]
            n = (fn[near] * area[near, None]).sum(0)
            k = int(np.where(f[t] == vi)[0][0])
            corner_n[t, k] = n / max(np.linalg.norm(n), 1e-12)
    # one vertex per (vertex, normal rounded)
    key = np.concatenate([f.reshape(-1, 1), np.round(corner_n.reshape(-1, 3) * 1e4)], axis=1)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.reshape(-1)
    v2 = v[f.reshape(-1)[first]]
    n2 = corner_n.reshape(-1, 3)[first]
    f2 = inv.reshape(-1, 3)
    return v2, f2, n2


def weld(tris, tol=1e-4):
    """(m, 3, 3) corner positions -> (v, f) with corners at the same place merged."""
    p = np.asarray(tris, dtype=np.float64).reshape(-1, 3)
    key = np.round(p / tol).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    f = inv.reshape(-1).reshape(-1, 3)
    return p[first], f


def islands(n, f):
    """Connected pieces over shared vertices: a label per triangle."""
    lab = np.arange(n)
    while True:
        m = np.minimum(np.minimum(lab[f[:, 0]], lab[f[:, 1]]), lab[f[:, 2]])
        new = lab.copy()
        for k in range(3):
            np.minimum.at(new, f[:, k], m)
        new = new[new]
        if np.array_equal(new, lab):
            break
        lab = new
    _, tl = np.unique(lab[f[:, 0]], return_inverse=True)
    return tl.reshape(-1)


def plane_frame(normal, up=(0.0, 0.0, 1.0)):
    """(right, up, normal) for a surface seen from its normal's side: up is `up` laid into the
    plane, right = up x normal (the viewer's right)."""
    n = unit(normal)
    u = np.asarray(up, dtype=np.float64)
    u = unit(u - (u @ n) * n)
    return np.cross(u, n), u, n


# --- the speedometer ---------------------------------------------------------------------------------

def dial_frame(dial_tris_worn):
    """The model's dial disc (glTF mesh 9, worn): its middle, its normal toward the rider, its up
    (world z laid into it), its right (the rider's right) and its radius."""
    t = np.asarray(dial_tris_worn, dtype=np.float64).reshape(-1, 3, 3)
    fn = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    a = 0.5 * np.linalg.norm(fn, axis=1)
    n = unit(fn.sum(0))
    if n[1] > 0:   # toward the rider: back (-Y) and up
        n = -n
    c = (t.mean(axis=1) * a[:, None]).sum(0) / a.sum()
    pts = t.reshape(-1, 3) - c
    h = pts @ n
    radius = float(np.linalg.norm(pts - h[:, None] * n, axis=1).max())
    right, up, n = plane_frame(n)
    return c, n, up, right, radius


def dial_uv(points, c, up, right, radius):
    """The dial texture's (u, v) of points on (or over) the dial: a plain projection onto its plane."""
    d = np.asarray(points, dtype=np.float64) - c
    k = DIAL_ART_R / radius
    return np.column_stack([0.5 + (d @ right) * k, 0.5 - (d @ up) * k])


def _needle_stations(radius):
    L, T = NEEDLE_LEN * radius, NEEDLE_TAIL * radius
    hw_tail, hw_root, hw_tip = NEEDLE_TAIL_W / 2, NEEDLE_ROOT_W / 2, NEEDLE_TIP_W / 2
    rr = hw_tail   # the counterweight's round end
    st = []
    for k in range(5):   # round end, from its point to its full width
        a = math.pi / 2 * k / 4
        st.append((-T + rr - rr * math.cos(a), rr * math.sin(a)))
    st.append((-T + rr + 0.30, hw_tail))
    st.append((-0.18, hw_root * 1.05))
    for s in (0.25, 0.30 * L, 0.55 * L, 0.80 * L, 0.95 * L):
        frac = (s - 0.25) / (0.95 * L - 0.25)
        st.append((s, hw_root + (hw_tip - hw_root) * frac))
    st.append((L, 0.0))   # the point
    return st


def needle_geometry(radius):
    """The needle at the dial's zero mark, in dial-plane coordinates (x right, y up, h over the
    face): a tapered blade with a ridge along its top, a counterweight behind the pivot, a skirt
    down to NEEDLE_H all round. Returns (verts (n, 3) as (x, y, h), tris, per-vertex (s, w) for UVs)."""
    st = _needle_stations(radius)
    th = math.radians(DIAL_ZERO)
    d = np.array([math.sin(th), math.cos(th)])      # along the needle (clockwise from up)
    across = np.array([d[1], -d[0]])                 # d turned 90 degrees clockwise: the needle's right
    verts, sw, tris = [], [], []

    def add(s, w, h):
        p = s * d + w * across
        verts.append((p[0], p[1], h))
        sw.append((s, w))
        return len(verts) - 1

    left, mid, right = [], [], []
    for s, hw in st:
        if hw <= 1e-9:
            i = add(s, 0.0, NEEDLE_TOP_H)
            left.append(i)
            mid.append(i)
            right.append(i)
        else:
            left.append(add(s, -hw, NEEDLE_TOP_H))
            mid.append(add(s, 0.0, NEEDLE_RIDGE_H if hw > 0.02 else NEEDLE_TOP_H))
            right.append(add(s, hw, NEEDLE_TOP_H))
    for i in range(len(st) - 1):   # the top, as two ridged strips
        tris += [(left[i], left[i + 1], mid[i + 1]), (left[i], mid[i + 1], mid[i]),
                 (mid[i], mid[i + 1], right[i + 1]), (mid[i], right[i + 1], right[i])]
    # the outline round: left side tail->tip, then right side tip->tail
    ring = left + right[::-1][1:-1]
    ring_sw = [sw[i] for i in ring]
    foot = [add(s, w, NEEDLE_H) for s, w in ring_sw]
    m = len(ring)
    for k in range(m):
        k2 = (k + 1) % m
        a, b, c2, e = ring[k], ring[k2], foot[k2], foot[k]
        tris += [(a, e, c2), (a, c2, b)]
    v = np.array(verts)
    f = np.array(tris, dtype=np.int64)
    # wind the top's triangles up (+h) and the skirt's out from the needle's centre line
    v3 = v
    f = drop_degenerate(v3, f, 1e-9)
    fn = face_normals(v3, f)
    cen = v3[f].mean(axis=1)
    # the top faces must face +h; the skirt faces out from the centre line
    top = np.abs(unit(fn)[:, 2]) > 0.5
    flip_top = top & (fn[:, 2] < 0)
    s_c = (cen[:, :2] @ d)
    on_line = np.outer(s_c, d)
    out = cen[:, :2] - on_line
    flip_side = (~top) & (np.einsum("ij,ij->i", fn[:, :2], out) < 0)
    f[flip_top | flip_side] = f[flip_top | flip_side][:, [0, 2, 1]]
    return v3, f, np.array(sw)


def speedo_pieces(dial_tris_worn, seat_at, flip):
    """Our speedometer over the model's blank dial (glTF mesh 9, which the build drops): the face
    (front_dial, a disc of DIAL_SEGMENTS in the dial's plane, the art's planar UVs), the hub cap
    (front_dial, over the needle's root, the art's middle), the lit copy of the face (front_dialglow,
    DIAL_GLOW_H over it, the same UVs: its glow map lights the numerals and ticks) and the needle
    (front_needle, at the zero mark, its UVs in the needle patch). Returns (pieces, parts_keys):
    parts_keys are CMB_BikeParts.ini's Needle* lines (worn), as {key: value string}."""
    c, n, up, right, radius = dial_frame(dial_tris_worn)

    def world(x, y, h):
        return c + np.outer(x, right) + np.outer(y, up) + np.outer(h, n)

    pieces = []
    # the face and its lit copy: a fan
    ang = np.linspace(0.0, 2 * math.pi, DIAL_SEGMENTS, endpoint=False)
    for label, r, h in (("front_dial", radius, 0.0), ("front_dialglow", min(DIAL_GLOW_R, radius), DIAL_GLOW_H)):
        x = np.r_[0.0, r * np.sin(ang)]
        y = np.r_[0.0, r * np.cos(ang)]
        v = world(x, y, np.full(len(x), h))
        # the ring runs clockwise as the rider sees it (sin, cos): (centre, next, this) is counter-clockwise
        f = np.array([(0, 1 + (k + 1) % DIAL_SEGMENTS, 1 + k) for k in range(DIAL_SEGMENTS)], dtype=np.int64)
        assert np.all(face_normals(v, f) @ n > 0)
        uv = dial_uv(v, c, up, right, radius)[f]
        pieces.append(piece("dial", label, v, f, np.tile(n, (len(v), 1)), uv, seat_at, flip))
    # the hub cap: a short drum with a domed top, about the dial's normal
    prof = [(HUB_R, HUB_H), (HUB_R, HUB_H + 0.10), (HUB_R * 0.86, HUB_H + 0.18), (HUB_R * 0.52, HUB_TOP_H - 0.02), (0.0, HUB_TOP_H)]
    segs = 16
    rings, hv = [], []
    for r, h in prof:
        ring = []
        for k in range(segs):
            a = 2 * math.pi * k / segs
            ring.append(len(hv))
            hv.append((r * math.sin(a), r * math.cos(a), h))
        rings.append(ring)
    hv = np.array(hv)
    hf = drop_degenerate(hv, np.array(grid_strip(rings), dtype=np.int64), 1e-9)
    v = world(hv[:, 0], hv[:, 1], hv[:, 2])
    hf = orient_outward(v, hf, c + n * (HUB_H - 0.3))
    hn = smooth_normals(v, hf)
    pieces.append(piece("dial", "front_dial", v, hf, hn, dial_uv(v, c, up, right, radius)[hf], seat_at, flip))
    # the needle
    nv, nf, sw = needle_geometry(radius)
    v = world(nv[:, 0], nv[:, 1], nv[:, 2])
    s_lo, s_hi = -NEEDLE_TAIL * radius, NEEDLE_LEN * radius
    w_max = NEEDLE_TAIL_W / 2
    u0, v0, u1, v1 = NEEDLE_PATCH
    pad_u, pad_v = 0.06 * (u1 - u0), 0.10 * (v1 - v0)
    uu = u0 + pad_u + (sw[:, 0] - s_lo) / (s_hi - s_lo) * (u1 - u0 - 2 * pad_u)
    vv = v0 + pad_v + (sw[:, 1] / w_max * 0.5 + 0.5) * (v1 - v0 - 2 * pad_v)
    uvn = np.column_stack([uu, vv])
    fv, ff, fnrm = flat_split(v, nf)   # hard edges: the ridge and the skirt read as facets
    pieces.append(piece("needle", "front_needle", fv, ff, fnrm, uvn[nf], seat_at, flip))
    pivot = c + n * NEEDLE_H
    keys = {
        "NeedlePoint": ",".join(f"{round(float(x), 2) + 0.0:.2f}" for x in pivot),
        "NeedleAxis": ",".join(f"{round(float(x), 4) + 0.0:.4f}" for x in n),
        "NeedleZero": f"{NEEDLE_ZERO_KEY:g}",
        "NeedleMax": f"{DIAL_MAX:g}",
        "NeedlePerMph": f"{DIAL_PER_MPH:g}",
    }
    return pieces, keys


def needle_sphere(parts_keys, radius=None):
    """The needle shape's culling sphere (worn): on the pivot, the needle's length plus 1, so its
    sweep never leaves it (the plugin grows a sphere only by how far its centre moves)."""
    p = np.array([float(t) for t in parts_keys["NeedlePoint"].split(",")])
    r = (radius if radius is not None else DIAL_R_MODEL) * NEEDLE_LEN + 1.0
    return p, r


def overlay_heights(verts_worn, dial_tris_worn):
    """(min, max) height of points over the dial's plane (worn): for the build's offset checks."""
    c, n, _, _, _ = dial_frame(dial_tris_worn)
    h = (np.asarray(verts_worn) - c) @ n
    return float(h.min()), float(h.max())


# --- the tail and brake lights -------------------------------------------------------------------------

def _shell(tris_worn, offset, grow, drop_sliver):
    """One lens's shell: its rearward-facing triangles (the front and the first LENS_SIDE_DEPTH of
    its side wall), each vertex pushed `offset` out along its welded normal (mitred, so the flat
    front sits exactly `offset` off), grown by `grow` about the lens's middle. Returns
    [(v, f, n, (xmin, xmax, zmin, zmax))] per island."""
    v, f = weld(tris_worn)
    f = drop_degenerate(v, f, 1e-10)
    tl = islands(len(v), f)
    out = []
    for isl in range(tl.max() + 1):
        fi = f[tl == isl]
        cen = v[fi].mean(axis=1)
        if drop_sliver:
            mid = np.median(cen, axis=0)
            fi = fi[np.linalg.norm(cen - mid, axis=1) <= LENS_SLIVER]
            cen = v[fi].mean(axis=1)
        if len(fi) == 0:
            continue
        fn = unit(face_normals(v, fi))
        front_y = v[np.unique(fi)][:, 1].min()
        rear_facing = fn[:, 1] < -0.5
        side = (np.abs(fn[:, 1]) <= 0.5) & (v[fi][:, :, 1].max(axis=1) <= front_y + LENS_SIDE_DEPTH)
        fi = fi[rear_facing | side]
        if len(fi) == 0:
            continue
        used = np.unique(fi)
        remap = np.full(len(v), -1)
        remap[used] = np.arange(len(used))
        vv, ff = v[used], remap[fi]
        # welded normal and the mitre factor (the largest of 1/cos to its faces, capped at 2)
        fnn = unit(face_normals(vv, ff))
        area = tri_areas(vv, ff)
        acc = np.zeros_like(vv)
        for k in range(3):
            np.add.at(acc, ff[:, k], fnn * area[:, None])
        nv = unit(acc)
        mit = np.ones(len(vv))
        for k in range(3):
            cosang = np.einsum("ij,ij->i", nv[ff[:, k]], fnn)
            np.maximum.at(mit, ff[:, k], 1.0 / np.clip(cosang, 0.5, 1.0))
        moved = vv + nv * (offset * mit)[:, None]
        mid = vv.mean(axis=0)
        moved = mid + (moved - mid) * grow
        box = (vv[:, 0].min(), vv[:, 0].max(), vv[:, 2].min(), vv[:, 2].max())
        sv, sf, sn = corner_split(moved, ff, 45.0)
        out.append((sv, sf, sn, box))
    return out


def _lens_uvs(v, f, box, region):
    """Planar along -Y (the lens seen from behind: the viewer's right is -X), the lens's x/z extent
    filling `region` (u0, v0, u1, v1) of the texture."""
    xmin, xmax, zmin, zmax = box
    u0, v0, u1, v1 = region
    p = v[f]
    u = u0 + (xmax - p[:, :, 0]) / max(xmax - xmin, 1e-9) * (u1 - u0)
    w = v0 + (zmax - p[:, :, 2]) / max(zmax - zmin, 1e-9) * (v1 - v0)
    return np.stack([np.clip(u, u0, u1), np.clip(w, v0, v1)], axis=-1)


def lamp_shells(lens_tris_worn, brake_extra_tris_worn, seat_at, flip):
    """The running light and the brake light: shells over the red lenses (which stay in
    static_glass, unchanged), lit by their glow maps. rear_tail: the tail lens's (glTF mesh 95's rear
    piece, the stray sliver of triangles reaching forward under the fender dropped) TAIL_OFFSET out;
    rear_brake: the tail lens's and both rear signal lenses' (mesh 34, US-style run/brake/turn
    lamps) BRAKE_OFFSET out, grown BRAKE_GROW. UVs: the lens seen from behind laid over its box
    of the lens art (LENS_TAIL_BOX, LENS_ROUND_BOX)."""
    pieces = []
    for sv, sf, sn, box in _shell(lens_tris_worn, TAIL_OFFSET, 1.0, True):
        pieces.append(piece("tail_led", "rear_tail", sv, sf, sn, _lens_uvs(sv, sf, box, LENS_TAIL_BOX), seat_at, flip))
    for sv, sf, sn, box in _shell(lens_tris_worn, BRAKE_OFFSET, BRAKE_GROW, True):
        pieces.append(piece("brake_led", "rear_brake", sv, sf, sn, _lens_uvs(sv, sf, box, LENS_TAIL_BOX), seat_at, flip))
    if brake_extra_tris_worn is not None and len(brake_extra_tris_worn):
        for sv, sf, sn, box in _shell(brake_extra_tris_worn, BRAKE_OFFSET, BRAKE_GROW, False):
            pieces.append(piece("brake_led", "rear_brake", sv, sf, sn, _lens_uvs(sv, sf, box, LENS_ROUND_BOX), seat_at, flip))
    return pieces


# --- the mirrors ---------------------------------------------------------------------------------------

def bend_convex(verts, normals, centre, normal, radius):
    """Normals of a convex mirror: each vertex's from a sphere of `radius` whose middle is
    `radius` behind `centre` along `normal` (the glass's, toward the viewer), so the cube map
    shades across the glass instead of showing one flat colour. Kept on the side the given
    normals face (any frame: all in the same one)."""
    v = np.asarray(verts, dtype=np.float64)
    nn = unit(normal)
    sphere = np.asarray(centre, dtype=np.float64) - nn * float(radius)
    out = unit(v - sphere)
    if normals is not None:
        old = np.asarray(normals, dtype=np.float64)
        back = np.einsum("ij,ij->i", out, old) < 0
        out[back] = -out[back]
    return out


def _resample(pts, n, bend=1.2):
    """A closed outline resampled to n points, spaced by arc length plus `bend` units per radian of
    turning (so the tight ends get more of them), starting at its outboard point."""
    p = np.asarray(pts)
    seg = np.roll(p, -1, axis=0) - p
    length = np.linalg.norm(seg, axis=1)
    ang = np.arctan2(seg[:, 1], seg[:, 0])
    turn = np.abs((np.diff(np.r_[ang, ang[0]]) + np.pi) % (2 * np.pi) - np.pi)
    w = length + bend * turn
    cum = np.r_[0.0, np.cumsum(w)]
    start = int(np.argmax(p[:, 0]))
    t0 = cum[start]
    targets = (t0 + np.arange(n) * cum[-1] / n) % cum[-1]
    out = []
    for t in targets:
        k = int(np.searchsorted(cum, t, side="right") - 1)
        k = min(k, len(p) - 1)
        frac = (t - cum[k]) / max(cum[k + 1] - cum[k], 1e-12)
        out.append(p[k] + frac * seg[k])
    return np.array(out)


def mirror_outline(style, n=MIRROR_SEGMENTS):
    """The glass's outline (x outboard, y up, centred on the glass's box), counter-clockwise seen
    from the glass's side. egg: an ellipse MIRROR_GLASS across whose height falls off to
    MIRROR_EGG_TAPER at the outboard end (paris and autumn); d: a teardrop (daily) with a straight,
    level top, a round inboard end (a half circle), and a bottom sweeping up in a quarter ellipse into
    a rounded point (radius 1.2) outboard, just under the top's line."""
    W, H = MIRROR_GLASS
    a, b = W / 2, H / 2
    if style == "egg":
        t = np.linspace(0, 2 * math.pi, 1440, endpoint=False)
        x = a * np.cos(t)
        s = 1.0 - (1.0 - MIRROR_EGG_TAPER) * (x / a + 1) / 2
        pts = np.column_stack([x, b * np.sin(t) * s])
    else:
        rt = 1.2                      # the point's radius
        xi, yt = -a + b, b - rt       # the inboard half circle's middle; the point's height
        segs = []
        t = np.linspace(math.pi / 2, 3 * math.pi / 2, 240)          # inboard end: top round to bottom
        segs.append(np.column_stack([xi + b * np.cos(t), b * np.sin(t)]))
        t = np.linspace(0.0, math.pi / 2, 360)[1:]                    # the bottom: a quarter ellipse up to the point
        segs.append(np.column_stack([xi + (a - xi) * np.sin(t), yt - (yt + b) * np.cos(t)]))
        t = np.linspace(0.0, math.pi / 2, 60)[1:]                     # the point, round into the top
        segs.append(np.column_stack([a - rt + rt * np.cos(t), yt + rt * np.sin(t)]))
        x = np.linspace(a - rt, xi, 240)[1:-1]                        # the top, back to the start
        segs.append(np.column_stack([x, np.full_like(x, b)]))
        pts = np.vstack(segs)
    lo, hi = pts.min(0), pts.max(0)
    pts = pts - (lo + hi) / 2
    pts = pts * np.array([W / (hi[0] - lo[0]), H / (hi[1] - lo[1])])
    return _resample(pts, n)


def _offset2d(o, d):
    """A closed counter-clockwise outline pushed d out along its normals."""
    t = np.roll(o, -1, axis=0) - np.roll(o, 1, axis=0)
    nrm = unit(np.column_stack([t[:, 1], -t[:, 0]]))
    return o + d * nrm


def _ring_world(frame, xy, h):
    C, A, B, N = frame
    xy = np.asarray(xy)
    h = np.broadcast_to(np.asarray(h, dtype=np.float64), (len(xy),))
    return C + np.outer(xy[:, 0], A) + np.outer(xy[:, 1], B) + np.outer(h, N)


def _cylinder(p0, p1, r0, r1, sides, caps=(False, False), phase=0.0):
    """A tube from p0 to p1 (radii r0, r1), outward winding; caps close the ends."""
    ax = unit(np.asarray(p1) - np.asarray(p0))
    ref = np.array([0.0, 0.0, 1.0]) if abs(ax[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    e1 = unit(np.cross(ax, ref))
    e2 = np.cross(ax, e1)
    verts, rings = [], []
    for p, r in ((p0, r0), (p1, r1)):
        ring = []
        for k in range(sides):
            a = 2 * math.pi * k / sides + phase
            ring.append(len(verts))
            verts.append(np.asarray(p) + r * (math.cos(a) * e1 + math.sin(a) * e2))
        rings.append(ring)
    tris = grid_strip(rings)
    for end, (p, ring) in enumerate(zip((p0, p1), rings)):
        if caps[end]:
            ci = len(verts)
            verts.append(np.asarray(p, dtype=np.float64))
            for k in range(sides):
                tris.append((ci, ring[k], ring[(k + 1) % sides]))
    v = np.array(verts)
    f = np.array(tris, dtype=np.int64)
    mid = (np.asarray(p0) + np.asarray(p1)) / 2
    f = orient_outward(v, f, mid)
    return v, f


def _sphere(c, r, seg=8, rings=6):
    verts = [np.asarray(c) + np.array([0.0, 0.0, r])]
    for i in range(1, rings):
        phi = math.pi * i / rings
        for k in range(seg):
            a = 2 * math.pi * k / seg
            verts.append(np.asarray(c) + r * np.array([math.sin(phi) * math.cos(a), math.sin(phi) * math.sin(a), math.cos(phi)]))
    verts.append(np.asarray(c) + np.array([0.0, 0.0, -r]))
    tris = []
    for k in range(seg):
        tris.append((0, 1 + k, 1 + (k + 1) % seg))
    for i in range(rings - 2):
        a0, b0 = 1 + i * seg, 1 + (i + 1) * seg
        for k in range(seg):
            k2 = (k + 1) % seg
            tris += [(a0 + k, b0 + k, b0 + k2), (a0 + k, b0 + k2, a0 + k2)]
    last = len(verts) - 1
    base = 1 + (rings - 2) * seg
    for k in range(seg):
        tris.append((last, base + (k + 1) % seg, base + k))
    v = np.array(verts)
    f = orient_outward(v, np.array(tris, dtype=np.int64), np.asarray(c))
    return v, f


def _smooth(v, f):
    return v, f, smooth_normals(v, f)


def mirror_head(style, frame):
    """One under-bar head (the +X side), worn: [(material, v, f, n)] for the cup, the glass and the
    socket the ball sits in. frame = (C, A, B, N): the glass's middle, outboard, up and its normal."""
    o = mirror_outline(style)
    m = len(o)
    W = MIRROR_GLASS[0]
    d_in, d_out = MIRROR_DEPTH

    def depth(x):
        return (d_in + d_out) / 2 - (d_in - d_out) * np.clip(x / W, -0.5, 0.5)

    # the glass: a shallow dome over the outline (rho = 1 at the edge), normals from bend_convex
    ring_k = (1.0, 0.62, 0.28)
    gv = [_ring_world(frame, o * k, MIRROR_SAG * (1 - k * k)) for k in ring_k]
    gv.append(_ring_world(frame, np.zeros((1, 2)), MIRROR_SAG))
    gv = np.vstack(gv)
    rings = [list(range(i * m, (i + 1) * m)) for i in range(len(ring_k))]
    gf = grid_strip(rings)
    centre_i = len(ring_k) * m
    gf += [(rings[-1][k], centre_i, rings[-1][(k + 1) % m]) for k in range(m)]   # wound as grid_strip's
    gf = np.array(gf, dtype=np.int64)
    C, A, B, N = frame
    if (face_normals(gv, gf) @ N).sum() < 0:   # the glass faces the rider (+N)
        gf = gf[:, [0, 2, 1]]
    gn = bend_convex(gv, np.tile(N, (len(gv), 1)), C + N * MIRROR_SAG, N, MIRROR_CONVEX_R)
    # the cup: a rolled lip round the glass, then a smooth back; rings from the glass's edge out and back
    lip = [(-0.18, 0.10), (0.05, 0.40), (0.35, 0.50), (0.62, 0.32), (MIRROR_LIP, -0.05)]
    cv = [_ring_world(frame, _offset2d(o, dx), h) for dx, h in lip]
    rim = _offset2d(o, MIRROR_LIP + 0.02)
    mid2 = rim.mean(axis=0)
    for phi in (22.0, 45.0, 66.0, 82.0):
        k = math.cos(math.radians(phi))
        xy = mid2 + (rim - mid2) * k
        cv.append(_ring_world(frame, xy, -0.25 - depth(xy[:, 0]) * math.sin(math.radians(phi))))
    cv.append(_ring_world(frame, mid2[None, :], -0.25 - depth(np.array([mid2[0]]))))
    cv = np.vstack(cv)
    nr = len(lip) + 4
    rings = [list(range(i * m, (i + 1) * m)) for i in range(nr)]
    cf = grid_strip(rings)
    pole = nr * m
    cf += [(pole, rings[-1][(k + 1) % m], rings[-1][k]) for k in range(m)]
    cf = np.array(cf, dtype=np.int64)
    # one sheet, wound alike throughout by grid_strip: turned as a whole so its back faces away from
    # the cup's inside (then the lip's inner wall faces the glass, its crown the rider)
    back = cf[len(lip) * 2 * m:]
    fn = face_normals(cv, back)
    if np.einsum("ij,ij->i", fn, cv[back].mean(axis=1) - (C - N * 0.8)).sum() < 0:
        cf = cf[:, [0, 2, 1]]
    cn = smooth_normals(cv, cf)
    return o, [("black_m", cv, cf, cn), ("mirror", gv, gf, gn)], depth


def mirror_side(style, grip, clamp=None, outboard=0.0):
    """The +X side's under-bar mirror, worn: [(material, v, f, n)] and a few numbers (the head's
    frame, the clamp point, the ball). The head hangs under the grip, its top at MIRROR_TOP at
    most; the stalk runs from `clamp` (the switch housing's underside) down and out to a ball at
    the cup's inboard upper back."""
    grip = np.asarray(grip, dtype=np.float64)
    N = unit(MIRROR_NORMAL)
    A = unit(np.array([1.0, 0.0, 0.0]) - N[0] * N)
    B = np.cross(N, A)
    C = grip + np.array(MIRROR_HEAD_OFFSET) + np.array([outboard, 0.0, 0.0])
    frame = (C, A, B, N)
    o, parts, depth = mirror_head(style, frame)
    top = max(p[1][:, 2].max() for p in parts)
    if top > MIRROR_TOP:   # lower the whole head so its top is at MIRROR_TOP
        dz = top - MIRROR_TOP
        C = C - np.array([0.0, 0.0, dz])
        frame = (C, A, B, N)
        o, parts, depth = mirror_head(style, frame)
    # the ball: on the cup's back at its inboard upper end
    rim = _offset2d(o, MIRROR_LIP + 0.02)
    mid2 = rim.mean(axis=0)
    pick = int(np.argmax(-MIRROR_BALL_AT[0] * rim[:, 0] + MIRROR_BALL_AT[1] * rim[:, 1]))   # the inboard-upper point of the rim
    phi = math.radians(MIRROR_BALL_AT[2])
    xy = mid2 + (rim[pick] - mid2) * math.cos(phi)
    h = -0.25 - depth(np.array([xy[0]]))[0] * math.sin(phi)
    on_shell = _ring_world(frame, xy[None, :], h)[0]
    inside = C - N * 0.8
    ball_c = on_shell + unit(on_shell - inside) * (MIRROR_BALL_R * 0.45)
    foot = np.asarray(clamp, dtype=np.float64) if clamp is not None else grip + np.array(MIRROR_CLAMP_OFFSET)
    axis = unit(ball_c - foot)
    # the socket the ball sits in: a short collar out of the shell toward the stalk
    sock0 = ball_c - axis * (MIRROR_BALL_R * 0.55)
    sv, sf = _cylinder(sock0 - unit(ball_c - inside) * 0.5, ball_c + axis * 0.05, 1.25, 1.12, 10, caps=(False, False))
    parts.append(("black_m",) + _smooth(sv, sf))
    bv, bf = _sphere(ball_c, MIRROR_BALL_R, 10, 6)
    parts.append(("black_m",) + _smooth(bv, bf))
    # the stalk: a thin rod, slightly thicker at the top, from inside the mount to inside the ball
    stalk_top = foot + axis * 1.2
    tv, tf = _cylinder(stalk_top, ball_c - axis * 0.4, MIRROR_STALK_R * 1.08, MIRROR_STALK_R, 8)
    parts.append(("black_m",) + _smooth(tv, tf))
    # the mount: a round boss under the housing and a hex lock nut below it
    mv, mf = _cylinder(foot - axis * 0.4, foot + axis * 1.0, 1.0, 1.0, 10, caps=(False, True))
    parts.append(("black_m",) + _smooth(mv, mf))
    nv, nf = _cylinder(foot + axis * 1.0, foot + axis * 1.55, 0.92, 0.92, 6, caps=(True, True), phase=math.pi / 6)
    parts.append(("black_m",) + flat_split(nv, nf))
    info = dict(centre=C, normal=N, outboard_axis=A, up=B, clamp=foot, ball=ball_c,
                stalk_len=float(np.linalg.norm(ball_c - foot)),
                stalk_down_deg=float(math.degrees(math.asin(max(-1.0, min(1.0, -axis[2]))))),
                top=float(max(p[1][:, 2].max() for p in parts[:2])))
    return parts, info


def mirror_under_pieces(style, grip, grip_r, clamp, seat_at, flip, outboard=0.0):
    """Both under-bar mirrors of one style ("egg" or "d"; 2/3 as in [Look] Mirrors), label
    front_mirrorUnderEgg / front_mirrorUnderD: per side the cup with its stalk, ball and mount
    (black_m) and the convex glass (mirror). grip: the +X grip's centre (worn; Grip in
    CMB_BikeParts.ini); grip_r: its radius (2.3 on this model; the sizes are this model's, the
    place follows the grip); clamp: where the stalk leaves the switch housing (worn, +X side; None:
    MIRROR_CLAMP_OFFSET from the grip). The -X side is the mirror image."""
    key = {2: "egg", 3: "d", "2": "egg", "3": "d"}.get(style, str(style).lower())
    if key not in MIRROR_STYLES:
        raise ValueError(f"mirror style {style!r}: egg or d")
    label = MIRROR_STYLES[key]
    if grip_r is not None and np.ndim(grip_r) == 1 and len(grip_r) == 3 and np.ndim(grip) == 0:
        grip, grip_r = grip_r, grip   # (radius, point) given the other way round
    parts, _ = mirror_side(key, grip, clamp, outboard)
    pieces = []
    for mat, v, f, n in parts:
        pieces.append(piece(mat, label, v, f, n, None, seat_at, flip))
        v2, f2, n2 = mirror_x(v, f, n)
        pieces.append(piece(mat, label, v2, f2, n2, None, seat_at, flip))
    return pieces


# --- clearance ----------------------------------------------------------------------------------------

def _as_tris(x):
    """Points (n, 3), triangles (m, 3, 3) or a (verts, tris) pair -> (points to test, triangles or None)."""
    if isinstance(x, (tuple, list)) and len(x) == 2 and np.ndim(x[1]) == 2:
        v = np.asarray(x[0], dtype=np.float64)
        f = np.asarray(x[1], dtype=np.int64)
        t = v[f]
        pts = np.vstack([v, t.mean(axis=1), (t[:, 0] + t[:, 1]) / 2, (t[:, 1] + t[:, 2]) / 2, (t[:, 2] + t[:, 0]) / 2])
        return pts, t
    a = np.asarray(x, dtype=np.float64)
    if a.ndim == 3:
        pts = np.vstack([a.reshape(-1, 3), a.mean(axis=1)])
        return pts, a
    return a.reshape(-1, 3), None


def _rotation(axis, deg):
    u = unit(axis)
    a = math.radians(deg)
    c, s, k = math.cos(a), math.sin(a), 1 - math.cos(a)
    return np.array([[c + u[0] * u[0] * k, u[0] * u[1] * k - u[2] * s, u[0] * u[2] * k + u[1] * s],
                     [u[1] * u[0] * k + u[2] * s, c + u[1] * u[1] * k, u[1] * u[2] * k - u[0] * s],
                     [u[2] * u[0] * k - u[1] * s, u[2] * u[1] * k + u[0] * s, c + u[2] * u[2] * k]])


class _Near:
    """Distances from points to a fixed set of triangles (nearest.py's grid), only within `margin`
    of them: farther reads as inf."""

    def __init__(self, tris, margin):
        from nearest import TriangleGrid
        self.margin = margin
        self.ok = len(tris) > 0
        if not self.ok:
            return
        self.lo = tris.min(axis=(0, 1)) - margin
        self.hi = tris.max(axis=(0, 1)) + margin
        # cells no smaller than a third of the margin: a search out to the margin then looks at a few
        # hundred cells a point, whatever the triangles' size
        self.edge = max(margin / 3.0, 2.0 * float(np.median(np.linalg.norm(tris[:, 1] - tris[:, 0], axis=1))))
        self.grid = TriangleGrid(tris, self.edge)

    def least(self, pts):
        if not self.ok:
            return math.inf, None
        p = pts[np.all((pts >= self.lo) & (pts <= self.hi), axis=1)]
        if len(p) == 0:
            return math.inf, None
        _, _, d = self.grid.closest(p, self.edge)
        j = int(np.argmin(d))
        return (float(d[j]), p[j]) if d[j] <= self.margin else (math.inf, None)


def _within(tris, lo, hi):
    return tris[np.all((tris.max(axis=1) >= lo) & (tris.min(axis=1) <= hi), axis=1)]


def clearance(turning, static, steer_point, steer_axis, bar_angle, step=1.0, margin=8.0, detail=False):
    """The least gap between a part that turns with the bars and a fixed one over every bar angle
    from -bar_angle to +bar_angle (every `step` degrees, both ends included), the turn about
    steer_axis through steer_point as the plugin makes it. turning / static: points (n, 3),
    triangles (m, 3, 3) or (verts, tris); with triangles on a side the gap is to its surface (the
    other's vertices, edge midpoints and triangle middles against it, both ways), else between
    points. A gap over `margin` reads as inf. With detail: (gap, angle, the nearest point: on the
    turning part at that angle, or on the fixed one)."""
    tp, tt = _as_tris(turning)
    sp, st = _as_tris(static)
    P = np.asarray(steer_point, dtype=np.float64)
    n = max(1, int(math.ceil(abs(bar_angle) / step))) if bar_angle else 0
    angles = np.linspace(-abs(bar_angle), abs(bar_angle), 2 * n + 1) if n else np.array([0.0])
    rots = [_rotation(steer_axis, a) for a in angles]
    swept = np.vstack([(tp - P) @ R.T + P for R in rots])
    lo, hi = swept.min(0) - margin, swept.max(0) + margin
    near_static = _Near(_within(st, lo, hi), margin) if st is not None else None
    near_turning = _Near(tt, margin) if tt is not None else None
    sp_near = sp[np.all((sp >= lo) & (sp <= hi), axis=1)]
    best = (math.inf, 0.0, None)
    for ang, R in zip(angles, rots):
        cands = []
        tp_r = (tp - P) @ R.T + P
        if near_static is not None:
            cands.append(near_static.least(tp_r))
        if near_turning is not None and len(sp_near):
            d, w = near_turning.least((sp_near - P) @ R + P)   # the fixed part turned back instead
            cands.append((d, w if w is None else (w - P) @ R.T + P))
        if near_static is None and near_turning is None and len(sp_near):
            d2 = ((tp_r[:, None, :] - sp_near[None, :, :]) ** 2).sum(-1)
            i, j = np.unravel_index(np.argmin(d2), d2.shape)
            if d2[i, j] <= margin * margin:
                cands.append((math.sqrt(d2[i, j]), tp_r[i]))
        for d, w in cands:
            if d < best[0]:
                best = (d, float(ang), w)
    return best if detail else best[0]


# --- the badge ------------------------------------------------------------------------------------------

def badge_uvs(verts, tris):
    """Fixed UVs for static_badge (the model's blank badges: the two tank panels, glTF mesh 2, and
    the rear fender's emblem, mesh 1), per triangle corner (m, 3, 2), nif convention. Each island
    is laid flat on its own plane, seen from outside with world z up (so neither side reads
    mirrored), turned so its long axis runs across, at one scale both ways: a long island (a tank
    panel, wider than BADGE_LONG times
    its height) across the texture's width (BADGE_BAND_W) on the winged wheel; a small one over
    the roundel (BADGE_ROUNDEL), its narrower side spanning the roundel and a little more. Any
    frame with z up (worn or parked)."""
    v = np.asarray(verts, dtype=np.float64)
    f = np.asarray(tris, dtype=np.int64)
    uv = np.zeros((len(f), 3, 2))
    tl = islands(len(v), f)
    for isl in range(tl.max() + 1):
        sel = tl == isl
        t = v[f[sel]]
        fn = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]).sum(0)
        right, up, n = plane_frame(fn)
        mid = t.reshape(-1, 3).mean(0)
        a = (t - mid) @ right
        b = (t - mid) @ up
        # turned so the island's long axis runs across (within 45 degrees of world level): the tank
        # panels follow the tank's line, sloping about 15 degrees, and the emblem follows them
        pa, pb = a.reshape(-1), b.reshape(-1)
        cov = np.cov(np.vstack([pa - pa.mean(), pb - pb.mean()]))
        w_, vec = np.linalg.eigh(cov)
        ax = vec[:, 1]
        tilt = math.atan2(ax[1], ax[0])
        tilt = (tilt + math.pi / 2) % math.pi - math.pi / 2
        if abs(tilt) > math.pi / 4:
            tilt = 0.0
        ct, st = math.cos(tilt), math.sin(tilt)
        a, b = a * ct + b * st, -a * st + b * ct
        a0, a1, b0, b1 = a.min(), a.max(), b.min(), b.max()
        W, H = a1 - a0, b1 - b0
        if W > BADGE_LONG * H:
            k = BADGE_BAND_W / W
            cu, cv = 0.5, 0.5
        else:
            cu, cv, r = BADGE_ROUNDEL
            k = 2 * r * 1.12 / min(W, H)
        uv[sel, :, 0] = cu + (a - (a0 + a1) / 2) * k
        uv[sel, :, 1] = cv - (b - (b0 + b1) / 2) * k
    return uv.astype(np.float32)


# --- the rear fender's badge patch (the customisation build, 2026-11-07a) -----------------------------------------------
# static_badgeFender: a conforming patch on the rear fender's top, between the seat's end (parked y 67.0) and the rear
# roundel (y 85.5), FENDER_PATCH_SIZE (across x along: the long axis across the bike, so it reads from behind) centred
# on the centre line at parked y FENDER_PATCH_Y. A FENDER_PATCH_GRID grid of quads cast straight down onto the fender's
# triangles (static_paint's glTF mesh 14), its columns at equal steps along the surface across (so the art isn't
# stretched where the fender curves down to its sides) and its rows at equal steps in y, every vertex lifted
# FENDER_PATCH_LIFT along the surface's normal: the worn nifs' half floats (1/32 to 1/16 of a unit up here) keep it
# clear of the paint (DESIGN's overlay rule: 0.25 and up). Its UVs are the tank plates' rectangle (BADGE_PLATE_RECT,
# badge_uvs' long-island band) seen from behind with z up: u to the viewer's right (the bike's right, parked -x), v down
# toward the rear: so one badge material serves both tank plates and this patch (look_options.json's atlas cells).
FENDER_PATCH_SIZE = (14.0, 5.8)
FENDER_PATCH_Y = 76.0
FENDER_PATCH_GRID = (24, 10)     # quads across, along: 2 x 240 triangles
FENDER_PATCH_LIFT = 0.32       # 0.3 left one vertex 0.247 off the paint in the worn nifs' half floats
FENDER_PATCH_SAMPLES = 801       # the arc length's samples across, over the fender's x range
BADGE_PLATE_RECT = (0.020, 0.299, 0.980, 0.701)   # u0, v0, u1, v1: a tank plate's (BADGE_BAND_W across, 2.4:1)


def _cast_down(tris, cnrm, x, y):
    """Straight-down rays at (x, y) onto triangles (T, 3, 3) with corner normals (T, 3, 3): the topmost hit per ray,
    (points (k, 3), normals (k, 3) facing up, hit (k,) bool)."""
    k = len(x)
    pts, nrm, hit = np.zeros((k, 3)), np.zeros((k, 3)), np.zeros(k, bool)
    best = np.full(k, -np.inf)
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    den = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
    ok = np.abs(den) > 1e-12
    a, b, c, den, tn = a[ok], b[ok], c[ok], den[ok], cnrm[ok]
    for s in range(0, k, 64):
        px, py = x[s:s + 64, None], y[s:s + 64, None]
        w0 = ((b[:, 1] - c[:, 1]) * (px - c[:, 0]) + (c[:, 0] - b[:, 0]) * (py - c[:, 1])) / den
        w1 = ((c[:, 1] - a[:, 1]) * (px - c[:, 0]) + (a[:, 0] - c[:, 0]) * (py - c[:, 1])) / den
        w2 = 1.0 - w0 - w1
        inside = (w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9)
        z = np.where(inside, w0 * a[:, 2] + w1 * b[:, 2] + w2 * c[:, 2], -np.inf)
        j = np.argmax(z, axis=1)
        r = np.arange(len(j))
        zz = z[r, j]
        got = np.isfinite(zz)
        idx = np.arange(s, s + len(j))[got]
        jj, rr = j[got], r[got]
        W = np.column_stack([w0[rr, jj], w1[rr, jj], w2[rr, jj]])
        pts[idx] = np.column_stack([x[idx], y[idx], zz[got]])
        n = unit(np.einsum("ij,ijk->ik", W, tn[jj]))
        n[n[:, 2] < 0] *= -1.0
        nrm[idx], hit[idx], best[idx] = n, True, zz[got]
    return pts, nrm, hit


def fender_badge_patch(fender, flip=False, size=FENDER_PATCH_SIZE, centre_y=FENDER_PATCH_Y, grid=FENDER_PATCH_GRID,
                       lift=FENDER_PATCH_LIFT, rect=BADGE_PLATE_RECT):
    """The rear fender's badge patch (see FENDER_PATCH_*): fender = [(verts (n, 3), tris (m, 3), normals (n, 3) or
    None)], the fender's pieces in the parked frame. Returns (verts (V, 3), tris (T, 3), normals (V, 3), uvs (T, 3, 2)
    per corner, nif convention) in the parked frame, wound outward (up; pre-flipped with flip, as piece())."""
    tris = np.concatenate([np.asarray(v, np.float64)[np.asarray(f, np.int64)] for v, f, _ in fender])
    cn = np.concatenate([unit(np.asarray(n, np.float64) if n is not None else smooth_normals(np.asarray(v, np.float64),
                                                                                            np.asarray(f, np.int64)))[np.asarray(f, np.int64)]
                         for v, f, n in fender])
    nu, nv = grid
    w, h = size
    ys = np.linspace(centre_y - h / 2, centre_y + h / 2, nv + 1)
    near = (tris[:, :, 1].max(axis=1) >= ys[0] - 1.0) & (tris[:, :, 1].min(axis=1) <= ys[-1] + 1.0)
    tris, cn = tris[near], cn[near]
    if not len(tris):
        raise ValueError(f"fender_badge_patch: no fender triangles at y {ys[0]:.1f}..{ys[-1]:.1f}")
    x_lo, x_hi = float(tris[:, :, 0].min()), float(tris[:, :, 0].max())
    xs = np.linspace(x_lo, x_hi, FENDER_PATCH_SAMPLES)
    rows_p, rows_n = [], []
    for y in ys:
        p, n, hit = _cast_down(tris, cn, xs, np.full(len(xs), y))
        if not hit[np.argmin(np.abs(xs))]:
            raise ValueError(f"fender_badge_patch: the centre line misses the fender at y {y:.2f}")
        # the hit run through x = 0, its arc length from there
        c = int(np.argmin(np.abs(xs)))
        lo, hi = c, c
        while lo > 0 and hit[lo - 1]:
            lo -= 1
        while hi < len(xs) - 1 and hit[hi + 1]:
            hi += 1
        run = p[lo:hi + 1]
        s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(run, axis=0), axis=1))])
        s -= np.interp(0.0, xs[lo:hi + 1], s)
        want = np.linspace(-w / 2, w / 2, nu + 1)
        if want[0] < s[0] or want[-1] > s[-1]:
            raise ValueError(f"fender_badge_patch: the fender is {s[-1] - s[0]:.2f} across at y {y:.2f}, under the "
                             f"patch's {w}")
        px = np.interp(want, s, xs[lo:hi + 1])
        p, n, hit = _cast_down(tris, cn, px, np.full(len(px), y))
        if not hit.all():
            raise ValueError(f"fender_badge_patch: a vertex misses the fender at y {y:.2f}")
        rows_p.append(p + lift * n)
        rows_n.append(n)
    v = np.vstack(rows_p)
    n = np.vstack(rows_n)
    idx = np.arange((nu + 1) * (nv + 1)).reshape(nv + 1, nu + 1)
    a, b, c, d = idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()
    f = np.vstack([np.column_stack([a, b, c]), np.column_stack([a, c, d])]).astype(np.int64)
    gi, gj = np.meshgrid(np.arange(nu + 1), np.arange(nv + 1))
    u0, v0, u1, v1 = rect
    uv = np.column_stack([u1 - (u1 - u0) * gi.ravel() / nu, v0 + (v1 - v0) * gj.ravel() / nv])
    fn = face_normals(v, f)
    if (fn[:, 2] <= 0).any():
        raise ValueError("fender_badge_patch: a triangle faces down (the fender too steep for the grid)")
    uvc = uv[f].astype(np.float32)
    if flip:
        f, uvc = f[:, [0, 2, 1]], uvc[:, [0, 2, 1]]
    return v, f, n, uvc


# --- the licence plate (since the 2026-11-08a build, C2: plates.md 2) --------------------------------------
# static_plate is the model's plate (glTF mesh 24, split from static_black) with UVs of its own: the rear face (its
# triangles facing the rear, parked +y, by PLATE_FACE_DOT, on the slab's rear half) fills 0..1 both ways read true from
# behind (u to the viewer's right, the bike's right, parked -x; v down), in the face's fitted plane, its bounding box (the
# rounded corners leave the box's corners unused); the front face and the edges lie on PLATE_STRIP_V, the design cell's
# plain strip (plates_d.dds row 245 of the 256-row cell, the face drawn in 226 rows from row 8: a design material's UV
# transform takes 0..1 to the drawn face), squashed to +-PLATE_STRIP_DV so no triangle's UVs are degenerate.
# static_plateText is ours: an 8 x 2 grid over the face's text band (PLATE_TEXT_BAND_U/V of the face: 20.0 x 4.52 on
# this model) in the fitted plane, lifted PLATE_TEXT_LIFT along its normal (DESIGN's overlay rule, 0.25 and up in the worn
# nif's half floats), its UVs 0..1 over the band (the text cell's drawn area through the text material's transform).
PLATE_FACE_DOT = 0.9
PLATE_STRIP_V = (245.0 - 8.0) / 226.0
PLATE_STRIP_DV = 0.012
PLATE_TEXT_LIFT = 0.30
PLATE_TEXT_BAND_U = (0.0375, 0.9625)
PLATE_TEXT_BAND_V = (0.271, 0.729)
PLATE_TEXT_GRID = (8, 2)


def plate_face(verts, tris, whole=False):
    """The plate's rear face: (mask over tris, frame (centre, e_u, e_v, normal), extent (u0, u1, v0, v1)) in the parked
    frame; e_u the viewer's right from behind (parked -x laid into the face's plane), e_v down (-z laid in), the
    normal toward the rear; the plane fitted to the face's vertices (least squares). whole: tris are the face alone."""
    v = np.asarray(verts, dtype=np.float64)
    f = np.asarray(tris, dtype=np.int64)
    fn = unit(face_normals(v, f))
    cen = v[f].mean(axis=1)
    mid = 0.5 * (v[:, 1].min() + v[:, 1].max())
    face = np.ones(len(f), bool) if whole else (np.abs(fn[:, 1]) > PLATE_FACE_DOT) & (cen[:, 1] > mid)
    if not face.any():
        raise ValueError("plate_face: no triangle faces the rear")
    p = v[np.unique(f[face])]
    c = p.mean(axis=0)
    _, _, vt = np.linalg.svd(p - c)
    n = vt[2] if vt[2][1] > 0 else -vt[2]
    e_u = unit(np.array([-1.0, 0.0, 0.0]) - (np.array([-1.0, 0.0, 0.0]) @ n) * n)
    e_v = unit(np.cross(e_u, n))   # (the viewer's right) x (toward the viewer) = down
    q = p - c
    u, w = q @ e_u, q @ e_v
    return face, (c, e_u, e_v, n), (float(u.min()), float(u.max()), float(w.min()), float(w.max()))


def plate_uvs(verts, tris):
    """static_plate's UVs per corner (T, 3, 2): the rear face read true from behind over 0..1, the rest on the
    design cell's strip (see above)."""
    v = np.asarray(verts, dtype=np.float64)
    f = np.asarray(tris, dtype=np.int64)
    face, (c, e_u, e_v, n), (u0, u1, v0, v1) = plate_face(v, f)
    q = v - c
    U = np.clip((q @ e_u - u0) / (u1 - u0), 0.0, 1.0)
    V = np.clip((q @ e_v - v0) / (v1 - v0), 0.0, 1.0)
    depth = q @ n
    span = max(float(depth.max() - depth.min()), 1e-6)
    deep = (depth - depth.min()) / span
    strip = PLATE_STRIP_V + PLATE_STRIP_DV * ((V - 0.5) + 0.5 * (deep - 0.5))
    uv_face = np.column_stack([U, V])
    uv_rest = np.column_stack([0.98 * U + 0.02 * deep, strip])   # the depth too: no edge's UVs are a line
    return np.where(face[:, None, None], uv_face[f], uv_rest[f])


def plate_text_overlay(face_tris, flip=False, lift=PLATE_TEXT_LIFT, grid=PLATE_TEXT_GRID):
    """static_plateText: face_tris (T, 3, 3) the plate's rear face (parked frame). Returns (verts, tris, normals, uvs
    per corner (T, 3, 2)) in the parked frame, wound toward the rear (pre-flipped with flip, as piece())."""
    t = np.asarray(face_tris, dtype=np.float64)
    v, f = weld(t)
    face, (c, e_u, e_v, n), (u0, u1, v0, v1) = plate_face(v, f, whole=True)
    nu, nv = grid
    U = np.linspace(PLATE_TEXT_BAND_U[0], PLATE_TEXT_BAND_U[1], nu + 1)
    V = np.linspace(PLATE_TEXT_BAND_V[0], PLATE_TEXT_BAND_V[1], nv + 1)
    gu, gv = np.meshgrid(U, V)
    pos = (c + np.outer(u0 + gu.ravel() * (u1 - u0), e_u) + np.outer(v0 + gv.ravel() * (v1 - v0), e_v) + lift * n)
    uv = np.column_stack([(gu.ravel() - U[0]) / (U[-1] - U[0]), (gv.ravel() - V[0]) / (V[-1] - V[0])])
    idx = np.arange((nu + 1) * (nv + 1)).reshape(nv + 1, nu + 1)
    a, b, cc, d = idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()
    tris = np.vstack([np.column_stack([a, b, cc]), np.column_stack([a, cc, d])]).astype(np.int64)
    if (face_normals(pos, tris) @ n <= 0).any():
        tris = tris[:, [0, 2, 1]]
    normals = np.tile(n, (len(pos), 1))
    uvc = uv[tris].astype(np.float32)
    if flip:
        tris, uvc = tris[:, [0, 2, 1]], uvc[:, [0, 2, 1]]
    return pos, tris, normals, uvc


# --- the brake discs (since the 2026-11-01a build) ---------------------------------------------------------
# Test 47: the model's discs (glTF meshes 78 and 100) read as low-quality plates: a 36-48 segment outline, the face cut
# into long thin triangles from the rim to octagonal holes, dented in the source. Ours: a drilled disc with a 96-segment
# outline. The friction band, DISC_BAND to 1 of the outer radius, is 24 cells of 15 degrees, each with one drilled hole
# (radius DISC_HOLE_R) at DISC_HOLE_AT of the way across the band, alternating (a drilled disc's zigzag); the carrier, from
# the bore to the band, is 6 cells of 60 degrees, each with a round window. Every cell's face is quads between its
# outline and its hole's circle, the hole's points on the rays from its centre to the outline's (star-shaped, so nothing
# overlaps); both faces, the holes' walls, the rim and the bore. All sizes are fractions of the outer radius, so one art
# (bike_art.disc_art) serves both discs: the faces' UVs are planar, u = 0.5 + dy / (2 R_art), v = 0.5 - dz / (2 R_art),
# R_art = DISC_ART_R x the outer radius (dy, dz from the axle in the frame the disc is made in).
DISC_BAND = 0.70                 # the friction band's inner edge
DISC_CELLS, DISC_WINDOWS = 24, 6
DISC_HOLE_AT = (0.33, 0.67)      # the holes' radii across the band, alternating
DISC_HOLE_R = 0.0266             # the drilled holes' radius (0.36 on the front, 0.33 on the rear)
# The bore, a fraction of the outer radius: the carrier's windows are laid out for it, the art paints the bore's chamfer
# there and (since 2026-11-02a, disc_pieces' bore "shared") the geometry cuts it there too, so both discs' art and
# geometry agree. This build's discs: the bolt heads' least radius is 0.143 of the outer radius on the front, 0.150 on
# the rear; the smaller, rounded down, keeps every bolt on the carrier. DISC_HUB_REF_BOLTS is the 2026-11-01a build's
# (bore "bolts": the art's bore at 0.15, the geometry's at the bolt heads, which left a ring of the bore's wall colour
# round the front disc's hole, review look-2).
DISC_HUB_REF = 0.142
DISC_HUB_REF_BOLTS = 0.15
DISC_WINDOW_AT = 0.55            # the windows' centres, across the carrier (bore to band, of DISC_HUB_REF)
DISC_WINDOW_R = 0.24             # the windows' radius, of the carrier's width
DISC_ARC, DISC_ARC_HUB = 4, 8    # segments per band cell's arc (96 round), per carrier cell's bore arc (48 round)
DISC_SIDE, DISC_SIDE_HUB = 3, 6  # points along a band cell's and a carrier cell's radial sides
DISC_ART_R = 1.02                # the art's square spans this much of the outer radius each way
DISC_WALL_UV = 0.02              # units: a wall takes the UVs of a ring this far either side of its edge (the chamfer)


def disc_hub_ref(bore="shared"):
    """The bore's fraction of the outer radius the windows (and the art's bore) are laid out for: "shared" (2026-11-02a)
    or "bolts" (the 2026-11-01a build's)."""
    if bore not in ("shared", "bolts"):
        raise ValueError(f"disc bore {bore!r}: shared or bolts")
    return DISC_HUB_REF if bore == "shared" else DISC_HUB_REF_BOLTS


def disc_layout(r_out=1.0, hub_ref=DISC_HUB_REF):
    """The holes of a disc of outer radius r_out: [(kind, angle (rad), radius from the axle, hole radius)], kind
    "hole" (the band's drilled holes) or "window" (the carrier's), the carrier from the bore at hub_ref."""
    out = []
    band = DISC_BAND * r_out
    dt = 2 * math.pi / DISC_CELLS
    for k in range(DISC_CELLS):
        rr = band + DISC_HOLE_AT[k % 2] * (r_out - band)
        out.append(("hole", (k + 0.5) * dt, rr, DISC_HOLE_R * r_out))
    hub = hub_ref * r_out
    dc = 2 * math.pi / DISC_WINDOWS
    for k in range(DISC_WINDOWS):
        out.append(("window", (k + 0.5) * dc, hub + DISC_WINDOW_AT * (band - hub), DISC_WINDOW_R * (band - hub)))
    return out


def disc_pieces(centre_yz, x0, x1, r_out, r_hub, flip=False, bore="shared"):
    """Our brake disc about the x axis through (y, z) = centre_yz, its faces at x0 and x1, out to r_out:
    (verts (n, 3), tris (m, 3), normals (n, 3), uvs (n, 2)), in the frame the centre is given in. The bore: bore
    "shared" (since 2026-11-02a) at DISC_HUB_REF x r_out, where the art paints it, which must be inside r_hub (the bolt
    heads' least radius: they sit on the carrier) or ValueError; "bolts" (the 2026-11-01a build) at r_hub itself, the
    windows laid out for DISC_HUB_REF_BOLTS. The faces' normals are +-x, the walls' radial (inward on the holes and
    the bore), split at the 90-degree edges; every triangle winds with its normal (pre-flipped with flip, as piece()
    does). The UVs: planar on the faces (see above), a wall the DISC_WALL_UV ring either side of its edge on the face
    (the art paints it as the chamfer)."""
    cy, cz = float(centre_yz[0]), float(centre_yz[1])
    x0, x1 = (float(x0), float(x1)) if x0 < x1 else (float(x1), float(x0))
    hub_ref = disc_hub_ref(bore)
    R, hub = float(r_out), float(r_hub)
    if bore == "shared":
        hub = DISC_HUB_REF * R
        if hub > float(r_hub):
            raise ValueError("the bore %.3f is outside the bolt heads at %.3f" % (hub, float(r_hub)))
    band = DISC_BAND * R
    r_art = DISC_ART_R * R
    verts, norms, uvs, tris = [], [], [], []

    def uv_of(p):
        return (0.5 + p[0] / (2 * r_art), 0.5 - p[1] / (2 * r_art))

    def add(x, p, n, uv):
        verts.append((x, cy + p[0], cz + p[1]))
        norms.append(n)
        uvs.append(uv)
        return len(verts) - 1

    def tri(a, b, c, want):
        pa, pb, pc = (np.array(verts[i]) for i in (a, b, c))
        if np.dot(np.cross(pb - pa, pc - pa), want) < 0:
            b, c = c, b
        tris.append((a, b, c))

    def pol(r, t):
        return np.array([r * math.cos(t), r * math.sin(t)])

    def arc(r, t0, t1, segs):
        return [pol(r, t0 + (t1 - t0) * k / segs) for k in range(segs + 1)]

    def side(r0, r1, t, pts):
        return [pol(r0 + (r1 - r0) * k / (pts + 1), t) for k in range(1, pts + 1)]

    def cell(boundary, h, rho):
        """One cell: both faces between its outline and its hole, and the hole's wall."""
        boundary = np.asarray(boundary)
        n = len(boundary)
        dirs = np.array([(b - h) / np.linalg.norm(b - h) for b in boundary])
        ring = h + rho * dirs
        for x, nx in ((x1, 1.0), (x0, -1.0)):
            bi = [add(x, b, (nx, 0.0, 0.0), uv_of(b)) for b in boundary]
            hi = [add(x, q, (nx, 0.0, 0.0), uv_of(q)) for q in ring]
            for i in range(n):
                j = (i + 1) % n
                tri(bi[i], bi[j], hi[j], (nx, 0, 0))
                tri(bi[i], hi[j], hi[i], (nx, 0, 0))
        # the wall: normals toward the hole's centre; UVs just outside the hole (x1 side) and just inside it (x0)
        a = [add(x1, q, (0.0, -d[0], -d[1]), uv_of(h + (rho + DISC_WALL_UV) * d)) for q, d in zip(ring, dirs)]
        b = [add(x0, q, (0.0, -d[0], -d[1]), uv_of(h + (rho - DISC_WALL_UV) * d)) for q, d in zip(ring, dirs)]
        for i in range(n):
            j = (i + 1) % n
            want = (0.0, -(dirs[i][0] + dirs[j][0]), -(dirs[i][1] + dirs[j][1]))
            tri(a[i], b[i], b[j], want)
            tri(a[i], b[j], a[j], want)

    holes = disc_layout(R, hub_ref)
    dt = 2 * math.pi / DISC_CELLS
    for k in range(DISC_CELLS):
        t0, t1 = k * dt, (k + 1) * dt
        B = (arc(band, t0, t1, DISC_ARC) + side(band, R, t1, DISC_SIDE) + arc(R, t1, t0, DISC_ARC)
             + side(R, band, t0, DISC_SIDE))
        _, ang, rr, rho = holes[k]
        cell(B, pol(rr, ang), rho)
    dc = 2 * math.pi / DISC_WINDOWS
    per = DISC_CELLS // DISC_WINDOWS
    for k in range(DISC_WINDOWS):
        t0, t1 = k * dc, (k + 1) * dc
        B = (arc(hub, t0, t1, DISC_ARC_HUB) + side(hub, band, t1, DISC_SIDE_HUB) + arc(band, t1, t0, DISC_ARC * per)
             + side(band, hub, t0, DISC_SIDE_HUB))
        _, ang, rr, rho = holes[DISC_CELLS + k]
        cell(B, pol(rr, ang), rho)
    # the rim (outward) and the bore (inward)
    for r, segs, sign in ((R, DISC_CELLS * DISC_ARC, 1.0), (hub, DISC_WINDOWS * DISC_ARC_HUB, -1.0)):
        ang = [2 * math.pi * k / segs for k in range(segs)]
        d = [np.array([math.cos(t), math.sin(t)]) for t in ang]
        face_r = r - sign * DISC_WALL_UV   # the face side of the wall's UV ring
        a = [add(x1, r * e, (0.0, sign * e[0], sign * e[1]), uv_of(face_r * e)) for e in d]
        b = [add(x0, r * e, (0.0, sign * e[0], sign * e[1]), uv_of((2 * r - face_r) * e)) for e in d]
        for i in range(segs):
            j = (i + 1) % segs
            want = (0.0, sign * (d[i][0] + d[j][0]), sign * (d[i][1] + d[j][1]))
            tri(a[i], b[i], b[j], want)
            tri(a[i], b[j], a[j], want)
    v = np.array(verts, dtype=np.float64)
    f = np.array(tris, dtype=np.int64)
    n = unit(np.array(norms, dtype=np.float64))
    uv = np.array(uvs, dtype=np.float64)
    # one vertex per (place, normal, UV): the faces' shared cell edges merged
    key = np.concatenate([np.round(v * 1e5), np.round(n * 1e4), np.round(uv * 1e6)], axis=1).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    order = np.argsort(first)               # keep the vertices in the order they were made
    rank = np.empty_like(order)
    rank[order] = np.arange(len(order))
    f = rank[inv.reshape(-1)][f]
    first = first[order]
    v, n, uv = v[first], n[first], uv[first]
    if flip:
        f = f[:, [0, 2, 1]]
    return v, f, n, uv


def disc_check(v, f, n, flip=False):
    """For tests: (open edges, non-manifold edges, edges used twice the same way, triangles against their normals) of
    disc_pieces' output, with the vertices welded by place."""
    q = np.round(v * 1e5).astype(np.int64)
    _, inv = np.unique(q, axis=0, return_inverse=True)
    F = inv.reshape(-1)[f if not flip else f[:, [0, 2, 1]]]
    e = np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    und, cnt = np.unique(np.sort(e, axis=1), axis=0, return_counts=True)
    dirs, dcnt = np.unique(e, axis=0, return_counts=True)
    fn = unit(face_normals(v, f if not flip else f[:, [0, 2, 1]]))
    against = int((np.einsum("ij,ij->i", fn, n[f].mean(axis=1)) <= 0).sum())
    return int((cnt == 1).sum()), int((cnt > 2).sum()), int((dcnt > 1).sum()), against


# --- the rim styles (since the 2026-11-08a build, C2) ------------------------------------------------------
# Seven styles, each wheel its own shape wheelF_rim<Style> / wheelR_rim<Style> (harley_meshes.RIM_STYLE_LABELS; the
# plugin's rim group 1-7, CMB_LookCode bits 3-6): procedural, in the parked frame about the axle, x across from the
# axle's x (+ the bike's left: the brake discs' side), r from the axle. Every style keeps the stock hoop's profile
# (RIM_HOOP: the cast rim's cross-section, read off wheelF_rim and wheelR_rim at fdb5b3a: its tyre side, where the bead
# sits, point for point; its axle side a little thicker than the cast's sheet so the hoop is a closed solid) and stays
# within RIM_ENVELOPE between r 2 and the hoop (look_options.json's rim_envelope: clear of the discs, the front fork's
# rings and legs, the rear caliper and the belt pulley). A spoke, blade or plate ends RIM_ATTACH inside the hoop's well,
# so no joint shows. Each style's triangles carry one of three parts, by material: "body" (black_m: the finish's
# palette segment, U 56-127 of rim_p.dds), "trim" (chrome: U 216-255, the silver trims: nipples, caps, the nucleus) and
# "steel" (silver: U 0-47, Scrap's rivets and weld beads, which the art rusts). The UVs are the style's cell of the rim
# atlas (look_options.json's rim_atlas: 2048 square, 4 x 4 cells of 512, cell 2 x style + wheel, an 8-px margin), each
# part in a region of its own (RIM_REGIONS, fractions of the cell inside its margin): the faces planar (u = 0.5 +
# dy / 2R, v = 0.5 - dz / 2R across the face region, R the hoop's outer radius; both sides of a plate share their
# texels), the hoop and the hubs cylindrical (u round, v along the profile), the bars (spokes, blades, rings) along
# their length; no two parts share a texel. art-wheels' look_wheels.py paints by part per texel.
RIM_STYLES = ("Laced", "Disc", "Star", "Turbine", "Prewar", "Atomic", "Scrap")
RIM_KEYS = ("laced", "disc", "star", "turbine", "prewar", "atomic", "scrap")   # look_options.json's rim_styles keys
RIM_WHEELS = ("F", "R")
# The design's triangle estimates per wheel (custom.md 5) did not count the hoop: the stock hoop's profile alone is
# RIM_HOOP_SEGMENTS x 2 x its points; RIM_TRIS_MAX is the estimate plus RIM_HOOP_ALLOWANCE (checked by the self-test)
RIM_TRIS_DESIGN = {"Laced": 8000, "Disc": 2000, "Star": 3000, "Turbine": 5000, "Prewar": 3000, "Atomic": 5000, "Scrap": 3000}
RIM_HOOP_ALLOWANCE = 1800
RIM_HOOP_SEGMENTS = 48
# The hoop's cross-section (x, r), a closed polygon: the tyre side from the -x flange's lip to the +x one's (the cast's
# points within 0.05), then the axle side back. The front: lips at x +-4.62 r 23.42-23.80, bead seats to (3.20, 21.88),
# (2.02, 21.72), the well's floor r 21.12 within x +-1.92, its underside r 19.5. The rear: lips at x +-4.10 r 21.62, the
# flange's wall at x 3.85 down to r 19.62, seats to (2.70, 18.30), (1.72, 18.20), the well's floor r 17.70 within
# x +-1.62, its rib r 17.05 within x +-0.6.
RIM_HOOP = {
    "F": ((-4.62, 23.80), (-4.42, 23.42), (-3.20, 21.88), (-2.02, 21.72), (-1.92, 21.12), (1.92, 21.12), (2.02, 21.72),
          (3.20, 21.88), (4.42, 23.42), (4.62, 23.80), (4.62, 23.15), (3.25, 21.55), (2.00, 19.50), (-2.00, 19.50),
          (-3.25, 21.55), (-4.62, 23.15)),
    "R": ((-4.10, 21.62), (-3.85, 19.62), (-2.70, 18.30), (-1.72, 18.20), (-1.62, 17.70), (1.62, 17.70), (1.72, 18.20),
          (2.70, 18.30), (3.85, 19.62), (4.10, 21.62), (4.05, 19.45), (2.80, 18.00), (1.90, 17.40), (0.60, 17.05),
          (-0.60, 17.05), (-1.90, 17.40), (-2.80, 18.00), (-4.05, 19.45)),
}
RIM_HOOP_TYRE_SIDE = {"F": 10, "R": 10}   # the profile's first points: the tyre side (the stock's outer profile)
RIM_HOOP_MIN = {"F": 20.5, "R": 18.4}     # the envelope's top: above it the hoop alone
# (r0, r1, x0, x1): between r0 and r1 a style stays within x0..x1 (look_options.json's rim_envelope)
RIM_ENVELOPE = {"F": ((2.0, 6.0, -5.5, 4.9), (6.0, 20.5, -5.3, 3.9)), "R": ((2.0, 18.4, -5.5, 4.9),)}
RIM_ATTACH = {"F": (20.2, 1.5), "R": (17.5, 0.5)}   # (r, |x| at most): a bar's end inside the hoop's well (F: the
#                                                     box x +-1.92 r 19.5-21.12; R: the rib x +-0.6 r 17.05-17.70)
RIM_ATLAS = 2048
RIM_CELL = 512
RIM_MARGIN = 8
RIM_REGIONS = {"face": (0.0, 0.0, 0.72, 0.72), "hub": (0.76, 0.0, 1.0, 0.44), "trim": (0.76, 0.48, 1.0, 0.60),
               "steel": (0.76, 0.64, 1.0, 0.72), "hoop": (0.0, 0.76, 1.0, 0.86), "bars": (0.0, 0.90, 1.0, 1.0)}
RIM_PART_MATERIAL = {"body": "black_m", "trim": "chrome", "steel": "silver"}
RIM_PART_REGIONS = {"body": ("face", "hub", "hoop", "bars"), "trim": ("trim",), "steel": ("steel",)}
RIM_SPLIT_DEG = 35.0       # the normals part at sharper edges than this (lathes, plates)
RIM_BAR_SPLIT_DEG = 80.0   # and the bars' (round: 5-8 sides smooth; a blade's or a cap's square edges stay hard)


def rim_cell(style, wheel):
    """The (style, wheel)'s cell of the rim atlas, (x, y, w, h) in texels: cell 2 x style index + (0 F, 1 R), four
    to a row (look_options.json's rim_atlas cells)."""
    i = 2 * RIM_STYLES.index(style) + RIM_WHEELS.index(wheel)
    return (i % 4) * RIM_CELL, (i // 4) * RIM_CELL, RIM_CELL, RIM_CELL


def rim_to_atlas(uvl, region, style, wheel):
    """Region-local UVs (0..1 each way) -> the atlas's."""
    x, y, w, h = rim_cell(style, wheel)
    u0, v0, u1, v1 = RIM_REGIONS[region]
    inner = RIM_CELL - 2 * RIM_MARGIN
    uvl = np.asarray(uvl, dtype=np.float64)
    u = (x + RIM_MARGIN + (u0 + uvl[..., 0] * (u1 - u0)) * inner) / RIM_ATLAS
    v = (y + RIM_MARGIN + (v0 + uvl[..., 1] * (v1 - v0)) * inner) / RIM_ATLAS
    return np.stack([u, v], axis=-1)


def _signed_volume(v, f):
    t = v[f]
    return float(np.einsum("ij,ij->i", t[:, 0], np.cross(t[:, 1], t[:, 2])).sum() / 6.0)


def _lathe_rings(profile, segs, closed, theta0=0.0):
    """A surface of revolution about the x axis: profile [(x, r)] (r 0 = a pole), segs + 1 columns (the last the first
    again, for the UVs' seam). Returns (verts, tris, uvs per corner (u round 0..1, v along the profile 0..1)); poles'
    degenerate triangles dropped; winding as it falls (the caller orients)."""
    P = np.asarray(profile, dtype=np.float64)
    m = len(P)
    th = theta0 + 2.0 * math.pi * np.arange(segs + 1) / segs
    v = np.stack([np.repeat(P[:, :1], segs + 1, axis=1), P[:, 1:2] * np.cos(th), P[:, 1:2] * np.sin(th)], axis=-1).reshape(-1, 3)
    edges = [(i, i + 1) for i in range(m - 1)] + ([(m - 1, 0)] if closed else [])
    seg_len = [math.hypot(*(P[b] - P[a])) for a, b in edges]
    total = max(sum(seg_len), 1e-9)
    s = np.concatenate([[0.0], np.cumsum(seg_len)]) / total
    tris, uvs = [], []
    S = segs + 1
    for e, (a, b) in enumerate(edges):
        sa, sb = s[e], s[e + 1]
        for j in range(segs):
            A, B, C, D = a * S + j, a * S + j + 1, b * S + j + 1, b * S + j
            ua, ub = j / segs, (j + 1) / segs
            tris += [(A, B, C), (A, C, D)]
            uvs += [((ua, sa), (ub, sa), (ub, sb)), ((ua, sa), (ub, sb), (ua, sb))]
    f = np.array(tris, dtype=np.int64)
    uv = np.array(uvs, dtype=np.float64)
    keep = tri_areas(v, f) > 1e-9
    return v, f[keep], uv[keep]


def _bar(stations, sides, closed=False, caps=True, phase=0.0):
    """A tube through stations [(centre, e1, e2, a, b)]: each ring centre + a cos(t) e1 + b sin(t) e2 (sides points);
    closed: the last station joins the first (a ring); caps close the ends. Returns (verts, tris, uvs per corner: u along
    the length 0..1, v round 0..1), the caps' UVs on the end rings' line. Winding as it falls (the caller orients)."""
    k = len(stations)
    t = phase + 2.0 * math.pi * np.arange(sides + 1) / sides
    rings = []
    for c, e1, e2, a, b in stations:
        rings.append(np.asarray(c) + np.outer(a * np.cos(t), e1) + np.outer(b * np.sin(t), e2))
    v = np.vstack(rings)
    S = sides + 1
    cs = [np.asarray(s[0], dtype=np.float64) for s in stations]
    seg = [float(np.linalg.norm(cs[i + 1] - cs[i])) for i in range(k - 1)] + ([float(np.linalg.norm(cs[0] - cs[-1]))] if closed else [])
    total = max(sum(seg), 1e-9)
    s = np.concatenate([[0.0], np.cumsum(seg)]) / total
    pairs = [(i, i + 1) for i in range(k - 1)] + ([(k - 1, 0)] if closed else [])
    tris, uvs = [], []
    for e, (i, i2) in enumerate(pairs):
        for j in range(sides):
            A, B, C, D = i * S + j, i * S + j + 1, i2 * S + j + 1, i2 * S + j
            va, vb = j / sides, (j + 1) / sides
            tris += [(A, B, C), (A, C, D)]
            uvs += [((s[e], va), (s[e], vb), (s[e + 1], vb)), ((s[e], va), (s[e + 1], vb), (s[e + 1], va))]
    if caps and not closed:
        for i, u in ((0, 0.0), (k - 1, 1.0)):
            ci = len(v)
            v = np.vstack([v, cs[i][None]])
            for j in range(sides):
                tris.append((ci, i * S + j, i * S + j + 1))
                uvs.append(((u, 0.5), (u, j / sides), (u, (j + 1) / sides)))
    f = np.array(tris, dtype=np.int64)
    uv = np.array(uvs, dtype=np.float64)
    keep = tri_areas(v, f) > 1e-9
    return v, f[keep], uv[keep]


def _orient_closed(v, f):
    """A closed body's triangles, all flipped if they wind inward (by the signed volume)."""
    return f if _signed_volume(v, f) >= 0 else f[:, [0, 2, 1]]


def _orient_toward(v, f, direction):
    """Each triangle flipped where its normal points against direction(centres) (an open sheet's outside)."""
    fn = face_normals(v, f)
    d = direction(v[f].mean(axis=1))
    bad = np.einsum("ij,ij->i", fn, d) < 0
    f = f.copy()
    f[bad] = f[bad][:, [0, 2, 1]]
    return f


def _flip_uv(f, uv, flipped):
    """The corners' UVs follow a per-triangle flip (columns 1 and 2 swapped where flipped)."""
    uv = uv.copy()
    uv[flipped] = uv[flipped][:, [0, 2, 1]]
    return uv


def _orient(v, f, uv, how):
    """Orient (closed: by the signed volume; else a direction function) keeping each corner's UV."""
    g = _orient_closed(v, f) if how == "closed" else _orient_toward(v, f, how)
    flipped = (g != f).any(axis=1)
    return g, _flip_uv(f, uv, flipped)


def _radial(c):
    """Away from the axle in the wheel's plane (for sheets facing out round it)."""
    d = np.column_stack([np.zeros(len(c)), c[:, 1], c[:, 2]])
    return unit(d)


def _axial_out(c):
    """Away from the wheel's middle plane, along x."""
    return np.column_stack([np.sign(c[:, 0]) + (c[:, 0] == 0), np.zeros(len(c)), np.zeros(len(c))])


def _frame_at(theta):
    """(radial, tangential) unit vectors in the wheel's plane at angle theta (from +y toward +z)."""
    return np.array([0.0, math.cos(theta), math.sin(theta)]), np.array([0.0, -math.sin(theta), math.cos(theta)])


def _planar(v, R):
    """The face region's UVs: the wheel's plane, R the hoop's outer radius at the region's edge."""
    return np.stack([0.5 + v[..., 1] / (2 * R), 0.5 - v[..., 2] / (2 * R)], axis=-1)


class _Rim:
    """One style's parts as they're made: (part, verts, tris, region-local uvs per corner, region). phase: the style's
    surfaces of revolution start this fraction of a segment round (each style its own, RIM_STYLES' index / 7), so no two
    styles' hoops or hubs lie on the same triangles: the parked bike carries every style, the ones not chosen invisible
    (a renderer's ray, or a depth test, then always meets the shown style's surface, never a twin)."""

    def __init__(self, wheel, phase=0.0):
        self.wheel = wheel
        self.phase = phase
        self.parts = []
        self.R = max(r for _, r in RIM_HOOP[wheel])

    def add(self, part, v, f, uv, region, orient, split=RIM_SPLIT_DEG):
        f, uv = _orient(v, f, uv, orient)
        self.parts.append((part, v, f, uv, region, split))

    def lathe(self, part, profile, region, segs, closed=True, orient="closed", theta0=0.0, uv="round"):
        v, f, uv_ = _lathe_rings(profile, segs, closed, theta0 + self.phase * 2.0 * math.pi / segs)
        if uv == "planar":
            uv_ = _planar(v[f], self.R)
        self.add(part, v, f, uv_, region, orient)

    def bar(self, part, stations, sides, region, closed=False, caps=True, phase=0.0):
        v, f, uv = _bar(stations, sides, closed, caps, phase)
        self.add(part, v, f, uv, region, "closed", RIM_BAR_SPLIT_DEG)


def _hoop(rim, segs=RIM_HOOP_SEGMENTS):
    rim.lathe("body", RIM_HOOP[rim.wheel], "hoop", segs)


def _straight_stations(p0, p1, widths, thick, positions, twist=None, curve=None):
    """Stations along a radial bar from p0 to p1 (local points): at each fraction in positions, the half width
    (tangential) and half thickness (along x) given; twist(fraction) turns the section about the bar (radians)."""
    p0, p1 = np.asarray(p0, np.float64), np.asarray(p1, np.float64)
    ax = unit(p1 - p0)
    out = []
    for s, a, b in zip(positions, widths, thick):
        c = p0 + s * (p1 - p0)
        if curve is not None:
            c = curve(s, c)
        th = math.atan2(c[2], c[1])
        _, tang = _frame_at(th)
        e_x = np.array([1.0, 0.0, 0.0])
        e1 = unit(tang - (tang @ ax) * ax)
        e2 = unit(e_x - (e_x @ ax) * ax - (e_x @ e1) * e1)
        if twist is not None:
            q = twist(s)
            e1, e2 = math.cos(q) * e1 + math.sin(q) * e2, -math.sin(q) * e1 + math.cos(q) * e2
        out.append((c, e1, e2, a, b))
    return out


def _polar(r, th, x=0.0):
    return np.array([x, r * math.cos(th), r * math.sin(th)])


def _hub_barrel(rim, x0, x1, r_end, r_mid, segs=32, part="body"):
    """An open barrel (its ends r_end at x0 and x1, r_mid between) and two trim caps closing it."""
    prof = [(x0, r_end), (x0 + 0.25 * (x1 - x0), r_mid), (x1 - 0.25 * (x1 - x0), r_mid), (x1, r_end)]
    rim.lathe(part, prof, "hub", segs, closed=False, orient=_radial)
    for x, sgn in ((x0, -1.0), (x1, 1.0)):
        cap = [(x + sgn * 0.15, 0.0), (x + sgn * 0.12, 0.55 * r_end), (x - sgn * 0.05, r_end + 0.12)]
        rim.lathe("trim", cap, "trim", segs, closed=False, orient=_axial_out, uv="planar")


def _laced(rim):
    w = rim.wheel
    r_att, x_att = RIM_ATTACH[w]
    x_fl = 3.5
    # the hub: a barrel between two flanges (r 4.5, 0.6 thick, at x +-3.5), its ends trim caps
    prof = [(-5.0, 1.9), (-4.4, 2.3), (-3.8, 2.4), (-3.8, 4.5), (-3.2, 4.5), (-3.2, 2.6), (3.2, 2.6), (3.2, 4.5),
            (3.8, 4.5), (3.8, 2.4), (4.3, 2.3), (4.7, 1.9)]
    rim.lathe("body", prof, "hub", 32, closed=False, orient=_radial)
    for x, sgn in ((-5.0, -1.0), (4.7, 1.0)):
        rim.lathe("trim", [(x + sgn * 0.12, 0.0), (x + sgn * 0.08, 1.2), (x - sgn * 0.05, 2.0)], "trim", 24,
                  closed=False, orient=_axial_out, uv="planar")
    # 40 spokes cross-3: 20 a flange, its holes 18 degrees apart (the other flange's 9 degrees on), leading and
    # trailing alternate; the rim end 54 degrees (720 x 3 / 40) on; the rim's holes 9 degrees apart, either side of the
    # well's middle by x_att / 3
    r_hole, sp_r, alpha = 4.0, 0.225, math.radians(54.0)
    for side, x_hub in ((-1.0, -x_fl), (1.0, x_fl)):
        for k in range(20):
            th = math.radians(18.0 * k + (9.0 if side > 0 else 0.0))
            th_rim = th + (alpha if k % 2 == 0 else -alpha)
            p0 = _polar(r_hole, th, x_hub)
            p1 = _polar(r_att, th_rim, side * x_att / 3.0)
            ax = unit(p1 - p0)
            e1 = unit(np.cross(ax, [1.0, 0.0, 0.0]))
            e2 = np.cross(ax, e1)
            rim.bar("body", [(p0 - 0.2 * ax, e1, e2, sp_r, sp_r), (p1, e1, e2, sp_r, sp_r)], 5, "bars")
            # the nipple: a short collar where the spoke meets the hoop
            n0 = p1 - 1.1 * ax
            rim.bar("trim", [(n0, e1, e2, 0.33, 0.33), (p1 + 0.15 * ax, e1, e2, 0.33, 0.33)], 6, "trim")
    _hoop(rim)


def _disc(rim):
    """Two dished covers from the hoop's lips to the hub, sunk to x +-2.5 at r 6, and a domed cap each side."""
    w = rim.wheel
    if w == "F":
        neg = [(-4.30, 23.00), (-4.80, 20.4), (-4.15, 15.0), (-3.20, 9.5), (-2.55, 6.3), (-2.70, 5.8), (-4.40, 5.1),
               (-5.05, 3.4), (-5.30, 1.4), (-5.35, 0.0)]
        pos = [(4.30, 23.00), (3.85, 20.4), (3.40, 15.0), (2.85, 9.5), (2.50, 6.3), (2.65, 5.8), (4.10, 5.1), (4.60, 3.4),
               (4.85, 1.4), (4.90, 0.0)]
    else:
        neg = [(-3.95, 20.80), (-4.70, 18.2), (-4.10, 13.5), (-3.20, 9.0), (-2.55, 6.3), (-2.70, 5.8), (-4.40, 5.1),
               (-5.05, 3.4), (-5.30, 1.4), (-5.35, 0.0)]
        pos = [(3.95, 20.80), (4.60, 18.2), (4.10, 13.5), (3.20, 9.0), (2.55, 6.3), (2.70, 5.8), (4.30, 5.1), (4.65, 3.4),
               (4.85, 1.4), (4.90, 0.0)]
    for prof in (neg, pos):
        cover, cap = prof[:6], prof[5:]
        rim.lathe("body", cover, "face", 40, closed=False, orient=_axial_out, uv="planar")
        rim.lathe("trim", cap, "trim", 32, closed=False, orient=_axial_out, uv="planar")
    _hoop(rim)


def _spokes(rim, n, th0, widths, thick, positions, r0=5.4, sides=8, twist=None, curve_deg=0.0, region="bars"):
    r_att, _ = RIM_ATTACH[rim.wheel]
    for k in range(n):
        th = th0 + 2.0 * math.pi * k / n

        def curve(s, c, th=th):
            if not curve_deg:
                return c
            r = r0 + s * (r_att - r0)
            q = th + math.radians(curve_deg) * s ** 1.3
            return _polar(r, q, c[0])

        st = _straight_stations(_polar(r0, th), _polar(r_att, th), widths, thick, positions, twist=twist,
                                curve=curve if curve_deg else None)
        rim.bar("body", st, sides, region)


def _star(rim):
    """Five straight spokes, 3.5 wide, flaring to the hub and the hoop (the cast look's fillets), on a hub barrel."""
    w = rim.wheel
    _hub_barrel(rim, -4.9, 4.2 if w == "F" else 4.7, 4.2, 6.8)
    t_end = 0.85 if w == "F" else 0.5
    _spokes(rim, 5, math.pi / 2, (2.7, 2.15, 1.75, 1.75, 2.05, 2.45), (1.25, 1.05, 0.85, 0.85, 0.85, t_end),
            (0.0, 0.1, 0.25, 0.75, 0.92, 1.0))
    _hoop(rim)


def _turbine(rim):
    """Twelve blades curving 22 degrees from the hub to the hoop, pitched 50 degrees across the wheel's plane (a fan's
    faces show from the side) and twisted 10 degrees more along their length."""
    w = rim.wheel
    _hub_barrel(rim, -4.9, 4.2 if w == "F" else 4.7, 4.2, 6.8)
    pitch = math.radians(50.0)
    chord_end = 1.45 if w == "F" else 0.95   # the end's x extent (chord x cos(pitch + twist)) inside the well
    pos = (0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0)
    half_chord = tuple(2.2 - (2.2 - chord_end) * s for s in pos)
    _spokes(rim, 12, 0.0, (0.2,) * 8, half_chord, pos, sides=4,
            twist=lambda s: pitch + math.radians(10.0 * s), curve_deg=22.0)
    _hoop(rim)


def _sector_face(r_in, r_out, th0, th1, hole_c, hole_r, rings, x_of, n_out=4, n_rad=3, n_in=2):
    """One sector's face with a round hole (prewar's vents): the sector's outline (its outer arc, the radial edge at
    th1, the inner arc, the radial edge at th0, counter-clockwise: the corners and the radial edges' points shared with
    the next sector's), each outline point joined to the hole's circle where the ray from the hole's centre meets it
    (the sector is star-shaped from there), rings blending the two. Returns (verts, tris)."""
    cy, cz = hole_c
    o = []
    for t in np.linspace(th0, th1, n_out + 1)[:-1]:
        o.append((r_out * math.cos(t), r_out * math.sin(t)))
    for r in np.linspace(r_out, r_in, n_rad + 1)[:-1]:
        o.append((r * math.cos(th1), r * math.sin(th1)))
    for t in np.linspace(th1, th0, n_in + 1)[:-1]:
        o.append((r_in * math.cos(t), r_in * math.sin(t)))
    for r in np.linspace(r_in, r_out, n_rad + 1)[:-1]:
        o.append((r * math.cos(th0), r * math.sin(th0)))
    o = np.array(o)
    phi = np.unwrap(np.arctan2(o[:, 1] - cz, o[:, 0] - cy))
    h = np.column_stack([cy + hole_r * np.cos(phi), cz + hole_r * np.sin(phi)])
    rays = len(o)
    pts = []
    for i in range(rings + 1):
        b = i / rings
        q = (1 - b) * h + b * o
        r = np.hypot(q[:, 0], q[:, 1])
        pts.append(np.column_stack([x_of(r), q[:, 0], q[:, 1]]))
    v = np.vstack(pts)
    tris = []
    for i in range(rings):
        for j in range(rays):
            j2 = (j + 1) % rays
            a, b, c, d = i * rays + j, i * rays + j2, (i + 1) * rays + j2, (i + 1) * rays + j
            tris += [(a, b, c), (a, c, d)]
    return v, np.array(tris, dtype=np.int64)


def _prewar(rim):
    """A pressed steel disc, dished, with eight round vents, and a dog-dish cap (r 9) either side."""
    w = rim.wheel
    r_att, _ = RIM_ATTACH[w]
    r_in, thick = 7.0, 0.32
    dish = 1.1

    def x_mid(r):
        return -dish * (1.0 - np.clip((np.asarray(r) - r_in) / (r_att - r_in), 0.0, 1.0)) ** 1.5

    r_c = 0.5 * (r_in + r_att) + 0.3
    hole = 2.55 if w == "F" else 2.15
    for k in range(8):
        th0 = 2.0 * math.pi * k / 8
        th1 = th0 + 2.0 * math.pi / 8
        thc = 0.5 * (th0 + th1)
        c = (r_c * math.cos(thc), r_c * math.sin(thc))
        for sgn in (-1.0, 1.0):
            v, f = _sector_face(r_in, r_att, th0, th1, c, hole, 2, lambda r, s=sgn: x_mid(r) + s * thick / 2)
            rim.add("body", v, f, _planar(v[f], rim.R), "face", lambda q, s=sgn: np.tile([s, 0.0, 0.0], (len(q), 1)))
        # the vent's lip: a short tube between the faces round the hole
        st = []
        for j in range(25):
            phi = 2.0 * math.pi * j / 24
            p = np.array([c[0] + hole * math.cos(phi), c[1] + hole * math.sin(phi)])
            st.append(p)
        ring = np.array(st)
        xm = x_mid(np.hypot(ring[:, 0], ring[:, 1]))
        v = np.vstack([np.column_stack([xm - thick / 2, ring]), np.column_stack([xm + thick / 2, ring])])
        tris, uvs = [], []
        for j in range(24):
            a, b, c2, d = j, j + 1, 25 + j + 1, 25 + j
            tris += [(a, b, c2), (a, c2, d)]
            uvs += [((j / 24, 0.0), ((j + 1) / 24, 0.0), ((j + 1) / 24, 1.0)), ((j / 24, 0.0), ((j + 1) / 24, 1.0), (j / 24, 1.0))]
        cen = np.array([0.0, c[0], c[1]])
        rim.add("body", v, np.array(tris, np.int64), np.array(uvs) * np.array([1.0, 0.3]), "hub", lambda q, cen=cen: -np.column_stack([np.zeros(len(q)), q[:, 1] - cen[1], q[:, 2] - cen[2]]))
    # the dog-dish caps: a dome from r 9 to the axle, its edge rolled under
    xp = 3.75 if w == "F" else 4.3
    for prof in ([(-1.0, 8.7), (-1.6, 9.2), (-2.4, 8.6), (-3.7, 7.0), (-4.6, 4.8), (-5.1, 2.4), (-5.25, 0.0)],
                 [(0.5, 8.7), (1.0, 9.2), (1.9, 8.6), (xp - 0.15, 6.0), (4.5, 4.4), (4.8, 2.4), (4.9, 0.0)]):
        rim.lathe("trim", prof, "trim", 32, closed=False, orient=_axial_out, uv="planar")
    _hoop(rim)


def _ellipse_ring(rim, a, b, rot, tube, steps=64, sides=6):
    st = []
    for j in range(steps):
        t = 2.0 * math.pi * j / steps
        y, z = a * math.cos(t), b * math.sin(t)
        c = np.array([0.0, y * math.cos(rot) - z * math.sin(rot), y * math.sin(rot) + z * math.cos(rot)])
        dt = np.array([0.0, -a * math.sin(t), b * math.cos(t)])
        dt = np.array([0.0, dt[1] * math.cos(rot) - dt[2] * math.sin(rot), dt[1] * math.sin(rot) + dt[2] * math.cos(rot)])
        tang = unit(dt)
        e1 = np.array([1.0, 0.0, 0.0])
        e2 = np.cross(tang, e1)
        st.append((c, e1, e2, tube, tube))
    rim.bar("body", st, sides, "bars", closed=True)


def _atomic(rim):
    """Three spokes and two elliptical rings round the hub, its ends the nucleus (trim domes)."""
    w = rim.wheel
    r_att, _ = RIM_ATTACH[w]
    prof = [(-4.6, 2.6), (-3.6, 5.6), (-1.0, 6.4), (1.0, 6.4), (3.0, 5.6), (4.0, 2.6)]
    rim.lathe("body", prof, "hub", 32, closed=False, orient=_radial)
    for x, sgn in ((-4.6, -1.0), (4.0, 1.0)):
        rim.lathe("trim", [(x + sgn * 0.9, 0.0), (x + sgn * 0.75, 1.4), (x + sgn * 0.35, 2.3), (x - sgn * 0.1, 2.75)],
                  "trim", 24, closed=False, orient=_axial_out, uv="planar")
    t_end = 0.6 if w == "F" else 0.45
    _spokes(rim, 3, math.pi / 2, (1.6, 1.25, 1.1, 1.1, 1.3), (0.8, 0.7, 0.6, 0.6, t_end), (0.0, 0.12, 0.4, 0.88, 1.0),
            r0=5.6)
    a, b = (15.4, 7.9) if w == "F" else (13.4, 7.6)
    for rot in (math.radians(30.0), math.radians(150.0)):
        _ellipse_ring(rim, a, b, rot, 0.42)
    _hoop(rim)


def _rivet(rim, centre, normal, r=0.32, h=0.18):
    """A low dome (6 sides) standing on a plate at centre, facing normal."""
    n = unit(np.asarray(normal, np.float64))
    e1 = unit(np.cross(n, [0.0, 0.0, 1.0] if abs(n[2]) < 0.9 else [0.0, 1.0, 0.0]))
    e2 = np.cross(n, e1)
    c = np.asarray(centre, np.float64)
    rim.bar("steel", [(c - 0.05 * n, e1, e2, r, r), (c + 0.6 * h * n, e1, e2, 0.75 * r, 0.75 * r),
                      (c + h * n, e1, e2, 0.05, 0.05)], 6, "steel")


def _scrap(rim):
    """Three plates riveted over each other, each a third of the wheel and a bit (their x stepped), a hub barrel, weld
    beads round the hub."""
    w = rim.wheel
    r_att, _ = RIM_ATTACH[w]
    _hub_barrel(rim, -4.9, 4.2 if w == "F" else 4.7, 4.2, 6.6)
    thick = 0.28
    rings = (5.6, 8.5, 12.0, 15.5, r_att)
    for k in range(3):
        x0 = (k - 1) * 0.36
        th0 = math.radians(120.0 * k - 9.0 + 90.0)
        th1 = th0 + math.radians(138.0)
        steps = 23
        ths = np.linspace(th0, th1, steps + 1)
        grid = np.array([[(x0, r * math.cos(t), r * math.sin(t)) for t in ths] for r in rings])   # (rings, steps+1, 3)
        nr, ns = grid.shape[:2]
        for sgn in (-1.0, 1.0):
            v = (grid + np.array([sgn * thick / 2, 0.0, 0.0])).reshape(-1, 3)
            tris = []
            for i in range(nr - 1):
                for j in range(ns - 1):
                    a, b, c, d = i * ns + j, i * ns + j + 1, (i + 1) * ns + j + 1, (i + 1) * ns + j
                    tris += [(a, b, c), (a, c, d)]
            f = np.array(tris, np.int64)
            rim.add("body", v, f, _planar(v[f], rim.R), "face", lambda q, s=sgn: np.tile([s, 0.0, 0.0], (len(q), 1)))
        # the radial edges' walls (the overlaps show them)
        for j in (0, ns - 1):
            col = grid[:, j]
            v = np.vstack([col - [thick / 2, 0, 0], col + [thick / 2, 0, 0]])
            tris, uvs = [], []
            for i in range(nr - 1):
                a, b, c, d = i, i + 1, nr + i + 1, nr + i
                tris += [(a, b, c), (a, c, d)]
                uvs += [((i / (nr - 1), 0.0), ((i + 1) / (nr - 1), 0.0), ((i + 1) / (nr - 1), 1.0)),
                        ((i / (nr - 1), 0.0), ((i + 1) / (nr - 1), 1.0), (i / (nr - 1), 1.0))]
            th = ths[j]
            tang = np.array([0.0, -math.sin(th), math.cos(th)]) * (1.0 if j else -1.0)
            rim.add("body", v, np.array(tris, np.int64), np.array(uvs) * np.array([1.0, 0.25]), "hub",
                    lambda q, t=tang: np.tile(t, (len(q), 1)))
        # rivets along the plate's leading edge, both faces, inside the next plate's overlap
        for rr in (8.5, 12.5, r_att - 3.0):
            t = th1 - math.radians(4.5)
            for sgn in (-1.0, 1.0):
                _rivet(rim, _polar(rr, t, x0 + sgn * thick / 2), (sgn, 0.0, 0.0))
    # weld beads round the hub, either side: a lumpy ring
    for x in (-0.36 - thick / 2 - 0.05, 0.36 + thick / 2 + 0.05):
        st = []
        for j in range(36):
            t = 2.0 * math.pi * j / 36
            rr = 6.75 + 0.06 * math.sin(7.0 * t)
            c = _polar(rr, t, x)
            tang = np.array([0.0, -math.sin(t), math.cos(t)])
            e1 = np.array([1.0, 0.0, 0.0])
            e2 = np.cross(tang, e1)
            g = 0.3 + 0.07 * math.sin(11.0 * t) ** 2
            st.append((c, e1, e2, g, g))
        rim.bar("steel", st, 5, "steel", closed=True)
    _hoop(rim)


RIM_MAKERS = {"Laced": _laced, "Disc": _disc, "Star": _star, "Turbine": _turbine, "Prewar": _prewar,
              "Atomic": _atomic, "Scrap": _scrap}


def rim_style_pieces(style, wheel, axle, flip=False):
    """One rim style's wheel (style one of RIM_STYLES, wheel "F" or "R"), about the axle (parked x, y, z), in the
    parked frame: [(material, verts (n, 3), tris (m, 3), normals (n, 3), uvs (m, 3, 2) atlas, part)] one a part
    (RIM_PART_MATERIAL), wound outward (pre-flipped with flip, as piece()), the vertices split where the normals part
    by more than RIM_SPLIT_DEG."""
    rim = _Rim(wheel, RIM_STYLES.index(style) / len(RIM_STYLES))
    RIM_MAKERS[style](rim)
    out = []
    for part in ("body", "trim", "steel"):
        vs, fs, ns, uvs, off = [], [], [], [], 0
        for p, v, f, uv, region, split in rim.parts:
            if p != part:
                continue
            if region not in RIM_PART_REGIONS[part]:
                raise ValueError(f"rim {style} {wheel}: a {part} part in the {region} region")
            vw, fw = weld(v[f], tol=1e-5)   # the seams' twins one vertex for the normals (the UVs are per corner)
            v2, f2, n2 = corner_split(vw, fw, split)
            vs.append(v2)
            fs.append(f2 + off)
            ns.append(n2)
            uvs.append(rim_to_atlas(np.clip(uv, 0.0, 1.0), region, style, wheel))
            off += len(v2)
        if not vs:
            continue
        v, f, n, uv = np.vstack(vs) + np.asarray(axle, dtype=np.float64), np.vstack(fs), np.vstack(ns), np.vstack(uvs)
        if flip:
            f, uv = f[:, [0, 2, 1]], uv[:, [0, 2, 1]]
        out.append((RIM_PART_MATERIAL[part], v, f, n, uv.astype(np.float32), part))
    return out


def rim_check(pieces, style, wheel, axle, flip=False):
    """For tests and the build: [messages] for one style's wheel: inside the envelope below the hoop's top, the hoop
    part inside the stock profile's outline (x within its lips, r at most its lips' top), its triangles winding with
    their normals, every UV in its cell; and (tris, x range, r range)."""
    msgs = []
    ax = np.asarray(axle, dtype=np.float64)
    n_tris = 0
    lo_x, hi_x, hi_r = 1e9, -1e9, 0.0
    P = np.asarray(RIM_HOOP[wheel])
    cx, cy, cw, ch = rim_cell(style, wheel)
    for mat, v, f, n, uv, part in pieces:
        if flip:
            f = f[:, [0, 2, 1]]
        q = v - ax
        r = np.hypot(q[:, 1], q[:, 2])
        x = q[:, 0]
        n_tris += len(f)
        lo_x, hi_x, hi_r = min(lo_x, x.min()), max(hi_x, x.max()), max(hi_r, r.max())
        for r0, r1, x0, x1 in RIM_ENVELOPE[wheel]:
            s = (r >= r0) & (r < r1)
            if s.any() and (x[s].min() < x0 - 1e-6 or x[s].max() > x1 + 1e-6):
                msgs.append(f"{part}: x {x[s].min():.2f}..{x[s].max():.2f} between r {r0} and {r1}, outside {x0}..{x1}")
        s = r < RIM_ENVELOPE[wheel][0][0]
        if s.any() and (x[s].min() < RIM_ENVELOPE[wheel][0][2] - 1e-6 or x[s].max() > RIM_ENVELOPE[wheel][0][3] + 1e-6):
            msgs.append(f"{part}: x {x[s].min():.2f}..{x[s].max():.2f} inside r {RIM_ENVELOPE[wheel][0][0]}")
        if r.max() > P[:, 1].max() + 1e-6 or np.abs(x[r >= RIM_HOOP_MIN[wheel]]).max(initial=0.0) > np.abs(P[:, 0]).max() + 1e-6:
            msgs.append(f"{part}: beyond the stock hoop (r up to {r.max():.3f}, its {P[:, 1].max()})")
        fn = unit(face_normals(v, f))
        agree = np.einsum("ij,ij->i", fn, n[f].mean(axis=1))
        if (agree <= 0).any():
            msgs.append(f"{part}: {(agree <= 0).sum()} of {len(f)} triangles wind against their normals")
        if (tri_areas(v, f) <= 1e-9).any():
            msgs.append(f"{part}: degenerate triangles")
        px = np.asarray(uv, np.float64) * RIM_ATLAS
        if (px[..., 0].min() < cx + RIM_MARGIN - 1e-3 or px[..., 0].max() > cx + cw - RIM_MARGIN + 1e-3
                or px[..., 1].min() < cy + RIM_MARGIN - 1e-3 or px[..., 1].max() > cy + ch - RIM_MARGIN + 1e-3):
            msgs.append(f"{part}: UVs outside the cell's {cw - 2 * RIM_MARGIN}-texel square at ({cx}, {cy})")
    return msgs, n_tris, (lo_x, hi_x), hi_r


# --- self-test ------------------------------------------------------------------------------------------

def _synthetic_dial():
    """A disc like the model's mesh 9 (worn): 12 segments, radius 3.72, facing the rider."""
    c = np.array([0.377, 65.351, 98.837])
    n = unit([0.0, -0.8346, 0.5509])
    right, up, n = plane_frame(n)
    ang = np.linspace(0, 2 * math.pi, 12, endpoint=False)
    ring = [c + 3.719 * (math.sin(a) * right + math.cos(a) * up) for a in ang]
    return np.array([[c, ring[(k + 1) % 12], ring[k]] for k in range(12)])


def check_pieces(pieces, outward_from=None, min_area=1e-6):
    """For tests: every piece's triangles are non-degenerate, wind with the normals they carry, and
    (with outward_from, a parked-frame point) face away from it on the whole. Returns messages."""
    msgs = []
    for mat, label, v, f, n, uv in pieces:
        area = tri_areas(v, f)
        if (area <= min_area).any():
            msgs.append(f"{label}/{mat}: {(area <= min_area).sum()} degenerate triangles")
        if len(np.unique(f)) != len(v):
            msgs.append(f"{label}/{mat}: {len(v) - len(np.unique(f))} unused vertices")
        if n is not None:
            fn = unit(face_normals(v, f))
            agree = np.einsum("ij,ij->i", fn, n[f].mean(axis=1))
            if (agree <= 0).any():
                msgs.append(f"{label}/{mat}: {(agree <= 0).sum()} of {len(f)} triangles wind against their normals")
        if uv is not None and (uv.min() < 0 or uv.max() > 1):
            msgs.append(f"{label}/{mat}: UVs outside 0..1 ({uv.min():.3f}..{uv.max():.3f})")
    return msgs


def _selftest():
    seat_at = 27.69
    pieces, keys = speedo_pieces(_synthetic_dial(), seat_at, False)
    print("speedo:", {p[1] + "/" + p[0]: len(p[3]) for p in pieces}, keys)
    shells_in = []
    for cx in (0.3,):
        # a 7.3 x 2.4 box lens, 1 deep, facing -Y, plus one sliver triangle
        x0, x1, z0, z1, y0, y1 = cx - 3.65, cx + 3.65, 53.1, 55.5, -64.15, -63.15
        corners = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1], [x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]])
        quads = [(0, 1, 2, 3), (1, 5, 6, 2), (5, 4, 7, 6), (4, 0, 3, 7), (3, 2, 6, 7), (4, 5, 1, 0)]
        bf = np.array([t for q in quads for t in ((q[0], q[1], q[2]), (q[0], q[2], q[3]))])
        bf = orient_outward(corners, bf, corners.mean(axis=0))
        shells_in += list(corners[bf])
        shells_in.append(np.array([[0.2, -37.7, 53.5], [x1, y1, z1], [x0, y1, z1]]))
    lamp = lamp_shells(np.array(shells_in), None, seat_at, False)
    for mat, label, v, f, n, uv in lamp:
        front = (seat_at - v[:, 1]).min()
        print(f"   {label}: {len(f)} triangles, its front {(-64.15) - front:.3f} out from the lens's")
    print("lamps:", [(p[1], len(p[3])) for p in lamp])
    for style in ("egg", "d"):
        mp = mirror_under_pieces(style, (29.4, 38.39, 96.0), 2.3, None, seat_at, False)
        _, info = mirror_side(style, (29.4, 38.39, 96.0))
        print(f"mirror {style}: {sum(len(p[3]) for p in mp)} triangles both sides, "
              f"top z {info['top']:.2f}, stalk {info['stalk_len']:.2f} long {info['stalk_down_deg']:.0f} deg down")
        for m in check_pieces(mp):
            print("   ", m)
    for m in check_pieces(pieces + lamp):
        print("   ", m)
    for name, args in (("front", ((-68.11, 29.87), 5.61, 6.35, 13.54, 1.97)), ("rear", ((68.11, 29.94), 6.78, 7.53, 12.53, 1.89))):
        v, f, n, uv = disc_pieces(*args)
        op, nm, same, against = disc_check(v, f, n)
        r = np.hypot(v[:, 1] - args[0][0], v[:, 2] - args[0][1])
        print(f"disc {name}: {len(f)} triangles, {len(v)} vertices; welded: {op} open edges, {nm} non-manifold, {same} "
              f"edges twice the same way, {against} triangles against their normals; x {v[:, 0].min():.2f}..{v[:, 0].max():.2f}, "
              f"r {r.min():.3f}..{r.max():.3f}, UVs {uv.min():.3f}..{uv.max():.3f}")
        assert abs(r.min() - DISC_HUB_REF * args[3]) < 1e-6, "the shared bore isn't at DISC_HUB_REF of the outer radius"
        vb, fb, nb, uvb = disc_pieces(*args, bore="bolts")
        rb = np.hypot(vb[:, 1] - args[0][0], vb[:, 2] - args[0][1])
        assert abs(rb.min() - args[4]) < 1e-6, "the bolts bore isn't at r_hub"
        print(f"   bore: shared {r.min():.3f} ({DISC_HUB_REF} of the outer radius), bolts {rb.min():.3f} (r_hub)")
    try:
        disc_pieces((0.0, 0.0), 0.0, 0.35, 13.5, 1.5)
        raise AssertionError("a bore outside the bolt heads was accepted")
    except ValueError as e:
        print(f"disc: a bolt circle inside the shared bore refused ({e})")
    # 2026-11-08a: the plate (a synthetic slab like glTF mesh 24: 21.62 x 9.86, 0.68 thick, facing the rear, parked +y)
    # and the 14 rim styles about this model's axles (parked)
    x0, x1, y0, y1, z0, z1 = 12.12, 33.74, 76.81, 77.49, 41.16, 51.02
    corners = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1], [x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]])
    quads = [(0, 1, 2, 3), (1, 5, 6, 2), (5, 4, 7, 6), (4, 0, 3, 7), (3, 2, 6, 7), (4, 5, 1, 0)]
    pf = orient_outward(corners, np.array([t for q in quads for t in ((q[0], q[1], q[2]), (q[0], q[2], q[3]))]), corners.mean(axis=0))
    puv = plate_uvs(corners, pf)
    face, (c, e_u, e_v, n), _ = plate_face(corners, pf)
    fu = puv[face].reshape(-1, 2)
    fp = corners[pf[face]].reshape(-1, 3)
    du = np.polyfit(fp[:, 0], fu[:, 0], 1)[0] if np.ptp(fp[:, 0]) else 0.0
    assert face.sum() == 2 and du < 0 and fu.min() >= 0 and fu.max() <= 1, "the plate's face isn't read true from behind"
    ov, of, on, ouv = plate_text_overlay(corners[pf[face]])
    lift = (ov - c) @ n
    assert len(of) == 2 * PLATE_TEXT_GRID[0] * PLATE_TEXT_GRID[1] and np.allclose(lift, PLATE_TEXT_LIFT)
    assert (unit(face_normals(ov, of)) @ n > 0.99).all() and ouv.min() == 0 and ouv.max() == 1
    print(f"plate: face {face.sum()} triangles read true (du/dx {du:.4f}), the rest on v {puv[~face][..., 1].min():.3f}.."
          f"{puv[~face][..., 1].max():.3f}; the text overlay {len(of)} triangles, lifted {lift.min():.3f}")
    axles = {"F": (-0.38, -68.14, 29.86), "R": (-0.38, 68.14, 29.94)}
    total = 0
    for style in RIM_STYLES:
        for wheel in RIM_WHEELS:
            p = rim_style_pieces(style, wheel, axles[wheel])
            msgs, n_tris, (lo, hi), r_max = rim_check(p, style, wheel, axles[wheel])
            welded = [disc_check(v, f, nrm) for _, v, f, nrm, _, _ in p]
            total += n_tris
            print(f"rim {style} {wheel}: {n_tris} triangles (design {RIM_TRIS_DESIGN[style]} + the hoop), x {lo:.2f}..{hi:.2f}, "
                  f"r up to {r_max:.2f}; parts " + ", ".join(f"{q[5]} {len(q[2])}" for q in p))
            for m in msgs:
                print("   ", m)
            assert not msgs and n_tris <= RIM_TRIS_DESIGN[style] + RIM_HOOP_ALLOWANCE, f"rim {style} {wheel}"
            assert all(w[3] == 0 for w in welded), f"rim {style} {wheel}: triangles against their normals"
    for wheel in RIM_WHEELS:   # no triangle of one style's on another's (the parked bike carries them all, invisible but one)
        cents = {}
        for style in RIM_STYLES:
            p = rim_style_pieces(style, wheel, axles[wheel])
            cents[style] = {tuple(c) for _, v, f, _, _, _ in p for c in np.round(v[f].mean(axis=1) * 1e3).astype(np.int64)}
        twins = [(a, b, len(cents[a] & cents[b])) for i, a in enumerate(RIM_STYLES) for b in RIM_STYLES[i + 1:] if cents[a] & cents[b]]
        assert not twins, f"rims {wheel}: styles sharing triangles {twins}"
    print(f"rims: 14 shapes, {total} triangles; no two styles of a wheel share a triangle")


if __name__ == "__main__":
    _selftest()
