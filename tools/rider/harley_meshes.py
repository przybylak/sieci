#!/usr/bin/env python3
"""Builds the bike meshes from a glTF model instead of the game's own motorcycle.

Made for "Harley Davidson Iron 883 2015" by Nieve5677 (https://sketchfab.com/niev),
CC-BY-4.0, as Sketchfab's glTF download of it: 112 meshes, 1.3 million triangles, twelve
materials that are all the same placeholder grey (no textures came with it), a raw frame
that's Z up with the front at -Y and the ground at z = 0 (the same way round as the vanilla
motorcycle), 548 units long. Any glTF laid out like that will do.

What it writes (the same four files build_bike_meshes.py does, see there for why):

  CMB_BikeParked.nif      the vanilla motorcycle nif with its own shape hidden and ours added,
                          so its collision (what you bump into and what the reverse rays stop
                          at) stays as it was; the model scaled to the vanilla bike's length
  CMB_BikeWorn.nif        ours as a wearable armor mesh on AnimObjectA (the seat over the
                          character's origin)
  CMB_BikeWornRider.nif   the same hanging off the rider's COM (with --seat; F for the female
  CMB_BikeWornRiderF.nif  rider)
  CMB_BikeView.nif        (since the 2026-11-01a build; --view 0 leaves it out) the bike in first
                          person: the worn nif's shapes unskinned, in full precision, under a hidden
                          NiNode CMB_BikeView, no collision; the plugin shows and places a
                          script-placed copy of it in first person, where the game hides the worn one
  Textures/CMB/CMB_Bike_d/_n/_s.dds     with --uvs none only (the fallback build): palette
                          textures, each material one block of a 256x8 strip (no mipmaps, so
                          blocks never blend at a distance), every vertex's UV at its
                          material's block; the textured build's textures and materials
                          (Textures/CMB/Bike, Materials/CMB/Bike) come from bike_textures.py
  CMB_BikeFit.json        where this model's seat, grips and pegs are, for riding_anims.py --fit:
                          the riding clips are posed to the bike (hips on the seat, hands on the
                          grips, feet on the pegs), so they're rebuilt for this model, and then
                          this script is run again with --seat for the bike that hangs off the
                          seated rider (the seat height moved)
  CMB_BikeParts.ini       the worn bike's moving parts for the F4SE plugin, in its mesh space: the
                          axles and the wheel radius, the steering axis (SteerPoint, SteerAxis) and
                          the line a shape's culling sphere must sit ahead of to count as the bar
                          assembly (FrontMinY), how far the bars turn (BarAngle), the headlamp's
                          lens and its axis (LampPoint, LampAxis), and Grip, the +X grip's centre,
                          the very point the fit file's grip_r holds and the clips put the palm on:
                          the plugin rolls the hand round the grip about it (test 38: it rolled about
                          the wrist node, 6.5 units from the grip, so the palm left the bar), and
                          the speedometer needle's pivot and scale (NeedlePoint, NeedleAxis,
                          NeedleZero, NeedleMax, NeedlePerMph)

The geometry: each material's meshes are merged, welded and split into connected pieces, and
each piece is cut down with quadric edge collapse (fast_simplification) towards its share of
--tris by surface area (so the tyres keep their shape and a bolt gets a few triangles), the
simplifier's error capped so that no piece is crushed to reach its share: one that can't get
there within the cap keeps more, so the default 90000 comes out at about 225k triangles (tests
40 and 41, AGG_CAP, FINE_AGG; small pieces, the lenses, the painted panels and the small chrome
are kept whole, and only the specks under SPECK_AREA are dropped). Each corner's shading normal
is the glTF's own (at the closest point of its piece's surface where the piece was cut down),
a vertex split in two or more where its corners' normals part, so the model's hard edges stay
hard and its curves round (gltf_normals). Since the 2026-11-01a build a closed piece the cut
crushed (under 0.6 of its volume kept: the seat's piping cord) is cut again at twice its share
till it keeps 0.8 (the volume guard, --volume-guard 0 for 2026-10-31a's cut), and the brake
discs are the mod's own drilled discs (bike_pieces.disc_pieces, --disc model for the model's,
whose dented plates shade by the averaged normals).
The parts go into 30 shapes (LABELS; 28 with --disc model; since the 2026-11-07a build 33, LOOK_LABELS: static_badge
split into the two tank plates and the rear roundel, and our patch on the rear fender, the customisation slots' own
shapes, --look-slots 0 for the 30; since the 2026-11-08a build 49, look_labels(): the licence plate split from
static_black with its text overlay, --look-plate, and the seven rim styles on each wheel, --look-rims), by what moves them (role_of: the fixed bike; the bar
assembly, "front": the bars, grips, levers, mirrors, the fork tubes, both triple clamps, the
speedometer and the headlamp, which the plugin turns about the steering axis with the rider's
steering; the fork's lower end, "fork": the sliders, the front mudguard, the brake caliper, the
axle and its hardware, which turn with the bars and also ride up and down with the front
wheel's suspension travel, so the mudguard stays over the tyre and the axle in the fork ends;
and the two wheels, which spin) and then by what they are (label_of, by the glTF mesh a piece
came from, else its material): one shape per surface that wants its own shader and texture set
(the paint, chrome, exhaust, engine, black, seat, glass and badge of the fixed bike; chrome,
black, glass and the lamp's lit parts at the bars; the tyre with its hub, the rim and the brake
disc of each wheel) and one per thing the plugin moves or lights on its own (the speedometer needle, the
dial's backlight, the tail and brake light shells over the red lens, each mirror variant).
A shape's name is <stem>_<label> and says its role (static_, rear_, front_, fork_, wheelF_,
wheelR_; the plugin reads the role from the name first and from the culling sphere
otherwise, CMB_BikeParts.ini), so it can be told apart however many there are (the plugin
holds up to 48 since the 2026-10-31a build; before, at most 16, which is why 27c had twelve), and the game
shows at most 65535 vertices per shape (MAX_VERTS keeps a margin for the UV seams; the plugin holds 64 since the
2026-11-08a build). The
fallback build (--uvs none) shades them from palette textures as 27c did (MATERIALS below;
the body colour is --body); the textured build (--stage) names a materials file per shape
and takes each shape's shader values from bike_materials.json (see BUILD STAGES).

  python harley_meshes.py --pynifly <io_scene_nifly> --gltf <...>/scene.gltf \
      --vanilla <...>/meshes/setdressing/vehicles/motorcycle/motorcycle_clean.nif \
      --out <Data>/Meshes/CMB --textures <Data>/Textures/CMB \
      [--seat <Data>/Meshes/Actors/Character/Animations/MT/CMB_Rider] [--tris 90000] [--body 7a1118]
      [--sit 0.27] [--grip 29.4,-10.7,96] [--peg 19,6,27]
      [--stage export|build --stage-dir S] [--materials bike_materials.json] [--uvs none|stage] [--bgsm 0|1]
      [--volume-guard 1|0] [--disc ours|model] [--disc-bore shared|bolts] [--view 1|0] [--look-slots 1|0]
      [--look-rims 1|0] [--look-plate 1|0]

BUILD STAGES (build_bike.sh runs them): with no --stage, the fallback build (--uvs none): palette
textures, no materials files (the 27c way). The textured build is three steps: --stage export
writes the finished shapes (S/manifest.json and S/shapes/<label>.npz, in the parked frame: the
positions after the normal split, the triangles as written, each triangle's material, glTF mesh
and piece, and the fixed UVs of the dial, needle, badge, light shells and discs; a shape's file is rewritten only when
its arrays changed, so the texture stage's caches keep what didn't); bike_textures.py
unwraps them and bakes their textures and materials, returning S/uv/<label>.npz (a UV per
triangle corner); --stage build makes the same shapes again (they must match the export), splits
each vertex where its corners' UVs differ (the seams) and writes the nifs naming
Materials\\CMB\\Bike\\<mat>_worn.bgsm (worn) and <mat>.bgsm (parked), with the same values and
textures in the nif's own shader block. The game reads the named file and doesn't fall back to
the block when it is missing (test 47: the bike went magenta), so the materials files must ship
with the meshes; the block's values serve tools and --bgsm 0, which writes empty material names
(the shader block alone, as 27c).

The rider sits --sit of the way along the seat from its front edge (0.27: snug behind the
tank, as on the real thing, which keeps the long reach to the bars within arm's length even
with the bars turned 20 degrees; test 20's 0.35 left the outer hand short of its grip).
--grip and --peg are the grip's centre and the peg's top on the bike's +X side in the model's
own frame (measured on this model; the other side mirrors them). The grip is the rubber
sleeve on the bar's end: a cylinder of radius 2.3, 16 long, its centre at (29.4, -10.7, 96.0)
by a principal-axis fit of its vertices (test 38); the brake lever runs 6 units ahead of it,
parallel, thinner (radius 1, tapering to a ball end), and the earlier grip points (test 36's
x 24.5 was the lever clamp; a fit of the vertices with |x| 27-39 gives the lever) put the
hands on the lever perches and switch housings. The model is scaled to the
vanilla bike's length, so the collision and the plugin's clearances still fit; that makes it
about a quarter bigger than the real bike next to the character, like the vanilla bike.

The output mixes the model (CC-BY-4.0: credit Nieve5677 wherever it's shared) with the
vanilla nif's collision (Bethesda's), so it isn't committed to the repository.
"""

import argparse
import json
import math
import os
import struct
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_bike_meshes import _block_offsets, apply, mat_mul, read_seat, rigid_inverse  # noqa: E402
from nearest import TriangleGrid, nearest_vertex  # noqa: E402

VANILLA_LENGTH = 196.0   # the vanilla motorcycle along Y (its bounds are y[-98, 98])
HIPS_Y_WORN = -5.0       # the middle of the buttocks zone riding_anims.py seats (worn y -14..4)
GROUND_FOOT_L = [-30.0, 6.0, 0.0]   # the left foot at a stop, as for the vanilla bike (this one is as wide)
MODEL_NAME = "Harley Davidson Iron 883 2015 by Nieve5677 (CC-BY-4.0)"
BIKE_BONE = "AnimObjectA"
VIEW_NODE = "CMB_BikeView"   # the view nif's hidden node and its shapes' stem ([View] Node in CMB_Slope.ini)
PALETTE_W, PALETTE_H, BLOCK = 256, 8, 8   # 32 blocks of 8x8 (19 used)
PALETTE = "CMB_Bike"   # textures\CMB\CMB_Bike_d/_n/_s.dds: the fallback build's (27c's had another stem)

# name: (rgb, alpha, specular 0-255, gloss 0-255, env mask 0-255, shape)
MATERIALS = {
    "chrome":      ((112, 114, 120), 255, 150, 230, 150, "metal"),
    "silver":      ((120, 122, 128), 255, 120, 190, 110, "metal"),
    "tex2":        ((48, 48, 52), 255, 110, 170, 70, "metal"),       # the air cleaner cover: dark metal
    "body":        (None, 255, 90, 200, 70, "metal"),                # --body
    "logo_decals": ((36, 36, 38), 255, 90, 150, 30, "metal"),        # the tank badges, no texture to show: satin black
    "black_m":     ((24, 24, 26), 255, 70, 95, 25, "matte"),          # engine, frame, forks: black metal
    "tex1":        ((28, 28, 30), 255, 75, 105, 30, "matte"),
    "material":    ((16, 16, 16), 255, 28, 35, 0, "matte"),           # "gum": tyres, grips, cables
    "leather":     ((34, 27, 22), 255, 45, 65, 0, "matte"),
    "glass":       ((150, 160, 170), 90, 120, 240, 120, "glass"),     # the headlight
    "o_glass":     ((232, 128, 24), 150, 150, 230, 90, "glass"),      # indicators
    "r_glass":     ((196, 24, 24), 150, 150, 230, 90, "glass"),       # the tail light
    "lamp_black":  ((18, 18, 20), 255, 120, 235, 110, "metal"),       # our headlamp's bucket and projector: gloss black
    "lamp_led":    ((236, 242, 255), 255, 40, 60, 0, "glow"),         # its running-light ring and projector face: lit
    # Ours (bike_pieces.py): the mirror glass, the speedometer's dial and needle, the tail and brake light shells.
    "mirror":      ((70, 72, 76), 255, 200, 250, 230, "metal"),
    "dial":        ((14, 14, 15), 255, 60, 120, 0, "matte"),
    "needle":      ((235, 92, 24), 255, 90, 160, 0, "matte"),
    "tail_led":    ((150, 12, 10), 255, 40, 60, 0, "glow"),
    "brake_led":   ((255, 36, 24), 255, 40, 60, 0, "glow"),
}
# The materials by the names the texture stage knows them by (the manifest's "materials"): the glTF's "material" is the rubber
# ("gum") and "logo_decals" the badges.
STAGE_NAME = {"material": "gum", "logo_decals": "logo"}
# Test 20: with the first palette (chrome 176 grey, specular 255, mask 255) the forks, exhausts
# and the headlight face rendered flat white in the sun, and the tan tank badge showed as a
# patch; so chrome is a mid grey with the reflection at 60%, the lens darker and duller, the
# badge satin black.

ROLES = ("", "front", "fork", "wheelF", "wheelR")   # static; turns with the bars; turns and rides with the front wheel; spins; spins
BAR_HEIGHT = 85.0   # above this (parked frame) and ahead of the seat it's the bar assembly
# A piece of the bar assembly whose centre is below this (parked frame, z up, the ground at 0)
# is the fork's lower end, which moves with the front wheel's suspension travel. On this model
# the sliders' centres are at z 41 (they run 27..60), the front mudguard's at 50 (30..62), the
# brake caliper's at 31, the axle's at 30, the rubber fork boots' at 63 (56..70); the chrome
# fork tubes' at 69 (58..88) and the lower triple clamp's at 86: the line goes between the boots
# and the tubes. The boots go with the sliders they're clamped to; compressed 10 their tops
# reach z 80, a unit under the clamp. (Test 37: the fork legs and the mudguard didn't take the
# wheel's offset, so at +10 the tyre went into the mudguard and the axle left the fork ends.)
FORK_SPLIT_Z = 66.0
RAKED_BEHIND = 8.0   # role_of: the lower clamp's centre is 2.5 behind the raked axis, its bolts 3.5, the stem nut 6.5

# The shapes (the 2026-10-31a build), in the order they're made (the culling spheres are written in that order), each
# with the role that moves it. The plugin tells the role from the name: "_static_" fixed, "_rear_tail" the running
# light and "_rear_brake" the brake light (fixed, lit or specked), "_front_" the bar assembly ("_front_glow" and
# "_front_dialglow" lit with the headlamp, "_front_needle" the speedometer needle, "_front_mirror*" the mirror
# variants), "_fork" the fork's lower end, "_wheelF" and "_wheelR" the wheels.
LABELS = (
    ("static_paint", ""), ("static_chrome", ""), ("static_exhaust", ""), ("static_engine", ""), ("static_black", ""),
    ("static_seat", ""), ("static_glass", ""), ("static_badge", ""), ("rear_tail", ""), ("rear_brake", ""),
    ("front_chrome", "front"), ("front_black", "front"), ("front_glass", "front"), ("front_glow", "front"),
    ("front_dial", "front"), ("front_dialglow", "front"), ("front_needle", "front"),
    ("front_mirrorStock", "front"), ("front_mirrorUnderEgg", "front"), ("front_mirrorUnderD", "front"),
    ("fork_chrome", "fork"), ("fork_paint", "fork"), ("fork_black", "fork"), ("fork_glass", "fork"),
    ("wheelF_tyre", "wheelF"), ("wheelF_rim", "wheelF"), ("wheelF_disc", "wheelF"),
    ("wheelR_tyre", "wheelR"), ("wheelR_rim", "wheelR"), ("wheelR_disc", "wheelR"),
)
ROLE_OF_LABEL = dict(LABELS)
# Since the 2026-11-01a build the brake discs are our own (bike_pieces.disc_pieces), each its own shape: --disc model
# leaves these two out and keeps the model's discs in the tyres' shapes (2026-10-31a's 28).
DISC_LABELS = ("wheelF_disc", "wheelR_disc")
DISC_MESHES = (78, 100)             # the model's brake discs (front, rear): their plates, the silver pieces not small
FIXED_UV = ("static_badge", "rear_tail", "rear_brake", "front_dial", "front_dialglow", "front_needle",
            "wheelF_disc", "wheelR_disc")   # our art's layout
WORN_ONLY = ("rear_tail", "rear_brake", "front_dialglow")   # lit overlays: the parked bike shows the plain lens and dial
# The front end's roles (the bar assembly, the lower fork, the front wheel): since the 2026-11-10a build their worn
# shapes cast as their parked ones (load_shaders; test 34 to 2026-11-09a: none, for the headlamp at the lens)
FRONT_ROLES = ("front", "fork", "wheelF")
PARKED_HIDDEN = ("front_mirrorUnderEgg", "front_mirrorUnderD")   # variants: in the parked nif, hidden by the node flag
MIRROR_VARIANTS = ("front_mirrorStock", "front_mirrorUnderEgg", "front_mirrorUnderD")
# The customisation build (2026-11-07a, --look-slots 1, the default; 0 = LABELS, 2026-11-06a's nifs byte for byte): its
# slots' shapes, each the source of its own materials file, so a material swap (MSWP) reaches that one shape alone.
# static_badge splits by island into the tank plates, TankL (x > 0 parked: the bike's left) and TankR (x < 0), glTF mesh
# BADGE_TANK_MESH, and the rear roundel (mesh BADGE_ROUNDEL_MESH, in no slot in C1): the same triangles and fixed UVs,
# their materials static_badge's values over its textures ("textures_of"), and as their culling sphere the three's
# union, 2026-11-06a's static_badge sphere (the plates' own sit at worn y 32.5, past FrontMinY's fixed side, 24.9:
# they would move it, and with [Parts] RolesByName=0 the sphere rule would turn them with the bars). And static_badgeFender,
# ours (bike_pieces.fender_badge_patch) on the rear fender's top (glTF mesh REAR_FENDER_MESH of static_paint), invisible
# (materials "static_badgeFender": alpha test 255, off's textures) until a badge is swapped onto it. In the parked nif the
# under-bar mirrors (PARKED_OFF) show instead of being node-hidden, naming <label>_off.bgsm (invisible), so an MSWP can
# show them (their own <label>.bgsm the swap's target); the worn and view nifs keep their materials (the plugin's speck).
BADGE_SPLIT = ("static_badgeTankL", "static_badgeTankR", "static_badgeRear")
FENDER_BADGE = "static_badgeFender"
BADGE_TANK_MESH, BADGE_ROUNDEL_MESH, REAR_FENDER_MESH = 2, 1, 14
LOOK_LABELS = sum((tuple((b, "") for b in BADGE_SPLIT + (FENDER_BADGE,)) if label == "static_badge" else ((label, role),)
                   for label, role in LABELS), ())
ROLE_OF_LABEL.update(LOOK_LABELS)
FIXED_UV = FIXED_UV + BADGE_SPLIT + (FENDER_BADGE,)
BADGE_UV = ("static_badge",) + BADGE_SPLIT   # bike_pieces.badge_uvs' layout
PARKED_OFF = ("front_mirrorUnderEgg", "front_mirrorUnderD")
# The second customisation build (2026-11-08a, C2; --look-rims 1 and --look-plate 1, the defaults; both 0 = LOOK_LABELS,
# 2026-11-07a's nifs byte for byte). The plate: glTF mesh 24 (PLATE_MESHES) out of static_black into static_plate, with
# fixed UVs of its own (bike_pieces.plate_uvs: the rear face read true from behind over 0..1, the rest on the design
# cell's strip), its materials static_black's values over its own re-sampled textures (static_plate_d/_n/_s); and ours,
# static_plateText (bike_pieces.plate_text_overlay: the text band 0.30 over the face), invisible until a text is swapped
# on, as static_badgeFender. static_black is assembled whole as 2026-11-07a's and split after, so the texture stage's
# UVs serve it less the plate's rows, and it keeps 2026-11-07a's culling sphere (the union with the plate's: FrontMinY
# and the sphere rules unmoved). The rims: bike_pieces.rim_style_pieces, one shape a style a wheel (RIM_STYLE_LABELS,
# wheelF_rim<Style> / wheelR_rim<Style>, roles wheelF / wheelR: they spin and steer as the tyres), made after the
# wheels are measured (measure_parts never sees them), fixed UVs in the rim atlas's cells, each its own materials file,
# invisible (bike_materials.json, as static_badgeFender) until a Rims option swaps its style on and the cast rim to
# off.bgsm; the plugin hides the styles not chosen on the worn and view bikes (its rim group).
RIM_STYLES = ("Laced", "Disc", "Star", "Turbine", "Prewar", "Atomic", "Scrap")   # bike_pieces.RIM_STYLES, rim 1-7
RIM_STYLE_LABELS = tuple((f"wheel{w}_rim{style}", f"wheel{w}") for style in RIM_STYLES for w in ("F", "R"))
PLATE_LABEL, PLATE_TEXT = "static_plate", "static_plateText"
C2_LABELS = ((PLATE_LABEL, ""), (PLATE_TEXT, "")) + RIM_STYLE_LABELS


def look_labels(rims=True, plate=True):
    """The customisation build's shapes: LOOK_LABELS, with the plate's two after static_black (plate) and the 14 rim
    styles after wheelR_disc (rims)."""
    out = []
    for label, role in LOOK_LABELS:
        out.append((label, role))
        if plate and label == "static_black":
            out += [(PLATE_LABEL, ""), (PLATE_TEXT, "")]
    return tuple(out) + (RIM_STYLE_LABELS if rims else ())


ROLE_OF_LABEL.update(C2_LABELS)
FIXED_UV = FIXED_UV + tuple(label for label, _ in C2_LABELS)
OFF_MAT = "off"   # bike_materials.json's invisible material (Materials\CMB\Bike\off.bgsm, Textures\CMB\Bike\off_*.dds)
MAX_VERTS = 60000   # per shape, after the UV seams (the game's limit is 65535)
# Routing (label_of): the glTF meshes that go somewhere their material alone wouldn't send them.
DROP_MESHES = {9: "the speedometer's dial face (ours replaces it)"}
MIRROR_MESHES = (58, 59)            # the stock mirrors: housings and stems, glass
MIRROR_GLASS_MESH = 59
EXHAUST_MESHES = (101,)             # both pipes and the mufflers
PLATE_MESHES = (24,)                # the number plate (dark metal like the air cleaner cover, but not engine)
RIM_MESHES = (30, 31, 106, 107, 108, 109, 110, 111, 32, 98)   # the cast rims and their spoke trims
ENGINE_MESHES = (97, 103, 40, 16, 45, 85, 3)   # crankcase, cylinders, heads (rubber in the glTF), air cleaner, side
#                                     cover, the crankcase's round covers, the oil filter, the starter behind it
DIAL_MESH = 9
TAIL_LENS_MESH, SIGNAL_LENS_MESH = 95, 34   # r_glass: the tail lens (its rearmost piece), the rear signals' lenses
TANK_MESH = 13
# Where an under-bar mirror's stalk starts (worn, +X side): None leaves it to bike_pieces, which measured it under
# the switch housing on this model, (23.0, 41.0, 94.1); a first estimate from the videos was (23, 37.5, 97.5).
MIRROR_CLAMP = None
GRIP_RADIUS = 2.3                   # the grip sleeve's radius (see --grip)
MIRROR_CLEARANCE = 1.5              # least gap from a mirror to the tank with the bars at full lock
CONVEX_RADIUS = 35.0                # the stock mirror glass's normals: a sphere this far behind the glass (or
#                                     bike_pieces.MIRROR_CONVEX_R, the under-bar mirrors', if it has one)
#                                     (bike_pieces.MIRROR_CONVEX_R if it has one, so all the mirrors match)
OVERLAY_MIN = (("front_dialglow", "dial face", 0.25), ("front_needle", "dial face", 0.5),
               ("front_needle", "front_dialglow", 0.25), ("rear_tail", "tail lens", 0.25),
               ("rear_brake", "tail and signal lenses", 0.5), ("rear_brake", "rear_tail", 0.25))

# The decimation (decimate()). Test 40: the simplifier (Sp4cerat's quadric edge collapse in
# fast_simplification) collapses an edge while its error is under 1e-9 * (iteration + 3) ** agg,
# and at the agg 7 used until then that ends near 1.2e5, no bound at all: every piece went down
# to its area share however much shape that cost, and the repeat passes (up to four calls, each
# from the already-cut mesh's quadrics) crushed it further. The right grip was a blade, the
# speedo a crystal, the switch housing a box, the rims 12-14-sided with shards across the spokes
# (their outline 20.7 to 24.6 from the axle where the source's is 23.7-23.8), a cable lost its
# upper two thirds (32.8 units off at worst), the fork boots had slits. A bigger budget doesn't
# help those (1.53 times it left them as crushed). Now one call per piece with its share as the
# target and the error capped (AGG_CAP: agg 4.5 stops at a summed squared plane distance of
# about 1.14 game units squared, 4.0 at about 0.11, the tighter one on the env-mapped and glass
# parts, where the cubemap shows each facet: at 4.5 the fuel cap and the indicator lenses kept
# 9-12-sided outlines). A piece that can't reach its share within the cap stops short of it, so
# --tris 90000 comes out at about 225k triangles; the source surface's 95th percentile distance
# from the build went from 1.65 units to 0.06, its worst from 12.2 to 1.2.
AGG_CAP = {"matte": 4.5, "metal": 4.0, "glass": 4.0}
KEEP_TRIS = 300   # up to this many triangles a piece is kept whole (its share would only nick it)
KEEP_FRAC = 0.6   # and so is one whose share is this much of what it has or more
# Cut at FINE_AGG whatever they're made of: the bar assembly's pieces, in the rider's view all
# the time (at matte's 4.5 the black mirror housings, 2,048 source triangles cut to 156 and 174,
# poked through the chrome mirror glass on them as a dark wedge, at agg 7 too on the other
# mirror; and the right master cylinder, 4,944 cut to 562, swallowed the chrome ring flush on
# its lid down to a broken crescent; 3,500 more triangles on its 30 black pieces than at 4.5,
# where the housings kept whole would cost 38,700 and look no different), and any piece of
# FINE_AREA (units squared) or more off the wheels, the big covers (at 4.5 a flat bevel cut
# across the air cleaner cover's lower half; 5,500 more triangles, on 34 of them). The metal
# and the glass are at 4.0 already, so it's the matte this tightens.
FINE_AGG = 4.0
FINE_AREA = 300.0
# Kept whole (test 41): the painted panels and badges (PAINTED: the tank, both fenders, the
# tank badges): at 4.0 the rear fender's rolled lip, the bike's nearest part to the riding
# camera, was cut to a row of sawtooth teeth, and still tore at 2.5 (77% of it kept); whole
# they cost 10,800 more triangles. And the chrome and silver pieces (BRIGHT) of up to
# BRIGHT_TRIS triangles and BRIGHT_AREA or more off the wheels, where the cubemap shows every
# facet: at 4.0 the fuel cap's dome (1,092 cut to 161) reflected as hex-like folds. That takes in
# 15 pieces (the fuel cap, the indicator bezels, the stem nut, caliper and axle caps, other nuts
# and trims) for 7,500 more triangles; by the 1,100 triangles alone it would take in 104 for
# 67,000, the wheels' 54 spoke trims among them, and the bolts under BRIGHT_AREA look like the
# source cut down.
PAINTED = ("body", "logo_decals")
BRIGHT = ("chrome", "silver")
BRIGHT_TRIS = 1100
BRIGHT_AREA = 20.0
SPECK_AREA = 0.25   # pieces under this (units squared) are dropped: 12 of them, 1 unit squared in all
# The pieces under SMALL_AREA (about a centimetre across) were all dropped before test 40: 279 of
# them, the crankcase, primary cover, hub, fender and cover screws and nuts among them. They stay
# now, but a bolt's own centre says little about what it's fixed to, so it spins with a wheel
# only when the ordinary piece nearest it (by its source vertices) is a wheel's (a disc bolt)
# and otherwise takes role_of like any piece (by the nearest piece alone a bar housing screw
# went into the fixed metal shape, still while the bars turned, and lifted that shape's sphere
# 5 units).
SMALL_AREA = 4.0

# The shading normals (gltf_normals()). Test 40: averaged over every face at a welded vertex they
# smeared the hard edges and the creases decimation makes on curved parts (15.7 degrees off the
# glTF's own on average, 69 at the 95th percentile, chrome reflections folded with black
# wedges), and cancelled to nothing where opposite faces were welded together (210 vertices,
# specks of random light). Now each corner takes the glTF's own normal at the closest point of
# its piece's source surface to a point NORMAL_NUDGE of the way from the corner to its
# triangle's centre (so a corner on a hard edge reads its own side of it); a sample more than
# NORMAL_GUARD_DEG off its own triangle has read another feature (a coarse triangle bridging a
# bevel) and takes the averaged normal instead (without it the derby cover and the fuel cap
# folded); a piece kept whole takes the glTF's normals at its corners as they are (test 41); and
# a vertex's corners that agree within SPLIT_DEG share one vertex while the rest get their own,
# so the source's hard edges stay hard. 5.2 degrees off on average, 21 at the 95th percentile,
# 1.9% of the surface over 45 (10.5% before); the split costs about 30% more vertices (the
# fixed matte shape has 48,609 of the 65,535 a shape may have).
NORMAL_NUDGE = 0.25
NORMAL_GUARD_DEG = 45.0
SPLIT_DEG = 30.0

# BSLightingShaderProperty flags, Fallout 4's bits (nif.xml's Fallout4ShaderPropertyFlags1/2). Until the 2026-10-31a build the converter
# also set 0x100 and 0x8000, Skyrim's Receive_Shadows and EnvMap_Light_Fade, which in Fallout 4 are RGB_Falloff and
# Dismemberment; no vanilla static or vehicle shape sets either.
SF1_SPECULAR, SF1_SKINNED, SF1_ENV_MAP, SF1_CAST_SHADOWS = 0x1, 0x2, 0x80, 0x200
SF1_ZBUFFER_TEST = 0x80000000
SF1_OWN_EMIT = 0x400000   # set on every shape, as vanilla does; it glows by its emissive colour (black unless lit)

# Our headlamp (the model's own, a plain can, sat still while the forks turned: its centre is
# 20 units behind the steering head, past role_of's 16): a 5.75" LED unit, 15 across,
# on the fork bracket where the model's was, in the worn bike's space (+Y forward, Z up).
LAMP_X, LAMP_Z = 0.3, 81.9          # the lamp's axis
LAMP_FACE_Y, LAMP_R = 75.0, 7.5     # the lens sits here; the bucket runs 13 back from it
LAMP_LENS = (LAMP_X, LAMP_FACE_Y + 1.3, LAMP_Z)   # the lens's centre: where the light comes from
# The headlamp's light is a reference the controller script places at the lens (LampPoint in
# CMB_BikeParts.ini, kept there by the plugin); the lamp piece nifs of tests 32-35 (the light's
# add-on nodes in an unskinned armor addon of their own) never reached the player's 3D.
SF2_ZBUFFER_WRITE, SF2_DOUBLE_SIDED, SF2_GLOW_MAP = 0x1, 0x10, 0x40
SHADER_TYPES = {"default": 0, "env": 1, "glow": 2}   # Default, Environment_Map, Glow_Shader
ALPHA_BLEND_FLAGS = 4845   # blend src alpha / inv src alpha, test greater

# Each shape's shader (tools/rider/bike_materials.json overrides these per material; a material is
# one shape's, <mat> = its label: since the 2026-10-31a build the needle has its own, the dial's art with a glow map
# lighting its blade, so it reads at night). The cube maps are vanilla's, named by their paths (none copied); since
# 2026-11-02a the mirrors' too, MB (the game's own reflective bathroom mirrors' cube: test 48, "the game cube looks
# better"); MR, ours (a sharp sky and ground), is written by the texture stage only if a material names it (the
# 2026-11-01a look, in the optional A-B folder).
CUBES = {"CH": "Shared\\Cubemaps\\MetalChrome01Cube_e.dds", "DI": "Shared\\Cubemaps\\mipblur_DefaultOutside1_dielectric.dds",
         "GL": "Shared\\Cubemaps\\shinyglass_e.dds", "MB": "Shared\\Cubemaps\\MetalBrushed02Cube_e.dds",
         "MR": "CMB\\Bike\\mirror_cube_e.dds"}
SHAPE_MAT = {}   # label -> material where a material serves more than one shape (none now)
_ENV = lambda cube, scale: dict(shader="env", cube=cube, env_scale=scale)   # noqa: E731
_GLOW = lambda rgb, mult, glow_map=True: dict(shader="glow", emit=dict(colour=rgb, mult=mult, glow_map=glow_map))   # noqa: E731
_GLASS = dict(alpha=dict(mode="blend", flags=ALPHA_BLEND_FLAGS, threshold=0))
DEFAULT_SHADERS = {
    "static_paint": _ENV("DI", 0.5), "static_chrome": _ENV("CH", 1.0), "static_exhaust": _ENV("CH", 1.0),
    "static_engine": _ENV("DI", 0.3), "static_black": {}, "static_seat": {}, "static_glass": {**_ENV("GL", 1.0), **_GLASS},
    "static_badge": _ENV("CH", 0.8),
    # 2026-11-07a (--look-slots 1): the split plates as static_badge (over its textures), the fender patch invisible
    **{b: {**_ENV("CH", 0.8), "textures_of": "static_badge"} for b in BADGE_SPLIT},
    FENDER_BADGE: dict(alpha=dict(mode="test", flags=4844, threshold=255), textures_of=OFF_MAT),
    # 2026-11-08a: the plate as static_black (over its own textures), the text overlay and the rim styles invisible
    "static_plate": {}, "static_plateText": dict(alpha=dict(mode="test", flags=4844, threshold=255), textures_of="off"),
    **{label: dict(alpha=dict(mode="test", flags=4844, threshold=255), textures_of="off") for label in
       ("wheelF_rimLaced", "wheelR_rimLaced", "wheelF_rimDisc", "wheelR_rimDisc", "wheelF_rimStar", "wheelR_rimStar",
        "wheelF_rimTurbine", "wheelR_rimTurbine", "wheelF_rimPrewar", "wheelR_rimPrewar", "wheelF_rimAtomic",
        "wheelR_rimAtomic", "wheelF_rimScrap", "wheelR_rimScrap")},
    "rear_tail": _GLOW((1.0, 0.012, 0.006), 2.5), "rear_brake": _GLOW((1.0, 0.005, 0.0025), 8.0),   # deep red, brake brighter
    "front_chrome": _ENV("CH", 1.0), "front_black": {}, "front_glass": {**_ENV("GL", 1.0), **_GLASS},
    "front_glow": _GLOW((1.0, 0.95, 0.9), 6.0, False), "front_dial": {}, "front_needle": _GLOW((1.0, 0.12, 0.03), 1.5),
    "front_dialglow": _GLOW((1.0, 0.86, 0.66), 1.5),
    "front_mirrorStock": _ENV("MR", 1.5), "front_mirrorUnderEgg": _ENV("MR", 1.5), "front_mirrorUnderD": _ENV("MR", 1.5),
    "fork_chrome": _ENV("CH", 1.0), "fork_paint": _ENV("DI", 0.5), "fork_black": {}, "fork_glass": {**_ENV("GL", 1.0), **_GLASS},
    "wheelF_tyre": _ENV("DI", 0.25), "wheelR_tyre": _ENV("DI", 0.25), "wheelF_rim": _ENV("DI", 0.4), "wheelR_rim": _ENV("DI", 0.4),
    "wheelF_disc": _ENV("DI", 0.4), "wheelR_disc": _ENV("DI", 0.4),
}
SHADER_BASE = dict(shader="default", cube=None, env_scale=1.0, smoothness=1.0, spec_colour=(1.0, 1.0, 1.0), spec_mult=1.0,
                   emit=None, alpha=None, two_sided=True, textures_of=None)
# The invisible material (2026-11-07a): the parked nif's PARKED_OFF mirrors' blocks and bike_materials.json's "off"
# (alpha test 255 over off_d.dds's alpha 0: nothing drawn, no shadow; look_paint.py writes its materials files)
OFF_SHADER = dict(alpha=dict(mode="test", flags=4844, threshold=255), cast_shadows_worn=False, cast_shadows_parked=False)


# --- glTF --------------------------------------------------------------------------------

def load_gltf(path: Path, normals=None, sources=None):
    """Each material's vertices and triangles, merged: {name: (V (n,3) float64, F (m,3) int64)}.
    With normals (a dict), each material's glTF normals at the corners of those triangles go
    into it too, (m, 3, 3): the weld makes one vertex of a hard edge's two, and the corners keep
    the export's own normals for gltf_normals() (the faces' own where a primitive has none).
    With sources (a dict), each triangle's glTF mesh index, (m,): the merge by material loses
    which mesh a triangle came from, and the shapes are routed by it (label_of)."""
    d = json.loads(path.read_text())
    bufs = [(path.parent / b["uri"]).read_bytes() for b in d["buffers"]]
    types = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
    widths = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}

    def accessor(i):
        a = d["accessors"][i]
        bv = d["bufferViews"][a["bufferView"]]
        dt = np.dtype(types[a["componentType"]])
        n = widths[a["type"]]
        off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        stride = bv.get("byteStride", dt.itemsize * n)
        if stride != dt.itemsize * n:
            raise ValueError("interleaved buffer views aren't handled")
        return np.frombuffer(bufs[bv["buffer"]], dtype=dt, count=a["count"] * n, offset=off).reshape(a["count"], n)

    for node in d["nodes"]:
        if any(k in node for k in ("matrix", "translation", "rotation", "scale")) and "mesh" in node:
            raise ValueError("a mesh node with its own transform: not handled (this model has none)")
    groups = {}
    for mesh_index, m in enumerate(d["meshes"]):
        for p in m["primitives"]:
            name = d["materials"][p["material"]]["name"]
            v = accessor(p["attributes"]["POSITION"]).astype(np.float64)
            f = accessor(p["indices"]).reshape(-1, 3).astype(np.int64)
            if "NORMAL" in p["attributes"]:
                n = np.nan_to_num(accessor(p["attributes"]["NORMAL"]).astype(np.float64))[f]
            else:
                n = np.repeat(unit(face_normals(v, f))[:, None, :], 3, axis=1)
            groups.setdefault(name, []).append((v, f, n, np.full(len(f), mesh_index, np.int64)))
    merged = {}
    for name, parts in groups.items():
        vs, fs, ns, ss, off = [], [], [], [], 0
        for v, f, n, s in parts:
            vs.append(v)
            fs.append(f + off)
            ns.append(n)
            ss.append(s)
            off += len(v)
        v, f, keep = weld(np.vstack(vs), np.vstack(fs))   # the parts of a material together: a tyre's halves share their seam
        merged[name] = (v, f)
        if normals is not None:
            normals[name] = np.vstack(ns)[keep]
        if sources is not None:
            sources[name] = np.concatenate(ss)[keep]
    return merged


def gltf_scene_matrix(path: Path):
    """The 4x4 that takes the raw POSITION accessors (what load_gltf reads: the node transforms
    are ignored) to the glTF scene's frame (every mesh node's ancestors' matrices; None if the
    meshes' differ). A Blender import then turns the scene from Y up to Z up, (x, -z, y)."""
    d = json.loads(path.read_text())
    nodes = d["nodes"]

    def local(n):
        if "matrix" in n:
            return np.array(n["matrix"], dtype=np.float64).reshape(4, 4).T   # column-major
        m = np.eye(4)
        if "scale" in n:
            m = np.diag([*n["scale"], 1.0]) @ m
        if "rotation" in n:
            x, y, z, w = n["rotation"]
            r = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                          [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                          [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
            m[:3, :3] = r @ m[:3, :3]
        if "translation" in n:
            m[:3, 3] += n["translation"]
        return m

    found = []

    def walk(i, parent):
        world = parent @ local(nodes[i])
        if "mesh" in nodes[i]:
            found.append(world)
        for c in nodes[i].get("children", []):
            walk(c, world)

    for root in d["scenes"][d.get("scene", 0)]["nodes"]:
        walk(root, np.eye(4))
    if not found or any(not np.allclose(m, found[0], atol=1e-9) for m in found):
        return None
    return found[0]


def weld(v, f, tol=1e-3):
    """Merge vertices at the same place. The export keeps a vertex per face corner along
    hard edges, which leaves the simplifier a patchwork of islands whose borders it won't
    collapse (pieces came back ten times over budget). Across a material's parts too: the
    simplifier doesn't keep a border where it is, so two parts decimated apart crack along
    their seam (a tyre's halves meet on the tread's centre line). Returns the vertices, the
    triangles and which of the triangles given are kept (not collapsed to a line by it)."""
    key = np.round(v / tol).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    f = inv.reshape(-1)[f] if inv.ndim > 1 else inv[f]
    keep = (f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])
    return v[first], f[keep], keep


def components(n, f):
    """Connected components over the triangles: (count, label per vertex). Label propagation
    with pointer jumping, all in numpy."""
    lab = np.arange(n)
    while True:
        m = np.minimum(np.minimum(lab[f[:, 0]], lab[f[:, 1]]), lab[f[:, 2]])
        new = lab.copy()
        for k in range(3):
            np.minimum.at(new, f[:, k], m)
        while True:
            jumped = new[new]
            if np.array_equal(jumped, new):
                break
            new = jumped
        if np.array_equal(new, lab):
            break
        lab = new
    uniq, inv = np.unique(lab, return_inverse=True)
    return len(uniq), inv


def decimate(groups, normals, total_target, speck_area=SPECK_AREA, small_area=SMALL_AREA, min_tris=8, weight=None, role=None,
             sources=None, guard=False, shape_of=None, guard_report=None):
    """Cut the model down, each connected piece towards its share of total_target triangles by
    surface area: so a tyre keeps its shape while a bolt gets a few triangles, instead of the
    thousands of small pieces of one material (tread blocks, bolts, cables) starving the big
    ones. The share is the simplifier's target and AGG_CAP its error bound, so a piece stops
    short of its share where reaching it would crush it, and the result runs well over
    total_target (about 225k for 90000 on this model). Kept whole: a piece of up to KEEP_TRIS
    triangles or with a share of KEEP_FRAC of them or more, the glass (the indicator and
    tail light lenses: the cubemap shows each facet), the PAINTED panels and the small BRIGHT
    pieces off the wheels; the bar assembly and the pieces of FINE_AREA or more off the wheels
    are cut at FINE_AGG whatever they're made of (role(verts) says which part a piece moves
    with, by role_of's names). Pieces of under speck_area (game units squared) are dropped.
    Coordinates must be scaled to game units already; normals is what load_gltf filled.
    Returns (material, verts, tris, small, source, mesh) per piece: small if it's under small_area,
    source the piece as it was with its glTF corner normals (verts, tris, normals), for
    gltf_normals(), mesh the glTF mesh most of its triangles came from (with sources, what
    load_gltf filled; else -1). With guard (the volume guard, since the 2026-11-01a build), a closed piece the cut
    crushed is cut again (volume_guard(); shape_of and guard_report are its)."""
    import fast_simplification as fs
    pieces = []   # (material, verts, tris, area, corner normals, glTF mesh)
    dropped = dropped_area = 0
    for name, (v, f) in groups.items():
        k, lab = components(len(v), f)
        tri = v[f]
        area = 0.5 * np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
        tri_lab = lab[f[:, 0]]
        piece_area = np.bincount(tri_lab, weights=area, minlength=k)
        order = np.argsort(tri_lab, kind="stable")
        bounds = np.searchsorted(tri_lab[order], np.arange(k + 1))
        for c in range(k):
            sel = order[bounds[c]:bounds[c + 1]]
            if piece_area[c] < speck_area:
                dropped += 1
                dropped_area += piece_area[c]
                continue
            used, inv = np.unique(f[sel], return_inverse=True)
            mesh = int(np.bincount(sources[name][sel]).argmax()) if sources is not None else -1
            pieces.append((name, v[used], inv.reshape(-1, 3), float(piece_area[c]), normals[name][sel], mesh))
    total_area = sum(p[3] for p in pieces)
    counts = np.array([len(p[2]) for p in pieces])
    areas = np.array([p[3] * (weight(p[1]) if weight else 1.0) for p in pieces])
    # Budget by area; a piece already under its budget keeps all its triangles and the rest
    # share what it leaves (a few rounds of that).
    budget = np.zeros(len(pieces))
    free = np.ones(len(pieces), bool)
    for _ in range(6):
        spare = total_target - counts[~free].sum()
        budget[free] = spare * areas[free] / max(areas[free].sum(), 1e-9)
        done = free & (budget >= counts)
        if not done.any():
            break
        budget[done] = counts[done]
        free &= ~done
    budget = np.maximum(np.minimum(budget, counts), np.minimum(min_tris, counts)).astype(int)
    result = []
    cut = []   # (index in result, its share, its error cap): the pieces the simplifier cut, for the volume guard
    kept = held = over = painted = bright = fine = 0
    for (name, v, f, area, n0, mesh), b in zip(pieces, budget):
        v0, f0 = v, f
        kind = MATERIALS[name][5]
        part = role(v) if role else ""
        wheel = part.startswith("wheel")
        small_bright = name in BRIGHT and len(f) <= BRIGHT_TRIS and area >= BRIGHT_AREA and not wheel
        if len(f) <= KEEP_TRIS or b >= KEEP_FRAC * len(f) or kind == "glass":
            kept += 1
        elif name in PAINTED or small_bright:
            kept += 1
            painted += name in PAINTED
            bright += small_bright
        else:
            agg = AGG_CAP[kind]
            if part == "front" or (area >= FINE_AREA and not wheel):
                agg = FINE_AGG
                fine += agg < AGG_CAP[kind]
            vo, fo = fs.simplify(v, f, target_count=int(b), agg=agg)
            v, f = np.asarray(vo, dtype=np.float64), np.asarray(fo, dtype=np.int64)
            v = snap_border(v, f, v0, f0)
            if len(f) > b * 1.05:
                held += 1
                over += len(f) - b
            cut.append((len(result), int(b), agg))
        result.append((name, v, f, area < small_area, (v0, f0, n0), mesh))
    got = sum(len(r[2]) for r in result)
    print(f"  {len(pieces)} pieces kept ({sum(p[3] < small_area for p in pieces)} of them under {small_area:g} units²), "
          f"{dropped} specks dropped ({dropped_area:.0f} units² of {total_area:.0f}); budget {int(budget.sum())} triangles, "
          f"got {got}: {kept} pieces whole ({painted} painted, {bright} small chrome or silver), {held} held over their "
          f"share by the error cap ({over} triangles), {fine} cut finer than their material's cap (FINE_AGG)")
    per = {}
    for name, _, f, _, _, _ in result:
        per[name] = per.get(name, 0) + len(f)
    for name, (v, f) in groups.items():
        if name in per:
            print(f"  {name:12s} {len(f):8d} -> {per[name]:6d} tris")
    if guard or guard_report is not None:   # off, it only measures (the manifest's volumes: check_bike_meshes fails them)
        volume_guard(result, cut, shape_of, guard_report, recut=guard)
    return result


# The volume guard (since the 2026-11-01a build; --volume-guard 0 is 2026-10-31a's cut, byte for byte). Test 47: the
# seat's piping cord (glTF mesh 25's second piece, a closed 0.5 x 0.15 tube along the seam) was cut from 2,368 to 210
# triangles and kept 0.34 of its volume: it stood out of the seat as fins at random angles, "textures in the air".
# The same audit over all 775 pieces found two more crushed closed pieces (static_black's glTF 46, 0.21; static_engine's
# glTF 45, 0.32); every other closed piece keeps 0.62 or more. A closed piece of at least VOLUME_MIN that keeps under
# VOLUME_KEEP of its volume is cut again from the source at twice its target, and again, until it keeps VOLUME_OK (or
# the target reaches its source's count: then it's kept whole). A re-cut that would take its shape past
# VOLUME_SHAPE_CAP vertices in the nifs is not made (logged): the decimation's welded vertices grow by up to
# VOLUME_SEAM_GROWTH by the time the normal and UV seams are split (2026-10-31a's shapes: 1.69 to 2.14, static_black
# 2.09), which keeps every shape well under MAX_VERTS.
VOLUME_MIN = 0.05            # closed pieces of at least this volume (units cubed) are guarded
VOLUME_KEEP = 0.6            # cut again if the simplified piece keeps less than this share of its volume
VOLUME_OK = 0.8              # until it keeps this share
VOLUME_SHAPE_CAP = 55000     # a shape's vertices in the nifs (after the seams) a re-cut may take it to, at most
VOLUME_SEAM_GROWTH = 2.25    # the nif's vertices per welded vertex of the decimation, at most (2.14 measured, a margin)


def volume_guard(result, cut, shape_of=None, report=None, recut=True):
    """decimate()'s second pass: the cut pieces that are closed in the source and of at least VOLUME_MIN cubic units,
    and keep under VOLUME_KEEP of their volume, cut again from the source at twice their target until they keep
    VOLUME_OK (or kept whole), unless that takes their shape (shape_of(material, verts, mesh), the label) past
    VOLUME_SHAPE_CAP. result's entries are replaced in place. report (a dict) gets "volume_guard": the pieces re-cut
    [{piece, mesh, material, label, from, to, share_from, share}] and "volumes": every closed cut piece guarded or not
    [{piece, mesh, label, src_tris, tris, share}] (check_bike_meshes reads both). recut False (--volume-guard 0) only
    measures: result is left as it is."""
    import fast_simplification as fs
    welded = {}
    labels = {}
    for i, (name, v, f, small, source, mesh) in enumerate(result):
        labels[i] = shape_of(name, v, mesh) if shape_of else ""
        welded[labels[i]] = welded.get(labels[i], 0) + len(v)
    guarded, volumes, stopped = [], [], 0
    for i, b, agg in cut:
        name, v, f, small, source, mesh = result[i]
        v0, f0, n0 = source
        vol0 = closed_volume(v0, f0)
        if vol0 is None or abs(vol0) < VOLUME_MIN:
            continue
        share0 = share = abs(closed_volume(v, f, closed=True)) / abs(vol0)
        label = labels[i]
        tgt, tris0 = b, len(f)
        while recut and share < VOLUME_OK and share0 < VOLUME_KEEP:
            tgt *= 2
            if tgt >= len(f0):
                nv, nf = v0, f0
            else:
                vo, fo = fs.simplify(v0, f0, target_count=tgt, agg=agg)
                nv, nf = np.asarray(vo, dtype=np.float64), np.asarray(fo, dtype=np.int64)
                nv = snap_border(nv, nf, v0, f0)
            after = welded[label] - len(v) + len(nv)
            if after * VOLUME_SEAM_GROWTH > VOLUME_SHAPE_CAP:
                stopped += 1
                print(f"  volume guard: glTF mesh {mesh} {name} ({label}): not cut again at {len(nf)} triangles, which "
                      f"would take {label} to about {after * VOLUME_SEAM_GROWTH:.0f} vertices (over {VOLUME_SHAPE_CAP}); "
                      f"kept at {len(f)} triangles, volume share {share:.2f}")
                break
            welded[label] = after
            v, f = nv, nf
            share = abs(closed_volume(v, f, closed=True)) / abs(vol0)
            if tgt >= len(f0):
                break
        if len(f) != tris0:
            result[i] = (name, v, f, small, source, mesh)
            guarded.append(dict(piece=i, mesh=int(mesh), material=name, label=label, **{"from": tris0}, to=len(f),
                                share_from=round(share0, 4), share=round(share, 4)))
            print(f"  volume guard: glTF mesh {mesh} {name} ({label}): {tris0} -> {len(f)} triangles (share of the "
                  f"budget {b}), volume {abs(closed_volume(v, f, closed=True)):.3f} of {abs(vol0):.3f} "
                  f"({share0:.2f} -> {share:.2f})")
        volumes.append(dict(piece=i, mesh=int(mesh), label=label, src_tris=len(f0), tris=len(f), share=round(share, 4)))
    print(f"  volume guard{'' if recut else ' (off: measured only)'}: {len(volumes)} closed pieces cut, {len(guarded)} cut again (+"
          f"{sum(g['to'] - g['from'] for g in guarded)} triangles), {stopped} stopped by the shapes' vertex cap; the least "
          f"volume kept {min([x['share'] for x in volumes] or [1.0]):.2f}")
    if report is not None:
        report["volume_guard"] = guarded
        report["volumes"] = volumes


def closed_volume(v, f, closed=False):
    """The enclosed volume of a closed piece (None if it has open edges, unless closed)."""
    if not closed and len(border_vertices(f)):
        return None
    c = v.mean(axis=0)
    a, b_, d = v[f[:, 0]] - c, v[f[:, 1]] - c, v[f[:, 2]] - c
    return float(np.einsum("ij,ij->i", a, np.cross(b_, d)).sum() / 6.0)


def border_vertices(f):
    """The indices of the vertices on open edges (edges with one triangle)."""
    e = np.sort(np.vstack([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]), axis=1)
    ue, cnt = np.unique(e, axis=0, return_counts=True)
    return np.unique(ue[cnt == 1])


def snap_border(v, f, v0, f0):
    """The decimated piece's border vertices put back on the piece's original border: the
    simplifier moves them off it (a third of the tyre's did), so two parts that met along a
    seam, decimated apart, came apart along it (test 21: the tyre looked loose on the rim).
    Each one goes to the nearest original border vertex."""
    b1 = border_vertices(f)
    b0 = border_vertices(f0)
    if len(b1) == 0 or len(b0) == 0:
        return v
    orig = v0[b0]
    out = v.copy()
    for i in range(0, len(b1), 256):
        idx = b1[i:i + 256]
        d = ((v[idx][:, None, :] - orig[None, :, :]) ** 2).sum(axis=2)
        out[idx] = orig[d.argmin(axis=1)]
    return out


def pieces_of(v, f, least=30):
    """A material's connected pieces: (verts, tris) each, the small ones left out."""
    k, lab = components(len(v), f)
    out = []
    for c in range(k):
        sel = lab[f[:, 0]] == c
        if sel.sum() < least:
            continue
        used, inv = np.unique(f[sel], return_inverse=True)
        out.append((v[used], inv.reshape(-1, 3)))
    return out


def measure_parts(groups, steer=None):
    """The moving parts, in the parked frame: the two tyres (the two round rubber pieces as
    tall as they are long) give the axles and the wheel radius; the fork tubes (the pieces
    ahead that are long along one raked axis, one each side) give the steering axis. --steer
    overrides the axis (x,y,z of a point on it and the rake in degrees)."""
    rounds = []   # the round rubber pieces as tall as they are long: a tyre, or a layer of one
    for v, f in pieces_of(*groups["material"]):
        lo, hi = v.min(axis=0), v.max(axis=0)
        dy, dz = hi[1] - lo[1], hi[2] - lo[2]
        if dz > 40 and abs(dz - dy) < 4 and hi[0] - lo[0] < 20:
            rounds.append(((lo + hi) / 2, dz / 2))
    tyres = []   # one per axle: the layers of a tyre (tread, carcass) share its centre
    for c, r in rounds:
        for t in tyres:
            if np.linalg.norm(t[0][1:] - c[1:]) < 4.0:   # the same axle (a tyre's halves sit side by side)
                t[1] = max(t[1], r)
                break
        else:
            tyres.append([c, r])
    tyres.sort(key=lambda t: t[0][1])
    if len(tyres) != 2:
        raise ValueError(f"expected two tyres among the rubber pieces, found {len(tyres)} (of {len(rounds)} round pieces)")
    (front, rf), (rear, rr) = tyres
    parts = dict(front_axle=front, rear_axle=rear, wheel_radius=(rf + rr) / 2)
    # The rim's lip: the farthest any round non-rubber piece on the front axle reaches.
    lips = []
    for mat in ("black_m", "chrome", "silver"):
        for v, f in pieces_of(*groups.get(mat, (np.zeros((0, 3)), np.zeros((0, 3), np.int64)))):
            if np.abs(v[:, 0]).max() >= 13.0:
                continue
            r = np.hypot(v[:, 1] - front[1], v[:, 2] - front[2])
            bins = np.unique(np.floor(np.degrees(np.arctan2(v[:, 2] - front[2], v[:, 1] - front[1])) / 10.0).astype(int))
            if r.max() < rf and len(bins) >= 25:
                lips.append(float(r.max()))
    parts["rim_radius"] = max(lips) if lips else 0.0
    if steer:
        x, y, z, rake = steer
        parts["steer_point"] = np.array([x, y, z])
        parts["steer_axis"] = np.array([0.0, math.sin(math.radians(rake)), math.cos(math.radians(rake))])
        return parts
    tubes = []
    for mat in ("chrome", "black_m", "silver"):
        for v, f in pieces_of(*groups.get(mat, (np.zeros((0, 3)), np.zeros((0, 3), np.int64)))):
            lo, hi = v.min(axis=0), v.max(axis=0)
            m = v.mean(axis=0)
            if not (m[1] < front[1] + rf + 15 and 4 < abs(m[0]) < 16 and hi[2] - lo[2] > 20 and hi[0] - lo[0] < 8):
                continue
            c = v - m
            _, _, vt = np.linalg.svd(c[:: max(1, len(c) // 2000)], full_matrices=False)
            if abs(vt[0][2]) < 0.6:   # not long along something upright
                continue
            tubes.append(v)
    if not tubes:
        raise ValueError("no fork tubes found ahead: pass --steer x,y,z,rake")
    # The fork assembly's long axis: the principal axis of all the tubes' vertices together
    # (one tube's own axis wobbles with its lugs and clamps; test 21's came out at 17 degrees
    # from a lower, 24 from an upper, on a 30-degree fork).
    allv = np.vstack(tubes)
    point = allv.mean(axis=0)
    c = allv - point
    c[:, 0] = 0.0   # the two sides together, in the centre plane
    _, _, vt = np.linalg.svd(c[:: max(1, len(c) // 4000)], full_matrices=False)
    axis = vt[0] if vt[0][2] >= 0 else -vt[0]
    axis[0] = 0.0
    axis /= np.linalg.norm(axis)
    point[0] = 0.0
    parts["steer_point"], parts["steer_axis"] = point, axis
    parts["tubes"] = len(tubes)
    return parts


def wheel_of(v, parts):
    """Which wheel a piece is part of, if any: it lies inside the wheel's drum (within 13 of
    the centre plane, within the tyre's radius of the axle) and either runs round the axle
    (tyre, rim, disc, hub, pulley: 300 degrees or more of it) or is a spoke (from the hub out
    to the rim, on the centre plane). A brake caliper sits inside the drum too, but off to
    one side and short of the hub, so it stays with the forks. (Test 20: by the pieces'
    centres alone, half the spokes and the rim bands went to the fixed shapes, and the rims
    seemed to spin away from the tyres.)"""
    for role, key in (("wheelF", "front_axle"), ("wheelR", "rear_axle")):
        c = parts[key]
        if np.abs(v[:, 0] - c[0]).max() >= 13.0:
            continue
        r = np.hypot(v[:, 1] - c[1], v[:, 2] - c[2])
        if r.max() >= parts["wheel_radius"] + 1.5:
            continue
        bins = np.unique(np.floor(np.degrees(np.arctan2(v[:, 2] - c[2], v[:, 1] - c[1])) / 10.0).astype(int))
        if len(bins) >= 25:   # a ring, a toothed one with a gap too (the belt's wrap round the pulley)
            return role
        if r.min() < 9.0 and r.max() > 14.0 and np.abs(v[:, 0] - c[0]).max() < 6.5:   # a spoke (this model's are split in two, 2..6 out)
            return role
    return None


def seat_tyre(v, parts, role):
    """The tyre's inner edge pulled in to the rim: in this model the rim's lip ends 2 units
    short of the tyre's bead (a ring of nothing between them: test 21's "rims not attached"),
    so the bead's vertices, from the inner edge to 25 units out, slide in to the lip's radius."""
    c = parts["front_axle"] if role == "wheelF" else parts["rear_axle"]
    r = np.hypot(v[:, 1] - c[1], v[:, 2] - c[2])
    lip, bead = parts.get("rim_radius", 0.0), r.min()
    if not lip or bead <= lip + 0.3 or bead > lip + 6.0:
        return v
    outer = min(bead + 1.7, parts["wheel_radius"] - 2.0)
    k = np.clip((outer - r) / (outer - bead), 0.0, 1.0)
    pull = (bead - lip) * k
    out = v.copy()
    out[:, 1] -= (v[:, 1] - c[1]) / np.maximum(r, 1e-6) * pull
    out[:, 2] -= (v[:, 2] - c[2]) / np.maximum(r, 1e-6) * pull
    return out


def role_of(v, parts, raked=True):
    """Which moving part a piece belongs to: a wheel (wheel_of), else the steering assembly
    if its centre is ahead of the steering head (forks, fender, headlight) or up at the bars
    (bars, grips, levers, mirrors), and of that the fork's lower end if its centre is below
    FORK_SPLIT_Z (sliders, mudguard, caliper, axle), else fixed. And (raked, since the 2026-10-31a build) the bar
    assembly also takes what sits within RAKED_BEHIND behind the steering axis at its own
    height above SteerPoint: the axis rakes back 29 degrees, so "16 behind the steering head"
    at SteerPoint's height is already 15.6 ahead of the axis at the lower triple clamp's (z
    68.5), which stood still while the fork tubes turned through it (27c, raked=False, still
    the decimation's choice so the triangles stay 27c's). Only adds: every piece 27c moved
    keeps its role (16 behind the raked axis would also have taken the coil, wiring and bolts
    under the tank's nose, 10-16 behind it, which are the frame's)."""
    wheel = wheel_of(v, parts)
    if wheel:
        return wheel
    cx, cy, cz = v.mean(axis=0)
    sp = parts["steer_point"]
    if cy < sp[1] + 16:
        return "fork" if cz < FORK_SPLIT_Z else "front"
    if raked and cz > sp[2]:
        ax = parts["steer_axis"]
        if cy < sp[1] + (cz - sp[2]) * ax[1] / ax[2] + RAKED_BEHIND:   # parked: +y is back, and so is the axis going up
            return "front"   # the lower clamp, its pinch bolts and the stem nut under it: with the bars, not the fork's travel
    # Up at bar height: within 45 of the steering head anything (the risers, the clamp, the
    # speedo, the mirrors that reach back over the tank), and out to 65 only what sits off the
    # centre line: the grips, levers, switch housings and the left mirror sit 45-57 behind the
    # head on this model (the bars sweep back), so with one line at 45 they stayed with the
    # frame while the bars turned (test 35: 590 vertices of bar end in the fixed shapes); but
    # the tank's chrome filler cap, on the centre line 55 behind the head, has its centre just
    # above BAR_HEIGHT too, and a plain 65 would have turned it with the bars.
    if cz > BAR_HEIGHT and (cy < sp[1] + 45 or (abs(cx) > 12 and cy < sp[1] + 65)):
        return "front"
    return ""


def label_of(role, material, mesh):
    """Which shape (LABELS) a piece of the model goes into: by the part it moves with (role_of)
    and what it is, its glTF mesh where its material alone would send it elsewhere, else its
    material. None for a piece that's dropped (DROP_MESHES)."""
    if mesh in DROP_MESHES:
        return None
    kind = MATERIALS[material][5]
    if role in ("wheelF", "wheelR"):   # the rim (and its trims) apart from the tyre, disc and hub, for rim styles
        return f"{role}_rim" if mesh in RIM_MESHES else f"{role}_tyre"
    if role == "fork":
        return ("fork_paint" if material == "body" else "fork_glass" if kind == "glass"
                else "fork_chrome" if material in BRIGHT else "fork_black")
    if role == "front":
        if mesh in MIRROR_MESHES:
            return "front_mirrorStock"
        return ("front_glow" if kind == "glow" else "front_glass" if kind == "glass"
                else "front_chrome" if material in BRIGHT else "front_black")
    if material == "body":
        return "static_paint"
    if material == "logo_decals":
        return "static_badge"
    if mesh in EXHAUST_MESHES:
        return "static_exhaust"
    if material in BRIGHT:
        return "static_chrome"
    if kind == "glass":
        return "static_glass"
    if material == "leather":
        return "static_seat"
    if mesh in ENGINE_MESHES or (material == "tex2" and mesh not in PLATE_MESHES):
        return "static_engine"
    return "static_black"


def lathe(profile, segments=32, inside=False):
    """A surface of revolution about the Y axis (x = r cos, z = r sin) from a profile of (r, y)
    points, wound so the normals face outward along the profile's direction (right-hand rule:
    a profile running forward (+y) faces outward, one running inward in r at one y faces +y);
    inside=True turns it inside out (a reflector dish seen from the front)."""
    rings, verts = [], []
    for r, y in profile:
        ring = []
        for s in range(segments):
            a = 2.0 * math.pi * s / segments
            ring.append(len(verts))
            verts.append((r * math.cos(a), y, r * math.sin(a)))
        rings.append(ring)
    tris = []
    for k in range(len(rings) - 1):
        a, b = rings[k], rings[k + 1]
        for s in range(segments):
            s2 = (s + 1) % segments
            tris.append((a[s], b[s], b[s2]))
            tris.append((a[s], b[s2], a[s2]))
    v = np.array(verts, dtype=np.float64)
    f = np.array(tris, dtype=np.int64)
    t = v[f]
    area = np.linalg.norm(np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]), axis=1)
    f = f[area > 1e-6]   # the apex rings (r = 0) make degenerate triangles
    if inside:
        f = f[:, [0, 2, 1]]
    return v, f


def headlamp_pieces(seat_at, flip):
    """Our headlamp, as (material, verts, tris) pieces in the parked model's frame: a gloss
    black bucket with a chrome bezel, a chrome reflector dish, a projector in the middle with
    a lit face, a lit running-light ring inside the bezel and a shallow glass lens."""
    yF, R = LAMP_FACE_Y, LAMP_R

    def place(v):   # lathe space (about the lamp's axis) -> worn -> parked (a half turn about z: the winding holds)
        w = v + np.array([LAMP_X, 0.0, LAMP_Z])
        return np.column_stack([-w[:, 0], seat_at - w[:, 1], w[:, 2]])

    def piece(material, profile, inside=False):
        v, f = lathe(profile, 32, inside)
        if flip:   # the main loop flips every piece to the vanilla's winding: ours is right already
            f = f[:, [0, 2, 1]]
        return material, place(v), f

    return [
        piece("lamp_black", [(0.0, yF - 13.0), (3.5, yF - 12.8), (6.0, yF - 12.0), (7.1, yF - 10.5), (R, yF - 8.5), (R, yF - 1.5), (6.6, yF - 1.5)]),
        piece("chrome", [(6.6, yF - 1.6), (R + 0.1, yF - 1.6), (R + 0.7, yF - 0.9), (R + 0.7, yF + 0.3), (R + 0.1, yF + 1.0), (6.8, yF + 1.0), (6.8, yF + 0.2)]),
        piece("chrome", [(2.7, yF - 8.6), (4.6, yF - 6.2), (5.9, yF - 3.6), (6.6, yF - 1.4), (6.8, yF - 0.6)], inside=True),
        piece("lamp_black", [(0.0, yF - 9.0), (2.7, yF - 9.0), (2.7, yF - 3.2), (2.3, yF - 3.0)]),
        piece("lamp_led", [(2.3, yF - 3.0), (0.0, yF - 3.0)]),
        piece("lamp_led", [(6.5, yF - 1.0), (5.6, yF - 1.0)]),
        piece("glass", [(6.8, yF + 0.2), (5.4, yF + 0.8), (3.0, yF + 1.2), (0.0, yF + 1.3)]),
    ]


def old_headlamp(v, seat_at):
    """A piece of the model's own headlamp (lens, bezel rings, face, bucket): wholly inside the
    cylinder our lamp fills, in the parked frame."""
    x, y, z = -v[:, 0], seat_at - v[:, 1], v[:, 2]
    return bool(np.all((np.abs(x - LAMP_X) < 8.5) & (np.abs(z - LAMP_Z) < 8.5) & (y > 61.0) & (y < 77.0)))


def rows(a):
    """An array's rows as tuples (what PyNifly's ctypes buffers take)."""
    return [tuple(r) for r in a.tolist()]


def unit(a):
    length = np.linalg.norm(a, axis=-1, keepdims=True)
    return a / np.maximum(length, 1e-12)


def face_normals(v, f):
    """Each triangle's normal by its winding, twice its area long."""
    tri = v[f]
    return np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])


def vertex_normals(v, f, per_corner=False):
    """The area-weighted mean of the faces' normals at each vertex. Where they cancel (opposite
    faces welded together: the shock and kickstand springs, the lever fittings; 210 vertices of
    the build before test 40 had no normal, specks of random light) the vertex takes its
    largest face's normal. per_corner gives them by triangle corner instead, (3m, 3), and there
    each corner its own face's (gltf_normals' guard: the split keeps the two sides apart)."""
    n = np.zeros_like(v)
    fn = face_normals(v, f)
    size = np.linalg.norm(fn, axis=1)
    total = np.zeros(len(v))
    for k in range(3):
        np.add.at(n, f[:, k], fn)
        np.add.at(total, f[:, k], size)
    length = np.linalg.norm(n, axis=1)
    bad = (length <= 1e-3 * total) & (total > 0)   # under a thousandth of the faces' summed size
    n = n / np.where(length > 1e-12, length, 1.0)[:, None]
    corner_v = f.reshape(-1)
    if bad.any():
        at = np.flatnonzero(bad[corner_v])
        at = at[np.lexsort((np.repeat(size, 3)[at], corner_v[at]))]   # by vertex, the largest face last
        last = np.r_[corner_v[at][1:] != corner_v[at][:-1], True]
        n[corner_v[at][last]] = unit(fn[at[last] // 3])
    if not per_corner:
        return n
    out = n[corner_v]
    own = bad[corner_v] & (np.repeat(size, 3) > 0)
    out[own] = np.repeat(unit(fn), 3, axis=0)[own]
    return out


def gltf_normals(v, f, source):
    """A decimated piece's shading normals from the glTF's own (see NORMAL_NUDGE): each corner's
    from the closest point of the piece's source surface to a point NORMAL_NUDGE of the way to
    its triangle's centre, the averaged normal where that's over NORMAL_GUARD_DEG off its
    triangle, the corners split by split_corners. A piece kept whole takes the glTF's normals at
    its corners as they are, but for a zero one (a NaN in the file) or one facing away from its
    triangle (155 corners of the bike's: the double-sided shader would light them from behind),
    which take the averaged: the sampling smooths them towards each triangle's own, and on the
    whole tank (test 41) that left a step across its highlight that neither the source nor the
    cut-down tank had, and the 45-degree guard, which is for a sample that has read another
    feature, flattened the rounded edges where the source's normals run further off the faces
    (narrow bevels, thin rods, the rear fender's rolled lip). Returns (verts, tris, normals,
    guarded corners); the positions don't change, a vertex only gains copies."""
    v0, f0, n0 = source
    fn = np.repeat(unit(face_normals(v, f)), 3, axis=0)
    if v.shape == v0.shape and f.shape == f0.shape and np.array_equal(f, f0) and np.array_equal(v, v0):
        cn = unit(n0.reshape(-1, 3))
        off = ~((cn * fn).sum(axis=1) > 0.0)   # zero (a NaN in the file), or facing away from its triangle
    else:
        tri = v[f]
        at = ((1.0 - NORMAL_NUDGE) * tri + NORMAL_NUDGE * tri.mean(axis=1, keepdims=True)).reshape(-1, 3)
        t0 = v0[f0]
        # The cells one and a half of the piece's typical triangle (its bounding box's longest
        # side) and the first reach a tenth of it: the corners lie on or near the source surface,
        # so most are settled by the triangles of a cell or two (about 15 s for the bike; one grid
        # of every piece's triangles took 3.5 minutes for the same answers, but for a few hundred
        # corners exactly as near two triangles).
        size = np.median(np.ptp(t0, axis=1).max(axis=1))
        grid = TriangleGrid(t0, max(1.5 * size, 0.02))
        near, bary, _ = grid.closest(at, reach=max(0.1 * size, 0.005))
        cn = unit((n0[near] * bary[:, :, None]).sum(axis=1))
        off = ~((cn * fn).sum(axis=1) >= math.cos(math.radians(NORMAL_GUARD_DEG)))   # NaN counts as off
    if off.any():
        cn[off] = vertex_normals(v, f, per_corner=True)[off]
    return (*split_corners(v, f, cn, SPLIT_DEG), int(off.sum()))


def split_corners(v, f, cn, deg):
    """One vertex per group of a vertex's corners whose normals (cn, (3m, 3) by triangle and
    corner) agree: each corner in turn joins the first group whose mean so far is within deg of
    it, or starts its own. Returns (verts, tris, normals): a vertex's copies in a row, in the
    order of the vertices, and each normal its group's mean. Where every corner is within half
    of deg of a vertex's first corner (most vertices) they all join that one group, which needs
    no loop: the mean of normals within an angle of one stays within it."""
    flat = f.reshape(-1)
    order = np.argsort(flat, kind="stable")   # the corners by vertex, in their order
    vert = flat[order]
    start = np.r_[0, np.flatnonzero(vert[1:] != vert[:-1]) + 1]
    count = np.diff(np.r_[start, len(vert)])
    lead = np.repeat(start, count)
    cos_half = math.cos(math.radians(deg / 2.0 - 0.5))   # half a degree in hand for the rounding
    together = (cn[order] * cn[order[lead]]).sum(axis=1) >= cos_half
    one = np.logical_and.reduceat(together, start)
    group = np.zeros(len(flat), np.int64)   # by sorted corner
    groups = np.ones(len(start), np.int64)
    cos_t = math.cos(math.radians(deg))
    for s in np.flatnonzero(~one):
        a, b = start[s], start[s] + count[s]
        means = []
        for i in range(a, b):
            x, y, z = cn[order[i]]
            for g, m in enumerate(means):
                length = max(math.sqrt(m[0] * m[0] + m[1] * m[1] + m[2] * m[2]), 1e-12)
                if (m[0] * x + m[1] * y + m[2] * z) / length >= cos_t:
                    m[0] += x
                    m[1] += y
                    m[2] += z
                    group[i] = g
                    break
            else:
                group[i] = len(means)
                means.append([x, y, z])
        groups[s] = len(means)
    first_new = np.cumsum(groups) - groups   # each vertex's first copy
    new = np.repeat(first_new, count) + group
    nn = np.zeros((int(groups.sum()), 3))
    np.add.at(nn, new, cn[order])   # in the corners' order, as the groups were summed
    newidx = np.empty(len(flat), np.int64)
    newidx[order] = new
    copies = np.repeat(vert[start], groups)
    return v[copies], newidx.reshape(-1, 3), unit(nn)



# --- textures and materials --------------------------------------------------------------

def write_dds(path: Path, rgba: np.ndarray):
    """An uncompressed RGBA8 DDS with one mip level (the palette must never blend)."""
    h, w = rgba.shape[:2]
    header = struct.pack("<4sI", b"DDS ", 124)
    header += struct.pack("<IIIII", 0x1 | 0x2 | 0x4 | 0x8 | 0x1000, h, w, w * 4, 0)   # flags: caps, height, width, pitch, pixelformat
    header += struct.pack("<I", 1) + b"\0" * 44                                    # mip count, reserved
    # A8R8G8B8: the masks name the channels in a little-endian pixel, so the bytes go B, G, R, A.
    header += struct.pack("<II4sIIIII", 32, 0x41, b"\0\0\0\0", 32, 0xFF0000, 0xFF00, 0xFF, 0xFF000000)
    header += struct.pack("<IIIII", 0x1000, 0, 0, 0, 0)                            # caps: texture
    bgra = rgba[:, :, [2, 1, 0, 3]].astype(np.uint8)
    path.write_bytes(header + bgra.tobytes())


def write_palette(folder: Path, order, body):
    """The fallback build's three palette textures (textures\\CMB\\CMB_Bike_d/_n/_s.dds); returns
    each material's UV."""
    folder.mkdir(parents=True, exist_ok=True)
    d = np.zeros((PALETTE_H, PALETTE_W, 4), np.uint8)
    n = np.zeros_like(d)
    s = np.zeros_like(d)
    n[:, :] = (128, 128, 255, 255)
    uvs = {}
    for i, name in enumerate(order):
        rgb, alpha, spec, gloss, env, _ = MATERIALS[name]
        if rgb is None:
            rgb = body
        d[:, i * BLOCK:(i + 1) * BLOCK] = (*rgb, alpha)
        s[:, i * BLOCK:(i + 1) * BLOCK] = (spec, gloss, env, 255)
        uvs[name] = ((i * BLOCK + BLOCK / 2) / PALETTE_W, 0.5)
    for suffix, image in (("d", d), ("n", n), ("s", s)):
        write_dds(folder / f"{PALETTE}_{suffix}.dds", image)
    return uvs


SHADER_KEYS = ("shader", "cube", "env_scale", "smoothness", "spec_colour", "spec_mult", "emit", "alpha", "two_sided",
               "cast_shadows_worn", "cast_shadows_parked", "textures_of", "ssr")   # ssr (2026-11-02a): the materials file's
# screen-space reflections only (bike_textures.write_bgsm); the nif's own block keeps none: a shape naming a materials
# file takes the file's


def cube_path(cube):
    """A cube map as bike_materials.json names it (a CUBES shorthand, or a path under Textures)
    as the nif does."""
    path = CUBES.get(cube, cube).replace("/", "\\")
    return path if path.lower().startswith("textures\\") else "textures\\" + path


def load_shaders(path):
    """Each shape's shader settings and material stem: SHADER_BASE, DEFAULT_SHADERS over it, and
    the shape's material in bike_materials.json over those ({"materials": {<mat>:
    {"labels": [...], and any of SHADER_KEYS}}}). Since the 2026-11-10a build the riding bike's front end (FRONT_ROLES)
    casts as the parked one does: its cast_shadows_worn is its cast_shadows_parked, whatever the table says (test 52's
    wish, the front wheel's shadow; test 34's rule, no shadow from the front end, was for a headlamp at the lens, and
    the shadow lamp sits 28 past it since test 35); the lit overlays (WORN_ONLY) keep their own. Every shape of either
    label set (LABELS, LOOK_LABELS: a materials file may name either's); spec[OFF_MAT] is the invisible material's
    (2026-11-07a: OFF_SHADER, bike_materials.json's "off" over it), which no shape has as its own."""
    known = dict(LABELS + LOOK_LABELS + C2_LABELS)
    mats = {label: SHAPE_MAT.get(label, label) for label in known}
    spec = {}
    for label, role in known.items():
        spec[label] = {**SHADER_BASE, "cast_shadows_worn": label not in WORN_ONLY, "cast_shadows_parked": True,
                       **DEFAULT_SHADERS[label]}
    off = {**SHADER_BASE, **OFF_SHADER}
    if path:
        data = json.loads(Path(path).read_text())
        for mat, m in data.get("materials", {}).items():
            if mat == OFF_MAT:
                off.update({k: m[k] for k in SHADER_KEYS if k in m})
            for label in m.get("labels", []):
                if label not in spec:
                    raise ValueError(f"{path}: material {mat} names {label!r}, which isn't one of the shapes (LABELS)")
                mats[label] = mat
                spec[label].update({k: m[k] for k in SHADER_KEYS if k in m})
    for label, role in known.items():
        s = spec[label]
        if s["shader"] not in SHADER_TYPES:
            raise ValueError(f"{label}: shader {s['shader']!r} isn't one of {list(SHADER_TYPES)}")
        if s["shader"] == "env" and not s.get("cube"):
            raise ValueError(f"{label}: an environment-mapped shader needs a cube map")
        if role in FRONT_ROLES and label not in WORN_ONLY:   # 2026-11-10a: the front end casts as the parked bike's
            s["cast_shadows_worn"] = bool(s["cast_shadows_parked"])
    spec[OFF_MAT] = off
    return spec, mats


def texture_paths(spec, mat, worn, palette):
    """A shape's texture set: its material's own (textures\\CMB\\Bike\\<mat>_d/_n/_s, _g when it
    glows by a glow map on the riding bike; another material's with "textures_of", as the rear disc the front's) or the
    fallback build's palette, and its cube map."""
    base = f"textures\\CMB\\{PALETTE}" if palette else f"textures\\CMB\\Bike\\{spec.get('textures_of') or mat}"
    t = {"Diffuse": f"{base}_d.dds", "Normal": f"{base}_n.dds", "Specular": f"{base}_s.dds"}
    if worn and not palette and spec["shader"] == "glow" and spec["emit"] and spec["emit"].get("glow_map"):
        t["Glow"] = f"{base}_g.dds"
    if spec["shader"] == "env":
        cube = cube_path(spec["cube"])
        if palette and not cube.lower().startswith("textures\\shared\\"):
            cube = cube_path("CH")   # the fallback build has no texture stage to write our mirror's cube: vanilla chrome's
        t["EnvMap"] = cube
    return t


# --- nif ---------------------------------------------------------------------------------

def shader_setup(shape, base_props, spec, skinned, worn, textures, material=""):
    """The shape's BSLightingShaderProperty: the materials file it names (material: "" with
    --bgsm 0, as 27c) and the same values and textures in the block itself, so a missing file
    looks the same (and the bits no materials file carries, Skinned, are right)."""
    props = base_props.copy()
    props.nameID = props.controllerID = -1
    props.rootMaterialNameID = -1   # copied from the vanilla block it named an unrelated string of ours (27c)
    kind = spec["shader"]
    emit = spec["emit"] if worn else None   # parked, nothing is lit
    if kind == "glow" and not (emit and "Glow" in textures):
        kind = "default"   # lit by the emissive colour alone (27c's headlamp ring, proven in test 30), or not at all
    sf1 = SF1_SPECULAR | SF1_OWN_EMIT | SF1_ZBUFFER_TEST
    if skinned:
        sf1 |= SF1_SKINNED
    if spec["cast_shadows_worn" if worn else "cast_shadows_parked"]:
        sf1 |= SF1_CAST_SHADOWS
    sf2 = SF2_ZBUFFER_WRITE
    if spec["two_sided"]:   # the model has single-plane bits (rim lips, fender undersides) that vanish from one side otherwise
        sf2 |= SF2_DOUBLE_SIDED
    props.Shader_Type = SHADER_TYPES[kind]
    props.Env_Map_Scale = 0.0
    if kind == "env":
        sf1 |= SF1_ENV_MAP
        props.Env_Map_Scale = float(spec["env_scale"])
    if emit:
        for i in range(3):
            props.Emissive_Color[i] = float(emit["colour"][i])
        props.Emissive_Color[3] = 1.0
        props.Emissive_Mult = float(emit["mult"])
        if "Glow" in textures:
            sf2 |= SF2_GLOW_MAP
    else:
        for i in range(3):
            props.Emissive_Color[i] = 0.0
        props.Emissive_Mult = 1.0
    props.Shader_Flags_1 = sf1
    props.Shader_Flags_2 = sf2
    props.Glossiness = float(spec["smoothness"])   # Fallout 4's smoothness, 0..1 (27c wrote Skyrim's 90/30/110/30)
    props.Spec_Str = float(spec["spec_mult"])
    for i in range(3):
        props.Spec_Color[i] = float(spec["spec_colour"][i])
    props.Alpha = 1.0
    shape.shader.name = material
    shape.shader._properties = props
    shape.shader._checked_for_materials = True   # PyNifly would read the materials file into these if it found one
    shape.save_shader_attributes()
    for slot, path in textures.items():
        shape.shader.set_texture(slot, path)   # the shader block exists now, so this writes to it
    if spec["alpha"]:
        a = spec["alpha"]
        blend = a.get("mode", "blend") == "blend"
        shape.has_alpha_property = True
        shape.alpha_property.properties.flags = int(a.get("flags") or (ALPHA_BLEND_FLAGS if blend else 0x12EC))
        shape.alpha_property.properties.threshold = int(a.get("threshold", 0 if blend else 127))
        shape.save_alpha_property()


def add_shape(nif, name, verts, tris, uvs, normals, base_props, use_type, spec, skinned, worn, textures, material="",
              bone=None, bind=None, TransformBuf=None, parent=None):
    props = base_props.copy()
    props.nameID = props.controllerID = props.collisionID = -1
    props.skinInstanceID = props.shaderPropertyID = props.alphaPropertyID = -1
    if not skinned:
        # Test 40: the parked bike's positions in full precision. In half floats (the vanilla
        # shape's format) they sit on a 1/16-unit grid above 64 units, which flattened 1,083
        # small triangles to nothing (1,325 of test 40's mesh would be). The worn nifs keep
        # half floats until one is tried in game (PyNifly writes them, vertex format 0x45b).
        props.hasFullPrecision = 1
    new = nif.createShapeFromData(name, verts, tris, uvs, normals, props=props, use_type=use_type, parent=parent)
    if skinned:
        def buf(m):
            b = TransformBuf()
            b.store([m[0][3], m[1][3], m[2][3]], [m[0][:3], m[1][:3], m[2][:3]], [1.0, 1.0, 1.0])
            return b
        identity = TransformBuf()
        identity.set_identity()
        new.set_global_to_skin(identity)
        new.add_bone(bone, buf(bind) if bind else identity)
        new.set_skin_to_bone_xform(bone, buf(rigid_inverse(bind)) if bind else identity)
        new.setShapeWeights(bone, [(i, 1.0) for i in range(len(verts))])
    shader_setup(new, base_props.shader_props, spec, skinned, worn, textures, material)
    return new


def fix_all_bone_bounds(path: Path, spheres, skin_to_bone=None):
    """A culling sphere per shape into its BSSkin::BoneData, in the order the shapes were
    made (the game culls skinned meshes with it; nifly's own is too small for a mesh this
    long, and the plugin tells the moving parts apart by where their spheres are)."""
    data = bytearray(path.read_bytes())
    blocks = [off for off, name in _block_offsets(data) if name == "BSSkin::BoneData"]
    if len(blocks) != len(spheres):
        raise ValueError(f"{path}: {len(blocks)} bone-data blocks for {len(spheres)} shapes")
    for off, (centre, radius) in zip(blocks, spheres):
        if struct.unpack_from("<I", data, off)[0] != 1:
            raise ValueError("expected one bone in BSSkin::BoneData")
        c = list(apply(skin_to_bone, centre)) if skin_to_bone else list(centre)
        struct.pack_into("<4f", data, off + 4, *c, radius)
    path.write_bytes(bytes(data))


def sphere_of(verts):
    lo = verts.min(axis=0)
    hi = verts.max(axis=0)
    centre = (lo + hi) / 2
    return centre, float(np.linalg.norm(verts - centre, axis=1).max()) + 1.0


class Base:
    """What's copied from the vanilla shape: its buffer properties and shader properties."""
    def __init__(self, shape):
        self.props = shape.properties
        self.shader_props = shape.shader.properties
        self.use_type = shape.properties.bufType

    def copy(self):
        return self.props.copy()


# --- the shapes --------------------------------------------------------------------------

def to_worn_frame(v):
    """Parked model frame -> the worn bike's (a half turn about z: the winding holds); seat_at apart."""
    return np.column_stack([-v[:, 0], -v[:, 1], v[:, 2]])


def corner_normals_split(v, f):
    """Shading normals for a piece of ours given without: each corner its face's, and a vertex
    split where they part by more than SPLIT_DEG (hard edges stay hard, curves round)."""
    cn = np.repeat(unit(face_normals(v, f)), 3, axis=0)
    return split_corners(v, f, cn, SPLIT_DEG)


def seam_split(v, f, n, uv):
    """One vertex per (vertex, UV) pair its corners use (the seam rule, which bike_textures.py
    counts the same way: corners share a vertex iff the same exported vertex and the same UV
    quantised to 1/32768). uv is per corner, (T, 3, 2). Returns (verts, tris, normals, uvs)."""
    q = np.round(np.asarray(uv, dtype=np.float64).reshape(-1, 2) * 32768.0).astype(np.int64)
    key = np.column_stack([f.reshape(-1), q])
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    return v[uniq[:, 0]], inv.reshape(-1, 3), n[uniq[:, 0]], uniq[:, 1:] / 32768.0


def overlay_gaps(pairs):
    """The least gap from each overlay to the surface under it, as built and in the worn nifs'
    half floats (worn coordinates up to 128 sit on a 1/16 grid, so an overlay within
    a step or two of what it covers can sink into it in places and z-fight). pairs: (overlay,
    base, verts (n,3) worn, tris (m,3,3) worn, nominal). Returns [(overlay, base, nominal, gap,
    gap in half floats)]; raises if a gap as built is under 0.9 of its nominal (the pieces'
    offsets) or in half floats under 0.4 of it (0.1 for 0.25: more than a step of the grid; the
    rounding of both surfaces can take up to 0.09 off a 0.25 gap along the dial's normal)."""
    out = []
    for name, base, verts, tris, nominal in pairs:
        if not len(verts) or not len(tris):
            raise ValueError(f"overlay check: no geometry for {name} over {base}")
        size = float(np.median(np.ptp(tris, axis=1).max(axis=1)))
        exact = TriangleGrid(tris, max(size, 0.5)).closest(verts, reach=1.0)[2].min()
        h = lambda a: np.asarray(a, dtype=np.float16).astype(np.float64)   # noqa: E731
        half = TriangleGrid(h(tris), max(size, 0.5)).closest(h(verts), reach=1.0)[2].min()
        out.append((name, base, nominal, float(exact), float(half)))
        if exact < 0.9 * nominal or half < 0.4 * nominal:
            raise ValueError(f"{name} is {exact:.3f} off {base} as built, {half:.3f} in half floats, for a nominal "
                             f"{nominal} (at least 0.9 of it as built and 0.4 in half floats)")
    return out


def axis_rotation(axis, deg):
    """The rotation by deg about a unit axis (Rodrigues; right-handed, as the plugin's AxisRotation)."""
    a = unit(np.asarray(axis, dtype=np.float64))
    t = math.radians(deg)
    k = np.array([[0.0, -a[2], a[1]], [a[2], 0.0, -a[0]], [-a[1], a[0], 0.0]])
    return np.eye(3) + math.sin(t) * k + (1.0 - math.cos(t)) * k @ k


def turning_clearance(verts, tris, steer_point, steer_axis, bar_angle, step=1.0):
    """The least distance from a part that turns with the bars (its vertices, worn) to a fixed
    surface (triangles (m,3,3), worn) with the bars anywhere from -bar_angle to +bar_angle (every
    step degrees), turned about steer_axis through steer_point as the plugin turns them. Returns
    (gap, angle). The vertices against the surface: a mirror's corners and the tank's are what
    come close, so it reads a few hundredths short of a surface-to-surface gap at most. Only the
    vertices within 6 of the surface's box are searched (a far one costs a search of the whole
    surface), so a gap over 6 reads as the distance to the box."""
    lo, hi = tris.min(axis=(0, 1)), tris.max(axis=(0, 1))
    sp = np.asarray(steer_point, dtype=np.float64)
    grid = TriangleGrid(tris, 2.0)
    limit = abs(bar_angle)

    def least(angles):
        moved = np.stack([(verts - sp) @ axis_rotation(steer_axis, deg).T + sp for deg in angles])   # (angles, n, 3)
        gaps = np.linalg.norm(np.maximum(0.0, np.maximum(lo - moved, moved - hi)), axis=2)   # to the box: a lower bound
        near = gaps < 6.0
        if near.any():   # every angle's near vertices in one search
            gaps[near] = grid.closest(moved[near], reach=1.0)[2]
        per_angle = gaps.min(axis=1)
        i = int(np.argmin(per_angle))
        return float(per_angle[i]), float(angles[i])

    # Every 4 degrees, then every `step` within 4 of the closest (the gap changes smoothly with the angle).
    coarse = least(np.unique(np.r_[np.arange(-limit, limit, 4.0), limit]))
    fine = np.arange(max(-limit, coarse[1] - 4.0), min(limit, coarse[1] + 4.0) + 1e-9, step)
    return min(coarse, least(fine))


def fmt_value(value, digits):
    """A number or a point for CMB_BikeParts.ini (as given if it's a string already)."""
    if isinstance(value, str):
        return value
    if np.ndim(value):
        return ",".join(fmt_value(x, digits) for x in value)
    return f"{round(float(value), digits) + 0.0:g}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pynifly", type=Path, required=True, help="PyNifly's io_scene_nifly folder")
    ap.add_argument("--gltf", type=Path, required=True, help="the model's scene.gltf")
    ap.add_argument("--vanilla", type=Path, required=True, help="vanilla motorcycle_clean.nif (its collision is kept)")
    ap.add_argument("--out", type=Path, required=True, help="output folder, normally <Data>/Meshes/CMB")
    ap.add_argument("--textures", type=Path, required=True, help="normally <Data>/Textures/CMB (the palette goes there with --uvs none)")
    ap.add_argument("--seat", type=Path, help="the riding clips folder (MT\\CMB_Rider, with CMB_RiderSeat.json)")
    ap.add_argument("--tris", type=int, default=90000,
                    help="the triangle budget the pieces' shares are cut from (each piece's by its area is the "
                         "simplifier's target); the error cap stops the pieces that can't reach theirs without losing "
                         "their shape, so 90000 comes out at about 225k triangles")
    ap.add_argument("--body", default="7a1118", help="the tank and fenders' colour, hex rgb (the palette's)")
    ap.add_argument("--sit", type=float, default=0.27,
                    help="the hips go this far along the seat from its front edge (0..1); 0.27 is snug behind the "
                         "tank, where the arms, nearly straight on this bike, still reach the grips with the bars turned")
    ap.add_argument("--seat-at", type=float, help="instead of --sit: the parked model's y that goes under the hips")
    ap.add_argument("--grip", default="29.4,-10.7,96",
                    help="the grip's centre on the +X side, parked model x,y,z (the rubber sleeve's, see above)")
    ap.add_argument("--peg", default="19,6,27", help="the foot peg's top on the +X side, parked model x,y,z")
    ap.add_argument("--steer", help="the steering axis if it isn't found: x,y,z of a point on it (parked model) and the rake in degrees")
    ap.add_argument("--bar-angle", type=float, default=20.0, help="how far the bars turn, degrees (0: nothing turns)")
    ap.add_argument("--stage", choices=("export", "build"),
                    help="export: write the shapes to --stage-dir for the texture stage and stop; build: make the nifs "
                         "with the texture stage's UVs from --stage-dir (see BUILD STAGES)")
    ap.add_argument("--stage-dir", type=Path, help="the stage folder (manifest.json, shapes/, uv/)")
    ap.add_argument("--materials", type=Path,
                    help="bike_materials.json, each material's shader values (default: the one next to this script, "
                         "else built-in values)")
    ap.add_argument("--uvs", choices=("none", "stage"),
                    help="none: palette UVs and textures, the fallback build (the default without --stage); "
                         "stage: the texture stage's (--stage build)")
    ap.add_argument("--bgsm", type=int, choices=(0, 1),
                    help="1: each shape names its materials file (the default with --uvs stage); 0: empty names, the "
                         "nif's own shader block alone (27c's way; the default with --uvs none)")
    ap.add_argument("--volume-guard", type=int, choices=(0, 1), default=1,
                    help="1 (since the 2026-11-01a build): a closed piece the simplifier crushed (under 0.6 of its volume "
                         "kept) is cut again at twice its share till it keeps 0.8 (volume_guard); 0: 2026-10-31a's cut")
    ap.add_argument("--disc", choices=("ours", "model"), default="ours",
                    help="ours (since the 2026-11-01a build): the brake discs are the mod's own drilled discs "
                         "(bike_pieces.disc_pieces), shapes wheelF_disc and wheelR_disc in place of the model's plates; "
                         "model: the model's discs in the tyres' shapes, 2026-10-31a's 28 shapes")
    ap.add_argument("--disc-bore", choices=("shared", "bolts"), default="shared",
                    help="shared (since 2026-11-02a): our discs' bore cut at bike_pieces.DISC_HUB_REF of the outer "
                         "radius, where the art paints it (inside the bolt heads, or the build stops); bolts: at the "
                         "bolt heads' least radius, the 2026-11-01a build's (its five nifs byte for byte). The export "
                         "writes it into the stage manifest, and the build (and bike_art.py) refuse another")
    ap.add_argument("--view", type=int, choices=(0, 1), default=1,
                    help="1 (since the 2026-11-01a build): also write CMB_BikeView.nif, the bike in first person (the worn "
                         "shapes unskinned under a hidden node, which the plugin shows and places); 0: not written")
    ap.add_argument("--look-slots", type=int, choices=(0, 1), default=1,
                    help="1 (since the 2026-11-07a build, the customisation slots): static_badge split into "
                         "static_badgeTankL, static_badgeTankR and static_badgeRear, the rear fender's patch "
                         "static_badgeFender (invisible), the parked nif's under-bar mirrors shown with invisible "
                         "<label>_off.bgsm materials (PARKED_OFF) instead of node-hidden: 33 shapes; 0: LABELS' 30, "
                         "2026-11-06a's nifs byte for byte")
    ap.add_argument("--look-rims", type=int, choices=(0, 1), default=1,
                    help="1 (since the 2026-11-08a build): the seven rim styles, each wheel's its own shape "
                         "(wheelF_rimLaced ... wheelR_rimScrap, bike_pieces.rim_style_pieces), invisible materials "
                         "files until a Rims option swaps one on; 0: none (with --look-plate 0, 2026-11-07a's nifs "
                         "byte for byte). Only with --look-slots 1")
    ap.add_argument("--look-plate", type=int, choices=(0, 1), default=1,
                    help="1 (since the 2026-11-08a build): the licence plate split from static_black into "
                         "static_plate (its own UVs and materials), and static_plateText over its face, invisible "
                         "until a text is swapped on; 0: the plate in static_black, as 2026-11-07a. Only with "
                         "--look-slots 1")
    args = ap.parse_args()
    grip = np.array([float(t) for t in args.grip.split(",")])
    peg = np.array([float(t) for t in args.peg.split(",")])
    uvs_mode = args.uvs or ("stage" if args.stage == "build" else "none")
    if args.stage and not args.stage_dir:
        ap.error("--stage needs --stage-dir")
    if uvs_mode == "stage" and args.stage != "build":
        ap.error("--uvs stage is the texture stage's UVs: use it with --stage build")
    if args.stage == "build" and uvs_mode != "stage":
        ap.error("--stage build takes its UVs from the stage folder (--uvs stage)")
    palette = uvs_mode == "none"
    use_bgsm = args.bgsm if args.bgsm is not None else int(not palette)
    if use_bgsm and palette:
        ap.error("--bgsm 1 names materials files that point at the texture stage's textures: not with --uvs none")
    materials_path = args.materials
    if materials_path is None and (Path(__file__).resolve().parent / "bike_materials.json").exists():
        materials_path = Path(__file__).resolve().parent / "bike_materials.json"
    shaders, mat_of = load_shaders(materials_path)
    exporting = args.stage == "export"

    sys.path.insert(0, str(args.pynifly))
    from pyn.pynifly import NifFile, TransformBuf  # noqa: E402
    try:
        import bike_pieces as BP   # the speedometer, the light shells, the under-bar mirrors (the mod's own parts)
    except ImportError as e:
        print(f"bike_pieces.py (next to this script) is needed for the speedometer, lights and mirrors: {e}", file=sys.stderr)
        return 1

    body = tuple(int(args.body[i:i + 2], 16) for i in (0, 2, 4))
    print(f"loading {args.gltf}")
    corner_normals, sources = {}, {}
    groups = load_gltf(args.gltf, corner_normals, sources)
    unknown = sorted(set(groups) - set(MATERIALS))
    if unknown:
        print(f"materials with no entry in MATERIALS: {unknown}", file=sys.stderr)
        return 1
    # The parked model's frame: the vanilla's length, centred in x and y, the ground at z = 0.
    allv = np.vstack([v for v, _ in groups.values()])
    lo, hi = allv.min(axis=0), allv.max(axis=0)
    scale = VANILLA_LENGTH / (hi[1] - lo[1])
    shift = np.array([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
    for name, (v, f) in groups.items():
        groups[name] = ((v + shift) * scale, f)
    seat_v = groups["leather"][0]   # measured before decimation thins the seat's top
    parts = measure_parts(groups, [float(t) for t in args.steer.split(",")] if args.steer else None)
    rake = math.degrees(math.atan2(parts["steer_axis"][1], parts["steer_axis"][2]))
    print(f"wheels: front axle ({parts['front_axle'][1]:.1f}, {parts['front_axle'][2]:.1f}), rear ({parts['rear_axle'][1]:.1f}, "
          f"{parts['rear_axle'][2]:.1f}), radius {parts['wheel_radius']:.1f}, the rim's lip at {parts['rim_radius']:.1f}; steering axis through "
          f"({parts['steer_point'][1]:.1f}, {parts['steer_point'][2]:.1f}) raked {rake:.0f} deg"
          + (f" (from {parts['tubes']} fork tubes)" if "tubes" in parts else " (--steer)"))
    print(f"decimating: shares of {args.tris} triangles by area (the wheels' pieces at 2.5 times theirs), the error capped"
          f"{', the volume guard on' if args.volume_guard else ''}:")
    guard_report = {}
    pieces = decimate(groups, corner_normals, args.tris, weight=lambda v: 2.5 if wheel_of(v, parts) else 1.0,
                      role=lambda v: role_of(v, parts, raked=False), sources=sources, guard=bool(args.volume_guard),
                      shape_of=lambda name, v, mesh: label_of(role_of(v, parts), name, mesh) or "", guard_report=guard_report)
    look = bool(args.look_slots)
    look_rims, look_plate = look and bool(args.look_rims), look and bool(args.look_plate)   # 2026-11-08a
    if look_rims and tuple(getattr(BP, "RIM_STYLES", ())) != RIM_STYLES:
        print(f"bike_pieces.RIM_STYLES isn't {RIM_STYLES}", file=sys.stderr)
        return 1
    labels_built = [(label, role) for label, role in (look_labels(look_rims, look_plate) if look else LABELS)
                    if args.disc == "ours" or label not in DISC_LABELS]
    seat_front, seat_back = float(seat_v[:, 1].min()), float(seat_v[:, 1].max())
    hips_y = args.seat_at if args.seat_at is not None else seat_front + args.sit * (seat_back - seat_front)
    # The worn bike is turned round and shifted so the hips' spot lands at HIPS_Y_WORN.
    seat_at = hips_y + HIPS_Y_WORN
    # The seat's top under the buttocks (their lowest point is a little behind the hips' spot,
    # the thighs ahead of it sit higher), down the seat's middle.
    under = seat_v[(np.abs(seat_v[:, 0]) < 4) & (seat_v[:, 1] >= hips_y - 3) & (seat_v[:, 1] <= hips_y + 9)]
    seat_top_z = float(under[:, 2].max()) if len(under) else float(seat_v[:, 2].max())
    print(f"scale {scale:.4f}: the bike is {(hi[1] - lo[1]) * scale:.0f} long, {(hi[0] - lo[0]) * scale:.0f} wide, "
          f"{(hi[2] - lo[2]) * scale:.0f} tall; the seat runs y {seat_front:.0f}..{seat_back:.0f}, "
          f"the hips at y {hips_y:.1f} where its top is z {seat_top_z:.1f}")

    def to_worn(p):
        return [round(float(-p[0]), 2), round(float(-p[1] + seat_at), 2), round(float(p[2]), 2)]

    def worn_v(v):   # parked -> worn, arrays
        return np.column_stack([-v[:, 0], seat_at - v[:, 1], v[:, 2]])

    steer_axis_worn = [0.0, round(float(-parts["steer_axis"][1]), 4), round(float(parts["steer_axis"][2]), 4)]
    fit = dict(model=MODEL_NAME, seat_top_z=round(seat_top_z, 2),
               grip_r=to_worn([-abs(grip[0]), grip[1], grip[2]]), grip_l=to_worn([abs(grip[0]), grip[1], grip[2]]),
               peg_r=to_worn([-abs(peg[0]), peg[1], peg[2]]), peg_l=to_worn([abs(peg[0]), peg[1], peg[2]]),
               ground_foot_l=GROUND_FOOT_L, seat_at=round(seat_at, 2), hips_y=round(hips_y, 2),
               steer_point=to_worn(parts["steer_point"]), steer_axis=steer_axis_worn, bar_angle=args.bar_angle)
    if not exporting:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "CMB_BikeFit.json").write_text(json.dumps(fit, indent=1) + "\n")
        print(f"wrote {args.out / 'CMB_BikeFit.json'}: seat top {fit['seat_top_z']}, right grip {fit['grip_r']}, "
              f"right peg {fit['peg_r']} (worn space; rebuild the clips with riding_anims.py --fit)")

    # The vanilla's winding, so ours matches (a wrong one shows the bike inside out).
    src = NifFile(str(args.vanilla))
    vshape = src.shapes[0]
    vv = np.array(vshape.verts, dtype=np.float64)
    vt = np.array(vshape.tris, dtype=np.int64)
    vn = np.array(vshape.normals, dtype=np.float64)
    tri = vv[vt]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    agree = float(np.mean(np.sign(np.sum(fn * vn[vt[:, 0]], axis=1))))
    flip = agree < 0
    print(f"the vanilla's triangles wind {'with' if not flip else 'against'} their normals ({agree:+.2f}); "
          f"{'flipping ours' if flip else 'keeping the glTF winding'}")

    order = list(MATERIALS)   # the palette's blocks, and the texture stage's material ids (STAGE_NAME)
    stage_materials = [STAGE_NAME.get(m, m) for m in order]
    if palette and not exporting:
        uv_of = write_palette(args.textures, order, body)
        print(f"wrote the palette textures to {args.textures} ({PALETTE}_d/_n/_s.dds)")

    # The pieces' roles (role_of: what moves them) and shapes (label_of: what they are).
    roles = [role_of(v, parts) for _, v, _, _, _, _ in pieces]
    roles27 = [role_of(v, parts, raked=False) for _, v, _, _, _, _ in pieces]
    # What a bolt is on: the ordinary piece with the source vertex nearest its centre. The
    # source's, not the cut-down piece's (test 41: a brake disc cut from 8,336 triangles to
    # 1,434 has few vertices left near its bolts, and the silver ring beside them won, so 9 of
    # the 10 disc bolts went into the fork's or the fixed shapes and stood still on the
    # spinning discs).
    ordinary = [i for i, p in enumerate(pieces) if not p[3]] or list(range(len(pieces)))
    ordinary_v = np.vstack([pieces[i][4][0] for i in ordinary])
    ordinary_of = np.concatenate([np.full(len(pieces[i][4][0]), i) for i in ordinary])
    specks = [i for i, p in enumerate(pieces) if p[3]]
    if specks:
        nearest = nearest_vertex(ordinary_v, np.array([pieces[i][1].mean(axis=0) for i in specks]))
        for i, at in zip(specks, nearest):   # a bolt spins with a wheel if what it's on does (SMALL_AREA)
            if roles[ordinary_of[at]].startswith("wheel"):
                roles[i] = roles27[i] = roles[ordinary_of[at]]
    started = time.time()
    collected = {label: [] for label, _ in labels_built}   # (material, verts, tris, normals or None, UVs per vertex or None, glTF mesh, piece)
    dropped = dropped_ours = guarded = averaged = corners = 0
    dropped_meshes = {}
    plates = {}   # --disc ours: wheel role -> the model's disc plates replaced [(piece, source verts, tris)]
    bolts = {}    # and the small silver pieces of the same meshes, the bolts on the disc's carrier (kept): their verts
    raked = []
    dial_tris, tail_lens, signal_lenses, tank_v = [], [], [], []
    for pid, ((name, v, f, small, source, mesh), role, role27) in enumerate(zip(pieces, roles, roles27)):
        if old_headlamp(v, seat_at):
            dropped += 1
            continue
        if mesh == DIAL_MESH:
            dial_tris.append(worn_v(v)[f])
        label = label_of(role, name, mesh)
        if label is None:
            dropped_meshes[mesh] = dropped_meshes.get(mesh, 0) + len(f)
            dropped_ours += 1
            continue
        if look and label == "static_badge":   # 2026-11-07a: by island (each badge piece is one)
            if mesh not in (BADGE_TANK_MESH, BADGE_ROUNDEL_MESH):
                print(f"a badge piece of glTF mesh {mesh}, neither the tank plates' ({BADGE_TANK_MESH}) nor the "
                      f"roundel's ({BADGE_ROUNDEL_MESH})", file=sys.stderr)
                return 1
            label = BADGE_SPLIT[2] if mesh == BADGE_ROUNDEL_MESH else BADGE_SPLIT[0] if v[:, 0].mean() > 0 else BADGE_SPLIT[1]
        if args.disc == "ours" and mesh in DISC_MESHES and role.startswith("wheel") and name == "silver":
            if not small:
                plates.setdefault(role, []).append((pid, source[0], f))   # replaced by our own disc (below)
                continue
            bolts.setdefault(role, []).append(source[0])
        if role != role27:
            raked.append((label, mesh, worn_v(v).mean(axis=0)))
        if role.startswith("wheel") and name == "silver" and not small:
            # Test 40: the wheels' silver (the brake discs) shades by the averaged normals:
            # the discs are dented in the source, and its normals read as mottled grey under
            # the wheels' matte shader. The bolts on them (small) keep the glTF's: averaged,
            # their cross heads smeared (test 41).
            n = vertex_normals(v, f)
            averaged += 1
        else:
            v, f, n, off = gltf_normals(v, f, source)
            guarded += off
            corners += 3 * len(f)
        if role.startswith("wheel") and name == "material":
            v = seat_tyre(v, parts, role)
        if mesh == MIRROR_GLASS_MESH:   # convex: the cube map shades across the glass instead of one flat colour
            fsum = face_normals(v, f).sum(axis=0)
            glass_n = unit(fsum if fsum[1] > 0 else -fsum)   # toward the rider (parked +y)
            facing = n @ glass_n > 0.5
            n = n.copy()
            radius = getattr(BP, "MIRROR_CONVEX_R", CONVEX_RADIUS)   # as the under-bar mirrors' glass
            n[facing] = unit(np.asarray(BP.bend_convex(v[facing], n[facing], v.mean(axis=0), glass_n, radius)))
        if mesh == TAIL_LENS_MESH and worn_v(v)[:, 1].mean() < -55.0:   # the tail lens (95's other pieces: the side reflectors)
            tail_lens.append(worn_v(v)[f])
        if mesh == SIGNAL_LENS_MESH:
            signal_lenses.append(worn_v(v)[f])
        if mesh == TANK_MESH:
            tank_v.append((worn_v(v), f))
        collected[label].append((name, v, f, n, None, mesh, pid))
    n_plates = sum(len(x) for x in plates.values())
    print(f"the glTF's normals on {len(pieces) - dropped - dropped_ours - averaged - n_plates} pieces, the averaged on the wheels' {averaged} silver ones; "
          f"{guarded} of {corners} corners took the averaged normal (sampled over {NORMAL_GUARD_DEG:g} degrees off their own "
          f"triangle, or none in the file) ({time.time() - started:.0f} s)")
    for mesh, n_tris in sorted(dropped_meshes.items()):
        print(f"dropped glTF mesh {mesh} ({n_tris} triangles): {DROP_MESHES[mesh]}")
    for label, mesh, c in raked:
        print(f"  with the bars by the raked axis (27c: fixed): glTF mesh {mesh} at worn ({c[0]:.1f}, {c[1]:.1f}, {c[2]:.1f}) -> {label}")
    lamp = headlamp_pieces(seat_at, flip)
    for name, v, f in lamp:
        collected[label_of("front", name, -1)].append((name, v, f, None, None, -1, -1))
    print(f"the headlamp: {len(lamp)} pieces of our own on the fork bracket, turning with the bars; "
          f"{dropped} piece(s) of the model's own lamp dropped")

    # Ours (bike_pieces.py): the speedometer over the model's dial, the light shells over its tail and rear signal
    # lenses, the under-bar mirrors. Worn-frame inputs, parked-frame pieces.
    if not dial_tris or not tail_lens or not signal_lenses:
        print("the dial face, the tail lens or the rear signal lenses weren't found (glTF meshes "
              f"{DIAL_MESH}, {TAIL_LENS_MESH}, {SIGNAL_LENS_MESH})", file=sys.stderr)
        return 1
    started = time.time()
    ours, needle_keys = BP.speedo_pieces(np.concatenate(dial_tris), seat_at, flip)
    ours = list(ours)
    ours += list(BP.lamp_shells(np.concatenate(tail_lens), np.concatenate(signal_lenses), seat_at, flip))
    for style in ("egg", "D"):   # [Look] Mirrors 2 and 3
        ours += list(BP.mirror_under_pieces(style, fit["grip_r"], GRIP_RADIUS, MIRROR_CLAMP, seat_at, flip))
    # Our brake discs (--disc ours) in place of the model's plates: on the axle the plugin spins the wheel about, in
    # the plate's x range (its two faces, which the caliper's pads hug: 0.35 apart on the front, 0.32 on the rear), out
    # to its outer radius about that axle, the bore just inside the bolt heads on its carrier (the bolts stay the
    # model's, with the tyre's shape; without them, the plate's own least radius).
    disc_replaced, disc_fit = {}, {}
    if args.disc == "ours":
        for role, axle in (("wheelF", "front_axle"), ("wheelR", "rear_axle")):
            if not plates.get(role):
                print(f"--disc ours: no disc plate of glTF meshes {DISC_MESHES} found on the {role} wheel", file=sys.stderr)
                return 1
            pv = np.vstack([x[1] for x in plates[role]])
            c = parts[axle]
            r = np.hypot(pv[:, 1] - c[1], pv[:, 2] - c[2])
            x0, x1, r_out, r_hub = float(pv[:, 0].min()), float(pv[:, 0].max()), float(r.max()), float(r.min())
            if bolts.get(role):
                bv = np.vstack(bolts[role])
                r_hub = float(np.hypot(bv[:, 1] - c[1], bv[:, 2] - c[2]).min())
            try:
                dv, df, dn, duv = BP.disc_pieces((float(c[1]), float(c[2])), x0, x1, r_out, r_hub, flip, args.disc_bore)
            except ValueError as e:
                print(f"--disc-bore {args.disc_bore}: the {role} disc: {e}", file=sys.stderr)
                return 1
            ours.append(("silver", f"{role}_disc", dv, df, dn, duv))
            meshes_of = {}
            for pid, sv, sf in plates[role]:
                m = pieces[pid][5]
                meshes_of[m] = meshes_of.get(m, 0) + len(sf)
            for m, n_tris in meshes_of.items():
                disc_replaced[str(m)] = disc_replaced.get(str(m), 0) + n_tris
            disc_fit[f"{role}_disc"] = dict(meshes=sorted(meshes_of), x=[round(-x1, 4), round(-x0, 4)], r_out=round(r_out, 4),
                                            r_hub=round(r_hub, 4), axle_worn=to_worn(c), tris=len(df), verts=len(dv))
            print(f"  {role}_disc: our drilled disc ({len(df)} triangles, {len(dv)} vertices) for glTF mesh(es) "
                  f"{sorted(meshes_of)}' plate ({sum(meshes_of.values())} triangles): parked x {x0:.2f}..{x1:.2f}, "
                  f"r {r_hub:.2f}..{r_out:.2f} about the axle ({c[1]:.2f}, {c[2]:.2f})")
    made = time.time() - started
    next_piece = len(pieces)
    for material, label, v, f, n, uv in ours:
        if label not in collected:
            raise ValueError(f"bike_pieces gave a piece for {label!r}, which isn't a shape (LABELS)")
        if material not in MATERIALS:
            raise ValueError(f"bike_pieces gave a {material!r} piece, which isn't a material (MATERIALS)")
        v = np.asarray(v, dtype=np.float64)
        f = np.asarray(f, dtype=np.int64)
        if uv is not None:   # per vertex (V, 2) or per corner (T, 3, 2): per corner from here
            uv = np.asarray(uv, dtype=np.float64)
            if uv.shape == (len(v), 2) and uv.shape != (len(f), 3, 2):
                uv = uv[f]
            if uv.shape != (len(f), 3, 2):
                raise ValueError(f"bike_pieces: {label} UVs {uv.shape} for {len(v)} vertices, {len(f)} triangles")
        if n is None:   # each corner its face's normal, split at hard edges (the corners keep their order)
            v, f, n = corner_normals_split(v, f)
        else:
            n = unit(np.asarray(n, dtype=np.float64))
        collected[label].append((material, v, f, n, uv, -1, next_piece))
        next_piece += 1
    if look:   # 2026-11-07a: the rear fender's badge patch, cast onto the fender's pieces (parked frame)
        fender = [(v, f, n) for _, v, f, n, _, mesh, _ in collected["static_paint"] if mesh == REAR_FENDER_MESH]
        try:
            pv, pf, pn, puv = BP.fender_badge_patch(fender, flip)
        except ValueError as e:
            print(f"the rear fender's badge patch: {e}", file=sys.stderr)
            return 1
        collected[FENDER_BADGE].append(("logo_decals", pv, pf, unit(pn), puv.astype(np.float64), -1, next_piece))
        next_piece += 1
        print(f"  {FENDER_BADGE}: the rear fender's badge patch, {len(pf)} triangles, {len(pv)} vertices, lifted "
              f"{BP.FENDER_PATCH_LIFT} over glTF mesh {REAR_FENDER_MESH}'s {sum(len(x[1]) for x in fender)} triangles")
    rim_parts = {}   # 2026-11-08a: piece -> its part (bike_pieces.RIM_PART_MATERIAL's keys) for the stage export
    if look_plate:   # the plate's text overlay over its rear face (static_black's glTF mesh 24 pieces, parked frame)
        pv_ = [(v, f) for _, v, f, _, _, mesh, _ in collected["static_black"] if mesh in PLATE_MESHES]
        if not pv_:
            print(f"--look-plate 1: no piece of glTF mesh {PLATE_MESHES} in static_black", file=sys.stderr)
            return 1
        tris_ = np.concatenate([v[f] for v, f in pv_])
        wv, wf = BP.weld(tris_)
        face, _, _ = BP.plate_face(wv, wf)
        tv, tf, tn, tuv = BP.plate_text_overlay(wv[wf[face]], flip)
        collected[PLATE_TEXT].append(("logo_decals", tv, tf, unit(tn), tuv.astype(np.float64), -1, next_piece))
        next_piece += 1
        print(f"  {PLATE_TEXT}: the plate's text band, {len(tf)} triangles, lifted {BP.PLATE_TEXT_LIFT} over glTF mesh "
              f"{PLATE_MESHES[0]}'s rear face ({int(face.sum())} of its {len(wf)} triangles)")
    if look_rims:   # the rim styles about the axles (parked frame)
        for wheel, axle in (("F", "front_axle"), ("R", "rear_axle")):
            for style in RIM_STYLES:
                label = f"wheel{wheel}_rim{style}"
                for material, v, f, n, uv, part in BP.rim_style_pieces(style, wheel, [float(x) for x in parts[axle]], flip):
                    rim_parts[next_piece] = part
                    collected[label].append((material, v, f, unit(n), uv.astype(np.float64), -1, next_piece))
                    next_piece += 1
        print(f"  the rim styles: {', '.join(RIM_STYLES)} on each wheel, "
              f"{sum(len(p[2]) for lb, _ in RIM_STYLE_LABELS for p in collected[lb])} triangles")
    print(f"ours: {len(ours)} pieces (the speedometer's dial, backlight, needle and hub; the tail and brake light shells; "
          f"the under-bar mirrors, egg and D{'; the brake discs' if args.disc == 'ours' else ''}) ({made:.0f} s)")

    # The shapes, each its pieces together (the vanilla's winding).
    shapes = {}   # label -> dict(v, f, n, mat, src, piece, uvc (fixed UVs per corner or None), role)
    black_keep = None   # 2026-11-08a (--look-plate 1): which of the whole static_black's triangles stay in it
    for label, role in labels_built:
        if look_plate and label == PLATE_LABEL:   # made by static_black's split (below)
            continue
        if not collected[label]:
            print(f"the {label} shape has no pieces", file=sys.stderr)
            return 1
        vs, fs, ns, mats, srcs, pids, uvcs, off = [], [], [], [], [], [], [], 0
        for name, v, f, n, uvc, mesh, pid in collected[label]:
            if flip:
                f = f[:, [0, 2, 1]]
                if uvc is not None:
                    uvc = uvc[:, [0, 2, 1]]
            vs.append(v)
            fs.append(f + off)
            ns.append(n if n is not None else vertex_normals(v, f))   # our headlamp: its own
            mats += [order.index(name)] * len(f)
            srcs += [mesh] * len(f)
            pids += [pid] * len(f)
            uvcs.append(uvc)
            off += len(v)
        v, f, n = np.vstack(vs), np.vstack(fs), np.vstack(ns)
        uvc = None
        if label in FIXED_UV and label not in BADGE_UV:
            if any(u is None for u in uvcs):
                raise ValueError(f"{label}: a piece of bike_pieces' without the fixed UVs this shape needs")
            uvc = np.vstack(uvcs)
        elif label in BADGE_UV:   # the badges' own layout, over our emblem (per island: the split plates' are the same)
            buv = np.asarray(BP.badge_uvs(worn_v(v), f), dtype=np.float64)
            uvc = buv[f] if buv.shape == (len(v), 2) else buv.reshape(len(f), 3, 2)
        if len(v) > MAX_VERTS:
            print(f"the {label} shape has {len(v)} vertices, over the {MAX_VERTS} a shape may have with room for its UV "
                  f"seams. Lower --tris if it was raised; but --tris only sets the pieces' shares, and the error caps "
                  f"(AGG_CAP, FINE_AGG) and the pieces kept whole (KEEP_TRIS, PAINTED, BRIGHT) set a floor it can't go "
                  f"below: past that, loosen the caps or keep fewer pieces whole", file=sys.stderr)
            return 1
        shapes[label] = dict(v=v, f=f, n=unit(n), mat=np.array(mats, np.int16), src=np.array(srcs, np.int16),
                             piece=np.array(pids, np.int32), uvc=uvc, role=role)
        if look_plate and label == "static_black":   # 2026-11-08a: the plate out of the whole, as 2026-11-07a made it
            whole = shapes.pop(label)
            plate = np.isin(whole["src"], PLATE_MESHES)
            black_keep = ~plate
            for name, sel, rl in ((label, black_keep, role), (PLATE_LABEL, plate, ROLE_OF_LABEL[PLATE_LABEL])):
                used = np.zeros(len(whole["v"]), bool)
                used[whole["f"][sel].ravel()] = True
                remap = np.cumsum(used) - 1
                shapes[name] = dict(v=whole["v"][used], f=remap[whole["f"][sel]], n=whole["n"][used], mat=whole["mat"][sel],
                                    src=whole["src"][sel], piece=whole["piece"][sel], uvc=None, role=rl)
            pl = shapes[PLATE_LABEL]
            pl["uvc"] = np.asarray(BP.plate_uvs(pl["v"], pl["f"]), dtype=np.float64)
            print(f"  {PLATE_LABEL}: glTF mesh {PLATE_MESHES[0]}'s {int(plate.sum())} triangles out of static_black's "
                  f"{len(plate)} ({len(pl['v'])} vertices), its own UVs")
    shapes = {label: shapes[label] for label, _ in labels_built}   # the nifs' order

    # Checks: the overlays clear of what they cover in half floats; every mirror clear of the tank at full lock.
    def worn_tris(s, sel=None):
        t = worn_v(s["v"])[s["f"]]
        return t if sel is None else t[sel]

    dial = shapes["front_dial"]
    # The dial's face: front_dial's biggest piece (the hub cap over the needle is its other).
    tri_area = np.linalg.norm(face_normals(dial["v"], dial["f"]), axis=1)
    face_piece = max(set(dial["piece"].tolist()), key=lambda p: tri_area[dial["piece"] == p].sum())
    lens_all = np.concatenate([np.concatenate(tail_lens), np.concatenate(signal_lenses)])
    bases = {"dial face": worn_tris(dial, dial["piece"] == face_piece), "tail lens": np.concatenate(tail_lens),
             "tail and signal lenses": lens_all, "front_dialglow": worn_tris(shapes["front_dialglow"]),
             "rear_tail": worn_tris(shapes["rear_tail"])}
    started = time.time()
    overlays = [(name, base, worn_v(shapes[name]["v"]), bases[base], nominal) for name, base, nominal in OVERLAY_MIN]
    if look:   # 2026-11-07a: the fender patch over the rear fender (static_paint's glTF mesh REAR_FENDER_MESH)
        sp_ = shapes["static_paint"]
        overlays.append((FENDER_BADGE, "rear fender", worn_v(shapes[FENDER_BADGE]["v"]),
                         worn_tris(sp_, sp_["src"] == REAR_FENDER_MESH), BP.FENDER_PATCH_LIFT))
    if look_plate:   # 2026-11-08a: the text overlay over the plate's rear face
        pl = shapes[PLATE_LABEL]
        pface, _, _ = BP.plate_face(pl["v"], pl["f"])
        overlays.append((PLATE_TEXT, "plate face", worn_v(shapes[PLATE_TEXT]["v"]), worn_tris(pl, pface), BP.PLATE_TEXT_LIFT))
    gaps = overlay_gaps(overlays)
    for name, base, nominal, exact, half in gaps:
        print(f"  overlay {name} over {base}: {exact:.3f} off ({half:.3f} in half floats; nominal {nominal})")
    sp_w, ax_w = np.array(to_worn(parts["steer_point"])), np.array(steer_axis_worn)
    tank = np.concatenate([tv[tf] for tv, tf in tank_v])   # (m, 3, 3) worn
    print(f"  ({time.time() - started:.0f} s)")
    started = time.time()
    for label in MIRROR_VARIANTS:
        gap, deg = turning_clearance(worn_v(shapes[label]["v"]), tank, sp_w, ax_w, args.bar_angle)
        print(f"  {label}: {gap:.2f}{' or more' if gap >= 6.0 else ''} clear of the tank with the bars anywhere within "
              f"{args.bar_angle:g} degrees (closest at {deg:+.0f})")
        if gap < MIRROR_CLEARANCE:
            print(f"{label} comes within {gap:.2f} of the tank with the bars at {deg:+.0f} degrees (at least "
                  f"{MIRROR_CLEARANCE} wanted)", file=sys.stderr)
            return 1
    print(f"  ({time.time() - started:.0f} s)")

    # Worn: turned round to face +Y like a character, the seat over the origin, on one bone.
    def turned(v):
        return np.column_stack([-v[:, 0], -v[:, 1] + seat_at, v[:, 2]])

    spheres = {label: sphere_of(turned(s["v"])) for label, s in shapes.items()}
    if look:   # the split badges share the three's union sphere, 2026-11-06a's static_badge's (see BADGE_SPLIT)
        union = sphere_of(turned(np.vstack([shapes[b]["v"] for b in BADGE_SPLIT])))
        for b in BADGE_SPLIT:
            spheres[b] = union
    if look_plate:   # 2026-11-08a: static_black keeps 2026-11-07a's sphere (with the plate's vertices)
        spheres["static_black"] = sphere_of(turned(np.vstack([shapes["static_black"]["v"], shapes[PLATE_LABEL]["v"]])))
    pivot = np.array([float(x) for x in (needle_keys["NeedlePoint"].split(",") if isinstance(needle_keys["NeedlePoint"], str)
                                         else needle_keys["NeedlePoint"])])
    # The needle turns about its pivot: its sphere there, as long as the needle, so the sweep never leaves it.
    spheres["front_needle"] = (pivot, float(np.linalg.norm(turned(shapes["front_needle"]["v"]) - pivot, axis=1).max()) + 1.0)
    static_y = [c[1] for label, (c, _) in spheres.items() if not ROLE_OF_LABEL[label]]
    front_y = [c[1] for label, (c, _) in spheres.items() if ROLE_OF_LABEL[label] in ("front", "fork")]
    front_min_y = (max(static_y) + min(front_y)) / 2 if front_y else to_worn(parts["front_axle"])[1]
    print(f"{len(shapes)} shapes:")
    for label, s in shapes.items():
        c, r = spheres[label]
        srcs = sorted(set(int(x) for x in s["src"]) - {-1})
        print(f"  {label}: {len(s['v'])} vertices, {len(s['f'])} triangles, sphere ({c[0]:.1f}, {c[1]:.1f}, {c[2]:.1f}) r {r:.1f}"
              f"{', glTF meshes ' + ','.join(map(str, srcs)) if srcs else ''}{' + ours' if (s['src'] == -1).any() else ''}")
    print(f"FrontMinY {front_min_y:.1f}: the fixed shapes' spheres up to y {max(static_y):.1f}, the bars' and fork's from "
          f"{min(front_y):.1f}")

    if args.stage_dir:
        stage = args.stage_dir
        to_parked = np.array([[scale, 0, 0, scale * shift[0]], [0, scale, 0, scale * shift[1]],
                              [0, 0, scale, scale * shift[2]], [0, 0, 0, 1]])
        scene = gltf_scene_matrix(args.gltf)
        y_up_to_z_up = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=np.float64)
        manifest = dict(version=1, frame="parked", seat_at=round(seat_at, 4),
                        gltf_to_parked=to_parked.tolist(),
                        gltf_to_parked_applies_to="the raw POSITION accessors (the glTF's node matrices ignored)",
                        blender_to_parked=None if scene is None else (to_parked @ np.linalg.inv(y_up_to_z_up @ scene)).tolist(),
                        blender_to_parked_applies_to="a default Blender glTF import's world coordinates (node matrices "
                                                     "and the Y-up to Z-up turn applied)",
                        parked_to_worn="(-x, seat_at - y, z)", materials=stage_materials,
                        steer_point=[float(x) for x in parts["steer_point"]], steer_axis=[float(x) for x in parts["steer_axis"]],
                        steer_point_worn=to_worn(parts["steer_point"]), steer_axis_worn=steer_axis_worn,
                        bar_angle=args.bar_angle, max_verts=MAX_VERTS, labels={})
        # Since the 2026-11-01a build: the build flags, the volume guard's work and the discs (check_bike_meshes reads
        # them: the model's triangles per material may differ from the reference's by exactly these)
        if args.disc == "ours":   # 2026-11-02a: the bore's rule (an older export has none: the 2026-11-01a build's, bolts)
            manifest["disc_bore"] = args.disc_bore
        manifest.update(volume_guard_on=bool(args.volume_guard), disc=args.disc,
                        volume_guard=guard_report.get("volume_guard", []), volumes=guard_report.get("volumes", []),
                        disc_replaced=disc_replaced, discs=disc_fit)
        for label, s in shapes.items():
            manifest["labels"][label] = dict(
                role=s["role"], mat=mat_of[label], verts=len(s["v"]), tris=len(s["f"]),
                uv="fixed" if label in FIXED_UV else "unwrap", max_verts=MAX_VERTS,
                sources=sorted(set(int(x) for x in s["src"]) - {-1}), ours=bool((s["src"] == -1).any()),
                parked=label not in WORN_ONLY, parked_hidden=label in PARKED_HIDDEN and not look,
                **({"parked_off": label in PARKED_OFF} if look else {}))
            if label in dict(RIM_STYLE_LABELS):   # 2026-11-08a: the rim atlas's cell and the parts by material
                style, wheel = label[len("wheelF_rim"):], label[len("wheel")]
                manifest["labels"][label]["rim"] = dict(
                    style=style, index=RIM_STYLES.index(style) + 1, wheel=wheel, cell=list(BP.rim_cell(style, wheel)),
                    atlas=BP.RIM_ATLAS, margin=BP.RIM_MARGIN, regions={k: list(v) for k, v in BP.RIM_REGIONS.items()},
                    parts={p: m for p, m in BP.RIM_PART_MATERIAL.items()},
                    part_codes={p: i for i, p in enumerate(BP.RIM_PART_MATERIAL)})
            if look_plate and label == "static_black":
                manifest["labels"][label]["split"] = dict(
                    plate=PLATE_LABEL, meshes=list(PLATE_MESHES), whole_tris=int(len(black_keep)),
                    uv="the texture stage's static_black rows less the plate's (uv/static_black.npz of the whole)")
            if look_plate and label == PLATE_LABEL:
                manifest["labels"][label]["plate"] = dict(
                    face="0..1 read true from behind (u the viewer's right, v down)", strip_v=BP.PLATE_STRIP_V,
                    strip_dv=BP.PLATE_STRIP_DV, text=PLATE_TEXT, text_lift=BP.PLATE_TEXT_LIFT,
                    text_band_u=list(BP.PLATE_TEXT_BAND_U), text_band_v=list(BP.PLATE_TEXT_BAND_V))
        if exporting:
            (stage / "shapes").mkdir(parents=True, exist_ok=True)
            written, kept = [], []
            for label, s in shapes.items():
                arrays = dict(pos=s["v"].astype(np.float64), nrm=s["n"].astype(np.float32), tri=s["f"].astype(np.int32),
                              mat=s["mat"], src=s["src"], piece=s["piece"])
                if s["uvc"] is not None:
                    arrays["uv_fixed"] = s["uvc"].astype(np.float32)
                if label in dict(RIM_STYLE_LABELS):   # 2026-11-08a: each triangle's part (0 body, 1 trim, 2 steel)
                    codes = list(BP.RIM_PART_MATERIAL)
                    arrays["part"] = np.array([codes.index(rim_parts[int(p)]) for p in s["piece"]], dtype=np.int8)
                # Written only if it changed (since the 2026-11-01a build): savez stamps the time into the file, and the
                # texture stage keys its caches on the files' bytes, so a rewrite of the same arrays re-keyed every bake
                path = stage / "shapes" / f"{label}.npz"
                if path.exists():
                    try:
                        with np.load(path) as old:
                            same = set(old.files) == set(arrays) and all(
                                old[k].dtype == a.dtype and np.array_equal(old[k], a) for k, a in arrays.items())
                    except (OSError, ValueError):
                        same = False
                    if same:
                        kept.append(label)
                        continue
                np.savez_compressed(path, **arrays)
                written.append(label)
            gone = sorted(p.stem for p in (stage / "shapes").glob("*.npz") if p.stem not in shapes)
            for label in gone:   # a shape this build doesn't make (--disc model after ours)
                (stage / "shapes" / f"{label}.npz").unlink()
            (stage / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
            print(f"wrote the stage export to {stage}: manifest.json and {len(shapes)} shapes ({len(written)} written: "
                  f"{', '.join(written) or 'none'}; {len(kept)} unchanged{'; removed ' + ', '.join(gone) if gone else ''})")
            return 0
        # The build: the same shapes as the export, or the texture stage's UVs belong to something else.
        exported = json.loads((stage / "manifest.json").read_text())
        if args.disc == "ours" and exported.get("disc", "model") == "ours" and exported.get("disc_bore", "bolts") != args.disc_bore:
            print(f"{stage}: the export's discs have the bore {exported.get('disc_bore', 'bolts')!r}, this build "
                  f"--disc-bore {args.disc_bore}: export again with the same (build_bike.sh DISC_BORE=)", file=sys.stderr)
            return 1
        for label, s in shapes.items():
            with np.load(stage / "shapes" / f"{label}.npz") as e:
                same = (np.array_equal(e["pos"], s["v"]) and np.array_equal(e["tri"], s["f"]) and np.array_equal(e["mat"], s["mat"]))
            if not same or exported["labels"].get(label, {}).get("tris") != len(s["f"]):
                print(f"{stage}: the exported {label} isn't the shape this build makes: export again (--stage export) "
                      f"and rerun the texture stage", file=sys.stderr)
                return 1

    # The UVs, per triangle corner, and the vertices split along their seams.
    final = {}
    for label, s in shapes.items():
        if palette:
            per_mat = np.array([uv_of[m] for m in order])
            uvc = np.repeat(per_mat[s["mat"]][:, None, :], 3, axis=1)
            mat = mat_of[label]
        else:
            uv_file = args.stage_dir / "uv" / f"{label}.npz"
            info_file = args.stage_dir / "uv" / f"{label}.json"
            if uv_file.exists():
                with np.load(uv_file) as e:
                    uvc = np.asarray(e["uv"], dtype=np.float64)
                if label == "static_black" and black_keep is not None and uvc.shape == (len(black_keep), 3, 2):
                    uvc = uvc[black_keep]   # 2026-11-08a: the whole's UVs (the texture stage's) less the plate's
                    info_file = None
                if uvc.shape != (len(s["f"]), 3, 2):
                    print(f"{uv_file}: UVs {uvc.shape} for {len(s['f'])} triangles", file=sys.stderr)
                    return 1
                if s["uvc"] is not None and np.abs(uvc - s["uvc"]).max() > 1e-3:
                    print(f"  {label}: the texture stage's UVs differ from the fixed ones by up to "
                          f"{np.abs(uvc - s['uvc']).max():.4f} (the stage's are used)")
            elif s["uvc"] is not None:   # a fixed-UV shape the texture stage hasn't seen (2026-11-07a's): its rule
                uvc = np.round(s["uvc"] * 32768.0) / 32768.0   # (bike_textures.write_uv: quantised to 1/32768)
            else:
                print(f"{uv_file} is missing: run the texture stage (bike_textures.py) on {args.stage_dir}", file=sys.stderr)
                return 1
            info = json.loads(info_file.read_text()) if info_file is not None and info_file.exists() else {}
            mat = info.get("mat", mat_of[label])
            if mat != mat_of[label]:
                print(f"  {label}: material {mat} (the texture stage's), not {mat_of[label]}")
        if not np.isfinite(uvc).all():
            print(f"{label}: UVs that aren't numbers", file=sys.stderr)
            return 1
        v, f, n, uv = seam_split(s["v"], s["f"], s["n"], uvc)
        if not palette and "verts_after_seams" in info and info["verts_after_seams"] != len(v):
            print(f"{label}: {len(v)} vertices after the seams here, {info['verts_after_seams']} by the texture stage's "
                  f"count: the seam rule differs", file=sys.stderr)
            return 1
        if len(v) > MAX_VERTS:
            print(f"{label}: {len(v)} vertices with its UV seams, over {MAX_VERTS}: unwrap it with fewer seams or split it",
                  file=sys.stderr)
            return 1
        outside = int(((uv < -1e-6) | (uv > 1 + 1e-6)).any(axis=1).sum())
        if outside:
            print(f"  {label}: {outside} vertices with UVs outside 0..1")
        final[label] = dict(v=v, f=f, n=n, uv=uv, mat=mat, role=s["role"])
    if not palette:
        print("the UV seams: " + ", ".join(f"{label} {len(shapes[label]['v'])}->{len(x['v'])}" for label, x in final.items()))

    def material_name(label, worn, off=False):
        if not use_bgsm:
            return ""
        return f"Materials\\CMB\\Bike\\{final[label]['mat']}{'_off' if off else '_worn' if worn else ''}.bgsm"

    base = Base(vshape)

    # Parked: the vanilla nif, its shape hidden, ours added: not the lit overlays (the plain lens and dial show), the
    # under-bar mirrors hidden by the node flag (there for a preview and a later swap; the stock mirror shows); since
    # 2026-11-07a (--look-slots 1) not hidden but drawn with the invisible material, <label>_off.bgsm (PARKED_OFF),
    # which the mirror options' MSWPs swap for <label>.bgsm.
    parked = args.out / "CMB_BikeParked.nif"
    parked.write_bytes(args.vanilla.read_bytes())
    nif = NifFile(str(parked))
    old = nif.shapes[0]
    old.flags = old.flags | 1   # hidden
    for label, x in final.items():
        if label in WORN_ONLY:
            continue
        off = look and label in PARKED_OFF
        sh, tmat = (shaders[OFF_MAT], OFF_MAT) if off else (shaders[label], x["mat"])
        new = add_shape(nif, f"CMB_Bike_{label}", rows(x["v"]), rows(x["f"]), rows(x["uv"]), rows(x["n"]), base, base.use_type,
                        sh, False, False, texture_paths(sh, tmat, False, palette), material_name(label, False, off))
        if label in PARKED_HIDDEN and not look:
            new.flags = new.flags | 1
    nif.save()
    check = NifFile(str(parked))
    names = [s.name for s in check.shapes]
    hidden = [s.name for s in check.shapes if s.flags & 1]
    blocks = [name for _, name in _block_offsets(parked.read_bytes())]
    print(f"wrote {parked}: {len(names)} shapes {names}, hidden {hidden}, "
          f"collision {'kept' if any(b.startswith('bhk') for b in blocks) else 'NOT FOUND'} ({len(blocks)} blocks)")

    def worn(path: Path, bone, bind):
        out = NifFile()
        out.initialize("FO4", str(path), "NiNode", path.stem)
        allverts = []
        for label, x in final.items():
            tv = turned(x["v"])
            tn = to_worn_frame(x["n"])
            allverts.append(tv)
            add_shape(out, f"{path.stem}_{label}", rows(tv), rows(x["f"]), rows(x["uv"]), rows(tn), base, base.use_type,
                      shaders[label], True, True, texture_paths(shaders[label], x["mat"], True, palette),
                      material_name(label, True), bone, bind, TransformBuf)
        out.save()
        allverts = np.vstack(allverts)
        fix_all_bone_bounds(path, [spheres[label] for label in final], rigid_inverse(bind) if bind else None)
        check = NifFile(str(path))
        lo, hi = allverts.min(axis=0), allverts.max(axis=0)
        node_names = []
        try:
            node_names = [n.name for n in check.nodes.values()] if isinstance(check.nodes, dict) else [n.name for n in check.nodes]
        except Exception as e:   # noqa: BLE001
            node_names = [f"(nodes unreadable: {e})"]
        print(f"wrote {path}: {len(check.shapes)} shapes on {bone}; nodes {len(node_names)}")
        print(f"  bounds x[{lo[0]:.1f},{hi[0]:.1f}] y[{lo[1]:.1f},{hi[1]:.1f}] z[{lo[2]:.1f},{hi[2]:.1f}]")
        for s in check.shapes:
            if bind:
                r = s.get_shape_skin_to_bone(bone)
                s2b = [list(r.rotation[i]) + [r.translation[i]] for i in range(3)] + [[0.0, 0.0, 0.0, 1.0]]
                m = mat_mul(bind, s2b)
                vs = s.verts
                err = max(math.dist(apply(m, p), p) for p in vs[:2000])
                if err > 0.01:
                    raise ValueError(f"{path} {s.name}: skin-to-bone round trip off by {err}")
            label = s.name[len(path.stem) + 1:]
            c, r = spheres[label]
            print(f"  {s.name}: {len(s.verts)} verts, bones {list(s.bone_weights)}, alpha {s.has_alpha_property}, "
                  f"sphere ({c[0]:.0f}, {c[1]:.0f}, {c[2]:.0f}) r {r:.0f}")

    # The moving parts for the F4SE plugin, in the worn bike's mesh space: it tells a
    # wheel by a culling sphere on an axle and the bar assembly by one ahead of FrontMinY
    # (the fork's lower end counts with it: its sphere sits ahead too, and its name says
    # which it is). Grip is the +X grip's centre, the same point the fit file's grip_r
    # holds (so the clips' palm sits on it; the other grip mirrors it in x): the pivot
    # of the plugin's wrist roll. Test 38: the plugin rolled the hand about the wrist
    # node, which the clips put 6.5 units from the grip (6 along the fingers' axis, 2.5
    # across), so the palm swung off the bar as the forearm twisted. The needle (since the 2026-10-31a build)
    # turns about NeedleAxis through NeedlePoint, NeedleZero + NeedlePerMph a mph degrees,
    # NeedleMax at most; without those keys it stays at its rest.
    fa, ra, sp = to_worn(parts["front_axle"]), to_worn(parts["rear_axle"]), to_worn(parts["steer_point"])
    gr = fit["grip_r"]
    partsfile = args.out / "CMB_BikeParts.ini"
    partsfile.write_text(
        "; Written by the bike's mesh build (tools/rider) for CMB_Slope.dll: the worn bike's moving parts, in its mesh space\n"
        "; (+Y forward, Z up, the ground at z 0). Delete this file and nothing moves.\n"
        "[Parts]\n"
        f"FrontAxle={fa[0]},{fa[1]},{fa[2]}\n"
        f"RearAxle={ra[0]},{ra[1]},{ra[2]}\n"
        f"WheelRadius={parts['wheel_radius']:.2f}\n"
        f"SteerPoint={sp[0]},{sp[1]},{sp[2]}\n"
        f"SteerAxis={steer_axis_worn[0]},{steer_axis_worn[1]},{steer_axis_worn[2]}\n"
        f"Grip={gr[0]},{gr[1]},{gr[2]}\n"
        f"FrontMinY={front_min_y:.1f}\n"
        f"BarAngle={args.bar_angle:g}\n"
        f"LampPoint={LAMP_LENS[0]},{LAMP_LENS[1]},{LAMP_LENS[2]}\n"
        "LampAxis=0,1,0\n"
        f"NeedlePoint={fmt_value(needle_keys['NeedlePoint'], 2)}\n"
        f"NeedleAxis={fmt_value(needle_keys['NeedleAxis'], 4)}\n"
        f"NeedleZero={fmt_value(needle_keys['NeedleZero'], 3)}\n"
        f"NeedleMax={fmt_value(needle_keys['NeedleMax'], 3)}\n"
        f"NeedlePerMph={fmt_value(needle_keys['NeedlePerMph'], 4)}\n")
    print(f"wrote {partsfile}: front axle {fa}, rear axle {ra}, radius {parts['wheel_radius']:.1f}, "
          f"steering axis through {sp} along {steer_axis_worn}, the +X grip at {gr} (the wrist roll's pivot), "
          f"the bar assembly's spheres beyond y {front_min_y:.1f}, the needle about {fmt_value(needle_keys['NeedleAxis'], 4)} "
          f"through {fmt_value(needle_keys['NeedlePoint'], 2)}")

    # The bike in first person (since the 2026-11-01a build): the game hides the player's third-person 3D in first person,
    # and the worn bike with it, so the plugin shows this copy there instead, placed every frame where the worn one
    # is (a script-placed MovableStatic, CMB_BikeView). The worn nif's shapes, the same vertices in the bike's own space
    # (full precision, as the parked nif's), materials and shadows, unskinned, named CMB_BikeView_<label> under one
    # NiNode, CMB_BikeView, that is hidden (flag bit 0): without the plugin a placed copy shows nothing. No collision.
    def view(path: Path):
        out = NifFile()
        out.initialize("FO4", str(path), "BSFadeNode", path.stem)
        identity = TransformBuf()
        identity.set_identity()
        node = out.add_node(VIEW_NODE, identity, out.rootNode)
        node.flags = node.flags | 1   # hidden
        for label, x in final.items():
            add_shape(out, f"{VIEW_NODE}_{label}", rows(turned(x["v"])), rows(x["f"]), rows(x["uv"]),
                      rows(to_worn_frame(x["n"])), base, base.use_type, shaders[label], False, True,
                      texture_paths(shaders[label], x["mat"], True, palette), material_name(label, True), parent=node)
        out.save()
        check = NifFile(str(path))
        blocks = [name for _, name in _block_offsets(path.read_bytes())]
        print(f"wrote {path}: {len(check.shapes)} shapes under the hidden node {VIEW_NODE}, "
              f"{'collision NOT expected: ' if any(b.startswith('bhk') for b in blocks) else 'no collision, '}"
              f"{len(blocks)} blocks")

    worn(args.out / "CMB_BikeWorn.nif", BIKE_BONE, None)
    if args.view:
        view(args.out / "CMB_BikeView.nif")
    else:
        (args.out / "CMB_BikeView.nif").unlink(missing_ok=True)
    if args.seat:
        male = read_seat(args.seat)
        if male is None:
            print(f"no CMB_RiderSeat.json in {args.seat}: run riding_anims.py first", file=sys.stderr)
            return 1
        made_for = json.loads((args.seat / "CMB_RiderSeat.json").read_text()).get("fit", "the vanilla motorcycle")
        if made_for != MODEL_NAME:
            print(f"WARNING: the clips in {args.seat} were fitted to {made_for}, not to this model: "
                  f"the rider's seat height differs. Rebuild them with riding_anims.py --fit "
                  f"{args.out / 'CMB_BikeFit.json'} and run this again.", file=sys.stderr)
        female = read_seat(args.seat / "Female") or male
        for (bone, bind), name in ((male, "CMB_BikeWornRider.nif"), (female, "CMB_BikeWornRiderF.nif")):
            worn(args.out / name, bone, bind)
    return 0


if __name__ == "__main__":
    sys.exit(main())
