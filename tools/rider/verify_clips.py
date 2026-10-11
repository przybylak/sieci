#!/usr/bin/env python3
"""Checks generated riding clips against the vanilla clips they replace.

For every clip: same length and frame count as the vanilla clip it replaces (in
the player's folder search order), the same control events at the same times
(footstep sounds excluded), identical root motion (the ridden U-turns: same total
turn, distance and length instead), all 95 bones present, unit rotations, and an
AnimTextData record that matches the clip. Clips that are only built from a vanilla
clip (jumping and landing) are listed as not built when it wasn't extracted.

  python verify_clips.py --pynifly <io_scene_nifly> --vanilla <...>/meshes/actors/character --clips <CMB_Rider folder>
"""

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import riding_anims as R  # noqa: E402
from rigmath import Rig  # noqa: E402


def angle_deg(a, b):
    return math.degrees(2 * math.acos(min(1.0, abs(float(np.dot(a, b))))))


def same_turn(ours, vanilla):
    """A reshaped path keeps vanilla's sample count, final heading and distance covered."""
    def length(s):
        return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(s, s[1:]))
    return (len(ours) == len(vanilla)
            and abs(ours[-1][3] - vanilla[-1][3]) < 1e-3
            and abs(length(ours) - length(vanilla)) < 0.01 * length(vanilla) + 0.5)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pynifly", type=Path, required=True)
    ap.add_argument("--vanilla", type=Path, required=True)
    ap.add_argument("--clips", type=Path, required=True)
    ap.add_argument("--female", action="store_true", help="the clips are the Female subfolder")
    args = ap.parse_args()

    A = R.load_anim_module(args.pynifly)
    rig = Rig.from_hkx(A.load_fo4_skeleton(str(args.vanilla / "characterassets" / "skeleton.hkx")))
    problems = provisional = unbuilt = 0
    records = json.loads((args.clips / R.CLIP_DATA_FILE).read_text())
    for spec in R.clip_table():
        ours_path = args.clips / (spec.name + ".hkx")
        src_path = R.source_path(args.vanilla, spec, args.female, A)
        if not ours_path.exists():
            if src_path is None and spec.duration <= 0:
                print(f"--  {spec.name:28} not built: its vanilla clip wasn't extracted")
                unbuilt += 1
                continue
            print(f"MISSING {spec.name}")
            problems += 1
            continue
        ours = A.load_fo4_animation(str(ours_path))
        issues = []
        rec = records.get(spec.name)
        if rec is None:
            issues.append("no AnimTextData record")
        else:
            if abs(rec["duration"] - ours.duration) > 1e-4:
                issues.append("record length differs")
            if sorted((round(t, 3), n) for t, n in rec["events"]) != sorted((round(a.time, 3), a.text) for a in ours.annotations):
                issues.append("record events differ")
        if len(ours.tracks) != len(rig.names):
            issues.append(f"{len(ours.tracks)} tracks")
        if src_path is None:
            provisional += 1
            if abs(ours.duration - spec.duration) > 0.05:
                issues.append("provisional length")
            status = "ok " if not issues else "BAD"
            problems += bool(issues)
            print(f"{status} {spec.name:28} {ours.duration:5.2f}s {ours.num_frames:3}f  provisional (no vanilla clip)  {'; '.join(issues)}")
            continue
        src = A.load_fo4_animation(str(src_path))
        if abs(ours.duration - src.duration) > 1e-4 or ours.num_frames != src.num_frames:
            issues.append(f"length {ours.duration:.3f}s/{ours.num_frames}f vs {src.duration:.3f}s/{src.num_frames}f")
        want = sorted((round(a.time, 4), a.text) for a in src.annotations if not a.text.startswith("Foot"))
        got = sorted((round(a.time, 4), a.text) for a in ours.annotations)
        if want != got:
            issues.append(f"events {got} vs {want}")
        rf_ours, _ = R.reference_frame_samples(A, ours_path.read_bytes())
        rf_src, _ = R.reference_frame_samples(A, src_path.read_bytes())
        if spec.root_motion:
            if not same_turn(rf_ours, rf_src):
                issues.append("U-turn doesn't match vanilla's turn, distance or length")
        elif rf_ours != rf_src:
            issues.append("root motion differs")
        worst = 0.0
        com = rig.index("COM")
        heights = [ours.tracks[com].translations[f][2] for f in range(ours.num_frames)]
        for f in (0, ours.num_frames // 2, ours.num_frames - 1):
            for b in ("RArm_Hand", "LLeg_Calf", "Spine2", "AnimObjectA"):
                q = ours.tracks[rig.index(b)].rotations[f]
                worst = max(worst, abs(np.linalg.norm(q) - 1.0))
        if worst > 1e-3:
            issues.append(f"non-unit rotations ({worst:.4f})")
        status = "ok " if not issues else "BAD"
        problems += bool(issues)
        source = src_path.relative_to(args.vanilla / "animations").with_suffix("").as_posix()
        print(f"{status} {spec.name:28} {ours.duration:5.2f}s {ours.num_frames:3}f  events {len(got)}  "
              f"seat z {min(heights):5.1f}..{max(heights):5.1f}  from {source}  {'; '.join(issues)}")
    print(("all clips ok" if not problems else f"{problems} clip(s) with problems")
          + (f"; {provisional} provisional" if provisional else "")
          + (f"; {unbuilt} not built (extract their vanilla clips)" if unbuilt else ""))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
