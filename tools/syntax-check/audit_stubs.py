#!/usr/bin/env python3
"""Compares the hand-written API stubs with real Papyrus sources.

The stubs in stubs/ are written from the Creation Kit wiki; this checks every function
and event they declare against the game's own script sources (and F4SE's), which come
with the Creation Kit or F4SE (F4SE's repository has both under scripts/vanilla and
scripts/modified). Reports declarations that don't exist or whose types differ.

  python audit_stubs.py <folder with the real .psc files> [<another folder> ...]
"""
import glob
import os
import re
import sys

DECL = re.compile(r"(?:([\w\[\]:]+)\s+)?(function|event)\s+([\w.]+)\s*\((.*)\)", re.I)


def declarations(folder):
    """{(script, name): (return type, kind, parameter types)} with continued lines joined."""
    out = {}
    for path in glob.glob(os.path.join(folder, "*.psc")):
        script = os.path.basename(path)[:-4].lower()
        text = open(path, encoding="latin-1").read()
        text = re.sub(r"\\\s*\n", " ", text)        # Papyrus line continuation
        for line in text.splitlines():
            line = line.split(";")[0].strip()
            m = DECL.match(line)
            if not m:
                continue
            ret, kind, name, params = m.groups()
            types = tuple(p.strip().split()[0].lower() for p in params.split(",") if p.strip())
            out[(script, name.lower())] = ((ret or "").lower(), kind.lower(), types, line)
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    real = {}
    for folder in sys.argv[1:]:
        real.update(declarations(folder))
    here = os.path.dirname(os.path.abspath(__file__))
    problems = 0
    for sub in ("vanilla", "f4se"):
        for key, (ret, kind, types, line) in sorted(declarations(os.path.join(here, "stubs", sub)).items()):
            r = real.get(key)
            if r is None:
                print(f"not in the real sources: stubs/{sub}/{key[0]}.psc: {line}")
                problems += 1
            elif (r[0], r[1], r[2]) != (ret, kind, types) and not (
                    # ScriptEventName parameters take a string
                    tuple("string" if t == "scripteventname" else t for t in r[2]) == types and r[:2] == (ret, kind)):
                print(f"differs: stubs/{sub}/{key[0]}.psc\n   stub: {line}\n   real: {r[3]}")
                problems += 1
    print(f"{problems} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
