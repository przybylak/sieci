#!/usr/bin/env python3
"""A ride through the engine model (engine_model.py), rendered the way the game plays it.

  python3 -I render.py --loops <dir> --out ride.wav [--stepped] [--table idle:860,on:1400,...] [--cfg '{"ShiftRpm": 2600}']
                       [--ride ride.csv]

The ride (31 s, the demo ride every demo of the engine sound has used): 0-2.4 s the start sound (the loops silent),
2.4-6 idle, 6-10 full throttle from rest, 10-16 the top speed (900 u/s) with the key held, 16-19 key released (the
bike coasts down to ~350 u/s), 19-22 full throttle again, 22-25 braking to a stop, 25-28 idle, at 28 the stop sound.

Each loop is ONE voice playing round and round, as in the game (a loop listed in both families too); once a frame
(60 fps) the model sets every voice's pitch and level, which the voice glides to within the frame (as SetFrequency and
a short FadeTo would), or with --stepped the pitch jumps once a frame as the game's SetFrequency does (the level still
glides, as a short FadeTo does). Every loop is first scaled to one RMS, so the model's gains mean the same thing for
each. The voices start together at their files' first sample. The start's last 0.3 s and the stop's first 0.5 s are
matched to the idle's level from the model's level law. The loops play from 2.2 s (a 0.3 s fade-in) to 28.2 s (a 0.25 s
fade-out).

--table is the loop set in the plugin INI's [Sound] Loops form: family:base rpm, comma-separated, where idle:R is
CMB_EngineIdleLP.wav, on:R is CMB_EngineOn<R>LP.wav and off:R is CMB_EngineOff<R>LP.wav (default: the shipped set),
except on:2000, the cruise sound record's CMB_EngineCruiseLP.wav (CMB_EngineOn2000LP.wav in a set built before it took
that name, demo D's: read when there is no CMB_EngineCruiseLP.wav). The CSVs name the voices by their table entry.
--cfg overrides model constants (engine_model.DEFAULTS' names), as a JSON object or a path to a JSON file.

--ride plays a recorded ride instead of the demo ride: a CSV with the header t,speed,forward,braking[,held] (seconds,
units a second, 0/1, 0/1, 0/1: the plugin's trace replayed, say), the speed interpolated between rows and the keys held
from each row. It starts 2.4 s in (after the start sound) and is followed by 3 s at rest and the stop sound.

Writes the WAV (mono 16-bit, peak-normalised to 0.89), <out>.csv (the model's state at 10 Hz: t, speed, forward,
gear, rpm, load, the rider's load, the on-family weight, clutch in, in an up-shift, coasting, the level in dB) and
<out>_frames.csv (every frame: the state and each loop's gain and pitch), and prints the state every 0.5 s."""
import argparse
import json
import os
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine_model import Engine  # noqa: E402

FPS = 60
SR = 44100
TABLE = "idle:860,on:1400,on:1700,on:2000,on:2400,on:2800,on:3300,off:1400,off:1800,off:2300,off:2800"
FILE_NAME = {"CMB_EngineOn2000LP": "CMB_EngineCruiseLP"}   # the voice's file where it isn't the voice's name


def loop_file(loops_dir, name):
    """The WAV a voice plays: FILE_NAME's, or the voice's own name when that one isn't there (an older set)."""
    path, own = Path(loops_dir) / f"{FILE_NAME.get(name, name)}.wav", Path(loops_dir) / f"{name}.wav"
    return own if not path.is_file() and own.is_file() else path


def parse_table(line):
    """'idle:860,on:1400,...' -> (on [(name, rpm)], off [(name, rpm)], idle (name, rpm))."""
    on, off, idle = [], [], None
    for item in line.split(","):
        fam, _, r = item.strip().partition(":")
        rpm = float(r)
        if fam == "idle":
            idle = ("CMB_EngineIdleLP", rpm)
        elif fam in ("on", "off"):
            (on if fam == "on" else off).append((f"CMB_Engine{fam.capitalize()}{int(rpm)}LP", rpm))
        else:
            raise SystemExit(f"--table: {item!r}: the family is idle, on or off")
    if idle is None or not on:
        raise SystemExit("--table: an idle loop and at least one on-load loop are needed")
    return on, off, idle


def read(path):
    """A 16-bit WAV -> (float samples, the mean of the channels; sample rate)."""
    with wave.open(str(path)) as w:
        sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
        if w.getsampwidth() != 2:
            raise SystemExit(f"{path}: 16-bit PCM WAV expected")
        x = np.frombuffer(w.readframes(n), "<i2").astype(float) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(1)
    return x, sr


def write(path, y, sr):
    y = np.clip(y, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((y * 32767).astype("<i2").tobytes())


def ride_profile():
    """(t) -> (speed u/s, forward 0/1, braking) for the demo ride."""
    def at(t):
        if t < 6.0:
            return 0.0, 0.0, False
        if t < 16.0:
            v = 900.0 * min(1.0, max(0.0, (t - 6.15) / 3.2)) ** 1.15
            return v, 1.0, False
        if t < 19.0:
            v = 350.0 + 550.0 * np.exp(-(t - 16.0) / 1.2)
            return v, 0.0, False
        if t < 22.0:
            v0 = 350.0 + 550.0 * np.exp(-3.0 / 1.2)
            v = v0 + (900.0 - v0) * min(1.0, (t - 19.0) / 2.6) ** 1.1
            return v, 1.0, False
        if t < 25.0:
            v = max(0.0, 900.0 * (1.0 - (t - 22.0) / 2.4))
            return v, 0.0, True
        return 0.0, 0.0, False
    return at


def csv_profile(path, offset=2.4):
    """(t) -> (speed, forward, braking, held) from a ride CSV (t,speed,forward,braking[,held]), its first row at offset s;
    and the ride's length."""
    rows = []
    with open(path) as fh:
        head = fh.readline().strip().split(",")
        for ln in fh:
            if ln.strip():
                rows.append([float(x) for x in ln.split(",")])
    a = np.array(rows)
    t = a[:, 0] - a[0, 0]
    col = {n: i for i, n in enumerate(head)}

    def at(tt):
        x = tt - offset
        if x < 0.0 or x > t[-1]:
            return 0.0, 0.0, False, False
        i = min(len(t) - 1, int(np.searchsorted(t, x, side="right")) - 1)
        v = float(np.interp(x, t, a[:, col["speed"]]))
        hd = bool(a[i, col["held"]]) if "held" in col else False
        return v, float(a[i, col["forward"]]), bool(a[i, col["braking"]]) and v > 10.0, hd
    return at, float(t[-1])


def render(loops_dir, cfg, loops_on, loops_off, idle, T=31.0, start=(0.0, "CMB_EngineStart"), stop=(28.0, "CMB_EngineStop"),
           run_from=2.2, run_to=28.2, step_pitch=False, phase_seed=None, profile=None):
    """Returns (rows, the raw mix, the voices' names). rows: (t, v, fwd, gear, rpm, load, rider load, on-family weight,
    {loop: (gain, pitch)}, clutch, in_shift, coasting, level dB). phase_seed: start every loop at a random point
    instead (the game starts them together, so their relative phase at a hand-over is arbitrary)."""
    buf = {}
    names = list(dict.fromkeys([n for n, _ in loops_on] + [n for n, _ in loops_off] + [idle[0]]))   # one voice per loop
    for n in names:
        x, s = read(loop_file(loops_dir, n))
        if s != SR:
            raise SystemExit(f"{n}.wav: {s} Hz; 44100 expected")
        buf[n] = x / (np.sqrt(np.mean(x ** 2)) + 1e-12) * 0.1
    eng = Engine(list(loops_on), list(loops_off), tuple(idle), cfg)
    prof = profile or ride_profile()
    N = int(T * SR)
    out = np.zeros(N)
    pos = {n: 0.0 for n in names}
    if phase_seed is not None:
        rng = np.random.default_rng(phase_seed)
        pos = {n: float(rng.uniform(0, len(buf[n]))) for n in names}
    gain_prev = {n: 0.0 for n in names}
    pitch_prev = {n: 1.0 for n in names}
    spf = SR // FPS
    rows = []
    ramp = np.linspace(0, 1, spf, endpoint=False)
    for f in range(N // spf):
        t = f / FPS
        v, fwd, brk, *held = prof(t)
        mix = eng.step(1.0 / FPS, v, fwd, brk, bool(held and held[0]))
        run = 1.0 if run_from <= t < run_to else 0.0
        if t < run_from + 0.3 and run:
            run = (t - run_from) / 0.3
        if t >= run_to - 0.25 and run:
            run = max(0.0, (run_to - t) / 0.25)
        rows.append((t, v, fwd, eng.gear + 1, eng.rpm, eng.load, eng.rload, eng.fam_w,
                     {n: (g * run, p) for n, (g, p) in mix.items()}, float(eng.clutch), float(eng.in_shift),
                     float(eng.coasting), eng.level_db()))
        i0 = f * spf
        for n in names:
            g, p = mix.get(n, (0.0, pitch_prev[n]))
            g *= run
            gs = gain_prev[n] + (g - gain_prev[n]) * ramp
            ps = np.full(spf, p) if step_pitch else pitch_prev[n] + (p - pitch_prev[n]) * ramp
            if gain_prev[n] > 1e-5 or g > 1e-5:
                b = buf[n]
                ph = pos[n] + np.cumsum(ps)
                idx = ph % len(b)
                i = np.floor(idx).astype(int)
                fr = idx - i
                out[i0:i0 + spf] += (b[i] * (1 - fr) + b[(i + 1) % len(b)] * fr) * gs
                pos[n] = ph[-1] % len(b)
            else:
                pos[n] = (pos[n] + spf * p) % len(buf[n])
            gain_prev[n], pitch_prev[n] = g, p
    # the one-shots, scaled so the idle in them (the start's last 0.3 s, the stop's first 0.5 s) meets the idle's level
    idle_level = 0.1 * eng.idle_level()
    for (t, n), seg in ((start, "tail"), (stop, "head")):
        if n:
            x, _ = read(Path(loops_dir) / f"{n}.wav")
            part = x[-int(0.3 * SR):] if seg == "tail" else x[:int(0.5 * SR)]
            x = x * idle_level / (np.sqrt(np.mean(part ** 2)) + 1e-12)
            i = int(t * SR)
            out[i:i + len(x)] += x[:N - i]
    return rows, out, names


def write_csv(rows, names, out_csv, frames_csv):
    with open(out_csv, "w") as fh:
        fh.write("t,speed,forward,gear,rpm,load,rider_load,on_family,clutch,in_shift,coasting,level_db\n")
        for r in rows[::6]:
            fh.write(",".join(f"{v:.3f}" for v in r[:8] + r[9:]) + "\n")
    with open(frames_csv, "w") as fh:
        fh.write("t,speed,gear,rpm,load,rider_load,on_family,clutch,in_shift,level_db," + ",".join(f"g_{n},p_{n}" for n in names) + "\n")
        for r in rows:
            m = r[8]
            fh.write(f"{r[0]:.4f},{r[1]:.2f},{r[3]},{r[4]:.1f},{r[5]:.3f},{r[6]:.3f},{r[7]:.3f},{r[9]:.0f},{r[10]:.0f},{r[12]:.3f}," +
                     ",".join(f"{m.get(n, (0.0, 0.0))[0]:.4f},{m.get(n, (0.0, 0.0))[1]:.4f}" for n in names) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--loops", type=Path, required=True, help="the loop set (build_loops.py --out)")
    ap.add_argument("--out", type=Path, required=True, help="the WAV to write (the CSVs go beside it)")
    ap.add_argument("--stepped", action="store_true", help="the pitch steps once a frame, as the game sets it")
    ap.add_argument("--table", default=TABLE, help="the loop set as family:rpm,... (the plugin INI's Loops form)")
    ap.add_argument("--cfg", default=None, help="model constants to override: a JSON object or a JSON file")
    ap.add_argument("--phase-seed", type=int, default=None, help="start each loop at a random point (seeded)")
    ap.add_argument("--ride", default=None, help="a recorded ride (CSV t,speed,forward,braking[,held]) instead of the demo ride")
    a = ap.parse_args()
    cfg = None
    if a.cfg:
        cfg = json.load(open(a.cfg)) if os.path.isfile(a.cfg) else json.loads(a.cfg)
    on, off, idle = parse_table(a.table)
    kw = {}
    if a.ride:
        prof, length = csv_profile(a.ride)
        T = 2.4 + length + 3.0
        kw = dict(profile=prof, T=T, stop=(T - 3.0, "CMB_EngineStop"), run_to=T - 2.8)
    rows, mix, names = render(a.loops, cfg, on, off, idle, step_pitch=a.stepped, phase_seed=a.phase_seed, **kw)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    write(a.out, mix / np.max(np.abs(mix)) * 0.89, SR)
    write_csv(rows, names, a.out.with_suffix(".csv"), a.out.with_name(a.out.stem + "_frames.csv"))
    print(f"peak of the raw mix (before the 0.89 normalisation): {float(np.max(np.abs(mix))):.4f}")
    for r in rows[::30]:
        print(f"t {r[0]:5.1f} v {r[1]:4.0f} fwd {r[2]:.0f} gear {r[3]} rpm {r[4]:5.0f} load {r[5]:.2f} rider {r[6]:.2f} on {r[7]:.2f} "
              f"{'C' if r[9] else ' '}{'S' if r[10] else ' '}{'c' if r[11] else ' '} {r[12]:+5.1f} dB  " +
              " ".join(f"{k[10:]}:{g:.2f}@{p:.2f}" for k, (g, p) in r[8].items() if g > 0.005))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
