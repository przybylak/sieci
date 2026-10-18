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
  Textures/CMB/CMB_Harley_d/_n/_s.dds   palette textures: each material is one block of a
                          128x8 strip (no mipmaps, so blocks never blend at a distance), and
                          every vertex's UV points at its material's block
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
                          the wrist node, 6.5 units from the grip, so the palm left the bar)

The geometry: each material's meshes are merged, welded and split into connected pieces, and
each piece is cut down with quadric edge collapse (fast_simplification) towards its share of
--tris by surface area (so the tyres keep their shape and a bolt gets a few triangles), the
simplifier's error capped so that no piece is crushed to reach its share: one that can't get
there within the cap keeps more, so the default 90000 comes out at about 225k triangles (tests
40 and 41, AGG_CAP, FINE_AGG; small pieces, the lenses, the painted panels and the small chrome
are kept whole, and only the specks under SPECK_AREA are dropped). Each corner's shading normal
is the glTF's own (at the closest point of its piece's surface where the piece was cut down),
a vertex split in two or more where its corners' normals part, so the model's hard edges stay
hard and its curves round (gltf_normals; the wheels' brake discs keep the averaged normals).
The parts go into shapes by shading: the metal (environment-mapped: chrome, silver, the body
colour), the matte (black metal, rubber, leather) and the glass (translucent); a few, not
twelve, because the F4SE plugin holds at most a dozen skins and the game shows at most 65535
vertices per shape. Colours, specular and gloss come from the material names (MATERIALS
below); the body colour is --body.

And by what moves (ROLES, role_of): the fixed bike; the bar assembly ("front": the bars,
grips, levers, mirrors, the fork tubes, the triple clamps and the headlamp, which the plugin
turns about the steering axis with the rider's steering); the fork's lower end ("fork": the
sliders, the front mudguard, the brake caliper, the axle and its hardware, which turn with the
bars and also ride up and down with the front wheel's suspension travel, so the mudguard
stays over the tyre and the axle in the fork ends); and the two wheels, which spin. The shapes
are named for it (<stem>_front_metal, <stem>_fork_matte, <stem>_wheelF, ...) and the plugin
tells them apart by their names and their culling spheres (CMB_BikeParts.ini).

  python harley_meshes.py --pynifly <io_scene_nifly> --gltf <...>/scene.gltf \
      --vanilla <...>/meshes/setdressing/vehicles/motorcycle/motorcycle_clean.nif \
      --out <Data>/Meshes/CMB --textures <Data>/Textures/CMB \
      [--seat <Data>/Meshes/Actors/Character/Animations/MT/CMB_Rider] [--tris 90000] [--body 7a1118]
      [--sit 0.27] [--grip 29.4,-10.7,96] [--peg 19,6,27]

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
about a quarter bigger than a real Iron 883 next to the character, like the vanilla bike.

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
PALETTE_W, PALETTE_H, BLOCK = 128, 8, 8   # 16 blocks of 8x8
CUBEMAP = "textures\\shared\\cubemaps\\mipblur_defaultoutside1.dds"

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
}
# Test 20: with the first palette (chrome 176 grey, specular 255, mask 255) the forks, exhausts
# and the headlight face rendered flat white in the sun, and the tan tank badge showed as a
# patch; so chrome is a mid grey with the reflection at 60%, the lens darker and duller, the
# badge satin black.

KINDS = ("metal", "matte", "glass", "glow")   # glow: lit (emissive), no reflection
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

# BSLightingShaderProperty flags (nif.xml's SkyrimShaderPropertyFlags, as Fallout 4 still uses them)
SF1_SPECULAR, SF1_SKINNED, SF1_ENV_MAP, SF1_RECEIVE_SHADOWS, SF1_CAST_SHADOWS = 0x1, 0x2, 0x80, 0x100, 0x200
SF1_ZBUFFER_TEST = 0x80000000
SF1_OWN_EMIT = 0x400000   # the shape glows by its emissive colour

# Our headlamp (the model's own, a plain can, sat still while the forks turned: its centre is
# 20 units behind the steering head, past role_of's 16): a 5.75" Harley LED unit, 15 across,
# on the fork bracket where the model's was, in the worn bike's space (+Y forward, Z up).
LAMP_X, LAMP_Z = 0.3, 81.9          # the lamp's axis
LAMP_FACE_Y, LAMP_R = 75.0, 7.5     # the lens sits here; the bucket runs 13 back from it
LAMP_LENS = (LAMP_X, LAMP_FACE_Y + 1.3, LAMP_Z)   # the lens's centre: where the light comes from
# The headlamp's light is a reference the controller script places at the lens (LampPoint in
# CMB_BikeParts.ini, kept there by the plugin); the lamp piece nifs of tests 32-35 (the light's
# add-on nodes in an unskinned armor addon of their own) never reached the player's 3D.
SF2_ZBUFFER_WRITE, SF2_DOUBLE_SIDED, SF2_ENVMAP_LIGHT_FADE = 0x1, 0x10, 0x8000
SHADER_DEFAULT, SHADER_ENV_MAP = 0, 1
ALPHA_BLEND_FLAGS = 4845   # blend src alpha / inv src alpha, test greater


# --- glTF --------------------------------------------------------------------------------

def load_gltf(path: Path, normals=None):
    """Each material's vertices and triangles, merged: {name: (V (n,3) float64, F (m,3) int64)}.
    With normals (a dict), each material's glTF normals at the corners of those triangles go
    into it too, (m, 3, 3): the weld makes one vertex of a hard edge's two, and the corners keep
    the export's own normals for gltf_normals() (the faces' own where a primitive has none)."""
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
    for m in d["meshes"]:
        for p in m["primitives"]:
            name = d["materials"][p["material"]]["name"]
            v = accessor(p["attributes"]["POSITION"]).astype(np.float64)
            f = accessor(p["indices"]).reshape(-1, 3).astype(np.int64)
            if "NORMAL" in p["attributes"]:
                n = np.nan_to_num(accessor(p["attributes"]["NORMAL"]).astype(np.float64))[f]
            else:
                n = np.repeat(unit(face_normals(v, f))[:, None, :], 3, axis=1)
            groups.setdefault(name, []).append((v, f, n))
    merged = {}
    for name, parts in groups.items():
        vs, fs, ns, off = [], [], [], 0
        for v, f, n in parts:
            vs.append(v)
            fs.append(f + off)
            ns.append(n)
            off += len(v)
        v, f, keep = weld(np.vstack(vs), np.vstack(fs))   # the parts of a material together: a tyre's halves share their seam
        merged[name] = (v, f)
        if normals is not None:
            normals[name] = np.vstack(ns)[keep]
    return merged


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


def decimate(groups, normals, total_target, speck_area=SPECK_AREA, small_area=SMALL_AREA, min_tris=8, weight=None, role=None):
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
    Returns (material, verts, tris, small, source) per piece: small if it's under small_area,
    source the piece as it was with its glTF corner normals (verts, tris, normals), for
    gltf_normals()."""
    import fast_simplification as fs
    pieces = []   # (material, verts, tris, area, corner normals)
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
            pieces.append((name, v[used], inv.reshape(-1, 3), float(piece_area[c]), normals[name][sel]))
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
    kept = held = over = painted = bright = fine = 0
    for (name, v, f, area, n0), b in zip(pieces, budget):
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
        result.append((name, v, f, area < small_area, (v0, f0, n0)))
    got = sum(len(r[2]) for r in result)
    print(f"  {len(pieces)} pieces kept ({sum(p[3] < small_area for p in pieces)} of them under {small_area:g} units²), "
          f"{dropped} specks dropped ({dropped_area:.0f} units² of {total_area:.0f}); budget {int(budget.sum())} triangles, "
          f"got {got}: {kept} pieces whole ({painted} painted, {bright} small chrome or silver), {held} held over their "
          f"share by the error cap ({over} triangles), {fine} cut finer than their material's cap (FINE_AGG)")
    per = {}
    for name, _, f, _, _ in result:
        per[name] = per.get(name, 0) + len(f)
    for name, (v, f) in groups.items():
        if name in per:
            print(f"  {name:12s} {len(f):8d} -> {per[name]:6d} tris")
    return result


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


def role_of(v, parts):
    """Which moving part a piece belongs to: a wheel (wheel_of), else the steering assembly
    if its centre is ahead of the steering head (forks, fender, headlight) or up at the bars
    (bars, grips, levers, mirrors), and of that the fork's lower end if its centre is below
    FORK_SPLIT_Z (sliders, mudguard, caliper, axle), else fixed."""
    wheel = wheel_of(v, parts)
    if wheel:
        return wheel
    cx, cy, cz = v.mean(axis=0)
    sp = parts["steer_point"]
    if cy < sp[1] + 16 and cz < FORK_SPLIT_Z:
        return "fork"
    # Up at bar height: within 45 of the steering head anything (the risers, the clamp, the
    # speedo, the mirrors that reach back over the tank), and out to 65 only what sits off the
    # centre line: the grips, levers, switch housings and the left mirror sit 45-57 behind the
    # head on this model (the bars sweep back), so with one line at 45 they stayed with the
    # frame while the bars turned (test 35: 590 vertices of bar end in the fixed shapes); but
    # the tank's chrome filler cap, on the centre line 55 behind the head, has its centre just
    # above BAR_HEIGHT too, and a plain 65 would have turned it with the bars.
    if cy < sp[1] + 16 or (cz > BAR_HEIGHT and (cy < sp[1] + 45 or (abs(cx) > 12 and cy < sp[1] + 65))):
        return "front"
    return ""


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


# --- textures ----------------------------------------------------------------------------

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
    """The three palette textures; returns each material's UV."""
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
    write_dds(folder / "CMB_Harley_d.dds", d)
    write_dds(folder / "CMB_Harley_n.dds", n)
    write_dds(folder / "CMB_Harley_s.dds", s)
    return uvs


# --- nif ---------------------------------------------------------------------------------

def shader_setup(shape, base_props, kind, skinned, textures, casts=True):
    """Our own textures and settings on the shape (no materials file, so the nif's count)."""
    props = base_props.copy()
    props.nameID = props.controllerID = -1
    sf1 = SF1_SPECULAR | SF1_RECEIVE_SHADOWS | SF1_ZBUFFER_TEST
    if casts:
        sf1 |= SF1_CAST_SHADOWS
    sf2 = SF2_ZBUFFER_WRITE
    if skinned:
        sf1 |= SF1_SKINNED
    props.Shader_Type = SHADER_DEFAULT
    props.Env_Map_Scale = 0.0
    if kind == "metal":
        props.Shader_Type = SHADER_ENV_MAP
        props.Env_Map_Scale = 1.0
        sf1 |= SF1_ENV_MAP
        sf2 |= SF2_ENVMAP_LIGHT_FADE
    sf2 |= SF2_DOUBLE_SIDED   # the model has single-plane bits (rim lips, fender undersides) that vanish from one side otherwise
    props.Shader_Flags_2 = sf2
    if kind == "glow":   # lit by itself: the headlamp's running light and projector face
        sf1 |= SF1_OWN_EMIT
        for i in range(4):
            props.Emissive_Color[i] = 1.0
    props.Shader_Flags_1 = sf1
    props.Glossiness = {"metal": 90.0, "matte": 30.0, "glass": 110.0, "glow": 30.0}[kind]
    props.Spec_Str = 1.0
    props.Spec_Color[0] = props.Spec_Color[1] = props.Spec_Color[2] = 1.0
    props.Alpha = 1.0
    props.Emissive_Mult = 6.0 if kind == "glow" else 1.0
    shape.shader.name = ""
    shape.shader._properties = props
    shape.save_shader_attributes()
    for slot, path in textures.items():
        shape.shader.set_texture(slot, path)   # the shader block exists now, so this writes to it
    if kind == "glass":
        shape.has_alpha_property = True
        shape.alpha_property.properties.flags = ALPHA_BLEND_FLAGS
        shape.alpha_property.properties.threshold = 0
        shape.save_alpha_property()


def texture_paths(kind):
    t = {"Diffuse": "textures\\CMB\\CMB_Harley_d.dds", "Normal": "textures\\CMB\\CMB_Harley_n.dds",
         "Specular": "textures\\CMB\\CMB_Harley_s.dds"}
    if kind == "metal":
        t["EnvMap"] = CUBEMAP
        t["EnvMask"] = "textures\\CMB\\CMB_Harley_s.dds"
    return t


def add_shape(nif, name, verts, tris, uvs, normals, base_props, use_type, kind, skinned, bone=None, bind=None, TransformBuf=None, casts=True):
    props = base_props.copy()
    props.nameID = props.controllerID = props.collisionID = -1
    props.skinInstanceID = props.shaderPropertyID = props.alphaPropertyID = -1
    if not skinned:
        # Test 40: the parked bike's positions in full precision. In half floats (the vanilla
        # shape's format) they sit on a 1/16-unit grid above 64 units, which flattened 1,083
        # small triangles to nothing (1,325 of test 40's mesh would be). The worn nifs keep
        # half floats until one is tried in game (PyNifly writes them, vertex format 0x45b).
        props.hasFullPrecision = 1
    new = nif.createShapeFromData(name, verts, tris, uvs, normals, props=props, use_type=use_type)
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
    shader_setup(new, base_props.shader_props, kind, skinned, texture_paths(kind), casts=casts)
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pynifly", type=Path, required=True, help="PyNifly's io_scene_nifly folder")
    ap.add_argument("--gltf", type=Path, required=True, help="the model's scene.gltf")
    ap.add_argument("--vanilla", type=Path, required=True, help="vanilla motorcycle_clean.nif (its collision is kept)")
    ap.add_argument("--out", type=Path, required=True, help="output folder, normally <Data>/Meshes/CMB")
    ap.add_argument("--textures", type=Path, required=True, help="normally <Data>/Textures/CMB")
    ap.add_argument("--seat", type=Path, help="the riding clips folder (MT\\CMB_Rider, with CMB_RiderSeat.json)")
    ap.add_argument("--tris", type=int, default=90000,
                    help="the triangle budget the pieces' shares are cut from (each piece's by its area is the "
                         "simplifier's target); the error cap stops the pieces that can't reach theirs without losing "
                         "their shape, so 90000 comes out at about 225k triangles")
    ap.add_argument("--body", default="7a1118", help="the tank and fenders' colour, hex rgb")
    ap.add_argument("--sit", type=float, default=0.27,
                    help="the hips go this far along the seat from its front edge (0..1); 0.27 is snug behind the "
                         "tank, where the arms, nearly straight on this bike, still reach the grips with the bars turned")
    ap.add_argument("--seat-at", type=float, help="instead of --sit: the parked model's y that goes under the hips")
    ap.add_argument("--grip", default="29.4,-10.7,96",
                    help="the grip's centre on the +X side, parked model x,y,z (the rubber sleeve's, see above)")
    ap.add_argument("--peg", default="19,6,27", help="the foot peg's top on the +X side, parked model x,y,z")
    ap.add_argument("--steer", help="the steering axis if it isn't found: x,y,z of a point on it (parked model) and the rake in degrees")
    ap.add_argument("--bar-angle", type=float, default=20.0, help="how far the bars turn, degrees (0: nothing moves)")
    args = ap.parse_args()
    grip = np.array([float(t) for t in args.grip.split(",")])
    peg = np.array([float(t) for t in args.peg.split(",")])

    sys.path.insert(0, str(args.pynifly))
    from pyn.pynifly import NifFile, TransformBuf  # noqa: E402

    body = tuple(int(args.body[i:i + 2], 16) for i in (0, 2, 4))
    print(f"loading {args.gltf}")
    corner_normals = {}
    groups = load_gltf(args.gltf, corner_normals)
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
    print(f"decimating: shares of {args.tris} triangles by area (the wheels' pieces at 2.5 times theirs), the error capped:")
    pieces = decimate(groups, corner_normals, args.tris, weight=lambda v: 2.5 if wheel_of(v, parts) else 1.0,
                      role=lambda v: role_of(v, parts))
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

    steer_axis_worn = [0.0, round(float(-parts["steer_axis"][1]), 4), round(float(parts["steer_axis"][2]), 4)]
    fit = dict(model=MODEL_NAME, seat_top_z=round(seat_top_z, 2),
               grip_r=to_worn([-abs(grip[0]), grip[1], grip[2]]), grip_l=to_worn([abs(grip[0]), grip[1], grip[2]]),
               peg_r=to_worn([-abs(peg[0]), peg[1], peg[2]]), peg_l=to_worn([abs(peg[0]), peg[1], peg[2]]),
               ground_foot_l=GROUND_FOOT_L, seat_at=round(seat_at, 2), hips_y=round(hips_y, 2),
               steer_point=to_worn(parts["steer_point"]), steer_axis=steer_axis_worn, bar_angle=args.bar_angle)
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

    order = [m for m in MATERIALS if m in groups or m in ("lamp_black", "lamp_led")]   # ours too: the headlamp's
    uv_of = write_palette(args.textures, order, body)
    print(f"wrote the palette textures to {args.textures}")

    # The shapes: by what moves (ROLES) and how it's shaded (KINDS); a wheel is one matte
    # shape whatever its pieces are made of (black rims, as on the real thing).
    roles = [role_of(v, parts) if args.bar_angle > 0 else "" for _, v, _, _, _ in pieces]
    # What a bolt is on: the ordinary piece with the source vertex nearest its centre. The
    # source's, not the cut-down piece's (test 41: a brake disc cut from 8,336 triangles to
    # 1,434 has few vertices left near its bolts, and the silver ring beside them won, so 9 of
    # the 10 disc bolts went into the fork's or the fixed shapes and stood still on the
    # spinning discs).
    ordinary = [i for i, p in enumerate(pieces) if not p[3]] or list(range(len(pieces)))
    ordinary_v = np.vstack([pieces[i][4][0] for i in ordinary])
    ordinary_of = np.concatenate([np.full(len(pieces[i][4][0]), i) for i in ordinary])
    specks = [i for i, p in enumerate(pieces) if p[3]] if args.bar_angle > 0 else []
    if specks:
        nearest = nearest_vertex(ordinary_v, np.array([pieces[i][1].mean(axis=0) for i in specks]))
        for i, at in zip(specks, nearest):   # a bolt spins with a wheel if what it's on does (SMALL_AREA)
            if roles[ordinary_of[at]].startswith("wheel"):
                roles[i] = roles[ordinary_of[at]]
    started = time.time()
    buckets = {}
    dropped = guarded = averaged = corners = 0
    for (name, v, f, small, source), role in zip(pieces, roles):
        if old_headlamp(v, seat_at):
            dropped += 1
            continue
        kind = "matte" if role.startswith("wheel") else MATERIALS[name][5]
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
        buckets.setdefault((role, kind), []).append((name, v, f, n))
    print(f"the glTF's normals on {len(pieces) - dropped - averaged} pieces, the averaged on the wheels' {averaged} silver ones; "
          f"{guarded} of {corners} corners took the averaged normal (sampled over {NORMAL_GUARD_DEG:g} degrees off their own "
          f"triangle, or none in the file) ({time.time() - started:.0f} s)")
    lamp = headlamp_pieces(seat_at, flip)
    for name, v, f in lamp:
        buckets.setdefault(("front" if args.bar_angle > 0 else "", MATERIALS[name][5]), []).append((name, v, f, None))
    print(f"the headlamp: {len(lamp)} pieces of our own on the fork bracket, turning with the bars; "
          f"{dropped} piece(s) of the model's own lamp dropped")
    shapes = {}   # name -> (verts, tris, uvs, normals, kind, role), in the order they're made
    for role in ROLES:
        for kind in KINDS:
            if (role, kind) not in buckets:
                continue
            vs, fs, us, ns, off = [], [], [], [], 0
            for name, v, f, n in buckets[(role, kind)]:
                if flip:
                    f = f[:, [0, 2, 1]]
                vs.append(v)
                fs.append(f + off)
                us.append(np.tile(np.array(uv_of[name]), (len(v), 1)))
                ns.append(n if n is not None else vertex_normals(v, f))   # our headlamp: its own
                off += len(v)
            v = np.vstack(vs)
            f = np.vstack(fs)
            label = role if role.startswith("wheel") else f"{role}_{kind}" if role else kind
            if len(v) > 65535:
                print(f"the {label} shape has {len(v)} vertices, over the 65535 a shape may have. Lower --tris if it was "
                      f"raised; but --tris only sets the pieces' shares, and the error caps (AGG_CAP, FINE_AGG) and the pieces "
                      f"kept whole (KEEP_TRIS, PAINTED, BRIGHT) set a floor it can't go below: past that, loosen the caps or "
                      f"keep fewer pieces whole", file=sys.stderr)
                return 1
            shapes[label] = (v, f, np.vstack(us), np.vstack(ns), kind, role)
            print(f"  {label}: {len(v)} vertices, {len(f)} triangles ({len(buckets[(role, kind)])} pieces)")

    base = Base(vshape)

    # Parked: the vanilla nif, its shape hidden, ours added.
    parked = args.out / "CMB_BikeParked.nif"
    parked.write_bytes(args.vanilla.read_bytes())
    nif = NifFile(str(parked))
    old = nif.shapes[0]
    old.flags = old.flags | 1   # hidden
    for label, (v, f, u, n, kind, _) in shapes.items():
        # Parked, nothing is lit: the lamp's lit parts are plain white there.
        add_shape(nif, f"CMB_Harley_{label}", rows(v), rows(f), rows(u), rows(n), base, base.use_type, "matte" if kind == "glow" else kind, False)
    nif.save()
    check = NifFile(str(parked))
    names = [s.name for s in check.shapes]
    hidden = [s.name for s in check.shapes if s.flags & 1]
    blocks = [name for _, name in _block_offsets(parked.read_bytes())]
    print(f"wrote {parked}: shapes {names}, hidden {hidden}, "
          f"collision {'kept' if any(b.startswith('bhk') for b in blocks) else 'NOT FOUND'} ({len(blocks)} blocks)")

    # Worn: turned round to face +Y like a character, the seat over the origin, on one bone.
    def turned(v):
        return np.column_stack([-v[:, 0], -v[:, 1] + seat_at, v[:, 2]])

    spheres = {label: sphere_of(turned(v)) for label, (v, *_) in shapes.items()}

    def worn(path: Path, bone, bind):
        out = NifFile()
        out.initialize("FO4", str(path), "NiNode", path.stem)
        allverts = []
        for label, (v, f, u, n, kind, role) in shapes.items():
            tv = turned(v)
            tn = np.column_stack([-n[:, 0], -n[:, 1], n[:, 2]])
            allverts.append(tv)
            # The bar assembly, the fork's lower end and the front wheel cast no shadow: the
            # bike's front end must not shadow the headlamp's beam (test 34). The worn bike's
            # only: the parked bike has no beam and keeps its sun shadow whole (test 35's
            # cleared them by name in every output).
            add_shape(out, f"{path.stem}_{label}", rows(tv), rows(f), rows(u), rows(tn), base, base.use_type, kind,
                      True, bone, bind, TransformBuf, casts=role not in ("front", "fork", "wheelF"))
        out.save()
        allverts = np.vstack(allverts)
        fix_all_bone_bounds(path, list(spheres.values()), rigid_inverse(bind) if bind else None)
        check = NifFile(str(path))
        lo, hi = allverts.min(axis=0), allverts.max(axis=0)
        node_names = []
        try:
            node_names = [n.name for n in check.nodes.values()] if isinstance(check.nodes, dict) else [n.name for n in check.nodes]
        except Exception as e:   # noqa: BLE001
            node_names = [f"(nodes unreadable: {e})"]
        print(f"wrote {path}: {len(check.shapes)} shapes on {bone}; nodes {node_names}")
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
    # across), so the palm swung off the bar as the forearm twisted.
    fa, ra, sp = to_worn(parts["front_axle"]), to_worn(parts["rear_axle"]), to_worn(parts["steer_point"])
    gr = fit["grip_r"]
    static_y = [c[1] for label, (c, _) in spheres.items() if not shapes[label][5]]
    front_y = [c[1] for label, (c, _) in spheres.items() if shapes[label][5] in ("front", "fork")]
    front_min_y = (max(static_y) + min(front_y)) / 2 if front_y else fa[1]
    partsfile = args.out / "CMB_BikeParts.ini"
    partsfile.write_text(
        "; Written by harley_meshes.py for CMB_Slope.dll: the worn bike's moving parts, in its mesh space\n"
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
        "LampAxis=0,1,0\n")
    print(f"wrote {partsfile}: front axle {fa}, rear axle {ra}, radius {parts['wheel_radius']:.1f}, "
          f"steering axis through {sp} along {steer_axis_worn}, the +X grip at {gr} (the wrist roll's pivot), "
          f"the bar assembly's spheres beyond y {front_min_y:.1f}")

    worn(args.out / "CMB_BikeWorn.nif", BIKE_BONE, None)
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
