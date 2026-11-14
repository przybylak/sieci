# Commonwealth Motorbike (Fallout 4 mod, work in progress)

A rideable motorbike for Fallout 4:

- **faster than on foot**: 250% of your speed by default, adjustable from the console
- **companions come along**: they run alongside at the same speed (or, opt-in, ride along hidden)
- **runs on Flamer Fuel**: one unit per 300 m ridden, taken from the side bag first, so it isn't a free speed boost in Survival
- **side bag**: small storage, size adjustable from the console
- **park it, call it, ride it**: activate the bike or use its keys (favorite them to a hotkey); optional F4SE hotkey; since the 2026-11-09a build getting on takes about 1.5 s with the look unchanged (test 51: 5-6 s), and a second press while the bike's menu is coming is ignored (test 51's black screen after Ride); since the 2026-11-10a build (test 52: 3-5 s, the screen black for 3.0-3.6 s of it) the worn bike goes on right after the screen fades and the screen comes back as soon as the bike is held and coloured and you are seated, the rest of getting on after it: about 1.1-1.3 s of black with the stock look and 1.6-2.1 s with a full look, by the estimate (the log's stage-times line shows the real split)
- **seated riding animations** with lean in turns and ridden U-turns; the bike turns with you on the spot and in conversations; since the 2026-11-01a build hits don't stagger you while riding (MCM "Steady in the saddle", so the bike no longer hangs round your hips through a stagger), and with F4SE the plugin checks that the seated clips are playing and the script puts them back if they aren't (test 47's rider "floating" after a fight was the plugin running out of copies of her bone data, held by the blood decals: fixed); since the 2026-11-02a build "Steady in the saddle" is a perk of its own with the two condition tabs the game's own stagger lining has (test 48: eight staggers got through the first one; the console's `CMB_RiderSteadyWay` tries the game's own perk too), the pose is left alone for 6 s after an item's use so an animation mod's use clip plays whole, the camera's with it (test 48's camera stuck after a stimpak), and with F4SE the hands let go of the grips while that clip plays (test 48's arm stretched while eating) and the pose isn't measured in first person, where the game's third-person skeleton stands; since the 2026-11-06a build using an item while riding fast (a stimpak by its hotkey, food from the Pip-Boy) no longer slows the bike: above 150 units a second the item animation mod's clip isn't played (the item is used as always), stopped or slow it plays, and the arm no longer stretches when eating right after the Pip-Boy (test 49); items another mod equips on you (a reload fixer's dummy potion) no longer start the item watch; since the 2026-11-09a build an item's use clip that still starts at speed (test 50: the item animation mod's own idle never passes that refusal) is stopped as it starts, the plugin telling the animation graph `IdleStop`, then `IdleForceDefaultState` (`[Steer] UseStop`), so the bike should keep its speed; since the 2026-11-10a build (test 52: by the hotkey the clip was cut before the item was used) a potion on a favourites hotkey used at 150 units a second or faster is used at once, without the game's use animation, the way the Pip-Boy uses it (`[Steer] QuickUse`), and the use-clip stop acts only on an item's props, never on a drawn weapon; since the 2026-11-14a build (test 53: by its number key the plugin never saw the key, the game giving its own key codes) a number key is found by the game's own name and code, and when the plugin can't take one the item's clip is cut and the script uses the item, or the clip plays until the item is used, so a stimpak by its number key always heals at speed (`[Steer] QuickKeyCodes`, `QuickCut`, `UseStopUnapplied`)
- **an engine sound from a real V-twin** (demodave's recording, CC0): with F4SE (since test 44's build) the plugin runs a model of a four-speed gearbox and pitches and fades eleven loops every frame with your speed and throttle, shifting up as you pull away and falling off as you let go; since test 45's build the engine keeps a real ride's pace rather than the game's quick bike, so a pull-away climbs from the moment you press forward, each one shifting a little differently, the cruise holds steady and a roll-off falls slowly in gear; since test 46's build each loop's level is set at once rather than faded, so a gear change no longer cuts out, and the engine is louder and punchier, with hotter recordings, more between the cruise and a full-throttle pull and its full volume out past the riding camera (test 45's build needed the MCM's engine volume at 100); since test 47's a steady cruise wanders in pitch and level like a hand on a real throttle (since the 2026-10-31a build more, in slow swings of a second or two that peak 3 to 5% off the cruise's rpm, never past about 6%, and about 1 to 1.5 dB in level), each up-shift dips briefly as the throttle closes, the engine reverberates as the game's other sounds do, and the MCM's engine volume starts at 90 in a new save; since the 2026-11-01a build 1st and 2nd change up later, at about 2,600 rpm, and a stop changes down so you hear it (three blipped down-shifts rolling to a stop, two braking, then the clutch); since the 2026-11-02a build the idle is louder, 2.5 dB under the cruise where it was 8.7 under (test 48: "it feels like there is no sound"), so a stop no longer goes quiet and the start and stop sounds run into and out of it without a step; since the 2026-11-06a build the idle is a little louder (level with the cruise), each take-off starts with a short rev, and each gear change is longer (about half a second of the darker sound and the dip; `IdleDb`, `LaunchFlare`, `ShiftTime` and `ShiftDipTime` in `CMB_Slope.ini`); since the 2026-11-09a build each gear lasts longer than the last at full throttle from a stop, 1st about 1.6 s, 2nd 2.0 and 3rd 2.5 (test 50: 3rd was pinned at 1.25 s, shorter than 2nd; test 51: 1st lasted about 3.5 s: `[Sound] HeardRiseGears`, `ShiftGapGears`); since the 2026-11-10a build 3rd lasts about 3 s (test 52's wish) and the Pip-Boy (or any menu that pauses the game) at speed holds the engine's note instead of dropping it to 1st and climbing back after the close (`[Sound] MenuHold`); since the 2026-11-14a build (test 53: "a bit flat") five gears shift higher, at about 3200-3400 rpm at full throttle, the cruise as before, the note never falls while the bike gains nor drops to 1st on a throttle lift (`HeardKeep`, `LiftDown`), and the engine and the water go quiet while a menu pauses the game (`MenuQuiet`); without F4SE, an idle and a cruise loop crossfaded by speed
- **a V-twin cruiser** as the bike (Nieve5677's Sketchfab model, CC-BY: see the credits), on the vanilla motorcycle's collision; with F4SE its wheels spin with the distance ridden (since the 2026-11-09a build by each frame's own movement, so they stop with the bike, and they hold still while you brake: test 50's wish) and the bars turn with you (the hands go with them, and since the 2026-10-31a build the lower triple clamp too); the vanilla bike can be built instead
- **its look** (since the 2026-10-31a build): textured all over, with procedural textures baked from the 1.3-million-triangle model onto the game's mesh (the download has no textures): an oxblood tank and fenders with a clear coat and a cream double coachline, our own winged-wheel badge, dark mirror-like chrome, a black wrinkle-finish engine with bright fin edges, a leather-grained seat, tyres with their tread; a material file for every surface (the hook for paint and parts at a workbench later); with F4SE **a working speedometer** (its needle follows your speed, about 50 on the dial at full speed by default, and its numerals light up with the headlamp), **a tail light** lit while you ride that brightens with both rear signals when you brake, and **mirrors** that show a sky (Fallout 4 can't show real reflections), in the stock style or either of two styles hung under the bar ends (`[Look] Mirrors` in `CMB_Slope.ini`; since the 2026-11-07a build the ones you fit at the bike, which the parked bike shows too). Every new behaviour of the plugin has a key in `CMB_Slope.ini` whose off value gives the previous build's back; the textures and the lower triple clamp turning with the bars come with the meshes (the previous build's meshes copied back give its look). Since the 2026-11-01a build the tank's cream line is one smooth curve with round corners, the seat's piping is re-cut, the brake discs are our own drilled ones and the mirror glass is brighter; with F4SE the tail lamp lights the road behind a soft red, three times brighter while you brake (MCM "Tail lamp lights the road"), and **the bike is under you in first person** (MCM "Bike in first person"; no hands on the grips: the game shows no arms with the weapon away). Since the 2026-11-02a build the chrome is polished (its material files reflect six times as much, with sharper glints and screen-space reflections: test 48's "too dull"), the mirrors show the game's own mirror cube (test 48's pick of the two), the front brake disc has no light ring round its bore, and with F4SE the bike in first person stays under your eye at every speed (test 48: it slid back by 58 ms of the speed, so at full speed you sat over its rear wheel; `[View] Eye`). Since the 2026-11-06a build the chrome is toned down, still bright but not pearly or smeared (its material files reflect 2.5 times the cube where the 2026-11-02a build's did 6, with less specular and no screen-space reflections: test 49), the rims and discs are a little greyer, and with F4SE going into first person eases the view about 20 degrees down so the dial and the bars are in sight (MCM "Look down on getting into first person (deg)"; test 49's bike out of view looking level), with a riding field of view (off by default) and your eye's place on the bike in the MCM too; the optional MO2 folder "2026-11-02a look (A-B)" gives the 2026-11-02a build's look back. Since the 2026-11-09a build (test 50) opening the Pip-Boy from third person no longer tips the view, a little look of your own while the view eases down adds to it (past 5 degrees you take over), the ease starts a quarter of a second into first person, the view bike's place in the game's scene is made to hold it (test 50 never saw it; the plugin now logs how it is drawn) and the riding field of view looks for the game's own field more widely, from half a second into first person; and (test 51) a tip its own check turns off within 2 s of a load or of getting on is off for that entry only, not for the session; since the 2026-11-10a build the front wheel, the fork and the bars cast their shadow in the sun while you ride, as the parked bike's always did (test 52's wish), and in first person (test 52: the bike still never seen) the plugin moves the first-person bike under your own cell's node while it shows and runs the game's own update on it (`[View] Parent`, `Update`), logs four more `view: drawn?` lines to settle why it isn't seen, tries the camera's own two fields for the riding field of view (`FovSearch=2`), and lets a mouse move of up to 15 degrees add to the tip (`TipYield=15`); since the 2026-11-14a build (test 53: the bike seen at last, but shaking, and you sat over the tank) the first-person bike is held so your eye stays put on it as it tilts, following the game's own camera each frame (`[View] EyeLock`, `Camera`), your eye 11 units further back, over the seat, and the riding field of view is gone (the game wrote its own back)
- **customising at the bike** (since the 2026-11-07a build): the parked bike's menu has a Customise button; a field kit comes out of the side bag beside the bike and you change the badges on both sides of the tank and on the rear fender (13 emblems of our own, from the Brotherhood of Steel to a pre-war army star, and four of the game's own by path), the paint (13 faction schemes, 24 colours, 6 neutrals, each with its coachline) and the mirrors (stock, under the bars egg or D, none) at the armour menu, paying in components; since the 2026-11-08a build also the rims (seven styles of our own, from laced spokes to a scrap plate, in chrome, satin black, gloss black, bronze, gunmetal or the body colour, and the cast rim in five finishes: 48 choices), the tyres (black, whitewall, red line), any paint colour from the MCM (a hue slider and four shades) and the licence plate (12 designs of our own, from the Commonwealth standard to Vault-Tec's and the factions', 60 stamped preset texts, crude ones among them behind a switch, and 16 colours for its letters and its background); the bike shows the new look parked, ridden and in first person. **Nothing changes until you choose**: every slot starts on the bike as it came. The MCM's Look section turns it off, picks the kit, and has a free mode with a choice per slot and faction sets (see *Customising the bike* below); since the 2026-11-09a build (test 51) the field kit's automatic mode puts an armour bench out first and then the game's own armour bench (the toolbox, which the game can't seat you at, only as a test), the parked bike shows a new paint or rim finish at once after an MCM apply, moving the MCM's paint hue or shade chooses Free colour, and the Vault-Tec plate's cog is redrawn at the plate's own size; since the 2026-11-10a build (test 52) the field kit's menu no longer shuts at once with Global Stash by SKK installed (the kit is linked to SKK's stash before it opens), a kit menu that closes within half a second with nothing changed never counts as working (the same kit once more, then the next kind), and a Free colour applied in the MCM shows from the first ride; since the 2026-11-14a build (test 53) Free colour shows in third person on every ride (the colours go into the chosen options' own swaps before the bike goes on: `[Look] WornIndex`), the armour menu names the item "Motorbike" and each slot's choice with its slot ("Paint: Factory"), its preview shows the whole bike, and the field kit comes out only in your own settlements (MCM "Field kit only in your settlements")
- **a headlamp** (the Sketchfab build, F4SE): a round LED lamp on the fork bracket with its running light lit, and a real spot beam (like the power armor's, a light the mod places at the lamp) that turns with the bars and tilts with the bike; MCM: off, on, or on at night, and a hotkey
- **rides like a vehicle, not a person**: 75% less fall damage while riding (adjustable), deep water ends the ride and leaves the bike on the bank, and an enemy's hit knocks you off (optional; since the 2026-11-06a build a power attack only when it takes the "Big hit" share of your health, as any other hit, explosions always: MCM "Power attacks throw you off", off by default; since the 2026-11-09a build the bike parked after a knock-off never appears inside someone: a spot with an actor in it has no room, the bike is put back where it stood only if that place is still free, and while anyone else stands where it would appear it stays hidden and shows once the place is clear (you count only in the bike's very place, and not where the mod has just put it clear of you: getting off, calling it, bringing it; since the 2026-11-10a build someone knocked down there counts too, as does a dog or a crouching NPC right beside the settled bike, and you only within 150 units of its ground): test 50's crash came half a second after a knock-off with raiders round the bike); with F4SE, hostile people, creatures and smaller robots (since test 43 by a list of their own, `CMB_RamRobots`) the bike hits at speed are knocked over and take a little damage, the bike losing some speed at each (since test 45's build a dog the mod's script hasn't answered for by the time you reach it is ridden through rather than braked for, and knocked over when the answer comes, and a robot ridden at again after a hit is knocked over again; since test 46's an old save's knock-overs no longer make it brake for those same animals; MCM "Knock enemies over"; never companions, essential characters, anyone in power armor or the big ones: super mutants, behemoths, deathclaws, sentry bots and the like; since the 2026-11-01a build the knock-over that takes an enemy's last health kills it, and the kill is yours, experience and quests as for a shot: MCM "Knock-overs can kill"; since the 2026-11-02a build a knock-over holds the throttle to 85% of the speed for a quarter of a second, not 60% for 0.4 s, and a pack's hits share one dip, so the bike no longer nearly stops at a pack; an enemy of a medium race the script hasn't answered for by the time you reach it is ridden through, not braked for, when it was said yes to earlier in the ride or you are in a fight; and a kill by the bike gives the game's own experience, the killing hit being your own damage: MCM "Kill experience")
- **follows the ground**: the parked bike stands on the ground, tilted to match the slope (with F4SE, on the ground you just rode over, and since test 46's build a called bike on the ground under its wheels, leaning up to 20° across a slope; since test 47's getting off where you got on puts the bike back where it stood, the parked spot is checked for room as a call's is, and a bike called while you stand on a car comes to the ground beside it); with F4SE, the bike also pitches with the ground while you ride, leans into turns at speed (the rider with it, head level), stops short of boulder faces but slides along a railing beside it, climbs over low fallen trunks and stumps and up a step, but since test 45's build not onto a rail, a barrier or a log with a drop behind it (since test 46's not onto a rail lying on the ground or met at an angle nor along a fence either, and at full speed it stops short of a rail rather than with its front wheel in it; since test 47's it eases off only for what stays in its way, not for things you steer past, looks along its turn, stops about a wheel's radius short of a rail, isn't climbed onto a rail met at a shallow angle and doesn't ride on along one its front wheel is in), keeps its tyres on top of small bumps, takes a landing on its suspension and keeps going, backs up to a rail or a ledge's lip with its rear tyre just short of it and down off something it hangs on, turns in a circle rather than on the spot, climbs slopes too steep to walk up, and the camera sits farther back (since the 2026-11-01a build it also looks along the arc of the turn you're in, so a thing beside the curve eases the throttle by its distance instead of stopping the bike, a barrier on legs isn't climbed, a call from on top of a car or a truck puts the bike on the ground beside it rather than on its edge, and a high drop no longer halves the speed for most of a second; since the 2026-11-02a build a narrow thing ahead, a mailbox, a lamp post or a sign, is eased past by its distance and never stops the bike, while walls, cars and rails met square still do, a kerb or a log at speed holds the throttle to 85% rather than 55%, and a touch along a rail or a car's flank picks up again at once rather than from a crawl; since the 2026-11-06a build it steps round a post or a mailbox on its path to the open side (`Sidestep`) when you ride straight at it, a rail over posts is a wall, a pull-away from rest is punchier in its first second, and a call from on top of a truck tries the most room's own navmesh point first, so the bike comes down to the street; since the 2026-11-09a build how early it eases off for a wall or a car ahead is the MCM's "Caution", closer by default (60%: the throttle eases from about 8 m at full speed, where it was 11 m; 100% is the 2026-11-08a build), a bridge's end post with a drop behind it is no longer climbed as a step, and a call from a truck's bed tries the navmesh beside the truck first; since the 2026-11-10a build a new save starts at Caution 50, the sidestep still finding a post at Caution 60's reach, and a mouse move under 5 degrees no longer cancels a sidestep)
- **its own sounds** (since the 2026-11-01a build; the game's own sound files, since the 2026-11-02a build under sound records of the mod's own, heard at the riding camera's distance: test 48 heard none of them): your character's own jump and landing sounds are muted while you ride; a tyre thump on every landing with a real fall, louder the higher the drop, a metal clunk on big ones and a splash into water; with F4SE a spray riding through shallow water, by speed and depth (the MCM's Sound section: "Bike sounds through the mod's own records", "Landing loudness range (dB)"); since the 2026-11-06a build landings sound like tyres and a dull thud, no metal, riding into water splashes, and riding through water is the mod's own wet-road swish, quieter when slow, louder at speed (MCM "Landing sounds without metal", "Water sound loop"); since the 2026-11-09a build a second, gentler wet-road loop from the same recording, with less hiss and more body, is the default ("Wet road, gentle"; "Wet road (the mod's own)" is the earlier one), since the 2026-11-10a build 3 dB louder (test 52's wish; `[Fx] WaterGentleDb=-3` is 2026-11-09a's level)
- **MCM menu** for every setting (with MCM installed); with F4SE, gear in the bike's slot goes back on after a ride

> **Status: in testing.** It has been tested in game round by round since the first build (test 53 the
> latest), each round answered from the logs and videos sent back. Every round's changes are checked offline
> before they ship: the plugin's structure, every script property and the vanilla form IDs, the scripts compiled
> against stand-in versions of the Fallout 4 scripting API, and `CMB_Slope.dll` run against a fake game
> (`tools/f4se-slope/test`). What changed since the last round hasn't run in the game until the next, so expect
> fixes after each.
> [TESTING.md](docs/TESTING.md) says what to send back.
>
> **Test 50's crash** (there since 2026-11-06a): the game crashed once, a Havok stack overflow about half a
> second after the third knock-off in 21 s, in a fight with several raiders (the plugin wasn't in the crash stack;
> suspected, about half sure: after a knock-off the bike was parked on a spot an actor stood in). Since the
> 2026-11-09a build the parked bike is kept out of anyone's place (`[Room] ActorRoom`, `ParkBack` and `ParkGuard`
> below); test 52 tried it with "Power attacks throw you off" on, four knock-offs with quick get-ons: no crash. If
> the game ever crashes again, send the crash log with both logs: its actor can be matched with the plugin's `room:` lines.

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
4. jumping, sprinting and (by default) combat are blocked.

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
| Testing in game + Papyrus log | I can't run the game; the logs and screenshots are how fixes happen (with F4SE the plugin's `CMB_Slope.log` too; since test 41 the session before's is kept beside it as `CMB_Slope_prev.log`, so a crash and a restart don't lose it) |

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
| Get off | use the keys again (favorite them for a hotkey) |
| Side bag | activate the parked bike → "Open side bag", or keys → "Open side bag" when the bike isn't nearby |
| Customise (since 2026-11-07a) | activate the parked bike → "Customise": the field kit and the armour menu (*Customising the bike* below); not while riding, in a fight or swimming |
| F4SE hotkey | **B** by default: off / on / call |
| Brake (F4SE plugin, since 2026-11-01a) | **Space** while riding (MCM Hotkeys "Brake key (scan code)", a DirectInput scan code: 57 Space, 42 Left Shift, 29 Left Ctrl, 56 Left Alt, 45 X, 46 C, 0 none; the log names the key it read): brakes with forward held and holds the bike still once stopped; back (S) still brakes and backs up; off the bike Space jumps as always |

Don't favorite the keys to the F4SE hotkey's own key: one press then fires both, and the second is turned away as busy (harmless, but the log shows it twice).

## Customising the bike

Since the 2026-11-07a build (the first customisation build; the second, 2026-11-08a, adds the rims, the tyres, a free
paint colour and the licence plate). Activate the parked bike and choose **Customise**: a field kit (a toolbox) comes
out of the side bag beside the bike, on your side, you stand at it and the armour menu opens with the bike listed as
"Motorbike" (up to 2026-11-10a the menu called it "Default", its object template's name: test 53). Since the 2026-11-14a
build the kit comes out only in a settlement of yours (below). Its eleven slots:

| Slot | Choices (the first is the bike as it came) | Cost |
|---|---|---|
| Tank badge, left | Stock (winged wheel), None, Brotherhood of Steel, Brotherhood helmet, Enclave, Enclave helmet, Gunners, Minutemen, Railroad, Institute, Vault-Tec, Atom Cats, Raiders, Children of Atom, Pre-war army star (all 13 drawn for the mod), Gunners (game art), Pre-war army star (game art) | a badge Adhesive 1, Cloth 1; Stock and None free |
| Tank badge, right | the same, and "Same as the left" (the default: it follows the left; any other choice ends that, "Same as the left" brings it back) | the same; "Same as the left" free |
| Rear fender badge | None (as it came), the 13 of ours, the two chest decals and, on the fender only, the Minutemen flag and the Brotherhood flag (game art) | Adhesive 1, Cloth 1 |
| Paint | Factory (oxblood); 13 schemes, two-tone with their coachline (the eleven factions', Nuka-Cola, Red Rocket); 24 colours (Fire red to Raspberry); 6 neutrals (Gloss black, Pearl white, Silver, Gunmetal, Pre-war cream, Primer grey); "Palette test: colour index" (cobalt blue if the colour lookup works, primer grey if not); since 2026-11-08a "Free colour (hue in the MCM)": the MCM's "Paint hue" in one of four shades, with a cream coachline | Factory Oil 1; a colour (and Free colour) Adhesive 2, Oil 2 and the Armorer perk |
| Mirrors | Stock, Under the bars (egg), Under the bars (D), None | stock Steel 1, Glass 1; egg or D Steel 2, Glass 2, Screws 1; none Screws 1; a mirror taken off comes back as a loose mod |
| Rims (since 2026-11-08a) | Stock (cast); the cast rim in satin black, gloss black, bronze, gunmetal or body colour; seven styles of our own (Laced, Solid disc, Star five, Turbine, Pre-war steel, Atomic, Scrap plate), each in chrome, satin black, gloss black, bronze, gunmetal or body colour: 48 in all, on both wheels | a cast finish Adhesive 1, Oil 1; a style Steel 3, Screws 2, Oil 1 and the Armorer perk; Stock free |
| Tyres (since 2026-11-08a) | Black (as it came), Whitewall, Red line (on both sidewalls of both tyres) | Adhesive 1, Oil 1; Black free |
| Plate (since 2026-11-08a) | Stock (plain); 12 designs of our own: Commonwealth standard, Commonwealth vintage, Blank, Vault-Tec, RobCo, Nuka-Cola, Red Rocket, Brotherhood of Steel, Minutemen, Institute, Raider scrap, Army motor pool | Steel 1, Oil 1; Stock free |
| Plate text (since 2026-11-08a) | The plate's own (the design's text), None, and 60 stamped presets of 5 to 7 characters: 32 themed (AB 1234, VLT 111, PIP-BOY, PALADIN, GEN-3, ...), 14 funny (DOGMEAT, I♥RADS, NO CAPS, ...), 14 crude (BITE ME, ...: MCM "Crude plate texts" off hides them) | Steel 1; the plate's own and None free |
| Plate letters, Plate background (since 2026-11-08a) | The plate's own (the design's colour), and 16 colours: Plate white, Cream, Black, Plate red, Maroon, Commonwealth blue, Vault blue, Vault yellow, Orange, Forest green, Olive drab, Gunmetal, Teal, Phosphor green, Silver, Rust | Oil 1; the plate's own free |

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
armour menu's preview (its bike keeps the design's colours): the parked bike beside the kit changes as soon as you take
one. A faction set with a plate (Brotherhood of Steel, Minutemen, Institute, Vault-Tec, Raiders, Pre-war army) also fits
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

**MCM, Look** (before Hotkeys; 20 controls since 2026-11-08a, 21 since 2026-11-14a): "Customise at the bike" (on: the
Customise button; off: no button and the bike as it came), "Field kit" (Automatic, two toolbox tests, Armour bench and,
since 2026-11-09a, "The game's armour bench"), since 2026-11-14a "Field kit only in your settlements" (on; and the
section "Field kit preview" after Look), "Parts from the side bag", "Crude plate texts" (since 2026-11-08a, on by
default; off: the 14 crude plate texts aren't offered at the kit, and a plate wearing one shows its design's own text at
the next getting on, activation or Apply), and "Free customising (no field kit, no cost)", which shows a choice per slot
(the eleven above, with "Paint hue" and "Paint shade" under the paint), "Faction set" (the paint and all three badges of
one of eleven sets, and for six of them the plate) and "Apply the look": it puts the choices on the parked and
first-person bikes at once and on the ridden bike at the next getting on, except a new rim style: then the ridden bike
is put on again within about a second (you stay seated; the bike is gone for a moment). Turning "Customise at the bike"
off (or changing a choice without "Apply the look") takes effect at the next getting on or activation of the parked bike
(or Apply, or a load), and on the ridden bike also when it swaps mid-ride (a weapon drawn or put away, a hit); a load
mid-ride with "Customise at the bike" off puts the ridden bike on again too if its rims weren't the cast ones.

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
it: ParkedReload). Since 2026-11-14a: the preview's values are a first guess (the bike may be small: zoom in, or Tune),
and an option you didn't choose keeps the last colour written into it until you choose it again (only the preview
shows that). Weathered paint, more badges, the front fender, the headlamp's colour and the seat come later.

## Console settings

| Command | Default |
|---|---|
| `set CMB_SpeedPercent to <100–500>` | 250 |
| `set CMB_BagCapacity to <n>` (lbs with F4SE, items without; 0 = unlimited) | 60 |
| `set CMB_CompanionMode to <0 run alongside / 1 ride along>` | 0 |
| `set CMB_UseFuel to <0/1>` | 1 |
| `set CMB_FuelDistance to <units per fuel>` (about 70 units = 1 m; lower = thirstier) | 21000 (~300 m) |
| `set CMB_AllowCombat to <0/1>` | 0 |
| `set CMB_UseRiderPose to <0/1>` (seated riding animations, needs `CMB_RiderPose.esp`) | 1 |
| `set CMB_EngineVolume to <0–100>` | 90 (70 up to test 46's build; a save keeps its own) |
| `set CMB_MaxTilt to <0–50>` (how far the bike and the rider pitch with the ground while riding, F4SE plugin; 0 = always level, parked too) | 45 |
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
| `set CMB_ViewEyeUp to <-30–20>`, `set CMB_ViewEyeForward to <-30–30>` (MCM "Eye height on the bike", "Eye forward on the bike", since 2026-11-06a, F4SE plugin: your eye in first person lower (-, the bike higher into view) or higher, back (-) or forward, in game units on top of `[View] EyeAt`; at once) | 0, 0 |
| `set CMB_TailLightMode to <0/1>` (MCM "Tail lamp lights the road", F4SE plugin; 0 = the lens only glows; next time you get on) | 1 |
| `set CMB_FirstPersonBike to <0/1>` (MCM "Bike in first person", F4SE plugin; 0 = no bike in first person; next time you get on) | 1 |
| `set CMB_LookOn to <0/1>` (MCM Look "Customise at the bike", since 2026-11-07a: 0 = no Customise and the stock look, as 2026-11-06a, the bikes at the next getting on, activation of the parked bike, "Apply the look" or load) | 1 |
| `set CMB_KitMode to <0–4>` (MCM Look "Field kit", since 2026-11-07a: 0 automatic, since 2026-11-09a the armour bench then the game's own, `WorkbenchArmorA` (up to 2026-11-08a the toolbox then the armour bench); 1 the toolbox, 2 the toolbox with the armour bench's keyword (both tests: the toolbox can't be sat in), 3 the armour bench, 4 the game's armour bench (since 2026-11-09a)) | 0 |
| `set CMB_KitWorked to -1` (console only, since 2026-11-07a: the mode automatic found working, since 2026-11-09a 3 or 4 (a 1 or 2 an older build wrote is forgotten); -1 = start at the armour bench again) | -1 |
| `set CMB_KitWhere to <0/1>` (MCM Look "Field kit only in your settlements", since 2026-11-14a: 1 = Customise at the parked bike opens the field kit only in a settlement whose workshop is yours, elsewhere a message and no kit; 0 = anywhere, as 2026-11-10a; MCM "Free customising" works anywhere either way) | 1 |
| `set CMB_KitPreview to <0–2>` (MCM "Field kit preview", since 2026-11-14a, F4SE plugin: how the field kit's armour menu shows the bike, 1 New, 0 As before (2026-11-10a's view, a tyre filling the menu), 2 Tune: `CMB_KitPrevSize` (%), `CMB_KitPrevTurn` and `CMB_KitPrevTilt` (steps of 6.4 degrees), `CMB_KitPrevUp`, `CMB_KitPrevZoomOut`, `CMB_KitPrevZoomIn`, the MCM's six "Preview ..." sliders; at the next Customise) | 1 (the sliders 30, 7, 0, 0, -1, 1) |
| `set CMB_LookOptions to <0–32767>` (console only, since 2026-11-09a, without F4SE: test 51's six script switches, 1 FastMount, 2 KitHeld, 4 ParkedReload, 8 PaletteIndex, 16 MountGuard, 32 HueFree, since 2026-11-10a test 52's five, 128 KitStash, 256 KitRetry, 512 MountEarly, 1024 WornColoursFirst, 2048 HueSwap, and since 2026-11-14a test 53's two, 4096 WornIndex, 8192 KeptMods (64 and 16384 are the plugin's own; it writes 32767 at its defaults); 0 = all off, as 2026-11-08a; 63 = 2026-11-09a's; with F4SE `CMB_Slope.dll` writes it from `[Look]` at its start, at a load and on getting on, so set those keys instead) | 4031 (63 in 2026-11-09a) |
| `set CMB_LookHue to <0–359>` (MCM Look "Paint hue", since 2026-11-08a: the Free colour paint's hue round the colour wheel, 0 red, 120 green, 240 blue; used only with Paint "Free colour", from "Apply the look" or the next getting on or activation of the parked bike) | 210 |
| `set CMB_LookShade to <0–3>` (MCM Look "Paint shade", since 2026-11-08a: the Free colour paint's shade, 0 Deep, 1 Normal, 2 Light, 3 Pastel) | 1 |
| `set CMB_LookPlateCrude to <0/1>` (MCM Look "Crude plate texts", since 2026-11-08a: 0 = the 14 crude plate texts not offered at the field kit, and a plate wearing one shows its design's own text from the next getting on, activation of the parked bike or "Apply the look") | 1 |
| `set CMB_BrakeKey to <scan code>` (MCM "Brake key (scan code)", F4SE plugin: 57 Space, 42 Left Shift, 29 Left Ctrl, 56 Left Alt, 45 X, 46 C; 0 = none: back (S) only; next time you get on) | 57 (Space) |
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

With MCM installed, all of these but the two sound picks, `CMB_RiderSteadyWay`, `CMB_PoseUseWindow`, `CMB_UseCameraFix`, `CMB_RiderUseOwn`, `CMB_FxThudDb`, `CMB_KitWorked`, `CMB_LookOptions` and the commands are in *Mod Config → Commonwealth Motorbike* instead. The 2026-11-06a build adds these controls there: in Riding "Look down on getting into first person (deg)" (`CMB_ViewTip`, 20; 0 = the view left as it is, as 2026-11-02a), "Eye forward on the bike" and "Eye height on the bike" (the two above), and "Power attacks throw you off" (`CMB_KnockOffPower`, off; on = every power attack does, as 2026-11-02a); in Sound "Landing sounds without metal" (`CMB_FxLandDull`, on; off = 2026-11-02a's sets) and "Water sound loop" (`CMB_FxWaterLoop`: "Wet road (the mod's own)", the default, "Churning water", or "As the 2026-11-02a build (spray)", next time you get on). The console's `set CMB_ViewTip to 15` sets the first. The 2026-11-07a build adds the Look section (11 controls, *Customising the bike* above), the 2026-11-08a build nine
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
back; `[View] Fov` below).

## CMB_Slope.ini (F4SE plugin): this build's new keys

`Data\F4SE\Plugins\CMB_Slope.ini` holds the plugin's settings, read again each time you get on; each section's comments
say what every key does. The 2026-11-14a build answers test 53, and every new behaviour has a key, an MCM value or a
`CMB_LookOptions` bit whose off value gives the 2026-11-10a build back (for the gears, all their rows together); the one
exception is the field kit's names (below):

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
| `[Sound] HeardRiseGears` (changed) | 2,0.79,0.65,1,1 | 2.5,0.95,0.5,1 |
| `[Sound] ShiftGapGears` (changed) | 0,2,3,1.5 | 0,2,3 |
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
| `[Sound] ShiftGapGears` (2026-11-09a's key) | 0,2,3 | 0,2,2.5 |
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
| `[Sound] HeardRiseGears` | 2.5,0.95,0.5,1 (test 51; 2,0.79,0.65,1,1 since 2026-11-14a) | 1,1,1,1 (or empty); 1,0.95,0.5,1 the build's first set |
| `[Sound] ShiftGapGears` | 0,2.0,2.5 (test 51; 0,2,3 since 2026-11-10a, 0,2,3,1.5 since 2026-11-14a) | empty; 0,1.5,1.75 the build's first set |
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
| `[Steer] LaunchFrom`, `LaunchLead` | 0.25, 0.45 | (parameters: the throttle a launch starts at; the speed cap's lead meanwhile) |
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
| `[Sound] HeardStop`, `HeardBrake`, `StopGap`, `StopHold`, `StopAfter` | 300, 600, 0.4, 0.4, 0.3 | (parameters; inert with `StopShift=0`) |
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
    CMB_BikeActivatorScript   parked bike menu
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
    CMB_GearRestoreF4SE       optional (F4SE): puts slot-57 gear back on after a ride
    CMB_LookF4SE              optional (F4SE, since 2026-11-07a): the chosen look's material swap on the parked and
                              first-person bikes (and on the ridden one where the game refuses its mods); since
                              2026-11-08a also the colours (the free paint, body-colour rims, the plate's), since
                              2026-11-14a also into the chosen options' swaps before the ridden bike goes on
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
                              plates, their texts and colours), and look_ids.txt, their records' committed IDs (since
                              2026-11-07a)
tools/syntax-check/           compile-checks the scripts on Linux without the CK
tools/rider/                  bike meshes (from the Sketchfab model or the vanilla bike), their textures and material
                              files (Blender), previews of the bike as the game shades it, riding clips (Python +
                              PyNifly), rider-pose plugin and AnimTextData (Python); since 2026-11-07a the badges'
                              atlas and materials (bike_art.py --badges, look_badges.py) and the paint palette
                              (look_paint.py); since 2026-11-08a the rims' and tyres' textures and the hue palette
                              (look_wheels.py), the plate's art (bike_art.py --plates, look_plates.py) and the new
                              shapes' own material files (look_shapes.py)
tools/sound/                  engine sound: the loops built from the recording, the engine model, a ride renderer,
                              the old synthesiser (Python + numpy)
tools/package/                since 2026-11-14a: packages a build (its README.txt, Data/ and two zips) from a commit and
                              the previous package's assets, and verifies the zips (docs/BUILD_GUIDE.md, *For developers:
                              packaging a build*)
```

## Roadmap

1. **Done, in testing in game:** ride / park / call / side bag / companions / fuel, worn and parked bike meshes,
   seated riding animations with lean, MCM menu, engine sound and gear restore.
2. **In testing, the 2026-11-07a to 2026-11-14a builds:** customising at the bike (the badges, the paint, the mirrors at
   a field kit; then the rims, the tyres, a free paint colour and the licence plate), the 2026-11-09a build's fixes for
   tests 50 and 51 (the parked bike kept out of people, items at speed, Caution, the wheels, the bridge's posts, the
   truck, first person, the gears, the water, the field kit, getting on), the 2026-11-10a build's for test 52
   (getting on quicker, items by hotkey at speed, the field kit with Global Stash, Free colour's first ride, Caution
   50's sidestep, the parked bike's guard, first person's diagnostic, the engine in the Pip-Boy, 3rd gear, the front
   wheel's shadow, the gentle water louder), and the 2026-11-14a build's for test 53 (number keys at speed, Free colour
   in third person, first person steady with the eye over the seat, the FOV dropped, the field kit's names, preview and
   settlements, the engine quiet in menus, five gears). **Next:** the 2026-11-14b build (handguns on the bike, looking
   back when reversing, the A/D lean in first person, sidesteps round bigger things, the right-hand cables); the next
   rounds of in-game testing; the remaining vanilla-timed stop and idle clips. Wheel spin and the bars' turn come with
   the Sketchfab build and F4SE (see DESIGN.md); more customisation in later builds (the helmet badges in 3D, the plates
   redrawn, the saddle's colour, wear), weathered paint, more badges, the front fender, the headlamp's colour and the
   seat; luggage and the mod's own toolbox and parts box.
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
