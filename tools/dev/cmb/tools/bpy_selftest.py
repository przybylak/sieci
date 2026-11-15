#!/usr/bin/env python3
"""Self-test of bpy, the 3D suite as a Python module (Commonwealth Motorbike asset tools), headless, on the CPU.

What tools/rider/bike_textures.py and look_render.py ask of it, each on a few triangles:
  1. import bpy, factory settings, Cycles on the CPU with a fixed seed: a 64x64 render of a cube on a floor
     under a sun, saved as a PNG and read back (lit, not flat)
  2. the same with OpenImageDenoise and the AgX view transform (look_render.py's)
  3. a glTF file read by bpy.ops.import_scene.gltf (bike_textures.py reads the model that way)
  4. UVs by smart_project, average_islands_scale and pack_islands (bike_textures.py's calls) and an
     ambient-occlusion bake into a 64x64 image
  5. the same render twice gives the same pixels
  6. texture2ddecoder imports (look_render.py decodes the DDS textures with it)

    <bpy python> -I bpy_selftest.py --out <folder> [--threads 4]

Exit 0 and a last line "ok".
"""
import argparse
import base64
import json
import struct
import sys
import time
from pathlib import Path

import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    bad = 0

    def check(what, ok):
        nonlocal bad
        print(("  ok   " if ok else "  FAIL ") + what, flush=True)
        bad += 0 if ok else 1

    import bpy
    from mathutils import Vector
    print(f"bpy {bpy.app.version_string} ({bpy.app.build_hash.decode()}, {bpy.app.build_date.decode()}), "
          f"python {sys.version.split()[0]}, numpy {np.__version__}, background {bpy.app.background}")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.seed = 1
    scene.cycles.use_animated_seed = False
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.samples = 16
    scene.cycles.use_denoising = False
    scene.render.threads_mode = "FIXED"
    scene.render.threads = a.threads
    scene.render.resolution_x = scene.render.resolution_y = 64
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "Standard"   # the factory setting is AgX
    check(f"Cycles is the engine, on the {scene.cycles.device}", scene.render.engine == "CYCLES")

    def mesh_object(name, verts, faces):
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts, [], faces)
        me.update()
        ob = bpy.data.objects.new(name, me)
        scene.collection.objects.link(ob)
        return ob

    c = 1.0
    cube = mesh_object("cube", [(-c, -c, 0), (c, -c, 0), (c, c, 0), (-c, c, 0), (-c, -c, 2), (c, -c, 2), (c, c, 2), (-c, c, 2)],
                       [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    floor = mesh_object("floor", [(-6, -6, 0), (6, -6, 0), (6, 6, 0), (-6, 6, 0)], [(0, 1, 2, 3)])
    mat = bpy.data.materials.new("red")
    mat.use_nodes = True   # (deprecated since bpy 5; still needed for the node tree in 5.1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.1, 0.1, 1.0)
    cube.data.materials.append(mat)
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.0
    sun.rotation_euler = (0.9, 0.0, 0.6)
    scene.collection.objects.link(sun)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.location = (6.0, -6.0, 5.0)
    cam.rotation_euler = (Vector((0, 0, 1)) - Vector(cam.location)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cam)
    scene.camera = cam
    world = bpy.data.worlds.new("world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.05, 0.07, 0.1, 1.0)
    scene.world = world

    def render(name):
        path = a.out / name
        scene.render.filepath = str(path)
        t = time.time()
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(str(path))
        px = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], img.channels)
        bpy.data.images.remove(img)
        return px, time.time() - t, path

    px, dt, path = render("render_64.png")
    red = px[..., 0] - px[..., 1]
    check(f"{path.name}: {px.shape[1]}x{px.shape[0]}, {path.stat().st_size} bytes in {dt:.1f} s; brightness "
          f"{px[..., :3].min():.2f}..{px[..., :3].max():.2f}, {int((red > 0.2).sum())} red pixels",
          px.shape[:2] == (64, 64) and px[..., :3].max() > 0.5 and px[..., :3].std() > 0.05 and (red > 0.2).sum() > 100)
    px2, _, _ = render("render_64_again.png")
    check(f"a second render: the largest difference {float(np.abs(px - px2).max()):.4f}", np.array_equal(px, px2))

    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
    scene.cycles.denoising_prefilter = "ACCURATE"
    scene.cycles.denoising_quality = "BALANCED"
    scene.view_settings.view_transform = "AgX"
    den, dt, path = render("render_64_oidn_agx.png")
    check(f"{path.name}: OpenImageDenoise + AgX in {dt:.1f} s, differs from the plain render by "
          f"{float(np.abs(den[..., :3] - px[..., :3]).mean()):.3f} on average",
          scene.cycles.denoiser == "OPENIMAGEDENOISE" and den[..., :3].std() > 0.05
          and float(np.abs(den[..., :3] - px[..., :3]).mean()) > 0.01)
    scene.cycles.use_denoising = False
    scene.view_settings.view_transform = "Standard"

    # a glTF: one triangle, its buffer inline
    pos = struct.pack("<9f", 0, 0, 0, 1, 0, 0, 0, 1, 0)
    idx = struct.pack("<3H", 0, 1, 2) + b"\0\0"
    gltf = dict(asset=dict(version="2.0"), scene=0, scenes=[dict(nodes=[0])], nodes=[dict(mesh=0, name="tri")],
                meshes=[dict(name="tri", primitives=[dict(attributes=dict(POSITION=0), indices=1)])],
                buffers=[dict(byteLength=len(pos) + len(idx),
                              uri="data:application/octet-stream;base64," + base64.b64encode(pos + idx).decode())],
                bufferViews=[dict(buffer=0, byteOffset=0, byteLength=len(pos)),
                             dict(buffer=0, byteOffset=len(pos), byteLength=6)],
                accessors=[dict(bufferView=0, componentType=5126, count=3, type="VEC3", min=[0, 0, 0], max=[1, 1, 0]),
                           dict(bufferView=1, componentType=5123, count=3, type="SCALAR")])
    gpath = a.out / "tri.gltf"
    gpath.write_text(json.dumps(gltf))
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(gpath))
    new = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    check(f"glTF import: {[(o.name, len(o.data.vertices), len(o.data.polygons)) for o in new]}",
          len(new) == 1 and len(new[0].data.vertices) == 3 and len(new[0].data.polygons) == 1)
    for o in new:
        bpy.data.objects.remove(o)

    # UVs and an ambient-occlusion bake on the cube (the floor shades its lower edge)
    bpy.context.view_layer.objects.active = cube
    cube.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    # bike_textures.py's own calls (pack_islands with these arguments takes about 10 s even for six squares: the
    # concave packer tries every rotation; with the operator's defaults it took 47 s here)
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.0, area_weight=0.0, correct_aspect=True,
                             scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.average_islands_scale()
    t = time.time()
    bpy.ops.uv.pack_islands(rotate=True, rotate_method="ANY", scale=True, margin_method="FRACTION", margin=0.02,
                            shape_method="CONCAVE")
    pack_s = time.time() - t
    bpy.ops.object.mode_set(mode="OBJECT")
    uv = np.array([d.uv[:] for d in cube.data.uv_layers.active.data])
    check(f"smart_project + pack_islands ({pack_s:.0f} s): {len(uv)} loop UVs in {uv.min():.2f}..{uv.max():.2f}",
          len(uv) == 24 and uv.min() >= 0 and uv.max() <= 1 and np.ptp(uv, axis=0).min() > 0.5)
    img = bpy.data.images.new("ao", 64, 64, alpha=False, float_buffer=True)
    nodes = mat.node_tree.nodes
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = img
    nodes.active = tex
    scene.cycles.samples = 16
    t = time.time()
    bpy.ops.object.bake(type="AO", margin=2)
    ao = np.array(img.pixels[:], dtype=np.float32).reshape(64, 64, 4)[..., 0]
    check(f"AO bake 64x64 in {time.time() - t:.1f} s: values {ao.min():.2f}..{ao.max():.2f}, mean {ao.mean():.2f}",
          ao.max() > 0.9 and 0.2 < ao.mean() < 0.99 and ao.std() > 0.02)

    try:
        import texture2ddecoder as t2d
        check("texture2ddecoder imports (decode_bc7 there)", hasattr(t2d, "decode_bc7"))
    except ImportError as e:
        check(f"texture2ddecoder: {e}", False)

    print("ok" if not bad else f"{bad} check(s) failed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
