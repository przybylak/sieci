COMMONWEALTH MOTORBIKE - READY-TO-INSTALL FILES (2026-11-14a, repository commit @COMMIT@)

The Data folder is the whole mod except the rider-pose plugin, which has to be built from
your own load order:

  Data\CommonwealthMotorbike.esp      the plugin (since this build eight more records, for the field
                                      kit's settlements switch and its preview, and the kit's item and
                                      slots named)
  Data\Scripts\*.pex                  compiled scripts (Caprica, Fallout 4 format; no Creation Kit
                                      needed), twelve, as 2026-11-10a's: CMB_HotkeyF4SE (since this
                                      build it also uses a potion whose use clip the plugin cut at
                                      speed), CMB_GearRestoreF4SE and CMB_LookF4SE (the customised look on
                                      the parked and first-person bikes and its colours, since this build
                                      also the ridden bike's) need F4SE. Three change: the controller,
                                      CMB_HotkeyF4SE and CMB_LookF4SE
  Data\Scripts\Source\User\*.psc      their sources
  Data\MCM\                           Mod Configuration Menu page and hotkeys (since this build the
                                      field kit's "only in your settlements" switch and its preview
                                      section; the riding field of view setting is gone)
  Data\F4SE\Plugins\CMB_Slope.dll     F4SE plugin: steeper slopes, farther camera, bike tilt, steering,
                                      the speedometer, the lights and the mirrors, the bike in first
                                      person, the landing and water sounds, the sidestep, the launch,
                                      items at speed, the look you fit at the bike, the parked bike kept
                                      out of people, Caution, the wheels, the gears, items by hotkey at
                                      speed, the bike's ready signal at getting on, the parked bike's
                                      guard, the engine through a menu, and since this build the number
                                      keys at speed by the game's own key codes, Free colour in third
                                      person, the first-person bike held steady under your eye, the field
                                      kit's preview, the engine quiet in menus and five gears (Fallout 4
                                      1.11.240 + F4SE 0.7.9 only); its settings are in CMB_Slope.ini
                                      beside it
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

No optional folder, as 2026-11-10a. If the 2026-11-06a package's "Commonwealth Motorbike - 2026-11-02a look
(A-B)" is still in MO2, keep it unticked (or remove it): it has the old badge and none of the new shapes.

WHAT'S NEW IN 2026-11-14a
  The fixes build for test 53 (run on 2026-11-10a), with most of its wishes; five come in the next build,
  2026-11-14b (below). What test 53 liked is as it was: getting on in about 2 s, the field kit's menu
  holding beside Global Stash by SKK, the front end's shadow, the bike seen in first person, Caution 50's
  sidestep, the tip, the engine held through a menu. Changed: the ESP (8 new records, and the field kit's
  item and slot names), three scripts (the controller, CMB_HotkeyF4SE and CMB_LookF4SE), the MCM page,
  CMB_Slope.dll and CMB_Slope.ini. The meshes, textures, materials, sounds, riding clips and the
  rider-pose plugin are 2026-11-10a's.

  WHAT TEST 54 SHOULD TRY (WHAT TO TEST below has the steps):
  - a stimpak by its number key at full speed: healed at once, with no animation and the speed kept;
  - which key you press for the bike's own hotkey: 0 or B;
  - Free colour in third person from the first moment of every ride, and the "Palette test" paint ridden:
    cobalt or grey?
  - first person: no shake, and you sit over the seat, not on the tank;
  - the field kit: the item named "Motorbike", the slots named, the whole bike in the preview, and only in
    your settlements;
  - the Pip-Boy and the pause menu silent at speed;
  - the five gears;
  - and, not tried in test 53, the guard beside a knocked-down NPC and a few A/Bs.

  TEST 53'S FIXES:
  - Number keys at speed (a stimpak by its number key was never used: the game gives a key as its own key
    code, 0x31 for number key 1, where the plugin looked for scan codes, so it never saw the key, and the
    use clip was then cut before the game applied the item): the plugin now finds a number key by the
    game's own name and code ([Steer] QuickKeyCodes), and the log names a key in hex ("quick: key 0x31
    ..."). If it still can't take a key (a gamepad, or [Steer] QuickUse=0), the clip is cut and the hotkey
    script uses the item unless the game already did ([Steer] QuickCut), or the clip plays until the item
    is used and is cut then ([Steer] UseStopUnapplied): either way the stimpak heals. Each use now counts
    for one clip only, so a double tap, or a stimpak right after a chem, is no longer cut unused. A
    self-test says where a key gets lost and which key the bike's hotkey really is ([Diag] QuickProbe).
  - Free colour in third person (blue on every ride but the one the game loaded into): the colours are
    written into the chosen options' own colour swaps before the bike goes on, so the game builds the
    ridden bike with them, as it builds the parked bike; no swap after the fade ([Look] WornIndex). A
    hue-only change no longer puts the bike's parts on again, about 1.2 s quicker getting on ([Look]
    KeptMods). A diagnostic says what the paint held ([Diag] WornPasses), and [Look] Repass=1 is an A/B if
    it is still wrong.
  - The riding field of view (the game wrote its own back every frame): gone, with its MCM slider, as you
    wished; an older save's setting is ignored ([View] Fov=0).
  - The engine's late-start line counted from the press, which a look change could stretch: it counts from
    the moment the bike was ready now ([Diag] HandoverFromReady).

  TEST 53'S WISHES:
  - First person steady, your eye further back: the first-person bike is held so your eye stays put on it
    as it tilts (on a slope, in a lean, over a bump), at once every frame, pointing along your heading,
    and it follows the game's own camera each frame ([View] EyeLock, EyeAxes, Camera, EyeAtCamera). Your
    eye sits 11 units further back, over the seat, where the game's own camera is at a stop ([View]
    EyeAt=0,1,128; the MCM's "Eye forward on the bike" still adds to it). A "view: lock:" line every 2 s
    says what still moves ([Diag] ViewLock).
  - The field kit: the armour menu calls the item "Motorbike" (it read "Default") and names each choice
    with its slot ("Paint: Factory", "Rims: ...", "Tank L: ..."); its preview shows the whole bike,
    smaller and turned three-quarters, with room to zoom (the MCM's "Field kit preview": New, As before,
    or Tune with six sliders; [Look] KitPreview); and with the MCM's "Field kit only in your settlements"
    on, Customise opens the kit only in a settlement of yours: elsewhere a message, and nothing comes out
    of the side bag. "Free customising" in the MCM works anywhere.
  - Silence in the Pip-Boy and the pause menu: the engine and the water sound fade out within 0.15 s while
    a menu pauses the game and come back at the same note after it ([Sound] MenuQuiet).
  - The gears: five gears shifting higher, at about 3200-3400 rpm at full throttle (into 5th about 2500),
    2nd and 3rd rising all the way, a short 4th, the cruise as before; the note no longer drops while the
    bike is gaining ([Sound] HeardKeep), and a short lift of the throttle no longer blips 2nd down to 1st
    ([Sound] LiftDown). A stop still shifts down with blips.

  NEXT BUILD, 2026-11-14b (not in this one):
  - handguns on the bike (in the right hand, the left on the bar); looking back when reversing in first
    person; the lean on A/D in first person; sidestepping round bigger things than posts; the right-hand
    cables that float in first person.

  MCM:
    Look gains "Field kit only in your settlements" (on), after "Field kit"; a new section after Look,
    "Field kit preview" (New; As before is 2026-11-10a's view; Tune uses its six sliders: size, turn,
    tilt, up / down, zoom out, zoom in); Riding's "Field of view riding in first person" is gone. The side
    bag's help says its parts count only with the kit allowed anywhere. Console: set CMB_KitWhere to 0,
    set CMB_KitPreview to 0.

  CMB_SLOPE.INI (every new key at its default in the file, with its comment):
    [Steer] QuickKeyCodes=auto, QuickKeyState=1, QuickCut=1, UseStopUnapplied=wait, UseStopWaitMax=3,
    UseStopLead=1.5; [Look] WornIndex=1, KeptMods=1, Repass=0, KitPreview=1, KitPreviewLog=1
    (KitPreviewPos, KitPreviewTurn, KitPreviewScale and KitPreviewZoom commented out at their defaults);
    [View] EyeLock=1, EyeAxes=1, Camera=1, EyeAtCamera=1, Fov=0; [Diag] QuickProbe=1, WornPasses=1,
    HandoverFromReady=1, ViewLock=1; [Sound] HeardKeep=1, HeardCreep=0.3, LiftDown=0.08, MenuQuiet=1,
    MenuQuietOut=0.15, MenuQuietIn=0.3. Changed defaults: [View] EyeAt=0,1,128 (was 0,12,128); [Sound]
    ShiftRpm=3500 (2500), Gears=410.6,636.4,954.5,1272.7,1626.4 (555.556,750,960,1161.6),
    ShiftDraw=3200,3700 (2300,3000), HeardRiseGears=2,0.79,0.65,1,1 (2.5,0.95,0.5,1),
    ShiftGapGears=0,2,3,1.5 (0,2,3), LaunchRise=650 (350), LaunchFlare=0.35 (0.5).

  EVERY NEW THING HAS A SWITCH whose off value is 2026-11-10a:
    [Steer] QuickKeyCodes=scan, QuickKeyState=0, QuickCut=0, UseStopUnapplied=cut; [Look] WornIndex=0,
    KeptMods=0, KitPreview=0 (Repass=0 is its default); [View] EyeAt=0,12,128, EyeLock=0, EyeAxes=0,
    Camera=0, EyeAtCamera=0, Fov=1 (then set CMB_ViewFov in the console: the slider is gone); [Diag]
    QuickProbe=0, WornPasses=0, HandoverFromReady=0, ViewLock=0; [Sound] MenuQuiet=0, HeardKeep=0,
    LiftDown=0, and the gears all together at ShiftRpm=2500, Gears=555.556,750,960,1161.6,
    ShiftDraw=2300,3000, HeardRiseGears=2.5,0.95,0.5,1, ShiftGapGears=0,2,3, LaunchRise=350,
    LaunchFlare=0.5; MCM "Field kit only in your settlements" off, "Field kit preview" As before. The one
    exception is the field kit's item and slot names (only names: an ESP with 2026-11-10a's can be built
    from the repository with the generator's --kit-names 0, and isn't in this package). 2026-11-10a's
    switches back to 2026-11-09a's are all still there.

  KNOWN, LEFT FOR NOW:
  - Whether the number keys reach the game's favourites handler at all is the self-test's to say; if they
    don't, QuickCut or UseStopUnapplied still heal at speed, after the clip's first moment.
  - The MCM's help for the built-in hotkey says "48 = B"; it may really be the 0 key (step 2 tells).
  - Free colour in third person relies on the game applying a swap's colour while it builds the ridden
    bike: the Palette test (step 6) says whether it does. An option you didn't choose keeps the last
    colour written into it until you choose it again (only the armour menu's preview shows that). The
    first getting on after a real change of parts (not just a colour) is still about 1.2 s slower.
  - The field kit's preview numbers are a first guess: the bike may be small (zoom in, or Tune), and test
    54's log lines set the final ones. The names have no switch in the game.
  - First person: how much of the shake goes is test 54's to say; the "view: lock:" lines tell what is
    left.
  - Whether the game lets a sound fade while it is paused is test 54's question; the throttle-off sound at
    the top of a pull is pitched further up than before.
  - From 2026-11-10a: with an animation mod that plays a decoration after each item use, a use at speed
    still starts that decoration, cut at its first frame (a dip of about 100-150 u/s for about 0.3 s);
    Caution 50 is only a new save's default; with [Lamp] Ahead set under about 10 and MCM "Headlamp casts
    shadows" on, the front end can shadow its own beam (the default 28 keeps it clear); when getting on, a
    follower is stowed and the headlamp lit up to about a second after the screen is back.
  - From 2026-11-09a: a bike kept hidden by the guard when you go through a door or fast travel stays
    hidden where it waits until you call it; the parked bike blinks once when its look is put on outside a
    ride; the riding armours kept between rides stay in your inventory, hidden: before uninstalling, get
    off and run cqf CMB_ControllerQuest EmergencyReset, which takes them out too.
  - From 2026-11-08a: the plate's colours aren't previewed in the armour menu, and after you take a new
    design there the preview shows the old design's own text until you leave the kit; the rim styles you
    didn't fit are still drawn, invisible, on the parked bike; a rim style changed in the MCM while riding
    (or a load mid-ride with "Customise at the bike" off, on a rim style) puts the ridden bike on again
    within about a second; without F4SE the parked and first-person bikes stay stock and the ridden bike's
    colours stay their defaults; weathered paint, more badges, the front fender, the headlamp's colour and
    the seat come later.

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
  (WorkbenchArmorA, the field kit's mode 4) (docs\ASSETS.md lists them); since this build the plugin also
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
  3. If you had edited CMB_Slope.ini, put your values into the new one: [Steer], [Look], [View], [Diag]
     and [Sound] have new keys, and EyeAt and seven [Sound] gear keys new defaults (README.md's first key
     table lists them).
  4. Load test 53's save. Keep Global Stash by SKK installed. Before every quit copy both logs aside,
     renamed with the step (CMB_Slope_stepN.log, Papyrus_stepN.log): the plugin keeps only one earlier
     session. Then WHAT TO TEST below.
  Updating mid-ride: get off first, save, then update.

WHAT TO TEST (docs\TESTING.md, "The 2026-11-14a build", has the details and the log lines; the
numbers are its steps)
  1. Number keys at speed: a stimpak on number key 1, Jet on another. At full speed press 1 three times, a
     second apart, then Jet's key. Used at once, no animation, the speed kept? The log now names keys in
     hex (number key 1 is "key 0x31"); send every "quick: self-test" and "quick: this ride" line.
  2. The bike's hotkey: get on and off once each with it, as you always do, and tell us which key you
     press, 0 or B (the "quick: the ride began ... after the ... key" lines say which the game saw).
  3. [Steer] QuickUse=0, get on, a stimpak by its key at speed twice quickly: two heals, no slow-down? Jet
     once: one dose?
  4. Also QuickCut=0 (QuickUse still 0): about a second of the animation, then it stops; healed, the speed
     held? Then QuickUse=1 and QuickCut=1 back.
  5. Free colour (a hue other than 210, a plate with colours), in third person by the hotkey and by E:
     your hue from the first moment, every ride, and after a hue-only change (getting on as quick)? First
     person the same? After a load? Only if still wrong: [Look] Repass=1, get off and on; then back to 0.
  6. Paint "Palette test: colour index" at the field kit, ridden in third person: cobalt or primer grey?
     Optional: [Look] WornIndex=0, get on: blue again as in test 53? Then 1.
  7. First person, flat, on a slope and through turns: any shake? Your seat over the seat, not on the tank
     (or the MCM's "Eye forward on the bike" number you like)? Parked on a slope: the bars and dial still?
     A/B one ride each: [View] EyeLock=0; EyeAtCamera=0; EyeAxes=0. Send the "view: lock:" and "camera:"
     lines.
  8. The FOV setting is gone from the MCM; first person keeps the game's own field of view.
  9. Field kit in Sanctuary: the item "Motorbike", the slots "Paint: Factory" and so on, the whole bike in
     the preview? Screenshots as the menu opens and after a paint and a rim; zoom all the way out and in.
     Only if it looks wrong: "Field kit preview" Tune and its sliders (which values?). A/B: As before (the
     tyre).
  10. Customise on a road: refused with a message, nothing out of the side bag? With "Field kit only in
      your settlements" off: the kit opens. "Free customising" works anywhere.
  11. The Pip-Boy and Esc at full speed, 3 s each: quiet within a moment, the same note after? In water,
      the water quiet too?
  12. Gears: full throttle from a stop: five gears, higher shifts, 2nd and 3rd rising, a short 4th? A
      short lift in 2nd while speeding up, and at a steady low speed: no blip to 1st? A stop: blips as
      before.
  13. Not tried in test 53: knock an NPC down beside the parked bike and get off next to them: the bike
      hidden until they stand up?
  14. Not tried in test 53: a few A/Bs, one at a time: [Look] MountEarly=0, [Room] GuardBodies=0 (with
      step 13), [Steer] SidestepCaution=0, [Sound] MenuHold=0, HeardKeep=0. Anything better or worse?
  Send CMB_Slope.log (and CMB_Slope_prev.log after a crash), Papyrus.0.log, the copies you saved, any
  crash log, the screenshots of step 9, and a video if you have one.

QUESTIONS FOR YOU (docs\TESTING.md has them in full)
  T54-1. A stimpak by its number key at speed: used at once, no clip, the speed kept? Jet too?
  T54-2. Which key do you press for the bike's hotkey, 0 or B?
  T54-3. With QuickUse off: healed each time, one Jet dose? With QuickCut off too: healed after about a
         second?
  T54-4. Free colour right in third person from the first moment, every ride? The plate? After a load?
  T54-5. The Palette test: cobalt or primer grey?
  T54-6. First person: any shake left? Your seat place right? Which A/B was steadiest?
  T54-7. The item "Motorbike", the slot names, the whole bike in the preview? If you tuned it, which
         values?
  T54-8. Refused on the road, allowed in Sanctuary, and anywhere with the switch off?
  T54-9. The engine and the water quiet in the Pip-Boy and the pause menu, and back at the same note?
  T54-10. The five gears: the higher shifts, the short 4th, no drop on a lift, the throttle-off sound?
  T54-11. The bike hidden while a knocked-down NPC lay in its place?
  T54-12. Anything an A/B made better or worse?

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
