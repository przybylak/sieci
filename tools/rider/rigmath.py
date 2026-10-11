"""Small rig toolkit for Fallout 4 skeletons: quaternions, forward kinematics,
two-bone IK and linear-blend skinning (for preview renders).

Conventions (same as Havok / the game):
  - quaternions are (x, y, z, w) and rotate column vectors: v' = R(q) @ v
  - a bone's local transform is  T(translation) @ R(rotation)
  - global = parent_global @ local, everything in the character's Root space
    (+Y forward, +Z up, +X to the character's right)
"""

import math
from dataclasses import dataclass

import numpy as np


# --------------------------------------------------------------------------
# Quaternions (x, y, z, w)
# --------------------------------------------------------------------------

def q_norm(q):
    q = np.asarray(q, dtype=float)
    return q / np.linalg.norm(q)


def q_mul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return np.array([
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    ])


def q_conj(q):
    return np.array([-q[0], -q[1], -q[2], q[3]])


def q_axis_angle(axis, degrees):
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    h = math.radians(degrees) / 2
    return np.array([*(axis * math.sin(h)), math.cos(h)])


def q_to_mat(q):
    x, y, z, w = q_norm(q)
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def mat_to_q(m):
    m = np.asarray(m, dtype=float)
    tr = m[0, 0] + m[1, 1] + m[2, 2]
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        q = [(m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s, 0.25 * s]
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = math.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        q = [0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s, (m[2, 1] - m[1, 2]) / s]
    elif m[1, 1] > m[2, 2]:
        s = math.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        q = [(m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[2, 1]) / s, (m[0, 2] - m[2, 0]) / s]
    else:
        s = math.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
        q = [(m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, 0.25 * s, (m[1, 0] - m[0, 1]) / s]
    q = q_norm(q)
    return q if q[3] >= 0 else -q


def q_slerp(a, b, t):
    a, b = q_norm(a), q_norm(b)
    d = float(np.dot(a, b))
    if d < 0:
        b, d = -b, -d
    if d > 0.9995:
        return q_norm(a + t * (b - a))
    th = math.acos(d)
    return (math.sin((1 - t) * th) * a + math.sin(t * th) * b) / math.sin(th)


def rot_between(u, v):
    """Smallest rotation matrix turning direction u onto direction v."""
    u = np.asarray(u, float) / np.linalg.norm(u)
    v = np.asarray(v, float) / np.linalg.norm(v)
    c = float(np.dot(u, v))
    axis = np.cross(u, v)
    s = np.linalg.norm(axis)
    if s < 1e-9:
        if c > 0:
            return np.eye(3)
        # 180 degrees: any perpendicular axis
        perp = np.cross(u, [1, 0, 0] if abs(u[0]) < 0.9 else [0, 1, 0])
        return q_to_mat(q_axis_angle(perp, 180))
    return q_to_mat(q_axis_angle(axis, math.degrees(math.atan2(s, c))))


def rot_x(deg):
    return q_to_mat(q_axis_angle([1, 0, 0], deg))


def rot_y(deg):
    return q_to_mat(q_axis_angle([0, 1, 0], deg))


def rot_z(deg):
    return q_to_mat(q_axis_angle([0, 0, 1], deg))


def compose(t, r):
    m = np.eye(4)
    m[:3, :3] = r
    m[:3, 3] = t
    return m


# --------------------------------------------------------------------------
# Skeleton and forward kinematics
# --------------------------------------------------------------------------

@dataclass
class Rig:
    names: list
    parents: list
    ref_t: np.ndarray   # (n, 3) local translations
    ref_q: np.ndarray   # (n, 4) local rotations

    @classmethod
    def from_hkx(cls, skeleton):
        return cls(
            names=list(skeleton.bones),
            parents=list(skeleton.parents),
            ref_t=np.array([p.translation for p in skeleton.reference_pose], dtype=float),
            ref_q=np.array([p.rotation for p in skeleton.reference_pose], dtype=float),
        )

    def index(self, name):
        return self.names.index(name)

    def fk(self, local_t=None, local_q=None):
        """Global 4x4 transforms for all bones from local translations/rotations."""
        local_t = self.ref_t if local_t is None else local_t
        local_q = self.ref_q if local_q is None else local_q
        g = np.zeros((len(self.names), 4, 4))
        for i, p in enumerate(self.parents):
            local = compose(local_t[i], q_to_mat(local_q[i]))
            g[i] = local if p < 0 else g[p] @ local
        return g


class Pose:
    """Mutable pose: local translations/rotations plus helpers to set global rotations."""

    def __init__(self, rig: Rig):
        self.rig = rig
        self.t = rig.ref_t.copy()
        self.q = rig.ref_q.copy()

    def copy(self):
        p = Pose(self.rig)
        p.t, p.q = self.t.copy(), self.q.copy()
        return p

    def globals(self):
        return self.rig.fk(self.t, self.q)

    def set_global_rot(self, name, r_global, g=None):
        """Give a bone a global rotation (its parent's current global stays as it is)."""
        i = self.rig.index(name)
        g = self.globals() if g is None else g
        p = self.rig.parents[i]
        parent_r = np.eye(3) if p < 0 else g[p][:3, :3]
        self.q[i] = mat_to_q(parent_r.T @ r_global)

    def rotate_global(self, name, r_delta):
        """Apply an extra global-space rotation to a bone (and so to its children)."""
        g = self.globals()
        i = self.rig.index(name)
        self.set_global_rot(name, r_delta @ g[i][:3, :3], g)

    def aim(self, name, target, g=None):
        """Turn a bone (minimal rotation) so its +X axis points at a world position."""
        g = self.globals() if g is None else g
        i = self.rig.index(name)
        cur = g[i][:3, :3]
        pos = g[i][:3, 3]
        r = rot_between(cur[:, 0], np.asarray(target) - pos) @ cur
        self.set_global_rot(name, r, g)

    def pos(self, name):
        return self.globals()[self.rig.index(name)][:3, 3]


def two_bone_ik(pose: Pose, upper, lower, end, target, pole):
    """Point upper/lower bones so `end` reaches `target`, bending toward `pole`.

    Lengths come from the rig; the bend plane contains the pole direction.
    """
    rig = pose.rig
    g = pose.globals()
    a = g[rig.index(upper)][:3, 3]
    b0 = g[rig.index(lower)][:3, 3]
    c0 = g[rig.index(end)][:3, 3]
    l1 = np.linalg.norm(b0 - a)
    l2 = np.linalg.norm(c0 - b0)
    target = np.asarray(target, float)
    d = target - a
    dist = min(np.linalg.norm(d), l1 + l2 - 1e-3)
    dirn = d / np.linalg.norm(d)
    # distance along a->target where the knee/elbow projects, and its offset from the line
    x = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist)
    h = math.sqrt(max(l1 * l1 - x * x, 0.0))
    pole = np.asarray(pole, float)
    side = pole - np.dot(pole, dirn) * dirn
    side /= np.linalg.norm(side)
    joint = a + dirn * x + side * h
    pose.aim(upper, joint)
    pose.aim(lower, a + dirn * dist)
    return joint


# --------------------------------------------------------------------------
# Skinning (previews)
# --------------------------------------------------------------------------

def xform_to_mat(buf):
    """PyNifly TransformBuf -> 4x4 (rotation rows, uniform scale, translation)."""
    m = np.eye(4)
    m[:3, :3] = np.array([list(r) for r in buf.rotation], dtype=float) * float(buf.scale)
    m[:3, 3] = list(buf.translation)
    return m


def nif_followers(skeleton_nif, rig: Rig):
    """Bones that exist only in skeleton.nif (skin helpers like Belly_skin).

    They aren't animated; they follow their parent. Returns [(name, parent, local 4x4)]
    ordered so parents come first.
    """
    nodes = skeleton_nif.nodes
    out, known = [], set(rig.names)
    pending = [n for n in nodes if n not in known and nodes[n].parent is not None]
    while pending:
        progressed = False
        for name in list(pending):
            parent = nodes[name].parent.name
            if parent in known:
                out.append((name, parent, xform_to_mat(nodes[name].transform)))
                known.add(name)
                pending.remove(name)
                progressed = True
        if not progressed:
            break
    return out


class SkinnedMesh:
    """A nif shape's verts + skin, ready to be posed with a rig's global transforms."""

    def __init__(self, shape, rig: Rig, followers=()):
        self.rig = rig
        self.followers = list(followers)
        self.verts = np.array(shape.verts, dtype=float)
        self.tris = np.array(shape.tris, dtype=int)
        g2s = shape.global_to_skin
        self.g2s = xform_to_mat(g2s) if g2s is not None else np.eye(4)
        self.bones = []
        names = rig.names + [f[0] for f in self.followers]
        weights = shape.bone_weights
        for bone, vw in weights.items():
            if bone not in names:
                continue
            idx = np.array([v for v, _ in vw], dtype=int)
            w = np.array([wt for _, wt in vw], dtype=float)
            s2b = xform_to_mat(shape.get_shape_skin_to_bone(bone))
            self.bones.append((names.index(bone), s2b, idx, w))

    def _all_globals(self, globals_):
        names = list(self.rig.names)
        g = list(globals_)
        for name, parent, local in self.followers:
            g.append(g[names.index(parent)] @ local)
            names.append(name)
        return g

    def posed(self, globals_):
        globals_ = self._all_globals(globals_)
        hom = np.c_[self.verts, np.ones(len(self.verts))]
        out = np.zeros((len(self.verts), 3))
        total = np.zeros(len(self.verts))
        for bi, s2b, idx, w in self.bones:
            # Verts are stored in skin space; skin-to-bone already maps them into
            # bone space (it includes the inverse of global-to-skin).
            m = globals_[bi] @ s2b
            out[idx] += (hom[idx] @ m.T)[:, :3] * w[:, None]
            total[idx] += w
        missing = total < 1e-6
        out[missing] = self.verts[missing]
        total[missing] = 1.0
        return out / total[:, None]
