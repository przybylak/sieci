#!/usr/bin/env bash
# Runs CMB_Slope.dll against the fake game under Wine: full test (offset known), probe only
# (no offset), the slope guard, a wrong game version, the tilt with transposed matrices, a
# game whose bike skin and 3D disagree about them, BackPush=mod, loads into a ride (test 40's
# lost lean, and the log of the session before kept), climbing low things (test 40's fallen
# trunks and stumps), knocking enemies over (test 40's wish, test 41's and test 42's answers), backing down
# a slope (test 40's shaking camera) and up to a rail or a ledge (test 42: the rear's clearance from the
# parts file, the ray under the rear tyre), the arms (test 41: ArmPole and the inside arm's
# fade) and the brought bike's spot (test 41: the room asks; test 42's answer, the box along the
# spot's heading and the test ray tried again for an ask, with an ESP of test 42's build too);
# riding beside a railing (test 42) and test 44's rails (a beam not climbed, a step still; backing off
# a beam hung up) ride with the climbing and the backing; the engine sound (test 44's build: the
# script's hand-over of its loops played by the harness, the Address Library and the sound functions
# the fake's own; test 46: the game's SetVolume and FadeTo as test 45's tester found them); the 2026-10-31a build's look (the
# shapes' roles by their names (the fake's table, 30 since the 2026-11-01a build's two brake discs), the speedometer's
# needle, the tail and brake lights, the dial's backlight, the mirrors' choice, every new key's off value, 27c's twelve
# names, 50 shapes past MAX_SKINS), on a bike of its own (the other modes keep the 5-shape fake); the 2026-11-01a build's
# blood decals and the rider's copy pool (test 47's floating rider), WallStop beside the turn, the climb's boost and
# barriers on legs, the tail lamp's light and the bike in first person, and the landings and the bike's own sounds
# (the landing cue and the water loop); the 2026-11-02a build's item uses and first person (the hands let go for a use
# clip, the knees not measured there, your eye on the seat), knocking over (a pack's hits one dip, enemies passed while
# their ask is pending, in a mode of its own: hits), the narrow things, kerbs and rails, the idle and the bike's own
# sound records, and the log's rate limits and frame-rate line; the 2026-11-06a build's look down on getting into first
# person, the riding FOV and the eye's globals, a narrow thing's own reference, the rail at 1.5 radii and the sidestep,
# the launch from rest (in a mode of its own: launch), the most room's navmesh point, items used at speed, the food arm,
# the player's own items and power attacks, the headlamp let go, the landings without metal, the water loop's law and
# kinds, the longer gear change and the launch's flare; the 2026-11-07a build's customisation: the CMB_LookCode global
# (an older ESP without it), the mirrors as chosen at the bike ([Look] Mirrors=-1) on the worn and first-person bikes,
# and the split tank badges and the rear fender's patch held (in a mode of its own: custom); the 2026-11-08a build's
# rim styles held and hidden as chosen at the bike ([Look] Rims, CMB_LookCode bits 3-6), the plate's two shapes, the
# look colours written into the worn bike's materials ([Look] PaintWheel and PlateColours) and 64 skins (custom), and an
# older ESP without the colour globals (roomold; the writer with three of the four on look's bike, and only into its
# V's palette in custom: reviews B3, B2); the 2026-11-09a build's knock-off guards (an actor in a spot's place is no room,
# the parked bike's old spot asked first, the parked bike kept hidden while anyone is in its place: room), an item's use
# clip stopped at speed and the graph's slot-1 events listed (arms), the Caution slider, the wheels by the frame's own
# movement and held while braking, and the bridge's end post (in a mode of its own: caution), the truck's call in its
# new order (room), the first-person tip held off in the Pip-Boy, composed with your own look and after a settle, the
# view bike's ancestors' bounds, the draw diagnostic, the near plane and the FOV search (view), each gear's own rise and
# least time (sound), the gentle wet road (fx), and an older ESP without the build's two globals (roomold); and with
# test 51's fixes, the [Look] switches the scripts read (CMB_LookOptions, written again at a load: custom; an older ESP
# without it: roomold), a worn shape the game rebuilt in place held afresh and the look colours written only through a
# lighting shader (custom), a tip verdict within TipLoadGrace of a load holding for that entry only (custom), the draw
# line's reference (view) and each gear longer than the last (sound); and with the review of those fixes, the parked
# bike's guard counting the player only in its own box and not where the script placed it (a park after a bend, a call's
# spot 7 100 ahead, the put-back's band: room), the FOV search within PlayerCamera's 0x1B0 bytes (view) and Caution 50
# at test 45's rail (caution); and the 2026-11-10a build's (test 52's fixes): a potion's quickkey at speed used by the
# script with no clip and UseStop only on an item's props (arms), CMB_LookOptions' five new bits, CMB_RideReady and the
# worn paint's diagnostic (custom, look), the first-person draw diagnostic, the view bike under the player's cell and
# the game's own update, the FOV found by the camera's layout and the tip's yield (view), the engine held through a
# menu, 3rd gear's 3 s and the paused-game lines (sound), the gentle loop's own trim (fx), Caution 50's sidestep found
# at 60's reach (caution), the guard's bodies, floor and the player's height (room), and an older ESP without the
# build's two globals (roomold); and with the review of those fixes, a quickkey taken only while the hotkey script's
# watch is on (arms) and the bike ready at the MCM's tilt 0 (look). 26 modes (0-25). Needs MinGW-w64 and wine64.
# The 2026-11-10a build: 1762 checks ok (full 382, probe 10, guard 8, wrongversion 4, transposed 76, disagree 6,
# backpush 6, riderinplace 18, riderheldonly 8, load 43, climb 125, wall 75, ram 110, hits 22, launch 13, caution 24,
# backing 56, arms 47, room 149, roomold 59, decals 77, sound 110, look 67, view 157, fx 46, custom 64); 1757 before its
# review's fixes; 1688 at 2026-11-09a (1682 before its review's fixes, 1667 before test 51's fixes), 1611 in 25 modes
# at 2026-11-08a. The 2026-11-14a build (test 53's fixes) adds: the number keys at speed by the game's own key codes
# and Quickkey names, the favourites' self-test, an item's use clip judged at its props by its own cause, rule 3's wait
# and QuickCut's hand-over to the hotkey script (arms, 47 + 21); the field kit's preview written by the plugin and its
# menu's 3D logged (12), and Free colour's worn indexes in CMB_LookOptions (4096-16384), the worn paint's render passes,
# Repass and the paint not written (12) (custom, 64 + 24); an older ESP's dormant preview (roomold, 59 + 1); the
# first-person eye held on the bike as tilted, its axes along your heading, the camera's own place of the frame through
# GetTranslation, the lock's line, the FOV dropped and EyeAt 0,1,128 (view, 157 + 19); the engine silent in a menu
# (MenuQuiet), the note not falling while the bike gains (HeardKeep), no 2nd -> 1st on a lift (LiftDown) and the five
# gears (12), and the hand-over line from the bike's ready time (3) (sound, 110 + 15); the water loop silent in a menu
# (fx, 46 + 2). DEF57 rides every older mode at the new keys' off values. Expected at 2026-11-14a: 1844 checks ok (full
# 382, probe 10, guard 8, wrongversion 4, transposed 76, disagree 6, backpush 6, riderinplace 18, riderheldonly 8, load
# 43, climb 125, wall 75, ram 110, hits 22, launch 13, caution 24, backing 56, arms 68, room 149, roomold 60, decals 77,
# sound 125, look 67, view 176, fx 48, custom 88).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
x86_64-w64-mingw32-gcc -std=c11 -O1 -Wall -Wextra -o "$WORK/fake_game.exe" "$HERE/fake_game.c" -static-libgcc
WINE="${WINE:-$(command -v wine64 || echo /usr/lib/wine/wine64)}"
export WINEDEBUG=-all WINEPREFIX="${WINEPREFIX:-$WORK/prefix}"
status=0
ONLY="${ONLY:-}"   # ONLY=full bash run.sh: just that run, for a quick turn
# 2026-11-06a: drive's new [Steer] keys at their off values (the 2026-11-02a build's driving) in every mode whose INI
# doesn't name them; a mode that names one (launch) keeps its own. Put into the INI's first [Steer] (or a [Steer] added
# at the end): GetPrivateProfileString takes a section's and a key's first copy, so nothing may be written twice.
DEF51='Sidestep=0 LaunchTau=0'
# 2026-11-09a: every new key of the round at its off value (the 2026-11-08a build's), Section/Key=value, in every mode
# whose INI doesn't name the key (whatever its section): put at the end of the mode's first [Section] (the rides rewrite
# "[Section]\nKey=..." texts), or into a [Section] added at the end. An empty value is written as Key= (GetPrivateProfileString then gives ""). Near, GuardMargin and WheelStill have no
# off value (their defaults change nothing with the rest off): not here.
DEF54='Steer/Caution=100 Steer/UseListen=0 Steer/UseStop= Steer/ClimbStepSpan=0 Parts/WheelSpin=0 Parts/WheelLock=0 Room/ActorRoom=0 Room/ParkBack=0 Room/ParkGuard=0 Room/SnapOrder=0 View/TipMenu=0 View/TipYield=0 View/TipSettle=0 View/Bounds=0 View/FovSearch=0 Diag/ViewDraw=0 Sound/HeardRiseGears=1,1,1,1 Sound/ShiftGapGears='
# 2026-11-09a, test 51's fixes: the round's new keys at their off values (2026-11-09a as of t54-merge), the same way (the
# loop below takes DEF54's, then these). The gear keys need none: DEF54 already gives every older mode their 08a values.
DEF55='Look/FastMount=0 Look/KitHeld=0 Look/ParkedReload=0 Look/PaletteIndex=0 Look/MountGuard=0 Look/HueFree=0 Look/Rehold=0 Look/LightingOnly=0 View/TipLoadGrace=0'
# 2026-11-10a, test 52's fixes: the round's new keys at their off values (2026-11-09a, 1712b81), the same way (after DEF54's
# and DEF55's). Not in it: ViewThird (its default 0 is off), QuickUseAbove, QuickKeys, MenuRejoin and ViewThirdOffset (no off
# value of their own: they act only with QuickUse, MenuHold or ViewThird on), WaterGentleDb (its default 0 is 2026-11-09a's
# plugin; -3 is 09a's level with the rebuilt loop, an A/B), and the changed defaults of ViewDraw, FovSearch, TipYield and
# ShiftGapGears (DEF54 already pins them for every older mode).
DEF56='Look/KitStash=0 Look/KitRetry=0 Look/MountEarly=0 Look/RideReady=0 Look/WornColoursFirst=0 Look/HueSwap=0 Diag/WornColour=0 Steer/QuickUse=0 Steer/UseStopCue=any Steer/UseStopNotUnder= Steer/UseStopAt=knees Steer/SidestepCaution=0 Steer/SidestepMouse=3 Room/GuardBodies=0 Room/GuardFloor=0 Room/GuardPlayerZ=0 Diag/Paused=0 View/Parent=0 View/Update=0 Diag/ViewDrawEvery=0 Sound/MenuHold=0'
# 2026-11-14a, test 53's fixes: the round's new keys at their off values (2026-11-10a, c716330), the same way (after DEF54's,
# DEF55's and DEF56's). The kit unit's: KitPreview and KitPreviewLog (not KitPreviewPos, Turn, Scale and Zoom: New's values,
# acting only with KitPreview). The view unit's: EyeLock, EyeAxes, Camera, EyeAtCamera, Fov=1 (CMB_ViewFov as in 10a),
# ViewLock and EyeAt at 10a's 0,12,128 (its default is 0,1,128 now). The quick unit's: QuickKeyCodes, QuickKeyState, QuickCut,
# UseStopUnapplied and QuickProbe (not UseStopWaitMax and UseStopLead: they act only with UseStopUnapplied=wait). The colour
# unit's: WornIndex, KeptMods, WornPasses and HandoverFromReady (not Repass: its default 0 is off). The sound unit's: HeardKeep,
# LiftDown, MenuQuiet and the gear table's changed defaults at 10a's values (ShiftRpm, Gears, ShiftDraw, LaunchRise,
# LaunchFlare; HeardRiseGears and ShiftGapGears DEF54 already pins; not HeardCreep, MenuQuietOut, MenuQuietIn: they act only
# with HeardKeep or MenuQuiet on). The [Sound] key is HeardKeep, not the design's Climb: [Steer] Climb exists, and the loop's
# "already named" test is section-blind.
DEF57='Look/KitPreview=0 Look/KitPreviewLog=0 View/EyeLock=0 View/EyeAxes=0 View/Camera=0 View/EyeAtCamera=0 View/Fov=1 Diag/ViewLock=0 View/EyeAt=0,12,128 Steer/QuickKeyCodes=scan Steer/QuickKeyState=0 Steer/QuickCut=0 Steer/UseStopUnapplied=cut Diag/QuickProbe=0 Look/WornIndex=0 Look/KeptMods=0 Diag/WornPasses=0 Diag/HandoverFromReady=0 Sound/HeardKeep=0 Sound/LiftDown=0 Sound/MenuQuiet=0 Sound/ShiftRpm=2500 Sound/Gears=555.556,750,960,1161.6 Sound/ShiftDraw=2300,3000 Sound/LaunchRise=350 Sound/LaunchFlare=0.5'
run() { # <name> <mode> <ini body>
  if [ -n "$ONLY" ] && [ "$ONLY" != "$1" ]; then return; fi
  mkdir -p "$WORK/$1"
  cp "$HERE/../../../Data/F4SE/Plugins/CMB_Slope.dll" "$WORK/$1/"
  local ini="$3" kv steer='[Steer]\n'
  for kv in $DEF51; do
    case "$ini" in "${kv%%=*}="*|*"\n${kv%%=*}="*) continue;; esac
    case "$ini" in *'\n') ;; *) ini="$ini\n";; esac
    case "$ini" in
      *"$steer"*) ini="${ini/"$steer"/"$steer$kv\n"}";;
      *) ini="$ini$steer$kv\n";;
    esac
  done
  local sec key pre rest
  for kv in $DEF54 $DEF55 $DEF56 $DEF57; do
    sec="[${kv%%/*}]\n" kv="${kv#*/}" key="${kv%%=*}"
    case "$ini" in "$key="*|*"\n$key="*) continue;; esac
    case "$ini" in *'\n') ;; *) ini="$ini\n";; esac
    case "$ini" in
      *"$sec"*)   # at the end of the first [Section], so the rides' rewrites of "[Section]\nKey=..." still find their text
        pre="${ini%%"$sec"*}$sec" rest="${ini#*"$sec"}"
        case "$rest" in
          '['*) ini="$pre$kv\n$rest";;
          *'\n['*) ini="$pre${rest%%'\n['*}\n$kv\n[${rest#*'\n['}";;
          *) ini="$ini$kv\n";;
        esac;;
      *) ini="$ini$sec$kv\n";;
    esac
  done
  printf '%b' "$ini" > "$WORK/$1/CMB_Slope.ini"
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
run full 0 "$KNOWN[Tilt]\nMaxRoll=10\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nDecalsFollow=0\nTorsoSolveFrom=0.5\nTorsoTwist=0.75\nTorsoSideLean=0.25\nWristRoll=1.0\nHandPitch=0\nArmPole=1.1,-0.3,-0.9\nArmPoleTurn=0.35,-0.3,-1.0\nArmPoleTurnBars=10\nArmReach=0.80\nNodelessNear=2\nBumpMax=0\nLiftRate=0\nSuspension=0\nLandSink=1\nLandSpeed=700\n[Steer]\nLowObstacleThrottle=0\nLandHold=0.5\nLandAir=0.3\nLandStop=0.25\n$PARTS"   # TorsoTwist, TorsoSideLean, WristRoll, HandPitch, ArmPole, ArmPoleTurn, ArmPoleTurnBars, ArmReach and NodelessNear (test 41: the hat's Head_skin) written at their defaults so the full run can rewrite them for a ride; TorsoSolveFrom at test 39's half second, which the lean rides' timings were made for (one ride rewrites it to the default 1.3); test 42's landing: LandSink, LandSpeed, LandHold, LandAir and LandStop at their defaults, so a ride can rewrite LandHold and LandSink to 0; DecalsFollow=0 (2026-11-01a): the test-29 decal, cloned from the body onto its copy, is held as it was, so those checks keep their meaning (mode 18 has the decals that follow)
run probe 1 '[Slope]\nSlopeOffset=\nProbe=1\nIntervalMs=100\nDumpPointers=0x2B8\n'
run guard 3 "$KNOWN$TILT0"
run wrongversion 2 "$KNOWN$TILT0"
run transposed 4 "$KNOWN${TILT0}DecalsFollow=0\n"   # 2026-11-01a: TiltTests' test-29 decal held as before, as in the full run
run disagree 5 "$KNOWN$TILT0"
run backpush 6 "$KNOWN[Tilt]\nTrace=1\nPivotHeight=74\nPivotForward=0\nBumpMax=0\nLiftRate=0\nSuspension=0\n[Steer]\nBackPush=mod\n"
run riderinplace 7 "$KNOWN[Tilt]\nMaxRoll=10\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nBumpMax=0\nLiftRate=0\nSuspension=0\nRiderSwap=0\nRiderPlain=0\n$PARTSNOGRIP[Diag]\nAPWatch=1\nAPWatchFor=120\nAPWatchEvery=2\n"   # test 46's AP watch: [Diag] at its defaults, so the run can rewrite them (mode 7 only)
run riderheldonly 8 "$KNOWN[Tilt]\nMaxRoll=10\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nBumpMax=0\nLiftRate=0\nSuspension=0\nRiderWrite=0\nRiderSkinned=0\n$PARTS"
run load 9 "$KNOWN[Tilt]\nMaxRoll=10\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=-1\nBumpMax=0\nLiftRate=0\nSuspension=0\n$PARTS"   # test 40's finding 2: the upper body's lean solved (TorsoLean=-1) at TorsoSolveFrom's default 1.3, which no other run tries after a load
run climb 10 "$KNOWN[Tilt]\nMaxRoll=10\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nTorsoSolveFrom=0.5\nBumpMax=0\nLiftRate=0\nSuspension=0\n[Steer]\nClimb=1\nClimbMaxTop=0\nNarrowHeights=3\nClimbBeamLow=8\nWallStop=0.6\nWallStopReach=1\nWallStopPersist=0.15\nWallStopNear=0\nWallStopArc=90\nWallStopShort=10\nWallStopNarrow=0\nFaceAlong=30\nFaceAlongRays=1\nSlideHold=1.0\nSlideAngle=15\n$PARTS"   # test 40's finding 8: the fake's capsule stopped by low things (mode 10 only); Climb=1 written so the run can rewrite it to 0 for a ride; test 42's railing: FaceAlong, FaceAlongRays, SlideHold and SlideAngle at their defaults, so rides can rewrite them to 0; test 44's rails: ClimbMaxTop=0 (the ClimbTop rule alone) for the checks made before them, the rails ride rewriting it to 18, the default; test 45's rails: NarrowHeights, ClimbBeamLow and WallStop at their defaults, so rides can rewrite each to its off value; test 46's glimpses: WallStopReach, WallStopPersist, WallStopNear, WallStopArc and WallStopShort at their defaults, so rides can rewrite each to its off value (test 46's build), WallStopNear's to 1 (its default is its off value, 0, since the review of test 47's build)
run wall 19 "$KNOWN[Tilt]\nMaxRoll=10\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nTorsoSolveFrom=0.5\nBumpMax=0\nLiftRate=0\nSuspension=0\n[Steer]\nClimb=1\nClimbMaxTop=0\nNarrowHeights=3\nClimbBeamLow=8\nWallStop=0.6\nWallStopReach=1\nWallStopPersist=0.15\nWallStopNear=0\nWallStopArc=90\nWallStopShort=10\nFaceArc=90\nWallStopClimb=1\nClimbLegs=145\nWallStopNarrow=40\nFaceAlong=30\nFaceAlongRays=1\nSlideHold=1.0\nSlideAngle=15\nSlideRestore=0.5\nFaceAlongKeep=1.0\nWallNarrowSame=1\nWallNarrowHigh=1\nSidestep=0\n$PARTS"   # 2026-11-01a (test 47's WallStop cuts at full speed in Sanctuary and the wooden road barriers climbed at 10-30 deg; mode 19 only): mode 10's world and [Steer], with FaceArc, WallStopClimb and ClimbLegs written at their defaults so rides can rewrite each to its 0 (the 2026-10-31a build); 2026-11-06a: WallNarrowSame and WallNarrowHigh at their defaults so rides can rewrite each to 0 (2026-11-02a), Sidestep=0 (the older rides' 2026-11-02a driving; the sidestep's rides rewrite it to 40)
run ram 11 "$KNOWN[Tilt]\nMaxRoll=10\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nTorsoSolveFrom=0.5\nBumpMax=0\nLiftRate=0\nSuspension=0\n[Ram]\nEnabled=1\nHitKeep=0.6\nHitHold=0.4\nAskGap=0.12\nAskAnswered=1\nAskFree=0.5\nYesKeep=10\nHitGrace=1\nHighRay=96\nSideRays=20\nRobots=1\nPendingPass=1\nFaceActors=1\nSeenGrace=1.5\nHitChain=0\nPendingFoe=0\n$PARTS"   # test 40's finding 7: the harness plays CMB_RamScript (mode 11 only); Enabled=1, HitHold=0.4 and AskGap=0.12 (test 41's packs) written so the run can rewrite them to 0 for a ride; test 42's knocking over: AskAnswered, AskFree, YesKeep, HitGrace, HighRay, SideRays and Robots at their defaults, so rides can rewrite each to 0; test 44's PendingPass, FaceActors and SeenGrace too; the 2026-11-02a build's HitKeep=0.6 (HitHold=0.4 above), HitChain=0 and PendingFoe=0 written: 2026-11-01a's knocking over, its checks the off values (mode 22 has the new ones)
run hits 22 "$KNOWN[Tilt]\nMaxRoll=10\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nTorsoSolveFrom=0.5\nBumpMax=0\nLiftRate=0\nSuspension=0\n[Ram]\nEnabled=1\nHitKeep=0.85\nHitHold=0.25\nAskGap=0.12\nAskAnswered=1\nAskFree=0.5\nYesKeep=10\nHitGrace=1\nHighRay=96\nSideRays=20\nRobots=1\nPendingPass=1\nFaceActors=1\nSeenGrace=1.5\nHitChain=1.0\nPendingFoe=2\n$PARTS"   # the 2026-11-02a build's knock-overs (test 48: the speed lost at hits, the brakes for pending asks); mode 11 stays at 2026-11-01a's values; HitKeep, HitHold, HitChain and PendingFoe written at their defaults, so rides can rewrite each to its off value (or take it out for the compiled default)
run launch 23 "$KNOWN$TILT0[Steer]\nLaunchTau=1.5\nLaunchFrom=0.25\nLaunchLead=0.45\n"   # 2026-11-06a (test 49's slow take-off; mode 23 only): the launch from rest; the drive unit's from here
run caution 25 "$KNOWN[Tilt]\nMaxRoll=10\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nTorsoSolveFrom=0.5\nBumpMax=0\nLiftRate=0\nSuspension=0\n[Steer]\nClimb=1\nClimbMaxTop=0\nNarrowHeights=3\nClimbBeamLow=8\nWallStop=0.6\nWallStopReach=1\nWallStopPersist=0.15\nWallStopNear=0\nWallStopArc=90\nWallStopShort=10\nFaceArc=90\nWallStopClimb=1\nClimbLegs=145\nWallStopNarrow=40\nFaceAlong=30\nFaceAlongRays=1\nSlideHold=1.0\nSlideAngle=15\nSlideRestore=0.5\nFaceAlongKeep=1.0\nWallNarrowSame=1\nWallNarrowHigh=1\nSidestep=0\n$PARTS"   # 2026-11-09a (test 50's Caution, the wheels and the bridge's end post, rides that can't go into full or climb; mode 25 only): mode 19's world and INI; the drive unit's from here
run backing 12 "$KNOWN[Tilt]\nTrace=1\nPivotHeight=74\nPivotForward=0\nBumpMax=0\nLiftRate=0\nSuspension=0\n[Steer]\nBackFollow=10\nBackClearance=0\nBackMargin=25\nBackLedge=1\nBackHungDrop=40\nBrakeKey=-1\n$PARTS0"   # test 40's finding 6: backing down follows the ground (a ground profile, a ripple and a physics-lite controller, mode 12 only); BackFollow=10 written so the run can rewrite it to 0 for test 40's rule; test 42's backing too early: the parts file (the rear tyre's back edge 66.6 behind the rider) with BackClearance, BackMargin and BackLedge at their defaults, so rides can rewrite BackClearance to 150 and BackLedge to 0; test 44's rails: BackHungDrop at its default, so a ride can rewrite it to 0; the 2026-11-01a build's brake key: BrakeKey at its default (-1, the ESP's CMB_BrakeKey 57), so rides can rewrite it to 0 and 31
PARTS20="${PARTS/BarAngle=10/BarAngle=20}"   # the game's bar angle, so the bars reach 12 deg on the spot
run arms 13 "$KNOWN[Tilt]\nMaxRoll=10\nPivotHeight=74\nPivotForward=0\nTorsoLean=8\nTorsoTwist=0.75\nTorsoSideLean=0.25\nBumpMax=0\nLiftRate=0\nSuspension=0\nArmPole=1.1,-0.3,-0.9\nArmPoleTurn=0.35,-0.3,-1.0\nArmPoleTurnBars=10\n$PARTS20"   # test 41's finding 5: the inside arm's fade at 5 and 12 deg of the bars, both arms, ArmPoleTurn=0,0,0 for a ride, the arm lines' figures against the bones; TorsoLean 8 so the arms are solved with the bars straight
run room 14 "$KNOWN$TILT0[Room]\nBox=1\nSide=40\nFore=110\nRaysRetry=1\nLine=50\nGroundNear=25\nGroundSlope=25\nAround=1\nLineFallback=0\nSlide=1\nTilted=1\nParkTilt=1\nParkRoll=20\nParkCheck=1\nSnapNext=1\nSnapSpot=1\nSnapBest=1\nSnapDrop=250\n"   # test 41: the brought bike's spot, the controller's room asks played by the harness (modes 14 and 15 only; mode 11 is the ESP without the CMB_Room globals); test 42's spot: Box, Side, Fore and RaysRetry at their defaults, so rides can rewrite Box and RaysRetry to 0; test 44: Line and GroundNear at their defaults, so a ride can rewrite them to 0 and 60 (test 44's build); test 45's GroundSlope at its default, so a ride can rewrite it to 0 (test 45's first build); test 46's Around, LineFallback, Slide, Tilted, ParkTilt and ParkRoll at their defaults, so a ride can rewrite the five to test 45's build (the controller's PickBikeSpot played for calls); test 47's ParkCheck and SnapNext at their defaults, so rides can rewrite each to 0 (test 46's build; the controller's getting off and its navmesh snap's word played); the 2026-11-01a build's SnapSpot at its default, so a ride can rewrite it to 0 (the 2026-10-31a build; the controller's navmesh point played); the 2026-11-06a build's SnapBest and SnapDrop at their defaults, so rides can rewrite them to 0 and 100 (2026-11-02a)
run roomold 15 "$KNOWN$TILT0[Look]\nKitPreview=1\nKitPreviewLog=1\n"   # test 43: an ESP of test 42's build (the six CMB_Room globals, no CMB_RoomAskAngle) with this plugin: the eight rays as before; no [Room] section, the code's defaults; 2026-11-14a: [Look] KitPreview=1 and KitPreviewLog=1 (the defaults), so the older ESP's dormant preview is tried
run decals 18 "$KNOWN[Tilt]\nMaxRoll=10\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nBumpMax=0\nLiftRate=0\nSuspension=0\nDecalsFollow=1\nReuseByWalk=1\nPoolWait=1\nOrphanRestore=1\nRepointEveryFrame=1\nPoseCheck=1\nSeatKneeMin=52\n[Diag]\nRepointLines=3\nRiderCopies=320\n$PARTS"   # 2026-11-01a (test 47's floating rider): the decals that follow, the copy pool reused by the walk, its wait, the orphans put back, the re-points every frame and their lines, the clips' knees (logs.md 2.6's D1-D10, each under the game's smart and raw re-point); every new key at its default, so the run can rewrite each to its off value (RiderCopies to 3 and 40)
SOUND='[Sound]\nDrive=1\nLibrary=\nSetVolume=1\nFirstFade=400\nWander=0.055\nWanderTau=1.5\nWanderLevel=0.3\nWanderSteady=0.25\nWanderSmooth=0.5\nWanderMax=0.06\nShiftTime=0.55\nShiftDip=4\nShiftDipTime=0.4\nLevelScale=1\nLevelOffset=5\nIdleDb=-9\nHeardSpeed=1\nCoastFall=150\nDownRpm=1475\nClutchFall=750\nLaunchDraw=1250,1500\nLaunchRise=350\nLaunchFlare=0.5\nLaunchFlareTime=1.2\nShiftDraw=2300,3000\nDownHold=1\nDownHeld=1\nStopShift=1\nHeardStop=300\nHeardBrake=600\nStopGap=0.4\nStopHold=0.4\nStopAfter=0.3\nLoops=idle:860,on:1400,on:1700,on:2000,on:2400,on:2800,on:3300,off:1400,off:1800,off:2300,off:2800\n'   # the 2026-11-06a build's IdleDb (-9, test 49's "slightly louder"), ShiftTime 0.55, ShiftDipTime 0.4 and LaunchFlare 0.5 (with LaunchFlareTime 1.2) written so rides can rewrite them to the 2026-11-02a build's -11, 0.35, 0.24 and 0 (and IdleDb to the 2026-11-01a build's -17.2) and drop IdleDb and LaunchFlare (the code's defaults)
run sound 16 "$KNOWN[Tilt]\nTrace=1\nPivotHeight=74\nPivotForward=0\nBumpMax=0\nLiftRate=0\nSuspension=0\n$SOUND"   # test 44's build: the engine sound (mode 16 only); Drive, Library, FirstFade, Wander, LevelScale and Loops at their defaults so the run can rewrite them (test 46: SetVolume and LevelOffset too, which rides rewrite to 0 for test 45's FadeTo and levels), and test 45's HeardSpeed, CoastFall, DownRpm, ClutchFall, LaunchDraw, LaunchRise, ShiftDraw, DownHold and DownHeld, which a ride rewrites to test 44's values; test 47's WanderTau, WanderLevel, WanderSteady, WanderSmooth and ShiftDip and the 2026-10-31a build's WanderMax, which rides rewrite to test 46's; the 2026-11-01a build's ShiftDraw 2300,3000 and StopShift with its five, which rides rewrite to the 2026-10-31a build's and StopAfter to 0 (the other modes have no [Sound] section: the code's defaults, the driver idle with nothing handed over); Trace=1 for the trace line's engine word
# The 2026-10-31a build's look (mode 17 only): its own fake bike, the 28 shapes of the 2026-10-31a build under CMB_BikeWornRider (the built
# nifs' culling spheres), and the parts file of the 2026-10-31a build: 27c's CMB_BikeParts.ini (the real axles, steering
# axis, BarAngle 20) with FrontMinY 31.7 and the needle's keys the mesh tool writes from the dial (the fake's
# Grip kept: its hands sit there). RolesByName and the [Speedo], [Tail] and [Look] keys at their defaults, so the
# run can rewrite each to its off value (the look's keys are read again on getting on). [Sound] Drive=0: the brake
# light's flag with the engine's sound off.
PARTSLOOK='[Parts]\nRolesByName=1\nFrontAxle=0.38,95.83,29.86\nRearAxle=0.38,-40.45,29.94\nWheelRadius=29.86\nSteerPoint=-0.0,89.84,40.69\nSteerAxis=0.0,-0.4902,0.8716\nGrip=56.45,79.79,54.85\nFrontMinY=31.7\nBarAngle=20\nBarFullAt=45\nLampPoint=0.3,76.3,81.9\nLampAxis=0,1,0\nNeedlePoint=0.38,64.93,99.11\nNeedleAxis=0.0000,-0.8346,0.5509\nNeedleZero=0\nNeedleMax=240\nNeedlePerMph=3\n'
LOOK='[Speedo]\nNeedle=1\nScale=1.75\nTau=0.3\nBacklight=1\n[Tail]\nGlow=1\nBrake=1\nBrakeHold=0.3\n[Look]\nMirrors=1\n'
run look 17 "$KNOWN[Tilt]\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nBumpMax=0\nLiftRate=0\nSuspension=0\n$PARTSLOOK$LAMP$LOOK[Sound]\nDrive=0\n"
VIEW49='[TailLight]\nEnabled=1\nBack=8\nPitch=30\nBrakeGain=3\nBrakeBy=colour\n[View]\nEnabled=1\nLead=0\nHandoverTime=1.0\nStale=1\nEye=0\nEyeSide=1\nEyeSmooth=0.05\nEyeSmoothZ=0.25\nEyeMax=150\nStaleLines=3\nTipTime=0.4\nFovTime=0.3\nFovOffset=auto\n'   # 2026-11-01a (mode 20 only): the tail lamp's light and the first-person bike, the keys a ride rewrites at their defaults (Lead 0 for exact numbers; a ride rewrites it to 1); [Look] Cull=1 goes in through LOOK's Mirrors line; 2026-11-02a: Eye=0 so the 2026-11-01a build's checks keep their numbers (the eye's rides rewrite it to 1), EyeSide, EyeSmooth, EyeSmoothZ, EyeMax and StaleLines at their defaults so rides can rewrite them; 2026-11-06a: TipTime, FovTime and FovOffset at their defaults, likewise
run view 20 "$KNOWN[Tilt]\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nBumpMax=0\nLiftRate=0\nSuspension=0\n$PARTSLOOK$LAMP${LOOK/Mirrors=1\\n/Mirrors=1\\nCull=1\\n}$VIEW49[Sound]\nDrive=0\n"
# 2026-11-07a, the customisation build (mode 24 only): the mirrors chosen at the bike (CMB_LookCode) and the split badges' and
# the fender patch's shapes, on mode 17's look bike with its parts file, lamp and look keys, [Look] Mirrors=-1 (the new default,
# "as chosen at the bike"). After the look and view runs: PARTSLOOK and LOOK are defined with them.
run custom 24 "$KNOWN[Tilt]\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nBumpMax=0\nLiftRate=0\nSuspension=0\n$PARTSLOOK$LAMP${LOOK/Mirrors=1\\n/Mirrors=-1\\n}[Sound]\nDrive=0\n"
# The 2026-11-01a build's bike sounds and landings (mode 21 only): the water loop the fake script plays and hands over, driven through this
# mode's own Address Library (no BSStringPool::GetEntry in it: LandSoft's soft landings named from the game's own events); LandSoft,
# LandSoftNames, Land, Water, WaterSource and WaterSplash at their defaults, so the run can rewrite them (Water to 0, WaterSource to controller);
# the 2026-11-02a build's WaterGain at its default (0, the 2026-11-01a build's level), so a ride can rewrite it to -6; the 2026-11-06a build's
# WaterSpeedFull=600 and WaterCurve=1 (the 2026-11-02a build's law, so the older rides keep their numbers), which rides take out for the code's 900 and 2.
run fx 21 "$KNOWN[Tilt]\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nBumpMax=0\nLiftRate=0\nSuspension=0\n[Steer]\nLandSoft=1\nLandSoftNames=pool\n[Fx]\nLand=1\nWater=1\nWaterSource=loaded\nWaterSplash=6\nWaterGain=0\nWaterSpeedFull=600\nWaterCurve=1\n$PARTS"
exit $status
