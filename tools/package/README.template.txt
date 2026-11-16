COMMONWEALTH MOTORBIKE - READY-TO-INSTALL FILES (2026-11-16a, repository commit @COMMIT@)

The Data folder is the whole mod except the rider-pose plugin, which has to be built from
your own load order:

  Data\CommonwealthMotorbike.esp      the plugin (72 new records since 2026-11-15b: the seat's slot and
                                      its 15 choices, the two 3D helmet badges and the Gunners skull on
                                      both tanks and the skull on the rear fender, and their lists; the
                                      look's recipes carry their place in the alphabetical order)
  Data\Scripts\*.pex                  compiled scripts (Caprica, Fallout 4 format; no Creation Kit
                                      needed), twelve, as before: CMB_HotkeyF4SE, CMB_GearRestoreF4SE
                                      and CMB_LookF4SE (the customised look on the parked, ridden and
                                      first-person bikes and its colours) need F4SE. Two change: the
                                      controller (the seat's slot, the MCM's dropdowns, "Same as the
                                      left" for the new choices) and CMB_LookF4SE (the seat's colour)
  Data\Scripts\Source\User\*.psc      their sources
  Data\MCM\                           Mod Configuration Menu page and hotkeys (since this build Look has
                                      a "Seat" dropdown after "Tyres", and its dropdowns list their
                                      choices alphabetically)
  Data\F4SE\Plugins\CMB_Slope.dll     F4SE plugin: steeper slopes, farther camera, bike tilt, steering,
                                      the speedometer, the lights and the mirrors, the bike in first
                                      person, the landing and water sounds, the sidestep, the launch,
                                      items at speed, the look you fit at the bike, the parked bike kept
                                      out of people, Caution, the wheels, the gears, items by hotkey at
                                      speed, the bike's ready signal at getting on, the parked bike's
                                      guard, the engine through a menu, the number keys at speed, Free
                                      colour in third person, the first-person bike held under your eye,
                                      the field kit's preview, the engine quiet in menus, five gears, the
                                      camera's place in first person read right, the first-person bike
                                      hidden until it is coloured, the slower pull, three earlier logs
                                      kept, A and D turning the bike in first person, the view's lean,
                                      looking back and the look key, a handgun drawn seated and the
                                      put-away, your own body in first person, the wide sidestep, and the
                                      lamps and the frame-rate line by the game's frame (Fallout 4
                                      1.11.240 + F4SE 0.7.9 only); its settings are in CMB_Slope.ini
                                      beside it. Both are 2026-11-15b's, unchanged
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
                                      axis, lens and speedometer needle are. Since this build all five
                                      nifs carry the two 3D helmets on each tank plate, invisible until
                                      you choose one; CMB_BikeParts.ini is 2026-11-10a's, unchanged
  Data\Textures\CMB\Bike\             its textures, 129 DDS: since this build the helmets' four and the
                                      seat's two are new, and the badge atlas (the skull and the
                                      helmets' enamel plates) and the six plate textures (the emblems
                                      and the new plate font) change
  Data\Materials\CMB\Bike\            its material files, 468 (41 new since 2026-11-15b: the helmets'
                                      ten, the skull's and the two enamel plates' three, the seat's 28):
                                      one per surface for the riding bike, *_worn.bgsm, and one per
                                      surface for the parked bike. The meshes need them: a missing
                                      material file shows the bike magenta.
  Data\Meshes\Actors\Character\Animations\MT\CMB_Rider\          106 riding clips + CMB_RiderClips.json
                                                                 + CMB_RiderSeat.json
  Data\Meshes\Actors\Character\Animations\MT\CMB_Rider\Female\   106 female clips (CBBE seat height), same files

No optional folder, as 2026-11-14a. If the 2026-11-06a package's "Commonwealth Motorbike - 2026-11-02a look
(A-B)" is still in MO2, keep it unticked (or remove it): it has the old badge and none of the new shapes.

WHAT'S NEW IN 2026-11-16a
  The third customisation build, the first of two art builds (the author's picks): 3D helmet badges,
  the Gunners skull, the plates redrawn with a new plate font, the seat's colour, and the lists in
  alphabetical order. Nothing of riding changes: CMB_Slope.dll and CMB_Slope.ini are 2026-11-15b's.
  You haven't tried 2026-11-15a and 2026-11-15b yet: this package holds both, and test 55 (below)
  can run before test 56, after it or in the same round. Changed since 2026-11-15b: the ESP (72 new
  records), two scripts (the controller and CMB_LookF4SE), the MCM page, the five bike meshes, the
  badge atlas and the plate textures; new: the helmets' and the seat's textures and materials.

  WHAT TEST 56 SHOULD TRY (WHAT TO TEST below has the steps, 56-1 to 56-14):
  - the kit's lists and the MCM's dropdowns in alphabetical order, and a choice in the MCM applied
    as named (two probes: the log lines answer them);
  - the two 3D helmets: on their enamel plates, in the preview, parked, ridden and in first person;
    the Enclave's eyes at night; your knees in hard leans; the under-bar mirrors at full lock;
    "Same as the left"; nothing left over after going back to Stock; the Gunners skull;
  - each plate design at riding distance;
  - each seat colour, the dark ones in the game's light, the piped ones close up, the seat with Free
    colour and an MCM Apply mid-ride, an old save;
  - the frame rate beside the parked bike.

  NEW IN THIS BUILD:
  - Tank badges "Enclave helmet (3D)" and "Brotherhood helmet (3D)" (Steel 2, Screws 1, Adhesive 1):
    the tank's badge plate becomes a plain enamel plate with the stock badge's chrome edge (black for
    the Enclave, steel grey for the Brotherhood) and a cast helmet emblem of our own stands on it,
    centred on the plate and angled with it, about 2.5 cm proud: it catches the light and casts its
    own shading. The Enclave's eyes glow amber. "Same as the left" follows a 3D left. The flat
    "Enclave helmet" and "Brotherhood helmet" stay. Every bike carries both helmets on both sides,
    invisible until chosen, so going back to a flat badge or Stock leaves no helmet behind.
  - "Gunners skull" on both tanks and the rear fender (Adhesive 1, Cloth 1): a bone-white skull with
    a cross on the brow and a stitched mouth, no plate round it.
  - The licence plates: every design's emblem redrawn at the plate's own size, so it keeps its shape
    at riding distance, and a new die-pressed plate font for the texts and legends, in the style of
    1950s plates: narrow, square, flat-cut and raised. Layouts, texts and colours as before.
  - A new slot, "Seat" (Cloth 2, Adhesive 1; Dark brown, as it came, free): Black, Tobacco brown,
    Saddle tan, Oxblood, Olive drab, Cream, Slate grey, Red, Navy, Pre-war turquoise, and four with a
    contrasting piping: Black with red piping, Black with cream piping, Dark brown with cream piping,
    Oxblood with black piping. The leather keeps its grain, shading and worn edges; the black seats
    have half the stock leather's sheen so they read darker than the stock brown. Faction sets leave
    the seat.
  - The lists: the MCM's eleven Look dropdowns (both tank badges, the fender, Paint, Rims, Seat, the
    plate's four, Faction set) list their choices alphabetically after the pinned ones (as it came,
    None, "Same as the left", "The plate's own"; Paint's "Palette test: colour index" last); Mirrors
    and Tyres stay steppers. The kit's lists get the same order if the armour menu sorts by the
    recipes' priority (test 56 tells). Your saved choices don't change, only the order shown.
  - The first getting on after the update puts the look's mods on afresh once (logged).

  NEXT:
  - The fixes tests 55 and 56 ask for. Then build B, the second art build: wear and weathered paint
    (Weathered, Dusty, Muddy, Rusty, Bloody, two combinations, muddy tyres), a badge on the front
    fender, the headlamp's colour (the lens and the beam) and two more badges, Nuka-Cola and Red
    Rocket; later, from 2026-11-15b's open ends, seated clips for a drawn pistol, the left hand to
    the pistol while reloading, first person's own pistol, an MCM switch for your body in first
    person.

  MCM:
    Look: "Seat" after "Tyres" (22 controls; "Dark brown (as it came)" in every save); the eleven
    dropdowns alphabetical, read and set through the controller's properties (the globals keep the
    option's number, so saves don't change). If a dropdown always shows its first choice or a choice
    there does nothing, say so: the next build binds them to globals of their own.

  CMB_SLOPE.INI: no new key; the file is 2026-11-15b's (below).

  EVERY NEW THING IS OPT-IN: each slot starts as it came, and the helmets stay invisible until
    chosen. The old order of the lists and the old plates are files, not keys (README.md's first
    table): the 2026-11-15b package's six plate textures (Data\Textures\CMB\Bike\plates_d/_n/_s.dds
    and plate_text_d/_n/_s.dds) in an MO2 mod of their own ticked below this one give the old
    letters and emblems back.

  KNOWN, LEFT FOR NOW:
  - Whether the kit's lists follow the alphabetical order (and which way up), and whether the MCM's
    dropdowns work through the controller's properties, are test 56's to say.
  - The helmets are smaller than first planned: they fit inside the enamel plate both sides show and
    clear of the under-bar mirrors at full lock. Every bike draws the four hidden helmets (about
    14,000 triangles): test 56 measures the frame rate beside the parked bike.
  - A piped seat looks like its plain colour from riding distance (the welt is under a pixel there).
    The steel grey plate on the Brotherhood paint is the weakest contrast of all the paints (it reads
    by its chrome edge and gloss).
  - The 2026-11-15b build's known issues (below) still hold.

2026-11-15b AND 2026-11-15a (IN THIS PACKAGE TOO: TEST 55)
  2026-11-15b is the wishes build for tests 53 and 54, on top of 2026-11-15a (test 54's fixes), which
  you haven't tried yet: this package holds both, and test 55 covers both. What test 54 liked is as it
  was. Changed in 2026-11-15b since 2026-11-15a: the ESP (nine new records), two scripts (the
  controller and CMB_GearRestoreF4SE), the MCM page, CMB_Slope.dll, CMB_Slope.ini and four bike meshes
  (the right-hand cables); its textures, materials, sounds and riding clips were 2026-11-10a's.

  WHAT TEST 55 SHOULD TRY (WHAT TO TEST below has the steps, 1 to 24):
  - FIRST set the MCM's "Eye forward on the bike" and "Eye height on the bike" back to 0 (your save
    keeps them), and check that Riding's "Weapons while riding" says "Handguns only";
  - steps 1-10, 2026-11-15a's: the field kit's plate colours with no crash and its preview; first
    person steady with your eye in the right place, and no red tank right after getting on; getting
    on quick again; the slower pull from a stop and at speed; three earlier logs kept; the field kit
    refused outside a settlement;
  - steps 11-15, first person: A and D turning the bike; the view's lean in turns; looking back
    while reversing (over the shoulder, or third person); the look key (Z); your own body on the bike;
  - steps 16-20, a handgun on the bike: drawn seated with the left hand on the bar, no look back while
    a weapon is out and A/D turning the bike with it, a rifle put away, getting on with a weapon out,
    which pistols count, a save with a weapon out;
  - step 21, the bike stepping round parked cars and other wide things, never walls;
  - step 22, the right-hand cables turning with the bars; step 23, the frame-rate line; step 24, the
    A/Bs.

  TEST 53'S AND 54'S WISHES (2026-11-15b):
  - A and D in first person ("can turning with A and D be the same as when turning with mouse?"): they
    now turn the bike as the mouse does, with the lean and the bars, instead of moving you sideways
    ([Steer] FirstKeys).
  - The view leans into turns in first person with the bike, 4 degrees at the bike's whole lean by
    default: the MCM's "View leans in turns (first person, deg)", 0-10 ([View] Roll).
  - Looking back while reversing in first person ("there is no way to turn just the camera"): hold S a
    moment and the view turns over your shoulder (D right, A left), the mouse turns only your head
    while the bike keeps its heading, the other side key swings the view round the back, and W brings
    it to the front; or the MCM's "Third person" switches the camera to third person while you back
    ([View] LookBack). Hold Z to look round while riding in first person, the bike keeping its line:
    the MCM's Hotkeys "Look key (scan code)", 0 = none ([View] LookKey). The plugin first checks that
    your game's camera takes the turn; if it doesn't, the log says so, the lean and the look key do
    nothing and backing uses third person ([View] CameraTurn). With a weapon drawn there is no look
    back and no third person while backing, and the look key turns your head 60 degrees at most; the
    lean stays.
  - Handguns on the bike ("only handgun can be used ... hold handlebar with at least one hand
    (preferably left) and shooting with another (right)"): the MCM's "Weapons while riding" replaces
    "Allow combat while riding". "Handguns only", the default in every save, lets you draw and fire a
    handgun from the saddle: in third person you stay seated, the left hand on the bar, the right arm
    and the gun the game's own, the bike under you ([Tilt] GunPose). Anything else you draw is put
    away ("Only a handgun can be used on the motorbike."), getting on with a weapon out puts it away
    first ([Tilt] PutAway), and VATS stays off. "None" and "Any weapon (standing poses)" are the old
    switch off and on. Your old switch isn't carried over (it was on): that's on purpose. With a
    weapon drawn in third person A and D turn the bike too, instead of sliding it ([Steer]
    FirstKeysArmed), and loading a save no longer puts a drawn weapon away by itself.
  - Your own body in first person ("for 1st person it would be nice if character model was visible"):
    your arms with the hands on the grips, your chest and legs, in your outfit, in the pose you ride
    in third person (ride a moment in third person first, once a game session); the head and the worn
    bike hidden. Not with the Pip-Boy, a weapon out, an item's use or looking back ([View] Body). The
    open question is whether the game draws it at all: the log's "body:" lines answer it.
  - Sidestepping big things ("does it work only for mailboxes/lampposts?"): a parked car, a barrel
    group, a fence piece or debris that ends near your line on one side is now steered round on that
    side, braking a little meanwhile; never walls, buildings, cliffs or the ground, nor while you turn
    ([Steer] SidestepWide). The camera sweeping past a post no longer starts and drops a sidestep
    (SidestepSteady), and moving the mouse the way a sidestep goes keeps it, or hands it to you
    (SidestepMouseSide).
  - The right-hand cables: the two thin cables under the right switch block and the wire from the right
    of the bar now turn with the bars instead of floating in the air (the meshes).
  - The lamps' lead and the frame-rate line now count the game's own frames (the plugin runs twice a
    frame): the frame-rate line says about half what test 54's did, and a long pause is one line
    ([Lamp] FrameLead, [Diag] FpsFrames, PausedFrames).

  TEST 54'S FIXES (2026-11-15a, in this package too):
  - The two crashes at the field kit (both right after "Plate background: The plate's own"): the plate
    colours you choose there now go on the parked bike when you leave the menu, with the rest of the
    look, as the MCM's Apply does ([Look] KitDefer).
  - First person still shook: the fix that makes the first-person bike follow the game's own camera
    read the camera's place in the wrong space and switched itself off; it reads it as the world place
    it is now ([View] CameraWorld), and the bike's lead uses the game's own frame ([View] LeadFrame).
  - No preview in the kit's menu: New now puts the whole bike 400 ahead of the menu's camera, turned
    three-quarters; in Tune the first slider is "Preview distance" (less is a bigger bike).
  - The stock red tank for a moment in first person right after getting on: the first-person bike
    stays hidden until its colours are on, 3 s at most ([View] LookWait).
  - Getting on about 0.85 s slower than 2026-11-10a: with the look unchanged the colour work is now
    skipped ([Look] MountQuick).
  - The plugin keeps the three sessions before as CMB_Slope_prev.log, CMB_Slope_prev2.log and
    CMB_Slope_prev3.log ([Diag] KeepLogs).
  - Your eye: the default holds the "eye forward" -6 and "eye up" -3 you used ([View] EyeAt=0,-5,125);
    the MCM's two eye sliders still add to it, so set them back to 0.
  - The speed and the gears ("bike reaches 50 just on gear 2"): above 0.6 of its top speed the bike
    takes 5.5 s more to reach it, so the speed climbs with the gears and the top comes about when 3rd
    ends; the engine's gears and their sound are untouched ([Steer] PullTime, PullFrom).

  MCM:
    Riding: "Weapons while riding" (None, Handguns only, Any weapon (standing poses)) where "Allow combat
    while riding" was; after "Look down on getting into first person (deg)" two new controls, "Looking
    back while reversing (first person)" (Off, Over the shoulder, Third person) and "View leans in turns
    (first person, deg)" (0-10, 4). Hotkeys: "Look key (scan code)" after "Brake key (scan code)" (44 =
    Z, 0 = none). From 2026-11-15a: in "Field kit preview" "Preview size (%)" is "Preview distance"
    (100-2000, 400 = New; a save from 2026-11-14a first shows 30, which means New's 400 until you move
    it), and "Preview zoom in" starts at 3; Riding's "Eye forward on the bike" and "Eye height on the
    bike" are as before, but set both to 0 now (above).

  CMB_SLOPE.INI (every new key at its default in the file, with its comment):
    This build: [Steer] FirstKeys=1, FirstKeysArmed=1, SidestepWide=1 (with SidestepWideShift=160,
    SidestepWideRate=120, SidestepWideMost=25, SidestepWideLong=300, SidestepWideDrop=60,
    SidestepWideClear=40, SidestepWideTall=180), SidestepSteady=30, SidestepMouseSide=1; [Tilt]
    PutAway=1, GunPose=1, GunStandBack=1, GunPredict=1, GunBlend=0.25, GunSeatEvery=5; [Lamp]
    FrameLead=1; [View] CameraTurn=1, Roll=-1, LookBack=-1 (with LookBackAngle=150, LookBackHead=60,
    LookBackSide=1, LookBackAfter=0.3, LookBackIn=0.35, LookBackOut=0.3, LookBackLinger=0.5,
    LookBackSwing=0.4), LookKey=-1 (with LookMax=150, LookSnap=0.15), Body=1 (with BodyEye=0,7,7,
    BodyLeanMax=35, BodyShiftMax=15, BodyBack=100, BodyFade=1); [Diag] BodyProbe=1, BodyProbeEvery=10,
    FpsFrames=1, TurnEachRide=0, PausedFrames=1, GunTrace=1, GunListen=1. (-1 = the MCM's value;
    LookBack=2 acts only while the MCM's "Looking back while reversing" isn't Off.)
    2026-11-15a's: [Steer] PullTime=5.5, PullFrom=0.6; [Look] KitDefer=1, MountQuick=1,
    KitTuneDistance=1, KitPreviewScene=1; [View] CameraWorld=1, LeadFrame=1, LookWait=3; [Diag]
    KeepLogs=3. Its changed defaults: [View] EyeAt=0,-5,125 (was 0,1,128); [Look] KitPreviewPos=0,400,0
    (0,0,0), KitPreviewTurn=0,0,0.785398 (0,0.02,44.764), KitPreviewScale=1 (0.3), KitPreviewZoom=-1,3
    (-1,1), the four commented out at their defaults.

  EVERY NEW THING HAS A SWITCH whose off value is 2026-11-15a:
    [Steer] FirstKeys=0, FirstKeysArmed=0, SidestepWide=0, SidestepSteady=0, SidestepMouseSide=0; [View]
    CameraTurn=0, Roll=0, LookBack=0, LookKey=0, Body=0; [Tilt] PutAway=0, GunPose=0, GunStandBack=0;
    [Lamp] FrameLead=0; [Diag] FpsFrames=0, PausedFrames=0, BodyProbe=0, GunTrace=0, GunListen=0; the
    MCM's "Weapons while riding" None or Any weapon (the old switch off or on). The one exception is the
    cables, which are in the meshes (the 2026-11-10a package's four nifs copied back give the old ones).
    2026-11-15a's switches back to 2026-11-14a: [Look] KitDefer=0 (save first: it may crash at the kit
    again), MountQuick=0, KitTuneDistance=0, KitPreviewScene=0, and KitPreviewPos=0,0,0,
    KitPreviewTurn=0,0.02,44.764, KitPreviewScale=0.3, KitPreviewZoom=-1,1; [View] EyeAt=0,1,128,
    CameraWorld=0, LeadFrame=0, LookWait=0; [Steer] PullTime=0; [Diag] KeepLogs=1 (read at the game's
    start). The earlier builds' switches are all still there.

  KNOWN, LEFT FOR NOW:
  - First person: that your game builds its camera the way the plugin turns it is checked once a
    session (one log line); if not, the lean and the look key do nothing and backing uses third person.
    In first person a slow mouse move neither keeps nor lets go of a running sidestep (it ends by
    itself within 2 s). With a weapon drawn in third person, whether the bike turns on A and D or the
    body snaps back to the camera is test 55's to say.
  - Handguns: the shots and the muzzle flash leave from where the game's standing clip holds the gun
    (up to about 20-30 units off the drawn pistol); first person keeps the game's own two-handed
    pistol; reloading keeps the left hand on the bar; drawn at speed before a second or two of
    holstered riding it shows the standing pose once; which pistols count is test 55's to say.
  - Your body in first person: if the game hides it in a way the plugin can't undo, nothing new shows
    and the log says so; it needs a moment of third-person riding once a game session; the collar may
    look cut near the camera ([View] Near=5 is an A/B); no MCM switch ([View] Body=0).
  - The wide sidestep's numbers are a first, reasoned set; parked cars that are part of the scenery's
    combined meshes are still only braked for.
  - The cables: at full lock the cut opens 2-3 units behind the headlamp (not seen from your eye).
  - From 2026-11-15a: with IAF / Chem Reanimations, an item used at speed is used at once, but the start
    of that mod's decoration clip still shows for a moment; the kit's plate colours show on the parked
    bike when the menu closes, not while it is open; the preview's 400 is worked out from test 54's
    numbers (the bike may look small); that the camera's place is a world place is inferred (one log
    line a session settles it); the slower pull leaves little margin to the engine's own climb late in
    3rd, and a lower MCM speed makes it slower too.
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
    parked and first-person bikes stay stock and the ridden bike's colours stay their defaults.

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
  ArmorTorsoPowerT60, ArmorHatExtraLarge) and writes nothing into them; since 2026-11-15b the ESP's
  handgun list holds the game's pistol keyword (WeaponTypePistol), and the controller names the rifle
  keyword (WeaponTypeRifle) and the game's sheathe action (ActionSheath). Global Stash by SKK, another
  mod, is only asked about: whether its plugin (SKKGlobalStashScrapping.esp) is loaded, and then four of
  its forms by ID at run time; nothing of it is in this package.

INSTALL / UPDATE (Mod Organizer 2)
  1. Get off the bike, save, quit. If you edited CMB_Slope.ini, keep a copy of it.
  2. Install this zip's Data under the old mod's name and choose Replace (not Merge), or remove the old
     mod in MO2 and install this one fresh (over 2026-11-15b, or over 2026-11-14a: this package holds
     2026-11-15a and 2026-11-15b too). By hand without MO2: copy Data over and let everything
     overwrite. The separate "Commonwealth Motorbike - Rider Pose" mod from make_rider_pose.bat stays
     as it is: no need to rerun it. (If you run make_rider_pose.bat from the repository at this
     build's commit, it also writes CMB_RiderPose_report.txt next to CMB_RiderPose.esp: please send
     it; the plugin it makes is the same.)
  3. If you had edited CMB_Slope.ini: from 2026-11-15b nothing changed in it; from 2026-11-14a put your
     values into the new one: [Tilt], [Steer], [Lamp], [Look], [View] and [Diag] have new keys, and
     [View] EyeAt and the four KitPreview values new defaults (README.md's key tables list them).
  4. Load your save. In the MCM's Look section check "Seat" after "Tyres". Coming from 2026-11-14a:
     set "Eye forward on the bike" and "Eye height on the bike" back to 0 first, and check that
     "Weapons while riding" says "Handguns only". Keep Global Stash by SKK installed. The plugin keeps
     the logs of the three sessions before; say which session each step was in. Then WHAT TO TEST
     below.
  Updating mid-ride: get off first, save, then update.

WHAT TO TEST, TEST 56 (docs\TESTING.md, "The 2026-11-16a build", has the details and the log lines;
the numbers are its steps)
  56-1. The field kit's "Tank L", "Seat" and "Paint" lists: alphabetical from the top, from the
        bottom, or the old order? Screenshots.
  56-2. The MCM's Look dropdowns alphabetical, each showing your choice from before? Papyrus.0.log:
        "Look: the MCM reads its dropdowns through the controller's properties ..." on opening the
        page. Choose Seat "Saddle tan" and Tank badge, right "Brotherhood helmet (3D)", Apply: on the
        bike as named, still shown when you reopen the MCM? A seat chosen at the kit then shown in
        the MCM? If a dropdown is stuck on its first choice or a choice does nothing, say so.
  56-3. At the kit, "Tank L: Enclave helmet (3D)" and "Tank R: Brotherhood helmet (3D)", then the other
        way round: in the preview, parked, ridden and in first person, each inside its enamel plate,
        raised and cast-looking? Screenshots.
  56-4. After dark: the Enclave's eyes amber, parked and ridden, the headlamp on and off? Too bright,
        too dim, plastic? The metals by day?
  56-5. Both helmets on: lean hard both ways at speed, stop with the left foot down: any knee or leg
        through a helmet (which side, when)?
  56-6. The under-bar mirrors (egg, then D) at full lock both ways: clear of the helmets?
  56-7. "Same as the left" with a 3D left; a 3D left with the flat Enclave helmet on the right; both
        back to Stock: nothing left over on any bike, after a ride and after a save and a load?
  56-8. "Gunners skull" on the left, the right and the rear fender: how does it look?
  56-9. Each plate design at riding distance, with its own text and with one of yours: the new letters
        and emblems legible? Which aren't?
  56-10. Each seat colour, parked, ridden and in first person: as its name, grain and worn edges kept?
  56-11. Black, Oxblood, Tobacco brown, Navy and the stock Dark brown, by day, in shade and at night,
         close and from a few steps: which look alike? Black darker than the stock brown and still
         leather? Pre-war turquoise?
  56-12. The four piped seats close up: the welt clearly in its second colour?
  56-13. Free colour paint with a coloured seat, the hue moved: the seat unchanged? The seat changed in
         the MCM with Apply while riding: the first-person bike at once, the ridden one at the next
         getting on? A save from before the update: the seat as it came? Back to Dark brown: as before?
  56-14. Your frame rate 3-4 m from the parked bike at a fixed spot, still for 20 s: on 2026-11-15b
         (if you run test 55 first) and on this build, stock and with both helmets on.
  Send Papyrus.0.log and CMB_Slope.log of each session and the screenshots of 56-1 and 56-3.

WHAT TO TEST, TEST 55 (if you haven't run it yet; docs\TESTING.md, "The 2026-11-15a build" for steps
1-10 and "The 2026-11-15b build" for steps 11-24, has the details and the log lines)
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
  9. Customise on a road outside a settlement: refused with a message, nothing out of the side bag?
     With "Field kit only in your settlements" off, the same spot: the kit opens?
  10. Any of 2026-11-15a's A/Bs you haven't tried yet, one at a time (KitDefer=0 only on a save you can
      lose). Anything better or worse?
  11. First person, W held, steer with A and D only: the bike turns as with the mouse, no sliding
      sideways? The mouse as before? A/B: [Steer] FirstKeys=0.
  12. In those turns the view leans a little: try "View leans in turns (first person, deg)" from 0 to
      10. The log's "camera: GetRotation's answer ..." and "camera: the turn followed ..." lines (or a
      "camera: ... off this session" line): send them. A/B: [View] Roll=0.
  13. First person, from a stop hold S a moment: the view over your right shoulder (A: the left one),
      the mouse turning only your head, the other side key swinging the view round the back, W back to
      the front; with something right behind you too; the Pip-Boy while looking back. Then "Looking
      back while reversing" on "Third person": third person while you back? Which do you prefer?
  14. Hold Z in first person and move the mouse: only your head turns, the bike keeps its line? Does Z
      clash with one of your keys ("Look key (scan code)" takes another)?
  15. Ride a few seconds in third person, straight, then first person: your arms with the hands on the
      grips (following the bars), chest and legs in your outfit? No head or hair in view, no second
      bike, no flicker? The Pip-Boy, a drawn pistol, looking back: the body goes and comes back?
      Screenshots. Send the "body:" lines. If it looks wrong: [View] Body=0; the collar cut: [View]
      Near=5.
  16. A 10mm pistol: ride two or three seconds holstered, then draw it in third person: seated, the left
      hand on the bar, the bike under you? Aim, fire, reload, put it away; steer both ways; stop and
      ride off with it out; one draw straight after getting on (the old standing pose, once). A/Bs: [Tilt]
      GunPose=0, GunPredict=0.
  17. A weapon drawn: reverse in first person: the view stays ahead (the lean stays)? Put it away:
      over the shoulder again? With "Third person" in the MCM: stays in first person, no flicker or swap;
      drawn while backing in third person: back to first person at once? Z with it drawn: about 60
      degrees at most? Third person with it drawn, A and D: no sliding; does the bike turn, or the body
      snap back to the camera? A/B: [Steer] FirstKeysArmed=0.
  18. With the pistol out, a rifle's favourites key: "Only a handgun can be used on the motorbike.", the
      rifle put away within a second, you stay on? A/B: [Tilt] PutAway=0.
  19. Get on with a rifle out, then with the pistol out: both put away and you get on?
  20. A pipe pistol, a .44 revolver, a laser pistol, a plasma pistol, a flare gun: which can you draw?
      First person with the pistol out (the game's own arms, not changed yet). The MCM's "None" and "Any
      weapon (standing poses)" once each, then back to "Handguns only". A save made with the pistol out
      on the bike, loaded: the pistol still out, not put away by itself? A rifle switched to by its
      favourites key (being put away), saved at once and loaded: still put away, or the ride ended?
  21. Ride straight at parked cars, barrels, a short fence piece or debris with one side open (5-10 of
      them): a swerve round on the open side? Too sharp, too late, too close? A car right across the
      road, a wall, a cliff, a building's corner: only braking, as before? The mouse moved a little or a
      lot the way a sidestep goes, and the other way. A few sidesteps in first person with the mouse
      still: they run to the end? A/Bs: [Steer] SidestepWide=0, SidestepSteady=0, SidestepMouseSide=0.
  22. First person, slow or stopped, swing the bars: the cables under the right switch block and the
      wire from the right of the bar stay attached? The same in third person from the right. Anything
      broken behind the headlamp at full lock?
  23. Just look: the "time: the last 10 s" line about your real frame rate, ending "the plugin's task
      2.0 times a frame"? A/B: [Lamp] FrameLead=0.
  24. Any of 2026-11-15b's A/Bs you haven't tried yet, one at a time. Anything better or worse?
  Send CMB_Slope.log and its three _prev logs, Papyrus.0.log, any crash log, CMB_RiderPose_report.txt
  if you made it, the screenshots of steps 2 and 15, and a video of steps 16 and 18 if you can.

QUESTIONS FOR YOU (docs\TESTING.md has them in full)
  T56-1. The kit's lists: alphabetical from the top, from the bottom, or the old order?
  T56-2. The MCM's dropdowns alphabetical? The "reads its dropdowns" line? A choice applied as named,
         still shown after the kit?
  T56-3. The 3D helmets inside their plates, raised and cast-looking? Their size and place right?
  T56-4. The Enclave's eyes at night? The metals by day?
  T56-5. Any knee or leg through a helmet?
  T56-6. The under-bar mirrors clear of the helmets at full lock?
  T56-7. Anything left over after "Same as the left", a flat right, Stock again, a ride and a load?
  T56-8. The Gunners skull?
  T56-9. The plates at riding distance: legible? Which designs or characters aren't?
  T56-10. Each seat colour as its name, grain and worn edges kept?
  T56-11. Which dark seats look alike in the game's light? Black still leather? Pre-war turquoise?
  T56-12. The piped seats' welts clear close up?
  T56-13. The seat apart from Free colour? The MCM's Apply mid-ride? An old save's seat?
  T56-14. The frame rate beside the parked bike, before and after, stock and with the helmets?
  (test 55)
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
  T55-10. Anything a 2026-11-15a A/B made better or worse?
  T55-11. A and D in first person: the bike turns as with the mouse?
  T55-12. The view's lean: how much do you like? "Answer's matrix" or "transpose", and "the turn
          followed"?
  T55-13. Looking back while reversing: over the shoulder or third person, which do you prefer?
  T55-14. The look key: works? Z free in your bindings, or which key did you take?
  T55-15. Your body in first person: seen at all? Hands on the grips? What did "body: drawn?" say?
  T55-16. A handgun drawn while riding: seated, left hand on the bar, the bike under you? GunPredict=0?
  T55-17. A weapon drawn: the view ahead while reversing, first person kept, Z at about 60 degrees?
          A and D in third person: the bike turning, or the body snapping back?
  T55-18. A rifle by its favourites key: put away within a second, and you stayed on?
  T55-19. Getting on with a weapon out: put away and on?
  T55-20. Which pistols could you draw? "None" and "Any weapon" as the old switch? The saves loaded
          with a weapon out: the pistol still out, the rifle still put away?
  T55-21. Wide things stepped round: how did the swerve feel? Walls only braked for? First-person
          sidesteps running to the end?
  T55-22. The right-hand cables attached when the bars turn?
  T55-23. The frame-rate line about your real frame rate?
  T55-24. Anything a 2026-11-15b A/B made better or worse?

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
