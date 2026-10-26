#!/usr/bin/env python3
"""The loops and one-shots cut from demodave's recording itself: the idle loop, the start, the stop, and the 2300 rpm
closed-throttle loop made of flattened pieces of the recording's falls.

  python3 -I make_piece_loops.py --idle <demodave's idle.wav> --out <dir>

The source: Freesound 502690 by demodave, "Harley Davidson Sportster - Idling with Engine Revs" (Creative Commons 0),
161.9 s, 16-bit 44.1 kHz stereo as downloaded. Its two channels are one signal 1024 samples (23.2 ms) apart: averaging
them builds a slapback into every pulse, so the tool takes the leading (right) channel, found by cross-correlation above
1.5 kHz (a mono file is taken as it is).

Writes, in --out (44.1 kHz 16-bit mono):
  CMB_EngineIdleLP.wav           the idle, ~860 rpm: a plain excerpt (92.0-98.3 s; the idle is too irregular to
                                 flatten), its loudness trend divided out, wrapped with a 40 ms crossfade at the end
                                 point (within the last 0.25 s) whose next 40 ms best match the start
  CMB_EngineStart.wav            the start, catching and settling to idle (0.25-2.6 s); its last 0.3 s at the idle
                                 loop's level in the game, the catch (about 23 dB over its own idle) compressed 4:1
                                 above twice that level
  CMB_EngineStop.wav             idle, then the engine cut (158.6-160.6 s); its first 0.5 s at the idle's level
  CMB_EnginePieceOff2300LP.wav   2300 rpm, throttle shut: flattened pieces of the falls after the blips (below)
  loops.json                     what each was made from, and its measures

The idle and the one-shots get a gentle tone match toward the riding loops (zero-phase FFT shelves: -4 dB under 100 Hz,
+3 dB over 700 Hz; circular over the idle loop, so its seam stays seamless; a one-shot is padded). Every loop is at
-13.5 dBFS RMS through a soft limiter (unchanged under -3.1 dBFS, a tanh bend above it that never reaches full scale);
the one-shots' idle parts are set to the idle's level in the game (-6 dB under the loop), so the hand-overs are level.
build_loops.py copies the idle, start and stop as they are.

The 2300 rpm closed-throttle loop. demodave blips the throttle 34 times, and after each blip the engine falls back
with the throttle shut, crossing 2300 rpm in a few cycles. Every engine cycle the recording holds is found first:
  1. a dechirped half-order comb map: per 10 ms frame (0.2 s Hann window, 25-1500 Hz), for 12 log-rpm slopes from
     -4/s to +6/s the window is warped so a path R exp(s (t - tc)) becomes constant, and every candidate R (700-6200,
     0.4 % steps) is scored by its half-order lines k R/120 Hz (every k, so the odd ones too) against the midpoints
     (fast blips and falls stay visible; a plain comb smears them);
  2. seeds: every 0.1 s, the map's three highest local maxima above 9 dB;
  3. from each seed not already covered, a cycle walker follows the engine one 720-degree cycle at a time (each next
     period, within +-12 % of the last, maximises the correlation of the next cycle stretched onto the mean of the
     last two; 30-3000 Hz), both ways, until the correlation stays under 0.5 for two cycles;
  4. each walked run (6 cycles and a mean correlation of 0.65 at least) is checked for the rpm scale on its
     flattened cycles: the lag-2 coherence not above lag-1 + 0.05 (else the walker's "cycle" is 360 degrees and the
     rpm reads 2x high), and the mean cycle's two 360-degree halves unlike (r < 0.6; alike = 1440 degrees, the rpm
     reads 2x low); where runs overlap, the one with the higher mean correlation keeps the time.
Then the pieces: runs of 2 or more consecutive cycles within +-6 % of 2300 rpm, falling (log-rpm slope over +-3
cycles at most -0.10 a second), walker r >= 0.65. Each is flattened at 2300 (the phase is the cycle count at the
walker's boundaries, monotone cubic in between, resampled to exactly n cycles of 120/2300 s: pitch and formants move by
at most the 6 %), its linear level trend over 40 ms windows divided out, and dropped if its flattened cycle-to-cycle
coherence is under 0.65. Each piece is EQ'd (zero-phase, cut only) so the pieces' pooled octave shape meets the
reference ride's closed-throttle shape at 2300 rpm (OFF2300_TARGET: numbers measured on the reference ride; nothing of
it is in the loop; cap +-8 dB), and each piece toward the pooled shape (weight n/(n + 0.5), cap +-6 dB). The pieces are
scaled to one RMS and chained greedily (tried from each of the 12 longest as the first; the chain whose worst join or
wrap is best is kept): the next piece is the unused one that best matches the chain's tail after alignment by sliding
cross-correlation (skipping up to half a cycle of its head, or trimming up to half a cycle off the chain's end), joined
over half a cycle with linear ramps normalised for the measured correlation. The chain is wrapped at the whole-cycle
end (searched over the last 2 cycles, +-0.5 cycle) whose next 2 cycles best match its first 2. build_loops.py takes
it from here (its tone match, levels and limiter); its own pulse-grain Off2300 stays 1.4 dB rms short of the tone
target at the EQ's +-8 dB cap, these pieces reach it."""
import argparse
import json
import os
import wave
from multiprocessing import Pool
from pathlib import Path

import numpy as np

SR = 44100
LOOP_RMS = 10 ** (-13.5 / 20)  # every loop's RMS
IDLE_LEVEL_DB = -6.0           # the level the idle plays at in the game, for the one-shots' joins (the files the user
                               # heard were made with -6 dB; the model's idle is -5.2 dB, and render.py and the game set
                               # the one-shots' level themselves)
KNEE = 0.7                     # the soft limiter: peaks above -3.1 dBFS bend smoothly towards full scale, never past it

IDLE_SPAN = (92.0, 98.3)
IDLE_BASE = 860.0
IDLE_WRAP_S = 0.040
START_SPAN, STOP_SPAN = (0.25, 2.6), (158.6, 160.6)
SHELF = dict(low_db=-4.0, high_db=3.0)   # the idle and the one-shots (half of the shelves the old light-throttle loops had)

# the flattened-piece loops: name, family, base rpm, the reference ride's octave shape there (63..8k Hz, dB re the
# 20 Hz-16 kHz total; 17 frames within +-6 % of 2300 rpm with the throttle shut)
PIECE_LOOPS = [("CMB_EnginePieceOff2300LP", "off", 2300, [-8.8, -1.9, -9.1, -16.6, -15.1, -16.4, -20.6, -27.1])]
TOL = 0.06                     # a cycle within +-6 % of the base
R_MIN = 0.65                   # the walker's correlation at least
MIN_CYC = 2                    # cycles in a piece (falls cross +-6 % in 2-4 cycles)
COH_MIN = 0.65                 # the flattened piece's cycle-to-cycle coherence at least
JOIN = 0.5                     # join crossfade, cycles
WRAP = 2.0                     # wrap crossfade, cycles
OFF_SLOPE = -0.10              # log rpm a second: falling
TM_CAP, TM_PIECE_CAP, SHRINK = 8.0, 6.0, 0.5

# the cycle finder
SLOPES = np.array([-4, -2.5, -1.5, -0.8, -0.3, 0, 0.3, 0.8, 1.5, 2.5, 4, 6.0])
RGRID = 700 * 1.004 ** np.arange(int(np.log(6200 / 700) / np.log(1.004)))
# the map's frames: the map the shipped loop was made with was computed in these four parts (s), and its 10 ms grid,
# float steps included, decides which frames seed the walker every 0.1 s and where each walk starts, so the parts are
# kept: a single grid over the whole file seeds 325 frames instead of 328 and the loop comes out with 19 pieces, not 18
MAP_PARTS = ((0.0, 41.0), (40.8, 81.0), (80.8, 121.0), (120.8, 161.9))
BAND = (30.0, 3000.0)
SEED_THR = 9.0
RUN_MIN_CYCLES, RUN_MIN_R = 6, 0.65
OCT = np.array([63, 125, 250, 500, 1000, 2000, 4000, 8000.0])


# --- reading and writing --------------------------------------------------------------------------------------------

def read_lead(path):
    """Mono float. A stereo file whose channels are one signal at a lag (r > 0.9 above 1.5 kHz at a nonzero lag)
    gives its leading channel; another stereo file the mean of its channels; a mono file itself."""
    with wave.open(str(path)) as w:
        sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
        if w.getsampwidth() != 2 or sr != SR:
            raise SystemExit(f"{path}: 16-bit 44.1 kHz PCM WAV expected")
        x = np.frombuffer(w.readframes(n), "<i2").astype(float) / 32768
    if ch == 1:
        return x, "mono"
    x = x.reshape(-1, ch)
    if ch == 2:
        lag, r = channel_lag(x[:, 0], x[:, 1])
        if r > 0.9 and lag != 0:
            lead = 1 if lag < 0 else 0
            return x[:, lead].copy(), (f"stereo, one signal {abs(lag)} samples ({1000 * abs(lag) / SR:.1f} ms) apart (r {r:.3f} "
                                       f"above 1.5 kHz): the {'right' if lead else 'left'} (leading) channel")
    return x.mean(1), "stereo, mean of the channels"


def channel_lag(a, b, maxlag=4096, fc=1500.0):
    """(lag, r): the lag k (|k| <= maxlag) maximising the correlation of a(t) and b(t + k) above fc, over three 10 s
    excerpts; k < 0 means b leads."""
    n = len(a)
    acc = np.zeros(2 * maxlag + 1)
    for c in (0.25, 0.5, 0.75):
        s = int(c * n) - 5 * SR
        if s < 0 or s + 10 * SR > n:
            s, e = 0, n
        else:
            e = s + 10 * SR
        aa, bb = a[s:e], b[s:e]
        N = 1 << int(np.ceil(np.log2(2 * len(aa))))
        f = np.fft.rfftfreq(N, 1 / SR)
        A, B = np.fft.rfft(aa, N) * (f > fc), np.fft.rfft(bb, N) * (f > fc)
        ha, hb = np.fft.irfft(A, N), np.fft.irfft(B, N)
        cc = np.fft.irfft(np.conj(A) * B, N) / np.sqrt(np.sum(ha ** 2) * np.sum(hb ** 2) + 1e-30)
        acc += np.concatenate([cc[-maxlag:], cc[:maxlag + 1]])
    acc /= 3
    i = int(np.argmax(acc))
    return i - maxlag, float(acc[i])


def limit(y):
    """The soft limiter: unchanged under KNEE, above it a tanh bend that never reaches full scale. (y, samples bent)"""
    a = np.abs(y)
    over = a > KNEE
    out = y.copy()
    out[over] = np.sign(y[over]) * (KNEE + (1 - KNEE) * np.tanh((a[over] - KNEE) / (1 - KNEE)))
    return out, int(over.sum())


def write(path, y, limited=True):
    """16-bit mono (through the limiter unless it has been applied already); returns its length, RMS and limiter share."""
    n = 0
    if limited:
        y, n = limit(y)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    rms = 20 * np.log10(np.sqrt(np.mean(y ** 2)) + 1e-12)
    print(f"wrote {Path(path).name}: {len(y) / SR:.2f} s, rms {rms:.1f} dBFS, peak {20 * np.log10(np.max(np.abs(y)) + 1e-12):.1f} dBFS"
          + (f", {n} samples limited ({100.0 * n / len(y):.3f}%)" if n else ""))
    return dict(len_s=round(len(y) / SR, 3), rms_dBFS=round(rms, 2), limited_pct=round(100.0 * n / len(y), 3))


# --- the idle, start and stop ----------------------------------------------------------------------------------------

def _biquad_mag(b, a, f, fs=48000.0):
    z = np.exp(-2j * np.pi * f / fs)
    return np.abs((b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z))


def loudness(x, win=0.1, hop=0.01):
    """(t, dB): BS.1770 K-weighted mean square in win-second windows (the weighting applied zero-phase by FFT)."""
    n = len(x) + SR
    f = np.fft.rfftfreq(n, 1 / SR)
    k = _biquad_mag([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585], f)
    k = k * _biquad_mag([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621], f)
    y = np.fft.irfft(np.fft.rfft(x, n) * k, n)[:len(x)]
    W, H = int(win * SR), int(hop * SR)
    starts = np.arange(0, len(y) - W + 1, H)
    c = np.concatenate([[0.0], np.cumsum(y ** 2)])
    return (starts + W / 2) / SR, 10 * np.log10((c[starts + W] - c[starts]) / W + 1e-12)


def detrend_loudness(y, win=0.1, hop=0.01):
    """Divide out the linear dB trend of the K-weighted loudness (win-second windows). Returns (y, slope dB/s)."""
    t, L = loudness(y, win, hop)
    p = np.polyfit(t, L, 1)
    tt = np.arange(len(y)) / SR
    return y / 10 ** ((np.polyval(p, tt) - np.mean(L)) / 20), float(p[0])


def xfade(out_seg, in_seg, c):
    """Linear ramps normalised so the expected power stays constant for two signals of correlation c (equal power is
    wrong for correlated signals)."""
    t = (np.arange(len(out_seg)) + 0.5) / len(out_seg)
    a, b = 1 - t, t
    return (out_seg * a + in_seg * b) / np.sqrt(a * a + b * b + 2 * a * b * max(c, 0.0))


def corr(a, b):
    a, b = a - a.mean(), b - b.mean()
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def idle_loop(x, span=IDLE_SPAN, wrap_s=IDLE_WRAP_S, search_s=0.25):
    """A plain excerpt (the idle is too irregular to flatten), its level trend divided out, wrapped at the end point
    within the last search_s seconds whose next wrap_s best match the start."""
    X = int(wrap_s * SR)
    y = x[int(span[0] * SR):int(span[1] * SR) + X]
    y, slope = detrend_loudness(y)
    hi = len(y) - X
    best = (-2.0, None)
    for n in range(hi - int(search_s * SR), hi):
        c = corr(y[:X], y[n:n + X])
        if c > best[0]:
            best = (c, n)
    c, n = best
    loop = y[:n].copy()
    loop[:X] = xfade(y[n:n + X], y[:X], c)
    return loop, dict(span_s=list(span), level_trend_removed_dB_per_s=round(slope, 2), wrap_s=wrap_s, wrap_corr=round(c, 3))


def compress(y, threshold, ratio, attack=0.010, release=0.150):
    """A slow compressor: the 30 ms RMS envelope over the threshold is brought down to 1/ratio of its excess (in dB)."""
    k = int(0.030 * SR)
    env = np.sqrt(np.convolve(y ** 2, np.ones(k) / k, "same")) + 1e-9
    want = np.where(env > threshold, (env / threshold) ** (1.0 / ratio - 1.0), 1.0)
    g = np.empty_like(want)
    a, r = np.exp(-1.0 / (attack * SR)), np.exp(-1.0 / (release * SR))
    cur = 1.0
    for i, w in enumerate(want):
        cur = a * cur + (1 - a) * w if w < cur else r * cur + (1 - r) * w
        g[i] = cur
    return y * g


def shelves(y, low_db=0.0, high_db=0.0, low_fc=100.0, high_fc=700.0, circular=True):
    """Zero-phase low and high shelves (a smooth step over about an octave in log frequency), applied by FFT: over a
    loop's whole length (circular), so the seam stays seamless; a one-shot is padded first."""
    if not (low_db or high_db):
        return y
    n = len(y) if circular else len(y) + SR
    f = np.fft.rfftfreq(n, 1 / SR)
    lf = np.log2(np.maximum(f, 1.0))
    g_db = low_db / (1 + np.exp((lf - np.log2(low_fc)) * 4)) + high_db / (1 + np.exp(-(lf - np.log2(high_fc)) * 4))
    out = np.fft.irfft(np.fft.rfft(y, n) * 10 ** (g_db / 20), n)
    return out[:len(y)]


def rms_to(y, level):
    return y * level / (np.sqrt(np.mean(y ** 2)) + 1e-12)


def idle_start_stop(x, out):
    rep = {}
    loop, info = idle_loop(x)
    loop = rms_to(shelves(loop, **SHELF), LOOP_RMS)
    print(f"CMB_EngineIdleLP: {IDLE_SPAN[0]}-{IDLE_SPAN[1]} s, wrap r {info['wrap_corr']:.3f}")
    rep["CMB_EngineIdleLP"] = dict(base_rpm=IDLE_BASE, **info, **write(out / "CMB_EngineIdleLP.wav", loop))
    idle_level = LOOP_RMS * 10 ** (IDLE_LEVEL_DB / 20)

    def cut(t0, t1, fin, fout):
        s = shelves(x[int(t0 * SR):int(t1 * SR)].copy(), circular=False, **SHELF)
        s[:int(fin * SR)] *= np.linspace(0, 1, int(fin * SR))
        s[-int(fout * SR):] *= np.linspace(1, 0, int(fout * SR))
        return s
    start = cut(*START_SPAN, 0.01, 0.15)
    start *= idle_level / np.sqrt(np.mean(start[-int(0.3 * SR):] ** 2))
    start = compress(start, 2.0 * idle_level, 4.0)   # the catch is ~23 dB over its idle: 4:1 over twice the idle
    stop = cut(*STOP_SPAN, 0.15, 0.01)
    stop *= idle_level / np.sqrt(np.mean(stop[:int(0.5 * SR)] ** 2))
    rep["CMB_EngineStart"] = dict(span_s=list(START_SPAN), **write(out / "CMB_EngineStart.wav", start))
    rep["CMB_EngineStop"] = dict(span_s=list(STOP_SPAN), **write(out / "CMB_EngineStop.wav", stop))
    return rep


# --- every engine cycle in the recording --------------------------------------------------------------------------------

def bandpass(x, lo, hi):
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = np.ones_like(f)
    if lo:
        g *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** 8)
    if hi:
        g *= 1 / (1 + (f / hi) ** 8)
    return np.fft.irfft(X * g, n)


_X = None


def _init(x):
    global _X
    _X = x


def _map_chunk(cs):
    x = _X
    W = int(0.20 * SR)
    N = 1 << 15
    df = SR / N
    fmax = 700.0
    base = RGRID[:, None] / 120.0
    K = np.arange(1, int(fmax / (700 / 120)) + 2)
    on = K[None, :] * base
    off = on - base / 2
    mask = on < fmax
    cnt = mask.sum(1)
    ion = np.floor(on / df).astype(int); won = on / df - ion
    ioff = np.floor(off / df).astype(int); woff = off / df - ioff
    han = np.hanning(W)
    tau = (np.arange(W) - W / 2) / SR
    warps = []
    for s in SLOPES:
        u = tau if s == 0 else np.expm1(s * tau) / s
        warps.append(np.interp(np.linspace(u[0], u[-1], W), u, np.arange(W)))
    ts, best = [], []
    for c in cs:
        s0 = int(round(c * SR)) - W // 2
        if s0 < 0 or s0 + W > len(x):
            continue
        seg = x[s0:s0 + W]
        rows = []
        for pos in warps:
            y = np.interp(pos, np.arange(W), seg) * han
            L = 20 * np.log10(np.abs(np.fft.rfft(y, N)) + 1e-9)
            von = L[ion] * (1 - won) + L[ion + 1] * won
            voff = L[ioff] * (1 - woff) + L[ioff + 1] * woff
            rows.append(((von - voff) * mask).sum(1) / cnt)
        ts.append(c); best.append(np.array(rows).max(0))
    return np.array(ts), np.array(best, np.float32)


def map_frames():
    """The map's frame centres (s): 10 ms apart over MAP_PARTS, each part from 0.1 s after its start to 0.1 s before
    its end; where two parts meet, a frame within 5 ms of the one before it is dropped."""
    c = np.sort(np.concatenate([np.arange(a + 0.1, b - 0.1, 0.01) for a, b in MAP_PARTS]))
    return c[np.r_[True, np.diff(c) > 0.005]]


def comb_map(x):
    """(t, R, M): the best score over the slopes per 10 ms frame and candidate rpm, on up to 4 cores (each frame is
    computed on its own, so the result doesn't depend on how many)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    xb = np.fft.irfft(X * ((f > 25) & (f < 1500)), len(x))
    frames = map_frames()
    jobs = np.array_split(frames, 16)
    with Pool(max(1, min(4, os.cpu_count() or 1)), initializer=_init, initargs=(xb,)) as p:
        parts = p.map(_map_chunk, jobs)
    t = np.concatenate([q[0] for q in parts]); M = np.concatenate([q[1] for q in parts])
    return t, RGRID, M


def seeds(t, R, M, thr, every=0.1, top=3, sep=0.08):
    out = []
    step = max(1, int(round(every / 0.01)))
    for i in range(0, len(t), step):
        row = M[i]
        loc = np.where((row[1:-1] > row[:-2]) & (row[1:-1] >= row[2:]) & (row[1:-1] >= thr))[0] + 1
        loc = loc[np.argsort(-row[loc])]
        chosen = []
        for j in loc:
            if all(abs(np.log(R[j] / R[k])) > sep for k in chosen):
                chosen.append(j)
            if len(chosen) >= top:
                break
        out += [(float(row[j]), float(t[i]), float(R[j])) for j in chosen]
    out.sort(reverse=True)
    return out


def _seg(x, a, P, Lr):
    """x from fractional sample a over P samples, resampled to Lr points (linear)."""
    pos = a + np.arange(Lr) * (P / Lr)
    i = np.floor(pos).astype(int)
    if i[0] < 0 or i[-1] + 1 >= len(x):
        return None
    f = pos - i
    return x[i] * (1 - f) + x[i + 1] * f


def _ncc(a, b):
    a = a - a.mean(); b = b - b.mean()
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def walk_cycles(xb, b0, P0, direction=1, r_stop=0.5, span=0.12, du=0.003, Lr=256, nmax=4000, patience=2):
    """Follow the engine cycle by cycle from boundary b0 (samples) with period P0 (samples, 720 degrees): each next
    period maximises the correlation of the next cycle (stretched to the template length) with the mean of the last
    two cycles. Returns the boundaries and per-cycle correlations (in walking order); direction -1 walks back."""
    x = xb if direction > 0 else xb[::-1]
    b = b0 if direction > 0 else (len(xb) - 1 - b0)
    pmin, pmax = 120 / 6500 * SR, 120 / 650 * SR
    us = np.exp(np.arange(-span, span + du / 2, du))
    bounds, rs = [b], []
    prev = [_seg(x, b - P0, P0, Lr)]
    if prev[0] is None:
        return [], []
    P = P0
    bad = 0
    for _ in range(nmax):
        tmpl = prev[-1] if len(prev) == 1 else 0.5 * (prev[-1] / (np.std(prev[-1]) + 1e-12) + prev[-2] / (np.std(prev[-2]) + 1e-12))
        best = (-2, None, None)
        for u in us:
            Pn = P * u
            s = _seg(x, b, Pn, Lr)
            if s is None:
                break
            r = _ncc(tmpl, s)
            if r > best[0]:
                best = (r, Pn, s)
        r, Pn, s = best
        if Pn is None or not (pmin <= Pn <= pmax):
            break
        if r < r_stop:
            bad += 1
            if bad >= patience:
                break
        else:
            bad = 0
        b = b + Pn
        P = Pn
        bounds.append(b); rs.append(r)
        prev = (prev + [s])[-2:]
    while rs and rs[-1] < r_stop:      # drop trailing bad cycles
        rs.pop(); bounds.pop()
    if direction < 0:
        bounds = [len(xb) - 1 - v for v in bounds]
    return bounds, rs


def cubic(x, pos):
    i = np.clip(np.floor(pos).astype(int), 1, len(x) - 3)
    f = pos - np.floor(pos)
    p0, p1, p2, p3 = x[i - 1], x[i], x[i + 1], x[i + 2]
    return p1 + 0.5 * f * (p2 - p0 + f * (2 * p0 - 5 * p1 + 4 * p2 - p3 + f * (3 * (p1 - p2) + p3 - p0)))


def pchip(xk, yk, xq):
    """Monotone cubic (Fritsch-Carlson) interpolation."""
    xk, yk = np.asarray(xk, float), np.asarray(yk, float)
    h = np.diff(xk); d = np.diff(yk) / h
    m = np.zeros(len(xk))
    m[0], m[-1] = d[0], d[-1]
    for k in range(1, len(xk) - 1):
        if d[k - 1] * d[k] > 0:
            w1, w2 = 2 * h[k] + h[k - 1], h[k] + 2 * h[k - 1]
            m[k] = (w1 + w2) / (w1 / d[k - 1] + w2 / d[k])
    i = np.clip(np.searchsorted(xk, xq) - 1, 0, len(xk) - 2)
    t = (xq - xk[i]) / h[i]
    h00 = (1 + 2 * t) * (1 - t) ** 2; h10 = t * (1 - t) ** 2; h01 = t * t * (3 - 2 * t); h11 = t * t * (t - 1)
    return h00 * yk[i] + h10 * h[i] * m[i] + h01 * yk[i + 1] + h11 * h[i] * m[i + 1]


def cycle_len(R):
    return 120.0 / R * SR


def flatten_bounds(x, bounds, R):
    """x between the first and last boundary (samples; consecutive boundaries = one 720-degree cycle) resampled so the
    phase runs at R/120 per second: exactly (len(bounds) - 1) cycles of cycle_len(R) samples."""
    nb = len(bounds) - 1
    L = cycle_len(R)
    nout = int(round(nb * L))
    ph_out = np.arange(nout) / L
    src = pchip(np.arange(nb + 1), np.asarray(bounds, float), ph_out)
    return cubic(x, src)


def cycles_matrix(y, R):
    L = cycle_len(R)
    n = int(len(y) // L)
    return y[(np.arange(n)[:, None] * L + np.arange(int(L))[None, :]).astype(int)]


def per_cycle_coherence(y, R, lag=1):
    C = cycles_matrix(y, R)
    C = C - C.mean(1, keepdims=True)
    a, b = C[:-lag], C[lag:]
    return (a * b).sum(1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1) + 1e-12)


def halves_r(y, R):
    """r between the two 360-degree halves of the mean 720-degree cycle (a V-twin's differ; alike = rpm read 2x low)."""
    C = cycles_matrix(y, R)
    m = C.mean(0)
    h = len(m) // 2
    return float(np.corrcoef(m[:h], m[h:2 * h])[0, 1])


def check_run(x, run, above=1500.0):
    """lag-1 / lag-2 coherence and halves r of a run's flattened cycles, on its longest stretch above `above` rpm (at
    idle the cycles alternate loud and soft, so lag 2 beats lag 1 there naturally)."""
    rpm_all = np.array([120 * SR / (q[1] - q[0]) for q in run])
    ok = rpm_all >= above
    best, cur = (0, 0), None
    for k, v in enumerate(ok):
        if v and cur is None:
            cur = k
        if (not v or k == len(ok) - 1) and cur is not None:
            e = k + 1 if v else k
            if e - cur > best[1] - best[0]:
                best = (cur, e)
            cur = None
    if best[1] - best[0] >= 4:
        run = run[best[0]:best[1]]
    bounds = np.r_[[q[0] for q in run], run[-1][1]]
    rpm = 120 * SR / np.diff(bounds)
    R = float(np.median(rpm))
    y = flatten_bounds(x, bounds, R)
    c1 = per_cycle_coherence(y, R)
    c2 = per_cycle_coherence(y, R, 2) if len(run) >= 4 else c1
    return float(c1.mean()), float(c2.mean()), halves_r(y, R)


def find_cycles(x):
    """Rows (start s, end s, r) of every cycle the walker followed, sorted, non-overlapping."""
    t, R, M = comb_map(x)
    xb = bandpass(x, *BAND)
    sd = seeds(t, R, M, SEED_THR)
    runs, covered, rejected = [], [], 0
    for sc, ts, Rs in sd:
        if any(t0 <= ts <= t1 and lo / 1.08 <= Rs <= hi * 1.08 for t0, t1, lo, hi in covered):
            continue
        P0 = 120 / Rs * SR
        f, rf = walk_cycles(xb, ts * SR, P0, 1, r_stop=0.5)
        bk, rb = walk_cycles(xb, ts * SR, P0, -1, r_stop=0.5)
        run = [(bk[k + 1], bk[k], rb[k]) for k in range(len(rb))] + [(f[k], f[k + 1], rf[k]) for k in range(len(rf))]
        run.sort()
        if len(run) < 2:
            covered.append((ts - 0.05, ts + 0.05, Rs, Rs))
            continue
        rpm = np.array([120 * SR / (q[1] - q[0]) for q in run])
        covered.append((run[0][0] / SR, run[-1][1] / SR, rpm.min(), rpm.max()))
        mr = float(np.mean([q[2] for q in run]))
        if len(run) < RUN_MIN_CYCLES or mr < RUN_MIN_R:
            rejected += 1
            continue
        c1, c2, hv = check_run(x, run)
        if c2 > c1 + 0.05 or hv > 0.6:
            rejected += 1
            continue
        runs.append((mr, run))
    runs.sort(key=lambda q: -q[0] * len(q[1]) ** 0.25)     # where runs overlap, the better one keeps the time
    taken, cyc = [], []
    for mr, run in runs:
        for q in run:
            a0, b0 = q[0] / SR, q[1] / SR
            if any(a0 < tb - 1e-4 and b0 > ta + 1e-4 for ta, tb in taken):
                continue
            cyc.append((a0, b0, q[2]))
        taken.append((run[0][0] / SR, run[-1][1] / SR))
    cyc = np.array(sorted(cyc))
    print(f"cycles: {len(sd)} seeds over {SEED_THR} dB, {len(runs)} runs kept, {rejected} rejected; {len(cyc)} cycles, "
          f"{np.sum(cyc[:, 1] - cyc[:, 0]):.1f} s")
    return cyc


# --- the flattened-piece loops ------------------------------------------------------------------------------------------

def table(cyc):
    a, b, r = cyc[:, 0], cyc[:, 1], cyc[:, 2]
    rpm = 120 / (b - a)
    tm = 0.5 * (a + b)
    run = np.zeros(len(a), int)
    for k in range(1, len(a)):
        run[k] = run[k - 1] + (1 if abs(a[k] - b[k - 1]) > 1e-3 else 0)
    slope = np.full(len(a), np.nan)
    idx = np.arange(len(a))
    for k in range(len(a)):
        m = (run == run[k]) & (np.abs(idx - k) <= 3)
        if m.sum() >= 3:
            slope[k] = np.polyfit(tm[m], np.log(rpm[m]), 1)[0]
    return dict(a=a, b=b, r=r, rpm=rpm, run=run, slope=slope)


def find_pieces(T, R):
    """Runs of consecutive qualifying cycles (indices k..j inclusive): within TOL of R, falling, walker r >= R_MIN."""
    inb = np.abs(np.log(T["rpm"] / R)) <= np.log(1 + TOL)
    s = T["slope"]
    ok = inb & (s <= OFF_SLOPE) & (T["r"] >= R_MIN) & np.isfinite(s)
    out, k, n = [], 0, len(ok)
    while k < n:
        if ok[k]:
            j = k
            while j + 1 < n and ok[j + 1] and T["run"][j + 1] == T["run"][k]:
                j += 1
            if j - k + 1 >= MIN_CYC:
                out.append((k, j))
            k = j + 1
        else:
            k += 1
    return out


def detrend_level(y, win=0.04, hop=0.005):
    """Divide out the linear dB trend of the plain energy in win-second windows (each fall gets quieter as it slows)."""
    W, H = int(win * SR), int(hop * SR)
    if len(y) < 3 * W:
        return y, 0.0
    c = np.concatenate([[0.0], np.cumsum(y ** 2)])
    s = np.arange(0, len(y) - W + 1, H)
    L = 10 * np.log10((c[s + W] - c[s]) / W + 1e-12)
    t = (s + W / 2) / SR
    p = np.polyfit(t, L, 1)
    tt = np.arange(len(y)) / SR
    return y / 10 ** ((np.polyval(p, tt) - np.mean(L)) / 20), float(p[0])


def build_pieces(x, T, runs, R):
    pieces = []
    for k, j in runs:
        bounds = np.r_[T["a"][k:j + 1], T["b"][j]] * SR
        y = flatten_bounds(x, bounds, R)
        y, slope_db = detrend_level(y)
        coh = per_cycle_coherence(y, R)
        info = dict(span_s=[round(float(T["a"][k]), 3), round(float(T["b"][j]), 3)], cycles=int(j - k + 1),
                    source_rpm=[int(T["rpm"][k:j + 1].min()), int(T["rpm"][k:j + 1].max())],
                    walker_r=round(float(T["r"][k:j + 1].mean()), 3), coherence=round(float(coh.mean()) if len(coh) else 0.0, 3),
                    level_trend_dB_per_s=round(slope_db, 1))
        pieces.append((y, info))
    return pieces


def octaves_re_total(y, N=8192):
    """Hann N-point power spectra, each normalised to unit power over 20 Hz-16 kHz, averaged; octave bands 63..8k in dB
    re that total; the centroid over 20 Hz-16 kHz."""
    w = np.hanning(N)
    f = np.fft.rfftfreq(N, 1 / SR)
    band = (f >= 20) & (f <= 16000)
    acc = np.zeros(len(f)); n = 0
    yy = y if len(y) >= N else np.pad(y, (0, N - len(y)))
    for s in range(0, len(yy) - N + 1, N // 4):
        P = np.abs(np.fft.rfft(yy[s:s + N] * w)) ** 2
        tot = P[band].sum()
        if tot > 0:
            acc += P / tot; n += 1
    acc /= max(n, 1)
    oct_db = np.array([10 * np.log10(acc[(f >= c / 2 ** 0.5) & (f < c * 2 ** 0.5)].sum() + 1e-20) for c in OCT])
    cen = float((acc[band] * f[band]).sum() / acc[band].sum())
    return oct_db, cen


def smooth_eq(y, gains_db, pad=True):
    """Zero-phase EQ: octave gains (at OCT) interpolated in log frequency, applied by FFT (padded unless circular)."""
    n = len(y) + (SR // 4 if pad else 0)
    f = np.fft.rfftfreq(n, 1 / SR)
    lf = np.log2(np.maximum(f, 20.0))
    g = np.interp(lf, np.log2(OCT), gains_db)
    out = np.fft.irfft(np.fft.rfft(y, n) * 10 ** (g / 20), n)
    return out[:len(y)]


def sliding_ncc(tmpl, sig):
    """Normalised correlation of tmpl (length X, mean removed) with every window sig[s:s+X], s = 0..len(sig)-X."""
    X = len(tmpl)
    n = len(sig) - X + 1
    if n <= 0:
        return np.zeros(0)
    t = tmpl - tmpl.mean()
    N = 1 << int(np.ceil(np.log2(len(sig) + X)))
    num = np.fft.irfft(np.fft.rfft(sig, N) * np.conj(np.fft.rfft(t, N)), N)[:n]
    c1 = np.concatenate([[0.0], np.cumsum(sig)])
    c2 = np.concatenate([[0.0], np.cumsum(sig * sig)])
    ssum = c1[X:X + n] - c1[:n]
    ssq = c2[X:X + n] - c2[:n]
    var = np.maximum(ssq - ssum * ssum / X, 1e-20)
    return num / (np.sqrt(var) * np.linalg.norm(t) + 1e-12)


def best_join(out, y, X, L):
    """Best alignment of piece y after the chain `out`: either skip s in [0, L/2] samples of y's head, or trim
    t in (0, L/2] samples off the chain's end; returns (r, trim, skip)."""
    h = int(L // 2)
    best = (-2.0, 0, 0)
    if len(y) > X + h + 1:
        c = sliding_ncc(out[-X:], y[:X + h])          # skip s
        k = int(np.argmax(c))
        best = (float(c[k]), 0, k)
    if len(out) > X + h + 1:
        c = sliding_ncc(y[:X], out[-(X + h):])        # window start in the chain's last X+h samples
        k = int(np.argmax(c))                         # trim = h - k
        if c[k] > best[0] and h - k > 0:
            best = (float(c[k]), h - k, 0)
    return best


def chain_from(pieces, first, R, X):
    L = cycle_len(R)
    order, joins = [first], []
    rem = [i for i in range(len(pieces)) if i != first]
    out = pieces[first].copy()
    while rem:
        cands = [(best_join(out, pieces[i], X, L), i) for i in rem]
        (c, trim, skip), i = max(cands, key=lambda q: q[0][0])
        y = pieces[i]
        if trim:
            out = out[:-trim]
        tail = out[-X:]
        out = np.concatenate([out[:-X], xfade(tail, y[skip:skip + X], c), y[skip + X:]])
        joins.append(round(c, 3))
        order.append(i)
        rem.remove(i)
    return out, order, joins


def wrap_fast(y, R, X, search_cycles=2, fine=0.5):
    """The loop's end n: the whole-cycle point of one of the last search_cycles cycles, +-fine of a cycle, whose next
    X samples best match the first X (by sliding correlation); the first X samples crossfaded from y[n:n+X]."""
    L = cycle_len(R)
    kmax = int((len(y) - X - fine * L) // L)
    lo = int(round((max(1, kmax - search_cycles + 1)) * L - fine * L))
    hi = int(round(kmax * L + fine * L))
    lo = max(lo, X + 1)
    hi = min(hi, len(y) - X)
    c = sliding_ncc(y[:X], y[lo:hi + X])
    k = int(np.argmax(c))
    n = lo + k
    loop = y[:n].copy()
    loop[:X] = xfade(y[n:n + X], y[:X], float(c[k]))
    return loop, float(c[k])


def chain(pieces, R, join=JOIN, wrap_cycles=WRAP):
    """Greedy chains from every piece as the first (up to 12 longest); keeps the one whose worst join/wrap is best."""
    L = cycle_len(R)
    X = int(round(join * L))
    Xw = int(round(wrap_cycles * L))
    firsts = sorted(range(len(pieces)), key=lambda i: -len(pieces[i]))[:12]
    best = None
    for f in firsts:
        out, order, joins = chain_from(pieces, f, R, X)
        if len(out) < Xw * 2 + 2 * L:
            continue
        loop, wc = wrap_fast(out, R, Xw, search_cycles=4 if len(out) > 30 * L else 2)
        score = min(joins + [wc]) + 0.25 * float(np.mean(joins + [wc]))
        if best is None or score > best[0]:
            best = (score, loop, order, joins, wc)
    return best


def piece_loop(x, T, R, target):
    """The pieces at R, each EQ'd so the pooled shape meets the target and each piece the pooled shape (cut only: the
    largest gain is shifted to 0 dB), chained, wrapped, at -13.5 dBFS RMS through the limiter."""
    pcs = build_pieces(x, T, find_pieces(T, R), R)
    group = [p for p in pcs if p[1]["coherence"] >= COH_MIN]
    if not group:
        return None
    shapes = [octaves_re_total(y)[0] for y, _ in group]
    w = np.array([info["cycles"] for _, info in group], float)
    pooled = 10 * np.log10(np.sum([w_ * 10 ** (shapes[k] / 10) for k, w_ in enumerate(w)], axis=0) / w.sum())
    g1 = np.clip(np.asarray(target, float) - pooled, -TM_CAP, TM_CAP)
    gains = []
    for k, (_, info) in enumerate(group):
        n = info["cycles"]
        gains.append(g1 + np.clip((pooled - shapes[k]) * n / (n + SHRINK), -TM_PIECE_CAP, TM_PIECE_CAP))
    ys = [smooth_eq(y, gains[k] - gains[k].max()) for k, (y, _) in enumerate(group)]
    rms0 = float(np.mean([np.sqrt(np.mean(y ** 2)) for y in ys]))
    ys = [y * rms0 / (np.sqrt(np.mean(y ** 2)) + 1e-12) for y in ys]
    best = chain(ys, R)
    if best is None:
        return None
    _, loop, order, joins, wc = best
    loop = loop * LOOP_RMS / (np.sqrt(np.mean(loop ** 2)) + 1e-12)
    loop, nlim = limit(loop)
    info = dict(pieces=[dict(group[i][1], eq_octaves_dB=[round(float(v), 1) for v in gains[i] - gains[i].mean()]) for i in order],
                found=len(pcs), dropped_low_coherence=len(pcs) - len(group), cycles=int(w.sum()), join_corr=joins,
                wrap_corr=round(wc, 3), limited_pct=round(100.0 * nlim / len(loop), 3))
    return loop, info


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--idle", type=Path, required=True, help="demodave's recording (stereo as downloaded, or its right channel)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    x, note = read_lead(a.idle)
    if not 160.0 < len(x) / SR < 163.0:
        raise SystemExit("this doesn't look like demodave's recording (161.9 s expected)")
    print(f"{a.idle.name}: {note}")
    a.out.mkdir(parents=True, exist_ok=True)
    report = {"_source": dict(file=a.idle.name, channel=note)}
    report.update(idle_start_stop(x, a.out))
    T = table(find_cycles(x))
    for name, fam, R, target in PIECE_LOOPS:
        res = piece_loop(x, T, R, target)
        if res is None:
            raise SystemExit(f"{name}: no usable pieces at {R} rpm")
        loop, info = res
        print(f"{name}: {len(info['pieces'])} pieces ({info['cycles']} cycles; {info['found']} found, {info['dropped_low_coherence']} "
              f"under coherence {COH_MIN}), joins min/median {min(info['join_corr']):.2f}/{np.median(info['join_corr']):.2f}, "
              f"wrap {info['wrap_corr']:.2f}")
        w = write(a.out / f"{name}.wav", loop, limited=False)     # limited already (its share is in info)
        report[name] = dict(base_rpm=R, family=fam, tone_target_oct_dB=target, **info, len_s=w["len_s"], rms_dBFS=w["rms_dBFS"])
    with open(a.out / "loops.json", "w") as fh:
        json.dump(report, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
