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

Since 2026-11-10a (test 52's fixes) the generator makes two records more, right after `CMB_LookOptions` and only with
the look: `CMB_RiderQuickUse` 0xBF5 and `CMB_RideReady` 0xBF6, float globals at 0 (it throws unless they land there:
`CMB_Slope.dll` looks for them by ID), filled into the controller's group `Fixes_56`; `CMB_LookOptions` is 4031 (the five
new bits on) and `CMB_Caution` 50. `--look-ids` appends `CMB_RiderQuickUse 000BF5` and `CMB_RideReady 000BF6`.
`tools/build.sh` prints `checked cmb_controllerscript: 193 properties`, `checked cmb_lookf4se: 33 properties` and
`checked 263 look options in 11 slots: ... highest 000BF6; look_ids.txt 830 IDs; the MCM's Look section 20 controls`,
and "plugin and scripts agree"; the ESP holds **1045** in its header's count (no new group), its next ID **0xBF7** (777
IDs left under the 0xF00 guard). The MCM's Riding "Caution" help begins "50, the default:"; nothing else in
`config.json` or `keybinds.json` changes. `--look-build 2026-11-07a` still writes the 2026-11-07a build's ESP,
`config.json` and `keybinds.json` byte for byte. `check.sh` prints no warning (12 .pex); `CMB_HotkeyF4SE`'s two new
constants are AutoReadOnly (no fill), as are the field kit's.

Test 52's fixes change the four worn and view nifs and 76 materials files: the front end's shadow
([ASSETS.md](ASSETS.md), *The front end's shadow*). From the repository, `<tree>` a copy of 2026-11-09a's, with the DDS
tools' Python and Blender's:
```
cp -a <2026-11-09a's asset tree> <tree>
python3 -I tools/rider/harley_meshes.py --pynifly <PyNifly> --gltf <scene.gltf> --vanilla <motorcycle_clean.nif> \
    --out <tree>/Meshes/CMB --textures <tree>/Textures/CMB --seat <CMB_Rider clips> --disc-bore shared \
    --stage build --stage-dir <2026-11-08a's stage> --materials tools/rider/bike_materials.json   # the five nifs (four change)
<Blender python> -I tools/rider/bike_textures.py --stage-dir <2026-11-06a's 30-shape stage with the tex cache> \
    --gltf <scene.gltf> --materials tools/rider/bike_materials.json --art <its art> --out <tree> \
    --dds-python <DDS python> --only front_chrome,front_black,front_glass,front_glow,front_dial,front_dialglow,\
front_needle,front_mirrorStock,front_mirrorUnderEgg,front_mirrorUnderD,fork_chrome,fork_paint,fork_black,fork_glass,\
wheelF_tyre,wheelF_rim,wheelF_disc                       # the 33 front materials files; textures up to date, no bake
<base06n> = 2026-11-06a's Data with its front_*, fork_*, wheelF_* _worn.bgsm taken from <tree> (17 files)
<DDS python> -I tools/rider/look_paint.py --data <tree> --base <base06n> --stage <2026-11-07a's stage>   # then --check
<base07n> = 2026-11-07a's Data with its front_*, fork_*, wheelF_* _worn.bgsm taken from <tree> (61 files)
<DDS python> -I tools/rider/look_wheels.py --data <tree> --base <base07n> --stage <2026-11-07a's stage> \
    --rim-stage <2026-11-08a's stage>                                                              # then --check
python3 -I tools/rider/check_bike_meshes.py --pynifly <PyNifly> --data <tree> --reference <an earlier build's Meshes/CMB> \
    --stage-dir <2026-11-08a's stage> --look-reference <2026-11-06a's Data> --c2-reference <2026-11-07a's Data> \
    --look-c2 --look-targets all                                                                  # 83 checks, all passed
```
The texture stage is 2026-11-06a's 30-shape stage (its manifest, shapes and UVs) with the texture cache: on a later stage
the bake keys, which hold every shape's hash, would miss and re-bake. `look_paint.py --check` gives 11 PASS and
`look_wheels.py --check` 21 over those bases. Only the four nifs and the 76 materials files differ from 2026-11-09a's
tree (557 files), each in its cast-shadow bit or byte alone; a second build is byte for byte the first. The package's
verifier checks those 80 by sha256 and everything else as 2026-11-09a's.

The gentle wet-road loop is rebuilt 3 dB louder (never in git; the package takes it from the build's output folder),
and the engine model's checks gain a fifth build and a menu ride:
```
python3 -I -B tools/sound/make_water_loop.py --variant gentle --ex1 <ex1.wav> --out <out>/Sound/FX/CMB
        # CMB_FxWaterRoadSoftLP.wav (A -23.5 dBFS; sha256 edfb5ad6...0eb5) and water_gentle.json
python3 -I -B tools/sound/make_water_loop.py --variant gentle --measure <out>/Sound/FX/CMB/CMB_FxWaterRoadSoftLP.wav
        # exit 0 (2026-11-09a's loop: exit 1, its level)
python3 -I tools/sound/engine_model.py --check-off      # five builds (31a, 01a, 02a, 06a, 09a), 44136 frames each
python3 -I tools/sound/engine_model.py --check-menu     # MenuHold through a menu, and not with MenuHold=0
```
The loop is repeatable byte for byte, and 1712b81's tool still makes 2026-11-09a's loop byte for byte (the wet road's,
`CMB_FxWaterRoadLP.wav`, is unchanged). `check_off_2026-11-09a.txt` is written from 1712b81's model (`git show
1712b81:tools/sound/engine_model.py > old.py`, then `--write-expected old.py --off 09a`).

Since 2026-11-14a (test 53's fixes) the generator makes eight records more, right after `CMB_RideReady` and only with
the look: `CMB_KitWhere` 0xBF7 (1) and the field kit preview's seven, `CMB_KitPreview` 0xBF8 (1), `CMB_KitPrevSize`
0xBF9 (30), `CMB_KitPrevTurn` 0xBFA (7), `CMB_KitPrevTilt` 0xBFB (0), `CMB_KitPrevUp` 0xBFC (0), `CMB_KitPrevZoomOut`
0xBFD (-1) and `CMB_KitPrevZoomIn` 0xBFE (1), float globals (it throws unless they land there: `CMB_Slope.dll` looks for
the seven by ID), `CMB_KitWhere` filled into the controller's group `Fixes_57`. The look item's object template is named
"Motorbike" and every look mod "<slot label>: <option>" (`look_options.json`'s new `label` per slot). `--look-ids`
appends the eight (838 IDs). `tools/build.sh` prints `checked cmb_controllerscript: 194 properties`, `... names on: the
item's template 'Motorbike', 263 mods named <slot label>: <option>; the MCM's Look section 21 controls` and "plugin and
scripts agree"; the ESP holds **1053** in its header's count (no new group), its next ID **0xBFF** (769 IDs left under
the 0xF00 guard). The MCM's `config.json` gains Look's "Field kit only in your settlements" and a section "Field kit
preview" (a stepper and six sliders), the side bag's help a clause, and loses Riding's "Field of view riding in first
person"; `keybinds.json` doesn't change. `dotnet tools/esp-generator/bin/out/EspGenerator.dll --kit-names 0
<folder>/CommonwealthMotorbike.esp` makes an A/B plugin with 2026-11-10a's names ("Default" and the bare option names;
not shipped), which `check_plugin.py ... --kit-names 0` checks; `--look-build 2026-11-07a` still writes the 2026-11-07a
build's ESP, `config.json` and `keybinds.json` byte for byte, with or without `--kit-names 0`. `check.sh` prints no
warning (12 .pex); the F4SE stub `ScriptObject.psc` gains `RegisterForRemoteEvent` and `UnregisterForRemoteEvent`, as
F4SE 0.7.9's own (`audit_stubs.py`: 0 problems). Test 53's fixes change no asset: the meshes, textures, materials,
sounds and clips are 2026-11-10a's. `python3 -I tools/sound/engine_model.py --check-off` checks six builds (the new
`check_off_2026-11-10a.txt` is written from c716330's model: `git show c716330:tools/sound/engine_model.py > old.py`,
then `--write-expected old.py --off 10a`) and `--check-climb` the five gears.

Since 2026-11-15a (test 54's fixes) the generator makes no new record: the ESP keeps **1053** in its header's count and
its next ID **0xBFF**, look_ids.txt its 838 IDs. Two globals' values change, `CMB_KitPrevSize` 0xBF9 30 -> **400** and
`CMB_KitPrevZoomIn` 0xBFE 1 -> **3** (Tune now starts at New's preview), and in `config.json` the "Field kit preview"
section's first slider is "Preview distance" (100-2000, step 25, on the same global) where it was "Preview size (%)"
(10-200, step 5), with the stepper's and "Preview zoom in"'s helps; `keybinds.json` doesn't change. A record-by-record
comparison with 2026-11-14a's plugin: `TES4: same`, `added 0`, `removed 0`, `changed 2` (the two FLTV). `tools/build.sh`
prints `checked cmb_controllerscript: 194 properties` and "plugin and scripts agree" as before; `--look-build
2026-11-07a` still writes the 2026-11-07a build's three files byte for byte, and `check_plugin.py ... --kit-names 0`
still passes. Two scripts change (`CMB_ControllerScript.psc`, `CMB_LookF4SE.psc`; `check.sh`: 12 .pex, no warning, no
new native in the stubs). No asset changes: the meshes, textures, materials, sounds and clips are 2026-11-10a's. The
engine model doesn't change either (the slower pull is the plugin's throttle, `[Steer] PullTime`): `engine_model.py
--check-off` checks the same six builds and no new `check_off` file is written. The harness
(`tools/f4se-slope/test/run.sh`, 26 modes) expects 1878 checks: custom 101, view 187, launch 17, sound 128, load 45,
wrongversion 5, the rest as 2026-11-14a's; `DEF58` rides every older mode at this build's off values.

Since 2026-11-15b (test 53's and test 54's wishes) the generator makes nine records more, right after the field kit's
0xBFE and only with the look: first person's `CMB_ViewBack` 0xBFF (1, the MCM's "Looking back while reversing (first
person)"), `CMB_ViewBackNow` 0xC00 (0, the plugin's word to the controller, no control), `CMB_ViewRoll` 0xC01 (4) and
`CMB_LookKey` 0xC02 (44, Z), then the weapons' `CMB_RideWeapons` 0xC03 (1, Handguns only), `CMB_HandgunKeywords` 0xC04
(a FLST holding Fallout4.esm's WeaponTypePistol 04A0A0; more keywords can be added with a plugin editor), `CMB_RiderGun` 0xC05,
`CMB_WeaponAway` 0xC06 and `CMB_RiderGunPose` 0xC07 (0 each): 8 float globals and 1 form list, each block throwing
unless they land there (`CMB_Slope.dll` finds the four view globals and the weapons' four by ID, and the harness's fake
uses the same numbers: renumber them together). The controller's group `Fixes_59` gets nine properties after
`CMB_KitWhere`: `CMB_ViewBack`, `CMB_ViewBackNow`, the five weapons forms, and Fallout4.esm's `WeaponTypeRifle` (04A0A1,
a keyword: never a handgun) and `ActionSheath` (046BAF, an action: the put-away's fallback). `CMB_AllowCombat` (0x802,
0) stays, read only by a controller without `CMB_RideWeapons`. `--look-ids` appends the nine (look_ids.txt **847** IDs;
the file is append-only: never renumber or remove a line). In `config.json` Riding's switch "Allow combat while riding"
gives its place to the stepper "Weapons while riding" (None, Handguns only, Any weapon (standing poses), on 0xC03), the
stepper "Looking back while reversing (first person)" (Off, Over the shoulder, Third person, on 0xBFF) and the slider
"View leans in turns (first person, deg)" (0-10, step 1, on 0xC01) come after "Look down on getting into first person
(deg)", and Hotkeys gets the slider "Look key (scan code)" (0-211, step 1, on 0xC02) after "Brake key (scan code)";
`keybinds.json` doesn't change. `tools/build.sh` prints `checked cmb_controllerscript: 203 properties` and "plugin and
scripts agree"; the ESP holds **1062** in its header's count (no new group: the form list joins the fuel list's), its
next ID **0xC08** (760 IDs left under the 0xF00 guard). A record-by-record comparison with 2026-11-15a's plugin: `TES4:
HEDR records 1053 -> 1062, next ID 0xBFF -> 0xC08`, `added 9 (000BFF-000C07): 8 GLOB, 1 FLST`, `removed 0`, `changed 1`
(the controller quest's VMAD). `--look-build 2026-11-07a` still writes the 2026-11-07a build's ESP, `config.json` and
`keybinds.json` byte for byte (none of the nine; the switch kept). Two scripts change, `CMB_ControllerScript.psc` (the
weapons' rules; third person while backing, its poll on timer 59 and the put-away's on 60) and `CMB_GearRestoreF4SE.psc`
(`GunKeywords`, a gun instance's keywords through F4SE), and since the review the controller's OnGameReloaded cancels a
put-away caught in a save; `check.sh`: 12 .pex, no warning. The stubs gain the vanilla
`Actor.GetEquippedWeapon`, `WornHasKeyword`, `PlayIdleAction` and the `OnItemUnequipped` event,
`InputEnableLayer.EnableFighting`, `Weapon.psc` and `Action.psc`, and F4SE's `Actor.GetInstanceOwner` and
`InstanceData.psc` (`Owner`, `GetKeywords`), as the real sources have them (`audit_stubs.py`: 0 problems).
`tools/rider/make_rider_plugin.py` now also writes `CMB_RiderPose_report.txt` beside the plugin it makes (every subgraph
entry of the human race and its additive races, and the pistol entries' clips by name, for a later build's seated pistol
clips; `--no-report` leaves it out; the plugin is the same either way). The engine model doesn't change. The harness
(`tools/f4se-slope/test/run.sh`, 26 modes) expects 1972 checks: wall 101, caution 25, sound 130, view 230, roomold 61,
arms 89, the rest as 2026-11-15a's (1963 before the review's fixes: wall 99, view 225, arms 87); `DEF59` rides every older
mode at this build's off values, the review's `[Steer] FirstKeysArmed=0` among them.

Test 53's wish (c), the right-hand cables, changes the four nifs whose bars the plugin turns: `tools/rider/bar_cables.py`
cuts the pieces of `static_black` that hang from the bars into a new shape `<stem>_front_cables` (DESIGN.md, *Spinning
wheels and turning bars*), on the built nifs, every other block byte for byte. From the repository, on the 2026-11-10a
package's Data (the asset base; its nifs are 2026-11-15a's):
```
python3 -I tools/rider/bar_cables.py --data <2026-11-10a's Data> --out <overlay>/Data/Meshes/CMB --pynifly <PyNifly>
#   -> the three worn nifs and CMB_BikeView.nif (3 cables cut: 2239 triangles, 2046 vertices into front_cables);
#      CMB_BikeParked.nif and CMB_BikeParts.ini untouched; --bar-cables 0 writes the four as they were, byte for byte
python3 -I tools/rider/check_bike_meshes.py --pynifly <PyNifly> --data <the asset base with the overlay laid over it> \
    --look-c2                                                     # 74 PASS, 0 FAIL (2026-11-10a's tree: 1 FAIL, "cables")
```
`build_bike.sh` runs it as its `cables` stage after `build` (in the default list; `CABLES=0` skips it, and a nif already
cut is left as it is), and `look_render.py --views cables` renders the bars at -16, 0 and +16 degrees and the cut at
full lock. The four nifs' sha256: `CMB_BikeView.nif` 1a5faffc..., `CMB_BikeWorn.nif` 38795a24..., `CMB_BikeWornRider.nif`
9c621c21..., `CMB_BikeWornRiderF.nif` 99bd4135... (the package manifest has them in full); two runs give the same. The
package lays them over the asset base with `OVERLAY=<overlay>/Data` (a Data-like folder: `Meshes/CMB/...` at its top).

Since 2026-11-16a (the third customisation build, C3: the 3D helmet badges, the Gunners skull, the plates' emblems and
font, the seat's colour, the alphabetical lists) the generator makes **72** records more, right after the weapons'
0xC07 and only with the look, as a third block `c3_ids` of `look_options.json` (every C3 entry carries `"since":
"2026-11-16a"`): `CMB_Look_Seat` 0xC08 (0, the seat as it came), `CMB_ap_Seat` 0xC09 (an attach point named "Seat"),
the tank options "Enclave helmet (3D)", "Brotherhood helmet (3D)" and "Gunners skull" (TankL 17-19 at 0xC0A-0xC12,
TankR 18-20 at 0xC13-0xC1B; MSWP, OMOD, COBJ each) and the fender's "Gunners skull" (18, 0xC1C-0xC1E), the Seat's 15
options (0xC1F-0xC4B: as it came, ten solid colours, four with a contrasting piping; each swap's two entries carry the
colour's V, (row + 0.5) / 16, as CNAM), its option list `CMB_LookOptions_Seat` 0xC4C, two empty swap lists
`CMB_LookSwaps_PlateInk` 0xC4D and `CMB_LookSwaps_PlateBack` 0xC4E (so `CMB_LookSwapLists` stays index = slot with the
Seat at 11) and `CMB_LookSwaps_Seat` 0xC4F: 1 GLOB, 1 KYWD, 22 MSWP, 22 OMOD, 22 COBJ, 4 FLST. The block throws unless
`NextFormID` is 0xC08 at its start and each record lands at its table ID. In place: the 34 tank swaps of 2026-11-07a's
tank options gain the four helmet shapes' identities (2 -> 6 entries, the slots' `sources_c3`), the tank and fender
lists the new options, `CMB_LookCategories` and `CMB_LookSwapLists` the Seat's (12 each), the look item and both riding
armours a 12th attach point and the template its option 0, and every look recipe's created-object priority its
option's place in the alphabetical order (the pinned ones first: as it came, None, "Same as the left", "The plate's
own"; Paint's palette test last; the steppers Mirrors and Tyres in their order; an option 0's priority stays 0, so 273
of the 285 recipes carry one). The controller's group `Look_C3` gets five properties after `LookSetPlate`
(`CMB_Look_Seat`, `TankRightOf`, `UiOrder`, `UiRank`, `UiStart`; the eleven full properties `UiTankL` ... `UiFactionSet`
are the script's own, never filled) and CMB_LookF4SE's three at its end (`CMB_Look_Seat`, `TankRightOf`, `SeatV`); the
controller's group `Look_C3_UiFallback` (eleven globals for a later ESP, should MCM not call the full properties) is
left unfilled. `--look-ids` appends the 72 (look_ids.txt **919** IDs; append-only: never renumber or remove a line). In
`config.json` the Look section gets the dropdown "Seat" after "Tyres" (22 controls), and the eleven dropdowns (both tank
badges, the fender, Paint, Rims, Seat, the plate's four, Faction set) list their choices alphabetically after the pinned
ones and read and write the controller's properties `UiTankL` ... `UiFactionSet` (`"sourceType": "PropertyValueInt"`,
`"scriptName": "CMB_ControllerScript"`, on the quest 0x80D) instead of the globals; `keybinds.json` doesn't change.
`tools/build.sh` prints `checked cmb_controllerscript: 208 properties`, `checked cmb_lookf4se: 36 properties`, `checked
285 look options in 12 slots: 249 swaps, 285 look recipes, ... highest 000C4F; look_ids.txt 919 IDs; ... C3
000C08-000C4F (72), the lists alphabetical: 273 recipes with a priority; the MCM's Look section 22 controls` and "plugin
and scripts agree"; the ESP holds **1134** in its header's count (no new group), its next ID **0xC50** (688 IDs left
under the 0xF00 guard). A record-by-record comparison with 2026-11-15b's plugin: `TES4: HEDR records 1062 -> 1134, next
ID 0xC08 -> 0xC50`, `added 72 (000C08-000C4F): 22 COBJ, 22 MSWP, 22 OMOD, 4 FLST, 1 GLOB, 1 KYWD`, `removed 0`, `changed
298` (34 MSWP, 252 COBJ priorities, 8 FLST, 3 ARMO, the controller quest's VMAD). Two scripts change,
`CMB_ControllerScript.psc` (slot 11, the right tank's follow through `TankRightOf`, the dropdowns' properties and the
fallback's hooks) and `CMB_LookF4SE.psc` (the seat's V in Compose and WornIndex, the follow); `check.sh`: 12 .pex, no
warning. The F4SE plugin and `CMB_Slope.ini` don't change (2026-11-15b's, byte for byte), nor does the harness.

The off switches of the ESP (none of the two is in the package; each A/B ESP is checked by `check_plugin.py`):
```
dotnet tools/esp-generator/bin/out/EspGenerator.dll --look-build 2026-11-08a <folder>/CommonwealthMotorbike.esp
#   -> 2026-11-15b's ESP, config.json and keybinds.json byte for byte (none of the 72, nothing in place);
#      --look-build 2026-11-07a still the 2026-11-07a build's (fdb5b3a); the generator knows 07a, 08a and 16a
dotnet tools/esp-generator/bin/out/EspGenerator.dll --kit-order table <folder>/CommonwealthMotorbike.esp
#   -> the presentation in table order: every recipe's priority 0, the MCM's dropdowns on the globals in table order
#      (2026-11-15b's lists, the C3 choices at their ends), the Ui arrays the identity; espcmp against the default:
#      changed 274 (273 COBJ INTV, the quest's VMAD)
dotnet tools/esp-generator/bin/out/EspGenerator.dll --dump <folder>/CommonwealthMotorbike.esp | \
    python3 -I tools/esp-generator/check_plugin.py Data/Scripts/Source/User --kit-order table --mcm <folder>
#   -> "plugin and scripts agree" (an A/B's MCM is checked from its own folder: --mcm <its Data-like folder>)
```

The art of C3 is built from the shipped files and the repository's own drawing code, with no stage and no bake
([ASSETS.md](ASSETS.md), *The third customisation build's files*): the helmets by `look_emblems.py` (the new
`emblems` stage of `build_bike.sh`, after `cables`) and `emblem_art.py`, the skull, the grounds and the plates by
`bike_art.py --badges` / `--plates`, `look_badges.py` and `look_plates.py`, the seat by `look_seat.py`. From the
repository, with the mesh Python and the DDS Python ([ASSETS.md](ASSETS.md), *Tools*), into one overlay a unit:
```
python3 -I tools/rider/bike_art.py --badges --out <art_b>           # the skull, the two enamel grounds (badges.json)
<DDS python> -I tools/rider/look_badges.py --art <art_b> --out <overlay B>                 # 3 DDS, 3 new materials
python3 -I tools/rider/bike_art.py --plates --out <art_p>           # the die-pressed font, the emblems at plate scale
<DDS python> -I tools/rider/look_plates.py --art <art_p> --out <overlay B>                 # 6 DDS change
<mesh python> -I tools/rider/look_emblems.py --data <2026-11-10a's Data> --data <2026-11-15b's meshes> \
    --out <overlay A>/Meshes/CMB --pynifly <PyNifly> [--ground-field <art_b>/badges.json]   # the five nifs
<DDS python> -I tools/rider/emblem_art.py --data <overlay A>                               # 4 DDS, 10 materials
<DDS python> -I tools/rider/look_seat.py --data <overlay C> --base <2026-11-10a's Data> \
    --base <2026-11-15b's meshes> --pynifly <PyNifly>                                      # 2 DDS, 28 materials
```
Each tool has its `--check` (below, and [ASSETS.md](ASSETS.md)); two runs give the same bytes, and the 61 files of the
2026-11-16a package rebuild byte for byte from this commit. The off switches of the art, each giving 2026-11-15b's files
byte for byte: `look_emblems.py --emblems 0` (`EMBLEMS=0`: the five nifs as they are, no helmet art), `bike_art.py
--badges --through 2026-11-08a` with `look_badges.py --through 2026-11-08a` (the 13-badge atlas), `bike_art.py --plates
--plate-font 2026-11-08a --plate-emblems 2026-11-09a` (the stroked font and the 2026-11-09a emblems: `plates_d/_n/_s.dds`
b5eacce3..., 78b75210..., 8892936a..., `plate_text_d/_n/_s.dds` f81f2791..., 2884547f..., cff4e808...); `look_seat.py`
only adds files (the seat's option 0 is the shipped files). In a game install the A/B is the 2026-11-15b package's files
copied back over this build's (the five nifs, the three badge and six plate textures). The checks over the whole tree
(the 2026-11-10a package's Data with 2026-11-15b's four meshes and the three overlays laid over it, in that order):
```
<mesh python> -I tools/rider/check_bike_meshes.py --pynifly <PyNifly> --data <tree> --look-c3 [--look-targets all] \
    --ground-field <art_b>/badges.json --knees <tree>/Meshes/Actors/Character/Animations/MT/CMB_Rider
#   -> 80 PASS, "all checks passed": 51 shapes parked, 54 worn and view (55 of the plugin's 64), the helmets inside their
#      ground's enamel field and clear of the bars' sweep and the riding clips' legs, 468 materials files, 129 DDS
#      (120.5 MB of the 125 MB budget), seat_p.dds a palette (A8R8G8B8, one mip)
<DDS python> -I tools/rider/look_badges.py --check --art <art_b> --out <tree> \
    --plate-nif <tree>/Meshes/CMB/CMB_BikeParked.nif --pynifly <PyNifly> --base <2026-11-15b's tree>   # all passed
<DDS python> -I tools/rider/look_plates.py --check --art <art_p> --out <tree>          # 22 checks, all passed
<DDS python> -I tools/rider/look_seat.py --check --data <tree> --base <2026-11-10a's Data> --base <2026-11-15b's meshes> \
    --pynifly <PyNifly>                                                               # all checks passed
<DDS python> -I tools/rider/emblem_art.py --check --data <tree> --reference <2026-11-10a's Data>   # all passed
```
The package lays the four overlays over the asset base in order, `OVERLAY=<2026-11-15b's meshes>:<overlay
A>:<overlay B>:<overlay C>` (a colon-separated list, the later winning): 47 files new and 14 changed against
2026-11-15b's package (the five nifs, the three badge textures and the six plate textures).

The vanilla form IDs the plugins use (PlayerRef, XMarker, HumanRace, HumanRaceSubGraphData, SpeedMult, CarryWeight, FallingDamageMod, Health, Pip-Boy, AnimArchetypePlayer) were checked against Mutagen's FormKey list generated from the real `Fallout4.esm`. The record layouts were also compared field by field with xEdit's Fallout 4 definitions.

## For developers: packaging a build

Since 2026-11-14a the release package is made by `tools/package` ([its README](../tools/package/README.md) has the
details and every rule): `package.sh` makes `CommonwealthMotorbike_<build>/` (`README.txt` and `Data/`) and its two
zips, `CommonwealthMotorbike_<build>.zip` and `CommonwealthMotorbike_MO2.zip` (`Data`'s contents at its root, a Mod
Organizer 2 mod folder as it is), from one commit of this repository and the asset base: the previous package's `Data`
folder, with any newly built assets laid over it. `verify_zips.py` proves both zips afterwards. Bash, git, Python 3's
standard library and Caprica are all it needs. For a build:

1. Write `tools/package/builds/<build>.json` from `builds/TEMPLATE.json` (the ESP's record count and next object ID and
   the records it must hold; the files per extension; the assets and compiled scripts that differ from the previous
   package, which the verifier fails if they aren't listed) and the build's notes into
   `tools/package/README.template.txt` (line 1 names the build and keeps `@COMMIT@`; the heading `WHAT'S NEW IN
   <build>`; ASCII; the credit block at its end exactly as `CREDITS.txt`). Commit: the tracked files under `Data/` and
   `tools/` must be clean.
2. Restore the asset base from the previous package's zip, unpacked as data (`bash tools/package/package.sh --extract
   <its zip> <folder>`), and prove it (`bash tools/package/package.sh --check-assets
   <folder>/CommonwealthMotorbike_<previous>/Data`: every file of `assets.sha256` there byte for byte, and no other
   asset).
3. Package: `BUILD=<build> ASSETS=<previous Data> [OVERLAY=<new assets>] OUT=<out> CAPRICA=<Caprica> bash
   tools/package/package.sh`. It reads the commit's objects, never the working tree: the tracked files under `Data/`
   (but the four synthesised engine WAVs, which come from the asset base) and one `.pex` per `.psc`, compiled from the
   commit's sources by its own `tools/syntax-check/check.sh`, the headers stamped with the commit's time so that two
   runs give the same bytes. It prints what it took from where, one `ok` line per guard check, both zips' sizes and md5
   and `packaged commit <sha7>`; any `FAIL` stops it before a zip is written.
4. Verify: `python3 -I tools/package/verify_zips.py <out>/CommonwealthMotorbike_<build>.zip
   <out>/CommonwealthMotorbike_MO2.zip --repo . --commit HEAD --previous <the previous package's folder>
   --list-changes`: one PASS or FAIL line per check, exit 0 only with no FAIL. `--list-changes` prints what differs from
   the previous package, with each file's sha256: when it is exactly what the build meant to change, paste it into the
   manifest's `vs_previous` (a later commit can hold it: `PACKAGE_COMMIT=<the build's commit>` still packages and names
   the build's commit; give the verifier the same).
5. Once the build has shipped, `bash tools/package/package.sh --write-assets-manifest <its Data folder>` rewrites
   `assets.sha256` for the next build, to commit with its manifest.

On a fresh machine the tools are rebuilt as in the steps above: MinGW-w64 for `CMB_Slope.dll` (step 1b; wine for its
harness), Caprica for the scripts (`tools/syntax-check/build-caprica.sh`, step 2), the .NET 8 SDK for the generator
(`tools/build.sh`, above), Python 3 for the rest; the asset base comes back from the last package's zip (step 2 of this
list). `builds/2026-11-10a.json` rebuilds the 2026-11-10a package byte for byte and is the tools' own test
(`tools/package/README.md`, *2026-11-10a, rebuilt*).

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
