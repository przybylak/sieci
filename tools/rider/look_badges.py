#!/usr/bin/env python3
"""The faction badges' textures and materials (since the 2026-11-07a build), from bike_art.py --badges' atlas.

    <dds python> -I look_badges.py --art <stage>/art_badges --out <Data-like tree> [--look-options <json>]
    <dds python> -I look_badges.py --check --art <stage>/art_badges --out <tree> [--plate-npz <stage>/shapes/static_badge.npz]
    <dds python> -I look_badges.py --sheet <out.png> --out <tree> [--plate-npz ...]

Writes, under --out (a Data folder's layout):

  Textures\\CMB\\Bike\\badges_d.dds   BC3 2048 with mips (alpha the emblems' outlines), filtered in linear light
  Textures\\CMB\\Bike\\badges_n.dds   BC5 1024 with mips (a normal map: chrome raised, enamel sunk)
  Textures\\CMB\\Bike\\badges_s.dds   BC5 1024 with mips (R specular, G smoothness)
  Materials\\CMB\\Bike\\badge_<key>.bgsm, one per badge of look_options.json (17): the stock badge's material
      (static_badgeTankL.bgsm under --out, else static_badge.bgsm: the chrome cube x0.8, alpha test 128, two-sided;
      decal on for a badge the rear fender patch shows) with
      - ours: the atlas, tiles clamped, and a UV transform taking the plate's rectangle (plate_rect: the same on both
        tank plates and the rear fender patch) to the badge's drawn cell: scale u 0.25 / 0.96, v (213 / 2048) / 0.402,
        offset = the cell's drawn corner minus the rectangle's corner at that scale (uv' = uv x scale + offset);
      - game art (the 4 "(game art)" entries): the game's textures by path, never read here (we hold no game file);
        a chest decal (it has an alpha) as the whole square centred on the plate, at the plate's height; a cloth flag
        (no alpha, the fender only) over the whole patch; painted, so no chrome cube;
      - badge_<key>_r.bgsm too, the u scale negated, if look_options.json's right_mirrored (2026-11-07a: false, both
        plates read true from outside, measured).

--check (no writing): the atlas' sizes and formats; every cell's alpha inside its drawn 512 x 213; the 16-pixel
margin's alpha 0 at every mip it is a texel or more wide; each badge's coverage 25-82 % of the plate's rectangle; with
--plate-npz, the share of each emblem outside what both tank plates show; the 17 materials read back byte for byte
(bgsm.py) and hold the transform, the textures and the flags above; the brand words (check_bike_meshes.py's) in
no badge's name, motif or key; and the guard: no game texture path is a file under --out (nothing of the game copied).

--sheet: a flat contact sheet of every badge on the left and right tank plates (their outlines from --plate-npz, else
the safe hexagon) and the fender patch, over the factory paint, lit simply; game art as a labelled grey stand-in.
"""
import argparse
import ast
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bgsm  # noqa: E402

TEX = ("Textures", "CMB", "Bike")
MAT = ("Materials", "CMB", "Bike")
PAINT = (0x7A, 0x11, 0x18)
# the stock badge's material, the template of ours: the split tank plates' since 2026-11-07a (mesh's tree has no
# static_badge.bgsm; static_badgeTankL.bgsm is 2026-11-06a's static_badge.bgsm byte for byte), else 2026-11-06a's own
TEMPLATES = ("static_badgeTankL.bgsm", "static_badge.bgsm")


def template_path(out):
    for name in TEMPLATES:
        p = Path(out, *MAT, name)
        if p.exists():
            return p
    return Path(out, *MAT, TEMPLATES[-1])


def load_png(path):
    from PIL import Image
    im = Image.open(path)
    im.load()
    return np.asarray(im.convert("RGBA"), dtype=np.uint8).copy()


def brand_words():
    """check_bike_meshes.py's BRAND tuple, read without importing it (it loads the nif tools)."""
    tree = ast.parse((HERE / "check_bike_meshes.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "BRAND" for t in node.targets):
            return [w.decode() for w in ast.literal_eval(node.value)]
    raise SystemExit("check_bike_meshes.py: no BRAND")


def cell_transform(at, cell, mirrored=False):
    """(scale_u, scale_v, offset_u, offset_v) taking plate_rect to the cell's drawn area: uv' = uv * scale + offset."""
    (W, H), (cw, ch), (dw, dh) = at["size"], at["cell"], at["draw"]
    u0, v0, u1, v1 = at["plate_rect"]
    c, r = cell
    su, sv = (dw / W) / (u1 - u0), (dh / H) / (v1 - v0)
    cu0, cv0 = c * cw / W, (r * ch + (ch - dh) / 2) / H
    if mirrored:
        return -su, sv, cu0 + u1 * su, cv0 - v0 * sv
    return su, sv, cu0 - u0 * su, cv0 - v0 * sv


def game_transform(at, flag):
    """A game emblem: a chest decal's whole square centred on the plate at its height; a flag over the whole patch."""
    u0, v0, u1, v1 = at["plate_rect"]
    sv = 1.0 / (v1 - v0)
    ov = -v0 * sv
    if flag:
        su = 1.0 / (u1 - u0)
        return su, sv, -u0 * su, ov
    return sv, sv, 0.5 - 0.5 * sv, ov


def is_flag(b):
    return b["slots"] == ["Fender"]


def material_for(template, b, at, mirrored=False):
    m = bgsm.loads(template)
    m.pop("_raw_tex", None)
    m.pop("_raw_strings", None)
    m["tile_flags"] = 0                                   # clamp both ways
    m["alpha_test"], m["alpha_test_ref"], m["two_sided"] = True, 128, True
    # decal on (the depth bias) for a badge the rear fender's patch can show: the patch sits 0.27-0.37 over the
    # paint and a swap replaces its whole material, whose own decal flag (static_badgeFender.bgsm) would go with it
    m["decal"] = "Fender" in b["slots"]
    if b["art"] == "ours":
        su, sv, ou, ov = cell_transform(at, b["cell"], mirrored)
        m["textures"].update(diffuse=at["diffuse"], normal=at["normal"], smoothspec=at["smoothspec"])
    else:
        su, sv, ou, ov = game_transform(at, is_flag(b))
        if mirrored:
            su, ou = -su, ou + su
        t = b["textures"]
        m["textures"].update(diffuse=t["diffuse"] or "", normal=t["normal"] or "", smoothspec=t["smoothspec"] or "",
                             envmap="")
        m["environment_mapping"] = False                  # a painted decal or a cloth flag, not chrome
        m["specular_mult"], m["smoothness"] = 0.5, 0.5
    m.update(uv_scale_u=su, uv_scale_v=sv, uv_offset_u=ou, uv_offset_v=ov)
    return m


def material_names(opts):
    out = []
    for b in opts["badges"]:
        out.append((b, b["material"], False))
        if opts["right_mirrored"] and "TankR" in b["slots"]:
            out.append((b, b["material"][:-5] + "_r.bgsm", True))
    return out


def write(args, opts):
    import write_dds
    at = opts["atlas"]
    tex = Path(args.out, *TEX)
    mat = Path(args.out, *MAT)
    tex.mkdir(parents=True, exist_ok=True)
    mat.mkdir(parents=True, exist_ok=True)
    jobs = (("badges_d", "bc3", dict(gamma_mips=True)), ("badges_n", "bc5", dict(normal=True)), ("badges_s", "bc5", {}))
    sizes = 0
    for stem, fmt, kw in jobs:
        img = load_png(Path(args.art, stem + ".png"))
        data = write_dds.build([img], fmt, **kw)
        out = Path(args.out, "Textures", *at[{"badges_d": "diffuse", "badges_n": "normal", "badges_s": "smoothspec"}[stem]].split("\\"))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        sizes += len(data)
        print(f"{out}: {fmt} {img.shape[1]}x{img.shape[0]}, {len(data)} bytes")
    template = template_path(args.out).read_bytes()
    for b, name, mirrored in material_names(opts):
        m = material_for(template, b, at, mirrored)
        p = Path(args.out, "Materials", *name.split("\\"))
        bgsm.write(p, m)
        print(f"{p}: uv scale {m['uv_scale_u']:.6f} {m['uv_scale_v']:.6f} offset {m['uv_offset_u']:.6f} "
              f"{m['uv_offset_v']:.6f}, diffuse {m['textures']['diffuse']}")
    print(f"textures {sizes} bytes ({sizes / 1048576:.2f} MB), {len(material_names(opts))} materials")
    return 0


# --- the plates' outlines ----------------------------------------------------------------------------------------

def plate_masks(at, npz):
    """(left, right) plate masks over one cell (ch, cw), True where the plate shows the badge, from the shipped
    static_badge geometry's fixed UVs (bike_pieces.badge_uvs); None without the file."""
    if not npz:
        return None
    import bike_pieces as bp
    z = np.load(npz)
    pos, tri, uv = z["pos"], z["tri"], z["uv_fixed"].astype(np.float64)
    isl = bp.islands(len(pos), tri)
    (cw, ch), (dw, dh) = at["cell"], at["draw"]
    u0, v0, u1, v1 = at["plate_rect"]
    py, px = np.mgrid[0:ch, 0:cw] + 0.5
    out = {}
    for i in range(isl.max() + 1):
        sel = isl == i
        u = uv[sel]
        X = (u[..., 0] - u0) / (u1 - u0) * dw
        Y = (ch - dh) / 2 + (u[..., 1] - v0) / (v1 - v0) * dh
        if X.max() - X.min() < dw * 0.5:
            continue                                     # the roundel: in no slot
        m = np.zeros((ch, cw), bool)
        for (x0, x1, x2), (y0, y1, y2) in zip(X, Y):
            d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
            if abs(d) < 1e-12:
                continue
            l0 = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / d
            l1 = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / d
            m |= (l0 >= -1e-9) & (l1 >= -1e-9) & (1 - l0 - l1 >= -1e-9)
        side = "left" if pos[tri[sel]].reshape(-1, 3)[:, 0].mean() > 0 else "right"   # the stage frame: x > 0 left
        out[side] = m
    return out["left"], out["right"]


def safe_mask(at):
    import bike_art
    from bike_art import Canvas, sd_poly
    cw, ch = at["cell"]
    m = sd_poly(Canvas(cw, ch), bike_art.BADGE_SAFE) <= 0
    return m, m


# --- the check ---------------------------------------------------------------------------------------------------

class Report:
    def __init__(self):
        self.fails = 0

    def check(self, ok, what, detail=""):
        self.fails += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {what}{(': ' + detail) if detail else ''}")


def check(args, opts):
    import write_dds
    rep = Report()
    at = opts["atlas"]
    (W, H), (cw, ch), (dw, dh), margin = at["size"], at["cell"], at["draw"], at["margin"]
    paths = {k: Path(args.out, "Textures", *at[k].split("\\")) for k in ("diffuse", "normal", "smoothspec")}
    dec = {}
    total = 0
    for k, p in paths.items():
        if not p.exists():
            rep.check(False, f"{p.name} there")
            continue
        info, faces = write_dds.read_dds(p)
        want = ("bc3", W) if k == "diffuse" else ("bc5", W // 2)
        full = 1 + int(np.log2(want[1]))
        rep.check((info["format"], info["w"], info["h"], info["mips"]) == (want[0], want[1], want[1], full),
                  f"{p.name}: {want[0]} {want[1]}x{want[1]}, {full} mips", f"{info['format']} {info['w']}x{info['h']} {info['mips']} mips")
        dec[k] = faces[0]
        total += p.stat().st_size
    rep.check(7.5e6 <= total <= 9.5e6, "the atlas' three textures about 8.4 MB", f"{total} bytes")
    meta = json.loads(Path(args.art, "badges.json").read_text()) if args.art else None
    ours = [b for b in opts["badges"] if b["art"] == "ours"]
    masks = plate_masks(at, args.plate_npz)
    both = (masks[0] & masks[1]) if masks else None
    if "diffuse" in dec:
        levels = dec["diffuse"]
        a0 = levels[0][..., 3]
        y0, y1 = int(round((ch - dh) / 2)), int(round((ch + dh) / 2))
        outside, cov_bad, margin_bad, plate_bad = [], [], [], []
        covs, plates = {}, {}
        for b in ours:
            c, r = b["cell"]
            cell = a0[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw]
            ring = np.ones((ch, cw), bool)
            ring[y0:y1, :] = False
            if cell[ring].max(initial=0) > 0:
                outside.append(f"{b['key']} {int((cell[ring] > 0).sum())} texels")
            cov = float((cell[y0:y1] >= 128).mean())
            covs[b["key"]] = cov
            if not 0.25 <= cov <= 0.82:
                cov_bad.append(f"{b['key']} {cov:.2f}")
            for lv, img in enumerate(levels):
                m = margin >> lv
                if m < 1:
                    break
                s = 1 << lv
                cc = img[r * ch // s:(r + 1) * ch // s, c * cw // s:(c + 1) * cw // s, 3]
                band = np.ones(cc.shape, bool)
                band[m:-m, m:-m] = False
                if cc[band].max(initial=0) > 0:
                    margin_bad.append(f"{b['key']} mip {lv}: {int(cc[band].max())}")
            if both is not None:
                on = cell >= 128
                share = float((on & ~both).sum() / max(1, on.sum()))
                plates[b["key"]] = share
                if share > 0.005:
                    plate_bad.append(f"{b['key']} {share:.3%}")
        rep.check(not outside, f"every cell's alpha inside its drawn {dw} x {dh}", "; ".join(outside))
        rep.check(not margin_bad, f"the {margin}-pixel margin's alpha 0 at every mip it is a texel or more wide (mips 0-"
                                  f"{int(np.log2(margin))})", "; ".join(margin_bad))
        rep.check(not cov_bad, "each badge covers 25-82 % of the plate's rectangle",
                  "; ".join(cov_bad) or ", ".join(f"{k} {v:.2f}" for k, v in covs.items()))
        if both is not None:
            rep.check(not plate_bad, "each emblem inside what both tank plates show (0.5 % or less outside)",
                      "; ".join(plate_bad) or "most outside: " + max(plates, key=plates.get) + f" {max(plates.values()):.3%}")
        empty = [(c, r) for c in range(at["cols"]) for r in range(at["rows"])
                 if [c, r] not in [b["cell"] for b in ours]]
        spare = max((int(a0[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw].max()) for c, r in empty), default=0)
        rep.check(spare == 0, f"the {len(empty)} spare cells empty", f"alpha up to {spare}")
    if meta is not None:
        keys = sorted(meta["badges"])
        rep.check(keys == sorted(b["key"] for b in ours) and all(meta["badges"][b["key"]]["cell"] == b["cell"] for b in ours),
                  "badges.json: our 13 in look_options.json's cells", ", ".join(keys))
    # the materials
    template = template_path(args.out)
    tmpl = bgsm.loads(template.read_bytes()) if template.exists() else None
    bad = []
    names = material_names(opts)
    for b, name, mirrored in names:
        p = Path(args.out, "Materials", *name.split("\\"))
        if not p.exists():
            bad.append(f"{name} missing")
            continue
        data = p.read_bytes()
        m = bgsm.loads(data)
        if bgsm.dumps(m) != data:
            bad.append(f"{name}: not byte for byte through bgsm.py")
        want = (cell_transform(at, b["cell"], mirrored) if b["art"] == "ours" else
                (lambda t: (-t[0], t[1], t[2] + t[0], t[3]) if mirrored else t)(game_transform(at, is_flag(b))))
        got = (m["uv_scale_u"], m["uv_scale_v"], m["uv_offset_u"], m["uv_offset_v"])
        if max(abs(x - y) for x, y in zip(want, got)) > 1e-6:
            bad.append(f"{name}: uv {got} not {want}")
        if b["art"] == "ours":
            # the plate's corners land on the drawn cell's
            u0, v0, u1, v1 = at["plate_rect"]
            c, r = b["cell"]
            cu = [u * got[0] + got[2] for u in (u0, u1)]
            cv_ = [v * got[1] + got[3] for v in (v0, v1)]
            wu = [c * cw / W, (c + 1) * cw / W]
            wv = [(r * ch + (ch - dh) / 2) / H, (r * ch + (ch + dh) / 2) / H]
            if mirrored:
                wu = wu[::-1]
            if max(abs(x - y) for x, y in zip(cu + cv_, wu + wv)) > 1e-6:
                bad.append(f"{name}: the plate maps to {cu} {cv_}, not the cell {wu} {wv}")
            tex = (at["diffuse"], at["normal"], at["smoothspec"])
        else:
            t = b["textures"]
            tex = (t["diffuse"] or "", t["normal"] or "", t["smoothspec"] or "")
        if (m["textures"]["diffuse"], m["textures"]["normal"], m["textures"]["smoothspec"]) != tex:
            bad.append(f"{name}: textures {m['textures']}")
        if not (m["tile_flags"] == 0 and m["alpha_test"] and m["alpha_test_ref"] == 128 and m["two_sided"]):
            bad.append(f"{name}: tile {m['tile_flags']} alpha test {m['alpha_test']} {m['alpha_test_ref']} two-sided {m['two_sided']}")
        if m["decal"] != ("Fender" in b["slots"]):
            bad.append(f"{name}: decal {m['decal']} (wanted on exactly for a badge the fender patch shows)")
        if b["art"] == "ours" and tmpl is not None:
            same = [k for k in ("environment_mapping", "env_map_mask_scale", "specular_mult", "smoothness", "cast_shadows",
                                "receive_shadows") if m[k] != tmpl[k]] + (["envmap"] if m["textures"]["envmap"] != tmpl["textures"]["envmap"] else [])
            if same:
                bad.append(f"{name}: differs from {template.name} in {same}")
        if b["art"] == "game" and (m["environment_mapping"] or m["textures"]["envmap"]):
            bad.append(f"{name}: a game emblem with the chrome cube")
    rep.check(not bad, f"the {len(names)} badge materials: read back byte for byte, the transform, the textures, clamp, "
                       f"alpha test 128, two-sided, decal on for the fender's, the stock badge's chrome on ours",
              "; ".join(bad))
    targets = sorted({t for s in opts["slots"] for o in s["options"] if o["kind"] == "badge" for _, t in o["swap"]})
    missing = [t for t in targets if not Path(args.out, "Materials", *t.split("\\")).exists()]
    rep.check(not missing, f"every badge target of look_options.json's swaps there ({len(targets)})", "; ".join(missing))
    words = brand_words()
    text = json.dumps([[b["key"], b["name"], b["motif"]] for b in opts["badges"]]
                      + ([meta] if meta is not None else [])).lower()
    hits = [w for w in words if w in text]
    rep.check(not hits, "no brand word in the badges' keys, names, motifs or badges.json", ", ".join(hits))
    copied = []
    for b in opts["badges"]:
        for t in (b["textures"] or {}).values():
            if t and (Path(args.out, "Textures", *t.split("\\")).exists() or Path(args.out, *t.split("\\")).exists()):
                copied.append(t)
    rep.check(not copied, "the guard: no game texture under --out (game art is by path, nothing copied)", "; ".join(copied))
    print(f"{'all checks passed' if not rep.fails else f'{rep.fails} check(s) failed'}")
    return 1 if rep.fails else 0


# --- the flat sheet ----------------------------------------------------------------------------------------------

def standin(cw, ch, label):
    """A grey stand-in for a game texture (we hold none), its name written on it."""
    sys.path.insert(0, str(HERE))
    from look_render import draw_text
    img = np.full((ch, cw, 3), 118, np.uint8)
    img[::16, :] = 100
    img[:, ::16] = 100
    draw_text(img, 8, ch // 2 - 7, "(GAME ART)", 2, (230, 230, 230))
    draw_text(img, 8, ch // 2 + 9, label[:40], 2, (230, 230, 230))
    return np.dstack([img, np.full((ch, cw), 255, np.uint8)])


def sheet(args, opts):
    import write_dds
    from PIL import Image
    sys.path.insert(0, str(HERE))
    from look_render import draw_text
    at = opts["atlas"]
    (W, H), (cw, ch), (dw, dh) = at["size"], at["cell"], at["draw"]
    _, faces = write_dds.read_dds(Path(args.out, "Textures", *at["diffuse"].split("\\")))
    d = faces[0][0]
    _, faces = write_dds.read_dds(Path(args.out, "Textures", *at["normal"].split("\\")))
    n = np.asarray(Image.fromarray(faces[0][0]).resize((W, H), Image.BILINEAR)).astype(np.float64) / 255 * 2 - 1
    _, faces = write_dds.read_dds(Path(args.out, "Textures", *at["smoothspec"].split("\\")))
    s = np.asarray(Image.fromarray(faces[0][0]).resize((W, H), Image.BILINEAR)).astype(np.float64) / 255
    masks = plate_masks(at, args.plate_npz) or safe_mask(at)
    fender = np.zeros((ch, cw), bool)
    fender[int((ch - dh) / 2):int((ch + dh) / 2), :] = True
    rows = []
    for b in opts["badges"]:
        if b["art"] == "ours":
            c, r = b["cell"]
            sl = (slice(r * ch, (r + 1) * ch), slice(c * cw, (c + 1) * cw))
            rgba, nn, ss = d[sl].astype(np.float64) / 255, n[sl], s[sl]
        else:
            img = standin(cw, int(dh), Path(b["textures"]["diffuse"].replace("\\", "/")).name)
            rgba = np.zeros((ch, cw, 4))
            top = int((ch - dh) / 2)
            if is_flag(b):
                rgba[top:top + img.shape[0]] = img / 255
            else:
                side = int(dh)
                x0 = (cw - side) // 2
                rgba[top:top + side, x0:x0 + side] = np.asarray(Image.fromarray(img).resize((side, side))) / 255
            nn = np.zeros((ch, cw, 3))
            nn[..., 2] = 1
            ss = np.zeros((ch, cw, 3)) + 0.3
        lit = np.clip(-0.35 * nn[..., 0] - 0.5 * nn[..., 1] + 0.8 * nn[..., 2], 0, 1)[..., None]
        env = (0.55 + 0.45 * np.clip(-2 * nn[..., 1] + 0.3, -1, 1))[..., None]
        col = rgba[..., :3] * (0.35 + 0.65 * lit) + rgba[..., :3] * ss[..., :1] * 1.3 * env
        col = col + (ss[..., :1] * ss[..., 1:2]) * 0.25 * lit ** 8
        a = (rgba[..., 3] >= 0.5).astype(np.float64)
        tiles = []
        for m, slot in ((masks[0], "TankL"), (masks[1], "TankR"), (fender, "Fender")):
            bg = np.zeros((ch, cw, 3)) + np.array(PAINT) / 255 * 0.85
            bg[~m] = (0.16, 0.16, 0.18)
            show = a * m * (slot in b["slots"])
            t = bg * (1 - show[..., None]) + col * show[..., None]
            t = (np.clip(t, 0, 1) * 255).astype(np.uint8)
            if slot not in b["slots"]:
                draw_text(t, 12, ch // 2 - 7, "NOT IN THIS SLOT", 2, (150, 150, 150))
            tiles.append(np.pad(t, ((0, 0), (0, 6), (0, 0)), constant_values=24))
        row = np.concatenate(tiles, 1)
        head = np.full((24, row.shape[1], 3), 24, np.uint8)
        draw_text(head, 6, 5, f"{b['key']}: {b['name']}", 2)
        rows.append(np.concatenate([head, row], 0))
    cols = 2
    rh, rw = rows[0].shape[:2]
    nr = (len(rows) + cols - 1) // cols
    canvas = np.full((nr * rh, cols * (rw + 12), 3), 24, np.uint8)
    for i, rimg in enumerate(rows):
        r, c = divmod(i, cols)
        canvas[r * rh:(r + 1) * rh, c * (rw + 12):c * (rw + 12) + rw] = rimg
    hdr = np.full((30, canvas.shape[1], 3), 24, np.uint8)
    draw_text(hdr, 6, 8, "BADGES ON THE LEFT AND RIGHT TANK PLATES (SEEN FROM OUTSIDE) AND THE REAR FENDER PATCH; "
                         "FLAT PREVIEW FROM THE DDS", 2)
    img = np.concatenate([hdr, canvas], 0)
    out = Path(args.sheet)
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(img).save(out)
    print(f"{out}: {img.shape[1]}x{img.shape[0]}, {len(rows)} badges")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--art", type=Path, help="bike_art.py --badges' output (badges_d/_n/_s.png, badges.json)")
    ap.add_argument("--out", type=Path, required=True, help="a Data folder's layout (Textures, Materials)")
    ap.add_argument("--look-options", type=Path, default=HERE.parent / "esp-generator" / "look_options.json")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--plate-npz", type=Path, help="the stage's shapes/static_badge.npz: the tank plates' outlines")
    ap.add_argument("--sheet", type=Path, help="write a flat contact sheet of every badge on every slot here")
    args = ap.parse_args()
    opts = json.loads(args.look_options.read_text())
    if args.check:
        return check(args, opts)
    if args.sheet:
        return sheet(args, opts)
    if not args.art:
        ap.error("--art is needed to write")
    return write(args, opts)


if __name__ == "__main__":
    sys.exit(main())
