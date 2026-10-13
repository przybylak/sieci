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

The geometry: each material's meshes are merged, welded and split into connected pieces, each
piece is cut down with quadric edge collapse (fast_simplification) to its share of --tris by
surface area (so the tyres keep their shape and a bolt gets a few triangles), and the parts go
into three shapes: the metal (environment-mapped: chrome, silver, the body colour), the matte
(black metal, rubber, leather) and the glass (translucent). Three, not twelve, because the
F4SE plugin holds at most four skins and the game shows at most 65535 vertices per shape.
Colours, specular and gloss come from the material names (MATERIALS below); the body colour
is --body.

  python harley_meshes.py --pynifly <io_scene_nifly> --gltf <...>/scene.gltf \
      --vanilla <...>/meshes/setdressing/vehicles/motorcycle/motorcycle_clean.nif \
      --out <Data>/Meshes/CMB --textures <Data>/Textures/CMB \
      [--seat <Data>/Meshes/Actors/Character/Animations/MT/CMB_Rider] [--tris 60000] [--body 7a1118]
      [--sit 0.35] [--grip 20,-15,98] [--peg 19,6,27]

The rider sits --sit of the way along the seat from its front edge (0.35: snug behind the
tank, as on the real thing, which also keeps the long reach to the bars within arm's length).
--grip and --peg are the grip's centre and the peg's top on the bike's +X side in the model's
own frame (measured on this model; the other side mirrors them). The model is scaled to the
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
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_bike_meshes import _block_offsets, apply, mat_mul, read_seat, rigid_inverse  # noqa: E402

VANILLA_LENGTH = 196.0   # the vanilla motorcycle along Y (its bounds are y[-98, 98])
HIPS_Y_WORN = -5.0       # the middle of the buttocks zone riding_anims.py seats (worn y -14..4)
GROUND_FOOT_L = [-30.0, 6.0, 0.0]   # the left foot at a stop, as for the vanilla bike (this one is as wide)
MODEL_NAME = "Harley Davidson Iron 883 2015 by Nieve5677 (CC-BY-4.0)"
BIKE_BONE = "AnimObjectA"
PALETTE_W, PALETTE_H, BLOCK = 128, 8, 8   # 16 blocks of 8x8
CUBEMAP = "textures\\shared\\cubemaps\\mipblur_defaultoutside1.dds"

# name: (rgb, alpha, specular 0-255, gloss 0-255, env mask 0-255, shape)
MATERIALS = {
    "chrome":      ((176, 178, 184), 255, 255, 235, 255, "metal"),
    "silver":      ((150, 152, 158), 255, 210, 190, 190, "metal"),
    "tex2":        ((52, 52, 56), 255, 160, 170, 130, "metal"),       # the belt drive cover: dark metal
    "body":        (None, 255, 140, 215, 140, "metal"),               # --body
    "logo_decals": ((120, 108, 92), 255, 110, 150, 60, "metal"),      # the tank badges, no texture to show
    "black_m":     ((24, 24, 26), 255, 70, 95, 25, "matte"),          # engine, frame, forks: black metal
    "tex1":        ((28, 28, 30), 255, 75, 105, 30, "matte"),
    "material":    ((16, 16, 16), 255, 28, 35, 0, "matte"),           # "gum": tyres, grips, cables
    "leather":     ((34, 27, 22), 255, 45, 65, 0, "matte"),
    "glass":       ((215, 220, 226), 115, 255, 250, 220, "glass"),    # the headlight
    "o_glass":     ((232, 128, 24), 165, 240, 240, 160, "glass"),     # indicators
    "r_glass":     ((196, 24, 24), 165, 240, 240, 160, "glass"),      # the tail light
}
SHAPES = ("metal", "matte", "glass")

# BSLightingShaderProperty flags (nif.xml's SkyrimShaderPropertyFlags, as Fallout 4 still uses them)
SF1_SPECULAR, SF1_SKINNED, SF1_ENV_MAP, SF1_RECEIVE_SHADOWS, SF1_CAST_SHADOWS = 0x1, 0x2, 0x80, 0x100, 0x200
SF1_ZBUFFER_TEST = 0x80000000
SF2_ZBUFFER_WRITE, SF2_DOUBLE_SIDED, SF2_ENVMAP_LIGHT_FADE = 0x1, 0x10, 0x8000
SHADER_DEFAULT, SHADER_ENV_MAP = 0, 1
ALPHA_BLEND_FLAGS = 4845   # blend src alpha / inv src alpha, test greater


# --- glTF --------------------------------------------------------------------------------

def load_gltf(path: Path):
    """Each material's vertices and triangles, merged: {name: (V (n,3) float64, F (m,3) int64)}."""
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
            groups.setdefault(name, []).append((v, f))
    merged = {}
    for name, parts in groups.items():
        vs, fs, off = [], [], 0
        for v, f in parts:
            vs.append(v)
            fs.append(f + off)
            off += len(v)
        merged[name] = weld(np.vstack(vs), np.vstack(fs))
    return merged


def weld(v, f, tol=1e-3):
    """Merge vertices at the same place. The export keeps a vertex per face corner along
    hard edges, which leaves the simplifier a patchwork of islands whose borders it won't
    collapse (pieces came back ten times over budget)."""
    key = np.round(v / tol).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    f = inv.reshape(-1)[f] if inv.ndim > 1 else inv[f]
    keep = (f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])
    return v[first], f[keep]


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


def decimate(groups, total_target, speck_area=4.0, min_tris=8):
    """Cut the model down to about total_target triangles, each connected piece getting its
    share by surface area: so a tyre keeps its shape while a bolt gets a few triangles, instead
    of the thousands of small pieces of one material (tread blocks, bolts, cables) starving the
    big ones. Pieces of under speck_area (game units squared, so about a centimetre across) are
    dropped. Coordinates must be scaled to game units already."""
    import fast_simplification as fs
    pieces = []   # (material, verts, tris, area)
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
            fc = f[order[bounds[c]:bounds[c + 1]]]
            if piece_area[c] < speck_area:
                dropped += 1
                dropped_area += piece_area[c]
                continue
            used, inv = np.unique(fc, return_inverse=True)
            pieces.append((name, v[used], inv.reshape(-1, 3), float(piece_area[c])))
    total_area = sum(p[3] for p in pieces)
    counts = np.array([len(p[2]) for p in pieces])
    areas = np.array([p[3] for p in pieces])
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
    out = {}
    for (name, v, f, _), b in zip(pieces, budget):
        # A closed tube (the cables) often stops well short of the target in one call and
        # gives a little more each call after; a few passes, while they still pay.
        for _ in range(4):
            if b >= len(f):
                break
            vo, fo = fs.simplify(v, f, target_reduction=1.0 - b / len(f), agg=7)
            vo, fo = np.asarray(vo, dtype=np.float64), np.asarray(fo, dtype=np.int64)
            gain = len(fo) < 0.95 * len(f)
            v, f = vo, fo
            if not gain:
                break
        vs, fs_, n = out.get(name, ([], [], 0))
        out[name] = (vs + [v], fs_ + [f + n], n + len(v))
    result = {name: (np.vstack(vs), np.vstack(fs_)) for name, (vs, fs_, _) in out.items()}
    got = sum(len(f) for _, f in result.values())
    print(f"  {len(pieces)} pieces kept, {dropped} specks dropped ({dropped_area:.0f} units² of {total_area:.0f}); "
          f"budget {int(budget.sum())} triangles, got {got}")
    for name, (v, f) in groups.items():
        if name in result:
            print(f"  {name:12s} {len(f):8d} -> {len(result[name][1]):6d} tris")
    return result


def rows(a):
    """An array's rows as tuples (what PyNifly's ctypes buffers take)."""
    return [tuple(r) for r in a.tolist()]


def vertex_normals(v, f):
    n = np.zeros_like(v)
    tri = v[f]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])   # area-weighted
    for k in range(3):
        np.add.at(n, f[:, k], fn)
    length = np.linalg.norm(n, axis=1, keepdims=True)
    return n / np.where(length > 1e-12, length, 1.0)


# --- textures ----------------------------------------------------------------------------

def write_dds(path: Path, rgba: np.ndarray):
    """An uncompressed RGBA8 DDS with one mip level (the palette must never blend)."""
    h, w = rgba.shape[:2]
    header = struct.pack("<4sI", b"DDS ", 124)
    header += struct.pack("<IIIII", 0x1 | 0x2 | 0x4 | 0x8 | 0x1000, h, w, w * 4, 0)   # flags: caps, height, width, pitch, pixelformat
    header += struct.pack("<I", 1) + b"\0" * 44                                    # mip count, reserved
    header += struct.pack("<II4sIIIII", 32, 0x41, b"\0\0\0\0", 32, 0xFF, 0xFF00, 0xFF0000, 0xFF000000)   # RGBA
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

def shader_setup(shape, base_props, kind, skinned, textures):
    """Our own textures and settings on the shape (no materials file, so the nif's count)."""
    props = base_props.copy()
    props.nameID = props.controllerID = -1
    sf1 = SF1_SPECULAR | SF1_RECEIVE_SHADOWS | SF1_CAST_SHADOWS | SF1_ZBUFFER_TEST
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
    if kind == "glass":
        sf2 |= SF2_DOUBLE_SIDED
    props.Shader_Flags_1 = sf1
    props.Shader_Flags_2 = sf2
    props.Glossiness = {"metal": 90.0, "matte": 30.0, "glass": 110.0}[kind]
    props.Spec_Str = 1.0
    props.Spec_Color[0] = props.Spec_Color[1] = props.Spec_Color[2] = 1.0
    props.Alpha = 1.0
    props.Emissive_Mult = 1.0
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


def add_shape(nif, name, verts, tris, uvs, normals, base_props, use_type, kind, skinned, bone=None, bind=None, TransformBuf=None):
    props = base_props.copy()
    props.nameID = props.conrollerID = props.collisionID = -1
    props.skinInstanceID = props.shaderPropertyID = props.alphaPropertyID = -1
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
    shader_setup(new, base_props.shader_props, kind, skinned, texture_paths(kind))
    return new


def fix_all_bone_bounds(path: Path, verts, skin_to_bone=None):
    """A culling sphere round every vertex of every shape, into each BSSkin::BoneData (the
    game culls skinned meshes with it; nifly's own is too small for a mesh this long)."""
    lo = verts.min(axis=0)
    hi = verts.max(axis=0)
    centre = (lo + hi) / 2
    radius = float(np.linalg.norm(verts - centre, axis=1).max()) + 1.0
    c = list(apply(skin_to_bone, centre)) if skin_to_bone else list(centre)
    data = bytearray(path.read_bytes())
    count = 0
    for off, name in _block_offsets(data):
        if name == "BSSkin::BoneData":
            if struct.unpack_from("<I", data, off)[0] != 1:
                raise ValueError("expected one bone in BSSkin::BoneData")
            struct.pack_into("<4f", data, off + 4, *c, radius)
            count += 1
    path.write_bytes(bytes(data))
    return count, radius


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
    ap.add_argument("--tris", type=int, default=60000,
                    help="the triangle budget (the result runs about a third over it: the thin closed "
                         "tubes of the cables won't go down to their share)")
    ap.add_argument("--body", default="7a1118", help="the tank and fenders' colour, hex rgb")
    ap.add_argument("--sit", type=float, default=0.35,
                    help="the hips go this far along the seat from its front edge (0..1)")
    ap.add_argument("--seat-at", type=float, help="instead of --sit: the parked model's y that goes under the hips")
    ap.add_argument("--grip", default="20,-15,98", help="the grip's centre on the +X side, parked model x,y,z")
    ap.add_argument("--peg", default="19,6,27", help="the foot peg's top on the +X side, parked model x,y,z")
    args = ap.parse_args()
    grip = np.array([float(t) for t in args.grip.split(",")])
    peg = np.array([float(t) for t in args.peg.split(",")])

    sys.path.insert(0, str(args.pynifly))
    from pyn.pynifly import NifFile, TransformBuf  # noqa: E402

    body = tuple(int(args.body[i:i + 2], 16) for i in (0, 2, 4))
    print(f"loading {args.gltf}")
    groups = load_gltf(args.gltf)
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
    print(f"decimating to about {args.tris} triangles:")
    groups = decimate(groups, args.tris)
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

    fit = dict(model=MODEL_NAME, seat_top_z=round(seat_top_z, 2),
               grip_r=to_worn([-abs(grip[0]), grip[1], grip[2]]), grip_l=to_worn([abs(grip[0]), grip[1], grip[2]]),
               peg_r=to_worn([-abs(peg[0]), peg[1], peg[2]]), peg_l=to_worn([abs(peg[0]), peg[1], peg[2]]),
               ground_foot_l=GROUND_FOOT_L, seat_at=round(seat_at, 2), hips_y=round(hips_y, 2))
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

    order = [m for m in MATERIALS if m in groups]
    uv_of = write_palette(args.textures, order, body)
    print(f"wrote the palette textures to {args.textures}")

    # The three shapes: vertices, triangles, UVs, normals (the parked frame).
    shapes = {}
    for kind in SHAPES:
        vs, fs, us, off = [], [], [], 0
        for name in order:
            if MATERIALS[name][5] != kind:
                continue
            v, f = groups[name]
            if flip:
                f = f[:, [0, 2, 1]]
            vs.append(v)
            fs.append(f + off)
            us.append(np.tile(np.array(uv_of[name]), (len(v), 1)))
            off += len(v)
        v = np.vstack(vs)
        f = np.vstack(fs)
        if len(v) > 65535:
            print(f"the {kind} shape has {len(v)} vertices, over the 65535 a shape may have: lower --tris", file=sys.stderr)
            return 1
        shapes[kind] = (v, f, np.vstack(us), vertex_normals(v, f))
        print(f"  {kind}: {len(v)} vertices, {len(f)} triangles")

    base = Base(vshape)

    # Parked: the vanilla nif, its shape hidden, ours added.
    parked = args.out / "CMB_BikeParked.nif"
    parked.write_bytes(args.vanilla.read_bytes())
    nif = NifFile(str(parked))
    old = nif.shapes[0]
    old.flags = old.flags | 1   # hidden
    for kind in SHAPES:
        v, f, u, n = shapes[kind]
        add_shape(nif, f"CMB_Harley_{kind}", rows(v), rows(f), rows(u), rows(n), base, base.use_type, kind, False)
    nif.save()
    check = NifFile(str(parked))
    names = [s.name for s in check.shapes]
    hidden = [s.name for s in check.shapes if s.flags & 1]
    blocks = [name for _, name in _block_offsets(parked.read_bytes())]
    print(f"wrote {parked}: shapes {names}, hidden {hidden}, "
          f"collision {'kept' if any(b.startswith('bhk') for b in blocks) else 'NOT FOUND'} ({len(blocks)} blocks)")

    # Worn: turned round to face +Y like a character, the seat over the origin, on one bone.
    def worn(path: Path, bone, bind):
        out = NifFile()
        out.initialize("FO4", str(path), "NiNode", path.stem)
        allverts = []
        for kind in SHAPES:
            v, f, u, n = shapes[kind]
            tv = np.column_stack([-v[:, 0], -v[:, 1] + seat_at, v[:, 2]])
            tn = np.column_stack([-n[:, 0], -n[:, 1], n[:, 2]])
            allverts.append(tv)
            add_shape(out, f"{path.stem}_{kind}", rows(tv), rows(f), rows(u), rows(tn), base, base.use_type, kind,
                      True, bone, bind, TransformBuf)
        out.save()
        allverts = np.vstack(allverts)
        count, radius = fix_all_bone_bounds(path, allverts, rigid_inverse(bind) if bind else None)
        check = NifFile(str(path))
        lo, hi = allverts.min(axis=0), allverts.max(axis=0)
        print(f"wrote {path}: {len(check.shapes)} shapes on {bone}, {count} bone-data blocks, culling radius {radius:.0f}")
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
            print(f"  {s.name}: {len(s.verts)} verts, bones {list(s.bone_weights)}, alpha {s.has_alpha_property}, "
                  f"textures {dict(s.shader.textures) if s.shader else {}}")

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
