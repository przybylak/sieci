#!/usr/bin/env bash
# Syntax/type-checks the mod's Papyrus scripts with Caprica against
# declaration-only stubs of the Fallout 4 API (stubs/).
#
# This catches typos, wrong argument counts and type errors. It does NOT prove
# the scripts work in game, and the stubs are hand-written from the Creation Kit
# wiki, not Bethesda's real sources - the Creation Kit compile is the real test.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
SRC="$ROOT/Data/Scripts/Source/User"
CAPRICA="${CAPRICA:-$HERE/.caprica/src/build/Caprica/Caprica}"
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT

if [ ! -x "$CAPRICA" ]; then
  echo "Caprica not found at $CAPRICA - run build-caprica.sh first (or set CAPRICA=...)" >&2
  exit 2
fi

run_caprica() { # <output dir> <import dirs (colon separated)> <input dir>
  local imports=()
  IFS=':' read -ra dirs <<< "$2"
  for d in "${dirs[@]}"; do imports+=(-i "$d"); done
  "$CAPRICA" -q -g fallout4 -f "$HERE/Fallout4_Flags.flg" "${imports[@]}" -o "$1" "$3"
}

# Core scripts: vanilla API only. The optional *F4SE.psc scripts are checked separately.
CORE="$OUT/core"
mkdir -p "$CORE" "$OUT/pex"
find "$SRC" -maxdepth 1 -name '*.psc' ! -name '*F4SE.psc' -exec cp {} "$CORE"/ \;

status=0
if run_caprica "$OUT/pex" "$HERE/stubs/vanilla" "$CORE"; then
  echo "ok    core scripts: $(cd "$CORE" && ls *.psc | tr '\n' ' ')"
else
  echo "FAIL  core scripts"; status=1
fi

# F4SE scripts: vanilla + F4SE stubs, with the core scripts importable.
F4SE_STUBS="$OUT/stubs-f4se"
mkdir -p "$F4SE_STUBS"
cp "$HERE"/stubs/vanilla/*.psc "$F4SE_STUBS"/
cp "$HERE"/stubs/f4se/*.psc "$F4SE_STUBS"/
for script in "$SRC"/*F4SE.psc; do
  name="$(basename "$script")"
  one="$OUT/f4se-${name%.psc}"
  mkdir -p "$one"
  cp "$script" "$one"/
  if run_caprica "$OUT/pex" "$F4SE_STUBS:$CORE" "$one"; then
    echo "ok    $name (with F4SE stubs)"
  else
    echo "FAIL  $name"; status=1
  fi
done

exit $status
