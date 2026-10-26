#!/usr/bin/env python3
"""The engine's loop set: each riding loop's tone matched to the reference ride, its attacks and its pulse-to-pulse
brightness brought to a real engine's, levelled and limited; the idle, start and stop copied as they are.

  python3 -I build_loops.py --grains <dir> --unlimited <dir> --pieces <dir> --out <dir>

--grains and --unlimited are make_grain_loops.py's two outputs (its loops.json gives each pulse's attack; the
unlimited WAVs are the material), --pieces is make_piece_loops.py's output (the idle, start and stop, and the 2300 rpm
closed-throttle loop). Writes, in --out, the 13 files the game plays (44.1 kHz 16-bit mono) and loops.json (what each
was made from, the EQ, the measures before and after):
  CMB_EngineOn1400LP, On1700LP, On2400LP,      on load at 1400 1700 2400 2800 3300 rpm (the pulse-grain loops)
    On2800LP, On3300LP
  CMB_EngineCruiseLP                           on load at 2000 rpm (a pulse-grain loop: the On2000 of the plugin's
                                               Loops line, under the name the cruise sound record plays, so the
                                               script's own idle-cruise crossfade has it too)
  CMB_EngineOff1400LP, Off1800LP, Off2800LP    throttle shut at 1400 1800 2800 rpm (the pulse-grain loops)
  CMB_EngineOff2300LP                          throttle shut at 2300 rpm (the flattened pieces: the pulse-grain loop
                                               stays 1.4 dB rms short of the tone target at the EQ's cap, the pieces
                                               of demodave's falls, the same engine and microphone, reach it)
  CMB_EngineIdleLP, CMB_EngineStart, CMB_EngineStop   copied byte for byte
The on-load family is pulse grains all through: one engine and one microphone from the idle up (pieces of other
recordings at 2000 and 2400 put two changes of source into every pull, where the firing pulse's form changes: mean-cycle
r 0.54-0.81 at those hand-overs against 0.84-0.91 within the grains set).

The reference. Every target here is a number measured on the reference ride (an Iron 883 on the road, the right
channel: "daily" in the targets; where it has too few frames at an rpm, its shape plus the difference a second,
level-linear Iron 883 ride ("paris") shows between two rpm): nothing of either ride is in a loop, and neither is needed
to build. TARGETS holds each loop's octave shape (63 Hz-8 kHz, dB re the 20 Hz-16 kHz total), third octaves (50 Hz-8 kHz)
and centroid; CREST the per-cycle crest of the within-cycle envelope per band; ORDER_TARGET the half-order line pattern.

Per loop, in this order:
  1. the tone match: a smooth zero-phase EQ through nodes at 63 Hz, the third octaves 99-500 Hz and the octaves 1-8 kHz
     (cosine in log frequency between nodes), fitted to the target's node levels by a bounded Levenberg-Marquardt fit on
     the predicted spectrum, with a slope penalty (0.05 dB^2 per octave) on each increment (it suppresses the
     alternating node pattern a line spectrum can't see) and a small ridge; the third octaves are smoothed over +-0.75
     third (Gaussian, in power) in both the loop and the target, so where a line falls within a band doesn't steer the
     fit. Cuts to -12 dB, boosts to +8 dB (a cut raises no noise floor). The target shape is tilted (bisection, dB per
     octave about 1 kHz) so the loop's centroid at its base follows the reference ride's centroid law through every
     base (CENTROID_LAW: on load 280.3 Hz x (rpm / 1966)^0.57, off load 199.4 Hz x (rpm / 1839)^0.20, fitted over
     1400-2700 rpm): a family of pitched loops of one engine steps by about (b/a)^(beta - 1) at each hand-over, about
     -7 % on load and -18 % off load, and nothing more. Applied once over the whole loop (circular), so the wrap stays
     as seamless as built.
  2. the attacks: the pulse-grain pulses are throttle snaps, their energy in each band sits in the attack: per
     720-degree cycle the band peak (2 ms) is 14-24 dB over the cycle's median against 7-15 dB in the reference ride.
     In every band more than 1 dB over the reference the attacks are lowered by a fixed amount (the part of the
     envelope 3-9 dB and more over its running cycle median brought down by up to the shift; zero-phase, circular),
     the shift found by bisection so the median crest meets the reference. A fixed shift keeps the pulse-to-pulse
     spread of attack strength (On2000's 5-16 kHz burst rate lands on the reference's: 40/17.5/3.8 a second at 4/8/12 dB
     against 40/17.3/4.2), where a ceiling made every attack equal. Then the tone match is fitted again.
  3. the line pattern (On1400, On1700, On2000): per half-order gains (+-8 dB, the lines' total power kept) toward the
     reference ride's pattern at their rpm, where the grains had order 5 9-13 dB strong and order 4 7 dB weak at
     cruise. It follows the orders when the loop is pitched. The riskiest step: if the cruise sounds hollow or phasey,
     ORDER_TARGET = {} removes it.
  4. the on-load loops' pulse-to-pulse brightness: after the tone match their 100 ms centroid sd is 10-13.5 % against
     the reference's 7.1-7.7 %, from the throttle-snap pulses' differences (the per-pulse HF/LF ratio has an sd of
     0.28-0.42 in ln). Each pulse's HF/LF ratio is pulled toward its cylinder's median (split at 700 or 1000 Hz, by a
     share of 0.25-1: the smallest HF gain sd that brings the centroid sd to 8.0 % or under, else the lowest centroid
     sd), the gain changing in a 2 ms ramp ending 1 ms before each attack; then the tone match once more.
  5. the level: -13.5 dBFS RMS through a look-ahead gain limiter (the gain each sample needs to stay under -1 dBFS,
     its minimum over +-1 ms, then averaged over +-1 ms, circular: a smooth gain of about 2 ms with at most 1.8 dB of
     cut, which adds no harmonics, where a waveshaper's distortion read -26 dB against the 4-16 kHz band); the gain is
     iterated so the limited file lands at -13.50."""
import argparse
import json
import shutil
import wave
from pathlib import Path

import numpy as np

SR = 44100
LOOP_RMS = 10 ** (-13.5 / 20)

# the loop set: key, source ("grains": make_grain_loops.py's unlimited loop; "pieces": make_piece_loops.py's)
PICK = [("on1400", "grains"), ("on1700", "grains"), ("on2000", "grains"), ("on2400", "grains"), ("on2800", "grains"),
        ("on3300", "grains"), ("off1400", "grains"), ("off1800", "grains"), ("off2300", "pieces"), ("off2800", "grains")]
KEEP = ["CMB_EngineIdleLP.wav", "CMB_EngineStart.wav", "CMB_EngineStop.wav"]
# a loop written under another name than CMB_Engine<On|Off><rpm>LP: On2000 is the cruise sound record's file (the ESP's
# CMB_EngineCruiseLPSD plays CMB_EngineCruiseLP.wav, the script's crossfade and the plugin's On2000 alike)
FILE_NAME = {"on2000": "CMB_EngineCruiseLP"}
CENTROID_LAW = dict(on=(280.3, 1966.0, 0.57), off=(199.4, 1839.0, 0.20))
CREST_SLACK = 1.0     # dB: a band within this of the reference's crest is left alone

# the reference ride's measures per loop (numbers only): "how" says which frames ("daily": the reference ride within
# +-6 % of the base and in the same state; where it has too few there, its shape at the nearest rpm plus the difference
# the level-linear "paris" ride shows between the two rpm), "m4" the octave shape 63 Hz-8 kHz and "third" the third
# octaves 50 Hz-8 kHz (dB re the 20 Hz-16 kHz total, 8192-point Hann frames each normalised to its total, averaged),
# "centroid" (Hz; the tone match aims at CENTROID_LAW instead)
TARGETS = {
    "on1400": dict(
        how="daily on frames +-6% (n 64, median 1426 rpm)",
        m4=[-6.42, -2.41, -9.78, -16.57, -15.85, -15.39, -20.46, -27.23],
        third=[-14.18, -7.38, -5.62, -6.47, -11.26, -14.76, -14.12, -14.83, -20.61, -20.75, -23.09, -18.74, -21.6,
               -22.4, -19.85, -21.1, -19.67, -22.95, -25.79, -28.87, -30.41, -31.73],
        centroid=253.4),
    "on1700": dict(
        how="daily on frames +-6% (n 177, median 1680 rpm)",
        m4=[-9.29, -1.83, -9.01, -15.53, -14.94, -15.77, -21.03, -27.46],
        third=[-12.35, -12.66, -4.88, -5.68, -12.1, -12.42, -14.95, -14.4, -19.35, -20.0, -21.98, -18.66, -19.93,
               -20.83, -19.94, -21.35, -20.44, -23.23, -27.34, -28.85, -30.62, -31.63],
        centroid=256.1),
    "on2000": dict(
        how="daily on frames +-6% (n 434, median 1966 rpm)",
        m4=[-6.89, -2.81, -8.05, -13.99, -14.67, -15.78, -20.37, -26.42],
        third=[-17.2, -7.38, -12.26, -5.03, -8.26, -12.02, -13.69, -12.92, -17.59, -18.88, -20.2, -18.59, -19.21,
               -20.81, -20.13, -21.14, -20.43, -22.62, -26.63, -28.09, -29.57, -30.38],
        centroid=280.3),
    "on2400": dict(
        how="daily on frames +-6% (n 28, median 2344 rpm)",
        m4=[-11.58, -2.12, -7.43, -13.45, -14.31, -14.92, -18.95, -24.46],
        third=[-22.61, -12.06, -4.83, -6.76, -11.32, -10.36, -13.89, -13.2, -16.24, -17.75, -23.35, -18.19, -19.07,
               -20.22, -19.4, -20.66, -19.17, -21.53, -24.88, -26.12, -28.77, -27.51],
        centroid=319.7),
    "on2800": dict(
        how="daily on2400 + (paris on at 2800 - paris on at 2400) (paris n 1230/432)",
        m4=[-11.29, -2.35, -7.53, -12.08, -12.56, -12.89, -16.99, -22.86],
        third=[-19.04, -13.47, -9.28, -2.85, -11.41, -11.43, -14.17, -11.86, -14.84, -16.23, -22.22, -17.38, -16.36,
               -18.17, -17.04, -18.81, -17.41, -19.4, -23.07, -24.21, -27.41, -25.49],
        centroid=383.3),
    "on3300": dict(
        how="daily on2400 + (paris on at 3300 - paris on at 2400) (paris n 1230/80)",
        m4=[-12.67, -3.13, -7.02, -10.43, -10.47, -10.57, -14.41, -20.31],
        third=[-27.99, -12.94, -12.69, -2.89, -12.54, -11.89, -13.38, -10.82, -13.76, -14.91, -19.29, -15.85, -14.73,
               -14.43, -14.97, -16.51, -14.71, -17.0, -20.43, -21.4, -24.71, -22.86],
        centroid=514.8),
    "off1400": dict(
        how="daily off1800 + (paris off at 1400 - paris off at 1800) (paris n 659/93)",
        m4=[-5.63, -2.73, -9.31, -12.92, -14.21, -16.26, -23.0, -28.13],
        third=[-13.05, -6.9, -6.48, -6.73, -10.07, -13.0, -14.57, -15.0, -16.72, -18.92, -18.06, -17.75, -19.33,
               -19.79, -19.72, -21.6, -22.2, -25.55, -28.18, -31.5, -33.05, -31.19],
        centroid=220.0),
    "off1800": dict(
        how="daily off frames +-6% (n 183, median 1839 rpm)",
        m4=[-7.32, -2.07, -10.1, -14.03, -15.67, -19.03, -25.47, -30.98],
        third=[-12.95, -9.14, -6.69, -4.72, -11.57, -14.28, -14.24, -16.42, -18.15, -19.06, -19.28, -18.98, -20.59,
               -22.41, -22.3, -24.66, -24.96, -27.93, -30.94, -33.77, -34.99, -34.43],
        centroid=199.4),
    "off2300": dict(
        how="daily off frames +-6% (n 39, median 2220 rpm)",
        m4=[-8.5, -1.88, -8.97, -16.7, -15.83, -16.86, -21.84, -27.23],
        third=[-15.29, -10.08, -3.97, -7.41, -11.83, -12.37, -13.54, -16.12, -20.25, -21.25, -23.51, -19.07, -21.23,
               -22.07, -20.05, -22.64, -22.76, -24.23, -27.49, -30.09, -31.39, -30.3],
        centroid=226.7),
    "off2800": dict(
        how="daily off2300 + (paris off at 2800 - paris off at 2300) (paris n 1070/354)",
        m4=[-8.94, -1.96, -8.6, -15.81, -15.16, -14.82, -19.0, -24.13],
        third=[-12.25, -12.66, -7.4, -5.19, -11.12, -14.36, -14.73, -12.89, -18.54, -21.0, -23.66, -19.19, -20.06,
               -20.47, -17.96, -20.43, -21.02, -21.67, -24.2, -27.46, -28.74, -26.57],
        centroid=257.6),
}
# the per-cycle crest of the within-cycle envelope (dB: each 720-degree cycle's band peak over the cycle's median,
# 2 ms windows, the median over cycles) in the bands 354-707, 707-1414, 1414-2828, 2828-5657, 5657-11314, 11314-16000 Hz,
# from the reference ride's cycles in the rpm bin named (the best-covered bin where the loop's own has too few cycles)
CREST = {
    "on1400": [8.33, 11.39, 11.3, 13.48, 11.28, 14.82],   # 1250-1550 rpm
    "on1700": [7.4, 11.46, 10.53, 13.0, 10.4, 13.35],   # 1550-1850 rpm
    "on2000": [7.44, 9.71, 9.11, 11.59, 9.18, 10.59],   # 1850-2200 rpm
    "on2400": [7.44, 9.71, 9.11, 11.59, 9.18, 10.59],   # 1850-2200 rpm
    "on2800": [7.44, 9.71, 9.11, 11.59, 9.18, 10.59],   # 1850-2200 rpm
    "on3300": [7.44, 9.71, 9.11, 11.59, 9.18, 10.59],   # 1850-2200 rpm
    "off1400": [7.0, 7.13, 5.62, 5.44, 4.4, 5.3],   # 1850-2200 rpm
    "off1800": [7.0, 7.13, 5.62, 5.44, 4.4, 5.3],   # 1850-2200 rpm
    "off2300": [7.0, 7.13, 5.62, 5.44, 4.4, 5.3],   # 1850-2200 rpm
    "off2800": [7.0, 7.13, 5.62, 5.44, 4.4, 5.3],   # 1850-2200 rpm
}

# the reference ride's half-order line pattern (k = 1..16, dB re the strongest line) on steady stretches, for the loops
# whose territory it was measured in: On1400 the 1493 rpm cruise, On1700 the 1649 and 1807 cruises, On2000 the 1868 /
# 1953 / 1986 cruises and the 1937 / 1989 / 2046 on-load stretches (their mean; the rows' sd is 0.1-2.8 dB: the pattern
# is order-locked, not a fixed resonance)
_D = dict(c1493=[-32.5, -26.2, -21.8, -16.7, -8.3, -13.8, -2.0, 0.0, -4.1, -5.2, -5.0, -6.8, -14.6, -9.2, -22.2, -14.0],
          c1649=[-33.7, -27.7, -24.4, -15.8, -5.3, -10.4, 0.0, -1.0, -2.2, -10.8, -9.9, -6.2, -15.1, -9.0, -14.7, -17.4],
          c1807=[-32.2, -30.4, -26.1, -13.1, -2.8, -9.9, 0.0, -1.0, -2.1, -13.7, -15.2, -6.5, -15.8, -9.8, -11.4, -18.6],
          c1868=[-27.8, -25.3, -20.9, -13.4, -1.0, -9.5, 0.0, -1.8, -1.4, -15.3, -15.3, -5.3, -12.3, -10.8, -11.4, -12.3],
          c1953=[-30.0, -22.6, -20.6, -11.0, 0.0, -8.1, -0.2, -2.2, -1.5, -9.7, -17.8, -5.3, -13.3, -9.3, -9.9, -14.2],
          c1986=[-28.0, -21.6, -20.4, -11.8, -0.4, -7.0, 0.0, -2.4, -2.5, -10.3, -16.0, -7.3, -12.5, -12.1, -13.4, -15.7],
          o1937=[-34.5, -25.0, -22.0, -12.0, -2.3, -14.0, 0.0, -3.9, -2.4, -11.2, -18.8, -9.7, -15.8, -16.3, -14.7, -17.6],
          o1989=[-32.6, -25.4, -20.5, -10.8, -0.8, -8.8, 0.0, -3.4, -3.1, -7.8, -16.0, -7.5, -14.0, -12.7, -13.4, -17.8],
          o2046=[-31.9, -25.3, -20.7, -10.1, -0.5, -9.9, 0.0, -4.7, -4.5, -9.1, -18.9, -11.7, -15.0, -15.8, -17.2, -17.9])
ORDER_TARGET = {"on1400": np.array(_D["c1493"]), "on1700": np.mean([_D["c1649"], _D["c1807"]], 0),
                "on2000": np.mean([_D[k] for k in ("c1868", "c1953", "c1986", "o1937", "o1989", "o2046")], 0)}


def law_centroid(fam, R):
    c0, r0, beta = CENTROID_LAW[fam]
    return c0 * (R / r0) ** beta


# --- i/o --------------------------------------------------------------------------------------------------------------
def read(path):
    """16-bit 44.1 kHz WAV -> float (a stereo file's first channel)."""
    with wave.open(str(path)) as w:
        sr, ch, n, sw = w.getframerate(), w.getnchannels(), w.getnframes(), w.getsampwidth()
        if sw != 2 or sr != SR:
            raise SystemExit(f"{path}: 16-bit 44.1 kHz PCM WAV expected")
        x = np.frombuffer(w.readframes(n), "<i2").astype(np.float64).reshape(-1, ch) / 32768
    return x[:, 0]


def write(path, y):
    """16-bit mono, clipped to full scale."""
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 32767 / 32768) * 32768).round().clip(-32768, 32767).astype("<i2").tobytes())


def rms(x):
    return float(np.sqrt(np.mean(x ** 2)))


def db(v):
    return float(20 * np.log10(v + 1e-12))


# --- spectra (the reference's measures: 8192-point Hann frames, each normalised to its 20 Hz-16 kHz total) --------------
NFFT = 8192
OCT8 = np.array([63, 125, 250, 500, 1000, 2000, 4000, 8000], float)
OCT10 = np.array([31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000])


def freqs(sr, n=NFFT):
    return np.fft.rfftfreq(n, 1 / sr)


def spec_frames(x, sr, times, n=NFFT, chunk=512):
    """Power spectra (Hann, n samples centred on each time) -> P[frames, n//2+1] (float32, as measured)."""
    w = np.hanning(n).astype(np.float32)
    half = n // 2
    idx = (np.asarray(times) * sr).astype(int)
    P = np.zeros((len(idx), n // 2 + 1), np.float32)
    xp = np.concatenate([np.zeros(half, np.float32), x, np.zeros(half, np.float32)])
    for s in range(0, len(idx), chunk):
        ii = idx[s:s + chunk]
        seg = np.stack([xp[i:i + n] for i in ii])
        P[s:s + len(ii)] = np.abs(np.fft.rfft(seg * w, axis=1)) ** 2
    return P


def octaves(Pm, f):
    """Octave levels (dB re the 20 Hz-16 kHz total) of a mean power spectrum, at OCT10."""
    tot = Pm[(f >= 20) & (f < 16000 * 2 ** 0.5)].sum()
    return np.array([10 * np.log10(Pm[(f >= c / 2 ** 0.5) & (f < c * 2 ** 0.5)].sum() / tot + 1e-15) for c in OCT10])


def centroid(Pm, f, lo=20.0, hi=16000.0):
    m = (f >= lo) & (f <= hi)
    return float((f[m] * Pm[..., m]).sum(-1) / (Pm[..., m].sum(-1) + 1e-20))


def ltas_psd(x, circular=True):
    """Octaves of the long-term spectrum (unit RMS, 16384-point Hann, mean power per bin, dB); circular=True tiles a
    loop so its wrap is measured like any other point."""
    N = 16384
    w = np.hanning(N)
    x = x / rms(x)
    if circular:
        xx = np.tile(x, max(2, int(np.ceil(2 * N / len(x))) + 1))
        starts = range(0, len(x), N // 2)
    else:
        xx = x
        starts = range(0, len(x) - N, N // 2)
    S = np.mean([np.abs(np.fft.rfft(xx[i:i + N] * w)) ** 2 for i in starts], axis=0)
    f = np.fft.rfftfreq(N, 1 / SR)
    return np.array([10 * np.log10(S[(f >= c / 2 ** 0.5) & (f < c * 2 ** 0.5)].mean() + 1e-12) for c in OCT8])


def m4_loop(x, hop=0.05):
    """The octave shape on a loop (circular): octaves 63..8k in dB re the 20 Hz-16 kHz total, the centroid (Hz), and
    the mean normalised power spectrum."""
    f = freqs(SR)
    L = len(x) / SR
    tt = np.arange(0.0, L, hop) + L
    P = spec_frames(np.tile(x, 3).astype(np.float32), SR, tt)
    Pn = (P / P[:, (f >= 20) & (f <= 16000)].sum(1, keepdims=True)).mean(0)
    return octaves(Pn, f)[1:9], centroid(Pn, f), Pn


def third_oct(Pn, lo=50.0, hi=10000.0):
    """third-octave levels (dB re total) of a mean normalised 8192-point spectrum."""
    f = freqs(SR)
    cs = 1000.0 * 2 ** (np.arange(-13, 11) / 3.0)
    cs = cs[(cs >= lo) & (cs <= hi)]
    tot = Pn[(f >= 20) & (f <= 16000)].sum()
    return cs, np.array([10 * np.log10(Pn[(f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))].sum() / tot + 1e-15) for c in cs])


def fluct(x, sr, t0, t1, win=0.1, hop=0.025, ma=1.0):
    """The natural-fluctuation measure: 100 ms windows (hop 25 ms), level (dB) and centroid (20 Hz-16 kHz); the
    residual after a centred 1 s moving average: level sd (dB), centroid sd (% of the mean)."""
    seg = x[int(t0 * sr):int(t1 * sr)].astype(np.float64)
    W, H = int(win * sr), int(hop * sr)
    n = (len(seg) - W) // H
    fr = np.stack([seg[i * H:i * H + W] for i in range(n)])
    L = 10 * np.log10(np.mean(fr ** 2, 1) + 1e-12)
    S = np.abs(np.fft.rfft(fr * np.hanning(W), 8192, axis=1)) ** 2
    f = np.fft.rfftfreq(8192, 1 / sr); m = (f >= 20) & (f <= 16000)
    C = (f[m] * S[:, m]).sum(1) / (S[:, m].sum(1) + 1e-20)
    k = int(round(ma / hop)) | 1
    ker = np.ones(k) / k
    Lr = (L - np.convolve(L, ker, "same"))[k // 2:n - k // 2]
    Cm = np.convolve(C, ker, "same")
    Cr = ((C - Cm) / Cm)[k // 2:n - k // 2]
    return dict(lev_sd=float(np.std(Lr)), cen_sd_pct=float(100 * np.std(Cr)))


def fluct_loop(x):
    """The fluctuation on a loop (circular: tiled, at least one whole period and 2.5 s measured, 0.6 s of lead-in
    either side)."""
    L = len(x) / SR
    span = max(L, 2.5)
    k = int(np.ceil((span + 1.2) / L)) + 1
    return fluct(np.tile(x, k).astype(np.float32), SR, 0.6, 0.6 + span)


# --- engine-cycle measures ---------------------------------------------------------------------------------------------
def comb_score(x, R, fmax=900.0, win=None):
    """How far the half-order lines (k R/120 Hz) stand over the points halfway between them (mean dB)."""
    W = int((win or max(0.25, 4 * 120.0 / R)) * SR)
    N = 1 << int(np.ceil(np.log2(W * 4)))
    f = np.fft.rfftfreq(N, 1 / SR)
    han = np.hanning(W)
    b = R / 120.0
    k = np.arange(1, int(fmax / b) + 1)
    out = []
    xx = np.tile(x, 2 + W // len(x) + 1)
    for s in range(0, len(x), W // 2):
        Lv = 20 * np.log10(np.abs(np.fft.rfft(xx[s:s + W] * han, N)) + 1e-7)
        out.append(np.interp(k * b, f, Lv).mean() - np.interp((k - 0.5) * b, f, Lv).mean())
    return float(np.mean(out))


def coherence(x, R):
    """adjacent 720-degree cycles' correlation at R (circular): mean, p5."""
    Lc = 120.0 / R * SR
    xx = np.tile(x, 2)
    n = int(len(x) // Lc) + 1
    C = xx[(np.arange(n)[:, None] * Lc + np.arange(int(Lc))[None, :]).astype(int)]
    C = C - C.mean(1, keepdims=True)
    r = (C[:-1] * C[1:]).sum(1) / (np.linalg.norm(C[:-1], axis=1) * np.linalg.norm(C[1:], axis=1) + 1e-12)
    return float(r.mean()), float(np.percentile(r, 5))


def seam_pct(x):
    """The wrap's second difference as a percentile of the loop's own (a seam would sit near 100)."""
    d2 = np.abs(np.diff(np.r_[x[-1], x, x[0]], 2))
    return float(100 * np.mean(d2 < d2[0]))


def _biquad_mag(b, a, f, fs=48000.0):
    z = np.exp(-2j * np.pi * f / fs)
    return np.abs((b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z))


def kweight_mag(f):
    k = _biquad_mag([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585], f)
    return k * _biquad_mag([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621], f)


def loudness_loop(x):
    """BS.1770 K-weighted level of a loop (circular, exact for a periodic signal), dB (LUFS = this - 0.691)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    w = np.full(len(f), 2.0)
    w[0] = 1.0
    if len(x) % 2 == 0:
        w[-1] = 1.0
    return float(10 * np.log10((w * np.abs(X * kweight_mag(f)) ** 2).sum() / len(x) ** 2 + 1e-20))


# --- per-pulse leveling (the on-load pulse-grain loops) -------------------------------------------------------------------
def split_bands(x, fc):
    """circular zero-phase split at fc (a one-octave raised-cosine crossover in log f): (LF, HF), LF + HF = x."""
    n = len(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    u = np.clip(np.log2(np.maximum(f, 1.0)) - np.log2(fc / 2 ** 0.5), 0, 1)
    lf = np.fft.irfft(np.fft.rfft(x) * (0.5 + 0.5 * np.cos(np.pi * u)), n)
    return lf, x - lf


def refine_onsets(x, ons, fc=700.0, lead=125, span=176, k_ms=3.0):
    """each listed onset moved to the sample within +-4 ms of (onset - lead) where the HF energy 3 ms after over 3 ms
    before peaks (the attack: +13..+22 dB)."""
    _, hf = split_bands(x, fc)
    L = len(x)
    k = int(k_ms * 1e-3 * SR)
    c = np.concatenate([[0.0], np.cumsum(np.tile(hf, 2) ** 2)])
    out = []
    for o in ons:
        q = (o - lead + np.arange(-span, span + 1, 2)) % L
        q = np.where(q < k, q + L, q)
        v = (c[q + k] - c[q]) / (c[q] - c[q - k] + 1e-20)
        out.append(int(q[int(np.argmax(v))] % L))
    return np.sort(np.array(out))


def _pulse_env(n, bounds, gains, ramp):
    env = np.empty(n)
    seg = [(bounds[i], bounds[(i + 1) % len(bounds)]) for i in range(len(bounds))]
    for (s, e), gv in zip(seg, gains):
        env[np.arange(s, e if e > s else e + n) % n] = gv
    w = 0.5 - 0.5 * np.cos(np.pi * (np.arange(ramp) + 0.5) / ramp)
    for i, (s, e) in enumerate(seg):          # from the previous pulse's gain to this one's, the ramp ending at s
        env[(s - ramp + np.arange(ramp)) % n] = gains[i - 1] + (gains[i] - gains[i - 1]) * w
    return env, seg


def pulse_level(x, ons, fc=700.0, alpha_hf=0.0, alpha_lev=0.0, smooth=7, ramp_ms=2.0, guard_ms=1.0):
    """per firing pulse (from guard_ms before one attack to guard_ms before the next):
    alpha_hf pulls the pulse's HF/LF energy ratio toward its cylinder's median (A and B apart) by that share in log;
    alpha_lev pulls the pulse's level toward a circular moving average over `smooth` pulses (the slow flutter stays).
    The gains change in a raised-cosine ramp ending guard_ms before each attack (the quiet before it); the envelope
    is periodic, so the wrap stays as seamless as it was. Returns (y, info)."""
    n = len(x)
    g = int(guard_ms * 1e-3 * SR)
    bounds = np.sort((ons - g) % n)
    R = int(ramp_ms * 1e-3 * SR)
    lf, hf = split_bands(x, fc)
    seg = [(bounds[i], bounds[(i + 1) % len(bounds)]) for i in range(len(bounds))]
    idx = [np.arange(s, e if e > s else e + n) % n for s, e in seg]
    lr = np.array([np.log(np.sum(hf[i] ** 2) / (np.sum(lf[i] ** 2) + 1e-20) + 1e-20) for i in idx])
    cyl = np.arange(len(lr)) % 2
    dev = lr.copy()
    for c in (0, 1):
        dev[cyl == c] -= np.median(lr[cyl == c])
    g_hf = np.exp(-alpha_hf * dev / 2)
    env_hf, _ = _pulse_env(n, bounds, g_hf, R)
    y = lf + hf * env_hf
    lv = np.array([10 * np.log10(np.mean(y[i] ** 2) + 1e-20) for i in idx])
    k = np.ones(smooth) / smooth
    trend = np.convolve(np.r_[lv[-(smooth // 2):], lv, lv[:smooth // 2]], k, "valid")
    dl = lv - trend
    for c in (0, 1):                          # the A/B level difference is the engine's: keep it
        dl[cyl == c] -= np.mean(dl[cyl == c])
    g_lev = 10 ** (-alpha_lev * dl / 20)
    env_lev, _ = _pulse_env(n, bounds, g_lev, R)
    y = y * env_lev
    return y, dict(pulses=len(seg), hf_dev_sd_ln=round(float(np.std(dev)), 3), hf_gain_sd_dB=round(float(np.std(20 * np.log10(g_hf))), 2),
                   lev_dev_sd_dB=round(float(np.std(dl)), 2), lev_gain_sd_dB=round(float(np.std(20 * np.log10(g_lev))), 2))


# --- the within-cycle envelope crest -----------------------------------------------------------------------------------------
CREST_BANDS = [(354, 707), (707, 1414), (1414, 2828), (2828, 5657), (5657, 11314), (11314, 16000)]


def band_masks(n, edges=(354, 707, 1414, 2828, 5657, 11314)):
    """complementary zero-phase masks (raised-cosine crossovers a third of an octave wide in log f) for the bands
    below edges[0], between the edges and above edges[-1]; they sum to 1 at every frequency."""
    f = np.fft.rfftfreq(n, 1 / SR)
    lf = np.log2(np.maximum(f, 1.0))
    lows = []
    for e in edges:   # low-pass at e
        u = np.clip((lf - (np.log2(e) - 1 / 6)) / (1 / 3), 0, 1)
        lows.append(0.5 + 0.5 * np.cos(np.pi * u))
    M = [lows[0]] + [lows[i + 1] - lows[i] for i in range(len(edges) - 1)] + [1 - lows[-1]]
    return M


def _circ_smooth(v, ms):
    n = len(v)
    W = max(3, int(ms * 1e-3 * SR) | 1)
    k = np.zeros(n)
    h = np.hanning(W + 2)[1:-1]
    h /= h.sum()
    k[:W] = h
    k = np.roll(k, -(W // 2))
    return np.fft.irfft(np.fft.rfft(v) * np.fft.rfft(k), n)


def _band_cycle_crests(x, R, circular=True):
    """per band: each 720-degree cycle's band peak (2 ms windows, 1 ms hop) over the cycle's median, dB."""
    xx = np.tile(x, 3) if circular else x
    X = np.fft.rfft(xx)
    f = np.fft.rfftfreq(len(xx), 1 / SR)
    W, H = int(0.002 * SR), int(0.001 * SR)
    st = np.arange(0, len(xx) - W, H)
    te = (st + W / 2) / SR
    a, b = (len(x) / SR, 2 * len(x) / SR) if circular else (0.0, len(x) / SR)
    T = 120.0 / R
    out = []
    for lo, hi in CREST_BANDS:
        Y = X.copy()
        Y[(f < lo) | (f >= hi)] = 0
        y = np.fft.irfft(Y, len(xx))
        c = np.concatenate([[0.0], np.cumsum(y ** 2)])
        e = 10 * np.log10((c[st + W] - c[st]) / W + 1e-15)
        res, k = [], 0
        while a + (k + 1) * T <= b:
            s = (te >= a + k * T) & (te < a + (k + 1) * T)
            res.append(e[s].max() - np.median(e[s]))
            k += 1
        out.append(res)
    return out


def band_crest(x, R, circular=True):
    """per band, the median over cycles of each cycle's band peak over its median (dB)."""
    return np.array([np.median(res) for res in _band_cycle_crests(x, R, circular)])


def band_crest_dist(x, R, circular=True, qs=(10, 50, 90)):
    """band_crest's per-cycle values as percentiles [band][q]."""
    return np.array([np.percentile(res, qs) for res in _band_cycle_crests(x, R, circular)])


def _circ_median(v, win):
    """circular running median of v over win samples (centred)."""
    from numpy.lib.stride_tricks import sliding_window_view as swv
    h = win // 2
    vv = np.r_[v[-h:], v, v[:win - h - 1]]
    return np.median(swv(vv, win), 1)


def crest_shift(x, R, shift_db, knee_lo=3.0, knee_w=6.0, env_ms=1.0, gain_ms=1.0, hop_ms=1.0):
    """per band (band_masks; under 354 Hz untouched): the attacks are lowered by a fixed amount instead of being held
    under a ceiling, so the pulse-to-pulse spread of attack strength is kept: with L the energy envelope (zero-phase
    1 ms) in dB over its running median across one cycle, the gain is -shift x clip((L - knee_lo) / knee_w, 0, 1) dB
    (no change under knee_lo dB, the full shift from knee_lo + knee_w up), smoothed over gain_ms; circular."""
    n = len(x)
    X = np.fft.rfft(x)
    M = band_masks(n)
    y = np.fft.irfft(X * M[0], n)
    hop = int(hop_ms * 1e-3 * SR)
    nd = n // hop
    win = max(3, int(round(120.0 / R / (hop_ms * 1e-3))))
    cuts = []
    for b, sdb in enumerate(shift_db):
        yb = np.fft.irfft(X * M[b + 1], n)
        if sdb <= 0:
            y += yb
            cuts.append(0.0)
            continue
        e = _circ_smooth(yb ** 2, env_ms) + 1e-14
        ed = e[:nd * hop].reshape(nd, hop).mean(1)
        md = _circ_median(np.log(ed), win)
        m = np.exp(np.interp(np.arange(n) / hop - 0.5, np.arange(nd), md, period=nd))
        L = 10 * np.log10(e / m)
        gdb = -sdb * np.clip((L - knee_lo) / knee_w, 0, 1)
        gdb = _circ_smooth(gdb, gain_ms)
        y += yb * 10 ** (gdb / 20)
        cuts.append(round(float(np.percentile(-gdb, 99)), 1))
    return y, cuts


def fit_crest_shift(x, R, target, iters=7, slack=1.0, **kw):
    """per band, the shift (0..24 dB) that brings the median per-cycle crest to the target; bands within slack of the
    target (or under it) are left alone."""
    t = np.asarray(target, float)
    c0 = band_crest(x, R)
    need = c0 > t + slack
    lo, hi = np.zeros(len(t)), np.full(len(t), 24.0)
    for _ in range(iters):
        mid = (lo + hi) / 2
        y, _ = crest_shift(x, R, np.where(need, mid, 0.0), **kw)
        over = band_crest(y, R) > t
        lo = np.where(over, mid, lo)
        hi = np.where(over, hi, mid)
    sh = np.where(need, (lo + hi) / 2, 0.0)
    y, cuts = crest_shift(x, R, sh, **kw)
    return y, sh, c0, band_crest(y, R), cuts


# --- the tone match on octave and third-octave nodes, toward a centroid -------------------------------------------------
SMOOTH_SD = 0.75     # thirds: the smoothing (Gaussian sd, in thirds, in power) of the loop's and the target's thirds
NODES = np.r_[63.0, 1000.0 * 2 ** (np.arange(-10, -2) / 3.0), 1000.0, 2000.0, 4000.0, 8000.0]   # thirds 99.2 .. 500 Hz
TH_IDX = list(range(3, 11))    # the targets' "third" (50 Hz .. 8 kHz, 1000 * 2^(k/3), k = -13..9): 99.2 .. 500 Hz
CUT_CAP, BOOST_CAP = 12.0, 8.0 # cuts may go deeper than boosts (a cut raises no noise floor)
TC = 1000.0 * 2 ** (np.arange(-13, 10) / 3.0)      # the 23 third-octave centres of the targets (50 Hz .. 8 kHz)


def _smooth_db(th_db):
    """thirds (dB) smoothed in power over neighbouring thirds (Gaussian, sd SMOOTH_SD thirds)."""
    k = np.arange(len(th_db))
    W = np.exp(-0.5 * ((k[:, None] - k[None, :]) / SMOOTH_SD) ** 2)
    W /= W.sum(1, keepdims=True)
    return 10 * np.log10(W @ 10 ** (np.asarray(th_db) / 10) + 1e-20)


def _nodes_from(o, th):
    """node levels from the 8 octaves and the 23 thirds."""
    t = _smooth_db(th)
    return np.r_[o[0], t[TH_IDX], o[4:8]]


def eq_curve_n(f, gains_db):
    """the smooth gain curve (dB) through the node gains (cosine in log f between nodes, flat outside; a boost at 63 Hz
    fades to 0 dB at 20 Hz, so no sub-audible rumble is raised)."""
    g = np.asarray(gains_db, float)
    lc = np.log2(NODES)
    lf = np.log2(np.maximum(f, 1.0))
    out = np.zeros(len(f))
    out[lf <= lc[0]] = g[0]
    out[lf >= lc[-1]] = g[-1]
    for i in range(len(lc) - 1):
        m = (lf >= lc[i]) & (lf < lc[i + 1])
        u = (lf[m] - lc[i]) / (lc[i + 1] - lc[i])
        w = 0.5 - 0.5 * np.cos(np.pi * u)
        out[m] = g[i] * (1 - w) + g[i + 1] * w
    if g[0] > 0:
        lo = (f < 40.0)
        u = np.clip((np.log2(np.maximum(f[lo], 1.0)) - np.log2(20.0)) / (np.log2(40.0) - np.log2(20.0)), 0, 1)
        out[lo] = g[0] * u
    return out


def apply_eq_n(x, gains_db):
    """zero-phase, circular (one FFT over the loop: a circular convolution of a periodic signal is periodic, so the
    wrap stays as seamless as built)."""
    n = len(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    return np.fft.irfft(np.fft.rfft(x) * 10 ** (eq_curve_n(f, gains_db) / 20), n)


def node_levels(x):
    """the loop's levels at the nodes and its centroid, octaves and thirds."""
    o, c, Pn = m4_loop(x)
    th = third_oct(Pn)[1]
    return _nodes_from(o, th), c, o, th


def target_nodes(tg, tilt=0.0):
    """a target's levels at the nodes, tilted by `tilt` dB per octave about 1 kHz."""
    o, th = np.asarray(tg["m4"], float), np.asarray(tg["third"], float)
    return _nodes_from(o, th) + tilt * np.log2(NODES / 1000.0)


def _predict(Pn, f, gains):
    """the node levels and centroid of a mean spectrum Pn after the curve `gains` (the EQ is zero-phase and smooth, so
    the frames' spectra are Pn x |H|^2 to within the window's leakage)."""
    P = Pn * 10 ** (eq_curve_n(f, gains) / 10)
    tot_o = P[(f >= 20) & (f < 16000 * 2 ** 0.5)].sum()
    tot_t = P[(f >= 20) & (f <= 16000)].sum()
    o = np.array([10 * np.log10(P[(f >= c / 2 ** 0.5) & (f < c * 2 ** 0.5)].sum() / tot_o + 1e-15) for c in OCT8])
    th = np.array([10 * np.log10(P[(f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))].sum() / tot_t + 1e-15) for c in TC])
    m = (f >= 20) & (f <= 16000)
    return _nodes_from(o, th), float((f[m] * P[m]).sum() / P[m].sum())


def fit_eq_n(x, tnodes, base=None, lam=0.05, ridge=0.002, iters=30, outer=2):
    """node gains g (base: the curve already applied to x; base + g held within -CUT_CAP..+BOOST_CAP) bringing the loop's
    node levels to the target shape, by a bounded Levenberg-Marquardt fit on the predicted spectrum (_predict) with a
    smoothness penalty lam on the increment's slope (dB^2 per octave) and a small ridge on g; then `outer` corrections
    of the target by the measured-minus-predicted levels. Returns (g, node levels, centroid)."""
    base = np.zeros(len(NODES)) if base is None else np.asarray(base, float)
    f = freqs(SR)
    _, _, Pn = m4_loop(x)
    lo, hi = -CUT_CAP - base, BOOST_CAP - base
    dl = np.diff(np.log2(NODES))
    t_eff = np.asarray(tnodes, float).copy()

    def resid(g):
        lv, _ = _predict(Pn, f, g)
        d = lv - t_eff
        d -= d.mean()
        return np.r_[d, np.sqrt(lam) * np.diff(g) / np.sqrt(dl), np.sqrt(ridge) * g]    # the increment kept smooth
    g = np.zeros(len(NODES))
    for _ in range(outer + 1):
        mu = 1.0
        r = resid(g)
        for _ in range(iters):
            J = np.empty((len(r), len(g)))
            for k in range(len(g)):
                e = np.zeros(len(g)); e[k] = 0.05
                J[:, k] = (resid(g + e) - r) / 0.05
            A_, b_ = J.T @ J, J.T @ r
            while True:
                gn = np.clip(g - np.linalg.solve(A_ + mu * np.eye(len(g)), b_), lo, hi)
                rn = resid(gn)
                if rn @ rn < r @ r or mu > 1e6:
                    break
                mu *= 4.0
            if rn @ rn < r @ r:
                done = (r @ r - rn @ rn) < 1e-6
                g, r, mu = gn, rn, max(mu / 4.0, 1e-4)
                if done:
                    break
            else:
                break
        lv_m, _, _, _ = node_levels(apply_eq_n(x, g))
        lv_p, _ = _predict(Pn, f, g)
        t_eff = t_eff + ((lv_p - lv_p.mean()) - (lv_m - lv_m.mean()))
    lv, c, _, _ = node_levels(apply_eq_n(x, g))
    return g, lv, c


def fit_eq_centroid(x, tg, c_target, base=None, lo=-3.0, hi=3.0, iters=8):
    """the tilt (dB per octave) of the target shape whose fitted EQ puts the loop's centroid on c_target (bisection);
    returns (gains, tilt, node levels after, centroid after)."""
    best = None
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        g, lv, c = fit_eq_n(x, target_nodes(tg, mid), base, outer=1)
        if best is None or abs(c - c_target) < abs(best[3] - c_target):
            best = (g, mid, lv, c)
        if c > c_target:
            hi = mid
        else:
            lo = mid
    g, lv, c = fit_eq_n(x, target_nodes(tg, best[1]), base)
    return (g, best[1], lv, c) if abs(c - c_target) <= abs(best[3] - c_target) else best


def limit_smooth(y, ceil_db=-1.0, look_ms=1.0):
    """a look-ahead gain limiter: the gain each sample needs to stay under ceil_db, its minimum over +-look_ms, then
    averaged over +-look_ms (so the gain never exceeds what any sample needs, and every change is a ~2 ms ramp);
    circular, so the loop's wrap is untouched. Returns (y, samples whose gain is under 1, max cut dB)."""
    c = 10 ** (ceil_db / 20)
    a = np.abs(y)
    need = np.minimum(1.0, c / np.maximum(a, 1e-12))
    W = int(look_ms * 1e-3 * SR)
    g1 = need.copy()
    for s in range(1, W + 1):
        g1 = np.minimum(g1, np.minimum(np.roll(need, s), np.roll(need, -s)))
    k = 2 * W + 1
    cs = np.concatenate([[0.0], np.cumsum(np.r_[g1[-W:], g1, g1[:W]])])
    g2 = (cs[k:] - cs[:-k]) / k
    g2 = np.minimum(g2, need)                       # guards the float rounding of the running mean
    return y * g2, int((g2 < 0.99999).sum()), float(-20 * np.log10(g2.min()))


# --- the half-order line pattern ---------------------------------------------------------------------------------------------
ORDER_K = np.arange(1, 17)          # half-orders k (order k/2), k * R/120 Hz
ORDER_CAP = 8.0


def order_levels(x, R, win=0.5):
    """each half-order line's peak power over 0.5 s frames (Hann, zero-padded to 2^17) on a loop at its base (tiled),
    dB re the strongest."""
    W = int(win * SR)
    Nf = 1 << 17
    w = np.hanning(W)
    f = np.fft.rfftfreq(Nf, 1 / SR)
    xx = np.tile(x, 2)
    acc = np.zeros(len(ORDER_K))
    n = 0
    for s in range(0, len(x), W // 2):
        Pw = np.abs(np.fft.rfft(xx[s:s + W] * w, Nf)) ** 2
        for i, k in enumerate(ORDER_K):
            fk = k * R / 120.0
            m = np.abs(f - fk) < 0.012 * fk + 1.0
            acc[i] += Pw[m].max()
        n += 1
    v = 10 * np.log10(acc / n)
    return v - v.max()


def order_eq(x, R, gains_db):
    """per half-order gains on the loop's line frequencies (cosine-interpolated in linear frequency between lines,
    the first line's gain below it, tapering to 0 dB from line 16.5 to 18); zero-phase, circular. The gains follow
    the orders when the loop is pitched."""
    n = len(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    f0 = R / 120.0
    u = f / f0
    g = np.interp(u, ORDER_K, gains_db)
    lo = u < ORDER_K[0]
    g[lo] = gains_db[0]
    k0 = np.clip(np.floor(u).astype(int), 1, ORDER_K[-1] - 1)
    fr = np.clip(u - k0, 0, 1)
    w = 0.5 - 0.5 * np.cos(np.pi * fr)
    gi = np.asarray(gains_db)
    mid = (u >= ORDER_K[0]) & (u <= ORDER_K[-1])
    g[mid] = gi[k0[mid] - 1] * (1 - w[mid]) + gi[k0[mid]] * w[mid]
    hi = u > ORDER_K[-1]
    taper = np.clip((18.0 - u[hi]) / 1.5, 0, 1)
    g[hi] = gi[-1] * (0.5 - 0.5 * np.cos(np.pi * taper))
    return np.fft.irfft(np.fft.rfft(x) * 10 ** (g / 20), n)


def fit_order_eq(x, R, target, iters=3):
    """the per-order gains (within +-ORDER_CAP) bringing the loop's half-order pattern to the target pattern, the
    lines' total power kept (so the centroid and the tone match stay where they were). Returns (y, gains, levels
    before, after)."""
    t = np.asarray(target, float)
    g = np.zeros(len(ORDER_K))
    o0 = order_levels(x, R)
    y = x
    for _ in range(iters):
        o = order_levels(y, R)
        d = (t - t.mean()) - (o - o.mean())
        g = g + d
        g = np.clip(g - g.mean(), -ORDER_CAP, ORDER_CAP)
        P = 10 ** (order_levels(x, R) / 10)
        g = np.clip(g - 10 * np.log10(np.sum(P * 10 ** (g / 10)) / np.sum(P)), -ORDER_CAP, ORDER_CAP)
        y = order_eq(x, R, g)
    return y, g, o0, order_levels(y, R)


# --- the build ----------------------------------------------------------------------------------------------------------------
def level(y):
    """scale to -13.5 dBFS RMS, limit, and correct the gain until the limited file's RMS is -13.50; quantised to 16 bits.
    Also what the limiter changed: re the loop and re the loop's own 4-16 kHz band."""
    g = LOOP_RMS / rms(y)
    for _ in range(4):
        z, n, _ = limit_smooth(y * g)
        g *= LOOP_RMS / rms(z)
    z, n, cut = limit_smooth(y * g)
    q = np.clip(np.round(z * 32768), -32768, 32767) / 32768
    d = z - y * g
    f = np.fft.rfftfreq(len(y), 1 / SR)
    hb = (f >= 4000) & (f <= 16000)
    D_, Y_ = np.fft.rfft(d), np.fft.rfft(y * g)
    dist = dict(re_loop_dB=round(db(np.sqrt(np.sum(d ** 2) / np.sum((y * g) ** 2))), 1),
                re_4_16k_band_dB=round(float(10 * np.log10(np.sum(np.abs(D_[hb]) ** 2) / np.sum(np.abs(Y_[hb]) ** 2) + 1e-20)), 1))
    return q, n, g, cut, db(np.abs(y * g).max()), dist


def r1(v):
    return [round(float(u), 1) for u in v]


def build_one(key, src, x, attacks):
    """One loop (key e.g. "on2000") from its material x; attacks: the grain tool's attack samples (grains only).
    Returns (the 16-bit loop, its report)."""
    B = int(key[-4:])
    fam = "off" if key.startswith("off") else "on"
    tg = TARGETS[key]
    t = np.array(tg["m4"])
    c_t = law_centroid(fam, B)
    o0, c0, _ = m4_loop(x)
    lv0, _, _, _ = node_levels(x)
    # (1) the tone match
    g, tilt0, _, _ = fit_eq_centroid(x, tg, c_t)
    y = apply_eq_n(x, g)
    # (2) the within-cycle envelope crest
    ct = np.array(CREST[key])
    cb = band_crest(y, B)
    if np.any(cb > ct + CREST_SLACK):
        y, sh, cb0, cb1, cuts = fit_crest_shift(y, B, ct, slack=CREST_SLACK, knee_lo=3.0, knee_w=6.0)
        crest = dict(target=r1(ct), before=r1(cb0), after_shift=r1(cb1), attack_shift_dB=r1(sh), attack_cut_p99_dB=cuts)
    else:
        crest = dict(target=r1(ct), before=r1(cb), after_shift=None)
    g_pre = g.copy()
    g2 = g3 = None
    tilt = tilt0
    if crest["after_shift"] is not None:
        # the tone match fitted again on the shaped loop (the sum of the curves held within the caps), the tilt found
        # again (the attack shaping darkens the loop)
        g2, tilt, _, _ = fit_eq_centroid(y, tg, c_t, base=g, lo=tilt0 - 1.5, hi=tilt0 + 1.5, iters=7)
        y = apply_eq_n(y, g2)
        g = g + g2
    # (3) the half-order line pattern toward the reference's (where measured), before the pulse leveling, so its choice
    # is made on the final line pattern
    ordq = None
    if key in ORDER_TARGET:
        y, og, oo0, oo1 = fit_order_eq(y, B, ORDER_TARGET[key])
        tt = ORDER_TARGET[key]
        ordq = dict(target=r1(tt), gains_dB=r1(og), before=r1(oo0), after=r1(oo1),
                    rms_before=round(float(np.sqrt(np.mean(((oo0 - oo0.mean()) - (tt - tt.mean())) ** 2))), 2),
                    rms_after=round(float(np.sqrt(np.mean(((oo1 - oo1.mean()) - (tt - tt.mean())) ** 2))), 2))
    # (4) the on-load grains loops' pulse-to-pulse brightness, judged on the re-fitted tone
    plev = None
    if src == "grains" and fam == "on":
        ons = refine_onsets(apply_eq_n(x, g_pre), np.sort(np.array(attacks, int)), lead=0)
        f0 = fluct_loop(y)
        trials = [(f0["cen_sd_pct"], 0.0, None, 0.0, y, dict(hf_gain_sd_dB=0.0))]
        for fc in (700.0, 1000.0):
            for al in (0.25, 0.5, 0.75, 1.0):
                yy, info = pulse_level(y, ons, fc, al)
                trials.append((fluct_loop(yy)["cen_sd_pct"], info["hf_gain_sd_dB"], fc, al, yy, info))
        ok = [tr for tr in trials if tr[0] <= 8.0]
        best = min(ok, key=lambda tr: tr[1]) if ok else min(trials, key=lambda tr: tr[0])
        y = best[4]
        f1 = fluct_loop(y)
        plev = dict(fc_Hz=best[2], alpha=best[3], **best[5], before=dict(lev=round(f0["lev_sd"], 2), cen=round(f0["cen_sd_pct"], 1)),
                    after=dict(lev=round(f1["lev_sd"], 2), cen=round(f1["cen_sd_pct"], 1)))
    # after a pulse leveling, the tone fitted once more (the tilt in a narrow range: a small change)
    if plev and plev["alpha"]:
        g3, tilt, _, _ = fit_eq_centroid(y, tg, c_t, base=g, lo=tilt - 0.5, hi=tilt + 0.5, iters=5)
        y = apply_eq_n(y, g3)
        g = g + g3
    # (5) the level
    q, n, gain, lim_cut, pk_before, lim_dist = level(y)
    o2, c2, _ = m4_loop(q)
    lv2, _, _, th2 = node_levels(q)
    tn_f = target_nodes(tg, tilt)
    fl = fluct_loop(q)
    rep = dict(key=key, base_rpm=B, family=fam, source=src, len_s=round(len(q) / SR, 3), target=tg["how"],
               centroid_law_Hz=round(c_t, 1), target_tilt_dB_per_oct=round(float(tilt), 2),
               eq_nodes_dB=dict(zip([f"{c:g}" for c in NODES], r1(g))),
               eq_capped=[f"{c:g}" for c, v in zip(NODES, g) if v <= -CUT_CAP + 0.05 or v >= BOOST_CAP - 0.05],
               nodes_before=r1(lv0), nodes_after=r1(lv2), nodes_target=r1(tn_f),
               nodes_resid_rms=round(float(np.sqrt(np.mean((lv2 - tn_f - np.mean(lv2 - tn_f)) ** 2))), 2),
               third_100_504_after=r1(th2[TH_IDX]), third_100_504_target=r1(np.asarray(tg["third"])[TH_IDX]),
               m4_before=r1(o0), m4_after=r1(o2), m4_target=r1(t),
               resid_rms_63_4k=round(float(np.sqrt(np.mean((o2 - t)[:7] ** 2))), 2),
               centroid_before=round(c0), centroid_after=round(c2), centroid_target=round(tg["centroid"]),
               psd_after=r1(ltas_psd(q)), rms_dBFS=round(db(rms(q)), 2), peak_dBFS=round(db(np.abs(q).max()), 2),
               limited_pct=round(100.0 * n / len(q), 3), limiter_max_cut_dB=round(lim_cut, 2),
               peak_before_limiter_dBFS=round(pk_before, 2), limiter_change=lim_dist,
               kloud_re_rms_dB=round(loudness_loop(q) - db(rms(q)), 2),
               seam_d2_pct=round(seam_pct(q), 1), seam_d2_pct_source=round(seam_pct(x), 1),
               eq_first_dB=r1(g_pre), eq_refit_dB=None if g2 is None else r1(g2),
               eq_final_refit_dB=None if g3 is None else [round(float(v), 2) for v in g3],
               crest=dict(crest, final=r1(band_crest(q, B)), dist_p10_50_90_final=np.round(band_crest_dist(q, B), 1).tolist()),
               pulse_leveling=plev, order_eq=ordq, m5_after=dict(lev=round(fl["lev_sd"], 2), cen=round(fl["cen_sd_pct"], 1)),
               coherence=round(coherence(q, B)[0], 3), comb=round(comb_score(q, B), 1))
    return q, rep


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grains", type=Path, required=True, help="make_grain_loops.py --out (its loops.json)")
    ap.add_argument("--unlimited", type=Path, required=True, help="make_grain_loops.py --unlimited (the loops)")
    ap.add_argument("--pieces", type=Path, required=True, help="make_piece_loops.py --out")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--only", default="", help="comma-separated keys to build, e.g. on2000,off2300 (default all)")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    gl = json.load(open(a.grains / "loops.json"))
    only = set(s for s in a.only.split(",") if s)
    rep = {}
    for key, src in PICK:
        if only and key not in only:
            continue
        stem = f"{'On' if key.startswith('on') else 'Off'}{key[-4:]}LP"
        if src == "grains":
            path, attacks = a.unlimited / f"CMB_EngineGrain{stem}.wav", gl[f"CMB_EngineGrain{stem}"]["attacks"]
        else:
            path, attacks = a.pieces / f"CMB_EnginePiece{stem}.wav", None
        q, r = build_one(key, src, read(path), attacks)
        name = FILE_NAME.get(key, f"CMB_Engine{stem}")
        write(a.out / f"{name}.wav", q)
        r["from_file"] = path.name
        rep[name] = r
        print(f"{name}: {src:6s} {r['len_s']:5.2f}s EQ {' '.join(f'{v:+.1f}' for v in r['eq_nodes_dB'].values())} (capped {r['eq_capped']}) "
              f"tilt {r['target_tilt_dB_per_oct']:+.2f} node resid {r['nodes_resid_rms']:.2f} dB cen {r['centroid_before']}->{r['centroid_after']} "
              f"(law {r['centroid_law_Hz']}, reference {r['centroid_target']}) rms {r['rms_dBFS']} peak {r['peak_dBFS']} (before "
              f"{r['peak_before_limiter_dBFS']}) limited {r['limited_pct']}% max cut {r['limiter_max_cut_dB']} dB; seam "
              f"{r['seam_d2_pct_source']}->{r['seam_d2_pct']}; M5 {r['m5_after']} coh {r['coherence']} comb {r['comb']}; crest "
              f"{r['crest']['before']} -> {r['crest']['final']} (target {r['crest']['target']})"
              + (f"; orders rms {r['order_eq']['rms_before']} -> {r['order_eq']['rms_after']} dB" if r["order_eq"] else "")
              + (f"; pulse leveling fc {r['pulse_leveling']['fc_Hz']} alpha {r['pulse_leveling']['alpha']}" if r["pulse_leveling"] else ""))
    if not only:
        for f in KEEP:
            shutil.copyfile(a.pieces / f, a.out / f)
            x = read(a.out / f)
            rep[f[:-4]] = dict(source=f"{a.pieces.name}/{f} (copied byte for byte)", len_s=round(len(x) / SR, 3),
                               rms_dBFS=round(db(rms(x)), 2), peak_dBFS=round(db(np.abs(x).max()), 2),
                               kloud_re_rms_dB=round(loudness_loop(x) - db(rms(x)), 2) if "LP" in f else None)
            print(f, rep[f[:-4]])
    with open(a.out / "loops.json", "w") as fh:
        json.dump(rep, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
