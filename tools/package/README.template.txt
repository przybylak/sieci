COMMONWEALTH MOTORBIKE - READY-TO-INSTALL FILES (2026-11-15a, repository commit @COMMIT@)

The Data folder is the whole mod except the rider-pose plugin, which has to be built from
your own load order:

  Data\CommonwealthMotorbike.esp      the plugin (no new record since 2026-11-14a; this build changes two
                                      starting values of the field kit preview's Tune sliders)
  Data\Scripts\*.pex                  compiled scripts (Caprica, Fallout 4 format; no Creation Kit
                                      needed), twelve, as 2026-11-14a's: CMB_HotkeyF4SE,
                                      CMB_GearRestoreF4SE and CMB_LookF4SE (the customised look on the
                                      parked, ridden and first-person bikes and its colours) need F4SE.
                                      Two change: the controller and CMB_LookF4SE
  Data\Scripts\Source\User\*.psc      their sources
  Data\MCM\                           Mod Configuration Menu page and hotkeys (since this build the
                                      field kit preview's "Preview size (%)" slider is "Preview distance")
  Data\F4SE\Plugins\CMB_Slope.dll     F4SE plugin: steeper slopes, farther camera, bike tilt, steering,
                                      the speedometer, the lights and the mirrors, the bike in first
                                      person, the landing and water sounds, the sidestep, the launch,
                                      items at speed, the look you fit at the bike, the parked bike kept
                                      out of people, Caution, the wheels, the gears, items by hotkey at
                                      speed, the bike's ready signal at getting on, the parked bike's
                                      guard, the engine through a menu, the number keys at speed, Free
                                      colour in third person, the first-person bike held under your eye,
                                      the field kit's preview, the engine quiet in menus, five gears, and
                                      since this build the camera's place in first person read right, the
                                      first-person bike hidden until it is coloured, the slower pull and
                                      three earlier logs kept (Fallout 4 1.11.240 + F4SE 0.7.9 only); its
                                      settings are in CMB_Slope.ini beside it
  Data\Sound\FX\CMB\                  engine sounds: the idle, start and stop and ten riding loops, built
                                      from a real V-twin's recording, and the mod's own two wet-road water
                                      loops, CMB_FxWaterRoadLP.wav and the gentler
                                      CMB_FxWaterRoadSoftLP.wav (see the credits at the end): 15 files,
                                      2026-11-10a's, unchanged
  Data\Meshes\CMB\                    the bike (Nieve5677's cruiser, see the credits at the end): parked,
                                      and worn three ways: hanging off the seated rider
                                      (CMB_BikeWornRider.nif, ...RiderF.nif for the female/CBBE seat
                                      height) and planted on the ground (CMB_BikeWorn.nif);
                                      CMB_BikeView.nif, the bike you see under you in first person;
                                      CMB_BikeParts.ini tells the plugin where its wheels, steering
                                      axis, lens and speedometer needle are. 2026-11-10a's, unchanged
  Data\Textures\CMB\Bike\             its textures, 123 DDS, 2026-11-10a's, unchanged
  Data\Materials\CMB\Bike\            its material files, 427, 2026-11-10a's, unchanged: one per surface
                                      for the riding bike, *_worn.bgsm, and one per surface for the
                                      parked bike. The meshes need them: a missing material file shows
                                      the bike magenta.
  Data\Meshes\Actors\Character\Animations\MT\CMB_Rider\          106 riding clips + CMB_RiderClips.json
                                                                 + CMB_RiderSeat.json
  Data\Meshes\Actors\Character\Animations\MT\CMB_Rider\Female\   106 female clips (CBBE seat height), same files

No optional folder, as 2026-11-14a. If the 2026-11-06a package's "Commonwealth Motorbike - 2026-11-02a look
(A-B)" is still in MO2, keep it unticked (or remove it): it has the old badge and none of the new shapes.

WHAT'S NEW IN 2026-11-15a
  The fixes build for test 54 (run on 2026-11-14a), with two of its wishes: your eye where you put it,
  and the speed climbing with the gears. You chose fixes first, and the slower pull so that the gear
  sounds stay exactly as they are. What test 54 liked is as it was: the number keys at speed, the
  bike's hotkey on B, Free colour in third person, the field kit's names and its settlements rule, the
  engine quiet in menus, the five gears' sound, the guard beside a knocked-down NPC. Changed: the ESP
  (two values), two scripts (the controller and CMB_LookF4SE), the MCM page, CMB_Slope.dll and
  CMB_Slope.ini. The meshes, textures, materials, sounds, riding clips and the rider-pose plugin are
  2026-11-10a's.

  WHAT TEST 55 SHOULD TRY (WHAT TO TEST below has the steps):
  - the field kit: plate colours, "The plate's own" among them, several times in one visit: no crash,
    and the colours on the parked bike once you leave the menu; the preview: the whole bike, zoomed
    fully out and in ("Preview distance" in Tune if it is too near or too far);
  - first person: FIRST set the MCM's "Eye forward on the bike" and "Eye height on the bike" back to 0
    (your save keeps them), then ride on rough ground: steady now? your eye in the right place? and
    first person right after getting on: no red tank;
  - getting on: about as quick as in test 53 again (about 2.5 s to the screen back);
  - the pull: from a stop the speed keeps climbing through the gears and reaches the top about when 3rd
    ends; how it feels speeding up again after a lift or a hit; a few A/Bs;
  - the logs: three earlier sessions kept;
  - and, not tried in test 54, the field kit refused on a road outside a settlement, and allowed
    anywhere with the MCM switch off.

  TEST 54'S FIXES:
  - The two crashes at the field kit (both right after "Plate background: The plate's own"): a plate
    colour chosen at the kit used to change the parked bike beside it at once, while the menu was open,
    and both crashes came in the frames right after that. The plate colours you choose there now go on
    the parked bike when you leave the menu, with the rest of the look, as the MCM's Apply does (the MCM
    never crashed) ([Look] KitDefer). You see them on the parked bike once the menu has closed.
  - First person still shook: the fix that makes the first-person bike follow the game's own camera
    switched itself off on its first frame, because it read the camera's place in the wrong space (the
    log's "118676" was the camera's distance from the world's origin). It reads it as the world place
    it is now ([View] CameraWorld). The plugin's frame task also turned out to run twice for each frame
    the game draws, so the bike's lead guess was nearly 0 every second run: it now uses the game's own
    frame ([View] LeadFrame).
  - No preview in the kit's menu (its camera was inside the bike): the menu turns out to read the turn
    in radians, ignore the scale and place the bike ahead of its camera by the position. New now puts the
    whole bike 400 ahead, turned three-quarters, with room to zoom; in Tune the first slider is "Preview
    distance" (less is a bigger bike). Two more log lines say where the menu's camera is, so the next
    build can set the final distance.
  - The stock red tank for a moment in first person right after getting on: the first-person bike now
    stays hidden until its colours are on (3 s at most), and at a hand-over the old one stays until the
    new one is coloured ([View] LookWait).
  - Getting on about 0.85 s slower than 2026-11-10a: last build's Free colour fix redid its colour work
    at every getting on; with the look unchanged it is now skipped (one check), so getting on is about
    as quick as before ([Look] MountQuick).
  - The session logs: the plugin now keeps the three sessions before as CMB_Slope_prev.log,
    CMB_Slope_prev2.log and CMB_Slope_prev3.log, so a crash and two restarts no longer lose one ([Diag]
    KeepLogs).
  - Your eye: the default now holds the "eye forward" -6 and "eye up" -3 you used ([View] EyeAt=0,-5,125);
    the MCM's two eye sliders still add to it, so set them back to 0.
  - The speed and the gears ("bike reaches 50 just on gear 2, but it still goes on for 2 more without
    gaining speed"): above 0.6 of its top speed the bike now takes 5.5 s more to reach it, from a stop and
    at speed alike, so the speed climbs with the gears and the top comes about when 3rd ends and 4th
    comes in (about 6 s after the press). The take-off is as before, and the engine's gears and their
    sound are untouched: 5.5 s is the slowest pull that keeps the sound as it is ([Steer] PullTime,
    PullFrom). After a lift or a hit at speed the bike climbs back at the same, slower rate.

  NEXT BUILD, 2026-11-15b (not in this one):
  - A and D turning the bike in first person as the mouse does, with a slight lean; the rider's arms and
    body seen in first person; looking back when reversing in first person; handguns on the bike (in the
    right hand, the left on the bar); sidestepping big objects, not only posts; the right-hand cables
    that float in first person.

  MCM:
    In the "Field kit preview" section "Preview size (%)" is now "Preview distance" (100-2000, 400 = New:
    how far ahead of the menu's camera the bike sits; a save from 2026-11-14a first shows 30, which means
    New's 400 until you move it), and "Preview zoom in" starts at 3. Riding's "Eye forward on the bike"
    and "Eye height on the bike" are as before, but set both to 0 now (above).

  CMB_SLOPE.INI (every new key at its default in the file, with its comment):
    [Steer] PullTime=5.5, PullFrom=0.6; [Look] KitDefer=1, MountQuick=1, KitTuneDistance=1,
    KitPreviewScene=1; [View] CameraWorld=1, LeadFrame=1, LookWait=3; [Diag] KeepLogs=3. Changed
    defaults: [View] EyeAt=0,-5,125 (was 0,1,128); [Look] KitPreviewPos=0,400,0 (0,0,0),
    KitPreviewTurn=0,0,0.785398 (0,0.02,44.764), KitPreviewScale=1 (0.3), KitPreviewZoom=-1,3 (-1,1), the
    four commented out at their defaults.

  EVERY NEW THING HAS A SWITCH whose off value is 2026-11-14a:
    [Look] KitDefer=0 (save first: it may crash at the kit again), MountQuick=0, KitTuneDistance=0,
    KitPreviewScene=0, and KitPreviewPos=0,0,0, KitPreviewTurn=0,0.02,44.764, KitPreviewScale=0.3,
    KitPreviewZoom=-1,1; [View] EyeAt=0,1,128, CameraWorld=0, LeadFrame=0, LookWait=0; [Steer]
    PullTime=0; [Diag] KeepLogs=1 (read at the game's start). With KitTuneDistance=0 "Preview distance"
    is the old size slider again (its old 30 then by set CMB_KitPrevSize to 30 in the console: the
    slider now starts at 100). 2026-11-14a's switches back to 2026-11-10a's are all still there.

  KNOWN, LEFT FOR NOW:
  - With IAF / Chem Reanimations, an item used at speed (by its number key too) is used at once, but the
    start of that mod's decoration clip still shows for a moment after each use.
  - The plate colours chosen at the field kit now show on the parked bike when the menu closes, not
    while it is open (the menu's preview never showed them either).
  - The preview's 400 is worked out from test 54's numbers: the bike may look small (zoom in, or Tune);
    test 55's log sets the final value.
  - First person: that the camera's place is a world place is inferred (about 70% sure; one log line a
    session settles it). With the bike now keeping up with the camera your eye may feel a little
    further back at speed than in test 54. If it still feels like riding without suspension while the
    log says "the camera root 0.00", what is left is the game's own camera over the bumps.
  - The slower pull leaves little margin to the engine's own climb late in 3rd; after a lift at speed
    the note follows the bike, a gentler pull; a lower MCM speed makes the pull slower too.
  - From 2026-11-14a: an option you didn't choose keeps the last colour written into it until you
    choose it again (only the armour menu's preview shows that); the first getting on after a real
    change of parts (not just a colour) is about 1.2 s slower.
  - From 2026-11-10a: Caution 50 is only a new save's default; with [Lamp] Ahead set under about 10 and
    MCM "Headlamp casts shadows" on, the front end can shadow its own beam (the default 28 keeps it
    clear); when getting on, a follower is stowed and the headlamp lit up to about a second after the
    screen is back.
  - From 2026-11-09a: a bike kept hidden by the guard when you go through a door or fast travel stays
    hidden where it waits until you call it; the parked bike blinks once when its look is put on outside a
    ride; the riding armours kept between rides stay in your inventory, hidden: before uninstalling, get
    off and run cqf CMB_ControllerQuest EmergencyReset, which takes them out too.
  - From 2026-11-08a: after you take a new plate design at the kit the preview shows the old design's
    own text until you leave the kit; the rim styles you didn't fit are still drawn, invisible, on the
    parked bike; a rim style changed in the MCM while riding (or a load mid-ride with "Customise at the
    bike" off, on a rim style) puts the ridden bike on again within about a second; without F4SE the
    parked and first-person bikes stay stock and the ridden bike's colours stay their defaults; weathered
    paint, more badges, the front fender, the headlamp's colour and the seat come later.

BORROWED BY PATH (the game's own files, resolved in its archives; none is in this package; nothing new)
  the field kit's toolbox     SetDressing\Toolbox\Toolbox_Large.nif
  the armour bench (mode 3)   Furniture\Workstations\WorkbenchArmor\WorkstationArmorB01.nif
  the mirrors' loose mods     Props\ModsPartBox\ModCrate.nif
  the "(game art)" badges     Armor\CombatArmor\ChestDecalGunner_d.dds; ChestDecalStar_d.dds and
                              ChestDecal_n.dds; SetDressing\Minutemen\FlagMinutemen01_d/_n/_s.dds;
                              SetDressing\BOSFlag01_d/_n/_s.dds
  our badges' shine           Shared\Cubemaps\MetalChrome01Cube_e.dds, as the stock badge
  the chrome rims' shine      the same cube, as the bike's chrome
  the other rims' shine       Shared\Cubemaps\mipblur_DefaultOutside1_dielectric.dds, as the stock rims
  Records by FormID: the armour bench's keywords and idle, the workshop keywords, the loose mods' type,
  the toolbox's sound, the six components, the Armorer perk and the game's own armour bench
  (WorkbenchArmorA, the field kit's mode 4) (docs\ASSETS.md lists them); since 2026-11-14a the plugin also
  reads four of the game's own preview transforms for its log (MiscMod01, xTranMiniGun,
  ArmorTorsoPowerT60, ArmorHatExtraLarge) and writes nothing into them. Global Stash by SKK, another mod,
  is only asked about: whether its plugin (SKKGlobalStashScrapping.esp) is loaded, and then four of its
  forms by ID at run time; nothing of it is in this package.

INSTALL / UPDATE (Mod Organizer 2)
  1. Get off the bike, save, quit. If you edited CMB_Slope.ini, keep a copy of it.
  2. Install this zip's Data under the old mod's name and choose Replace (not Merge), or remove the old
     mod in MO2 and install this one fresh. By hand without MO2: copy Data over and let everything
     overwrite. The separate "Commonwealth Motorbike - Rider Pose" mod from make_rider_pose.bat stays as
     it is: no need to rerun make_rider_pose.bat.
  3. If you had edited CMB_Slope.ini, put your values into the new one: [Steer], [Look], [View] and
     [Diag] have new keys, and [View] EyeAt and the four KitPreview values new defaults (README.md's
     first key table lists them).
  4. Load test 54's save. In the MCM set "Eye forward on the bike" and "Eye height on the bike" back to
     0 first. Keep Global Stash by SKK installed. The plugin now keeps the logs of the three sessions
     before; say which session each step was in. Then WHAT TO TEST below.
  Updating mid-ride: get off first, save, then update.

WHAT TO TEST (docs\TESTING.md, "The 2026-11-15a build", has the details and the log lines; the
numbers are its steps)
  1. Field kit in Sanctuary (save first): in one visit take a new plate design, then "Plate background:
     The plate's own", then a "Plate letters" colour and two or three more plate colours. No crash? Leave
     the menu: your plate colours on the parked bike now? Two or three times.
  2. The preview: a screenshot as the menu opens. The whole bike, turned three-quarters? Zoom all the
     way out and all the way in (a second at each end, screenshots). Only if it is too near or too far:
     "Field kit preview" Tune, "Preview distance" (less = bigger); which value looked right?
  3. First person, with the eye sliders at 0: a flat road at full speed, rough ground, turns, standing
     still. Still shaking? Your eye in the right place, standing and at speed (if you move the sliders,
     to what)? A/B one ride each: [View] CameraWorld=0, LeadFrame=0. Send the "camera:" and "view:
     lock:" lines.
  4. Get on and switch to first person straight away, several times: no bike for about a second, then
     your colours, never the red one? Ride on past a few cell changes: no red flicker? A/B: [View]
     LookWait=0.
  5. Get on and off five times with the look unchanged: about 2.5 s to the screen back? Free colour
     right from the first moment? Then a hue change in the MCM, and once after a restart and a load.
     A/B: [Look] MountQuick=0.
  6. From a stop, forward held to the top speed on a long flat road: the take-off as before, then the
     speed climbing through 2nd and 3rd, the top about when 3rd ends (about 6 s)? The gears sounding as
     in test 54? Too slow or too quick?
  7. At speed let go for half a second and press again; pull away again from half speed after a turn;
     a hit or a kerb at speed: sluggish? The note while it gains? A/Bs in [Steer], one or two rides
     each: PullFrom=0.8, PullTime=6, PullTime=7 (and PullTime=4.5 if 5.5 feels too slow); PullTime=0
     is the old pull.
  8. After three starts: CMB_Slope_prev.log, CMB_Slope_prev2.log and CMB_Slope_prev3.log beside
     CMB_Slope.log, and its first line saying so?
  9. Not tried in test 54: Customise on a road outside a settlement: refused with a message, nothing out
     of the side bag? With "Field kit only in your settlements" off, the same spot: the kit opens?
  10. Any A/B you haven't tried yet, one at a time (KitDefer=0 only on a save you can lose). Anything
      better or worse?
  Send CMB_Slope.log and its three _prev logs, Papyrus.0.log, any crash log, the screenshots of step 2,
  and a video if you have one.

QUESTIONS FOR YOU (docs\TESTING.md has them in full)
  T55-1. Plate colours at the field kit, "The plate's own" after a new design among them: no crash? The
         colours on the parked bike once you left the menu?
  T55-2. The preview: the whole bike? Zoomed fully out and in? If you moved "Preview distance", to what?
  T55-3. First person with the eye sliders at 0: steady on rough ground? Your eye's place right,
         standing and at speed?
  T55-4. First person right after getting on: no red tank? Any red flicker at a hand-over?
  T55-5. Getting on as quick as in test 53 (about 2.5 s to the screen back)? Free colour still right?
  T55-6. From a stop: does the speed climb with the gears now, the top as 3rd ends? Too slow or too
         quick? The gears' sound as good as in test 54?
  T55-7. Speeding up again after a lift, a turn or a hit: sluggish? Which A/B felt best?
  T55-8. Three earlier logs there after three starts?
  T55-9. Refused on the road, allowed anywhere with the switch off?
  T55-10. Anything an A/B made better or worse?

TIMING STAND-INS (optional, as before)
  38 clips use a stand-in vanilla clip for their timing because these weren't extracted:
    mt\confident\turninplace*.hkx (12), mt\confident\walk_to_stand.hkx,
    mt\confident\female\turninplace*.hkx (12), mt\confident\female\walk_to_stand_l45/l90/l180/r45/r180.hkx,
    mt\neutral\jogleanleft/right, sprintleanleft/right.hkx and the same 4 in mt\neutral\female\.

These files are partly derived from Bethesda's (the parked bike's collision, the clips): for your
own install only.
  Bike model: "Harley Davidson Iron 883 2015" by Nieve5677 (CC-BY-4.0)
    https://sketchfab.com/3d-models/harley-davidson-iron-883-2015-612071b783f14a7288df2d361be9a244
    by https://sketchfab.com/niev, licence https://creativecommons.org/licenses/by/4.0/
    Changed for the game: cut down to about 230,000 triangles, given UV maps and textures baked
    from the full model, scaled, and put on the vanilla motorcycle's collision; the speedometer's
    dial and needle, the lights' shells, the under-bar mirrors and the badges are the mod's own.
  Engine sound: built from demodave's "Harley Davidson Sportster - Idling with Engine Revs"
    (https://freesound.org/s/502690/, CC0; credited with thanks).
  Water sounds: the two wet-road loops, made from "Cars driving on a wet road 3" (Pixabay 101246,
    freesound_community), under the Pixabay Content License; the recording isn't included.
