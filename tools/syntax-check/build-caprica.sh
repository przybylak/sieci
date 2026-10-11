#!/usr/bin/env bash
# Builds the Caprica Papyrus compiler on Linux so the mod's scripts can be
# syntax-checked without Windows or the Creation Kit.
# Upstream Caprica only builds with MSVC; caprica-linux.patch + compat/ fix that.
#
# Needs: git, cmake, clang++, Boost (filesystem, program_options, container).
#   Debian/Ubuntu: apt-get install cmake clang libboost-filesystem-dev \
#                  libboost-program-options-dev libboost-container-dev
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${CAPRICA_WORKDIR:-$HERE/.caprica}"
COMMIT=9cd6d32ec2750adae329e81f7276dac95251e000

if [ ! -d "$WORK/src" ]; then
  git clone https://github.com/nikitalita/Caprica "$WORK/src"
fi
cd "$WORK/src"
git checkout -q "$COMMIT"
if git apply --check "$HERE/caprica-linux.patch" 2>/dev/null; then
  git apply "$HERE/caprica-linux.patch"
fi

mkdir -p build && cd build
CXX=clang++ cmake .. -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_FLAGS="-msse4.2 -I$HERE/compat -include $HERE/compat/wincompat.h -w -fms-extensions" >/dev/null
make -j"$(nproc)" >/dev/null
echo "Built: $WORK/src/build/Caprica/Caprica"
