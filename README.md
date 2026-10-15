# Commonwealth Motorbike (Fallout 4 mod, work in progress)

A rideable motorbike for Fallout 4:

- **faster than on foot**: 250% of your speed by default, adjustable from the console
- **companions come along**: they run alongside at the same speed (or, opt-in, ride along hidden)
- **runs on Flamer Fuel**: one unit per 300 m ridden, taken from the side bag first, so it isn't a free speed boost in Survival
- **side bag**: small storage, size adjustable from the console
- **park it, call it, ride it**: activate the bike or use its keys (favorite them to a hotkey); optional F4SE hotkey
- **seated riding animations** with lean in turns and ridden U-turns; the bike turns with you on the spot and in conversations; an **engine sound** that follows your speed
- **a Harley-Davidson Iron 883** as the bike (Nieve5677's Sketchfab model, CC-BY), on the vanilla motorcycle's collision; with F4SE its wheels spin with the distance ridden and the bars turn with you (the hands go with them); the vanilla bike can be built instead
- **a headlamp** (the Harley build, F4SE): a round LED lamp on the fork bracket with its running light lit, and a real spot beam that turns with the bars and tilts with the bike; MCM: off, on, or on at night, and a hotkey
- **rides like a vehicle, not a person**: 75% less fall damage while riding (adjustable), deep water ends the ride and leaves the bike on the bank, and an enemy's hit knocks you off (optional)
- **follows the ground**: the parked bike stands on the ground, tilted to match the slope (with F4SE, on the ground you just rode over); with F4SE, the bike also pitches with the ground while you ride, turns in a circle rather than on the spot, climbs slopes too steep to walk up, and the camera sits farther back
- **MCM menu** for every setting (with MCM installed); with F4SE, gear in the bike's slot goes back on after a ride

> **Status: never run in game.** The plugin is generated and verified offline: its structure, every script property
> and the vanilla form IDs are checked, and the scripts compile cleanly against stand-in versions of the
> Fallout 4 scripting API. Nobody has loaded it in the game yet, so expect a round or two of fixes.
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

Getting off reverses all of that and parks the bike next to you. Indoors, power armor and furniture automatically park it outside; deep water leaves it on the bank.

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
| Creation Kit (optional) | not needed: the scripts can be compiled with Caprica (`tools/syntax-check`); `compile_scripts.bat` uses the Creation Kit's compiler if you have it |
| F4SE (optional) | dedicated hotkey, weight-based side bag, slot-57 gear put back on after a ride, steeper slopes, a camera farther back and the bike tilting with the ground while riding, and the parked bike laid on the ground under you (the `CMB_Slope.dll` plugin, Fallout 4 1.11.240 only), MCM menu; without it you favorite the keys for a hotkey and the bag counts items |
| Testing in game + Papyrus log | I can't run the game; the log and screenshots are how fixes happen |

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
| F4SE hotkey | **B** by default: off / on / call |

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
| `set CMB_EngineVolume to <0–100>` | 70 |
| `set CMB_MaxTilt to <0–50>` (how far the bike and the rider pitch with the ground while riding, F4SE plugin; 0 = always level, parked too) | 45 |
| `set CMB_HeadlampMode to <0/1/2>` (the headlamp: off, on while riding, on at night; F4SE plugin and the Harley build; the MCM hotkey toggles it) | 2 |
| `set CMB_RidingCameraDistance to <units>` (F4SE plugin; the game's own is about 150) | 450 |
| `set CMB_MaxSlope to <degrees>` (steepest slope while riding, F4SE plugin; on foot the game allows 47) | 45 |
| `set CMB_TurnRadius to <units>` (tightest turn at riding speed, F4SE plugin; 0 = turn like on foot) | 180 |
| `set CMB_TurnRadiusSlow to <units>` (tightest turn at walking pace, F4SE plugin) | 50 |
| `set CMB_StandTurnRate to <deg/s>` (turning when stopped, F4SE plugin) | 60 |
| `cqf CMB_ControllerQuest EmergencyReset` | undo everything if stuck |
| `cqf CMB_ControllerQuest ForceGiveKeys` | keys, if an alternative-start mod skipped the Pip-Boy |

With MCM installed, all of these are in *Mod Config → Commonwealth Motorbike* instead.

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
    CMB_SideBagScript         capacity-limited side bag
    CMB_PlayerAliasScript     save/load hook
    CMB_HotkeyF4SE            optional F4SE hotkey
    CMB_GearRestoreF4SE       optional (F4SE): puts slot-57 gear back on after a ride
  Meshes/CMB/, Textures/CMB/  the bike meshes and their textures go here (built by tools/rider)
  Sound/FX/CMB/               engine sounds (synthesised by tools/sound)
  MCM/Config/                 MCM menu and hotkey (written by the generator)
  F4SE/Plugins/CMB_Slope.dll  optional F4SE plugin: steeper slopes, farther camera, bike tilt (tools/f4se-slope)
compile_scripts.bat           compiles the scripts with the Creation Kit's compiler
make_rider_pose.bat           builds CMB_RiderPose.esp + its AnimTextData from your load order
docs/                         install, assets, testing and design notes
tools/build.sh                regenerates the plugin and runs all offline checks
tools/esp-generator/          C# (Mutagen) plugin generator + plugin/script cross-check
tools/syntax-check/           compile-checks the scripts on Linux without the CK
tools/rider/                  bike meshes (from the Sketchfab model or the vanilla bike), riding clips (Python + PyNifly),
                              rider-pose plugin and AnimTextData (Python)
tools/sound/                  engine sound synthesiser (Python + numpy)
```

## Roadmap

1. **Done, untested in game:** ride / park / call / side bag / companions / fuel, worn and parked bike meshes,
   seated riding animations with lean.
2. **Next:** in-game testing; the remaining vanilla-timed stop and idle clips. MCM menu, engine sound and
   gear restore are in, untested. Wheel spin and the bars' turn come with the Harley build and F4SE (see DESIGN.md).
3. **Later:** a visible pillion passenger, mount/dismount animations. Possibly a v2 built on the engine's mount
   system instead ([DESIGN.md](docs/DESIGN.md)).

## Credits

- Bike model: ["Harley Davidson Iron 883 2015"](https://sketchfab.com/3d-models/harley-davidson-iron-883-2015-612071b783f14a7288df2d361be9a244)
  by [Nieve5677](https://sketchfab.com/niev), licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
  Converted for the game by `tools/rider/harley_meshes.py`: cut down from 1.3 million triangles to about 110,000,
  coloured by part name (the download has no textures), scaled to the vanilla bike's length and put on the vanilla
  motorcycle's collision. The converted meshes aren't in this repository; anyone sharing them keeps this credit.
