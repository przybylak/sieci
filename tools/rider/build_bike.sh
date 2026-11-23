#!/usr/bin/env bash
# Builds the bike's meshes, textures and materials into a Data tree, in stages:
#   export    harley_meshes.py --stage export: the finished shapes into the stage folder ($STAGE; a shape's file is
#             rewritten only when it changed, so the texture stage's caches keep the rest)
#   art       bike_art.py: our own art (the dial, the badge, the lens patterns, the brake discs, the mirror's cube faces)
#   textures  bike_textures.py (Blender): each shape's UVs, the bakes from the full model, the DDS textures and
#             both materials files per material (Textures/CMB/Bike, Materials/CMB/Bike); ONLY=<labels> does part
#             of it (each call well under 10 minutes; a per-label cache keeps what's done), QUICK=1 small bakes
#   build     harley_meshes.py --stage build: the nifs with the stage's UVs and the materials named (the parked
#             and the three worn ones, and since the 2026-11-01a build CMB_BikeView.nif, the bike in first person),
#             CMB_BikeParts.ini and CMB_BikeFit.json
#   cables    bar_cables.py (since 2026-11-15b): the cables that hang from the bars, cut out of the fixed shape into
#             their own shape that turns with the bars (test 53: the right-hand ones floated), in the worn and view nifs
#             in place; a nif already cut is left as it is; CABLES=0 skips it (2026-11-15a's nifs)
#   emblems   look_emblems.py (since 2026-11-16a, C3): the 3D helmet emblems (Enclave, Brotherhood of Steel), four shapes
#             added in place to all five nifs, each hidden on its own materials file until a tank option swaps it on;
#             then emblem_art.py: their textures (helms_d/_n/_s/_g) and 10 materials files; a nif that has them already
#             is left as it is; EMBLEMS=0 writes the nifs as they are (2026-11-15b's) and no art
#   shells    look_shells.py (since 2026-11-21a, art build B): the two wear shells (static_wear over static_paint,
#             fork_wear over fork_paint) and the front fender's badge patch (fork_badgeFront) added in place to all five
#             nifs, each hidden on its own materials file until a look option swaps it on, and the rear fender patch
#             raised over the wear; their six materials files; a nif that has them already is left as it is; SHELLS=0
#             writes the nifs as they are (2026-11-17a's) and no materials file. Since 2026-11-22a also the paint
#             condition shells (static_paintwear, fork_paintwear), the wear shells on the exhaust, the engine's covers
#             and the fork lowers, static_wear lifted over the badges, and every overlay shell's alpha property and own
#             file blending (PAINTWEAR=0, PART_SHELLS=0, BADGE_LIFT=0, OVERLAY_BLEND=0 each leave its part out: all four 0
#             give 2026-11-21a's nifs and materials files)
#   stand     look_stand.py (since 2026-11-22a, test 58's wish): the model's side stand leg turned down about its pivot bolt
#             in CMB_BikeParked.nif only (the ridden and view nifs keep it folded), so the parked bike leans on it; a nif
#             whose stand is down already is left as it is; STAND=0 writes it as it is (the shells stage's)
#   check     check_bike_meshes.py over the Data tree (and against $REFERENCE if given)
#   fallback  harley_meshes.py --uvs none instead of export..build: palette textures, no materials files
#             (27c's way; the emergency build), then check it with "check"
# usage: [VAR=value ...] tools/rider/build_bike.sh [stage ...]     (default: export art textures build cables emblems shells stand check)
# Inputs, from the environment:
#   PYNIFLY     PyNifly's io_scene_nifly folder                                     (every stage but art)
#   GLTF        the model's scene.gltf                                              (export, textures, build, fallback)
#   VANILLA     the game's meshes/setdressing/vehicles/motorcycle/motorcycle_clean.nif (export, build, fallback)
#   SEAT        the riding clips' folder (Meshes/Actors/Character/Animations/MT/CMB_Rider) for the rider nifs
#   DATA        the output Data tree                                                (required)
#   STAGE       the stage folder (default: $DATA/../bike_stage: with DATA=<repository>/Data, <repository>/bike_stage,
#               which .gitignore leaves out)
#   BLENDER_PY  a Python with Blender's bpy module                                  (textures)
#   DDS_PY      a Python with the DDS encoders (see bike_textures.py)               (textures, emblems)
#   REFERENCE   a previous build's Meshes/CMB: CMB_BikeParts.ini's keys and CMB_BikeFit.json compared (check)
#   MATERIALS   the materials' shader values (default: bike_materials.json here, if it's there)
#   MESH_ARGS   more harley_meshes.py arguments, e.g. "--tris 90000"
#   DISC_BORE   shared (the default since 2026-11-02a: the brake discs' bore where the art paints it) or bolts (the
#               2026-11-01a build's, its nifs and disc art byte for byte): harley_meshes.py and bike_art.py --disc-bore;
#               the export writes it into the stage manifest, and art and build refuse another
#   CABLES      1 (the default since 2026-11-15b) or 0 (the nifs as harley_meshes.py wrote them): the cables stage
#   EMBLEMS     1 (the default since 2026-11-16a) or 0 (the nifs as the cables stage left them, no helmet art): the
#               emblems stage
#   SHELLS      1 (the default since 2026-11-21a) or 0 (the nifs as the emblems stage left them, no materials file):
#               the shells stage
#   PAINTWEAR, PART_SHELLS, BADGE_LIFT, OVERLAY_BLEND
#               1 (the defaults since 2026-11-22a) or 0: the shells stage's paint condition shells, part shells,
#               static_wear over the badges and the overlay shells' blending alpha property and own files
#               (look_shells.py --paintwear, --parts, --badge-lift, --overlay-blend); all four 0: 2026-11-21a's nifs
#   STAND       1 (the default since 2026-11-22a) or 0 (the parked nif as the shells stage left it): the stand stage
#   PYTHON      the Python for export, art, build, cables, emblems, shells, stand, fallback and check: 3.10+ with numpy and fast_simplification
#               (default python3; on Windows' Git Bash, where a python.org install has no python3, e.g. PYTHON=python
#               or PYTHON="py -3"). It runs with -I, which leaves out the user's site-packages (pip install --user):
#               install the two into that Python itself
# The outputs mix the model (CC-BY-4.0, credit its author) with the vanilla nif's collision: they are not
# committed to the repository.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
: "${DATA:?DATA (the output Data tree) is required}"
STAGE="${STAGE:-$DATA/../bike_stage}"
MESH_ARGS="${MESH_ARGS:-}"
DISC_BORE="${DISC_BORE:-shared}"
read -r -a PY <<< "${PYTHON:-python3}"   # a command with its arguments ("py -3")
MATERIALS="${MATERIALS:-$HERE/bike_materials.json}"
materials=()
[ -f "$MATERIALS" ] && materials=(--materials "$MATERIALS")
stages=("$@")
[ ${#stages[@]} -eq 0 ] && stages=(export art textures build cables emblems shells stand check)

need() { for v in "$@"; do [ -n "${!v:-}" ] || { echo "build_bike.sh: $v is required for this stage" >&2; exit 2; }; done; }

meshes() {   # harley_meshes.py with the build's own arguments, then the given ones
    need PYNIFLY GLTF VANILLA
    local seat=()
    [ -n "${SEAT:-}" ] && seat=(--seat "$SEAT")
    mkdir -p "$DATA/Meshes/CMB" "$DATA/Textures/CMB"
    # shellcheck disable=SC2086
    "${PY[@]}" -I "$HERE/harley_meshes.py" --pynifly "$PYNIFLY" --gltf "$GLTF" --vanilla "$VANILLA" \
        --out "$DATA/Meshes/CMB" --textures "$DATA/Textures/CMB" "${seat[@]}" --disc-bore "$DISC_BORE" $MESH_ARGS "$@"
}

for stage in "${stages[@]}"; do
    started=$(date +%s)
    echo "== $stage"
    case "$stage" in
        export)
            mkdir -p "$STAGE"
            meshes --stage export --stage-dir "$STAGE" "${materials[@]}" ;;
        art)
            "${PY[@]}" -I "$HERE/bike_art.py" --out "$STAGE/art" --disc-bore "$DISC_BORE" --stage-manifest "$STAGE/manifest.json" ;;
        textures)
            need GLTF BLENDER_PY DDS_PY
            extra=()
            [ -n "${ONLY:-}" ] && extra+=(--only "$ONLY")
            [ -n "${QUICK:-}" ] && extra+=(--quick)
            "$BLENDER_PY" -I "$HERE/bike_textures.py" --stage-dir "$STAGE" --gltf "$GLTF" \
                --materials "$MATERIALS" --art "$STAGE/art" --out "$DATA" \
                --dds-python "$DDS_PY" "${extra[@]}" ;;
        build)
            meshes --stage build --stage-dir "$STAGE" "${materials[@]}" ;;
        fallback)
            meshes --uvs none "${materials[@]}" ;;
        cables)
            "${PY[@]}" -I "$HERE/bar_cables.py" --data "$DATA" --out "$DATA/Meshes/CMB" --bar-cables "${CABLES:-1}" \
                ${PYNIFLY:+--pynifly "$PYNIFLY"} ;;
        emblems)
            need PYNIFLY
            "${PY[@]}" -I "$HERE/look_emblems.py" --data "$DATA" --out "$DATA/Meshes/CMB" --emblems "${EMBLEMS:-1}" \
                --pynifly "$PYNIFLY" "${materials[@]}"
            if [ "${EMBLEMS:-1}" != 0 ]; then
                need DDS_PY
                "$DDS_PY" -I "$HERE/emblem_art.py" --data "$DATA" "${materials[@]}"
            fi ;;
        shells)
            need PYNIFLY
            bgsm_out=()
            [ "${SHELLS:-1}" != 0 ] && bgsm_out=(--bgsm-out "$DATA")
            "${PY[@]}" -I "$HERE/look_shells.py" --data "$DATA" --out "$DATA/Meshes/CMB" --shells "${SHELLS:-1}" \
                --paintwear "${PAINTWEAR:-1}" --parts "${PART_SHELLS:-1}" --badge-lift "${BADGE_LIFT:-1}" \
                --overlay-blend "${OVERLAY_BLEND:-1}" \
                --pynifly "$PYNIFLY" "${materials[@]}" "${bgsm_out[@]}" ;;
        stand)
            "${PY[@]}" -I "$HERE/look_stand.py" --data "$DATA" --out "$DATA/Meshes/CMB" --stand "${STAND:-1}" \
                ${PYNIFLY:+--pynifly "$PYNIFLY"} ;;
        check)
            need PYNIFLY
            ref=()
            [ -n "${REFERENCE:-}" ] && ref=(--reference "$REFERENCE")
            stage_arg=()
            [ -f "$STAGE/manifest.json" ] && stage_arg=(--stage-dir "$STAGE")
            "${PY[@]}" -I "$HERE/check_bike_meshes.py" --pynifly "$PYNIFLY" --data "$DATA" "${ref[@]}" "${stage_arg[@]}" ;;
        *)
            echo "build_bike.sh: unknown stage $stage (export art textures build cables emblems shells stand check fallback)" >&2
            exit 2 ;;
    esac
    echo "== $stage done in $(( $(date +%s) - started )) s"
done
