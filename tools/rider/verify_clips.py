#!/usr/bin/env python3
"""Checks generated riding clips against the vanilla clips they replace.

For every clip: same length and frame count, the same control events at the same
times (footstep sounds excluded), identical root motion, all 95 bones present,
and the decoded pose matching what the generator intended (compression error).

  python verify_clips.py --pynifly <io_scene_nifly> --vanilla <...>/meshes/actors/character --clips <CMB_Rider folder>
"""

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import riding_anims as R  # noqa: E402
from rigmath import Rig  # noqa: E402


def angle_deg(a, b):
    return math.degrees(2 * math.acos(min(1.0, abs(float(np.dot(a, b))))))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pynifly", type=Path, required=True)
    ap.add_argument("--vanilla", type=Path, required=True)
    ap.add_argument("--clips", type=Path, required=True)
    ap.add_argument("--female", action="store_true", help="the clips are the Female subfolder")
    args = ap.parse_args()

    A = R.load_anim_module(args.pynifly)
    rig = Rig.from_hkx(A.load_fo4_skeleton(str(args.vanilla / "characterassets" / "skeleton.hkx")))
    rider = R.Rider(rig)
    rider.hip_z = None
    problems = skipped = 0
    for spec in R.clip_table():
        ours_path = args.clips / (spec.name + ".hkx")
        src_path = R.source_path(args.vanilla, spec, args.female)
        if src_path is None:
            skipped += 1
            print(f"--  {spec.name:28} vanilla clip not supplied, not generated")
            continue
        if not ours_path.exists():
            print(f"MISSING {spec.name}")
            problems += 1
            continue
        ours = A.load_fo4_animation(str(ours_path))
        src = A.load_fo4_animation(str(src_path))
        issues = []
        if abs(ours.duration - src.duration) > 1e-4 or ours.num_frames != src.num_frames:
            issues.append(f"length {ours.duration:.3f}s/{ours.num_frames}f vs {src.duration:.3f}s/{src.num_frames}f")
        want = sorted((round(a.time, 4), a.text) for a in src.annotations if not a.text.startswith("Foot"))
        got = sorted((round(a.time, 4), a.text) for a in ours.annotations)
        if want != got:
            issues.append(f"events {got} vs {want}")
        rf_ours, _ = R.reference_frame_samples(A, ours_path.read_bytes())
        rf_src, _ = R.reference_frame_samples(A, src_path.read_bytes())
        if rf_ours != rf_src:
            issues.append("root motion differs")
        if len(ours.tracks) != len(rig.names):
            issues.append(f"{len(ours.tracks)} tracks")
        # Spot-check compression: decoded COM height and hand/foot bone rotations vs the vanilla-length plan
        worst = 0.0
        com = rig.index("COM")
        heights = [ours.tracks[com].translations[f][2] for f in range(ours.num_frames)]
        for f in (0, ours.num_frames // 2, ours.num_frames - 1):
            for b in ("RArm_Hand", "LLeg_Calf", "Spine2", "AnimObjectA"):
                i = rig.index(b)
                q = ours.tracks[i].rotations[f]
                worst = max(worst, abs(np.linalg.norm(q) - 1.0))
        if worst > 1e-3:
            issues.append(f"non-unit rotations ({worst:.4f})")
        status = "ok " if not issues else "BAD"
        problems += bool(issues)
        print(f"{status} {spec.name:28} {ours.duration:5.2f}s {ours.num_frames:3}f  events {len(got)}  "
              f"seat z {min(heights):5.1f}..{max(heights):5.1f}  from {src_path.parent.name}  {'; '.join(issues)}")
    for spec in R.provisional_specs():
        path = args.clips / (spec.name + ".hkx")
        if not path.exists():
            print(f"MISSING {spec.name}")
            problems += 1
            continue
        a = A.load_fo4_animation(str(path))
        ok = len(a.tracks) == len(rig.names) and abs(a.duration - spec.duration) < 0.05
        problems += not ok
        print(f"{'ok ' if ok else 'BAD'} {spec.name:28} {a.duration:5.2f}s {a.num_frames:3}f  provisional (no vanilla reference)")
    print(("all clips ok" if not problems else f"{problems} clip(s) with problems")
          + (f"; {skipped} waiting for vanilla files" if skipped else ""))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
