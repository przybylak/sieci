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
`tools/f4se-slope/test/parked_tilt.py` checks the script's formula for tilting the parked bike (since the 2026-11-09a
build 26 modes, the new one 25 `caution`: `bash tools/f4se-slope/test/run.sh caution`). It's
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
  nine core scripts (`CMB_StaggerWatchEffectScript` since 2026-11-01a). If F4SE's script sources are installed (in `Data\Scripts\Source`, `Source\F4SE` or
  `Source\User`; with MO2 run it from MO2 so it sees them), it also compiles the optional F4SE scripts (hotkey, gear
  restore and, since 2026-11-07a, `CMB_LookF4SE`, the customised look's material swap on the parked and first-person
  bikes: 12 `.pex` in all, as `check.sh` makes); otherwise it skips them, and the mod works without them (the bike's
  look then stays stock on those two bikes).

## 3. Install the mod

**Mod manager (recommended):** zip the *contents* of the repository's `Data` folder (`CommonwealthMotorbike.esp`, `Scripts`, `Meshes`, `Sound`, `MCM`), install that zip like any other mod and enable `CommonwealthMotorbike.esp`.

**Manual:** copy the contents of `Data` into `<Fallout 4>\Data`, then enable the plugin (`plugins.txt` line `*CommonwealthMotorbike.esp`, or the in-game Mods menu).

Load order doesn't matter: the plugin doesn't edit any vanilla record.

**The engine sound:** the repository's `Data\Sound\FX\CMB` has only the synthesised fallback four (`CMB_EngineIdleLP`,
`CMB_EngineCruiseLP`, `CMB_EngineStart`, `CMB_EngineStop`). The package's 13 files replace those four with recorded
ones and add the nine loops the F4SE plugin drives; they are built from demodave's recording (Freesound 502690, CC0,
not in the repository) by `sh tools/sound/run_all.sh <its WAV> <out dir>` (Python 3 and numpy, about 8 minutes):
put `<out dir>\loops\*.wav` in the zip's (or the installed mod's) `Sound\FX\CMB`, over the four, not in the
repository's. Without them the nine loops have no files, so with `CMB_Slope.dll` the plugin gets no full set
([DESIGN.md](DESIGN.md), *The engine sound*): set `[Sound] Drive=0` in `CMB_Slope.ini`, and the engine is the script's
crossfade of the four, as without the plugin.

**The water loops:** the two wet roads are built from the tester's example 1 ("Cars driving on a wet road 3", Pixabay
101246, decoded to a WAV; neither it nor the loops are in the repository): `python3 -I -B
tools/sound/make_water_loop.py --ex1 ex1.wav --out <dir>` writes `CMB_FxWaterRoadLP.wav` (the 2026-11-06a build's,
byte for byte) and, since the 2026-11-09a build, `... --variant gentle ...` the gentle one, `CMB_FxWaterRoadSoftLP.wav`
(`WATER=ex1.wav sh tools/sound/run_all.sh <WAV> <out dir>` builds both into `loops/`). Both go beside the engine's 13 in
the package's `Data\Sound\FX\CMB\` (15 WAVs; its `water.json` and `water_gentle.json` aren't shipped). Since that build
`python3 -I -B tools/sound/engine_model.py --check-off` checks four builds' off values (the 2026-11-06a build's model
added).

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

The customisation's records (since 2026-11-07a: 347, CMB_LookCode at 0x8AF and 0x8BA-0xA13) come from
`tools/esp-generator/look_options.json`, built into the generator: the one table of the slots, options, badges, paint
rows and faction sets, which the meshes' and badges' tools, `check_plugin.py` and `look_render.py` read too. Options
keep their index and their records' IDs; a later build only appends. After adding options there, run `dotnet
tools/esp-generator/bin/out/EspGenerator.dll --look-ids tools/esp-generator/look_ids.txt` and commit `look_ids.txt`: it
only appends (it refuses to change or drop a line), and `check_plugin.py` fails when the plugin doesn't match it.
In the 2026-11-07a build `tools/build.sh`'s plugin check printed `checked 102 look options in 5 slots: 101 swaps, 102
recipes on CMB_WorkbenchBike, 3 loose mods, sources unique per slot, CMB_LookCode 0008AF, highest 000A13; look_ids.txt
347 IDs; the MCM's Look section 11 controls`, `checked cmb_controllerscript: 174 properties` and `checked cmb_lookf4se:
10 properties`, and the ESP held 562 in its header's count (208 + 347 records and the 7 new groups), its next ID 0xA14.

Since 2026-11-08a (the second customisation build) the table also holds six new slots and Paint's 46th option, and the
generator makes their 477 records as a second block after the first build's, at 0xA14-0xBF0 (the four colour values at
the fixed 0xA14-0xA17, then the hue, the shade, the crude switch, the slots' globals and attach points, the options and
their lists: `look_ids.txt` 824 IDs). `tools/build.sh` prints `checked 263 look options in 11 slots: 227 swaps, 263
recipes on CMB_WorkbenchBike, 3 loose mods, 14 crude behind CMB_LookPlateCrude, sources unique per slot, CMB_LookCode
0008AF, colours 000A14-000A17, highest 000BF0; look_ids.txt 824 IDs; the MCM's Look section 20 controls`, `checked
cmb_controllerscript: 187 properties` and `checked cmb_lookf4se: 31 properties`; the ESP holds 1039 in its header's
count (562 + 477, no new group), its next ID 0xBF1. `dotnet tools/esp-generator/bin/out/EspGenerator.dll --look-build
2026-11-07a <folder>/CommonwealthMotorbike.esp` makes the 2026-11-07a build's ESP (and its MCM `config.json` and
`keybinds.json` in `<folder>/MCM/Config/CommonwealthMotorbike/`) byte for byte: every `look_options.json` entry
`"since": "2026-11-08a"` dropped; any build name but 2026-11-07a and 2026-11-08a is refused. The customisation's
meshes, badges, paint, rims, tyres and plates are built by `tools/rider` ([ASSETS.md](ASSETS.md), *The
customisation's files* and *The second customisation build's files*: `harley_meshes.py --look-rims 1 --look-plate 1`,
the defaults, then `look_shapes.py`, `look_wheels.py`, `bike_art.py --plates` and `look_plates.py`).

Since 2026-11-09a (test 50's fixes) the generator makes three records more, right after the second block and only
with it: `CMB_Caution` 0xBF1 (60), `CMB_ViewMenu` 0xBF2 (0) and `CMB_FxWaterRoadSoftLPSD` 0xBF3 (the gentle wet road);
it throws unless they land there, and `CMB_FxWaterLoop` (0x8B4) is 3 (2 under `--look-build 2026-11-07a`, which still
makes that build's ESP and MCM files byte for byte). `tools/build.sh` prints `checked cmb_controllerscript: 189
properties`, `checked 14 effect sounds: output model CMB_SOMMonoFx (00089D), static 0, 12 the game's files by path and
2 the mod's own (CMB_FxWaterRoadLPSD, CMB_FxWaterRoadSoftLPSD)` and `... highest 000BF3; look_ids.txt 827 IDs; the
MCM's Look section 20 controls`, and "plugin and scripts agree"; the ESP holds **1042** in its header's count, its next
ID **0xBF4** (780 IDs left under the 0xF00 guard). The MCM's `config.json` gains Riding's "Caution (how early the bike
eases off for obstacles, %)" and the "Water sound loop" stepper's fourth option, "Wet road, gentle". Test 50's fixes
change no asset.

Since test 51's fixes (the same build) the generator makes one record more, right after those three and only with them:
`CMB_LookOptions` 0xBF4 (63; it throws unless it lands there), and the 263 look recipes carry no BNAM (as the game's
armour mod recipes; `--look-build 2026-11-07a` keeps that build's, with it). `dotnet
tools/esp-generator/bin/out/EspGenerator.dll --recipe-bench CMB_WorkbenchBike <output.esp>` makes an A/B plugin whose
263 look recipes carry BNAM `CMB_WorkbenchBike` as 2026-11-08a's (never shipped). `tools/build.sh` prints `checked
cmb_controllerscript: 191 properties`, `checked cmb_lookf4se: 33 properties` and `checked 263 look options in 11 slots:
227 swaps, 263 look recipes, no BNAM (as the game's armour mod recipes), 3 loose mods, 14 crude behind
CMB_LookPlateCrude, sources unique per slot, CMB_LookCode 0008AF, colours 000A14-000A17, highest 000BF4; look_ids.txt
828 IDs; the MCM's Look section 20 controls`; the ESP holds **1043** in its header's count, its next ID **0xBF5** (779
IDs left under the 0xF00 guard). The MCM's "Field kit" gains a fifth option, "The game's armour bench", and the "Paint
hue" and "Paint shade" helps end `Moving it chooses Paint "Free colour" when you Apply (or at the next getting on).`
`check.sh` prints no warning (12 .pex).

Test 51's fixes change three textures, the Vault-Tec plate's (`plates_d.dds`, `plates_n.dds`, `plates_s.dds`; the
meshes and materials are the 2026-11-08a build's). From the repository, with the DDS tools' Python
([ASSETS.md](ASSETS.md)):
```
cp -a <2026-11-08a's asset tree> <tree>
python3 -I tools/rider/bike_art.py --plates --out <art folder>             # the 12 designs, the Vault-Tec cog redrawn
<DDS python> -I tools/rider/look_plates.py --art <art folder> --out <tree> \
    --old-stage <2026-11-07a's stage> --stage <2026-11-08a's stage>
<DDS python> -I tools/rider/look_plates.py --check ...  (same arguments)   # 23 checks, all passed
<DDS python> -I tools/rider/look_plates.py --sheet <folder> ...            # the contact sheets
```
Only `plates_d.dds`, `plates_n.dds` and `plates_s.dds` differ from 2026-11-08a's tree (sha256 b5eacce3...,
78b75210..., 8892936a...); the package's verifier checks those three and everything else as 2026-11-08a's.

The vanilla form IDs the plugins use (PlayerRef, XMarker, HumanRace, HumanRaceSubGraphData, SpeedMult, CarryWeight, FallingDamageMod, Health, Pip-Boy, AnimArchetypePlayer) were checked against Mutagen's FormKey list generated from the real `Fallout4.esm`. The record layouts were also compared field by field with xEdit's Fallout 4 definitions.

## Appendix: building the plugin by hand in the Creation Kit

You only need this if the generated plugin turns out to have a problem and you'd rather rebuild it in the editor. Every EditorID starts with `CMB_`, and the values below mirror the generator.

1. **Globals** (Float): `CMB_SpeedPercent` 250, `CMB_CompanionMode` 0, `CMB_AllowCombat` 0, `CMB_ForceThirdPerson` 1, `CMB_UseRiderPose` 1, `CMB_CatchUpDistance` 2500, `CMB_BagCapacity` 60, `CMB_HotkeyCode` 48, `CMB_UseFuel` 1, `CMB_FuelDistance` 21000, `CMB_EngineVolume` 90, `CMB_FallDamageCut` 75, `CMB_DismountOnHit` 1, `CMB_BikeFollowsRider` 1, `CMB_KnockOffDamage` 10, `CMB_FreeFallDamage` 20, `CMB_RidingCameraDistance` 450, `CMB_MaxSlope` 45, `CMB_SlopeLive` 0 (must be 0x82A), `CMB_CameraLive` 0 (must be 0x82B), `CMB_TiltLive` 0 (must be 0x82C), `CMB_GroundNormalX`, `CMB_GroundNormalY`, `CMB_GroundNormalZ` 0 (must be 0x82D, 0x82E, 0x82F), `CMB_MaxTilt` 45, `CMB_ParkX`, `CMB_ParkY`, `CMB_ParkZ`, `CMB_ParkAngle`, `CMB_ParkUpX`, `CMB_ParkUpY`, `CMB_ParkUpZ` 0 (must be 0x831-0x837), `CMB_TrackSlope` 0 (must be 0x838), `CMB_TurnRadius` 180, `CMB_StandTurnRate` 60, `CMB_TurnRadiusSlow` 50 (must be 0x839, 0x83A, 0x83B). The fixed form IDs are where `CMB_Slope.dll` looks for them.
   **FormList** `CMB_FuelItems` containing Flamer Fuel (`AmmoFlamerFuel`, 000CAC78).
   Since 2026-11-01a (the generator lists every later form; these are this round's): `CMB_TailRefHi`, `CMB_TailRefLo`,
   `CMB_ViewRefHi`, `CMB_ViewRefLo`, `CMB_RoomAskKind`, `CMB_RiderPoseOff` 0 and `CMB_BrakeKey` 57 (must be 0x872-0x878);
   `CMB_RamKills` 1, `CMB_TailLightMode` 1, `CMB_FirstPersonBike` 1, `CMB_RiderSteady` 1, `CMB_PoseReactionWindow` 3,
   `CMB_PoseOffAfter` 3; `CMB_FxVolume` 90, `CMB_FxWaterId`, `CMB_FxDriven`, `CMB_FxAir`, `CMB_FxLandSeq` 0,
   `CMB_FxLandLevel` -1, `CMB_FxLandPlayed` 0 (must be 0x884-0x88A); `CMB_FxMuteRider`, `CMB_FxLandOn`, `CMB_FxWaterOn` 1,
   `CMB_FxLandPick`, `CMB_FxWaterPick` 0. **FormLists** of the game's own sound descriptors: `CMB_FxLandSounds` (1D3313,
   1D3312, 05BAD7, 03C7A9, 0452CE), `CMB_FxLandSoundsAlt` (1D3313, 20A0B9, 1A8550, 089380, 20A0B8), `CMB_FxWaterLoops`
   (1E4F2D, 1E4F2C, 03D0A7, 1E4F1B). **Light** `CMB_TailLight` (radius 220, colour 255/24/10, Dynamic and Non-Shadow
   Spotlight, FOV 120, fade 0.75) and **Movable Static** `CMB_BikeView` (model `CMB\CMB_BikeView.nif`).
   Since 2026-11-02a (28 records, 0x893-0x8AE; the ESP then holds 198 records, its next ID 0x8AF): `CMB_RiderItemUse` 0,
   `CMB_RamCombat` 0 and `CMB_FxLandRange` 10 (must be 0x893-0x895: the plugin looks for them); `CMB_RiderSteadyWay` 1,
   `CMB_PoseUseWindow` 6, `CMB_UseCameraFix` 1, `CMB_RamKillXP` 1 and `CMB_FxOwnSounds` 1. **Sound Output Model**
   `CMB_SOMMonoFx`: `CMB_SOMMonoEngine`'s values exactly (Attenuates With Distance, Uses HRTF, reverb send 5, static
   attenuation 0, fade-in 0-0 with the curve 0/50/80/95, fade-out 600-4000 with 50/20/5/0). **Sound Descriptors**, 13,
   each a standard descriptor in `AudioCategorySFX` (0172A1) on `CMB_SOMMonoFx`, priority 128, static attenuation 0, no
   conditions, with the files, pitch and loudness variation of the game's record it follows (docs/ASSETS.md, "The game's
   sound files our own records name by path"): `CMB_FxTyreLightSD`, `CMB_FxTyreHeavySD`, `CMB_FxClunkSD`,
   `CMB_FxSplashSD`, `CMB_FxSplashHeavySD`, `CMB_FxThudHeavySD`, `CMB_FxClunkBarrelSD`, `CMB_FxSplashMediumSD`,
   `CMB_FxThudWaterSD`, and the four loops (Loop) `CMB_FxWaterSprayLPSD` (pitch +15), `CMB_FxWaterSprayLargeLPSD`
   (pitch -15), `CMB_FxWaterStreamLPSD`, `CMB_FxWaterChurnLPSD`. **FormLists** of them in the borrowed lists' slots:
   `CMB_FxLandSoundsOwn` (TyreLight, TyreHeavy, Clunk, Splash, SplashHeavy), `CMB_FxLandSoundsAltOwn` (TyreLight,
   ThudHeavy, ClunkBarrel, SplashMedium, ThudWater), `CMB_FxWaterLoopsOwn` (WaterSpray, WaterSprayLarge, WaterStream,
   WaterChurn). No form ID may be over 0xF00 (the light plugin's range, the rest kept for the customisation builds).
   Since 2026-11-06a (10 records, 0x8B0-0x8B9; the ESP then holds 208 records, its next ID 0x8BA; **0x8AF is left
   unmade**, kept for the customisation build's `CMB_LookCode`, and the generator throws if any form takes it):
   **Globals** (float) `CMB_ViewTip` 20, `CMB_ViewFov` 0, `CMB_ViewEyeForward` 0, `CMB_ViewEyeUp` 0 and
   `CMB_FxWaterLoop` 2 (must be 0x8B0-0x8B4, all five: the plugin looks for them), `CMB_KnockOffPower` 0,
   `CMB_RiderUseOwn` 1, `CMB_FxLandDull` 1 and `CMB_FxThudDb` -11; the **FormList** `CMB_FxLandSoundsDull`
   (`CMB_FxTyreLightSD`, `CMB_FxTyreHeavySD`, `CMB_FxThudHeavySD`, `CMB_FxSplashSD`, `CMB_FxSplashHeavySD`,
   `CMB_FxThudWaterSD`). **Three changed in place**: `CMB_FxSplashSD` names
   `Data\Sound\FX\FST\Player\Water\FST_Water_Jump_Down_01.wav` and `_02.wav`; `CMB_FxSplashHeavySD` names
   `Data\Sound\FX\PHY\Generic\PHY_Generic_Water_Medium_01.wav`, `_02.wav` and `_03.wav` (its variation as before);
   0x8A9 is renamed `CMB_FxWaterRoadLPSD` and names one file, `FX\CMB\CMB_FxWaterRoadLP.wav` (Loop, no pitch or loudness
   variation), the mod's own (docs/ASSETS.md).
2. *(no keyword: `CMB_AnimFlavorRider` lives in `CMB_RiderPose.esp`)*
3. **Messages** (tick *Message Box*; button order matters):
   `CMB_ParkedMenu` "Motorbike" / "What do you want to do?" with buttons `Ride`, `Open side bag`, `Cancel` (since
   2026-11-07a `Ride`, `Open side bag`, `Customise`, `Cancel`, the third with the condition `GetGlobalValue CMB_LookOn
   == 1`: the script reads 0 ride, 1 bag, 2 customise, 3 cancel).
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
   **Magic Effect** `CMB_StaggerWatchEffect` (since 2026-11-01a): as `CMB_SwimWatchEffect`, script `CMB_StaggerWatchEffectScript`; **Spell** `CMB_StaggerWatchAbility`: Ability, Constant Effect, Self, that effect with `IsStaggered == 1` (Subject).
   **Perk** `CMB_RiderSteadyPerk` "Steady in the saddle": not playable, hidden, one rank; one entry point Mod Incoming Stagger, Multiply 0, no conditions (the controller adds and removes it).
   **Perk** `CMB_RiderSteadyPerk2` (since 2026-11-02a) "Steady in the saddle": the same, but the entry's condition tabs 2 and its entry point function 0 (EPFB 0000), as the game's own `mod_armor_LessStagger`; the controller gives it with `CMB_RiderSteadyWay` 1 (2 gives the game's 00245AFE, 0 `CMB_RiderSteadyPerk`).
   **Magic Effect** `CMB_RamKillEffect` (since 2026-11-02a): archetype Value Modifier, actor value Health (000002D4), Fire and Forget, Target Actor; flags Hostile, Detrimental, Painless, No Hit Effect, No Duration, No Area, Hide in UI (not No Hit Event); no art, no sounds. **Spell** `CMB_RamKillSpell` "Motorbike knock-over": type Spell, Fire and Forget, Target Actor, Manual Cost Calc, Ignore Resistance, No Absorb/Reflect, cost 0; one effect, `CMB_RamKillEffect`, magnitude 100000, area 0, duration 0 (`CMB_RamScript` casts it from the player for the killing hit).
6. **Activator** `CMB_BikeActivator`: name "Motorbike", activate text "Use", model `CMB\CMB_BikeParked.nif`, script `CMB_BikeActivatorScript`.
   **Container** `CMB_SideBagContainer`: name "Side Bag", model `CMB\CMB_BikeParked.nif`, script `CMB_SideBagScript`.
7. **Interior cell** `CMB_HoldingCell` holding four *persistent* references: `CMB_BikeRef` (the activator), `CMB_SideBagRef` (the container), `CMB_HoldingMarkerRef` (an XMarker) and `CMB_GroundProbeRef` (an XMarker that feels for the navmesh around the parked bike; once the unused `CMB_DrySpotMarkerRef`, same record).
8. **Quest** `CMB_ControllerQuest`: *Start Game Enabled*, priority 50.
   - Reference alias `Player` (Specific Reference: PlayerRef) with script `CMB_PlayerAliasScript`.
   - Scripts `CMB_ControllerScript` and, optionally (F4SE), `CMB_HotkeyF4SE` and `CMB_GearRestoreF4SE`, then
     `CMB_RamScript` and, since 2026-11-07a, `CMB_LookF4SE` (F4SE; the quest's five in that order).
   - Since 2026-11-02a the controller's three new groups (`Rider_Pose_Fixes`, `Ram_Fixes`, `Fx_Own_Records`: 11
     properties, 138 in all) and `CMB_RamScript`'s `Kill_Experience` (`CMB_RamKillSpell`, `CMB_RamKillXP`: 17 in all)
     are filled with the records of the same names.
   - Since 2026-11-06a two more groups (`Rider_Fixes_51`: `CMB_KnockOffPower`, `CMB_RiderUseOwn`; `Fx_Fixes_51`:
     `CMB_FxLandDull`, `CMB_FxThudDb`, `CMB_FxLandSoundsDull`, `CMB_FxWaterLoop`, and `CMB_FxWaterRoad` =
     `CMB_FxWaterRoadLPSD`: 7 properties, 145 in all), none Mandatory.
   - Since 2026-11-07a the group `Look_C1` (29 properties, 174 in all: the look's globals, lists, keywords, the kit's
     furnitures, the controller's five arrays `LookSetPaint`, `LookSetTank`, `LookSetFender` (12 entries, [0] = -1),
     `LookKeys` (102 "Slot:key"), `LookSlotStart` (0, 17, 35, 53, 98)) and `CMB_LookF4SE`'s 10, none Mandatory. The
     customisation's 347 records are the generator's (`LookRecords`, from `look_options.json`); by hand they are too
     many to list here: `dotnet tools/esp-generator/bin/out/EspGenerator.dll --dump Data/CommonwealthMotorbike.esp`
     prints each.
   - Since 2026-11-08a the group `Look_C2` (13 properties, 187 in all: the six new slots' globals `CMB_Look_Rims`,
     `CMB_Look_Tyres`, `CMB_Look_Plate`, `CMB_Look_PlateText`, `CMB_Look_PlateInk`, `CMB_Look_PlateBack`, then
     `CMB_LookHue`, `CMB_LookShade`, `CMB_LookPlateCrude` and the arrays `LookRimStyle` (48), `LookTextCrude` (62),
     `LookPlateOwnText` (13) and `LookSetPlate` (12)) and `CMB_LookF4SE`'s 21 more (31: the same nine globals, the four
     colour values `CMB_LookPaintV` to `CMB_LookPlateTextV`, the arrays `PaintRow`, `RimBody`, `TextCrude`,
     `PlateOwnText`, `PlateOwnInk`, `PlateOwnBack` and the string arrays `RimBodyTargets`, `RimBodyHueTargets`), none
     Mandatory; `LookKeys` now 263 ("Paint:free" after "Paint:test", so `LookSlotStart` is 0, 17, 35, 53, 99, 103, 151,
     154, 167, 229, 246). The 477 records are the generator's (`BuildC2`), `--dump` prints them (1009 records).
   - Since 2026-11-09a the group `Fixes_54` (2 properties, 189 in all: `CMB_ViewMenu` and the sound
     `CMB_FxWaterRoadSoft`, none Mandatory; `CMB_Caution` has no property: no script reads it).
   - Since test 51's fixes (2026-11-09a) the group `Fixes_55` (2 properties, 191 in all: `CMB_LookOptions` and
     `WorkbenchArmorA`, Fallout4.esm 0x12EA9B, the field kit's mode 4), and `CMB_LookF4SE`'s `Fixes_55` (33:
     `CMB_LookOptions` and the float array `RimFinishV`, 48 values), none Mandatory.
   - The MCM's seven new controls (Riding: the four first-person sliders and "Power attacks throw you off"; Sound:
     "Landing sounds without metal" and the "Water sound loop" stepper) are in `config.json`, written by the generator.
9. **Properties:** fill every *Mandatory* property ("Auto-Fill All" gets the vanilla ones). Script-typed properties called `Controller` point at `CMB_ControllerQuest`. `Pipboy` is the vanilla Pip-Boy armor (00021B3B), `FallingDamageMod` and `Health` the vanilla actor values (000BA43D, 000002D4).
