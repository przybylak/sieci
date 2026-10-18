"""Closest points on a triangle mesh for many points at once, in numpy alone (the mesh scripts'
users install numpy and fast_simplification and nothing else, so no scipy).

harley_meshes.py takes each decimated corner's shading normal from the glTF's own normals at the
closest point of its piece's source surface (test 40): some 600,000 points over the source's 1.3
million triangles. The triangles go into a uniform grid of cubic cells, each into every cell its
bounding box touches. A point looks at the triangles of the cells its search box (a cube of
half-width `reach` round it) overlaps: anything within reach of the point lies inside the box, so
its triangle is filed in one of those cells, and once the nearest triangle found is no farther
than reach the point is settled. The rest go round again with the reach doubled. So the answer is
the exact closest point, whatever the cell size and the first reach (they only set the speed);
where two triangles are exactly as near (a point over a convex edge is as near to both faces, a
point on two faces welded back to back is on both), the first found wins: a smaller reach's
before a larger one's, then by cell (x fastest, z slowest), and in a cell the triangles in
their order.

One grid per piece, of that piece's triangles only, sized to its triangles: the first version, one
grid of every piece's triangles at 0.25 units with the other pieces' filtered out after the
gather, took 3.5 minutes a run for the same answers (about 16 s now; the same distance for every
one of the 598,788 points, and 349 exact ties that went to the other triangle).
"""

import numpy as np


def closest_on_triangles(p, a, b, c):
    """The closest point to each p on the triangle (a, b, c), all (n, 3): (squared distance (n,),
    barycentric coordinates of the point (n, 3)). By the Voronoi regions of the corners, the
    edges and the face (Ericson, Real-Time Collision Detection, 5.1.5); a degenerate triangle
    gives its nearest corner."""
    ab, ac, ap = b - a, c - a, p - a
    d1 = np.einsum("ij,ij->i", ab, ap)
    d2 = np.einsum("ij,ij->i", ac, ap)
    bp = p - b
    d3 = np.einsum("ij,ij->i", ab, bp)
    d4 = np.einsum("ij,ij->i", ac, bp)
    cp = p - c
    d5 = np.einsum("ij,ij->i", ab, cp)
    d6 = np.einsum("ij,ij->i", ac, cp)
    va = d3 * d6 - d5 * d4
    vb = d5 * d2 - d1 * d6
    vc = d1 * d4 - d3 * d2
    den = va + vb + vc
    den = np.where(np.abs(den) > 1e-30, den, 1e-30)
    v = vb / den   # inside the face
    w = vc / den
    u = 1.0 - v - w
    with np.errstate(divide="ignore", invalid="ignore"):
        # The regions in reverse order of precedence, so where rounding puts a point in two,
        # the earlier test of the usual order has the last word.
        m = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0)   # edge bc
        t = np.where(m, (d4 - d3) / np.where(m, (d4 - d3) + (d5 - d6), 1.0), 0.0)
        u[m], v[m], w[m] = 0.0, 1.0 - t[m], t[m]
        m = (vb <= 0) & (d2 >= 0) & (d6 <= 0)                 # edge ac
        t = np.where(m, d2 / np.where(m, d2 - d6, 1.0), 0.0)
        u[m], v[m], w[m] = 1.0 - t[m], 0.0, t[m]
        m = (d6 >= 0) & (d5 <= d6)                            # corner c
        u[m], v[m], w[m] = 0.0, 0.0, 1.0
        m = (vc <= 0) & (d1 >= 0) & (d3 <= 0)                 # edge ab
        t = np.where(m, d1 / np.where(m, d1 - d3, 1.0), 0.0)
        u[m], v[m], w[m] = 1.0 - t[m], t[m], 0.0
        m = (d3 >= 0) & (d4 <= d3)                            # corner b
        u[m], v[m], w[m] = 0.0, 1.0, 0.0
        m = (d1 <= 0) & (d2 <= 0)                             # corner a
        u[m], v[m], w[m] = 1.0, 0.0, 0.0
    bad = ~np.isfinite(u) | ~np.isfinite(v) | ~np.isfinite(w)
    if bad.any():   # a degenerate triangle: its nearest corner
        near = np.argmin(np.stack([((p[bad] - x[bad]) ** 2).sum(1) for x in (a, b, c)], 1), 1)
        uvw = np.zeros((len(near), 3))
        uvw[np.arange(len(near)), near] = 1.0
        u[bad], v[bad], w[bad] = uvw[:, 0], uvw[:, 1], uvw[:, 2]
    q = a * u[:, None] + b * v[:, None] + c * w[:, None]
    return ((p - q) ** 2).sum(1), np.stack([u, v, w], 1)


class TriangleGrid:
    """A mesh's triangles, (m, 3, 3) corner coordinates, filed by cell for closest()."""

    def __init__(self, tris, cell):
        tris = np.asarray(tris, dtype=np.float64)
        self.a, self.b, self.c = (np.ascontiguousarray(tris[:, k]) for k in range(3))
        self.cell = float(cell)
        self.origin = tris.min(axis=(0, 1))
        self.dims = np.floor((tris.max(axis=(0, 1)) - self.origin) / self.cell).astype(np.int64) + 1
        c0 = self._cells(tris.min(axis=1))
        c1 = self._cells(tris.max(axis=1))
        tri, cx, cy, cz = self._expand(c0, c1)
        key = self._key(cx, cy, cz)
        order = np.argsort(key, kind="stable")   # stable: a cell's triangles stay in their order
        self.tri_of = tri[order]
        self.keys, self.start, self.count = np.unique(key[order], return_index=True, return_counts=True)

    def _cells(self, p):
        return np.clip(np.floor((p - self.origin) / self.cell).astype(np.int64), 0, self.dims - 1)

    def _key(self, cx, cy, cz):
        return (cz * self.dims[1] + cy) * self.dims[0] + cx

    @staticmethod
    def _expand(c0, c1):
        """Every cell of each box [c0, c1] (inclusive cell ranges, one row a box), x fastest:
        (box index, cx, cy, cz) per cell."""
        ext = c1 - c0 + 1
        n = ext.prod(axis=1)
        box = np.repeat(np.arange(len(c0)), n)
        k = np.arange(len(box)) - np.repeat(np.cumsum(n) - n, n)
        ex, ey = ext[box, 0], ext[box, 1]
        return (box, c0[box, 0] + k % ex, c0[box, 1] + (k // ex) % ey, c0[box, 2] + k // (ex * ey))

    def closest(self, p, reach, budget=200_000):
        """The nearest triangle to each point p (n, 3) and the closest point on it: (triangle
        index (n,), barycentric coordinates (n, 3), distance (n,)). reach is the first search
        box's half-width; budget bounds the point-triangle pairs worked on at once (memory)."""
        p = np.asarray(p, dtype=np.float64)
        n = len(p)
        best = np.full(n, np.inf)
        tri = np.zeros(n, np.int64)
        bary = np.zeros((n, 3))
        todo = np.arange(n)
        r = float(reach)
        while len(todo):
            lo = self._cells(p[todo] - r)
            hi = self._cells(p[todo] + r)
            whole = np.all((lo == 0) & (hi == self.dims - 1), axis=1)   # the box takes in every cell
            qi, cx, cy, cz = self._expand(lo, hi)
            key = self._key(cx, cy, cz)
            at = np.minimum(np.searchsorted(self.keys, key), len(self.keys) - 1)
            hit = self.keys[at] == key
            qi, at = qi[hit], at[hit]   # (point, filled cell) in order: a point's cells together
            cnt = self.count[at]
            per_point = np.bincount(qi, weights=cnt, minlength=len(todo)).astype(np.int64)
            # Chunks of whole points, each about `budget` pairs (a point's pairs stay together).
            cum = np.cumsum(per_point)
            cuts = np.searchsorted(cum, np.arange(budget, cum[-1] if len(cum) else 0, budget), side="right")
            cell_end = np.searchsorted(qi, np.r_[cuts, len(todo)])
            cell_from = 0
            for pt_from, pt_to, ce in zip(np.r_[0, cuts], np.r_[cuts, len(todo)], cell_end):
                if pt_to <= pt_from:
                    cell_from = ce
                    continue
                c_cnt = cnt[cell_from:ce]
                c_start = self.start[at[cell_from:ce]]
                c_q = qi[cell_from:ce]
                cell_from = ce
                if not len(c_cnt):
                    continue
                total = int(c_cnt.sum())
                rep = np.repeat(np.arange(len(c_cnt)), c_cnt)
                within = np.arange(total) - np.repeat(np.cumsum(c_cnt) - c_cnt, c_cnt)
                cand = self.tri_of[c_start[rep] + within]
                pq = c_q[rep]   # pairs, in order of the point
                d2, bc = closest_on_triangles(p[todo[pq]], self.a[cand], self.b[cand], self.c[cand])
                first = np.r_[0, np.flatnonzero(pq[1:] != pq[:-1]) + 1]
                pts = pq[first]
                least = np.minimum.reduceat(d2, first)
                lens = np.diff(np.r_[first, len(pq)])
                at_least = np.flatnonzero(d2 == np.repeat(least, lens))
                pick = at_least[np.searchsorted(at_least, first)]   # the first pair at the least distance
                g = todo[pts]
                better = least < best[g]
                g, pick = g[better], pick[better]
                best[g] = least[better]
                tri[g] = cand[pick]
                bary[g] = bc[pick]
            settled = (best[todo] <= r * r) | whole
            todo = todo[~settled]
            r *= 2.0
        return tri, bary, np.sqrt(best)


def nearest_vertex(v, p, reach=2.0):
    """The index of the nearest of the points v (m, 3) to each point p (n, 3): the first of them
    on a tie, the same answers as np.argmin over all of v, from the points in a cube of half-width
    reach round each p (v sorted by x, so a slab is a slice), the reach doubled until the nearest
    lies within it. harley_meshes.py's bolts: 267 centres against 600,000 source vertices took 6 s
    by the whole argmin, under 1 s so."""
    v = np.asarray(v, dtype=np.float64)
    if not len(v):
        raise ValueError("no points to search")
    order = np.argsort(v[:, 0], kind="stable")
    xs = v[order, 0]
    out = np.zeros(len(p), np.int64)
    for k, q in enumerate(np.asarray(p, dtype=np.float64)):
        r = float(reach)
        while True:
            a = int(np.searchsorted(xs, q[0] - r, side="left"))
            b = int(np.searchsorted(xs, q[0] + r, side="right"))
            idx = np.sort(order[a:b])   # by index, so the first of a tie wins as in argmin
            idx = idx[np.all(np.abs(v[idx, 1:] - q[1:]) <= r, axis=1)]
            if len(idx):
                d = ((v[idx] - q) ** 2).sum(axis=1)
                j = int(np.argmin(d))
                if d[j] <= r * r or len(idx) == len(v):   # all nearer than r lie in the cube
                    out[k] = idx[j]
                    break
            r *= 2.0
    return out
