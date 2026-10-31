#!/usr/bin/env python3
"""Read and write Fallout 4 material files: .bgsm (BSLightingShader material) and .bgem (BSEffectShader material).

Fallout 4 writes version 2 of both. The layout follows the field order of PyNifly's reader (pyn/bgsmaterial.py)
and of Material Editor (ousnius) - the version conditions are kept so v1..v22 files read too, but only v2 is
round-trip tested (byte-identical on 16 real v2 BGSM, 1 v1 BGSM and 2 v2 BGEM files). Standard library only.

A material is a dict: 'signature' (b'BGSM'/b'BGEM'), 'version', the fields below by name, and 'textures' (BGSM: diffuse,
normal, smoothspec, greyscale, envmap, glow, innerlayer, wrinkles, displacement for v2; BGEM: base, grayscale, envmap,
normal, envmapmask) plus 'root_material' (BGSM). Texture paths are relative to Data\\Textures (no 'textures\\' prefix),
as in vanilla files. Strings are written NUL-terminated, an empty one as length 1 (as all 170 strings in the real files).

    python3 -I bgsm.py dump file.bgsm
    python3 -I bgsm.py roundtrip a.bgsm b.bgem ...          # read + write, compare bytes
    python3 -I bgsm.py make out.bgsm spec.json               # defaults + the JSON's fields (see new_bgsm)

Fallout 4 semantics worth knowing (docs/DESIGN.md, "The bike's look"): smoothness 0..1 multiplies the _s map's G;
specular_mult the _s map's R; the env map is the cube in textures['envmap'] scaled by env_map_mask_scale;
emit_enabled + emittance_color/emittance_mult light the surface (glow map: glowmap flag + textures['glow']); the game
applies a nif's .bgsm when the shader block's name is the path ('Materials\\...'), and a material swap (OMOD/MSWP)
replaces one .bgsm path by another.
"""
import json
import struct
import sys

# (name, kind, condition(version, material) or None). Kinds: B u8, ?, bool (u8), I u32, f f32, 3f three f32, S string
BASE = [
    ("tile_flags", "I", None), ("uv_offset_u", "f", None), ("uv_offset_v", "f", None),
    ("uv_scale_u", "f", None), ("uv_scale_v", "f", None), ("alpha", "f", None),
    ("alpha_blend", "B", None), ("alpha_blend_src", "I", None), ("alpha_blend_dst", "I", None),
    ("alpha_test_ref", "B", None), ("alpha_test", "?", None), ("zbuffer_write", "?", None), ("zbuffer_test", "?", None),
    ("ssr", "?", None), ("wetness_ssr", "?", None), ("decal", "?", None), ("two_sided", "?", None),
    ("decal_no_fade", "?", None), ("non_occluder", "?", None), ("refraction", "?", None),
    ("refraction_falloff", "?", None), ("refraction_power", "f", None),
    ("environment_mapping", "?", lambda v, m: v < 10), ("env_map_mask_scale", "f", lambda v, m: v < 10),
    ("depth_bias", "?", lambda v, m: v >= 10),
    ("grayscale_to_palette_color", "?", None),
    ("mask_writes", "B", lambda v, m: v >= 6),
]
BGSM_TEX_OLD = ["diffuse", "normal", "smoothspec", "greyscale", "envmap", "glow", "innerlayer", "wrinkles", "displacement"]
BGSM_TEX_NEW = ["diffuse", "normal", "smoothspec", "greyscale", "glow", "wrinkles", "specular", "lighting", "flow"]
BGSM = [
    ("enable_editor_alpha_ref", "?", None),
    ("translucency", "?", lambda v, m: v >= 8), ("translucency_thick_object", "?", lambda v, m: v >= 8),
    ("translucency_mix_albedo", "?", lambda v, m: v >= 8), ("translucency_subsurface_color", "3f", lambda v, m: v >= 8),
    ("translucency_transmissive_scale", "f", lambda v, m: v >= 8), ("translucency_turbulence", "f", lambda v, m: v >= 8),
    ("rim_lighting", "?", lambda v, m: v < 8), ("rim_power", "f", lambda v, m: v < 8),
    ("backlight_power", "f", lambda v, m: v < 8), ("subsurface_lighting", "?", lambda v, m: v < 8),
    ("subsurface_rolloff", "f", lambda v, m: v < 8),
    ("specular_enabled", "?", None), ("specular_color", "3f", None), ("specular_mult", "f", None),
    ("smoothness", "f", None), ("fresnel_power", "f", None),
    ("wet_spec_scale", "f", None), ("wet_spec_power", "f", None), ("wet_min_var", "f", None),
    ("wet_envmap_scale", "f", lambda v, m: v < 10), ("wet_fresnel_power", "f", None), ("wet_metalness", "f", None),
    ("pbr", "?", lambda v, m: v > 2),
    ("custom_porosity", "?", lambda v, m: v >= 9), ("porosity_value", "f", lambda v, m: v >= 9),
    ("root_material", "S", None),
    ("aniso_lighting", "?", None), ("emit_enabled", "?", None),
    ("emittance_color", "3f", lambda v, m: m.get("emit_enabled")),
    ("emittance_mult", "f", None), ("model_space_normals", "?", None), ("external_emittance", "?", None),
    ("lum_emittance", "f", lambda v, m: v >= 12),
    ("use_adaptive_emissive", "?", lambda v, m: v >= 13), ("adaptive_exposure_offset", "f", lambda v, m: v >= 13),
    ("adaptive_final_exposure_min", "f", lambda v, m: v >= 13), ("adaptive_final_exposure_max", "f", lambda v, m: v >= 13),
    ("back_lighting", "?", lambda v, m: v < 8),
    ("receive_shadows", "?", None), ("hide_secret", "?", None), ("cast_shadows", "?", None),
    ("dissolve_fade", "?", None), ("assume_shadowmask", "?", None), ("glowmap", "?", None),
    ("env_map_window", "?", lambda v, m: v < 7), ("env_map_eye", "?", lambda v, m: v < 7),
    ("hair", "?", None), ("hair_tint_color", "3f", None), ("tree", "?", None), ("facegen", "?", None),
    ("skin_tint", "?", None), ("tessellate", "?", None),
    ("displacement_bias", "f", lambda v, m: v < 3), ("displacement_scale", "f", lambda v, m: v < 3),
    ("tessellation_pn_scale", "f", lambda v, m: v < 3), ("tessellation_base_factor", "f", lambda v, m: v < 3),
    ("tessellation_fade_distance", "f", lambda v, m: v < 3),
    ("grayscale_to_palette_scale", "f", None),
    ("skew_specular_alpha", "?", lambda v, m: v >= 1),
    ("terrain", "?", lambda v, m: v >= 3),
    ("terrain_unk_int1", "I", lambda v, m: v == 3 and m.get("terrain")),
    ("terrain_threshold_falloff", "f", lambda v, m: v >= 3 and m.get("terrain")),
    ("terrain_tiling_distance", "f", lambda v, m: v >= 3 and m.get("terrain")),
    ("terrain_rotation_angle", "f", lambda v, m: v >= 3 and m.get("terrain")),
]
BGEM_TEX = ["base", "grayscale", "envmap", "normal", "envmapmask"]
BGEM_TEX_11 = ["specular", "lighting", "glow"]
BGEM = [
    ("environment_mapping", "?", lambda v, m: v >= 10), ("env_map_mask_scale", "f", lambda v, m: v >= 10),
    ("blood_enabled", "?", None), ("effect_lighting", "?", None), ("falloff_enabled", "?", None),
    ("falloff_color_enabled", "?", None), ("grayscale_to_palette_alpha", "?", None), ("soft_enabled", "?", None),
    ("base_color", "3f", None), ("base_color_scale", "f", None),
    ("falloff_start_angle", "f", None), ("falloff_stop_angle", "f", None),
    ("falloff_start_opacity", "f", None), ("falloff_stop_opacity", "f", None),
    ("lighting_influence", "f", None), ("envmap_min_lod", "B", None), ("soft_depth", "f", None),
    ("emittance_color", "3f", lambda v, m: v >= 11),
    ("adaptive_exposure_offset", "f", lambda v, m: v >= 15), ("adaptive_final_exposure_min", "f", lambda v, m: v >= 15),
    ("adaptive_final_exposure_max", "f", lambda v, m: v >= 15),
    ("glowmap", "?", lambda v, m: v >= 16), ("effect_pbr_specular", "?", lambda v, m: v >= 20),
]


class _R:
    def __init__(self, data):
        self.d, self.o = data, 0

    def take(self, fmt):
        v = struct.unpack_from("<" + fmt, self.d, self.o)
        self.o += struct.calcsize("<" + fmt)
        return v

    def string(self):
        (n,) = self.take("I")
        raw = self.d[self.o:self.o + n]
        self.o += n
        return raw


FMT = {"B": "B", "?": "B", "I": "I", "f": "f", "3f": "3f"}


def _read_fields(r, spec, m):
    v = m["version"]
    for name, kind, cond in spec:
        if cond is not None and not cond(v, m):
            continue
        if kind == "S":
            raw = r.string()
            m[name] = raw.rstrip(b"\0").decode("utf-8", "replace")
            m.setdefault("_raw_strings", {})[name] = raw
        else:
            val = r.take(FMT[kind])
            m[name] = list(val) if kind == "3f" else (bool(val[0]) if kind == "?" else val[0])


def _tex_names(m):
    v = m["version"]
    if m["signature"] == b"BGSM":
        if v > 2:
            return BGSM_TEX_NEW + (["distance_field_alpha"] if v >= 17 else [])
        return BGSM_TEX_OLD
    return BGEM_TEX + (BGEM_TEX_11 if v >= 11 else [])


def loads(data: bytes) -> dict:
    r = _R(data)
    sig, version = r.take("4sI")
    if sig not in (b"BGSM", b"BGEM"):
        raise ValueError(f"not a material file: {sig!r}")
    m = {"signature": sig, "version": version}
    _read_fields(r, BASE, m)
    m["textures"], m["_raw_tex"] = {}, {}
    for t in _tex_names(m):
        raw = r.string()
        m["_raw_tex"][t] = raw
        m["textures"][t] = raw.rstrip(b"\0").decode("utf-8", "replace")
    _read_fields(r, BGSM if sig == b"BGSM" else BGEM, m)
    if r.o != len(data):
        m["_trailing"] = data[r.o:]
    return m


def _pack_string(s, raw=None):
    if raw is not None and raw.rstrip(b"\0").decode("utf-8", "replace") == s:
        return struct.pack("<I", len(raw)) + raw   # keep the file's own encoding of it
    b = s.encode("utf-8") + b"\0"   # vanilla: every string NUL-terminated, an empty one is length 1
    return struct.pack("<I", len(b)) + b


def _write_fields(spec, m):
    out = b""
    v = m["version"]
    for name, kind, cond in spec:
        if cond is not None and not cond(v, m):
            continue
        val = m[name]
        if kind == "S":
            out += _pack_string(val, m.get("_raw_strings", {}).get(name))
        elif kind == "3f":
            out += struct.pack("<3f", *val)
        else:
            out += struct.pack("<" + FMT[kind], int(val) if kind in ("?", "B", "I") else float(val))
    return out


def dumps(m: dict) -> bytes:
    out = struct.pack("<4sI", m["signature"], m["version"]) + _write_fields(BASE, m)
    raw = m.get("_raw_tex", {})
    for t in _tex_names(m):
        out += _pack_string(m["textures"].get(t, ""), raw.get(t))
    out += _write_fields(BGSM if m["signature"] == b"BGSM" else BGEM, m)
    return out + m.get("_trailing", b"")


def read(path):
    with open(path, "rb") as f:
        return loads(f.read())


def write(path, m):
    with open(path, "wb") as f:
        f.write(dumps(m))


BASE_DEFAULTS = dict(tile_flags=3, uv_offset_u=0.0, uv_offset_v=0.0, uv_scale_u=1.0, uv_scale_v=1.0, alpha=1.0,
                     alpha_blend=0, alpha_blend_src=6, alpha_blend_dst=7, alpha_test_ref=128, alpha_test=False,
                     zbuffer_write=True, zbuffer_test=True, ssr=False, wetness_ssr=False, decal=False, two_sided=False,
                     decal_no_fade=False, non_occluder=False, refraction=False, refraction_falloff=False,
                     refraction_power=0.0, environment_mapping=False, env_map_mask_scale=1.0, depth_bias=False,
                     grayscale_to_palette_color=False, mask_writes=63)


def new_bgsm(**kw) -> dict:
    """A v2 BGSM with Material Editor-like defaults (an opaque, shadow-casting, specular surface); kw override."""
    m = dict(signature=b"BGSM", version=2, **BASE_DEFAULTS)
    m.update(textures={t: "" for t in BGSM_TEX_OLD}, enable_editor_alpha_ref=False,
             rim_lighting=False, rim_power=2.0, backlight_power=0.0, subsurface_lighting=False, subsurface_rolloff=0.3,
             specular_enabled=True, specular_color=[1.0, 1.0, 1.0], specular_mult=1.0, smoothness=1.0, fresnel_power=5.0,
             wet_spec_scale=-1.0, wet_spec_power=-1.0, wet_min_var=-1.0, wet_envmap_scale=-1.0, wet_fresnel_power=-1.0,
             wet_metalness=-1.0, root_material="", aniso_lighting=False, emit_enabled=False,
             emittance_color=[1.0, 1.0, 1.0], emittance_mult=1.0, model_space_normals=False, external_emittance=False,
             back_lighting=False, receive_shadows=True, hide_secret=False, cast_shadows=True, dissolve_fade=False,
             assume_shadowmask=False, glowmap=False, env_map_window=False, env_map_eye=False, hair=False,
             hair_tint_color=[0.5, 0.5, 0.5], tree=False, facegen=False, skin_tint=False, tessellate=False,
             displacement_bias=-0.5, displacement_scale=10.0, tessellation_pn_scale=1.0, tessellation_base_factor=1.0,
             tessellation_fade_distance=0.0, grayscale_to_palette_scale=1.0, skew_specular_alpha=False)
    tex = kw.pop("textures", {})
    m.update(kw)
    m["textures"].update(tex)
    return m


def new_bgem(**kw) -> dict:
    """A v2 BGEM (effect shader: glass, lens glow) with defaults; kw override."""
    m = dict(signature=b"BGEM", version=2, **BASE_DEFAULTS)
    m.update(textures={t: "" for t in BGEM_TEX}, blood_enabled=False, effect_lighting=False, falloff_enabled=False,
             falloff_color_enabled=False, grayscale_to_palette_alpha=False, soft_enabled=False,
             base_color=[1.0, 1.0, 1.0], base_color_scale=1.0, falloff_start_angle=1.0, falloff_stop_angle=1.0,
             falloff_start_opacity=0.0, falloff_stop_opacity=0.0, lighting_influence=1.0, envmap_min_lod=0,
             soft_depth=100.0)
    tex = kw.pop("textures", {})
    m.update(kw)
    m["textures"].update(tex)
    return m


def _public(m):
    return {k: (v.decode() if isinstance(v, bytes) else v) for k, v in m.items() if not k.startswith("_")}


def main(argv):
    if len(argv) >= 2 and argv[0] == "dump":
        for p in argv[1:]:
            print(p, json.dumps(_public(read(p)), indent=1))
        return 0
    if len(argv) >= 2 and argv[0] == "roundtrip":
        bad = 0
        for p in argv[1:]:
            data = open(p, "rb").read()
            m = loads(data)
            again = dumps(m)
            clean = {k: v for k, v in m.items() if not k.startswith("_")}   # without the raw-string memory
            ok, ok2 = again == data, dumps(clean) == data
            bad += not ok
            print(f"{'OK ' if ok else 'BAD'} {'clean-identical' if ok2 else 'clean-differs'} v{m['version']} "
                  f"{m['signature'].decode()} {len(data)}B {p}")
        return 1 if bad else 0
    if len(argv) == 3 and argv[0] == "make":
        spec = json.load(open(argv[2]))
        kind = spec.pop("kind", "bgsm")
        m = new_bgsm(**spec) if kind == "bgsm" else new_bgem(**spec)
        write(argv[1], m)
        print(f"wrote {argv[1]} ({len(dumps(m))} bytes)")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
