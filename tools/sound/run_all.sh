#!/bin/sh
# Builds the engine's loop set from demodave's recording and renders the demo ride through it (about 8 minutes on
# 4 cores: the grains 2, the pieces 2, the tone match 4, the renders a few seconds).
#
#   sh tools/sound/run_all.sh <demodave's idle.wav> [out dir]
#
# The out dir (default tools/sound/out, which git ignores) gets:
#   loops/   the 13 WAVs the game plays (Data\Sound\FX\CMB) and loops.json: the idle, the start, the stop,
#            CMB_EngineCruiseLP.wav (the 2000 rpm loop on load, the plugin's On2000) and the nine more the plugin drives
#   demo/    CMB_engine_demo.wav (the model's renderer: the pitch glides within each frame) and
#            CMB_engine_demo_stepped.wav (the game's way: the pitch steps once a frame), each with its CSVs
#   work/    the grain and piece tools' outputs and every tool's log
# The last stage (hot_loops.py, since test 45's answer) takes every file of loops/ 2.5 dB hotter through a memoryless
# soft limiter (knee -6 dBFS, ceiling -1). HOT=0 leaves the set as build_loops.py writes it: test 45's set.
# With WATER=<example 1 as WAV> set (the 2026-11-06a build: "Cars driving on a wet road 3", Pixabay 101246, decoded first with
# ffmpeg -i <the mp3> -c:a pcm_s16le ex1.wav), make_water_loop.py also writes the 14th WAV the game plays, the mod's own
# wet-road water loop CMB_FxWaterRoadLP.wav, into loops/ with its water.json (exit 1 if one of its checks fails), and (the
# 2026-11-09a build) the 15th, the gentle wet road CMB_FxWaterRoadSoftLP.wav (--variant gentle) with its water_gentle.json.
# With CHECK=<dir> set, every WAV in loops/ is compared byte for byte with the one of the same name in <dir> (the
# cruise loop with CMB_EngineOn2000LP.wav when <dir> is a set built before it took the cruise's name, demo D's; a set
# built before test 45's answer, demo D's or test 45's, with HOT=0; each wet road only when <dir> has it).
#
# The recording is someone else's work (Creative Commons 0, but still not ours to re-host): it and everything built
# from it stay out of the repository. Every tool runs isolated (python3 -I -B) with its files as arguments.
set -e
if [ $# -lt 1 ] || [ ! -f "$1" ]; then
    echo "usage: sh $0 <demodave's idle.wav> [out dir]" >&2
    exit 2
fi
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=$1
OUT=${2:-$HERE/out}
PY="nice -n 10 python3 -I -B"
mkdir -p "$OUT/work" "$OUT/loops" "$OUT/demo"
t0=$(date +%s)
echo "grains (make_grain_loops.py) ..."
$PY "$HERE/make_grain_loops.py" --idle "$SRC" --out "$OUT/work/grains" --unlimited "$OUT/work/grains_unlimited" \
    > "$OUT/work/grains.log" 2>&1
echo "pieces (make_piece_loops.py) ..."
$PY "$HERE/make_piece_loops.py" --idle "$SRC" --out "$OUT/work/pieces" > "$OUT/work/pieces.log" 2>&1
echo "the loop set (build_loops.py) ..."
$PY "$HERE/build_loops.py" --grains "$OUT/work/grains" --unlimited "$OUT/work/grains_unlimited" \
    --pieces "$OUT/work/pieces" --out "$OUT/loops" > "$OUT/work/build.log" 2>&1
if [ "${HOT:-1}" != 0 ]; then
    echo "hotter (hot_loops.py) ..."
    $PY "$HERE/hot_loops.py" --in "$OUT/loops" --out "$OUT/loops" > "$OUT/work/hot.log" 2>&1
fi
if [ -n "${WATER:-}" ]; then
    echo "the wet road (make_water_loop.py) ..."
    $PY "$HERE/make_water_loop.py" --ex1 "$WATER" --out "$OUT/loops" > "$OUT/work/water.log" 2>&1
    echo "the gentle wet road (make_water_loop.py --variant gentle) ..."
    $PY "$HERE/make_water_loop.py" --variant gentle --ex1 "$WATER" --out "$OUT/loops" > "$OUT/work/water_gentle.log" 2>&1
fi
echo "the demo ride (render.py) ..."
$PY "$HERE/render.py" --loops "$OUT/loops" --out "$OUT/demo/CMB_engine_demo.wav" > "$OUT/work/render.log" 2>&1
$PY "$HERE/render.py" --loops "$OUT/loops" --out "$OUT/demo/CMB_engine_demo_stepped.wav" --stepped \
    > "$OUT/work/render_stepped.log" 2>&1
echo "done in $(( $(date +%s) - t0 )) s: $OUT/loops ($(ls "$OUT/loops" | grep -c '\.wav$') WAVs), $OUT/demo"
if [ -n "$CHECK" ]; then
    bad=0
    for f in "$OUT"/loops/*.wav; do
        ref=$CHECK/$(basename "$f")
        if [ ! -f "$ref" ] && [ "$(basename "$f")" = CMB_EngineCruiseLP.wav ]; then
            ref=$CHECK/CMB_EngineOn2000LP.wav
        fi
        if [ ! -f "$ref" ] && { [ "$(basename "$f")" = CMB_FxWaterRoadLP.wav ] || [ "$(basename "$f")" = CMB_FxWaterRoadSoftLP.wav ]; }; then
            echo "no ref    $(basename "$f")"
            continue
        fi
        if cmp -s "$f" "$ref"; then
            echo "same      $(basename "$f")"
        else
            echo "DIFFERENT $(basename "$f")"
            bad=1
        fi
    done
    exit $bad
fi
