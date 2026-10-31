#!/usr/bin/env python3
"""Write a DDS texture with a full mip chain, in the formats Fallout 4 uses.

Encoders (--encoder auto, the default): quicktex (rgbcx, level 10) for BC1/BC3/BC4/BC5 - 1.5-2.5 dB better than
etcpak's - and etcpak (bc7enc) for BC7; --encoder etcpak uses etcpak for all (faster). Uncompressed RGBA8 needs
neither. BC7 of an opaque image is limited to mode 1 (bc7enc's mode 6 decodes 255 alpha as 254: -0.5 dB RGB).
Don't call etcpak.decompress_bc7: it segfaults (etcpak 0.9.15); texture2ddecoder decodes everything. Install (into a venv,
never system-wide):

    uv venv -p 3.13 <venv> && VIRTUAL_ENV=<venv> uv pip install pillow numpy etcpak quicktex texture2ddecoder

Formats (--format):
  bc1    DXT1, RGB (1-bit alpha ignored)          FO4: diffuse without alpha, env masks, glow maps
  bc3    DXT5, RGBA                               FO4: diffuse with alpha (alpha test/blend), older _s maps
  bc4    ATI1/BC4U, one channel (R)               greyscale masks
  bc5    ATI2/BC5U, two channels (R, G)           FO4: normal maps (X, Y; Z rebuilt) and specular maps (R spec, G gloss)
  bc7    BC7 (DX10 header)                        FO4: high-quality diffuse/normal with alpha (vanilla uses it too)
  rgba8  uncompressed A8R8G8B8 (legacy header) or R8G8B8A8_UNORM (--header dx10)

Headers (--header): auto (default) = legacy FourCC for bc1 (DXT1), bc3 (DXT5), bc4 (ATI1), bc5 (ATI2) and rgba8
(A8R8G8B8 masks), DX10 for bc7 and for anything --srgb; dx10 = always a DX10 extension header (BC1_UNORM...).

Colour space: Fallout 4 samples its textures as UNORM (no *_SRGB formats in vanilla); --srgb writes the *_SRGB DXGI
format (DX10 header) and filters the mips in linear light - for other engines/tests, not for FO4. --gamma-mips filters
in linear light but keeps the UNORM format (the right choice for FO4 colour maps). --normal renormalises the mips as
unit vectors (input: a tangent-space normal map, X in R, Y in G, Z in B, 128 = 0); --flip-green inverts G first
(OpenGL <-> DirectX convention).

Cube maps: --cube with six inputs in D3D order +X -X +Y -Y +Z -Z (each square, same size).

    python3 -I write_dds.py in.png out.dds --format bc7
    python3 -I write_dds.py n.png n.dds --format bc5 --normal
    python3 -I write_dds.py px.png nx.png py.png ny.png pz.png nz.png sky.dds --format bc1 --cube
    python3 -I write_dds.py --info a.dds b.dds       # header summary
    python3 -I write_dds.py --batch jobs.json        # many at once (bike_textures.py): [{"inputs", "output",
                                                     # "format", build()'s keywords}]; inputs may be .npy (uint8)

read_dds() decodes what this writes (texture2ddecoder), for checks and contact sheets. Round-trip test (every
format, independent header parse and decoder, PSNR per mip): t48's tools_test/dds_roundtrip.py <this folder> ...
"""
import argparse
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

# DXGI formats
DXGI = {
    ("rgba8", False): 28, ("rgba8", True): 29,      # R8G8B8A8_UNORM(_SRGB)
    ("bc1", False): 71, ("bc1", True): 72,
    ("bc3", False): 77, ("bc3", True): 78,
    ("bc4", False): 80, ("bc5", False): 83,
    ("bc7", False): 98, ("bc7", True): 99,
}
FOURCC = {"bc1": b"DXT1", "bc3": b"DXT5", "bc4": b"ATI1", "bc5": b"ATI2"}
BLOCK_BYTES = {"bc1": 8, "bc4": 8, "bc3": 16, "bc5": 16, "bc7": 16}

DDSD_CAPS, DDSD_HEIGHT, DDSD_WIDTH, DDSD_PITCH = 0x1, 0x2, 0x4, 0x8
DDSD_PIXELFORMAT, DDSD_MIPMAPCOUNT, DDSD_LINEARSIZE = 0x1000, 0x20000, 0x80000
DDPF_ALPHAPIXELS, DDPF_FOURCC, DDPF_RGB = 0x1, 0x4, 0x40
DDSCAPS_COMPLEX, DDSCAPS_TEXTURE, DDSCAPS_MIPMAP = 0x8, 0x1000, 0x400000
DDSCAPS2_CUBEMAP_ALLFACES = 0x200 | 0x400 | 0x800 | 0x1000 | 0x2000 | 0x4000 | 0x8000
D3D10_RESOURCE_DIMENSION_TEXTURE2D, D3D11_RESOURCE_MISC_TEXTURECUBE = 3, 0x4


# --- mips ----------------------------------------------------------------------------------

def srgb_to_linear(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def half(img):
    """2x2 box filter on a float (h, w, c) image; an odd or 1-wide side is kept by edge replication."""
    h, w = img.shape[:2]
    if h % 2 and h > 1:
        img = np.concatenate([img, img[-1:]], 0)
    if w % 2 and w > 1:
        img = np.concatenate([img, img[:, -1:]], 1)
    if img.shape[0] > 1:
        img = 0.5 * (img[0::2] + img[1::2])
    if img.shape[1] > 1:
        img = 0.5 * (img[:, 0::2] + img[:, 1::2])
    return img


def mip_chain(rgba8, count, linear_rgb=False, normal=False):
    """rgba8 (h, w, 4) uint8 -> list of uint8 levels, the first the input. count 0 = down to 1x1."""
    f = rgba8.astype(np.float64) / 255.0
    if linear_rgb:
        f[..., :3] = srgb_to_linear(f[..., :3])
    levels = [rgba8]
    h, w = rgba8.shape[:2]
    full = 1 + int(np.floor(np.log2(max(h, w))))
    n = full if count == 0 else min(count, full)
    cur = f
    for _ in range(1, n):
        cur = half(cur)
        out = cur.copy()
        if normal:
            v = out[..., :3] * 2.0 - 1.0
            v /= np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-8)
            out[..., :3] = v * 0.5 + 0.5
        if linear_rgb:
            out[..., :3] = linear_to_srgb(out[..., :3])
        levels.append(np.clip(np.rint(out * 255.0), 0, 255).astype(np.uint8))
    return levels


# --- block compression -----------------------------------------------------------------------

def pad4(img):
    """Edge-replicate to a multiple of 4 on each side (mips under 4x4 are stored as one block)."""
    h, w = img.shape[:2]
    H, W = (h + 3) // 4 * 4, (w + 3) // 4 * 4
    if (H, W) == (h, w):
        return img
    return np.pad(img, ((0, H - h), (0, W - w), (0, 0)), mode="edge")


def compress(level, fmt, encoder, bc7_uber=1, opaque=False):
    lv = np.ascontiguousarray(pad4(level))
    h, w = lv.shape[:2]
    if fmt == "rgba8":
        return level.tobytes()   # caller reorders for the legacy header
    if encoder in ("quicktex", "auto") and fmt in ("bc1", "bc3", "bc4", "bc5"):
        import quicktex.s3tc.bc1 as q1
        import quicktex.s3tc.bc3 as q3
        import quicktex.s3tc.bc4 as q4
        import quicktex.s3tc.bc5 as q5
        from quicktex import RawTexture
        raw = RawTexture.frombytes(lv.tobytes(), w, h)
        enc = {"bc1": lambda: q1.BC1Encoder(10), "bc3": lambda: q3.BC3Encoder(10), "bc4": lambda: q4.BC4Encoder(0),
               "bc5": lambda: q5.BC5Encoder(0, 1)}[fmt]()
        return bytes(enc.encode(raw))
    import etcpak
    # etcpak takes RGBA bytes (checked by round trip in tools_test/dds_roundtrip.py)
    data = lv.tobytes()
    if fmt == "bc1":
        return etcpak.compress_bc1(data, w, h)
    if fmt == "bc3":
        return etcpak.compress_bc3(data, w, h)
    if fmt == "bc4":
        return etcpak.compress_bc4(data, w, h)
    if fmt == "bc5":
        return etcpak.compress_bc5(data, w, h)
    if fmt == "bc7":
        p = etcpak.BC7CompressBlockParams()
        p.m_uber_level = bc7_uber
        if opaque:
            p.m_mode_mask = 0x02   # mode 1 only: exact 255 alpha
        return etcpak.compress_bc7(data, w, h, p)
    raise ValueError(fmt)


# --- header ---------------------------------------------------------------------------------

def header(fmt, w, h, mips, srgb, dx10, cube, has_alpha):
    flags = DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT
    if mips > 1:
        flags |= DDSD_MIPMAPCOUNT
    if fmt == "rgba8":
        flags |= DDSD_PITCH
        pitch = w * 4
    else:
        flags |= DDSD_LINEARSIZE
        pitch = max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * BLOCK_BYTES[fmt]
    caps = DDSCAPS_TEXTURE | (DDSCAPS_COMPLEX | DDSCAPS_MIPMAP if mips > 1 else 0) | (DDSCAPS_COMPLEX if cube else 0)
    caps2 = DDSCAPS2_CUBEMAP_ALLFACES if cube else 0
    hd = struct.pack("<4sI", b"DDS ", 124) + struct.pack("<6I", flags, h, w, pitch, 0, mips) + b"\0" * 44
    if dx10:
        pf = struct.pack("<II4sIIIII", 32, DDPF_FOURCC, b"DX10", 0, 0, 0, 0, 0)
    elif fmt == "rgba8":   # A8R8G8B8: bytes B, G, R, A
        pf = struct.pack("<II4sIIIII", 32, DDPF_RGB | DDPF_ALPHAPIXELS, b"\0\0\0\0", 32,
                         0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    else:
        pf = struct.pack("<II4sIIIII", 32, DDPF_FOURCC, FOURCC[fmt], 0, 0, 0, 0, 0)
    hd += pf + struct.pack("<5I", caps, caps2, 0, 0, 0)
    if dx10:
        dxgi = DXGI[(fmt, srgb)]
        hd += struct.pack("<5I", dxgi, D3D10_RESOURCE_DIMENSION_TEXTURE2D,
                          D3D11_RESOURCE_MISC_TEXTURECUBE if cube else 0, 1, 1 if has_alpha else 0)
    assert len(hd) == 128 + (20 if dx10 else 0)
    return hd


def load_rgba(path):
    """An image file, or a .npy array (h, w), (h, w, 3) or (h, w, 4) of uint8, as (h, w, 4) RGBA."""
    if str(path).lower().endswith(".npy"):
        a = np.load(path, allow_pickle=False)
        if a.dtype != np.uint8:
            raise ValueError(f"{path}: {a.dtype}, not uint8")
        if a.ndim == 2:
            a = np.repeat(a[..., None], 3, 2)
        if a.shape[2] == 3:
            a = np.concatenate([a, np.full(a.shape[:2] + (1,), 255, np.uint8)], 2)
        return np.ascontiguousarray(a)
    im = Image.open(path)
    im.load()
    return np.asarray(im.convert("RGBA"), dtype=np.uint8).copy()


def read_dds(path):
    """Decode a DDS this module writes (legacy DXT1/DXT5/ATI1/ATI2/A8R8G8B8 or DX10): (info dict, [faces][mips] of
    (h, w, 4) uint8 RGBA). Needs texture2ddecoder for the block formats."""
    data = Path(path).read_bytes()
    flags, h, w, pitch, depth, mips = struct.unpack_from("<6I", data, 8)
    fourcc = data[84:88]
    caps2 = struct.unpack_from("<I", data, 112)[0]
    off = 128
    if fourcc == b"DX10":
        dxgi = struct.unpack_from("<I", data, 128)[0]
        off = 148
        fmt = {71: "bc1", 72: "bc1", 77: "bc3", 78: "bc3", 80: "bc4", 83: "bc5", 98: "bc7", 99: "bc7", 28: "rgba8x",
               29: "rgba8x"}[dxgi]
    else:
        fmt = {b"DXT1": "bc1", b"DXT5": "bc3", b"ATI1": "bc4", b"ATI2": "bc5", b"\0\0\0\0": "rgba8"}[fourcc]
    faces = 6 if caps2 & 0x200 else 1
    out = []
    for _ in range(faces):
        lw, lh, levels = w, h, []
        for _ in range(max(1, mips)):
            if fmt.startswith("rgba8"):
                n = lw * lh * 4
                px = np.frombuffer(data, np.uint8, n, off).reshape(lh, lw, 4)
                px = px[..., [2, 1, 0, 3]] if fmt == "rgba8" else px
            else:
                import texture2ddecoder as t2d
                dec = {"bc1": t2d.decode_bc1, "bc3": t2d.decode_bc3, "bc4": t2d.decode_bc4, "bc5": t2d.decode_bc5,
                       "bc7": t2d.decode_bc7}[fmt]
                W4, H4 = (lw + 3) // 4 * 4, (lh + 3) // 4 * 4
                n = (W4 // 4) * (H4 // 4) * BLOCK_BYTES[fmt]
                bgra = np.frombuffer(dec(data[off:off + n], W4, H4), np.uint8).reshape(H4, W4, 4)[:lh, :lw]
                px = bgra[..., [2, 1, 0, 3]]
            off += n
            levels.append(np.ascontiguousarray(px))
            lw, lh = max(1, lw // 2), max(1, lh // 2)
        out.append(levels)
    if off != len(data):
        raise ValueError(f"{path}: {len(data) - off} bytes left over after the mips")
    return dict(w=w, h=h, mips=mips, format=fmt, cube=faces == 6), out


def run_batch(jobs):
    """jobs: [{"inputs": [...], "output": path, "format": ..., and any of build()'s keywords: mips, gamma_mips,
    normal, flip_green, cube, header_mode, encoder, bc7_uber}]. Each output written to a temporary name first."""
    keys = ("mips", "srgb", "gamma_mips", "normal", "flip_green", "header_mode", "encoder", "bc7_uber", "cube")
    for job in jobs:
        imgs = [load_rgba(p) for p in job["inputs"]]
        data = build(imgs, job["format"], **{k: job[k] for k in keys if k in job})
        out = Path(job["output"])
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_name(out.name + ".part")
        tmp.write_bytes(data)
        tmp.replace(out)
        print(f"{out}: {job['format']} {imgs[0].shape[1]}x{imgs[0].shape[0]}{' cube' if job.get('cube') else ''}, "
              f"{len(data)} bytes", flush=True)


def build(images, fmt, mips=0, srgb=False, gamma_mips=False, normal=False, flip_green=False,
          header_mode="auto", encoder="auto", bc7_uber=1, cube=False):
    """images: list of (h, w, 4) uint8 arrays (1, or 6 for a cube). Returns the DDS bytes."""
    if fmt == "bc4" and srgb or fmt == "bc5" and srgb:
        raise ValueError("BC4/BC5 have no sRGB variant")
    h, w = images[0].shape[:2]
    if any(im.shape != images[0].shape for im in images):
        raise ValueError("all faces must be the same size")
    if cube and (len(images) != 6 or h != w):
        raise ValueError("a cube map takes six square faces")
    if fmt != "rgba8" and (h % 4 or w % 4):
        raise ValueError(f"{w}x{h}: block formats need sides that are multiples of 4 (powers of two preferred)")
    dx10 = header_mode == "dx10" or fmt == "bc7" or srgb
    body = b""
    nm = None
    has_alpha = False
    for im in images:
        im = im.copy()
        if flip_green:
            im[..., 1] = 255 - im[..., 1]
        has_alpha |= bool((im[..., 3] < 255).any())
        levels = mip_chain(im, mips, linear_rgb=(srgb or gamma_mips) and not normal, normal=normal)
        nm = len(levels)
        for lv in levels:
            if fmt == "rgba8":
                body += lv.tobytes() if dx10 else lv[..., [2, 1, 0, 3]].tobytes()
            else:
                body += compress(lv, fmt, encoder, bc7_uber, opaque=bool((lv[..., 3] == 255).all()))
    return header(fmt, w, h, nm, srgb, dx10, cube, has_alpha) + body


DXGI_NAMES = {28: "R8G8B8A8_UNORM", 29: "R8G8B8A8_UNORM_SRGB", 71: "BC1_UNORM", 72: "BC1_UNORM_SRGB", 77: "BC3_UNORM",
              78: "BC3_UNORM_SRGB", 80: "BC4_UNORM", 83: "BC5_UNORM", 98: "BC7_UNORM", 99: "BC7_UNORM_SRGB"}


def info(path):
    """One line about a DDS file's header."""
    d = Path(path).read_bytes()[:148]
    flags, h, w, pitch, depth, mips = struct.unpack_from("<6I", d, 8)
    pff, fourcc, bits = struct.unpack_from("<I4sI", d, 80)
    caps, caps2 = struct.unpack_from("<2I", d, 108)
    fmt = fourcc.decode("latin1") if fourcc != b"\0\0\0\0" else f"RGB{bits}"
    if fourcc == b"DX10":
        g = struct.unpack_from("<I", d, 128)[0]
        fmt = "DX10 " + DXGI_NAMES.get(g, str(g))
    return f"{path}: {w}x{h} {fmt} mips {mips}{' cube' if caps2 & 0x200 else ''}"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "--info":
        for p in argv[1:]:
            print(info(p))
        return 0
    if len(argv) == 2 and argv[0] == "--batch":
        import json
        run_batch(json.loads(Path(argv[1]).read_text()))
        return 0
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", type=Path, help="input image(s) then the output .dds")
    ap.add_argument("--format", required=True, choices=["bc1", "bc3", "bc4", "bc5", "bc7", "rgba8"])
    ap.add_argument("--mips", type=int, default=0, help="mip levels: 0 = the full chain to 1x1 (default), 1 = none")
    ap.add_argument("--srgb", action="store_true", help="write the *_SRGB DXGI format (DX10) with linear-light mips")
    ap.add_argument("--gamma-mips", action="store_true", help="linear-light mip filtering, UNORM format (FO4 colour)")
    ap.add_argument("--normal", action="store_true", help="renormalise mips as tangent-space normals")
    ap.add_argument("--flip-green", action="store_true", help="invert G (OpenGL <-> DirectX normal maps)")
    ap.add_argument("--header", choices=["auto", "dx10"], default="auto")
    ap.add_argument("--encoder", choices=["auto", "etcpak", "quicktex"], default="auto")
    ap.add_argument("--bc7-uber", type=int, default=1, help="bc7enc uber level 0-4 (slower, better)")
    ap.add_argument("--cube", action="store_true", help="six inputs +X -X +Y -Y +Z -Z -> a cube map")
    a = ap.parse_args(argv)
    *ins, out = a.inputs
    imgs = [load_rgba(p) for p in ins]
    data = build(imgs, a.format, a.mips, a.srgb, a.gamma_mips, a.normal, a.flip_green, a.header, a.encoder,
                 a.bc7_uber, a.cube)
    out.write_bytes(data)
    print(f"{out}: {a.format}{' sRGB' if a.srgb else ''} {imgs[0].shape[1]}x{imgs[0].shape[0]}"
          f"{' cube' if a.cube else ''}, {len(data)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
