COMMONWEALTH MOTORBIKE - READY-TO-INSTALL FILES (2026-11-16b, repository commit @COMMIT@)

The Data folder is the whole mod except the rider-pose plugin, which has to be built from
your own load order:

  Data\CommonwealthMotorbike.esp      the plugin (no new record since 2026-11-16a: three of the
                                      field kit preview's Tune values change, to New's 1050, -2 and
                                      -45; 2026-11-16a's 72 new records: the seat's slot and its 15
                                      choices, the two 3D helmet badges and the Gunners skull on
                                      both tanks and the skull on the rear fender, and their lists;
                                      the look's recipes carry their place in the alphabetical
                                      order)
  Data\Scripts\*.pex                  compiled scripts (Caprica, Fallout 4 format; no Creation Kit
                                      needed), twelve, as before: CMB_HotkeyF4SE,
                                      CMB_GearRestoreF4SE and CMB_LookF4SE (the customised look on
                                      the parked, ridden and first-person bikes and its colours)
                                      need F4SE. One changes in this build: the controller (a
                                      weapon's put-away counts only the time the game runs); in
                                      2026-11-16a the controller and CMB_LookF4SE (the seat's slot
                                      and colour, the MCM's dropdowns)
  Data\Scripts\Source\User\*.psc      their sources
  Data\MCM\                           Mod Configuration Menu page and hotkeys (since 2026-11-16a
                                      Look has a "Seat" dropdown after "Tyres", and its dropdowns
                                      list their choices alphabetically; since this build the "Field
                                      kit preview" helps describe New's new place)
  Data\F4SE\Plugins\CMB_Slope.dll     F4SE plugin: steeper slopes, farther camera, bike tilt,
                                      steering, the speedometer, the lights and the mirrors, the
                                      bike in first person, the landing and water sounds, the
                                      sidestep, the launch, items at speed, the look you fit at the
                                      bike, the parked bike kept out of people, Caution, the wheels,
                                      the gears, items by hotkey at speed, the bike's ready signal
                                      at getting on, the parked bike's guard, the engine through a
                                      menu, the number keys at speed, Free colour in third person,
                                      the first-person bike held under your eye, the field kit's
                                      preview, the engine quiet in menus, five gears, the camera's
                                      place in first person, the first-person bike hidden until it
                                      is coloured, the pull, three earlier logs kept, A and D
                                      turning the bike in first person, the view's lean, looking
                                      back and the look key, a handgun drawn seated and the
                                      put-away, your own body in first person, the wide sidestep,
                                      the lamps and the frame-rate line by the game's frame, and
                                      since this build test 55's fixes: the first-person camera's
                                      place, the bike while zooming in, the cell moves, the view's
                                      lean by the turning rate, the look back's pitch, what comes
                                      with your body, the put-away on the player, the handgun seated
                                      with both hands on the bars, the field kit's preview placed,
                                      the even climb and the gears at the matching speeds (Fallout 4
                                      1.11.240 + F4SE 0.7.9 only); its settings are in CMB_Slope.ini
                                      beside it. Both change in this build
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
  Data\Meshes\CMB\                    the bike (Nieve5677's cruiser, see the credits at the end):
                                      parked, and worn three ways: hanging off the seated rider
                                      (CMB_BikeWornRider.nif, ...RiderF.nif for the female/CBBE seat
                                      height) and planted on the ground (CMB_BikeWorn.nif);
                                      CMB_BikeView.nif, the bike you see under you in first person;
                                      CMB_BikeParts.ini tells the plugin where its wheels, steering
                                      axis, lens and speedometer needle are. Since 2026-11-16a all
                                      five nifs carry the two 3D helmets on each tank plate,
                                      invisible until you choose one: 2026-11-16a's, unchanged;
                                      CMB_BikeParts.ini is 2026-11-10a's, unchanged
  Data\Textures\CMB\Bike\             its textures, 129 DDS, 2026-11-16a's, unchanged (in
                                      2026-11-16a the helmets' four and the seat's two were new, and
                                      the badge atlas and the six plate textures changed)
  Data\Materials\CMB\Bike\            its material files, 468, 2026-11-16a's, unchanged (41 new in
                                      2026-11-16a: the helmets' ten, the skull's and the two enamel
                                      plates' three, the seat's 28): one per surface for the riding
                                      bike, *_worn.bgsm, and one per surface for the parked bike.
                                      The meshes need them: a missing material file shows the bike
                                      magenta.
  Data\Meshes\Actors\Character\Animations\MT\CMB_Rider\          106 riding clips + CMB_RiderClips.json
                                                                 + CMB_RiderSeat.json
  Data\Meshes\Actors\Character\Animations\MT\CMB_Rider\Female\   106 female clips (CBBE seat height), same files

No optional folder, as 2026-11-14a. If the 2026-11-06a package's "Commonwealth Motorbike - 2026-11-02a look
(A-B)" is still in MO2, keep it unticked (or remove it): it has the old badge and none of the new shapes.

WHAT'S NEW IN 2026-11-16b
  Test 55's fixes, on top of 2026-11-16a, the art build, which you haven't tried yet: this package
  holds both, and test 56 covers both (2026-11-16a's part is below). What test 55 liked is as it was.
  Changed since 2026-11-16a: CMB_Slope.dll, CMB_Slope.ini, the ESP (three Tune values), the controller
  script and four MCM helps; the meshes, textures, materials, sounds and riding clips are
  2026-11-16a's.

  WHAT TEST 56 SHOULD TRY (WHAT TO TEST below has the steps, 56-1 to 56-37):
  - steps 1-14, 2026-11-16a's art: the kit's lists and the MCM's dropdowns in alphabetical order, the
    two 3D helmets, the Gunners skull, the plates, the seat's colours, the frame rate beside the
    parked bike;
  - steps 15-20, first person: still shaking? zooming in with the wheel; a stutter across cells (with
    an A/B); the view's lean; the mouse while looking back; A and D at 0.45;
  - steps 21-24, your body in first person: one bike, no gun on the grip, nothing of your outfit in
    front of your eye (and nothing gone that you want to see), where the body sits;
  - steps 25-29, a handgun on the bike: drawn right after getting on, seated with both hands on the
    bars and the gun in hand; a rifle put away at once, a save right after it; the rifle's bike swap;
  - steps 30-32, the field kit's preview: the whole bike, zoom and turn;
  - steps 33-36, the pull and the gears: a full pull, steady speeds, picking up again, a log; step 37,
    the A/Bs.

  TEST 55'S FIXES:
  - The first-person shake ("EyeAtCamera off this session" again): the game's answer for the camera's
    place is your eye's offset from your own place, which the camera reads at its own moment; the
    plugin now finds which way your game uses it and the first-person bike follows the camera's own
    place ([View] CameraPlace).
  - No bike for about half a second when zooming into first person with the wheel (the game fades you
    and the worn bike before it switches): the first-person bike now shows in the riding bike's place
    meanwhile, the worn bike hidden ([View] NearThird).
  - The first-person stutter: the first-person bike was moved between the cells' scene nodes at every
    cell crossed (196 moves); now only near a cell's edge, straight from cell to cell, and a log line
    on getting off says whether a move costs a frame ([View] ParentKeep, [Diag] ParentTime).
  - "didn't see any difference" with the view's lean: the MCM's "View leans in turns" is now the lean
    in degrees in an ordinary turn at speed, more in a sharp one, less in a gentle one ([View]
    RollTurn). Looking back while reversing, the mouse now tilts the view up and down, up to 45
    degrees ([View] LookPitch). A and D in first person turn at 0.45 of the old rate, your pick
    ([Steer] FirstKeys).
  - With your body in first person: the second set of bars and speedometer (the worn bike, which the
    game drew though it was flagged hidden) is shrunk away ([View] BodyWorn); the holstered gun on the
    right grip is hidden ([View] BodyWeapon); outfit pieces near your eye with no sleeve or glove in
    them, like the rusty cage, are shrunk away ([View] BodyNear); the game's first-person arms are
    hidden while you look back ([View] BodyArmsBack), and stay hidden through VATS or getting off
    until the next first-person frame; your body follows the camera's own place with the first-person
    bike, so your hands stay on the grips ([View] BodyFollowCamera); your eye is where the game's own
    is, so the body sits on the seat ([View] BodyEye=0,2,-0.5, was 0,7,7). The "body: drawn?" line,
    which couldn't tell, is gone ([Diag] BodyDrawn).
  - The put-away never called the game ("0 calls", the rifle could still fire): your game's player has
    its own form of the call the plugin checks, and it is taken now, so a rifle is put away at once
    ([Tilt] PutAwayProbe). A save right after the put-away began ended the ride: its seconds now count
    only while the game runs ([Tilt] PutAwayUnpaused).
  - A handgun in third person ("the right arm swings out"): seated with both hands on the bars, the
    pistol carried into your right hand on the grip, the pose read against the right frame and no jump
    carried on at a draw ([Tilt] GunBothBars, GunCarry, GunRootFrame, GunPredictMax); drawn right
    after getting on, the seat pose taken at getting on serves, so the bike isn't swapped ([Tilt]
    GunStillRide).
  - The field kit's preview ("half of the bike was in view"): the plugin now places the whole bike in
    the menu's view, in its upper half, turned three-quarters and seen a little from above; the zoom
    and the turning still work ([Look] KitFit, KitFind). New's record is 0,1050,-45, a little from
    above, and Tune starts there in a new save.
  - The gears ("1st gear shoots bike up to 30 almost instantly ... 1st should be short, up to 10, then
    gradually change"): the bike now gains speed evenly from the press, 1st to about 10-12 on the
    dial, 2nd to about 24, 3rd to about 42, 4th to about 50, the top about when 5th comes in (about 8
    s), the engine sounding as in test 55 at these speeds ([Steer] PullTime, PullFrom, LaunchFrom,
    PullClimb; [Sound] SpeedMap).

  NEXT:
  - The fixes test 56 asks for. Then build B, the second art build: wear and weathered paint
    (Weathered, Dusty, Muddy, Rusty, Bloody, two combinations, muddy tyres), a badge on the front
    fender, the headlamp's colour (the lens and the beam) and two more badges, Nuka-Cola and Red
    Rocket; later, from the open ends, seated clips for a drawn pistol, the right forearm aimed along
    the camera with a handgun out, the left hand to the pistol while reloading, first person's own
    pistol, an MCM switch for your body in first person, the riding bike kept through a rifle's
    put-away.

  MCM:
    No new control. "Field kit preview": its help says New is placed by the plugin; Tune's "Preview
    distance", "Preview tilt" and "Preview up / down" start at New's 1050, -2 and -45 in a new save
    (your save keeps 400, 0, 0: set them by hand if you use Tune). From 2026-11-16a: Look's "Seat"
    (below).

  CMB_SLOPE.INI (every new key at its default in the file, with its comment):
    This build: [View] CameraPlace=1, NearThird=60 (with NearFade=0.99), ParentKeep=1 (with
    ParentMargin=256), RollTurn=40, LookPitch=45, BodyWorn=1, BodyWeapon=1 (with
    BodyWeaponNodes=WEAPON), BodyNear=20, BodyArmsBack=90, BodyFollowCamera=1; [Diag] ParentTime=1,
    BodyDrawn=1; [Tilt] PutAwayProbe=1, PutAwayUnpaused=1, GunRootFrame=1, GunBothBars=1, GunCarry=1,
    GunStillRide=1, GunPredictMax=15; [Look] KitFind=1, KitFit=1 (with KitFitView=40,
    KitFitBox=0.07,0.50); [Steer] PullClimb=1; [Sound] SpeedMap=225:480,430:700,680:910,935:935.
    Changed defaults: [Steer] FirstKeys=0.45 (was 1), PullTime=8 (5.5), PullFrom=0.1 (0.6),
    LaunchFrom=0.1 (0.25); [View] BodyEye=0,2,-0.5 (0,7,7); [Look] KitPreviewPos=0,1050,-45 (0,400,0),
    KitPreviewTurn=-0.223219,0,0.785398 (0,0,0.785398), the two commented out at their defaults.
    2026-11-16a added no key.

  EVERY NEW THING HAS A SWITCH whose off value is 2026-11-16a:
    [View] CameraPlace=0, NearThird=0, ParentKeep=0, RollTurn=0, LookPitch=0, BodyWorn=0,
    BodyWeapon=0, BodyNear=0, BodyArmsBack=0, BodyEye=0,7,7, BodyFollowCamera=0; [Diag] ParentTime=0,
    BodyDrawn=0; [Tilt] PutAwayProbe=0, PutAwayUnpaused=0, GunRootFrame=0, GunBothBars=0, GunCarry=0,
    GunStillRide=0, GunPredictMax=0; [Look] KitFind=0, KitFit=0, KitPreviewPos=0,400,0,
    KitPreviewTurn=0,0,0.785398; [Steer] FirstKeys=1, PullTime=5.5, PullFrom=0.6, LaunchFrom=0.25,
    PullClimb=0; [Sound] SpeedMap= (empty); the MCM's Tune sliders at 400, 0 and 0. Each is read on
    getting on. The earlier builds' switches are all still there.

  KNOWN, LEFT FOR NOW:
  - First person: which way your game uses the camera's answer is settled by one log line ("camera:
    the camera root at ..."); if none fits, the plugin turns that part off as before and the line says
    why. Whether a cell move costs a frame is the ParentTime line's and the ParentKeep=0 A/B's to say.
    Your body following the camera rests on the order test 55's log shows (your 3D updated before the
    camera); if your game updates it after the camera, the hands run a frame ahead of the grips (the
    lock line's BodyFollowCamera part says so; A/B [View] BodyFollowCamera=0).
  - Your body: the outfit pieces near your eye are judged by coarse bounds, so a chest piece, a
    backpack, a collar, a scarf or a sleeveless top near your neck may vanish from your view (A/B
    [View] BodyNear=10 or 0). A rifle drawn still swaps the bike under you for the planted one for 2-4
    s, as in test 55; a pistol drawn soon after can show the standing pose once.
  - Handguns: no one-handed aiming pose yet (the right hand stays on the grip with the gun in it,
    reloading too); a draw or a put-away can show one frame of the game's standing clip; where the
    game hangs the drawn gun, and whether the shots and the muzzle flash leave from the gun in your
    hand, is test 56's to say (one log line a draw).
  - The field kit's preview: the menu's view was measured from test 55's screenshot; if the bike looks
    bigger or smaller than planned, [Look] KitFitBox sizes it; if the menu puts its own place back
    every frame, what shows depends on the game (the log's close line and your screenshot say).
  - The pull: the take-off is gentler than before (0.3 of the top after about 2 s; 0.4 s in test 55)
    and slow speeds pick up more slowly; the engine's top is squeezed (a steady 38-52 on the dial all
    sounds about the same, and in a full pull 4th settles while the needle still climbs from about 42
    to 50); a lower MCM speed makes the pull slower too.
  - From 2026-11-15b: that your game builds its camera the way the plugin turns it is checked once a
    session (one log line); if not, the lean and the look key do nothing and backing uses third
    person. In first person a slow mouse move neither keeps nor lets go of a running sidestep (it ends
    by itself within 2 s). Your body in first person needs a moment of third-person riding once a game
    session; the collar may look cut near the camera ([View] Near=5 is an A/B); no MCM switch ([View]
    Body=0).
  - The wide sidestep's numbers are a first, reasoned set; parked cars that are part of the scenery's
    combined meshes are still only braked for.
  - The cables: at full lock the cut opens 2-3 units behind the headlamp (not seen from your eye).
  - From 2026-11-15a: with an item animation mod, an item used at speed is used at once, but the start
    of that mod's decoration clip still shows for a moment; the kit's plate colours show on the parked
    bike when the menu closes, not while it is open.
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

2026-11-16a (IN THIS PACKAGE TOO: TEST 56, STEPS 1-14)
  The third customisation build, the first of two art builds (the author's picks): 3D helmet badges,
  the Gunners skull, the plates redrawn with a new plate font, the seat's colour, and the lists in
  alphabetical order. Its plugin was 2026-11-15b's; its art is this package's. Changed in 2026-11-16a
  since 2026-11-15b: the ESP (72 new records), two scripts (the controller and CMB_LookF4SE), the MCM
  page, the five bike meshes, the badge atlas and the plate textures; new: the helmets' and the seat's
  textures and materials.

  NEW IN 2026-11-16a:
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

  MCM:
    Look: "Seat" after "Tyres" (22 controls; "Dark brown (as it came)" in every save); the eleven
    dropdowns alphabetical, read and set through the controller's properties (the globals keep the
    option's number, so saves don't change). If a dropdown always shows its first choice or a choice
    there does nothing, say so: the next build binds them to globals of their own.

  EVERY NEW THING IS OPT-IN: each slot starts as it came, and the helmets stay invisible until
    chosen. The old order of the lists and the old plates are files, not keys (README.md's table of
    the 2026-11-16a build's switches): the 2026-11-15b package's six plate textures (Data\Textures\CMB\Bike\plates_d/_n/_s.dds
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
  2. Install this zip's Data under the old mod's name and choose Replace (not Merge), or remove the
     old mod in MO2 and install this one fresh (over 2026-11-15b: this package holds 2026-11-16a too).
     By hand without MO2: copy Data over and let everything overwrite. The separate "Commonwealth
     Motorbike - Rider Pose" mod from make_rider_pose.bat stays as it is: no need to rerun it.
  3. If you had edited CMB_Slope.ini: put your values into the new one: [Tilt], [Steer], [Look],
     [View], [Sound] and [Diag] have new keys, and [Steer] FirstKeys, PullTime, PullFrom, LaunchFrom,
     [View] BodyEye and the two commented KitPreview values new defaults (README.md's key tables list
     them).
  4. Load your save. In the MCM's Look section check "Seat" after "Tyres", and that Riding's "Weapons
     while riding" says "Handguns only". If you use the field kit preview's Tune, set its sliders to
     1050, -2 and -45 first. The plugin keeps the logs of the three sessions before; say which session
     each step was in. Then WHAT TO TEST below.
  Updating mid-ride: get off first, save, then update.

WHAT TO TEST, TEST 56 (docs\TESTING.md, "Test 56", has the details and the log lines; the numbers
are its steps: 1-14 2026-11-16a's art, 15-37 this build's fixes)
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
         (before you install this package) and on this build, stock and with both helmets on.
  56-15. First person, two or three minutes: full speed, rough ground, turns, standing still. Still
         shaking? Send the "camera: the camera root at ..." line; no "EyeAtCamera off" line? A/B:
         [View] CameraPlace=0.
  56-16. In third person zoom into first person with the mouse wheel, slowly, a few times, and back
         out: one bike all the way, never none, never two? A/B: [View] NearThird=0.
  56-17. A long straight run across a few cells in first person: any stutter? The same run with [View]
         ParentKeep=0: which stutters more? Send the "view: Parent: this ride ..." lines of both.
  56-18. "View leans in turns (first person, deg)" at 2, 5 and 10 in ordinary turns at speed: a clear
         difference now? Which do you like? A/B: [View] RollTurn=0.
  56-19. Back up in first person until the view is over your shoulder, move the mouse up and down: the
         view tilts (45 degrees at most) and comes back level when you ride on? The first-person arms
         gone while you look back (and with Z, looking far round)? Still looking back, open VATS, and
         another time get off: afterwards, in first person, your first-person arms and weapon there?
         A/Bs: [View] LookPitch=0, BodyArmsBack=0.
  56-20. A and D in first person at 0.45: right, too much, too little? A/B: [Steer] FirstKeys=1.
  56-21. Ride a few seconds in third person, then first person at speed: one set of bars and one
         speedometer? Stop and go again. Screenshots. A/B: [View] BodyWorn=0.
  56-22. A weapon holstered (two or three from the quick menu): no gun on the right grip in first
         person? A/B: [View] BodyWeapon=0.
  56-23. Look down: hands, sleeves and Pip-Boy there, the rusty cage gone, nothing else of your outfit
         in front of your eye? Anything gone that you want to see (a sleeveless top, a vest, a
         backpack)? What do you wear? Screenshot. A/Bs: [View] BodyNear=10, BodyNear=0.
  56-24. The body shown more often, in the first ride too? Sitting right, not sunk into the seat? Over
         bumps and at a hitch the hands on the grips, not a frame ahead or behind? Send the lock
         lines' "BodyFollowCamera: ..." part. A/Bs: [View] BodyEye=0,7,7, BodyFollowCamera=0.
  56-25. Get on with a 10mm pistol and ride off; within two seconds draw it in third person: seated,
         both hands on the bars, the pistol in your right hand, no bike swap? Ride, turn, stop, ride
         on; fire a few shots: where do the shots and the muzzle flash come from? A short video.
  56-26. Put it away and draw it again a few times, stopped and riding: a jerk (one frame is
         expected), anything flying off? A/Bs: [Tilt] GunBothBars=0, GunCarry=0, GunRootFrame=0,
         GunPredictMax=0, GunStillRide=0.
  56-27. With the pistol out, a rifle's favourites key: put away at once, no sheathe pause, you stay
         on? A/B: [Tilt] PutAwayProbe=0.
  56-28. The rifle key and a save at once: still on the bike after the save, the rifle away? A/B:
         [Tilt] PutAwayUnpaused=0.
  56-29. Get on with a rifle out: put away first, quickly? Riding, a rifle by its key, then the pistol
         within a few seconds: seated at once? A hitch in first person with the rifle's swap? First
         person with the pistol out: as before?
  56-30. Customise, the Motorbike: the whole bike in the upper half, three-quarters, a little from
         above? Screenshots at once and while browsing mods.
  56-31. Zoom with the wheel and turn it with the mouse: as before? A plate colour, then leave: on the
         parked bike at the close?
  56-32. Only if the bike is still cut or badly placed: the same as test 55, or another fault? [Look]
         KitFitBox (0.12,0.45 is smaller), or Tune from 1050, -2, -45: which values looked right?
         A/Bs: [Look] KitFit=0; "As before" and back to New.
  56-33. From a stop hold forward to the top on a flat road, watching the needle and listening: 1st to
         about 10-12, 2nd to 24, 3rd to 42, 4th to 50, the top as 5th comes in (about 8 s)? The sound
         as in test 55? The take-off too slow?
  56-34. Steady at about 10, 20, 30, 40 and 50 on the dial: the right gear, no hopping? From about 38
         up the engine sounds about the same: does that bother you?
  56-35. Pull away from half speed after a turn; tap off the throttle at speed: sluggish? The note
         steady?
  56-36. Ride slowly into a log or a kerb, forward held: climbed as before? A/Bs, a ride each: [Steer]
         PullTime=7, PullTime=9, [Sound] SpeedMap= (empty), 2026-11-16a's PullTime=5.5 PullFrom=0.6
         LaunchFrom=0.25 with SpeedMap=, [Steer] PullClimb=0 at a log.
  56-37. Any of this build's A/Bs you haven't tried yet, one at a time (CMB_SLOPE.INI's switches
         above). Anything better or worse?
  Send CMB_Slope.log and its _prev logs and Papyrus.0.log of each session, any crash log, the
  screenshots of 56-1, 56-3, 56-21, 56-23 and 56-30, and a short video of 56-25 to 56-28 if you can.

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
  T56-15. First person still shaking? The "camera: the camera root at ..." line, and no "EyeAtCamera
          off"?
  T56-16. Zooming in with the wheel: one bike all the way?
  T56-17. The stutter across cells, with ParentKeep 1 and 0? The ParentTime lines?
  T56-18. The view's lean visible now? Which value?
  T56-19. The mouse tilting the look back, level again on riding on? The arms gone looking back, and
          back after VATS or getting off?
  T56-20. A and D at 0.45: right?
  T56-21. One set of bars and one speedometer with your body shown?
  T56-22. No gun on the right grip?
  T56-23. Nothing in front of your eye? Anything gone that you want to see? What do you wear?
  T56-24. The body more often, sitting right? The hands on the grips at a hitch? BodyFollowCamera=0
          better or worse?
  T56-25. A pistol drawn right after getting on: seated, both hands on the bars, the gun in hand, no
          swap? Where did the shots and the flash come from?
  T56-26. A jerk at a draw or a put-away? Any gun A/B better?
  T56-27. A rifle by its key put away at once, and you stayed on?
  T56-28. A save right after the rifle key: still on the bike?
  T56-29. Getting on with a rifle out? A pistol soon after a rifle: seated at once? A hitch with the
          swap?
  T56-30. The kit's preview: the whole bike, in the upper half, three-quarters?
  T56-31. Zoom and turn as before? The plate colours at the close?
  T56-32. If still off: what, and which values looked right?
  T56-33. A full pull: the speed matching the gears? The take-off too slow? The sound as in test 55?
  T56-34. Steady speeds: the right gear, no hopping? The squeezed top: a bother?
  T56-35. Picking up again: sluggish? The note steady?
  T56-36. A log or a kerb as before? Which pull A/B felt best?
  T56-37. Anything a 2026-11-16b A/B made better or worse?

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
