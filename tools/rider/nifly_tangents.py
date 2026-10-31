#!/usr/bin/env python3
"""Fallout 4 normal-map tangent space, as the game will see it on our nifs (numpy only).

The bike's nifs are written by PyNifly, whose nifly library computes every vertex's tangent frame itself when a
shape is made from positions, normals and UVs (BSTriShape::CalcTangentSpace, nifly src/Geometry.cpp): per triangle
the directions of dP/du and dP/dv (each normalised, so every triangle counts the same), summed per vertex,
Gram-Schmidt against the vertex normal (which is first stored as bytes), and stored as bytes again. nifly calls the
dP/dv one the "tangent" and the dP/du one the "bitangent" (Bethesda's own naming). A tangent-space normal map then
reads: R along dP/du, G along dP/dv with v running DOWN the image (the nif's UVs; DirectX's green), B along the
normal. Blender bakes tangent space with MikkTSpace and v up, which is neither, so the bike's textures are baked in
object space and re-encoded here with nifly's own frames (decision 12 of the t48 plan):

    frames = nifly_frames(pos, tris, normals, uvs)       # per vertex of the shape as written (after the UV seams)
    n_ts = encode(n_obj, du, dv, n)                       # per texel, with the frames interpolated to it

Also the I3 seam rule (one vertex per exported vertex and UV quantised to 1/32768: harley_meshes' seam_split) and a
reader for the BSTriShape vertex records of a written nif (PyNifly has no tangent getter), used by

    python3 -I nifly_tangents.py validate --pynifly <io_scene_nifly> --stage-dir S [--labels a,b] [--out report.txt]

which writes each label's shape with PyNifly (full precision, as the parked nif, and half precision in the worn
frame, as the worn nifs), reads the frames back from the file's bytes and reports the angle between them and this
module's (RMS and max), and the error a normal encoded with these frames shows when decoded with the read-back ones.
"""
import argparse
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np

UV_Q = 32768.0   # interface I3: UVs quantised to 1/32768


# --- the seam rule (I3) ---------------------------------------------------------------------------------------------

def quantise_uv(uv):
    return np.round(np.asarray(uv, dtype=np.float64) * UV_Q) / UV_Q


def seam_split(tri, uv):
    """tri (T,3) exported vertex indices, uv (T,3,2) per corner (nif convention). Returns (src (V',) exported vertex of
    each split vertex, uv (V',2), corner_to_vertex (T,3)) in the order harley_meshes' seam_split makes them (np.unique
    of (vertex, qu, qv)), so the index of a split vertex here is its index in the nif."""
    q = np.round(np.asarray(uv, dtype=np.float64).reshape(-1, 2) * UV_Q).astype(np.int64)
    key = np.column_stack([np.asarray(tri).reshape(-1).astype(np.int64), q])
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    return uniq[:, 0], uniq[:, 1:] / UV_Q, inv.reshape(-1, 3)


# --- nifly's frames -------------------------------------------------------------------------------------------------

def to_bytes(v):
    """nifly's unit-vector byte: static_cast<uint8_t>(std::round(((x + 1) / 2) * 255)) (float32 maths)."""
    x = ((np.asarray(v, dtype=np.float32) + np.float32(1)) / np.float32(2)) * np.float32(255)
    return np.floor(x + np.float32(0.5)).astype(np.int64).astype(np.uint8)   # all >= 0: floor(x+.5) == std::round


def from_bytes(b):
    return (np.asarray(b, dtype=np.float32) / np.float32(255)) * np.float32(2) - np.float32(1)


def _normalise(v):
    d = np.sqrt((v * v).sum(-1, dtype=np.float32)).astype(np.float32)
    d = np.where(d == 0, np.float32(1), d)
    return (v / d[..., None]).astype(np.float32)


def nifly_frames(pos, tri, nrm, uv):
    """Per vertex (the shape's own, after the seams): (du, dv, n) as nifly stores them, decoded to floats: du = the
    "bitangent" (dP/du), dv = the "tangent" (dP/dv, v down), n = the normal as bytes. Also returns the float
    vectors before the bytes (du_f, dv_f) and cond, how much of the UV directions is left after the Gram-Schmidt
    (0..1; under ~0.25 the frame is float noise, in nifly as here: the UVs run along the normal there)."""
    P = np.asarray(pos, dtype=np.float32)
    W = np.asarray(uv, dtype=np.float32)
    tri = np.asarray(tri, dtype=np.int64)
    n = from_bytes(to_bytes(nrm))                       # UpdateRawNormals: the normal comes back from its bytes
    i1, i2, i3 = tri[:, 0], tri[:, 1], tri[:, 2]
    e1, e2 = P[i2] - P[i1], P[i3] - P[i1]
    s1, s2 = W[i2, 0] - W[i1, 0], W[i3, 0] - W[i1, 0]
    t1, t2 = W[i2, 1] - W[i1, 1], W[i3, 1] - W[i1, 1]
    r = s1 * t2 - s2 * t1
    r = np.where(r >= 0, np.float32(1), np.float32(-1))[:, None]
    sdir = _normalise((t2[:, None] * e1 - t1[:, None] * e2) * r)   # dP/du
    tdir = _normalise((s1[:, None] * e2 - s2[:, None] * e1) * r)   # dP/dv
    V = len(P)
    tan1 = np.zeros((V, 3), np.float32)
    tan2 = np.zeros((V, 3), np.float32)
    for k in (i1, i2, i3):
        np.add.at(tan1, k, tdir)
        np.add.at(tan2, k, sdir)
    zero = ~tan1.any(1) | ~tan2.any(1)
    T = _normalise(tan1)
    T = T - n * (n * T).sum(1, keepdims=True)
    cond = np.linalg.norm(T, axis=1)                    # what is left of dP/dv off the normal (1 = all of it)
    T = _normalise(T)
    B = _normalise(tan2)
    B = B - n * (n * B).sum(1, keepdims=True)
    B = B - T * (T * B).sum(1, keepdims=True)
    cond = np.minimum(cond, np.linalg.norm(B, axis=1))  # and of dP/du off the normal and dP/dv: near 0 = float noise
    B = _normalise(B)
    Tz = np.stack([n[:, 1], n[:, 2], n[:, 0]], 1)
    T = np.where(zero[:, None], Tz, T)
    B = np.where(zero[:, None], np.cross(n, Tz), B)
    dv = from_bytes(to_bytes(T))
    du = np.concatenate([B[:, :1], from_bytes(to_bytes(B[:, 1:]))], 1)   # bitangent X is stored as a float
    cond = np.where(zero, 0.0, cond)
    return du, dv, n, B, T, cond


# --- re-encoding ----------------------------------------------------------------------------------------------------

def encode(n_obj, du, dv, n, min_z=0.05):
    """Object-space unit normals (N,3) -> tangent-space (N,3) for frames (N,3) each (normalised here): the exact
    solve M x = n_obj with M = [du dv n], normalised, z kept >= min_z (BC5 rebuilds z = sqrt(1 - x^2 - y^2))."""
    du, dv, n = (_normalise(np.asarray(a, dtype=np.float32)).astype(np.float64) for a in (du, dv, n))
    M = np.stack([du, dv, n], axis=2)                    # columns
    det = np.linalg.det(M)
    bad = np.abs(det) < 1e-6
    M[bad] = np.eye(3)
    x = np.linalg.solve(M, np.asarray(n_obj, dtype=np.float64)[..., None])[..., 0]
    x[bad] = (0.0, 0.0, 1.0)
    x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-12)
    low = x[:, 2] < min_z
    if low.any():
        xy = x[low, :2]
        xy *= (math.sqrt(1 - min_z ** 2) / np.maximum(np.linalg.norm(xy, axis=1, keepdims=True), 1e-12))
        x[low, :2] = xy
        x[low, 2] = min_z
    return x


def decode(n_ts, du, dv, n):
    """What the shader does: normalize(du x + dv y + n z) (frames normalised)."""
    du, dv, n = (_normalise(np.asarray(a, dtype=np.float32)).astype(np.float64) for a in (du, dv, n))
    v = du * n_ts[:, :1] + dv * n_ts[:, 1:2] + n * n_ts[:, 2:3]
    return v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-12)


# --- a written nif's vertex records ---------------------------------------------------------------------------------

TRISHAPES = ("BSTriShape", "BSSubIndexTriShape", "BSMeshLODTriShape", "BSDynamicTriShape")


def nif_blocks(data: bytes):
    """[(offset, size, type name)] of a Fallout 4 (20.2.0.7, bsver 130) nif's blocks."""
    i = data.index(b"\n") + 1 + 9
    nblocks = struct.unpack_from("<I", data, i)[0]
    i += 8
    for _ in range(4):
        i += 1 + data[i]
    ntypes = struct.unpack_from("<H", data, i)[0]
    i += 2
    types = []
    for _ in range(ntypes):
        n = struct.unpack_from("<I", data, i)[0]
        types.append(data[i + 4:i + 4 + n].decode())
        i += 4 + n
    type_idx = struct.unpack_from(f"<{nblocks}H", data, i)
    i += 2 * nblocks
    sizes = struct.unpack_from(f"<{nblocks}I", data, i)
    i += 4 * nblocks
    nstrings = struct.unpack_from("<I", data, i)[0]
    i += 8
    for _ in range(nstrings):
        i += 4 + struct.unpack_from("<I", data, i)[0]
    i += 4 + 4 * struct.unpack_from("<I", data, i)[0]
    out = []
    for t, size in zip(type_idx, sizes):
        out.append((i, size, types[t & 0x7FFF]))
        i += size
    return out


def read_vertices(path):
    """Each BSTriShape's vertex records: [dict(pos, uv, normal, du, dv, tris, full)] in block order; du = the stored
    bitangent (X float, Y and Z bytes), dv = the stored tangent, all decoded as nifly decodes them."""
    data = Path(path).read_bytes()
    out = []
    for off, size, kind in nif_blocks(data):
        if kind not in TRISHAPES:
            continue
        i = off + 4                                       # name
        i += 4 + 4 * struct.unpack_from("<I", data, i)[0]  # extra data list
        i += 4 + 4 + 13 * 4 + 4                           # controller, flags, transform, collision
        i += 16 + 12                                      # bounding sphere; skin, shader, alpha refs
        desc = struct.unpack_from("<Q", data, i)[0]
        i += 8
        ntris, nverts, dsize = struct.unpack_from("<IHI", data, i)
        i += 10
        flags = desc >> 44
        full = bool(flags & (1 << 10))
        vsize = (desc & 0xF) * 4
        # nibble 0 the record's size / 4, then one nibble per attribute's offset / 4: position, UV, UV2, normal, tangent...
        o_uv, o_n, o_t = ((desc >> 8) & 0xF) * 4, ((desc >> 16) & 0xF) * 4, ((desc >> 20) & 0xF) * 4
        if not (flags & (1 << 4)) or not (flags & (1 << 3)):
            raise ValueError(f"{path}: a shape without normals or tangents")
        raw = np.frombuffer(data, np.uint8, nverts * vsize, i).reshape(nverts, vsize)
        if full:
            p4 = raw[:, :16].copy().view(np.float32)
        else:
            p4 = raw[:, :8].copy().view(np.float16).astype(np.float32)
        uv = raw[:, o_uv:o_uv + 4].copy().view(np.float16).astype(np.float32)
        nb = raw[:, o_n:o_n + 4]
        tb = raw[:, o_t:o_t + 4]
        tris = np.frombuffer(data, np.uint16, ntris * 3, i + nverts * vsize).reshape(ntris, 3)
        out.append(dict(pos=p4[:, :3], uv=uv, normal=from_bytes(nb[:, :3]), dv=from_bytes(tb[:, :3]),
                        du=np.column_stack([p4[:, 3], from_bytes(nb[:, 3]), from_bytes(tb[:, 3])]),
                        tris=tris.astype(np.int64), full=full))
    return out


# --- validation -----------------------------------------------------------------------------------------------------

def angles(a, b):
    a = a / np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-12)
    b = b / np.maximum(np.linalg.norm(b, axis=1, keepdims=True), 1e-12)
    return np.degrees(np.arccos(np.clip((a * b).sum(1), -1, 1)))


def validate(args):
    sys.path.insert(0, str(args.pynifly))
    from pyn import pynifly as P   # noqa: E402
    from pyn.nifdefs import NiShapeBuf, PynBufferTypes   # noqa: E402
    stage = args.stage_dir
    man = json.loads((stage / "manifest.json").read_text())
    seat = float(man["seat_at"])
    labels = args.labels.split(",") if args.labels else list(man["labels"])
    args.work.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(12345)
    lines = ["label frame verts | du vs read-back rms/max deg | dv rms/max | normal rms | encode->decode rms/max deg "
             "(30 deg test normals) | the same at well-conditioned vertices | encode->decode with the frames before "
             "bytes; (n) after the vertex count = ill-conditioned vertices (cond < 0.25: under a quarter of a UV "
             "direction left off the normal, where the UVs run along it, e.g. a planar projection over a dome's "
             "wall): nifly's frame there is float noise too, and only a flat normal is safe (the art labels' maps "
             "are flat there)"]
    tot = {k: [] for k in ("du", "dv", "rt", "rt_w", "rt_f")}
    for label in labels:
        uvf = stage / "uv" / f"{label}.npz"
        with np.load(stage / "shapes" / f"{label}.npz") as z:
            pos, nrm, tri = z["pos"], z["nrm"], z["tri"]
            fixed = z["uv_fixed"] if "uv_fixed" in z.files else None
        if uvf.exists():
            with np.load(uvf) as z:
                uvc = z["uv"]
        elif fixed is not None:
            uvc = fixed
        else:
            continue
        src, uv, c2v = seam_split(tri, uvc)
        for frame in ("parked", "worn"):
            v = pos[src].astype(np.float64)
            n = nrm[src].astype(np.float64)
            if frame == "worn":
                v = np.column_stack([-v[:, 0], seat - v[:, 1], v[:, 2]])
                n = np.column_stack([-n[:, 0], -n[:, 1], n[:, 2]])
            n = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
            du, dv, nb, du_f, dv_f, cond = nifly_frames(v, c2v, n, uv)
            nif = P.NifFile()
            path = args.work / f"{label}_{frame}.nif"
            nif.initialize("FO4", str(path), "NiNode", "tangent_check")
            props = NiShapeBuf()
            props.bufType = PynBufferTypes.BSTriShapeBufType
            props.hasFullPrecision = 1 if frame == "parked" else 0
            tl = lambda a: [tuple(r) for r in a.tolist()]   # noqa: E731
            nif.createShapeFromData(label, tl(v), tl(c2v), tl(uv), tl(n), props=props)
            nif.save()
            back = read_vertices(path)[0]
            if back["tris"].shape != c2v.shape or not (back["tris"] == c2v).all():
                raise ValueError(f"{path}: triangles came back different")
            if np.abs(back["uv"] - uv).max() > 1e-3 or np.abs(back["pos"] - v).max() > (1e-3 if frame == "parked" else 0.07):
                raise ValueError(f"{path}: vertices came back in another order")
            a_du, a_dv, a_n = angles(du, back["du"]), angles(dv, back["dv"]), angles(nb, back["normal"])
            # a test normal 30 degrees off each vertex normal, in a random direction round it
            tdir = rng.normal(size=n.shape)
            tdir -= n * (tdir * n).sum(1, keepdims=True)
            tdir /= np.maximum(np.linalg.norm(tdir, axis=1, keepdims=True), 1e-12)
            test = n * math.cos(math.radians(30)) + tdir * math.sin(math.radians(30))
            enc = encode(test, du, dv, nb)
            rt = angles(decode(enc, back["du"], back["dv"], back["normal"]), test)
            enc_f = encode(test, du_f, dv_f, nb)
            rt_f = angles(decode(enc_f, back["du"], back["dv"], back["normal"]), test)
            well = cond >= 0.25
            rt_w = rt[well] if well.any() else np.zeros(1)
            r = lambda a: f"{math.sqrt((a ** 2).mean()):.3f}/{a.max():.2f}"   # noqa: E731
            lines.append(f"{label} {frame} {len(v)} ({int((~well).sum())}) | {r(a_du)} | {r(a_dv)} | {r(a_n)} | "
                         f"{r(rt)} | {r(rt_w)} | {r(rt_f)}")
            for k, a in (("du", a_du), ("dv", a_dv), ("rt", rt), ("rt_w", rt_w), ("rt_f", rt_f)):
                tot[k].append(a)
            print(lines[-1], flush=True)
    allr = {k: np.concatenate(v) if v else np.zeros(1) for k, v in tot.items()}
    rms = {k: math.sqrt((a ** 2).mean()) for k, a in allr.items()}
    lines.append("ALL | du rms {:.3f} max {:.2f} | dv rms {:.3f} max {:.2f} | encode->decode rms {:.3f} max {:.2f} "
                 "| well-conditioned rms {:.3f} max {:.2f} | with float frames rms {:.3f} max {:.2f} | vertices {}".format(
                     rms["du"], allr["du"].max(), rms["dv"], allr["dv"].max(), rms["rt"], allr["rt"].max(),
                     rms["rt_w"], allr["rt_w"].max(), rms["rt_f"], allr["rt_f"].max(), len(allr["du"])))
    print(lines[-1])
    ok = rms["rt_w"] < 2.0
    lines.append(f"decision 12 (< 2 deg RMS at the well-conditioned vertices): {'PASS' if ok else 'FAIL'}")
    if args.out:
        args.out.write_text("\n".join(lines) + "\n")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="write each label with PyNifly, read the frames back, compare")
    v.add_argument("--pynifly", type=Path, required=True)
    v.add_argument("--stage-dir", type=Path, required=True)
    v.add_argument("--labels", default="")
    v.add_argument("--work", type=Path, default=None, help="where the test nifs go (default: <stage>/tangent_check)")
    v.add_argument("--out", type=Path, default=None)
    a = ap.parse_args(argv)
    if a.cmd == "validate":
        a.work = a.work or a.stage_dir / "tangent_check"
        return validate(a)
    return 2


if __name__ == "__main__":
    sys.exit(main())
