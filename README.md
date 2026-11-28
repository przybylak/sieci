# Commonwealth Motorbike (Fallout 4 mod, work in progress)

A rideable motorbike for Fallout 4:

- **faster than on foot**: 250% of your speed by default, adjustable from the console
- **companions come along**: they run alongside at the same speed (or, opt-in, ride along hidden)
- **runs on Flamer Fuel**: one unit per 300 m ridden, taken from the side bag first, so it isn't a free speed boost in Survival
- **side bag**: small storage, size adjustable from the console
- **park it, call it, ride it**: activate the bike or use its keys (favorite them to a hotkey); optional F4SE hotkey; since the 2026-11-09a build getting on takes about 1.5 s with the look unchanged (test 51: 5-6 s), and a second press while the bike's menu is coming is ignored (test 51's black screen after Ride); since the 2026-11-10a build (test 52: 3-5 s, the screen black for 3.0-3.6 s of it) the worn bike goes on right after the screen fades and the screen comes back as soon as the bike is held and coloured and you are seated, the rest of getting on after it: about 1.1-1.3 s of black with the stock look and 1.6-2.1 s with a full look, by the estimate (the log's stage-times line shows the real split); since the 2026-11-15a build (test 54: about 0.85 s slower in 2026-11-14a, the screen back 3.4 s after the press) an unchanged look's colour pass and parts check are skipped, so getting on is about as quick as in 2026-11-10a again (`[Look] MountQuick`); since the 2026-11-22a build getting on right after a change at the field kit no longer crashes the game (test 58: twice, a Headlamp colour picked and Ride pressed at once): the kit's new look no longer goes onto the parked bike while the game is showing it as you get on (`[Look] ParkedSwapHold`); since the 2026-11-23a build (test 59: "when getting off I'm sometimes put far away from where I got off": the bike went a bike length and a half back along your track, behind the camera; your pick) getting off parks the bike beside you, on your right (on your left when there's no room on your right), in view, where you got off, the spot back along the track only when neither side has room, with one ask of the plugin where there were four (`[Room] ParkBeside`), and getting on no longer loads the parked bike again first: it vanishes as you get on, before the bike you ride goes on (as you press E when it carries the plugin's look swap, 0.2 s into the fade otherwise; test 59: "getting on and off wait time is longer than normal"; `[Room] MountHide`)
- **seated riding animations** with lean in turns and ridden U-turns; the bike turns with you on the spot and in conversations; since the 2026-11-01a build hits don't stagger you while riding (MCM "Steady in the saddle", so the bike no longer hangs round your hips through a stagger), and with F4SE the plugin checks that the seated clips are playing and the script puts them back if they aren't (test 47's rider "floating" after a fight was the plugin running out of copies of her bone data, held by the blood decals: fixed); since the 2026-11-02a build "Steady in the saddle" is a perk of its own with the two condition tabs the game's own stagger lining has (test 48: eight staggers got through the first one; the console's `CMB_RiderSteadyWay` tries the game's own perk too), the pose is left alone for 6 s after an item's use so an animation mod's use clip plays whole, the camera's with it (test 48's camera stuck after a stimpak), and with F4SE the hands let go of the grips while that clip plays (test 48's arm stretched while eating) and the pose isn't measured in first person, where the game's third-person skeleton stands; since the 2026-11-06a build using an item while riding fast (a stimpak by its hotkey, food from the Pip-Boy) no longer slows the bike: above 150 units a second the item animation mod's clip isn't played (the item is used as always), stopped or slow it plays, and the arm no longer stretches when eating right after the Pip-Boy (test 49); items another mod equips on you (a reload fixer's dummy potion) no longer start the item watch; since the 2026-11-09a build an item's use clip that still starts at speed (test 50: the item animation mod's own idle never passes that refusal) is stopped as it starts, the plugin telling the animation graph `IdleStop`, then `IdleForceDefaultState` (`[Steer] UseStop`), so the bike should keep its speed; since the 2026-11-10a build (test 52: by the hotkey the clip was cut before the item was used) a potion on a favourites hotkey used at 150 units a second or faster is used at once, without the game's use animation, the way the Pip-Boy uses it (`[Steer] QuickUse`), and the use-clip stop acts only on an item's props, never on a drawn weapon; since the 2026-11-14a build (test 53: by its number key the plugin never saw the key, the game giving its own key codes) a number key is found by the game's own name and code, and when the plugin can't take one the item's clip is cut and the script uses the item, or the clip plays until the item is used, so a stimpak by its number key always heals at speed (`[Steer] QuickKeyCodes`, `QuickCut`, `UseStopUnapplied`); since the 2026-11-23a build (your pick after test 59: "it would make more sense to not have any healing animation in 3rd person unless you can fix it") a stimpak used while riding in third person, by its number key or from the Pip-Boy, slow or at speed, plays no clip: the item works and your hands stay on the bars; used another way (the Favourites menu) its clip plays until the item comes and is cut then, so the heal is never lost (`[Steer] UseNoClip`; first person as before)
- **a handgun from the saddle** (since the 2026-11-15b build, test 53's wish; MCM "Weapons while riding"): by default only a handgun can be drawn and fired while riding, in third person seated with the left hand on the bar and the right arm the game's own (aim, fire, reload), the bike staying under you (with F4SE and `CMB_Slope.dll`); anything else you draw is put away, VATS stays off, and getting on with a weapon out puts it away first. "None" keeps every weapon away (a weapon out ends the ride) and "Any weapon (standing poses)" allows every weapon and VATS in the game's standing poses, as the old "Allow combat while riding" off and on; since the 2026-11-16b build (test 55: the right arm swinging out of the seated body, the put-away never calling the game) both hands stay on the bars with the pistol carried into the right hand on its grip (no aiming pose yet), drawn right after getting on too, and anything else drawn is put away by the game's own call at once, a save right after it no longer ending the ride; since the 2026-11-17a build (test 56: the weapon rules switched off for the session by the Pip-Boy right after a put-away, and "it shouldn't even be pulled out") a menu no longer switches the rules off (they come back once the game and the script agree again), a rifle is never drawn while riding: it becomes your weapon but stays holstered, "Only a handgun can be used on the motorbike." still showing, a rifle's number key with a pistol out puts the pistol away first, and a quick swap between two handguns is no longer taken for "not a handgun" (`[Tilt] GunCheckUnpaused`, `GunCheckRecover`, `DrawHandgunOnly`, `QuickHolsterFirst`, `GunJudgeWait`); since the 2026-11-21a build (test 57: "pistols were just flying around when holstered, hunting rifle was placed in strange spots", the legs "spasming" or "running with a gun" in third person) the game's copy of a holstered weapon in your right hand is hidden, so nothing hangs on your forearm (a holster mod's copy still shows), putting a pistol away in third person keeps you seated until the riding animation is back, a pistol drawn in first person is seated at once back in third person, the "Only a handgun" message names only the weapon you hold, and the game no longer aims while riding (your decision after test 57: aiming slows you on foot, and would the bike; the right mouse button is the free look); with "Handguns only" a rifle still can't be drawn while riding at all: its number key equips it holstered and R draws nothing until you get off (`[Tilt] GunHandHide`, `GunAwayKeep`, `GunSeatKeep`, `GunNoteSure`, `[Steer] AimBlock`); since the 2026-11-22a build (test 58: "with right-click we are aiming a gun and it's slowing bike down": 2026-11-21a's block never switched on, the game naming its handler otherwise) the game really doesn't aim while riding (`[Steer] AimStruct`), and whatever another mod hangs off your body, a visible-holster mod's pistol on your thigh, a backpack, follows your body while you ride (test 58: "gun is being holstered to random places, often outside of the body of character"; your rule: the mod has to work whatever else is installed: `[Tilt] AttachUnclone`, `AttachBoneRole`; `AttachHide` hides them instead, a fallback); since the 2026-11-23a build (test 59: "the character isn't aiming, but she still holds the gun with both hands"; your pick) with a pistol drawn your left hand stays on the left grip and your right hand holds the pistol alone: in third person it comes off its grip and points the pistol ahead over the bars, in first person your own body stays shown, its left hand on the grip, and only the game's right arm holds the pistol (`[Tilt] GunOneHand`, `GunHoldAt`, `[View] BodyGunGrip`); and a holster mod's pistol on your thigh is found as hanging off the thigh itself, so it follows your thigh also in the moment right after a put-away (test 59: "guns are still showing up in random places"; `[Tilt] AttachSkeleton`)
- **an engine sound from a real V-twin** (demodave's recording, CC0): with F4SE (since test 44's build) the plugin runs a model of a four-speed gearbox and pitches and fades eleven loops every frame with your speed and throttle, shifting up as you pull away and falling off as you let go; since test 45's build the engine keeps a real ride's pace rather than the game's quick bike, so a pull-away climbs from the moment you press forward, each one shifting a little differently, the cruise holds steady and a roll-off falls slowly in gear; since test 46's build each loop's level is set at once rather than faded, so a gear change no longer cuts out, and the engine is louder and punchier, with hotter recordings, more between the cruise and a full-throttle pull and its full volume out past the riding camera (test 45's build needed the MCM's engine volume at 100); since test 47's a steady cruise wanders in pitch and level like a hand on a real throttle (since the 2026-10-31a build more, in slow swings of a second or two that peak 3 to 5% off the cruise's rpm, never past about 6%, and about 1 to 1.5 dB in level), each up-shift dips briefly as the throttle closes, the engine reverberates as the game's other sounds do, and the MCM's engine volume starts at 90 in a new save; since the 2026-11-01a build 1st and 2nd change up later, at about 2,600 rpm, and a stop changes down so you hear it (three blipped down-shifts rolling to a stop, two braking, then the clutch); since the 2026-11-02a build the idle is louder, 2.5 dB under the cruise where it was 8.7 under (test 48: "it feels like there is no sound"), so a stop no longer goes quiet and the start and stop sounds run into and out of it without a step; since the 2026-11-06a build the idle is a little louder (level with the cruise), each take-off starts with a short rev, and each gear change is longer (about half a second of the darker sound and the dip; `IdleDb`, `LaunchFlare`, `ShiftTime` and `ShiftDipTime` in `CMB_Slope.ini`); since the 2026-11-09a build each gear lasts longer than the last at full throttle from a stop, 1st about 1.6 s, 2nd 2.0 and 3rd 2.5 (test 50: 3rd was pinned at 1.25 s, shorter than 2nd; test 51: 1st lasted about 3.5 s: `[Sound] HeardRiseGears`, `ShiftGapGears`); since the 2026-11-10a build 3rd lasts about 3 s (test 52's wish) and the Pip-Boy (or any menu that pauses the game) at speed holds the engine's note instead of dropping it to 1st and climbing back after the close (`[Sound] MenuHold`); since the 2026-11-14a build (test 53: "a bit flat") five gears shift higher, at about 3200-3400 rpm at full throttle, the cruise as before, the note never falls while the bike gains nor drops to 1st on a throttle lift (`HeardKeep`, `LiftDown`), and the engine and the water go quiet while a menu pauses the game (`MenuQuiet`); since the 2026-11-15a build (test 54: the top speed came in 2nd, 3rd to 5th at the same speed) the bike itself pulls more slowly above 0.6 of its top, so its speed climbs with the gears and reaches the top about when 3rd ends, the gears' sound untouched (`[Steer] PullTime`); since the 2026-11-16b build (test 55: "1st gear shoots bike up to 30 almost instantly") the bike gains speed evenly from the press, 1st ending at about 10-12 on the dial and the top coming about when 5th does, about 8 s after the press, the five gears sounding as before at the speeds that now match them (`[Steer] PullTime`, `PullFrom`, `LaunchFrom`, `[Sound] SpeedMap`); since the 2026-11-17a build (test 56: "takeoff is a tad too slow", "shifting down when being slowed down or stopping is sometimes weird") the take-off is a tad quicker, 2nd at about 12 on the dial, and coasting to a stop the engine shifts down one gear at a time near the speeds it shifted up at, each with one blip, a hard brake dropping to idle after a shift or two (`[Steer] LaunchFrom`, `[Sound] DownBands`, `HeardStop`, `HeardBrake`); since the 2026-11-21a build (test 57: "4th gear - 50-50? shortest currently", "when letting go at top speed rolling distance should be twice as much as is now, with gradual slow down") the gears change up in even steps, at about 12, 24, 36 and 46 on the dial (your pick), and letting go at speed the bike rolls about twice as far, slowing hardest at first and more and more gently, the engine shifting down one gear at a time over the roll (`[Steer] CoastDrag`, `[Sound] HeardRiseGears`, `ShiftGapGears`, `DownBands`); since the 2026-11-22a build (test 58: "overall it feels more sluggish and slower than before": pulls begun rolling changed up into 4th at about 32 and 5th at about 43 on the dial) every full pull changes up at about 12, 24, 36 and 46 on the dial, from a stop, from a middle speed or up a hill, and a menu that pauses the game at speed (the Pip-Boy) no longer cuts the throttle (`[Sound] UpBands`, `[Steer] MenuKeep`); since the 2026-11-23a build (test 59: "still feels a bit sluggish on take-off") the take-off is quicker, 0.3 of the top in about 1.5 s and half in about 2.8 (your pick), the gears still at about 12, 24, 36 and 46 on the dial, 1st to 3rd revving out before each change (`[Steer] LaunchFrom`, `[Sound] HeardRiseGears`); without F4SE, an idle and a cruise loop crossfaded by speed
- **a V-twin cruiser** as the bike (Nieve5677's Sketchfab model, CC-BY: see the credits), on the vanilla motorcycle's collision; with F4SE its wheels spin with the distance ridden (since the 2026-11-09a build by each frame's own movement, so they stop with the bike, and they hold still while you brake: test 50's wish) and the bars turn with you (the hands go with them, since the 2026-10-31a build the lower triple clamp too, and since the 2026-11-15b build the two cables and the wire on the right of the bars, which floated in the air in a turn: test 53); the vanilla bike can be built instead
- **its look** (since the 2026-10-31a build): textured all over, with procedural textures baked from the 1.3-million-triangle model onto the game's mesh (the download has no textures): an oxblood tank and fenders with a clear coat and a cream double coachline, our own winged-wheel badge, dark mirror-like chrome, a black wrinkle-finish engine with bright fin edges, a leather-grained seat, tyres with their tread; a material file for every surface (the hook for paint and parts at a workbench later); with F4SE **a working speedometer** (its needle follows your speed, about 50 on the dial at full speed by default, and its numerals light up with the headlamp), **a tail light** lit while you ride that brightens with both rear signals when you brake, and **mirrors** that show a sky (Fallout 4 can't show real reflections), in the stock style or either of two styles hung under the bar ends (`[Look] Mirrors` in `CMB_Slope.ini`; since the 2026-11-07a build the ones you fit at the bike, which the parked bike shows too). Every new behaviour of the plugin has a key in `CMB_Slope.ini` whose off value gives the previous build's back; the textures and the lower triple clamp turning with the bars come with the meshes (the previous build's meshes copied back give its look). Since the 2026-11-01a build the tank's cream line is one smooth curve with round corners, the seat's piping is re-cut, the brake discs are our own drilled ones and the mirror glass is brighter; with F4SE the tail lamp lights the road behind a soft red, three times brighter while you brake (MCM "Tail lamp lights the road"), and **the bike is under you in first person** (MCM "Bike in first person"; no hands on the grips: the game shows no arms with the weapon away). Since the 2026-11-02a build the chrome is polished (its material files reflect six times as much, with sharper glints and screen-space reflections: test 48's "too dull"), the mirrors show the game's own mirror cube (test 48's pick of the two), the front brake disc has no light ring round its bore, and with F4SE the bike in first person stays under your eye at every speed (test 48: it slid back by 58 ms of the speed, so at full speed you sat over its rear wheel; `[View] Eye`). Since the 2026-11-06a build the chrome is toned down, still bright but not pearly or smeared (its material files reflect 2.5 times the cube where the 2026-11-02a build's did 6, with less specular and no screen-space reflections: test 49), the rims and discs are a little greyer, and with F4SE going into first person eases the view about 20 degrees down so the dial and the bars are in sight (MCM "Look down on getting into first person (deg)"; test 49's bike out of view looking level), with a riding field of view (off by default) and your eye's place on the bike in the MCM too; the optional MO2 folder "2026-11-02a look (A-B)" gives the 2026-11-02a build's look back. Since the 2026-11-09a build (test 50) opening the Pip-Boy from third person no longer tips the view, a little look of your own while the view eases down adds to it (past 5 degrees you take over), the ease starts a quarter of a second into first person, the view bike's place in the game's scene is made to hold it (test 50 never saw it; the plugin now logs how it is drawn) and the riding field of view looks for the game's own field more widely, from half a second into first person; and (test 51) a tip its own check turns off within 2 s of a load or of getting on is off for that entry only, not for the session; since the 2026-11-10a build the front wheel, the fork and the bars cast their shadow in the sun while you ride, as the parked bike's always did (test 52's wish), and in first person (test 52: the bike still never seen) the plugin moves the first-person bike under your own cell's node while it shows and runs the game's own update on it (`[View] Parent`, `Update`), logs four more `view: drawn?` lines to settle why it isn't seen, tries the camera's own two fields for the riding field of view (`FovSearch=2`), and lets a mouse move of up to 15 degrees add to the tip (`TipYield=15`); since the 2026-11-14a build (test 53: the bike seen at last, but shaking, and you sat over the tank) the first-person bike is held so your eye stays put on it as it tilts, following the game's own camera each frame (`[View] EyeLock`, `Camera`), your eye 11 units further back, over the seat, and the riding field of view is gone (the game wrote its own back); since the 2026-11-15a build (test 54: still shaking, the camera check having switched itself off on its first frame, and the stock red tank for a moment) the game's camera place is read as the world place it is and the bike's lead uses the game's own frame (`[View] CameraWorld`, `LeadFrame`), the first-person bike stays hidden until its colours are on (`LookWait`), and your eye sits where test 54 put it, 6 back and 3 lower (`EyeAt`; set the MCM's two eye sliders back to 0); since the 2026-11-15b build (test 53's and 54's wishes) A and D turn the bike in first person as the mouse does (they used to step sideways: `[Steer] FirstKeys`), the view leans into turns with the bike (MCM "View leans in turns (first person, deg)", 4), backing up turns the view over your shoulder, or into third person while you back (MCM "Looking back while reversing (first person)"; not with a weapon drawn), holding Z lets you look round while the bike keeps its line (MCM "Look key (scan code)"), and your own body, the arms on the grips, the chest and legs in your outfit, is drawn on the bike in first person in the pose you ride in in third person (`[View] Body`; whether the game draws it is test 55's question); since the 2026-11-16b build (test 55: the shake back, a moment with no bike when zooming in, a second set of bars and a gun on the grip with your body shown) the first-person camera's place is read the way the game makes it (`[View] CameraPlace`), zooming in with the wheel shows the first-person bike in the riding one's place (`NearThird`), it moves between the cells' nodes only near a cell's edge (`ParentKeep`), the view leans by how fast you turn (`RollTurn`) and tilts with the mouse while you look back (`LookPitch`), A and D turn at 0.45 of the limit (your pick), and with your body shown the worn bike, the holstered gun and the outfit pieces near your eye are hidden, the game's first-person arms too while you look back, and your eye sits where the game's own is (`BodyWorn`, `BodyWeapon`, `BodyNear`, `BodyArmsBack`, `BodyEye`), the body following the camera's own place with the bike (`BodyFollowCamera`); since the 2026-11-17a build (test 56: the shake fix turned itself off at once, the bike gone in third person after your body had shown, the inside of your outfit when looking down, a second arm with the look key) the first-person camera's place is found as your game eases it, so the bike and your body follow it (`[View] CameraEase`), zoomed in to your head the bike stays while the plugin swaps its first-person bike (`NearHandover`), the bike is drawn again in third person the moment your body stops showing (`BodyNodes`), your eye sits at your face in front of the neck (`BodyEye`, `BodyLeanMax`), and the game's own first-person arms are hidden while you look aside with the look key (`BodyArmsLook`); since the 2026-11-21a build (test 57: the bike, and sometimes you, still gone in third person after your body had shown, "Z in 3rd person doesn't work", the free look wished on the right mouse button) once your body stops showing the plugin asks the game to redo what it draws of you, so the bike is under you again in third person (`[View] BodyRedraw`, `BodyRedrawHide`), and the free look is on the right mouse button too (Z still works) and works in third person, the camera swinging round you while the bike keeps its line and easing back behind when you let go (`[View] LookButton`, `LookThird`); since the 2026-11-22a build (test 58: "same with 3rd person (but Z doesn't work)": riding, the game keeps its own third-person camera behind you) the plugin swings that camera round you itself, as far as you move the mouse (up to about 150 degrees, 60 with a weapon out), and eases it back behind when you let go (`[View] LookOrbit`); since the 2026-11-23a build (test 59: "right-click/Z for free camera doesn't work when gun is out in 3rd person camera") it works with a weapon drawn too: with none the game's own free camera swings round you, with one the plugin swings it, and no hiccup switches the look off for the rest of the session (`[View] LookOrbitGame`, `LookRecover`)
- **customising at the bike** (since the 2026-11-07a build): the parked bike's menu has a Customise button; a field kit comes out of the side bag beside the bike and you change the badges on both sides of the tank and on the rear fender (13 emblems of our own, from the Brotherhood of Steel to a pre-war army star, and four of the game's own by path), the paint (13 faction schemes, 24 colours, 6 neutrals, each with its coachline) and the mirrors (stock, under the bars egg or D, none) at the armour menu, paying in components; since the 2026-11-08a build also the rims (seven styles of our own, from laced spokes to a scrap plate, in chrome, satin black, gloss black, bronze, gunmetal or the body colour, and the cast rim in five finishes: 48 choices), the tyres (black, whitewall, red line), any paint colour from the MCM (a hue slider and four shades) and the licence plate (12 designs of our own, from the Commonwealth standard to Vault-Tec's and the factions', 60 stamped preset texts, crude ones among them behind a switch, and 16 colours for its letters and its background); the bike shows the new look parked, ridden and in first person. **Nothing changes until you choose**: every slot starts on the bike as it came. The MCM's Look section turns it off, picks the kit, and has a free mode with a choice per slot and faction sets (see *Customising the bike* below); since the 2026-11-09a build (test 51) the field kit's automatic mode puts an armour bench out first and then the game's own armour bench (the toolbox, which the game can't seat you at, only as a test), the parked bike shows a new paint or rim finish at once after an MCM apply, moving the MCM's paint hue or shade chooses Free colour, and the Vault-Tec plate's cog is redrawn at the plate's own size; since the 2026-11-10a build (test 52) the field kit's menu no longer shuts at once with Global Stash by SKK installed (the kit is linked to SKK's stash before it opens), a kit menu that closes within half a second with nothing changed never counts as working (the same kit once more, then the next kind), and a Free colour applied in the MCM shows from the first ride; since the 2026-11-14a build (test 53) Free colour shows in third person on every ride (the colours go into the chosen options' own swaps before the bike goes on: `[Look] WornIndex`), the armour menu names the item "Motorbike" and each slot's choice with its slot ("Paint: Factory"), its preview shows the whole bike, and the field kit comes out only in your own settlements (MCM "Field kit only in your settlements"); since the 2026-11-15a build (test 54: two crashes at the kit just after a plate colour, and no preview) a plate colour chosen at the kit goes on the parked bike when the menu closes (`[Look] KitDefer`), and the preview puts the bike 400 ahead of the menu's camera, turned three-quarters (Tune's first slider is its distance); since the 2026-11-16a build (the third customisation build) two 3D helmet badges, an Enclave and a Brotherhood helmet standing on an enamel plate (black for the Enclave, steel grey for the Brotherhood), and the Gunners skull on the tank and the rear fender, the seat's colour (15: as it came, ten leathers and four with a contrasting piping), every licence plate's emblem redrawn to read at riding distance with a new die-pressed plate font in the style of 1950s plates, and the MCM's and the kit's lists in alphabetical order; since the 2026-11-16b build (test 55: half the bike above the menu's view) the plugin places the whole bike in the armour menu's view itself, in its upper half, turned three-quarters and seen a little from above (`[Look] KitFit`); since the 2026-11-17a build (test 56) the Brotherhood of Steel, Minutemen, Nuka-Cola and Red Rocket plates are redrawn in their own colours, the 3D Enclave helmet stands on a polished chrome plate, the Gunners skull sits on a green flag patch, the flat Brotherhood of Steel badge is the colour emblem and Saddle tan is browner, and at the kit the plugin holds the bike (drag it with the left button to turn it about its middle, the wheel to zoom), turns it to the part of the slot you are on, and sets the kit out where you stand when its spot has no room (`[Look] KitHold`, `KitSlotView`, `KitRoom`); since the 2026-11-21a build (art build B, the second art build, with test 57's wishes) a Wear slot (Weathered, Dusty, Muddy, Rusty, Bloody and two combinations, Wasteland and Raider, over any paint), three muddy tyres, a badge on top of the front mudguard, the headlamp's colour (Warm as it came, Cool white, Amber, Selective yellow, Blue-white: the lens and the beam), the Nuka-Cola and Red Rocket badges, the 3D Enclave helmet on the Enclave's flag and the 3D Brotherhood helmet between two cogs, and the Brotherhood of Steel, Minutemen, Nuka-Cola and Red Rocket plates' top line centred; and at the kit the wheel zooms wherever the cursor is and holding the left button anywhere off the lists turns the bike (the wheel no longer scrolls the lists: the arrow keys do), the bike keeps your view in a slot's mods and their previews, and it turns only to a slot the highlight rests on (`[Look] KitMouse`, `KitWheelOwn`, `KitFollow`, `KitSlotSettle`, `KitNewSlots`); since the 2026-11-22a build (art build C, the third art build, with all your wishes after test 58) a Paint condition slot under the Wear (Scratched, Chipped, Sun-faded, Worn, Primer patches: choose it together with any Wear, the grime on top), the Wear also on the exhaust pipes and mufflers, the engine's outer covers and the front fork's lowers and over the tank and rear badges, the Wear (and Paint condition) on the parked bike (the shells blending in the meshes) and the bike under you in third person (`[Look] OverlayRuntime`), not only at the kit and in first person, the muddy tyres' tread clean where it meets the road, three meshing black gears on metallic blue behind the 3D Brotherhood helmet, Nuka-Cola's script neater, six more headlamp colours, and the front fender badge taken out (your pick: a save that had one shows none); and at the kit the bike on screen turns to each slot (the plugin holds the bike the menu really draws), the wheel zooms out as well as in, and with the cursor over the list panel the wheel scrolls the lists as the game does, zooming the bike anywhere else (`[Look] KitDrawn`, `KitWheelDown`, `KitWheelLists`, `KitSlots22`); since the 2026-11-23a build (your wishes after test 59) Rusty, and Raider's rust, lighter, see-through and darker at its edges, with no frame round the badge plates, three meshing gears on either side of the 3D Brotherhood helmet (your layout), the Wear and Paint condition on all four bikes every time, the parked bike after getting off and the bike under you in third person included, within a moment (test 59: "paint effects are not visible on free standing bike"; `[Look] OverlayParked`, on now, `OverlayEvery`, `OverlayQuick`), and at the kit no frame of the menu's own pose between options (`[Look] KitLate`, `KitPrePlace`)
- **a headlamp** (the Sketchfab build, F4SE): a round LED lamp on the fork bracket with its running light lit, and a real spot beam (like the power armor's, a light the mod places at the lamp) that turns with the bars and tilts with the bike; MCM: off, on, or on at night, and a hotkey; since the 2026-11-15b build its light and the tail lamp's lead by the game's own frame (`[Lamp] FrameLead`); since the 2026-11-21a build in five colours, the lens and the beam alike (the Headlamp slot, at the kit or in the MCM); since the 2026-11-22a build in eleven: Halogen, Daylight, Ice blue, Red, Green and Purple too
- **rides like a vehicle, not a person**: 75% less fall damage while riding (adjustable), deep water ends the ride and leaves the bike on the bank, and an enemy's hit knocks you off (optional; since the 2026-11-06a build a power attack only when it takes the "Big hit" share of your health, as any other hit, explosions always: MCM "Power attacks throw you off", off by default; since the 2026-11-09a build the bike parked after a knock-off never appears inside someone: a spot with an actor in it has no room, the bike is put back where it stood only if that place is still free, and while anyone else stands where it would appear it stays hidden and shows once the place is clear (you count only in the bike's very place, and not where the mod has just put it clear of you: getting off, calling it, bringing it; since the 2026-11-10a build someone knocked down there counts too, as does a dog or a crouching NPC right beside the settled bike, and you only within 150 units of its ground): test 50's crash came half a second after a knock-off with raiders round the bike); with F4SE, hostile people, creatures and smaller robots (since test 43 by a list of their own, `CMB_RamRobots`) the bike hits at speed are knocked over and take a little damage, the bike losing some speed at each (since test 45's build a dog the mod's script hasn't answered for by the time you reach it is ridden through rather than braked for, and knocked over when the answer comes, and a robot ridden at again after a hit is knocked over again; since test 46's an old save's knock-overs no longer make it brake for those same animals; MCM "Knock enemies over"; never companions, essential characters, anyone in power armor or the big ones: super mutants, behemoths, deathclaws, sentry bots and the like; since the 2026-11-01a build the knock-over that takes an enemy's last health kills it, and the kill is yours, experience and quests as for a shot: MCM "Knock-overs can kill"; since the 2026-11-02a build a knock-over holds the throttle to 85% of the speed for a quarter of a second, not 60% for 0.4 s, and a pack's hits share one dip, so the bike no longer nearly stops at a pack; an enemy of a medium race the script hasn't answered for by the time you reach it is ridden through, not braked for, when it was said yes to earlier in the ride or you are in a fight; and a kill by the bike gives the game's own experience, the killing hit being your own damage: MCM "Kill experience")
- **follows the ground**: the parked bike stands on the ground, tilted to match the slope (with F4SE, on the ground you just rode over, and since test 46's build a called bike on the ground under its wheels, leaning up to 20° across a slope; since test 47's getting off where you got on puts the bike back where it stood, the parked spot is checked for room as a call's is, and a bike called while you stand on a car comes to the ground beside it); with F4SE, the bike also pitches with the ground while you ride, leans into turns at speed (the rider with it, head level), stops short of boulder faces but slides along a railing beside it, climbs over low fallen trunks and stumps and up a step, but since test 45's build not onto a rail, a barrier or a log with a drop behind it (since test 46's not onto a rail lying on the ground or met at an angle nor along a fence either, and at full speed it stops short of a rail rather than with its front wheel in it; since test 47's it eases off only for what stays in its way, not for things you steer past, looks along its turn, stops about a wheel's radius short of a rail, isn't climbed onto a rail met at a shallow angle and doesn't ride on along one its front wheel is in), keeps its tyres on top of small bumps, takes a landing on its suspension and keeps going, backs up to a rail or a ledge's lip with its rear tyre just short of it and down off something it hangs on, turns in a circle rather than on the spot, climbs slopes too steep to walk up, and the camera sits farther back (since the 2026-11-01a build it also looks along the arc of the turn you're in, so a thing beside the curve eases the throttle by its distance instead of stopping the bike, a barrier on legs isn't climbed, a call from on top of a car or a truck puts the bike on the ground beside it rather than on its edge, and a high drop no longer halves the speed for most of a second; since the 2026-11-02a build a narrow thing ahead, a mailbox, a lamp post or a sign, is eased past by its distance and never stops the bike, while walls, cars and rails met square still do, a kerb or a log at speed holds the throttle to 85% rather than 55%, and a touch along a rail or a car's flank picks up again at once rather than from a crawl; since the 2026-11-06a build it steps round a post or a mailbox on its path to the open side (`Sidestep`) when you ride straight at it, a rail over posts is a wall, a pull-away from rest is punchier in its first second, and a call from on top of a truck tries the most room's own navmesh point first, so the bike comes down to the street; since the 2026-11-09a build how early it eases off for a wall or a car ahead is the MCM's "Caution", closer by default (60%: the throttle eases from about 8 m at full speed, where it was 11 m; 100% is the 2026-11-08a build), a bridge's end post with a drop behind it is no longer climbed as a step, and a call from a truck's bed tries the navmesh beside the truck first; since the 2026-11-10a build a new save starts at Caution 50, the sidestep still finding a post at Caution 60's reach, and a mouse move under 5 degrees no longer cancels a sidestep; since the 2026-11-15b build it also steps round a parked car, a barrel group, a fence piece or debris that ends near your line on one side, braking a little meanwhile (never walls, buildings, cliffs, the ground or anyone, nor while you turn: `[Steer] SidestepWide`), the camera sweeping past a post no longer starts and drops a sidestep (`SidestepSteady`), and moving the mouse the way a sidestep goes keeps it, or hands it to you (`SidestepMouseSide`)); since the 2026-11-22a build (test 58: "having one tire in the ground"; your wish: "it would be cool if bike was leaning a bit on sidestand/kickstand") every parked bike, got off, called or brought, is set on the ground under both its tyres and leans a little to its left on its own side stand, down on the parked bike now, never rolled onto a car's hood or a ledge beside it, and stands up as you get on (`[Room] ParkFit`, `ParkStand`); since the 2026-11-23a build (test 59: "it leans, but not always; sometimes one tyre is partially in the ground") its lean on the stand is held between 5 and 20 degrees from upright, so on a slope rising toward the stand it still rests on it and after a swim it no longer lies 31 degrees over, a tyre whose ray met a wrecked car's body is set on the ground under it, and each wheel rests on the highest point under its edge (`[Room] ParkLean`, `ParkTyres`)
- **its own sounds** (since the 2026-11-01a build; the game's own sound files, since the 2026-11-02a build under sound records of the mod's own, heard at the riding camera's distance: test 48 heard none of them): your character's own jump and landing sounds are muted while you ride; a tyre thump on every landing with a real fall, louder the higher the drop, a metal clunk on big ones and a splash into water; with F4SE a spray riding through shallow water, by speed and depth (the MCM's Sound section: "Bike sounds through the mod's own records", "Landing loudness range (dB)"); since the 2026-11-06a build landings sound like tyres and a dull thud, no metal, riding into water splashes, and riding through water is the mod's own wet-road swish, quieter when slow, louder at speed (MCM "Landing sounds without metal", "Water sound loop"); since the 2026-11-09a build a second, gentler wet-road loop from the same recording, with less hiss and more body, is the default ("Wet road, gentle"; "Wet road (the mod's own)" is the earlier one), since the 2026-11-10a build 3 dB louder (test 52's wish; `[Fx] WaterGentleDb=-3` is 2026-11-09a's level)
- **MCM menu** for every setting (with MCM installed); with F4SE, gear in the bike's slot goes back on after a ride

> **Status: in testing.** It has been tested in game round by round since the first build (test 60 the latest; this
> is the 2026-11-24a build, for test 61), each round answered from the logs and videos sent back. Every round's
> changes are checked offline before they ship: the plugin's structure, every script property and the vanilla form
> IDs, the scripts compiled against stand-in versions of the Fallout 4 scripting API, and `CMB_Slope.dll` run
> against a fake game (`tools/f4se-slope/test`). What changed since the last round hasn't run in the game until the
> next, so expect fixes after each.
> [TESTING.md](docs/TESTING.md) says what to send back.
>
> **Test 50's crash** (there since 2026-11-06a): the game crashed once, a Havok stack overflow about half a
> second after the third knock-off in 21 s, in a fight with several raiders (the plugin wasn't in the crash stack;
> suspected, about half sure: after a knock-off the bike was parked on a spot an actor stood in). Since the
> 2026-11-09a build the parked bike is kept out of anyone's place (`[Room] ActorRoom`, `ParkBack` and `ParkGuard`
> below); test 52 tried it with "Power attacks throw you off" on, four knock-offs with quick get-ons: no crash. If
> the game ever crashes again, send the crash log with both logs: its actor can be matched with the plugin's `room:` lines.
>
> **Test 54's crashes** (2026-11-14a): the game crashed twice at the field kit, both times in the frames right after a
> plate colour ("Plate background: The plate's own") re-composed the parked bike beside the kit while its menu was
> open (a null read in the graphics driver while the world was drawn). Since the 2026-11-15a build nothing changes
> the parked bike's materials while that menu is open (`[Look] KitDefer`), and the plugin keeps the three earlier
> sessions' logs (`[Diag] KeepLogs`), so a crash and two restarts no longer lose one.
>
> **Test 58's crashes** (2026-11-21a): the game crashed twice getting on, each time a moment after a Headlamp colour was
> picked at the field kit and Ride pressed at once, while the kit's new look was still going onto the parked bike (the
> same null read in the graphics driver as test 54's; the plugin wasn't in the crash stack). Since the 2026-11-22a build
> the parked bike's look goes on only by loading its 3D again, never onto the 3D the game is showing while you get on
> (`[Look] ParkedSwapHold`). TESTING's test 59 tries it first; if the game crashes again at a getting on, send the crash
> log with both logs: the plugin's `lens:` line and the script's mount line say what the two bikes carried then.
> Test 59 (one session on 2026-11-22a, 21 getting-ons and 15 field kit visits) had no crash.

## Already exists?

Fallout 4 does have some ride/drive mods that predate this one. I couldn't open Nexus from my environment, so these come from search results:

- *Driveable Motorcycle Mod* (reportedly with a pillion seat and a Dogmeat sidecar)
- *GrownUp Buttercup* and *RidingGiddyupButtercup*: rideable robot horse mounts
- *Drivable Cars Redux*, *Drivable Humvee*

This project is a from-scratch attempt with its own approach, see [DESIGN.md](docs/DESIGN.md).

## How it works, in one paragraph

There's no vehicle physics in Fallout 4's engine for the player, so the bike is an illusion. When you get on:

1. the parked bike disappears;
2. you start "wearing" the bike as an invisible-in-inventory armor piece;
3. your speed is multiplied;
4. jumping and sprinting are blocked, and by default only a handgun can be out (MCM "Weapons while riding", since the 2026-11-15b build; before it combat was blocked by default).

Getting off reverses all of that and parks the bike next to you. Indoors (dungeons and sewers are interiors), in the walled towns the game builds as worldspaces of their own (Diamond City, Goodneighbor, Nuka-World's market and amphitheater), in power armor and in furniture you can't get on, and riding into any of them parks it outside: through a door it waits there and is brought to you when you come out near it (with F4SE, since test 41, on the first of seven spots with room, each checked since test 43 as a bike-shaped box along your heading and since test 45 with a clear line from you to it and its ground near yours, so not behind a fence or inside a house, and since test 46 also beside and behind you, slid or turned clear of a fence or a wall its spot touches, or left where it waited when none has: outside Diamond City's gate the fixed spot was in the fence; a call with room at none takes the spot with the most room, and since test 46 with none to take says there's no room rather than putting the bike past a fence or inside a house), and after a fast travel in it stays where you set off; it can't be called there either; deep water leaves it on the bank.

> **What it looks like:** the game has no motorcycle riding animations (the `AnimsMotorcycle` keyword in
> `Fallout4.esm` is unused, and the archives hold only two parked-bike models). So the mod brings its own: a
> seated set of the holstered walk/run/turn/start/stop/idle clips, generated from the vanilla ones with the same
> timing and root motion, and the bike leans with you in turns. They're switched on while you ride by
> `CMB_RiderPose.esp`, which adds animation entries the way the DLCs do, without editing HumanRace, and
> comes with the animation data the Creation Kit would otherwise have to generate.
> Without it you run in place over the bike. See [ASSETS.md](docs/ASSETS.md).

## What's needed

| Need | Why |
|---|---|
| Fallout 4 on PC, any version from 1.10 (2017) on | the plugin is light (ESL) and edits no vanilla records |
| **Python 3** | `make_rider_pose.bat` builds `CMB_RiderPose.esp` and its animation data from your load order and game files |
| Python + [PyNifly](https://github.com/BadDogSkyrim/PyNifly), Bethesda Archive Extractor | only to build the bike meshes and riding clips yourself (the meshes put the Sketchfab model on the vanilla bike's collision and the clips are derived from the game's files, so none of it is in the repository) |
| Blender as a Python module (`bpy`), and the DDS encoders `quicktex` and `etcpak` | only to build the bike's textures and material files yourself (`tools/rider/build_bike.sh`, [ASSETS.md](docs/ASSETS.md)); a bash shell runs the build |
| Creation Kit (optional) | not needed: the scripts can be compiled with Caprica (`tools/syntax-check`); `compile_scripts.bat` uses the Creation Kit's compiler if you have it |
| F4SE (optional) | dedicated hotkey, weight-based side bag, slot-57 gear put back on after a ride, steeper slopes, a camera farther back, the bike tilting with the ground and knocking enemies over while riding, the bike brought from a door put on a spot with room, the parked bike laid on the ground under you, the engine sound's gears and pitch, and the speedometer's needle, the tail and brake light and the choice of mirrors, and since the 2026-11-01a build the tail lamp's light, the bike in first person, the brake key, the rider-pose check and the water sound, and since the 2026-11-02a build the hands let go for an item's use clip, the first-person bike under your eye, narrow things eased past and the frame-rate line in the log, and since the 2026-11-06a build the sidestep, the launch from rest, items at speed, the first-person tip and field of view and the water loop's level, and since the 2026-11-07a build the mirrors you fit at the bike on the ridden bike and the chosen look on the parked and first-person bikes (F4SE's material swap; without F4SE those two stay stock), and since the 2026-11-08a build the rim style you fit on the ridden and first-person bikes (the others hidden) and the colours: the free paint colour, body-colour rims and the plate's letters and background (F4SE's swap on every bike and the plugin's write on the ridden one; without F4SE each shows its own default), and since the 2026-11-09a build the parked bike kept out of people's places, an item's use clip stopped at speed, the Caution slider, the wheels stopping with the bike, the bridge's end posts, the truck's call, first person's fixes, the gears' lengths and the gentle water loop's level, and since test 51's fixes (the same build) the worn bike's colours written at getting on, a rebuilt shape held again, the tip's grace after a load and the switches the scripts read through `CMB_LookOptions` (the `CMB_Slope.dll` plugin, Fallout 4 1.11.240 only; the rays and the engine sound also need the Address Library), MCM menu; without it you favorite the keys for a hotkey and the bag counts items |
| Testing in game + Papyrus log | I can't run the game; the logs and screenshots are how fixes happen (with F4SE the plugin's `CMB_Slope.log` too; the sessions before are kept beside it, as `CMB_Slope_prev.log` since test 41 and since 2026-11-15a also `CMB_Slope_prev2.log` and `CMB_Slope_prev3.log`, so a crash and two restarts don't lose one) |

## Getting started

The plugin is already built (`Data/CommonwealthMotorbike.esp`). You need to:

1. Get the bike meshes, riding clips and compiled scripts (build them: [docs/ASSETS.md](docs/ASSETS.md), [BUILD_GUIDE](docs/BUILD_GUIDE.md))
2. Copy the contents of `Data` into the game's `Data` folder, or zip them for your mod manager, and enable `CommonwealthMotorbike.esp`
3. Run `make_rider_pose.bat` (with MO2: `make_rider_pose.bat "<MO2 folder>" <profile>`) and enable `CMB_RiderPose.esp`
4. Test: [docs/TESTING.md](docs/TESTING.md)

Details for every step: [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md).

## Controls

| Action | How |
|---|---|
| Call the bike | use **Motorbike Keys** (Aid) when it isn't nearby → "Call it here" |
| Get on | activate the bike → "Ride", or use the keys next to it |
| Get off | use the keys again (favorite them for a hotkey); since 2026-11-22a (F4SE plugin) the bike is set on the ground under both its tyres and leans on its own side stand, and getting on stands it up (`[Room] ParkFit`, `ParkStand`); since 2026-11-23a it is parked beside you, on your right (on your left when there's no room on your right), back along the track only when neither side has room, leaning 5 to 20 degrees from upright, and getting on hides it as you get on, with no reload first (`[Room] ParkBeside`, `ParkLean`, `ParkTyres`, `MountHide`) |
| Side bag | activate the parked bike → "Open side bag", or keys → "Open side bag" when the bike isn't nearby |
| Customise (since 2026-11-07a) | activate the parked bike → "Customise": the field kit and the armour menu (*Customising the bike* below); not while riding, in a fight or swimming; since 2026-11-17a (F4SE plugin) in the menu hold the left mouse button above the lists and move the mouse to turn the bike, roll the wheel there to zoom (`[Look] KitHold`); since 2026-11-21a the wheel zooms wherever the cursor is, on the lists too, and holding the left button anywhere off the lists (beside them, above them) turns the bike; on the lists the left button picks rows as before, and the wheel no longer scrolls them: move through a long list with the arrow keys (or W and S) (`[Look] KitMouse`, `KitWheelOwn`); since 2026-11-22a the wheel zooms out as well as in, and with the cursor over the list panel it scrolls the lists as the game does, zooming the bike anywhere else; the bike on screen turns to each slot (`KitWheelDown`, `KitWheelLists`, `KitDrawn`); since 2026-11-23a with no frame of the menu's own pose between options (`KitLate`, `KitPrePlace`) |
| F4SE hotkey | **B** by default: off / on / call |
| Brake (F4SE plugin, since 2026-11-01a) | **Space** while riding (MCM Hotkeys "Brake key (scan code)", a DirectInput scan code: 57 Space, 42 Left Shift, 29 Left Ctrl, 56 Left Alt, 45 X, 46 C, 0 none; the log names the key it read): brakes with forward held and holds the bike still once stopped; back (S) still brakes and backs up; off the bike Space jumps as always |
| Turn in first person (F4SE plugin, since 2026-11-15b) | **A** / **D** turn the bike as the mouse does (up to 2026-11-15a they stepped sideways: `[Steer] FirstKeys=0`), and with a weapon drawn in third person too (`FirstKeysArmed`); backing up with **S** turns the view over your shoulder (D right, A left; MCM "Looking back while reversing (first person)": Off, Over the shoulder, Third person; not with a weapon drawn) |
| Look round (F4SE plugin, since 2026-11-15b) | hold **Z** in first person on the bike (MCM Hotkeys "Look key (scan code)": 44 Z, 45 X, 46 C, 56 Left Alt, 0 none; the log names the key it read): the mouse turns only your head and the bike keeps its line; let go and the view comes back; since 2026-11-21a also the **right mouse button** (`[View] LookButton`, 257; Z still works), and in third person too: the mouse swings the camera round you while the bike keeps its line, and the camera eases back behind you when you let go (`[View] LookThird`); since 2026-11-22a in third person the plugin swings the game's camera itself, as far as you move the mouse (up to about 150 degrees, 60 with a weapon out: `[View] LookOrbit`); since 2026-11-23a with a weapon drawn too (with none the game's own free camera swings), never switched off for the session (`LookOrbitGame`, `LookRecover`) |
| A handgun (since 2026-11-15b) | draw (R) and fire as on foot: in third person seated, the left hand on the bar (since 2026-11-16b both hands on the bars, the pistol in the right); another weapon is put away (MCM Riding "Weapons while riding": None, Handguns only, Any weapon (standing poses)); since 2026-11-17a with Handguns only (F4SE plugin) a rifle is never drawn: it comes equipped and holstered (`[Tilt] DrawHandgunOnly`), and R draws nothing while riding until you get off; since 2026-11-21a the game doesn't aim while riding (the right button is the look's; the left fires as usual: `[Steer] AimBlock`); since 2026-11-22a for real (2026-11-21a's block never found the game's handler: `[Steer] AimStruct`), so the right button neither aims nor slows the bike; since 2026-11-23a your left hand stays on the bar and the right holds the pistol alone: in third person off its grip, pointing ahead, in first person with your body shown (`[Tilt] GunOneHand`, `[View] BodyGunGrip`) |

Don't favorite the keys to the F4SE hotkey's own key: one press then fires both, and the second is turned away as busy (harmless, but the log shows it twice).

## Customising the bike

Since the 2026-11-07a build (the first customisation build; the second, 2026-11-08a, adds the rims, the tyres, a free
paint colour and the licence plate; the third, 2026-11-16a, the 3D helmet badges, the Gunners skull, the plates redrawn,
the seat's colour and the lists in alphabetical order; 2026-11-17a corrects four plates, three badges and a seat colour
after test 56; the fourth, 2026-11-21a, art build B, adds the Wear slot, three muddy tyres, the front fender's badge,
the headlamp's colour and two badges, and redraws the 3D helmets' plates and four plates' top lines; the fifth,
2026-11-22a, art build C, adds the Paint condition slot, the Wear on three more parts and over the badges and six
headlamp colours, redraws the Brotherhood helmet's plate and Nuka-Cola's script, cleans the muddy tyres' tread and takes
the front fender badge out; 2026-11-23a lightens Rusty and puts three gears either side of the 3D Brotherhood helmet).
Activate the parked bike and choose **Customise**: a field kit (a toolbox) comes out of the side bag beside the bike, on
your side, you stand at it and the armour menu opens with the bike listed as "Motorbike" (up to 2026-11-10a the menu
called it "Default", its object template's name: test 53). Since the 2026-11-14a build the kit comes out only in a
settlement of yours (below). Its fifteen slots (since 2026-11-22a Paint condition in and the front fender badge out;
twelve up to 2026-11-17a, eleven up to 2026-11-15b):

| Slot | Choices (the first is the bike as it came) | Cost |
|---|---|---|
| Tank badge, left | Stock (winged wheel), None, Brotherhood of Steel, Brotherhood helmet, Enclave, Enclave helmet, Gunners, Minutemen, Railroad, Institute, Vault-Tec, Atom Cats, Raiders, Children of Atom, Pre-war army star (all 13 drawn for the mod), Gunners (game art), Pre-war army star (game art); since 2026-11-16a Enclave helmet (3D) and Brotherhood helmet (3D) (a cast helmet emblem of our own standing on a plain enamel plate with the stock badge's chrome edge: black for the Enclave, whose eyes glow amber, steel grey for the Brotherhood) and Gunners skull (a bone-white skull, no plate round it); since 2026-11-21a Nuka-Cola (a red crimped bottle cap with "Nuka" and "Cola" in white script and the swoosh) and Red Rocket (the round sign: a black rim, a red ring with RED ROCKET along its top, a yellow centre with two black R's back to back and a red rocket), and the 3D helmets on new plates: the Enclave's on the Enclave's flag, the Brotherhood's between two black cogs; since 2026-11-22a the 3D Brotherhood helmet on metallic blue with a fine sparkle between three meshing black gears, and Nuka-Cola's script redrawn even (one weight, slant and baseline, the swoosh clear between the words); since 2026-11-23a three meshing black gears either side of the 3D Brotherhood helmet, none behind it (your layout) | a badge Adhesive 1, Cloth 1; a 3D helmet Steel 2, Screws 1, Adhesive 1; Stock and None free |
| Tank badge, right | the same, and "Same as the left" (the default: it follows the left; any other choice ends that, "Same as the left" brings it back) | the same; "Same as the left" free |
| Rear fender badge | None (as it came), the 13 of ours, the two chest decals and, on the fender only, the Minutemen flag and the Brotherhood flag (game art); since 2026-11-16a Gunners skull; since 2026-11-21a Nuka-Cola and Red Rocket (Nuka-Cola's script redrawn since 2026-11-22a) | Adhesive 1, Cloth 1 |
| Paint | Factory (oxblood); 13 schemes, two-tone with their coachline (the eleven factions', Nuka-Cola, Red Rocket); 24 colours (Fire red to Raspberry); 6 neutrals (Gloss black, Pearl white, Silver, Gunmetal, Pre-war cream, Primer grey); "Palette test: colour index" (cobalt blue if the colour lookup works, primer grey if not); since 2026-11-08a "Free colour (hue in the MCM)": the MCM's "Paint hue" in one of four shades, with a cream coachline | Factory Oil 1; a colour (and Free colour) Adhesive 2, Oil 2 and the Armorer perk |
| Mirrors | Stock, Under the bars (egg), Under the bars (D), None | stock Steel 1, Glass 1; egg or D Steel 2, Glass 2, Screws 1; none Screws 1; a mirror taken off comes back as a loose mod |
| Rims (since 2026-11-08a) | Stock (cast); the cast rim in satin black, gloss black, bronze, gunmetal or body colour; seven styles of our own (Laced, Solid disc, Star five, Turbine, Pre-war steel, Atomic, Scrap plate), each in chrome, satin black, gloss black, bronze, gunmetal or body colour: 48 in all, on both wheels | a cast finish Adhesive 1, Oil 1; a style Steel 3, Screws 2, Oil 1 and the Armorer perk; Stock free |
| Tyres (since 2026-11-08a) | Black (as it came), Whitewall, Red line (on both sidewalls of both tyres); since 2026-11-21a Black, muddy, Whitewall, muddy and Red line, muddy (the tread caked, the sidewalls splashed, the bands partly showing; since 2026-11-22a the tread's faces clean and black where they meet the road, the mud between the blocks and on the shoulders) | Adhesive 1, Oil 1; Black free |
| Plate (since 2026-11-08a) | Stock (plain); 12 designs of our own: Commonwealth standard, Commonwealth vintage, Blank, Vault-Tec, RobCo, Nuka-Cola, Red Rocket, Brotherhood of Steel, Minutemen, Institute, Raider scrap, Army motor pool (since 2026-11-16a every emblem redrawn at the plate's own size and the letters in a die-pressed plate font; since 2026-11-21a the Brotherhood of Steel, Minutemen, Nuka-Cola and Red Rocket plates' top line centred on the plate) | Steel 1, Oil 1; Stock free |
| Plate text (since 2026-11-08a) | The plate's own (the design's text), None, and 60 stamped presets of 5 to 7 characters: 32 themed (AB 1234, VLT 111, PIP-BOY, PALADIN, GEN-3, ...), 14 funny (DOGMEAT, I♥RADS, NO CAPS, ...), 14 crude (BITE ME, ...: MCM "Crude plate texts" off hides them) | Steel 1; the plate's own and None free |
| Plate letters, Plate background (since 2026-11-08a) | The plate's own (the design's colour), and 16 colours: Plate white, Cream, Black, Plate red, Maroon, Commonwealth blue, Vault blue, Vault yellow, Orange, Forest green, Olive drab, Gunmetal, Teal, Phosphor green, Silver, Rust | Oil 1; the plate's own free |
| Seat (since 2026-11-16a) | Dark brown (as it came); ten leathers: Black, Tobacco brown, Saddle tan, Oxblood, Olive drab, Cream, Slate grey, Red, Navy, Pre-war turquoise; four with a contrasting piping: Black with red piping, Black with cream piping, Dark brown with cream piping, Oxblood with black piping. The grain, shading and lighter worn edges stay in every colour; faction sets leave the seat | Cloth 2, Adhesive 1; Dark brown free |
| Wear (since 2026-11-21a) | As it came; Weathered (sun-faded on top, chipped to primer and bare steel at the knee grips and the edges, fine scratches), Dusty, Muddy (mud from the wheels on both fenders and the tank's lower front), Rusty (rust from the edges, round the badges and the plate, under the tank), Bloody (spatter and smears), and two together: Wasteland (weathered, dusty and muddy) and Raider (rusty and bloody). Over any paint, Free colour included, and over Paint condition; since 2026-11-22a also on the exhaust pipes and mufflers (with Weathered heat colours near the cylinders, with Rusty rust heavy on the mufflers), the engine's outer covers and the front fork's lowers, and over the tank's badge plates and the rear badge (mud and blood where they land, dust along a plate's top edge, rust from under its bottom edge; up to 2026-11-21a they were kept clear); since 2026-11-23a Rusty (and Raider's rust) lighter: scattered rust stains, see-through with darker edges, nothing along a badge plate's outline, the mufflers' rust brown rather than orange; faction sets leave it | Oil 1, Cloth 1; As it came free |
| Front fender badge (2026-11-21a only) | gone since 2026-11-22a (your pick after test 58: "I would drop front fender badge"): not offered at the kit or in the MCM and never drawn, so a save that had one shows none (its records stay, so old saves load). In 2026-11-21a: None (as it came); every badge of the rear fender's list, in its order, then Nuka-Cola and Red Rocket: on top of the front mudguard, just ahead of its highest point, read from in front; it turns with the bars | Adhesive 1, Cloth 1; None free |
| Headlamp (since 2026-11-21a) | Warm (as it came), Cool white, Amber, Selective yellow, Blue-white; since 2026-11-22a Halogen, Daylight, Ice blue, Red, Green, Purple (Red and Purple light the road dimly, as coloured lamps do): the lens and the beam alike (parked and unlit, a coloured lamp shows a tinted bulb; Halogen and Daylight look as Warm) | Glass 1, Screws 1; Warm free |
| Paint condition (since 2026-11-22a) | Pristine (as it came); Scratched (fine scratches through the clear coat, a few deeper ones to grey primer and bright steel, scuffs where things rub), Chipped (flaked chips at the edges and the knee grips, stone chips low down and at the front), Sun-faded (a chalky fade on what faces the sky, the clear coat peeling in patches on the tops), Worn (all three), Primer patches (grey and red-oxide repair patches with feathered, sanded edges). The paint's own damage, over any paint and under the Wear's grime: choose it together with any Wear and the dirt, rust and blood lie on top; nothing over the badges but the fade; faction sets leave it | Oil 1, Cloth 1; Pristine free |

Leave the menu and the kit goes back into the bag; the bike shows the new look parked, ridden and in first person (the
parked and first-person bikes through F4SE; the ridden bike's mirrors through `CMB_Slope.dll`). In one of your
settlements its workshop's components count; elsewhere the side bag's do as well as yours. **Nothing changes until you
choose**: each slot starts on the bike as it came, so with no choice the bike looks as the 2026-11-07a and 2026-11-06a
builds' did.

**Rims, tyres, the free colour and the plate** (since 2026-11-08a). A rim style takes the place of the cast wheel on
both wheels; the styles you didn't fit stay on the bike invisible (on the ridden and first-person bikes the plugin also
hides them, as it hides the mirrors you didn't fit). A body-colour rim takes the paint's colour, and follows it when the
paint changes (with Free colour, the hue). Free colour paints the tank and fenders in the hue of the MCM's "Paint hue"
(0-359 round the colour wheel: 0 red, 120 green, 240 blue; 210, a steel blue, by default) and the depth of its "Paint
shade" (Deep, Normal, Light, Pastel); a new hue or shade shows at "Apply the look" or the next getting on or
activation of the parked bike. Since 2026-11-09a moving the hue or the shade chooses Paint "Free colour" there, unless a
faction set is applied with it or you choose another Paint in the same MCM visit (`[Look] HueFree`; test 51: "it didn't
do anything", the paint not being Free colour). The plate: a design brings its own text and colours ("The plate's own");
a text, a letters' colour and a background colour of your own replace them. The two colour slots aren't shown in the
armour menu's preview (its bike keeps the design's colours): since 2026-11-15a the parked bike beside the kit takes them
when you leave the menu (up to 2026-11-14a as soon as you took one, which crashed the game twice in test 54: `[Look]
KitDefer`). A faction set with a plate (Brotherhood of Steel, Minutemen, Institute, Vault-Tec, Raiders, Pre-war army) also fits
that plate with its own text and colours.

**The 2026-11-09a build's fixes** (test 51). The parked bike shows a new paint or rim finish at once after "Apply the
look" (test 51: grey until the next ride): each paint and rim finish has its own palette colour (`[Look]
PaletteIndex`), and the parked bike's 3D is loaded again (`[Look] ParkedReload`): it vanishes for a moment, behind the
pause menu until you close it, and comes back at once, whoever stands beside it. Getting on keeps the look's mods on the
worn bike between rides (`[Look] FastMount`: about 1.5 s with the look unchanged), and a second press while the bike's
menu is coming is ignored (`[Look] MountGuard`). The Vault-Tec plate's cog is redrawn at the plate's own size: eight
teeth and a hole in the middle, clear of the yellow pinstripe (test 51: the logo was a blob in the corner); every other
plate is unchanged.

Since the 2026-11-09a build (test 51: the field kit never worked) automatic puts an armour bench beside the bike, and if
its menu closes at once, the game's own armour bench (Fallout4.esm's). A bench counts as working once its menu stayed
open 2 s, you made a change, or you were at it; that one is remembered for next time (`CMB_KitWorked`; a remembered
toolbox from an older build is forgotten once). The toolbox modes are tests: the game's toolbox can't be sat in (up to
2026-11-08a automatic tried it first and remembered a mode as soon as its menu opened: `[Look] KitHeld=0`). Emergency
reset also puts a field kit away.

**The 2026-11-14a build's field kit** (test 53's wishes). Each slot's choice is named with its slot in the armour
menu ("Tank L: Stock (winged wheel)", "Paint: Factory", "Rims: ..."; the slot rows show the fitted mod's name), and the
menu's preview shows the whole bike, smaller and turned three-quarters, with room to zoom (test 53: a tyre filled it):
with F4SE `CMB_Slope.dll` writes the preview at run time, as the MCM's "Field kit preview" says (New; As before, the
2026-11-10a build's view; Tune, with six sliders for its size, turn, tilt, height and zoom limits). With MCM Look
"Field kit only in your settlements" on (the default) Customise opens the kit only in a settlement whose workshop is
yours; anywhere else "The field kit works only in your settlements." and nothing comes out of the side bag (off:
anywhere, as before). "Free customising" in the MCM works anywhere either way. The names have no switch: an ESP built
with the generator's `--kit-names 0` has 2026-11-10a's (not in the package). Free colour now shows on the ridden bike in
third person too (test 53: blue there on every ride but the one the game loaded into): before the bike goes on, its
colours are written into the chosen options' own swaps, which the game builds the bike from (`[Look] WornIndex`).

**The 2026-11-15a build's field kit** (test 54's fixes). The game crashed twice at the kit, each time in the frames
right after a plate colour ("Plate background: The plate's own") re-composed the parked bike beside it while the
menu was open: the plate colours you choose there now go on the parked bike when you leave the menu, with the rest of
the look, as the MCM's Apply does (`[Look] KitDefer`). The preview showed nothing (its camera was inside the bike):
New now puts the whole bike 400 ahead of the menu's camera, turned three-quarters, with room to zoom; in Tune the
first slider is "Preview distance" (100-2000; less is a bigger bike), not the size, which the menu ignores (a
2026-11-14a save keeps that slider's 30, meaning New's 400 until you move it).

**The 2026-11-16a build: the 3D helmets, the Gunners skull, the plates, the seat and the lists** (the third customisation
build, the first of two art builds; the author's picks). "Enclave helmet (3D)" and "Brotherhood helmet (3D)" in both tank
slots turn the tank's badge plate into a plain enamel plate with the stock badge's chrome edge (black for the Enclave,
steel grey for the Brotherhood) and stand a cast helmet emblem of our own on it, centred on the plate and angled with it,
about 2.5 cm proud: it catches the light and casts its own shading, from the side, the riding view and the kit's preview; the Enclave's eyes
glow amber. "Same as the left" follows a 3D left as any other choice. The flat "Enclave helmet" and "Brotherhood helmet"
stay. Every bike carries both helmets on both sides, invisible until chosen (a swap can't add a shape), so a flat badge or
Stock again leaves no helmet behind. "Gunners skull" is a bone-white skull with a cross on the brow and a stitched mouth,
with no plate round it, on the tank and the rear fender. Every licence plate's emblem is redrawn at the plate's own size
(as the Vault-Tec cog was in 2026-11-09a) so it keeps its shape at riding distance, and the letters of the texts and
legends are a new die-pressed plate font in the style of 1950s plates: narrow, square, flat-cut and raised; the layouts,
texts and colours are as before. The Seat slot (above) colours the seat's leather, its grain, shading and worn edges kept;
the black seats have half the stock leather's sheen so they read darker than the stock brown. And the lists: the MCM's
eleven Look dropdowns (both tank badges, the fender, Paint, Rims, Seat, the plate's four, Faction set) show their choices
alphabetically after the pinned ones (as it came, None, "Same as the left", "The plate's own"; Paint's "Palette test:
colour index" last); Mirrors and Tyres stay steppers. The kit's lists are given the same order through the recipes'
priority, if the armour menu sorts by it (test 56 tells). Your saved choices don't change: only the order shown. The
first getting on after the update puts the look's mods on afresh once (the look's key has the seat now; logged).

**The 2026-11-16b build's field kit** (test 55's fix: "half of the bike was in view", too high, too close, side-on). Test
55's screenshot gave the armour menu's camera (at the scene's origin, about 40 degrees across), so 2026-11-15a's 400
ahead made the bike two screen-heights tall, its top half above the view. With the MCM's "Field kit preview" on New the
plugin now places the bike itself: the whole bike between 0.07 and 0.50 of the screen's height, above the menu's list,
centred, turned three-quarters with its front wheel nearer and seen a little from above; the mouse wheel's zoom and the
mouse's turning still work (`[Look] KitFit`, `KitFitBox`). New's record is now 0,1050,-45 with the bike's top tipped 12.8
degrees towards you, which shows the whole bike even where the plugin can't place it, and Tune's sliders start there in
a new save ("Preview distance" 1050, "Preview tilt" -2, "Preview up / down" -45; a save keeps its own 400, 0, 0). The
plugin finds the menu's bike by its 3D too (`[Look] KitFind`), since the menu's item reads as the bike only at a change.

**The 2026-11-17a build: four plates, three badges and the tan** (test 56's art corrections, after your pictures; the
plates' letters, which "looked better than before", are unchanged). Four plate designs are redrawn in their own
colours, each emblem filling the plate's top-left corner (the text runs across the middle of every plate, so no emblem
can lie under it): "Brotherhood of Steel" has the Brotherhood's emblem in colour (a white disc with three black cogs, a
dark sword point up with a gold cross-guard and pommel, blue wings), the plate steel grey as before; "Minutemen" the
flag's device in cream on the blue (a musket broken by a lightning bolt, three stars); "Nuka-Cola" a red crimped bottle
cap with "Nuka" and "Cola" in a white script of our own and a swoosh between them, "ZAP THAT THIRST!" across the top
where the script line was; "Red Rocket" is the whole plate as the round sign: a black rim, a red frame, a yellow centre
with the letters in red, the round sign (two R's back to back with a rocket) in the corner, "RED ROCKET" along the top
and "GASOLINE - DIESEL - FUSION" along the bottom in white (another background colours the centre; Cream gives the same
yellow). The 3D Enclave helmet stands on polished chrome inside the chrome edge, a thin dark line between them, where
the black enamel hid it; the Brotherhood helmet's plate stays steel grey. "Gunners skull" is a rough-edged white skull,
the X on its brow, on a deep green flag patch with slightly rounded corners (both tanks and the rear fender). The flat
"Brotherhood of Steel" badge is the colour emblem (a white disc with three black gears, a steel sword with a gold guard
and pommel, blue wings, a black outline) on the tanks and the rear fender: no red wings. "Saddle tan" is a browner,
less yellow leather tan. Only eight textures change: every choice, name, cost, record and material is as before, and
the 2026-11-16b package's eight textures copied back give the old art (*CMB_Slope.ini* below, the art's switches).

**The 2026-11-17a build's field kit** (test 56: "zoom didn't work in field kit", "seemed like I was able to grab it
only by front wheel", a view per slot wished for, "field kit pushes me through the wall if there is not enough space").
With "Field kit preview" on New the plugin now holds the bike in the armour menu: hold the left mouse button anywhere
above the menu's lists and move the mouse to turn it about its own middle, never tipping sideways, and roll the wheel
there to zoom in and out about the middle (over the lists the wheel scrolls them); the menu's own turn (its grab, a
gamepad's stick) turns it the same way (`[Look] KitHold`). In test 56 the menu's own zoom never moved, so the plugin
reads the frame's mouse input itself, and the menu's turn swung the bike about the ground between its wheels. On each
slot the bike turns to that part, gliding: the rear for the four plate lists, the left side for Tank L, the right for
Tank R, the seat from above, the rear fender from behind and above, the wheels from the side for Rims and Tyres,
three-quarters for Paint and Mirrors; you can still turn and zoom it from there (`KitSlotView`, each view a key). And
before the kit comes out the plugin checks the spot the game walks you to (its ground, a clear line from you, nothing
close round it, the bike's own side not counted; with the armour bench, the bench's own place): with no room there the
kit (or the bench) is set out where you stand, so you aren't moved into a wall (`KitRoom`).

**The 2026-11-21a build: wear, muddy tyres, the front fender's badge, the headlamp's colour, two badges, the helmets'
plates and the plates' top lines** (art build B, the second art build, with your wishes after test 57). "Wear" lays
one of seven looks over the paint, whatever the paint (Free colour too): Weathered (sun-faded on top, chipped to grey
primer and bare steel at the knee grips and along the edges, stone chips at the front, fine scratches), Dusty (a pale
khaki film on what faces up, thick in the creases, washed off in streaks down the sides), Muddy (mud thrown up by the
wheels: both fenders caked low down and behind the wheels, the tank's lower front, the tank top clean), Rusty (rust
from the edges, round the badges and the plate and under the tank, with streaks), Bloody (spatter, drops with tails,
three hand smears, drips), and two together, Wasteland (weathered, dusty and muddy) and Raider (rusty and bloody). It is
drawn by our own code on two thin shells over the paint of the tank and rear fender and of the front mudguard, 0.3
units over it and invisible until you choose a wear, so the paint under it is still the paint you chose; the tank's
badge plates and the rear badge are kept clear of it, and both fender badges sit over it. Three muddy tyres join the
Tyres slot: "Black, muddy", "Whitewall, muddy" and "Red line, muddy". "Front fender badge" puts a badge on top of the
front mudguard, just ahead of its highest point, read from in front: any badge of the rear fender's list, in its order,
then Nuka-Cola and Red Rocket; it turns with the bars and rides the suspension. "Headlamp" colours the lamp: Warm (as
it came), Cool white, Amber, Selective yellow or Blue-white, the lens and the beam alike (riding, an Apply in the MCM
changes the beam at once and the ridden bike's lens at the next getting on; parked and unlit, a coloured lamp shows a
tinted bulb behind the glass). Two new badges for both tanks and both fenders: Nuka-Cola (a red crimped bottle cap with
"Nuka" and "Cola" in white script and the swoosh between) and Red Rocket (the round sign: a black rim, a red ring with
RED ROCKET along its top, a yellow centre with two black R's back to back and a red rocket). The 3D Enclave helmet now
stands on the Enclave's flag (red and white stripes inside the chrome edge, the blue corner with a ring of 13 white
stars), and the 3D Brotherhood helmet's steel grey plate has a black cog from the Brotherhood's emblem on each side
(your wishes). The Brotherhood of Steel plate's top line is centred on the plate and ends well inside it (test 57: it
ran off the right edge, under the tail lamp from low behind), and so are the Minutemen's, Nuka-Cola's and Red Rocket's,
which had the same layout. Every new choice is opt-in; the files the art changes (the five meshes, the badge atlas, two
plate textures) have their own switches (*CMB_Slope.ini* below, the art's switches).

**The 2026-11-21a build's field kit** (test 57: "when selecting menu for e.g. plates bike goes into default position",
the bike side-on after E for the rest of the visit, the slot read walking the list, and the wheel and the drag "only
first time after opening field kit": in test 57 the cursor sat on the lists, where 2026-11-17a left the wheel and the
clicks to the menu). With "Field kit preview" on New the wheel zooms the bike wherever the cursor is, on the lists too,
and holding the left button anywhere off the lists (beside them, above them) and moving the mouse turns it; on the lists
the left button picks rows as before (`[Look] KitMouse`, the lists' box `KitListBox`; your pick). While the kit shows
the bike the wheel no longer scrolls the lists (`KitWheelOwn`): move through a long list (Paint, Rims, Plate text) with
the arrow keys (or W and S), the list following the highlight; `KitWheelOwn=0` gives the wheel to the lists as well. In
a slot's mods (E) the menu loads a bike for each mod and shows the one you are on: the plugin now holds them all, so
every preview keeps your view and zoom, and a sudden change by the menu is never taken as a turn (`KitFollow`). The bike
turns to a slot's part only once the highlight has stayed on it a quarter of a second, so a quick sweep over the list
doesn't swing it about (`KitSlotSettle`). The three new slots have views of their own: Wear three-quarters from a little
above, Front fender badge the front mudguard from the front, Headlamp the bike from the front (`KitNewSlots`, each view
a key).

**The 2026-11-22a build: Paint condition, the Wear on more parts and over the badges, the tread, the Brotherhood
helmet's gears, Nuka-Cola's script, six headlamp colours, the front fender badge out** (art build C, the third art
build: your wishes after test 58, all of them). "Paint condition" is the paint's own damage, under the Wear's grime:
Scratched (fine scratches through the clear coat, a few deeper ones to grey primer and bright steel, scuffs where things
rub, most at the knee grips and on the tops), Chipped (flaked chips at the rolled edges, the tight bends and the knee
grips, stone chips on what faces the front wheel and low down), Sun-faded (a pale, chalky fade on what faces the sky,
the clear coat peeling in patches on the tops), Worn (all three) and Primer patches (grey filler primer and two
red-oxide repair patches with feathered, sanded edges). **Paint condition and Wear can be chosen together**: the dirt,
rust and blood lie on top of the damaged paint ("scratched, chipped and weathered paint and then on top of that
rusty/muddy"). It is drawn on two more thin shells, 0.16 units over the paint and under the Wear's, invisible until you
choose. The Wear now also reaches the exhaust pipes and mufflers (with Weathered heat colours near the cylinders, with
Rusty rust heavy on the mufflers), the engine's outer covers (the crankcase, the primary and cam covers, the air
cleaner) and the front fork's lowers, "not too much but noticeable", and it lies over the tank and rear badges (mud and
blood where they land, dust along a badge plate's top edge, rust from under its bottom edge; the 3D helmets stand above
it). The Wear and Paint condition now show on the parked bike and on the bike under you in third person too (test 58:
"wear is not visible outside of field kit menu"): on the parked bike through the shells' blending in the meshes, on the
bike under you a moment after the screen comes back (`[Look] OverlayRuntime`; `OverlayParked` is test 59's A/B for the
parked bike). The muddy tyres' tread is clean and black where it meets the road, the mud between its blocks
and on its shoulders ("it doesn't stick like that irl"). The 3D Brotherhood helmet stands on a metallic blue plate with
a fine sparkle, framed by three meshing black gears (a big one behind the helmet, its teeth showing round it, and a
smaller one either side), and Nuka-Cola's script is redrawn even: one weight, one slant, one baseline, the swoosh clear
between the words (the plate's small cap as before). The Headlamp slot has six more colours: Halogen, Daylight, Ice
blue, Red, Green and Purple, the lens and the beam alike. And **the front fender badge is gone** (your pick: "I would
drop front fender badge"): it is no longer offered at the kit or in the MCM and is never drawn, so a save that had one
chosen shows none (its records stay, so old saves load). Every new choice is opt-in; the files the art changes (the five
meshes, the Wear's materials and 18 of its maps, the six muddy tyres, the badge atlas) have their own switches
(*CMB_Slope.ini* below, the art's switches).

**The 2026-11-22a build's field kit** (test 58: "it zooms in on the bike, but doesn't zoom out, also scroll doesn't work
on menu to look through items in field kit"; "bike doesn't spin to position to show what is being changed"). The plugin
now asks the menu's own renderer which bike it draws and holds that one (`[Look] KitDrawn`): in test 58 the views went
to two bikes the menu wasn't showing, so the bike on screen kept the menu's three-quarter view. Each slot turns the bike
you see to its part again, Paint condition three-quarters from a little above (`KitSlots22`, `KitViewPaintWear`). The
wheel zooms out as well as in (`KitWheelDown`: the game's down notch was never counted), and **with the cursor over the
list panel the wheel scrolls the lists as the game does**, zooming the bike anywhere else (`KitWheelLists`, your pick;
the panel is `KitListBox`); holding the left button off the lists still turns the bike. The front fender badge has no
row and no view any more.

**The 2026-11-23a build: Rusty lighter, three gears either side of the Brotherhood helmet, the Wear on every bike at
once** (your wishes after test 59). Rusty, and Raider's rust, which stacks it, is lighter: fewer and smaller rust
stains, each see-through in its middle so the paint shows through and darker at its edge, browner, with fewer and
fainter streaks, and nothing traces the badges' plates any more (test 59: "rust is too much, should be less intense,
more transparent and in darker colors on edges"; "in preview badges are shown ok, beside for rusty where there is a
rectangle around the frame"): one or two stains sit by each plate at random places, and the mufflers' rust is brown
rather than orange. The 3D Brotherhood helmet stands between two groups of three meshing black gears on its metallic
blue plate, after your sketch ("I was hoping to have 3 gears shown on each side"): on each side a big gear low toward
the plate's end, a smaller one above it and a smaller one beside the helmet, the small ones' teeth in the big one's
gaps, and no gear behind the helmet any more. And the Wear and Paint condition now show on all four bikes every time
(test 59: "paint effects are not visible on free standing bike"; "wears are showing correctly in the preview, but are
not visible on the bike when outside of field kit"): on the parked bike right after its blink a couple of seconds after
the kit closes, and within a second of getting off; on the bike under you from the moment the screen comes back, and
within a split second of drawing or putting away a weapon (`[Look] OverlayParked`, on now, `OverlayEvery`,
`OverlayQuick`: *CMB_Slope.ini* below). The files the art changes (Rusty's and Raider's 30 maps, the badge atlas) have
their own switches (*CMB_Slope.ini* below, the art's switches).

**The 2026-11-23a build's field kit** (test 59: "between every option bike gets into default position for a moment").
The menu puts each option's bike in at its own three-quarter pose in its own update of the frame, after the plugin had
turned the bike for that frame, so one frame showed it so. The plugin now also turns a new bike right after the menu's
update, before the frame is drawn (`[Look] KitLate`), and turns the bikes the menu has loaded but not shown yet too
(`KitPrePlace`), so each option keeps the slot's view.

**MCM, Look** (before Hotkeys; 20 controls since 2026-11-08a, 21 since 2026-11-14a, 22 since 2026-11-16a, 25 since
2026-11-21a, still 25 since 2026-11-22a and in 2026-11-23a): "Customise at the bike" (on: the Customise button; off: no
button and the bike as it came), "Field kit" (Automatic, two toolbox tests, Armour bench and, since 2026-11-09a, "The
game's armour bench"), since 2026-11-14a "Field kit only in your settlements" (on; and the section "Field kit preview"
after Look), "Parts from the side bag", "Crude plate texts" (since 2026-11-08a, on by default; off: the 14 crude plate
texts aren't offered at the kit, and a plate wearing one shows its design's own text at the next getting on, activation
or Apply), and "Free customising (no field kit, no cost)", which shows a choice per slot (the eleven above, since
2026-11-16a twelve with "Seat" after "Tyres", since 2026-11-21a fifteen with "Front fender badge" after "Rear fender
badge", "Wear" after "Paint shade" and "Headlamp" after "Mirrors", since 2026-11-22a "Paint condition" after "Paint
shade" and no "Front fender badge", with "Paint hue" and "Paint shade" under the paint; since 2026-11-16a the dropdowns
alphabetical, read and set through the controller's properties, the globals keeping the option's number), "Faction set"
(the paint and all three badges of one of eleven sets, and for six of them the plate) and "Apply the look": it puts the
choices on the parked and first-person bikes at once and on the ridden bike at the next getting on, except a new rim
style: then the ridden bike is put on again within about a second (you stay seated; the bike is gone for a moment).
Turning "Customise at the bike" off (or changing a choice without "Apply the look") takes effect at the next getting on
or activation of the parked bike (or Apply, or a load), and on the ridden bike also when it swaps mid-ride (a weapon
drawn or put away, a hit); a load mid-ride with "Customise at the bike" off puts the ridden bike on again too if its
rims weren't the cast ones.

Known, left for now: in the menu, while the right badge follows the left, the preview shows the right as the left was
when the menu opened (the bike follows the new left once you close it); after a load the parked bike's look comes back
within a second; the ridden bike needs F4SE's swap where the game refuses its mods (logged); replacing the mirrors at
the kit gives that mirror's loose mod back each time; an emergency reset while the kit switches from the toolbox to the
bench (about 2 s), with a new Customise straight after it, can let the old switch go on into the new session (rare: wait
a few seconds after a reset). Since 2026-11-08a: the plate's colours aren't previewed in the armour menu (above), and
after a new design is taken the preview shows the old design's own text until the session ends; the rim styles you
didn't fit are still drawn, invisible, on the parked bike (TESTING's step 12 asks about the frame rate); a rim style
changed in the MCM while riding puts the ridden bike on again within about a second (it blinks out for a moment). Since
2026-11-09a the parked bike blinks once when its look is put on outside a ride (an apply, the kit's end, a load beside
it: ParkedReload). Since 2026-11-14a: an option you didn't choose keeps the last colour written into it until you choose
it again (only the preview shows that). Since 2026-11-15a: the preview's distance is computed from test 54's numbers
(the bike may look small: zoom in, or Tune's "Preview distance"), and the plate colours show on the parked bike when you
leave the menu, not while it is open. Since 2026-11-16a: whether the kit's lists follow the alphabetical order (and
which way up) is test 56's to say, as is whether the MCM's dropdowns work through the controller's properties (if one
always shows its first choice or a choice does nothing, the next build binds them to globals of their own, already wired
in the scripts); the helmets are smaller than the 12 cm first planned (they fit inside the enamel plate both sides show,
and clear of the under-bar mirrors at full lock); every bike draws the four hidden helmets (about 14,000 triangles: test
56 measures the frame time beside the parked bike); a piped seat looks like its plain colour from riding distance (the
welt is under a pixel there); the Brotherhood's steel grey plate on the Brotherhood paint is the weakest contrast of all
the paints (it reads by its chrome edge and gloss). Since 2026-11-16b: the menu's camera was measured from one
screenshot (about 40 degrees across: if test 56's picture shows the bike bigger or smaller than `KitFitBox`, the view is
off by that ratio, `[Look] KitFitView`); if the menu writes its own place back after the plugin's every frame, what
shows depends on the frame's order (the `kit: fit:` line at the close counts it, the screenshot says which); the
record's tilt assumes the menu turns about the screen's level (otherwise the bike tips 12.8 degrees nose up or down:
Tune's tilt 0 takes it away). Since 2026-11-17a: the Nuka-Cola cap is the plate's own red, so it reads faintly from
riding distance; on Red Rocket's own background a thin yellow line can show round the black rim; the chrome under the
Enclave helmet at night is the renders' guess, not the game's light; the kit's views per slot and the wheel's input rest
on menu fields no test has read before (the `kit: slot:` line and the close line say what your game gives); the kit set
out where you stand can overlap the bike or the wall. Since 2026-11-21a: the wear is a blended layer over the paint,
which the game may light, sort or fade at a distance otherwise than the renders do (test 58 says; a cut-out layer is the
fallback); blood on the dark paints (the Factory oxblood, Gloss black) reads more by its sheen than its colour; the wear
runs partly under the tank's badge plates and is kept off them; every bike draws the two shells and the front patch,
invisible until chosen (about 13,500 triangles: test 58 measures the frame rate beside the parked bike); at full lock
the bars pass close over the tank's wear; a coloured lamp's bright centre can look near white or yellow, its colour in
the glow and on the road, and Amber's beam is dimmer than Warm's; on the right tank the Enclave flag's blue corner is
toward the rear (each side reads as the flag seen from outside); the ridden bike's lens takes a new colour at the next
getting on (the beam at once); the kit's views for the three new slots are chosen from the shapes, not from a picture of
the game, and the lists' box was measured on a 16:9 screen (`KitListBox`). Since 2026-11-22a: the Wear and Paint
condition show on the riding bike a moment after the screen comes back (the plugin's runtime swap, about 2-4 s), and on
the parked bike by the meshes' own blending, which only the game can prove (test 59's `[Look] OverlayParked=1` is the
A/B); in which order the game draws the two see-through layers is test 59's to see (the grime is meant to hide the
paint's damage whichever comes first); the grime over a badge doesn't know the badge's art (dust along the plate's top
edge, rust along its bottom edge), and the rust on the tank's sides keeps its band round each plate; every bike draws
five more shells, invisible until chosen (about 20,700 triangles: test 59 measures the frame rate beside the parked
bike); the big gear behind the 3D Brotherhood helmet shows only round the helmet (about an eighth of it), and the
plate's Nuka-Cola cap keeps its old script (the new pen fills its letters at that size); Red and Purple light the road
at about a quarter of Warm's brightness, and Daylight is a touch warmer than Warm; the kit's preview shows the parked
bike upright with its stand down; over the list panel the wheel no longer zooms. Since 2026-11-23a: the Wear and Paint
condition go on every bike through the plugin's runtime swap (test 59: the meshes' blending alone never showed them), so
the parked bike still blinks once a couple of seconds after the kit closes, the wear on right after it, and the bike
under you can be clean for a frame or two before its swap (under the fade at a getting on); Rusty is light at riding
distance in our renders (if it is too faint now, two numbers of its tool make it stronger); the gears either side of the
helmet are smaller than 22a's flank gears (three fit a side), the right group the left's mirror image; the kit's flash
fix rests on the order test 59's log shows (the close line counts where each new bike came in). Another seat shape
later, if wanted.

## Console settings

| Command | Default |
|---|---|
| `set CMB_SpeedPercent to <100–500>` | 250 |
| `set CMB_BagCapacity to <n>` (lbs with F4SE, items without; 0 = unlimited) | 60 |
| `set CMB_CompanionMode to <0 run alongside / 1 ride along>` | 0 |
| `set CMB_UseFuel to <0/1>` | 1 |
| `set CMB_FuelDistance to <units per fuel>` (about 70 units = 1 m; lower = thirstier) | 21000 (~300 m) |
| `set CMB_RideWeapons to <0/1/2>` (MCM Riding "Weapons while riding", since 2026-11-15b: 0 None, no weapon out on the bike, a weapon out ends the ride; 1 Handguns only, the left hand on the bar (the seated pose and the put-away need the F4SE plugin); 2 Any weapon, the game's standing poses; at once; a save from an earlier build starts on 1) | 1 |
| `set CMB_AllowCombat to <0/1>` (up to 2026-11-15a the MCM's "Allow combat while riding"; since 2026-11-15b read only by an older ESP without `CMB_RideWeapons`: 0 is None, 1 Any weapon) | 0 |
| `set CMB_UseRiderPose to <0/1>` (seated riding animations, needs `CMB_RiderPose.esp`) | 1 |
| `set CMB_EngineVolume to <0–100>` | 90 (70 up to test 46's build; a save keeps its own) |
| `set CMB_MaxTilt to <0–50>` (how far the bike and the rider pitch with the ground while riding, F4SE plugin; 0 = always level, parked too; since 2026-11-22a the parked bike still leans on its side stand) | 45 |
| `set CMB_HeadlampMode to <0/1/2>` (the headlamp: off, on while riding, on at night; F4SE plugin and the Sketchfab build; the MCM hotkey switches it for the ride without changing this) | 2 |
| `set CMB_RidingCameraDistance to <units>` (F4SE plugin; the game's own is about 150) | 450 |
| `set CMB_MaxSlope to <degrees>` (steepest slope while riding, F4SE plugin; on foot the game allows 47) | 45 |
| `set CMB_TurnRadius to <units>` (tightest turn at riding speed, F4SE plugin; 0 = turn like on foot) | 180 |
| `set CMB_TurnRadiusSlow to <units>` (tightest turn at walking pace, F4SE plugin) | 50 |
| `set CMB_StandTurnRate to <deg/s>` (turning when stopped, F4SE plugin) | 60 |
| `set CMB_Caution to <50–100>` (MCM Riding "Caution (how early the bike eases off for obstacles, %)", since 2026-11-09a, F4SE plugin: lower, closer to a wall or a car before the bike eases off and stops; 100 = as 2026-11-08a; read again once a second while riding; 60 till 2026-11-09a, 50 since 2026-11-10a for a new save, a save keeping its own) | 50 |
| `set CMB_RamEnemies to <0/1>` (hostile actors the bike hits at speed are knocked over, F4SE plugin; 0 = it brakes for them as for anyone) | 1 |
| `set CMB_RamMinSpeed to <units a second>` (knocked over only this fast or faster; riding speed is about 900 at 250%; slower, the bike brakes for them) | 450 |
| `set CMB_RamDamage to <0–50>` (their damage at riding speed, percent of their max health: half that at the slowest, up to one and a half times faster; the last of it only with `CMB_RamKills`) | 10 |
| `set CMB_RamKills to <0/1>` (a knock-over that takes an enemy's last health kills it, the kill the player's; 0 = never the last point of health) | 1 |
| `set CMB_RamKillXP to <0–2>` (MCM "Kill experience", since 2026-11-02a: 1 = the bike's killing hit is your own damage spell, so the game gives its own experience for the kill; 2 = the same another way, should 1 give none; 0 = no experience, as 2026-11-01a) | 1 |
| `set CMB_RiderSteady to <0/1>` (MCM "Steady in the saddle": hits don't stagger you while riding; 0 = staggered as on foot) | 1 |
| `set CMB_RiderSteadyWay to <1/2/0>` (console only, since 2026-11-02a: the perk "Steady in the saddle" gives; 1 = `CMB_RiderSteadyPerk2`, ours with two condition tabs; 2 = the game's own `mod_armor_LessStagger` (245AFE), one step less stagger; 0 = the 2026-11-01a build's three-tab record; taken up within a second, but get off and on between ways so each ride's counts are its own) | 1 |
| `set CMB_PoseReactionWindow to <0–5>` (MCM "Pose re-check pause after a hit (s)": the rider pose isn't applied again this long after a hit, an item used or a stagger, and the Pip-Boy check is on; 0 = applied again at any standing footstep, no menu check, as 2026-10-31a) | 3 |
| `set CMB_PoseUseWindow to <seconds>` (console only, since 2026-11-02a: the rider pose is never applied again this long after an item's use, or after the Pip-Boy's or favourites' close when it was used there, so an animation mod's use clip plays whole; 0 = as 2026-11-01a) | 6 |
| `set CMB_UseCameraFix to <0/1>` (console only, since 2026-11-02a: 6 s after an item's use a camera left without its switch has its view entered again, then a message; 0 = only the log line) | 1 |
| `set CMB_RiderUseOwn to <0/1>` (console only, since 2026-11-06a, F4SE: only the Pip-Boy, the favourites and hotkeys start the item watch, so another mod's dummy potion doesn't; 0 = every potion, as 2026-11-02a) | 1 |
| `set CMB_ViewEyeUp to <-30–20>`, `set CMB_ViewEyeForward to <-30–30>` (MCM "Eye height on the bike", "Eye forward on the bike", since 2026-11-06a, F4SE plugin: your eye in first person lower (-, the bike higher into view) or higher, back (-) or forward, in game units on top of `[View] EyeAt`; at once; since 2026-11-15a `EyeAt` holds test 54's -6 and -3 already, so a save from an earlier build should set both back to 0) | 0, 0 |
| `set CMB_ViewBack to <0/1/2>` (MCM Riding "Looking back while reversing (first person)", since 2026-11-15b, F4SE plugin: backing up in first person, 0 Off, 1 Over the shoulder, 2 Third person while you back; `[View] LookBack=-1` reads it) | 1 |
| `set CMB_ViewRoll to <0–10>` (MCM Riding "View leans in turns (first person, deg)", since 2026-11-15b, F4SE plugin: degrees the view leans at the bike's whole lean, since 2026-11-16b in an ordinary turn at riding speed, a 40-degree-a-second turn (`[View] RollTurn`), up to one and a half times that in a sharp one; 0 = level, as 2026-11-15a; at once) | 4 |
| `set CMB_TailLightMode to <0/1>` (MCM "Tail lamp lights the road", F4SE plugin; 0 = the lens only glows; next time you get on) | 1 |
| `set CMB_FirstPersonBike to <0/1>` (MCM "Bike in first person", F4SE plugin; 0 = no bike in first person; next time you get on) | 1 |
| `set CMB_LookOn to <0/1>` (MCM Look "Customise at the bike", since 2026-11-07a: 0 = no Customise and the stock look, as 2026-11-06a, the bikes at the next getting on, activation of the parked bike, "Apply the look" or load) | 1 |
| `set CMB_KitMode to <0–4>` (MCM Look "Field kit", since 2026-11-07a: 0 automatic, since 2026-11-09a the armour bench then the game's own, `WorkbenchArmorA` (up to 2026-11-08a the toolbox then the armour bench); 1 the toolbox, 2 the toolbox with the armour bench's keyword (both tests: the toolbox can't be sat in), 3 the armour bench, 4 the game's armour bench (since 2026-11-09a)) | 0 |
| `set CMB_KitWorked to -1` (console only, since 2026-11-07a: the mode automatic found working, since 2026-11-09a 3 or 4 (a 1 or 2 an older build wrote is forgotten); -1 = start at the armour bench again) | -1 |
| `set CMB_KitWhere to <0/1>` (MCM Look "Field kit only in your settlements", since 2026-11-14a: 1 = Customise at the parked bike opens the field kit only in a settlement whose workshop is yours, elsewhere a message and no kit; 0 = anywhere, as 2026-11-10a; MCM "Free customising" works anywhere either way) | 1 |
| `set CMB_KitPreview to <0–2>` (MCM "Field kit preview", since 2026-11-14a, F4SE plugin: how the field kit's armour menu shows the bike, 1 New, 0 As before (2026-11-10a's view, a tyre filling the menu), 2 Tune: `CMB_KitPrevSize` (since 2026-11-15a the distance ahead of the menu's camera, 100-2000, MCM "Preview distance"; up to 2026-11-14a the size in %, as again with `[Look] KitTuneDistance=0`), `CMB_KitPrevTurn` and `CMB_KitPrevTilt` (steps of 6.4 degrees), `CMB_KitPrevUp`, `CMB_KitPrevZoomOut`, `CMB_KitPrevZoomIn`, the MCM's six "Preview ..." sliders; at the next Customise; since 2026-11-16b New is placed in the menu's view by the plugin, `[Look] KitFit`) | 1 (the sliders 1050, 7, -2, -45, -1, 3 in a new save since 2026-11-16b; 400, 7, 0, 0, -1, 3 in 2026-11-15a to 2026-11-16a; 30, 7, 0, 0, -1, 1 up to 2026-11-14a, which a save keeps: 30 then means New's 400) |
| `set CMB_LookOptions to <0–8388607>` (console only, since 2026-11-09a, without F4SE: test 51's six script switches, 1 FastMount, 2 KitHeld, 4 ParkedReload, 8 PaletteIndex, 16 MountGuard, 32 HueFree, since 2026-11-10a test 52's five, 128 KitStash, 256 KitRetry, 512 MountEarly, 1024 WornColoursFirst, 2048 HueSwap, and since 2026-11-14a test 53's two, 4096 WornIndex, 8192 KeptMods, and since 2026-11-15a test 54's two, 32768 KitDefer, 65536 MountQuick, and since 2026-11-17a test 56's 131072 KitRoom, and since 2026-11-22a test 58's three, 262144 ParkedSwapHold, 524288 OverlayRuntime, 1048576 OverlayParked, and since 2026-11-23a test 59's two, 2097152 OverlayEvery, 4194304 OverlayQuick (64 and 16384 are the plugin's own; it writes 8388607 at its defaults, 1048575 in 2026-11-22a (OverlayParked off), 262143 in 2026-11-17a and 2026-11-21a, 131071 in 2026-11-15a to 2026-11-16b, 32767 up to 2026-11-14a); 0 = all off, as 2026-11-08a; 63 = 2026-11-09a's; with F4SE `CMB_Slope.dll` writes it from `[Look]` at its start, at a load and on getting on, so set those keys instead) | 4031 (63 in 2026-11-09a) |
| `set CMB_LookHue to <0–359>` (MCM Look "Paint hue", since 2026-11-08a: the Free colour paint's hue round the colour wheel, 0 red, 120 green, 240 blue; used only with Paint "Free colour", from "Apply the look" or the next getting on or activation of the parked bike) | 210 |
| `set CMB_LookShade to <0–3>` (MCM Look "Paint shade", since 2026-11-08a: the Free colour paint's shade, 0 Deep, 1 Normal, 2 Light, 3 Pastel) | 1 |
| `set CMB_LookPlateCrude to <0/1>` (MCM Look "Crude plate texts", since 2026-11-08a: 0 = the 14 crude plate texts not offered at the field kit, and a plate wearing one shows its design's own text from the next getting on, activation of the parked bike or "Apply the look") | 1 |
| `set CMB_BrakeKey to <scan code>` (MCM "Brake key (scan code)", F4SE plugin: 57 Space, 42 Left Shift, 29 Left Ctrl, 56 Left Alt, 45 X, 46 C; 0 = none: back (S) only; next time you get on) | 57 (Space) |
| `set CMB_LookKey to <scan code>` (MCM Hotkeys "Look key (scan code)", since 2026-11-15b, F4SE plugin: held in first person on the bike the mouse turns only your head; 44 Z, 45 X, 46 C, 56 Left Alt, 256-260 the mouse buttons; W, A, S, D and the brake key refused; 0 = none; next time you get on; since 2026-11-21a the right mouse button is a second look key, `[View] LookButton` in `CMB_Slope.ini`, and either works in third person too, `LookThird`; since 2026-11-22a in third person the plugin swings the game's camera round you itself, `LookOrbit`, since 2026-11-23a with a weapon drawn too, `LookOrbitGame`) | 44 (Z) |
| `set CMB_FxVolume to <0–100>` (MCM "Bike effects volume": the landing and water sounds; 0 = none) | 90 |
| `set CMB_FxOwnSounds to <0/1>` (MCM "Bike sounds through the mod's own records", since 2026-11-02a: the landings and the water through the mod's own sound records over the game's files, heard at the riding camera's distance; 0 = the game's own records, as 2026-11-01a, much quieter: landings at once, the water next time you get on; since 2026-11-06a off is the game's own records for the landings only with "Landing sounds without metal" off, and for the water only with "Water sound loop" on its first choice ("As the 2026-11-02a build (spray)"): for test 48's A/B turn all three to their 2026-11-02a values) | 1 |
| `set CMB_FxLandRange to <0–30>` (MCM "Landing loudness range (dB)", since 2026-11-02a: how far under the hardest landing the softest one sounds; 18 = as 2026-11-01a; smaller makes small drops louder) | 10 |
| `set CMB_FxThudDb to <-40–0>` (console only, since 2026-11-06a: the dull thud under big landings, in dB, with MCM "Landing sounds without metal" on) | -11 |
| `set CMB_FxLandOn to <0/1>`, `CMB_FxWaterOn`, `CMB_FxMuteRider` (MCM "Landing sound", "Water sound" (F4SE plugin), "Mute the rider's own jump and landing sounds"; 0 = as 2026-10-31a; the last two next time you get on) | 1 |
| `set CMB_FxLandPick to <0/1>` (console only: 1 = the second set of landing sounds) | 0 |
| `set CMB_FxWaterPick to <0–3>` (console only: which water loop, next time you get on) | 0 |
| `cqf CMB_ControllerQuest FxAudition <n>`, then close the console (since 2026-11-02a it waits for the menus to close: the console pauses the game) | 0-4 the landing set, 10-14 the second set, 20-23 the water loops for 3 s, through the mod's own records; 100 more (100-104, 110-114, 120-123) the game's own records; -1 every one of ours in turn and -2 every one of the game's (14 each, 2.5 s apart, about 47 s); since 2026-11-06a -3 the landings as heard, small to big, then two into water (seven, 2.5 s apart), and 22 the wet road; at the effects volume |
| `cqf CMB_ControllerQuest EmergencyReset` | undo everything if stuck |
| `cqf CMB_ControllerQuest ForceGiveKeys` | keys, if an alternative-start mod skipped the Pip-Boy |
| `cqf CMB_ControllerQuest DecideTeleportsAtOnce 1` (a door or a fast travel decided the moment the game sends it, as up to test 40; 0 = once it's over; kept in the save) | 0 |
| `cqf CMB_ControllerQuest WatchBusy 0` (no busy watch: a keys, hotkey or bike action that hangs isn't let go after 10 s; 1 = on again; kept in the save) | 1 |

With MCM installed, all of these but the two sound picks, `CMB_RiderSteadyWay`, `CMB_PoseUseWindow`, `CMB_UseCameraFix`, `CMB_RiderUseOwn`, `CMB_FxThudDb`, `CMB_KitWorked`, `CMB_LookOptions`, since 2026-11-15b `CMB_AllowCombat`, and the commands are in *Mod Config → Commonwealth Motorbike* instead. The 2026-11-06a build adds these controls there: in Riding "Look down on getting into first person (deg)" (`CMB_ViewTip`, 20; 0 = the view left as it is, as 2026-11-02a), "Eye forward on the bike" and "Eye height on the bike" (the two above), and "Power attacks throw you off" (`CMB_KnockOffPower`, off; on = every power attack does, as 2026-11-02a); in Sound "Landing sounds without metal" (`CMB_FxLandDull`, on; off = 2026-11-02a's sets) and "Water sound loop" (`CMB_FxWaterLoop`: "Wet road (the mod's own)", the default, "Churning water", or "As the 2026-11-02a build (spray)", next time you get on). The console's `set CMB_ViewTip to 15` sets the first. The 2026-11-07a build adds the Look section (11 controls, *Customising the bike* above), the 2026-11-08a build nine
more in it (20): "Crude plate texts", "Paint hue", "Paint shade" and a choice for each of the six new slots.
The 2026-11-09a build adds "Caution (how early the bike eases off for obstacles, %)" in Riding, after "Turning
when stopped (deg/s)" (`CMB_Caution`, 50-100 in steps of 5, 60 by default; 100 = 2026-11-08a; it needs the
plugin), and a fourth choice in Sound's "Water sound loop", "Wet road, gentle", the new default ("Wet road (the
mod's own)" is 2026-11-08a's). A save from an earlier build keeps its own "Water sound loop": choose "Wet road,
gentle" there by hand. Test 51's fixes add a fifth choice to Look's "Field kit", "The game's armour bench", and the
"Paint hue" and "Paint shade" helps say that moving them chooses Paint "Free colour" at Apply. The 2026-11-10a build
makes Riding's "Caution" 50 by default for a new save (its help says so; a save keeps its own value: set 50 by hand
to try it, 60 was 2026-11-09a's default). The 2026-11-14a build adds "Field kit only in your settlements" to Look,
after "Field kit" (21 controls), and a section of its own after Look, "Field kit preview" (New, As before or Tune, and
six "Preview ..." sliders for Tune), and Riding no longer has a field of view setting (test 53: the game wrote its own
back; `[View] Fov` below). The 2026-11-15a build renames "Preview size (%)" to "Preview distance" (100-2000 in steps
of 25, 400 by default: how far ahead of the menu's camera the bike sits), "Preview zoom in" starts at 3, and the
"Field kit preview" help describes New's 400; Riding's "Eye forward on the bike" and "Eye height on the bike" are
unchanged, but `[View] EyeAt` now holds test 54's -6 and -3, so set both back to 0. The 2026-11-15b build puts the
stepper "Weapons while riding" (None, Handguns only, Any weapon (standing poses); `CMB_RideWeapons`) in Riding where
"Allow combat while riding" was (every save starts on Handguns only: the setting is new, and the old switch isn't
carried over), adds "Looking back while reversing (first person)" (Off, Over the shoulder, Third person;
`CMB_ViewBack`, Over the shoulder) and "View leans in turns (first person, deg)" (0-10 in steps of 1, `CMB_ViewRoll`,
4) to Riding after "Look down on getting into first person (deg)", and "Look key (scan code)" (0-211, `CMB_LookKey`,
44 = Z) to Hotkeys after "Brake key (scan code)". Your body in first person has no MCM switch (`[View] Body` in
`CMB_Slope.ini`). The 2026-11-16a build adds the dropdown "Seat" to Look after "Tyres" (22 controls; `CMB_Look_Seat`,
"Dark brown (as it came)" by default), and the eleven Look dropdowns list their choices alphabetically after the pinned
ones, read and set through the controller's properties `UiTankL` ... `UiFactionSet` (the globals keep the option's
number, so the console's `CMB_Look_*` values and your saves are as before). The 2026-11-16b build adds no control: the
"Field kit preview" stepper's help says New is placed in the menu's view by the plugin, and Tune's "Preview distance",
"Preview tilt" and "Preview up / down" start at New's 1050, -2 and -45 in a new save, their helps saying so (a save keeps
its own values: 400, 0 and 0 from 2026-11-15a). The 2026-11-17a build changes nothing in the MCM (its folder is
2026-11-16b's). The 2026-11-21a build adds three Look dropdowns, "Front fender badge" after "Rear fender badge",
"Wear" after "Paint shade" and "Headlamp" after "Mirrors" (25 controls; `CMB_Look_FrontFender`, `CMB_Look_Wear`,
`CMB_Look_Headlamp`, each on its first choice in a new save and an old one, read and set through the controller's
properties `UiFrontFender`, `UiWear`, `UiHeadlamp` as the others), and "Tyres" steps through the three muddy tyres
too; Look's "Headlamp" is the lamp's colour, beside the Headlamp section's mode. The free look on the right button and
the aim's block have no MCM control (`[View] LookButton`, `[Steer] AimBlock` in `CMB_Slope.ini`); `keybinds.json` is
as before. The 2026-11-22a build adds "Paint condition" to Look after "Paint shade" (`CMB_Look_PaintWear`, "Pristine
(as it came)" in a new save and an old one, read and set through the controller's property `UiPaintWear` as the
others) and takes "Front fender badge" out (25 controls still); "Headlamp" lists eleven colours, Warm first, then
alphabetical. The third-person orbit, the kit's wheel, the parked bike's stand and the attachments have no MCM control
(`CMB_Slope.ini`); `keybinds.json` is as before. The 2026-11-23a build changes nothing in the MCM (its folder is
2026-11-22a's): the bike parked beside you, its lean, the Wear on every bike, the one-handed pistol, the look with a
weapon, the holster, items in third person and the take-off have no MCM control (`CMB_Slope.ini`).

## CMB_Slope.ini (F4SE plugin): this build's new keys

**The 2026-11-24a build** answers test 60 (run on 2026-11-23b) with its fixes and your wishes after it. `CMB_Slope.dll`,
`CMB_Slope.ini`, the controller and `CMB_HotkeyF4SE` change; the ESP, the MCM and the art are 2026-11-23b's. Every new
behaviour has a key whose off value gives 2026-11-23b back (the harness's `DEF65` pins them for the older checks):

| Key | Shipped | Off (2026-11-23b) | What it does |
|---|---|---|---|
| `[Room] ParkStop` | 0.3 | 0 | a getting off holds you still from its ask and parks the bike where you stopped (test 60: 400-550 behind) |
| `[Room] ParkHold` | 0.6 | 0 | the move keys held through the black don't walk you on, for this long at most |
| `[Room] ParkSolid` | 1 | 0 | the parked bike placed again after its enable, its collision checked at once and 2 s on, put back at most twice |
| `[Room] ParkFresh` | 0 | 0 | A/B: a same-cell quick cycle's bike through the holding marker first |
| `[Room] ParkLeanClear` | 1 | 0 | the room beside you counts the bike's lean |
| `[Room] ParkFootFix` | 1 | 0 | the side stand's foot measured on the ground under it |
| `[Room] ParkFallbackSearch` | 1 | 0 | nearby spots tried in turn when the ridden track has no room |
| `[Room] GuardStuckMove` | 2 | 0 | someone unmoving in the bike's place this many seconds: the bike goes elsewhere at once |
| `[Room] SwimSpot` | 1 | 0 | after a swim the bike comes back along your way out of the water |
| `[Steer] UseItemFirst` | 1 | 0 | a use clip never cut before its item comes (test 60: 11 presses, 1 heal); presses wait their turn |
| `[Tilt] UseSeatHold` | 1 | 0 | through a third-person use clip you stay seated, hands on the grips, its props hidden |
| `[View] BodyArmsUse` | 1 | 0 | first person: the arms hidden while a use clip plays (`BodyArmsUseTail` 1.3 s after its item, 4 s at most) |
| `[View] LookAim` | 1 | 0 | first person with a weapon drawn: the look turns your aim with it, the bike keeps its line |
| `[View] AimSit` | 0 | 0 | A/B probe for the aim through the sit heading; off |
| `[View] BodyGunGripNodeless`, `BodyGunGripSpeck` | 1, shoulder | 0, joint | the first-person left arm's node-less bones found by their binds and shrunk to one point at the shoulder |
| `[View] NearThirdOff` | 70 | 0 | the near-camera stand-in ends only past this, no flicker at `NearThird` |
| `[View] LookOrbitArmed`, `LookOrbitLearn` | **0**, **0** | 0, 0 | the third-person look with a weapon drawn turning the camera round you; new and not yet reviewed, so off: 2 and 1 to try it (test 61's step 9) |
| `[View] LookOrbitClear`, `LookOrbitAbs` | 1, 1 | 0, 0 | with `LookOrbitArmed=2`: the camera kept off walls; the turn added to the game's own answer |
| `[Look] KitQuickExit` | 1 | 0 | getting on let through as the field kit's menu closes (test 60: refused 4-8 s) |
| `[Look] EquipLate` | 1 | 0 | the worn bike's colours written after the screen is back |
| `[Look] KitGuard` | 1 | 0 | the frame task's work on the kit's bike kept apart from the menu's own update; `KitLate`'s default is now 0 |
| `[Sound] LandOnce` | 1 | 0 | a flight's landing sound once |
| `[Diag] LookShots`, `QuickApplyProbe`, `GunGripBones`, `NearDrawEvery`, `OrbitWhy` | 1 | 0 | log lines: where shots go, the engine's item routes (log only), the grip's bones, the stand-in's lines once a showing, the orbit's account |
| `[Diag] UseMoveEvent`, `OrbitEachRide` | 0 | 0 | A/B and probe switches, off |
| `[Diag] APWatch` | **0** | 1 | the AP watch off by default; its line no longer calls the base value its max |

Known: with a weapon drawn and the look held in first person, followers catching up may line up by your aim, not the bike.

**The 2026-11-23b build** is 2026-11-23a plus the second review's four fixes: install this one, not 2026-11-23a (test 60
runs on it). No key is new and nothing of the art, the ESP, the MCM or `CMB_Slope.ini` changes; `CMB_Slope.dll` and two
scripts do. A stimpak from the Favourites menu right after the Pip-Boy keeps its heal: `[Steer] UseNoClip`'s Pip-Boy
window is now read from the game's own open menus, lasts 1.5 s after the Pip-Boy was last open (4 s in 2026-11-23a), and
any other menu opened since, the Favourites menu among them, ends it, so that clip plays until its item comes and is cut
then. Getting on hides a parked bike carrying the look's swap before the fade whatever `[Look] MountGuard` and
`ParkedSwapHold` say (2026-11-23a left it to 0.2 s into the fade with `MountGuard=1` and `ParkedSwapHold=0`). And two
fixes in the look's scripts: while a getting off holds the bike busy with a confirming swap overdue, the look's timer
runs no sooner than every 0.5 s (`LookRetryDelay`; 2026-11-23a every 0.05 s), and with `[Look] WornIndex=0` and
`MountQuick=1` a load keeps its own compose instead of composing again.

`Data\F4SE\Plugins\CMB_Slope.ini` holds the plugin's settings, read again each time you get on; each section's comments
say what every key does. The 2026-11-23a build answers test 59 (run on 2026-11-22a) with its fixes and your wishes after
it: every new behaviour of the plugin has a key whose off value gives the 2026-11-22a build back, and a changed
default's old value is its off value (all of the off values together are 2026-11-22a's plugin, but for one unkeyed crash
fix at the field kit, below). The art's two changes are files with their own switches (the second table). The ESP and
the MCM are 2026-11-22a's; three scripts change; the sounds and clips are 2026-11-22a's:

| Key or control | Default | Off (2026-11-22a) |
|---|---|---|
| `[Room] ParkBeside` (`CMB_RoomOptions` 65536, for the script; its ask kind 7) | 65 (units to your right, else your left; 58-200) | 0: the bike parked back along the track you rode, a bike length and a half behind you (test 59: "sometimes put far away from where I got off") |
| `[Room] ParkLean` (`CMB_RoomOptions` 131072) | 5,20 (degrees from upright, min,max) | empty: the lean 3 to 12 against the ground across the tyres (test 59: tipping away from its stand on a rise, 31 degrees over after a swim) |
| `[Room] ParkTyres` | 1 | 0: one ray at each tyre's contact (test 59: the rear tyre on a wrecked car's body) |
| `[Room] MountHide` (`CMB_RoomOptions` 262144; acts only with `[Look] MountEarly=1`) | 1 (the parked bike hidden as you press E when it carries the look's swap, else 0.2 s into the fade; no reload) | 0: 2026-11-22a's getting on: a runtime-swapped parked bike loaded again before the fade (a blink, then the fade), the bike hidden after the worn bike's equip and the camera, stood up by the controller's own thread |
| `[Look] OverlayParked` (changed; `CMB_LookOptions` 1048576, for the scripts) | 1 | 0: the parked bike's load swap alone (test 59: no Wear or Paint condition on it) |
| `[Look] OverlayEvery` (`CMB_LookOptions` 2097152) | 1 | 0: the worn bike's runtime swap dropped when its timer came before the ride had started, none on the parked bike at a getting off (test 59: the Wear at 5 of 21 getting-ons) |
| `[Look] OverlayQuick` (`CMB_LookOptions` 4194304) | 1 | 0: each runtime swap composed afresh (about 2 s), the worn bike's 1 s after its equip and tried once (test 59: clean for 2-4 s after each draw) |
| `[Look] KitLate` (acts only with `KitDrawn=1`) | 1 | 0: the drawn bike turned by the plugin's frame task alone (test 59: a frame of the menu's own pose at each option) |
| `[Look] KitPrePlace` (acts only with `KitDrawn=1`) | 1 | 0: the shown bike alone turned |
| `[View] LookOrbitGame` (acts only with `LookOrbit=1`) | 1 | 0: the orbit writes the camera every frame of a held look, whatever the game does (test 59: 95 degrees round against the orbit's 48) |
| `[View] LookRecover` | 1 | 0: the orbit's or the ease's first failed check switches it off for the session (test 59: off at the first hold, so no look with a weapon drawn) |
| `[Tilt] GunOneHand` (acts only with `GunBothBars=1`) | 1 | 0: third person, a pistol drawn while riding: both hands on the grips, the pistol in your right fist on its grip (test 59) |
| `[Tilt] GunHoldAt` (acts only with `GunOneHand=1`) | -3,-2,9 (in the bike's axes: x out, y forward, z up; each within 30) | (no off value: where your right hand holds the pistol, from where it sits on its grip) |
| `[View] BodyGunGrip` | 1 | 0: first person, your body hidden with a weapon out and the game's own arms holding the pistol in both hands (test 59) |
| `[Tilt] AttachSkeleton` | 1 | 0: only what hangs off your skins' own bones counts as on your body (test 59: the holster on 'RLeg_Thigh' never found) |
| `[Diag] AttachFresh` | 1 | 0: `AttachWhere` measures every shape as it reads |
| `[Steer] UseNoClip` | 1 | 0: in third person an item's use clip as in 2026-11-22a (a slow hotkey's clip played, a Pip-Boy use's clip left to play until the item came, your hands off the bars meanwhile, under 150 u/s nothing cut) |
| `[Steer] LaunchFrom` (changed) | 0.25 (of the top) | 0.14 (no key of its own: set it by hand, with `HeardRiseGears`) |
| `[Sound] HeardRiseGears` (changed) | 2.1,1.35,1,1,1 | 2,0.86,0.8,1,1 (by hand, with `LaunchFrom`) |

`GunHoldAt` has no off value of its own: with `GunOneHand=0` it does nothing. The three changed defaults' old values are
their off values: `OverlayParked=0`, `LaunchFrom=0.14` and `HeardRiseGears=2,0.86,0.8,1,1`, with every new key at its
off value, are 2026-11-22a's plugin (but for the field kit's unkeyed crash fix, below). The take-off has no new key: to
get 2026-11-22a's take-off back, set `[Steer] LaunchFrom=0.14` and `[Sound] HeardRiseGears=2,0.86,0.8,1,1` by hand, both
together.

The art's switches (files and the art tools' flags; each off value gives 2026-11-22a's files byte for byte):

| Switch | Default | Off (2026-11-22a) |
|---|---|---|
| Rusty's and Raider's 30 Wear maps (`wear_rusty_*` and `wear_raider_*`: `_d`, `_n` and `_s` of the static, fork, static_engine, static_exhaust and fork_black shells) | lighter, see-through, darker at the edges, nothing along a badge plate's outline | the 2026-11-22a package's 30 copied back (`look_wear.py --rust 2026-11-22a`) |
| the badge atlas (`badges_d/_n/_s.dds`: three gears either side of the 3D Brotherhood helmet) | redrawn | the 2026-11-22a package's three copied back (`bike_art.py --badges --bos-ground 2026-11-22a`, or `--through 2026-11-22a`) |

What they do:
- **ParkBeside** (your pick after test 59: getting off parks the bike beside you; test 59: "when getting off I'm
  sometimes put far away from where I got off": the bike went a bike length and a half back along your track, behind the
  camera): getting off asks the plugin once, at you along your heading: the bike's middle 65 to your right and 28 ahead
  (where the bike under you was), along your heading; room there (the box, a clear line from you), no one in its place
  (the guard, you not counted) and, with `ParkFit` on, its fit on the ground, all in one answer (a side where the tyres
  won't fit, a ledge or a drop, counts as no room); else the same on your left; neither side: the spot back along the
  track as before. The bike goes at the very spot the plugin checked, even when you get off while still rolling; with
  `ParkFit=0` the beside spot is settled as 2026-11-22a settled a checked spot (`room: ask N ... (the parked bike beside
  the player: ParkBeside): on their right ...`, a side the fit rejects `...: not fitted there (its fit's line says why):
  no room on this side`; `Parked bike beside the player (the plugin's [Room] ParkBeside, one ask): 65 to their right, 28
  ahead, ...`). One ask where 2026-11-22a made four, so the getting-off black should be shorter (test 59: 1.9-2.0 s).
- **ParkLean** (test 59: "it leans, but not always"): the lean on the stand is measured from upright, the one that puts
  the stand's foot on its ground, held to 5..20 degrees: on ground rising toward the stand it still leans 5 (the foot a
  few units into the rise), on ground falling steeply to it at most 20 (the foot just over it); getting on stands it up
  to upright, the riding bike's roll (`... leaning X on its stand from upright: roll -X`, `(its ... from upright held to
  5: the foot ... into its ground)`).
- **ParkTyres** (test 59: "sometimes one tyre is partially in the ground"; the rear tyre on a wrecked car's body at
  20:24:52): a tyre's ray that met something more than 12 over the line from the other tyre through the middle is looked
  under, and each wheel rests on the highest of its contact and the ground 8 and 16 ahead and behind it, so a curb's lip
  or a paving edge lifts it instead of it sinking in (`; the rear tyre's ray met something ... looked under it, ...`; `;
  the front tyre raised ... (its footprint)`).
- **MountHide** (test 59: "getting on and off wait time is longer than normal"): getting on no longer loads the parked
  bike again before the fade, and the bike is gone before the bike you ride goes on: when it carries the plugin's look
  swap (most getting-ons now: OverlayParked) it is hidden as you press E, before the fade (so the swapped bike is never
  drawn into the getting on: test 58's crash guard), otherwise 0.2 s into the fade, a leaning bike stood up by the
  bike's own script meanwhile, not the controller's (in 2026-11-22a its steps took turns with getting on's own). No wait
  in either case; you may see the bike vanish just before the screen goes black. A getting on that fails or is undone
  brings it back where it stood. Lines: `Getting on: the parked bike's look at the mount (ParkedSwapHold): ...: its 3D
  hidden at once, before the fade (MountHide: no reload; the bike back at the ride's end, or where it stood if the
  getting on is undone)`, or without a swap `Getting on: the parked bike hidden under the fade before the equip (the
  plugin's [Room] MountHide).`.
- **OverlayParked, OverlayEvery, OverlayQuick** (test 59: "paint effects are not visible on free standing bike"; "wears
  are showing correctly in the preview, but are not visible on the bike when outside of field kit"): the game's own swap
  at a load never draws the Wear or Paint condition, the meshes' blending or not; the plugin's runtime swap does. Now
  every bike gets it every time: the parked bike at each load (`OverlayParked`, on now), also right after getting off
  (`OverlayEvery`: 2026-11-22a refused it while the ride was ending), and the bike under you at every getting on and
  every weapon's draw or put-away (`OverlayEvery`: 2026-11-22a dropped it at 16 of 21 getting-ons). `OverlayQuick`
  reuses the look's swap as put together (no 2 s compose), puts the worn bike's on 0.1 s after its equip, under the
  getting on's fade, tries again every 0.2 s until the bike's 3D takes it, and once more a second later (a re-equip's
  first swap can land on the bike it replaces) (`Look: the worn bike's 3D: the look's swap at runtime too, N entries
  applied (OverlayRuntime, the compose reused, 0.3 s after its equip, under the getting on's fade)` and `..., the
  confirming swap)`; `Look: the parked bike's fresh 3D (its 3D's load): ... (OverlayParked, the compose reused)`). The
  parked bike still blinks once a couple of seconds after the kit closes: that reload is what gives the swap a fresh 3D
  (the crashes of tests 54 and 58 came after a swap on a parked 3D that stayed drawn), and the wear now lands with it.
- **KitLate, KitPrePlace** (test 59: "between every option bike gets into default position for a moment"): at each
  option the menu puts its new bike in at its own three-quarter pose during its own update, after the plugin's turn of
  that frame, so one frame was drawn so. `KitLate` turns a new bike right after the menu's update (its AdvanceMovie and
  PreDisplay), before the frame is drawn; `KitPrePlace` turns the bikes the menu has loaded but not shown yet too, so
  they come in turned (`kit: hold (2026-11-23a): ... the new drawn bikes: A placed right after the menu's AdvanceMovie,
  ..., M at the menu's own pose (drawn so a frame) ...`: M is 0 when the flash is gone).
- **Fixes with no key of their own** (the review of the merged build): at the field kit with `KitDrawn=1` and
  `KitFollow=0` (an A/B no test used) 2026-11-22a read values it had never set, a possible crash; 2026-11-23a writes the
  drawn bike's view there as with `KitFollow=1` (with `KitFollow=1`, the default, nothing changes). `KitPrePlace` reads
  only the menu's live loaded models and turns only models the game still holds (the visit's line counts the frames it
  found no list and the models it skipped). `BodyGunGrip` gives the old first-person shapes back when the game replaces
  its first-person 3D, and holds 24 at most (`body: the first-person 3D's left arm given back after N s (a new
  first-person 3D): ...`). The look's reused swap (`OverlayQuick`) can't outlive a save load: the swap carries a marker
  entry, `CMB\Bike\composed\<look>`, that matches no shape, and a load forgets it, so after a load the look is composed
  afresh. And during a getting on the look's timers start again only when something is due, the confirming swap at its
  own 1.0 s. These four act only with their keys on (off, 2026-11-22a's), but for an empty look timer (nothing due),
  which no longer runs, to no effect.
- **LookOrbitGame** (test 59: "right-click/Z for free camera doesn't work when gun is out in 3rd person camera"): with
  no weapon drawn the game's own free camera swings with the mouse itself, and 2026-11-22a's orbit, writing the camera
  as well, saw it 95 degrees round against its own 48 and switched itself off for the session; with a weapon drawn the
  game keeps its camera behind you, so nothing could swing it after that. Now the plugin watches each frame whether the
  game swings its camera itself and then leaves the camera to it, writing nothing; when it doesn't (a weapon drawn) the
  plugin swings it, up to 60 degrees (`view: that hold: the game swung the camera itself on N frame(s), the plugin on M
  (a weapon drawn) (LookOrbitGame)`).
- **LookRecover** (test 59: the ease back off for the session with the camera 1.4 degrees from behind): no check of the
  look switches anything off for the session; a hold the camera doesn't follow ends that hold's orbit only (`... the
  orbit tried again at the next (LookRecover)`), an ease the camera doesn't follow watches the game's own camera back,
  and a camera already behind ends the ease at once.
- **GunOneHand, GunHoldAt** (test 59: "the character isn't aiming, but she still holds the gun with both hands"; your
  pick: the left hand back on the left grip): in third person, with a pistol drawn while riding (and `GunBothBars=1`),
  your left hand stays on its grip and your right hand comes off its grip and holds the pistol over the bars at
  `GunHoldAt` from where it sat, its barrel turned along the bike's heading (75 degrees at most); the put-away brings
  the hand back onto its grip (`gun: one-handed (GunOneHand): the right hand off its grip on the hold ...; the pistol's
  barrel (its 3D's +Y) N deg off the bike's heading ..., turned onto it; its up N deg from the bike's; the left hand on
  its grip`). The shots are the game's, as before.
- **BodyGunGrip** (the same, in first person): the game draws its first-person arms in a frame of their own, so their
  left hand can't be put on the bike's grip; instead, with a pistol out your own body stays shown, its left hand on the
  grip as when riding without one, its right arm hidden, and the game's first-person right arm and pistol are drawn as
  the game draws them (draw, fire, reload, put away), its first-person left arm shrunk away (`body: first person, a
  handgun out (BodyGunGrip): your body shown, ...`; given back at the put-away, the Pip-Boy, a look back, third person
  or getting off: `body: the first-person 3D's left arm given back after N s (...)`).
- **AttachSkeleton** (test 59: "guns are still showing up in random places"): your body's skins hang on helper bones
  beside the thigh's own bone, so what your holster mod hangs off 'RLeg_Thigh' was never found as on your body; the
  skeleton's bones above the skins' now count too, with the part a skin's bone there would have, and the seat pose reads
  them, so the holster's copy follows your thigh, also in the moment right after a put-away while the plugin still holds
  your seat pose (`rider: an attachment: 'WeaponPistolUp' < 'RLeg_Thigh', ..., hangs off the skeleton's 'RLeg_Thigh'
  (... AttachSkeleton) ...`).
- **AttachFresh**: `AttachWhere`'s measures leave out the shapes the game isn't drawing as written (a copy just made, or
  hidden) and say how many (`...; left out: N not updated by the game (...), N hidden (AttachFresh)`).
- **UseNoClip** (your pick after test 59: "it would make more sense to not have any healing animation in 3rd person
  unless you can fix it"): riding in third person, a use clip is cut at its first frame, at any speed, whenever the item
  is known to be used already: a potion's number key, which the plugin now hands to the script at any speed (the item
  works at once), or a clip within 1.5 s after the Pip-Boy was last open, with no other menu since (its item is applied
  in the menu; since 2026-11-23b read from the game's own open menus, 4 s and the script's menu global in 2026-11-23a).
  Any other clip (the Favourites menu, even right after the Pip-Boy, another mod's way of using an item) plays until its
  item comes and is cut then, so the heal is never lost; an animation mod's use clip is refused at any speed. Your hands
  stay on the bars (`rider: an item's use clip at N u/s (...; the Pip-Boy open N s before them, no other cause: its item
  applied in the menu, in third person no use clip (UseNoClip)): IdleStop sent to the graph (UseStop): taken ...`;
  another: `... left to play until it is`, then `... (the item used N s into its clip, ...): IdleStop sent ...`; at the
  ride's end `quick: this ride in third person: N item use clip(s) cut at their props after the Pip-Boy, N potion key(s)
  under QuickUseAbove handed to the script (UseNoClip)`). First person as before.
- **LaunchFrom, HeardRiseGears** (test 59: "still feels a bit sluggish on take-off"; your pick: 0.3 of the top in about
  1.5 s, half in about 2.8): from rest the throttle starts at 0.25 of the top (was 0.14) and climbs evenly from there,
  the top 6.7 s after the press: 0.3 of the top after about 1.5 s, half after about 2.65 (test 59: 2.09 and 3.58, most
  of its starts from a long stand and in third person, where the game's own first second is slow). 1st, 2nd and 3rd's
  heard speed climbs faster (2.1, 1.35, 1 x HeardRise), so each gear still revs to about 3400-3500 rpm before its change
  at its band, about 12, 24, 36 and 46 on the dial (`launch: from rest: 0.3 of the top after X s, half after Y s, ...
  (the throttle from 0.25 ...)`). `LaunchFrom=0.14` with `HeardRiseGears=2,0.86,0.8,1,1` gives 2026-11-22a's take-off
  back.

Each part's settings line is in `CMB_Slope.log` at the start and on getting on: `  room (2026-11-23a, test 59):
ParkBeside=65 (...); ParkLean=5,20 (...); ParkTyres=1 (...); MountHide=1 (...): CMB_RoomOptions 65536 131072 262144
...`, `  look (2026-11-23a, test 59): OverlayEvery=1 (...) OverlayQuick=1 (...): CMB_LookOptions 8388607 for the
scripts`, `  kit (2026-11-23a): [Look] KitLate=1 (...) KitPrePlace=1 (...)`, `  look (2026-11-23a, test 59): [View]
LookOrbitGame=1 (...) LookRecover=1 (...)`, `  grip (2026-11-23a, test 59): GunOneHand=1 GunHoldAt=-3,-2,9 [View]
BodyGunGrip=1 (...)` and `  attachments and item use (2026-11-23a, test 59): AttachSkeleton=1 [Diag] AttachFresh=1
[Steer] UseNoClip=1 (...)`; the older lines now say `from rest the throttle starts at 0.25 (LaunchFrom)`,
`HeardRiseGears=2.1,1.35,1,1,1` and `OverlayParked=1 (...)`. With the off values each line says "2026-11-22a" or names
the old behaviour.

Known, left for now (test 60 asks about each):
- Getting off: the spot is your right first (the stand side towards you, in a third-person camera's view); in first
  person it is beside you, not in front; with no room either side the bike still goes back along the track, behind the
  camera. The getting-off and getting-on times can only be measured in the game (the stage line; the harness can't time
  the scripts): what MountHide takes away is the stand-up's turn-taking and the reload before the fade, not the bike's
  own equip; with the look's swap on it (usual now) the parked bike vanishes as you press E, just before the screen goes
  black.
- The lean: held at 5 on ground rising toward the stand, the foot goes a few units into the rise, and held at 20 on a
  steep fall it hangs a few units over it (a real bike there would fall over or tip): on pavement that may show; a bike
  turned to cut a steep cross slope would need the placements to choose its heading (not done). The tyres' rays still
  start 88 up, and a real step higher than 12 under one wheel is taken as a thing and looked under.
- The Wear: the bike under you is clean for the frames between its build and the swap (0.1-0.3 s, under the fade at a
  getting on); two swaps an equip (the confirming one); the parked bike blinks once at the kit's close.
- The field kit: which call of the menu puts its new bike in is inferred from test 59's log and video; if it is later
  than both the plugin's passes, the flash stays and the close line says so.
- The look: the harness's model of test 59's camera is a reading of its numbers; the plugin reads each frame whether the
  game moved the camera itself, and the hold line says which it found. With no weapon the camera is the game's while you
  hold the key with the mouse still (if the game brings it back, it comes back).
- A pistol: its barrel is taken along its model's +Y (not proven: the line gives the angle and how upright the gun ends
  up), and the hold's place `GunHoldAt` is a first set; in first person the game's right arm with your body's torso and
  left arm is two skeletons drawn in two passes, meeting at the right shoulder below the eye, and a reload's left-hand
  clip plays with that arm shrunk.
- The holster: what lay along your right forearm in test 59's picture was still there after the .44's copies were let
  go, so it may be another mod's arm gear, not the holster (the video should tell).
- Items in third person: a clip of an item used another way (the Favourites menu, another mod) plays until its item
  comes, with your hands off the bars meanwhile, as in 2026-11-22a: the cost of never losing a heal; a number key the
  plugin couldn't take is left to the game's own use, as before. (In 2026-11-23a a use from the Favourites menu within 4
  s of closing the Pip-Boy was cut early and lost its heal: fixed in 2026-11-23b.)
- The take-off: the game was fitted to test 59's pulls and the fit reads about 0.1 s slow, so about 1.55 s to 0.3 of the
  top after a long stand and 1.3 within seconds of moving; the twin (`tools/sound/engine_model.py`) keeps its
  2026-11-17a defaults.
- The art: *Customising the bike* above.
- The 2026-11-22a build's known issues (below) still hold, but for what this build fixes: the Wear on the parked and
  riding bikes, the third-person look with a weapon, the holster on the thigh, the parked bike's spot and lean.

### The 2026-11-22a build's keys (still there; off = 2026-11-21a)

The 2026-11-22a build answered test 58 (run on 2026-11-21a) with its fixes and every wish you made (art build C): every
new behaviour of the plugin has a key whose off value gives the 2026-11-21a build back, and no default changed (all of
the off values together are 2026-11-21a's plugin). Its art's new choices were an opt-in look slot and options; the files
it changed have their own switches (the second table). The ESP and the MCM changed (Paint condition in, the front fender
badge out, six headlamp colours: *Customising the bike* above), and three scripts; the sounds and clips were
2026-11-21a's:

| Key or control | Default | Off (2026-11-21a) |
|---|---|---|
| `[Look] ParkedSwapHold` (`CMB_LookOptions` 262144, for the scripts) | 1 | 0: the field kit's new look put onto the parked bike's 3D as it shows, loaded again unless you are getting on (test 58's two crashes: a Headlamp colour, then Ride at once) |
| `[Look] OverlayRuntime` (`CMB_LookOptions` 524288, for the scripts; the worn bike) | 1 | 0: the game's own swap at the worn bike's equip alone (test 58: the Wear in the kit and in first person only) |
| `[Look] OverlayParked` (`CMB_LookOptions` 1048576, for the scripts; an A/B for test 59) | 0 (1 since 2026-11-23a) | 0 (1: the look's swap at runtime on the parked bike's 3D at each load too) |
| `[Diag] LensLine` | 1 | 0: no `lens:` line |
| `[View] LookOrbit` (+ `LookOrbitGain` 0: learned while you ride) | 1 | 0: in third person the game's own camera, kept behind you while riding (test 58: "Z doesn't work") |
| `[Steer] AimStruct` | 1 | 0: the aim's handler looked for by its class name alone, which the game doesn't use (2026-11-21a: `AimBlock` and `AimWatch` never switched on) |
| `[Look] KitDrawn` (acts only with `KitHold=1`) | 1 | 0: every model of the bike the menu has held, the one it draws not looked for (test 58: the views not on screen) |
| `[Look] KitWheelDown` | 1 | 0: only the wheel's up notches counted (test 58: no zoom-out) |
| `[Look] KitWheelLists` (acts only with `KitMouse=1`) | 1 | 0: the wheel zooms anywhere and never scrolls the lists |
| `[Look] KitSlots22` (+ `KitViewPaintWear` -45,15) | 1 | 0: 2026-11-21a's slots (the front fender's view, `KitViewFrontFender` 0,25, no longer in the INI; no view of its own for Paint condition) |
| `[Tilt] AttachUnclone` | 1 | 0: another mod's copy of a shape the plugin moves held from what it carries (test 58: the holster mod's pistol in the air beside the bike) |
| `[Tilt] AttachBoneRole` | 1 | 0: an attachment moved by the names up its chain |
| `[Tilt] AttachHide` (the fallback) | 0 | 0 (1: attachments outside an equipped item hidden while riding; 2: equipped ones too) |
| `[Diag] AttachWhere` | 1 | 0: no `rider: an attachment ...` lines |
| `[Sound] UpBands` | 215,429,644,823 (u/s for a top of 900) | empty: a pull's up-shifts by the engine's own least times from wherever it began (test 58: 4th at 32 and 5th at 43 on the dial in pulls begun rolling) |
| `[Steer] MenuKeep` | 1 | 0: the speed measure falls to 0 while a menu pauses the game and the throttle is cut at the close (test 58: 470 to 223 u/s after the Pip-Boy) |
| `[Room] ParkFit` (`CMB_RoomOptions` bit 32768, for the script) | 1 | 0: the parked bike as the controller placed it, upright (test 58: "having one tire in the ground") |
| `[Room] ParkStand` (acts only with `ParkFit=1`) | 17.28,2.97,2.61 (the side stand's foot in the parked bike's frame) | empty: no lean, upright on its tyres' ground |

With `AimStruct=0` the shipped `AimBlock=1` and `AimWatch=1` find no handler in the game, as in 2026-11-21a (test 58's
`aim: no AttackBlockHandler ...` line): that is 2026-11-21a's plugin. `OverlayParked` is off by default, so the parked
bike's Wear rests on the meshes' own blending; it is test 59's A/B for that (on by default since 2026-11-23a: test 59
showed the blending alone never draws it).

The look's and the art's switches (files, choices and the art tools' flags; each off value gives 2026-11-21a's files or
forms byte for byte):

| Switch | Default | Off (2026-11-21a) |
|---|---|---|
| MCM Look "Paint condition" (`CMB_Look_PaintWear`, new; slot 15) | Pristine (as it came) | (option 0: the two Paint condition shells on their own invisible files) |
| the front fender badge (slot 13) | retired: not in the kit or the MCM, never drawn (its records kept: old saves load, a chosen badge shows none) | (an ESP from the generator's `--look-build 2026-11-21a`; not in the package) |
| the new Headlamp choices (Halogen, Daylight, Ice blue, Red, Green, Purple) | (not chosen) | any other choice |
| the five bike meshes: the Paint condition shells, the Wear's three part shells (the exhaust, the engine's covers, the fork's lowers), the wear shell over the badges, every overlay shell blending in its mesh | there, invisible until chosen | the 2026-11-21a package's five nifs copied back (`look_shells.py --paintwear 0 --parts 0 --badge-lift 0 --overlay-blend 0`; `build_bike.sh` with `PAINTWEAR=0 PART_SHELLS=0 BADGE_LIFT=0 OVERLAY_BLEND=0` and `STAND=0`); then Paint condition and the parts' wear have nothing to show on, the grime stays off the badges, and the stand is folded (set `[Room] ParkFit=0` with them: 2026-11-21a's parking, upright) |
| the parked nif's side stand | down | `look_stand.py --stand 0` (`STAND=0`): the shells' parked nif as it is, the stand folded; with `[Room] ParkFit=0` that is 2026-11-21a's parked bike (`ParkFit=0` with the shipped mesh stands it upright with its stand down) |
| the two wear shells' own files (`static_wear`, `fork_wear`, `.bgsm` and `_worn.bgsm`) | blending, invisible | 2026-11-21a's four copied back (`look_shells.py --overlay-blend 0`) |
| the Wear's 28 materials (`wear_<look>_static`, `_fork`, `.bgsm` and `_worn.bgsm`) | depth written, alpha-tested at 8 | 2026-11-21a's copied back (`look_wear.py --overlay-depth 2026-11-21a`) |
| the Wear's 18 static maps that change (`wear_<look>_static_d/_n/_s.dds`) | the grime over the tank and rear badges | 2026-11-21a's copied back (`look_wear.py --badge-grime 2026-11-21a`) |
| the muddy tyres' six diffuses (`wheelF_tyre_mud_d.dds`, `_ww_mud_d`, `_rl_mud_d` and the same `wheelR_`) | the tread's faces clean | 2026-11-21a's copied back (`look_wear.py --tyre-mud 2026-11-21a`) |
| the badge atlas (`badges_d/_n/_s.dds`: the Brotherhood helmet's gears on metallic blue, Nuka-Cola's script) | redrawn | the 2026-11-21a package's three copied back (`bike_art.py --badges --through 2026-11-21a`, or per cell `--bos-ground 2026-11-21a`, `--nuka-script 2026-11-21a`) |
| the ESP's look (all of 2026-11-22a's: Paint condition, the six colours and their beams, the Wear's part shells, the front fender retired) | 2026-11-22a's | (an ESP from the generator's `--look-build 2026-11-21a` is 2026-11-21a's, byte for byte; not in the package) |

What they do:
- **ParkedSwapHold** (test 58: "game crashed after selecting lamp color": twice, Ride pressed within 4 s of the kit's
  close while its new look was still being put together; test 54's two crashes at the kit were the same null read in the
  graphics driver): every one came a moment after F4SE's swap had put a look onto the parked bike's 3D while it was
  showing, and that 3D then stayed drawn (into the getting on; in test 54 under the kit's menu). The parked bike's look
  now goes on only by loading its 3D again with the look kept on it, never while you get on or ride (it waits for the
  next load), and a runtime swap still on the parked bike when you get on is thrown away before the screen goes black
  (`Look: the parked bike's swap holds N entries, kept for its 3D's next load, none applied to the 3D it shows (...;
  ParkedSwapHold: ...)`; at every getting on `Getting on: the parked bike's look at the mount (ParkedSwapHold): ...`).
  The Headlamp was incidental: "pick one, close the kit, hop on at once" is what put the press inside the kit's put-on.
  A getting on with a runtime swap still on the parked bike (only with `OverlayParked=1` now) loads it once more first:
  it blinks once at the press, and the stand-up starts after that load.
- **OverlayRuntime** (test 58: "wear is not visible outside of field kit menu, sometimes only in 1st person"): the
  game's own swap at a 3D's load may leave see-through layers undrawn where the shape's own mesh doesn't blend (the
  Wear's grime; the helmets and the badges, opaque, show), while F4SE's swap at runtime, the kit's and the first-person
  bike's way, shows them. The look's swap now also goes on at runtime on the worn bike after each time it goes on
  (`Look: the worn bike's 3D: the look's swap at runtime too, N entries applied (OverlayRuntime)`), 2-4 s after the
  screen comes back; it is asked again right before it goes on, after its compose, and none goes on once you are off the
  bike, busy or the look has moved on (`Look: the worn bike's runtime swap not put on after its compose: ...
  (OverlayRuntime)`). The parked bike's Wear rests on the meshes: their overlay shells blend now, so the game's own swap
  at its load should show it.
- **OverlayParked** (an A/B for test 59, off by default): the same runtime swap on the parked bike's 3D each time it
  loads (`Look: the parked bike's fresh 3D (...): the look's swap at runtime too, N of M entries applied
  (OverlayParked)`), for the case the meshes' blending alone doesn't show its Wear (TESTING's step 5). It is asked again
  right before the swap, after its compose, and none goes on while you get on, ride or use the field kit (`Look: the
  parked bike's 3D loaded (...): no runtime swap on it ..., <why> (OverlayParked; at a later load)`); a getting on
  throws one still on it away before the fade. Off by default because every runtime swap left on the parked bike is one
  a getting on has to load away first (test 58's crashes came from such a swap).
- **LensLine** (test 58's crash): at each ride's first held frame of the worn bike's headlamp lens, and when its
  material changes, a line with the lens shape, its 3D, its material file and its texture (8 a ride at most).
- **LookOrbit, LookOrbitGain** (test 58: "same with 3rd person (but Z doesn't work)": riding, the game keeps its
  third-person camera behind you, so the held look moved it 10-22 degrees): with the look key held in third person (Z or
  the right button) the plugin swings the game's camera round you itself by the mouse, as far as the first-person look
  goes (`LookMax` 150, 60 with a weapon drawn), holds it there, and eases it back behind over `LookThirdBack` (0.5 s)
  when you let go; the bike keeps its line all along. `LookOrbitGain` is how far one unit of the game's mouse input
  turns it (0: learned while you ride, test 58's 0.0159 until then; a minus sign swings the other way). Should the game
  not follow the plugin's writes, the orbit is off for the session and the look is 2026-11-21a's (`view: the
  third-person orbit not followed ...`).
- **AimStruct** (test 58: "with right-click we are aiming a gun and it's slowing bike down"; every session `aim: no
  AttackBlockHandler at PlayerControls+0x220 (.?AUAttackBlockHandler@@ there)`): the game names the handler as a struct,
  as all its input handlers, and 2026-11-21a looked for the class's name only, so `AimBlock` never switched on; with
  `AimStruct` either name is taken (`aim: AttackBlockHandler (PlayerControls+0x220, ...) ... wrapped ...`). The Pip-Boy
  is its own event and is never kept from the game, so it should open while you look ("can't open pipboy when swinging
  camera" seems to have been the game's own aim).
- **KitDrawn** (test 58: "bike doesn't spin to position to show what is being changed": the views went to two bikes the
  menu wasn't showing): the plugin asks the menu's own renderer which bike it draws and holds that one alone, so the
  view, the zoom and the turn go to the bike you see; when it can't tell, 2026-11-21a's way, with a line why (`kit:
  drawn (2026-11-22a): ...`).
- **KitWheelDown** (test 58: "it zooms in on the bike, but doesn't zoom out"): the wheel's down notch never passed
  2026-11-21a's test (its value is likely under 0); a notch is counted either way by its code now (the close line counts
  both by sign).
- **KitWheelLists** (your pick after test 58: "scroll doesn't work on menu to look through items in field kit"): with
  the cursor over the list panel (`KitListBox`) the wheel goes to the menu untouched, so the lists scroll as the game's
  do; anywhere else it zooms the bike (`KitWheelOwn` keeps it from the menu there).
- **KitSlots22, KitViewPaintWear**: Paint condition turns the bike three-quarters from a little above (-45, 15); the
  front fender badge, out of the kit, has no view (`KitViewFrontFender` left the INI; its 0,25 is still the code's with
  `KitSlots22=0`).
- **AttachUnclone** (test 58: "in 3rd person gun is being holstered to random places, often outside of the body of
  character"; your rule: "Our mod will need to work regardless of other mods installed"): your holster mod copies the
  pistol in your hand as you put it away, and the copy carried the place this plugin had given the hand's pistol (the
  seated right hand's), applied under the thigh: tens of units off your body. Every place the plugin writes on a held
  shape is now kept for 0.5 s, and a new shape that carries one of them exactly is another mod's copy: it is held from
  that shape's own place, where the other mod put it (`rider:   8 of them carried a local transform this plugin wrote on
  a held shape (...): held from that shape's own and given it (AttachUnclone)`). No mod's names in it: any mod that
  copies a shape the plugin moves.
- **AttachBoneRole**: anything hung off a bone of your body (found by the body's skin, not by names) moves exactly as
  your body's skin does at that bone, with the bike's tilt, the lean, the arms and the pose, whatever the other mod
  named its nodes (`rider: <shape> hangs off the body's bone '...' ...: the body's part there ..., not ... by the names
  on its way (AttachBoneRole)` where that changes one).
- **AttachHide** (the fallback, off): 1 shrinks such attachments that aren't part of an equipped item (a holster mod's
  copies) to a speck while riding, in third person and with your body in first person; 2 also those of equipped items (a
  backpack), never the Pip-Boy, your gun or the bike.
- **AttachWhere**: a line for each new attachment (its root, the bone of your body it hangs off, the body's part there)
  and, at 0.5 s and 2 s, where it is against the tilted bone (`rider: the attachment '...' at 0.5 s (tilted): ...`; "off
  that place" 0.000 is exact).
- **UpBands** (test 58: "overall it feels more sluggish and slower than before"; the up-shifts in full pulls at 11, 25,
  32 and 43 on the dial): like for like the pulls were as quick as test 57's, but the engine changes gear by its own
  least times from wherever a pull began, so a pull begun rolling changed into 4th and 5th early and the engine sat at
  2300-2500 rpm from 32 on the dial. In a pull (the bike gaining) a gear's up-shift now waits for the bike's band (1-2
  at 215, 2-3 at 429, 3-4 at 644, 4-5 at 823 u/s: about 12, 24, 36 and 46 on the dial), or for the gear's rpm at the
  full-throttle shift draw's top (a slow first gear), and comes there; a steady speed's gears are as before (`sound:
  gear 4 at 644 u/s, ...; at the band 644 (UpBands, held 1.20 s)`). After a long stand the first change comes a little
  under 12 (the game's own first second).
- **MenuKeep** (test 58: after the Pip-Boy at speed the bike dropped to about half and pulled again; two coast lines
  counted a menu's time): while a menu pauses the game nothing moves, so the plugin's speed measure fell to 0 and at the
  close its Lead cap cut the throttle to about a fifth; now the measure is held through the pause (`steer: a menu paused
  the game 2.4 s at 548 u/s: the speed measure held through it (MenuKeep)`) and a coast's line counts only the riding
  time (`; the game paused N s in it (a menu), not counted`).
- **ParkFit** (test 58: "it looks like bike started to 'not align' with ground it stays on when character is off of it,
  having one tire in the ground"; not a change of 2026-11-21a: the placement was as before): a park on the track you
  rode takes your feet's height a bike length and a half back, its pitch over 80 units where the tyres stand 136 apart
  and its roll from the ground's normals, so on rough or sloping ground one tyre ended 1.5-2.5 units in the ground or
  the bike 4-5 over it. After every placement (getting off, a call, a bring, after a swim, the guard's later show) the
  controller now asks the plugin about the bike's own place: rays under each tyre, both sides, the middle and the
  stand's foot give the height (both tyres on the ground), the pitch and the ground's roll (held to `ParkRoll`, 20)
  (`room: ask ... (the parked bike's fit: ParkFit): fitted: ...`; `Parked bike set on the ground under its tyres (the
  plugin's [Room] ParkFit, ...)`). The review of 2026-11-22a: the sides' and the stand's rays start 25 over the middle's
  ground (the middle's 40 over the tyres' line), so a car's hood, a ledge, a barrel or a rail beside the bike isn't read
  as the ground under it; two sides that disagree give the middle one of their two slopes and level across, and a side
  on nothing the other side's alone (`...; its sides' ground off one slope through the middle's (...): the slope across
  by its left side, the right's set aside`). A tyre's ray (or both sides') finding no ground, the MCM's tilt at 0
  (level, as every park) or a bike outside your worldspace: not fitted, and the bike still leans on its stand over the
  tilt it was placed with (`Parked bike leaning 8.6 on its side stand over the tilt its settle N gave it (not fitted by
  the plugin's [Room] ParkFit): ...`).
- **ParkStand** (your wish: "it would be cool if bike was leaning a bit on sidestand/kickstand"): the bike has its own
  side stand, folded behind the left footpeg; on the parked bike it is down now (the meshes' switch above), and with
  `ParkFit` the bike leans to its left till the stand's foot (this key: where the parked mesh has it) is on the ground
  under it: 8.6 degrees on the level, 3 to 12 against the ground across its tyres (a kerb under the foot leans it less,
  a dip more). Getting on stands it up as the screen fades (its roll back to the ground's in five steps over 0.2 s:
  `Getting on: the parked bike stood up off its side stand (...)`). Empty: upright on its tyres' ground, the stand still
  down. 2026-11-21a's look is `ParkFit=0` with `build_bike.sh`'s `STAND=0` mesh (the stand folded).

Each part's settings line is in `CMB_Slope.log` at the start and on getting on: `  look (2026-11-22a, test 58):
ParkedSwapHold=1 (...) OverlayRuntime=1 (the look's swap at runtime too on the worn bike after each equip)
OverlayParked=0 (the parked bike's load swap alone); [Diag] LensLine=1: CMB_LookOptions 1048575 for the scripts`, `
look (2026-11-22a, test 58): [View] LookOrbit=1 (...) LookOrbitGain=0 (...); [Steer] AimStruct=1 (the aim's handler by
its struct's name too, 1.11.240's)`, `  kit (2026-11-22a): [Look] KitDrawn=1 (...) KitWheelDown=1 (...) KitWheelLists=1
(...) KitSlots22=1 (...); views (heading, elevation): paint condition -45,15`, `  attachments (2026-11-22a, test 58):
AttachUnclone=1 AttachBoneRole=1 AttachHide=0 [Diag] AttachWhere=1 (...)`, `  sound (2026-11-22a, test 58):
UpBands=215,429,644,823: in a pull ...`, `  steer (2026-11-22a, test 58): MenuKeep=1: ...` and `  room: ParkFit=1: the
parked bike set on the ground under its tyres after every placement (...); ParkStand=17.28,2.97,2.61: ...`;
2026-11-21a's kit line still names the front fender's view (0,25: the code's, used only with `KitSlots22=0`), and the
worn bike's lines say 62 shapes (test 58: 57; the five new shells). With the off values each line says "2026-11-21a" or
names the old behaviour.

Known, left for now (test 59 asks about each):
- The crash: its engine reason is inferred from the logs (each crash came a moment after a look was put on a parked bike
  that stayed drawn), not read in the game; if one comes again, the mount line and the lens line say what both bikes
  carried. By default no runtime swap is left on the parked bike any more (`OverlayParked=0`); with `OverlayParked=1`
  (the A/B) it stands between rides with one on it (never put on while getting on, riding or at the kit, re-asked right
  before the swap, but drawn under the bench's menu when the kit opens beside it): a crash at the kit's opening would
  make `OverlayParked=0` the answer, and a getting on beside such a bike loads it once more first (it blinks at the
  press; about 0.1-0.2 s). With `[Look] MountGuard=0` (2026-11-09a's A/B) nothing is thrown away at the mount.
- The look: that the game keeps its third-person camera where the plugin writes it while riding is read from test 58's
  eases, not seen (the "not followed" line switches the orbit off for the session); how hard the game pulls it back
  ("the correction" in the back line) and whether the mouse reaches the game's look input in third person ("learned from
  N free frame(s)") are test 59's to say; a pad's right stick is untried.
- The field kit: which bike the menu draws is asked of a game function the plugin hasn't called before (checked against
  the menu's own name; the line says why not otherwise); a bike under a placed parent can't be held (2026-11-21a's way
  then); the wheel's down convention is inferred (the close line counts it); the list panel's box was measured on a 16:9
  screen.
- Attachments: a copy made more than 0.5 s after the plugin last wrote its source is held from what it carries; a mod
  that sets its shapes' own places every frame would fight the plugin's writes (not seen in test 58); between the copy
  and its hold (one update, 0.03 s in test 58) the copy shows where the other mod put it; `AttachHide=2` would hide a
  hat's or helmet's loose parts too.
- The drive: a pull from a long stand starts with the game's own first second (about 1.1 s to 100 u/s against 0.5
  rolling), its first change at about 10.7 on the dial; up a long climb 2nd may reach its rev ceiling before 24 on the
  dial, and 4th is held while the bike still gains; the twin (`tools/sound/engine_model.py`) has no bands.
- The parked bike: the lean's side follows the angle convention test 7 confirmed (a bike leaning right, its stand in the
  air, would say the sign is wrong); with the stand downhill on a side slope the bike leans the slope plus up to 12
  degrees (a real bike might tip); on a crest under the stand the foot can go a few units into the ground (the lean held
  at 3); the stand-up is five steps and may look stepped on a slow frame; the kit's preview shows the bike upright with
  its stand down; with `ParkStand=` or `ParkFit=0` the parked bike stands upright with its stand down, its foot just off
  the ground (2026-11-21a's look is `ParkFit=0` with the `STAND=0` mesh); the tyres' rays still start 88 up, so
  something overhanging a tyre's contact lower than that would read as its ground, and something on a true slope's low
  side lays the bike level across there.
- The art: *Customising the bike* above.
- The 2026-11-21a build's known issues (below) still hold, but for what this build fixes: the aim, the third-person
  look, the field kit's views and wheel, a holster mod's copy off your body, the Wear on the parked and riding bikes.

### The 2026-11-21a build's keys (still there; off = 2026-11-17a)

The 2026-11-21a build answered test 57 (run on 2026-11-17a) with its fixes and the tester's wishes, and brought the rest
of build B, the second art build: every new behaviour of the plugin has a key whose off value gives the 2026-11-17a
build back, and a changed default's old value is its off value (all of the off values together are 2026-11-17a's
plugin). Its art's new choices were opt-in look slots and options; the files it changed have their own switches (the
second table). The ESP and the MCM changed (the three new slots, *Customising the bike* above); the sounds and clips
were 2026-11-17a's:

| Key or control | Default | Off (2026-11-17a) |
|---|---|---|
| `[View] BodyRedraw` | 1 | 0: nothing asked of the game after your body (test 57: the bike, and four times you too, gone in third person for 2 s to a minute after your body had shown) |
| `[View] BodyRedrawHide` (acts only with `BodyRedraw=1`) | 1 | 0: the ask alone, never a hidden frame |
| `[Diag] ThirdWhere` | 1 | 0: no `third:` lines |
| `[View] LookButton` | 257 (the right mouse button) | 0: no second look key (`LookKey`, the MCM's Z, alone) |
| `[View] LookThird` (+ `LookThirdBack` 0.5 s) | 1 | 0: the look key in first person only (test 57: "Z in 3rd person doesn't work") |
| `[Steer] AimBlock` | 1 (the game's handler found only since 2026-11-22a, with `AimStruct=1`) | 0: the game aims while riding (with `LookButton=257` the right button then looks and aims) |
| `[Diag] AimWatch` | 1 | 0: no `aim:` line for an aim the game makes; with `AimBlock=0` too, nothing wrapped |
| `[Look] KitFollow` (acts only with `KitHold=1`) | 1 | 0: the menu's first model alone held (test 57: the bike side-on after E) |
| `[Look] KitSlotSettle` | 0.25 (s) | 0: the bike turned to each slot read at once (test 57: 50 turns in 8 s) |
| `[Look] KitMouse` (+ `KitListBox` 0.22,0.46,0.78,0.97) | 1 | 0: the wheel and the drag only above `KitHoldAbove` (0.55) |
| `[Look] KitWheelOwn` (acts only with `KitMouse=1`) | 1 | 0: the lists scroll with the wheel too |
| `[Look] KitNewSlots` (+ `KitViewWear` -45,15, `KitViewFrontFender` 0,25 (out of the INI since 2026-11-22a: the code's, used with `KitSlots22=0`), `KitViewHeadlamp` 0,5) | 1 | 0: the three-quarter view for Wear, Front fender badge and Headlamp |
| `[Tilt] GunHandHide` | 1 | 0: the game's copy of a holstered weapon in your right hand drawn (test 57: the pistol on the forearm, the rifle along it) |
| `[Tilt] GunAwayKeep` | 1.0 (s) | 0: a third-person put-away eased out at once (test 57: the standing clip's legs and arms for a moment) |
| `[Tilt] GunSeatKeep` | 1 | 0: the seat poses dropped when the worn bike is swapped (test 57: "running with a gun" after a first-person draw) |
| `[Tilt] GunNoteSure` (`CMB_RoomOptions` bit 8192, for the script) | 1 | 0: 2026-11-17a's note (a pistol named "not a handgun" when cycling fast) |
| `[Steer] CoastDrag` | 270,90 (u/s each second at the top, near the stop) | empty: the throttle rolls off evenly over `Coast` (2 s from the top) |
| `[Sound] HeardRiseGears`, `ShiftGapGears` (changed) | 2,0.86,0.8,1,1 (2.1,1.35,1,1,1 since 2026-11-23a); 0,1.8,2,1.7 | 2,0.79,0.65,1,1; 0,2,3,1.5 |
| `[Sound] DownBands` (changed) | 170,380,600,780 (u/s for a top of 900) | 170,400,700,860 |

The look's and the art's switches (files, choices and the art tools' flags; each off value gives 2026-11-17a's files or
forms byte for byte):

| Switch | Default | Off (2026-11-17a) |
|---|---|---|
| MCM Look "Wear" (`CMB_Look_Wear`, new; slot 12) | As it came | (option 0: the two shells on their own invisible files) |
| MCM Look "Front fender badge" (`CMB_Look_FrontFender`, new; slot 13; retired since 2026-11-22a) | None | (option 0: the patch invisible) |
| MCM Look "Headlamp" (`CMB_Look_Headlamp`, new; slot 14) | Warm (as it came) | (option 0: the shipped lens and beam) |
| the new tank, fender and tyre choices (Nuka-Cola, Red Rocket; the three muddy tyres) | (not chosen) | any other choice |
| the two wear shells and the front fender's patch in the five bike meshes, the rear fender's patch raised over the wear | there, invisible until chosen | the 2026-11-17a package's five nifs copied back (`look_shells.py --shells 0`, `build_bike.sh` with `SHELLS=0`); then a Wear or a front fender badge has nothing to show on |
| the badge atlas (`badges_d/_n/_s.dds`: Nuka-Cola and Red Rocket in two spare cells, the Enclave helmet's flag, the Brotherhood helmet's cogs) | redrawn | the 2026-11-17a package's three copied back (`bike_art.py --badges --through 2026-11-17a`, or the grounds alone `--enclave-ground 2026-11-17a`, `--bos-ground 2026-11-17a`); then Nuka-Cola and Red Rocket show nothing |
| the plates' top lines (`plates_d.dds`, `plates_s.dds`) | centred | the 2026-11-17a package's two copied back (`bike_art.py --plates --plate-top 2026-11-17a`) |
| the coloured lamps' unlit lens (`front_glow_<colour>.bgsm`) | a tinted bulb (`look_lamp.py --lens-glass tinted`) | `--lens-glass clear`: the stock lens (not in the package) |
| the ESP's look (all of 2026-11-21a's: the three slots, the new options, the eight beams) | 2026-11-21a's | (an ESP from the generator's `--look-build 2026-11-16a` is 2026-11-17a's, byte for byte; not in the package) |

What they do:
- **BodyRedraw, BodyRedrawHide** (test 57: "when swapping between 1st and 3rd person bike and even character model were
  disappearing, mostly in 3rd person"; of 22 switches to third person every one after your body had shown lost the bike,
  none of the others, and it came back only when a weapon was drawn or put away): the game draws you from a list it
  makes afresh when your 3D changes, and entering first person it made it while your body showed, the worn bike shrunk
  away. Once you are in third person with the bike plain again (after your body, or after the first-person bike stood in
  near the camera) the plugin sets the flag the game sets itself at such a change, at once and 0.5 and 2 s on, so the
  game makes the list again from the bike as it is (`body: your 3D marked changed (ScenegraphChange, bit 29 on the root)
  ... ended: third person, the worn bike plain ...`, then `body: the game took the mark ...`). If the game leaves it alone
  for 3 frames, `BodyRedrawHide` does it the game's own way, you hidden for one frame with it and shown at the next, once
  each time (a single-frame flicker at most).
- **ThirdWhere** (test 57's lines said the worn bike's flags, not where it was): at each switch from first to third
  person while riding (16 a ride) and 0.5, 2 and 4 s on, `third: ...`: whether your body showed before it, where you,
  your 3D, the bike's bone and shapes and the camera are, the camera's distance from you and from your eye, whether the
  third-person skeleton moved, and which of the bike's and your shapes the game's list holds.
- **LookButton** (your wish: "can 'free camera' when on bike be under right-click instead of Z key?"): a second look
  key beside `LookKey` (the MCM's Z), either held is the look; a scan code or 256-260 for the mouse buttons (257 the
  right one); a mouse button is read as `LookKey` is and from the game's own button events too (`view: the look key
  (Mouse 2, by the game's own button event) held ...` says only the game's events had it).
- **AimBlock, AimWatch** (your decision after test 57: "I would like to block aiming because it slows down the bike, as
  when walking"): while riding, the game's aim (its SecondaryAttack: the right mouse button, a pad's left trigger) is
  kept from it, a press begun on the bike with its holds and its release; firing and everything else stay the game's,
  and a press begun before getting on aims as usual until let go (`aim: the game's aim (SecondaryAttack, ...) pressed at
  ... kept from the game while riding (AimBlock) ...` and its release line). `AimWatch` says at its end each aim the game
  makes while riding, with the bike's speeds, and whether it slowed the bike (with `AimBlock=0` it watches only).
- **LookThird, LookThirdBack** (test 57: "Z in 3rd person doesn't work"): in third person on the bike the look key held
  (Z or the right button): the mouse swings the camera round you and the bike keeps its line (A and D still turn it);
  let go, the camera eases back behind you over `LookThirdBack` (0.5 s), the bike held meanwhile. The ease turns the
  third-person camera's own turn, which the plugin learns from your first look of the session, a swing of 10 degrees or
  more (`view: the look let go in third person ... eased back behind ... through ThirdPersonState +0x...`); until it has,
  or should the camera not follow, the bike keeps its line after you let go till you bring the camera back within 20
  degrees of it with the mouse.
- **KitFollow** (test 57: "when selecting menu for e.g. plates bike goes into default position"): in a slot's mods the
  menu loads a bike for each mod shown and draws the one you are on, while 2026-11-17a held only the first; every bike of
  ours the menu has is now held, a new one gets your view and zoom at once, and a sudden change by the menu (its putting
  a model back) is written over, never taken as a turn (`kit: hold: the menu's models (2026-11-21a): N loaded ..., the
  slot objects hang under loaded model K; ...`).
- **KitSlotSettle** (test 57: the slot read "flickering", 50 turns in 8 s): it wasn't flickering, the list's highlight
  really walked row by row under the wheel and the drags; the bike turns to a slot's part once the highlight has stayed
  on it 0.25 s.
- **KitMouse, KitListBox, KitWheelOwn** (test 57: the wheel and the drag "only first time after opening field kit"; your
  pick): the wheel zooms wherever the cursor is, and a drag turns the bike when it begins outside the lists' box (left,
  top, right, bottom as fractions of the screen, measured on test 57's pictures); inside it the menu keeps its clicks.
  `KitWheelOwn` keeps the wheel from the menu while it shows the bike (its events made events of no type, in place, while
  the menu reads them, and put back right after), so the lists don't scroll under a zoom: move in them with the arrow keys or W and S.
- **KitNewSlots, KitViewWear, KitViewFrontFender, KitViewHeadlamp**: Wear, Front fender badge and Headlamp turn the bike
  to their views (heading, elevation, as the other `KitView` keys), their attach points found by name.
- **GunHandHide** (test 57: "in 3rd pistols were just flying around when holstered, hunting rifle was placed in strange
  spots"): the game's own copy of the weapon in your right hand (the one drawn when you draw) stayed drawn on the bike
  while holstered, on the forearm or along it; while the weapon is holstered it is now shrunk to a speck, as in first
  person with your body. A holster mod's copy on the thigh or the back is drawn as before (`gun: holstered: N held
  shape(s) of the hand's weapon 3D ... shrunk to a speck (GunHandHide); the game's own: bit 0 ...`).
- **GunAwayKeep** (test 57: "character legs were spasming"): putting a handgun away in third person keeps the seat pose
  whole until the riding animation is back on the seat (the hands near the grips, the knees on the seat, two frames
  running), 1 s at most, then eases out as before (`gun: put away in third person: the seat pose kept 0.xx s until the
  clips were back on the seat (...)`).
- **GunSeatKeep** (test 57: "she was just running with a gun while having bike skirt on"): a handgun drawn in first
  person swaps the bike under you, and that swap dropped the seat poses, so back in third person she ran with the gun
  until a holstered, calm second; they are now kept over the swap, so you sit at once (`gun: the worn bike's bone is
  another now (...): the seat poses kept ... (GunSeatKeep)`).
- **GunNoteSure** (test 57: "[Form <10mm>] equipped, not a handgun" while cycling the number keys): the controller's
  "Only a handgun" note at an equip names only the weapon equipped now, judged on its own data (`CMB_RoomOptions` bit
  8192; `Weapons: ...'s equip handled after ... came: no note for it (the plugin's GunNoteSure).`).
- **CoastDrag** (test 57: "when letting go at top speed rolling distance should be twice as much as is now, with gradual
  slow down"): let go, the throttle rolls off by the speed, 270 u/s each second at the top and 90 near the stop, straight
  between: more drag at speed, less as the bike slows. From the top about twice test 57's roll (some 33 m), about 42 on
  the dial after a second, 30 after two, 20 after three, 11 after four, stopped after about 6 s; the brake stops the
  bike as before (`steer: a coast from 929 u/s (the throttle 1.00; CoastDrag 270,90): stopped after 5.76 s ...; each
  second 727, 510, 333, 188, 69 u/s`).
- **HeardRiseGears, ShiftGapGears, DownBands** (test 57: the up-shifts at 12, 26, 43 and 49 on the dial, "4th gear -
  50-50? shortest currently"; your pick, even steps): 2nd and 3rd climb a little faster for a shorter least time, 4th a
  longer one, so a full pull changes up at about 12, 24, 36 and 46 on the dial, 1.45, 3.3, 5.3 and 7.0 s after the press,
  each gear sounding as it climbs; a coast's down-shifts come a little under those (5-4 at about 780 u/s, 4-3 at 600,
  3-2 at 380, 2-1 at 170), one gear at a time over the longer roll (`sound: a stop from ... one gear at a time
  (DownBands)`).

Each part's settings line is in `CMB_Slope.log` at the start and on getting on: `  view (2026-11-21a, test 57):
BodyRedraw=1 (...) BodyRedrawHide=1 (...); [Diag] ThirdWhere=1 (...)`, `  look (2026-11-21a, test 57): [View]
LookButton=257: Mouse 2 (VK 0x02): ...; LookThird=1 (...) LookThirdBack=0.5; [Steer] AimBlock=1 (...); [Diag]
AimWatch=1 (...)`, `  kit (2026-11-21a): [Look] KitFollow=1 (...) KitSlotSettle=0.25 (...) KitMouse=1 (...)
KitListBox=0.22,0.46,0.78,0.97 KitWheelOwn=1 (...) KitNewSlots=1 (...); views (heading, elevation): wear -45,15, front
fender 0,25, headlamp 0,5`, `  weapons (2026-11-21a, test 57): GunHandHide=1 GunAwayKeep=1 GunSeatKeep=1 GunNoteSure=1
(...)` and `  steer (2026-11-21a, test 57): CoastDrag=270,90: let go, the throttle rolls off by the speed, ...`; the older
lines now say `HeardRiseGears=2,0.86,0.8,1,1 ShiftGapGears=0,1.8,2,1.7` and `DownBands=170,380,600,780`, and the worn
bike's lines 57 shapes (test 57: 54; the two shells and the front patch). With the off values each line says "as
2026-11-17a" or names the old behaviour.

Known, left for now (test 58 asks about each):
- The bike after your body: that the game makes its list afresh at the plugin's ask is read off its flags, not seen in
  its code (`the game took the mark` says whether it took it; the bike on screen whether that was enough); the hidden
  frame can show as one flicker; a part the bike had hidden at that moment (the brake light, the lamp's glow) could
  stay hidden until the next change.
- The look and the aim: whether the plugin's key reading sees the right button while the game reads the mouse (the
  game's own events cover it, the held line says which), and that the aim's handler is where the plugin looks for it
  (one line either way; without it nothing is blocked); a pad's left trigger aims no more while riding either, but is
  no look key; in third person the first look of the session teaches the plugin the camera's turn (until then the bike
  keeps its line after the release till you bring the camera back with the mouse), and which of the game's fields holds
  it is read from that look;
  no MCM switch for the button or the block (`CMB_Slope.ini`).
- The field kit: which of the menu's bikes it draws isn't read (the plugin holds them all); a gamepad turn faster than 15
  degrees a frame is dropped; `KitListBox` was measured on a 16:9 screen; a long list scrolls only by the keys while the
  kit shows the bike.
- Weapons: a holster mod's copy shows in its holster at the put-away and is tilted with you from the next tenth of a
  second; after a first-person draw the bike under you can jump once when the script swaps it back; whether the game
  itself hides the hand's copy on the bike is one log line's to say.
- The drive: the coast's last second may be a little shorter in the game than in the harness; 5-4 comes close under the
  pull's 4-5 (`DownBands=170,380,600,760` is the A/B if it lands above 46 on the dial); 2nd still varies a little from
  pull to pull; a side key alone near the end of a coast creeps up to about a second later than before.
- The art: *Customising the bike* above.
- The 2026-11-17a build's known issues (below) still hold, but for what this build fixes: the bike in third person
  after your body, a holstered weapon in the hand, the seat pose after a first-person draw, the handgun note.

### The 2026-11-17a build's keys (still there; off = 2026-11-16b)

The 2026-11-17a build answered test 56 (run on 2026-11-16b) with its fixes and its art corrections: every new behaviour
of the plugin has a key whose off value gives the 2026-11-16b build back, and a changed default's old value is its off
value (all of the off values together are 2026-11-16b's plugin). Its art corrections were eight textures, with their own
switches (the second table); its meshes, materials, sounds and clips were 2026-11-16b's, and so were its ESP and MCM:

| Key or control | Default | Off (2026-11-16b) |
|---|---|---|
| `[View] CameraEase` (acts only with `CameraPlace=1`) | 1 | 0: CameraPlace's probe as 2026-11-16b (test 56: "EyeAtCamera off this session" 84 ms into first person, BodyFollowCamera off with it) |
| `[View] NearHandover` | 1 | 0: near the camera in third person a handover's old first-person bike hidden at once (test 56: the bars and dial gone 0.6 s) |
| `[View] BodyNodes` | 0 | 1: bit 0 on the worn bike's and the weapon's nodes while your body shows (test 56: the bike not drawn in third person afterwards, "crazy frog") |
| `[View] BodyArmsLook` | 30 (deg) | 0: the game's first-person arms hidden only past `BodyArmsBack` (90) (test 56: a second arm with the look key) |
| `[View] BodyEye`, `BodyLeanMax` (changed) | 0,6,-3; 40 (deg) | 0,2,-0.5; 35 (test 56: the eye in the outfit's collar, its inside seen looking down) |
| `[Diag] BodyWornLine` | 1 | 0: no `body: the worn bike as the showing ends` lines |
| `[Tilt] GunCheckUnpaused` | 1 | 0: the weapon state's 6-s check against the script counts real seconds (test 56: the Pip-Boy right after a put-away switched the weapon rules off for the session) |
| `[Tilt] GunCheckRecover` | 0.5 (s) | 0: a failed check turns the weapon rules off for the session |
| `[Tilt] DrawHandgunOnly` (`CMB_RoomOptions` bit 2048, for the script) | 1 | 0: the game draws a rifle, then it is put away (test 56: out 0.4-1.9 s) |
| `[Tilt] QuickHolsterFirst` | 1 | 0: a rifle's number key with a pistol out swaps the rifle in drawn, then it is put away |
| `[Tilt] GunJudgeWait` (`CMB_RoomOptions` bit 4096, for the script) | 1 | 0: a weapon drawn with none equipped at that moment judged at once (test 56: the .44 put away as "not a handgun") |
| `[Tilt] NodelessOnce` | 1 | 0: the hands' finger bones without a node of their own judged again at every hold |
| `[Tilt] SkinArraysCheck` | 1 | 0: a held part's bone lists read as they were at its hold |
| `[Diag] HeldWhere` | 1 | 0: no `the new plain shapes hang off` and `sits D from that hand` lines |
| `[Look] KitHold` (+ `KitZoom` 0.6,3,1.12, `KitDrag` 0.25,0.25, `KitHoldAbove` 0.55; acts only with `KitFit=1`) | 1 | 0: the menu's own turn about the bike's bottom, no zoom (test 56) |
| `[Look] KitSlotView` (+ `KitTurnTime` 0.35, `KitViewRear` -165,10, `KitViewTankL` -90,10, `KitViewTankR` 90,10, `KitViewSeat` -60,60, `KitViewFender` -150,40, `KitViewWheels` -80,3; acts only with `KitHold=1`) | 1 | 0: one view (the menu's three-quarter), the turn and the zoom as `KitHold` |
| `[Look] KitRoom` (`CMB_LookOptions` 131072, for the script; + `KitRoomRing` 20, `KitRoomBench` 60 for the armour bench's place) | 1 | 0: the field kit's spot never checked (test 56: "pushes me through the wall") |
| `[Steer] LaunchFrom` (changed) | 0.14 (of the top; 0.25 since 2026-11-23a) | 0.1 |
| `[Sound] DownBands` (+ `DownBlend` 100) | 170,400,700,860 (u/s for a top of 900; 170,380,600,780 since 2026-11-21a) | empty: a stop's down-shifts by `SpeedMap`'s speed (test 56: late, a third of them skipping a gear) |
| `[Sound] HeardStop`, `HeardBrake` (changed) | 900, 1500 (u/s a second) | 300, 600 |

The art's switches (files and the art tools' flags; each off value gives 2026-11-16b's files byte for byte):

| Art | Default | Off (2026-11-16b) |
|---|---|---|
| the four plate designs (`plates_d/_n/_s.dds`, `plate_p.dds`: the Brotherhood of Steel, Minutemen, Nuka-Cola and Red Rocket emblems, gold a seventh fixed colour, Red Rocket's own row yellow) | redrawn | the 2026-11-16b package's four copied back (`bike_art.py --plates --plate-emblems 2026-11-16a`); `plate_text_*` and every material are unchanged either way |
| the badge atlas (`badges_d/_n/_s.dds`: the Gunners skull's flag patch, the Brotherhood of Steel colour emblem, the Enclave helmet's chrome ground) | redrawn | the 2026-11-16b package's three copied back (`bike_art.py --badges --through 2026-11-16a`, or one at a time `--gunskull-art 2026-11-16a`, `--bos-art 2026-11-07a`, `--enclave-ground 2026-11-16a`); `--through 2026-11-08a` still gives 2026-11-15b's |
| the seat palette (`seat_p.dds`: Saddle tan) | a76239 | bf7028: the 2026-11-16b package's copied back (`look_seat.py --seat-colours 2026-11-16a`) |

What they do:
- **CameraEase** (test 56: "bike still shakes too much", the body "shaking a lot more than bike", and in the log
  "EyeAtCamera off this session" 84 ms into the first first-person ride, before CameraPlace had looked at all its
  readings): riding, your game's camera trails your place by about 67 ms of your speed (63 units at 950 u/s), its height
  following the bumps late the same way: it eases toward your place + the game's answer, so none of CameraPlace's
  readings was the camera. The plugin now also reads the camera eased that way (learning how fast it eases), the camera
  as it stands and two more; nothing is moved until one of them matches the camera better than the frame's guess (`camera:
  the camera root at GetTranslation's answer read as the camera root eased toward the player's place + the answer at call
  1 (its time constant ... ms) ...`, once); if none does, or the kept one stops matching, a line says so and the bike is
  placed by the frame's guess until one matches again: never off for the session. Your body follows the same place
  (`BodyFollowCamera`, off all of test 56 with it). The `view: lock:` lines end `; CameraEase: ...: the kept reading off
  the camera root at the next task ..., the Lead's guess ...`.
- **NearHandover** (test 56, 12:53:21: zoomed in to your head in third person, the bars and the dial gone for 0.6 s
  while the plugin handed the first-person bike over to a new one, which the game fades in): the old one stays drawn
  there with the new one until the handover ends, as in first person.
- **BodyNodes, BodyWornLine** (test 56: "when bike is visible in 1st, it stops being in 3rd - looks like crazy frog",
  until getting off or a draw swapped the bike's 3D): entering first person the game marks your 3D's tree changed and
  makes afresh what it draws of it once it draws it again, which is the first frame your body shows, when 2026-11-16b
  had just set the hidden flag on the worn bike's and the weapon's nodes: the bike was left out of what the game draws,
  and clearing the flag later didn't bring it back. With `BodyNodes=0` no node's flag is written: the worn bike's and
  the weapon's shapes are shrunk to a speck alone (as when zooming in, one bike), so the bike is drawn again the moment
  your body stops showing. `BodyWornLine` says in what state the worn bike was left: `body: the worn bike as the showing
  ends (...): ...` on that frame and `body: the worn bike 0.5 s after the showing ended (...): ...` (its shapes' flags,
  any speck left, the culling spheres, the nodes above them, the player's root).
- **BodyEye, BodyLeanMax** (test 56: "I was able to look into character model when looking down"): at 0,2,-0.5 the
  camera sat at the head's joint, right over the opening of your outfit's collar. At 0,6,-3 it sits at your face, about
  6.5 ahead of the joint once your upper body is pitched, the neck and collar behind it and your chest below and ahead;
  `BodyLeanMax` 40 lets the pitch take that, the body moved about as little as before (2 back and down), the upper body
  leaning back about 5 degrees more.
- **BodyArmsLook** (test 56: a second arm with the look key at about 85-90 degrees, hidden and shown nine times in six
  seconds): the game's own first-person arms are hidden while you look further aside than 30 degrees (the look key, the
  look back), back under 25, unless a weapon is out or an item is being used (then `BodyArmsBack`'s 90, as before).
- **GunCheckUnpaused, GunCheckRecover** (test 56, 12:53:08: the .44 put away, the Pip-Boy a second later, and the
  check of the game's weapon state against the script's word, 6 s apart, counted through the pause: "the weapon rules
  here off for the session", the seated pose with them, so test 56's steps 25-26 ran without them): the check counts only
  while the game runs (as the put-away's own seconds since 2026-11-16b), and if it fails anyway the rules come back once
  the two agree again for 0.5 s (`gun: ... the weapon rules back on (...; switched off N time(s) this session)`; five
  times in a session and they stay off).
- **DrawHandgunOnly, QuickHolsterFirst** (test 56: "it shouldn't even be pulled out"; your pick: never drawn): riding
  with "Handguns only", the game's draw of a weapon the plugin judges not a handgun (as the script does: the handgun
  list's keywords, or the pistol keyword, on the weapon or its instance; one it can't read is let through) is refused: it becomes your weapon but stays
  holstered, ready when you get off, and the controller says "Only a handgun can be used on the motorbike." when it is
  equipped (`CMB_RoomOptions` bit 2048). A rifle's number key while a weapon is out puts that weapon away first, then
  gives the key to the game, so the rifle comes holstered. The plugin stops the game's own draw call (the player's
  slot 0xC9, the put-away's); a rifle that comes out some other way (the Pip-Boy with a weapon out, the favourites
  menu) is put away after, as in test 56, with its own line, and each ride's line on getting off counts the draws
  (`gun: this ride the game asked N draw(s) through slot 0xC9: ...`).
- **GunJudgeWait** (test 56, 12:51:32: the .44 by its number key put away as "not a handgun", the 10mm's unequip
  handled before the .44's equip): a weapon drawn while none is equipped at that moment is judged again 0.3 s later
  (`CMB_RoomOptions` bit 4096; `Weapons: ... judged again in 0.3 s (the plugin's GunJudgeWait).`).
- **NodelessOnce, SkinArraysCheck, HeldWhere** (test 56: "after holstering weapon on bike in 3rd person, in 1st fingers
  are elongated"): the finger bones with no node of their own get their hand at their own part's hold only, not again
  whenever another shape (a weapon's) is held mid-equip; and a held part whose bone lists the game rebuilt is held again,
  so no finger is read through a list the game let go of (each a way the plugin itself can draw a spike; which one test
  56 had, the log can't say). `HeldWhere` names where new held shapes hang (a holster mod's second copy shows as one)
  and a finger found far from its hand.
- **KitHold, KitSlotView, KitRoom** and their parameters (test 56: no zoom, the bike grabbed only by its front wheel,
  a view per slot wished for, pushed through a wall): *Customising the bike* above (`kit: hold (2026-11-17a): the menu's
  bike (item ...) held about its centre ...` at each Customise, `kit: slot: ...` once a visit, `kit: hold: the slot
  '...' (from ...): ...` at each slot, `kit: hold: ... the menu closed after N frame(s): ...` at the close; `room: ask N
  ... (the field kit's spot: KitRoom): ...`).
- **LaunchFrom** (test 56: "takeoff is a tad too slow, beside that it was ok"): from rest the throttle starts at 0.14 of
  the top and climbs evenly from there as before, so the first second is a little quicker and the rest of the pull about
  0.36 s sooner: 0.3 of the top after about 1.9 s (2.2-2.4 in test 56), 2nd at about 12 on the dial, each gear's sound
  as before.
- **DownBands, DownBlend, HeardStop, HeardBrake** (test 56: "shifting down when being slowed down or stopping is
  sometimes weird, not natural": 32 of 96 down-shifts skipped a gear, a stop from the top going 5-4 at about 490 u/s,
  4-3 at 100-245, then the clutch from 3rd): with the throttle shut the engine shifts down by the speed it hears, and
  `SpeedMap` fed it the bike's speed plus about 245 through 2nd and 3rd, so the down-shifts came far under the pull's own
  up-shifts, late and bunched. Now a stop feeds it a map of its own, so the down-shifts come near the bike's 860, 700,
  400 and 170 u/s (5-4, 4-3, 3-2, 2-1), a little under the pull's up-shifts (from the top a little later: about 745,
  583, 398 and 169 in the harness's game, test 56's fitted); it comes in as the bike slows (`DownBlend`: all of
  it 100 u/s under the speed at the let-go, so a lift with the speed holding is as before), and the heard speed keeps up
  (`HeardStop` 900, `HeardBrake` 1500). A coast from the top: four shifts one gear at a time, each one blip, 0.4-0.55 s
  apart, the clutch near the stop; a hard brake: a shift or two and the clutch takes the rest, a hard stop. Each stop gets
  a line: `sound: a stop from 877 u/s in gear 5, 2.11 s to the clutch: 5-4 at 744 (a blip), ..., the clutch in at 49 u/s
  from gear 1; one gear at a time (DownBands)`.

Each part's settings line is in `CMB_Slope.log` at the start and on getting on: `  view (2026-11-17a, test 56):
BodyNodes=0 (...) BodyArmsLook=30 (...); [Diag] BodyWornLine=1 (...)`, `  view (2026-11-17a, test 56): CameraEase=1 (...)
NearHandover=1 (...)`, `  weapons (2026-11-17a, test 56): GunCheckUnpaused=1 GunCheckRecover=0.5 DrawHandgunOnly=1
QuickHolsterFirst=1 GunJudgeWait=1 NodelessOnce=1 SkinArraysCheck=1 [Diag] HeldWhere=1 (...)`, `  kit (2026-11-17a):
[Look] KitHold=1 (...) KitSlotView=1 (...) KitTurnTime=0.35 KitZoom=0.6,3,1.12 KitDrag=0.25,0.25 KitHoldAbove=0.55; views
(heading, elevation): rear -165,10, tank L -90,10, tank R 90,10, seat -60,60, fender -150,40, wheels -80,3; KitRoom=1
(...) KitRoomRing=20 KitRoomBench=60` and `  sound (2026-11-17a, test 56): DownBands=170,400,700,860 DownBlend=100: ...`; the older lines
now say `from rest the throttle starts at 0.14 (LaunchFrom)`, `HeardStop=900 HeardBrake=1500`, `BodyEye=(0, 6, -3)
BodyLeanMax=40` and `CMB_LookOptions 262143`. With the off values each line says "as 2026-11-16b" or names the old
behaviour.

Known, left for now (test 57 asks about each):
- First person: CameraEase rests on test 56's numbers (the camera eased toward your place + the game's answer, a time
  constant of about 72 ms); if your game's camera doesn't ease so, the plugin says so loudly and places the bike by the
  frame's guess, as in test 56, while it goes on looking. Your body following the camera rests on your 3D being
  updated before the camera (the lock line's skeleton part says). The worn bike's return in third person rests on a
  reading of the game's flags (its drawing isn't visible from the plugin); if it still goes, the two body lines say
  what of the plugin's is left on it. Backing over the shoulder still hides your body (`BodyBack` 100; `BodyBack=0` is
  the A/B), and it can flicker when the look hovers there.
- Weapons: whether every draw goes through the call the plugin stops is the ride's count line's to say; a rifle that
  comes out another way (the Pip-Boy or the favourites menu with a weapon out) is put away after, as in test 56; R with
  a rifle equipped while riding does nothing, silently (the message comes when it is equipped); a handgun drawn in first
  person still swaps the worn bike for the planted one (the controller's armour choice, as at each first-person draw of
  test 56); which of the two causes made test 56's spikes isn't known (HeldWhere's lines say); a holster mod's second
  copy of a holstered weapon is held and tilted like the game's own.
- The field kit: the menu's slot fields and its input through MenuControls are read in a game for the first time (the
  `kit: slot:` and close lines say what yours gives; the views fall back on the shown mods' names); dragging by the
  menu's own grab may jitter for a frame; with no room at its spot the kit is set out where you stand and may overlap
  the bike or a wall; the bike's other side isn't tried (the line from you to it crosses the bike).
- The drive: a stop's first down-shift comes about 0.7 s after the let-go (`[Sound] StopAfter=0.15` is an A/B); from a
  cruise the first shifts catch up from the cruise's taller gear, one every 0.4 s; a hard brake ends with the clutch
  from 3rd; a lift and press at a steady speed may now leave the engine a gear or two lower than in test 56 once the bike
  has slowed 100 u/s.
- The art: the Nuka-Cola cap is the plate's own red and reads faintly from riding distance; on Red Rocket's own
  background a thin yellow line can show round the black rim; the Enclave helmet's chrome at night is the renders'
  guess.
- Not changed in this build: the stutter across cells (test 56: a cell move made a long frame about 1.5 times as likely
  just after it, but 84% of the long frames came elsewhere; `ParentKeep=0` untried), getting on after a change at the
  kit (5.8-6.1 s, about 2.4 s more than with the look unchanged), the occasional frame-rate drops, VATS off on the bike.
- The 2026-11-16b build's known issues (below) still hold, but for what this build fixes: CameraPlace switching itself
  off, NearThird's handover, the worn bike's nodes, `BodyEye`, the rifle drawn before its put-away, the take-off.

### The 2026-11-16b build's keys (still there; off = 2026-11-16a)

The 2026-11-16b build answered test 55 (run on 2026-11-15b) on top of 2026-11-16a's art: every new behaviour has a key
whose off value gives the 2026-11-16a build back (whose plugin is 2026-11-15b's, byte for byte), and a changed default's
old value is its off value. Its meshes, textures and materials were 2026-11-16a's:

| Key or control | Default | Off (2026-11-16a) |
|---|---|---|
| `[View] CameraPlace` | 1 | 0: GetTranslation's answer read as `CameraWorld` reads it (test 55: EyeAtCamera turned itself off at once, the shake) |
| `[View] NearThird` (+ `NearFade` 0.99) | 60 (units from your eye, 0-200) | 0: the first-person bike hidden in third person however near the camera (test 55: no bike for about half a second zooming in) |
| `[View] ParentKeep` (+ `ParentMargin` 256) | 1 | 0: the first-person bike moved under your cell's node at once, and put back and moved again at every cell crossed |
| `[View] RollTurn` | 40 (deg/s) | 0: the view's lean by the bike's lean (0 or the whole slider in a turn at speed) |
| `[View] LookPitch` | 45 (deg) | 0: the look back's pitch the game's own |
| `[View] BodyWorn` | 1 | 0: with your body shown, the worn bike's shapes only flagged hidden (test 55's second bars and speedometer) |
| `[View] BodyWeapon` (+ `BodyWeaponNodes` WEAPON) | 1 | 0: the third-person weapon left as the game has it (test 55: the holstered gun on the right grip) |
| `[View] BodyNear` | 20 (units) | 0: only the head's bones shrunk away (test 55: an outfit piece in front of the eye) |
| `[View] BodyArmsBack` | 90 (deg) | 0: the game's first-person arms never touched (test 55: hanging in view when looking back) |
| `[View] BodyEye` (changed) | 0,2,-0.5 (0,6,-3 since 2026-11-17a) | 0,7,7 |
| `[View] BodyFollowCamera` (acts only with `CameraPlace=1` and `Body=1`) | 1 | 0: your body placed once a frame by the plugin's task, before the camera's update |
| `[Steer] FirstKeys` (changed) | 0.45 | 1 (0, as before: A and D step sideways in first person) |
| `[Diag] ParentTime` | 1 | 0: no Parent line on getting off |
| `[Diag] BodyDrawn` | 1 | 0: 2026-11-16a's `body: drawn?` line |
| `[Tilt] PutAwayProbe` | 1 | 0: on the player nothing called (test 55: "0 calls", the sheathe action after 1 s) |
| `[Tilt] PutAwayUnpaused` (`CMB_RoomOptions` bit 1024, for the script) | 1 | 0: the put-away's seconds in real time (test 55: a save right after the ask ended the ride) |
| `[Tilt] GunRootFrame` | 1 | 0: the gun pose reads the bones against the task's root |
| `[Tilt] GunBothBars` | 1 | 0: a handgun out, the game's right arm carried to the seat's shoulder |
| `[Tilt] GunCarry` | 1 | 0: the drawn gun where the game's standing clip holds it |
| `[Tilt] GunStillRide` | 1 | 0: drawn above 120 u/s before a riding seat pose is read, not posed (the standing clips, the planted bike) |
| `[Tilt] GunPredictMax` | 15 (units) | 0: no limit on what GunPredict carries on |
| `[Look] KitFind` | 1 | 0: the menu's bike seen only by its item (one line a visit, at a change) |
| `[Look] KitFit` (+ `KitFitView` 40, `KitFitBox` 0.07,0.50) | 1 | 0: the menu places the bike from the record |
| `[Look] KitPreviewPos`, `KitPreviewTurn` (changed; commented out: the defaults) | 0,1050,-45; -0.223219,0,0.785398 | 0,400,0; 0,0,0.785398 |
| MCM "Field kit preview" Tune's "Preview distance", "Preview tilt", "Preview up / down" (the ESP's `CMB_KitPrevSize`, `CMB_KitPrevTilt`, `CMB_KitPrevUp`) | 1050, -2, -45 in a new save | 400, 0, 0 (a save keeps its own: set them by hand) |
| `[Steer] PullTime`, `PullFrom`, `LaunchFrom` (changed) | 8 (s), 0.1, 0.1 (of the top; `LaunchFrom` 0.14 since 2026-11-17a, 0.25 since 2026-11-23a) | 5.5, 0.6, 0.25 |
| `[Steer] PullClimb` | 1 | 0: the climb's push at a log built at the pull's rate too |
| `[Sound] SpeedMap` | 225:480,430:700,680:910,935:935 | empty: the engine hears the bike's own speed |

What they do:
- **CameraPlace** (test 55: the shake back, `camera: EyeAtCamera off this session` at the first frame): the game's
  camera answer is your eye's offset from your own place, not a world place, and the camera reads your place at its own
  moment, up to three times a frame. The plugin now matches the camera's place against each way of reading the answer,
  for each of the game's calls in a frame, keeps the one that fits (`camera: the camera root at GetTranslation's answer
  read as the player's place + the answer (call 1 of 3 since the task; 0.00 from it; ...)`), and moves the first-person
  bike at that call (settled on a later call, the earlier calls of a frame move it too, so a frame with fewer calls is
  drawn at its last one). If none fits, EyeAtCamera turns itself off as before, the line giving every reading's distance.
- **BodyFollowCamera** (the build's review): with CameraPlace the first-person bike moves at the camera's own update,
  after the plugin's task has put your body on it. At that update your body now gets the camera's move since the task
  less what its own skeleton moved since the task, so the hands stay on the grips of the bike you see; the lock line ends
  `; BodyFollowCamera: N move(s) of your body X (median) / Y (most), its skeleton's own since the task A of the camera's
  B (medians)`, which tells test 56 which case holds (A about B: the skeleton carries the body; A about 0: this key does
  the work).
- **NearThird, NearFade** (test 55: zooming in with the wheel, the game fades you and the worn bike before it switches to
  first person): while the third-person camera is within 60 of your eye on the bike, or you are faded, the first-person
  bike shows in the riding bike's own place and the worn bike is hidden, shrunk away as with your body when `BodyWorn` is
  on: one bike, never two (`view: third person with the camera 35 from your eye (the player's fade 0.40): the view bike
  ... shown at its own place, the worn bike hidden ...`, then `... over after 0.45 s (first person)`).
- **ParentKeep, ParentMargin, ParentTime** (test 55's first-person stutter: 196 moves of the first-person bike between
  cells' nodes, 144 of them a put-back and a move again at every cell crossed): the bike is moved only once it nears its
  cell's edge (256 inside the cell's box), and from then on straight from cell to cell. On getting off one line times the
  moves and counts the slow frames after them against the rest of first person (`view: Parent: this ride N move(s) ...`),
  so test 56 says whether a move costs a frame.
- **RollTurn** (test 55: "didn't see any difference between changed numbers"): the view leans the MCM's "View leans in
  turns" degrees in a 40-degree-a-second turn at riding speed, in proportion (at most one and a half times), none under
  150 u/s or backing. It followed the bike's lean, which is 0 or the whole MaxLean in a turn at speed.
- **LookPitch** (test 55: the mouse's vertical did nothing while looking back): looking back over your shoulder the mouse
  tilts the view up and down, up to 45 degrees, eased back level when you ride forward; the look key alone is as before.
- **FirstKeys** is 0.45 of the turning limit (your pick after test 55).
- **BodyWorn, BodyWeapon, BodyWeaponNodes, BodyNear, BodyArmsBack, BodyEye, BodyDrawn** (test 55: a second set of bars
  and a speedometer riding ahead of the first, a gun on the right grip, a rusty piece of the outfit in front of the eye,
  the first-person arms hanging in view looking back): the game draws the worn bike's shapes even with their hidden flag
  set, so while your body shows they are shrunk to a speck and the worn bike's nodes hidden (`BodyWorn`); the weapon in
  your hand or a weapon slot likewise (`BodyWeapon`; `BodyWeaponNodes=WEAPON`, a holster mod's node can be added); an
  outfit piece near your eye with no sleeve or glove in it is shrunk whole (`BodyNear=20`; sleeves, gloves and the
  Pip-Boy stay); the game's first-person arms are hidden while you look more than 90 degrees back (`BodyArmsBack`; in another camera,
  VATS or getting off's, they stay hidden, `body: the first-person 3D kept hidden in another camera (...)`, and are given
  back at the next first-person frame); and
  your eye sits where the game's own is, 2 ahead of the head's joint and 0.5 below it (`BodyEye=0,2,-0.5`, test 55's
  probe; 0,7,7 was a guess that sank the body into the seat). The "drawn?" verdict is gone (nothing the plugin reads
  tells it): `body: hidden with the body: ...` at each showing and `body: shown ... s: ...` instead (`[Diag] BodyDrawn`).
- **PutAwayProbe, PutAwayUnpaused** (test 55: "0 calls" at every put-away; a save right after the ask ended the ride):
  the player has its own heading function in the slot the probe checks, which calls the actor's; the probe now takes
  that form too, with both checks it needs, so the game's own put-away is called on you (`gun: the player's slot 0xC7
  ... is PlayerCharacter's heading ...`). The put-away's seconds (the plugin's 4 s of calls, and through `CMB_RoomOptions`
  bit 1024 the script's sheathe at 1 s and the ride's end at 3 s) count only while the game runs, so a save or a menu
  right after the ask no longer ends the ride (`Weapons: still out 1.0 s after the ask; 4.3 s more with the game paused,
  not counted: ...`).
- **GunRootFrame, GunBothBars, GunCarry, GunPredictMax, GunStillRide** (test 55: "the right arm swings out", the pistol
  never in the posed hand, a jerk at a draw, the standing pose drawn at speed right after getting on): with a handgun
  out in third person the seated pose reads the bones against the 3D root they were animated with (the game moves the
  root a frame ahead of the bones: 25-36 units a frame at speed in test 55; checked once a session, `gun: ... the root a
  frame ahead of the bones ...`); both hands stay on the bars and the drawn gun, which isn't on the rider while drawn, is
  carried from the game's right hand into the posed one (no one-handed aiming pose yet); a bone's jump over 15 in a frame
  (the clips' switch at a draw) isn't carried on into the next; and drawn at speed before a riding seat pose is read, the
  still one taken at getting on serves, so you are seated at once and the bike under you isn't swapped.
- **KitFind, KitFit, KitFitView, KitFitBox, KitPreviewPos, KitPreviewTurn** (test 55: "half of the bike was in view"):
  *Customising the bike* above (`kit: fit (2026-11-16b): the menu's bike (item ...) moved from (...) to (...) ...` at
  each Customise, `kit: fit: ... the menu closed after N frame(s): ...` at the close).
- **PullTime, PullFrom, LaunchFrom, PullClimb, SpeedMap** (test 55: "1st gear shoots bike up to 30 almost instantly,
  then next 20 is divided for 4 gears - 1st should be short, up to 10, then gradually change"): the game follows the
  throttle at once, so the bike reached 0.6 of its top in about 1.2 s while the engine's 1st lasts 1.44 s whatever the
  bike does. The throttle now climbs evenly from its floor, 0.11 of the top a second, from the press to the top
  (PullTime 8, PullFrom 0.1, LaunchFrom 0.1), and the engine hears the bike's speed through `SpeedMap`'s points, so each
  gear sounds as in test 55 at the new speeds: from a stop 2nd at about 12 on the dial, 3rd at 24, 4th at 42, 5th at
  about 50, the top about 8 s after the press (`sound: gear 2 at 220 u/s, 3246 rpm, heard 404 u/s; the engine's speed
  469 (SpeedMap)`). PullClimb keeps the climb's push at a log or a kerb as quick as before.

Each part's settings line is in `CMB_Slope.log` at the start and on getting on: `  view (2026-11-16b, test 55):
CameraPlace=1 (...) NearThird=60 NearFade=0.99 (...) ParentKeep=1 ParentMargin=256 (...) RollTurn=40 (...) LookPitch=45
(...); [Diag] ParentTime=1`, `  view (2026-11-16b, test 55): BodyWorn=1 (...) BodyWeapon=1 (...) BodyWeaponNodes=WEAPON
BodyNear=20 (...) BodyArmsBack=90 (...); [Diag] BodyDrawn=1`, `  view (2026-11-16b, the review): BodyFollowCamera=1 (...)`,
`  weapons (2026-11-16b, test 55): PutAwayProbe=1
PutAwayUnpaused=1 GunRootFrame=1 GunBothBars=1 GunCarry=1 GunStillRide=1 GunPredictMax=15 (...)`, `  kit (2026-11-16b):
[Look] KitFind=1 (...) KitFit=1 (...) KitFitView=40 KitFitBox=0.07,0.5`, `  steer (2026-11-16b, test 55): from rest the
throttle climbs evenly from its floor (0.1), 0.112 of the top a second, the top 8.0 s after the press (...); PullClimb=1:
...` and `  sound (2026-11-16b, test 55): SpeedMap=225:480,430:700,680:910,935:935: the bike's speed goes into the engine
through these points (...)`; the older lines now say `FirstKeys=0.45` and `BodyEye=(0, 2, -0.5)`. With the off values
each line says "as 2026-11-16a" or names the old behaviour.

Known, left for now (test 56 asks about each):
- First person: CameraPlace's reading is settled only by test 56's `camera: the camera root at ...` line; whether
  Parent's moves cost frames by the ParentTime line and the `ParentKeep=0` A/B; whether the game holds your pitch while
  the look back has the mouse by the look's end line. BodyFollowCamera rests on the order test 55's log shows (your 3D
  updated before the camera): if the game updates your 3D after the camera, the body gets the camera's move on top of
  its skeleton's and the hands run a frame's travel ahead of the grips (the lock line's A about 0 while riding says so;
  A/B `BodyFollowCamera=0`).
- Your body: whether the game honours the hidden flag on the worn bike's and the weapon's nodes isn't known (the speck
  covers every shape the plugin holds); BodyNear judges by the outfit's coarse bounds, so a chest piece, a backpack, a
  collar or a scarf with no sleeve near your neck goes whole, and a sleeveless top may vanish from your view (A/B
  `BodyNear=10` or 0); a rifle drawn still swaps the worn bike for the planted one for 2-4 s (the controller's own, as in
  test 55), a candidate for first-person hitches.
- Handguns: no one-handed aiming pose (the right hand stays on the grip with the gun in it; reloading keeps it there);
  a draw or a put-away can show one frame of the standing clip; where the game hangs the drawn gun, and whether the
  shots and the muzzle flash leave from the carried one, is test 56's (GunCarry's line); GunRootFrame's order of the
  game's update is read off test 55's log and self-checked once a session; after a rifle's put-away the seat poses are
  read again, so a pistol drawn straight after can show the standing pose.
- The field kit: *Customising the bike* above.
- The pull: the take-off is gentler (0.3 of the top after about 2 s; 0.4 s in 2026-11-16a) and the pick-up at low speed
  slower; the sound's top band is squeezed (a steady 38-52 on the dial all about 2,000 rpm, and in a pull 4th settles
  while the needle still climbs from about 42 to 50); a lower MCM speed makes the pull slower in units a second too
  (2nd and 3rd flatter; not simulated); `SpeedMap`'s points are tuned to PullTime 8 at the game's top of about 935.
- The 2026-11-16a build's and the 2026-11-15b build's known issues (below) still hold, but for what this build fixes:
  the put-away on the player, the handgun's right arm and the standing pose right after getting on, and `BodyEye`'s guess.

### The 2026-11-16a build's switches (still there; off = 2026-11-15b)

The 2026-11-16a build added no key: its `CMB_Slope.dll` and `CMB_Slope.ini` were 2026-11-15b's, byte for byte (the new
shapes need nothing of the plugin: 55 of its 64 bike shapes). Its new behaviour is the look's, and each has an off value
that gives the 2026-11-15b build back:

| Switch | Default | Off (2026-11-15b) |
|---|---|---|
| MCM Look "Seat" (`CMB_Look_Seat`, new; slot 11) | Dark brown (as it came) | (the stock seat is option 0: the shipped files) |
| the new tank and fender choices ("Enclave helmet (3D)", "Brotherhood helmet (3D)", "Gunners skull") | (not chosen) | any other choice: the helmets back on their invisible files on every bike |
| the four helmet shapes in the five bike meshes | there, invisible until chosen | the 2026-11-15b package's five nifs copied back (`look_emblems.py --emblems 0`) |
| the plates' emblems and the die-pressed font (`plates_d/_n/_s.dds`, `plate_text_d/_n/_s.dds`) | redrawn | the 2026-11-15b package's six textures copied back (`bike_art.py --plates --plate-font 2026-11-08a --plate-emblems 2026-11-09a`) |
| the badge atlas (`badges_d/_n/_s.dds`: the skull and the two enamel grounds in three spare cells) | 16 badges | the 2026-11-15b package's three copied back (`bike_art.py --badges --through 2026-11-08a`); the 13 older cells are unchanged either way |
| the order of the look's choices in the MCM's dropdowns and at the kit | alphabetical after the pinned ones (as it came, None, "Same as the left", "The plate's own"; Paint's palette test last) | (no switch: an ESP from the generator's `--kit-order table` has 2026-11-15b's order; not in the package) |
| the ESP's look (all of 2026-11-16a's) | 2026-11-16a's | (an ESP from the generator's `--look-build 2026-11-08a` is 2026-11-15b's, byte for byte; not in the package) |

What they do: *Customising the bike* above. The log lines: in `Papyrus.0.log`, opening the MCM's Look page `Look: the
MCM reads its dropdowns through the controller's properties (...)` once a session, and per choice there `Look: the MCM's
<slot> dropdown (its property): rank <r> = <key> (<index>)`; at the kit `Customise: seat = Seat:<key> (<index>)` and, with
a 3D left and the right on "Same as the left", `Customise: the right tank badge follows the left: TankL:enclavehelm3d`;
the look's colour lines end ` seat <V>` (the seat's palette row, -1 for the stock seat).

Known, left for now: the questions of test 56 (the kit's order by the recipes' priority and which way up; whether the
MCM calls the dropdowns' properties, with its fallback wired in the scripts and idle; the helmets against your knees and
the bars; the Enclave's eyes at night; the frame time beside the parked bike; the dark seats in the game's light), and
the 2026-11-15b build's known issues (below), which still hold.

### The 2026-11-15b build's keys (still there; off = 2026-11-15a)

The 2026-11-15b build answers test 53's and test 54's wishes, and every new behaviour has a key or an MCM value whose off
value gives the 2026-11-15a build back; the one exception is the right-hand cables, which are in the meshes (2026-11-15a's
four nifs, the 2026-11-10a package's, copied back give the old ones):

| Key or control | Default | Off (2026-11-15a) |
|---|---|---|
| `[Steer] FirstKeys` | 1 (a share of the turning limit, 0-1; 0.45 since 2026-11-16b) | 0: A and D step sideways in first person |
| `[Steer] FirstKeysArmed` | 1 | 0: with a weapon drawn in third person A and D strafe as in 2026-11-15a (FirstKeys acts in first person only); acts only with `FirstKeys` |
| `[View] CameraTurn` | 1 | 0: the first-person camera's "which way it looks" call not wrapped: no look and no lean of the view (with `LookBack` on, backing then switches to third person: `LookBack=0` for 2026-11-15a) |
| `[View] Roll` | -1 (the MCM's "View leans in turns (first person, deg)", 4) | 0: the view stays level |
| `[View] LookBack` (+ `LookBackAngle` 150, `LookBackHead` 60, `LookBackSide` 1, `LookBackAfter` 0.3, `LookBackIn` 0.35, `LookBackOut` 0.3, `LookBackLinger` 0.5, `LookBackSwing` 0.4) | -1 (the MCM's "Looking back while reversing (first person)": Over the shoulder) | 0: the view stays ahead while backing |
| `[View] LookKey` (+ `LookMax` 150, `LookSnap` 0.15) | -1 (the MCM's "Look key (scan code)", 44 = Z; a second key, `LookButton` 257, since 2026-11-21a) | 0: no look key |
| `[Diag] TurnEachRide` | 0 | (for tests: 1 = the camera's two checks again at each getting on) |
| MCM Riding "Weapons while riding" (`CMB_RideWeapons`, new, in the place of "Allow combat while riding") | Handguns only (in every save: the setting is new) | None = 2026-11-15a with "Allow combat while riding" off; Any weapon (standing poses) = with it on |
| MCM Riding "Looking back while reversing (first person)" (`CMB_ViewBack`, new) | Over the shoulder | Off (Third person: the game switches to third person while you back) |
| MCM Riding "View leans in turns (first person, deg)" (`CMB_ViewRoll`, new) | 4 (0-10) | 0 |
| MCM Hotkeys "Look key (scan code)" (`CMB_LookKey`, new) | 44 (Z) | 0: none |
| `[Tilt] PutAway` | 1 | 0: nothing called; a weapon that isn't a handgun: the script's sheathe action after 1 s, the ride ended after 3 s |
| `[Tilt] GunPose` | 1 | 0: a handgun out in the game's standing weapon poses, the ground-planted bike |
| `[Tilt] GunStandBack` | 1 | 0: the seat watch measures the knees while a weapon is drawn (the pose applied again mid-draw, test 53) |
| `[Tilt] GunPredict`, `GunBlend`, `GunSeatEvery` | 1, 0.25 (s), 5 (s) | `GunPredict=0`: the bones as last read (all three act only with `GunPose`) |
| `[Diag] GunTrace`, `GunListen` | 1, 1 | 0: no `gun:` lines; no graph-event list while a weapon is out |
| `[View] Body` (+ `BodyEye` 0,7,7 (0,2,-0.5 since 2026-11-16b, 0,6,-3 since 2026-11-17a), `BodyLeanMax` 35 (40 since 2026-11-17a), `BodyShiftMax` 15, `BodyBack` 100, `BodyFade` 1) | 1 | 0: your body left to the game, unseen in first person |
| `[Diag] BodyProbe`, `BodyProbeEvery` | 1, 10 (s) | 0: no `body:` probe lines |
| `[Steer] SidestepWide` (+ `SidestepWideShift` 160, `SidestepWideRate` 120, `SidestepWideMost` 25, `SidestepWideLong` 300, `SidestepWideDrop` 60, `SidestepWideClear` 40, `SidestepWideTall` 180) | 1 | 0: wide things only braked for (`SidestepWideDrop=0`: no ground test; `SidestepWideTall=0`: no height test) |
| `[Steer] SidestepSteady` | 30 (deg/s) | 0: a sidestep can start while the camera sweeps past |
| `[Steer] SidestepMouseSide` | 1 | 0: a mouse move over `SidestepMouse` lets a sidestep go, either way |
| `[Lamp] FrameLead` | 1 | 0: the lamps' lead by the plugin's task's own time (nearly 0 every second run) |
| `[Diag] FpsFrames` | 1 | 0: the frame-rate line counts the plugin's tasks (about twice the game's frames) |
| `[Diag] PausedFrames` | 1 | 0: the paused watch on the time line's count (a pause can come out as two lines) |
| the right-hand cables (the four worn and first-person nifs) | turn with the bars | (no switch: 2026-11-15a's nifs copied back) |

What they do:
- **FirstKeys** (test 54: "can turning with A and D be the same as when turning with mouse? it still does the same
  moving right or left but facing forward all the time"): in first person the game takes a side key as a step sideways;
  now it gets none and A/D turn the bike as a side key does in third person (the whole turning limit, eased in and out),
  with the lean and the bars (`steer: first person: the side keys turn the bike (FirstKeys 1 of the clamp, N deg/s
  now): the game gets no strafe`, once a ride). FirstKeysArmed does the same with a weapon drawn in third person, where
  the game strafed too (test 53: the bike slid 27-44 degrees off its heading): `steer: a weapon drawn in third person
  (the weapon state 3): the side keys turn the bike (...; FirstKeysArmed): the game gets no strafe`.
- **CameraTurn, Roll** (test 53: the lean in first person): the game's first-person camera call that says which way the
  camera looks is wrapped; the plugin first checks how the game builds the camera from it (`camera: GetRotation's answer
  ...: the root's rotation is the answer's matrix ...`), then leans the view into turns with the bike, Roll degrees at
  the bike's whole lean, about the bike's forward (`camera: the turn followed ...`). If the game turns its camera another
  way the log says so (`... off this session`, `the turn not followed`) and nothing turns: backing then uses third person.
- **LookBack** (test 53: "backing in 1st person ... there is no way to turn just the camera"): backing up in first person
  the view turns over the shoulder (the side key's side, D right, A left; none: right), the mouse turns only your head
  while the bike keeps its heading, the other side key held a moment swings the view through the back to the other
  shoulder, and forward brings it to the front at once (`view: looking back over the right shoulder (...)`, `view: back
  to the front after 2.4 s (forward)`); or, with the MCM's "Third person", the game switches to third person while you
  back and back to first person when you ride on (`View: third person while backing` in the Papyrus log). The Pip-Boy
  faces the view forward. With a weapon drawn (or being drawn or put away) there is no look back and no third person
  while backing, and the view still leans in turns (`view: backing with a weapon drawn (the weapon state 3): no look back
  over the shoulder (LookBack 1); ...`). `LookBack=2` in the INI takes effect only while the MCM's "Looking back while
  reversing" isn't Off.
- **LookKey**: hold it (Z) in first person on the bike, at any speed, to look round with the mouse; the bike keeps its
  line, and letting go brings the view back (`view: the look key (Z) held at 612 u/s: ...`). Say if Z clashes with one
  of your keys: the MCM's "Look key (scan code)" takes another (0 = none). With a weapon drawn it turns your head 60
  degrees at most.
- **Weapons while riding, PutAway, GunPose, GunStandBack, GunPredict** (test 53: "when on bike, only handgun can be used
  ... hold handlebar with at least one hand (preferably left) and shooting with another (right)"): in Handguns only, the
  default, a handgun (a gun with the game's pistol keyword on the gun itself, on what it wears or on its parts, where
  the modular pistols may carry it by their grip: the log says which reading found it) can be drawn and fired while
  riding: in third person you stay seated with the left hand on the bar and the lean and steering as on a holstered ride, the right arm and the gun the game's own (aim, fire, reload),
  and the bike stays under you (no swap to the planted bike at each draw). The seated pose is read while you ride
  holstered (`gun: the seat pose read (still ...)`, `(riding ...)` after a second or two over 200 u/s), so drawn at speed
  straight after getting on you get the old standing pose once (`gun: a handgun out at 640 u/s with no riding seat pose
  yet ...`). Anything else out is put away ("Only a handgun can be used on the motorbike."; `gun: put away asked ...`,
  `gun: the weapon state 3 > 4 > 5 > 0: away 0.62 s after the ask ...`), the game's own put-away called by the plugin;
  getting on with a weapon out puts it away first. VATS stays off. GunStandBack keeps the pose from being applied again
  mid-draw (test 53: four times). "None" and "Any weapon (standing poses)" are the old switch off and on; your old
  setting isn't carried over (test 53's save had it on), so every save starts on Handguns only, as you asked. Loading
  a save no longer puts a drawn weapon away by itself, and a put-away caught in a save doesn't block the next ones.
- **Body, BodyProbe** (test 54: "for 1st person it would be nice if character model was visible, no arms and torso is
  throwing me off a bit"): in first person your own body is drawn on the bike: the arms with the hands on the grips
  (turning with the bars), the chest and legs, in your own outfit, in the riding pose taken while you rode in third
  person (so ride a moment in third person, seated with the bars straight, once a game session); the head shrunk away
  (your eye is in it) and the worn bike hidden (the first-person bike shows instead). Not with the Pip-Boy open, a weapon
  out, while an item is used, or looking back. Whether the game draws it at all is the open question: the `body:` lines
  say what the game does with your body there (`body: first person: the player's 3D root ...`, `body: drawn? ... the game
  visits it`). There is no MCM switch: `[View] Body=0` turns it off.
- **SidestepWide, SidestepSteady, SidestepMouseSide** (test 53: "does it work only for mailboxes/lampposts? it would be
  nice if it would do that for most of non-alive things"): a parked car, a barrel group, a fence piece or debris that
  ends near your line on one side is steered round on that side as the narrow sidestep does, a quick lane change,
  braking a little meanwhile; never walls, buildings, cliffs, the ground or anyone, and not while you turn (`sidestep:
  Sedan02_Postwar (layer 29) wide 560 past the front wheel ...: to the left, ... (SidestepWide)`). The camera sweeping
  past a post no longer starts and drops a sidestep (`sidestep: not started for c_Post02: the rider is steering ...`),
  and moving the mouse the way a sidestep goes keeps it, or hands it to you (`sidestep: the mouse 7.2 deg toward the open
  side: kept`, `sidestep: handed to the rider after 0.31 s: ...`); in first person the sidestep's own turn no longer
  reads as the mouse, so it runs to its end. At each ride's end `sidestep: this ride 3 narrow and 2
  wide started: ...` says which rule refused most. Too sharp: `SidestepWideRate=90` and `SidestepWideMost=20`.
- **FrameLead, FpsFrames, PausedFrames** (test 54: the plugin's task runs twice a game frame): the headlamp's and the
  tail lamp's light now lead by the game's own frame, the frame-rate line counts the game's frames (`time: ...` about
  half test 54's number, ending `; the game's frames, the plugin's task 2.0 times a frame (FpsFrames)`), and a long pause
  is one `game: the world paused ...` line, not two.
- **The right-hand cables** (test 53: "cables that should be attached to handlebar on the right side ... just floating"):
  the two thin cables under the right switch block and the wire from the right of the bar now turn with the bars, in
  first and third person (their bar end cut out into a shape of its own, which the plugin turns as it turns the bars);
  with the bars straight nothing looks different.

Each part's settings line is in `CMB_Slope.log` at the start and on getting on: `  steer (2026-11-15b, the review):
FirstKeysArmed=1 (a weapon drawn in third person: the side keys turn the bike as FirstKeys does in first person, the game
gets no strafe)`, `  view (2026-11-15b, test 54):
CameraTurn=1 (FirstPersonState's GetRotation wrapped: the look and the view's lean) Roll=-1 (the MCM's CMB_ViewRoll, 4
in a new save) LookBack=-1 (...) ...; [Steer] FirstKeys=1 (...); [Diag] TurnEachRide=0`, `  view: LookKey=-1: the MCM's
CMB_LookKey 44, Z (VK 0x5A): held in first person on the bike, ...`, `  view (2026-11-15b, test 54): Body=1 (the
rider's own body shown in first person, in the riding pose taken in third person) BodyEye=(0, 7, 7) BodyLeanMax=35
BodyShiftMax=15 BodyBack=100 BodyFade=1; [Diag] BodyProbe=1 BodyProbeEvery=10`, `  weapons (2026-11-15b, test 53's wish
a): PutAway=1 GunPose=1 GunStandBack=1 GunPredict=1 GunBlend=0.25 GunSeatEvery=5 GunTrace=1 GunListen=1 (...)`, `  sidestep
(2026-11-15b, test 53's wish g): SidestepWide=1: ...; SidestepSteady=30: ...; SidestepMouseSide=1: ...` and `  frame
(2026-11-15b): [Lamp] FrameLead=1 (...) [Diag] FpsFrames=1 (...) PausedFrames=1 (...)`; with them `globals: the
2026-11-15b build's 4 found, CMB_ViewBack to CMB_LookKey (...)` and `globals: the 2026-11-15b weapons globals found,
CMB_RideWeapons 1, ...`, and in `Papyrus.0.log` at every getting on `Weapons while riding: Handguns only (CMB_RideWeapons
1): fighting on, VATS off (a handgun equipped).` (or `fighting off ... (no handgun equipped)`).

Known, left for now:
- First person: that the game builds its camera from the call the plugin turns is checked once a session, not known
  (`camera: GetRotation's answer ...` settles it); if it doesn't, the view's lean and the look key do nothing and backing
  switches to third person (one line says so).
- With a weapon drawn in third person A and D now turn the bike (`FirstKeysArmed`); whether the game then snaps the body
  back to where the camera looks is test 55's to say. In first person a slow mouse move neither keeps nor lets go of a
  running sidestep (the plugin rewrites the heading every frame while it runs); the keys, back and the brake still do,
  and it ends by itself within 2 s.
- Handguns: the shots and the muzzle flash leave from where the game's standing clip holds the gun (up to about 20-30
  units off the drawn pistol); the head looks ahead, not where you aim; first person keeps the game's own two-handed
  pistol; reloading keeps the left hand on the bar; drawn at speed before a second or two of holstered riding (after
  getting on or a load) it shows the standing pose once; which pistols count (the modular ones, the revolver, the flare
  gun) is test 55's to say; the put-away rests on an engine call the plugin checks once a session (`gun: the player's
  slot 0xC7 is the heading's getter ...`).
- Your body in first person: if the game hides it by something the plugin can't undo, nothing shows and the `body:`
  lines say so; it needs a moment of third-person riding once a game session; the collar or shoulders may look cut near
  the camera (an A/B: `[View] Near=5`); `BodyEye` (0,7,7) is a guess, and the probe line gives the real offset (since 2026-11-16b 0,2,-0.5, test 55's).
- The wide sidestep's numbers are a first, reasoned set, not ridden; parked cars that are part of the scenery's combined
  meshes (no reference of their own) are still only braked for.
- The cables: at full lock the cut opens 2.4-3.2 units behind the headlamp (not seen from the eye or the riding camera
  in the renders).
- The rider-pose report (`CMB_RiderPose_report.txt`, for seated pistol clips in a later build) comes from
  `make_rider_pose.bat` of this build's repository; the package doesn't hold the tool, and the plugin it makes is
  unchanged.
- The 2026-11-15a build's known issues (below) still hold, but for the lamps' lead and the frame-rate line, which now
  count the game's frames.

### The 2026-11-15a build's keys (still there; off = 2026-11-14a)

Every new behaviour of the 2026-11-15a build (test 54) has a key or a `CMB_LookOptions` bit whose off value gives the
2026-11-14a build back. Since 2026-11-15b `[Lamp] Lead`, the tail lamp's lead and the frame-rate line count the game's
frames too (`[Lamp] FrameLead`, `[Diag] FpsFrames`, the table above):

| Key or control | Default | Off (2026-11-14a) |
|---|---|---|
| `[Look] KitDefer` (`CMB_LookOptions` 32768) | 1 | 0: a plate colour chosen at the field kit re-composes the parked bike at once, with the menu open (test 54's two crashes) |
| `[Look] MountQuick` (65536) | 1 | 0: WornIndex's colour pass and the kept bike's key worked out afresh at every getting on (about 0.9 s more black) |
| `[Look] KitPreviewPos`, `KitPreviewTurn`, `KitPreviewScale`, `KitPreviewZoom` (changed; commented out: the defaults) | 0,400,0; 0,0,0.785398; 1; -1,3 (since 2026-11-16b 0,1050,-45 and -0.223219,0,0.785398) | 0,0,0; 0,0.02,44.764; 0.3; -1,1 (the menu's camera inside the bike) |
| `[Look] KitTuneDistance` | 1 | 0: Tune's first slider is the bike's size in % again, the bike at the camera |
| `[Look] KitPreviewScene` | 1 | 0: no `kit: the menu's scene` and `kit: the menu's camera` lines |
| MCM "Preview distance" (was "Preview size (%)", `CMB_KitPrevSize`) and "Preview zoom in" (`CMB_KitPrevZoomIn`) | 400 (100-2000), 3 | (Tune only; with `KitTuneDistance=0` the first is the size again, its 30 by `set CMB_KitPrevSize to 30`) |
| `[View] EyeAt` (changed) | 0,-5,125 | 0,1,128 |
| `[View] CameraWorld` | 1 | 0: the camera's answer read through its parent: EyeAtCamera turns itself off at once, as in test 54 |
| `[View] LeadFrame` | 1 | 0: the Lead's guess by each run of the task's own time (nearly 0 on every second run) |
| `[View] LookWait` | 3 (seconds) | 0: the first-person bike shown as soon as it is built, stock colours and all |
| `[Steer] PullTime` | 5.5 (seconds; 8 since 2026-11-16b) | 0: the throttle climbs as `Accel` and `LaunchTau` give it at any speed (the top reached while the sound is in 2nd) |
| `[Steer] PullFrom` | 0.6 (of the top; 0.1 since 2026-11-16b) | (a parameter: where the slower climb begins; acts only with `PullTime` over 0) |
| `[Diag] KeepLogs` | 3 | 1: only `CMB_Slope_prev.log` kept (read at the game's start) |

What they do:
- **KitDefer** (test 54: the game crashed twice at the field kit, both times in the frames right after "Plate
  background: The plate's own" re-composed the parked bike beside the kit while the menu was open; the MCM's plate
  settings never crashed): a plate colour (Plate letters, Plate background) chosen at the kit now goes on the parked
  bike when the menu closes, with the rest of the look, as the MCM's Apply does after its menu; nothing swaps the parked
  bike's materials while the workbench menu is open (`Customise: Plate background = PlateBack:own (0): on the parked
  bike when the menu closes (KitDefer)`, then at the close `Customise: the plate colours chosen in the menu (1) go on
  the parked bike with the look, the menu closed (KitDefer)`). The armour menu's preview never showed these two slots,
  so you see your plate colours once you leave the menu.
- **MountQuick** (test 54: getting on about 0.85 s slower than in test 53, the screen back 3.40 s after the press
  against 2.54 s): 2026-11-14a's Free colour fix wrote the look's colours into the chosen options' swaps, and worked out
  the kept bike's parts, at every getting on, about 70 script calls behind the black screen. Both are now remembered and
  skipped while the look is the same (one swap read checks it: `Look: the worn bike's colour indexes before its equip
  (WornIndex): in its options' swaps since the last pass, the look unchanged (MountQuick), ...`); a load, a restart or a
  look change always gets the full pass. Getting on should be about as quick as in 2026-11-10a again.
- **The field kit's preview** (KitPreviewPos, KitPreviewTurn, KitPreviewScale, KitPreviewZoom, KitTuneDistance,
  KitPreviewScene; test 54: no bike in the kit's menu): its log showed the menu reads the turn in radians, ignores the
  scale and puts the bike where the position says, ahead of its camera along y; with 14a's position 0 the camera sat
  inside the bike. New now puts the bike 400 ahead, turned 45 degrees, scale 1, zoom -1..3 (`kit: the preview's
  transform written (the new one): pos 0,400,0, turn 0,0,0.785398, scale 1, zoom -1..3 (...)`). Tune's first slider is
  the distance ("Preview distance": less is a bigger bike); a 2026-11-14a save keeps that slider's 30, which means New's
  400 until you move it. KitPreviewScene logs where the menu's camera is and whether the whole bike is in its view
  (`kit: the menu's scene: ...`, `kit: the menu's camera: ... the whole bike in view: yes (...)`), so the next build can
  set the distance from the real camera.
- **CameraWorld, LeadFrame** (first person; test 54: "it still shakes ... every hole is visible as a shake"; the log:
  `camera: EyeAtCamera off this session: the camera root 118676.34 from GetTranslation's place at the next frame`, the
  camera's distance from the world's origin): the game's own camera place, which the first-person bike follows each
  frame, is taken as a place in the world (2026-11-14a read it through the camera's parent, doubling it, so its
  self-check switched the fix off on the first frame); once a session `camera: GetTranslation's answer (...) as the
  camera root's world ([View] CameraWorld=1): the root 0.00 from it at the next task; ...` says it fits. And the
  plugin's frame task runs twice for each frame the game draws, so the second run's own time, which `Lead`'s guess used,
  was nearly 0: with LeadFrame the guess uses the game's frame (the lock line ends `; LeadFrame: 2.0 task(s) a game
  frame ...`).
- **LookWait** (test 54: "default red is showing for a moment" in first person right after getting on): the script
  colours a fresh first-person bike a second or so after the game builds it; the plugin now keeps it hidden until its
  colours are on, 3 s at most (`view: first person: the view bike ... kept hidden until its look is on ...`, `view: the
  view bike ...'s look on 1.25 s after its 3D: its materials swapped ...`), and at a hand-over keeps the old one shown
  until the new one is coloured.
- **EyeAt** (test 54: "I think -6 and -9 was the best for me as in camera positioning"): the default holds the MCM's
  "eye forward" -6 and "eye up" -3 you used; **set the MCM's "Eye forward on the bike" and "Eye height on the bike" back
  to 0** (a save keeps them, and they still add to EyeAt).
- **PullTime, PullFrom** (test 54: "bike reaches 50 just on gear 2, but it still goes on for 2 more without gaining
  speed"; you chose the slower pull so the gears keep their sound): above 0.6 of its top (PullFrom) the bike takes 5.5 s
  more to reach it, from rest and at speed alike, so its speed climbs with the engine's gears: into 2nd at about half
  the top, into 3rd at about 0.78, the top about when 3rd ends and 4th comes in (about 6 s after the press). The
  take-off under 0.6 is as before, and the engine's gears, their lengths and shift points are untouched: 5.5 s is the
  slowest pull that keeps the sound as it is (6 lowers late 3rd by about 90 rpm, 7 makes 3rd flat). After a lift or a
  hit at speed the bike climbs back at the same rate (from half speed about 4-5 s; `PullFrom=0.8` keeps it quick up to
  0.8 of the top). `launch: from rest: ..., 0.9 after 5.1 s, the top (0.97) after 6.0 s (...); ...; above 0.6 of the top
  at most 0.0727 a second (PullTime)`.
- **KeepLogs** (test 54: two crash restarts in a row lost the first session's log): the logs of the three sessions
  before are kept beside `CMB_Slope.log` as `CMB_Slope_prev.log`, `CMB_Slope_prev2.log` and `CMB_Slope_prev3.log`
  (newest first); the first line says so (`...; the session before's log kept as CMB_Slope_prev.log, the two before it
  as CMB_Slope_prev2.log and CMB_Slope_prev3.log (KeepLogs=3)`).

Each part's settings line is in `CMB_Slope.log` at the start: `  look (2026-11-15a, test 54): KitDefer=1 (the kit's
plate colours on the parked bike at the menu's close) MountQuick=1 (getting on reuses an unchanged look's indexes and
kept key): CMB_LookOptions 131071 for the scripts`, `  kit (2026-11-15a): [Look] KitTuneDistance=1 (Tune's first slider:
the distance, pos y) KitPreviewScene=1 (the menu's scene and camera lines, with KitPreviewLog)`, `  view (2026-11-15a,
test 54): CameraWorld=1 (GetTranslation's answer the camera root's world) LeadFrame=1 (the Lead's time the game's frame)
LookWait=3 (the view bike kept hidden until its look is on, for at most that)` and `  steer (2026-11-15a, test 54):
above 0.6 of the top the throttle climbs at most 0.0727 of the top a second, the top 5.5 s from there at full throttle,
...`; the 2026-11-14a kit line now says `New: pos 0,400,0, turn 0,0,0.785398, scale 1, zoom -1..3`, the view line
`EyeAt=(0, -5, 125)`, and every look line `CMB_LookOptions 131071 for the scripts`.

Known, left for now:
- With IAF / Chem Reanimations, an item used at speed (by its number key too) is used at once, but the start of that
  mod's decoration clip still shows for a moment after each use (cut at its first frame: a short dip, as after a use
  from the Pip-Boy); keeping it from starting at all while riding is for a later build.
- The plate colours chosen at the field kit now show on the parked bike when the kit's menu closes, not while it is open
  (the menu's preview never showed them either).
- The preview's 400 is computed from test 54's numbers: the bike may look small (zoom in, or Tune's "Preview distance"),
  and test 55's camera line sets the final value; what one zoom unit does is still unknown.
- First person: that the game's camera answer is a place in the world is inferred (about 70% sure; the once-a-session
  `camera: GetTranslation's answer ...` line settles it). With the bike now keeping up with the camera your eye may feel
  a little further back at speed than in test 54 (standing it is the same). If it still feels "without suspension" while
  the log says `the camera root 0.00`, what is left is the game's own camera path over bumps, which only a new feature
  could smooth. `[Lamp] Lead`, the tail lamp's lead and the frame-rate line still count the task's two runs a frame (since
  2026-11-15b the game's frames: `[Lamp] FrameLead`, `[Diag] FpsFrames`).
- The slower pull: 5.5 s leaves a small margin to the engine's own climb late in 3rd (if a `sound: gear 4 at ...` line
  shows the bike under the `heard` speed, 5 s is the next step); after a lift at speed the note follows the bike, a
  gentler pull; a lower MCM speed makes the pull slower too (not simulated).
- `KeepLogs` is read at the game's start only.
- Test 54 settled three of 2026-11-14a's questions: the bike's hotkey is B (so the MCM's "48 = B" is right), Free colour
  shows in third person (the Palette test was cobalt), and a sound fades while the game is paused (MenuQuiet).
- Coming in 2026-11-15b: A and D turning the bike in first person as the mouse does, with a slight lean; the rider's
  arms and body seen in first person; looking back when reversing; handguns on the bike; sidestepping big objects; the
  right-hand cables in first person.

### The 2026-11-14a build's keys (still there; off = 2026-11-10a)

Every new behaviour of the 2026-11-14a build (test 53) has a key, an MCM value or a `CMB_LookOptions` bit whose off
value gives the 2026-11-10a build back (for the gears, all their rows together); the one exception is the field kit's
names (below). Since 2026-11-15a New's four preview values and `[View] EyeAt` have new defaults (the table above: the
values below are 2026-11-14a's), the MCM's "Preview size (%)" is "Preview distance" (`[Look] KitTuneDistance`), and the
plugin writes `CMB_LookOptions` 131071 at its defaults:

| Key or control | Default | Off (2026-11-10a) |
|---|---|---|
| `[Steer] QuickKeyCodes` | auto | scan: QuickKeys compared raw (never the game's codes) |
| `[Steer] QuickKeyState` | 1 | 0: the number keys not read from the keyboard's own state |
| `[Steer] QuickCut` | 1 | 0: an unapplied clip after a number key not handed to the script |
| `[Steer] UseStopUnapplied` | wait | cut: an item's clip at speed cut at its props whatever |
| `[Steer] UseStopWaitMax` | 3 (seconds) | (a parameter: how long a clip with no item yet is left to play) |
| `[Steer] UseStopLead` | 1.5 (seconds) | (a parameter: how long before its props an item's use is that clip's) |
| `[Diag] QuickProbe` | 1 | 0: no self-test lines, no hotkey-key lines |
| `[Look] WornIndex` (`CMB_LookOptions` 4096) | 1 | 0: the worn bike's colours by the plugin's write and HueSwap's swap only (once it was 1 in a session, the options' swaps are put back before each getting on) |
| `[Look] KeptMods` (8192) | 1 | 0: any change of the look re-attaches the kept worn bike's mods |
| `[Look] Repass` | 0 | (0 is off; 1 = an A/B: the game's own render-pass clear after a colour write) |
| `[Diag] WornPasses` | 1 | 0: no "was" words, no `look: the worn paint's passes` or `the worn paint not written` lines |
| MCM Look "Field kit only in your settlements" (`CMB_KitWhere`, new) | on | off: the field kit anywhere |
| MCM "Field kit preview" (`CMB_KitPreview`, new) | New | As before (the ESP's view: a tyre fills the menu) |
| MCM "Preview size (%)", "Preview turn", "Preview tilt", "Preview up / down", "Preview zoom out", "Preview zoom in" (`CMB_KitPrevSize` ... `CMB_KitPrevZoomIn`, new) | 30, 7, 0, 0, -1, 1 | (used only with "Field kit preview" Tune) |
| `[Look] KitPreview` | 1 | 0: the plugin never writes the preview |
| `[Look] KitPreviewPos`, `KitPreviewTurn`, `KitPreviewScale`, `KitPreviewZoom` (commented out: the defaults) | 0,0,0; 0,0.02,44.764; 0.3; -1,1 | (parameters: the preview "New") |
| `[Look] KitPreviewLog` | 1 | 0: no `kit:` lines |
| the field kit's item and slot names (the ESP) | "Motorbike"; "Paint: Factory" and so on | (no switch: an ESP from the generator's `--kit-names 0` has 2026-11-10a's names; not in the package) |
| `[View] EyeAt` (changed) | 0,1,128 | 0,12,128 (over the tank's rear) |
| `[View] EyeLock` | 1 | 0: your eye followed on the untilted bike with EyeSmooth (the bike swung under you with the tilt) |
| `[View] EyeAxes` | 1 | 0: the first-person bike turned as the third-person skeleton is, not along your heading |
| `[View] Camera`, `EyeAtCamera` | 1, 1 | 0, 0: no camera call wrapped; the bike placed by the plugin's frame and `Lead` alone |
| `[View] Fov` | 0 | 1: `CMB_ViewFov` used again (console only: the MCM slider is gone) |
| `[Diag] ViewLock` | 1 | 0: no `view: lock:` line |
| MCM Riding "Field of view riding in first person" | removed | (`[View] Fov=1` and `set CMB_ViewFov to <60-120>`) |
| `[Sound] MenuQuiet`, `MenuQuietOut`, `MenuQuietIn` | 1, 0.15, 0.3 (seconds) | `MenuQuiet=0`: heard through a menu |
| `[Sound] HeardKeep`, `HeardCreep` | 1, 0.3 | `HeardKeep=0` |
| `[Sound] LiftDown` | 0.08 | 0 |
| `[Sound] ShiftRpm` (changed) | 3500 | 2500 |
| `[Sound] Gears` (changed) | 410.6,636.4,954.5,1272.7,1626.4 | 555.556,750,960,1161.6 |
| `[Sound] ShiftDraw` (changed) | 3200,3700 | 2300,3000 |
| `[Sound] HeardRiseGears` (changed) | 2,0.79,0.65,1,1 (2,0.86,0.8,1,1 since 2026-11-21a, 2.1,1.35,1,1,1 since 2026-11-23a) | 2.5,0.95,0.5,1 |
| `[Sound] ShiftGapGears` (changed) | 0,2,3,1.5 (0,1.8,2,1.7 since 2026-11-21a) | 0,2,3 |
| `[Sound] LaunchRise` (changed) | 650 | 350 |
| `[Sound] LaunchFlare` (changed) | 0.35 | 0.5 |
| `[Diag] HandoverFromReady` | 1 | 0: the late hand-over line from the ride's start, past 6.0 s |

What they do:
- **QuickKeyCodes, QuickKeyState, QuickCut, UseStopUnapplied, UseStopWaitMax, UseStopLead, QuickProbe** (test 53: a
  stimpak by its number key at speed was never used and no `quick:` line came: the game gives a key's virtual-key code,
  0x31 for number key 1, and QuickKeys' scan codes never matched; the clip was then cut before the game applied the
  item): the plugin now finds a number key by the game's own name for it (`Quickkey1` to `Quickkey12`, whatever key you
  bound) or by its virtual key, and the log shows the key in hex: `quick: key 0x31 (the slot 1, the game's 'Quickkey1')
  at 812 u/s: Stimpak (00023736, a potion) handed to the script's watch, not the game's animated use (allowStimpakUse
  1): CMB_RiderQuickUse 17` (number key 1 is 0x31, 2 is 0x32 and so on, 0 is 0x30, - is 0xBD, = is 0xBB). `QuickKeys` is
  still written as scan codes: the plugin turns them into the game's keys. If the plugin still can't take a key
  (QuickUse off, a gamepad), a potion's clip at speed is cut at its props and the item handed to the hotkey script,
  which uses it unless the game did (QuickCut: `quick: number key (0x31, the slot 1) at N u/s: Stimpak (...) not taken
  from the game, its use clip cut at the props before the item came: handed to the script's watch to use it (QuickCut):
  CMB_RiderQuickUse -N`), or the clip plays until the item is used and is cut then (UseStopUnapplied: `... left to play
  until it is, 3 s at most (UseStopUnapplied)`), so the stimpak always heals. Each item use now counts for one clip
  only: a double-tap, or a stimpak right after a chem, is no longer cut unused. QuickProbe's lines (`quick: self-test:
  ...`, `quick: this ride: ...`, `input: the first movement key from the game: ...`, `quick: the ride began 1.92 s after
  the 0 key (0x30) went down ...`) show where a key gets lost and which key the bike's own hotkey is pressed as: 0 or B.
- **WornIndex, KeptMods, Repass, WornPasses** (`CMB_LookOptions` 4096 and 8192; test 53: Free colour blue in third
  person on every ride but the one the game loaded into, though the plugin's write read back): before the worn bike goes
  on, the look's colours are written as the colour indexes of the chosen options' own material swaps, so the game builds
  the worn bike with them, as it does the parked bike (`Look: the worn bike's colour indexes before its equip
  (WornIndex): Paint 4 of 4 set ...`); no F4SE swap after the fade. A colour-only change (hue, shade, plate colours,
  mirrors) no longer re-attaches the kept worn bike's mods (KeptMods; about 1.2 s quicker). `[Diag] WornPasses` says
  what the worn paint's material held before the write (`...; was 0.3374 already, 2 passes built before it`) and what
  its render passes hold 0.5 s and 2 s after, and with Paint "Palette test: colour index" what the game put in it
  (`look: the worn paint not written (...): ...'s material holds 0.4609`); `[Look] Repass=1` is an A/B: the game's own
  render-pass clear after a colour write. The plugin writes `CMB_LookOptions` 32767 at its defaults (16384 is its own:
  WornIndex was on this session); without F4SE the ESP's 4031 holds none of the new bits.
- **The field kit** (test 53's wishes): the armour menu names the item "Motorbike" (it read "Default", its object
  template's name) and every slot's choice with its slot, "Paint: Factory", "Rims: ...", "Tank L: ..." (only the
  plugin's names: the same records, nothing in a save; the way back is an ESP built with `--kit-names 0`, not shipped);
  the preview shows the whole bike, smaller and turned three-quarters with room to zoom out ("Field kit preview" New;
  Tune and its six sliders move it, As before is 2026-11-10a's tyre), written by the plugin while the game runs (`kit:
  the preview's transform written (the new one): ...`), and `[Look] KitPreviewLog` logs the preview's numbers and the
  menu's zoom so the next build can fix the best values in the ESP; and with "Field kit only in your settlements" on,
  Customise at the parked bike opens the kit only in a settlement whose workshop is yours: anywhere else "The field kit
  works only in your settlements." and nothing comes out of the side bag (`Customise refused: not in one of your
  settlements (...)`). "Free customising" in the MCM works anywhere either way.
- **EyeLock, EyeAxes, Camera, EyeAtCamera, ViewLock** (first person; test 53: "bike was shaking violently ... felt like
  character was sitting on fuel tank"): the first-person bike is held so your eye sits at `EyeAt` on it as it is tilted
  (the pitch on a slope, the lean, the lift), at once every frame, so the bike turns about your head and never moves
  against it; it points along your heading; and the game's own first-person camera call is wrapped so the bike follows
  the camera's place of each frame (`camera: FirstPersonState (...): GetTranslation (slot 0xD, ...) wrapped ...`).
  `EyeAt` is 11 units further back, over the seat, where the game's own camera sits at a stop; the MCM's "Eye forward on
  the bike" still adds to it. `[Diag] ViewLock`'s `view: lock:` line every 2 s says what moves what.
- **Fov** (test 53: the game wrote its own 80 back; "fov slider ... can be dropped"): the riding FOV is gone, with the
  MCM's slider; an older save's slider value is ignored (`view: CMB_ViewFov 90 (an older save's riding FOV) left alone:
  ...` once). `FovSearch`, `FovTime` and `FovOffset` act only with `Fov=1`.
- **MenuQuiet, MenuQuietOut, MenuQuietIn** (test 53: the bike heard in the Pip-Boy and the pause menu): while a menu
  pauses the game the engine and the water loop fade out over `MenuQuietOut` (0.15 s) and back over `MenuQuietIn` (0.3
  s) after it (`sound: held at gear 3, ...; the loops out over 0.15 s (MenuQuiet)`, `sound: resumed after ...; the loops
  back over 0.30 s from the close (MenuQuiet)`); 0 = heard through it.
- **HeardKeep, HeardCreep** (test 53: "the climb in the sound wasn't smooth, it was dropping when it shouldn't"): with
  the throttle on and the bike gaining the engine's note never falls (the heard speed kept up, creeping on at
  `HeardCreep` 0.3 of its gear's rise; the trace's ` keep`); 0 = 2026-11-10a.
- **LiftDown** (test 53: 2nd to 1st on a throttle lift): a lift's down-shift only once the heard speed is 8 % under the
  lift's (never for a gear already under `DownRpm`), so a lift with the speed holding never blips down; a stop's
  down-shifts are as before; 0 = 2026-11-10a.
- **The gears** (test 53: "a bit flat - didn't raise RPM as much as I was expecting"): five gears up-shifting at about
  3200-3400 rpm at full throttle (into 5th about 2500), 2nd and 3rd climbing all through, a short 4th, the cruise as
  before (5th is the old 4th: 1937 rpm at 900 u/s): `ShiftRpm` 3500, `Gears` 410.6,636.4,954.5,1272.7,1626.4,
  `ShiftDraw` 3200,3700, `HeardRiseGears` 2,0.79,0.65,1,1, `ShiftGapGears` 0,2,3,1.5, `LaunchRise` 650, `LaunchFlare`
  0.35; all seven at their 2026-11-10a values are that build's gears (`ShiftDraw=2900,3400` is a milder set with the new
  gears). After each getting off `sound: generation N's ride: the note held N times for N s while the bike gained
  (HeardKeep), N lift down-shift(s) held back (LiftDown); ...`.
- **HandoverFromReady**: the engine's late hand-over line counts from the moment the bike was ready (`sound: generation
  N handed over 5.2 s after the bike was ready (usually 3; 8.1 s after the ride's start)`), not from the press, which a
  look change's attach could stretch (test 53's false 6.1 s).
- **CMB_KitWhere to CMB_KitPrevZoomIn**: eight new globals (0xBF7-0xBFE) for the MCM's new controls; `CMB_ViewFov`
  (0x8B1) stays in the ESP, unused.

Each part's settings line is in `CMB_Slope.log` at the start: `  quick (2026-11-14a, test 53): QuickKeyCodes=auto (the
game's Quickkey names, else QuickKeys' virtual keys 0x31,0x32,...,0xBD,0xBB) QuickKeyState=1 QuickCut=1
UseStopUnapplied=wait UseStopWaitMax=3 UseStopLead=1.5 QuickProbe=1`, `  look (2026-11-14a, test 53): WornIndex=1
KeptMods=1 Repass=0; [Diag] WornPasses=1 HandoverFromReady=1: CMB_LookOptions 32767 for the scripts`, `  kit
(2026-11-14a): [Look] KitPreview=1 (New: pos 0,0,0, turn 0,0.02,44.764, scale 0.3, zoom -1..1) KitPreviewLog=1`, `  view
(2026-11-14a, test 53): EyeLock=1 (...) EyeAxes=1 Camera=1 EyeAtCamera=1 (...) Fov=0 (...); [Diag] ViewLock=1`, `  sound
(2026-11-14a, test 53): HeardKeep=1 HeardCreep=0.3 LiftDown=0.08: ...` and `  sound (2026-11-14a, test 53): MenuQuiet=1
MenuQuietOut=0.15 MenuQuietIn=0.3: ...`; the 2026-11-10a and 2026-11-09a look lines now say `CMB_LookOptions 32767 for
the scripts`.

Known, left for now:
- Whether the number keys reach the favourites' handler at all is the self-test's to say (`quick: self-test: in N s:
  ...`); if they don't, QuickCut or UseStopUnapplied still heal at speed, after the clip's props.
- The MCM's help for the built-in hotkey says "48 = B"; F4SE takes the game's own key code, where 48 is the 0 key: the
  hotkey lines say which, and the help is fixed once test 54 has said.
- Free colour in third person rests on the game applying a colour swap's index while it builds the ridden bike: the
  Palette test says whether it does. An option you didn't choose keeps the last colour written into it until you choose
  it again (only the armour menu's preview can see that). The first getting on after a real change of mods (not just a
  colour) is still about 1.2 s slower.
- The field kit's preview values are a first guess (the bike may be small: zoom in, or Tune); the names have no switch
  in the game.
- Whether the game lowers the sound while paused (MenuQuiet's premise) is test 54's question; after a menu that ends
  with the bike much slower than when it opened the note can still fall, as in 2026-11-10a; the throttle-off loop is
  pitched further up at the top of a pull.
- Looking back when reversing, the A/D lean, handguns on the bike, sidesteps round bigger things and the right-hand
  cables in first person come in 2026-11-14b.

### The 2026-11-10a build's keys (still there; off = 2026-11-09a)

Every new behaviour of the 2026-11-10a build (test 52) has a key, an MCM value or a `CMB_LookOptions` bit whose off
value gives the 2026-11-09a build back. Since 2026-11-14a `QuickKeys` is turned into the game's own key codes
(`[Steer] QuickKeyCodes`) and the log names a key in hex (`quick: key 0x31 ...`) where the text below says scan codes,
and the FOV rows act only with `[View] Fov=1`:

| Key or control | Default | Off (2026-11-09a) |
|---|---|---|
| `[Look] KitStash` (`CMB_LookOptions` 128) | 1 | 0: the field kit not linked to Global Stash by SKK's stash |
| `[Look] KitRetry` (256) | 1 | 0: being in the kit at its opening counts as working, however short; no second try |
| `[Look] MountEarly` (512) | 1 | 0: 2026-11-09a's getting on, the screen back at "Mounted." |
| `[Look] RideReady` | 1 | 0: `CMB_RideReady` never written (getting on then waits its 1 s) |
| `[Look] WornColoursFirst` (1024) | 1 | 0: the colour values written after the worn bike's equip |
| `[Look] HueSwap` (2048) | 1 | 0: no F4SE swap while the plugin writes the colours |
| `[Diag] WornColour` | 1 | 0: no `look: the worn paint` lines |
| `[Steer] QuickUse` | 1 | 0: the game's own animated hotkey use |
| `[Steer] QuickUseAbove` | 150 (u/s) | (a parameter: slower, the game's own use) |
| `[Steer] QuickKeys` | 2,3,4,5,6,7,8,9,10,11,12,13 (scan codes: slots 1-12) | (a parameter: re-maps the keys to the slots) |
| `[Steer] UseStopCue` | props | any |
| `[Steer] UseStopNotUnder` | WEAPON | empty |
| `[Steer] UseStopAt` | props | knees |
| MCM Riding "Caution" (`CMB_Caution`) | 50 for a new save (a save keeps its own) | 60 |
| `[Steer] SidestepCaution` | 60 | 0: the rays at your Caution's own reach |
| `[Steer] SidestepMouse` | 5 (deg) | 3 |
| `[Room] GuardBodies` | 1 | 0 |
| `[Room] GuardFloor` | 1 | 0 |
| `[Room] GuardPlayerZ` | 150 (units) | 0: the player's height ignored |
| `[View] Parent` | 1 | 0: the first-person bike stays under its own cell |
| `[View] Update` | 1 | 0: the plugin's own writes only (2: also its parent's update) |
| `[Diag] ViewDraw` (2026-11-09a's key) | 2 | 1: 2026-11-09a's three lines (0: none) |
| `[Diag] ViewDrawEvery` | 10 (seconds) | 0: with every 2-s probe |
| `[Diag] ViewThird`, `ViewThirdOffset` | 0, 150 | (an A/B for TESTING's step 10: 1 shows the first-person bike 150 to your right in third person) |
| `[View] FovSearch` (2026-11-09a's key) | 2 | 1: 2026-11-09a's search (0: 2026-11-08a's) |
| `[View] TipYield` (2026-11-09a's key) | 15 (deg) | 5 |
| `[Sound] MenuHold`, `MenuRejoin` | 1, 1.0 (seconds) | `MenuHold=0` |
| `[Sound] ShiftGapGears` (2026-11-09a's key) | 0,2,3 (0,2,3,1.5 since 2026-11-14a, 0,1.8,2,1.7 since 2026-11-21a) | 0,2,2.5 |
| `[Fx] WaterGentleDb` | 0 (dB) | -3: 2026-11-09a's level with the new loop (0 is 2026-11-09a's plugin) |
| `[Diag] Paused` | 1 | 0: no lines |
| the front end's shadow (the meshes and materials) | cast | the 2026-11-09a build's files |

What they do:
- **KitStash, KitRetry** (`CMB_LookOptions` 128 and 256; test 52: the field kit's menu shut after 0.17 s, 12 times of
  12): another mod, Global Stash by SKK (`SKKGlobalStashScrapping.esp`), links every workbench you use to its stash the
  first time, and to do it disables and enables the bench, which throws you out of its menu; every field kit is a new
  bench. With SKK installed the kit is now linked to SKK's stash, with SKK's own keyword, before it opens, wherever SKK
  would link it itself (its auto transfer in a settlement, its standalone-workbench link elsewhere): SKK then leaves it
  alone and the kit's components are the stash's (`Field kit: Global Stash by SKK: the kit linked to its stash first
  (SKK_GSSKeyword ..., the stash ...; its auto transfer on): its workbench handler leaves the kit alone`, then at the
  activation `Field kit: mode 3: the kit's link at the activation: the stash`). And a kit menu that closes within half a
  second (`KitFastClose`, 0.5 s) with nothing changed never counts as working, wherever you were: the same kit is used
  once more by itself, and if that closes as fast too, the next kind of kit is tried (the armour bench, then the game's
  own): `Field kit: mode 3: the menu closed 0.17 s after it opened, no change: under KitFastClose 0.5 s, the player in
  the kit at its open doesn't count: the kit used again (KitRetry), enabled again after 0.6 s`, or the second time
  `Field kit: mode 3: the menu closed again ... s after it opened, no change: ...: used again once already (KitRetry):
  this mode doesn't work here`. If SKK throws you out of a kit it was linked for all the same, the retry leaves SKK's
  own link as it is (`Field kit: mode 3: the pre-linked kit closed fast all the same: the retry keeps its link as it is
  (...), no read-back`), and the kit is linked only to a stash that is a container (`Field kit: Global Stash by SKK:
  installed, but its stash ... isn't a container (another version?): not linked`, where SKK links it itself and the
  retry opens it). Without SKK nothing else changes: no call to it, and a menu you leave within half a second comes
  back once.
- **QuickUse, QuickUseAbove, QuickKeys** (test 52: a stimpak by its hotkey at speed was never used: the use clip, which
  the game applies the item at, was cut before it got there): riding at 150 u/s or faster, a potion on a favourites
  hotkey (a stimpak, a chem, food or a drink) is used at once, without the game's use animation, so the bike keeps its
  speed. The plugin takes the key from the game (it wraps the favourites' key handler, found through the Address
  Library, after checking what it is) and writes `CMB_RiderQuickUse`; the F4SE hotkey script reads it, takes the item in
  that slot and equips it the way the Pip-Boy does. Weapons, grenades and armour on hotkeys, a gamepad and a slower bike
  work as before, and so does a press in the first second or so after getting on, before the hotkey script's watch is
  on (`quick: key 2 (the slot 1, the game's '...') at 640 u/s: 00023736, a potion, but the script's watch not on yet
  (CMB_RiderQuickUse 0): the game's own hotkey use (QuickUse)`): the plugin takes a key only while that watch is on. The
  log names a key by its keyboard scan code, not by its label: the number row's 1 is scan code 2, 2 is 3, and so on to
  9 = 10, 0 = 11, - = 12 and = = 13, which are slots 1 to 12, so number key 1 shows as `key 2 (the slot 1, ...)`. A
  press: `quick: key 2 (the slot 1, the game's '...') at 812 u/s: Stimpak (00023736, a potion) handed to the script's
  watch, not the game's animated use (allowStimpakUse 1): CMB_RiderQuickUse 17` and, in `Papyrus.0.log`, `Used [Form
  <Stimpak (00023736)>] by its hotkey at speed: equipped by the script (QuickUse, slot 1).`. The session's first
  ride says whether the handler was wrapped: `quick: FavoritesManager (Address Library
  4801690) +0x...: its OnButtonEvent wrapped (QuickUse; ...)`, or `...: <why>: nothing wrapped, the hotkeys are the
  game's own (QuickUse)`. `QuickKeys` re-maps the keys for another hotkey layout.
- **UseStopCue, UseStopNotUnder, UseStopAt** (the checker's finding 2 on 2026-11-09a): the use-clip stop now acts only
  on an item's props in your hands, never on a drawn weapon (a new shape under the `WEAPON` node is a weapon's: `rider:
  new shapes <shape> < WEAPON < RArm_Hand, under WEAPON: a weapon's, no item's cue (UseStopNotUnder)`), and
  stops the clip at the props' first frame instead of when the knees leave the seat (`rider: an item's use clip at 786
  u/s (its props, Stimpack:0 < AnimObjectR1 < RArm_Hand, this frame): IdleStop sent to the graph (UseStop): taken; ...`).
- **MountEarly, RideReady** (`CMB_LookOptions` 512; test 52: 3-5 s from the press to riding, the screen black for
  3.0-3.6 s of it): the worn bike goes on right after the screen fades (its look synced first), then the camera, the
  parked bike's disable, the pose, the controls and the ride's tick; the screen comes back as soon as the plugin says the
  bike is ready (`CMB_RideReady` 1: the worn bike's shapes held and coloured, you held and seated, or with the MCM's
  "Bike tilts with the ground" at 0, where you aren't held, the bike held and coloured and you seated; at most
  `MountReadyWait`, 1 s, after the controls), and the rest (followers, the headlamp, the ride's watches) happens after
  it. Estimated from test 52's timings, not yet seen in the game: the black about 1.1-1.3 s with the stock look and
  1.6-2.1 s with a full look; the press to riding about 2.0-2.8 s. The real split is in `Papyrus.0.log` at each getting
  on: `Getting on: the press 0.00, the fade 0.31, the equip 1.12, the pose 1.40, ready 1.92 (CMB_RideReady after 0.80
  s), the screen back 1.95, Mounted 2.66 (real seconds)`, and in `CMB_Slope.log`: `getting on: the bike ready 0.25 s
  after CMB_TiltLive (50 shapes held, 3 colours written, the rider on the seat): CMB_RideReady 1` (or `getting on: the
  bike not ready 1.0 s after CMB_TiltLive (...)`, which names what was missing); at the MCM's tilt 0 the clock is the
  ride's start: `getting on: the bike ready 0.67 s into the ride, the MCM's tilt 0 (... the rider not held (the MCM's
  tilt 0), the knees on the seat): CMB_RideReady 1`, or `getting on: the bike not ready 2.0 s into the ride, the MCM's
  tilt 0 (...)`. The "no bike shape" check (test 52's false alarm) now counts from `CMB_TiltLive`, or from the ride's
  start with the tilt at 0.
- **WornColoursFirst, HueSwap, WornColour** (1024 and 2048; test 52: Free colour rode blue on the first ride after an
  Apply): the colour values are written before the worn bike goes on, so the plugin's first write into its new shapes
  is this look's, and with Free colour the game's own colour swap runs once after the fade too (`Look: Free colour on
  the worn bike: the plugin writes it, and the F4SE swap once after the fade too (HueSwap)`). `[Diag] WornColour` reads
  the ridden paint back 0.5 s and 2 s after its write (`look: the worn paint 0.5 s on: CMB_BikeWornRiderF_static_paint
  the shape ... under the 3D root, its property the same, its material the same (...paint_hue_p.dds, 0.4995; written
  0.4995); 1 static_paint shape(s) under the 3D root, 1 through the biped (1 in all)`): if the colour is ever wrong
  again, those lines say whether the paint drawn is the one written.
- **Caution 50, SidestepCaution, SidestepMouse** (test 52 rode Caution 50: 8 sidesteps of 27, six lost because the post
  was found too late): a new save starts at Caution 50, where the bike eases off about 7 m from an obstacle at full speed
  and the throttle is gone at about 5 m; a save keeps the value it has (set 50 on the MCM's Riding page to try it; 60
  was 2026-11-09a's default). The sidestep still finds a post, a mailbox or a lamp at Caution 60's reach: when your
  Caution's rays find nothing ahead, the two longer rays are cast again to 60's reach, and what they find goes to the
  sidestep alone, the throttle keeping your Caution's verdict (`sidestep: <thing> at 578 (found by Caution 60's reach,
  SidestepCaution; the throttle Caution 50's): the rays to 582 past the front wheel, Caution 50's own to 527`, right
  after the sidestep's start line). A mouse move under 5 degrees no longer cancels a sidestep (test 52's let-gos came at
  3.1-3.5 degrees); a bigger one does, as before (`sidestep: let go after ... s: the game's own target moved N deg (the
  mouse) ...`). The fallback with no `CMB_Caution` (`[Steer] Caution=-1`, an older ESP) is 50 too.
- **GuardBodies, GuardFloor, GuardPlayerZ** (the checker's findings 1, 4 and 7a on 2026-11-09a): the parked bike stays
  hidden while anyone is in its place, now also an NPC knocked down there (their body without its capsule: `room: ask
  N at (...), heading H (the parked bike's place: ParkGuard): someone in it: XXXXXXXX (skeleton.nif, layer 8: a body, no
  capsule met), ...`), and a dog or a crouching NPC right beside the bike once it has settled (the guard's ray down
  landing on the bike's own top no longer counts as the ground, and its rays pass the bike's own 3D: `... (the ground
  taken at the bike's place: the ray stopped 61 over it, on the bike)`); and you count only within 150 units of its
  ground, not from a bridge or a balcony above it (`...: no one in it (21 rays down, 16 across); the player 300 above it:
  not counted (GuardPlayerZ)`).
- **Parent, Update, ViewDraw=2, ViewDrawEvery, ViewThird** (first person; test 52: the bike still never seen, with
  `Cull=1` and `Near=5` too, every chain of its parents through the cell's multibound node): two levers, both on. `[View]
  Parent=1` moves the first-person bike under your own cell's node while it shows (the game draws a cell's objects by
  that cell's box, and the bike is placed in the cell where you got on): it is put back at third person, getting off, a
  load, a door, a handover, and whenever either cell changes, with its safety rules (DESIGN.md, *The bike in first
  person*): `view: Parent: the view bike's 3D moved from ... to the player's cell ...'s (it showed outside by N of its own
  cell's box), for the reference FFxxxxxx`, `view: Parent: put back under its own cell (third person)`. `[View]
  Update=1` runs the game's own update on it after the plugin's placement, and turns itself off for the session, with a
  line, if the game puts it elsewhere (`view: the game's update put the view bike's root N from ours (the first shape N):
  [View] Update off this session`). The diagnostic that should settle why it isn't seen, `[Diag] ViewDraw=2` (the new
  default), logs four more lines: `view: drawn? the flags: ...` (its draw flags against the worn bike's), `view: drawn?
  the fade node: ...`, `view: drawn? the cell's multibound: ...` (the cell's box against the bike and the eye) and `view:
  drawn? the player's cell: ...`, at each first person's first frame and then every 10 s (`ViewDrawEvery`; an unchanged
  chain is one short `view: drawn? the chain as before (...)` line, and no line is over 900 characters: test 52's log had
  417 of them a showing). `[Diag] ViewThird=1` is an A/B for one test step: in third person it shows the first-person
  bike 150 to your right (`view: third person: the view bike shown 150 to your right ([Diag] ViewThird): is a second
  bike there?`). Test 53 says whether the bike shows now.
- **FovSearch=2** (test 52: the riding field of view never found; the camera's live pair read 80 and 80 at +0x168 and
  +0x16C): the riding field of view (the MCM's slider till 2026-11-10a) now tries the camera's own two fields, the world
  FOV at PlayerCamera+0x168 first, checked against the camera's frustum, and keeps it only if the view widens with it
  0.1 s on (`camera: the world FOV at PlayerCamera+0x168 (...), 0.51 s into first person (FovSearch=2)`, then `camera:
  the world FOV at PlayerCamera+0x168 (...): followed, kept (...)`); otherwise it is put back and the first-person field
  is tried at the next entry (`camera: PlayerCamera+0x168 not followed (...): put back; +0x16C at the next entry`).
  Neither field a field of view: 2026-11-09a's search.
- **TipYield 15** (test 52: right after a load the tip was taken over by a 5-8 degree mouse move): your own look adds to
  the 20-degree look down and stops it only past 15 degrees.
- **MenuHold, MenuRejoin** (test 52: the Pip-Boy at speed dropped the engine to 1st with the clutch in, then it climbed
  through the gears again after the close): while a menu pauses the game the engine's note is held as it was (`sound:
  held at gear 3, 2315 rpm, heard 891 u/s while a menu pauses the game (UI menu mode 1)`), and after the close the speed
  held is fed for at most `MenuRejoin` (1 s) until the bike's own reading is back (or the brake goes on): `sound: resumed
  after 3.1 s: gear 3, 2320 rpm, heard 893 u/s; the held 895 u/s fed 0.40 s (the reading back to 810)`.
- **ShiftGapGears 0,2,3** (test 52's wish): 3rd lasts about 3 s on a full-throttle pull (1st about 1.5 s, 2nd 2.0, 3rd
  3.0; 4th about 6.5 s from a standstill, where it was 6.0); the climb back after a hard brake in 3rd is 0.5 s longer too.
  The settings line: `  sound: HeardRiseGears=2.5,0.95,0.5,1 ShiftGapGears=0,2,3: ... at least 1.25, 2, 3 s in gears 1-3
  before an up-shift (0 or missing: MinShiftGap)`.
- **The gentle water louder** (test 52's wish): "Wet road, gentle" (the MCM's "Water sound loop", the default) is 3 dB
  louder, its sound as before (the loop rebuilt from the same recording at -23.5 dBFS A-weighted, where 2026-11-09a's was
  -26.5). `[Fx] WaterGentleDb` trims it alone, in dB: -3 plays it at 2026-11-09a's level; the driven line ends `..., the
  gentle wet road (CMB_FxWaterLoop 3), WaterRoadDb +0 dB, WaterGentleDb +0 dB`.
- **Paused** (test 52: the engine silent for 16-20 s after getting on, the game paused or out of focus for most of it):
  no change in behaviour, a diagnostic. During a ride the plugin logs the game's window out of focus (`game: the window
  out of focus 13:42:33.7-13:42:43.8 (10.1 s)`), the world paused by a menu (`game: the world paused ... (10.2 s: the
  movement update 0 times)`) and the game's frame stopped (`game: the frame task didn't run for 6.97 s (...)`), each of
  a second or more, and the engine's late hand-over line says how much of its wait that was (`sound: generation N handed
  over 13.4 s after the ride's start (usually 3), 10.1 s of it paused or out of focus`).
- **The front end's shadow** (test 52's wish; no key): the front wheel, the fork and the bars cast their shadow in the
  sun while you ride, as the parked bike's always did (from test 34 to 2026-11-09a they cast none, for the headlamp's
  beam; the shadow lamp sits `[Lamp] Ahead` 28 past the lens since test 35). Only the four worn and first-person meshes
  and 76 materials files changed, each in its shadow flag alone.
- **CMB_LookOptions, CMB_RiderQuickUse, CMB_RideReady**: `CMB_LookOptions` (0xBF4) carries five more switches for the
  scripts, 128 KitStash, 256 KitRetry, 512 MountEarly, 1024 WornColoursFirst and 2048 HueSwap: the plugin writes 4095 at
  its defaults, and without F4SE the ESP's 4031 (all but 64, the plugin's own) is used. Two new globals: `CMB_RiderQuickUse`
  (0xBF5, the potion taken from a hotkey) and `CMB_RideReady` (0xBF6, the bike ready at getting on).

Each part's settings line is in `CMB_Slope.log` at the start: `  look (2026-11-10a, test 52): KitStash=1 KitRetry=1
MountEarly=1 WornColoursFirst=1 HueSwap=1 RideReady=1; [Diag] WornColour=1: CMB_LookOptions 4095 for the scripts`,
`  rider (2026-11-10a, test 52): QuickUse=1 QuickUseAbove=150 QuickKeys=2,3,4,5,6,7,8,9,10,11,12,13 UseStopCue=props
UseStopNotUnder=WEAPON UseStopAt=props`, `  drive (2026-11-10a, test 52): SidestepCaution=60 SidestepMouse=5; [Room]
GuardBodies=1 GuardFloor=1 GuardPlayerZ=150`, `  view (2026-11-10a, test 52): Parent=1 Update=1; [Diag] ViewDrawEvery=10
ViewThird=0 ViewThirdOffset=150` and `  sound (2026-11-10a, test 52): MenuHold=1 MenuRejoin=1.0; [Diag] Paused=1; [Fx]
WaterGentleDb=+0 dB`; the 2026-11-09a build's lines now read `  view (2026-11-09a): TipMenu=1 TipYield=15 TipSettle=0.25
Bounds=1 Near=0 FovSearch=2; [Diag] ViewDraw=2` and `... LightingOnly=1: CMB_LookOptions 4095 for the scripts (64: the
worn bike's colours written here)`. The plugin finds the build's two globals by their IDs (`globals: the 2026-11-10a
build's 2 found, CMB_RiderQuickUse and CMB_RideReady (FE005BF5-FE005BF6)`; with an older ESP `globals: no
CMB_RiderQuickUse or CMB_RideReady (0xBF5-0xBF6, an older ESP): QuickUse and RideReady do nothing`).

Known, left for now:
- With an animation mod that plays a decoration after each item use (the item animation mod and the like), a hotkey use
  at speed still starts that decoration, which is cut at its first frame: a dip of about 100-150 u/s for about 0.3 s, as
  after a use from the Pip-Boy.
- Hotkey N uses favourites slot N (F4SE lists the slots in order); if a key ever uses another slot's item, `[Steer]
  QuickKeys` re-maps the keys, or `QuickUse=0`. Another plugin that already wraps the favourites' key handler leaves
  QuickUse off (its line says so).
- Caution 50 is only a new save's default: a save from an earlier build keeps its own (set it on the MCM's Riding page).
- With `[Lamp] Ahead` set under about 10 and MCM "Headlamp casts shadows" on, the bike's front end can shadow its own
  beam again (the default 28 keeps it clear).
- The first-person bike may still be unseen: send the `view: drawn?`, `view: Parent:` and `view: the game's update` lines.
- When getting on, a follower is stowed and the headlamp lit up to about a second after the screen is back.
- A menu that pauses the game while the bike really stops would resume at the held speed for at most `MenuRejoin` (none
  known); the gentle water's 3 dB also lifts the shallow splash (its shape is unchanged).

### The 2026-11-09a build's keys (still there; off = 2026-11-08a)

Every new behaviour of the 2026-11-09a build (tests 50 and 51) has a key or an MCM control whose off value gives the
2026-11-08a build back (for the gears, their rows give the build's first set too); five of its defaults changed in the
2026-11-10a build and two in the 2026-11-14a build (in brackets in the table):

| Key or control | Default | Off (2026-11-08a) |
|---|---|---|
| MCM Riding "Caution (how early the bike eases off for obstacles, %)" (`CMB_Caution`, new) | 60 (50 for a new save since 2026-11-10a) | 100 |
| `[Steer] Caution` | -1: the MCM's (50-100 here overrides it) | 100 |
| `[Parts] WheelSpin` | 1 | 0: the wheels turn by the 0.2 s speed (they run on after a stop) |
| `[Parts] WheelStill` | 5 (u/s) | (a parameter: no turning under it) |
| `[Parts] WheelLock` | 1 | 0: the wheels turn while braking |
| `[Steer] ClimbStepSpan` | 3 | 0: a step up judged by the one ray a wheelbase on |
| `[Room] SnapOrder` | 1 | 0: the most room's flat snap first |
| `[Room] ActorRoom` | 1 | 0: an actor in a spot passed, as before |
| `[Room] ParkBack` | 1 | 0: the bike put back where it stood without asking |
| `[Room] ParkGuard`, `GuardMargin` | 1, 15 | `ParkGuard=0`: the parked bike shown at once |
| `[Steer] UseStop` | IdleStop,IdleForceDefaultState | empty: nothing sent |
| `[Steer] UseListen` | 2.0 (seconds) | 0: no line |
| `[View] TipMenu` | 1 | 0: the Pip-Boy's first person tipped as any |
| `[View] TipYield` | 5 (deg; 15 since 2026-11-10a) | 0: a move of 0.1 deg in a frame stops the tip |
| `[View] TipSettle` | 0.25 (seconds) | 0: the tip from the first frame on the bike |
| `[View] Bounds` | 1 | 0: the view bike's parents in the scene left as they are |
| `[Diag] ViewDraw` | 1 (2 since 2026-11-10a) | 0: no `view: drawn?` lines |
| `[View] Near` | 0: never written | (an A/B for TESTING's step 9: 5 puts the camera's near plane at 5 while the view bike shows) |
| `[View] FovSearch` | 1 (2 since 2026-11-10a; only with `[View] Fov=1` since 2026-11-14a) | 0: one search at the first want, +0x100..+0x1F0, degrees only |
| `[View] FovOffset` (its range) | auto | (0x40-0x1AC with `FovSearch=1`, within PlayerCamera; 0x100-0x1F0 with 0) |
| `[Sound] HeardRiseGears` | 2.5,0.95,0.5,1 (test 51; 2,0.79,0.65,1,1 since 2026-11-14a, 2,0.86,0.8,1,1 since 2026-11-21a, 2.1,1.35,1,1,1 since 2026-11-23a) | 1,1,1,1 (or empty); 1,0.95,0.5,1 the build's first set |
| `[Sound] ShiftGapGears` | 0,2.0,2.5 (test 51; 0,2,3 since 2026-11-10a, 0,2,3,1.5 since 2026-11-14a, 0,1.8,2,1.7 since 2026-11-21a) | empty; 0,1.5,1.75 the build's first set |
| MCM Sound "Water sound loop" (`CMB_FxWaterLoop`) | "Wet road, gentle" (3, new) | "Wet road (the mod's own)" (2) |
| `[Look] FastMount` (test 51) | 1 | 0: the worn bike removed at every getting off, its mods attached at every equip and its colours swapped there and again |
| `[Look] MountGuard` | 1 | 0: the look synced before the parked bike's menu, no activation guard, no watchdog |
| `[Look] KitHeld` | 1 | 0: the toolbox first, remembered when its menu opens |
| MCM Look "Field kit" (`CMB_KitMode`) | Automatic: the armour bench, then the game's ("The game's armour bench", 4, new) | (`KitHeld=0`) |
| `[Look] PaletteIndex` | 1 | 0: the paint and rim entries as their records hold them |
| `[Look] ParkedReload` | 1 | 0: no reload |
| `[Look] HueFree` | 1 | 0: the hue only with Free colour chosen |
| `[Look] Rehold` | 1 | 0: the hold stays on the old shape |
| `[Look] LightingOnly` | 1 | 0: no shader check |
| `[View] TipLoadGrace` | 2 (seconds) | 0: a tip verdict holds for the session |

What they do:
- **Caution**: how early the bike eases off for a wall or a car ahead (test 50: "over cautious"). At 60% it lets the
  throttle off from about 8 m at full speed (583 units past the front wheel) and has none left from about 6 m (421); at
  100% (the 2026-11-08a build) from about 11 m (805) and none from 535. The MCM's slider is read on getting on and once
  a second while riding, so it can be changed mid-ride (`steer: Caution 60% -> 100% (CMB_Caution): ... (the MCM)`).
  50% is the floor (test 45's rail met square at full speed still stops in time). Technically: `FaceLook` and
  `WallStopPersist` times Caution, `WallStop` divided by 0.5 + Caution/2, and under 100% the stop's need from the
  quicker speed (0.05 s), so the throttle comes back sooner once the bike has slowed; WallStop's lines end
  `..., Caution 60%)`. A wall seen only inside FaceLook's reach (a glimpse) gets less margin at 60%, and the sidestep
  starts later (a post first read about 575 units past the front wheel instead of about 725): 70% gives both back.
- **WheelSpin, WheelLock**: the wheels turn by how far the bike really moved each frame, so they stop when it stops (none
  under `WheelStill`, 5 u/s), and they hold still while braking (back or the brake key at speed); reversing turns them
  backward as before. The needle is unchanged. The settings line: `  parts: the wheels turn by the frame's own movement,
  none under 5 u/s (WheelSpin), held while braking (WheelLock)`.
- **ClimbStepSpan**: a step the climb's boost would take is looked at in three more places between its face and a
  wheelbase on; if its top doesn't carry on (test 50's bridge: an end post with a drop and a rail behind it) there is
  no boost: `climb: ... its top ends within 67 past its face (...): a post, not a step (ClimbStepSpan): not climbed with
  the boost`. Kerbs, steps and pavements are climbed as before (`... its top carrying on at 3 points between
  (ClimbStepSpan)`).
- **SnapOrder** (`CMB_RoomOptions` bit 64): a call with a spot that has room but is off the navmesh (test 50: a truck's
  bed) asks that spot's own navmesh point first, then the spot with the most room measured to the navmesh in 3-D (on
  its own ground), then the most room's navmesh point, then the first spot as before: `The bike's spot: Bike's spot 10's
  navmesh point (126 from it), heading 307: room, walkable (its own snap 4): taken before the most room (spot 9, none
  there) (the plugin's [Room] SnapOrder).`
- **ActorRoom, ParkBack, ParkGuard** (`CMB_RoomOptions` bits 128 and 256, and 512 since the review of test 51's fixes:
  ParkGuard's ask kind 3, the player not counted): the bike never appears inside someone. A spot with an actor met by
  its own rays (and 21 rays down over its box) has no room: `room: ask N at (...), heading N: none, an actor in its
  place: ... (ActorRoom)`, with the actor's reference ID. After a short ride the bike is put back where it stood only if
  that place is still free (`Parked bike not put back where it stood: its old spot asked about first (the plugin's
  [Room] ParkBack): ...`). While an NPC is within `GuardMargin` (15) of where it would appear it stays hidden, looked at
  again every half second, and shows once the place is clear (`The parked bike kept hidden: someone in its place (the
  plugin's [Room] ParkGuard): looked at again every 0.5 s.`, then `The parked bike shown after N s: its place clear
  (ParkGuard).`). You count only if you stand in the bike's own place, and not at all where the mod has just put the
  bike clear of you (getting off, calling it, bringing it, putting it back where it stood), so it no longer vanishes
  when you get off after a bend or call it into a narrow spot (`... (the parked bike's place: ParkGuard, the player not
  counted): no one in it ...`); a colour reload shows it again at once. After 15 s it tries a spot beside or behind you
  once, and calling it or getting on always ends the wait.
- **UseStop, UseListen**: an item used at speed (a stimpak by hotkey or from the Pip-Boy) whose use clip still starts
  (test 50: the item animation mod's idle doesn't pass the graph slot `UseBlockAbove` refuses) is stopped as it starts:
  the plugin tells the animation graph `IdleStop`, then `IdleForceDefaultState` if the first isn't taken (`rider: an
  item's use clip at N u/s (...): IdleStop sent to the graph (UseStop): taken; ...`). It acts only at
  `UseBlockAbove` (150 u/s) or faster, with an item used within `UseLetGo` (4 s) or its props just in the hands, and
  once a clip. `UseListen` lists the animation graph's events through that slot for 2 s after each item, for the next
  fix (`rider: the graph's events through PlayerCharacter's slot 1 in the 2.0 s from ... (UseListen): ...`).
- **TipMenu, TipYield, TipSettle**: the Pip-Boy opened from third person is a first person of its own (test 50: the
  tip fired there, five times in five); now no tip when an entry's first frame has the eye far from its place on the
  bike (`view: no tip: this first person began with the eye N from EyeAt (a menu's camera: the Pip-Boy from third
  person)`) or while the controller says the Pip-Boy is open (the global `CMB_ViewMenu`: `view: no tip: the Pip-Boy
  open (CMB_ViewMenu)`). Your own look while the view eases down adds to it and stops it only past `TipYield` (5
  degrees): `view: you looked yourself N deg up over N frame(s), ...: stopped at ...`. The tip starts `TipSettle`
  (0.25 s) into the entry, once the camera has settled.
- **Bounds, ViewDraw, Near**: test 50's log said the first-person bike was shown, but it was never seen. The plugin now
  grows the world bounds of its parents in the scene to hold it (the game only does that for its own moves) and logs
  three `view: drawn?` lines at each entry and with each 2-s probe: the chain of parents, the camera's frustum and near
  plane, and whether last frame's writes held. `Near` is an A/B for TESTING's step 9 only: `[View] Near=5` puts the
  camera's near plane at 5 while the view bike shows (`view: the camera's near plane 15 -> 5 while the view bike shows
  ([View] Near)`).
- **FovSearch**: the riding field of view's field (test 50: not found) is looked for half a second into first person,
  again at the next entries up to 3 times until a load, over PlayerCamera+0x40..+0x1AC (within its 0x1B0 bytes on
  1.11.240, so nothing past its end is read or written): the pair in degrees or in
  radians, the world FOV alone, or the world camera's frustum (`camera: the world FOV at PlayerCamera+0x... (...),
  0.50 s into first person (search 1 of 3)`, or `... not found ...; candidates: ...` with what it saw).
- **HeardRiseGears, ShiftGapGears**: each gear's own rise of the heard speed (`HeardRise` times each) and its least
  time before the next up-shift (0: `MinShiftGap`). Since test 51 (1st lasted about 3.5 s, longer than 2nd and 3rd)
  the defaults make each gear longer than the last at full throttle from a stop: 1st about 1.6 s, 2nd 2.0, 3rd 2.5
  (this build's first set gave about 3.8, 1.5 and 1.75; 2026-11-08a 3.8, 1.46 and 1.25). On a slow uphill pull 2nd can
  outlast 3rd. The settings line: `  sound: HeardRiseGears=2.5,0.95,0.5,1 ShiftGapGears=0,2,2.5: the heard speed's rise
  by gear 350, 133, 70, 140 u/s^2 (HeardRise x each); at least 1.25, 2, 2.5 s in gears 1-3 before an up-shift (0 or
  missing: MinShiftGap)`. `HeardRiseGears=1,0.95,0.5,1` with `ShiftGapGears=0,1.5,1.75` is the first set; `1,1,1,1`
  with `ShiftGapGears=` empty is 2026-11-08a's. Known: after a quick tap of the brake at the cruise the engine climbs
  back in 3rd for about 5 s where it took 2.5 s (3rd's rise is unchanged); `HeardRiseGears=2.5,0.95,0.7,1` shortens
  that, if it bothers you.
- **"Wet road, gentle"**: the same recording as "Wet road (the mod's own)", filtered for less hiss and more body (under
  250 Hz 11% of its power instead of 2%, 1-2 kHz 30% instead of 41%, over 4 kHz 1% instead of 7%), 3.5 dB quieter;
  `[Fx] WaterRoadDb` trims both wet roads. Papyrus: `Bike sounds: the plugin drives the water loop: the gentle wet road
  (CMB_FxWaterLoop 3) (instance N, poll N).`
- **FastMount** (test 51; `CMB_LookOptions` bit 1): getting on is quicker (test 51: 5-6 s, the look's mods attached and
  its colours swapped behind the fade, twice). The worn bike's two riding armours now stay in your inventory between
  rides, unequipped and hidden (non-playable, no weight, no value), with the look's mods on them. Getting on with the
  look unchanged takes about 1.5 s (`Look: the worn bike's kept mods (the look unchanged): no attach`), and drawing or
  holstering a weapon mid-ride no longer pauses; a changed look attaches its mods once (about 3 s). The worn bike's
  colours are written once at getting on: by the plugin when `[Look] PaintWheel` and `PlateColours` are 1, otherwise
  by one F4SE swap after the screen fades back in. A look changed while riding goes on the parked bike when you park
  it. `cqf CMB_ControllerQuest EmergencyReset` (off the bike, before uninstalling) takes the kept armours out of your
  inventory too.
- **MountGuard** (bit 16): activating the parked bike twice quickly opens one menu; the second press is ignored
  (`Parked bike activated again N s into the last activation (its menu or choice under way): ignored`; test 51's black
  screen after Ride was most likely a second menu queued behind the fade). The menu comes before any look work, and
  Ride does none of its own. If getting on is ever held up, a watchdog fades the screen back in after 8 s and logs
  where and which menus were open (`Getting on: not mounted N s after its fade (at ...; ...): faded back in (the
  watchdog)`); after 25 s out of every menu the ride is given up ("The motorbike couldn't be got on. Try again.").
- **KitHeld** (bit 2): the field kit should work now (test 51: never; the toolbox can't be sat in, and a mode was
  remembered as soon as its menu opened). Automatic puts an armour bench beside the bike, and if its menu closes at
  once, the game's own armour bench (Fallout4.esm's `WorkbenchArmorA`, the MCM's "The game's armour bench"). A bench
  counts as working once its menu stayed open 2 s, you made a change, or you were at it; that one is remembered
  (`CMB_KitWorked` 3 or 4), and a remembered toolbox from an older build is forgotten once. The look's 263 recipes no
  longer name the mod's own bench keyword (BNAM; the game's 722 armour mod recipes name none either).
- **PaletteIndex, ParkedReload** (bits 8 and 4): after an MCM apply the parked bike shows the new paint and rim finish
  at once (test 51: grey until the next ride). Each paint and rim finish gets its own palette colour, and the parked
  bike's 3D is loaded again: it vanishes for a moment (behind the pause menu until you close it) and comes back at
  once, whoever stands beside it (`Look: the parked bike's 3D loaded again for its colours (the MCM, ParkedReload)`).
  Each key at 0 turns its half off.
- **HueFree** (bit 32): moving the MCM's "Paint hue" or "Paint shade" chooses Paint "Free colour" when you Apply (or at
  the next activation or getting on), unless a faction set is applied with it or you choose another Paint in the same
  visit (test 51: "it didn't do anything": the hue colours only Free colour). `HueFree=0`: the hue colours only a Paint
  already set to Free colour.
- **Rehold, LightingOnly** (the plugin's own; the checker's findings): when the game rebuilds the worn bike's 3D in
  place, the plugin moves to the new shapes, so they keep tilting, hiding and taking the look's colours; the look's
  colours are written only into the game's lit materials, never into a part with another kind of shader. 0: as before.
- **TipLoadGrace** (2 s): if the first-person tip's self-check turns the tip off (or flips it) within 2 s of a load or
  of getting on, that holds for that entry only and the next entry tries again (test 51: off for the whole session
  after a load); 0: until the game is restarted. ViewDraw's chain line now ends `, for the reference FFxxxxxx`.
- **CMB_LookOptions** (0xBF4, new): the scripts read the six switches above (FastMount 1, KitHeld 2, ParkedReload 4,
  PaletteIndex 8, MountGuard 16, HueFree 32) through this global, which the plugin writes from `[Look]` at its start,
  at a load and on getting on (64 more when the plugin writes the worn bike's colours itself: 127 by default); without
  F4SE the ESP's 63, all six on.

Each unit's settings line is in `CMB_Slope.log` at the start: `  steer: Caution=-1: the MCM's CMB_Caution, read on
getting on and once a second while riding; ClimbStepSpan=3: ...`, `  room: SnapOrder=1: ...`, `  room: ActorRoom=1
ParkBack=1 ParkGuard=1 GuardMargin=15: ...`, `  rider: UseListen=2 UseStop=IdleStop,IdleForceDefaultState: ...`,
`  view (2026-11-09a): TipMenu=1 TipYield=5 TipSettle=0.25 Bounds=1 Near=0 FovSearch=1; [Diag] ViewDraw=1`, the
sound line above, `  look (2026-11-09a fixes): FastMount=1 KitHeld=1 ParkedReload=1 PaletteIndex=1 MountGuard=1
HueFree=1 Rehold=1 LightingOnly=1: CMB_LookOptions 127 for the scripts (64: the worn bike's colours written here)`
and `  view (2026-11-09a, test 51): TipLoadGrace=2 (a tip verdict within 2 s of a load or getting on holds for that
entry only; 0: for the session)`; the plugin finds the build's globals by their IDs (`globals: the 2026-11-09a
build's 2 found, CMB_Caution and CMB_ViewMenu (...)` and `globals: the 2026-11-09a fixes' CMB_LookOptions found
(...)`; with an older ESP `... 0 of 2 found (0xBF1-0xBF2, an older ESP): none used` and `globals: no CMB_LookOptions
(0xBF4, an older ESP): ...`).

Known, left for now: a bike kept hidden by ParkGuard when you go through a door or fast travel stays hidden where it
waits until you call it (`The parked bike kept hidden after N s: the player went elsewhere: it waits there hidden;
calling it brings it (ParkGuard).`); test 50's crash fix and the view bike's Bounds fix are each about half sure until
the game shows them; the first-person bike under the first-person 3D, the riding FOV on by default and a fix through
the item animation mod's own idle path wait for test 52's answers; the getting-on watchdog's lines (`Getting on: not
mounted ...`), if you ever see them, are wanted.

### The 2026-11-08a build's keys (still there; off = 2026-11-07a)

Every new behaviour of the 2026-11-08a build has a key or an MCM control whose off value gives the 2026-11-07a
build back, and each new slot starts on the bike as it came, so nothing changes until you choose:

| Key or control | Default | Off (2026-11-07a) |
|---|---|---|
| `[Look] Rims` (new; in the INI as a comment, `;Rims=1`: the default) | 1: the ridden and first-person bikes show the rim style fitted at the bike (the cast rim while none is) and the plugin hides the six others, as it hides the mirrors | 0: the plugin hides no rim shape (the materials alone decide what shows) |
| `[Look] PaintWheel` (new) | 1: the Free colour's hue and a body-colour rim's colour written into the ridden bike's paint and rim materials | 0: never written (the ridden bike's colours are then F4SE's swap's alone, at getting on and after a load) |
| `[Look] PlateColours` (new) | 1: the plate's background and letters' colours written into the ridden bike's plate materials | 0: never written (as `PaintWheel=0`, for the plate) |
| each new slot (`CMB_Look_Rims`, `CMB_Look_Tyres`, `CMB_Look_Plate`, `CMB_Look_PlateText`, `CMB_Look_PlateInk`, `CMB_Look_PlateBack`) | Stock (cast), Black, Stock (plain), the plate's own, the plate's own, the plate's own | (the defaults are the 2026-11-07a look) |
| Paint "Free colour (hue in the MCM)" | (not chosen) | any other paint |
| MCM Look "Paint hue" (`CMB_LookHue`), "Paint shade" (`CMB_LookShade`) | 210, Normal (1) | (used only with Paint "Free colour") |
| MCM Look "Crude plate texts" (`CMB_LookPlateCrude`) | on (1) | off (0): the 14 crude texts hidden (a content switch: on is the build's default) |
| MCM Look "Customise at the bike" (`CMB_LookOn`, 2026-11-07a's) | on | off: every slot's first choice, the bike as it came |

**Rims=1** reads `CMB_LookCode` as `[Look] Mirrors=-1` does: since this build its bits 3-6 hold the rim style chosen
at the bike (0 the cast rim, 1-7 Laced, Solid disc, Star five, Turbine, Pre-war steel, Atomic, Scrap plate), and the
plugin's log says each change: `look: the rims now 4, Turbine (CMB_LookCode 0x25, as chosen at the bike)`. The colours:
four globals at fixed IDs, `CMB_LookPaintV`, `CMB_LookRimV`, `CMB_LookPlateV` and `CMB_LookPlateTextV` (0xA14-0xA17; -1
= nothing to write), hold the colour the script chose; each frame while riding the plugin writes it into the ridden
bike's materials that need it and reads it back (`look: CMB_BikeWornRider_static_paint colour 0.5835 written (read
back 0.5835; the paint)`), and leaves a material that can't take it alone, with a line (`look:
CMB_BikeWornRider_static_plate colour 0.0020 not written: its shader property has no palette flag (0x80000000) (the
plate)`). It writes a colour only into a material whose lookup texture is that colour's palette (Free colour's paint:
`paint_hue_p.dds`; a body-colour rim: `paint_hue_p.dds` with Free colour, `paint_p.dds` otherwise; the plate:
`plate_p.dds`; its letters: `plate_text_p.dds`) and leaves any other alone, with a line once a ride (`look:
CMB_BikeWornRider_wheelF_rimStar colour 0.5835 not written: its lookup texture is CMB\Bike\paint_p.dds, not
paint_hue_p.dds (the rim)`); a lookup texture without a readable name is written as before. The colours are the ridden
bike's own look: an Apply while riding leaves them until the ridden bike is put on again. The parked and first-person
bikes get their colours from F4SE's swap (`CMB_LookF4SE`). The meshes' new shapes (the plate split from the bike's black
parts, with a text overlay over it, and seven rim styles on each wheel) are 2026-11-07a's own look or invisible until a
choice is made, and have no key: the 2026-11-07a build's meshes give them back whole.

### The 2026-11-07a build's keys (still there; off = 2026-11-06a)

Every new behaviour of the 2026-11-07a build has a key or an MCM control whose off value gives the 2026-11-06a build
back, and each customisation slot starts on the bike as it came:

| Key or control | Default | Off (2026-11-06a) |
|---|---|---|
| `[Look] Mirrors` (changed) | -1: the mirrors you fit at the bike (the stock ones while nothing is chosen) | 1: always the stock ones on the ridden bike (0, 2 and 3 force the others, as before) |
| MCM Look "Customise at the bike" (`CMB_LookOn`) | on | off: no Customise button, nothing put on at getting on, the parked and first-person bikes back to the stock look at the next getting on, activation of the parked bike, "Apply the look" or load |
| each slot (`CMB_Look_TankL`, `CMB_Look_TankR`, `CMB_Look_Fender`, `CMB_Look_Paint`, `CMB_Look_Mirrors`) | Stock, Same as the left, None, Factory, Stock | (the defaults are the 2026-11-06a look) |
| MCM Look "Field kit" (`CMB_KitMode`) | Automatic (0: the toolbox, then the armour bench) | Armour bench (3) |
| console `CMB_KitWorked` | -1 | -1: automatic starts from the toolbox again |
| MCM Look "Parts from the side bag" (`CMB_KitBagLink`) | on | off: your own components (and a settlement's workshop) only |
| MCM Look "Free customising (no field kit, no cost)" (`CMB_LookFree`), "Faction set" (`CMB_LookFactionSet`) | off, (none) | (off already; a faction set acts only at "Apply the look") |

**Mirrors=-1** reads the global `CMB_LookCode` (which the script writes when a look is put on) each frame while riding:
the mirror chosen at the bike, the stock one while nothing is chosen, and 1 (the stock one) with an ESP older than this
build. The plugin's log says each change: `look: the mirrors now 2, under the bars, egg (CMB_LookCode 0x6, as chosen at
the bike)`. The meshes' new shapes (the tank badge split in two, the rear fender's badge patch, the parked bike's
under-bar mirrors) are invisible or 2026-11-06a's own until a choice is made, and have no key: the 2026-11-06a build's
meshes give them back whole.

### The 2026-11-06a build's keys (still there; off = 2026-11-02a)

Every new behaviour of the 2026-11-06a build has a key or an MCM control whose off value gives the 2026-11-02a build
back:

| Key | Default | Off (2026-11-02a) |
|---|---|---|
| `[Steer] WallNarrowSame` | 1 | 0: any side hit wide |
| `[Steer] WallNarrowHigh` | 1 | 0: the side rays at axle height only |
| `[Steer] Sidestep` | 40 (deg/s) | 0: no sidestep |
| `[Steer] SidestepMost`, `SidestepShift`, `SidestepFrom` | 12, 60, 250 | (parameters: the most it turns off its line, deg; how far across, units; from this speed, u/s) |
| `[Steer] LaunchTau` | 1.5 (seconds) | 0: the even ramp from a tenth |
| `[Steer] LaunchFrom`, `LaunchLead` | 0.25 (0.1 since 2026-11-16b, 0.14 since 2026-11-17a, 0.25 again since 2026-11-23a), 0.45 | (parameters: the throttle a launch starts at; the speed cap's lead meanwhile) |
| `[Steer] UseBlockAbove` | 150 (u/s) | 0: an item's use clip played at any speed |
| `[Steer] UseBlockEvents` | dyn_ActivationAllowMovement | (the animation graph events refused at speed, up to 4) |
| `[Steer] UseHold`, `UseHoldFrom` | 2.0 (seconds), 200 (u/s) | `UseHold=0`: the speed cap through standing clips at speed |
| `[Tilt] PoseViewSettle` | 0.1 (seconds) | 0: the knees and hands measured from the first frame back in third person |
| `[Tilt] UseRearm` | 1 (seconds) | 0: one use clip an item |
| `[Tilt] UseBackTime` | 0.4 (seconds) | 0.2 |
| `[Tilt] PoseOffRewrite` | 1 | 0: `CMB_RiderPoseOff` written only when the plugin's own word changes |
| `[Room] SnapBest` | 1 | 0: the most room taken as before |
| `[Room] SnapDrop` | 250 | 100 |
| `[Sound] IdleDb` (changed) | -9 | -11 (`-10` the tester's choice) |
| `[Sound] ShiftTime`, `ShiftDipTime` (changed) | 0.55, 0.4 | 0.35, 0.24 |
| `[Sound] LaunchFlare` | 0.5 (0.35 since 2026-11-14a) | 0: no launch rev |
| `[Sound] LaunchFlareTime` | 1.2 (seconds) | (a parameter) |
| `[Fx] WaterSpeedFull` (changed) | 900 | 600 |
| `[Fx] WaterCurve` | 2 | 1: the speed's share linear |
| `[Fx] WaterChurnDb`, `WaterRoadDb` | -8, 0 (dB) | (trims of the MCM's two loops; unused with "As the 2026-11-02a build (spray)") |
| `[View] TipTime` | 0.4 (seconds) | (the MCM's "Look down ..." eased over this; 0 = at once) |
| `[View] FovTime` | 0.3 (seconds) | (the riding field of view eased to and back over this; only with `[View] Fov=1` since 2026-11-14a) |
| `[View] FovOffset` | auto | (where PlayerCamera keeps the world FOV: found by its value, or a hex offset 0x100-0x1F0; only with `[View] Fov=1` since 2026-11-14a) |
| `[Look] Cull` (changed) | 0 | 1: hidden parts also culled by the game's flags |

What they do:
- **WallNarrowSame, WallNarrowHigh**: a post, mailbox or pump met off-centre is narrow when a side ray meets only its
  own placed object and a ray 80 out passes. The far ray 80 out looks where a straight face through the hit and the
  side ray's meeting would be, so a long wall, fence or car flank met at a slant still reads wide (WallStop's stop), as
  in 2026-11-02a; only a thing that ends within 80 on that side reads narrow. The side rays also look at 1.5 wheel
  radii, so a rail over posts is a wall. The narrow and wide lines name the side ray's object and reference.
- **Sidestep**: a narrow thing on the path with no side key or mouse turn is stepped round toward its open side, up to
  `SidestepMost` (12) degrees at 40 a second till `SidestepShift` (60) across, then back onto a parallel line, from
  `SidestepFrom` (250) u/s; never for walls, cars or people, and a side key, the brake or the mouse lets it go. Before
  stepping to a side it checks the way across too: a ray out of the bike to that side (78), one along the step's own
  path to the new line, and one along the new line past the thing. A guard rail, fence, wall or parked car alongside
  takes that side (`sidestep: none for ...: the ray out 78 to its right met ...` or `... the ray from the capsule's
  right edge to its lane ... met ...`), and the other side is tried.
- **LaunchTau**: pulling away from rest the throttle starts at `LaunchFrom` (0.25) and closes on the top over 1.5 s, the
  cap allowing `LaunchLead` (0.45); a launch stuck against something drops back to `Lead`. A launch counts as stuck
  only under 20 u/s 0.6 s in (pinned on a kerb or a hillside); an ordinary pull-away is at 40-60 by then, so its
  `launch: from rest: ...` line is written. Re-accelerating at speed is as before.
- **UseBlockAbove, UseHold**: above 150 u/s the animation graph's `dyn_ActivationAllowMovement` (an item's use clip) is
  refused, so no item animation and no speed loss; a standing clip that still plays at 200 or more with forward held
  leaves the speed cap off for up to 2 s.
- **PoseViewSettle, UseRearm, UseBackTime**: the first third-person frames after first person stand, so the knees and
  hands aren't read for 0.1 s; a second use clip within 1 s of one's end is taken; a clip ends after 0.4 s of the hands
  back and the knees seated (test 49's stretched arm).
- **PoseOffRewrite**: `CMB_RiderPoseOff` is compared with the global itself, so a load or getting on in first person
  that zeroes it gets -1 written again (the build-49 check's finding 2).
- **SnapBest, SnapDrop**: a call with no spot with room asks about the most room's own navmesh point before the most
  room is taken (test 49's calls from the red truck), and a navmesh point's ground may be 250 under yours.
- **IdleDb, ShiftTime, ShiftDipTime, LaunchFlare**: the idle level with the cruise (-4.0 dB); each up-shift's gap 0.55 s
  with the dip 0.4 s; a launch press revs over itself by half, fading over `LaunchFlareTime`.
- **WaterSpeedFull, WaterCurve, WaterChurnDb, WaterRoadDb**: the water loop's level by (speed / 900) squared, so slow is
  quieter and full speed full; the churn 8 dB down and the wet road as built.
- **TipTime, FovTime, FovOffset**: how the MCM's first-person tip and field of view are eased in, and where the field of
  view is found (the game's own settings are never written). The tip comes once each time you go into first person
  from third person on the bike; coming back from aiming, a scope or VATS doesn't tip the view again. With
  `CMB_ViewFov` at your own FOV nothing is written or logged. If something else changes the FOV mid-ride, it is left
  alone the rest of the ride; if it puts ours back, yours comes back as you leave first person or get off (`camera:
  the world FOV back to N (...: ours again after something else had changed it)`).
- **Cull**: test 49 showed no measurable gain, so 0 by default (specks only); 1 is the 2026-11-02a build's.

The look's material changes have no key: the optional MO2 folder "2026-11-02a look (A-B)" in the 2026-11-06a package
gives 2026-11-02a's chrome, discs and rims back whole (tick it below the main mod, restart the game). The console's
`CMB_RiderUseOwn`, the MCM's seven new controls and the three re-pointed sound records are listed above and in
[TESTING.md](docs/TESTING.md).

### The 2026-11-02a build's keys (still there; off = 2026-11-01a)

| Key | Default | Off (2026-11-01a) |
|---|---|---|
| `[Tilt] UseLetGo` | 4.0 (seconds) | 0: the hands held on the grips through item uses (an ESP without `CMB_RiderItemUse` the same) |
| `[Tilt] UseHandOff`, `UseBlend`, `UseMax` | 30, 0.3, 8.0 | (parameters: a clips' hand this far from its grip is an item's use clip; the ease out and back in, seconds; the let-go's longest, seconds from the item) |
| `[Tilt] PoseFirstPerson` | 1 | 0: the knees measured in first person too (the script's footstep watch acts on first person's footsteps) |
| `[Ram] HitKeep` (changed) | 0.85 | 0.6 |
| `[Ram] HitHold` (changed) | 0.25 | 0.4 |
| `[Ram] HitChain` | 1.0 (seconds) | 0: each hit `HitKeep` of the speed then, the lower of two within the hold |
| `[Ram] PendingFoe` | 2 | 0: an enemy of a medium race (raiders, ghouls) not yet answered at the front wheel braked for (1: passed only if said yes to earlier in the ride) |
| `[Steer] WallStopNarrow` | 40 | 0: every wall WallStop's, however narrow |
| `[Steer] LowObstacleThrottle` | 0.85 | 0: `ObstacleThrottle`'s 0.55 |
| `[Steer] SlideRestore` | 0.5 (seconds) | 0: a slide's hold from the throttle the speed cap has left |
| `[Steer] FaceAlongKeep` | 1.0 (seconds) | 0: a face alongside only while the side rays confirm it |
| `[Sound] IdleDb` (changed) | -11 (-9 since 2026-11-06a) | -17.2 (`-10` louder, `-12` softer) |
| `[Fx] WaterGain` | 0 (dB) | (0 is the 2026-11-01a build's level; -6 halves the water) |
| `[View] Eye` | 1 | 0: the first-person bike at its own place (2026-11-01a: by full speed you sat over its rear wheel) |
| `[View] EyeAt`, `EyeSide`, `EyeSmooth`, `EyeSmoothZ`, `EyeMax` | 0,12,128 (0,1,128 since 2026-11-14a), 1, 0.05, 0.25, 150 (`EyeSide`, `EyeSmooth` and `EyeSmoothZ` unused with `EyeLock=1`) | (parameters: your eye's place on the bike, x right, y forward, z up; `EyeSide=0` follows fore-aft and height only) |
| `[View] StaleLines` | 3 | 0: every "third-person skeleton stopped / moves again" line logged |
| `[Diag] FpsLine` | 1 | 0: no "time: the last 10 s: N frames a second ..." line |

What they do:
- **UseLetGo**: after an item used while riding (the controller counts them in `CMB_RiderItemUse`), a clips' hand more
  than `UseHandOff` from its grip, or the knees off the seat, within 4 s is the item's use clip (an animation mod's,
  such as Immersive Animation Framework's): while it plays the hands and the upper body are the clips', the rider only
  tilting with the bike, eased out and back in; a prop in the hand goes with it. No use clip, nothing changes.
- **PoseFirstPerson**: in first person (the Pip-Boy too) the game's third-person skeleton stands, so the knees aren't
  measured there and `CMB_RiderPoseOff` reads -1 till third person; the script's footstep watch leaves first person's
  footsteps alone by it.
- **HitKeep, HitHold, HitChain**: at a knock-over the throttle is held to 85% of the speed for a quarter of a second,
  and hits a second apart or less share one dip, 85% of the speed before the pack's first hit.
- **PendingFoe**: an enemy of a medium race the bike reaches before the script has answered is driven through, not
  braked for, when the script said yes to it earlier in the ride (1) or, with 2, whenever you are in combat
  (`CMB_RamCombat`); braked for the moment the script says no. Never anyone the script said no to this ride
  (companions, essential characters, anyone not hostile); with 2, a companion's first ask in a fight may be passed
  until its no (about 0.1-0.2 s), never knocked over. Dogmeat is never asked.
- **WallStopNarrow**: a wall WallStop would cut for is tested for width by two rays 40 to either side of its path. One
  both pass (a mailbox, a lamp post, a sign, a post) gets FaceLook's own ease as it nears, never WallStop's cut; walls,
  cars, rails and barriers met square are cut as before. Ridden straight at, a post is eased but bumped, not stopped
  short of.
- **LowObstacleThrottle**: a kerb, log or rock lip lower than 1.5 wheel radii holds the throttle to 85% instead of 55%.
- **SlideRestore**: a slide's hold starts from what the throttle was when the speed cap began to bind, if that was within
  half a second, so a touch along a rail picks up again at once, not from a crawl.
- **FaceAlongKeep**: a face confirmed alongside (a rail, a car's flank) stays alongside for a second while it is the same
  object, still lies along the heading and is ahead, though the side rays lose it for a moment.
- **IdleDb**: the idle at -6.0 dB, 2.5 dB under the cruise; `-17.2` gives the 2026-11-01a build's quiet idle back.
- **WaterGain**: the water loop's level in dB on top of the effects volume.
- **Eye**: every frame the view bike is shown it is moved on its own axes so your eye sits at `EyeAt` on it (the seated
  rider's eye); `EyeMax` lets go while the camera is far from it (a menu's camera, the switch into first person).
- **StaleLines, FpsLine**: the log's rate limit for the skeleton's stop and start lines, and a frame-rate line every 10 s
  while riding, with `[Look] Cull`, first or third person and stopped or moving (the frame-rate A/B of TESTING.md).

The 2026-11-02a build's look changes had no key: its package's optional folder "2026-11-01a look (A-B)" is retired.

### The 2026-11-01a build's keys (still there; off = 2026-10-31a)

| Key | Default | Off (2026-10-31a) |
|---|---|---|
| `[Tilt] DecalsFollow` | 1 | 0: decals held like any skin |
| `[Tilt] ReuseByWalk` | 1 | 0: copies reused by their count |
| `[Tilt] PoolWait` | 1 | 0: a full pool leaves the rider level for the ride |
| `[Tilt] OrphanRestore` | 1 | 0: a skin left on an orphan copy is held from it as it is |
| `[Tilt] RepointEveryFrame` | 1 | 0: held skins checked at the 0.1 s sync only |
| `[Tilt] PoseCheck` | 1 | 0: `CMB_RiderPoseOff` never written, so the script never applies the pose again on it |
| `[Tilt] SeatKneeMin` | 52 | (a parameter: the higher knee under this over the ground point is off the seat; seated clips 60-68) |
| `[Diag] RepointLines` | 3 | 0: every re-point logged |
| `[Diag] RiderCopies` | 320 | (a test hook: the pool's size, 320 is 2026-10-31a's, at most 640) |
| `[Steer] WallStopClimb` | 1 | 0: while the climb's boost is on, the longer rays straight, to the raw need |
| `[Steer] FaceArc` | 90 (degrees) | 0: FaceLook's straight rays alone, WallStop for every wall |
| `[Steer] ClimbLegs` | 145 (degrees) | 0: a face round at its foot is a log without asking |
| `[Steer] BrakeKey` | -1 (the MCM's) | 0: no brake key, back (S) only |
| `[Steer] LandSoft` | 1 | 0: the game's hard landings as they come |
| `[Steer] LandSoftNames` | pool | (where the soft landings' names come from: `pool` or `game`) |
| `[Room] SnapSpot` | 1 | 0: the first spot with room taken as before |
| `[Sound] ShiftDraw` (changed) | 2300,3000 (3200,3700 since 2026-11-14a) | 2000,2900 |
| `[Sound] StopShift` | 1 | 0: a stop is a gear, then the clutch |
| `[Sound] HeardStop`, `HeardBrake`, `StopGap`, `StopHold`, `StopAfter` | 300, 600 (900, 1500 since 2026-11-17a), 0.4, 0.4, 0.3 | (parameters; inert with `StopShift=0`) |
| `[TailLight] Enabled` | 1 | 0: the light parked far below, lighting nothing |
| `[TailLight] Point`, `Back`, `Pitch`, `RunGain` | (the tail shell's centre), 8, 30, 1 | (parameters) |
| `[TailLight] BrakeGain` | 3 | 1: no brighter while braking |
| `[TailLight] BrakeBy` | colour | (`dimmer` is the fallback if braking doesn't brighten it) |
| `[TailLight] ColourOffset`, `DimmerOffset` | 0x12C, 0x144 | (the game's light layout) |
| `[View] Enabled` | 1 | 0: the first-person bike kept hidden |
| `[View] Lead`, `HandoverTime`, `Stale`, `Node`, `Trace` | 1, 1.0, 1, CMB_BikeView, 1 | (parameters; `Stale=0`: always the skeleton's word) |
| `[Look] Cull` | 1 (0 since 2026-11-06a) | 0: hidden parts shrunk to a speck only, the game's flags never touched |
| `[Fx] Land` | 1 | 0: no landing cue from the plugin (the script's one level, at `JumpDown` landings only; 2026-10-31a's silence is the MCM's "Landing sound" off) |
| `[Fx] LandFrom`, `LandFull`, `AirMin`, `AirHold` | 40, 400, 0.35, 0.3 | (parameters: the fall's speed at level 0 and 1, the seconds in the air for a flight, the hold after it) |
| `[Fx] Water` | 1 | 0: no water loop |
| `[Fx] WaterSource` | loaded | (`controller`: the water surface read from the character controller instead) |
| `[Fx] WaterFull`, `WaterSpeedFull`, `WaterStill`, `WaterPitch`, `WaterRise`, `WaterFall` | 40, 600 (900 since 2026-11-06a), 0.15, 0.85,1.0, 0.08, 0.4 | (parameters) |
| `[Fx] WaterSplash`, `WaterSplashTime`, `WaterSplashSpeed` | 6, 0.35, 300 | (`WaterSplash=0`: no entry splash) |

There are no `PoseOffGrip` or `PoseOffAfter` keys: the pose check measures the knees (`SeatKneeMin`), and the seconds
off the seat after which the script applies the pose again are the global `CMB_PoseOffAfter` (3). The 2026-11-01a
package's optional folders "2026-10-31a look (A-B)" and "game mirror cube (A-B)" are retired, and so is the 2026-11-02a
package's "2026-11-01a look (A-B)": the 2026-11-06a package carries only "2026-11-02a look (A-B)", and the 2026-11-07a
package none (that folder's meshes have one badge: with it ticked no choice shows on the parked bike, so untick it).

The keys turn up the first time you're outdoors with a Pip-Boy, so a new game's intro and Vault 111 are left alone.

## Repository layout

```
Data/                         mirrors the game's Data folder
  CommonwealthMotorbike.esp   the plugin (generated, ESL-flagged)
  Scripts/Source/User/        Papyrus sources; compiled .pex land in Data/Scripts
    CMB_ControllerScript      the brain: mount, dismount, speed, companions, parking
    CMB_BikeActivatorScript   parked bike menu; since 2026-11-22a it tells the controller each time the parked bike's
                              3D loads (`OnLoad`), for the look's runtime swap (OverlayRuntime); since 2026-11-23a it
                              also stands the leaning bike up in its own thread as you get on (`StandUp`, MountHide)
    CMB_KeysEffectScript      keys aid item
    CMB_SwimWatchEffectScript tells the controller when you start and stop swimming
    CMB_StaggerWatchEffectScript tells the controller when you're staggered while riding (a check of
                              "Steady in the saddle"; since 2026-11-01a)
    CMB_SideBagScript         capacity-limited side bag
    CMB_PlayerAliasScript     save/load hook
    CMB_MCMRelay              global functions MCM's keybinds and buttons call; each finds the controller and calls it
    CMB_HotkeyF4SE            optional F4SE hotkey; since 2026-11-10a it also uses a potion the plugin took from a
                              favourites hotkey at speed (`CMB_RiderQuickUse`), since 2026-11-14a also one whose clip
                              the plugin cut before the game used it (QuickCut)
    CMB_GearRestoreF4SE       optional (F4SE): puts slot-57 gear back on after a ride; since 2026-11-15b also reads a
                              gun's own keywords for the handgun test (`GunKeywords`), since 2026-11-21a the worn
                              weapon slot's item for the handgun note (`WornGun`)
    CMB_LookF4SE              optional (F4SE, since 2026-11-07a): the chosen look's material swap on the parked and
                              first-person bikes (and on the ridden one where the game refuses its mods); since
                              2026-11-08a also the colours (the free paint, body-colour rims, the plate's), since
                              2026-11-14a also into the chosen options' swaps before the ridden bike goes on, since
                              2026-11-15a skipped while the look is unchanged (MountQuick), and the parked bike's
                              swap never while the workbench menu is open (KitDefer); since 2026-11-16a also the
                              seat's colour and the right tank's follow by key (TankRightOf); since 2026-11-21a the
                              Wear, Front fender badge and Headlamp slots; since 2026-11-22a the Paint condition slot,
                              the parked bike's look only by loading its 3D again (ParkedSwapHold) and the composed
                              swap at runtime on the parked bike's fresh 3D (OverlayRuntime); since 2026-11-23a the
                              composed swap reused while it is the look as put on (OverlayQuick)
    CMB_RamScript             knocks enemies over (does anything only with F4SE and CMB_Slope.dll, whose rays see them)
  Meshes/CMB/                 the bike meshes and CMB_BikeParts.ini go here (built by tools/rider)
  Textures/CMB/Bike/          the bike's textures (built by tools/rider); the three palette textures earlier builds
                              put directly in Textures/CMB are no longer used and can be deleted
  Materials/CMB/Bike/         the bike's material files, one for the riding bike and one for the parked bike per
                              surface (built by tools/rider)
  Sound/FX/CMB/               engine sounds: here only the synthesised fallback four (the idle, cruise, start and stop
                              of the script's crossfade); the package's 13, built by tools/sound from demodave's
                              recording, replace them and add the nine loops the plugin drives, and since 2026-11-06a
                              the wet-road water loop `CMB_FxWaterRoadLP.wav` (made by tools/sound/make_water_loop.py),
                              since 2026-11-09a also its gentler twin `CMB_FxWaterRoadSoftLP.wav` (`--variant
                              gentle`; 3 dB louder since 2026-11-10a)
  MCM/Config/                 MCM menu and hotkey (written by the generator)
  F4SE/Plugins/CMB_Slope.dll  optional F4SE plugin: steeper slopes, farther camera, bike tilt, the bike's moving parts,
                              speedometer, lights and mirrors (tools/f4se-slope); its settings in CMB_Slope.ini
compile_scripts.bat           compiles the scripts with the Creation Kit's compiler
make_rider_pose.bat           builds CMB_RiderPose.esp + its AnimTextData from your load order
docs/                         install, assets, testing and design notes
tools/build.sh                regenerates the plugin and runs all offline checks
tools/esp-generator/          C# (Mutagen) plugin generator + plugin/script cross-check; look_options.json, the one
                              table of the customisation's slots, options, badges, paint rows and faction sets (since
                              2026-11-08a also the rim styles and finishes, the tyre bands, the hue palette, the
                              plates, their texts and colours; since 2026-11-16a the 3D emblems, the seat's palette
                              and the lists' display order; since 2026-11-21a the wear, the front fender's badge, the
                              headlamp's colours and their beams; since 2026-11-22a Paint condition, the Wear's part
                              shells, six more headlamp colours and the front fender badge retired), and look_ids.txt,
                              their records' committed IDs (since 2026-11-07a)
tools/syntax-check/           compile-checks the scripts on Linux without the CK
tools/rider/                  bike meshes (from the Sketchfab model or the vanilla bike), their textures and material
                              files (Blender), previews of the bike as the game shades it, riding clips (Python +
                              PyNifly), rider-pose plugin and AnimTextData (Python); since 2026-11-07a the badges'
                              atlas and materials (bike_art.py --badges, look_badges.py) and the paint palette
                              (look_paint.py); since 2026-11-08a the rims' and tyres' textures and the hue palette
                              (look_wheels.py), the plate's art (bike_art.py --plates, look_plates.py) and the new
                              shapes' own material files (look_shapes.py); since 2026-11-15b the bars' cables cut
                              into a shape that turns with them (bar_cables.py, `build_bike.sh`'s `cables` stage) and
                              the rider-pose report (`CMB_RiderPose_report.txt`); since 2026-11-16a the 3D helmet
                              badges added to the built nifs (look_emblems.py with emblem_pieces.py, `build_bike.sh`'s
                              `emblems` stage) and their textures and materials (emblem_art.py), and the seat's colour
                              (look_seat.py); since 2026-11-21a the wear shells and the front fender's badge patch
                              added to the built nifs (look_shells.py with shell_pieces.py, `build_bike.sh`'s `shells`
                              stage), the Wear slot's art and the muddy tyres (look_wear.py) and the headlamp's lens
                              colours (look_lamp.py); since 2026-11-22a the Paint condition shells, the Wear's shells on
                              the exhaust, the engine's covers and the fork's lowers, the wear shell over the badges
                              and every overlay shell blending (look_shells.py), the parked bike's side stand turned
                              down (look_stand.py, `build_bike.sh`'s `stand` stage), Paint condition's and the parts'
                              art (look_wear.py) and the Brotherhood helmet's gears and Nuka-Cola's script (bike_art.py);
                              since 2026-11-23a Rusty's lighter rust (look_wear.py --rust) and three gears either side
                              of the 3D Brotherhood helmet (bike_art.py --bos-ground)
tools/sound/                  engine sound: the loops built from the recording, the engine model, a ride renderer,
                              the old synthesiser (Python + numpy)
tools/package/                since 2026-11-14a: packages a build (its README.txt, Data/ and two zips) from a commit and
                              the previous package's assets, and verifies the zips (docs/BUILD_GUIDE.md, *For developers:
                              packaging a build*)
```

## Roadmap

1. **Done, in testing in game:** ride / park / call / side bag / companions / fuel, worn and parked bike meshes,
   seated riding animations with lean, MCM menu, engine sound and gear restore.
2. **In testing, the 2026-11-07a to 2026-11-23b builds:** customising at the bike (the badges, the paint, the mirrors at
   a field kit; then the rims, the tyres, a free paint colour and the licence plate), the 2026-11-09a build's fixes for
   tests 50 and 51 (the parked bike kept out of people, items at speed, Caution, the wheels, the bridge's posts, the
   truck, first person, the gears, the water, the field kit, getting on), the 2026-11-10a build's for test 52 (getting
   on quicker, items by hotkey at speed, the field kit with Global Stash, Free colour's first ride, Caution 50's
   sidestep, the parked bike's guard, first person's diagnostic, the engine in the Pip-Boy, 3rd gear, the front wheel's
   shadow, the gentle water louder), the 2026-11-14a build's for test 53 (number keys at speed, Free colour in third
   person, first person steady with the eye over the seat, the FOV dropped, the field kit's names, preview and
   settlements, the engine quiet in menus, five gears), and the 2026-11-15a build's for test 54 (no crash at the field
   kit's plate colours, its preview 400 ahead, first person steady with the camera's place read right and no red flash,
   the eye where test 54 put it, getting on quick again, the speed climbing with the gears, three earlier logs kept),
   and the 2026-11-15b build's for test 53's and 54's wishes (A and D turning the bike in first person, the view leaning
   in turns, looking back when reversing and a look key, a handgun from the saddle with the left hand on the bar, your
   own body in first person, sidesteps round cars and other wide things, the right-hand cables turning with the bars),
   and the 2026-11-16a build, the third customisation build (art build A: the Enclave and Brotherhood helmets in 3D on
   an enamel plate, the Gunners skull, every plate's emblem redrawn with a die-pressed plate font, the seat's colour,
   the lists in alphabetical order), and the 2026-11-16b build's for test 55 (the first-person shake, the bike while
   zooming in, the cell moves, the view's lean by the turning rate and the look back's pitch, A and D at 0.45; with your
   body in first person no second bike, gun or outfit piece in view and no arms looking back, the body sitting where the
   game's eye is; the put-away called on the player and saves not counted, a handgun seated with both hands on the bars
   and the gun in hand, also right after getting on; the field kit's preview placed by the plugin; a short 1st, an even
   climb and the gears' sound at the matching speeds), and the 2026-11-17a build's for test 56 (the first-person
   camera found as the game eases it and the bike kept near the camera at a handover; the bike drawn again in third
   person after your body, the eye in front of the neck, the arms hidden with the look key; the weapon rules kept
   across a menu, rifles never drawn while riding, a quick swap judged again, the spikes from the hands; the field
   kit's bike held, zoomed and turned to each slot, the kit set out where you stand; the take-off a tad quicker and a
   stop's down-shifts one gear at a time) and its art corrections (the Brotherhood of Steel, Minutemen, Nuka-Cola and
   Red Rocket plates, the Gunners skull on a green flag patch, the Brotherhood of Steel badge in colour, the Enclave
   helmet's chrome ground, Saddle tan), and the 2026-11-21a build's for test 57 and its wishes (the bike drawn again in
   third person after your body; the free look on the right mouse button and in third person, the game's aim blocked
   while riding; the field kit's bike held on every model the menu has, turned only to a slot the highlight rests on,
   the wheel zooming anywhere and a drag off the lists turning it; no holstered weapon in the hand, the seat pose kept
   through a put-away and a first-person draw, the handgun note; the coast twice as long and gradual, the gears in even
   steps) with **build B**, the second art build (the Wear slot's seven looks, three muddy tyres, the front fender's
   badge, the headlamp's colour, the lens and the beam, the Nuka-Cola and Red Rocket badges, the 3D Enclave helmet on
   the Enclave's flag and the 3D Brotherhood helmet between two cogs, four plates' top lines centred), and the
   2026-11-22a build's for test 58 and every wish it brought (no crash getting on after a change at the kit; the Wear on
   the parked and riding bikes; the game's aim blocked for real and the third-person look as the plugin's own orbit;
   the field kit's views on the bike it draws, the wheel both ways and scrolling the lists over the list panel; other
   mods' attachments, a holstered pistol on the thigh, following the body; the up-shifts at their bands in every pull,
   the speed kept through a menu; the parked bike on the ground under both tyres, leaning on its own side stand) with
   **build C**, the third art build (Paint condition under the Wear, the Wear on the exhaust, the engine's covers and the
   fork's lowers and over the badges, the muddy tread clean where it meets the road, three gears on metallic blue
   behind the 3D Brotherhood helmet, Nuka-Cola's script, eleven headlamp colours, the front fender badge out), and the
   2026-11-23a build's for test 59 and its wishes (getting off parks the bike beside you, its lean on the stand held
   between 5 and 20 degrees and its tyres on the ground beside a car or a curb, getting on with the parked bike hidden
   under the fade; the Wear and Paint condition on every bike at once; no flash at the kit's options; the third-person
   look with a weapon drawn; a pistol held one-handed with the left hand on the bar, in third and first person; the
   holster on the thigh; no item clip in third person; a quicker take-off; Rusty lighter, three gears either side of the
   3D Brotherhood helmet), and the 2026-11-23b build, 2026-11-23a with its second review's four fixes.
   **Next:** test 60 on the 2026-11-23b build and its fixes; from 2026-11-15b's to 2026-11-23b's open ends, seated clips
   for a drawn pistol (from the rider-pose report), the right forearm aimed along the camera with a handgun out, the
   left hand to the pistol while reloading, first person's own pistol, an MCM switch for the body in first person and
   for the look button and the aim's block, the riding bike kept through a rifle's put-away and through a handgun drawn
   in first person, your body shown while backing over the shoulder; the next rounds of in-game testing; the remaining
   vanilla-timed stop and idle clips. Wheel spin and the bars' turn come with the Sketchfab build and F4SE (see
   DESIGN.md); later, if wanted, another seat shape and loose rim parts (after the mirrors' double return is fixed);
   luggage and the mod's own toolbox and parts box.
3. **Later:** a visible pillion passenger, mount/dismount animations. Possibly a v2 built on the engine's mount
   system instead ([DESIGN.md](docs/DESIGN.md)).

## Credits

- Bike model: ["Harley Davidson Iron 883 2015"](https://sketchfab.com/3d-models/harley-davidson-iron-883-2015-612071b783f14a7288df2d361be9a244)
  by [Nieve5677](https://sketchfab.com/niev), licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
  Converted for the game by the mesh tools in `tools/rider` (`build_bike.sh`): cut down from 1.3 million triangles to
  about 230,000 (230,815 with the mod's own parts), given UV maps and procedural textures baked from the full model by
  `tools/rider/bike_textures.py` (the download has no textures), scaled to the vanilla bike's length and put on the
  vanilla motorcycle's collision; the speedometer's dial and needle, the lights' shells, the under-bar mirrors and the
  badges are the mod's own. The converted meshes and their textures aren't in this repository; anyone sharing them
  keeps this credit.
- Engine sound: ["Harley Davidson Sportster - Idling with Engine Revs"](https://freesound.org/s/502690/) by demodave
  (Freesound), released under [Creative Commons 0](https://creativecommons.org/publicdomain/zero/1.0/); CC0 asks for
  no credit, so this one is a courtesy. `tools/sound` makes every file of the engine sound from its right channel: the
  start, the stop and the idle cut from it, the ten riding loops made from its own firing pulses and falls. Neither
  the recording nor the files are in this repository (`tools/sound/README.md`). Their tone was matched to three
  on-board videos of the same model of bike, someone else's, which were only measured: nothing of their audio is in
  the mod. The under-bar mirrors' shapes were measured off frames of them the same way.
- Water sound: made from "Cars driving on a wet road 3" by freesound_community (Pixabay, 101246), under the Pixabay
  Content License. `tools/sound/make_water_loop.py` cuts three stretches of it into the mod's own wet-road loops
  (since 2026-11-09a also a gentler one); the recording isn't in this repository.
