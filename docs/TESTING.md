# Testing in game

I can't run Fallout 4, so in-game testing is yours. These checks are ordered so that the first failure points at one specific part.

## Turn on Papyrus logging first

In `Documents\My Games\Fallout4\Fallout4Custom.ini`:

```ini
[Papyrus]
bEnableLogging=1
bEnableTrace=1
bLoadDebugInformation=1
```

The log goes to `Documents\My Games\Fallout4\Logs\Script\Papyrus.0.log`. Every mod action writes a line starting with `[CMB]`, and script errors show up there too.

Without F4SE you'll see one or two harmless errors about the `F4SE` / `CMB_HotkeyF4SE` scripts not being found. That's the mod checking whether they're there. When something breaks, send the log, plus a screenshot or a short clip if it's visual.

## Test order

Use a throwaway save in an open area (e.g. outside Sanctuary), with a companion following you, some **Flamer Fuel** in your inventory,
and, if you have one, a bag or other gear that sits in an unusual slot.

| # | Do | Expect |
|---|---|---|
| 1 | Load the save while outdoors | "Motorbike Keys (2)" added (Aid tab), plus a hint. On a new game this happens when you first step outside Vault 111 |
| 2 | Use the keys | menu "Your motorbike isn't nearby." |
| 3 | Pick "Call it here" | the bike appears a few steps ahead, facing your way (invisible = `CMB_BikeParked.nif` missing) |
| 4 | Activate the bike → "Ride" | short fade; you're in 3rd person, **seated** on the bike, hands on the bars, left foot down; "Fuel: N" shown; your bag still on (no bike under you = `CMB_BikeWornRider.nif`/`CMB_BikeWornRiderF.nif` missing; standing over the bike = see row 4b) |
| 4b | *(only if you stand over the bike)* check `CMB_RiderPose.esp` is active (and, with MO2, the *Rider Pose* mod) | then the seated clips aren't playing: send the log, a screenshot, and what `make_rider_pose.bat` printed |
| 4c | Cripple a leg or an arm (Survival), ride | still seated (the crippled-limb entries are copied too) |
| 5 | Run around, turn | clearly faster than on foot (~2.5×), feet up on the pegs, leaning forward, bike and rider lean into turns; no jumping, no sprinting, weapons holstered; your companion keeps up running alongside |
| 5b | Stop, turn on the spot, start again; talk to someone while seated | foot goes down when stopped, smooth start/stop; the bike turns with you on the spot and stays lined up in dialogue, hands on the grips. `set CMB_BikeFollowsRider to 0` and get on again for the old planted bike, to compare |
| 5c | While riding, hold the key for the opposite direction (a U-turn) | you swing round in a short leaning arc and keep going, instead of stopping, spinning and setting off backwards |
| 6 | Use the keys again (or favorite them and press the hotkey) | fade; the bike is parked to your right; after 300 m or more of riding, Flamer Fuel went down by about one per 300 m |
| 7 | Activate the bike → "Open side bag" | a container opens; put stuff in |
| 8 | Overfill the bag (default 60 lbs with F4SE, or 60 items without) | extra items bounce back with "The side bag is full" |
| 9 | Ride up to a building door and go inside | auto-dismount; outside again, the bike is parked by the door |
| 10 | Ride, save, load that save | still riding, still fast, still can't jump |
| 11 | Ride, fast travel | still riding at the destination |
| 12 | *(opt-in, outside companion quests)* `set CMB_CompanionMode to 1`, ride, get off | companion disappears while riding and steps out behind you afterwards |
| 13a | Put all your Flamer Fuel in the side bag, ride | fuel is taken from the bag first |
| 13b | Ride until the fuel runs out | "Your motorbike ran out of fuel." and the bike is parked next to you; getting back on is refused until you have fuel |
| 14 | Try riding in power armor | refused with a message |
| 15 | Get on, sit still, then ride off and stop | engine start, idle while standing, louder/higher while moving, run-down when you get off (silent = see the engine-sound note in DESIGN.md) |
| 16 | *(F4SE)* wear something in slot 57, ride, get off | it comes off while riding and goes back on afterwards |
| 17 | *(MCM)* Mod Config → Commonwealth Motorbike | every setting there; change the speed, get on: the new speed applies |
| 18 | Ride off a drop that hurts on foot (try the same drop on foot first) | about 75% less damage (`CMB_FallDamageCut`); in Survival, a drop that cripples your legs on foot shouldn't while riding (please check: the cut is on fall damage, and leg damage from falls should follow it). Landing still shows the standing clips unless the jump clips were extracted (ASSETS.md) |
| 19 | Ride into a lake or a river until you'd swim, also off a ledge into deep water | "The motorbike can't go into deep water."; you're off and swimming, no bike in sight. Using the keys while swimming is refused. Climb out: about 3 s later "Your motorbike rolls up." and it's a few steps ahead of you, on the ground. Shallow water (paddling depth) rides normally |
| 20 | Get on next to an enemy; let a bloatfly sting you; take a big hit (a shotgun blast, a power attack, a grenade) | nothing in the first 3 s; small stings don't knock you off; the big hit does: "You're knocked off the motorbike.", bike parked next to you (the log says how much health it took). `set CMB_KnockOffDamage to 25` needs bigger hits; with `set CMB_DismountOnHit to 0` you stay on, and when a fight starts (weapons off while riding) a hint says how to get off |
| 21 | Load a save from before the keys arrived (or a new game), go outside | exactly two keys and one hint, even right after a load or a door |

## Console settings

| Command | Effect |
|---|---|
| `set CMB_SpeedPercent to 300` | faster bike (100–500). Above ~350 the world may not stream in fast enough |
| `set CMB_BagCapacity to 200` | bigger side bag (lbs with F4SE, items without; 0 = unlimited) |
| `set CMB_CompanionMode to 0` / `1` | companions run alongside (default) / ride along hidden (riskier during companion quests and scenes) |
| `set CMB_UseFuel to 0` | free riding, no fuel |
| `set CMB_FuelDistance to 10500` | twice as thirsty (default 21000 = one Flamer Fuel per ~300 m) |
| `set CMB_AllowCombat to 1` | shooting while riding (takes effect next time you get on) |
| `set CMB_ForceThirdPerson to 0` | stay in your current camera |
| `set CMB_UseRiderPose to 0` | no seated animations (run in place over the bike); `1` to turn them back on, next time you get on |
| `set CMB_HotkeyCode to 34` | F4SE hotkey (DirectX scan code, 34 = G, 0 = off); save and reload afterwards |
| `set CMB_EngineVolume to 40` | quieter engine (0–100, 0 = silent) |
| `set CMB_FallDamageCut to 100` | no fall damage while riding (0–100, default 75 = 75% less) |
| `set CMB_DismountOnHit to 0` | enemies' hits don't knock you off (default 1) |
| `set CMB_KnockOffDamage to 25` | only hits taking 25% of your max health knock you off (default 10; power attacks and explosions always do; 0 = any hit) |
| `set CMB_BikeFollowsRider to 0` | the worn bike stays planted on the ground instead of turning with the seated rider (default 1) |

Speed changes apply the next time you get on.

## Finding the mod's forms in the console

The plugin is light (ESL), so its form IDs start with `FE` and depend on your load order. Find them with
`help "Motorbike" 4` (or `help CMB_ 4`). For example, to look at the worn bike directly:
`player.equipitem <CMB_BikeRiderArmor id>`.

**Keys never arrived?** They wait until you're outdoors *with a Pip-Boy*. Alternative-start mods sometimes skip the Pip-Boy. Then:

```
cqf CMB_ControllerQuest ForceGiveKeys
```

## Emergency reset

If you end up stuck (still fast, can't jump, bike missing, companion missing):

```
cqf CMB_ControllerQuest EmergencyReset
```

If the console rejects that, try `cqf CMB_ControllerQuest "CMB_ControllerScript.EmergencyReset"`.
It removes the worn bike, restores speed and controls, clears the riding animations, brings hidden companions back and parks the bike next to you.
Still seated after getting off? `player.caf` (ChangeAnimFlavor with no keyword) clears the riding animation flavour by hand.

**Before uninstalling:** get off the bike (or run the reset), then save. Uninstalling mid-ride would leave the speed bonus on you and companions hidden in the holding cell.

## What to send back if something fails

1. Which step number failed and what happened instead
2. `Papyrus.0.log` (look for `[CMB]` and `error`)
3. Any Creation Kit compile errors, full text
4. Your mod list if it might be a conflict (anything touching player animations, companions or movement speed)
5. For animation problems: the text `make_rider_pose.bat` printed
