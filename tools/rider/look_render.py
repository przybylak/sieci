#!/usr/bin/env python3
"""Fallout 4-like preview renders of the built bike nifs (Blender's Cycles on the CPU, Blender as a Python module).

A look at the bike before it goes in game. It reads what the game reads and shades it the way Fallout 4's
lighting shader does, as far as is cheap:

- the nifs through PyNifly; a shape whose shader name is a material file found under --data takes the material's
  values and textures (the game ignores the nif block then), any other the nif block's (an empty name, or a
  material file that isn't there: the `Materials\\CMB` A/B);
- the DDS decoded here (texture2ddecoder): base colour = `_d` (its alpha for blend/test), the normal = `_n`
  (DirectX green, BC5's blue rebuilt), specular = `_s` R x specular colour x mult, smoothness = `_s` G x the
  material's (clamped to 0..1, as 27c's 90/30/110/30 must be), a GGX highlight from the sun only;
- environment-mapped shapes lit from a cube lookup on the reflection vector, `_s` R x env scale (Fresnel-weighted
  on the dielectric cube): no ray-traced reflection of the scene, as in the game (FO4 cannot show real
  reflections); our own cube (`Textures\\CMB\\Bike\\mirror_cube_e.dds`) decoded from its DDS, the vanilla cubes
  (in the game's archives, not read here) by procedural stand-ins written to --env;
- emissive = `_g` x colour x mult (colour x mult without a glow map), lit whatever the light;
- what the F4SE plugin does on the riding bike: the shapes' roles told by their names (the plugin's table), the
  needle turned about NeedleAxis through NeedlePoint (CMB_BikeParts.ini) clockwise as the rider sees it, the bars
  turned about SteerAxis, and the shapes the plugin shrinks to a speck (the lamp's lit parts and the dial's
  backlight with the lamp off, the brake shell unless braking, the tail shell with [Tail] Glow=0, the mirror
  variants but the [Look] Mirrors one) left out;
- shapes without Cast_Shadows cast none, single-sided ones are culled from behind;
- day and night presets (night: the lamp on, its beam a spot light where the plugin puts the game's light).

    <bpy python> -I tools/rider/look_render.py --pynifly <io_scene_nifly> --data <Data> --out <dir> \\
        --prefix before_ [--views all|<set>|v1,v2] [--size 1280x800] [--samples 20] [--env <dir>]
    <bpy python> -I tools/rider/look_render.py --sheet <out.png> <png>...           (contact sheet)
    <bpy python> -I tools/rider/look_render.py --compare <dir> <prefixA> <prefixB> <out.png>
    <bpy python> -I tools/rider/look_render.py --list-views

--data is a Data folder: Meshes\\CMB (the nifs, CMB_BikeParts.ini, CMB_BikeFit.json), Textures, Materials.
Paths are matched without regard to case, as the game does. Nothing from the files read is ever executed.
"""

import argparse
import json
import math
import os
import shutil
import struct
import sys
import time
import zlib
from pathlib import Path

import numpy as np

# ----------------------------------------------------------------------------------------------------------------
# views: cameras in the worn bike's space (+Y forward, +X the bike's right, z up, the ground at 0)

DAY, NIGHT = "day", "night"
EYE = (0.0, 3.0, 121.0)          # the rider's eye, first person: the one bike_pieces.py aims the mirrors at
VIEWS = {
    "front34": dict(cam=(195, 280, 122), at=(0, 30, 50), lens=50),
    "rear34": dict(cam=(-170, -240, 122), at=(0, 22, 50), lens=50),
    "side_r": dict(cam=(370, 28, 62), at=(0, 28, 52), lens=55),
    "side_l": dict(cam=(-370, 28, 62), at=(0, 28, 52), lens=55),
    "cockpit_0": dict(cam=EYE, at=(0, 60, 94), lens=32, mph=0),
    "cockpit_50": dict(cam=EYE, at=(0, 60, 94), lens=32, mph=50),
    "dial_50": dict(cam=EYE, at=(0.38, 65.35, 98.84), lens=150, mph=50),
    "tail_off": dict(cam=(-32, -150, 74), at=(0, -58, 55), lens=60, brake=False),
    "tail_on": dict(cam=(-32, -150, 74), at=(0, -58, 55), lens=60, brake=True),
    "night_front34": dict(cam=(195, 280, 122), at=(0, 30, 50), lens=50, preset=NIGHT),
    "night_rear34": dict(cam=(-170, -240, 122), at=(0, 22, 50), lens=50, preset=NIGHT),
    "night_cockpit": dict(cam=EYE, at=(0, 60, 94), lens=32, mph=30, preset=NIGHT),
    "mirror_stock": dict(cam=EYE, at=(30, 40, 94), lens=32, mirrors=1),
    "mirror_egg": dict(cam=EYE, at=(30, 40, 94), lens=32, mirrors=2),
    "mirror_d": dict(cam=EYE, at=(30, 40, 94), lens=32, mirrors=3),
    "mirror_none": dict(cam=EYE, at=(30, 40, 94), lens=32, mirrors=0),
    "bars_stock": dict(cam=(105, 118, 122), at=(22, 42, 93), lens=45, mirrors=1),
    "bars_egg": dict(cam=(105, 118, 122), at=(22, 42, 93), lens=45, mirrors=2),
    "bars_d": dict(cam=(105, 118, 122), at=(22, 42, 93), lens=45, mirrors=3),
    "bars_none": dict(cam=(105, 118, 122), at=(22, 42, 93), lens=45, mirrors=0),
    "close_tank": dict(cam=(82, 36, 100), at=(9, 31, 76), lens=50),
    "close_engine": dict(cam=(92, 20, 50), at=(6, 30, 44), lens=45),
    "close_wheel": dict(cam=(96, 104, 36), at=(0, 96, 30), lens=45),
    "close_seat": dict(cam=(40, -42, 112), at=(0, -14, 64), lens=45),
    "fulllock_pos": dict(cam=(0, 12, 265), at=(0, 40, 92), lens=42, bar=+1),
    "fulllock_neg": dict(cam=(0, 12, 265), at=(0, 40, 92), lens=42, bar=-1),
    "parked34": dict(cam=(195, 280, 122), at=(0, 30, 50), lens=50, parked=True),
}
SETS = {
    "day": ["front34", "rear34", "side_r", "side_l", "cockpit_0", "cockpit_50", "tail_off", "tail_on"],
    "night": ["night_front34", "night_rear34", "night_cockpit"],
    "mirrors": ["mirror_stock", "mirror_egg", "mirror_d", "mirror_none", "bars_stock", "bars_egg", "bars_d", "bars_none"],
    "close": ["close_tank", "close_engine", "close_wheel", "close_seat"],
    "lock": ["fulllock_pos", "fulllock_neg", "parked34", "dial_50"],
}
SETS["all"] = [v for k in ("day", "night", "mirrors", "close", "lock") for v in SETS[k]]
SHEETS = {"closeups": SETS["close"]}

# the plugin's roles by name (CMB_Slope.c g_roleTags, first fit wins); 27c's names give 27c's roles with it
TURNING = {"front", "glow", "backlight", "needle", "fork", "wheelF"}
MIRROR_TAGS = (("_front_mirrorstock", 1), ("_front_mirrorunderegg", 2), ("_front_mirrorunderd", 3))


def role_of(name):
    n = name.lower()
    if ":" in n and n.rsplit(":", 1)[1].isdigit():
        n = n.rsplit(":", 1)[0]
    for end, role in (("_front_needle", "needle"), ("_front_glow", "glow"), ("_front_dialglow", "backlight"),
                      ("_rear_tail", "tail"), ("_rear_brake", "brake")):
        if n.endswith(end):
            return role, 0
    if "_fork" in n:
        return "fork", 0
    if "_wheelf" in n:
        return "wheelF", 0
    if "_wheelr" in n:
        return "wheelR", 0
    for end, v in MIRROR_TAGS:
        if n.endswith(end):
            return "front", v
    if "_front_" in n:
        return "front", 0
    return "none", 0


# ----------------------------------------------------------------------------------------------------------------
# files

class DataIndex:
    """Case-insensitive lookup of game paths (backslashes, any case) under a Data folder."""

    def __init__(self, root):
        self.root = Path(root)
        self.files = {}
        for d, _, fs in os.walk(self.root):
            for f in fs:
                p = Path(d) / f
                self.files[str(p.relative_to(self.root)).replace("\\", "/").lower()] = p

    def find(self, game_path, under=""):
        if not game_path:
            return None
        g = game_path.replace("\\", "/").strip("/").lower()
        for cand in (g, f"{under}/{g}" if under else None):
            if cand and cand in self.files:
                return self.files[cand]
        return None


def srgb_to_linear(c):
    c = np.asarray(c, dtype=np.float32)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4).astype(np.float32)


DXGI = {71: "bc1", 72: "bc1", 77: "bc3", 78: "bc3", 80: "bc4", 83: "bc5", 98: "bc7", 99: "bc7",
        28: "rgba8", 29: "rgba8", 87: "bgra8", 91: "bgra8"}
FOURCC = {b"DXT1": "bc1", b"DXT5": "bc3", b"DXT4": "bc3", b"ATI1": "bc4", b"BC4U": "bc4", b"ATI2": "bc5",
          b"BC5U": "bc5"}
BLOCK = {"bc1": 8, "bc4": 8, "bc3": 16, "bc5": 16, "bc7": 16}


def read_dds(path):
    """Level 0 of every face of a DDS: list of (h, w, 4) uint8 RGBA arrays, first row the top; and its format."""
    import texture2ddecoder as t2d
    b = Path(path).read_bytes()
    if b[:4] != b"DDS ":
        raise ValueError(f"{path}: not a DDS file")
    h, w, mips = struct.unpack_from("<III", b, 12)[0], struct.unpack_from("<I", b, 16)[0], struct.unpack_from("<I", b, 28)[0]
    pf_flags, fourcc = struct.unpack_from("<I", b, 80)[0], b[84:88]
    bits, rm, gm, bm, am = struct.unpack_from("<5I", b, 88)
    caps2 = struct.unpack_from("<I", b, 112)[0]
    off, fmt, cube = 128, None, bool(caps2 & 0x200)
    if pf_flags & 4 and fourcc == b"DX10":
        dxgi, _, misc = struct.unpack_from("<III", b, 128)
        off, fmt, cube = 148, DXGI.get(dxgi), cube or bool(misc & 4)
        if fmt is None:
            raise ValueError(f"{path}: DXGI format {dxgi} not handled")
    elif pf_flags & 4:
        fmt = FOURCC.get(fourcc)
        if fmt is None:
            raise ValueError(f"{path}: FourCC {fourcc!r} not handled")
    elif bits == 32:
        fmt = "masked32"
    else:
        raise ValueError(f"{path}: {bits}-bit uncompressed DDS not handled")
    mips = max(1, mips)

    def level_size(lw, lh):
        if fmt in BLOCK:
            return max(1, (lw + 3) // 4) * max(1, (lh + 3) // 4) * BLOCK[fmt]
        return lw * lh * 4

    chain = sum(level_size(max(1, w >> i), max(1, h >> i)) for i in range(mips))
    faces = []
    for f in range(6 if cube else 1):
        data = b[off + f * chain: off + f * chain + level_size(w, h)]
        if fmt in BLOCK:
            raw = getattr(t2d, "decode_" + fmt)(data, w, h)
            a = np.frombuffer(raw, np.uint8).reshape(h, w, 4)[:, :, [2, 1, 0, 3]].copy()  # BGRA -> RGBA
        elif fmt == "masked32":
            px = np.frombuffer(data, "<u4").reshape(h, w)
            a = np.zeros((h, w, 4), np.uint8)
            for i, m in enumerate((rm, gm, bm, am)):
                if m:
                    shift = (m & -m).bit_length() - 1
                    a[:, :, i] = ((px & m) >> shift) * 255 // (m >> shift)
                else:
                    a[:, :, i] = 255
        else:
            px = np.frombuffer(data, np.uint8).reshape(h, w, 4)
            a = px[:, :, [2, 1, 0, 3]].copy() if fmt == "bgra8" else px.copy()
        faces.append(a)
    return faces, fmt, cube


def write_png(path, rgb):
    rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
    h, w, c = rgb.shape
    raw = b"".join(b"\x00" + rgb[y].tobytes() for y in range(h))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2 if c == 3 else 6, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def load_png(path):
    """(h, w, 3) uint8, first row the top, through bpy's image loader."""
    import bpy
    im = bpy.data.images.load(str(path))
    w, h = im.size
    a = np.empty(w * h * 4, np.float32)
    im.pixels.foreach_get(a)
    bpy.data.images.remove(im)
    return (np.clip(a.reshape(h, w, 4)[::-1, :, :3], 0, 1) * 255 + 0.5).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------
# a 5x7 font for the sheets' labels

_GLYPHS = """
A 01110 10001 10001 11111 10001 10001 10001|B 11110 10001 10001 11110 10001 10001 11110
C 01110 10001 10000 10000 10000 10001 01110|D 11110 10001 10001 10001 10001 10001 11110
E 11111 10000 10000 11110 10000 10000 11111|F 11111 10000 10000 11110 10000 10000 10000
G 01110 10001 10000 10111 10001 10001 01111|H 10001 10001 10001 11111 10001 10001 10001
I 01110 00100 00100 00100 00100 00100 01110|J 00111 00010 00010 00010 00010 10010 01100
K 10001 10010 10100 11000 10100 10010 10001|L 10000 10000 10000 10000 10000 10000 11111
M 10001 11011 10101 10101 10001 10001 10001|N 10001 10001 11001 10101 10011 10001 10001
O 01110 10001 10001 10001 10001 10001 01110|P 11110 10001 10001 11110 10000 10000 10000
Q 01110 10001 10001 10001 10101 10010 01101|R 11110 10001 10001 11110 10100 10010 10001
S 01111 10000 10000 01110 00001 00001 11110|T 11111 00100 00100 00100 00100 00100 00100
U 10001 10001 10001 10001 10001 10001 01110|V 10001 10001 10001 10001 10001 01010 00100
W 10001 10001 10001 10101 10101 10101 01010|X 10001 10001 01010 00100 01010 10001 10001
Y 10001 10001 01010 00100 00100 00100 00100|Z 11111 00001 00010 00100 01000 10000 11111
0 01110 10001 10011 10101 11001 10001 01110|1 00100 01100 00100 00100 00100 00100 01110
2 01110 10001 00001 00010 00100 01000 11111|3 11111 00010 00100 00010 00001 10001 01110
4 00010 00110 01010 10010 11111 00010 00010|5 11111 10000 11110 00001 00001 10001 01110
6 00110 01000 10000 11110 10001 10001 01110|7 11111 00001 00010 00100 01000 01000 01000
8 01110 10001 10001 01110 10001 10001 01110|9 01110 10001 10001 01111 00001 00010 01100
_ 00000 00000 00000 00000 00000 00000 11111|- 00000 00000 00000 11111 00000 00000 00000
. 00000 00000 00000 00000 00000 01100 01100|: 00000 01100 01100 00000 01100 01100 00000
+ 00000 00100 00100 11111 00100 00100 00000|/ 00001 00010 00010 00100 01000 01000 10000
( 00010 00100 01000 01000 01000 00100 00010|) 01000 00100 00010 00010 00010 00100 01000
= 00000 00000 11111 00000 11111 00000 00000|, 00000 00000 00000 00000 01100 00100 01000
"""
FONT = {}
for _g in _GLYPHS.replace("\n", "|").split("|"):
    if _g.strip():
        _c, *_rows = _g.split()
        FONT[_c] = np.array([[ch == "1" for ch in r] for r in _rows], bool)


def draw_text(img, x, y, text, scale=2, colour=(255, 255, 255)):
    for ch in text.upper():
        g = FONT.get(ch)
        if g is not None:
            m = np.kron(g, np.ones((scale, scale), bool))
            h, w = m.shape
            sub = img[y:y + h, x:x + w]
            sub[m[:sub.shape[0], :sub.shape[1]]] = colour
        x += 6 * scale


def shrink(img, f):
    h, w = (img.shape[0] // f) * f, (img.shape[1] // f) * f
    return img[:h, :w].reshape(h // f, f, w // f, f, 3).mean(axis=(1, 3)).astype(np.uint8)


def sheet(out, paths, cols=4, tile_w=640, labels=None):
    imgs = [load_png(p) for p in paths]
    tiles = []
    for im in imgs:
        f = max(1, im.shape[1] // tile_w)
        tiles.append(shrink(im, f))
    th, tw = max(t.shape[0] for t in tiles), max(t.shape[1] for t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    canvas = np.full((rows * (th + 22), cols * tw, 3), 24, np.uint8)
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        canvas[r * (th + 22) + 22: r * (th + 22) + 22 + t.shape[0], c * tw: c * tw + t.shape[1]] = t
        draw_text(canvas, c * tw + 6, r * (th + 22) + 4, (labels or [Path(p).stem for p in paths])[i])
    write_png(out, canvas)
    return out


def compare(out_dir, pa, pb, out):
    out_dir = Path(out_dir)
    names = sorted(p.name[len(pa):] for p in out_dir.glob(f"{pa}*.png") if (out_dir / (pb + p.name[len(pa):])).exists())
    names = [n for n in names if not n.startswith(("sheet", "compare"))]
    paths, labels = [], []
    for n in names:
        paths += [out_dir / (pa + n), out_dir / (pb + n)]
        labels += [pa + n[:-4], pb + n[:-4]]
    return sheet(out, paths, cols=2, tile_w=640, labels=labels) if paths else None


# ----------------------------------------------------------------------------------------------------------------
# environment: equirect images in the worn space (Blender's equirect: u = -atan2(y, x) / 2pi + 0.5,
# v = atan2(z, hypot(x, y)) / pi + 0.5, the first row at the bottom)

def equirect_dirs(w, h):
    u = (np.arange(w) + 0.5) / w
    v = (np.arange(h) + 0.5) / h
    phi = (0.5 - u) * 2 * np.pi
    el = (v - 0.5) * np.pi
    P, E = np.meshgrid(phi, el)
    return np.stack([np.cos(E) * np.cos(P), np.cos(E) * np.sin(P), np.sin(E)], -1).astype(np.float32), E


def _blur_rows(a, r):
    if r < 1:
        return a
    k = 2 * r + 1
    c = np.cumsum(np.concatenate([a[:, -r:], a, a[:, :r + 1]], axis=1), axis=1)
    return (c[:, k:] - c[:, :-k]) / k


def _blur(a, r, n=3):
    for _ in range(n):
        a = _blur_rows(a, r)
        a = np.swapaxes(_blur_rows(np.swapaxes(np.pad(a, ((r + 1, r + 1), (0, 0), (0, 0)), mode="edge"), 0, 1), r), 0, 1)[r + 1:-r - 1]
    return a


def _smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


SUN_DIR = np.array([0.55, 0.45, 0.70])         # toward the sun (day preset), the bike's front right, high
SUN_DIR = SUN_DIR / np.linalg.norm(SUN_DIR)


def standin(kind, w=1024, h=512):
    """Procedural stand-ins for the vanilla cubes (in the game's archives, not read here). Linear values <= 1, as an
    8-bit cube."""
    d, el = equirect_dirs(w, h)
    rng = np.random.default_rng({"outside": 1, "dielectric": 2, "chrome": 3, "glass": 4}[kind])
    sun = np.clip(d @ SUN_DIR, -1, 1)
    zen, hor = np.array([0.20, 0.33, 0.62]), np.array([0.78, 0.82, 0.86])
    g_far, g_near = np.array([0.10, 0.09, 0.075]), np.array([0.24, 0.22, 0.19])
    sky = hor + (zen - hor) * _smooth(0.0, 0.9, el)[..., None]
    ground = g_near + (g_far - g_near) * _smooth(0.0, -0.6, el)[..., None]
    # low clouds and a few dark masses on the horizon (buildings, trees), so a curve shows a gradient
    noise = _blur(rng.random((h // 8, w // 8, 1)).repeat(8, 0).repeat(8, 1), 6, 2)[..., 0]
    clouds = _smooth(0.52, 0.62, noise) * _smooth(0.02, 0.25, el) * (1 - _smooth(0.5, 1.2, el))
    sky = sky * (1 - 0.25 * clouds[..., None]) + 0.25 * clouds[..., None]
    skyline = _smooth(0.5, 0.56, _blur(rng.random((1, w // 16, 1)).repeat(16, 1), 2, 2)[0, :, 0])[None, :] * 0.06
    mass = (el > 0) & (el < skyline)
    col = np.where((el > 0)[..., None], sky, ground)
    col[mass] = np.array([0.07, 0.075, 0.07])
    if kind == "chrome":
        band = (el < 0) & (el > -0.10)                  # the dark band under a sharp horizon: chrome's look
        col[band] = np.array([0.03, 0.03, 0.035])
        col += (0.9 * np.clip(sun - 0.995, 0, None) / 0.005)[..., None]
        col = np.clip(col * 1.15, 0, 1)
    elif kind in ("outside", "dielectric"):
        col += (0.35 * np.exp(-(1 - sun) / 0.03))[..., None]
        col = _blur(col, 10, 3)                         # "mipblur"
        if kind == "dielectric":
            col = col * 0.8
    elif kind == "glass":
        col = col * 0.35
        for az, e, sw, sh in ((0.6, 0.35, 0.25, 0.18), (2.4, 0.25, 0.35, 0.12), (-1.8, 0.5, 0.15, 0.25)):
            phi = np.arctan2(d[..., 1], d[..., 0])
            m = (np.abs(np.angle(np.exp(1j * (phi - az)))) < sw) & (np.abs(el - e) < sh)
            col[m] = np.array([0.95, 0.95, 0.92])
        col = _blur(col, 3, 2)
    return np.clip(col, 0, 1).astype(np.float32)


STANDIN_FOR = {"metalchrome01cube_e": "chrome", "metalchrome02cube_e": "chrome", "metalshinetopcube01_e": "chrome",
               "mipblur_defaultoutside1": "outside", "mipblur_defaultoutside1_dielectric": "dielectric",
               "shinyglass_e": "glass", "shinybright_e": "glass"}


def cube_to_equirect(faces, w=1024, h=512, up="y"):
    """Six D3D faces (+X -X +Y -Y +Z -Z, a face's first row its top) -> a linear equirect in the worn space."""
    d, _ = equirect_dirs(w, h)
    x, y, z = d[..., 0], d[..., 1], d[..., 2]
    c = np.stack([x, z, y], -1) if up == "y" else np.stack([x, y, z], -1)
    ax = np.abs(c)
    major = np.argmax(ax, -1)
    cx, cy, cz = c[..., 0], c[..., 1], c[..., 2]
    face = np.where(major == 0, np.where(cx > 0, 0, 1), np.where(major == 1, np.where(cy > 0, 2, 3), np.where(cz > 0, 4, 5)))
    sc = np.select([face == 0, face == 1, face == 2, face == 3, face == 4], [-cz, cz, cx, cx, cx], -cx)
    tc = np.select([face == 2, face == 3], [cz, -cz], -cy)
    ma = np.maximum(np.take_along_axis(ax, major[..., None], -1)[..., 0], 1e-9)
    fh, fw = faces[0].shape[:2]
    fu = np.clip(((sc / ma + 1) / 2) * fw - 0.5, 0, fw - 1)
    fv = np.clip(((tc / ma + 1) / 2) * fh - 0.5, 0, fh - 1)
    lin = np.stack([srgb_to_linear(f[:, :, :3] / 255.0) for f in faces])
    u0, v0 = np.floor(fu).astype(int), np.floor(fv).astype(int)
    u1, v1 = np.minimum(u0 + 1, fw - 1), np.minimum(v0 + 1, fh - 1)
    du, dv = (fu - u0)[..., None], (fv - v0)[..., None]
    out = (lin[face, v0, u0] * (1 - du) * (1 - dv) + lin[face, v0, u1] * du * (1 - dv)
           + lin[face, v1, u0] * (1 - du) * dv + lin[face, v1, u1] * du * dv)
    return out.astype(np.float32)


# ----------------------------------------------------------------------------------------------------------------
# reading the nif

def read_parts(path):
    keys = {}
    if path and Path(path).exists():
        for line in Path(path).read_text(errors="replace").splitlines():
            line = line.split(";", 1)[0].strip()
            if "=" in line:
                k, v = line.split("=", 1)
                try:
                    vals = [float(x) for x in v.split(",")]
                except ValueError:
                    continue
                keys[k.strip()] = vals if len(vals) > 1 else vals[0]
    return keys


def shape_shader(P, nifly, f, s, data, use_bgsm):
    """The shader as the game reads it: the material file when the name is one found under data, else the block."""
    from ctypes import create_string_buffer
    from pyn.bgsmaterial import BGSMaterial
    sp = s.properties
    block = P.NiShader(file=f, id=sp.shaderPropertyID, parent=s)
    p = block.properties
    name = block.name or ""

    def slot(i):
        buf = create_string_buffer(512)
        nifly.getShaderTextureSlot(f._handle, s._handle, i, buf, 512)
        return buf.value.decode("utf-8", "replace")

    alpha = None
    if sp.alphaPropertyID != P.NODEID_NONE:
        a = s.alpha_property.properties
        alpha = dict(blend=bool(a.flags & 1), test=bool(a.flags & 0x200), ref=int(a.threshold))
    sf1, sf2 = p.Shader_Flags_1, p.Shader_Flags_2
    sh = dict(name=name, source="nif", type=p.Shader_Type, spec_on=bool(sf1 & 1),
              smooth=float(np.clip(p.Glossiness, 0, 1)), spec_col=tuple(p.Spec_Color[:3]), spec_mult=p.Spec_Str,
              env_on=p.Shader_Type == 1 and bool(sf1 & 0x80) and bool(slot(4)), env_scale=p.Env_Map_Scale,
              emit_on=bool(sf1 & 0x400000), emit_col=tuple(p.Emissive_Color[:3]), emit_mult=p.Emissive_Mult,
              glow_on=bool(sf2 & 0x40) and bool(slot(2)), two_sided=bool(sf2 & 0x10), cast=bool(sf1 & 0x200),
              alpha=alpha, mat_alpha=p.Alpha,
              tex=dict(d=slot(0), n=slot(1), g=slot(2), cube=slot(4), s=slot(7)), under="")
    mat = data.find(name) if (use_bgsm and name.lower().endswith(".bgsm")) else None
    if mat is not None:
        m = BGSMaterial(str(mat))
        t = m.textures
        sh.update(source="bgsm", path=str(mat), spec_on=bool(m.specularEnabled), smooth=float(np.clip(m.smoothness, 0, 1)),
                  spec_col=tuple(m.specularColor), spec_mult=m.specularMult,
                  env_on=bool(m.environmentMapping) and bool(t.get("EnvMap")), env_scale=m.environmentMappingMaskScale,
                  emit_on=bool(m.emitEnabled), emit_col=tuple(m.emittanceColor), emit_mult=m.emittanceMult,
                  glow_on=bool(m.glowmap) and bool(t.get("Glow")), two_sided=bool(m.twoSided), cast=bool(m.castShadows),
                  alpha=(dict(blend=bool(m.alphblend0), test=bool(m.alphatest), ref=int(m.alphatestref))
                         if (m.alphblend0 or m.alphatest) else None), mat_alpha=m.Alpha,
                  tex=dict(d=t.get("Diffuse", ""), n=t.get("Normal", ""), g=t.get("Glow", ""),
                           cube=t.get("EnvMap", ""), s=t.get("Specular", "")), under="textures")
    elif name.lower().endswith(".bgsm"):
        sh["source"] = "nif (no " + name + ")" if use_bgsm else "nif (--bgsm 0)"
    if not sh["emit_on"] or (max(sh["emit_col"]) * sh["emit_mult"] <= 0 and not sh["glow_on"]):
        sh["emit_on"] = False
    return sh


def read_nif(pyn_dir, path, data, use_bgsm, to_worn=None):
    sys.path.insert(0, str(pyn_dir))
    from pyn import pynifly as P
    from pyn.niflydll import nifly
    f = P.NifFile(str(path))
    shapes = []
    for s in f.shapes:
        if s.properties.flags & 1:      # hidden in the nif (the vanilla shape, the parked bike's variants)
            continue
        v = np.asarray(s.verts, np.float64)
        xf = s.transform                                 # the shape's own (identity in our builds)
        R = np.array([list(r) for r in xf.rotation], np.float64)
        v = v @ (R * xf.scale).T + np.array(list(xf.translation), np.float64)
        nrm = np.asarray(s.normals, np.float64) @ R.T if s.normals is not None else None
        if to_worn is not None:
            v = v * to_worn[0] + to_worn[1]
            nrm = nrm * to_worn[0] if nrm is not None else None
        uv = np.asarray(s.uvs, np.float64) if s.uvs else np.zeros((len(v), 2))
        tri = np.asarray(s.tris, np.int64)
        if to_worn is not None and np.prod(to_worn[0]) < 0:
            tri = tri[:, [0, 2, 1]]                      # a mirroring keeps the faces outward
        role, variant = role_of(s.name)
        shapes.append(dict(name=s.name, v=v, n=nrm, uv=uv, tri=tri, role=role, variant=variant,
                           shader=shape_shader(P, nifly, f, s, data, use_bgsm)))
    return shapes


# ----------------------------------------------------------------------------------------------------------------
# Blender

class Scene:
    def __init__(self, args, data):
        import bpy
        self.bpy, self.args, self.data = bpy, args, data
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.sc = bpy.context.scene
        self.images, self.envs, self.log, self.env_values = {}, {}, [], []
        self.env_dir = Path(args.env)
        self.env_dir.mkdir(parents=True, exist_ok=True)
        self.objects = {"worn": [], "parked": []}

    # --- images
    def image(self, key, rgba, colour):
        """rgba: (h, w, 4) float 0..1 or uint8, first row the top."""
        bpy = self.bpy
        if key in self.images:
            return self.images[key]
        h, w = rgba.shape[:2]
        flt = rgba.dtype != np.uint8
        im = bpy.data.images.new(key[-60:], w, h, alpha=True, float_buffer=flt)
        im.colorspace_settings.name = colour
        a = (rgba.astype(np.float32) / (1.0 if flt else 255.0))[::-1]
        im.pixels.foreach_set(np.ascontiguousarray(a, np.float32).ravel())
        im.update()
        self.images[key] = im
        return im

    def texture(self, game_path, under, kind):
        if not game_path:
            return None
        p = self.data.find(game_path, under) or self.data.find(game_path, "textures")
        if p is None:
            self.log.append(f"missing texture {game_path}")
            return None
        key = f"{kind}:{p}"
        if key in self.images:
            return self.images[key]
        faces, fmt, _ = read_dds(p)
        a = faces[0]
        if kind == "n":                       # x, y from R, G (DirectX green), z rebuilt; out in OpenGL green
            x = a[:, :, 0] / 255.0 * 2 - 1
            y = a[:, :, 1] / 255.0 * 2 - 1
            z = np.sqrt(np.clip(1 - x * x - y * y, 0, 1))
            g = (y + 1) / 2 if self.args.normal_green == "gl" else 1 - (y + 1) / 2
            a = np.stack([(x + 1) / 2, g, (z + 1) / 2, np.ones_like(x)], -1).astype(np.float32)
            a = (a * 255 + 0.5).astype(np.uint8)
        return self.image(key, a, "Non-Color" if kind in ("n", "s") else "sRGB")

    def env(self, game_path, under):
        """An equirect for a cube path: ours decoded, a vanilla one's stand-in."""
        stem = Path(game_path.replace("\\", "/")).stem.lower() if game_path else "mipblur_defaultoutside1"
        p = self.data.find(game_path, under) or self.data.find(game_path, "textures") if game_path else None
        key = f"env:{p or stem}"
        if key in self.envs:
            return self.envs[key]
        if p is not None:
            faces, fmt, cube = read_dds(p)
            eq = cube_to_equirect(faces, up=self.args.cube_up) if cube else srgb_to_linear(faces[0][:, :, :3] / 255.0)
            what = f"decoded {p.name} ({fmt}, cube up {self.args.cube_up})"
        else:
            kind = STANDIN_FOR.get(stem, "outside")
            cache = self.env_dir / f"standin_{kind}.npy"
            if cache.exists():
                eq = np.load(cache)
            else:
                eq = standin(kind)
                np.save(cache, eq)
                write_png(self.env_dir / f"standin_{kind}.png",
                          (np.clip(eq[::-1], 0, 1) ** (1 / 2.2) * 255 + 0.5).astype(np.uint8))
            what = f"stand-in '{kind}' for {stem}"
        self.log.append(f"cube {game_path or '(none)'}: {what}")
        # eq's first row is the bottom (Blender's v); image() takes first-row-top arrays
        rgba = np.concatenate([eq[::-1], np.ones(eq.shape[:2] + (1,), np.float32)], -1)
        im = self.image(key, rgba, "Linear Rec.709")
        self.envs[key] = im
        return im

    # --- materials
    def material(self, sh, label):
        bpy = self.bpy
        m = bpy.data.materials.new(label)
        if m.node_tree is None:          # Blender before 5 makes the tree only on request
            m.use_nodes = True
        nt = m.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        N_, L_ = nt.nodes.new, nt.links.new
        out = N_("ShaderNodeOutputMaterial")
        uv = N_("ShaderNodeUVMap")
        uv.uv_map = "UVMap"
        geo = N_("ShaderNodeNewGeometry")

        def tex(img):
            t = N_("ShaderNodeTexImage")
            t.image = img
            t.interpolation = "Linear"
            L_(uv.outputs["UV"], t.inputs["Vector"])
            return t

        def math(op, a, b=None, c=None):
            n = N_("ShaderNodeMath")
            n.operation = op
            for i, x in enumerate((a, b, c)):
                if x is None:
                    continue
                if isinstance(x, (int, float)):
                    n.inputs[i].default_value = float(x)
                else:
                    L_(x, n.inputs[i])
            return n.outputs[0]

        td = self.texture(sh["tex"]["d"], sh["under"], "d")
        ts = self.texture(sh["tex"]["s"], sh["under"], "s")
        tn = self.texture(sh["tex"]["n"], sh["under"], "n")
        tg = self.texture(sh["tex"]["g"], sh["under"], "g") if sh["glow_on"] else None
        dnode = tex(td) if td else None
        base = dnode.outputs["Color"] if dnode else None
        if tn:
            nm = N_("ShaderNodeNormalMap")
            nm.space = "TANGENT"
            nm.uv_map = "UVMap"
            L_(tex(tn).outputs["Color"], nm.inputs["Color"])
            normal = nm.outputs["Normal"]
        else:
            normal = geo.outputs["Normal"]
        if ts:
            sep = N_("ShaderNodeSeparateColor")
            L_(tex(ts).outputs["Color"], sep.inputs["Color"])
            spec_r, smooth_g = sep.outputs["Red"], sep.outputs["Green"]
        else:
            spec_r = smooth_g = None
        diff = N_("ShaderNodeBsdfDiffuse")
        if base is not None:
            L_(base, diff.inputs["Color"])
        else:
            diff.inputs["Color"].default_value = (0.5, 0.5, 0.5, 1)
        L_(normal, diff.inputs["Normal"])
        shader = diff.outputs["BSDF"]

        def add(a, b):
            n = N_("ShaderNodeAddShader")
            L_(a, n.inputs[0])
            L_(b, n.inputs[1])
            return n.outputs[0]

        if sh["spec_on"]:
            gl = N_("ShaderNodeBsdfGlossy")
            try:
                gl.distribution = "GGX"
            except Exception:  # noqa: BLE001
                pass
            sm = math("MULTIPLY", smooth_g, sh["smooth"]) if smooth_g is not None else None
            rough = math("MAXIMUM", math("SUBTRACT", 1.0, sm) if sm is not None else 1.0 - sh["smooth"], 0.04)
            L_(rough, gl.inputs["Roughness"])
            sc = N_("ShaderNodeVectorMath")
            sc.operation = "SCALE"
            sc.inputs[0].default_value = sh["spec_col"]
            if spec_r is not None:
                L_(math("MULTIPLY", spec_r, sh["spec_mult"]), sc.inputs["Scale"])
            else:
                sc.inputs["Scale"].default_value = sh["spec_mult"]
            L_(sc.outputs["Vector"], gl.inputs["Color"])
            L_(normal, gl.inputs["Normal"])
            shader = add(shader, gl.outputs["BSDF"])
        if sh["env_on"]:
            neg = N_("ShaderNodeVectorMath")
            neg.operation = "SCALE"
            L_(geo.outputs["Incoming"], neg.inputs[0])
            neg.inputs["Scale"].default_value = -1.0
            ref = N_("ShaderNodeVectorMath")
            ref.operation = "REFLECT"
            L_(neg.outputs["Vector"], ref.inputs[0])
            L_(normal, ref.inputs[1])
            et = N_("ShaderNodeTexEnvironment")
            et.image = self.env(sh["tex"]["cube"], sh["under"])
            L_(ref.outputs["Vector"], et.inputs["Vector"])
            kv = N_("ShaderNodeValue")                 # env scale x the preset's share (set_preset)
            kv.outputs[0].default_value = sh["env_scale"]
            self.env_values.append((kv, sh["env_scale"]))
            strength = math("MULTIPLY", spec_r, kv.outputs[0]) if spec_r is not None else kv.outputs[0]
            if "dielectric" in sh["tex"]["cube"].lower():
                fr = N_("ShaderNodeFresnel")
                fr.inputs["IOR"].default_value = 1.5
                L_(normal, fr.inputs["Normal"])
                strength = math("MULTIPLY", strength, math("MULTIPLY_ADD", fr.outputs[0], 0.65, 0.35))
            em = N_("ShaderNodeEmission")
            L_(et.outputs["Color"], em.inputs["Color"])
            L_(strength, em.inputs["Strength"])
            shader = add(shader, em.outputs["Emission"])
        if sh["emit_on"]:
            em = N_("ShaderNodeEmission")
            col = tuple(min(1.0, c) for c in sh["emit_col"]) + (1.0,)
            if tg is not None:
                mix = N_("ShaderNodeMix")
                mix.data_type = "RGBA"
                mix.blend_type = "MULTIPLY"
                mix.inputs["Factor"].default_value = 1.0
                L_(tex(tg).outputs["Color"], mix.inputs[6])
                mix.inputs[7].default_value = col
                L_(mix.outputs[2], em.inputs["Color"])
            else:
                em.inputs["Color"].default_value = col
            em.inputs["Strength"].default_value = sh["emit_mult"]
            shader = add(shader, em.outputs["Emission"])
        al = sh["alpha"]
        if al and (al["blend"] or al["test"]) and dnode is not None:
            a = math("MULTIPLY", dnode.outputs["Alpha"], sh["mat_alpha"])
            if al["test"]:
                keep = math("GREATER_THAN", a, al["ref"] / 255.0)
                a = math("MULTIPLY", a, keep) if al["blend"] else keep
            tr = N_("ShaderNodeBsdfTransparent")
            mx = N_("ShaderNodeMixShader")
            L_(a, mx.inputs["Factor"])
            L_(tr.outputs[0], mx.inputs[1])
            L_(shader, mx.inputs[2])
            shader = mx.outputs[0]
        if not sh["two_sided"]:
            tr = N_("ShaderNodeBsdfTransparent")
            mx = N_("ShaderNodeMixShader")
            L_(geo.outputs["Backfacing"], mx.inputs["Factor"])
            L_(shader, mx.inputs[1])
            L_(tr.outputs[0], mx.inputs[2])
            shader = mx.outputs[0]
        L_(shader, out.inputs["Surface"])
        try:   # nothing lights the scene but the sun, the sky and the lamp's light: FO4's emissive lights nothing
            m.cycles.emission_sampling = "NONE"
        except (AttributeError, TypeError):
            pass
        return m

    # --- meshes
    def add_shapes(self, shapes, which):
        bpy = self.bpy
        for s in shapes:
            me = bpy.data.meshes.new(s["name"])
            v, tri = s["v"].astype(np.float32), s["tri"].astype(np.int32)
            me.vertices.add(len(v))
            me.vertices.foreach_set("co", v.ravel())
            me.loops.add(len(tri) * 3)
            me.loops.foreach_set("vertex_index", tri.ravel())
            me.polygons.add(len(tri))
            me.polygons.foreach_set("loop_start", np.arange(0, len(tri) * 3, 3, dtype=np.int32))
            me.polygons.foreach_set("loop_total", np.full(len(tri), 3, np.int32))
            me.update(calc_edges=True)
            lay = me.uv_layers.new(name="UVMap")
            luv = s["uv"][tri.ravel()].astype(np.float32).copy()
            luv[:, 1] = 1.0 - luv[:, 1]          # the nif's v runs down, Blender's up
            lay.data.foreach_set("uv", luv.ravel())
            me.polygons.foreach_set("use_smooth", np.ones(len(tri), bool))
            if s["n"] is not None:
                n = s["n"] / np.maximum(np.linalg.norm(s["n"], axis=1, keepdims=True), 1e-9)
                me.normals_split_custom_set_from_vertices(n.tolist())
            me.materials.append(self.material(s["shader"], s["name"]))
            ob = bpy.data.objects.new(s["name"], me)
            self.sc.collection.objects.link(ob)
            ob.visible_glossy = False                  # no ray-traced reflections: the game has none
            ob.visible_shadow = bool(s["shader"]["cast"])
            s["ob"] = ob
            self.objects[which].append(s)

    def setup(self):
        bpy, sc, a = self.bpy, self.sc, self.args
        bpy.ops.mesh.primitive_plane_add(size=6000)
        g = bpy.context.object
        gm = bpy.data.materials.new("ground")
        if gm.node_tree is None:
            gm.use_nodes = True
        b = gm.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (0.085, 0.08, 0.072, 1)
        b.inputs["Roughness"].default_value = 0.92
        g.data.materials.append(gm)
        g.visible_glossy = False
        w = bpy.data.worlds.new("w")
        sc.world = w
        nt = w.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        out = nt.nodes.new("ShaderNodeOutputWorld")
        self.sky = nt.nodes.new("ShaderNodeTexSky")
        for t in ("MULTIPLE_SCATTERING", "HOSEK_WILKIE", "PREETHAM"):
            try:
                self.sky.sky_type = t
                break
            except TypeError:
                pass
        for k, v in (("sun_disc", False), ("sun_elevation", math.asin(SUN_DIR[2])),
                     ("sun_rotation", math.atan2(SUN_DIR[1], SUN_DIR[0]) + math.pi / 2)):
            try:
                setattr(self.sky, k, v)
            except (AttributeError, TypeError):
                pass
        self.bg = nt.nodes.new("ShaderNodeBackground")
        self.bg_night = nt.nodes.new("ShaderNodeBackground")
        self.bg_night.inputs["Color"].default_value = (0.010, 0.014, 0.030, 1)
        self.sky_mix = nt.nodes.new("ShaderNodeMixShader")       # 0 day sky, 1 night
        black = nt.nodes.new("ShaderNodeBackground")
        black.inputs["Color"].default_value = (0, 0, 0, 1)
        lp = nt.nodes.new("ShaderNodeLightPath")
        gmix = nt.nodes.new("ShaderNodeMixShader")               # glossy rays see no sky: the cube does that
        nt.links.new(self.sky.outputs["Color"], self.bg.inputs["Color"])
        nt.links.new(self.bg.outputs[0], self.sky_mix.inputs[1])
        nt.links.new(self.bg_night.outputs[0], self.sky_mix.inputs[2])
        nt.links.new(lp.outputs["Is Glossy Ray"], gmix.inputs[0])
        nt.links.new(self.sky_mix.outputs[0], gmix.inputs[1])
        nt.links.new(black.outputs[0], gmix.inputs[2])
        nt.links.new(gmix.outputs[0], out.inputs["Surface"])
        from mathutils import Vector
        sd = bpy.data.lights.new("sun", "SUN")
        sd.angle = math.radians(1.5)
        sd.color = (1.0, 0.95, 0.88)
        self.sun = bpy.data.objects.new("sun", sd)
        self.sun.rotation_euler = Vector(SUN_DIR).to_track_quat("Z", "Y").to_euler()
        sc.collection.objects.link(self.sun)
        md = bpy.data.lights.new("moon", "SUN")
        md.angle = math.radians(1.0)
        md.color = (0.62, 0.72, 1.0)
        self.moon = bpy.data.objects.new("moon", md)
        self.moon.rotation_euler = Vector((-0.4, 0.3, 0.86)).to_track_quat("Z", "Y").to_euler()
        sc.collection.objects.link(self.moon)
        ld = bpy.data.lights.new("lamp", "SPOT")
        ld.spot_size = math.radians(78)
        ld.spot_blend = 0.6
        ld.color = (1.0, 0.945, 0.878)                           # the LIGH record's 255/241/224
        ld.shadow_soft_size = 0.5
        self.lamp = bpy.data.objects.new("lamp", ld)
        sc.collection.objects.link(self.lamp)
        cd = bpy.data.cameras.new("cam")
        cd.clip_start, cd.clip_end = 0.5, 8000
        self.cam = bpy.data.objects.new("cam", cd)
        sc.collection.objects.link(self.cam)
        sc.camera = self.cam
        sc.render.engine = "CYCLES"
        cy = sc.cycles
        cy.device = "CPU"
        cy.samples = a.samples
        cy.use_adaptive_sampling = True
        cy.adaptive_threshold = 0.05
        cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces = 3, a.bounces, 1
        cy.transmission_bounces, cy.volume_bounces, cy.transparent_max_bounces = 0, 0, 8
        cy.caustics_reflective = cy.caustics_refractive = False
        cy.sample_clamp_indirect = 4.0
        try:                     # the indirect light past the first bounce as AO: cheap, and close to the game's
            cy.use_fast_gi = True
            cy.fast_gi_method = "REPLACE"
            sc.world.light_settings.distance = 60.0
        except (AttributeError, TypeError):
            pass
        cy.use_denoising = True
        # ACCURATE prefilters the albedo/normal guides: with FAST, the guides' own sampling noise on a glossy
        # surface in the sun (the clear-coat paint) told the denoiser to keep the noise, and it showed as a fine
        # sparkle that the game (no sampling) never has; ~4 s a frame more
        for k, val in (("denoiser", "OPENIMAGEDENOISE"), ("denoising_prefilter", a.prefilter),
                       ("denoising_quality", a.denoise)):
            try:
                setattr(cy, k, val)
            except (AttributeError, TypeError):
                pass
        sc.render.use_persistent_data = True
        sc.render.threads_mode = "FIXED"
        sc.render.threads = a.threads
        sc.render.resolution_x, sc.render.resolution_y = a.size
        sc.render.resolution_percentage = 100
        sc.render.image_settings.file_format = "PNG"
        sc.view_settings.view_transform = a.view_transform

    def set_preset(self, preset, lamp_on, parts):
        night = preset == NIGHT
        self.sky_mix.inputs[0].default_value = 1.0 if night else 0.0
        self.bg.inputs["Strength"].default_value = self.args.sky
        self.bg_night.inputs["Strength"].default_value = 1.0
        self.sun.data.energy = 0.0 if night else self.args.sun
        self.moon.data.energy = 0.06 if night else 0.0
        self.sc.view_settings.exposure = self.args.night_exposure if night else self.args.exposure
        k = self.args.night_env if night else 1.0
        for kv, scale in self.env_values:
            kv.outputs[0].default_value = scale * k
        from mathutils import Vector
        lp = Vector(parts.get("LampPoint", [0.3, 76.3, 81.9]))
        ax = Vector(parts.get("LampAxis", [0, 1, 0])).normalized()
        pitch = math.radians(2.0)                                  # [Lamp] Pitch, the beam dipped 2 degrees
        beam = (ax * math.cos(pitch) - Vector((0, 0, 1)) * math.sin(pitch)).normalized()
        self.lamp.location = lp + ax * 28.0                        # [Lamp] Ahead: 28 out along the beam
        self.lamp.rotation_euler = (-beam).to_track_quat("Z", "Y").to_euler()
        self.lamp.data.energy = self.args.lamp_power if (night and lamp_on) else 0.0

    def look(self, cam, at, lens):
        from mathutils import Vector
        self.cam.location = Vector(cam)
        self.cam.rotation_euler = (Vector(at) - Vector(cam)).to_track_quat("-Z", "Y").to_euler()
        self.cam.data.lens = lens


def turn_matrix(axis, point, deg):
    from mathutils import Matrix, Vector
    p = Vector(point)
    return Matrix.Translation(p) @ Matrix.Rotation(math.radians(deg), 4, Vector(axis).normalized()) @ Matrix.Translation(-p)


def view_state(name, v, args, parts):
    st = dict(preset=v.get("preset", DAY), parked=v.get("parked", False), mph=v.get("mph", 0.0),
              brake=v.get("brake", False), mirrors=v.get("mirrors", 1), bar=v.get("bar", 0) * parts.get("BarAngle", 20.0))
    st["lamp"] = st["preset"] == NIGHT                       # MCM "On at night", the default
    st.update(tail=args.tail, backlight=args.backlight, needle=args.needle)
    for kv in args.set or []:
        k, val = kv.split("=", 1)
        st[k] = type(st.get(k, 0.0))(float(val)) if not isinstance(st.get(k), str) else val
    return st


def apply_state(scene, st, parts):
    """Visibility and maps of the shapes as the plugin leaves them on this frame."""
    from mathutils import Matrix
    sig = []
    np_ = parts.get("NeedlePoint")
    na = parts.get("NeedleAxis")
    theta = parts.get("NeedleZero", 0.0) + min(parts.get("NeedleMax", 240.0), parts.get("NeedlePerMph", 3.0) * st["mph"])
    sa, sp = parts.get("SteerAxis"), parts.get("SteerPoint")
    for which in ("worn", "parked"):
        for s in scene.objects[which]:
            ob, role = s["ob"], s["role"]
            show = (which == "parked") == st["parked"]
            M = Matrix.Identity(4)
            if which == "worn" and show:
                if role == "glow":
                    show = st["lamp"]
                elif role == "backlight":
                    show = st["lamp"] and bool(st["backlight"])
                elif role == "tail":
                    show = bool(st["tail"])
                elif role == "brake":
                    show = bool(st["brake"])
                elif role == "needle":
                    show = bool(st["needle"])
                    if np_ and na:
                        M = turn_matrix(na, np_, -theta)       # clockwise as the rider sees it
                if s["variant"]:
                    show = show and s["variant"] == st["mirrors"]
                if role in TURNING and st["bar"] and sa and sp:
                    M = turn_matrix(sa, sp, st["bar"]) @ M
            ob.hide_render = not show
            ob.matrix_world = M
            if show:
                sig.append((s["name"], tuple(round(x, 4) for row in M for x in row)))
    return sig


# ----------------------------------------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pynifly", type=Path)
    ap.add_argument("--data", type=Path, help="a Data folder (Meshes\\CMB, Textures, Materials)")
    ap.add_argument("--nif", default="Meshes/CMB/CMB_BikeWorn.nif", help="the riding bike, relative to --data")
    ap.add_argument("--parked-nif", default="Meshes/CMB/CMB_BikeParked.nif")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--prefix", default="")
    ap.add_argument("--views", default="all", help="all, a set (" + ", ".join(SETS) + ") or names, comma-separated")
    ap.add_argument("--size", default="1280x800")
    ap.add_argument("--samples", type=int, default=10)
    ap.add_argument("--bounces", type=int, default=1, help="diffuse bounces (the rest as AO)")
    ap.add_argument("--denoise", default="BALANCED", choices=("HIGH", "BALANCED", "FAST"), help="OIDN quality")
    ap.add_argument("--prefilter", default="ACCURATE", choices=("ACCURATE", "FAST", "NONE"),
                    help="OIDN's prefilter of the albedo/normal guides (FAST showed a sampling sparkle on the"
                         " paint in a first set of renders)")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--env", type=Path, help="where the vanilla cubes' stand-ins are kept (default <out>/env)")
    ap.add_argument("--cube-up", choices=("y", "z"), default="y", help="our cube's up face (D3D +Y; z = the zup file)")
    ap.add_argument("--bgsm", type=int, default=1, help="0: ignore material files (the Materials\\CMB rename A/B)")
    ap.add_argument("--sun", type=float, default=3.2)
    ap.add_argument("--sky", type=float, default=0.12)
    ap.add_argument("--exposure", type=float, default=0.0)
    ap.add_argument("--view-transform", default="AgX",
                    help="Blender's view transform: AgX (default) desaturates very bright colours toward white, so a"
                         " strong red emissive reads pink; Standard clips each channel, nearer the game's per-channel"
                         " tone curve for judging a light's hue")
    ap.add_argument("--night-exposure", type=float, default=1.6)
    ap.add_argument("--night-env", type=float, default=0.3, help="cube reflections' share at night (untested in game)")
    ap.add_argument("--lamp-power", type=float, default=1.0e6)
    ap.add_argument("--normal-green", choices=("dx", "gl"), default="dx",
                    help="how _n's green is read: dx (FO4's, +Y down the image) or gl (a check of the other way)")
    ap.add_argument("--tail", type=int, default=1, help="[Tail] Glow")
    ap.add_argument("--backlight", type=int, default=1, help="[Speedo] Backlight")
    ap.add_argument("--needle", type=int, default=1, help="[Speedo] Needle")
    ap.add_argument("--set", action="append", help="override a view's state, e.g. mirrors=2, mph=40, bar=10, lamp=1")
    ap.add_argument("--sheet", nargs="+", metavar=("OUT", "PNG"))
    ap.add_argument("--compare", nargs=4, metavar=("DIR", "PREFIX_A", "PREFIX_B", "OUT"))
    ap.add_argument("--list-views", action="store_true")
    args = ap.parse_args()
    if args.list_views:
        for k, v in SETS.items():
            print(f"{k}: {', '.join(v)}")
        return 0
    if args.sheet:
        print(sheet(args.sheet[0], args.sheet[1:]))
        return 0
    if args.compare:
        print(compare(*args.compare))
        return 0
    if not (args.pynifly and args.data and args.out):
        ap.error("--pynifly, --data and --out are needed to render")
    args.size = tuple(int(x) for x in args.size.lower().split("x"))
    args.out.mkdir(parents=True, exist_ok=True)
    args.env = args.env or args.out / "env"
    names = []
    for part in args.views.split(","):
        names += SETS.get(part, [part])
    for n in names:
        if n not in VIEWS:
            ap.error(f"no view {n!r} (--list-views)")
    t0 = time.time()
    data = DataIndex(args.data)
    parts = read_parts(data.find("Meshes/CMB/CMB_BikeParts.ini"))
    fit = data.find("Meshes/CMB/CMB_BikeFit.json")
    seat_at = json.loads(fit.read_text()).get("seat_at", 27.69) if fit else 27.69
    scene = Scene(args, data)
    scene.setup()
    worn = read_nif(args.pynifly, data.find(args.nif), data, args.bgsm)
    scene.add_shapes(worn, "worn")
    if any(VIEWS[n].get("parked") for n in names):
        pk = data.find(args.parked_nif)
        parked = read_nif(args.pynifly, pk, data, args.bgsm, to_worn=(np.array([-1.0, -1.0, 1.0]), np.array([0, seat_at, 0])))
        scene.add_shapes(parked, "parked")
    t_build = time.time() - t0
    lines = [f"data {args.data}, worn {args.nif}: {len(worn)} shapes, bgsm {args.bgsm}"]
    for s in worn:
        sh = s["shader"]
        lines.append(f"  {s['name']:<38} {s['role']:<9}{'v' + str(s['variant']) if s['variant'] else '  '} "
                     f"type {sh['type']} {sh['source']:<6} env {'%.2f %s' % (sh['env_scale'], Path(sh['tex']['cube'].replace(chr(92), '/')).stem) if sh['env_on'] else '-':<40} "
                     f"emit {'%.1f' % sh['emit_mult'] if sh['emit_on'] else '-':<5} smooth {sh['smooth']:.2f} spec {sh['spec_mult']:.2f} "
                     f"{'2-sided' if sh['two_sided'] else '1-sided'} {'shadow' if sh['cast'] else 'no-shadow'}"
                     f"{' alpha' if sh['alpha'] else ''} verts {len(s['v'])} tris {len(s['tri'])}")
    lines += sorted(set(scene.log))
    lines.append(f"scene built in {t_build:.1f} s")
    print("\n".join(lines), flush=True)
    timings, done = {}, {}
    for n in names:
        v = VIEWS[n]
        st = view_state(n, v, args, parts)
        sig = (st["preset"], st["lamp"], v["cam"], v["at"], v["lens"], tuple(apply_state(scene, st, parts)))
        path = args.out / f"{args.prefix}{n}.png"
        if sig in done:
            shutil.copyfile(done[sig], path)
            timings[n] = dict(seconds=0.0, same_as=done[sig].name)
            print(f"{n}: the same frame as {done[sig].name} (copied)", flush=True)
            continue
        scene.set_preset(st["preset"], st["lamp"], parts)
        scene.look(v["cam"], v["at"], v["lens"])
        scene.sc.render.filepath = str(path)
        t1 = time.time()
        scene.bpy.ops.render.render(write_still=True)
        dt = time.time() - t1
        timings[n] = dict(seconds=round(dt, 1), state={k: st[k] for k in sorted(st)})
        done[sig] = path
        print(f"{n}: {dt:.1f} s -> {path}", flush=True)
    for sname, members in SHEETS.items():
        if all(m in names for m in members):
            sheet(args.out / f"{args.prefix}{sname}.png", [args.out / f"{args.prefix}{m}.png" for m in members], cols=2)
    tfile = args.out / f"{args.prefix}timings.json"
    old = json.loads(tfile.read_text()) if tfile.exists() else {}
    old.update(timings)
    old["_last_run"] = dict(scene_build_s=round(t_build, 1), wall_s=round(time.time() - t0, 1),
                            size=list(args.size), samples=args.samples, threads=args.threads, views=names)
    tfile.write_text(json.dumps(old, indent=1))
    (args.out / f"{args.prefix}shapes.txt").write_text("\n".join(lines) + "\n")
    print(f"total {time.time() - t0:.1f} s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
