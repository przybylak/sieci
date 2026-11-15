#!/usr/bin/env bash
# build_at_base.sh <worktree> [image base] - runs the worktree's own tools/f4se-slope/build.sh (unchanged,
# -Werror) with the DLL's image base fixed; the default base is that of the DLL committed at the
# worktree's HEAD, so an unchanged source gives the committed bytes back. Then compares with HEAD's DLL.
# Its helpers are under $CMB_ROOT/bin (CMB_ROOT default /opt/cmb).
set -euo pipefail
WT="$(cd "$1" && pwd)"; BASE="${2:-}"
CMB="${CMB_ROOT:-/opt/cmb}"
mkdir -p "$CMB/build"
HEADDLL="$(mktemp "$CMB/build/head.XXXXXX.dll")"
git -C "$WT" show HEAD:Data/F4SE/Plugins/CMB_Slope.dll > "$HEADDLL"
if [ -z "$BASE" ]; then
  BASE="$(python3 -I -c 'import struct,sys; d=open(sys.argv[1],"rb").read(); o=struct.unpack_from("<I",d,0x3c)[0]; print(hex(struct.unpack_from("<Q",d,o+48)[0]))' "$HEADDLL")"
fi
echo "image base $BASE"
PATH="$CMB/bin/basewrap:$PATH" CMB_IMAGE_BASE="$BASE" bash "$WT/tools/f4se-slope/build.sh"
sha256sum "$WT/Data/F4SE/Plugins/CMB_Slope.dll"
python3 -I "$CMB/bin/pecmp.py" "$WT/Data/F4SE/Plugins/CMB_Slope.dll" "$HEADDLL" || true
rm -f "$HEADDLL"
