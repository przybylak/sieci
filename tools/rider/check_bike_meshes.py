#!/usr/bin/env python3
"""Checks a bike build (harley_meshes.py's nifs, and the texture stage's textures and materials) in a Data tree.

  python check_bike_meshes.py --pynifly <io_scene_nifly> --data <Data> [--reference <27c Data>/Meshes/CMB]
      [--stage-dir <stage>] [--look-reference <the previous build's Data>] [--look-options <look_options.json>]
      [--look-targets art|all] [--look-c2] [--look-c3] [--knees <the riding clips' folder>] [--ground-field <badges.json>]

What it checks (FAIL lines make the exit status 1; INFO lines are numbers for the notes):
  shapes     every worn nif has the 30 shapes of harley_meshes.LABELS (the stage's, with --stage-dir: 28 with --disc
             model), named <stem>_<label>, in that order, skinned; the parked nif the vanilla shape (hidden) and ours
             but the lit overlays (WORN_ONLY), the under-bar mirror variants hidden by the node flag; at most MAX_VERTS
             vertices a shape; every UV in 0..1
  view       CMB_BikeView.nif (the bike in first person, since the 2026-11-01a build): the worn shapes named
             CMB_BikeView_<label>, unskinned, under the NiNode CMB_BikeView (hidden by its flag bit 0), no collision
             block, every vertex the worn nif's (the parked nif's turned round, to 1e-4; the worn nif's half floats to
             their rounding), the worn nif's materials files
  shaders    Fallout 4's flag bits only (no 0x100 in the first word, no 0x8000 in the second), smoothness 0..1, no
             root material, Skinned on the worn shapes only
  materials  the shader names all empty (--bgsm 0) or all Materials\\CMB\\Bike\\<mat>[_worn].bgsm, each file there
             and read back by PyNifly's reader, its textures, environment map, glow map, emissive, two-sidedness and
             shadow the same as the nif's own block; no file there that no nif names
  textures   every texture the nifs and materials name is in the Data tree (the vanilla cube maps excepted), each a
             DDS of the format its suffix wants (_d BC1/BC3, _n and _s BC5, _g BC1, cube maps flagged), with every
             mip level (the fallback palette excepted), no BC7; the total size and count of Textures/CMB/Bike (the
             budget, TEX_BUDGET); our mirror cubes (mirror_cube_e and mirror_cube_zup_e, the one-file swap) both
             there if a materials file names ours (MR), else neither (since 2026-11-02a the mirrors name the game's,
             MB, and the main Data ships no cube of ours); with --stage-dir, the mirror glass's texels of each
             mirror's _d a mid grey (mean 90-140 sRGB: the game tints the cube by it, test 47's near-black glass
             showed black)
  look       (2026-11-02a, test 48) the mirrors' six materials files name the game's cube MetalBrushed02Cube_e at env
             2.0; (2026-11-06a, test 49) the chrome's eight (CHROME_MATS, parked and worn) env 2.5, spec mult 1.5,
             screen-space reflections off, and the wheels' eight (WHEEL_MATS: the rims and discs, parked and worn; the
             rear disc's own files over the front's textures) env 0.25, spec mult 0.75; with --look-reference (the
             2026-11-02a build's Data), the chrome's and the wheels' _d/_n/_s the reference's byte for byte (the look is
             the materials files' alone, and the stage is the reference's)
  custom     (2026-11-07a, the customisation build: harley_meshes.py --look-slots 1, found by the fender patch in the
             nifs; --look-options demands it) 33 shapes: static_badgeTankL/TankR/Rear and static_badgeFender in the worn,
             parked and view nifs, each naming its own materials file and the plugin's fixed role by name; the parked
             nif's under-bar mirrors (PARKED_OFF) not hidden, naming <label>_off.bgsm; the invisible materials files
             (the patch's own, the _off ones, off.bgsm: alpha test 255, alpha 0, no shadow); the patch at least 0.25
             over the paint at every vertex in the worn nif's half floats; every MSWP source and target of
             look_options.json in Materials (the art unit's badge_*.bgsm listed, --look-targets all to demand them),
             their textures checked as the nifs' are (the game's badge art by path aside), the palette one mip; no
             real-world brand in the option table's names; with --look-reference (2026-11-06a's Data) CMB_BikeParts.ini
             and CMB_BikeFit.json its bytes and the three split badges together its static_badge (every vertex with
             its UV, each split shape its culling sphere); the texture budget TEX_BUDGET_LOOK
  c2         (2026-11-08a, the second customisation build: harley_meshes.py --look-rims 1 --look-plate 1, found by the
             plate's text overlay or a rim style in the worn nif; --look-c2 demands it) 49 shapes in the worn and view nifs
             (46 in the parked); static_plate glTF mesh 24's 316 triangles and, with --c2-reference (2026-11-07a's
             Data), static_black and static_plate together 2026-11-07a's static_black (triangle multisets of the worn
             nif's half-float positions) with its culling sphere, CMB_BikeParts.ini and CMB_BikeFit.json its bytes; the plate's rear face read true from behind (u to the
             viewer's right, v down, 0..1); static_plateText at least 0.25 over the face in the worn nif's half floats,
             0.4 inside its outline, its UVs 0..1; every rim style (the parked nif's full precision about the parts file's
             axles) inside bike_pieces.RIM_ENVELOPE below the hoop's top and the stock hoop's outline above it, its
             culling sphere within 1.0 of its axle, 0.3 clear of its wheel's disc and (with --stage-dir) the belt
             pulley; the new shapes' own materials files (the rim styles' and the text overlay's invisible, static_plate's
             naming static_plate_d/_n/_s); every MSWP source and target of the option table in Materials (art-wheels' and
             art-plates' listed until the merge, --look-targets all to demand them); the texture budget TEX_BUDGET_C2.
             static_plate's edges and front face lie on the design cell's strip (v 1.04-1.06: bike_pieces.PLATE_STRIP_V),
             the one UV allowed past 1
  shadows    (2026-11-10a, test 52's wish: the front wheel's shadow; test 34's "no shadow from the front end" dropped)
             in the worn and view nifs each shape casts as the parked nif's same label (an under-bar mirror the parked
             nif draws with its _off file: as its own parked materials file, the one a swap shows), the lit overlays
             (WORN_ONLY) and the decals (the plate's text, the fender patch) none; every _worn materials file in
             Materials\\CMB\\Bike casts as its parked twin (a lit overlay's, with none: no shadow), and the front rims'
             finishes (rimF_*_worn, castF_*_worn) cast
  overlays   the dial's backlight, the needle and the light shells clear of what they cover in the worn nif's half
             floats; the needle's culling sphere on NeedlePoint and long enough; where the needle points at rest
  mirrors    every mirror variant clear of the tank with the bars anywhere within BarAngle
  parts      CMB_BikeParts.ini: every key of the reference's the same but FrontMinY (reported), the Needle keys
             there; CMB_BikeFit.json the same bytes as the reference's
  brand      no brand name in any output (the model's credit in CMB_BikeFit.json excepted)
  totals     each shape's vertices and triangles; triangles per material against the reference's (its palette
             UVs say each one's material), with --stage-dir (or the fallback build's palette) split into the model's
             and ours: the model's must equal the reference's but for glTF mesh 9 (the dial face, 24 tex1) and, with
             --stage-dir, the pieces the volume guard cut again and the disc plates ours replaced (the manifest's
             volume_guard and disc_replaced, printed)
  volumes    (--stage-dir) no closed piece of the model keeps under 0.6 of its volume after the cut (the manifest's
             volumes; the volume guard since the 2026-11-01a build)
  discs      (--stage-dir, --disc ours) each of our discs in the replaced plate's x range and at its outer radius
             about the axle, within 0.05 (the parked nif's full-precision vertices); since 2026-11-02a its bore at
             bike_pieces.DISC_HUB_REF of the outer radius (within 0.005, inside the bolt heads: the manifest's r_hub),
             where the art paints it, and the disc _d's face ring just outside the bore the carrier's colour (within
             10 sRGB of DISC_CARRIER; the 2026-11-01a build's art had the bore's wall colour there on the front disc)
  clamp      the lower triple clamp's box: its vertices in front_black now, in the fixed shapes in the reference
  cables     (2026-11-15b, bar_cables.py, test 53's wish (c): the right-hand cables floated) no piece of a fixed shape hangs
             from the bars (bar_cables.find_bar_cables on the view nif's full-precision positions, else the worn nif's:
             a long thin piece with a bar end 0.5 or nearer to the bar assembly and 12 or more from the steering axis);
             with the split's shape front_cables (in the worn and view nifs, not the parked: the plugin never turns the
             parked bike's bars): the plugin's bar assembly by its name and by its culling sphere, static_black's
             materials file, every corner one of static_black's vertices (position, UV and normal: its UVs on
             static_black's atlas), the cut where it meets static_black's kept triangles at most CUT_R from the steering
             axis (the gap a turn opens there), and the tank clear of it with the bars within BarAngle
  c3         (2026-11-16a, look_emblems.py, the 3D helmets; found by the shapes in the worn nif, --look-c3 demands them) the
             four shapes static_helmEnclaveL/R and static_helmBosL/R last in every nif (51 parked, 54 worn and view: the
             plugin's 55 of MAX_SKINS 64), each naming its own materials file (<shape>.bgsm parked, <shape>_worn.bgsm the
             others), skinned in the worn nifs only, shown by the node flag, an alpha property each; their 8 own files
             invisible (alpha test 255, alpha 0, no shadow, off_d/_n/_s, no cube): hidden until a tank option swaps them;
             helm_enclave.bgsm and helm_bos.bgsm as the table's emblems.items (the glow over helms_g with no cube; the
             chrome cube at 0.8); on the parked nif (full precision) each helmet at most EMBLEM_MAX_VERTS vertices and
             EMBLEM_TRIS triangles, SKIRT..HEIGHT_MAX over its plate (cast along the plate's normal onto it), every vertex
             EMBLEM_FIELD_INSET inside its ground's enamel field (unit B's, the area both plates show, inside the chrome
             bevel: emblem_pieces.GROUND_FIELD_UV or --ground-field's badges.json, mapped through the plate's UVs) and
             inside the plate's outline inset EMBLEM_INSET, no outward-facing vertex over the plate within EMBLEM_PAINT of the paint (the walls'
             foot and the skirt go through: the plate is 0.03-0.5 over the paint under them), clear of every other shape
             (its plate and the other helmet on it, its alternative, aside); the bar assembly (front_*, fork_*, the
             under-bar mirrors among them) turned within BarAngle at least EMBLEM_BARS clear of them (the view nif); with --knees the rider's legs in every
             riding clip (the package's CMB_Rider and Female: the leg bones through PyNifly's skeleton.nif, in the bike's
             frame by CMB_RiderSeat.json) against each helmet and, for comparison, its plate (an estimated LEG_RADIUS of
             flesh round the bones; no body mesh here); the budget TEX_BUDGET_C3
  c4         (2026-11-21a, look_shells.py, art build B; found by the shapes in the worn nif, --look-c4 demands them) the
             three shapes static_wear, fork_wear and fork_badgeFront last in every nif (54 parked, 57 worn and view: the
             plugin's 58 of MAX_SKINS 64, the first-person bike's 57 of VIEW_SHAPES 64), each naming its own materials file,
             skinned in the worn nifs only (one bone, its source's: the culling sphere's centre its source's and round its
             vertices), shown by the node flag, an alpha property each, no shadow in any nif, the shells one-sided, the patch
             two-sided as the rear patch; the plugin's roles by their names (g_roleTags: static_wear fixed, the two fork_
             ones the lower fork: they turn with the bars and ride the suspension) and by their spheres (RolesByName=0),
             no colour writer's tag at a name's end; the six own files invisible (alpha test 255, alpha 0, no shadow,
             off_d, no cube; the shells' one-sided, the patch's the rear patch's bytes). Each shell, in every nif: every
             vertex one of its source's (the record but the position: UV, normal, tangent, skin), the vertices at one
             source position at one shell position (closed at the hard edges), its triangles its source's, every vertex
             shell_pieces.SHELL_BAND over the source in full precision (parked, view) and C4_BAND_HALF in the worn half
             floats, over its triangles never nearer the source than SHELL_FLOOR, no vertex inside another shape (the
             winding number of every shape but the open sheets, in full precision and in the half floats). The front
             patch: every vertex FRONT_PATCH_LIFT over fork_paint within C4_PATCH_VERTEX, over its triangles within
             C4_PATCH_RANGE (no gap, no poke-through at the mudguard's curvature), every triangle facing out, on the
             crown (C4_CROWN), its UVs the plate rectangle read from in front (u to the bike's left, v toward the
             front); each badge patch (the front and the raised rear one) C4_OVER_WEAR over its wear shell everywhere;
             the bar assembly turned within BarAngle C4_BARS clear of static_wear
"""

import argparse
import json
import math
import struct
import sys
from ctypes import create_string_buffer
from pathlib import Path, PureWindowsPath

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harley_meshes as H  # noqa: E402
import bar_cables as BC  # noqa: E402
import emblem_pieces as EP  # noqa: E402
import shell_pieces as SHP  # noqa: E402
import look_emblems as LE  # noqa: E402
from build_bike_meshes import _block_offsets  # noqa: E402
from nearest import TriangleGrid  # noqa: E402

WORN = ("CMB_BikeWorn", "CMB_BikeWornRider", "CMB_BikeWornRiderF")
BRAND = (b"harley", b"davidson", b"sportster")
VIEW = "CMB_BikeView"   # the view nif's stem, node and shapes' prefix (harley_meshes.VIEW_NODE)
TEX_BUDGET = (93, 89.0)  # Textures/CMB/Bike: files, MB (since the 2026-11-01a build's discs: 2026-10-31a's 90 files, 85.3 MB)
# The customisation build's (2026-11-07a, harley_meshes.py --look-slots 1): look_paint.py's index maps (3.5 MB), palette
# and off's three, and the art's badge atlas (badges_d/_n/_s, 8.4 MB): 99 files and 92.6 MB without the atlas
TEX_BUDGET_LOOK = (104, 102.0)
# The second customisation build's (2026-11-08a, C2: art-wheels' rim atlas, cast maps, tyres and hue palette, art-plates'
# plate atlases, palettes and the stock re-sample): plan t53 2.2's budget; 2026-11-07a's tree keeps TEX_BUDGET_LOOK
TEX_BUDGET_C2 = (124, 125.0)
# 2026-11-16a (C3): 2026-11-15b's 123 files and 118.6 MB, the helmets' four (helms_d/_n/_s/_g, 1.3 MB: unit A) and the
# seat's index map and palette (0.7 MB: unit C); the plates' and badges' atlases keep their sizes (unit B)
TEX_BUDGET_C3 = (130, 125.0)
# 2026-11-21a (art build B): the merged tree's 180 files and 142.1 MB: 2026-11-17a's, the Wear slot's 42 maps and the
# muddy tyres' six diffuses (22.6 MB less the materials: look_wear.py) and the three tinted lenses (look_lamp.py)
TEX_BUDGET_C4 = (182, 145.0)
ART_WHEELS = ("rim", "cast", "wheelf_tyre_", "wheelr_tyre_", "paint_hue", "static_paint_hue", "fork_paint_hue", "paint_p")
ART_PLATES = ("plate_", "text_", "plates_", "static_plate_d", "static_plate_n", "static_plate_s")
LOOK_OPTIONS = Path(__file__).resolve().parent.parent / "esp-generator" / "look_options.json"
# 2026-11-16a (C3): the 3D helmets (look_emblems.py, unit A) and the other units' files that arrive at the merge
C3_LABELS = tuple(label for label, _, _ in EP.SHAPES)
C3_SEAT = ("static_seat_", "seat_p")              # unit C's seat colours (look_seat.py)
C3_BADGES = ("badge_gunskull", "badge_hg_")       # unit B's skull and the helmets' grounds (look_badges.py)
EMBLEM_MAX_VERTS = 6000   # a helmet's vertices at most (c3.md 3.1; MAX_VERTS is the shapes' general limit)
EMBLEM_TRIS = (2500, 3500)
EMBLEM_INSET = 0.3        # the footprint inside the plate's outline inset this much
EMBLEM_FIELD_INSET = 0.1  # every vertex this far inside its ground's enamel field (the build insets the footprint 0.2)
EMBLEM_PAINT = 0.25       # no helmet vertex this near the paint but the wall's foot and the skirt (the overlay rule)
EMBLEM_BARS = 0.3         # the bar assembly turned within BarAngle at least this clear of the helmets (the author's minimum:
                          # the under-bar mirrors cross the right plate 1.3 over it at full lock; the right helmets' relief
                          # is made shallower there, emblem_pieces.MIRROR_CLEAR)
MAX_SKINS = 64            # CMB_Slope.dll's bike shapes (the worn nif's and the main shape)
VIEW_SHAPES = 64          # CMB_Slope.dll's first-person bike's shapes (its ViewRig)
# 2026-11-21a (art build B, look_shells.py): the wear shells and the front fender's badge patch, after every other shape
C4_SHELLS = (("static_wear", "static_paint"), ("fork_wear", "fork_paint"))
C4_PATCH, C4_PATCH_ON = "fork_badgeFront", "fork_paint"
C4_LABELS = tuple(lb for lb, _ in C4_SHELLS) + (C4_PATCH,)
C4_BAND_HALF = (0.297, 0.343)   # the worn nifs' half floats: every shell vertex this far over its source (where their step,
                                # 1/16 past 64 units, leaves no point within SHELL_BAND; the count outside SHELL_BAND reported)
C4_PATCH_VERTEX = (0.02, 0.05)  # the front patch's vertices FRONT_PATCH_LIFT over fork_paint within this (full, half floats)
C4_PATCH_RANGE = (0.40, 0.56)   # ... and over its triangles everywhere (the cast: no poke-through at the curvature, no gap)
C4_OVER_WEAR = 0.08             # each badge patch (front and rear) over its wear shell everywhere, in the half floats too
C4_CROWN = 0.7                  # the front patch on the crown: the mudguard's normal under it within acos(this) of the
                                # direction from the front axle
C4_BARS = 0.05                  # the bar assembly turned within BarAngle at least this clear of static_wear (front_black
                                # passes 0.42 over the tank's paint at full lock: 0.10 over the shell)
LEG_RADIUS = 5.0          # the knee's and the shin's flesh round the leg bones (an estimate: no body mesh here)
# The option table's names are scanned for the brand words above (BRAND: Fallout's own factions and fictional brands
# are fine; the scan keeps real-world names out of the menus)
NAME_BRANDS = tuple(w.decode() for w in BRAND)
# 2026-11-02a's look (test 48): the mirrors on the game's cube (the tester's A/B). 2026-11-06a's (test 49: the chrome "too
# bright, pearly, smudged", the discs and rims "a bit too white"): the chrome env 2.5, spec 1.5, no screen-space
# reflections (2026-11-02a: 6, 2, on), the rims and discs env 0.25, spec 0.75 (0.4, 1), by their materials files alone.
# The 2026-11-02a build's values are the optional MO2 folder "2026-11-02a look (A-B)".
MIRROR_CUBE, MIRROR_ENV = "shared\\cubemaps\\metalbrushed02cube_e.dds", 2.0
CHROME_MATS = ("static_chrome", "static_exhaust", "front_chrome", "fork_chrome")
CHROME_ENV, CHROME_SPEC, CHROME_SSR = 2.5, 1.5, False
WHEEL_MATS = ("wheelF_rim", "wheelR_rim", "wheelF_disc", "wheelR_disc")
WHEEL_ENV, WHEEL_SPEC = 0.25, 0.75
DISC_CARRIER_SRGB = (0x4A, 0x4C, 0x50)   # bike_art.DISC_CARRIER
MIRROR_GLASS_SRGB = (90, 140)   # the mirror glass's mean in its _d (the 2026-11-01a build: 6e7276; 2026-10-31a's 08090a)
PALETTE_27C = ("chrome", "silver", "tex2", "body", "logo_decals", "black_m", "tex1", "material", "leather", "glass",
               "o_glass", "r_glass", "lamp_black", "lamp_led")   # 27c's palette blocks, 8 of 128 wide each
CLAMP_BOX = ((-12.7, 12.7), (65.0, 76.7), (64.1, 72.9))   # worn: the lower triple clamp (glTF mesh 74's piece)
FOURCC_FOR = {"_d": {"DXT1", "DXT5"}, "_n": {"ATI2"}, "_s": {"ATI2"}, "_g": {"DXT1"}, "_e": {"DXT1", "DXT5"}}


class Report:
    def __init__(self):
        self.fails = 0

    def check(self, ok, what, detail=""):
        print(f"{'PASS' if ok else 'FAIL'}  {what}{': ' + detail if detail else ''}")
        self.fails += not ok
        return ok

    @staticmethod
    def info(what, detail=""):
        print(f"INFO  {what}{': ' + detail if detail else ''}")


def files_by_lower(root: Path):
    return {str(p.relative_to(root)).replace("/", "\\").lower(): p for p in root.rglob("*") if p.is_file()} if root.exists() else {}


def dds_header(path: Path):
    """(width, height, mips, format, cube) of a DDS."""
    data = path.read_bytes()[:148]
    if data[:4] != b"DDS ":
        return None
    h, w = struct.unpack_from("<II", data, 12)
    mips = max(1, struct.unpack_from("<I", data, 28)[0])
    pf_flags, fourcc = struct.unpack_from("<I4s", data, 80)
    caps2 = struct.unpack_from("<I", data, 112)[0]
    fmt = fourcc.decode("ascii", "replace") if pf_flags & 0x4 else ("A8R8G8B8" if pf_flags & 0x40 else f"flags{pf_flags:#x}")
    if fmt == "DX10":
        fmt = f"DX10:{struct.unpack_from('<I', data, 128)[0]}"
    return w, h, mips, fmt, bool(caps2 & 0x200)


def nif_texts(data: bytes):
    """A Fallout 4 nif header's text: its first line, the author and script fields, the block types and the string
    table (shape and node names, material names)."""
    i = data.index(b"\n") + 1
    out = [data[:i]]
    i += 9
    nblocks = struct.unpack_from("<I", data, i)[0]
    i += 8
    for _ in range(4):
        out.append(data[i + 1:i + 1 + data[i]])
        i += 1 + data[i]
    ntypes = struct.unpack_from("<H", data, i)[0]
    i += 2
    for _ in range(ntypes):
        n = struct.unpack_from("<I", data, i)[0]
        out.append(data[i + 4:i + 4 + n])
        i += 4 + n
    i += 6 * nblocks
    nstrings = struct.unpack_from("<I", data, i)[0]
    i += 8
    for _ in range(nstrings):
        n = struct.unpack_from("<I", data, i)[0]
        out.append(data[i + 4:i + 4 + n])
        i += 4 + n
    return out


def bc1_level0(path: Path):
    """The first mip level of a BC1 (DXT1) DDS as an (h, w, 3) uint8 array (numpy only: the mirror glass check)."""
    data = path.read_bytes()
    h, w = struct.unpack_from("<II", data, 12)
    blocks = np.frombuffer(data, dtype="<u2", count=(h // 4) * (w // 4) * 4, offset=128).reshape(-1, 4)
    c0, c1 = blocks[:, 0].astype(np.int32), blocks[:, 1].astype(np.int32)
    bits = (blocks[:, 2].astype(np.uint32) | (blocks[:, 3].astype(np.uint32) << 16))

    def rgb565(c):
        return np.stack([((c >> 11) & 31) * 255 // 31, ((c >> 5) & 63) * 255 // 63, (c & 31) * 255 // 31], -1)
    p0, p1 = rgb565(c0), rgb565(c1)
    four = (c0 > c1)[:, None]
    p2 = np.where(four, (2 * p0 + p1) // 3, (p0 + p1) // 2)
    p3 = np.where(four, (p0 + 2 * p1) // 3, 0)
    pal = np.stack([p0, p1, p2, p3], 1)                                  # (n, 4, 3)
    idx = (bits[:, None] >> (2 * np.arange(16, dtype=np.uint32))) & 3    # (n, 16)
    px = np.take_along_axis(pal, idx[..., None].astype(np.int64), axis=1)   # (n, 16, 3)
    img = px.reshape(h // 4, w // 4, 4, 4, 3).transpose(0, 2, 1, 3, 4).reshape(h, w, 3)
    return img.astype(np.uint8)


def bc5_level0(path: Path):
    """The first mip level of a BC5 (ATI2, two BC4 channels: _n and _s) DDS as an (h, w, 2) uint8 array (numpy only:
    the chrome's texture comparison, 2026-11-02a)."""
    data = path.read_bytes()
    h, w = struct.unpack_from("<II", data, 12)
    fourcc = data[84:88]
    off = 128 + (20 if fourcc == b"DX10" else 0)
    blocks = np.frombuffer(data, dtype=np.uint8, count=(h // 4) * (w // 4) * 16, offset=off).reshape(-1, 2, 8)
    chans = []
    for c in range(2):
        b = blocks[:, c, :]
        r0, r1 = b[:, 0].astype(np.int32), b[:, 1].astype(np.int32)
        bits = np.zeros(len(b), dtype=np.uint64)
        for k in range(6):
            bits |= b[:, 2 + k].astype(np.uint64) << np.uint64(8 * k)
        eight = (r0 > r1)[:, None]
        i = np.arange(1, 7)[None, :]
        p8 = ((7 - i) * r0[:, None] + i * r1[:, None]) // 7            # 6 between, of 8
        i5 = np.arange(1, 5)[None, :]
        p6 = ((5 - i5) * r0[:, None] + i5 * r1[:, None]) // 5          # 4 between, then 0 and 255
        p6 = np.concatenate([p6, np.zeros((len(b), 1), np.int32), np.full((len(b), 1), 255, np.int32)], 1)
        pal = np.concatenate([r0[:, None], r1[:, None], np.where(eight, p8, p6)], 1)   # (n, 8)
        idx = ((bits[:, None] >> (np.uint64(3) * np.arange(16, dtype=np.uint64))) & np.uint64(7)).astype(np.int64)
        px = np.take_along_axis(pal, idx, axis=1)                          # (n, 16)
        chans.append(px.reshape(h // 4, w // 4, 4, 4).transpose(0, 2, 1, 3).reshape(h, w))
    return np.stack(chans, -1).astype(np.uint8)


def ini_keys(path: Path):
    out = {}
    for line in path.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith(";"):
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def art_owner(leaf):
    """The art unit whose file a C2 materials or texture file is (2026-11-08a: they arrive at the merge), or None (ours)."""
    low = leaf.lower().split("\\")[-1]
    if low.startswith(("wheelf_rim", "wheelr_rim")):   # the cast rims' and the rim styles' own files: the mesh build's
        return None
    if low.startswith(ART_PLATES):
        return "art-plates"
    if low.startswith(ART_WHEELS):
        return "art-wheels"
    if low.startswith(C3_SEAT) and low not in ("static_seat.bgsm", "static_seat_worn.bgsm", "static_seat_d.dds",
                                               "static_seat_n.dds", "static_seat_s.dds"):
        return "seat (unit C)"
    if low.startswith(C3_BADGES):
        return "art-badges (unit B)"
    return None


def look_checks(rep, args, opts, labels, materials, textures, worn_geo, worn_names, parked_names, parked_flags, P):
    """The customisation build's (2026-11-07a, harley_meshes.py --look-slots 1) shapes and the option table's swaps."""
    import re
    import bgsm as B   # ours (tools/rider/bgsm.py)
    new = H.BADGE_SPLIT + (H.FENDER_BADGE,)
    mat = lambda name: f"materials\\cmb\\bike\\{name}.bgsm".lower()   # noqa: E731
    bad = []
    for label in new:
        if (worn_names.get(label) or "").lower() != mat(label + "_worn"):
            bad.append(f"{label} worn {worn_names.get(label)!r}")
        if (parked_names.get(label) or "").lower() != mat(label):
            bad.append(f"{label} parked {parked_names.get(label)!r}")
        if not ("_static_" in f"_{label}" and not any(t in f"_{label}" for t in ("_fork", "_wheelF", "_wheelR", "_front_", "_rear_"))):
            bad.append(f"{label}: not the plugin's fixed role by its name")
    for label in H.PARKED_OFF:
        if (parked_names.get(label) or "").lower() != mat(label + "_off") or parked_flags.get(label, 1) & 1:
            bad.append(f"{label} parked {parked_names.get(label)!r} flags {parked_flags.get(label)}")
        if (worn_names.get(label) or "").lower() != mat(label + "_worn"):
            bad.append(f"{label} worn {worn_names.get(label)!r}")
    c2_rims, c2_plate = H.RIM_STYLE_LABELS[0][0] in labels, H.PLATE_TEXT in labels
    rep.check(not bad and len([x for x in labels if x not in RIDDEN_ONLY + C3_LABELS + C4_LABELS]) == len(H.look_labels(c2_rims, c2_plate)),
              f"custom: {len(labels)} shapes; {', '.join(new)} in the worn, parked and view nifs (the view's names the worn's), "
              f"each its own materials file and the plugin's fixed role by name; the parked nif's under-bar mirrors "
              f"({', '.join(H.PARKED_OFF)}) not hidden, naming <label>_off.bgsm", "; ".join(bad))
    # the invisible materials files: the fender patch's own (its stock look), the parked mirrors' and the swaps' off
    invisible = [H.FENDER_BADGE, H.FENDER_BADGE + "_worn"] + [x + "_off" for x in H.PARKED_OFF] + \
                [opts["off_material"].split("\\")[-1][:-len(".bgsm")]]
    bad = []
    for name in invisible:
        path = materials.get(mat(name)[len("materials\\"):])
        if path is None:
            bad.append(f"{name}.bgsm missing")
            continue
        m = B.read(path)
        if not (m["alpha_test"] and m["alpha_test_ref"] == 255 and m["alpha"] == 0.0 and not m["cast_shadows"]):
            bad.append(f"{name}: alpha test {m['alpha_test']} ref {m['alpha_test_ref']} alpha {m['alpha']} shadows {m['cast_shadows']}")
    rep.check(not bad, f"custom: {len(invisible)} invisible materials files (alpha test 255, alpha 0, no shadow): "
                       f"{', '.join(invisible)}", "; ".join(bad))
    # the patch over the paint, in the worn nif's half floats
    if H.FENDER_BADGE not in worn_geo or "static_paint" not in worn_geo:
        rep.check(False, f"custom: the rear fender patch over the paint", f"no {H.FENDER_BADGE} in CMB_BikeWorn.nif")
    else:
        pv = worn_geo[H.FENDER_BADGE][0]
        v, f, _ = worn_geo["static_paint"]
        t = v[f]
        c = t[:, :, 1].mean(axis=1)
        t = t[(c > pv[:, 1].min() - 4) & (c < pv[:, 1].max() + 4)]
        g = TriangleGrid(t, 0.6).closest(pv, reach=1.0)[2]
        rep.check(len(t) and g.min() >= 0.25, f"custom: the rear fender patch at least 0.25 over the paint at every one of its "
                                              f"{len(pv)} vertices in the worn nif's half floats",
                  f"{g.min():.3f} to {g.max():.3f}")
    # every MSWP source and target there (the art unit's badge files listed until the merge)
    missing, art, n = set(), set(), 0
    c2_art = {}   # 2026-11-08a: art-wheels' and art-plates' files, until the merge
    for slot in opts["slots"]:
        for o in slot["options"]:
            for pair in o["swap"] or []:
                for x in pair:
                    n += 1
                    if x.replace("/", "\\").lower() in materials:
                        continue
                    leaf = x.split("\\")[-1]
                    owner = art_owner(leaf) if args.look_targets == "art" else None
                    if owner:
                        c2_art.setdefault(owner, set()).add(leaf)
                        continue
                    (art if leaf.lower().startswith("badge_") and args.look_targets == "art" else missing).add(leaf)
    aside = [f"the art unit's {len(art)} badge materials files"] if art else []
    aside += [f"{owner}'s {len(v)}" for owner, v in sorted(c2_art.items())]
    rep.check(not missing, f"custom: the option table's {n} MSWP sources and targets in Materials"
                           + (f" ({', '.join(aside)} aside)" if aside else ""), ", ".join(sorted(missing)[:12]))
    if art:
        rep.info("custom: the art unit's badge materials files not here yet", ", ".join(sorted(art)))
    for owner, v in sorted(c2_art.items()):
        rep.info(f"custom: {owner}'s materials files not here yet (the merge brings them)", f"{len(v)}: " + ", ".join(sorted(v)[:6]) + " ...")
    # the option table's names: no real-world brand
    names = [x.get("name", "") for x in opts["slots"]]
    names += [o.get("name", "") for s in opts["slots"] for o in s["options"]]
    names += [b.get(k) or "" for b in opts["badges"] for k in ("name", "motif")]
    names += [r.get("name", "") for r in opts["paint_rows"]] + [x.get("name", "") for x in opts["sets"]]
    hits = sorted({f"{nm!r}: {w}" for nm in names for w in NAME_BRANDS if re.search(rf"\b{re.escape(w)}\b", nm.lower())})
    rep.check(not hits, f"custom: no real-world brand in the option table's {len(names)} names", "; ".join(hits))
    # with the 2026-11-06a build's Data: the parts and fit files its bytes, the split badges its static_badge
    if args.look_reference:
        rm = args.look_reference / "Meshes" / "CMB"
        diff = [n_ for n_ in ("CMB_BikeParts.ini", "CMB_BikeFit.json")
                if (args.data / "Meshes" / "CMB" / n_).read_bytes() != (rm / n_).read_bytes()]
        rep.check(not diff, "custom: CMB_BikeParts.ini and CMB_BikeFit.json the reference's bytes (--look-reference: the split "
                            "and the patch move no key, FrontMinY included)", ", ".join(diff))
        ref = P.NifFile(str(rm / "CMB_BikeWorn.nif"))
        rs = next((s for s in ref.shapes if s.name == "CMB_BikeWorn_static_badge"), None)
        if rs is None or not all(b in worn_geo for b in H.BADGE_SPLIT):
            rep.check(False, "custom: the three split badges together the reference's static_badge",
                      "no CMB_BikeWorn_static_badge in the reference" if rs is None else "not all three in CMB_BikeWorn.nif")
        else:
            def rows_of(vv, uu):
                a = np.round(np.column_stack([vv, uu]) * 2 ** 20).astype(np.int64)
                return a[np.lexsort(a.T[::-1])]
            ra = rows_of(np.asarray(rs.verts, np.float64), np.asarray(rs.uvs, np.float64))
            na = rows_of(np.vstack([worn_geo[b][0] for b in H.BADGE_SPLIT]), np.vstack([worn_geo[b][2] for b in H.BADGE_SPLIT]))
            tri_n = sum(len(worn_geo[b][1]) for b in H.BADGE_SPLIT)
            data = (args.data / "Meshes" / "CMB" / "CMB_BikeWorn.nif").read_bytes()
            bone = [off for off, nm in _block_offsets(data) if nm == "BSSkin::BoneData"]
            rdata = (rm / "CMB_BikeWorn.nif").read_bytes()
            rbone = [off for off, nm in _block_offsets(rdata) if nm == "BSSkin::BoneData"]
            ref_labels = [s.name[len("CMB_BikeWorn_"):] for s in ref.shapes]
            rsph = rdata[rbone[ref_labels.index("static_badge")] + 4:rbone[ref_labels.index("static_badge")] + 20]
            sph = [data[bone[labels.index(b)] + 4:bone[labels.index(b)] + 20] for b in H.BADGE_SPLIT]
            same = ra.shape == na.shape and np.array_equal(ra, na) and tri_n == len(rs.tris)
            rep.check(same and all(x == rsph for x in sph),
                      "custom: the three split badges together the reference's static_badge (every vertex with its UV, "
                      "the triangles' count) and each its culling sphere",
                      f"{len(na)} vertices, {tri_n} triangles (the reference {len(ra)}, {len(rs.tris)}); spheres "
                      f"{'the same' if all(x == rsph for x in sph) else 'differ'}")


def c2_checks(rep, args, labels, materials, worn_geo, worn_names, parked_geo, parked_names, P):
    """The second customisation build's (2026-11-08a, harley_meshes.py --look-rims 1 --look-plate 1) shapes."""
    import bgsm as B   # ours (tools/rider/bgsm.py)
    import bike_pieces as BP
    meshes = args.data / "Meshes" / "CMB"
    want = [lb for lb, _ in H.look_labels(True, True)]
    built = [x for x in labels if x not in RIDDEN_ONLY + C3_LABELS + C4_LABELS]   # 2026-11-15b's front_cables (bar_cables.py),
    later = [x for x in labels if x in RIDDEN_ONLY + C3_LABELS + C4_LABELS]          # 2026-11-16a's helmets (look_emblems.py) and
    # 2026-11-21a's shells and patch (look_shells.py) aside
    rep.check(built == want, f"c2: {len(built)} shapes in the worn and view nifs, {len([x for x in built if x not in H.WORN_ONLY])} "
                             f"in the parked (49 and 46: 2026-11-07a's 33 and 30, the plate's two, the 14 rim styles)"
                             + (f"; and {', '.join(later)} (bar_cables.py, look_emblems.py, look_shells.py)" if later else ""),
              "" if built == want else f"missing {sorted(set(want) - set(built))}, extra {sorted(set(built) - set(want))}")
    mat = lambda name: f"materials\\cmb\\bike\\{name}.bgsm".lower()   # noqa: E731
    # the new shapes' own materials files: named, the invisible ones invisible, static_plate's over its own textures
    bad = []
    for label, _ in H.C2_LABELS:
        if (worn_names.get(label) or "").lower() != mat(label + "_worn") or (parked_names.get(label) or "").lower() != mat(label):
            bad.append(f"{label}: worn {worn_names.get(label)!r} parked {parked_names.get(label)!r}")
            continue
        for name in (label, label + "_worn"):
            path = materials.get(mat(name)[len("materials\\"):])
            if path is None:
                bad.append(f"{name}.bgsm missing")
                continue
            m = B.read(path)
            if label == H.PLATE_LABEL:
                if m["textures"]["diffuse"].lower() != "cmb\\bike\\static_plate_d.dds" or m["alpha_test"]:
                    bad.append(f"{name}: diffuse {m['textures']['diffuse']}, alpha test {m['alpha_test']}")
            elif not (m["alpha_test"] and m["alpha_test_ref"] == 255 and m["alpha"] == 0.0 and not m["cast_shadows"]
                      and m["textures"]["diffuse"].lower() == "cmb\\bike\\off_d.dds" and bool(m["decal"]) == (label == H.PLATE_TEXT)):
                bad.append(f"{name}: not invisible (alpha test {m['alpha_test']} ref {m['alpha_test_ref']} alpha {m['alpha']} "
                           f"shadows {m['cast_shadows']} decal {m['decal']})")
    rep.check(not bad, f"c2: the 16 new shapes' own materials files: the 14 rim styles' and {H.PLATE_TEXT}'s invisible (alpha test "
                       f"255, alpha 0, no shadow, off's textures; the text's decal), {H.PLATE_LABEL}'s naming static_plate_d/_n/_s",
              "; ".join(bad[:8]))
    if H.PLATE_LABEL not in worn_geo or H.PLATE_TEXT not in worn_geo:
        rep.check(False, "c2: the plate's shapes in CMB_BikeWorn.nif")
        return
    # the plate: glTF mesh 24's 316 triangles; with 2026-11-07a's Data, static_black and static_plate its static_black
    pv, pf, puv = worn_geo[H.PLATE_LABEL]
    rep.check(len(pf) == 316, f"c2: {H.PLATE_LABEL} glTF mesh 24's 316 triangles", f"{len(pf)}")
    if args.c2_reference:
        ref = P.NifFile(str(args.c2_reference / "Meshes" / "CMB" / "CMB_BikeWorn.nif"))
        rs = next((x for x in ref.shapes if x.name == "CMB_BikeWorn_static_black"), None)

        def tri_rows(v, f):   # each triangle its three corners' keys, sorted (the corner order and the winding aside)
            q = np.round(np.asarray(v, np.float64) * 2 ** 12).astype(np.int64) + 2 ** 20   # within 2^21 for |x| < 256
            key = (q[:, 0] << 42) | (q[:, 1] << 21) | q[:, 2]
            t = np.sort(key[np.asarray(f, np.int64)], axis=1)
            return t[np.lexsort(t.T[::-1])]
        if rs is None or "static_black" not in worn_geo:
            rep.check(False, "c2: static_black and static_plate together 2026-11-07a's static_black", "no static_black")
        else:
            bv, bf, _ = worn_geo["static_black"]
            ours = np.vstack([tri_rows(bv, bf), tri_rows(pv, pf)]
                             + [tri_rows(*worn_geo[x][:2]) for x in RIDDEN_ONLY if x in worn_geo])   # 2026-11-15b's cut cables
            ours = ours[np.lexsort(ours.T[::-1])]
            theirs = tri_rows(rs.verts, rs.tris)
            data = (meshes / "CMB_BikeWorn.nif").read_bytes()
            rdata = (args.c2_reference / "Meshes" / "CMB" / "CMB_BikeWorn.nif").read_bytes()
            bone = [off for off, nm in _block_offsets(data) if nm == "BSSkin::BoneData"]
            rbone = [off for off, nm in _block_offsets(rdata) if nm == "BSSkin::BoneData"]
            rl = [x.name[len("CMB_BikeWorn_"):] for x in ref.shapes]
            sph = data[bone[labels.index("static_black")] + 4:bone[labels.index("static_black")] + 20]
            rsph = rdata[rbone[rl.index("static_black")] + 4:rbone[rl.index("static_black")] + 20]
            same = ours.shape == theirs.shape and np.array_equal(ours, theirs)
            rep.check(same and sph == rsph, "c2: static_black and static_plate together 2026-11-07a's static_black (every triangle's "
                                            "half-float corners, as multisets) and static_black its culling sphere",
                      f"{len(bf)} + {len(pf)} triangles (the reference {len(rs.tris)}); "
                      f"{'the same' if same else 'differ'}; sphere {'the same' if sph == rsph else 'differs'}")
    if args.c2_reference:
        rm = args.c2_reference / "Meshes" / "CMB"
        diff = [n_ for n_ in ("CMB_BikeParts.ini", "CMB_BikeFit.json") if (meshes / n_).read_bytes() != (rm / n_).read_bytes()]
        rep.check(not diff, "c2: CMB_BikeParts.ini and CMB_BikeFit.json 2026-11-07a's bytes (--c2-reference: the plate's split and "
                            "the rims move no key, FrontMinY included)", ", ".join(diff))
    # the rear face read true from behind (worn: the rear is -y, the viewer's right from behind +x)
    t = pv[pf]
    fn = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
    cen = t.mean(axis=1)
    face = (np.abs(fn[:, 1]) > BP.PLATE_FACE_DOT) & (cen[:, 1] < 0.5 * (pv[:, 1].min() + pv[:, 1].max()))
    fv, fu = t[face].reshape(-1, 3), puv[pf[face]].reshape(-1, 2)
    A = np.column_stack([fv[:, 0], fv[:, 2], np.ones(len(fv))])
    cu = np.linalg.lstsq(A, fu[:, 0], rcond=None)[0]
    cv = np.linalg.lstsq(A, fu[:, 1], rcond=None)[0]
    rep.check(face.sum() > 0 and cu[0] > 0 and cv[1] < 0 and abs(cu[1]) < 1e-3 and abs(cv[0]) < 1e-3 and fu.min() > -1e-3
              and fu.max() < 1 + 1e-3 and np.ptp(fu[:, 0]) > 0.99 and np.ptp(fu[:, 1]) > 0.99,
              f"c2: the plate's rear face ({int(face.sum())} triangles) read true from behind over 0..1 (u to the viewer's right, "
              f"v down)", f"u = {cu[0]:.4f} x + {cu[1]:.4f} z, v = {cv[0]:.4f} x + {cv[1]:.4f} z")
    # the text overlay: 0.25 over the face in half floats, 0.4 inside its outline, UVs 0..1
    ov, of, ouv = worn_geo[H.PLATE_TEXT]
    g = TriangleGrid(t[face], 0.6).closest(ov, reach=1.0)[2]
    e = np.vstack([pf[face][:, [0, 1]], pf[face][:, [1, 2]], pf[face][:, [2, 0]]])
    es = np.sort(e, axis=1)
    u_, inv, cnt = np.unique(es, axis=0, return_inverse=True, return_counts=True)
    border = u_[cnt == 1]
    a2, b2 = pv[border[:, 0]][:, [0, 2]], pv[border[:, 1]][:, [0, 2]]
    q = ov[:, [0, 2]]
    ab = b2 - a2
    tt = np.clip(np.einsum("pij,ij->pi", q[:, None, :] - a2[None], ab) / np.maximum((ab * ab).sum(1), 1e-12), 0, 1)
    d = np.linalg.norm(q[:, None, :] - (a2[None] + tt[..., None] * ab[None]), axis=2).min(axis=1)
    lo2, hi2 = pv[np.unique(pf[face])][:, [0, 2]].min(0), pv[np.unique(pf[face])][:, [0, 2]].max(0)
    inside = ((q > lo2) & (q < hi2)).all(axis=1)
    rep.check(len(of) == 32 and g.min() >= 0.25 and d.min() >= 0.4 and inside.all() and ouv.min() > -1e-4 and ouv.max() < 1 + 1e-4,
              f"c2: {H.PLATE_TEXT} ({len(of)} triangles) at least 0.25 over the plate's face at every vertex in the worn nif's half "
              f"floats, 0.4 inside its rounded outline, its UVs 0..1", f"{g.min():.3f} to {g.max():.3f} over; {d.min():.2f} inside")
    # the rim styles: the envelope and the hoop (the parked nif, full precision), the spheres, the clearances
    parts = {}
    for line in (meshes / "CMB_BikeParts.ini").read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            parts[k.strip()] = v.strip()
    if (meshes / "CMB_BikeFit.json").exists():
        seat_at = json.loads((meshes / "CMB_BikeFit.json").read_text())["seat_at"]
    else:   # a package's tree (the fit file is a build file, never shipped): the parked nif's turn, from the paint
        seat_at = float(np.median(worn_geo["static_paint"][0][:, 1] + parked_geo["static_paint"][:, 1]))
        rep.info("c2", f"no CMB_BikeFit.json: seat_at {seat_at:.4f} from the paint's vertices, worn against parked")
    data = (meshes / "CMB_BikeWorn.nif").read_bytes()
    bone = [off for off, nm in _block_offsets(data) if nm == "BSSkin::BoneData"]
    pulley = None
    if args.stage_dir and (args.stage_dir / "shapes" / "wheelR_tyre.npz").exists():
        with np.load(args.stage_dir / "shapes" / "wheelR_tyre.npz") as z:
            pulley = z["pos"][z["tri"][z["src"] == 79]]
    bad, worst_sphere, worst_disc, worst_pulley = [], 0.0, 1e9, 1e9
    tol = 0.01   # the parts file's axles are to 0.01
    for label, role in H.RIM_STYLE_LABELS:
        wheel = role[-1]
        ax_w = np.array([float(x) for x in parts["FrontAxle" if wheel == "F" else "RearAxle"].split(",")])
        ax = np.array([-ax_w[0], seat_at - ax_w[1], ax_w[2]])   # parked
        v = parked_geo.get(label)
        if v is None:
            bad.append(f"{label} not in the parked nif")
            continue
        x, r = v[:, 0] - ax[0], np.hypot(v[:, 1] - ax[1], v[:, 2] - ax[2])
        for r0, r1, x0, x1 in BP.RIM_ENVELOPE[wheel]:
            sel = (r >= r0) & (r < r1)
            if sel.any() and (x[sel].min() < x0 - tol or x[sel].max() > x1 + tol):
                bad.append(f"{label}: x {x[sel].min():.2f}..{x[sel].max():.2f} at r {r0}-{r1}")
        prof = np.asarray(BP.RIM_HOOP[wheel])
        hoop = r >= BP.RIM_HOOP_MIN[wheel]
        if r.max() > prof[:, 1].max() + tol or (hoop.any() and np.abs(x[hoop]).max() > np.abs(prof[:, 0]).max() + tol):
            bad.append(f"{label}: past the stock hoop (r {r.max():.3f})")
        c = np.frombuffer(data[bone[labels.index(label)] + 4:bone[labels.index(label)] + 16], "<f4").astype(np.float64)
        worst_sphere = max(worst_sphere, float(np.linalg.norm(c - ax_w)))
        dv, df_, _ = worn_geo[f"wheel{wheel}_disc"]
        dpk = np.column_stack([-dv[:, 0], seat_at - dv[:, 1], dv[:, 2]])
        near = TriangleGrid(dpk[df_], 1.0).closest(v, reach=3.0)[2]
        worst_disc = min(worst_disc, float(near.min()))
        if wheel == "R" and pulley is not None:
            worst_pulley = min(worst_pulley, float(TriangleGrid(pulley, 1.0).closest(v, reach=4.0)[2].min()))
    rep.check(not bad, "c2: every rim style inside bike_pieces.RIM_ENVELOPE below the hoop's top and the stock hoop's outline "
                       "above it (the parked nif about the parts file's axles)", "; ".join(bad[:6]))
    rep.check(worst_sphere <= 1.0, "c2: every rim style's culling sphere within 1.0 of its axle (the 6-unit rule's wheel)",
              f"the worst {worst_sphere:.3f} off")
    rep.check(worst_disc >= 0.3 and (pulley is None or worst_pulley >= 0.3),
              "c2: every rim style 0.3 or more clear of its wheel's brake disc" + (" and the belt pulley (the stage's glTF mesh 79)"
                                                                                    if pulley is not None else ""),
              f"the disc {worst_disc:.2f}" + (f", the pulley {worst_pulley:.2f}" if pulley is not None else " (no --stage-dir: the pulley not checked)"))


SHADOW_OFF56 = H.WORN_ONLY + (H.PLATE_TEXT, H.FENDER_BADGE)   # the lit overlays and the decals: no shadow when ridden
# 2026-11-15b (bar_cables.py): the bars' cables cut out of static_black into front_cables, in the worn and view nifs only
RIDDEN_ONLY = (BC.LABEL,)
SPLIT_FROM = {BC.LABEL: BC.SOURCE}
CUT_R = 10.0         # the cut at most this far from the steering axis: it opens 2 r sin(angle / 2) in a turn (3.5 at 20)
TANK_CLEAR = 0.3     # the moved cables at least this clear of the tank with the bars anywhere within BarAngle


def cable_checks(rep, meshes, labels, worn_geo, parts, tank):
    """2026-11-15b (bar_cables.py; test 53's wish (c), the right-hand cables floating in first person): no fixed piece
    hangs from the bars; the split's front_cables turns with them, on static_black's own texels."""
    sp = np.array([float(x) for x in parts.get("SteerPoint", "0,0,0").split(",")])
    ax = H.unit(np.array([float(x) for x in parts.get("SteerAxis", "0,0,1").split(",")]))
    bar = float(parts.get("BarAngle", "20"))
    # the pieces: on the view nif's full-precision positions (the worn nif's half floats otherwise)
    view = meshes / f"{VIEW}.nif"
    if view.exists():
        nif = BC.Nif(view.read_bytes())
        geo = {nif.name_of(k)[len(VIEW) + 1:]: BC.TriShape(nif.blocks[k]) for k in nif.shapes()}
        geo = {label: (g.positions(), g.tris) for label, g in geo.items()}
        where = f"{VIEW}.nif"
    else:
        geo = {label: (g[0], g[1]) for label, g in worn_geo.items()}
        where = "CMB_BikeWorn.nif"
    bar_tris = np.vstack([v[f] for label, (v, f) in geo.items() if label.startswith("front_")])
    found = []
    for label, (v, f) in geo.items():
        if label.startswith(("static_", "rear_")):
            found += [(label, c) for c in BC.find_bar_cables(v, f, bar_tris, sp, ax, bar, verbose=False, name=label)]
    rep.check(not found, f"cables: no piece of a fixed shape hangs from the bars ({where}: a long thin piece with a bar end "
                         f"{BC.ATTACH:g} or nearer to the bar assembly, {BC.R_END:g} or more from the steering axis)",
              "" if not found else f"{len(found)}: " + "; ".join(f"{label} piece {c['piece']} ({len(c['tris'])} triangles, its bar end on the bike's "
                                            f"{'right' if c['seed_x'] > 0 else 'left'} {c['seed_r'][1]:.1f} from the axis: "
                                            f"it leaves the bars by {c['bar_gap']:.1f} at BarAngle {bar:g})" for label, c in found))
    if BC.LABEL not in labels:
        rep.info("cables", f"no {BC.LABEL} (bar_cables.py not run on these nifs)")
        return
    # the plugin's role by name (CMB_Slope.c g_roleTags: the first tag that fits) and by its sphere (RolesByName=0)
    tags = (("_front_needle", True, "needle"), ("_front_glow", True, "glow"), ("_front_dialglow", True, "glow"),
            ("_rear_tail", True, "tail"), ("_rear_brake", True, "brake"), ("_fork", False, "fork"), ("_wheelF", False, "wheel"),
            ("_wheelR", False, "wheel"), ("_front_mirrorStock", True, "front"), ("_front_mirrorUnderEgg", True, "front"),
            ("_front_mirrorUnderD", True, "front"), ("_front_", False, "front"), ("_static_", False, "fixed"))
    name = f"CMB_BikeWorn_{BC.LABEL}".lower()
    by_name = next((role for tag, end, role in tags if (name.endswith(tag.lower()) if end else tag.lower() in name)), None)
    data = (meshes / "CMB_BikeWorn.nif").read_bytes()
    bone = [off for off, nm in _block_offsets(data) if nm == "BSSkin::BoneData"]
    c = np.array(struct.unpack_from("<4f", data, bone[labels.index(BC.LABEL)] + 4))
    lamp = np.array([float(x) for x in parts.get("LampPoint", "0,0,0").split(",")])
    front_min_y = float(parts.get("FrontMinY", "0"))
    by_sphere = c[1] > front_min_y and not (c[3] < 12.0 and np.linalg.norm(c[:3] - lamp) < 20.0)
    v, f, uv = worn_geo[BC.LABEL]
    held = np.linalg.norm(v - c[:3], axis=1).max() <= c[3]
    rep.check(by_name == "front" and by_sphere and held and len(bone) == len(labels),
              f"cables: {BC.LABEL} the plugin's bar assembly by its name (RolesByName=1) and by its culling sphere "
              f"(RolesByName=0: ahead of FrontMinY {front_min_y:g}, not the lamp's), the sphere round its vertices",
              f"by its name {by_name}; its sphere ({c[0]:.1f}, {c[1]:.1f}, {c[2]:.1f}) r {c[3]:.1f}")
    # static_black's own vertices (position, UV, normal) and materials file: its texels on static_black's atlas
    files_ok = True
    detail = []
    for stem in ("CMB_BikeWorn", VIEW):
        path = meshes / f"{stem}.nif"
        if not path.exists():
            continue
        nif = BC.Nif(path.read_bytes())
        ks, kn = nif.shape_named(f"{stem}_{BC.SOURCE}"), nif.shape_named(f"{stem}_{BC.LABEL}")
        if ks is None or kn is None:
            files_ok = False
            detail.append(f"{stem}: the shapes missing")
            continue
        src, new = BC.TriShape(nif.blocks[ks]), BC.TriShape(nif.blocks[kn])
        mat_s = nif.strings[struct.unpack_from("<i", nif.blocks[src.shader], 4)[0]]
        mat_n = nif.strings[struct.unpack_from("<i", nif.blocks[new.shader], 4)[0]]
        uvo, no = ((src.desc >> 8) & 0xF) * 4, ((src.desc >> 16) & 0xF) * 4
        rec = lambda g: np.ascontiguousarray(np.concatenate([g.records[:, :uvo + 4], g.records[:, no:no + 3]], axis=1))  # noqa: E731
        have = {r.tobytes() for r in rec(src)}
        missing = sum(r.tobytes() not in have for r in rec(new))
        if mat_s != mat_n or missing or new.desc != src.desc:
            files_ok = False
        detail.append(f"{stem}: {len(new.records)} vertices, {missing} not one of {BC.SOURCE}'s; materials file "
                      f"{mat_n.decode()}{'' if mat_s == mat_n else ' (' + BC.SOURCE + ': ' + mat_s.decode() + ')'}")
    rep.check(files_ok, f"cables: every {BC.LABEL} vertex one of {BC.SOURCE}'s (position, UV and normal: its texels on "
                         f"{BC.SOURCE}'s atlas), under {BC.SOURCE}'s materials file", "; ".join(detail))
    # the cut: where it meets static_black's triangles, at most CUT_R from the axis
    if BC.LABEL not in geo:
        rep.check(False, f"cables: {BC.LABEL} in {where}")
        return
    (sv, sf), (nv, nf) = geo[BC.SOURCE], geo[BC.LABEL]
    q = lambda a: {tuple(x) for x in np.round(np.asarray(a) * 1024.0).astype(np.int64)}  # noqa: E731
    shared = np.array(sorted(q(nv[np.unique(nf)]) & q(sv[np.unique(sf)])), np.float64) / 1024.0   # the kept triangles'
    r = BC.axis_distance(shared, sp, ax) if len(shared) else np.zeros(1)
    rep.check(len(shared) > 0 and r.max() <= CUT_R,
              f"cables: the cut where {BC.LABEL} meets {BC.SOURCE} at most {CUT_R:g} from the steering axis",
              f"{len(shared)} shared vertices, {r.min():.1f}-{r.max():.1f} from it: it opens {BC.kink(r.max(), 16):.1f} at 16 "
              f"degrees, {BC.kink(r.max(), bar):.1f} at BarAngle {bar:g}")
    gap, at = H.turning_clearance(v, tank, sp, ax, bar)
    rep.check(gap >= TANK_CLEAR, f"cables: {BC.LABEL} at least {TANK_CLEAR:g} clear of the tank with the bars within {bar:g} "
                                 f"degrees", f"{gap:.2f} (at {at:+.0f})")


def _shape_full(nif, name):
    """A shape's full-precision (or half-float) vertices, triangles and decoded normals from bar_cables' reader."""
    k = nif.shape_named(name)
    if k is None:
        return None
    s = BC.TriShape(nif.blocks[k])
    at = ((s.desc >> 16) & 0xF) * 4
    return s.positions(), s.tris, s.records[:, at:at + 3].astype(np.float64) / 255.0 * 2.0 - 1.0


def c3_checks(rep, args, meshes, labels, materials, parts):
    """2026-11-16a (C3, look_emblems.py): the 3D helmets: four shapes a nif, last, invisible on their own files until a
    tank option's swap; their limits, their place on the plates and their clearances."""
    import bgsm as B
    stems = (("CMB_BikeParked", "CMB_Bike", ""), ("CMB_BikeWorn", "CMB_BikeWorn", "_worn"),
             ("CMB_BikeWornRider", "CMB_BikeWornRider", "_worn"), ("CMB_BikeWornRiderF", "CMB_BikeWornRiderF", "_worn"),
             (VIEW, VIEW, "_worn"))
    counts, bad, names = [], [], {}
    for stem, nm, w in stems:
        path = meshes / f"{stem}.nif"
        if not path.exists():
            continue
        nif = BC.Nif(path.read_bytes())
        shapes = [nif.name_of(k) for k in nif.shapes()]
        counts.append(f"{stem} {len(shapes)}")
        want = [f"{nm}_{label}" for label in C3_LABELS]
        tail = shapes[-4 - len(C4_LABELS):-len(C4_LABELS)] if shapes[-len(C4_LABELS):] == [f"{nm}_{lb}" for lb in C4_LABELS] \
            else shapes[-4:]   # 2026-11-21a: look_shells.py's three after them
        if tail != want:
            bad.append(f"{stem}: its last shapes {tail}")
        for label in C3_LABELS:
            k = nif.shape_named(f"{nm}_{label}")
            if k is None:
                continue
            s = BC.TriShape(nif.blocks[k])
            mat = nif.strings[struct.unpack_from("<i", nif.blocks[s.shader], 4)[0]].decode()
            names.setdefault(label + w, set()).add(mat.lower())
            if mat.lower() != f"materials\\cmb\\bike\\{label}{w}.bgsm".lower():
                bad.append(f"{stem}_{label}: materials file {mat}")
            if (s.skin >= 0) != (stem in WORN) or struct.unpack_from("<I", s.head, 12)[0] & 1:
                bad.append(f"{stem}_{label}: skinned {s.skin >= 0}, flags {struct.unpack_from('<I', s.head, 12)[0]}")
            if s.alpha < 0:
                bad.append(f"{stem}_{label}: no alpha property")
    worn_n = next((int(c.split()[-1]) for c in counts if c.startswith("CMB_BikeWorn ")), 0)
    rep.check(not bad and worn_n + 1 <= MAX_SKINS,
              f"c3: the four helmets ({', '.join(C3_LABELS)}) last in every nif, each naming its own materials file "
              f"(<shape>.bgsm parked, <shape>_worn.bgsm ridden and in first person), skinned in the worn nifs only, shown "
              f"by the node flag, an alpha property each; the plugin's shapes {worn_n + 1} of MAX_SKINS {MAX_SKINS}",
              "; ".join(counts + bad[:8]))
    # invisible by default: the own files (alpha test 255, alpha 0, no shadows, off's textures, no cube)
    bad = []
    for stem_w in sorted(names):
        path = materials.get(f"cmb\\bike\\{stem_w}.bgsm".lower())
        if path is None:
            bad.append(f"{stem_w}.bgsm missing")
            continue
        m = B.read(path)
        if not (m["alpha_test"] and m["alpha_test_ref"] == 255 and m["alpha"] == 0.0 and not m["cast_shadows"]
                and m["textures"]["diffuse"].lower() == "cmb\\bike\\off_d.dds" and not m["environment_mapping"]):
            bad.append(f"{stem_w}: alpha test {m['alpha_test']} ref {m['alpha_test_ref']} alpha {m['alpha']} shadows "
                       f"{m['cast_shadows']} diffuse {m['textures']['diffuse']} env {m['environment_mapping']}")
    rep.check(len(names) == 8 and not bad, f"c3: the helmets invisible until a swap: their {len(names)} own materials "
                                            f"files alpha test 255, alpha 0, no shadow, off_d/_n/_s, no cube", "; ".join(bad))
    # the emblem materials (the swaps' targets): helm_enclave glows by helms_g with no cube, helm_bos on the chrome cube
    opts = json.loads(LOOK_OPTIONS.read_text()) if LOOK_OPTIONS.exists() else {}
    bad = []
    for item in (opts.get("emblems") or {}).get("items", []):
        leaf = item["material"].replace("/", "\\").lower()
        path = materials.get(leaf)
        if path is None:
            bad.append(f"{item['material']} missing")
            continue
        m = B.read(path)
        t = {k: v.replace("/", "\\").lower() for k, v in m["textures"].items()}
        tex = {k: v.replace("/", "\\").lower() for k, v in opts["emblems"]["textures"].items()}
        if (t["diffuse"], t["normal"], t["smoothspec"]) != (tex["diffuse"], tex["normal"], tex["smoothspec"]):
            bad.append(f"{item['material']}: textures {t['diffuse']}, {t['normal']}, {t['smoothspec']}")
        if item["glow"] and not (m["glowmap"] and m["emit_enabled"] and t["glow"] == tex["glow"] and not m["environment_mapping"]):
            bad.append(f"{item['material']}: glow map {m['glowmap']} {t['glow']!r}, env {m['environment_mapping']}")
        if item.get("env_scale") and not (m["environment_mapping"] and abs(m["env_map_mask_scale"] - item["env_scale"]) < 1e-6
                                          and t["envmap"] == opts["emblems"]["env"].lower() and not m["glowmap"]):
            bad.append(f"{item['material']}: env {m['environment_mapping']} {m['env_map_mask_scale']:g} {t['envmap']!r}")
    rep.check(not bad and opts.get("emblems"), "c3: the emblems' materials files as the table's emblems.items (helm_enclave "
                                               "the glow shader over helms_g, no cube; helm_bos the chrome cube at 0.8)",
              "; ".join(bad))
    # the shapes on the parked nif's plates (full precision)
    nif = BC.Nif((meshes / "CMB_BikeParked.nif").read_bytes())
    paint = _shape_full(nif, "CMB_Bike_static_paint")
    others = {}
    for k in nif.shapes():
        name = nif.name_of(k)
        if name.startswith("CMB_Bike_") and name[len("CMB_Bike_"):] not in C3_LABELS + C4_LABELS + ("static_paint",) \
                and not name.endswith(("_static_badgeTankL", "_static_badgeTankR")):
            s = BC.TriShape(nif.blocks[k])
            others[name[len("CMB_Bike_"):]] = s.positions()[s.tris]
    lines, bad, worst = [], [], {"h": 0.0, "inset": np.inf, "paint": np.inf, "other": (np.inf, "")}
    fields = {name: EP.GROUND_FIELD_UV for name in EP.HELMETS}
    if args.ground_field:
        gb = json.loads(args.ground_field.read_text())["badges"]
        fields = {name: tuple(tuple(p) for p in gb[f"hg_{name}"]["field"]["outline_plate_uv"]) for name in EP.HELMETS}
    for label, helmet, side in EP.SHAPES:
        g = _shape_full(nif, f"CMB_Bike_{label}")
        pl = _shape_full(nif, f"CMB_Bike_{EP.PLATES[side]}")
        if g is None or pl is None:
            bad.append(f"{label}: not in the parked nif")
            continue
        v, f, n = g
        fr = EP.plate_frame(*pl, BC.TriShape(nif.blocks[nif.shape_named(f"CMB_Bike_{EP.PLATES[side]}")]).uvs())
        rel = v - fr["origin"]
        xy = np.column_stack([rel @ fr["right"], rel @ fr["up"]])
        W, N, hit = EP.cast_on_plate(fr, xy)
        if not hit.all():
            bad.append(f"{label}: {int((~hit).sum())} vertices off its plate")
            continue
        h = rel @ fr["n"] - W
        poly = EP.inset_polygon(fr["outline"], EMBLEM_INSET)
        inset = float(EP.inside_convex(poly, xy).min())
        if len(v) > EMBLEM_MAX_VERTS or not EMBLEM_TRIS[0] <= len(f) <= EMBLEM_TRIS[1]:
            bad.append(f"{label}: {len(v)} vertices, {len(f)} triangles")
        if h.max() > EP.HEIGHT_MAX + 1e-3 or h.min() < EP.SKIRT - 0.02:
            bad.append(f"{label}: {h.min():.3f}..{h.max():.3f} over its plate")
        if inset < 0:
            bad.append(f"{label}: {-inset:.3f} outside the plate's outline inset {EMBLEM_INSET:g}")
        # inside its ground's enamel field (unit B's; the area both plates show), clear of the chrome bevel
        field = EP.field_outline(fr, fields[helmet], 16)
        in_field = -float(EP.sd_polygon(field, xy).max())
        if in_field < EMBLEM_FIELD_INSET:
            bad.append(f"{label}: {in_field:.3f} inside its ground's field (under {EMBLEM_FIELD_INSET:g})")
        worst["field"] = min(worst.get("field", np.inf), in_field)
        # the paint: only the walls' foot and the skirt may come near (a vertex there faces along the plate, not out)
        tris = paint[0][paint[1]]
        lo, hi = v.min(axis=0) - 3, v.max(axis=0) + 3
        c = tris.mean(axis=1)
        tris = tris[np.all((c > lo) & (c < hi), axis=1)]
        d = TriangleGrid(tris, 0.6).closest(v, reach=1.0)[2]
        facing = n @ fr["n"] > math.cos(math.radians(45.0))
        near = (d < EMBLEM_PAINT) & (h > 0.0) & facing
        if near.any():
            bad.append(f"{label}: {int(near.sum())} outward-facing vertices over the plate within {EMBLEM_PAINT:g} of the paint")
        top = h > EMBLEM_PAINT
        if top.any() and d[top].min() < EMBLEM_PAINT:
            bad.append(f"{label}: {d[top].min():.3f} from the paint {EMBLEM_PAINT:g} up")
        # every other shape (but its plate and the other helmets, its alternatives on the same plate)
        clear = (np.inf, "")
        for name, t in others.items():
            cc = t.mean(axis=1)
            t = t[np.all((cc > lo) & (cc < hi), axis=1)]
            if len(t):
                dd = TriangleGrid(t, 1.0).closest(v[h > 0.0], reach=1.0)[2]
                clear = min(clear, (float(dd.min()), name))
        if clear[0] < EMBLEM_PAINT:
            bad.append(f"{label}: {clear[0]:.3f} from {clear[1]}")
        worst["h"] = max(worst["h"], float(h.max()))
        worst["inset"] = min(worst["inset"], inset)
        worst["paint"] = min(worst["paint"], float(d[top].min()) if top.any() else np.inf)
        worst["other"] = min(worst["other"], clear)
        lines.append(f"{label} {len(v)} vertices, {len(f)} triangles, {np.ptp(xy[:, 0]):.2f} wide and {np.ptp(xy[:, 1]):.2f} tall "
                     f"(its foot), {h.min():+.2f}..{h.max():.2f} over its plate, {in_field:.2f} inside its ground's field, "
                     f"{inset:.2f} inside the plate's outline inset {EMBLEM_INSET:g}, {d.min():.2f} from the paint ({d[top].min() if top.any() else 0:.2f} "
                     f"from {EMBLEM_PAINT:g} up), " + (f"{clear[0]:.2f} from {clear[1]}" if clear[1] else "no other shape within 3"))
    rep.check(not bad, f"c3: each helmet at most {EMBLEM_MAX_VERTS} vertices and {EMBLEM_TRIS[0]}-{EMBLEM_TRIS[1]} triangles, "
                       f"{EP.SKIRT:g}..{EP.HEIGHT_MAX:g} over its plate (the parked nif, full precision), every vertex at "
                       f"least {EMBLEM_FIELD_INSET:g} inside its ground's enamel field ("
                       + (f"{args.ground_field}" if args.ground_field else "emblem_pieces.GROUND_FIELD_UV")
                       + f": the area both plates show, inside the chrome bevel) and the plate's outline inset {EMBLEM_INSET:g}, nothing facing out within {EMBLEM_PAINT:g} of the paint (the wall's "
                       f"foot and the skirt aside: the plate is 0.03-0.5 over it there), clear of every other shape",
              "; ".join(bad[:8]))
    for line in lines:
        rep.info("c3 helmet", line)
    # the bars turned within BarAngle against the helmets (fixed): the worn nif's front_* shapes
    sp = np.array([float(x) for x in parts.get("SteerPoint", "0,0,0").split(",")])
    ax = H.unit(np.array([float(x) for x in parts.get("SteerAxis", "0,0,1").split(",")]))
    bar = float(parts.get("BarAngle", "20"))
    view = BC.Nif((meshes / f"{VIEW}.nif").read_bytes()) if (meshes / f"{VIEW}.nif").exists() else None
    if view is not None:
        front = np.vstack([BC.TriShape(view.blocks[k]).positions() for k in view.shapes()
                           if "_front_" in view.name_of(k).lower() or "_fork" in view.name_of(k).lower()])
        gaps = []
        for label in C3_LABELS + tuple(EP.PLATES.values()):
            g = _shape_full(view, f"{VIEW}_{label}")
            if g is None:
                continue
            tris = g[0][g[1]]
            r_axis = BC.axis_distance(g[0], sp, ax)
            a_axis = (g[0] - sp) @ ax
            fr_r, fr_a = BC.axis_distance(front, sp, ax), (front - sp) @ ax
            sel = (fr_r > r_axis.min() - 6) & (fr_r < r_axis.max() + 6) & (fr_a > a_axis.min() - 6) & (fr_a < a_axis.max() + 6)
            gap, at = H.turning_clearance(front[sel], tris, sp, ax, bar) if sel.any() else (np.inf, 0.0)
            gaps.append((label, gap, at))
        helm = [x for x in gaps if x[0] in C3_LABELS]
        rep.check(helm and min(x[1] for x in helm) >= EMBLEM_BARS,
                  f"c3: the bar assembly (front_*, fork_*) turned within BarAngle {bar:g} at least {EMBLEM_BARS:g} clear of "
                  f"the helmets ({VIEW}.nif, full precision; a gap over 6 reads as the distance to the box)",
                  "; ".join(f"{lb} {gp:.1f} (at {at:+.0f})" for lb, gp, at in gaps))
    if args.knees:
        knee_checks(rep, args.knees, meshes, args.pynifly)
    else:
        rep.info("c3 knees", "not measured (--knees <the riding clips' folder>): TESTING step 1, in game")


ROLE_TAGS = (("_front_needle", True, "needle"), ("_front_glow", True, "glow"), ("_front_dialglow", True, "glow"),
             ("_rear_tail", True, "tail"), ("_rear_brake", True, "brake"), ("_fork", False, "fork"), ("_wheelF", False, "wheel"),
             ("_wheelR", False, "wheel"), ("_front_mirrorStock", True, "front"), ("_front_mirrorUnderEgg", True, "front"),
             ("_front_mirrorUnderD", True, "front"), ("_front_", False, "front"), ("_static_", False, "fixed"))
COLOUR_TAGS = ("_wheelF_rim", "_wheelR_rim", "_rimLaced", "_rimDisc", "_rimStar", "_rimTurbine", "_rimPrewar", "_rimAtomic",
               "_rimScrap", "_static_paint", "_fork_paint", "_static_plate", "_static_plateText")   # CMB_Slope.c g_lookGroups


def role_by_name(name):
    """The plugin's role for a shape's name (CMB_Slope.c g_roleTags, the first tag that fits; case aside)."""
    low = name.lower()
    return next((role for tag, end, role in ROLE_TAGS if (low.endswith(tag.lower()) if end else tag.lower() in low)), None)


def _records_map(new, src):
    """Each of new's vertices' source vertex (a TriShape each): the source vertices whose record but the position is the
    same bytes, the nearest of them. -1 where none."""
    cut = 12 if src.full else 6
    by = {}
    for i, r in enumerate(src.records[:, cut:]):
        by.setdefault(r.tobytes(), []).append(i)
    sp, npos = src.positions(), new.positions()
    out = np.full(len(new.records), -1, np.int64)
    for i, r in enumerate(new.records[:, cut:]):
        cand = by.get(r.tobytes())
        if cand:
            d = np.linalg.norm(sp[cand] - npos[i], axis=1)
            out[i] = cand[int(np.argmin(d))]
    return out


def _bone_sphere(nif, s):
    """(centre in the bike's space, radius, bone data bytes) of a skinned shape's one bone."""
    inst = nif.blocks[s.skin]
    data = nif.blocks[struct.unpack_from("<i", inst, 4)[0]]
    rot = np.array(struct.unpack_from("<9f", data, 20)).reshape(3, 3)
    trans = np.array(struct.unpack_from("<3f", data, 56))
    cs = np.array(struct.unpack_from("<3f", data, 4))
    return rot.T @ (cs - trans), struct.unpack_from("<f", data, 16)[0], data


def c4_checks(rep, args, meshes, labels, materials, parts):
    """2026-11-21a (art build B, look_shells.py): the wear shells (static_wear, fork_wear) and the front fender's badge
    patch (fork_badgeFront): three shapes a nif, last, invisible on their own files until a look option's swap; the
    shells over their sources, the patch's cast, their roles, the skin count."""
    import bgsm as B
    stems = (("CMB_BikeParked", "CMB_Bike", ""), ("CMB_BikeWorn", "CMB_BikeWorn", "_worn"),
             ("CMB_BikeWornRider", "CMB_BikeWornRider", "_worn"), ("CMB_BikeWornRiderF", "CMB_BikeWornRiderF", "_worn"),
             (VIEW, VIEW, "_worn"))
    nifs = {stem: BC.Nif((meshes / f"{stem}.nif").read_bytes()) for stem, _, _ in stems if (meshes / f"{stem}.nif").exists()}
    counts, bad, names = [], [], {}
    front_min_y = float(parts.get("FrontMinY", "0"))
    for stem, nm, w in stems:
        nif = nifs.get(stem)
        if nif is None:
            continue
        shapes = [nif.name_of(k) for k in nif.shapes()]
        counts.append(f"{stem} {len(shapes)}")
        if shapes[-3:] != [f"{nm}_{label}" for label in C4_LABELS]:
            bad.append(f"{stem}: its last shapes {shapes[-3:]}")
        for label in C4_LABELS:
            k = nif.shape_named(f"{nm}_{label}")
            if k is None:
                continue
            s = BC.TriShape(nif.blocks[k])
            sh = nif.blocks[s.shader]
            mat = nif.strings[struct.unpack_from("<i", sh, 4)[0]].decode()
            f1, f2 = struct.unpack_from("<II", sh, 16)
            names.setdefault(label + w, set()).add(mat.lower())
            if mat.lower() != f"materials\\cmb\\bike\\{label}{w}.bgsm".lower():
                bad.append(f"{stem}_{label}: materials file {mat}")
            if (s.skin >= 0) != (stem in WORN) or struct.unpack_from("<I", s.head, 12)[0] & 1 or s.alpha < 0:
                bad.append(f"{stem}_{label}: skinned {s.skin >= 0}, flags {struct.unpack_from('<I', s.head, 12)[0]}, alpha {s.alpha}")
            if f1 & H.SF1_CAST_SHADOWS:
                bad.append(f"{stem}_{label}: casts a shadow")
            if bool(f2 & 0x10) != (label == C4_PATCH):
                bad.append(f"{stem}_{label}: two-sided {bool(f2 & 0x10)}")
            role = role_by_name(f"{nm}_{label}")
            want = "fork" if label.startswith("fork_") else "fixed"
            if role != want or any(f"{nm}_{label}".lower().endswith(t.lower()) for t in COLOUR_TAGS):
                bad.append(f"{stem}_{label}: the plugin's role by its name {role} (want {want}), or a colour writer's tag")
            if s.skin >= 0:   # its source's bone: the same bind and sphere centre, round its vertices; RolesByName=0's rule
                src = dict(C4_SHELLS).get(label, C4_PATCH_ON)
                ss = BC.TriShape(nif.blocks[nif.shape_named(f"{nm}_{src}")])
                c, r, data = _bone_sphere(nif, s)
                cs, rs, sdata = _bone_sphere(nif, ss)
                if data[:16] != sdata[:16] or data[20:] != sdata[20:] or r < rs:
                    bad.append(f"{stem}_{label}: its bone data isn't {src}'s (the bind, the sphere's centre, a radius as large)")
                if np.linalg.norm(s.positions() - c, axis=1).max() > r + 1e-3:
                    bad.append(f"{stem}_{label}: its culling sphere doesn't hold its vertices")
                if want == "fixed" and c[1] > front_min_y:
                    bad.append(f"{stem}_{label}: its sphere ahead of FrontMinY (RolesByName=0 would turn it with the bars)")
    worn_n = next((int(c.split()[-1]) for c in counts if c.startswith("CMB_BikeWorn ")), 0)
    view_n = next((int(c.split()[-1]) for c in counts if c.startswith(f"{VIEW} ")), 0)
    rep.check(not bad and worn_n + 1 <= MAX_SKINS and view_n <= VIEW_SHAPES,
              f"c4: the three shapes ({', '.join(C4_LABELS)}) last in every nif, each naming its own materials file, skinned "
              f"in the worn nifs only (its source's bone and sphere centre, the sphere round it), shown, an alpha property each, "
              f"no shadow, the shells one-sided and the patch two-sided; the plugin's roles by name (static_wear fixed, the "
              f"fork_ two the lower fork: with the bars and the suspension) and by sphere, no colour writer's tag; the "
              f"plugin's shapes {worn_n + 1} of MAX_SKINS {MAX_SKINS}, the first-person bike's {view_n} of VIEW_SHAPES {VIEW_SHAPES}",
              "; ".join(counts + bad[:8]))
    # the six own files: invisible (alpha test 255, alpha 0, no shadows, off's textures, no cube); the shells' one-sided,
    # the patch's the rear patch's bytes
    bad = []
    for stem_w in sorted(names):
        path = materials.get(f"cmb\\bike\\{stem_w}.bgsm".lower())
        if path is None:
            bad.append(f"{stem_w}.bgsm missing")
            continue
        m = B.read(path)
        if not (m["alpha_test"] and m["alpha_test_ref"] == 255 and m["alpha"] == 0.0 and not m["cast_shadows"]
                and m["textures"]["diffuse"].lower() == "cmb\\bike\\off_d.dds" and not m["environment_mapping"]):
            bad.append(f"{stem_w}: alpha test {m['alpha_test']} ref {m['alpha_test_ref']} alpha {m['alpha']} shadows "
                       f"{m['cast_shadows']} diffuse {m['textures']['diffuse']} env {m['environment_mapping']}")
        if stem_w.startswith(C4_PATCH):
            twin = materials.get(f"cmb\\bike\\{H.FENDER_BADGE}{stem_w[len(C4_PATCH):]}.bgsm".lower())
            if twin is None or twin.read_bytes() != path.read_bytes():
                bad.append(f"{stem_w}: not {H.FENDER_BADGE}{stem_w[len(C4_PATCH):]}.bgsm's bytes")
        elif m["two_sided"]:
            bad.append(f"{stem_w}: two-sided")
    rep.check(len(names) == 6 and not bad, f"c4: the new shapes invisible until a swap: their {len(names)} own materials files "
                                           f"alpha test 255, alpha 0, no shadow, off_d/_n/_s, no cube; the shells' one-sided, "
                                           f"the patch's the rear patch's ({H.FENDER_BADGE}.bgsm) bytes", "; ".join(bad))
    # the shells over their sources, nif by nif (full precision in the parked and view nifs, half floats in the worn ones)
    lo_b, hi_b = SHP.SHELL_BAND
    inside_done = set()
    for label, src in C4_SHELLS:
        lines, bad = [], []
        for stem, nm, _ in stems:
            nif = nifs.get(stem)
            if nif is None or nif.shape_named(f"{nm}_{label}") is None:
                continue
            s = BC.TriShape(nif.blocks[nif.shape_named(f"{nm}_{label}")])
            so = BC.TriShape(nif.blocks[nif.shape_named(f"{nm}_{src}")])
            m = _records_map(s, so)
            if (m < 0).any():
                bad.append(f"{stem}: {int((m < 0).sum())} vertices not one of {src}'s (the record but the position)")
                continue
            sv, ov = s.positions(), so.positions()
            # closed: every source position's vertices among the shell's at one shell position (the positions told by the
            # full-precision source: the view nif's, vertex for vertex the worn nifs', where the half floats round two
            # near places to one)
            full_src = ov
            if not so.full and VIEW in nifs and nifs[VIEW].shape_named(f"{VIEW}_{src}") is not None:
                fv = BC.TriShape(nifs[VIEW].blocks[nifs[VIEW].shape_named(f"{VIEW}_{src}")]).positions()
                if len(fv) == len(ov):
                    full_src = fv
            pos, _ = SHP.weld_positions(full_src, 65536.0)
            spread = 0.0
            order = np.argsort(pos[m], kind="stable")
            pm, sp_ = pos[m][order], sv[order]
            cuts = np.flatnonzero(np.diff(pm)) + 1
            for grp in np.split(np.arange(len(pm)), cuts):
                if len(grp) > 1:
                    spread = max(spread, float(np.abs(sp_[grp] - sp_[grp[0]]).max()))
            if spread > 0.0:
                bad.append(f"{stem}: a source position's vertices {spread:.4f} apart in the shell (it opens at a hard edge)")
            tri_src = {tuple(np.roll(t, -int(np.argmin(t)))) for t in so.tris}
            mapped = m[s.tris]
            wrong = sum(tuple(np.roll(t, -int(np.argmin(t)))) not in tri_src for t in mapped)
            if wrong:
                bad.append(f"{stem}: {wrong} triangles not {src}'s (with its winding)")
            tris = ov[so.tris]
            grid = TriangleGrid(tris, 1.0)
            d = grid.closest(sv, reach=0.6)[2]
            band = C4_BAND_HALF if not s.full else SHP.SHELL_BAND
            if d.min() < band[0] - 1e-6 or d.max() > band[1] + 1e-6:
                bad.append(f"{stem}: its vertices {d.min():.4f}-{d.max():.4f} over {src} (want {band[0]:g}-{band[1]:g})")
            samples, _ = SHP.triangle_samples(sv, s.tris)
            ds = grid.closest(samples.reshape(-1, 3), reach=0.6)[2].reshape(len(s.tris), -1)
            if ds.min() < SHP.SHELL_FLOOR:
                bad.append(f"{stem}: over its triangles {ds.min():.4f} from {src} (under {SHP.SHELL_FLOOR:g})")
            area = np.linalg.norm(np.cross(sv[s.tris[:, 1]] - sv[s.tris[:, 0]], sv[s.tris[:, 2]] - sv[s.tris[:, 0]]), axis=1) / 2
            share = float((area[:, None] * ((ds >= lo_b) & (ds <= hi_b))).sum() / (area.sum() * ds.shape[1]))
            lines.append(f"{stem} {len(sv)} vertices {d.min():.4f}-{d.max():.4f} over {src}"
                         + ("" if s.full else f" ({int(((d < lo_b) | (d > hi_b)).sum())} outside {lo_b:g}-{hi_b:g})")
                         + f", its triangles {ds.min():.3f}-{ds.max():.3f} ({100 * share:.1f}% of the area {lo_b:g}-{hi_b:g})")
            # inside another shape: the parked nif (full precision) and one worn nif (the half floats)
            if stem in ("CMB_BikeParked", "CMB_BikeWorn"):
                others = {}
                for k in nif.shapes():
                    name = nif.name_of(k)
                    lb = name[len(nm) + 1:] if name.startswith(nm + "_") else None
                    if lb is None or lb == label or lb in C4_LABELS or lb in H.BADGE_SPLIT + (H.FENDER_BADGE, H.PLATE_TEXT):
                        continue
                    g = BC.TriShape(nif.blocks[k])
                    others[lb] = (g.positions(), g.tris)
                hit = SHP.inside_shapes(sv, others)
                n_in = int(sum(h is not None for h in hit))
                inside_done.add(stem)
                if n_in:
                    which = sorted({h for h in hit if h is not None})
                    bad.append(f"{stem}: {n_in} vertices inside {', '.join(which)}")
                lines.append(f"{stem}: no vertex inside another shape (the winding number of each shape but the open sheets)"
                             if not n_in else f"{stem}: {n_in} inside")
        rep.check(not bad and lines, f"c4: {label} over {src}: every vertex one of {src}'s (UV, normal, tangent, skin), "
                                     f"closed at the hard edges, its triangles {src}'s, every vertex {lo_b:g}-{hi_b:g} over it "
                                     f"(the worn nifs' half floats {C4_BAND_HALF[0]:g}-{C4_BAND_HALF[1]:g}), over its triangles "
                                     f"at least {SHP.SHELL_FLOOR:g}, no vertex inside another shape", "; ".join(bad[:8]))
        for line in lines:
            rep.info(f"c4 {label}", line)
    # the front patch's cast, and both badge patches over the wear shells
    axle_w = np.array([float(x) for x in parts.get("FrontAxle", "0,0,0").split(",")])
    for stem, nm, _ in stems:
        nif = nifs.get(stem)
        if nif is None or stem not in ("CMB_BikeParked", "CMB_BikeWorn", VIEW):
            continue
        bad, lines = [], []
        s = BC.TriShape(nif.blocks[nif.shape_named(f"{nm}_{C4_PATCH}")])
        on = BC.TriShape(nif.blocks[nif.shape_named(f"{nm}_{C4_PATCH_ON}")])
        wear = BC.TriShape(nif.blocks[nif.shape_named(f"{nm}_fork_wear")])
        pv, on_v = s.positions(), on.positions()
        tol = C4_PATCH_VERTEX[0] if s.full else C4_PATCH_VERTEX[1]
        grid = TriangleGrid(on_v[on.tris], 1.0)
        ti, bc, d = grid.closest(pv, reach=1.0)
        if np.abs(d - SHP.FRONT_PATCH_LIFT).max() > tol:
            bad.append(f"its vertices {d.min():.3f}-{d.max():.3f} over {C4_PATCH_ON} (want {SHP.FRONT_PATCH_LIFT:g} +-{tol:g})")
        samples, _ = SHP.triangle_samples(pv, s.tris)
        ds = grid.closest(samples.reshape(-1, 3), reach=1.0)[2]
        if ds.min() < C4_PATCH_RANGE[0] or ds.max() > C4_PATCH_RANGE[1]:
            bad.append(f"over its triangles {ds.min():.3f}-{ds.max():.3f} (want {C4_PATCH_RANGE[0]:g}-{C4_PATCH_RANGE[1]:g})")
        dw = TriangleGrid(wear.positions()[wear.tris], 1.0).closest(samples.reshape(-1, 3), reach=1.0)[2]
        if dw.min() < C4_OVER_WEAR:
            bad.append(f"{dw.min():.3f} over fork_wear (under {C4_OVER_WEAR:g})")
        # facing out, on the crown (the surface's normal under it from the axle), the winding
        fn = SHP.unit(np.cross(pv[s.tris[:, 1]] - pv[s.tris[:, 0]], pv[s.tris[:, 2]] - pv[s.tris[:, 0]]))
        t_on = on_v[on.tris]
        sn = SHP.unit(np.cross(t_on[:, 1] - t_on[:, 0], t_on[:, 2] - t_on[:, 0]))
        under = sn[ti]
        axle = axle_w if stem != "CMB_BikeParked" else None
        if axle is None:   # the parked frame: the view nif's static_paint fitted to the parked one's
            vw_paint = BC.TriShape(nifs[VIEW].blocks[nifs[VIEW].shape_named(f"{VIEW}_static_paint")]).positions()
            pk_paint = BC.TriShape(nif.blocks[nif.shape_named("CMB_Bike_static_paint")]).positions()
            Rv, tv = LE.fit_rigid(pk_paint, vw_paint)
            axle = (axle_w - tv) @ Rv
        radial = pv - axle
        radial[:, 0] = 0.0
        radial = SHP.unit(radial)
        crown = np.einsum("ij,ij->i", under, radial)
        if crown.min() < C4_CROWN:
            bad.append(f"the mudguard under it {np.degrees(np.arccos(crown.min())):.0f} degrees off the axle's direction (off the crown)")
        facing = np.einsum("ij,ij->i", fn, SHP.unit((pv[s.tris].mean(axis=1) - axle) * np.array([0.0, 1.0, 1.0])))
        if facing.min() <= 0.5:
            bad.append(f"a triangle facing in or along ({facing.min():.2f})")
        # the UVs: the plate rectangle, read from in front: u to the bike's left, v toward the front
        uv = s.uvs()
        u0, v0, u1, v1 = SHP.BADGE_PLATE_RECT
        if uv[:, 0].min() < u0 - 1e-3 or uv[:, 0].max() > u1 + 1e-3 or uv[:, 1].min() < v0 - 1e-3 or uv[:, 1].max() > v1 + 1e-3:
            bad.append(f"UVs u {uv[:, 0].min():.3f}-{uv[:, 0].max():.3f} v {uv[:, 1].min():.3f}-{uv[:, 1].max():.3f}")
        left = np.array([1.0, 0.0, 0.0]) if stem == "CMB_BikeParked" else np.array([-1.0, 0.0, 0.0])
        ahead = np.array([0.0, -1.0, 0.0]) if stem == "CMB_BikeParked" else np.array([0.0, 1.0, 0.0])
        cu, cv = np.corrcoef(uv[:, 0], pv @ left)[0, 1], np.corrcoef(uv[:, 1], pv @ ahead)[0, 1]
        if cu < 0.99 or cv < 0.9:
            bad.append(f"its UVs not read from in front (u with the bike's left {cu:.2f}, v with ahead {cv:.2f})")
        lines.append(f"{len(pv)} vertices {d.min():.3f}-{d.max():.3f} over {C4_PATCH_ON}, its triangles {ds.min():.3f}-"
                     f"{ds.max():.3f}, {dw.min():.3f} or more over fork_wear; the crown under it within "
                     f"{np.degrees(np.arccos(min(1.0, crown.min()))):.0f} degrees of the axle's direction; u with the bike's left "
                     f"{cu:.3f}, v with ahead {cv:.3f}")
        # the rear patch over static_wear
        rear = BC.TriShape(nif.blocks[nif.shape_named(f"{nm}_{H.FENDER_BADGE}")])
        sw = BC.TriShape(nif.blocks[nif.shape_named(f"{nm}_static_wear")])
        paint = BC.TriShape(nif.blocks[nif.shape_named(f"{nm}_static_paint")])
        rs, _ = SHP.triangle_samples(rear.positions(), rear.tris)
        rs = rs.reshape(-1, 3)
        sw_v = sw.positions()
        near = np.all([(sw_v[:, i] > rs[:, i].min() - 3) & (sw_v[:, i] < rs[:, i].max() + 3) for i in range(3)], axis=0)
        tsel = near[sw.tris].all(axis=1)
        drw = TriangleGrid(sw_v[sw.tris[tsel]], 1.0).closest(rs, reach=1.0)[2] if tsel.any() else np.full(1, np.inf)
        drp = TriangleGrid(paint.positions()[paint.tris], 1.0).closest(rs, reach=1.0)[2]
        if drw.min() < C4_OVER_WEAR:
            bad.append(f"the rear patch {drw.min():.3f} over static_wear (under {C4_OVER_WEAR:g})")
        lines.append(f"the rear patch {H.FENDER_BADGE} {drp.min():.3f}-{drp.max():.3f} over static_paint over its triangles, "
                     f"{drw.min():.3f} or more over static_wear")
        rep.check(not bad, f"c4: {stem}: the front patch {C4_PATCH} cast on {C4_PATCH_ON}'s crown: every vertex "
                           f"{SHP.FRONT_PATCH_LIFT:g} over it (+-{tol:g}), over its triangles {C4_PATCH_RANGE[0]:g}-"
                           f"{C4_PATCH_RANGE[1]:g} (no gap, no poke-through at the curvature), facing out, on the crown, its UVs the "
                           f"plate rectangle read from in front; it and the rear patch at least {C4_OVER_WEAR:g} over the wear shells",
                  "; ".join(bad))
        for line in lines:
            rep.info(f"c4 {stem}", line)
    # the bar assembly against static_wear (the view nif, full precision): the mirrors, the cables and the bars turned
    view = nifs.get(VIEW)
    if view is not None:
        sp = np.array([float(x) for x in parts.get("SteerPoint", "0,0,0").split(",")])
        ax = H.unit(np.array([float(x) for x in parts.get("SteerAxis", "0,0,1").split(",")]))
        bar = float(parts.get("BarAngle", "20"))
        sw = BC.TriShape(view.blocks[view.shape_named(f"{VIEW}_static_wear")])
        tris = sw.positions()[sw.tris]
        gaps = []
        for k in view.shapes():
            name = view.name_of(k)
            if "_front_" not in name.lower():
                continue
            g = BC.TriShape(view.blocks[k]).positions()
            gap, at = H.turning_clearance(g, tris, sp, ax, bar)
            gaps.append((name[len(VIEW) + 1:], gap, at))
        worst = min(gaps, key=lambda x: x[1])
        rep.check(worst[1] >= C4_BARS, f"c4: the bar assembly (front_*: the mirrors and the cables among them) turned within "
                                       f"BarAngle {bar:g} at least {C4_BARS:g} clear of static_wear ({VIEW}.nif)",
                  "; ".join(f"{lb} {gp:.2f} (at {at:+.0f})" for lb, gp, at in sorted(gaps, key=lambda x: x[1])[:6]))


def knee_checks(rep, clips: Path, meshes: Path, pyn: Path):
    """The rider's legs against the helmets in every riding clip (the package's CMB_Rider and its Female folder): the
    legs' bone lines (thigh to calf to foot, the clips' own joints through PyNifly's Fallout 4 skeleton.nif for the
    hierarchy) in the bike's frame (CMB_RiderSeat.json: the bike rides on its bone through its bind), their least distance
    to each helmet and, for comparison, to its plate. The flesh round the bones is not here (no body mesh): the clearance
    printed is that distance less LEG_RADIUS, an estimate; the game is the proof (TESTING step 1)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import riding_anims as R
    from rigmath import Rig
    A = R.load_anim_module(pyn)
    from pyn.pynifly import NifFile
    sk = NifFile(str(pyn / "skeletons" / "FO4" / "skeleton.nif"))
    view = BC.Nif((meshes / f"{VIEW}.nif").read_bytes())
    targets = {label: _shape_full(view, f"{VIEW}_{label}")[0] for label in C3_LABELS + tuple(EP.PLATES.values())}
    legs = (("LLeg_Thigh", "LLeg_Calf"), ("LLeg_Calf", "LLeg_Foot"), ("RLeg_Thigh", "RLeg_Calf"), ("RLeg_Calf", "RLeg_Foot"))
    best = {label: (np.inf, "") for label in targets}
    nclips = nframes = 0
    for folder in (clips, clips / "Female"):
        seat = folder / "CMB_RiderSeat.json"
        if not seat.exists():
            continue
        js = json.loads(seat.read_text())
        bind = np.array(js["transform"], np.float64)
        for path in sorted(folder.glob("*.hkx")):
            a = A.load_fo4_animation(str(path))
            names = list(a.bone_names)
            if not all(b in names for b in ("COM",) + tuple(x for l in legs for x in l)):
                continue
            parents = []
            for nm in names:
                node = sk.nodes.get(nm)
                p = node.parent if node is not None else None
                while p is not None and p.name not in names:
                    p = p.parent
                parents.append(names.index(p.name) if p is not None else -1)
            if any(p >= i for i, p in enumerate(parents)):
                order_ok = False
            else:
                order_ok = True
            rig = Rig(names=names, parents=parents, ref_t=np.zeros((len(names), 3)), ref_q=np.tile([0, 0, 0, 1.0], (len(names), 1)))
            com = names.index("COM")
            nclips += 1
            for fi in range(a.num_frames):
                lt = np.array([a.tracks[i].translations[fi] for i in range(len(names))], np.float64)
                lq = np.array([a.tracks[i].rotations[fi] for i in range(len(names))], np.float64)
                if order_ok:
                    G = rig.fk(lt, lq)
                else:
                    G = np.zeros((len(names), 4, 4))
                    done = np.zeros(len(names), bool)
                    from rigmath import compose, q_to_mat
                    while not done.all():
                        for i, p in enumerate(parents):
                            if not done[i] and (p < 0 or done[p]):
                                loc = compose(lt[i], q_to_mat(lq[i]))
                                G[i] = loc if p < 0 else G[p] @ loc
                                done[i] = True
                to_bike = bind @ np.linalg.inv(G[com])
                pts = {nm: (to_bike @ G[names.index(nm)][:, 3])[:3] for pair in legs for nm in pair}
                nframes += 1
                for label, v in targets.items():
                    for a0, a1 in legs:
                        p0, p1 = pts[a0], pts[a1]
                        e = p1 - p0
                        t = np.clip((v - p0) @ e / max(e @ e, 1e-9), 0, 1)
                        d = float(np.linalg.norm(v - (p0 + t[:, None] * e), axis=1).min())
                        if d < best[label][0]:
                            best[label] = (d, f"{path.parent.name}/{path.stem} frame {fi} {a0}-{a1}")
    if not nframes:
        rep.info("c3 knees", f"no riding clip with the leg bones in {clips}")
        return
    helm = {lb: x for lb, x in best.items() if lb in C3_LABELS}
    worst = min(x[0] for x in helm.values())
    rep.check(worst - LEG_RADIUS > 0.0,
              f"c3 knees: in {nclips} riding clips ({nframes} frames, male and female) the legs' bone lines at least "
              f"{worst:.1f} from the helmets (an estimated flesh of {LEG_RADIUS:g} round them leaves {worst - LEG_RADIUS:.1f}; "
              f"the plates, for comparison: " + ", ".join(f"{lb} {best[lb][0]:.1f}" for lb in EP.PLATES.values()) + ")",
              "; ".join(f"{lb} {d:.1f} ({where})" for lb, (d, where) in helm.items()))


def shadow_checks56(rep, shadow_of, roles, parked_names, materials, bgsmaterial):
    """The shadows' rule since the 2026-11-10a build (test 52's wish, the front wheel's shadow; test 34's "no shadow
    from the front end" dropped: harley_meshes.load_shaders): in the worn and view nifs each shape's cast-shadow bit
    is the parked nif's same label's (a label the parked nif draws with its _off file, an under-bar mirror: its own
    parked materials file's, the one a swap shows there), the lit overlays (WORN_ONLY) and the decals
    (static_plateText, static_badgeFender) none; every _worn materials file casts as its parked twin (one with no
    twin, a lit overlay's: none); the front rims' finishes (rimF_*_worn, castF_*_worn: the Rims options' files) cast."""
    parked = shadow_of.get("CMB_BikeParked", {})
    opened = {}

    def file_casts(leaf):   # cmb\bike\<name>.bgsm (lower case): its cast_shadows, None when the file isn't there
        if leaf not in opened:
            path = materials.get(leaf)
            opened[leaf] = None if path is None else bool(bgsmaterial.MaterialFile.Open(str(path)).castShadows)
        return opened[leaf]

    for stem in WORN + (VIEW,):
        got = shadow_of.get(stem)
        if got is None:
            continue
        bad, front = [], 0
        for label, cast in got.items():
            if label in SHADOW_OFF56:
                want, why = False, "a lit overlay or decal"
            elif parked_names.get(label, "").lower().endswith("_off.bgsm"):
                want, why = file_casts(f"cmb\\bike\\{label.lower()}.bgsm"), f"its parked file {label}.bgsm"
            elif SPLIT_FROM.get(label, label) in parked:
                twin = SPLIT_FROM.get(label, label)
                want, why = parked[twin], "the parked nif's" + (f" {twin} (it was cut from it)" if twin != label else "")
            else:
                bad.append(f"{label}: not in the parked nif")
                continue
            if want is None:
                bad.append(f"{label}: {why} missing")
                continue
            if cast != want:
                bad.append(f"{label} {'casts' if cast else 'no shadow'} ({why}: {'casts' if want else 'none'})")
            front += cast and roles.get(label) in H.FRONT_ROLES
        rep.check(not bad, f"{stem}: each shape casts a shadow as the parked bike's same label, the front end too "
                           f"({front} of its shapes cast), the lit overlays and decals none", "; ".join(bad[:12]))
    worn_files = sorted(k for k in materials if k.startswith("cmb\\bike\\") and k.endswith("_worn.bgsm"))
    if not worn_files:
        return
    bad, alone = [], []
    for leaf in worn_files:
        twin = leaf[:-len("_worn.bgsm")] + ".bgsm"
        cast, want = file_casts(leaf), file_casts(twin)
        name = materials[leaf].name
        if want is None:
            alone.append(name)
            if cast:
                bad.append(f"{name} casts (no parked twin: a lit overlay's)")
        elif cast != want:
            bad.append(f"{name} {'casts' if cast else 'no shadow'}, "
                       f"{materials[twin].name} {'casts' if want else 'none'}")
    rep.check(not bad, f"materials files: each of the {len(worn_files)} _worn files casts as its parked twin "
                       f"({len(alone)} without one, none of them casting: {', '.join(alone)})",
              f"{len(bad)} differ: " + "; ".join(bad[:12]) if bad else "")
    finishes = [k for k in worn_files if materials[k].name.lower().startswith(("rimf_", "castf_"))]
    off = [materials[k].name for k in finishes if not file_casts(k)]
    if finishes:
        rep.check(not off, f"materials files: the front rims' {len(finishes)} finishes (rimF_*_worn, castF_*_worn) "
                           "cast", ", ".join(off))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pynifly", type=Path, required=True)
    ap.add_argument("--data", type=Path, required=True, help="the Data tree (Meshes/CMB, Textures/CMB, Materials/CMB)")
    ap.add_argument("--reference", type=Path, help="the reference build's Meshes/CMB (27c)")
    ap.add_argument("--stage-dir", type=Path, help="the stage export the build was made from (per-material totals)")
    ap.add_argument("--look-reference", type=Path,
                    help="the previous build's Data tree (2026-11-02a's): the chrome's and the wheels' textures must be its bytes")
    ap.add_argument("--look-options", type=Path,
                    help="the customisation build's option table (default: tools/esp-generator/look_options.json when the "
                         "nifs are that build's, harley_meshes.py --look-slots 1); given, the nifs must be that build's")
    ap.add_argument("--c2-reference", type=Path,
                    help="2026-11-07a's Data (the second customisation build's reference): static_black and static_plate "
                         "together its static_black, CMB_BikeParts.ini and CMB_BikeFit.json its bytes")
    ap.add_argument("--look-c2", action="store_true",
                    help="the nifs must be the second customisation build's (2026-11-08a: harley_meshes.py --look-rims 1 "
                         "--look-plate 1); without it, its checks run when the nifs have its shapes")
    ap.add_argument("--look-c3", action="store_true",
                    help="the nifs must have the C3 helmets (2026-11-16a, look_emblems.py); without it, its checks run when "
                         "the nifs have them")
    ap.add_argument("--look-c4", action="store_true",
                    help="the nifs must have art build B's shapes (2026-11-21a, look_shells.py: the wear shells and the "
                         "front fender's badge patch); without it, its checks run when the nifs have them")
    ap.add_argument("--ground-field", type=Path,
                    help="unit B's badges.json: the helmets' grounds' enamel fields (default the outline recorded in "
                         "emblem_pieces.GROUND_FIELD_UV)")
    ap.add_argument("--knees", type=Path,
                    help="the riding clips' folder (Meshes/Actors/Character/Animations/MT/CMB_Rider): the legs against the "
                         "helmets in every clip (C3)")
    ap.add_argument("--look-targets", choices=("art", "all"), default="art",
                    help="art (until the art unit's files are in the tree): the badge materials files (badge_*.bgsm) the "
                         "option table's swaps target are listed when missing; all: every target must be there")
    args = ap.parse_args()
    sys.path.insert(0, str(args.pynifly))
    import logging
    logging.disable(logging.WARNING)   # PyNifly's "could not find materials file" for every named shape
    from pyn import pynifly as P  # noqa: E402
    from pyn import bgsmaterial  # noqa: E402
    from pyn.niflydll import nifly  # noqa: E402

    rep = Report()
    meshes = args.data / "Meshes" / "CMB"
    textures = files_by_lower(args.data / "Textures")
    materials = files_by_lower(args.data / "Materials")
    manifest = None
    if args.stage_dir and (args.stage_dir / "manifest.json").exists():
        manifest = json.loads((args.stage_dir / "manifest.json").read_text())
    # the shapes this build made: the stage's (28 with --disc model), else harley_meshes.LABELS (30), or LOOK_LABELS (33)
    # when the worn nif has the customisation build's fender patch
    if manifest:
        labels = list(manifest["labels"])
    else:
        worn0 = meshes / "CMB_BikeWorn.nif"
        wb = worn0.read_bytes() if worn0.exists() else b""
        look0 = f"CMB_BikeWorn_{H.FENDER_BADGE}".encode() in wb
        rims0, plate0 = f"CMB_BikeWorn_{H.RIM_STYLE_LABELS[0][0]}".encode() in wb, f"CMB_BikeWorn_{H.PLATE_TEXT}".encode() in wb
        labels = [label for label, _ in (H.look_labels(rims0, plate0) if look0 else H.LABELS)]
        if f"CMB_BikeWorn_{BC.LABEL}".encode() in wb:   # 2026-11-15b: bar_cables.py's split, after the build's shapes
            labels.append(BC.LABEL)
        if f"CMB_BikeWorn_{C3_LABELS[0]}".encode() in wb:   # 2026-11-16a: look_emblems.py's helmets, after those
            labels += list(C3_LABELS)
        if f"CMB_BikeWorn_{C4_LABELS[0]}".encode() in wb:   # 2026-11-21a: look_shells.py's shells and patch, after those
            labels += list(C4_LABELS)
    roles = dict(H.LABELS + H.LOOK_LABELS + H.C2_LABELS + ((BC.LABEL, "front"),) + tuple((x, "") for x in C3_LABELS)
                 + (("static_wear", ""), ("fork_wear", "fork"), (C4_PATCH, "fork")))
    look = H.FENDER_BADGE in labels   # the customisation build's nifs (2026-11-07a, --look-slots 1)
    look_path = args.look_options or (LOOK_OPTIONS if look and LOOK_OPTIONS.exists() else None)
    look_opts = json.loads(look_path.read_text()) if look_path else None
    swap_files = set()   # the option table's MSWP sources and targets (cmb\bike\<name>.bgsm, lower case)
    if look_opts:
        for slot in look_opts["slots"]:
            for o in slot["options"]:
                for pair in o["swap"] or []:
                    swap_files.update(x.replace("/", "\\").lower() for x in pair)
        for pair in look_opts.get("rim_body_targets", []):   # 2026-11-08a: Compose's own targets, the body finishes' bodyhue
            swap_files.update(x.replace("/", "\\").lower() for x in pair)   # twins (Free colour), which no MSWP names
    if args.look_options:
        rep.check(look, "custom: the customisation build's shapes (harley_meshes.py --look-slots 1: "
                        f"{', '.join(H.BADGE_SPLIT + (H.FENDER_BADGE,))})", "" if look else f"{len(labels)} shapes, none of them")

    def block(f, s):
        sp = s.properties
        return P.NiShader(file=f, id=sp.shaderPropertyID, parent=s)

    def slots(f, s):
        out = {}
        for i in range(10):
            buf = create_string_buffer(512)
            nifly.getShaderTextureSlot(f._handle, s._handle, i, buf, 512)
            if buf.value:
                out[i] = buf.value.decode("utf-8", "replace")
        return out

    # --- shapes and shaders -------------------------------------------------------------------------------------
    named = {}            # material file name (lower) -> [(nif, shape, block props, slots)]
    used_textures = set()
    worn_geo = {}         # label -> (verts, tris, uvs) from CMB_BikeWorn.nif
    worn_names = {}       # label -> CMB_BikeWorn.nif's materials file name
    parked_geo = {}       # label -> verts from CMB_BikeParked.nif (full precision)
    parked_names = {}     # label -> CMB_BikeParked.nif's materials file name
    parked_flags = {}     # label -> its node flags
    shadow_of = {}        # nif stem -> {label: its shader block's cast-shadow bit} (shadow_checks56)
    for stem in WORN + ("CMB_BikeParked",):
        path = meshes / f"{stem}.nif"
        if not path.exists():
            if stem in ("CMB_BikeWorn", "CMB_BikeParked"):
                rep.check(False, f"{stem}.nif", "missing")
            else:
                rep.info(f"{stem}.nif", "not built (no --seat)")
            continue
        f = P.NifFile(str(path))
        worn = stem != "CMB_BikeParked"
        shapes = list(f.shapes)
        if worn:
            want = [f"{stem}_{label}" for label in labels]
            got = [s.name for s in shapes]
        else:
            want = ["Motorcycle:0"] + [f"CMB_Bike_{label}" for label in labels if label not in H.WORN_ONLY + RIDDEN_ONLY]
            got = [s.name for s in shapes]
        rep.check(got == want, f"{stem}: {len(got)} shapes named and ordered as LABELS",
                  "" if got == want else f"missing {sorted(set(want) - set(got))}, extra {sorted(set(got) - set(want))}")
        if not worn:
            hidden = sorted(s.name for s in shapes if s.flags & 1)
            want_hidden = sorted(["Motorcycle:0"] + ([] if look else [f"CMB_Bike_{label}" for label in H.PARKED_HIDDEN]))
            rep.check(hidden == want_hidden, f"{stem}: hidden by the node flag: {hidden}")
        bad_flags, too_big, bad_uv, bad_shadow, bad_skin, names = [], [], [], [], [], set()
        for s in shapes:
            if s.name == "Motorcycle:0":
                continue
            label = s.name[len(stem) + 1:] if worn else s.name[len("CMB_Bike_"):]
            sp = s.properties
            if sp.vertexCount > H.MAX_VERTS:
                too_big.append(f"{label} {sp.vertexCount}")
            uv = np.asarray(s.uvs, dtype=np.float64)
            top = 1 + 1e-4
            if label == H.PLATE_LABEL:   # 2026-11-08a: its edges on the design cell's strip, past 1 (bike_pieces.PLATE_STRIP_V)
                import bike_pieces as BPc
                top = BPc.PLATE_STRIP_V + BPc.PLATE_STRIP_DV + 1e-3
            if len(uv) and (uv.min() < -1e-4 or uv[:, 0].max() > 1 + 1e-4 or uv[:, 1].max() > top):
                bad_uv.append(f"{label} [{uv.min():.3f},{uv.max():.3f}]")
            if (sp.skinInstanceID != P.NODEID_NONE) != worn:
                bad_skin.append(label)
            sh = block(f, s)
            p = sh.properties
            sf1, sf2 = p.Shader_Flags_1, p.Shader_Flags_2
            # No root material: none, or (in the parked nif, whose string table the vanilla's shares) an empty string
            root = f.get_string(p.rootMaterialNameID) if p.rootMaterialNameID != P.NODEID_NONE else ""
            if sf1 & 0x100 or sf2 & 0x8000 or not 0.0 <= p.Glossiness <= 1.0 or root or bool(sf1 & H.SF1_SKINNED) != worn:
                bad_flags.append(f"{label} SF1 {sf1:#x} SF2 {sf2:#x} smooth {p.Glossiness:g} root {root!r}")
            shadow_of.setdefault(stem, {})[label] = bool(sf1 & H.SF1_CAST_SHADOWS)
            if not worn and label == "front_glow" and max(p.Emissive_Color[0], p.Emissive_Color[1], p.Emissive_Color[2]) > 0:
                bad_shadow.append("front_glow lit on the parked bike")
            sl = slots(f, s)
            used_textures.update(sl.values())
            name = sh.name or ""
            names.add(bool(name))
            if name:
                named.setdefault(name.lower(), []).append((stem, label, p, sl))
                if not name.lower().startswith("materials\\cmb\\bike\\") or name.lower().endswith("_worn.bgsm") != worn:
                    bad_flags.append(f"{label} material name {name}")
            if stem == "CMB_BikeWorn":
                worn_geo[label] = (np.asarray(s.verts, dtype=np.float64), np.asarray(s.tris, dtype=np.int64), uv)
                worn_names[label] = name
            if not worn:
                parked_geo[label] = np.asarray(s.verts, dtype=np.float64)
                parked_names[label] = name
                parked_flags[label] = s.flags
        rep.check(not too_big, f"{stem}: at most {H.MAX_VERTS} vertices a shape", ", ".join(too_big))
        rep.check(not bad_uv, f"{stem}: UVs in 0..1", ", ".join(bad_uv))
        rep.check(not bad_skin, f"{stem}: {'skinned' if worn else 'not skinned'}", ", ".join(bad_skin))
        rep.check(not bad_flags, f"{stem}: Fallout 4 flags, smoothness 0..1, no root material, material names", "; ".join(bad_flags))
        if not worn:
            rep.check(not bad_shadow, f"{stem}: the lamp unlit", ", ".join(bad_shadow))
        rep.check(len(names) <= 1, f"{stem}: material names all set or all empty")

    # --- the view nif (the bike in first person, since the 2026-11-01a build) ------------------------------------
    view_path = meshes / f"{VIEW}.nif"
    if not view_path.exists():
        rep.check(False, f"{VIEW}.nif", "missing (harley_meshes.py --view 1)")
    else:
        f = P.NifFile(str(view_path))
        shapes = list(f.shapes)
        want = [f"{VIEW}_{label}" for label in labels]
        got = [s.name for s in shapes]
        rep.check(got == want, f"{VIEW}: {len(got)} shapes named and ordered as the worn nif's",
                  "" if got == want else f"missing {sorted(set(want) - set(got))}, extra {sorted(set(got) - set(want))}")
        blocks = [name for _, name in _block_offsets(view_path.read_bytes())]
        skinned = [s.name for s in shapes if s.properties.skinInstanceID != P.NODEID_NONE]
        rep.check(not skinned and not any(b.startswith("bhk") or b.startswith("BSSkin") for b in blocks),
                  f"{VIEW}: no skin, no collision block", f"skinned {skinned}; blocks {sorted(set(blocks))}")
        parents = set()
        node_flags = None
        for s in shapes:
            par = s.parent
            parents.add(par.name if par is not None else None)
            if par is not None and par.name == VIEW:
                node_flags = par.flags
        rep.check(parents == {VIEW} and node_flags is not None and node_flags & 1,
                  f"{VIEW}: every shape under the NiNode {VIEW}, hidden by its flag bit 0",
                  f"parents {sorted(map(str, parents))}, flags {node_flags}")
        seat_at = None
        bad_v, bad_m, bad_sh, worst_parked, worst_worn = [], [], [], 0.0, 0.0
        for s in shapes:
            label = s.name[len(VIEW) + 1:]
            v = np.asarray(s.verts, dtype=np.float64)
            sh = block(f, s)
            p = sh.properties
            if (sh.name or "") != worn_names.get(label, ""):
                bad_m.append(f"{label} {sh.name!r} (worn {worn_names.get(label)!r})")
            if p.Shader_Flags_1 & H.SF1_SKINNED:
                bad_sh.append(f"{label} SF1 {p.Shader_Flags_1:#x}")
            shadow_of.setdefault(VIEW, {})[label] = bool(p.Shader_Flags_1 & H.SF1_CAST_SHADOWS)
            if label in parked_geo and len(parked_geo[label]) == len(v):
                pk = parked_geo[label]
                if seat_at is None:
                    seat_at = float(np.median(v[:, 1] + pk[:, 1]))
                turned = np.column_stack([-pk[:, 0], seat_at - pk[:, 1], pk[:, 2]])
                d = float(np.abs(v - turned).max()) if len(v) else 0.0
                worst_parked = max(worst_parked, d)
                if d > 1e-4:
                    bad_v.append(f"{label} {d:.5f} off the parked nif's")
            if label in worn_geo:
                wv = worn_geo[label][0]
                if len(wv) != len(v):
                    bad_v.append(f"{label} {len(v)} vertices, the worn nif {len(wv)}")
                    continue
                d = np.abs(v - wv)
                worst_worn = max(worst_worn, float(d.max()) if len(v) else 0.0)
                if (d > 1e-4 + np.abs(wv) * 2.0 ** -11).any():   # half floats: within half their step
                    bad_v.append(f"{label} {float(d.max()):.4f} off the worn nif's")
            elif label not in parked_geo:
                bad_v.append(f"{label}: in neither the worn nor the parked nif")
        rep.check(not bad_v, f"{VIEW}: every vertex the worn bike's (the parked nif's turned round to 1e-4, the worn nif's "
                             f"half floats to their rounding)", "; ".join(bad_v[:8]))
        rep.info(f"{VIEW} vertices", f"at most {worst_parked:.6f} off the parked nif's turned round (seat_at {seat_at}), "
                                     f"{worst_worn:.4f} off the worn nif's half floats")
        rep.check(not bad_m, f"{VIEW}: the worn nif's materials files", "; ".join(bad_m[:8]))
        rep.check(not bad_sh, f"{VIEW}: not skinned in the shader flags", "; ".join(bad_sh))
        rep.info(f"{VIEW}.nif", f"{len(shapes)} shapes, {sum(len(s.verts) for s in shapes)} vertices, "
                                f"{view_path.stat().st_size / 1048576:.1f} MB")

    # --- materials files ----------------------------------------------------------------------------------------
    palette_build = any(PureWindowsPath(t).stem.lower() == f"{H.PALETTE.lower()}_d" for t in used_textures)
    rep.info("build", ("the fallback (palette textures)" if palette_build else "textured")
             + (", materials files named" if named else ", no materials files (the shader blocks alone)"))
    missing_mat, mismatch = [], []
    for name, uses in sorted(named.items()):
        path = materials.get(name[len("materials\\"):]) if name.startswith("materials\\") else None
        if path is None:
            missing_mat.append(name)
            continue
        m = bgsmaterial.MaterialFile.Open(str(path))
        t = {k: v.replace("/", "\\").lower() for k, v in m.textures.items()}
        used_textures.update("textures\\" + v for v in m.textures.values())
        for stem, label, p, sl in uses[:1]:
            nif_t = {k: sl.get(i, "").lower().removeprefix("textures\\") for k, i in
                     (("Diffuse", 0), ("Normal", 1), ("Specular", 7), ("EnvMap", 4), ("Glow", 2))}
            for k, v in nif_t.items():
                if t.get(k, "") != v:
                    mismatch.append(f"{name} {k}: bgsm {t.get(k, '')!r} nif {v!r}")
            env = bool(p.Shader_Flags_1 & H.SF1_ENV_MAP)
            if bool(m.environmentMapping) != env:
                mismatch.append(f"{name}: environment mapping bgsm {m.environmentMapping} nif {env}")
            if bool(m.glowmap) != bool(p.Shader_Flags_2 & H.SF2_GLOW_MAP):
                mismatch.append(f"{name}: glow map bgsm {m.glowmap}")
            if bool(m.twoSided) != bool(p.Shader_Flags_2 & H.SF2_DOUBLE_SIDED):
                mismatch.append(f"{name}: two-sided bgsm {m.twoSided}")
            if bool(m.castShadows) != bool(p.Shader_Flags_1 & H.SF1_CAST_SHADOWS):
                mismatch.append(f"{name}: shadows bgsm {m.castShadows}")
            lit = max(p.Emissive_Color[0], p.Emissive_Color[1], p.Emissive_Color[2]) > 0
            if bool(m.emitEnabled) != lit:
                mismatch.append(f"{name}: emissive bgsm {m.emitEnabled} nif {lit}")
            if abs(m.smoothness - p.Glossiness) > 1e-3:
                mismatch.append(f"{name}: smoothness bgsm {m.smoothness:g} nif {p.Glossiness:g}")
    if named:
        rep.check(not missing_mat, f"materials files: {len(named)} named, every one in {args.data / 'Materials'}", ", ".join(missing_mat))
        ours = [k for k in materials if k.startswith("cmb\\bike\\") and k.endswith(".bgsm")]
        unused = sorted(k for k in ours if "materials\\" + k not in named and k not in swap_files)
        rep.check(not unused, f"materials files: every one of the {len(ours)} in Materials\\CMB\\Bike named by a nif"
                              + (" or by the option table's swaps" if swap_files else "") + " (none shipped unused)",
                  ", ".join(unused))
        for k in sorted(swap_files):   # the swaps' materials files there: their textures are checked as the nifs' are
            path = materials.get(k)
            if path is not None and "materials\\" + k not in named:
                used_textures.update("textures\\" + v for v in bgsmaterial.MaterialFile.Open(str(path)).textures.values() if v)
        rep.check(not mismatch, "materials files read back (PyNifly) agree with the nifs' blocks", "; ".join(mismatch[:12]))

    # --- shadows (2026-11-10a: the front end casts as the parked bike's) ------------------------------------------
    shadow_checks56(rep, shadow_of, roles, parked_names, materials, bgsmaterial)

    # --- textures -----------------------------------------------------------------------------------------------
    vanilla_cubes = {("textures\\" + c).lower() for k, c in H.CUBES.items() if k != "MR"}
    if look_opts:   # the game's own badge art, by path (look_options.json's badges with art "game")
        for b in look_opts["badges"]:
            for t in (b.get("textures") or {}).values():
                if t:
                    vanilla_cubes.add(("textures\\" + t.replace("/", "\\")).lower())
    look_palettes = set()   # the option table's palettes: one mip, no row blur (2026-11-07a's paint_p; 2026-11-08a's
    if look_opts:           # paint_hue_p, rim_p, plate_p and plate_text_p; 2026-11-16a's seat_p)
        for pal in (look_opts["palette"], look_opts.get("hue_palette"), look_opts.get("rim_palette"),
                    *(look_opts.get("plate_palette") or {}).values(), look_opts.get("seat_palette")):
            if isinstance(pal, dict) and pal.get("texture"):
                look_palettes.add(pal["texture"].replace("/", "\\").lower())
    missing_tex, bad_dds, seen, art_tex = [], [], set(), {}
    for t in sorted({u.lower() for u in used_textures}):
        rel = t.removeprefix("textures\\")
        path = textures.get(rel)
        if path is None:
            if t in vanilla_cubes:
                continue
            owner = art_owner(rel) if args.look_targets == "art" else None
            if owner:   # 2026-11-08a: an art unit's texture (static_plate.bgsm names art-plates' re-sample), until the merge
                art_tex.setdefault(owner, []).append(rel.split("\\")[-1])
                continue
            missing_tex.append(t)
            continue
        if path in seen:
            continue
        seen.add(path)
        hdr = dds_header(path)
        if hdr is None:
            bad_dds.append(f"{rel}: not a DDS")
            continue
        w, h, mips, fmt, cube = hdr
        tex_stem = PureWindowsPath(rel).stem.lower()
        palette = tex_stem.startswith(H.PALETTE.lower() + "_")
        full = int(math.log2(max(w, h))) + 1
        suffix = tex_stem[-2:]
        if palette or rel in look_palettes:
            if fmt != "A8R8G8B8" or (not palette and mips != 1):   # 2026-11-07a's paint palette: one mip, no row blur
                bad_dds.append(f"{rel}: {fmt}, {mips} mips")
            continue
        if mips != full:
            bad_dds.append(f"{rel}: {mips} of {full} mips")
        if fmt.startswith("DX10:98") or fmt.startswith("DX10:99"):
            bad_dds.append(f"{rel}: BC7")
        if suffix in FOURCC_FOR and fmt not in FOURCC_FOR[suffix]:
            bad_dds.append(f"{rel}: {fmt} for {suffix}")
        if suffix == "_e" and not cube:
            bad_dds.append(f"{rel}: not a cube map")
    rep.check(not missing_tex, f"textures: {len(seen)} named, every one in {args.data / 'Textures'} (vanilla cube maps aside"
                               + "".join(f"; {o}'s {len(v)} until the merge" for o, v in sorted(art_tex.items())) + ")",
              ", ".join(missing_tex[:12]))
    for owner, v in sorted(art_tex.items()):
        rep.info(f"textures: {owner}'s not here yet (the merge brings them)", ", ".join(sorted(v)))
    rep.check(not bad_dds, "textures: DDS formats by suffix, every mip, no BC7", "; ".join(bad_dds[:12]))
    bike_tex = args.data / "Textures" / "CMB" / "Bike"
    if bike_tex.exists():
        dds = list(bike_tex.rglob("*.dds"))
        total = sum(p.stat().st_size for p in dds)
        budget = (TEX_BUDGET_C4 if all(lb in labels for lb in C4_LABELS) else TEX_BUDGET_C3 if all(lb in labels for lb in C3_LABELS) else TEX_BUDGET_C2 if any(lb in labels for lb, _ in H.C2_LABELS)
                  else TEX_BUDGET_LOOK if look else TEX_BUDGET)
        rep.check(len(dds) <= budget[0] and total <= budget[1] * 1024 * 1024,
                  f"textures: Textures/CMB/Bike {len(dds)} files, {total / 1048576:.1f} MB of DDS (budget {budget[0]} "
                  f"files, {budget[1]:g} MB)")
    if not palette_build and named:
        # Our mirror cube ships only if a materials file names it (MR, the 2026-11-01a build's mirrors), and then both:
        # the one the nifs name and the +Z-up one TESTING has the tester copy over it if the game shows the sky sideways
        # (a one-file swap, so the same size and format). Since 2026-11-02a the mirrors name the game's, and neither ships.
        cubes = {n: textures.get(f"cmb\\bike\\{n}.dds") for n in ("mirror_cube_e", "mirror_cube_zup_e")}
        ours_named = "textures\\cmb\\bike\\mirror_cube_e.dds" in {u.lower() for u in used_textures}
        if ours_named:
            heads = {n: dds_header(p) if p else None for n, p in cubes.items()}
            same = all(h and h[4] for h in heads.values()) and len({h[:4] for h in heads.values()}) == 1
            rep.check(same, "textures: our mirror cube named, both of ours there, cube maps of the same size and format",
                      "; ".join(f"{n} {h[:4] if h else 'missing'}" for n, h in heads.items()))
        else:
            there = sorted(p.name for p in bike_tex.glob("mirror_cube*_e.dds")) if bike_tex.exists() else []
            rep.check(not there, "textures: no mirror cube of ours in Textures/CMB/Bike (no materials file names it)",
                      ", ".join(there))

    # the mirror glass's colour in each mirror's _d (the stage says which triangles are glass: the model's glass, glTF
    # mesh 59's chrome, and ours, "mirror")
    if manifest and not palette_build and all(label in worn_geo for label in H.MIRROR_VARIANTS if label in labels):
        lines, ok = [], True
        for label in H.MIRROR_VARIANTS:
            if label not in labels:
                continue
            with np.load(args.stage_dir / "shapes" / f"{label}.npz") as e:
                mats_l = np.array(manifest["materials"])[e["mat"]]
                glass = ((mats_l == "mirror") | ((mats_l == "chrome") & (e["src"] == H.MIRROR_GLASS_MESH)))
            v, f, uv = worn_geo[label]
            name = worn_names.get(label, "")
            mfile = materials.get(name.lower()[len("materials\\"):]) if name else None
            dpath = None
            if mfile is not None:
                d_rel = bgsmaterial.MaterialFile.Open(str(mfile)).textures.get("Diffuse", "")
                dpath = textures.get(d_rel.replace("/", "\\").lower())
            if dpath is None or len(f) != len(glass) or not glass.any():
                ok = False
                lines.append(f"{label}: no _d or no glass triangles")
                continue
            img = bc1_level0(dpath)
            hgt, wid = img.shape[:2]
            c = uv[f[glass]].mean(axis=1)
            px = img[np.clip((c[:, 1] * hgt).astype(int), 0, hgt - 1), np.clip((c[:, 0] * wid).astype(int), 0, wid - 1)]
            mean = float(px.mean())
            ok &= MIRROR_GLASS_SRGB[0] <= mean <= MIRROR_GLASS_SRGB[1]
            lines.append(f"{label} {mean:.0f} ({int(glass.sum())} glass triangles)")
        rep.check(ok, f"mirror glass a mid grey in its _d (mean {MIRROR_GLASS_SRGB[0]}-{MIRROR_GLASS_SRGB[1]} sRGB)", "; ".join(lines))

    # --- the look's materials files (2026-11-02a, test 48: the mirrors on the game's cube, the chrome brighter) ------
    if named and not palette_build:
        import bgsm as B   # ours (tools/rider/bgsm.py): every field, ssr included
        mirror_bad, chrome_bad, wheel_bad, mirror_n, chrome_n, wheel_n = [], [], [], 0, 0, 0
        for mat, want in ([(m, "mirror") for m in H.MIRROR_VARIANTS if m in labels] + [(m, "chrome") for m in CHROME_MATS if m in labels] +
                          [(m, "wheel") for m in WHEEL_MATS if m in labels]):
            for worn in ("", "_worn"):
                path = materials.get(f"cmb\\bike\\{mat}{worn}.bgsm".lower())   # the keys are lower case
                if path is None:
                    {"mirror": mirror_bad, "chrome": chrome_bad, "wheel": wheel_bad}[want].append(f"{mat}{worn}.bgsm missing")
                    continue
                m = B.read(path)
                cube = m["textures"].get("envmap", "").replace("/", "\\").lower()
                env, spec, ssr = float(m["env_map_mask_scale"]), float(m["specular_mult"]), bool(m["ssr"])
                if want == "mirror":
                    mirror_n += 1
                    if cube != MIRROR_CUBE or abs(env - MIRROR_ENV) > 1e-6:
                        mirror_bad.append(f"{mat}{worn}: {cube or '(no cube)'} env {env:g}")
                elif want == "chrome":
                    chrome_n += 1
                    if abs(env - CHROME_ENV) > 1e-6 or abs(spec - CHROME_SPEC) > 1e-6 or ssr != CHROME_SSR:
                        chrome_bad.append(f"{mat}{worn}: env {env:g} spec {spec:g} ssr {ssr}")
                else:   # 2026-11-06a: the rims and discs
                    wheel_n += 1
                    if abs(env - WHEEL_ENV) > 1e-6 or abs(spec - WHEEL_SPEC) > 1e-6:
                        wheel_bad.append(f"{mat}{worn}: env {env:g} spec {spec:g}")
        rep.check(not mirror_bad and mirror_n == 2 * sum(m in labels for m in H.MIRROR_VARIANTS),
                  f"look: the mirrors' {mirror_n} materials files name the game's cube ({MIRROR_CUBE}) at env {MIRROR_ENV:g}",
                  "; ".join(mirror_bad))
        rep.check(not chrome_bad and chrome_n == 2 * sum(m in labels for m in CHROME_MATS),
                  f"look: the chrome's {chrome_n} materials files at env {CHROME_ENV:g}, spec mult {CHROME_SPEC:g}, "
                  f"screen-space reflections {'on' if CHROME_SSR else 'off'}", "; ".join(chrome_bad))
        rep.check(not wheel_bad and wheel_n == 2 * sum(m in labels for m in WHEEL_MATS),
                  f"look: the rims' and discs' {wheel_n} materials files at env {WHEEL_ENV:g}, spec mult {WHEEL_SPEC:g}",
                  "; ".join(wheel_bad))
        if args.look_reference:
            # The look is the materials files' alone (2026-11-06a): the chrome's and the wheels' textures are the
            # reference's (the 2026-11-02a build's Data, from the same stage) byte for byte. The rear disc has its own
            # materials files over the front disc's textures ("textures_of"): a map in neither tree is skipped.
            ref_tex = files_by_lower(args.look_reference / "Textures")
            diff, n = [], 0
            for mat in CHROME_MATS + WHEEL_MATS:
                for slot in ("d", "n", "s"):
                    key = f"cmb\\bike\\{mat}_{slot}.dds".lower()
                    a, b = textures.get(key), ref_tex.get(key)
                    if a is None and b is None:
                        continue
                    n += 1
                    if a is None or b is None:
                        diff.append(f"{mat}_{slot}.dds missing")
                    elif a.read_bytes() != b.read_bytes():
                        diff.append(f"{mat}_{slot}.dds differs")
            rep.check(not diff and n, f"look: the chrome's and the wheels' {n} textures the reference's byte for byte (--look-reference; "
                                      f"the materials files alone changed)", "; ".join(diff))
        else:
            rep.info("look", "the chrome's and the wheels' textures not compared (no --look-reference)")

    # --- the parts file and the fit file --------------------------------------------------------------------------
    parts = ini_keys(meshes / "CMB_BikeParts.ini") if (meshes / "CMB_BikeParts.ini").exists() else {}
    rep.check(bool(parts), "CMB_BikeParts.ini there")
    needle_keys = ("NeedlePoint", "NeedleAxis", "NeedleZero", "NeedleMax", "NeedlePerMph")
    rep.check(all(k in parts for k in needle_keys), "CMB_BikeParts.ini: the needle's keys",
              ", ".join(f"{k}={parts.get(k)}" for k in needle_keys))
    if args.reference:
        ref = ini_keys(args.reference / "CMB_BikeParts.ini")
        diff = [f"{k}: {v} -> {parts.get(k)}" for k, v in ref.items() if k != "FrontMinY" and parts.get(k) != v]
        rep.check(not diff, f"CMB_BikeParts.ini: the reference's {len(ref) - 1} keys but FrontMinY the same", "; ".join(diff))
        rep.info("FrontMinY", f"{ref.get('FrontMinY')} -> {parts.get('FrontMinY')}")
        same = (meshes / "CMB_BikeFit.json").read_bytes() == (args.reference / "CMB_BikeFit.json").read_bytes()
        rep.check(same, "CMB_BikeFit.json: the reference's bytes")

    # --- overlays, the needle, the mirrors (CMB_BikeWorn.nif: AnimObjectA, its mesh space is the bike's) ---------------
    complete = all(label in worn_geo for label in labels)
    if worn_geo and not complete:
        rep.check(False, "the geometry checks (overlays, needle, mirrors, totals, clamp)", f"CMB_BikeWorn.nif hasn't the {len(labels)} shapes")
    if complete:
        def tris_of(label, sel=None):
            v, f, _ = worn_geo[label]
            t = v[f]
            return t if sel is None else t[sel]

        def gap(verts, tris):
            size = float(np.median(np.ptp(tris, axis=1).max(axis=1)))
            return float(TriangleGrid(tris, max(size, 0.5)).closest(verts, reach=1.0)[2].min())

        v, f, _ = worn_geo["front_dial"]
        n, lab = H.components(len(v), f)
        area = np.linalg.norm(H.face_normals(v, f), axis=1)
        face = lab[f[:, 0]] == np.argmax(np.bincount(lab[f[:, 0]], weights=area, minlength=n))

        def near(label, box_of, pad=3.0):
            t = tris_of(label)
            lo, hi = worn_geo[box_of][0].min(axis=0) - pad, worn_geo[box_of][0].max(axis=0) + pad
            c = t.mean(axis=1)
            return t[np.all((c >= lo) & (c <= hi), axis=1)]

        bases = {"dial face": tris_of("front_dial", face), "front_dialglow": tris_of("front_dialglow"),
                 "tail lens": near("static_glass", "rear_tail"), "tail and signal lenses": near("static_glass", "rear_brake"),
                 "rear_tail": tris_of("rear_tail")}
        lines, ok = [], True
        for name, base, nominal in H.OVERLAY_MIN:
            g = gap(worn_geo[name][0], bases[base])
            ok &= g >= 0.4 * nominal
            lines.append(f"{name} over {base} {g:.3f} ({nominal})")
        rep.check(ok, "overlays clear of what they cover in the worn nif's half floats (at least 0.4 of nominal)", "; ".join(lines))
        if all(k in parts for k in needle_keys[:2]):
            pivot = np.array([float(x) for x in parts["NeedlePoint"].split(",")])
            axis = H.unit(np.array([float(x) for x in parts["NeedleAxis"].split(",")]))
            data = (meshes / "CMB_BikeWorn.nif").read_bytes()
            bone = [off for off, name in _block_offsets(data) if name == "BSSkin::BoneData"]
            i = labels.index("front_needle")
            c = np.array(struct.unpack_from("<3f", data, bone[i] + 4))
            r = struct.unpack_from("<f", data, bone[i] + 16)[0]
            nv = worn_geo["front_needle"][0]
            reach = float(np.linalg.norm(nv - pivot, axis=1).max())
            height = (nv - pivot) @ axis
            rep.check(len(bone) == len(labels) and np.linalg.norm(c - pivot) < 0.02 and r >= reach + 0.5,
                      "the needle's culling sphere on NeedlePoint, past its tip",
                      f"centre {np.round(c, 2).tolist()} r {r:.2f}; NeedlePoint {pivot.tolist()}, the needle reaches {reach:.2f}")
            up = H.unit(np.array([0.0, 0.0, 1.0]) - axis[2] * axis)
            right = np.cross(up, axis)   # the rider's right looking at the dial
            tip = nv[np.argmax(np.linalg.norm(nv - pivot, axis=1))] - pivot
            angle = math.degrees(math.atan2(tip @ right, tip @ up))
            rep.check(abs(height).max() < 0.5, "the needle lies over the dial at the pivot's height",
                      f"{height.min():+.2f}..{height.max():+.2f} along NeedleAxis")
            rep.info("needle at rest", f"tip {angle:+.1f} degrees from the dial's up, clockwise as the rider sees it "
                                       f"(0 mph; NeedleZero {parts.get('NeedleZero')}, NeedleMax {parts.get('NeedleMax')}, "
                                       f"NeedlePerMph {parts.get('NeedlePerMph')})")
        # the mirrors against the tank at every bar angle
        sp = np.array([float(x) for x in parts.get("SteerPoint", "0,0,0").split(",")])
        ax = H.unit(np.array([float(x) for x in parts.get("SteerAxis", "0,0,1").split(",")]))
        bar = float(parts.get("BarAngle", "20"))
        tv, tf, _ = worn_geo["static_paint"]
        tank = tv[tf][np.all(tv[tf][:, :, 1] > 5.0, axis=1)]   # the tank (the rear fender is behind the seat)
        lines, ok = [], True
        for label in H.MIRROR_VARIANTS:   # the worn nif's (half float) vertices, as the plugin turns them
            best, at = H.turning_clearance(worn_geo[label][0], tank, sp, ax, bar)
            ok &= best >= H.MIRROR_CLEARANCE
            lines.append(f"{label} {best:.2f}")
        rep.check(ok, f"mirrors at least {H.MIRROR_CLEARANCE} clear of the tank with the bars within {bar:g} degrees", "; ".join(lines))
        cable_checks(rep, meshes, labels, worn_geo, parts, tank)

    # --- totals ---------------------------------------------------------------------------------------------------
    if complete:
        print("      shape                    verts    tris")
        for label in labels:
            v, f, _ = worn_geo[label]
            print(f"      {label:24s} {len(v):6d} {len(f):7d}")
        rep.info("total", f"{sum(len(g[0]) for g in worn_geo.values())} vertices, {sum(len(g[1]) for g in worn_geo.values())} "
                          f"triangles in {len(worn_geo)} shapes")
        mats = None   # per label: material per triangle (names) and whether it's ours (bike_pieces)
        allowed = {}  # material -> the model's triangles the build changed on purpose (the volume guard, our discs)
        if manifest:
            for g in manifest.get("volume_guard", []):
                m = H.STAGE_NAME.get(g["material"], g["material"])
                allowed[m] = allowed.get(m, 0) + g["to"] - g["from"]
                rep.info("volume guard", f"glTF mesh {g['mesh']} {m} ({g['label']}): {g['from']} -> {g['to']} triangles, "
                                         f"volume kept {g['share_from']:.2f} -> {g['share']:.2f}")
            for mesh, n in manifest.get("disc_replaced", {}).items():
                allowed["silver"] = allowed.get("silver", 0) - int(n)
                rep.info("disc replaced", f"glTF mesh {mesh}'s plate, {n} silver triangles of the model's, by our disc")
            mats = {}
            for label in labels:
                with np.load(args.stage_dir / "shapes" / f"{label}.npz") as e:
                    if len(e["tri"]) != len(worn_geo[label][1]):
                        mats = None
                        rep.check(False, f"--stage-dir's {label} has {len(e['tri'])} triangles, the nif {len(worn_geo[label][1])}")
                        break
                    mats[label] = (np.array(manifest["materials"])[e["mat"]], (e["src"] == -1) & (e["piece"] >= 0))
        elif palette_build:
            names = [H.STAGE_NAME.get(m, m) for m in H.MATERIALS]
            mats = {}
            for label in labels:
                v, f, uv = worn_geo[label]
                block = np.floor(uv[f[:, 0], 0] * H.PALETTE_W / H.BLOCK).astype(int)
                mats[label] = (np.array(names)[block], None)
        if args.reference and (args.reference / "CMB_BikeWorn.nif").exists():
            rf = P.NifFile(str(args.reference / "CMB_BikeWorn.nif"))
            ref_tris, ref_mat = 0, {}
            clamp_ref = {}
            for s in rf.shapes:
                uv = np.asarray(s.uvs, dtype=np.float64)
                f = np.asarray(s.tris, dtype=np.int64)
                ref_tris += len(f)
                for b, k in zip(*np.unique(np.floor(uv[f[:, 0], 0] * 128 / 8).astype(int), return_counts=True)):
                    m = H.STAGE_NAME.get(PALETTE_27C[b], PALETTE_27C[b])
                    ref_mat[m] = ref_mat.get(m, 0) + int(k)
                rv = np.asarray(s.verts, dtype=np.float64)
                inside = np.all([(rv[:, i] >= lo) & (rv[:, i] <= hi) for i, (lo, hi) in enumerate(CLAMP_BOX)], axis=0)
                clamp_ref[s.name[len("CMB_BikeWorn_"):]] = int(inside.sum())
            if mats is not None:
                model, ours = {}, {}
                for label, (m, is_ours) in mats.items():
                    for name in np.unique(m):
                        sel = m == name
                        if is_ours is not None:
                            ours[name] = ours.get(name, 0) + int((sel & is_ours).sum())
                            model[name] = model.get(name, 0) + int((sel & ~is_ours).sum())
                        else:
                            model[name] = model.get(name, 0) + int(sel.sum())
                print("      material     27c   model now   ours   model - 27c")
                bad = []
                for name in sorted(set(ref_mat) | set(model) | set(ours)):
                    d = model.get(name, 0) - ref_mat.get(name, 0)
                    print(f"      {name:11s} {ref_mat.get(name, 0):6d} {model.get(name, 0):9d} {ours.get(name, 0):6d} {d:+9d}")
                    expect = (-24 if name == "tex1" else 0) + allowed.get(name, 0)
                    if d != expect and (ours or name not in ("black_m", "mirror", "dial", "needle", "tail_led", "brake_led")):
                        bad.append(f"{name} {d:+d} (allowed {expect:+d})")
                split = bool(ours)
                rep.check(not bad, "triangles per material: the model's as the reference's, but glTF mesh 9's 24 tex1"
                          + (" and the volume guard's and discs' (" + ", ".join(f"{k} {v:+d}" for k, v in sorted(allowed.items()))
                             + ")" if allowed else "")
                          + ("" if split else " (no --stage-dir: black_m not split from ours)"), ", ".join(bad))
                rep.info("triangles", f"reference {ref_tris}, now {sum(len(g[1]) for g in worn_geo.values())} "
                                      f"(ours {sum(ours.values()) if split else '?'})")
            # the lower clamp
            now = {}
            for label, (v, f, _) in worn_geo.items():
                inside = np.all([(v[:, i] >= lo) & (v[:, i] <= hi) for i, (lo, hi) in enumerate(CLAMP_BOX)], axis=0)
                if inside.any():
                    now[label] = int(inside.sum())
            static_now = sum(k for label, k in now.items() if not roles[label])
            static_ref = sum(k for name, k in clamp_ref.items() if name in ("metal", "matte", "glass"))
            rep.check(now.get("front_black", 0) >= 300 and static_ref - static_now >= 300,
                      "the lower triple clamp turns with the bars (front_black)",
                      f"vertices in its box now {now}; the reference's {clamp_ref}")

    # --- the volume guard and our discs (the stage manifest, since the 2026-11-01a build) --------------------------
    if manifest is not None:
        vols = manifest.get("volumes")
        if vols is None:
            rep.check(False, "volumes: the stage manifest lists the closed pieces' volumes", "an export older than the "
                             "2026-11-01a build's: export again")
        else:
            low = sorted((x for x in vols if x["share"] < 0.6), key=lambda x: x["share"])
            rep.check(not low, f"volumes: no closed piece of the model under 0.6 of its volume after the cut ({len(vols)} "
                               f"closed pieces cut; the least {min([x['share'] for x in vols] or [1.0]):.2f})",
                      "; ".join(f"glTF mesh {x['mesh']} ({x['label']}) {x['src_tris']} -> {x['tris']} triangles, "
                                f"{x['share']:.2f}" for x in low[:8]))
        if manifest.get("disc", "model") == "ours":
            lines, ok, bores = [], True, []
            for label in H.DISC_LABELS:
                fit = manifest.get("discs", {}).get(label)
                if fit is None or label not in parked_geo:
                    ok = False
                    lines.append(f"{label}: {'not in the manifest' if fit is None else 'not in the parked nif'}")
                    continue
                pv = parked_geo[label]
                seat = float(manifest["seat_at"])
                wv = np.column_stack([-pv[:, 0], seat - pv[:, 1], pv[:, 2]])   # worn
                ax = np.array(fit["axle_worn"], dtype=np.float64)
                r = np.hypot(wv[:, 1] - ax[1], wv[:, 2] - ax[2])
                dx = max(abs(wv[:, 0].min() - fit["x"][0]), abs(wv[:, 0].max() - fit["x"][1]))
                dr = abs(r.max() - fit["r_out"])
                ok &= dx <= 0.05 and dr <= 0.05
                lines.append(f"{label} x {wv[:, 0].min():.3f}..{wv[:, 0].max():.3f} (the plate's {fit['x'][0]:.3f}.."
                             f"{fit['x'][1]:.3f}), r_out {r.max():.3f} ({fit['r_out']:.3f}), the bore {r.min():.3f} "
                             f"({fit['r_hub']:.3f}), {len(pv)} vertices")
                # the bore and the rim about the disc's own centre (its vertices' box: the rim is a whole polygon), so an
                # axle a few thousandths off doesn't take from the bore what it adds to the rim
                cy, cz = (wv[:, 1].min() + wv[:, 1].max()) / 2, (wv[:, 2].min() + wv[:, 2].max()) / 2
                ro = np.hypot(wv[:, 1] - cy, wv[:, 2] - cz)
                bores.append((label, float(ro.min()), float(ro.max()), float(fit["r_hub"])))
            rep.check(ok, "discs: ours within 0.05 of the model's plate in x and outer radius", "; ".join(lines))
            # 2026-11-02a (review look-2): the bore where the art paints it, inside the bolt heads
            import bike_pieces as BPc
            rule = manifest.get("disc_bore", "bolts")
            blines, bok = [], rule == "shared" and len(bores) == len(H.DISC_LABELS)
            for label, bore, r_out, r_hub in bores:
                want_bore = BPc.DISC_HUB_REF * r_out
                bok &= abs(bore - want_bore) <= 0.005 and bore < r_hub
                blines.append(f"{label} {bore:.4f} ({bore / r_out:.4f} of r_out {r_out:.3f}; {BPc.DISC_HUB_REF} gives "
                              f"{want_bore:.4f}), the bolt heads at {r_hub:.3f}")
            rep.check(bok, f"discs: the bore at {BPc.DISC_HUB_REF} of the outer radius (+-0.005), inside the bolt heads "
                           f"(the manifest's disc_bore {rule!r}: shared wanted)", "; ".join(blines))
            d_path = textures.get("cmb\\bike\\wheelf_disc_d.dds")
            if d_path is not None:
                img = bc1_level0(d_path).astype(np.float64)
                size = img.shape[0]
                u = (np.arange(size) + 0.5) / size
                dy = (u[None, :] - 0.5) * 2 * BPc.DISC_ART_R
                dz = -(u[:, None] - 0.5) * 2 * BPc.DISC_ART_R
                rr = np.hypot(dy, dz)                              # in outer radii, as bike_art.draw_disc
                px = 2 * BPc.DISC_ART_R / size
                ring = (rr >= BPc.DISC_HUB_REF) & (rr <= BPc.DISC_HUB_REF + 3 * px)
                mean = img[ring].mean(axis=0)
                off = float(np.abs(mean - np.array(DISC_CARRIER_SRGB)).max())
                rep.check(off <= 10.0, f"discs: the _d's face ring from the bore out 3 texels the carrier's colour (within 10 "
                                       f"sRGB of {bytes(DISC_CARRIER_SRGB).hex()})",
                          f"mean ({mean[0]:.0f}, {mean[1]:.0f}, {mean[2]:.0f}) over {int(ring.sum())} texels, {off:.0f} off")
            else:
                rep.check(False, "discs: wheelF_disc_d.dds there (the bore's art)")

    # --- the customisation build (2026-11-07a) ------------------------------------------------------------------------
    if look or args.look_options:   # (on another build with --look-options, each fails)
        look_checks(rep, args, look_opts, labels, materials, textures, worn_geo, worn_names, parked_names, parked_flags, P)
    c2 = any(lb in labels for lb, _ in H.C2_LABELS)
    if args.look_c2:
        rep.check(c2, "c2: the second customisation build's shapes (harley_meshes.py --look-rims 1 --look-plate 1)",
                  "" if c2 else f"{len(labels)} shapes, none of them")
    if c2 or args.look_c2:
        c2_checks(rep, args, labels, materials, worn_geo, worn_names, parked_geo, parked_names, P)
    c3 = all(x in labels for x in C3_LABELS)
    if args.look_c3:
        rep.check(c3, "c3: the 2026-11-16a helmets (look_emblems.py)", "" if c3 else f"{len(labels)} shapes, none of them")
    if c3:
        c3_checks(rep, args, meshes, labels, materials, parts)
    c4 = all(x in labels for x in C4_LABELS)
    if args.look_c4:
        rep.check(c4, "c4: the 2026-11-21a wear shells and front fender patch (look_shells.py)",
                  "" if c4 else f"{len(labels)} shapes, none of them")
    if c4:
        c4_checks(rep, args, meshes, labels, materials, parts)

    # --- brand ----------------------------------------------------------------------------------------------------
    hits = []
    fit_credit = json.dumps(H.MODEL_NAME).encode()
    for root in (meshes, args.data / "Textures" / "CMB", args.data / "Materials" / "CMB"):
        if not root.exists():
            continue
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            data = path.read_bytes()
            if path.name == "CMB_BikeFit.json":
                data = data.replace(fit_credit, b'""')
            low = data.lower()
            words = [w.decode() for w in BRAND if w in low]   # six letters or more: never by chance in binary data
            # "883" is: in a binary file's vertex data a run like "B883" turns up by chance, so only its text counts
            # (a nif's header strings and texture paths, a materials file's texture paths, a text file whole)
            if path.suffix.lower() == ".nif":
                text = b"\n".join(nif_texts(data) + [t.encode() for t in used_textures])
            elif path.suffix.lower() in (".bgsm", ".bgem"):
                text = b"\n".join(v.encode() for v in bgsmaterial.MaterialFile.Open(str(path)).textures.values())
            elif path.suffix.lower() == ".dds":
                text = b""
            else:
                text = data
            if b"883" in text:
                words.append("883")
            if words:
                hits.append(f"{path.relative_to(args.data)}: {', '.join(words)}")
    rep.check(not hits, "no brand name in the outputs (the model's credit in CMB_BikeFit.json aside)", "; ".join(hits))

    print(f"{'all checks passed' if not rep.fails else f'{rep.fails} check(s) failed'}")
    return 1 if rep.fails else 0


if __name__ == "__main__":
    sys.exit(main())
