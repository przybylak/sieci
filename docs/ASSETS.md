# Assets: bike meshes, riding animations, rider-pose plugin

The mod reuses Fallout 4's own motorcycle model and adds its own riding animations. **None of it is in this
repository**, because it's all derived from Bethesda's files. The tools in `tools/rider` build it on your PC from
your own copy of the game:

| File (under `Data\`) | Built by | What it is |
|---|---|---|
| `Meshes\CMB\CMB_BikeParked.nif` | `build_bike_meshes.py` | unmodified copy of the vanilla motorcycle (keeps its collision) |
| `Meshes\CMB\CMB_BikeWorn.nif` | `build_bike_meshes.py` | the same model as wearable armor: faces forward, seat over the origin, skinned to the `AnimObjectA` bone |
| `Meshes\Actors\Character\Animations\MT\CMB_Rider\*.hkx` and `...\CMB_Rider\Female\*.hkx` | `riding_anims.py` | seated riding versions of the holstered walk/run/turn/start/stop/idle clips |
| `CMB_RiderPose.esm` | `make_rider_pose.bat` | small plugin that makes the game use those clips while you ride |
| `Meshes\AnimTextData\...` | `generate_anim_info.bat` (Creation Kit) | the game's index of clip timing and root motion, regenerated to include the riding clips |
| `Meshes\CMB\CMB_Keys.nif` (optional) | you: copy any vanilla key mesh | 3D preview of the keys in the Pip-Boy |

If someone already handed you the meshes and the `CMB_Rider` folder, skip to
[the rider-pose plugin](#4-the-rider-pose-plugin). That step always runs on your own PC.

## 1. Tools

- **Python 3.10+** with numpy (`pip install numpy`; add `matplotlib` for preview images).
  `make_rider_plugin.py` needs nothing beyond Python itself.
- **PyNifly 29.1 or newer** ([BadDogSkyrim/PyNifly](https://github.com/BadDogSkyrim/PyNifly) releases). Unzip the
  release and pass its `io_scene_nifly` folder as `--pynifly`. Blender isn't needed: the scripts use PyNifly's nif
  library (`NiflyDLL.dll` ships in the zip) and its Fallout 4 HKX reader/writer directly.
- **Archive2** (comes with the Creation Kit, `<Fallout 4>\Tools\Archive2`) or Bethesda Archive Extractor, to pull
  files out of the game's `.ba2` archives.

## 2. Extract the game files

Into one work folder (say `C:\CMBwork`), keeping the archive paths:

| From | Files |
|---|---|
| `Fallout4 - Meshes.ba2` | `meshes\setdressing\vehicles\motorcycle\motorcycle_clean.nif` (or `motorcycle_dirty.nif`) |
| | `meshes\actors\character\characterassets\skeleton.nif`, `malebody.nif`, `femalebody.nif` |
| `Fallout4 - Animations.ba2` | `meshes\actors\character\characterassets\skeleton.hkx` |
| | everything in `meshes\actors\character\animations\mt\player\` and `...\mt\neutral\` (with their `female` subfolders) |

Use the bodies your game actually shows (for example the CBBE `femalebody.nif`): they're only used to sit the hips
exactly on the seat. Skeleton replacers that keep the vanilla body bones (Community Fixes' `skeleton.nif`, Combined
Arms' `skeleton.hkx`, which only adds weapon bones) are fine.

## 3. Meshes and clips

```
set PYN=C:\Tools\PyNifly\io_scene_nifly
set W=C:\CMBwork\meshes\actors\character
set OUT=<repository>\Data\Meshes

python tools\rider\build_bike_meshes.py --pynifly %PYN% ^
    --model C:\CMBwork\meshes\setdressing\vehicles\motorcycle\motorcycle_clean.nif --out %OUT%\CMB

python tools\rider\riding_anims.py --pynifly %PYN% --vanilla %W% ^
    --body %W%\characterassets\malebody.nif --female-body %W%\characterassets\femalebody.nif ^
    --out %OUT%\Actors\Character\Animations\MT\CMB_Rider

python tools\rider\verify_clips.py --pynifly %PYN% --vanilla %W% --clips %OUT%\Actors\Character\Animations\MT\CMB_Rider
python tools\rider\verify_clips.py --pynifly %PYN% --vanilla %W% --clips %OUT%\Actors\Character\Animations\MT\CMB_Rider\Female --female
```

Generating the clips takes a while (around 15 minutes for both sets).

**How the worn bike works.** Armor meshes must be skinned. The bike is weighted 100% to `AnimObjectA`, a bone that
sits on the ground at the character's origin and that walking and running never move. So the bike stays planted
under you, and the riding clips can lean it, with the rider, in turns. The script also turns the parked bike round,
because the vanilla model points backwards.

**How the clips are made.** Every clip the game plays for holstered movement gets a seated version with **the same
file name, length, root motion and control events** as the vanilla clip it stands in for. Only the body pose changes,
so the game's speed and turning logic is untouched. Footstep sounds are dropped. The pose is fitted to the bike: hips
on the seat, hands on the grips (exact, via IK), feet on the pegs, leaning forward more with speed and into turns. At a
standstill the left foot goes down and the bike tips onto it. `verify_clips.py` checks all of that against the vanilla
files. `preview.py` renders still images if you want to look before going in game.

**Female clips** go in `CMB_Rider\Female`, timed from the vanilla female clips where those exist.

**Weapon drawn.** There are no riding clips for that: with combat allowed (`CMB_AllowCombat 1`), drawing a weapon
shows the normal standing weapon poses. The game also has no backwards or sideways clips with the weapon holstered.
The character turns round instead, so riding never needs them.

### Still missing

| Clips | Why | What to do |
|---|---|---|
| `walk_to_stand_l45/l90/l180/r/r45/r90/r180` | the vanilla files weren't in the first batch | extract `mt\neutral\walk_to_stand_*.hkx` (and `mt\neutral\female\...`), run `riding_anims.py` again. Until then, stopping while turning shows a standing stop |
| idle, idle flavours, dialogue (`posea_*`) | same | made without a vanilla reference ("provisional": guessed lengths, no events). Extract `mt\player\posea_*.hkx` (and `female\`) and run again to time them like the originals |

`riding_anims.py` prints the exact paths of anything it couldn't build.

## 4. The rider-pose plugin

```
make_rider_pose.bat
```

It reads your own `Fallout4.esm` and writes `Data\CMB_RiderPose.esm` (light, about 2 KB). Under the hood:
`python tools\rider\make_rider_plugin.py --fallout4 <Fallout 4>\Data\Fallout4.esm --out Data\CMB_RiderPose.esm`.

**How it works.** While you ride, the controller script gives the player the animation flavour keyword
`CMB_AnimFlavorRider` (`ChangeAnimFlavor`). The plugin holds that keyword and an **additive race**. That is how the
DLCs add animations to humans without touching HumanRace: their races (`DLC03HumanRaceAdditiveSubgraphData` and
so on) add subgraph entries to `HumanRaceSubGraphData`. Ours adds a copy of each of the player's third-person
holstered entries, with the keyword added and `MT\CMB_Rider\` searched first (`MT\CMB_Rider\Female\` first for
the female entries). The game uses the entry whose keywords all match and that matches the most of them, so the
copies only win while the keyword is on. Anything the folder doesn't have (jumping, swimming, staggering) comes
from the usual folders.

**HumanRace isn't edited.** LooksMenu, LooksMenu Customization Compendium and other race mods keep working without a
patch, whatever the load order. `CMB_RiderPose.esm` loads with the masters (it's an `.esm`) and is light-flagged,
so it doesn't take a load-order slot.

**Why it's built on your PC.** The copied entries come from your `Fallout4.esm`; their folder lists are Bethesda's
data, and guessing them would break every animation the riding folder doesn't cover. The rest of the plugin comes
from `tools/rider/template/CMB_RiderPose.esm`, which `tools/build.sh` generates.

### Animation data (Creation Kit)

The game reads clip timing and root motion from `Meshes\AnimTextData`, not from the `.hkx` files, so it has to be
regenerated once the clips and `CMB_RiderPose.esm` are installed:

- **Without a mod manager:** double-click `generate_anim_info.bat`.
- **Mod Organizer 2:** the Creation Kit must see MO2's virtual Data folder. In MO2: *Executables* (the gears icon)
  → add one with Binary `C:\Windows\System32\cmd.exe`, Arguments `/c "<repository>\generate_anim_info.bat"`,
  Start in `<Fallout 4>`. Run it from MO2. The new `Meshes\AnimTextData` files land in MO2's *Overwrite*; move them
  into the motorbike mod.

Either way it runs `CreationKit.exe -GenerateAnimInfo:CMB_RiderPose.esm "<Fallout 4>\Data" "<Fallout 4>\Data"`.
The plugin is an `.esm` with no spaces in its name because this command only accepts that.

> Some Creation Kit updates have reportedly broken `-GenerateAnimInfo` (Nexus threads around the 2024 next-gen
> update). If no `AnimTextData` folder appears, send the window's text; the fallback is writing those files directly,
> which needs a few vanilla `AnimTextData` files to copy the format from.

### Turning it off

`set CMB_UseRiderPose to 0` (back on: `1`). Or untick `CMB_RiderPose.esm`. Without it the mod still works, and you
run in place over the bike as before.

## Quick in-game look at the worn bike

`help CMB 4` lists the mod's forms. `player.equipitem <CMB_BikeRiderArmor form id>` shows the worn bike without
riding; `player.unequipitem <id>` and `player.removeitem <id> 1` undo it.

| Symptom | Likely cause |
|---|---|
| bike missing, armor equipped | `CMB_BikeWorn.nif` not at `Data\Meshes\CMB\` |
| pink / white bike | the vanilla motorcycle textures/materials aren't loading (they come from the base game archives) |
| bike pops out at screen edges | an old `CMB_BikeWorn.nif` with a small culling sphere; rebuild it |
| standing rider over the bike while riding | rider pose off, `CMB_RiderPose.esm` not active, or animation data not generated |
| rider seated but slides / clips misbehave | `AnimTextData` missing or outdated: run `generate_anim_info.bat` again |
| standing pose for a moment when stopping in a turn | the `walk_to_stand_*` clips (see *Still missing*) |

## Background: why custom clips

The game has no motorcycle riding animations to borrow. `Fallout4.esm` does contain a keyword called
`AnimsMotorcycle` (`000AB732`), but nothing uses it, and the animation archives hold no motorcycle clips. The only
motorcycle assets are the two parked-bike models (the rusted `Motorcycle01` and the clean pre-war
`Motorcycle01_Prewar`). Open Animation Replacer isn't needed, and this doesn't use it: the subgraph system above is
the game's own way of swapping animation folders.
