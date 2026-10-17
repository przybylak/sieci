#!/usr/bin/env bash
# Runs CMB_Slope.dll against the fake game under Wine: full test (offset known), probe only
# (no offset), the slope guard, a wrong game version, the tilt with transposed matrices, a
# game whose bike skin and 3D disagree about them, and BackPush=mod. Needs MinGW-w64 and wine64.
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
PARTS='[Parts]\nFrontAxle=0.4,99.6,29.9\nRearAxle=0.4,-36.7,29.9\nWheelRadius=29.9\nSteerPoint=0,87.6,51.4\nSteerAxis=0,-0.4,0.9165\nFrontMinY=44.2\nBarAngle=10\nBarFullAt=45\nLampPoint=0.3,76.3,81.9\nLampAxis=0,1,0\n[Lamp]\nAhead=0\nLead=0\n'
TILT0='[Tilt]\nPivotHeight=74\nPivotForward=0\nBumpMax=0\nLiftRate=0\nSuspension=0\n'   # the tilt about the seat itself, as the checks expect (the game's default is the ground since test 29); TorsoLean=0 in the runs with parts: the upper body's lean is tried on its own ride; BumpMax=0, LiftRate=0 and Suspension=0 keep the bump, the rate and the suspension off for the old checks' first-order numbers (each is tried on its own)
run full 0 "$KNOWN[Tilt]\nMaxRoll=10\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nTorsoSideLean=0.25\nWristRoll=1.0\nBumpMax=0\nLiftRate=0\nSuspension=0\n$PARTS"   # TorsoSideLean and WristRoll written at their defaults so the full run can rewrite them to 0 for a ride
run probe 1 '[Slope]\nSlopeOffset=\nProbe=1\nIntervalMs=100\nDumpPointers=0x2B8\n'
run guard 3 "$KNOWN$TILT0"
run wrongversion 2 "$KNOWN$TILT0"
run transposed 4 "$KNOWN$TILT0"
run disagree 5 "$KNOWN$TILT0"
run backpush 6 "$KNOWN[Tilt]\nTrace=1\nPivotHeight=74\nPivotForward=0\nBumpMax=0\nLiftRate=0\nSuspension=0\n[Steer]\nBackPush=mod\n"
run riderinplace 7 "$KNOWN[Tilt]\nMaxRoll=10\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nBumpMax=0\nLiftRate=0\nSuspension=0\nRiderSwap=0\nRiderPlain=0\n$PARTS"
run riderheldonly 8 "$KNOWN[Tilt]\nMaxRoll=10\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nBumpMax=0\nLiftRate=0\nSuspension=0\nRiderWrite=0\nRiderSkinned=0\n$PARTS"
exit $status
