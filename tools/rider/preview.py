#!/usr/bin/env python3
"""Renders preview images of the riding poses: posed body + bike from a few angles.

  python preview.py --pynifly <io_scene_nifly> --vanilla <...>/meshes/actors/character \
      --bike <Data>/Meshes/CMB/CMB_BikeWorn.nif --body <...>/malebody.nif --out preview.png
"""

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import riding_anims as R  # noqa: E402
from rigmath import Rig, SkinnedMesh, nif_followers, rot_x, rot_z  # noqa: E402


def draw(ax, meshes, view, title):
    """Painter's-algorithm render. view: 3x3 rotation, camera looks along +Y of the view space."""
    from matplotlib.collections import PolyCollection
    polys, shades, depths = [], [], []
    light = np.array([0.4, -0.6, 0.7])
    light /= np.linalg.norm(light)
    for verts, tris, color in meshes:
        v = verts @ view.T
        t = v[tris]
        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
        lit = 0.35 + 0.65 * np.abs(n @ light)
        polys.extend(t[:, :, [0, 2]])
        shades.extend(np.clip(np.outer(lit, color), 0, 1))
        depths.extend(t[:, :, 1].mean(axis=1))
    order = np.argsort(depths)[::-1]
    pc = PolyCollection([polys[i] for i in order], facecolors=[shades[i] for i in order], edgecolors="none")
    ax.add_collection(pc)
    allv = np.concatenate([m[0] @ view.T for m in meshes])
    ax.set_xlim(allv[:, 0].min() - 5, allv[:, 0].max() + 5)
    ax.set_ylim(allv[:, 2].min() - 5, allv[:, 2].max() + 5)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=9)
    ax.axis("off")


VIEWS = {
    "side": rot_z(90),                        # camera on the rider's right
    "front 3/4": rot_x(-12) @ rot_z(150),
    "rear 3/4": rot_x(-15) @ rot_z(-35),
    "front": rot_z(180),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pynifly", type=Path, required=True)
    ap.add_argument("--vanilla", type=Path, required=True)
    ap.add_argument("--bike", type=Path, required=True)
    ap.add_argument("--body", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--poses", default="cruise,run,leanleft,idle")
    ap.add_argument("--views", default=",".join(VIEWS))
    ap.add_argument("--size", type=float, default=4.2)
    args = ap.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(args.pynifly))
    from pyn.pynifly import NifFile

    A = R.load_anim_module(args.pynifly)
    rig = Rig.from_hkx(A.load_fo4_skeleton(str(args.vanilla / "characterassets" / "skeleton.hkx")))
    followers = nif_followers(NifFile(str(args.vanilla / "characterassets" / "skeleton.nif")), rig)
    body = SkinnedMesh(NifFile(str(args.body)).shapes[0], rig, followers)
    bike_shape = NifFile(str(args.bike)).shapes[0]
    bike_v = np.array(bike_shape.verts)
    bike_t = np.array(bike_shape.tris)

    rider = R.Rider(rig)

    def min_z(pose):
        v = body.posed(pose.globals())
        sel = (np.abs(v[:, 0]) < 9) & (v[:, 1] > -14) & (v[:, 1] < 4) & (v[:, 2] > 50)
        return float(v[sel, 2].min())
    rider.seat(min_z)

    named = {
        "cruise": R.RideParams(lean=R.SPEEDS["walk"]["lean"]),
        "run": R.RideParams(lean=R.SPEEDS["run"]["lean"]),
        "leanleft": R.RideParams(lean=R.SPEEDS["run"]["lean"], roll=-R.SPEEDS["run"]["lean_roll"]),
        "idle": R.IDLE,
    }
    poses = [(n, named[n]) for n in args.poses.split(",")]
    views = {k: VIEWS[k] for k in args.views.split(",")}
    fig, axes = plt.subplots(len(poses), len(views), figsize=(args.size * len(views), args.size * len(poses)))
    axes = np.atleast_2d(axes)
    for row, (name, params) in zip(axes, poses):
        pose = rider.pose(params)
        g = pose.globals()
        body_v = body.posed(g)
        bike = (np.c_[bike_v, np.ones(len(bike_v))] @ g[rig.index("AnimObjectA")].T)[:, :3]
        meshes = [(bike, bike_t, np.array([0.55, 0.55, 0.6])), (body_v, body.tris, np.array([0.93, 0.76, 0.62]))]
        for ax, (vname, view) in zip(row, views.items()):
            draw(ax, meshes, view, f"{name} - {vname}")
    fig.tight_layout()
    fig.savefig(args.out, dpi=70)
    print(f"wrote {args.out}; COM z = {rider.hip_z:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
