#!/usr/bin/env python3
"""Cross-checks the generated plugin against the Papyrus sources.

Reads the generator's --dump output on stdin and the .psc files, and fails if:
  - the plugin sets a property the script doesn't declare (the game ignores it),
  - a Mandatory property isn't filled,
  - a property points at the wrong kind of record (e.g. a Global where an Armor is expected).

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
    "spell": {"Spell"},
    "int": {"Int"},
    "bool": {"Bool"},
    "float": {"Float"},
}

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


def main() -> int:
    scripts = parse_scripts(Path(sys.argv[1]))
    attached = parse_dump(sys.stdin.read().splitlines())
    problems = []
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
    if problems:
        print("PROBLEMS:", *problems, sep="\n  ")
        return 1
    print("plugin and scripts agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
