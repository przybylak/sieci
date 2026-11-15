#!/usr/bin/env python3
"""Round-trip test of tools/rider/write_dds.py (Commonwealth Motorbike asset tools; rewritten 2026-11-14 after
the one write_dds.py's header names was lost with its folder).

Every format write_dds.py writes, each with every encoder it can use: the header parsed here (not by write_dds),
each mip decoded here (BC1/BC3/BC4/BC5 by this file's own numpy decoders and by texture2ddecoder, BC7 by
texture2ddecoder) and compared, as PSNR over the channels the format stores, with the mip write_dds.py made from
the source. Then the options (normal maps, linear-light mips, sRGB, cube maps, one mip, green flipped), the
command line (--info, --batch with a .npy input, a PNG input) and that two runs give the same bytes.

    <DDS python> -I dds_roundtrip.py <repository>/tools/rider [--out <folder>] [--digests]

--out keeps the files written (default: a temporary folder, removed). --digests prints each case's SHA-256
(a later setup with the same package versions should print the same ones).
Exit 0 and a last line "N checks, all passed".
"""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

BLOCK = {"bc1": 8, "bc3": 16, "bc4": 8, "bc5": 16, "bc7": 16}
LEGACY = {b"DXT1": "bc1", b"DXT5": "bc3", b"ATI1": "bc4", b"ATI2": "bc5"}
DXGI = {71: ("bc1", False), 72: ("bc1", True), 77: ("bc3", False), 78: ("bc3", True), 80: ("bc4", False),
        83: ("bc5", False), 98: ("bc7", False), 99: ("bc7", True), 28: ("rgba8", False), 29: ("rgba8", True)}


# --- this file's own reading -------------------------------------------------------------------------------------

def parse(data):
    """The header, by the DDS documentation: dict(w, h, mips, fmt, srgb, dx10, cube, bgra, offset)."""
    if data[:4] != b"DDS " or struct.unpack_from("<I", data, 4)[0] != 124:
        raise ValueError("not a DDS header")
    flags, h, w, pitch, depth, mips = struct.unpack_from("<6I", data, 8)
    pf_size, pf_flags, fourcc, bits, rm, gm, bm, am = struct.unpack_from("<II4sIIIII", data, 76)
    caps, caps2 = struct.unpack_from("<2I", data, 108)
    if pf_size != 32:
        raise ValueError("pixel format size")
    d = dict(w=w, h=h, mips=max(1, mips), flags=flags, pitch=pitch, caps=caps, cube=bool(caps2 & 0x200),
             dx10=fourcc == b"DX10", srgb=False, bgra=False, offset=128)
    if d["dx10"]:
        dxgi, dim, misc, array, misc2 = struct.unpack_from("<5I", data, 128)
        d["fmt"], d["srgb"] = DXGI[dxgi]
        d.update(offset=148, dxgi=dxgi, dim=dim, misc=misc, array=array)
    elif pf_flags & 0x4:
        d["fmt"] = LEGACY[fourcc]
    else:
        if (bits, rm, gm, bm, am) != (32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000):
            raise ValueError("an uncompressed layout other than A8R8G8B8")
        d.update(fmt="rgba8", bgra=True)
    return d


def _blocks(buf, w, h, size):
    return np.frombuffer(buf, np.uint8).reshape(h // 4, w // 4, size)


def _colour_block(b, four_always):
    """(H/4, W/4, 8) BC1 colour blocks -> (H/4, W/4, 4, 4, 4) RGBA uint8."""
    c0 = b[..., 0].astype(np.uint32) | (b[..., 1].astype(np.uint32) << 8)
    c1 = b[..., 2].astype(np.uint32) | (b[..., 3].astype(np.uint32) << 8)

    def rgb(c):
        r, g, bl = (c >> 11) & 31, (c >> 5) & 63, c & 31
        return np.stack([(r << 3) | (r >> 2), (g << 2) | (g >> 4), (bl << 3) | (bl >> 2)], -1).astype(np.float64)
    p0, p1 = rgb(c0), rgb(c1)
    four = (c0 > c1)[..., None] | four_always
    pal = np.zeros(c0.shape + (4, 4), np.float64)
    pal[..., 0, :3], pal[..., 1, :3] = p0, p1
    pal[..., 2, :3] = np.where(four, (2 * p0 + p1) / 3, (p0 + p1) / 2)
    pal[..., 3, :3] = np.where(four, (p0 + 2 * p1) / 3, 0)
    pal[..., 3] = 255
    pal[..., 3, 3] = np.where(four[..., 0], 255, 0)
    bits = b[..., 4:8].astype(np.uint32)
    idx = np.stack([(bits[..., r] >> (2 * c)) & 3 for r in range(4) for c in range(4)], -1)   # (.., 16)
    out = np.take_along_axis(pal, idx[..., None].repeat(4, -1), axis=-2)
    return np.clip(np.rint(out), 0, 255).astype(np.uint8).reshape(c0.shape + (4, 4, 4))


def _alpha_block(b):
    """(H/4, W/4, 8) BC4 blocks -> (H/4, W/4, 4, 4) uint8."""
    a0, a1 = b[..., 0].astype(np.float64), b[..., 1].astype(np.float64)
    pal = np.zeros(a0.shape + (8,), np.float64)
    pal[..., 0], pal[..., 1] = a0, a1
    eight = a0 > a1
    for i in range(1, 7):
        pal[..., i + 1] = np.where(eight, ((7 - i) * a0 + i * a1) / 7, ((5 - i) * a0 + i * a1) / 5 if i < 5 else 0)
    pal[..., 7] = np.where(eight, pal[..., 7], 255)
    bits = np.zeros(a0.shape, np.uint64)
    for i in range(6):
        bits |= b[..., 2 + i].astype(np.uint64) << np.uint64(8 * i)
    idx = np.stack([(bits >> np.uint64(3 * i)) & np.uint64(7) for i in range(16)], -1).astype(np.int64)
    out = np.take_along_axis(pal, idx, axis=-1)
    return np.clip(np.rint(out), 0, 255).astype(np.uint8).reshape(a0.shape + (4, 4))


def _tile(x):
    """(H/4, W/4, 4, 4[, c]) -> (H, W[, c])."""
    return x.swapaxes(1, 2).reshape((x.shape[0] * 4, x.shape[1] * 4) + x.shape[4:])


def decode_own(fmt, buf, w, h):
    """Block data -> (h, w, 4) RGBA uint8 (BC4: the channel in R, G = B = 0... as stored: R only; BC5: R and G)."""
    b = _blocks(buf, w, h, BLOCK[fmt])
    out = np.zeros((h, w, 4), np.uint8)
    out[..., 3] = 255
    if fmt == "bc1":
        out[:] = _tile(_colour_block(b, False))
    elif fmt == "bc3":
        out[:] = _tile(_colour_block(b[..., 8:], True))
        out[..., 3] = _tile(_alpha_block(b[..., :8]))
    elif fmt == "bc4":
        out[..., 0] = _tile(_alpha_block(b))
    elif fmt == "bc5":
        out[..., 0] = _tile(_alpha_block(b[..., :8]))
        out[..., 1] = _tile(_alpha_block(b[..., 8:]))
    else:
        raise ValueError(fmt)
    return out


def decode_t2d(fmt, buf, w, h):
    import texture2ddecoder as t2d
    dec = {"bc1": t2d.decode_bc1, "bc3": t2d.decode_bc3, "bc4": t2d.decode_bc4, "bc5": t2d.decode_bc5,
           "bc7": t2d.decode_bc7}[fmt]
    return np.frombuffer(dec(bytes(buf), w, h), np.uint8).reshape(h, w, 4)[..., [2, 1, 0, 3]]


def levels_of(data, d):
    """[faces][mips] of (source-size RGBA by this file's decoder or None, by texture2ddecoder or None)."""
    off, out = d["offset"], []
    for _ in range(6 if d["cube"] else 1):
        w, h, lv = d["w"], d["h"], []
        for _ in range(d["mips"]):
            if d["fmt"] == "rgba8":
                n = w * h * 4
                px = np.frombuffer(data, np.uint8, n, off).reshape(h, w, 4)
                lv.append((px[..., [2, 1, 0, 3]] if d["bgra"] else px, None))
            else:
                W, H = (w + 3) // 4 * 4, (h + 3) // 4 * 4
                n = (W // 4) * (H // 4) * BLOCK[d["fmt"]]
                buf = data[off:off + n]
                own = decode_own(d["fmt"], buf, W, H)[:h, :w] if d["fmt"] != "bc7" else None
                lv.append((own, decode_t2d(d["fmt"], buf, W, H)[:h, :w]))
            off += n
            w, h = max(1, w // 2), max(1, h // 2)
        out.append(lv)
    if off != len(data):
        raise ValueError(f"{len(data) - off} bytes left after the last mip")
    return out


def psnr(a, b):
    mse = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
    return 99.0 if mse == 0 else 10 * np.log10(255.0 ** 2 / mse)


# --- the test image ----------------------------------------------------------------------------------------------

def picture(w=256, h=128, alpha=True, seed=7):
    """Gradients, a disc with a hard edge, stripes and a little noise; alpha a ramp with a hole."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:h, 0:w].astype(np.float64)
    r = 40 + 170 * x / (w - 1)
    g = 60 + 150 * y / (h - 1)
    b = 128 + 100 * np.sin(x / 9.0) * np.cos(y / 13.0)
    disc = (x - w * 0.3) ** 2 + (y - h * 0.5) ** 2 < (h * 0.3) ** 2
    r, g, b = np.where(disc, 220, r), np.where(disc, 40, g), np.where(disc, 30, b)
    stripes = ((x + y) // 8 % 2 == 0) & (x > w * 0.7)
    g = np.where(stripes, 230, g)
    img = np.stack([r, g, b], -1) + rng.normal(0, 3, (h, w, 3))
    a = np.full((h, w), 255.0)
    if alpha:
        a = 255 * x / (w - 1)
        a[(x - w * 0.75) ** 2 + (y - h * 0.5) ** 2 < (h * 0.2) ** 2] = 0
    return np.clip(np.rint(np.dstack([img, a])), 0, 255).astype(np.uint8)


def normal_map(w=128, h=128):
    y, x = np.mgrid[0:h, 0:w].astype(np.float64)
    nx, ny = 0.6 * np.sin(x / 7.0), 0.6 * np.cos(y / 5.0)
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    n = np.stack([nx, ny, nz], -1)
    return np.clip(np.rint(np.dstack([n * 127.5 + 127.5, np.full((h, w), 255.0)])), 0, 255).astype(np.uint8)


# --- the checks ----------------------------------------------------------------------------------------------------

# the lowest PSNR (dB) a case's first mip may show, by format and encoder: what this picture gave on 2026-11-14
# with pillow 13.0.0, numpy 2.5.4, etcpak 0.9.15, quicktex 0.3.1 and texture2ddecoder 1.0.6, less a decibel or
# two (etcpak's BC1 is poor on this picture's noise: 27 dB where quicktex gives 38). The smaller mips, where the
# noise and the hard edges are a few texels, only have to stay above ANY_MIP.
FLOOR = {("bc1", "quicktex"): 36.0, ("bc1", "etcpak"): 26.0, ("bc3", "quicktex"): 37.0, ("bc3", "etcpak"): 27.0,
         ("bc4", "quicktex"): 46.0, ("bc4", "etcpak"): 45.0, ("bc5", "quicktex"): 43.0, ("bc5", "etcpak"): 42.0,
         ("bc7", "etcpak"): 37.0}
ANY_MIP = 14.0
CHANNELS = {"bc1": [0, 1, 2], "bc3": [0, 1, 2, 3], "bc4": [0], "bc5": [0, 1], "bc7": [0, 1, 2, 3],
            "rgba8": [0, 1, 2, 3]}


class Run:
    def __init__(self, WD, out, digests):
        self.WD, self.out, self.digests, self.n, self.bad = WD, out, digests, 0, 0

    def check(self, what, ok):
        self.n += 1
        self.bad += 0 if ok else 1
        print(("  ok   " if ok else "  FAIL ") + what, flush=True)

    def case(self, name, images, fmt, floor=None, expect=None, **kw):
        """Build, parse and decode here, compare with write_dds.py's own mips; returns the bytes."""
        WD = self.WD
        data = WD.build(images, fmt, **kw)
        (self.out / f"{name}.dds").write_bytes(data)
        d = parse(data)
        exp = dict(w=images[0].shape[1], h=images[0].shape[0], fmt=fmt, cube=len(images) == 6)
        exp.update(expect or {})
        hdr = all(d[k] == v for k, v in exp.items())
        full = 1 + int(np.floor(np.log2(max(images[0].shape[:2]))))
        mips = full if kw.get("mips", 0) == 0 else min(kw["mips"], full)
        hdr &= d["mips"] == mips and bool(d["flags"] & 0x20000) == (mips > 1)
        hdr &= d["pitch"] == (exp["w"] * 4 if fmt == "rgba8" else (exp["w"] // 4) * (exp["h"] // 4) * BLOCK[fmt])
        try:
            faces = levels_of(data, d)
        except ValueError as e:
            self.check(f"{name}: {e}", False)
            return data
        lows, firsts, worst_gap, exact = [], [], 0, True
        linear = (kw.get("srgb") or kw.get("gamma_mips")) and not kw.get("normal")
        for im, lv in zip(images, faces):
            src = im.copy()
            if kw.get("flip_green"):
                src[..., 1] = 255 - src[..., 1]
            want = WD.mip_chain(src, kw.get("mips", 0), linear_rgb=bool(linear), normal=bool(kw.get("normal")))
            for (own, t2d), ref in zip(lv, want):
                ch = CHANNELS[fmt]
                got = own if own is not None else t2d
                if fmt == "rgba8":
                    exact &= bool((got == ref).all())
                    continue
                if got.shape[0] >= 4 and got.shape[1] >= 4:
                    lows.append(psnr(got[..., ch], ref[..., ch]))
                    if got.shape[:2] == src.shape[:2]:
                        firsts.append(lows[-1])
                if own is not None and t2d is not None:   # two decoders: the same picture to a rounding step
                    worst_gap = max(worst_gap, int(np.abs(own[..., ch].astype(int) - t2d[..., ch].astype(int)).max()))
        mine = WD.read_dds(self.out / f"{name}.dds")
        same_reader = mine[0]["w"] == d["w"] and mine[0]["mips"] == d["mips"] and len(mine[1]) == len(faces)
        if fmt == "rgba8":
            ok, note = hdr and exact and same_reader, "every mip exact"
        else:
            enc = "etcpak" if fmt == "bc7" or kw.get("encoder") == "etcpak" else "quicktex"
            fl = FLOOR[(fmt, enc)] if floor is None else floor
            ok = hdr and same_reader and min(firsts) >= fl and min(lows) >= ANY_MIP and worst_gap <= 2
            note = f"PSNR {min(firsts):.1f} dB (floor {fl:.0f}), {min(lows):.1f} at the worst of {len(lows)} mips" + \
                   (f", decoders within {worst_gap}" if fmt != "bc7" else "")
        hd = f"{d['w']}x{d['h']} {'DX10 ' + str(d['dxgi']) if d['dx10'] else 'legacy'} mips {d['mips']}" + \
             (" cube" if d["cube"] else "")
        tail = f" sha256 {hashlib.sha256(data).hexdigest()[:16]}" if self.digests else ""
        self.check(f"{name}: {hd}, {len(data)} bytes; {note}{'' if hdr else '; HEADER WRONG ' + str(d)}{tail}", ok)
        again = WD.build(images, fmt, **kw)
        if again != data:
            self.check(f"{name}: a second build differs", False)
        return data


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rider", type=Path, help="the repository's tools/rider folder (write_dds.py)")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--digests", action="store_true")
    a = ap.parse_args()
    sys.dont_write_bytecode = True   # no __pycache__ beside the repository's files
    sys.path.insert(0, str(a.rider.resolve()))
    import write_dds as WD
    from PIL import Image
    import importlib.metadata as md
    print("python", sys.version.split()[0], " ".join(f"{n} {md.version(n)}" for n in
          ("pillow", "numpy", "etcpak", "quicktex", "texture2ddecoder")))
    tmp = None
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        out = a.out
    else:
        tmp = tempfile.TemporaryDirectory()
        out = Path(tmp.name)
    R = Run(WD, out, a.digests)
    rgba, rgb, nrm = picture(alpha=True), picture(alpha=False), normal_map()

    print("formats and encoders")
    for enc in ("auto", "etcpak"):
        e = "" if enc == "auto" else "_etcpak"
        R.case(f"bc1{e}", [rgb], "bc1", encoder=enc)
        R.case(f"bc3{e}", [rgba], "bc3", encoder=enc)
        R.case(f"bc4{e}", [rgb], "bc4", encoder=enc)
        R.case(f"bc5{e}", [rgb], "bc5", encoder=enc)
    R.case("bc1_quicktex", [rgb], "bc1", encoder="quicktex")
    R.case("bc7_opaque", [rgb], "bc7", expect=dict(dx10=True, dxgi=98))
    R.case("bc7_alpha", [rgba], "bc7", expect=dict(dx10=True, dxgi=98))
    R.case("bc7_uber0", [rgba], "bc7", bc7_uber=0)
    R.case("rgba8_legacy", [rgba], "rgba8", expect=dict(dx10=False, bgra=True))
    R.case("rgba8_dx10", [rgba], "rgba8", header_mode="dx10", expect=dict(dx10=True, dxgi=28))

    print("options")
    R.case("bc1_dx10", [rgb], "bc1", header_mode="dx10", expect=dict(dx10=True, dxgi=71))
    R.case("bc3_srgb", [rgba], "bc3", srgb=True, expect=dict(dx10=True, dxgi=78, srgb=True))
    R.case("bc7_srgb", [rgba], "bc7", srgb=True, expect=dict(dx10=True, dxgi=99, srgb=True))
    R.case("bc1_gamma_mips", [rgb], "bc1", gamma_mips=True, expect=dict(dx10=False))
    R.case("bc5_normal", [nrm], "bc5", normal=True)
    R.case("bc5_normal_flip", [nrm], "bc5", normal=True, flip_green=True)
    R.case("bc7_normal", [nrm], "bc7", normal=True)
    R.case("bc1_one_mip", [rgb], "bc1", mips=1)
    R.case("bc3_three_mips", [rgba], "bc3", mips=3)
    R.case("rgba8_one_mip", [rgba], "rgba8", mips=1)
    sq = [np.ascontiguousarray(np.roll(picture(64, 64, alpha=False, seed=s), s * 5, axis=1)) for s in range(6)]
    R.case("bc1_cube", sq, "bc1", cube=True, floor=30.0, expect=dict(cube=True))   # 64x64: the same detail, smaller
    R.case("rgba8_cube", sq, "rgba8", cube=True, expect=dict(cube=True))

    # the normal map's mips stay unit vectors (the stored X, Y give a Z; nothing longer than 1)
    lv = WD.mip_chain(nrm, 0, normal=True)
    v = np.concatenate([(m[..., :3].astype(np.float64) / 255 * 2 - 1).reshape(-1, 3) for m in lv])
    ln = np.linalg.norm(v, axis=1)
    R.check(f"normal mips: lengths {ln.min():.3f}..{ln.max():.3f} over {len(lv)} mips", 0.97 < ln.min() and ln.max() < 1.03)
    # linear-light mips are brighter than gamma-space ones where light and dark meet
    chk = np.zeros((64, 64, 4), np.uint8)
    chk[..., 3] = 255
    chk[(np.add.outer(np.arange(64), np.arange(64)) % 2) == 0, :3] = 255
    g_, l_ = WD.mip_chain(chk, 2)[1], WD.mip_chain(chk, 2, linear_rgb=True)[1]
    R.check(f"a checkerboard's second mip: {int(g_[0, 0, 0])} in gamma space, {int(l_[0, 0, 0])} in linear light",
            126 <= int(g_[0, 0, 0]) <= 129 and 186 <= int(l_[0, 0, 0]) <= 189)
    for bad, why in (((rgb[:126, :250], "bc1"), "sides not multiples of 4"), ((rgb, "bc5", 0, True), "BC5 sRGB")):
        try:
            WD.build([bad[0]], *bad[1:])
            R.check(f"refuses {why}", False)
        except ValueError as e:
            R.check(f"refuses {why}: {e}", True)

    print("command line")
    exe, script = sys.executable, str(a.rider.resolve() / "write_dds.py")
    png, npy = out / "in.png", out / "in.npy"
    Image.fromarray(rgba).save(png)
    np.save(npy, rgb[..., :3])

    def run(*args):
        return subprocess.run([exe, "-I", "-B", script, *map(str, args)], capture_output=True, text=True)
    p = run(png, out / "cli_bc7.dds", "--format", "bc7")
    R.check(f"png -> bc7: {p.stdout.strip() or p.stderr.strip()[-200:]}",
            p.returncode == 0 and (out / "cli_bc7.dds").read_bytes() == WD.build([rgba], "bc7"))
    p = run(png, out / "cli_bc5.dds", "--format", "bc5", "--normal", "--flip-green", "--mips", "4")
    R.check("png -> bc5 --normal --flip-green --mips 4: the same bytes as build()",
            p.returncode == 0 and (out / "cli_bc5.dds").read_bytes()
            == WD.build([rgba], "bc5", mips=4, normal=True, flip_green=True))
    jobs = [dict(inputs=[str(npy)], output=str(out / "batch" / "b_bc1.dds"), format="bc1", gamma_mips=True),
            dict(inputs=[str(png)], output=str(out / "batch" / "b_rgba8.dds"), format="rgba8", mips=1)]
    (out / "jobs.json").write_text(json.dumps(jobs))
    p = run("--batch", out / "jobs.json")
    R.check(f"--batch, a .npy (h, w, 3) input: {len(p.stdout.splitlines())} lines",
            p.returncode == 0 and (out / "batch" / "b_bc1.dds").read_bytes() == WD.build([rgb], "bc1", gamma_mips=True)
            and (out / "batch" / "b_rgba8.dds").read_bytes() == WD.build([rgba], "rgba8", mips=1)
            and not list((out / "batch").glob("*.part")))
    p = run("--info", out / "cli_bc7.dds", out / "bc1_cube.dds", out / "rgba8_legacy.dds", out / "bc5.dds")
    lines = p.stdout.splitlines()
    R.check("--info: " + " | ".join(ln.split(": ", 1)[-1] for ln in lines),
            p.returncode == 0 and len(lines) == 4 and lines[0].endswith("256x128 DX10 BC7_UNORM mips 9")
            and lines[1].endswith("64x64 DXT1 mips 7 cube") and lines[2].endswith("256x128 RGB32 mips 9")
            and lines[3].endswith("256x128 ATI2 mips 9"))
    info, lv = WD.read_dds(out / "bc1_cube.dds")
    R.check(f"read_dds: a cube of {len(lv)} faces x {len(lv[0])} mips", info["cube"] and len(lv) == 6 and len(lv[0]) == 7
            and lv[0][0].shape == (64, 64, 4))

    if tmp:
        tmp.cleanup()
    print(f"{R.n} checks, " + ("all passed" if not R.bad else f"{R.bad} FAILED"))
    return 1 if R.bad else 0


if __name__ == "__main__":
    sys.exit(main())
