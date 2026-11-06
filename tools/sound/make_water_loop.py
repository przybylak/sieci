#!/usr/bin/env python3
"""The mod's own wet-road loop (the 2026-11-06a build): the water sound the bike plays riding through water.

  python3 -I -B make_water_loop.py --ex1 <example 1 as WAV> --out <dir>

Test 49's tester heard the 2026-11-02a build's water loop (the game's small waterfall splatter, pitched up 15 %) as
"frying or crumpling foil" and pointed to two recordings of cars on a wet road. Example 1, "Cars driving on a wet road 3"
(Pixabay 101246, freesound_community), is steady traffic on a wet road: a smooth "shhh" (Gaussian, 3.7 dB between the
20 ms level's p10 and p90), centroid about 1.86 kHz, 79 % of its power at 250 Hz-4 kHz. This tool cuts the mod's loop
from it; the recording isn't in the repository, and neither is the loop. The mp3 is decoded first, by hand:

  ffmpeg -i <the mp3> -c:a pcm_s16le ex1.wav      (in a new, empty folder; the tools take WAVs)

The input is checked: 16-bit PCM, 24 kHz, stereo, 11.98 s (the file as Pixabay gives it). The steps:

  1. three clean stretches (SEGS: 0.30-3.10, 4.40-8.10 and 9.60-11.90 s; left out: the start, a tone at 3.2-4.2 s,
     1.35-1.70 kHz, 19-20 dB over its band, and a low thump at 8.4-8.7 s), each mono ((L + R) / 2);
  2. each resampled to 44.1 kHz (FFT zero padding: the source has nothing over 12 kHz), a second-order high-pass at
     HP_HZ (120 Hz: the traffic's rumble, which the engine covers) and a first-order roll-off from ROLL_HZ (6 kHz);
  3. spliced with XF (0.25 s) equal-power crossfades (the stretches are uncorrelated noise), the slow level flattened
     (FLAT s windows, within FLAT_DB), the tail crossfaded into the head over WRAP (0.4 s): the loop starts there;
  4. levelled to TARGET_A dBFS A-weighted (-23: the engine's cruise plays at about -16 dBFS equivalent, so at full
     depth and speed the wet road sits about 8 dB under it; [Fx] WaterRoadDb trims it in the game).

Writes, in --out, CMB_FxWaterRoadLP.wav (44.1 kHz mono 16-bit PCM, as the engine's 13 WAVs; the game plays it from
Data\\Sound\\FX\\CMB as CMB_FxWaterRoadLPSD's file, 0x8A9) and water.json: the source (its name, size, sha256, rate,
channels, length), the constants, the measures and the output's sha256. The checks, none by ear (exit 1 if one fails):

  - the seam: the wrap's spectral step (0.1 s windows either side, Hann, unit-norm magnitude spectra) and its level step
    each within the loop's own 90th percentile of the same steps elsewhere, and the wrap's sample step within the 99th
    percentile of all sample steps (build_loops.py's seam_pct on the wrap's second difference under 99);
  - the spectrum: the loop's centroid within 15 % of example 1's own (the high-pass and the roll-off move it a little),
    over 80 % of its power at 250 Hz-4 kHz, under 15 % above 4 kHz (the spray's 76 %);
  - the level: A-weighted at TARGET_A within 0.1 dB, the peak under -3 dBFS, the 20 ms level's p90 - p10 under 3 dB.

The recording is Pixabay content (the Pixabay Content License: usable in a project, not to be passed on as it is): the
loop is cut, filtered, re-levelled, spliced and looped from three stretches of it, and ships in the mod's package with
the credit line (README "Credits")."""
import argparse
import hashlib
import json
import os
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_loops import SR, db, rms, seam_pct, write  # noqa: E402

NAME = "CMB_FxWaterRoadLP.wav"
SRC_RATE, SRC_CH, SRC_SECONDS = 24000, 2, 11.98
SEGS = [(0.30, 3.10), (4.40, 8.10), (9.60, 11.90)]   # s: the clean stretches (the start, the tone and the thump left out)
XF = 0.25          # s, each splice's equal-power crossfade
WRAP = 0.40        # s, the wrap's crossfade (the tail into the head)
HP_HZ = 120.0      # the second-order high-pass
ROLL_HZ = 6000.0   # the first-order roll-off
FLAT, FLAT_DB = 0.4, 6.0   # the slow level flattened over these windows (s), within +-FLAT_DB
TARGET_A = -23.0   # dBFS, A-weighted
WIN = 0.1          # s, the seam check's windows


def read_source(path):
    """example 1 as 16-bit PCM WAV -> (rate, channels, samples x channels as float)."""
    with wave.open(str(path)) as w:
        sr, ch, n, sw = w.getframerate(), w.getnchannels(), w.getnframes(), w.getsampwidth()
        if sw != 2:
            raise SystemExit(f"{path}: 16-bit PCM expected (ffmpeg -i <mp3> -c:a pcm_s16le ex1.wav)")
        x = np.frombuffer(w.readframes(n), "<i2").astype(np.float64).reshape(-1, ch) / 32768
    if sr != SRC_RATE or ch != SRC_CH or abs(n / sr - SRC_SECONDS) > 0.05:
        raise SystemExit(f"{path}: {sr} Hz, {ch} channel(s), {n / sr:.2f} s; example 1 is {SRC_RATE} Hz stereo, {SRC_SECONDS} s "
                         "(\"Cars driving on a wet road 3\", Pixabay 101246, decoded as it comes)")
    return sr, ch, x


def resample(sig, r0, r1):
    n1 = int(round(len(sig) * r1 / r0))
    spec = np.fft.rfft(sig)
    out = np.zeros(n1 // 2 + 1, dtype=complex)
    k = min(len(spec), len(out))
    out[:k] = spec[:k]
    return np.fft.irfft(out, n1) * (n1 / len(sig))


def shape(sig, r):
    """the high-pass (second order, HP_HZ) and the roll-off (first order, ROLL_HZ), as magnitudes on the spectrum."""
    spec = np.fft.rfft(sig)
    f = np.fft.rfftfreq(len(sig), 1 / r)
    hp = (f / HP_HZ) ** 2 / np.sqrt(1 + (f / HP_HZ) ** 4)
    roll = 1.0 / np.sqrt(1 + (f / ROLL_HZ) ** 2)
    return np.fft.irfft(spec * hp * roll, len(sig))


def flatten(sig, r):
    n = int(FLAT * r)
    env = np.sqrt(np.convolve(sig ** 2, np.ones(n) / n, mode="same") + 1e-12)
    g = np.clip(np.sqrt((sig ** 2).mean()) / env, 10 ** (-FLAT_DB / 20), 10 ** (FLAT_DB / 20))
    return sig * g


def equal_power(n):
    t = np.linspace(0, 1, n)
    return np.cos(t * np.pi / 2), np.sin(t * np.pi / 2)


def a_weight_db(f):
    """IEC 61672 A-weighting, 0 dB at 1 kHz."""
    f2 = f ** 2
    ra = (12194 ** 2 * f2 ** 2) / ((f2 + 20.6 ** 2) * np.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2)) * (f2 + 12194 ** 2))
    return 20 * np.log10(ra + 1e-30) + 2.0


def a_level(sig, r):
    p = np.abs(np.fft.rfft(sig)) ** 2
    f = np.fft.rfftfreq(len(sig), 1 / r)
    w = 10 ** (a_weight_db(np.maximum(f, 1.0)) / 10)
    return float(10 * np.log10((p * w).sum() / p.sum() * (sig ** 2).mean() + 1e-30))


def spectrum(sig, r):
    """(centroid Hz, share under 250 Hz, 250 Hz-4 kHz, over 4 kHz) of the power spectrum."""
    p = np.abs(np.fft.rfft(sig)) ** 2
    f = np.fft.rfftfreq(len(sig), 1 / r)
    tot = p.sum()
    return (float((f * p).sum() / tot), float(p[f < 250].sum() / tot), float(p[(f >= 250) & (f < 4000)].sum() / tot),
            float(p[f >= 4000].sum() / tot))


def build(x, sr):
    mono = x.mean(axis=1)
    pieces = [shape(resample(mono[int(a * sr):int(b * sr)], sr, SR), SR) for a, b in SEGS]
    nx = int(XF * SR)
    y = pieces[0]
    for p in pieces[1:]:
        fo, fi = equal_power(nx)
        y = np.concatenate([y[:-nx], y[-nx:] * fo + p[:nx] * fi, p[nx:]])
    y = flatten(y, SR)
    nw = int(WRAP * SR)
    fo, fi = equal_power(nw)
    loop = np.concatenate([y[-nw:] * fo + y[:nw] * fi, y[nw:-nw]])
    return loop * 10 ** ((TARGET_A - a_level(loop, SR)) / 20)


def measures(loop, ex_centroid):
    cen, lo, mid, hi = spectrum(loop, SR)
    n20 = int(0.02 * SR)
    e = np.array([10 * np.log10((loop[i:i + n20] ** 2).mean() + 1e-20) for i in range(0, len(loop) - n20, n20)])
    n = int(WIN * SR)

    def spec(s):
        v = np.abs(np.fft.rfft(s * np.hanning(len(s))))
        return v / (np.linalg.norm(v) + 1e-30)

    def lev(s):
        return 10 * np.log10((s ** 2).mean() + 1e-30)

    two = np.concatenate([loop, loop])
    seam = len(loop)
    d_wrap = float(np.linalg.norm(spec(two[seam - n:seam]) - spec(two[seam:seam + n])))
    l_wrap = float(lev(two[seam:seam + n]) - lev(two[seam - n:seam]))
    d_else = [np.linalg.norm(spec(loop[i - n:i]) - spec(loop[i:i + n])) for i in range(n, len(loop) - n, n)]
    l_else = [abs(lev(loop[i:i + n]) - lev(loop[i - n:i])) for i in range(n, len(loop) - n, n)]
    steps = np.abs(np.diff(loop))
    step_wrap = float(abs(loop[0] - loop[-1]))
    return {
        "seconds": round(len(loop) / SR, 4), "samples": int(len(loop)),
        "rms_dBFS": round(db(rms(loop)), 2), "a_weighted_dBFS": round(a_level(loop, SR), 2), "peak_dBFS": round(db(float(np.abs(loop).max())), 2),
        "centroid_Hz": round(cen, 1), "example_centroid_Hz": round(ex_centroid, 1), "centroid_re_example": round(cen / ex_centroid, 4),
        "share_under_250": round(lo, 4), "share_250_4k": round(mid, 4), "share_over_4k": round(hi, 4),
        "level_20ms_p10_p50_p90_dBFS": [round(float(np.percentile(e, q)), 2) for q in (10, 50, 90)],
        "level_20ms_p90_p10_dB": round(float(np.percentile(e, 90) - np.percentile(e, 10)), 2),
        "wrap_spectral_step": round(d_wrap, 4), "spectral_step_median_p90": [round(float(np.median(d_else)), 4), round(float(np.percentile(d_else, 90)), 4)],
        "wrap_level_step_dB": round(l_wrap, 3), "level_step_median_p90_dB": [round(float(np.median(l_else)), 3), round(float(np.percentile(l_else, 90)), 3)],
        "wrap_sample_step": round(step_wrap, 5), "wrap_sample_step_percentile": round(float(100 * np.mean(steps < step_wrap)), 1),
        "sample_step_median_p99": [round(float(np.median(steps)), 5), round(float(np.percentile(steps, 99)), 5)],
        "seam_pct": round(seam_pct(loop), 1),
    }


def checks(m):
    """[(what, ok)]: the listen-free checks of the module's docstring."""
    return [
        ("the wrap's spectral step within the loop's own p90", m["wrap_spectral_step"] <= m["spectral_step_median_p90"][1]),
        ("the wrap's level step within the loop's own p90", abs(m["wrap_level_step_dB"]) <= m["level_step_median_p90_dB"][1]),
        ("the wrap's sample step within the 99th percentile", m["wrap_sample_step_percentile"] < 99.0 and m["seam_pct"] < 99.0),
        ("the centroid within 15 % of example 1's", abs(m["centroid_re_example"] - 1.0) <= 0.15),
        ("over 80 % at 250 Hz-4 kHz, under 15 % over 4 kHz", m["share_250_4k"] > 0.80 and m["share_over_4k"] < 0.15),
        ("A-weighted at TARGET_A within 0.1 dB", abs(m["a_weighted_dBFS"] - TARGET_A) <= 0.1),
        ("the peak under -3 dBFS", m["peak_dBFS"] < -3.0),
        ("the 20 ms level's p90 - p10 under 3 dB", m["level_20ms_p90_p10_dB"] < 3.0),
    ]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description="The mod's own wet-road water loop from example 1 (Pixabay 101246, decoded to WAV).")
    ap.add_argument("--ex1", required=True, help="example 1 as a 16-bit PCM WAV (ffmpeg -i <mp3> -c:a pcm_s16le ex1.wav)")
    ap.add_argument("--out", required=True, help="the folder for CMB_FxWaterRoadLP.wav and water.json")
    a = ap.parse_args()
    sr, ch, x = read_source(a.ex1)
    ex_centroid = spectrum(x.mean(axis=1), sr)[0]
    loop = build(x, sr)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    wav = out / NAME
    write(wav, loop)
    with wave.open(str(wav)) as w:   # the file as written (16-bit), measured as the game will play it
        heard = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float64) / 32768
    m = measures(heard, ex_centroid)
    res = checks(m)
    info = {
        "file": NAME, "sha256": sha256(wav), "format": "44.1 kHz mono 16-bit PCM",
        "source": {"title": "Cars driving on a wet road 3", "site": "Pixabay", "id": 101246, "user": "freesound_community",
                   "licence": "Pixabay Content License", "file": Path(a.ex1).name, "bytes": Path(a.ex1).stat().st_size,
                   "sha256": sha256(a.ex1), "rate": sr, "channels": ch, "seconds": round(len(x) / sr, 3)},
        "settings": {"segments_s": SEGS, "crossfade_s": XF, "wrap_s": WRAP, "highpass_Hz": HP_HZ, "rolloff_Hz": ROLL_HZ,
                     "flatten_s": FLAT, "flatten_dB": FLAT_DB, "target_a_dBFS": TARGET_A},
        "measures": m, "checks": {what: bool(ok) for what, ok in res},
    }
    (out / "water.json").write_text(json.dumps(info, indent=1) + "\n")
    print("%s: %.2f s, RMS %.1f dBFS, A-weighted %.1f, peak %.1f; centroid %.0f Hz (example 1 %.0f), <250 %.2f, 250-4k %.2f, >4k %.2f" % (
        NAME, m["seconds"], m["rms_dBFS"], m["a_weighted_dBFS"], m["peak_dBFS"], m["centroid_Hz"], m["example_centroid_Hz"], m["share_under_250"],
        m["share_250_4k"], m["share_over_4k"]))
    print("20 ms level: p10 %.1f p50 %.1f p90 %.1f (p90-p10 %.1f dB)" % (*m["level_20ms_p10_p50_p90_dBFS"], m["level_20ms_p90_p10_dB"]))
    print("the wrap: spectral step %.3f (elsewhere median %.3f, p90 %.3f), level step %+.2f dB (elsewhere median %.2f, p90 %.2f), sample step %.4f "
          "(percentile %.1f; median %.4f, p99 %.4f), seam_pct %.1f" % (
              m["wrap_spectral_step"], *m["spectral_step_median_p90"], m["wrap_level_step_dB"], *m["level_step_median_p90_dB"], m["wrap_sample_step"],
              m["wrap_sample_step_percentile"], *m["sample_step_median_p99"], m["seam_pct"]))
    for what, ok in res:
        print("%-4s %s" % ("ok" if ok else "FAIL", what))
    print("wrote %s (sha256 %s) and water.json" % (wav, info["sha256"]))
    return 0 if all(ok for _, ok in res) else 1


if __name__ == "__main__":
    sys.exit(main())
