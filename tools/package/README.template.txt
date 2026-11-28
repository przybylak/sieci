COMMONWEALTH MOTORBIKE - READY-TO-INSTALL FILES (2026-11-24a, repository commit @COMMIT@)

The Data folder is the whole mod except the rider-pose plugin, which has to be built from
your own load order:

  Data\CommonwealthMotorbike.esp      the plugin, 2026-11-22a's, unchanged (no record new or
                                      changed in this build; 2026-11-22a's 52 new records, the Paint
                                      condition slot with its six choices and the headlamp in six
                                      more colours with their beams, and 39 changed in place, the
                                      front fender badge retired: its records kept, never drawn)
  Data\Scripts\*.pex                  compiled scripts (Caprica, Fallout 4 format; no Creation Kit
                                      needed), twelve, as before: CMB_HotkeyF4SE,
                                      CMB_GearRestoreF4SE and CMB_LookF4SE (the customised look on
                                      the parked, ridden and first-person bikes and its colours)
                                      need F4SE. Three change against 2026-11-22a, which you have:
                                      the controller (the bike parked beside you when you get off,
                                      its lean from upright, the parked bike hidden as you get on
                                      with no reload first, the look's swap on the bike under you
                                      and on the parked one at every getting on and off),
                                      CMB_LookF4SE (the look's swap reused, no wait for it) and
                                      CMB_BikeActivatorScript (it stands the leaning bike up itself
                                      as you get on); against 2026-11-23a two, the controller and
                                      CMB_LookF4SE (the second review's fixes); against 2026-11-23b two,
                                      the controller and CMB_HotkeyF4SE (this build's)
  Data\Scripts\Source\User\*.psc      their sources
  Data\MCM\                           Mod Configuration Menu page and hotkeys, 2026-11-22a's,
                                      unchanged (since 2026-11-22a Look has "Paint condition" after
                                      "Paint shade" and no "Front fender badge", 25 controls, and
                                      "Headlamp" lists eleven colours)
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
                                      (2026-11-21a), test 58's (2026-11-22a: no crash getting on
                                      after a change at the kit, the game's aim really blocked, the
                                      third-person look as the plugin's own orbit, the field kit's
                                      bike as the menu draws it, other mods' attachments following
                                      your body, the gears at their bands, the parked bike on the
                                      ground leaning on its side stand), and since this build test
                                      59's: the bike parked beside you when you get off, its lean
                                      and tyres, getting on and off quicker, the Wear on every bike
                                      at once, no flash at the kit's options, the third-person look
                                      with a weapon drawn, a pistol held one-handed with your left
                                      hand on the bar, the holster on your thigh, no item clip in
                                      third person, a quicker take-off (Fallout 4 1.11.240 + F4SE
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
                                      axis, lens and speedometer needle are. The five nifs are
                                      2026-11-22a's, unchanged (since 2026-11-22a five more thin
                                      shells, invisible until you choose, and the parked bike's side
                                      stand down); CMB_BikeParts.ini is 2026-11-10a's, unchanged
  Data\Textures\CMB\Bike\             its textures, 277 DDS. 33 changed in 2026-11-23a (none since), the
                                      same sizes: Rusty's and Raider's 30 Wear maps (lighter, see-through
                                      rust, darker at its edges, nothing round the badge plates) and
                                      the badge atlas (badges_d/_n/_s.dds: three gears either side of
                                      the 3D Brotherhood helmet); the rest are 2026-11-22a's
  Data\Materials\CMB\Bike\            its material files, 608, 2026-11-22a's, unchanged: one per
                                      surface for the riding bike, *_worn.bgsm, and one per surface
                                      for the parked bike. The meshes need them: a missing material
                                      file shows the bike magenta.
  Data\Meshes\Actors\Character\Animations\MT\CMB_Rider\          106 riding clips + CMB_RiderClips.json
                                                                 + CMB_RiderSeat.json
  Data\Meshes\Actors\Character\Animations\MT\CMB_Rider\Female\   106 female clips (CBBE seat height), same files

No optional folder, as 2026-11-14a. If the 2026-11-06a package's "Commonwealth Motorbike - 2026-11-02a look
(A-B)" is still in MO2, keep it unticked (or remove it): it has the old badge and none of the new shapes.

WHAT'S NEW IN 2026-11-24a
  Test 60's fixes and your wishes after it, in one build, on top of 2026-11-23b. Changed since
  2026-11-23b, which you have: CMB_Slope.dll, CMB_Slope.ini and two scripts (the controller and
  CMB_HotkeyF4SE); the ESP, the MCM and all the art are 2026-11-23b's. Every new behaviour has a key
  in CMB_Slope.ini whose off value gives 2026-11-23b's back (each key's comment says which).

  GETTING OFF
  - A fast getting off no longer leaves the bike 400-550 behind you: from the moment you ask to get
    off you are held still under the black, and the bike is placed beside where you stopped ([Room]
    ParkStop=0.3; 0 = off). W held through the black no longer walks you on ([Room] ParkHold=0.6).
    A getting off with no black (out of fuel, knocked off, a weapon drawn) stops on screen about
    0.7 s sooner.
  - The parked bike stays solid: it is placed again after it appears (the two bikes you walked
    through in test 60 were the only ones not placed after appearing), checked at its place right
    away and again 2 s later, and put back at most twice if its collision is missing ([Room]
    ParkSolid=1). The room beside you now counts the bike's lean ([Room] ParkLeanClear=1).
  - Where it parks: the side stand's foot is measured on the ground under it, not in a crack
    ([Room] ParkFootFix=1); when the track you rode has no room, nearby spots are tried in turn
    ([Room] ParkFallbackSearch=1); someone standing still in the bike's place for 2 s sends the
    bike to a spot beside or behind you at once, not after 15 s ([Room] GuardStuckMove=2); after a
    swim the bike comes back along your way out of the water, and "Your motorbike rolls up." shows
    only when it is shown ([Room] SwimSpot=1).
  - The first getting on after a load runs this build's way (2026-11-23b ran the previous build's
    until your first getting off).

  STIMPAKS WHILE RIDING
  - Third person: a use clip is never cut before its item comes, so every press heals ([Steer]
    UseItemFirst=1; test 60 had 11 presses and 1 heal). Presses close together wait their turn.
  - Third person: through the clip you stay posed seated, hands on the grips, the clip's props
    hidden ([Tilt] UseSeatHold=1). At speed the bike slows for about a second while the clip plays:
    the game's use animation drives the movement.
  - First person: your arms are hidden while the clip plays, and given back when it is over (4 s at
    most), or at once on a draw, a shot, the Pip-Boy, a camera change or getting off ([View]
    BodyArmsUse=1).
  - The log says, 2 s after each key use, how many are left and your health.

  WEAPONS AND THE LOOK
  - First person: the look with a weapon drawn turns your aim with it, so shots go where the
    crosshair is, not along the bike; the bike keeps its line ([View] LookAim=1).
  - First person: no second left hand on the pistol: the left arm's bones the game gives no name of
    their own are found by their shape and shrunk away with the rest ([View] BodyGunGripNodeless=1,
    BodyGunGripSpeck=shoulder; 0 and joint together give 2026-11-23b's).
  - Third person: the look with a weapon drawn turning the camera round you is new and not yet
    reviewed, so it ships off. To try it set [View] LookOrbitArmed=2 and LookOrbitLearn=1 (step
    61-9), and set both back to 0 if it misbehaves.

  SMALLER FIXES
  - Getting on right after the field kit's menu closes works at once; it was refused for 4-8 s
    ([Look] KitQuickExit=1).
  - Getting on with a customised look is quicker: the worn bike's colours are written after the
    screen is back ([Look] EquipLate=1).
  - A landing's sound plays once ([Sound] LandOnce=1).
  - The log: the near-camera stand-in's lines (40% of test 60's log) come once per showing, and it
    no longer flickers on and off at 60 ([View] NearThirdOff=70, [Diag] NearDrawEvery=1); no "nan"
    in the camera's lines; the water readings at a ride's start fixed; the gun state's names
    corrected; the field kit's bike kept apart from the menu's own update ([Look] KitGuard=1, and
    KitLate's default is now 0); the AP watch off by default, its line no longer calling the
    base value its max ([Diag] APWatch=0).

  KNOWN: with a weapon drawn and the look held in first person, followers catching up with you may
  line up by your aim rather than the bike.

WHAT WAS NEW IN 2026-11-23b
  2026-11-23a plus a second review's four fixes: install this one, not 2026-11-23a (test 60 runs on
  it). 2026-11-23a is test 59's fixes and your wishes after it, in one build, on top of 2026-11-22a;
  what test 59 liked is as it was. Changed since 2026-11-22a, which you have: CMB_Slope.dll,
  CMB_Slope.ini, three scripts and 33 textures (Rusty's and Raider's Wear maps, the badge atlas);
  the ESP, the MCM, the meshes, the material files, the sounds and the riding clips are
  2026-11-22a's. Since 2026-11-23a only CMB_Slope.dll and two scripts change.

  THE SECOND REVIEW'S FIXES (2026-11-23b; no new key, no art change):
  - A stimpak from the Favourites menu right after the Pip-Boy keeps its heal: the plugin now reads
    the Pip-Boy from the game's own open menus, its window is 1.5 s after the Pip-Boy was last open
    (4 s in 2026-11-23a), and any other menu since, the Favourites menu among them, ends it, so that
    clip plays until its item comes and is cut then ([Steer] UseNoClip).
  - Getting on hides a parked bike carrying the look's swap before the fade with any [Look]
    MountGuard and ParkedSwapHold (2026-11-23a skipped it with MountGuard=1 and ParkedSwapHold=0).
  - Two fixes in the look's scripts: while getting off with a confirming swap overdue the look's
    timer runs no oftener than every 0.5 s (it ran every 0.05 s), and with [Look] WornIndex=0 and
    MountQuick=1 a load keeps its own compose.

  FOUR THINGS TO KNOW FIRST:
  - Getting off puts the bike beside you, on your right (on your left when there's no room on your
    right), in view, where you got off; only when neither side has room does it go back along the
    track as before ([Room] ParkBeside, your pick). Look to your side as the screen comes back.
  - The take-off is quicker: 0.3 of the top in about 1.5 s, half in about 2.8 s, the gears still at
    about 12, 24, 36 and 46 on the dial ([Steer] LaunchFrom, [Sound] HeardRiseGears; your pick).
  - A stimpak used while riding in third person, by its number key or from the Pip-Boy, slow or at
    speed, no longer plays a clip: the item works and your hands stay on the bars ([Steer]
    UseNoClip; your pick). Used from the Favourites menu, also right after the Pip-Boy, its clip
    plays until the health comes, then it is cut. First person is as before.
  - With a pistol out your left hand stays on the bar and the right holds the pistol alone: in third
    person it comes off its grip and points the pistol ahead, in first person your own body stays
    shown with its left hand on the grip ([Tilt] GunOneHand, [View] BodyGunGrip; your pick).

  WHAT TEST 60 SHOULD TRY (WHAT TO TEST below has the steps, 60-1 to 60-26):
  - steps 1-7 first, getting off and on: the bike beside you on flat ground, on slopes, by a wall,
    by a car, its lean on the stand, getting on (time the blacks), and their A/Bs;
  - steps 8-9, the take-off from a stand and the gears on the dial;
  - steps 10-14, the art: Rusty and Raider at the badges and riding, the gears beside the helmet,
    the Wear and Paint condition on all four bikes and how quickly they come, and their A/Bs;
  - step 15, the field kit: no flash between options;
  - steps 16-19, a pistol out: the left hand on the bar in third person and in first;
  - steps 20-21, the third-person look with no weapon and with one drawn;
  - steps 22-23, the holster on your thigh while riding and right after a put-away;
  - steps 24-25, a stimpak in third person, by its number key and from the Pip-Boy, slow and fast;
  - step 26, the frame rate.

  THE ART (our own drawings, nothing traced or copied):
  - "rust is too much, should be less intense, more transparent and in darker colors on edges"; "a
    rectangle around the frame": Rusty, and Raider's rust, lighter: fewer, smaller stains, each
    see-through in its middle and darker at its edge, browner, fewer and fainter streaks, nothing
    along a badge plate's outline, the mufflers' rust brown rather than orange.
  - "I was hoping to have 3 gears shown on each side": three meshing black gears on either side of
    the 3D Brotherhood helmet on its metallic blue plate, after your layout (a big one low toward
    the plate's end, a smaller one above it, a smaller one beside the helmet), none behind it.
  - "paint effects are not visible on free standing bike"; "wears are showing correctly in the
    preview, but are not visible on the bike when outside of field kit": the game's own swap never
    draws the Wear or Paint condition, so the plugin's swap now goes on every bike every time: the
    parked bike right after its blink when the kit closes and within a second of getting off, the
    bike under you from the moment the screen comes back and within a split second of a weapon's
    draw ([Look] OverlayParked, on now, OverlayEvery, OverlayQuick).

  TEST 59'S FIXES AND YOUR WISHES:
  - "when getting off I'm sometimes put far away from where I got off": the plugin parked the bike a
    bike length and a half back along your track, behind the camera. Now it parks it beside you, in
    one ask of the plugin where there were four ([Room] ParkBeside).
  - "it leans, but not always; sometimes one tyre is partially in the ground": its lean on the stand
    is held between 5 and 20 degrees from upright, so it still rests on its stand on a slope rising
    toward it and no longer lies 31 degrees over after a swim; a tyre that met a wrecked car's body
    is set on the ground under it, and each wheel rests on the highest point under its edge ([Room]
    ParkLean, ParkTyres).
  - "getting on and off wait time is longer than normal": getting off makes one ask, and getting on
    no longer loads the parked bike again before the fade: it vanishes as you press E when it
    carries the plugin's look swap (most times now), otherwise 0.2 s into the fade, before the bike
    you ride goes on; a getting on that fails puts it back where it stood ([Room] MountHide).
  - "between every option bike gets into default position for a moment": the plugin now also turns
    the menu's new bike right after the menu's own update, before the frame is drawn, and the bikes
    it has loaded but not shown yet ([Look] KitLate, KitPrePlace).
  - "right-click/Z for free camera doesn't work when gun is out in 3rd person camera": with no
    weapon drawn the game's own free camera swings round you, with one the plugin swings it (up to
    about 60 degrees), and no hiccup switches the look off for the session any more ([View]
    LookOrbitGame, LookRecover).
  - "she still holds the gun with both hands": your left hand stays on the left grip and the right
    holds the pistol alone, in third person and in first ([Tilt] GunOneHand, GunHoldAt; [View]
    BodyGunGrip).
  - "guns are still showing up in random places": your holster mod's copies on the thigh are found
    as hanging off the thigh itself, so they follow your thigh, also in the moment right after a
    put-away ([Tilt] AttachSkeleton; [Diag] AttachFresh for the log's measures).
  - "it would make more sense to not have any healing animation in 3rd person": no item-use clip
    while riding in third person after a number key or the Pip-Boy, the item still used, your hands
    on the bars; any other use's clip plays until its item comes and is cut then, so the heal is
    never lost ([Steer] UseNoClip).
  - "still feels a bit sluggish on take-off": the take-off quicker, the gears where they were
    ([Steer] LaunchFrom 0.25, [Sound] HeardRiseGears 2.1,1.35,1,1,1).

  NEXT:
  - The fixes test 60 asks for. Later, from the open ends: seated clips for a drawn pistol, the left
    hand to the pistol while reloading, an MCM switch for your body in first person and for the look
    button and the aim's block, the riding bike kept through a rifle's put-away and a handgun drawn
    in first person, your body shown while backing.

  MCM:
    2026-11-22a's, unchanged (25 Look controls).

  CMB_SLOPE.INI (every new key at its default in the file, with its comment):
    This build: [Room] ParkBeside=65, ParkLean=5,20, ParkTyres=1, MountHide=1; [Look]
    OverlayEvery=1, OverlayQuick=1, KitLate=1, KitPrePlace=1; [View] LookOrbitGame=1, LookRecover=1,
    BodyGunGrip=1; [Tilt] GunOneHand=1, GunHoldAt=-3,-2,9, AttachSkeleton=1; [Diag] AttachFresh=1;
    [Steer] UseNoClip=1. Three defaults change: [Look] OverlayParked=1 (0 in 2026-11-22a: test 59's
    A/B), [Steer] LaunchFrom=0.25 (0.14) and [Sound] HeardRiseGears=2.1,1.35,1,1,1 (2,0.86,0.8,1,1).

  EVERY NEW THING HAS A SWITCH whose off value is 2026-11-22a:
    [Room] ParkBeside=0 (the spot back along the track), ParkLean= (empty), ParkTyres=0,
    MountHide=0; [Look] OverlayEvery=0, OverlayQuick=0, OverlayParked=0, KitLate=0, KitPrePlace=0;
    [View] LookOrbitGame=0, LookRecover=0, BodyGunGrip=0; [Tilt] GunOneHand=0 (then GunHoldAt does
    nothing), AttachSkeleton=0; [Diag] AttachFresh=0; [Steer] UseNoClip=0; and the take-off, which
    has no key of its own: set [Steer] LaunchFrom=0.14 and [Sound] HeardRiseGears=2,0.86,0.8,1,1 by
    hand, both together. Each is read on getting on. The changed art's switch is files: the
    2026-11-22a package's Data\Textures\CMB\Bike\badges_d.dds, badges_n.dds, badges_s.dds and the 30
    wear_rusty_* and wear_raider_* maps, in an MO2 mod of their own ticked below this one, give test
    59's rust and the helmet's old gears back. The earlier builds' switches are all still there.

  KNOWN, LEFT FOR NOW:
  - Getting off: the spot is your right first (the stand side towards you); in first person it is
    beside you, not in front; with no room either side the bike still goes back along the track,
    behind the camera. How much shorter the blacks are is test 60's to measure.
  - The lean: held at 5 on ground rising toward the stand the foot goes a few units into the rise,
    and held at 20 on a steep fall it hangs a few units over it; a real step higher than about a
    hand under one wheel is taken as a thing and looked under.
  - The Wear: the parked bike still blinks once a couple of seconds after the kit closes (the wear
    lands with it); the bike under you can be clean for a frame or two before its swap.
  - The field kit: the flash fix rests on the order test 59's log shows; if the menu puts its new
    bike in later still, the log's close line says so.
  - The look: with no weapon the camera is the game's while you hold the key, so if the game brings
    it back with the mouse still, it comes back.
  - A pistol: which way a pistol's barrel points in its model is taken as the game's forward (the
    log gives the angle and how upright the gun is held); the hold's place is a first set ([Tilt]
    GunHoldAt); in first person the game's right arm meets your body at the right shoulder, and a
    reload's left-hand clip plays with the game's left arm shrunk away.
  - The holster: what lay along your right forearm in test 59's picture may be another mod's arm
    gear rather than the holster (60-22 asks).
  - Items in third person: an item used another way than its number key or the Pip-Boy (the
    Favourites menu, another mod) shows its clip, your hands off the bars, until the item comes,
    then it is cut, so the heal is never lost (2026-11-23a's early cut of a Favourites use right
    after the Pip-Boy is fixed in 2026-11-23b).
  - Getting on: with the look's swap on it the parked bike vanishes as you press E, just before the
    screen goes black ([Room] MountHide=0 is test 59's reload: a blink, then the fade).
  - The art: Rusty is light at riding distance in our renders (if it is too faint, two numbers of
    its tool make it stronger); the gears either side of the helmet are smaller than 22a's flank
    gears, the right group the left's mirror image.
  - From 2026-11-22a: the crash's cause is read from the logs, not seen in the game's code (test 59
    had none); which of two see-through layers the game draws first; the grime over a badge doesn't
    know the badge's art; every bike draws five more shells, invisible until chosen; Red and Purple
    are about a quarter as bright on the road as Warm; which bike the field kit's menu draws is
    asked of a game function (the log says if it fails); the list panel's box was measured on a 16:9
    screen; the stand-up as you get on is five quick steps; a copy another mod makes shows for a
    frame or two where that mod put it before the plugin holds it; from a long stand the first gear
    change comes a little under 12 on the dial.
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
     old mod in MO2 and install this one fresh (over 2026-11-23b). By hand without
     MO2: copy Data over and let everything overwrite. The separate "Commonwealth Motorbike - Rider
     Pose" mod from make_rider_pose.bat stays as it is: no need to rerun it.
  3. If you had edited CMB_Slope.ini: put your values into the new one: [Look], [View], [Steer],
     [Tilt], [Room], [Sound] and [Diag] have new keys, and two defaults change ([Look] KitLate 0,
     [Diag] APWatch 0; README.md's key tables list them).
  4. Load your save: the ESP and the MCM are 2026-11-22a's, so nothing is put on afresh. Have the
     10mm and a stimpak on the favourites' number keys, as in test 60. For 61-1 and 61-5 a video is
     the best measure. The plugin keeps the logs of the three sessions before; say which session
     each step was in. Then WHAT TO TEST below.
  Updating mid-ride: get off first, save, then update.

WHAT TO TEST, TEST 61 (docs\TESTING.md, "Test 61", has the log lines for each step: 1-4 getting off
and where the bike parks, 5-6 stimpaks, 7-8 a pistol in first person, 9 the third-person look with a
weapon (optional), 10-12 the smaller fixes)
  61-1. Getting off fast: at full speed on open ground, get off, five times. Is the bike right
        beside you after the black every time (test 60: 400-550 behind)? Once, keep W held through
        the black: do you stay where you are?
  61-2. The parked bike solid: after each getting off, walk into the bike before pressing E. Do you
        ever pass through it? Then a quick series: get off, get on, get off, five times in a row.
  61-3. A getting off with no black: run the tank dry, or get knocked off, or draw a weapon at speed.
        Does the bike stop and park beside you as before?
  61-4. Where it parks: get off by wrecked cars or rubble, on Sanctuary's slabs, and with a wall
        behind you. Is the stand's foot on the ground (not in the air), the bike on a spot with
        room? Then swim and come out: does the bike come back by your way out, and does "Your
        motorbike rolls up." show only when you can see it?
  61-5. A stimpak in third person at speed: press its key three times about half a second apart. Does
        each press heal (the HP bar)? Do you stay seated with your hands on the grips, no syringe
        shown? The bike slowing for about a second is expected. A video helps here.
  61-6. A stimpak in first person: by its key, then from the Pip-Boy, then from the Favourites menu.
        Are your arms hidden while it plays and back after it, and did each heal?
  61-7. The 10mm in first person: draw it. Is the second left hand on the pistol gone? Take a hit
        while it is out, then put it away.
  61-8. The look with the pistol out in first person: hold the look key, look 45-60 degrees to one
        side and shoot at something. Do the shots go to the crosshair? Does the bike keep its line?
  61-9. Optional, the third-person look with a weapon: in CMB_Slope.ini set [View] LookOrbitArmed=2
        and LookOrbitLearn=1. In third person with a weapon drawn, hold the look key and move the
        mouse. Does the camera turn round you (up to 60 degrees) and ease back when you let go? Try
        it near a wall. Set both back to 0 afterwards, or at once if anything misbehaves.
  61-10. The field kit: close its menu and press E on the bike straight away. Do you get on at once?
        With a customised look, about how long does getting on take now (test 60: about 5.5 s)?
  61-11. Jump off something and land: one landing sound, or two?
  61-12. After the session: how big is CMB_Slope.log (test 60's was 14.6 MB)?

QUESTIONS FOR YOU (docs\TESTING.md has them in full)
  Q61-1. Did the bike ever appear behind you, or did you walk through it, at any getting off?
  Q61-2. Did every stimpak press heal? How did the seated pose look through it?
  Q61-3. With the look in first person, did the shots go where you aimed?
  Q61-4. If you tried 61-9: did the camera turn round you, and did anything look wrong?

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
