#!/usr/bin/env python3
"""Synthesises the motorbike's engine sounds (original audio, nothing sampled).

A 45-degree V-twin: two exhaust pulses per 720 degrees of crank, 405 and 315
degrees apart, which gives the uneven "potato" idle. Each pulse is a low thump
from the exhaust pipe plus a burst of filtered noise; a quiet valve-train tick
and a little saturation make it less synthetic.

  CMB_EngineStart.wav     starter motor, catch, rev, settle to idle (one-shot)
  CMB_EngineStop.wav      idle running down to a stop (one-shot)
  CMB_EngineIdleLP.wav    ~900 rpm, seamless loop
  CMB_EngineCruiseLP.wav  ~2700 rpm, seamless loop

44.1 kHz, 16-bit mono WAV, the format the Creation Kit expects.

  python make_engine_sounds.py --out <Data>/Sound/FX/CMB [--seed 7]
"""

import argparse
import math
import wave
from pathlib import Path

import numpy as np

SR = 44100
FIRING_OFFSETS = (0.0, 405.0)  # crank degrees within each 720-degree cycle


def firing_times(rpm_at, duration):
    """Times (s) at which a cylinder fires, for an rpm curve rpm_at(t)."""
    t = np.arange(int(duration * SR)) / SR
    rpm = np.maximum(rpm_at(t), 0.0)
    crank = np.cumsum(rpm / 60.0 * 360.0 / SR)  # degrees
    times = []
    cycle = 0
    while True:
        done = True
        for off in FIRING_OFFSETS:
            angle = cycle * 720.0 + off
            idx = np.searchsorted(crank, angle)
            if idx < len(crank):
                times.append((idx / SR, rpm[idx], 1 if off else 0))
                done = False
        if done:
            return times
        cycle += 1


def damped(freq, tau, length):
    t = np.arange(int(length * SR)) / SR
    return np.sin(2 * math.pi * freq * t) * np.exp(-t / tau)


def band(noise, lo, hi):
    """Band-pass by FFT mask with soft edges; keeps a loop periodic."""
    spec = np.fft.rfft(noise)
    f = np.fft.rfftfreq(len(noise), 1 / SR)
    mask = 1 / (1 + (lo / np.maximum(f, 1)) ** 4) / (1 + (f / hi) ** 4)
    return np.fft.irfft(spec * mask, len(noise))


def convolve(x, k, circular):
    n = len(x) if circular else len(x) + len(k)
    y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(k, n), n)
    return y if circular else y[:len(x)]


def engine(times, length, rng, circular=False, load=0.5):
    """Render exhaust pulses at the given (time, rpm, cylinder) firings."""
    n = int(length * SR)
    impulses = np.zeros(n)
    for t, rpm, cyl in times:
        i = int(t * SR) % n if circular else int(t * SR)
        if i < n:
            gain = (1.0 if cyl == 0 else 0.86) * rng.uniform(0.88, 1.08)
            impulses[i] += gain * (0.55 + 0.45 * min(rpm / 2500.0, 1.4))
    thump = damped(62, 0.030, 0.25) + 0.55 * damped(124, 0.016, 0.25) + 0.25 * damped(205, 0.010, 0.25)
    low = convolve(impulses, thump, circular)
    envelope = convolve(impulses, np.exp(-np.arange(int(0.06 * SR)) / SR / (0.010 + 0.008 * load)), circular)
    body = band(rng.standard_normal(n), 140, 1300) * envelope
    crack = band(rng.standard_normal(n), 1800, 5200) * convolve(impulses, np.exp(-np.arange(int(0.01 * SR)) / SR / 0.0025),
                                                               circular)
    tick = band(rng.standard_normal(n), 3000, 9000) * (0.5 + 0.5 * np.sign(np.sin(np.cumsum(np.ones(n)) / SR * 2 * math.pi * 18)))
    mix = 1.0 * low + (0.55 + 0.4 * load) * body + 0.18 * crack + 0.025 * tick
    return mix


def finish(signal, peak_db=-3.0, fade_in=0.0, fade_out=0.0):
    s = np.tanh(signal / (np.max(np.abs(signal)) + 1e-9) * 1.6)  # a little grit
    if fade_in:
        k = int(fade_in * SR)
        s[:k] *= np.linspace(0, 1, k)
    if fade_out:
        k = int(fade_out * SR)
        s[-k:] *= np.linspace(1, 0, k)
    s *= 10 ** (peak_db / 20) / (np.max(np.abs(s)) + 1e-9)
    return s


def loop(rpm, cycles, rng, load):
    """Exactly `cycles` engine cycles, rendered circularly so the loop is seamless."""
    length = cycles * 720.0 / (rpm / 60.0 * 360.0)
    n = int(round(length * SR))
    length = n / SR
    times = []
    for c in range(cycles):
        for off in FIRING_OFFSETS:
            jitter = rng.normal(0, 0.0012)
            times.append(((c * 720.0 + off) / (rpm / 60.0 * 360.0) + jitter, rpm, 1 if off else 0))
    sig = engine(times, length, rng, circular=True, load=load)
    sig = np.tanh(sig / (np.max(np.abs(sig)) + 1e-9) * 1.6)
    return sig * 10 ** (-3.0 / 20) / np.max(np.abs(sig))


def starter(duration, rng):
    """Starter motor whine with cranking compression bumps."""
    t = np.arange(int(duration * SR)) / SR
    crank = 0.5 + 0.5 * np.sin(2 * math.pi * 4.2 * t) ** 2
    saw = sum(np.sin(2 * math.pi * 210 * k * t * (1 + 0.04 * t)) / k for k in range(1, 8))
    whine = 0.35 * saw * crank + 0.15 * band(rng.standard_normal(len(t)), 600, 3000) * crank
    return whine * np.minimum(1, t / 0.05)


def start_sound(rng):
    crank_time, run_time = 0.65, 2.1
    total = crank_time + run_time

    def rpm(t):
        r = np.zeros_like(t)
        run = t - crank_time
        catch = (run >= 0)
        rise = 300 + 2300 * np.clip(run / 0.32, 0, 1) ** 0.7
        settle = 900 + (2600 - 900) * np.exp(-np.maximum(run - 0.32, 0) / 0.35)
        r[catch] = np.where(run[catch] < 0.32, rise[catch], settle[catch])
        return r
    sig = engine(firing_times(rpm, total), total, rng, load=0.7)
    s = starter(crank_time + 0.08, rng)
    sig[:len(s)] += s * np.max(np.abs(sig)) * 0.5
    return finish(sig, fade_out=0.05)


def stop_sound(rng):
    total = 1.6

    def rpm(t):
        return np.where(t < 1.15, 900 * np.clip(1 - t / 1.15, 0, 1) ** 0.6 + 120 * (t < 1.0), 0)
    sig = engine(firing_times(rpm, total), total, rng, load=0.3)
    sig *= np.clip(1.25 - np.arange(len(sig)) / SR / 1.3, 0, 1)
    clunk = damped(48, 0.05, 0.3) * 0.6
    at = int(1.12 * SR)
    sig[at:at + len(clunk)] += clunk[:len(sig) - at] * np.max(np.abs(sig))
    return finish(sig, fade_in=0.01, fade_out=0.1)


def write_wav(path: Path, samples):
    data = (np.clip(samples, -1, 1) * 32767).astype("<i2").tobytes()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)
    print(f"wrote {path}  {len(samples) / SR:.2f}s")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    write_wav(args.out / "CMB_EngineStart.wav", start_sound(rng))
    write_wav(args.out / "CMB_EngineStop.wav", stop_sound(rng))
    write_wav(args.out / "CMB_EngineIdleLP.wav", loop(900, 15, rng, load=0.3))
    write_wav(args.out / "CMB_EngineCruiseLP.wav", loop(2700, 45, rng, load=0.8))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
