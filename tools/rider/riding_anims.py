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

Standing-still clips (idle, idle flavours, dialogue) are seated too. A clip with
no vanilla file at all is "provisional": in place, with a guessed length.

The vanilla clip each one copies is the one the player would play: the clip name
looked up in the player's folders in the game's order (SEARCH_ORDER), falling back
to a stand-in if that file wasn't extracted. --female-body also writes
CMB_Rider/Female from the female folders. Next to the clips goes CMB_RiderClips.json
with their root motion and events for the AnimTextData (make_rider_plugin.py).

Needs PyNifly's io_scene_nifly folder (its anim_fo4.py writes the clips) and the
vanilla clips/skeleton extracted from Fallout4 - Animations.ba2 / Meshes.ba2:

  python riding_anims.py --pynifly <io_scene_nifly> --vanilla <...>/meshes/actors/character \
      --body <...>/malebody.nif --female-body <...>/femalebody.nif \
      --out <Data>/Meshes/Actors/Character/Animations/MT/CMB_Rider \
      [--game-files vanilla_character_animation_list.txt] [--fit <Data>/Meshes/CMB/CMB_BikeFit.json]

--fit takes the contact points of another bike model (harley_meshes.py writes the file
for its model) in place of the vanilla motorcycle's below.
"""

import argparse
import importlib.util
import json
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
FIT_NAME = "vanilla motorcycle"
# The bars turn (a bike-fit file says about what axis, and how far): the grips move with
# them, so the hands do too. None for the vanilla bike, whose bars don't move.
STEER_POINT = None
STEER_AXIS = None
BAR_ANGLE = 0.0


def apply_fit(path: Path):
    """Take the contact points from a bike-fit file (harley_meshes.py writes one for its
    model): the same keys as the constants above, lower-case, in the worn bike's space."""
    global SEAT_TOP_Z, GRIP_R, GRIP_L, PEG_R, PEG_L, GROUND_FOOT_L, FIT_NAME, STEER_POINT, STEER_AXIS, BAR_ANGLE
    fit = json.loads(Path(path).read_text())
    SEAT_TOP_Z = float(fit["seat_top_z"])
    GRIP_R, GRIP_L = np.array(fit["grip_r"], float), np.array(fit["grip_l"], float)
    PEG_R, PEG_L = np.array(fit["peg_r"], float), np.array(fit["peg_l"], float)
    if "ground_foot_l" in fit:
        GROUND_FOOT_L = np.array(fit["ground_foot_l"], float)
    if "steer_axis" in fit and fit.get("bar_angle", 0.0) > 0:
        STEER_POINT = np.array(fit["steer_point"], float)
        STEER_AXIS = np.array(fit["steer_axis"], float)
        STEER_AXIS /= np.linalg.norm(STEER_AXIS)
        BAR_ANGLE = float(fit["bar_angle"])
    FIT_NAME = fit.get("model", str(path))
    return fit


def rot_about(axis, degrees):
    """Rotation about a unit axis (Rodrigues)."""
    a = math.radians(degrees)
    c, s = math.cos(a), math.sin(a)
    x, y, z = axis
    return np.array([[c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
                     [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
                     [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)]])


def grips(steer):
    """The grips with the bars turned `steer` degrees (positive to the left: the F4SE plugin
    turns the bar assembly the same way, about the same axis, when the rider turns)."""
    if STEER_AXIS is None or not steer:
        return GRIP_R, GRIP_L
    r = rot_about(STEER_AXIS, steer)
    return r @ (GRIP_R - STEER_POINT) + STEER_POINT, r @ (GRIP_L - STEER_POINT) + STEER_POINT


def steer_for(roll):
    """The bars' turn that goes with a lean: into the turn, the full angle from a few degrees
    of lean (the plugin's bars are at the full angle in any real turn)."""
    if roll == 0.0 or BAR_ANGLE == 0.0:
        return 0.0
    k = min(abs(roll) / 4.0, 1.0)
    return -math.copysign(BAR_ANGLE * k, roll)   # roll negative = leaning left = bars left (positive)

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
    steer: float = 0.0         # the bars' turn, degrees (+ = left); the hands follow


# Speed-dependent settings (lean, bounce amplitude, roll for the Lean* clips)
# Bounce moves COM, and the worn bike hangs off COM, so it's kept to a few millimetres:
# a hint of suspension rather than the rider bouncing on the seat.
SPEEDS = {
    "walk":   dict(lean=14.0, bounce=0.15, lean_roll=8.0),
    "jog":    dict(lean=17.0, bounce=0.2, lean_roll=12.0),
    "run":    dict(lean=20.0, bounce=0.3, lean_roll=16.0),
    "sprint": dict(lean=24.0, bounce=0.35, lean_roll=18.0),
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

        # Arms and hands on the grips (where the turned bars put them).
        grip_r, grip_l = grips(p.steer)
        self._arm(pose, "R", grip_r, pole=[1.0, -0.6, -0.7])
        self._arm(pose, "L", grip_l, pole=[-1.0, -0.6, -0.7])

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
        return RideParams(lean=s["lean"], roll=roll, bounce=s["bounce"] * math.sin(4 * math.pi * t), steer=steer_for(roll))
    return at


def turning(speed, direction, peak):
    """Riding while swinging round (180s): lean into the turn, most in the middle."""
    s = SPEEDS[speed]
    sign = -1.0 if direction == "l" else 1.0

    def at(t):
        roll = sign * peak * math.sin(math.pi * t)
        return RideParams(lean=s["lean"], roll=roll, bounce=s["bounce"] * math.sin(4 * math.pi * t), steer=steer_for(roll))
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
                          foot_down=1.0 - k, steer=steer_for(turn))
    return at


def stopping(speed, direction=None, peak=0.0):
    """Slow down, put the left foot down; a turning stop leans into the turn first."""
    s = SPEEDS[speed]
    sign = -1.0 if direction == "l" else 1.0

    def at(t):
        k = ease((t - 0.35) / 0.5)
        turn = sign * peak * math.sin(math.pi * min(t / 0.6, 1.0)) if direction else 0.0
        return RideParams(lean=s["lean"] + (IDLE.lean - s["lean"]) * k, roll=IDLE.roll * k + turn, foot_down=k,
                          steer=steer_for(turn))
    return at


def standing(_t):
    return IDLE


def takeoff(speed):
    """Leaving the ground: weight back a little, feet stay on the pegs."""
    s = SPEEDS[speed]

    def at(t):
        return RideParams(lean=s["lean"] - 8.0 * math.sin(math.pi * t))
    return at


def airborne(speed):
    s = SPEEDS[speed]

    def at(t):
        return RideParams(lean=s["lean"] - 4.0)
    return at


def landing(speed, hard=False):
    """Touchdown: absorb it with the upper body (COM stays put: the bike hangs off it)."""
    s = SPEEDS[speed]
    depth = 14.0 if hard else 8.0

    def at(t):
        return RideParams(lean=s["lean"] + depth * math.sin(math.pi * min(t / 0.45, 1.0)))
    return at


class UTurn:
    """The 180-degree reversals (walk_to_walk_l180 etc.) ridden as an arc. Vanilla's
    root motion brakes to a stop, spins round and sets off the other way, like a person
    turning round. This keeps going at the entry speed while the heading swings round,
    so the path is a U, leaning into it. The turn's direction comes from the vanilla
    clip's own yaw (MT\\Neutral's walk_to_walk_l180 actually turns right), and the
    heading is round by `startAllowRotation`, like vanilla's, so the game's steering
    takes over at the same moment."""

    def __init__(self, speed, peak):
        self.speed, self.peak = speed, peak

    def plan(self, vanilla, duration, events):
        """(vanilla root-motion samples, clip length, annotations) -> (samples, motion)."""
        n = len(vanilla)
        dt = duration / (n - 1)
        total = vanilla[-1][3]
        sign = 1.0 if total > 0 else -1.0                 # positive yaw turns left
        allow = [a.time for a in events if a.text.lower() == "startallowrotation"]
        share = min(max((allow[0] if allow else 0.75 * duration) / duration, 0.2), 0.9)
        # Vanilla's average pace (it brakes into the spin and speeds up out of it), so
        # the clip covers the same distance in the same time.
        speed = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(vanilla, vanilla[1:])) / duration

        def heading(u):
            return total * ease(u / share)
        out, x, y = [(0.0, 0.0, 0.0, 0.0)], 0.0, 0.0
        for i in range(1, n):
            h = heading((i - 0.5) / (n - 1))              # midpoint of the step
            x += -math.sin(h) * speed * dt
            y += math.cos(h) * speed * dt
            out.append((x, y, 0.0, heading(i / (n - 1))))
        s = SPEEDS[self.speed]
        roll = -sign * self.peak                          # lean into it: left turn, roll left

        def motion(t):
            r = roll * math.sin(math.pi * min(t / share, 1.0))
            return RideParams(lean=s["lean"], roll=r, bounce=s["bounce"] * math.sin(4 * math.pi * t), steer=steer_for(r))
        return out, motion


# Root motion and events of every clip, for the AnimTextData that make_rider_plugin.py
# writes (the game reads those from AnimTextData, not from the .hkx).
CLIP_DATA_FILE = "CMB_RiderClips.json"
SEAT_FILE = "CMB_RiderSeat.json"      # where COM sits when seated, for build_bike_meshes.py

# Folders the player's holstered (MT) subgraph entries search, in order: what
# vanilla's AnimTextData resolves every clip name to (checked for all 193 male and
# 191 female names). A riding clip copies the timing of the clip it replaces.
SEARCH_ORDER = {
    False: ("mt/player", "mt/confident", "mt/neutral"),
    True: ("mt/player/female", "mt/confident/female", "mt/neutral/female", "mt/player", "mt/confident", "mt/neutral"),
}


@dataclass
class ClipSpec:
    name: str                 # clip name = output file name (no extension)
    motion: object            # function t -> RideParams
    stand_ins: tuple = ()     # clips whose timing can stand in if this one wasn't extracted
    duration: float = 0.0     # length if no vanilla clip is found at all (provisional); 0 = skip
    timing: tuple = ()        # clips to take the timing from instead, if their events match
    root_motion: object = None  # e.g. UTurn: reshapes vanilla's path (and picks the motion to fit)


def seated_gesture(kind, seed):
    """Standing-still clips (idle, idle flavours, dialogue): seated, hands on the bars,
    with a little head movement so it doesn't look frozen."""
    def at(t):
        breath = 0.1 * math.sin(2 * math.pi * t)
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


def idle_specs():
    """The player's standing idle, idle flavours and dialogue clips (mt\\player), seated.
    The female folder lacks idledialogue6 and idleflavor9; those fall back to the male ones."""
    specs = [ClipSpec("posea_idle1", seated_gesture("still", 0), duration=4.0)]
    specs += [ClipSpec(f"posea_idleflavor{i}", seated_gesture("look", i), duration=6.0) for i in range(1, 10)]
    specs += [ClipSpec(f"posea_idledialogue{i}", seated_gesture("still", i), duration=5.0) for i in range(1, 7)]
    specs += [ClipSpec(f"posea_listen{i}", seated_gesture("still", i), duration=4.0) for i in range(1, 3)]
    for size, length in (("s", 2.5), ("m", 4.0), ("l", 6.0)):
        specs += [ClipSpec(f"posea_talk_{size}{i}", seated_gesture("talk", i), duration=length) for i in range(1, 9)]
    specs += [ClipSpec("posea_agree1", seated_gesture("nod", 0), duration=1.8),
              ClipSpec("posea_disagree1", seated_gesture("shake", 0), duration=1.8)]
    return specs


def clip_table():
    lean = {s: SPEEDS[s]["lean_roll"] for s in SPEEDS}
    specs = [
        ClipSpec("walkforward", riding("walk")),
        ClipSpec("walkleanleft", riding("walk", -lean["walk"])),
        ClipSpec("walkleanright", riding("walk", lean["walk"])),
        ClipSpec("jogforward", riding("jog")),
        ClipSpec("jogleanleft", riding("jog", -lean["jog"]), ("jogforward",)),
        ClipSpec("jogleanright", riding("jog", lean["jog"]), ("jogforward",)),
        ClipSpec("runforward", riding("run")),
        ClipSpec("runleanleft", riding("run", -lean["run"])),
        ClipSpec("runleanright", riding("run", lean["run"])),
        ClipSpec("sprintforward", riding("sprint")),
        ClipSpec("sprintleanleft", riding("sprint", -lean["sprint"]), ("sprintforward",)),
        ClipSpec("sprintleanright", riding("sprint", lean["sprint"]), ("sprintforward",)),
        ClipSpec("walk_to_walk_l180", turning("walk", "l", 12.0), root_motion=UTurn("walk", 12.0)),
        ClipSpec("walk_to_walk_r180", turning("walk", "r", 12.0), root_motion=UTurn("walk", 12.0)),
        ClipSpec("run_to_run_l180", turning("run", "l", 18.0), root_motion=UTurn("run", 18.0)),
        ClipSpec("run_to_run_r180", turning("run", "r", 18.0), root_motion=UTurn("run", 18.0)),
        ClipSpec("walk_to_stand", stopping("walk")),
        ClipSpec("walk_to_stand_r", stopping("walk")),
        ClipSpec("run_to_stand", stopping("run")),
    ]
    for speed in ("walk", "run"):
        specs.append(ClipSpec(f"stand_to_{speed}", starting(speed)))
        for d in ("l", "r"):
            for angle, peak in (("30", 5.0), ("90", 9.0), ("180", 12.0)):
                specs.append(ClipSpec(f"stand_to_{speed}_{d}{angle}", starting(speed, d, peak)))
    for d in ("l", "r"):
        for angle, peak in (("45", 5.0), ("90", 8.0), ("180", 10.0)):
            specs.append(ClipSpec(f"walk_to_stand_{d}{angle}", stopping("walk", d, peak)))
    for d in ("left", "right"):
        for angle in ("45", "90", "180"):
            for fast in ("", "_fast"):
                specs.append(ClipSpec(f"turninplace{d}{angle}{fast}", standing))
    return specs + idle_specs() + jump_specs()


def jump_specs():
    """Jumping, falling and landing (MT\\Neutral, female versions where they exist).
    Only built from the vanilla clips (duration 0): the landing states wait for their
    events, so a guessed clip could hold the rider in place. The hard landings take the
    soft landings' timing when those have the hard landing's events (JumpDown), so they
    don't stop you as long."""
    specs = []
    for kind, speed in (("inplace", "walk"), ("walk", "walk"), ("run", "run")):
        specs += [ClipSpec(f"jump{kind}", takeoff(speed)),
                  ClipSpec(f"jump{kind}fall", airborne(speed)),
                  ClipSpec(f"jump{kind}land", landing(speed))]
    specs += [ClipSpec("jumpimpactland", landing("walk", hard=True), timing=("jumpinplaceland",)),
              ClipSpec("jumprunimpactland", landing("run", hard=True), timing=("jumprunland",))]
    return specs


def find_clip(vanilla_root: Path, name: str, female: bool):
    anims = vanilla_root / "animations"
    for folder in SEARCH_ORDER[female]:
        p = anims / folder / (name + ".hkx")
        if p.exists():
            return p
    return None


def control_events(A, path: Path):
    """Events the behaviour graph acts on: footstep sounds and foot-sync markers aside."""
    return {a.text.lower() for a in A.load_fo4_animation(str(path)).annotations
            if not a.text.lower().startswith(("foot", "sync"))}


def source_path(vanilla_root: Path, spec: ClipSpec, female: bool, A=None):
    """The extracted vanilla clip whose timing, events and root motion a riding clip
    copies: the clip itself from the first folder the player searches, else a stand-in.
    A spec's `timing` clip is preferred when it has at least the control events of the
    clip itself (needs the animation module A to check)."""
    own = find_clip(vanilla_root, spec.name, female)
    if A is not None and own is not None:
        for name in spec.timing:
            alt = find_clip(vanilla_root, name, female)
            if alt is not None and control_events(A, alt) >= control_events(A, own):
                return alt
    if own is not None:
        return own
    for name in spec.stand_ins:
        p = find_clip(vanilla_root, name, female)
        if p is not None:
            return p
    return None


def game_source(game_files, spec: ClipSpec, female: bool):
    """Where the game itself takes the clip from, given the archive's file list."""
    for folder in SEARCH_ORDER[female]:
        if f"{folder}/{spec.name}" in game_files:
            return f"{folder}/{spec.name}"
    return None


def read_game_files(path: Path):
    """vanilla_character_animation_list.txt -> {"mt/player/walkforward", ...}"""
    prefix = "meshes\\actors\\character\\animations\\"
    out = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        l = line.strip().lower()
        if l.startswith(prefix) and l.endswith(".hkx"):
            out.add(l[len(prefix):-4].replace("\\", "/"))
    return out


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


def write_clip(A, rider: Rider, spec: ClipSpec, vanilla_root: Path, out_dir: Path, female=False):
    """Writes the clip; returns (path, poses, vanilla source or None if provisional)."""
    rig = rider.rig
    src_path = source_path(vanilla_root, spec, female, A)
    if src_path is None:
        if spec.duration <= 0:
            return None, None, None
        return write_provisional(A, rider, spec, out_dir) + (None,)
    src = A.load_fo4_animation(str(src_path))
    n = src.num_frames
    # The vanilla root motion is copied so the game's speed and turning maths stay
    # identical, or reshaped with the same heading timing (the ridden U-turn).
    samples, _ = reference_frame_samples(A, src_path.read_bytes())
    motion = spec.motion
    if spec.root_motion:
        samples, motion = spec.root_motion.plan(samples, src.duration, src.annotations)

    poses = [rider.pose(motion(i / max(1, n - 1))) for i in range(n)]
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

    data = bytearray(out.read_bytes())
    ours, start = reference_frame_samples(A, bytes(data))
    if len(ours) != len(samples):
        raise ValueError(f"{spec.name}: {len(ours)} root-motion samples vs {len(samples)} in vanilla")
    for i, s in enumerate(samples):
        struct.pack_into("<4f", data, start + 16 * i, *s)
    out.write_bytes(bytes(data))
    return out, poses, src_path


def clip_data(A, path: Path):
    """Root motion and events of a written clip, as the AnimTextData record the game
    reads instead of the .hkx (see animtextdata.py)."""
    import animtextdata
    anim = A.load_fo4_animation(str(path))
    try:
        samples, _ = reference_frame_samples(A, path.read_bytes())
    except (StopIteration, KeyError, struct.error):
        samples = []
    if len(samples) < 2:
        samples = [(0.0, 0.0, 0.0, 0.0)] * 2
    events = sorted((round(a.time, 6), a.text) for a in anim.annotations)
    rec = animtextdata.clip_record(path.stem, anim.duration, samples, events)
    return dict(duration=rec["duration"], translations=rec["translations"],
                rotations=rec["rotations"], events=rec["events"])


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
    ap.add_argument("--female-only", action="store_true",
                    help="only the Female set (e.g. after switching body mods); needs --female-body")
    ap.add_argument("--game-files", type=Path,
                    help="list of the archive's character animation files, to report clips that "
                         "weren't extracted from the folder the game uses")
    ap.add_argument("--fit", type=Path,
                    help="bike-fit file with the seat, grips and pegs of another bike model "
                         "(harley_meshes.py writes CMB_BikeFit.json); default: the vanilla motorcycle")
    args = ap.parse_args()
    if args.fit:
        apply_fit(args.fit)
        print(f"fitted to: {FIT_NAME} (seat top {SEAT_TOP_Z}, grips {GRIP_R.tolist()}, pegs {PEG_R.tolist()}"
              + (f", bars turning {BAR_ANGLE:g} deg in turns" if BAR_ANGLE else "") + ")")
    game_files = read_game_files(args.game_files) if args.game_files else None

    sys.path.insert(0, str(args.pynifly))
    A = load_anim_module(args.pynifly)
    rig = Rig.from_hkx(A.load_fo4_skeleton(str(args.vanilla / "characterassets" / "skeleton.hkx")))

    if args.female_only and not args.female_body:
        ap.error("--female-only needs --female-body")
    sets = [] if args.female_only else [("male", args.body, args.out, False)]
    if args.female_body:
        sets.append(("female", args.female_body, args.out / "Female", True))
    wanted = set()
    for label, body_nif, out_dir, female in sets:
        rider = Rider(rig)
        rider.seat(seat_probe(rig, body_nif, args.vanilla) if body_nif else None)
        print(f"{label}: seat height COM z = {rider.hip_z:.1f}")
        out_dir.mkdir(parents=True, exist_ok=True)
        write_seat(rider, out_dir / SEAT_FILE)
        records_path = out_dir / CLIP_DATA_FILE
        records = json.loads(records_path.read_text()) if args.only and records_path.exists() else {}
        written = provisional = 0
        missing = []
        for spec in clip_table():
            if args.only and spec.name not in args.only:
                continue
            out, _, src = write_clip(A, rider, spec, args.vanilla, out_dir, female)
            if out is None:
                missing.append(spec.name)
                records.pop(spec.name, None)
                game = game_source(game_files, spec, female) if game_files else None
                if game:
                    wanted.add(game)
                continue
            rel = src.relative_to(args.vanilla / "animations").with_suffix("").as_posix() if src else None
            records[spec.name] = dict(clip_data(A, out), source=rel)
            written += 1
            provisional += src is None
            game = game_source(game_files, spec, female) if game_files else None
            if game and game != rel:
                wanted.add(game)
        records_path.write_text(json.dumps(records, indent=1, sort_keys=True) + "\n")
        print(f"{label}: wrote {written} clips ({provisional} provisional) and {CLIP_DATA_FILE} to {out_dir}")
        if missing:
            print(f"{label}: skipped {len(missing)} clips that are only built from the vanilla ones "
                  f"(not extracted): {', '.join(missing)}")
    if wanted:
        print("timed from a stand-in or skipped; for the exact vanilla timing and the jump clips, "
              "extract these and run again:")
        for m in sorted(wanted):
            print(f"  meshes/actors/character/animations/{m}.hkx")
    return 0


def write_seat(rider: Rider, path: Path):
    """COM's model-space transform with the rider seated upright and still: the bind
    pose of the worn bike that hangs off COM (build_bike_meshes.py --seat). Every clip
    keeps COM there apart from the lean roll and a few millimetres of bounce."""
    com = rider.rig.index("COM")
    g = rider.pose(RideParams()).globals()[com]
    path.write_text(json.dumps(dict(bone="COM", hip_z=round(rider.hip_z, 4), fit=FIT_NAME,
                                    transform=[[round(float(v), 7) for v in row] for row in g]),
                               indent=1) + "\n")


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
