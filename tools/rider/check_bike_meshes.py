#!/usr/bin/env python3
"""Checks a bike build (harley_meshes.py's nifs, and the texture stage's textures and materials) in a Data tree.

  python check_bike_meshes.py --pynifly <io_scene_nifly> --data <Data> [--reference <27c Data>/Meshes/CMB]
      [--stage-dir <stage>] [--look-reference <the previous build's Data>] [--look-options <look_options.json>]
      [--look-targets art|all] [--look-c2]

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
ART_WHEELS = ("rim", "cast", "wheelf_tyre_", "wheelr_tyre_", "paint_hue", "static_paint_hue", "fork_paint_hue", "paint_p")
ART_PLATES = ("plate_", "text_", "plates_", "static_plate_d", "static_plate_n", "static_plate_s")
LOOK_OPTIONS = Path(__file__).resolve().parent.parent / "esp-generator" / "look_options.json"
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
    rep.check(not bad and len(labels) == len(H.look_labels(c2_rims, c2_plate)),
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
    rep.check(labels == want, f"c2: {len(labels)} shapes in the worn and view nifs, {len([x for x in labels if x not in H.WORN_ONLY])} "
                              f"in the parked (49 and 46: 2026-11-07a's 33 and 30, the plate's two, the 14 rim styles)",
              "" if labels == want else f"missing {sorted(set(want) - set(labels))}, extra {sorted(set(labels) - set(want))}")
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
            ours = np.vstack([tri_rows(bv, bf), tri_rows(pv, pf)])
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
    seat_at = json.loads((meshes / "CMB_BikeFit.json").read_text())["seat_at"]
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
            elif label in parked:
                want, why = parked[label], "the parked nif's"
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
    roles = dict(H.LABELS + H.LOOK_LABELS + H.C2_LABELS)
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
            want = ["Motorcycle:0"] + [f"CMB_Bike_{label}" for label in labels if label not in H.WORN_ONLY]
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
    if look_opts:           # paint_hue_p, rim_p, plate_p and plate_text_p)
        for pal in (look_opts["palette"], look_opts.get("hue_palette"), look_opts.get("rim_palette"),
                    *(look_opts.get("plate_palette") or {}).values()):
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
        budget = TEX_BUDGET_C2 if any(lb in labels for lb, _ in H.C2_LABELS) else TEX_BUDGET_LOOK if look else TEX_BUDGET
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
