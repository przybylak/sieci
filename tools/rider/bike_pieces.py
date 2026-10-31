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


if __name__ == "__main__":
    _selftest()
