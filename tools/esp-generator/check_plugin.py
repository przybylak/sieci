#!/usr/bin/env python3
"""Cross-checks the generated plugin against the Papyrus sources.

Reads the generator's --dump output on stdin and the .psc files, and fails if:
  - the plugin sets a property the script doesn't declare (the game ignores it),
  - a Mandatory property isn't filled,
  - a property points at the wrong kind of record (e.g. a Global where an Armor is expected),
  - an engine sound (CMB_Engine*) doesn't play through the plugin's own output model CMB_SOMMonoEngine, or that model
    doesn't read back with the fields the generator writes (since test 45's answer),
  - a bike effect (CMB_Fx*SD, since 2026-11-02a) isn't on CMB_SOMMonoFx with the engine model's fields, or its category,
    static attenuation, loop or files aren't the generator's (FX_SOUNDS), the own lists' slots aren't in order, the
    borrowed lists don't hold the game's 14 records, or any sound plays through another model.

  dotnet run -c Release -- --dump CommonwealthMotorbike.esp | python3 check_plugin.py <Scripts/Source/User>
"""
import re
import sys
from pathlib import Path

# Papyrus property type -> record types (Mutagen class names) that can fill it.
COMPATIBLE = {
    "light": {"Light"},
    "actor": {"PlacedNpc"},
    "objectreference": {"PlacedObject", "PlacedNpc"},
    "globalvariable": {"GlobalFloat", "GlobalInt", "GlobalShort", "GlobalBool"},
    "message": {"Message"},
    "armor": {"Armor"},
    "potion": {"Ingestible"},
    "keyword": {"Keyword"},
    "actorvalue": {"ActorValueInformation"},
    "sound": {"SoundDescriptor"},
    "quest": {"Quest"},
    "formlist": {"FormList"},
    "faction": {"Faction"},
    "spell": {"Spell"},
    "perk": {"Perk"},
    "movablestatic": {"MovableStatic"},
    "soundcategory": {"SoundCategory"},
    "int": {"Int"},
    "bool": {"Bool"},
    "float": {"Float"},
}

# The engine's output model (Program.cs, EngineOutputModel): SOMMono02000 exactly (since test 47: the reverb send 5, the
# static attenuation 0, no output values, the fade-in curve 0/50/80/95) but for the fade-out distances, full level out to
# 600 (past the riding camera) and its 50/20/5/0 curve from there out to 4000. The dump's "sopm" line for it must be this.
ENGINE_MODEL = "CMB_SOMMonoEngine"
ENGINE_MODEL_FIELDS = ("flags AttenuatesWithDistance reverb 5 type UsesHrtf static 0 channels none fade-in 0-0 [0,50,80,95] "
                       "fade-out 600-4000 [50,20,5,0] effect-chain none")
ENGINE_SOUNDS = 13      # the start, the stop, the idle, the cruise and the nine more the plugin drives
# 2026-11-02a (test 48: the landing and water sounds played 13-37 dB under their files): the bike effects' own records over
# the game's files by path (Program.cs, FxOwn), on an output model of their own with the engine model's fields exactly.
# Each: its file count, its first file (the game's own string), its loop; all of them category AudioCategorySFX and a
# static attenuation of 0.
FX_MODEL = "CMB_SOMMonoFx"
FX_MODEL_FIELDS = ENGINE_MODEL_FIELDS
FX_CATEGORY = "0172A1:Fallout4.esm"
FX_SOUNDS = {
    "CMB_FxTyreLightSD": (3, r"data\Sound\FX\PHY\RubberTire\PHY_Rubber_Tire_L_01.wav", "None"),
    "CMB_FxTyreHeavySD": (3, r"data\Sound\FX\PHY\RubberTire\PHY_Rubber_Tire_H_02.wav", "None"),
    "CMB_FxClunkSD": (4, r"data\Sound\FX\PHY\MetalAuto\PHY_Metal_Auto_Medium_H_01.wav", "None"),
    "CMB_FxSplashSD": (2, r"Data\Sound\FX\FST\Water\Land\FST_Water_Jump_Down_01.wav", "None"),
    "CMB_FxSplashHeavySD": (1, r"Data\Sound\FX\PHY\PHY_Water_M_01.wav", "None"),
    "CMB_FxThudHeavySD": (3, r"data\Sound\FX\FST\ArmorPower\FST_ArmorPower_Land_3D_Dirt_02.wav", "None"),
    "CMB_FxClunkBarrelSD": (4, r"data\Sound\FX\PHY\MetalBarrel\PHY_Metal_Barrel_H_01.wav", "None"),
    "CMB_FxSplashMediumSD": (3, r"Data\Sound\FX\PHY\Generic\PHY_Generic_Water_Medium_01.wav", "None"),
    "CMB_FxThudWaterSD": (3, r"data\Sound\FX\FST\ArmorPower\FST_ArmorPower_Land_3D_Water_02.wav", "None"),
    "CMB_FxWaterSprayLPSD": (2, r"data\Sound\FX\AMB\Waterfall\AMB_WaterfallSplatter_Small_02_LP.wav", "Loop"),
    "CMB_FxWaterSprayLargeLPSD": (2, r"data\Sound\FX\AMB\Waterfall\AMB_WaterfallSplatter_Large_01_LP.wav", "Loop"),
    "CMB_FxWaterStreamLPSD": (1, r"fx\amb\water\exterior\amb_water_stream_01_lp.wav", "Loop"),
    "CMB_FxWaterChurnLPSD": (2, r"data\Sound\FX\AMB\Waterfall\AMB_Waterfall_Churn_02_LP.wav", "Loop"),
}
# The lists, slot by slot: ours by EditorID, the borrowed ones (2026-11-01a, kept for the A/B) by the game's FormIDs.
FX_OWN_LISTS = {
    "CMB_FxLandSoundsOwn": ["CMB_FxTyreLightSD", "CMB_FxTyreHeavySD", "CMB_FxClunkSD", "CMB_FxSplashSD", "CMB_FxSplashHeavySD"],
    "CMB_FxLandSoundsAltOwn": ["CMB_FxTyreLightSD", "CMB_FxThudHeavySD", "CMB_FxClunkBarrelSD", "CMB_FxSplashMediumSD", "CMB_FxThudWaterSD"],
    "CMB_FxWaterLoopsOwn": ["CMB_FxWaterSprayLPSD", "CMB_FxWaterSprayLargeLPSD", "CMB_FxWaterStreamLPSD", "CMB_FxWaterChurnLPSD"],
}
FX_BORROWED_LISTS = {
    "CMB_FxLandSounds": ["1D3313", "1D3312", "05BAD7", "03C7A9", "0452CE"],
    "CMB_FxLandSoundsAlt": ["1D3313", "20A0B9", "1A8550", "089380", "20A0B8"],
    "CMB_FxWaterLoops": ["1E4F2D", "1E4F2C", "03D0A7", "1E4F1B"],
}
RECORD = re.compile(r"^  ([0-9A-F]{6}) (\S+)\s+(\S*)\s*$")

PROPERTY = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_:]*(?:\[\])?)\s+Property\s+(\w+)\b(.*)$", re.IGNORECASE)


def parse_scripts(folder: Path):
    scripts = {}
    for psc in folder.glob("*.psc"):
        text = psc.read_text(encoding="utf-8", errors="replace")
        header = re.search(r"^\s*Scriptname\s+(\w+)", text, re.IGNORECASE | re.MULTILINE)
        if not header:
            continue
        props = {}
        for line in text.splitlines():
            m = PROPERTY.match(line.split(";")[0])
            if m and "autoreadonly" not in m.group(3).lower():
                props[m.group(2).lower()] = (m.group(1), "mandatory" in m.group(3).lower(), m.group(2))
        scripts[header.group(1).lower()] = props
    return scripts


def parse_dump(lines):
    attached = []  # (script, {prop: record type})
    for line in lines:
        s = line.strip()
        if s.startswith("script "):
            attached.append((s.split()[1].lower(), {}))
        elif " = " in s and attached:
            name, value = s.split(" = ", 1)
            attached[-1][1][name.lower()] = value.split()[-1]
    return attached


def check_sounds(lines):
    """The engine sounds' output model: (problems, a summary line)."""
    recs, cur = [], None
    for line in lines:
        m = RECORD.match(line)
        if m:
            cur = dict(id=m.group(1), type=m.group(2), edid=m.group(3), model=None, sopm=None)
            recs.append(cur)
        elif cur is not None and line.strip().startswith("output model "):
            cur["model"] = line.split()[2:]
        elif cur is not None and line.strip().startswith("sopm "):
            cur["sopm"] = line.strip()[5:]
        elif cur is not None and line.strip().startswith("sound category "):
            m2 = re.match(r"sound category (\S+) static (\S+) loop (\S+) files (\d+): ?(.*)$", line.strip())
            cur["sound"] = (m2.group(1), m2.group(2), m2.group(3), int(m2.group(4)),
                            m2.group(5).split("; ") if m2.group(5) else []) if m2 else None
        elif cur is not None and line.strip().startswith("item "):
            cur.setdefault("items", []).append(line.split()[1])
    problems = []
    models = [r for r in recs if r["type"] == "SoundOutputModel" and r["edid"] == ENGINE_MODEL]
    if len(models) != 1:
        return [f"{len(models)} SoundOutputModel records named {ENGINE_MODEL}, 1 expected"], ""
    om = models[0]
    if om["sopm"] != ENGINE_MODEL_FIELDS:
        problems.append(f"{ENGINE_MODEL} reads back as\n    {om['sopm']}\n  where the generator writes\n    {ENGINE_MODEL_FIELDS}")
    sounds = [r for r in recs if r["type"] == "SoundDescriptor" and r["edid"].startswith("CMB_Engine")]
    if len(sounds) != ENGINE_SOUNDS:
        problems.append(f"{len(sounds)} engine sounds (CMB_Engine*), {ENGINE_SOUNDS} expected")
    for r in sounds:
        want = [f"{om['id']}:CommonwealthMotorbike.esp", "SoundOutputModel"]
        if r["model"] != want:
            problems.append(f"{r['edid']}: output model {' '.join(r['model'] or ['none'])}, not {ENGINE_MODEL} ({om['id']})")
    line = f"checked {len(sounds)} engine sounds: output model {ENGINE_MODEL} ({om['id']}), its fields as written"
    fx_problems, fx_line = check_fx(recs, om)
    problems += fx_problems
    return problems, line + ("; " + fx_line if fx_line else "")


def check_fx(recs, engine_model):
    """The bike effects' own records (2026-11-02a): (problems, the summary's second half)."""
    by_id = {r["id"]: r for r in recs}
    models = [r for r in recs if r["type"] == "SoundOutputModel" and r["edid"] == FX_MODEL]
    if len(models) != 1:
        return [f"{len(models)} SoundOutputModel records named {FX_MODEL}, 1 expected"], ""
    fm = models[0]
    problems = []
    if fm["sopm"] != FX_MODEL_FIELDS:
        problems.append(f"{FX_MODEL} reads back as\n    {fm['sopm']}\n  where the generator writes\n    {FX_MODEL_FIELDS}")
    sounds = {r["edid"]: r for r in recs if r["type"] == "SoundDescriptor" and r["edid"].startswith("CMB_Fx") and r["edid"].endswith("SD")}
    if set(sounds) != set(FX_SOUNDS):
        problems.append(f"effect sounds {sorted(sounds)}, expected {sorted(FX_SOUNDS)}")
    for edid, (count, first, loop) in FX_SOUNDS.items():
        r = sounds.get(edid)
        if r is None:
            continue
        if r["model"] != [f"{fm['id']}:CommonwealthMotorbike.esp", "SoundOutputModel"]:
            problems.append(f"{edid}: output model {' '.join(r['model'] or ['none'])}, not {FX_MODEL} ({fm['id']})")
        snd = r.get("sound")
        want = (FX_CATEGORY, "0", loop, count, first)
        got = None if snd is None else (snd[0], snd[1], snd[2], snd[3], snd[4][0] if snd[4] else None)
        if got != want or (snd and len(snd[4]) != snd[3]):
            problems.append(f"{edid}: category, static, loop, file count and first file {got}, expected {want}")
    for r in recs:
        if r["type"] != "SoundDescriptor":
            continue
        want = engine_model if r["edid"].startswith("CMB_Engine") else fm if r["edid"] in FX_SOUNDS else None
        if want is None:
            problems.append(f"{r['edid']}: a sound that is neither an engine sound nor a bike effect")
        elif r["model"] != [f"{want['id']}:CommonwealthMotorbike.esp", "SoundOutputModel"]:
            problems.append(f"{r['edid']}: output model {' '.join(r['model'] or ['none'])}, not {want['edid']} ({want['id']})")
    lists = {r["edid"]: r for r in recs if r["type"] == "FormList"}
    for name, slots in FX_OWN_LISTS.items():
        items = (lists.get(name) or {}).get("items")
        got = [by_id.get(i.split(":")[0], {}).get("edid", i) if i.endswith(":CommonwealthMotorbike.esp") else i for i in items or []]
        if got != slots:
            problems.append(f"{name}: {got}, expected {slots}")
    for name, slots in FX_BORROWED_LISTS.items():
        items = (lists.get(name) or {}).get("items")
        want = [f"{s}:Fallout4.esm" for s in slots]
        if items != want:
            problems.append(f"{name}: {items}, expected the game's {want}")
    return problems, (f"checked {len(sounds)} effect sounds: output model {FX_MODEL} ({fm['id']}), static 0, "
                      f"the game's files by path")


def perk_lines(lines):
    """The perks' entry lines, one a perk (2026-11-02a: Steady's two records, CMB_RiderSteadyPerk and CMB_RiderSteadyPerk2)."""
    out, cur = [], None
    for line in lines:
        m = RECORD.match(line)
        if m:
            cur = (m.group(1), m.group(3)) if m.group(2) == "Perk" else None
        elif cur and line.strip().startswith("entry "):
            out.append(f"perk {cur[1]} ({cur[0]}): {line.strip()}")
    return out


def main() -> int:
    scripts = parse_scripts(Path(sys.argv[1]))
    dump = sys.stdin.read().splitlines()
    attached = parse_dump(dump)
    problems, sounds_line = check_sounds(dump)
    if not attached:
        problems.append("no scripts found in the plugin dump")
    for script, props in attached:
        declared = scripts.get(script)
        if declared is None:
            problems.append(f"{script}: attached in the plugin but there is no {script}.psc")
            continue
        for name, record_type in props.items():
            if name not in declared:
                problems.append(f"{script}.{name}: set in the plugin but not declared in the script")
                continue
            ptype = declared[name][0].lower()
            allowed = COMPATIBLE.get(ptype, {"Quest"} if ptype.startswith("cmb_") else set())
            if record_type not in allowed:
                problems.append(f"{script}.{name}: {declared[name][0]} property points at a {record_type}")
        for name, (ptype, mandatory, original) in declared.items():
            if mandatory and name not in props:
                problems.append(f"{script}.{original}: Mandatory but not filled in the plugin")
    for script, props in attached:
        print(f"checked {script}: {len(props)} properties")
    if sounds_line:
        print(sounds_line)
    for line in perk_lines(dump):
        print(line)
    if problems:
        print("PROBLEMS:", *problems, sep="\n  ")
        return 1
    print("plugin and scripts agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
