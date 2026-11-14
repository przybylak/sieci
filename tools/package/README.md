# Release packaging

Builds the ready-to-install package of a build, `CommonwealthMotorbike_<build>/` (`README.txt` + `Data/`) and its two
zips, from one commit of this repository and the asset base, and verifies the zips afterwards. Standard library
Python (run with `python3 -I`), bash, git and the Papyrus compiler of `tools/syntax-check`.

| File | What it is |
|---|---|
| `package.sh` | the packager: git checks, compiles the scripts, then `pkglib.py package` (folder, guard, zips) |
| `pkglib.py` | the shared code: what a package is made of, the guard, the zip writer, the asset list, safe extraction. Its header says what each check does and where it is simpler than the lost packager's |
| `verify_zips.py` | the verifier: re-opens both zips and proves them against the commit, the previous package and the build's manifest |
| `builds/<build>.json` | a build's manifest (below); `builds/TEMPLATE.json` is the commented template |
| `README.template.txt` | the package's `README.txt`, with `@COMMIT@` on line 1 where the commit goes. The build's notes are written here |
| `CREDITS.txt` | the README's credit block, byte for byte. The packager and the verifier refuse a README whose tail differs |
| `game_paths.txt` | the game's own files the mod names by path and does not ship |
| `assets.sha256` | sha256 and path (relative to `Data`) of the asset base's 787 files: what git does not hold |

## The asset base

Meshes, textures, materials, sounds and the rider's clips are not in git. The packager takes them from the previous
package's `Data` folder (`ASSETS`), every file under `Meshes/CMB`, `Textures/CMB`, `Materials/CMB`, `Sound/FX/CMB`
and `Meshes/Actors/Character/Animations/MT/CMB_Rider`, then lays the build's newly built assets over them
(`OVERLAY`, one or more folders laid out like `Data`). `assets.sha256` lists the base, so a restored tree can be
proved complete:

```
# from a package zip, on a fresh machine: unpacked as data (plain files only, nothing outside the new folder,
# nothing executable), never with unzip into a folder that holds scripts
bash tools/package/package.sh --extract <dl>/CommonwealthMotorbike_2026-11-10a.zip /opt/cmb/pkg10a
bash tools/package/package.sh --check-assets /opt/cmb/pkg10a/CommonwealthMotorbike_2026-11-10a/Data
#   -> "all 787 files of assets.sha256 are there, byte for byte, and no other asset" (exit 0);
#      a missing, different or unlisted asset file is named and the exit code is 1
```

`package.sh` makes the same check before it packages (`CHECK_ASSETS=0` skips it). After a build has shipped, its
package is the next build's asset base: `bash tools/package/package.sh --write-assets-manifest <its Data folder>`
rewrites `assets.sha256`, to commit with the next build's manifest.

## Packaging a build

1. Write `builds/<build>.json` from `builds/TEMPLATE.json` and the build's notes into `README.template.txt` (line 1
   names the build and keeps `@COMMIT@`; the heading `WHAT'S NEW IN <build>`; the credit block stays as
   `CREDITS.txt` has it, or both change together). Commit: tracked files under `Data/` and `tools/` must be clean.
2. Package (a few seconds for the folder, about fifteen for the zips):

```
BUILD=2026-11-14a \
ASSETS=/opt/cmb/pkg10a/CommonwealthMotorbike_2026-11-10a/Data \
OVERLAY=<folder of this build's new assets>[:<another>] \
OUT=/opt/cmb/out/2026-11-14a \
CAPRICA=/opt/cmb/caprica/src/build/Caprica/Caprica \
bash tools/package/package.sh 2>&1 | tee /opt/cmb/out/package_2026-11-14a.log
```

   It prints what it took from where (each overlaid file with its sha256), one `ok` line per guard check, both
   zips' sizes and md5, and `packaged commit <sha7>`. Any `FAIL` stops it before a zip is written (an earlier
   run's zips in `OUT` are removed first; the folder is left to look at).
3. Verify:

```
python3 -I tools/package/verify_zips.py \
    /opt/cmb/out/2026-11-14a/CommonwealthMotorbike_2026-11-14a.zip /opt/cmb/out/2026-11-14a/CommonwealthMotorbike_MO2.zip \
    --repo . --commit HEAD --previous /opt/cmb/pkg10a/CommonwealthMotorbike_2026-11-10a [--list-changes]
#   -> one PASS/FAIL line per check, "<n> PASS, <m> FAIL", exit 0 only with no FAIL
```

   `--list-changes` prints the `vs_previous` block as found (what differs from the previous package, with each
   file's sha256): read it, and when it is what the build meant to change, paste it into the manifest.

`PACKAGE_COMMIT=<rev>` packages another commit than `HEAD` and names it in the README. `HEAD` may differ from it
only outside what a package is made from (`Data/`, `tools/syntax-check/`, `tools/esp-generator/look_options.json`):
so a manifest corrected in a later commit (step 3's paste) still packages, and names, the build's commit. Give the
verifier the same commit.

What goes in, read from the commit's objects and never from the working tree: every file the commit tracks under
`Data/` but `Meshes/CMB/PUT_MESHES_HERE.txt` and the four engine WAVs (`CMB_EngineStart`, `Stop`, `CruiseLP`,
`IdleLP`: the repository's are synthesised fallbacks, the package's are built from the recording and come from the
asset base); one `.pex` per tracked `.psc`, compiled from the commit's sources by the commit's own
`tools/syntax-check/check.sh` in a temporary folder. A `CMB_BikeFit.json` is never taken from anywhere.

## The two zips

`CommonwealthMotorbike_<build>.zip` holds the folder `CommonwealthMotorbike_<build>/` (`README.txt`, `Data/`).
`CommonwealthMotorbike_MO2.zip` holds `Data`'s contents at its root and no `README.txt`: a Mod Organizer 2 mod
folder as it is. Both are deterministic: a fixed member order, deflate level 6, no directory entries or extra
fields, modes 0644 (the commit's mode for a tracked file: the DLL's 0755), every member's time the packaged
commit's committer time in UTC. The compiled scripts' headers are stamped the same way (the commit's time, the
source folder `/tmp/tmp.0000000000`), since the compiler writes its clock and its temporary folder there. Two runs
on the same inputs give the same bytes with the same zlib; another zlib build may deflate differently, which is why
the verifier compares contents and not zip bytes.

## A build's manifest

`builds/<build>.json`; keys starting with `_` are comments. `builds/TEMPLATE.json` explains each key in place.

| Key | Holds | Read by |
|---|---|---|
| `build`, `previous` | the build's name; the build whose package is the asset base and the verifier's `--previous` | both |
| `esp.records`, `esp.next_object_id` | the plugin header's record count and next object ID (`"0xBF7"`) | guard, verifier |
| `esp.edids` | records that must be in the plugin, `TYPE:EditorID` | guard, verifier |
| `counts` | files per extension over the whole package | guard, verifier |
| `vs_previous.changed`, `.added` | package paths (`Data/...`) of the assets and compiled scripts that differ from the previous package or are new, each with its sha256 in this package (or `null`) | verifier |
| `vs_previous.removed` | assets of the previous package this build must not have | packager (drops them), verifier |
| `pex_header`, `zip` | only to rebuild an old package byte for byte (2026-11-10a's) | packager, verifier |

The verifier fails a difference that is not listed and a listed file that did not change. A compiled script counts
as changed when its code differs; its header alone always differs between builds.

## 2026-11-10a, rebuilt

The old packager was lost with its container; its last package is this folder's test. With `builds/2026-11-10a.json`
(that package's compile time, temporary folder and member times) the tools rebuild it byte for byte:

```
BUILD=2026-11-10a PACKAGE_COMMIT=c716330 OUT=<out> bash tools/package/package.sh
#   -> 817 files, "diff -r" clean against the original package's folder;
#      CommonwealthMotorbike_2026-11-10a.zip  78337906 bytes  md5 9f9bd48dc638748b3ef637cdb26a2e74
#      CommonwealthMotorbike_MO2.zip          78265392 bytes  md5 8ece91bf4617ee0bd214c78b22d0d67c   (the originals')
python3 -I tools/package/verify_zips.py <out>/CommonwealthMotorbike_2026-11-10a.zip <out>/CommonwealthMotorbike_MO2.zip \
    --repo . --commit c716330 --previous /opt/cmb/pkg10a/CommonwealthMotorbike_2026-11-10a
#   -> "51 PASS, 0 FAIL"
```

(Python 3.13.18 with zlib 1.3, Caprica 9cd6d32e + `tools/syntax-check/caprica-linux.patch`.)
