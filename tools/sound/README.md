# Engine sound tools

The bike's engine is a set of looping recordings that the plugin pitches and fades every frame, from an rpm, gear and
load model driven by the bike's speed and the forward key. Without the plugin, the script crossfades the idle and
cruise loops by speed. These tools build that set from one recording and render a ride through it, so you can hear it
before it goes into the game.

```
sh tools/sound/run_all.sh <demodave's idle.wav> [out dir]          # everything, about 8 minutes on 4 cores
```

| File | What it does |
|---|---|
| `make_grain_loops.py` | Pulse-grain loops for the riding range. Every firing pulse of the recording's 34 blips and the falls after them is found, typed (the V-twin's A and B pulses) and timed. A loop at R rpm lays real pulses at R's firing times, each drawn at random from the pulses nearest R. Ten loops: on load at 1400 to 3300 rpm, throttle shut at 1400 to 2800 rpm. Writes them limited and unlimited, plus each pulse's attack. |
| `make_piece_loops.py` | The files cut from the recording itself. These are the idle loop (92.0 to 98.3 s), the start (0.25 to 2.6 s) and the stop (158.6 to 160.6 s), plus the 2300 rpm closed-throttle loop made from 18 flattened pieces of its falls. Before that it finds every engine cycle in the recording with a dechirped comb map and a cycle walker. |
| `build_loops.py` | The shipped set. Each riding loop's tone is matched to the reference ride: a third-octave EQ, the brightness law, the attacks, the half-order line pattern on 1400, 1700 and 2000, and the pulse-to-pulse brightness. Each loop is then levelled to -13.5 dBFS RMS through a look-ahead limiter. The idle, start and stop are copied as they are. The 2000 rpm loop on load is written as `CMB_EngineCruiseLP.wav`, the file the cruise sound record plays. |
| `hot_loops.py` | The last stage, since test 45's answer: every one of the 13 files 2.5 dB hotter, its peaks rounded off by a memoryless soft limiter (knee -6 dBFS, ceiling -1). See *Hotter loops* below. |
| `engine_model.py` | The engine model: rpm, gear, load, and each loop's pitch and level, frame by frame. The plugin's C port follows it, and every constant's measured basis is in its `DEFAULTS`. Since test 45's build the gears follow a "heard speed" with a real ride's limits rather than the game's bike (`HeardSpeed` and the keys after it). |
| `render.py` | Renders the demo ride, or a recorded one (`--ride`), through the model and a loop set, the way the game plays it. Writes a WAV and CSVs of the model's state. |
| `run_all.sh` | Runs all of the above, end to end. |
| `make_engine_sounds.py` | The old synthesiser: the fallback set (see below). |

Every tool runs isolated (`python3 -I`) with its files as arguments. It needs Python 3 and numpy, nothing else.

## The recordings

- **demodave, "Harley Davidson Sportster - Idling with Engine Revs"**, Freesound 502690,
  <https://freesound.org/s/502690/>. Licence: **Creative Commons 0**, a public-domain dedication with no conditions; it
  is credited as a courtesy.
  - Every file of the set comes from this recording.
  - Download the WAV as Freesound offers it: stereo, 16-bit, 44.1 kHz, 161.9 s. The tools check the length.
  - Its two channels are one signal 1024 samples (23.2 ms) apart, so averaging them would build a slapback into every
    pulse. Each tool takes the leading (right) channel itself, found by cross-correlation.
- **spinopel, "harley-davidson-sportster-acceleration"**, Pixabay 345717. Licence: **Pixabay Content License** (free to
  use, no attribution needed, but the raw file may not be passed on as it is).
  - It gave the earlier set its on-load loops.
  - Nothing of it is in this set, and none of these tools reads it.

**The reference rides** are three on-board videos of an Iron 883 (`daily`, `autumn`, `paris` in the comments). They are
someone else's recordings, and they are only measured. The tools store what was measured as plain numbers:

- the octave and third-octave shapes, the brightness law, the envelope crests and the line patterns, in `build_loops.py`;
- the model's constants, in `engine_model.py`.

Nothing of their audio is in any file, and the tools don't need them to build.

## Commands

The whole build, with an optional check against a known-good set:

```
sh tools/sound/run_all.sh ~/Downloads/<demodave's WAV>                       # into tools/sound/out
CHECK=<a known-good loops dir> sh tools/sound/run_all.sh <WAV> <out dir>    # also cmp every WAV with it
HOT=0 sh tools/sound/run_all.sh <WAV> <out dir>                             # without the last stage: test 45's set
```

`run_all.sh` writes three folders:

- `<out>/loops/`: the 13 files for `Data\Sound\FX\CMB`, plus `loops.json`, which records what each file was made from
  and its measures before and after (`build_loops.py`'s, then `hot_loops.py`'s). They are the idle, the start, the stop, `CMB_EngineCruiseLP.wav` (the 2000 rpm
  loop on load: the plugin's On2000, and the cruise of the script's crossfade) and the nine more the plugin drives.
- `<out>/demo/`: `CMB_engine_demo.wav` (the pitch glides within each frame) and `CMB_engine_demo_stepped.wav` (the
  pitch steps once a frame, as the game sets it), each with its CSVs.
- `<out>/work/`: the grain and piece tools' outputs, and every tool's log.

The steps one by one:

```
python3 -I tools/sound/make_grain_loops.py --idle <WAV> --out <work>/grains --unlimited <work>/grains_unlimited
python3 -I tools/sound/make_piece_loops.py --idle <WAV> --out <work>/pieces
python3 -I tools/sound/build_loops.py --grains <work>/grains --unlimited <work>/grains_unlimited \
        --pieces <work>/pieces --out <loops>
python3 -I tools/sound/hot_loops.py --in <loops> --out <loops>      # in place; --gain 0 changes nothing
python3 -I tools/sound/render.py --loops <loops> --out ride.wav [--stepped]
```

### Hotter loops (since test 45's answer)

In test 45 the tester set the engine to 100 in the MCM (an instance volume of 1.0, the most the game takes) and still
found it too quiet. The game plays the loops faithfully; they were made quiet: `build_loops.py` levels each riding loop
to -13.5 dBFS RMS with its peaks at -1 dBFS, a crest (peak over RMS) of 12.5 dB, where the reference rides' is 9.2 to
11.7 dB. `hot_loops.py` treats all 13 files alike:

- the gain, +2.5 dB, then a curve on each sample alone: the identity up to the knee (-6 dBFS); from there a cubic
  (Hermite) from slope 1 at the knee to slope 0 at the ceiling (-1 dBFS, the 16-bit step at or under it), reached where
  the loops' own peaks land (-1 dBFS + the gain); the ceiling beyond that (only the start's crank reaches it);
- no memory, so a loop's wrap stays exactly as seamless as built, and the start and the stop need no edge handling;
- a set already through it is refused (its `loops.json` has the "hot" entries), and `--gain 0` writes every file back
  byte for byte.

On test 45's set (2026-10-27):

| File | RMS dBFS | Peak dBFS | Crest dB | Over the knee | Residual re 4-16 kHz | Wrap step, x the median step |
|---|---|---|---|---|---|---|
| Idle (860) | -13.50 → -11.08 | -1.01 → -1.00 | 12.49 → 10.08 | 6.6 % | -26.1 dB | 1.30 → 1.30 |
| On1400 | -13.50 → -11.30 | -1.00 → -1.00 | 12.50 → 10.30 | 9.2 % | -13.1 dB | 0.34 → 0.35 |
| On1700 | -13.50 → -11.25 | -1.00 → -1.00 | 12.50 → 10.25 | 8.4 % | -13.6 dB | 0.42 → 0.43 |
| Cruise (On2000) | -13.50 → -11.20 | -1.00 → -1.00 | 12.50 → 10.20 | 7.8 % | -15.0 dB | 0.88 → 0.90 |
| On2400 | -13.50 → -11.18 | -1.00 → -1.00 | 12.50 → 10.18 | 7.2 % | -16.7 dB | 0.37 → 0.37 |
| On2800 | -13.50 → -11.12 | -1.00 → -1.00 | 12.50 → 10.12 | 7.7 % | -15.6 dB | 1.24 → 1.26 |
| On3300 | -13.50 → -11.09 | -1.00 → -1.00 | 12.50 → 10.09 | 9.0 % | -17.2 dB | 0.36 → 0.36 |
| Off1400 | -13.50 → -11.11 | -1.00 → -1.00 | 12.50 → 10.11 | 7.2 % | -23.4 dB | 0.55 → 0.56 |
| Off1800 | -13.50 → -11.13 | -1.11 → -1.00 | 12.39 → 10.13 | 7.1 % | -23.2 dB | 1.86 → 1.90 |
| Off2300 | -13.50 → -11.11 | -1.89 → -1.13 | 11.61 → 9.98 | 5.6 % | -23.2 dB | 2.15 → 2.18 |
| Off2800 | -13.50 → -11.05 | -1.00 → -1.00 | 12.50 → 10.05 | 6.3 % | -25.5 dB | 0.54 → 0.54 |
| Start | -15.88 → -13.77 | -0.00 → -1.00 | 15.88 → 12.77 | 3.4 % | -14.5 dB | |
| Stop | -21.52 → -19.03 | -7.43 → -4.96 | 14.09 → 14.07 | 0.1 % | -52.3 dB | |

- The RMS rises 2.3 to 2.5 dB (the limiter takes back up to 0.2 of the 2.5), the loops' crest comes to 10.0-10.3 dB.
- The seam check of `build_loops.py` (the wrap's second difference as a percentile of the loop's own) moves by under
  0.7 points on every loop: Cruise 44.7 → 45.2, On1400 0.7 → 0.8, On2800 95.4 → 95.6 (it was that before).
- The price of no memory is some distortion on the pulses' peaks. The residual column is the curve's non-linear part
  (the output less its best linear fit to the input) against the file's own 4-16 kHz band. On the on-load loops it
  lies 13 to 17 dB under that band, on the others 23 to 26; octave by octave it lies at least 13.8 dB under the loop's
  own up to 8 kHz (10.5 in On2800's 16 kHz octave, where the loop has little). A look-ahead gain limiter like
  `build_loops.py`'s (2 ms ramps, circular, so just as seamless) would leave it 20-24 dB under on the on-load loops,
  with their crest at 10.2-10.5. If the pulses sound gritty, that is the alternative.
- `loops.json` keeps every file's entry and adds "hot": the settings, the measures before and after, the share over
  the knee, the residual and the wrap. The entry's own `rms_dBFS`, `peak_dBFS` and `kloud_re_rms_dB` become the
  file's after this stage.

### Trying other constants or another loop set

You can audition a change before it goes into the plugin's INI:

```
python3 -I tools/sound/render.py --loops <loops> --out ride.wav --cfg '{"ShiftRpm": 2600, "Wander": 0.0}'
python3 -I tools/sound/render.py --loops <loops> --out ride.wav --table idle:860,on:1400,on:2000,off:1800
python3 -I tools/sound/render.py --loops <loops> --out ride.wav --ride ride.csv
```

- `--cfg` takes `engine_model.DEFAULTS` names, as a JSON object or a JSON file. The plugin's `[Sound]` section has a
  key for each of these constants.
- `--table` is the loop set in the INI's `Loops` form, family:base rpm. `idle:R` means `CMB_EngineIdleLP.wav`, `on:R`
  means `CMB_EngineOn<R>LP.wav` and `off:R` means `CMB_EngineOff<R>LP.wav`, except `on:2000`, which is
  `CMB_EngineCruiseLP.wav` (or `CMB_EngineOn2000LP.wav` when that isn't there: a set built before the cruise took
  that name, as demo D's was). The CSVs name each loop by its table entry.
- `--ride` plays a recorded ride instead of the demo ride: a CSV with the header `t,speed,forward,braking[,held]`
  (seconds, units a second, then 0 or 1 each; `held` is the plugin holding the throttle for something ahead). The
  speed is interpolated between rows and the keys kept from each row. The ride starts 2.4 s in, after the start sound,
  and ends with 3 s at rest and the stop sound. Demo E (test 45's build) is 51 s of test 44's ride, its speed and keys
  every 0.25 s from the plugin's log, rendered this way.
- Test 44's model is `--cfg '{"HeardSpeed": 0, "CoastFall": 70, "DownRpm": 1750, "ClutchFall": 900, "LevelScale": 0.3,
  "LevelOffset": 0, "LaunchDraw": [0, 0], "LaunchRise": 0, "ShiftDraw": [0, 0], "DownHold": 0, "DownHeld": 0}'`, the same
  values the INI's comments give. Test 45's levels are `--cfg '{"LevelScale": 0.7, "LevelOffset": 0}'` (test 46: LevelScale
  1.0, LevelOffset +5 dB, each loop's gain held at 0 dB).
- The CSV (`ride.csv`, 10 rows a second) gives the gear, rpm, load, on-family weight, clutch, shift and coast state,
  and the level. `ride_frames.csv` gives every frame's gain and pitch per loop.

### The build is repeatable

Every random choice is seeded: the grain loops by the seed in their table row, and the model's pitch wander by
`WanderSeed`. On 2026-10-26 (Python 3.13, numpy 2.5.3), a rebuild from the downloaded file was checked:

- All 13 files matched, byte for byte, the set the user heard as demo D (that check is now made with `HOT=0`: demo D's
  set, like test 45's, predates the last stage) (its `CMB_EngineOn2000LP.wav` is
  `CMB_EngineCruiseLP.wav` here; `CHECK` compares the two when the known-good set has the old name).
- `render.py` on those files gave demo D's WAVs and CSVs byte for byte.
- The CSV's gears and rpm matched `engine_model.py` driven on its own over the same ride.

Another numpy or BLAS can change the last bits of an FFT. A rebuild there can differ by a least significant bit here and
there. The piece tool's cycle walker can then also pick a cycle differently.

## Why the WAVs aren't in the repository

They are made from someone else's recording. CC0 lets the mod ship them, but this repository holds only the project's
own work and the tools that turn other people's material into the mod's files. The meshes built from the game's files
follow the same rule (see `.gitignore`).

- The package carries the built set.
- The repository keeps no 5 MB of binaries that would change whenever a constant does.
- The reference videos aren't ours at all, so only numbers measured from them are here.

`.gitignore` keeps `tools/sound/out/` out, and also keeps out the nine loops (`CMB_EngineOn*LP.wav` and
`CMB_EngineOff*LP.wav`) built into `Data/Sound/FX/CMB`. Don't build into `Data/Sound/FX/CMB` in the repository: the
idle, the cruise, the start and the stop would overwrite the four tracked fallback files, which no ignore pattern
can keep out.

## The fallback set: `make_engine_sounds.py`

The old synthesiser is now the fallback. It makes original audio with nothing sampled: a 45-degree V-twin firing
pattern, an exhaust thump and a noise burst per pulse.

```
python3 tools/sound/make_engine_sounds.py --out Data/Sound/FX/CMB [--seed 7]
```

It writes four files: `CMB_EngineStart`, `CMB_EngineStop`, `CMB_EngineIdleLP` (~900 rpm) and `CMB_EngineCruiseLP`
(~2700 rpm). These are the four files the repository carries in `Data/Sound/FX/CMB`, the fallback: they have no gear
model and no other loops, and are made only for the script's two-loop crossfade. The nine other loops the plugin drives
(`CMB_EngineOn1400LP` to `CMB_EngineOff2800LP`) exist only in the package, built by `run_all.sh` from demodave's
recording, whose idle, cruise (the 2000 rpm loop on load), start and stop replace these four there.

So a build from the repository alone has no full set for the plugin. The ESP's nine sound records name files that
aren't there, and what the game's `Sound.Play` gives for them hasn't been seen:

- 0 or less: the controller's check of the ids stops at the first ("Engine sound: the script's crossfade (loop 2,
  On1400, has the instance id 0: it didn't play)." in the Papyrus log), offers nothing and plays its crossfade of
  these four, as in test 43.
- The id of an instance that plays nothing: the check passes it (it looks only at the ids' range) and the plugin takes
  the set and drives it. Only two loops then sound: the idle at rest, and this cruise, pitched as a 2000 rpm loop (a
  third high), only on load between about 1840 and 2190 rpm. Everywhere else on load, and all through a roll-off,
  there is silence.

With the plugin, `[Sound] Drive=0` in `CMB_Slope.ini` makes it decline every set, so such a build gets the crossfade
either way.
