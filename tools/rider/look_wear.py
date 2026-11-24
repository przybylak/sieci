#!/usr/bin/env python3
"""Build 2026-11-21a's (art build B, C3 items 3.5 and 3.6) wear art: the Wear slot's overlay maps and materials and the
muddy tyres. No bake and no picture: everything is drawn here from the shipped nifs and textures with our own noise.

The Wear slot (look_options.json's slot 12, the contract SP/t63/contract.md) shows one overlay at a time on two shells the
patcher adds to every bike nif: `static_wear` (a copy of `static_paint`'s vertex records lifted 0.32 along the averaged
normal, the same UVs) and `fork_wear` (of `fork_paint`). An option swaps the shells' invisible own files for its
materials; the overlay is alpha-blended over whatever paint is under it (Free colour too). Option 0, "As it came", is
the identity (the shells stay invisible): no file here. What it writes into --data (Textures\\CMB\\Bike,
Materials\\CMB\\Bike):

  wear_<key>_static_d.dds   1024 BC3: the overlay's colour (sRGB, times the factory paint's own baked occlusion, so the
                            shell is shaded as the paint under it) and its cover in alpha; the colour bled into the
                            texels no triangle covers (the gutters), so a mip or a filter at an island's edge never
                            pulls in black. wear_<key>_fork_d.dds the same at 512.
  wear_<key>_static_n.dds   512 BC5 (fork 256): the tangent-space normal (Direct3D green, as look_wheels.py's): the
                            shipped paint's own _n detail with the wear's relief over it (chips sunk, mud and blisters
                            raised, rust pitted).
  wear_<key>_static_s.dds   512 BC5 (fork 256): R specular, G smoothness of the wear (dust and rust matte, primer satin,
                            blood semi-gloss, wet mud a little sheen).
  wear_<key>_static.bgsm    and _worn, wear_<key>_fork.bgsm and _worn: the shipped static_paint / fork_paint materials
                            files with the three textures, alpha blend on (SrcAlpha, InvSrcAlpha), decal on (the depth
                            bias), no z write, one-sided, no shadows cast, no environment map, no palette.
  wheel<W>_tyre_mud_d.dds   (and _ww_mud_d, _rl_mud_d; W = F, R) 1024 BC1: the shipped tyre diffuse (black, whitewall,
                            red line) with our mud: the tread caked, the sidewalls splashed thinning toward the rim, mud
                            packed in the tread's grooves (the rubber's baked shading), the rubber's shading on the mud.
  wheel<W>_tyre_mud.bgsm    (and _ww_mud, _rl_mud, each with _worn): the shipped tyre files, the diffuse renamed; the
                            shipped _n and _s are shared.

The keys (the contract's options 1-7): weathered, dusty, muddy, rusty, bloody, wasteland (weathered + dust + mud) and
raider (rust + blood). Each option is a stack ("over") of the five layers drawn here:

  weathered  sun fade: a pale semi-transparent haze, heavier on what faces the sky and mottled; chips to the grey primer
             (bare steel in the bigger ones) at the convex edges, the knee areas (the tank's sides at the seat's front)
             and where the front wheel throws stones (the tank's front, the front fender's front); fine scratches,
             thickest round the knees and on the tank's top.
  dust       a pale khaki film on what faces up, thick in the creases (the occlusion's local dip) and the occluded
             corners, more low down (the road's dust), washed off in vertical streaks on the sides, wiped at the knees.
  mud        cast from the wheels: rays from each tyre's tread where a wheel rolling forward throws it (up and back
             behind the contact patch, forward over the top into the fender) and from the ground round the contact
             patches (from beside the tyre in and up onto the outsides, from under it onto the insides), each hit a
             droplet stretched along its travel by its incidence; the cake: the fenders' insides facing their tyre, their
             outsides by the gap to the tyre and the height (up to MUD_REACH over the axle, the rear fender's tail more),
             the tank's lower front, streaked in arcs about the axle (the spray's way); pale and matte where it dried
             thin, darker and a little glossy only where thick; a fine speckle where the spray thins out.
  rust       blooms from the convex edges (paint blistered round them), rings round the tank badges, the rear badge,
             the fender patch and the plate, the tank's underside, a little inside the fenders, streaks running down from
             the blooms.
  blood      spatter from four sources (a hit at the front left, a burst at the right side, a fall from above the rear, a
             splash from behind on the right): droplets cast as rays, stretched by their incidence with a tail pointing
             away from the source and satellite drops ahead of the long ones; three hand smears (streaky along the
             stroke, thinning toward its end); drips running down from the big drops on the steep faces.

Every layer stays off the paint under the tank plates and the rear roundel (PLATE_CLEAR: they sit 0.03-0.5 over the
paint, so the 0.32 shell runs partly over and partly under them, and wear there would stop along a line across the
emblem); the paint the shell leaves out (inside the frame, under the seat) is drawn but never seen.

Every feature is in the parked nif's frame (+z up, -y forward), from the parked nif's paint shapes rasterised into UV at
twice the map's size (WORK) for each texel's position, normal, convexity (per welded vertex: the paint shapes are closed
sheets, their edges rolled lips), island and size; the noise is bike_art.py's 3D value noise and fbm, so a feature runs on
across a UV seam; the occlusion is the factory diffuse's luminance over its part's colour (the coachline's texels told by
the shipped index map). Nothing is traced or sampled from a picture; the shipped files read are the nifs, the factory
paint's _d (occlusion only) and _n (detail), its index map (which texels are the coachline) and the tyres' _d (their base).

--check (after a build, or alone on a built tree): every file's format, size and full mip chain; every materials file's
values (the template's but the textures and the overlay's flags) and every texture it names present; each option's cover
per region (tank top, sides, underside, lower front, knees, rear fender outside and inside, the front fender's, round the
badges and the plate) against the option's own expectations; each combination at least each of its parts on every texel;
the muddy tyres' mud by radius (the tread over the inner sidewall) and on the bands; no wear over the tank plates and the
roundel; the five nifs' paint UVs the parked one's (one overlay serves every bike); the total size; nothing else in the
tree.

    <python with numpy, Pillow, quicktex, texture2ddecoder> -I tools/rider/look_wear.py --data <out Data> \\
        --base <2026-11-10a's Data> [--base <later Data> ...] --pynifly <io_scene_nifly> [--only key,...] [--check]

--base: the asset base, read only, later folders over earlier ones (the package's Data, then a build's meshes over it).
Nothing from the files read is executed.

Since 2026-11-22a (build C5; test 58's wishes, the contract SP/t64/contract.md sections 1-3):

  Paint condition    (slot 15) paintwear_<key>_static_d/_n/_s (1024 BC3, 512 BC5) and paintwear_<key>_fork (512, 256),
                     materials paintwear_<key>_static/_fork(_worn).bgsm on the paintwear shells (0.16 over the paint,
                     under the Wear's 0.32), keys scratched, chipped, faded, worn (the three stacked) and primer: the
                     paint's own damage only (scratches through the clear coat, deep ones to primer and steel, scuffs
                     where things rub; flaked and stone chips; sun fade with the clear coat peeling on the tops; repair
                     patches of grey filler and red-oxide primer with feathered edges and a sanded halo), never grime;
                     where its shell lies over a tank plate or the roundel (the plate under PC_SHELL over the paint: the
                     plates' ends) only the sun haze (a clean patch there would show through the plate's clear parts);
                     elsewhere under a plate the shell runs below it and the paint condition shows through the badge's
                     clear parts. New files: no flag.
  the Wear on parts  wear_<key>_<part>_d/_n/_s (512 BC3, 256 BC5) and wear_<key>_<part>(_worn).bgsm for the shells
                     unit's part shells (PARTS: static_exhaust, static_engine, fork_black), each in its source shape's
                     own UV space, its colour times that shape's own baked occlusion (its diffuse's luminance over its
                     bright level): heat colouring on the pipes from each port and a dulled haze (Weathered), rust heavy
                     on the mufflers' bottoms, seams and clamps, white corrosion on the engine's covers (Rusty), mud
                     caked low down by the wheels and the road (Muddy), dust at PART_DUST of the paint's, blood where the
                     rays reach (the paint and the parts cast together; the paint's own droplets keep the paint-only
                     cast). New files: no flag.
  --badge-grime      2026-11-22a (the default): the grime goes over the tank plates and the rear roundel (the shells
                     unit lifts static_wear over them): dust caught along a plate's top edge, mud and blood as they fall,
                     rust bleeding from under its bottom edge with streaks below (a plate is a clear rectangle round its
                     badge's art: a ring all round showed as a frame); Weathered keeps only its sun haze there (a
                     badge fades with the paint but takes no chip or scratch).
                     2026-11-21a: every layer off them, 2026-11-21a's 42 wear maps byte for byte.
  --overlay-depth    2026-11-22a (the default): every overlay's material writes depth and alpha-tests at OVERLAY_TEST
                     besides the blend (two blended shells over the paint share their bounds, so the game can't sort
                     them: a grime texel then hides the paint condition under it whichever is drawn first);
                     2026-11-21a: no z write, no test (2026-11-21a's 28 wear materials byte for byte).
  --tyre-mud         2026-11-22a (the default; test 58: "the tire part where it touches ground is too muddy"): the
                     tread's faces that meet the road clean (a few specks), mud packed in the grooves and on the blocks'
                     walls, clods on the shoulders, the sidewalls as 2026-11-21a's; 2026-11-21a: the tread caked, the six
                     tyre diffuses byte for byte.
  Every old value with 2026-11-21a's asset base (the nifs of assets16a/a) rebuilds 2026-11-21a's 88 files byte for byte.
  On the 2026-11-22a base the parked nif comes from 2026-11-21a's shells unit, whose rear fender patch sits 0.16 higher:
  Rusty's and Raider's static maps then differ near that patch (their rust ring is measured to it), nothing else.
  --check holds the tree to the flags given and grows: the budget per group (BUDGETS), Paint condition's cover per
  region and off the plates, Worn at least each of its parts, the grime over the plates (a rust ring, dust at the edges,
  Weathered off), the parts (mud low down, dust, rust and weathering on each, the pipes' heat colour by their ports, the
  mixes at least their parts), the tread's faces clean and its grooves muddy.

Since 2026-11-23a (test 59: "rust is too much, should be less intense, more transparent and in darker colors on edges";
the rust round the Brotherhood plate and dripping off its lower edge read as "a rectangle around the frame"):

  --rust             2026-11-23a (the default): Rusty's rust (Raider's too, which stacks it) lighter on the paint and the
                     parts (layer_rust_light, part_rust_light): fewer, smaller blooms from the same places (the edges,
                     under the tank, inside the fenders, by the number plate, the mufflers' bottoms) and some in random
                     clumps, each see-through in its middle (the paint shows through a brown stain) and darker and denser
                     at its edge (a band about RUST_RIM_W wide), browner (no bright orange), fainter and fewer streaks;
                     nothing along a plate's outline (22a's band round the badges, the ring along a plate's bottom edge
                     and its drips gone): two or three blooms by each tank plate and the roundel at random places on its
                     outline (plate_blooms), and over a plate's face the rust as on the paint round it.
                     2026-11-22a: 2026-11-22a's rust; with every other flag at its default the 2026-11-22a 243 files
                     byte for byte (the 30 Rusty and Raider maps are the ones that change).
  --check with --rust 2026-11-23a: no look draws a plate's outline (per plate, the share of its outline band with grime
  over 0.3 at most OUTLINE_SHARE or OUTLINE_FACTOR x the share round it), Rusty lighter (hardly a texel near opaque, the
  blooms' middles see-through, their edges darker than their middles), Rusty's cover expectations EXPECT_RUST_NEW (22a's
  "more round the badges" gone), a part's rust at least 0.012 (0.03 with the old rust).
"""
import argparse
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bgsm as B  # noqa: E402
import look_paint as LP  # noqa: E402
import write_dds as W  # noqa: E402
from bike_art import noise3 as _noise3, fbm as _fbm  # noqa: E402
from look_wheels import raster, uv_islands  # noqa: E402
from nearest import closest_on_triangles  # noqa: E402

TEX = "CMB\\Bike\\"
KEYS = ("weathered", "dusty", "muddy", "rusty", "bloody", "wasteland", "raider")
NAMES = {"weathered": "Weathered", "dusty": "Dusty", "muddy": "Muddy", "rusty": "Rusty", "bloody": "Bloody",
         "wasteland": "Wasteland", "raider": "Raider"}
STACKS = {"weathered": ("weathered",), "dusty": ("dust",), "muddy": ("mud",), "rusty": ("rust",), "bloody": ("blood",),
          "wasteland": ("weathered", "dust", "mud"), "raider": ("rust", "blood")}
SHAPES = {"static": dict(label="static_paint", size=1024, aux=512), "fork": dict(label="fork_paint", size=512, aux=256)}
WORK = 2                      # the working grid: the map's size times this (the factory _d and _n are at that size)
TYRE_SIZE = 1024
TYRES = (("", "_mud"), ("_ww", "_ww_mud"), ("_rl", "_rl_mud"))   # the shipped diffuse's suffix -> the muddy one's
NIFS = ("CMB_BikeParked", "CMB_BikeWorn", "CMB_BikeWornRider", "CMB_BikeWornRiderF", "CMB_BikeView")
FACTORY_BODY, FACTORY_COACH = "7a1118", "c8a860"      # 2026-11-06a's paint (look_paint.FACTORY)
COACH_U = 212                                         # the index map's coachline band starts at 216 (look_paint)
MUD_REACH = {"F": (38.0, 12.0), "R": (46.0, 14.0)}  # the mud on a fender's outside: up to the axle's height + this; the
                                                    # gap from the tyre it falls off over (units)
PC_SHELL = 0.16                                       # the paintwear shell's lift: Paint condition off a plate under it
PLATE_CLEAR = 0.62                                    # wear kept off paint this near a tank plate or the roundel
SCRATCHES = {"static": 1400, "fork": 260}            # fine scratches a shape
KNEE_AHEAD, KNEE_UP, KNEE_R = 8.0, 9.0, (8.0, 6.0)   # the knees: ahead of the seat's front, over its low part; radii
# (since 2026-11-22a) the Paint condition slot (slot 15, the contract SP/t64/contract.md): options 1-5 on the paintwear
# shells, the paint's own damage only (the Wear slot keeps the grime over it)
PC_KEYS = ("scratched", "chipped", "faded", "worn", "primer")
PC_NAMES = {"scratched": "Scratched", "chipped": "Chipped", "faded": "Sun-faded", "worn": "Worn",
            "primer": "Primer patches"}
PC_STACKS = {"scratched": ("pc_scratch",), "chipped": ("pc_chip",), "faded": ("pc_fade",),
             "worn": ("pc_fade", "pc_scratch", "pc_chip"), "primer": ("pc_primer",)}
PC_SCRATCHES = {"static": 3200, "fork": 650}          # Scratched: scratches a shape
PC_PATCHES = {"static": 9, "fork": 3}                 # Primer patches: patches a shape
CLEARCOAT = "e6e1d6"     # the clear coat lifting and peeling: paler, chalky
FILLER, FILLER_DARK, RED_OXIDE = "8d8b85", "6f6d68", "7a3a26"   # grey filler primer, its sanded darker grain, red oxide
# (since 2026-11-22a) the Wear on more parts: the shells unit's part shells (SP/t64/units/shells/notes.md section 0), each
# drawn in its source shape's own UV space; maps wear_<key>_<part>_d (BC3) and _n/_s (BC5) at these sizes
PARTS = {"static_exhaust": dict(label="static_exhaust", size=512, aux=256, wheels=("R", "F")),
         "static_engine": dict(label="static_engine", size=512, aux=256, wheels=("F",)),
         "fork_black": dict(label="fork_black", size=512, aux=256, wheels=("F",))}
HEAT = ("3c4f7e", "6a4a78", "b8913f", "cdb98a")       # a hot pipe's colours from the port: blue, purple, gold, straw
DULL = "b4b0a6"                                       # a dulled, oxidised metal haze
ALU_OXIDE = "cfcdc4"                                  # white corrosion on the engine's covers
DEPTH_OLD, DEPTH_NEW = "2026-11-21a", "2026-11-22a"   # --overlay-depth: no z write (21a); z write + alpha test (22a)
OVERLAY_TEST = 8                                      # 22a: the overlays' alpha test reference (with the blend)
GRIME_OLD, GRIME_NEW = "2026-11-21a", "2026-11-22a"   # --badge-grime: the plates clear (21a), or under the grime (22a)
TREAD_OLD, TREAD_NEW = "2026-11-21a", "2026-11-22a"   # --tyre-mud: the tread caked (21a), or clean faces (22a)
RUST_OLD, RUST_NEW = "2026-11-22a", "2026-11-23a"    # --rust: 22a's rust (opaque, round the plates), or lighter (23a)
BUDGET_WEAR, BUDGET_ALL = 20.0e6, 24.0e6              # bytes: the wear maps, and with the muddy tyres

# colours (sRGB hex), our own palette
HAZE = "dcd6ca"          # sun-faded, chalky
PRIMER = "7d7b74"        # grey primer under the chips
STEEL = "5c5d5e"         # bare steel in a deep chip
SCRATCH = "c9c5bd"
DUST, DUST_DARK = "bcab8b", "988769"
MUD_WET, MUD_MID, MUD_DRY = "3a2e22", "5b4935", "8d7a5b"
RUST_DARK, RUST, RUST_LIGHT, RUST_STAIN = "3b1f13", "8a461c", "b2702f", "6e3c1f"
# (since 2026-11-23a, --rust) the lighter rust: a bloom's dark edge, its see-through body (two browns), the faint wash
# round it
RUST_RIM, RUST_BODY, RUST_PALE, RUST_WASH = "2a150b", "7a3e1c", "8e5229", "5a3820"
RUST_RIM_W = 0.4                                      # (since 2026-11-23a) a bloom's dark edge: about this wide (units)
BLOOD_THICK, BLOOD, BLOOD_THIN = "330404", "6a0c0a", "8a2a1a"
TYRE_MUD_WET, TYRE_MUD_DRY = "3e3226", "6e5c44"


# --- small helpers -------------------------------------------------------------------------------------------------

def hexlin(h):
    return LP.hexlin(h)


def ss(a, b, x):
    """smoothstep from a to b (a > b runs downhill)."""
    t = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def soft(x, w):
    """A soft step at 0 of width w (antialiased threshold)."""
    return np.clip(np.asarray(x, np.float64) / w + 0.5, 0.0, 1.0)


def _off(seed):
    return np.array([seed * 37.17 + 3.1, seed * -19.73 + 7.7, seed * 11.31 - 5.3])


def noise(P, scale, seed):
    """bike_art.py's 3D value noise (0..1) at points P (n, 3), features about `scale` units."""
    return _noise3(P / scale + _off(seed))


def fbm(P, scale, seed, octaves=4):
    """bike_art.py's fbm (about 0.1..0.9, mean 0.5), features about `scale` units."""
    return _fbm(P / scale + _off(seed), octaves)


def aniso(P, d, along, across, seed):
    """Value noise stretched along the direction d: features `along` units along it, `across` across."""
    d = np.asarray(d, np.float64)
    d = d / np.linalg.norm(d)
    e1 = np.cross(d, [0.0, 0.0, 1.0] if abs(d[2]) < 0.9 else [1.0, 0.0, 0.0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(d, e1)
    q = np.stack([P @ d / along, P @ e1 / across, P @ e2 / across], -1)
    return _noise3(q + _off(seed))


def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)


def find(bases, rel):
    """A file under the asset base (the last --base that has it), else None."""
    for b in reversed(bases):
        p = b / rel
        if p.exists():
            return p
    return None


def need(bases, rel):
    p = find(bases, rel)
    if p is None:
        raise SystemExit(f"--base: no {rel}")
    return p


# --- the shapes ----------------------------------------------------------------------------------------------------

def load_shapes(pynifly, nif, labels):
    """{label: dict(v, n, uv, tri)} of the nif's shapes whose names end with _<label> (positions as stored)."""
    sys.path.insert(0, str(pynifly))
    from pyn import pynifly as P
    f = P.NifFile(str(nif))
    out = {}
    for s in f.shapes:
        for lab in labels:
            if s.name.lower().endswith("_" + lab.lower()):
                out[lab] = dict(v=np.asarray(s.verts, np.float64), n=np.asarray(s.normals, np.float64),
                                uv=np.asarray(s.uvs, np.float64), tri=np.asarray(s.tris, np.int64), name=s.name)
    missing = [lab for lab in labels if lab not in out]
    if missing:
        raise SystemExit(f"{nif.name}: no shape {', '.join(missing)}")
    return out


def load_shapes_opt(pynifly, nif, labels):
    """load_shapes for the shapes that are there: {label: shape}."""
    sys.path.insert(0, str(pynifly))
    from pyn import pynifly as P
    f = P.NifFile(str(nif))
    out = {}
    for s in f.shapes:
        for lab in labels:
            if s.name.lower().endswith("_" + lab.lower()):
                out[lab] = dict(v=np.asarray(s.verts, np.float64), uv=np.asarray(s.uvs, np.float64),
                                tri=np.asarray(s.tris, np.int64), name=s.name)
    return out


def welded(v, tri):
    """(welded index per vertex, welded positions, welded triangles, unique edges)."""
    _, inv = np.unique(np.round(v, 3), axis=0, return_inverse=True)
    inv = inv.ravel()
    pw = np.zeros((inv.max() + 1, 3))
    pw[inv] = v
    T = inv[tri]
    e = np.sort(np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), axis=1)
    return inv, pw, T, np.unique(e, axis=0)


def convexity(v, tri, smooth=0):
    """Per vertex: the mean-curvature estimate at its welded position (1 / radius; > 0 convex: a sphere of radius r gives
    1/r), from the edges round it against the area-weighted normal; then `smooth` rounds of neighbour averaging."""
    inv, pw, T, ek = welded(v, tri)
    fn = np.cross(pw[T[:, 1]] - pw[T[:, 0]], pw[T[:, 2]] - pw[T[:, 0]])
    vn = np.zeros_like(pw)
    for k in range(3):
        np.add.at(vn, T[:, k], fn)
    vn = unit(vn)
    d = pw[ek[:, 1]] - pw[ek[:, 0]]
    dd = np.maximum((d * d).sum(1), 1e-12)
    ks, kc = np.zeros(len(pw)), np.zeros(len(pw))
    np.add.at(ks, ek[:, 0], -2.0 * (vn[ek[:, 0]] * d).sum(1) / dd)
    np.add.at(ks, ek[:, 1], 2.0 * (vn[ek[:, 1]] * d).sum(1) / dd)
    np.add.at(kc, ek[:, 0], 1)
    np.add.at(kc, ek[:, 1], 1)
    kap = ks / np.maximum(kc, 1)
    for _ in range(smooth):
        acc, cnt = kap.copy(), np.ones(len(pw))
        np.add.at(acc, ek[:, 0], kap[ek[:, 1]])
        np.add.at(acc, ek[:, 1], kap[ek[:, 0]])
        np.add.at(cnt, ek[:, 0], 1)
        np.add.at(cnt, ek[:, 1], 1)
        kap = acc / cnt
    return kap[inv]


class Grid:
    """A paint shape rasterised into its UV at `size` (WORK x the map): the covered texels as flat arrays (index into
    the size x size image, triangle, barycentric weights, position, normal, convexity, island, texel size in units)."""

    def __init__(self, shp, size):
        self.size = size
        v, n, uv, tri = shp["v"], shp["n"], shp["uv"], shp["tri"]
        tid, bary = raster(uv[tri], size, size)
        self.cov = tid >= 0
        self.idx = np.flatnonzero(self.cov)
        t = tid.ravel()[self.idx].astype(np.int64)
        b = bary.reshape(-1, 2)[self.idx].astype(np.float64)
        w = np.stack([1.0 - b[:, 0] - b[:, 1], b[:, 0], b[:, 1]], -1)
        self.tri, self.w = t, w
        corners = tri[t]
        self.P = np.einsum("nk,nkc->nc", w, v[corners])
        self.N = unit(np.einsum("nk,nkc->nc", w, n[corners]))
        self.kap = np.einsum("nk,nk->n", w, convexity(v, tri, 0)[corners])
        self.kap_s = np.einsum("nk,nk->n", w, convexity(v, tri, 6)[corners])
        isl = uv_islands(tri, uv[tri], np.arange(len(tri)))
        root = np.array([isl[i] for i in range(len(tri))])
        self.island = root[t]
        a3 = 0.5 * np.linalg.norm(np.cross(v[tri[:, 1]] - v[tri[:, 0]], v[tri[:, 2]] - v[tri[:, 0]]), axis=1)
        u = uv[tri] * size
        e1, e2 = u[:, 1] - u[:, 0], u[:, 2] - u[:, 0]
        a2 = 0.5 * np.abs(e1[:, 0] * e2[:, 1] - e2[:, 0] * e1[:, 1])
        self.texel = np.sqrt(a3 / np.maximum(a2, 1e-9))[t]          # units per texel of this grid
        self.n = len(self.idx)

    def image(self, vals, fill=0.0):
        """Flat per-texel values (n[, c]) into a size x size image (the rest `fill`)."""
        vals = np.asarray(vals)
        img = np.full((self.size * self.size,) + vals.shape[1:], fill, vals.dtype if vals.dtype != bool else np.float64)
        img[self.idx] = vals
        return img.reshape((self.size, self.size) + vals.shape[1:])

    def flat(self, img):
        return img.reshape((self.size * self.size,) + img.shape[2:])[self.idx]

    def blur(self, vals, radius):
        """A coverage-normalised blur of per-texel values (two box passes of `radius` texels a side)."""
        img, cov = self.image(vals.astype(np.float64)), self.cov.astype(np.float64)
        for _ in range(2):
            img, cov = _box(img, radius), _box(cov, radius)
        return self.flat(img / np.maximum(cov, 1e-9))


def _box(img, r):
    """Separable box filter of half-width r with zero padding."""
    out = img
    for ax in (0, 1):
        c = np.cumsum(np.pad(out, [(r + 1, r) if a == ax else (0, 0) for a in range(out.ndim)]), axis=ax)
        hi = np.take(c, np.arange(2 * r + 1, c.shape[ax]), axis=ax)
        lo = np.take(c, np.arange(0, c.shape[ax] - 2 * r - 1), axis=ax)
        out = (hi - lo) / (2 * r + 1)
    return out


class Splat:
    """The covered texels hashed into 3D cells, to draw a primitive (a droplet, a run) on every texel near a point."""

    def __init__(self, g, cell=1.0):
        self.g, self.cell = g, cell
        k = np.floor(g.P / cell).astype(np.int64)
        self.lo = k.min(0)
        k -= self.lo
        self.dim = k.max(0) + 1
        key = (k[:, 2] * self.dim[1] + k[:, 1]) * self.dim[0] + k[:, 0]
        self.order = np.argsort(key, kind="stable")
        self.keys = key[self.order]

    def near(self, c, r):
        """The texels in the cells a sphere of radius r round c touches."""
        a = np.floor((np.asarray(c) - r) / self.cell).astype(np.int64) - self.lo
        b = np.floor((np.asarray(c) + r) / self.cell).astype(np.int64) - self.lo
        a, b = np.maximum(a, 0), np.minimum(b, self.dim - 1)
        if (a > b).any():
            return np.zeros(0, np.int64)
        out = []
        for z in range(a[2], b[2] + 1):
            for y in range(a[1], b[1] + 1):
                k0 = (z * self.dim[1] + y) * self.dim[0]
                i0 = np.searchsorted(self.keys, k0 + a[0], "left")
                i1 = np.searchsorted(self.keys, k0 + b[0], "right")
                if i1 > i0:
                    out.append(self.order[i0:i1])
        return np.concatenate(out) if out else np.zeros(0, np.int64)


def raycast(o, d, V, T, reach=160.0, chunk=64):
    """Nearest hits within `reach` of rays (o, d: (k, 3)) on triangles (V[T]): (t, triangle, hit point, triangle normal)
    with t = inf and triangle -1 for a miss. Moller-Trumbore, both faces; the rays taken in coherent bunches (sorted by
    origin and direction), each bunch against the triangles whose boxes meet the bunch's swept box."""
    A, Bv, C = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    e1, e2 = Bv - A, C - A
    fn = unit(np.cross(e1, e2))
    tlo, thi = np.minimum(np.minimum(A, Bv), C), np.maximum(np.maximum(A, Bv), C)
    k = len(o)
    az = np.round(np.degrees(np.arctan2(d[:, 1], d[:, 0])) / 4.0)
    el = np.round(np.degrees(np.arcsin(np.clip(d[:, 2], -1, 1))) / 4.0)
    q = np.round(o / 4.0)
    order = np.lexsort((el, az, q[:, 2], q[:, 1], q[:, 0]))
    best_t = np.full(k, np.inf)
    best_i = np.full(k, -1, np.int64)
    for s in range(0, k, chunk):
        r = order[s:s + chunk]
        ends = o[r] + d[r] * reach
        lo = np.minimum(o[r], ends).min(0) - 1e-3
        hi = np.maximum(o[r], ends).max(0) + 1e-3
        sel = np.flatnonzero(np.all((thi >= lo) & (tlo <= hi), axis=1))
        if not len(sel):
            continue
        oo, dd = o[r, None, :], d[r, None, :]
        a_, f1, f2 = A[sel][None], e1[sel][None], e2[sel][None]
        p = np.cross(dd, f2)
        det = (f1 * p).sum(-1)
        ok = np.abs(det) > 1e-12
        inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
        tv = oo - a_
        u = (tv * p).sum(-1) * inv
        qv = np.cross(tv, f1)
        v = (dd * qv).sum(-1) * inv
        t = (f2 * qv).sum(-1) * inv
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-3) & (t <= reach)
        t = np.where(hit, t, np.inf)
        j = t.argmin(1)
        tj = t[np.arange(len(j)), j]
        best_t[r] = tj
        best_i[r] = np.where(np.isfinite(tj), sel[j], -1)
    hitp = o + d * np.where(np.isfinite(best_t), best_t, 0.0)[:, None]
    return best_t, best_i, hitp, fn[np.clip(best_i, 0, None)]


# --- the scene: both paint shapes and the parts round them --------------------------------------------------------

class Scene:
    """The parked nif's measurements the layers use: the wheels, the seat's front, the knees, the badges and the plate,
    and both paint shapes as triangles (for the rays)."""

    def __init__(self, pynifly, nif):
        labs = ("static_paint", "fork_paint", "wheelF_tyre", "wheelR_tyre", "static_seat", "static_plate",
                "static_badgeTankL", "static_badgeTankR", "static_badgeRear", "static_badgeFender") + tuple(PARTS)
        sh = load_shapes(pynifly, nif, labs)
        self.shapes = sh
        self.wheels = {}
        for w in "FR":
            v = sh[f"wheel{w}_tyre"]["v"]
            c = (v.min(0) + v.max(0)) / 2.0
            r = np.hypot(v[:, 1] - c[1], v[:, 2] - c[2]).max()
            tr = v[np.hypot(v[:, 1] - c[1], v[:, 2] - c[2]) > r - 2.0]          # the tread: the tyre's width
            half = float(np.abs(tr[:, 0] - c[0]).max())
            self.wheels[w] = dict(c=c, r=float(r), half=float(half))
        seat = sh["static_seat"]["v"]
        self.seat_front = float(seat[:, 1].min())
        self.badge_sets = [sh[k]["v"] for k in ("static_badgeTankL", "static_badgeTankR", "static_badgeRear",
                                                "static_badgeFender")]
        self.plate = sh["static_plate"]["v"]
        self.plates = [(sh[k]["v"], sh[k]["tri"]) for k in ("static_badgeTankL", "static_badgeTankR", "static_badgeRear")]
        self.plate_rims = [plate_rim(v, tri) for v, tri in self.plates]
        # the knees: the tank's sides just ahead of the seat, at the seat's height
        tv, tn = sh["static_paint"]["v"], sh["static_paint"]["n"]
        zseat = float(np.percentile(seat[:, 2], 30))
        want = np.array([self.seat_front - KNEE_AHEAD, zseat + KNEE_UP])
        self.knees = []
        for sx in (1.0, -1.0):         # the tank's outer side face nearest the knee's (y, z): its point on the surface
            ok = (tv[:, 1] < self.seat_front) & (tv[:, 0] * sx > 8.0) & (tn[:, 0] * sx > 0.5)
            i = np.flatnonzero(ok)[np.argmin(((tv[ok][:, 1:] - want) ** 2).sum(1))]
            self.knees.append((tv[i].copy(), unit(tn[i])))
        # every paint triangle, for the rays
        V, T, off = [], [], 0
        for lab in ("static_paint", "fork_paint"):
            V.append(sh[lab]["v"])
            T.append(sh[lab]["tri"] + off)
            off += len(sh[lab]["v"])
        self.V, self.T = np.concatenate(V), np.concatenate(T)
        # (since 2026-11-22a) the paint and the parts together, for the parts' droplets: [(key, first triangle)]; the
        # paint's own droplets keep 2026-11-21a's paint-only cast
        Vp, Tp, self.part_ranges, off, nt = [self.V], [self.T], [], len(self.V), len(self.T)
        for lab in PARTS:
            Vp.append(sh[lab]["v"])
            Tp.append(sh[lab]["tri"] + off)
            self.part_ranges.append((lab, nt))
            off += len(sh[lab]["v"])
            nt += len(sh[lab]["tri"])
        self.Vp, self.Tp = np.concatenate(Vp), np.concatenate(Tp)
        # (since 2026-11-22a) each part shell as the nif has it (the shells unit's: the source's vertex records, only the
        # triangles it kept), when it is there: the part art is drawn only where it lies
        self.part_shells = load_shapes_opt(pynifly, nif, tuple(f"{lab}_wear" for lab in PARTS))

    def report(self):
        F, R = self.wheels["F"], self.wheels["R"]
        return (f"wheels F {F['c'].round(2).tolist()} r {F['r']:.2f}, R {R['c'].round(2).tolist()} r {R['r']:.2f}; seat front "
                f"y {self.seat_front:.1f}; knees {[k.round(1).tolist() for k, _ in self.knees]}")


def knee_weight(sc, P, N):
    """The knees' grip: 1 at each knee's point on the tank's side, an ellipse KNEE_R (along, up) round it, on the faces
    that look the knee's way."""
    kn = np.zeros(len(P))
    for k, kn_n in sc.knees:
        d = P - k
        q = (d[:, 1] / KNEE_R[0]) ** 2 + (d[:, 2] / KNEE_R[1]) ** 2 + (d[:, 0] / KNEE_R[1]) ** 2
        kn = np.maximum(kn, np.exp(-2.0 * q) * ss(0.2, 0.6, N @ kn_n))
    return kn


class Ctx:
    """One paint shape's working grid with its features (flat over the covered texels)."""

    def __init__(self, sc, key, shp, bases, shade_img, nrm_img, coach_img):
        meta = SHAPES[key]
        self.key, self.meta, self.sc = key, meta, sc
        self.g = g = Grid(shp, meta["size"] * WORK)
        P, N = g.P, g.N
        self.shade = np.clip(g.flat(shade_img), 0.05, 1.05)
        self.coach = g.flat(coach_img) > 0.5
        self.kap, self.kap_s = g.kap, g.kap_s
        self.pn = g.flat(nrm_img)                     # the paint's own tangent-space normal (x, y, z)
        self.up = N[:, 2]
        self.tank = (P[:, 1] < sc.seat_front + 3.0) if key == "static" else np.zeros(g.n, bool)
        self.rear = ~self.tank if key == "static" else np.zeros(g.n, bool)
        self.front = np.ones(g.n, bool) if key == "fork" else np.zeros(g.n, bool)
        # the local occlusion dip (a crease): the occlusion's neighbourhood mean over its own value
        self.crease = np.clip((g.blur(self.shade, max(2, int(round(0.5 / np.median(g.texel))))) - self.shade) * 3.0, 0, 1)
        # the knees: an ellipse on the tank's sides (8 units along, 6 up), facing out
        self.knee = knee_weight(sc, P, N) * self.tank
        # each wheel's polar coordinates: forward f (-y), up u; the gap to the tread, the lateral distance off the tyre
        self.wheel = {}
        for w, wh in sc.wheels.items():
            f, u = -(P[:, 1] - wh["c"][1]), P[:, 2] - wh["c"][2]
            rho = np.hypot(f, u)
            th = np.degrees(np.arctan2(u, f))       # 0 the front, 90 the top, 180 the rear
            to_axis = unit(np.stack([-(P[:, 0] - wh["c"][0]) * 0.3, (wh["c"][1] - P[:, 1]), wh["c"][2] - P[:, 2]], -1))
            self.wheel[w] = dict(gap=rho - wh["r"], th=th, lat=np.maximum(np.abs(P[:, 0] - wh["c"][0]) - wh["half"], 0),
                                 facing=(N * to_axis).sum(1))
        self.badge_d = _nearest_dist(P, sc.badge_sets)
        # under the always-shown plates (the tank badges' and the rear roundel, 0.03-0.5 over the paint, the shell 0.32
        # partly under them): no wear there (the shells unit's finding), the rust ring starts at their edge
        self.plate_h = plate_footprint(P, sc.plates)             # (since 2026-11-22a: kept) to the nearest plate
        self.under_plate = ss(PLATE_CLEAR + 0.12, PLATE_CLEAR - 0.12, self.plate_h)
        self.rim_d = _nearest_dist(P, sc.plate_rims, 3.0)       # (since 2026-11-22a) to a plate's outline
        # (since 2026-11-22a) where along its plate's outline a texel lies: -1 the plate's bottom edge, +1 its top (the
        # badge's art is the plate's middle; its clear rectangle has no edge to see, so the grime keeps to the top and
        # bottom edges, where dust settles and rust bleeds from under it)
        self.rim_v = np.zeros(g.n)
        for (v, _), rim in zip(sc.plates, sc.plate_rims):
            d = _nearest_dist(P, [rim], 3.0)
            zc, hz = float(v[:, 2].mean()), max(float(np.ptp(v[:, 2])) / 2, 0.5)
            self.rim_v = np.where(d <= self.rim_d + 1e-9, np.clip((P[:, 2] - zc) / hz, -1, 1), self.rim_v)
        # (since 2026-11-22a) where a plate lies under the paintwear shell (0.16 over the paint; the plates sit 0.03-0.5 over
        # it: the shell over a plate's ends, the shells unit's green): Paint condition kept off there only; elsewhere under
        # a plate the shell runs below it and the paint condition shows through the badge's clear parts
        self.plate_low = ss(PC_SHELL + 0.015, PC_SHELL, self.plate_h)
        self.plate_d = _nearest_dist(P, [sc.plate])
        self.splat = Splat(g)


class PartCtx(Ctx):
    """(since 2026-11-22a) One part shell's source shape's working grid with the features the part layers use (the paint
    shape's that make no sense here are zero: no tank, knee or plate)."""

    def __init__(self, sc, label, shp, shade_img, nrm_img):
        meta = PARTS[label]
        self.key, self.meta, self.sc = label, meta, sc
        self.g = g = Grid(shp, meta["size"] * WORK)
        P, N = g.P, g.N
        self.shade = np.clip(g.flat(shade_img), 0.05, 1.05)
        self.coach = np.zeros(g.n, bool)
        self.kap, self.kap_s = g.kap, g.kap_s
        self.pn = g.flat(nrm_img)
        self.up = N[:, 2]
        self.tank = self.rear = self.front = np.zeros(g.n, bool)
        self.crease = np.clip((g.blur(self.shade, max(2, int(round(0.5 / np.median(g.texel))))) - self.shade) * 3.0, 0, 1)
        self.knee = np.zeros(g.n)
        self.wheel = {}
        for w, wh in sc.wheels.items():
            f, u = -(P[:, 1] - wh["c"][1]), P[:, 2] - wh["c"][2]
            rho = np.hypot(f, u)
            to_axis = unit(np.stack([-(P[:, 0] - wh["c"][0]) * 0.3, (wh["c"][1] - P[:, 1]), wh["c"][2] - P[:, 2]], -1))
            self.wheel[w] = dict(gap=rho - wh["r"], th=np.degrees(np.arctan2(u, f)),
                                 lat=np.maximum(np.abs(P[:, 0] - wh["c"][0]) - wh["half"], 0), facing=(N * to_axis).sum(1))
        self.badge_d = np.full(g.n, 12.0)
        self.under_plate = np.zeros(g.n)
        self.plate_h = np.full(g.n, 2.0)
        self.plate_low = np.zeros(g.n)
        self.rim_d = np.full(g.n, 3.0)
        self.rim_v = np.zeros(g.n)
        self.plate_d = np.full(g.n, 12.0)
        self.port_d = np.full(g.n, 99.0)
        if label == "static_exhaust":          # each pipe's port: the top of each of its two long pieces
            v, tri = shp["v"], shp["tri"]
            for piece in _pieces(v, tri):
                vs = v[np.unique(tri[piece])]
                if np.ptp(vs[:, 2]) > 20.0:       # a pipe (the mufflers and clamps lie low)
                    port = vs[vs[:, 2] > vs[:, 2].max() - 1.2].mean(0)
                    self.port_d = np.minimum(self.port_d, np.linalg.norm(P - port, axis=1))
        self.splat = Splat(g)
        # where the part's shell lies (its triangles rasterised in the same UVs), a little grown so a filter at its edge
        # keeps the colour; everywhere when the nif has no shell for it
        shell = sc.part_shells.get(f"{label}_wear")
        if shell is not None:
            tid, _ = raster(shell["uv"][shell["tri"]], g.size, g.size)
            on = (tid >= 0).astype(np.float64)
            self.shell_cover = np.clip(g.flat(_box(on, 2)) * 3.0, 0, 1)
        else:
            self.shell_cover = np.ones(g.n)


def _pieces(v, tri):
    """The triangles of each welded connected piece of a shape: [index arrays]."""
    _, pw, T, ek = welded(v, tri)
    par = np.arange(len(pw))

    def root(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    for a, b in ek:
        ra, rb = root(a), root(b)
        if ra != rb:
            par[rb] = ra
    comp = np.array([root(i) for i in range(len(pw))])[T[:, 0]]
    return [np.flatnonzero(comp == c) for c in np.unique(comp)]


def part_inputs(bases, label, size):
    """(the occlusion, the shape's tangent normal) at size x size from a part's shipped _d (its luminance over its own
    bright level: the bake's occlusion in its colours) and _n."""
    d = W.read_dds(need(bases, Path("Textures/CMB/Bike") / f"{label}_d.dds"))[1][0][0][..., :3]
    nm = W.read_dds(need(bases, Path("Textures/CMB/Bike") / f"{label}_n.dds"))[1][0][0]
    L = LP.lum(LP.lin(d / 255.0))
    shade = L / max(float(np.percentile(L, 97)), 1e-4)
    x = nm[..., 0] / 255.0 * 2 - 1
    y = nm[..., 1] / 255.0 * 2 - 1
    z = np.sqrt(np.clip(1 - x * x - y * y, 0, 1))
    return _fit(shade, size), _fit(np.stack([x, y, z], -1), size)


def _nearest_dist(P, sets, reach=12.0, chunk=16384):
    """Each P's distance to the nearest point of the point sets (each a few hundred points), up to reach (beyond: reach),
    looked for only in each set's box grown by reach."""
    out = np.full(len(P), reach)
    for pts in sets:
        lo, hi = pts.min(0) - reach, pts.max(0) + reach
        sel = np.flatnonzero(np.all((P >= lo) & (P <= hi), axis=1))
        for s in range(0, len(sel), chunk):
            i = sel[s:s + chunk]
            d = np.sqrt(((P[i, None, :] - pts[None, :, :]) ** 2).sum(-1).min(1))
            out[i] = np.minimum(out[i], d)
    return out


def plate_rim(v, tri, step=0.1):
    """Points every `step` along a plate's outline (its welded mesh's boundary edges)."""
    _, pw, T, _ = welded(v, tri)
    e = np.sort(np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), axis=1)
    ek, cnt = np.unique(e, axis=0, return_counts=True)
    out = []
    for i, j in ek[cnt == 1]:
        a, b = pw[i], pw[j]
        k = max(1, int(np.ceil(np.linalg.norm(b - a) / step)))
        out.append(a[None] + (b - a)[None] * (np.arange(k) / k)[:, None])
    return np.concatenate(out)


def plate_footprint(P, plates, chunk=4096):
    """Each P's distance to the nearest of the plate meshes (each (v, tri), a hundred-odd triangles), looked for only in
    each plate's box grown by 2 (beyond: 2)."""
    out = np.full(len(P), 2.0)
    for v, tri in plates:
        lo, hi = v.min(0) - 2.0, v.max(0) + 2.0
        sel = np.flatnonzero(np.all((P >= lo) & (P <= hi), axis=1))
        A, Bv, C = v[tri[:, 0]], v[tri[:, 1]], v[tri[:, 2]]
        m = len(tri)
        for s in range(0, len(sel), chunk):
            i = sel[s:s + chunk]
            p = np.repeat(P[i], m, axis=0)
            d2, _ = closest_on_triangles(p, np.tile(A, (len(i), 1)), np.tile(Bv, (len(i), 1)), np.tile(C, (len(i), 1)))
            out[i] = np.minimum(out[i], np.sqrt(d2.reshape(len(i), m).min(1)))
    return out


def factory_inputs(bases, label, size):
    """(the occlusion, the coachline mask, the paint's tangent normal (x, y, z)) at size x size from the shipped factory
    diffuse, the index map and _n."""
    d = W.read_dds(need(bases, Path("Textures/CMB/Bike") / f"{label}_d.dds"))[1][0][0][..., :3]
    u = W.read_dds(need(bases, Path("Textures/CMB/Bike") / f"{label}_rf_d.dds"))[1][0][0][..., 0]
    nm = W.read_dds(need(bases, Path("Textures/CMB/Bike") / f"{label}_n.dds"))[1][0][0]
    L = LP.lum(LP.lin(d / 255.0))
    coach = u >= COACH_U
    shade = np.where(coach, L / LP.lum(hexlin(FACTORY_COACH)), L / LP.lum(hexlin(FACTORY_BODY)))
    x = nm[..., 0] / 255.0 * 2 - 1
    y = nm[..., 1] / 255.0 * 2 - 1
    z = np.sqrt(np.clip(1 - x * x - y * y, 0, 1))
    n = np.stack([x, y, z], -1)
    return _fit(shade, size), _fit(coach.astype(np.float64), size), _fit(n, size)


def _fit(img, size):
    """Box-down or repeat-up an image to size x size (powers of two)."""
    h = img.shape[0]
    if h == size:
        return img
    if h > size:
        f = h // size
        return img.reshape(size, f, size, f, *img.shape[2:]).mean(axis=(1, 3))
    f = size // h
    return np.repeat(np.repeat(img, f, 0), f, 1)


# --- the layers ----------------------------------------------------------------------------------------------------

class Layer:
    """Colour (linear, defined everywhere), cover, relief (units), specular, smoothness: flat over a context's texels."""

    def __init__(self, n, colour, spec=0.1, gloss=0.2):
        self.rgb = np.tile(hexlin(colour), (n, 1)) if isinstance(colour, str) else colour
        self.a = np.zeros(n)
        self.h = np.zeros(n)
        self.spec = np.full(n, spec)
        self.gloss = np.full(n, gloss)

    def paint_at(self, idx, cov, colour, spec, gloss, h=None):
        """paint() on the texels idx only (cov per idx; colour hex or (3,) linear)."""
        cov = np.clip(cov, 0, 1)
        col = hexlin(colour) if isinstance(colour, str) else np.asarray(colour)
        self.rgb[idx] = self.rgb[idx] * (1 - cov[:, None]) + col[None] * cov[:, None]
        self.spec[idx] = self.spec[idx] * (1 - cov) + spec * cov
        self.gloss[idx] = self.gloss[idx] * (1 - cov) + gloss * cov
        self.a[idx] = self.a[idx] + cov * (1 - self.a[idx])
        if h is not None:
            self.h[idx] = self.h[idx] + h * cov
        return self

    def paint(self, cov, colour, spec, gloss, h=None):
        """Lay `colour` (hex or (n, 3) linear) over this layer with cover `cov` (0..1)."""
        cov = np.clip(cov, 0, 1)
        col = hexlin(colour)[None, :] if isinstance(colour, str) else colour
        self.rgb = self.rgb * (1 - cov[:, None]) + col * cov[:, None]
        self.spec = self.spec * (1 - cov) + spec * cov
        self.gloss = self.gloss * (1 - cov) + gloss * cov
        self.a = self.a + cov * (1 - self.a)
        if h is not None:
            self.h = self.h + h * cov
        return self


def over(layers):
    """The layers stacked in order (each over the ones before): one Layer."""
    out = None
    for L in layers:
        if out is None:
            out = Layer(len(L.a), L.rgb.copy(), 0, 0)
            out.a, out.h, out.spec, out.gloss = L.a.copy(), L.h.copy(), L.spec.copy(), L.gloss.copy()
            continue
        a = L.a
        # the colour: alpha-weighted, with a small floor so a texel no layer covers keeps a blend of their colours
        wb = out.a * (1 - a) + 1e-3
        wt = a + 1e-3
        out.rgb = (out.rgb * wb[:, None] + L.rgb * wt[:, None]) / (wb + wt)[:, None]
        out.spec = (out.spec * wb + L.spec * wt) / (wb + wt)
        out.gloss = (out.gloss * wb + L.gloss * wt) / (wb + wt)
        out.h = out.h + L.h                    # the relief stacks: mud over dust over a chip
        out.a = a + out.a * (1 - a)
    return out


def droplet_mask(P, c, n, t, r, elong, tail, texel):
    """A droplet at c (normal n) travelling along t (in the surface): an ellipse r x r*elong along t, a tail tapering
    `tail` x its length beyond it (away from where it came from), antialiased over a texel."""
    q = P - c
    a = q @ t
    side = q - a[:, None] * t[None] - (q @ n)[:, None] * n[None]
    b = np.linalg.norm(side, axis=1)
    L = r * elong
    body = soft(1.0 - np.sqrt((a / L) ** 2 + (b / r) ** 2), texel / max(r, 1e-6) * 1.5)
    if tail > 0:
        s = np.clip((a - L * 0.6) / (L * tail), 0, 1)
        width = r * 0.42 * (1.0 - s) ** 1.3
        tl = soft(width - b, texel) * (a > L * 0.6) * (a < L * 0.6 + L * tail)
        body = np.maximum(body, tl)
    return body


def splat_drops(ctx, hits, colour_fn, layer, rng):
    """Draw droplets (hits: list of (point, normal, travel direction, radius, elongation, tail)) into a layer."""
    g, sp = ctx.g, ctx.splat
    tex = float(np.median(g.texel))
    for c, n, d, r, el, tail in hits:
        t = d - (d @ n) * n
        tl = np.linalg.norm(t)
        t = t / tl if tl > 1e-6 else np.cross(n, [0.0, 0.0, 1.0]) / max(np.linalg.norm(np.cross(n, [0.0, 0.0, 1.0])), 1e-6)
        reach = r * el * (1.0 + tail) + 3 * tex
        idx = sp.near(c, reach)
        if not len(idx):
            continue
        Pn = g.P[idx]
        keep = ((g.N[idx] @ n) > 0.35) & (np.abs((Pn - c) @ n) < 0.6 + r)
        idx = idx[keep]
        if not len(idx):
            continue
        m = droplet_mask(g.P[idx], c, n, t, r, el, tail, tex)
        on = m > 0
        if not on.any():
            continue
        idx, m = idx[on], m[on]
        col, spec, gloss, h = colour_fn(r, rng)
        layer.paint_at(idx, m, col, spec, gloss, h)


def run_mask(P, c, n, length, width, texel):
    """A run down the surface from c (normal n): a streak `length` long, `width` wide, tapering, a bead at its end."""
    gdir = np.array([0.0, 0.0, -1.0])
    gdir = gdir - (gdir @ n) * n
    gl = np.linalg.norm(gdir)
    if gl < 0.2:
        return np.zeros(len(P))
    gdir /= gl
    q = P - c
    a = q @ gdir
    side = q - a[:, None] * gdir[None] - (q @ n)[:, None] * n[None]
    b = np.linalg.norm(side, axis=1)
    s = np.clip(a / length, 0, 1)
    w = width * (1.0 - 0.55 * s) + width * 0.5 * np.exp(-((a - length) / (width * 1.2)) ** 2)
    return soft(w - b, texel) * (a > -width) * (a < length + width)


def splat_runs(ctx, runs, layer, colour, spec, gloss, h, alpha):
    g, sp = ctx.g, ctx.splat
    tex = float(np.median(g.texel))
    for c, n, length, width in runs:
        idx = sp.near(c + np.array([0, 0, -length / 2]), length / 2 + width * 2)
        if not len(idx):
            continue
        keep = ((g.N[idx] @ n) > 0.3) & (np.abs((g.P[idx] - c) @ n) < 1.0)
        idx = idx[keep]
        if not len(idx):
            continue
        m = run_mask(g.P[idx], c, n, length, width, tex)
        if not (m > 0).any():
            continue
        layer.paint_at(idx, m * alpha, colour, spec, gloss, h)


def pick(ctx, weight, count, rng):
    """`count` texels drawn with probability proportional to weight (none where it is 0)."""
    w = np.clip(weight, 0, None)
    if w.sum() <= 0 or count <= 0:
        return np.zeros(0, np.int64)
    return rng.choice(ctx.g.n, size=count, replace=True, p=w / w.sum())


def line_mask(P, c, n, t, half, width, texel):
    """A scratch: a segment through c along t (in the surface), 2 x half long, `width` wide in the middle tapering to
    nothing at its ends; the distance measured in the surface's plane (the line follows a gentle curve)."""
    q = P - c
    a = q @ t
    side = q - a[:, None] * t[None] - (q @ n)[:, None] * n[None]
    b = np.linalg.norm(side, axis=1)
    s = np.clip(np.abs(a) / half, 0, 1)
    w = width * np.sqrt(np.clip(1 - s * s, 0, 1))
    # under a texel wide: drawn a texel wide at the line's share of it, so a fine line stays a faint line
    k = np.clip(w * 2 / texel, 0, 1)
    return soft(np.maximum(w, texel * 0.5) - b, texel * 0.6) * k * (np.abs(a) < half)


def near_same(ctx, c, n, reach, depth=0.6):
    """The texels within reach of c on faces turned the way n is (not the sheet's other face), near its plane."""
    g = ctx.g
    idx = ctx.splat.near(c, reach)
    if not len(idx):
        return idx
    keep = ((g.N[idx] @ n) > 0.35) & (np.abs((g.P[idx] - c) @ n) < depth)
    return idx[keep]


def surface_dir(n, base, angle):
    """The direction `base` laid into the plane of n, turned by angle (radians) about n."""
    t = np.asarray(base, np.float64) - (np.asarray(base, np.float64) @ n) * n
    if np.linalg.norm(t) < 0.2:
        t = np.cross(n, [1.0, 0.0, 0.0])
    t = t / np.linalg.norm(t)
    b = np.cross(n, t)
    return t * math.cos(angle) + b * math.sin(angle)


def layer_weathered(ctx, rng):
    g, P, N = ctx.g, ctx.g.P, ctx.g.N
    L = Layer(g.n, HAZE, 0.18, 0.3)
    # the sun: what faces the sky most, in the open, mottled; the oxidised blotches on top
    expo = ss(-0.1, 0.95, ctx.up) ** 1.4 * (0.3 + 0.7 * ss(0.35, 0.95, ctx.shade))
    mott = fbm(P, 7.0, 1, 4)
    blot = ss(0.56, 0.70, fbm(P, 3.0, 2, 4)) * ss(0.3, 0.85, ctx.up)
    haze = np.clip(0.04 + 0.30 * expo * (0.5 + 1.6 * (mott - 0.5) + 0.5) + 0.18 * blot, 0, 0.46)
    L.paint(haze, HAZE, 0.16, 0.28)
    L.haze = haze                       # (since 2026-11-22a) the sun's share alone: over the plates with --badge-grime
    # where chips come: the convex edges (the rolled lips and the tighter bends), the knees, the stones the front wheel
    # throws (what faces forward on the tank and the front fender)
    edge = np.maximum(ss(0.3, 1.2, ctx.kap), 0.75 * ss(0.12, 0.45, ctx.kap_s))
    fw = ctx.wheel["F"]
    stone = ss(-0.1, -0.7, N[:, 1]) * np.exp(-np.maximum(fw["gap"], 0) / 40.0) * (ctx.tank | ctx.front)
    field = 0.75 * edge + 1.0 * ctx.knee + 0.5 * stone + 0.05
    big = fbm(P, 0.5, 3, 4)                       # flaked chips: edges and knees
    fine = noise(P, 0.12, 4)                      # stone chips: small dots
    reach = big + 0.48 * np.minimum(field, 1.2)
    chip_big = soft(reach - 0.93, 0.02)
    chip_fine = soft(fine - (0.985 - 0.16 * np.minimum(field, 1.2)), 0.015) * ss(0.02, 0.25, field)
    chip = np.maximum(chip_big, chip_fine)
    steel = soft(reach - 1.03, 0.02)
    rim = np.clip(soft(reach - 0.905, 0.02) - chip_big, 0, 1)      # the paint's broken edge round a flake, lighter
    L.paint(rim * 0.55, SCRATCH, 0.3, 0.45)
    L.paint(chip, PRIMER, 0.14, 0.32, h=-0.035)
    L.paint(steel * chip, STEEL, 0.55, 0.5, h=-0.02)
    # fine scratches: short straight lines, mostly along the bike, crowded round the knees and on the tank's top and the
    # front fender's (boots, a belt, a strap)
    where = (0.06 + 1.6 * ctx.knee + 0.55 * ss(0.5, 0.95, ctx.up) * ctx.tank + 0.3 * ctx.front * ss(0.0, 0.8, ctx.up)
             + 0.15 * ctx.rear * ss(0.3, 0.9, ctx.up))
    count = SCRATCHES[ctx.key]
    tex = float(np.median(g.texel))
    sc = np.zeros(g.n)
    for i in pick(ctx, where, count, rng):
        c, n = P[i], N[i]
        at_knee = ctx.knee[i] > 0.3
        t = surface_dir(n, (0.0, 1.0, 0.0), rng.normal(0, 0.9 if at_knee else 0.35))
        half = 0.5 * float(np.exp(rng.uniform(np.log(0.4), np.log(4.0))))
        idx = near_same(ctx, c, n, half + 0.2, 0.4 + 0.1 * half)
        if not len(idx):
            continue
        m = line_mask(P[idx], c, n, t, half, float(rng.uniform(0.012, 0.035)), tex) * float(rng.uniform(0.45, 0.95))
        sc[idx] = np.maximum(sc[idx], m)
    L.paint(sc * 0.85, SCRATCH, 0.3, 0.42, h=-0.008)
    return L


def layer_dust(ctx, rng, grime=GRIME_OLD):
    g, P, N = ctx.g, ctx.g.P, ctx.g.N
    blot = fbm(P, 5.0, 12, 4)
    col = hexlin(DUST)[None, :] * (1 - ss(0.4, 0.7, blot))[:, None] + hexlin(DUST_DARK)[None, :] * ss(0.4, 0.7, blot)[:, None]
    L = Layer(g.n, col, 0.08, 0.15)
    up = ss(-0.05, 0.9, ctx.up)
    occl = ss(0.95, 0.5, ctx.shade) * ss(-0.6, 0.0, ctx.up)
    low = ss(72.0, 36.0, P[:, 2])
    wash = ss(0.58, 0.74, aniso(P, (0, 0, 1), 9.0, 0.8, 13)) * (1 - up)
    grain = noise(P, 0.09, 11)
    amt = 0.42 * up + 0.85 * ctx.crease + 0.30 * occl + 0.28 * low + 0.35 * (blot - 0.5)
    amt = amt * (1 - 0.65 * ctx.knee) * (1 - 0.55 * wash)
    a = np.clip(amt, 0, 0.9) * (0.78 + 0.44 * grain)
    L.paint(np.clip(a, 0, 0.92), col, 0.08, 0.15, h=0.01)
    if grime == GRIME_NEW:          # (since 2026-11-22a) the dust caught along a plate's top edge, broken up
        rim = ss(0.6, 0.1, ctx.rim_d) * ss(0.3, 0.75, ctx.rim_v) * soft(fbm(P, 0.8, 14, 3) - 0.45, 0.05)
        L.paint(np.clip(rim * 0.5 * (0.7 + 0.6 * grain), 0, 0.6), col, 0.08, 0.15, h=0.01)
    return L


def _mud_colour(thick, P):
    """Pale and dry where thin, darker and wet only where thick (linear, (n, 3)), and its spec / smoothness."""
    v = fbm(P, 1.5, 22, 3)
    t = np.clip(thick * 1.15 - 0.15 + 0.45 * (v - 0.5), 0, 1)
    wet, mid, dry = hexlin(MUD_WET), hexlin(MUD_MID), hexlin(MUD_DRY)
    lo = ss(0.0, 0.6, t)
    hi = ss(0.65, 1.0, t)
    col = dry[None] * (1 - lo)[:, None] + mid[None] * (lo - hi)[:, None] + wet[None] * hi[:, None]
    return col, 0.07 + 0.25 * hi, 0.14 + 0.4 * hi


def spray_rays(sc, rng, n_tread=9000, n_ground=5000):
    """Mud rays: (origins, directions, size scale) from each tyre's tread (a wheel rolling forward throws mud up and
    back behind its contact patch, forward over its top) and from the ground round the contact patches (up)."""
    O, D, S = [], [], []
    for w, wh in sc.wheels.items():
        c, R, half = wh["c"], wh["r"], wh["half"]
        # the tread: the angle of release phi (0 the front, 90 the top, 180 the rear, -90 the ground), weighted
        k = n_tread // 2
        phi = np.where(rng.random(k) < 0.72, rng.uniform(-178.0, -100.0, k), rng.uniform(95.0, 178.0, k))
        ph = np.radians(phi)
        x = c[0] + rng.uniform(-half * 0.9, half * 0.9, k)
        f, u = R * np.cos(ph), R * np.sin(ph)
        o = np.stack([x, c[1] - f, c[2] + u], -1)
        vf, vu = np.sin(ph), -np.cos(ph)                 # the tread's velocity, the wheel rolling forward
        d = np.stack([rng.normal(0, 0.28, k), -vf + rng.normal(0, 0.18, k), vu + rng.normal(0, 0.18, k)], -1)
        O.append(o)
        D.append(unit(d))
        S.append(np.full(k, 1.0))
        # the ground: splashes round the contact patch: from beside the tyre in and up (onto the outsides), from under
        # it up and out (onto the insides)
        k = n_ground // 2
        side = np.where(rng.random(k) < 0.5, -1.0, 1.0)
        outside = rng.random(k) < 0.7
        gx = c[0] + np.where(outside, side * (half + rng.uniform(0.5, 12.0, k)), rng.uniform(-half, half, k))
        gy = c[1] + rng.normal(0, 11.0, k)
        o = np.stack([gx, gy, np.full(k, 0.3)], -1)
        dx = np.where(outside, -side * rng.uniform(0.05, 0.45, k), side * rng.uniform(0.05, 0.5, k))
        d = np.stack([dx, rng.normal(0, 0.35, k), rng.uniform(0.6, 1.0, k)], -1)
        O.append(o)
        D.append(unit(d))
        S.append(np.full(k, 0.8))
    return np.concatenate(O), np.concatenate(D), np.concatenate(S)


def layer_mud(ctx, rng, hits):
    g, P, N = ctx.g, ctx.g.P, ctx.g.N
    base = np.zeros(g.n)          # how much mud: 0..1
    streak = np.zeros(g.n)        # the spray's streaks round each wheel (arcs about its axle)
    wide = np.zeros(g.n)          # how far the fine spray reaches
    for w, wh in ctx.sc.wheels.items():
        q = ctx.wheel[w]
        own = ctx.front if w == "F" else ctx.rear
        cz = wh["c"][2]
        gap = np.maximum(q["gap"], 0)
        # the insides facing the tyre: caked
        inside = ss(0.0, 0.5, q["facing"]) * np.exp(-gap / 9.0) * np.exp(-q["lat"] / 4.0)
        # the outsides: the spray wraps round the edges and the puddles splash up: by the gap and the height
        top, fall = MUD_REACH[w]
        outer = np.exp(-gap / fall) * ss(cz + top, cz + top - 26.0, P[:, 2])
        if w == "R":                               # the tail behind the wheel: thrown up and back
            outer = outer * (0.75 + 0.45 * ss(95.0, 170.0, q["th"]))
        base = np.maximum(base, own * np.maximum(0.95 * inside, 0.85 * outer))
        wide = np.maximum(wide, own * np.exp(-gap / 22.0) * ss(cz + 46.0, cz + 10.0, P[:, 2]))
        arc = np.radians(q["th"]) * wh["r"]
        sn = _noise3(np.stack([arc / 5.0, (q["gap"] + wh["r"]) / 0.45, P[:, 0] / 0.7], -1) + _off(26 + (w == "R")))
        streak = np.where(own, sn, streak)
    # the tank's lower front, from the front wheel: its arcs too
    fw = ctx.wheel["F"]
    tank_front = ctx.tank * ss(-0.15, -0.75, N[:, 1]) * ss(84.0, 64.0, P[:, 2])
    base = np.maximum(base, 0.8 * tank_front)
    wide = np.maximum(wide, 0.9 * tank_front)
    if ctx.key == "static":
        arc = np.radians(fw["th"]) * ctx.sc.wheels["F"]["r"]
        sn = _noise3(np.stack([arc / 5.0, (fw["gap"]) / 0.45, P[:, 0] / 0.7], -1) + _off(28))
        streak = np.where(ctx.tank, sn, streak)
    blot = fbm(P, 2.2, 23, 4)
    thick = np.clip(base * (0.62 + 1.2 * (blot - 0.5) + 0.7 * (streak - 0.5)) + 0.18 * base, 0, 1)
    cov = soft(thick - 0.2, 0.06)
    col, spec, gloss = _mud_colour(thick, P)
    L = Layer(g.n, col.copy(), 0.1, 0.2)
    lump = fbm(P, 0.35, 24, 3)
    L.paint(cov * 0.97, col, spec, gloss, h=0.05 + 0.16 * thick * lump)
    # the spray's fine speckle, thinning with the reach
    spk = noise(P, 0.11, 25)
    dots = soft(spk - (0.95 - 0.28 * np.clip(wide * 1.2, 0, 1)), 0.03) * ss(0.04, 0.25, wide)
    dcol, dspec, dgloss = _mud_colour(np.full(g.n, 0.25), P)
    L.paint(dots * 0.9, dcol, dspec, dgloss, h=0.03)

    def mcol(r, rng_):
        t = float(np.clip(0.15 + r * 1.1 + rng_.normal(0, 0.15), 0, 1))
        c = hexlin(MUD_DRY) * (1 - t) + hexlin(MUD_WET) * t
        return c, 0.08 + 0.2 * t, 0.15 + 0.3 * t, 0.05 + 0.08 * t
    splat_drops(ctx, hits, mcol, L, rng)
    return L


def layer_rust(ctx, rng, grime=GRIME_OLD):
    g, P, N = ctx.g, ctx.g.P, ctx.g.N
    v = fbm(P, 0.9, 31, 4)
    col = (hexlin(RUST_DARK)[None] * ss(0.6, 0.35, v)[:, None] + hexlin(RUST)[None] * (1 - np.abs(v - 0.5) * 2)[:, None]
           + hexlin(RUST_LIGHT)[None] * ss(0.5, 0.75, v)[:, None])
    col = col / np.maximum((ss(0.6, 0.35, v) + (1 - np.abs(v - 0.5) * 2) + ss(0.5, 0.75, v))[:, None], 1e-6)
    L = Layer(g.n, col.copy(), 0.07, 0.12)
    # where: blooms from the edges, round the badges and the plate, the tank's underside, inside the fenders
    edge = np.clip(ss(0.25, 1.6, ctx.kap) * 0.8 + ss(0.08, 0.5, ctx.kap_s) * 0.7, 0, 1.2)
    badge = ss(2.6, 0.5, ctx.badge_d)
    plate = ss(9.0, 2.0, ctx.plate_d)
    under = ctx.tank * ss(-0.15, -0.7, ctx.up)
    inside = (ctx.front | ctx.rear) * ss(0.0, 0.5, np.maximum(ctx.wheel["F"]["facing"], ctx.wheel["R"]["facing"])) \
        * np.exp(-np.maximum(np.minimum(ctx.wheel["F"]["gap"], ctx.wheel["R"]["gap"]), 0) / 10.0)
    field = 0.75 * edge + 1.0 * badge + 0.8 * plate + 0.95 * under + 0.5 * inside + 0.05
    b1 = fbm(P, 1.4, 32, 5)
    core = soft(b1 + 0.45 * np.minimum(field, 1.3) - 0.98, 0.03)
    halo = np.clip(soft(b1 + 0.45 * np.minimum(field, 1.3) - 0.88, 0.06) - core, 0, 1)
    pit = noise(P, 0.12, 33)
    # the stain round a bloom (rust bleeding into the paint, the paint lifted), then the rust itself
    L.paint(halo * 0.42, RUST_STAIN, 0.1, 0.25, h=0.025)
    L.paint(core, col, 0.07, 0.12, h=0.02 + 0.04 * pit)
    speck = soft(noise(P, 0.08, 34) - 0.8, 0.03) * core
    L.paint(speck * 0.8, RUST_LIGHT, 0.06, 0.1)
    # streaks run down from the blooms on the steep faces
    steep = (np.abs(ctx.up) < 0.75).astype(float)
    src = pick(ctx, core * steep * (b1 > 0.55), 260 if ctx.key == "static" else 90, rng)
    runs = [(P[i], N[i], float(rng.uniform(1.0, 5.0)), float(rng.uniform(0.08, 0.22))) for i in src]
    splat_runs(ctx, runs, L, RUST, 0.07, 0.12, 0.01, 0.55)
    if grime == GRIME_NEW:
        # (since 2026-11-22a) over a plate only a ring at its edge (rust creeping in from under it), broken up, and a few
        # streaks running down from its lower edge
        up = ctx.under_plate
        L.a = L.a * (1.0 - up)
        ring = (ss(0.9, 0.15, ctx.rim_d) * ss(-0.3, -0.75, ctx.rim_v)
                * soft(fbm(P, 0.55, 35, 3) - 0.47, 0.04))     # along the bottom edge only, broken up
        L.paint(np.clip(ring * np.maximum(up, ss(0.6, 0.1, ctx.rim_d)), 0, 1), col, 0.07, 0.12, h=0.02)
        low = ring * up * (np.abs(ctx.up) < 0.75) * (N[:, 2] < 0.3)
        src = pick(ctx, low, 24 if ctx.key == "static" else 0, rng)
        runs = [(P[i], N[i], float(rng.uniform(1.0, 3.5)), float(rng.uniform(0.08, 0.18))) for i in src]
        splat_runs(ctx, runs, L, RUST, 0.07, 0.12, 0.01, 0.5)
    return L



def plate_blooms(sc):
    """(since 2026-11-23a, --rust) Two or three rust blooms by each tank plate and the roundel, at random places on its
    outline, each pushed a little off it, in or out ((centre, radius) list, the same every build): rust that breaks out
    by a plate here and there, never along its edges."""
    if getattr(sc, "_blooms", None) is None:
        sc._blooms = []
        for i, ((v, _), rim) in enumerate(zip(sc.plates, sc.plate_rims)):
            rng = np.random.default_rng(370 + i)
            zc, hz = float(v[:, 2].mean()), max(float(np.ptp(v[:, 2])) / 2, 0.5)
            w = 1.0 + 1.5 * np.clip((zc - rim[:, 2]) / hz, 0, 1)          # rather the lower half: water sits there
            c0 = v.mean(0)
            for k in rng.choice(len(rim), size=int(rng.integers(2, 4)), replace=False, p=w / w.sum()):
                c = rim[k] + (c0 - rim[k]) / max(np.linalg.norm(c0 - rim[k]), 1e-6) * float(rng.uniform(-1.0, 1.2))
                sc._blooms.append((c, float(rng.uniform(1.1, 2.3))))
    return sc._blooms


def _rust_blooms(L, g, s, thr, rim_a, body_a, pit, h0=0.015):
    """(since 2026-11-23a, --rust) Rust blooms where s passes thr on layer L (its colour the body's): a faint wash round
    each, a see-through body (the paint shows through, body_a, varied by pit) going darker and denser to the bloom's
    edge (rim_a, a band about RUST_RIM_W wide) where the rust's front lifts the paint, dark pits in it; the bloom (0..1)
    returned."""
    P = g.P
    core = soft(s - thr, 0.03)
    r = max(1, int(round(RUST_RIM_W / 2.0 / np.median(g.texel))))
    rim = core * (1.0 - ss(0.55, 0.95, g.blur(core, r)))   # 1 at a bloom's edge, 0 well inside it
    halo = np.clip(soft(s - (thr - 0.05), 0.04) - core, 0, 1)
    L.paint(halo * 0.1, RUST_WASH, 0.1, 0.25, h=0.01)
    col = L.rgb * (1.0 - rim)[:, None] + hexlin(RUST_RIM)[None] * rim[:, None]
    L.paint(core * (body_a * (0.75 + 0.5 * pit) * (1.0 - rim) + rim_a * rim), col, 0.07, 0.12,
            h=h0 + 0.03 * pit * (1.0 - rim) + 0.015 * rim)
    L.paint(soft(noise(P, 0.08, 34) - 0.82, 0.03) * core * 0.45, RUST_RIM, 0.06, 0.1)
    return core


def _rust_body(P, seed):
    """(since 2026-11-23a, --rust) The lighter rust's body colour (linear): two browns by a slow noise."""
    t = ss(0.3, 0.75, fbm(P, 0.9, seed, 4))
    return hexlin(RUST_BODY)[None] * (1 - t)[:, None] + hexlin(RUST_PALE)[None] * t[:, None]


def layer_rust_light(ctx, rng):
    """(since 2026-11-23a, --rust; test 59: "rust is too much, should be less intense, more transparent and in darker
    colors on edges", and the rust round the Brotherhood plate read as "a rectangle around the frame") Rusty, lighter:
    fewer, smaller blooms from the same places (the edges, the tank's underside, inside the fenders, by the number
    plate), each see-through in its middle and dark at its edge, browner, fewer and fainter streaks; nothing follows a
    plate's outline (22a's band round the badges and ring along a plate's bottom edge gone): two or three blooms by each
    plate at random places on its outline, and over a plate's face the rust as on the paint round it."""
    g, P, N = ctx.g, ctx.g.P, ctx.g.N
    L = Layer(g.n, _rust_body(P, 31), 0.07, 0.12)
    edge = np.clip(ss(0.25, 1.6, ctx.kap) * 0.8 + ss(0.08, 0.5, ctx.kap_s) * 0.7, 0, 1.2)
    plate = ss(9.0, 2.0, ctx.plate_d)
    under = ctx.tank * ss(-0.15, -0.7, ctx.up)
    inside = (ctx.front | ctx.rear) * ss(0.0, 0.5, np.maximum(ctx.wheel["F"]["facing"], ctx.wheel["R"]["facing"])) \
        * np.exp(-np.maximum(np.minimum(ctx.wheel["F"]["gap"], ctx.wheel["R"]["gap"]), 0) / 10.0)
    spots = np.zeros(g.n)
    for j, (c, r) in enumerate(plate_blooms(ctx.sc)):
        lo, hi = c - 2.0 * r, c + 2.0 * r
        i = np.flatnonzero(np.all((P >= lo) & (P <= hi), axis=1))
        if len(i):
            d = np.linalg.norm(P[i] - c, axis=1) * (0.7 + 0.6 * fbm(P[i], 0.7, 36 + j, 3))
            spots[i] = np.maximum(spots[i], ss(r, 0.3 * r, d))
    clump = ss(0.42, 0.7, fbm(P, 6.0, 37, 3))                # where the paint gave way: random, in clumps
    field = (0.75 * edge + 0.8 * plate + 0.95 * under + 0.5 * inside + (0.75 if ctx.key == "static" else 0.5) * clump
             + 1.1 * spots + 0.05)
    b1 = fbm(P, 1.4, 32, 5)
    s = b1 + 0.45 * np.minimum(field, 1.3)
    core = _rust_blooms(L, g, s, 0.96, 0.7, 0.45, noise(P, 0.12, 33))
    steep = (np.abs(ctx.up) < 0.75).astype(float)
    src = pick(ctx, core * steep * (b1 > 0.6), 110 if ctx.key == "static" else 35, rng)
    runs = [(P[i], N[i], float(rng.uniform(1.0, 4.0)), float(rng.uniform(0.06, 0.16))) for i in src]
    splat_runs(ctx, runs, L, RUST_BODY, 0.07, 0.12, 0.008, 0.28)
    return L

def blood_rays(sc, rng):
    """Blood rays: four sources (a hit at the front left, a burst at the right side, a fall from above the rear, a
    splash from behind on the right), each
    a cone of droplets toward the bike; (origins, directions, size scale)."""
    srcs = [((18.0, -118.0, 82.0), (0.0, -56.0, 58.0), 14.0, 1500, 1.0),
            ((-48.0, 2.0, 84.0), (-8.0, -4.0, 74.0), 16.0, 1100, 0.95),
            ((22.0, 30.0, 140.0), (0.0, 62.0, 64.0), 15.0, 800, 1.1),
            ((-40.0, 95.0, 50.0), (-6.0, 62.0, 60.0), 12.0, 700, 0.9)]
    O, D, S = [], [], []
    for o, at, cone, k, sz in srcs:
        o, at = np.array(o), np.array(at)
        axis = unit(at - o)
        e1 = unit(np.cross(axis, [0, 0, 1.0]))
        e2 = np.cross(axis, e1)
        ang = np.radians(cone) * np.sqrt(rng.random(k))
        az = rng.uniform(0, 2 * np.pi, k)
        d = (axis[None] * np.cos(ang)[:, None] + e1[None] * (np.sin(ang) * np.cos(az))[:, None]
             + e2[None] * (np.sin(ang) * np.sin(az))[:, None])
        O.append(np.tile(o, (k, 1)))
        D.append(d)
        S.append(np.full(k, sz))
    return np.concatenate(O), np.concatenate(D), np.concatenate(S)


SMEARS = [  # (from, to, width, the face's outward hint): hand smears on the tank's left side, the rear fender's right top,
    # the front fender's left side
    ((14.6, -14.0, 79.0), (13.6, 6.0, 71.0), 1.6, (1.0, 0.0, 0.0)),
    ((-6.5, 48.0, 70.5), (-4.5, 70.0, 66.5), 1.4, (-0.5, 0.0, 0.85)),
    ((6.2, -66.0, 56.0), (6.0, -50.0, 58.0), 1.2, (1.0, 0.0, 0.2)),
]


def layer_blood(ctx, rng, hits):
    g, P, N = ctx.g, ctx.g.P, ctx.g.N
    L = Layer(g.n, BLOOD, 0.35, 0.55)
    # the smears: a stroke, ragged at its sides, streaky along it (fingers), thinning toward its end
    for i, (a, b, w, hint) in enumerate(SMEARS):
        a, b = np.array(a), np.array(b)
        mid = 0.5 * (a + b)
        faces = np.flatnonzero((N @ unit(np.array(hint))) > 0.3)
        if not len(faces) or ctx.key in PARTS:
            continue                                    # smears are on the paint only
        j = int(faces[np.argmin(((P[faces] - mid) ** 2).sum(1))])
        if np.linalg.norm(P[j] - mid) > 4.0:
            continue                                    # not on this shape
        n0 = N[j]
        a, b = a + n0 * ((P[j] - mid) @ n0), b + n0 * ((P[j] - mid) @ n0)     # onto the surface's level
        d = b - a
        ln = np.linalg.norm(d)
        d = d / ln
        q = P - a
        s = np.clip(q @ d, 0, ln)
        off = np.linalg.norm(q - s[:, None] * d[None], axis=1)
        rag = 0.35 * (fbm(P, 0.6, 61 + i, 3) - 0.5)
        body = soft(w * (1.0 - 0.35 * s / ln) + rag * w - off, 0.08)
        streak = 0.45 + 0.55 * ss(0.35, 0.65, aniso(P, d, 6.0, 0.18, 62 + i))
        fade = 1.0 - 0.75 * (s / ln) ** 1.2
        same = ((N @ n0) > 0.4) & (np.abs(q @ n0) < 3.0)
        L.paint(np.clip(body * streak * fade * same, 0, 0.85), BLOOD_THIN, 0.3, 0.5, h=0.008)

    def bcol(r, rng_):
        t = float(np.clip(r * 1.6 + rng_.normal(0, 0.1), 0, 1))
        c = hexlin(BLOOD_THIN) * (1 - t) + hexlin(BLOOD_THICK) * t
        return c, 0.35 + 0.2 * t, 0.55 + 0.25 * t, 0.015 + 0.05 * t
    splat_drops(ctx, hits, bcol, L, rng)
    # drips from the big drops on the steep faces
    big = [(c, n, r) for c, n, _, r, _, _ in hits if r > 0.28 and abs(n[2]) < 0.65]
    runs = [(c, n, float(rng.uniform(1.0, 4.5)) * (r / 0.3), r * 0.45) for c, n, r in big]
    splat_runs(ctx, runs, L, BLOOD, 0.35, 0.55, 0.02, 0.92)
    return L


def droplets_from(sc, O, D, S, rng, kind):
    """Cast rays, keep the hits, and file each as a droplet with the shape it landed on: {shape key: [drops]}."""
    t, tri, hp, fn = raycast(O, D, sc.V, sc.T)
    ns = len(sc.shapes["static_paint"]["tri"])
    out = {"static": [], "fork": []}
    for i in np.flatnonzero(tri >= 0):
        n = fn[i]
        if n @ D[i] > 0:
            n = -n                                      # the face the ray met
        cosi = abs(float(n @ D[i]))
        el = float(np.clip(1.0 / max(cosi, 0.22), 1.0, 4.5))
        if kind == "mud":
            r = float(np.exp(rng.uniform(np.log(0.05), np.log(0.45)))) * S[i]
            tail = 0.0 if rng.random() < 0.6 else 0.5
        else:
            r = float(np.exp(rng.uniform(np.log(0.03), np.log(0.42)))) * S[i]
            if rng.random() < 0.04:
                r *= 2.2
            tail = float(np.clip((el - 1.0) * 0.9, 0.0, 2.2))
        key = "static" if tri[i] < ns else "fork"
        out[key].append((hp[i] + n * 0.0, n, D[i], r, el, tail))
        if kind == "blood" and el > 1.6 and rng.random() < 0.7:     # a satellite drop ahead of a long one
            tt = D[i] - (D[i] @ n) * n
            tt /= max(np.linalg.norm(tt), 1e-6)
            out[key].append((hp[i] + tt * r * el * (2.2 + rng.random()), n, D[i], r * 0.3, 1.2, 0.0))
    return out, int((tri >= 0).sum())


# --- the Paint condition layers (since 2026-11-22a): the paint's own damage, no grime --------------------------------

def _scratch_lines(ctx, rng, where, count, kinds):
    """Short straight scratches: `count` drawn where `where` says, each of a kind (share, colour, width range, alpha
    range, relief); returns per kind the cover (max over its lines)."""
    g, P, N = ctx.g, ctx.g.P, ctx.g.N
    tex = float(np.median(g.texel))
    covs = [np.zeros(g.n) for _ in kinds]
    shares = np.cumsum([k[0] for k in kinds])
    for i in pick(ctx, where, count, rng):
        c, n = P[i], N[i]
        at_knee = ctx.knee[i] > 0.3
        t = surface_dir(n, (0.0, 1.0, 0.0), rng.normal(0, 0.95 if at_knee else 0.4))
        half = 0.5 * float(np.exp(rng.uniform(np.log(0.3), np.log(5.0))))
        kind = int(np.searchsorted(shares, rng.random() * shares[-1], side="right"))
        kind = min(kind, len(kinds) - 1)
        _, _, (w0, w1), (a0, a1), _ = kinds[kind]
        idx = near_same(ctx, c, n, half + 0.2, 0.4 + 0.1 * half)
        if not len(idx):
            continue
        m = line_mask(P[idx], c, n, t, half, float(rng.uniform(w0, w1)), tex) * float(rng.uniform(a0, a1))
        covs[kind][idx] = np.maximum(covs[kind][idx], m)
    return covs


def pc_scratch(ctx, rng):
    """Scratched: fine scratches through the clear coat (pale), deeper ones to the primer and a few to bare steel, crowded
    where things rub (the knees, the tank's top, the fenders' tops), and scuffed patches of very fine marks there."""
    g, P = ctx.g, ctx.g.P
    L = Layer(g.n, SCRATCH, 0.3, 0.42)
    where = (0.08 + 1.8 * ctx.knee + 0.7 * ss(0.5, 0.95, ctx.up) * ctx.tank + 0.45 * ctx.front * ss(0.0, 0.8, ctx.up)
             + 0.4 * ctx.rear * ss(0.3, 0.9, ctx.up))
    # scuffs: a haze of fine marks along the bike where things rub
    scuff = ss(0.45, 0.75, aniso(P, (0.1, 1.0, 0.05), 1.6, 0.05, 81)) * ss(0.55, 0.7, fbm(P, 2.5, 82, 3))
    L.paint(np.clip(scuff * np.clip(where, 0, 1.2) * 0.45, 0, 0.45), SCRATCH, 0.26, 0.4, h=-0.004)
    kinds = [(0.80, SCRATCH, (0.012, 0.035), (0.45, 0.95), -0.008),
             (0.15, PRIMER, (0.03, 0.06), (0.8, 1.0), -0.025),
             (0.05, STEEL, (0.025, 0.05), (0.85, 1.0), -0.03)]
    covs = _scratch_lines(ctx, rng, where, PC_SCRATCHES[ctx.key], kinds)
    for (_, colour, _, _, h), cv in zip(kinds, covs):
        spec, gloss = (0.3, 0.42) if colour == SCRATCH else (0.14, 0.32) if colour == PRIMER else (0.6, 0.55)
        if colour != SCRATCH:                        # a pale rim round a deep scratch (the paint's broken edge)
            rim = np.clip(ctx.g.blur(cv, 1) * 1.6 - cv, 0, 1)
            L.paint(rim * 0.6, SCRATCH, 0.3, 0.42)
        L.paint(cv, colour, spec, gloss, h=h)
    return L


def pc_chip(ctx, rng):
    """Chipped: flaked chips to the primer (bare steel in the deep ones, a pale broken edge round each) at the convex
    edges and the knee grips; stone chips where the front wheel throws them and low down by both wheels."""
    g, P, N = ctx.g, ctx.g.P, ctx.g.N
    L = Layer(g.n, PRIMER, 0.14, 0.32)
    edge = np.maximum(ss(0.3, 1.2, ctx.kap), 0.75 * ss(0.12, 0.45, ctx.kap_s))
    fw = ctx.wheel["F"]
    stone = ss(-0.1, -0.7, N[:, 1]) * np.exp(-np.maximum(fw["gap"], 0) / 40.0) * (ctx.tank | ctx.front)
    low = np.zeros(g.n)
    for w, wh in ctx.sc.wheels.items():
        own = ctx.front if w == "F" else ctx.rear
        low = np.maximum(low, own * np.exp(-np.maximum(ctx.wheel[w]["gap"], 0) / 14.0)
                         * ss(wh["c"][2] + 18.0, wh["c"][2] + 4.0, P[:, 2]) * ss(0.2, -0.3, ctx.wheel[w]["facing"]))
    field = 0.85 * edge + 1.15 * ctx.knee + 0.45 * stone + 0.35 * low + 0.04
    if ctx.key == "fork":
        field = field * 0.75             # the front mudguard's many rolled lips: fewer chips along them
    big = fbm(P, 0.5, 91, 4)
    fine = noise(P, 0.11, 92)
    reach = big + 0.5 * np.minimum(field, 1.2)
    chip_big = soft(reach - 0.9, 0.02)
    chip_fine = soft(fine - (0.98 - 0.15 * np.minimum(field, 1.2)), 0.015) * ss(0.02, 0.25, field)
    chip = np.maximum(chip_big, chip_fine)
    steel = soft(reach - 1.0, 0.02)
    rim = np.clip(soft(reach - 0.875, 0.02) - chip_big, 0, 1)
    L.paint(rim * 0.55, SCRATCH, 0.3, 0.45)
    L.paint(chip, PRIMER, 0.14, 0.32, h=-0.035)
    L.paint(steel * chip, STEEL, 0.55, 0.5, h=-0.02)
    return L


def pc_fade(ctx, rng):
    """Sun-faded: a pale chalky haze, strongest on what faces the sky in the open, mottled, with oxidised blotches; the
    clear coat lifting in patches on the tops (paler still, matte, a crisp lighter edge)."""
    g, P = ctx.g, ctx.g.P
    L = Layer(g.n, HAZE, 0.16, 0.28)
    expo = ss(-0.15, 0.95, ctx.up) ** 1.3 * (0.3 + 0.7 * ss(0.35, 0.95, ctx.shade))
    mott = fbm(P, 7.0, 101, 4)
    blot = ss(0.55, 0.70, fbm(P, 3.0, 102, 4)) * ss(0.3, 0.85, ctx.up)
    haze = np.clip(0.05 + 0.36 * expo * (0.5 + 1.6 * (mott - 0.5) + 0.5) + 0.2 * blot, 0, 0.55)
    L.paint(haze, HAZE, 0.14, 0.25)
    L.haze = haze                       # its share over the plates (a badge fades with the paint)
    peel_f = fbm(P, 2.0, 103, 4) + 0.4 * expo
    peel = soft(peel_f - 1.0, 0.02) * ss(0.45, 0.8, expo)
    edge = np.clip(soft(peel_f - 0.975, 0.015) * ss(0.45, 0.8, expo) - peel, 0, 1)
    L.paint(edge * 0.85, "f2efe8", 0.1, 0.2, h=0.012)
    L.paint(peel * 0.62, CLEARCOAT, 0.08, 0.15, h=-0.01)
    return L


def pc_primer(ctx, rng):
    """Primer patches: repairs sanded back and primed, never top-coated: grey filler primer (a red-oxide one on the
    static shape), feathered where it was sprayed thin, a dull scuffed halo of sanding round each."""
    g, P, N = ctx.g, ctx.g.P, ctx.g.N
    L = Layer(g.n, FILLER, 0.12, 0.25)
    open_face = ss(0.35, 0.8, ctx.shade) * (1.0 - ctx.under_plate) * (np.abs(ctx.up) < 0.97)
    k = PC_PATCHES[ctx.key]
    centres = []
    for i in pick(ctx, open_face * (0.6 + 0.4 * ctx.tank + 0.5 * ss(0.0, 0.8, ctx.up)), 60, rng):
        if all(np.linalg.norm(P[i] - P[j]) > 9.0 for j in centres):
            centres.append(i)
        if len(centres) == k:
            break
    grain = noise(P, 0.25, 111)
    for n_, i in enumerate(centres):
        c, n = P[i], N[i]
        r = float(rng.uniform(2.2, 5.5)) * (0.7 if ctx.key == "fork" else 1.0)
        idx = near_same(ctx, c, n, r * 1.9, 3.0)
        idx = idx[(N[idx] @ n) > 0.2]
        if not len(idx):
            continue
        d = np.linalg.norm(P[idx] - c, axis=1)
        wob = 1.0 + 0.32 * (fbm(P[idx], 1.6, 112 + n_, 3) - 0.5) * 2
        re = r * wob
        core = soft(re * 0.82 - d, 0.05)
        feather = ss(re * 1.18, re * 0.82, d) * 0.55 * (0.7 + 0.6 * grain[idx])
        halo = ss(re * 1.65, re * 1.18, d) * (1 - ss(re * 1.18, re * 0.82, d)) * 0.3
        halo = halo * ss(0.4, 0.7, aniso(P[idx], (0.2, 1.0, 0.1), 0.8, 0.05, 113 + n_))
        colour = RED_OXIDE if (ctx.key == "static" and n_ in (2, 6)) else FILLER
        L.paint_at(idx, halo, SCRATCH, 0.2, 0.3, h=-0.004)
        L.paint_at(idx, np.maximum(core, feather), colour, 0.1, 0.22, h=0.01)
        L.paint_at(idx, core * ss(0.55, 0.85, grain[idx]) * 0.35, FILLER_DARK if colour == FILLER else "5e2a1b", 0.1, 0.2)
    return L


PC_LAYERS = {"pc_scratch": pc_scratch, "pc_chip": pc_chip, "pc_fade": pc_fade, "pc_primer": pc_primer}


# --- the part shells' layers (since 2026-11-22a): the pipes, the engine's covers, the fork lowers ------------------------

def part_weathered(ctx, rng):
    """Weathered on a part: the metal dulled (a haze, heaviest on top), heat colouring on the pipes from each port (blue,
    purple, gold, straw, fading out about 14 units down the pipe), chips to bare metal at the edges and stone chips low on
    what faces forward."""
    g, P, N = ctx.g, ctx.g.P, ctx.g.N
    L = Layer(g.n, DULL, 0.2, 0.3)
    expo = ss(-0.3, 0.9, ctx.up) * (0.4 + 0.6 * ss(0.3, 0.9, ctx.shade))
    mott = fbm(P, 4.0, 131, 4)
    L.paint(np.clip(0.08 + 0.3 * expo * (0.6 + 1.2 * (mott - 0.5)), 0, 0.45), DULL, 0.2, 0.3)
    if ctx.key == "static_exhaust":
        d = ctx.port_d + 1.2 * (fbm(P, 2.0, 132, 3) - 0.5)
        stops = np.array([0.0, 4.0, 8.0, 12.0])
        cols = np.array([hexlin(c) for c in HEAT])
        t = np.clip(np.interp(d, stops, np.arange(4.0)), 0, 3)
        i0 = np.floor(np.minimum(t, 2.999)).astype(int)
        f = (t - i0)[:, None]
        col = cols[i0] * (1 - f) + cols[i0 + 1] * f
        L.paint(np.clip(0.8 * ss(16.0, 6.0, d), 0, 0.8), col, 0.5, 0.55)
    edge = np.maximum(ss(0.4, 1.6, ctx.kap), 0.6 * ss(0.15, 0.5, ctx.kap_s))
    stone = ss(-0.1, -0.7, N[:, 1]) * ss(50.0, 25.0, P[:, 2])
    field = 0.7 * edge + 0.5 * stone + 0.04
    reach = fbm(P, 0.45, 133, 4) + 0.45 * np.minimum(field, 1.2)
    chip = np.maximum(soft(reach - 0.95, 0.02), soft(noise(P, 0.12, 134) - (0.985 - 0.12 * np.minimum(field, 1.2)), 0.015))
    L.paint(chip * 0.9, STEEL, 0.5, 0.45, h=-0.02)
    return L


def part_rust(ctx, rng):
    """Rusty on a part: rust blooms from the edges and low down, heavy on the mufflers' bottoms and seams and the clamps,
    pitted, with streaks running down; on the engine's covers white corrosion spots and rust only at the edges."""
    g, P, N = ctx.g, ctx.g.P, ctx.g.N
    v = fbm(P, 0.9, 141, 4)
    col = (hexlin(RUST_DARK)[None] * ss(0.6, 0.35, v)[:, None] + hexlin(RUST)[None] * (1 - np.abs(v - 0.5) * 2)[:, None]
           + hexlin(RUST_LIGHT)[None] * ss(0.5, 0.75, v)[:, None])
    col = col / np.maximum((ss(0.6, 0.35, v) + (1 - np.abs(v - 0.5) * 2) + ss(0.5, 0.75, v))[:, None], 1e-6)
    L = Layer(g.n, col.copy(), 0.07, 0.12)
    edge = np.clip(ss(0.3, 1.6, ctx.kap) * 0.8 + ss(0.1, 0.5, ctx.kap_s) * 0.7, 0, 1.2)
    low = ss(40.0, 15.0, P[:, 2]) * ss(0.3, -0.6, ctx.up)
    if ctx.key == "static_engine":
        oxide = soft(fbm(P, 1.0, 142, 4) + 0.3 * ctx.crease + 0.2 * low - 0.82, 0.04)
        L.paint(oxide * 0.75, ALU_OXIDE, 0.1, 0.15, h=0.01)
        field = 0.6 * edge + 0.03
    elif ctx.key == "static_exhaust":
        heat = ss(14.0, 4.0, ctx.port_d)
        field = 0.7 * edge + 0.9 * low + 0.5 * heat + 0.12
    else:
        field = 0.7 * edge + 0.7 * low + 0.1
    b1 = fbm(P, 1.2, 143, 5)
    core = soft(b1 + 0.45 * np.minimum(field, 1.3) - 0.98, 0.03)
    halo = np.clip(soft(b1 + 0.45 * np.minimum(field, 1.3) - 0.88, 0.06) - core, 0, 1)
    L.paint(halo * 0.4, RUST_STAIN, 0.1, 0.25, h=0.02)
    L.paint(core, col, 0.07, 0.12, h=0.02 + 0.04 * noise(P, 0.12, 144))
    steep = (np.abs(ctx.up) < 0.75).astype(float)
    src = pick(ctx, core * steep * (b1 > 0.55), 80, rng)
    runs = [(P[i], N[i], float(rng.uniform(0.8, 3.5)), float(rng.uniform(0.08, 0.2))) for i in src]
    splat_runs(ctx, runs, L, RUST, 0.07, 0.12, 0.01, 0.5)
    return L



def part_rust_light(ctx, rng):
    """(since 2026-11-23a, --rust) Rusty on a part, lighter (as layer_rust_light): fewer blooms from the same places
    (the mufflers' bottoms and seams, the clamps, by the hot ports, the edges), see-through with dark edges, fewer and
    fainter streaks; the engine covers' white corrosion as 2026-11-22a's."""
    g, P, N = ctx.g, ctx.g.P, ctx.g.N
    L = Layer(g.n, _rust_body(P, 141), 0.07, 0.12)
    edge = np.clip(ss(0.3, 1.6, ctx.kap) * 0.8 + ss(0.1, 0.5, ctx.kap_s) * 0.7, 0, 1.2)
    low = ss(40.0, 15.0, P[:, 2]) * ss(0.3, -0.6, ctx.up)
    if ctx.key == "static_engine":
        oxide = soft(fbm(P, 1.0, 142, 4) + 0.3 * ctx.crease + 0.2 * low - 0.82, 0.04)
        L.paint(oxide * 0.75, ALU_OXIDE, 0.1, 0.15, h=0.01)
        field = 0.6 * edge + 0.03
    elif ctx.key == "static_exhaust":
        heat = ss(14.0, 4.0, ctx.port_d)
        field = 0.7 * edge + 0.8 * low + 0.45 * heat + 0.1
    else:
        field = 0.7 * edge + 0.7 * low + 0.1
    b1 = fbm(P, 1.2, 143, 5)
    s = b1 + 0.45 * np.minimum(field, 1.3)
    core = _rust_blooms(L, g, s, 0.98, 0.7, 0.45, noise(P, 0.12, 144), h0=0.012)
    steep = (np.abs(ctx.up) < 0.75).astype(float)
    src = pick(ctx, core * steep * (b1 > 0.6), 45, rng)
    runs = [(P[i], N[i], float(rng.uniform(0.8, 3.0)), float(rng.uniform(0.06, 0.16))) for i in src]
    splat_runs(ctx, runs, L, RUST_BODY, 0.07, 0.12, 0.008, 0.28)
    return L

def part_mud(ctx, rng, hits):
    """Muddy on a part: caked low down by the wheels it sits by (the fork lowers by the axle, the mufflers' bottoms, the
    crankcase's front), a speckle where the spray thins, the droplets the wheels throw onto it."""
    g, P, N = ctx.g, ctx.g.P, ctx.g.N
    base = np.zeros(g.n)
    wide = np.zeros(g.n)
    for w in ctx.meta["wheels"]:
        wh, q = ctx.sc.wheels[w], ctx.wheel[w]
        gap = np.maximum(q["gap"], 0)
        near = np.exp(-gap / 16.0) * np.exp(-q["lat"] / 10.0)
        lowz = ss(wh["c"][2] + 6.0, wh["c"][2] - 14.0, P[:, 2])
        base = np.maximum(base, near * (0.45 + 0.55 * lowz) * (0.6 + 0.4 * ss(-0.2, 0.5, q["facing"])))
        wide = np.maximum(wide, np.exp(-gap / 26.0) * ss(wh["c"][2] + 20.0, wh["c"][2] - 10.0, P[:, 2]))
    # the road's splash: low down on any part, most on what faces down or forward
    road = ss(27.0, 12.0, P[:, 2]) * (0.45 + 0.55 * np.maximum(ss(0.2, -0.6, ctx.up), ss(-0.1, -0.7, N[:, 1])))
    base = np.maximum(base, 0.6 * road)
    wide = np.maximum(wide, ss(46.0, 18.0, P[:, 2]))
    base = base * (0.75 + 0.25 * ss(0.4, -0.5, ctx.up))
    blot = fbm(P, 1.8, 151, 4)
    thick = np.clip(base * (0.6 + 1.2 * (blot - 0.5)) + 0.15 * base, 0, 1)
    col, spec, gloss = _mud_colour(thick, P)
    L = Layer(g.n, col.copy(), 0.1, 0.2)
    L.paint(soft(thick - 0.22, 0.06) * 0.96, col, spec, gloss, h=0.05 + 0.12 * thick * fbm(P, 0.35, 152, 3))
    dots = soft(noise(P, 0.11, 153) - (0.95 - 0.28 * np.clip(wide * 1.2, 0, 1)), 0.03) * ss(0.04, 0.25, wide)
    dcol, dspec, dgloss = _mud_colour(np.full(g.n, 0.25), P)
    L.paint(dots * 0.9, dcol, dspec, dgloss, h=0.03)

    def mcol(r, rng_):
        t = float(np.clip(0.15 + r * 1.1 + rng_.normal(0, 0.15), 0, 1))
        return hexlin(MUD_DRY) * (1 - t) + hexlin(MUD_WET) * t, 0.08 + 0.2 * t, 0.15 + 0.3 * t, 0.05 + 0.08 * t
    splat_drops(ctx, hits, mcol, L, rng)
    return L


def part_droplets(sc, O, D, S, rng, kind):
    """The rays cast against the paint and the parts together; the hits on a part filed as droplets: {part: [drops]}
    (the paint's own droplets come from the paint-only cast, as 2026-11-21a's)."""
    t, tri, hp, fn = raycast(O, D, sc.Vp, sc.Tp)
    out = {lab: [] for lab in PARTS}
    starts = [(lab, s0) for lab, s0 in sc.part_ranges]
    for i in np.flatnonzero(tri >= sc.part_ranges[0][1]):
        lab = [l_ for l_, s0 in starts if tri[i] >= s0][-1]
        n = fn[i] if fn[i] @ D[i] <= 0 else -fn[i]
        el = float(np.clip(1.0 / max(abs(float(n @ D[i])), 0.22), 1.0, 4.5))
        if kind == "mud":
            r = float(np.exp(rng.uniform(np.log(0.05), np.log(0.45)))) * S[i]
            tail = 0.0 if rng.random() < 0.6 else 0.5
        else:
            r = float(np.exp(rng.uniform(np.log(0.03), np.log(0.42)))) * S[i]
            tail = float(np.clip((el - 1.0) * 0.9, 0.0, 2.2))
        out[lab].append((hp[i], n, D[i], r, el, tail))
    return out


# --- the maps ------------------------------------------------------------------------------------------------------

def bleed(img, cov, rounds=24):
    """Empty texels take their nearest covered texel's value (ring by ring), the rest the covered texels' mean."""
    H, Wd = cov.shape
    lab = np.where(cov, np.arange(H * Wd).reshape(H, Wd), -1)
    lab = LP.dilate(lab, rounds)
    flat = img.reshape(H * Wd, *img.shape[2:])
    out = flat.copy()
    got = lab.ravel() >= 0
    out[got] = flat[lab.ravel()[got]]
    rest = ~got
    if rest.any():
        out[rest] = flat[cov.ravel()].mean(0)
    return out.reshape(img.shape)


def _down(img, f):
    H, Wd = img.shape[:2]
    return img.reshape(H // f, f, Wd // f, f, *img.shape[2:]).sum(axis=(1, 3))


def relief_normal(ctx, h, paint_n):
    """The overlay's tangent-space normal on the working grid: the paint's own _n with the wear's relief (h in units)
    added (Direct3D: R +u, G +v down the image), the slopes in units over units (h's differences over the texel's size),
    no difference across an island's border."""
    g = ctx.g
    H = g.image(h)
    isl = g.image(g.island.astype(np.float64) + 1.0)
    tex = g.image(g.texel, 1.0)
    grads = []
    for ax in (1, 0):
        fwd = np.roll(H, -1, ax) - H
        bwd = H - np.roll(H, 1, ax)
        okf = (np.roll(isl, -1, ax) == isl) & (isl > 0)
        okb = (np.roll(isl, 1, ax) == isl) & (isl > 0)
        gsum = np.where(okf, fwd, 0) + np.where(okb, bwd, 0)
        cnt = okf.astype(float) + okb.astype(float)
        grads.append(g.flat(gsum / np.maximum(cnt, 1) / tex))
    gx, gy = grads
    nx, ny, nz = paint_n[:, 0], paint_n[:, 1], np.maximum(paint_n[:, 2], 0.2)
    # whiteout blend of the paint's normal and the relief's (-gx, -gy, 1)
    out = unit(np.stack([nx - gx * nz, ny - gy * nz, nz], -1))
    return out


def shape_maps(ctx, layer, clear_plates=True):
    """(_d RGBA uint8 at size, _n RGBA at aux, _s RGBA at aux, a report) of one layer stack on one shape."""
    g, meta = ctx.g, ctx.meta
    size, aux = meta["size"], meta["aux"]
    # the colour, shaded by the factory occlusion as the paint under it is
    rgb = layer.rgb * np.clip(ctx.shade, 0.12, 1.0)[:, None]
    a = np.clip(layer.a, 0, 1) * ((1.0 - ctx.under_plate) if clear_plates else 1.0)
    cov = g.cov.astype(np.float64)
    pa = g.image(a)
    prgb = g.image(rgb * (a[:, None] + 1e-3))
    wsum = g.image(a + 1e-3)
    f = WORK
    A = _down(pa, f) / np.maximum(_down(cov, f), 1e-9)
    C = _down(prgb, f) / np.maximum(_down(wsum, f), 1e-9)[..., None]
    covd = _down(cov, f) > 0
    rgba = np.concatenate([LP.srgb(C) , A[..., None]], -1)
    rgba = bleed(rgba, covd)
    d8 = np.clip(np.rint(rgba * 255), 0, 255).astype(np.uint8)
    # the normal and the specular at the aux size
    n = relief_normal(ctx, layer.h, ctx.pn)
    fa = g.size // aux
    wn = g.image(np.ones(g.n))
    N_ = _down(g.image(n), fa) / np.maximum(_down(wn, fa), 1e-9)[..., None]
    N_ = unit(N_)
    covn = _down(cov, fa) > 0
    N_ = bleed(N_, covn)
    n8 = np.zeros((aux, aux, 4), np.uint8)
    n8[..., :3] = np.clip(np.rint((N_ * 0.5 + 0.5) * 255), 0, 255).astype(np.uint8)
    n8[..., 3] = 255
    wsp = g.image(a + 0.05)
    S_ = _down(g.image(np.stack([layer.spec, layer.gloss], -1) * (a + 0.05)[:, None]), fa) / np.maximum(_down(wsp, fa), 1e-9)[..., None]
    S_ = bleed(S_, covn)
    s8 = np.zeros((aux, aux, 4), np.uint8)
    s8[..., :2] = np.clip(np.rint(S_ * 255), 0, 255).astype(np.uint8)
    s8[..., 3] = 255
    return d8, n8, s8


def _erode(m, k):
    """(since 2026-11-23a) A boolean image eroded k times by its four neighbours."""
    out = m.copy()
    for _ in range(k):
        e = out.copy()
        e[1:] &= out[:-1]
        e[:-1] &= out[1:]
        e[:, 1:] &= out[:, :-1]
        e[:, :-1] &= out[:, 1:]
        out = e
    return out


def write_tex(path, img, fmt, **kw):
    data = W.build([img], fmt, **kw)
    path.write_bytes(data)
    return len(data)


# --- the tyres -----------------------------------------------------------------------------------------------------

def tyre_mud(sc, bases, w, tread_mode=TREAD_NEW):
    """The mud's cover and colour (linear) per texel of a tyre's 1024 map, and a report. tread_mode (--tyre-mud):
    2026-11-21a caked the whole tread; 2026-11-22a (test 58: "the tire part where it touches ground is too muddy ... black
    parts are showing through") packs the mud in the grooves and on the blocks' walls, clods on the shoulders, and leaves
    the faces that meet the road clean; the sidewalls as 2026-11-21a's."""
    shp = sc.shapes[f"wheel{w}_tyre"]
    wh = sc.wheels[w]
    size = TYRE_SIZE * WORK
    g = Grid(shp, size)
    P, N = g.P, g.N
    c = wh["c"]
    r = np.hypot(P[:, 1] - c[1], P[:, 2] - c[2])
    R = wh["r"]
    d0 = W.read_dds(need(bases, Path("Textures/CMB/Bike") / f"wheel{w}_tyre_d.dds"))[1][0][0][..., :3]
    lum = LP.lum(LP.lin(d0 / 255.0))
    tl = np.median(lum[lum > 0.005])
    shade = np.clip(g.flat(_fit(lum / tl, size)), 0.3, 1.6)
    tread = ss(R - 1.8, R - 0.5, r)
    side = ss(R - 10.0, R - 0.8, r)
    hub = ss(16.0, 20.0, r)
    blot = fbm(P, 2.0, 71, 4)
    groove = ss(0.95, 0.55, shade) * tread
    # caked on the tread, splashed in blotches down the sidewall thinning toward the rim, packed in the grooves
    amt = 0.85 * tread + 0.8 * side ** 1.3 + 0.35 * groove + 0.9 * (blot - 0.5)
    a = soft(amt - 0.52, 0.1) * np.clip(0.55 + amt, 0, 1) * hub
    spk = noise(P, 0.16, 72)
    dots = soft(spk - (0.9 - 0.22 * side), 0.03) * ss(0.05, 0.4, side) * hub
    splash = soft(fbm(P, 1.3, 74, 4) - 0.6, 0.04) * ss(21.5, 23.0, r) * hub     # splashes anywhere on the sidewall
    a = np.clip(np.maximum(np.maximum(a, dots * 0.9), splash * 0.9), 0, 0.95)
    if tread_mode == TREAD_NEW:
        rad = np.stack([np.zeros(g.n), P[:, 1] - c[1], P[:, 2] - c[2]], -1) / np.maximum(r, 1e-9)[:, None]
        nr = (N * rad).sum(1)                                  # 1 on a face turned out to the road, 0 on a wall
        zone = ss(R - 3.6, R - 2.6, r)                         # the tread band, the shoulders to the crown
        crown = ss(R - 1.0, R - 0.35, r) * ss(0.72, 0.9, nr)   # the blocks' faces that meet the road
        wall = zone * ss(0.7, 0.4, nr)                         # the grooves' floors and walls, the blocks' sides
        shoulder = zone * ss(R - 0.4, R - 1.6, r)              # the tread's flanks down to the sidewall
        clod = fbm(P, 0.7, 75, 4)
        amt_t = 0.95 * wall + 0.55 * shoulder + 0.4 * ss(0.95, 0.55, shade) * zone + 1.1 * (clod - 0.5)
        a_t = soft(amt_t - 0.45, 0.08) * np.clip(0.5 + amt_t, 0, 1)
        speck = soft(noise(P, 0.14, 76) - 0.9, 0.03) * 0.7     # a few specks left on the faces
        a = a * (1 - zone) + a_t * zone
        a = np.clip(a * (1 - crown) + crown * np.minimum(a, speck), 0, 0.95)
    t = np.clip(0.3 + 0.6 * tread + 0.3 * (fbm(P, 1.2, 73, 3) - 0.5) * 2, 0, 1)
    col = hexlin(TYRE_MUD_DRY)[None] * (1 - t)[:, None] + hexlin(TYRE_MUD_WET)[None] * t[:, None]
    col = col * np.clip(0.4 + 0.6 * shade, 0.3, 1.1)[:, None]
    cov = g.cov.astype(np.float64)
    A = _down(g.image(a), WORK) / np.maximum(_down(cov, WORK), 1e-9)
    C = _down(g.image(col * (a[:, None] + 1e-3)), WORK) / np.maximum(_down(g.image(a + 1e-3), WORK), 1e-9)[..., None]
    covd = _down(cov, WORK) > 0
    A, C = bleed(A, covd), bleed(C, covd)
    rr = _down(g.image(r), WORK) / np.maximum(_down(cov, WORK), 1e-9)
    return A, C, rr, covd


def tyre_diffuse(base_srgb, A, C):
    L = LP.lin(base_srgb / 255.0)
    out = L * (1 - A[..., None]) + C * A[..., None]
    rgba = np.zeros(base_srgb.shape[:2] + (4,), np.uint8)
    rgba[..., :3] = LP.to_u8(out)
    rgba[..., 3] = 255
    return rgba


# --- the materials -------------------------------------------------------------------------------------------------

def wear_material(template, key, shape, prefix="wear", depth=DEPTH_OLD):
    """An overlay's materials file (the Wear slot's, prefix wear; since 2026-11-22a Paint condition's, paintwear) on the
    shell's source shape's shipped file."""
    m = dict(template)
    m["textures"] = dict(template["textures"])
    stem = f"{prefix}_{key}_{shape}"
    m["textures"].update(diffuse=TEX + f"{stem}_d.dds", normal=TEX + f"{stem}_n.dds",
                         smoothspec=TEX + f"{stem}_s.dds", greyscale="", envmap="")
    m.update(alpha=1.0, alpha_blend=1, alpha_blend_src=6, alpha_blend_dst=7, alpha_test=False, alpha_test_ref=128,
             zbuffer_write=False, zbuffer_test=True, decal=True, decal_no_fade=False, two_sided=False,
             environment_mapping=False, env_map_mask_scale=1.0, grayscale_to_palette_color=False,
             grayscale_to_palette_scale=1.0, cast_shadows=False, receive_shadows=True, specular_enabled=True,
             specular_mult=1.0, smoothness=1.0)
    if depth == DEPTH_NEW:
        # (since 2026-11-22a) two blended overlays over the paint (Paint condition's at 0.16, the Wear's at 0.32) share their
        # source's bounds, so the game can't sort them: each writes its depth and discards its empty texels, so a grime
        # texel hides the paint condition under it whichever is drawn first (the shells unit's advice)
        m.update(zbuffer_write=True, alpha_test=True, alpha_test_ref=OVERLAY_TEST)
    m.pop("_raw_tex", None)
    m.pop("_raw_strings", None)
    return m


def tyre_material(template, w, suf):
    m = dict(template)
    m["textures"] = dict(template["textures"])
    m["textures"]["diffuse"] = TEX + f"wheel{w}_tyre{suf}_d.dds"
    m.pop("_raw_tex", None)
    m.pop("_raw_strings", None)
    return m


def plan():
    """{relative path under Data: (kind, format, width, height)} of everything this tool writes."""
    out = {}
    for key in KEYS:
        for sh, meta in SHAPES.items():
            t = f"Textures/CMB/Bike/wear_{key}_{sh}"
            out[f"{t}_d.dds"] = ("d", "bc3", meta["size"])
            out[f"{t}_n.dds"] = ("n", "bc5", meta["aux"])
            out[f"{t}_s.dds"] = ("s", "bc5", meta["aux"])
            for worn in ("", "_worn"):
                out[f"Materials/CMB/Bike/wear_{key}_{sh}{worn}.bgsm"] = ("m", sh, worn)
    for key in KEYS:
        for sh, meta in PARTS.items():
            t = f"Textures/CMB/Bike/wear_{key}_{sh}"
            out[f"{t}_d.dds"] = ("d", "bc3", meta["size"])
            out[f"{t}_n.dds"] = ("n", "bc5", meta["aux"])
            out[f"{t}_s.dds"] = ("s", "bc5", meta["aux"])
            for worn in ("", "_worn"):
                out[f"Materials/CMB/Bike/wear_{key}_{sh}{worn}.bgsm"] = ("m", sh, worn)
    for key in PC_KEYS:
        for sh, meta in SHAPES.items():
            t = f"Textures/CMB/Bike/paintwear_{key}_{sh}"
            out[f"{t}_d.dds"] = ("d", "bc3", meta["size"])
            out[f"{t}_n.dds"] = ("n", "bc5", meta["aux"])
            out[f"{t}_s.dds"] = ("s", "bc5", meta["aux"])
            for worn in ("", "_worn"):
                out[f"Materials/CMB/Bike/paintwear_{key}_{sh}{worn}.bgsm"] = ("pm", sh, worn)
    for w in "FR":
        for src, suf in TYRES:
            out[f"Textures/CMB/Bike/wheel{w}_tyre{suf}_d.dds"] = ("t", "bc1", TYRE_SIZE)
            for worn in ("", "_worn"):
                out[f"Materials/CMB/Bike/wheel{w}_tyre{suf}{worn}.bgsm"] = ("tm", w + src, worn)
    return out


# --- build ---------------------------------------------------------------------------------------------------------

class Report(list):
    """The build's lines, each printed as it comes."""

    def append(self, line):
        print(line, flush=True)
        super().append(line)


PC_SEED = {"pc_scratch": 501, "pc_chip": 502, "pc_fade": 503, "pc_primer": 504}


PART_DUST = 0.55                                      # a part's dust: the paint's layer at this share
PART_SEED = {"weathered": 601, "dust": 602, "mud": 603, "rust": 604, "blood": 605}


def make_layers(sc, bases, keys_needed, report, pc_needed=(), grime=GRIME_OLD, parts=(), rust=RUST_OLD):
    """{shape key: (ctx, {layer name: Layer})} for the layers the keys need (the Wear keys' and the Paint condition
    keys')."""
    need_l = sorted({l for k in keys_needed for l in STACKS[k]})
    need_pc = sorted({l for k in pc_needed for l in PC_STACKS[k]})
    ctxs = {}
    for key, meta in SHAPES.items():
        t0 = time.time()
        size = meta["size"] * WORK
        shade, coach, nrm = factory_inputs(bases, meta["label"], size)
        ctxs[key] = Ctx(sc, key, sc.shapes[meta["label"]], bases, shade, nrm, coach)
        g = ctxs[key].g
        report.append(f"{meta['label']}: {g.n} texels of {size}x{size}, {g.size and len(np.unique(g.island))} islands, "
                      f"texel {np.median(g.texel):.3f} units, occlusion p5/p50 {np.percentile(ctxs[key].shade, 5):.2f}/"
                      f"{np.percentile(ctxs[key].shade, 50):.2f} ({time.time() - t0:.1f} s)")
    drops, pdrops = {}, {}
    if "mud" in need_l:
        O, D, S = spray_rays(sc, np.random.default_rng(101))
        drops["mud"], nh = droplets_from(sc, O, D, S, np.random.default_rng(102), "mud")
        report.append(f"mud rays {len(O)}: {nh} hits (static {len(drops['mud']['static'])}, fork {len(drops['mud']['fork'])})")
        if parts:
            pdrops["mud"] = part_droplets(sc, O, D, S, np.random.default_rng(103), "mud")
            report.append("  on the parts: " + ", ".join(f"{k} {len(v)}" for k, v in pdrops["mud"].items()))
    if "blood" in need_l:
        O, D, S = blood_rays(sc, np.random.default_rng(201))
        drops["blood"], nh = droplets_from(sc, O, D, S, np.random.default_rng(202), "blood")
        report.append(f"blood rays {len(O)}: {nh} hits (static {len(drops['blood']['static'])}, fork "
                      f"{len(drops['blood']['fork'])})")
        if parts:
            pdrops["blood"] = part_droplets(sc, O, D, S, np.random.default_rng(203), "blood")
            report.append("  on the parts: " + ", ".join(f"{k} {len(v)}" for k, v in pdrops["blood"].items()))
    out = {}
    for key, ctx in ctxs.items():
        layers = {}
        for i, name in enumerate(need_l):
            t0 = time.time()
            rng = np.random.default_rng(300 + 17 * i + (0 if key == "static" else 7))
            if name == "weathered":
                layers[name] = layer_weathered(ctx, rng)
            elif name == "dust":
                layers[name] = layer_dust(ctx, rng, grime)
            elif name == "mud":
                layers[name] = layer_mud(ctx, rng, drops["mud"][key])
            elif name == "rust":
                layers[name] = layer_rust(ctx, rng, grime) if rust == RUST_OLD else layer_rust_light(ctx, rng)
            elif name == "blood":
                layers[name] = layer_blood(ctx, rng, drops["blood"][key])
            report.append(f"  {key} {name}: cover mean {layers[name].a.mean():.3f}, over 0.5 {(layers[name].a > 0.5).mean():.3f} "
                          f"({time.time() - t0:.1f} s)")
        for name in need_pc:
            t0 = time.time()
            layers[name] = PC_LAYERS[name](ctx, np.random.default_rng(PC_SEED[name] + (0 if key == "static" else 50)))
            report.append(f"  {key} {name}: cover mean {layers[name].a.mean():.3f}, over 0.5 {(layers[name].a > 0.5).mean():.3f} "
                          f"({time.time() - t0:.1f} s)")
        out[key] = (ctx, layers)
    for lab in parts:
        t0 = time.time()
        meta = PARTS[lab]
        shade, nrm = part_inputs(bases, meta["label"], meta["size"] * WORK)
        ctx = PartCtx(sc, lab, sc.shapes[meta["label"]], shade, nrm)
        report.append(f"{lab}: {ctx.g.n} texels of {ctx.g.size}x{ctx.g.size}, texel {np.median(ctx.g.texel):.3f} units "
                      f"({time.time() - t0:.1f} s)")
        layers = {}
        for name in need_l:
            rng = np.random.default_rng(PART_SEED[name] + 10 * list(PARTS).index(lab))
            if name == "weathered":
                layers[name] = part_weathered(ctx, rng)
            elif name == "dust":
                layers[name] = layer_dust(ctx, rng)
                layers[name].a = layers[name].a * PART_DUST     # a part's dust lighter: "not too much but noticeable"
            elif name == "mud":
                layers[name] = part_mud(ctx, rng, pdrops["mud"][lab])
            elif name == "rust":
                layers[name] = part_rust(ctx, rng) if rust == RUST_OLD else part_rust_light(ctx, rng)
            elif name == "blood":
                layers[name] = layer_blood(ctx, rng, pdrops["blood"][lab])
            report.append(f"  {lab} {name}: cover mean {layers[name].a.mean():.3f}")
        out[lab] = (ctx, layers)
    return out


def _label(sh):
    """A shape key's source shape (the paint shapes' and the parts')."""
    return SHAPES[sh]["label"] if sh in SHAPES else PARTS[sh]["label"]


def _plate_haze(ctx, L, u=None):
    """A copy of a layer with a sun haze (Weathered, Sun-faded) with only that haze over the tank plates and the roundel
    (u, default their footprints: the grime's shell lies over them now; a badge fades with the paint, but its enamel takes
    no chip, scratch or primer of the paint's); a layer without a haze kept off them."""
    u = ctx.under_plate if u is None else u
    if not hasattr(L, "haze"):
        return _mask(L, u)
    out = Layer(len(L.a), L.rgb * (1 - u)[:, None] + hexlin(HAZE)[None] * u[:, None], 0, 0)
    out.a = L.a * (1 - u) + L.haze * u
    out.h = L.h * (1 - u)
    out.spec = L.spec * (1 - u) + 0.16 * u
    out.gloss = L.gloss * (1 - u) + 0.28 * u
    return out


def _mask(L, m):
    """A copy of a layer with its cover times (1 - m)."""
    out = Layer(len(L.a), L.rgb, 0, 0)
    out.a, out.h, out.spec, out.gloss = L.a * (1.0 - m), L.h, L.spec, L.gloss
    return out


def build(args):
    t_all = time.time()
    keys = [k for k in (args.only or KEYS) if k in KEYS]
    pc_keys = [k for k in (args.only or PC_KEYS) if k in PC_KEYS]
    mdir = args.data / "Materials" / "CMB" / "Bike"
    tdir = args.data / "Textures" / "CMB" / "Bike"
    mdir.mkdir(parents=True, exist_ok=True)
    tdir.mkdir(parents=True, exist_ok=True)
    nif = need(args.base, Path("Meshes/CMB/CMB_BikeParked.nif"))
    sc = Scene(args.pynifly, nif)
    report = Report()
    report.append(f"parked nif {nif}")
    report.append(sc.report())
    report.append("options: " + ", ".join(f"{i} {k} \"{NAMES[k]}\" = {' + '.join(STACKS[k])}" for i, k in enumerate(KEYS, 1)))
    report.append("Paint condition: " + ", ".join(f"{i} {k} \"{PC_NAMES[k]}\"" for i, k in enumerate(PC_KEYS, 1)))
    report.append(f"--badge-grime {args.badge_grime}, --tyre-mud {args.tyre_mud}, --rust {args.rust}")
    total = 0
    if keys or pc_keys:
        shapes = make_layers(sc, args.base, keys, report, pc_keys, args.badge_grime, tuple(PARTS) if keys else (),
                             args.rust)
        for key in keys:
            for sh, (ctx, layers) in shapes.items():
                if sh in PARTS:
                    d8, n8, s8 = shape_maps(ctx, _mask(over([layers[n] for n in STACKS[key]]), 1.0 - ctx.shell_cover))
                elif args.badge_grime == GRIME_NEW:
                    # the grime goes over the plates (the shells unit lifts static_wear over them); the weathered layer
                    # (the paint's own damage) stays off them
                    stack = [_plate_haze(ctx, layers[n]) if n == "weathered" and sh in SHAPES else layers[n]
                             for n in STACKS[key]]
                    d8, n8, s8 = shape_maps(ctx, over(stack), clear_plates=False)
                else:
                    d8, n8, s8 = shape_maps(ctx, over([layers[n] for n in STACKS[key]]))
                stem = f"wear_{key}_{sh}"
                total += write_tex(tdir / f"{stem}_d.dds", d8, "bc3", gamma_mips=True)
                total += write_tex(tdir / f"{stem}_n.dds", n8, "bc5", normal=True)
                total += write_tex(tdir / f"{stem}_s.dds", s8, "bc5")
                a = d8[..., 3][_down(ctx.g.cov.astype(float), WORK) > 0] / 255.0
                report.append(f"{stem}: cover mean {a.mean():.3f}, texels over 0.5 {(a > 0.5).mean():.3f}")
                for worn in ("", "_worn"):
                    tpl = B.read(need(args.base, Path("Materials/CMB/Bike") / f"{_label(sh)}{worn}.bgsm"))
                    B.write(mdir / f"{stem}{worn}.bgsm", wear_material(tpl, key, sh, depth=args.overlay_depth))
        for key in pc_keys:
            for sh, (ctx, layers) in shapes.items():
                if sh not in SHAPES:
                    continue                             # Paint condition is the paint's only
                # over a plate's ends (its shell above the plate) only the sun haze: a clean patch would show through the
                # plate's clear parts; a scratch, chip or primer patch there would lie over the badge's art
                stack = [_plate_haze(ctx, layers[n], ctx.plate_low) for n in PC_STACKS[key]]
                d8, n8, s8 = shape_maps(ctx, over(stack), clear_plates=False)
                stem = f"paintwear_{key}_{sh}"
                total += write_tex(tdir / f"{stem}_d.dds", d8, "bc3", gamma_mips=True)
                total += write_tex(tdir / f"{stem}_n.dds", n8, "bc5", normal=True)
                total += write_tex(tdir / f"{stem}_s.dds", s8, "bc5")
                a = d8[..., 3][_down(ctx.g.cov.astype(float), WORK) > 0] / 255.0
                report.append(f"{stem}: cover mean {a.mean():.3f}, texels over 0.5 {(a > 0.5).mean():.3f}")
                for worn in ("", "_worn"):
                    tpl = B.read(need(args.base, Path("Materials/CMB/Bike") / f"{SHAPES[sh]['label']}{worn}.bgsm"))
                    B.write(mdir / f"{stem}{worn}.bgsm", wear_material(tpl, key, sh, "paintwear", args.overlay_depth))
    if not args.only or args.tyres:
        for w in "FR":
            t0 = time.time()
            A, C, rr, covd = tyre_mud(sc, args.base, w, args.tyre_mud)
            for src, suf in TYRES:
                base = W.read_dds(need(args.base, Path("Textures/CMB/Bike") / f"wheel{w}_tyre{src}_d.dds"))[1][0][0][..., :3]
                total += write_tex(tdir / f"wheel{w}_tyre{suf}_d.dds", tyre_diffuse(base, A, C), "bc1", gamma_mips=True)
                for worn in ("", "_worn"):
                    tpl = B.read(need(args.base, Path("Materials/CMB/Bike") / f"wheel{w}_tyre{src}{worn}.bgsm"))
                    B.write(mdir / f"wheel{w}_tyre{suf}{worn}.bgsm", tyre_material(tpl, w, suf))
            report.append(f"wheel{w} tyre mud: cover mean {A[covd].mean():.3f} ({time.time() - t0:.1f} s)")
    print(f"wrote {total} bytes of textures into {args.data} in {time.time() - t_all:.1f} s")
    return 0


# --- check ---------------------------------------------------------------------------------------------------------

class Regions:
    """The check's regions on one shape's map (at the map's own size): {name: mask (size, size)} and the covered mask."""

    def __init__(self, sc, key):
        meta = SHAPES[key]
        g = Grid(sc.shapes[meta["label"]], meta["size"])
        P, N = g.P, g.N
        tank = (P[:, 1] < sc.seat_front + 3.0) if key == "static" else np.zeros(g.n, bool)
        rear = ~tank if key == "static" else np.zeros(g.n, bool)
        front = np.ones(g.n, bool) if key == "fork" else np.zeros(g.n, bool)
        kn = knee_weight(sc, P, N) * tank
        w = sc.wheels["F" if key == "fork" else "R"]
        c = w["c"]
        to_axis = unit(np.stack([np.zeros(g.n), c[1] - P[:, 1], c[2] - P[:, 2]], -1))
        facing = (N * to_axis).sum(1)
        gap = np.hypot(P[:, 1] - c[1], P[:, 2] - c[2]) - w["r"]
        fender = rear | front
        out = fender & (facing < -0.2)
        r = {}
        if key == "static":
            r["tank_top"] = tank & (N[:, 2] > 0.6)
            r["tank_side"] = tank & (np.abs(N[:, 0]) > 0.6) & (kn < 0.2)
            r["tank_under"] = tank & (N[:, 2] < -0.5)
            r["tank_lowfront"] = tank & (N[:, 1] < -0.5) & (P[:, 2] < 76.0)
            r["knee"] = kn > 0.5
            r["near_badge"] = _nearest_dist(P, sc.badge_sets, 6.0) < 2.0
            r["near_plate"] = rear & (_nearest_dist(P, [sc.plate], 12.0) < 8.0)
            fps = [plate_footprint(P, [pl]) for pl in sc.plates]      # each plate's (their minimum: plate_footprint's)
            fp = np.min(fps, axis=0)
            r["on_plates"] = fp < PLATE_CLEAR - 0.15
            rim = _nearest_dist(P, sc.plate_rims, 3.0)
            r["plate_low"] = fp < PC_SHELL - 0.005
            # (since 2026-11-23a) per plate: the band along its outline (0.5 in on the plate, 0.8 out on the paint) and the
            # reference round it (its face's middle, 1.5 in, and the paint 2.0-3.5 out): an outline shows as more grime
            # in the band than in the reference
            self.bands = []
            for name, f_, pr in zip(("TankL", "TankR", "Rear"), fps, sc.plate_rims):
                d = _nearest_dist(P, [pr], 4.0)
                on = f_ < PLATE_CLEAR - 0.15
                self.bands.append((name, g.image(((on & (d < 0.5)) | (~on & (d < 0.8))).astype(float)) > 0.5,
                                   g.image(((on & (d > 1.5)) | (~on & (d > 2.0) & (d < 3.5))).astype(float)) > 0.5))
            r["plate_rim"] = r["on_plates"] & (rim < 0.5)
            r["plate_mid"] = r["on_plates"] & (rim > 1.5)
            rim_v = np.zeros(g.n)
            for (v, _), pr in zip(sc.plates, sc.plate_rims):
                d = _nearest_dist(P, [pr], 3.0)
                zc, hz = float(v[:, 2].mean()), max(float(np.ptp(v[:, 2])) / 2, 0.5)
                rim_v = np.where(d <= rim + 1e-9, np.clip((P[:, 2] - zc) / hz, -1, 1), rim_v)
            r["plate_rim_top"] = r["plate_rim"] & (rim_v > 0.75)
            r["plate_rim_bottom"] = r["plate_rim"] & (rim_v < -0.75)
        pre = "rear" if key == "static" else "front"
        r[f"{pre}_in"] = fender & (facing > 0.3) & (gap < 10.0)
        r[f"{pre}_out"] = out
        z0, z1 = np.percentile(P[out, 2], [35, 65])      # the outside's lower and upper third
        r[f"{pre}_out_low"] = out & (P[:, 2] < z0)
        r[f"{pre}_out_high"] = out & (P[:, 2] > z1)
        self.cov = g.cov
        self.masks = {k: g.image(v.astype(float)) > 0.5 for k, v in r.items()}
        self.g = g


# each option's expectations on the regions' mean cover: (region, op, value or other region, factor)
EXPECT = {
    "weathered": [("knee", ">", "tank_side", 1.5), ("tank_top", ">", "tank_under", 1.5), ("tank_side", ">=", 0.05, 1),
                  ("rear_out", ">=", 0.08, 1), ("front_out", ">=", 0.08, 1), ("tank_top", "<=", 0.7, 1)],
    "dusty": [("tank_top", ">", "tank_under", 1.5), ("tank_top", ">=", 0.25, 1), ("rear_out", ">=", 0.15, 1),
              ("knee", "<", "tank_side", 1.0)],
    "muddy": [("rear_in", ">=", 0.45, 1), ("front_in", ">=", 0.45, 1), ("rear_out_low", ">", "rear_out_high", 2.0),
              ("front_out_low", ">", "front_out_high", 1.5), ("tank_lowfront", ">", "tank_top", 3.0),
              ("tank_top", "<=", 0.08, 1), ("rear_out_low", ">=", 0.15, 1), ("front_out_low", ">=", 0.15, 1)],
    "rusty": [("near_badge", ">", "tank_side", 2.0), ("tank_under", ">", "tank_top", 2.0), ("near_plate", ">", "rear_out_high", 1.3),
              ("tank_under", ">=", 0.3, 1), ("tank_top", "<=", 0.35, 1)],
    "bloody": [("tank_side", ">=", 0.02, 1), ("front_out", ">=", 0.02, 1), ("rear_out", ">=", 0.02, 1),
               ("tank_side", "<=", 0.35, 1), ("tank_under", "<=", 0.2, 1)],
}
# (since 2026-11-23a, --rust 2026-11-23a) Rusty's lighter rust: under the tank and by the number plate, little on the
# tank's top, less than 22a's (no band round the badges: 22a's near_badge expectation gone)
EXPECT_RUST_NEW = [("tank_under", ">", "tank_top", 2.0), ("near_plate", ">", "rear_out_high", 1.3),
                   ("tank_under", ">=", 0.15, 1), ("tank_top", "<=", 0.25, 1), ("static_all", "<=", 0.13, 1)]
RUST_OPAQUE = 0.02           # (since 2026-11-23a) Rusty: at most this share of its rust's texels near opaque (over 0.85)
RUST_INNER_A = 0.6           # (since 2026-11-23a) Rusty: a bloom's middle (3 texels in) this see-through at most
RUST_EDGE_DARK = 0.93        # (since 2026-11-23a) Rusty: a bloom's edge (its outer 2 texels) this dark at most of its middle
OUTLINE_SHARE = 0.2          # (since 2026-11-23a) a plate's outline band: grime over 0.3 on at most this share of it, or
OUTLINE_FACTOR = 1.5         # at most this times the share round it (the middle of its face, the paint further out)
PARTS_OF = {"wasteland": ("weathered", "dusty", "muddy"), "raider": ("rusty", "bloody")}
PC_EXPECT = {   # (since 2026-11-22a) Paint condition's
    "scratched": [("knee", ">", "tank_side", 1.5), ("tank_top", ">", "tank_under", 1.5), ("static_all", "<=", 0.15, 1),
                  ("tank_side", ">=", 0.01, 1)],
    "chipped": [("knee", ">", "tank_side", 2.0), ("front_out", ">=", 0.02, 1), ("static_all", "<=", 0.15, 1),
                ("fork_all", "<=", 0.25, 1)],
    "faded": [("tank_top", ">", "tank_side", 2.0), ("tank_top", ">=", 0.25, 1), ("tank_under", "<=", 0.1, 1)],
    "primer": [("static_all", ">=", 0.02, 1), ("static_all", "<=", 0.2, 1), ("fork_all", ">=", 0.005, 1)],
    "worn": [("tank_top", ">=", 0.25, 1), ("knee", ">=", 0.2, 1)],
}
BUDGETS = {"wear on the paint": 20.0e6, "wear on the parts": 12.0e6, "paint condition": 14.0e6, "tyres": 4.3e6,
           "all": 48.0e6}            # (since 2026-11-22a) bytes of textures per group (BUDGET_WEAR, BUDGET_ALL before)


def _group(rel):
    name = Path(rel).name
    if name.startswith("wheel"):
        return "tyres"
    if name.startswith("paintwear_"):
        return "paint condition"
    return "wear on the parts" if any(f"_{p}_" in name for p in PARTS) else "wear on the paint"


PLATE_MAX = 0.01             # an option's mean cover over the plates' footprints
COMBO_TOL = 20 / 255.0       # BC3's alpha (8 steps between a block's two ends, both maps' errors): a combination's texel
COMBO_SHARE = 0.005          # may sit this under a part's on at most this share of the texels


def _mip_count(w, h):
    return int(math.floor(math.log2(max(w, h)))) + 1


def check(args):
    bad, n_ok = [], 0

    def rep(ok, what, detail=""):
        nonlocal n_ok
        print(f"{'ok  ' if ok else 'FAIL'} {what}" + (f": {detail}" if detail else ""))
        if ok:
            n_ok += 1
        else:
            bad.append(what)
    todo = plan()
    # the files: there, the formats, sizes and mips; nothing else in the tree
    groups = {}
    for rel, spec in sorted(todo.items()):
        p = args.data / rel
        if not p.exists():
            rep(False, rel, "missing")
            continue
        if spec[0] in "dnst":
            info = W.read_dds(p)[0]
            want = (spec[1], spec[2], spec[2], _mip_count(spec[2], spec[2]))
            got = (info["format"], info["w"], info["h"], info["mips"])
            if got != want:
                rep(False, rel, f"{got} not {want}")
            grp = _group(rel)
            groups[grp] = groups.get(grp, 0) + p.stat().st_size
    others = [str(p.relative_to(args.data)) for p in args.data.rglob("*") if p.is_file()
              and str(p.relative_to(args.data)).replace("\\", "/") not in todo]
    rep(not others, f"{len(todo)} files: formats (BC3 _d, BC5 _n/_s, BC1 tyres), sizes and full mip chains; nothing else "
        f"in the tree", "; ".join(others[:6]))
    over_b = [g for g, b in groups.items() if b > BUDGETS[g]] + (["all"] if sum(groups.values()) > BUDGETS["all"] else [])
    rep(not over_b, "the texture budget: " + ", ".join(f"{g} {b / 1e6:.2f} MB (at most {BUDGETS[g] / 1e6:.1f})"
                                                       for g, b in groups.items())
        + f"; all {sum(groups.values()) / 1e6:.2f} MB in {sum(1 for s_ in todo.values() if s_[0] in 'dnst')} textures (at most "
        f"{BUDGETS['all'] / 1e6:.0f})", ", ".join(over_b))
    # the materials: the template's values but the textures and the overlay's flags; every texture they name present
    new_depth = args.overlay_depth == DEPTH_NEW
    flags = dict(alpha=1.0, alpha_blend=1, alpha_blend_src=6, alpha_blend_dst=7, alpha_test=new_depth,
                 zbuffer_write=new_depth, zbuffer_test=True, decal=True, two_sided=False, environment_mapping=False,
                 grayscale_to_palette_color=False, cast_shadows=False, receive_shadows=True, specular_enabled=True,
                 specular_mult=1.0, smoothness=1.0)
    if new_depth:
        flags["alpha_test_ref"] = OVERLAY_TEST
    mbad, named = [], 0
    for rel, spec in sorted(todo.items()):
        if spec[0] not in ("m", "pm", "tm") or not (args.data / rel).exists():
            continue
        m = B.read(args.data / rel)
        name = Path(rel).name
        if spec[0] in ("m", "pm"):
            prefix = "wear" if spec[0] == "m" else "paintwear"
            key = name[len(prefix) + 1:].rsplit("_" + spec[1], 1)[0]
            tpl = B.read(need(args.base, Path("Materials/CMB/Bike") / f"{_label(spec[1])}{spec[2]}.bgsm"))
            want = wear_material(tpl, key, spec[1], prefix, args.overlay_depth)
            for k, v in flags.items():
                if m[k] != v:
                    mbad.append(f"{name} {k} {m[k]}")
        else:
            w, src = spec[1][0], spec[1][1:]
            suf = dict(TYRES)[src]
            tpl = B.read(need(args.base, Path("Materials/CMB/Bike") / f"wheel{w}_tyre{src}{spec[2]}.bgsm"))
            want = tyre_material(tpl, w, suf)
        if B.dumps(m) != B.dumps(want):
            mbad.append(f"{name} differs from the template's plan")
        for slot, t in m["textures"].items():
            if not t:
                continue
            if not t.lower().startswith("cmb\\"):
                continue                                 # the game's own (the tyres' cube): by path in the game
            named += 1
            rel_t = Path("Textures") / t.replace("\\", "/")
            if not (args.data / rel_t).exists() and find(args.base, rel_t) is None:
                mbad.append(f"{name}: {slot} {t} missing")
    rep(not mbad, f"{sum(1 for s in todo.values() if s[0] in ('m', 'pm', 'tm'))} materials files: the shipped paint, part and "
        f"tyre files but the textures and (the overlays') alpha blend, decal, "
        f"{'z write and an alpha test at %d' % OVERLAY_TEST if new_depth else 'no z write'}, one-sided, no shadows, no env "
        f"map, no palette; all {named} of our textures they name present (the game's cube by path)", "; ".join(mbad[:6]))
    nif = need(args.base, Path("Meshes/CMB/CMB_BikeParked.nif"))
    sc = Scene(args.pynifly, nif)
    # one overlay serves every bike: the paint shapes' UVs and triangles alike in the five nifs
    ubad = []
    for nm in NIFS:
        p = find(args.base, Path("Meshes/CMB") / f"{nm}.nif")
        if p is None:
            ubad.append(f"{nm} missing")
            continue
        labs = ("static_paint", "fork_paint") + tuple(PARTS)
        o = load_shapes(args.pynifly, p, labs)
        for lab in labs:
            a, b = sc.shapes[lab], o[lab]
            if a["uv"].shape != b["uv"].shape or not np.array_equal(a["tri"], b["tri"]) or np.abs(a["uv"] - b["uv"]).max() > 1e-6:
                ubad.append(f"{nm} {lab}")
    rep(not ubad, "the five nifs' static_paint, fork_paint and the three parts: the parked nif's UVs and triangles",
        "; ".join(ubad))
    # each option's cover per region
    regions = {k: Regions(sc, k) for k in SHAPES}
    cover = {}
    for key in KEYS:
        cover[key] = {}
        for sh, R in regions.items():
            p = args.data / f"Textures/CMB/Bike/wear_{key}_{sh}_d.dds"
            if not p.exists():
                continue
            a = W.read_dds(p)[1][0][0][..., 3] / 255.0
            cover[key][sh] = a
            cover[key].update({name: float(a[m].mean()) if m.any() else float("nan") for name, m in R.masks.items()})
            cover[key][sh + "_all"] = float(a[R.cov].mean())
            cover[key][sh + "_over"] = float((a[R.cov] > 0.5).mean())
    names = [n for R in regions.values() for n in R.masks]
    print("cover (mean alpha) per region: " + ", ".join(f"{n} {int(sum(m.sum() for R in regions.values() for k, m in R.masks.items() if k == n))}"
                                                        for n in names))
    print(f"  {'':<10}" + "".join(f"{n[:11]:>12}" for n in names + ["static_all", "fork_all"]))
    for key in KEYS:
        if cover[key]:
            print(f"  {key:<10}" + "".join(f"{cover[key].get(n, float('nan')):12.3f}" for n in names + ["static_all", "fork_all"]))
    for key, exp in EXPECT.items():
        if not cover.get(key):
            continue
        if key == "rusty" and args.rust == RUST_NEW:
            exp = EXPECT_RUST_NEW
        fails = []
        for reg, op, ref, fac in exp:
            a = cover[key][reg]
            b = cover[key][ref] * fac if isinstance(ref, str) else ref
            ok = {">": a > b, ">=": a >= b, "<": a < b, "<=": a <= b}[op]
            if not ok:
                fails.append(f"{reg} {a:.3f} {op} {ref if not isinstance(ref, str) else f'{fac:g} x {ref} {b:.3f}'}")
        rep(not fails, f"{key}: cover where the design puts it ({len(exp)} expectations)", "; ".join(fails))
    if args.badge_grime == GRIME_OLD:
        clear = [f"{k} {cover[k]['on_plates']:.3f}" for k in KEYS if cover.get(k) and not cover[k]["on_plates"] <= PLATE_MAX]
        rep(not clear, f"no wear over the tank plates and the rear roundel (the shell runs partly over and partly under "
            f"them): every option's mean cover there at most {PLATE_MAX}", "; ".join(clear))
    else:
        R = regions["static"]
        g_bad = []
        for k in KEYS:
            if not cover.get(k):
                continue
            a = cover[k]["static"]
            on, top, bot, mid = (float(a[R.masks[m_]].mean()) for m_ in ("on_plates", "plate_rim_top", "plate_rim_bottom",
                                                                           "plate_mid"))
            want = {"weathered": on <= 0.5 and mid <= 0.5, "dusty": top > 1.5 * mid and top > bot,
                    "rusty": (bot > 0.1 and bot > 3.0 * top and mid < 0.5 * bot) if args.rust == RUST_OLD else on > 0.005,
                    "bloody": on > 0.005}.get(k, on > 0.005)
            g_bad += [] if want else [f"{k} on {on:.3f} top edge {top:.3f} bottom edge {bot:.3f} middle {mid:.3f}"]
        rep(not g_bad, "the grime over the tank plates and the rear roundel (--badge-grime 2026-11-22a): Weathered's sun "
            "haze only (no chip or scratch) on them, dust along their top edges, " +
            ("rust along their bottom edges (the middles less)" if args.rust == RUST_OLD else
             "rust breaking out by them here and there (--rust 2026-11-23a)") + ", blood and the mixes on them",
            "; ".join(g_bad))
    if args.rust == RUST_NEW:
        # (since 2026-11-23a) no look draws a plate's outline (test 59: Rusty's rust round the Brotherhood plate read as
        # "a rectangle around the frame"): per look and plate, the share of its outline band with grime over 0.3 at most
        # OUTLINE_SHARE or OUTLINE_FACTOR times the share round it
        R = regions["static"]
        o_bad, o_info = [], []
        for k in KEYS:
            if not cover.get(k):
                continue
            a = cover[k]["static"]
            row = []
            for name, band, ref in R.bands:
                so, sr = float((a[band] > 0.3).mean()), float((a[ref] > 0.3).mean())
                row.append(f"{name} {so:.2f}/{sr:.2f}")
                if so > max(OUTLINE_SHARE, OUTLINE_FACTOR * sr):
                    o_bad.append(f"{k} {name} outline {so:.2f} round it {sr:.2f}")
            o_info.append(f"  {k}: " + ", ".join(row))
        rep(not o_bad and bool(o_info), f"no plate's outline drawn by any look: grime over 0.3 on at most {OUTLINE_SHARE} "
            f"of a plate's outline band or {OUTLINE_FACTOR} x the share round it (outline/round per plate)",
            "; ".join(o_bad) + ("\n" + "\n".join(o_info) if o_info else ""))
        # (since 2026-11-23a) Rusty lighter: its blooms see-through (hardly a texel near opaque, the middles at most
        # RUST_INNER_A) and darker at their edges than in their middles, on the paint and the mufflers
        r_bad, r_info = [], []
        for sh in ("static", "fork", "static_exhaust"):
            p = args.data / f"Textures/CMB/Bike/wear_rusty_{sh}_d.dds"
            if not p.exists():
                continue
            img = W.read_dds(p)[1][0][0].astype(np.float64) / 255.0
            a = img[..., 3]
            lum = img[..., :3] @ np.array([0.2126, 0.7152, 0.0722])
            patch = a > 0.25
            e2, e3 = _erode(patch, 2), _erode(patch, 3)
            edge, mid = patch & ~e2, e3
            opq = float((a > 0.85).sum() / max((a > 0.1).sum(), 1))
            ratio = float(lum[edge].mean() / max(lum[mid].mean(), 1e-6)) if mid.any() else 0.0
            am = float(a[mid].mean()) if mid.any() else 0.0
            r_info.append(f"  {sh}: near opaque {opq:.3f}, middles' alpha {am:.2f}, edge / middle brightness {ratio:.2f}")
            if not (opq <= RUST_OPAQUE and am <= RUST_INNER_A and ratio <= RUST_EDGE_DARK and edge.sum() > 1000):
                r_bad.append(sh)
        rep(not r_bad and bool(r_info), f"Rusty lighter (--rust 2026-11-23a): at most {RUST_OPAQUE} of its texels near opaque, "
            f"its blooms' middles at most {RUST_INNER_A} and their edges at most {RUST_EDGE_DARK} x as bright",
            "; ".join(r_bad) + ("\n" + "\n".join(r_info) if r_info else ""))
    # Paint condition: its cover per region, off the plates, Worn at least each of its parts
    pcov = {}
    for key in PC_KEYS:
        pcov[key] = {}
        for sh, R in regions.items():
            p = args.data / f"Textures/CMB/Bike/paintwear_{key}_{sh}_d.dds"
            if p.exists():
                a = W.read_dds(p)[1][0][0][..., 3] / 255.0
                pcov[key][sh] = a
                pcov[key].update({name: float(a[m].mean()) if m.any() else float("nan") for name, m in R.masks.items()})
                pcov[key][sh + "_all"] = float(a[R.cov].mean())
    print(f"  {'':<10}" + "".join(f"{n[:11]:>12}" for n in names + ["static_all", "fork_all"]))
    for key in PC_KEYS:
        if pcov[key]:
            print(f"  {key:<10}" + "".join(f"{pcov[key].get(n, float('nan')):12.3f}" for n in names + ["static_all", "fork_all"]))
    for key, exp in PC_EXPECT.items():
        if not pcov.get(key):
            continue
        fails = []
        for reg, op, ref, fac in exp:
            a = pcov[key][reg]
            b = pcov[key][ref] * fac if isinstance(ref, str) else ref
            if not {">": a > b, ">=": a >= b, "<": a < b, "<=": a <= b}[op]:
                fails.append(f"{reg} {a:.3f} {op} {ref if not isinstance(ref, str) else f'{fac:g} x {ref} {b:.3f}'}")
        rep(not fails, f"Paint condition {key}: cover where the design puts it ({len(exp)} expectations)", "; ".join(fails))
    pclear = [f"{k} {pcov[k]['plate_low']:.3f}" for k in PC_KEYS if pcov.get(k) and not
              pcov[k]["plate_low"] <= (PLATE_MAX if k in ("scratched", "chipped", "primer") else 0.55)]
    rep(not pclear, f"Paint condition where its shell lies over a tank plate or the roundel (the plate under {PC_SHELL} over "
        f"the paint: the plates' ends): only the sun haze (Sun-faded, Worn), no scratch, chip or primer (at most "
        f"{PLATE_MAX}); elsewhere under a plate it shows through the badge's clear parts", "; ".join(pclear))
    if all(pcov.get(k) for k in ("worn", "scratched", "chipped", "faded")):
        worst = []
        for sh in SHAPES:
            under = np.max([pcov[p_][sh] for p_ in ("scratched", "chipped", "faded")], axis=0) - pcov["worn"][sh]
            m = regions[sh].cov
            worst.append(f"{sh} {(under[m] > COMBO_TOL).mean() * 100:.2f} % under" +
                         (" (too many)" if (under[m] > COMBO_TOL).mean() > COMBO_SHARE else ""))
        rep(not any("too many" in x for x in worst), "Paint condition worn: at least each of scratched, chipped, faded",
            "; ".join(worst))
    # the parts: the Wear where it belongs on each
    part_bad, part_info = [], []
    for lab, meta in PARTS.items():
        g = Grid(sc.shapes[meta["label"]], meta["size"])
        shell = sc.part_shells.get(f"{lab}_wear")
        if shell is not None:                      # measured where the part's shell lies (only there is it drawn)
            tid, _ = raster(shell["uv"][shell["tri"]], g.size, g.size)
            g.cov = g.cov & (tid >= 0)
        Pz = g.image(g.P[:, 2], np.nan)
        z0, z1 = np.nanpercentile(Pz[g.cov], [30, 70])
        low, high = g.cov & (Pz < z0), g.cov & (Pz > z1)
        cv = {}
        for key in KEYS:
            p = args.data / f"Textures/CMB/Bike/wear_{key}_{lab}_d.dds"
            if p.exists():
                a = W.read_dds(p)[1][0][0][..., 3] / 255.0
                cv[key] = (float(a[g.cov].mean()), float(a[low].mean()), float(a[high].mean()), a)
        if len(cv) < len(KEYS):
            continue
        part_info.append(f"{lab}: " + ", ".join(f"{k} {v[0]:.2f} (low {v[1]:.2f} high {v[2]:.2f})" for k, v in cv.items()))
        if not (cv["muddy"][1] > 1.5 * cv["muddy"][2] and cv["muddy"][0] > 0.03):
            part_bad.append(f"{lab} muddy not low")
        if not (cv["dusty"][0] > 0.05 and cv["rusty"][0] > (0.03 if args.rust == RUST_OLD else 0.012)
                and cv["weathered"][0] > 0.05):
            part_bad.append(f"{lab} dusty/rusty/weathered too faint")
        for combo, parts in PARTS_OF.items():
            under = np.max([cv[p_][3] for p_ in parts], axis=0) - cv[combo][3]
            if (under[g.cov] > COMBO_TOL).mean() > COMBO_SHARE:
                part_bad.append(f"{lab} {combo} under its parts")
        if lab == "static_exhaust":
            port = np.full(g.n, 99.0)
            for piece in _pieces(sc.shapes[lab]["v"], sc.shapes[lab]["tri"]):
                vs = sc.shapes[lab]["v"][np.unique(sc.shapes[lab]["tri"][piece])]
                if np.ptp(vs[:, 2]) > 20.0:
                    port = np.minimum(port, np.linalg.norm(g.P - vs[vs[:, 2] > vs[:, 2].max() - 1.2].mean(0), axis=1))
            hot = g.image(port, 99.0)
            a = cv["weathered"][3]
            near, far = g.cov & (hot < 6.0), g.cov & (hot > 25.0)
            part_info.append(f"  the pipes' heat colour: weathered cover by the ports {a[near].mean():.2f}, far down {a[far].mean():.2f}")
            if not a[near].mean() > 2.0 * a[far].mean():
                part_bad.append("static_exhaust: no heat colour by the ports")
    rep(not part_bad and bool(part_info), "the Wear on the parts: mud low down, dust, rust and weathering on each, the "
        "pipes' heat colour by their ports, the mixes at least their parts", "; ".join(part_bad)
        + ("\n    " + "\n    ".join(part_info) if part_info else ""))
    for key, parts in PARTS_OF.items():
        if not cover.get(key) or not all(cover.get(p) for p in parts):
            continue
        worst = []
        for sh in SHAPES:
            under = np.max([cover[p][sh] for p in parts], axis=0) - cover[key][sh]
            m = regions[sh].cov
            worst.append(f"{sh} {(under[m] > COMBO_TOL).mean() * 100:.2f} % of texels under, the most {under[m].max():.3f}")
            if (under[m] > COMBO_TOL).mean() > COMBO_SHARE:
                worst[-1] += " (too many)"
        rep(not any("too many" in x for x in worst), f"{key}: at least each of {', '.join(parts)} (within {COMBO_TOL:.3f})",
            "; ".join(worst))
    # the muddy tyres: mud by radius (the tread over the inner sidewall), the bands still under it in part
    tbad, tinfo = [], []
    for w in "FR":
        wh = sc.wheels[w]
        g = Grid(sc.shapes[f"wheel{w}_tyre"], TYRE_SIZE)
        r = g.image(np.hypot(g.P[:, 1] - wh["c"][1], g.P[:, 2] - wh["c"][2]), -1.0)
        base = W.read_dds(need(args.base, Path("Textures/CMB/Bike") / f"wheel{w}_tyre_d.dds"))[1][0][0][..., :3] / 255.0
        p = args.data / f"Textures/CMB/Bike/wheel{w}_tyre_mud_d.dds"
        if not p.exists():
            continue
        mud = W.read_dds(p)[1][0][0][..., :3] / 255.0
        dl = LP.lum(LP.lin(mud)) - LP.lum(LP.lin(base))
        changed = np.abs(mud - base).max(-1) > 12 / 255.0
        R = wh["r"]
        tread = g.cov & (r > R - 1.0)
        inner = g.cov & (r > 22.5) & (r < R - 6.0)
        ct, ci = changed[tread].mean(), changed[inner].mean()
        if args.tyre_mud == TREAD_OLD:
            tinfo.append(f"wheel{w}: texels muddied: tread {ct:.2f}, inner sidewall {ci:.2f}, lighter on average "
                         f"{dl[g.cov].mean():+.4f}")
            if not (ct > 0.45 and ct > 1.5 * ci and dl[tread].mean() > 0):
                tbad.append(f"wheel{w}")
        else:
            rad = np.stack([np.zeros(g.n), g.P[:, 1] - wh["c"][1], g.P[:, 2] - wh["c"][2]], -1)
            nr = g.image((g.N * unit(rad)).sum(1), 0.0)
            crown = g.cov & (r > R - 0.5) & (nr > 0.9)
            walls = g.cov & (r > R - 3.2) & (nr < 0.45)
            cc, cw = changed[crown].mean(), changed[walls].mean()
            tinfo.append(f"wheel{w}: texels muddied: the faces that meet the road {cc:.2f}, the grooves and walls {cw:.2f}, "
                         f"the inner sidewall {ci:.2f}")
            if not (cc < 0.25 and cw > 0.4 and cw > 2.0 * cc):
                tbad.append(f"wheel{w}")
        for src, suf in TYRES[1:]:
            b2 = W.read_dds(need(args.base, Path("Textures/CMB/Bike") / f"wheel{w}_tyre{src}_d.dds"))[1][0][0][..., :3] / 255.0
            m2 = W.read_dds(args.data / f"Textures/CMB/Bike/wheel{w}_tyre{suf}_d.dds")[1][0][0][..., :3] / 255.0
            band = g.cov & (np.abs(b2 - base).max(-1) > 0.2)
            seen = (np.abs(m2 - b2).max(-1) < 12 / 255.0)[band].mean() if band.any() else 0.0
            same_mud = np.abs(m2 - mud).max(-1)[g.cov & ~band].mean()
            tinfo.append(f"  {suf}: its band {band.sum()} texels, {seen:.2f} of them clean; elsewhere {same_mud * 255:.1f}/255 from the black's")
            if not (band.any() and 0.15 < seen < 0.95 and same_mud < 3 / 255.0):
                tbad.append(f"wheel{w}{suf}")
    rep(not tbad, ("the muddy tyres: the tread caked, the inner sidewall less" if args.tyre_mud == TREAD_OLD else
                   "the muddy tyres: the tread's faces clean, the mud in its grooves and walls") +
        ", the bands partly clean, the same mud on each variant", "; ".join(tbad) + ("\n    " + "\n    ".join(tinfo) if tinfo else ""))
    print(f"look_wear --check: {n_ok} passed, {len(bad)} failed" + (": " + ", ".join(bad) if bad else ""))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, required=True, help="the Data tree to write (Materials, Textures)")
    ap.add_argument("--base", type=Path, action="append", required=True,
                    help="the asset base's Data (read only; repeat: later folders over earlier ones)")
    ap.add_argument("--pynifly", type=Path, required=True, help="PyNifly's io_scene_nifly (the parked nif's shapes)")
    ap.add_argument("--only", type=lambda s: [k for k in s.split(",") if k],
                    help="build only these keys, `tyres` for the muddy tyres (a work aid: --check wants them all)")
    ap.add_argument("--tyres", action="store_true", help="with --only: the muddy tyres too")
    ap.add_argument("--check", action="store_true", help="check a built tree (and nothing written)")
    ap.add_argument("--badge-grime", choices=(GRIME_NEW, GRIME_OLD), default=GRIME_NEW,
                    help="(since 2026-11-22a) the Wear's grime over the tank plates and the rear roundel: 2026-11-22a (the "
                         "default) dust, mud, blood and a rust ring at the plate's edge over them (the shells unit lifts "
                         "static_wear over the plates), the weathered layer kept off; 2026-11-21a every layer kept off "
                         "(2026-11-21a's 42 wear maps byte for byte); --check holds the tree to the same")
    ap.add_argument("--overlay-depth", choices=(DEPTH_NEW, DEPTH_OLD), default=DEPTH_NEW,
                    help="(since 2026-11-22a) the overlays' depth: 2026-11-22a (the default) z write on and an alpha test at "
                         f"{OVERLAY_TEST} besides the blend (two blended shells the game can't sort); 2026-11-21a no z write, no "
                         "test (2026-11-21a's 28 wear materials byte for byte)")
    ap.add_argument("--tyre-mud", choices=(TREAD_NEW, TREAD_OLD), default=TREAD_NEW,
                    help="(since 2026-11-22a) the muddy tyres' tread: 2026-11-22a (the default) mud in the grooves and on "
                         "the shoulders, the faces that meet the road clean; 2026-11-21a the whole tread caked (2026-11-21a's "
                         "six tyre diffuses byte for byte); --check holds the tree to the same")
    ap.add_argument("--rust", choices=(RUST_NEW, RUST_OLD), default=RUST_NEW,
                    help="(since 2026-11-23a) Rusty's rust (Raider's too) on the paint and the parts: 2026-11-23a (the "
                         "default) lighter: fewer, smaller blooms, see-through in the middle and dark at the edge, browner, "
                         "fainter streaks, nothing along a plate's outline (a few blooms by each plate at random places); "
                         "2026-11-22a: 2026-11-22a's rust (with its band round the badges and ring along the plates' bottom "
                         "edges) and the 2026-11-22a files byte for byte; --check holds the tree to the same")
    args = ap.parse_args()
    if args.only and "tyres" in args.only:
        args.only = [k for k in args.only if k != "tyres"] or ["-"]
        args.tyres = True
    if args.only:
        bad = [k for k in args.only if k not in KEYS + PC_KEYS and k != "-"]
        if bad:
            ap.error(f"--only: no key {', '.join(bad)} ({', '.join(KEYS)})")
    if any(args.data.resolve() == b.resolve() for b in args.base):
        ap.error("--data must not be a --base (the base is read only)")
    return check(args) if args.check else build(args)


if __name__ == "__main__":
    sys.exit(main())
