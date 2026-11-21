COMMONWEALTH MOTORBIKE - READY-TO-INSTALL FILES (2026-11-21a, repository commit @COMMIT@)

The Data folder is the whole mod except the rider-pose plugin, which has to be built from
your own load order:

  Data\CommonwealthMotorbike.esp      the plugin: 151 new records in this build (the Wear, Front
                                      fender badge and Headlamp slots with their choices, Nuka-Cola
                                      and Red Rocket on both tanks and the rear fender, three muddy
                                      tyres, the headlamp's beam in four more colours) and 29
                                      changed in place (the look's lists, the three new attach points
                                      on the bike, the alphabetical order); 2026-11-16a's 72 records
                                      (the seat, the 3D helmets, the Gunners skull) and 2026-11-16b's
                                      three preview values as before
  Data\Scripts\*.pex                  compiled scripts (Caprica, Fallout 4 format; no Creation Kit
                                      needed), twelve, as before: CMB_HotkeyF4SE,
                                      CMB_GearRestoreF4SE and CMB_LookF4SE (the customised look on
                                      the parked, ridden and first-person bikes and its colours)
                                      need F4SE. Three change in this build: the controller (the
                                      three new slots, the headlamp's beam by its colour, the
                                      "Only a handgun" note only for the weapon you hold),
                                      CMB_LookF4SE (the three new slots) and CMB_GearRestoreF4SE (the
                                      worn weapon read for that note); in 2026-11-17a the controller
                                      too (a quick swap judged again, the rifle's message, the field
                                      kit's spot)
  Data\Scripts\Source\User\*.psc      their sources
  Data\MCM\                           Mod Configuration Menu page and hotkeys: Look has three new
                                      dropdowns in this build, "Front fender badge" after "Rear
                                      fender badge", "Wear" after "Paint shade" and "Headlamp"
                                      after "Mirrors" (25 controls), and "Tyres" steps through the
                                      muddy tyres too; the hotkeys are as before
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
                                      55's fixes (2026-11-16b), test 56's (2026-11-17a: the camera's
                                      ease, the bike after your body, rifles never drawn, the field
                                      kit's bike held, the stops' down-shifts), and since this build
                                      test 57's: the bike drawn again in third person after your
                                      body, the free look on the right mouse button and in third
                                      person, the game's aim blocked while riding, the field kit's
                                      bike held on every model the menu has with its wheel and drag
                                      anywhere off the lists, no holstered weapon in your hand, the
                                      seat pose kept through a put-away and a first-person draw, the
                                      longer coast and the even gears (Fallout 4 1.11.240 + F4SE
                                      0.7.9 only); its settings are in CMB_Slope.ini beside it. Both
                                      change in this build
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
                                      five nifs carry the two 3D helmets on each tank plate, and
                                      since this build the two thin wear shells and the front
                                      fender's badge patch, all invisible until you choose (the rear
                                      fender's patch sits a little higher now, over the wear): the
                                      five change in this build; CMB_BikeParts.ini is 2026-11-10a's,
                                      unchanged
  Data\Textures\CMB\Bike\             its textures, 180 DDS. 51 are new in this build (the wear's 42,
                                      the muddy tyres' six, the coloured lamps' three) and five
                                      change, the same sizes: the badge atlas (badges_d/_n/_s.dds:
                                      Nuka-Cola, Red Rocket, the Enclave helmet's flag, the
                                      Brotherhood helmet's cogs) and two plate textures
                                      (plates_d/_s.dds: four plates' top line centred); the rest are
                                      2026-11-17a's
  Data\Materials\CMB\Bike\            its material files, 524: 56 new in this build (the wear's 28,
                                      the muddy tyres' 12, the two shells' and the front fender
                                      patch's own six, the two new badges', the coloured lamps'
                                      eight), the rest 2026-11-17a's: one per surface for the riding
                                      bike, *_worn.bgsm, and one per surface for the parked bike.
                                      The meshes need them: a missing material file shows the bike
                                      magenta.
  Data\Meshes\Actors\Character\Animations\MT\CMB_Rider\          106 riding clips + CMB_RiderClips.json
                                                                 + CMB_RiderSeat.json
  Data\Meshes\Actors\Character\Animations\MT\CMB_Rider\Female\   106 female clips (CBBE seat height), same files

No optional folder, as 2026-11-14a. If the 2026-11-06a package's "Commonwealth Motorbike - 2026-11-02a look
(A-B)" is still in MO2, keep it unticked (or remove it): it has the old badge and none of the new shapes.

WHAT'S NEW IN 2026-11-21a
  Test 57's fixes, your wishes and the rest of build B, the second art build, in one build (your
  pick), on top of 2026-11-17a. What test 57 liked is as it was. Changed since 2026-11-17a:
  CMB_Slope.dll, CMB_Slope.ini, the ESP and the MCM (three new look slots), three scripts, the five
  meshes and five textures, and 107 new files (the wear, the muddy tyres, the coloured lamps, two
  badges); the sounds and the riding clips are 2026-11-17a's.

  THREE THINGS TO KNOW FIRST:
  - With "Weapons while riding" on "Handguns only" a rifle can't be drawn while riding at all
    (since 2026-11-17a, your pick after test 56): its number key equips it holstered, "Only a
    handgun can be used on the motorbike." shows, and R draws nothing until you get off. That is
    what test 57 saw with the hunting rifle: not a fault.
  - The free look is on the right mouse button now (Z still works), in first person and, new, in
    third person, and the game no longer aims while riding: the right button is the look's, the
    left button fires as usual ([View] LookButton, LookThird; [Steer] AimBlock).
  - At the field kit the mouse wheel zooms the bike wherever the cursor is, the lists too, and
    holding the left button anywhere off the lists turns it. The wheel no longer scrolls the
    lists: move through a long one with the arrow keys (or W and S) ([Look] KitMouse,
    KitWheelOwn).

  WHAT TEST 58 SHOULD TRY (WHAT TO TEST below has the steps, 58-1 to 58-32):
  - steps 1-12, the art: the seven wears over a few paints, the muddy tyres, the front fender
    badge, Nuka-Cola and Red Rocket, the Enclave helmet on its flag, the Brotherhood helmet
    between its cogs, the plates' top lines, the headlamp's five colours at night, everything as
    it came again, and the frame rate beside the parked bike;
  - steps 13-16, the field kit: the wheel and the drag anywhere, a slot's mods (E), the highlight
    walking, the three new slots' views;
  - steps 17-19, the even gears and the longer coast;
  - steps 20-24, the look on the right button and in third person, no aiming on the bike;
  - steps 25-28, handguns in third person: nothing in the hand while holstered, holstering, a
    draw in first person, cycling the number keys;
  - steps 29-31, the bike in third person after your body;
  - step 32, the A/Bs.

  ART BUILD B (our own drawings and shapes, nothing traced or copied; every new choice opt-in, each
  new slot starting as the bike came):
  - "Wear", seven looks over any paint, Free colour too: Weathered (sun-faded on top, chipped to
    primer and bare steel at the knee grips and the edges, stone chips, fine scratches), Dusty,
    Muddy (both fenders caked low and behind the wheels, the tank's lower front), Rusty (from the
    edges, round the badges and the plate, under the tank), Bloody (spatter, smears, drips), and
    two together: Wasteland (weathered, dusty and muddy) and Raider (rusty and bloody). Drawn on
    two thin shells over the paint; the tank's badge plates and the rear badge kept clear, the
    fender badges over it.
  - "Tyres": Black, muddy; Whitewall, muddy; Red line, muddy.
  - "Front fender badge": any badge of the rear fender's list, then Nuka-Cola and Red Rocket, on
    top of the front mudguard, read from in front; it turns with the bars.
  - "Headlamp": Warm (as it came), Cool white, Amber, Selective yellow, Blue-white, the lens and the
    beam alike; parked and unlit, a coloured lamp shows a tinted bulb.
  - Two new badges for both tanks and both fenders: Nuka-Cola (a red crimped bottle cap with
    "Nuka" and "Cola" in white script and the swoosh) and Red Rocket (the round sign: black rim,
    red ring with RED ROCKET, yellow centre with two R's back to back and a rocket).
  - Your wishes: the 3D Enclave helmet stands on the Enclave's flag (red and white stripes, the
    blue corner with a ring of 13 stars), the 3D Brotherhood helmet between two black cogs from
    the Brotherhood's emblem.
  - "only brotherhood of steel plate top text needs to be centered": centred, ending well inside
    the plate; the Minutemen, Nuka-Cola and Red Rocket plates' top lines too.

  TEST 57'S FIXES AND YOUR WISHES:
  - "bike and even character model were disappearing, mostly in 3rd person": after your body had
    shown in first person the game kept drawing you from what it had made while your body
    showed, the bike shrunk away. Back in third person the plugin now asks the game to redo it
    from the bike as it is; if the game leaves the ask, it is made the game's own way (you hidden
    for one frame) ([View] BodyRedraw, BodyRedrawHide; [Diag] ThirdWhere's "third:" lines say
    where everything is at each switch).
  - "can 'free camera' when on bike be under right-click instead of Z key?": the right mouse
    button looks round too ([View] LookButton=257); "I would like to block aiming because it slows
    down the bike": the game doesn't aim while riding ([Steer] AimBlock; [Diag] AimWatch says if an
    aim ever slows the bike).
  - "Z in 3rd person doesn't work": in third person the look swings the camera round you while the
    bike keeps its line, and the camera eases back behind you when you let go ([View] LookThird,
    LookThirdBack=0.5).
  - The field kit: "when selecting menu for e.g. plates bike goes into default position": in a
    slot's mods the menu shows a bike per mod, and the plugin now holds them all ([Look]
    KitFollow); the bike turns only to a slot the highlight rests on ([Look] KitSlotSettle=0.25);
    the wheel and the drag anywhere off the lists (your pick: [Look] KitMouse, KitListBox,
    KitWheelOwn); views for Wear, the front fender badge and the headlamp ([Look] KitNewSlots).
  - "pistols were just flying around when holstered, hunting rifle was placed in strange spots":
    the game's own copy of a holstered weapon in your right hand is hidden while riding (a holster
    mod's copy still shows) ([Tilt] GunHandHide); "legs were spasming": putting a pistol away in
    third person keeps you seated until the riding animation is back ([Tilt] GunAwayKeep=1.0);
    "running with a gun": a pistol drawn in first person is seated at once back in third person
    ([Tilt] GunSeatKeep); the "Only a handgun" message names only the weapon you hold ([Tilt]
    GunNoteSure).
  - "rolling distance should be twice as much as is now, with gradual slow down": let go at the
    top and the bike rolls about twice as far, slowing hardest at first and more gently as it
    slows, stopped after about 6 s ([Steer] CoastDrag=270,90).
  - "4th gear - 50-50? shortest currently": the gears change up in even steps, at about 12, 24, 36
    and 46 on the dial (your pick), and a coast's down-shifts come one at a time in the matching
    bands ([Sound] HeardRiseGears=2,0.86,0.8,1,1, ShiftGapGears=0,1.8,2,1.7,
    DownBands=170,380,600,780).

  NEXT:
  - The fixes test 58 asks for. Later, from the open ends: seated clips for a drawn pistol, the
    right forearm aimed along the camera with a handgun out, the left hand to the pistol while
    reloading, first person's own pistol, an MCM switch for your body in first person and for the
    look button and the aim's block, the riding bike kept through a rifle's put-away and a handgun
    drawn in first person, your body shown while backing.

  MCM:
    Look: "Front fender badge" after "Rear fender badge", "Wear" after "Paint shade", "Headlamp"
    after "Mirrors" (25 controls), each on its first choice; "Tyres" steps through six. Look's
    "Headlamp" is the lamp's colour; the Headlamp section's mode is as before.

  CMB_SLOPE.INI (every new key at its default in the file, with its comment):
    This build: [View] BodyRedraw=1, BodyRedrawHide=1, LookButton=257, LookThird=1 (with
    LookThirdBack=0.5); [Diag] ThirdWhere=1, AimWatch=1; [Steer] AimBlock=1, CoastDrag=270,90;
    [Look] KitFollow=1, KitSlotSettle=0.25, KitMouse=1 (with KitListBox=0.22,0.46,0.78,0.97),
    KitWheelOwn=1, KitNewSlots=1 (with KitViewWear=-45,15, KitViewFrontFender=0,25,
    KitViewHeadlamp=0,5); [Tilt] GunHandHide=1, GunAwayKeep=1.0, GunSeatKeep=1, GunNoteSure=1.
    Changed defaults: [Sound] HeardRiseGears=2,0.86,0.8,1,1 (was 2,0.79,0.65,1,1),
    ShiftGapGears=0,1.8,2,1.7 (0,2,3,1.5), DownBands=170,380,600,780 (170,400,700,860).

  EVERY NEW THING HAS A SWITCH whose off value is 2026-11-17a:
    [View] BodyRedraw=0, BodyRedrawHide=0, LookButton=0, LookThird=0; [Diag] ThirdWhere=0,
    AimWatch=0; [Steer] AimBlock=0, CoastDrag= (empty); [Look] KitFollow=0, KitSlotSettle=0,
    KitMouse=0, KitWheelOwn=0, KitNewSlots=0; [Tilt] GunHandHide=0, GunAwayKeep=0, GunSeatKeep=0,
    GunNoteSure=0; [Sound] HeardRiseGears=2,0.79,0.65,1,1, ShiftGapGears=0,2,3,1.5,
    DownBands=170,400,700,860. Each is read on getting on. The new look choices start as the bike
    came (Wear "As it came", Front fender badge "None", Headlamp "Warm (as it came)", the tyres
    and badges as you had them). The changed art's switch is files: the 2026-11-17a package's five
    nifs (Data\Meshes\CMB\CMB_BikeParked.nif, CMB_BikeWorn.nif, CMB_BikeWornRider.nif,
    CMB_BikeWornRiderF.nif, CMB_BikeView.nif), its badge atlas (Data\Textures\CMB\Bike\badges_d.dds,
    badges_n.dds, badges_s.dds) and two plate textures (plates_d.dds, plates_s.dds)
    in an MO2 mod of their own, ticked below this one, give test 57's meshes, helmet plates and
    top lines back (a wear, a front fender badge, Nuka-Cola and Red Rocket then have nothing to
    show on). The earlier builds' switches are all still there.

  KNOWN, LEFT FOR NOW:
  - The bike after your body: the fix rests on the game redoing what it draws of you when asked,
    as it does when you go into first person; the log says whether it took each ask. A
    single-frame flicker is possible right after the switch, and a part hidden at that moment
    (the brake light, the lamp's glow) could stay hidden until the next change.
  - The look and the aim: whether the plugin's key reading sees the right button while the game has the mouse
    (the log says which way the plugin read it); in third person the first look of the session
    teaches the plugin where the game keeps the camera's turn, and until then the bike turns
    toward the camera when you let go, as before; a pad's left trigger doesn't aim while riding
    either; no MCM switch for the button or the block (CMB_Slope.ini).
  - The field kit: which of the menu's bikes it shows isn't read (the plugin holds them all); the
    lists' box was measured on a 16:9 screen; a long list scrolls by the keys only, while the kit
    shows the bike.
  - Weapons: a holster mod's copy appears in its holster at a put-away and is tilted with you a
    tenth of a second later; after a draw in first person the bike under you may jump once when
    the script swaps it back.
  - The drive: the coast's last second may be a little shorter in the game than worked out; 5-4
    comes close under the pull's 4-5 ([Sound] DownBands=170,380,600,760 is the A/B if it comes
    above 46 on the dial); a side key near the end of a coast creeps up to a second later.
  - The art: the wear is a blended layer over the paint, which the game may light, sort or fade
    at a distance otherwise than the renders; blood on the dark paints reads more by its sheen;
    the wear runs partly under the tank's badge plates and is kept off them; every bike draws the
    two shells and the front patch, invisible until chosen (about 13,500 triangles: step 12 asks
    for the frame rate); a coloured lamp's bright centre can look near white or yellow, its colour
    in the glow and on the road, and Amber's beam is dimmer than Warm's; on the right tank the
    Enclave flag's blue corner is toward the rear; the ridden bike's lens takes a new colour at
    the next getting on (the beam at once).
  - From 2026-11-17a: the first-person camera fix rests on test 56's numbers (the log says so
    loudly if your camera doesn't ease so); backing over the shoulder still hides your body
    ([View] BodyBack=0 is the A/B), and it can flicker at the edge; whether every draw of your game
    goes through the call the plugin stops is one log line a ride's to say, and a rifle that comes
    out another way (the Pip-Boy or the favourites menu with a weapon out) is put away after; which
    of two causes made test 56's spikes isn't known yet; the field kit's menu fields are read in a
    game for the first time (its log lines say what yours gives), dragging by the menu's own grab
    may jitter for a frame, and a kit set out where you stand may overlap the bike or a wall; a
    stop's first down-shift comes about 0.7 s after you let go, a hard brake ends in the clutch
    from 3rd; the Nuka-Cola plate's cap reads faintly from riding distance, and on Red Rocket's own
    background a thin yellow line can show round the black rim. Not changed: the stutter across
    cells, getting on after a change at the kit (about 6 s), the occasional frame-rate drops, VATS
    off on the bike.
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
     old mod in MO2 and install this one fresh (over 2026-11-17a).
     By hand without MO2: copy Data over and let everything overwrite. The separate "Commonwealth
     Motorbike - Rider Pose" mod from make_rider_pose.bat stays as it is: no need to rerun it.
  3. If you had edited CMB_Slope.ini: put your values into the new one: [View], [Steer], [Tilt],
     [Look] and [Diag] have new keys, and [Sound] HeardRiseGears, ShiftGapGears and DownBands new
     defaults (README.md's key tables list them).
  4. Load your save. The MCM's Look section should have 25 controls ("Front fender badge", "Wear"
     and "Headlamp" new); if it has 22, an older ESP or MCM is loaded. Check that Riding's
     "Weapons while riding" says "Handguns only", and have a pistol, a second handgun and the
     hunting rifle on the favourites' number keys, your holster mod on as in test 57. The first
     getting on puts the look on afresh once. Note your frame rate beside the parked bike before
     you install, if you can (58-12). The plugin keeps the logs of the three sessions before; say
     which session each step was in. Then WHAT TO TEST below.
  Updating mid-ride: get off first, save, then update.

WHAT TO TEST, TEST 58 (docs\TESTING.md, "Test 58", has the details and the log lines; the numbers
are its steps: 1-12 the art, 13-16 the field kit, 17-32 the fixes and your wishes)
  For steps 1-11: at the field kit choose each, look at it in the kit, then at the parked bike close
  up, then from the riding camera, side and behind. A screenshot of each, close and riding.
  58-1. "Wear" on the stock paint, each in turn: Weathered, Dusty, Muddy, Rusty, Bloody, Wasteland,
        Raider. Parked from both sides and behind, then riding: does each read as its name?
  58-2. Muddy, then Bloody, over Gloss black and a Free colour: the wear stays over every paint?
        Blood on the dark paints readable?
  58-3. Wasteland with a rear and a front fender badge: the badges clean over the mud, no
        flicker? No wear across the tank badges or the rear badge, no hard line? The front
        mudguard's wear turning with the bars? The wear in first person, looking down?
  58-4. By day and at night, the lamp lit: the wear lit like the paint? A flicker or a halo from a
        distance? The lenses, the mirrors' glass, the chrome next to it?
  58-5. "Tyres": Black, muddy; Whitewall, muddy; Red line, muddy: tread caked, sidewalls splashed,
        the bands partly showing?
  58-6. "Front fender badge" Vault-Tec, then Gunners skull: on top of the front mudguard, the
        right way round from in front? Turning and moving with the wheel when riding?
  58-7. Tank L "Nuka-Cola" with Tank R "Same as the left", the rear fender and the front fender
        badge too; then all "Red Rocket": right? Nothing cut off? From riding distance?
  58-8. Tank L and R "Enclave helmet (3D)": the flag behind the helmet, the blue corner with its
        ring of stars? The stars too small, the flag too busy? The right tank's blue corner toward
        the rear: a bother?
  58-9. Tank L and R "Brotherhood helmet (3D)": a black cog each side of the helmet, clear of it
        and of the chrome edge?
  58-10. "Plate: Brotherhood of Steel" (SYNTH? on black): the top line centred over the big
         letters, clear of the tail lamp from low behind on the left? Minutemen, Nuka-Cola, Red
         Rocket too?
  58-11. At night (or "set gamehour to 22" in the console), "Headlamp" each in turn: the road in
         the colour, the lens glowing in it? Parked, a tinted bulb? Amber too dim? Riding, MCM
         Look "Headlamp" Amber and Apply: the beam amber at once, still after a few cells and
         after getting off and on? Once with "Headlamp casts shadows" on.
  58-12. Everything as it came again (Wear, Tyres, Front fender badge, Headlamp): exactly as
         2026-11-17a, no new flicker? The frame rate 3-4 m from the parked bike, still for 20 s:
         every slot as it came, then Wear Wasteland, same spot (and 2026-11-17a's if you noted
         it).
        The art's A/B for 58-1 to 58-12: the 2026-11-17a package's five nifs, three badge textures
        and two plate textures (above) in an MO2 mod of their own, ticked below this one.
  58-13. Customise, the Motorbike: roll the wheel anywhere, on the slot list too: the bike zooms,
         the highlight stays? Hold the left button beside or above the list and move the mouse:
         the bike turns? On the list the left button picks rows? A long list by the arrow keys:
         fine? Send the "kit: hold (2026-11-21a): ..." close line. A/Bs: [Look] KitWheelOwn=0,
         KitMouse=0.
  58-14. Plate text (the rear), E: the bike stays at the rear, every mod's preview the same? Tab
         back; the same on Paint and Tank L. Send the "kit: hold: the menu's models ..." line. A/B:
         [Look] KitFollow=0.
  58-15. The arrow keys quickly up and down the slots: no swing, a turn after a quarter second?
         A/B: [Look] KitSlotSettle=0.
  58-16. Wear (three-quarters from a little above), Front fender badge (the front mudguard from
         the front), Headlamp (the front): screenshots. A/B: [Look] KitNewSlots=0.
  58-17. From a stop hold forward to the top: the gears at about 12, 24, 36 and 46 on the dial, 4th
         about as long as 2nd and 3rd, each still climbing? A/B: [Sound]
         HeardRiseGears=2,0.79,0.65,1,1 ShiftGapGears=0,2,3,1.5 DownBands=170,400,700,860 (test
         57's gears).
  58-18. Let go at the top, no brake: about twice test 57's roll, slowing hardest first, about 42
         on the dial after 1 s, 30 after 2, 20 after 3, 11 after 4, stopped after about 6 s; the
         down-shifts one at a time over it? Too long, too short? A/Bs: [Steer] CoastDrag= (test
         57's), 300,60, 280,120, 225,225; if 5-4 comes above 46 on the dial, [Sound]
         DownBands=170,380,600,760.
  58-19. The same coast from about 30 on the dial; a hard brake from the top (as quick as
         before); A or D alone at the end of a coast (its creep later): a bother?
  58-20. First person at speed, no weapon: hold the right button and move the mouse: only your
         head turns? Z too? Send the "view: the look key (Mouse 2...) held ..." line.
  58-21. A pistol out, full speed, first person: hold the right button a few seconds: no sights,
         no zoom, no slowing? The left button fires? Then in third person. Send the "aim:" lines.
  58-22. [Steer] AimBlock=0: hold the right button 3 s at full speed: the game aims; did the bike
         slow? Send the "aim: the game aimed ..." line. Put AimBlock=1 back.
  58-23. Third person at speed: hold the right button (or Z) and swing the camera round you: the
         bike keeps its line, A and D still turn it? Let go: the camera back behind in about half
         a second, the bike not turning to where you looked? Four or five times, big swings and
         small. From the first look on, or only later? A sideways slide? Send the "view: the look
         let go in third person ..." lines.
  58-24. Holding the look in third person, open the Pip-Boy or switch to first person: the look
         just ends, no jump? A/Bs: [View] LookThird=0, LookButton=0.
  58-25. Third person, a pistol holstered: nothing in her right hand or on the forearm, the
         holster mod's pistol on the thigh? The hunting rifle's number key: holstered (R draws
         nothing while riding), only on her back, never along the arm or across the tank? Send
         the "gun: holstered: ..." line. A/B: [Tilt] GunHandHide=0.
  58-26. Draw and holster the pistol a few times in third person while riding: after each
         holster the arms on the bars, the legs on the seat? A/B: [Tilt] GunAwayKeep=0.
  58-27. Draw the pistol in first person, switch to third with it out: seated, both hands on the
         bars at once? A jump of the bike about a second later? A/B: [Tilt] GunSeatKeep=0.
  58-28. Cycle the number keys quickly, pistols and the rifle mixed: "Only a handgun" only when the
         rifle ends up equipped? A/B: [Tilt] GunNoteSure=0.
  58-29. Third person, first person with no weapon (your body shows) 5-10 s, third again; five
         times or more, short spells and a long one: the bike and you there at once, and staying?
         A one-frame flicker right after the switch? Send the "third:" and "body: your 3D marked
         changed ..." / "the game took the mark" lines.
  58-30. The same after the Pip-Boy, and after drawing a pistol in first person half a second
         before the switch; then with a pistol out the whole time (always fine in test 57).
  58-31. Right after a switch back to third person, brake hard and switch the headlamp off and
         on: the brake light and the lamp's glow there? If the bike still goes missing, one ride
         each with [View] BodyRedrawHide=0 and BodyRedraw=0 (and BodyWorn=0 if the "third:"
         lines read 0 entries).
  58-32. Any of this build's A/Bs you haven't tried yet, one at a time (CMB_SLOPE.INI's switches
         above). Anything better or worse?
  Send CMB_Slope.log and its _prev logs and Papyrus.0.log of each session, any crash log, the
  screenshots of 58-1 to 58-11 and 58-16, and a short video of 58-13, 58-14, 58-23, 58-25 to 58-27,
  58-29 and 58-30 if you can.

QUESTIONS FOR YOU (docs\TESTING.md has them in full)
  T58-1. Each wear: does it read as its name? Which would you change?
  T58-2. The wear over Gloss black and Free colour? Blood on the dark paints?
  T58-3. The badges clean over the wear, no flicker, no line across a tank badge?
  T58-4. The wear lit like the paint by day and at night? A halo from a distance?
  T58-5. The muddy tyres right?
  T58-6. The front fender badge on the mudguard, the right way round, turning with the bars?
  T58-7. Nuka-Cola and Red Rocket right, from riding distance too?
  T58-8. The Enclave helmet on the flag: the stars, the busyness, the right tank's corner?
  T58-9. The Brotherhood helmet's two cogs?
  T58-10. The plates' top lines centred, clear of the tail lamp?
  T58-11. The five colours on the road and in the lens? Amber too dim? The beam after Apply?
  T58-12. As it came exactly as 2026-11-17a? The frame rate, stock against Wasteland?
  T58-13. The wheel's zoom and the drag anywhere? The lists by the arrow keys: fine?
  T58-14. After E the rear kept, every preview the same? The "the menu's models" line?
  T58-15. The highlight walking: no swing?
  T58-16. The three new views right?
  T58-17. The gears in even steps, each still climbing?
  T58-18. The coast: about twice as far, gradual? Too long, too short? The best CoastDrag?
  T58-19. From 30, a hard brake, the creep at the end: as before?
  T58-20. The right button's look in first person: which line came?
  T58-21. No aim and no slowing with the right button held? The left button firing?
  T58-22. With AimBlock=0: did the aim slow the bike?
  T58-23. The look in third person: back behind with no turn? From the first look on? A slide?
  T58-24. A look ended by the Pip-Boy or first person: no jump?
  T58-25. Nothing in the hand or along the arm while holstered? The "the game's own: bit 0" part?
  T58-26. After a holster in third person: the arms on the bars, the legs on the seat?
  T58-27. A pistol drawn in first person: seated at once in third? A jump of the bike?
  T58-28. Cycling the keys: the message only for the rifle?
  T58-29. The bike and you there in third person after your body, every time? A flicker?
  T58-30. After the Pip-Boy and a draw: the bike there? With a pistol out all along?
  T58-31. The brake light and the lamp's glow after a switch? Which A/B changed what?
  T58-32. Anything a 2026-11-21a A/B made better or worse?

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
