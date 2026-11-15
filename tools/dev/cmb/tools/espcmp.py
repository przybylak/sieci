#!/usr/bin/env python3
"""Compares two of the game's plugins (.esp/.esm/.esl) record by record, by FormID.

  python3 -I espcmp.py <old.esp> <new.esp> [--list]

Prints
  TES4: the header record's changed subrecords (HEDR decoded: record count, next object ID),
  added N (lo-hi): n TYPE, ...     records only in <new>
  removed N (lo-hi): n TYPE, ...   records only in <old>
  changed N                        then one line per changed record: FormID, type, EditorID and the
                                   subrecord types that differ ("xA->B" where their number differs;
                                   "flags"/"version"/"vc" for the record header, "order" when only the
                                   subrecords' order differs, "group" when the record sits in another GRUP).
--list also names every added and removed record and shows each differing subrecord's bytes (first 32).

Walks GRUPs to any depth, inflates compressed records (flag 0x00040000, zlib) and joins XXXX big subrecords.
A FormID is shown as its low six hex digits for the plugin's own records and as <master>:<id> for overrides, so
the comparison holds when the two plugins' master lists differ. Exit status 0 when both files parse (different
or not), 2 on a usage or parse error. Reads only; standard library only.
"""
import struct
import sys
import zlib

COMPRESSED = 0x00040000
HEADER = 24


class ParseError(Exception):
    pass


def subrecords(data, where):
    """[(type, bytes)] of a record's data; an XXXX subrecord gives the next one's real size."""
    out = []
    pos = 0
    big = None
    n = len(data)
    while pos < n:
        if pos + 6 > n:
            raise ParseError(f"{where}: subrecord header runs past the record ({n - pos} byte(s) left)")
        kind = data[pos:pos + 4].decode("latin-1")
        size = struct.unpack_from("<H", data, pos + 4)[0]
        pos += 6
        if kind == "XXXX":
            if size != 4 or pos + 4 > n:
                raise ParseError(f"{where}: bad XXXX subrecord")
            big = struct.unpack_from("<I", data, pos)[0]
            pos += 4
            continue
        if big is not None:
            size, big = big, None
        if pos + size > n:
            raise ParseError(f"{where}: {kind} ({size} bytes) runs past the record")
        out.append((kind, bytes(data[pos:pos + size])))
        pos += size
    if big is not None:
        raise ParseError(f"{where}: XXXX with no subrecord after it")
    return out


class Record:
    __slots__ = ("kind", "flags", "formid", "vc", "version", "unknown", "subs", "group", "compressed")

    def edid(self):
        for kind, data in self.subs:
            if kind == "EDID":
                return data.split(b"\0")[0].decode("latin-1")
        return ""


class Plugin:
    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            self.data = f.read()
        self.tes4 = None
        self.records = {}       # key -> Record
        self.order = []         # keys in file order
        self.groups = 0
        self.duplicates = []
        self.masters = []
        data = self.data
        if len(data) < HEADER or data[:4] != b"TES4":
            raise ParseError(f"{path}: not a plugin (no TES4 record at the start)")
        pos = self._record(0, len(data), ())
        self.tes4 = self._last
        self.masters = [d.split(b"\0")[0].decode("latin-1") for k, d in self.tes4.subs if k == "MAST"]
        self._walk(pos, len(data), ())

    def key(self, formid):
        """(master name lowercased, or '' for the plugin's own; object ID)."""
        index = formid >> 24
        if index < len(self.masters):
            return (self.masters[index].lower(), formid & 0xFFFFFF)
        return ("", formid & 0xFFFFFF)

    def _record(self, pos, end, group):
        data = self.data
        if pos + HEADER > end:
            raise ParseError(f"{self.path}: record header at 0x{pos:X} runs past its container")
        kind = data[pos:pos + 4].decode("latin-1")
        size, flags, formid, vc, version, unknown = struct.unpack_from("<IIIIHH", data, pos + 4)
        body = pos + HEADER
        if body + size > end:
            raise ParseError(f"{self.path}: {kind} {formid:08X} at 0x{pos:X} ({size} bytes) runs past its container")
        raw = data[body:body + size]
        where = f"{self.path}: {kind} {formid:08X}"
        if flags & COMPRESSED:
            if size < 4:
                raise ParseError(f"{where}: compressed record shorter than its size field")
            want = struct.unpack_from("<I", raw, 0)[0]
            try:
                raw = zlib.decompress(raw[4:])
            except zlib.error as e:
                raise ParseError(f"{where}: zlib: {e}") from None
            if len(raw) != want:
                raise ParseError(f"{where}: inflates to {len(raw)} bytes, header says {want}")
        r = Record()
        r.kind, r.flags, r.formid, r.vc, r.version, r.unknown = kind, flags, formid, vc, version, unknown
        r.subs = subrecords(raw, where)
        r.group = group
        self._last = r
        return body + size

    def _walk(self, pos, end, group):
        data = self.data
        while pos < end:
            if pos + HEADER > end:
                raise ParseError(f"{self.path}: {end - pos} stray byte(s) at 0x{pos:X}")
            if data[pos:pos + 4] == b"GRUP":
                size, label, gtype = struct.unpack_from("<I4si", data, pos + 4)
                if size < HEADER or pos + size > end:
                    raise ParseError(f"{self.path}: GRUP at 0x{pos:X} (size {size}) runs past its container")
                self.groups += 1
                self._walk(pos + HEADER, pos + size, group + ((gtype, label),))
                pos += size
            else:
                pos = self._record(pos, end, group)
                r = self._last
                k = self.key(r.formid)
                if k in self.records:
                    self.duplicates.append(k)
                else:
                    self.order.append(k)
                self.records[k] = r


def show(key):
    master, oid = key
    return f"{master}:{oid:06X}" if master else f"{oid:06X}"


def by_type(subs):
    out = {}
    for kind, data in subs:
        out.setdefault(kind, []).append(data)
    return out


def sub_diff(old, new):
    """Names of the subrecord types that differ between two subrecord lists, in order of first appearance."""
    a, b = by_type(old), by_type(new)
    names = []
    for kind in list(dict.fromkeys([k for k, _ in old] + [k for k, _ in new])):
        la, lb = a.get(kind, []), b.get(kind, [])
        if la == lb:
            continue
        names.append(kind if len(la) == len(lb) else f"{kind} x{len(la)}->{len(lb)}")
    if not names and old != new:
        names.append("order")
    return names


def record_diff(old, new):
    names = []
    if old.kind != new.kind:
        names.append(f"type {old.kind}->{new.kind}")
    if old.flags != new.flags:
        names.append(f"flags 0x{old.flags:08X}->0x{new.flags:08X}")
    if old.version != new.version:
        names.append(f"version {old.version}->{new.version}")
    if (old.vc, old.unknown) != (new.vc, new.unknown):
        names.append("vc")
    if old.group != new.group:
        names.append("group")
    return names + sub_diff(old.subs, new.subs)


def hexs(data):
    return data[:32].hex() + ("..." if len(data) > 32 else "") + f" ({len(data)})"


def detail(old, new, indent):
    a, b = by_type(old), by_type(new)
    for kind in list(dict.fromkeys([k for k, _ in old] + [k for k, _ in new])):
        la, lb = a.get(kind, []), b.get(kind, [])
        if la == lb:
            continue
        for i in range(max(len(la), len(lb))):
            x = la[i] if i < len(la) else None
            y = lb[i] if i < len(lb) else None
            if x == y:
                continue
            n = f"[{i}]" if max(len(la), len(lb)) > 1 else ""
            print(f"{indent}{kind}{n}: {hexs(x) if x is not None else '-'} -> {hexs(y) if y is not None else '-'}")


def summary(word, keys, plugin, listing):
    if not keys:
        print(f"{word} 0")
        return
    counts = {}
    for k in keys:
        kind = plugin.records[k].kind
        counts[kind] = counts.get(kind, 0) + 1
    own = sorted(k for k in keys if not k[0]) or sorted(keys)
    span = show(own[0]) if own[0] == own[-1] else f"{show(own[0])}-{show(own[-1])}"
    kinds = ", ".join(f"{n} {kind}" for kind, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
    print(f"{word} {len(keys)} ({span}): {kinds}")
    if listing:
        for k in sorted(keys):
            r = plugin.records[k]
            print(f"  {show(k)} {r.kind} {r.edid()}")


def tes4_diff(old, new, listing):
    lines = []
    for name in sub_diff(old.subs, new.subs):
        kind = name.split()[0]
        a, b = by_type(old.subs).get(kind, []), by_type(new.subs).get(kind, [])
        if kind == "HEDR" and len(a) == len(b) == 1 and len(a[0]) == len(b[0]) == 12:
            (va, na, ia), (vb, nb, ib) = struct.unpack("<fiI", a[0]), struct.unpack("<fiI", b[0])
            parts = []
            if va != vb:
                parts.append(f"version {va:g} -> {vb:g}")
            if na != nb:
                parts.append(f"records {na} -> {nb}")
            if ia != ib:
                parts.append(f"next ID 0x{ia:X} -> 0x{ib:X}")
            lines.append("HEDR " + ", ".join(parts))
        elif kind in ("MAST", "CNAM", "SNAM"):
            text = lambda l: "[" + ", ".join(d.split(b"\0")[0].decode("latin-1") for d in l) + "]"
            lines.append(f"{kind} {text(a)} -> {text(b)}")
        else:
            lines.append(name)
    head = [n for n in record_diff(old, new) if n not in sub_diff(old.subs, new.subs)]
    lines = head + lines
    print("TES4: " + ("; ".join(lines) if lines else "same"))
    if listing and lines:
        detail(old.subs, new.subs, "  ")


def main(argv):
    args = [a for a in argv[1:] if a != "--list"]
    listing = "--list" in argv[1:]
    if len(args) != 2 or any(a.startswith("--") for a in args):
        print(__doc__)
        return 2
    try:
        old, new = Plugin(args[0]), Plugin(args[1])
    except (OSError, ParseError) as e:
        print(f"espcmp: {e}", file=sys.stderr)
        return 2
    for name, p in (("old", old), ("new", new)):
        print(f"{name}: {p.path}: {len(p.data)} bytes, {len(p.records)} records in {p.groups} groups"
              + (f", {len(p.duplicates)} DUPLICATE FormID(s): {', '.join(show(k) for k in p.duplicates[:8])}"
                 if p.duplicates else ""))
    if old.data == new.data:
        print("identical files")
        return 0
    tes4_diff(old.tes4, new.tes4, listing)
    added = [k for k in new.order if k not in old.records]
    removed = [k for k in old.order if k not in new.records]
    summary("added", added, new, listing)
    summary("removed", removed, old, listing)
    changed = []
    for k in new.order:
        if k in old.records:
            names = record_diff(old.records[k], new.records[k])
            if names:
                changed.append((k, names))
    print(f"changed {len(changed)}")
    for k, names in changed:
        r = new.records[k]
        print(f"  {show(k)} {r.kind} {r.edid()}: {', '.join(names)}")
        if listing:
            detail(old.records[k].subs, r.subs, "      ")
    common = [k for k in new.order if k in old.records]
    if [k for k in old.order if k in new.records] != common:
        print("order: the records both files have come in a different order")
    if not (added or removed or changed) and old.tes4.subs == new.tes4.subs:
        print("same records; the files differ only in layout (compression, group headers or order)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
