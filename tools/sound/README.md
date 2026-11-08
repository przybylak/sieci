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
| `engine_model.py` | The engine model: rpm, gear, load, and each loop's pitch and level, frame by frame. The plugin's C port follows it, and every constant's measured basis is in its `DEFAULTS`. Since test 45's build the gears follow a "heard speed" with a real ride's limits rather than the game's bike (`HeardSpeed` and the keys after it); since the 2026-11-01a build a stop shifts down with blips (`StopShift`); since the 2026-11-02a build the idle is louder (`IdleDb` -11, -17.2 before: test 48's "make it louder when idle"); since the 2026-11-09a build each gear has its own heard rise and least time (`HeardRiseGears`, `ShiftGapGears`: test 50's "3rd gear pinned", and test 51's "1st < 2nd < 3rd"). `--check-off` checks its off values against four earlier builds' frames (`check_off_2026-10-31a.txt` to `check_off_2026-11-06a.txt`). |
| `render.py` | Renders the demo ride, or a recorded one (`--ride`), through the model and a loop set, the way the game plays it. Writes a WAV and CSVs of the model's state. |
| `make_water_loop.py` | Since the 2026-11-06a build: the mod's own wet-road water loop, `CMB_FxWaterRoadLP.wav`, from the tester's example 1 (see *The wet road* below), with `water.json` and its listen-free checks. Since the 2026-11-09a build `--variant gentle` makes the gentler one, `CMB_FxWaterRoadSoftLP.wav`, with `water_gentle.json` (see *The gentle wet road*); `--measure` checks a loop already made. |
| `run_all.sh` | Runs all of the above, end to end (both wet roads with `WATER=`). |
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
- **freesound_community, "Cars driving on a wet road 3"**, Pixabay 101246 (test 49's tester's example 1). Licence:
  **Pixabay Content License** (as spinopel's). `make_water_loop.py` cuts three stretches of it into the mod's own wet-road
  loops (since the 2026-11-09a build also a gentler one); the recording and the loops stay out of the repository. Check the file's Pixabay page before a package ships the
  loop (the licence shown, and whether it names a Freesound original and its author, who then gets the credit).

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
WATER=<example 1 as WAV> sh tools/sound/run_all.sh <WAV> <out dir>          # also both wet roads, into loops/
```

`run_all.sh` writes three folders:

- `<out>/loops/`: the 13 files for `Data\Sound\FX\CMB`, plus `loops.json`, which records what each file was made from
  and its measures before and after (`build_loops.py`'s, then `hot_loops.py`'s). They are the idle, the start, the stop, `CMB_EngineCruiseLP.wav` (the 2000 rpm
  loop on load: the plugin's On2000, and the cruise of the script's crossfade) and the nine more the plugin drives. With
  `WATER=` also the two wet roads, `CMB_FxWaterRoadLP.wav` and `CMB_FxWaterRoadSoftLP.wav`, with `water.json` and
  `water_gentle.json` (15 WAVs).
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
  "LevelOffset": 0, "LaunchDraw": [0, 0], "LaunchRise": 0, "ShiftDraw": [0, 0], "DownHold": 0, "DownHeld": 0, "IdleDb": -17.2}'`,
  the same values the INI's comments give. Test 45's levels are `--cfg '{"LevelScale": 0.7, "LevelOffset": 0, "IdleDb": -17.2}'`
  (test 46: LevelScale 1.0, LevelOffset +5 dB, each loop's gain held at 0 dB).
- The 2026-10-31a build's model is `--cfg '{"StopShift": 0, "ShiftDraw": [2000, 2900], "IdleDb": -17.2}'`. The 2026-11-01a build
  draws each pull's up-shift from `ShiftDraw` 2300-3000 and gives a stop its down-shifts (`StopShift`, with `HeardStop`,
  `HeardBrake`, `StopGap`, `StopHold` and `StopAfter`: the comments on `DEFAULTS`); the demo ride renders with them by default.
- The 2026-11-01a build's model is `--cfg '{"IdleDb": -17.2}'`. The 2026-11-02a build's idle (test 48: "make it louder when
  idle", "when bike stops on obstacle it goes fully quiet") is `IdleDb` -11: the idle at -6.0 dB, 2.5 dB under test 48's
  cruise, where the start and stop sounds' idle parts meet it (`make_piece_loops.py`'s `IDLE_LEVEL_DB`). It is the floor of
  every state, so a roll-off to a stop stays at -6.0 dB instead of sinking to -12.2; the cruise and every pull are as
  before. `render.py` scales its start and stop sounds to meet the model's idle, so in the renders they now sit 6.2 dB
  higher, where the game plays them (the files as made, which the game doesn't scale).
- The 2026-11-02a build's model is `--cfg '{"IdleDb": -11, "ShiftTime": 0.35, "ShiftDipTime": 0.24, "LaunchFlare": 0}'`. The
  2026-11-06a build (test 49: "idle could be a slightly louder", "gear sound should be longer on each shift", "I just want
  take off to be faster"): `IdleDb` -9, the idle at -4.0 dB, level with the cruise (a let-off at the cruise keeps its level);
  `ShiftTime` 0.55 and `ShiftDipTime` 0.4, the off family through 0.55 s of each gap, the shift points as before; and a launch
  rev, `LaunchFlare` 0.5 over `LaunchFlareTime` 1.2 s: a press in 1st revs the slip by up to half over itself, 1938 rpm and
  -1.1 dB at +0.5 s in the harness's game where the 2026-11-02a build had 1432 and -5.2; the gears as before.
- The 2026-11-06a build's model (the 2026-11-08a build's too) is `--cfg '{"HeardRiseGears": [1, 1, 1, 1], "ShiftGapGears": []}'`.
  The 2026-11-09a build (test 50: "3rd gear pinned", 1.26 s against 2nd's 1.42 in the tester's log): the heard speed rose
  `HeardRise` all pull, met the bike early in 3rd, the load and with it the up-shift point fell to `ShiftLo`, and 3rd waited
  only for `MinShiftGap`. Now each gear has its own heard rise, `HeardRiseGears` 1, 0.95, 0.5, 1 (x `HeardRise`, the rise
  only), and its own least time before its up-shift, `ShiftGapGears` 0, 1.5, 1.75 s (0 or missing: `MinShiftGap`). On the
  harness's game pull (12 s of W) 2nd lasts 1.54 s and 3rd 1.75 (1.46 and 1.25 before), 4th at 7.13 s (6.55), the rpm
  still climbing through 3rd (under 50 rpm/s for 0.12 s, 0.29 before). A sharp slow-down in 3rd also comes back more
  slowly: after a 0.15 s tap of the brake at the cruise (the heard speed down to about 550), 3rd takes about 5 s back to
  900 (2.5 s before).
- Test 51 ("1st < 2nd < 3rd"): 1st was all clutch slip, the heard speed rising at `HeardRise` from the launch's lead to the
  1->2 point while the bike passed 900 at 3.25 s (the logs' 1st 2.85-3.98 s, median 3.47 over 11 pulls from rest; the
  twin 3.83), so the first set made 1st > 3rd > 2nd. Now `HeardRiseGears` 2.5, 0.95, 0.5, 1 (1st's rise x 2.5, the slip's
  rpm climbing with it: 1900 -> 2566 rpm in 1.5 s) and `ShiftGapGears` 0, 2.0, 2.5: on the harness's game pull 1st lasts
  1.54 s, 2nd 2.00, 3rd 2.50, 4th at 6.04 s from the press (7.13 before). A quicker throttle (a 2 s ramp) gives the same;
  a slow, uphill pull (a 4 s ramp) 1.37 / 2.86 / 2.50, the one case where 2nd outlasts 3rd (it waits for the bike).
  Rejected: 2.6 with 1.75, 2.4 (1.48 / 1.99 / 2.40, thinner margins); 2.2 with 1.9, 2.4 (1st 1.75 against 2nd's 1.90).
  `--cfg '{"HeardRiseGears": [1, 0.95, 0.5, 1], "ShiftGapGears": [0, 1.5, 1.75]}'` is the first set's model (the
  2026-11-09a build as of t54-merge), frame for frame.
- The CSV (`ride.csv`, 10 rows a second) gives the gear, rpm, load, on-family weight, clutch, shift and coast state,
  and the level. `ride_frames.csv` gives every frame's gain and pitch per loop.

### The off values' check

```
python3 -I tools/sound/engine_model.py --check-off                       # 0 if each build's off values give its frames
python3 -I tools/sound/engine_model.py --check-off --off 02a             # only the 2026-11-02a build's
python3 -I tools/sound/engine_model.py --check-off --against <old model> --off 01a   # frame by frame against another file
```

`--check-off` runs the model over the demo ride, a random ride of 60 segments in the harness's game and five stops (44,136
frames) four times, once with each earlier build's off values, and compares each frame (the gear, the rpm, the clutch, the heard
level and every loop's gain and pitch, exactly) with that build's file, 500 frames a hash, and its gear changes:

| `--off` | the off values | the file | written from |
|---|---|---|---|
| `31a` | `StopShift=0`, `ShiftDraw` 2000,2900, `IdleDb` -17.2 (and the later builds' `ShiftTime` 0.35, `ShiftDipTime` 0.24, `LaunchFlare` 0, `HeardRiseGears` 1,1,1,1, `ShiftGapGears` empty) | `check_off_2026-10-31a.txt` | 0c3df02's `engine_model.py` |
| `01a` | `IdleDb` -17.2 (and the same five) | `check_off_2026-11-01a.txt` | 993f582's `engine_model.py` |
| `02a` | `IdleDb` -11, `ShiftTime` 0.35, `ShiftDipTime` 0.24, `LaunchFlare` 0 (and the later two) | `check_off_2026-11-02a.txt` | f0253e8's `engine_model.py` |
| `06a` | `HeardRiseGears` 1,1,1,1, `ShiftGapGears` empty | `check_off_2026-11-06a.txt` | 6bc75e4's `engine_model.py` (the 2026-11-08a build's: unchanged) |

It prints each ride's count and one line a build, `check-off: the same, frame for frame over 44136 frames (HeardRiseGears=1,1,1,1,
ShiftGapGears= against the 2026-11-06a build's model)`, and exits 1 if any frame differs. Each file is written from that build's own model
(`git show 993f582:tools/sound/engine_model.py > old.py`, then `--write-expected old.py --off 01a`). The 2026-10-31a file's
hashes are 0c3df02's, whose own `IdleDb` was -17.2; only its header's off values gained `IdleDb` (rewritten the same way with
`--off 31a`: every other line the same). The 2026-11-06a build's three keys were the same in 0c3df02's and 993f582's models
(ShiftTime 0.35, ShiftDipTime 0.24, no launch rev), so both older files' hashes stand; only their headers' off values gained
the three. The 2026-11-02a file is f0253e8's (`--write-expected old.py --off 02a`). The 2026-11-06a file is 6bc75e4's
(`--write-expected old.py --off 06a`); none of the older models had the 2026-11-09a build's two keys, so the three older files
were written again from their own models with them: the hashes the same, only line 2's off values longer.

### The wet road (the 2026-11-06a build)

```
ffmpeg -i <the mp3> -c:a pcm_s16le ex1.wav                                    # in a new, empty folder
python3 -I -B tools/sound/make_water_loop.py --ex1 ex1.wav --out <dir>       # CMB_FxWaterRoadLP.wav and water.json
```

Test 49's tester heard the water loop of the 2026-11-02a build (the game's small waterfall splatter, pitched up 15 %, 76 %
of it above 4 kHz) as "frying or crumpling foil" and sent two recordings of cars on a wet road. Example 1 is steady traffic:
a smooth hiss with no crackle, centroid about 1.86 kHz. The tool takes its three clean stretches (0.30-3.10, 4.40-8.10 and
9.60-11.90 s: not the start, a 1.35-1.70 kHz tone at 3.2-4.2 s or a low thump at 8.4-8.7 s), mono, at 44.1 kHz, high-passed at
120 Hz and rolled off from 6 kHz, splices them with 0.25 s equal-power crossfades, flattens the slow level (0.4 s, within
6 dB), wraps the tail into the head over 0.4 s and levels it to -23 dBFS A-weighted. On example 1 as Pixabay gives it
(24 kHz stereo, 11.98 s; the tool checks that):

| measure | the loop |
|---|---|
| length | 7.90 s, 44.1 kHz mono 16-bit (the engine WAVs' format) |
| level | RMS -23.1 dBFS, A-weighted -23.0, peak -9.8; the 20 ms level's p10-p90 -24.2 to -22.2 (2.0 dB) |
| spectrum | centroid 1763 Hz (example 1: 1863); under 250 Hz 2 %, 250 Hz-4 kHz 91 %, over 4 kHz 7 % |
| the wrap | spectral step 0.676 (the loop's own 0.1 s steps: median 0.675, p90 0.718), level step -0.21 dB (median 0.33, p90 1.04), sample step at the 90th percentile of all |

Every one of those is a check (`water.json` holds them; exit 1 if one fails), none of them by ear: the seam within the
loop's own steps, the centroid within 15 % of example 1's, the level at its target. The game plays the file as 0x8A9
`CMB_FxWaterRoadLPSD`'s, `Data\Sound\FX\CMB\CMB_FxWaterRoadLP.wav`, when the MCM's "Water sound loop" is on "Wet road"
(the 2026-11-08a build's default, option 2 since the 2026-11-09a build); `[Fx] WaterRoadDb` trims it. The build is
repeatable (byte for byte on a second run, numpy 2.5.3).

### The gentle wet road (the 2026-11-09a build)

```
python3 -I -B tools/sound/make_water_loop.py --variant gentle --ex1 ex1.wav --out <dir>   # CMB_FxWaterRoadSoftLP.wav, water_gentle.json
python3 -I -B tools/sound/make_water_loop.py --variant gentle --measure <a loop WAV>      # its checks on a loop already made
```

Test 50's tester heard the wet road as "staticky": 41 % of it at 1-2 kHz and 27 % over 2 kHz, 2 % under 250 Hz (the
recording itself has 8 %). The gentle variant takes the same three stretches, splices, flattening and wrap, with another
shape and level: a second-order high-pass at 60 Hz (not 120: the traffic's body kept), a second-order roll-off from 2.5 kHz
(not first-order from 6 kHz), a first-order low shelf +5 dB under 300 Hz, a 3 dB dip at 1.5 kHz (a Gaussian on a log
frequency axis, 1.5 octaves wide at half its depth) and -26.5 dBFS A-weighted (3.5 dB quieter). Without `--variant` the tool
is the 2026-11-06a build's, byte for byte (the WAV and `water.json`, checked on example 1).

| measure | the wet road (2) | the gentle wet road (3) |
|---|---|---|
| length | 7.90 s | 7.90 s, 44.1 kHz mono 16-bit |
| level | RMS -23.1 dBFS, A-weighted -23.0, peak -9.8 | RMS -25.2 dBFS, A-weighted -26.5, peak -11.7; the 20 ms level's p10-p90 -26.5 to -24.2 (2.2 dB) |
| bands | under 250 Hz 2.3 %, 250 Hz-1 kHz 29.0, 1-2 kHz 41.3, 2-4 kHz 20.2, 4-8 kHz 6.4 | 11.2 %, 49.0, 29.6, 9.4, 0.9 |
| centroid | 1763 Hz | 1008 Hz |
| the wrap | spectral step 0.676 (p90 0.718), level step -0.21 dB (p90 1.04) | spectral step 0.640 (the loop's own 0.1 s steps: median 0.665, p90 0.718), level step +0.25 dB (median 0.35, p90 1.28), sample step at the 83rd percentile of all |

Its checks (exit 1 if one fails): the seam's three as the wet road's; instead of the centroid within 15 % of example 1's,
the centroid 900-1150 Hz, at least 8 % under 250 Hz, under 35 % at 1-2 kHz, under 2 % over 4 kHz (and over 80 % at
250 Hz-4 kHz); A-weighted at -26.5 within 0.1 dB; the peak and the 20 ms level as the wet road's. On the wet road's loop
(`--measure`) five of them fail (the four spectrum checks and the level). The game plays the file as 0xBF3
`CMB_FxWaterRoadSoftLPSD`'s, `Data\Sound\FX\CMB\CMB_FxWaterRoadSoftLP.wav`, when the MCM's "Water sound loop" is on
"Wet road, gentle" (option 3, the default); `[Fx] WaterRoadDb` trims both wet roads. It is the same kind of derivative of
the same recording (cut, filtered, spliced, re-levelled and looped), shipped in the package with the same credit; neither
loop is in the repository. Repeatable byte for byte on a second run (numpy 2.5.3).

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
