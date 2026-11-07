# Commonwealth Motorbike (Fallout 4 mod, work in progress)

A rideable motorbike for Fallout 4:

- **faster than on foot**: 250% of your speed by default, adjustable from the console
- **companions come along**: they run alongside at the same speed (or, opt-in, ride along hidden)
- **runs on Flamer Fuel**: one unit per 300 m ridden, taken from the side bag first, so it isn't a free speed boost in Survival
- **side bag**: small storage, size adjustable from the console
- **park it, call it, ride it**: activate the bike or use its keys (favorite them to a hotkey); optional F4SE hotkey
- **seated riding animations** with lean in turns and ridden U-turns; the bike turns with you on the spot and in conversations; since the 2026-11-01a build hits don't stagger you while riding (MCM "Steady in the saddle", so the bike no longer hangs round your hips through a stagger), and with F4SE the plugin checks that the seated clips are playing and the script puts them back if they aren't (test 47's rider "floating" after a fight was the plugin running out of copies of her bone data, held by the blood decals: fixed); since the 2026-11-02a build "Steady in the saddle" is a perk of its own with the two condition tabs the game's own stagger lining has (test 48: eight staggers got through the first one; the console's `CMB_RiderSteadyWay` tries the game's own perk too), the pose is left alone for 6 s after an item's use so an animation mod's use clip plays whole, the camera's with it (test 48's camera stuck after a stimpak), and with F4SE the hands let go of the grips while that clip plays (test 48's arm stretched while eating) and the pose isn't measured in first person, where the game's third-person skeleton stands; since the 2026-11-06a build using an item while riding fast (a stimpak by its hotkey, food from the Pip-Boy) no longer slows the bike: above 150 units a second the item animation mod's clip isn't played (the item is used as always), stopped or slow it plays, and the arm no longer stretches when eating right after the Pip-Boy (test 49); items another mod equips on you (a reload fixer's dummy potion) no longer start the item watch
- **an engine sound from a real V-twin** (demodave's recording, CC0): with F4SE (since test 44's build) the plugin runs a model of a four-speed gearbox and pitches and fades eleven loops every frame with your speed and throttle, shifting up as you pull away and falling off as you let go; since test 45's build the engine keeps a real ride's pace rather than the game's quick bike, so a pull-away climbs from the moment you press forward, each one shifting a little differently, the cruise holds steady and a roll-off falls slowly in gear; since test 46's build each loop's level is set at once rather than faded, so a gear change no longer cuts out, and the engine is louder and punchier, with hotter recordings, more between the cruise and a full-throttle pull and its full volume out past the riding camera (test 45's build needed the MCM's engine volume at 100); since test 47's a steady cruise wanders in pitch and level like a hand on a real throttle (since the 2026-10-31a build more, in slow swings of a second or two that peak 3 to 5% off the cruise's rpm, never past about 6%, and about 1 to 1.5 dB in level), each up-shift dips briefly as the throttle closes, the engine reverberates as the game's other sounds do, and the MCM's engine volume starts at 90 in a new save; since the 2026-11-01a build 1st and 2nd change up later, at about 2,600 rpm, and a stop changes down so you hear it (three blipped down-shifts rolling to a stop, two braking, then the clutch); since the 2026-11-02a build the idle is louder, 2.5 dB under the cruise where it was 8.7 under (test 48: "it feels like there is no sound"), so a stop no longer goes quiet and the start and stop sounds run into and out of it without a step; since the 2026-11-06a build the idle is a little louder (level with the cruise), each take-off starts with a short rev, and each gear change is longer (about half a second of the darker sound and the dip; `IdleDb`, `LaunchFlare`, `ShiftTime` and `ShiftDipTime` in `CMB_Slope.ini`); without F4SE, an idle and a cruise loop crossfaded by speed
- **a V-twin cruiser** as the bike (Nieve5677's Sketchfab model, CC-BY: see the credits), on the vanilla motorcycle's collision; with F4SE its wheels spin with the distance ridden and the bars turn with you (the hands go with them, and since the 2026-10-31a build the lower triple clamp too); the vanilla bike can be built instead
- **its look** (since the 2026-10-31a build): textured all over, with procedural textures baked from the 1.3-million-triangle model onto the game's mesh (the download has no textures): an oxblood tank and fenders with a clear coat and a cream double coachline, our own winged-wheel badge, dark mirror-like chrome, a black wrinkle-finish engine with bright fin edges, a leather-grained seat, tyres with their tread; a material file for every surface (the hook for paint and parts at a workbench later); with F4SE **a working speedometer** (its needle follows your speed, about 50 on the dial at full speed by default, and its numerals light up with the headlamp), **a tail light** lit while you ride that brightens with both rear signals when you brake, and **mirrors** that show a sky (Fallout 4 can't show real reflections), in the stock style or either of two styles hung under the bar ends (`[Look] Mirrors` in `CMB_Slope.ini`; since the 2026-11-07a build the ones you fit at the bike, which the parked bike shows too). Every new behaviour of the plugin has a key in `CMB_Slope.ini` whose off value gives the previous build's back; the textures and the lower triple clamp turning with the bars come with the meshes (the previous build's meshes copied back give its look). Since the 2026-11-01a build the tank's cream line is one smooth curve with round corners, the seat's piping is re-cut, the brake discs are our own drilled ones and the mirror glass is brighter; with F4SE the tail lamp lights the road behind a soft red, three times brighter while you brake (MCM "Tail lamp lights the road"), and **the bike is under you in first person** (MCM "Bike in first person"; no hands on the grips: the game shows no arms with the weapon away). Since the 2026-11-02a build the chrome is polished (its material files reflect six times as much, with sharper glints and screen-space reflections: test 48's "too dull"), the mirrors show the game's own mirror cube (test 48's pick of the two), the front brake disc has no light ring round its bore, and with F4SE the bike in first person stays under your eye at every speed (test 48: it slid back by 58 ms of the speed, so at full speed you sat over its rear wheel; `[View] Eye`). Since the 2026-11-06a build the chrome is toned down, still bright but not pearly or smeared (its material files reflect 2.5 times the cube where the 2026-11-02a build's did 6, with less specular and no screen-space reflections: test 49), the rims and discs are a little greyer, and with F4SE going into first person eases the view about 20 degrees down so the dial and the bars are in sight (MCM "Look down on getting into first person (deg)"; test 49's bike out of view looking level), with a riding field of view (off by default) and your eye's place on the bike in the MCM too; the optional MO2 folder "2026-11-02a look (A-B)" gives the 2026-11-02a build's look back
- **customising at the bike** (since the 2026-11-07a build): the parked bike's menu has a Customise button; a field kit comes out of the side bag beside the bike and you change the badges on both sides of the tank and on the rear fender (13 emblems of our own, from the Brotherhood of Steel to a pre-war army star, and four of the game's own by path), the paint (13 faction schemes, 24 colours, 6 neutrals, each with its coachline) and the mirrors (stock, under the bars egg or D, none) at the armour menu, paying in components; the bike shows the new look parked, ridden and in first person. **Nothing changes until you choose**: every slot starts on the bike as it came. The MCM's Look section turns it off, picks the kit, and has a free mode with a choice per slot and faction sets (see *Customising the bike* below)
- **a headlamp** (the Sketchfab build, F4SE): a round LED lamp on the fork bracket with its running light lit, and a real spot beam (like the power armor's, a light the mod places at the lamp) that turns with the bars and tilts with the bike; MCM: off, on, or on at night, and a hotkey
- **rides like a vehicle, not a person**: 75% less fall damage while riding (adjustable), deep water ends the ride and leaves the bike on the bank, and an enemy's hit knocks you off (optional; since the 2026-11-06a build a power attack only when it takes the "Big hit" share of your health, as any other hit, explosions always: MCM "Power attacks throw you off", off by default); with F4SE, hostile people, creatures and smaller robots (since test 43 by a list of their own, `CMB_RamRobots`) the bike hits at speed are knocked over and take a little damage, the bike losing some speed at each (since test 45's build a dog the mod's script hasn't answered for by the time you reach it is ridden through rather than braked for, and knocked over when the answer comes, and a robot ridden at again after a hit is knocked over again; since test 46's an old save's knock-overs no longer make it brake for those same animals; MCM "Knock enemies over"; never companions, essential characters, anyone in power armor or the big ones: super mutants, behemoths, deathclaws, sentry bots and the like; since the 2026-11-01a build the knock-over that takes an enemy's last health kills it, and the kill is yours, experience and quests as for a shot: MCM "Knock-overs can kill"; since the 2026-11-02a build a knock-over holds the throttle to 85% of the speed for a quarter of a second, not 60% for 0.4 s, and a pack's hits share one dip, so the bike no longer nearly stops at a pack; an enemy of a medium race the script hasn't answered for by the time you reach it is ridden through, not braked for, when it was said yes to earlier in the ride or you are in a fight; and a kill by the bike gives the game's own experience, the killing hit being your own damage: MCM "Kill experience")
- **follows the ground**: the parked bike stands on the ground, tilted to match the slope (with F4SE, on the ground you just rode over, and since test 46's build a called bike on the ground under its wheels, leaning up to 20° across a slope; since test 47's getting off where you got on puts the bike back where it stood, the parked spot is checked for room as a call's is, and a bike called while you stand on a car comes to the ground beside it); with F4SE, the bike also pitches with the ground while you ride, leans into turns at speed (the rider with it, head level), stops short of boulder faces but slides along a railing beside it, climbs over low fallen trunks and stumps and up a step, but since test 45's build not onto a rail, a barrier or a log with a drop behind it (since test 46's not onto a rail lying on the ground or met at an angle nor along a fence either, and at full speed it stops short of a rail rather than with its front wheel in it; since test 47's it eases off only for what stays in its way, not for things you steer past, looks along its turn, stops about a wheel's radius short of a rail, isn't climbed onto a rail met at a shallow angle and doesn't ride on along one its front wheel is in), keeps its tyres on top of small bumps, takes a landing on its suspension and keeps going, backs up to a rail or a ledge's lip with its rear tyre just short of it and down off something it hangs on, turns in a circle rather than on the spot, climbs slopes too steep to walk up, and the camera sits farther back (since the 2026-11-01a build it also looks along the arc of the turn you're in, so a thing beside the curve eases the throttle by its distance instead of stopping the bike, a barrier on legs isn't climbed, a call from on top of a car or a truck puts the bike on the ground beside it rather than on its edge, and a high drop no longer halves the speed for most of a second; since the 2026-11-02a build a narrow thing ahead, a mailbox, a lamp post or a sign, is eased past by its distance and never stops the bike, while walls, cars and rails met square still do, a kerb or a log at speed holds the throttle to 85% rather than 55%, and a touch along a rail or a car's flank picks up again at once rather than from a crawl; since the 2026-11-06a build it steps round a post or a mailbox on its path to the open side (`Sidestep`) when you ride straight at it, a rail over posts is a wall, a pull-away from rest is punchier in its first second, and a call from on top of a truck tries the most room's own navmesh point first, so the bike comes down to the street)
- **its own sounds** (since the 2026-11-01a build; the game's own sound files, since the 2026-11-02a build under sound records of the mod's own, heard at the riding camera's distance: test 48 heard none of them): your character's own jump and landing sounds are muted while you ride; a tyre thump on every landing with a real fall, louder the higher the drop, a metal clunk on big ones and a splash into water; with F4SE a spray riding through shallow water, by speed and depth (the MCM's Sound section: "Bike sounds through the mod's own records", "Landing loudness range (dB)"); since the 2026-11-06a build landings sound like tyres and a dull thud, no metal, riding into water splashes, and riding through water is the mod's own wet-road swish, quieter when slow, louder at speed (MCM "Landing sounds without metal", "Water sound loop")
- **MCM menu** for every setting (with MCM installed); with F4SE, gear in the bike's slot goes back on after a ride

> **Status: in testing.** It has been tested in game round by round since the first build (test 49 the
> latest), each round answered from the logs and videos sent back. Every round's changes are checked offline
> before they ship: the plugin's structure, every script property and the vanilla form IDs, the scripts compiled
> against stand-in versions of the Fallout 4 scripting API, and `CMB_Slope.dll` run against a fake game
> (`tools/f4se-slope/test`). What changed since the last round hasn't run in the game until the next, so expect
> fixes after each.
> [TESTING.md](docs/TESTING.md) says what to send back.

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
| F4SE (optional) | dedicated hotkey, weight-based side bag, slot-57 gear put back on after a ride, steeper slopes, a camera farther back, the bike tilting with the ground and knocking enemies over while riding, the bike brought from a door put on a spot with room, the parked bike laid on the ground under you, the engine sound's gears and pitch, and the speedometer's needle, the tail and brake light and the choice of mirrors, and since the 2026-11-01a build the tail lamp's light, the bike in first person, the brake key, the rider-pose check and the water sound, and since the 2026-11-02a build the hands let go for an item's use clip, the first-person bike under your eye, narrow things eased past and the frame-rate line in the log, and since the 2026-11-06a build the sidestep, the launch from rest, items at speed, the first-person tip and field of view and the water loop's level, and since the 2026-11-07a build the mirrors you fit at the bike on the ridden bike and the chosen look on the parked and first-person bikes (F4SE's material swap; without F4SE those two stay stock) (the `CMB_Slope.dll` plugin, Fallout 4 1.11.240 only; the rays and the engine sound also need the Address Library), MCM menu; without it you favorite the keys for a hotkey and the bag counts items |
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

Since the 2026-11-07a build (the first customisation build). Activate the parked bike and choose **Customise**: a field
kit (a toolbox) comes out of the side bag beside the bike, on your side, you stand at it and the armour menu opens with
the bike listed as "Motorbike". Its five slots:

| Slot | Choices (the first is the bike as it came) | Cost |
|---|---|---|
| Tank badge, left | Stock (winged wheel), None, Brotherhood of Steel, Brotherhood helmet, Enclave, Enclave helmet, Gunners, Minutemen, Railroad, Institute, Vault-Tec, Atom Cats, Raiders, Children of Atom, Pre-war army star (all 13 drawn for the mod), Gunners (game art), Pre-war army star (game art) | a badge Adhesive 1, Cloth 1; Stock and None free |
| Tank badge, right | the same, and "Same as the left" (the default: it follows the left; any other choice ends that, "Same as the left" brings it back) | the same; "Same as the left" free |
| Rear fender badge | None (as it came), the 13 of ours, the two chest decals and, on the fender only, the Minutemen flag and the Brotherhood flag (game art) | Adhesive 1, Cloth 1 |
| Paint | Factory (oxblood); 13 schemes, two-tone with their coachline (the eleven factions', Nuka-Cola, Red Rocket); 24 colours (Fire red to Raspberry); 6 neutrals (Gloss black, Pearl white, Silver, Gunmetal, Pre-war cream, Primer grey); "Palette test: colour index" (cobalt blue if the colour lookup works, primer grey if not) | Factory Oil 1; a colour Adhesive 2, Oil 2 and the Armorer perk |
| Mirrors | Stock, Under the bars (egg), Under the bars (D), None | stock Steel 1, Glass 1; egg or D Steel 2, Glass 2, Screws 1; none Screws 1; a mirror taken off comes back as a loose mod |

Leave the menu and the kit goes back into the bag; the bike shows the new look parked, ridden and in first person (the
parked and first-person bikes through F4SE; the ridden bike's mirrors through `CMB_Slope.dll`). In one of your
settlements its workshop's components count; elsewhere the side bag's do as well as yours. **Nothing changes until you
choose**: each slot starts on the bike as it came, so with no choice the bike is the 2026-11-06a build's.

The field kit tries the toolbox first; if the game won't seat you at it within 6 seconds it puts an armour bench beside
the bike instead, and remembers the one that worked (`CMB_KitWorked`). Emergency reset also puts a field kit away.

**MCM, Look** (before Hotkeys): "Customise at the bike" (on: the Customise button; off: no button and the bike as it
came), "Field kit" (Automatic, Toolbox, Toolbox (armour bench keyword), Armour bench), "Parts from the side bag", and
"Free customising (no field kit, no cost)", which shows a choice per slot (the five above), "Faction set" (the paint
and all three badges of one of eleven sets) and "Apply the look": it puts the choices on the parked bike at once and on
the ridden bike at the next getting on. Turning "Customise at the bike" off (or changing a choice without "Apply the
look") takes effect at the next getting on or activation of the parked bike (or Apply, or a load).

Known, left for now: in the menu, while the right badge follows the left, the preview shows the right as the left was
when the menu opened (the bike follows the new left once you close it); after a load the parked bike's look comes back
within a second; the ridden bike needs F4SE's swap where the game refuses its mods (logged); replacing the mirrors at
the kit gives that mirror's loose mod back each time; an emergency reset while the kit switches from the toolbox to the
bench (about 2 s), with a new Customise straight after it, can let the old switch go on into the new session (rare:
wait a few seconds after a reset). Rims, tyres and more badges come later.

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
| `set CMB_KitMode to <0–3>` (MCM Look "Field kit", since 2026-11-07a: 0 automatic, the toolbox then the armour bench; 1 the toolbox, 2 the toolbox with the armour bench's keyword, 3 the armour bench) | 0 |
| `set CMB_KitWorked to -1` (console only, since 2026-11-07a: the mode automatic found working, 1 or 3; -1 = try the toolbox first again) | -1 |
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

With MCM installed, all of these but the two sound picks, `CMB_RiderSteadyWay`, `CMB_PoseUseWindow`, `CMB_UseCameraFix`, `CMB_RiderUseOwn`, `CMB_FxThudDb`, `CMB_KitWorked` and the commands are in *Mod Config → Commonwealth Motorbike* instead. The 2026-11-06a build adds seven controls there: in Riding "Look down on getting into first person (deg)" (`CMB_ViewTip`, 20; 0 = the view left as it is, as 2026-11-02a), "Field of view riding in first person" (`CMB_ViewFov`, 0 = your own; 60-120), "Eye forward on the bike" and "Eye height on the bike" (the two above), and "Power attacks throw you off" (`CMB_KnockOffPower`, off; on = every power attack does, as 2026-11-02a); in Sound "Landing sounds without metal" (`CMB_FxLandDull`, on; off = 2026-11-02a's sets) and "Water sound loop" (`CMB_FxWaterLoop`: "Wet road (the mod's own)", the default, "Churning water", or "As the 2026-11-02a build (spray)", next time you get on). The console's `set CMB_ViewTip to 15` and `set CMB_ViewFov to 90` set the first two. The 2026-11-07a build adds the Look section (11 controls, *Customising the bike* above).

## CMB_Slope.ini (F4SE plugin): this build's new keys

`Data\F4SE\Plugins\CMB_Slope.ini` holds the plugin's settings, read again each time you get on; each section's comments
say what every key does. Every new behaviour of the 2026-11-07a build has a key or an MCM control whose off value gives
the 2026-11-06a build back, and each customisation slot starts on the bike as it came, so nothing changes until you
choose:

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
| `[Sound] LaunchFlare` | 0.5 | 0: no launch rev |
| `[Sound] LaunchFlareTime` | 1.2 (seconds) | (a parameter) |
| `[Fx] WaterSpeedFull` (changed) | 900 | 600 |
| `[Fx] WaterCurve` | 2 | 1: the speed's share linear |
| `[Fx] WaterChurnDb`, `WaterRoadDb` | -8, 0 (dB) | (trims of the MCM's two loops; unused with "As the 2026-11-02a build (spray)") |
| `[View] TipTime` | 0.4 (seconds) | (the MCM's "Look down ..." eased over this; 0 = at once) |
| `[View] FovTime` | 0.3 (seconds) | (the MCM's "Field of view ..." eased to and back over this) |
| `[View] FovOffset` | auto | (where PlayerCamera keeps the world FOV: found by its value, or a hex offset 0x100-0x1F0) |
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
| `[View] EyeAt`, `EyeSide`, `EyeSmooth`, `EyeSmoothZ`, `EyeMax` | 0,12,128, 1, 0.05, 0.25, 150 | (parameters: your eye's place on the bike, x right, y forward, z up; `EyeSide=0` follows fore-aft and height only) |
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
| `[Sound] ShiftDraw` (changed) | 2300,3000 | 2000,2900 |
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
    CMB_HotkeyF4SE            optional F4SE hotkey
    CMB_GearRestoreF4SE       optional (F4SE): puts slot-57 gear back on after a ride
    CMB_LookF4SE              optional (F4SE, since 2026-11-07a): the chosen look's material swap on the parked and
                              first-person bikes (and on the ridden one where the game refuses its mods)
    CMB_RamScript             knocks enemies over (does anything only with F4SE and CMB_Slope.dll, whose rays see them)
  Meshes/CMB/                 the bike meshes and CMB_BikeParts.ini go here (built by tools/rider)
  Textures/CMB/Bike/          the bike's textures (built by tools/rider); the three palette textures earlier builds
                              put directly in Textures/CMB are no longer used and can be deleted
  Materials/CMB/Bike/         the bike's material files, one for the riding bike and one for the parked bike per
                              surface (built by tools/rider)
  Sound/FX/CMB/               engine sounds: here only the synthesised fallback four (the idle, cruise, start and stop
                              of the script's crossfade); the package's 13, built by tools/sound from demodave's
                              recording, replace them and add the nine loops the plugin drives, and since 2026-11-06a
                              the wet-road water loop `CMB_FxWaterRoadLP.wav` (made by tools/sound/make_water_loop.py)
  MCM/Config/                 MCM menu and hotkey (written by the generator)
  F4SE/Plugins/CMB_Slope.dll  optional F4SE plugin: steeper slopes, farther camera, bike tilt, the bike's moving parts,
                              speedometer, lights and mirrors (tools/f4se-slope); its settings in CMB_Slope.ini
compile_scripts.bat           compiles the scripts with the Creation Kit's compiler
make_rider_pose.bat           builds CMB_RiderPose.esp + its AnimTextData from your load order
docs/                         install, assets, testing and design notes
tools/build.sh                regenerates the plugin and runs all offline checks
tools/esp-generator/          C# (Mutagen) plugin generator + plugin/script cross-check; look_options.json, the one
                              table of the customisation's slots, options, badges, paint rows and faction sets, and
                              look_ids.txt, their records' committed IDs (since 2026-11-07a)
tools/syntax-check/           compile-checks the scripts on Linux without the CK
tools/rider/                  bike meshes (from the Sketchfab model or the vanilla bike), their textures and material
                              files (Blender), previews of the bike as the game shades it, riding clips (Python +
                              PyNifly), rider-pose plugin and AnimTextData (Python); since 2026-11-07a the badges'
                              atlas and materials (bike_art.py --badges, look_badges.py) and the paint palette
                              (look_paint.py)
tools/sound/                  engine sound: the loops built from the recording, the engine model, a ride renderer,
                              the old synthesiser (Python + numpy)
```

## Roadmap

1. **Done, in testing in game:** ride / park / call / side bag / companions / fuel, worn and parked bike meshes,
   seated riding animations with lean, MCM menu, engine sound and gear restore.
2. **In testing, the 2026-11-07a build:** customising at the bike (the badges, the paint, the mirrors at a field
   kit). **Next:** the next rounds of in-game testing; the remaining vanilla-timed stop and idle clips. Wheel spin and
   the bars' turn come with the Sketchfab build and F4SE (see DESIGN.md); more customisation in later builds: rims,
   tyres, weathered paint and a hue slider; more badges, the front fender, the plate, the headlamp's colour and the
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
  Content License. `tools/sound/make_water_loop.py` cuts three stretches of it into the mod's own wet-road loop; the
  recording isn't in this repository.
