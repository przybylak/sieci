# Testing in game

I can't run Fallout 4, so in-game testing is yours. These checks are ordered so that the first failure points at one specific part.

## Turn on Papyrus logging first

In `Documents\My Games\Fallout4\Fallout4Custom.ini`:

```ini
[Papyrus]
bEnableLogging=1
bEnableTrace=1
bLoadDebugInformation=1
```

The log goes to `Documents\My Games\Fallout4\Logs\Script\Papyrus.0.log`. Every mod action writes a line starting with `[CMB]`, and script errors show up there too.

Without F4SE you'll see one or two harmless errors about the `F4SE` / `CMB_HotkeyF4SE` scripts not being found. That's the mod checking whether they're there. When something breaks, send the log, plus a screenshot or a short clip if it's visual.

## Test 60: the 2026-11-23b build (test 59's fixes and your wishes; 2026-11-23a with its second review's fixes)

The 2026-11-23a build answers test 59 (run on 2026-11-22a): its fixes and your wishes after it, in one build; the
2026-11-23b build is 2026-11-23a with a second review's four fixes, so install 2026-11-23b, not 2026-11-23a: a stimpak
from the Favourites menu right after the Pip-Boy keeps its heal (step 25), getting on hides a parked bike carrying the
look's swap before the fade with any `[Look] MountGuard` and `ParkedSwapHold` (step 6), and two fixes in the look's
scripts (a look timer while getting off, a load's compose with `WornIndex=0`). No key is new, and the ESP, the MCM,
`CMB_Slope.ini` and the art are 2026-11-23a's. Your picks: getting off parks the bike beside you, with the old spot back
along the track as the fallback; no healing clip while riding in third person; the left hand on the bar with a pistol
out, in first and third person; and a quicker take-off, 0.3 of the top in about 1.5 s and half in about 2.8 s, the gears
still at about 12, 24, 36 and 46 on the dial. Steps 1-7 are getting off and on, steps 8-9 the take-off and the gears,
steps 10-14 the art and the Wear on every bike, step 15 the field kit, steps 16-19 a pistol out, steps 20-21 the
third-person look, steps 22-23 the holster on your thigh, steps 24-25 a stimpak in third person and step 26 the frame
rate, with the questions T60-1 to T60-26 at the end and, after them, the open questions and the log lines that settle
them. What test 59 liked (no crash, the muddy tread, Nuka-Cola's script, the headlamp's colours, the front fender badge
gone, the kit's views and wheel, the third-person look with no weapon out, the gears at their bands) is as it was.

- **Getting off:** the bike is parked beside you, on your right (on your left when there's no room on your right), in
  view, where you got off; only with no room on either side does it go back along the track as before (test 59: "when
  getting off I'm sometimes put far away from where I got off": a bike length and a half back, behind the camera).
- **The parked bike:** it leans on its stand between 5 and 20 degrees from upright, so it still rests on its stand on a
  slope rising toward the stand and no longer lies over at 31 degrees after a swim; a tyre beside a wrecked car is set
  on the ground under it, not on the car, and a wheel at a curb's edge sits on it.
- **Getting on and off quicker:** getting off asks the plugin once instead of four times, and getting on no longer loads
  the parked bike again first: it vanishes as you press E (as the screen goes dark when it carries no look swap), before
  the bike under you goes on (test 59: "getting on and off wait time is longer than normal").
- **The take-off:** quicker, your pick (test 59: "still feels a bit sluggish on take-off").
- **The art:** Rusty (and Raider's rust) lighter, see-through and darker at its edges, with no rust frame round the
  badge plates (your wish: "rust is too much, should be less intense, more transparent and in darker colors on edges";
  "a rectangle around the frame"); three meshing gears on either side of the 3D Brotherhood helmet, after your layout
  ("I was hoping to have 3 gears shown on each side"); and the Wear and Paint condition on all four bikes every time,
  the parked bike and the bike under you in third person included, within a moment (test 59: "paint effects are not
  visible on free standing bike"; "wears are showing correctly in the preview, but are not visible on the bike when
  outside of field kit").
- **The field kit:** no frame of the menu's own pose between options (test 59: "between every option bike gets into
  default position for a moment").
- **A pistol out:** your left hand stays on the left grip and your right hand holds the pistol alone, in third person
  and in first (test 59: "the character isn't aiming, but she still holds the gun with both hands").
- **The look in third person:** it works with a weapon drawn too, and it never switches itself off for the session (test
  59: "right-click/Z for free camera doesn't work when gun is out in 3rd person camera").
- **The holster:** your holster mod's pistol on your thigh is found as hanging off the thigh itself, so it follows your
  thigh, also in the moment right after a put-away (test 59: "guns are still showing up in random places").
- **A stimpak in third person:** no clip on the bike, by its number key or from the Pip-Boy, slow or at speed: the item
  works and your hands stay on the bars (your pick; test 59: "it would make more sense to not have any healing animation
  in 3rd person unless you can fix it"). First person is as before.

Five things to know first: when you get off, the bike is beside you, on your right as a rule (look there as the screen
comes back, not behind); the parked bike blinks once a couple of seconds after the field kit closes, and the Wear is on
it right after that blink; getting on, the parked bike usually vanishes as you press E, just before the screen goes
black; in third person a stimpak by its number key or from the Pip-Boy plays no clip at all, the health still comes; and
with a pistol out in third person your right hand leaves the bar and holds the pistol over it.

Do this section's steps in one game session if you can, in this order (getting off first, the art and the kit by the
parked bike in one of your settlements, the night views after them, then the rides), and say which session each step was
in. Every new behaviour of the plugin has a key whose off value gives the 2026-11-22a build back (README's table of this
build's keys), so each A/B is one key away; the changed art's A/B is files (after step 14). Things only the game can
settle: how much shorter the getting-off and getting-on blacks are (steps 1 and 6), whether a bike leaning 5 degrees on
a slope rising toward its stand still looks as if it rests on it (step 5), when the armour menu puts a new bike in (step
15), whether the game draws its first-person arms through the plugin's shrunk bone data and which way a pistol's barrel
points (steps 16-18), which of two readings of test 59's third-person camera is the game's (step 20), and what the dark
thing along your right forearm in test 59's holster picture was (step 22).

Before you start:
- install 2026-11-23b as a Replace over 2026-11-22a (skip 2026-11-23a). If you edited `CMB_Slope.ini`, put your values
  into the new one: `[Look]`, `[View]`, `[Steer]`, `[Tilt]`, `[Room]` and `[Diag]` have new keys, and three defaults
  change: `[Look] OverlayParked` 1 (test 59's A/B; 0 in 2026-11-22a), `[Steer] LaunchFrom` 0.25 (0.14) and `[Sound]
  HeardRiseGears` 2.1,1.35,1,1,1 (2,0.86,0.8,1,1) (README's table). Otherwise use the shipped file as it is;
- the ESP and the MCM are 2026-11-22a's, unchanged (the Look section's 25 controls); a 2026-11-22a save loads as it is
  and nothing is put on afresh;
- the same load order as test 59: your visible-holster mod on;
- have the 10mm, the .44 and the flare gun on the favourites' number keys, a stimpak on one too, and a few stimpaks;
- the night views want night: wait for it, or in the console `set gamehour to 22`;
- for the blacks (steps 1 and 6) a video is the best measure (30 fps or more); say where the recording skipped;
- each A/B below: change one key in `CMB_Slope.ini`, save the file, get off and on (no restart), and put it back after.

The log's first lines: `CMB_Slope.log` has six settings lines more: `  room (2026-11-23a, test 59): ParkBeside=65
(getting off: the bike 65 to your right, else your left, 28 ahead, ...); ParkLean=5,20 (...); ParkTyres=1 (...);
MountHide=1 (...): CMB_RoomOptions 65536 131072 262144 ...`, `  look (2026-11-23a, test 59): OverlayEvery=1 (...)
OverlayQuick=1 (...): CMB_LookOptions 8388607 for the scripts`, `  kit (2026-11-23a): [Look] KitLate=1 (...)
KitPrePlace=1 (...)`, `  grip (2026-11-23a, test 59): GunOneHand=1 GunHoldAt=-3,-2,9 [View] BodyGunGrip=1 (...)`, ` look
(2026-11-23a, test 59): [View] LookOrbitGame=1 (...) LookRecover=1 (...)` and `  attachments and item use (2026-11-23a,
test 59): AttachSkeleton=1 [Diag] AttachFresh=1 [Steer] UseNoClip=1 (...)`; and three older ones read differently: `
steer (2026-11-16b, test 55): from rest the throttle starts at 0.25 (LaunchFrom) and climbs evenly from there, 0.112 of
the top a second, the top 6.7 s after the press ...`, `  sound: HeardRiseGears=2.1,1.35,1,1,1 ShiftGapGears=0,1.8,2,1.7:
...` and 2026-11-22a's look line, `... OverlayParked=1 (...)`. No 2026-11-23a lines, or `ParkBeside=0 (getting off at
the track's spot: 2026-11-22a)` with an INI you didn't change, mean an older `CMB_Slope.dll` or `CMB_Slope.ini` is
loaded: stop and say so.

### Getting off and on (2026-11-23a): steps 1-7

(test 59: "when getting off I'm sometimes put far away from where I got off": the plugin parked the bike a bike length
and a half back along your track, 145 units on 13 of 19 get-offs, behind the camera; "it leans, but not always;
sometimes one tyre is partially in the ground": on slopes rising toward the stand the bike tipped away from it, after a
swim it lay 31 degrees over, beside a wrecked car the rear tyre's ray met the car; and "getting on and off wait time is
longer than normal": getting on about 0.5 s slower than test 58's, the getting-off black 1.9-2.0 s against 1.7)

1. **Getting off on flat ground**: ride a short way along a road in third person and get off. As the screen comes back
   the bike should be right beside you on your right, its stand side towards you, in view (not behind the camera), its
   middle about where the bike was under you. Do it five times or more, at a stop and right after riding, and once
   getting off while the bike still rolls: it is set at the very spot the plugin checked, not shifted along. Time the
   black on the video if you record: test 59's was 1.9-2.0 s, about 1.3 s is expected.
   - `CMB_Slope.log`: `room: ask N: on the player's right at (x, y): room (...)`, the guard's `room: ask N at (...) ...
     (the parked bike's place: ParkGuard, the player not counted): no one in it ...`, its fit's `room: ask N at (...)
     (the parked bike's fit: ParkFit): fitted: ..., leaning 8.6 on its stand from upright: roll -8.6 ...`, and then
     `room: ask N at (px, py, pz), heading H (the parked bike beside the player: ParkBeside): on their right, ...`.
   - `Papyrus.0.log`: `Parked bike beside the player (the plugin's [Room] ParkBeside, one ask): 65 to their right, 28
     ahead, along their heading; fitted: pitch ..., roll ..., leaning 8.6 on its side stand.` then `Dismounted.`; no
     `The park spot (the track just ridden)` line and no `Parked bike set on the ground under its tyres` line at a
     getting off: one ask where 2026-11-22a made four.
2. **On slopes**: get off riding up a slope, riding down one, and across one both ways (the ground falling to your
   right, then to your left). The bike is beside you each time, on your right as a rule, both tyres on the ground.
3. **By a wall**: get off with a wall or a fence close on your right: the bike should be on your left instead. Then get
   off with a ledge, a drop or a high kerb close on your right, where both tyres couldn't sit on the ground: the bike
   should be on your left too (such a side counts as no room). Then get off in a narrow gap with no room either side
   (between two walls, a car and a wall): it goes back along the track as in test 59.
   - Left: `... (the parked bike beside the player: ParkBeside): on their left, ...` and `... 65 to their left, 28
     ahead, ...`.
   - Neither: `Papyrus.0.log` `... none on either side (the plugin's lines say why).`, then 2026-11-22a's lines (`The
     park spot (the track just ridden) ...`).
4. **By a car, a curb, a step**: get off with a wrecked car close on your right (the bike's wheels near the car's body),
   at a curb, and with a step or a paving edge under a wheel. Both tyres should sit on the ground or on the curb's edge,
   never on the car's body and never sunk into the step. Kneel by the wheels and look.
   - A tyre whose ray met the car: the fit line ends `; the rear tyre's ray met something N over the line from the front
     tyre through the middle's (<its name>): looked under it, its ground ...` (or the front tyre's).
   - A wheel on an edge: `; the front tyre raised N onto the ground 8 ahead of its contact (its footprint)` (or 16, or
     behind).
5. **The lean on the stand**: on flat ground the bike leans about 9 degrees to its left on its stand. Across a slope
   with the stand uphill it should still lean onto its stand a little (at least 5 degrees), not stand upright or tip
   away from it; with the stand downhill it leans more, but no more than 20 degrees (test 59's spot after a swim leaned
   31). Then let it come to you after a swim and call it (keys → Call) to a slope: the same. Does a bike at 5 or 20 look
   right, or does the foot look buried or in the air?
   - The fit line: `leaning X on its stand from upright: roll -X`; held: `(its -6.7 from upright held to 5: the foot 3.6
     into its ground)` or `(its 31.0 from upright held to 20: the foot 3.0 over its ground)`.
6. **Getting on**: get on next to the leaning bike several times, some right after the field kit. There is no reload
   blink at the press any more. When the parked bike carries the plugin's look swap (most getting-ons now: step 13) it
   vanishes as you press E, just before the screen goes black, without standing up first; otherwise it stands up and
   vanishes 0.2 s into the fade. You ride upright, no jump. Time the black on the video and the press to riding (test
   58: 2.5-3.1 s of black for a quick one, test 59 2.8-3.3; the press to Mounted 3.6 s in test 58, 4.1 in test 59): as
   quick as test 58's or quicker? Does the bike vanishing at the press look wrong?
   - `Papyrus.0.log`, with the look's swap on it: `Getting on: the parked bike's look at the mount (ParkedSwapHold):
     ...; a runtime swap on its 3D (...): its 3D hidden at once, before the fade (MountHide: no reload; the bike back at
     the ride's end, or where it stood if the getting on is undone); ...`. Without one: `Getting on: the parked bike
     hidden under the fade before the equip (the plugin's [Room] MountHide).`, and the stand-up's `Getting on: the
     parked bike stood up off its side stand (...)` only when it finished before the hide.
   - Every getting on: `Getting on: the press 0.00, the fade ..., the equip ..., the pose ..., ready ... (CMB_RideReady
     after ... s), the screen back ..., Mounted ... (real seconds)`: send them all; no `Getting on: waited X s for the
     parked bike's look` after the kit (test 59: 1.1-2.1 s three times).
   - If a getting on fails (a message, you stay on foot), the bike should be back where it stood, leaning.
7. **The A/Bs**: `[Room] ParkBeside=0` (test 59's spot back along the track), `ParkLean=` (empty: 2026-11-22a's lean, 3
   to 12 against the ground across), `ParkTyres=0` (one ray at each tyre's contact), `MountHide=0` (2026-11-22a's
   getting on: the bike loaded again first, a blink, then the fade, and the hide after the equip). A few get-offs and
   get-ons each, on the same ground; back to the shipped values after.

### The take-off and the gears (2026-11-23a): steps 8-9

(test 59: "still feels a bit sluggish on take-off": the plugin's take-off was 17a's, but most of test 59's starts were
from a stand of 5 s or more and in third person, where the game's own first second is slow; from rest 0.3 of the top
came after 2.09 s and half after 3.58; your pick: 0.3 of the top in about 1.5 s, half in about 2.8, the gears at about
12, 24, 36 and 46 on the dial)

8. **From a stand**: on a long flat road take off from a stop with W held to the top, about ten times: half after
   standing still a while, half right after stopping, some in first person and some in third. The first second or two
   should pull away briskly, not sluggishly, and without a jerk.
   - Each take-off: `launch: from rest: 0.3 of the top after X s, half after Y s, 0.9 after Z s, the top (0.97) after W
     s (the throttle from 0.25 closing on the top over 1.5 s, the cap's lead 0.45: LaunchTau); ...`: X about 1.5 (about
     1.55 after standing, 1.3 when the bike moved a few seconds before), Y about 2.65, Z about 5.9.
9. **The gears on the dial**: in the same pulls the gears should still change at about 12, 24, 36 and 46 on the dial,
   each gear sounding as if it revs out before it changes (not changing up early or soft). Let go at the top a few times
   and coast to a stop, and brake hard from the top once or twice: both as in test 59.
   - The gear lines: `sound: gear 2 at ~215 u/s, ~3400 rpm ... (UpBands, held ...)`, then gear 3 at ~429, 4 at ~644, 5
     at ~823; from a stand 1-2 and 2-3 at about 3400-3500 rpm, 3-4 about 3200, 4-5 about 2570 (when the bike was moving
     just before, 1-2 about 2700 and 2-3 about 3250).
   - A/B, by hand (the take-off has no key of its own): set `[Steer] LaunchFrom=0.14` and `[Sound]
     HeardRiseGears=2,0.86,0.8,1,1` together (2026-11-22a's take-off), a few take-offs, then back to 0.25 and
     2.1,1.35,1,1,1. Better or worse?

### The art and the Wear on every bike (2026-11-23a): steps 10-14

At the field kit choose each in turn and look at it in the kit's preview, then leave the kit and look at the parked bike
close up (after its blink a couple of seconds after the kit closes), then ride away and look at it from the riding
camera, in third person from the side and from behind, by day and at night. A screenshot of each, close and riding,
please.

10. **Rusty**: Wear "Rusty", the Brotherhood of Steel badge on one tank and "Brotherhood helmet (3D)" on the other. Look
    close at the badges: no rust frame round a plate and no drips off its lower edge any more; the rust is scattered
    brown stains, the paint showing through them, each darker at its edge, one or two of them by a plate at random
    places. Then the whole bike parked and riding, by day and at night: lighter than in test 59 (less rust, less
    orange), the mufflers brown rust rather than bright orange. Is it now too faint?
    - `Papyrus.0.log`: `Customise: wear = Wear:rusty (4)`.
11. **Raider, and every Wear at the badges**: Wear "Raider": the same lighter rust under the blood. Then Weathered,
    Dusty, Muddy, Bloody and Wasteland in turn, close at both tank badges and the rear badge: no frame round any plate.
    `Customise: wear = Wear:raider (7)`.
12. **The gears beside the helmet**: Tank L and Tank R "Brotherhood helmet (3D)". On each tank the metallic blue plate
    shows three black gears on each side of the helmet: a big one low toward the plate's end, a smaller one above it,
    and a smaller one up beside the helmet, the small ones' teeth in the big one's gaps; no gear behind or under the
    helmet, every gear whole, none cut by the plate's chrome edge. Parked and riding, by day and at night. Compare it
    with your layout: should the gears be bigger, or placed differently? Everything else on the badges as in test 59.
    - `Papyrus.0.log`: `Customise: tank left = TankL:boshelm3d (18)`, `... tank right = TankR:boshelm3d (19)`.
13. **The Wear and Paint condition on all four bikes, and how quickly**: Wear "Wasteland" or "Rusty" with Paint
    condition "Chipped". Look at the kit's preview; close the kit: the parked bike blinks once a couple of seconds later
    and should show the wear and the chipped paint right after the blink. Get on at once and look at the bike as the
    screen comes back in third person: the wear from the first moment, no clean bike first. Draw a pistol and put it
    away a few times while riding in third person: the bike may flash clean for a split second at most (test 59: clean
    for 2-4 s after each). Switch to first person: the bike under you as before. Get off and look at the parked bike
    beside you: the wear within a second of the screen coming back. Five getting-ons, some straight after the kit and
    some later. Then save beside the bike, change the Wear at the kit, and load that save: the parked bike (and the bike
    under you after getting on) shows the save's Wear, not the newer one.
    - `CMB_Slope.log` at the start: `  look (2026-11-23a, test 59): OverlayEvery=1 (...) OverlayQuick=1 (...):
      CMB_LookOptions 8388607 for the scripts`.
    - `Papyrus.0.log`, every getting on: `Look: the worn bike's 3D: the look's swap at runtime too, 39 entries applied
      (OverlayRuntime, the compose reused, 0.3 s after its equip, under the getting on's fade)` (with `try 2` when the
      first try came before the bike's 3D was built), then `... (OverlayRuntime, the compose reused, 1.3 s after its
      equip, the confirming swap)`; every weapon draw and put-away the same two lines, about 0.2-0.4 s and 1.2-1.4 s
      after the equip (test 59 had them at 5 of 21 getting-ons, 4-5 s after the draws).
    - Every getting off, within about a second of `Dismounted.`: `Look: the parked bike's fresh 3D (its 3D's load): the
      look's swap at runtime too, N of M entries applied (OverlayParked, the compose reused)` (test 59: never at a
      getting off).
    - After the kit: `Look: the parked bike's swap holds N entries, kept for its 3D's next load ... (ParkedSwapHold:
      loaded again)`, `Look: the parked bike's 3D loaded again for its colours (the field kit, ParkedReload)` (the
      blink) and right after it the `fresh 3D ... (OverlayParked, the compose reused)` line; in first person `Look: the
      first-person bike: N of M entries applied, colours: ... (OverlayQuick: the compose reused)`.
14. **The A/Bs**: one at a time, back to 1 after: `[Look] OverlayQuick=0` (the wear comes 2-4 s after each equip again),
    `OverlayEvery=0` (the wear missing at most getting-ons and on the parked bike after getting off, as in test 59),
    `OverlayParked=0` (test 59's parked bike: no Wear or Paint condition on it at all).

The changed art's A/B is files: the 2026-11-22a package's `Data\Textures\CMB\Bike\` `badges_d.dds`, `badges_n.dds`,
`badges_s.dds` (the big gear behind the helmet, one smaller either side) and the 30 `wear_rusty_*` and `wear_raider_*`
maps (`_d`, `_n` and `_s` of `static`, `fork`, `static_engine`, `static_exhaust` and `fork_black`: 22a's rust), in a
small MO2 mod of their own ticked below this one (README's table of this build's art switches).

### The field kit (2026-11-23a): step 15

(test 59: "between every option bike gets into default position for a moment": at each option the menu puts the new bike
in at its own three-quarter pose in its own update of the frame, after the plugin's turn, so one frame was drawn so)

15. **No flash between options**: Customise, the Motorbike, the Fender slot (the rear fender from above). Press E and
    move up and down its mods one by one, slowly and then quickly: the bike should stay on the fender view at every
    option, with no frame of the usual three-quarter pose in between. The same on Plate text (the rear) and Tank L (the
    left side). If you record, a few seconds of it at 60 fps help.
    - At the first Customise of the session: `kit: late: ExamineMenu's AdvanceMovie (+0x...) and PreDisplay (+0x...)
      wrapped (vtable +0x..., slots 4 and 5, passed through): ...` (or `kit: late: ExamineMenu: <why>`).
    - At each close, before 2026-11-22a's close line: `kit: hold (2026-11-23a): the menu's bike (item ...): the menu
      closed; the new drawn bikes: A placed right after the menu's AdvanceMovie, P at its PreDisplay (KitLate: ...), O
      first seen by the frame task already at the visit's view, M at the menu's own pose (drawn so a frame); the loaded
      bikes not drawn placed ahead N time(s), K at most at once (KitPrePlace)`. M should be 0; send the line either way:
      A, P and O say where the menu puts its new bike in, and its end, `the list's stride not found in N frame(s), an
      unreferenced model skipped M time(s)`, how often the bikes not shown yet couldn't be turned.
    - A flash still seen: `kit: late (2026-11-23a): a new drawn bike ... drawn so for a frame` lines, one each. A/Bs:
      `[Look] KitLate=0`, then `KitPrePlace=0`: better or worse?

### A pistol out: the left hand on the bar (2026-11-23a): steps 16-19

(test 59: "the character isn't aiming, but she still holds the gun with both hands": in third person both hands were on
the bars with the pistol in the right fist on its grip; in first person your body vanished at a draw and the game's own
arms held the pistol in both hands; your pick: the left hand back on the left grip in both, the gun one-handed)

16. **Third person, a draw**: ride in third person a few seconds with the pistol holstered, then draw the 10mm (its
    number key) while riding. Your left hand should stay on the left grip, and your right hand should come off the right
    grip and hold the pistol out over the bars, pointing ahead. Does the pistol look upright or on its side? Does the
    right wrist or elbow look bent wrong? Then the .44 the same way. A screenshot from the side and from behind.
    - Each draw: `gun: a handgun out (the weapon state 2, the gun state 0) at N u/s: the rider on the riding seat pose
      read N s ago, the left hand on its grip, the right holding the pistol off the bar (GunOneHand) (GunPose)`, then
      `gun: one-handed (GunOneHand): the right hand off its grip on the hold 9.7 from the seat pose's wrist (GunHoldAt
      -3,-2,9), the arm at N% of its reach, the wrist turned N deg from the seat pose; the pistol's barrel (its 3D's +Y)
      N deg off the bike's heading in the seat pose's fist, turned onto it; its up N deg from the bike's; the left hand
      on its grip`. "Its up" 0 is upright, 90 on its side.
    - If instead `gun: one-handed: the pistol's barrel (its 3D's +Y) N deg off the bike's heading ..., over 75: not
      turned, the fist's own kept (GunOneHand)`, say which gun: its barrel isn't along its +Y.
17. **Fire and put away, third person**: fire a few shots riding in third person: the shots go where they did in test
    59. Put the pistol away while riding: the right hand goes back onto its grip, smoothly.
18. **First person**: switch to first person and draw the pistol. You should still see your own body, legs and left arm,
    the left hand on the left grip, and only one arm, the right, holding the pistol (test 59: the body gone, both hands
    on the pistol). Fire a few shots, reload, then put it away: your right arm back on its grip.
    - The draw: `body: first person, a handgun out (BodyGunGrip): your body shown, its left hand on the grip, its right
      arm's N bone(s) shrunk at the shoulder; the game's first-person 3D's left arm shrunk to a speck: N bone(s) in M
      skinned shape(s) (...), its right arm and pistol as the game has them` (test 59 had `body: first person: the
      rider's body not shown: a weapon out`).
    - The put-away: `body: the first-person 3D's left arm given back after N s (the weapon away): M shape(s) on their
      own bone data again`.
    - Is a second left hand or arm anywhere in view (the game's, not shrunk)? Does the right shoulder look joined?
19. **Menus and edges with a pistol out**: with the pistol out in first person open the Pip-Boy and close it; look back
    over your shoulder; switch to third person and back. Then get off with the pistol out in first person, and on foot
    draw and put away the pistol in first person. Nothing should be left missing: on foot both of the game's arms as
    normal, the Pip-Boy arm normal.
    - Each time the body stops showing with the gun: the `... left arm given back after N s (<why>) ...` line; `(a new
      first-person 3D)` as the why means the game replaced its first-person arms while the gun was out: say what you did
      just before.
    - A/Bs: `[Tilt] GunOneHand=0` (third person: both hands on the bars, test 59's), `[View] BodyGunGrip=0` (first
      person: test 59's); if the hold's place is off, `[Tilt] GunHoldAt` (x out, y forward, z up from where the hand
      sits on its grip; -3,-2,9 shipped).

### The look in third person (2026-11-23a): steps 20-21

(test 59: "right-click/Z for free camera doesn't work when gun is out in 3rd person camera", and with no gun out "yes,
works correctly": with no weapon drawn the game's own free camera swung as well as the plugin's orbit, 95 degrees round
against the orbit's 48, so the orbit switched itself off for the session on the first hold; with a weapon drawn the game
keeps its camera behind you, and only the orbit could have swung it)

20. **No weapon drawn**: ride in third person at speed, hold the right button (or Z) and move the mouse left and right:
    the camera should swing round you smoothly, as far as you move it, the bike going straight on. Let go: the camera
    comes back behind you. Do it again three or four times: it should work every time (in test 59 the orbit worked only
    for its first half second, the game's own look after).
    - Each release: `view: that hold: the game swung the camera itself on N frame(s), the plugin on M (a weapon away)
      (LookOrbitGame)`, N much larger than M; `view: the third-person camera back behind you after T s (...)
      (LookOrbit)`, `...; the game's own return, the ease's writes not followed (LookRecover)) (LookOrbit)` when the
      game brought its camera back itself.
    - No line says "off this session" any more. If a check fails: `... the camera the game's own for this hold, the
      orbit tried again at the next (LookRecover)`.
21. **A weapon drawn**: draw the 10mm, still in third person, riding. Hold the right button (or Z) and move the mouse:
    the camera should swing round you too, up to about a quarter turn either side (60 degrees), and come back behind
    when you let go; this is what didn't work in test 59. Put the weapon away and draw it again, a few holds each way.
    - `view: that hold: the game swung the camera itself on 0 frame(s), the plugin on M (a weapon drawn)
      (LookOrbitGame)`.
    - A/Bs: `[View] LookOrbitGame=0` (2026-11-22a's orbit every frame, with no weapon too: test 59's 95 against 48, but
      for that hold only), `LookRecover=0` (2026-11-22a's checks: the first that fails switches the orbit or the ease
      off for the session).

### The holster on your thigh (2026-11-23a): steps 22-23

(test 59: "guns are still showing up in random places": your body's skins hang on helper bones beside the thigh's own
bone, so the holster mod's copies under 'RLeg_Thigh' were never found as hanging off your body; in the moment right
after a put-away, while the plugin still holds your seat pose, they were drawn where the game's standing clip has the
thigh; and a dark thing lay along your right forearm in third person)

22. **Riding holstered**: ride in third person and put the 10mm, the .44 and the flare gun away in turn while riding,
    straight and leaning in turns, over a few bumps. Each holstered pistol should sit on your right thigh and stay there
    through the leans and the bumps. Look at your right forearm too: is anything lying along it, and is it there before
    any draw? A short video.
    - At each put-away: `rider: an attachment: 'WeaponPistolUp' < 'RLeg_Thigh', N held shape(s) ('...' ...), hangs off
      the skeleton's 'RLeg_Thigh' (no skin's bone: the body's skin there through '...' under it, AttachSkeleton); the
      body's part there none (the tilt alone) (AttachWhere)` (", new shapes" at the next put-aways of a ride); the flare
      gun's the same.
    - At 0.5 s and 2 s: `rider: the attachment 'WeaponPistolUp' at 2.0 s (tilted): its root (...) from the bone
      'RLeg_Thigh' in the bone's frame (...); its shapes' written transforms put it 0.00x to 0.0xx off that place from
      the drawn bone; ...`: near 0, it follows the thigh. A copy not drawn as written yet: `...; left out: N not updated
      by the game (...), N hidden (AttachFresh)`.
23. **Right after a put-away (posed)**: draw a pistol and put it away while riding in third person, and watch your thigh
    in the half second right after the put-away, when your arms go back to the bars: the holstered pistol should be on
    your thigh from the first moment, not off to the side. Do it standing on the bike, slowly and at speed, three times
    each.
    - The seat pose's line counts more bones (`the seat pose read (still, N bones ...)`: the skeleton's nodes over your
      skins' bones), and at the put-away the attachment line as in step 22.
    - A/B: `[Tilt] AttachSkeleton=0` (2026-11-22a's: no `an attachment:` line for 'WeaponPistolUp', test 59's).

### A stimpak in third person (2026-11-23a): steps 24-25

(your pick after test 59: no healing clip on the bike in third person, the item still used: "it would make more sense to
not have any healing animation in 3rd person unless you can fix it"; in test 59 a stimpak by its number key at a crawl
played the game's own clip, the hands off the bars, and one from the Pip-Boy played its clip after the menu closed)

24. **By its number key**: riding in third person, use a stimpak by its number key at full speed, then riding slowly,
    then standing still on the bike. Each time: no injection clip, both hands on the bars, the health restored (the
    plugin hands the item to the script, so any clip is cut where it starts).
    - Slow or standing: `quick: key 0x.. (the slot N, the game's 'QuickkeyN') at N u/s: Stimpak (00023736, a potion)
      handed to the script's watch, not the game's animated use (...): CMB_RiderQuickUse N (UseNoClip: under
      QuickUseAbove, in third person)`; at speed the same line without the `(UseNoClip: ...)` (as before).
25. **From the Pip-Boy, and the Favourites menu**: riding in third person, use a stimpak from the Pip-Boy at full speed,
    then slowly, then standing on the bike: no clip after the Pip-Boy closes (its item is applied in the menu, so the
    clip is cut at its first frame), both hands on the bars, the health restored. Then from the Favourites menu (hold
    the number key, or the d-pad's wheel): its clip may play a moment and is cut when the item comes; the health must be
    restored every time. Then the case 2026-11-23b fixes: open the Pip-Boy, close it with nothing used, and within a
    second use a stimpak from the Favourites menu: a short clip may play, but the health must come back (in 2026-11-23a
    it was cut as the Pip-Boy's and the heal was lost). Do it three times, at speed and slowly. Then the same, by key,
    from the Pip-Boy and from the Favourites menu, in first person: as in test 59 (the plugin leaves first person
    alone).
    - After the Pip-Boy: `rider: an item's use clip at N u/s (its props, Stimpack:0 < ... < AnimObjectL1, this frame;
      the Pip-Boy open N s before them, no other cause: its item applied in the menu, in third person no use clip
      (UseNoClip)): IdleStop sent to the graph (UseStop): taken; the clip over after 0.0x s`.
    - From the Favourites menu, also right after the Pip-Boy: `... no item used yet (...): left to play until it is`,
      then `rider: an item's use clip at N u/s (the item used N s into its clip, CMB_RiderItemUse N; ...): IdleStop sent
      ...`, at any speed; never `the Pip-Boy open N s before them ...` for a Favourites use (the Pip-Boy's window lasts
      1.5 s after it was last open, and the Favourites menu ends it).
    - At the ride's end: `quick: this ride in third person: N item use clip(s) cut at their props after the Pip-Boy, N
      potion key(s) under QuickUseAbove handed to the script (UseNoClip)`.
    - A/B: `[Steer] UseNoClip=0` (the clip as in test 59, the hands off the bars meanwhile).

### The frame rate (step 26)

26. **As in test 59**: ride as you usually do for a few minutes, in a town and in the open, and stand 3-4 m from the
    parked bike at a fixed spot for 20 s, with Wear "Wasteland" and Paint condition "Worn": any frame drops, at the
    kit's options, at a getting on, at a weapon's draw? (test 59: "didn't notice any frame drops"). `CMB_Slope.log`'s
    `time: the last 10 s: N frames a second (...)` lines say it too.

Send `CMB_Slope.log` and its `_prev` logs and `Papyrus.0.log` of each session, the screenshots of steps 1-5 (the bike
beside you on flat ground, on a slope, by a wall, by a car, leaning across a slope both ways), 10-13 (Rusty and Raider
at the badges and riding, every Wear's badges, the gears beside the helmet, the four bikes with the wear) and 16-18 (a
pistol out in third and first person), and a short video of steps 1 and 6 (the blacks), 15 (the kit's options), 20-21
(the look), 22-23 (the holster) and 24-25 (a stimpak) if you can.

### Questions for you (test 60)

- **T60-1 (step 1).** Getting off on flat ground: the bike beside you on your right, in view? The black shorter than
  test 59's?
- **T60-2 (step 2).** On slopes, up, down and across both ways: still beside you, the tyres on the ground?
- **T60-3 (step 3).** A wall on your right: the bike on your left? No room either side: back along the track?
- **T60-4 (step 4).** By a car, a curb, a step: both tyres on the ground or the edge, never on the car or sunk in?
- **T60-5 (step 5).** The lean: on its stand on flat ground, at least a little with the stand uphill, no more than 20
  with it downhill, after a swim and a call? Does 5 or 20 look right?
- **T60-6 (step 6).** Getting on: the bike gone at the press or under the fade, no blink? As quick as test 58's? The
  vanishing at the press acceptable?
- **T60-7 (step 7).** Which of `ParkBeside=0`, `ParkLean=`, `ParkTyres=0`, `MountHide=0` was better than the default, if
  any?
- **T60-8 (step 8).** The take-off brisk enough now (or too quick, or jerky), from a stand and right after stopping?
- **T60-9 (step 9).** The gears still at about 12, 24, 36 and 46, each revving out before it changes? The coast and the
  brake as before? 2026-11-22a's take-off better?
- **T60-10 (step 10).** Rusty: no frame round the plates, lighter, see-through with dark edges? Too faint now?
- **T60-11 (step 11).** Raider the same? A frame round a plate with any Wear?
- **T60-12 (step 12).** The three gears either side of the helmet: as your layout? Bigger, smaller, moved?
- **T60-13 (step 13).** The Wear and Paint condition on all four bikes, at once after the kit's blink, from the first
  moment after getting on, within a second after getting off, at most a split-second clean at a draw?
- **T60-14 (step 14).** `OverlayQuick=0`, `OverlayEvery=0`, `OverlayParked=0`: worse, as expected?
- **T60-15 (step 15).** No frame of the menu's own pose between options? What did the `kit: hold (2026-11-23a)` lines
  count?
- **T60-16 (step 16).** Third person, a pistol drawn: the left hand on its grip, the right holding the pistol over the
  bars, pointing ahead? Upright or on its side? The wrist and elbow right?
- **T60-17 (step 17).** The shots as before? The right hand back on its grip at the put-away?
- **T60-18 (step 18).** First person, a pistol drawn: your body and left hand on the grip, one arm on the pistol? A
  second left hand anywhere? Firing and reloading right?
- **T60-19 (step 19).** After the Pip-Boy, a look back, third person and getting off with the pistol out: nothing left
  missing? `GunOneHand=0` or `BodyGunGrip=0` better?
- **T60-20 (step 20).** No weapon: the camera round you every time, back behind when you let go?
- **T60-21 (step 21).** A weapon drawn: the camera round you up to a quarter turn, back behind? `LookOrbitGame=0` or
  `LookRecover=0` better?
- **T60-22 (step 22).** The holstered pistols on your thigh through leans and bumps? Anything along your right forearm?
- **T60-23 (step 23).** Right after a put-away: on your thigh from the first moment? `AttachSkeleton=0` worse?
- **T60-24 (step 24).** A stimpak by its key in third person, fast, slow and standing: no clip, the health restored?
- **T60-25 (step 25).** From the Pip-Boy in third person: no clip after it closes? From the Favourites menu, also right
  after the Pip-Boy: the health every time? First person as before?
- **T60-26 (step 26).** Any frame drops?

### The open questions and the lines that settle them (test 60)

For your checker: what each part of this build couldn't settle offline, the log line that settles it and the A/B it
suggests.

- **Getting off beside you** (steps 1-4): the spot is 65 to the player's right (else their left) and 28 ahead, where the
  worn bike's middle was, along their heading; in first person it is beside you, not in front. With ParkFit on, a side
  where both tyres won't sit on the ground (a ledge, a drop) counts as no room (`... not fitted there (its fit's line
  says why): no room on this side`); with ParkFit=0 the beside spot is settled as 22a's checked spot (PlaceOnSpot). The
  bike is set at the spot the plugin checked, the player's roll during the ask not added. Neither side free: the track's
  spot, behind the camera, as before. Lines: `room: ask N ... (the parked bike beside the player: ParkBeside): ...` and
  `Parked bike beside the player (the plugin's [Room] ParkBeside, one ask): ...`; none on either side: `... none on
  either side (the plugin's lines say why).`. A/B `[Room] ParkBeside=0`.
- **The getting-off and getting-on times** (steps 1 and 6): the harness can't time Papyrus. Getting off makes one ask
  where 2026-11-22a made four (0.7-0.8 s of asks in test 59, each 0.20-0.28 s); getting on drops the stand-up's turn
  taking with the controller and the reload before the fade: a runtime-swapped parked bike (most getting-ons) is hidden
  at once as E is pressed, before the fade, so it is never drawn into the getting on (test 58's crash guard; since
  2026-11-23b with any `[Look] MountGuard` and `ParkedSwapHold`, 2026-11-23a skipping it with `MountGuard=1` and
  `ParkedSwapHold=0`), and one without a swap 0.2 s into the fade; a failed or undone getting on brings it back where it
  stood (MountUndo). The rest of test 59's 0.5 s (the heavier worn mesh's equip, ParkedSwapHold's mount line) is not
  touched. Lines: `Getting on: the press 0.00, the fade ..., ... Mounted ... (real seconds)`, the mount line's `... its
  3D hidden at once, before the fade (MountHide: no reload; ...)`, `Getting on: the parked bike hidden under the fade
  before the equip (...)`. A/B `[Room] MountHide=0`.
- **The lean** (step 5): a rigid bike whose foot is on its ground can't rest on its stand where the ground rises toward
  it, nor lean over 20 degrees without tipping, so the lean from upright is held to 5..20 and the foot goes a few units
  into the rise (3.7 in the harness at test 59's worst) or over the fall (3.0); on pavement that may show. A bike turned
  to cut a steep cross slope would need the placements to choose the heading: not done. Lines: the fit line's `leaning X
  on its stand from upright: roll -X` and `(its ... from upright held to 5: the foot ... into its ground)`. A/B `[Room]
  ParkLean=` (2026-11-22a's), or other bounds (`ParkLean=<min>,<max>`, within 0 to 40).
- **The tyres** (step 4): the tyres' rays still start 88 up; ParkTyres sets aside one tyre's ground more than 12 over
  the line from the other tyre through the middle's (a thing over one contact), not both at once, and a real step higher
  than 12 under one wheel is taken as a thing and looked under. Lines: `; the rear tyre's ray met something ... looked
  under it, ...`, `; the front tyre raised ... (its footprint)`. A/B `[Room] ParkTyres=0`.
- **The Wear on every bike** (step 13): F4SE's runtime swap alone draws the overlays (test 59), so every bike gets one:
  the worn bike two per equip (the confirming one: a re-equip's first swap can land on the 3D it replaces), the parked
  bike one per load, the kit's reload (the blink) kept because it gives the runtime swap a fresh 3D (every crash of
  tests 54 and 58 came after a swap on a long-drawn parked 3D). The worn bike is clean for the frames between its 3D's
  build and the swap (0.1-0.3 s, under the fade at a getting on); the parked bike blinks once at the kit's close. After
  a save load the look is composed afresh (the reused swap carries a marker of its look, and a load forgets it). Lines:
  the `Look: ... (OverlayRuntime, the compose reused, N s after its equip, ...)` and `(OverlayParked, the compose
  reused)` lines. A/Bs `[Look] OverlayQuick=0`, `OverlayEvery=0`, `OverlayParked=0`.
- **The rust's strength** (step 10): at riding distance the new rust is light in our renders; the game lit 22a's
  brighter and more orange than the renders, so it should read, but if it is too faint the knobs are the blooms'
  threshold and their body's alpha in `look_wear.py`'s `layer_rust_light` (behind the same flag). Raider's blood across
  the left plate's art is Bloody's (unchanged since 22a), not an outline. The A/B is the 2026-11-22a package's 30 maps.
- **The gears' layout** (step 12): three a side in a flank 146 px wide, the large ones' tips 36.6 px and the small ones'
  25.6 (smaller than 22a's flank gears, 54.7), mirror images left and right (your sketch's right group sat a little
  higher), meshing where your sketch's gears float apart. A layout change is in `bike_art.py` (`BOS23_TRAIN`); the A/B
  is the 2026-11-22a package's atlas.
- **The kit's flash** (step 15): that the menu puts its new bike in during its own update, after the plugin's turn of
  the frame, is read from test 59's log and video, not seen. Which call of the menu does it isn't known: the late pass
  runs after both AdvanceMovie and PreDisplay; later than both, or off the frame task's thread, and the flash stays.
  Line: `kit: hold (2026-11-23a): ...` (M 0: gone; M over 0 with X over 0: another thread). KitPrePlace's list stride is
  found from its live entries (0xA0 in test 59): while a model is still loading no stride fits and nothing is pre-placed
  that frame (the line counts them). A/Bs `[Look] KitLate=0`, `KitPrePlace=0`.
- **A pistol, third person** (steps 16-17): the barrel's axis is taken as the weapon 3D's +Y (the model's forward in the
  game, not proven), the turn capped at 75 degrees; the hold's place (`GunHoldAt`) and the arm at about two thirds of
  its reach are a first set. Lines: `gun: one-handed (GunOneHand): ... the pistol's barrel (its 3D's +Y) N deg off ...;
  its up N deg from the bike's ...`. A/Bs `[Tilt] GunOneHand=0`, `GunHoldAt`.
- **A pistol, first person** (steps 18-19): the game's first-person arms are drawn in a frame of their own, so their
  left hand isn't put on the grip; the plugin shrinks their left arm through copies of its shapes' bone data and shows
  your body's left arm instead. That the first-person pass draws through that bone data, that the game's right arm with
  your body's torso reads as one rider, and how a reload's left-hand clip looks with that arm shrunk are the game's to
  show. Lines: `body: first person, a handgun out (BodyGunGrip): ...` and `body: the first-person 3D's left arm given
  back after ...` (`(a new first-person 3D)`: the game replaced it while held; the review's fix gives the old shapes
  back first and holds 24 at most). A/B `[View] BodyGunGrip=0`.
- **The third-person look** (steps 20-21): which of two readings of test 59's 95 against 48 is the game's (its free
  camera swinging from its own state, the plugin's writes not shown; or its swing added on top of the writes) is for the
  hold line to say: `view: that hold: the game swung the camera itself on N frame(s), the plugin on M (a weapon away)`;
  M on most frames with the camera doubled would say the second, with the plugin's "ahead" rule acting. The 21a ease's
  watch keeps the bike's line up to 1.5 s while the game brings its camera back. A/Bs `[View] LookOrbitGame=0`,
  `LookRecover=0`.
- **The holster** (steps 22-23): in the game the holster's copies already took no part of their own by their names, so
  outside the pose they moved with the thigh in 22a too; what AttachSkeleton changes there is that they are found
  (AttachBoneRole, AttachHide, AttachWhere act on them), and in the posed moment after a put-away (about 0.4 s in test
  59) that they are carried with the thigh. The dark thing along the right forearm in test 59's picture was still there
  after the .44's copies were let go, so it may not be the holster's: the right arm wears skinned gear another mod adds,
  held with the upper arm (the `N with an upper arm; placed by the node they sit on` lines). Lines: `rider: an
  attachment: 'WeaponPistolUp' < 'RLeg_Thigh', ...` and its `at 0.5 s` and `at 2.0 s` lines. A/B `[Tilt]
  AttachSkeleton=0`; `[Diag] AttachFresh=0` changes only the measures.
- **No item clip in third person** (steps 24-25): a number key the plugin couldn't take is left to the game's own use
  (cut and handed to the script by QuickCut, or the game's clip waiting for its event, as before), and a clip is cut at
  its first frame only where the item is known to be applied or handed over (the plugin's own hand-over of a number key,
  or props within 1.5 s after the Pip-Boy was last open, with no other menu since: since 2026-11-23b read from the UI's
  own menu stack, 4 s and the script's `CMB_ViewMenu` in 2026-11-23a); any other (the Favourites menu, another mod's
  route) plays until its item comes, the hands off the bars meanwhile as in 22a, and is cut then, so the heal is never
  lost. The Favourites menu, or any other menu opened after the Pip-Boy, ends its window, so a Favourites use right
  after the Pip-Boy keeps its heal (2026-11-23a's open edge, fixed in 2026-11-23b; harness UN8); with the UI unreadable
  there is no window at all (the wait, the safe side). Lines: `rider: an item's use clip ... in third person no use clip
  (... UseNoClip)): IdleStop sent ...`, the quick line's `(UseNoClip: under QuickUseAbove, in third person)` and the
  ride's `quick: this ride in third person: ...` line. A/B `[Steer] UseNoClip=0`.
- **The take-off** (steps 8-9): the game was fitted to test 59's 16 pulls from rest (its follow slower at small inputs,
  about 110 u/s^2 under 100 u/s from a stand; rms 5.6 u/s) and the fit reads about 0.1 s slower than test 59's own
  lines, so about 1.55 / 2.65 s from a stand and 1.3 / 2.65 warm in the game. The twin (`tools/sound/engine_model.py`)
  keeps its 2026-11-17a defaults. Lines: the `launch: from rest: ...` and gear lines. A/B by hand (no DEF64 key):
  `[Steer] LaunchFrom=0.14` with `[Sound] HeardRiseGears=2,0.86,0.8,1,1`.
- **The cost** (step 26): the kit's late pass and pre-placing run only in a held kit visit; the overlays add one or two
  runtime swaps an equip and one a parked load; the look's swing test is a few reads a frame of a held look. No new
  shape or texture.

## Test 59: the 2026-11-22a build (test 58's fixes and your wishes, art build C)

The 2026-11-22a build answers test 58 (run on 2026-11-21a): its fixes and every wish you made (your pick: "Everything"),
in one build. Step 1 is test 58's crash, tried again first; steps 2-12 are the art, steps 13-15 the field kit, steps
16-21 the parked bike, steps 22-25 the look and the aim, steps 26-29 the gears, steps 30-32 other mods' attachments,
step 33 the frame rate and step 34 the A/Bs, with the questions T59-1 to T59-34 at the end and, after them, the open
questions and the log lines that settle them. What test 58 liked (the plates, Red Rocket, the Enclave's flag, the bike
after your body, the stops) is as it was.

- **The crash:** the field kit's new look no longer goes onto the parked bike the game is showing while you get on (test
  58's two crashes: a Headlamp colour picked, Ride pressed at once).
- **The art (art build C, your wishes):** a Paint condition slot under the Wear (Scratched, Chipped, Sun-faded, Worn,
  Primer patches: "scratched, chipped and weathered paint and then on top of that rusty/muddy"); the Wear on the exhaust
  pipes and mufflers, the engine's outer covers and the front fork's lowers too, and over the tank and rear badges; the
  Wear (and Paint condition) on the parked bike and the bike under you in third person, not only in the kit and in first
  person; the muddy tyres' tread clean and black where it meets the road; three meshing black gears on metallic blue
  behind the 3D Brotherhood helmet; the Nuka-Cola badge's script neater; six more headlamp colours (Halogen, Daylight,
  Ice blue, Red, Green, Purple); and the front fender badge taken out ("I would drop front fender badge").
- **The field kit:** the bike on screen turns to each slot (the plugin now holds the bike the menu really draws), the
  wheel zooms out as well as in, and with the cursor over the list panel the wheel scrolls the lists as the game does
  (your pick); anywhere else it zooms.
- **The parked bike:** set on the ground under both its tyres wherever you park it, leaning a little to its left on its
  own side stand, which is down now; getting on stands it up.
- **The look and the aim:** the right button no longer aims or slows the bike (2026-11-21a's block never switched on:
  the game names its handler otherwise), so the Pip-Boy should open while you look; in third person the plugin swings
  the game's camera round you itself, with Z or the right button.
- **The gears:** the up-shifts at about 12, 24, 36 and 46 on the dial in every pull, also one begun rolling or up a hill
  (test 58: 4th at about 32 and 5th at about 43 in pulls begun rolling); a menu that pauses the game at speed (the
  Pip-Boy) no longer cuts the throttle.
- **Other mods' attachments:** your holster mod's pistol stays on your thigh while you ride (test 58: "holstered to
  random places, often outside of the body"), and a backpack or anything else another mod hangs off your body follows
  it.

Four things to know first: the front fender badge is gone (not in the kit or the MCM, never drawn; a save that had one
shows none); at the kit the wheel scrolls the lists with the cursor over the list panel and zooms the bike anywhere
else; the parked bike leans on its side stand (on its left, under the footpeg); and Paint condition and Wear can be
chosen together, the paint's damage under, the grime on top.

Do this section's steps in one game session if you can, in this order (step 1 first, the art and the kit by the parked
bike in one of your settlements, the headlamp at night, then the rides), and say which session each step was in. Every
new behaviour of the plugin has a key whose off value gives the 2026-11-21a build back (README's table of this build's
keys), so each A/B is one key away; every new look choice is opt-in, and the changed art's A/B is files (after step 12).
Things only the game can settle: whether the crash is gone (step 1), whether the meshes' blending alone shows the Wear
on the parked bike (steps 4-5), in which order the game draws two see-through layers (Paint condition under the Wear,
step 3), which bike the armour menu draws and how the game sends the wheel's down notch (steps 13 and 15), which way the
bike leans on its stand and what it does beside a car or a ledge (steps 16 and 18), whether the game keeps its
third-person camera where the plugin puts it (step 24), and where the holster mod's copy sits against your thigh (step
30).

Before you start:
- install as a Replace over 2026-11-21a. If you edited `CMB_Slope.ini`, put your values into the new one: `[Look]`,
  `[View]`, `[Steer]`, `[Sound]`, `[Tilt]`, `[Room]` and `[Diag]` have new keys (`[Look] OverlayParked` off by default,
  an A/B for step 5), no default changes, and `[Look] KitViewFrontFender` is gone (README's table). Otherwise use the
  shipped file as it is;
- load your usual save, and save again before step 1 (it repeats test 58's crash). The same load order as test 58: your
  visible-holster mod on, and a backpack mod if you have one (step 31);
- the ESP and the MCM change: the MCM's Look section still has 25 controls, with "Paint condition" after "Paint shade"
  and no "Front fender badge", and "Headlamp" lists eleven colours. If it shows "Front fender badge", an older ESP or
  MCM folder is loaded: stop and say so. Riding's "Weapons while riding" on "Handguns only";
- the first time you get on after the update the look's mods go on afresh once (the look has a new slot):
  `Papyrus.0.log` says `Look: put on (load)` once and the worn bike's mods attached afresh; a second getting on is as
  quick as before. A 2026-11-21a save starts with Paint condition "Pristine (as it came)"; a front fender badge it had
  is gone;
- note your frame rate beside the parked bike on 2026-11-21a before you install, if you can (step 33; test 58 gave no
  figures);
- have the 10mm pistol and the hunting rifle on the favourites' number keys;
- the headlamp's step wants night: wait for it, or in the console `set gamehour to 22`;
- each A/B below: change one key in `CMB_Slope.ini`, save the file, get off and on (no restart), and put it back after.

The log's first lines: `CMB_Slope.log` has seven settings lines more: `  look (2026-11-22a, test 58): ParkedSwapHold=1
(...) OverlayRuntime=1 (the look's swap at runtime too on the worn bike after each equip) OverlayParked=0 (the parked
bike's load swap alone); [Diag] LensLine=1: CMB_LookOptions 1048575 for the scripts`, `  look (2026-11-22a, test 58):
[View] LookOrbit=1 (...) LookOrbitGain=0 (...); [Steer] AimStruct=1 (the aim's handler by its struct's name too,
1.11.240's)`, `  kit (2026-11-22a): [Look] KitDrawn=1 (...) KitWheelDown=1 (...) KitWheelLists=1 (...) KitSlots22=1
(...); views (heading, elevation): paint condition -45,15`, `  attachments (2026-11-22a, test 58): AttachUnclone=1
AttachBoneRole=1 AttachHide=0 [Diag] AttachWhere=1 (...)`, `  sound (2026-11-22a, test 58): UpBands=215,429,644,823: in
a pull (the bike gaining 40 u/s^2 or more) ...`, `  steer (2026-11-22a, test 58): MenuKeep=1: ...` and `  room:
ParkFit=1: the parked bike set on the ground under its tyres after every placement (...); ParkStand=17.28,2.97,2.61:
...`. No 2026-11-22a lines, or `UpBands=: ... (the 2026-11-21a build)` and `ParkFit=0: ... (2026-11-21a)` with an INI
you didn't change, mean an older `CMB_Slope.dll` or `CMB_Slope.ini` is loaded: stop and say so.

### Test 58's crash, again (2026-11-22a): step 1

(test 58: "game crashed after selecting lamp color": both crashes came at a getting on right after a Headlamp colour was
picked, the kit closed and Ride pressed within 4 s, while the kit's new look was still being put onto the parked bike;
test 54's two crashes at the kit were the same kind)

1. **A change at the kit, then Ride at once**: save first. At the field kit pick a Headlamp colour, close the kit and
   press E on the bike straight away (Ride). Ride a few seconds, get off, and do it again, five times or more: with
   different colours, twice with a Wear or a Paint condition changed in the same visit, once with nothing changed. The
   game should not crash. If it does, send the crash log with both logs and say which try it was.
   - `Papyrus.0.log`, when E comes while the kit's look is still being put together (test 58's case): `Look: the parked
     bike's swap holds N entries, kept for its 3D's next load, none applied to the 3D it shows (the field kit;
     ParkedSwapHold: getting on)`, then `Getting on: waited X s for the parked bike's look`. At every getting on:
     `Getting on: the parked bike's look at the mount (ParkedSwapHold): ...; the Headlamp Headlamp:<colour> (...)`; with
     the defaults it reads "its 3D with the load's own look (no runtime swap on it)", and "its 3D loaded again before
     the fade" (with step 5's `OverlayParked=1`) means a runtime swap on the parked bike's 3D was thrown away before the
     screen went black, as meant.
   - `CMB_Slope.log`, a moment after each getting on: `lens (2026-11-22a, [Diag] LensLine):
     CMB_BikeWornRiderF_front_glow held at the mount: its 3D ... its shader property ... names
     'Materials\CMB\Bike\front_glow_worn.bgsm'; ...` and 1-3 s later `... changed (...)` with the colour's lens. Send
     them with any crash: they say what both bikes carried in that second.
   - Please don't try `[Look] ParkedSwapHold=0` unless asked: it is test 58's crash condition.

### The art, build C (2026-11-22a): steps 2-12

At the field kit choose each in turn and look at it in the kit's preview, then leave the kit and look at the parked bike
close up (wait 3 s after the kit closes: the wear and the paint's condition go on a moment after the bike shows), then
ride away and look at it from the riding camera (wait 3-4 s after the screen comes back), in third person from the side
and from behind, and in first person where a step says. A screenshot of each, close and riding, please. Every new choice
is opt-in (Paint condition starts "Pristine (as it came)"), and every other plate, badge and seat is as in test 58.

**Paint condition** (steps 2-3; your wish: "there should be an option for paint to be weathered too, now it's always in
pristine condition"; drawn by our own code on two new thin shells 0.16 units over the paint of the tank and rear fender
and of the front mudguard, under the Wear's 0.32, invisible until you choose)

2. **Five looks**: with Wear "As it came", set "Paint condition" to each in turn: Scratched, Chipped, Sun-faded, Worn,
   Primer patches. Look at the parked bike from both sides and from behind, then riding, by day and at night. Does each
   read as its name?
   - Scratched: short fine scratches through the clear coat, a few deeper ones to grey primer and bright steel, scuffed
     patches where things rub; most at the knee grips, on the tank top and on the fenders' tops.
   - Chipped: flaked chips to primer (bare steel in the deep ones) at the rolled edges, the tight bends and the knee
     grips; stone chips on what faces the front wheel and low by both wheels.
   - Sun-faded: a pale, chalky fade, strongest on what faces the sky, mottled, the clear coat peeling in patches on the
     tops.
   - Worn: the three together.
   - Primer patches: nine repair patches (three on the front mudguard) of grey filler primer, two of them red oxide,
     with sprayed, feathered edges and a sanded halo round each.
   - Over a tank badge or the rear badge no scratch, chip or primer (only the fade, at a plate's ends).
   - `Papyrus.0.log`: `Customise: paint condition = PaintWear:scratched (1)` to `Customise: paint condition =
     PaintWear:primer (5)`; at the kit the mods read "Paint condition: Scratched" and so on (Oil 1, Cloth 1).
3. **Under the Wear**: Paint condition and Wear together: Worn with Muddy, Chipped with Rusty, Sun-faded with Dusty,
   Scratched with Bloody, Primer patches with Wasteland. The mud, rust, dust and blood should lie on top of the damaged
   paint, never the paint's damage over the mud. Look along the tank from the side at a low angle and move round it: any
   flicker between the two layers, or a patch where the damage shows through the grime? Once over Gloss black and once
   over Free colour too.

**The Wear on every bike, on more parts and over the badges** (steps 4-7; test 58: "wear is not visible outside of field
kit menu, sometimes only in 1st person"; "all 'wear' option should also be applied on exhaust pipes and other parts of
the bike, not too much but noticeable"; "badges on gas tank are not covered when they should e.g. bloody")

4. **All four bikes**: with Wear "Wasteland" look at the kit's preview, then at the parked bike after the kit closes
   (wait 3 s), get on and look at the bike under you in third person (wait 3-4 s after the screen comes back), switch to
   first person and look down at the tank, then get off and look at the parked bike again (wait 3 s). The wear should
   show on all four (test 58: the parked bike and third person clean): on the parked bike from its meshes now (the
   shells blend in them), on the bike under you through the plugin's swap a moment after the screen comes back. The same
   with Rusty and with Bloody, and once with a Paint condition.
   - `Papyrus.0.log`: after the kit `Look: the parked bike's 3D loaded again for its colours (the field kit,
     ParkedReload)`; after each getting on, 2-4 s after the screen comes back, `Look: the worn bike's 3D: the look's
     swap at runtime too, N entries applied (OverlayRuntime)` (or `Look: the worn bike's runtime swap not put on after
     its compose: <why> (OverlayRuntime)` when you got off or the look changed meanwhile).
5. **The Wear's A/Bs**: if the parked bike showed no wear in step 4, set `[Look] OverlayParked=1` (off by default: an
   A/B for this test): the plugin then also puts the look on the parked bike's 3D at runtime each time it loads, as it
   does on the bike under you. Close the kit or get off, wait 3 s and look again: does the wear show now? Then `[Look]
   OverlayRuntime=0`: does the wear still show on the bike under you in third person, from the meshes alone? Put both
   back after (`OverlayParked=0`, `OverlayRuntime=1`). If the parked bike's wear needed `OverlayParked=1`, also try step
   1 once with it on.
   - With `OverlayParked=1`: after the kit and after getting off `Look: the parked bike's fresh 3D (its 3D's load): the
     look's swap at runtime too, N of M entries applied (OverlayParked), colours: ...`; never under the kit's menu,
     while you get on or ride (re-asked right before the swap): `Look: the parked bike's 3D loaded (...): no runtime
     swap on it, <why> (OverlayParked; at a later load)` or `... no runtime swap on it after the compose, a field kit
     session (OverlayParked; at a later load)`; at the next getting on the mount line's `a runtime swap on its 3D (...):
     its 3D loaded again before the fade` (the bike blinks once at the press).
6. **The parts**: with each Wear in turn look at the exhaust pipes and mufflers (on the right), the engine's side covers
   and air cleaner (both sides) and the front fork's lowers: they carry it too, not too much but noticeable. Weathered:
   the metal dulled, heat colours (blue, purple, gold, straw) on the pipes near the cylinders, chips at the edges;
   Dusty: a film of dust; Muddy: caked low down by the wheels (the fork's lowers by the axle), splashes on the mufflers'
   bottoms and the crankcase's front; Rusty: rust heavy on the mufflers, the seams and the clamps, white corrosion spots
   on the engine's covers; Bloody: drops where the blood reaches. Turn the bars and ride over bumps: the fork lowers'
   grime moves with them. Parked and riding.
   - `CMB_Slope.log` at each getting on: `tilt: CMB_BikeWornRiderF_static_exhaust_wear is a fixed part [none, by its
     name] ...`, the same for `..._static_engine_wear` and `..._static_paintwear`, and `..._fork_black_wear is the lower
     fork (with the bars and the front wheel's travel) [fork, by its name] ...` (and `..._fork_paintwear`); in first
     person `view: the reference ...'s 3D ('CMB_BikeView', ...): 62 shape(s) under 'CMB_BikeView', 62 matched by label
     to the worn bike's 62 held skin(s)` (test 58: 57). No `past the 64 this plugin holds` line.
7. **Over the badges**: with Dusty, Muddy, Rusty and Bloody, a tank badge and a rear fender badge on, look closely at
   the tank's badge plates from the side and at the rear badge: the grime lies over them now (mud and blood where they
   land, dust along a plate's top edge, rust bleeding from under its bottom edge; Weathered only fades them). The 3D
   helmets stand above it (their bases may take a little). No flicker between a badge and the grime at any distance? No
   hard line or frame round a plate?

**The tyres** (step 8; test 58: "tire part where it touches ground is too muddy - it doesn't stick like that irl - black
parts are showing through")

8. **The tread**: set "Tyres" to "Black, muddy", "Whitewall, muddy" and "Red line, muddy" in turn: the tread's faces
   that meet the road black and clean, mud packed between the blocks and on the shoulders, the sidewalls as in test 58.
   Parked close up (kneel by the front wheel) and riding. `Customise: tyres = Tyres:blackmud (3)`.

**The badges** (steps 9-10; test 58: "BoS cogs are showing but I had something different in mind", three interlocking
gears, and "bos helmet background should be metallic blue"; "nuka cola badges are ok, just text looks a bit wonky,
especially in Nuka part")

9. **The Brotherhood helmet's gears**: Tank L and Tank R "Brotherhood helmet (3D)": the plate behind the helmet metallic
   blue with a fine sparkle (it glints as you move round it), and three black gears that mesh: a smaller gear left and
   right of the helmet, each with a ring and a hole showing the blue, and the teeth of a big gear behind the helmet
   showing round its top and bottom and where the small gears bite into it. Parked and riding, by day and at night.
   Should the big gear show more? Is the blue too light or too dark? `Customise: tank left = TankL:boshelm3d (18)`.
10. **Nuka-Cola's script**: Tank L, Tank R and the rear fender "Nuka-Cola": "Nuka" and "Cola" in one even script, the
    same thickness, one slant, sitting on one line, the swoosh clear between the words, nothing touching. The Nuka-Cola
    plate's small cap is as before. `Customise: tank left = TankL:nukacola (20)`.

**The headlamp** (step 11; at night; test 58: "colors themselves are fine, but larger selection is needed")

11. **Eleven colours**: at night, parked and riding, set "Headlamp" to each new one in turn: Halogen (a warm
    yellow-white, like an old bulb), Daylight (a neutral cream white, a touch warmer than Warm), Ice blue (a pale icy
    blue), Red, Green and Purple, then "Warm (as it came)" again. The light on the road takes the colour; Red and Purple
    light the road dimly, as coloured lamps do: should they be brighter? Parked and unlit, Ice blue, Red, Green and
    Purple show a tinted bulb behind the glass (Halogen and Daylight look as Warm). The 2026-11-21a five are as they
    were. In the MCM "Headlamp" lists all eleven, Warm first, then alphabetical.
    - `Papyrus.0.log`: `Customise: headlamp = Headlamp:halogen (5)`, `Headlamp:daylight (6)`, `Headlamp:iceblue (7)`,
      `Headlamp:red (8)`, `Headlamp:green (9)`, `Headlamp:purple (10)` (at the kit Glass 1, Screws 1); `CMB_Slope.log`'s
      lens line names `front_glow_<colour>_worn.bgsm`, and `front_glow_<colour>_d.dds` for Ice blue, Red, Green and
      Purple.

**As it came, and an old save** (step 12)

12. **As it came, and the front fender badge gone**: set Paint condition to "Pristine (as it came)", Wear to "As it
    came", Tyres to "Black (as it came)" and Headlamp to "Warm (as it came)": the bike should look exactly as in
    2026-11-21a, parked, ridden, in first person and in the kit, with no new flicker on the tank, the fenders, the
    exhaust, the engine or the fork's legs. The kit has a "Paint condition" row and no "Front fender badge" row; the
    MCM's Look section "Paint condition" after "Paint shade" (Pristine (as it came), then Chipped, Primer patches,
    Scratched, Sun-faded, Worn) and no "Front fender badge". If your 2026-11-21a save had a front fender badge: after
    loading, nothing on the front mudguard, parked or ridden.
    - `Papyrus.0.log` after loading such a save: `Look: put on (load)` once and, at the first getting on, the worn
      bike's mods attached afresh.

The changed art's A/B is files: the 2026-11-21a package's `Data\Meshes\CMB\` nifs (`CMB_BikeParked.nif`,
`CMB_BikeWorn.nif`, `CMB_BikeWornRider.nif`, `CMB_BikeWornRiderF.nif`, `CMB_BikeView.nif`: no Paint condition or part
shells, the wear shell kept off the badges, the shells not blending, the side stand folded; Paint condition and the
parts' wear then have nothing to show on; with them set `[Room] ParkFit=0`, 2026-11-21a's parking, so the bike doesn't
lean on a folded stand), `Data\Materials\CMB\Bike\` `static_wear.bgsm`, `static_wear_worn.bgsm`, `fork_wear.bgsm`,
`fork_wear_worn.bgsm` and the 28 `wear_<look>_static` and `_fork` materials (no depth, no alpha test),
`Data\Textures\CMB\Bike\` `badges_d.dds`, `badges_n.dds`, `badges_s.dds` (the cogs on grey, the old script), the Wear's
18 static maps that changed (`wear_<look>_static_d/_n/_s.dds`: the grime kept off the badges) and the six muddy tyre
diffuses (`wheelF_tyre_mud_d.dds`, `_ww_mud_d`, `_rl_mud_d` and the same `wheelR_`: the tread caked), in a small MO2 mod
of their own ticked below this one (README's table of this build's art switches). For the frame rate, the five nifs
alone say what the new shells cost.

### The field kit (2026-11-22a): steps 13-15

(test 58: "it zooms in on the bike, but doesn't zoom out, also scroll doesn't work on menu to look through items in
field kit; arrows scroll list"; "no, bike doesn't spin to position to show what is being changed": the views were set on
two bikes the menu wasn't showing, and the wheel's down notch was never counted)

13. **The views on screen**: Customise, the Motorbike. Move through the slots with the arrow keys and stop on each:
    Plate (the bike turns to its rear), Tank L (its left side), Tank R (its right side), Seat (from above), Fender (the
    rear fender), Rims and Tyres (the wheels), Paint and Mirrors (three-quarters), Wear and Paint condition
    (three-quarters from a little above), Headlamp (the front). The bike on screen should turn each time, gliding. Two
    screenshots.
    - At the first Customise of the session: `kit: drawn: Interface3D::Renderer::GetByName (Address Library 2222524) at
      +0x...: the menu's renderer asked for once a visit, by the 3D manager's own name` (or why not).
    - At each visit and each time the drawn bike changes: `kit: drawn (2026-11-22a): the renderer 'WorkbenchItem3D'
      (...): its ... 'Motorcycle' (...) is the bike drawn, held alone: ...`. Send it: it says which bike the menu draws
      (a loaded model, the slot objects' one or the menu's own item 3D), the question test 58 left. If instead `kit:
      drawn (2026-11-22a): <why>: 21a's models held (KitFollow's)`, the why says what failed, and the bike turns as in
      test 58.
    - A/B: `[Look] KitDrawn=0` (2026-11-21a's way: the views not on screen).
14. **In a slot's mods**: highlight Plate text (the bike turns to its rear) and press E: move up and down the mods (each
    one previews on the bike): every preview keeps the rear and your zoom; zoom and turn it there too. Tab back to the
    slots; the same on Paint and on Tank L.
15. **The wheel and the drag**: with the cursor above the bike or beside the lists, roll the wheel both ways: the bike
    zooms in and out. With the cursor over the list panel, roll the wheel: the list scrolls as the game's lists do and
    the bike doesn't zoom (your pick). Hold the left button beside or above the lists and move the mouse: the bike
    turns; on the lists the left button picks rows as before.
    - At each close, before 2026-11-21a's close lines: `kit: hold (2026-11-22a): the menu's bike (item ...): the menu
      closed; the drawn model ...; the wheel's events: up (0x800) a with a value over 0, b under, c at 0, held up to X
      ms; down (0x900) d over 0, e under, f at 0, held up to Y ms; L notch(es) passed to the lists (KitWheelLists), the
      zoom at the end Z`. Send it: the down row says how the game sends the wheel's down notch (test 58 suggests a value
      under 0), and L above 0 with the list scrolling is your wish working.
    - If the wheel zooms over the lists or scrolls them off them: `[Look] KitListBox` (0.22,0.46,0.78,0.97: the list
      panel's left, top, right and bottom as fractions of the screen, measured on a 16:9 screen). A/Bs: `KitWheelDown=0`
      (no zoom-out, test 58's), `KitWheelLists=0` (the wheel zooms anywhere, test 58's), `KitSlots22=0` (2026-11-21a's
      slots: no view of its own for Paint condition).

### The parked bike (2026-11-22a): steps 16-21

(test 58: "it looks like bike started to 'not align' with ground it stays on when character is off of it, having one
tire in the ground; I was thinking that it would be cool if bike was leaning a bit on sidestand/kickstand": the parks on
the track you rode had a tyre 1.5-2.5 units in the ground or the bike 4-5 over it; the bike had a side stand all along,
folded behind the left footpeg)

16. **On flat ground**: get off on a road. The bike should lean a little to its left on its side stand (about 9
    degrees), the stand's foot on the ground and both tyres on the ground. Walk round it: the stand is on the left,
    under the footpeg. If it leans to its right instead (the stand in the air), say so: one sign in the script to turn
    round.
    - `CMB_Slope.log`: `room: ask N at (...), heading H (the parked bike's fit: ParkFit): fitted: the front tyre's
      ground ..., the rear's ..., the middle's ...: its middle ... over/under it, pitch ..., the ground's roll ...,
      leaning ... on its stand: roll ...; the stand's foot's ground ... over/under the tyres' line there`.
    - `Papyrus.0.log`: `Parked bike set on the ground under its tyres (the plugin's [Room] ParkFit, after the settle N):
      moved ... up, pitch ..., roll ... (the ground's ..., leaning 8.6 on its side stand).`
17. **On slopes**: get off on a slope riding up it, then riding down it, then across it both ways (the stand uphill,
    then downhill): both tyres sit on the ground, neither sinking in nor floating, and the stand's foot touches the
    ground. With the stand downhill the bike leans the slope and up to 12 degrees more: does it look as if it would tip?
18. **Beside a car, a ledge, a crate**: get off right beside a parked car, once with the car on the bike's right and
    once on its left (the stand's side), beside a ledge or a step about a hand high, beside a crate or a barrel, and at
    the edge of a drop. The bike stays on its own ground, both tyres on the ground and leaning on its stand, never
    rolled onto the car's hood or the ledge (the review found the side rays reading those as the ground under it; they
    now start just above the bike's own ground).
    - `room: ask ... (the parked bike's fit: ParkFit): fitted: ...`, ending `; its sides' ground off one slope through
      the middle's (the right's ... over it, the left's ... over): the slope across by its left side, the right's set
      aside` (or the left's) when one side stood on something; with no ground on one side, that side set aside and the
      other's slope used.
19. **Rough ground, calls and a swim**: get off on rubble, at a kerb, with a bump between the wheels; call the bike
    (keys → Call) to a few places; let it roll up after a swim. Each time: the tyres on the ground, the bike leaning on
    its stand. Say if anything of it goes into the ground.
    - Where the plugin can't fit it: `room: ask ... (the parked bike's fit: ParkFit): not fitted, no ground under its
      <part> within 88: its side stand's lean alone, 8.6`, then `Parked bike leaning 8.6 on its side stand over the tilt
      its settle N gave it (not fitted by the plugin's [Room] ParkFit): ...`: it still leans on its stand, on the ground
      the game put it on.
20. **Getting on, a load, the kit**: get on next to the leaning bike: it stands up as you get on, the screen fades and
    you ride upright, no jump. Save next to the leaning bike and load: still leaning, on the ground; get on: it stands
    up as before. Use the field kit and close it: the bike still leans (the kit's preview shows it upright, its stand
    down).
    - `Getting on: the parked bike stood up off its side stand (roll ... -> ..., ParkStandUp).`
21. **The A/Bs**: `[Room] ParkStand=` (empty): the bike upright on its tyres' ground (its stand still down, the foot
    just off the ground); `[Room] ParkFit=0`: 2026-11-21a's parking (upright, the old height and tilt; the stand still
    down: 2026-11-21a's look is that with step 12's 2026-11-21a parked mesh). Back to the shipped values after. With the
    MCM's tilt at 0 (`set CMB_MaxTilt to 0`: no tilt with the ground) the parked bike stands level and still leans on
    its stand (`The parked bike's fit: not asked for (tilting turned off: level, as every park): its side stand's lean
    alone asked for.`); put your value back (45 by default).

### The look and the aim (2026-11-22a): steps 22-25

(test 58: "with right-click we are aiming a gun and it's slowing bike down - same with 3rd person (but Z doesn't work)"
and "can't open pipboy when swinging camera": 2026-11-21a's block never switched on, its handler's name not the game's;
and riding, the game keeps its third-person camera behind you, so the held look moved it only 10-22 degrees)

22. **No aim on the bike**: ride at full speed in first person with a pistol out and hold the right button a few
    seconds: no iron sights, no zoom, the dial doesn't drop; the left button still fires. Then the same in third person.
    - Once, at the first ride: `aim: AttackBlockHandler (PlayerControls+0x220, vtable +0x...): ShouldHandleEvent (slot
      1, +0x...) wrapped and OnButtonEvent (slot 8, +0x...) wrapped: while riding the game's aim (SecondaryAttack) is
      kept from it (AimBlock); ...` (test 58 had `aim: no AttackBlockHandler at PlayerControls+0x220
      (.?AUAttackBlockHandler@@ there) ...` every session: the game names the handler as a struct, `[Steer] AimStruct`).
    - Each press: `aim: the game's aim (SecondaryAttack, the mouse's button 2, the right) pressed at ... u/s ...: kept
      from the game while riding (AimBlock): ...`, and at its release `aim: the aim's button let go after N s: ... the
      game never aimed; the bike ... u/s at the press, ... at its least, ...`.
23. **The Pip-Boy while you look**: hold the right button (looking round) and press Tab: does the Pip-Boy open? And
    right after letting go? The same holding Z.
24. **The look in third person, with Z and with the right button**: ride in third person at speed, hold Z and move the
    mouse: the camera swings round you as far as you move it (to your side, in front of you, up to about 150 degrees),
    stays there while you hold the mouse still, and the bike keeps going straight (A and D still steer). Let go: the
    camera swings back behind you in half a second and the bike does not turn. Then the same with the right button. With
    a pistol out it stops at about 60 degrees. Is the swing too fast, too slow or the wrong way for your mouse?
    - Each hold: `view: the look key (Z) held in third person at 865 u/s: the plugin swings the camera round you by the
      mouse, the bike keeps its line (LookOrbit; the camera 0 deg off the bike now; ThirdPersonState +0xF0 targetYaw and
      +0xF4 currentYaw written, 0.0159 rad a unit of the look input, learned from N free frame(s))` (`(Mouse 2)` for the
      right button).
    - Each release: `view: the look let go in third person after 3.1 s (the orbit 120 deg off the bike at most, 118 now,
      the camera read): eased back behind over 0.5 s (LookOrbit)`, then `view: the third-person camera back behind you
      after 0.50 s (the camera 0.4 deg off the bike, the correction 2.1 deg) (LookOrbit)`. Send them all: "the
      correction" says how hard the game pulls its camera back, "learned from N free frame(s)" whether the plugin reads
      your mouse there (none in a session would say it doesn't).
    - If the camera doesn't follow: `view: the third-person orbit not used for this hold: ... (LookOrbit)`, or `view:
      the third-person orbit not followed: the camera N deg off the bike against the orbit's M (...): off this session,
      ...` (the look is then 2026-11-21a's for the rest of the session), or `... not back within 20 deg: the bike keeps
      its line till it is`.
25. **The A/Bs**: `[Steer] AimBlock=0`: ride at full speed with a pistol out and hold the right button 3 s: the game
    aims again (test 58's case); did the bike slow? `aim: the game aimed (the gun state 6, sighted) for N s while riding
    ...: the aim slowed the bike (AimWatch)`, or `... didn't slow the bike`. Can you open the Pip-Boy while it aims? Put
    `AimBlock=1` back. `[Steer] AimStruct=0`: the handler looked for by its class name alone, as in 2026-11-21a: the
    first ride's line is test 58's `aim: no AttackBlockHandler at PlayerControls+0x220 (.?AUAttackBlockHandler@@ there)
    ...` and the right button aims and slows the bike again; put it back to 1. `[View] LookOrbit=0` (2026-11-21a's
    third-person look: the camera stays behind). If the swing's speed is wrong, `[View] LookOrbitGain` (0 learns it
    while you ride; 0.0159 is test 58's; more swings faster, a minus sign the other way).

### The gears (2026-11-22a): steps 26-29

(test 58: "sound wise it's ok, but overall it feels more sluggish and slower than before": like for like the pulls were
as quick as test 57's, but most began rolling, and those changed up into 4th at about 32 and into 5th at about 43 on the
dial, the engine at 2300-2500 rpm from there; and after the Pip-Boy at speed the throttle was cut, 470 to 223 u/s)

26. **From a stop and from a middle speed**: on a long flat road, from a stop hold forward to the top: the gears change
    at about 12, 24, 36 and 46 on the dial (the first change a little under 12 when you have stood a while: the game's
    own first second). Then ride at about 20 on the dial, let go a moment, and hold forward to the top: the gears should
    still change at about 24, 36 and 46 (test 58: 32 and 43). Does the engine pull through each gear? Does the bike feel
    as lively as in test 57?
    - The gear lines: `sound: gear 4 at 644 u/s, ... rpm, heard ... u/s; the engine's speed ... (SpeedMap); at the band
      644 (UpBands, held 1.20 s)` (`gear 3 at ~429`, `gear 5 at ~823`); "(UpBands, held" says the gear waited for its
      band.
27. **Up a hill, and steady**: up a long hill at full throttle the gears change at the same dial readings as on the
    flat; if the bike can't reach 46 it stays in 4th until it stops gaining. At a steady 20 and 35 on the dial the gears
    as in test 58 (no change meant there).
28. **A menu at speed**: at full throttle at about 30 on the dial open the Pip-Boy (or the favourites) for a few seconds
    and close it: the bike carries on at the speed it had (test 58: it dropped to about half and pulled again). The same
    while coasting after letting go: the roll carries on.
    - `steer: a menu paused the game 2.4 s at 548 u/s: the speed measure held through it (MenuKeep)`; a coast with a
      menu in it: `steer: a coast from ...: stopped after 5.7 s at 5 u/s, 2280 u on; the game paused 2.4 s in it (a
      menu), not counted; each second ...` (each second's speed its own, not test 58's "181, 181, 181").
29. **The A/Bs**: `[Sound] UpBands=` (test 58's gears), `UpBands=215,429,620,800` (3rd and 4th a little shorter);
    `[Steer] MenuKeep=0` (test 58's drop after a menu).

### Other mods' attachments (2026-11-22a): steps 30-32

(test 58: "in 3rd person gun is being holstered to random places, often outside of the body of character": your holster
mod copies the pistol in your hand as you put it away, and the copy took over the place this plugin had given the hand's
pistol, so it hung in the air beside the bike; your rule: "Our mod will need to work regardless of other mods
installed", so whatever another mod hangs off your body now follows it)

30. **The holstered pistol on your thigh**: your holster mod on, as in test 58. Get on holstered, ride, draw the 10mm in
    third person and put it away while riding. Look at your right thigh in third person: the holstered pistol sits on it
    and stays on it as the bike leans in turns and over bumps; then look in first person. A short video.
    - At each put-away: `rider:   8 of them carried a local transform this plugin wrote on a held shape ('...' carried
      what this plugin wrote on the held '...' 0.03 s before: a copy another mod made of it): held from that shape's own
      and given it (AttachUnclone)`.
    - `rider: an attachment: 'WeaponPistolUp' < 'RLeg_Thigh', N held shape(s) (...), hangs off the body's bone
      'RLeg_Thigh'; the body's part there none (AttachWhere)`, then at 0.5 s and 2 s `rider: the attachment
      'WeaponPistolUp' at 0.5 s (tilted): its root (x, y, z) from the bone 'RLeg_Thigh' in the bone's frame (d away);
      its shapes' written transforms put it a to b off that place from the drawn bone; its N shape(s) drawn c to d from
      the root, e to f from the drawn bone (AttachWhere)`. "Off that place" 0.000 says it follows your thigh exactly;
      "from the root" reads a few units for a pistol (test 58's copies would read tens).
31. **Again, a rifle, a backpack**: draw and holster three times, with the bike leaning and straight; then the hunting
    rifle (its number key: it stays holstered while riding) on your back the same way. If you have a backpack mod, wear
    one: it stays on your back through leans and bumps.
32. **The A/Bs**: `[Tilt] AttachUnclone=0`: the holstered pistol back in the air beside the bike (test 58's);
    `AttachBoneRole=0`: should look as with 1 for these two mods. The fallback: `AttachHide=1` hides the holstered
    weapons (anything another mod hangs off you outside an equipped item) while riding, `AttachHide=2` the backpack too;
    0 again after.

### The frame rate (step 33)

33. **Beside the parked bike**: stand 3-4 m from the parked bike at a fixed spot you can find again (by its side in
    Sanctuary, facing it, for example), still for 20 s, and note your frame rate with your usual frame counter: with
    every slot as it came; then with Wear "Wasteland" and Paint condition "Worn" at the same spot; and on 2026-11-21a
    too if you noted it before installing (test 58 gave no figures). Every bike carries five more shells, invisible
    until chosen: about 20,700 triangles and five draw calls more than 2026-11-21a. Then sit on the bike at that spot,
    stopped, 20 s each way: `CMB_Slope.log`'s `time: the last 10 s: N frames a second (...), stopped` lines say it too.

### The A/Bs (step 34)

34. Any of this build's A/Bs you haven't tried yet, one at a time, a ride or two each (README's table of this build's
    keys): `[Look] OverlayParked=1`, `OverlayRuntime=0`, `KitDrawn=0`, `KitWheelDown=0`, `KitWheelLists=0`,
    `KitSlots22=0`; `[View] LookOrbit=0`; `[Steer] AimBlock=0`, `AimStruct=0`, `MenuKeep=0`; `[Sound] UpBands=` (and
    `215,429,620,800`); `[Room] ParkStand=`, `ParkFit=0`; `[Tilt] AttachUnclone=0`, `AttachBoneRole=0`, `AttachHide=1`
    and `2`. `[Diag] LensLine=0` and `AttachWhere=0` change only log lines; `[Look] ParkedSwapHold=0` only if asked
    (test 58's crash). Anything better or worse?

Send `CMB_Slope.log` and its `_prev` logs and `Papyrus.0.log` of each session, any crash log, the screenshots of steps
2-13 (each paint condition and the combinations, the wear on the four bikes, the parts and the badges, the tread, the
gears, the script, the headlamp's colours, close and riding; two of the kit's views) and of steps 16-19 (the parked bike
on flat ground, on a slope both ways, beside a car or a ledge, on rough ground), and a short video of steps 15, 20, 24
and 30 if you can.

### Questions for you (test 59)

- **T59-1 (step 1).** No crash in five or more tries of a change at the kit and Ride at once? Which "Getting on: the
  parked bike's look at the mount" lines came?
- **T59-2 (step 2).** Each paint condition: does it read as its name? Which would you change, and how?
- **T59-3 (step 3).** Paint condition under the Wear: the grime always on top? Any flicker between the two?
- **T59-4 (step 4).** The Wear on the kit's preview, the parked bike, third person and first person?
- **T59-5 (step 5).** With `OverlayParked=1`: the wear on the parked bike when it had none? With `OverlayRuntime=0`:
  still on the bike under you?
- **T59-6 (step 6).** The Wear on the exhaust, the engine's covers and the fork's lowers: noticeable but not too much?
  The heat colours, the rust on the mufflers?
- **T59-7 (step 7).** The grime over the tank and rear badges: right? A flicker, a frame round a plate?
- **T59-8 (step 8).** The muddy tread: clean where it meets the road, the mud between the blocks?
- **T59-9 (step 9).** The Brotherhood helmet's three gears on metallic blue: the big gear enough? The blue right?
- **T59-10 (step 10).** Nuka-Cola's script even now?
- **T59-11 (step 11).** The six new colours on the road and in the lens? Red and Purple too dim?
- **T59-12 (step 12).** As it came exactly as 2026-11-21a? The front fender badge gone, an old save's too?
- **T59-13 (step 13).** The bike on screen turning to each slot? What did the "kit: drawn (2026-11-22a)" line say?
- **T59-14 (step 14).** In a slot's mods every preview keeping the view and the zoom?
- **T59-15 (step 15).** The wheel zooming in and out off the lists, scrolling them over the panel? The close line's
  wheel counts?
- **T59-16 (step 16).** On flat ground: leaning to its left on the stand, both tyres and the foot on the ground?
- **T59-17 (step 17).** On slopes, up, down and across both ways: the tyres on the ground? Downhill, does it look about
  to tip?
- **T59-18 (step 18).** Beside a car, a ledge, a crate or a drop: the bike on its own ground, never rolled onto them?
- **T59-19 (step 19).** Rough ground, calls and a swim: anything into the ground? Leaning on the stand where a "not
  fitted" line came too?
- **T59-20 (step 20).** Standing up as you get on, no jump? After a load and the kit still leaning?
- **T59-21 (step 21).** `ParkStand=` and `ParkFit=0`: which do you like better than the default, if any?
- **T59-22 (step 22).** No aim and no slowing with the right button, in first and third person? The "aim:
  AttackBlockHandler ... wrapped" line?
- **T59-23 (step 23).** The Pip-Boy while looking: does it open?
- **T59-24 (step 24).** The third-person orbit with Z and with the right button: round you, held, back behind with no
  turn? The speed right? The release lines' "the correction"?
- **T59-25 (step 25).** With `AimBlock=0`: did the aim slow the bike? With `AimStruct=0` test 58's aim back?
  `LookOrbit=0` against the orbit?
- **T59-26 (step 26).** The gears at about 12, 24, 36 and 46 from a stop and from a middle speed? Lively again?
- **T59-27 (step 27).** Up a hill and at a steady speed: right?
- **T59-28 (step 28).** After the Pip-Boy at speed and in a coast: the speed kept?
- **T59-29 (step 29).** Which `UpBands` felt best?
- **T59-30 (step 30).** The holstered pistol on your thigh, through leans and bumps, in first person too? The "at 0.5 s"
  line's "off that place"?
- **T59-31 (step 31).** Three holsters, the rifle, a backpack: all on your body?
- **T59-32 (step 32).** `AttachUnclone=0` back in the air? `AttachHide` needed at all?
- **T59-33 (step 33).** The frame rate beside the parked bike, stock against Wasteland with Worn (and 2026-11-21a)?
- **T59-34 (step 34).** Anything a 2026-11-22a A/B made better or worse?

### The open questions and the lines that settle them (test 59)

For your checker: what each part of this build couldn't settle offline, the log line that settles it and the A/B it
suggests.

- **The crash** (step 1): its engine reason is inferred from the logs, not read from the game: every crash of tests 54
  and 58 came a moment after F4SE's swap had put a look on a parked bike's 3D that then stayed drawn (into a getting on,
  under the kit's menu). If one comes again, the Papyrus mount line (`Getting on: the parked bike's look at the mount
  (ParkedSwapHold): ...`) and the plugin's `lens (2026-11-22a, [Diag] LensLine): ...` lines of that second say what both
  bikes carried. By default the parked bike carries no runtime swap at all now (`OverlayParked=0`), so the mount's
  reload before the fade almost never runs; with `OverlayParked=1` (step 5) every runtime swap on it is re-asked right
  before it goes on (none while getting on, riding or in a kit session), but a swapped bike still stands between rides
  and is drawn under the bench's menu when the kit opens beside it: a crash there would make `OverlayParked=0` the
  answer. With `[Look] MountGuard=0` (2026-11-09a's A/B) nothing is thrown away at the mount.
- **The Wear at a 3D's load** (steps 4-5): that the game's own swap at a load turns blending on only where the shape's
  own mesh and file already blend is a reading of test 58's video and logs; the shells blend now, and the parked bike's
  Wear rests on that alone by default. Wear on the parked bike with `OverlayParked=0` says the meshes fixed it; none
  until `OverlayParked=1` says they don't (then the next build turns it on). `OverlayRuntime=0` with the wear still on
  the bike under you says the same for the worn bike.
- **Two see-through layers** (step 3): both shells share their paint's bounds, so the game's sort can't order them; the
  overlays write depth and test their alpha at 8 so the grime hides the paint's damage whichever is drawn first. If the
  damage shows over the mud, the fallback is an alpha test alone for Paint condition (a material change).
- **The grime over a badge** (step 7) doesn't know the badge's art (the plate is a clear rectangle round it), so the
  dust keeps to the plate's top edge and the rust to its bottom edge; rust on the tank's sides keeps 2026-11-21a's band
  round each plate, faintly rectangular close up.
- **The art's taste** (steps 9 and 11): the big gear shows about 12 % round the helmet (a layout change in `bike_art.py`
  if it should show more); Red and Purple light the road at 0.24 and 0.20 of Warm's brightness (FadeValue 6.0 and 7.2
  would bring them to 0.6: a table change); Daylight (5000 K) is a little warmer than Warm (about 5500 K).
- **The kit's drawn bike** (step 13): which bike the armour menu draws is asked of the game's own renderer through a
  function the plugin hasn't called before (`kit: drawn: Interface3D::Renderer::GetByName ...`), its answer taken only
  when its name field is the 3D manager's; a bike under a placed parent can't be held (21a's way then, the line says
  so). A/B `[Look] KitDrawn=0`. The kit's preview shows the parked bike upright with its stand down (its look in the
  menu is still open).
- **The wheel** (step 15): the down notch's sign is inferred (test 58: never counted); the close line's down row counts
  each code's events by sign. The cursor over the panel is read in the input hook from the last checked cursor: one
  unknown counts as off the lists (the wheel zooms). A/Bs `KitWheelDown=0`, `KitWheelLists=0`, the box `KitListBox`.
- **The parked bike's lean** (steps 16-21) uses the angle convention the script's tilt uses (test 7): leaning right with
  the stand in the air would say the sign is wrong (one line in the script). With the stand downhill on a side slope the
  total roll reaches about 21 degrees on a 12-degree slope; on a crest under the stand the foot can sit a few units in
  the ground (the lean held at 3); the stand-up is five steps over 0.2 s (after the parked bike's reload, if a getting
  on has one) and may look stepped on a slow frame. Beside things (step 18): the sides' and the foot's rays start 25
  over the middle's ground and the middle's 40 over the tyres' line, so a car's hood, a ledge or a barrel is passed
  under; two sides off one slope give the middle one of the two sides' slopes and level, so when something stands on a
  true slope's low side the bike lies level across there (never past either side's slope); the tyres' rays still start
  88 up, so something overhanging a tyre's contact lower than that would still read as its ground. A park the plugin
  can't fit leans on its stand over the game's own tilt. Lines: `room: ask ... (the parked bike's fit: ParkFit): ...`
  (with `its sides' ground off one slope ...` where one side was set aside), `Parked bike set on the ground under its
  tyres ...`, `Parked bike leaning 8.6 on its side stand over ...`, `Getting on: the parked bike stood up ...`. A/Bs
  `[Room] ParkStand=`, `ParkFit=0` (2026-11-21a's look needs `build_bike.sh`'s `STAND=0` mesh too).
- **The aim's struct name** (step 22): `[Steer] AimStruct=1` takes the handler by the struct's name the game uses (test
  58's line every session); the first ride's `aim: AttackBlockHandler ... wrapped ...` line settles it. A/B
  `AimStruct=0` (2026-11-21a's, no block).
- **The third-person orbit** (step 24): that the game keeps its camera where the plugin writes it while riding is read
  from test 58's eases, not seen; "the correction" in the back line says how hard it pulls back (well over 20 degrees:
  hard), "learned from N free frame(s)" whether the mouse reaches the game's look input in third person; "not followed"
  switches the orbit off for the session. A pad's right stick is untried. A/Bs `[View] LookOrbit=0`, `LookOrbitGain`.
- **The Pip-Boy** (step 23): the plugin keeps only the aim's event from the game, never the Pip-Boy's; test 58's shut
  Pip-Boy looks like the game's own while it aimed. The Pip-Boy's own lines with the aim's press line say it.
- **The gears** (steps 26-27): a pull from a long stand starts with the game's own first second (about 1.1 s to 100 u/s
  against 0.5 rolling), so its first change comes at about 10.7 on the dial; up a long climb 2nd may reach its rev
  ceiling before 24 on the dial (405 u/s in the harness's climb) and 4th is held while the bike still gains. The gear
  lines' "(UpBands, held" say where each waited. A/Bs `[Sound] UpBands=`, `UpBands=215,429,620,800`.
- **A menu at speed** (step 28): `MenuKeep` holds the speed measure for any pause the game's menu mode reports; a hitch
  is not a menu. A/B `[Steer] MenuKeep=0`.
- **Attachments** (steps 30-32): a copy made more than 0.5 s after the plugin last wrote its source (or past 64 writes)
  is held from what it carries; a mod that sets its shapes' own places every frame would fight the plugin's writes (not
  seen in test 58); between the copy and its hold (one update, 0.03 s in test 58) the copy shows where the other mod put
  it; `AttachHide=2` would hide a hat's loose parts too. The `at 0.5 s` and `at 2.0 s` lines say where each attachment
  is drawn. A/Bs `[Tilt] AttachUnclone=0`, `AttachBoneRole=0`, `AttachHide=1`, `2`.
- **The cost** (step 33): every bike draws five more invisible shells (about 20,700 triangles, +6.5 %); the worn bike
  holds 63 shapes of the plugin's 64.
- **The MCM's dropdowns** through the controller's properties (open since test 56): "Paint condition" and the
  eleven-colour "Headlamp" are read and set that way too; one always showing its first choice would say they don't.

## Test 58: the 2026-11-21a build (test 57's fixes, your wishes and art build B)

The 2026-11-21a build answers test 57 (run on 2026-11-17a): its fixes, your wishes and the rest of build B, the second
art build, in one build (your pick). Steps 1-12 are the art, steps 13-16 the field kit, steps 17-32 the fixes and the
wishes, with the questions T58-1 to T58-32 at the end. What test 57 liked is as it was.

- **The art (build B):** a Wear slot with seven looks over any paint (Weathered, Dusty, Muddy, Rusty, Bloody, and two
  together: Wasteland and Raider); three muddy tyres; a badge on top of the front mudguard (any badge of the rear
  fender's list); the headlamp in five colours, the lens and the beam (Warm as it came, Cool white, Amber, Selective
  yellow, Blue-white); two new badges for the tanks and both fenders, Nuka-Cola and Red Rocket; the 3D Enclave helmet on
  the Enclave's flag and the 3D Brotherhood helmet between two cogs (your wishes); the Brotherhood of Steel plate's top
  line centred (and the Minutemen, Nuka-Cola and Red Rocket plates', which had the same layout).
- **The field kit:** the wheel zooms wherever the cursor is, the lists too, and holding the left button anywhere off
  the lists turns the bike (your pick); the wheel no longer scrolls the lists (the arrow keys do); in a slot's mods
  (after E) and their previews the bike keeps your view; it turns only to a slot the highlight rests on; views for the
  three new slots.
- **The fixes and the wishes:** the gears in even steps (up-shifts at about 12, 24, 36 and 46 on the dial, your pick)
  and the coast about twice as long, slowing gradually ("rolling distance should be twice as much"); the free look on
  the right mouse button (Z still works) and in third person ("Z in 3rd person doesn't work"), the game's aim blocked
  while riding (your decision: aiming slows you on foot, and would the bike); in third person no pistol or rifle in the
  hand or along the arm while holstered, no running legs or hanging arms after a put-away, seated at once with a pistol
  drawn in first person, the "Only a handgun" message only for a rifle; and the bike (and you) drawn in third person
  after your body showed in first person ("bike and even character model were disappearing, mostly in 3rd person").

One thing test 57 didn't know: with "Weapons while riding" on "Handguns only" a rifle can't be drawn while riding at
all, by design since 2026-11-17a (your pick after test 56): its number key equips it holstered, "Only a handgun can be
used on the motorbike." shows, and R draws nothing until you get off. That is what you saw with the hunting rifle; it
isn't a fault.

Do this section's steps in one game session if you can, in this order (the art and the kit by the parked bike in one of
your settlements, the headlamp at night, then the rides), and say which session each step was in. Every new behaviour
of the plugin has a key whose off value gives the 2026-11-17a build back (README's table of this build's keys), so each
A/B is one key away; every new look choice is opt-in, and the changed art's A/B is files (after step 12). Things only
the game can settle: how a blended wear layer looks in the game's light (steps 1-4) and what the shells cost beside the
parked bike (step 12), which of the menu's bikes the armour menu shows after E and whether its lists get the wheel
through the menu's input (steps 13-14), whether the plugin's key reading sees the right mouse button while the game
reads the mouse (step 20), where the game keeps its third-person camera's turn (step 23), whether the game had hidden
the holstered weapon in your hand (step 25), and whether the game redoes what it draws of you when the plugin asks
(steps 29-31).

Before you start:
- install as a Replace over 2026-11-17a. If you edited `CMB_Slope.ini`, put your values into the new one: `[View]`,
  `[Steer]`, `[Tilt]`, `[Look]` and `[Diag]` have new keys, and `[Sound] HeardRiseGears`, `ShiftGapGears` and
  `DownBands` new defaults (README's table). Otherwise use the shipped file as it is;
- load your usual save. The ESP and the MCM change: the MCM's Look section should have 25 controls, with "Front fender
  badge" after "Rear fender badge", "Wear" after "Paint shade" and "Headlamp" after "Mirrors", and "Tyres" stepping
  through six. If it has 22, an older ESP or MCM folder is loaded: stop and say so. Riding's "Weapons while riding" on
  "Handguns only";
- the first time you get on after the update the look's mods go on afresh once (the look has three more slots):
  `Papyrus.0.log` says `Look: N of N mods on the worn bike`; a second getting on is as quick as before. A 2026-11-17a
  save starts with Wear "As it came", no front fender badge and the warm headlamp;
- note your frame rate beside the parked bike on 2026-11-17a before you install, if you can (step 12);
- have a pistol (the 10mm), a second handgun and the hunting rifle on the favourites' number keys, and your
  visible-holster mod on, as in test 57;
- the headlamp's step wants night: wait for it, or in the console `set gamehour to 22`;
- each A/B below: change one key in `CMB_Slope.ini`, save the file, get off and on (no restart), and put it back after.

The log's first lines: `CMB_Slope.log` has five settings lines more: `  view (2026-11-21a, test 57): BodyRedraw=1 (...)
BodyRedrawHide=1 (...); [Diag] ThirdWhere=1 (...)`, `  look (2026-11-21a, test 57): [View] LookButton=257: Mouse 2 (VK
0x02): ...; LookThird=1 (...) LookThirdBack=0.5; [Steer] AimBlock=1 (...); [Diag] AimWatch=1 (...)`, `  kit
(2026-11-21a): [Look] KitFollow=1 (...) KitSlotSettle=0.25 (...) KitMouse=1 (...) KitListBox=0.22,0.46,0.78,0.97
KitWheelOwn=1 (...) KitNewSlots=1 (...); views (heading, elevation): wear -45,15, front fender 0,25, headlamp 0,5`,
`  weapons (2026-11-21a, test 57): GunHandHide=1 GunAwayKeep=1 GunSeatKeep=1 GunNoteSure=1 (...)` and `  steer
(2026-11-21a, test 57): CoastDrag=270,90: let go, the throttle rolls off by the speed, ...`; the older lines now say
`HeardRiseGears=2,0.86,0.8,1,1 ShiftGapGears=0,1.8,2,1.7` and `DownBands=170,380,600,780`. No 2026-11-21a lines, or
`CoastDrag=: let go, the throttle rolls off evenly over Coast (... the 2026-11-17a build)` and `BodyRedraw=0 (nothing
asked, as 2026-11-17a)` with an INI you didn't change, mean an older `CMB_Slope.dll` or `CMB_Slope.ini` is loaded: stop
and say so.

### The art, build B (2026-11-21a): steps 1-12

At the field kit choose each in turn and look at it in the kit's preview, then leave the kit and look at the parked bike
close up, then ride away and look at it from the riding camera, in third person from the side and from behind, and in
first person where a step says. A screenshot of each, close and riding, please. Every new choice is opt-in (each new
slot starts as it came), and every other plate, badge and seat is as in test 57.

**The wear** (steps 1-4; build B's wear and weathered paint: drawn by our own code on two new thin shells that lie 0.3
units over the paint of the tank and rear fender and of the front mudguard, invisible until you choose a wear)

1. **Seven looks**: on the stock paint (Factory) set "Wear" to each in turn: Weathered, Dusty, Muddy, Rusty, Bloody,
   Wasteland, Raider. Look at the parked bike from both sides and from behind, then ride a little and look from the
   riding camera. Does each read as its name?
   - Weathered: the paint sun-faded on top (paler, a little chalky), chipped to grey primer and bare steel at the knee
     grips (the tank's rear sides) and along the edges, stone chips at the tank's front and the front mudguard's, fine
     scratches.
   - Dusty: a pale khaki film on what faces up, thick in the creases, washed off in streaks down the sides, wiped at the
     knees.
   - Muddy: both fenders caked low down and behind the wheels (their insides too), the tank's lower front muddy, the
     tank top clean.
   - Rusty: rust blooming from the edges, a ring round the tank badges, the rear badge and the plate, rust under the
     tank, streaks running down.
   - Bloody: spatter and drops with tails, three hand smears (the tank's left side, the rear fender's right top, the
     front mudguard's left side), drips.
   - Wasteland: weathered, dusty and muddy together; Raider: rusty and bloody together.
   - `Papyrus.0.log`: `Customise: wear = Wear:weathered (1)` to `Customise: wear = Wear:raider (7)`; at the kit the
     mods read "Wear: Weathered" and so on (Oil 1, Cloth 1).
2. **Over other paints**: with Muddy, then Bloody, change the paint to Gloss black and to Free colour (the MCM's hue):
   the wear stays and shows over every paint. Blood on the dark paints (the Factory oxblood, Gloss black) shows more by
   its sheen than its colour: still readable? Say which wear looks wrong on which paint.
3. **Close up, with the badges**: Wear "Wasteland" with a rear fender badge and a front fender badge (step 6) on: the
   badges sit cleanly over the mud, with no flicker between them at any distance. Look closely at the tank's badge
   plates from the side and at the rear badge: no wear drawn across them and no hard line where the wear stops over a
   badge (the wear is kept off them). Ride and turn the bars both ways: the front mudguard's wear moves with it. In
   first person look down at the tank: the wear is there too.
4. **By day and at night**: with a wear on, by day and at night with the headlamp lit: does the wear look lit like the
   paint under it (no glowing or too-dark patches)? Any flicker, or a halo round the bike from a distance? Do the lamps'
   lenses, the mirrors' glass or the chrome look wrong next to the wear? A/B: Wear "As it came".

**The tyres** (step 5)

5. **Muddy tyres**: set "Tyres" to "Black, muddy", "Whitewall, muddy" and "Red line, muddy" in turn: mud caked on the
   tread and splashed up the sidewalls, the white or red band partly showing through (more of it at the rear). Parked
   close up and riding. `Customise: tyres = Tyres:blackmud (3)`, `Tyres:whitewallmud (4)`, `Tyres:redlinemud (5)`
   (Adhesive 1, Oil 1).

**The badges and the plates** (steps 6-10; your wishes after test 57: the Enclave's flag behind the 3D Enclave helmet,
"for BoS 3d helmet - cogs from logo on both sides"; and "only brotherhood of steel plate top text needs to be
centered")

6. **The front fender badge**: set "Front fender badge" to Vault-Tec, then to Gunners skull. Stand in front of the
   bike: the badge sits on top of the front mudguard, just ahead of its highest point, the right way round as you read
   it from in front. Its list is the rear fender's badges in their order, then Nuka-Cola and Red Rocket. Ride, turn the
   bars both ways, ride over bumps: the badge stays on the mudguard, turning and moving with the wheel. `Customise:
   front fender = FrontFender:vaulttec (9)`, `FrontFender:gunskull (18)`; at the kit "Front fender: Vault-Tec"
   (Adhesive 1, Cloth 1).
7. **Two new badges**: set Tank L to "Nuka-Cola" with Tank R on "Same as the left", the rear fender and the front
   fender badge to "Nuka-Cola"; then all of them to "Red Rocket". Nuka-Cola: a red bottle cap with crimped edges,
   "Nuka" and "Cola" in white script with the swoosh between. Red Rocket: a round sign, a black rim, a red ring with RED
   ROCKET in white along its top, a yellow centre with two black R's back to back and a red rocket between them. Both
   tanks the same, nothing cut off at a plate's edge, on the fenders squashed a little as every badge. From riding
   distance a small red-and-white and a red-and-yellow roundel? `Customise: tank left = TankL:nukacola (20)`,
   `Customise: fender = Fender:redrocket (20)`, `Customise: front fender = FrontFender:nukacola (19)`.
8. **The Enclave helmet on the flag**: Tank L and Tank R "Enclave helmet (3D)": behind the helmet the plate is now the
   Enclave's flag, red and white stripes across the whole plate inside its chrome edge, a blue corner (upper left as you
   look at it, on each side) with a ring of 13 small white stars, the dark helmet standing over the stripes. Parked and
   riding, by day and at night. Are the stars too small, or the flag too busy behind the helmet? On the right tank the
   blue corner is toward the rear (each side reads as the flag seen from outside): does that bother you? `Customise:
   tank left = TankL:enclavehelm3d (17)`.
9. **The Brotherhood helmet between two cogs**: Tank L and Tank R "Brotherhood helmet (3D)": the steel grey plate with a
   black cog left and right of the helmet (nine teeth and a round hole: the big cog of the Brotherhood's emblem), clear
   of the helmet and of the chrome edge. By day and at night. `Customise: tank left = TankL:boshelm3d (18)`.
10. **The plates' top lines**: "Plate: Brotherhood of Steel" with any text (SYNTH? on black, as in test 57):
    "BROTHERHOOD OF STEEL" now sits centred over the big letters, as AD VICTORIAM under them, and ends well inside the
    plate. Look from low behind on the left as in test 57: it shouldn't run under the tail lamp. Then the Minutemen,
    Nuka-Cola and Red Rocket plates: their top lines centred the same way. `Customise: plate = Plate:bos (8)`.

**The headlamp** (step 11; at night)

11. **Five colours, the lens and the beam**: at night, parked and riding, set "Headlamp" to each in turn: Cool white (a
    whiter, cooler light than Warm), Amber (orange), Selective yellow (a deep yellow), Blue-white (a little blue), then
    "Warm (as it came)" again. The light on the road takes the colour; the lens's bright centre may look near white or
    yellow (as a bright lamp does), its glow and the road coloured. Parked and unlit, Amber, Selective yellow and
    Blue-white show a tinted bulb behind the glass (Cool white looks as Warm). Is Amber's beam too dim? Then while riding
    at night: MCM Look "Headlamp" to Amber and "Apply the look": the beam turns amber at once (the ridden bike's lens at
    the next getting on); ride across a few cells: still amber; get off and on: amber. The same once with MCM
    "Headlamp casts shadows" on.
    - `Papyrus.0.log`: at the kit `Customise: headlamp = Headlamp:amber (2)` ("Headlamp: Amber", Glass 1, Screws 1);
      riding, after Apply, `Look: the headlamp's beam (the MCM): Headlamp:amber, a fresh light (...) handed over`.

**As it came, and the cost** (step 12; the two shells and the front patch are on every bike, invisible until chosen:
about 13,500 triangles a bike more, and with a wear two blended layers over the paint)

12. **As it came, and the frame rate**: set Wear to "As it came", Tyres to "Black (as it came)", the front fender badge
    to "None" and the Headlamp to "Warm (as it came)": the bike should look exactly as in 2026-11-17a, parked, ridden, in
    first person and in the kit, with no new flicker on the tank, the fenders or the front mudguard. Then the frame
    rate: stand 3-4 m from the parked bike at a fixed spot you can find again (by its side in Sanctuary, facing it, for
    example), still for 20 s, and note your frame rate with your usual frame counter: with every slot as it came, then
    with Wear "Wasteland" at the same spot; on 2026-11-17a too if you noted it before installing (test 56's step 14 did
    the same for the helmets). Any drop? Then sit on the bike at that spot, stopped, 20 s each way: `CMB_Slope.log`'s
    `time: the last 10 s: N frames a second (...), stopped` lines say it too.

The changed art's A/B is files: the 2026-11-17a package's `Data\Meshes\CMB\` nifs (`CMB_BikeParked.nif`,
`CMB_BikeWorn.nif`, `CMB_BikeWornRider.nif`, `CMB_BikeWornRiderF.nif`, `CMB_BikeView.nif`: no shells, no front patch, the
rear patch where it was; a Wear or a front fender badge then has nothing to show on), `Data\Textures\CMB\Bike\`
`badges_d.dds`, `badges_n.dds`, `badges_s.dds` (17a's helmet grounds; Nuka-Cola and Red Rocket then show nothing) and
`plates_d.dds`, `plates_s.dds` (17a's top lines), in a small MO2 mod of their own ticked below this one (README's table
of this build's art switches). For the frame rate, the five nifs alone say what the shells cost.

### The field kit (2026-11-21a): steps 13-16

(test 57: "when selecting menu for e.g. plates bike goes into default position": after E the bike stayed side-on for
the rest of the visit; the slot read walked the list; and the wheel and the drag "only first time after opening field
kit, and not always": the cursor sat on the lists, where 2026-11-17a left the wheel and the clicks to the menu)

13. **The wheel and the drag anywhere**: Customise, the Motorbike. Put the cursor anywhere, on the slot list too, and
    roll the mouse wheel: the bike zooms in and out, and the list's highlight doesn't move. Hold the left button with
    the cursor beside the list (left or right of it) or above it and move the mouse: the bike turns. With the cursor on
    the list the left button picks rows as before. The wheel no longer scrolls the lists: in a long list (Paint, Rims,
    Plate text) move with the arrow keys (or W and S), and the list follows the highlight. Is that fine, or do you miss
    the wheel there?
    - At each close, before 2026-11-17a's close line: `kit: hold (2026-11-21a): the menu's bike (item ...): the menu
      closed; the models: ...; the slot read changed C time(s): ...; the wheel: E event(s) kept from the menu
      (KitWheelOwn), Z notch(es) zoomed with the cursor on the lists; drags begun: O outside the lists' box, I in it`.
      E above 0 with the lists not scrolling says the wheel reached them through the menu's input, as the plugin takes
      it.
    - 30 frames into each visit, after 2026-11-17a's `kit: slot: ...`: `kit: slot (2026-11-21a): the 3D manager's
      highlighted part N; the menu's zoom distance Z, frame time F s, cursor box ...; its +0x590 ...; models held n of
      m loaded`. Send it: a "frame time" near your real frame time says the menu's later fields are where the plugin
      reads them.
    - If the drag turns the bike on the lists, or not beside them: `[Look] KitListBox` (0.22,0.46,0.78,0.97: the lists'
      left, top, right and bottom as fractions of the screen, measured on test 57's 1920 x 1080 video). A/Bs:
      `KitWheelOwn=0` (the lists scroll with the wheel too), `KitMouse=0` (2026-11-17a's: the wheel and the drag only
      above the lists).
14. **In a slot's mods**: highlight Plate text (the bike turns to its rear) and press E: the mods list opens. The bike
    should stay at the rear (in test 57 it turned side-on). Move up and down the mods (each one previews on the bike):
    every preview shows the rear at the same zoom; zoom and turn it there too. Tab back to the slots. The same on Paint
    and on Tank L.
    - After E: `kit: hold: the menu's models (2026-11-21a): 6 loaded (0x40 apart), 6 of them our bike (loaded 0, 1, 2,
      3, 4, 5); the slot objects hang under loaded model K; 6 held; the menu's state 1` (the numbers yours). Send it: it
      says how many bikes the menu loads in a mods list and, by "hang under", which one it shows. `their stride not
      found: the first only` would mean only the first is held (test 57's case).
    - A/B: `[Look] KitFollow=0` (2026-11-17a's: the first model only; test 57's side view after E should come back).
15. **The highlight walking**: move the highlight quickly up and down the slot list with the arrow keys: the bike
    shouldn't swing about while it moves; stop on a slot for a quarter of a second and it turns to that slot's part.
    - 2026-11-17a's `kit: hold: the slot '...' (from ...): ...` only for the slots the highlight rested on (test 57's
      14:05 visit had 50 of them in 8 s). The close line's `the slot read changed C time(s): A taken (held 0.25 s), N
      not (read for less), W within 0.15 s of a wheel notch, B with the left button down` says what walked the list.
    - A/B: `[Look] KitSlotSettle=0` (each read turns the bike at once).
16. **The new slots' views**: highlight Wear (the bike three-quarters, from a little above), Front fender badge (the
    front mudguard from the front, a little above) and Headlamp (the bike from the front). A screenshot of each. Would
    you like another view for any (`[Look] KitViewWear`, `KitViewFrontFender`, `KitViewHeadlamp`: heading, elevation in
    degrees, as the other views)?
    - `kit: hold: the slot 'Wear' (from the highlighted slot object): three-quarter (the wear), heading -45.0, elevation
      15.0 (eased over 0.35 s)`, `... 'Front fender' ...: the front fender from the front, heading 0.0, elevation 25.0
      ...`, `... 'Headlamp' ...: the front, heading 0.0, elevation 5.0 ...`.
    - A/B: `[Look] KitNewSlots=0` (the three-quarter view for the three).

### Test 57's fixes and your wishes (2026-11-21a): steps 17-32

**The gears and the coast** (steps 17-19; test 57: the up-shifts at 12, 26, 43 and 49 on the dial, "4th gear - 50-50?
shortest currently", your pick even steps at about 12, 24, 36 and 46; "when letting go at top speed rolling distance
should be twice as much as is now, with gradual slow down")

17. **Even steps**: from a stop on a long flat road hold forward to the top speed, watching the dial at each gear
    change. They should come in even steps, at about 12, 24, 36 and 46 on the dial, 4th lasting about as long as 2nd and
    3rd (about 2 s each) instead of a moment. Does each gear still sound like a gear climbing? Is the spacing right?
    - `sound: gear 2 at ~210 u/s ...`, `gear 3 at ~430`, `gear 4 at ~640`, `gear 5 at ~820` (test 57: 218, 464, 778,
      880). Each pull shifts a little differently: 2nd can run long enough to put the 2-3 at 24-27 on the dial.
    - A/B: `[Sound] HeardRiseGears=2,0.79,0.65,1,1`, `ShiftGapGears=0,2,3,1.5` and `DownBands=170,400,700,860` together
      (test 57's gears).
18. **The coast from the top**: at the top speed let go of forward and roll to a stop without braking. The bike should
    roll about twice as far as in test 57 (some 33 m instead of 16), slowing hardest at first and more and more gently:
    about 42 on the dial after a second, 30 after two, 20 after three, 11 after four, stopped after about 6 s. The
    engine shifts down one gear at a time over the roll (5-4 at about 44 on the dial, 4-3 at about 34, 3-2 at about 21,
    2-1 at about 10), then idles for the last bit. Natural? Too long, too short?
    - `CMB_Slope.log`: the throttle trace's `..., rolling off by CoastDrag)`, then `steer: a coast from 929 u/s (the
      throttle 1.00; CoastDrag 270,90): stopped after 5.76 s at 5 u/s, 2287 u on; each second 727, 510, 333, 188, 69
      u/s` and the stop line `sound: a stop from 929 u/s in gear 5, 4.53 s to the clutch: 5-4 at 779 (a blip), 4-3 at
      599 (a blip), 3-2 at 380 (a blip), 2-1 at 170 (a blip), the clutch in at 122 u/s from gear 1; one gear at a time
      (DownBands)` (the numbers yours; test 57's said about 2.1 s to the clutch).
    - If 5-4 comes above 46 on the dial (over the pull's 4-5): `[Sound] DownBands=170,380,600,760`.
    - A/Bs: `[Steer] CoastDrag=` (test 57's roll), `CoastDrag=300,60` (a firmer start, a longer gentle tail),
      `CoastDrag=280,120` (a shorter tail), `CoastDrag=225,225` (an even slowing, about as long).
19. **From a middle speed, and braking**: the same coast from about 30 on the dial: the down-shifts one gear at a time,
    the clutch in 1st. Then at the top speed brake hard (Space or back) to a stop: as quick as in test 57, one or two
    quick down-shifts, then the idle (the coast line ends `braked after ...`). And near the end of a coast press A or D
    alone: the side key's slow creep starts only once the roll has ended, now up to about a second later than before
    (the throttle's tail takes that long): a bother?

**The look and the aim** (steps 20-24; your wish after test 57: "can 'free camera' when on bike be under right-click
instead of Z key?", and your decision: "I would like to block aiming because it slows down the bike, as when
walking"; "Z in 3rd person doesn't work")

20. **The right button looks, in first person**: ride in first person at speed with no weapon out. Hold the right
    mouse button and move the mouse: only your head turns, the bike keeps going straight; let go and the view comes
    back. Z still does the same.
    - `view: the look key (Mouse 2) held at 862 u/s: the mouse turns the head only (the bike keeps its line)`. If it
      says `(Mouse 2, by the game's own button event)`, the plugin's key reading didn't see the button and it read the
      game's own event: send it either way.
21. **No aiming on the bike**: ride at full speed in first person with a pistol out. Hold the right button for a few
    seconds and watch the dial: the game must not aim (no iron sights, no zoom) and the bike must not slow down; the
    left button still fires. The same in third person.
    - Once, at the first ride: `aim: AttackBlockHandler (PlayerControls+0x220, vtable +0x...): ShouldHandleEvent (slot
      1, +0x...) wrapped and OnButtonEvent (slot 8, +0x...) wrapped: while riding the game's aim (SecondaryAttack) is
      kept from it (AimBlock); ...`. If it says `aim: no AttackBlockHandler at PlayerControls+0x220 (...)` or gives
      another reason, nothing is blocked (the look on the button still works, the game aims too): send it.
    - Each press: `aim: the game's aim (SecondaryAttack, the mouse's button 2, the right) pressed at 912 u/s in first
      person (a weapon drawn): kept from the game while riding (AimBlock): ...`, and at its release `aim: the aim's
      button let go after 1.8 s: 108 event(s) kept from the game (ShouldHandleEvent answered no 108, OnButtonEvent
      dropped 0), 0 passed on; the gun state 0 (drawn) throughout: the game never aimed; the bike 912 u/s at the press,
      905 at its least, ...`. "OnButtonEvent dropped" above 0 means the game reached the aim another way and the
      plugin's second gate caught it: send it.
    - On getting off: `aim: this ride: N press(es) of the aim's button (N kept from the game), 0 aim(s) by the game (0
      slowed the bike); ...`.
22. **The aim's A/B** (test 57 couldn't say whether an aim slows the bike): set `[Steer] AimBlock=0`, ride at full speed
    with a pistol out and hold the right button for 3 s: now the game aims. Did the bike slow down? The log says either
    way: `aim: the game aimed (the gun state 6, sighted) for 2.1 s while riding (the aim's button passed to it): the bike
    925 u/s at its start, 610 at its least (-34%), 640 at its end, the throttle 1.00 -> 0.71: the aim slowed the bike
    (AimWatch)`, or `... the aim didn't slow the bike`. Put `AimBlock=1` back.
23. **The look in third person**: ride in third person at speed. Hold the right button (or Z) and move the mouse: the
    camera swings round you (look at the bike from the side, from the front) while the bike keeps its line; A and D
    still turn the bike. Let go: the camera swings back behind you in about half a second, and the bike does NOT turn
    toward where you looked. Do it four or five times, with big swings (more than 10 degrees) and small ones. The first
    look of the session teaches the plugin where the game keeps the camera's turn: if after it the bike still turned
    toward the camera at the release, say whether later ones did too. Swung far round, does the bike slide sideways?
    - Once a session: `view: the third-person camera's look is its root's +y column (...)`. Each hold: `view: the look
      key (Mouse 2) held in third person at 880 u/s: the mouse swings the camera round you, the bike keeps its line
      (LookThird; the camera 2 deg off the bike now)`, and once a ride with A or D `steer: the look held in third person:
      the side keys turn the bike (...)`.
    - Each release: `view: the look let go in third person after 3.1 s (the camera 95 deg off the bike at most, 80
      now): eased back behind over 0.5 s through ThirdPersonState +0x... (...) (LookThirdBack); this hold: ...`, then
      `view: the third-person camera back behind you after 0.50 s (...)`; or, before anything is learned, `...: no
      ThirdPersonState float followed the camera's yaw yet: the camera not eased back; the bike keeps its line till the
      camera is back within 20 deg of it (move the mouse back) (LookThird); this hold: ...`, then, once you bring the
      camera back, `view: the third-person camera back within 20 deg of the bike after ...`; or `view: the third-person
      camera didn't follow ThirdPersonState ...: the ease stopped, off this session; the bike keeps its line ...`. Send them all: "this hold:" names the field that came closest. "the camera 0 deg
      off the bike at most" while you swung it would mean the game turned the camera with you.
24. **A look cut short**: hold the right button in third person and open the Pip-Boy, or switch to first person while
    holding it: the look just ends, no jump of the bike (`view: the look in third person ended at once (the Pip-Boy):
    the camera left where it is (LookThird)`, or `(first person)`).
    - A/Bs: `[View] LookThird=0` (the look in first person only, 2026-11-17a's), `LookButton=0` (no look on the right
      button; with `AimBlock=1` the button then does nothing while riding).

**Handguns in third person** (steps 25-28; test 57: "in 3rd person character legs were spasming or she was just
running with a gun while having bike skirt on, also in 3rd pistols were just flying around when holstered, hunting
rifle was placed in strange spots"; the MCM's "Weapons while riding" on "Handguns only", your visible-holster mod on)

25. **Holstered, nothing in the hand**: ride in third person with a pistol equipped and holstered: nothing in her right
    hand, nothing lying on the forearm; the holster mod's pistol on the thigh still shows. Press the hunting rifle's
    number key while riding: it comes equipped and holstered (it can't be drawn while riding: R draws nothing until you
    get off), only on her back where the holster mod puts it, never along the arm, down her side or across the tank. A
    short video.
    - At each holstered spell with a weapon equipped: `gun: holstered: 8 held shape(s) of the hand's weapon 3D 'Weapon
      10mm (00004822)' < 'Weapon' < 'RArm_Hand' shrunk to a speck (GunHandHide); the game's own: bit 0 on that 3D clear,
      on 'Weapon' clear, its world scale 1.000`. Send it: "clear" and 1.000 say the game didn't hide the hand's copy on
      the bike (test 57's case, hidden by the plugin now); "set" or a scale of 0 would say the game did, and test 57's
      copies came from something else.
    - A/B: `[Tilt] GunHandHide=0` (the hand's copy shown again, as in test 57).
26. **Holstering in third person**: draw and holster the pistol a few times in third person while riding (R, wait a
    second, R): after each holster the arms stay on the bars and the legs on the seat, no swing or run for a moment.
    - Each put-away: `gun: put away in third person: the seat pose kept 0.xx s until the clips were back on the seat
      (the clips' hands L/R 9.0/12.0 from the grips, the knees 64) (GunAwayKeep)`, or `... kept 1.00 s (the most, 1 s):
      the clips not back on the seat (...)`; the ride's line at getting off ends `kept through K put-away(s) in third
      person, 0.xx s on average (GunAwayKeep)`. "(the most, 1 s)" every time would mean the plugin's measure of "seated
      again" doesn't fit your game: say so.
    - A/B: `[Tilt] GunAwayKeep=0` (eased out at once, as in test 57).
27. **Drawn in first person, then third**: draw the pistol in first person, then switch to third person with it still
    out: she sits with both hands on the bars at once (test 57: she ran with the gun until you holstered and rode a
    while). Holster; again a couple of times. Watch the bike: it may jump once, about a second after you're back in
    third person (the script swaps the bike under you back): say if you see it.
    - At the draw in first person: `gun: the worn bike's bone is another now (...): the seat poses kept, the rider's root
      and arms the same (GunSeatKeep)`, and no `gun: the still/riding seat pose dropped` there; back in third person, at
      once, `gun: a handgun out (...): the rider on the riding seat pose read N s ago, both hands on the bars
      (GunBothBars) (GunPose)`.
    - A/B: `[Tilt] GunSeatKeep=0` (the pose dropped at the swap: the running legs, as in test 57).
28. **Cycling the number keys**: riding, cycle quickly through your number keys, the pistols and the rifle mixed: "Only a
    handgun can be used on the motorbike." should come only when the rifle ends up equipped.
    - `Papyrus.0.log`: `Weapons: [Weapon <10mm (00004822)>]'s equip handled after [Weapon <HuntingRifle (0004F46A)>]
      came: no note for it (the plugin's GunNoteSure).` where 2026-11-17a wrote "[Form <10mm>] equipped, not a handgun";
      the rifle's own `Weapons: [Weapon <HuntingRifle ...>] equipped, not a handgun: it stays holstered while riding (the
      plugin's DrawHandgunOnly).`; rarely `... equipped: the worn weapon slot held another weapon at 3 look(s): not
      judged, no note (the plugin's GunNoteSure).`. No pistol named "not a handgun".
    - A/B: `[Tilt] GunNoteSure=0` (2026-11-17a's note).

**The bike after your body** (steps 29-31; test 57: "when swapping between 1st and 3rd person bike and even character
model were disappearing, mostly in 3rd person": of 22 switches to third person the 14 that came after your body had
shown in first person lost the bike, four times you too, for 2 s to a whole minute, until a weapon was drawn or put
away; the 8 with a pistol out in first person, no body, were all fine)

29. **First person with your body, then third**: ride in third person, switch to first person with no weapon out (your
    body shows), ride 5-10 seconds, switch back to third person (the view key or the wheel). Are the bike and you there
    at once, and do both stay? Five times or more in one ride: short spells (2 s) and one long one (a minute or more).
    Right after each switch, watch for one very short flicker of you and the bike (a single frame): say if you see it.
    - At every switch to third person while riding: `third: at the switch from first person to third person (switch N
      this ride, after X s in first person; your body shown in it, ...): you at (...) ...; your root's list: E
      entr(ies), W naming the worn bike's 57 shape(s) (...), ...; NearThird on|off; BodyRedraw: ...` (57: test 57's 54
      and the three new shapes), then `third: 0.5 s after ...`, `2.0 s ...` and `4.0 s ...` (or `third: back in first
      person ...`).
    - After a showing: `body: your 3D marked changed (ScenegraphChange, bit 29 on the root) 0.36 s after your body's
      showing (third person) ... ended: third person, the worn bike plain ...` and `body: the game took the mark 0.01 s
      after it (ScenegraphChange clear again)`. If the game left it: `body: the mark left set by the game for 3 frames:
      you hidden for one frame with it ...` (that frame is the flicker), then it took it, or `... taken back (...)`. On
      getting off: `body: BodyRedraw this ride: N end(s) ..., M mark(s) of your 3D (ScenegraphChange), the game took K,
      hidden one frame H time(s), T taken back (got off)`.
    - Send the log with the time of any switch that lost the bike: the "third:" lines of the drawn and the lost switches
      side by side say where the game keeps it.
30. **After the Pip-Boy, after a draw**: in first person with your body showing open the Pip-Boy, close it, and switch
    to third person within a second or two. Then again, but draw a pistol in first person and switch to third person
    half a second later with it out. For comparison, the same switches with a pistol out the whole time in first person
    (no body): the bike was always there in test 57; it should still be.
31. **The lights after a switch, and the A/Bs**: right after coming back to third person (with and without your body
    before), brake hard and switch the headlamp off and on (its hotkey): do the brake light and the lamp's glow still
    show? (The game keeps what it drew you from, so a part hidden at that moment could stay hidden: this tells.) If the
    bike (or you) still goes missing anywhere, note the time, then one ride each: `[View] BodyRedrawHide=0` (the ask
    alone, no flicker possible) and `[View] BodyRedraw=0` (2026-11-17a's: the bike should go missing again after your
    body). If the "third:" lines read 0 entries in your root's list throughout, also one ride with `[View] BodyWorn=0`
    (the worn bike not shrunk away with your body: test 55's second bike in first person comes back with it, and it says
    whether the shrinking is what the game keeps). Say which changed what.

**The A/Bs** (step 32)

32. Any of this build's A/Bs you haven't tried yet, one at a time, a ride or two each (README's table of this build's
    keys): `[View] BodyRedraw=0`, `BodyRedrawHide=0`, `LookButton=0`, `LookThird=0`; `[Steer] AimBlock=0`, `CoastDrag=`
    (and `300,60`, `280,120`, `225,225`); `[Tilt] GunHandHide=0`, `GunAwayKeep=0`, `GunSeatKeep=0`, `GunNoteSure=0`;
    `[Look] KitFollow=0`, `KitSlotSettle=0`, `KitMouse=0`, `KitWheelOwn=0`, `KitNewSlots=0`; `[Sound]
    HeardRiseGears=2,0.79,0.65,1,1` with `ShiftGapGears=0,2,3,1.5` and `DownBands=170,400,700,860` (test 57's gears),
    `DownBands=170,380,600,760`. `[Diag] ThirdWhere=0` and `AimWatch=0` change only log lines (with `AimBlock=0` too,
    `AimWatch=0` leaves the aim's handler untouched). Anything better or worse?

Send `CMB_Slope.log` and its `_prev` logs and `Papyrus.0.log` of each session, any crash log, the screenshots of steps
1-11 (each wear, the tyres, the badges, the plates, the headlamp's colours, close and riding) and 16 (the three new
views), and a short video of steps 13-14, 23, 25-27 and 29-30 if you can.

### Questions for you (test 58)

- **T58-1 (step 1).** Each wear look: does it read as its name? Which would you change, and how?
- **T58-2 (step 2).** The wear over Gloss black and Free colour: right? Blood on the dark paints readable?
- **T58-3 (step 3).** The badges clean over the wear, no flicker, no line across a tank badge? The wear in first person?
- **T58-4 (step 4).** The wear lit like the paint, by day and at night? A flicker or a halo from a distance?
- **T58-5 (step 5).** The muddy tyres: the tread caked, the sidewalls splashed, the bands partly showing?
- **T58-6 (step 6).** The front fender badge on the mudguard, the right way round from in front, turning with the bars?
- **T58-7 (step 7).** Nuka-Cola and Red Rocket on the tanks and both fenders: right? From riding distance?
- **T58-8 (step 8).** The Enclave helmet on the flag: the stars too small, the flag too busy? The right tank's blue
  corner toward the rear: a bother?
- **T58-9 (step 9).** The Brotherhood helmet between two cogs, clear of the helmet and the edge?
- **T58-10 (step 10).** The plates' top lines centred, clear of the tail lamp from low behind?
- **T58-11 (step 11).** The five colours on the road and in the lens? Amber too dim? The beam at once after Apply, still
  after cells?
- **T58-12 (step 12).** As it came exactly as 2026-11-17a? The frame rate beside the parked bike, stock against Wasteland
  (and 2026-11-17a)?
- **T58-13 (step 13).** The wheel's zoom and the drag anywhere off the lists? The lists by the arrow keys: fine? What did
  the close line's "the wheel: E event(s) kept" say?
- **T58-14 (step 14).** After E the rear kept, every preview the same? What did the "the menu's models" line say?
- **T58-15 (step 15).** The highlight walking: no swing, a turn after a quarter second? The close line's slot counts?
- **T58-16 (step 16).** The three new views: right, or which would you change?
- **T58-17 (step 17).** The gears in even steps at about 12, 24, 36 and 46, each still climbing? The spacing right?
- **T58-18 (step 18).** The coast from the top: about twice as far, gradual, the down-shifts spread over it? Too long,
  too short? Which `CoastDrag` A/B felt best?
- **T58-19 (step 19).** From 30 on the dial, and a hard brake: as before? The side key's later creep a bother?
- **T58-20 (step 20).** The right button's look in first person: which "view: the look key (Mouse 2 ...)" line came?
- **T58-21 (step 21).** No aim and no slowing with the right button held, in first and third person? The left button
  firing? The "aim: AttackBlockHandler ..." line?
- **T58-22 (step 22).** With `AimBlock=0`: did the aim slow the bike? What did "aim: the game aimed ..." say?
- **T58-23 (step 23).** The look in third person: the camera round you, the bike on its line, back behind in half a
  second with no turn, from the first look on or later? A sideways slide? The release lines' "through ThirdPersonState
  +0x..." and "this hold:"?
- **T58-24 (step 24).** A look ended by the Pip-Boy or first person: no jump?
- **T58-25 (step 25).** No gun in the hand or along the arm while holstered, the holster mod's copies still there? What
  did "the game's own: bit 0 ..." read?
- **T58-26 (step 26).** After a holster in third person: the arms on the bars, the legs on the seat? How long did "the
  seat pose kept" say?
- **T58-27 (step 27).** A pistol drawn in first person: seated at once back in third person? A jump of the bike?
- **T58-28 (step 28).** Cycling the number keys: the message only for the rifle, no pistol named "not a handgun"?
- **T58-29 (step 29).** The bike and you there in third person after your body, every time? A one-frame flicker? "the
  game took the mark" each time?
- **T58-30 (step 30).** After the Pip-Boy and a pistol's draw: the bike there? With a pistol out all along, as before?
- **T58-31 (step 31).** The brake light and the lamp's glow after a switch? Which A/B changed what?
- **T58-32 (step 32).** Anything a 2026-11-21a A/B made better or worse?

## Test 57: the 2026-11-17a build (test 56's fixes and art corrections)

The 2026-11-17a build answers test 56 (run on 2026-11-16b): its fixes and its art corrections in one build (your pick;
the rest of build B, wear and weathered paint, the front fender's badge and the headlamp's lens and beam, comes later).
Steps 1-8 are the art, steps 9-30 the fixes, with the questions T57-1 to T57-30 at the end. What test 56 liked is as it
was.

- **The art corrections:** the Brotherhood of Steel, Minutemen, Nuka-Cola and Red Rocket plates redrawn after your
  pictures (the letters unchanged); the 3D Enclave helmet standing on a polished chrome plate (the black one hid it);
  the Gunners skull on a green flag patch; the flat Brotherhood of Steel tank badge in colour (no red wings); Saddle tan
  browner, less yellow.
- **The fixes:** the field kit's bike held by the plugin (drag to turn it about its middle, the wheel to zoom), turned
  to each slot's part, and the kit set out where you stand when its spot has no room; the take-off a tad quicker and a
  stop's down-shifts one gear at a time; the weapon rules no longer switched off by a menu (in test 56 the Pip-Boy right
  after a put-away switched them off for the session, so its steps 25-26 were never really tested: steps 16-17 do them
  again), rifles never drawn while riding (the plugin stops the game's draw: the rifle stays equipped and holstered, and
  "Only a handgun can be used on the motorbike." still shows), a rifle's number key with a pistol out putting the pistol
  away first, a quick swap no longer taken for "not a handgun", the spikes from the hands; in first person the camera's
  place found as your game eases it (in test 56 the shake fix never ran), the bike kept near the camera while the
  plugin swaps its first-person bike, the bike drawn again in third person after your body showed ("crazy frog"), the
  eye in front of your neck (no looking into your outfit), and the game's first-person arms hidden with the look key.

Do this section's steps in one game session if you can, in this order (the art and the kit by the parked bike in one of
your settlements, then the rides), and say which session each step was in. Every new behaviour of the plugin has a key
whose off value gives the 2026-11-16b build back (README's table of this build's keys), so each A/B is one key away; the
art's A/B is files (after step 8). Things only the game can settle: whether your camera eases the way test 56's numbers
say (step 23), whether every draw of a weapon goes through the call the plugin stops (step 21), which of two causes made
the spikes (step 22), how the armour menu's fields and the wheel's input read in your game (steps 9 and 10), whether
the worn bike comes back in third person for the reason the game's flags suggest (step 26), and how a braked stop
sounds (step 14).

Before you start:
- install as a Replace over 2026-11-16b. If you edited `CMB_Slope.ini`, put your values into the new one: `[Tilt]`,
  `[Look]`, `[View]`, `[Sound]` and `[Diag]` have new keys, and `[Steer] LaunchFrom`, `[View] BodyEye`, `BodyLeanMax`,
  `[Sound] HeardStop` and `HeardBrake` new defaults (README's table). Otherwise use the shipped file as it is;
- load your usual save. The ESP and the MCM are 2026-11-16b's (22 controls in Look); Riding's "Weapons while riding" on
  "Handguns only";
- have two handguns (a 10mm and the .44, or the flare gun) and a rifle on the favourites' number keys;
- each A/B below: change one key in `CMB_Slope.ini`, save the file, get off and on (no restart), and put it back after.

The log's first lines: `CMB_Slope.log` has five settings lines more: `  view (2026-11-17a, test 56): BodyNodes=0 (...)
BodyArmsLook=30 (...); [Diag] BodyWornLine=1 (...)`, `  view (2026-11-17a, test 56): CameraEase=1 (...) NearHandover=1
(...)`, `  weapons (2026-11-17a, test 56): GunCheckUnpaused=1 GunCheckRecover=0.5 DrawHandgunOnly=1 QuickHolsterFirst=1
GunJudgeWait=1 NodelessOnce=1 SkinArraysCheck=1 [Diag] HeldWhere=1 (...)`, `  kit (2026-11-17a): [Look] KitHold=1 (...)
KitSlotView=1 (...) KitTurnTime=0.35 KitZoom=0.6,3,1.12 KitDrag=0.25,0.25 KitHoldAbove=0.55; views (heading,
elevation): rear -165,10, tank L -90,10, tank R 90,10, seat -60,60, fender -150,40, wheels -80,3; KitRoom=1 (...)
KitRoomRing=20 KitRoomBench=60` and `  sound (2026-11-17a, test 56): DownBands=170,400,700,860 DownBlend=100: ...`; the older lines now
say `from rest the throttle starts at 0.14 (LaunchFrom)`, `HeardStop=900 HeardBrake=1500`, `BodyEye=(0, 6, -3)
BodyLeanMax=40` and `CMB_LookOptions 262143`. No 2026-11-17a lines, or `CameraEase=0 (CameraPlace's probe as
2026-11-16b)` and `DownBands=: a stop's down-shifts by the speed SpeedMap gives the engine (the 2026-11-16b build)` with
an INI you didn't change, mean an older `CMB_Slope.dll` or `CMB_Slope.ini` is loaded: stop and say so.

### The art corrections (2026-11-17a): steps 1-8

At the field kit choose each in turn and look at it in the kit's preview, then leave the kit and look at the parked bike
close up, then ride away and look at it from the riding camera, in third person from the side and from behind. A
screenshot of each, close and riding, please, beside your picture if you can. Every other plate, badge and seat is as
in test 56.

**The plates** (steps 1-4; test 56: "BoS logo on plate wrong, minuteman logo on plate wrong, nuka cola plate logo wrong,
red rocket plate - whole design"; the letters "looked better than before" and are unchanged)

1. **Brotherhood of Steel** ("Plate: Brotherhood of Steel"): top left, the Brotherhood's emblem in colour: a white disc
   with three black cogs, a dark sword point up through it with a gold cross-guard and pommel, blue wings sweeping up
   both sides, a dark outline. The plate stays steel grey with its legends. From riding distance it should still read
   as a white disc on blue wings. `Papyrus.0.log`: `Customise: plate = Plate:bos (8)`.
2. **Minutemen** ("Plate: Minutemen"): top left, in the plate's cream on its blue: the flag's device, a musket from
   lower left to upper right broken by a lightning bolt, and three stars. Does it read as the Minutemen's from riding
   distance? `Customise: plate = Plate:minutemen (9)`.
3. **Nuka-Cola** ("Plate: Nuka-Cola"): top left, a red crimped bottle cap with "Nuka" and "Cola" in white script and a
   swoosh between them; "ZAP THAT THIRST!" along the top where the script line was; the wave and "ENJOY NUKA-COLA!" as
   before. The cap is the plate's own red, so from riding distance it may be faint: would a white or steel cap read
   better? `Customise: plate = Plate:nuka (6)`.
4. **Red Rocket** ("Plate: Red Rocket"): the whole plate as the round sign: a black rim, a red frame, a yellow centre
   with the plate's letters in red, the round sign in the top-left corner (two R's back to back with a red rocket
   between them), "RED ROCKET" along the top and "GASOLINE - DIESEL - FUSION" along the bottom, both white. Then try one
   other "Plate background": the yellow centre takes that colour and the red frame stays (Cream gives the same yellow as
   the design's own). A thin yellow line may show round the black rim. `Customise: plate = Plate:redrocket (7)`.
   - For each: is the emblem clear of the big letters? How does it read from riding distance?

**The badges** (steps 5-7; test 56: "enclave background shouldn't be black - it makes helmet not clearly visible -
chrome would be nice"; the Gunners skull "should look like on attached pic"; the flat Brotherhood of Steel badge showed
red wings)

5. **The Enclave helmet on chrome**: set Tank L and Tank R to "Enclave helmet (3D)": the plate under the helmet is now
   polished chrome inside its chrome edge, with a thin dark line between the edge and the plate. Parked and riding, by
   day and at night: does the dark helmet stand out clearly against the chrome, and at night does its shape show, not
   only its amber eyes? Is the chrome too bright, or too plain? Then "Brotherhood helmet (3D)": its plate stays steel
   grey. `Customise: tank left = TankL:enclavehelm3d (17)`, `Customise: tank right = TankR:enclavehelm3d (18)`.
6. **The Gunners skull** ("Gunners skull" on Tank L, Tank R and Fender): a deep green patch with slightly rounded
   corners and a rough-edged white skull in its middle, the X on its forehead, two eye holes, a nose hole and stitched
   teeth, the green showing through them. Nothing of it cut off at the plate's edge or the fender patch's (on the fender
   it is squashed a little, as the old skull was). Compare it with your picture. `Customise: tank left = TankL:gunskull
   (19)`, `Customise: fender = Fender:gunskull (18)`.
7. **The Brotherhood of Steel badge** ("Brotherhood of Steel" on Tank L, Tank R and the Fender): the colour emblem, a
   white disc with three black gears, a grey sword through it with a gold cross-guard and pommel, blue wings both sides,
   a black outline; no red anywhere. From riding distance too. `Customise: tank left = TankL:bos (2)`.

**The seat** (step 8; test 56: "saddle tan too yellow")

8. **Saddle tan** ("Seat: Saddle tan"): a warmer, browner leather tan, no longer yellow-orange. Still clearly different
   from Tobacco brown (darker than it), Red and Cream, parked and riding? `Customise: seat = Seat:tan (3)`.

The art has no INI switch. Its A/B is files: the 2026-11-16b package's eight textures (`Data\Textures\CMB\Bike\`
`badges_d.dds`, `badges_n.dds`, `badges_s.dds`, `seat_p.dds`, `plates_d.dds`, `plates_n.dds`, `plates_s.dds`,
`plate_p.dds`) in a small MO2 mod of their own, ticked below this one, give test 56's plates, badges and seat back
(README's table of this build's art switches).

### Test 56's fixes (2026-11-17a): steps 9-30

**The field kit** (steps 9-11; test 56: "zoom didn't work in field kit", "seemed like I was able to grab it only by
front wheel", "would be nice if position of bike changed when selecting an option", "field kit pushes me through the
wall if there is not enough space")

9. **Turn and zoom**: Customise, pick the Motorbike. Hold the left mouse button anywhere above the menu's lists and
   move the mouse: the whole bike should turn about its middle, left and right spinning it, up and down showing it more
   from above or below, never tipping sideways. Let go. Roll the mouse wheel with the cursor above the lists: it zooms
   in and out about the middle; over the lists the wheel only scrolls them. The menu's own grab (the front wheel) and a
   gamepad's stick turn it the same way.
   - At the first Customise of the session: `kit: hold: MenuControls (+0x30E8B10) ...: its input read (slot 0 wrapped,
     passed on; ...)` (or `kit: hold: MenuControls: ...: no wheel zoom and no drag of the plugin's own ...`: send it),
     and only if the cursor isn't found `kit: hold: the cursor unknown (MenuCursor: ...): the wheel and the drag act
     wherever it is`.
   - At each Customise: `kit: hold (2026-11-17a): the menu's bike (item ...) held about its centre (0.0, 0.0, 56.2) of
     its own, at (...) in the menu's view (the fit at the menu's turn: ...); the menu's turn: heading -45.0, elevation
     12.8 (the three-quarter view); ...` (the `kit: fit` lines of test 56 don't come with KitHold on).
   - At the close: `kit: hold: the menu's bike (item ...): the menu closed after N frame(s): ...; the wheel K notch(es)
     taken (J with the cursor below KitHoldAbove), zoom Z; turned by the drag in D frame(s), by the menu's own turn T
     time(s); S slot change(s); the input read (E event(s), V mouse move(s), the mouse's buttons: ...); the cursor last
     at ...; the view at the end: ...`. Send it: "the mouse's buttons" says which codes your wheel sends (0x800 and 0x900
     expected), "E event(s)" 0 would mean the menu's input never reached the plugin, and the cursor's range shows
     whether the menu keeps the cursor to part of the screen.
   - If the wheel or the drag counts too high or too low on the screen: `[Look] KitHoldAbove` (0.55, the top part of the
     screen where they act). A drag that turns the wrong way: `KitDrag=-0.25,0.25` (or the second number negative).
     A/B: `[Look] KitHold=0` (2026-11-16b's preview: the menu's own turn about the bike's bottom, no zoom).
10. **A view per slot**: move through the slots on the left. Plate, Plate text, Plate letters and Plate back should turn
    the bike to show its rear; Tank L its left side, Tank R its right side; Seat from above; Fender the rear fender
    from behind and above; Rims and Tyres the wheels from the side; Paint and Mirrors the usual three-quarter view. Each
    turn should glide (about a third of a second), not jump, and from any of them you can still turn and zoom it.
    Screenshots of two.
    - 30 frames into each visit, once: `kit: slot: the menu's state N; its slot objects n (index i: XXXXXXXX 'Plate');
      its keyword ...; its mods m (...): the slot Plate`. Send it: it shows how the armour menu's fields read in your
      game (if the slot objects and the keyword read "not a keyword" or "none" and only the mods give the slot, the
      turns still work, by the mods' names).
    - At each slot: `kit: hold: the slot 'Plate' (from the highlighted slot object): the rear, heading -165.0, elevation
      10.0 (eased over 0.35 s)`; leaving the lists, `kit: hold: no slot: three-quarter (the menu's own turn), ...`.
    - A view you'd like otherwise: `[Look] KitViewRear`, `KitViewTankL`, `KitViewTankR`, `KitViewSeat`,
      `KitViewFender`, `KitViewWheels` (heading, elevation, in degrees: README's table), `KitTurnTime` for the glide (0
      jumps). A/B: `[Look] KitSlotView=0` (one view; the turn and the zoom as in step 9).
11. **The wall**: park the bike along a wall, a metre or less from it, stand at its front or back on the wall's side
    and choose Customise with your usual field kit (test 56 used the armour bench, mode 3, every time): you shouldn't be
    moved into or through the wall; the bench (or the toolbox, modes 1 and 2) comes out where you stand instead (it may
    overlap the bike or the wall to look at; you stay put). Again with the bench's side of the bike towards the wall. Then
    in the open: as before, the kit beside the bike.
    - `CMB_Slope.log`: `room: ask N at (x, y, z), heading H (the field kit's spot: KitRoom): room (...; 10 rays, none
      towards the bike)` in the open (with the armour bench, field kit modes 3 and 4: `(the field kit's bench: KitRoom)`,
      its own place 110 out), and by the wall `... none, no clear line from the player: ...` or `... none, something N
      from it at 50 over its ground (...)`. With the bench and no room the bench comes out where you stand.
    - `Papyrus.0.log`: `The field kit's spot: room (...)` or `... none (...)`, and `Customise: field kit mode 1 (the
      toolbox) at x, y, right of the bike`, ending ` (moved N to where you stand: no room at its spot)` when it had none.
    - A/B: `[Look] KitRoom=0` (2026-11-16b: the spot never checked).

**The take-off and the stops** (steps 12-15; test 56: "takeoff is a tad too slow, beside that it was ok"; "shifting
down when being slowed down or stopping is sometimes weird, not natural": a third of the down-shifts skipped a gear,
two or three blips inside a second, late)

12. **The take-off**: from a stop on a long flat road hold forward to the top speed. The first second should be a
    little quicker than in test 56, but no jump: 2nd at about 12 on the dial (test 56: about 10), then the same even
    climb, the gears sounding as before. Right now, still slow, or too quick?
    - `launch: from rest: 0.3 of the top after ~1.9 s, half after ~3.5 s, 0.9 after ~6.9 s, the top (0.97) after ~7.5 s
      (the throttle from 0.14 ...)` (test 56: 2.2-2.4, 3.7-4.0, 7.0-7.3 and 7.6-7.8 s), and `sound: gear 2 at ~210-220
      u/s, ...; the engine's speed ~470 (SpeedMap)` (test 56: 175 u/s), gear 3 at about 440 u/s, gear 4 at about
      750-800, gear 5 at about 910.
    - A/Bs: `[Steer] LaunchFrom=0.1` (test 56's take-off), `LaunchFrom=0.17` (a little quicker still).
13. **Coasting to a stop**: at the top speed let go of forward and coast to a stop without braking. You should hear four
    down-shifts, one gear at a time, each with one short blip, spread over about two seconds (5-4 at about 40 on the
    dial, 4-3 at about 33, 3-2 at about 22, 2-1 at about 10), then the idle as the bike stops. Natural? Then the same
    from a steady 30 on the dial, and from 20 (from a cruise the first shifts come one after another, 0.4 s apart, until
    the engine has caught up with the speed).
    - In each stop the gear lines end `; the engine's speed N (DownBands)`, and at the clutch: `sound: a stop from 877
      u/s in gear 5, 2.11 s to the clutch: 5-4 at 744 (a blip), 4-3 at 583 (a blip), 3-2 at 397 (a blip), 2-1 at 170 (a
      blip), the clutch in at 49 u/s from gear 1; one gear at a time (DownBands)`. Every `a stop from` line without "a
      hard stop" should list steps of one gear.
    - The first shift comes about 0.7 s after you let go (the plugin keeps a let-go key 0.2 s, and the engine brakes
      first), so from the top 5-4 lands nearer 40 than 48 on the dial. If it feels late: `[Sound] StopAfter=0.15`.
    - A/Bs: `[Sound] DownBands=` with `HeardStop=300` and `HeardBrake=600` (test 56's down-shifts),
      `DownBands=200,450,760,880` (each a little earlier).
14. **A hard brake**: at the top speed brake hard to a stop: one or two quick down-shifts, then the engine drops to idle.
    Does it sound like an emergency stop, or should it step further down first? `sound: a stop from ... , braked: 5-4 at
    823 (a blip), 4-3 at 190 (a blip), the clutch in at 41 u/s from gear 3; a hard stop (braked: the bike stopped before
    the gears could step down, the clutch took the rest)`. (A stop against a log or a wall with forward held still goes
    straight to 1st, as in test 56.)
15. **A short lift**: at a steady speed let go of forward for half a second and press again: no down-shift should come
    if the bike hardly slowed. Let go longer, until the bike has slowed a little, and press again: the engine may now be
    a gear or two lower than in test 56 (the pull's gear for that speed). Does that bother you? A/B: `[Sound]
    DownBlend=0` (the stop's shifts begin at every let-go).

**Handguns on the bike, again** (steps 16-22). Test 56's steps 25-26 were judged with the weapon rules off: the Pip-Boy
opened a second after the .44 went away switched them off for the session (12:53:08), so the seated pose with both
hands on the bars was never seen; steps 16-17 do them again. Then the rifles (test 56: "I stay on but it's not put away
immediately, it shouldn't even be pulled out"), a quick swap and the spikes. The MCM's "Weapons while riding" on
"Handguns only".

16. **Drawn right after getting on** (test 56's step 25 again): get on with a 10mm pistol equipped and ride off at once;
    within two seconds draw it (R) in third person while riding. You should be seated, both hands on the bars, the
    pistol in your right hand on the grip, and the bike shouldn't vanish and come back. Ride a while with it out, turn
    both ways, stop, ride off again. Fire a few shots: do the shots and the muzzle flash leave from the gun in your hand
    or from beside you? A short video helps.
    - `gun: a handgun out at N u/s with no riding seat pose yet: the still one (read N s ago) stands in until one is read
      (GunStillRide)`, and no `tilt: CMB_BikeWornRiderF_* back level and let go (no longer worn ...)` at that draw (the
      bike not swapped).
    - `gun: a handgun out (the weapon state 2, ...) at N u/s: the rider on the riding seat pose read N s ago, both hands
      on the bars (GunBothBars) (GunPose)`, then once a draw `gun: the drawn weapon's 3D (the biped's object 41, '<name>'
      ...) hangs off '<parent>' ...: carried from the game's right hand to the posed one (GunCarry)` (or `gun: no drawn
      weapon's 3D at the biped's object 41 ...` or `... has shapes held on the rider ...`): send it either way.
17. **Putting it away, the Pip-Boy, drawing again** (test 56's step 26 again, and its 1B): put the pistol away (R) and
    draw it again a few times, stopped and riding: any jerk at the moment of drawing or putting away (one frame is
    expected), anything flying off? Then put it away and open the Pip-Boy straight away; close it after 5 s or more;
    draw again in third person: seated with both hands on the bars as before? Do the same with the pause menu and with a
    quicksave in between, over a long ride. Is the pose there every time?
    - No `gun: the weapon state at Actor+0x134 reads 0 ... the weapon rules here off ...` line, and the weapon state's
      trace lines (`gun: the weapon state 0 > 2 > 3 in ...`) all session (in test 56 they stopped at 12:53:08).
    - If the check fails anyway: `... for 6.0 s (N s more with the game paused, not counted: GunCheckUnpaused): the weapon
      rules here off until the two agree again for 0.5 s (GunCheckRecover) (GunPose, GunStandBack)`, then `... agreeing
      for 0.5 s: the weapon rules back on (GunPose, GunStandBack; GunCheckRecover; switched off 1 time(s) this session)`.
      Send both.
    - Every 10 s posed and at the end: `gun: posed N s ...: the bones' own move a game frame at most X relative to the
      root the bones were animated with (Y against the task's root, GunRootFrame), ...; the drawn weapon carried N
      frame(s) (GunCarry)`; once a session `gun: the bones moved A a frame on average ...: the root a frame ahead of the
      bones, as GunRootFrame takes it (GunRootFrame)`. If it says `... the game's update isn't in the order GunRootFrame
      takes ...` instead, say so.
    - A/Bs: `[Tilt] GunCheckUnpaused=0` (real seconds: a menu right after a put-away can switch the rules off again, as
      in test 56), `GunCheckRecover=0` (once off, off for the session); and test 56's, never tried with the rules on:
      `GunBothBars=0` (the game's right arm carried to the seat's shoulder), `GunCarry=0` (the gun where the game's clip
      holds it), `GunRootFrame=0`, `GunPredictMax=0`, `GunStillRide=0`.
18. **A rifle by its number key**: riding with nothing drawn, press a rifle's number key: the rifle must NOT come out. It
    becomes your weapon, holstered, and "Only a handgun can be used on the motorbike." shows. Press R with it equipped:
    nothing is drawn. Get off: R draws it.
    - At the first ride: `gun: the player's slot 0xC9 (+0xDA13D0, DrawWeaponMagicHands) wrapped: riding, Handguns only,
      the game's draw of a weapon that isn't a handgun refused, it stays equipped and holstered (DrawHandgunOnly; ...)`.
    - The key: `quick: key 0x3N (...) ...: the game's own hotkey use (QuickUse)`, then `gun: the game's draw of XXXXXXXX
      (the weapon state 0) refused: not a handgun (...): it stays equipped and holstered (DrawHandgunOnly)` (or `...
      refused: the number key's XXXXXXXX not the equipped weapon yet (...)` and then `gun: number key's XXXXXXXX
      equipped: not a handgun (...): it stays holstered`). `Papyrus.0.log`: `Weapons: [Weapon <...>] equipped, not a
      handgun: it stays holstered while riding (the plugin's DrawHandgunOnly).`, and no "put away asked".
    - A/B: `[Tilt] DrawHandgunOnly=0` (the game draws the rifle, then it is put away: test 56).
19. **A rifle's key with a pistol out**: draw the pistol, then press a rifle's number key: the pistol goes away and the
    rifle comes equipped but holstered, never in your hands. The rifle that comes should be the one whose key you pressed
    (say if another one came).
    - `quick: key 0x3N ...: XXXXXXXX (form type 0x2B, a weapon not surely a handgun, with a weapon out): kept from the
      game, the weapon out put away first (QuickHolsterFirst)`, `gun: number key N's XXXXXXXX isn't surely a handgun
      (its base form) and a weapon is out (the state 3): the press held back, ...`, then `gun: put away 0.4x s after
      number key N (1 call(s)): its use given to the game (UseQuickkeyItem M: true), XXXXXXXX to come equipped and
      holstered (QuickHolsterFirst)` (M is the key's number less one), and Papyrus's "equipped, not a handgun" line;
      never `gun: CHECK: number key N's ... NOT equipped`. A grenade's key with the pistol out leaves the pistol out.
    - A/B: `[Tilt] QuickHolsterFirst=0` (the game swaps the rifle in drawn, then it is put away).
20. **A quick swap between handguns** (test 56: the .44 put away as "not a handgun" at 12:51:32): with a pistol out,
    cycle quickly through your number keys passing only handguns (the 10mm, the .44, the flare gun): each should come
    out drawn, none put away.
    - `Papyrus.0.log`: `Weapons: a weapon drawn and none equipped at this moment (unequipped [Weapon <...>]): judged
      again in 0.3 s (the plugin's GunJudgeWait).`, and no `... out, not a handgun (unequipped ...)` line for a handgun.
    - A/B: `[Tilt] GunJudgeWait=0` (judged at once).
21. **Getting on with a rifle out, and the other ways a rifle comes**: get on with a rifle out: it is put away first,
    as before. Riding, equip a rifle from the Pip-Boy, and once from the favourites menu: if it comes out drawn it is
    put away after, as in test 56 (the plugin stops only the game's own draw): `gun: XXXXXXXX out (the weapon state 3)
    without a draw through slot 0xC9 (...)` or `... swapped in with a weapon out (...)`, then the put-away.
    - On getting off after every ride: `gun: this ride the game asked N draw(s) through slot 0xC9: M refused, K given
      back; J weapon(s) that aren't handguns out by another way (DrawHandgunOnly)`. Send these lines: they say whether
      every draw of your game goes through the call the plugin stops. If N stays 0 while you drew handguns that ride,
      it doesn't (say so).
22. **The spikes from the hands** (test 56: after holstering a weapon on the bike in third person, long metal spikes
    from both hands in first person): holster your weapon in third person, swap weapons with the number keys in third
    person (the .44 among them), then go to first person and look at your hands for a while, riding. Any spikes? Then
    the same in first person only.
    - Each hold of new shapes mid-ride: `rider:   the new plain shapes hang off: 'Weapon 44 (000CE97D)' < 'WEAPON' < ...
      (HeldWhere)` (a holster mod's second copy shows as `... < 'WeaponPistolUp' ...`), and no `rider: NakedHands ...:
      34 bones without a node ...` line after the one at getting on.
    - Which of the two causes it was, if the spikes come: `rider: ...'s bone arrays were replaced by the game (...): held
      again with them (SkinArraysCheck)` (the game rebuilt the hands' bone lists) or `rider: ...'s node-less bone N (with
      the left hand) sits D from that hand (...): drawn so, the skin between them is a spike (HeldWhere)` (a finger left
      behind). Send any you see, with the time.
    - A/Bs: `[Tilt] NodelessOnce=0`, `SkinArraysCheck=0` (do the spikes come back with one of them?).

**First person** (steps 23-29; test 56: "bike still shakes too much", the body "shaking a lot more than bike" and the
hands moving round the bars, the bars and dial gone for a moment zoomed in, the bike gone in third person after your
body had shown ("looks like crazy frog"), the inside of your outfit when looking down, a second arm with the look key)

23. **The shake**: in first person ride for a few minutes: straight at full speed, over rough ground, through turns,
    and stop and go a few times. Does the bike still shake against your view? Do your hands stay on the grips, and does
    your body still shake more than the bike?
    - `CMB_Slope.log`, once, within about half a second of riding in first person: `camera: the camera root at
      GetTranslation's answer read as the camera root eased toward the player's place + the answer at call 1 (its time
      constant 7x ms) of 3 since the task (over the last N informative frames its error at the next task 0.0x (median) /
      0.xx (p90), the Lead's guess 0.6x / 1.4x; ...) ([View] CameraPlace, CameraEase): the view bike and your body follow
      the camera's own place at that call (settle 1)`. Another reading or call is fine: send the line. Its time
      constant says whether your camera eases the way test 56's numbers say (about 72 ms).
    - Good: no `camera: EyeAtCamera off this session` line; the `view: lock:` lines end `; CameraEase: the camera root
      eased toward ... (its time constant 7x ms); the kept reading off the camera root at the next task M (median) / Q
      (p90) / X (most) over F frame(s), the Lead's guess m / q / x there; ...; 1 settle(s), 0 fall-back(s) this session`
      with M well under m (test 56's Lead: 0.69 / 1.44), and `; BodyFollowCamera: N move(s) of your body ...` with N
      about the frames (test 56: 0 all session). Send its "its skeleton's own since the task A of the camera's B" too (A
      about 0 while B is a frame's travel would say your game updates your 3D after the camera).
    - Bad: `camera: CameraPlace: no reading of GetTranslation's answer matches the camera root in 120 informative frames
      (...)`, or `camera: the camera root off GetTranslation's answer read as ...: ... the view bike by the task's
      placement until a reading matches again, the probe goes on ([View] CameraEase; fall-back N)`: the bike is then
      placed by the frame's guess (test 56's shake) while the plugin keeps looking. Send the log: its figures are the next
      build's data.
    - A/B: `[View] CameraEase=0` (2026-11-16b's probe: off again at once).
24. **Into first person**: get off and on a few times and go into first person each time, by the view key and by the
    mouse wheel: the bike shouldn't jump or lag for a moment as you go in.
25. **Zoomed in, across cells**: in third person zoom in with the wheel until the camera is at your head (the
    first-person bike stands in near the camera, test 56's step 16) and ride on like that on a long straight run across
    a few cells, so the plugin hands the first-person bike over to a new one now and then: the bars and the dial should
    never vanish (test 56: gone for 0.6 s at 12:53:21). The log has `view: Parent: put back under its own cell (a
    handover)` and about a second later `view: handed over from ... to ...`; the video says the rest. A/B: `[View]
    NearHandover=0` (the bars gone for a moment at a handover).
26. **The bike after your body** (test 56: "when bike is visible in 1st, it stops being in 3rd - looks like crazy
    frog"): ride in third person, switch to first person (your body shows), ride a few seconds, switch back to third
    person (the view key or the wheel). Is the bike under you in third person right away, and does it stay for the rest
    of the ride? Three or four times in one ride, with and without zooming slowly. And in first person still ONE bike
    (one set of bars, one speedometer, no gun on the grip)?
    - At each showing: `body: hidden with the body: the worn bike's 54 shape(s) shrunk to a speck, 0 node(s) of it
      hidden (bit 0: none); the weapon's N shape(s) shrunk, 0 node(s) hidden (bit 0: none); ...`.
    - When it ends: `body: the worn bike as the showing ends (third person, third person): 54 shape(s) held, bit 0 on 0
      (the look's own 0, ours 0); the bone data: a speck on 0 of the ...; the culling spheres: 0 of 54 bone(s) smaller
      than the bind's; ...; our hidden nodes 0; the player's root 0x... (...); NearThird on (...)`, then `body: the worn
      bike 0.5 s after the showing ended (third person; now third person): ... NearThird off`. Read "a speck on 0", "bit
      0 on 0" and "our hidden nodes 0": if the bike is still gone with all of that, nothing of the plugin's is left on it
      and the cause is elsewhere (the line's root flags say more): send the log and the time.
    - A/B: `[View] BodyNodes=1` (2026-11-16b's hiding: the crazy frog should come back).
27. **Looking down** (test 56: "I was able to look into character model when looking down - should see body"): in first
    person with your body showing, look down as far as you like, also while riding: your chest, belly and legs seen from
    outside, not the inside of your outfit round a hole. Does your body sit right: on the seat, hands on the grips, feet
    on the pegs, not leaning back oddly (the upper body leans back about 5 degrees more than in test 56)? A screenshot.
    - `body: hidden with the body: ...; the eye BodyEye (0, 6, -3) from HEAD, the pitch wanted 4x deg (BodyLeanMax 40)`,
      and in the "shown" line `the upper body pitched 40.0 deg back ...` with the body moved about 2 back and down.
    - A/B: `[View] BodyEye=0,2,-0.5` with `BodyLeanMax=35` (test 56's placement).
28. **The look key** (test 56: a second arm hung in view while Z turned your head): hold Z and look to the side and
    behind slowly, then back: no second arm or hand at any angle. Then with a pistol drawn, look with Z too (the arms
    holding the pistol may show at the side: say if that looks wrong).
    - `body: looking aside 31 deg off your heading (more than BodyArmsLook 30): the first-person 3D hidden (...)`, and
      `body: the first-person 3D given back (looking ahead again: ...)` when it comes back: one pair a look, not nine
      (test 56: nine in six seconds).
    - A/B: `[View] BodyArmsLook=0` (hidden only past 90, as in test 56).
29. **Backing over the shoulder**: back up until the view looks over your shoulder: your body isn't shown there, as in
    test 56 (the seat looks empty). Try `[View] BodyBack=0` once: your body stays while you look back. Better, or do you
    see the inside of your neck and shoulders? Does the body flicker when the look hovers near the edge?

**The A/Bs** (step 30)

30. Any of this build's A/Bs you haven't tried yet, one at a time, a ride or two each (README's table of this build's
    keys): `[View] CameraEase=0`, `NearHandover=0`, `BodyNodes=1`, `BodyEye=0,2,-0.5` with `BodyLeanMax=35`,
    `BodyArmsLook=0`, `BodyBack=0`; `[Tilt] GunCheckUnpaused=0`, `GunCheckRecover=0`, `DrawHandgunOnly=0`,
    `QuickHolsterFirst=0`, `GunJudgeWait=0`, `NodelessOnce=0`, `SkinArraysCheck=0`; `[Look] KitHold=0`,
    `KitSlotView=0`, `KitRoom=0`; `[Steer] LaunchFrom=0.1`; `[Sound] DownBands=` with `HeardStop=300 HeardBrake=600`,
    `DownBlend=0`, `StopAfter=0.15`. `[Diag] BodyWornLine=0` and `HeldWhere=0` change only log lines. Anything better
    or worse?

Send `CMB_Slope.log` and its `_prev` logs and `Papyrus.0.log` of each session, any crash log, the screenshots of steps
1-8 (each plate and badge close and riding), 10 and 27, and a short video of steps 16-19, 22 and 25 if you can.

### Questions for you (test 57)

- **T57-1 (step 1).** The Brotherhood of Steel plate's emblem: as the Brotherhood's, close and from riding distance?
- **T57-2 (step 2).** The Minutemen plate's musket, bolt and stars: as the flag's, from riding distance too?
- **T57-3 (step 3).** The Nuka-Cola cap and its script: right? Faint from riding distance? "ZAP THAT THIRST!" on top?
- **T57-4 (step 4).** The Red Rocket plate as the round sign? Another background? The yellow line round the rim?
- **T57-5 (step 5).** The Enclave helmet on chrome: clear by day and at night? The chrome too bright or too plain?
- **T57-6 (step 6).** The Gunners skull on its green patch: as your picture? Anything cut off, on the fender too?
- **T57-7 (step 7).** The Brotherhood of Steel badge in colour, no red: right, from riding distance too?
- **T57-8 (step 8).** Saddle tan: no longer too yellow? Still apart from Tobacco brown, Red and Cream?
- **T57-9 (step 9).** The kit's bike turned about its middle by the drag, never tipping? The wheel's zoom above the
  lists? What did the close line's "the mouse's buttons" and "E event(s)" say?
- **T57-10 (step 10).** A view per slot, gliding? Which views would you change? What did the `kit: slot:` line say?
- **T57-11 (step 11).** Along a wall, with the armour bench: not moved into it, the bench where you stand? In the open as
  before?
- **T57-12 (step 12).** The take-off: right now, still slow, or too quick? 2nd at about 12 on the dial?
- **T57-13 (step 13).** Coasting to a stop: four one-gear down-shifts, one blip each, natural? Late (`StopAfter=0.15`)?
  From 30 and 20 on the dial?
- **T57-14 (step 14).** A hard brake: one or two shifts then the idle: natural, or should it step down further?
- **T57-15 (step 15).** A short lift: no down-shift? A longer one: the gear or two lower a bother? `DownBlend=0`?
- **T57-16 (step 16).** A pistol drawn right after getting on: seated, both hands on the bars, the gun in hand, no bike
  swap? Where did the shots and the muzzle flash come from? What did the GunCarry line say?
- **T57-17 (step 17).** After the Pip-Boy, the pause menu and a quicksave: the seated pose every time? Any "weapon
  rules here off" line, and then "back on"? A jerk at a draw? The GunRootFrame line?
- **T57-18 (step 18).** A rifle by its key never drawn, the message shown, R doing nothing while riding?
- **T57-19 (step 19).** A rifle's key with the pistol out: the pistol away, the rifle holstered, the right rifle?
- **T57-20 (step 20).** A quick swap between handguns: each drawn, none put away?
- **T57-21 (step 21).** Getting on with a rifle out? The Pip-Boy's and the favourites menu's rifle put away after?
  What did the ride's "the game asked N draw(s) through slot 0xC9" lines say?
- **T57-22 (step 22).** Any spikes from the hands, third person to first or first person only? Which "rider:" line came?
- **T57-23 (step 23).** First person: still shaking? The body more than the bike? What did the "eased toward" line say
  (its time constant), and no "EyeAtCamera off"? The lock line's CameraEase part against the Lead's?
- **T57-24 (step 24).** Into first person by the key and by the wheel: no jump or lag?
- **T57-25 (step 25).** Zoomed in across cells: the bars and the dial there at every handover?
- **T57-26 (step 26).** The bike under you in third person after your body showed, every time? One bike in first
  person? What did the "worn bike as the showing ends" lines say?
- **T57-27 (step 27).** Looking down: your body from outside, no hole? Sitting right?
- **T57-28 (step 28).** The look key: no second arm at any angle, with and without a pistol?
- **T57-29 (step 29).** Backing over the shoulder: `BodyBack=0` better or worse? A flicker at the edge?
- **T57-30 (step 30).** Anything a 2026-11-17a A/B made better or worse?

## Test 56: the 2026-11-16b build (test 55's fixes) and the 2026-11-16a build's art

The 2026-11-16b build answers test 55 (run on 2026-11-15b) on top of the 2026-11-16a build, the art build, which you
haven't tried yet: this package holds both, and test 56 covers both in this section: steps 1-14 the art (2026-11-16a's,
as written for it), steps 15-37 the fixes, with the questions T56-1 to T56-37 at the end. What test 55 liked is as it
was.

- **The fixes (2026-11-16b):** the first-person shake (the camera's place now found the way your game makes it), the
  half second with no bike when you zoom in with the wheel, the first-person bike's moves between cells (a candidate for
  the stutter), the view's lean by how fast you turn, the mouse tilting the view while you look back, A and D at 0.45
  (your pick); with your body in first person no second set of bars and speedometer, no gun on the right grip, no
  outfit piece in front of your eye, no first-person arms hanging in view when looking back, and the body sitting where
  the game's eye is; the game's own put-away called on you and a save right after it not counted; a handgun drawn seated
  with both hands on the bars and the gun in your right hand, also right after getting on; the field kit's preview
  placed by the plugin; a short 1st and an even climb, the engine's gears sounding as before at the speeds that match.
- **The art (2026-11-16a):** two 3D helmet badges (an Enclave and a Brotherhood helmet, each a cast emblem standing on an
  enamel plate on the tank, centred on it and angled with it), the Gunners skull on the tank and the rear fender, every
  licence plate's emblem redrawn to read at riding distance with a new die-pressed plate font, the seat's colour (a
  twelfth slot), and the MCM's and the kit's lists in alphabetical order.

The two halves don't depend on each other: do them in any order, but do steps 15-16 (the camera) before your body's
steps 21-24. Do this section's steps in one game session if you can, and say which session each step was in. Every new
behaviour of 2026-11-16b has a key whose off value gives the 2026-11-16a build back (README's table of this build's
keys), so each A/B is one key away; the art's A/Bs are files (step 9's), and every new look choice is opt-in. Things
only the game can settle: which reading of the camera's place fits your game (step 15), whether a cell move costs a
frame (step 17), whether your 3D is updated before the camera (step 24's lock-line part), where the game hangs a drawn pistol (step 25), how the armour menu maps the preview's record (step 30),
the armour menu's order (step 1) and whether MCM reads the dropdowns through the controller's properties (step 2).

Before you start:
- install as a Replace over 2026-11-15b (this package holds 2026-11-16a too). If you edited `CMB_Slope.ini`, put your
  values into the new one: `[Tilt]`, `[Steer]`, `[Look]`, `[View]`, `[Sound]` and `[Diag]` have new keys, and `[Steer]
  FirstKeys`, `PullTime`, `PullFrom`, `LaunchFrom`, `[View] BodyEye` and the commented `[Look] KitPreviewPos` and
  `KitPreviewTurn` new defaults (README's table). Otherwise use the shipped file as it is;
- load your usual save. The MCM's Look section should have 22 controls, with "Seat" after "Tyres". If it has 21 or no
  "Seat", an older ESP or MCM folder is loaded: stop and say so. Riding's "Weapons while riding" on "Handguns only";
- the first time you get on after the update the look's mods go on afresh once (the look's key has the seat now):
  `Papyrus.0.log` says so; a second getting on is as quick as before;
- note your frame rate at a fixed spot on 2026-11-15b before you install, if you can (step 14);
- each A/B below: change one key in `CMB_Slope.ini`, save the file, get off and on (no restart), and put it back after.

The log's first lines: `CMB_Slope.log` has seven settings lines more: `  view (2026-11-16b, test 55): CameraPlace=1 (...)
NearThird=60 NearFade=0.99 (...) ParentKeep=1 ParentMargin=256 (...) RollTurn=40 (...) LookPitch=45 (...); [Diag]
ParentTime=1`, `  view (2026-11-16b, test 55): BodyWorn=1 (...) BodyWeapon=1 (...) BodyWeaponNodes=WEAPON BodyNear=20
(...) BodyArmsBack=90 (...); [Diag] BodyDrawn=1`, `  view (2026-11-16b, the review): BodyFollowCamera=1 (...)`, `
weapons (2026-11-16b, test 55): PutAwayProbe=1 PutAwayUnpaused=1
GunRootFrame=1 GunBothBars=1 GunCarry=1 GunStillRide=1 GunPredictMax=15 (...)`, `  kit (2026-11-16b): [Look] KitFind=1
(...) KitFit=1 (...) KitFitView=40 KitFitBox=0.07,0.5`, `  steer (2026-11-16b, test 55): from rest the throttle climbs
evenly from its floor (0.1), 0.112 of the top a second, the top 8.0 s after the press (...); PullClimb=1: ...` and `
sound (2026-11-16b, test 55): SpeedMap=225:480,430:700,680:910,935:935: the bike's speed goes into the engine through
these points (...)`; the older lines now say `FirstKeys=0.45` and `BodyEye=(0, 2, -0.5)`. No 2026-11-16b lines, or
`CameraPlace=0 (... as 2026-11-16a)` and `SpeedMap=: the engine hears the bike's own speed` with an INI you didn't
change, mean an older `CMB_Slope.dll` or `CMB_Slope.ini` is loaded: stop and say so.

### The art (2026-11-16a): steps 1-14

**The lists** (steps 1-2; two probes: whether the armour menu orders a slot's choices by the recipes' priority, and
whether MCM reads and sets a dropdown through the controller's properties)

1. **The kit's order**: at the field kit open "Tank L" and look at the order of the choices. Is it alphabetical after
   Stock and None (Atom Cats, Brotherhood helmet, Brotherhood helmet (3D), Brotherhood of Steel, Children of Atom,
   Enclave, ...), alphabetical from the bottom up, or the old order (Stock, None, Brotherhood of Steel, Brotherhood
   helmet, Enclave, Enclave helmet, Gunners, ...)? The same for "Seat" and "Paint". A screenshot of each helps. Nothing
   else changes at the kit: the names are "Tank L: ...", "Seat: ...".
2. **The MCM's dropdowns**: open the MCM's Look page. Every dropdown (both tank badges, the fender, Paint, Rims, Seat,
   the plate's four, Faction set) should list its choices alphabetically after the pinned ones (the bike as it came,
   None, "Same as the left" third on the right tank, "The plate's own"), Paint's "Palette test: colour index" last;
   Mirrors and Tyres stay steppers. Each should show the choice you had before the update.
   - `Papyrus.0.log`, once a session on opening the page: `Look: the MCM reads its dropdowns through the controller's
     properties (the tank right's: TankR:sameleft (17) at rank 2)` (or another slot's).
   - Choose "Seat: Saddle tan" and "Tank badge, right: Brotherhood helmet (3D)": one line each, `Look: the MCM's seat
     dropdown (its property): rank 12 = Seat:tan (3)`. Press "Apply the look": the parked bike shows them by name. Close
     and reopen the MCM: the dropdowns still show them.
   - Then at the field kit choose another seat, leave the kit and reopen the MCM: the Seat dropdown shows the kit's
     choice.
   - If the first line never comes, a dropdown always shows its first choice, or a choice does nothing at Apply, the
     property route doesn't work on your MCM: say so (the next build binds the dropdowns to globals of their own; the
     scripts are ready for it). The kit still works either way.

**The 3D helmets and the skull** (steps 3-8)

3. **Fit them**: at the kit choose "Tank L: Enclave helmet (3D)" and "Tank R: Brotherhood helmet (3D)" (Steel 2, Screws
   1, Adhesive 1 each). The tank's badge plates become plain enamel plates with the stock badge's chrome edge (black on
   the left, steel grey on the right), each with its helmet standing on it. Look in the kit's preview, at the parked bike
   close up, ridden in third person from the side and behind, and in first person looking down. Each helmet should sit
   inside its enamel plate, none of it over the chrome edge or the paint, and read as a raised cast emblem, not a
   sticker (try a low sun across it). Screenshots of each, please. Then the same with the Brotherhood helmet on the left
   and the Enclave on the right.
4. **The Enclave's eyes at night**: after dark, look at the Enclave helmet, parked and ridden, the headlamp on and off:
   the eyes glow amber. Too bright, too dim, or plastic-looking? And in daylight: does the Enclave's dark gunmetal and
   the Brotherhood's steel look like metal?
5. **Your knees**: with both 3D helmets on, ride and lean hard both ways at speed, sprint-lean if your load order has
   it, then stop with the left foot down and look from the side and the front in third person: no knee or leg should
   pass through a helmet. Note the side and the moment if one does.
6. **The bars**: fit the under-bar mirrors (egg, then D), and with the helmets on turn the bars to full lock both ways
   at a crawl, in first person and from the side: no mirror passes through a helmet.
7. **"Same as the left"**: set the right tank badge to "Same as the left" with a 3D left: both plates show the same
   helmet (`Papyrus.0.log`: `Customise: the right tank badge follows the left: TankL:enclavehelm3d`). Then a 3D left with
   a flat right (Tank R: Enclave helmet, the flat one): the right shows the flat badge and no 3D helmet. Then put both
   back to Stock: no helmet is left on any of the three bikes (parked, ridden, first person), after a ride and after a
   save and a load.
8. **The Gunners skull**: choose "Gunners skull" on the left, the right (or "Same as the left") and the rear fender
   (Adhesive 1, Cloth 1): a pale skull with a black cross on the brow and a stitched mouth, no plate round it, on any
   paint you like.

**The plates** (step 9)

9. **Each design at riding distance**: choose each plate design in turn at the kit (with its own text, and with a text of
   your own), then ride away and look back at it from the riding camera, about a bike's length behind and more. The
   letters should look pressed into the plate, narrow and square, and read clearly; the small emblem in the top-left
   corner should keep its shape and not run into the stripe, the legend or the edge. Which designs or characters are
   hard to read? (B, 8, 6 and 9 have the smallest holes.) Optional A/B: the 2026-11-15b package's six plate textures
   (`Data\Textures\CMB\Bike\plates_d.dds`, `plates_n.dds`, `plates_s.dds`, `plate_text_d.dds`, `plate_text_n.dds`,
   `plate_text_s.dds`) in a small MO2 mod of their own, ticked below this one, give the old letters and emblems back.

**The seat** (steps 10-13)

10. **Each colour**: at the kit choose each "Seat: ..." in turn (Cloth 2, Adhesive 1; the stock one free). Look at it
    parked, ridden in third person and in first person looking down. The colour should match its name, and the
    leather's grain, shading and slightly lighter worn edges should still show. `Papyrus.0.log`: `Customise: seat =
    Seat:tan (3)`, and the look's colour lines end `seat 0.15625` (the colour's row; `seat -1` for Dark brown, as it
    came).
11. **The dark seats in the game's light** (a probe: the renders' light isn't the game's): Black, Oxblood, Tobacco brown,
    Navy and Dark brown (as it came), in daylight, in shade and at night, close and from a few steps away. Which look
    alike? Black should look clearly darker than the original dark brown and still look like leather (a soft sheen, not
    matte cloth). Pre-war turquoise is the light turquoise of 1950s two-tone upholstery: does it fit?
12. **The piped seats**: on Black with red piping, Black with cream piping, Dark brown with cream piping and Oxblood with
    black piping the welt along the seat's edge should show clearly in the second colour, close up (from riding
    distance a piped seat looks like its plain colour: expected).
13. **With the rest of the look**: Paint "Free colour" with a coloured seat, then move the hue: the seat doesn't change
    colour and the paint doesn't take the seat's. While riding, change the seat in the MCM and press "Apply the look":
    the first-person bike shows it at once, the ridden bike at the next getting on. Load a save from before the update:
    the seat is "as it came", everything else as it was. Last, Seat back to "Dark brown (as it came)": exactly the seat
    of before the update.

**The cost** (step 14; a probe: every bike carries the four helmets hidden, about 14,000 triangles)

14. **Frame time beside the parked bike**: stand 3-4 m from the parked bike at a fixed spot you can find again (for
    example by the bike's side in Sanctuary, facing it), still for 20 s, and note your frame rate with your usual frame
    counter: first on 2026-11-15b (test 55's install, before you install this package), then on this build at the same
    spot, with the stock look and with both 3D helmets on. Any drop? If you only have this build, the stock look and both
    helmets at the same spot.

The art has no INI switch: every new choice is opt-in (each slot starts as it came), and the old order of the lists and
the old plates are A/B files, not keys (README's table of the 2026-11-16a build's switches). Send the screenshots of
steps 1 and 3, and any of steps 5, 9 and 11 that show a problem.

### Test 55's fixes (2026-11-16b): steps 15-37

**First person: the camera and the view** (steps 15-20; test 55: the shake back, its camera check off at the first
frame; about half a second with no bike when zooming in; a stutter; "didn't see any difference" with the lean's slider;
the mouse's vertical doing nothing while looking back; A and D)

15. **The shake**: in first person ride two or three minutes: straight at full speed, over rough ground, through turns,
    and standing still. Does the bike still shake against your view? (The plugin now finds the camera's place each
    frame the way your game makes it: your own place plus the game's answer.)
    - `CMB_Slope.log`, once, at the first riding frame in first person: `camera: the camera root at GetTranslation's
      answer read as the player's place + the answer (call 1 of 3 since the task; 0.00 from it; the player's place + it
      0.00, ...) ([View] CameraPlace): the view bike follows the camera's own place at that call` (another reading or
      call is fine: send the line), then the first check's line ending `; [View] CameraPlace: the player's place + the
      answer 0.00, ...`.
    - Good: no `camera: EyeAtCamera off this session` line; the `view: lock:` lines say `EyeAtCamera` without "off",
      `the camera root 0.00 at most from that place at the next task`, and end `; CameraPlace: the player's place + the
      answer at call 1, 0 switch(es)` (a few switches are fine). Their "the Lead's guess off it by" figures stay: they are
      the task's guess, which the plugin now corrects at the camera's own update.
    - Bad: the off line (it now gives every reading's distance) or many switches: send the log.
    - A/B: `[View] CameraPlace=0` (2026-11-16a's reading: the check turns itself off as in test 55).
16. **Zooming in with the wheel**: on the bike in third person zoom into first person with the mouse wheel, slowly, a
    few times, and back out, stopped and riding. One bike all the way in: no moment with no bike, and never two (two
    sets of bars or two speedometers)?
    - `view: third person with the camera 35 from your eye (the player's fade 0.40): the view bike ... shown at its own
      place, the worn bike hidden ([View] NearThird 60, NearFade 0.99)`, then `view: the view bike near the camera in
      third person over after 0.45 s (first person)`, and no `third person: the view bike hidden` line in between. On
      getting off: `view: the view bike stood in for the worn bike near the camera in third person N time(s) this ride,
      ... s in all`. While it stands in, the worn bike is shrunk away as it is with your body (`[View] BodyWorn`).
    - A/B: `[View] NearThird=0` (2026-11-16a: no bike for about half a second).
17. **Across cells**: ride in first person across a few cells (a long straight run of a minute or two) and note any
    stutter or hitch, as in test 55. Then the same run with `[View] ParentKeep=0` (the old moves): which stutters more?
    - Far fewer `view: Parent:` lines than test 55's 196: `view: Parent: the view bike left under its own cell while its
      sphere is 9xx inside that cell's box (...)` once a ride, `view: Parent: the view bike's 3D moved straight from the
      player's last cell ... to the player's cell ...`, and hardly any `put back under its own cell (the player's cell is
      another now)`.
    - On getting off: `view: Parent: this ride N move(s) (K straight from cell to cell), P put back, ...; the calls X us
      (median) / Y (most); first person: H frame(s) over 25 ms within 0.6 s after a move or put-back (in T s), G
      elsewhere (in U s) ([Diag] ParentTime; ...)`. Send it from both runs: H in T seconds against G in U says whether a
      move costs a frame.
18. **The view's lean**: try the MCM's Riding "View leans in turns (first person, deg)" at 2, 5 and 10 in ordinary turns
    at speed. The number is now the lean in degrees in an ordinary turn at speed (40 degrees a second of turning), more
    in a sharp one (up to one and a half times), less in a gentle one, none slow or backing: 10 should lean clearly more
    than 2. Which do you like? The eye lines' `leaned N deg (the bike's lean M)` now vary with the turn. A/B: `[View]
    RollTurn=0` (test 55's lean, by the bike's lean: 0 or the whole slider).
19. **Looking back**: back up in first person until the view turns over your shoulder, then move the mouse up and down:
    the view tilts up and down (45 degrees at most) and comes back level with the front when you ride forward again.
    While you look back (and holding Z, looking far round) the game's first-person arms that hung in view in test 55
    should be gone, back when you look ahead. Then, still looking back, open VATS, and another time get off: afterwards,
    in first person on the bike or on foot, your first-person arms and weapon must be there.
    - At the look's end: `view: the look back's pitch: the mouse moved it N deg at most over T s, ... (the game moved the
      player's pitch: ... | the game held the player's pitch: ...)`; the eye line while looking back ends `, pitched N
      deg up by the look's own (LookPitch)`.
    - `body: looking back 150 deg off your heading (more than BodyArmsBack 90): the first-person 3D hidden (bit 0 on
      PlayerCharacter+0xB78's BSFadeNode 'skeleton.nif')`, and ahead again `body: the first-person 3D given back (looking
      ahead again: the look 12 deg off your heading; ...)`. Through VATS or getting off: `body: the first-person 3D kept
      hidden in another camera (...): bit 0 cleared at the next first-person frame, ...`, and later `body: the first-person
      3D given back (...; bit 0 cleared ...)`.
    - A/Bs: `[View] LookPitch=0` (the game's own pitch), `[View] BodyArmsBack=0` (the arms left to the game).
20. **A and D**: in first person A and D now turn the bike at 0.45 of the turning limit (your pick after test 55). Is it
    right? `steer: first person: the side keys turn the bike (FirstKeys 0.45 of the clamp, N deg/s now): the game gets
    no strafe`, once a ride. A/B: `[Steer] FirstKeys=1` (2026-11-16a's).

**Your body in first person** (steps 21-24; test 55: a second set of bars and a speedometer riding ahead of the first,
a gun on the right grip, a rusty piece of your outfit in front of your eye, the body shown in only some rides)

21. **One bike**: ride a few seconds in third person, straight, at speed (the plugin takes your riding pose then), then
    switch to first person and keep riding fast. Look at the bars and the speedometer: only ONE set of bars and ONE
    speedometer now? Stop and ride off again: still one? Screenshots.
    - At each showing, after `body: first person: the rider's body shown (...)`: `body: hidden with the body: the worn
      bike's 54 shape(s) shrunk to a speck, 1 node(s) of it hidden (bit 0: '...'); the weapon's N shape(s) shrunk, ...;
      near the eye N shape(s) shrunk whole (...: <their names>); the pose: HEAD (x, y, z), the spine's joint (x, y, z) in
      the bike's space, the eye BodyEye (0, 2, -0.5) from HEAD, the pitch wanted W deg (BodyLeanMax 35)`. 0.5 s in and
      every 10 s: `body: shown 0.5 s: ... held hidden with it: ...` (there is no "drawn?" verdict any more: the numbers in
      it don't tell whether the game draws your body). A large "set again by us" count says the game un-hides those nodes
      every frame (the speck still hides the shapes).
    - A/B: `[View] BodyWorn=0` (2026-11-16a: the second bike again).
22. **No gun on the grip**: with a pistol (or any weapon) holstered, look at the right grip in first person: no gun
    lying on it? Pick another weapon from the quick menu (holstered) and look again. The "hidden with the body" line
    counts the weapon's shapes (0 when nothing hangs in the hand). A/B: `[View] BodyWeapon=0` (the gun on the grip). If
    you use a holster mod and its gun shows, its node can be added: `BodyWeaponNodes=WEAPON,<its node>`.
23. **Nothing in front of your eye**: look down in first person: your hands on the grips, your sleeves and the Pip-Boy
    as in test 55, and the rusty piece of your outfit (the cage) in front of your eye gone. Anything else of your outfit
    in front of your eye? And the other way: is anything gone that you want to see? A chest piece, a backpack, a collar
    or a scarf with no sleeve in it near your neck is shrunk away whole (the plugin judges by the outfit's coarse
    bounds), so a sleeveless top or vest may vanish from your view too. Say what you wear and what you miss, with a
    screenshot; the "hidden with the body" line names the pieces. A/Bs: `[View] BodyNear=10` (only what is nearer your
    eye), `BodyNear=0` (the head alone, 2026-11-16a).
24. **When and where it sits**: does the body show more often than in test 55, in the first ride too (it should, unless
    you look back, have the Pip-Boy open or a weapon out)? Does it sit right: hands on the grips, not sunk into the seat,
    not leaning back oddly? Over bumps and through any hitch, do the hands stay on the grips, or run ahead of them or
    lag behind for a frame? (Your body now follows the camera's own place with the bike, `[View] BodyFollowCamera`.)
    - The `view: lock:` lines end `; BodyFollowCamera: N move(s) of your body X (median) / Y (most), its skeleton's own
      since the task A of the camera's B (medians)`: send them. A about B: the game's skeleton carries your body and the
      key does little; A about 0 while riding: the key does the work, and if then the hands run ahead of the grips, the
      game updates your 3D after the camera (say so). A/B: `[View] BodyFollowCamera=0` (your body placed once a frame,
      2026-11-16a).
    - "the pitch wanted" in the "hidden with the body" line under 35 now (35 every time in test 55), the "body moved
      (...)" in the shown line small (test 55: 6-10 down, now about 1-5), and `not shown: the head's eye X from EyeAt`
      lines rare (27 in test 55).
    - A/B: `[View] BodyEye=0,7,7` (where the body sat in test 55).

**Handguns on the bike** (steps 25-29; test 55: the right arm swinging out of the seated body, the pistol never in the
posed hand, the standing pose when drawn right after getting on, the put-away never calling the game, a save right
after the ask ending the ride). The MCM's "Weapons while riding" on "Handguns only".

25. **Drawn right after getting on**: get on with a 10mm pistol equipped and ride off at once; within two seconds draw it
    (R) in third person while riding. You should be seated, both hands on the bars, the pistol in your right hand on the
    grip, and the bike shouldn't vanish and come back. Ride a while with it out, turn both ways, stop, ride off again.
    Aim and fire a few shots: where do the shots and the muzzle flash come from, the gun in your hand or beside you? A
    short video helps.
    - `gun: a handgun out at N u/s with no riding seat pose yet: the still one (read N s ago) stands in until one is read
      (GunStillRide)`; no `... (ride a second or two holstered first) ...` and no `tilt: CMB_BikeWornRiderF_* back level
      and let go (no longer worn ...)` at that draw (the bike not swapped).
    - `gun: a handgun out (the weapon state 2, ...) at N u/s: the rider on the riding seat pose read N s ago, both hands
      on the bars (GunBothBars) (GunPose)`, then once a draw `gun: the drawn weapon's 3D (the biped's object 41, '<name>'
      ...) hangs off '<parent>' ...: carried from the game's right hand to the posed one (GunCarry)` (or `gun: no drawn
      weapon's 3D at the biped's object 41 ...` or `... has shapes held on the rider ...`): send it either way, it says
      where your game hangs the drawn gun.
26. **Drawing and putting away**: put it away (R) and draw it again a few times, stopped and riding: any jerk at the
    moment of drawing or putting away (one frame is expected), anything flying off?
    - Every 10 s posed and at the end: `gun: posed N s ...: the bones' own move a game frame at most X relative to the
      root the bones were animated with (Y against the task's root, GunRootFrame), ...; the drawn weapon carried N
      frame(s) (GunCarry)`: X a few units at speed, Y like test 55's 10-30. Once a session: `gun: the bones moved A a frame
      on average against the root they were animated with and B against the task's own (...): the root a frame ahead of
      the bones, as GunRootFrame takes it (GunRootFrame)`. If it says `... the game's update isn't in the order
      GunRootFrame takes: the task's root for the session ...` instead, say so.
    - A/Bs: `[Tilt] GunBothBars=0` (the game's right arm carried to the seat's shoulder, 2026-11-16a), `GunCarry=0` (the
      gun where the game's clip holds it), `GunRootFrame=0`, `GunPredictMax=0`, `GunStillRide=0`.
27. **A rifle by its key**: with the pistol out press a rifle's favourites key: "Only a handgun can be used on the
    motorbike.", the rifle away at once (under a second), no sheathe pause, and you stay on.
    - Once a session: `gun: the player's slot 0xC7 (+0xD62DA0) is PlayerCharacter's heading: it calls the heading's
      getter (+0xC5A8D0) first; 0xC8 the ret-0 stub (+0xC5CF40): slot 0xC9 (+0xDA13D0) taken as DrawWeaponMagicHands
      (PutAway, PutAwayProbe)`; then `gun: put away asked (CMB_WeaponAway N): DrawWeaponMagicHands(false) called, the
      weapon state 3` and `gun: the weapon state 3 > 4 > 5 > 0: away 0.xx s after the ask (CMB_WeaponAway N, 1 call)`;
      `Papyrus.0.log`: `Weapons: put away after 0.x s (the plugin's put-away, or the game's own).`
    - Bad: `... not the layout expected, nothing called (PutAway): ... (PutAwayProbe: its call's target ... reads ...;
      0xC8 ...)`: send it.
28. **A save right after**: press the rifle key and save at once (quicksave or the menu). After the save you should
    still be on the bike, the rifle away. `Papyrus.0.log`: `Weapons: still out 1.0 s after the ask; 4.3 s more with the
    game paused, not counted: the sheathe action played (True).` or `Weapons: put away after ... (...; N s more with the
    game paused, not counted).`, and no `the ride ended`. A/Bs: `[Tilt] PutAwayProbe=0` (nothing called on you: the
    sheathe after 1 s), `PutAwayUnpaused=0` (real time: a save right after the ask can end the ride again).
29. **Getting on with a rifle out, and the rifle's swap**: get on with a rifle out: it is put away first, quickly, and
    you get on. Then, riding with nothing drawn, draw a rifle by its key, let it be put away and draw the pistol within a
    few seconds: seated at once, or the standing pose first (`gun: a handgun out ... with no riding seat pose yet ...`)?
    A rifle drawn still swaps the bike under you for the planted one for 2-4 s, as in test 55, and the seat poses are
    read again after it. In first person, does a hitch come with that swap? Then first person with the pistol out: as
    before (the game's own arms).

**The field kit's preview** (steps 30-32; test 55: "half of the bike was in view", too high, too close, side-on)

30. **The whole bike**: in a settlement, at the parked bike choose Customise and pick the Motorbike: a screenshot as soon
    as it shows and another while browsing a slot's mods. Expected: the whole bike in the upper half of the screen, in
    the middle, turned three-quarters with its front towards you on the left, seen a little from above, the menu's list
    below it (the plugin now places it in the menu's view itself).
    - Within a second of the bike showing, at each Customise: `kit: fit (2026-11-16b): the menu's bike (item XXXXXXXX)
      moved from (mx, my, mz) to (~0.8, ~701, ~10) (N object(s)): ...; the bike 0.07 to 0.50 of the screen's height, 0.35
      to 0.65 across, in a view 40.00 deg across ...` ("moved from" is where the menu put the new record: it settles how
      the menu maps it); at the close `kit: fit: the menu's bike (item ...): the menu closed after N frame(s): our place
      kept K, written again A (the menu's own place back), the menu's small moves of it kept T`. The `kit: the menu's 3D`,
      scene and camera lines now come at the menu's opening too.
    - Bad: `kit: fit: ... not moved (...)`: send the log.
31. **Zoom and turn**: roll the mouse wheel out and in and drag the bike round with the mouse: it zooms and turns as
    before? A screenshot. Pick a plate colour (as in test 55) and leave the menu: the colours on the parked bike when the
    menu closes (KitDefer, as before).
32. **Only if the bike is still cut or badly placed**: first, is it the same as test 55 (the top half off)? Then the
    plugin's placing didn't show: say so and send the log. To size it in New: `[Look] KitFitBox` (0.07,0.50: the bike's
    top and bottom on the screen, as fractions of its height from the top; 0.12,0.45 makes it smaller; get off and on the
    bike to read it again). To tune by hand: "Field kit preview" "Tune (the sliders below)": "Preview distance" bigger =
    smaller bike (start at 1050; 1300 if still too big), "Preview up / down" more negative = lower (start at -45, steps of
    25), "Preview tilt" 0 if it looks tipped oddly; leave the MCM, Customise again, and say which values looked right.
    Your save shows 400, 0, 0 from before: set 1050, -2 and -45 first. A/Bs: `[Look] KitFit=0` (the menu places it from
    the new record alone), "Field kit preview" As before and back to New.

**The pull and the gears** (steps 33-36; test 55: "1st gear shoots bike up to 30 almost instantly, then next 20 is
divided for 4 gears - 1st should be short, up to 10, then gradually change")

33. **A full pull**: from a stop on a long flat road hold forward to the top speed, watching the speedometer and
    listening. The engine should sound as in test 55 (the same five gears, the same lengths); the needle: 1st up to about
    10-12, then an even climb, 2nd to about 24, 3rd to about 42, 4th to about 50, the top about when 5th comes in (about
    8 s). Does the speed match the gears now? Is the take-off too slow (0.3 of the top after about 2 s now; 0.4 s in
    test 55), the climb too slow or too quick?
    - `sound: gear 2 at ~220 u/s, ~3250 rpm, heard ~404 u/s; the engine's speed ~470 (SpeedMap)` (test 55: 568 u/s),
      `gear 3 at ~430 ...`, `gear 4 at ~750 ...`, `gear 5 at ~900 ...`, about 1.4, 3.4, 6.4 and 7.9 s after the press as
      before; `launch: from rest: 0.3 of the top after ~1.9 s, half after ~3.7 s, 0.9 after ~7.1 s, the top (0.97) after
      ~7.7 s (...); ...; above 0.1 of the top at most 0.112 a second (PullTime)` (test 55: 0.42 / 0.82 / 4.8 / 5.7 s).
34. **Steady speeds**: ride steadily at about 10, 20, 30, 40 and 50 on the dial for a few seconds each: does the gear you
    hear sound right for the speed, and does it ever hop between two gears? The top of the sound is squeezed to keep the
    pull's sound: from about 38 to 52 on the dial the engine sounds about the same (5th, about 2,000 rpm), and in a full
    pull 4th settles while the needle still climbs from about 42 to 50. Does that bother you?
35. **Picking up again**: pull away from about half speed after a turn, and tap off the throttle for a moment at speed:
    the note shouldn't drop or blip. Sluggish? At low speed the throttle climbs at the pull's rate too (0.1 to 0.3 of the
    top in about 1.8 s; 0.6 s in test 55).
36. **A log or a kerb**: ride slowly into a fallen log or a kerb and keep forward held: it climbs as before (`[Steer]
    PullClimb`: the push at a low thing builds as quickly as in test 55)?
    - A/Bs, a ride each: `[Steer] PullTime=7` (quicker: 1st to about 13, the top as 4th comes in), `PullTime=9` (slower:
      1st to about 11, the top in 5th); `[Sound] SpeedMap=` (the engine hears the bike's own speed: 1st waits for the
      bike and 2nd and 3rd go flat, which is why the map is there); 2026-11-16a's pull and sound, `[Steer] PullTime=5.5`,
      `PullFrom=0.6`, `LaunchFrom=0.25` with `[Sound] SpeedMap=`; test 55's A/B, `PullFrom=0.2`, `PullTime=9`,
      `LaunchFrom=0.25` with `SpeedMap=` (1st to about 19 on the dial, 2nd and 3rd flat); `[Steer] PullClimb=0` at a log.

**The A/Bs** (step 37)

37. Any of this build's A/Bs you haven't tried yet, one at a time, a ride or two each (README's table of this build's
    keys): `[View] CameraPlace=0`, `NearThird=0`, `ParentKeep=0`, `RollTurn=0`, `LookPitch=0`, `BodyWorn=0`,
    `BodyWeapon=0`, `BodyNear=0`, `BodyArmsBack=0`, `BodyEye=0,7,7`, `BodyFollowCamera=0`; `[Steer] FirstKeys=1`; `[Tilt] PutAwayProbe=0`,
    `PutAwayUnpaused=0`, `GunRootFrame=0`, `GunBothBars=0`, `GunCarry=0`, `GunStillRide=0`, `GunPredictMax=0`; `[Look]
    KitFind=0`, `KitFit=0`; the pull's (step 36). `[Diag] ParentTime=0` and `BodyDrawn=0` change only log lines. Anything
    better or worse?

Send `CMB_Slope.log` and its `_prev` logs and `Papyrus.0.log` of each session, any crash log, the screenshots of steps
21, 23 and 30, and a short video of steps 25-28 if you can.

### Questions for you (test 56)

- **T56-1 (step 1).** The kit's lists: alphabetical from the top, from the bottom, or the old order?
- **T56-2 (step 2).** The MCM's dropdowns alphabetical? Did the "reads its dropdowns through the controller's
  properties" line come, and did a choice there apply as named and stay shown after the kit?
- **T56-3 (step 3).** The 3D helmets: inside their plates, none over the chrome edge? Raised and cast-looking, or flat?
  In the preview, parked, ridden and in first person? Their size and place on the plate right?
- **T56-4 (step 4).** The Enclave's eyes at night: amber, too bright or too dim, plastic? The metals in daylight?
- **T56-5 (step 5).** Any knee or leg through a helmet, leaning or with a foot down? Which side, when?
- **T56-6 (step 6).** The under-bar mirrors at full lock: clear of the helmets?
- **T56-7 (step 7).** "Same as the left" with a 3D left, a 3D left with a flat right, back to Stock: anything left over
  on any bike, after a ride and a load?
- **T56-8 (step 8).** The Gunners skull on the tank and the fender: how does it look?
- **T56-9 (step 9).** The plates at riding distance: the new letters and emblems legible? Which designs or characters
  aren't? Better or worse than the old ones (the A/B, if you tried it)?
- **T56-10 (step 10).** Each seat colour as its name, grain and worn edges kept, parked, ridden and in first person?
- **T56-11 (step 11).** Which dark seats look alike in the game's light? Black darker than the stock brown, still
  leather? Pre-war turquoise?
- **T56-12 (step 12).** The piped seats' welts clear close up?
- **T56-13 (step 13).** The seat and Free colour apart? The MCM's Apply mid-ride? An old save's seat as it came?
- **T56-14 (step 14).** The frame rate beside the parked bike: 2026-11-15b against this build, stock and with the
  helmets?
- **T56-15 (step 15).** First person: still shaking? Which reading did the "camera: the camera root at ..." line name,
  and did an "EyeAtCamera off" line come?
- **T56-16 (step 16).** Zooming in with the wheel: one bike all the way, never none, never two?
- **T56-17 (step 17).** The stutter across cells: better, worse or the same, and with `ParentKeep=0`? The ParentTime
  lines of both runs?
- **T56-18 (step 18).** The view's lean: visible now? Which value of the slider do you like?
- **T56-19 (step 19).** Looking back: the mouse tilts the view, and it comes back level? The first-person arms gone
  while you look back, back when you look ahead, and after VATS or getting off while looking back? Did the end line say
  the game moved or held your pitch?
- **T56-20 (step 20).** A and D at 0.45: right, too much, too little?
- **T56-21 (step 21).** One set of bars and one speedometer with your body shown?
- **T56-22 (step 22).** No gun on the right grip, whatever the quick menu put in hand?
- **T56-23 (step 23).** Nothing of your outfit in front of your eye? Anything gone that you want to see (a sleeveless
  top, a vest, a backpack)? What do you wear? `BodyNear=10` or 0 better?
- **T56-24 (step 24).** The body more often, in the first ride too? Sitting right? The hands on the grips over bumps
  and at a hitch, or a frame ahead or behind? The lock line's BodyFollowCamera part (A against B)?
  `BodyFollowCamera=0` better or worse?
- **T56-25 (step 25).** Drawn right after getting on: seated, both hands on the bars, the pistol in your hand, no swap?
  Where did the shots and the muzzle flash come from? What did the GunCarry line say?
- **T56-26 (step 26).** A jerk at a draw or a put-away, more than a frame? The GunRootFrame line: "the root a frame ahead
  of the bones", or "isn't in the order"? Any A/B better?
- **T56-27 (step 27).** A rifle by its key: away within a second, no sheathe pause, still on the bike? The "is
  PlayerCharacter's heading" line?
- **T56-28 (step 28).** A save right after the rifle key: still on the bike? The "not counted" line?
- **T56-29 (step 29).** Getting on with a rifle out? A pistol drawn soon after a rifle's put-away: seated at once? A
  hitch in first person with the rifle's swap?
- **T56-30 (step 30).** The kit's preview: the whole bike in the upper half, three-quarters, a little from above? What
  did "moved from" say?
- **T56-31 (step 31).** Zoom and turn as before? The plate colours on the parked bike at the close?
- **T56-32 (step 32).** If still off: the same as test 55, or another fault? Which `KitFitBox` or Tune values looked
  right?
- **T56-33 (step 33).** A full pull: the speed matching the gears now? The take-off too slow? The sound as in test 55?
- **T56-34 (step 34).** Steady speeds: the right gear, no hopping? The squeezed top band (38-52 on the dial all one
  note, 4th settling while the needle climbs): does it bother you?
- **T56-35 (step 35).** Picking up again after a turn or a tap off: sluggish? The note steady?
- **T56-36 (step 36).** A log or a kerb climbed as before? Which pull A/B felt best?
- **T56-37 (step 37).** Anything a 2026-11-16b A/B made better or worse?

## The 2026-11-15b build: test 53's and test 54's wishes, in this order

This build adds what tests 53 and 54 asked for: A and D turning the bike in first person as the mouse does; the view
leaning a little into turns; looking back over your shoulder when you reverse in first person, and a key to look round;
a handgun from the saddle, the left hand on the bar; your own body in first person; the bike stepping round parked cars
and other wide things, not only posts; the right-hand cables turning with the bars. You didn't test 2026-11-15a, so
test 55 runs on this build and covers both: first the 2026-11-15a build's steps 1-10 (the next section), then steps
11-24 here, with questions T55-1 to T55-10 there and T55-11 to T55-24 here. Every new behaviour has an off value that
gives the 2026-11-15a build back (README's table of the 2026-11-15b build's keys), so each A/B is one key away. Four things only the game can
settle: whether the game builds its first-person camera the way the plugin turns it (step 12), whether it draws your
body in first person at all (step 15), whether the game's own put-away works on the bike (step 18) and which pistols
count as handguns (step 20).

Before you start:
- **in the MCM set "Eye forward on the bike" and "Eye height on the bike" back to 0 first** (your save keeps test 54's
  -6 and -3; the new default already holds them: step 3 of the next section);
- install as a Replace over 2026-11-14a (this build holds all of 2026-11-15a); F4SE and `CMB_Slope.dll` as before. If
  you edited `CMB_Slope.ini`, put your values into the new one: `[Tilt]`, `[Steer]`, `[Lamp]`, `[View]` and `[Diag]`
  have new keys (and 2026-11-15a's own: the next section);
- the MCM's Riding "Weapons while riding" should read "Handguns only": it is new, so your old "Allow combat while
  riding" (on in test 53) isn't carried over, on purpose. Leave it on "Handguns only" for steps 1-10 too;
- the A/B switches are in `CMB_Slope.ini`: for example `[View] Body=0` (no body in first person), `[View]
  CameraTurn=0` (nothing turns the view), `[Steer] FirstKeys=0` (A and D as before), `[Tilt] GunPose=0` (the old
  standing gun poses), `[Steer] SidestepWide=0` (wide things only braked for). Change one, save the file, get off and on
  (no restart), and put it back after;
- optional, for a later build's seated pistol clips: if you run `make_rider_pose.bat` from the repository, update it to
  this build's commit (the package's README names it) and run it once as before: it now also writes
  `CMB_RiderPose_report.txt` next to `CMB_RiderPose.esp`. Send that file. The plugin it makes is the same, so skip this
  if it's a bother.

The log's first lines: `CMB_Slope.log` has seven settings lines more: `  steer (2026-11-15b, the review):
FirstKeysArmed=1 (...)`, `  view (2026-11-15b, test 54): CameraTurn=1
(FirstPersonState's GetRotation wrapped: the look and the view's lean) Roll=-1 (...) LookBack=-1 (...) ...; [Steer]
FirstKeys=1 (...); [Diag] TurnEachRide=0`, `  view: LookKey=-1: the MCM's CMB_LookKey 44, Z (VK 0x5A): held in first
person on the bike, ...`, `  view (2026-11-15b, test 54): Body=1 (...) BodyEye=(0, 7, 7) ...; [Diag] BodyProbe=1
BodyProbeEvery=10`, `  weapons (2026-11-15b, test 53's wish a): PutAway=1 GunPose=1 GunStandBack=1 GunPredict=1 ...`,
`  sidestep (2026-11-15b, test 53's wish g): SidestepWide=1: ...` and `  frame (2026-11-15b): [Lamp] FrameLead=1 ...
[Diag] FpsFrames=1 ... PausedFrames=1 ...`, and two globals lines, `globals: the 2026-11-15b build's 4 found, CMB_ViewBack
to CMB_LookKey (...)` and `globals: the 2026-11-15b weapons globals found, CMB_RideWeapons 1, ...`. `Papyrus.0.log` at
every getting on: `Weapons while riding: Handguns only (CMB_RideWeapons 1): fighting on, VATS off (a handgun
equipped).` (or `fighting off ... (no handgun equipped)`). A globals line saying `0 of 4 found` or `no CMB_RideWeapons`,
or the MCM still showing "Allow combat while riding", means an older ESP or MCM folder is loaded: stop and say so.

**First person** (steps 11-15; test 53: the bike leaning but the view level, "no way to turn just the camera" when
backing; test 54: A and D sliding the bike sideways, no arms and torso)

11. **A and D turn the bike**: ride in first person and steer with A and D only (W held). The bike should turn as with
    the mouse (the bars over, the bike leaning), not slide sideways. Then steer with the mouse: it should feel exactly
    as before.
    - `CMB_Slope.log`, once a ride: `steer: first person: the side keys turn the bike (FirstKeys 1 of the clamp, N deg/s
      now): the game gets no strafe`.
    - A/B: `[Steer] FirstKeys=0` (A and D slide as before).
12. **The view leans**: in those turns the view now leans a little with the bike (4 degrees at the most). Try the
    MCM's Riding "View leans in turns (first person, deg)" from 0 (level, as before) to 10: which do you like?
    - `CMB_Slope.log`, the first ride in first person: `camera: FirstPersonState (...): GetRotation (slot 0xC, ...)
      wrapped ...`, then `camera: GetRotation's answer (w, x, y, z) and the camera root's world rotation at the next
      task: ...: the root's rotation is the answer's matrix (1 frame(s))` (or `its transpose`, or `... times a constant
      local rotation`: send it, it says how the game builds its camera), and at the first turn `camera: the turn
      followed (10 frames within 0.01 of the turned answer): ..., the view leaned 0.7 deg (0.7 asked; + right)`.
    - Bad: a `camera: ... off this session`, `camera: GetRotation not called ...`, `camera: the camera root never
      matched ...` or `camera: the turn not followed ...` line, then `view: LookBack 1 (over the shoulder) without a
      camera to turn (...)`: the view can't be turned on your game, so the lean and the look key do nothing and backing
      switches to third person (step 13). Say so; nothing else breaks.
    - A/B: `[View] Roll=0`.
13. **Looking back while reversing**: in first person, from a stop, hold S a moment: the view turns over your right
    shoulder (hold D while backing: still right; hold A: over the left one). While it is turned the mouse turns only
    your head and the bike keeps going straight back. Hold the other side key a moment: the view swings round the back
    to the other shoulder. Press W: the view comes back to the front at once. Try it with something right behind you
    too. Open the Pip-Boy while looking back: the view should face forward for it.
    - `CMB_Slope.log`: `view: looking back over the right shoulder (backing 0.3 s; LookBackAngle 150, the mouse +/-60)`,
      `view: the look swung through the back to the left shoulder (...)`, `view: back to the front after 2.4 s
      (forward)`; the eye line every 2 s ends `; the view turned 148.0 deg right of the bike (backing), leaned ...`.
    - Then set the MCM's Riding "Looking back while reversing (first person)" to "Third person" and back up: the game
      should switch to third person while you back and back to first person when you ride forward (`Papyrus.0.log`:
      `View: third person while backing (CMB_ViewBackNow 1).`, then `View: first person again after backing
      (CMB_ViewBackNow 0).`). Which do you prefer? "Off" = as before. Put it back to "Over the shoulder". (`[View]
      LookBack=2` in the INI does the same, but only while this MCM setting isn't "Off".) With a weapon drawn neither
      happens: step 17.
    - A/B: `[View] LookBack=0` (the view stays ahead), `[View] CameraTurn=0` (nothing turns the view: over the
      shoulder becomes third person).
14. **The look key**: hold Z while riding in first person and move the mouse: only your head turns, the bike keeps its
    line; let go and the view comes back. Does Z clash with one of your keys? If it does, the MCM's Hotkeys "Look key
    (scan code)" takes another (44 = Z, 45 = X, 46 = C, 56 = Left Alt; 0 = none): say which you took. (With a weapon
    drawn it turns your head 60 degrees at most: step 17.)
    - `CMB_Slope.log`: on getting on `  view: LookKey=-1: the MCM's CMB_LookKey 44, Z (VK 0x5A): ...`; held `view: the
      look key (Z) held at 612 u/s: the mouse turns the head only (the bike keeps its line)`, then `view: the look key
      let go after 1.8 s (...)`.
    - A/B: `[View] LookKey=0`.
15. **Your own body**: get on in third person and ride a few seconds at speed, going straight (the plugin remembers how
    you sit). Switch to first person while riding. Look down: do you see your arms with the hands on the grips, your
    chest and legs, in your outfit? Turn with the mouse and with A and D: do the hands stay on the grips as the bars
    turn? Any piece of your head or hair in front of the camera? Anything flickering? A second bike? Open the Pip-Boy,
    and draw your pistol: the body should go and come back. Looking back (step 13) it should go too, and come back
    looking ahead. Get off and on again in first person straight away: it should show at once (the pose is kept for the
    game session). A screenshot or two help.
    - `CMB_Slope.log`: once a session `body: the riding pose taken in third person (N bone node(s), ...)`. At each first
      person, first `body: first person: the player's 3D root BSFadeNode 'skeleton.nif' flags 0x... [...]; ... hidden
      (bit 0): ...` (it says what hides your body in first person: send it whatever it says), `body: first person: the
      root's fade ...`, `body: the first-person 3D (...)` and `body: the third-person skeleton in first person ...`;
      then `body: first person: the rider's body shown (...)`, and 0.5 s later `body: drawn? ... the game visits it ...`
      (the game draws it: you should see it) or `... not visited ...` (the game hides it some other way: nothing new
      shows, and that is the answer). Hidden for a reason: `body: first person: the rider's body not shown: <why>`. At
      getting off: `body: the rider's body shown in first person N time(s) this ride, ...`.
    - If it looks wrong (a body standing through the bike, your arms out of place, the inside of a head): a screenshot,
      then `[View] Body=0` turns it off. If the collar or the shoulders look cut off near the camera, A/B `[View]
      Near=5`.

**A handgun on the bike** (steps 16-20; test 53: "only handgun can be used ... hold handlebar with at least one hand
(preferably left) and shooting with another (right)"; the MCM's "Weapons while riding" on "Handguns only")

16. **Draw, aim, fire**: with a 10mm pistol equipped, get on and ride straight for two or three seconds with the gun
    away. Then draw it (R, or fire) in third person while riding: are you seated, the left hand on the bar, the bike
    under you (not swapped, no flicker)? Aim, fire, reload, put it away (R). Steer both ways with it out: does the left
    hand follow the bar? Stop with it out, then ride off again: any jump between the standing and the riding seat? Draw
    while standing still, then ride off. Once, draw straight after getting on, before riding: you should see the old
    standing pose for that one draw (fine; just say how it looked).
    - `CMB_Slope.log`: while you ride holstered `gun: the seat pose read (still, ...)` and `(riding, ...)`; at the draw
      `gun: the weapon state 0 > 1 > 2 > 3 in 0.55 s (...)` and `gun: a handgun out (...) at 640 u/s: the rider on the
      riding seat pose read 12.3 s ago, the right arm the game's, carried to the seat's shoulder (GunPose)`; every 10 s
      `gun: posed 12.4 s, ...: the bones' own move a game frame at most X relative to the root, the prediction off by at
      most Y (GunPredict=1); ...`; at the ride's end `gun: a handgun out on the seat pose 2 time(s) this ride, 14.6 s in
      all (GunPose)`. The draw before riding: `gun: a handgun out at 640 u/s with no riding seat pose yet (...)`.
      `Papyrus.0.log`: no `Rider pose applied (standing footsteps while riding ...)` during the draws, and the Slot 57
      lines no longer switching between `CMB_BikeWorn.nif` and `CMB_BikeWornRiderF.nif` at each draw.
    - A/Bs: `[Tilt] GunPose=0` (the old standing poses), `GunPredict=0` (does the body wobble more at speed with the gun
      out?).
17. **A weapon drawn: looking back, the look key, A and D**: with a weapon out the view no longer looks back, and A and D
    turn the bike in third person too.
    - Draw the pistol in first person, then reverse (hold S from a stop): the view should stay looking ahead (no turn
      over your shoulder while a weapon is out), and the view still leans in turns. Put the pistol away and reverse
      again: the view turns over your shoulder as in step 13.
    - Set the MCM's "Looking back while reversing (first person)" to "Third person", draw the pistol in first person and
      reverse: the game should stay in first person, and the bike shouldn't flicker or swap. Then put the pistol away,
      reverse (third person), and draw it while reversing: back to first person at once. Put the MCM back to "Over the
      shoulder".
    - With the pistol drawn, hold Z and move the mouse far to one side: your head turns about 60 degrees at most.
    - In third person with a weapon drawn, riding, press A and D. Before, the bike slid sideways; now it shouldn't slide.
      Does it turn, or does the body snap back to where the camera looks?
    - `CMB_Slope.log`: once a backing `view: backing with a weapon drawn (the weapon state 3): no look back over the
      shoulder (LookBack 1); the look key turns the head 60 deg at most` (or `no third person (LookBack 2)`); drawn while
      already in third person from backing: `view: third person while backing over after N s (a weapon drawn):
      CMB_ViewBackNow 0`; with "Third person" and the pistol out, no `View: third person while backing` in
      `Papyrus.0.log` and no Slot 57 swap. A and D with a weapon drawn in third person, once a ride: `steer: a weapon
      drawn in third person (the weapon state 3): the side keys turn the bike (FirstKeys 1 of the clamp, N deg/s now;
      FirstKeysArmed): the game gets no strafe`, and no `slide:` lines 27-44 deg off the heading.
    - A/B: `[Steer] FirstKeysArmed=0` (the slide in third person back).
18. **Not a handgun**: with the pistol out, press a rifle's favourites key. You should see "Only a handgun can be used
    on the motorbike.", the rifle put away within a second, and you stay on the bike and can't draw it. Then switch
    back to the pistol and draw it.
    - `Papyrus.0.log`: `Weapons: [Weapon < (...)>] out, not a handgun (...): put away asked (CMB_WeaponAway 3).`, then
      `Weapons: put away after 0.6 s (...)` (or `still out 1.0 s after the ask: the sheathe action played ...`, or `still
      out 3.0 s after the ask: the ride ended (2026-11-15a's rule).`). `CMB_Slope.log`, once a session: `gun: the
      player's slot 0xC7 is the heading's getter (...): slot 0xC9 (...) taken as DrawWeaponMagicHands (PutAway)` (or
      `... not the layout expected, nothing called ...`); then `gun: put away asked (CMB_WeaponAway 3):
      DrawWeaponMagicHands(false) called, the weapon state 3` and `gun: the weapon state 3 > 4 > 5 > 0: away 0.62 s
      after the ask (...)` (or `... not away 4.00 s after the ask (..., 6 calls)`: the game's put-away does nothing
      there).
    - A/B: `[Tilt] PutAway=0` (the script's sheathe action, then the ride ends after 3 s).
19. **Getting on with a weapon out**: get on with a rifle out, then with the pistol out: both should be put away and you
    get on, holstered (`Papyrus.0.log`: `Getting on: the weapon put away first (0.8 s; ...)`).
20. **Which guns count, and a save**: try a pipe pistol, a .44 revolver, a laser pistol, a plasma pistol and a flare gun:
    which can you draw on the bike? (`Papyrus.0.log`, once a gun: `Weapons: [Weapon <...>] equipped: a handgun keyword on
    the base form True, worn True, on the instance True (17 keywords); WeaponTypeRifle worn False, on the instance False:
    a handgun.`: send them, they say which test found each.) First person with the pistol out keeps the game's own
    two-handed arms (not changed yet). Then the MCM's "None" and "Any weapon (standing poses)" once each (the 2026-11-15a
    build with "Allow combat while riding" off and on), and back to "Handguns only". Last, the saves:
    - save on the bike with the pistol drawn, ride on a bit, then load that save: the pistol should stay out, not put
      away by itself (no `gun: put away asked` line in `CMB_Slope.log` until the script asks);
    - switch to a rifle by its favourites key on the bike (it starts being put away), save at once and load: the rifle
      should still be put away, or the ride end as in step 18, not stay out for good.

**Sidesteps round wide things** (step 21; test 53: "does it work only for mailboxes/lampposts?")

21. **Wide things**: Caution as you like it (50 is fine). Ride straight at a parked car, a barrel group, a short fence
    piece or a heap of debris where one side is open (the thing ends within about a bike's width of your line),
    forward held, no A or D, the mouse still. The bike should swerve round it on the open side (a quick lane change,
    braking a little as it does) and carry on. Try 5-10 of them, and once a car right across the road (no open side: it
    should brake as before). How does the swerve feel: too sharp, too late, too close to the thing's corner? Then ride at
    a house's wall, a cliff, a long fence or a building's corner: it should only brake, as before. Then the mouse: as a
    sidestep (narrow or wide) starts, move the mouse a little the way it goes: it should carry on; a lot that way: you
    take over smoothly; the other way: it lets go as before. Sweep the mouse fast past a post ahead: no start-and-stop
    jerk any more. Last, a few sidesteps in first person (posts, mailboxes, cars) with the mouse still: they should run
    to the end, not stop after a tenth of a second.
    - `CMB_Slope.log`: `sidestep: Sedan02_Postwar (layer 29) wide 560 past the front wheel at 905, its edge within 40
      to the left (...): to the left, ... (SidestepWide)`, then `sidestep: over after 0.4x s (wide): ...`; a wall: `...
      wide and tall: ...` or `... no edge within 120 ...`; the mouse: `sidestep: the mouse 7.2 deg toward the open side:
      kept (SidestepMouseSide)`, `sidestep: handed to the rider after 0.31 s: ...`, `sidestep: not started for c_Post02:
      the rider is steering (...; SidestepSteady)`; in first person with the mouse still, `sidestep: over after ...` with
      no `kept` line and no `let go ... (the mouse)` a tenth of a second in. At each ride's end `sidestep: this ride 3
      narrow and 2 wide started: ...; wide ones not stepped round: 12 not a placed thing of their kind, 3 too tall, no
      edge near 4, ...`: send them, they say which rule refused most.
    - A/Bs, a ride each: `[Steer] SidestepWide=0` (wide things only braked for), `SidestepSteady=0`,
      `SidestepMouseSide=0`. If the swerve is too sharp: `SidestepWideRate=90` and `SidestepWideMost=20`.

**The cables** (step 22; test 53: "cables that should be attached to handlebar on the right side ... just floating")

22. **The right-hand cables**: ride in first person, slow down or stop, and swing the bars left and right (the mouse, or
    A and D): the two thin cables coming out under the right switch block and the thin wire from the right side of the
    bar should stay attached and swing with the bar (before, their ends hung in the air one way and went into the switch
    block the other). With the bars straight nothing should look different. Then the same in third person, from the
    right side, while turning. If anything near the steering head, behind the headlamp, looks broken at full lock, say
    where.
    - `CMB_Slope.log`, on getting on: `tilt: CMB_BikeWornRiderF_front_cables is the bar assembly [front, by its name]
      (...)` (`CMB_BikeWornRider_front_cables` for a male rider); in first person `view: the reference ...'s 3D
      ('CMB_BikeView', ...): 50 shape(s) under 'CMB_BikeView', 50 matched by label to the worn bike's 50 held skin(s)`
      (test 54: 49).

**The lamps and the frame-rate line** (step 23; test 54: the plugin's task runs twice a frame)

23. **Nothing to do but look**: the `time: the last 10 s ...` line's number should now be about your real frame rate
    (about half test 54's), ending `; the game's frames, the plugin's task 2.0 times a frame (FpsFrames)`; a long pause
    (the Pip-Boy open a while at a stop) is one `game: the world paused ...` line, not two. The headlamp's beam and the
    tail lamp's light should keep up at speed. A/B: `[Lamp] FrameLead=0`.

**The A/Bs** (step 24)

24. **The A/Bs**: if you haven't already in the steps above, one at a time, each for a ride or two, then put it back:
    `[Steer] FirstKeys=0` (step 11), `[View] Roll=0` (step 12), `LookBack=0` and `CameraTurn=0` (step 13), `LookKey=0`
    (step 14), `Body=0` and `Near=5` (step 15), `[Tilt] GunPose=0` and `GunPredict=0` (step 16), `[Steer]
    FirstKeysArmed=0` (step 17), `[Tilt] PutAway=0` (step 18), `[Steer] SidestepWide=0`, `SidestepSteady=0` and
    `SidestepMouseSide=0` (step 21). Anything better or worse?

The off values, each giving 2026-11-15a: `[Steer] FirstKeys=0`, `FirstKeysArmed=0`, `SidestepWide=0`,
`SidestepSteady=0`, `SidestepMouseSide=0`; `[View] CameraTurn=0`, `Roll=0`, `LookBack=0`, `LookKey=0`, `Body=0`;
`[Tilt] PutAway=0`, `GunPose=0`, `GunStandBack=0`; `[Lamp] FrameLead=0`; `[Diag] FpsFrames=0`, `PausedFrames=0`,
`BodyProbe=0`, `GunTrace=0`, `GunListen=0`; in the MCM "Weapons while riding" on "None" or "Any weapon (standing poses)"
(the old switch off or on), "Looking back while reversing (first person)" on "Off", "View leans in turns (first person,
deg)" at 0 and "Look key (scan code)" at 0. The cables have no switch (2026-11-15a's four bike nifs copied back give the
old ones). The 2026-11-15a build's own switches back to 2026-11-14a's are all still there (the next section).

Send all the logs of each session (`CMB_Slope.log` and its three `_prev` logs, `Papyrus.0.log`), any crash log,
`CMB_RiderPose_report.txt` if you made it, the screenshots of steps 2 and 15, and a short video of steps 16 and 18 if
you can.

### Questions for you (test 55, the 2026-11-15b build)

- **T55-11 (step 11).** A and D in first person: the bike turns as with the mouse, no sliding sideways? The mouse as
  before?
- **T55-12 (step 12).** The view's lean in turns: how much do you like (0-10)? Did the log say "the root's rotation is
  the answer's matrix" (or "its transpose") and "the turn followed", or a "camera: ... off this session" line?
- **T55-13 (step 13).** Looking back while reversing: over the shoulder, the head with the mouse, the swing round the
  back, W back to the front, the Pip-Boy? Or do you prefer "Third person"?
- **T55-14 (step 14).** The look key: does it work? Is Z free in your bindings, or which key did you take?
- **T55-15 (step 15).** Your body in first person: seen at all? The hands on the grips while turning? Any head, hair,
  flicker or second bike? What did "body: drawn?" say? Was `Near=5` better at the collar?
- **T55-16 (step 16).** A handgun drawn while riding: seated, the left hand on the bar, the bike under you? Steering with
  it out, stopping and riding off? `GunPredict=0` better or worse?
- **T55-17 (step 17).** With a weapon drawn: the view stayed ahead while reversing, and the game stayed in first person
  with "Third person"? The look key about 60 degrees? A and D in third person: does the bike turn, or does the body snap
  back to the camera?
- **T55-18 (step 18).** A rifle by its favourites key: put away within a second, and you stayed on? What did the `gun:
  the weapon state 3 > ...` line say?
- **T55-19 (step 19).** Getting on with a rifle out and with the pistol out: both put away and on?
- **T55-20 (step 20).** Which pistols could you draw (pipe, .44, laser, plasma, flare gun)? "None" and "Any weapon" as
  the old switch off and on? After loading the save, did the pistol stay out, and was the rifle still put away?
- **T55-21 (step 21).** Wide things stepped round: how did the swerve feel? Walls and buildings only braked for? The
  mouse keeping, handing over or letting go as described? First-person sidesteps running to the end?
- **T55-22 (step 22).** The right-hand cables attached when the bars turn? Anything broken behind the headlamp at full
  lock?
- **T55-23 (step 23).** The frame-rate line about your real frame rate, "2.0 times a frame"? One line for a long pause?
- **T55-24 (step 24).** Anything an A/B made better or worse?

## The 2026-11-15a build: test 54's fixes, in this order

This is the fixes build for test 54 (run on 2026-11-14a: two crashes at the field kit, both just after "Plate
background: The plate's own"; first person still shaking, because the camera check switched itself off on its first
frame; no preview in the kit's menu, the menu's camera inside the bike; the stock red tank for about 0.6 s when first
person came right after getting on; getting on about 0.85 s slower than 2026-11-10a; the top speed reached in 2nd gear)
and for two of its wishes: your eye where you put it (forward -6, up -3) as the default, and the speed climbing with the
gears. For the gears you chose the slower pull, so the gear sounds stay exactly as they are: the bike now takes longer
to reach its top, the engine's gears are untouched. What test 54 liked is as it was: the number keys at speed, the
bike's hotkey on B, Free colour in third person, the kit's names and its settlements rule, the engine quiet in menus,
the five gears' sound, the guard beside a downed NPC. Not in this build, coming in 2026-11-15b: A and D turning the bike
in first person (with a slight lean), the rider's arms and body in first person, looking back when reversing, handguns
on the bike, sidestepping big objects, the right-hand cables. Steps 1-10 in this order; each says what to look for and
the log line that answers it. Every new behaviour has an off value that gives the 2026-11-14a build back (README's table
of the 2026-11-15a build's keys), so each A/B is one key away. Five steps settle what only the game can: whether the kit's crash is gone (step
1), where the menu's camera really is (step 2), the space of the camera's answer in first person (step 3) and how the
slower pull feels from a stop and at speed (steps 6 and 7).

Before you start:
- install as a Replace (2026-11-15a over 2026-11-14a); F4SE and `CMB_Slope.dll` as before. If you edited
  `CMB_Slope.ini`, put your values into the new one: `[Steer]`, `[Look]`, `[View]` and `[Diag]` have new keys, and
  `[View] EyeAt` and the field kit preview's four New values have new defaults;
- **in the MCM set "Eye forward on the bike" and "Eye height on the bike" back to 0 first** (your save keeps test 54's
  -6 and -3; the new default already holds them, so leaving them would put your eye 6 further back and 3 lower again);
- keep Global Stash by SKK installed; play with `CMB_AllowCombat` as you usually do (on 2026-11-15b: leave the
  MCM's "Weapons while riding" on "Handguns only", the section above);
- the plugin now keeps the logs of the three sessions before (step 8), so a crash and two restarts no longer lose one;
  still say which session each step was in;
- a change to `CMB_Slope.ini` is read when you get on: save the file, get off and on (no restart), unless a step says
  otherwise;
- the 2026-11-14a build's steps (the next section) were test 54's: no need to run them again, but one wasn't tried then
  and is asked again here (step 9).

The log's first lines: `CMB_Slope.log`'s first line now ends `...; the session before's log kept as
CMB_Slope_prev.log, the two before it as CMB_Slope_prev2.log and CMB_Slope_prev3.log (KeepLogs=3)` (the first two
starts after the update: `..., the one before it as CMB_Slope_prev2.log (KeepLogs=3)` and `... (KeepLogs=3: none
older)`), and there are four settings lines more: `  look (2026-11-15a, test 54): KitDefer=1 (the kit's plate colours
on the parked bike at the menu's close) MountQuick=1 (getting on reuses an unchanged look's indexes and kept key):
CMB_LookOptions 131071 for the scripts`, `  kit (2026-11-15a): [Look] KitTuneDistance=1 (Tune's first slider: the
distance, pos y) KitPreviewScene=1 (the menu's scene and camera lines, with KitPreviewLog)`, `  view (2026-11-15a, test
54): CameraWorld=1 (GetTranslation's answer the camera root's world) LeadFrame=1 (the Lead's time the game's frame)
LookWait=3 (the view bike kept hidden until its look is on, for at most that)` and `  steer (2026-11-15a, test 54):
above 0.6 of the top the throttle climbs at most 0.0727 of the top a second, the top 5.5 s from there at full throttle,
the launch's curve and the even ramp alike (PullTime, PullFrom: the speed rising with the engine's gears); a launch
from rest ends once the bike is that fast`. The older lines now read `  kit (2026-11-14a): [Look] KitPreview=1 (New: pos
0,400,0, turn 0,0,0.785398, scale 1, zoom -1..3) KitPreviewLog=1`, `  view: Enabled=1 ... EyeAt=(0, -5, 125) ...`, and
every look line says `CMB_LookOptions 131071 for the scripts`. The MCM's "Field kit preview" section still showing
"Preview size (%)" means an older MCM folder is loaded: stop and say so.

**The field kit** (steps 1-2; test 54: two crashes, both right after "Plate background: The plate's own" in the menu,
and no preview: the menu's camera sat inside the bike)

1. **The plate colours, no crash**: save first. In Sanctuary choose Customise at the parked bike and, in one visit to
   the menu, take a new Plate design, then "Plate background: The plate's own", then a "Plate letters" colour, then two
   or three more plate colours, "The plate's own" again among them. The game should not crash. The parked bike's plate
   no longer changes while the menu is open: leave the menu and look at the parked bike: are your plate colours on it
   now? Do it two or three times (test 54 crashed in both of its two tries).
   - `Papyrus.0.log`, in the menu, for each plate colour: `Customise: Plate background = PlateBack:own (0): on the
     parked bike when the menu closes (KitDefer)` (no `the parked bike re-composed` and no `... applied now (the field
     kit)` while the menu is open); when it closes: `Customise: the plate colours chosen in the menu (3) go on the
     parked bike with the look, the menu closed (KitDefer)`, then `Look: put on (the field kit): ...` and `Look: the
     parked bike's swap holds 63 entries, 28 applied now (the field kit), colours: ...` (numbers for illustration). If
     you step away from the kit before the menu has quite closed: `Look: the parked bike's swap waits for the workbench
     menu to close (the field kit, KitDefer)` and `Look: the workbench menu closed N s later: ...`.
   - If it crashes anyway: send the crash log and all four `CMB_Slope` logs and the Papyrus log of that session; say
     which choice you had just made.
   - A/B, only on a save you can lose: `[Look] KitDefer=0` brings back 2026-11-14a's re-compose in the menu (it may
     crash). Put it back to 1.
2. **The preview**: at Customise, take a screenshot as the armour menu opens. Does the whole bike show, turned
   three-quarters, in the middle (it may look small)? Roll the mouse wheel all the way out, wait a second, then all the
   way in, wait a second (each stop is logged); a screenshot at both ends.
   - `CMB_Slope.log`, once at the start: `kit: the preview's transform written (the new one): pos 0,400,0, turn
     0,0,0.785398, scale 1, zoom -1..3 (it was pos 0,0,0, turn 0,0,135, scale 0.45, zoom 0.5..1.5)`. At Customise: `kit:
     the menu's 3D: item FExxx8CE; model 'Motorcycle' ...: its local scale 1.000 at (x, Y, z) ...; bound (bx, BY, bz) r
     109.6 ...; zoom 0.00 in -1.00..3.00 ...`: Y about 440 and BY about 442 mean the record's distance is used as
     assumed (test 54: 39.7 and 42.5); right after it `kit: the menu's scene: ...` and `kit: the menu's camera: ...` (it
     ends `the whole bike in view: yes (...)` or `no (...)`, or says `none found ...`); while you zoom, `kit: the
     menu's zoom settled at ...`. Send them all: they give the next build the camera's real place and field of view.
   - Only if the bike is too near (cut off) or too far (tiny): the MCM's "Field kit preview" section, "Tune (the sliders
     below)", then "Preview distance" (less = bigger, more = smaller; 400 is New's), and if needed "Preview turn",
     "Preview up / down" and the zooms; leave the MCM and Customise again. Which values looked right? `kit: the
     preview's transform written (the MCM's sliders): ...`. On a save from 2026-11-14a the slider first shows 30: that
     means New's 400 until you move it.
   - A/B: "Field kit preview" "As before" (2026-11-10a's tyre), then back to "New".

**First person** (steps 3-4; test 54: "it still shakes ... every hole is visible as a shake", the stock red tank for
about 0.6 s)

3. **Steady, and your eye's place**: with "Eye forward on the bike" and "Eye height on the bike" at 0 (see *Before you
   start*), ride in first person for 2-3 minutes: on a flat road at full speed, over rough ground, through turns, and
   standing still. Does the bike still shake against your view? Is your eye in the right place, standing and at full
   speed? (At speed it may feel a little further back than in test 54: the bike no longer lags a frame behind the
   camera.) If you move the sliders again, say to what, and whether you judged it standing or at speed.
   - `CMB_Slope.log`: `camera: FirstPersonState (...): GetTranslation (slot 0xD, ...) wrapped ...` once, then once
     `camera: GetTranslation's answer (x, y, z) as the camera root's world ([View] CameraWorld=1): the root 0.00 from it
     at the next task; read through the root's parent (2026-11-14a's reading) 118xxx.xx; the root's local (...), its
     parent ...` (send it whatever its numbers). Good: the root 0.00 and **no** `camera: EyeAtCamera off this session`
     line. Every 2 s `view: lock: ...` ending `... the camera root 0.00 at most from that place at the next task;
     LeadFrame: 2.0 task(s) a game frame (median of N), the frame 9.5 ms (median), the camera's moves and the Lead's
     error at its tasks ...`: send them; "2.0 tasks a game frame" confirms the task runs twice a frame, as test 54's log
     suggested.
   - If it still feels like "riding without suspension" while the log says "the camera root 0.00", the bike now follows
     the game's own camera exactly and what is left is the camera's own path over the bumps: say so (smoothing that is
     a new feature for a later build).
   - A/B, one ride each: `[View] CameraWorld=0` (2026-11-14a's reading: the `EyeAtCamera off this session` line comes
     back, and the shake), then `LeadFrame=0`. Put them back.
4. **No red tank**: get on and switch to first person straight away, within a second or two, several times. You should
   see no bike for about a second, then the bike in your colours, never the red stock one. Then ride on in first person
   past a few cell changes: no red flicker when the first-person bike is handed over.
   - `CMB_Slope.log`: `view: first person: the view bike FFxxxxxx kept hidden until its look is on (0.80 s after its 3D;
     [View] LookWait 3 s at most)` then `view: the view bike FFxxxxxx's look on 1.25 s after its 3D: its materials
     swapped (25 of 49 shape(s)) ([View] LookWait)`. At a hand-over the `look on` line comes 1-2 s after `Tail light
     and first-person bike handed over` (`Papyrus.0.log`), then `view: handed over from ... to ...: the old one hidden
     and parked (the new one has had its 3D for the HandoverTime ...)`. Bad: `... not seen in 3 s ...: shown as it is`
     every time (the colour swap wasn't seen: send the log).
   - A/B: `[View] LookWait=0`: the red flash as in test 54.

**Getting on** (step 5; test 54: the screen back 3.40 s after the press, against 2.54 s in test 53)

5. **Quick again**: get on and off five times or more without changing the look. The black screen should be about as
   short as in test 53 (about 2.5 s from the press to the screen back, not 3.4). Free colour (or the Palette test)
   right in third person from the first moment, every ride. Then change only the hue in the MCM (Apply) and get on: the
   colour right at once (that ride does the full colour pass, so it takes a little longer); then get on again (quick
   again). Once: quit to the desktop, start again, load, get on: the colour right from the first moment.
   - `Papyrus.0.log`: `Getting on: the press 0.00, the fade 0.20, the equip 1.60, the pose ..., ready ..., the
     screen back 2.55, Mounted ... (real seconds)` (numbers for illustration; test 54: the equip 2.5, the screen back
     3.4); from the second ride after a load or a look change `Look: the worn bike's colour indexes before its equip
     (WornIndex): in its options' swaps since the last pass, the look unchanged (MountQuick), colours: ...`; the first
     ride after a load or a change has the 2026-11-14a line (`... Paint 4 of 4 set ...` or `... as they were ...`)
     once.
   - A/B: `[Look] MountQuick=0`: the black screen as in test 54.

**The pull** (steps 6-7; test 54: "bike reaches 50 just on gear 2, but it still goes on for 2 more without gaining
speed"; you chose a slower pull so the gears keep their sound)

6. **From a stop**: on a long flat road hold forward from a stop to the top speed. The take-off should feel as before
   (the first second, the surge to about half speed); after that the bike keeps gaining speed through 2nd and 3rd and
   reaches its top about when 3rd ends and 4th comes in (about 6 s after the press), instead of in 2nd. The gears
   should sound exactly as in test 54. Does the speed now match the gears? Does the pull feel too slow or too quick?
   - `CMB_Slope.log`: `launch: from rest: 0.3 of the top after 1.37 s, half after 1.6 s, 0.9 after 5.1 s, the top (0.97)
     after 6.0 s (the throttle from 0.25 closing on the top over 1.5 s, the cap's lead 0.45: LaunchTau); the cap bound
     N s; above 0.6 of the top at most 0.0727 a second (PullTime)` (about 5 and 6 s; test 54: `0.9 after 2.91-3.10 s`,
     no "the top");
     the gear lines `sound: gear 2 at ~450-550 u/s ...`, `sound: gear 3 at ~700-760 u/s ...` (test 54: about 910),
     `sound: gear 4 at ~900-935 u/s ...`, `sound: gear 5 ...` 1.5 s later, the shifts still about 1.5, 3.5, 6.5 and 8.0
     s after the press; the trace's `throttle: ... (keys ..., the game gets the throttle's, at the pull's rate
     (PullTime))` from about a second after the press to the top. If `gear 4 at` comes with the bike's speed under the
     `heard` speed (say `gear 4 at 860 u/s, ..., heard 870`), the bike fell behind the engine there: say so.
7. **Speeding up again at speed**: at full speed let go of the throttle for half a second and press it again; slow down
   to about half speed for a turn and pull away again; take a hit (or a kerb) at speed. The bike now climbs back at the
   same slower rate above 0.6 of its top (from half speed about 4-5 s to the top; 2026-11-14a about 1 s). Does that
   feel sluggish? The engine note shouldn't drop while the bike gains: how does it sound while it speeds up again (it
   now follows the speed more closely, a gentler pull)?
   - A/Bs in `[Steer]` (read on getting on), one ride or two each: `PullFrom=0.8` (quick again up to 0.8 of the top,
     slow only near it: the recovery after a lift or a hit is quicker), `PullTime=6` (a little slower, the top as 4th
     starts; the note about 90 rpm lower late in 3rd), `PullTime=7` (slower still: 3rd sounds flat, the trade-off
     against the sound), and if 5.5 feels too slow `PullTime=4.5`; `PullTime=0` is 2026-11-14a's pull (the top in
     2nd). Which felt best? Put them back.

**The logs** (step 8; test 54: session A's `CMB_Slope.log` was lost to two crash restarts in a row)

8. **Three earlier sessions kept**: nothing to do but look. After the game has been started three times, the plugin's
   folder (`Documents\My Games\Fallout4\F4SE`) holds `CMB_Slope.log` (this session), `CMB_Slope_prev.log`,
   `CMB_Slope_prev2.log` and `CMB_Slope_prev3.log` (the three before, newest first), and the first line of
   `CMB_Slope.log` says so (above). After a crash send them all. A failure to move one says `  (KeepLogs: N older
   log(s) couldn't be moved on, MoveFileEx error E)`: send that too. (`[Diag] KeepLogs=1`: only `CMB_Slope_prev.log`,
   as before; read at the game's start only.)

**Asked again: what test 54 didn't try** (step 9)

9. **The field kit only in your settlements** (2026-11-14a's step 10): park on a road outside any settlement and
   choose Customise: a message "The field kit works only in your settlements." and nothing comes out of the side bag
   (`Papyrus.0.log`: `Customise refused: not in one of your settlements (no settlement location): the field kit is for
   your settlements only (CMB_KitWhere 1).`). Then the MCM's Look "Field kit only in your settlements" off, at the same
   spot: the kit comes out and its menu opens there, parts from the side bag as before. The MCM's "Free customising"
   with "Apply the look" on the road works either way. Put the switch back on.

**The A/Bs** (step 10)

10. **The A/Bs**: if you haven't already in the steps above, one at a time, each for a ride or two, then put it back:
    `[Look] MountQuick=0` (step 5), `[View] CameraWorld=0` and `LeadFrame=0` (step 3), `LookWait=0` (step 4), `[Steer]
    PullTime=0` and `PullFrom=0.8` (steps 6-7). `KitDefer=0` only on a save you can lose (step 1). Anything better or
    worse?

The off values, each giving 2026-11-14a: `[Look] KitDefer=0`, `MountQuick=0`, `KitTuneDistance=0`,
`KitPreviewScene=0`, and New's four values at 2026-11-14a's (uncomment them: `KitPreviewPos=0,0,0`,
`KitPreviewTurn=0,0.02,44.764`, `KitPreviewScale=0.3`, `KitPreviewZoom=-1,1`); `[View] EyeAt=0,1,128`,
`CameraWorld=0`, `LeadFrame=0`, `LookWait=0`; `[Steer] PullTime=0`; `[Diag] KeepLogs=1` (at the next start). The MCM's
"Preview distance" is 2026-11-14a's "Preview size (%)" again with `KitTuneDistance=0` (its 30 then needs `set
CMB_KitPrevSize to 30` in the console: the slider now starts at 100). The 2026-11-14a build's own switches back to
2026-11-10a's are all still there.

Send all the logs of each session (`CMB_Slope.log` and its three `_prev` logs, `Papyrus.0.log`), any crash log, the
screenshots of step 2, and a video if you have one.

### Questions for you (test 55)

- **T55-1 (step 1).** The plate colours at the field kit, "The plate's own" after a new design among them, several
  times in one visit: no crash? The parked bike's plate in your colours once you left the menu?
- **T55-2 (step 2).** The preview: the whole bike, turned three-quarters? Zoomed fully out and in? If you moved "Preview
  distance" (or the others), to what?
- **T55-3 (step 3).** First person with the eye sliders at 0: steady now on rough ground? Your eye's place right,
  standing and at full speed? If you moved the sliders, to what, and judged standing or at speed?
- **T55-4 (step 4).** First person right after getting on: no red tank? Any red flicker at a hand-over?
- **T55-5 (step 5).** Getting on as quick as in test 53 (about 2.5 s to the screen back)? Free colour right from the
  first moment, after a hue change and after a restart?
- **T55-6 (step 6).** From a stop: does the speed climb with the gears now, the top as 3rd ends? Too slow or too quick?
  The gears' sound as good as in test 54?
- **T55-7 (step 7).** Speeding up again after a lift, a turn or a hit: sluggish? The note while it gains? Which A/B felt
  best (PullFrom 0.8, PullTime 6, 7, 4.5)?
- **T55-8 (step 8).** After three starts, `CMB_Slope_prev.log`, `_prev2` and `_prev3` there, and the first line saying
  so?
- **T55-9 (step 9).** Customise refused on a road outside a settlement, and allowed anywhere with the switch off?
- **T55-10 (step 10).** Anything an A/B made better or worse?

## The 2026-11-14a build: test 53's fixes, in this order

This is the fixes build for test 53 (run on 2026-11-10a: a stimpak by its number key at speed never used, its clip cut
12 times; Free colour blue in third person on every ride but the one the game loaded into; the riding FOV written back
by the game) and for its wishes: first person steady with your eye further back, the field kit's item and slots named, a
preview of the whole bike, the kit only in your settlements, the FOV dropped, the engine silent in the Pip-Boy and the
pause menu, and gears that rise more, smoothly, with no 2nd to 1st drop on a lift. What test 53 liked is as it was:
getting on in about 2 s, the field kit's menu holding beside Global Stash by SKK, the front end's shadow, the bike seen
in first person, Caution 50's sidestep, the tip, the engine held through a menu. Not in this build, coming in
2026-11-14b: handguns on the bike, looking back when reversing in first person, the A/D lean, sidesteps round bigger
things, the right-hand cables. Steps 1-14 in this order; each says what to look for and the log line that answers it.
Every new behaviour has an off value that gives the 2026-11-10a build back (README's first key table; the item's and
slots' names are the one exception), so each A/B is one key or one MCM setting away. Five steps settle what only the
game can: the number keys' way in (step 1), which key the bike's hotkey is (step 2), the Palette test (step 6), the
camera's own place in first person (step 7) and the field kit's preview (step 9).

Before you start:
- install as a Replace (2026-11-14a over 2026-11-10a); F4SE and `CMB_Slope.dll` as before. If you edited
  `CMB_Slope.ini`, put your values into the new one: several sections have new keys, and `[View] EyeAt` and seven
  `[Sound]` gear keys have new defaults;
- keep Global Stash by SKK installed; play with `CMB_AllowCombat` as you usually do;
- copy both logs aside before every quit (`CMB_Slope_stepN.log`, `Papyrus_stepN.log`): the plugin keeps only one earlier
  session;
- a change to `CMB_Slope.ini` is read when you get on: save the file, get off and on (no restart), unless a step says
  otherwise;
- the 2026-11-10a build's steps (the next section) were test 53's: no need to run them again, but two of them weren't
  tried then and are asked again here (steps 13 and 14).

The log's first lines: `CMB_Slope.log` has six settings lines more than before: `  quick (2026-11-14a, test 53):
QuickKeyCodes=auto (the game's Quickkey names, else QuickKeys' virtual keys 0x31,0x32,...,0xBD,0xBB) QuickKeyState=1
QuickCut=1 UseStopUnapplied=wait UseStopWaitMax=3 UseStopLead=1.5 QuickProbe=1`, `  look (2026-11-14a, test 53):
WornIndex=1 KeptMods=1 Repass=0; [Diag] WornPasses=1 HandoverFromReady=1: CMB_LookOptions 32767 for the scripts`, `  kit
(2026-11-14a): [Look] KitPreview=1 (New: pos 0,0,0, turn 0,0.02,44.764, scale 0.3, zoom -1..1) KitPreviewLog=1`, `  view
(2026-11-14a, test 53): EyeLock=1 (EyeAt held on the bike as tilted, at once) EyeAxes=1 Camera=1 EyeAtCamera=1 (the view
bike moved to the camera's own place of the frame) Fov=0 (CMB_ViewFov left alone: the game's own FOV); [Diag]
ViewLock=1`, and two `  sound (2026-11-14a, test 53): HeardKeep=1 HeardCreep=0.3 LiftDown=0.08: ...` and `  sound
(2026-11-14a, test 53): MenuQuiet=1 MenuQuietOut=0.15 MenuQuietIn=0.3: ...`; the older lines now read `  view: Enabled=1
... EyeAt=(0, 1, 128) ...`, `  sound: ... Gears=410.6,636.4,954.5,1272.7,1626.4 ShiftRpm=3500 ...`, `  sound:
HeardRiseGears=2,0.79,0.65,1,1 ShiftGapGears=0,2,3,1.5: ... at least 1.25, 2, 3, 1.5 s in gears 1-4 ...`, and the
2026-11-10a and 2026-11-09a look lines say `CMB_LookOptions 32767 for the scripts`. No `kit:` line at all, and the MCM
still showing "Field of view riding in first person", mean an older ESP or MCM folder is loaded: stop and say so.

**Number keys at speed** (steps 1-4; test 53: no `quick:` line ever came, because the game gives a key as its Windows
key code, 0x31 for number key 1, where the plugin looked for scan codes)

1. **A stimpak by its number key**: a stimpak on number key 1, Jet on another number key. At full speed press 1 three
   times, a second apart, then Jet's key once. Is each used at once, with no animation and no slow-down?
   - `CMB_Slope.log`, each press: `quick: key 0x31 (the slot 1, the game's 'Quickkey1') at 812 u/s: Stimpak (00023736, a
     potion) handed to the script's watch, not the game's animated use (allowStimpakUse 1): CMB_RiderQuickUse 17`. The
     log now names a key by the game's own code in hex: number key 1 is 0x31, 2 is 0x32 and so on to 9 = 0x39, 0 is
     0x30, - is 0xBD and = is 0xBB. `Papyrus.0.log`: `Used [Form <Stimpak (00023736)>] by its hotkey at speed: equipped
     by the script (QuickUse, slot 1).` and `Used [Form <Stimpak (00023736)>] while riding.`
   - The self-test (send every one of these lines): at the first ride `quick: self-test: the live singleton ...` and
     `quick: probe: ...`; `input: the first movement key from the game: 'Forward' 0x57 (...): the game's key codes are
     virtual keys (QuickProbe)` (0x11 there instead would mean scan codes after all: say so); each ride `quick:
     self-test: in N s: ...`, which should end `the favourites' handler is reached (its input handling on, +0x18: 1)
     (QuickProbe)` (`... NOT reached through its vtables ...` is a finding, not a failure of yours); `quick: the first
     quickkey event through OnButtonEvent: 0x31 'Quickkey1' ...`; at each ride's end `quick: this ride: 3 number-key
     press(es) by the keyboard's own state ..., 9 through OnButtonEvent (presses 3, holds 3, releases 3; taken 3, the
     game's 0) ...`; and any `... NOT through OnButtonEvent ...` line.
   - With an animation mod's decoration after the use: `rider: an item's use clip at N u/s (its props, ..., this frame;
     the script's hand-over 0.3N s before them, CMB_RiderQuickUse 17): IdleStop sent to the graph (UseStop): taken; ...`
     (the short dip as from the Pip-Boy).
2. **The bike's hotkey: 0 or B?** Get on and get off once each with the bike's own F4SE hotkey, the way you always do,
   and tell us which key you pressed. `quick: the bike's hotkey CMB_HotkeyCode 48: ...` once, then at each ride's start
   and end `quick: the ride began 1.92 s after the 0 key (0x30) went down, ...: CMB_HotkeyCode 48 is pressed as a
   virtual key, as F4SE gives it (QuickProbe)`, or `... after the B key (0x42) ...: ... as a DirectInput scan code`.
   (The MCM's help says "48 = B"; if the log says 0, that help is wrong and a later build fixes it. A press of the 0 key
   that is also a potion's slot 10 says `(also the bike's hotkey: CMB_HotkeyCode 48)`.)
3. **When the plugin can't take the key** (an A/B): `[Steer] QuickUse=0`, get on, ride fast, press the stimpak's key
   twice quickly. Two heals, no slow-down? Then Jet once: one dose, not two?
   - `CMB_Slope.log`: `rider: an item's use clip at N u/s (its props, ..., this frame; number key 0x31 (the slot 1) 0.3N
     s before them, not taken from the game): IdleStop sent to the graph (UseStop): taken; ...`, then `quick: number key
     (0x31, the slot 1) at N u/s: Stimpak (...) not taken from the game, its use clip cut at the props before the item
     came: handed to the script's watch to use it (QuickCut): CMB_RiderQuickUse -N`. `Papyrus.0.log`: `Used [Form
     <Stimpak ...>] by its hotkey at speed: its use clip was cut before the game used it: equipped by the script
     (QuickCut, slot 1).` For Jet, `Not used again: [Form <Jet ...>] by its hotkey at speed: the game used it itself
     (QuickCut, ...)` is the script holding back a second dose.
4. Also `QuickCut=0` (QuickUse still 0), get on, a stimpak by its key at speed: about a second of the use animation,
   then it stops. Healed? The speed held? `rider: an item's use clip at N u/s (its props, ..., this frame): no item used
   yet (...): left to play until it is, 3 s at most (UseStopUnapplied)`, then `rider: an item's use clip at N u/s (the
   item used N s into its clip, CMB_RiderItemUse N; its props, ...): IdleStop sent to the graph (UseStop): taken; ...`.
   Then put `QuickUse=1` and `QuickCut=1` back.

**Free colour in third person** (steps 5-6; test 53: blue in third person on every ride but the one the game loaded
into)

5. **Free colour, ridden**: choose Free colour with a hue other than 210 (at 210 blue is the right colour), for example
   126 (green), and a plate with coloured letters and background; Apply. Get on in third person by the hotkey and by E,
   and watch the paint and the plate from the first moment you see the bike. Is it your hue from the start, on every
   ride? Ride, get off, get on a few times, and once after changing only the hue in the MCM (Apply). Switch to first
   person and back: the same colour both ways? Once, load a save made while riding in third person: right?
   - `Papyrus.0.log`: `Look: the worn bike's colour indexes before its equip (WornIndex): Paint 4 of 4 set Plate 2 of 2
     set Plate text 2 of 2 set, colours: paint 0.337402 rims -1 plate 0.267578 text 0.218750` (later rides `... Paint 4
     as they were ...`), and `Look: the worn bike's colours are in its mods' swaps before the equip (WornIndex): no F4SE
     swap after the fade`.
   - `CMB_Slope.log`: `look: CMB_BikeWornRiderF_static_paint colour 0.3374 written (read back 0.3374; the paint); was
     0.3374 already, N passes built before it` means the game built the paint with your colour; `...; was 0.3960, ...`
     means it didn't. Send the two lines `look: the worn paint's passes 0.5 s on: ...` and `... 2.0 s on: ...` of a blue
     ride and of a right one.
   - After the hue-only change: does getting on take the usual time, not about a second longer? `Look: the worn bike's
     kept mods (the look unchanged): no attach` and no `Look: 7 of 7 mods on the worn bike`.
   - Only if third person is still blue (or the old hue): `[Look] Repass=1`, get off and on. Right now? `look: Repass:
     BSShaderUtil::ClearRenderPasses (Address Library 2317600) at +0x21C8CA0, as F4SE 0.7.9 has it`, then `look:
     CMB_BikeWornRiderF_static_paint: its render passes cleared after the write (Repass: ...)`. If the game crashes with
     it, say so. Put it back to 0.
6. **The Palette test paint ride**: at the field kit choose Paint "Palette test: colour index" and ride in third person:
   is the bike cobalt (a strong blue) or primer grey? `CMB_Slope.log`: `look: the worn paint not written (CMB_LookPaintV
   -1: Paint isn't Free colour): CMB_BikeWornRiderF_static_paint's material holds 0.4609 (...)`: 0.4609 means the game
   put the swap's own colour on the ridden bike (what the Free colour fix relies on), 0.6641 that it didn't. Then back
   to Free colour. Optional A/B: `[Look] WornIndex=0`, get on: third person blue again as in test 53 (that proves the
   fix), with `Look: the worn bike's colour indexes put back as the ESP has them (WornIndex off): ...` once; then 1
   again.

**First person** (steps 7-8; test 53: "the bike was shaking violently", "sitting on the fuel tank", and the FOV slider
to go)

7. **Steady, and the eye further back**: ride in first person for 2-3 minutes on a flat road, standing still on a slope,
   and through turns. Does the bike still shake? Do you sit in the right place now, over the seat with the tank in front
   of you? If you still sit too far forward or back, try the MCM's "Eye forward on the bike" and tell us the number you
   like. Park on a slope in first person (the bike leaning back or forward): the bars and the dial should stay still in
   front of you, the ground tilting under the bike.
   - `CMB_Slope.log`: `camera: FirstPersonState (vtable +0x...): GetTranslation (slot 0xD, +0x...) wrapped ([View]
     Camera; EyeAtCamera=1: the view bike moved to the camera's own place of each frame)` once, at the first
     first-person frame on the bike (send instead any `... not wrapped`, `camera: GetTranslation not called in 1.0 s
     ...` or `camera: EyeAtCamera off this session: ...`); the eye line every 2 s ends `; on the bike as tilted (pitch
     P, roll R, lift L) the eye at (0.0, 1.0, 128.0) (EyeLock: EyeAt held there)`; and every 2 s a `view: lock: the last
     2.0 s (N frames): ...` line: send them (its last figure, `the camera root N at most from that place at the next
     task`, near 0 means the bike follows the camera's own place of each frame).
   - A/B, one ride each: `[View] EyeLock=0` (2026-11-10a's view: does the shake come back?); then EyeLock=1 with
     `EyeAtCamera=0` (worse at full speed?); then `EyeAxes=0`. Which felt steadiest? Optional: `EyeAt=0,12,128`
     (2026-11-10a's seat place) for one ride, to compare. Put them back.
8. **The FOV is gone**: the MCM's Riding page no longer has "Field of view riding in first person", and first person
   keeps the game's own field of view. There is no `camera: the world FOV` line in the session; if your save had the
   slider set, `view: CMB_ViewFov 90 (an older save's riding FOV) left alone: [View] Fov=0, the game's own FOV (1 =
   used, as 2026-11-10a)` once. Nothing to do but look.

**The field kit** (steps 9-10; test 53's wishes: the item read "Default", a tyre filled the preview, the slots had no
names, and the kit only in your settlements)

9. **Its name, its slots and the preview**: in Sanctuary choose Customise at the parked bike. Take a screenshot as the
   armour menu opens, and one after picking a paint and a rim. Then zoom all the way out with the mouse wheel and all
   the way in (the plugin logs it). Is the item called "Motorbike"? Do the slot rows read "Paint: Factory", "Rims: ...",
   "Tank L: ..."? Does the whole bike show, turned three-quarters? (It may be small: zoom in.)
   - `CMB_Slope.log`: `kit: the preview's transform written (the new one): pos 0,0,0, turn 0,0.02,44.764, scale 0.3,
     zoom -1..1 (it was pos 0,0,0, turn 0,0,135, scale 0.45, zoom 0.5..1.5)` once at the start; `kit: the preview's
     record CMB_BikeLookPreview (...)` and four `kit: the game's preview transform ...` lines; at Customise `kit: the
     menu's 3D: item ...` and, while you zoom, `kit: the menu's zoom settled at ...`. Send them all: they tell the next
     build which numbers the game uses.
   - Only if the bike isn't whole or well placed: the MCM's "Field kit preview" section, "Tune (the sliders below)";
     move "Preview size (%)", "Preview turn", "Preview up / down" and the two zooms; leave the MCM and Customise again.
     Which values looked right? `kit: the preview's transform written (the MCM's sliders): ...`.
   - A/B: "Field kit preview" "As before": 2026-11-10a's view (the tyre) again, `kit: the preview's transform written
     (back to the ESP's): ...`. Then back to "New".
10. **Only in your settlements**: Customise in Sanctuary works as before (`Customise: in your settlement (its workshop
    151806): the field kit allowed (CMB_KitWhere 1).` in `Papyrus.0.log`). Park on a road outside any settlement and
    choose Customise: a message "The field kit works only in your settlements." and nothing comes out of the side bag
    (`Customise refused: not in one of your settlements (no settlement location): the field kit is for your settlements
    only (CMB_KitWhere 1).`). Then the MCM's Look "Field kit only in your settlements" off, the same spot: the kit
    opens, parts from the side bag as before. The MCM's "Free customising" with "Apply the look" on the road: the look
    changes (it works anywhere). Put the switch back on.

**The engine** (steps 11-12)

11. **Silence in the Pip-Boy and the pause menu**: at full speed open the Pip-Boy for 3 s, then close it; then the same
    with Esc. The engine should go quiet within a moment of opening and come back at the same note after closing. Once
    riding through water: is the water sound quiet in the menu too? (The start and stop sounds are unchanged.)
   - `CMB_Slope.log`: `sound: held at gear 3, 2084 rpm, heard 800 u/s while a menu pauses the game (UI menu mode 1); the
     loops out over 0.15 s (MenuQuiet)` at the open, then `sound: resumed after 3.1 s: gear 3, ...; the held 800 u/s fed
     0.25 s (the reading back to 721); the loops back over 0.30 s from the close (MenuQuiet)` (numbers for
     illustration). If you still hear the engine in the menu with these lines there, the game keeps the sound's level
     while paused: say so. A/B: `[Sound] MenuQuiet=0`.
12. **The gears**: from a stop, full throttle to the top speed: five gears, each change higher than before (about
    3200-3400 rpm, into 5th about 2500), the note rising all through 2nd and 3rd, a short 4th, then the cruise as
    before. Pull away and tap off the throttle briefly in 2nd while the bike is still speeding up: the note shouldn't
    drop or blip down to 1st. Ride steadily at about a quarter of the top speed and let go of the throttle for a moment:
    no down-and-up blip. A normal stop from speed: the down-shift blips as before.
   - `CMB_Slope.log`: `sound: gear 2 at ...` up to `sound: gear 5 at ...`; no `gear 1 ..., a blip` right after a `gear
     2` line with the bike faster; the trace's engine word ` keep` while the note is held up; after each getting off
     `sound: generation N's ride: the note held N times for N s while the bike gained (HeardKeep), N lift down-shift(s)
     held back (LiftDown); ...`.
   - Tell us: do the higher shifts and the short 4th sound right, or too busy? Does the throttle-off sound at the top of
     a pull sound stretched (its loop is pitched up further than before)?
   - A/B: `[Sound] HeardKeep=0` (the note may sag while the bike gains), `LiftDown=0`; 2026-11-10a's gears all together:
     `ShiftRpm=2500`, `Gears=555.556,750,960,1161.6`, `ShiftDraw=2300,3000`, `HeardRiseGears=2.5,0.95,0.5,1`,
     `ShiftGapGears=0,2,3`, `LaunchRise=350`, `LaunchFlare=0.5`; milder shifts with the new gears:
     `ShiftDraw=2900,3400`.

**Asked again: what test 53 didn't try** (steps 13-14)

13. **The guard beside a downed NPC** (2026-11-10a's step 8): knock an NPC down beside the parked bike and get off next
    to them: the bike stays hidden until they stand up. `CMB_Slope.log`: `room: ask N at (...), heading H (the parked
    bike's place: ParkGuard): someone in it: XXXXXXXX (skeleton.nif, layer 8: a body, no capsule met), ...` (a standing
    one: `(..., layer 30)`). Also get off beside a dog or a crouching NPC (`... someone in it: ... (the ground taken at
    the bike's place: the ray stopped 61 over it, on the bike)` after the settle), and on a bridge over someone, the
    bike's spot well under you: it shows (`... no one in it (21 rays down, 16 across); the player 312 above it: not
    counted (GuardPlayerZ)`).
14. **The A/Bs**: one at a time, each for a ride or two, then put it back. Each gives one part of 2026-11-10a (or of an
    earlier build) back, so you can tell whether that part's change is what you notice:
   - `[Look] MountEarly=0`: getting on as 2026-11-09a, the screen back only at "Mounted." (is today's about 2 s really
     quicker?);
   - `[Room] GuardBodies=0`, with step 13: the bike shows while the NPC lies there;
   - `[Steer] SidestepCaution=0`: Caution 50's sidestep at its own reach (does it find posts later?);
   - `[Sound] MenuHold=0`: the engine steps on, silent, through a menu, so it comes back in 1st after the close (test
     52's drop);
   - `[View] EyeLock=0` (step 7), `[Steer] QuickUse=0` (step 3), `[Look] WornIndex=0` (step 6), `[Sound] HeardKeep=0`
     (step 12), if you haven't already.

The off values, each giving 2026-11-10a: `[Steer] QuickKeyCodes=scan`, `QuickKeyState=0`, `QuickCut=0`,
`UseStopUnapplied=cut`; `[Diag] QuickProbe=0`, `WornPasses=0`, `HandoverFromReady=0`, `ViewLock=0`; `[Look]
WornIndex=0`, `KeptMods=0`, `Repass=0` (its default), `KitPreview=0`, `KitPreviewLog=0`; MCM "Field kit only in your
settlements" off, "Field kit preview" As before; `[View] EyeAt=0,12,128`, `EyeLock=0`, `EyeAxes=0`, `Camera=0`,
`EyeAtCamera=0`, `Fov=1` (with `set CMB_ViewFov to 90` in the console: the MCM slider is gone); `[Sound] MenuQuiet=0`,
`HeardKeep=0`, `LiftDown=0`, and the gears as in step 12. The item's and slots' names have no switch (an ESP built with
the generator's `--kit-names 0` has 2026-11-10a's; it isn't in the package). The 2026-11-10a build's own switches back
to 2026-11-09a's are all still there.

Send both logs a session, any crash log, the screenshots of step 9, and a video if you have one.

### Questions for you (test 54)

- **T54-1 (step 1).** A stimpak by its number key at speed: used at once, no clip, the speed kept? Jet too?
- **T54-2 (step 2).** Which key do you press for the bike's hotkey, 0 or B?
- **T54-3 (steps 3 and 4).** With QuickUse off: healed each time, one Jet dose? With QuickCut off too: healed after
  about a second of the animation?
- **T54-4 (step 5).** Free colour right in third person from the first moment, on every ride? The plate? After a load?
  Getting on as quick after a hue change?
- **T54-5 (step 6).** The Palette test: cobalt or primer grey?
- **T54-6 (step 7).** First person: any shake left? Your seat place right (or the "Eye forward" number you like)? Which
  A/B was steadiest?
- **T54-7 (step 9).** The item "Motorbike", the slot names, the whole bike in the preview? If you tuned it, which
  values?
- **T54-8 (step 10).** Refused on the road, allowed in Sanctuary, and anywhere with the switch off?
- **T54-9 (step 11).** The engine and the water quiet in the Pip-Boy and the pause menu, and back at the same note?
- **T54-10 (step 12).** The five gears: the higher shifts, the short 4th, no drop on a lift, the throttle-off sound?
- **T54-11 (step 13).** The bike hidden while a knocked-down NPC lay in its place?
- **T54-12 (step 14).** Anything an A/B made better or worse?

## The 2026-11-10a build: test 52's fixes, in this order

This is the fixes build for test 52 (run on 2026-11-09a: the field kit's menu shut by Global Stash by SKK, items by
hotkey at speed never used, getting on 3-5 s, Free colour blue on the first ride, the engine silent after getting on,
Caution 50's sidesteps, the parked bike's guard, first person still unseen, the FOV, the tip after a load and the
engine through the Pip-Boy) and for its wishes: the front wheel's shadow, 3rd gear about 3 s and the gentle water
louder. What test 52 liked is as it was: the driving feel, the sidestep, the take-off, the power-attack switch, the
chrome, the whole look, 2026-11-09a's gears and its quick getting on. Steps 1-18 in this order; each names the log line
that answers it, and every new behaviour has an off value that gives the 2026-11-09a build back (README's first key
table), so each A/B is one key or one MCM setting away. Four steps settle what only the game can: the slot each number
key uses (step 3), the Free colour diagnostic (step 5), the first-person diagnostic (step 9) and the paused-engine
diagnostic (step 18).

Before you start:
- install as a Replace (2026-11-10a over 2026-11-09a); F4SE and `CMB_Slope.dll` as before. Reset nothing: a new save
  starts at Riding "Caution" 50, but your save keeps its own (60 if you never moved it): set it to 50 by hand for step
  6;
- keep Global Stash by SKK installed (step 4), and play with `CMB_AllowCombat` as you usually do (step 2);
- copy both logs aside before every quit (`CMB_Slope_stepN.log`, `Papyrus_stepN.log`): the plugin keeps only one
  earlier session;
- the 2026-11-09a build's steps (the next section) were test 52's: no need to run them again.

The log's first lines: `CMB_Slope.log` has `globals: the 2026-11-10a build's 2 found, CMB_RiderQuickUse and CMB_RideReady
(FE005BF5-FE005BF6)` (the FExxx part is your load order's) and five settings lines more than before:
`  look (2026-11-10a, test 52): KitStash=1 KitRetry=1 MountEarly=1 WornColoursFirst=1 HueSwap=1 RideReady=1; [Diag] WornColour=1:
CMB_LookOptions 4095 for the scripts`, `  rider (2026-11-10a, test 52): QuickUse=1 QuickUseAbove=150
QuickKeys=2,3,4,5,6,7,8,9,10,11,12,13 UseStopCue=props UseStopNotUnder=WEAPON UseStopAt=props`, `  drive (2026-11-10a,
test 52): SidestepCaution=60 SidestepMouse=5; [Room] GuardBodies=1 GuardFloor=1 GuardPlayerZ=150`, `  view (2026-11-10a,
test 52): Parent=1 Update=1; [Diag] ViewDrawEvery=10 ViewThird=0 ViewThirdOffset=150` and `  sound (2026-11-10a, test
52): MenuHold=1 MenuRejoin=1.0; [Diag] Paused=1; [Fx] WaterGentleDb=+0 dB`; the 2026-11-09a lines now read `  view
(2026-11-09a): TipMenu=1 TipYield=15 TipSettle=0.25 Bounds=1 Near=0 FovSearch=2; [Diag] ViewDraw=2`, `  sound:
HeardRiseGears=2.5,0.95,0.5,1 ShiftGapGears=0,2,3: ... at least 1.25, 2, 3 s in gears 1-3 before an up-shift (0 or
missing: MinShiftGap)` and `  look (2026-11-09a fixes): ... LightingOnly=1: CMB_LookOptions 4095 for the scripts (64: the
worn bike's colours written here)`. A line `globals: no CMB_RiderQuickUse or CMB_RideReady (0xBF5-0xBF6, an older ESP):
QuickUse and RideReady do nothing` means an older ESP is loaded: stop and say so.

1. **Getting on** (test 52: 3-5 s from the press to riding, the screen black for 3.0-3.6 s of it): five times by the
   hotkey and twice by E (the bike's menu, Ride). How long is the screen black, and the press to riding, by feel?
   - `Papyrus.0.log`, at each getting on, the stage times from the press (by E, the menu's Ride): `Getting on: the
     press 0.00, the fade 0.31, the equip 1.12, the pose 1.40, ready 1.92 (CMB_RideReady after 0.80 s), the screen back
     1.95, Mounted 2.66 (real seconds)`. The black is from just after "the fade" to "the screen back": estimated at
     about 1.1-1.3 s with the stock look and 1.6-2.1 s with a full look; this line shows the real split.
   - `CMB_Slope.log`: `getting on: the bike ready 0.25 s after CMB_TiltLive (50 shapes held, 3 colours written, the
     rider on the seat): CMB_RideReady 1`, and no `tilt: a second into the ride and no bike shape found` (test 52's
     false alarm: the count now starts at `CMB_TiltLive`).
   - Send any `getting on: the bike not ready 1.0 s after CMB_TiltLive (...)` line (it names what was missing) and any
     `ready ... (no CMB_RideReady within MountReadyWait, 1.0 s)`. A follower is stowed and the headlamp lit up to about
     a second after the screen is back: anything odd there?
   - Once with the MCM's "Bike tilts with the ground" at 0: does the screen come back as fast as at 45? `CMB_Slope.log`:
     `getting on: the bike ready ... s into the ride, the MCM's tilt 0 (... the rider not held (the MCM's tilt 0), the
     knees on the seat): CMB_RideReady 1` (not `getting on: the bike not ready 2.0 s into the ride, the MCM's tilt 0
     (...)`). Put the tilt back.
   - A/B once: `[Look] MountEarly=0` (2026-11-09a's getting on, the screen back at "Mounted.").
2. **Items at speed**, at full speed: a stimpak by its number key three times, then a second potion (Jet) on another key.
   Is each used at once? Any clip? Does the bike keep its speed?
   - `CMB_Slope.log`, a press: `quick: key 2 (the slot 1, the game's '...') at 812 u/s: Stimpak (00023736, a potion)
     handed to the script's watch, not the game's animated use (allowStimpakUse 1): CMB_RiderQuickUse 17`;
     `Papyrus.0.log`: `Used [Form
     <Stimpak (00023736)>] by its hotkey at speed: equipped by the script (QuickUse, slot 1).` and `Used [Form <Stimpak
     (00023736)>] while riding.`. The log names a key by its scan code, not its label: number key 1 is scan code 2 (`key
     2`), number key 2 is `key 3`, and so on (0 is `key 11`); the slot is the key's own number.
   - With an animation mod's decoration after the use: `rider: an item's use clip at N u/s (its props, <shape> < <node>
     < <node>, this frame): IdleStop sent to the graph (UseStop): taken; the clip over after N s, the speed N` (a dip of
     about 100-150 u/s for about 0.3 s, as from the Pip-Boy: acceptable?).
   - A press under 150 u/s: `...: under QuickUseAbove 150: the game's own hotkey use (QuickUse)` and the game's clip as
     before. A stack's last one: `Not used: [Form <...>] by its hotkey at speed: none left, the stack's last one gone
     (...)` or the plugin's `the slot empty` line.
   - A press at speed right as the screen comes back after getting on (if you are past 150 u/s by then), before the
     hotkey script's watch is on: the game's own use, with its clip (`quick: key 2 (the slot 1, the game's '...') at ...
     u/s: 00023736, a potion, but the script's watch not on yet (CMB_RiderQuickUse 0): the game's own hotkey use
     (QuickUse)`); the next press a second later is the script's (`handed to the script's watch`, and `Used ...
     equipped by the script` in `Papyrus.0.log`).
   - Then the same potion from the Pip-Boy at speed, for comparison.
   - A weapon drawn at speed: it draws, with `rider: new shapes <shape> < WEAPON < RArm_Hand, under WEAPON: a weapon's, no
     item's cue (UseStopNotUnder)` and no IdleStop line.
   - A/B: `[Steer] QuickUse=0` (2026-11-09a: the game's animated hotkey use).
3. **The quickkey slot mapping** (only the game can say): favourite three different potions on number keys 1, 2 and 5,
   with 3 and 4 left empty; press each at speed. Does each `quick: key N (the slot M, ...)` line name the potion on that
   key (number key 1: `key 2 (the slot 1, ...)`; 2: `key 3 (the slot 2, ...)`; 5: `key 6 (the slot 5, ...)`), and is
   that the one used (Papyrus's `Used ... by its hotkey ...` names the same item)? Number key 3 at speed: `quick: key 4
   (the slot 3, ...) at ... u/s: the slot empty: the game's own hotkey use (QuickUse)`. Send the session's first `quick:
   FavoritesManager (Address Library 4801690) +0x...: its OnButtonEvent wrapped (QuickUse; ...)` line, or its `quick:
   FavoritesManager (Address Library 4801690): <why>: nothing wrapped, the hotkeys are the game's own (QuickUse)` line.
   No `quick:` line at all for a number key while riding means the plugin never sees the keys: send the log.
4. **Field kit** (automatic, Customise at the parked bike), once in one of your settlements and once outside. Does the
   menu stay open? Which mode worked?
   - `Papyrus.0.log`, with Global Stash by SKK: `Field kit: Global Stash by SKK: the kit linked to its stash first
     (SKK_GSSKeyword ..., the stash ...; its auto transfer on): its workbench handler leaves the kit alone` (outside a
     settlement `...; its standalone workbench link on): ...`, or `Field kit: Global Stash by SKK: its standalone
     workbench link off: not linked (it won't touch the kit)`), then `Field kit: mode 3: the kit's link at the
     activation: the stash` (or `...: the settlement's workshop N: relinked after its load`), `Field kit: mode 3: the
     menu open after 0.1 s, the player in the kit` and at the close `Field kit: mode 3 worked (its menu open ... s):
     remembered (CMB_KitWorked 3)` (or `(a change made)`).
   - Is there any `SKK_GSSMainScript.TransferFrom` line after the link line? (There shouldn't be.)
   - Then once with `[Look] KitStash=0` (save the INI, reload the save): kicked as in test 52, then `Field kit: mode 3:
     the menu closed 0.17 s after it opened, no change: under KitFastClose 0.5 s, the player in the kit at its open
     doesn't count: the kit used again (KitRetry), enabled again after ... s` and the menu opens again and holds. If it
     is kicked again instead: `Field kit: mode 3: the menu closed again ... s after it opened, no change: ...: used
     again once already (KitRetry): this mode doesn't work here` and `...: trying mode 4`. Send the lines; put KitStash
     back to 1.
5. **Free colour** (test 52: blue ridden after an Apply, red parked): an MCM hue change, Apply, the first ride. The
   colour from the start, or a change within a second or two (HueSwap)? The plate right on that ride?
   - `Papyrus.0.log`: `Look: Free colour on the worn bike: the plugin writes it, and the F4SE swap once after the fade
     too (HueSwap)`, then `Look: the worn bike's colours: N entries applied (F4SE) ...`.
   - **The Free colour diagnostic**: send the `look: the worn paint 0.5 s on: ...` and `look: the worn paint 2.0 s on:
     ...` lines, e.g. `look: the worn paint 0.5 s on: CMB_BikeWornRiderF_static_paint the shape ... under the 3D root,
     its property the same, its material the same (...paint_hue_p.dds, 0.4995; written 0.4995); 1 static_paint
     shape(s) under the 3D root, 1 through the biped (1 in all)`: one static_paint shape or two, the material the same
     or changed? With HueSwap on, `its material another (...)` at 2.0 s can be the swap's own; for the cause, ride once
     with `[Look] HueSwap=0`: two static_paint shapes, "another" material or "not under the 3D root" then point at the
     paint drawn not being the shape written.
   - A/B: `[Look] WornColoursFirst=0` (the old order: the previous look's colour first).
6. **Caution 50** (a new save gets 50; your save keeps its own: set 50 on the MCM's Riding page). Ride at posts,
   mailboxes and lamps as in test 52 (8 sidesteps of 27 there): do the sidesteps come as they did at 60?
   - A sidestep that Caution 60's reach found has, right after its start line (`sidestep: <thing> (layer N) narrow D
     past the front wheel at V: to the ...`), `sidestep: <thing> at D (found by Caution 60's reach, SidestepCaution; the
     throttle Caution 50's): the rays to R past the front wheel, Caution 50's own to r`. The throttle still eases at 50's
     distance (`rays: a wall ahead ...` no further than r).
   - A mouse move under 5 degrees keeps a sidestep; a bigger one: `sidestep: let go after ... s: the game's own target
     moved N deg (the mouse) ...`.
   - The bridge's rail still stops short (`...: WallStop, Caution 50%)`).
   - A/B: `[Steer] SidestepCaution=0` (2026-11-09a's Caution 50).
7. **The front wheel's shadow** (test 52's wish): in sunlight, Customise, Rims "Star five" in any finish (both wheels),
   leave the kit. Stop with the sun to one side and look at the ground beside the bike, ridden (third person) and then
   parked: do the front wheel, the fork and the bars cast a shadow when ridden, as the parked bike's front end does?
   Then the stock rims (Rims "Stock (cast)") once, ridden. A screenshot of each: there is no log line, the picture is
   the answer. At night with the headlamp on (MCM "Headlamp casts shadows" on, `[Lamp] Ahead` 28, the default): is the
   beam still clear of the bike's own shadow?
8. **The guard**: knock an NPC down beside the parked bike and get off next to them: the bike stays hidden till they
   stand up: `room: ask N at (...), heading H (the parked bike's place: ParkGuard): someone in it: XXXXXXXX
   (skeleton.nif, layer 8: a body, no capsule met), ...` (a standing one: `(..., layer 30)`). Get off beside a dog or a
   crouching NPC: after the settle `... someone in it: ... (the ground taken at the bike's place: the ray stopped 61
   over it, on the bike)`. Get off on a bridge over someone, the bike's spot well under you: `... no one in it (21 rays
   down, 16 across); the player 312 above it: not counted (GuardPlayerZ)`.
9. **First person** (the first-person diagnostic): stopped right after getting on, then riding a few cells. Is any of
   the bike visible? A screenshot either way.
   - Send every `view: drawn? the flags: ...`, `view: drawn? the fade node: ...`, `view: drawn? the cell's multibound:
     ...` and `view: drawn? the player's cell: ...` line (at each first person's first frame, then every 10 s; an
     unchanged chain is one `view: drawn? the chain as before (...)` line), every `view: Parent: ...` line (`view:
     Parent: the view bike's 3D moved from ... to the player's cell ...'s (it showed outside by N of its own cell's
     box), for the reference FFxxxxxx`) and any `view: the game's update put the view bike's root N from ours ...:
     [View] Update off this session` line.
10. Only if step 9 showed nothing: `[Diag] ViewThird=1`, get off and on, third person: is a second bike 150 to your
    right? (`view: third person: the view bike shown 150 to your right ([Diag] ViewThird): is a second bike there?`.)
    Then back to 0.
11. Only if step 9 showed the bike: `[View] Parent=0`, get off and on, look again; then `Parent=1` with `Update=0`. Which
    lever did it?
12. **Parent's safety**: in first person on the bike, go through a door (an interior), fast travel, quicksave and
    quickload, ride across several cells. No second bike left behind, no crash? `view: Parent: put back under its own
    cell (...)` at each (a load: `(a load (PreLoadGame))`, third person: `(third person)`, getting off: `(got off)`, a
    handover: `(a handover)`, a cell crossed: `(the player's cell is another now)`, then `view: Parent: the view bike's
    3D moved ...` again). Any `view: the reference ... own cell is gone ...` or `view: Parent: 21 moves in ... s (more
    than 20 in 10 s): [View] Parent off this session` line?
13. **FOV**: MCM "Field of view riding in first person" 90, first person for 2 s: wider? `camera: the world FOV at
    PlayerCamera+0x168 (the layout's worldFOV: 80 = the frustum's 80.0 across; firstPersonFOV +0x16C 80), 0.51 s into
    first person (FovSearch=2)`, then `camera: the world FOV at PlayerCamera+0x168 (...): followed, kept (...)`, or
    `camera: PlayerCamera+0x168 not followed (...): put back; +0x16C at the next entry` and at the next entry the same
    for +0x16C.
14. **The tip**: into first person moving the mouse as you do, also right after a load: the view eases 20 degrees down
    unless you really look away (`view: looked 20 deg down on getting into first person (from ...; your own look N deg
    up on top; the camera now ...)`; a real look: `view: you looked yourself N deg up over ...`).
15. **The Pip-Boy at speed**: at full speed open the Pip-Boy for 3 s, close it: the engine note goes on, no take-off
    sound. `sound: held at gear 3, 2315 rpm, heard 891 u/s while a menu pauses the game (UI menu mode 1)` at the open,
    then `sound: resumed after 3.1 s: gear 3, 2320 rpm, heard 893 u/s; the held 895 u/s fed 0.40 s (the reading back to
    810)`, and no `sound: gear 1 at ... (clutch in)` between (numbers for illustration). A/B: `[Sound] MenuHold=0`.
16. **Gears**: full throttle from a stop: 3rd about 3 s (`sound: gear 3 at ...` to `sound: gear 4 at ...`). Brake hard
    in 3rd and pull again: is the climb back fine (0.5 s longer than 2026-11-09a's)? A/B: `[Sound]
    ShiftGapGears=0,2,2.5`.
17. **Water** at speed on "Wet road, gentle": louder than 2026-11-09a's, still not hissy? `fx: the water loop (id N)
    driven (CMB_FxDriven N): ...; the gentle wet road (CMB_FxWaterLoop 3), WaterRoadDb +0 dB, WaterGentleDb +0 dB`.
    A/B: `[Fx] WaterGentleDb=-3` is 2026-11-09a's level.
18. **The paused-engine diagnostic** (test 52: the engine silent 16-20 s after getting on): right after getting on,
    Alt-Tab out for 10 s and come back; once, open the pause menu for 10 s. `game: the window out of focus
    13:42:33.7-13:42:43.8 (10.1 s)`, `game: the world paused 13:44:02.1-13:44:12.3 (10.2 s: the movement update 0
    times)`, `game: the frame task didn't run for 6.97 s (13:42:33.66)` (a minimised window); a late hand-over: `sound:
    generation N handed over 13.4 s after the ride's start (usually 3), 10.1 s of it paused or out of focus`. Is any
    silence after getting on now explained?

The off values, each giving 2026-11-09a: `[Look] KitStash=0`, `KitRetry=0`, `MountEarly=0`, `RideReady=0`,
`WornColoursFirst=0`, `HueSwap=0`; `[Steer] QuickUse=0`, `UseStopCue=any`, `UseStopNotUnder=` (empty), `UseStopAt=knees`,
`SidestepCaution=0`, `SidestepMouse=3`; MCM "Caution" 60; `[Room] GuardBodies=0`, `GuardFloor=0`, `GuardPlayerZ=0`;
`[View] Parent=0`, `Update=0`, `FovSearch=1`, `TipYield=5`; `[Diag] ViewDraw=1`, `ViewDrawEvery=0`, `WornColour=0`,
`Paused=0`; `[Sound] MenuHold=0`, `ShiftGapGears=0,2,2.5`; `[Fx] WaterGentleDb=-3` (2026-11-09a's level; 0 is its plugin).
`[Diag] ViewThird` is an A/B for step 10 only (0, the default, shows nothing). The front wheel's shadow has no switch:
2026-11-09a's meshes and materials give it back. The 2026-11-09a build's own switches back to 2026-11-08a's are all
still there.

Send both logs a session, any crash log, the screenshots of steps 7 and 9, and the video if you have one.

### Questions for you (test 53)

- **T53-1 (step 1).** Getting on quick enough: the black, and the press to riding?
- **T53-2 (step 2).** Items at speed: used at once, no clip, the speed kept? The dip after an item animation mod's
  decoration, if you have one: acceptable?
- **T53-3 (step 3).** Did each number key use the potion on it?
- **T53-4 (step 4).** Did the field kit's menu stay open? Which mode worked?
- **T53-5 (step 5).** Free colour right from the first ride?
- **T53-6 (step 6).** Caution 50's sidestep as good as 60's?
- **T53-7 (step 7).** The front wheel's shadow, ridden and parked?
- **T53-8 (steps 9-11).** First person: was any of the bike seen? (And step 10's or 11's answer, if it was asked.)
- **T53-9 (step 12).** Anything odd after a door, a fast travel or a load in first person?
- **T53-10 (steps 13 and 14).** The FOV wider? The tip kept when you move the mouse a little?
- **T53-11 (steps 15 and 16).** The engine through the Pip-Boy; 3rd gear's 3 s, and the climb back after a brake?
- **T53-12 (step 17).** The gentle water's level?
- **T53-13 (step 18).** Any silence after getting on, and were you in another window or a menu then?

From test 52's video (no new test needed; the clock is the video's time plus 13:15:17.4):
- **V1.** 13:55:50-13:56:30: is the worn bike's plate Army's or Nuka's? And from 13:47:25 on: Institute's or Army's?
- **V2.** 13:17:43-13:18:00 and 13:42:33-13:42:50: is the game in a menu or another window?
- **V3.** 23:11.6-23:15 in the video (13:38:29-32): is any of the bike, or its dial, on screen?

## The 2026-11-09a build: test 50's and test 51's fixes

This is the fixes build for test 50 (run on 2026-11-06a; the 2026-11-08a build changed only the look, so everything
test 50 found still held) and for test 51 (run on 2026-11-08a: the field kit, getting on, the parked bike's colours,
the black screen after Ride, Free colour, the gears, the Vault-Tec plate and first person after a load). What tests 50
and 51 liked is as it was: the sidestep, the take-off, the power-attack switch, the chrome and the whole C2 look. Steps
1-12 answer test 50, steps 13-21 test 51, in this order. Each step names the log line that answers it, and every new
behaviour has an off value that gives the 2026-11-08a build back (README's first key table; for the gears, step 18),
so each A/B is one key or one MCM setting away.

Before you start:
- install as a Replace (2026-11-09a over 2026-11-08a); F4SE and `CMB_Slope.dll` as before. Reset nothing: in a new save
  the MCM shows Riding "Caution (how early the bike eases off for obstacles, %)" at 60 and Sound "Water sound loop" on
  "Wet road, gentle"; a save from an earlier build keeps its own "Water sound loop" (2026-11-08a's default was "Wet road
  (the mod's own)"), so check both and set them by hand;
- MCM Riding "Power attacks throw you off" on for step 1 (its default is still off);
- copy both logs aside before every quit (`CMB_Slope_stepN.log`, `Papyrus_stepN.log`): the plugin keeps only one
  earlier session;
- the 2026-11-08a build's steps (the next section) were test 51's: no need to run them again, steps 13-21 answer what
  it found; in a save from an earlier build the field kit forgets a remembered toolbox once (step 15), and the first
  ride after installing attaches the look's mods once (step 13).

The log's first lines: `CMB_Slope.log` has `globals: the 2026-11-09a build's 2 found, CMB_Caution and CMB_ViewMenu
(FE055BF1-FE055BF2)` (FE055 in test 50's load order; yours may differ), `globals: the 2026-11-09a fixes' CMB_LookOptions
found (FE055BF4)` and one settings line a part: `  steer: Caution=-1: the MCM's CMB_Caution, read on getting on and once
a second while riding; ClimbStepSpan=3: ...`, `  parts: the wheels turn by the frame's own movement, none under 5 u/s
(WheelSpin), held while braking (WheelLock)`, `  rider: UseListen=2 UseStop=IdleStop,IdleForceDefaultState: ...`,
`  view (2026-11-09a): TipMenu=1 TipYield=5 TipSettle=0.25 Bounds=1 Near=0 FovSearch=1; [Diag] ViewDraw=1`, `  room:
SnapOrder=1: ...`, `  room: ActorRoom=1 ParkBack=1 ParkGuard=1 GuardMargin=15: ...`, `  sound:
HeardRiseGears=2.5,0.95,0.5,1 ShiftGapGears=0,2,2.5: ...`, `  look (2026-11-09a fixes): FastMount=1 KitHeld=1
ParkedReload=1 PaletteIndex=1 MountGuard=1 HueFree=1 Rehold=1 LightingOnly=1: CMB_LookOptions 127 for the scripts (64:
the worn bike's colours written here)` and `  view (2026-11-09a, test 51): TipLoadGrace=2 (a tip verdict within 2 s of a
load or getting on holds for that entry only; 0: for the session)`; at the first getting on `  steer: Caution 60%
(CMB_Caution): FaceLook 0.18, WallStop 0.75, WallStopPersist 0.09, the need from the 0.05 s speed`. A line `globals: the
2026-11-09a build's 0 of 2 found (0xBF1-0xBF2, an older ESP): none used` means an older ESP is loaded, and so does
`globals: no CMB_LookOptions (0xBF4, an older ESP): ...`: stop and say so.

1. **Fights and knock-offs** (test 50's crash came half a second after the third knock-off in 21 s, with raiders round
   the bike). With "Power attacks throw you off" on, get knocked off with raiders close, three times or more, and get
   back on quickly each time.
   - Expected: no crash, and the bike never appears inside anyone. `CMB_Slope.log`: `room: ask N at (...), heading N:
     none, an actor in its place: ... (ActorRoom)`, with the actor's reference ID, its model and which ray met it (`met
     by the ray down 37 ahead of its middle, 40 to its right`).
   - `Papyrus.0.log`: `The parked bike kept hidden: someone in its place (the plugin's [Room] ParkGuard): looked at
     again every 0.5 s.`, then `The parked bike shown after N s: its place clear (ParkGuard).` (after 15 s it tries a
     spot beside or behind you instead); `CMB_Slope.log` meanwhile `room: ask N at (...) (the parked bike's place:
     ParkGuard): someone in it: ...`, and at the end `...: no one in it (21 rays down, 16 across)`.
   - After a short ride, get off right where the bike stood with an NPC beside it: `The parked bike's old spot: none
     (an actor in its place).` and `Parked bike not put back where it stood: its old spot asked about first (the
     plugin's [Room] ParkBack): no room there (the line above says why): its spot asked about instead.`
   - Ride a bend and get off: the bike shows at once (`room: ask N at (...), heading N (the parked bike's place:
     ParkGuard, the player not counted): no one in it (21 rays down, 16 across)`). You no longer keep it hidden where
     the mod has just put it clear of you (getting off, calling it, bringing it, putting it back where it stood); while
     it is held for someone else you count only standing in its very place.
   - Known: if you go through a door or fast travel while the bike is kept hidden, it stays hidden where it waits until
     you call it (`The parked bike kept hidden after N s: the player went elsewhere: it waits there hidden; calling it
     brings it (ParkGuard).`). Getting on or calling it always ends the wait.
   - If the game crashes, send the crash log: the actor in it is compared with the last `room:` lines.
2. **Items at speed**: a stimpak by its hotkey at full speed, then one from the Pip-Boy (closed while still riding).
   - Does the bike keep its speed? Is the item used (health up)? Does the pose, the camera or a weapon do anything odd?
   - Log: `rider: an item's use clip at N u/s (...): IdleStop sent to the graph (UseStop): taken; the clip over after N
     s, the speed N` (or `...: not taken, IdleForceDefaultState taken; ...`, or `...: none taken: the clip plays
     (UseHold holds the throttle)`: then say what the clip did), and either way `rider: the graph's events through
     PlayerCharacter's slot 1 in the 2.0 s from ... (UseListen): ...`.
   - A/B: `[Steer] UseStop=` (empty: nothing sent, 2026-11-08a), get off and on.
3. **Caution**: the usual streets at 60 (the default), then 100 and 50 from the MCM while riding.
   - Each change is logged within a second: `steer: Caution 60% -> 100% (CMB_Caution): ... (the MCM)`. WallStop's lines
     end `..., Caution 60%)`.
   - Still over-cautious at 60? Does the front wheel ever touch a wall or a car (where, and at which Caution)?
   - At 60 the sidestep round a post or a mailbox starts later: the post is first read about 575 units past the front
     wheel instead of about 725 at 100 (70 to 100 gives that room back). Does it still step round in time (T52-1)?
4. **Wheels**: brake hard from full speed (back or the brake key): the wheels hold still till the bike stops. Roll to a
   stop off the throttle: they stop with the bike, no run-on. Reverse: they turn backward. Log: the `parts:` line above.
   A/B: `[Parts] WheelSpin=0` and `WheelLock=0` (2026-11-08a's wheels).
5. **The bridge's end post** (test 50's, 14:37:48) at full speed: no climb up the post into the rail; `climb: a low face
   at the capsule (...): ...: its top ends within N past its face (...), though a wheelbase on, N ahead, the ground N
   over its foot: a post, not a step (ClimbStepSpan): not climbed with the boost`. Kerbs and steps are still climbed
   with the boost (`... its top carrying on at 3 points between (ClimbStepSpan)`).
6. **The truck**: call the bike from the truck bed (test 50's). It should come beside the truck, on the ground: `The
   bike's spot: Bike's spot N's navmesh point (N from it), heading N: room, walkable (its own snap N): taken before the
   most room (spot N, none there) (the plugin's [Room] SnapOrder).` If it goes onto the truck again, send the call's
   `Papyrus.0.log` lines and the plugin's `room: ask` lines.
7. **The Pip-Boy from third person**, riding: open it and close it, three times. The view isn't pitched: `view: no tip:
   this first person began with the eye N from EyeAt (a menu's camera: the Pip-Boy from third person)` or `view: no tip:
   the Pip-Boy open (CMB_ViewMenu)`.
8. **Into first person moving the mouse a little**: the view eases 20 deg down with your own look on top (`view: looked
   20 deg down on getting into first person (from N deg down; your own look N deg down on top; the camera now N deg
   down)`); a bigger look, past 5 deg, takes over (`view: you looked yourself N deg up over N frame(s), ...`). Can you
   look as you like after?
9. **The view bike**, stopped and then at speed: look straight down, then 25-30 deg down. Is any of the bike visible
   (the dial, the bars, the tank, the mirrors)? Send screenshots; the `view: drawn? the chain: ...`, `view: drawn? the
   camera: ...` and `view: drawn? last frame's writes: ...` lines go with them. Only if nothing shows: `[Look] Cull=1`,
   get off and on, look again; if still nothing, `[View] Near=5`, off and on, again (`view: the camera's near plane 15
   -> 5 while the view bike shows ([View] Near)`). Put both back after. Each chain line now ends `, for the reference
   FFxxxxxx` (step 19).
10. **FOV**: MCM "Field of view riding in first person" 90; into first person for 2 s. Wider or not? Log: `camera: the
    world FOV at PlayerCamera+0x... (...), 0.50 s into first person (search 1 of 3)`, or at three entries `camera: the
    world FOV not found in PlayerCamera+0x40..+0x1AC (...): ...; candidates: ...`: send those lines.
11. **Gears**: replaced by step 18 (test 51 found 1st longer than both 2nd and 3rd; the lengths changed again).
12. **Water**: ride through shallow water at speed on "Wet road, gentle" (`Papyrus.0.log`: `Bike sounds: the plugin
    drives the water loop: the gentle wet road (CMB_FxWaterLoop 3) (instance N, poll N).`; `CMB_Slope.log`: `fx: the
    water loop (id N) driven (CMB_FxDriven N): ...; the gentle wet road (CMB_FxWaterLoop 3), WaterRoadDb +0 dB`). Then
    "Wet road (the mod's own)", get off and on, ride the same water and compare (T52-4).
13. **Getting on** (test 51: 5-6 s), five rides with a look on:
    - `Parked bike activated: choice 0.` to `Mounted.` within 2 s (the same second or the next);
    - no `a second into the ride and no bike shape found`;
    - one `Look: the worn bike's kept mods (the look unchanged): no attach` a getting on (the first ride after
      installing, and the first after a look change, show `Look: 7 of 7 mods on the worn bike` instead), and no `Look:
      the worn bike's F4SE swap again`;
    - draw a weapon mid-ride twice: the kept line again (the very first draw attaches once), no gap;
    - send any `Look: the worn bike's kept mods: N of M after the equip` line. A/B: `[Look] FastMount=0`.
14. **Double press** (test 51's black screen after Ride): activate the bike twice quickly, then Ride: `Parked bike
    activated again 0.0x s into the last activation (its menu or choice under way): ignored` (or no line, if your second
    press answered the menu), and no black screen. If you ever see `Getting on: not mounted ... (the watchdog)`,
    `Getting on given up ...` or `Getting on: undone ...`, send them with the minute: their stage and menus name the
    cause (the screen fades back in after 8 s; after 25 s out of every menu the ride is given up: "The motorbike
    couldn't be got on. Try again."). A/B: `[Look] MountGuard=0`.
15. **Field kit** (automatic, your save): once, `Field kit: CMB_KitWorked 1 (the toolbox, remembered on its menu's open
    alone) forgotten: automatic starts at the armour bench`; then `Customise: field kit mode 3 (the armour bench) at
    ...` and `Field kit: mode 3: the menu open after N s, the player in the kit`.
    - Does the armour bench take you in? Do Rims and Plate list mods (`Customise: Rims = ...`)? Make one change:
      `Field kit: mode 3 worked (a change made): remembered (CMB_KitWorked 3)`.
    - If its menu closes at once: `Field kit: mode 3: the menu closed 0.5 s after it opened, no change made, the player
      never in the kit: this mode doesn't work here`, `Field kit: mode 3: its menu closed at once: trying mode 4` and
      `Customise: field kit mode 4 (the game's armour bench) at ...`. Does the game's bench work?
    - With a paint change made, the parked bike reloads in front of you at the kit's end: `Look: the parked bike's 3D
      loaded again for its colours (the field kit, ParkedReload)`, and it shows at once (no `kept hidden`).
    - A/B: `[Look] KitHeld=0` (the toolbox first, as 2026-11-08a); MCM "Field kit" forces either bench.
16. **Parked paint** (test 51: grey after an MCM apply): MCM faction set Army, Apply, close the menu and look at once:
    green? Lines: `Look: the parked bike's swap holds 63 entries, N applied now (the MCM)` and `Look: the parked bike's
    3D loaded again for its colours (the MCM, ParkedReload)` (it vanishes for a moment, behind the pause menu until you
    close it). Then `[Look] ParkedReload=0` (restart, or ride once, so that the plugin's `look (2026-11-09a fixes)` line
    says ParkedReload=0), BoS then Army again: still green? (no reload line now).
17. **Free colour** (test 51: "it didn't do anything"): load, move only the hue, Apply: `Look: the MCM's paint hue moved
    (210 -> 280, shade Normal) (the MCM): Paint is now "Free colour"`; the paint takes the hue, and the MCM's Paint
    reads Free colour when reopened. Then move the hue and choose a factory Paint in one visit, Apply: `... chosen with
    it wins: Paint left`. A/B: `[Look] HueFree=0`.
18. **Gears** (test 51: 1st outlasted 2nd and 3rd): full throttle from a stop. Does each gear last longer than the last
    (about 1.6, 2.0 and 2.5 s)? The start's line: `  sound: HeardRiseGears=2.5,0.95,0.5,1 ShiftGapGears=0,2,2.5: the
    heard speed's rise by gear 350, 133, 70, 140 u/s^2 (HeardRise x each); at least 1.25, 2, 2.5 s in gears 1-3 before
    an up-shift (0 or missing: MinShiftGap)`; then `sound: gear 2`, `gear 3` and `gear 4` about 1.6, 3.6 and 6 s after
    the press. At the cruise a quick tap of the brake and full throttle again: 3rd's rise is as before, so the climb
    back in 3rd still takes about 5 s. Too long? `[Sound] HeardRiseGears=2.5,0.95,0.7,1`, get off and on, try again.
    A/B: `HeardRiseGears=1,0.95,0.5,1` with `ShiftGapGears=0,1.5,1.75` (this build's first set).
19. **After a load on the bike**, into first person twice (test 51: the tip was off for the session after a load): the
    tip comes at the second entry. At the first: `view: the camera didn't follow the player's pitch (+0xC0): the view
    left as it was (this entry only: it began N s after a load, TipLoadGrace 2)` (or `flipped (the tip goes on) (this
    entry only: ...)`); at the second `view: looked N deg down on getting into first person`. With `[Diag] ViewDraw=1`
    (the default) every `view: drawn? the chain: ...` line ends `, for the reference FFxxxxxx`: the same ID as `view:
    first person: the view bike shown (the reference ...)` and the `handed over from ... to ...` lines. A/B: `[View]
    TipLoadGrace=0`.
20. **Engine sound**: still "pitched down" now that getting on is quick? The engine hand-over (`Engine sound: the plugin
    drives the 11 loops (..., 3.x s after getting on)`) should now come about 1.5 s after you choose Ride, not 5-6 s.
21. **The Vault-Tec plate**: Customise, Plate "Vault-Tec" (its own text, e.g. VLT 111). Look up close with the bike
    parked (a couple of steps behind it), then from the saddle in third person while riding. Does the top-left emblem
    read as a cog (eight teeth, a hole in the middle), apart from the yellow pinstripe? A screenshot of each, please:
    there is no log line, the picture is the answer.

The off values, each giving 2026-11-08a: MCM "Caution" 100; `[Room] ActorRoom=0`, `ParkBack=0`, `ParkGuard=0`;
`[Steer] UseStop=` (empty), `UseListen=0`, `ClimbStepSpan=0`; `[Parts] WheelSpin=0`, `WheelLock=0`; `[Room]
SnapOrder=0`; `[View] TipMenu=0`, `TipYield=0`, `TipSettle=0`, `Bounds=0`, `FovSearch=0`, `TipLoadGrace=0`; `[Diag]
ViewDraw=0`; `[Look] FastMount=0`, `KitHeld=0`, `ParkedReload=0`, `PaletteIndex=0`, `MountGuard=0`, `HueFree=0`,
`Rehold=0`, `LightingOnly=0`; `[Sound] HeardRiseGears=1,1,1,1`, `ShiftGapGears=` (empty: `1,0.95,0.5,1` with
`0,1.5,1.75` is this build's first set); MCM "Water sound loop" "Wet road (the mod's own)". The 2026-11-08a build's
own switches back to 2026-11-07a's are all still there.

Send both logs a session, any crash log, the screenshots of steps 9 and 21, and the video if you have one.

### Questions for you (test 52)

- **T52-1 (step 3).** Caution 60: right, or 70, or 50? 70 is safer for a wall that comes into view late, and gives the
  sidestep back the room it had (at 60 it starts about 575 units past the front wheel, at 70 to 100 about 725).
- **T52-2 (step 2).** Did the bike keep its speed through items, by hotkey and from the Pip-Boy?
- **T52-3 (step 9).** Was the first-person bike seen at any point of step 9 (and with `Cull=1` or `Near=5`)?
- **T52-4 (step 12).** The gentle water loop or the old one?
- **T52-5 (step 1).** Was the parked bike ever hidden when you didn't expect it (after a door or a fast travel it waits
  hidden till you call it)?
- **T52-6 (steps 13 and 14).** Was getting on quick enough? Any black screen, or a watchdog line?
- **T52-7 (step 15).** Which bench worked, and did Rims and Plate list the mods?
- **T52-8 (step 16).** Was the parked bike green at once, and with `ParkedReload=0` too?
- **T52-9 (step 18).** The gears' lengths: each longer than the last? The climb back in 3rd after a brake tap (about 5
  s): keep it, or `HeardRiseGears=2.5,0.95,0.7,1`?
- **T52-10 (step 21).** The Vault-Tec cog: does it read, up close and from the saddle?

## The 2026-11-08a build: rims, tyres, the hue, the plates, in this order

This is the second customisation build: rims and tyres, a free paint colour from the MCM, and the licence plate, all
at the field kit as before (and in the MCM's free mode). **Nothing changes until you choose**: with nothing chosen the
bike is the 2026-11-07a build's, parked, ridden and in first person (the plate is a re-sampled copy of the old one:
step 1 asks). This test answers what only the game can (does a palette colour take on the rims' shiny materials, does
the plugin's colour write reach the ridden bike, do the hidden rim styles stay hidden, do the plate's colours show
without a preview, does the crude switch hide the recipes at once); each step names the log line that answers it.

Before you start:
- install as a Replace; F4SE and `CMB_Slope.dll` as before (the colours on every bike need F4SE, the ridden bike's rim
  styles the plugin);
- load the 2026-11-07a test's save (or test 50's). If the 2026-11-07a build's test hasn't been run yet, its twelve
  steps are in that build's package (README.txt, WHAT TO TEST) and in this file at that build's commit; this test
  takes for granted that the field kit opens the armour menu with the bike listed (its steps 3 and 4);
- put Steel, Screws, Oil and Adhesive (a few of each) in the workshop or the side bag; Armorer 1 for the rim styles and
  Free colour (or `player.addperk 4B254`);
- copy both logs aside before every quit (`CMB_Slope_stepN.log`, `Papyrus_stepN.log`): the plugin keeps only one
  earlier session.

The log's first lines: `CMB_Slope.log` has `globals: the 2026-11-07a build's CMB_LookCode found (...)`, `globals: the
2026-11-08a build's look colours found, CMB_LookPaintV to CMB_LookPlateTextV (...)` and the settings line `look: [Look]
Rims=1 PaintWheel=1 PlateColours=1 (2026-11-08a: the rim styles hidden as chosen at the bike; the paint's and rims'
colour, the plate's colours written)`. At the first getting on the parts' lines name the 14 rim shapes, `tilt:
CMB_BikeWornRider_wheelF_rimLaced is the front wheel [wheelF+rim2, by its name] (...)` up to `...wheelR_rimScrap is
the rear wheel [wheelR+rim8, by its name]`, and the plate's two, `tilt: CMB_BikeWornRider_static_plate is a fixed
part [none, by its name] (...)` and `...static_plateText ...`. A line `globals: no look colours (0xA14-0xA17, an older
ESP): [Look] PaintWheel and PlateColours write nothing` means an older ESP is loaded: stop and say so.

1. **The stock bike, before any choice**: parked, ridden and in first person, beside the 2026-11-07a test's spot.
   - Expected: exactly as 2026-11-07a: the cast rims, black tyres, the plain plate. The plate is now a shape of its own
     with a re-sampled copy of its old texture: say if it looks any different (lighter, darker, blurred, its edges).
   - Log: `CMB_Slope.log` at getting on `look: the rims now 0, the cast rim (stock) (CMB_LookCode 0x5, as chosen at the
     bike)`, and no `look: ... colour ... written` line (nothing to colour).
2. **The new lists** (at the field kit): "Rims" (48), "Tyres", "Plate", "Plate text", "Plate letters", "Plate
   background", and "Paint" ends with "Free colour (hue in the MCM)". Hover them (nothing is paid until you take one):
   - does the preview show each rim style whole on both wheels, round, with nothing of another style and no cast rim
     showing through? No purple anywhere?
   - the plate designs and texts on the preview's plate; the two colour lists change nothing in the preview (expected:
     their colours show on the parked bike once taken, step 8).
3. **Rims on the three bikes**: take "Turbine, chrome", leave the kit.
   - Log, `Papyrus.0.log`: `Customise: rims = Rims:turbine_chrome (24)` and `Look: put on (the field kit): ..., rims
     Rims:turbine_chrome, ...; CMB_LookCode 37`; on getting on `CMB_Slope.log` `look: the rims now 4, Turbine
     (CMB_LookCode 0x25, as chosen at the bike)`.
   - Parked, ridden and in first person: Turbine on both wheels. Ridden: do the rims spin with the tyres, steer with the
     front wheel and ride the suspension with it? Any cast rim, or another style, showing through?
   - A/B: `[Look] Rims=0` (the plugin hides no rim shape; the cast rim may show inside the new one on the ridden bike:
     expected with 0), then back to the default.
   - Mid-ride: in the MCM's free mode Rims "Laced, chrome", "Apply the look". Within about a second the ridden bike is
     put on again with Laced: you stay seated, the bike gone for a moment (`Papyrus.0.log`: `Look: the rims' style
     changed while riding (Rims:turbine_chrome worn, CMB_LookCode's style 1): the worn bike put on again with the look's
     mods`). How long is it gone? Does the camera, the rider or the speed jump?
4. **Finishes** (the palette on a shiny, env-mapped material: the 2026-11-07a build's open question again): Laced in
   satin black, gloss black, bronze and gunmetal, then "Cast, bronze".
   - Grey, white or black where a colour should be means the palette doesn't take on these materials (a later build then
     bakes the finishes): say which. Chrome has no palette and shows regardless. "Cast, satin black" should look like
     the stock rim.
   - Body colour: "Laced, body colour" with the Enclave paint: the rims the paint's colour, the trims the coachline's
     (`Look: the parked bike's swap holds N entries, M applied now (the field kit), colours: paint -1 rims 0.023438
     plate -1 text -1`; ridden, `look: CMB_BikeWornRider_wheelF_rimLaced colour 0.0234 written (read back 0.0234; the
     rim)`). Then Paint "Free colour": do the rims follow the hue (rims and paint 0.3960 at the default hue)? At getting
     on a line per rim shape such as `look: CMB_BikeWornRider_wheelF_rimLaced colour 0.3960 not written: its lookup
     texture is ...paint_p.dds, not paint_hue_p.dds (the rim)` may show once, before F4SE's swap puts the rim's hue
     material on (the plugin writes a colour only into its own palette): send the log if one shows later in a ride. It
     also names the lookup texture as the game holds it; a `written (read back ...)` line means the name matched (or the
     game keeps none).
5. **Tyres**: "Whitewall", then "Red line": on both sidewalls of both tyres, round, on the rubber only (not the tread,
   not the rim), no seam across the band.
6. **The hue** (the MCM's free mode): Paint "Free colour", "Paint hue" 120, "Paint shade" Light, "Apply the look".
   - The parked bike at once, the ridden one at the next getting on. Log, `Papyrus.0.log`: `Look: from the MCM: paint
     hue 120 shade Light` and `Look: put on (the MCM): ...`; `CMB_Slope.log` on getting on `look:
     CMB_BikeWornRider_static_paint colour 0.5835 written (read back 0.5835; the paint)` and the same for `fork_paint`.
   - Then hue 300, shade Deep (0.2085). Ride, save and load mid-ride: does the ridden bike keep its colour?
   - Do the four shades differ, and does a step of a few degrees move the colour without a jump?
7. **Plates** (readable? raised?): "Commonwealth standard" with "The plate's own" text (AB 1234), then "Vault-Tec"
   (VLT 111). From the riding camera: can you read them? Up close at the kit: do the letters look raised (stamped)? Then
   every design once, and a few texts (a screenshot of each design). Log: `Customise: plate = Plate:standard (1)`.
8. **Plate colours** (no preview): on the Commonwealth standard, "Plate letters" "Vault yellow", then "Plate
   background" "Black".
   - Does the parked bike's plate change at once? Log, `Papyrus.0.log`: `Customise: plate letters =
     PlateInk:vaultyellow (8): the parked bike re-composed` and `Customise: plate background = PlateBack:black (3): the
     parked bike re-composed`.
   - The ridden bike (`look: CMB_BikeWornRider_static_plate colour 0.0098 written (read back 0.0098; the plate)` and
     `look: CMB_BikeWornRider_static_plateText colour 0.4688 written (read back 0.4688; the plate's text)`)? First
     person, if you look back? The menu's bike keeps the design's own colours (expected).
9. **The crude switch**: take "BITE ME (crude)" on the Commonwealth standard; MCM Look "Crude plate texts" off; reopen
   the kit: the 14 crude texts are gone from the list; activate the parked bike (or get on): it shows the plate's own
   text, AB 1234 (`Look: the plate text PlateText:biteme is crude and "Crude plate texts" is off: the plate's own
   (PlateText:ab1234)`). On again: BITE ME is back on the bike and in the list.
10. **Staying put**: leave the parked bike's cell and come back; save, quit, load: the rims, tyres, plate and its
    colours on the parked and the ridden bike (`Look: the parked bike's swap holds N entries, M applied now (load),
    colours: ...`, within a second of the load).
11. **Off values**: `[Look] PaintWheel=0` with a Free colour: no `look: ... colour ... written` line for the paint;
    does the ridden bike still show the hue (then F4SE's swap alone reaches its materials; if it shows the default
    steel blue instead, the plugin's write is what colours it: say which), also after a load mid-ride; `[Look]
    PlateColours=0` likewise for the plate; MCM "Customise at the bike" off and Apply: everything stock, the rims, tyres
    and plate too (`Look: put on (the MCM): ... (Customise at the bike is off: the stock look); CMB_LookCode 0`). Do
    that once while riding on a rim style: within about a second the ridden bike is put on again with the cast rims
    (`Look: the rims' style changed while riding (...)`).
12. **Frame rate**: one spot in Sanctuary, the stock look, then "Laced, chrome" and the Vault-Tec plate: note both, and
    `CMB_Slope.log`'s frame-time line for each (`time: frame N us avg, N max, over N (bike N/N for 50 shape(s), ...`).

Every new thing has an off value that gives the 2026-11-07a build: each new slot's first choice (with every slot there
the bike is 2026-11-07a's), `[Look] Rims=0`, `[Look] PaintWheel=0`, `[Look] PlateColours=0`, and MCM Look "Customise at
the bike" off (every slot stock). "Crude plate texts" off hides the 14 crude texts (a content switch; on is the
default). The 2026-11-07a build's own switches back to 2026-11-06a's are all still there (README's second key table).

Send both logs per session, screenshots of steps 2, 4, 7 and 8 (or a recording).

### Questions for you

- **T-C2-1 (steps 3, 4).** Which rim styles and finishes would you keep? Any too busy at riding distance?
- **T-C2-2 (step 6).** The hue's shades (Deep, Normal, Light, Pastel): the right steps?
- **T-C2-3 (step 5).** The whitewall's width.
- **T-C2-4 (steps 7-9).** The plates: the 60 texts (strike or add any, 5 to 7 characters); the crude set's strength
  (is BASTARD or PISSOFF as strong as it should go?); the 12 designs (keep all, swap any?); the 16 colours; Stock (the
  plain plate) as the default, or a new game on the Commonwealth standard with AB 1234?
- **T-C2-5 (steps 3, 5, 7).** The costs (a rim style needs Armorer 1, as the paint colours).
- **T-C2-6 (from the 2026-11-07a test).** Did the palette show on the paint, and did "Palette test: colour index" show
  cobalt? It decides whether a later build bakes the rims' finishes.
- **T-C2-7 (step 7).** The Institute plate's own letters are teal on its pearl white: readable, but a weak contrast
  (2.7 to 1; its legends are black for that reason). Keep the teal, or make its letters black (11.9 to 1; its emblem
  black too)?

### Questions for your checker, still open from the 2026-11-07a build (data only; nothing of the game's ships)

- **Q-K1 (the bench's type).** The TNAM (type) of `WorkbenchArmor` 0657FF and `Workbench_General` 091FD4.
- **Q-K2 (the menu's order).** An armour bench's mod order within a slot: the form order, the name, or the recipe's?
- **Q-K3 (later badges).** The sheet `CMB_Q9_faction_textures.png` (the T-60 crops).

### The look's keys (since the 2026-10-31a build)

The bike's look has these keys in `CMB_Slope.ini`, all read again on getting on; the off value gives 27c's behaviour:

| Key | Default | Off (27c's) | What it does |
|---|---|---|---|
| `[Parts] RolesByName` | 1 | 0 (for 27c's meshes) | 1: each shape's part told by its name first; 0: 27c's rules alone (by where its culling sphere sits), with this build's meshes the needle then rests and the lights, the dial's backlight and all three mirrors always show, whatever the keys below say |
| `[Speedo] Needle` | 1 | 0 | 0: the needle shrunk to a speck at its hub (27c had none) |
| `[Speedo] Scale` | 1.75 | 1 (true speed) | the dial's gearing: 1.75 reads full speed, 900 units a second, as about 50; 1 is the world's true speed, 28.8 mph at 900 |
| `[Speedo] Tau` | 0.3 | 0 | seconds the needle takes to follow the speed; 0 follows it at once |
| `[Speedo] Backlight` | 1 | 0 | 1: the dial's numerals glow with the headlamp; 0: never (the needle's own faint glow stays: `Needle=0` takes it with the needle) |
| `[Tail] Glow` | 1 | 0 | 1: the tail lamp lit while riding; 0: the plain lens |
| `[Tail] Brake` | 1 | 0 | 1: the brake light; 0: never lit |
| `[Tail] BrakeHold` | 0.3 | 0 | seconds the brake light stays on after you let go of the brake |
| `[Look] Mirrors` | -1 (since 2026-11-07a; 1 before) | 1 | the riding bike's mirrors: 1 the stock ones (27c's), 2 egg-shaped under the bar ends, 3 D-shaped under the bar ends, 0 none; since 2026-11-07a -1, the default: the ones fitted at the bike's field kit (`CMB_LookCode`), the stock ones while nothing is chosen, and the parked bike shows the fitted ones too (before, it kept the stock ones) |
| `[Look] Rims` | 1 (since 2026-11-08a) | 0 | the rim styles: 1, the ridden and first-person bikes show the style fitted at the bike's field kit (`CMB_LookCode` bits 3-6; the cast rim while none is) and the others shrunk to specks, as the mirrors; 0, no rim shape hidden by the plugin (the materials alone decide what shows, as 2026-11-07a) |
| `[Look] PaintWheel` | 1 (since 2026-11-08a) | 0 | 1: the Free colour paint's hue and a body-colour rim's colour written into the ridden bike's paint and rim materials (their palette row, `fLookupScale`), read back and logged; 0: never written, as 2026-11-07a (the ridden bike's colours F4SE's swap's alone, at getting on and after a load) |
| `[Look] PlateColours` | 1 (since 2026-11-08a) | 0 | the same for the licence plate's background and letters |

With `RolesByName` left at 1 and every other key at its off value this build's bike looks like 27c's but for its
textures and the lower triple clamp turning with the bars: no needle, no lit tail, brake or dial, the stock mirrors.
`RolesByName=0` is only for 27c's meshes (2026-10-31a's step 15): with the 2026-10-31a build's meshes it shows everything (the needle at rest, both
lights and the backlight lit, all three mirrors). Two changes have no key, since they come with the meshes: the
textures and material files, and the clamp; 27c's meshes copied back give both back. `Materials\CMB` is required: the
meshes name their material files, and the game shows a missing one as magenta (test 47). The needle, the lights and the mirrors' choice need the plugin to hold the riding bike,
which it does only with at least one of the MCM's "Steepest slope while riding", "Riding camera distance" and "Bike
tilts with the ground" above 0 (all three at 0: every mirror shows, the lights and the backlight lit, the needle
at rest, as without the plugin).

## Test order

Use a throwaway save in an open area (e.g. outside Sanctuary), with a companion following you, some **Flamer Fuel** in your inventory,
and, if you have one, a bag or other gear that sits in an unusual slot.

| # | Do | Expect |
|---|---|---|
| 1 | Load the save while outdoors | "Motorbike Keys (2)" added (Aid tab), plus a hint. On a new game this happens when you first step outside Vault 111 |
| 2 | Use the keys | menu "Your motorbike isn't nearby." |
| 3 | Pick "Call it here" | the bike appears a few steps ahead, facing your way (invisible = `CMB_BikeParked.nif` missing) |
| 4 | Activate the bike → "Ride" | short fade; you're in 3rd person, **seated** on the bike, hands on the bars, left foot down; "Fuel: N" shown; your bag still on (no bike under you = `CMB_BikeWornRider.nif`/`CMB_BikeWornRiderF.nif` missing; standing over the bike = see row 4b) |
| 4b | *(only if you stand over the bike)* check `CMB_RiderPose.esp` is active (and, with MO2, the *Rider Pose* mod) | then the seated clips aren't playing: send the log, a screenshot, and what `make_rider_pose.bat` printed Since 2026-11-02a (steps 7 and 8 of its list): "Steady in the saddle" is `CMB_RiderSteadyPerk2` (`set CMB_RiderSteadyWay to 2` the game's own perk, `0` the 2026-11-01a build's three-tab record), each ride's hit events, power attacks and staggers counted at getting off ("Hit events this ride: N (M power attacks; ...), staggers K (...)"), a stagger's end logged half a second after it; the pose is left alone for `CMB_PoseUseWindow` (6 s) after an item's use ("... its use clip may follow: the pose left alone for 6.0 s."), and in first person the plugin doesn't measure the knees (`[Tilt] PoseFirstPerson`), so the footstep watch leaves first person's footsteps alone. Since 2026-11-06a (step 4 of its list): above 150 a second an item's use clip isn't played (`[Steer] UseBlockAbove`; "rider: the graph's dyn_ActivationAllowMovement at N u/s (an item's use clip): refused, the speed kept (UseBlockAbove 150)"), a standing clip that still plays at speed leaves the throttle alone (`UseHold`), the knees and hands aren't measured for 0.1 s after first person (`[Tilt] PoseViewSettle`), and another mod's item equipped with no menu open is left out of the use watch (`CMB_RiderUseOwn` 1). |
| 4c | Cripple a leg or an arm (Survival), ride | still seated (the crippled-limb entries are copied too) |
| 5 | Run around, turn | clearly faster than on foot (~2.5×), feet up on the pegs, leaning forward, bike and rider lean into turns; no jumping, no sprinting, weapons holstered; your companion keeps up running alongside |
| 5b | Stop, turn on the spot, start again; talk to someone while seated | foot goes down when stopped, smooth start/stop; the bike turns with you on the spot and stays lined up in dialogue, hands on the grips. `set CMB_BikeFollowsRider to 0` and get on again for the old planted bike, to compare |
| 5c | While riding, hold the key for the opposite direction (a U-turn) | you swing round in a short leaning arc and keep going, instead of stopping, spinning and setting off backwards |
| 6 | Use the keys again (or favorite them and press the hotkey) | fade; the bike is parked to your right; after 300 m or more of riding, Flamer Fuel went down by about one per 300 m |
| 7 | Activate the bike → "Open side bag" | a container opens; put stuff in |
| 8 | Overfill the bag (default 60 lbs with F4SE, or 60 items without) | extra items bounce back with "The side bag is full" |
| 9 | Ride up to a building door and go inside, come out again; then ride to Diamond City's gate (or Goodneighbor's) and go in; inside, try the keys' "Call it here" and getting on; come out through the gate; ride in again and leave by fast travel to somewhere far off, then go back to the bike on foot and use the keys; last, riding outside, fast travel straight into Diamond City or Goodneighbor | auto-dismount at the door and at the gate ("You leave the motorbike parked outside."; the Papyrus log: "Gone in N game minutes after the last tick outdoors: a door." and "The bike waits outside the door, in ..."); coming out of the same door or gate (or another door of the same building or town, within about 85 m of the bike) the bike is in front of you, a little to your right (since test 41 on the first of its spots with room, or left where it waited: row 9b, step 2), on the ground, with no sound and no message, and the next use of the keys or the hotkey gets on (since test 40; test 39: it was left inside or behind Diamond City's wall, and there was no bike outside the gate): "Bike brought from the door it waited at, N units away." in the log; out far off, it stays at the door ("Out N units from the door the bike waits at: it stays there."), calling it brings it, and walked back to, the keys get you on rather than moving it; the fast travel in: "Your motorbike stays where you set off." (the log: "... a fast travel."), and the bike is where you fast travelled from, outside, and calling it brings it (test 39: it said parked outside while the bike stayed at Sanctuary). Say where the bike was each time you came out. In Diamond City and Goodneighbor, calling gives "There's no room for your motorbike here." and getting on "There's no room to ride in here." (since test 39: they, the pre-war Sanctuary, Far Harbor's memory simulation and Nuka-World's market and amphitheater are worldspaces of their own, outdoors to the game; the Papyrus log says "In an enclosed worldspace"); dungeons and sewers are interiors, refused as before. Since test 41 a door or a fast travel is decided once it's over, not when the game sends its teleport event (test 40: the event came while the player was still at the gate, so the way out of Diamond City brought no bike, three times, and the way in brought it to the gate): row 9b gives the log at each step |
| 9b | *(test 41: doors and keys, in this order; note the times)* 1. Ride in at Diamond City's gate. 2. Walk out through the gate. 3. Ride in again; leave the town by fast travel to somewhere far off (over about 85 m from the gate), then fast travel back into Diamond City on foot. 4. In the town, use the keys, once from the Pip-Boy (Aid → Motorbike Keys) and once by a favourites slot (not the F4SE hotkey's own key: test 41's first six hotkey presses each fired the keys too, "Keys used" and "Keys ignored: busy (…)" at once, the keys being on favourites slot 10, the hotkey's key; harmless), and pick "Call it here". 5. Press the hotkey with the Pip-Boy open. 6. Walk out, ride off a way, and fast travel straight into Diamond City on the bike. 7. Walk out, call the bike, ride in at the gate once more, walk out, and load the autosave the exit made. 8. A building door: as 1 and 2. 9. *(test 43)* Outdoors, stand in a passage 100 to 150 wide (a fenced walkway, between two cars) facing along it and call the bike; then facing across it, and call it again. 10. *(test 45)* By Sanctuary's houses, as in test 44 (22:54:49 to 22:55:42), call the bike: with a picket fence a step or two ahead of you and open ground past it; facing a house's wall about 3 m away (the first spot, 220 ahead, inside the house); facing a wall up close; standing in a hedge. 11. *(test 46)* As in test 45 (14:48 to 16:53 of its video), call the bike: with a fence, a wall, a hedge or rubble right in front of you (its calls 1, 6 and 8: every spot ahead past it); with a picket fence or a wall a step to the side of the spot ahead (calls 2 and 4: the bike's nose in it); on an open hillside facing down it (calls 10 and 11), and up it. Look where the bike stands each time, and how it sits. 12. *(test 47)* Get on facing a wall or a house's window at point blank and get off a couple of seconds later without riding off (test 46's 13:52); ride a bike length or two nose first into a wall and get off there; then a longer ride ending beside a wall or a fence. Stand on a wrecked car and call the bike, then on Red Rocket's red truck (test 46's 14:32 and 17:06), then beside each, and call it again | 1. "Teleport seen (t …): the player in [WorldSpace \<Commonwealth …>] at (x, y); riding True, bike at a door False.", "Loading screen up" (with ", a teleport pending." if the event came first: say which came first), "Loading screen over.", "Teleport handled (the loading screen closed, N s after it): the player in … DiamondCity …", "Gone in N game minutes after the last tick outdoors: a door." (once: test 41 had it twice at 15:57:50 and 15:59:19, the 1 s tick and the teleport handling's own tick both reaching it, with one outcome; it's logged past the busy claim now) and "The bike waits outside the door, in …"; between the event and the handling at most one "Ride tick skipped: a teleport is pending"; never "left hidden" (test 40, the fast travel in at 15:31:35: "The bike was put beside the player after they went in: left hidden", a ride tick having run between the event and the move). 2. "Teleport handled (the loading screen closed, …): the player in [WorldSpace \<Commonwealth …>]; riding False, bike at a door True.", then, since test 41, one "Bike's spot N (220 ahead, 60 right): room (the ground N below)." or "… none (the nearest hit N along a ray, on the bike's 110, or the ground N off)." or "none (no ground within 100 of the spot)." or, since test 43, "none (the ground N above the spot)." line per spot tried (seven at most: 220 ahead and 60 right or left, 150 ahead and 60 right or left, 300 ahead and 60 right or left, 100 ahead), "The bike's spot: N (…), heading A." and "Bike brought from the door it waited at, N units away."; right after a load, before the plugin's test ray passes, "Bike's spot 1 (…): not checked (the plugin's rays aren't working here): asked again in 1.5 s." and the plugin's "room: ask N: the rays weren't trusted (the test ray N s ago): tried again for it", then the spot asked about again (test 42 never needed it: say if it comes, and what the second answer was; "where it waited (spot 1 not checked twice: …)" if both were). Since test 43 the plugin checks each spot as a bike-shaped box along your heading, 110 fore and aft and 40 to each side ("room: ask N at (x, y, z), heading A: room (…)" or "… none, something N along the right (of 40: N on the bike's 110) (name, layer N)"), not eight rays 110 out every way, so outside Diamond City's gate a nearer spot than in test 42 may now have room: say where the bike stood and whether that's wanted (`[Room] Box=0` in CMB_Slope.ini, read again on getting on, gives test 42's eight rays). Send the "heading A" numbers too: they tell `GetAngleZ`'s range, 0 to 360 or ±180. The bike stands clear on its spot, not in the gate's fence (test 41: in the chain-link fence and gate each of the three times, 191 to 452 units from the door, a fixed spot with no look at what was there; test 40: no line and no bike, three times). With room at none of the seven: "The bike's spot: where it waited (none of the 7 has room)." and "The bike is left where it waited, N units away: no spot with room found (the spot lines above say why)." in place of "Bike brought", the bike where you got off, outside the gate (walk to it and the keys get on, or call it). "Bike's spot N (…): not checked (no answer in 0.5 s)." means the plugin didn't answer: send CMB_Slope.log, whose "room: ask N at (x, y, z): room (the ground N below the spot)" and "… none, something N along +x (name, layer N)" lines say what its rays found at each spot; "not checked (the ESP has no CMB_Room globals)" is an old plugin file. Say where the bike stood each time, and whether anyone stood on the spot (a settler there is passed through: "; an actor there (…), passed" on the plugin's line). 3. Out far off: "Out N units from the door the bike waits at: it stays there."; back in on foot: "Bike not brought from the door (the teleport): in an enclosed worldspace (… DiamondCity …)." 4. Each use: "Keys used (t …).", then "Keys: riding False, busy False, the bike near False / at a door True (in …), the player in … DiamondCity …", "Keys: the bike waits at a door: bringing it.", "Bike not brought from the door (the keys): in an enclosed worldspace (…).", "Keys: the menu.", "Keys menu: Call it here." and "Calling the bike refused: in an enclosed worldspace (…): There's no room for your motorbike here.", the message on screen too (test 40: nothing in the log in any of the three windows, 15:32:33-15:33:04, 15:35:52-15:36:36 and 15:37:26-15:37:49). A use that leaves no "Keys used" line never reached the script: say how it was made. A "Keys effect started on …, not the player" line, or one saying its Controller property is empty, is where it stopped. "Keys ignored: busy (who, N s)." names what held it, and a "Busy held N s (who): let go." line (a busy held over 10 s) is news: send it. 5. "Hotkey (the F4SE hotkey) ignored: in a menu." (or "(the MCM hotkey)"). 6. Coming out, the bike brought as in 2; going in, "Gone in N game minutes after the last tick outdoors: a fast travel." (once), "Your motorbike stays where you set off." on screen, and no "Slot 57:" line around that dismount (test 40, 15:31:35: two ride ticks ran at once, one putting the bike back on while the other ended the ride). 7. "Loaded with the bike waiting at a door: looked at once the load is over.", "Teleport handled (look 1, after loading a save, …)" and "Bike brought from the door it waited at, N units away." within about a second of the load (test 40: brought within a second as well, the save having the player outside already; it should still be so). 8. As 1 and 2, the player in "…, indoors" in place of the town's worldspace. Every load logs "Switches: teleports decided once they're over, busy watch on (10.000000 s)."; `cqf CMB_ControllerQuest DecideTeleportsAtOnce 1` (kept in the save) gives test 40's rules back for an A/B, and `cqf CMB_ControllerQuest WatchBusy 0` turns the busy watch off. Getting on, off or calling refused anywhere says why in the log ("Getting on refused: …", "Getting off refused: …", "Calling the bike refused: …"), and so does each activation of the parked bike ("Parked bike activated: choice N."). 9. Facing along the passage: a spot in it has room ("room: ask N at (…), heading A: room (the ground N below the spot)"; the box is 80 across, the eight rays of test 42 needed 220), and the bike stands in the passage, along it. Facing across it: the spots refused ("… none, something N along fore (of 110: N on the bike's 110) (…)"), and with room at none of the seven the call takes the one with the most room since test 43, "The bike's spot: N (…), heading A, the most room of the 7 (the nearest hit K along a ray, on the bike's 110, or the ground K below; none has room, a call takes the most room)." (test 42's build took the first, outside Diamond City's gate the fence). Say where the bike stood each time; `[Room] Box=0` is test 42's rule for an A/B. 10. After the settings "  room: Line=50 GroundNear=25 GroundSlope=25: a clear line asked for from the player to the spot, that high over the ground under each (the player's by a ray down under them); the spot's ground within 25 of the player's, or by a slope of up to 25 deg to the spot, the ground along the line stepping by no more than 25". A fence or a wall between you and a spot: `CMB_Slope.log` "room: ask N at (x, y, z), heading A: none, no clear line from the player: something N along the N to the spot (what, layer N), 50 over the ground under each (the player's Z, the spot's Z)" and the Papyrus log "Bike's spot K (…): none (no clear line from the player to it)." (test 44: the bike through the picket fence, the fence out of the box's reach at the spot); a spot on a house's floor, or any ground more than 25 from yours with a step on the way: "none, the ground N above the player's (what, layer N), over 25; a clear line from the player; not a slope: a step of N up N along it (what, layer N), over 25" (test 44: "room (the ground 34 above)", the bike inside the house); a spot with room ends its line "; a clear line from the player (N long, 50 over each ground), the spot's ground N below the player's (within 25)". Also call it on an open hillside (about 15 deg), once facing uphill and once downhill: the spots have room by the slope, "the spot's ground N above the player's (over 25: within N (25 and 25 deg over the N to it), the ground followed every N along it, no step over 25)" (test 45's first build refused every spot there and placed one unchecked); a spot refused for its ground below says "; checked at its ground: clear" (or what its box met). `[Room] GroundSlope=0` is that first build's rule. Once the bike is placed: "The bike settled N from the checked spot (the navmesh snap, 30 at most)." or "The bike settled N from the checked spot (the navmesh snap), over 30: put back on the checked spot, level on its ground." (test 44, in the hedge: the bike 250 from the checked spot when you got on; since test 47 the putting back only when no other spot passes: step 12). The bike stands on your side of the fence, outside the house and out of the hedge; say whether one put back on the checked spot looks right there (floating, sunk, tilted wrongly). Facing a wall up close with every spot refused, a call took spot 1 as before test 41 (test 45's calls 1, 6 and 8: past the fence, inside the house, beyond the rubble): since test 46 step 11. `[Room] Line=0` with `GroundNear=60` (read again on getting on) is test 44's check, and `SpotSettleMax` 0 (the controller's constant) test 44's snap. 11. After the settings a third "  room:" line, "  room: Around=1 LineFallback=0 Slide=1 Tilted=1 ParkTilt=1 ParkRoll=20: spots beside and behind the player asked after the seven ahead; a call with no spot with room nor a most-room one (with a clear line) is refused, the bike not brought; a box with a hit slid away from it by what it lacks and 10, else turned 90 either way, and checked again; the spot's ground looked for down to 100 and its distance times tan GroundSlope, the box tilted with the ground under its ends; the brought bike tilted to the ground under its wheels, its roll up to 20" ("room: no CMB_RoomOptions to CMB_RoomGround (an older ESP): …" is test 45's ESP). With none of the seven ahead to take (the fence or the wall in front: "none (no clear line from the player to it)."), four more are asked: "Bike's spot 8 (100 behind, 110 right): …", "9 (100 behind, 110 left)", "10 (120 behind, across)" (turned across your heading) and "11 (220 behind)", and the bike stands beside or behind you on your side of the fence (test 45: "none of the 7 has room (a call takes the first, as before test 41)", the bike 220 ahead past the fence, in the house, beyond the rubble). With none of the eleven to take: "The bike's spot: none of the 11 has room, and none to take for the most room (a hit along its box or the ground below, each with a clear line): the call is refused." and "Calling the bike refused: no spot with room around the player (the spot lines above say why): There's no room for your motorbike here.", that on screen and the bike left where it was (from a door, with the bike that came in with you: "Bike not brought (…) from where the player went in: no spot with room around the player, kept hidden."). A spot whose box meets the fence or the wall is moved off it: `CMB_Slope.log` "room: ask N: slid 50 back along its heading to (x, y): room (…)" ("forward along its heading", "to its left", …), or "room: ask N: turned 90 to the right, heading H: room (…)" (then to the left), "…: not tried, the box would stand on the player" for a move onto you; the Papyrus log "The bike's spot: N (…), heading H, where the plugin found room (50 from the asked spot, turned 0).", and the bike clear of the fence (test 45's calls 2 and 4: the most room's box with the fence 59 and the wall 78 along its 110, the nose that far in). Downhill: the spot's ground found lower down ("no ground within 100 above or N below the spot" only past the slope's reach), the plugin's line ending "; the box tilted with the ground under its ends (-15 deg along its heading, 0 across)" and "; parked tilted to the ground under its wheels: pitch -15.0, roll 0.0" (" (its N held to ParkRoll's 20)" across a steep slope; "; not tilted for parking: …" says why not), the Papyrus log "Bike's spot N (…): room (the ground N below, its wheels' ground at pitch 15.0 down, roll 0.0)." and, once settled, "Parked bike tilted to the ground under its wheels (the plugin's, on the checked spot): pitch P, roll R." (after "… over 30: put back on the checked spot, on its ground." when the navmesh snap went too far), the bike on the slope with both wheels on the ground (test 45's calls 10 and 11: "no ground within 100", the box's level aft rays on the slope behind the spot; the bike 300 ahead and 84 below, its roll held at the script's 10, or left level, "the navmesh around the parked bike is too coarse to tilt it by"); a most-room spot comes with its tilt too and is settled as a checked one. Say whether the tilted bike sits on its wheels, floats or sinks, and whether a roll of up to 20 across a slope looks right on its stand. `[Room] Around=0`, `LineFallback=1`, `Slide=0`, `Tilted=0` and `ParkTilt=0` (read again on getting on) are test 45's build for their parts. 12. After the settings a fourth "  room:" line, "  room: ParkCheck=1 SnapNext=1: getting off, the bike put back where it stood when the ride moved the player less than a wheelbase from where they got on, else its spot asked about as a call's (slid or turned), with no room there the spots beside and behind the player; a spot with room whose navmesh snap goes past the script's SpotSettleMax isn't walkable: the next spot asked, the checked spot taken only when none passes". Getting off where you got on: "Parked bike put back where it stood before getting on: the ride moved the player N from where they got on, under 136 (the plugin's [Room] ParkCheck).", and the bike exactly where it stood (test 46, 13:52 to 13:56: the parked bike through the window, "No Navmesh found, object not moved", and inside the house). Getting on from beside it, riding a little onto where it stood and getting off there: "Parked bike not put back where it stood: the ride moved the player N, under 136, but they stand where it stood (N along its heading, N across it): its spot asked about instead (the plugin's [Room] ParkCheck).", then the park spot's lines below, and the bike beside you, not on you. Getting off after a ride: "The park spot (the track just ridden): room (…)." (or "(beside the player)", or "none (…)"), then "The parked bike's spot: the track just ridden, as before (room there).", or "The parked bike's spot: …, heading H, where the plugin found room (N from the asked spot, turned T)." (`CMB_Slope.log` "room: ask N: slid 50 back along its heading …"), or with no room there the four beside and behind you asked ("Bike's spot 8 (100 behind, 110 right): …") and "The parked bike's spot: 8 (100 behind, 110 right), heading H.", or "The parked bike's spot: as before (none of the 4 beside and behind the player has room either)."; the bike clear of the wall. On the car or the truck: a spot with room up there whose navmesh snap would go far, "Bike's spot N (…): its navmesh snap N from it, over 30: not walkable, the next spot asked (the plugin's [Room] SnapNext).", and the bike on the ground beside or behind you (test 46: spot 9 on the sedan, the snap 89, and spot 7 on the truck, 207, the bike put back up there each time); a most-room spot only if its own snap passes ("Bike's spot N (…), the most room: its navmesh snap N from it, over 30: not walkable either." if not); where none passes, "The bike's spot: N (…), heading H: the first with room, its navmesh snap too far, and no other spot passes (the plugin's [Room] SnapNext): taken as before." and the bike up there as before. Beside the car or the truck, a call as any other. Say where the bike stood each time, and whether a bike kept off the car you stand on is what you want. `[Room] ParkCheck=0` and `SnapNext=0` (read again on getting on) are test 46's build Since 2026-11-02a: step 4 of its list is the 2026-11-01a build's step 10, the calls from the red truck's hood and cab, which test 48 didn't get to; nothing of it changed. Since 2026-11-06a (step 6 of its list): with no spot with room, the most room's own navmesh point is tried before the most room is taken (`[Room] SnapBest`, "...: taken (the plugin's [Room] SnapBest)."), and a navmesh point's ground may be 250 under yours (`SnapDrop`; 100 before). |
| 10 | Ride, save, load that save | still riding, still fast, still can't jump |
| 10b | *(F4SE plugin; test 41)* On the bike: quicksave, ride on a little, quickload (a load in place); then load a save made on the bike somewhere else; then quit to the main menu and load a save made on the bike from there. Each time ride off and turn hard for a few seconds at speed | after each load the bike leans into the turns and the rider leans forward with it, about 14 degrees, at once (test 40: after the load at 15:23:42 the bars turned and the wheels spun, but the bike stood upright through the turns and the rider sat up, until he got off and on). `CMB_Slope.log`: one "load: a save loaded (PostLoadGame); before it riding (the globals slope …, camera …, tilt …), N bike skin(s) and N rider shape(s) held, …; the globals now …; the player at (…), the 3D root at (…)" line, then "load: the ride resumed N s after the load (slope 45, camera 450, tilt 45; …)" (your MCM values), and "load: 2.5 s into the ride after the load: N bike skin(s), N rider shape(s) held, the rider written (or not written while the bike stands level), the upper body's lean N deg, final; the tilt pitch … roll … (the lean N at N units/s), the globals …, the ground under it, the rays working: resumed", and the same at 6.0 s. Since test 41 an in-game load starts as a cold one does: whatever the plugin held is let go of at the load and held afresh in the loaded 3D (the old holds went on into it before). If the 2.5 s line says "not resumed:" and why, what it names is let go and held afresh once ("load: what didn't resume let go and held afresh, as getting off and on does (once a load): …"), and the 6 s line says whether that took: send both. A line "tilt: riding with CMB_TiltLive at 0 for N s …" is test 40's picture exactly (the bike kept level, the rider not held, only the moving parts running), and so is, in the Papyrus log, "CMB_TiltLive read 0.000000 while riding, put back to N." (the script's ride tick puts it back within a second, so the plugin's line then means the script's tick isn't running): send them with the Papyrus log of that load, and say what the MCM's "Bike tilts with the ground" reads; "tilt: CMB_TiltLive reads N now" follows if it comes back. "load: not riding after the load" while on the bike is news too. The log's first line gives the date and says "the session before's log kept as CMB_Slope_prev.log" (since 2026-11-15a also the two before it, `CMB_Slope_prev2.log` and `CMB_Slope_prev3.log`): after a crash or a restart send those as well (test 40's restart overwrote the log that would have said why). Say which save each load was (a quicksave at the same spot, an older one elsewhere) and how it was loaded |
| 11 | Ride, fast travel | still riding at the destination (into a walled town or an interior: row 9) |
| 12 | *(opt-in, outside companion quests)* `set CMB_CompanionMode to 1`, ride, get off | companion disappears while riding and steps out behind you afterwards |
| 13a | Put all your Flamer Fuel in the side bag, ride | fuel is taken from the bag first |
| 13b | Ride until the fuel runs out | "Your motorbike ran out of fuel." and the bike is parked next to you; getting back on is refused until you have fuel |
| 14 | Try riding in power armor; get on, then get into a power armor frame (if the game lets you activate it while seated); then draw a weapon and try to get on | refused with "You can't ride a motorbike in power armor."; in the frame within a second you're off with "You can't ride in power armor. The motorbike is parked nearby."; the weapon refused with "Put your weapon away first." (since 2026-11-15b with "Weapons while riding" on None or Any weapon; on Handguns only, the default, it is put away and you get on: the 2026-11-15b build's step 19) (calling the bike in power armor is allowed: it's only the riding) |
| 15 | Get on, sit still, then ride off and stop | engine start, idle while standing, louder/higher while moving, run-down when you get off (silent = see the engine-sound note in DESIGN.md; with F4SE and its Address Library the plugin drives the engine since test 44's build: row 17q) |
| 16 | *(F4SE)* wear something in slot 57, ride, get off | it comes off while riding and goes back on afterwards |
| 17 | *(MCM)* Mod Config → Commonwealth Motorbike | every setting there; change the speed, get on: the new speed applies |
| 17c | *(F4SE)* With `CMB_Slope.dll` and `CMB_Slope.ini` in `Data\F4SE\Plugins`: load a save, get on, ride up something steeper than you can walk up, get off | you can ride up it; the log (`Documents\My Games\Fallout4\F4SE\CMB_Slope.log`) has "riding: slope limit at controller+0x418 47.00 -> 60.00 deg" and "back to 47.00 deg" (worked in test 6). If the game doesn't start or crashes, remove the two files and send that log and `f4se.log` |
| 17b | *(F4SE plugin)* In third person, zoom in a bit with the mouse wheel; get on; ride; get off | on getting on the camera is all the way out (450 by default), and you can zoom in again with the wheel after a couple of seconds; on getting off, back to your own zoom and distance. The log: "camera: ... 150 -> 450", "camera zoom: getting on, target ... -> all the way out" and "getting off ... back to ...". If it says "aren't fractions" or "no third-person camera state", send the log (the zoom is left alone then). Try MCM "Riding camera distance" 450–600 and say which feels right |
| 17d | *(F4SE plugin)* Ride up and down a hill, across a side slope, over a curb and some rocks, back up a slope, and jump off a ledge; get off and on a few times. Record it if you can | the bike pitches nose-up uphill and nose-down downhill (also reversing), at most 45° (MCM "Bike tilts with the ground", the climb limit), smoothly, no twitch at a curb or a rock lip and no jitter on rough ground; over a lip or a crest the nose comes up as soon as the front wheel is on it, and the wheels stay on the slope (test 29: the bike sank into slopes and the pitch lagged at edges; the lift is up to 60 now); ridden at a boulder face too steep to climb, the bike stops short of it rather than putting its front wheel into the rock (two rays forward at axle height and near the wheel's top, as far as 0.3 s of the speed past the front wheel, ease the throttle off towards a face steeper than the climb limit, to nothing at the wheel: "rays: a face ahead (N deg): M past the front wheel at axle height, the throttle eased to X%" lines in the log; `FaceLook` in CMB_Slope.ini; test 31's quarter-second cut, whose word came with the face already at the wheel, stays as a backstop); over small hills, stones and curbs the tyres stay on top (test 33: they sank in; a wheel that would sit below its own ray's hit is lifted out, the bump part straight to the deficit under it and never above it, settling over `BumpSettle` 0.45 s; the whole lift, filtered part and bump together, rises at most `LiftRate` 120 units a second, so no launch: test 34's rose 60 in a frame, test 35's 34 in a quarter second at 900 units a second, and the bike jumped; since test 36 the wheels follow the ground on their own within 10 units of the frame and the frame settles with one small rebound over a step or a drop (the suspension: `Suspension`, `SuspFrequency` 2 Hz, `SuspDamping` 0.6 (0.5 was a tad too soft in test 37), `SuspTravel` 10 of compression, `SuspDroop` 4 of extension for both wheels (test 38: at -10 the sliders left the stanchions, and the look was "a bit too much, like there was no weight behind it"), a wheel extending over `SuspExtend` 0.1 s and compressing within 0.03, the frame sinking by the droop at most where both wheels' ground is below the rider's contact (no wheels hanging at -10 at a stop), the rear rising into the frame at most `SuspCompressRear` 4 (its mudguard is on the frame: test 37 found the tyre in it at +10), the lower fork legs, front mudguard and caliper riding with the front wheel's travel since test 38, along the steering axis since test 39 (test 38: they moved along the bike's z, 4.9 off the raked stanchions at full travel, "forks were getting out of tubes"): look at the front end over bumps and say whether the travel looks weighted now; the trace's "susp F/R" says how far each wheel sits off the frame: say whether it reads as suspension and whether the rebound is too much or too little); the bump part at most `BumpMax` 30, 1.5 wheel radii while an obstacle verdict is in force, so a 35 to 45-unit stone doesn't leave the tyre 15 units in it); a fallen tree or a knee-high stone (lower than 1.5 wheel radii; a trunk or a stump lower than the face rays look, met by the capsule between the wheels: row 17i) is ridden over at 55% throttle without stopping first (`ObstacleThrottle`, 0.4 crawled in test 37; "rays: an obstacle lower than 1.5 wheel radii ahead ... the throttle held to 55%"; a face is an obstacle only at 50 degrees or more since test 37 (`ObstacleAngle`; ten of 39 holds were faces of 45 to 49, which the bike climbs), a low one, with nothing at 1.5 wheel radii, only at 60 or more since test 38 (`LowObstacleAngle`; five rock faces of 50 to 57 held the bike to 55% that it rides over anyway: fewer holds on low rocks now, the "rays:" lines still name what held), and an obstacle whose hit is at or behind the front wheel's edge sets the hold but leaves the throttle free ("left at 100%", "at the wheel: the throttle free, the suspension's"; 16 of the holds were the ground under the pitched bike): fewer holds on slopes, none once on top; test 35 stopped first and then went over: once on the stone the hit lay behind the front wheel's edge and the verdict flipped wall, obstacle, wall; now a hit half a wheel radius or more behind the wheel's edge, with the front wheel's ray finding the ground half a radius or more up (the bike on the thing), is under the bike, an obstacle and never a wall (a wall the bike nosed into, its front wheel through it over flat ground, stays a wall and stops it), and after an obstacle verdict a wall needs `WallFrames` 5 frames ahead of the wheel while `ObstacleHold` 1 s runs; the "rays:" lines name what the ray hit and its collision layer, and never say "a wall" more than 15 units (half a wheel radius) behind the front wheel; test 35's bushes with food items stopped the bike like a wall: they were layer 15, non-collidable, which the rays now pass through along with everything the character controller's own collision layer doesn't collide with, read from the game's COLL record on each load (the log's "rays: the character controller's collision layer ... collides with layers ..." line: send it; test 37's read the record at the wrong offsets and fell back to the built-in table, so the line should list the layers now), the phantoms that list holds (spells, cloud traps, the pick and query layers, actors, trap triggers, character bumpers) passed through besides since test 37, and the rider's own capsule and body are passed through too (test 36's four 40% holds at -125, a unit past the rays' start, were the rider's own 3D): a bush, a hubflower and a navcut gap in front should give no verdict; an animal or a person in front still stops the bike short of it, their capsule being solid to the face rays ("rays: a wall ahead ... (SkeletonExport, layer 30), the throttle eased to 0%" in test 39), but the bike doesn't rear up at one now: test 39's radstag, the front wheel's ray took its capsule, 107 above the feet, for the ground and the bike reared up at it for 0.6 s; since test 40 the wheels' rays pass through actors, "rays: a ground ray passed through ... an actor, not the ground" with `Trace=1`), a boulder face of 55 degrees or more (`WallAngle`) stops the bike as before; across a slope it stays upright; in a turn at speed the bike and the rider lean into it gently (half the physical lean for that speed and turning rate, the turning rate smoothed over half a second, at most 14 degrees and 30 degrees a second: test 32's jumped 18 degrees between quarter seconds on a side key; `MaxLean`, `LeanRate`, `LeanSmooth`, `LeanDead`, `LeanGain` in CMB_Slope.ini, read again on getting on; nothing below walking pace), the rider's head staying level with the horizon (`HeadLevel`), straight again as the turn ends; with A/D the heading eases into the turn over about 0.14 s and out of it over 0.08 s when the key is let go (`TurnEaseIn`, `TurnEaseOut`; test 33: it snapped, a snake; test 34: 0.35 s felt heavy), the lean keeping up (`LeanRate` 50), the mouse as before; it keeps its pitch in the air and standing still; every ride starts level. The seat and bars stay under the rider. `CMB_Slope.log` has a "trace:" line every 0.25 s: "pitch from wheels" (two rays under the wheels, with the lift and how many rays missed), "track" where a ray misses, "normal" in the first metre of a ride without rays, "held" in the air. Send it with the video times |
| 17e | Ride at least a couple of bike lengths, stop, get off: on a slope, beside a curb, right after a U-turn; then ride up a rock face steeper than you can walk (about 60°), also diagonally, and try to get off on it, also after turning sideways on it; ride back to the top or bottom and get off there; also park along a steep side slope | the bike stands on the ground you just rode over, a bike length and a half away, facing the way you rode there; on the rock face, or anything steeper than 45° (a bit less than you can walk up): "Too steep to get off here." (the log says how steep); after a steep stretch or along a side slope the bike goes back to where the track was 45° or less and leaned 20° or less across. `CMB_Slope.log`: "park: on getting off, the spot last written (... s before)"; Papyrus log: "Parked bike tilted to the track just ridden" or "Parked bike level on ..."; parked on a steep stretch the pitch can go up to 45 (the roll stays within 10) and both wheels touch. Get on and straight off without moving: beside you on the navmesh, or level at your height where it's too coarse |
| 17f | *(F4SE plugin)* Riding: ride slowly and fast and turn hard; try a U-turn at walking pace and at speed. From a stop, hold left (then right) alone for a few seconds, camera behind you, then with the camera swung to the side. Then reverse: stop, hold back for a few seconds (the camera behind you), then back and left, back and right; also hold back with the camera looking at the front of the bike, and back towards a wall. Note the times | moving, it turns as in test 12 (wider the faster). A side key from a stop: the bike turns about 60° a second and crawls forward slowly, round a small circle (about 55 units, `CreepRadius`), it doesn't ride off. Back: the bike doesn't drive forward or turn round; it should roll back slowly (about 80 units a second) facing forward, or at worst stand still; with a side key the rear swings that way, and letting go of the side key (still holding back) stops the turning; letting go of back, no creep starts on its own. Backing into a wall: it stops with its rear just short of the wall, not through it; backing towards a drop: it stops with the rear wheel at the edge. Back + left/right next to a car or a wall: the rear swings only until it would touch, then the bike stops (or backs up straight if that's clear); the other side key swings it away. Backing down a steep slope: it stays on the ground and pitches with the slope. Backing along a level road, and down a gentle slope: the bike stays on top of the road, it doesn't sink into it (test 39: each gap under the feet closed onto the road while the controller held itself supported was followed by the controller in the air and the player 20 to 37 units down through the road; since test 40 a gap is closed only while the controller isn't supported, and since test 41 only down to the controller's own clearance, 0.5 at least, each step following the ground under it: row 17j). Backing with Dogmeat or anyone behind: it stops; one beside the rear wheel isn't taken for the ground. Back and a side key: the bars turn the key's way (test 38: they followed the nose). Backing off something the front wheel climbed (a car, a boulder, a ledge, a collapsed roof): the bike comes down nose-up with the rear wheel on the ground, not half under it (test 38: the lift dropped to 0 while the pitch was held at 41; it is held with the pitch now); send the "rays: the wheels' rays" lines if any part still sinks (since test 40 they come from a hand of 10 refilled by one every 6 s, with a hand of their own while backing: test 39's 30 a ride were spent by 01:35:02, before the backing tests). The riding tilt's default is 45 now (MCM up to 50), the climb limit, so the wheels stay on a rock face. Backing into a chain-link fence: it stops; over a tin can, a dropped gun or a body: it doesn't. Backing up onto a curb, and along a raised slab: no stop, no sinking in. A side key with the bike stuck against something, then free: a short lurch at most, then the creep; on rocks the creep takes a second to get going, then holds. The log's "rays:" lines carry the gap under the feet, the step's dz, whether the rays had the feet on the ground, and the controller's state, support count, fake support, in-air-pre-move and flags: with those, `BackSink=1` (a gap is closed to 1 below the controller's own clearance since test 41, 0.5 at least; with `BackFollow=0`, test 40's rule, to 1 below the 0.5 hover, the feet half a unit into the ground) and `BackSupportCheck=1` in `CMB_Slope.ini` are worth a run each on the same slope, to see whether either keeps the state at 0 (the supported bit 1) while backing down. A side key held still for seconds without the creep starting would show in the "creep:" lines as "[mode changed N times, keys kept]". Needs F4SE's Address Library (`version-1-11-240-0.bin`) for the rays. Say what it does, and whether the rider stays seated. The log: "input: MovementHandler ... wrapped" once; "creep:" lines (the game gets (0, small), the movement last used the same, "moving +N along the heading (want 58)"); "reverse:" lines ("the game gets (-0.00, -0.00)", "pushing back by steps after rays", "moving -N along the heading", with "rays (filter 30): the ground ..."), the Address Library line and "a test ray down beside the bike (filter 30) hit ... rays work", "stopped: something behind (knee height, left), N units back (name, layer L, at ...)", "not turning (that way: ...); backing up straight", "a ray passed through ... (layer L)", and "steps after rays moves the bike back: kept". Please send the log even if all looks right |
| 17g | The Sketchfab model (its look since the 2026-10-31a build: row 17s): look at the parked bike close up and from across a street, in daylight and at night, then at yourself riding in third person from the side, the front and behind, standing still and at speed; also the Pip-Boy's lighting on it at night. Screenshots of each | a cruiser the size of the old bike, deep red tank and fenders, chrome that reflects the sky, black engine and frame, translucent headlight and lights; the rider's hips on the seat behind the tank, hands on the grips with the arms nearly straight, feet on the pegs under the hips, the left foot down at a stop; nothing of the old bike shows; it doesn't pop out at the screen's edge; the parked bike bumps and blocks as before (the old bike's collision). With F4SE: the wheels turn with the ground going by (backwards when reversing, still at a stop), rims, spokes, discs and tyres together, and the whole front end (forks, bars, grips, levers, mirrors, headlight, front wheel) turns 20 degrees into a turn at a stop or at walking pace and about 12 at speed, all the way only in a real turn (90 degrees a second of turning; a creep turn is two thirds), the hands on the grips at any bar angle, the grips, levers, switch housings and mirrors turning with the bars together with the hands (test 35: the hands turned, the grips and the left mirror stayed with the frame), the elbows bending to reach rather than the forearms stretching (since test 29 the clips keep the hands at the straight grips in every pose and the plugin moves the arms with the bars: the hand to the turned grip, the elbow by a two-bone solve since test 30; `RiderHands=0` in CMB_Slope.ini for the A/B; the log says on the hold whether each side's shoulder, elbow and hand nodes were found ("rider:   the arms' chains: ..."), once a ride per side when the arm is first solved, with the upper arm's and forearm's lengths, the grip's distance from the shoulder and how far the elbow moved ("rider: the left arm solved: ..."), and which plain shapes move with the arms or the head and in which role ("rider:   plain shapes moving with the arms or the head: ...": the Pip-Boy's screen is there with the forearm since test 32); the upper body leans forward so the grips sit at 80% of the arms' reach with the bars straight (`ArmReach` 0.80 since test 39, 0.88 before; test 32: the clips lock the arms straight; "rider: the upper body leaned N deg forward ..." in the log; `TorsoLean` in CMB_Slope.ini, -1 = as needed, 0 = off, `ArmReach`) and turns toward the far grip in a turn (`TorsoTwist`), the elbows bending rather than the wrists stretching at full lock, the head keeping its own pitch; since test 36 the chest turns 0.75 of the bars (`TorsoTwist`, was 0.4) and leans into the turn by 0.25 degrees per degree of the bars (`TorsoSideLean`), so at full lock at a crawl, seen from the front and above, the inner shoulder goes back with the inner grip and that arm is bent, not folded, the elbow out but not back; the hand rolls round the grip since test 37, and since test 40 so that its long axis, the knuckle line, lies along the forearm seen along the grip (`WristRoll` 1.0 of the way, `HandPitch` 0 degrees above it, + = the knuckles up; test 39: "cat paw", the fists bent down at the wrist, the old roll keeping the clips' fixed bend; the clips lay the hand the same way now, so the roll is only the plugin's forearm moving from the clips' with the lean and the bent elbows, likely 10 to 20 degrees at rest, as "the hand rolled N round the grip"; `WristRoll=0` = the hand keeps the clips' orientation, turned with the bars: test 37 read the wrist 25 degrees off the clips' pose at the straight bars and 42 to 46 on the inner wrist with the bars 8 over), so look at the wrists at rest and at full lock from the front, the side and above: the back of the hand in line with the forearm, no bend down at the wrist; say whether they want `HandPitch` a few degrees either way (read again on getting on); send the "rider: the left/right wrist turned at most N deg from the clips' pose this ride, on the steady frames" lines from the ride's end (since test 40 from the steady frames alone: the arms still, the grip at 50 to 103% of the reach, the clips' hand at the bars, a second clear of the ride's start and of a jump; test 39's 136.7 and 161.0 degrees came from the frames with the map open for a fast travel) and the "rider: the left/right arm solved" lines' wrist and roll ("the hand rolled N round the grip, aligned with the forearm: its axis N deg above the forearm's seen along the grip (HandPitch N)"; since test 39 the roll pivots on the grip's centre, `Grip` in the parts file, so the palm stays on the bar: the "parts" line after getting on names it); the "rider: the left/right arm solved" lines give the grip's share of the reach; the lean is solved 1.3 s in (`TorsoSolveFrom`; half a second before test 40) and again every half second till it's final, the best reading kept, final on two readings of the riding pose that agree or 3 s in (test 33's first ride solved 15 degrees before the pose settled; test 39: at five of six ride starts the first reading, 0.8 or 0.9 s in, read 100% with 15.9 to 21.1 degrees, against 14.6 half a second later), and the final lean is always in the log (", final" on the "leaned" line, or "rider: the upper body's lean final at N deg"), but not while the arm bones jump or the grips read under 95% of the reach (test 37: the Pip-Boy opened a second after getting on set a 0 lean for five minutes): open the Pip-Boy within a second of getting on, close it and ride: "rider: the upper body's lean not solved yet" and then "rider: the upper body leaned N deg forward" in the log (opened later, the lean solved before it stands: "rider: the upper body's lean final at N deg ... (the grips at 82% now)"; the lean is first solved 1.3 s in since test 40); hold the Pip-Boy open over 20 s from within a second of getting on, close it and ride: the line "taken as it comes" at 20 s and then "the riding pose came: solved again" (test 38: the 20 s fallback would have kept the 0 lean); a fast travel on the bike, riding on at the destination: the lean stays what it was before the fast travel (about 14 degrees), "the upper body's lean final at N deg: the solve from before a jump of N units (a door, a fast travel) stands" about 3 s after it, or, if a reading beats it, "solved again after a jump of N units (a door, a fast travel)" (since test 40; test 39: both fast travels arrived moving, the grips at 92 to 95%, and the lean fell to 11.1 and 11.4 degrees for the rest of the ride; test 38: a fast travel leaves the rider held, nothing re-solved); the fingers (test 33: the tips of both hands stretched into spikes since test 30; test 34: 34 of the hands' 36 bones have no node): held through their own world transforms now and mapped with the hand or the forearm by where they sit (the log's "rider: NakedHands...: 34 bones without a node, held through their own transforms: N with the left hand, N with the right, N with a forearm, N carried with the tilt alone" line, and the "bones:" dump with "(no node, its own transform)"); look at the hands close up, bars straight and turned: no spikes, the fingers curled on the grips; the hands sit on the rubber grips now (the fit's grip re-measured from the model in test 38: the sleeve's centre at x 29.4, y -10.7, z 96; test 37's x 24.5 put the palms on the lever perches and switch housings), the arms a little wider; since test 39 the upper body leans about 14 degrees (`ArmReach` 0.80, was 0.88 and 6 to 9 degrees) and the elbows bend down and a little out (`ArmPole`; test 38: "arms still look broken", the elbows out at shoulder height) toward the tester's reference riders, the elbows tucked under the shoulders, the forearms nearer level (since test 41 out as much as down, for a level forearm, and the inside arm eased back in a turn: row 17k): say whether it reads as a rider now, from the side and the front, at rest and at full lock; the body's skin helper bones (belly, breasts, shoulder and upper-arm fat, rib helpers) move with the torso and the upper arms since test 39 (before, they stayed where the clips put them: a hump on the upper back and caved shoulders as the torso leaned), logged as "rider: ...: N bones with no part by name take their parents'": look at the upper back and the shoulders from behind and above; `RiderHands=0` for the A/B; tests 21-28's clips were posed with turned bars and the hands came off in every blend), straight again when you stop turning; on a slope the rider pitches and rolls with the bike about the contact under the rider (test 29: about the seat the lower wheel went into the slope; test 23: the bike pitched 20° under a level rider, hands in the air): the hands stay on the grips and the hips on the seat at any pitch, the head looks down the hill on a descent; a holstered weapon and the Pip-Boy go with the body; nothing on any NPC changes (their meshes share the player's bone data, which the plugin copies rather than writes); every skinned shape of the rider is held or none is (test 24: the suit was refused for a bone with no vertices and stayed level while the body pitched, tearing the rider), so a rider that stays level on a slope means a shape's bone data was refused and the log's "rider:" lines say which, its bone and the check (a bone whose node can't be read or is hidden is just left as it is, logged with its values; a cloth bone's sheared transform is carried along; a shape whose skin instance the game replaces, a decal's say, is held again within 0.1 s and the log says so); they also list every shape held, a line at a time. Frame rate (test 25 lost about 30 fps with the rider held): compare the fps on foot, on the bike with the MCM tilt at 0 and at 20, and with each of `RiderSkinned`, `RiderPlain`, `RiderSwap`, `RiderWrite` set to 0 in turn in CMB_Slope.ini (read again on each getting-on: change, get off, get on); the log's "time:" lines give the plugin's own cost per frame in microseconds and the memory queries a frame (test 26: each one cost 100 us there, 39 a frame; none now, and the skin sync's count is on the line too), so a frame that costs the plugin 50 us while the game loses 7 ms points at a side effect of what's written, and the switches say which and "parts:" (with `Trace=1`) give the bar angle and the turning rate. The chrome is a mid grey with the sky in it, not white (test 20); the tank badge is satin black (since the 2026-10-31a build: chrome dark with the sky in it, our own winged-wheel badge, row 17s). Say if any part is see-through, black, missing, too shiny or too dull, whether the red suits (`--body` takes another colour), and whether the bars should turn more or less. Reverse: the first back press of a session judges the method only once the bike is at rest with no side key, and a failed verdict is retried 3 s later (test 20 pressed back at 900 with a side key and lost reverse for the session): press back while still rolling, then from a stop, both must back up. The throttle (tests 21-23): W builds the speed up evenly over about 3 s from a tenth of the top (the input is set from the measured speed curve, so the speed, not the input, ramps), with or without a side key held, and never more than a fifth of the top ahead of the bike's real speed (from a stop the first second is the game's own getting under way, then the ramp; stuck against something with W held, the bike moves off gently once free, no lunge); letting go lets the bike roll off over about 2 s; S brakes it off in under half a second, the bike runs down, and only once it has stopped does the reverse start (no roll back after letting go of S while it's still rolling on); a side key alone creeps only once the bike has rolled off. Say whether the build-up, the coasting and the brake feel right (`[Steer]` `Accel`, `Coast`, `Brake` in CMB_Slope.ini; `Throttle=0` is the old feel); the log's "throttle:" lines give the speed fraction and the input written |
| 17h | *(F4SE plugin)* Get on in daylight with MCM Headlamp "On", then "On at night" after dark; press the headlamp hotkey (MCM > Hotkeys); ride, turn, go up and down a slope; look at the lamp from the front and the side, parked and ridden; MCM "Headlamp casts shadows" on, get off and on; get off | No lamp piece since test 35 (no `CMB_BikeLamp*.nif`, nothing in slot 58 touched): the beam is the light reference the controller places. A 5.75" round LED lamp with a chrome bezel on the fork bracket, turning with the forks; its running-light ring and projector face lit only while the lamp is on (a speck otherwise; plain white on the parked bike), and since the 2026-10-31a build the speedometer's numerals with them (`[Speedo] Backlight`, row 17s); with the lamp on, a warm-white spot beam on the ground ahead that turns with the bars and tilts with the bike, off when parked or when the hotkey says so ("Headlamp on/off"); "On at night" lights it after 19:00 and before 6:30. The Papyrus log: "Headlamp light placed (N)", "Headlamp lit/out". `CMB_Slope.log`: "headlamp: the lens at ...", "lamp: the light reference N the script placed: its 3D '...' (..., N child(ren): ...) put at the lens ... the beam along ..." (send that line whatever it says: the light's node names tell what the game made of the reference). Across cells: ride a few hundred metres at night with the lamp on (test 32: the beam went after 25 s, the reference's cell unloaded behind the bike; test 33: moving it at every cell crossing made it flicker; now a fresh reference is placed once the bike is two cells from where the last was placed, "Headlamp light handed over (N) in cell X, Y." in the Papyrus log about every 9 s at speed, the old one kept at the lens by the plugin until the new one's 3D is in and parked then: "lamp: the light handed over from A to B: the old one parked (the new one has its 3D)"; the beam should not flicker at a handover; CMB_Slope.log still says if a reference's 3D is ever gone while the lamp is wanted). Test 34's one-to-three-frame blackouts at speed: the light is placed 28 units ahead of the lens along the beam and led by a frame of the speed (`Ahead`, `Lead` in CMB_Slope.ini, read again on getting on), the old light of a handover stays 5 frames after the new one's 3D is in (`HandoverFrames`), and the worn bike's front end casts no shadow (the parked bike keeps its sun shadow since test 35); say whether any blackouts are left at full speed over bumps and in turns, with shadows on and off (test 35: none in 3.5 minutes of night riding). The beam reaches 4000 units at 78 degrees and fade 2.4 now (test 35: 85 degrees and 2.7 were a bit too wide and a little too bright): say if the width and brightness are right now. The hotkey leaves the MCM's mode alone: with "On at night" set press it by day (the lamp lights, the setting still reads "On at night"), get off and on (it's off again by day), press it at night (out), and wait for dawn or dusk (its say ends). Nothing in slot 58 is touched any more (the lamp piece went after test 35: "Slot 58: nothing" at tick 2 as well, the placed light does the job): the Papyrus log's "Slot 57:" line (once the bike is on) says what the biped holds there and which model, and there is no "Slot 58:" line and no "lamp: ... CMB_BikeLamp*" line. If the beam points the wrong way: `[Lamp] BeamAxis=` in CMB_Slope.ini (x, y, z, -x, -y, -z), get off and on; if there's no beam at all, say whether the lamp's ring lights up with the hotkey and send both logs |
| 17i | *(F4SE plugin; tests 41 and 45)* Off-road among fallen trees and stumps (north of Red Rocket, as in test 40): ride at them with forward held, straight on and at an angle, at speed and from a crawl, and with a stump beside the bike; then the rock pile of 15:42:24 and a rocky slope. Note the times | over a fallen trunk or a stump lower than a wheel (about 30; since test 45 a trunk lying on the ground, round, and a stump, narrow, still; a rail or a beam over 18, `ClimbMaxTop`, only where the ground goes on at its height a wheelbase past it, as on a step up: row 17n) the bike goes on without a stop of over a second (test 40: four dead stops in three minutes, 900 to near 0 in half a second, stuck 1 to 3 s: the player's capsule met the trunk's side between the wheels, which the game's 47-degree climb limit makes a wall, and no ray looked that low). `CMB_Slope.log`: "climb: the capsule radius N, height N …" once a ride; "climb: a low face at the capsule (what, layer N): N ahead at 4, … at 10 (N deg), nothing at 31.9 within …; the wheels' pitch …, the ground normal …, speed …: the climb limit 47 -> 85", then "climb: over it after N s (the feet N up, speed N -> N, N on along the heading): the climb limit back to 47", or "climb: cut after N s: …", "climb: off after …" or "climb: given up after N s stalled …". Stuck at a sharp-edged stump (17 to 32 high, its side upright to the capsule, which no limit climbs): "climb: stepped up N (the top N at N-N ahead, the rays down reading …; what, layer N) and 4 on, room for the capsule's 128 over it [1 of 2]" and the bike on top, or "climb: no step: …" with why, or "climb: the step up didn't take: …". Stopped with forward held and nothing climbed: one "climb: stopped with forward held (…): not climbed: …; the rays: …" a stall, the reason naming what kept it (nothing low ahead of the capsule, the wheels' line pitched over 22, a wall ahead, an actor, something at 31.9 above the feet): send those with the times. The rock pile and rocky slopes aren't climbed this way (test 41's answer, trunks and stumps only: `ClimbMaxPitch` 22, the four stops read 5 to 20 under the wheels, test 40's rock pile 31 to 37). Since test 45 the boost's line says why a trunk or stump taller than 18 was let through: "…; at 18 N ahead: round, receding toward its foot (ClimbMaxTop)" for a trunk, "…: narrow, the ray 36 to the left passes it (ClimbMaxTop)" for a stump, "…: a step up, the ground N over the ground at its foot …" for a step; a trunk sunk in the ground so its face is upright, with the ground behind it lower and as wide as the bike, is a beam and stops the bike: "climb: stopped with forward held (…): not climbed: a beam with a drop behind it, not a step up: something at 18 above the feet N ahead (what, layer N; ClimbMaxTop), not round (N deg at its foot) and long (…), and a wheelbase on, N ahead, the ground N over the ground at its foot (…)": send those with the times, and say whether any trunk or stump stopped the bike that you'd expect it to climb (`ClimbMaxTop=0` is test 44's climbing). Say whether going over a trunk looks like a hop, a float or a lurch, and whether the stump's step up looks right. `Climb=0` in CMB_Slope.ini (read again on getting on): never, as in test 40; `ClimbStep=0`: the boost alone, no step. Since test 46 a stump or a trunk over 18 is narrow only where the rays to its sides pass it at 18, 24 and its top less 4 (`NarrowHeights`), and one lower than 18 but 8 or more high is judged too (`ClimbBeamLow`): a kerb or a step whose top goes on, a log (not upright) and a stump (narrow) still climbed, the boost's line saying which ("; its top 12.0 over its foot: a step up, the ground 12.0 over its foot 36 past its face (ClimbBeamLow)", "…: not upright (N deg at its foot, N at its top), a log (ClimbBeamLow)", "…: narrow, the ray 36 to the left passes it at N (ClimbBeamLow)", "…: too low to tell (ClimbBeamLow)"); a low upright face as wide as the bike with a drop behind it (a rail or a plank lying on the ground, a log sunk to an upright face) stops the bike, "… not climbed: a low beam with a drop behind it: …" (row 17n): say whether any trunk or stump stopped the bike that you'd expect it to climb (`ClimbBeamLow=0` and `NarrowHeights=1` are test 45's). Since test 47 (`NarrowBoth`, row 17n) the side rays go across the face, into it along its normal from 36 out and 36 to either side, and a face is narrow only if both sides pass it: the boost's line reads "…: narrow, the rays 36 to either side across its face pass it at 18 and 24 (ClimbMaxTop, NarrowHeights, NarrowBoth)" ("…across its heading" with no usable normal; a low one "; its top 12.0 over its foot: narrow, the rays 36 to either side across its face pass it at 9 (ClimbBeamLow, NarrowBoth)"); a stump or a rock wider than about 72 along its face met off its middle, which one side passes, now reads long and is climbed only as a step up (its top going on), held otherwise ("… long (the ray 36 to the left passes it, the one to the right meets it, …); the side rays cast across its face, its line N deg off the heading (NarrowBoth)"); round logs are as before. Say whether any stump or rock you'd expect to climb now stops the bike (test 46's tyre pile at 17:16 of its video, just after the truck, is one to try again), with the time; `NarrowBoth=0` is test 46's. The "rays: nothing ahead now (was …)" lines name the verdict that stood, what and for how long, 20 of them at a ride's start and one more every 3 s (test 40's 60 a ride were spent in two minutes off-road, and the next three stops had none) |
| 17j | *(F4SE plugin; test 41)* Back down the slopes of test 40 (15:42:49, 15:43:05, 15:43:13) at the reverse's 80 a second, a gentle one and over a brow too; then along a level road. Record it | the picture steady while backing downhill, no small jumps of the background (test 40: the whole picture shook while the bike stayed put on screen, about 5 px at 1080p; the bike's applied pitch was smooth, 12.0 to 8.9, while the controller said it was in the air most of the way and the game's gravity carried it down in hops the camera followed); the bike on the ground all the way, not sinking, over the brow and a dip too. Since test 41, backing level or down, each step follows the ground's slope over 10 units under the step's middle (`BackFollow`), the controller supported or not, and with it unsupported a gap is closed only down to its own clearance. The log (`Trace=1`, the default): each "rays:" line ends "; follow N by the window (the ground N ahead, N behind over 10), own N, closing N" (or "held", "by the slope 55 back", "an edge"), and the "  height: z N (ours N over N calls, the game's N); a call's vertical speed changed N at most; supported N of M calls; the controller's velocity z …" line after it should have the game's share near 0 and small changes of the vertical speed; "reverse: the controller in the air after N s supported …" and "… supported again …" at its flips (once a second at most), and "reverse: a push back starts, …" with the capsule's size and the controller's gravity field (+0x330). Say whether the view still shakes. `BackFollow=0` in CMB_Slope.ini (read again on getting on) is test 40's rule, for an A/B on the same slope |
| 17k | *(F4SE plugin; test 41)* Ride a straight road at speed for a few seconds, then turn at full lock at a crawl, both ways; look at the arms from the side, the front and above | the forearms near level to the grips, the elbows a little further out than in test 40 and low (test 40: the upper arm went down and forward and the forearm rose 14 to 18 degrees to the grip; test 41's answer: a level forearm matters more than the elbow under the shoulder): `ArmPole` 1.1,-0.3,-0.9 since test 41 (test 40's 0.35,-0.3,-1.0), picked by an emulation of the plugin's arm solve on the rig and the clips as the flattest forearm with the elbow at most a unit further out than at 1.0,-0.3,-1.0 (wide elbows were test 38's complaint). The log, once a hold at speed (over 300 for a second, the bars straight, the arms still, the lean final): "rider: the arms riding (N a second for N s, the bars N deg, the upper body N deg forward): the left arm: the elbow N out, N forward, N below the shoulder (the upper arm N deg below level), the forearm +N deg to the wrist seen from the side (+ rising), the pole (…), the wrist turned N deg from the clips' pose, the hand rolled N round the grip; the right arm: …"; the emulation expects the elbow about 14 out and 11 below, the upper arm 38 below level, the forearm +6 at the run clip (+4 at the walk) and the wrist 16 to 17 degrees from the clips' pose (test 40's pole: 9 out, 15 below, +18, the wrist 10). The "rider: the left/right arm solved" lines at getting on, the idle clip, carry the same figures: about 12 and 15 out, the forearms +1 and +2. In a turn the inside arm (on the side the bars turn to) eases back to test 40's pole by 10 degrees of the bars (`ArmPoleTurn`, `ArmPoleTurnBars`), so it bends in rather than folding out: its wrist about 21 degrees from the clips' pose at 4 of the bars, 24 at 8 and 31 at 12 (52 at 12 without the fade), the outside one about 18; its arm line ends ", N of the way to ArmPoleTurn", and the ride-end wrist lines say "the elbow's pole N of the way to ArmPoleTurn". Look at the elbow's crease and the shoulder's skin with the elbow out, and at the wrists with the bars straight: say whether it reads as your sketches now. `ArmPole=0.35,-0.3,-1.0` with `ArmPoleTurn=0,0,0` (read again on getting on) gives test 40's arms back exactly |
| 17l | *(F4SE plugin and CMB_RamScript; tests 41, 43 and 45)* Ride straight at a raider (or a feral ghoul, a mole rat) at full speed; then at two close together; then at a pack (test 42's `LvlViciousDog` five times: coyotes in that load order), through it and back at it within ten seconds; at a protectron, an eyebot and a mutant hound, the hound coming in from the side too; then the same with MCM "Knock enemies over" off; at a settler; at a super mutant; at your companion standing in the way; and slowly (under 450 a second) at an enemy. Since test 45 also: through packs of dogs, wolves or coyotes at speed, some coming in from the side (test 44, 22:47 to 22:49); at a protectron through its middle, head-on, then turned and at it again within 3 to 4 s, twice (as at 22:49:56 and 22:50:13); and at an enemy right after braking hard from full speed, so the bike is slow when its answer comes. Note the times | at speed the bike doesn't brake for the enemy and knocks it aside: `CMB_Slope.log` "rams: XXXXXXXX (race …: medium) seen N past the front wheel at N a second (…): asked the script (ask n)", "rams: XXXXXXXX may be knocked over, the script says (ask n), N ms after the ask", "rams: XXXXXXXX hit at N a second, N past the front wheel: told the script (ask n); the throttle held to 60% of it (540 a second) for 0.40 s", and in the Papyrus log "Ram: XXXXXXXX may be knocked over (ask n)." and "Ram: XXXXXXXX knocked over at N a second (ask n): force F, D damage, health a -> b.": it loses about a tenth of its health at riding speed (`CMB_RamDamage` 10, the last of it a kill with `CMB_RamKills`), and the bike loses some speed and builds it up again over a couple of seconds (test 41's answer). Two close together: both knocked over, the hits told 0.12 s apart at least, and since test 41 the asks too (`AskGap` 0.12; test 41: five "Ram: N of the plugin's asks went unread." lines in packs, a second animal seen 46 to 120 ms after the first replacing the first's ask before the script's 0.1 s poll read it, the plugin asking again when it next saw it, no hit lost): none now; since test 43 each ask is told once the one before it is answered (`AskAnswered`), so the second one's lines read "rams: … seen …: its ask waits for the answer to ask n (AskAnswered)" and then "rams: …'s ask told the script (ask n) N ms after it was seen, N ms after the answer to ask m". The pack (test 42: "dogs were strange", some knocked over and some stopping the bike: the answers took 234 ms at the median while the asks went out 120 ms apart, and a dog not yet answered was braked for as a wall at its ask's very millisecond, 20:47:05.987): the dogs knocked over one after another and the bike not stopped by the pack, at most the one whose answer didn't come in time braked for. While a dog's ask is pending it keeps the throttle: "rams: X ahead (N past the front wheel at N a second): its ask pending for N ms, the throttle kept (AskFree, a small race)"; "rams: X N past the front wheel, no answer in N ms: braked for" for one whose answer took over 0.5 s (send those with the times); a dog back within 10 s of its yes isn't asked again, "… to be knocked over, the throttle free (said yes to N s ago, kept)"; one slowed by the hit just before it is knocked over all the same, "… under CMB_RamMinSpeed's 450, but N s after a hit at N: knocked over all the same (HitGrace)" (test 42: all ten "under 450" lines came within a second of a hit or of a brake for a pending ask). A "rams: ask n (X) unanswered for N ms: the next ask told anyway" line means the script stalled: send the Papyrus log around it. The MCM switch off: no "asked" line, the bike brakes for it as before. A settler: "Ram: … is not knocked over: not hostile (ask n)." and "rams: … is not to be knocked over, the script says: braked for"; the companion: "a companion". A super mutant: "rams: … (race …: size …, flags …) is too big (MaxSize): braked for as before", or, if its race reads medium, "Ram: … is not knocked over: too big (its race is in CMB_RamTooBig) (ask n).". Slow: "rams: … under CMB_RamMinSpeed's 450: not knocked over, braked for". The smaller robots (protectrons, eyebots, Mr. Handy and Gutsy, assaultrons) and the mutant hounds should be knocked over; since test 43 the robots by a list of their own (test 42: "rams: … (race ProtectronRace: size large, flags 42E08901) can't be knocked down (No Knockdowns): braked for as before", seven times): once at the start "rams: CMB_RamRobots: 4 races pass the size and No Knockdowns gates: ProtectronRace (large, flags 42E08901, No Knockdowns), EyeBotRace (…), HandyRace (…), AssaultronRace (…)" (send it: the other three's sizes and flags aren't known yet), and the ask's line "(race ProtectronRace: large, No Knockdowns, in CMB_RamRobots)"; "rams: CMB_RamRobots can't be read (…)" or "… isn't there (an older ESP)" means the gates stand for every race: send it. Whether the push moves a robot at all, the Papyrus log says: "Ram: X 0.5 s after the push: moved N units." (a protectron that moves nothing needs another way: say what it did). The eyebot (test 42: never asked about, no EyeBotRace line, the capsule bumping into it; it hovers over the rays at axle height): "rams: X (race EyeBotRace: …) seen N past the front wheel at N a second (the high actor ray, 96 up): asked the script (ask n)"; if no such line ever comes, try `HighRay=75`, then `110`. The hound from the side (test 42: "hit at 715 a second, -67 past the front wheel", the front wheel over it before it was pushed): "(the right actor ray)" or "(the left actor ray)" on its lines and the hit told ahead of the wheel; say whether the push from the flank is right or too eager (`SideRays=15`), and whether any dog is still braked for in a pack. Send the "rams: actors are found from their 3D …" line (or "… gives no actor") and the "rams: the rider's race reads …" line, whatever they say: they tell whether the game keeps the actor where the plugin reads it (test 41: 'skeleton.nif' (layer 30) gave the actor from +0x110, and HumanRace read medium). Say how far they fly (the push's force is a first guess, 3 at 450 rising to 8 at 900; test 41: 3.5 to 8.4, the distance fine), and whether the damage and the slowing feel right. One stepping in from the side is seen only within about 45 of the bike's line (the side rays, 20 out, and an animal's girth), not further out. A "Ram: CMB_RamScript is not on the quest" line means an old plugin file. Since test 45 (a third "  ram:" settings line, "  ram: PendingPass=1 FaceActors=1 SeenGrace=1.5: a small race whose ask is still pending at the front wheel passed, its hit told when the yes comes; …"): a dog, wolf or coyote not yet answered by the time the bike reaches it is passed, not braked for, "rams: X at the front wheel (N past it at N a second), its ask pending for N ms: passed, its hit told when the yes comes (PendingPass, a small race)", then on its yes "rams: X hit on its yes, N ms after it was passed at the front wheel at N a second (PendingPass): told the script (ask n); the throttle held …" (or "…, N ms after the hit told before it: told the script once 120 ms have passed (ask n), so its 0.1 s poll reads both") and the Papyrus log's "Ram: X knocked over …" (test 44: 7 dogs "N past the front wheel, no answer in 25-234 ms: braked for" and 2 "under CMB_RamMinSpeed's 450" right after: "some dogs just stopped the bike"); "rams: X passed at the front wheel N ms ago, no answer since: the pass over (Pass), braked for if ahead" for one never answered (send it with the time); a medium or large one pending at the wheel is braked for as before. The protectron ridden at again after a hit: "rams: X seen again N past the front wheel (…), N s after its hit, N s out of the rays: asked afresh (FaceActors)" and knocked over again, its pending ask keeping the throttle ("… the throttle kept (AskFree, a large race in CMB_RamRobots)"), no "rays: a wall ahead (…): … (skeleton.nif, layer 30)" for it and no stop (test 44: both head-on passes stopped, "protectron stops bike when I'm aiming to ride through middle of it"); back at it sooner than about 3 s after its hit (`CMB_RamScript`'s cooldown), "…: asked afresh 3.3 s after the hit, once the script's cooldown is over (FaceActors), braked for till then" and braked for as before, then "… the script's cooldown over: asked afresh (FaceActors)" and knocked over, with no "Ram: X is not knocked over: knocked over less than 3 s ago" in the Papyrus log (send any with the times). Slowed by the brake or a capsule after it was first seen at speed: "…: under CMB_RamMinSpeed's 450, but first seen N s ago at N: knocked over all the same (SeenGrace)" in the hit's line, within 1.5 s of first seeing it (test 44: the protectron first seen at 873 and 788, its yes at 72 and 444, "under 450: braked for"); one never seen at 450 or more is braked for as before. Say whether a pack still stops the bike anywhere, and whether passing a dog before its yes and knocking it over a moment later looks right. `[Ram] Enabled=0` in CMB_Slope.ini: never, as in test 40; `HitHold=0`: the speed kept at a hit; `AskGap=0` with `AskAnswered=0`: test 41's asks, told as the actor is seen; test 43's `AskAnswered`, `AskFree`, `YesKeep`, `HitGrace`, `HighRay`, `SideRays` and `Robots` each at 0 give test 42's for their own part, on a second "  ram:" settings line, and test 45's `PendingPass`, `FaceActors` and `SeenGrace` each at 0 test 44's for theirs, on the third (all read again on getting on). Since test 46 (test 45: the dog FF0215FA and the wolf FF020983 refused "knocked over less than 3 s ago" and braked for at 4:26 to 4:34 and 10:20, nothing knocked over that session yet, and gone over normally from 11:08, after four new knock-overs had cycled the script's four-slot list: its stamps, kept in the save, were from the session the save was made in, test 41's, by those very dogs, and `Utility.GetCurrentRealTime` starts again with each launch, so they lay in this session's future; the refusals' own log stamps hid most of those lines too): the script clears the knock-over and refusal stamps on getting on and drops any later than now wherever it reads them, "Ram: N stale knock-over/refusal stamps from an earlier session cleared." when there were some (send it); no "Ram: X is not knocked over: knocked over less than 3 s ago" for an actor before it was knocked over in the session (one ridden at again within 3 s of its knock-over still is, as it should). No switch: a plain fix. Since test 47 (test 46: the fix worked, "Ram: 8 stale knock-over/refusal stamps from an earlier session cleared." and no "less than 3 s ago" refusal, FF0215FA knocked over five times; but 27 of its 32 knock-overs came after the console's `tai` at 7:47, the animals standing still, and 3 of the 16 yeses not knocked over were braked for under 450 after the bike had been slowed, by `WallStop`'s cuts among others (row 17n); the build-27b check: only a stamp later than now was dropped, so an old session's that fell in this one's last 3 s still counted): with AI processing on (step 1 of *Test 47* above) ride through moving packs again. The controller has the ram script clear every knock-over, refusal and push stamp at every load, "Ram: N knock-over/refusal stamps from before the load cleared." when there were some (send it); "Ram: CMB_RamScript is not on the quest: ClearStamps not called, nobody is knocked over." at a load means the ram script is missing. Say whether a pack still stops the bike, and whether any dog is braked for after a slowdown. No switch: a plain fix. Since 2026-11-01a (test 47: "you can't kill an enemy while on the bike, just take them down to the last bit of health"; the raider FF0198E6 knocked over 17 times and held at 1.0 twice): with the MCM's "Knock-overs can kill" on (`CMB_RamKills`, the default) the hit that would leave under 1.0 health kills it, the player the killer (`Kill(PlayerRef)`: the experience, kill quests and the rest as for a shot). Step 6 of the 2026-11-01a build: "Ram: on from 450 a second, 10% of their health, the last of it a kill (the player's)." at getting on; the killing hit "Ram: X knocked over at N a second (ask K): force F, the hit's D damage takes the last of its health (H): killed, the player the killer." (with " (protected: the game lets the player kill it)" for a protected one); 0.5 s on "Ram: X 0.6 s after the push: moved N units; dead, the killer the player, the player's experience A -> B." with B over A, and the HUD's experience popup (say whether it showed); for any push the 0.5 s line now says whether it died and who killed it ("dead, the killer the player", "someone else" or "nobody"); "NOT dead after Kill (health N)" means the game refused it: send it with the time. The switch off: "..., never the last of it." and "health 1.0 -> 1.0", as in test 47. The refusals are as before (companions, settlers, essential characters, children, power armor, the big races) Since 2026-11-02a (step 6 of its list): the throttle held to 85% for 0.25 s at a hit (`HitKeep`, `HitHold`; 0.6 and 0.4 before), a pack's hits one dip (`HitChain`: "(HitChain: of the N before the pack's first hit, N s ago)"), a medium race pending at the front wheel passed when said yes to this ride or with the player in combat (`PendingFoe`, `CMB_RamCombat`: "passed, its hit told when the yes comes (PendingFoe: ...)"), a dip line a hit ("rams: X's hit at N a second: the speed's low N (0.88 of it) N s after it; ..."), and the killing hit the player's own `CMB_RamKillSpell` (MCM "Kill experience": "(+N: the game's, Spell.Cast)" in the push's line; 2 is `DoCombatSpellApply`, 0 the 2026-11-01a build's `Kill(PlayerRef)`). |
| 17m | *(F4SE plugin; test 41)* Ride with the Hard Hat on, then with glasses, a helmet and a scarf or a collar; at speed with the upper body leaned, and through turns; look from the side and the front in third person | nothing stretched: the hat moves with the head through the lean, in one piece, the glasses on the face, the scarf with the neck (test 41: "helmet is sitting in 'default' position being stretched forward with character tilt"; the Hard Hat is weighted 71.5% to Head_skin, a bone with no node of its own, which the plugin carried with the bike's tilt alone while HEAD took the lean, so the dome stayed where an upright head would be and the front followed the head forward; most vanilla headwear is weighted like it). In `CMB_Slope.log`, at each hold, the piece's line: "rider: AAClothesHardHat (000F6D90)[1]/Armor_Ha: 1 bones without a node, held through their own transforms: 0 with the left hand, 0 with the right, 0 with a forearm, 0 carried with the tilt alone, 1 with the head, 0 with the upper body, 0 with an upper arm; 1 placed by the node they sit on, within 2 of it (NodelessNear): the head 1, the upper body 0, the hands 0, the forearms 0, the upper arms 0" (test 41: "1 carried with the tilt alone"); a scarf's Neck_skin counts with the upper body; the hands' lines keep their old counts first, the fingers still placed by the hands' rules. A piece still stretched: send its line and a screenshot. `NodelessNear=0` in CMB_Slope.ini (read again on getting on) gives test 41's hat back |
| 17n | *(F4SE plugin; tests 43 and 45)* Ride along a guard rail (the GRail rails of test 42, by the road at 20:55) with forward held, the heading 10 to 30 degrees into it so the bike meets it, at speed; then into it at about 40 to 45 degrees; then along a building's wall the same way; then past a lamp post or a tree trunk at the roadside, grazing it. Since test 45 also: straight at a wooden road barrier (as at 22:47:39 of test 44) and at a guard rail lying on the ground (the brush pile's border at 22:48:57), slowly and at speed, forward held; then along the barrier, sliding on it as at 22:47:39; then at a step 20 to 30 high with level ground on top (a loading dock's low edge, a raised slab). Record it and note the times | along the rail the bike slides along it and carries on, losing some speed at the contact but not stopping (test 42: three times in three minutes a rail beside the bike read as a wall or an obstacle ahead, 897 to 359 and 909 to 31 a second, and once the climb's boost put the bike up the rail's foot: "it should go alongside"). `CMB_Slope.log`: once a ride "rays: the pick's hit normal at the first face (…), length 1.000, N deg off the heading, the rays' slope N: usable" (send it whatever it says: "not a unit vector" means the game doesn't fill the normal, and every face is judged as in test 42); along the rail "rays: a face alongside, N deg off the heading: N past the front wheel at axle height (GRail…, layer N), its normal (…): left alone", and at the contact "slide: along a face N deg off the heading (…, seen N s ago), the velocity N deg off the heading: the throttle held at N for up to 1 s (the speed along N would have capped it at N)" and "slide: over after N s: … (the speed along N, the throttle N)"; no "a wall ahead" or "an obstacle ahead" line for the rail and no "climb limit 47 -> 85" at it (a climb line naming "a face alongside" instead); the throttle trace ", slide held N for N s", with no "held to the measured speed" while it holds. At 40 to 45 degrees, the post and the trunk: stopped short as before, "a wall ahead" (for the post or the trunk "… (alongside by its normal, …, but the rays either side don't say so: …)" is right); along the building's wall "rays: a face alongside at the front wheel (…): the throttle not cut" may come too. Say whether the slide feels like going alongside, whether the speed lost at the contact (the game keeps about half) is acceptable, at what angle you met the rail and whether it slid before stopping, and whether 30 is the right boundary (`FaceAlong=20` and `40` on the same rail). `FaceAlong=0` with `SlideHold=0` in CMB_Slope.ini (read again on getting on) is test 42's build. Since test 45 (test 44: the capsule went up the barrier and the rail, 25 to 30 high, and the bike sat astride them, the wheels in the air: "bike shouldn't be able to get on them - it just gets stuck halfway through"): the "  climb:" settings line has "; a face with something 18 above the feet within 45 past it climbed only if round (receding toward its foot), narrow (a ray at 18 two capsule radii to a side passes it) or a step up (a ray down a wheelbase past it finds the ground that high over the ground at its foot) (ClimbMaxTop: a log, a stump or a step, not a rail or a beam with a drop behind it), and a low face with something 1.5 or 2 ClimbTops above the feet within 45 past it not climbed (a barrier's bar)"; at the barrier and the rail the bike stops short and isn't put up on them, no "the climb limit 47 -> 85" there, and once stuck with forward held "climb: stopped with forward held (…): not climbed: a beam with a drop behind it, not a step up: something at 18 above the feet N ahead (what, layer N; ClimbMaxTop), not round (N deg at its foot) and long (the rays 36 to either side meet it too), and a wheelbase on, N ahead, the ground N over the ground at its foot (what, layer N)" (or "… no ground from N over the ground at its foot to N under it"), or at the barrier's low foot "… not climbed: a bar beyond the low face: something at 48 above the feet N ahead (what, layer N; ClimbMaxTop), where the capsule would hang on the face under it (a barrier)"; at the step, on the flat and where the ground slopes a few degrees up or down to it, "climb: a low face at the capsule …; at 18 N ahead: a step up, the ground N over the ground at its foot N ahead (ClimbMaxTop) …: the climb limit 47 -> 85" and "climb: stepped up N …" or "climb: over it after N s …", the bike on top. Sliding along the barrier at speed can still put the capsule on it (test 44's was mounted so, the boost off): if the bike ends up astride it, back off (row 17o) and say how it got on. Whether the guard rail by the brush pile is refused depends on whether the pile behind it reads as ground 18 up: say which it was. `ClimbMaxTop=0` (read again on getting on) is test 44's climbing. Since test 46 (test 45: at its 2:56.4 a raised guard rail met at an angle, and at 9:48.9 a picket fence's post, read "narrow, the ray 36 to the right passes it" and the boost put the bike onto the rail and along the fence, a ray at 18 passing under a rail's beam or between pickets; at 5:24.0 a guard rail lying on the ground, "61 ahead at 4, 61 at 10 (95 deg)", its top under 18, climbed by design and ridden along on top; at 5:57.7 a raised rail met square at 905 first seen 187 past the front wheel, eased to 68%, the bike stopping with its front wheel in it): the "  climb:" line's narrow clause reads "narrow (rays two capsule radii to a side pass it at 18, 6 over it and the face's top less 4, each where it is within the face (NarrowHeights=3))", then "; a lower face, its top 8 or more over its foot, not climbed either if upright (80 to 100 deg at its foot and at its top), long (not narrow at 10 and its top less 2) and thin (the ground two capsule radii past its face under half its top over its foot): a rail lying on the ground (ClimbBeamLow), a kerb, a step, a log or a stump still climbed"; the "  steer:" line has "a wall dead ahead (not an actor) eased by the distance a stop needs: the speed squared over twice 0.6 of the brake's rate (FullSpeed / Brake, 2250 a second a second), a tenth of a second of the speed and 10, the throttle none within it, and looked for that far past the front wheel when FaceLook's reach is shorter, a face alongside by its normal not (WallStop)". At a raised rail met at an angle and at a fence's post the bike is held, no "the climb limit 47 -> 85", and once stuck "… not climbed: a beam with a drop behind it, not a step up: … long (the rays 36 to either side meet it too, cast at 18 and 24; a side's at 18 passes it, at 24 meets it (NarrowHeights)), …"; at the rail on the ground held too, "… not climbed: a low beam with a drop behind it: its top N over the ground at its foot N ahead (what, layer N; ClimbBeamLow 8), upright (N deg at its foot, N at its top) and long (the rays 36 to either side meet it too, cast at N), and 36 past its face, N ahead, the ground N over the ground at its foot (…)" (or "… no ground from …"); straight at a raised rail at full speed, about 400 out, "rays: a wall ahead (N deg): N past the front wheel at axle height (…), the throttle eased to 0% (a stop from 900 needs 400 past the front wheel, looked for that far, past FaceLook's reach: WallStop)", the bike stopping about 10 short of it, its front wheel out of it (since test 47 about 40: below). Every wall, not an actor nor a face alongside by its normal (a car or a rail you ride past keeps the old ease), now stops the bike about 10 short of the front wheel's edge rather than at it (since test 47 about 40), the ease starting further out the faster you go: say whether that feels early. A fence met under about 30 degrees off your heading lies past the side rays' reach (they meet a line up to about 58 degrees off square) and can still read narrow at every height (test 45's at 9:48.9 read 24 off): say if one does, with the time. As in test 45: up a wrecked car (5:28 to 5:36: the capsule up its body at ground normals of 29 and 44.5 degrees, within the game's 47, the face rays holding the throttle at 55%) and off a porch through its iron railing (7:33: no face-ray line, the three rays on the centre line passing between the balusters); say if they come again. `NarrowHeights=1`, `ClimbBeamLow=0` and `WallStop=0` (read again on getting on) are test 45's build for their parts. Since test 47 (test 46: "rails and low fences I was still able to ride through, and now I was getting slowed down or randomly stopped by objects and world geometry"; `WallStop` cut the throttle 81 times in 857 s of riding, 75 of them to nothing, most for fences, mailbox stands, stumps, rubble and stairs seen 200 to 400 past the front wheel at 900 for a tenth or two of a second while you steered past them; at 2:24.3 and 2:30.8 a wooden road barrier met at a shallow angle read "narrow, the ray 36 to the left passes it at 18 and 24" and was climbed; at 2:20.45 the next barrier, and at 16:45.2 a guard rail met square at low speed, "under the bike, the front wheel 49 (55) up on it: an obstacle, not a wall", the bike on top of them): after the settings the "  steer:" line's WallStop clause reads "…, a tenth of a second of the speed and 10, never under a wheel radius and 10 (WallStopShort), the throttle none within it, and looked for that and FaceLook's span past the front wheel whenever FaceLook's reach finds nothing (…), the ease running from there down to it (WallStopReach), …; a wall first seen past FaceLook's reach held to a floor falling from all of the throttle to half over 0.15 s, under half only once it has stayed that long, and only while it is past the need, its need 0.15 s of the speed more (WallStopPersist), one first seen within FaceLook's reach not (WallStopNear=0); the longer rays cast along the arc the bike's turning puts it on, left out where it turns more than 90 deg over their reach (WallStopArc)", and a "  rails:" line follows, "  rails: the narrow test's side rays cast across the face (into it along its level hit normal, two capsule radii to either side along its line), narrow only if both sides pass it: a post or a stump, not a rail met at a shallow angle (NarrowBoth=1); a face the face rays see at or behind the front wheel's edge (not an actor), with that wheel's ray over ClimbTop above the feet and the rear wheel's within half a radius of them, is a face the front wheel is in: a wall, not a thing under the bike (UnderBikeTop=1)". At full speed past fences, posts and stairs you steer by, no stop: a wall first seen far ahead, "rays: a wall ahead (N deg): N past the front wheel at axle height (…), the throttle eased to N% (a stop from 900 needs 535 past the front wheel: 400, and 0.15 s of the speed for a wall first seen past FaceLook's reach (WallStopPersist), seen by the longer rays, 810 past it (WallStopReach); held to N% till it has stayed 0.15 s, seen N s (WallStopPersist), or till it is at the need: WallStop)", costs at most about a third of the throttle if it's gone within a tenth of a second, and only one that stays all of it; turning, the line adds ", along the turn's arc, +N deg/s (WallStopArc)", and a turn harder than about 85 degrees a second at full speed leaves the longer rays out; one that appears close at speed counts at once, as in test 46 (`WallStopNear=1` holds it so too, "… seen N s (WallStopNear): WallStop)"), and one that comes into the rays' line between the need and its extra (turning onto a rail's line) is held only till it is at the need; while turning, what the turn's arc meets within FaceLook's reach or beside the front wheel isn't counted; and a verdict that moves to another thing, or into or out of WallStop, has its own line, "… (the verdict moved: the last line had X at N%)" (test 46's 15:47.9, 916 to 164 a second, had none). Straight at a raised rail or a wall at full speed: first seen about 800 out and eased from there, stopped with the front tyre about 40 short of it (a wheel radius and 10: `WallStopShort`; test 46's 10). At the barrier met at a shallow angle: held, no "the climb limit 47 -> 85", and once stuck "… long (the ray 36 to the left passes it, the one to the right meets it, cast at 18 and 24) …; the side rays cast across its face, its line N deg off the heading (NarrowBoth)" (or "the rays 36 to either side meet it too"); a post or a stump still "narrow, the rays 36 to either side across its face pass it at 18 and 24 (ClimbMaxTop, NarrowHeights, NarrowBoth)" and climbed. At the guard rail met slowly: stopped 40 short; and if the front wheel still gets up into a rail or a barrier, the rear one down, the bike stands, "rays: a wall ahead (N deg): -N past the front wheel at axle height (…), the throttle eased to 0% (behind the wheel's edge, the front wheel 49 up on it, over ClimbTop's 31.9, the rear wheel's ground 0 over the feet: a face the front wheel is in, a wall; UnderBikeTop) (a stop from N needs N past the front wheel: WallStop)", to be backed off (row 17o), not ridden along on top. Send every WallStop line you didn't expect with its time and what was there, and say whether the stops at rails now feel early or late. `WallStopReach=0`, `WallStopPersist=0`, `WallStopNear=0` (its default since the review of test 47's build), `WallStopArc=0` and `WallStopShort=0` together are test 46's `WallStop`, `NarrowBoth=0` and `UnderBikeTop=0` test 46's rails (all read again on getting on) Since 2026-11-02a (step 2 of its list): a narrow thing the rays 40 to either side of its path both pass (a mailbox, a lamp post, a sign) is eased by FaceLook and never cut by WallStop ("(narrow: the rays 40 to either side of its path pass it: FaceLook's ease, not WallStop's (WallStopNarrow))"), a cut wall's line says why it is wide ("(wide: ...: WallStopNarrow)"), and an obstacle lower than 1.5 wheel radii holds the throttle to 85% ("(LowObstacleThrottle)"); `[Steer] WallStopNarrow=0` and `LowObstacleThrottle=0` are test 48's. Since 2026-11-06a (steps 1 and 2 of its list): a side ray meeting only the hit's own placed object, with a ray 80 out passing, leaves it narrow (`WallNarrowSame`), the side rays also look at 1.5 wheel radii (`WallNarrowHigh`, so a rail over posts is a wall), and a narrow thing ridden at with no side key or turn is stepped round toward its open side (`Sidestep`: "sidestep: ... (Sidestep)", "sidestep: over after N s: ..."); `WallNarrowSame=0`, `WallNarrowHigh=0` and `Sidestep=0` are test 49's. |
| 17o | *(F4SE plugin; tests 43 and 45)* Back up (the reverse, 80 a second) straight toward a rail or a low wall behind you; then toward a car; then toward a ledge, a drop of a foot or more (a loading dock's edge, a roadside bank); then down a 33-degree slope with nothing behind (as at 20:59:43 of test 42). Since test 45: whenever the bike ends up hung on something, both wheels off the ground (astride a barrier, a rail or a log, as at 22:47:42 of test 44, or on a grill, 22:54:03), or pushed up against a low face it can't climb, back off it at once, within 3 s. Look from the side | the bike stops with about 25 free behind the rear tyre at the rail and the car (test 42: "way too far", 56 behind the tyre at a rail at 20:55:53 and about 86 on the slope: the clearance was the vanilla bike's 150), and at a ledge with the tyre's back edge a step short of the lip, not hanging over it. `CMB_Slope.log`: "reverse: the rear's clearance 95 from the parts file (the tyre's back edge 70 behind the rider + 25)" after the settings and at each push's start; at the rail "reverse: stopped: something behind (knee height, …)"; at the ledge "reverse: stopped: the ground drops away under the rear tyre, N units back (the ground N there, N below the slope 55 back's line)" or "… no ground under the rear tyre, …"; the trace's "rays" lines "… under the rear (95), N under the tyre (74), …". Down the slope: no stop till something is behind (a "drops away under the rear tyre" on an even slope is wrong: send it with the time). Say how close the tyre should stop (`BackMargin`, 25; 10 to nearly touch) and whether at a lip it should hang over a little; and, if you remember, what was behind the bike at 20:53:19 of test 42 (video about 18:16: "the ground drops away under the step, 1 units back"). `BackClearance=150` with `BackLedge=0` in CMB_Slope.ini (read again on getting on) is test 42's backing. Since test 45, after the settings "  reverse: BackHungDrop=40: hung up (both wheels' rays finding the ground over 10 under the feet, or forward stalled at a face at the capsule, in the last 3 s and within 40 of there), a drop of up to 40 under the step is backed off (20 otherwise)"; hung up, the bike backs down off the beam, "reverse: hung up (both wheels' rays found the ground under the feet, N at the front and N at the rear, N s ago): the ground N under the step backed off onto (BackHungDrop 40; over 20 a drop otherwise)" or "reverse: hung up (forward stalled at a face at the capsule (what, layer N, N ahead at 4), N s ago): …", a second apart at most (test 44: "reverse: stopped: the ground drops away under the step, 1 units back" every push, till the tester wriggled the bike off); deeper than 40, or no ground within 60, it stops, "reverse: stopped: the ground drops away under the step, N units back (N down, over BackHungDrop's 40 though hung up)" or "… (none within 60 under the feet, hung up)" (up to test 44 the ray under the step didn't reach a drop over 38, and the bike backed on unless the rear tyre's ray stopped it). Not hung up, a ledge stops the bike as above. Say whether backing off a beam lands the bike well, and whether 40 is enough. Since test 46 the bike should end up on a rail less often (row 17n: a rail lying on the ground, a raised rail met at an angle and a fence's post aren't climbed, and a rail met at full speed is stopped short of): when it still does, back off as above and say how it got on. Since test 47 less often still (row 17n: a barrier met at a shallow angle isn't narrow, a rail met slowly is stopped 40 short of); and with the front wheel up in a rail or a barrier and the rear one down, the bike now stands as at a wall, "rays: a wall ahead (N deg): -N past the front wheel at axle height (…), the throttle eased to 0% (behind the wheel's edge, the front wheel N up on it, over ClimbTop's 31.9, the rear wheel's ground N over the feet: a face the front wheel is in, a wall; UnderBikeTop) …", rather than riding on along its top at 55% (test 46's 2:20.45): back off it then, and say whether backing off works from there. `BackHungDrop=0` (read again on getting on) is test 44's backing Since 2026-11-02a (steps 2 and 3 of its list): a touch along a rail or a car's flank picks up again at once (`[Steer] SlideRestore`: "back up from N to what it was when the cap began to bind N s before (SlideRestore)"), and a face confirmed alongside stays so for a second while the side rays lose it (`FaceAlongKeep`: "the same face confirmed N s ago: FaceAlongKeep"); the backing itself is unchanged. |
| 17p | *(F4SE plugin; tests 43 and 48)* Ride over a bump or two first (a hop of half a second). Then ride off a high ledge with forward held, a fall of 0.7 s or more, as the rock cliffs at 19:53:30, 20:04:43 and 20:05:00 of test 47 (about 4 m); then off a step that gives half a second in the air; then off a ledge with a wall or a car just past where you land. Look from the side | The bike lands and carries on at its speed: no stop or stutter, the frame sinking on the suspension and coming back up. In test 47 it went 937 → 486 within 0.4 s and was at about half speed for 0.7 s ("character still stops/stutters when jumping off high ledge"): for a fall that high the game plays its hard landing, which moved the player by the landing clip, about 410 a second, whatever the speed. Since 2026-11-01a (step 9 of its list) the plugin passes the game's hard landings to the animations as the soft ones while riding (`[Steer] LandSoft`); test 43's landing hold and sink (test 42: 881 to 544 to 398 within 0.4 s, "it should sink on the suspension and carry on") stay. `CMB_Slope.log`: "graph: PlayerCharacter's NotifyAnimationGraph wrapped (...)" once; "graph: the soft landings named from the string pool (...)"; at each high drop "landing: 0.72 s in the air, the fall 489 a second (179 below its highest point): the throttle kept at 1.00 for 0.5 s (the Lead cap off; the measured speed 877 at the landing), the frame sunk 7.0 at the front wheel and 4.0 at the rear (the nose 1.3 deg down)", then "landing: the game's jumpImpactLandToRun (+0.00 s, after jumpRunningFall at -0.72 s), passed to the graph as jumpLandToRun (LandSoft)" and "landing: the hold over after 0.5N s: the speed along N at its lowest (+N s), N now (N at its lowest on the 0.05 s measure)" with N at 0.9 of the landing's speed or more (test 47's were 0.52); the trace's lift "lift N (landing N, nose N)" for about half a second, the throttle line ", landing hold N s left" and no "held to the measured speed" in the first half second. A soft landing reads "landing: the game's jumpLandToRun (+0.00 s, ...), a soft landing: as it is". Into the wall: "landing: the hold ended after N s: the speed along N under 0.25 of the top (stopped by something)" within about 0.3 s, and no lunge once you turn away. Off a ledge at a crawl (under a quarter of the top) the landing line reads "the throttle not held (the speed along N under LandStop's 0.25 of the top)" instead. If a line reads "no landing event from the game seen by the hook" or "no name for the soft landing yet", say so. Say whether the rider's landing looks right (the soft landing's seated clip now plays at every drop) and whether the sink looks right (`LandSpeed=700`; try 500 and 1000), and watch the arms and the hands through the landing (the rider sinks with the frame: if they jump, `LandSink=0`). `[Steer] LandSoft=0` (read again on getting on) is test 47's landing; `LandHold=0` with `LandSink=0` is test 42's |
| 17q | *(F4SE plugin and its Address Library, `version-1-11-240-0.bin`; test 44's build: the engine sound; test 45: the heard speed; test 46: the levels by SetVolume, louder; test 47: the throttle hand and the up-shift's dip)* With the MCM's engine volume at its default (70; since test 47 90 in a new save, a save keeping its own): get on and sit still for 5 s; ride off from the stop at full throttle and hold forward for 10 s (the bike is at its top speed in about 3, the engine shifts on for about 6); cruise for 20 s with forward held along a road with rails, cars or fences beside it now and then; let go of forward for a third of a second and press it again; let go and roll to a stop without braking; sit for 3 s; pull away like that three more times, a stop between; then forward for 2 s and brake (back) to a stop; sit for 3 s; get off. Ride again and move the MCM's engine volume during the cruise (to 30, to 100, and to where it sits right). Then quicksave on the bike, ride on, quickload and ride off again. Record it with the game's sound, and note the times | the start, then the idle you called perfect (demo C's, the same in demo D) while standing, settling over about 0.4 s as the plugin takes it (`FirstFade`, 400 ms: the script starts it at full and the model's idle is 12.0 dB under that since test 45, 5.2 before, so it eases down rather than steps; since test 46 a straight ramp of the plugin's own, to 12.2 dB under). Pulling away (test 44: "the way it's implemented is horrid - it's not natural whatsoever": 1.5 to 2 s flat at 1500, then 1st and 2nd swept in 2 s, every pull alike): the idle hands over to a deeper sound on load as you press, and the rpm climbs at once, from about 1250 to 1500 (each pull its own start), about 350 rpm a second; the first up-shift 2 to 4 s after the press at 2000 to 2900 rpm (each pull its own point: every ride's first at about 2430), 2nd climbing slowly, 3rd and 4th later, the last about 6 s after the press, long after the bike itself reached its top speed; each shift a third of a second darker with the rpm falling (since test 47 with a short dip in level too: below). At the top speed a steady beat (4th gear, about 1940 rpm) with a slow wander in its pitch (since test 47, and in its level with it; since the 2026-10-31a build swings typically peaking 3 to 5% off, never past about 6%: below), and no surge (test 44: 4 to 3 and back half a second later every 6 s, 79 times, most after the face rays, a ram or the climb had eased the throttle): a down-shift only if the bike loses about half its speed; the short let-off changes no gear; at a lower steady speed with forward held (the MCM's Speed slider at 100%, about 360 a second) one gear as well, 1st at about 2200 rpm (test 45's build before its review: 1 to 2 and back every 2 to 3 s at any steady 215 to 445). Letting go, a drop of 2 to 3.5 dB and a softer, darker sound, the rpm falling steadily in gear (about 150 rpm a second) for the second or so the game's bike takes to stop, now and then a down-shift with a short blip, then the clutch (at about 1750) and the fall to the idle within about a second (test 44: the gears ticked down silently in a second and the note collapsed to the idle as the bike stopped); braking, it falls faster; the stop sound as you get off. A pull clearly louder than the idle and the cruise: since test 46 a full-throttle pull about 3.8 dB over the cruise and 12 over the idle (paris about 4 and 11.6; test 45's game 1.6 over the cruise), a roll-off 2.6 to 3.1 under the cruise; and the whole engine louder than test 45's ("I had to set engine sound to 100 because it was too quiet, also it feels like sound isn't as punchy as it should": the cruise at -3.8 dB where it was -6.2, the files about 2.4 dB hotter, full level out to 600 from the bike where it was 150, the riding camera about 450 out), so the MCM's engine volume likely sits well under 100 now: say where it sits right with gunfire, footsteps and the radio, and whether the pulses sound gritty (the hotter files round their peaks off). Nothing clicks at a loop's seam, no jump in pitch or tone where one loop hands over to the next, nothing doubled or echo-y; since test 46 no drop-out at a gear change, nor about once a second through a pull-away (test 45: two of about 0.1 s at every up-shift, its video's 0:20.4, 0:21.8 and 0:23.0, and one at each hand-over, 0:18.1, 0:19.0 and 0:20.0: FadeTo fades every change over 100 ms at least, a loop brought back from silence inaudible for most of it); the volume slider changes the whole engine and brings in nothing new (since test 46 at once, the plugin reading it every frame: "sound: the engine volume 0.70 -> 1.00 (CMB_EngineVolume 100): in every loop's level from this frame" for each change); after the quickload the same sound. `Papyrus.0.log` at each ride's start: "[CMB] Engine sound: the plugin drives the 11 loops (generation N, answered in poll P), the engine volume in their levels." ("…P)." up to test 45; send whatever it says instead: "[CMB] Engine sound: the script's crossfade (the plugin declined generation N: see its log)." or "... (the plugin didn't answer in 0.5 s, generation N)." mean the old two-loop sound, the idle and the cruise crossfaded by speed; "[CMB] Engine sound: the plugin let go of generation N (CMB_SndDriven reads X): the script's crossfade, its two loops started afresh." mid-ride). `CMB_Slope.log`: after the settings "sound: found CMB_SndLoop01 to CMB_SndLoop11, CMB_SndGen and CMB_SndDriven (...), CMB_EngineVolume (FExxx81C)" (since test 46; "; no CMB_EngineVolume (0x81C): the engine volume taken as the MCM's default, 90" is an older ESP; 70 up to test 46) and three "  sound:" settings lines (four since test 47: below), the first since test 46 with "SetVolume=1 …; their levels by SetVolume, at once, the engine volume in them (Fade and LevelStep unused)", the second with "ClutchFall=750 … DownRpm=1475 … CoastFall=150 … Wander=0.025 WanderTau=1.5 … LevelScale=1 LevelOffset=5" (Wander=0.006 WanderTau=0.8 up to test 46, LevelScale=0.7 in test 45's build), the third "  sound: HeardSpeed=1 HeardRise=140 HeardTau=0.8 HeardLead=150 HeardPull=60 ClutchSpeed=150 CoastDown=1700 Blip=0.09 BlipTime=0.3 BlipTau=0.05 LaunchDraw=1250,1500 LaunchRise=350 ShiftDraw=2000,2900 DownHold=1 DownHeld=1: the engine follows a heard speed (up at most HeardRise, down with engine braking after a let-up); the launch's slip climbs from each pull's start; each pull's up-shift point drawn; a down-shift with the throttle on after DownHold under DownRpm, none while the throttle is held for something ahead" (a "not understood" list on the first line is news: send it); at the first ride "sound: the Address Library at ... (N ids) matches this game (...); BSSoundHandle::SetFrequency +0x..., FadeTo +0x..., IsPlaying +0x..., in .text; SetVolume +0x162E160" (since test 46: SetVolume's place is test 45's tester's reading of the game, not yet seen in a real library, so "… doesn't match this game (ID 2267057 gives 0x… where the plugin has 0x0162E160, BSSoundHandle::SetVolume): the script's crossfade drives the engine" and "sound: generation N declined (the Address Library at … hasn't BSSoundHandle::SetVolume where the plugin has it): …" mean it is elsewhere, and the old two-loop crossfade plays: send them first; or the line why not); at each ride's start "sound: generation N: loops ... playing 11 of 11" (fewer, or "declined (IsPlaying says none of them plays: a Papyrus instance id may not be the sound's id)", means the plugin's way of reaching the loops is wrong: the most important line to send) and "sound: generation N driven (CMB_SndDriven N): 11 loops' pitch and level from the engine model, the speed and the keys from the steering; the levels by SetVolume (applied at once, no fade, no FadeTo), the engine volume folded in (CMB_EngineVolume 70: x0.70, read every frame), the first 400 ms a straight ramp from the script's levels (the idle at the engine volume, the rest silent)" (test 45's build: "…; FadeTo's attenuation taken as hundredths of a dB (0 = full, 10000 = -100 dB: an assumption), 25 ms fades, the first of each loop heard over 400 ms"); on the pull "sound: gear 2 at N u/s, N rpm, heard N u/s" (the bike's speed near its top already, the heard speed about 540), then 3 and 4; letting go perhaps "sound: gear 3 at N u/s, N rpm, heard N u/s, a blip", and at the stop "sound: gear 1 at N u/s, N rpm, heard N u/s (clutch in)"; the trace line ending "engine g4 1937 rpm load 0.45 heard 900" at the cruise (since test 47 "… heard 900 hand +1.23%"); getting off "sound: generation N let go (the ids went to 0, generation N): driven N s, N calls (SetFrequency N, FadeTo 0, SetVolume N: each posts its change to the audio thread), 860-N rpm, gears used 1 2 3 4" (since test 46; more calls than before, about 160 a second through a pull, a level moving 0.001 sending; since test 47 about 75 a second at a steady cruise too, the level moving with the throttle hand; ", N returned false" inside the parenthesis is news: send it; "(the ride is over)" in place of "(the ids went to 0, …)" is a ride that ended with the ids still set: send it with the time); at the quickload "sound: generation N let go (a load: the loops don't survive it): ...", perhaps "sound: generation N already answered (CMB_SndDriven N: a save's set, its ids from before the save): left alone", and the new set driven. Should they come, send "sound: pitch over 1 refused: the loops pitched down only (...)" and "sound: loop K (id N): 30 calls in a row returned false (they only post a message: not expected): ...". Since test 47 (test 46: "engine sounds way better, it doesn't fluctuates at all which also isn't ideal, bike engine RPM always either rises or decreases, slowly or fast depending on mantle and gear"; its steady riding wobbled about 0.4% in rpm and 0.16 dB in level in 4 s windows, the real rides 0.9 to 2.3% and 0.34 to 0.81 dB; its up-shifts dipped 2.4 dB, a real one about 5.5; you kept the engine volume at 90): at a steady cruise with forward held the pitch and the level wander together, slowly, a rise louder and more loaded, a fall lighter (the throttle hand; since the 2026-10-31a build swings of a second or two typically peaking 3 to 5% off the cruise's rpm, never past about 6%, and 1 to 1.5 dB, at most 1.8, as smooth as 27c's, whose swings peaked about 2.5% off: its notes' "about 1%" was 4 s windows with the trend taken out, 1.2% now), and only while the throttle is steady: none through a pull, a let-up, a shift, the idle, or while the plugin eases the throttle for something ahead, where it settles within about a second (a quarter up to 27c) and grows again after; at each up-shift a dip of about 4 dB over a quarter second (about 0.15 s under -3 dB), the last one, into the cruise, about 6, heard at the top of a pull too, never a hole; a new save's engine volume 90 (yours keeps its own); the engine's output model the game's SOMMono02000 but for its distances, the reverb send 5 where test 46's was 100 (the game's world sounds use 5; at 100 the engine was far wetter than any of them wherever the area has reverb). `CMB_Slope.log`: a fourth settings line "  sound: WanderLevel=0.3 WanderSteady=0.25 WanderSmooth=0.5 WanderMax=0.06 ShiftDip=4 ShiftDipTime=0.24: the wander (the throttle hand) only while the throttle is steady, settling to 0 in a pull, a let-up, a shift and the idle, smoothed, held softly under WanderMax, the family loops' level moving with it; a throttle-off dip at each up-shift's clutch-in, at most 6 dB under the level there"; the trace's engine word ending " hand +1.23%" (the wander, in % of the heard rpm: 0.00% through a pull from rest, up to 6% either way at the cruise, never past); the let-go line with more `SetVolume` calls (about 75 a second at a steady cruise: the harness 152 in 2 s, test 46's game about 11 a second). Say whether the cruise's wander sounds like a hand on the throttle or like a fault (too much, too quick), whether the dip at a shift sounds like the throttle closing (too deep or too long: `ShiftDip`, `ShiftDipTime`), and whether the engine sounds drier where there are buildings about. The clicking test 46 heard was the game's Geiger counter (row 17r). Say whether the pull-away and the roll-off now sound like the reference rides, whether the cruise holds steady, any clicks, the volume you settled on, and how it compares with demo E (51 s of test 44's own ride through this model). For an A/B in `Data\F4SE\Plugins\CMB_Slope.ini`'s `[Sound]` (get off and on again: it's read on getting on): `HeardSpeed=0`, `CoastFall=70`, `DownRpm=1750`, `ClutchFall=900`, `LevelScale=0.3` with `LevelOffset=0`, `LaunchDraw=0,0`, `LaunchRise=0`, `ShiftDraw=0,0`, `DownHold=0` and `DownHeld=0` together are test 44's model exactly (with `SetVolume=0` its FadeTo too); `SetVolume=0` with `LevelScale=0.7` and `LevelOffset=0` test 45's build (its drop-outs included: compare a gear change), `SetVolume=0` alone test 45's FadeTo at this build's levels; `LevelOffset=6.8` a louder cruise (-2 dB) with less between it and a pull; `ShiftFamily=0`, the quick A/B test 45's answer offered, is no longer needed (with `SetVolume=0` it still takes an up-shift's two drop-outs out); `Wander=0.006`, `WanderTau=0.8`, `WanderLevel=0`, `WanderSteady=0`, `WanderSmooth=0` and `ShiftDip=0` together are test 46's sound (each alone its part); the hotter files and the engine's own output model have no key (test 45's package's 13 files in `Data\Sound\FX\CMB` give back its files; since test 47 the model is SOMMono02000's own but its distances, the reverb send 5 where test 46's was 100, and test 46's ESP gives its back); and if it's silent or wrong, `Drive=0` gives the old crossfade, for a comparison. Since 2026-11-01a (test 47: "rpm could be slightly higher", "the sound could indicate that gears are shifted down"): steps 2 and 3 of the 2026-11-01a build. 1st and 2nd change up at a median of about 2,600 rpm, up to about 2,950 (`ShiftDraw=2300,3000`; test 47: 2,330), 3rd at about 2,340 after a short moment at its top; rolling to a stop gives three blipped down-shifts about half a second apart, braking two, then the clutch (`StopShift=1`; "sound: gear 3 at ..., a blip", then 2 and 1, then "gear 1 ... (clutch in)"), the last of it up to 0.4 s after the bike stops; a half-second let-off sounds as before. The brake key: Space by default (MCM Hotkeys "Brake key (scan code)", `CMB_BrakeKey` 57; `[Steer] BrakeKey=-1` takes the MCM's): it brakes with forward held, the brake light on and the engine blipping down as with back, holds the bike still once stopped (no creep, no reverse) and pulls away when let go with forward held; back still backs up; off the bike Space jumps. "steer: BrakeKey=-1: the MCM's CMB_BrakeKey 57, Space ..." in the settings and "steer: the brake key (Space) held at ... u/s: braking" at a ride's first press. The engine hand-over's Papyrus line ends ", N s after getting on), the engine volume in their levels." (N about 3; more is a slow script engine). A/B: `ShiftDraw=2000,2900` and `StopShift=0` (2026-10-31a's gears), `BrakeKey=0` (no brake key) Since 2026-11-02a (step 5 of its list): the idle at -6.0 dB, 2.5 under the cruise (`[Sound] IdleDb=-11`; `-17.2` the 2026-11-01a build's, 8.7 under), so a stop no longer goes quiet and the start and stop sounds meet it without a step; the settings line reads "IdleDb=-11 LevelRpm=3000". Since 2026-11-06a (step 7 of its list): the idle at -9 (`IdleDb`, -11 test 49's), each up-shift's gap 0.55 s (`ShiftTime`, 0.35) with the dip 0.4 (`ShiftDipTime`, 0.24), and a take-off revs over itself (`LaunchFlare=0.5` over `LaunchFlareTime=1.2` s; 0 none); a pull-away from rest starts at a quarter throttle (`[Steer] LaunchTau`, step 3). |
| 17r | *(F4SE plugin and the controller; tests 46 and 47)* Ride a while and get off; sprint till the AP bar is part down, then walk 30 s; sprint it to 0 and walk a minute. Whenever AP stops refilling, type `player.getav ActionPointsRate` and `player.getav ActionPointsRateMult` in the console and note the numbers; then save, reload and say whether the refill comes back. Since test 47: first make sure AI processing is on (`tai` again if it was typed: "All AI Processing is On"); sprint AP to 0 on foot and walk a minute; then ride, get off, sprint it to 0 and walk a minute. Whenever the HUD's rads indicator shows with nothing radioactive near: `player.getav rads` twice, a minute apart; then save, reload and say whether it clears; and ride through the junkyard of test 46's 4:33, then walk through it. Note the times | AP refills as you walk (test 45: off the bike at 14:43, AP sat at exactly 77% through 30 s of walking after a sprint at 15:26, and at 0 for the 61 s after a sprint at 15:57 drained it at 15% a second: no drain and no refill, the sprint's drain itself working; "it has happened for a while"). The mod never touches AP, so this build only watches it. `CMB_Slope.log`: after the settings "  diag: APWatch=1 APWatchFor=120 APWatchEvery=2: off the bike, the gates of the player's AP refill (the sprinting bit, PlayerCamera+0x1A5, the AP regen delay and the CachedValues' bit 22) logged every APWatchEvery s for APWatchFor s after each getting off, and past that when one changes; read only"; from each getting off, every 2 s for 2 minutes, "AP watch (N s after getting off): sprinting no (the actor state's flags 0x…; "yes" while sprinting), PlayerCamera+0x1A5 N, the process …, its CachedValues …, flags 0x… (bit 22 set), apRegenDelay N (raw 0x…, HighProcessData … +0x68), the AP modifiers N, N, N (permanent, temporary, damage: AP under its max); refill gates shut: …", then "AP watch: the 120 s after getting off are over (APWatchFor): a line from now on only when one of the gates changes" and "AP watch (N s after getting off, a change): …" after it. AP refilling, the gates read "none" while it is under its max, and "(d) bit 22" alone at its max (the bit is set only while AP is under it). `Papyrus.0.log`: "[CMB] AP: N of N (N% of its max), rate N (base N), mult N (base N), sprinting no; getting on." at each getting on, "…; N s after getting off." every 2 s for 2 minutes, past them while AP is under its max "…, under its max." (an unchanged line every 20 s) and "…, back at its max." once it is. When AP is stuck send both logs around it with the time: which gate the plugin names shut while AP is under its max ((d) bit 22, or a CachedValues of "none", is the likelier, since (a) sprinting and (b) the scope's hold-breath would drain AP too), the rate and mult beside it, and the console's numbers. An apRegenDelay that reads nonsense (huge, or a raw value that isn't a small float) means its place is wrong: say so (+0x64 up to test 46, from CommonLibF4's headers, was Stamina's; since test 47 +0x68, AP's, by the build-27b check's reading of the game's GetRegenDelay). Since test 47 (test 46: AP full till 12:45, drained to 0 by a sprint by 12:51 and at exactly 0 for the last 5 minutes, every watch line "refill gates shut: none", the rate 6.0 and the mult 100; but all of it after the console's `tai` at 7:47, which alone stops every refill: with AI processing off the game's process lists return at once, nothing moves the actors' clock on, and nothing regenerates nor does any timed effect tick; test 45's AP checks came after its knock-overs, likely with AI off too; and the watch read Stamina's regen delay, not AP's): with AI on, AP refills after the sprint on foot and after the ride alike (most likely the mod has no AP bug: say if it does); the watch's lines show AP's own delay, "apRegenDelay N (raw 0x…, HighProcessData … +0x68)", a few seconds after a sprint, counting down to 0. If AP still sticks, send the watch's lines and the "[CMB] AP:" lines around it, the gate named shut and the console's two numbers, with the time. The rads indicator (test 46: "<1 RADS" from the junkyard at 4:33, about 2 s inside a radiation hazard's 1024 units, then "+2 RADS" from the getting off at 7:46 to the end, riding or not, with the Geiger counter's clicking, and the rad meter at the HP bar's end not growing; nothing in the mod reads or writes Rads): the two `player.getav rads` numbers (the same twice means no rads are being added), whether the reload cleared it, and whether the junkyard leaves it on after the bike, on foot, or both. `[Diag] APWatch=0` (read again on getting off) turns the plugin's lines off |
| 17s | *(the bike's look, since the 2026-10-31a build; F4SE plugin for the needle, the lights and the mirrors' choice)* Steps 10 to 17 of this build's list: the parked and the riding bike by day and at night, close up and from across a street; the speedometer standing, at full speed and at 150%; the tail and brake light from behind; each mirror style (`[Look] Mirrors` 1, 2, 3, 0) by day and at night, at full lock; `Data\Materials\CMB` renamed and back; the frame rate against 27c's; the log's role lines. Screenshots of each; the two logs saved before steps 13's swap, 14 and 15 | Paint deep oxblood and glossy with a soft reflection and a cream double line, our winged-wheel badge, no lettering; chrome dark with the sky in it (not white); a black wrinkle engine with bright fin edges; a grained seat; matte tyres with tread; no seams, smears, stretched patches or flicker. The needle on 0 standing, about 50 at full speed (`[Speedo] Scale` 1.75; 1 = the true 28.8 mph at 900 units a second), about 30 at 150%, back to 0 within a couple of seconds of stopping, turning with the bars; the dial's numerals lit with the headlamp only. The tail lamp red while riding, brighter with both rear signals while braking and out about half a second after, plain when parked. The mirrors a sky over a dark ground (not the world: the game can't show real reflections), the under-bar ones (2, 3) from the seat mostly ground with a strip of sky at the top (say whether they should tip up further), the right way up (else `mirror_cube_zup_e.dds` over `mirror_cube_e.dds`); the chosen style on the riding bike, never into the tank at full lock, the stock ones on the parked bike. No change with `Materials\CMB` renamed. Every shape "by its name" on the role lines; the "time:" lines' "for 28 shape(s)". Every key's off value: the table under this build's steps. Since 2026-11-01a: steps 12 to 18 of its list. `Materials\CMB` is needed (test 47: renamed, the bike went magenta), so no materials-off step. The tank's double line one smooth curve with a round turn at the rear end and no break over the seat's nose; the seat a round bead along the seam, nothing standing off it; our own drilled discs, a smooth round edge, holes you can see into, a fine circular grain, turning with the wheels; the mirror glass silvered with a sky by day (if it reads plain grey: the optional folder "game mirror cube (A-B)"). The tail lamp's light (MCM "Tail lamp lights the road", `[TailLight]`): the road behind lit a soft red for 2-3 m, the rider's back and the seat unlit, about three times brighter while braking; "Tail light placed (N)." in the Papyrus log, "tail:" lines in `CMB_Slope.log` (`BrakeBy=dimmer` if braking doesn't brighten it). The bike in first person (MCM "Bike in first person", `[View]`): the tank, the bars, the dial (about 50 at full speed), the mirrors and the lamp under you, leaning, pitching and turning, never blinking or see-through over 2-3 minutes at full speed, one shadow, one bike in third person, no hands on the grips; "First-person bike placed (N)." and the "view:" lines (`Lead=0` or `2` if it slides). The cull bit (`[Look] Cull`): no visible change; the FPS with it at 0 and 1, in third and first person; the "time:" lines "for 30 shape(s)". The optional folder "2026-10-31a look (A-B)" gives 31a's look back whole Since 2026-11-02a: steps 9, 10, 12, 13 and 14 of its list. In first person the view bike is moved every frame so your eye sits on its seat (`[View] Eye`, `EyeAt`: "the view bike moved (dx, dy, dz) on its own axes to put EyeAt there"); the mirrors name the game's `Shared\Cubemaps\MetalBrushed02Cube_e.dds`; the chrome's material files at env 6, specular 2, screen-space reflections on; the front disc without its light ring; a frame-rate line every 10 s while riding (`[Diag] FpsLine`: "time: the last 10 s: N frames a second ..."), so the Cull A/B needs no counter; at most three skeleton stop/start pairs in 10 s (`[View] StaleLines`). The optional folder "2026-11-01a look (A-B)" gives 2026-11-01a's look back whole; the "2026-10-31a look" and "game mirror cube" folders are retired. Since 2026-11-06a (steps 9 to 11 of its list): the chrome's materials env 2.5, specular 1.5 and no screen-space reflections, the rims and discs env 0.25, specular 0.75 (no texture changed); going into first person eases the view 20 degrees down (MCM "Look down on getting into first person (deg)"), a riding field of view (MCM, 0 = off) and the eye's place on the bike (MCM and console `CMB_ViewEyeForward`, `CMB_ViewEyeUp`); `[Look] Cull=0` by default (1 is test 49's); the optional folder is "2026-11-02a look (A-B)" (test 49's look) and "2026-11-01a look (A-B)" is retired. Since 2026-11-07a (its list's steps): the customisation build; with nothing chosen at the bike's field kit the bike is 2026-11-06a's (step 1); the badges, paint and mirrors chosen show on the parked, the ridden and the first-person bike (step 8); the 2026-11-06a package's optional folder must be off (its meshes have one badge); none ships. |
| 17t | *(the bike's own sounds, since the 2026-11-01a build; the water and the landing's level need the F4SE plugin)* Step 9 of the 2026-11-01a build: ride off a kerb or a porch step, then off a ledge of about a second's fall (as row 17p), at full speed and at walking pace; then ride into a shallow pond or river at speed, cruise through it, stop in it, pull away and ride out | Your character's own jump and landing sound (the shoes' thud) gone while you ride, back once you get off. A tyre thump on every landing with a real fall, louder the higher the drop, a metal clunk on top of the big ones, a splash into water; in water a spray that grows with speed and depth and settles to a lap when you stop, with a burst as you hit the water fast. The sounds are the game's own, borrowed (`CMB_FxLandSounds`, `CMB_FxLandSoundsAlt`, `CMB_FxWaterLoops`: docs/ASSETS.md's list). Papyrus: "Bike sounds: the rider's own footstep sounds muted while riding (AudioCategoryFSTplayer)." at each getting on and "... back." at each getting off; per landing "Bike sounds: landing (JumpDown) at level 0.47: sound 1 instance N, volume 0.298." (or "(SyncRight)"); at each getting on "Bike sounds: the plugin drives the water loop 0 (instance N, poll P)."; "In water while riding (the wade watch): True" about a second after the plugin's "into the water". `CMB_Slope.log`: "globals: the fx globals 7 of 7 found" and the settings line "  fx: Land=1 ..."; per landing "fx: landing cue 3 after 0.68 s in the air (the fall 208 a second): level 0.47 (-9.6 dB at the script's -18 dB floor), onto the ground" and "fx: the script played cue 3's landing sound 0.031 s after the landing" (send any "not played by the script" and any time over 0.1 s); in water "fx: the water loop (id N) driven", "fx: into the water at 640 u/s: 12.3 deep (the surface ... by the loaded data, type ...; ... by the controller; its swim height ...)", "fx: out of the water after 6.2 s (the deepest 31.0)", and the dry readings at the ride's start. Send "declined", "doesn't play", "of 7 found (0x884-0x88A, an older ESP)", an "into the water" on dry land, or none in a pond. To pick other sounds: `cqf CMB_ControllerQuest FxAudition 0` to `4` (the landing set), `10` to `14` (the second set), `20` to `23` (the water loops, 3 s each), "Bike sounds: audition N: [Sound ...] instance N." (instance 0: it didn't play); `set CMB_FxLandPick to 1` (the second landing set), `set CMB_FxWaterPick to 1` to `3`, then get off and on. Say whether the thump comes with the touch-down or a beat after, whether a landing ever has none or two, and where the "Bike effects volume" (MCM Sound, 90) sits right with the engine. Off, each as 2026-10-31a: the MCM's "Landing sound", "Water sound", "Mute the rider's own jump and landing sounds", the volume at 0; `[Fx] Water=0`; `[Fx] Land=0` turns only the plugin's levels off (the script's one level, at `JumpDown` landings only: not 2026-10-31a's, whose landings had no sound), `WaterSource=controller` reads the water from the character controller Since 2026-11-02a (step 11 of its list): the landings and the water through 13 sound records of our own over the game's files (MCM "Bike sounds through the mod's own records"; docs/ASSETS.md's second table), heard at the riding camera's distance; the landing range 10 dB (MCM "Landing loudness range (dB)", 18 before: "level 0.34 (-6.6 dB at the script's -10 dB floor)", "(our records, a 10 dB range)"); `[Fx] WaterGain` on the water loop; `FxAudition` waits for the menus to close, `-1` plays every one of ours and `-2` every one of the game's, a slot plus 100 is the game's record ("..., after the menus closed."); a level-0 cue reads "fx: cue N silent by the script (level 0)", not "played". Since 2026-11-06a (step 8 of its list): landings without metal (MCM "Landing sounds without metal": tyres, and on big drops a dull thud at `CMB_FxThudDb` -11 dB: "(our records, no metal, ...)"), into water a splash (the two splash records now name the game's own files: test 49 played silence there), the water loop the mod's own wet road (MCM "Water sound loop": the spray, the churn or the wet road), its level by (speed / 900) squared (`[Fx] WaterSpeedFull`, `WaterCurve`; 600 and 1 test 49's), and `FxAudition -3` plays the landings as heard. |
| 18 | Ride off small drops, then a big one (the Vault 111 cliff) | small drops cost nothing; the big one hurts, about 75% less than on foot; the log has a "Fall while riding" line per fall with the damage and percent of max health (send them: they tune `CMB_FreeFallDamage`, default 20%); seated all the way, landing included. Since 2026-11-06a (step 8 of its list): say which difficulty you play at (test 49's fall cost twice test 48's) |
| 18b | Ride fast downhill over bumps, and jump-land from a ledge | seated in the air and on landing: no sideways bike swing, no arm going up; with the plugin (`[Steer] LandSoft`, since 2026-11-01a) no landing stops you; without it a hard landing stops you briefly, a running one keeps you going |
| 19 | Ride into a lake or a river until you'd swim, also off a ledge into deep water | "The motorbike can't go into deep water."; you're off and swimming, no bike in sight. Using the keys while swimming is refused. Climb out: no bike on you (it comes off within 1.5 s at worst); about 3 s after you're out of the water altogether (not wading) "Your motorbike rolls up." a few steps past you, on the land side, not in the water (the log says how far you were from the deep water and whether you were still in water). Get straight back on: seated at once (if not, the log says "applying the rider pose again"). Shallow water (paddling depth) rides normally |
| 19b | Save while riding, load that save | seated within a couple of seconds; the log shows "Rider pose applied (after loading)" (send it if it says "refused") |
| 20 | Get on next to an enemy; let a bloatfly sting you; take a big hit (a shotgun blast, a power attack, a grenade) | nothing in the first 3 s; small stings don't knock you off; the big hit does: "You're knocked off the motorbike.", bike parked next to you (the log says how much health it took). `set CMB_KnockOffDamage to 25` needs bigger hits; with `set CMB_DismountOnHit to 0` you stay on, and when a fight starts (weapons off while riding) a hint says how to get off. Since 2026-11-01a (step 5 of its list): a hit that doesn't knock you off is logged, "Hit while riding: power attack False, blocked False, lost N% health since the last tick: not knocked off." (in the first 3 s "..., in the first 3 s after getting on: not counted.", one a second at most); hits don't stagger you while riding ("Steady in the saddle", `CMB_RiderSteady`; "Steady in the saddle: on (getting on): ..."), and a stagger that gets through anyway is logged, "Staggered while riding (Steady on)" (send it); for `CMB_PoseReactionWindow` (3 s) after a hit, an item used or a stagger the rider pose isn't applied again ("... a hit reaction or stagger, not the pose: left alone."); hits are watched for that with `CMB_DismountOnHit` 0 too, and only `CMB_DismountOnHit` knocks you off Since 2026-11-02a (step 8 of its list): an item used while riding (from the Pip-Boy, the favourites or a hotkey) opens `CMB_PoseUseWindow` (6 s, from the menu's close when it was used in one) in which the pose is never applied again, the Pip-Boy check included; with F4SE the hands and upper body are the clips' while its use clip plays (`[Tilt] UseLetGo`: "rider: the use clip began N s after the item ..."); 6 s after it the camera's controls are logged ("After [Form <...>] was used: the camera switch on, looking on, moving on, the camera state 8 (third person).") and a camera left without its switch has its view entered again (`CMB_UseCameraFix` 1), then the message "An item animation still holds the camera: get off and on to free it.". Since 2026-11-06a (step 5 of its list): a power attack throws you off only when it takes the Big hit share of your health, like any other hit ("... not knocked off (a power attack under Big hit's 10.0%: the MCM's Power attacks throw you off is off)."); the MCM's Riding "Power attacks throw you off" on gives test 49's; explosions always do. |
| 21 | Load a save from before the keys arrived (or a new game), go outside | exactly two keys and one hint, even right after a load or a door |

## Console settings

| Command | Effect |
|---|---|
| `set CMB_SpeedPercent to 300` | faster bike (100–500). Above ~350 the world may not stream in fast enough |
| `set CMB_BagCapacity to 200` | bigger side bag (lbs with F4SE, items without; 0 = unlimited) |
| `set CMB_CompanionMode to 0` / `1` | companions run alongside (default) / ride along hidden (riskier during companion quests and scenes) |
| `set CMB_UseFuel to 0` | free riding, no fuel |
| `set CMB_FuelDistance to 10500` | twice as thirsty (default 21000 = one Flamer Fuel per ~300 m) |
| `set CMB_RideWeapons to 2` | every weapon and VATS while riding, in the game's standing poses (MCM Riding "Weapons while riding" Any weapon, since 2026-11-15b; default 1 Handguns only: a handgun drawn seated with the left hand on the bar, anything else put away; 0 None: no weapon out on the bike; at once) |
| `set CMB_AllowCombat to 1` | shooting while riding (takes effect next time you get on; since 2026-11-15b read only by an older ESP without `CMB_RideWeapons`: use "Weapons while riding") |
| `set CMB_ForceThirdPerson to 0` | stay in your current camera |
| `set CMB_UseRiderPose to 0` | no seated animations (run in place over the bike); `1` to turn them back on, next time you get on |
| `set CMB_HotkeyCode to 34` | F4SE hotkey (DirectX scan code, 34 = G, 0 = off); save and reload afterwards |
| `set CMB_EngineVolume to 40` | quieter engine (0–100, 0 = silent) |
| `set CMB_FallDamageCut to 100` | no fall damage while riding (0–100, default 75 = 75% less) |
| `set CMB_DismountOnHit to 0` | enemies' hits don't knock you off (default 1) |
| `set CMB_FreeFallDamage to 30` | falls costing under 30% of max health are free while riding (default 20; 0 = off) |
| `set CMB_KnockOffDamage to 25` | only hits taking 25% of your max health knock you off (default 10; explosions always do, and power attacks with `CMB_KnockOffPower` 1; 0 = any hit) |
| `set CMB_KnockOffPower to 1` | every power attack throws you off, as in 2026-11-02a (MCM Riding "Power attacks throw you off", since 2026-11-06a; default 0: a power attack is a hit like any other) |
| `set CMB_BikeFollowsRider to 0` | the worn bike stays planted on the ground instead of turning with the seated rider (default 1) |
| `set CMB_RamEnemies to 0` | hostile actors hit at speed are braked for, not knocked over (default 1; needs F4SE and CMB_Slope.dll) |
| `set CMB_RamMinSpeed to 600` | knocked over only at 600 units a second or faster (default 450; riding speed is about 900) |
| `set CMB_RamDamage to 20` | knocked over with a fifth of their max health at riding speed (0–50, default 10; half that at the slowest, the last of it only with `CMB_RamKills`) |
| `set CMB_RamKills to 0` | a knock-over never takes an enemy's last point of health, as in 2026-10-31a (default 1: the knock-over that takes the last of it kills it, the kill the player's) |
| `set CMB_RamKillXP to 2` | the bike's kill credited by `DoCombatSpellApply` instead of `Spell.Cast` (MCM "Kill experience", since 2026-11-02a; default 1; 0 = `Kill(PlayerRef)`, no experience, as 2026-11-01a) |
| `set CMB_RiderSteady to 0` | hits stagger you while riding, as on foot (default 1: "Steady in the saddle") |
| `set CMB_RiderSteadyWay to 2` | "Steady in the saddle" by the game's own `mod_armor_LessStagger` (245AFE), one step less (since 2026-11-02a; default 1: `CMB_RiderSteadyPerk2`, ours with two tabs; 0 = the 2026-11-01a build's three-tab record) |
| `set CMB_PoseReactionWindow to 0` | the rider pose applied again at any standing footstep and no Pip-Boy check, as in 2026-10-31a (0–5, default 3 s after a hit, an item used or a stagger) |
| `set CMB_PoseUseWindow to 0` | an item stamps only the hit window and the Pip-Boy check ignores it, as in 2026-11-01a (since 2026-11-02a; default 6 s after an item's use, or after the menu's close when it was used in one) |
| `set CMB_UseCameraFix to 0` | no camera recovery after an item, only the log line (since 2026-11-02a; default 1: a camera left without its switch has its view entered again, then a message) |
| `set CMB_RiderUseOwn to 0` | every potion equipped while riding starts the item watch, another mod's dummy too, as in 2026-11-02a (since 2026-11-06a; default 1: only the Pip-Boy, the favourites and hotkeys count; needs F4SE) |
| `set CMB_Caution to 70` | the bike eases off for a wall or a car ahead a little earlier (MCM Riding "Caution (how early the bike eases off for obstacles, %)", since 2026-11-09a; 50-100, default 50 for a new save since 2026-11-10a, 60 before, a save keeping its own; 100 = as 2026-11-08a; read again once a second while riding; needs F4SE and CMB_Slope.dll) |
| `set CMB_ViewTip to 15` | the view eases 15 degrees down on getting into first person on the bike (MCM "Look down on getting into first person (deg)", since 2026-11-06a; 0-45, default 20; 0 = left as it is, as 2026-11-02a) |
| `set CMB_ViewFov to 90` | the world field of view while riding in first person (since 2026-11-06a, the MCM's slider till 2026-11-10a; 60-120, default 0: your own); since 2026-11-14a used only with `[View] Fov=1` in `CMB_Slope.ini` |
| `set CMB_ViewEyeUp to -8`, `set CMB_ViewEyeForward to -6` | your eye on the bike lower (the bike higher into view) and back (MCM "Eye height on the bike", -30..20, and "Eye forward on the bike", -30..30, since 2026-11-06a; default 0: `[View] EyeAt` as it is; at once; since 2026-11-15a `EyeAt` already holds test 54's -6 and -3, so a save from an earlier build should set both back to 0) |
| `set CMB_ViewBack to 2` | backing up in first person switches to third person while you back (MCM Riding "Looking back while reversing (first person)" Third person, since 2026-11-15b; default 1, over the shoulder; 0 off, as 2026-11-15a; needs CMB_Slope.dll) |
| `set CMB_ViewRoll to 8` | the view leans 8 degrees at the bike's whole lean in first person (MCM Riding "View leans in turns (first person, deg)", since 2026-11-15b; 0-10, default 4; 0 = level, as 2026-11-15a; at once) |
| `set CMB_TailLightMode to 0` | no tail lamp light, the lens only glows (default 1; next time you get on) |
| `set CMB_FirstPersonBike to 0` | no bike in first person (default 1; next time you get on) |
| `set CMB_BrakeKey to 42` | the brake key on Left Shift (a DirectInput scan code: 57 Space, the default, 42 Left Shift, 29 Left Ctrl, 56 Left Alt, 45 X, 46 C, 0 none; the log names the key it read) |
| `set CMB_LookKey to 45` | the look key on X (MCM Hotkeys "Look key (scan code)", since 2026-11-15b: held in first person on the bike the mouse turns only your head; default 44, Z; 0 none; 256-260 the mouse buttons; next time you get on) |
| `set CMB_FxVolume to 50` | quieter landing and water sounds (0–100, default 90; 0 = none) |
| `set CMB_FxOwnSounds to 0` | the landings and the water through the game's own records, as in 2026-11-01a (since 2026-11-02a; default 1: the mod's own records over the game's files; the water next time you get on). Since 2026-11-06a off is the game's own records for the landings only with "Landing sounds without metal" off, and for the water only with "Water sound loop" on its first choice ("As the 2026-11-02a build (spray)"): for test 48's A/B turn all three to their 2026-11-02a values |
| `set CMB_FxLandRange to 18` | the softest landing 18 dB under the hardest, as in 2026-11-01a (since 2026-11-02a; 0–30, default 10; smaller makes small drops louder) |
| `set CMB_FxLandDull to 0` | the landing sets with the metal clunk, as in 2026-11-02a (MCM "Landing sounds without metal", since 2026-11-06a; default 1) |
| `set CMB_FxThudDb to -14` | a softer thud under big landings (since 2026-11-06a; -40..0 dB, default -11; with `CMB_FxLandDull` 1) |
| `set CMB_FxWaterLoop to 0` | the water loop picked by `CMB_FxWaterPick`, as in 2026-11-02a (MCM "Water sound loop", since 2026-11-06a; 1 the churn, 2 the wet road, the default up to 2026-11-08a; since 2026-11-09a 3, the default, the gentle wet road; next time you get on) |
| `set CMB_LookOn to 0` | no Customise in the parked bike's menu and the stock look on every bike, as 2026-11-06a (MCM Look "Customise at the bike", since 2026-11-07a; default 1; the bikes at the next getting on, activation of the parked bike, "Apply the look" or load) |
| `set CMB_KitMode to 1` / `2` / `3` / `4` | the field kit forced: the toolbox / the toolbox with the armour bench's keyword (both tests: the toolbox can't be sat in) / the armour bench / since 2026-11-09a the game's armour bench, `WorkbenchArmorA` (MCM "Field kit", since 2026-11-07a; default 0, automatic: since 2026-11-09a the armour bench, then the game's, the one that worked remembered; up to 2026-11-08a the toolbox, then the armour bench) |
| `set CMB_KitWorked to -1` | automatic starts again from the armour bench (since 2026-11-07a, console only; automatic writes 3 or 4 here when a mode worked, and forgets a 1 or 2 an older build wrote) |
| `set CMB_LookOptions to 0` | without F4SE only: the script switches all off, as 2026-11-08a (since 2026-11-09a; the ESP's 4031 = all on: 1 FastMount, 2 KitHeld, 4 ParkedReload, 8 PaletteIndex, 16 MountGuard, 32 HueFree, and since 2026-11-10a 128 KitStash, 256 KitRetry, 512 MountEarly, 1024 WornColoursFirst, 2048 HueSwap; 63 = 2026-11-09a's; with F4SE `CMB_Slope.dll` writes it from `[Look]` at its start, at a load and on getting on, so set those keys instead: since 2026-11-14a 32767 at its defaults, with 4096 WornIndex, 8192 KeptMods and its own 16384, which the ESP's 4031 leaves off, and since 2026-11-15a 131071, with 32768 KitDefer and 65536 MountQuick, and since 2026-11-17a 262143, with 131072 KitRoom) |
| `set CMB_KitWhere to 0` | the field kit anywhere, as 2026-11-10a (MCM Look "Field kit only in your settlements", since 2026-11-14a; default 1: Customise opens the kit only in a settlement whose workshop is yours) |
| `set CMB_KitPreview to 0` | the field kit's preview as 2026-11-10a (MCM "Field kit preview" As before, since 2026-11-14a; default 1 New; 2 Tune, with `CMB_KitPrevSize`, `CMB_KitPrevTurn`, `CMB_KitPrevTilt`, `CMB_KitPrevUp`, `CMB_KitPrevZoomOut` and `CMB_KitPrevZoomIn`; needs `CMB_Slope.dll`; at the next Customise; since 2026-11-15a `CMB_KitPrevSize` is the distance ahead of the menu's camera, 100-2000, 400 = New's, MCM "Preview distance" (`[Look] KitTuneDistance=0`: the size in % again)) |
| `set CMB_KitBagLink to 0` | the field kit uses your own components (and a settlement's workshop) only (MCM "Parts from the side bag", since 2026-11-07a; default 1: outside your settlements the side bag's too) |
| `set CMB_LookHue to 120` | the Free colour paint's hue, 0-359 round the colour wheel (MCM Look "Paint hue", since 2026-11-08a; default 210; used only with Paint "Free colour", from "Apply the look" or the next getting on or activation of the parked bike) |
| `set CMB_LookShade to 2` | the Free colour paint's shade: 0 Deep, 1 Normal (the default), 2 Light, 3 Pastel (MCM Look "Paint shade", since 2026-11-08a) |
| `set CMB_LookPlateCrude to 0` | the 14 crude plate texts not offered at the field kit, and a plate wearing one shows its design's own text (MCM Look "Crude plate texts", since 2026-11-08a; default 1) |
| `set CMB_FxLandOn to 0`, `CMB_FxWaterOn`, `CMB_FxMuteRider` | no landing sound, no water sound, the rider's own footstep sounds kept (each default 1; the last two next time you get on) |
| `set CMB_FxLandPick to 1` / `set CMB_FxWaterPick to 2` | the second set of landing sounds / the third water loop (defaults 0; the water next time you get on) |
| `cqf CMB_ControllerQuest FxAudition 3`, then close the console | plays a candidate sound at the effects volume once the menus are closed (since 2026-11-02a: the console pauses the game): 0-4 the landing set, 10-14 the second set, 20-23 the water loops (3 s), through the mod's own records; 100 more the game's own records; -1 every one of ours and -2 every one of the game's, 2.5 s apart (about 47 s); since 2026-11-06a -3 the landings as heard, small to big, then two into water (seven, 2.5 s apart), and 22 is the wet road |
| `cqf CMB_ControllerQuest DecideTeleportsAtOnce 1` | doors and fast travels decided the moment the game sends the teleport, as up to test 40 (default 0: once it's over); kept in the save |
| `cqf CMB_ControllerQuest WatchBusy 0` | no busy watch (default 1: a keys, hotkey or bike action holding the script over 10 s is logged and let go); kept in the save |

Speed changes apply the next time you get on.

## Finding the mod's forms in the console

The plugin is light (ESL), so its form IDs start with `FE` and depend on your load order. Find them with
`help "Motorbike" 4` (or `help CMB_ 4`). For example, to look at the worn bike directly:
`player.equipitem <CMB_BikeRiderArmor id>`.

**Keys never arrived?** They wait until you're outdoors *with a Pip-Boy*. Alternative-start mods sometimes skip the Pip-Boy. Then:

```
cqf CMB_ControllerQuest ForceGiveKeys
```

## Emergency reset

If you end up stuck (still fast, can't jump, bike missing, companion missing):

```
cqf CMB_ControllerQuest EmergencyReset
```

If the console rejects that, try `cqf CMB_ControllerQuest "CMB_ControllerScript.EmergencyReset"`.
It removes the worn bike (since 2026-11-09a also the two riding armours kept in your inventory between rides, `[Look] FastMount`), restores speed and controls, clears the riding animations, brings hidden companions back and parks the bike next to you (indoors or in a walled town in the middle of a ride, it's left outside the door you took and comes to you when you come out near it, as in row 9).
Still seated after getting off? `player.caf` (ChangeAnimFlavor with no keyword) clears the riding animation flavour by hand.

**Before uninstalling:** get off the bike and run the reset (since 2026-11-09a it also takes the kept riding armours out of your inventory), then save. Uninstalling mid-ride would leave the speed bonus on you and companions hidden in the holding cell.

## What to send back if something fails

1. Which step number failed and what happened instead
2. `Papyrus.0.log` (look for `[CMB]` and `error`)
3. With F4SE: `Documents\My Games\Fallout4\F4SE\CMB_Slope.log`, and after a crash or a restart `CMB_Slope_prev.log`, `CMB_Slope_prev2.log` and `CMB_Slope_prev3.log` beside it (the three sessions before, kept since 2026-11-15a; one since test 41)
4. Any Creation Kit compile errors, full text
5. Your mod list if it might be a conflict (anything touching player animations, companions or movement speed)
6. For animation problems: the text `make_rider_pose.bat` printed
7. Since 2026-11-15b: `CMB_RiderPose_report.txt` (next to `CMB_RiderPose.esp`, written when `make_rider_pose.bat` of
   this build's repository runs), screenshots of your body in first person, and a short video of a handgun drawn on
   the bike and of a rifle put away
8. Since 2026-11-16a: screenshots of the field kit's "Tank L" list and of the 3D helmets (test 56's steps 1 and 3), and
   the frame rates of step 14
9. Since 2026-11-16b: screenshots of the bars with your body shown and of the view looking down (test 56's steps 21 and
   23) and of the field kit's preview (step 30), and a short video of a handgun drawn right after getting on and of a
   rifle put away (steps 25-28)
10. Since 2026-11-17a: screenshots of each redrawn plate and badge close and from riding distance (test 57's steps 1-8),
    of two of the field kit's slot views (step 10) and of the view looking down (step 27), and a short video of a
    handgun drawn after the Pip-Boy and of a rifle's number key (steps 16-19), of your hands after a weapon swap (step 22)
    and of the bars zoomed in across cells (step 25)
11. Since 2026-11-21a: screenshots of each wear, the muddy tyres, the new badges, the helmets' grounds, the plates' top
    lines and the headlamp's colours, close and from riding distance (test 58's steps 1-11), and of the field kit's
    three new views (step 16); the frame rates of step 12; and a short video of the field kit's wheel, drag and mods
    (steps 13-14), the look in third person (step 23), a holstered pistol, a holster and a first-person draw in third
    person (steps 25-27) and the switches back to third person after your body (steps 29-30)
12. Since 2026-11-22a: any crash log with both logs (test 59's step 1), screenshots of each paint condition and its
    combinations with the Wear, the wear on the parked and riding bikes (and with step 5's A/Bs), on the parts and over
    the badges, the muddy tread, the Brotherhood helmet's gears, the Nuka-Cola script and the headlamp's new colours,
    close and from riding distance (steps 2-11), two of the field kit's views (step 13) and the parked bike on flat
    ground, a slope, beside a car or a ledge and on rough ground (steps 16-19); the frame rates of step 33; and a short
    video of the field kit's wheel (step 15), getting on beside the leaning bike (step 20), the third-person orbit (step
    24) and a holstered pistol on your thigh while riding (step 30)
13. Since 2026-11-23a: screenshots of the bike beside you after getting off on flat ground, on a slope, by a wall and by
    a car, and leaning across a slope both ways (test 60's steps 1-5), of Rusty and Raider at the badges and riding, of
    every Wear at the badges, of the gears beside the Brotherhood helmet and of the Wear on the four bikes (steps
    10-13), and of a pistol out in third and first person (steps 16-18); and a short video of getting off and on (steps
    1 and 6: the blacks), the field kit's options (step 15), the third-person look with and without a weapon (steps
    20-21), the holster on your thigh (steps 22-23) and a stimpak in third person (steps 24-25)
