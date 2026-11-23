COMMONWEALTH MOTORBIKE - READY-TO-INSTALL FILES (2026-11-22a, repository commit @COMMIT@)

The Data folder is the whole mod except the rider-pose plugin, which has to be built from
your own load order:

  Data\CommonwealthMotorbike.esp      the plugin: 52 new records in this build (the Paint condition
                                      slot with its six choices, the headlamp in six more colours with
                                      their beams) and 39 changed in place (the look's lists, the new
                                      attach point on the bike, the Wear on three more parts, the
                                      front fender badge retired: its records kept, never drawn);
                                      2026-11-21a's 151 records as before
  Data\Scripts\*.pex                  compiled scripts (Caprica, Fallout 4 format; no Creation Kit
                                      needed), twelve, as before: CMB_HotkeyF4SE,
                                      CMB_GearRestoreF4SE and CMB_LookF4SE (the customised look on
                                      the parked, ridden and first-person bikes and its colours)
                                      need F4SE. Three change in this build: the controller (the
                                      parked bike's look by loading its 3D again, the look's swap at
                                      runtime on the parked and ridden bikes, the parked bike set on
                                      the ground and leaning on its stand, the Paint condition slot),
                                      CMB_LookF4SE (the same look work, the new slot) and
                                      CMB_BikeActivatorScript (it tells the controller each time the
                                      parked bike's 3D loads); in 2026-11-21a the controller,
                                      CMB_LookF4SE and CMB_GearRestoreF4SE
  Data\Scripts\Source\User\*.psc      their sources
  Data\MCM\                           Mod Configuration Menu page and hotkeys: Look has "Paint
                                      condition" after "Paint shade" and no "Front fender badge" in
                                      this build (25 controls still), and "Headlamp" lists eleven
                                      colours; the hotkeys are as before
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
                                      55's fixes (2026-11-16b), test 56's (2026-11-17a), test 57's
                                      (2026-11-21a: the bike after your body, the free look on the
                                      right mouse button and in third person, the field kit's mouse,
                                      holstered weapons, the coast and the gears), and since this
                                      build test 58's: no crash getting on after a change at the
                                      kit, the Wear on the parked and ridden bikes, the game's aim
                                      really blocked, the third-person look as the plugin's own
                                      orbit, the field kit's bike as the menu draws it with the wheel
                                      both ways and on the lists, other mods' attachments following
                                      your body, the gears at their bands in every pull, the speed
                                      kept through a menu, the parked bike on the ground under both
                                      tyres leaning on its side stand (Fallout 4 1.11.240 + F4SE
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
                                      axis, lens and speedometer needle are. Since this build all
                                      five nifs carry five more thin shells, invisible until you
                                      choose (Paint condition's two, the Wear's on the exhaust, the
                                      engine's covers and the fork's lowers), the wear shell rises
                                      over the badges and every overlay shell blends; the parked
                                      bike's side stand is down: the five change in this build;
                                      CMB_BikeParts.ini is 2026-11-10a's, unchanged
  Data\Textures\CMB\Bike\             its textures, 277 DDS. 97 are new in this build (Paint
                                      condition's 30, the Wear on the parts' 63, four coloured lamps)
                                      and 27 change, the same sizes: the badge atlas
                                      (badges_d/_n/_s.dds: the Brotherhood helmet's gears, Nuka-Cola's
                                      script), 18 of the Wear's maps (the grime over the badges) and
                                      the six muddy tyres (the tread's faces clean); the rest are
                                      2026-11-21a's
  Data\Materials\CMB\Bike\            its material files, 608: 84 new in this build (Paint
                                      condition's 20, the Wear on the parts' 42, the five new
                                      shells' own ten, the six new lamps' 12) and 32 changed (the
                                      Wear's 28, the two wear shells' own four), the rest
                                      2026-11-21a's: one per surface for the riding bike,
                                      *_worn.bgsm, and one per surface for the parked bike. The
                                      meshes need them: a missing material file shows the bike
                                      magenta.
  Data\Meshes\Actors\Character\Animations\MT\CMB_Rider\          106 riding clips + CMB_RiderClips.json
                                                                 + CMB_RiderSeat.json
  Data\Meshes\Actors\Character\Animations\MT\CMB_Rider\Female\   106 female clips (CBBE seat height), same files

No optional folder, as 2026-11-14a. If the 2026-11-06a package's "Commonwealth Motorbike - 2026-11-02a look
(A-B)" is still in MO2, keep it unticked (or remove it): it has the old badge and none of the new shapes.

WHAT'S NEW IN 2026-11-22a
  Test 58's fixes and every wish you made (your pick: "Everything"), art build C, in one build, on
  top of 2026-11-21a. What test 58 liked is as it was. Changed since 2026-11-21a: CMB_Slope.dll,
  CMB_Slope.ini, the ESP and the MCM (Paint condition in, the front fender badge out, six headlamp
  colours), three scripts, the five meshes, 27 textures and 32 material files, and 181 new files
  (Paint condition, the Wear on the parts, the coloured lamps); the sounds and the riding clips are
  2026-11-21a's.

  FOUR THINGS TO KNOW FIRST:
  - The front fender badge is gone (your pick: "I would drop front fender badge"): it isn't offered
    at the field kit or in the MCM and is never drawn; a save that had one chosen shows none.
  - At the field kit the mouse wheel scrolls the lists with the cursor over the list panel, as the
    game does, and zooms the bike (in and out now) anywhere else ([Look] KitWheelLists,
    KitWheelDown); holding the left button off the lists still turns the bike.
  - The parked bike leans a little to its left on its own side stand, down now, both tyres on the
    ground wherever you park it; getting on stands it up ([Room] ParkFit, ParkStand).
  - Paint condition (Scratched, Chipped, Sun-faded, Worn, Primer patches) and Wear can be chosen
    together: the paint's damage under, the mud, rust, dust and blood on top.

  WHAT TEST 59 SHOULD TRY (WHAT TO TEST below has the steps, 59-1 to 59-34):
  - step 1 first: test 58's crash, a Headlamp colour at the kit and Ride at once, five times;
  - steps 2-12, the art: Paint condition alone and under the Wear, the Wear on all four bikes (and
    its A/Bs), on the parts and over the badges, the muddy tread, the Brotherhood helmet's gears,
    Nuka-Cola's script, the eleven headlamp colours at night, everything as it came again;
  - steps 13-15, the field kit: the views on screen, a slot's mods, the wheel both ways and on the
    lists;
  - steps 16-21, the parked bike: flat ground, slopes both ways, beside a car or a ledge, rough
    ground, calls, getting on;
  - steps 22-25, the look and the aim: no aim or slowing on the right button, the Pip-Boy while
    you look, the third-person orbit with Z and with the right button;
  - steps 26-29, the gears: from a stop, from a middle speed, up a hill, a menu at speed;
  - steps 30-32, other mods' attachments: your holstered pistol on your thigh, a rifle, a backpack;
  - step 33, the frame rate beside the parked bike; step 34, the A/Bs.

  ART BUILD C (our own drawings and shapes, nothing traced or copied; every new choice opt-in, the
  new slot starting as the bike came):
  - "Paint condition", the paint's own damage under any Wear: Scratched (fine scratches through
    the clear coat, a few to primer and bright steel), Chipped (at the edges, the knee grips and
    low down), Sun-faded (a chalky fade on the tops, the clear coat peeling), Worn (all three),
    Primer patches (grey and red-oxide repairs). Drawn on two thin shells under the Wear's.
  - "all 'wear' option should also be applied on exhaust pipes and other parts": the Wear on the
    exhaust pipes and mufflers (heat colours with Weathered, rust heavy on the mufflers with
    Rusty), the engine's outer covers and the front fork's lowers.
  - "badges on gas tank are not covered when they should e.g. bloody": the grime over the tank
    and rear badges (mud and blood where they land, dust along a plate's top edge, rust from under
    its bottom edge); the 3D helmets stand above it.
  - "wear is not visible outside of field kit menu": the Wear and Paint condition on the parked
    bike (the shells blend in the meshes now) and on the bike under you in third person, a moment
    after the screen comes back ([Look] OverlayRuntime; [Look] OverlayParked=1 is test 59's A/B
    for the parked bike).
  - "tire part where it touches ground is too muddy": the tread's faces clean and black where they
    meet the road, the mud between the blocks and on the shoulders.
  - "bos helmet background should be metallic blue", three interlocking gears: the 3D Brotherhood
    helmet on metallic blue with a fine sparkle, a big black gear behind it and a smaller one
    either side, meshing.
  - "nuka cola badges are ok, just text looks a bit wonky": the script redrawn even, one weight,
    slant and baseline, the swoosh clear between the words (the plate's small cap as before).
  - "larger selection is needed": Halogen, Daylight, Ice blue, Red, Green and Purple, the lens and
    the beam alike (Red and Purple light the road dimly, as coloured lamps do).

  TEST 58'S FIXES AND YOUR WISHES:
  - "game crashed after selecting lamp color": both crashes came at a getting on right after a
    change at the kit, while its new look was still going onto the parked bike. The parked bike's
    look now goes on only by loading its 3D again, never onto the 3D the game is showing while you
    get on ([Look] ParkedSwapHold; [Diag] LensLine logs the lens at each getting on).
  - "with right-click we are aiming a gun and it's slowing bike down": 2026-11-21a's block never
    switched on (the game names its handler otherwise); now the game really doesn't aim while
    riding, and the Pip-Boy should open while you look ([Steer] AimStruct; AimBlock as before).
  - "same with 3rd person (but Z doesn't work)": riding, the game keeps its third-person camera
    behind you, so the plugin swings it round you itself with Z or the right button, as far as you
    move the mouse, and eases it back behind when you let go ([View] LookOrbit, LookOrbitGain).
  - The field kit: "bike doesn't spin to position to show what is being changed": the plugin now
    holds the bike the menu really draws ([Look] KitDrawn); "doesn't zoom out": the wheel's down
    notch is counted ([Look] KitWheelDown); "scroll doesn't work on menu": over the list panel the
    wheel scrolls the lists (your pick: [Look] KitWheelLists); Paint condition has its view and
    the front fender badge none ([Look] KitSlots22).
  - "in 3rd person gun is being holstered to random places, often outside of the body": your
    holster mod copies the pistol in your hand as you put it away, and the copy took the place
    this plugin had given the hand's pistol. Now anything another mod hangs off your body follows
    it exactly while you ride, whatever made it ([Tilt] AttachUnclone, AttachBoneRole; AttachHide
    hides such things instead, a fallback; [Diag] AttachWhere says where each one sits).
  - "overall it feels more sluggish and slower than before": the pulls were as quick as test
    57's, but most began rolling and changed up into 4th at about 32 and 5th at about 43 on the
    dial; every full pull now changes up at about 12, 24, 36 and 46 ([Sound] UpBands), and the
    Pip-Boy at speed no longer cuts the throttle ([Steer] MenuKeep).
  - "having one tire in the ground", "leaning a bit on sidestand/kickstand": every parked bike is
    set on the ground under both its tyres, never rolled onto a car or a ledge beside it, and leans
    on its own side stand, also where the plugin can't fit it ([Room] ParkFit, ParkStand).

  NEXT:
  - The fixes test 59 asks for. Later, from the open ends: seated clips for a drawn pistol, the
    right forearm aimed along the camera with a handgun out, the left hand to the pistol while
    reloading, first person's own pistol, an MCM switch for your body in first person and for the
    look button and the aim's block, the riding bike kept through a rifle's put-away and a handgun
    drawn in first person, your body shown while backing.

  MCM:
    Look: "Paint condition" after "Paint shade", on "Pristine (as it came)"; no "Front fender
    badge" (25 controls); "Headlamp" with eleven colours, Warm first, then alphabetical.

  CMB_SLOPE.INI (every new key at its default in the file, with its comment):
    This build: [Look] ParkedSwapHold=1, OverlayRuntime=1, OverlayParked=0 (an A/B for 59-5),
    KitDrawn=1, KitWheelDown=1, KitWheelLists=1, KitSlots22=1 (with KitViewPaintWear=-45,15);
    [Diag] LensLine=1, AttachWhere=1; [View] LookOrbit=1 (with LookOrbitGain=0); [Tilt]
    AttachUnclone=1, AttachBoneRole=1, AttachHide=0; [Sound] UpBands=215,429,644,823; [Steer]
    AimStruct=1, MenuKeep=1; [Room] ParkFit=1, ParkStand=17.28,2.97,2.61. No default changed; [Look] KitViewFrontFender is out of
    the file (its 0,25 still the code's, used with KitSlots22=0).

  EVERY NEW THING HAS A SWITCH whose off value is 2026-11-21a:
    [Look] ParkedSwapHold=0 (test 58's crash: only if asked), OverlayRuntime=0, KitDrawn=0,
    KitWheelDown=0, KitWheelLists=0, KitSlots22=0; [Diag] LensLine=0, AttachWhere=0; [View]
    LookOrbit=0; [Tilt] AttachUnclone=0, AttachBoneRole=0 (AttachHide and [Look] OverlayParked
    are 0 already); [Sound] UpBands= (empty); [Steer] AimStruct=0 (the aim's handler by its class
    name alone: no block, as 2026-11-21a in the game), MenuKeep=0; [Room] ParkFit=0, ParkStand=
    (empty). Each is read on getting on. The new look choices start as the bike came
    (Paint condition "Pristine (as it came)", the headlamp as you had it). The changed art's switch
    is files: the 2026-11-21a package's five nifs (Data\Meshes\CMB\CMB_BikeParked.nif,
    CMB_BikeWorn.nif, CMB_BikeWornRider.nif, CMB_BikeWornRiderF.nif, CMB_BikeView.nif), its
    Data\Materials\CMB\Bike\static_wear.bgsm, static_wear_worn.bgsm, fork_wear.bgsm,
    fork_wear_worn.bgsm and the 28 wear_<look>_static and _fork materials, and its
    Data\Textures\CMB\Bike\badges_d.dds, badges_n.dds, badges_s.dds, the 18 wear_<look>_static
    maps that changed and the six wheel?_tyre_*mud_d.dds, in an MO2 mod of their own ticked below
    this one, give test 58's meshes, stand, badges, grime and tread back (Paint condition and the
    parts' wear then have nothing to show on; set [Room] ParkFit=0 with the old nifs: their stand
    is folded). The earlier builds' switches are all still there.

  KNOWN, LEFT FOR NOW:
  - The crash: its cause is read from the logs (every crash came a moment after a look was put
    onto a parked bike the game was showing), not seen in the game's code; if the game crashes
    again at a getting on, the log's lens and mount lines say what both bikes carried. With [Look]
    OverlayParked=1 (an A/B) the parked bike carries the plugin's swap between rides and blinks
    once at the press as you get on.
  - The art: the Wear and Paint condition show on the bike under you 2-4 s after the screen comes
    back; on the parked bike they rest on the meshes' blending (59-5 checks it); which of the two see-through layers the game draws
    first is test 59's to see (the grime is meant to hide the paint's damage either way); the
    grime over a badge doesn't know the badge's art (dust along the plate's top edge, rust along
    its bottom edge); every bike draws five more shells, invisible until chosen (about 20,700
    triangles: step 31 asks for the frame rate); the big gear behind the Brotherhood helmet shows
    only round the helmet; Red and Purple are about a quarter as bright on the road as Warm, and
    Daylight is a touch warmer than Warm.
  - The field kit: which bike the menu draws is asked of a game function the plugin hasn't used
    before (the log says if it fails, and the kit works as in test 58 then); the list panel's box
    was measured on a 16:9 screen.
  - The parked bike: on a side slope with the stand downhill it leans the slope plus up to 12
    degrees; on a hump under the stand its foot can sink a little; the stand-up as you get on is
    five quick steps; the kit's preview shows the bike upright with its stand down; with
    ParkStand= or ParkFit=0 the bike stands upright with its stand down, the foot just off the
    ground (test 58's look is ParkFit=0 with the 2026-11-21a parked nif); a park the plugin can't
    fit leans on its stand over the game's own tilt; something on a slope's low side lays the bike
    level across there.
  - The look: that the game keeps its third-person camera where the plugin puts it is test 59's
    to see (if not, the log says "not followed" and the look is 2026-11-21a's for the session).
  - Attachments: a copy another mod makes shows for a frame or two where that mod put it before
    the plugin holds it; AttachHide=2 would hide a hat's loose parts too.
  - The drive: from a long stand the first gear change comes a little under 12 on the dial (the
    game's own first second); up a long hill 4th stays in while the bike still gains.
  - From 2026-11-21a: the bike after your body rests on the game redoing what it draws of you
    when asked (the log says whether it took each ask); a single-frame flicker is possible right
    after the switch; after a draw in first person the bike under you may jump once when the
    script swaps it back; the coast's last second may be a little shorter in the game than worked
    out, and 5-4 comes close under the pull's 4-5; blood on the dark paints reads more by its
    sheen; a coloured lamp's bright centre can look near white or yellow, and Amber's beam is
    dimmer than Warm's; on the right tank the Enclave flag's blue corner is toward the rear; the
    ridden bike's lens takes a new colour at the next getting on (the beam at once).
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
     old mod in MO2 and install this one fresh (over 2026-11-21a).
     By hand without MO2: copy Data over and let everything overwrite. The separate "Commonwealth
     Motorbike - Rider Pose" mod from make_rider_pose.bat stays as it is: no need to rerun it.
  3. If you had edited CMB_Slope.ini: put your values into the new one: [Look], [View], [Steer],
     [Sound], [Tilt], [Room] and [Diag] have new keys, no default changed, and [Look]
     KitViewFrontFender is gone (README.md's key tables list them).
  4. Load your save, and save again before 59-1 (it repeats test 58's crash). The MCM's Look
     section should have 25 controls with "Paint condition" after "Paint shade" and no "Front
     fender badge"; if it shows "Front fender badge", an older ESP or MCM is loaded. Check that
     Riding's "Weapons while riding" says "Handguns only", have the 10mm and the hunting rifle on
     the favourites' number keys, and your holster mod on as in test 58 (a backpack mod too, if you
     have one). The first getting on puts the look on afresh once. Note your frame rate beside the
     parked bike before you install, if you can (59-33). The plugin keeps the logs of the three
     sessions before; say which session each step was in. Then WHAT TO TEST below.
  Updating mid-ride: get off first, save, then update.

WHAT TO TEST, TEST 59 (docs\TESTING.md, "Test 59", has the details and the log lines; the numbers
are its steps: 1 the crash, 2-12 the art, 13-15 the field kit, 16-21 the parked bike, 22-25 the look
and the aim, 26-29 the gears, 30-32 other mods' attachments, 33 the frame rate, 34 the A/Bs)
  For steps 2-12: at the field kit choose each, look at it in the kit, then at the parked bike close
  up (wait 3 s), then from the riding camera (wait 3-4 s), side and behind, and in first person
  where a step says. A screenshot of each, close and riding.
  59-1. Save first. At the field kit pick a Headlamp colour, close the kit and press E on the bike
        at once (Ride); ride a little, get off, again: five times or more, other colours, twice with
        a Wear or a Paint condition changed too. No crash? If it crashes, send the crash log with
        both logs. Please don't try [Look] ParkedSwapHold=0 unless asked.
  59-2. "Paint condition" with Wear "As it came", each in turn: Scratched, Chipped, Sun-faded, Worn,
        Primer patches. Parked from both sides and behind, riding, day and night: does each read as
        its name? Nothing over a badge but the fade?
  59-3. Paint condition and Wear together (Worn + Muddy, Chipped + Rusty, Sun-faded + Dusty,
        Scratched + Bloody, Primer patches + Wasteland): the grime always on top? A flicker between
        the two, looking along the tank low?
  59-4. Wear "Wasteland": the kit's preview, the parked bike after the kit, third person after
        getting on (wait 3-4 s), first person, the parked bike after getting off: on all four? Rusty
        and Bloody too.
  59-5. If the parked bike showed no wear: [Look] OverlayParked=1, then close the kit or get off and
        look again: the wear there now? Then [Look] OverlayRuntime=0: still on the bike under you in
        third person? Put both back (OverlayParked=0, OverlayRuntime=1).
  59-6. Each Wear on the exhaust pipes and mufflers, the engine's side covers and air cleaner, the
        front fork's lowers: noticeable but not too much? Heat colours near the cylinders
        (Weathered), rust on the mufflers (Rusty)? The fork's grime moving with the bars?
  59-7. Dusty, Muddy, Rusty, Bloody with a tank and a rear badge: the grime over the badges now? No
        flicker, no frame round a plate? The 3D helmets standing above it?
  59-8. "Tyres" muddy, each: the tread's faces black and clean where they meet the road, mud between
        the blocks and on the shoulders, the sidewalls as before?
  59-9. Tank L and R "Brotherhood helmet (3D)": metallic blue with a sparkle, three black gears
        meshing (one either side, a big one behind)? The big gear enough? The blue right?
  59-10. Tank L and R and the rear fender "Nuka-Cola": the script even, the swoosh clear?
  59-11. At night (or "set gamehour to 22"), "Headlamp" Halogen, Daylight, Ice blue, Red, Green,
         Purple: the road and the lens in the colour? Red and Purple too dim? Parked, a tinted bulb
         for Ice blue, Red, Green and Purple?
  59-12. Everything as it came (Paint condition, Wear, Tyres, Headlamp): exactly as 2026-11-21a, no
         new flicker? No "Front fender badge" in the kit or the MCM, "Paint condition" there? An old
         save's front fender badge gone?
        The art's A/B for 59-2 to 59-12: the 2026-11-21a package's files (above) in an MO2 mod of
        their own, ticked below this one.
  59-13. Customise, the Motorbike: stop on each slot with the arrow keys: the bike on screen turns
         to its part (rear for the plates, each side for the tanks, the seat from above, the wheels,
         three-quarters for Wear and Paint condition, the front for Headlamp)? Two screenshots. Send
         the "kit: drawn (2026-11-22a): ..." lines. A/B: [Look] KitDrawn=0.
  59-14. Plate text (the rear), E: every mod's preview keeps the rear and your zoom? Tab back; the
         same on Paint and Tank L.
  59-15. The wheel with the cursor off the lists: zoom in and out? Over the list panel: the list
         scrolls, no zoom? The left button beside the lists turns the bike? Send the "kit: hold
         (2026-11-22a): ..." close line. A/Bs: [Look] KitWheelDown=0, KitWheelLists=0, KitSlots22=0.
  59-16. Get off on flat ground: the bike leaning a little to its left on its side stand, the foot
         and both tyres on the ground? If it leans right with the stand in the air, say so.
  59-17. Get off on a slope riding up, riding down, across both ways (stand uphill, downhill): both
         tyres on the ground, the foot touching? Downhill, does it look about to tip?
  59-18. Get off right beside a parked car (on the bike's right, then its left), a ledge or a step a
         hand high, a crate or a barrel, the edge of a drop: the bike on its own ground, leaning on
         its stand, never rolled onto the car's hood or the ledge?
  59-19. Rubble, a kerb, a bump between the wheels; a few calls (keys -> Call); after a swim:
         anything into the ground? Still leaning on the stand where the log says "not fitted"?
  59-20. Get on beside the leaning bike: it stands up as you get on, no jump? Save beside it, load:
         still leaning; the field kit and close it: still leaning?
  59-21. A/Bs: [Room] ParkStand= (upright on its tyres' ground), ParkFit=0 (test 58's parking, the
         stand still down); "set CMB_MaxTilt to 0" (level, still on its stand; put 45 back).
  59-22. A pistol out, full speed, first person: hold the right button a few seconds: no sights, no
         zoom, the dial doesn't drop, the left button fires? Then in third person. Send the "aim:
         AttackBlockHandler ... wrapped" line and the press lines.
  59-23. Holding the right button (and then Z), press Tab: does the Pip-Boy open? Right after
         letting go?
  59-24. Third person at speed: hold Z and move the mouse: the camera swings round you as far as you
         move it (up to about 150 degrees), stays, the bike straight (A and D still steer)? Let go:
         back behind in half a second, no turn of the bike? The same with the right button; with a
         pistol out about 60 degrees. Too fast, too slow, the wrong way? Send the "view: the look
         key (...) held in third person ..." and release lines.
  59-25. A/Bs: [Steer] AimBlock=0 (the game aims again: did the bike slow? the Pip-Boy?),
         AimStruct=0 (2026-11-21a's handler search: test 58's aim back), [View] LookOrbit=0
         (2026-11-21a's look); [View] LookOrbitGain if the swing's speed is wrong.
  59-26. From a stop to the top: the gears at about 12, 24, 36 and 46 on the dial? From about 20, a
         short lift, then forward to the top: still 24, 36 and 46 (test 58: 32 and 43)? Lively as
         test 57?
  59-27. Up a long hill at full throttle: the same dial readings? A steady 20 and 35: as before?
  59-28. At full throttle at about 30, the Pip-Boy a few seconds: the bike carries on at its speed?
         The same in a coast. Send the "steer: a menu paused the game ..." lines.
  59-29. A/Bs: [Sound] UpBands= (test 58's gears), UpBands=215,429,620,800; [Steer] MenuKeep=0.
  59-30. Your holster mod on: draw the 10mm in third person, put it away riding: the holstered
         pistol on your right thigh, staying there through leans and bumps, in first person too? A
         short video. Send the "AttachUnclone" and "an attachment:" lines.
  59-31. Three times more, leaning and straight; the hunting rifle on your back; a backpack if you
         have one: all on your body?
  59-32. A/Bs: [Tilt] AttachUnclone=0 (the pistol back in the air), AttachBoneRole=0; the fallback
         AttachHide=1 (holstered copies hidden while riding) and 2 (a backpack too).
  59-33. 3-4 m from the parked bike, still for 20 s, the frame rate: every slot as it came, then
         Wear Wasteland with Paint condition Worn, same spot (and 2026-11-21a's if you noted it).
  59-34. Any of this build's A/Bs you haven't tried yet, one at a time (CMB_SLOPE.INI's switches
         above). Anything better or worse?
  Send CMB_Slope.log and its _prev logs and Papyrus.0.log of each session, any crash log, the
  screenshots of 59-2 to 59-13 and 59-16 to 59-19, and a short video of 59-15, 59-20, 59-24 and
  59-30 if you can.

QUESTIONS FOR YOU (docs\TESTING.md has them in full)
  T59-1. No crash with a change at the kit and Ride at once?
  T59-2. Each paint condition: does it read as its name? Which would you change?
  T59-3. Paint condition under the Wear: the grime always on top? A flicker?
  T59-4. The Wear on all four bikes?
  T59-5. With OverlayParked=1 the wear on the parked bike where it had none? With OverlayRuntime=0?
  T59-6. The Wear on the exhaust, the engine's covers and the fork's lowers: right amount?
  T59-7. The grime over the badges: right? A frame round a plate?
  T59-8. The muddy tread clean where it meets the road?
  T59-9. The Brotherhood helmet's three gears on metallic blue?
  T59-10. Nuka-Cola's script even now?
  T59-11. The six new colours? Red and Purple too dim?
  T59-12. As it came exactly as 2026-11-21a? The front fender badge gone?
  T59-13. The bike on screen turning to each slot? The "kit: drawn" line?
  T59-14. A slot's mods keeping the view and the zoom?
  T59-15. The wheel both ways off the lists, scrolling them over the panel?
  T59-16. Flat ground: leaning to its left on the stand, all on the ground?
  T59-17. Slopes both ways and across: the tyres on the ground? About to tip downhill?
  T59-18. Beside a car, a ledge, a crate or a drop: never rolled onto them?
  T59-19. Rough ground, calls, a swim: anything into the ground? Leaning where "not fitted"?
  T59-20. Standing up as you get on? Still leaning after a load and the kit?
  T59-21. ParkStand= or ParkFit=0 better than the default?
  T59-22. No aim and no slowing on the right button?
  T59-23. The Pip-Boy while looking?
  T59-24. The third-person orbit with Z and the right button: round you, back with no turn?
  T59-25. With AimBlock=0 did the aim slow the bike? AimStruct=0 test 58's aim? LookOrbit=0?
  T59-26. The gears at about 12, 24, 36 and 46 from a stop and from a middle speed? Lively?
  T59-27. Up a hill and steady: right?
  T59-28. The speed kept after the Pip-Boy and in a coast?
  T59-29. Which UpBands felt best?
  T59-30. The holstered pistol on your thigh, through leans and bumps?
  T59-31. Three holsters, the rifle, a backpack: all on your body?
  T59-32. AttachUnclone=0 back in the air? AttachHide needed at all?
  T59-33. The frame rate, stock against Wasteland with Worn?
  T59-34. Anything a 2026-11-22a A/B made better or worse?

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
