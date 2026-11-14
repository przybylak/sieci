#!/usr/bin/env bash
# Builds a release package of the mod: the folder CommonwealthMotorbike_<build>/ (README.txt + Data/) and two
# zips of it, from one commit of this repository and the asset base (the previous package's Data folder).
#
#   BUILD=<build> [ASSETS=<Data folder>] [OVERLAY=<dir>[:<dir>...]] [OUT=<folder>] [CAPRICA=<binary>] \
#       [PACKAGE_COMMIT=<rev>] [CHECK_ASSETS=0] bash tools/package/package.sh
#   bash tools/package/package.sh --check-assets [<Data folder>]            # against tools/package/assets.sha256
#   bash tools/package/package.sh --write-assets-manifest [<Data folder>]   # rewrites tools/package/assets.sha256
#   bash tools/package/package.sh --extract <package.zip> <new folder>      # a package zip, unpacked as data
#
#   BUILD           the build's name (2026-11-14a); tools/package/builds/<build>.json must exist
#   ASSETS          the asset base: the previous package's Data folder
#                   (default /opt/cmb/pkg10a/CommonwealthMotorbike_2026-11-10a/Data)
#   OVERLAY         folders of this build's newly built assets, laid out like Data (Meshes/CMB/..., Sound/FX/CMB/...),
#                   applied in order over the asset base; every file taken is logged
#   OUT             where the folder and the zips go (default /opt/cmb/out/<build>; not inside the repository)
#   CAPRICA         the Papyrus compiler (tools/syntax-check/build-caprica.sh); default: the syntax check's own
#                   build, else /opt/cmb/caprica/src/build/Caprica/Caprica
#   PACKAGE_COMMIT  the commit whose content is packaged and named in README.txt (default HEAD)
#
# What is refused before anything is written:
#   - a tracked file under Data/ or tools/ that is modified or staged (untracked files don't count);
#   - HEAD differing from PACKAGE_COMMIT in what a package is made from: Data/, tools/syntax-check/ (the compile's
#     stubs and flags) or tools/esp-generator/look_options.json. So a later commit that only adds or changes
#     tools/package/ or the documents can still package an earlier commit, named as that commit.
# Everything of the repository that goes into the package is then read from PACKAGE_COMMIT's objects, never from
# the working tree: Data's files, and the scripts and the syntax check's files the compile uses. The files of
# tools/package itself (the template, the credits, the lists, the manifest) are the working tree's.
#
# The rest is tools/package/pkglib.py (its header says what the guard checks and how the zips are made
# deterministic). Afterwards: python3 -I tools/package/verify_zips.py ... (tools/package/README.md).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
LIB=(python3 -I "$HERE/pkglib.py")
ASSETS="${ASSETS:-/opt/cmb/pkg10a/CommonwealthMotorbike_2026-11-10a/Data}"

usage() { sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; }

case "${1:-}" in
  --check-assets)          exec "${LIB[@]}" check-assets "${2:-$ASSETS}" ;;
  --write-assets-manifest) exec "${LIB[@]}" write-assets-manifest "${2:-$ASSETS}" ;;
  --extract)               [ $# -eq 3 ] || { usage >&2; exit 2; }
                           exec "${LIB[@]}" extract "$2" "$3" ;;
  -h|--help)               usage; exit 0 ;;
  "")                      ;;
  *)                       usage >&2; exit 2 ;;
esac

BUILD="${BUILD:-}"
if ! [[ "$BUILD" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}[a-z]$ ]]; then
  echo "REFUSED: set BUILD to the build's name, like BUILD=2026-11-14a" >&2; exit 2
fi
OUT="$(python3 -I -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "${OUT:-/opt/cmb/out/$BUILD}")"
case "$OUT/" in "$(cd "$ROOT" && pwd -P)"/*) echo "REFUSED: OUT ($OUT) is inside the repository" >&2; exit 2 ;; esac
[ -f "$HERE/builds/$BUILD.json" ] || {
  echo "REFUSED: no tools/package/builds/$BUILD.json (copy builds/TEMPLATE.json and fill it in)" >&2; exit 2; }
[ -d "$ASSETS" ] || { echo "REFUSED: ASSETS ($ASSETS) is not a folder" >&2; exit 2; }

# --- which commit, and is the tree what that commit says
COMMIT="$(git -C "$ROOT" rev-parse --verify "${PACKAGE_COMMIT:-HEAD}^{commit}")"
dirty="$(git -C "$ROOT" status --porcelain --untracked-files=no -- Data tools)"
if [ -n "$dirty" ]; then
  echo "REFUSED: tracked files under Data/ or tools/ have changes:" >&2; echo "$dirty" >&2; exit 1
fi
FROM=(Data tools/syntax-check tools/esp-generator/look_options.json)
moved="$(git -C "$ROOT" diff --name-only "$COMMIT" HEAD -- "${FROM[@]}")"
if [ -n "$moved" ]; then
  echo "REFUSED: HEAD ($(git -C "$ROOT" rev-parse --short=7 HEAD)) differs from the commit to package" \
       "($(git -C "$ROOT" rev-parse --short=7 "$COMMIT")) in:" >&2; echo "$moved" >&2; exit 1
fi

# --- the compiler
if [ -z "${CAPRICA:-}" ]; then
  for c in "$ROOT/tools/syntax-check/.caprica/src/build/Caprica/Caprica" /opt/cmb/caprica/src/build/Caprica/Caprica; do
    if [ -x "$c" ]; then CAPRICA="$c"; break; fi
  done
fi
[ -x "${CAPRICA:-}" ] || {
  echo "REFUSED: no Papyrus compiler: run tools/syntax-check/build-caprica.sh or set CAPRICA=<binary>" >&2; exit 2; }

# --- the asset base, against the list in the repository
if [ "${CHECK_ASSETS:-1}" != 0 ]; then
  "${LIB[@]}" check-assets "$ASSETS" || {
    echo "REFUSED: the asset base is not the one tools/package/assets.sha256 lists (CHECK_ASSETS=0 skips this)" >&2
    exit 1; }
fi

# --- the scripts: the commit's sources, compiled by the commit's own syntax check, in a temporary folder
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir "$WORK/src" "$WORK/pex"
git -C "$ROOT" archive "$COMMIT" Data/Scripts/Source/User tools/syntax-check | tar -x -C "$WORK/src"
echo "compiling the scripts of $(git -C "$ROOT" rev-parse --short=7 "$COMMIT") with $CAPRICA" \
     "(sha256 $(sha256sum "$CAPRICA" | cut -c1-16)...)"
PEX_OUT="$WORK/pex" CAPRICA="$CAPRICA" bash "$WORK/src/tools/syntax-check/check.sh"

# --- the folder, the guard, the zips (an earlier run's zips in OUT are removed first: a refused run leaves none)
mkdir -p "$OUT"
overlays=()
if [ -n "${OVERLAY:-}" ]; then
  IFS=':' read -ra dirs <<< "$OVERLAY"
  for d in "${dirs[@]}"; do [ -n "$d" ] && overlays+=(--overlay "$d"); done
fi
"${LIB[@]}" package --repo "$ROOT" --commit "$COMMIT" --build "$BUILD" --assets "$ASSETS" \
    --pex "$WORK/pex" --out "$OUT" ${overlays[@]+"${overlays[@]}"}
