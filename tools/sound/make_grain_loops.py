#!/usr/bin/env python3
"""Pulse-grain engine loops for the riding range, made from demodave's recording of a real Sportster's exhaust pulses.

  python3 -I make_grain_loops.py --idle <demodave's idle.wav> --out <dir> --unlimited <dir> [--seconds 5]

The source: Freesound 502690 by demodave, "Harley Davidson Sportster - Idling with Engine Revs" (Creative Commons 0),
161.9 s, 16-bit 44.1 kHz stereo as downloaded. Its two channels are one signal 1024 samples (23.2 ms) apart: averaging
them builds a slapback into every pulse, so the tool takes the leading (right) channel, found by cross-correlation above
1.5 kHz (a mono file is taken as it is).

What a grain is. A V-twin fires twice per 720 crank degrees, 315 and 405 degrees apart. Every firing pulse of the
source is found with its type (A: the pulse followed by the short interval; B: the other), its neighbours (the
previous and next pulse) and its rpm:
  rises  - the blips' throttle-open rises (the throttle snapped open: strong, barking pulses; "on load"): the pulses
           are the sharp 1.5-8 kHz onsets, chained into a V-twin train; a smooth crank-angle-to-time fit per blip
           (cubic in crank angle plus one constant time offset for the B pulses) gives each pulse's rpm and the A/B
           parity, and the B pulses' acoustic offset (about -2.3 ms: the two pipes' different paths);
  falls  - the closed-throttle falls after each blip ("off load", overrun): tracked with a DP comb path, then within
           +-10% of each target rpm by a comb tracker (lines at k * rpm/120 Hz, a robust fit, a cycle resync); the
           pulses are put at the crank phases of the mean cycle's two-peak HF pattern, the pieces aligned to each
           other by their low-frequency mean cycles.
Each pulse's onset is then refined by cross-correlating its low-frequency waveform (< 400 Hz) with the mean of its
neighbours of the same type and rpm (+-1 ms), so the pulses line up at low frequency like an engine's cycles do. Each
pulse's attack is found in the source too: the sample within +-4 ms of (onset - 2.8 ms) where the energy above 700 Hz
in the 3 ms after it over the 3 ms before it peaks (the attacks lead the LF-aligned onsets by 1.9-3.2 ms).

How a loop at rpm R is made. Pulse marks are laid at R's firing times over a whole number of cycles (4-6 s): A every
cycle, B at the loop's crank angle after it (B_ANGLE_LOOP: 280-315 degrees, set so the loop's mean-cycle firing gap reads
the reference ride's 300-305 degrees; a fixed 315 degrees plus the source's -2.3 ms read 265-295), with a small timing
jitter (the natural cycle-to-cycle jitter measured in the reference rides is ~0.05 ms). For each mark a grain of the
right type is drawn at random from the pool nearest R (Gaussian weight in log rpm, a tolerance), never one used within
the last half of its type's in-tolerance pool (at least 3 picks). Each grain is the source from its previous to its next
pulse, time-warped piecewise so its intervals become the target's (warp exponent kappa: 1 = fully warped, which
shifts its resonances by the rpm ratio, used for pools within +-10%; 0 = not warped, the tail cut short, used for the
1400 rpm closed-throttle loop from falls at 1450-1940). Each use reads its high band (> 400 Hz) on a time axis whose
rate runs from 1 + e at the onset to 1 - e at either end of the grain (e random within +-4% per use; the read meets the
low band's at both ends, so nothing is skipped or read twice), so a reused pulse's fine structure differs (with
only the last 6 picks barred and no such variation, 15-36 % of the on-load cycles had a near-identical twin at 1-6 kHz,
which no real ride has; now under 5 %). The low-frequency part of each grain is pulled toward the pool's mean grain
(factor beta: the cycle-to-cycle coherence then matches a real engine's ~0.89 on load), the band levels' deviations
from the pool mean are shrunk (gamma) and a slow random level flutter (band-limited, periodic over the loop) is added,
so the 100 ms loudness and centroid fluctuation match the reference's natural values. Consecutive grains are joined by a 4 ms crossfade that ends 1 ms before the next
pulse's attack (in the quiet tail, so every attack is intact), and each grain's own material ends 1 ms before its
source's next attack; the ramps are linear, normalised for the two signals' correlation. Everything is placed
circularly: the loop has no seam.

Writes, in --out, 44.1 kHz 16-bit mono WAVs at -13.5 dBFS RMS through a soft limiter (knee -3 dBFS), named with the
base rpm (CMB_EngineGrainOn2000LP.wav, CMB_EngineGrainOff2300LP.wav, ...), and loops.json: per loop the base rpm, state,
length, pool (size, sources, rpm range), parameters, grain reuse, crossfade correlations, limiter share, the placed
onsets and the attacks (build_loops.py's pulse leveling reads them). With --unlimited, the same loops with their peak
at -1 dBFS and nothing limited: build_loops.py tone-matches these. Every random choice comes from a numpy generator
seeded per loop (the table's seed), so a rebuild gives the same files bit for bit."""

import argparse
import json
import wave
from pathlib import Path

import numpy as np

SR = 44100
LOOP_RMS = 10 ** (-13.5 / 20)
KNEE = 0.7

# --- the loop table -----------------------------------------------------------------------------------------------
# name, base rpm, state, pool source, selection sigma and tolerance (log rpm), warp exponent kappa, LF shrink beta,
# LF / HF level-deviation keep factors gamma_l / gamma_h, slow level flutter sd (dB), seed
LOOPS = [
    ("CMB_EngineGrainOn1400LP", 1400.0, "on", "rise", 0.07, 0.16, 1.0, 0.55, 0.2, 0.15, 0.15, 11),
    ("CMB_EngineGrainOn1700LP", 1700.0, "on", "rise", 0.07, 0.12, 1.0, 0.55, 0.2, 0.15, 0.15, 12),
    ("CMB_EngineGrainOn2000LP", 2000.0, "on", "rise", 0.07, 0.12, 1.0, 0.55, 0.2, 0.15, 0.15, 13),
    ("CMB_EngineGrainOn2400LP", 2400.0, "on", "rise", 0.07, 0.12, 1.0, 0.55, 0.2, 0.15, 0.15, 14),
    ("CMB_EngineGrainOn2800LP", 2800.0, "on", "rise", 0.07, 0.12, 1.0, 0.55, 0.2, 0.15, 0.15, 15),
    ("CMB_EngineGrainOn3300LP", 3300.0, "on", "rise", 0.07, 0.12, 1.0, 0.55, 0.2, 0.15, 0.15, 16),
    ("CMB_EngineGrainOff1400LP", 1400.0, "off", "fall_low", 0.30, 0.50, 0.0, 0.9, 0.3, 0.3, 0.15, 21),
    ("CMB_EngineGrainOff1800LP", 1800.0, "off", "fall_low", 0.07, 0.12, 1.0, 0.7, 0.3, 0.3, 0.15, 22),
    ("CMB_EngineGrainOff2300LP", 2300.0, "off", "fall2300", 0.06, 0.10, 1.0, 0.9, 0.3, 0.3, 0.15, 23),
    ("CMB_EngineGrainOff2800LP", 2800.0, "off", "fall2800", 0.06, 0.10, 1.0, 0.9, 0.3, 0.3, 0.15, 24),
]
AB_HF_KEEP = {"CMB_EngineGrainOn1400LP": 0.4}   # the first pulses of a blip: A's crack 3.9 dB over B's; keep 40% of that
# calibration targets, measured on the reference ride (an Iron 883 on the road, the right channel; measured only):
#   cycle coherence on load: on load and cruising 0.885-0.897 median (p10-90 0.85-0.92) -> beta is chosen for 0.89
#   100 ms level sd (1 s detrended): on load 0.33-0.42 at 1800-2050 rpm, off load 0.36-0.38 -> flutter for 0.37
COH_TARGET_ON = 0.89
LEV_SD_TARGET = 0.37
BETA_GRID = (0.25, 0.35, 0.45, 0.55, 0.65, 0.75)
FLUTTER_GRID = (0.0, 0.1, 0.2, 0.3, 0.4)
FALL_TARGETS = (1600.0, 1800.0, 2300.0, 2800.0)
FALL_TOL = {1600.0: 0.12, 1800.0: 0.10, 2300.0: 0.10, 2800.0: 0.10}
LIGHT_RISE = (54.40, 63.05)  # demodave's light-throttle rise and held rev: not a fall
JITTER_MS = 0.05      # natural cycle jitter (reference rides, demodave's held rev): 0.02-0.08 ms
XF_MS, GUARD_MS = 4.0, 1.0
B_ANGLE = {"on": 305.0, "off": 300.0}   # the B pulse's crank angle after A (degrees; ideal 315): the reference ride's
                                        # mean-cycle firing gap is 300-305 degrees at 1650-2050 rpm
# per loop, after one pass measured as the firing gap (the mean 720-degree cycle of the 1-8 kHz envelope, its two
# biggest peaks; 5-degree bins) on the loops built at B_ANGLE: 305 placed read 300 / 305 / 310 / 295 / 290 / 325 on
# load (1400..3300) and 300 placed read 300 / 305 / 285 off load (1400, 1800, 2800): the A and B pulses' attacks lead
# their LF-aligned onsets by different amounts, so each loop's angle is corrected once by the difference
# (a second pass: On1400 310 read 310, On2800 320 read 345, On3300 285 read 310; set between the passes' readings)
B_ANGLE_LOOP = {"CMB_EngineGrainOn1400LP": 307.0, "CMB_EngineGrainOn1700LP": 305.0, "CMB_EngineGrainOn2000LP": 300.0,
                "CMB_EngineGrainOn2400LP": 315.0, "CMB_EngineGrainOn2800LP": 310.0, "CMB_EngineGrainOn3300LP": 280.0,
                "CMB_EngineGrainOff1400LP": 300.0, "CMB_EngineGrainOff1800LP": 295.0, "CMB_EngineGrainOff2800LP": 315.0}
AVOID_FRAC, AVOID_MIN = 0.5, 3          # no reuse within this share of the type's in-tolerance pool (at least 3 picks)
HF_VAR = 0.04                           # each use's HF time axis x (1 + U(-HF_VAR, HF_VAR))
ATTACK_LEAD_MS, ATTACK_SPAN_MS, ATTACK_K_MS, ATTACK_FC = 2.8, 4.0, 3.0, 700.0
FC_LF = 400.0         # the low/high split for the coherence and level shaping


# --- reading -------------------------------------------------------------------------------------------------------

def read_lead(path):
    """Mono float. A stereo file whose channels are one signal at a lag (r > 0.9 above 1.5 kHz) gives its leading
    channel; another stereo file the mean; a mono file itself."""
    with wave.open(str(path)) as w:
        sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
        if w.getsampwidth() != 2 or sr != SR:
            raise SystemExit(f"{path}: 16-bit 44.1 kHz PCM WAV expected")
        x = np.frombuffer(w.readframes(n), "<i2").astype(float) / 32768
    if ch == 1:
        return x, "mono"
    x = x.reshape(-1, ch)
    a, b = x[:, 0], x[:, 1]
    acc = np.zeros(2 * 4096 + 1)
    for c in (0.25, 0.5, 0.75):
        s = int(c * len(a)) - 5 * SR
        aa, bb = a[s:s + 10 * SR], b[s:s + 10 * SR]
        N = 1 << int(np.ceil(np.log2(2 * len(aa))))
        f = np.fft.rfftfreq(N, 1 / SR)
        A, B = np.fft.rfft(aa, N) * (f > 1500), np.fft.rfft(bb, N) * (f > 1500)
        ha, hb = np.fft.irfft(A, N), np.fft.irfft(B, N)
        cc = np.fft.irfft(np.conj(A) * B, N) / np.sqrt(np.sum(ha ** 2) * np.sum(hb ** 2) + 1e-30)
        acc += np.concatenate([cc[-4096:], cc[:4097]])
    acc /= 3
    i = int(np.argmax(acc)); lag, r = i - 4096, float(acc[i])
    if r > 0.9 and lag != 0:
        lead = 1 if lag < 0 else 0
        return x[:, lead].copy(), f"stereo, one signal {abs(lag)} samples apart (r {r:.3f}): the {'right' if lead else 'left'} (leading) channel"
    return x.mean(1), "stereo, mean of the channels"


def bandpass(x, lo=None, hi=None):
    n = len(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones(len(f))
    if lo is not None:
        m *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** 8)
    if hi is not None:
        m *= 1 / (1 + (f / hi) ** 8)
    return np.fft.irfft(np.fft.rfft(x) * m, n)


def env(x, win):
    k = max(1, int(win * SR))
    return np.sqrt(np.convolve(x ** 2, np.ones(k) / k, "same"))


def cubic(x, pos):
    i = np.clip(np.floor(pos).astype(int), 1, len(x) - 3)
    f = pos - np.floor(pos)
    p0, p1, p2, p3 = x[i - 1], x[i], x[i + 1], x[i + 2]
    return p1 + 0.5 * f * (p2 - p0 + f * (2 * p0 - 5 * p1 + 4 * p2 - p3 + f * (3 * (p1 - p2) + p3 - p0)))


# --- rises: HF onset chains -------------------------------------------------------------------------------------------

def hf_log_energy(x):
    hp = bandpass(x, lo=1500, hi=8000)
    k = int(0.0005 * SR)
    return hp, 10 * np.log10(np.convolve(hp ** 2, np.ones(k) / k, "same") + 1e-12)


def blip_starts(hp, jump_db=15.0, min_gap=0.25):
    H = int(0.01 * SR); n = len(hp) // H
    Lh = 10 * np.log10(np.mean(hp[:n * H].reshape(n, H) ** 2, 1) + 1e-12)
    t = (np.arange(n) + 0.5) * H / SR
    out = []
    for i in range(10, n - 3):
        if np.mean(Lh[i:i + 3]) - np.median(Lh[max(0, i - 10):i]) > jump_db and (not out or t[i] - out[-1] > min_gap):
            out.append(t[i])
    return np.array(out)


def local_peaks(le, i0, i1, g=int(0.006 * SR), rel_db=18.0):
    seg = le[i0:i1]
    mx = np.maximum.reduce([np.roll(seg, d) for d in range(-g, g + 1, 5)])
    pk = np.where(seg >= mx)[0]
    pk = pk[(pk > g) & (pk < len(seg) - g)]
    if not len(pk):
        return np.array([], int)
    pk = pk[seg[pk] > seg[pk].max() - rel_db]
    th = []
    for p in pk:
        if th and p - th[-1] < g:
            if seg[p] > seg[th[-1]]:
                th[-1] = p
        else:
            th.append(p)
    return np.array(th, int) + i0


def chain(pk):
    """The longest prefix of onsets that is an accelerating V-twin train: each interval 0.6-1.15 x the one two before."""
    if len(pk) < 4:
        return pk[:0]
    d = np.diff(pk).astype(float)
    n = 2
    while n < len(d) and 0.6 < d[n] / d[n - 2] < 1.15:
        n += 1
    return pk[:n + 1]


def fit_crank(ch):
    """t_k = T(theta_k) + D * isB (T cubic in crank angle); of the two parities the one with the plausible |D| (the
    other parity absorbs 90 degrees into D). Returns isB, D (ms), rpm per pulse, residual sd (ms)."""
    t = ch / SR * 1000.0
    sols = []
    for par in (0, 1):
        k = np.arange(len(t)) + par
        isB = (k % 2 == 1).astype(float)
        th = 720.0 * (k // 2) + 315.0 * isB
        thn = (th - th.mean()) / 720.0
        deg = 3 if len(t) >= 8 else 2
        X = np.column_stack([thn ** p for p in range(deg + 1)] + [isB])
        c, *_ = np.linalg.lstsq(X, t, rcond=None)
        res = t - X @ c
        dT = sum(p * c[p] * thn ** (p - 1) for p in range(1, deg + 1)) / 720.0     # ms per crank degree
        sols.append((abs(c[-1]), isB, float(c[-1]), 1000.0 * 60.0 / (dT * 360.0), float(np.std(res))))
    _, isB, D, rpm, sd = min(sols, key=lambda s: s[0])
    return isB.astype(int), D, rpm, sd


def find_rises(x):
    hp, le = hf_log_energy(x)
    starts = blip_starts(hp)
    grains, chains = [], []
    for bi, s in enumerate(starts):
        ch = chain(local_peaks(le, int((s - 0.06) * SR), int((s + 0.8) * SR)))
        if len(ch) < 6:
            continue
        isB, D, rpm, sd = fit_crank(ch)
        chains.append(dict(start=float(s), n=len(ch), D_ms=D, resid_ms=sd, rpm=[float(rpm[0]), float(rpm[-1])], end=int(ch[-1]),
                           end_rpm=float(rpm[-1])))
        for i in range(1, len(ch) - 1):
            grains.append(dict(o_prev=float(ch[i - 1]), o=float(ch[i]), o_next=float(ch[i + 1]), type=int(isB[i]),
                               rpm=float(rpm[i]), src="rise", event=bi, t=float(ch[i] / SR)))
    return grains, chains, starts


# --- tracking (the half-order comb tracker, robust fit, phase, flatten, resync) ---------------------------------------------

def comb_track(x, t0, t1, guide, band=0.10, win=0.15, hop=0.01, fmax=1200.0, step=0.002):
    g = np.array(guide, float)
    W, H = int(win * SR), int(hop * SR)
    N = 1 << int(np.ceil(np.log2(W * 8)))
    df = SR / N
    han = np.hanning(W)
    offs = np.exp(np.arange(-band, band + 1e-9, step))
    rows = []
    for c in np.arange(t0 + win / 2, t1 - win / 2, hop):
        s = int(round(c * SR)) - W // 2
        if s < 0 or s + W > len(x):
            continue
        gr = float(np.exp(np.interp(c, g[:, 0], np.log(g[:, 1]))))
        L = 20 * np.log10(np.abs(np.fft.rfft(x[s:s + W] * han, N)) + 1e-7)
        best = (-1e9, gr)
        for R in gr * offs:
            b = R / 120.0
            k = np.arange(1, int(fmax / b) + 1)
            on, off = k * b / df, (k - 0.5) * b / df
            i0, i1 = np.floor(on).astype(int), np.floor(off).astype(int)
            sc = float(np.mean(L[i0] + (on - i0) * (L[i0 + 1] - L[i0])) - np.mean(L[i1] + (off - i1) * (L[i1 + 1] - L[i1])))
            if sc > best[0]:
                best = (sc, R)
        rows.append((c, best[1], best[0]))
    return np.array(rows)


def fit_track(rows, deg=3, iters=5):
    t, lr, w = rows[:, 0], np.log(rows[:, 1]), np.clip(rows[:, 2], 0.3, None)
    keep = np.ones(len(t), bool)
    for _ in range(iters):
        p = np.polyfit(t[keep], lr[keep], deg, w=w[keep])
        res = lr - np.polyval(p, t)
        keep = np.abs(res) < max(0.01, 2.5 * np.std(res[keep]))
    return p, float(np.std(res[keep])), float(keep.mean())


def cycle_len(R):
    return 120.0 / R * SR


def phase_of(poly, n0, n1):
    rpm = np.exp(np.polyval(poly, np.arange(n0, n1) / SR))
    return np.concatenate([[0.0], np.cumsum(rpm[:-1] / 120.0 / SR)])


def flatten_phi(x, phi, n0, R):
    start = np.ceil(phi[0])
    cycles = int(np.floor(phi[-1] - start))
    per = R / 120.0 / SR
    target = start + np.arange(int(round(cycles / per))) * per
    return cubic(x, np.interp(target, phi, np.arange(n0, n0 + len(phi)).astype(float)))


def cycles_matrix(y, R):
    L = cycle_len(R)
    n = int(len(y) // L)
    return y[(np.arange(n)[:, None] * L + np.arange(int(L))[None, :]).astype(int)]


def per_cycle_coherence(y, R):
    C = cycles_matrix(y, R)
    C = C - C.mean(1, keepdims=True)
    a, b = C[:-1], C[1:]
    return (a * b).sum(1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1) + 1e-12)


def resync(x, phi, n0, R, iters=3, maxlag_frac=0.15, smooth_cycles=3):
    best_phi, best_c = phi, float(np.mean(per_cycle_coherence(flatten_phi(x, phi, n0, R), R)))
    idx = np.arange(n0, n0 + len(phi)).astype(float)
    for _ in range(iters):
        y = flatten_phi(x, phi, n0, R)
        L = cycle_len(R)
        C = cycles_matrix(y, R)
        nC, Lc = C.shape
        ref = C.mean(0)
        Fr = np.conj(np.fft.rfft(ref - ref.mean(), 2 * Lc))
        maxlag = int(maxlag_frac * Lc)
        lags = np.zeros(nC)
        for k in range(nC):
            cc = np.fft.irfft(np.fft.rfft(C[k] - C[k].mean(), 2 * Lc) * Fr, 2 * Lc)
            cc = np.concatenate([cc[-maxlag:], cc[:maxlag + 1]])
            j = int(np.argmax(cc))
            frac = 0.0
            if 0 < j < len(cc) - 1:
                d = cc[j - 1] - 2 * cc[j] + cc[j + 1]
                frac = 0.5 * (cc[j - 1] - cc[j + 1]) / d if d != 0 else 0.0
            lags[k] = j - maxlag + frac
        if smooth_cycles > 1:
            lags = np.convolve(np.pad(lags, smooth_cycles // 2, mode="edge"), np.ones(smooth_cycles) / smooth_cycles, "valid")
        start = np.ceil(phi[0])
        per = R / 120.0 / SR
        pos_out = np.arange(nC) * L + lags + L / 2
        target_phase = start + (np.arange(nC) * L + L / 2) * per
        src_pos = np.interp(start + pos_out * per, phi, idx)
        cur = np.interp(src_pos, idx, phi)
        phi = np.maximum.accumulate(phi + np.interp(idx, src_pos, target_phase - cur))
        c = float(np.mean(per_cycle_coherence(flatten_phi(x, phi, n0, R), R)))
        if c > best_c:
            best_phi, best_c = phi, c
    return best_phi, best_c


# --- falls -----------------------------------------------------------------------------------------------------------------

def comb_map(x, t0, t1, win=0.25, hop=0.01, rmin=650.0, rmax=5600.0, fmax=250.0, step=0.005):
    W, H = int(win * SR), int(hop * SR)
    N = 1 << int(np.ceil(np.log2(W * 8)))
    df = SR / N
    R = rmin * np.exp(np.arange(0, np.log(rmax / rmin), step))
    on_i, off_i, seg = [], [], [0]
    for r in R:
        b = r / 120.0
        k = np.arange(1, int(fmax / b) + 1)
        on_i.append(k * b / df); off_i.append((k - 0.5) * b / df); seg.append(seg[-1] + len(k))
    on_i, off_i, seg = np.concatenate(on_i), np.concatenate(off_i), np.array(seg)

    def gather(L, p):
        i = np.floor(p).astype(int); fr = p - i
        return L[i] * (1 - fr) + L[i + 1] * fr
    han = np.hanning(W)
    ts, M = [], []
    for c in np.arange(t0, t1, hop):
        s = int(round(c * SR)) - W // 2
        if s < 0 or s + W > len(x):
            continue
        L = 20 * np.log10(np.abs(np.fft.rfft(x[s:s + W] * han, N)) + 1e-7)
        cs = np.concatenate([[0.0], np.cumsum(gather(L, on_i) - gather(L, off_i))])
        M.append((cs[seg[1:]] - cs[seg[:-1]]) / np.diff(seg)); ts.append(c)
    return np.array(ts), R, np.array(M)


def dp_path(M, R, max_up=0.01, max_down=0.03, pen=20.0):
    lr = np.log(R)
    n, m = M.shape
    acc = M[0].copy(); back = np.zeros((n, m), int)
    dl = lr[1] - lr[0]
    ku, kd = int(np.ceil(max_up / dl)), int(np.ceil(max_down / dl))
    for i in range(1, n):
        best = np.full(m, -1e18); arg = np.zeros(m, int)
        for s in range(-kd, ku + 1):
            prev = np.roll(acc, s) - pen * abs(s) * dl
            if s > 0:
                prev[:s] = -1e18
            elif s < 0:
                prev[s:] = -1e18
            upd = prev > best
            best[upd] = prev[upd]; arg[upd] = (np.arange(m) - s)[upd]
        acc = best + M[i]; back[i] = arg
    path = np.zeros(n, int); path[-1] = int(np.argmax(acc))
    for i in range(n - 1, 0, -1):
        path[i - 1] = back[i, path[i]]
    return R[path], M[np.arange(n), path]


def fall_guide(x, t0, t1, r0):
    t, R, M = comb_map(x, t0, t1, rmax=min(6000.0, r0 * 1.3))
    if len(t) < 10:
        return None
    M = M.copy()
    M[:5] -= 3.0 * np.abs(np.log(R / r0))[None, :] / 0.05
    r, s = dp_path(M, R)
    keep, low = len(r), r[0]
    for i in range(1, len(r)):
        low = min(low, r[i])
        if r[i] > low * 1.02 or r[i] < 1150 or LIGHT_RISE[0] <= t[i] <= LIGHT_RISE[1]:
            keep = i
            break
    j = min(keep, 20) - 1
    if j < 5 or r[j] > r[0] * 0.96:          # a fall: down by 4% within its first 0.2 s
        return None
    return t[:keep], r[:keep], s[:keep]


def band_piece(x, tg, rg, R, tol=0.10, min_cycles=4):
    win = float(np.clip(3.0 * 120.0 / R, 0.08, 0.16))
    fmax = 500.0 if R > 2000 else 400.0
    ok = np.abs(np.log(rg / R)) <= np.log(1 + tol)
    if ok.sum() < 3:
        return None
    a, b = tg[ok][0], tg[ok][-1]
    if (b - a) * R / 120 < min_cycles:
        return None
    pad = win / 2 + 0.03
    rows = comb_track(x, a - pad, b + pad, list(zip(tg, rg)), band=0.06, win=win, hop=0.005, fmax=fmax, step=0.002)
    if len(rows) < 6:
        return None
    p, sd, kept = fit_track(rows, deg=2)
    tt = np.arange(a - 0.05, b + 0.05, 0.002)
    rr = np.exp(np.polyval(p, tt))
    ok2 = np.abs(np.log(rr / R)) <= np.log(1 + tol)
    if ok2.sum() < 3:
        return None
    a, b = max(tt[ok2][0], a - 0.05), tt[ok2][-1]
    if (b - a) * R / 120 < min_cycles:
        return None
    n0, n1 = int(a * SR), int(b * SR)
    phi, coh = resync(x, phase_of(p, n0, n1), n0, R)
    return dict(t0=float(a), t1=float(b), n0=n0, phi=phi, coh=float(coh), poly=p)


def two_peak_theta(me, sab):
    Lc = len(me)
    sc = np.array([me[i] + me[int(i + sab) % Lc] for i in range(Lc)])
    return int(np.argmax(sc)), float(sc.max() / np.median(sc))


def circ_lag(a, b):
    """lag l maximising sum a[i] b[i+l] (circular)"""
    c = np.fft.irfft(np.conj(np.fft.rfft(a - a.mean())) * np.fft.rfft(b - b.mean()), len(a))
    return int(np.argmax(c))


def find_falls(x, chains, starts, D_ms, min_coh=0.5):
    xl = bandpass(x, hi=FC_LF)
    eh = env(bandpass(x, lo=1500, hi=8000), 0.0005)
    out = {R: [] for R in FALL_TARGETS}
    pieces_info = {R: [] for R in FALL_TARGETS}
    for ci, chn in enumerate(chains):
        te = chn["end"] / SR
        nxt = min([q for q in starts if q > te + 0.05], default=te + 3.0)
        g = fall_guide(x, te + 0.06, min(nxt - 0.05, te + 3.5), chn["end_rpm"])
        if g is None:
            continue
        for R in FALL_TARGETS:
            pc = band_piece(x, g[0], g[1], R, tol=FALL_TOL[R], min_cycles=3 if R < 2000 else 4)
            if pc is None or pc["coh"] < min_coh:
                continue
            pc["event"] = ci
            out[R].append(pc)
    pools = {}
    for R, pcs in out.items():
        if not pcs:
            pools[R] = []
            continue
        Lc = int(cycle_len(R))
        sab = 315.0 / 720.0 * cycle_len(R) + D_ms * 1e-3 * SR
        for pc in pcs:
            pc["me"] = np.sqrt((cycles_matrix(flatten_phi(eh, pc["phi"], pc["n0"], R), R) ** 2).mean(0))[:Lc]
            pc["ml"] = cycles_matrix(flatten_phi(xl, pc["phi"], pc["n0"], R), R).mean(0)[:Lc]
            pc["th"], pc["contrast"] = two_peak_theta(pc["me"], sab)
        # align the pieces' LF mean cycles to an iterated template (the most coherent piece first)
        ref = max(pcs, key=lambda p: p["coh"])
        T = np.roll(ref["ml"], -ref["th"])
        for _ in range(3):
            acc = np.zeros(Lc)
            for pc in pcs:
                pc["th"] = circ_lag(T, pc["ml"])          # pc.ml shifted by th matches T
                acc += np.roll(pc["ml"], -pc["th"]) / (np.std(pc["ml"]) + 1e-12)
            T = acc / len(pcs)
        # the pooled HF envelope (aligned) sets the A onset: its two-peak pattern
        ME = np.mean([np.roll(pc["me"], -pc["th"]) / pc["me"].mean() for pc in pcs], 0)
        th0, contrast = two_peak_theta(ME, sab)
        grains = []
        for pc in pcs:
            thA = (pc["th"] + th0) % Lc
            phi = pc["phi"]
            idx = np.arange(pc["n0"], pc["n0"] + len(phi)).astype(float)
            start = np.ceil(phi[0])
            marks = []
            for j in range(-1, int(phi[-1] - start) + 2):
                for ty, off in ((0, thA), (1, thA + sab)):
                    q = start + j + off / cycle_len(R)
                    if phi[0] <= q <= phi[-1]:
                        marks.append((float(np.interp(q, phi, idx)), ty))
            marks.sort()
            for i in range(1, len(marks) - 1):
                o = marks[i][0]
                grains.append(dict(o_prev=marks[i - 1][0], o=o, o_next=marks[i + 1][0], type=marks[i][1],
                                   rpm=float(np.exp(np.polyval(pc["poly"], o / SR))), src="fall", event=pc["event"], t=o / SR))
            pieces_info[R].append(dict(span_s=[round(pc["t0"], 3), round(pc["t1"], 3)], coherence=round(pc["coh"], 3),
                                       pulses=len(marks)))
        pools[R] = grains
        pieces_info[R] = dict(pieces=pieces_info[R], pooled_hf_two_peak_contrast=round(contrast, 2))
    return pools, pieces_info


# --- onset refinement at low frequency ------------------------------------------------------------------------------------

def refine(pool, xl, pre_ms=2.0, post_ms=12.0, maxlag_ms=1.0, iters=3, nb=0.15):
    if len(pool) < 4:
        return pool
    a, b = -int(pre_ms * 1e-3 * SR), int(post_ms * 1e-3 * SR)
    ml = int(maxlag_ms * 1e-3 * SR)
    n = b - a
    on = np.array([g["o"] for g in pool], float)
    ty = np.array([g["type"] for g in pool])
    lr = np.log([g["rpm"] for g in pool])

    def win(o, lo, hi):
        i = int(np.floor(o)); f = o - i
        s = xl[i + lo:i + hi + 1]
        return s[:-1] * (1 - f) + s[1:] * f
    for _ in range(iters):
        Wd = np.array([win(o, a - ml, b + ml) for o in on])
        core = Wd[:, ml:ml + n]
        core = core - core.mean(1, keepdims=True)
        core /= np.linalg.norm(core, axis=1, keepdims=True) + 1e-12
        new = on.copy()
        for i in range(len(pool)):
            m = (ty == ty[i]) & (np.abs(lr - lr[i]) < nb)
            m[i] = False
            if m.sum() < 3:
                continue
            T = core[m].mean(0)
            cc = np.empty(2 * ml + 1)
            for l in range(-ml, ml + 1):
                s = Wd[i, ml + l:ml + l + n]; s = s - s.mean()
                cc[l + ml] = np.dot(s, T) / (np.linalg.norm(s) + 1e-12)
            j = int(np.argmax(cc)); fr = 0.0
            if 0 < j < len(cc) - 1:
                d = cc[j - 1] - 2 * cc[j] + cc[j + 1]
                fr = 0.5 * (cc[j - 1] - cc[j + 1]) / d if d != 0 else 0.0
            new[i] = on[i] + (j - ml + fr)
        on = new
    mp = {}
    for g, o in zip(pool, on):
        mp[g["o"]] = o
    for g, o in zip(pool, on):
        g["o_raw"] = g["o"]; g["o"] = float(o)
    for g in pool:
        g["o_prev"] = mp.get(g["o_prev"], g["o_prev"]); g["o_next"] = mp.get(g["o_next"], g["o_next"])
    W = np.array([win(o, a, b) for o in on]); W = W - W.mean(1, keepdims=True)
    W /= np.linalg.norm(W, axis=1, keepdims=True) + 1e-12
    for i, g in enumerate(pool):
        m = (ty == ty[i]) & (np.abs(lr - lr[i]) < nb); m[i] = False
        g["lf_sim"] = float(np.dot(W[i], W[m].mean(0)) / (np.linalg.norm(W[m].mean(0)) + 1e-12)) if m.sum() >= 3 else float("nan")
    return pool


def attacks(x, pool):
    """each pulse's attack in the source: the sample within +-ATTACK_SPAN_MS of (onset - ATTACK_LEAD_MS) where the
    energy above ATTACK_FC in the ATTACK_K_MS after over the ATTACK_K_MS before peaks (build_loops.py's refine_onsets on
    the source); for the onset, the previous and the next pulse of each grain (g["a"], g["a_prev"], g["a_next"])."""
    hf = bandpass(x, lo=ATTACK_FC)
    c = np.concatenate([[0.0], np.cumsum(hf ** 2)])
    k = int(ATTACK_K_MS * 1e-3 * SR)
    lead, span = ATTACK_LEAD_MS * 1e-3 * SR, int(ATTACK_SPAN_MS * 1e-3 * SR)
    memo = {}

    def att(o):
        key = round(float(o), 3)
        if key not in memo:
            q = np.clip(int(round(o - lead)) + np.arange(-span, span + 1), k, len(x) - k - 1)
            v = (c[q + k] - c[q]) / (c[q] - c[q - k] + 1e-20)
            memo[key] = float(q[int(np.argmax(v))])
        return memo[key]
    for g in pool:
        g["a"] = min(att(g["o"]), g["o"])
        g["a_next"] = min(att(g["o_next"]), g["o_next"])
        g["a_prev"] = min(att(g["o_prev"]), g["o_prev"])
    return pool


# --- synthesis -----------------------------------------------------------------------------------------------------------------

def slow_noise(L, n, sd_db, f_lo=0.5, f_hi=6.0, rng=None):
    """a periodic (period L samples) band-limited random signal, sampled at n even points, sd sd_db"""
    if sd_db <= 0:
        return np.zeros(n)
    f = np.fft.rfftfreq(n, L / SR / n)
    spec = (rng.normal(size=len(f)) + 1j * rng.normal(size=len(f))) * ((f >= f_lo) & (f <= f_hi))
    s = np.fft.irfft(spec, n)
    return s / (np.std(s) + 1e-12) * sd_db


def synth(xl, xh, pool, R, n_cyc, rng, D_ms, kappa=1.0, beta=0.55, gam_l=0.3, gam_h=0.2, slow_db=0.3,
          sig=0.05, tol=0.10, avoid=6, jit_ms=JITTER_MS, xf_ms=XF_MS, guard_ms=GUARD_MS, ab_hf_keep=1.0,
          theta=None, avoid_frac=AVOID_FRAC, hf_var=HF_VAR):
    """One loop at R over n_cyc cycles from the pool: consecutive grains crossfade just before each attack (each
    interval is one grain's material). theta: the B pulse's crank angle (None: 315 degrees plus the source's offset
    D_ms). Returns (the loop, its report)."""
    P = cycle_len(R)
    L = int(round(n_cyc * P))
    P = L / n_cyc
    sab = 315.0 / 720.0 * P + D_ms * 1e-3 * SR if theta is None else theta / 720.0 * P
    marks = np.zeros(2 * n_cyc); types = np.zeros(2 * n_cyc, int)
    marks[0::2] = np.arange(n_cyc) * P
    marks[1::2] = np.arange(n_cyc) * P + sab
    types[1::2] = 1
    marks += rng.normal(0, jit_ms * 1e-3 * SR, len(marks))
    n = len(marks)
    Mx = np.r_[marks, marks[0] + L]
    Tn = np.diff(Mx)
    Tp = np.r_[Mx[0] - (marks[-1] - L), Tn[:-1]]
    X = int(xf_ms * 1e-3 * SR); gd = int(guard_ms * 1e-3 * SR)
    # selection weights
    rp = np.array([g["rpm"] for g in pool]); ty = np.array([g["type"] for g in pool])
    lr = np.log(rp / R)
    w0 = np.exp(-0.5 * (lr / sig) ** 2) * (np.abs(lr) <= np.log(1 + tol))
    picks, recent = [], {0: [], 1: []}
    av = {t: max(AVOID_MIN, int(avoid_frac * ((w0 > 0) & (ty == t)).sum())) if avoid_frac else avoid for t in (0, 1)}
    for t in types:
        w = w0 * (ty == t)
        for r in recent[t][-av[t]:]:
            w[r] = 0.0
        if w.sum() <= 0:
            w = w0 * (ty == t)
        i = int(rng.choice(len(pool), p=w / w.sum()))
        picks.append(i); recent[t].append(i)
    eps = rng.uniform(-hf_var, hf_var, len(picks)) if hf_var else np.zeros(len(picks))

    def render(g, tp, tn, t0, t1, ep=0.0):
        """the grain on target times [t0, t1) relative to its onset: (LF, HF, valid mask); ep: the HF time axis is
        stretched by (1 + ep) about the onset; valid ends GUARD before the source's next attack"""
        tau = np.arange(t0, t1).astype(float)
        sp_, sn_ = g["o"] - g["o_prev"], g["o_next"] - g["o"]
        rp_, rn_ = (sp_ / tp) ** kappa, (sn_ / tn) ** kappa
        s = np.where(tau < 0, g["o"] + tau * rp_, g["o"] + tau * rn_)
        hi_lim = g.get("a_next", g["o_next"]) - gd
        lo_lim = g["o_prev"] + gd
        valid = (s > lo_lim) & (s < hi_lim)
        # the HF read position: s + ep (d - d^2 / D) on each side of the onset (d = |s - o|, D the side's length): the HF
        # read rate runs from 1 + ep at the onset to 1 - ep at the side's end, where it meets s again (no hole, no overrun)
        d = np.abs(s - g["o"])
        D = np.where(s >= g["o"], hi_lim - g["o"], g["o"] - lo_lim)
        u = np.clip(d / np.maximum(D, 1.0), 0.0, 1.0)
        sh = s + np.sign(s - g["o"]) * ep * d * (1.0 - u)
        sl = np.clip(s, 2, len(xl) - 4)
        sh = np.clip(sh, 2, len(xl) - 4)
        return cubic(xl, sl), cubic(xh, sh), valid

    # where each grain must stop: its own material ends before its source's next pulse's attack (not its LF onset,
    # which lies 1.9-3.2 ms into the attack), and before the next grain's attack (at its mark less its lead, in target
    # time)
    def post_len(g, tn):
        rn_ = ((g["o_next"] - g["o"]) / tn) ** kappa
        return (g.get("a_next", g["o_next"]) - g["o"] - gd) / rn_

    def lead_t(g, tp):
        rp_ = ((g["o"] - g["o_prev"]) / tp) ** kappa
        return (g["o"] - g.get("a", g["o"])) / rp_
    leads = np.array([lead_t(pool[picks[k]], Tp[k]) for k in range(n)])
    e = np.array([Mx[k] + min(Tn[k] - leads[(k + 1) % n] - gd, post_len(pool[picks[k]], Tn[k])) for k in range(n)])
    e = np.round(e).astype(int)
    # templates: the mean LF of the pool grains (weights w0) per type at the nominal intervals
    nominal = {0: (P - sab, sab), 1: (sab, P - sab)}
    pre_max = int(X + gd + 0.25 * P)
    tmpl, refl, refh = {}, {}, {}
    levl, levh = {}, {}
    for t in (0, 1):
        tp, tn = nominal[t]
        acc, cnt, lv = np.zeros(pre_max + int(tn) + 2), np.zeros(pre_max + int(tn) + 2), []
        for i in np.where((w0 > 0) & (ty == t))[0]:
            gl, gh, ok = render(pool[i], tp, tn, -pre_max, int(tn) + 2)
            acc += gl * ok * w0[i]; cnt += ok * w0[i]
            body = (np.arange(-pre_max, int(tn) + 2) >= 0) & ok
            levl[i] = 10 * np.log10(np.mean(gl[body] ** 2) + 1e-12)
            levh[i] = 10 * np.log10(np.mean(gh[body] ** 2) + 1e-12)
            lv.append((w0[i], levl[i], levh[i]))
        tmpl[t] = (np.where(cnt > 0, acc / np.maximum(cnt, 1e-12), 0.0), -pre_max)
        lv = np.array(lv)
        refl[t] = float(np.average(lv[:, 1], weights=lv[:, 0]))
        refh[t] = float(np.average(lv[:, 2], weights=lv[:, 0]))
    ab_lf, ab_hf = refl[0] - refl[1], refh[0] - refh[1]
    refh_raw = dict(refh)
    mid = 0.5 * (refh[0] + refh[1])
    for t in (0, 1):                       # keep ab_hf_keep of the A/B difference in HF level
        refh_t = mid + ab_hf_keep * (refh[t] - mid)
        refh[t] = refh_t
    flutter = slow_noise(L, n, slow_db, rng=rng)
    segs, gaps = [], 0
    for k in range(n):
        g = pool[picks[k]]; t = types[k]
        s_out = e[k - 1] - X if k > 0 else e[n - 1] - L - X
        t0, t1 = int(s_out - round(Mx[k])), int(e[k] - round(Mx[k]))
        gl, gh, ok = render(g, Tp[k], Tn[k], t0, t1, eps[k])
        gaps += int((~ok).sum())
        tm, toff = tmpl[t]
        ii = np.arange(t0, t1) - toff
        inside = (ii >= 0) & (ii < len(tm))
        m_on = np.where(inside, tm[np.clip(ii, 0, len(tm) - 1)], gl)
        gl = gl * 10 ** (-(1 - gam_l) * (levl[picks[k]] - refl[t]) / 20)
        gl = m_on + beta * (gl - m_on)
        gh = gh * 10 ** (-((1 - gam_h) * (levh[picks[k]] - refh_raw[t]) + (refh_raw[t] - refh[t])) / 20)
        seg = (gl + gh) * ok * 10 ** (flutter[k] / 20)
        segs.append((int(s_out), seg))
    out = np.zeros(L)
    ti = (np.arange(X) + 0.5) / X
    cs = []
    for k in range(n):
        u = segs[k][1][-X:]; v = segs[(k + 1) % n][1][:X]
        uu, vv = u - u.mean(), v - v.mean()
        cs.append(float(np.dot(uu, vv) / (np.linalg.norm(uu) * np.linalg.norm(vv) + 1e-12)))
    for k in range(n):
        s_out, seg = segs[k]
        cin, cout = max(cs[k - 1], 0.0), max(cs[k], 0.0)
        w = np.ones(len(seg))
        w[:X] = ti / np.sqrt(ti ** 2 + (1 - ti) ** 2 + 2 * ti * (1 - ti) * cin)
        w[-X:] *= (1 - ti) / np.sqrt(ti ** 2 + (1 - ti) ** 2 + 2 * ti * (1 - ti) * cout)
        np.add.at(out, (s_out + np.arange(len(seg))) % L, seg * w)
    # start the file at the quietest point of the first cycle (5 ms RMS of the whole signal plus 3 ms RMS above 1.5 kHz,
    # each re its median), so the file starts and wraps in a pulse's tail, not on an attack
    def rms_c(sig, k):
        return np.sqrt(np.convolve(np.r_[sig[-k:], sig, sig[:k]] ** 2, np.ones(k) / k, "same")[k:-k])
    f = np.fft.rfftfreq(L, 1 / SR)
    hi_sig = np.fft.irfft(np.fft.rfft(out) * (f > 1500), L)
    e5, h3 = rms_c(out, int(0.005 * SR)), rms_c(hi_sig, int(0.003 * SR))
    crit = e5 / np.median(e5) + h3 / np.median(h3)
    lo, hi = int(marks[0] % L) + X, int(marks[0] % L) + int(P)
    rot = (lo + int(np.argmin(crit[np.arange(lo, hi) % L]))) % L
    out = np.roll(out, -rot)
    marks = marks - rot
    use = np.bincount(picks, minlength=len(pool))
    info = dict(len_s=round(L / SR, 3), cycles=n_cyc, rpm_exact=round(120.0 * SR / P, 3), pulses=n,
                pool_in_tolerance=int((w0 > 0).sum()), pool_rpm=[round(float(rp[w0 > 0].min()), 0), round(float(rp[w0 > 0].max()), 0)],
                distinct_grains=int((use > 0).sum()), max_reuse=int(use.max()),
                pool_sources=sorted(set(pool[i]["src"] for i in np.where(w0 > 0)[0])),
                pool_events=int(len(set(pool[i]["event"] for i in np.where(w0 > 0)[0]))),
                join_corr_median=round(float(np.median(cs)), 3) if cs else None,
                join_corr_p10=round(float(np.percentile(cs, 10)), 3) if cs else None,
                gap_samples=gaps, start_rotation_samples=int(rot), AB_level_diff_dB=dict(lf=round(ab_lf, 2), hf=round(ab_hf, 2)),
                onsets=[int(round(m)) % L for m in marks], attacks=[int(round(m - ld)) % L for m, ld in zip(marks, leads)],
                theta_deg=round(float(sab / P * 720.0), 2), avoid_per_type=[int(av[0]), int(av[1])], hf_var=hf_var,
                attack_lead_ms=[round(float(np.percentile(leads, q)) / SR * 1e3, 2) for q in (10, 50, 90)])
    return out, info


def coherence(y, R):
    """adjacent-cycle correlation at R (circular): mean"""
    Lc = cycle_len(R)
    yy = np.tile(y, 2)
    n = int(len(y) // Lc) + 1
    C = yy[(np.arange(n)[:, None] * Lc + np.arange(int(Lc))[None, :]).astype(int)]
    C = C - C.mean(1, keepdims=True)
    r = (C[:-1] * C[1:]).sum(1) / (np.linalg.norm(C[:-1], axis=1) * np.linalg.norm(C[1:], axis=1) + 1e-12)
    return float(r.mean())


def fluctuation(y, win=0.1, hop=0.025, ma=1.0):
    """the natural-fluctuation measure on a loop (tiled, circular): 100 ms level sd (dB) and centroid sd (%) after a 1 s
    moving average"""
    yy = np.tile(y, 3)
    W, H = int(win * SR), int(hop * SR)
    a0, a1 = len(y) - int(0.6 * SR), 2 * len(y) + int(0.6 * SR)
    seg = yy[a0:a1]
    n = (len(seg) - W) // H
    fr = np.stack([seg[i * H:i * H + W] for i in range(n)])
    L = 10 * np.log10(np.mean(fr ** 2, 1) + 1e-12)
    S = np.abs(np.fft.rfft(fr * np.hanning(W), 8192, axis=1)) ** 2
    f = np.fft.rfftfreq(8192, 1 / SR); m = (f >= 20) & (f <= 16000)
    C = (f[m] * S[:, m]).sum(1) / (S[:, m].sum(1) + 1e-20)
    k = int(round(ma / hop)) | 1
    ker = np.ones(k) / k
    Lr = (L - np.convolve(L, ker, "same"))[k // 2:n - k // 2]
    Cm = np.convolve(C, ker, "same")
    Cr = ((C - Cm) / Cm)[k // 2:n - k // 2]
    return float(np.std(Lr)), float(100 * np.std(Cr))


def calibrate(xl, xh, pool, R, n_cyc, seed, D_ms, state, kw):
    """beta for the cycle coherence (on load), then the slow flutter for the 100 ms level sd; same seed throughout"""
    log = []
    if state == "on":
        best = None
        for b in BETA_GRID:
            y, _ = synth(xl, xh, pool, R, n_cyc, np.random.default_rng(seed), D_ms, **dict(kw, beta=b))
            c = coherence(y, R)
            log.append(("beta", b, round(c, 3)))
            if best is None or abs(c - COH_TARGET_ON) < best[0]:
                best = (abs(c - COH_TARGET_ON), b)
        kw = dict(kw, beta=best[1])
    best = None
    for fl in FLUTTER_GRID:
        y, _ = synth(xl, xh, pool, R, n_cyc, np.random.default_rng(seed), D_ms, **dict(kw, slow_db=fl))
        lv, cv = fluctuation(y)
        log.append(("flutter", fl, round(lv, 3)))
        if best is None or abs(lv - LEV_SD_TARGET) < best[0] - 0.02:     # prefer less flutter when nearly equal
            best = (abs(lv - LEV_SD_TARGET), fl)
    kw = dict(kw, slow_db=best[1])
    return kw, log


# --- output ---------------------------------------------------------------------------------------------------------------------

def limit(y):
    a = np.abs(y)
    over = a > KNEE
    out = y.copy()
    out[over] = np.sign(y[over]) * (KNEE + (1 - KNEE) * np.tanh((a[over] - KNEE) / (1 - KNEE)))
    return out, int(over.sum())


def write_unlimited(path, y, peak_db=-1.0):
    """the same loop scaled so its peak is at peak_db (nothing limited); returns the gain to -13.5 dBFS RMS"""
    y = y * 10 ** (peak_db / 20) / (np.max(np.abs(y)) + 1e-12)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    rms = 20 * np.log10(np.sqrt(np.mean(y ** 2)) + 1e-12)
    return dict(unlimited_rms_dBFS=round(float(rms), 2), unlimited_gain_to_loop_rms_dB=round(float(-13.5 - rms), 2))


def write(path, y):
    y = y * LOOP_RMS / (np.sqrt(np.mean(y ** 2)) + 1e-12)
    peak = 20 * np.log10(np.max(np.abs(y)) + 1e-12)
    y, n = limit(y)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    return dict(rms_dBFS=round(float(20 * np.log10(np.sqrt(np.mean(y ** 2)))), 2), peak_before_limiter_dBFS=round(float(peak), 1),
                limited_pct=round(100.0 * n / len(y), 3))


def build_pools(x, log=print):
    rises, chains, starts = find_rises(x)
    D_ms = float(np.median([c["D_ms"] for c in chains]))
    log(f"rises: {len(chains)} blips, {len(rises)} pulses; B offset {D_ms:+.2f} ms (median over blips; IQR "
        f"{np.percentile([c['D_ms'] for c in chains], 25):+.2f}..{np.percentile([c['D_ms'] for c in chains], 75):+.2f}); "
        f"crank-fit residual {np.median([c['resid_ms'] for c in chains]):.2f} ms")
    xl = bandpass(x, hi=FC_LF)
    pools = {"rise": refine(rises, xl)}
    fp, finfo = find_falls(x, chains, starts, D_ms)
    for R, g in fp.items():
        pools[f"fall{int(R)}"] = refine(g, xl)
        log(f"falls at {R:.0f}: {len(finfo[R]['pieces'])} pieces, {len(g)} pulses, pooled HF two-peak contrast {finfo[R]['pooled_hf_two_peak_contrast']}")
    low = list(pools["fall1600"])
    for g in pools["fall1800"]:
        if not any(h["type"] == g["type"] and abs(h["o"] - g["o"]) < 0.002 * SR for h in low):
            low.append(g)
    pools["fall_low"] = low
    for k, p in pools.items():
        sims = [g["lf_sim"] for g in p if np.isfinite(g.get("lf_sim", np.nan))]
        if sims:
            log(f"  pool {k}: {len(p)} pulses, LF similarity to the neighbours' mean after alignment: median {np.median(sims):.3f}")
    meta = dict(B_offset_ms=round(D_ms, 3), rise_blips=[dict(start_s=round(c["start"], 2), pulses=c["n"], rpm=[round(v) for v in c["rpm"]],
                                                         B_offset_ms=round(c["D_ms"], 2)) for c in chains],
                falls={str(int(R)): v for R, v in finfo.items()})
    return pools, D_ms, xl, meta


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--idle", type=Path, required=True, help="demodave's recording (stereo as downloaded, or its right channel)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seconds", type=float, default=5.0, help="loop length, rounded to whole cycles (4-6 s)")
    ap.add_argument("--only", default="", help="comma-separated loop names to build (default all)")
    ap.add_argument("--no-calibrate", action="store_true", help="use the table's beta and flutter as they are")
    ap.add_argument("--unlimited", type=Path, default=None,
                    help="also write each loop with its peak at -1 dBFS and no limiter (for further EQ; loops.json gives the gain back to -13.5 dBFS RMS)")
    a = ap.parse_args()
    x, note = read_lead(a.idle)
    if not 160.0 < len(x) / SR < 163.0:
        raise SystemExit("this doesn't look like demodave's recording (161.9 s expected)")
    print(f"{a.idle.name}: {note}")
    a.out.mkdir(parents=True, exist_ok=True)
    pools, D_ms, xl, meta = build_pools(x)
    for k in pools:
        attacks(x, pools[k])
    xh = x - xl
    report = {"_source": dict(file=a.idle.name, channel=note, **meta)}
    idle_db = 10 * np.log10(np.mean(x[int(92.0 * SR):int(98.3 * SR)] ** 2))   # the idle loop's span (make_piece_loops.py)
    only = set(s for s in a.only.split(",") if s)
    for name, R, state, src, sig, tol, kappa, beta, gl, gh, slow, seed in LOOPS:
        if only and name not in only:
            continue
        pool = pools[src]
        if len(pool) < 8:
            print(f"{name}: pool {src} too small ({len(pool)} pulses), skipped")
            continue
        n_cyc = int(round(a.seconds * R / 120.0))
        kw = dict(kappa=kappa, beta=beta, gam_l=gl, gam_h=gh, slow_db=slow, sig=sig, tol=tol, ab_hf_keep=AB_HF_KEEP.get(name, 1.0),
                  theta=B_ANGLE_LOOP.get(name, B_ANGLE[state]))
        calib = []
        if not a.no_calibrate:
            kw, calib = calibrate(xl, xh, pool, R, n_cyc, seed, D_ms, state, kw)
        y, info = synth(xl, xh, pool, R, n_cyc, np.random.default_rng(seed), D_ms, **kw)
        coh = coherence(y, R); lv, cv = fluctuation(y)
        sel = [g for g in pool if abs(np.log(g["rpm"] / R)) <= np.log(1 + tol)]
        src_lv = [10 * np.log10(np.mean(x[int(g["o"]):int(g["o_next"])] ** 2)) - idle_db for g in sel]
        info.update(source_pulse_level_re_idle_dB=round(float(np.median(src_lv)), 1),
                    source_pulse_level_re_idle_IQR_dB=[round(float(np.percentile(src_lv, 25)), 1), round(float(np.percentile(src_lv, 75)), 1)])
        info.update(coherence=round(coh, 3), level_sd_100ms_dB=round(lv, 3), centroid_sd_100ms_pct=round(cv, 2))
        w = write(a.out / f"{name}.wav", y)
        if a.unlimited:
            a.unlimited.mkdir(parents=True, exist_ok=True)
            w.update(write_unlimited(a.unlimited / f"{name}.wav", y))
        report[name] = dict(base_rpm=R, state=state, pool=src, params=dict(sigma=sig, tolerance=tol, kappa=kappa, beta=kw["beta"], gamma_l=gl,
                            gamma_h=gh, flutter_db=kw["slow_db"], ab_hf_keep=kw["ab_hf_keep"], jitter_ms=JITTER_MS, xfade_ms=XF_MS,
                            guard_ms=GUARD_MS, B_offset_ms_source=round(D_ms, 3), B_angle_deg=B_ANGLE_LOOP.get(name, B_ANGLE[state]), avoid_frac=AVOID_FRAC,
                            hf_var=HF_VAR, seed=seed), calibration=calib,
                            **{k: v for k, v in info.items() if k not in ("onsets", "attacks")}, **w, onsets=info["onsets"],
                            attacks=info["attacks"])
        print(f"{name}: {info['len_s']:.2f} s, {info['cycles']} cycles at {info['rpm_exact']:.2f} rpm; pool {src} {info['pool_in_tolerance']} pulses "
              f"({info['pool_rpm'][0]:.0f}-{info['pool_rpm'][1]:.0f} rpm, {info['pool_events']} events), {info['distinct_grains']} used, max reuse "
              f"{info['max_reuse']}; joins r median {info['join_corr_median']}; gaps {info['gap_samples']}; beta {kw['beta']} flutter {kw['slow_db']} dB -> "
              f"coherence {info['coherence']}, 100 ms level sd {info['level_sd_100ms_dB']} dB, centroid sd {info['centroid_sd_100ms_pct']}%; "
              f"peak {w['peak_before_limiter_dBFS']} dBFS, limited {w['limited_pct']}%")
    with open(a.out / "loops.json", "w") as fh:
        json.dump(report, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
