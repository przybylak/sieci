#!/usr/bin/env python3
"""The geometry of art build B's new shapes (build 2026-11-21a, c3.md 3.5/3.6 and 3.8), numpy alone: the two wear
shells and the front mudguard's badge patch. look_shells.py puts them into the five built nifs; check_bike_meshes.py
measures them with the same functions.

The wear shells (static_wear over static_paint, fork_wear over fork_paint). A shell is its source's own vertex records
(UVs, normals, tangents, skin weights) with each position lifted along the normal averaged per position (weld_positions:
the vertices at one place share one lift, so the shell stays closed where the source's normals split at a hard edge, a
UV seam's copies too), SHELL_LIFT out, which is then fitted per position (shell_positions):
- a concave corner (a hard edge folding inward, a groove) brings the faces nearer than the lift along the averaged
  normal: the lift is lengthened there till the nearest point of the source is SHELL_LIFT away (at most
  SHELL_LIFT_MAX along the normal);
- the worn nifs keep positions in half floats (1/128 to 1/16 of a unit apart over the bike), which would put a shell
  vertex up to 0.06 off SHELL_LIFT over the worn nif's own (rounded) source: each position is moved within its
  rounding so that its worn copy is the half-float point nearest SHELL_LIFT over the worn source, its full-precision
  distance kept within SHELL_FIT_KEEP of SHELL_LIFT (fit_half).
Triangles with a vertex inside another shape (inside_shapes: the generalized winding number of each closed piece, in
full precision and in the worn half floats) are left out of the shell, and the vertices only they used: under the
frame, the seat, the chrome trim and the fork's mounts the wear would be drawn where it can't be seen.

The front mudguard's badge patch (fork_badgeFront): the rear fender patch's method (bike_pieces.fender_badge_patch: a
grid of quads cast onto the surface, its columns at equal steps of arc length across, every vertex lifted along the
surface's normal) turned to the mudguard, which wraps round the front wheel: each row of the grid lies in the plane
through the front axle at its angle (FRONT_PATCH_DEG: 0 straight up, + toward the front), rows at equal angles (equal
arc length along the mudguard's crown), and each row's rays cast toward the axle (the triangles turned so that ray is
straight down, then bike_pieces._cast_down). Its UVs are the badge atlas' plate rectangle (BADGE_PLATE_RECT, as the
tank plates and the rear patch), read true from in front of the bike: u to the viewer's right (the bike's left,
parked +x), v down toward the front of the bike. FRONT_PATCH_LIFT puts it over the wear shell (SHELL_LIFT) by more
than the half floats' rounding, so a badge shows over the mud (FENDER_RAISE does the same for the rear patch).

All in the parked frame (+x the bike's left, -y ahead, z up), full precision.
"""

import math

import numpy as np

import bike_pieces as BP
from nearest import TriangleGrid

SHELL_LIFT = 0.32          # c3.md 3.5: the shells' lift over their source (DESIGN's overlay rule: 0.25 and up in half floats)
SHELL_BAND = (0.30, 0.34)  # check_bike_meshes.py: every shell vertex this far over its source, in every nif
SHELL_LIFT_MAX = 0.48      # a concave corner's lift along its averaged normal at most this (45 degrees each way)
SHELL_FIT_KEEP = 0.019     # the half floats' fit (fit_half): the full-precision distance kept within this of SHELL_LIFT
SHELL_FIT_REACH = 2        # ... over the half-float points this many steps either side of the target in each coordinate
SHELL_FLOOR = 0.05         # over the shell's triangles (not only at its vertices) never nearer the source than this
INSIDE = 0.5               # a point is inside a shape where the shape's winding number is over this
FRONT_PATCH_SIZE = (8.4, 3.5)     # across (arc length), along (arc length): the plate rectangle's 2.4:1; the crown's
                                  # facets under it within 35 degrees of the axle's direction (8.8 across reaches a facet
                                  # of the shoulder at 46), 2.1 inside the crown's edge each side at its narrowest row
FRONT_PATCH_DEG = 1.5             # the patch's middle row: degrees round the front axle from straight up, + to the front
FRONT_PATCH_GRID = (14, 6)        # quads across, along (2 x 84 triangles; the rear patch's 0.58 spacing)
FRONT_PATCH_LIFT = 0.48           # over the mudguard: SHELL_LIFT and 0.16 more (the wear shell under it, both in half floats)
FRONT_PATCH_SAMPLES = 801         # the arc length's samples across, as the rear patch's
FRONT_PATCH_MIN_UP = 0.2          # a cast hit counts while its normal is within acos(this) of the row's ray (the crown, not the side wall)
FENDER_RAISE = 0.16               # the rear fender patch (static_badgeFender, bike_pieces.FENDER_PATCH_LIFT 0.32 over the fender)
                                  # raised this much more along its own normals: 0.48, over static_wear as the front patch
BADGE_PLATE_RECT = BP.BADGE_PLATE_RECT


def unit(a):
    return BP.unit(a)


# --- the shells ---------------------------------------------------------------------------------------------------

def weld_positions(v, scale=65536.0):
    """A position id per vertex (vertices at the same place share one: the hard edges' and the UV seams' copies)."""
    key = np.round(np.asarray(v, np.float64) * scale).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    return inv.reshape(-1), first


def averaged_normals(n, pos):
    """The normal averaged per position: the mean of the distinct normals of a position's vertices (a UV seam's copies
    count once), unit length. n (V, 3) the vertices' normals, pos (V,) their position ids."""
    n = unit(n)
    q = np.round(n * 64.0).astype(np.int64)   # the stored normals are bytes: equal ones agree to 1/127
    _, pick = np.unique(np.column_stack([pos, q]), axis=0, return_index=True)
    acc = np.zeros((int(pos.max()) + 1, 3))
    np.add.at(acc, pos[pick], n[pick])
    return unit(acc)


def surface_distance(points, tris, reach=0.6):
    """The distance from each point to the nearest point of the triangles (T, 3, 3)."""
    if not len(points):
        return np.zeros(0)
    return TriangleGrid(tris, 1.0).closest(np.asarray(points, np.float64), reach=reach)[2]


def shell_positions(v, f, n, worn=None, lift=SHELL_LIFT, log=None):
    """The shell's positions, one per source vertex (see the module's notes). v, f, n: the source in the parked frame
    (full precision). worn: None, or (R, t, source_worn) the worn frame (x_worn = R x + t) and the worn nif's own
    source positions (half floats), for the fit to the half floats (fit_half). Returns (positions (V, 3) in the parked
    frame, the averaged normals (V, 3), numbers)."""
    v = np.asarray(v, np.float64)
    f = np.asarray(f, np.int64)
    pos, first = weld_positions(v)
    na = averaged_normals(n, pos)                 # per position
    p = v[first]
    tris = v[f]
    grid = TriangleGrid(tris, 1.0)
    dist = lambda d: grid.closest(p + d[:, None] * na, reach=0.6)[2]
    d = np.full(len(p), float(lift))
    d0 = dist(d)
    concave = d0 < lift - 1e-4
    for _ in range(4):   # a concave corner: lengthen till the nearest face is `lift` away (the distance about linear in d)
        got = dist(d)
        short = got < lift - 1e-5
        if not short.any():
            break
        d[short] = np.minimum(d[short] * lift / np.maximum(got[short], 1e-6), SHELL_LIFT_MAX)
    full = dist(d)
    numbers = dict(positions=len(p), concave=int(concave.sum()), lift_max=float(d.max()),
                   full_min=float(full.min()), full_max=float(full.max()))
    q = p + d[:, None] * na
    if worn is not None:
        q = fit_half(q, grid, worn, f, lift, numbers)
    if log:
        log(f"    {numbers['positions']} positions, {numbers['concave']} at a concave corner (lifted up to "
            f"{numbers['lift_max']:.3f} along their averaged normal); every position {numbers['full_min']:.4f}-"
            f"{numbers['full_max']:.4f} over the source"
            + (f"; fitted to the worn nifs' half floats ({numbers['moved']} moved within their rounding cell): "
               f"{numbers['fit_full'][0]:.4f}-{numbers['fit_full'][1]:.4f} in full precision, {numbers['fit_worn'][0]:.4f}-"
               f"{numbers['fit_worn'][1]:.4f} in the half floats" if worn is not None else ""))
    return q[pos], na[pos], numbers


def _half_step(L, up):
    """The gap from each half float L to the next one up (up True) or down, per coordinate."""
    h = np.asarray(L, np.float64).astype(np.float16)
    nxt = np.nextafter(h, np.float16(np.inf) if up else np.float16(-np.inf)).astype(np.float64)
    return np.abs(nxt - h.astype(np.float64))


def fit_half(q, grid, worn, f, lift=SHELL_LIFT, numbers=None, keep=SHELL_FIT_KEEP, margin=0.45, reach=SHELL_FIT_REACH):
    """The shell's positions (P, 3, parked frame, full precision) moved within the worn nifs' half-float rounding so
    their worn copies lie as near `lift` over the worn nifs' own source as the half floats allow: per position the
    half-float points round the worn frame's target (the nearest and `reach` more either side in each coordinate), each taken
    as the worn vertex only if a point of its rounding cell (the target clamped into it, `margin` of the gaps either
    side) stays within `keep` of `lift` over the source in full precision; the one whose larger miss of `lift` (the
    half floats' or the full precision's) is the least wins. The worn vertex is then exactly that point's half float."""
    R, t, vw = worn
    vw = np.asarray(vw, np.float64)
    wgrid = TriangleGrid(vw[np.asarray(f, np.int64)], 1.0)
    target = q @ R.T + t                       # the worn (and view) frame
    base = half(target)
    steps = range(-reach, reach + 1)
    offs = [(a, b, c) for a in steps for b in steps for c in steps]
    best_err = np.full(len(q), np.inf)
    best_q = q.copy()
    best_worn = np.full(len(q), np.nan)
    best_full = np.full(len(q), np.nan)
    for o in offs:
        o = np.array(o, np.float64)
        L = base.copy()
        for k in range(3):   # o[k] half floats down or up in each coordinate
            for _ in range(int(abs(o[k]))):
                L[:, k] = np.nextafter(L[:, k].astype(np.float16), np.float16(np.inf if o[k] > 0 else -np.inf)).astype(np.float64)
        dl, dh = _half_step(L, False), _half_step(L, True)
        qw = L + np.clip(target - L, -margin * dl, margin * dh)   # the target clamped into L's rounding cell
        ok = np.all(half(qw.astype(np.float32)) == L, axis=1)
        qp = (qw - t) @ R                       # back to the parked frame (R orthonormal)
        gf = grid.closest(qp, reach=0.6)[2]
        gw = wgrid.closest(L, reach=0.6)[2]
        ok &= np.abs(gf - lift) <= keep
        err = np.maximum(np.abs(gw - lift), np.abs(gf - lift)) + 1e-3 * (np.abs(gw - lift) + np.abs(gf - lift))
        better = ok & (err < best_err)
        best_err[better] = err[better]
        best_q[better] = qp[better]
        best_worn[better] = gw[better]
        best_full[better] = gf[better]
    if np.isnan(best_worn).any():   # no candidate kept the full precision within `keep`: the target as it is
        miss = np.isnan(best_worn)
        best_q[miss] = q[miss]
        best_full[miss] = grid.closest(q[miss], reach=0.6)[2]
        best_worn[miss] = wgrid.closest(half(target[miss]), reach=0.6)[2]
    if numbers is not None:
        numbers.update(moved=int((np.abs(best_q - q).max(axis=1) > 1e-9).sum()),
                       fit_full=(float(best_full.min()), float(best_full.max())),
                       fit_worn=(float(best_worn.min()), float(best_worn.max())))
    return best_q


def half(x):
    """Positions as the worn nifs store them (IEEE half floats, round to nearest even), back in float64."""
    return np.asarray(x, np.float64).astype(np.float16).astype(np.float64)


def triangle_samples(v, f, steps=4):
    """Points on each triangle: the barycentric grid of `steps` (corners, edges and inside): (T, k, 3)."""
    w = np.array([(a / steps, b / steps, 1.0 - (a + b) / steps) for a in range(steps + 1) for b in range(steps + 1 - a)])
    return np.einsum("kj,ijd->ikd", w, np.asarray(v, np.float64)[f]), w


# --- inside another shape -----------------------------------------------------------------------------------------

def pieces(v, f):
    """A shape's connected pieces over its welded positions: [(triangle indices, closed)] (closed: every welded edge
    in exactly two of the piece's triangles)."""
    pos, _ = weld_positions(v, 1024.0)
    tw = pos[np.asarray(f, np.int64)]
    lab = BP.islands(int(pos.max()) + 1, tw)
    out = []
    for k in range(int(lab.max()) + 1):
        ti = np.where(lab == k)[0]
        e = np.sort(np.vstack([tw[ti][:, [0, 1]], tw[ti][:, [1, 2]], tw[ti][:, [2, 0]]]), axis=1)
        _, c = np.unique(e, axis=0, return_counts=True)
        out.append((ti, bool((c == 2).all())))
    return out


def winding_number(points, tris, chunk=4_000_000):
    """The generalized winding number of the triangles (T, 3, 3) at each point (van Oosterom and Strackee's solid
    angle): about 1 inside a closed surface wound outward, 0 outside, under 0.5 in size for an open sheet."""
    p = np.asarray(points, np.float64)
    out = np.zeros(len(p))
    if not len(p) or not len(tris):
        return out
    step = max(1, chunk // len(tris))
    A, B, C = tris[:, 0], tris[:, 1], tris[:, 2]
    for s in range(0, len(p), step):
        q = p[s:s + step, None, :]
        a, b, c = A[None] - q, B[None] - q, C[None] - q
        la, lb, lc = (np.linalg.norm(x, axis=2) for x in (a, b, c))
        det = np.einsum("ijk,ijk->ij", a, np.cross(b, c))
        den = la * lb * lc + np.einsum("ijk,ijk->ij", a, b) * lc + np.einsum("ijk,ijk->ij", b, c) * la \
            + np.einsum("ijk,ijk->ij", c, a) * lb
        out[s:s + step] = (2.0 * np.arctan2(det, den)).sum(axis=1) / (4.0 * math.pi)
    return out


def inside_shapes(points, shapes, pad=0.0):
    """Which points lie inside which shapes: shapes {label: (verts, tris)}; per point the first label it is inside
    (the winding number over INSIDE of the shape's pieces whose box holds it), else None. Every piece is counted
    (an open sheet's winding number stays under 0.5)."""
    p = np.asarray(points, np.float64)
    hit = np.full(len(p), None, dtype=object)
    for label, (sv, sf) in shapes.items():
        sv, sf = np.asarray(sv, np.float64), np.asarray(sf, np.int64)
        lo_all, hi_all = sv.min(axis=0) - pad, sv.max(axis=0) + pad
        cand = np.all((p >= lo_all) & (p <= hi_all), axis=1) & (hit == None)  # noqa: E711
        if not cand.any():
            continue
        w = np.zeros(len(p))
        for ti, _closed in pieces(sv, sf):
            t = sv[sf[ti]]
            lo, hi = t.min(axis=(0, 1)) - pad, t.max(axis=(0, 1)) + pad
            sel = cand & np.all((p >= lo) & (p <= hi), axis=1)
            if sel.any():
                w[sel] += winding_number(p[sel], t)
        inside = cand & (np.abs(w) > INSIDE)
        hit[inside] = label
    return hit


def keep_outside(f, inside_v):
    """The triangles none of whose vertices is inside another shape, and the vertices they use: (kept triangle mask,
    the kept vertices' indices in order, the triangles renumbered to them)."""
    f = np.asarray(f, np.int64)
    keep = ~np.asarray(inside_v, bool)[f].any(axis=1)
    used = np.unique(f[keep])
    remap = np.full(len(inside_v), -1, np.int64)
    remap[used] = np.arange(len(used))
    return keep, used, remap[f[keep]]


# --- the front mudguard's badge patch --------------------------------------------------------------------------------

def _row_frame(axle, deg):
    """The rotation taking the ray toward the axle at `deg` (0 straight down from above, + from the front: parked -y)
    to straight down, and back: (R, centre) with x' = R (x - centre)."""
    a = math.radians(deg)
    out = np.array([0.0, -math.sin(a), math.cos(a)])   # from the axle out to the crown at deg
    c, s = math.cos(a), math.sin(a)
    R = np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])
    if np.abs(R @ out - [0.0, 0.0, 1.0]).max() > 1e-9:
        R = R.T
    assert np.abs(R @ out - [0.0, 0.0, 1.0]).max() < 1e-9
    return R, np.asarray(axle, np.float64)


def _cast_row(tris, cn, axle, deg, xs):
    """The row at `deg`'s rays (one per x in xs, in the plane through the axle at that angle, toward the axle): the
    first hit's point and normal (facing out) in the parked frame, and whether it hit the crown (normal within
    acos(FRONT_PATCH_MIN_UP) of the ray)."""
    R, c = _row_frame(axle, deg)
    T = (tris - c) @ R.T
    N = cn @ R.T
    p, n, hit = BP._cast_down(T, N, np.asarray(xs, np.float64), np.zeros(len(xs)))
    hit &= n[:, 2] > FRONT_PATCH_MIN_UP
    return p @ R + c, n @ R, hit


def front_badge_patch(mudguard, axle, size=FRONT_PATCH_SIZE, centre_deg=FRONT_PATCH_DEG, grid=FRONT_PATCH_GRID,
                      lift=FRONT_PATCH_LIFT, rect=BADGE_PLATE_RECT):
    """The front mudguard's badge patch (see the module's notes): mudguard = (verts (n, 3), tris (m, 3), normals (n, 3))
    of fork_paint in the parked frame, axle the front axle there. Returns (verts (V, 3), tris (T, 3) wound outward,
    normals (V, 3), uvs (V, 2), numbers) in the parked frame."""
    v, f, n = (np.asarray(x) for x in mudguard)
    tris = np.asarray(v, np.float64)[np.asarray(f, np.int64)]
    cn = unit(np.asarray(n, np.float64))[np.asarray(f, np.int64)]
    nu, nv = grid
    w, h = size
    axle = np.asarray(axle, np.float64)
    x_lo, x_hi = float(tris[:, :, 0].min()), float(tris[:, :, 0].max())
    xs = np.linspace(x_lo, x_hi, FRONT_PATCH_SAMPLES)
    # the crown's radius at the middle row's centre (the middle of its crown run): the rows at equal arc length along
    # the crown are equal angles at that radius
    p, _, hit = _cast_row(tris, cn, axle, centre_deg, xs)
    if not hit.any():
        raise ValueError(f"front_badge_patch: no crown at {centre_deg} degrees")
    mid = int(np.argmin(np.abs(xs - 0.5 * (xs[hit].min() + xs[hit].max()))))
    r_crown = float(np.linalg.norm((p[mid] - axle)[1:]))
    half_deg = math.degrees(h / 2.0 / r_crown)
    degs = np.linspace(centre_deg - half_deg, centre_deg + half_deg, nv + 1)   # from the rear edge to the front edge
    # the centre line across: the middle of each row's crown run, averaged over the rows
    runs = []
    for deg in degs:
        _, _, hit = _cast_row(tris, cn, axle, deg, xs)
        if not hit.any():
            raise ValueError(f"front_badge_patch: the row at {deg:.2f} degrees misses the mudguard")
        idx = np.where(hit)[0]
        runs.append(0.5 * (xs[idx.min()] + xs[idx.max()]))
    x0 = float(np.mean(runs))
    rows_p, rows_n, widths = [], [], []
    for deg in degs:
        p, n_, hit = _cast_row(tris, cn, axle, deg, xs)
        c = int(np.argmin(np.abs(xs - x0)))
        if not hit[c]:
            raise ValueError(f"front_badge_patch: the centre line misses the mudguard at {deg:.2f} degrees")
        lo, hi = c, c
        while lo > 0 and hit[lo - 1]:
            lo -= 1
        while hi < len(xs) - 1 and hit[hi + 1]:
            hi += 1
        run = p[lo:hi + 1]
        s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(run, axis=0), axis=1))])
        s -= np.interp(x0, xs[lo:hi + 1], s)
        widths.append((float(-s[0]), float(s[-1])))
        want = np.linspace(-w / 2, w / 2, nu + 1)
        if want[0] < s[0] or want[-1] > s[-1]:
            raise ValueError(f"front_badge_patch: the crown is {s[-1] - s[0]:.2f} across at {deg:.2f} degrees, under the "
                             f"patch's {w}")
        px = np.interp(want, s, xs[lo:hi + 1])
        pp, nn, hh = _cast_row(tris, cn, axle, deg, px)
        if not hh.all():
            raise ValueError(f"front_badge_patch: a vertex misses the mudguard at {deg:.2f} degrees")
        rows_p.append(pp + lift * nn)
        rows_n.append(nn)
    V = np.vstack(rows_p)
    N = np.vstack(rows_n)
    idx = np.arange((nu + 1) * (nv + 1)).reshape(nv + 1, nu + 1)
    a, b, c_, d_ = idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()
    F = np.vstack([np.column_stack([a, b, c_]), np.column_stack([a, c_, d_])]).astype(np.int64)
    fn = BP.face_normals(V, F)
    cen = V[F].mean(axis=1) - np.asarray(axle, np.float64)
    cen[:, 0] = 0.0
    if (np.einsum("ij,ij->i", fn, cen) < 0).mean() > 0.5:
        F = F[:, [0, 2, 1]]
        fn = -fn
    if (np.einsum("ij,ij->i", fn, cen) <= 0).any():
        raise ValueError("front_badge_patch: a triangle faces in (the mudguard too steep for the grid)")
    gi, gj = np.meshgrid(np.arange(nu + 1), np.arange(nv + 1))
    u0, v0, u1, v1 = rect
    # the columns run toward parked +x (the bike's left: the viewer's right from in front), the rows from the rear edge
    # (the text's top seen from in front) to the front edge
    uv = np.column_stack([u0 + (u1 - u0) * gi.ravel() / nu, v0 + (v1 - v0) * gj.ravel() / nv])
    numbers = dict(r_crown=r_crown, degs=(float(degs[0]), float(degs[-1])), x0=x0, widths=widths,
                   margin=float(min(min(a_, b_) for a_, b_ in widths) - w / 2))
    return V, F, N, uv, numbers


def raise_patch(v, n, by=FENDER_RAISE):
    """The rear fender patch's vertices raised `by` along their own normals."""
    return np.asarray(v, np.float64) + by * unit(n)
