#!/usr/bin/env bash
# Runs CMB_Slope.dll against the fake game under Wine: full test (offset known), probe only
# (no offset), and a wrong game version. Needs MinGW-w64 and wine64.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
x86_64-w64-mingw32-gcc -std=c11 -O1 -Wall -Wextra -o "$WORK/fake_game.exe" "$HERE/fake_game.c" -static-libgcc
WINE="${WINE:-$(command -v wine64 || echo /usr/lib/wine/wine64)}"
export WINEDEBUG=-all WINEPREFIX="${WINEPREFIX:-$WORK/prefix}"
status=0
run() { # <name> <mode> <ini ProxySlopeOffset>
  mkdir -p "$WORK/$1"
  cp "$HERE/../../../Data/F4SE/Plugins/CMB_Slope.dll" "$WORK/$1/"
  printf '[Slope]\nProxySlopeOffset=%s\nProbe=1\nIntervalMs=100\n' "$3" > "$WORK/$1/CMB_Slope.ini"
  echo "== $1"
  if (cd "$WORK/$1" && "$WINE" "$WORK/fake_game.exe" 'CMB_Slope.dll' "$2"); then :; else status=1; fi
  log="$(find "$WINEPREFIX" "$WORK/$1" -name CMB_Slope.log 2>/dev/null | head -1 || true)"
  if [ -n "$log" ]; then mv "$log" "$HERE/last_$1.log"; fi
}
run full 0 0x9C
run probe 1 ""
run wrongversion 2 0x9C
exit $status
