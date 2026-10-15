# Assets: bike meshes, riding animations, rider-pose plugin

The mod's bike is Nieve5677's **Harley-Davidson Iron 883** ([Sketchfab](https://sketchfab.com/3d-models/harley-davidson-iron-883-2015-612071b783f14a7288df2d361be9a244),
CC-BY-4.0) standing on Fallout 4's own motorcycle's collision, and the riding animations are the mod's own. The
vanilla motorcycle can be used instead. **None of it is in this repository**: the meshes mix the model with
Bethesda's collision and the clips are derived from Bethesda's files. The tools in `tools/rider` build it on your PC
from your own copy of the game and the downloaded model:

| File (under `Data\`) | Built by | What it is |
|---|---|---|
| `Meshes\CMB\CMB_BikeParked.nif` | `harley_meshes.py` (`build_bike_meshes.py` for the vanilla bike) | the vanilla motorcycle nif with its own shape hidden and the Harley's nine shapes added (the headlamp's lit parts among them), so its collision is kept |
| `Meshes\CMB\CMB_BikeWornRider.nif`, `CMB_BikeWornRiderF.nif` | `harley_meshes.py --seat` | the same model as wearable armor: faces forward, seat over the origin, hanging off the rider's `COM` bone (male and female seat heights); no light nodes since test 32 (the game keeps only a skinned nif's shapes: they're in `CMB_BikeLamp.nif`) |
| `Meshes\CMB\CMB_BikeWorn.nif` | `harley_meshes.py` | the same again, skinned to the `AnimObjectA` bone on the ground: used when the rider isn't seated |
| `Meshes\CMB\CMB_BikeLamp.nif`, `CMB_BikeLampF.nif`, `CMB_BikeLampFrame.nif` | `harley_meshes.py` | the headlamp's light nodes as an unskinned piece of their own, a second armor addon in its own biped slot (58) on each bike armor: a `Prn` string on the root naming the bone the bike hangs off (COM at the male and female seat heights, `AnimObjectA` for the planted frame), as the Pip-Boy's mesh does; a three-vertex speck so the nif isn't empty; the two `BSValueNode`s at the lens in that bone's space (the bike's own skin-to-bone transform), +X down the beam, which the engine's ADDN path lights as it does the Pip-Boy's, and which `CMB_Slope.dll` keeps at the lens; `BSX` flags; a `P-AttachLightOverride` connect point at the lens (a helmet lamp's way of taking the Pip-Boy's light over). Test 32: the piece shared the bike's slot and never reached the player's 3D; the light placed as a reference lit, and is kept as the fallback |
| `Meshes\CMB\CMB_BikeFit.json` | `harley_meshes.py` | where the Harley's seat, grips, pegs and steering axis are, for the riding clips (`riding_anims.py --fit`) |
| `Meshes\CMB\CMB_BikeParts.ini` | `harley_meshes.py` | the axles, wheel radius, steering axis and the headlamp's lens for `CMB_Slope.dll`, which spins the wheels, turns the bars and places the lamp's light (install it with the meshes) |
| `Textures\CMB\CMB_Harley_d.dds`, `_n.dds`, `_s.dds` | `harley_meshes.py` | the Harley's textures: one colour block per part (the download has none) |
| `Meshes\Actors\Character\Animations\MT\CMB_Rider\*.hkx` and `...\CMB_Rider\Female\*.hkx` | `riding_anims.py` | seated riding versions of the holstered walk/run/turn/start/stop/idle clips, and of the jump/fall/land clips when those were extracted |
| `...\CMB_Rider\CMB_RiderClips.json` (and `Female\`) | `riding_anims.py` | each clip's root motion and events, for the step below |
| `...\CMB_Rider\CMB_RiderSeat.json` (and `Female\`) | `riding_anims.py` | where the seated rider's `COM` bone sits, for the bike that hangs off it |
| `CMB_RiderPose.esp` + `Meshes\AnimTextData\...` | `make_rider_pose.bat` | small plugin that makes the game use those clips while you ride, and the animation data it needs. Built from your load order; no Creation Kit |
| `Meshes\CMB\CMB_Keys.nif` (optional) | you: copy any vanilla key mesh | 3D preview of the keys in the Pip-Boy |

If someone already handed you the meshes and the `CMB_Rider` folder, skip to
[the rider-pose plugin](#4-the-rider-pose-plugin-and-animation-data). That step always runs on your own PC.

## 1. Tools

- **Python 3.10+** with numpy and fast_simplification (`pip install numpy fast_simplification`; add `matplotlib`
  for preview images). `make_rider_plugin.py` needs nothing beyond Python itself.
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

And the bike model: download ["Harley Davidson Iron 883 2015"](https://sketchfab.com/3d-models/harley-davidson-iron-883-2015-612071b783f14a7288df2d361be9a244)
by Nieve5677 from Sketchfab in its glTF form (the zip holds `scene.gltf`, `scene.bin` and the licence) and unzip it
to, say, `C:\CMBwork\harley`. It's CC-BY-4.0: the credit in the README goes with anything you share.

## 3. Meshes and clips

```
set PYN=C:\Tools\PyNifly\io_scene_nifly
set W=C:\CMBwork\meshes\actors\character
set OUT=<repository>\Data\Meshes
set TEX=<repository>\Data\Textures
set HARLEY=python tools\rider\harley_meshes.py --pynifly %PYN% --gltf C:\CMBwork\harley\scene.gltf ^
    --vanilla C:\CMBwork\meshes\setdressing\vehicles\motorcycle\motorcycle_clean.nif ^
    --out %OUT%\CMB --textures %TEX%\CMB

%HARLEY%

python tools\rider\riding_anims.py --pynifly %PYN% --vanilla %W% ^
    --body %W%\characterassets\malebody.nif --female-body %W%\characterassets\femalebody.nif ^
    --out %OUT%\Actors\Character\Animations\MT\CMB_Rider --fit %OUT%\CMB\CMB_BikeFit.json

%HARLEY% --seat %OUT%\Actors\Character\Animations\MT\CMB_Rider

python tools\rider\verify_clips.py --pynifly %PYN% --vanilla %W% --clips %OUT%\Actors\Character\Animations\MT\CMB_Rider
python tools\rider\verify_clips.py --pynifly %PYN% --vanilla %W% --clips %OUT%\Actors\Character\Animations\MT\CMB_Rider\Female --female
```

Three steps because each needs the one before: the first `harley_meshes.py` run measures the model and writes
`CMB_BikeFit.json` (its seat, grips and pegs); the clips are posed to that; and the second run makes the two bikes
that hang off the seated rider, which need the seat height the clips settled on (`CMB_RiderSeat.json`). Generating
the clips takes a while (around 25 minutes for both sets).

`harley_meshes.py` takes `--body <hex>` for the tank and fenders' colour (default a deep red, `7a1118`), `--tris`
for the triangle budget (default 90000; the result runs about a fifth over it), `--sit` for how far back on
the seat the rider sits (0.27 of the seat's length from its front: snug behind the tank, where the arms still reach the
turned bars) and `--bar-angle` for how far the bars turn
(20 degrees; 0 builds one static set of shapes). The model comes out as nine shapes: three fixed, four that turn
with the bars (metal, matte, glass and the headlamp's lit parts: the model's own lamp is dropped and a 5.75" LED unit lathed in its place) and the two wheels, which the F4SE plugin moves (DESIGN.md); the plugin turns the rider's hands with the bars. The model is scaled to the vanilla bike's
length so the collision and the F4SE plugin's clearances still fit, which makes it about a quarter bigger than a
real Iron 883 next to the character, as the vanilla bike is.

**The vanilla motorcycle instead:** `build_bike_meshes.py` makes the same four nifs from it, and the clips are built
without `--fit`:

```
python tools\rider\riding_anims.py --pynifly %PYN% --vanilla %W% ^
    --body %W%\characterassets\malebody.nif --female-body %W%\characterassets\femalebody.nif ^
    --out %OUT%\Actors\Character\Animations\MT\CMB_Rider

python tools\rider\build_bike_meshes.py --pynifly %PYN% ^
    --model C:\CMBwork\meshes\setdressing\vehicles\motorcycle\motorcycle_clean.nif --out %OUT%\CMB ^
    --seat %OUT%\Actors\Character\Animations\MT\CMB_Rider
```

Here the meshes come second because the bike that hangs off the rider needs to know where the seated rider sits.

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
on the seat, hands on the grips (exact, via IK), feet on the pegs, leaning forward more with speed and into turns
(the contact points come from `CMB_BikeFit.json` with `--fit`, otherwise they're the vanilla motorcycle's). At a
standstill the left foot goes down and the bike tips onto it. `verify_clips.py` checks all of that against the vanilla
files. `preview.py` renders still images if you want to look before going in game.

Two exceptions to "the same root motion". The 180° reversals while moving (`walk_to_walk_l180`/`r180`,
`run_to_run_l180`/`r180`) follow a leaning arc instead of vanilla's stop-and-spin, with the same length, total turn
and distance. And the hard landings (`JumpImpactLand`, `JumpRunImpactLand`) take the soft landing's timing when that
has the hard landing's events (`JumpDown`; foot-sync markers aside), so a drop doesn't stop you as long: in place
1.27 s instead of 1.77, running 0.5 s instead of 0.7 and straight into the run (`jumpEndToRun`). The female running
landing has no `JumpDown`, so the female hard running landing keeps its own 0.7 s. The jump, fall and landing clips are only built from the vanilla ones
(a guessed length could hold the rider in a landing): if they weren't extracted, `riding_anims.py` skips them and
jumps and landings show the standing clips. Those 11 are every clip the movement graph (`MTBehavior.hkx`) plays while
you're in the air, including the brief falls over bumps. Their timing can't come from the game's AnimTextData
instead: it only keeps records for clips with root motion, and these have none.

**Which vanilla clip.** The player's holstered animations come from `MT\Player`, then `MT\Confident`, then
`MT\Neutral` (female: the `Female` subfolders of those first). That order was read off the game's own AnimTextData
(all 193 male and 191 female clip names agree), and each riding clip copies the timing of the clip the game would
otherwise play. Female clips go in `CMB_Rider\Female`.

`riding_anims.py` also writes `CMB_RiderClips.json` next to the clips: their root motion and events in the form the
game's AnimTextData uses (checked against the Creation Kit's own output for 80 vanilla clips: within 1 unit and
0.6°).

**Weapon drawn.** There are no riding clips for that: with combat allowed (`CMB_AllowCombat 1`), drawing a weapon
while riding shows the normal standing weapon poses. Getting on with a weapon out is refused. The game also has no backwards or sideways clips with the weapon holstered.
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
