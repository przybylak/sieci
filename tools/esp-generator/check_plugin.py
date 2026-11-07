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
    borrowed lists don't hold the game's 14 records, or any sound plays through another model,
  - (2026-11-06a) the five globals CMB_Slope.dll finds by ID aren't at 0x8B0-0x8B4, or one of the round's nine globals
    hasn't its default,
  - (2026-11-07a, the customisation build) CMB_LookCode isn't at 0x8AF; the look's records don't follow look_options.json
    (each option's swap, object mod and recipe at the table's IDs, with its entries, attach point, components and perk;
    the lists index for index; no source in two slots; every recipe an option's mod on CMB_WorkbenchBike; the look item's
    and the riding armours' attach points, the item's one default template of each slot's option 0; the field kit's
    furnitures; the loose mods); the parked menu's Customise button isn't on CMB_LookOn; the controller's look tables
    don't match the table or a Look_C1 or CMB_LookF4SE property isn't filled; a record is past 0xF00; a line of
    look_ids.txt changed or a record from 0x8BA on isn't in it; or the MCM's Look section isn't the table's.

  dotnet run -c Release -- --dump CommonwealthMotorbike.esp | python3 check_plugin.py <Scripts/Source/User>
"""
import json
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
    # 2026-11-07a (the customisation build): the field kit, the composed swap, the controller's look tables.
    "furniture": {"Furniture"},
    "matswap": {"MaterialSwap"},
    "int[]": {"IntList"},
    "string[]": {"StringList"},
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
    # 2026-11-06a (test 49's check, Q-L: the 2026-11-02a strings named files that aren't in the game): the jump-down
    # files where the game has them, the medium water splash files, and the mod's own wet-road loop (FX\CMB\, relative
    # to Data\Sound as the engine's 13).
    "CMB_FxSplashSD": (2, r"Data\Sound\FX\FST\Player\Water\FST_Water_Jump_Down_01.wav", "None"),
    "CMB_FxSplashHeavySD": (3, r"Data\Sound\FX\PHY\Generic\PHY_Generic_Water_Medium_01.wav", "None"),
    "CMB_FxThudHeavySD": (3, r"data\Sound\FX\FST\ArmorPower\FST_ArmorPower_Land_3D_Dirt_02.wav", "None"),
    "CMB_FxClunkBarrelSD": (4, r"data\Sound\FX\PHY\MetalBarrel\PHY_Metal_Barrel_H_01.wav", "None"),
    "CMB_FxSplashMediumSD": (3, r"Data\Sound\FX\PHY\Generic\PHY_Generic_Water_Medium_01.wav", "None"),
    "CMB_FxThudWaterSD": (3, r"data\Sound\FX\FST\ArmorPower\FST_ArmorPower_Land_3D_Water_02.wav", "None"),
    "CMB_FxWaterSprayLPSD": (2, r"data\Sound\FX\AMB\Waterfall\AMB_WaterfallSplatter_Small_02_LP.wav", "Loop"),
    "CMB_FxWaterSprayLargeLPSD": (2, r"data\Sound\FX\AMB\Waterfall\AMB_WaterfallSplatter_Large_01_LP.wav", "Loop"),
    "CMB_FxWaterRoadLPSD": (1, r"FX\CMB\CMB_FxWaterRoadLP.wav", "Loop"),
    "CMB_FxWaterChurnLPSD": (2, r"data\Sound\FX\AMB\Waterfall\AMB_Waterfall_Churn_02_LP.wav", "Loop"),
}
# The lists, slot by slot: ours by EditorID, the borrowed ones (2026-11-01a, kept for the A/B) by the game's FormIDs.
FX_OWN_LISTS = {
    "CMB_FxLandSoundsOwn": ["CMB_FxTyreLightSD", "CMB_FxTyreHeavySD", "CMB_FxClunkSD", "CMB_FxSplashSD", "CMB_FxSplashHeavySD"],
    "CMB_FxLandSoundsAltOwn": ["CMB_FxTyreLightSD", "CMB_FxThudHeavySD", "CMB_FxClunkBarrelSD", "CMB_FxSplashMediumSD", "CMB_FxThudWaterSD"],
    "CMB_FxWaterLoopsOwn": ["CMB_FxWaterSprayLPSD", "CMB_FxWaterSprayLargeLPSD", "CMB_FxWaterRoadLPSD", "CMB_FxWaterChurnLPSD"],
    # 2026-11-06a: "Landing sounds without metal" (CMB_FxLandDull).
    "CMB_FxLandSoundsDull": ["CMB_FxTyreLightSD", "CMB_FxTyreHeavySD", "CMB_FxThudHeavySD", "CMB_FxSplashSD", "CMB_FxSplashHeavySD",
                             "CMB_FxThudWaterSD"],
}
# The effect sounds that play the mod's own files (shipped loose under Data\Sound\FX\CMB), not the game's.
FX_OWN_FILES = {"CMB_FxWaterRoadLPSD"}
# 2026-11-06a: the five globals CMB_Slope.dll finds by ID (all five or none), and the round's nine globals' values.
FIXED_51 = {"CMB_ViewTip": "0008B0", "CMB_ViewFov": "0008B1", "CMB_ViewEyeForward": "0008B2", "CMB_ViewEyeUp": "0008B3",
            "CMB_FxWaterLoop": "0008B4"}
GLOBALS_51 = {"CMB_ViewTip": "20", "CMB_ViewFov": "0", "CMB_ViewEyeForward": "0", "CMB_ViewEyeUp": "0", "CMB_FxWaterLoop": "2",
              "CMB_KnockOffPower": "0", "CMB_RiderUseOwn": "1", "CMB_FxLandDull": "1", "CMB_FxThudDb": "-11"}
# CMB_LookCode's fixed ID (kept free in 2026-11-06a, made there since 2026-11-07a).
LOOK_CODE_ID = "0008AF"
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
        elif cur is not None and line.strip().startswith("global value "):
            cur["value"] = line.split()[2]
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
    by_edid = {r["edid"]: r for r in recs}
    for name, want_id in FIXED_51.items():
        got = (by_edid.get(name) or {}).get("id")
        if got != want_id:
            problems.append(f"{name}: at {got}, expected {want_id} (CMB_Slope.dll finds it by ID)")
    for name, want_value in GLOBALS_51.items():
        r = by_edid.get(name)
        if r is None or r["type"] != "GlobalFloat" or r.get("value") != want_value:
            problems.append(f"{name}: {None if r is None else (r['type'], r.get('value'))}, expected a GlobalFloat of {want_value}")
    own = sorted(e for e in sounds if e in FX_OWN_FILES)
    return problems, (f"checked {len(sounds)} effect sounds: output model {FX_MODEL} ({fm['id']}), static 0, "
                      f"{len(sounds) - len(own)} the game's files by path and {len(own)} the mod's own ({', '.join(own)})")


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


def check_mcm(scripts_folder: Path):
    """2026-11-06a: the MCM help of "Bike sounds through the mod's own records" names the two controls whose own
    records play whatever it says ("Landing sounds without metal" on, "Water sound loop" past its first choice), and
    both are in the menu under those names."""
    config = scripts_folder.parents[2] / "MCM" / "Config" / "CommonwealthMotorbike" / "config.json"
    controls = {}

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("text"), str) and "help" in o:
                controls[o["text"]] = o["help"]
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(json.loads(config.read_text(encoding="utf-8")))
    own, past = "Bike sounds through the mod's own records", ("Landing sounds without metal", "Water sound loop")
    if own not in controls:
        return [f"MCM: no \"{own}\" control in {config.name}"]
    return [f"MCM: \"{own}\"'s help doesn't name \"{name}\" (its own records play whatever the switch says)"
            for name in past if name not in controls or f'"{name}"' not in controls[own]]


# 2026-11-07a (the customisation build, C1): the look's records against tools/esp-generator/look_options.json (the one
# option table) and look_ids.txt (the save-stable IDs), the controller's look tables, the parked menu's Customise button and
# the MCM's Look section.
HERE = Path(__file__).resolve().parent
LOOK_OPTIONS = HERE / "look_options.json"
LOOK_IDS = HERE / "look_ids.txt"
LOOK_FIRST_ID = 0x8BA          # the look's records: CMB_LookCode at 0x8AF, the rest from here on
ESL_RESERVE_FROM = 0xF00       # no record past it (the light plugin's last IDs stay free)
OURS, GAME = ":CommonwealthMotorbike.esp", ":Fallout4.esm"
LOOK_GLOBALS = {"CMB_LookOn": "1", "CMB_LookFree": "0", "CMB_LookFactionSet": "0", "CMB_KitMode": "0", "CMB_KitWorked": "-1",
                "CMB_KitBagLink": "1"}
# The field kit's three furnitures (custom 6.1, the plan's ladder): model, keywords (ours by EditorID, the game's by ID), marker.
KIT_FURNITURE = {
    "CMB_FieldKit": (r"SetDressing\Toolbox\Toolbox_Large.nif",
                     ["CMB_WorkbenchBike", "0A56D8", "14D04F", "12F848"], "-30,20,0"),
    "CMB_FieldKitArmorKw": (r"SetDressing\Toolbox\Toolbox_Large.nif",
                            ["CMB_WorkbenchBike", "0A56D8", "14D04F", "12F848", "0657FF", "091FD4"], "-30,20,0"),
    "CMB_FieldKitBench": (r"Furniture\Workstations\WorkbenchArmor\WorkstationArmorB01.nif",
                          ["0657FF", "0A56D8", "14D04F", "12F848", "091FD4", "CMB_WorkbenchBike"], "0,0,0"),
}
LOOSE_MOD_MODEL = r"Props\ModsPartBox\ModCrate.nif"
PARKED_MENU = ["Ride", "Open side bag", "Customise", "Cancel"]
RIDING_ARMOURS = ["CMB_BikeRiderArmor", "CMB_BikeRiderArmorFrame"]
LOOK_PATTERNS = {
    "omod": re.compile(r"omod ap (\S+) targets \[(.*?)\] loose (\S+) properties \[(.*?)\] name (.*)$"),
    "cobj": re.compile(r"cobj creates (\S+) bench (\S+) counts \[(.*?)\]$"),
    "component": re.compile(r"component (\S+) (\d+)$"),
    "condition": re.compile(r"condition (\S+) (\S+) (\S+) (\S+) runon (\S+)$"),
    "entry": re.compile(r"entry (\S+) -> (\S+) cnam (\S+)$"),
    "furn": re.compile(r"furn bench (\d+) wbdt (\d+) mnam ([0-9A-F]{8}) markers (\d+) vmad (\S+) keywords \[(.*?)\] model (.*)$"),
    "marker": re.compile(r"marker (\d+) enabled (\S+) offset (\S+) rot (\S+) keyword (\S+) entry ([0-9A-F]{8})$"),
    "armor": re.compile(r"armor playable (\S+) keywords \[(.*?)\] aps \[(.*?)\] model (\S+) preview (\S+) armatures \[(.*?)\] slot (\S+) name (.*)$"),
    "template": re.compile(r"template default (\S+) addon (\S+) includes \[(.*?)\]$"),
    "keyword": re.compile(r"keyword type (\S+) name (.*)$"),
    "misc": re.compile(r"misc model (\S+) preview (\S+) keywords \[(.*?)\] value (\S+) weight (\S+) name (.*)$"),
    "model": re.compile(r"model (\S+) name (.*)$"),
    "button": re.compile(r"button (\d+) conditions (\d+) text (.*)$"),
    "item": re.compile(r"item (\S+) (\S+)$"),
    "global": re.compile(r"global value (\S+)$"),
}


def look_records(lines):
    """The dump's records with their look lines, parsed: [{id, type, edid, <kind>: [match groups...]}]."""
    recs, cur = [], None
    for line in lines:
        m = RECORD.match(line)
        if m:
            cur = dict(id=m.group(1), type=m.group(2), edid=m.group(3), buttons=[])
            recs.append(cur)
            continue
        if cur is None:
            continue
        s = line.strip()
        for kind, pat in LOOK_PATTERNS.items():
            m2 = pat.match(s)
            if m2 and s.startswith(kind if kind not in ("global",) else "global value"):
                if kind == "button":
                    cur["buttons"].append([m2.groups(), []])
                elif kind == "condition" and cur["buttons"]:
                    cur["buttons"][-1][1].append(m2.groups())
                else:
                    cur.setdefault(kind, []).append(m2.groups())
                break
    return recs


def script_values(lines):
    """Every script's property values as the dump prints them: {script: {name: value}} (the last of a name wins)."""
    out, cur = {}, None
    for line in lines:
        s = line.strip()
        if s.startswith("script "):
            cur = out.setdefault(s.split()[1].lower(), {})
        elif cur is not None and " = " in s and not RECORD.match(line):
            name, value = s.split(" = ", 1)
            cur[name] = value
        elif RECORD.match(line):
            cur = None
    return out


def links(text):
    return [x for x in text.split(",") if x]


def look_group(scripts_folder: Path, script, group):
    """The property names of a .psc's Group <group> (or of the whole script with group None)."""
    text = (scripts_folder / f"{script}.psc").read_text(encoding="utf-8", errors="replace")
    if group:
        m = re.search(rf"^\s*Group\s+{group}\b(.*?)^\s*EndGroup", text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        text = m.group(1) if m else ""
    return [m.group(2) for m in (PROPERTY.match(l.split(";")[0]) for l in text.splitlines()) if m]


def check_look(lines, scripts_folder: Path):
    """(problems, the summary line)."""
    table = json.loads(LOOK_OPTIONS.read_text(encoding="utf-8"))
    recs = look_records(lines)
    by_id = {r["id"]: r for r in recs}
    by_edid = {r["edid"]: r for r in recs}
    problems = []

    def rec(edid, rtype):
        r = by_edid.get(edid)
        if r is None or r["type"] != rtype:
            problems.append(f"{edid}: {'missing' if r is None else r['type']}, expected a {rtype}")
            return None
        return r

    def fk(edid):
        r = by_edid.get(edid)
        return f"{r['id']}{OURS}" if r else f"<no {edid}>"

    code = by_id.get(f"{LOOK_CODE_ID}")
    if code is None or code["edid"] != "CMB_LookCode" or code["type"] != "GlobalFloat" or (code.get("global") or [[None]])[0][0] != "0":
        problems.append(f"0x8AF: {None if code is None else (code['edid'], code['type'])}, expected CMB_LookCode, a GlobalFloat of 0 "
                        "(CMB_Slope.dll finds it by ID)")
    for name, value in list(LOOK_GLOBALS.items()) + [(s["global"], str(s["default"])) for s in table["slots"]]:
        r = rec(name, "GlobalFloat")
        if r and (r.get("global") or [[None]])[0][0] != value:
            problems.append(f"{name}: {r.get('global')}, expected {value}")
    ma = rec("CMB_ma_Bike", "Keyword")
    if ma and ma.get("keyword", [[None]])[0][0] != "ModAssociation":
        problems.append(f"CMB_ma_Bike: type {ma.get('keyword')}, expected ModAssociation")
    rec("CMB_WorkbenchBike", "Keyword")
    aps = []
    for s in table["slots"]:
        r = rec(s["ap"], "Keyword")
        if r and r.get("keyword", [[None, None]])[0] != ("AttachPoint", s["name"]):
            problems.append(f"{s['ap']}: {r.get('keyword')}, expected an AttachPoint named {s['name']!r}")
        aps.append(fk(s["ap"]))

    # The options: a swap, an object mod and a recipe each, at the table's IDs, as the table says.
    swaps_total = recipes = loose = 0
    omod_ids, slot_sources = set(), {}
    for s in table["slots"]:
        ap = fk(s["ap"])
        listed = (by_id.get(s["list_id"]) or {}).get("item", [])
        swap_listed = (by_id.get(s["swaps_id"]) or {}).get("item", [])
        if (by_id.get(s["list_id"]) or {}).get("edid") != s["list"] or (by_id.get(s["swaps_id"]) or {}).get("edid") != s["swaps"]:
            problems.append(f"{s['key']}: its lists aren't {s['list']} at {s['list_id']} and {s['swaps']} at {s['swaps_id']}")
        if len(listed) != len(s["options"]):
            problems.append(f"{s['list']}: {len(listed)} entries, {len(s['options'])} options")
        n_swaps = sum(o["swap"] is not None for o in s["options"])
        if len(swap_listed) != n_swaps or any(o["kind"] == "follow" for o in s["options"][:n_swaps]):
            problems.append(f"{s['swaps']}: {len(swap_listed)} entries, expected {n_swaps} (only the last options may be `follow`)")
        for o in s["options"]:
            sw_id, mod_id, co_id = o["ids"]
            name = f"{s['key']}_{o['key']}"
            omod, cobj = by_id.get(mod_id), by_id.get(co_id)
            sw = by_id.get(sw_id) if sw_id else None
            if not omod or omod["edid"] != f"CMB_mod_{name}" or omod["type"] != "ArmorModification" or not omod.get("omod"):
                problems.append(f"CMB_mod_{name}: not at {mod_id}")
                continue
            omod_ids.add(f"{mod_id}{OURS}")
            o_ap, o_targets, o_loose, o_props, o_name = omod["omod"][0]
            want_props = f"MaterialSwaps:Add:{sw_id}{OURS}:0" if sw_id else ""
            want_loose = fk(o["loose"]) if o["loose"] else "none"
            if (o_ap, links(o_targets), o_loose, o_props, o_name) != (ap, [fk("CMB_ma_Bike")], want_loose, want_props, o["name"]):
                problems.append(f"CMB_mod_{name}: ap {o_ap} targets {o_targets} loose {o_loose} properties [{o_props}] name {o_name!r}; "
                                f"expected {ap}, [{fk('CMB_ma_Bike')}], {want_loose}, [{want_props}], {o['name']!r}")
            if o["loose"]:
                loose += 1
            if o["index"] >= len(listed) or listed[o["index"]] != (f"{mod_id}{OURS}", "ArmorModification"):
                problems.append(f"{s['list']}[{o['index']}]: not CMB_mod_{name}")
            if sw_id:
                swaps_total += 1
                entries = [(a, b, "none" if o["cnam"] is None else repr(float(o["cnam"]))) for a, b in o["swap"]]
                got = [(a, b, c if c == "none" else repr(float(c))) for a, b, c in (sw or {}).get("entry", [])]
                if not sw or sw["edid"] != f"CMB_sw_{name}" or got != entries:
                    problems.append(f"CMB_sw_{name} at {sw_id}: {None if not sw else (sw['edid'], got)}, expected {entries}")
                if o["index"] >= len(swap_listed) or swap_listed[o["index"]] != (f"{sw_id}{OURS}", "MaterialSwap"):
                    problems.append(f"{s['swaps']}[{o['index']}]: not CMB_sw_{name} (the object mod's own swap, index for index)")
                for a, _, _ in got:   # the plugin's own entries
                    slot_sources.setdefault(a.lower(), set()).add(s["key"])
            elif o["kind"] != "follow":
                problems.append(f"{s['key']}:{o['key']}: no swap, and not the `follow` kind")
            want_components = [(f"{table['components'][c]}{GAME}", str(n)) for c, n in o["cost"]]
            want_conditions = [("HasPerk", f"{table['perks'][o['perk']]}{GAME}", "EqualTo", "1", "Subject")] if o["perk"] else []
            if not cobj or cobj["edid"] != f"CMB_co_{name}" or cobj.get("cobj") != [(f"{mod_id}{OURS}", fk("CMB_WorkbenchBike"), "1/0")] \
                    or cobj.get("component", []) != want_components or cobj.get("condition", []) != want_conditions:
                problems.append(f"CMB_co_{name} at {co_id}: {None if not cobj else (cobj['edid'], cobj.get('cobj'), cobj.get('component'), cobj.get('condition'))}, "
                                f"expected CMB_mod_{name} on CMB_WorkbenchBike, {want_components}, {want_conditions}")
            else:
                recipes += 1
    shared = {src: sorted(keys) for src, keys in slot_sources.items() if len(keys) > 1}
    if shared:
        problems.append(f"sources in more than one slot (a swap on one would reach the other): {shared}")
    # Every recipe in the plugin: an object mod in a list, on CMB_WorkbenchBike.
    for r in recs:
        if r["type"] == "ConstructibleObject":
            c = (r.get("cobj") or [(None, None, None)])[0]
            if c[0] not in omod_ids or c[1] != fk("CMB_WorkbenchBike"):
                problems.append(f"{r['edid']}: creates {c[0]} on {c[1]}: not a look option's object mod on CMB_WorkbenchBike")
    for name, lists in (("CMB_LookCategories", [s["list_id"] for s in table["slots"]]), ("CMB_LookSwapLists", [s["swaps_id"] for s in table["slots"]])):
        r = rec(name, "FormList")
        if r and r.get("item", []) != [(f"{i}{OURS}", "FormList") for i in lists]:
            problems.append(f"{name}: {r.get('item')}, expected the five lists {lists} in slot order")

    # The look item and the riding armours: the keyword and the five attach points (every object mod's among them); the
    # item playable with one default template, each slot's option 0, one per attach point.
    option0 = [f"{s['options'][0]['ids'][1]}{OURS}@0" for s in table["slots"]]
    for name in ["CMB_BikeLook"] + RIDING_ARMOURS:
        r = rec(name, "Armor")
        if not r or not r.get("armor"):
            continue
        playable, keywords, appr, model, preview, _, _, _ = r["armor"][0]
        if fk("CMB_ma_Bike") not in links(keywords) or links(appr) != aps:
            problems.append(f"{name}: keywords [{keywords}] aps [{appr}], expected CMB_ma_Bike and the five attach points {aps}")
        templates = r.get("template", [])
        if name == "CMB_BikeLook":
            if (playable, model, preview) != ("True", r"CMB\CMB_BikeParked.nif", fk("CMB_BikeLookPreview")):
                problems.append(f"CMB_BikeLook: playable {playable} model {model} preview {preview}, expected a playable item, the parked nif, CMB_BikeLookPreview")
            if len(templates) != 1 or templates[0][0] != "True" or links(templates[0][2]) != option0:
                problems.append(f"CMB_BikeLook: templates {templates}, expected one default with each slot's option 0 {option0}")
        elif playable != "False" or templates:
            problems.append(f"{name}: playable {playable}, templates {templates}: the riding armours stay unplayable, with no template")
    for r in recs:
        if r["type"] == "ArmorModification" and r.get("omod") and r["omod"][0][0] not in aps:
            problems.append(f"{r['edid']}: attach point {r['omod'][0][0]} isn't one of the look item's and the riding armours'")

    # The field kit, its box, the composed swap, the loose mods.
    for name, (model, keywords, marker) in KIT_FURNITURE.items():
        r = rec(name, "Furniture")
        if not r:
            continue
        want_kw = [fk(k) if k.startswith("CMB_") else f"{k}{GAME}" for k in keywords]
        got = (r.get("furn") or [None])[0]
        if got is None or got[:5] != ("7", "1", "40000001", "1", "none") or links(got[5]) != want_kw or got[6] != model \
                or r.get("marker") != [("0", "True", marker, "0", "none", "FFFFFFFF")]:
            problems.append(f"{name}: {got} {r.get('marker')}, expected WBDT 7 (one byte), MNAM 40000001, one marker at {marker} "
                            f"(no keyword, entry points FFFFFFFF), no VMAD, keywords {want_kw}, {model}")
    box = rec("CMB_FieldKitBox", "MovableStatic")
    if box and box.get("model") != [(KIT_FURNITURE["CMB_FieldKit"][0], "Field kit")]:
        problems.append(f"CMB_FieldKitBox: {box.get('model')}, expected the toolbox, named Field kit")
    swap = rec("CMB_LookSwap", "MaterialSwap")
    if swap and swap.get("entry"):
        problems.append("CMB_LookSwap: entries in the plugin (CMB_LookF4SE fills it)")
    for o in (o for s in table["slots"] for o in s["options"] if o["loose"]):
        r = rec(o["loose"], "MiscItem")
        if r and (r.get("misc") or [[None]])[0][:3] != (LOOSE_MOD_MODEL, "248769" + GAME, "135C17" + GAME):
            problems.append(f"{o['loose']}: {r.get('misc')}, expected {LOOSE_MOD_MODEL}, MiscMod01, ObjectTypeLooseMod")

    # The parked menu: Customise (shown while CMB_LookOn is 1) before Cancel.
    menu = rec("CMB_ParkedMenu", "Message")
    if menu:
        texts = [b[0][2] for b in menu["buttons"]]
        conds = [b[1] for b in menu["buttons"]]
        want = [[], [], [("GetGlobalValue", fk("CMB_LookOn"), "EqualTo", "1", "Subject")], []]
        if texts != PARKED_MENU or conds != want:
            problems.append(f"CMB_ParkedMenu: {list(zip(texts, conds))}, expected {PARKED_MENU} with GetGlobalValue CMB_LookOn == 1 on Customise")

    # The controller's look tables and every Look_C1 property filled; CMB_LookF4SE's ten.
    values = script_values(lines)
    ctl = values.get("cmb_controllerscript", {})
    keys = [f"{s['key']}:{o['key']}" for s in table["slots"] for o in s["options"]]
    starts = [sum(len(x["options"]) for x in table["slots"][:i]) for i in range(len(table["slots"]))]
    sets = table["sets"]
    want_arrays = {
        "LookKeys": f"[{','.join(keys)}] StringList",
        "LookSlotStart": f"[{','.join(map(str, starts))}] IntList",
        "LookSetPaint": f"[{','.join(str(-1 if x['paint'] is None else x['paint']) for x in sets)}] IntList",
        "LookSetTank": f"[{','.join(str(-1 if x['tank_left'] is None else x['tank_left']) for x in sets)}] IntList",
        "LookSetFender": f"[{','.join(str(-1 if x['fender'] is None else x['fender']) for x in sets)}] IntList",
    }
    for name, want in want_arrays.items():
        if ctl.get(name) != want:
            problems.append(f"CMB_ControllerScript.{name}: {ctl.get(name)}, expected {want[:120]}")
    if sum(len((by_id.get(s["list_id"]) or {}).get("item", [])) for s in table["slots"]) != len(keys):
        problems.append("LookKeys doesn't count the option lists' entries")
    for script, group, have in (("CMB_ControllerScript", "Look_C1", ctl), ("CMB_LookF4SE", None, values.get("cmb_lookf4se", {}))):
        missing = [p for p in look_group(scripts_folder, script, group) if p not in have]
        if missing:
            problems.append(f"{script}: {', '.join(missing)} not filled in the plugin")

    # The IDs: none past the reserve; look_ids.txt's lines unchanged (a save's look keeps its records), and every record
    # from 0x8BA on (and 0x8AF) in it.
    highest = max(recs, key=lambda r: int(r["id"], 16))["id"] if recs else "000000"
    if int(highest, 16) >= ESL_RESERVE_FROM:
        problems.append(f"{by_id[highest]['edid']} at {highest}: past 0x{ESL_RESERVE_FROM:X} (the light plugin's last IDs stay free)")
    committed = [l.split() for l in LOOK_IDS.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    moved = [f"{e} {i}" for e, i in committed if (by_id.get(i) or {}).get("edid") != e]
    if moved:
        problems.append(f"look_ids.txt: {len(moved)} ID(s) not as committed (save-stable: a later build only appends), the first: "
                        f"{moved[0]} (now {(by_edid.get(moved[0].split()[0]) or {}).get('id')})")
    listed = {i for _, i in committed}
    new = [f"{r['edid']} {r['id']}" for r in recs if (int(r["id"], 16) >= LOOK_FIRST_ID or r["id"] == LOOK_CODE_ID) and r["id"] not in listed]
    if new:
        problems.append(f"look_ids.txt: {len(new)} record(s) not in it (append them: the generator's --look-ids), the first: {new[0]}")

    n_options = sum(len(s["options"]) for s in table["slots"])
    line = (f"checked {n_options} look options in {len(table['slots'])} slots: {swaps_total} swaps, {recipes} recipes on CMB_WorkbenchBike, "
            f"{loose} loose mods, sources {'unique' if not shared else 'SHARED'} per slot, CMB_LookCode {code['id'] if code else 'none'}, "
            f"highest {highest}; look_ids.txt {len(committed)} IDs")
    return problems, line


def check_mcm_look(scripts_folder: Path, lines):
    """The MCM's Look section: its controls in order, each on its global (the plugin's ID) with the table's names."""
    table = json.loads(LOOK_OPTIONS.read_text(encoding="utf-8"))
    config = json.loads((scripts_folder.parents[2] / "MCM" / "Config" / "CommonwealthMotorbike" / "config.json").read_text(encoding="utf-8"))
    ids = {r["edid"]: r["id"] for r in look_records(lines)}
    content = config.get("content", [])
    start = next((i for i, c in enumerate(content) if c.get("type") == "section" and c.get("text") == "Look"), None)
    if start is None:
        return ["MCM: no Look section"], 0
    section = []
    for c in content[start + 1:]:
        if c.get("type") == "section":
            break
        section.append(c)
    names = {s["global"]: [o["name"] for o in s["options"]] for s in table["slots"]}
    sets = [x["name"] for x in table["sets"]]
    want = [("switcher", "Customise at the bike", "CMB_LookOn", None, None),
            ("stepper", "Field kit", "CMB_KitMode", ["Automatic", "Toolbox", "Toolbox (armour bench keyword)", "Armour bench"], None),
            ("switcher", "Parts from the side bag", "CMB_KitBagLink", None, None),
            ("switcher", "Free customising (no field kit, no cost)", "CMB_LookFree", None, "control"),
            ("dropdown", "Tank badge, left", "CMB_Look_TankL", names["CMB_Look_TankL"], "condition"),
            ("dropdown", "Tank badge, right", "CMB_Look_TankR", names["CMB_Look_TankR"], "condition"),
            ("dropdown", "Rear fender badge", "CMB_Look_Fender", names["CMB_Look_Fender"], "condition"),
            ("dropdown", "Paint", "CMB_Look_Paint", names["CMB_Look_Paint"], "condition"),
            ("stepper", "Mirrors", "CMB_Look_Mirrors", names["CMB_Look_Mirrors"], "condition"),
            ("dropdown", "Faction set", "CMB_LookFactionSet", sets, "condition"),
            ("button", "Apply the look", "LookApply", None, "condition")]
    problems = []
    if len(section) != len(want):
        problems.append(f"MCM Look: {len(section)} controls, expected {len(want)}")
    for c, (ctype, text, target, options, group) in zip(section, want):
        vo = c.get("valueOptions", {})
        got_target = (c.get("action") or {}).get("function") if ctype == "button" else vo.get("sourceForm")
        want_target = target if ctype == "button" else f"CommonwealthMotorbike.esp|{int(ids.get(target, '0'), 16):X}"
        got_group = "control" if c.get("groupControl") == 1 else "condition" if c.get("groupCondition") == 1 else None
        if (c.get("type"), c.get("text"), got_target, vo.get("options"), got_group) != (ctype, text, want_target, options, group) \
                or not c.get("help"):
            problems.append(f"MCM Look: {c.get('type')} {c.get('text')!r} on {got_target} options {vo.get('options')} group {got_group}; "
                            f"expected {ctype} {text!r} on {want_target} options {options} group {group}, with a help text")
    return problems, len(section)


def main() -> int:
    scripts = parse_scripts(Path(sys.argv[1]))
    dump = sys.stdin.read().splitlines()
    attached = parse_dump(dump)
    problems, sounds_line = check_sounds(dump)
    problems += check_mcm(Path(sys.argv[1]))
    look_problems, look_line = check_look(dump, Path(sys.argv[1]))
    mcm_problems, mcm_count = check_mcm_look(Path(sys.argv[1]), dump)
    look_problems += mcm_problems
    if len(look_problems) > 20:   # an ESP without the look (2026-11-06a's) fails on every option: the first 20
        look_problems = look_problems[:20] + [f"... and {len(look_problems) - 20} more look problems"]
    problems += look_problems
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
    print(look_line + f"; the MCM's Look section {mcm_count} controls")
    if problems:
        print("PROBLEMS:", *problems, sep="\n  ")
        return 1
    print("plugin and scripts agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
