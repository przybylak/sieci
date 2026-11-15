# The development toolchain (`tools/dev`)

The plugin build, the test harness, the Papyrus compiler, the ESP generator, the packager and the asset tools need
a toolchain that lives outside the repository, in `$CMB_ROOT` (default `/opt/cmb`). When the container is replaced,
everything outside the repository is lost; `setup_tools.sh` rebuilds it from this folder and the network (apt, the
package index, the NuGet feed, the upstream git repositories). It needs nothing from the user and no secrets.

| In this folder | What it is |
|---|---|
| `setup_tools.sh` | rebuilds `$CMB_ROOT` (below) |
| `cmb/` | the helper files, laid out as `$CMB_ROOT`: `setup_tools.sh` installs each at the same relative path |
| `requirements/<env>.txt` | the exact packages of the three Python environments (`uv pip sync`) |

## Rebuilding everything

On a new container, the environment's setup script runs the core from the folder that holds the checkout (`sieci`):
`[ ! -f sieci/tools/dev/setup_tools.sh ] || bash sieci/tools/dev/setup_tools.sh` (a checkout of a commit before
`tools/dev` existed is skipped; under a minute on top of the apt install, a second when everything is there).

```
bash tools/dev/setup_tools.sh [--assets] [<repository>]       # as root; from the repository root or anywhere
CMB_ROOT=/opt/cmbtest bash tools/dev/setup_tools.sh           # another root (a test, or a second toolchain)
```

The default is the core: the plugin build, the harness and its queue, the Papyrus compiler, the ESP generator and
the packager. `--assets` adds the asset tools of `tools/rider` (about 2.5 GB with their caches). `<repository>` is the
checkout whose `build-caprica.sh` and ESP generator are used (default: the one the script is in); the helper files
and the pins always come from the script's own folder. Every step prints one line; a step whose result is already
there skips itself, so a second run prints "already" lines and takes a second. A failing step prints why and the end
of its log, and the script exits 1. Each step's whole output is in `$CMB_ROOT/setup-logs/<step>.log`.

| Step | What it does | Skipped when |
|---|---|---|
| `apt` | installs what is missing of: `cmake clang ninja-build libboost-filesystem-dev libboost-program-options-dev libboost-container-dev dotnet-sdk-8.0 gcc-mingw-w64-x86-64 wine wine64 util-linux` (and `git make python3 ca-certificates`, which the image has); checks wine64, flock, setsid, unshare | every package is installed |
| `helpers` | copies `cmb/` into `$CMB_ROOT` (a changed file is put in place with `mv`, the old one kept as `<file>.prev`); makes `bin build tmp logs wt` | every file is the same |
| `caprica` | `CAPRICA_WORKDIR=$CMB_ROOT/caprica bash tools/syntax-check/build-caprica.sh` | the binary is there, at build-caprica.sh's `COMMIT` |
| `f4se` | clones F4SE at v0.7.9 into `$CMB_ROOT/native/f4se` and checks the commit | the clone is at that commit |
| `generator` | `dotnet restore` and `dotnet build -c Release` of `tools/esp-generator` into its `bin/out` (in the checkout, ignored by git), with no build server left running | `bin/out/EspGenerator.dll` is newer than the sources and the packages are in the NuGet cache |
| `uv` (assets) | uses `uv` from `PATH`, else installs uv 0.11.32 into `$CMB_ROOT/uvenv` | a uv is there |
| `ddsenv`, `meshenv`, `bpyenv` (assets) | `uv venv -p 3.13` and `uv pip sync requirements/<env>.txt` | the environment holds exactly the pinned packages |
| `pynifly`, `nifly` (assets) | clones each at its pinned commit (PyNifly at depth 1) | the clone is at that commit |
| `niflydll` (assets) | builds the Linux NiflyDLL (below), copies it into PyNifly and makes the two skeleton links | the library and both links are there |

A new clone is made in a new empty folder (`<dir>.part`) and moved into place only once it is checked out at the
pinned commit, so a clone cut off half way is never taken for a finished one. `NUGET_PACKAGES` and `UV_CACHE_DIR`
are honoured (default `~/.nuget/packages`, `~/.cache/uv`: outside the repository, so also lost with the container).

Timings, on four cores beside two harness runs, with everything downloaded afresh (empty NuGet and uv caches) but the
apt packages already installed: the core 37-46 s (Caprica 20-22 s, the generator's restore and build 16-20 s),
`--assets` 91 s (the three environments 10-25 s, the PyNifly clone 28-34 s, the NiflyDLL build 38-42 s). The apt step
on a bare image adds the download and install of those packages.

## What lives in `$CMB_ROOT`

| Where | What | Made by |
|---|---|---|
| `hrun.sh`, `hall.sh`, `hrun_selftest.sh` | the harness queue, a whole-pass driver and the queue's self-test (below) | `helpers` |
| `harness.1.lock`, `harness.2.lock`, `heavy.lock`, `tmp/`, `logs/` | the queue's slots, its snapshots and its default logs | `hrun.sh` |
| `bin/pecmp.py` | says whether two PE32+ images differ only by their image base | `helpers` |
| `bin/build_at_base.sh`, `bin/basewrap/x86_64-w64-mingw32-gcc` | the plugin built at HEAD's image base (below) | `helpers` |
| `build/` | build_at_base.sh's scratch | `helpers` |
| `tools/espcmp.py` | two plugins compared record by record (below) | `helpers` |
| `tools/nifly_selftest.py`, `dds_roundtrip.py`, `plates_digest.py`, `bpy_selftest.py` | the asset tools' self-tests (below) | `helpers` |
| `scratch/safe_unzip.py` | `safe_unzip.py <zip> <folder>`: extracts only when no member leaves the folder and none is a link | `helpers` |
| `scratch/merge_union.py` | `merge_union.py <file>...`: resolves merge conflicts in run.sh by uniting both sides (a `DEF5n='...'` line gets both sides' keys; otherwise ours, then theirs past the lines both start with) | `helpers` |
| `caprica/src/build/Caprica/Caprica` | the Papyrus compiler | `caprica` |
| `native/f4se` | F4SE 0.7.9's sources: the stub audit's real Papyrus sources | `f4se` |
| `ddsenv`, `meshenv`, `bpyenv`, `uvenv` | the Python environments of the asset tools (and uv, when the machine has none) | `ddsenv` ... |
| `pynifly`, `native/nifly` | PyNifly and the nif library it is built from | `pynifly`, `nifly` |
| `native/niflydll-linux` | our CMakeLists.txt and shim/ for the Linux NiflyDLL, and its `build/` | `helpers`, `niflydll` |
| `wt/` | worktrees to build and test in (never the user's own checkout) | `git worktree add` |
| `setup-logs/` | each setup step's output | `setup_tools.sh` |

Not made by the setup, because they come from the user: the asset base (the previous package's Data folder, for
`tools/package`), the model's glTF, the game's files. See the end of this file.

The shell helpers read `CMB_ROOT` (default `/opt/cmb`) wherever the original had `/opt/cmb` written in; with
`CMB_ROOT` unset or `/opt/cmb` they do exactly what the originals did. The Python files and the NiflyDLL files have
no such path: their code is the originals' (a few comments are reworded).

## Versions

| What | Pin | Check |
|---|---|---|
| apt (24.04 noble) | gcc-mingw-w64-x86-64 13.2.0-6ubuntu1+26.1 (`x86_64-w64-mingw32-gcc -dumpversion`: 13-win32), binutils-mingw-w64-x86-64 2.41.90.20240122, wine/wine64 9.0~repack-4build3, clang 18.1.3, cmake 3.28.3, ninja 1.11.1, boost 1.83, dotnet-sdk-8.0 8.0.134, util-linux 2.39.3 | whatever the archive has; the `apt` step prints them |
| Caprica | github.com/nikitalita/Caprica 9cd6d32ec2750adae329e81f7276dac95251e000 + tools/syntax-check/caprica-linux.patch | the binary's sha256 bdd30a1a8b9262ad..., the same from a rebuild in another root |
| F4SE | github.com/ianpatt/f4se tag v0.7.9 = 4692e9bba0f87d8b8d1a0b79110bf212f2b2ada7 (CURRENT_RELEASE_RUNTIME 1.11.240) | scripts/vanilla: 103 .psc and a flags file; scripts/modified: 29 .psc |
| the ESP generator's package | `EspGenerator.csproj`'s one PackageReference, 0.53.1 (and what it pulls: 39 packages, 167 MB in the NuGet cache) | `dotnet restore` |
| uv | 0.11.32 (only installed when the machine has none) | |
| Python | 3.13.18 (the image's; `uv venv -p 3.13`) | |
| ddsenv | pillow 13.0.0, numpy 2.5.4, etcpak 0.9.15, quicktex 0.3.1, texture2ddecoder 1.0.6 (+ archspec, click): `requirements/ddsenv.txt` | the versions that reproduce the shipped textures byte for byte |
| meshenv | numpy 2.5.4, fast-simplification 0.2.0, matplotlib 3.11.2 (+ 9 dependencies): `requirements/meshenv.txt` | |
| bpyenv | bpy 5.1.2 (ec6e62d40fa9, 2026-05-19), numpy 2.5.4, texture2ddecoder 1.0.6 (+ 10 dependencies): `requirements/bpyenv.txt` | a 373 MB wheel, about 900 MB installed |
| PyNifly | github.com/BadDogSkyrim/PyNifly tag V30.3.0 = ac3c1453a5efa44f580033205ecaf5be9a005eed (`bl_info` and the library say 30.2.0) | |
| nifly | github.com/BadDogSkyrim/nifly at main's 8b43aaa022c4dec8edd0985630cb101ea9785d92 | |
| NiflyDLL (Linux) | clang 18.1.3, cmake 3.28.3, ninja 1.11.1 over the two checkouts above | sha256 be373e5ead3003d759fdca1692d28874964e91bab8d97b2fa305400058cf77ca, the same from three builds in two roots |

Why these: bpy's Linux wheels are cp313 from 5.1.0 on (5.0.x and 4.5.x are cp311); docs/ASSETS.md says the shipped
textures came from "bpy 5.1 on Python 3.13", and 5.1.2 is the last 5.1 (an unpinned install gives a later minor).
PyNifly's main is past the tag and rewrites `hkx/anim_fo4.py`, whose private functions `riding_anims.py` calls, so the
tag. The nifly pin is the commit main was at when the library was first built here.

## Scripts: the compiler, the generator, the plugin compare

```
# the generator and every check (rewrites the ESP, config.json, keybinds.json and tools/rider/template/CMB_RiderPose.esp
# in place: run it in a worktree and look at git status after)
CAPRICA=$CMB_ROOT/caprica/src/build/Caprica/Caprica bash tools/build.sh
#   -> "checked cmb_controllerscript: 194 properties" ... "plugin and scripts agree", 4 "ok" lines (1bc3f8a);
#      git status --porcelain --untracked-files=all prints nothing: the outputs are the committed bytes

# the 12 scripts compiled (Caprica writes the game's .pex format)
PEX_OUT=<folder> CAPRICA=$CMB_ROOT/caprica/src/build/Caprica/Caprica bash tools/syntax-check/check.sh
#   -> 4 "ok" lines, "pex   12 compiled scripts in <folder>", no warning. Two compiles of a script differ from byte 9
#      on (the compile time), nowhere else.

# the stubs against F4SE's real Papyrus sources
python3 -I tools/syntax-check/audit_stubs.py $CMB_ROOT/native/f4se/scripts/vanilla $CMB_ROOT/native/f4se/scripts/modified
#   -> "0 problem(s)"; two "unaudited" lines for stubs/vanilla/soundcategory.psc (Mute, UnMute): F4SE's folders have
#      no SoundCategory.psc, as audit_stubs.py's NO_SOURCE_HERE says

# an older build's plugin (docs/BUILD_GUIDE.md): fdb5b3a's Data/ files byte for byte
dotnet tools/esp-generator/bin/out/EspGenerator.dll --look-build 2026-11-07a <folder>/CommonwealthMotorbike.esp
git show fdb5b3a:Data/CommonwealthMotorbike.esp | cmp - <folder>/CommonwealthMotorbike.esp
#   -> no output; the same for <folder>/MCM/Config/CommonwealthMotorbike/{config,keybinds}.json

# two plugins record by record (by FormID; GRUPs, zlib-compressed records, XXXX subrecords; standard library only)
git show 1712b81:Data/CommonwealthMotorbike.esp > <old.esp>; git show c716330:Data/CommonwealthMotorbike.esp > <new.esp>
python3 -I $CMB_ROOT/tools/espcmp.py <old.esp> <new.esp> [--list]
#   -> "TES4: HEDR records 1043 -> 1045, next ID 0xBF5 -> 0xBF7", "added 2 (000BF5-000BF6): 2 GLOB", "removed 0",
#      "changed 3": 000BF1 GLOB CMB_Caution: FLTV; 000BF4 GLOB CMB_LookOptions: FLTV; 00080D QUST CMB_ControllerQuest: VMAD
#   353d8de against 1bc3f8a: "TES4: same", "added 0", "removed 0", "changed 2" (000BF9 GLOB CMB_KitPrevSize: FLTV,
#   000BFE GLOB CMB_KitPrevZoomIn: FLTV). --list names each added/removed record and shows the differing bytes.
#   Exit 0 when both files parse (different or not), 2 on a usage or parse error.
```

## The harness: the plugin build and its test under Wine

The plugin is built with MinGW-w64 (`tools/f4se-slope/build.sh`: `-std=c11 -O2 -Wall -Wextra -Werror`, about 15 s, no
warning) and tested by `tools/f4se-slope/test/run.sh` (26 modes) against a fake game under Wine. wine64 is
`/usr/lib/wine/wine64`, not on `PATH` (run.sh finds it); "wine32 is missing" notes are harmless.

```
git -C <checkout> worktree add $CMB_ROOT/wt/<name> <commit> --detach      # a worktree to build and test in
bash tools/f4se-slope/build.sh                                            # git status: M the DLL (the image base)
python3 -I $CMB_ROOT/bin/pecmp.py Data/F4SE/Plugins/CMB_Slope.dll <HEAD's DLL from git show>
#   -> "... ImageBase 0x34fe90000 ... ImageBase 0x261f30000 ... differing bytes: 989
#       ONLY THE IMAGE BASE: ... 5 header bytes (ImageBase/CheckSum) + 984 bytes in 328 relocated 8-byte pointers"
#      (1bc3f8a in $CMB_ROOT/wt/dev)
$CMB_ROOT/bin/build_at_base.sh <worktree> [<base>]                       # the same source at HEAD's image base
#   -> "image base 0x261f30000" ... "differing bytes: 0", "IDENTICAL"; git status --short prints nothing
```

**The image base.** MinGW's ld gives a DLL without `--image-base` a base hashed from the `-o` path as written, and
build.sh writes `$HERE/../../Data/F4SE/Plugins/CMB_Slope.dll`, so the checkout's absolute path decides it:
0x261f30000 at `/home/user/sieci` (1bc3f8a's committed DLL has that base), 0x34fe90000 in `/opt/cmb/wt/dev`,
0x21c5e0000 in `/opt/cmb/wt/base`; other builds' committed DLLs have other bases (c716330 0x3b65c0000, 1712b81
0x359930000, a02f9d9 0x1c5ca0000). Apart from the base (the header's ImageBase and CheckSum, and every relocated
pointer, each off by exactly the bases' difference) a fresh build is the committed file. The repository has no switch
for it (build.sh takes no option); `build_at_base.sh` runs the worktree's own build.sh unchanged with
`bin/basewrap/x86_64-w64-mingw32-gcc` first in `PATH`, which adds `-Wl,--image-base=<base of HEAD's DLL>` to the
`-shared` link. By hand the output must still be NAMED `CMB_Slope.dll` (the export table carries the name):

```
x86_64-w64-mingw32-gcc -std=c11 -O2 -Wall -Wextra -Werror -shared -o <folder>/CMB_Slope.dll tools/f4se-slope/CMB_Slope.c \
    -static-libgcc -Wl,--no-insert-timestamp -Wl,-s -lshell32 -Wl,--image-base=<base>
```

A build at the user's path without touching the user's tree: `unshare -m bash -c 'mount --bind <worktree>
/home/user/sieci && bash /home/user/sieci/tools/f4se-slope/build.sh'` (a private mount namespace).

**TMPDIR must be unset for Wine.** Wine 9.0 here aborts with TMPDIR set to anything, /tmp included:
`free(): invalid pointer`, no check line at all, run.sh returns 1. hrun.sh takes TMPDIR out of a mode's environment;
a bare `env -u TMPDIR USER=root ONLY=<mode> bash tools/f4se-slope/test/run.sh` needs it unset too. run.sh's work
folder and Wine prefix are under /tmp (mktemp -d), removed by run.sh at its end.

### The queue: hrun.sh, hall.sh

```
$CMB_ROOT/hrun.sh <worktree> <mode> [logfile]     # one mode through the queue
#   probe -> "probe ok=10 fail=0 rc=0 wait=0s run=12s log=..."
$CMB_ROOT/hall.sh <worktree> <outdir> [mode...]   # every mode (or the ones named), all queued at once; SUMMARY.txt
#   probe alone -> the table, "TOTAL 10 0 1 modes", "ALL PASS"
$CMB_ROOT/hrun.sh --status                        # who holds the slots
$CMB_ROOT/hrun.sh --cmd <command...>              # any other heavy job in a slot (HRUN_HEAVY=1: never beside full/climb)
$CMB_ROOT/hrun_selftest.sh [<hrun.sh>]            # dummy jobs on locks of their own, about 50 s:
#   10 tests, each "PASS", "snapshots left behind: 0", "SELFTEST PASS (<its folder>)"
```

`hrun.sh <worktree> <mode> [logfile]` copies run.sh, fake_game.c and Data/F4SE/Plugins/CMB_Slope.dll to a snapshot
under `$CMB_ROOT/tmp` WHEN IT IS CALLED, waits for a slot (flock on `harness.1.lock` and `harness.2.lock`, polled every
0.5 s: whichever frees first; full and climb take `heavy.lock` first, and the others stand back while the holder of
heavy.lock waits for a slot), then runs `env -u TMPDIR USER=root ONLY=<mode> nice -n 19 bash <snapshot>/tools/f4se-
slope/test/run.sh` in a session of its own with the lock descriptors closed. The log gets `## hrun:` lines
(worktree, HEAD, the three files' sha256, queue and run times); stdout one line `<mode> ok=<n> fail=<n> rc=<n>
wait=<s> run=<s> log=<path>`; exit 0 only with rc 0, no `  FAIL` line and at least one `  ok ` line. An unknown mode is
refused (run.sh would run nothing and return 0). The plugin's own log comes back as the worktree's
`tools/f4se-slope/test/last_<mode>.log` (ignored by git). The default log is `$CMB_ROOT/logs/<worktree's name>/<mode>.log`.

The locks live in `HRUN_DIR`, default `$CMB_ROOT`: two roots share the slots only if that is the same folder. A test
root (`CMB_ROOT=/opt/cmbtest`) therefore has slots of its own and does not wait for, or hold back, the real queue.
Replace an installed hrun.sh only with `mv new hrun.sh` (it is read whole before it runs, so a waiting copy survives
either way; `setup_tools.sh` does it that way).

The modes' run times, alone or two at a time (four cores): full and climb about 9 min each, wall, ram and sound about
7, view 6, arms, decals, fx and caution 3-4, the rest under 3; a 26-mode pass through hall.sh about 40 minutes. The
expected check counts per mode are in run.sh's header. The wall mode's sidestep check failed once beside other heavy
jobs and passed when run again alone: run wall alone when it fails, and keep other heavy work off the machine (or in a
queue slot, `hrun.sh --cmd`) while it runs.

## Assets: the Pythons and the nif library of `tools/rider`

| What | Where | Used as |
|---|---|---|
| DDS Python | `$CMB_ROOT/ddsenv/bin/python` | `DDS_PY`, "<DDS python>" (write_dds, look_paint, look_badges, look_shapes, look_wheels, look_plates) |
| mesh Python | `$CMB_ROOT/meshenv/bin/python` | `PYTHON` (harley_meshes, build_bike_meshes, check_bike_meshes, riding_anims, verify_clips, preview, bike_art, nifly_tangents, make_rider_plugin) |
| the 3D suite as a Python module | `$CMB_ROOT/bpyenv/bin/python` | `BLENDER_PY` (bike_textures, look_render) |
| PyNifly | `$CMB_ROOT/pynifly/io_scene_nifly` | `PYNIFLY`, `--pynifly` |

**The Linux NiflyDLL.** `pyn/niflydll.py` does `cdll.LoadLibrary(<io_scene_nifly>/NiflyDLL.dll)` and PyNifly's
repository has no binary (its releases ship one for the other OS in their zip). Its NiflyDLL/CMakeLists.txt names
folders that don't exist (external/nifly, include/), and its project file compiles `..\..\Nifly\src\*.cpp` with
`NiflyDLL/{Anim,Logger,NiflyFunctions,NiflyWrapper}.cpp`. So: our own `CMakeLists.txt` over both checkouts, unmodified,
plus `shim/`: a `windows.h` (FindProjectRoot() asks which file the library was loaded from: dladdr) and seven one-line
headers for includes spelt in another case. It builds an ELF shared object named `NiflyDLL.dll` (no `lib` in front),
with `-fdeclspec` (so `__declspec(dllexport)` parses) and `-ffp-contract=off` (no fused multiply-add, the arithmetic as
the other build does it): 19 ninja steps, 1325 exported functions. PyNifly's Python looks for its reference skeletons
as `<io_scene_nifly>/Skeletons/<GAME>/skeleton.nif`; the folders are `skeletons/` and `Skyrim/` (a case-insensitive file
system doesn't mind). Two links, or get_node_xform_to_global() falls back to zeros:

```
cmake -S $CMB_ROOT/native/niflydll-linux -B $CMB_ROOT/native/niflydll-linux/build -G Ninja -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_CXX_COMPILER=clang++ -DPYNIFLY_DIR=$CMB_ROOT/pynifly -DNIFLY_DIR=$CMB_ROOT/native/nifly
cmake --build $CMB_ROOT/native/niflydll-linux/build
cp $CMB_ROOT/native/niflydll-linux/build/NiflyDLL.dll $CMB_ROOT/pynifly/io_scene_nifly/   # ignored by PyNifly's .gitignore
ln -s skeletons $CMB_ROOT/pynifly/io_scene_nifly/Skeletons
ln -s Skyrim $CMB_ROOT/pynifly/io_scene_nifly/skeletons/SKYRIM
```

The self-tests: run from a folder outside the repository, with `-I -B` (`-B` keeps `__pycache__` out of the
repository's folders). None needs a file of the user's.

```
# PyNifly as the tools import it (sys.path.insert(0, <io_scene_nifly>); from pyn.pynifly import NifFile, TransformBuf):
# a nif with one triangle (BSTriShape, a material name) written, read back and compared; the same skinned to one bone,
# as the worn bike is
$CMB_ROOT/meshenv/bin/python -I -B $CMB_ROOT/tools/nifly_selftest.py --pynifly $CMB_ROOT/pynifly/io_scene_nifly --out <folder>
#   -> "library: .../NiflyDLL.dll version (30, 2, 0)", 13 "ok" lines, "ok"; the same from bpyenv, ddsenv and python3

# write_dds.py's round trip: every format and encoder, the header parsed and BC1/3/4/5 decoded by the test's own code
# and by texture2ddecoder, PSNR per mip, the options, the command line, two runs the same bytes
$CMB_ROOT/ddsenv/bin/python -I -B $CMB_ROOT/tools/dds_roundtrip.py <repository>/tools/rider [--out <folder>] [--digests]
#   -> "35 checks, all passed" (bc1 37.7 dB, bc3 38.9, bc4 47.8, bc5 44.6, bc7 40.2 opaque / 38.6 with alpha);
#      with --digests each case's sha256, e.g. bc1 a9a19d674034666e, bc7_opaque 47abdd87d16c3002, rgba8_cube
#      96fd64f4c87d8f38: the same pins print the same 35 digests

# byte for byte against the shipped textures, from the repository alone: the three plate atlases whose sha256
# docs/ASSETS.md records for the 2026-11-09a build (b5eacce3..., 78b75210..., 8892936a...)
$CMB_ROOT/meshenv/bin/python -I -B <repository>/tools/rider/bike_art.py --plates --out <art folder>          # 5 s
$CMB_ROOT/ddsenv/bin/python -I -B $CMB_ROOT/tools/plates_digest.py <repository>/tools/rider <art folder>
#   -> plates_d.dds 1398248 bytes b5eacce3d0379dd9763ce2ba564fc1f16dfae96ba7ff56d0f2d31239d078f2f1,
#      plates_n.dds 699216 bytes 78b752104ea15eec404d4808b7a3365f6ad001a58c5fb956cc5005cf55d3f298,
#      plates_s.dds 174928 bytes 8892936af4d292bc00234a3c45f4b176666b9e0447cdb3991ba7fed590320525, "ok"

# the 3D module headless: its path tracer on the CPU, a 64x64 render of a cube (lit, the same pixels twice), the
# denoiser + AgX, a glTF import, bike_textures.py's UV calls, an AO bake, texture2ddecoder
$CMB_ROOT/bpyenv/bin/python -I -B $CMB_ROOT/tools/bpy_selftest.py --out <folder>
#   -> "bpy 5.1.2 (ec6e62d40fa9, 2026-05-19), python 3.13.18, numpy 2.5.4, background True", 8 "ok" lines, "ok" (6 s)

# every tool starts under its Python (--help): the mesh Python's nine, the DDS Python's six, the module's two
# (look_render.py --list-views prints the view sets)
```

PyNifly's own pyn-layer tests, for the record (not needed): from a folder of links so that `tests\FO4\x.nif` resolves,
133 pass and 82 fail with this library: 49 are another game's tests (mostly no asset folder or module), the other 33
open a path in another case, look a material up by a path with backslashes, or start a subprocess. Its 20 animation
tests (the HKX reader and writer among them) all pass with its own runner.

`tools/rider/build_bike.sh` with these:

```
PYNIFLY=$CMB_ROOT/pynifly/io_scene_nifly PYTHON=$CMB_ROOT/meshenv/bin/python \
BLENDER_PY=$CMB_ROOT/bpyenv/bin/python DDS_PY=$CMB_ROOT/ddsenv/bin/python \
GLTF=<scene.gltf> VANILLA=<motorcycle_clean.nif> SEAT=<.../MT/CMB_Rider> DATA=<tree> STAGE=<stage> REFERENCE=<Meshes/CMB> \
  bash tools/rider/build_bike.sh [stage ...]
```

Still needs the user's files:

- **the built asset tree** (the previous package): `check_bike_meshes.py --data`, `look_render.py` (the bike's
  renders), `look_paint.py`/`look_badges.py`/`look_shapes.py`/`look_wheels.py`/`look_plates.py` (`--data`/`--base`/
  `--out`, and their `--check`), the package's verifier. It is also the first chance to compare this Linux-built nif
  library with the one the shipped nifs came from: read the shipped nifs with `check_bike_meshes.py`, and after a
  rebuild compare byte for byte (`REFERENCE`).
- **the model's glTF** (`scene.gltf` + `scene.bin`) and **the game's `motorcycle_clean.nif`** (and, for the clips,
  the game's `skeleton.hkx`, body nifs and reference clips): `harley_meshes.py`, `build_bike_meshes.py`,
  `bike_textures.py` (the bakes), `riding_anims.py`, `verify_clips.py`.
- **the stage folders** (shapes/, uv/*.npz, art/ of earlier builds): `look_plates.py` (the stock plate's re-sample
  needs `--old-stage`), `look_wheels.py`, `look_paint.py --stage`, `bike_textures.py --only`, `nifly_tangents.py
  validate`. Without them a texture rebuild starts from the glTF (about 28 minutes of bakes).

Not proved: that bpy 5.1.2's bakes equal the shipped ones (no bake input here; the patch level is a guess), that
fast-simplification 0.2.0 is the version the shipped meshes were cut with (the earlier pin is not recorded), and that
this library writes the same bytes as the other build.

## Packaging

`tools/package` (its README) needs only what the core sets up: python3, git and Caprica. Its asset base is the
previous package's Data folder, which is the user's: unpack the package zip as data, never with unzip into a folder
that holds scripts, then prove it complete:

```
bash tools/package/package.sh --extract <download folder>/CommonwealthMotorbike_<build>.zip $CMB_ROOT/pkg<build>
bash tools/package/package.sh --check-assets $CMB_ROOT/pkg<build>/CommonwealthMotorbike_<build>/Data
#   -> "all 787 files of assets.sha256 are there, byte for byte, and no other asset" (2026-11-10a's package)
python3 -I $CMB_ROOT/scratch/safe_unzip.py <zip> <new empty folder>     # any other zip: refuses a path out or a link
```

## Testing a rebuild

Into a fresh root, so the real one is left alone (the apt step finds the packages installed; that is fine):

```
CMB_ROOT=/opt/cmbtest bash tools/dev/setup_tools.sh && CMB_ROOT=/opt/cmbtest bash tools/dev/setup_tools.sh --assets
```

then the tests above against `/opt/cmbtest` (CAPRICA=/opt/cmbtest/caprica/src/build/Caprica/Caprica,
`CMB_ROOT=/opt/cmbtest /opt/cmbtest/hrun.sh <worktree> probe <log>` on the test root's own slots, the asset
self-tests with /opt/cmbtest's Pythons), and `rm -rf /opt/cmbtest` after. With fresh caches too
(`NUGET_PACKAGES=/opt/cmbtest/.cache/nuget UV_CACHE_DIR=/opt/cmbtest/.cache/uv`) it proves every download is still
there. Beside harness runs, run the builds at idle priority (`chrt -i 0 ionice -c 3 ...`) or in a queue slot.

## Not reproducible from the repository

- The user's files: the asset base (the previous package's zip, for `tools/package`), the model's glTF, the game's
  files (nifs, skeleton, clips) and earlier builds' stage folders. They are downloaded by hand and never committed.
- What a run leaves: the harness baselines and logs, the packages built (`$CMB_ROOT/out`), worktrees.
- The apt versions: the archive moves on (the `apt` step installs what it has and prints the versions).
- The NuGet set below the one pinned package (resolved at restore; no lock file in the generator).
