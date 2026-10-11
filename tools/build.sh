#!/usr/bin/env bash
# Regenerates Data/CommonwealthMotorbike.esp and runs every check that works
# without the game: plugin structure + property cross-check, and the Papyrus
# syntax check. Needs the .NET 8 SDK; the syntax check also needs Caprica
# (tools/syntax-check/build-caprica.sh).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GEN="$ROOT/tools/esp-generator"
ESP="$ROOT/Data/CommonwealthMotorbike.esp"
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1

echo "== Generating plugin"
dotnet build -c Release "$GEN/EspGenerator.csproj" -o "$GEN/bin/out" >/dev/null
dotnet "$GEN/bin/out/EspGenerator.dll" "$ESP" >/dev/null
echo "wrote $ESP"
TEMPLATE="$ROOT/tools/rider/template/CMB_RiderPose.esp"
dotnet "$GEN/bin/out/EspGenerator.dll" --rider-template "$TEMPLATE" >/dev/null
echo "wrote $TEMPLATE"

echo "== Plugin vs scripts"
dotnet "$GEN/bin/out/EspGenerator.dll" --dump "$ESP" | python3 -I "$GEN/check_plugin.py" "$ROOT/Data/Scripts/Source/User"

echo "== Papyrus syntax check"
"$ROOT/tools/syntax-check/check.sh"
