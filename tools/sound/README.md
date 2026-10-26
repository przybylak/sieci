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
| `engine_model.py` | The engine model: rpm, gear, load, and each loop's pitch and level, frame by frame. The plugin's C port follows it, and every constant's measured basis is in its `DEFAULTS`. |
| `render.py` | Renders the demo ride through the model and a loop set, the way the game plays it. Writes a WAV and CSVs of the model's state. |
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
```

`run_all.sh` writes three folders:

- `<out>/loops/`: the 13 files for `Data\Sound\FX\CMB`, plus `loops.json`, which records what each file was made from
  and its measures before and after. They are the idle, the start, the stop, `CMB_EngineCruiseLP.wav` (the 2000 rpm
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
python3 -I tools/sound/render.py --loops <loops> --out ride.wav [--stepped]
```

### Trying other constants or another loop set

You can audition a change before it goes into the plugin's INI:

```
python3 -I tools/sound/render.py --loops <loops> --out ride.wav --cfg '{"ShiftRpm": 2600, "Wander": 0.0}'
python3 -I tools/sound/render.py --loops <loops> --out ride.wav --table idle:860,on:1400,on:2000,off:1800
```

- `--cfg` takes `engine_model.DEFAULTS` names, as a JSON object or a JSON file. The plugin's `[Sound]` section has a
  key for each of these constants.
- `--table` is the loop set in the INI's `Loops` form, family:base rpm. `idle:R` means `CMB_EngineIdleLP.wav`, `on:R`
  means `CMB_EngineOn<R>LP.wav` and `off:R` means `CMB_EngineOff<R>LP.wav`, except `on:2000`, which is
  `CMB_EngineCruiseLP.wav` (or `CMB_EngineOn2000LP.wav` when that isn't there: a set built before the cruise took
  that name, as demo D's was). The CSVs name each loop by its table entry.
- The CSV (`ride.csv`, 10 rows a second) gives the gear, rpm, load, on-family weight, clutch, shift and coast state,
  and the level. `ride_frames.csv` gives every frame's gain and pitch per loop.

### The build is repeatable

Every random choice is seeded: the grain loops by the seed in their table row, and the model's pitch wander by
`WanderSeed`. On 2026-10-26 (Python 3.13, numpy 2.5.3), a rebuild from the downloaded file was checked:

- All 13 files matched, byte for byte, the set the user heard as demo D (its `CMB_EngineOn2000LP.wav` is
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
