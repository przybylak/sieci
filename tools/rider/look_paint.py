#!/usr/bin/env python3
"""The customisation build's (2026-11-07a, C1) materials that need no bake: the split badges' and the invisible
materials files, and the paint palette (the "Restored" index maps, the palette, a materials file per palette row).

What it writes into --data (Materials\\CMB\\Bike, Textures\\CMB\\Bike):

  the split badges   static_badgeTankL/TankR/Rear(.bgsm, _worn.bgsm): the 2026-11-06a build's static_badge(.bgsm,
                     _worn.bgsm) byte for byte under the new names (they name its static_badge_d/_n/_s.dds), so with the
                     stock options the bike looks as 2026-11-06a's; static_badge.bgsm and _worn.bgsm, which no nif
                     names now (harley_meshes.py --look-slots 1), are taken away
  the invisible      off.bgsm (the swaps' "None" target), static_badgeFender(.bgsm, _worn.bgsm) (the rear fender patch's
                     own: decal on, for the depth bias), front_mirrorUnderEgg_off.bgsm and front_mirrorUnderD_off.bgsm (the
                     parked nif's under-bar mirrors, PARKED_OFF): alpha test 255 over off_d.dds's alpha 0, material alpha
                     0, no shadows (bike_materials.json's "off" and "static_badgeFender"); off_d.dds (4 x 4 BC3, alpha
                     0), off_n.dds (flat) and off_s.dds (no specular), 4 x 4 BC5, every mip
  the palette        static_paint_rf_d.dds (2048, BC1) and fork_paint_rf_d.dds (1024, BC1): the Restored index maps.
                     Each texel's grey is a U of the palette (look_options.json's "palette"."u"): the tank (glTF mesh
                     13 of static_paint) U 56-127, the fenders (mesh 14, and the whole of fork_paint) 136-207, the cream
                     coachline (the tank's texels nearer its hue than the body's) 216-255; the level is the texel's
                     shade, its luminance over its part's colour in 2026-11-06a's diffuse (the body 0.2-1.6 over 72
                     levels, the coachline 0.4-1.4 over 40), so a row of a colour gives that colour shaded as 2026-11-06a
                     shaded its oxblood. The source mesh per texel is the texture stage's bake (tex_cache/<label>/
                     bake.npz "hid", the high mesh hit; the empty texels take their nearest painted texel's part).
                     The mips are made per part (an index can't be averaged: a tank and coachline mix lands in the
                     fenders' U): a mip texel is the coachline when the coachline covers a quarter of its level-0
                     footprint or more (so the line stays to about a quarter texel wide), else its footprint's
                     majority of the tank and the fenders, at the mean U of that part's footprint texels only; BC1
                     blocks that would decode a texel into a segment not its part's (endpoints across the tank and the
                     coachline interpolate through the fenders) are re-encoded on grey endpoints in their parts'
                     segments, each texel on an entry of its own.
                     paint_p.dds: 256 x 64 RGBA8, one mip (a lookup must not blur rows): rows 0-42 the option table's
                     paint_rows (a the tank, b the fenders, c the coachline; U 0-47 primer grey until a later build's
                     rust; the guards 48-55, 128-135, 208-215 blend their neighbours), 43-63 spare (row 42's).
                     static_paint_rf<rr>(.bgsm, _worn.bgsm) and fork_paint_rf<rr>(...) for each row rr (00-42) and
                     _rftest (the colour-index test option: row 42's, CNAM picks another): 2026-11-06a's four paint
                     materials files with the diffuse the index map, the greyscale slot paint_p.dds,
                     grayscale_to_palette_color on and grayscale_to_palette_scale (rr + 0.5) / 64 (the row's centre):
                     4 x 44 = 176 files. Option 0, "Factory", is no row: the identity swap, 2026-11-06a's files.

--check (after a build, or alone on a built tree) checks it all and the palette proof (SP/t49's palette_proof.py's
method with the three segments): 2026-11-06a's own colours (the oxblood 7a1118 tank and fenders, the c8a860 coachline)
as a row, looked up per texel through the index maps as written (BC1 decoded, level 0), give 2026-11-06a's diffuse back
at PROOF_DB or better over the painted texels; at every mip level no painted texel's U (R or G) is in a segment none of
its level-0 footprint's parts has, and at mips 1-3 the coachline's area is at least COACH_KEEP of level 0's (the proof
against 2026-11-06a's own mips 1-3 is printed); every row's BGSM scale is its row's centre and the palette one mip, so no
row reads its neighbours; every source and target of look_options.json's MSWPs that is ours is in the tree, but the art
unit's badge_<key>.bgsm (listed).

    <python with numpy, Pillow, quicktex, texture2ddecoder> -I tools/rider/look_paint.py --data <Data> \\
        --base <2026-11-06a's Data> --stage <the stage folder> [--options look_options.json] [--materials ...] [--check]

Fallout 4 semantics (DESIGN.md, "The bike's look"): there is no diffuse tint for lit materials; the palette lookup
(grayscale_to_palette_color, the greyscale slot, grayscale_to_palette_scale the V, F4SE's MSWP colorIndex the same) is
the one per-material colour the game has. Nothing from the files read is executed.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bgsm as B  # noqa: E402
import write_dds as W  # noqa: E402

FACTORY = ("7a1118", "7a1118", "c8a860")   # 2026-11-06a's paint (bike_materials.json "paint" and its pinstripe)
PRIMER = "6d6d68"                           # U 0-47 until the rust (a later build's Weathered)
BODY_SHADE, COACH_SHADE, PRIMER_SHADE = (0.2, 1.6), (0.4, 1.4), (0.2, 1.6)
TANK_MESH, FENDER_MESH = 13, 14
PROOF_DB = 33.0
COACH_COVER = 0.25   # a mip texel is the coachline from this share of its level-0 footprint up
COACH_KEEP = 0.5     # --check: the coachline's area at mips 1-3 at least this share of level 0's
ROWS = 64
SPLIT = ("static_badgeTankL", "static_badgeTankR", "static_badgeRear")
OFF_FILES = ("off.bgsm", "static_badgeFender.bgsm", "static_badgeFender_worn.bgsm",
             "front_mirrorUnderEgg_off.bgsm", "front_mirrorUnderD_off.bgsm")
PAINT = ("static_paint", "fork_paint")


def lin(c):
    c = np.asarray(c, np.float64)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def srgb(c):
    c = np.clip(np.asarray(c, np.float64), 0.0, None)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def hexlin(h):
    return lin(np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0)


def lum(c):
    return c[..., 0] * 0.2126 + c[..., 1] * 0.7152 + c[..., 2] * 0.0722


def segments(opts):
    u = opts["palette"]["u"]
    return {k: tuple(u[k]) for k in ("primer", "tank", "fenders", "coachline")}


def palette_row(seg, a, b, c, primer=PRIMER):
    """One row (256, 3) linear: each segment its colour x its shade ramp, the guards between blended."""
    row = np.zeros((256, 3))
    ramps = [("primer", hexlin(primer), PRIMER_SHADE), ("tank", hexlin(a), BODY_SHADE), ("fenders", hexlin(b), BODY_SHADE),
             ("coachline", hexlin(c), COACH_SHADE)]
    for key, col, (s0, s1) in ramps:
        u0, u1 = seg[key]
        t = (np.arange(u0, u1 + 1) - u0) / (u1 - u0)
        row[u0:u1 + 1] = col * (s0 + (s1 - s0) * t)[:, None]
    for (k0, _, _), (k1, _, _) in zip(ramps[:-1], ramps[1:]):   # the guards: the left segment's top to the right's foot
        g0, g1 = seg[k0][1], seg[k1][0]
        for i in range(g0 + 1, g1):
            t = (i - g0) / (g1 - g0)
            row[i] = row[g0] * (1 - t) + row[g1] * t
    return row


def to_u8(rgb_lin):
    return np.clip(np.round(srgb(rgb_lin) * 255.0), 0, 255).astype(np.uint8)


def dilate(label, rounds=96):
    """Empty texels (-1) take a neighbour's label, ring by ring (rounds at most; the rest stay -1)."""
    lab = label.copy()
    for _ in range(rounds):
        empty = lab < 0
        if not empty.any():
            break
        new = lab.copy()
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            sh = np.full_like(lab, -1)
            ys = slice(max(dy, 0), lab.shape[0] + min(dy, 0))
            yd = slice(max(-dy, 0), lab.shape[0] + min(-dy, 0))
            xs = slice(max(dx, 0), lab.shape[1] + min(dx, 0))
            xd = slice(max(-dx, 0), lab.shape[1] + min(-dx, 0))
            sh[yd, xd] = lab[ys, xs]
            take = empty & (new < 0) & (sh >= 0)
            new[take] = sh[take]
        if np.array_equal(new, lab):
            break
        lab = new
    return lab


def index_map(d_srgb, hid, seg, label):
    """The Restored index map (H, W) uint8 of one paint texture from its 2026-11-06a diffuse (H, W, 3 sRGB uint8) and
    its source mesh per texel (hid, -1 empty). Parts: 0 the tank, 1 the fenders, 2 the coachline."""
    L = lin(d_srgb.astype(np.float64) / 255.0)
    body, cream = hexlin(FACTORY[0]), hexlin(FACTORY[2])
    ch = L / (L.sum(-1, keepdims=True) + 1e-6)
    near_cream = np.linalg.norm(ch - cream / cream.sum(), axis=-1) < np.linalg.norm(ch - body / body.sum(), axis=-1)
    part = np.full(hid.shape, -1, np.int64)
    if label == "static_paint":
        part[hid == TANK_MESH] = 0
        part[(hid == TANK_MESH) & near_cream] = 2
        part[hid == FENDER_MESH] = 1
    else:
        part[hid >= 0] = 1
    painted = part >= 0
    part = dilate(part)
    part[part < 0] = 0 if label == "static_paint" else 1
    Y = lum(L)
    out = np.zeros(hid.shape, np.float64)
    for p, key, col, (s0, s1) in ((0, "tank", body, BODY_SHADE), (1, "fenders", body, BODY_SHADE),
                                  (2, "coachline", cream, COACH_SHADE)):
        sel = part == p
        u0, u1 = seg[key]
        shade = Y[sel] / lum(col)
        out[sel] = u0 + (u1 - u0) * np.clip((shade - s0) / (s1 - s0), 0, 1)
    return np.clip(np.round(out), 0, 255).astype(np.uint8), part, painted


def grey_rgba(g):
    return np.dstack([g, g, g, np.full_like(g, 255)])


SEG_KEYS = ("tank", "fenders", "coachline", "primer")   # the parts' segments (index_map's 0, 1, 2), then the primer


def seg_of(u, seg):
    """The segment index (SEG_KEYS) each U is in: its nearest segment (a guard's U goes to its nearer side)."""
    u = np.asarray(u, np.int64)
    return np.stack([np.maximum(0, np.maximum(seg[k][0] - u, u - seg[k][1])) for k in SEG_KEYS]).argmin(0)


def index_levels(g, part):
    """The index map's mip chain per part ([levels], [their parts]), down to 1 x 1: each level's per-part footprint
    share and mean U are the 2 x 2 box of the level above's (so a level's are its level-0 footprint's); a texel is the
    coachline when that share is COACH_COVER or more, else the larger of the tank's and the fenders' (the tank on a
    tie), at its part's mean U. A one-part map gets write_dds's box filter bit for bit."""
    h, w = g.shape
    cov = [(part == p).astype(np.float64) for p in range(3)]
    mean = [g.astype(np.float64) / 255.0 * c for c in cov]
    levels, parts = [g], [part]
    for _ in range(1, 1 + int(np.floor(np.log2(max(h, w))))):
        sums = [W.half(c * m) for c, m in zip(cov, mean)]
        cov = [W.half(c) for c in cov]
        mean = [np.where(c > 0, s / np.where(c > 0, c, 1.0), 0.0) for s, c in zip(sums, cov)]
        p = np.where(cov[2] >= COACH_COVER, 2, np.where(cov[1] > cov[0], 1, 0))
        m = np.choose(p, mean)
        levels.append(np.clip(np.rint(m * 255.0), 0, 255).astype(np.uint8))
        parts.append(p)
    return levels, parts


def _grey565(v):
    r, g_ = int(round(v * 31 / 255)), int(round(v * 63 / 255))
    return (r << 11) | (g_ << 5) | r, ((r << 3) | (r >> 2), (g_ << 2) | (g_ >> 4))


def index_bc1(u, part, seg):
    """One index-map level as BC1 blocks (quicktex's), and any block that decodes a texel's U (R or G) into a segment
    not its part's re-encoded: of every pair of grey endpoints from its texels' U and its parts' means, the one that
    leaves the fewest texels without an entry in their own segment, then the least error, each texel on its nearest
    entry in its own segment (a three-part block can have the fenders on the tank's and the coachline's middle entries).
    Returns (bytes, texels still astray)."""
    import texture2ddecoder as t2d
    data = bytearray(W.compress(grey_rgba(u), "bc1", "auto", opaque=True))
    up = W.pad4(u[..., None])[..., 0].astype(np.float64)
    pp = W.pad4(part[..., None])[..., 0]
    H, Wd = up.shape

    def astray(buf):
        bgra = np.frombuffer(t2d.decode_bc1(bytes(buf), Wd, H), np.uint8).reshape(H, Wd, 4)
        return (seg_of(bgra[..., 2], seg) != pp) | (seg_of(bgra[..., 1], seg) != pp)

    bad = astray(data).reshape(H // 4, 4, Wd // 4, 4).any(axis=(1, 3))
    for by, bx in zip(*np.nonzero(bad)):
        tu = up[by * 4:by * 4 + 4, bx * 4:bx * 4 + 4].ravel()
        tp = pp[by * 4:by * 4 + 4, bx * 4:bx * 4 + 4].ravel()
        codes = dict(_grey565(v) for v in np.concatenate([tu, [tu[tp == q].mean() for q in np.unique(tp)]]))
        pairs = [(a, b) for a in codes for b in codes if a >= b]   # a == b: one colour (indices 0-2 all give it)
        e0 = np.array([codes[a] for a, _ in pairs], np.float64)
        e1 = np.array([codes[b] for _, b in pairs], np.float64)
        ent = np.stack([e0, e1, (2 * e0 + e1) / 3, (e0 + 2 * e1) / 3], 1)   # (pairs, 4, R G); c0 > c1: four colours
        es = seg_of(np.rint(ent), seg)
        own = ((es[..., 0] == es[..., 1])[:, None, :]) & (es[:, None, :, 0] == tp[None, :, None])
        dist = np.abs(ent[:, None, :, 1] - tu[None, :, None])                # (pairs, 16, 4)
        best = np.where(own, dist, np.inf).min(2)
        lost = np.isinf(best)
        cost = lost.sum(1) * 1e6 + np.where(lost, dist.min(2), best).sum(1)
        i = int(cost.argmin())
        c0, c1 = pairs[i]
        idx = np.where(lost[i], dist[i].argmin(1), np.where(own[i], dist[i], np.inf).argmin(1))
        bits = int(sum(int(j) << (2 * k) for k, j in enumerate(idx)))
        o = (by * (Wd // 4) + bx) * 8
        data[o:o + 8] = int(c0).to_bytes(2, "little") + int(c1).to_bytes(2, "little") + bits.to_bytes(4, "little")
    return bytes(data), int((astray(data)[:u.shape[0], :u.shape[1]]).sum())


def index_dds(g, part, seg):
    """The index map's DDS (BC1, legacy header, the per-part mip chain), as write_dds.build writes BC1, and the
    texels left astray per level."""
    levels, parts = index_levels(g, part)
    body, left = b"", []
    for lv, pt in zip(levels, parts):
        b, n = index_bc1(lv, pt, seg)
        body += b
        left.append(n)
    return W.header("bc1", g.shape[1], g.shape[0], len(levels), False, False, False, False) + body, left


def rows_of(opts):
    rows = sorted(opts["paint_rows"], key=lambda r: r["row"])
    if [r["row"] for r in rows] != list(range(len(rows))) or len(rows) > ROWS:
        raise ValueError("look_options.json: paint_rows aren't rows 0.. in order")
    return rows


def palette_image(opts, seg):
    rows = rows_of(opts)
    img = np.zeros((ROWS, 256, 4), np.uint8)
    img[..., 3] = 255
    for r in rows:
        img[r["row"], :, :3] = to_u8(palette_row(seg, r["a"], r["b"], r["c"]))
    for i in range(len(rows), ROWS):
        img[i] = img[len(rows) - 1]
    return img


def paint_targets(opts):
    """{bgsm file name: (source label, worn, row)} of the Paint slot's MSWP targets but the identities."""
    out = {}
    slot = next(s for s in opts["slots"] if s["key"] == "Paint")
    for o in slot["options"]:
        if o["kind"] != "paint":
            continue
        for src, tgt in o["swap"]:
            name = tgt.split("\\")[-1]
            stem = src.split("\\")[-1][:-len(".bgsm")]
            worn = stem.endswith("_worn")
            out[name] = (stem[:-len("_worn")] if worn else stem, worn, int(o["row"]))
    return out


def off_material(spec, decal):
    a = spec.get("alpha") or {}
    return B.new_bgsm(textures={"diffuse": "CMB\\Bike\\off_d.dds", "normal": "CMB\\Bike\\off_n.dds",
                                "smoothspec": "CMB\\Bike\\off_s.dds"},
                      alpha=float(spec.get("material_alpha", 0.0)), alpha_blend=0, alpha_blend_src=6, alpha_blend_dst=7,
                      alpha_test=True, alpha_test_ref=int(a.get("threshold", 255)), decal=bool(decal),
                      two_sided=bool(spec.get("two_sided", True)), environment_mapping=False, env_map_mask_scale=1.0,
                      cast_shadows=False, receive_shadows=True, specular_enabled=True,
                      smoothness=float(spec.get("smoothness", 1.0)), specular_mult=float(spec.get("spec_mult", 1.0)),
                      specular_color=[float(x) for x in spec.get("spec_colour", [1.0, 1.0, 1.0])], root_material="")


def build(args, opts, mats):
    mdir = args.data / "Materials" / "CMB" / "Bike"
    tdir = args.data / "Textures" / "CMB" / "Bike"
    bm = args.base / "Materials" / "CMB" / "Bike"
    bt = args.base / "Textures" / "CMB" / "Bike"
    mdir.mkdir(parents=True, exist_ok=True)
    tdir.mkdir(parents=True, exist_ok=True)
    seg = segments(opts)
    written = []
    # the split badges: static_badge's files under their names; static_badge's own go (no nif names them)
    for label in SPLIT:
        for worn in ("", "_worn"):
            shutil.copyfile(bm / f"static_badge{worn}.bgsm", mdir / f"{label}{worn}.bgsm")
            written.append(f"{label}{worn}.bgsm")
    for worn in ("", "_worn"):
        p = mdir / f"static_badge{worn}.bgsm"
        if p.exists():
            p.unlink()
            print(f"removed {p.name} (no nif names it with --look-slots 1)")
    # the invisible materials and off's textures
    for name in OFF_FILES:
        spec = mats["static_badgeFender"] if name.startswith("static_badgeFender") else mats["off"]
        B.write(mdir / name, off_material(spec, bool(spec.get("decal")) and name.startswith("static_badgeFender")))
        written.append(name)
    z = np.zeros((4, 4, 4), np.uint8)
    (tdir / "off_d.dds").write_bytes(W.build([z], "bc3"))
    flat = np.dstack([np.full((4, 4), 128, np.uint8), np.full((4, 4), 128, np.uint8), np.full((4, 4), 255, np.uint8),
                      np.full((4, 4), 255, np.uint8)])
    (tdir / "off_n.dds").write_bytes(W.build([flat], "bc5", normal=True))
    (tdir / "off_s.dds").write_bytes(W.build([z], "bc5"))
    written += ["off_d.dds", "off_n.dds", "off_s.dds"]
    # the index maps
    for label in PAINT:
        _, faces = W.read_dds(bt / f"{label}_d.dds")
        d = faces[0][0][..., :3]
        with np.load(args.stage / "tex_cache" / label / "bake.npz") as z_:
            hid = z_["hid"].astype(np.int64)
        if hid.shape != d.shape[:2]:
            raise ValueError(f"{label}: the bake's {hid.shape} isn't the diffuse's {d.shape[:2]}")
        g, part, painted = index_map(d, hid, seg, label)
        data, left = index_dds(g, part, seg)
        (tdir / f"{label}_rf_d.dds").write_bytes(data)
        written.append(f"{label}_rf_d.dds")
        print(f"{label}_rf_d.dds: {g.shape[1]}x{g.shape[0]}, painted texels {int(painted.sum())} (tank "
              f"{int(((part == 0) & painted).sum())}, fenders {int(((part == 1) & painted).sum())}, coachline "
              f"{int(((part == 2) & painted).sum())}), {len(left)} mips per part, texels decoding outside their "
              f"part's segment {sum(left)}")
    # the palette, one mip
    (tdir / "paint_p.dds").write_bytes(W.build([palette_image(opts, seg)], "rgba8", mips=1))
    written.append("paint_p.dds")
    # the per-row materials files
    tex_p = opts["palette"]["texture"]
    n = 0
    for name, (label, worn, row) in sorted(paint_targets(opts).items()):
        m = B.read(bm / f"{label}{'_worn' if worn else ''}.bgsm")
        m["textures"]["diffuse"] = f"CMB\\Bike\\{label}_rf_d.dds"
        m["textures"]["greyscale"] = tex_p
        m["grayscale_to_palette_color"] = True
        m["grayscale_to_palette_scale"] = (row + 0.5) / ROWS
        B.write(mdir / name, m)
        n += 1
    written.append(f"{n} paint row materials files")
    print("wrote " + ", ".join(written))
    return 0


def any2(a):
    """The 2 x 2 OR of the last two axes (sides even or 1), as the next mip's footprint."""
    if a.shape[-2] > 1:
        a = a[..., 0::2, :] | a[..., 1::2, :]
    if a.shape[-1] > 1:
        a = a[..., 0::2] | a[..., 1::2]
    return a


def check(args, opts, mats):
    ok = True

    def rep(good, what, detail=""):
        nonlocal ok
        ok &= bool(good)
        print(f"{'PASS' if good else 'FAIL'}  {what}{': ' + detail if detail else ''}")

    mdir = args.data / "Materials" / "CMB" / "Bike"
    tdir = args.data / "Textures" / "CMB" / "Bike"
    bm = args.base / "Materials" / "CMB" / "Bike"
    bt = args.base / "Textures" / "CMB" / "Bike"
    seg = segments(opts)
    # the split badges, byte for byte
    bad = [f"{lb}{w}" for lb in SPLIT for w in ("", "_worn")
           if not (mdir / f"{lb}{w}.bgsm").exists() or (mdir / f"{lb}{w}.bgsm").read_bytes() != (bm / f"static_badge{w}.bgsm").read_bytes()]
    rep(not bad, "the split badges' 6 materials files 2026-11-06a's static_badge(.bgsm, _worn.bgsm) byte for byte", ", ".join(bad))
    # the invisible ones
    bad = []
    for name in OFF_FILES:
        p = mdir / name
        if not p.exists():
            bad.append(f"{name} missing")
            continue
        m = B.read(p)
        if not (m["alpha_test"] and m["alpha_test_ref"] == 255 and m["alpha"] == 0.0 and not m["cast_shadows"]
                and m["textures"]["diffuse"] == "CMB\\Bike\\off_d.dds" and not m["environment_mapping"]):
            bad.append(f"{name}: alpha test {m['alpha_test']} ref {m['alpha_test_ref']} alpha {m['alpha']} shadows "
                       f"{m['cast_shadows']} diffuse {m['textures']['diffuse']}")
        if name.startswith("static_badgeFender") and not m["decal"]:
            bad.append(f"{name}: decal off")
    def dds(path):   # [mips] of the first face, or [] when the file isn't there
        return W.read_dds(path)[1][0] if path.exists() else []

    f = dds(tdir / "off_d.dds")
    a_max = max([int(lv[..., 3].max()) for lv in f] or [255])
    rep(not bad and f and a_max == 0, f"the {len(OFF_FILES)} invisible materials files: alpha test 255, alpha 0, no shadows, "
                                      f"off_d.dds (alpha {a_max} at most, {len(f)} mips)", "; ".join(bad))
    # the palette
    f = dds(tdir / "paint_p.dds")
    pal = f[0] if f else np.zeros((0, 0, 4), np.uint8)
    rep(len(f) == 1 and pal.shape[:2] == (ROWS, 256), f"paint_p.dds 256 x {ROWS}, one mip", f"{pal.shape[1]}x{pal.shape[0]}, "
        f"{len(f)} mips")
    rows = rows_of(opts)
    want = palette_image(opts, seg)
    rep(np.array_equal(pal, want), f"paint_p.dds rows 0-{len(rows) - 1} the option table's paint_rows (and the spare rows row "
                                   f"{len(rows) - 1}'s)")
    # every row's materials file: its row's centre, the palette, the index map, otherwise 2026-11-06a's
    targets = paint_targets(opts)
    bad = []
    for name, (label, worn, row) in sorted(targets.items()):
        p = mdir / name
        if not p.exists():
            bad.append(f"{name} missing")
            continue
        m = B.read(p)
        base = B.read(bm / f"{label}{'_worn' if worn else ''}.bgsm")
        v = m["grayscale_to_palette_scale"] * ROWS - 0.5
        if abs(v - row) > 1e-4 or not m["grayscale_to_palette_color"] or m["textures"]["greyscale"] != opts["palette"]["texture"]:
            bad.append(f"{name}: row {v:.4f} for {row}, palette {m['grayscale_to_palette_color']} {m['textures']['greyscale']!r}")
        if m["textures"]["diffuse"] != f"CMB\\Bike\\{label}_rf_d.dds":
            bad.append(f"{name}: diffuse {m['textures']['diffuse']}")
        for k in base:
            if k.startswith("_") or k in ("textures", "grayscale_to_palette_color", "grayscale_to_palette_scale"):
                continue
            if base[k] != m[k]:
                bad.append(f"{name}: {k} {m[k]!r}, 2026-11-06a's {base[k]!r}")
        for k, t in base["textures"].items():
            if k not in ("diffuse", "greyscale") and t != m["textures"][k]:
                bad.append(f"{name}: texture {k} {m['textures'][k]!r}")
    rep(not bad and len(targets) == 4 * 44, f"the {len(targets)} paint row materials files: grayscale_to_palette_scale at "
                                            f"their row's centre ((row + 0.5) / {ROWS}: no neighbour read), the palette, "
                                            f"the index map, 2026-11-06a's values otherwise", "; ".join(bad[:8]))
    # the proof: 2026-11-06a's colours as a row through the index maps as written
    fac = to_u8(palette_row(seg, *FACTORY)).astype(np.float64) / 255.0
    for label in PAINT:
        _, f0 = W.read_dds(bt / f"{label}_d.dds")
        d = f0[0][0][..., :3].astype(np.float64) / 255.0
        f1 = dds(tdir / f"{label}_rf_d.dds")
        if not f1:
            rep(False, f"palette proof, {label}: {label}_rf_d.dds there")
            continue
        idx = f1[0][..., :3].astype(np.int64)
        with np.load(args.stage / "tex_cache" / label / "bake.npz") as z_:
            painted = z_["hid"] >= 0
        lines, good = [], True
        for c, name in ((0, "R"), (1, "G")):
            rec = fac[np.clip(idx[..., c], 0, 255)]
            mse = float(((rec - d)[painted] ** 2).mean())
            db = 10 * np.log10(1.0 / max(mse, 1e-12))
            good &= db >= PROOF_DB
            lines.append(f"{name} as U {db:.1f} dB")
        g_ = idx[..., 0]
        lines.append(f"{len(f1)} mips, U {int(g_[painted].min())}..{int(g_[painted].max())}")
        rep(good, f"palette proof, {label}: 2026-11-06a's colours as a row through {label}_rf_d.dds (BC1, level 0) give "
                  f"its diffuse back at {PROOF_DB:g} dB or more over the {int(painted.sum())} painted texels", "; ".join(lines))
        # every level: no painted texel's U in a segment none of its level-0 footprint's parts has (a box-filtered
        # index map puts a tank and coachline mix in the fenders'); the coachline kept at mips 1-3
        with np.load(args.stage / "tex_cache" / label / "bake.npz") as z_:
            part = index_map(f0[0][0][..., :3], z_["hid"].astype(np.int64), seg, label)[1]
        has, pt = np.stack([part == p for p in range(3)]), painted
        astray, area, dbs = [], [], []
        for k, lv in enumerate(f1):
            if k:
                has, pt = any2(has), any2(pt)
            if lv.shape[:2] != pt.shape:
                astray.append(-1)
                break
            n = 0
            for c in (0, 1):
                s_ = seg_of(lv[..., c], seg)
                own = np.zeros(pt.shape, bool)
                for p in range(3):
                    own |= (s_ == p) & has[p]
                n = max(n, int((pt & ~own).sum()))
            astray.append(n)
            area.append(int(((seg_of(lv[..., 1], seg) == 2) & pt).sum()) * 4 ** k)
            if 1 <= k <= 3 and k < len(f0[0]) and f0[0][k].shape[:2] == pt.shape:
                rec = fac[np.clip(lv[..., 1].astype(np.int64), 0, 255)]
                mse = float(((rec - f0[0][k][..., :3].astype(np.float64) / 255.0)[pt] ** 2).mean())
                dbs.append(f"mip {k} {10 * np.log10(1.0 / max(mse, 1e-12)):.1f} dB")
        rep(astray and min(astray) == 0 and max(astray) == 0,
            f"{label}_rf_d.dds, all {len(f1)} mips: no painted texel's U (R or G) in a segment none of its level-0 "
            f"footprint's parts has (the index map's mips per part)", "texels per mip " + ", ".join(map(str, astray)))
        if area and area[0]:
            keep = [a / area[0] for a in area[1:4]]
            rep(len(keep) == 3 and min(keep) >= COACH_KEEP, f"{label}_rf_d.dds: the coachline's area at mips 1-3 at "
                f"least {COACH_KEEP:g} of level 0's ({area[0]} texels)", ", ".join(f"{x:.2f}" for x in keep))
        print(f"INFO  {label}: 2026-11-06a's colours through {label}_rf_d.dds's mips (G as U) against 2026-11-06a's own "
              f"mips: {'; '.join(dbs)}")
    # every MSWP source and target that is ours
    names = {p.name.lower() for p in mdir.glob("*.bgsm")}
    art, missing, n = set(), [], 0
    for s in opts["slots"]:
        for o in s["options"]:
            for src, tgt in o["swap"] or []:
                for x in (src, tgt):
                    n += 1
                    leaf = x.split("\\")[-1]
                    if leaf.lower() in names:
                        continue
                    if leaf.lower().startswith("badge_"):
                        art.add(leaf)
                    else:
                        missing.append(leaf)
    rep(not missing, f"look_options.json's MSWPs: {n} sources and targets, every one of ours in {mdir} "
                     f"({len(art)} badge materials files are the art unit's)", ", ".join(sorted(set(missing))[:12]))
    print(f"INFO  the art unit's badge materials files not here: {', '.join(sorted(art))}" if art else "INFO  every badge materials file here")
    print("look_paint: all checks passed" if ok else "look_paint: FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, required=True, help="the Data tree to write (Materials, Textures)")
    ap.add_argument("--base", type=Path, required=True, help="2026-11-06a's Data tree (read only)")
    ap.add_argument("--stage", type=Path, required=True, help="the stage folder (tex_cache/<label>/bake.npz)")
    ap.add_argument("--options", type=Path, default=HERE.parent / "esp-generator" / "look_options.json")
    ap.add_argument("--materials", type=Path, default=HERE / "bike_materials.json")
    ap.add_argument("--check", action="store_true", help="check a built tree (and nothing written)")
    args = ap.parse_args()
    opts = json.loads(args.options.read_text())
    mats = json.loads(args.materials.read_text())["materials"]
    if args.data.resolve() == args.base.resolve():
        ap.error("--data and --base must differ (the base is read only)")
    return check(args, opts, mats) if args.check else build(args, opts, mats)


if __name__ == "__main__":
    sys.exit(main())
