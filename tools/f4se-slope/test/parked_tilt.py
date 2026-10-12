#!/usr/bin/env python3
"""Checks the parked bike's tilt formula (CMB_ControllerScript.TiltParkedBike).

A reference's angles (x, y, z) turn it as Z(z) X(x) Y(y), each clockwise the game's way
(the order of Gamebryo's EulerAnglesToAxesZXY): heading last, then pitch and roll about
its own axes. For random headings and slopes up to 10 degrees (inside both caps), the
script's pitch and roll must take the bike's up onto the ground's normal; parked on the
ridden track (an up at right angles to the line between the wheels' ground points, which
the plugin finds no steeper than 45 along and 20 across), the bike's length must lie along
that line even with the roll capped at 10 degrees; the pitch and the roll are capped each
on its own (a steep face at an angle keeps the full 45 pitch); and an uphill park facing
the slope must lift the bike's nose (the parked model faces -Y, hence the 180 degrees).

  python3 parked_tilt.py
"""
import math
import random
import sys

d = math.radians


def Z(z):
    c, s = math.cos(z), math.sin(z)
    return [[c, s, 0], [-s, c, 0], [0, 0, 1]]


def X(x):
    c, s = math.cos(x), math.sin(x)
    return [[1, 0, 0], [0, c, s], [0, -s, c]]


def Y(y):
    c, s = math.cos(y), math.sin(y)
    return [[c, 0, -s], [0, 1, 0], [s, 0, c]]


def mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def apply(m, v):
    return [sum(m[i][k] * v[k] for k in range(3)) for i in range(3)]


PARK_MAX_PITCH, PARK_MAX_ROLL = 45.0, 10.0


def script_angles(angle, n):
    """Pitch and roll as TiltParkedBike works them out (degrees, like Papyrus' Math)."""
    c, s = math.cos(d(angle)), math.sin(d(angle))
    nz = max(n[2], 0.01)
    pitch = math.degrees(math.atan((s * n[0] + c * n[1]) / nz))
    pitch = max(-PARK_MAX_PITCH, min(PARK_MAX_PITCH, pitch))
    roll = -math.degrees(math.asin(max(-1.0, min(1.0, c * n[0] - s * n[1]))))
    roll = max(-PARK_MAX_ROLL, min(PARK_MAX_ROLL, roll))
    return pitch, roll


def main() -> int:
    random.seed(1)
    worst = 0.0
    for _ in range(2000):
        angle = random.uniform(0, 360) + 180
        slope, towards = random.uniform(0, 10), random.uniform(0, 360)
        n = [math.sin(d(slope)) * math.sin(d(towards)), math.sin(d(slope)) * math.cos(d(towards)), math.cos(d(slope))]
        pitch, roll = script_angles(angle, n)
        up = apply(mul(Z(d(angle)), mul(X(d(pitch)), Y(d(roll)))), [0, 0, 1])
        worst = max(worst, max(abs(up[i] - n[i]) for i in range(3)))
    print(f"up onto the ground's normal: worst error {worst:.1e}")

    # Parking on the ridden track: the plugin's up is at right angles to the line between
    # the two wheels' ground points, so the bike's length must lie along that line, also
    # when the script caps the roll.
    worst_track = 0.0
    for _ in range(2000):
        heading = random.uniform(0, 360)
        climb = random.uniform(-45, 45)
        a = [math.sin(d(heading)) * math.cos(d(climb)), math.cos(d(heading)) * math.cos(d(climb)), math.sin(d(climb))]
        side = random.uniform(-20, 20)   # the ground's lean across the track
        nrm = [math.cos(d(heading)) * math.sin(d(side)), -math.sin(d(heading)) * math.sin(d(side)), math.cos(d(side))]
        dot = sum(nrm[i] * a[i] for i in range(3))
        up = [nrm[i] - dot * a[i] for i in range(3)]
        length = math.sqrt(sum(u * u for u in up))
        up = [u / length for u in up]
        angle = heading + 180
        pitch, roll = script_angles(angle, up)
        M = mul(Z(d(angle)), mul(X(d(pitch)), Y(d(roll))))
        back = apply(M, [0, 1, 0])           # the model's +Y is its back (it faces -Y)
        worst_track = max(worst_track, max(abs(back[i] + a[i]) for i in range(3)))
    print(f"parked on the track: the bike's length along it, worst error {worst_track:.1e}")

    # A 60 degree face, falling away at 40 degrees to the bike: the pitch stops at the cap
    # (scaling the normal down to 45 would have left it at about 37).
    n = [math.sin(d(60)) * math.sin(d(40)), math.sin(d(60)) * math.cos(d(40)), math.cos(d(60))]
    steep_pitch, steep_roll = script_angles(0, n)
    print(f"60 deg face at 40 deg to the bike: pitch {steep_pitch:.1f}, roll {steep_roll:.1f}")

    n = [0, -math.sin(d(20)), math.cos(d(20))]   # uphill to the north
    pitch, roll = script_angles(180, n)           # player facing north
    nose = apply(mul(Z(d(180)), mul(X(d(pitch)), Y(d(roll)))), [0, -1, 0])
    print(f"uphill park facing the slope: pitch {pitch:.1f}, roll {roll:.1f}, nose up {nose[2]:.3f}")
    ok = (worst < 1e-9 and worst_track < 1e-9 and nose[2] > 0.3 and abs(steep_pitch) == PARK_MAX_PITCH
          and abs(steep_roll) == PARK_MAX_ROLL)
    print("ok" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
