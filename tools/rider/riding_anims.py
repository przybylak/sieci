#!/usr/bin/env python3
"""Generates the seated riding animations (Fallout 4 .hkx) for Commonwealth Motorbike.

Every clip the game plays for holstered movement (walk/jog/run/sprint, leans,
turns in place, start/stop/reverse transitions) gets a riding version with the
same file name, length, root motion and control events as the vanilla clip it
replaces. Only the body pose changes, so the game's speed and turning logic is
untouched. Footstep sound events are dropped.

The pose is fitted to the bike model (see CONTACT POINTS): hips on the seat,
hands on the grips, feet on the forward pegs; at a standstill the left foot is
put down and the bike tips onto it. The worn bike is skinned to AnimObjectA, so
the clips also lean the bike, together with the rider, in turns.

Standing-still clips (idle, idle flavours, dialogue) are seated too. Until their
vanilla files are supplied they are "provisional": in place, guessed lengths.

Female characters look in a Female subfolder first, so --female-body also writes
CMB_Rider/Female, timed from the vanilla female clips where those exist.

Needs PyNifly's io_scene_nifly folder (its anim_fo4.py writes the clips) and the
vanilla clips/skeleton extracted from Fallout4 - Animations.ba2 / Meshes.ba2:

  python riding_anims.py --pynifly <io_scene_nifly> --vanilla <...>/meshes/actors/character \
      --body <...>/malebody.nif --female-body <...>/femalebody.nif \
      --out <Data>/Meshes/Actors/Character/Animations/MT/CMB_Rider
"""

import argparse
import importlib.util
import math
import struct
import sys
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rigmath import (Pose, Rig, q_axis_angle, q_mul,  # noqa: E402
                     rot_x, rot_y, rot_z, two_bone_ik)

# --------------------------------------------------------------------------
# CONTACT POINTS on the worn bike (build_bike_meshes.py output space:
# +Y forward, +X to the rider's right, Z up, seat dip over the origin).
# Measured from the vanilla motorcycle model.
# --------------------------------------------------------------------------
SEAT_TOP_Z = 65.6          # top of the seat dip at y = 0
GRIP_R = np.array([31.5, 22.4, 89.4])
GRIP_L = np.array([-31.5, 22.4, 89.4])
PEG_R = np.array([20.0, 37.0, 26.0])   # top of the forward foot pegs
PEG_L = np.array([-20.0, 37.0, 26.0])
GROUND_FOOT_L = np.array([-30.0, 6.0, 0.0])  # where the left foot goes down at a stop

FINGERS = ["Finger21", "Finger22", "Finger23", "Finger31", "Finger32", "Finger33",
           "Finger41", "Finger42", "Finger43", "Finger51", "Finger52", "Finger53"]
THUMB = ["Finger11", "Finger12", "Finger13"]


@dataclass(frozen=True)
class RideParams:
    lean: float = 14.0         # torso forward lean, degrees
    roll: float = 0.0          # bike + rider roll; negative = to the left
    foot_down: float = 0.0     # 0 = both feet on pegs, 1 = left foot on the ground
    bounce: float = 0.0        # vertical seat bounce, units
    head_turn: float = 0.0     # head yaw, degrees (+ = right)


# Speed-dependent settings (lean, bounce amplitude, roll for the Lean* clips)
SPEEDS = {
    "walk":   dict(lean=14.0, bounce=0.35, lean_roll=8.0),
    "jog":    dict(lean=17.0, bounce=0.55, lean_roll=12.0),
    "run":    dict(lean=20.0, bounce=0.75, lean_roll=16.0),
    "sprint": dict(lean=24.0, bounce=0.85, lean_roll=18.0),
}
IDLE = RideParams(lean=7.0, roll=-9.0, foot_down=1.0)


# --------------------------------------------------------------------------
# Posing
# --------------------------------------------------------------------------

def frame_from_axes(x, y_hint):
    """Rotation whose X axis is `x` and whose Y axis is as close to `y_hint` as possible."""
    x = np.asarray(x, float) / np.linalg.norm(x)
    y = np.asarray(y_hint, float) - np.dot(y_hint, x) * x
    y /= np.linalg.norm(y)
    return np.column_stack([x, y, np.cross(x, y)])


class Rider:
    def __init__(self, rig: Rig):
        self.rig = rig
        self.ref_globals = rig.fk()
        self.hip_z = None

    def seat(self, mesh_min_z_fn=None):
        """Find the COM height that puts the buttocks on the seat (uses the body mesh if given)."""
        self.hip_z = 74.0
        if mesh_min_z_fn is None:
            return
        for _ in range(3):
            low = mesh_min_z_fn(self.pose(RideParams(lean=14.0)))
            self.hip_z += (SEAT_TOP_Z + 0.3) - low

    def pose(self, p: RideParams) -> Pose:
        rig = self.rig
        pose = Pose(rig)
        com = rig.index("COM")
        pose.t[com] = [0.0, 0.0, self.hip_z + p.bounce]

        # Pelvis rolled back as when sitting; spine leans forward over three joints.
        pose.rotate_global("Pelvis", rot_x(12.0))
        for bone in ("Spine1", "Spine2", "Chest"):
            pose.rotate_global(bone, rot_x(-p.lean / 3.0))
        # Shoulders forward toward the bars.
        pose.rotate_global("RArm_Collarbone", rot_z(9.0))
        pose.rotate_global("LArm_Collarbone", rot_z(-9.0))

        # Legs: right foot on its peg, left foot on its peg or on the ground.
        self._leg(pose, "R", PEG_R + [0, -6, 8], toe=PEG_R + [0, 6, 1], pole=[0.45, 1, 0.3])
        # The ground spot is fixed in the world, but the rider is posed before the roll
        # is applied, so express it in the un-rolled frame.
        unroll = rot_y(-p.roll)
        peg_ankle = PEG_L + [0, -6, 8]
        ground_ankle = unroll @ (GROUND_FOOT_L + [0, -4, 8.5])
        ankle = (1 - p.foot_down) * peg_ankle + p.foot_down * ground_ankle
        toe = (1 - p.foot_down) * (PEG_L + [0, 6, 1]) + p.foot_down * (unroll @ (GROUND_FOOT_L + [-2, 9, 1]))
        self._leg(pose, "L", ankle, toe=toe, pole=[-0.45 - 0.4 * p.foot_down, 1, 0.3])

        # Arms and hands on the grips.
        self._arm(pose, "R", GRIP_R, pole=[1.0, -0.6, -0.7])
        self._arm(pose, "L", GRIP_L, pole=[-1.0, -0.6, -0.7])

        # Head level and looking ahead (slight downward look), optional yaw.
        g = pose.globals()
        neck = g[rig.index("Neck")][:3, :3]
        pose.set_global_rot("Neck", rot_x(p.lean * 0.45) @ neck, g)
        g = pose.globals()
        head_ref = self.ref_globals[rig.index("Head")][:3, :3]
        pose.set_global_rot("Head", rot_z(-p.head_turn) @ rot_x(-6.0) @ head_ref, g)

        # Roll: the whole rider (via COM) and the bike (AnimObjectA) turn together
        # around the forward axis through the ground contact line. Head counter-rolls a bit.
        if p.roll:
            r = rot_y(p.roll)
            pose.t[com] = r @ pose.t[com]
            pose.q[com] = q_mul(q_axis_angle([0, 1, 0], p.roll), pose.q[com])
            g = pose.globals()
            head = g[rig.index("Head")][:3, :3]
            pose.set_global_rot("Head", rot_y(-0.4 * p.roll) @ head, g)
        pose.q[rig.index("AnimObjectA")] = q_axis_angle([0, 1, 0], p.roll)
        return pose

    def _leg(self, pose, side, ankle, toe, pole):
        two_bone_ik(pose, f"{side}Leg_Thigh", f"{side}Leg_Calf", f"{side}Leg_Foot", ankle, pole)
        pose.aim(f"{side}Leg_Foot", toe)

    def _arm(self, pose, side, grip, pole):
        rig = self.rig
        sign = 1.0 if side == "R" else -1.0
        # Hand frame: fingers forward, down and a little outward; palm (-Y) facing down onto the bar.
        fingers = np.array([0.18 * sign, 0.75, -0.62])
        hand_r = frame_from_axes(fingers, [0.0, 0.55, 0.85])
        wrist = grip - hand_r[:, 0] * 6.0 + hand_r[:, 1] * 2.5
        two_bone_ik(pose, f"{side}Arm_UpperArm", f"{side}Arm_ForeArm1", f"{side}Arm_Hand", wrist, pole)
        pose.set_global_rot(f"{side}Arm_Hand", hand_r)
        # Curl fingers round the grip (local Z is the knuckle axis; negative curls toward the palm).
        for f in FINGERS:
            i = rig.index(f"{side}Arm_{f}")
            pose.q[i] = q_mul(rig.ref_q[i], q_axis_angle([0, 0, 1], -55.0))
        for f, a in zip(THUMB, (-15.0, -25.0, -25.0)):
            i = rig.index(f"{side}Arm_{f}")
            pose.q[i] = q_mul(rig.ref_q[i], q_axis_angle([0, 0, 1], a))


# --------------------------------------------------------------------------
# Clip table: which vanilla clip each riding clip mirrors, and how it moves
# --------------------------------------------------------------------------

def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def riding(speed, roll=0.0):
    s = SPEEDS[speed]

    def at(t):  # t = 0..1 through the clip; two bounces per cycle
        return RideParams(lean=s["lean"], roll=roll, bounce=s["bounce"] * math.sin(4 * math.pi * t))
    return at


def turning(speed, direction, peak):
    """Riding while swinging round (180s): lean into the turn, most in the middle."""
    s = SPEEDS[speed]
    sign = -1.0 if direction == "l" else 1.0

    def at(t):
        return RideParams(lean=s["lean"], roll=sign * peak * math.sin(math.pi * t),
                          bounce=s["bounce"] * math.sin(4 * math.pi * t))
    return at


def starting(speed, direction=None, peak=0.0):
    """Pull away: lift the foot, straighten the bike, lean into a turning start."""
    s = SPEEDS[speed]
    sign = -1.0 if direction == "l" else 1.0

    def at(t):
        k = ease(t / 0.6)
        turn = sign * peak * math.sin(math.pi * min(t / 0.8, 1.0)) if direction else 0.0
        return RideParams(lean=IDLE.lean + (s["lean"] - IDLE.lean) * k,
                          roll=IDLE.roll * (1 - k) + turn,
                          foot_down=1.0 - k)
    return at


def stopping(speed, direction=None, peak=0.0):
    """Slow down, put the left foot down; a turning stop leans into the turn first."""
    s = SPEEDS[speed]
    sign = -1.0 if direction == "l" else 1.0

    def at(t):
        k = ease((t - 0.35) / 0.5)
        turn = sign * peak * math.sin(math.pi * min(t / 0.6, 1.0)) if direction else 0.0
        return RideParams(lean=s["lean"] + (IDLE.lean - s["lean"]) * k, roll=IDLE.roll * k + turn, foot_down=k)
    return at


def standing(_t):
    return IDLE


@dataclass
class ClipSpec:
    name: str              # output file name (no extension)
    source: str            # vanilla clip to mirror (relative to the animations folder), or None
    motion: object         # function t -> RideParams
    duration: float = 0.0  # only for clips without a vanilla source (provisional)


def seated_gesture(kind, seed):
    """Standing-still clips (idle, idle flavours, dialogue): seated, hands on the bars,
    with a little head movement so it doesn't look frozen."""
    def at(t):
        breath = 0.25 * math.sin(2 * math.pi * t)
        if kind == "nod":
            turn, look = 0.0, 6.0 * math.sin(4 * math.pi * t) ** 2
        elif kind == "shake":
            turn, look = 14.0 * math.sin(6 * math.pi * t) * math.sin(math.pi * t), 0.0
        elif kind == "look":
            side = 1 if seed % 2 else -1
            turn, look = side * 35.0 * math.sin(math.pi * t) ** 2, 0.0
        elif kind == "talk":
            turn, look = 6.0 * math.sin(2 * math.pi * (t + seed * 0.13)), 2.0 * math.sin(6 * math.pi * t)
        else:  # still
            turn, look = 3.0 * math.sin(2 * math.pi * t), 0.0
        return replace(IDLE, bounce=breath, head_turn=turn, lean=IDLE.lean + look * 0.3)
    return at


def provisional_specs():
    """Clips the zip didn't include (no vanilla reference yet): standing idle, idle
    flavours and dialogue. Timings are guesses; regenerate with the vanilla files to match."""
    # Names are the player's own MT clips (mt\player): idle flavours 1-9, dialogue idles 1-6,
    # talk s/m/l 1-8. The female folder has fewer of each, so this covers both.
    specs = [ClipSpec("posea_idle1", None, seated_gesture("still", 0), 4.0)]
    specs += [ClipSpec(f"posea_idleflavor{i}", None, seated_gesture("look", i), 6.0) for i in range(1, 10)]
    specs += [ClipSpec(f"posea_idledialogue{i}", None, seated_gesture("still", i), 5.0) for i in range(1, 7)]
    specs += [ClipSpec(f"posea_listen{i}", None, seated_gesture("still", i), 4.0) for i in range(1, 3)]
    for size, length in (("s", 2.5), ("m", 4.0), ("l", 6.0)):
        specs += [ClipSpec(f"posea_talk_{size}{i}", None, seated_gesture("talk", i), length) for i in range(1, 9)]
    specs += [ClipSpec("posea_agree1", None, seated_gesture("nod", 0), 1.8),
              ClipSpec("posea_disagree1", None, seated_gesture("shake", 0), 1.8)]
    return specs


def clip_table():
    P, N = "mt/player/", "mt/neutral/"
    specs = [
        ClipSpec("walkforward", P + "walkforward", riding("walk")),
        ClipSpec("walkleanleft", P + "walkleanleft", riding("walk", -SPEEDS["walk"]["lean_roll"])),
        ClipSpec("walkleanright", P + "walkleanright", riding("walk", SPEEDS["walk"]["lean_roll"])),
        ClipSpec("jogforward", N + "jogforward", riding("jog")),
        ClipSpec("jogleanleft", N + "jogforward", riding("jog", -SPEEDS["jog"]["lean_roll"])),
        ClipSpec("jogleanright", N + "jogforward", riding("jog", SPEEDS["jog"]["lean_roll"])),
        ClipSpec("runforward", N + "runforward", riding("run")),
        ClipSpec("runleanleft", P + "runleanleft", riding("run", -SPEEDS["run"]["lean_roll"])),
        ClipSpec("runleanright", P + "runleanright", riding("run", SPEEDS["run"]["lean_roll"])),
        ClipSpec("sprintforward", N + "sprintforward", riding("sprint")),
        ClipSpec("sprintleanleft", N + "sprintforward", riding("sprint", -SPEEDS["sprint"]["lean_roll"])),
        ClipSpec("sprintleanright", N + "sprintforward", riding("sprint", SPEEDS["sprint"]["lean_roll"])),
        ClipSpec("walk_to_walk_l180", P + "walk_to_walk_l180", turning("walk", "l", 12.0)),
        ClipSpec("walk_to_walk_r180", P + "walk_to_walk_r180", turning("walk", "r", 12.0)),
        ClipSpec("run_to_run_l180", P + "run_to_run_l180", turning("run", "l", 18.0)),
        ClipSpec("run_to_run_r180", P + "run_to_run_r180", turning("run", "r", 18.0)),
        ClipSpec("walk_to_stand", N + "walk_to_stand", stopping("walk")),
        ClipSpec("walk_to_stand_r", N + "walk_to_stand_r", stopping("walk")),
        ClipSpec("run_to_stand", N + "run_to_stand", stopping("run")),
    ]
    for speed in ("walk", "run"):
        specs.append(ClipSpec(f"stand_to_{speed}", P + f"stand_to_{speed}", starting(speed)))
        for d in ("l", "r"):
            for angle, peak in (("30", 5.0), ("90", 9.0), ("180", 12.0)):
                specs.append(ClipSpec(f"stand_to_{speed}_{d}{angle}", P + f"stand_to_{speed}_{d}{angle}",
                                      starting(speed, d, peak)))
    for d in ("l", "r"):
        for angle, peak in (("45", 5.0), ("90", 8.0), ("180", 10.0)):
            specs.append(ClipSpec(f"walk_to_stand_{d}{angle}", N + f"walk_to_stand_{d}{angle}",
                                  stopping("walk", d, peak)))
    for d in ("left", "right"):
        for angle in ("45", "90", "180"):
            for fast in ("", "_fast"):
                name = f"turninplace{d}{angle}{fast}"
                specs.append(ClipSpec(name, N + name, standing))
    return specs


# --------------------------------------------------------------------------
# Writing clips
# --------------------------------------------------------------------------

def load_anim_module(pynifly: Path):
    spec = importlib.util.spec_from_file_location("anim_fo4", pynifly / "hkx" / "anim_fo4.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def reference_frame_samples(A, data: bytes):
    """Root-motion samples (x, y, z, yaw) of an animation hkx, and where they are stored."""
    secs = A._parse_hkx_sections(data)
    sec = secs["__data__"]
    base = sec["offset"]
    fixups = A._parse_local_fixups(data, sec)
    objects = A._parse_virtual_fixups(data, sec, secs["__classnames__"]["offset"])
    obj = next(o for o, cls in objects if cls == "hkaDefaultAnimatedReferenceFrame")
    count = struct.unpack_from("<I", data, base + obj + 0x48 + 8)[0]
    start = base + fixups[obj + 0x48]
    samples = [struct.unpack_from("<4f", data, start + 16 * i) for i in range(count)]
    return samples, start


def source_path(vanilla_root: Path, spec: ClipSpec, female: bool):
    """The vanilla clip whose timing, events and root motion a riding clip copies.

    Female characters look in a Female subfolder first, so the female set follows
    mt/player/female or mt/neutral/female where those exist. None if not supplied.
    """
    if spec.source is None:
        return None
    anims = vanilla_root / "animations"
    folder, name = spec.source.rsplit("/", 1)
    candidates = [anims / (spec.source + ".hkx")]
    if female:
        candidates[:0] = [anims / "mt/player/female" / (name + ".hkx"), anims / "mt/neutral/female" / (name + ".hkx")]
    return next((c for c in candidates if c.exists()), None)


def write_clip(A, rider: Rider, spec: ClipSpec, vanilla_root: Path, out_dir: Path, female=False):
    rig = rider.rig
    if spec.source is None:
        return write_provisional(A, rider, spec, out_dir)
    src_path = source_path(vanilla_root, spec, female)
    if src_path is None:
        return None
    src = A.load_fo4_animation(str(src_path))
    n = src.num_frames

    poses = [rider.pose(spec.motion(i / max(1, n - 1))) for i in range(n)]
    tracks = []
    for b in range(len(rig.names)):
        tracks.append(A.TrackData(
            translations=[list(p.t[b]) for p in poses],
            rotations=[list(p.q[b]) for p in poses],
            scales=[[1.0, 1.0, 1.0] for _ in poses],
        ))

    anim = A.AnimationData(
        duration=src.duration,
        num_frames=n,
        num_tracks=len(tracks),
        frame_duration=src.frame_duration,
        bone_names=list(rig.names),
        tracks=tracks,
        annotations=[a for a in src.annotations if not a.text.startswith("Foot")],
        track_to_bone_indices=list(range(len(rig.names))),
        original_skeleton_name=src.original_skeleton_name or "Root",
    )
    out = out_dir / (spec.name + ".hkx")
    A.write_fo4_animation(str(out), anim)

    # Copy the vanilla root motion so the game's speed and turning maths stay identical.
    samples, _ = reference_frame_samples(A, src_path.read_bytes())
    data = bytearray(out.read_bytes())
    ours, start = reference_frame_samples(A, bytes(data))
    if len(ours) != len(samples):
        raise ValueError(f"{spec.name}: {len(ours)} root-motion samples vs {len(samples)} in vanilla")
    for i, s in enumerate(samples):
        struct.pack_into("<4f", data, start + 16 * i, *s)
    out.write_bytes(bytes(data))
    return out, poses


def write_provisional(A, rider: Rider, spec: ClipSpec, out_dir: Path):
    """In-place clip without a vanilla reference: no events, no root motion."""
    rig = rider.rig
    n = int(round(spec.duration * 30)) + 1
    poses = [rider.pose(spec.motion(i / (n - 1))) for i in range(n)]
    tracks = [A.TrackData(translations=[list(p.t[b]) for p in poses],
                          rotations=[list(p.q[b]) for p in poses],
                          scales=[[1.0, 1.0, 1.0] for _ in poses]) for b in range(len(rig.names))]
    anim = A.AnimationData(duration=(n - 1) / 30.0, num_frames=n, num_tracks=len(tracks),
                           frame_duration=1.0 / 30.0, bone_names=list(rig.names), tracks=tracks,
                           annotations=[], track_to_bone_indices=list(range(len(rig.names))),
                           original_skeleton_name="Root")
    out = out_dir / (spec.name + ".hkx")
    A.write_fo4_animation(str(out), anim)
    return out, poses


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pynifly", type=Path, required=True, help="PyNifly's io_scene_nifly folder")
    ap.add_argument("--vanilla", type=Path, required=True,
                    help="extracted <...>/meshes/actors/character folder (skeleton + animations/mt)")
    ap.add_argument("--out", type=Path, required=True, help="output folder for the riding clips")
    ap.add_argument("--body", type=Path, help="body nif to seat the rider precisely (e.g. malebody.nif)")
    ap.add_argument("--female-body", type=Path,
                    help="female body nif (e.g. CBBE femalebody.nif); also writes the Female subfolder")
    ap.add_argument("--only", nargs="*", help="only these clip names")
    args = ap.parse_args()

    sys.path.insert(0, str(args.pynifly))
    A = load_anim_module(args.pynifly)
    rig = Rig.from_hkx(A.load_fo4_skeleton(str(args.vanilla / "characterassets" / "skeleton.hkx")))

    sets = [("male", args.body, args.out, False)]
    if args.female_body:
        sets.append(("female", args.female_body, args.out / "Female", True))
    missing = set()
    for label, body_nif, out_dir, female in sets:
        rider = Rider(rig)
        rider.seat(seat_probe(rig, body_nif, args.vanilla) if body_nif else None)
        print(f"{label}: seat height COM z = {rider.hip_z:.1f}")
        out_dir.mkdir(parents=True, exist_ok=True)
        written = 0
        for spec in clip_table() + provisional_specs():
            if args.only and spec.name not in args.only:
                continue
            if write_clip(A, rider, spec, args.vanilla, out_dir, female) is None:
                folder, name = spec.source.rsplit("/", 1)
                missing.add(f"{folder}/female/{name}" if female else spec.source)
                continue
            written += 1
        print(f"{label}: wrote {written} clips to {out_dir}")
    if missing:
        print("not generated, vanilla clip not supplied (extract it and run again):")
        for m in sorted(missing):
            print(f"  meshes/actors/character/animations/{m}.hkx")
    return 0


def seat_probe(rig, body_nif: Path, vanilla_root: Path):
    """Function pose -> lowest point of the buttocks over the seat, for Rider.seat()."""
    from pyn.pynifly import NifFile
    from rigmath import SkinnedMesh, nif_followers
    body = SkinnedMesh(NifFile(str(body_nif)).shapes[0], rig,
                       nif_followers(NifFile(str(vanilla_root / "characterassets" / "skeleton.nif")), rig))

    def min_z(pose):
        v = body.posed(pose.globals())
        sel = (np.abs(v[:, 0]) < 9) & (v[:, 1] > -14) & (v[:, 1] < 4) & (v[:, 2] > 50)
        return float(v[sel, 2].min())
    return min_z


if __name__ == "__main__":
    sys.exit(main())
