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
# sound 125, look 67, view 176, fx 48, custom 88). The 2026-11-15a build (test 54's fixes) adds: CMB_LookOptions' 32768
# KitDefer and 65536 MountQuick (custom, + 6); the field kit's preview 400 ahead of the menu's camera at 45 degrees, Tune's
# first slider as the distance and the menu's scene and camera lines (custom, + 7); GetTranslation's answer as the camera
# root's world, the Lead by the game's frame, the first-person bike hidden until its look is on, EyeAt 0,-5,125 (view, + 11);
# the slower pull above PullFrom (launch + 4, sound + 3) and three earlier logs kept (load + 2, wrongversion + 1): expected
# custom 101, view 187, launch 17, sound 128, load 45, wrongversion 5, the rest as 2026-11-14a's: 1878 checks. The 2026-11-15b
# build (test 53's and 54's wishes) adds, from the sidestep unit: the wide sidestep (a car, a barrier, a second car in the lane,
# a quay, terrain, precombined, a tall one, popped late), SidestepSteady (the camera swept), SidestepMouseSide (kept, let go,
# handed), with PullTime (wall, 75 + 24); found by SidestepCaution's reach (caution, 24 + 1); the paused watch's own counts, P1
# made deterministic and P2 at 18 frames a second (sound, 128 + 2); the lamps' lead and the frame-rate line by the game's frame
# with the task twice a frame (view + 3). From the fpcam unit: FirstPersonState's GetRotation wrapped and its convention probed,
# the view's lean into turns, A/D turning the bike in first person, looking back while reversing (over the shoulder, through
# the back, blocked, the Pip-Boy, third person while backing, the fallback when the camera can't be turned), the look key and
# CameraPitch on a turned camera (view + 19); the four globals missing with an older ESP (roomold, 60 + 1). From the weapons
# unit: a handgun on the bike, the game's own put-away called at the script's ask after its probe, the seat watch standing back
# while a weapon is drawn, the seat poses read and a handgun out drawn on them (the right arm the game's, carried to the seat's
# shoulder; the worn bike on the seat's COM; a game frame predicted), the pose off in first person, with GunPose=0, in Any
# weapon and after the state's cross-check (arms, 68 + 19). From the fpbody unit: the rider's own body in first person ([View]
# Body: the riding pose taken in third person and put on the view bike, the head shrunk, the root's bit 0 cleared, the worn
# bike hidden, the bars' turn, the Pip-Boy, a weapon and looking back, the game re-hiding it, PreLoadGame and getting off, the
# entry's probe lines and drawn?) (view + 16). DEF59 rides every older mode at the new keys' off values: expected wall 99,
# caution 25, sound 130, view 225, roomold 61, arms 87: 1963 checks. The review of 2026-11-15b adds: a weapon drawn (the weapons
# unit's globals now in mode 20 too): no look back over the shoulder while backing (the lean kept), no third person while backing
# (and dropped when one is drawn), the look key 60 deg at most; [Steer] FirstKeysArmed: no strafe with a weapon drawn in third
# person, 0 the strafe (view + 5); a save loaded with a lower CMB_WeaponAway and a weapon drawn: no put-away, the next ask called;
# CMB_RiderGunPose written afresh over the save's (arms + 2); a sidestep in first person: SidestepMouseSide=1 over with no "kept",
# 0 let go by its own turn as 2026-11-15a (wall + 2): expected wall 101, caution 25, sound 130, view 230, roomold 61, arms 89, the
# rest as 2026-11-15a's: 1972 checks. The 2026-11-16b build (test 55's fixes) adds, from the view unit: GetTranslation's answer read
# as the camera root takes it (the player's place + it, as test 55's game gives it, one call a frame and three, the root from the
# first or the last; the world answer settled at once), the view bike in the worn bike's place while the third-person camera is at
# your eye or you are faded (and the end into first person, NearThird=0), the view's lean by the turning rate (and RollTurn=0), the
# look back's own pitch (the game moving the player's pitch, the game holding it, the 45-deg limit, LookPitch=0), FirstKeys' default
# 0.45 and the round's keys line, Parent left in its cell's box and moved straight from cell to cell with its ParentTime line (and
# ParentKeep=0) (view, 230 + 19; ViewTests59's FirstKeys rides pinned at 1). DEF60 rides every older mode at the new keys' off
# values: expected view 249 from this unit.
# The kit unit adds: the field kit menu's bike
# found by its 3D ([Look] KitFind), placed in the menu's view by the plugin ([Look] KitFit: the fit, the menu's own place put
# back, its small moves kept, the summary, Tune and KitFit=0 untouched, a parent refused) and New's 16b defaults (custom,
# 101 + 9).
# The drive unit adds: the even climb from the
# throttle's floor (the code's PullTime 8, PullFrom 0.1, LaunchFrom 0.1: Q0-Q3; LaunchTests58's P1-P3 now write 16a's PullTime 5.5)
# (launch, 17 + 4); [Sound] SpeedMap with the even climb: the gear lines at 12/23/40/49 on the dial, the engine's gears as 16a's,
# the lines' "(SpeedMap)", SpeedMap= flat, a steady 300 u/s in 3rd, a lift (M0-M6; SoundTests58's S5a-c write PullTime 5.5) (sound,
# 130 + 7); PullClimb at a log held with the boost on (C1, C2) (climb, 125 + 2). DEF60 rides every older mode at the new keys' off
# values: expected launch 21, sound 137, climb 127, the rest as 2026-11-15b's: 1985 checks with this unit alone.
# The weapons unit adds: the put-away's probe
# taking PlayerCharacter's own slot 0xC7 (its call to the getter, 0xC8 the stub; not another field's getter, not without the stub),
# the put-away's seconds counted while the game runs (a menu 5 s after the ask, CMB_RoomOptions bit 1024), both hands on the bars
# with a handgun out, the drawn weapon's 3D (off the 3D root) carried to the posed right hand and given back, a clips' jump not
# extrapolated, the root a frame ahead of the bones (the game's order: the pose read at 300 u/s, drawn at 900) and its self-check
# both ways, the still seat pose standing in at speed (arms, 89 + 11 = 100). DEF60 rides every older mode at the new keys' off
# values: expected arms 100, the rest as 2026-11-16a's (1972 + 11 = 1983 with this unit alone).
# The body unit adds: what comes with the
# rider's body in first person (the worn bike specked and its nodes hidden, the weapon's 3D under WEAPON and in the gun slot
# hidden, outfit pieces near the eye shrunk whole, the first-person 3D hidden looking back, BodyEye 0,2,-0.5, the lines without
# a "drawn?" verdict; each key off as 2026-11-16a) (view, 230 + 14): view 244, 1986 checks with the rest as 2026-11-15b's.
# The merged 2026-11-16b with its review's fixes (the first-person 3D given back after a camera neither first nor third person and
# after getting off in one, NearThird's speck with BodyWorn, CameraPlace settled on a later call in frames with fewer calls: view
# + 4; [View] BodyFollowCamera with CameraPlace in the fake's order and test 55's, KitFit past unreadable children and an unwritable
# shape: custom + 4) expects view 267, arms 100, custom 114, launch 21, sound 137, climb 127, the rest as 5b04dbf's: 2046 checks.
# The 2026-11-17a drive unit (test 56: "takeoff is a tad too slow"; "shifting down when being slowed down or stopping is sometimes weird, not
# natural") adds: [Steer] LaunchFrom's 0.14, the even climb from there (launch, 21 + 1: R1; Q1-Q2 now write 16b's 0.1); in the fake's game as
# test 56's (its top 935, its pick-up 0.35 s behind the ask): test 56's pull and stop reproduced at 16b's values, the take-off a tad quicker
# with each gear's sound as before, a stop from the top, from a cruise and braked stepping down a gear at a time at the pull's bands ([Sound]
# DownBands, DownBlend, HeardStop 900, HeardBrake 1500) with its own line, and a lift with the speed holding as before (sound, 137 + 9: N0-N8;
# SoundTests60's M1-M6 now write 16b's LaunchFrom 0.1). DEF61 rides every older mode at the new keys' off values: launch 22, sound 146, the
# rest as ddf7b1e's: 2056 checks with this unit alone.
# The 2026-11-17a build (test 56's fixes) adds, from the weapons unit: the weapon state's cross-check across the Pip-Boy (a
# holster with the script lagging, 5 s paused: no switch-off), its recovery (6 s of disagreement: off until the two agree,
# then back on) and the pose after them and after a second pause, standing and at 300 u/s (C1-C3); CMB_RoomOptions bits 2048
# and 4096 (R1); the player's slot 0xC9 wrapped: a rifle's draw refused, a pistol's passed on, the put-away still the game's
# own (K1, K5); number keys with nothing out (the rifle holstered, the pipe pistol drawn: K2), with a pistol out (held back,
# put away, UseQuickkeyItem: the rifle holstered; its off value the game's swap: K3), and the equip a few frames after the
# draw (refused, given back for the pipe pistol, not for the pipe rifle: K4); the hands' node-less fingers not judged again
# at a weapon's hold (S1), a hand whose skin arrays the game rebuilt held again (S2), a weapon's two copies named (S3)
# (arms, 100 + 12 = 112). DEF61 rides every older mode at the new keys' off values: 2058 checks with this unit alone.
# The 2026-11-17a body unit (test 56's 1C, 56-23 and the Z look) adds: the worn bike drawn again in third person after a showing in the
# fake game's own list of what it draws (made afresh when ScenegraphChange is set: no node's bit 0 with the body), its state's two lines,
# NearThird's zoom out, BodyNodes=1's crazy frog reproduced, FrameTilt's write every task stopped, the camera in front of the neck
# (BodyEye 0,6,-3, BodyLeanMax 40), the first-person arms hidden at the look key's 30 deg and given back, a weapon's and BodyArmsLook=0's
# 90 (view, 267 + 10 = 277): 2056 checks with the rest as 2046's.
# 2026-11-17a, the kit unit (test 56's 56-30 to 56-32 and the wall) adds: the field kit's bike held about its centre ([Look] KitHold:
# at 16b's fit with the menu's turn, MenuControls' input read, the wheel's zoom about the centre and not with the cursor on the lists,
# the drag's turn without a roll and not begun on the lists, the menu's own turn taken as heading, a new model at the visit's view
# and zoom, the summary), a view per slot (KitSlotView: eased, each slot's view, the drag kept, the item select state; the menu's
# keyword and the mods' names when the slot objects say nothing; 0 one view), KitHold=0's menu turn left alone and KitRoom's
# CMB_LookOptions 131072 (custom, 114 + 12: K25-K36); the field kit's spot asked about (CMB_RoomAskKind 4: room, a fence between,
# a wall beside it, KitRoom=0) (room, 149 + 4: R1-R4). DEF61 rides every older mode at the new keys' off values: expected custom
# 126, room 153, the rest as ddf7b1e's: 2062 checks with this unit alone.
# The 2026-11-17a build (test 56's fixes) adds, from the cam unit: test 56's camera (the root eased toward your place + the answer,
# three calls a frame, your 3D a frame behind your place, 920 u/s): the eased reading settled, no off line, EyeAt at the camera and
# never a gap's worth off it through the entry, the lock line's CameraEase part under the Lead's; the root at your 3D + the answer
# exactly (a fall-back, the 3D's settled); a nudge no reading sees (the fall-back and the loud line, nothing moved, settled again
# without it); a handover near the camera in third person with the old one drawn till its end, and NearHandover=0 (view, 267 + 6);
# the same camera with your body and your place bobbing (the hand on its grip, BodyFollowCamera moving), and CameraEase=0's
# 2026-11-16b off (custom, 114 + 2). DEF61 rides every older mode at the new keys' off values: view 273, custom 116, 2054 checks with this unit alone.
# The merged 2026-11-17a (the cam, body, weapons, kit and drive units, with the plates' and badges' art) expects view 283 (267 + 6 cam
# + 10 body), custom 128 (114 + 2 cam + 12 kit), arms 116 (112 + 4 of its review's weapons fixes: a grenade's key leaves the
# pistol out, a newer key ends the window, no keyword read draws, UseQuickkeyItem's weapon looked at: W1-W4), room 157 (153 + 4: its
# review's item 4, the field kit's bench asked about at its own place, CMB_RoomAskKind 5, and the ring's rays towards the bike not
# cast: R5-R8), sound 146, launch 22, the rest as ddf7b1e's: 2110 checks.
# 2026-11-21a, the kit unit (test 57's 1B and 1C, art build B's slots) adds: the field kit's view on every model the menu has (KitFollow:
# after E on Plate text the menu's half-degree turn a half-degree turn, not 2026-11-17a's 119, and its six new models at the visit's view
# and zoom two frames on; its own 5-degree turn of the shown model taken, a 40-degree jump of another written over; the models line), the
# slot's read settled (KitSlotSettle: the highlight walking the list a row every other frame turns nothing, the slot it rests on once;
# the counts), the wheel on the lists zooming and kept from the menu with the chain put back (KitMouse, KitWheelOwn), a drag begun beside
# the lists turning and one on them not (KitListBox), art build B's Wear, Front fender and Headlamp by their attach points' editor IDs and
# by their mods' names (KitNewSlots), and the off values (custom, 128 + 12: K37-K48). DEF62 rides every older mode at the new keys' off
# values: 2122 checks with this unit alone.
# The 2026-11-21a third unit (test 57's 1A: the bike, and sometimes you, not drawn in third person after your body) adds, with the fake
# game's list keeping a worn shape that was a speck when it was made (BodyTests63, after BodyTests62Worn): 17a's loss and its return at
# the game's own change (T1), BodyRedraw's mark after a showing (T2), after NearThird's stand-in (T3), after a showing ended in first
# person by a weapon (T4), BodyRedrawHide's hidden frame where the game works bit 29 off only after one (T5) and BodyRedrawHide=0's mark
# taken back (T6), and ThirdWhere's four lines with the list read before and after the mark (T7) (view, 283 + 7). DEF62 rides every
# older mode at the new keys' off values: view 290, 2117 checks with this unit alone.
# The 2026-11-21a weapons unit (test 57's 1D, weapons in third person) adds: CMB_RoomOptions bit 8192 (GunNoteSure) and the keys' line
# (N1); the hand's weapon 3D (the biped's object 41 under RArm_Hand) a speck while holstered, drawn when drawn, its line, and GunHandHide=0
# (H1); a holster mod's copy and a biped 3D hung off the hand drawn (H2, guards); a posed handgun put away in third person with the
# clips standing on: the pose kept till they sit, and GunAwayKeep=0 (A1); kept GunAwayKeep at most (A2); the seat poses kept over the
# worn bike's swap in first person with a handgun out, posed at once back in third person, and GunSeatKeep=0 (E1) (arms, 116 + 6 =
# 122). DEF62 rides every older mode at the new keys' off values: 2116 checks with this unit alone.
# 2026-11-21a, the drive unit (test 57: "rolling distance should be twice as much as is now, with gradual slow down"; the gears in even
# steps, the user's pick) adds, in the fake's game as test 57's (its top 935, its pick-up 0.25 s behind the ask at 300 u/s^2 at most and
# 110 under 80 u/s; the coast's wait on one clock, RunFramesUntil63): CoastDrag's settings line off (O0); test 57's pull and coast
# reproduced at 2026-11-17a's values (the up-shifts at 12, 25, 43, 51 on the dial; 1203 u and 2.3 s from the key, 5-4 at 810, 4-3 631,
# 3-2 398, 2-1 169) (O1, O2); the code's defaults: the up-shifts at 12, 24, 36, 46 on the dial, 1.47, 1.84, 2.00, 1.70 s apart, each
# gear's rpm (O3, O4); the coast about twice as long and gradual ([Steer] CoastDrag 270,90), its line and trace word (O5, O6); its
# down-shifts one gear at a time in the new bands ([Sound] DownBands 170,380,600,780) over the longer coast (O7); the brake's stop as
# with CoastDrag= (O8); CoastDrag=450,450 = Coast 2, a value not understood (O9); from a cruise at 600 (O10); a lift at a steady 300
# (O11) (sound, 146 + 12 = 158; the older sound checks that took the code's gear table write 2026-11-17a's: SndGears17a63). DEF62
# rides every older mode at the new key's off value: 2122 checks with this unit alone.
# 2026-11-21a, the look unit (test 57: the free look on the right mouse button, the game's aim blocked while riding, the look in
# third person) adds: the round's keys line and the AttackBlockHandler's slots 1 and 8 wrapped (L1); the right button kept from the
# game in first person with a pistol out (no aim, no slowing, the release line; the left click still fires: L2) and the look on it
# (L3); AimBlock=0: the aim passed, the bike slowed by the fake's aim and the AimWatch line (L4); the look by the game's own button
# events alone (L5); the four keys off: 2026-11-17a's (L6); in third person the camera's look column learned (T1), the bike held
# while the mouse swings the camera (T2, T4), no state float learned: the bike's line kept till the camera is back (T3), ThirdPersonState
# +0xF4 learned and eased back behind (T5), a target/current pair written together (T5b), the side keys the plugin's with no strafe
# (T6), first person ending it at once (T7), an ease the camera doesn't follow: stopped and off (T8), LookThird=0 (T9) (view, 283 +
# 16). DEF62 rides every older mode at the new keys' off values: view 299, the rest as 24b2368's: 2126 checks with this unit alone.
# The merged 2026-11-21a (the third, look, kit, weapons and drive units, with the shells', wear's, art2d's and table's art and
# records) expects view 308 (283 + 7 third + 16 look + 2 of its review's look fixes: a release with nothing to ease keeps the
# bike's line till the camera is back within 20 deg (W1; T3 and T8 changed), the look column learned along the camera's line to
# you (C1)), custom 141 (128 + 12 kit + 1 of its review's item 3: a frame of wheel events only kept from the menu in place, the
# game's slot 0 still handed the chain: K49), arms 123 (116 + 6 weapons + 1 of its review's item 5: GunHandHide on a frame the
# rider is otherwise idle writes the hand's weapon parts alone: H3), sound 158 (146 + 12 drive), the rest as 24b2368's: 2167
# checks.
# 2026-11-22a, the aim unit (test 58: the aim's handler a struct, .?AU..., never wrapped; "Z in 3rd person doesn't work") adds: the
# fake's AttackBlockHandler and its bases now structs as 1.11.240's (L1, L2, L4 and L5 need the struct's name); the Pip-Boy key's
# event passed while the aim's press is kept (P1); the plugin's own third-person orbit on the game's own riding camera (the mouse
# turning you, the camera kept behind): the camera 120 deg round you and held with the bike on its line, its gain learned riding
# (O1), eased back behind (O2), the look key (Left Alt) the same (O3), 60 deg with a weapon (O4), against a pull three times as
# hard (O5), LookOrbit=0's 2026-11-21a (O6), a camera the writes never move: off for the session (O7); 2026-11-21a's third-person
# checks (W1, C1, T1-T9) ride LookOrbit=0 (view, 308 + 8). DEF63 rides every older mode at the key's off value: view 316, the rest
# as fbe9a7c's: 2175 checks with this unit alone.
# 2026-11-22a, the kit unit (test 58's 1D, art build C's slots) adds: the bike the menu's renderer draws held alone (KitDrawn: test 58's
# three bikes, the loaded one, the slot objects' one and the renderer's screen-attached one: the third at the view, the other two left;
# a new drawn bike at the view two frames on, one under an identity root; the renderer's name field not the manager's: 21a's models and
# why), the wheel's down notches of -1 zooming out (KitWheelDown), the wheel over the lists passed to them and zooming off them
# (KitWheelLists), Paint condition's view by its attach point and its mods and the front fender no slot (KitSlots22), the visit's line,
# and the off values (custom, 141 + 9: K50-K58). DEF63 rides every older mode at the new keys' off values: 2176 checks with this unit
# alone.
# 2026-11-22a, the drive unit (test 58: "overall it feels more sluggish"; the up-shifts at 11, 25, 32 and 43 on the dial; two coasts' lines
# that counted a menu's time) adds, in the fake's game as test 58's cold starts (its pick-up 0.35 s behind the ask at 300 u/s^2 at most and
# 110 under 120 u/s): UpBands' and MenuKeep's settings lines off (P0); test 58's pull from rest and its early shifts (a pull up a long climb)
# reproduced at 2026-11-21a's values (P1, P2); [Sound] UpBands: the same climb's shifts at the bands (P3), from rest at 11, 24, 36, 46 on the
# dial (P4), a pull begun rolling (P5), a steady speed's gears as before (P6); [Steer] MenuKeep: a menu in a pull, no cut at the close (P7),
# in a coast, the coast's line on the riding time (P8) (sound, 158 + 9 = 167). DEF63 rides every older mode at the new keys' off values:
# 2176 checks with this unit alone.
# The 2026-11-22a apply unit (test 58's 1A, the crashes at getting on after a field kit change, and 1C, the Wear on the parked and the
# worn bike) adds: CMB_LookOptions' 262144 [Look] ParkedSwapHold and 524288 OverlayRuntime, each alone and both, with the 2026-11-22a
# look line once per change (AP1-AP4); [Diag] LensLine: the worn bike's lens at the mount (its 3D, its property's file, its diffuse
# texture), a swap mid-ride's "changed" line, nothing more while nothing changes, the mount's line again at the next getting on, none
# with LensLine=0 (AP5-AP8) (custom, 141 + 9). DEF63 rides every older mode at the new keys' off values: custom 150, the rest as
# fbe9a7c's: 2176 checks with this unit alone.
# 2026-11-22a, the parked unit (test 58: "having one tire in the ground"; "leaning a bit on sidestand/kickstand") adds: [Room] ParkFit's
# and ParkStand's line and CMB_RoomOptions 32768 (P1); the controller's ask about the parked bike's own place (kind 6) answered from the
# ground under its tyres, its sides, its middle and its stand's foot, the answer applied as the controller applies it and the tyres' and
# the foot's contacts held to the fake's ground: flat ground (P2), test 58's 12:51:43 slope, pitch 5.4 and roll -12.4, the bike put 2
# under it (P3), a crest under the bike (P4), a sharper one under its frame, the bike raised (P5), a curb under the foot (P6) and one
# too high, the lean held to 3 (P7), no ground under the front tyre (P8), the bike's own 3D passed (P9), ParkStand= upright (P10),
# ParkFit=0: 2026-11-21a (P11) (room, 157 + 11). DEF63 rides every older mode at the new keys' off values: room 168, the rest as
# fbe9a7c's: 2178 checks with this unit alone.
# The 2026-11-22a attach unit (test 58's 1E: what other mods hang off the rider's skeleton follows her body) on fbe9a7c expects arms 128
# (123 + 5: a holster mod's deep copy of the posed hand's shape held from that shape's own transform (AU1), the keys' line (AN1), a
# backpack's strap under a node named as the left hand moved as the body's skin at SPINE1 (AB1), [Diag] AttachWhere's lines (AW1),
# AttachHide's specks (AH1)); DEF63 rides every older mode at the new keys' off values: the rest as fbe9a7c's: 2172 checks.
# The merged 2026-11-22a (the apply, aim, kit, attach, drive and parked units, with the shells', wear's, art2d's and table's art
# and records) expects view 317 (308 + 8 aim + 1 of its review's item 6: AimStruct=0 leaves the struct-named handler unwrapped:
# A0), custom 160 (141 + 9 kit + 9 apply + 1 of its review's apply fixes: [Look] OverlayParked, the parked half of OverlayRuntime,
# CMB_LookOptions 1048576, default 0 (AP9; AP1-AP4's words name the worn bike's half)), arms 128 (123 + 5 attach), sound 167 (158 + 9
# drive), room 176 (157 + 11 parked + 8 of its review's items 7 and 8: a car's hood, a ledge, a crate, a drop and a shelf beside or over
# the bike not read as its ground, an ask with no heading leaning by the stand: P12-P19; P8's Clear 8.59), the rest as fbe9a7c's: 2228
# checks.
# 2026-11-23a, the kit unit (test 59's 1F) adds, with the game's order modelled (the plugin's frame task, then the menu's own update
# through ExamineMenu's vtable slots 4 and 5, then the draw sampled): five options, each a frame with no drawn bike and a frame the
# menu attaches a new one at its own pose: none drawn off the view with KitLate (the late pass right after AdvanceMovie), none with
# KitPrePlace (the new one in the loaded list a frame before it's attached), one an option with both 0 (test 59's flash), and the
# visits' lines (custom, 160 + 5: K59-K63). DEF64 rides every older mode at the new keys' off values: 2233 checks with this unit alone.
# The 2026-11-23a drive unit (test 59: "still feels a bit sluggish on take-off"; the user's pick: 0.3 of the top in about 1.5 s, half in
# about 2.8, the gears at about 12, 24, 36, 46 on the dial) on 131f6b4 adds: [Steer] LaunchFrom's default 0.25 (22a 0.14) at the code's
# defaults, the throttle 0.25 + 0.1125 a second, one launch line "(the throttle from 0.25 ...)" (launch, 22 + 1: L1); the fake's game as
# test 59's (its follow slower at small inputs, FakeGameFrame's g_fakeTauLo65), test 59's take-off from a stand reproduced at 22a's values
# (T1), this build's: the settings lines (T0), quicker from a stand (T2) and from a start within seconds of moving (T3) with the up-shifts
# at the bands and their rpm ([Sound] HeardRiseGears' default 2.1,1.35,1,1,1, 22a 2,0.86,0.8,1,1), the coast and the brake as 22a's (T4,
# T5) (sound, 167 + 6). No new key, no DEF64 entry: the two changed defaults are pinned for every older mode already (DEF60's
# LaunchFrom=0.25 and DEF54's HeardRiseGears=1,1,1,1, mode 23 names its own LaunchFrom), and the older checks that took the code's
# (LaunchTests62's R1, SoundTests62's N3-N8, SoundTests63's, SoundTests64's) write 22a's (SndDrive22a65, SndRise22a65): 2235 checks
# with this unit alone.
# 2026-11-23a, test 59's fixes, the look unit's: [View] LookOrbitGame (each frame of a held third-person look the game's own swing
# of its camera told from the plugin's need: with no weapon drawn the camera left to the game, nothing written; with one, the
# orbit) and LookRecover (no check of the look switches anything off for the session: a hold not followed ends that hold's orbit,
# an ease not followed watches the game's own camera back, a camera behind already ends the ease at once), on test 59's riding
# camera (the fake's g_v63Field 5: the game's own free rotation with no weapon drawn, twice the heading's rate a unit of the look
# input, its writes never shown, back behind over 0.1 s once the mouse is still; with one drawn test 58's): the camera the game's
# own swing, not followed never (LR1), the ease's writes not shown and the game's return watched to behind (LR1b), the plugin's
# 60 deg with the 10mm drawn after a hold without (LR2), a camera behind already ending the orbit's ease at once (LR3), the
# 2026-11-21a ease watching the game's faster return (LR4), a hold not followed ending that hold only (LR5), LookOrbitGame=0: test
# 59's 95 against 48 (LR0) (view, 317 + 7). DEF64 rides every older mode at the new keys' off values: view 324, the rest as
# 131f6b4's: 2235 checks with this unit alone.
# The 2026-11-23a grip unit (test 59's 59-22: "she still holds the gun with both hands"; the user's pick, the left hand back on the
# left grip with a pistol drawn, the gun held one-handed) on 131f6b4 expects arms 133 (128 + 5: the keys' line at DEF64 (OH0); [Tilt]
# GunOneHand with GunBothBars=1: the right hand on the seat pose's wrist moved by GunHoldAt, the body and the left arm as the
# holstered ride drew them (OH1), the pistol's +Y turned onto the bike's heading from a seated fist 30 deg off (OH2), back on its grip
# at the put-away (OH3), GunOneHand=0: 2026-11-22a's both hands on the bars (OH4)) and view 326 (317 + 9: the keys' line (GP0);
# [View] BodyGunGrip: a handgun drawn in first person, your body still shown, its line (GP1), its left hand where it was, its right
# arm a speck (GP2), the first-person 3D's skin on a copy with its left-arm bones a speck, its right-arm bone and a right-arm-only
# shape the game's (GP3), given back at the put-away (GP4), the Pip-Boy (GP5), a weapon that isn't a handgun (GP6), getting off
# (GP7), BodyGunGrip=0 as 2026-11-22a (GP8)); DEF64 rides every older mode at the new keys' off values: the rest as 131f6b4's:
# 2242 checks.
# The 2026-11-23a overlay unit (test 59's 1A: the Wear and Paint condition only where F4SE's runtime swap went on; the worn bike's at 5 of
# 21 getting-ons, the parked bike's never at a getting off) adds: CMB_LookOptions' 2097152 [Look] OverlayEvery and 4194304 OverlayQuick,
# each alone and both, with the 2026-11-23a look line (AO1-AO4); OverlayParked's default 1 (AO5) (custom, 160 + 5). DEF64 rides every
# older mode at the new keys' off values: custom 165, the rest as 131f6b4's: 2233 checks with this unit alone.
# The 2026-11-23a parked unit (test 59's 1D and 1E: the bike beside you at a getting off, its lean from upright, its tyres, getting
# on's hide) on 131f6b4 expects room 187 (176 + 11: Q1 the keys' line and bits, Q2-Q4 ParkLean (flat, test 59's 20:25:18 rise toward
# the stand, its swim's fall), Q5-Q6 ParkTyres (a thing over the rear tyre's contact, a step under the front wheel's edge), Q7-Q10
# ParkBeside's kind 7 (their right, a wall: their left, walls both sides: none, an actor: their left), Q11 the four off), the rest as
# 131f6b4's: 2239 checks.
# The review of the 2026-11-23a grip unit (finding 2: BodyGunGrip's list of first-person shapes could run past its 24 when the
# first-person 3D was replaced while held, the old shapes left on our copies) adds GP9 (the first-person 3D replaced while held, a
# new root with 25 skinned shapes: the old given back first, its line, 24 of the new held, one left as it is) and GP10 (the new
# shapes all on their own data after getting off) (view + 2: the grip unit's 326 -> 328; with the look unit's 7, 333 -> 335).
# The parked unit's review fixes (t65-fixp, on t65-merge ea423be): room 189 (187 + 2: Q12 a side with room that the fit rejects is no
# room, the other side taken; Q13 ParkFit=0's kind 7 answers as a checked spot's, ParkTilt's tilt and the ground's offset, for the
# controller's settle); every other mode as ea423be's.
# The 2026-11-23a attach unit (test 59's 1C: the thigh holster's copies never attachments; the user's pick: no item's use clip in
# third person) on 131f6b4 expects arms 139 (128 + 11): test 59's tree ('Pelvis' < 'RLeg_Thigh', the skin on 'RLeg_Thigh_skin', the
# holster mod's 'WeaponPistolUp' on the thigh): the keys' line (AS0), the holster an attachment of 'RLeg_Thigh' (AS1), its copy
# carried with the thigh while posed (AS2), AttachWhere through 'RLeg_Thigh_skin' (AS3), AttachFresh's stale shape (AS4); an
# item's props right after the Pip-Boy (its item applied in the menu) cut at their frame in third person at speed (UN1) and slow
# (UN2), a potion's key under QuickUseAbove handed to the script (UN3), the ride's line (UN6), first person and UseNoClip=0 as
# before (UN4/UN5), and (its review's finding 4) a clip with no cause known whose item comes at its own event 1.25 s in, left to
# play till then and cut at it (UN7). DEF64 rides every older mode at the new keys' off values: the rest as 131f6b4's: 2239 checks.
# The review of 2026-11-23a, finding 3 (the kit unit's): KitPrePlace reads only the loaded list's live entries (their stride from
# two fields an entry, the span readable first) and writes only models still referenced: the list 0x280 long before an unreadable
# page, three live entries 0xA0 apart and a stale fourth past count: the one with no reference and the stale one left (K64) (custom
# + 1: 170 -> 171 on the merged build).
# The merged 2026-11-23a (the kit, drive, look, grip, overlay, parked and attach units, with the wear's and art2d's art, and its
# review's fixes: grip's GP9-GP10, parked's Q12-Q13, kit's K64, attach's UN7; overlay's fixes are the scripts' alone) expects view
# 335 (317 + 7 look + 9 grip + 2 of its review's finding 2), custom 171 (160 + 5 kit + 5 overlay + 1 of its review's finding 3),
# arms 145 (128 + 5 grip + 11 attach, its review's finding 4 among them, + 1 of the second review's: UN8), sound 173 (167 + 6 drive),
# launch 23 (22 + 1 drive), room 189 (176 + 11 parked + 2 of its review's finding 7), the rest as 131f6b4's: 2294 checks.
# The second review of the shipped 2026-11-23a (7cf1cbf), for 2026-11-23b (the attach unit's UseNoClip): the Pip-Boy window read from
# the UI's menu stack (the PipboyMenu on it), cancelled by the Favourites menu or any other menu since, and 1.5 s long, not 4: the
# Pip-Boy closed with nothing used, the Favourites menu within the window, then a clip whose item comes at its own event 1.25 s in:
# left to play and cut at the item (UN8; 7cf1cbf: cut at the props, the heal lost) (arms 144 -> 145).
# The 2026-11-24a grip unit (test 60's 1C: a second left hand still on the pistol in first person, BodyGunGrip having shrunk only the
# 3 bones whose node has a left-arm name) on bca9231 expects view 348 (335 + 13): the keys' line at DEF65 (GN0); test 60's
# first-person 3D (a 36-bone NakedHands with only its two hands' nodes, sleeves, a left-only leather piece with no node at all, a
# right band, a piece bound as the third-person body; a T-pose bind, test 60's two-handed grip 6.6 apart, the left fingers nearer the
# right hand): every left bone with no node judged by its bind, the pieces whole, the band and the right bones the game's (GN1); the
# hold's first 2 frames about each joint, then one point at the first-person left shoulder (GN2); GunGripBones' lines (GN3); a decal
# cloned from a held skin: 3 s of the 0.5 s look again on the fixed clock with no give-back (GN4) and given back onto its shape's own
# data at the put-away (GN5); a bind with the hands 8 apart: nothing of it judged (GN6); third person and back (GN7), a new
# first-person 3D (GN8), getting off (GN9); the off values as 2026-11-23b (GN10), BodyGunGripSpeck=joint (GN11), Nodeless=0 with
# the shoulder (GN12). DEF65 rides every older mode at the new keys' off values: the rest as bca9231's: 2307 checks.
# Its review's fixes (view + 6: 348 -> 354): the point shape by shape (finding 1): a piece that keeps a bone with no side as the
# game's (the hands too close in its bind: GN6; a bone the judge found no side for: GN13; with Nodeless=0 every piece with a bone
# without a node: GN12) is shrunk about each bone's own joint, and a frame in which one shrunk bone's transform won't read puts its
# whole piece about its joints (GN14): a vertex weighted half to a shrunk bone and half to the other lies within 5 of where the game
# draws it or of the point, never half way to the shoulder (56834cd: a sliver from the pistol's grip to the shoulder); a node and a
# slot at world scale 2 and a piece's entries at scale 1.5 (GN15); no 'LArm_UpperArm' node: the point a held bone (GN16); a decal
# made and the pistol put away within 0.5 s, on the fixed clock: found at the give-back and put on its shape's own data, and a rider
# hold that needs a copy of 36 bones then takes our copy free of it (GN17; finding 2); a decal, then a new first-person 3D: our copy
# kept out of the pool while the decal is on it, the rider's hold given another, back in the pool once the decal goes (GN18): 2313.
# The 2026-11-24a plog unit (test 60's small faults) on bca9231 expects view 345 (335 + 10: NearThird's off threshold NearThirdOff, on at
# 53 from your eye, still at 67, over at 88 (NT1), the camera 57 and 67 from your eye a frame apart (NT2), NearThirdOff=0 (NT3); NearDrawEvery's draw
# lines once a stand-in, four stand-ins in 2.8 s (ND1), one held 12 s (ND2), NearDrawEvery=0 (ND3); the keys' line (NT0); a lock line
# with CameraEase not settled, "none" for its empty window's figures, no nan in the mode's camera and lock lines (LN1); the gun state 5
# named as the game's table has it in the aim's release line (GN1) and the draw's trace (GN2); L2's and L4's lines read the new words),
# fx 50 (48 + 2: the ride's start with the loaded data's surface -FLT_MAX and the controller's word -4.86e36 (FW1), into water (FW2)),
# custom 176 (171 + 5: KitLate's default 0 and KitGuard's line (KG1), the menu's update on a thread of its own held inside its call: the
# task's work, after its 500-us wait, skipped (KG2), the update stuck inside its call: the guard let go after 1 s of the fake's fixed clock
# (KG3), KitGuard=0 KitLate=1 as 2026-11-23b with test 60's "0 placed ... 1 on another thread" (KG4), the update on the task's own thread
# with KitPrePlace (KG5)), the rest as bca9231's: 2311 checks. Its review's fix: custom 177 (+ KG6: KG3's stuck update with the task's
# own thread's AdvanceMovie and PreDisplay in and out every frame: the guard still lets go after 1 s): 2312 checks.
# The 2026-11-24a sfix unit (test 60's small faults) on bca9231 expects riderinplace 20 (18 + 2: [Diag] APWatch=1 the watch and CMB_RoomOptions'
# 4194304 clear (APW0), the key taken out, its new default 0: no watch line, its line, 4194304 set for the controller's AP lines (APW1)), look 72
# (67 + 5: [Look] KitQuickExit's and EquipLate's line and bits (CMB_LookOptions 8388608, CMB_RoomOptions 8388608: SX0, SX1), test 60's slow
# getting on (the camera alone 5.5 s, then the slope and the tilt together) with no "riding with CMB_TiltLive at 0" line (SX2), the slope live
# and the tilt at 0 still said (SX3), EquipLate=0's false line (SX4)) and fx 55 (48 + 7: [Sound] LandOnce on test 60's cue 83 (the fall
# 178 a second, level 0.38) and on hops at rest (level 0) with test 60's cues, SyncLeft at +0.076 s and JumpDown at +0.6 s: LandOnce=0 two
# plays, both heard (LO0), the default 1 one play, CMB_FxAir 2 till the answer + 1, its words on the "played" line (LO1), a late first
# JumpDown and CMB_FxAir back to 2 (LO2), at rest the level-0 line's words and a new hop within the hold its own flight (LO3), the key's line
# (LO4), the script's JumpDown before the plugin's landing frame, on cue 83's hop (LO5) and at rest (LO6): LandTouch's two answers). DEF65
# rides every older mode at the new keys' off values (APWatch at its old default 1): 2308 checks with this unit alone.
# The 2026-11-24a park unit (test 60's 1B: a fast getting off left the bike 400-550 behind; 1A: drawn with no collision after quick
# series on one spot; parkA2's lean note; CMB_RoomOptions not written at a load) on bca9231 expects room 218 (189 + 29). Mode 14's
# ParkStopTests66 on the fake's fixed clock, the fake ridden by its keys and the getting off's fade played (g_fader66: the handlers'
# slots silent, the movement update not): the keys' line and CMB_RoomOptions 1048576 (S1); at 900 a second under the fade the kind 7
# ask held, answered once she has stopped (the game's own stop 0.1 s), beside where she stopped (S2), still till the ride's end with W
# held (S3); ParkHold: still after it with W held, the keys back 0.2 s after W is let go (S4), or at its 0.6 s bound (S5); a run-on the
# input can't stop answered at ParkStop's bound (S6); at rest at once (S7); a newer ask drops it (S8); the 5 s let-go (S9); a load
# (S10); no fade (AutoDismount's, EmergencyReset's), W held: held by AfterInput's own branch, answered once stopped, "the input's
# handlers running" (S12, its review's finding 2); both off: 2026-11-23b, test 60's 1B reproduced, 675 past the ask (S11);
# CMB_RoomOptions written again at a load and a new game (L1, L2). ParkSolidTests66: kind 8 at the parked bike's own place: its 3D
# there (K1), not there (K2: test 60's state), another reference's (K3), a roof over it looked under (K4, K5), an actor over it
# passed (K6), the rays not working (K7), a repair played (K8), the reference watched (K9), ParkSolid=0 (K10). ParkLeanTests66: the
# leaned outline's nearest (T1), test 60's 14:28:31 pitch: the lean less (T2), a slim actor at the leaned top past the guard's look:
# the lean less (T3), no lean clears: 10 farther out (T4), ParkLeanClear=0 (T5). S11, K10 and T5 (the off values) pass on bca9231's
# DLL; the other 26 fail there. DEF65 rides every older mode at the new keys' off values: the rest as bca9231's: 2323 checks with this
# unit alone.
# The 2026-11-24a fit unit (test 60's T60-5 "is the foot in the air?": seven fits held to 20 with the stand's foot 0.9-13 over its
# ground, two on flat ground; its four getting offs by wrecked cars and rubble parked on the track's spot nose-up 26 or pitched -18;
# its swim's bike held hidden 16 s by a body with no capsule) on bca9231 expects room 213 (189 + 24, FitTests67): F1 the keys' line
# and CMB_RoomOptions 16384 and 524288; ParkFootFix: F2 test 60's 14:32:08 (ParkBeside, a crack 4 wide under the stand's foot, the
# landscape 5.4 under the slab: 8.6 on the slab, its pad's words), F3 a weed lying 2 over the ground round the foot (on 0.5 past it,
# not 4), F4 test 60's 14:58:21 (litter under the middle and the foot, the surface under it 7 down: the middle 0.0, 8.6), F5 the parked
# bike's own low part passed, F6 ParkFootFix=0 gives 23b's 20 (the off value's own check); ParkFallbackSearch's kind 9: F7 flat,
# fitted, F8 test 60's 14:28:31 as ask 838 had it (pitch 11.8, a ridge: the sides 19.6 and 11.2 under the middle, set aside, the
# foot's ground 9.9 under the tyres' line, the ground falling toward it: refused, "the lean it wants, 41.5 ... the stand's foot 5.9
# over its ground there (over 4)", the pad's right and left points not judged by a slope across set level; kind 6 there held to 20,
# no pad words), F17 a uniform cross-slope of 28.4 (F8 till the unit's review: both sides on one slope, refused, 41.3 and 6.0), F16
# test 60's 14:53:17 (ask 926: the front tyre's contact under a thing 13.2 high with no ground under it, raised 9.9 onto a step 8
# behind it, the foot 1.3 over at 20: refused, "the front tyre's contact under something 13.2 over the line ... (on a thing)"; kind 6
# fitted as 23b's ParkTyres), F9 the front tyre on a block 40 high: refused (over 24), F10 the two keys 0: neither bit, kind 9 a
# spot's answer (the off values' own check), F15 the scope's case: a car on both sides (ParkBeside none), the controller's fallback
# search played (ParkSearchPlayed67, as the script's ParkSearchSpots line for line): its first spot's (120 behind, across) fit
# refused (the foot over a hole), spot 3 (150 ahead, 60 right) taken, the 4th asked; the controller's ParkChecked played
# (ParkCheckedPlayed67) in a corridor (walls 45 either side, a short wall in the track spot's box): F18 the track's spot no room,
# spot 11 (220 behind) room but its fit refused, no other spot with room: spot 11 taken as 23b took it (the unit's review; the search
# before it: none, the track's spot inside the wall), F22 the same with no black (knocked off, a reset): the 4 AroundSpots only,
# F23 the search's time played (0.35 s an ask: out of its 2 s before spot 11's fit, spot 11 the first with room; 0.7 s: out of it
# after 3, the track's spot as before), F24 a spot not checked ends the search (after spot 11: spot 11; before it: as before), F19
# the track's spot room as asked, its fit refused, the search: spot 11 fitted, F20 the same with spot 11 walled: none, the track's
# spot as before, F21 Slide=1: the track's spot slid 40 forward, its fit there refused, the search none: the slid spot as before;
# GuardStuckMove (the guard's
# kind 2 every 0.75 s on the fixed clock): F11 test 60's swim, a body with no capsule: CMB_RoomGround 1 on the -n answer from 2 s on,
# F12 an actor's capsule unmoving: the same, F13 the capsule moving 20 an ask, then standing: marked only 2 s after it stopped, F14
# GuardStuckMove=0: never (the off value's own check). F1-F5, F7-F9, F11-F13, F15-F22 and F24 fail on bca9231's DLL (F23 is the
# played search's own clock); F8 and F16 fail on the unit's first DLL (e3aa47e). DEF65 rides every older mode at the four keys' off
# values: room 213, the rest as bca9231's: 2318 checks.
# The 2026-11-24a use unit (test 60: 11 stimpaks by their key in third person gave one heal, and the clip showed in both views) on
# bca9231 expects arms 185 (145 + 32 + 8 of its review), with the fake engine's item use (Eng67: the script's equip the game's animated use, its item 1.0
# s after its clip's props unless a stop came first, a second equip restarting a clip): UseItemFirst's hand-over left to play to its
# item and cut there (UI1), a chem applied at once cut at its props (UI2), three hand-overs with no clip then one (UI3), four presses
# 0.5 s apart one at a time (UI4), the ride's tally (UI5), QuickCut's hand-over (UI6), UseItemFirst=0 (UI7), a first-person record
# (UI8); the third review's N1 (UN10), N2 (UN9), N4 (UN11) and N5 (UN8b, UN8c: pass on bca9231 too); BodyArmsUse's key taken in first person (BA1), the
# first-person 3D hidden to the item and its tail (BA2), given back at 2.5 s with no item (BA3), at a draw and the Pip-Boy (BA4/BA5),
# the third-person flags line (BA6), BodyArmsUse=0 (BA7); QuickApplyProbe's three lines (QP1) and no call (QP2); UseSeatHold in
# GunTests59's world: Handguns only (SH1), a handgun drawn mid-hold (SH9), two presses chained (SH10), None (SH2), a weapon drawn in Any weapon (SH3), a rifle out before the key (SH11), no seat pose yet (SH4), first person
# (SH5), UseSeatHold=0 (SH6), the seat pose's read only near the seated mean (SH7), the weapon rules off (SH8). Its review: a handgun
# posed before the key (SH12: the hold posed, the let-go off, ended at its props gone), UseMoveEvent=1 (SH13), the shipped
# QuickKeyState=1 (UI1k, UI4k, BA2k, BA2r: the key's edge read before or after the hand-over, SH1k, SH10k), SH7 at GunSeatEvery 0.5 (a
# read due inside its mid-blend stretch). DEF65 rides every older mode at the new keys' off values (BodyArmsUseTail, a tunable with no
# off value, rides at its default): the rest as bca9231's: 2334 checks with this unit alone.
# 2026-11-24a, the aim unit (test 60's 1C: "hand with pistol doesn't follow camera when looking around and shooting"; the user's pick:
# the look turns your aim) adds, in the fake game's first person with the task twice a frame and its first-person arms following the
# actor (PlayerCharacter+0xB78 turned by the heading and the pitch after the tasks, at the camera's update): the keys' line (LA0); a
# weapon drawn, the look key held, the mouse at 90 deg/s 1 s: the heading 60 off the bike's line between the tasks, the camera and the
# arms with it, the plugin's own camera turn 0 (LA1); the drive turned back, the bike on its line (LA2); the view bike's axes and place
# kept (LA3); the heading the task reads the line (EyeAxes=1's view bike, LA4); the let-go's ease, aim and view together, and its line
# (LA5); a put-away and a draw mid-look, never 2L (LA6); a menu, the menu stack over the HUD's, the Pip-Boy and third person (LA7);
# a room ask while riding, the script's heading read with the aim in it (LA8b); D turning the line and the aim together, the view's
# lean about the bike's forward (LA9); LookShots' line (LA10); AimSit's probe (LA11); LookAim=0's 2026-11-23b look (LA12); and after
# the Parent tests (ViewLoadTests66: a load makes the plugin forget the cells' first-met spheres those tests match by, and LA13 turns
# LookAim off for the session) PreSaveGame, PreLoadGame and PostLoadGame (LA8) and the move's self-check (LA13) (view, 335 + 15). The
# camera's GetRotation slot is left as ViewTests59's rides left it (the plugin's wrapper). Its review adds: the game's target angle read
# less the aim ([Tilt] Trace's "the game's:" line: no rays here, no sidestep; LA17); the movement handler on a third of the frames, the
# drive turned by the aim of the moment through the sweep and the let-go (LA14); the getting off's second ask's heading kept (LA16);
# the handler silent across the ask (the fade), the frozen drive back on the line (LA15); the game's own move passed (a light stick
# push at a stop): no aim (LA18) (view + 5). DEF65 rides every older mode at the new keys' off values: view 355, the rest as
# bca9231's: 2314 checks.
# The 2026-11-24a orbit unit (test 60's 1D: "3rd person - still mostly bugged, right click and Z doesn't work to look around" with a
# pistol out; the log's "40-60 deg" was the plugin's own asked look, ThirdPersonState +0xF0/+0xF4 the game's outputs rebuilt each
# frame) on bca9231 adds a mode of its own, orbit (26: the view mode's keys and rig with the Address Library written, for
# LookOrbitClear's rays; the view mode, which has none, stays at 335), expecting 28 (the 4 load checks + 24: ViewTests67), on test
# 60's riding camera (the fake's g_v63Field 6: the camera root built from
# ThirdPersonState's own GetRotation and GetTranslation answers, slots 0x0C/0x0D in the fake's image, +0xF0/+0xF4 rebuilt from the
# heading after each task; your place at (-80000, 89000) as test 60's; a fixed stretch): the keys' line (OA0); slot 0xC outside the
# game's image refused, the armed hold every frame the plugin's (OAR); the free-rotation flag's place off slot 0x12's code (OA2b);
# both slots wrapped once (OA1); the probes settled, the calls a frame on and off the task's thread (OA2); test 60 on 2026-11-23b's
# keys, the camera behind, the game's frames over the plugin's (OA18) and its account naming the ahead test (OA17); the armed turn
# round you through a reversal, 60 either side, the camera on the circle, the bike on its line (OA3), a second thread's answers the
# same (OA14), eased back and the answers the game's own (OA4), the hold's account (OA5); LookOrbitArmed=1's every frame the plugin's
# (OA6); no weapon: the answers untouched (OA7); the weapon put away mid-hold (OA8); a wall: held at the last clear angle (OA9),
# pulled in (OA9b), LookOrbitClear=0 through it (OA9c); a jittering answer: the yaw set absolutely (OA10); a game reading its
# answers back (OA11); the translation not taken (OA12); every stop path disarming at once (OA15); the transpose and a world place
# (OA19); a root never taking the answers: never settled, LookOrbitArmed=1's (OA13); LookOrbitLearn: nothing learned with no
# weapon drawn (OA16). DEF65 rides every older mode at the new keys' off values: the rest as bca9231's: 2322 checks in 27 modes
# with this unit alone.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
# -fno-toplevel-reorder (2026-11-24a): the statics laid out in source order, so g_space (defined near the top) starts low in the
# image: the game addresses from RVA_LOOKUP_FORM (0x311B80) up must fall inside it. With GCC's own order the merged units' new
# statics went first and put it at +0x32d600 (bca9231: +0x2de240); in source order it is at +0x1ba040.
x86_64-w64-mingw32-gcc -std=c11 -O1 -fno-toplevel-reorder -Wall -Wextra -o "$WORK/fake_game.exe" "$HERE/fake_game.c" -static-libgcc
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
# 2026-11-15a, test 54's fixes: the round's new keys at their off values (2026-11-14a, 353d8de), the same way (after DEF54's
# to DEF57's). The look unit's: KitDefer and MountQuick (CMB_LookOptions 32768 and 65536). The kit unit's: KitTuneDistance
# and KitPreviewScene, and New's four values at 14a's (their defaults changed: pos 0,400,0, turn 0,0,0.785398, scale 1, zoom
# -1..3), so custom's 14a checks (K0-K8) ride 14a's preview exactly. The view unit's: CameraWorld, LeadFrame and LookWait
# (EyeAt's new default 0,-5,125 needs nothing: DEF57's 0,12,128 already gives every older mode its 10a eye). The drive unit's:
# PullTime=0 (not PullFrom: it acts only with PullTime on) and KeepLogs=1 (mode 9 takes it out before its load for the code's
# 3; mode 2 keeps 1).
DEF58='Look/KitDefer=0 Look/MountQuick=0 Look/KitPreviewPos=0,0,0 Look/KitPreviewTurn=0,0.02,44.764 Look/KitPreviewScale=0.3 Look/KitPreviewZoom=-1,1 Look/KitTuneDistance=0 Look/KitPreviewScene=0 View/CameraWorld=0 View/LeadFrame=0 View/LookWait=0 Steer/PullTime=0 Diag/KeepLogs=1'
# 2026-11-15b, the sidestep unit's keys at their off values (2026-11-15a, 1bc3f8a), the same way (after DEF54's to DEF58's): the wide
# sidestep (SidestepWide; not its seven numbers, which act only with it on), SidestepSteady, SidestepMouseSide, [Lamp] FrameLead (not
# LeadFrame: the loop's "already named" test is section-blind and DEF58 names [View] LeadFrame), [Diag] FpsFrames and PausedFrames
# (sound's P1 and P2 ride PausedFrames=1, the default).
# 2026-11-15b, test 54's: the fpcam unit's (not LookBackAngle .. LookBackSwing, LookMax, LookSnap: they act only with LookBack or LookKey on)
# 2026-11-15b, the weapons unit (test 53's wish a): its keys at their off values (2026-11-15a, 1bc3f8a), the same way (after
# DEF54's to DEF58's): PutAway, GunPose, GunStandBack, GunPredict (it acts only with GunPose), GunTrace and GunListen (not
# GunBlend and GunSeatEvery: they act only with GunPose). Mode 13's GunTests59 rewrites each to 1.
# 2026-11-15b, test 54's wishes: the round's new keys at their off values (2026-11-15a, 1bc3f8a), the same way (after DEF54's
# to DEF58's). The fpbody unit's: [View] Body=0 and [Diag] BodyProbe=0 (not BodyEye, BodyLeanMax, BodyShiftMax, BodyBack,
# BodyFade, BodyProbeEvery: they act only with Body or BodyProbe on).
# 2026-11-15b, the review's fixes: [Steer] FirstKeysArmed=0 (FirstKeys in first person only, as merged; the name clashes with no
# key any mode's INI or DEF line names: the loop's "already named" test is section-blind).
DEF59='Steer/SidestepWide=0 Steer/SidestepSteady=0 Steer/SidestepMouseSide=0 Lamp/FrameLead=0 Diag/FpsFrames=0 Diag/PausedFrames=0 View/CameraTurn=0 View/Roll=0 View/LookBack=0 View/LookKey=0 Steer/FirstKeys=0 Steer/FirstKeysArmed=0 Tilt/PutAway=0 Tilt/GunPose=0 Tilt/GunStandBack=0 Tilt/GunPredict=0 Diag/GunTrace=0 Diag/GunListen=0 View/Body=0 Diag/BodyProbe=0'
# 2026-11-16b, test 55's first person (the view unit's): the round's new keys at their off values (2026-11-16a, 5b04dbf), the same
# way (after DEF54's to DEF59's): CameraPlace, NearThird, ParentKeep, RollTurn, LookPitch, [Diag] ParentTime (not NearFade and
# ParentMargin: they act only with NearThird or ParentKeep on). FirstKeys' new default (0.45) needs nothing: DEF59 pins it at 0.
# 2026-11-16b, test 55's fixes: the round's new keys at their off values (2026-11-16a, 5b04dbf), the same way (after DEF54's
# to DEF59's). The kit unit's: KitFind and KitFit (not KitFitView and KitFitBox: they act only with KitFit; New's changed
# defaults need nothing: DEF58 already gives every mode 14a's four values).
# 2026-11-16b, test 55's fixes, the drive unit's keys at their off values (2026-11-16a, 5b04dbf), the same way (after DEF54's to DEF59's): the
# even climb's changed defaults PullFrom (0.1, 16a 0.6) and LaunchFrom (0.1, 16a 0.25; mode 23 names its own 0.25), PullClimb=0 and [Sound]
# SpeedMap= (the bike's own speed into the engine). PullTime's 16a value (5.5; the code's 8 now) needs no entry: DEF58's PullTime=0 (14a's)
# already rides every older mode, and the checks that want 16a's pull write PullTime=5.5 (LaunchTests58, SoundTests58, SoundTests60).
# 2026-11-16b, test 55's fixes (the weapons unit's: points D, E and E2): PutAwayProbe, PutAwayUnpaused (also CMB_RoomOptions bit
# 1024 for the controller), GunRootFrame, GunBothBars, GunCarry, GunStillRide and GunPredictMax at their off values (2026-11-16a,
# 5b04dbf), the same way (after DEF54's to DEF59's). Mode 13's GunStill61 and GunTests61 rewrite each to its default.
# 2026-11-16b, the body unit (test 55's point C): its keys at their off values (2026-11-16a, 5b04dbf), the same way (after DEF54's
# to DEF59's): [View] BodyWorn, BodyWeapon, BodyNear, BodyArmsBack, [Diag] BodyDrawn, and BodyEye at 16a's 0,7,7 (its default is
# 0,2,-0.5 now). Not BodyWeaponNodes: it acts only with BodyWeapon on.
# 2026-11-16b, the review's fixes: [View] BodyFollowCamera=0 (the body by the task alone, 2026-11-16a; it acts only with CameraPlace and
# Body on, both pinned off above for every older mode; the name clashes with no key any mode's INI or DEF line names).
DEF60='View/CameraPlace=0 View/NearThird=0 View/ParentKeep=0 View/RollTurn=0 View/LookPitch=0 Diag/ParentTime=0 Look/KitFind=0 Look/KitFit=0 Steer/PullFrom=0.6 Steer/LaunchFrom=0.25 Steer/PullClimb=0 Sound/SpeedMap= Tilt/PutAwayProbe=0 Tilt/PutAwayUnpaused=0 Tilt/GunRootFrame=0 Tilt/GunBothBars=0 Tilt/GunCarry=0 Tilt/GunStillRide=0 Tilt/GunPredictMax=0 View/BodyWorn=0 View/BodyWeapon=0 View/BodyNear=0 View/BodyArmsBack=0 View/BodyEye=0,7,7 Diag/BodyDrawn=0 View/BodyFollowCamera=0'
# 2026-11-17a, test 56's fixes, the drive unit's keys at their off values (2026-11-16b, ddf7b1e), the same way (after DEF54's to DEF60's):
# [Sound] DownBands= (a stop's down-shifts by SpeedMap's speed) and the changed defaults HeardStop (900, 16b 300) and HeardBrake (1500, 16b
# 600); mode 16's SOUND names both at 300 and 600 itself. Not DownBlend: it acts only with DownBands on. [Steer] LaunchFrom's new default (0.14,
# 16b 0.1) needs no entry: DEF60's LaunchFrom=0.25 (16a's) already rides every older mode (the loop would skip a second LaunchFrom), and the
# 16b checks that took the code's default (LaunchTests60's Q1-Q2, SoundTests60's M1-M6) write 0.1.
# 2026-11-17a, test 56's fixes (the weapons unit's: 1B, 56-27, 56-29 and the spikes of section 3): GunCheckUnpaused, GunCheckRecover
# (the cross-check's pause and its recovery), DrawHandgunOnly (slot 0xC9's wrapper; also CMB_RoomOptions bit 2048), QuickHolsterFirst
# and GunJudgeWait (CMB_RoomOptions bit 4096), NodelessOnce, SkinArraysCheck and [Diag] HeldWhere (the spikes) at their off values
# (2026-11-16b, ddf7b1e), the same way (after DEF54's to DEF60's). Mode 13's GunTests62 rewrites each to its default and back.
# 2026-11-17a, test 56's fixes (the body unit's: 1C, 56-23, the Z look): its keys at their off values (2026-11-16b, ddf7b1e), the same way
# (after DEF54's to DEF60's): [View] BodyNodes=1 (bit 0 on the worn bike's and the weapon's nodes with the body), BodyArmsLook=0
# (BodyArmsBack's angle alone), [Diag] BodyWornLine=0, and BodyLeanMax at 16b's 35 (its default is 40 now). BodyEye's new default
# (0,6,-3) needs nothing: DEF60 already pins 16a's 0,7,7 for every older check (BodyTests61 writes 16b's 0,2,-0.5 for its own).
# 2026-11-17a, test 56's fixes (the kit unit's keys at their off values, 2026-11-16b, ddf7b1e), the same way (after DEF54's to
# DEF60's): KitHold (the bike held about its centre, the wheel's zoom, the drag's turn), KitSlotView (a view per slot) and KitRoom
# (the field kit's spot asked about: CMB_LookOptions 131072); not KitTurnTime, KitZoom, KitDrag, KitHoldAbove, the six KitView*
# and KitRoomRing (they act only with KitHold, KitSlotView or KitRoom on).
# 2026-11-17a, test 56's first person (the cam unit's): [View] CameraEase and NearHandover at their off values (2026-11-16b, ddf7b1e), the same way
# (after DEF54's to DEF60's). Neither name is used in any other section, INI or DEF line.
DEF61='Sound/DownBands= Sound/HeardStop=300 Sound/HeardBrake=600 Tilt/GunCheckUnpaused=0 Tilt/GunCheckRecover=0 Tilt/DrawHandgunOnly=0 Tilt/QuickHolsterFirst=0 Tilt/GunJudgeWait=0 Tilt/NodelessOnce=0 Tilt/SkinArraysCheck=0 Diag/HeldWhere=0 View/BodyNodes=1 View/BodyArmsLook=0 Diag/BodyWornLine=0 View/BodyLeanMax=35 Look/KitHold=0 Look/KitSlotView=0 Look/KitRoom=0 View/CameraEase=0 View/NearHandover=0'
# 2026-11-21a, the kit unit's (test 57's 1B and 1C, art build B's slots): the new keys at their off values (2026-11-17a, 24b2368).
# Not in it: KitListBox, KitViewWear, KitViewFrontFender, KitViewHeadlamp (they act only with their switch on).
# 2026-11-21a, test 57's 1A (the third unit's: the bike, and sometimes you, not drawn in third person after your body): [View]
# BodyRedraw and BodyRedrawHide (your 3D marked changed once the bike is plain in third person after a showing or NearThird's stand-in,
# and the game's own hide-and-show for a mark it leaves) and [Diag] ThirdWhere (the lines at each switch to third person) at their off
# values (2026-11-17a, 24b2368), the same way (after DEF54's to DEF61's). No name is used in any other section, INI or DEF line.
# 2026-11-21a, test 57's fixes (the drive unit's keys at their off values, 2026-11-17a, 24b2368), the same way (after DEF54's to DEF61's):
# [Steer] CoastDrag (the throttle let go rolling off by the speed). The gear table's new defaults (HeardRiseGears, ShiftGapGears) and
# DownBands' need no pin here: DEF54 and DEF61 already pin older values for every older check (the sound checks that took the code's
# gear table write 2026-11-17a's: SndGears17a63). The name is used in no other section, INI or DEF line.
# 2026-11-21a, test 57's look (the look unit's keys at their off values, 2026-11-17a, 24b2368), the same way (after DEF54's to DEF61's):
# [View] LookButton (a second look key, the right mouse button), LookThird (the look key in third person) and [Steer] AimBlock (the
# game's aim kept from it while riding), [Diag] AimWatch (the aim's handler watched, the aim lines); not LookThirdBack (it acts only
# with LookThird). LookKey's default is unchanged (-1, the MCM's CMB_LookKey): nothing to pin. No name is used in any other section,
# INI or DEF line.
DEF62='Look/KitFollow=0 Look/KitSlotSettle=0 Look/KitMouse=0 Look/KitWheelOwn=0 Look/KitNewSlots=0 View/BodyRedraw=0 View/BodyRedrawHide=0 Diag/ThirdWhere=0 Tilt/GunHandHide=0 Tilt/GunAwayKeep=0 Tilt/GunSeatKeep=0 Tilt/GunNoteSure=0 Steer/CoastDrag= View/LookButton=0 View/LookThird=0 Steer/AimBlock=0 Diag/AimWatch=0'
# 2026-11-22a, test 58's look (the aim unit's key at its off value, 2026-11-21a, fbe9a7c), the same way (after DEF54's to DEF62's):
# [View] LookOrbit (the plugin's own third-person orbit); not LookOrbitGain (it acts only with LookOrbit). The aim's struct name
# (.?AUAttackBlockHandler@@) by [Steer] AimStruct (the review of 2026-11-22a, item 6: with DEF62's AimBlock and AimWatch at their
# shipped 1 the struct's name alone would wrap it where 2026-11-21a never found it). No name is used
# in any other section, INI or DEF line.
# 2026-11-22a, the kit unit's (test 58's 1D, art build C's slots): the new keys at their off values (2026-11-21a, fbe9a7c).
# Not in it: KitViewPaintWear (it acts only with KitSlots22).
# 2026-11-22a, test 58's fixes (the drive unit's keys at their off values, 2026-11-21a, fbe9a7c), the same way (after DEF54's to DEF62's):
# [Steer] MenuKeep (the speed measure held while a menu pauses the game) and [Sound] UpBands (a pull's up-shifts held for the bike's bands).
# Neither name is used in any other section, INI or DEF line.
# 2026-11-22a, test 58's 1A and 1C (the apply unit's keys at their off values, 2026-11-21a, fbe9a7c), the same way (after DEF54's to
# DEF62's): [Look] ParkedSwapHold, OverlayRuntime and (its review) OverlayParked (CMB_LookOptions 262144, 524288 and 1048576 for the
# scripts; OverlayParked's default 0 is off, pinned all the same) and [Diag] LensLine (the lens
# line at the mount). No name is used in any other section, INI or DEF line.
# 2026-11-22a, test 58's parked bike (the parked unit's keys at their off values, 2026-11-21a, fbe9a7c), the same way (after DEF54's
# to DEF62's): [Room] ParkFit (the parked bike set on the ground under its tyres after every placement, the controller's ask kind 6)
# and ParkStand (the side stand's foot: the lean on it; empty = upright). No name is used in any other section, INI or DEF line.
# 2026-11-22a, test 58's 1E (the attach unit's: the holster mod's pistol held off your body): [Tilt] AttachUnclone (a copy another
# mod makes of a shape this plugin writes held from that shape's own transform), AttachBoneRole (a subtree under a body bone moved as
# the body's skin there), AttachHide (the fallback: such subtrees shrunk while riding; its default is 0 already) and [Diag] AttachWhere
# (the lines) at their off values (2026-11-21a, fbe9a7c), the same way (after DEF54's to DEF62's). Mode 13's AttachTests64 rewrites
# each and back. No name is used in any other section, INI or DEF line.
DEF63='View/LookOrbit=0 Steer/AimStruct=0 Look/KitDrawn=0 Look/KitWheelDown=0 Look/KitWheelLists=0 Look/KitSlots22=0 Steer/MenuKeep=0 Sound/UpBands= Look/ParkedSwapHold=0 Look/OverlayRuntime=0 Diag/LensLine=0 Room/ParkFit=0 Room/ParkStand= Tilt/AttachUnclone=0 Tilt/AttachBoneRole=0 Tilt/AttachHide=0 Diag/AttachWhere=0 Look/OverlayParked=0'
# 2026-11-23a, the kit unit's (test 59's 1F): the new keys at their off values (2026-11-22a, 131f6b4).
# 2026-11-23a, test 59's fixes: the round's new keys at their off values (2026-11-22a, 131f6b4), the same way (after DEF54's to
# DEF63's). The look unit's: [View] LookOrbitGame and LookRecover.
# 2026-11-23a, test 59's 59-22 (the grip unit's keys at their off values, 2026-11-22a, 131f6b4), the same way (after DEF54's to DEF63's):
# [Tilt] GunOneHand (third person, a handgun posed with GunBothBars=1: the right hand off its grip holding it, the left on its grip),
# GunHoldAt (where, from the seat pose's wrist; it acts only with GunOneHand: pinned at its default) and [View] BodyGunGrip (first
# person, a handgun out: your body shown, its right arm hidden, the game's first-person left arm shrunk). Mode 13's GunTests65 and
# mode 20's BodyTests65 rewrite each and back. No name is used in any other section, INI or DEF line.
# 2026-11-23a, test 59's 1A (the overlay unit's keys at their off values, 2026-11-22a, 131f6b4), the same way (after DEF54's to DEF63's):
# [Look] OverlayEvery and OverlayQuick (CMB_LookOptions 2097152 and 4194304 for the scripts). OverlayParked's changed default (1;
# 22a's 0) needs nothing here: DEF63 already pins OverlayParked=0 for every older mode. No name is used in any other section, INI or DEF line.
# 2026-11-23a, test 59's 1D and 1E (the parked unit's: the bike beside you at a getting off, its lean from upright, its tyres, getting
# on's hide): [Room] ParkBeside, ParkLean, ParkTyres and MountHide at their off values (2026-11-22a, 131f6b4), the same way (after
# DEF54's to DEF63's). Mode 14's ParkTests65 rewrites each and back. No name is used in any other section, INI or DEF line.
# 2026-11-23a, test 59's 1C and the user's pick (the attach unit's): [Tilt] AttachSkeleton (an attachment may hang off a skeleton
# node the skins reach through their helper bones: the thigh's holster; the seat pose reads them too), [Diag] AttachFresh
# (AttachWhere leaves out shapes the game isn't drawing as written) and [Steer] UseNoClip (no item's use clip in third person
# while riding) at their off values (2026-11-22a, 131f6b4), the same way (after DEF54's to DEF63's). Mode 13's AttachTests65 and
# UseNoClipTests65 rewrite each and back. No name is used in any other section, INI or DEF line.
DEF64='Look/KitLate=0 Look/KitPrePlace=0 View/LookOrbitGame=0 View/LookRecover=0 Tilt/GunOneHand=0 Tilt/GunHoldAt=-3,-2,9 View/BodyGunGrip=0 Look/OverlayEvery=0 Look/OverlayQuick=0 Room/ParkBeside=0 Room/ParkLean= Room/ParkTyres=0 Room/MountHide=0 Tilt/AttachSkeleton=0 Diag/AttachFresh=0 Steer/UseNoClip=0'
# 2026-11-24a, test 60's 1C (the grip unit's keys at their off values, 2026-11-23b, bca9231), the same way (after DEF54's to DEF64's):
# [View] BodyGunGripNodeless (the first-person left arm's bones with no node judged by their binds, a left-only piece whole),
# BodyGunGripSpeck (joint: each shrunk bone about its own joint, not one point at the left shoulder) and [Diag] GunGripBones (the
# judge's lines). Mode 20's BodyTests67 rewrites each and back. No name is used in any other section, INI or DEF line.
# 2026-11-24a, test 60's small faults (the plog unit's keys at their off values, 2026-11-23b, bca9231), the same way (after DEF54's to DEF64's):
# [View] NearThirdOff (NearThird's stand-in ends past NearThird), [Diag] NearDrawEvery (ViewDraw's lines at every task of a stand-in) and [Look]
# KitGuard (the task's work on the kit's bike whenever it runs). KitLate's changed default (0; 2026-11-23b's 1) needs nothing here: DEF64
# already pins KitLate=0 for every older mode (KitTests65 writes 1 for its own). No name is used in any other section, INI or DEF line.
# 2026-11-24a, test 60's small faults (the sfix unit's): [Look] KitQuickExit (getting on let through as the field kit's menu closes:
# CMB_LookOptions 8388608) and EquipLate (a getting on's colour-only work on the worn bike after the screen, and the tilt watch through its
# black: CMB_RoomOptions 8388608), [Sound] LandOnce (CMB_FxAir held at 2 after the script's answer to a flight's cue) at their off values
# (2026-11-23b, bca9231), and [Diag] APWatch at its old default 1 (0 since 2026-11-24a; 1 also leaves CMB_RoomOptions' 4194304 clear;
# mode 7 names its own), the same way (after DEF54's to DEF64's). No name is used in any other section, INI or DEF line.
# 2026-11-24a, test 60's 1A and 1B (the park unit's: the rider held still at a getting off and the keys after it, the parked bike's
# collision checked and repaired, the leaned bars off the player's capsule): [Room] ParkStop, ParkHold, ParkSolid, ParkFresh (an A/B,
# 0 by default: pinned all the same) and ParkLeanClear at their off values (2026-11-23b, bca9231), the same way (after DEF54's to
# DEF64's). Mode 14's ParkStopTests66, ParkSolidTests66 and ParkLeanTests66 rewrite each and back. No name is used in any other section,
# INI or DEF line.
# 2026-11-24a, test 60's 1C and the user's pick (the aim unit's: the look turns your aim with a weapon drawn in first person): [View]
# LookAim, AimSit (an A/B probe, off by default) and [Diag] LookShots at their off values (2026-11-23b, bca9231), the same way (after
# DEF54's to DEF64's). Mode 20's ViewTests66 rewrites each and back. No name is used in any other section, INI or DEF line.
DEF65='View/BodyGunGripNodeless=0 View/BodyGunGripSpeck=joint Diag/GunGripBones=0 View/NearThirdOff=0 Diag/NearDrawEvery=0 Look/KitGuard=0 Look/KitQuickExit=0 Look/EquipLate=0 Sound/LandOnce=0 Diag/APWatch=1 Room/ParkStop=0 Room/ParkHold=0 Room/ParkSolid=0 Room/ParkFresh=0 Room/ParkLeanClear=0 Room/ParkFootFix=0 Room/ParkFallbackSearch=0 Room/GuardStuckMove=0 Room/SwimSpot=0 Steer/UseItemFirst=0 Tilt/UseSeatHold=0 View/BodyArmsUse=0 Diag/QuickApplyProbe=0 Diag/UseMoveEvent=0 View/LookAim=0 View/AimSit=0 Diag/LookShots=0 View/LookOrbitArmed=0 View/LookOrbitClear=0 View/LookOrbitLearn=0 View/LookOrbitAbs=0 Diag/OrbitWhy=0 Diag/OrbitEachRide=0'
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
  for kv in $DEF54 $DEF55 $DEF56 $DEF57 $DEF58 $DEF59 $DEF60 $DEF61 $DEF62 $DEF63 $DEF64 $DEF65; do
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
# 2026-11-24a (the orbit unit's, mode 26 only): [View] LookOrbitArmed and its keys on test 60's riding camera (ViewTests67), with the
# view mode's keys and rig but the Address Library written (LookOrbitClear's rays: mode 20 has none), so the view mode stays as it was.
run orbit 26 "$KNOWN[Tilt]\nTrace=1\nPivotHeight=74\nPivotForward=0\nTorsoLean=0\nBumpMax=0\nLiftRate=0\nSuspension=0\n$PARTSLOOK$LAMP${LOOK/Mirrors=1\\n/Mirrors=1\\nCull=1\\n}$VIEW49[Sound]\nDrive=0\n"
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
