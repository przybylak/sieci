# Assets: bike meshes, riding animations, rider-pose plugin

The mod's bike is Nieve5677's **Harley-Davidson Iron 883** ([Sketchfab](https://sketchfab.com/3d-models/harley-davidson-iron-883-2015-612071b783f14a7288df2d361be9a244),
CC-BY-4.0) standing on Fallout 4's own motorcycle's collision, and the riding animations are the mod's own. The
vanilla motorcycle can be used instead. **None of it is in this repository**: the meshes mix the model with
Bethesda's collision and the clips are derived from Bethesda's files. The tools in `tools/rider` build it on your PC
from your own copy of the game and the downloaded model:

| File (under `Data\`) | Built by | What it is |
|---|---|---|
| `Meshes\CMB\CMB_BikeParked.nif` | `harley_meshes.py` (`build_bike_meshes.py` for the vanilla bike) | the vanilla motorcycle nif with its own shape hidden and the model's 27 shapes added, `CMB_Bike_<label>` (30 since the 2026-11-07a build: the badge split in three and the rear fender's badge patch, and the two under-bar mirrors no longer hidden by their node flag but naming invisible materials; 25 in the 2026-10-31a build, before the brake discs were shapes of their own; twelve from test 38 to 27c, nine before; the two under-bar mirror styles among them hidden by their node flag; not the tail and brake lights' shells nor the dial's backlight, which only light on the riding bike), so its collision is kept; it keeps its sun shadow whole (the no-shadow flag below is the worn nifs' alone: test 35 found the parked bike's front end shadowless too) |
| `Meshes\CMB\CMB_BikeWornRider.nif`, `CMB_BikeWornRiderF.nif` | `harley_meshes.py --seat` | the same model as wearable armor: faces forward, seat over the origin, hanging off the rider's `COM` bone (male and female seat heights); no light nodes since test 32 (the game keeps only a skinned nif's shapes; the beam is a light the controller places, kept at the lens by `CMB_Slope.dll`); the bar assembly's, the lower fork's and front wheel's shapes cast no shadow (test 34: the bike shadowed its own headlamp; the worn nifs only), the lower fork (the sliders, front mudguard, caliper, axle and boots: three `_fork` shapes) rides with the front wheel's suspension travel since test 38, and the bar assembly takes the grips, levers, switch housings and the left mirror since test 35 (they sit 45 to 57 behind the steering head and stayed with the frame while the bars turned) |
| `Meshes\CMB\CMB_BikeWorn.nif` | `harley_meshes.py` | the same again (shapes, shadow flag and bar assembly), skinned to the `AnimObjectA` bone on the ground: used when the rider isn't seated |
| `Meshes\CMB\CMB_BikeView.nif` | `harley_meshes.py` (`--view 0` leaves it out) | since the 2026-11-01a build: the bike in first person, where the game hides the worn bike with the rest of the player's third-person 3D. The worn nif's 30 shapes with the same vertices (in full precision, as the parked nif's), materials and shadow flags, unskinned, named `CMB_BikeView_<label>` under one NiNode `CMB_BikeView` hidden by its flag bit 0 (without `CMB_Slope.dll` a placed copy shows nothing), no collision. The controller places it (the `CMB_BikeView` MovableStatic) and the plugin shows and moves it in first person (DESIGN.md) |
| `Meshes\CMB\CMB_BikeFit.json` | `harley_meshes.py` | where the bike's seat, grips, pegs and steering axis are, for the riding clips (`riding_anims.py --fit`); the grip centre at (29.4, -10.7, 96) since test 38 (`--grip 29.4,-10.7,96`, the rubber sleeve's centre by a fit of its vertices; test 34's 24.5,-15,98 put the hands on the lever perches, and 20 on the lever clamps) |
| `Meshes\CMB\CMB_BikeParts.ini` | `harley_meshes.py` | the axles, wheel radius, steering axis, `FrontMinY` (the line between the fixed shapes' culling spheres and the bar assembly's and lower fork's, halfway between the nearest two, 31.3 since test 38; it comes out of each build's shapes, so the grips joining the assembly in test 35 needed nothing of the plugin), `Grip` (the +x grip's centre in the worn bike's space, the fit's grip_r, 29.4, 38.39, 96.0: the wrist roll's pivot since test 39) and the headlamp's lens for `CMB_Slope.dll`, which spins the wheels, turns the bars and places the lamp's light (install it with the meshes); since the 2026-10-31a build also the speedometer's needle (`NeedlePoint`, `NeedleAxis`, `NeedleZero`, `NeedleMax`, `NeedlePerMph`: without them the needle is never turned), and `FrontMinY` 31.7 (31.3 in 27c); every other key as 27c's |
| `Textures\CMB\Bike\<mat>_d.dds`, `_n.dds`, `_s.dds`, `_g.dds`; `mirror_cube_e.dds`, `mirror_cube_zup_e.dds` | `bike_textures.py` (`build_bike.sh`'s `textures` stage) | since the 2026-10-31a build: one texture set per material on the shape's own UV atlas, baked from the full model and authored procedurally (DESIGN.md, *The bike's look*); the mirrors' sky (the zup file the same sky with +Z up, a one-file swap if the game shows it sideways), since the 2026-11-02a build only in the optional "2026-11-01a look (A-B)" folder: the mirrors name the game's `Shared\Cubemaps\MetalBrushed02Cube_e.dds`, and a cube of ours is written only if a material names it. 91 files, 86.6 MB since the 2026-11-02a build (93 and 88.6 in the 2026-11-01a build, 90 and 85.3 in the 2026-10-31a build): 30 materials, the needle's its own (the dial's art and a glow map on the blade), the two brake discs on one set, `wheelF_disc_*` (`bike_art.py`'s disc art; the rear disc's material names the front's textures, `"textures_of"`). 27c's three palette textures directly in `Textures\CMB` (`*_d.dds`, `_n`, `_s`: one colour block per part) are no longer used; `--uvs none` (the emergency build) writes that palette again as `Textures\CMB\CMB_Bike_d.dds`, `_n`, `_s` |
| `Materials\CMB\Bike\<mat>_worn.bgsm`, `<mat>.bgsm` | `bike_textures.py` (with `bgsm.py`) | since the 2026-10-31a build: a material file per material, the riding bike's (`_worn`: lit parts lit, no shadow from the bar assembly, lower fork and front wheel) and the parked bike's (shadows on, nothing lit; none for the two lights' shells and the dial's backlight, which the parked nif leaves out): 57 files (53 in the 2026-10-31a build). The meshes need them: the nifs name their material files, and the game shows a missing one as magenta (test 47; it doesn't fall back to the nif's own block) |
| `Textures\CMB\Bike\badges_d.dds`, `badges_n.dds`, `badges_s.dds` | `bike_art.py --badges` (the drawings, PNG) and `look_badges.py` (the DDS) | since the 2026-11-07a build: our own art, the 13 badges (Brotherhood of Steel, Brotherhood helmet, Enclave, Enclave helmet, Gunners, Minutemen, Railroad, Institute, Vault-Tec, Atom Cats, Raiders, Children of Atom, a pre-war army star) in one atlas, 4 x 8 cells of 512 x 256: `_d` BC3 2048 (alpha the outline), `_n` and `_s` BC5 1024, 8,389,072 bytes. Drawn from shapes (polygons, circles, rings, strokes, Bezier outlines, cogs, stars) in the stock badge's chrome and enamel: no source image, nothing traced or sampled from the game or anywhere else |
| `Materials\CMB\Bike\badge_<key>.bgsm` | `look_badges.py` | since the 2026-11-07a build: 17, one per badge, the stock badge's material with a UV scale and offset picking its atlas cell (ours, 13) or the game's textures by path (`gunners_g`, `army_g`, `minutemen_g`, `bosflag_g`: the "(game art)" options, below) |
| `Textures\CMB\Bike\static_paint_rf_d.dds`, `fork_paint_rf_d.dds`, `paint_p.dds` | `look_paint.py` | since the 2026-11-07a build: the paint's Restored index maps (2048 and 1024, BC1: each texel's part and shade as a grey, mips per part) and the palette (256 x 64, A8R8G8B8, one mip: 43 rows of `look_options.json`'s colours, rows 43-63 copies of row 42); ours, computed from the 2026-11-06a paint |
| `Materials\CMB\Bike\static_paint_rf<rr>.bgsm`, `..._worn.bgsm`, `fork_paint_rf<rr>.bgsm`, `..._worn.bgsm` (rr 00-42, and `_rftest`) | `look_paint.py` | since the 2026-11-07a build: 176, the 2026-11-06a paint materials pointed at the index map and the palette row (row + 0.5) / 64; Factory is 2026-11-06a's own files |
| `Materials\CMB\Bike\static_badgeTankL`, `static_badgeTankR`, `static_badgeRear` (`.bgsm`, `_worn.bgsm`); `off.bgsm`, `static_badgeFender(.bgsm, _worn.bgsm)`, `front_mirrorUnderEgg_off.bgsm`, `front_mirrorUnderD_off.bgsm`; `Textures\CMB\Bike\off_d.dds`, `off_n.dds`, `off_s.dds` | `look_paint.py` | since the 2026-11-07a build: the split badge's three shapes (2026-11-06a's `static_badge(.bgsm, _worn)` byte for byte, which are gone from the tree) and the five invisible materials (alpha test 255, alpha 0, no shadows; the fender patch's with decal on) over 4 x 4 textures; the build then has 100 DDS and 259 BGSM |
| `Meshes\Actors\Character\Animations\MT\CMB_Rider\*.hkx` and `...\CMB_Rider\Female\*.hkx` | `riding_anims.py` | seated riding versions of the holstered walk/run/turn/start/stop/idle clips (the arms' IK pole mostly down since test 39, (0.35, -0.3, -1.0) in the rig's root space, the left mirrored in x; before, (1, -0.6, -0.7), mostly sideways, which put the elbows out at shoulder height; the hand's frame from the forearm since test 40, its long axis along it seen along the grip, `HAND_PITCH` degrees above it, 0: before, a fixed frame, the wrists bent down 30 degrees in the cruise pose, test 39's "cat paw"), and of the jump/fall/land clips when those were extracted |
| `...\CMB_Rider\CMB_RiderClips.json` (and `Female\`) | `riding_anims.py` | each clip's root motion and events, for the step below |
| `...\CMB_Rider\CMB_RiderSeat.json` (and `Female\`) | `riding_anims.py` | where the seated rider's `COM` bone sits, for the bike that hangs off it |
| `CMB_RiderPose.esp` + `Meshes\AnimTextData\...` | `make_rider_pose.bat` | small plugin that makes the game use those clips while you ride, and the animation data it needs. Built from your load order; no Creation Kit |
| `Meshes\CMB\CMB_Keys.nif` (optional) | you: copy any vanilla key mesh | 3D preview of the keys in the Pip-Boy |
| `Sound\FX\CMB\CMB_FxWaterRoadLP.wav` | `tools/sound/make_water_loop.py` (`run_all.sh`'s optional `WATER=<example.wav>` stage) | since the 2026-11-06a build: the mod's own wet-road water loop, named by `CMB_FxWaterRoadLPSD` (0x8A9; the MCM's "Water sound loop" 2, the default): 7.90 s, 44.1 kHz mono 16-bit, -23 dB A-weighted, made from "Cars driving on a wet road 3" by freesound_community (Pixabay, 101246), under the Pixabay Content License: three stretches cut, filtered, re-levelled and looped into a file of our own. That licence allows the sound inside a project such as this mod, not on its own, so the recording (and anything decoded from it) is in neither this repository nor the package, only the loop inside the mod; the credit is README's. Decode the mp3 with ffmpeg in a folder of its own, then `python3 -I -B tools/sound/make_water_loop.py --ex1 <ex1.wav> --out <dir>` (numpy only; it checks the input is 24 kHz stereo 11.98 s and the loop's wrap, band shares and level, 8 checks, and a second run is byte-identical) |

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
- For the textured build (since the 2026-10-31a build): **Blender as a Python module** (`pip install bpy` into its own Python:
  this build's came from bpy 5.1 on Python 3.13) for the texture stage, a Python with **numpy, quicktex and etcpak** for the DDS
  encoder (`write_dds.py`; Pillow too, and `texture2ddecoder` for `bike_textures.py --sheet`), `texture2ddecoder` in Blender's Python for the previews
  (`look_render.py`), and a bash shell for `build_bike.sh` (Git Bash or WSL on Windows). Its other stages run `python3`, or the Python
  `PYTHON` names (`PYTHON=python` or `PYTHON="py -3"` in Git Bash, where a python.org install has no `python3`), with
  `-I`, which leaves out the user's site-packages: numpy and fast_simplification must be in that Python itself, not
  installed with `pip install --user`.

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
to, say, `C:\CMBwork\model`. It's CC-BY-4.0: the credit in the README goes with anything you share.

## 3. Meshes and clips

```
set PYN=C:\Tools\PyNifly\io_scene_nifly
set W=C:\CMBwork\meshes\actors\character
set OUT=<repository>\Data\Meshes
set TEX=<repository>\Data\Textures
set BIKE=python tools\rider\harley_meshes.py --pynifly %PYN% --gltf C:\CMBwork\model\scene.gltf ^
    --vanilla C:\CMBwork\meshes\setdressing\vehicles\motorcycle\motorcycle_clean.nif ^
    --out %OUT%\CMB --textures %TEX%\CMB

%BIKE%

python tools\rider\riding_anims.py --pynifly %PYN% --vanilla %W% ^
    --body %W%\characterassets\malebody.nif --female-body %W%\characterassets\femalebody.nif ^
    --out %OUT%\Actors\Character\Animations\MT\CMB_Rider --fit %OUT%\CMB\CMB_BikeFit.json

%BIKE% --seat %OUT%\Actors\Character\Animations\MT\CMB_Rider

python tools\rider\verify_clips.py --pynifly %PYN% --vanilla %W% --clips %OUT%\Actors\Character\Animations\MT\CMB_Rider
python tools\rider\verify_clips.py --pynifly %PYN% --vanilla %W% --clips %OUT%\Actors\Character\Animations\MT\CMB_Rider\Female --female
```

Three steps because each needs the one before: the first `harley_meshes.py` run measures the model and writes
`CMB_BikeFit.json` (its seat, grips and pegs); the clips are posed to that; and the second run makes the two bikes
that hang off the seated rider, which need the seat height the clips settled on (`CMB_RiderSeat.json`). Generating
the clips takes a while (around 25 minutes for both sets).

`harley_meshes.py` takes `--body <hex>` for the tank and fenders' colour in the palette build (default a deep red,
`7a1118`; the textured build's paint is the `paint` surface's `colour` in `tools/rider/bike_materials.json`), `--tris`
for the triangle budget the pieces' shares are cut from (default 90000; each piece's share by its area is the
simplifier's target, and a piece that can't reach it without losing its shape keeps more, so the bike comes out at
about 225,000 triangles), `--sit` for how far back on the seat the rider sits (0.27 of the seat's length from its
front: snug behind the tank, where the arms still reach the turned bars) and `--bar-angle` for how far the bars turn
(20 degrees; 0 writes `BarAngle=0`, and the plugin turns nothing). Since the 2026-11-01a build the model comes out as 30 shapes
named by what they are and where they move (DESIGN.md, *The bike's look*; 28 in the 2026-10-31a build, before the brake
discs were shapes of their own; `--disc model` still makes those 28); up to 27c it came out as twelve: three fixed, four that turn
with the bars (metal, matte, glass and the headlamp's lit parts: the model's own lamp is dropped and a 5.75" LED unit lathed in its place), three of the fork's lower end (`_fork`: the sliders, front mudguard, caliper, axle and boots, which turn with the bars and ride with the front wheel's suspension travel; `FORK_SPLIT_Z`, 66 on the parked model, divides them from the tubes and clamps) and the two wheels, which the F4SE plugin moves (DESIGN.md); the plugin turns the rider's hands with the bars. The model is scaled to the vanilla bike's
length so the collision and the F4SE plugin's clearances still fit, which makes it about a quarter bigger than a
real bike next to the character, as the vanilla bike is.

The geometry since test 40: each connected piece of the model is cut down in one call of the simplifier with its
error capped (before, every piece was forced down to its share, which crushed the grips, speedo, switch housings,
cables and fork boots and left the rims 12-14-sided). Small pieces, the lenses, the painted panels and badges (cut
down, the rear fender's rolled lip turned to sawtooth teeth) and the small chrome (the fuel cap's dome reflected as
folds) are kept whole; the bar assembly and the big covers are cut finer (at the black parts' cap the mirror housings
poked through their glass, the master cylinder's lid swallowed its chrome ring and a flat bevel crossed the air
cleaner cover). The bolts and nuts under a centimetre across stay (they were dropped), a brake disc's bolts spinning
with it. Every corner shades by the glTF's own normal (at the nearest point of its piece where the piece was cut
down), with a vertex split where its corners' normals part, so hard edges stay hard and curves round (the averaged
normals smeared both, and cancelled to nothing where opposite faces were welded). A closed piece the simplifier
crushes (under 0.6 of its volume kept) is cut again at twice its share till it keeps 0.8, the volume guard (since the
2026-11-01a build, `--volume-guard 0` for the 2026-10-31a cut; test 47: the seat's piping cord had been cut from 2,368
to 210 triangles, standing out of the seat as fins; with it two crushed closed pieces of the frame and the engine, 2,756
triangles more in all). The wheels' brake discs (dented in the model) were the model's, shaded by the averaged
normals, up to the 2026-10-31a build; since the 2026-11-01a build they are our own drilled discs (`--disc model` for
the model's), each a shape of its own on our art. The parked nif's positions are full precision; the worn nifs keep the vanilla
shape's half floats until one is tried in game. Each run takes about 40 s (the normals about 15 s of it), and the
largest shape, the fixed matte one, has about 48,600 of the 65,535 vertices a shape may have.

**The textured build (since the 2026-10-31a build).** The runs above (with no `--stage`) make the palette build, 27c's way, which
is all the clips need (`CMB_BikeFit.json`). The shipped bike then comes from `tools/rider/build_bike.sh`, in stages,
from a bash shell, its inputs in the environment:

```
PYNIFLY=C:/Tools/PyNifly/io_scene_nifly GLTF=C:/CMBwork/model/scene.gltf \
VANILLA=C:/CMBwork/meshes/setdressing/vehicles/motorcycle/motorcycle_clean.nif \
SEAT=<repository>/Data/Meshes/Actors/Character/Animations/MT/CMB_Rider DATA=<repository>/Data \
STAGE=C:/CMBwork/bike_stage BLENDER_PY=<a Python with bpy> DDS_PY=<a Python with quicktex and etcpak> \
REFERENCE=<a previous build's Meshes/CMB, optional> \
PYTHON=<a Python with numpy and fast_simplification, default python3> \
  bash tools/rider/build_bike.sh                       # = export art textures build check
```

`export` writes the finished shapes into the stage folder (`harley_meshes.py --stage export`, about a minute), `art`
our own art (the dial, the badge, the lens patterns, the mirrors' sky: `bike_art.py`, about 25 s), `textures` each
shape's UV atlas, the bakes from the full model, the DDS files and both material files per material (`bike_textures.py`
in Blender, about 28 minutes from scratch on four cores, seconds to minutes after a change; a per-label cache keeps what's done, and `ONLY=static_paint,static_chrome` does just those),
`build` the nifs with those UVs and the materials named (the parked and three worn ones, and since the 2026-11-01a
build `CMB_BikeView.nif`), `CMB_BikeParts.ini` and `CMB_BikeFit.json` (`harley_meshes.py --stage build`, about a
minute and a half; it refuses a stage made from different shapes), `check` reads everything back
(`check_bike_meshes.py`, about 15 s: exit 1 on any fault; with `REFERENCE` it also compares the parts file's keys and
the fit; with the stage it also checks the volume guard's work, the discs' fit and the mirror glass's colour). Since
the 2026-11-01a build `export` rewrites a shape's file only when the shape changed, so the texture stage's caches keep
the rest (a changed shape still re-keys the bakes of every label it occludes: this build's seat and discs needed the
full run, about 28 minutes in five `ONLY=` calls on four shared cores). `bash tools/rider/build_bike.sh fallback check` is the emergency build: the palette
textures (`Textures\CMB\CMB_Bike_*.dds`) and no material files, as 27c shipped. `MESH_ARGS` passes more arguments to
`harley_meshes.py` (`--tris`, `--bar-angle`, ...), `MATERIALS` another materials table (the default
`tools/rider/bike_materials.json` holds every surface's look and every shader value).

**The customisation's files (since the 2026-11-07a build).** `export` and `build` make the 33-shape nifs
(`MESH_ARGS="--look-slots 1"`, the default; `--look-slots 0` gives the 2026-11-06a build's 30 byte for byte). Three
steps after `build`, each with the DDS Python (quicktex, texture2ddecoder) and from the repository's root:

```
<DDS python> -I tools/rider/look_paint.py --data <Data> --base <2026-11-06a's Data> --stage <stage>      # then --check
python3 -I tools/rider/bike_art.py --badges --out <art folder>
<DDS python> -I tools/rider/look_badges.py --art <art folder> --out <Data>
<DDS python> -I tools/rider/look_badges.py --check --art <art folder> --out <Data> \
    --plate-npz <a --look-slots 0 stage>/shapes/static_badge.npz      # the one-shape badge's UVs, as 2026-11-06a's stage
```

`look_paint.py` writes the split badges' six materials (2026-11-06a's `static_badge` ones, which it removes), the five
invisible ones and their 4 x 4 textures, the paint's two index maps, the palette and its 176 materials; `--check` proves
the palette (2026-11-06a's colours as a row give its paint back, 39 dB), and that at every mip no texel's U is in a part
its footprint lacks, with the coachline kept at mips 1-3. `bike_art.py --badges` draws our 13 badges into
`badges_d/_n/_s.png` and `badges.json` (nothing else: a run without `--badges` is byte for byte as before);
`look_badges.py` writes the atlas's three DDS and the 17 `badge_<key>.bgsm` from the stock badge's material (its
template `static_badgeTankL.bgsm`, or `static_badge.bgsm` in a 2026-11-06a tree: the same bytes), all 17 with decal on
(the fender patch's depth bias; the tank plates share the files), and `--check` reads them back (`--sheet <png>` a flat
contact sheet of every badge on both plates and the fender). `check_bike_meshes.py` then takes `--look-options
tools/esp-generator/look_options.json` and, with the badges in, `--look-targets all` (every swap's target there).
`look_render.py --sheet all` renders every option of every slot on the parked, worn and preview frames (102 options x 3,
about 10 minutes; 64 transparent layers, `transparent_max_bounces`, since the parked bike's two overlapping invisible
under-bar mirrors rendered black past 8); `--swap Slot:key[,...]` one look. The option table, `look_options.json`, is
read only: the options and their files come from it.

To look before going in game, `tools/rider/look_render.py` renders the built bike as the game shades it (DESIGN.md,
*The bike's look*), in Blender's Python:

```
<a Python with bpy> -I tools/rider/look_render.py --pynifly C:/Tools/PyNifly/io_scene_nifly --data <repository>/Data \
    --out C:/CMBwork/renders --prefix after_ --views all           # or day, night, mirrors, close, lock, t49, or names
<a Python with bpy> -I tools/rider/look_render.py --compare C:/CMBwork/renders before_ after_ C:/CMBwork/renders/compare.png
```

Since the 2026-11-01a build it tints the cubes' reflections by the colour map, as the game does (`--env-albedo 1`, the
default: test 47's near-black mirror glass showed black in game and a sky in the 2026-10-31a previews, which added the
reflection untinted; `--env-albedo 0` is that old way), and the `t49` set holds test 47's close-ups: the tank's
coachline from both sides and its rear turn, the seat, both discs, the mirrors by day and at night.

**One optional MO2 folder** (since the 2026-11-02a build; the package carries it, off by default), a mod folder to
enable below the main one:
- *Commonwealth Motorbike - 2026-11-02a look (A-B)* (since the 2026-11-06a build): the 2026-11-02a build's bytes of
  every art file the 2026-11-06a build changes: the 16 BGSMs of the chrome's four materials and the rims' and discs'
  four, parked and worn, and the five nifs of `Meshes\CMB` (their shader blocks): 21 files, 43.5 MB (43,471,117 bytes),
  each equal to the 2026-11-02a package's. No texture changed, so none is in it. One restart shows test 49's look: the
  brighter, pearly chrome and the whiter discs and rims. No `CMB_BikeFit.json`, no `CMB_BikeParts.ini`: the packager's
  guard refuses them, and any file that isn't nif, dds, bgsm or bgem. **The 2026-11-07a package ships no optional
  folder**: this one's meshes have one badge and the parked under-bar mirrors hidden by their node flag, so with it
  ticked no badge, paint or mirror choice shows on the parked bike: untick it.

The 2026-11-02a package's folder, *Commonwealth Motorbike - 2026-11-01a look (A-B)*, is retired: the 2026-11-01a build's
bytes of every art file the 2026-11-02a build changed or dropped: the five nifs of `Meshes\CMB` (the disc bore, and the
chrome's and mirrors' shader values in their blocks), 21 DDS of `Textures\CMB\Bike` (the front disc's three, our mirror
cube and its +Z-up copy, and 16 maps whose baked occlusion moved a little with the new disc bore) and 14 BGSMs of
`Materials\CMB\Bike` (the four chrome materials' and three mirrors', parked and worn): 40 files, 70 MB. One restart
shows the whole 2026-11-01a look: the duller chrome, our own mirror sky, the light ring round the front disc's bore.

The 2026-11-01a package's two folders, "2026-10-31a look (A-B)" and "game mirror cube (A-B)", are retired (the build-48
check found the first shipped the build file `CMB_BikeFit.json`). Since the 2026-11-02a build the mirrors' materials
name the game's cube themselves (`bike_materials.json`: `"cube": "MB"`), the chrome's four materials are at env 6,
specular 2 with screen-space reflections, and the brake discs' bore is cut where the art paints it (`build_bike.sh`'s
`DISC_BORE=shared`); `"cube": "MR"`, env 1, specular 1, no `ssr` and `DISC_BORE=bolts` rebuild the 2026-11-01a build's
157 files byte for byte. `bike_textures.py --mirror-cube <path>` still writes the mirror materials with another cube.
Since the 2026-11-06a build (test 49: the chrome "too bright, pearly, smudged", the discs and rims too white) the
materials' fields are, from `bike_materials.json` (no texture changed):

| Materials (each parked and `_worn`) | Cube | Env (02a -> 06a) | Specular (02a -> 06a) | Screen-space reflections |
|---|---|---|---|---|
| static_chrome, static_exhaust, front_chrome, fork_chrome | CH (the game's `Shared\Cubemaps\MetalChrome01Cube_e.dds`) | 6.0 -> 2.5 | 2.0 -> 1.5 | on -> off |
| wheelF_rim, wheelR_rim, wheelF_disc, wheelR_disc | DI (`Shared\Cubemaps\mipblur_DefaultOutside1_dielectric.dds`) | 0.4 -> 0.25 | 1.0 -> 0.75 | off |
| static_badge | CH | 0.8 | 1.0 | off |
| the three mirrors | MB (`Shared\Cubemaps\MetalBrushed02Cube_e.dds`) | 2.0 | 1.0 | off |

`check_bike_meshes.py` checks them (`CHROME_ENV, CHROME_SPEC, CHROME_SSR = 2.5, 1.5, False`; `WHEEL_ENV, WHEEL_SPEC =
0.25, 0.75`), and with `--look-reference <the 2026-11-02a tree>` that the chrome's and the wheels' 21 maps are that
tree's.

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

**The hands.** Since test 40 each is turned about the grip's axis (the rig's x through the grip, so the palm stays on the
bar and the fingers keep their outward lean) till its long axis, seen along that axis, lies along the forearm (elbow
to wrist), `HAND_PITCH` degrees above it (0; + = the knuckles up, the wrist bent back). The long axis is the knuckle
line, from the hand's joint to the middle finger's first knuckle (`RArm_Finger31`, `LArm_Finger31`, 7.6 units off in
the vanilla skeleton's reference pose; `HAND_AXIS` in `riding_anims.py`), 5.8 degrees off the bone's x and, seen along
the grip, 4.8 above it: the same axis and the same measure as the F4SE plugin's `WristRoll` and `HandPitch`, so at 0
and 0 the plugin keeps the clips' wrists and turns a hand only as far as its own forearm swings from theirs. Test 39:
"cat paw", the fists bent down at the wrist: the hand had a fixed frame, the fingers 39 degrees below level whatever
the forearm did, so along the knuckle line the wrists were bent down 30 degrees in the cruise pose (27 for the CBBE
body) and 22 at the idle (21), and the plugin kept that bend (the first rebuild for test 40 laid the bone's x along the
forearm instead, which left the plugin rolling every hand 4.8 degrees knuckles-down). The turn moves the wrist (2.7
back and 2.6 down for the cruise pose's 34 degrees), so the arm is solved again to that wrist and the turn read off
the new forearm, three passes; on frame 0 the knuckle line ends within 0.1 degrees of the forearm in the cruise and
idle poses, and the build prints the most a set leaves ("hands along the forearms (HandPitch 0) to within N
degrees": up to 1.6 for a frame in the stops and starts, where the wrist comes to the arm's full stretch and the elbow
goes from bent to straight between passes). At the idle the arm is at full stretch, and the palm sits 0.9 off the bar
(1.1 for CBBE; 2.2 and 2.3 in test 39's clips). With `WristRoll` on, the plugin's `HandPitch` sets the hands in game
whatever the clips' `HAND_PITCH` is; kept equal, the hands look the same with `RiderHands=0` and before the plugin holds the rider.

Two exceptions to "the same root motion". The 180° reversals while moving (`walk_to_walk_l180`/`r180`,
`run_to_run_l180`/`r180`) follow a leaning arc instead of vanilla's stop-and-spin, with the same length, total turn
and distance. And the hard landings (`JumpImpactLand`, `JumpRunImpactLand`) take the soft landing's timing when that
has the hard landing's events (`JumpDown`; foot-sync markers aside), so a drop doesn't stop you as long: in place
1.27 s instead of 1.77, running 0.5 s instead of 0.7 and straight into the run (`jumpEndToRun`). The female running
landing has no `JumpDown`, so the female hard running landing keeps its own 0.7 s. While riding with the plugin's
`[Steer] LandSoft` (since the 2026-11-01a build) the hard landings aren't played at all: the game's hard landing events
reach the animation graph as the soft ones. Their seated clips stay for `LandSoft=0` and for a game the plugin can't
hook. The jump, fall and landing clips are only built from the vanilla ones
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
| the bike all magenta | `Materials\CMB\Bike` missing, or in a mod folder that isn't enabled: the meshes name their material files, and the game doesn't fall back to the nif's own values (test 47) |
| the mirrors plain grey, no sky in them | the game's `Shared\Cubemaps\MetalBrushed02Cube_e.dds` isn't reaching them: another mod replacing that cube, or an older `Materials\CMB\Bike` winning; our own cube was only in the 2026-11-02a package's "2026-11-01a look (A-B)" folder, retired since 2026-11-06a |
| bike pops out at screen edges | an old `CMB_BikeWorn.nif` with a small culling sphere; rebuild it |
| the old flat colours, no needle, no lit tail light, no mirror styles | an older `Meshes\CMB` wins (another mod folder, or 27c's files left in a later-loading one) |
| the bike blotchy or its colours on the wrong parts | `Textures\CMB\Bike` from another build than the meshes (their UV atlases belong together: build and install both) |
| riding: three mirrors at once, the brake light always lit, the needle at rest | no F4SE or no `CMB_Slope.dll`, or the log's role lines say "by its sphere" for the bike's shapes (their names didn't reach the plugin) |
| standing rider over the bike while riding | rider pose off, `CMB_RiderPose.esp` not active, or its AnimTextData missing (the mod folder from `make_rider_pose.bat` not enabled) |
| standing poses only with a crippled limb | an animation mod added player entries after the plugin was built: run `make_rider_pose.bat` again |
| rider seated but slides / clips misbehave | `AnimTextData` outdated: run `make_rider_pose.bat` again after rebuilding clips |

## Borrowed from the game

The game's own records our records name, by FormID (or, for the optional folder, by path), at runtime: nothing of the
game's is copied into the mod or overridden, so their categories, output models, conditions and sound files are the
game's own. Each is to be swapped for our own for a standalone mod (the right-hand column). The landing and water
sounds and the mute are the 2026-11-01a build's; the engine's category is test 44's:

| Referenced from | Slot or property | Role | EditorID | `Fallout4.esm` FormID | Replace with |
|---|---|---|---|---|---|
| `CMB_FxLandSounds` (FLST, FExxx890) | 0 | landing, light | `PHYRubberTireL` | 1D3313 | our own tyre thump (light) |
| | 1 | landing, heavy | `PHYRubberTireH` | 1D3312 | our own tyre thump (heavy) |
| | 2 | the clunk on a big drop | `PHYMetalAutoMediumH` | 05BAD7 | our own frame and suspension clunk |
| | 3 | into water | `FSTnpcWaterJumpDown` | 03C7A9 | our own splash |
| | 4 | into water, heavy | `PHYWaterSplash` | 0452CE | our own heavy splash |
| `CMB_FxLandSoundsAlt` (FLST, FExxx891; `set CMB_FxLandPick to 1`) | 0 | landing, light | `PHYRubberTireL` | 1D3313 | (as above) |
| | 1 | landing, heavy | `FSTArmorPowerHardLandingImpactDirt` | 20A0B9 | |
| | 2 | the clunk | `PHYMetalBarrelH` | 1A8550 | |
| | 3 | into water | `CWaterMedium` | 089380 | |
| | 4 | into water, heavy | `FSTArmorPowerHardLandingImpactWater` | 20A0B8 | |
| `CMB_FxWaterLoops` (FLST, FExxx892; `set CMB_FxWaterPick to 0`-`3`) | 0 | the water loop | `AMBWaterfallSplatterSmallLP` | 1E4F2D | our own spray loop |
| | 1 | | `AMBWaterfallSplatterLargeLP` | 1E4F2C | |
| | 2 | | `AMBWaterStream01LPSD` | 03D0A7 | |
| | 3 | | `AMBWaterfallChurn` | 1E4F1B | |
| the controller's `AudioCategoryFSTplayer` (SoundCategory) | muted while riding (MCM "Mute the rider's own jump and landing sounds") | the rider's own footstep, jump and landing sounds | `AudioCategoryFSTplayer` | 0F5FFC | our own riding clips without the footstep tags |
| the 13 engine sound descriptors (since test 44's build) | their category | the engine's volume class | `AudioCategorySFX` (SoundCategory) | 0172A1 | our own category |
| our output model `CMB_SOMMonoEngine` (FExxx871) | its values (copied, not referenced: test 45's answer) | the engine's attenuation and reverb | `SOMMono02000` (SoundOutputModel) | 07E5DC | (our own values already; listed as their source) |
| the mirrors' six material files' envmap (since 2026-11-02a, the main mod; by path) | the cube map | the mirrors' sky | `Shared\Cubemaps\MetalBrushed02Cube_e.dds` | (an archive path) | our own cube, `mirror_cube_e.dds` (the 2026-11-02a package's "2026-11-01a look (A-B)" folder, retired) |
| the controller, `set CMB_RiderSteadyWay to 2` (console; since 2026-11-02a) | the perk "Steady in the saddle" gives | one step less stagger, for the A/B | `mod_armor_LessStagger` (Perk) | 245AFE | (ours, `CMB_RiderSteadyPerk2`, is the default) |

Since the 2026-11-02a build these lists are the A/B: the controller plays the mod's own records below, and the MCM's
"Bike sounds through the mod's own records" off (`CMB_FxOwnSounds` 0) plays these, as the 2026-11-01a build did. Since
the 2026-11-06a build off is the game's own records for the landings only with "Landing sounds without metal" off, and
for the water only with "Water sound loop" on its first choice ("As the 2026-11-02a build (spray)"); for test 48's A/B,
turn all three to their 2026-11-02a values.

**The game's sound files our own records name by path (2026-11-02a).** 13 sound descriptors of the mod's own
(`CMB_Fx*SD`, FExxx89E-FExxx8AA), each but 8A9 (since 2026-11-06a the mod's own wet road) following the game's record in
the third column: the same files, in the order
its dump gives them, letter case kept, the same pitch and loudness variation, but static attenuation 0,
`AudioCategorySFX` and our output model `CMB_SOMMonoFx` (FExxx89D, the engine model's fields: full to 600, so heard at
the riding camera's 450). Nothing is copied: the game resolves those strings in its own archives (`Fallout4 -
Sounds.ba2`). Each file is to be replaced by our own for a standalone mod.

| Our record | Our list, slot | Follows (`Fallout4.esm`) | Files, by path | Replace with |
|---|---|---|---|---|
| `CMB_FxTyreLightSD` (89E) | `CMB_FxLandSoundsOwn` 0, `CMB_FxLandSoundsAltOwn` 0, `CMB_FxLandSoundsDull` 0 | `PHYRubberTireL` 1D3313 | `data\Sound\FX\PHY\RubberTire\PHY_Rubber_Tire_L_01.wav`, `_L_02.wav`, `_L_03.wav` | our own file |
| `CMB_FxTyreHeavySD` (89F) | `CMB_FxLandSoundsOwn` 1, `CMB_FxLandSoundsDull` 1 | `PHYRubberTireH` 1D3312 | `data\Sound\FX\PHY\RubberTire\PHY_Rubber_Tire_H_02.wav`, `_H_03.wav`, `_H_01.wav` | our own file |
| `CMB_FxClunkSD` (8A0) | `CMB_FxLandSoundsOwn` 2 | `PHYMetalAutoMediumH` 05BAD7 | `data\Sound\FX\PHY\MetalAuto\PHY_Metal_Auto_Medium_H_01.wav` to `_H_04.wav` | our own file |
| `CMB_FxSplashSD` (8A1) | `CMB_FxLandSoundsOwn` 3, `CMB_FxLandSoundsDull` 3 | `FSTnpcWaterJumpDown` 03C7A9 | since 2026-11-06a `Data\Sound\FX\FST\Player\Water\FST_Water_Jump_Down_01.wav`, `_02.wav` (the 2026-11-02a build's `...\FST\Water\Land\...` isn't in the game: the build-49 check; Q-W2 asks the game's own record for these) | our own file |
| `CMB_FxSplashHeavySD` (8A2) | `CMB_FxLandSoundsOwn` 4, `CMB_FxLandSoundsDull` 4 | `PHYWaterSplash` 0452CE | since 2026-11-06a `Data\Sound\FX\PHY\Generic\PHY_Generic_Water_Medium_01.wav`, `_02.wav`, `_03.wav` (`CWaterMedium`'s files, as 8A5; the 2026-11-02a build's `Data\Sound\FX\PHY\PHY_Water_M_01.wav` isn't in the game) | our own file |
| `CMB_FxThudHeavySD` (8A3) | `CMB_FxLandSoundsAltOwn` 1, `CMB_FxLandSoundsDull` 2 (the thud) | `FSTArmorPowerHardLandingImpactDirt` 20A0B9 | `data\Sound\FX\FST\ArmorPower\FST_ArmorPower_Land_3D_Dirt_02.wav`, `_03.wav`, `_01.wav` | our own file |
| `CMB_FxClunkBarrelSD` (8A4) | `CMB_FxLandSoundsAltOwn` 2 | `PHYMetalBarrelH` 1A8550 | `data\Sound\FX\PHY\MetalBarrel\PHY_Metal_Barrel_H_01.wav` to `_H_04.wav` | our own file |
| `CMB_FxSplashMediumSD` (8A5) | `CMB_FxLandSoundsAltOwn` 3 | `CWaterMedium` 089380 | `Data\Sound\FX\PHY\Generic\PHY_Generic_Water_Medium_01.wav`, `_02.wav`, `_03.wav` | our own file |
| `CMB_FxThudWaterSD` (8A6) | `CMB_FxLandSoundsAltOwn` 4, `CMB_FxLandSoundsDull` 5 (the water thud) | `FSTArmorPowerHardLandingImpactWater` 20A0B8 | `data\Sound\FX\FST\ArmorPower\FST_ArmorPower_Land_3D_Water_02.wav`, `_03.wav`, `_01.wav` | our own file |
| `CMB_FxWaterSprayLPSD` (8A7) | `CMB_FxWaterLoopsOwn` 0 | `AMBWaterfallSplatterSmallLP` 1E4F2D | `data\Sound\FX\AMB\Waterfall\AMB_WaterfallSplatter_Small_02_LP.wav`, `_Small_01_LP.wav` (a loop, pitch +15) | our own spray loop |
| `CMB_FxWaterSprayLargeLPSD` (8A8) | `CMB_FxWaterLoopsOwn` 1 | `AMBWaterfallSplatterLargeLP` 1E4F2C | `data\Sound\FX\AMB\Waterfall\AMB_WaterfallSplatter_Large_01_LP.wav`, `_Large_02_LP.wav` (a loop, pitch -15) | our own file |
| `CMB_FxWaterRoadLPSD` (8A9; `CMB_FxWaterStreamLPSD` up to 2026-11-02a) | `CMB_FxWaterLoopsOwn` 2; the MCM's "Water sound loop" 2 | (none: since 2026-11-06a the mod's own; it followed `AMBWaterStream01LPSD` 03D0A7, whose `fx\amb\water\exterior\amb_water_stream_01_lp.wav` isn't in the game) | `FX\CMB\CMB_FxWaterRoadLP.wav` (a loop; the package ships it: the first table) | (ours already) |
| `CMB_FxWaterChurnLPSD` (8AA) | `CMB_FxWaterLoopsOwn` 3 | `AMBWaterfallChurn` 1E4F1B | `data\Sound\FX\AMB\Waterfall\AMB_Waterfall_Churn_02_LP.wav`, `_Churn_01_LP.wav` (a loop) | our own file |

The sounds are candidates, not chosen by ear yet: `cqf CMB_ControllerQuest FxAudition 0` to `4`, `10` to `14` and `20`
to `23` play our own records, `100` more the game's (`100` to `104`, `110` to `114`, `120` to `123`), `-1` all of ours
and `-2` all of the game's, once the console is closed, at the bike effects volume; since 2026-11-06a `-3` the landings
as heard (the set in use: `CMB_FxLandSoundsDull`, 0x8B9, with the MCM's "Landing sounds without metal" on), small to
big, then two into water, and `22` the wet road (an instance id of 0 for one of ours means its file didn't resolve).
Beside these, the riding clips are built on your PC from the game's own clips (section 3), and the parked bike stands on
the vanilla motorcycle's collision (the table at the top).

**The customisation build's borrowed resources (2026-11-07a).** Every game file the customisation names, by path
(the game resolves it in its own archives) or by FormID: none is copied into the mod, the repository or the package.
For a standalone mod each is replaced by the right-hand column; our own drawings already exist for every "(game art)"
badge.

| Referenced from | Role | By path or `Fallout4.esm` FormID | Replace with |
|---|---|---|---|
| `CMB_FieldKit` (FURN, FExxx8CF), `CMB_FieldKitArmorKw` (8D0), `CMB_FieldKitBox` (MSTT, 8D2) | the field kit's toolbox | `SetDressing\Toolbox\Toolbox_Large.nif` | our own toolbox (a later build) |
| `CMB_FieldKitBench` (FURN, 8D1; the kit's mode 3 only) | the armour bench beside the bike | `Furniture\Workstations\WorkbenchArmor\WorkstationArmorB01.nif` | (our own toolbox makes it unneeded) |
| the three loose mods (MISC, 8D4-8D6) | the mirrors' parts | `Props\ModsPartBox\ModCrate.nif` | our own parts box (a later build) |
| `badge_gunners_g.bgsm` (tanks and fender) | "Gunners (game art)" | `Armor\CombatArmor\ChestDecalGunner_d.dds` | ours, `badge_gunners.bgsm` |
| `badge_army_g.bgsm` (tanks and fender) | "Pre-war army star (game art)" | `Armor\CombatArmor\ChestDecalStar_d.dds`, `Armor\CombatArmor\ChestDecal_n.dds` | ours, `badge_army.bgsm` |
| `badge_minutemen_g.bgsm` (fender only) | "Minutemen flag (game art)" | `SetDressing\Minutemen\FlagMinutemen01_d.dds`, `_n.dds`, `_s.dds` | ours, `badge_minutemen.bgsm` |
| `badge_bosflag_g.bgsm` (fender only) | "Brotherhood flag (game art)" | `SetDressing\BOSFlag01_d.dds`, `_n.dds`, `_s.dds` | ours, `badge_bos.bgsm` |
| our 13 `badge_<key>.bgsm` | the chrome's shine, as the stock badge's | `Shared\Cubemaps\MetalChrome01Cube_e.dds` | our own cube |
| the furnitures' keywords | the armour bench's menu, third person, its idle, the actor's scale; the workbench type | `WorkbenchArmor` 0657FF, `FurnitureForce3rdPerson` 0A56D8, `AnimFurnWorkbenchArmorA` 14D04F (the bench's hammering idle), `FurnitureScaleActorToOne` 12F848, `Workbench_General` 091FD4 | (the game's own behaviour: kept) |
| the controller's links | a settlement's workshop and the side bag as the bench's components | `WorkshopItemKeyword` 054BA6, `LinkedWorkbenchContainerKeyword` 1D1BEF; `LocTypeWorkshopSettlement` 083C9A, the quest `WorkshopParent` 02058E, the actor value `WorkshopPlayerOwned` 00033C | (kept) |
| the loose mods | their type and the inventory's turn | `ObjectTypeLooseMod` 135C17; the transform `MiscMod01` 248769 | (kept) |
| the controller | the toolbox's lid | the sound `DRScToolboxBOpen` 1B0652 | our own sound |
| the 102 recipes | the costs; the colours' perk | the components `c_Adhesive` 01FAA5, `c_Cloth` 1223C7, `c_Oil` 01FAB4, `c_Steel` 01FABD, `c_Glass` 01FAA4, `c_Screws` 03D294; the perk `Armorer01` 04B254 | (kept) |

Everything else the customisation ships is ours: the 13 badges (above: drawn from shapes, no source), the atlas, the
palette and the index maps (computed from our own 2026-11-06a paint), the 187 materials files of `look_paint.py` and the
17 of `look_badges.py`. Our badges add no credit line. The badges and the paint schemes are named for the game's own
factions and fictional brands (the Brotherhood, the Minutemen, Vault-Tec, Nuka-Cola, Red Rocket and the others), drawn
as our own art.

## Background: why custom clips

The game has no motorcycle riding animations to borrow. `Fallout4.esm` does contain a keyword called
`AnimsMotorcycle` (`000AB732`), but nothing uses it, and the animation archives hold no motorcycle clips. The only
motorcycle assets are the two parked-bike models (the rusted `Motorcycle01` and the clean pre-war
`Motorcycle01_Prewar`). Open Animation Replacer isn't needed, and this doesn't use it: the subgraph system above is
the game's own way of swapping animation folders.
