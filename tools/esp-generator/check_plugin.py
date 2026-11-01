#!/usr/bin/env python3
"""Cross-checks the generated plugin against the Papyrus sources.

Reads the generator's --dump output on stdin and the .psc files, and fails if:
  - the plugin sets a property the script doesn't declare (the game ignores it),
  - a Mandatory property isn't filled,
  - a property points at the wrong kind of record (e.g. a Global where an Armor is expected),
  - an engine sound (CMB_Engine*) doesn't play through the plugin's own output model CMB_SOMMonoEngine, or that model
    doesn't read back with the fields the generator writes (since test 45's answer).

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
    return problems, f"checked {len(sounds)} engine sounds: output model {ENGINE_MODEL} ({om['id']}), its fields as written"


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
    if problems:
        print("PROBLEMS:", *problems, sep="\n  ")
        return 1
    print("plugin and scripts agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
