# Commonwealth Motorbike (Fallout 4 mod, work in progress)

A rideable motorbike for Fallout 4:

- **faster than on foot**: 250% of your speed by default, adjustable from the console
- **companions come along**: they ride with you (hidden while riding) or run alongside at the same speed
- **side bag**: small storage, size adjustable from the console
- **park it, call it, ride it**: activate the bike or use its keys (favorite them to a hotkey); optional F4SE hotkey

> **Status: never run in game.** The scripts compile cleanly against stand-in versions of the Fallout 4
> scripting API (see `tools/syntax-check`), but nobody has built the plugin in the Creation Kit or
> tested it in game yet. Expect a round or two of fixes. [TESTING.md](docs/TESTING.md) says what to send back.

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

Getting off reverses all of that and parks the bike next to you. Indoors, power armor and furniture automatically park it outside.

## What's needed to build it

| Need | Who | Notes |
|---|---|---|
| Fallout 4 on PC + **Creation Kit** (free on Steam) | you | builds the `.esp` and compiles the scripts |
| **Outfit Studio** + NifSkope | you | one-time conversion of the vanilla motorcycle into a wearable mesh ([ASSETS.md](docs/ASSETS.md)) |
| Archive2 (comes with the CK) | you | extracts the vanilla mesh |
| F4SE | optional | dedicated hotkey and weight-based side bag; without it you use a favorites hotkey and an item-count bag |
| Testing in game + Papyrus log | you | I can't run the game; the log and screenshots are how fixes happen |
| An animator (or lots of patience) | later | real riding animations, see roadmap |

## Getting started

1. Build it: [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md) (Creation Kit, step by step)
2. Make the worn bike mesh: [docs/ASSETS.md](docs/ASSETS.md)
3. Test it: [docs/TESTING.md](docs/TESTING.md)

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
| `set CMB_CompanionMode to <0 run alongside / 1 ride along>` | 1 |
| `set CMB_AllowCombat to <0/1>` | 0 |
| `cqf CMB_ControllerQuest EmergencyReset` | undo everything if stuck |

## Repository layout

```
Scripts/Source/User/      Papyrus sources (copy into Data\Scripts\Source\User)
  CMB_ControllerScript    the brain: mount, dismount, speed, companions, parking
  CMB_BikeActivatorScript parked bike menu
  CMB_KeysEffectScript    keys aid item
  CMB_SideBagScript       capacity-limited side bag
  CMB_PlayerAliasScript   save/load hook
  CMB_HotkeyF4SE          optional F4SE hotkey
docs/                     build, assets, testing and design notes
tools/make_rider_pose.py  builds the experimental seated-pose animation folder
tools/syntax-check/       compile-checks the scripts on Linux without the CK
```

## Roadmap

1. **Stage 1 (this):** working ride / park / call / side bag / companions.
2. **Stage 2:** seated rider pose from vanilla clips (experimental, [ASSETS.md](docs/ASSETS.md#stage-2-experimental-seated-rider-pose)).
3. **Stage 3:** real riding animations, a visible pillion passenger, engine sounds tied to speed. Possibly a v2 built on the engine's mount system instead ([DESIGN.md](docs/DESIGN.md)).
