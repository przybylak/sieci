#!/usr/bin/env bash
# setup_tools.sh - rebuilds the toolchain that lives outside the repository, in $CMB_ROOT (default
# /opt/cmb), on a fresh 24.04 container: as root, non-interactive, idempotent (a step whose result is
# already there skips itself). Nothing comes from the user: no asset files, no secrets.
#
#   bash tools/dev/setup_tools.sh [--assets] [<repository>]
#
#   (default)     the core: apt packages, the helper files (tools/dev/cmb -> $CMB_ROOT), Caprica,
#                 F4SE 0.7.9's sources and the ESP generator (restore and build)
#   --assets      the core and the asset tools: uv, ddsenv, meshenv, bpyenv (about 1 GB), PyNifly and
#                 nifly at their pinned commits, the Linux NiflyDLL and its two skeleton links
#   <repository>  the checkout whose build-caprica.sh and ESP generator are used (default: the one
#                 this script is in); the helper files and the pins always come from this script's folder
#
# One line per step on stdout; a step's whole output goes to $CMB_ROOT/setup-logs/<step>.log. A step
# that fails prints why and the end of its log, and the script exits 1. NUGET_PACKAGES and UV_CACHE_DIR
# are honoured. tools/dev/README.md says what each part is and how to test it.
set -euo pipefail

ASSETS=0 REPO=""
for a in "$@"; do
  case "$a" in
    --assets) ASSETS=1 ;;
    -h|--help) sed -n '2,17p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "setup_tools.sh: unknown option $a (see --help)" >&2; exit 2 ;;
    *) [ -z "$REPO" ] || { echo "setup_tools.sh: one repository only" >&2; exit 2; }; REPO="$a" ;;
  esac
done
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "${REPO:-$HERE/../..}" && pwd)"
if [ ! -f "$REPO/tools/build.sh" ] || [ ! -f "$REPO/tools/syntax-check/build-caprica.sh" ]; then
  echo "setup_tools.sh: $REPO is not the repository (no tools/build.sh)" >&2; exit 2
fi
CMB="${CMB_ROOT:-/opt/cmb}"
case "$CMB" in /*) ;; *) echo "setup_tools.sh: CMB_ROOT must be an absolute path" >&2; exit 2 ;; esac
LOGS="$CMB/setup-logs"
mkdir -p "$CMB" "$LOGS"
export HOME="${HOME:-$(getent passwd "$(id -u)" | cut -d: -f6)}"
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1
exec 6> "$CMB/.setup.lock"
flock -n 6 || { echo "setup_tools.sh: waiting for another run on $CMB" >&2; flock 6; }

# --- the pins (tools/dev/README.md, "Versions")
APT_PKGS="cmake clang ninja-build libboost-filesystem-dev libboost-program-options-dev libboost-container-dev"
APT_PKGS+=" dotnet-sdk-8.0 gcc-mingw-w64-x86-64 wine wine64 util-linux git make python3 ca-certificates"
F4SE=(https://github.com/ianpatt/f4se v0.7.9 4692e9bba0f87d8b8d1a0b79110bf212f2b2ada7)
PYNIFLY=(https://github.com/BadDogSkyrim/PyNifly V30.3.0 ac3c1453a5efa44f580033205ecaf5be9a005eed)
NIFLY=(https://github.com/BadDogSkyrim/nifly main 8b43aaa022c4dec8edd0985630cb101ea9785d92)
NIFLYDLL_SHA=be373e5ead3003d759fdca1692d28874964e91bab8d97b2fa305400058cf77ca   # the recorded build
UV_VERSION=0.11.32   # installed only when no uv is on PATH
PYVER=3.13

# --- the step runner
MSGF="$(mktemp)"
trap 'rm -f "$MSGF"' EXIT
say() { printf '%s' "$*" > "$MSGF"; }          # the step's one line
die() { printf '%s' "$*" > "$MSGF"; exit 1; }  # the step's reason for failing
step() { # <name> <function> [args]: runs it in a subshell, its output in $LOGS/<name>.log
  local name="$1" t=$SECONDS rc=0 msg
  shift
  : > "$MSGF"
  set +e
  (
    set -eEo pipefail
    trap 'printf "a command failed (line %s): %s" "$LINENO" "$BASH_COMMAND" > "$MSGF"' ERR
    "$@"
  ) > "$LOGS/$name.log" 2>&1 < /dev/null 6>&-
  rc=$?
  set -e
  msg="$(cat "$MSGF")"
  if [ "$rc" = 0 ]; then
    printf '%-10s %s (%d s)\n' "$name" "$msg" "$((SECONDS - t))"
  else
    printf '%-10s FAILED: %s\n' "$name" "${msg:-exit status $rc}"
    echo "           the end of $LOGS/$name.log:"
    tail -n 25 "$LOGS/$name.log" | sed 's/^/           | /'
    exit 1
  fi
}

# clone_at <dir> <url> <tag or branch> <sha> [shallow]: <dir> checked out at <sha>. A new clone is made in
# a new empty folder (<dir>.part) and moved into place only once it is at <sha>. Sets CLONED.
clone_at() {
  local d="$1" url="$2" ref="$3" sha="$4" how="${5:-full}" tmp="$1.part"
  if [ -d "$d/.git" ]; then
    if [ "$(git -C "$d" rev-parse HEAD)" = "$sha" ]; then CLONED="already at ${sha:0:7}"; return; fi
    git -C "$d" checkout -q "$sha" 2>/dev/null || { git -C "$d" fetch -q origin "$sha"; git -C "$d" checkout -q "$sha"; }
    CLONED="moved to ${sha:0:7}"; return
  fi
  [ ! -e "$d" ] || die "$d exists and is not a git clone: move it away"
  rm -rf "$tmp"
  mkdir -p "$(dirname "$d")"
  if [ "$how" = shallow ]; then
    git clone -q --depth 1 --branch "$ref" "$url" "$tmp"
  else
    git clone -q "$url" "$tmp"
    git -C "$tmp" checkout -q "$sha"
  fi
  [ "$(git -C "$tmp" rev-parse HEAD)" = "$sha" ] || die "$url $ref is $(git -C "$tmp" rev-parse --short HEAD), not ${sha:0:7}"
  mv "$tmp" "$d"
  CLONED="cloned $url at $ref = ${sha:0:7}"
  if [ "$how" = shallow ]; then CLONED+=", depth 1"; fi
}

# --- core
s_apt() {
  local p missing=() n=0 did
  for p in $APT_PKGS; do
    n=$((n + 1))
    dpkg-query -W -f='${Status}' "$p" 2>/dev/null | grep -q 'install ok installed' || missing+=("$p")
  done
  if [ ${#missing[@]} -gt 0 ]; then
    [ "$(id -u)" = 0 ] || die "root is needed to install: ${missing[*]}"
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -q
    apt-get install -y -q "${missing[@]}"
    did="installed ${missing[*]}"
  else
    did="all $n packages already installed"
  fi
  local wine64
  wine64="$(command -v wine64 || echo /usr/lib/wine/wine64)"
  [ -x "$wine64" ] || die "no wine64 (neither on PATH nor /usr/lib/wine/wine64)"
  for p in flock setsid unshare timeout x86_64-w64-mingw32-gcc clang++ cmake ninja dotnet git python3; do
    command -v "$p" > /dev/null || die "no $p on PATH after the install"
  done
  p="mingw $(x86_64-w64-mingw32-gcc -dumpversion), wine $(dpkg-query -W -f='${Version}' wine)"
  p+=", clang $(clang++ -dumpversion), cmake $(cmake --version | sed -n '1s/.* //p')"
  p+=", dotnet-sdk $(dotnet --version | tail -n 1)"
  say "$did: $p"
}

s_helpers() {
  local f rel dst mode n=0 new=0 upd=0 fix=0
  mkdir -p "$CMB/bin" "$CMB/build" "$CMB/tmp" "$CMB/logs" "$CMB/wt"
  while IFS= read -r -d '' f; do
    rel="${f#"$HERE/cmb/"}" dst="$CMB/$rel" n=$((n + 1))
    mode=644; [ -x "$f" ] && mode=755
    if [ -f "$dst" ] && cmp -s "$f" "$dst"; then
      if [ "$(stat -c %a "$dst")" != "$mode" ]; then chmod "$mode" "$dst"; fix=$((fix + 1)); fi
      continue
    fi
    mkdir -p "$(dirname "$dst")"
    install -m "$mode" "$f" "$dst.new.$$"
    if [ -e "$dst" ]; then cp -p "$dst" "$dst.prev"; upd=$((upd + 1)); else new=$((new + 1)); fi
    mv -f "$dst.new.$$" "$dst"   # a new file put in place (a waiting hrun.sh keeps the copy it read)
  done < <(find "$HERE/cmb" -type f -print0 | sort -z)
  [ "$n" -gt 0 ] || die "no files under $HERE/cmb"
  local up=$((n - new - upd))
  say "$n files from tools/dev/cmb: $new installed, $upd replaced (old kept as .prev), $up up to date, $fix chmod"
}

s_caprica() {
  local w="$CMB/caprica" bin="$CMB/caprica/src/build/Caprica/Caprica" want
  want="$(sed -n 's/^COMMIT=//p' "$REPO/tools/syntax-check/build-caprica.sh")"
  [ -n "$want" ] || die "no COMMIT= in build-caprica.sh"
  if [ -x "$bin" ] && [ "$(git -C "$w/src" rev-parse HEAD 2>/dev/null)" = "$want" ]; then
    say "already built at ${want:0:7}: $bin"; return
  fi
  if [ -e "$w/src" ] && ! git -C "$w/src" rev-parse HEAD > /dev/null 2>&1; then rm -rf "$w/src"; fi
  CAPRICA_WORKDIR="$w" bash "$REPO/tools/syntax-check/build-caprica.sh"
  [ -x "$bin" ] || die "build-caprica.sh finished but there is no $bin"
  say "built at ${want:0:7} with caprica-linux.patch: $bin"
}

s_f4se() {
  local d="$CMB/native/f4se" nv nm
  clone_at "$d" "${F4SE[@]}"
  nv=$(find "$d/scripts/vanilla" -maxdepth 1 -name '*.psc' | wc -l)
  nm=$(find "$d/scripts/modified" -maxdepth 1 -name '*.psc' | wc -l)
  say "$CLONED: $d (scripts/vanilla $nv .psc, scripts/modified $nm .psc)"
}

s_generator() {
  local gen="$REPO/tools/esp-generator" out="$REPO/tools/esp-generator/bin/out" refs id ver miss=""
  local nuget="${NUGET_PACKAGES:-$HOME/.nuget/packages}"
  refs="$(sed -n 's/.*<PackageReference Include="\([^"]*\)" Version="\([^"]*\)".*/\1 \2/p' "$gen/EspGenerator.csproj")"
  [ -n "$refs" ] || die "no PackageReference in EspGenerator.csproj"
  while read -r id ver; do
    [ -d "$nuget/${id,,}/$ver" ] || miss+=" $id $ver"
  done <<< "$refs"
  if [ -z "$miss" ] && [ -f "$out/EspGenerator.dll" ] \
     && [ -z "$(find "$gen" -maxdepth 1 -type f -newer "$out/EspGenerator.dll" \( -name '*.cs' -o -name '*.csproj' -o -name '*.json' \))" ]; then
    say "already built: $out/EspGenerator.dll (packages in $nuget)"; return
  fi
  # no build servers left running afterwards (-nodeReuse:false, no shared compiler)
  dotnet restore "$gen/EspGenerator.csproj"
  dotnet build -c Release --no-restore -nodeReuse:false -p:UseSharedCompilation=false "$gen/EspGenerator.csproj" -o "$out"
  [ -f "$out/EspGenerator.dll" ] || die "dotnet build finished but there is no $out/EspGenerator.dll"
  say "restored${miss:- (cached)} into $nuget; built $out/EspGenerator.dll"
}

# --- assets
uvbin() { command -v uv || { [ -x "$CMB/uvenv/bin/uv" ] && echo "$CMB/uvenv/bin/uv"; } || true; }

s_uv() {
  local u
  u="$(uvbin)"
  if [ -n "$u" ]; then say "$u ($("$u" --version 2>/dev/null))"; return; fi
  rm -rf "$CMB/uvenv"
  python3 -m venv "$CMB/uvenv"
  "$CMB/uvenv/bin/python" -m pip install -q "uv==$UV_VERSION"
  u="$CMB/uvenv/bin/uv"
  [ -x "$u" ] || die "pip installed uv $UV_VERSION but there is no $u"
  say "no uv on PATH: installed $("$u" --version) into $CMB/uvenv"
}

same_pins() { # <venv> <requirements>: the venv holds exactly the requirements' packages
  diff <(grep -v '^#' "$2" | sort -f) <(VIRTUAL_ENV="$1" "$(uvbin)" pip freeze 2> /dev/null | sort -f) > /dev/null
}

s_venv() { # <name>: $CMB/<name> from tools/dev/requirements/<name>.txt
  local e="$CMB/$1" req="$HERE/requirements/$1.txt" u n v
  u="$(uvbin)"
  [ -n "$u" ] || die "no uv (the uv step installs it)"
  n=$(grep -cv '^#' "$req")
  if [ -x "$e/bin/python" ] && same_pins "$e" "$req"; then
    say "already there: $e ($n packages as pinned)"; return
  fi
  [ -x "$e/bin/python" ] || "$u" venv -q -p "$PYVER" "$e"
  VIRTUAL_ENV="$e" "$u" pip sync -q "$req"
  same_pins "$e" "$req" || die "after the install $e does not hold exactly $req's packages"
  v="$("$e/bin/python" -c 'import platform; print(platform.python_version())')"
  say "made $e: python $v, $n packages as pinned ($(du -sh "$e" | cut -f1))"
}

s_pynifly() {
  clone_at "$CMB/pynifly" "${PYNIFLY[@]}" shallow
  say "$CLONED: $CMB/pynifly"
}

s_nifly() {
  clone_at "$CMB/native/nifly" "${NIFLY[@]}"
  say "$CLONED: $CMB/native/nifly"
}

s_niflydll() {
  local src="$CMB/native/niflydll-linux" io="$CMB/pynifly/io_scene_nifly" sha note
  [ -f "$src/CMakeLists.txt" ] && [ -f "$src/shim/windows.h" ] || die "no $src/CMakeLists.txt or shim/ (step helpers)"
  [ -d "$io/pyn" ] && [ -d "$CMB/native/nifly/src" ] || die "PyNifly or nifly is missing (steps pynifly, nifly)"
  if [ -f "$io/NiflyDLL.dll" ] && [ -L "$io/Skeletons" ] && [ -L "$io/skeletons/SKYRIM" ] \
     && { [ ! -f "$src/build/NiflyDLL.dll" ] || cmp -s "$src/build/NiflyDLL.dll" "$io/NiflyDLL.dll"; }; then
    say "already there: $io/NiflyDLL.dll (sha256 $(sha256sum < "$io/NiflyDLL.dll" | cut -c1-16)) and both links"; return
  fi
  if [ ! -f "$src/build/NiflyDLL.dll" ]; then
    cmake -S "$src" -B "$src/build" -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=clang++ \
          -DPYNIFLY_DIR="$CMB/pynifly" -DNIFLY_DIR="$CMB/native/nifly"
    cmake --build "$src/build"
  fi
  cp "$src/build/NiflyDLL.dll" "$io/NiflyDLL.dll"
  # PyNifly looks for <io_scene_nifly>/Skeletons/<GAME>/skeleton.nif; the folders are skeletons/ and Skyrim/
  [ -L "$io/Skeletons" ] || ln -s skeletons "$io/Skeletons"
  [ -L "$io/skeletons/SKYRIM" ] || ln -s Skyrim "$io/skeletons/SKYRIM"
  sha="$(sha256sum < "$io/NiflyDLL.dll" | cut -d' ' -f1)"
  if [ "$sha" = "$NIFLYDLL_SHA" ]; then note="the recorded build's bytes"; else note="not the recorded ${NIFLYDLL_SHA:0:16}"; fi
  say "built $io/NiflyDLL.dll (sha256 ${sha:0:16}: $note) and linked Skeletons, skeletons/SKYRIM"
}

# --- the run
T0=$SECONDS
if [ "$ASSETS" = 1 ]; then a=", with --assets"; else a=""; fi
echo "setup_tools.sh: CMB_ROOT=$CMB, repository $REPO$a"
step apt s_apt
step helpers s_helpers
step caprica s_caprica
step f4se s_f4se
step generator s_generator
echo "core done in $((SECONDS - T0)) s"
if [ "$ASSETS" = 1 ]; then
  T1=$SECONDS
  step uv s_uv
  step ddsenv s_venv ddsenv
  step meshenv s_venv meshenv
  step bpyenv s_venv bpyenv
  step pynifly s_pynifly
  step nifly s_nifly
  step niflydll s_niflydll
  echo "assets done in $((SECONDS - T1)) s"
fi
echo "all done in $((SECONDS - T0)) s; logs in $LOGS. Not set up here: the user's asset files (tools/dev/README.md)"
