#!/usr/bin/env python3
"""The loop set's last stage: every file a few dB hotter, its peaks rounded off by a memoryless soft limiter.

  python3 -I hot_loops.py --in <loops dir> --out <dir> [--gain 2.5] [--knee -6] [--ceiling -1]

Since test 45's answer. The game plays the loops as they are, and the MCM's 100 (an instance volume of 1.0, the most
the game takes) left the engine too quiet: build_loops.py levels every riding loop to -13.5 dBFS RMS with its peaks at
-1 dBFS, a crest of 12.5 dB, where the reference rides' is 9.2-11.7. Here each of the 13 files (the 11 loops, the idle
among them, the start and the stop) gets the same treatment:

  y = shape(gain x x), gain +2.5 dB, shape: the identity up to the knee (-6 dBFS); from there a cubic (Hermite) from
  the knee, at slope 1, to the ceiling (-1 dBFS, the 16-bit step at or under it), at slope 0, reached where the loops'
  own peaks land (-1 dBFS + the gain); the ceiling beyond that.

The curve is monotone and its slope continuous (1 below the knee, 0 at the top). It has no memory: each sample is
mapped alone, so a loop's wrap stays exactly as seamless as built (the wrap's step can only shrink by the curve's
slope, like every other step), and the start and stop need no edge handling. On test 45's set the loops come to
-11.05 to -11.30 dBFS RMS with their peaks at -1.00 (Off2300's at -1.13), a crest of 10.0-10.3 dB;
6-9 % of each loop's samples lie over the knee. The price of no memory is some distortion on the pulses' peaks: the
curve's non-linear residual lies 13-17 dB under the on-load loops' own 4-16 kHz band (23-26 dB under the others'),
where the look-ahead limiter of build_loops.py (2 ms gain ramps) would leave it 20-24 dB under. loops.json says so per
file ("hot": residual_4_16k_dB).

Writes, in --out, each WAV of --in under its own name (44.1 kHz 16-bit mono) and --in's loops.json with a "hot" entry
per file: the settings, the RMS, peak and crest before and after, the share over the knee, the residual, and the
loop's wrap (build_loops.py's seam check, and the wrap's step against the loop's median step) before and after; the
entry's own rms_dBFS, peak_dBFS and kloud_re_rms_dB become the file's after this stage. --in and --out may be the same
folder. A set whose loops.json already has a "hot" entry is refused (the stage would be applied twice).
--gain 0 writes the files unchanged, byte for byte (test 45's set), with their "hot" entries."""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_loops import SR, db, loudness_loop, read, rms, seam_pct, write  # noqa: E402

LOOP_PEAK_DBFS = -1.0     # where build_loops.py's limiter puts the riding loops' peaks: the curve reaches the ceiling there


def shape(u, knee, ceil, top):
    """the soft limiter on |u|: identity up to knee, the cubic Hermite (knee, slope 1) -> (top, ceil, slope 0), ceil above."""
    a = np.abs(u)
    t = np.clip((a - knee) / (top - knee), 0.0, 1.0)
    cubic = (2 * t ** 3 - 3 * t ** 2 + 1) * knee + (t ** 3 - 2 * t ** 2 + t) * (top - knee) + (-2 * t ** 3 + 3 * t ** 2) * ceil
    return np.sign(u) * np.where(a <= knee, a, np.where(a >= top, ceil, cubic))


def band_power(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return float(np.sum(np.abs(X[(f >= lo) & (f <= hi)]) ** 2))


def measures(x, loop):
    m = dict(rms_dBFS=round(db(rms(x)), 2), peak_dBFS=round(db(np.abs(x).max()), 2))
    m["crest_dB"] = round(m["peak_dBFS"] - m["rms_dBFS"], 2)
    if loop:
        d = np.abs(np.diff(x))
        m["kloud_re_rms_dB"] = round(loudness_loop(x) - db(rms(x)), 2)
        m["seam_d2_pct"] = round(seam_pct(x), 1)
        m["wrap_step_re_median_step"] = round(float(abs(x[0] - x[-1]) / (np.median(d) + 1e-12)), 2)
        m["wrap_step_pct"] = round(float(100 * np.mean(d < abs(x[0] - x[-1]))), 1)
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="src", type=Path, required=True, help="a loop set: build_loops.py --out (WAVs and loops.json)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--gain", type=float, default=2.5, help="dB before the limiter (default 2.5; 0 = the files unchanged)")
    ap.add_argument("--knee", type=float, default=-6.0, help="dBFS where the curve leaves the identity (default -6)")
    ap.add_argument("--ceiling", type=float, default=-1.0, help="dBFS the curve never passes (default -1)")
    a = ap.parse_args()
    if not a.knee < a.ceiling < 0 or a.gain < 0:
        raise SystemExit("--knee < --ceiling < 0 dBFS and --gain >= 0 expected")
    rep = json.load(open(a.src / "loops.json"))
    if any(isinstance(v, dict) and "hot" in v for v in rep.values()):
        raise SystemExit(f"{a.src / 'loops.json'}: this set has been through hot_loops.py already")
    names = sorted(p.name for p in a.src.glob("CMB_Engine*.wav"))
    if not names:
        raise SystemExit(f"{a.src}: no CMB_Engine*.wav")
    g = 10 ** (a.gain / 20)
    knee = 10 ** (a.knee / 20)
    ceil = np.floor(10 ** (a.ceiling / 20) * 32768) / 32768          # the 16-bit step at or under the ceiling
    top = max(10 ** ((LOOP_PEAK_DBFS + a.gain) / 20), knee + 1.0001 * (ceil - knee))
    if (top - knee) > 3 * (ceil - knee):
        raise SystemExit("the cubic would overshoot (top - knee > 3 x (ceiling - knee)): raise --knee or lower --gain")
    xs = {n: read(a.src / n) for n in names}       # all read before any is written: --in may be --out
    a.out.mkdir(parents=True, exist_ok=True)
    for n in names:
        x = xs[n]
        loop = n.endswith("LP.wav")
        u = g * x
        y = shape(u, knee, ceil, top) if a.gain > 0 else x
        write(a.out / n, y)
        q = read(a.out / n)
        lin = float(np.dot(q, u) / np.dot(u, u))
        res = band_power(q - lin * u, 4000, 16000) / max(band_power(u, 4000, 16000), 1e-20)
        before, after = measures(x, loop), measures(q, loop)
        hot = dict(gain_dB=a.gain, knee_dBFS=a.knee, ceiling_dBFS=round(db(ceil), 4), top_in_dBFS=round(db(top), 2),
                   curve="identity to the knee, cubic Hermite (slope 1 -> 0) to the ceiling at top_in, the ceiling above",
                   before=before, after=after, over_knee_pct=round(float(100 * np.mean(np.abs(u) > knee)), 2),
                   residual_4_16k_dB=round(float(10 * np.log10(res + 1e-20)), 1) if a.gain > 0 else None)
        e = rep.setdefault(n[:-4], {})
        e["hot"] = hot
        e["rms_dBFS"], e["peak_dBFS"] = after["rms_dBFS"], after["peak_dBFS"]
        if loop:
            e["kloud_re_rms_dB"] = after["kloud_re_rms_dB"]
        print(f"{n:26s} rms {before['rms_dBFS']:6.2f} -> {after['rms_dBFS']:6.2f}  peak {before['peak_dBFS']:6.2f} -> "
              f"{after['peak_dBFS']:6.2f}  crest {before['crest_dB']:5.2f} -> {after['crest_dB']:5.2f}  over the knee "
              f"{hot['over_knee_pct']:4.1f}%  residual 4-16k {hot['residual_4_16k_dB']} dB"
              + (f"  seam {before['seam_d2_pct']} -> {after['seam_d2_pct']}, wrap step {before['wrap_step_re_median_step']}"
                 f" -> {after['wrap_step_re_median_step']} x the median step" if loop else ""))
    with open(a.out / "loops.json", "w") as fh:
        json.dump(rep, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
