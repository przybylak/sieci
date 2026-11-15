#!/usr/bin/env python3
"""Byte-for-byte proof of the DDS Python (Commonwealth Motorbike asset tools) that needs none of the user's files.

docs/ASSETS.md and docs/BUILD_GUIDE.md record the SHA-256 of three shipped textures that are made from the
repository alone: plates_d.dds, plates_n.dds and plates_s.dds of the 2026-11-09a build (unchanged in
2026-11-10a) start b5eacce3, 78b75210 and 8892936a. This builds the three the way look_plates.py's write()
does (its own functions, in its own order; the rest of write() needs the stage folders) and compares.

    python3 -I -B <repository>/tools/rider/bike_art.py --plates --out <art folder>      # numpy only
    <DDS python> -I -B plates_digest.py <repository>/tools/rider <art folder> [--out <folder>]

Exit 0 and a last line "ok" when all three match.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

WANT = {"plates_d.dds": "b5eacce3", "plates_n.dds": "78b75210", "plates_s.dds": "8892936a"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rider", type=Path, help="the repository's tools/rider folder")
    ap.add_argument("art", type=Path, help="bike_art.py --plates' output")
    ap.add_argument("--out", type=Path, help="keep the three files here")
    a = ap.parse_args()
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(a.rider.resolve()))
    import look_plates as LP
    import write_dds as W
    opts = json.loads((a.rider.resolve().parent / "esp-generator" / "look_options.json").read_text())
    meta = json.loads((a.art / "plates.json").read_text())
    files = {}
    segs = LP.part_segments(opts, meta)
    g, part = LP.load_png(a.art / "plates_d.png"), LP.load_png(a.art / "plates_part.png")
    files["plates_d.dds"], _ = LP.index_dds(g, part, segs)
    hd = LP.box_down(LP.heights(a.art, meta, "plates_h.png", "designs"), 2)
    files["plates_n.dds"] = W.build([LP.normals(hd, meta["face"]["px_a_unit"] / 2)], "bc5", normal=True)
    files["plates_s.dds"] = W.build([LP.spec_rgba(LP.load_png(a.art / "plates_s.png"), 4)], "bc5")
    bad = 0
    for name, data in files.items():
        h = hashlib.sha256(data).hexdigest()
        ok = h.startswith(WANT[name])
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: {len(data)} bytes, sha256 {h} (recorded {WANT[name]}...)")
        if a.out:
            a.out.mkdir(parents=True, exist_ok=True)
            (a.out / name).write_bytes(data)
    print("ok" if not bad else f"{bad} of 3 differ from the shipped textures")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
