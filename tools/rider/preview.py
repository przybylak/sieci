#!/usr/bin/env python3
"""Renders preview images of the riding poses: posed body + bike from a few angles.

  python preview.py --pynifly <io_scene_nifly> --vanilla <...>/meshes/actors/character \
      --bike <Data>/Meshes/CMB/CMB_BikeWorn.nif --body <...>/malebody.nif --out preview.png \
      [--fit <Data>/Meshes/CMB/CMB_BikeFit.json] [--mirrors 1] [--lit] [--no-body] [--crop x0,x1,y0,y1,z0,z1]

The bike's shapes are shaded by the words in their names (SHADES: the 28 shapes since the 2026-10-31a build, the 12 of 27c), and
the ones the plugin turns with the bars ("_front", "_fork", "_wheelF" in the name) turn with the pose's steering.
--mirrors picks the mirror variant shown as [Look] Mirrors does in game (0 none, 1 stock, 2 under-bar egg, 3 under-
bar D), --lit adds the lit overlays (the dial's backlight, the brake light; the plugin hides them in game while
off), --no-body leaves the rider out, --crop draws only the triangles in a box of the bike's own space (+Y forward)
and fits the view to them (for close-ups, e.g. the bars: -45,45,25,80,75,115 with --views behind).
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
    allv = np.concatenate([m[0][np.unique(m[1])] @ view.T for m in meshes if len(m[1])])
    ax.set_xlim(allv[:, 0].min() - 5, allv[:, 0].max() + 5)
    ax.set_ylim(allv[:, 2].min() - 5, allv[:, 2].max() + 5)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=9)
    ax.axis("off")


# Shading by the words in a shape's name, the first that matches: grey tones or RGB.
SHADES = (("dialglow", (0.95, 0.85, 0.6)), ("_front_glow", (1.0, 1.0, 0.95)), ("_rear_brake", (1.0, 0.15, 0.1)),
          ("_rear_tail", (0.75, 0.08, 0.06)), ("_front_needle", (0.95, 0.4, 0.1)), ("_front_dial", (0.1, 0.1, 0.1)),
          ("_paint", (0.48, 0.07, 0.09)), ("glass", 0.9), ("mirror", 0.7), ("chrome", 0.75), ("exhaust", 0.72),
          ("metal", 0.75), ("badge", 0.6), ("seat", (0.27, 0.21, 0.17)), ("engine", 0.33), ("tyre", 0.2), ("rim", 0.28),
          ("black", 0.3), ("matte", 0.3))
MIRRORS = {"_front_mirrorstock": 1, "_front_mirrorunderegg": 2, "_front_mirrorunderd": 3}
LIT = ("_front_dialglow", "_rear_brake")   # overlays the plugin shows only while lit

VIEWS = {
    "side": rot_z(90),                        # camera on the rider's right
    "front 3/4": rot_x(-12) @ rot_z(150),
    "rear 3/4": rot_x(-15) @ rot_z(-35),
    "front": rot_z(180),
    "behind": rot_x(-35),                     # from behind and above the rider (the bars, the dial, the mirrors)
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pynifly", type=Path, required=True)
    ap.add_argument("--vanilla", type=Path, required=True)
    ap.add_argument("--bike", type=Path, required=True)
    ap.add_argument("--body", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--poses", default="cruise,run,leanleft,idle")
    ap.add_argument("--views", default="side,front 3/4,rear 3/4,front", help=f"of {', '.join(VIEWS)}")
    ap.add_argument("--size", type=float, default=4.2)
    ap.add_argument("--fit", type=Path, help="bike-fit file (CMB_BikeFit.json), as for riding_anims.py")
    ap.add_argument("--mirrors", type=int, default=1, choices=(0, 1, 2, 3),
                    help="the mirror variant shown: 0 none, 1 stock, 2 under-bar egg, 3 under-bar D")
    ap.add_argument("--lit", action="store_true", help="show the lit overlays (the dial's backlight, the brake light)")
    ap.add_argument("--no-body", action="store_true", help="leave the rider out")
    ap.add_argument("--crop", help="x0,x1,y0,y1,z0,z1: only the bike's triangles in this box (its own space)")
    args = ap.parse_args()
    crop = np.array([float(t) for t in args.crop.split(",")]).reshape(3, 2) if args.crop else None
    if args.fit:
        R.apply_fit(args.fit)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(args.pynifly))
    from pyn.pynifly import NifFile

    A = R.load_anim_module(args.pynifly)
    rig = Rig.from_hkx(A.load_fo4_skeleton(str(args.vanilla / "characterassets" / "skeleton.hkx")))
    followers = nif_followers(NifFile(str(args.vanilla / "characterassets" / "skeleton.nif")), rig)
    body = SkinnedMesh(NifFile(str(args.body)).shapes[0], rig, followers)
    # Every visible shape of the bike nif, but the mirror variants not chosen and the lit overlays unless --lit.
    bike_parts = []
    for shape in NifFile(str(args.bike)).shapes:
        name = shape.name.lower()
        if shape.flags & 1:
            continue
        variant = next((v for k, v in MIRRORS.items() if name.endswith(k)), None)
        if variant is not None and variant != args.mirrors:
            continue
        if name.endswith(LIT) and not args.lit:
            continue
        shade = next((s for word, s in SHADES if word in name), 0.55)
        colour = np.array(shade if isinstance(shade, tuple) else (shade, shade, shade + 0.05))
        steers = any(w in name for w in ("front", "_fork", "wheelf"))   # turns with the bars
        verts, tris = np.array(shape.verts), np.array(shape.tris)
        if crop is not None:
            inside = np.all((verts >= crop[:, 0]) & (verts <= crop[:, 1]), axis=1)
            tris = tris[inside[tris].all(axis=1)]
            if not len(tris):
                continue
        bike_parts.append((verts, tris, colour, steers))

    rider = R.Rider(rig)

    def min_z(pose):
        v = body.posed(pose.globals())
        sel = (np.abs(v[:, 0]) < 9) & (v[:, 1] > -14) & (v[:, 1] < 4) & (v[:, 2] > 50)
        return float(v[sel, 2].min())
    rider.seat(min_z)

    named = {
        "cruise": R.RideParams(lean=R.SPEEDS["walk"]["lean"]),
        "run": R.RideParams(lean=R.SPEEDS["run"]["lean"]),
        "leanleft": R.RideParams(lean=R.SPEEDS["run"]["lean"], roll=-R.SPEEDS["run"]["lean_roll"],
                                 steer=R.steer_for(-R.SPEEDS["run"]["lean_roll"])),
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
        meshes = []
        for v, t, c, steers in bike_parts:
            if steers and params.steer and R.STEER_AXIS is not None:
                v = (v - R.STEER_POINT) @ R.rot_about(R.STEER_AXIS, params.steer).T + R.STEER_POINT
            meshes.append(((np.c_[v, np.ones(len(v))] @ g[rig.index("AnimObjectA")].T)[:, :3], t, c))
        if not args.no_body:
            meshes.append((body_v, body.tris, np.array([0.93, 0.76, 0.62])))
        for ax, (vname, view) in zip(row, views.items()):
            draw(ax, meshes, view, f"{name} - {vname}")
    fig.tight_layout()
    fig.savefig(args.out, dpi=70)
    print(f"wrote {args.out}; COM z = {rider.hip_z:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
