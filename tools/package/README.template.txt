COMMONWEALTH MOTORBIKE - READY-TO-INSTALL FILES (2026-11-17a, repository commit @COMMIT@)

The Data folder is the whole mod except the rider-pose plugin, which has to be built from
your own load order:

  Data\CommonwealthMotorbike.esp      the plugin, 2026-11-16b's, unchanged (no new record since
                                      2026-11-16a: 2026-11-16b changed three of the field kit
                                      preview's Tune values, to New's 1050, -2 and -45; 2026-11-16a's
                                      72 new records: the seat's slot and its 15 choices, the two 3D
                                      helmet badges and the Gunners skull on both tanks and the skull
                                      on the rear fender, and their lists; the look's recipes carry
                                      their place in the alphabetical order)
  Data\Scripts\*.pex                  compiled scripts (Caprica, Fallout 4 format; no Creation Kit
                                      needed), twelve, as before: CMB_HotkeyF4SE,
                                      CMB_GearRestoreF4SE and CMB_LookF4SE (the customised look on
                                      the parked, ridden and first-person bikes and its colours)
                                      need F4SE. One changes in this build: the controller (a quick
                                      swap between two weapons judged again a moment later, the
                                      message when a rifle comes holstered, the field kit's spot
                                      checked first); in 2026-11-16b the controller too (a weapon's
                                      put-away counts only the time the game runs)
  Data\Scripts\Source\User\*.psc      their sources
  Data\MCM\                           Mod Configuration Menu page and hotkeys, 2026-11-16b's,
                                      unchanged (since 2026-11-16a Look has a "Seat" dropdown after
                                      "Tyres", and its dropdowns list their choices alphabetically)
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
                                      the lamps and the frame-rate line by the game's frame, test
                                      55's fixes (2026-11-16b), and since this build test 56's: the
                                      first-person camera found as the game eases it, the bike kept
                                      near the camera at a handover, the bike drawn again in third
                                      person after your body, the eye in front of your neck, the
                                      arms hidden with the look key, the weapon rules kept across a
                                      menu, rifles never drawn while riding, the spikes from the
                                      hands, the field kit's bike held and turned to each slot, the
                                      kit's spot, the take-off and the stops' down-shifts (Fallout 4
                                      1.11.240 + F4SE 0.7.9 only); its settings are in CMB_Slope.ini
                                      beside it. Both change in this build
  Data\Sound\FX\CMB\                  engine sounds: the idle, start and stop and ten riding loops, built
                                      from a real V-twin's recording, and the mod's own two wet-road water
                                      loops, CMB_FxWaterRoadLP.wav and the gentler
                                      CMB_FxWaterRoadSoftLP.wav (see the credits at the end): 15 files,
                                      2026-11-10a's, unchanged
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
  Data\Textures\CMB\Bike\             its textures, 129 DDS. Eight change in this build, the same
                                      sizes: the badge atlas (badges_d/_n/_s.dds: the Gunners skull's
                                      flag patch, the Brotherhood of Steel emblem, the Enclave helmet's
                                      chrome plate), the seat palette (seat_p.dds: Saddle tan), the
                                      plate atlas (plates_d/_n/_s.dds: four designs) and the plate
                                      palette (plate_p.dds); the rest are 2026-11-16a's (in 2026-11-16a
                                      the helmets' four and the seat's two were new, and the badge
                                      atlas and the six plate textures changed)
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

WHAT'S NEW IN 2026-11-17a
  Test 56's fixes and its art corrections in one build (your pick; the rest of build B, wear and
  weathered paint, the front fender's badge and the headlamp's lens and beam, comes later), on top
  of 2026-11-16b. What test 56 liked is as it was. Changed since 2026-11-16b: CMB_Slope.dll,
  CMB_Slope.ini, the controller script and eight textures (the badge atlas, the seat palette, the
  plate atlas and its palette); the ESP, the MCM, the meshes, materials, sounds and riding clips are
  2026-11-16b's.

  WHAT TEST 57 SHOULD TRY (WHAT TO TEST below has the steps, 57-1 to 57-30):
  - steps 1-8, the art: the Brotherhood of Steel, Minutemen, Nuka-Cola and Red Rocket plates, the
    Enclave helmet on chrome, the Gunners skull on its green patch, the Brotherhood of Steel badge in
    colour, Saddle tan, each parked and from riding distance;
  - steps 9-11, the field kit: turning and zooming the bike, a view per slot, a kit by a wall;
  - steps 12-15, the take-off and the stops' down-shifts;
  - steps 16-22, handguns again (test 56's steps 25-26 ran with the weapon rules off: do them
    again, with the Pip-Boy between), rifles never drawn, a rifle's key with a pistol out, a quick
    swap, the ways a rifle can still come out, the spikes from the hands;
  - steps 23-29, first person: the shake, getting into first person, zoomed in across cells, the
    bike in third person after your body, looking down, the look key, backing over the shoulder;
  - step 30, the A/Bs.

  TEST 56'S ART CORRECTIONS (after your pictures; our own drawings, nothing traced or copied):
  - The plates (the letters unchanged): "Brotherhood of Steel" has the Brotherhood's emblem in
    colour top left (a white disc with three black cogs, a dark sword point up with a gold
    cross-guard and pommel, blue wings), the plate steel grey as before; "Minutemen" the flag's
    musket, lightning bolt and three stars in cream on the blue; "Nuka-Cola" a red crimped bottle
    cap with "Nuka" and "Cola" in white script and a swoosh, "ZAP THAT THIRST!" across the top;
    "Red Rocket" the whole plate as the round sign: black rim, red frame, yellow centre with red
    letters, the round sign (two R's back to back with a rocket) top left, RED ROCKET along the
    top and GASOLINE - DIESEL - FUSION along the bottom in white.
  - The 3D Enclave helmet stands on polished chrome inside the chrome edge (a thin dark line
    between them), where the black plate hid it; the Brotherhood helmet's plate stays steel grey.
  - "Gunners skull": a rough-edged white skull with the X on its brow on a deep green flag patch
    with slightly rounded corners, on both tanks and the rear fender.
  - The flat "Brotherhood of Steel" badge is the colour emblem (a white disc with three black gears,
    a steel sword with a gold guard and pommel, blue wings, a black outline): no red wings.
  - "Saddle tan" is a browner, less yellow leather tan.

  TEST 56'S FIXES:
  - The first-person shake: test 56's fix never ran (it switched itself off 84 ms into first
    person). Your game's camera eases toward your place, trailing it by about 67 ms of your speed;
    the plugin now finds it that way, and the bike and your body follow it; if it can't, it says
    so and keeps looking, never off for the session ([View] CameraEase).
  - Zoomed in to your head in third person, the bars and the dial no longer vanish while the plugin
    swaps the first-person bike for a new one ([View] NearHandover).
  - "looks like crazy frog": after your body had shown in first person the bike wasn't drawn in
    third person until you got off; the plugin no longer sets the hidden flag on the bike's nodes
    with your body (the bike's shapes are shrunk away instead), so the bike is drawn again at once
    ([View] BodyNodes; two log lines say how the bike was left, [Diag] BodyWornLine).
  - Looking down you saw the inside of your outfit: your eye now sits at your face in front of the
    neck, so you see your chest from outside ([View] BodyEye=0,6,-3, was 0,2,-0.5; BodyLeanMax=40,
    was 35).
  - A second arm with the look key: the game's first-person arms are hidden while you look further
    aside than 30 degrees, unless a weapon is out ([View] BodyArmsLook).
  - The weapon rules switched off for the session by the Pip-Boy right after a put-away: the check
    now counts only while the game runs, and if it fails anyway the rules come back once the game
    and the script agree again ([Tilt] GunCheckUnpaused, GunCheckRecover).
  - "it shouldn't even be pulled out": riding with "Handguns only", a rifle is never drawn: it
    becomes your weapon but stays holstered ("Only a handgun can be used on the motorbike." still
    shows), ready when you get off; a rifle's number key with a pistol out puts the pistol away
    first ([Tilt] DrawHandgunOnly, QuickHolsterFirst).
  - The .44 put away as "not a handgun" in a quick swap: a weapon drawn while none is equipped at
    that moment is judged again 0.3 s later ([Tilt] GunJudgeWait).
  - Spikes from both hands in first person after a weapon swap in third person: two ways the
    plugin could draw a finger away from its hand are closed ([Tilt] NodelessOnce,
    SkinArraysCheck), and the log says if one still happens ([Diag] HeldWhere).
  - The field kit: no zoom, the bike grabbed only by its front wheel, a view per slot wished for:
    the plugin now holds the bike in the menu: drag with the left button above the lists to turn
    it about its middle, roll the wheel there to zoom; it turns to the part of the slot you're on
    (the rear for the plates, each side for the tanks, the seat from above, the rear fender, the
    wheels) ([Look] KitHold, KitSlotView). "field kit pushes me through the wall": its spot is
    checked first, and with no room the kit is set out where you stand ([Look] KitRoom).
  - "takeoff is a tad too slow": 2nd now at about 12 on the dial, the first second a little
    quicker, the rest as before ([Steer] LaunchFrom=0.14, was 0.1).
  - "shifting down ... is sometimes weird": coasting to a stop the engine now shifts down one gear
    at a time near the speeds it shifted up at, each with one blip, the idle as the bike stops; a
    hard brake drops to idle after a shift or two ([Sound] DownBands, DownBlend; HeardStop=900,
    was 300; HeardBrake=1500, was 600).

  NEXT:
  - The fixes test 57 asks for. Then the rest of build B, the second art build: wear and weathered
    paint (Weathered, Dusty, Muddy, Rusty, Bloody, two combinations, muddy tyres), a badge on the
    front fender, the headlamp's colour (the lens and the beam) and two more badges, Nuka-Cola and
    Red Rocket; later, from the open ends, seated clips for a drawn pistol, the right forearm aimed
    along the camera with a handgun out, the left hand to the pistol while reloading, first
    person's own pistol, an MCM switch for your body in first person, the riding bike kept through
    a rifle's put-away and a handgun drawn in first person, your body shown while backing.

  MCM:
    No change (the MCM folder is 2026-11-16b's). From 2026-11-16b: "Field kit preview"'s help says
    New is placed by the plugin, and Tune's sliders start at 1050, -2 and -45 in a new save.

  CMB_SLOPE.INI (every new key at its default in the file, with its comment):
    This build: [View] CameraEase=1, NearHandover=1, BodyNodes=0, BodyArmsLook=30; [Diag]
    BodyWornLine=1, HeldWhere=1; [Tilt] GunCheckUnpaused=1, GunCheckRecover=0.5, DrawHandgunOnly=1,
    QuickHolsterFirst=1, GunJudgeWait=1, NodelessOnce=1, SkinArraysCheck=1; [Look] KitHold=1 (with
    KitZoom=0.6,3,1.12, KitDrag=0.25,0.25, KitHoldAbove=0.55), KitSlotView=1 (with
    KitTurnTime=0.35, KitViewRear=-165,10, KitViewTankL=-90,10, KitViewTankR=90,10,
    KitViewSeat=-60,60, KitViewFender=-150,40, KitViewWheels=-80,3), KitRoom=1 (with
    KitRoomRing=20); [Sound] DownBands=170,400,700,860 (with DownBlend=100).
    Changed defaults: [Steer] LaunchFrom=0.14 (was 0.1); [View] BodyEye=0,6,-3 (0,2,-0.5),
    BodyLeanMax=40 (35); [Sound] HeardStop=900 (300), HeardBrake=1500 (600).

  EVERY NEW THING HAS A SWITCH whose off value is 2026-11-16b:
    [View] CameraEase=0, NearHandover=0, BodyNodes=1, BodyArmsLook=0, BodyEye=0,2,-0.5,
    BodyLeanMax=35; [Diag] BodyWornLine=0, HeldWhere=0; [Tilt] GunCheckUnpaused=0,
    GunCheckRecover=0, DrawHandgunOnly=0, QuickHolsterFirst=0, GunJudgeWait=0, NodelessOnce=0,
    SkinArraysCheck=0; [Look] KitHold=0, KitSlotView=0, KitRoom=0; [Steer] LaunchFrom=0.1; [Sound]
    DownBands= (empty), HeardStop=300, HeardBrake=600. Each is read on getting on. The art's switch
    is files: the 2026-11-16b package's eight textures (Data\Textures\CMB\Bike\badges_d.dds,
    badges_n.dds, badges_s.dds, seat_p.dds, plates_d.dds, plates_n.dds, plates_s.dds, plate_p.dds)
    in an MO2 mod of their own, ticked below this one, give test 56's plates, badges and seat back.
    The earlier builds' switches are all still there.

  KNOWN, LEFT FOR NOW:
  - First person: the camera fix rests on test 56's numbers (your camera easing toward your place);
    if your game's camera doesn't, the log says so loudly and the bike is placed as in test 56
    while the plugin keeps looking. The bike's return in third person after your body rests on a
    reading of the game's flags; if it still goes, two log lines say what is left on it. Backing
    over the shoulder still hides your body ([View] BodyBack=0 is the A/B), and it can flicker at
    the edge.
  - Weapons: whether every draw of your game goes through the call the plugin stops is one log line
    a ride's to say; a rifle that comes out another way (the Pip-Boy or the favourites menu with a
    weapon out) is put away after, as in test 56; R with a rifle equipped while riding does
    nothing, silently; a handgun drawn in first person still swaps the bike under you for the
    planted one, as in test 56; which of two causes made test 56's spikes isn't known yet.
  - The field kit: the menu's slot fields and its mouse input are read in a game for the first
    time (two log lines say what yours gives); dragging by the menu's own grab may jitter for a
    frame; a kit set out where you stand may overlap the bike or a wall.
  - The stops: the first down-shift comes about 0.7 s after you let go ([Sound] StopAfter=0.15 is
    an A/B); from a cruise the first shifts come quickly one after another; a hard brake ends in the
    clutch from 3rd; a lift and press at a steady speed can leave the engine a gear or two lower
    than in test 56.
  - The art: the Nuka-Cola cap is the plate's own red and reads faintly from riding distance; on
    Red Rocket's own background a thin yellow line can show round the black rim; the Enclave
    helmet's chrome at night is as rendered, not yet seen in the game.
  - Not changed: the stutter across cells, getting on after a change at the kit (about 6 s), the
    occasional frame-rate drops, VATS off on the bike.
  - From 2026-11-16b: Your body following the camera rests on the order test 55's log shows (your
    3D updated before the camera); if your game updates it after the camera, the hands run a frame
    ahead of the grips (the lock line's BodyFollowCamera part says so; A/B [View]
    BodyFollowCamera=0). The outfit pieces near your eye are judged by coarse bounds, so a chest
    piece, a backpack, a collar, a scarf or a sleeveless top near your neck may vanish from your
    view (A/B [View] BodyNear=10 or 0). A rifle drawn another way still swaps the bike under you for
    the planted one for 2-4 s. No one-handed aiming pose yet (the right hand stays on the grip with
    the gun in it, reloading too); a draw or a put-away can show one frame of the game's standing
    clip. The field kit's preview view was measured from test 55's screenshot. The engine's top is
    squeezed (a steady 38-52 on the dial all sounds about the same); a lower MCM speed makes the
    pull slower too.
  - From 2026-11-16a: a piped seat looks like its plain colour from riding distance; the steel grey
    plate on the Brotherhood paint is the weakest contrast of all the paints; every bike draws the
    four hidden helmets.
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
    change of parts (not just a colour) is slower.
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
  2. Install this zip's Data under the old mod's name and choose Replace (not Merge), or remove the
     old mod in MO2 and install this one fresh (over 2026-11-16b).
     By hand without MO2: copy Data over and let everything overwrite. The separate "Commonwealth
     Motorbike - Rider Pose" mod from make_rider_pose.bat stays as it is: no need to rerun it.
  3. If you had edited CMB_Slope.ini: put your values into the new one: [Tilt], [Look], [View],
     [Sound] and [Diag] have new keys, and [Steer] LaunchFrom, [View] BodyEye, BodyLeanMax, [Sound]
     HeardStop and HeardBrake new defaults (README.md's key tables list them).
  4. Load your save. Check that Riding's "Weapons while riding" says "Handguns only", and have two
     handguns and a rifle on the favourites' number keys. The plugin keeps the logs of the three
     sessions before; say which session each step was in. Then WHAT TO TEST below.
  Updating mid-ride: get off first, save, then update.

WHAT TO TEST, TEST 57 (docs\TESTING.md, "Test 57", has the details and the log lines; the numbers
are its steps: 1-8 the art corrections, 9-30 the fixes)
  For steps 1-8: at the field kit choose each, look at it in the kit, then at the parked bike close
  up, then from the riding camera, side and behind. A screenshot of each, close and riding.
  57-1. "Plate: Brotherhood of Steel": the white disc with three black cogs, the dark sword with a
        gold guard and pommel, blue wings, top left; the plate steel grey? From riding distance a
        white disc on blue wings?
  57-2. "Plate: Minutemen": the musket broken by a lightning bolt and three stars, cream on the blue?
  57-3. "Plate: Nuka-Cola": the red crimped cap with "Nuka" / "Cola" in white script and a swoosh,
        "ZAP THAT THIRST!" on top? Faint from riding distance?
  57-4. "Plate: Red Rocket": the whole plate as the round sign (black rim, red frame, yellow centre,
        the round sign top left, RED ROCKET and GASOLINE - DIESEL - FUSION in white)? Then another
        background: the centre takes it, the frame stays? For each plate: clear of the big letters?
  57-5. Tank L and Tank R "Enclave helmet (3D)": polished chrome under the helmet, a thin dark line
        inside the edge; the helmet clear by day and at night, not only its eyes? Too bright, too
        plain? "Brotherhood helmet (3D)": still steel grey?
  57-6. "Gunners skull" on Tank L, Tank R and Fender: the green patch with rounded corners, the
        rough white skull with the X, eye holes, nose hole, stitched teeth? Nothing cut off? As your
        picture?
  57-7. "Brotherhood of Steel" on the tanks and the fender: the colour emblem, no red?
  57-8. "Seat: Saddle tan": browner, no longer yellow? Still apart from Tobacco brown, Red, Cream?
        The A/B for 57-1 to 57-8: the 2026-11-16b package's eight textures (above) in an MO2 mod of
        their own, ticked below this one.
  57-9. Customise, the Motorbike: hold the left button above the lists and move the mouse: the bike
        turns about its middle, never tipping? The wheel above the lists zooms, on the lists it
        scrolls? Send the "kit: hold: ... the menu closed after ..." line. A/B: [Look] KitHold=0.
  57-10. Move through the slots: the plates show the rear, Tank L and R each side, Seat from above,
         Fender the rear fender, Rims and Tyres the wheels, Paint and Mirrors three-quarters; each
         turn gliding, the turn and zoom still yours? Screenshots of two. Send the "kit: slot: ..."
         line. A/B: [Look] KitSlotView=0.
  57-11. Park along a wall, stand at the bike's end on the wall's side, Customise with your usual
         field kit (the armour bench, mode 3): not moved into the wall, the bench where you stand?
         The same with the bench's side towards the wall. In the open as before? A/B: [Look]
         KitRoom=0.
  57-12. From a stop hold forward to the top: a little quicker in the first second, 2nd at about 12
         on the dial, then as before? Right now, still slow, too quick? A/Bs: [Steer]
         LaunchFrom=0.1, 0.17.
  57-13. Let go at the top and coast to a stop: four down-shifts one gear at a time, one blip each,
         over about two seconds, then the idle? The same from 30 and 20 on the dial. Late? A/Bs:
         [Sound] StopAfter=0.15; DownBands= with HeardStop=300 HeardBrake=600 (test 56's);
         DownBands=200,450,760,880.
  57-14. A hard brake from the top: one or two quick shifts, then the idle: natural?
  57-15. A half-second lift at a steady speed: no down-shift? A longer one: a gear or two lower, a
         bother? A/B: [Sound] DownBlend=0.
  57-16. (Test 56's 25 again.) Get on with a 10mm and ride off; within two seconds draw it in third
         person: seated, both hands on the bars, the pistol in your right hand, no bike swap? Ride,
         turn, stop, ride on; fire a few shots: where do the shots and the muzzle flash come from?
         A short video.
  57-17. (Test 56's 26 again.) Put it away and draw it a few times: a jerk, anything flying off?
         Put it away and open the Pip-Boy at once for 5 s or more, close, draw again: seated as
         before? Again after the pause menu and a quicksave, over a long ride. A/Bs: [Tilt]
         GunCheckUnpaused=0, GunCheckRecover=0, GunBothBars=0, GunCarry=0, GunRootFrame=0,
         GunPredictMax=0, GunStillRide=0.
  57-18. Riding with nothing drawn, a rifle's number key: never drawn, the message shown, the rifle
         your weapon, holstered? R does nothing while riding; R draws it after getting off? A/B:
         [Tilt] DrawHandgunOnly=0.
  57-19. With the pistol out, a rifle's number key: the pistol away, the rifle equipped holstered,
         the one whose key you pressed? A/B: [Tilt] QuickHolsterFirst=0.
  57-20. With a pistol out, cycle quickly through handguns only (the 10mm, the .44, the flare gun):
         each drawn, none put away? A/B: [Tilt] GunJudgeWait=0.
  57-21. Get on with a rifle out: put away first? Riding, a rifle from the Pip-Boy and from the
         favourites menu: put away after, as in test 56? Send the "gun: this ride the game asked N
         draw(s) through slot 0xC9 ..." lines (one at each getting off).
  57-22. Holster in third person, swap weapons by number keys in third person (the .44 among them),
         then first person: spikes from the hands? Then first person only. A/Bs: [Tilt]
         NodelessOnce=0, SkinArraysCheck=0.
  57-23. First person a few minutes, full speed, rough ground, turns, stop and go: still shaking?
         The body more than the bike, the hands off the grips? Send the "camera: the camera root at
         GetTranslation's answer read as the camera root eased ..." line; no "EyeAtCamera off"? A/B:
         [View] CameraEase=0.
  57-24. Get off and on a few times, into first person by the key and by the wheel: no jump or lag?
  57-25. In third person zoom in to your head and ride across a few cells: the bars and the dial
         never gone? A/B: [View] NearHandover=0.
  57-26. Third person, first person (your body shows), third person again, three or four times a
         ride: the bike under you in third person at once and for the rest of the ride? One bike in
         first person still? A/B: [View] BodyNodes=1 (the crazy frog back).
  57-27. Look down in first person, also riding: your chest, belly and legs from outside, no hole?
         Sitting right, hands on the grips? Screenshot. A/B: [View] BodyEye=0,2,-0.5 with
         BodyLeanMax=35.
  57-28. Hold Z and look aside and behind slowly: no second arm at any angle? With a pistol drawn
         too. A/B: [View] BodyArmsLook=0.
  57-29. Back up until the view looks over your shoulder (your body hidden, as in test 56); then
         [View] BodyBack=0: better, or the inside of your neck and shoulders? A flicker at the edge?
  57-30. Any of this build's A/Bs you haven't tried yet, one at a time (CMB_SLOPE.INI's switches
         above). Anything better or worse?
  Send CMB_Slope.log and its _prev logs and Papyrus.0.log of each session, any crash log, the
  screenshots of 57-1 to 57-8, 57-10 and 57-27, and a short video of 57-16 to 57-19, 57-22 and 57-25
  if you can.

QUESTIONS FOR YOU (docs\TESTING.md has them in full)
  T57-1. The Brotherhood of Steel plate's emblem, close and from riding distance?
  T57-2. The Minutemen plate's musket, bolt and stars?
  T57-3. The Nuka-Cola cap and its script? Faint from riding distance?
  T57-4. The Red Rocket plate as the round sign? Another background? The yellow line round the rim?
  T57-5. The Enclave helmet on chrome, by day and at night? The chrome too bright or too plain?
  T57-6. The Gunners skull on its green patch: as your picture? Anything cut off?
  T57-7. The Brotherhood of Steel badge in colour, no red?
  T57-8. Saddle tan no longer too yellow, still apart from the others?
  T57-9. The kit's bike turned by the drag about its middle, zoomed by the wheel? The close line?
  T57-10. A view per slot, gliding? Which views would you change? The "kit: slot:" line?
  T57-11. Along a wall, with the armour bench: not moved into it? In the open as before?
  T57-12. The take-off: right now?
  T57-13. Coasting to a stop: one gear at a time, natural? Late?
  T57-14. A hard brake: natural?
  T57-15. A short lift: no down-shift? A longer one: a bother?
  T57-16. A pistol drawn right after getting on: seated, both hands on the bars, the gun in hand, no
          swap? Where did the shots and the flash come from?
  T57-17. After the Pip-Boy, the pause menu and a quicksave: the seated pose every time? Any "weapon
          rules here off" line, and "back on"? A jerk?
  T57-18. A rifle by its key never drawn, the message shown?
  T57-19. A rifle's key with the pistol out: holstered, the right rifle?
  T57-20. A quick swap between handguns: none put away?
  T57-21. The Pip-Boy's and the favourites menu's rifle? The ride's "draw(s) through slot 0xC9" lines?
  T57-22. Any spikes from the hands? Which "rider:" line came?
  T57-23. First person still shaking? The "eased toward" line, and no "EyeAtCamera off"?
  T57-24. Into first person: no jump or lag?
  T57-25. Zoomed in across cells: the bars and the dial there at every handover?
  T57-26. The bike under you in third person after your body, every time? One bike in first person?
  T57-27. Looking down: your body from outside, sitting right?
  T57-28. The look key: no second arm at any angle?
  T57-29. Backing: BodyBack=0 better or worse? A flicker?
  T57-30. Anything a 2026-11-17a A/B made better or worse?

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
