#!/usr/bin/env python3
"""Builds the EXPERIMENTAL seated "rider pose" animation folder.

Idea: while riding, the player's animation archetype is switched to
CMB_AnimArchetypeRider. A subgraph entry on HumanRace points that archetype at
Meshes\\Actors\\Character\\Animations\\CMB_Rider\\ first. Any clip found there
replaces the vanilla clip with the same relative file name. If every walk/run/
turn/idle clip is replaced by one seated loop, the player just sits while the
SpeedMult boost moves them - no running legs.

This script only copies files. It needs:
  --vanilla-dir  The folder the player's locomotion clips come from, extracted
                 from "Fallout4 - Animations.ba2" (Archive2 / BAE). It's the
                 folder listed in the Paths of HumanRace's third-person MT
                 subgraph entry for AnimArchetypePlayer (see docs/ASSETS.md).
  --pose         One .hkx clip with a seated pose, e.g. a vanilla bar-stool or
                 chair sitting loop.
  --out          Where to write the result, normally
                 <Data>\\Meshes\\Actors\\Character\\Animations\\CMB_Rider

Run with --dry-run first and read the list: only locomotion clips should be in it.
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

# Clip names that drive moving and standing around. Anything matching these is
# replaced by the seated pose; everything else (attacks, reloads, equips,
# furniture, reactions) is left alone.
LOCOMOTION = re.compile(
    r"(walk|run|jog|sprint|turn|idle|strafe|move|locomotion|start|stop|pivot)",
    re.IGNORECASE,
)
EXCLUDE = re.compile(
    r"(attack|reload|equip|unequip|draw|sheathe|holster|fire|bash|throw|grenade|"
    r"jump|land|fall|death|die|hit|stagger|furniture|chair|sit|sleep|pipboy|"
    r"pickup|ragdoll|swim|sneak|crouch|power ?armor|vats)",
    re.IGNORECASE,
)


def find_clips(vanilla_dir: Path) -> list[Path]:
    clips = []
    for path in sorted(vanilla_dir.rglob("*")):
        if path.suffix.lower() != ".hkx" or not path.is_file():
            continue
        name = path.stem
        if LOCOMOTION.search(name) and not EXCLUDE.search(name):
            clips.append(path.relative_to(vanilla_dir))
    return clips


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--vanilla-dir", type=Path, required=True)
    parser.add_argument("--pose", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true", help="only list what would be written")
    args = parser.parse_args()

    if not args.vanilla_dir.is_dir():
        print(f"--vanilla-dir is not a folder: {args.vanilla_dir}", file=sys.stderr)
        return 1
    if not args.pose.is_file() or args.pose.suffix.lower() != ".hkx":
        print(f"--pose must be an .hkx file: {args.pose}", file=sys.stderr)
        return 1

    clips = find_clips(args.vanilla_dir)
    if not clips:
        print("No locomotion clips found - check --vanilla-dir.", file=sys.stderr)
        return 1

    for rel in clips:
        target = args.out / rel
        print(("would write " if args.dry_run else "write ") + str(target))
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(args.pose, target)

    manifest = "\n".join(str(rel) for rel in clips) + "\n"
    if not args.dry_run:
        (args.out / "CMB_RiderPose_manifest.txt").write_text(manifest)
    print(f"{len(clips)} clips {'would be ' if args.dry_run else ''}replaced with {args.pose.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
