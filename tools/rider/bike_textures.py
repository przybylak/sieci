#!/usr/bin/env python3
"""The bike's textures and materials files: the textures stage of tools/rider/build_bike.sh (the 2026-10-31a build).

The model came with no textures, so every surface is made here from the model's own geometry: each shape gets its
own UV atlas (made after the decimation, on the shape as the nifs will carry it), maps baked from the full
1.3-million-triangle model (normals, ambient occlusion) and from the shape itself (position, normal and tangent
frame per texel), and procedural surfaces authored from those (bike_materials.json: paint under a clear coat,
chrome, a wrinkle-black engine with machined fin edges, satin powder coat, leather grain, rubber, lenses; the tank's
cream coachline since the 2026-11-01a build two offsets of one traced curve, coachline_v2). The fixed-UV shapes (dial,
needle, badge, tail and brake shells, and since the 2026-11-01a build the brake discs, both on one texture set:
"textures_of") use the mod's own art (bike_art.py) as it comes.

    <blender python> -I bike_textures.py --stage-dir S --gltf scene.gltf --out <Data> \\
        --dds-python <python with numpy, pillow, quicktex, etcpak> [--materials bike_materials.json] [--art S/art] \\
        [--only label,label] [--quick] [--force]

Inputs: S/manifest.json + S/shapes/<label>.npz (the stage's shapes, harley_meshes.py --stage export), the glTF
(untrusted data: only its geometry is read, by Blender's importer), S/art (bike_art.py). Outputs:
  S/uv/<label>.npz   uv (T,3,2) float32 per triangle corner, nif convention (v down), on the 1/32768 grid (not
                     pre-rounded to the nifs' half floats: nifly makes the tangent frames from the UVs it is given)
  S/uv/<label>.json  {"verts_after_seams", "mat", "coverage", ...}: corners share a vertex iff the same exported vertex
                     and the same quantised UV (harley_meshes' seam_split counts the same and refuses a mismatch)
  <Data>/Textures/CMB/Bike/<mat>_d.dds (BC1, BC3 with alpha), _n.dds (BC5, DirectX green, re-encoded into nifly's own
                     tangent frames: nifly_tangents.py), _s.dds (BC5: R specular, G smoothness), _g.dds (BC1, glow maps),
                     mirror_cube_e.dds (+ mirror_cube_zup_e.dds, the same sky with +Z up)
  <Data>/Materials/CMB/Bike/<mat>.bgsm (the parked bike: shadows on, nothing lit; none for a material the parked nif
                     leaves out, the lit overlays) and <mat>_worn.bgsm (the riding bike: its shadows as
                     bike_materials.json says, emissive on)
  S/tex_cache/<label>/  per-label cache (uv, bakes, authored maps), keyed on hashes of everything that goes in: a rerun
                     redoes only what changed; --only does part of a run (each call well under 10 minutes)
  S/tex_report.json  per label: vertices after the seams, UV coverage, the bake's misses, timings, brand-relief check

Three more modes, run after the textures:
    <dds python> -I bike_textures.py --stage-dir S --out <Data> --sheet atlases.png        # decode every DDS, contact sheet
    <blender python> -I bike_textures.py --stage-dir S --out <Data> --preview p.png        # Cycles look of the textured bike
    <python> -I bike_textures.py --stage-dir S --out <folder> --mirror-cube Shared\\Cubemaps\\MetalBrushed02Cube_e.dds
        # only the mirrors' six material files, naming a game cube by its path (the optional MO2 folder "game mirror
        # cube (A-B)"; no game file is copied)

Deterministic: Blender's UV operators and Cycles with a fixed seed, numpy noise from integer hashes, the DDS encoders.
Brand guard: no source textures exist and the emblems are the mod's own art (bike_art.py); the bake can still
carry embossed relief from the model's covers (air cleaner, derby and timer covers), so the high-detail normals of
those glTF meshes are low-passed (features under ~1.2 units flattened) and the relief removed is reported.
"""
import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nifly_tangents as NT  # noqa: E402

VERSION = 1
GLTF_MATERIALS = {"logo_decals": "logo", "material": "gum"}   # glTF material name -> the piece material (the manifest's) if renamed
CUBES = {"CH": "Shared\\Cubemaps\\MetalChrome01Cube_e.dds", "DI": "Shared\\Cubemaps\\mipblur_DefaultOutside1_dielectric.dds",
         "GL": "Shared\\Cubemaps\\shinyglass_e.dds", "MR": "CMB\\Bike\\mirror_cube_e.dds"}   # as harley_meshes.CUBES
OVERLAYS = ("rear_tail", "rear_brake", "front_dialglow", "front_needle", "static_badge")   # never occluders
MIRROR_VARIANTS = ("front_mirrorStock", "front_mirrorUnderEgg", "front_mirrorUnderD")
BAKE_DEFAULTS = dict(exclude_meshes=[0, 9, 10, 11, 12, 62, 63], cage=0.3, ray=0.9, ao_distance=10.0, ao_samples=48,
                     angle=66.0, angle_retry=80.0, margin_px=2, dilate_px=8, relief_meshes=[40, 41], relief_radius=0.6,
                     near_cell=1.0, near_fraction=0.3)


def log(*a):
    print(*a, flush=True)


def sha(*parts):
    h = hashlib.sha256()
    for p in parts:
        if isinstance(p, (bytes, bytearray)):
            h.update(p)
        elif isinstance(p, Path):
            h.update(p.read_bytes())
        else:
            h.update(json.dumps(p, sort_keys=True, default=str).encode())
        h.update(b"\0")
    return h.hexdigest()[:24]


def hexrgb(s):
    s = s.lstrip("#")
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], np.float64) / 255.0


def srgb_to_lin(c):
    c = np.asarray(c, dtype=np.float64)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# --- noise (deterministic: integer hashes) ---------------------------------------------------------------------------

_M = np.uint64(0x9E3779B97F4A7C15)


def _hash(ix, iy, iz, seed):
    with np.errstate(over="ignore"):
        h = (ix.astype(np.uint64) * np.uint64(0x8DA6B343) ^ iy.astype(np.uint64) * np.uint64(0xD8163841)
             ^ iz.astype(np.uint64) * np.uint64(0xCB1AB31F) ^ np.uint64(seed) * _M)
        h ^= h >> np.uint64(29)
        h *= np.uint64(0xBF58476D1CE4E5B9)
        h ^= h >> np.uint64(32)
        h *= np.uint64(0x94D049BB133111EB)
        h ^= h >> np.uint64(31)
    return (h >> np.uint64(40)).astype(np.float64) / float(1 << 24)


def vnoise(p, seed=0):
    """3D value noise in [0, 1) at points p (N,3) (lattice spacing 1), smooth (C1)."""
    i = np.floor(p)
    f = p - i
    i = i.astype(np.int64)
    u = f * f * (3 - 2 * f)
    out = 0.0
    for dx in (0, 1):
        wx = u[:, 0] if dx else 1 - u[:, 0]
        for dy in (0, 1):
            wy = u[:, 1] if dy else 1 - u[:, 1]
            for dz in (0, 1):
                wz = u[:, 2] if dz else 1 - u[:, 2]
                out = out + wx * wy * wz * _hash(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz, seed)
    return out


def fbm(p, octaves=3, seed=0):
    out, amp, tot = 0.0, 1.0, 0.0
    for k in range(octaves):
        out = out + amp * vnoise(p * (2.0 ** k), seed + 17 * k)
        tot += amp
        amp *= 0.5
    return out / tot


def worley(p, seed=0):
    """F1 and F2 distances to hashed feature points (one per unit cell), p (N,3)."""
    i = np.floor(p).astype(np.int64)
    f1 = np.full(len(p), 9.0)
    f2 = np.full(len(p), 9.0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                cx, cy, cz = i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz
                fp = np.stack([cx + _hash(cx, cy, cz, seed), cy + _hash(cx, cy, cz, seed + 1),
                               cz + _hash(cx, cy, cz, seed + 2)], 1)
                d = np.linalg.norm(fp - p, axis=1)
                f2 = np.where(d < f1, f1, np.minimum(f2, d))
                f1 = np.minimum(f1, d)
    return f1, f2


def height(kind, p, scale, seed):
    """A detail height field (roughly -1..1) of a given kind at world points p (N,3), feature size scale."""
    q = p / scale
    if kind == "noise":
        return 2 * fbm(q, 3, seed) - 1
    if kind == "stipple":
        return 2 * fbm(q, 2, seed) - 1
    if kind == "ridged":   # wrinkle paint: crinkled ridges
        a = 1 - np.abs(2 * vnoise(q, seed) - 1)
        b = 1 - np.abs(2 * vnoise(q * 2.13 + 7.1, seed + 5) - 1)
        return a * a + 0.5 * b * b - 0.75
    if kind == "cells":    # leather: pebbled cells with creases between
        f1, f2 = worley(q, seed)
        return np.clip((f2 - f1) * 2.2, 0, 1) - 0.5 + 0.25 * (2 * vnoise(q * 3.0, seed + 9) - 1)
    if kind == "hex":      # lens prisms: domed cells
        f1, _ = worley(q, seed)
        return 1 - 2 * np.clip(f1, 0, 1)
    raise ValueError(kind)


def detail_normals(n, p, det, seed, chunk=200000):
    """Perturb unit normals n (N,3) by a 3D height field's gradient (finite differences, seamless across UV
    islands): tilt ~ amp radians at the steepest."""
    kind = det.get("type", "none")
    if kind in ("none", "grooves") or det.get("amp", 0) <= 0:
        return n
    scale, amp = float(det["scale"]), float(det["amp"])
    out = np.empty_like(n)
    e = scale * 0.15
    for a in range(0, len(n), chunk):
        pp = p[a:a + chunk]
        g = np.zeros_like(pp)
        h0 = height(kind, pp, scale, seed)
        for k in range(3):   # forward differences: four evaluations a texel, not six
            off = np.zeros(3)
            off[k] = e
            g[:, k] = (height(kind, pp + off, scale, seed) - h0) / e
        nn = n[a:a + chunk]
        gt = g - nn * (g * nn).sum(1, keepdims=True)
        out[a:a + chunk] = unit(nn - amp * scale * 0.5 * gt)
    return out


def vertex_convexity(v, f):
    """Per vertex of a triangle mesh: the mean over its edges of n . (p - q) / |p - q| with n the (welded) vertex
    normal: + on convex edges (about +0.5 at a right-angled edge), 0 flat, - in creases. Scale-free, so a fin's rim
    reads the same as a cover's edge. Vertices are welded by position first (glTF splits them at seams)."""
    key = np.round(v * 1000.0).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.reshape(-1)
    vw = v[first]
    fw = inv[f]
    fn = np.cross(vw[fw[:, 1]] - vw[fw[:, 0]], vw[fw[:, 2]] - vw[fw[:, 0]])
    vn = np.zeros_like(vw)
    for k in range(3):
        np.add.at(vn, fw[:, k], fn)
    vn = unit(vn)
    e = np.concatenate([fw[:, [0, 1]], fw[:, [1, 2]], fw[:, [2, 0]]])
    e = np.unique(np.sort(e, 1), axis=0)
    e = e[e[:, 0] != e[:, 1]]
    d = vw[e[:, 1]] - vw[e[:, 0]]
    L = np.maximum(np.linalg.norm(d, axis=1), 1e-9)
    acc = np.zeros(len(vw))
    cnt = np.zeros(len(vw))
    np.add.at(acc, e[:, 0], -(vn[e[:, 0]] * d).sum(1) / L)
    np.add.at(acc, e[:, 1], (vn[e[:, 1]] * d).sum(1) / L)
    np.add.at(cnt, e[:, 0], 1)
    np.add.at(cnt, e[:, 1], 1)
    return (acc / np.maximum(cnt, 1))[inv]


# --- image helpers (2D float arrays with a coverage mask) ------------------------------------------------------------

def box_blur(img, r):
    """Box blur of radius r (separable, edge-clamped) of an (H,W[,C]) array."""
    if r <= 0:
        return img
    out = img
    for axis in (0, 1):
        pad = [(0, 0)] * out.ndim
        pad[axis] = (r + 1, r)
        c = np.cumsum(np.pad(out, pad, mode="edge"), axis=axis, dtype=np.float64)
        n = out.shape[axis]
        hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
        lo = np.take(c, np.arange(0, n), axis=axis)
        out = (hi - lo) / (2 * r + 1)
    return out


def masked_blur(img, mask, r, passes=2):
    """Blur only among covered texels (weights = mask): the mean of the covered neighbours."""
    m = mask.astype(np.float64)
    a = img * (m[..., None] if img.ndim == 3 else m)
    w = m
    for _ in range(passes):
        a, w = box_blur(a, r), box_blur(w, r)
    return a / np.maximum(w[..., None] if img.ndim == 3 else w, 1e-9)


def dilate_fill(img, mask, px, fill=None):
    """Grow the covered texels' values px texels out (mean of covered neighbours, one ring a step), then fill
    everything else with `fill` if given, else from a pull-push pyramid (so mips never pull in black). img (H,W,C)."""
    img = img.copy()
    m = mask.copy()
    for _ in range(px):
        w = box_blur(m.astype(np.float64), 1)
        s = box_blur(img * m[..., None], 1)
        grow = (~m) & (w > 1e-6)
        img[grow] = s[grow] / w[grow][:, None]
        m = m | grow
    if fill is not None:
        return np.where(m[..., None], img, np.asarray(fill, dtype=img.dtype))
    # pull-push for the rest
    levels = [(img * m[..., None], m.astype(np.float64))]
    while levels[-1][1].shape[0] > 1 and levels[-1][1].shape[1] > 1:
        a, w = levels[-1]
        H, W = w.shape
        a2 = a[:H // 2 * 2, :W // 2 * 2].reshape(H // 2, 2, W // 2, 2, -1).sum((1, 3))
        w2 = w[:H // 2 * 2, :W // 2 * 2].reshape(H // 2, 2, W // 2, 2).sum((1, 3))
        levels.append((a2, w2))
    a, w = levels[-1]
    fill = a / np.maximum(w[..., None], 1e-9)
    for a, w in reversed(levels[:-1]):
        H, W = w.shape
        up = np.repeat(np.repeat(fill, 2, 0), 2, 1)
        up = np.pad(up, ((0, H - up.shape[0]), (0, W - up.shape[1]), (0, 0)), mode="edge")[:H, :W]
        own = a / np.maximum(w[..., None], 1e-9)
        fill = np.where(w[..., None] > 0, own, up)
    out = np.where(m[..., None], img, fill)
    return out


def half_size(img):
    H, W = img.shape[:2]
    return img.reshape(H // 2, 2, W // 2, 2, *img.shape[2:]).mean((1, 3))


def to_u8(x):
    return np.clip(np.floor(np.asarray(x) * 255.0 + 0.5), 0, 255).astype(np.uint8)


# --- configuration ---------------------------------------------------------------------------------------------------

class Config:
    def __init__(self, args):
        self.args = args
        self.stage = args.stage_dir
        self.man = json.loads((self.stage / "manifest.json").read_text())
        self.mats_path = args.materials
        self.mats_json = json.loads(self.mats_path.read_text())
        self.materials = self.mats_json["materials"]
        self.types = self.mats_json["surface_types"]
        self.overrides = {int(k): v for k, v in self.mats_json.get("surface_overrides", {}).items()}
        self.bake = {**BAKE_DEFAULTS, **self.mats_json.get("bake", {})}
        self.mat_of = {}
        for mat, m in self.materials.items():
            for label in m["labels"]:
                if label in self.mat_of:
                    raise ValueError(f"{label} is in two materials")
                self.mat_of[label] = mat
        missing = [lb for lb in self.man["labels"] if lb not in self.mat_of]
        if missing:
            raise ValueError(f"{self.mats_path}: no material for {missing}")
        self.labels = list(self.man["labels"])
        self.piece_mats = self.man["materials"]
        self.art = args.art or self.stage / "art"
        self.cache = args.cache or self.stage / "tex_cache"
        self.quick = args.quick
        # the cache keys take the source of the code each step runs (an edit elsewhere keeps the costly bakes)
        import inspect
        src = lambda *fs: sha(VERSION, *[inspect.getsource(f) for f in fs])   # noqa: E731
        self.code_uv = src(unwrap, to_nif_uv, Scene)
        self.code_bake = src(Scene, set_uv, bake_gbuffer, bake_normals, bake_convexity, bake_ao, _bake_material,
                             _new_image, _pixels, ours_copy, high_set, occluders, vertex_convexity, unit, process_label)
        self.code_author = sha(src(author, curvature, heat_ports, nearest_dist, coachline_field, coachline_v2, raster_side_yz,
                                   march, resample_loop, dist_to_polyline, detail_normals, height, worley, fbm, vnoise,
                                   _hash, box_blur, masked_blur, dilate_fill, half_size, to_u8, srgb_to_lin, lin_to_srgb,
                                   smoothstep, unit, hexrgb, label_axle),
                               HERE / "nifly_tangents.py")
        self.code_dds = sha(src(dds_jobs_for, cube_jobs, run_dds, half_size, to_u8), HERE / "write_dds.py")

    def size(self, mat):
        s = int(self.materials[mat]["size"])
        return max(64, s // 4) if self.quick else s

    def s_size(self, mat):
        s = int(self.materials[mat].get("s_size", self.materials[mat]["size"]))
        return max(64, s // 4) if self.quick else s

    def shape(self, label):
        with np.load(self.stage / "shapes" / f"{label}.npz") as z:
            return {k: z[k] for k in z.files}

    def shape_hash(self, label):
        return sha(self.stage / "shapes" / f"{label}.npz")

    def is_art(self, mat):
        return "art" in self.materials[mat]

    def surfaces_of(self, label, shp, overrides=True):
        """Per triangle: its surface name (the material's piece-material map, then the glTF mesh overrides)."""
        m = self.materials[self.mat_of[label]]
        names = []
        for mid, src in zip(shp["mat"].tolist(), shp["src"].tolist()):
            pm = self.piece_mats[mid]
            s = self.overrides.get(src) if src >= 0 and overrides else None
            if s is None:
                s = m["surfaces"].get(pm)
            if s is None:
                raise ValueError(f"{label}: no surface for piece material {pm} (glTF mesh {src})")
            names.append(s)
        return names


# --- Blender ---------------------------------------------------------------------------------------------------------

class Scene:
    """One Blender session: the low shapes (every label, in the parked frame) and, when needed, the glTF placed in the
    parked frame (manifest's blender_to_parked)."""

    def __init__(self, cfg):
        import bpy
        self.bpy = bpy
        self.cfg = cfg
        bpy.ops.wm.read_factory_settings(use_empty=True)
        sc = bpy.context.scene
        self.sc = sc
        sc.render.engine = "CYCLES"
        sc.cycles.device = "CPU"
        sc.cycles.seed = 0
        sc.cycles.use_animated_seed = False
        sc.cycles.use_denoising = False
        sc.cycles.use_adaptive_sampling = False
        if cfg.args.threads:
            sc.render.threads_mode = "FIXED"
            sc.render.threads = cfg.args.threads
        sc.render.bake.margin = 0
        sc.render.bake.use_clear = False
        sc.render.bake.target = "IMAGE_TEXTURES"
        w = bpy.data.worlds.new("bake_world")
        w.use_nodes = True
        sc.world = w
        w.light_settings.distance = float(cfg.bake["ao_distance"])
        self.lows = {}
        self.highs = None
        for label in cfg.labels:
            self.lows[label] = self._low(label)

    def _low(self, label):
        bpy = self.bpy
        shp = self.cfg.shape(label)
        me = bpy.data.meshes.new(f"low_{label}")
        me.from_pydata(shp["pos"].tolist(), [], shp["tri"].tolist())
        if len(me.polygons) != len(shp["tri"]):
            raise ValueError(f"{label}: Blender made {len(me.polygons)} faces of {len(shp['tri'])} triangles")
        me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), bool))
        n = unit(shp["nrm"].astype(np.float64))
        me.normals_split_custom_set_from_vertices([tuple(x) for x in n.tolist()])
        o = bpy.data.objects.new(f"low_{label}", me)
        self.sc.collection.objects.link(o)
        o.hide_render = True
        return o

    def load_gltf(self, path):
        if self.highs is not None:
            return
        bpy = self.bpy
        from mathutils import Matrix
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(path))
        new = [o for o in bpy.data.objects if o not in before]
        b2p = Matrix(self.cfg.man["blender_to_parked"])
        for o in new:
            if o.parent is None:
                o.matrix_world = b2p @ o.matrix_world
        bpy.context.view_layer.update()
        self.highs = {}
        self.high_mat = {}
        for o in new:
            if o.type == "MESH" and o.name.startswith("desirefx.me_"):
                i = int(o.name[12:15]) - 1
                self.highs[i] = o
                gm = o.data.materials[0].name if o.data.materials else ""
                gm = gm.split(".")[0]
                self.high_mat[i] = GLTF_MATERIALS.get(gm, gm)
                o.hide_render = True
        self.high_verts = {}
        for i, o in self.highs.items():
            v = np.empty(len(o.data.vertices) * 3)
            o.data.vertices.foreach_get("co", v)
            v = v.reshape(-1, 3)
            M = np.array(o.matrix_world)
            self.high_verts[i] = v @ M[:3, :3].T + M[:3, 3]
        self.cvx_done = set()

    def cvx_material(self):
        """Emission = the vertex attribute tb_cvx (convexity, (c+1)/2): what the convexity bake reads off the high
        meshes (their glTF materials matter to no bake: the normal bake takes the geometry's normals)."""
        bpy = self.bpy
        m = bpy.data.materials.get("tb_cvx")
        if m is None:
            m = bpy.data.materials.new("tb_cvx")
            m.use_nodes = True
            nt = m.node_tree
            for n in list(nt.nodes):
                nt.nodes.remove(n)
            out = nt.nodes.new("ShaderNodeOutputMaterial")
            em = nt.nodes.new("ShaderNodeEmission")
            at = nt.nodes.new("ShaderNodeAttribute")
            at.attribute_name = "tb_cvx"
            nt.links.new(at.outputs["Color"], em.inputs["Color"])
            nt.links.new(em.outputs[0], out.inputs[0])
        return m

    def prepare_cvx(self, o, world_verts=None, mesh_id=-1):
        """Per-vertex convexity of a mesh object as its tb_cvx attribute (red; green = (glTF mesh + 1) / 256, so the
        same bake says which glTF mesh each texel was baked from), and the convexity material on it."""
        if o.name in getattr(self, "cvx_done", set()):
            return
        me = o.data
        me.calc_loop_triangles()
        f = np.empty(len(me.loop_triangles) * 3, np.int64)
        me.loop_triangles.foreach_get("vertices", f)
        if world_verts is None:
            v = np.empty(len(me.vertices) * 3)
            me.vertices.foreach_get("co", v)
            M = np.array(o.matrix_world)
            world_verts = v.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]
        c = vertex_convexity(world_verts, f.reshape(-1, 3))
        if "tb_cvx" in me.attributes:
            me.attributes.remove(me.attributes["tb_cvx"])
        a = me.attributes.new("tb_cvx", "FLOAT_COLOR", "POINT")
        g = ((c + 1) / 2).astype(np.float32)
        ident = np.full_like(g, (mesh_id + 1) / 256.0)
        a.data.foreach_set("color", np.column_stack([g, ident, np.zeros_like(g), np.ones_like(g)]).ravel())
        me.materials.clear()
        me.materials.append(self.cvx_material())
        if not hasattr(self, "cvx_done"):
            self.cvx_done = set()
        self.cvx_done.add(o.name)

    def only_visible(self, objs):
        keep = set(objs)
        for o in self.sc.objects:
            o.hide_render = o not in keep
        for o in objs:
            o.hide_render = False

    def select(self, active, others=()):
        bpy = self.bpy
        for o in bpy.context.view_layer.objects:
            o.select_set(False)
        for o in others:
            o.select_set(True)
        active.select_set(True)
        bpy.context.view_layer.objects.active = active


def unwrap(scn, label, surf_names, cfg, size, angle):
    """Smart UV per surface (islands never mix surfaces), islands scaled to their 3D area and by each surface's
    density, packed (concave, any rotation). Returns uv (T,3,2) in Blender's convention (v up)."""
    import bmesh
    bpy = scn.bpy
    o = scn.lows[label]
    me = o.data
    while me.uv_layers:
        me.uv_layers.remove(me.uv_layers[0])
    me.uv_layers.new(name="UVMap")
    scn.only_visible([o])
    scn.select(o)
    surf = np.array(surf_names)
    names = sorted(set(surf_names))
    for s in names:
        sel = (surf == s)
        bpy.ops.object.mode_set(mode="EDIT")   # in and out around each operator: a stale edit mesh writes old UVs back
        bm = bmesh.from_edit_mesh(me)
        bm.faces.ensure_lookup_table()
        for f in bm.faces:
            f.select_set(bool(sel[f.index]))
        bmesh.update_edit_mesh(me)
        bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=0.0, area_weight=0.0,
                                 correct_aspect=True, scale_to_bounds=False)
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.average_islands_scale()
    bpy.ops.object.mode_set(mode="OBJECT")
    uv = np.empty(len(me.loops) * 2)
    me.uv_layers[0].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 3, 2)
    for s in names:
        k = float(cfg.types[s].get("density", 1.0))
        if k != 1.0:
            uv[surf == s] *= math.sqrt(k)
    me.uv_layers[0].data.foreach_set("uv", uv.ravel())
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.select_all(action="SELECT")
    margin = cfg.bake["margin_px"] / float(size * (4 if cfg.quick else 1))   # full-size texels, --quick too
    try:
        bpy.ops.uv.pack_islands(rotate=True, rotate_method="ANY", scale=True, margin_method="FRACTION", margin=margin,
                                shape_method="CONCAVE")
    except TypeError:
        bpy.ops.uv.pack_islands(rotate=True, margin=margin)
    bpy.ops.object.mode_set(mode="OBJECT")
    me.uv_layers[0].data.foreach_get("uv", uv.ravel())
    return uv.reshape(-1, 3, 2)


def to_nif_uv(uv_blender):
    """Blender (v up) -> nif (v down) on the I3 1/32768 grid. Not pre-rounded to the half floats the nifs store
    (1/2048 apart in 0.5..1): nifly makes the tangent frames from the UVs it is given, and rounded ones collapse
    thin triangles (13% of a rim's) into frames of float noise; the game then samples within half a texel of 2048."""
    u = np.column_stack([uv_blender.reshape(-1, 2)[:, 0], 1.0 - uv_blender.reshape(-1, 2)[:, 1]])
    return NT.quantise_uv(np.clip(u, 0.0, 1.0)).reshape(-1, 3, 2)


def set_uv(scn, label, uv_nif):
    me = scn.lows[label].data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    b = uv_nif.reshape(-1, 2).copy()
    b[:, 1] = 1.0 - b[:, 1]
    me.uv_layers[0].data.foreach_set("uv", b.ravel())


def _bake_material(scn, o, img, gbuffer=False):
    bpy = scn.bpy
    m = bpy.data.materials.get("tb_bake") if not gbuffer else bpy.data.materials.get("tb_gbuf")
    name = "tb_gbuf" if gbuffer else "tb_bake"
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        nt = m.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        em = nt.nodes.new("ShaderNodeEmission")
        nt.links.new(em.outputs[0], out.inputs[0])
        if gbuffer:
            a_t = nt.nodes.new("ShaderNodeAttribute")
            a_t.attribute_name = "tb_tid"
            a_b = nt.nodes.new("ShaderNodeAttribute")
            a_b.attribute_name = "tb_bary"
            sep = nt.nodes.new("ShaderNodeSeparateColor")
            comb = nt.nodes.new("ShaderNodeCombineColor")
            nt.links.new(a_b.outputs["Color"], sep.inputs[0])
            nt.links.new(a_t.outputs["Fac"], comb.inputs[0])
            nt.links.new(sep.outputs[0], comb.inputs[1])
            nt.links.new(sep.outputs[1], comb.inputs[2])
            nt.links.new(comb.outputs[0], em.inputs["Color"])
        node = nt.nodes.new("ShaderNodeTexImage")
        node.name = "target"
    nt = m.node_tree
    node = nt.nodes["target"]
    node.image = img
    for n in nt.nodes:
        n.select = False
    node.select = True
    nt.nodes.active = node
    o.data.materials.clear()
    o.data.materials.append(m)


def _new_image(scn, name, size):
    bpy = scn.bpy
    img = bpy.data.images.new(name, size, size, alpha=True, float_buffer=True)
    img.colorspace_settings.name = "Non-Color"
    img.pixels.foreach_set(np.zeros(size * size * 4, np.float32))
    return img


def _pixels(img, size):
    a = np.empty(size * size * 4, np.float32)
    img.pixels.foreach_get(a)
    return a.reshape(size, size, 4)[::-1].copy()   # nif orientation: row 0 = v 0 (top)


def bake_gbuffer(scn, label, size):
    """Per texel: the triangle covering its centre and the barycentric weights there (Blender's own bake
    rasterisation, so the other bakes line up texel for texel)."""
    bpy = scn.bpy
    o = scn.lows[label]
    me = o.data
    T = len(me.polygons)
    for nm in ("tb_tid", "tb_bary"):
        if nm in me.attributes:
            me.attributes.remove(me.attributes[nm])
    at = me.attributes.new("tb_tid", "FLOAT", "FACE")
    at.data.foreach_set("value", np.arange(T, dtype=np.float32))
    ab = me.attributes.new("tb_bary", "FLOAT_COLOR", "CORNER")
    ab.data.foreach_set("color", np.tile(np.array([1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1], np.float32), T))
    img = _new_image(scn, f"gb_{label}", size)
    _bake_material(scn, o, img, gbuffer=True)
    scn.only_visible([o])
    scn.select(o)
    scn.sc.cycles.samples = 1
    bpy.ops.object.bake(type="EMIT", margin=0, use_clear=False)
    px = _pixels(img, size)
    bpy.data.images.remove(img)
    cov = px[..., 3] > 0.5
    tid = np.where(cov, np.rint(px[..., 0]).astype(np.int64), -1)
    if cov.any() and (np.abs(px[..., 0][cov] - tid[cov]).max() > 1e-3 or tid[cov].max() >= T):
        raise ValueError(f"{label}: the triangle-id bake came back off the integers")
    return tid.astype(np.int32), px[..., 1:3].astype(np.float32)


def bake_normals(scn, label, size, high_objs):
    bpy = scn.bpy
    o = scn.lows[label]
    img = _new_image(scn, f"nm_{label}", size)
    _bake_material(scn, o, img)
    scn.only_visible([o] + high_objs)
    scn.select(o, high_objs)
    scn.sc.cycles.samples = 1
    bpy.ops.object.bake(type="NORMAL", normal_space="OBJECT", use_selected_to_active=True,
                        cage_extrusion=float(scn.cfg.bake["cage"]), max_ray_distance=float(scn.cfg.bake["ray"]),
                        margin=0, use_clear=False)
    px = _pixels(img, size)
    bpy.data.images.remove(img)
    hit = px[..., 3] > 0.5
    n = px[..., :3] * 2.0 - 1.0
    return n.astype(np.float32), hit


def bake_convexity(scn, label, size, high_objs):
    """The high meshes' vertex convexity, carried onto the label's texels the way the normals are, and which glTF
    mesh each texel came from (-1: ours, or no hit)."""
    bpy = scn.bpy
    o = scn.lows[label]
    for h in high_objs:
        gl = h.name.startswith("desirefx.me_") and scn.highs is not None
        mid = int(h.name[12:15]) - 1 if gl else -1
        scn.prepare_cvx(h, scn.high_verts.get(mid) if gl else None, mid)
    img = _new_image(scn, f"cv_{label}", size)
    _bake_material(scn, o, img)
    scn.only_visible([o] + high_objs)
    scn.select(o, high_objs)
    scn.sc.cycles.samples = 1
    bpy.ops.object.bake(type="EMIT", use_selected_to_active=True, cage_extrusion=float(scn.cfg.bake["cage"]),
                        max_ray_distance=float(scn.cfg.bake["ray"]), margin=0, use_clear=False)
    px = _pixels(img, size)
    bpy.data.images.remove(img)
    hit = px[..., 3] > 0.5
    hid = np.where(hit, np.rint(px[..., 1] * 256.0).astype(np.int64) - 1, -1).astype(np.int16)
    return (px[..., 0] * 2 - 1).astype(np.float32), hit, hid


def bake_ao(scn, label, size, occluders, samples):
    bpy = scn.bpy
    o = scn.lows[label]
    img = _new_image(scn, f"ao_{label}", size)
    _bake_material(scn, o, img)
    scn.only_visible([o] + occluders)
    scn.select(o)
    scn.sc.cycles.samples = samples
    bpy.ops.object.bake(type="AO", margin=0, use_clear=False)
    px = _pixels(img, size)
    bpy.data.images.remove(img)
    return px[..., 0].astype(np.float32)


def ours_copy(scn, label, shp):
    """Our own triangles of a label (src -1: the headlamp, the mirrors' cups...) as a high object of their own, so
    the selected-to-active bake finds them (they have nothing in the glTF)."""
    bpy = scn.bpy
    sel = shp["src"] < 0
    if not sel.any():
        return None
    tri = shp["tri"][sel]
    used, inv = np.unique(tri, return_inverse=True)
    me = bpy.data.meshes.new(f"ours_{label}")
    me.from_pydata(shp["pos"][used].tolist(), [], inv.reshape(-1, 3).tolist())
    me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), bool))
    me.normals_split_custom_set_from_vertices([tuple(x) for x in unit(shp["nrm"][used].astype(np.float64)).tolist()])
    o = bpy.data.objects.new(f"ours_{label}", me)
    scn.sc.collection.objects.link(o)
    o.hide_render = True
    return o


def high_set(scn, cfg, label, shp):
    """The glTF meshes to bake a label from: its sources (manifest), plus the meshes welded into its pieces that lost
    the majority vote (a tyre's other half), found as those of the label's piece materials with most of their
    vertices near the label's own (same material) vertices."""
    srcs = set(int(s) for s in cfg.man["labels"][label]["sources"])
    cell = float(cfg.bake["near_cell"])
    extra = []

    def cell_key(k):   # exact: 21 bits a coordinate
        k = k + (1 << 20)
        return (k[:, 0] << 42) | (k[:, 1] << 21) | k[:, 2]
    for mid in sorted(set(shp["mat"].tolist())):
        pm = cfg.piece_mats[mid]
        tri = shp["tri"][shp["mat"] == mid]
        pts = shp["pos"][np.unique(tri)]
        base = np.floor(pts / cell).astype(np.int64)
        keys = np.unique(np.concatenate([cell_key(base + d) for d in
                                         np.array(np.meshgrid([-1, 0, 1], [-1, 0, 1], [-1, 0, 1])).reshape(3, -1).T]))
        for i, gm in scn.high_mat.items():
            if gm != pm or i in srcs or i in cfg.bake["exclude_meshes"]:
                continue
            v = scn.high_verts[i][::max(1, len(scn.high_verts[i]) // 4000)]
            frac = np.isin(cell_key(np.floor(v / cell).astype(np.int64)), keys).mean()
            if frac >= cfg.bake["near_fraction"]:
                extra.append((i, round(float(frac), 3)))
    for i, _ in extra:
        srcs.add(i)
    return sorted(s for s in srcs if s in scn.highs and s not in cfg.bake["exclude_meshes"]), extra


def occluders(cfg, scn, label):
    if label.startswith("wheelF") or label.startswith("wheelR"):
        w = label[:6]
        return [scn.lows[lb] for lb in cfg.labels if lb.startswith(w)]
    out = []
    for lb in cfg.labels:
        if lb in OVERLAYS:
            continue
        if lb in MIRROR_VARIANTS and lb != (label if label in MIRROR_VARIANTS else "front_mirrorStock"):
            continue
        out.append(scn.lows[lb])
    return out


# --- authoring -------------------------------------------------------------------------------------------------------

def curvature(P, N, cov, surf_img):
    """Mean curvature (1/units, + convex) from the texel grid: the change of the (baked) normal across a texel's
    neighbours over the change of position, where both neighbours are on the same island (continuous)."""
    H, W = cov.shape
    k = np.zeros((H, W))
    cnt = np.zeros((H, W))
    step = []
    for axis in (0, 1):
        a = np.roll(P, 1, axis) - np.roll(P, -1, axis)
        step.append(np.linalg.norm(a, axis=-1))
    allst = np.concatenate([s[cov] for s in step])
    med = np.median(allst[allst > 0]) if (allst > 0).any() else 1.0
    for axis in (0, 1):
        cp, cm = np.roll(cov, -1, axis), np.roll(cov, 1, axis)
        sp, sm = np.roll(surf_img, -1, axis), np.roll(surf_img, 1, axis)
        dP = np.roll(P, -1, axis) - np.roll(P, 1, axis)
        dN = np.roll(N, -1, axis) - np.roll(N, 1, axis)
        d2 = (dP * dP).sum(-1)
        ok = cov & cp & cm & (sp == surf_img) & (sm == surf_img) & (d2 > 1e-12) & (np.sqrt(d2) < 6 * med)
        kk = np.where(ok, (dN * dP).sum(-1) / np.maximum(d2, 1e-12), 0.0)
        k += kk
        cnt += ok
    return np.where(cnt > 0, k / np.maximum(cnt, 1), 0.0), med


def heat_ports(cfg, label, shp, ht):
    """The exhaust ports: this shape's vertices within `touch` of the named shape's upper part (its top `top`
    fraction by height: the cylinder heads, not the crankcase the pipes run past)."""
    other = cfg.shape(ht["near"])["pos"]
    z0, z1 = other[:, 2].min(), other[:, 2].max()
    other = other[other[:, 2] >= z1 - float(ht.get("top", 1.0)) * (z1 - z0)]
    mine = shp["pos"]
    near = np.zeros(len(mine), bool)
    for a in range(0, len(mine), 512):
        d = np.linalg.norm(mine[a:a + 512, None, :] - other[None, ::3, :], axis=2).min(1)
        near[a:a + 512] = d < float(ht["touch"])
    return mine[near]


def nearest_dist(p, pts, chunk=4096):
    out = np.full(len(p), 1e9)
    if not len(pts):
        return out
    for a in range(0, len(p), chunk):
        out[a:a + chunk] = np.linalg.norm(p[a:a + chunk, None, :] - pts[None], axis=2).min(1)
    return out


def coachline_field(P_tank, pos_tank, res=0.25):
    """Distance inside the tank's side silhouette (y, z) to its outline, as a grid and a lookup."""
    yz = pos_tank[:, 1:3]
    lo = yz.min(0) - 2
    hi = yz.max(0) + 2
    shape = np.ceil((hi - lo) / res).astype(int) + 1
    grid = np.zeros(shape, bool)
    q = np.floor((P_tank[:, 1:3] - lo) / res).astype(int)
    grid[q[:, 0], q[:, 1]] = True
    # close small holes (texels miss a few cells), then the exact distance of every inside cell to the outline
    g = box_blur(grid.astype(np.float64), 2) > 0.3
    g = box_blur(g.astype(np.float64), 1) > 0.99
    outside = ~g
    edge = outside & (box_blur(g.astype(np.float64), 1) > 0)
    ec = np.argwhere(edge).astype(np.float64) * res
    d = np.zeros(g.shape)
    inside = np.argwhere(g)
    if len(ec):
        d[g] = nearest_dist(np.column_stack([inside.astype(np.float64) * res, np.zeros(len(inside))]),
                            np.column_stack([ec, np.zeros(len(ec))]), chunk=2048)

    def lookup(pyz):
        f = (pyz - lo) / res
        i0 = np.clip(np.floor(f).astype(int), 0, np.array(d.shape) - 2)
        t = np.clip(f - i0, 0, 1)
        v00 = d[i0[:, 0], i0[:, 1]]
        v10 = d[i0[:, 0] + 1, i0[:, 1]]
        v01 = d[i0[:, 0], i0[:, 1] + 1]
        v11 = d[i0[:, 0] + 1, i0[:, 1] + 1]
        return (v00 * (1 - t[:, 0]) * (1 - t[:, 1]) + v10 * t[:, 0] * (1 - t[:, 1]) + v01 * (1 - t[:, 0]) * t[:, 1]
                + v11 * t[:, 0] * t[:, 1])
    return lookup


# --- the coachline since the 2026-11-01a build: two parallel offsets of one smooth traced curve ---------------------
# Test 47: 2026-10-31a's line (coachline_field: the iso-lines of a distance field on a 0.25-unit grid of the tank's
# projected outline) wobbled by up to 0.08 units (about 1.5 texels, every 2 to 3 units: the grid's staircase), its
# width was measured in projection, and the side mask faded it where the tank's surface folds under itself at the rear
# (the crease over the seat's nose): the line broke there and its turn was a sharp corner. coachline_v2 traces the
# outline at 0.02, smooths it, offsets it once (C, at inset + gap + radius) and draws the two lines as C's outward
# offsets, so they are parallel, round every corner (radius, radius + gap), keep one width on the surface, and are
# drawn on the tank's outer layer (no fade at the crease). Off value: no "radius" in the pinstripe entry (width 0.16).

def raster_side_yz(tris, lo, res, shape):
    """The tank's triangles (T,3,3) projected on (y, z): coverage (H,W) bool on cell centres, and the outermost x of
    the +x-facing and the -x-facing triangles per cell (for which surface layer is the outer one)."""
    cover = np.zeros(shape, bool)
    xmax = np.full(shape, -1e9)
    xmin = np.full(shape, 1e9)
    nx = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])[:, 0]
    for t, n in zip(tris, nx):
        yz = t[:, 1:3]
        a = np.floor((yz.min(0) - lo) / res).astype(int)
        b = np.ceil((yz.max(0) - lo) / res).astype(int) + 1
        a = np.clip(a, 0, np.array(shape) - 1)
        b = np.clip(b, 0, np.array(shape))
        if (b <= a).any():
            continue
        gy = lo[0] + (np.arange(a[0], b[0]) + 0.5) * res
        gz = lo[1] + (np.arange(a[1], b[1]) + 0.5) * res
        Y, Z = np.meshgrid(gy, gz, indexing="ij")
        v0, v1, v2 = yz
        d = (v1[1] - v2[1]) * (v0[0] - v2[0]) + (v2[0] - v1[0]) * (v0[1] - v2[1])
        if abs(d) < 1e-12:
            continue
        l0 = ((v1[1] - v2[1]) * (Y - v2[0]) + (v2[0] - v1[0]) * (Z - v2[1])) / d
        l1 = ((v2[1] - v0[1]) * (Y - v2[0]) + (v0[0] - v2[0]) * (Z - v2[1])) / d
        l2 = 1 - l0 - l1
        inside = (l0 >= -1e-9) & (l1 >= -1e-9) & (l2 >= -1e-9)
        if not inside.any():
            continue
        x = l0 * t[0, 0] + l1 * t[1, 0] + l2 * t[2, 0]
        sl = (slice(a[0], b[0]), slice(a[1], b[1]))
        cover[sl] |= inside
        if n > 0:
            xmax[sl] = np.where(inside, np.maximum(xmax[sl], x), xmax[sl])
        else:
            xmin[sl] = np.where(inside, np.minimum(xmin[sl], x), xmin[sl])
    return cover, xmax, xmin


def march(field, level):
    """Marching squares: the closed loops of field == level, in (row, col) index coordinates, longest first."""
    f = field - level
    pos = f > 0
    H, W = f.shape
    pts, ids = [], {}

    def edge_pts(axis):
        a = f[:-1, :] if axis == 0 else f[:, :-1]
        b = f[1:, :] if axis == 0 else f[:, 1:]
        ch = (a > 0) != (b > 0)
        r, c = np.nonzero(ch)
        t = a[r, c] / (a[r, c] - b[r, c])
        p = np.column_stack([r + (t if axis == 0 else 0), c + (t if axis == 1 else 0)])
        return r, c, p
    out = {}
    for axis in (0, 1):
        r, c, p = edge_pts(axis)
        for k in range(len(r)):
            ids[(axis, int(r[k]), int(c[k]))] = len(pts)
            pts.append(p[k])
    pts = np.array(pts)
    nbr = {}

    def link(e1, e2):
        nbr.setdefault(e1, []).append(e2)
        nbr.setdefault(e2, []).append(e1)
    pz = f > 0
    corners = pz[:-1, :-1].astype(int) + pz[1:, :-1] + pz[:-1, 1:] + pz[1:, 1:]
    for i, j in zip(*np.nonzero((corners > 0) & (corners < 4))):
        i, j = int(i), int(j)
        es = [e for e in ((0, i, j), (1, i + 1, j), (0, i, j + 1), (1, i, j)) if e in ids]
        if len(es) == 2:
            link(ids[es[0]], ids[es[1]])
        elif len(es) == 4:
            centre = (f[i, j] + f[i + 1, j] + f[i, j + 1] + f[i + 1, j + 1]) / 4
            if (centre > 0) == (f[i, j] > 0):
                link(ids[es[0]], ids[es[1]]); link(ids[es[2]], ids[es[3]])
            else:
                link(ids[es[3]], ids[es[0]]); link(ids[es[1]], ids[es[2]])
    seen = np.zeros(len(pts), bool)
    loops = []
    for s in range(len(pts)):
        if seen[s] or len(nbr.get(s, [])) != 2:
            continue
        loop = [s]
        seen[s] = True
        prev, cur = None, s
        while True:
            nx_ = [n for n in nbr[cur] if n != prev]
            if not nx_:
                break
            nxt = nx_[0]
            if nxt == s:
                break
            if seen[nxt]:
                break
            seen[nxt] = True
            loop.append(nxt)
            prev, cur = cur, nxt
        if len(loop) > 8:
            loops.append(pts[loop])
    loops.sort(key=lambda L: -len(L))
    return loops


def resample_loop(L, step, sigma=0.0):
    """A closed polyline resampled at equal arc length, then smoothed (a circular Gaussian of sigma, in units)."""
    P = np.vstack([L, L[:1]])
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    n = max(16, int(s[-1] / step))
    t = np.linspace(0, s[-1], n, endpoint=False)
    Q = np.column_stack([np.interp(t, s, P[:, k]) for k in range(P.shape[1])])
    if sigma > 0:
        k = int(np.ceil(3 * sigma / (s[-1] / n)))
        w = np.exp(-0.5 * ((np.arange(-k, k + 1) * s[-1] / n) / sigma) ** 2)
        w /= w.sum()
        Q = sum(w[i] * np.roll(Q, k - i, axis=0) for i in range(2 * k + 1))
    return Q


def dist_to_polyline(p, Q, chunk=2048):
    """Distance from points p (n,2) to the closed polyline Q (m,2), exact on its segments: (distance, unit direction
    from the nearest point to p)."""
    A = Q
    B = np.roll(Q, -1, axis=0)
    AB = B - A
    L2 = np.maximum((AB ** 2).sum(1), 1e-18)
    dist = np.zeros(len(p))
    dirv = np.zeros((len(p), 2))
    for a in range(0, len(p), chunk):
        q = p[a:a + chunk]
        d2 = ((q[:, None, :] - A[None]) ** 2).sum(2)
        i = d2.argmin(1)
        best = np.full(len(q), np.inf)
        bp = np.zeros((len(q), 2))
        for j in (i - 1, i):
            j = j % len(A)
            t = np.clip(((q - A[j]) * AB[j]).sum(1) / L2[j], 0, 1)
            c = A[j] + t[:, None] * AB[j]
            dd = np.linalg.norm(q - c, axis=1)
            better = dd < best
            best = np.where(better, dd, best)
            bp = np.where(better[:, None], c, bp)
        dist[a:a + chunk] = best
        v = q - bp
        dirv[a:a + chunk] = v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-12)
    return dist, dirv


def coachline_v2(P, N, tank_tris, ps, texel_px, report):
    """Per tank texel (P (n,3), N (n,3) its normal): the coachline's coverage 0..1. The outline is the tank's
    silhouette on (y, z), rasterised at 0.02 and traced (marching squares), its staircase smoothed out; C is the
    curve at outline distance inset + gap + radius; the two lines are C's outward offsets at radius and radius + gap,
    so they stay parallel and round every corner (radius and radius + gap); their width is measured on the surface
    (the field's slope across the line), their edges filtered over the texel's footprint (texel_px, units), and they
    are drawn only on the outermost layer of the tank seen along x."""
    inset, gap, hw = float(ps["inset"]), float(ps["gap"]), float(ps["width"]) / 2
    rc = float(ps.get("radius", 1.0))
    L0 = inset + gap + rc
    yz_all = tank_tris[:, :, 1:3].reshape(-1, 2)
    res = 0.02
    lo = yz_all.min(0) - 1.0
    hi = yz_all.max(0) + 1.0
    shape = tuple(np.ceil((hi - lo) / res).astype(int))
    cover, xmax, xmin = raster_side_yz(tank_tris, lo, res, shape)
    loops = march(cover.astype(np.float64), 0.5)
    outline = resample_loop(lo + (loops[0] + 0.5) * res, 0.05, sigma=0.12)
    # the outline's distance: coarse (every 5th cell of a 0.04 grid), then exact near level L0, where C is traced
    rb = 0.04
    ny, nz = int((hi[0] - lo[0]) / rb), int((hi[1] - lo[1]) / rb)
    gy = lo[0] + (np.arange(ny) + 0.5) * rb
    gz = lo[1] + (np.arange(nz) + 0.5) * rb
    Y, Z = np.meshgrid(gy, gz, indexing="ij")
    G = np.column_stack([Y.ravel(), Z.ravel()])
    ci = np.clip(((G - lo) / res).astype(int), 0, np.array(shape) - 1)
    ins = cover[ci[:, 0], ci[:, 1]]
    k = 5
    cy, cz = np.arange(0, ny, k), np.arange(0, nz, k)
    CY, CZ = np.meshgrid(gy[cy], gz[cz], indexing="ij")
    CG = np.column_stack([CY.ravel(), CZ.ravel()])
    cci = np.clip(((CG - lo) / res).astype(int), 0, np.array(shape) - 1)
    cins = cover[cci[:, 0], cci[:, 1]]
    dc = np.full(len(CG), -1.0)
    dc[cins] = dist_to_polyline(CG[cins], outline[::2])[0]
    # bilinear up to the fine grid
    fy = np.clip((np.arange(ny) / k), 0, len(cy) - 1.001)
    fz = np.clip((np.arange(nz) / k), 0, len(cz) - 1.001)
    i0, j0 = np.floor(fy).astype(int), np.floor(fz).astype(int)
    ty, tz = (fy - i0)[:, None], (fz - j0)[None, :]
    dcg = dc.reshape(len(cy), len(cz))
    i1, j1 = np.minimum(i0 + 1, len(cy) - 1), np.minimum(j0 + 1, len(cz) - 1)
    up = (dcg[i0][:, j0] * (1 - ty) * (1 - tz) + dcg[i1][:, j0] * ty * (1 - tz) + dcg[i0][:, j1] * (1 - ty) * tz
          + dcg[i1][:, j1] * ty * tz).ravel()
    dG = np.where(ins, up, -1.0)
    band = ins & (np.abs(up - L0) < 0.6)
    dG[band] = dist_to_polyline(G[band], outline)[0]
    field = dG.reshape(Y.shape)
    loopsC = march(field, L0)
    C = resample_loop(np.column_stack([gy[0] + loopsC[0][:, 0] * rb, gz[0] + loopsC[0][:, 1] * rb]), 0.04, sigma=0.08)
    report["coachline"] = dict(outline_len=round(float(np.linalg.norm(np.diff(outline, axis=0), axis=1).sum()), 1),
                               c_len=round(float(np.linalg.norm(np.diff(C, axis=0), axis=1).sum()), 1), loops_c=len(loopsC),
                               radius=rc)
    # the signed distance to C (+ outside it, toward the outline) on the grid where the lines can be, then per texel
    lines = ins & (up > inset - 0.6) & (up < L0 + 0.2)
    eg = np.where(ins, L0 - up, -1e3)        # off the band: a continuous stand-in far from both lines (no stray texels)
    ev = np.zeros((len(G), 2))
    dd, dv = dist_to_polyline(G[lines], C)
    sg = np.where(dG[lines] < L0, 1.0, -1.0)
    eg[lines] = dd * sg
    ev[lines] = dv * sg[:, None]
    eg = eg.reshape(Y.shape)
    ev = ev.reshape(Y.shape + (2,))
    f = (P[:, 1:3] - lo) / rb - 0.5
    a0 = np.clip(np.floor(f).astype(int), 0, np.array(Y.shape) - 2)
    t = np.clip(f - a0, 0, 1)
    w00 = (1 - t[:, 0]) * (1 - t[:, 1]); w10 = t[:, 0] * (1 - t[:, 1]); w01 = (1 - t[:, 0]) * t[:, 1]; w11 = t[:, 0] * t[:, 1]
    def samp(A):
        return (A[a0[:, 0], a0[:, 1]].T * w00 + A[a0[:, 0] + 1, a0[:, 1]].T * w10 + A[a0[:, 0], a0[:, 1] + 1].T * w01
                + A[a0[:, 0] + 1, a0[:, 1] + 1].T * w11).T
    e = samp(eg)
    gdir = samp(ev)
    gdir = gdir / np.maximum(np.linalg.norm(gdir, axis=1, keepdims=True), 1e-9)
    e = np.where(np.abs(e) > 100, -1e3, e)
    g3 = np.column_stack([np.zeros(len(P)), gdir])
    slope = np.sqrt(np.clip(1 - (g3 * N).sum(1) ** 2, 0.04, 1.0))
    cov = np.zeros(len(P))
    for off in (rc, rc + gap):
        across = np.abs(e - off) / slope                         # units on the surface
        cov = np.maximum(cov, np.clip(0.5 + (hw - across) / np.maximum(texel_px, 1e-3), 0, 1))
    # the outer layer only (the fold under the tank's rear lies under it in the projection)
    ci = np.clip(((P[:, 1:3] - lo) / res).astype(int), 0, np.array(shape) - 1)
    outer = np.where(N[:, 0] >= 0, P[:, 0] >= xmax[ci[:, 0], ci[:, 1]] - 0.35, P[:, 0] <= xmin[ci[:, 0], ci[:, 1]] + 0.35)
    graze = smoothstep(0.05, 0.15, np.abs(N[:, 0]))
    cov *= outer * graze
    report["coachline"]["texels"] = int((cov > 0.5).sum())
    return cov


def author(cfg, label, shp, uvc, gb, nh, hit, ao, cvx, hid, report):
    """The label's _d (RGBA), _n (tangent space, RGB) and _s (R spec, G smoothness) as float images (H,W,C), plus
    the paint layers kept for recolouring."""
    tid, bary = gb
    H, W = tid.shape
    cov = tid >= 0
    idx = np.nonzero(cov.ravel())[0]
    t = tid.ravel()[idx].astype(np.int64)
    b = bary.reshape(-1, 2)[idx].astype(np.float64)
    w = np.column_stack([b, 1.0 - b.sum(1)])
    tri = shp["tri"].astype(np.int64)
    pos = shp["pos"].astype(np.float64)
    nrm = unit(shp["nrm"].astype(np.float64))
    P = (w[:, :, None] * pos[tri[t]]).sum(1)
    Nl = unit((w[:, :, None] * nrm[tri[t]]).sum(1))
    # nifly's frames on the shape as the nifs carry it (after the seams)
    src_v, uv_split, c2v = NT.seam_split(tri, uvc)
    du, dv, nb, _, _, cond = NT.nifly_frames(pos[src_v], c2v, nrm[src_v], uv_split)
    corner = c2v[t]
    fdu = unit((w[:, :, None] * du[corner].astype(np.float64)).sum(1))
    fdv = unit((w[:, :, None] * dv[corner].astype(np.float64)).sum(1))
    fn = unit((w[:, :, None] * nb[corner].astype(np.float64)).sum(1))
    fcond = (w * cond[corner]).sum(1)
    # surfaces: the piece material's (then the shape's glTF mesh's override), then per texel the override of the
    # glTF mesh the bake hit (pieces welded from several glTF meshes carry only the majority's id)
    names = cfg.surfaces_of(label, shp)
    plain = cfg.surfaces_of(label, shp, overrides=False)
    src = shp["src"].astype(np.int64)[t]
    h_id = hid.reshape(-1)[idx].astype(np.int64)
    src = np.where(h_id >= 0, h_id, src)
    over = cfg.overrides
    snames = sorted(set(names) | set(plain) | {over[m] for m in set(src.tolist()) if m in over})
    sid_tri = np.array([snames.index(s) for s in names])
    sid_plain = np.array([snames.index(s) for s in plain])
    sid = np.where(h_id >= 0, sid_plain[t], sid_tri[t])
    for m in sorted(set(h_id.tolist()) & set(over)):
        sid[h_id == m] = snames.index(over[m])
    report["surface_texels"] = {s: int((sid == k).sum()) for k, s in enumerate(snames)}
    # the baked high normal (else the shape's own), sanity-limited
    nh_c = nh.reshape(-1, 3)[idx].astype(np.float64)
    ok = hit.ravel()[idx] & (np.linalg.norm(nh_c, axis=1) > 0.5)
    Nh = np.where(ok[:, None], unit(nh_c), Nl)
    agree = (Nh * Nl).sum(1)
    Nh = np.where(agree[:, None] < 0.0, Nl, Nh)
    blend = smoothstep(0.0, 0.35, agree)[:, None]
    Nh = unit(Nh * blend + Nl * (1 - blend))
    report["normal_bake_hits"] = round(float(ok.mean()), 4) if len(ok) else 1.0
    # brand guard: low-pass the relief of the risky covers
    relief = {}
    risky = np.isin(src, cfg.bake["relief_meshes"])
    if risky.any():
        Nimg = np.zeros((H * W, 3))
        Nimg[idx] = Nh
        mimg = np.zeros(H * W, bool)
        mimg[idx[risky]] = True
        P_img = np.zeros((H * W, 3))
        P_img[idx] = P
        texel = np.median(np.linalg.norm(np.diff(P_img.reshape(H, W, 3), axis=1), axis=-1)[
            cov[:, 1:] & cov[:, :-1]]) if cov.any() else 1.0
        r = max(1, int(round(cfg.bake["relief_radius"] / max(texel, 1e-6))))
        low = unit(masked_blur(Nimg.reshape(H, W, 3), mimg.reshape(H, W), r).reshape(-1, 3))
        for m_id in sorted(set(src[risky].tolist())):
            sel = risky & (src == m_id)
            before = np.degrees(np.arccos(np.clip((Nh[sel] * low[idx[sel]]).sum(1), -1, 1)))
            relief[str(m_id)] = dict(texels=int(sel.sum()), rms_deg=round(float(np.sqrt((before ** 2).mean())), 2),
                                     p99_deg=round(float(np.percentile(before, 99)), 2), radius_px=r)
        Nh[risky] = low[idx[risky]]
    report["relief_flattened"] = relief
    # image-space fields
    P_img = np.zeros((H, W, 3))
    P_img.reshape(-1, 3)[idx] = P
    N_img = np.zeros((H, W, 3))
    N_img.reshape(-1, 3)[idx] = Nh
    s_img = np.full((H, W), -1)
    s_img.reshape(-1)[idx] = sid
    curv, texel = curvature(P_img, N_img, cov, s_img)
    curv = masked_blur(curv, cov, 1, passes=1)
    kc = curv.reshape(-1)[idx]
    report["texel_units"] = round(float(texel / 2), 4)
    report["curvature_p50_p90_p99"] = [round(float(x), 3) for x in np.percentile(kc, [50, 90, 99])] if len(kc) else []
    # AO: a light masked blur takes the sampling noise out (it shows as blotches on bright surfaces: discs, chrome)
    ao_c = np.clip(masked_blur(ao.astype(np.float64), cov, 1, passes=2).reshape(-1)[idx], 0, 1)
    cv_img = masked_blur(cvx.astype(np.float64), cov, 1, passes=1)   # a texel's worth of softening
    cv_c = cv_img.reshape(-1)[idx]
    report["convexity_p1_p50_p99"] = [round(float(x), 3) for x in np.percentile(cv_c, [1, 50, 99])] if len(cv_c) else []
    # outputs (covered texels)
    C = len(idx)
    col = np.zeros((C, 3))
    alpha = np.ones(C)
    spec = np.zeros(C)
    smooth = np.zeros(C)
    Nf = Nh.copy()
    paint_mask = np.zeros(C)
    paint_shade = np.ones(C)
    seed0 = int(sha(label)[:6], 16) % 10000
    for k, sname in enumerate(snames):
        st = cfg.types[sname]
        sel = sid == k
        if not sel.any():
            continue
        p, nl, n_h, a = P[sel], Nl[sel], Nh[sel], ao_c[sel]
        if not st.get("bake_normals", True):   # the mirror glass: its own (convex-bent) normals, not the flat model's
            n_h = nl
        kk = cv_c[sel]   # the high mesh's convexity (scale-free: ~+0.5 on a right-angled edge)
        base = srgb_to_lin(hexrgb(st["colour"]))
        c = np.tile(base, (len(p), 1))
        sp = np.full(len(p), float(st["spec"]))
        sm = np.full(len(p), float(st["smooth"]))
        vary = float(st.get("vary", 0.0))
        if vary:
            v = 2 * fbm(p / 6.0, 3, seed0 + 11 * k) - 1
            c *= (1 + vary * 4 * v)[:, None]
            sm = sm * (1 + 0.5 * vary * v)
        kind = st["kind"]
        if kind == "paint":
            fl = float(st.get("flake", 0.0))
            if fl:
                c *= (1 + fl * (2 * vnoise(p / 0.05, seed0 + 3) - 1))[:, None]
            ps = st.get("pinstripe")
            if ps:
                tank = np.isin(src[sel], ps.get("meshes", []))
                if tank.any():
                    tank_tris = tri[np.isin(shp["src"], ps["meshes"])]
                    if "radius" in ps:   # since the 2026-11-01a build: two offsets of one smooth curve (coachline_v2)
                        line = coachline_v2(p[tank], nl[tank], pos[tank_tris], ps, texel / 2, report)
                    else:
                        field = coachline_field(p[tank], pos[np.unique(tank_tris)])
                        d = field(p[tank][:, 1:3])
                        side = smoothstep(0.35, 0.55, np.abs(nl[tank][:, 0]))
                        hw = float(ps["width"]) / 2
                        aa = max(texel, 1e-3)
                        line = np.zeros(int(tank.sum()))
                        for off in (float(ps["inset"]), float(ps["inset"]) + float(ps["gap"])):
                            line = np.maximum(line, 1 - smoothstep(hw, hw + aa, np.abs(d - off)))
                        line *= side
                    pc = srgb_to_lin(hexrgb(ps["colour"]))
                    ct = c[tank]
                    c[tank] = ct * (1 - line[:, None]) + pc * line[:, None]
                    spt, smt = sp[tank], sm[tank]
                    sp[tank] = spt * (1 - line) + float(ps["spec"]) * line
                    sm[tank] = smt * (1 - line) + float(ps["smooth"]) * line
                    report["pinstripe_texels"] = int((line > 0.5).sum())
        if kind == "disc" and "band" in st:
            ctr = report.get("axle")
            if ctr is not None:
                r = np.hypot(p[:, 1] - ctr[1], p[:, 2] - ctr[2])
                lo, hi = np.percentile(r, 2), np.percentile(r, 99.5)
                bandm = smoothstep(lo + 0.5 * (hi - lo) - 0.3, lo + 0.5 * (hi - lo) + 0.3, r)
                bc = srgb_to_lin(hexrgb(st["band"]["colour"]))
                c = c * (1 - bandm[:, None]) + bc * bandm[:, None]
                ring = np.exp(-((r - (lo + 0.78 * (hi - lo))) / (0.12 * (hi - lo))) ** 2) * 0.12
                tint = srgb_to_lin(hexrgb(st["band"]["tint"]))
                c = c * (1 - ring[:, None]) + tint * ring[:, None]
                sp = sp * (1 - bandm) + float(st["band"]["spec"]) * bandm
                sm = sm * (1 - bandm) + float(st["band"]["smooth"]) * bandm
                pitch = float(st["detail"]["scale"])
                phase = 2 * math.pi * (r / pitch + 0.3 * vnoise(p / 3.0, seed0 + 21))
                radial = np.zeros_like(p)
                radial[:, 1] = (p[:, 1] - ctr[1]) / np.maximum(r, 1e-6)
                radial[:, 2] = (p[:, 2] - ctr[2]) / np.maximum(r, 1e-6)
                g = (np.cos(phase) * float(st["detail"]["amp"]) * (0.4 + 0.6 * bandm))[:, None] * radial
                gt = g - n_h * (g * n_h).sum(1, keepdims=True)
                n_h = unit(n_h - gt)
        if kind == "tyre" and "tread" in st and report.get("axle") is not None:
            ctr = report["axle"]
            r = np.hypot(p[:, 1] - ctr[1], p[:, 2] - ctr[2])
            rm = np.percentile(r, 99.8)
            tm = smoothstep(float(st["tread"]["from"]) * rm, (float(st["tread"]["from"]) + 0.06) * rm, r)
            tc = srgb_to_lin(hexrgb(st["tread"]["colour"]))
            c = c * (1 - tm[:, None]) + tc * tm[:, None]
            sm = sm * (1 - tm) + float(st["tread"]["smooth"]) * tm
        edge = st.get("edge")
        if edge:
            e = smoothstep(float(edge["from"]), float(edge["to"]), kk) * float(edge.get("max", 1.0))
            if "z" in edge:   # a height band (parked units): the engine's cylinders and heads, not the cases below
                z0, z1 = (float(x) for x in edge["z"])
                e = e * smoothstep(z0 - 1.5, z0 + 1.5, p[:, 2]) * (1 - smoothstep(z1 - 1.5, z1 + 1.5, p[:, 2]))
            ec = srgb_to_lin(hexrgb(edge["colour"]))
            c = c * (1 - e[:, None]) + ec * e[:, None]
            sp = sp * (1 - e) + float(edge["spec"]) * e
            sm = sm * (1 - e) + float(edge["smooth"]) * e
            report.setdefault("edge_fraction", {})[sname] = round(float((e > 0.5).mean()), 4)
        wear = st.get("wear")
        if wear:
            e = smoothstep(float(wear["from"]), float(wear["to"]), kk) * float(wear.get("max", 1.0))
            ec = srgb_to_lin(hexrgb(wear["colour"]))
            c = c * (1 - e[:, None]) + ec * e[:, None]
            sm = sm * (1 - e) + float(wear["smooth"]) * e
        ht = st.get("heat")
        if ht:
            ports = heat_ports(cfg, label, shp, ht)
            d = nearest_dist(p, ports)
            tt = np.exp(-d / float(ht["length"])) * float(ht["strength"])
            cols = [srgb_to_lin(hexrgb(x)) for x in ht["colours"]]
            g1 = np.clip(tt * 2, 0, 1)[:, None]
            tint = cols[0] * (1 - g1) + cols[1] * g1
            g2 = np.clip(tt * 2 - 1, 0, 1)[:, None]
            tint = tint * (1 - g2) + cols[2] * g2
            c = c * (1 - tt[:, None]) + tint * tt[:, None] * 0.5
            report["heat_ports"] = int(len(ports))
        # dust in cavities and on upward faces, then the occlusion
        dust = float(st.get("dust", 0.0))
        if dust:
            cav = np.clip((1 - a) * 1.6 - 0.15, 0, 1) * (0.5 + 0.5 * np.clip(nl[:, 2], 0, 1))
            cav = np.maximum(cav, smoothstep(0.08, 0.3, -kk) * 0.6)
            dm = np.clip(dust * cav * (0.7 + 0.6 * vnoise(p / 1.5, seed0 + 31)), 0, 1)
            dc = srgb_to_lin(hexrgb("6e6558"))
            c = c * (1 - dm[:, None]) + dc * dm[:, None]
            sm = sm * (1 - 0.8 * dm)
            sp = sp * (1 - 0.5 * dm)
        aos = float(st.get("ao", 0.85))
        shade = 1 - aos * (1 - a ** 0.9)
        c *= shade[:, None]
        sp *= 1 - float(st.get("ao_spec", 0.5)) * (1 - a)
        if kind == "paint":
            paint_mask[sel] = 1.0
            paint_shade[sel] = shade
        col[sel] = c
        spec[sel] = sp
        smooth[sel] = sm
        if "alpha" in st:
            alpha[sel] = float(st["alpha"]) / 255.0
        Nf[sel] = detail_normals(n_h, p, st.get("detail", {}), seed0 + 101 * k)
    # tangent space, in nifly's frames; flat where the frame is float noise
    nts = NT.encode(Nf, fdu, fdv, fn)
    flat = smoothstep(0.12, 0.3, fcond)[:, None]
    nts = unit(nts * flat + np.array([0.0, 0.0, 1.0]) * (1 - flat))
    report["ill_conditioned_texels"] = round(float((fcond < 0.25).mean()), 5) if len(fcond) else 0.0
    d_img = np.zeros((H, W, 4))
    d_img.reshape(-1, 4)[idx, :3] = lin_to_srgb(col)
    d_img.reshape(-1, 4)[idx, 3] = alpha
    n_img = np.zeros((H, W, 3))
    n_img.reshape(-1, 3)[idx] = nts * 0.5 + 0.5
    s_img2 = np.zeros((H, W, 3))
    s_img2.reshape(-1, 3)[idx, 0] = np.clip(spec, 0, 1)
    s_img2.reshape(-1, 3)[idx, 1] = np.clip(smooth, 0, 1)
    o_img = np.zeros((H, W, 3))
    o_img.reshape(-1, 3)[idx] = Nf * 0.5 + 0.5
    layers = np.zeros((H, W, 2))
    layers.reshape(-1, 2)[idx, 0] = paint_mask
    layers.reshape(-1, 2)[idx, 1] = paint_shade
    px = int(cfg.bake["dilate_px"])
    d_img = dilate_fill(d_img, cov, px)
    n_img = dilate_fill(n_img, cov, px, fill=(0.5, 0.5, 1.0))   # flat beyond the padding: mips stay calm
    s_img2 = dilate_fill(s_img2, cov, px)
    # the normal map's padding: unit vectors
    v = unit(n_img * 2 - 1)
    v[..., 2] = np.maximum(v[..., 2], 0.05)
    n_img = unit(v) * 0.5 + 0.5
    return d_img, n_img, s_img2, o_img, layers


# --- per label pipeline ----------------------------------------------------------------------------------------------

class Cache:
    def __init__(self, cfg, label):
        self.dir = cfg.cache / label
        self.dir.mkdir(parents=True, exist_ok=True)
        self.keys_path = self.dir / "keys.json"
        self.keys = json.loads(self.keys_path.read_text()) if self.keys_path.exists() else {}
        self.force = cfg.args.force

    def valid(self, step, key, *files):
        return (not self.force and self.keys.get(step) == key and all((self.dir / f).exists() for f in files))

    def done(self, step, key):
        self.keys[step] = key
        self.keys_path.write_text(json.dumps(self.keys, indent=1, sort_keys=True) + "\n")


def gltf_hash(path):
    """The glTF and the buffers it names (bytes only)."""
    j = json.loads(Path(path).read_text())
    parts = [Path(path)]
    for b in j.get("buffers", []):
        uri = b.get("uri", "")
        if uri and not uri.startswith("data:") and "/" not in uri and "\\" not in uri and ".." not in uri:
            parts.append(Path(path).parent / uri)
    return sha(*parts)


def label_axle(cfg, label):
    """A wheel's axle (parked frame) from its tyre shape: the middle of the tyre's y/z extent; None off the wheels."""
    if not label.startswith("wheel"):
        return None
    shp = cfg.shape(label[:6] + "_tyre")
    gum = [i for i, n in enumerate(cfg.piece_mats) if n == "gum"]
    tri = shp["tri"][np.isin(shp["mat"], gum)]
    v = shp["pos"][np.unique(tri)]
    return [float((v[:, 0].min() + v[:, 0].max()) / 2), float((v[:, 1].min() + v[:, 1].max()) / 2),
            float((v[:, 2].min() + v[:, 2].max()) / 2)]


def write_uv(cfg, label, uv_nif, extra):
    out = cfg.stage / "uv"
    out.mkdir(parents=True, exist_ok=True)
    np.savez(out / f"{label}.npz", uv=uv_nif.astype(np.float32))
    shp = cfg.shape(label)
    src, _, _ = NT.seam_split(shp["tri"], uv_nif)
    info = {"verts_after_seams": int(len(src)), "mat": cfg.mat_of[label], **extra}
    (out / f"{label}.json").write_text(json.dumps(info, indent=1, sort_keys=True) + "\n")
    return info


def process_label(cfg, scn_box, label, gkey, report):
    """UVs, bakes and authoring of one label (cached step by step). Returns the arrays to write as textures."""
    mat = cfg.mat_of[label]
    shp = cfg.shape(label)
    cache = Cache(cfg, label)
    rep = report.setdefault(label, {})
    t0 = time.time()
    size = cfg.size(mat)
    surf_names = None if cfg.is_art(mat) else cfg.surfaces_of(label, shp)
    # 1. UVs
    fixed = cfg.man["labels"][label].get("uv") == "fixed"
    dens = {s: cfg.types[s].get("density", 1.0) for s in sorted(set(surf_names))} if surf_names else {}
    ukey = sha(cfg.code_uv, "uv", cfg.shape_hash(label), fixed, size, cfg.bake["angle"], cfg.bake["margin_px"], dens)
    if fixed:
        uv_nif = NT.quantise_uv(shp["uv_fixed"].astype(np.float64)).reshape(-1, 3, 2)
        info = write_uv(cfg, label, uv_nif, {"uv": "fixed"})
        rep.update(info)
        return None
    if cache.valid("uv", ukey, "uv.npz"):
        with np.load(cache.dir / "uv.npz") as z:
            uv_nif = z["uv"].astype(np.float64)
        angle = float(json.loads((cache.dir / "uv.json").read_text())["angle"])
    else:
        scn = scn_box()
        angle = float(cfg.bake["angle"])
        t = time.time()
        uv_nif = to_nif_uv(unwrap(scn, label, surf_names, cfg, size, angle))
        src, _, _ = NT.seam_split(shp["tri"], uv_nif)
        if len(src) > cfg.man["labels"][label].get("max_verts", 60000):
            log(f"  {label}: {len(src)} vertices after the seams at {angle} deg: again at {cfg.bake['angle_retry']}")
            angle = float(cfg.bake["angle_retry"])
            uv_nif = to_nif_uv(unwrap(scn, label, surf_names, cfg, size, angle))
        rep["t_unwrap"] = round(time.time() - t, 1)
        np.savez(cache.dir / "uv.npz", uv=uv_nif)
        (cache.dir / "uv.json").write_text(json.dumps({"angle": angle}) + "\n")
        cache.done("uv", ukey)
    if not np.isfinite(uv_nif).all():
        raise ValueError(f"{label}: UVs that aren't numbers")
    # 2. bakes
    occ = sorted(lb for lb in cfg.labels if lb not in OVERLAYS)
    samples = 8 if cfg.quick else int(cfg.bake["ao_samples"])
    bkey = sha(cfg.code_bake, "bake", ukey, gkey, {lb: cfg.shape_hash(lb) for lb in occ}, size, samples,
               {k: cfg.bake[k] for k in ("cage", "ray", "ao_distance", "exclude_meshes", "near_cell", "near_fraction")})
    if cache.valid("bake", bkey, "bake.npz"):
        with np.load(cache.dir / "bake.npz") as z:
            tid, bary, nh, hit, ao = z["tid"], z["bary"].astype(np.float32), z["nh"].astype(np.float32), z["hit"], z["ao"]
            cvx, hid = z["cvx"].astype(np.float32), z["hid"]
        rep.update(json.loads((cache.dir / "bake.json").read_text()))
    else:
        scn = scn_box()
        set_uv(scn, label, uv_nif)
        t = time.time()
        tid, bary = bake_gbuffer(scn, label, size)
        rep["t_gbuffer"] = round(time.time() - t, 1)
        t = time.time()
        highs, highs_i, extra = [], [], []
        if cfg.man["labels"][label]["sources"]:
            scn.load_gltf(cfg.args.gltf)
            highs_i, extra = high_set(scn, cfg, label, shp)
            highs = [scn.highs[i] for i in highs_i]
        oc = ours_copy(scn, label, shp)
        if oc is not None:
            highs.append(oc)
        nh, hit = bake_normals(scn, label, size, highs)
        binfo = {"high_meshes": highs_i, "high_added": extra}
        binfo["t_normals"] = round(time.time() - t, 1)
        t = time.time()
        cvx, cvx_hit, hid = bake_convexity(scn, label, size, highs)
        cvx = np.where(cvx_hit, cvx, 0).astype(np.float16).astype(np.float32)   # exactly what the cache gives back
        bary = bary.astype(np.float16).astype(np.float32)
        nh = nh.astype(np.float16).astype(np.float32)
        if oc is not None:
            scn.bpy.data.objects.remove(oc)
        binfo["t_convexity"] = round(time.time() - t, 1)
        t = time.time()
        ao = bake_ao(scn, label, size, occluders(cfg, scn, label), samples).astype(np.float16).astype(np.float32)
        binfo["t_ao"] = round(time.time() - t, 1)
        binfo["ao_occluders"] = [o.name[4:] for o in occluders(cfg, scn, label)]
        np.savez_compressed(cache.dir / "bake.npz", tid=tid, bary=bary.astype(np.float16), nh=nh.astype(np.float16),
                            hit=hit, ao=ao.astype(np.float16), cvx=np.where(cvx_hit, cvx, 0).astype(np.float16),
                            hid=hid)
        (cache.dir / "bake.json").write_text(json.dumps(binfo, indent=1) + "\n")
        rep.update(binfo)
        cache.done("bake", bkey)
    cov = tid >= 0
    rep["coverage"] = round(float(cov.mean()), 4)
    info = write_uv(cfg, label, uv_nif, {"uv": "unwrap", "angle": angle, "coverage": rep["coverage"], "size": size})
    rep["verts_after_seams"] = info["verts_after_seams"]
    # 3. authoring
    used = sorted(set(surf_names))
    akey = sha(cfg.code_author, "author", bkey, cfg.materials[mat], {s: cfg.types[s] for s in used},
               {k: cfg.bake[k] for k in ("relief_meshes", "relief_radius", "dilate_px")}, cfg.overrides)
    if cache.valid("author", akey, "author.npz"):
        rep.update(json.loads((cache.dir / "author.json").read_text()))
    else:
        t = time.time()
        arep = {"axle": label_axle(cfg, label)}
        d, n, s, o, layers = author(cfg, label, shp, uv_nif, (tid, bary), nh, hit, ao, cvx, hid, arep)
        arep["t_author"] = round(time.time() - t, 1)
        np.savez_compressed(cache.dir / "author.npz", d=to_u8(d), n=to_u8(n), s=to_u8(s), obj_n=to_u8(o),
                            layers=to_u8(layers))
        (cache.dir / "author.json").write_text(json.dumps(arep, indent=1) + "\n")
        rep.update(arep)
        cache.done("author", akey)
    rep["t_total"] = round(time.time() - t0, 1)
    return akey


# --- textures and materials files ------------------------------------------------------------------------------------

def tex_dir(cfg):
    return cfg.args.out / "Textures" / "CMB" / "Bike"


def mat_dir(cfg):
    return cfg.args.out / "Materials" / "CMB" / "Bike"


def dds_jobs_for(cfg, mat, akey_by_label, tmp):
    """The write_dds jobs for one material: from the authored arrays (baked labels) or the art PNGs."""
    m = cfg.materials[mat]
    if m.get("textures_of"):   # another material's set (the rear disc names the front's): nothing of its own
        return []
    out = tex_dir(cfg)
    size, s_size = cfg.size(mat), cfg.s_size(mat)
    jobs = []
    alpha = m.get("alpha") is not None
    if cfg.is_art(mat):
        art = m["art"]
        for slot in ("d", "n", "s", "g"):
            if slot in art:
                src = cfg.art / art[slot]
                if not src.exists():
                    raise FileNotFoundError(f"{mat}: art {src} is missing (bike_art.py --out {cfg.art})")
                inp = str(src)
                if cfg.quick:
                    inp = str(tmp / f"{mat}_{slot}_art.npy")
                    jobs.append(("resize", str(src), inp, size if slot != "s" else s_size))
            elif slot == "n":
                inp = str(tmp / f"{mat}_n_flat.npy")
                np.save(inp, np.tile(np.array([128, 128, 255], np.uint8), (size, size, 1)))
            elif slot == "s":
                fs = m.get("flat_s", [128, 128])
                inp = str(tmp / f"{mat}_s_flat.npy")
                np.save(inp, np.tile(np.array([fs[0], fs[1], 0], np.uint8), (s_size, s_size, 1)))
            else:
                continue
            fmt = {"d": "bc3" if alpha else "bc1", "n": "bc5", "s": "bc5", "g": "bc1"}[slot]
            jobs.append(dict(inputs=[inp], output=str(out / f"{mat}_{slot}.dds"), format=fmt,
                             gamma_mips=slot in ("d", "g"), normal=slot == "n"))
        return jobs
    label = [lb for lb in m["labels"] if cfg.man["labels"][lb].get("uv") != "fixed"]
    if len(label) != 1:
        raise ValueError(f"{mat}: one unwrapped label per baked material ({label})")
    label = label[0]
    with np.load(cfg.cache / label / "author.npz") as z:
        d, n, s = z["d"], z["n"], z["s"]
    if s.shape[0] != s_size:
        f = s.astype(np.float64) / 255
        while f.shape[0] > s_size:
            f = half_size(f)
        s = to_u8(f)
    np.save(tmp / f"{mat}_d.npy", d if alpha else d[..., :3])
    np.save(tmp / f"{mat}_n.npy", n)
    np.save(tmp / f"{mat}_s.npy", s)
    jobs.append(dict(inputs=[str(tmp / f"{mat}_d.npy")], output=str(out / f"{mat}_d.dds"),
                     format="bc3" if alpha else "bc1", gamma_mips=True))
    jobs.append(dict(inputs=[str(tmp / f"{mat}_n.npy")], output=str(out / f"{mat}_n.dds"), format="bc5", normal=True))
    jobs.append(dict(inputs=[str(tmp / f"{mat}_s.npy")], output=str(out / f"{mat}_s.dds"), format="bc5"))
    return jobs


def cube_jobs(cfg):
    jobs = []
    cube = cfg.mats_json.get("cube", {"mirror_cube_e": "mirror_cube"})
    meta = json.loads((cfg.art / "cube.json").read_text())
    for out_name, faces_key in cube.items():
        faces = [str(cfg.art / f) for f in meta["faces"][faces_key]]
        jobs.append(dict(inputs=faces, output=str(tex_dir(cfg) / f"{out_name}.dds"), format="bc1", gamma_mips=True,
                         cube=True))
    return jobs


def run_dds(cfg, jobs, tmp):
    resize = [j for j in jobs if isinstance(j, tuple)]
    real = [j for j in jobs if isinstance(j, dict)]
    if not real:
        return
    script = tmp / "jobs.json"
    script.write_text(json.dumps(real, indent=1))
    pre = ""
    if resize:   # --quick: art scaled down with Pillow in the DDS Python
        spec = json.dumps([list(r[1:]) for r in resize])
        pre = ("import json,numpy as np\nfrom PIL import Image\n"
               f"for src,dst,sz in json.loads({spec!r}):\n"
               "    np.save(dst, np.asarray(Image.open(src).convert('RGBA').resize((sz,sz), Image.LANCZOS), np.uint8))\n")
        subprocess.run([str(cfg.args.dds_python), "-I", "-c", pre], check=True)
    r = subprocess.run([str(cfg.args.dds_python), "-I", str(HERE / "write_dds.py"), "--batch", str(script)],
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"write_dds.py failed:\n{r.stdout}\n{r.stderr}")
    for line in r.stdout.splitlines():
        log("  " + line.replace(str(cfg.args.out), "<Data>"))


def write_bgsm(cfg, mat, cube_path=None, out=None):
    """<mat>.bgsm and <mat>_worn.bgsm; cube_path (a path under Textures) in place of the material's cube, out in place of
    the Data tree's Materials/CMB/Bike (bike_textures.py --mirror-cube: the optional MO2 folder)."""
    import bgsm
    m = cfg.materials[mat]
    out = out or mat_dir(cfg)
    out.mkdir(parents=True, exist_ok=True)
    base = f"CMB\\Bike\\{m.get('textures_of') or mat}"
    env = m["shader"] == "env"
    cube = (cube_path or CUBES.get(m.get("cube"), m.get("cube"))) if env else ""
    if cube and cube.lower().startswith("textures\\"):
        cube = cube[len("textures\\"):]
    written = []
    # A material whose shapes are all the riding bike's alone (the lit overlays, harley_meshes.WORN_ONLY: the manifest's
    # "parked" false) gets no parked file: no nif would name it (one left by an earlier run is taken away).
    parked = any(cfg.man["labels"][lb].get("parked", True) for lb in m["labels"])
    for worn in (False, True):
        if not worn and not parked:
            (out / f"{mat}.bgsm").unlink(missing_ok=True)
            continue
        emit = m.get("emit") if worn else None
        glow = bool(worn and emit and m["shader"] == "glow" and emit.get("glow_map"))
        roles = [cfg.man["labels"][lb].get("role", "") for lb in m["labels"]]
        shadows = bool(m["cast_shadows_worn"] if worn else m["cast_shadows_parked"])
        if worn and any(r in ("front", "fork", "wheelF") for r in roles):
            shadows = False   # as harley_meshes.load_shaders: the riding bike's front end never shadows the lamp
        tex = {"diffuse": base + "_d.dds", "normal": base + "_n.dds", "smoothspec": base + "_s.dds",
               "envmap": cube or "", "glow": base + "_g.dds" if glow else ""}
        kw = dict(textures=tex, environment_mapping=env, env_map_mask_scale=float(m["env_scale"]) if env else 1.0,
                  smoothness=float(m["smoothness"]), specular_mult=float(m["spec_mult"]),
                  specular_color=[float(x) for x in m["spec_colour"]], two_sided=bool(m["two_sided"]),
                  cast_shadows=shadows, receive_shadows=True, emit_enabled=bool(emit), glowmap=glow, root_material="")
        if emit:
            kw.update(emittance_color=[float(x) for x in emit["colour"]], emittance_mult=float(emit["mult"]))
        a = m.get("alpha")
        if a:
            blend = a.get("mode", "blend") == "blend"
            kw.update(alpha_blend=1 if blend else 0, alpha_blend_src=6, alpha_blend_dst=7, alpha_test=True,
                      alpha_test_ref=int(a.get("threshold", 0 if blend else 128)))
        path = out / f"{mat}{'_worn' if worn else ''}.bgsm"
        bgsm.write(path, bgsm.new_bgsm(**kw))
        back = bgsm.read(path)
        if back["textures"]["diffuse"] != tex["diffuse"] or back["emit_enabled"] != bool(emit):
            raise ValueError(f"{path}: read back differs")
        written.append(path.name)
    return written


# --- modes -----------------------------------------------------------------------------------------------------------

def run(cfg):
    args = cfg.args
    only = [x for x in (args.only or "").replace(",", " ").split() if x]
    bad = [x for x in only if x not in cfg.labels]
    if bad:
        raise SystemExit(f"--only: not labels of {cfg.stage}: {bad}")
    labels = only or cfg.labels
    mats = {cfg.mat_of[lb] for lb in labels}
    mats |= {cfg.materials[m]["textures_of"] for m in mats if cfg.materials[m].get("textures_of")}
    mats = sorted(mats, key=lambda m: list(cfg.materials).index(m))
    report_path = cfg.stage / "tex_report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}
    report.setdefault("labels", {})
    box = {}

    def scn_box():
        if "scn" not in box:
            t = time.time()
            box["scn"] = Scene(cfg)
            log(f"  Blender scene: {time.time() - t:.1f} s")
        return box["scn"]
    gkey = gltf_hash(args.gltf) if args.gltf else "no-gltf"
    tmp = cfg.cache / "_dds"
    tmp.mkdir(parents=True, exist_ok=True)
    t_all = time.time()
    for label in labels:
        t = time.time()
        log(f"{label} ({cfg.mat_of[label]})")
        process_label(cfg, scn_box, label, gkey, report["labels"])
        r = report["labels"][label]
        log(f"  done in {time.time() - t:.1f} s: verts after seams {r.get('verts_after_seams')}, coverage "
            f"{r.get('coverage', '-')}, normal hits {r.get('normal_bake_hits', '-')}")
    # textures per material (cached on the authored maps / the art)
    for mat in mats:
        m = cfg.materials[mat]
        if m.get("textures_of"):
            log(f"{mat}: {m['textures_of']}'s textures")
            report.setdefault("materials", {})[mat] = {"bgsm": write_bgsm(cfg, mat), "textures_of": m["textures_of"]}
            continue
        if cfg.is_art(mat):
            arts = [cfg.art / f for f in m["art"].values()]
            dkey = sha(cfg.code_dds, "dds", m, [Path(a) for a in arts], cfg.quick)
        else:
            lb = [x for x in m["labels"] if cfg.man["labels"][x].get("uv") != "fixed"][0]
            dkey = sha(cfg.code_dds, "dds", m, json.loads((cfg.cache / lb / "keys.json").read_text()).get("author"),
                       HERE / "write_dds.py")
        mc = Cache(cfg, f"_mat_{mat}")
        outs = [tex_dir(cfg) / f"{mat}_{s}.dds" for s in ("d", "n", "s")]
        if mc.valid("dds", dkey) and all(p.exists() for p in outs):
            log(f"{mat}: textures up to date")
        else:
            t = time.time()
            run_dds(cfg, dds_jobs_for(cfg, mat, None, tmp), tmp)
            mc.done("dds", dkey)
            log(f"{mat}: textures in {time.time() - t:.1f} s")
        report.setdefault("materials", {})[mat] = {"bgsm": write_bgsm(cfg, mat)}
    if any(cfg.materials[m].get("cube") == "MR" for m in mats):
        faces = json.loads((cfg.art / "cube.json").read_text())["faces"]
        ck = sha(cfg.code_dds, "cube", [cfg.art / f for k in sorted(faces) for f in faces[k]], cfg.mats_json.get("cube"))
        mc = Cache(cfg, "_cube")
        if not (mc.valid("dds", ck) and (tex_dir(cfg) / "mirror_cube_e.dds").exists()):
            run_dds(cfg, cube_jobs(cfg), tmp)
            mc.done("dds", ck)
    # budget
    total = sum(p.stat().st_size for p in tex_dir(cfg).glob("*.dds")) if tex_dir(cfg).exists() else 0
    report["dds_total_bytes"] = total
    report["dds_total_mb"] = round(total / 2 ** 20, 2)
    report["last_run"] = {"labels": labels, "quick": cfg.quick, "seconds": round(time.time() - t_all, 1)}
    report_path.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    log(f"DDS in {tex_dir(cfg)}: {total / 2 ** 20:.2f} MB; run {time.time() - t_all:.1f} s")
    over = [lb for lb, r in report["labels"].items() if r.get("verts_after_seams", 0) > 60000]
    if over:
        raise SystemExit(f"over 60,000 vertices after the seams: {over}")
    return 0


def sheet(cfg, out_png):
    """Decode every DDS written (write_dds.read_dds) and lay them out: per material _d, _n, _s (and _g); also saves
    each baked label's decoded _n to its cache (decoded.npz) for --preview."""
    from PIL import Image, ImageDraw
    import write_dds as WD
    (cfg.cache / "_dds").mkdir(parents=True, exist_ok=True)
    tiles = []
    checks = {}
    for mat, m in cfg.materials.items():
        # A material with no label in this stage (--disc model has no disc labels) is skipped, as --mirror-cube does.
        if not any(lb in cfg.man["labels"] for lb in m["labels"]):
            continue
        row = []
        lbs = [lb for lb in m["labels"] if cfg.man["labels"].get(lb, {}).get("uv") != "fixed"]
        src = None
        if lbs and not cfg.is_art(mat) and (cfg.cache / lbs[0] / "author.npz").exists():
            with np.load(cfg.cache / lbs[0] / "author.npz") as z:
                src = {k: z[k] for k in ("d", "n", "s")}
        for slot in ("d", "n", "s", "g"):
            p = tex_dir(cfg) / f"{mat}_{slot}.dds"
            if not p.exists():
                continue
            info, faces = WD.read_dds(p)
            img = faces[0][0]
            full = 1 + int(math.log2(max(info["w"], info["h"])))
            ck = {"size": info["w"], "format": info["format"], "mips": info["mips"], "full_mips": info["mips"] == full,
                  "bytes": p.stat().st_size}
            if src is not None and slot in src and src[slot].shape[0] == img.shape[0]:
                ch = {"d": [0, 1, 2], "n": [0, 1], "s": [0, 1]}[slot]
                mse = np.mean((img[..., ch].astype(np.float64) - src[slot][..., ch].astype(np.float64)) ** 2)
                ck["psnr_l0"] = 99.0 if mse == 0 else round(float(10 * np.log10(255.0 ** 2 / mse)), 2)
            checks[f"{mat}_{slot}"] = ck
            if slot in ("d", "s", "g"):
                np.save(cfg.cache / "_dds" / f"{mat}_{slot}_decoded.npy", img if slot == "d" else img[..., :3])
            if slot == "n":
                x = img[..., 0].astype(np.float64) / 255 * 2 - 1
                y = img[..., 1].astype(np.float64) / 255 * 2 - 1
                z = np.sqrt(np.clip(1 - x * x - y * y, 0, 1))
                img = np.dstack([img[..., 0], img[..., 1], to_u8(z * 0.5 + 0.5), np.full(x.shape, 255, np.uint8)])
                lbs = [lb for lb in m["labels"] if cfg.man["labels"].get(lb, {}).get("uv") != "fixed"]
                if lbs and not cfg.is_art(mat):
                    np.savez_compressed(cfg.cache / lbs[0] / "decoded.npz", n=img[..., :3])
            if slot == "s":
                img = np.dstack([img[..., 0], img[..., 1], np.zeros_like(img[..., 0]), np.full(img.shape[:2], 255, np.uint8)])
            if slot == "d" and m.get("alpha"):
                a = img[..., 3:4].astype(np.float64) / 255
                chk = ((np.indices(img.shape[:2]).sum(0) // 16) % 2)[..., None] * 60 + 100
                img = np.dstack([to_u8((img[..., :3] * a + chk * (1 - a)) / 255), img[..., 3]])
            row.append((slot, info, Image.fromarray(img[..., :3]).resize((256, 256), Image.LANCZOS)))
        if row:
            tiles.append((mat, row))
    cols = 4
    W, Hh = 256, 256 + 18
    sheet_img = Image.new("RGB", (2 * (cols * W + 10), (len(tiles) + 1) // 2 * Hh + 10), (30, 30, 32))
    dr = ImageDraw.Draw(sheet_img)
    for i, (mat, row) in enumerate(tiles):
        x0 = (i % 2) * (cols * W + 10)
        y0 = (i // 2) * Hh
        for j, (slot, info, im) in enumerate(row):
            sheet_img.paste(im, (x0 + j * W, y0 + 18))
            dr.text((x0 + j * W + 3, y0 + 3), f"{mat}_{slot} {info['w']} {info['format']}", fill=(230, 230, 230))
    sheet_img.save(out_png)
    for p in sorted(tex_dir(cfg).glob("*_e.dds")):
        info, faces = WD.read_dds(p)
        checks[p.stem] = {"size": info["w"], "format": info["format"], "mips": info["mips"], "cube": info["cube"],
                          "bytes": p.stat().st_size}
    (Path(out_png).with_suffix(".json")).write_text(json.dumps(checks, indent=1, sort_keys=True) + "\n")
    bad = [k for k, v in checks.items() if not v.get("full_mips", True) or v.get("psnr_l0", 99) < 30]
    log(f"wrote {out_png}: {len(tiles)} materials; decode checks {Path(out_png).with_suffix('.json')}"
        f"{': FAIL ' + ', '.join(bad) if bad else ' (all full mip chains, PSNR >= 30 dB)'}")
    return 1 if bad else 0


def preview(cfg, out_png):
    """A Cycles look at the textured bike, approximating Fallout 4's lighting shader: base = _d, specular = _s R,
    roughness from _s G, the env-mapped shapes' reflection a glossy layer scaled by _s R x env scale, normals from the
    shipped _n decoded through nifly's frames back to object space (so this also checks the re-encoding)."""
    import bpy
    from mathutils import Vector
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 24 if cfg.quick else 48
    sc.cycles.seed = 0
    sc.cycles.use_denoising = True
    W, H = (int(x) for x in cfg.args.preview_size.split("x"))
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.exposure = -0.6
    w = bpy.data.worlds.new("sky")
    w.use_nodes = True
    sc.world = w
    nt = w.node_tree
    sky = nt.nodes.new("ShaderNodeTexSky")
    try:
        sky.sky_type = "MULTIPLE_SCATTERING"
    except TypeError:
        pass
    sky.sun_elevation = math.radians(38)
    sky.sun_rotation = math.radians(140)
    nt.links.new(sky.outputs[0], nt.nodes["Background"].inputs[0])
    nt.nodes["Background"].inputs[1].default_value = 0.25
    ground = bpy.data.meshes.new("ground")
    ground.from_pydata([(-400, -400, 0), (400, -400, 0), (400, 400, 0), (-400, 400, 0)], [], [(0, 1, 2, 3)])
    g = bpy.data.objects.new("ground", ground)
    sc.collection.objects.link(g)
    gm = bpy.data.materials.new("ground")
    gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.07, 0.068, 0.065, 1)
    gm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
    ground.materials.append(gm)
    hidden = ("rear_tail", "rear_brake", "front_dialglow", "front_mirrorUnderEgg", "front_mirrorUnderD")
    show = [lb for lb in cfg.labels if lb not in hidden]
    images = {}   # the decoded maps --sheet saved (decoding needs texture2ddecoder, which Blender's Python lacks)

    def img_from(arr, name, colour):
        h, w_ = arr.shape[:2]
        im = bpy.data.images.new(name, w_, h, alpha=True, float_buffer=not colour)
        im.colorspace_settings.name = "sRGB" if colour else "Non-Color"
        a = arr.astype(np.float32)
        if a.shape[2] == 3:
            a = np.dstack([a, np.ones(a.shape[:2], np.float32)])
        im.pixels.foreach_set(a[::-1].ravel())
        im.pack()
        return im

    for label in show:
        mat = cfg.mat_of[label]
        m = cfg.materials[mat]
        shp = cfg.shape(label)
        uvf = cfg.stage / "uv" / f"{label}.npz"
        with np.load(uvf) as z:
            uv = z["uv"].astype(np.float64)
        me = bpy.data.meshes.new(label)
        me.from_pydata(shp["pos"].tolist(), [], shp["tri"].tolist())
        me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), bool))
        me.normals_split_custom_set_from_vertices([tuple(x) for x in unit(shp["nrm"].astype(np.float64)).tolist()])
        lay = me.uv_layers.new(name="UVMap")
        b = uv.reshape(-1, 2).copy()
        b[:, 1] = 1 - b[:, 1]
        lay.data.foreach_set("uv", b.ravel())
        o = bpy.data.objects.new(label, me)
        sc.collection.objects.link(o)
        if mat not in images:
            maps = {}
            stem = m.get("textures_of") or mat   # the rear disc's maps are the front's (textures_of)
            for slot in ("d", "s", "g"):
                p = tex_dir(cfg) / f"{stem}_{slot}.dds"
                if p.exists():
                    maps[slot] = np.load(cfg.cache / "_dds" / f"{stem}_{slot}_decoded.npy") if (
                        cfg.cache / "_dds" / f"{stem}_{slot}_decoded.npy").exists() else None
            images[mat] = maps
        # object-space normals: decode the shipped _n through nifly's frames (baked labels only)
        dec = cfg.cache / label / "decoded.npz"
        objn = None
        if dec.exists() and (cfg.cache / label / "bake.npz").exists():
            with np.load(dec) as z:
                ntex = z["n"].astype(np.float64) / 255 * 2 - 1
            with np.load(cfg.cache / label / "bake.npz") as z:
                tid, bary = z["tid"], z["bary"].astype(np.float64)
            Hh, Ww = tid.shape
            if ntex.shape[0] == Hh:
                cov = tid >= 0
                idx = np.nonzero(cov.ravel())[0]
                t = tid.ravel()[idx].astype(np.int64)
                bb = bary.reshape(-1, 2)[idx]
                wgt = np.column_stack([bb, 1 - bb.sum(1)])
                src_v, uv_split, c2v = NT.seam_split(shp["tri"], uv)
                pos, nrm = shp["pos"].astype(np.float64), unit(shp["nrm"].astype(np.float64))
                du, dv, nb, _, _, _ = NT.nifly_frames(pos[src_v], c2v, nrm[src_v], uv_split)
                cc = c2v[t]
                fr = [unit((wgt[:, :, None] * a[cc].astype(np.float64)).sum(1)) for a in (du, dv, nb)]
                nobj = NT.decode(ntex.reshape(-1, 3)[idx], *fr)
                objn = np.zeros((Hh * Ww, 3))
                objn[:] = (0.5, 0.5, 1.0)
                objn[idx] = nobj * 0.5 + 0.5
                objn = dilate_fill(objn.reshape(Hh, Ww, 3), cov, 4)
        mt = bpy.data.materials.new(f"pv_{label}")
        mt.use_nodes = True
        tree = mt.node_tree
        bsdf = tree.nodes["Principled BSDF"]
        out = tree.nodes["Material Output"]
        maps = images[mat]
        top = bsdf.outputs[0]
        nm = None
        if objn is not None:
            tn2 = tree.nodes.new("ShaderNodeTexImage")
            tn2.image = img_from(objn.astype(np.float32), f"{label}_objn", False)
            tn2.interpolation = "Closest" if objn.shape[0] <= 256 else "Linear"
            nm = tree.nodes.new("ShaderNodeNormalMap")
            nm.space = "OBJECT"
            tree.links.new(tn2.outputs["Color"], nm.inputs["Color"])
            tree.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
        tn = None
        if maps.get("d") is not None:
            tn = tree.nodes.new("ShaderNodeTexImage")
            tn.image = img_from(maps["d"].astype(np.float32) / 255, f"{mat}_d", True)
            tree.links.new(tn.outputs["Color"], bsdf.inputs["Base Color"])
        if maps.get("s") is not None:
            ts = tree.nodes.new("ShaderNodeTexImage")
            ts.image = img_from(maps["s"].astype(np.float32) / 255, f"{mat}_s", False)
            sep = tree.nodes.new("ShaderNodeSeparateColor")
            tree.links.new(ts.outputs["Color"], sep.inputs[0])
            inv = tree.nodes.new("ShaderNodeMath")
            inv.operation = "SUBTRACT"
            inv.inputs[0].default_value = 1.0
            tree.links.new(sep.outputs[1], inv.inputs[1])
            rough = tree.nodes.new("ShaderNodeMath")
            rough.operation = "POWER"
            rough.inputs[1].default_value = 1.5
            tree.links.new(inv.outputs[0], rough.inputs[0])
            tree.links.new(rough.outputs[0], bsdf.inputs["Roughness"])
            tree.links.new(sep.outputs[0], bsdf.inputs["Specular IOR Level"])
            if m["shader"] == "env":   # FO4: the cube's reflection x _s red x env scale, added over the lit diffuse
                mul = tree.nodes.new("ShaderNodeMath")
                mul.operation = "MULTIPLY"
                mul.inputs[1].default_value = float(m["env_scale"])
                tree.links.new(sep.outputs[0], mul.inputs[0])
                gl = tree.nodes.new("ShaderNodeBsdfGlossy")
                if m.get("cube") not in ("CH", "MR"):   # the dielectric cube is a dim blur of the sky: a Fresnel stand-in
                    lw = tree.nodes.new("ShaderNodeLayerWeight")
                    lw.inputs["Blend"].default_value = 0.35
                    fm = tree.nodes.new("ShaderNodeMath")
                    fm.operation = "MULTIPLY_ADD"
                    tree.links.new(lw.outputs["Fresnel"], fm.inputs[0])
                    fm.inputs[1].default_value = 0.75
                    fm.inputs[2].default_value = 0.25
                    m2 = tree.nodes.new("ShaderNodeMath")
                    m2.operation = "MULTIPLY"
                    tree.links.new(mul.outputs[0], m2.inputs[0])
                    tree.links.new(fm.outputs[0], m2.inputs[1])
                    mul = m2
                tree.links.new(mul.outputs[0], gl.inputs["Color"])
                tree.links.new(rough.outputs[0], gl.inputs["Roughness"])
                if nm is not None:
                    tree.links.new(nm.outputs["Normal"], gl.inputs["Normal"])
                add = tree.nodes.new("ShaderNodeAddShader")
                tree.links.new(bsdf.outputs[0], add.inputs[0])
                tree.links.new(gl.outputs[0], add.inputs[1])
                top = add.outputs[0]
        if label == "front_glow":
            bsdf.inputs["Emission Color"].default_value = (1, 0.95, 0.9, 1)
            bsdf.inputs["Emission Strength"].default_value = 3.0
        if m.get("alpha") and tn is not None:
            tr = tree.nodes.new("ShaderNodeBsdfTransparent")
            mix = tree.nodes.new("ShaderNodeMixShader")
            tree.links.new(tn.outputs["Alpha"], mix.inputs[0])
            tree.links.new(tr.outputs[0], mix.inputs[1])
            tree.links.new(top, mix.inputs[2])
            top = mix.outputs[0]
        tree.links.new(top, out.inputs[0])
        me.materials.append(mt)
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 50
    cam = bpy.data.objects.new("cam", cam_data)
    sc.collection.objects.link(cam)
    sc.camera = cam
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.0
    sun.data.angle = math.radians(1.5)
    sun.rotation_euler = (math.radians(50), 0, math.radians(140))
    sc.collection.objects.link(sun)
    # parked frame: the front at -y, +x the bike's left
    views = {"front34": ((230, -280, 125), (0, -5, 50)), "rear34": ((-230, 280, 130), (0, 5, 52)),
             "right": ((-330, 0, 70), (0, 0, 50)), "engine_left": ((115, -10, 60), (2, 0, 44)),
             "front_wheel": ((95, -120, 45), (0, -68, 32)), "tank_seat": ((80, 5, 140), (0, 15, 70))}
    only = [v for v in (cfg.args.views or "").split(",") if v]
    if only:
        views = {k: v for k, v in views.items() if k in only}
    shots = []
    for name, (loc, tgt) in views.items():
        cam.location = Vector(loc)
        d = Vector(tgt) - Vector(loc)
        cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        path = str(Path(out_png).with_name(Path(out_png).stem + f"_{name}.png"))
        sc.render.filepath = path
        t = time.time()
        bpy.ops.render.render(write_still=True)
        log(f"  {name}: {time.time() - t:.1f} s -> {path}")
        shots.append(path)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage-dir", type=Path, required=True)
    ap.add_argument("--gltf", type=Path, help="the model's scene.gltf (its geometry is the bake's source)")
    ap.add_argument("--materials", type=Path, default=HERE / "bike_materials.json")
    ap.add_argument("--art", type=Path, help="the parts' art (default: <stage>/art)")
    ap.add_argument("--out", type=Path, required=True, help="the Data tree (Textures/CMB/Bike, Materials/CMB/Bike)")
    ap.add_argument("--dds-python", type=Path, help="a Python with numpy, pillow, quicktex and etcpak (write_dds.py)")
    ap.add_argument("--only", help="labels to do (comma or space separated); the rest is left as it is")
    ap.add_argument("--quick", action="store_true", help="quarter-size maps, 8 AO samples (for trying things)")
    ap.add_argument("--force", action="store_true", help="ignore the cache")
    ap.add_argument("--cache", type=Path, help="default <stage>/tex_cache")
    ap.add_argument("--threads", type=int, default=0, help="Cycles threads (0: all)")
    ap.add_argument("--sheet", type=Path, help="mode: decode the DDS written, a contact sheet PNG (DDS Python)")
    ap.add_argument("--preview", type=Path, help="mode: Cycles renders of the textured bike (Blender Python)")
    ap.add_argument("--preview-size", default="1280x800")
    ap.add_argument("--views", help="--preview: some of front34,rear34,right,engine_left,front_wheel,tank_seat")
    ap.add_argument("--mirror-cube", metavar="GAME_PATH",
                    help="mode: write only the mirror materials' files (cube MR) naming this cube map instead of ours, a "
                         "path under Textures (e.g. Shared\\Cubemaps\\MetalBrushed02Cube_e.dds), into --out's "
                         "Materials/CMB/Bike: the optional MO2 folder \"game mirror cube (A-B)\" (the game's cube by path; "
                         "no game file copied)")
    a = ap.parse_args(argv)
    cfg = Config(a)
    if a.mirror_cube:
        written = []
        for mat, m in cfg.materials.items():
            if m.get("cube") == "MR" and any(lb in cfg.man["labels"] for lb in m["labels"]):
                written += write_bgsm(cfg, mat, cube_path=a.mirror_cube)
        log(f"wrote {len(written)} mirror materials naming {a.mirror_cube} to {mat_dir(cfg)}: {', '.join(written)}")
        return 0
    if a.sheet:
        return sheet(cfg, a.sheet)
    if a.preview:
        return preview(cfg, a.preview)
    if not a.dds_python:
        ap.error("--dds-python is required to write the textures")
    return run(cfg)


if __name__ == "__main__":
    sys.exit(main())
