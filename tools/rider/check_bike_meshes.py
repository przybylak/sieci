#!/usr/bin/env python3
"""Checks a bike build (harley_meshes.py's nifs, and the texture stage's textures and materials) in a Data tree.

  python check_bike_meshes.py --pynifly <io_scene_nifly> --data <Data> [--reference <27c Data>/Meshes/CMB]
      [--stage-dir <stage>]

What it checks (FAIL lines make the exit status 1; INFO lines are numbers for the notes):
  shapes     every worn nif has the 28 shapes of harley_meshes.LABELS, named <stem>_<label>, in that order, skinned;
             the parked nif the vanilla shape (hidden) and ours but the lit overlays (WORN_ONLY), the under-bar mirror
             variants hidden by the node flag; at most MAX_VERTS vertices a shape; every UV in 0..1
  shaders    Fallout 4's flag bits only (no 0x100 in the first word, no 0x8000 in the second), smoothness 0..1, no
             root material, Skinned on the worn shapes only, no shadow from the riding bike's front end
  materials  the shader names all empty (--bgsm 0) or all Materials\\CMB\\Bike\\<mat>[_worn].bgsm, each file there
             and read back by PyNifly's reader, its textures, environment map, glow map, emissive, two-sidedness and
             shadow the same as the nif's own block; no file there that no nif names
  textures   every texture the nifs and materials name is in the Data tree (the vanilla cube maps excepted), each a
             DDS of the format its suffix wants (_d BC1/BC3, _n and _s BC5, _g BC1, cube maps flagged), with every
             mip level (the fallback palette excepted), no BC7; the total size of Textures/CMB/Bike; both mirror
             cubes (mirror_cube_e, which the nifs name, and mirror_cube_zup_e, the one-file swap) in a textured build
  overlays   the dial's backlight, the needle and the light shells clear of what they cover in the worn nif's half
             floats; the needle's culling sphere on NeedlePoint and long enough; where the needle points at rest
  mirrors    every mirror variant clear of the tank with the bars anywhere within BarAngle
  parts      CMB_BikeParts.ini: every key of the reference's the same but FrontMinY (reported), the Needle keys
             there; CMB_BikeFit.json the same bytes as the reference's
  brand      no brand name in any output (the model's credit in CMB_BikeFit.json excepted)
  totals     each shape's vertices and triangles; triangles per material against the reference's (its palette
             UVs say each one's material), with --stage-dir (or the fallback build's palette) split into the model's
             and ours: the model's must equal the reference's but for glTF mesh 9 (the dial face, 24 tex1)
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


def ini_keys(path: Path):
    out = {}
    for line in path.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith(";"):
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pynifly", type=Path, required=True)
    ap.add_argument("--data", type=Path, required=True, help="the Data tree (Meshes/CMB, Textures/CMB, Materials/CMB)")
    ap.add_argument("--reference", type=Path, help="the reference build's Meshes/CMB (27c)")
    ap.add_argument("--stage-dir", type=Path, help="the stage export the build was made from (per-material totals)")
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
    labels = [label for label, _ in H.LABELS]
    roles = dict(H.LABELS)

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
            want_hidden = sorted(["Motorcycle:0"] + [f"CMB_Bike_{label}" for label in H.PARKED_HIDDEN])
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
            if len(uv) and (uv.min() < -1e-4 or uv.max() > 1 + 1e-4):
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
            if worn and roles.get(label) in ("front", "fork", "wheelF") and sf1 & H.SF1_CAST_SHADOWS:
                bad_shadow.append(label)
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
        rep.check(not too_big, f"{stem}: at most {H.MAX_VERTS} vertices a shape", ", ".join(too_big))
        rep.check(not bad_uv, f"{stem}: UVs in 0..1", ", ".join(bad_uv))
        rep.check(not bad_skin, f"{stem}: {'skinned' if worn else 'not skinned'}", ", ".join(bad_skin))
        rep.check(not bad_flags, f"{stem}: Fallout 4 flags, smoothness 0..1, no root material, material names", "; ".join(bad_flags))
        rep.check(not bad_shadow, f"{stem}: {'no shadow from the front end' if worn else 'the lamp unlit'}", ", ".join(bad_shadow))
        rep.check(len(names) <= 1, f"{stem}: material names all set or all empty")

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
        unused = sorted(k for k in ours if "materials\\" + k not in named)
        rep.check(not unused, f"materials files: every one of the {len(ours)} in Materials\\CMB\\Bike named by a nif (none shipped unused)",
                  ", ".join(unused))
        rep.check(not mismatch, "materials files read back (PyNifly) agree with the nifs' blocks", "; ".join(mismatch[:12]))

    # --- textures -----------------------------------------------------------------------------------------------
    vanilla_cubes = {("textures\\" + c).lower() for k, c in H.CUBES.items() if k != "MR"}
    missing_tex, bad_dds, seen = [], [], set()
    for t in sorted({u.lower() for u in used_textures}):
        rel = t.removeprefix("textures\\")
        path = textures.get(rel)
        if path is None:
            if t in vanilla_cubes:
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
        if palette:
            if fmt != "A8R8G8B8":
                bad_dds.append(f"{rel}: {fmt}")
            continue
        if mips != full:
            bad_dds.append(f"{rel}: {mips} of {full} mips")
        if fmt.startswith("DX10:98") or fmt.startswith("DX10:99"):
            bad_dds.append(f"{rel}: BC7")
        if suffix in FOURCC_FOR and fmt not in FOURCC_FOR[suffix]:
            bad_dds.append(f"{rel}: {fmt} for {suffix}")
        if suffix == "_e" and not cube:
            bad_dds.append(f"{rel}: not a cube map")
    rep.check(not missing_tex, f"textures: {len(seen)} named, every one in {args.data / 'Textures'} (vanilla cube maps aside)",
              ", ".join(missing_tex[:12]))
    rep.check(not bad_dds, "textures: DDS formats by suffix, every mip, no BC7", "; ".join(bad_dds[:12]))
    bike_tex = args.data / "Textures" / "CMB" / "Bike"
    if bike_tex.exists():
        total = sum(p.stat().st_size for p in bike_tex.rglob("*.dds"))
        rep.check(total <= 90 * 1024 * 1024, f"textures: Textures/CMB/Bike {total / 1048576:.1f} MB of DDS (budget 90)")
    if not palette_build and named:
        # Both mirror cubes ship: the one the nifs name and the +Z-up one TESTING has the tester copy over it if the
        # game shows the sky sideways (a one-file swap, so the same size and format).
        cubes = {n: textures.get(f"cmb\\bike\\{n}.dds") for n in ("mirror_cube_e", "mirror_cube_zup_e")}
        heads = {n: dds_header(p) if p else None for n, p in cubes.items()}
        same = all(h and h[4] for h in heads.values()) and len({h[:4] for h in heads.values()}) == 1
        rep.check(same, "textures: both mirror cubes there, cube maps of the same size and format",
                  "; ".join(f"{n} {h[:4] if h else 'missing'}" for n, h in heads.items()))

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
        rep.check(False, "the geometry checks (overlays, needle, mirrors, totals, clamp)", "CMB_BikeWorn.nif hasn't the 28 shapes")
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
        if args.stage_dir and (args.stage_dir / "manifest.json").exists():
            manifest = json.loads((args.stage_dir / "manifest.json").read_text())
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
                    expect = -24 if name == "tex1" else 0
                    if d != expect and (ours or name not in ("black_m", "mirror", "dial", "needle", "tail_led", "brake_led")):
                        bad.append(f"{name} {d:+d}")
                split = bool(ours)
                rep.check(not bad, "triangles per material: the model's as the reference's, but glTF mesh 9's 24 tex1"
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
