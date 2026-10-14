# Install guide

The plugin (`Data/CommonwealthMotorbike.esp`) is **already built**: all records, scripts and properties are in it.
**No Creation Kit is needed** for any step. What's left is the game-derived files, the compiled scripts, and a copy.

| Step | Time | Tool |
|---|---|---|
| 1. Bike meshes and riding clips | ~30 min the first time, or none if you were given them | Bethesda Archive Extractor, Python + PyNifly |
| 2. Compiled scripts | none if you were given them, else 1 min | the shared `.pex` files, or `compile_scripts.bat` (Creation Kit) |
| 3. Install the mod | 2 min | copy, or zip for your mod manager |
| 4. Rider-pose plugin + animation data | 1 min | `make_rider_pose.bat` |
| 5. Test | 15 min | [TESTING.md](TESTING.md) |

## What you need

- Fallout 4 on PC, any current version (the plugins are ESL-flagged, which needs 1.10 or later, i.e. any version since 2017).
- Python 3 (for step 4; with numpy and [PyNifly](https://github.com/BadDogSkyrim/PyNifly) 29.1+ for step 1).
- *Optional:* F4SE, for the dedicated hotkey, the weight-based side bag and putting slot-57 gear back on after a ride.
  MCM (Mod Configuration Menu, needs F4SE) for a settings menu.
- *Optional:* the Creation Kit (free on Steam), only to compile the scripts yourself.

## 1. Meshes and riding clips

Follow [ASSETS.md](ASSETS.md). You end up with:

```
Data\Meshes\CMB\CMB_BikeParked.nif   (unmodified copy of the vanilla motorcycle)
Data\Meshes\CMB\CMB_BikeWornRider.nif, CMB_BikeWornRiderF.nif   (same model, facing forward, hanging off the seated rider's COM)
Data\Meshes\CMB\CMB_BikeWorn.nif     (same model, facing forward, skinned to AnimObjectA on the ground)
Data\Meshes\CMB\CMB_Keys.nif         (optional: copy of a vanilla key)
Data\Meshes\Actors\Character\Animations\MT\CMB_Rider\   (riding clips + CMB_RiderClips.json + CMB_RiderSeat.json, with a Female subfolder)
```

## 1b. The slope plugin (optional, F4SE)

`Data\F4SE\Plugins\CMB_Slope.dll` (steeper slopes, the riding camera, the bike's tilt, the ground under the
player for parking) is built from `tools/f4se-slope/CMB_Slope.c` with MinGW-w64
(`tools/f4se-slope/build.sh`; on Debian/Ubuntu `apt-get install gcc-mingw-w64-x86-64`, on Windows MSYS2's
`mingw-w64-x86_64-gcc`). `tools/f4se-slope/test/run.sh` runs it under Wine against a stand-in for the game, and
`tools/f4se-slope/test/parked_tilt.py` checks the script's formula for tilting the parked bike. It's
for Fallout 4 1.11.240 with F4SE 0.7.9 only; a new game version needs the addresses at the top of the source updated
from F4SE's source for that version.

## 2. Compiled scripts

The scripts need to be compiled to `Data\Scripts\*.pex`. Two ways:

- **Without the Creation Kit:** `tools/syntax-check` compiles them with [Caprica](https://github.com/nikitalita/Caprica),
  an open-source Papyrus compiler that writes Fallout 4's script format:
  `CAPRICA=<Caprica> PEX_OUT=Data/Scripts tools/syntax-check/check.sh`. It compiles against declarations of the
  game's script API kept in `tools/syntax-check/stubs` (checked against the Creation Kit wiki and, for F4SE,
  F4SE 0.7.9's own `Actor.psc`). Prebuilt `.pex` files made this way may come with the meshes and clips.
- **With the Creation Kit:** double-click **`compile_scripts.bat`**. It finds Fallout 4 through the registry
  (or `set FO4=D:\path\to\Fallout 4` first), unzips the vanilla script sources the first time, and compiles the
  five core scripts. If F4SE's script sources are installed (in `Data\Scripts\Source`, `Source\F4SE` or
  `Source\User`; with MO2 run it from MO2 so it sees them), it also compiles the two optional F4SE scripts
  (hotkey, gear restore); otherwise it skips them, and the mod works without them.

## 3. Install the mod

**Mod manager (recommended):** zip the *contents* of the repository's `Data` folder (`CommonwealthMotorbike.esp`, `Scripts`, `Meshes`, `Sound`, `MCM`), install that zip like any other mod and enable `CommonwealthMotorbike.esp`.

**Manual:** copy the contents of `Data` into `<Fallout 4>\Data`, then enable the plugin (`plugins.txt` line `*CommonwealthMotorbike.esp`, or the in-game Mods menu).

Load order doesn't matter: the plugin doesn't edit any vanilla record.

## 4. Rider-pose plugin and animation data

With the mod installed (step 4 reads the riding clips' data from it):

- **Mod Organizer 2:** `make_rider_pose.bat "C:\path\to\MO2" <profile>` (the profile name defaults to `Default`).
  It writes a new mod, *Commonwealth Motorbike - Rider Pose*; refresh MO2, enable it and `CMB_RiderPose.esp`.
- **No mod manager:** double-click `make_rider_pose.bat`. It writes `CMB_RiderPose.esp` and `Meshes\AnimTextData`
  into the game's Data folder; enable the plugin.

It copies the player's animation entries from your load order (the Unofficial Patch's crippled-limb ones included)
and writes the animation data the game needs for them, which the Creation Kit would otherwise generate
([how it works](ASSETS.md#4-the-rider-pose-plugin-and-animation-data)). Run it again after adding, removing or
updating mods that add player animations. `CMB_RiderPose.esp` adds an additive race, the way the DLCs add animations,
so it doesn't conflict with HumanRace mods such as LooksMenu Customization Compendium, and its place in the load
order doesn't matter.

## 5. Test

[TESTING.md](TESTING.md). The keys arrive the first time you're **outdoors with a Pip-Boy**: right after leaving Vault 111 on a new game, or straight away on an existing save.

---

## The biped slot (read this if you wear modded bags, belts or holsters)

While riding, the worn bike occupies **biped slot 57**, and anything else you wear in slot 57 comes off for the ride.
With F4SE, `CMB_GearRestoreF4SE` remembers it and puts it back on when you get off. Without F4SE it stays in your
inventory, because vanilla Papyrus can't tell what was in a slot. Slot 57 was picked because
the usual candidate, 58, is used by Eli's Armour Compendium bags (Basic, Medic, Hipster) and some weapon display
pieces. Slot 60 is named "Pipboy" in the record format, so it was avoided.

To check your own setup: in FO4Edit, look for any armor or armor addon with *First Person Flags* `57 - Unnamed`.
If one of yours uses 57, change `BikeSlot` in `tools/esp-generator/Program.cs` and run `tools/build.sh` (the gear-restore script gets the new slot from there too).
Alternatively, edit *First Person Flags* on both `CMB_BikeRiderArmor` and `CMB_BikeRiderAA` in FO4Edit; they must match.

## For developers: regenerating the plugin

The plugin is generated by `tools/esp-generator` (C#, [Mutagen](https://github.com/Mutagen-Modding/Mutagen)). After changing a script's properties or a record:

```
tools/build.sh
```

This regenerates `Data/CommonwealthMotorbike.esp` and the MCM menu files (`Data/MCM/Config/CommonwealthMotorbike`, written from the same build so their form IDs match). It then checks that every property in the plugin exists in the matching script with a compatible type, and that every `Mandatory` property is filled. Finally it runs the Papyrus syntax check (`tools/syntax-check`). Needs the .NET 8 SDK. The output is deterministic, so an unchanged generator gives a byte-identical plugin.

`tools/build.sh` also writes `tools/rider/template/CMB_RiderPose.esp`, the skeleton `make_rider_plugin.py` fills in.

The vanilla form IDs the plugins use (PlayerRef, XMarker, HumanRace, HumanRaceSubGraphData, SpeedMult, CarryWeight, FallingDamageMod, Health, Pip-Boy, AnimArchetypePlayer) were checked against Mutagen's FormKey list generated from the real `Fallout4.esm`. The record layouts were also compared field by field with xEdit's Fallout 4 definitions.

## Appendix: building the plugin by hand in the Creation Kit

You only need this if the generated plugin turns out to have a problem and you'd rather rebuild it in the editor. Every EditorID starts with `CMB_`, and the values below mirror the generator.

1. **Globals** (Float): `CMB_SpeedPercent` 250, `CMB_CompanionMode` 0, `CMB_AllowCombat` 0, `CMB_ForceThirdPerson` 1, `CMB_UseRiderPose` 1, `CMB_CatchUpDistance` 2500, `CMB_BagCapacity` 60, `CMB_HotkeyCode` 48, `CMB_UseFuel` 1, `CMB_FuelDistance` 21000, `CMB_EngineVolume` 70, `CMB_FallDamageCut` 75, `CMB_DismountOnHit` 1, `CMB_BikeFollowsRider` 1, `CMB_KnockOffDamage` 10, `CMB_FreeFallDamage` 20, `CMB_RidingCameraDistance` 450, `CMB_MaxSlope` 45, `CMB_SlopeLive` 0 (must be 0x82A), `CMB_CameraLive` 0 (must be 0x82B), `CMB_TiltLive` 0 (must be 0x82C), `CMB_GroundNormalX`, `CMB_GroundNormalY`, `CMB_GroundNormalZ` 0 (must be 0x82D, 0x82E, 0x82F), `CMB_MaxTilt` 15, `CMB_ParkX`, `CMB_ParkY`, `CMB_ParkZ`, `CMB_ParkAngle`, `CMB_ParkUpX`, `CMB_ParkUpY`, `CMB_ParkUpZ` 0 (must be 0x831-0x837), `CMB_TrackSlope` 0 (must be 0x838), `CMB_TurnRadius` 180, `CMB_StandTurnRate` 60, `CMB_TurnRadiusSlow` 50 (must be 0x839, 0x83A, 0x83B). The fixed form IDs are where `CMB_Slope.dll` looks for them.
   **FormList** `CMB_FuelItems` containing Flamer Fuel (`AmmoFlamerFuel`, 000CAC78).
2. *(no keyword: `CMB_AnimFlavorRider` lives in `CMB_RiderPose.esp`)*
3. **Messages** (tick *Message Box*; button order matters):
   `CMB_ParkedMenu` "Motorbike" / "What do you want to do?" with buttons `Ride`, `Open side bag`, `Cancel`.
   `CMB_KeysMenu` "Motorbike" / "Your motorbike isn't nearby." with buttons `Call it here`, `Open side bag`, `Cancel`.
4. **Armor Addon** `CMB_BikeRiderAA`: race HumanRace, biped slot 57, male model `CMB\CMB_BikeWornRider.nif`, female model `CMB\CMB_BikeWornRiderF.nif`.
   **Armor** `CMB_BikeRiderArmor`: name "Motorbike", *Non-Playable*, slot 57, race HumanRace, addon `CMB_BikeRiderAA`, everything else 0.
   The same pair again as `CMB_BikeRiderFrameAA` (male+female model `CMB\CMB_BikeWorn.nif`) and `CMB_BikeRiderArmorFrame`.
5. **Magic Effect** `CMB_BikeKeysEffect`: archetype Script, Fire and Forget, Self, casting sound level Silent.
   Flags: No Duration, No Magnitude, No Area, Hide in UI, Painless. Script: `CMB_KeysEffectScript`.
   **Potion** `CMB_BikeKeys`: name "Motorbike Keys", model `CMB\CMB_Keys.nif`, weight 0, value 0, No Auto Calc, effect `CMB_BikeKeysEffect` (0/0/0).
   **Magic Effect** `CMB_SwimWatchEffect`: archetype Script, Constant Effect, Self, casting sound level Silent, the same flags plus No Hit Event. Script: `CMB_SwimWatchEffectScript`.
   **Magic Effect** `CMB_WadeWatchEffect`: the same, with the script's `Wading` property ticked.
   **Spell** `CMB_SwimWatchAbility`: type Ability, Constant Effect, Self, two effects (0/0/0): `CMB_SwimWatchEffect` with the condition `IsSwimming == 1` and `CMB_WadeWatchEffect` with `IsInWater == 1` (both Subject).
6. **Activator** `CMB_BikeActivator`: name "Motorbike", activate text "Use", model `CMB\CMB_BikeParked.nif`, script `CMB_BikeActivatorScript`.
   **Container** `CMB_SideBagContainer`: name "Side Bag", model `CMB\CMB_BikeParked.nif`, script `CMB_SideBagScript`.
7. **Interior cell** `CMB_HoldingCell` holding four *persistent* references: `CMB_BikeRef` (the activator), `CMB_SideBagRef` (the container), `CMB_HoldingMarkerRef` (an XMarker) and `CMB_GroundProbeRef` (an XMarker that feels for the navmesh around the parked bike; once the unused `CMB_DrySpotMarkerRef`, same record).
8. **Quest** `CMB_ControllerQuest`: *Start Game Enabled*, priority 50.
   - Reference alias `Player` (Specific Reference: PlayerRef) with script `CMB_PlayerAliasScript`.
   - Scripts `CMB_ControllerScript` and, optionally (F4SE), `CMB_HotkeyF4SE` and `CMB_GearRestoreF4SE`.
9. **Properties:** fill every *Mandatory* property ("Auto-Fill All" gets the vanilla ones). Script-typed properties called `Controller` point at `CMB_ControllerQuest`. `Pipboy` is the vanilla Pip-Boy armor (00021B3B), `FallingDamageMod` and `Health` the vanilla actor values (000BA43D, 000002D4).
