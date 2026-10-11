#!/usr/bin/env python3
"""Builds CMB_RiderPose.esm, the plugin behind the seated riding animations.

While you ride, the controller script puts the CMB_AnimFlavorRider keyword on
the player (ChangeAnimFlavor). The plugin's additive race adds subgraph entries
to HumanRaceSubGraphData, the same way the DLCs add theirs: one copy of each of
the player's third-person MT (weapon holstered) entries, with the keyword added
and the riding clip folder searched first:

    Actors\\Character\\Animations\\MT\\CMB_Rider\\          (Female\\ first for female entries)
    ...then the entry's own folders, so anything without a riding version
       (jumping, swimming, staggering) plays as usual

The game uses the entry whose keywords all match and that matches the most of
them, so these only win while the keyword is on. HumanRace is not edited, so
LooksMenu, LooksMenu Customization Compendium and other race mods keep working
without a patch, whatever the load order.

The entries are copied from your own Fallout4.esm because their folder lists
can't be redistributed or guessed. The rest of the plugin (keyword, race) comes
from template/CMB_RiderPose.esm, written by tools/esp-generator.

  python make_rider_plugin.py --fallout4 "<Fallout 4>\\Data\\Fallout4.esm" --out "<mod folder>\\CMB_RiderPose.esm"

Then generate the animation data (see generate_anim_info.bat). Standard library only.
"""

import argparse
import struct
import sys
import zlib
from pathlib import Path

PLUGIN_NAME = "CMB_RiderPose.esm"
FLAVOR_EDID = "CMB_AnimFlavorRider"
RACE_EDID = "CMB_RiderSubgraphData"
PLACEHOLDER_GRAPH = b"CMB_TEMPLATE_PLACEHOLDER\0"
RIDER_FOLDER = "Actors\\Character\\Animations\\MT\\CMB_Rider\\"

HUMAN_RACE = 0x013746
ANIM_ARCHETYPE_PLAYER = 0x06B508
KEYWORD_TYPE_ANIM_GENDER = 14

ROLES = {0: "MT", 1: "Weapon", 2: "Furniture", 3: "Idle", 4: "Pipboy"}
SUBGRAPH_TYPES = {b"SAKD", b"SGNM", b"SAPT", b"STKD", b"SRAF"}
FLAG_COMPRESSED = 0x40000


# --------------------------------------------------------------------------
# Reading plugins
# --------------------------------------------------------------------------

def subrecords(data: bytes):
    """Record data -> [(type, bytes)], resolving XXXX size overrides."""
    out, i, big = [], 0, None
    while i < len(data):
        t = data[i:i + 4]
        size = struct.unpack_from("<H", data, i + 4)[0]
        i += 6
        if t == b"XXXX":
            big = struct.unpack_from("<I", data, i)[0]
            i += size
            continue
        if big is not None:
            size, big = big, None
        out.append((t, data[i:i + size]))
        i += size
    return out


def pack_subrecords(subs) -> bytes:
    out = bytearray()
    for t, d in subs:
        if len(d) > 0xFFFF:
            out += b"XXXX" + struct.pack("<HI", 4, len(d)) + t + struct.pack("<H", 0)
        else:
            out += t + struct.pack("<H", len(d))
        out += d
    return bytes(out)


def u32(b: bytes) -> int:
    return struct.unpack("<I", b)[0]


def cstr(b: bytes) -> str:
    return b.rstrip(b"\0").decode("cp1252")


class Plugin:
    def __init__(self, path: Path):
        self.path = path
        with open(path, "rb") as f:
            head = f.read(24)
            if head[:4] != b"TES4":
                raise SystemExit(f"{path} is not a Fallout 4 plugin")
            size, self.flags = struct.unpack_from("<II", head, 4)
            self.header = head + f.read(size)
        self.masters = [cstr(d) for t, d in subrecords(self.header[24:]) if t == b"MAST"]

    def groups(self):
        """Yields (label, group bytes) for each top-level group."""
        with open(self.path, "rb") as f:
            f.seek(len(self.header))
            while True:
                gh = f.read(24)
                if len(gh) < 24:
                    return
                size = struct.unpack_from("<I", gh, 4)[0]
                yield gh[8:12], gh + f.read(size - 24)

    def records(self, rtype: bytes):
        """Yields (header, decompressed data) for every record in the top-level group rtype."""
        for label, group in self.groups():
            if label != rtype:
                continue
            i = 24
            while i < len(group):
                if group[i:i + 4] == b"GRUP":
                    i += struct.unpack_from("<I", group, i + 4)[0]
                    continue
                size, flags = struct.unpack_from("<II", group, i + 4)
                data = group[i + 24:i + 24 + size]
                if flags & FLAG_COMPRESSED:
                    data = zlib.decompress(data[4:])
                yield group[i:i + 24], data
                i += 24 + size

    def record(self, rtype: bytes, form_id: int):
        return next(((h, d) for h, d in self.records(rtype) if struct.unpack_from("<I", h, 12)[0] == form_id), None)


# --------------------------------------------------------------------------
# Subgraph entries
# --------------------------------------------------------------------------

def entry_ranges(subs):
    """[start, end) of each subgraph entry: a run of SAKD/SGNM/SAPT/STKD closed by SRAF."""
    ranges, start = [], None
    for i, (t, _) in enumerate(subs):
        if t in SUBGRAPH_TYPES and start is None:
            start = i
        if t == b"SRAF" and start is not None:
            ranges.append((start, i + 1))
            start = None
    return ranges


def describe(entry):
    keywords = [u32(d) for t, d in entry if t == b"SAKD"]
    graph = next((cstr(d) for t, d in entry if t == b"SGNM"), "")
    paths = [cstr(d) for t, d in entry if t == b"SAPT"]
    role, perspective = struct.unpack_from("<HH", next(d for t, d in entry if t == b"SRAF"))
    return keywords, graph, paths, role, perspective


def riding_copy(entry, flavor_id: int, female: bool):
    """The entry with the flavour keyword added and the riding folder(s) searched first."""
    paths = [cstr(d) for t, d in entry if t == b"SAPT"]
    style = paths[0] if paths else RIDER_FOLDER
    lead = style[:style.lower().find("actors\\")] if "actors\\" in style.lower() else ""
    first = [lead + RIDER_FOLDER + "Female\\", lead + RIDER_FOLDER] if female else [lead + RIDER_FOLDER]
    if not style.endswith("\\"):
        first = [p.rstrip("\\") for p in first]
    last_kw = max((i for i, (t, _) in enumerate(entry) if t == b"SAKD"), default=-1)
    out, added_paths = [], False
    if last_kw < 0:
        out.append((b"SAKD", struct.pack("<I", flavor_id)))
    for i, (t, d) in enumerate(entry):
        if t in (b"SAPT", b"SRAF") and not added_paths:
            out += [(b"SAPT", p.encode("cp1252") + b"\0") for p in first]
            added_paths = True
        out.append((t, d))
        if i == last_kw:
            out.append((b"SAKD", struct.pack("<I", flavor_id)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fallout4", type=Path, required=True, help="the game's Data\\Fallout4.esm")
    ap.add_argument("--out", type=Path, required=True, help=f"where to write {PLUGIN_NAME}")
    ap.add_argument("--template", type=Path, default=Path(__file__).resolve().parent / "template" / PLUGIN_NAME)
    args = ap.parse_args()
    if args.out.name != PLUGIN_NAME:
        raise SystemExit(f"the plugin must be called {PLUGIN_NAME} (the controller script looks for that name)")

    game = Plugin(args.fallout4)
    if game.masters:
        raise SystemExit(f"{args.fallout4} has masters; pass the game's own Fallout4.esm")
    human = game.record(b"RACE", HUMAN_RACE)
    if not human:
        raise SystemExit("HumanRace not found; is this Fallout4.esm?")
    # HumanRace takes its animation setup from a template race (HumanRaceSubGraphData).
    template_race = next((u32(d) for t, d in subrecords(human[1]) if t == b"SRAC"), HUMAN_RACE)
    source = game.record(b"RACE", template_race)
    source_subs = subrecords(source[1])
    source_edid = next((cstr(d) for t, d in source_subs if t == b"EDID"), f"{template_race:08X}")
    keyword_types = {struct.unpack_from("<I", h, 12)[0]: next((u32(d) for t, d in subrecords(d) if t == b"TNAM"), 0)
                     for h, d in game.records(b"KYWD")}

    tpl = Plugin(args.template)
    if tpl.masters != ["Fallout4.esm"]:
        raise SystemExit(f"unexpected template masters {tpl.masters}")
    flavor_id = next(struct.unpack_from("<I", h, 12)[0] for h, d in tpl.records(b"KYWD")
                     if any(t == b"EDID" and cstr(v) == FLAVOR_EDID for t, v in subrecords(d)))

    # Fallout4.esm has no masters and is the template's first master, so form IDs
    # copied from it mean the same thing in the new plugin.
    copies, report = [], []
    for start, end in entry_ranges(source_subs):
        entry = source_subs[start:end]
        keywords, graph, paths, role, perspective = describe(entry)
        if role != 0 or perspective != 0 or ANIM_ARCHETYPE_PLAYER not in keywords:
            continue
        female = any(keyword_types.get(k) == KEYWORD_TYPE_ANIM_GENDER for k in keywords)
        copy = riding_copy(entry, flavor_id, female)
        copies += copy
        report.append((keywords, female, describe(copy)[2], graph))
    if not copies:
        raise SystemExit(f"no third-person player MT entries in {source_edid}; nothing to build")

    out = bytearray(tpl.header)
    for label, group in tpl.groups():
        if label != b"RACE":
            out += group
            continue
        header, data = next(tpl.records(b"RACE"))
        subs = subrecords(data)
        ranges = entry_ranges(subs)
        if len(ranges) != 1 or not any(d == PLACEHOLDER_GRAPH for t, d in subs[ranges[0][0]:ranges[0][1]]):
            raise SystemExit("the template's race should hold exactly one placeholder subgraph entry")
        start, end = ranges[0]
        subs = subs[:start] + copies + subs[end:]
        subs = [(t, struct.pack("<I", template_race) if t == b"SADD" else d) for t, d in subs]
        data = pack_subrecords(subs)
        record = header[:4] + struct.pack("<I", len(data)) + header[8:] + data
        out += group[:4] + struct.pack("<I", 24 + len(record)) + group[8:24] + record

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(bytes(out))
    print(f"wrote {args.out}")
    print(f"  additive to {source_edid} ({template_race:06X}), the template race of HumanRace")
    for keywords, female, paths, graph in report:
        kws = ", ".join(f"{k:06X}" for k in keywords)
        print(f"  + MT 3rd [{kws} + {FLAVOR_EDID}]{' (female)' if female else ''}  {graph}")
        for p in paths:
            print(f"      {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
