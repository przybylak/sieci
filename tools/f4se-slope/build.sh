#!/usr/bin/env bash
# Builds CMB_Slope.dll (the F4SE plugin) with MinGW-w64 into Data/F4SE/Plugins.
#   Debian/Ubuntu: apt-get install gcc-mingw-w64-x86-64
# On Windows, MSYS2's mingw-w64-x86_64-gcc works the same way.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/../../Data/F4SE/Plugins"
mkdir -p "$OUT"
x86_64-w64-mingw32-gcc -std=c11 -O2 -Wall -Wextra -Werror -shared \
    -o "$OUT/CMB_Slope.dll" "$HERE/CMB_Slope.c" \
    -static-libgcc -Wl,--no-insert-timestamp -Wl,-s -lshell32
cp "$HERE/CMB_Slope.ini" "$OUT/CMB_Slope.ini"
echo "wrote $OUT/CMB_Slope.dll"
