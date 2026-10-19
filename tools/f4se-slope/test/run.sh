#!/usr/bin/env bash
# Runs CMB_Slope.dll against the fake game under Wine: full test (offset known), probe only
# (no offset), the slope guard, a wrong game version, the tilt with transposed matrices, a
# game whose bike skin and 3D disagree about them, BackPush=mod, loads into a ride (test 40's
# lost lean, and the log of the session before kept), climbing low things (test 40's fallen
# trunks and stumps), knocking enemies over (test 40's wish, test 41's answers), backing down
# a slope (test 40's shaking camera) and the arms (test 41: ArmPole and the inside arm's
# fade). Needs MinGW-w64 and wine64.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
x86_64-w64-mingw32-gcc -std=c11 -O1 -Wall -Wextra -o "$WORK/fake_game.exe" "$HERE/fake_game.c" -static-libgcc
WINE="${WINE:-$(command -v wine64 || echo /usr/lib/wine/wine64)}"
export WINEDEBUG=-all WINEPREFIX="${WINEPREFIX:-$WORK/prefix}"
status=0
ONLY="${ONLY:-}"   # ONLY=full bash run.sh: just that run, for a quick turn
run() { # <name> <mode> <ini body>
  if [ -n "$ONLY" ] && [ "$ONLY" != "$1" ]; then return; fi
  mkdir -p "$WORK/$1"
  cp "$HERE/../../../Data/F4SE/Plugins/CMB_Slope.dll" "$WORK/$1/"
  printf '%b' "$3" > "$WORK/$1/CMB_Slope.ini"
  echo "== $1"
  if (cd "$WORK/$1" && "$WINE" "$WORK/fake_game.exe" 'CMB_Slope.dll' "$2"); then :; else status=1; fi
  log="$(find "$WINEPREFIX" "$WORK/$1" -name CMB_Slope.log 2>/dev/null | head -1 || true)"
  if [ -n "$log" ]; then mv "$log" "$HERE/last_$1.log"; fi
}
KNOWN='[Slope]\nTarget=controller\nSlopeOffset=0x418\nSlopeUnit=cosine\nExpectedDegrees=47\nProbe=1\nIntervalMs=100\nDumpPointers=0x2B8\n'
PARTS0='[Parts]\nFrontAxle=0.4,99.6,29.9\nRearAxle=0.4,-36.7,29.9\nWheelRadius=29.9\nSteerPoint=0,87.6,51.4\nSteerAxis=0,-0.4,0.9165\nFrontMinY=44.2\nBarAngle=10\nBarFullAt=45\nLampPoint=0.3,76.3,81.9\nLampAxis=0,1,0\n'
LAMP='[Lamp]\nAhead=0\nLead=0\n'
PARTS="${PARTS0}Grip=56.45,79.79,54.85\n$LAMP"   # Grip: the +x grip's centre, the wrist roll's pivot (test 38); the fake's left hand sits 6 units from its mirror along the fingers, as the clips place it
PARTSNOGRIP="$PARTS0$LAMP"                      # without it the wrist rolls about the hand's node, as before test 38: riderinplace checks that
TILT0='[Tilt]\nPivotHeight=74\nPivotForward=0\nBumpMax=0\nLiftRate=0\nSuspension=0\n'   # the tilt about the seat itself, as the checks expect (the game's default is the ground since test 29); TorsoLean=0 in the runs with parts: the upper body's lean is tried on its own ride; BumpMax=0, LiftRate=0 and Suspension=0 keep the bump, the rate and the suspension off for the old checks' first-order numbers (each is tried on its own)
run full 0 "$KNOWN[Tilt]\nMaxRoll=10\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nTorsoSolveFrom=0.5\nTorsoTwist=0.75\nTorsoSideLean=0.25\nWristRoll=1.0\nHandPitch=0\nArmPole=1.1,-0.3,-0.9\nArmPoleTurn=0.35,-0.3,-1.0\nArmPoleTurnBars=10\nArmReach=0.80\nBumpMax=0\nLiftRate=0\nSuspension=0\n$PARTS"   # TorsoTwist, TorsoSideLean, WristRoll, HandPitch, ArmPole, ArmPoleTurn, ArmPoleTurnBars and ArmReach written at their defaults so the full run can rewrite them for a ride; TorsoSolveFrom at test 39's half second, which the lean rides' timings were made for (one ride rewrites it to the default 1.3)
run probe 1 '[Slope]\nSlopeOffset=\nProbe=1\nIntervalMs=100\nDumpPointers=0x2B8\n'
run guard 3 "$KNOWN$TILT0"
run wrongversion 2 "$KNOWN$TILT0"
run transposed 4 "$KNOWN$TILT0"
run disagree 5 "$KNOWN$TILT0"
run backpush 6 "$KNOWN[Tilt]\nTrace=1\nPivotHeight=74\nPivotForward=0\nBumpMax=0\nLiftRate=0\nSuspension=0\n[Steer]\nBackPush=mod\n"
run riderinplace 7 "$KNOWN[Tilt]\nMaxRoll=10\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nBumpMax=0\nLiftRate=0\nSuspension=0\nRiderSwap=0\nRiderPlain=0\n$PARTSNOGRIP"
run riderheldonly 8 "$KNOWN[Tilt]\nMaxRoll=10\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nBumpMax=0\nLiftRate=0\nSuspension=0\nRiderWrite=0\nRiderSkinned=0\n$PARTS"
run load 9 "$KNOWN[Tilt]\nMaxRoll=10\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=-1\nBumpMax=0\nLiftRate=0\nSuspension=0\n$PARTS"   # test 40's finding 2: the upper body's lean solved (TorsoLean=-1) at TorsoSolveFrom's default 1.3, which no other run tries after a load
run climb 10 "$KNOWN[Tilt]\nMaxRoll=10\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nTorsoSolveFrom=0.5\nBumpMax=0\nLiftRate=0\nSuspension=0\n[Steer]\nClimb=1\n$PARTS"   # test 40's finding 8: the fake's capsule stopped by low things (mode 10 only); Climb=1 written so the run can rewrite it to 0 for a ride
run ram 11 "$KNOWN[Tilt]\nMaxRoll=10\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nTorsoSolveFrom=0.5\nBumpMax=0\nLiftRate=0\nSuspension=0\n[Ram]\nEnabled=1\nHitHold=0.4\n$PARTS"   # test 40's finding 7: the harness plays CMB_RamScript (mode 11 only); Enabled=1 and HitHold=0.4 written so the run can rewrite them to 0 for a ride
run backing 12 "$KNOWN[Tilt]\nTrace=1\nPivotHeight=74\nPivotForward=0\nBumpMax=0\nLiftRate=0\nSuspension=0\n[Steer]\nBackFollow=10\n"   # test 40's finding 6: backing down follows the ground (a ground profile, a ripple and a physics-lite controller, mode 12 only); BackFollow=10 written so the run can rewrite it to 0 for test 40's rule
PARTS20="${PARTS/BarAngle=10/BarAngle=20}"   # the game's bar angle, so the bars reach 12 deg on the spot
run arms 13 "$KNOWN[Tilt]\nMaxRoll=10\nPivotHeight=74\nPivotForward=0\nTorsoLean=8\nTorsoTwist=0.75\nTorsoSideLean=0.25\nBumpMax=0\nLiftRate=0\nSuspension=0\nArmPole=1.1,-0.3,-0.9\nArmPoleTurn=0.35,-0.3,-1.0\nArmPoleTurnBars=10\n$PARTS20"   # test 41's finding 5: the inside arm's fade at 5 and 12 deg of the bars, both arms, ArmPoleTurn=0,0,0 for a ride, the arm lines' figures against the bones; TorsoLean 8 so the arms are solved with the bars straight
exit $status
