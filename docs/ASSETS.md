# Assets: bike meshes, riding animations, rider-pose plugin

The mod reuses Fallout 4's own motorcycle model and adds its own riding animations. **None of it is in this
repository**, because it's all derived from Bethesda's files. The tools in `tools/rider` build it on your PC from
your own copy of the game:

| File (under `Data\`) | Built by | What it is |
|---|---|---|
| `Meshes\CMB\CMB_BikeParked.nif` | `build_bike_meshes.py` | unmodified copy of the vanilla motorcycle (keeps its collision) |
| `Meshes\CMB\CMB_BikeWornRider.nif`, `CMB_BikeWornRiderF.nif` | `build_bike_meshes.py --seat` | the same model as wearable armor: faces forward, seat over the origin, hanging off the rider's `COM` bone (male and female seat heights) |
| `Meshes\CMB\CMB_BikeWorn.nif` | `build_bike_meshes.py` | the same again, skinned to the `AnimObjectA` bone on the ground: used when the rider isn't seated |
| `Meshes\Actors\Character\Animations\MT\CMB_Rider\*.hkx` and `...\CMB_Rider\Female\*.hkx` | `riding_anims.py` | seated riding versions of the holstered walk/run/turn/start/stop/idle clips, and of the jump/fall/land clips when those were extracted |
| `...\CMB_Rider\CMB_RiderClips.json` (and `Female\`) | `riding_anims.py` | each clip's root motion and events, for the step below |
| `...\CMB_Rider\CMB_RiderSeat.json` (and `Female\`) | `riding_anims.py` | where the seated rider's `COM` bone sits, for the bike that hangs off it |
| `CMB_RiderPose.esp` + `Meshes\AnimTextData\...` | `make_rider_pose.bat` | small plugin that makes the game use those clips while you ride, and the animation data it needs. Built from your load order; no Creation Kit |
| `Meshes\CMB\CMB_Keys.nif` (optional) | you: copy any vanilla key mesh | 3D preview of the keys in the Pip-Boy |

If someone already handed you the meshes and the `CMB_Rider` folder, skip to
[the rider-pose plugin](#4-the-rider-pose-plugin-and-animation-data). That step always runs on your own PC.

## 1. Tools

- **Python 3.10+** with numpy (`pip install numpy`; add `matplotlib` for preview images).
  `make_rider_plugin.py` needs nothing beyond Python itself.
- **PyNifly 29.1 or newer** ([BadDogSkyrim/PyNifly](https://github.com/BadDogSkyrim/PyNifly) releases). Unzip the
  release and pass its `io_scene_nifly` folder as `--pynifly`. Blender isn't needed: the scripts use PyNifly's nif
  library (`NiflyDLL.dll` ships in the zip) and its Fallout 4 HKX reader/writer directly.
- **Bethesda Archive Extractor** (or Archive2, which comes with the Creation Kit) to pull files out of the game's
  `.ba2` archives.

## 2. Extract the game files

Into one work folder (say `C:\CMBwork`), keeping the archive paths:

| From | Files |
|---|---|
| `Fallout4 - Meshes.ba2` | `meshes\setdressing\vehicles\motorcycle\motorcycle_clean.nif` (or `motorcycle_dirty.nif`) |
| | `meshes\actors\character\characterassets\skeleton.nif`, `malebody.nif`, `femalebody.nif` |
| `Fallout4 - Animations.ba2` | `meshes\actors\character\characterassets\skeleton.hkx` |
| | everything in `meshes\actors\character\animations\mt\player\`, `...\mt\confident\` and `...\mt\neutral\` (with their `female` subfolders) |
| | in particular the jump clips: `mt\neutral\jump*.hkx` and `mt\neutral\female\jump*.hkx` (`JumpInPlace`, `JumpWalk`, `JumpRun`, their `Fall` and `Land` clips, `JumpImpactLand`, `JumpRunImpactLand`) |

Use the bodies your game actually shows (for example the CBBE `femalebody.nif`): they're only used to sit the hips
exactly on the seat. Skeleton replacers that keep the vanilla body bones (Community Fixes' `skeleton.nif`, Combined
Arms' `skeleton.hkx`, which only adds weapon bones) are fine.

## 3. Meshes and clips

```
set PYN=C:\Tools\PyNifly\io_scene_nifly
set W=C:\CMBwork\meshes\actors\character
set OUT=<repository>\Data\Meshes

python tools\rider\riding_anims.py --pynifly %PYN% --vanilla %W% ^
    --body %W%\characterassets\malebody.nif --female-body %W%\characterassets\femalebody.nif ^
    --out %OUT%\Actors\Character\Animations\MT\CMB_Rider

python tools\rider\build_bike_meshes.py --pynifly %PYN% ^
    --model C:\CMBwork\meshes\setdressing\vehicles\motorcycle\motorcycle_clean.nif --out %OUT%\CMB ^
    --seat %OUT%\Actors\Character\Animations\MT\CMB_Rider

python tools\rider\verify_clips.py --pynifly %PYN% --vanilla %W% --clips %OUT%\Actors\Character\Animations\MT\CMB_Rider
python tools\rider\verify_clips.py --pynifly %PYN% --vanilla %W% --clips %OUT%\Actors\Character\Animations\MT\CMB_Rider\Female --female
```

Generating the clips takes a while (around 25 minutes for both sets). The meshes come second because the bike
that hangs off the rider needs to know where the seated rider sits (`CMB_RiderSeat.json`).

**How the worn bike works.** Armor meshes must be skinned. While you're seated, the bike is weighted 100% to `COM`,
the bone the whole body hangs from, at exactly where `COM` sits in the riding clips. So it's under you where it
should be, leans with you in turns, and turns with you when the game twists the body on the spot or in dialogue
(DESIGN.md has the details). The second copy, `CMB_BikeWorn.nif`, is weighted to `AnimObjectA`, a bone that sits on
the ground at the character's origin and that walking and running never move: the controller uses it when the rider
isn't seated (no rider pose, weapon drawn, or `CMB_BikeFollowsRider 0`), so the bike stays planted. The script also
turns the bike round, because the vanilla model points backwards.

**How the clips are made.** Every clip the game plays for holstered movement gets a seated version with **the same
file name, length, root motion and control events** as the vanilla clip it stands in for. Only the body pose changes,
so the game's speed and turning logic is untouched. Footstep sounds are dropped. The pose is fitted to the bike: hips
on the seat, hands on the grips (exact, via IK), feet on the pegs, leaning forward more with speed and into turns. At a
standstill the left foot goes down and the bike tips onto it. `verify_clips.py` checks all of that against the vanilla
files. `preview.py` renders still images if you want to look before going in game.

Two exceptions to "the same root motion". The 180° reversals while moving (`walk_to_walk_l180`/`r180`,
`run_to_run_l180`/`r180`) follow a leaning arc instead of vanilla's stop-and-spin, with the same length, total turn
and distance. And the hard landings (`JumpImpactLand`, `JumpRunImpactLand`) take the soft landing's timing when the
events match, so a drop doesn't stop you as long. The jump, fall and landing clips are only built from the vanilla ones
(a guessed length could hold the rider in a landing): if they weren't extracted, `riding_anims.py` skips them and
jumps and landings show the standing clips.

**Which vanilla clip.** The player's holstered animations come from `MT\Player`, then `MT\Confident`, then
`MT\Neutral` (female: the `Female` subfolders of those first). That order was read off the game's own AnimTextData
(all 193 male and 191 female clip names agree), and each riding clip copies the timing of the clip the game would
otherwise play. Female clips go in `CMB_Rider\Female`.

`riding_anims.py` also writes `CMB_RiderClips.json` next to the clips: their root motion and events in the form the
game's AnimTextData uses (checked against the Creation Kit's own output for 80 vanilla clips: within 1 unit and
0.6°).

**Weapon drawn.** There are no riding clips for that: with combat allowed (`CMB_AllowCombat 1`), drawing a weapon
shows the normal standing weapon poses. The game also has no backwards or sideways clips with the weapon holstered.
The character turns round instead, so riding never needs them.

### Stand-ins

If a clip wasn't extracted from the folder the game uses, the nearest one stands in for its timing (for example
`MT\Neutral` for `MT\Confident`, or `JogForward` for `JogLeanLeft`). Pass the archive's file list with
`--game-files` and `riding_anims.py` lists exactly which files would make the timing exact. The animation data
always describes the clip as built, so a stand-in only means the turn or lean takes slightly different time
than vanilla's.

## 4. The rider-pose plugin and animation data

```
make_rider_pose.bat "C:\Modding\MO2" Default      (Mod Organizer 2: instance folder and profile)
make_rider_pose.bat                                 (no mod manager)
```

It reads your load order and game files and writes `CMB_RiderPose.esp` (light, a few KB) and its
`Meshes\AnimTextData`. With MO2 both go into a new mod, *Commonwealth Motorbike - Rider Pose*: enable it and the
plugin. Under the hood: `python tools\rider\make_rider_plugin.py --data <Fallout 4>\Data --mo2 <MO2> --profile <name>
--out <...>\CMB_RiderPose.esp`.

**Run it again** whenever you add, remove or update a mod that adds animation entries for the player (the
Unofficial Fallout 4 Patch does), or the riding clips change.

**How it works.** While you ride, the controller script gives the player the animation flavour keyword
`CMB_AnimFlavorRider` (`ChangeAnimFlavor`). The plugin holds that keyword and an **additive race**, the way the DLCs,
Sim Settlements 2 and Combined Arms add animations to humans without touching HumanRace: subgraph entries added
to `HumanRaceSubGraphData`. Ours is a copy of every third-person holstered entry for the player, from
`HumanRaceSubGraphData` itself and from every additive race in your load order, each with the keyword added and
`MT\CMB_Rider` searched first (`MT\CMB_Rider\Female` first for female entries). The game uses the entry whose keywords
all match and that matches the most of them, so with the keyword on, a copy always beats the entry it copies,
including the Unofficial Patch's crippled-limb entries. Anything without a riding version (swimming, staggering,
and jumping and landing unless those clips were extracted) comes from the usual folders.

**Masters.** Always `Fallout4.esm`, plus any plugin whose keywords the copied entries use (for example
`Unofficial Fallout 4 Patch.esp`). Rebuild it if you remove one of those.

**HumanRace isn't edited.** LooksMenu, LooksMenu Customization Compendium and other race mods keep working without a
patch, whatever the load order.

### Animation data without the Creation Kit

The game doesn't look for clips at run time. For every subgraph entry, `Meshes\AnimTextData` holds what the Creation
Kit's `-GenerateAnimInfo` worked out in advance: which file each clip name resolves to, each clip's length, root
motion and events, and the graph's speed and stance data. The files are named after the entry:
`(CRC32 of the folder list << 32) | CRC32 of the behaviour graph` (lowercase, Bethesda's CRC: zero start, no final
xor). That formula reproduces the file names of a Creation Kit-built mod exactly.

`make_rider_plugin.py` writes the files for each copied entry from the entry it copies: the game's own files, read from
your `Fallout4 - Animations.ba2` (or loose files, or `--animtextdata <folder>` with extracted ones), with every clip we
provide pointed at `CMB_Rider` and given our clip's length, root motion and events (`CMB_RiderClips.json`). Speed and
stance data don't name clips and are copied. Footstep events are left out, as in the clips. The vanilla persistent
list (`PersistantSubgraphInfoAndOffsetData.txt`) isn't touched: holstered entries aren't in it.

### Turning it off

`set CMB_UseRiderPose to 0` (back on: `1`). Or untick `CMB_RiderPose.esp`. Without it the mod still works, and you
run in place over the bike.

## Quick in-game look at the worn bike

`help CMB 4` lists the mod's forms. `player.equipitem <CMB_BikeRiderArmorFrame form id>` shows the worn bike without
riding (the seated version, `CMB_BikeRiderArmor`, only lines up when seated); `player.unequipitem <id>` and
`player.removeitem <id> 1` undo it.

| Symptom | Likely cause |
|---|---|
| bike missing, armor equipped | `CMB_BikeWornRider.nif` / `CMB_BikeWornRiderF.nif` (seated) or `CMB_BikeWorn.nif` (otherwise) not at `Data\Meshes\CMB\` |
| bike sunk into the ground or floating while seated | the `CMB_BikeWornRider` meshes were built from an older clip set: build the clips, then the meshes with `--seat` |
| pink / white bike | the vanilla motorcycle textures/materials aren't loading (they come from the base game archives) |
| bike pops out at screen edges | an old `CMB_BikeWorn.nif` with a small culling sphere; rebuild it |
| standing rider over the bike while riding | rider pose off, `CMB_RiderPose.esp` not active, or its AnimTextData missing (the mod folder from `make_rider_pose.bat` not enabled) |
| standing poses only with a crippled limb | an animation mod added player entries after the plugin was built: run `make_rider_pose.bat` again |
| rider seated but slides / clips misbehave | `AnimTextData` outdated: run `make_rider_pose.bat` again after rebuilding clips |

## Background: why custom clips

The game has no motorcycle riding animations to borrow. `Fallout4.esm` does contain a keyword called
`AnimsMotorcycle` (`000AB732`), but nothing uses it, and the animation archives hold no motorcycle clips. The only
motorcycle assets are the two parked-bike models (the rusted `Motorcycle01` and the clean pre-war
`Motorcycle01_Prewar`). Open Animation Replacer isn't needed, and this doesn't use it: the subgraph system above is
the game's own way of swapping animation folders.
