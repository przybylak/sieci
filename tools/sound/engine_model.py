"""The engine's rpm and each loop's pitch and level from the bike's speed and throttle.

This is the reference the plugin's C port follows (tools/f4se-slope: the same constants, the same order of operations,
one call per frame). Speeds are game units per second (900 u/s = the bike's top speed, about 46 km/h).

The constants are calibrated to a V-twin cruiser on the road (the reference rides: "daily", the ride the user pointed to as
the right sound, whose three example stretches ride at median 1800-2060 rpm; "autumn" and "paris", two more; measured
only, nothing of them is in a loop). Every constant's measured basis is in the comments on DEFAULTS below. Revised
after measuring this model's first demo against the reference: the full-throttle up-shift at 2500 rpm with the gears scaled by 2500/3000 (each gear's rpm per
u/s unchanged), MinShiftGap 1.25 s, the level law's own reference LevelRpm 3000, ShiftFamily 1; the rpm rises at most
RiseRate in log rpm a second (the per-frame pitch step leaving idle); in 1st gear the raw demand switches the on family
and below the idle's fade band the family weight jumps (no closed-throttle loop at a launch); a slow random wander of
the family loops' pitch (Wander, WanderTau; an LCG the C twin reproduces). Test 47: the throttle hand (that wander
larger, smoothed, the family loops' level moving with it, only while the throttle is steady: WanderLevel, WanderSteady,
WanderSmooth) and a throttle-off dip at each up-shift (ShiftDip, ShiftDipTime); each 0 is test 46's model. The 2026-10-31a build
(3-5 % for the hand): that walk larger again, held softly under WanderMax before the smoothing, smoothed longer;
WanderMax 0 with 27c's Wander, WanderSmooth is 27c's model. The 2026-11-01a build (test 47: "rpm could be slightly higher
the closer it is to shifting gear", "the sound could indicate that gears are shifted down"): each pull's up-shift drawn
from ShiftDraw 2300-3000 (2000-2900 before), and a stop's down-shifts each blipped (StopShift and the five keys after it,
below); StopShift=0 with ShiftDraw (2000, 2900) is the 2026-10-31a build's model exactly (--check-off). The 2026-11-02a
build (test 48: "make it louder when idle", "when bike stops on obstacle it goes fully quiet"): IdleDb -11 (-17.2
before), the idle at -6.0 dB where the start and stop sounds meet it; IdleDb=-17.2 is the 2026-11-01a build's model
exactly. The 2026-11-06a build (test 49: "idle could be a slightly louder", "gear sound should be longer on each shift", "I just
want take off to be faster"): IdleDb -9 (the idle at -4.0 dB, level with the cruise), ShiftTime 0.55 and ShiftDipTime 0.4
(0.35, 0.24), and a launch rev (LaunchFlare 0.5 over LaunchFlareTime 1.2 s; 0: none); IdleDb=-11 with ShiftTime 0.35,
ShiftDipTime 0.24 and LaunchFlare 0 is the 2026-11-02a build's model exactly (--check-off checks all three builds).

Gearbox. Four gears with the measured steps 1.35 / 1.28 / 1.21; each gear's entry is its speed at ShiftRpm (2500).
2nd reaches ShiftRpm at 750 u/s (3000 rpm at the top speed), 4th cruises at the top speed at 1937 rpm.
  - Up-shift when the gear's rpm at this speed passes ShiftLo + (ShiftRpm - ShiftLo) * pull, where pull is the
    rider's load above the cruise load, 0..1 (0 at a steady speed with the key held; 1 when gaining
    (1 - CruiseLoad) * FullAccel = 220 u/s^2 or more, as the game's 300 u/s^2 does): full throttle shifts at 2500,
    a steady key at 2200. Also: the engine has caught up with its gear (over ShiftCatch of that point: after a
    coast the engine can sit below its gear for a moment, and a quick key tap then shifted up at 1800); the next
    gear lands over DownRpm (else it hunts); MinShiftGap since the last up-shift and DownGap since any shift (a
    gear entered by a down-shift needs at least 0.59 s at 300 u/s^2 to reach 3000, so this never over-revs).
  - An up-shift is a clutch gap of ShiftTime: the rpm first flares (toward its value at the clutch-in x (1 + Flare)
    for FlareTime, time constant FlareTau), then falls to the new gear's rpm with time constant ShiftFall. The
    engine load is cut for the gap; the level and (with ShiftFamily 0) the loop family follow the rider and don't dip.
  - With the throttle on, a down-shift under DownRpm, only if the lower gear's rpm stays under ShiftLo (with the
    landing rule above, neither shift can undo the other at once, whatever the load does), DownGap after any shift.
  - Throttle shut (coast, brake): the rpm dips by LashDip (time constant LashTau: driveline lash) and then follows
    the road speed, but falls no faster than CoastFall (BrakeFall when braking) rpm a second: the game's coast
    (900 to 0 in 2 s) and brake are far harder than a real roll-off (-44..-96 rpm/s in the daily ride). It never
    rises while the throttle is shut, so the gear can follow the speed down silently: it steps to the gear whose
    rpm at this speed is nearer the engine's (in log), at least DownGap apart. No sawtooth, no blips.
  - Clutch in near the stop: throttle shut, 1st gear's rpm at this speed under ClutchIn, and the bike braking or
    slowing by more than ClutchDecel u/s^2, or 1st gear's rpm under the launch slip (IdleRpm + Launch): the engine
    falls to idle, at most ClutchFall rpm a second. (A coast that levels out at ~20 km/h, like the demo ride's,
    stays in gear.) From there the next throttle launches in 1st: the clutch slips at IdleRpm + Launch * the key
    (the rider revs to it at once) until 1st gear's rpm takes over (no step).
  - The rider's load comes from the bike's acceleration smoothed over AccelTau (each frame's raw difference let
    0.5 % of speed noise a frame hold the cruise in 3rd at 2344 by faking a pull).

Loops: the idle loop, and two families (on load and off load), each a list of (name, base rpm); a loop may be in
both (one voice: its gains add in power).
  - The idle fades out over log rpm between IdleRpm + IdleFade[0] and IdleRpm + IdleFade[1] (equal power); the
    families fade in with it.
  - Within a family exactly one loop plays, except for a short crossfade (XfadeTime, equal power) when it hands over
    to another (through an up-shift's gap only downward). The family's loop is the one whose territory holds the
    rpm: the boundary between neighbours a < b is at a * (b / a) ** Split (OnSplit, OffSplit), and the loop changes
    only once the rpm is past a boundary by Hyst (log rpm). A hand-over starts only when the last one has finished.
    (Loops of one engine at one rpm interfere, phasing at ~1 Hz: so one loop at a time, not a blend.)
  - The family: on load when the rider's load rises over OnAbove; off load when the rider's demand (the throttle
    before smoothing) stays under OffBelow for OffHold seconds; the change crossfades over FamilyTime (equal
    power). ShiftFamily=1 also plays the off family through an up-shift's gap (the reference rides' shifts are
    28-35 % darker); 0: the family follows the rider.
  - Pitch = rpm / base, held within MinPitch..MaxPitch, except inside the idle's fade band, where the idle and the
    families' lowest loops follow the rpm unclamped.

Level (the law of the level-linear paris ride, scaled): in dB re full load at LevelRpm (3000),
  LevelScale * max(IdleDb, RpmDb * log2(rpm / LevelRpm) + LoadDb * (rider load - 1)) + LevelOffset,
held at 0 dB (the game's volume tops out there; test 46) before the crossfades, so each loop's gain is 1 at most and a
hand-over at the ceiling stays equal power (level_db() gives it before the ceiling, heard_db() after it, less ShiftDip).
LevelScale 0.3 is what the daily and autumn cameras deliver (0.29-0.36 of paris's range): idle -5.2 dB, full load
at 3000 rpm 0 dB. Test 45: 0.7 (the tester: the cameras' compression copied, not the bike; paris's pull is 11.6 dB over
its idle): idle -12.0 dB. Test 46 (the tester: too quiet, not punchy; the game plays the loops faithfully, its volume
tops out at 1): LevelScale 1.0 and LevelOffset +5 dB: the cruise at -3.8 dB (-6.2 in test 45), a full-load pull at
0 dB (clamped from +1.9 at 2400 rpm: +3.8 over the cruise), the throttle closed at the cruise -2.6..-3.1, the idle
-12.2 dB (8.4 under the cruise; -12.0 in test 45: the one-shots meet it as they did). The demo ride's windows (the
first pull 6.5-10 s, the cruise 12-16 s, power sums): the first pull +2.6 over the cruise (+2.1 at 0.7; paris about
+4 over steady riding; with the 0 dB ceiling a louder cruise leaves a pull less room: 6.8 dB of offset would put the
cruise at -2 and every pull within 2 dB of it). Test 48's answer (the 2026-11-02a build): IdleDb -11, the idle at
-6.0 dB, 2.5 under test 48's cruise (-3.5 at 1990 rpm; it was 8.7 under) and exactly where the start and stop sounds'
idle parts meet it (make_piece_loops.py's IDLE_LEVEL_DB: the start's last 0.3 s and the stop's first 0.5 s 6.0 dB under
the loops, so since test 45 each start dropped 6.2 dB into the idle and each stop rose 6.2 out of it). IdleDb is the
floor of every state: it also holds the throttle shut under about 1945 rpm, the cruise's load under 1650 and a full-load
launch under 1360 (8 % of the random ride's frames, by 6.2 dB at most); the cruise and every pull are untouched, and a
roll-off to a stop stays at -6.0 instead of sinking to -12.2. Test 49's answer (the 2026-11-06a build; the tester tried -11,
-10 and -12 and kept -10, "idle could be a slightly louder when I'm on the bike"): IdleDb -9, the idle at -4.0 dB, level
with the cruise (-3.8 at 1937 rpm in 4th). The floor then holds the throttle shut under about 2250 rpm, so a let-off at the
cruise keeps its level (the off family's timbre and the rpm's dip still tell it; at -11 it fell 1.9 dB, at -10 0.9), and
the start and stop sounds (6.0 dB under the loops) each step 2 dB into and out of the idle. IdleDb=-11 is the 2026-11-02a
build's levels exactly; -10 test 49's.

The heard speed (test 45; HeardSpeed=0: the bike's own speed, as up to test 44). The game's bike does everything 2-3x
faster than the reference rides (0 to 900 u/s in about 3 s, a let-up stops it in about 2 s), and the gears tied to
that speed swept 1st and 2nd in 2 s and fell to idle as the bike stopped. The engine follows a heard speed instead:
  - With the throttle on it rises at most HeardRise u/s^2 (140: 1st's launch about 2.9 s, 2nd 1.3-1.5 s, the rpm
    climbing 470 rpm/s in 2nd, 360 in 3rd; replayed over test 44's ride, the up-shifts 1.25-1.85 s apart and the last
    6 s after the key; paris: first shift at a median 2.6 s, gaps 1.25-1.85 s, 2nd 200-500 rpm/s) toward
    the bike's speed (in 1st toward it + HeardLead: the clutch slipping before the wheels go, only in a launch, from
    the clutch's last going in till the bike passes ClutchSpeed, or a real pull, the bike gaining faster than
    HeardRise: at a steady speed the heard speed is the bike's), and follows a lower bike speed with the time constant
    HeardTau (the rpm dips with a 10 % dip, a few per cent). The rider's load is full while the bike is HeardPull or
    more ahead of it, the cruise load once it has caught up. An up-shift also needs the bike's own speed to land the
    next gear LAND (3 %) over DownRpm, unless the bike gains faster than HeardRise: the slip and the lead don't shift
    up at a steady speed (test 45's review: with the lead at a steady 215-445 u/s the slip passed ShiftLo, 2nd came
    under DownRpm and the gear went 1 <-> 2 every 2-3 s; the 3 % keeps the measured speed's noise from doing the same
    at 443 u/s, where 2nd's rpm meets DownRpm).
  - With it shut it falls CoastFall (BrakeFall braking) rpm a second in the gear (engine braking: paris -150 median),
    never under the bike's speed (the bike faster, it rises as with the throttle on); under CoastDown rpm a down-shift with a throttle blip (the rpm to Blip over the
    new gear's for BlipTime, time constant BlipTau, the rider's load full: paris +27 % peak in 0.3 s, +5 dB); the
    clutch goes in once the bike itself is under ClutchSpeed (or 1st's heard rpm under ClutchIn), the heard speed
    then the bike's.
  - The throttle on with the bike under ClutchSpeed: 1st (a launch; a wall).
  - A stop (StopShift, the 2026-11-01a build; needs the heard speed): with the throttle shut StopAfter s (braking at
    once) the heard speed falls toward a slower bike at least HeardStop (HeardBrake braking) u/s^2, so the gears come
    down through CoastDown one at a time, each with its blip, StopGap apart; the clutch waits up to StopHold after the
    bike itself went under ClutchSpeed, for the heard speed to get there too or a running blip to end, and a blip that
    would end past StopHold isn't started. The throttle on, nothing changes.
The launch (any mode): the clutch slips from LaunchDraw's start (drawn per pull; 0,0: IdleRpm + Launch x the key),
rising LaunchRise rpm a second at the heard speed's fastest rise (LaunchRise x heard speed / HeardRise) until 1st's
rpm takes over; an up-shift out of the slip takes the heard speed to the slip's rpm in 1st (the step to 2nd is the
gear's). The launch rev (the 2026-11-06a build, test 49: "I just want take off to be faster"; the first 0.5-0.75 s of a
launch sat at the IdleDb floor, heard only as a pitch rise): a press in 1st in a launch with the bike under ClutchSpeed
revs the slip by LaunchFlare over itself, the share fading out as a cosine over LaunchFlareTime (1938 rpm and -1.1 dB at
+0.5 s where the 2026-11-02a build had 1432 and -5.2); only 1st's rpm target moves, the slip the gear decisions read, the
heard speed and every shift are as before (LaunchFlare=0: the 2026-11-02a build's). Each pull (each press of the key) draws its full-throttle shift point from ShiftDraw (0,0: ShiftRpm) and its
launch from LaunchDraw, from the wander's LCG in a stream of their own (paris: shifts at 2000-2900, launches at
1250-1500). With the throttle
on, a down-shift only after the gear's rpm (the heard speed's) has stayed under DownRpm for DownHold seconds (0: at
once), and not while the plugin holds or eases its throttle for something ahead (DownHeld: the face rays, a wall,
a ram's hit, the climb's boost: the 'held' input)."""
import json
import math
import os
import sys

DEFAULTS = dict(
    # --- the engine at rest and pulling away
    IdleRpm=860.0,        # the user's choice: demodave's idle loop (the one called perfect) fires every 140.7 ms
                          # = 853 rpm; the reference rides' warm idle is 922-1060 (980 suggested), not used
    Launch=640.0,         # clutch slip at full key = 860 + 640 = 1500: paris 1418 (1196-1575), daily 1440-1665
    ClutchIn=1900.0,      # the reference rides' clutch-in falls start at ~1970 (1640-2218, paris); here 1st gear's rpm at
                          # the speed where the clutch goes in (422 u/s, ~1 s before the game's coast stops the bike)
    ClutchFall=750.0,     # rpm/s at most, clutch in: paris -730 mean (-500..-1000), autumn -900..-1100 (900 up to
                          # test 44; the tester measured the game's at ~900)
    ClutchDecel=150.0,    # u/s^2 of slowing that counts as stopping: the game's coast is 450, its brake 2250, the
                          # demo's brake 375; the demo's coast has levelled out to < 60 by 422 u/s (judgement)
    AccelTau=0.25,        # s, the acceleration's smoothing: holds the shift schedule with 0.5-3 % speed noise a frame
    # --- gears: speed (u/s) at ShiftRpm; rpm per u/s 4.50 / 3.333 / 2.604 / 2.152
    Gears=[555.556, 750.0, 960.0, 1161.6],
                          # (666.667, 900, 1152, 1393.92 at ShiftRpm 3000 x 2500/3000, so each gear's rpm per u/s is
                          # unchanged by the lower shift point)
                          # steps 1.35 (1->2: autumn 1.35 n 10, paris 1.26-1.39), 1.28 (2->3: paris 1.25-1.32, daily
                          # 1.29-1.31), 1.21 (3->4: daily/paris 1.18-1.21); 4th at 900 u/s = 1937 rpm (the user: cruise
                          # near 1900-2050; their stretch at 117-132 s cruises at 1957)
    ShiftRpm=2500.0,      # full-throttle up-shift (3000, the pooled rides' p75-p90, put the pulls back where the user
                          # had called an earlier demo too high): the user's three daily stretches shift at median
                          # ~2290-2470, the daily ride at 2262 (p10-p90 1626-2558)
    ShiftLo=2200.0,       # steady-key up-shift: gentle up-shifts (< 300 rpm/s) median 2328, p25 2009; 2200 leaves
                          # 3rd at 900 u/s (2344) a 6.5 % margin so the cruise always reaches 4th
    DownRpm=1475.0,       # with the throttle on only: well under the cruise (4th at 900 = 1937), so a 10 % dip
                          # (1743) doesn't cross it (1750 up to test 44: a dip to 813 u/s did, 79 down-and-up pairs)
    DownHold=1.0,         # s the gear's rpm stays under DownRpm before that down-shift (0: at once, as up to test 44)
    DownHeld=1,           # 1: no down-shift with the throttle on while the plugin holds or eases its throttle for
                          # something ahead (the 'held' input; test 44: 54 of the 79 pairs came from those); 0: as
                          # up to test 44
    MinShiftGap=1.25,     # s between up-shifts: the shortest measured town gap (1.25-1.85, median 1.55, n 12); with the
                          # 2500 shift point 2nd reaches 2500 at 750 u/s
    DownGap=0.5,          # s after any shift before a down-shift (and an up-shift): without it braking made three
                          # down-shifts in 0.58 s
    ShiftCatch=0.9,       # the engine within 10 % of the up-shift point (it lags its gear by ~0.1 s pulling: 4.5 %)
    # --- the up-shift's clutch gap (measured on the model as on the ride)
    ShiftTime=0.55,       # s: paris gap 0.30 (IQR 0.30-0.40), daily fall 0.39 (0.19-0.73). The 2026-11-06a build (test 49:
                          # "gear sound should be longer on each shift"): 0.55 (0.35 before, the 2026-11-02a build's): the
                          # off family through 0.55 s of each gap, the shift points the same (3.83, 5.29, 6.55 s from rest in
                          # the harness's game), the largest frame step 0.51 dB summed (0.62 before)
    FlareTime=0.08, Flare=0.05, FlareTau=0.04,
                          # the flare: model +3.6..+4.4 % (daily median +2.9 %, p10-p90 -0.5..+10; the rides +5 %)
    ShiftFall=0.10,       # s, the rides' fall constant: model peak->engaged 0.37-0.42 s at a steady speed (daily 0.39),
                          # 0.15-0.18 s in 1->2 under the game's 300 u/s^2 (the bike keeps gaining speed in the gap)
    # --- following and loads
    RpmUp=0.10, RpmDown=0.22,   # s: idle to the slip rpm in 0.1-0.2 s (paris)
    RiseRate=2.64,        # the rpm rises at most this much in log rpm a second (4.5 % a frame at 60 fps, 78 cents): the
                          # game sets the pitch once a frame, and leaving idle stepped +187, +144, +113 c in successive
                          # frames; 860 -> 1500 now takes 0.21 s (paris: 0.1-0.2 s). Pulls (<= 1250 rpm/s at 2000 = 0.6
                          # a second) and the flare never reach it
    LoadRise=0.08, LoadFall=0.15,
    CruiseLoad=0.45, FullAccel=400.0,   # the rider's load = 0.45 + smoothed accel / 400
    # --- throttle shut
    LashDip=0.032, LashTau=0.15,   # the roll-off's quick dip: daily -2.4..-5.9 % in 0.2-0.5 s (n 5) less the slide
                                   # in that time; model -3.6..-3.9 % at 0.45 s
    CoastFall=150.0,      # rpm/s at most when coasting: paris -150 median (IQR -220..-110, 4-9 s), daily -100,
                          # autumn -120 (70 up to test 44: the daily ride's roll-offs, -44..-96)
    BrakeFall=300.0,      # rpm/s at most when braking: paris roll-off IQR edge -304; clutch-in then at 1850-1950 rpm
                          # (paris ~1970)
    # --- loops
    IdleFade=(150.0, 330.0),       # 1010 .. 1190 rpm: the idle at x1.17 .. a 1400 loop at x0.85 (crossed in
                                   # 0.05-0.2 s: launch, clutch-in fall)
    MinPitch=0.75, MaxPitch=1.25,  # safety clamps; with these bases the factors stay 0.85-1.17
    OnSplit=0.5, OffSplit=0.5,     # boundaries at the geometric means
    Hyst=0.02, XfadeTime=0.05,     # XfadeTime 0.05 s had the least hand-over cancellation of 0.017-0.10
    OnAbove=0.30, OffBelow=0.15,   # in 1st gear the raw demand counts too (a launch plays the on family from the key
                                   # press: the closed-throttle Off1400 played for the first 0.09 s), and below the
                                   # idle's fade band (both families silent) the family weight jumps
    OffHold=0.05,         # s: daily roll-offs change timbre with the throttle (centroid -27..-51 %, half the change
                          # at -0.07 s re the rpm dip's start, n 5)
    FamilyTime=0.08,      # s on/off crossfade: complete within the measured ~0.1 s
    ShiftFamily=1,        # 1 = the off family through each up-shift's gap (shifts 28-35 % darker in all rides; the
                          # daily -40 % at 0.12 s; with 0 the shift darkened -16 %, late, at 0.58 s); 0 = the family
                          # follows the rider
    # --- the heard rpm's slow wander: the family loops' pitch x (1 + w), w a slow random walk (Ornstein-Uhlenbeck, time
    # constant WanderTau, sd Wander) from a 32-bit LCG (bit-identical in C); the gearbox never sees it. Test 47, the
    # throttle hand (the tester: "it doesn't fluctuate at all ... bike engine RPM always either rises or decreases"; test
    # 46's note, 4 s windows of steady riding with the trend taken out: the real rides' rpm 0.9-2.3 %, their level
    # 0.34-0.81 dB, the game's 0.4 % and 0.16 dB): larger and slower, smoothed (WanderSmooth), the level moving with the
    # pitch (WanderLevel), only while the throttle is steady (WanderSteady). 27c (0.025, 1.5, smoothed over 0.2 s) gave,
    # the note's way (4 s windows with the trend out), the heard rpm 1.02 % and the level 0.31 dB, the autumn ride's; its
    # tester on that "about 1 %": "1% won't be really noticeable - 3-5% probably would be better". The windows take out
    # most of a swing this slow: against the cruise's own mean 27c's heard rpm already had an sd of 2.4 %, its swings
    # peaking 2.5 % off (median; IQR 1.5-3.9, p90 5.0, 1 swing in 17 past 6 %, 8.3 at most). Now (the 2026-10-31a build) the walk is
    # larger, held softly under WanderMax before the smoothing and smoothed longer: measured on this model (900 u/s in 4th
    # with the key held, 5 seeds of 392 s, against the cruise's mean; a swing's peak: an excursion's largest |deviation|, a
    # new one once past the other side by 0.5 %) the heard rpm's sd 3.1 %, its swings peaking 3.4 % off (median; IQR
    # 2.0-4.7, p90 5.35, 1 in 43 past 6 %, 6.3 at most: the hand itself never 6), a swing's rise or fall 2.1 % on each
    # side of its middle (median, between turns of 1 %; 27c 1.55) over 1.6 s (1.1); the pitch moving 6.2 cents rms in
    # 0.1 s (p99 16.6; 27c 6.8, 17.5); the level's sd 0.93 dB, its swings 1.0 dB (median; p90 1.6), 1.9 at most (27c
    # 0.71, 0.74, 1.5, 2.5); the note's windows 1.16 % and 0.35 dB, 0.30 dB per 1 %. Test 46's 0.006, 0.8 (and 0 for the
    # four since): 0.39 % in the windows, the level flat, 5.1 cents. Through a pull from rest the wander is 0
    Wander=0.055, WanderTau=1.5,   # the walk's sd before WanderMax and the smoothing (heard 3.1 %); 27c's 0.025, 1.5 (the
                                   # autumn ride's 1.02 % in the windows; the note: 0.02-0.025 with 1.5-2, unsmoothed, gives
                                   # 0.9-1.1 %); test 46's 0.006, 0.8 (the daily's cruise track 0.48-0.69 % over 2.4-5.8 s,
                                   # 0.45 % by that measure)
    WanderSeed=12345,
    WanderLevel=0.3,      # dB of level per 1 % of the wander, on the family loops (the idle's level and pitch never wander):
                          # a rise louder and more loaded, a fall lighter (the rides: autumn 0.34 dB at 1.02 %, daily 0.43
                          # at 1.41, paris 0.81 at 2.36: 0.30-0.34 dB per 1 %, the rpm's and the load's together; kept for
                          # the 2026-10-31a build: the swing larger, the ratio the rides', WanderMax holding the level within 1.8 dB);
                          # 0: the level doesn't wander (test 46)
    WanderSteady=0.25,    # s: the wander only while the throttle is steady (on, no up-shift's gap, the clutch out, over
                          # the idle's band, the rider's load under WANDER_PULL of the way from the cruise's to full, the
                          # plugin not holding the throttle); else it settles to 0 with this time constant (a pull, a
                          # let-up, a shift, the idle) and grows again from 0 by its own walk; 0: everywhere (test 46)
    WanderSmooth=0.5,     # s: the walk smoothed with this time constant before it is heard (the hand's and the engine's
                          # inertia: the bare walk moves the pitch 24 cents rms in 0.1 s, 27c's 15.6); after a let-up at
                          # 900 u/s the hand goes back at 3.9 %/s at its fastest (median of 200; 10.6 the fastest), under
                          # the coast's fall: the heard rpm never rose with the throttle shut in its gear (27c: in 2 of
                          # 200, +1.7 %/s); 27c's 0.2; 0: the bare walk (test 46)
    WanderMax=0.06,       # the walk held softly under this before the smoothing (WanderMax x tanh(walk / WanderMax)), 27c's
                          # reply: the swings' peaks rarely past 6 % where a walk of the same typical swing unheld passes
                          # 6 % in 1 swing of 9 and reaches 10 % (0.035, 1.0, 0.5: peaks 3.1 % median, p90 6.4); the
                          # family loops' pitch then within x 0.94-1.06 of the rpm's (in a steady cruise at any speed the
                          # heard loops' 0.86-1.16, inside MinPitch..MaxPitch; their gain at the 0 dB ceiling only at
                          # 2200-2600 rpm, its rise flattened); 0: unheld (27c)
    # --- test 47: a throttle-off dip at each up-shift (paris, 55 shifts: about -5.5 dB, about 0.3 s under -3 dB; the
    # game in test 46: -2.4 dB, the rpm's fall alone, a full-load pull held at the 0 dB ceiling). Measured on this model
    # (a pull from rest at the game's 300 u/s^2, 4 seeds, the level against its mean 0.25-0.05 s before the clutch-in, the
    # 0.6 s after): at the ceiling -4.0 dB at +0.07 s, 0.15 s under -3 dB; under it (the shift drawn lower) -4.7..-5.0
    # with the rpm's fall, 0.17 s; the pull's last shift, into the cruise, -6.2 (at the floor; its load falling to the
    # cruise's too); ShiftDip=0: -0.4..-2.0, none under -3 dB but that last (-3.7)
    ShiftDip=4.0,         # dB at its deepest (0: none, test 46), from the up-shift's clutch-in, after the 0 dB ceiling (so it
                          # is heard at the top of a pull), never taking the level more than DIP_FLOOR under where it was
                          # at the clutch-in
    ShiftDipTime=0.4,     # s: in over its first quarter, full depth, out over its last third (cosine ramps). The 2026-11-06a
                          # build (test 49): 0.4 (0.24 before, the 2026-11-02a build's): 0.24 s under -3 dB in 1->2 and
                          # 2->3 (0.15), the last into the cruise 0.10-0.14 s under -6 (the floor and the law's fall)
    # --- level, dB re full load at LevelRpm: LevelScale * max(IdleDb, RpmDb log2(rpm/LevelRpm) + LoadDb (load - 1))
    LevelScale=1.0,       # paris (linear): idle 11.6 dB under a pull, the throttle closing -4..-5 dB; 1.0 (test 46) is
                          # paris's own law: the idle 8.4 dB under the cruise, a full-load pull at the cruise's rpm 2.75
                          # over it (0.7 in test 45: idle -12.0 dB, on - off 3.5 dB, the pull's windows +2.1 over the
                          # cruise; 0.3 up to test 44: what the daily/autumn cameras deliver, 0.29-0.36 of paris's range)
    RpmDb=9.6, LoadDb=5.0,   # paris (linear): 9.6 dB per rpm doubling, on - off 5.0 dB
    IdleDb=-9.0,          # the floor of every state. The 2026-11-06a build (test 49: the tester kept -10, "idle could be a
                          # slightly louder"): -9, the idle at -4.0 dB, level with the cruise (a let-off at the cruise keeps
                          # its level; the start and stop sounds step 2 dB into and out of it). The 2026-11-02a build's -11
                          # (test 48: "make it louder when idle"): the idle at -6.0 dB, where the start and stop sounds' idle
                          # parts meet it (make_piece_loops.py's IDLE_LEVEL_DB), 2.5 under test 48's cruise, where paris's
                          # -17.2 (-12.2 dB, the 2026-11-01a build's) put it 8.7 under; -10 the idle at -5.0, -12 at -7.0
    LevelOffset=5.0,      # dB on every level, each loop's gain then held at 0 dB (test 46; 0 with LevelScale 0.7: test
                          # 45's levels): the cruise at -3.8 dB, full load from about 2100 rpm at the 0 dB ceiling
    LevelRpm=3000.0,      # the level law's own reference (it was ShiftRpm; moving the shift point to 2500 must not
                          # make all riding 0.76 dB louder against the idle)
    # --- test 45: the heard speed and the pulls (the module's docstring); every one off restores test 44's
    HeardSpeed=1,         # 1: the engine follows the heard speed; 0: the bike's own speed (as up to test 44)
    HeardRise=140.0,      # u/s^2 at most, the heard speed's rise (the game's own: 300; the tester: about 150)
    HeardTau=0.8,         # s: the throttle on, the heard speed follows a lower bike speed with this time constant
    HeardLead=150.0,      # u/s: in 1st the heard speed may run this far ahead of the bike's (the game's bike creeps
                          # for its first 0.5-1.5 s: the launch's rpm rises from the press all the same), only in a
                          # launch (from the clutch's last going in till the bike passes ClutchSpeed) or a real pull
                          # (the bike gaining faster than HeardRise); at a steady speed none (test 45's review: with it
                          # 1st and 2nd hunted at a steady 215-445 u/s)
    HeardPull=60.0,       # u/s: the bike this far or more ahead of the heard speed = full load
    ClutchSpeed=150.0,    # u/s: the throttle shut and the bike itself under this, the clutch goes in (the heard
                          # speed then the bike's); the throttle on, 1st
    CoastDown=1700.0,     # rpm: the throttle shut, a down-shift with a blip once the gear's rpm is under this (paris
                          # 2004, IQR 1570-2500; the game's coasts are short: it comes near the end of a long one);
                          # 0: none (the gear held to the clutch)
    Blip=0.09, BlipTime=0.30, BlipTau=0.05,
                          # paris (n 21): peak 1.27x the rpm before in 0.30 s, settling 1.16x (a 1.21-1.35 step):
                          # the blip overshoots the new gear by ~9 %, +4.8..5.2 dB, centroid +46 % (on load);
                          # Blip=0: the rpm just rises to the new gear's (autumn, no blip)
    LaunchDraw=(1250.0, 1500.0),   # rpm: each pull's slip start, drawn (paris 1250-1500, median 1380); 0,0: IdleRpm +
                                   # Launch x the key (1500, as up to test 44)
    LaunchRise=350.0,     # rpm/s the slip climbs at the heard speed's fastest rise (paris 370, IQR 250-540; daily 270,
                          # autumn 310); 0: a flat slip (as up to test 44: 1.5-2 s at 1500, then a sprint)
    LaunchFlare=0.5,      # the 2026-11-06a build (test 49: "I just want take off to be faster"): a launch press revs the
                          # slip x (1 + LaunchFlare x share), the share 1 -> 0 as a cosine over LaunchFlareTime: in the
                          # harness's game 1938 rpm and -1.1 dB at +0.5 s (1432 and -5.2 before), the up-shifts as before;
                          # 0: none (the 2026-11-02a build's); 0.3 milder, 0.6 punchier
    LaunchFlareTime=1.2,  # s, the launch rev's fade
    ShiftDraw=(2300.0, 3000.0),    # rpm: each pull's full-throttle up-shift, drawn (paris first shifts 2000-2900,
                                   # median 2370); 0,0: ShiftRpm (every pull-away identical, as up to test 44). The
                                   # 2026-11-01a build (test 47: "rpm could be slightly higher the closer it is to
                                   # shifting gear"; its 1->2 at a median 2355, 2->3 2347, 3->4 2289): 2300-3000, 1->2
                                   # and 2->3 at a median 2607 and 2596 (p10-p90 2356-2929) over 40 pulls of the
                                   # harness's game, +250 (about 10 %); 3->4 stays at 2343, all 3rd has at the top
                                   # speed; 2000,2900: the 2026-10-31a build's
    # --- the 2026-11-01a build: a stop's down-shifts (test 47: "the sound could indicate that gears are shifted down"; its
    # roll to a stop gave one blip at most, 19:40:33.106 "gear 3 at 224 u/s, 1668 rpm, heard 790 u/s, a blip", and a
    # braked stop the clutch straight from 4th, 19:41:23.609 "gear 1 at 145 u/s, 1738 rpm, heard 145 u/s (clutch in)": with
    # the throttle shut the heard speed fell only CoastFall in the gear, 70 u/s^2 in 4th, where the game's bike loses 450
    # coasting and 2250 braking, so it never got through CoastDown's bands before the clutch). With StopShift the heard
    # speed falls toward a slower bike at least HeardStop (HeardBrake braking) u/s^2, so the bands come about 0.46 s apart
    # (4->3 at about 40 km/h, 3->2 at 33, 2->1 at 26), each down-shift CoastDown's blip, StopGap apart, the clutch waiting
    # up to StopHold after the bike's ClutchSpeed for the last blip. The harness's game: let go at the cruise, blips 4->3,
    # 3->2 and 2->1 at +0.60, +1.06 and +1.53 s (1730, 1812 and 1835 rpm), the clutch at +1.83 (2134); braking, blips at
    # +0.22 and +0.62 (1790, 1631), the clutch from 2nd at +0.98; a 0.5 s let-off and a 0.15 s tap of the brake: no shift
    StopShift=1,          # 1: a stop's down-shifts each blipped (needs HeardSpeed); 0: the 2026-10-31a build's stop (the heard
                          # speed falls CoastFall, BrakeFall braking, rpm a second in the gear: a gear, then the clutch)
    HeardStop=300.0,      # u/s^2, about 4.3 m/s^2: the throttle shut StopAfter s, coasting (the game's coast 450, 6.4 m/s^2,
                          # a firm real stop)
    HeardBrake=600.0,     # u/s^2, about 8.6 m/s^2: braking, at once (the game's brake 2250): two blips, then the clutch
    StopGap=0.4,          # s between a stop's down-shifts (DownGap 0.5 for the rest): paris's blip, 0.3 s (n 21), and a pull
                          # of the lever (a judgement: the rides' down-shift spacing isn't among the numbers kept)
    StopHold=0.4,         # s the clutch may wait after the bike itself went under ClutchSpeed, for the heard speed or a
                          # running blip; a blip that would end later isn't started (0: the clutch at the bike's 150)
    StopAfter=0.3,        # s: a coast's faster fall begins only once the throttle has been shut this long, so a quick
                          # roll-off sounds as before (session 1: 12 let-offs of about 0.25 s); braking begins at once
)
EPS = 1e-4      # timer comparisons: float and double agree when a time is a whole number of frames
LAND = 1.03     # the heard speed: an up-shift lands the next gear this much over DownRpm at the bike's own speed
WANDER_PULL = 0.25   # the throttle steady (WanderSteady): the rider's load under this share of the way from the cruise to full
DIP_FLOOR = 6.0      # dB: ShiftDip takes the level at most this far under where it was at the clutch-in


class Family:
    """One family's state: the loop playing (cur), the one fading out (prev, -1 = none), the crossfade's progress."""

    def __init__(self, loops, split):
        self.loops = sorted(loops, key=lambda l: l[1])
        self.split = split
        self.cur, self.prev, self.x = 0, -1, 1.0

    def bound(self, i):
        """log rpm of the boundary between loop i and loop i + 1."""
        a, b = self.loops[i][1], self.loops[i + 1][1]
        return math.log(a) + self.split * (math.log(b) - math.log(a))

    def step(self, dt, rpm, c, down_only=False):
        """down_only: through an up-shift's gap the loop may only hand over downward (the flare doesn't
        reach for the loop above and come back 0.05 s later)."""
        lr = math.log(rpm)
        if self.x < 1.0:
            self.x = min(1.0, self.x + dt / c["XfadeTime"])
        if self.x >= 1.0:
            self.prev = -1
            n = len(self.loops)
            t = self.cur
            while not down_only and t < n - 1 and lr > self.bound(t) + c["Hyst"]:
                t += 1
            while t > 0 and lr < self.bound(t - 1) - c["Hyst"]:
                t -= 1
            if t != self.cur:
                self.prev, self.cur = self.cur, t
                self.x = min(1.0, dt / c["XfadeTime"])     # dt of this frame counts: the new loop starts audible

    def gains(self):
        """[(index, gain)] equal power."""
        if self.prev < 0:
            return [(self.cur, 1.0)]
        return [(self.cur, math.sin(self.x * math.pi / 2)), (self.prev, math.cos(self.x * math.pi / 2))]


class Engine:
    def __init__(self, loops_on, loops_off, idle, cfg=None):
        self.c = dict(DEFAULTS, **(cfg or {}))
        self.fam_on = Family(loops_on, self.c["OnSplit"])
        self.fam_off = Family(loops_off, self.c["OffSplit"]) if loops_off else None
        self.on = self.fam_on.loops
        self.off = self.fam_off.loops if self.fam_off else []
        self.idle = idle                       # (name, base rpm)
        self.gear = 0
        self.rpm = self.c["IdleRpm"]
        self.load = 0.0                        # the engine's (cut by an up-shift's gap)
        self.rload = 0.0                       # the rider's (the throttle smoothed)
        self.shift_left = 0.0                  # an up-shift's gap still to run
        self.shift_rpm0 = 0.0                  # the rpm at its clutch-in (the flare is relative to it)
        self.since_up = 9.0                    # since the last up-shift
        self.since_shift = 9.0                 # since the last shift either way
        self.speed_prev = 0.0
        self.acc_s = 0.0                       # the acceleration smoothed over AccelTau (u/s^2)
        self.coasting = False                  # throttle shut, clutch out
        self.coast_ref = 0.0                   # the rpm path a coast may fall along at most
        self.clutch = True                     # clutch in (near the stop: the engine idles)
        self.on_sel = False                    # the on-load family chosen
        self.off_timer = 0.0
        self.fam_w = 0.0                       # 0 = off load .. 1 = on load
        self.lowest = {self.on[0][0]} | ({self.off[0][0]} if self.off else set())
        self.wander = 0.0                      # the heard rpm's slow wander (a fraction)
        self.wander_raw = 0.0                  # its random walk before WanderSmooth (test 47)
        self.dip_ref = 0.0                     # the level (dB, at most 0) at the last up-shift's clutch-in (ShiftDip's floor)
        self.steady = False                    # the throttle steady this frame (WanderSteady)
        self.lcg = int(self.c["WanderSeed"]) & 0xFFFFFFFF
        self.dlcg = (int(self.c["WanderSeed"]) ^ 0x9E3779B9) & 0xFFFFFFFF   # the pulls' draws
        self.vh = 0.0                          # the heard speed (the bike's own with HeardSpeed 0)
        self.was_on = False                    # the throttle on last frame (a press draws the pull's points)
        sd, ld = self.c["ShiftDraw"], self.c["LaunchDraw"]
        self.shift_at = 0.5 * (sd[0] + sd[1]) if sd[1] > 0.0 else self.c["ShiftRpm"]    # this pull's up-shift point
        self.launch_at = (0.5 * (ld[0] + ld[1]) if ld[1] > 0.0 else self.c["IdleRpm"] + self.c["Launch"])
        self.low_t = 0.0                       # the gear's rpm under DownRpm this long, the throttle on
        self.blip_left = 0.0                   # a coast down-shift's blip still to run
        self.held = False
        self.launch = True                     # a launch: from the clutch's last going in till the bike passes ClutchSpeed
        self.shut_t = 0.0                      # StopShift: the throttle shut this long (coasting)
        self.stop_t = 0.0                      # StopShift: the bike under ClutchSpeed with the throttle shut this long
        self.flare_t = -1.0                    # the 2026-11-06a build: since the launch press (-1: none)

    def noise(self):
        """uniform in [-1, 1) from a 32-bit LCG (Numerical Recipes' constants): the C twin draws the same numbers."""
        self.lcg = (self.lcg * 1664525 + 1013904223) & 0xFFFFFFFF
        return (self.lcg >> 8) / 8388608.0 - 1.0

    def gear_k(self, g):
        """rpm per unit of speed in gear g: each gear's entry is its speed at ShiftRpm."""
        return self.c["ShiftRpm"] / self.c["Gears"][g]

    def draw(self, lo, hi):
        """lo..hi from the same LCG, its own stream (seeded WanderSeed ^ 0x9E3779B9): a pull's points don't hang on how
        many frames the wander has drawn (the C twin draws the same numbers)."""
        self.dlcg = (self.dlcg * 1664525 + 1013904223) & 0xFFFFFFFF
        return lo + (hi - lo) * ((self.dlcg >> 8) / 16777216.0)

    def step(self, dt, speed, forward, braking=False, held=False):
        """speed: measured (u/s); forward: the forward key held (0/1) or the throttle fraction; held: the plugin holds
        or eases its throttle for something ahead (the face rays, a wall, a ram's hit, the climb's boost)."""
        c = self.c
        heard = bool(c["HeardSpeed"])
        v = abs(speed)
        accel = (speed - self.speed_prev) / max(dt, 1e-4)
        self.speed_prev = speed
        self.acc_s += (accel - self.acc_s) * (1.0 - math.exp(-dt / c["AccelTau"]))
        self.held = bool(held)
        on = not braking and forward > 0.0
        if on and not self.was_on:             # a press: this pull's shift point and launch
            if c["ShiftDraw"][1] > 0.0:
                self.shift_at = self.draw(c["ShiftDraw"][0], c["ShiftDraw"][1])
            if c["LaunchDraw"][1] > 0.0:
                self.launch_at = self.draw(c["LaunchDraw"][0], c["LaunchDraw"][1])
        # the 2026-11-06a build: a press in 1st in a launch, the bike under ClutchSpeed, starts the launch rev
        if on and not self.was_on and c["LaunchFlare"] > 0.0 and self.launch and self.gear == 0 and v < c["ClutchSpeed"]:
            self.flare_t = 0.0
        elif not on:
            self.flare_t = -1.0
        elif self.flare_t >= 0.0:
            self.flare_t += dt
        self.was_on = on
        if self.blip_left > 0.0:
            self.blip_left -= dt
        self.shut_t = 0.0 if on else self.shut_t + dt
        # the heard speed: up at most HeardRise toward the bike (in 1st with the throttle on in a launch or a real pull,
        # toward it + HeardLead); the throttle on, down after a slower bike over HeardTau; shut, down CoastFall
        # (BrakeFall) rpm a second in the gear, never under the bike
        if v >= c["ClutchSpeed"]:
            self.launch = False
        lead = c["HeardLead"] if (on and self.gear == 0 and (self.launch or self.acc_s > c["HeardRise"])) else 0.0
        if heard:
            if v + lead > self.vh:
                self.vh = min(v + lead, self.vh + c["HeardRise"] * dt)
            elif on:
                self.vh += (v + lead - self.vh) * (1.0 - math.exp(-dt / c["HeardTau"]))
            else:
                fall = (c["BrakeFall"] if braking else c["CoastFall"]) / self.gear_k(self.gear)
                if c["StopShift"] and (braking or self.shut_t >= c["StopAfter"] - EPS):
                    fall = max(fall, c["HeardBrake"] if braking else c["HeardStop"])
                self.vh = max(v, self.vh - fall * dt)
        else:
            self.vh = v
        # the rider's demand: forward held and gaining speed = full; held at a steady speed = cruise; off = closed
        if not on:
            want = 0.0
        elif heard:
            want = min(1.0, c["CruiseLoad"] + (1.0 - c["CruiseLoad"]) * max(0.0, v + lead - self.vh) / c["HeardPull"]) * forward
        else:
            want = min(1.0, c["CruiseLoad"] + max(0.0, self.acc_s) / c["FullAccel"]) * forward
        lwant = 1.0 if (self.blip_left > EPS and not on) else want    # a coast down-shift's blip: the throttle opened
        tau = c["LoadRise"] if lwant > self.rload else c["LoadFall"]
        self.rload += (lwant - self.rload) * (1.0 - math.exp(-dt / tau))
        pull = min(1.0, max(0.0, (self.rload - c["CruiseLoad"]) / (1.0 - c["CruiseLoad"])))
        self.since_up += dt
        self.since_shift += dt
        if self.shift_left > 0.0:
            self.shift_left -= dt
        in_shift = self.shift_left > EPS
        eng_want = 0.0 if in_shift else lwant
        tau = c["LoadRise"] if eng_want > self.load else c["LoadFall"]
        self.load += (eng_want - self.load) * (1.0 - math.exp(-dt / tau))
        throttle = want > 0.0
        top = len(c["Gears"]) - 1
        k0 = self.gear_k(0)
        if heard:
            self.stop_t = self.stop_t + dt if (not throttle and v < c["ClutchSpeed"]) else 0.0
            bike_in = v < c["ClutchSpeed"] and (not c["StopShift"] or self.stop_t >= c["StopHold"] - EPS
                                                 or self.vh < c["ClutchSpeed"])
            self.clutch = (not throttle) and (bike_in or (self.gear == 0 and self.vh * k0 < c["ClutchIn"]))
            if c["StopShift"] and self.clutch and self.blip_left > EPS:
                self.clutch = False            # a stop's down-shift: its blip ends before the clutch goes in
            if self.clutch:
                self.vh = v
                self.launch = True
            elif throttle and v < c["ClutchSpeed"] and self.gear > 0:
                self.gear = 0                  # a launch (or a wall): 1st, the heard speed within 1st's reach
                self.shift_left = 0.0
                in_shift = False
                self.vh = min(self.vh, v + c["HeardLead"])
                self.launch = True
        else:
            self.clutch = (not throttle) and v * k0 < c["ClutchIn"] and (
                braking or self.acc_s < -c["ClutchDecel"] or v * k0 < c["IdleRpm"] + c["Launch"])
        if self.clutch or throttle:
            self.blip_left = 0.0
        vs = self.vh
        # the clutch's slip in 1st: from the pull's start, climbing LaunchRise at the heard speed's fastest rise
        slip = (c["IdleRpm"] + (self.launch_at - c["IdleRpm"]) * min(1.0, forward)
                + c["LaunchRise"] * vs / c["HeardRise"])
        # the gear
        if self.clutch:
            self.gear = 0
            self.shift_left = 0.0
            in_shift = False
            self.low_t = 0.0
        elif not in_shift:
            k = self.gear_k(self.gear)
            vg = vs
            if throttle and self.gear == 0 and slip > vs * k:
                vg = slip / k                  # 1st's rpm is the slip's
            if throttle:
                up_at = c["ShiftLo"] + (self.shift_at - c["ShiftLo"]) * pull
                if (self.gear < top and vg * k > up_at and self.rpm > c["ShiftCatch"] * up_at
                        and vg * self.gear_k(self.gear + 1) > c["DownRpm"] and self.since_up >= c["MinShiftGap"] - EPS
                        and self.since_shift >= c["DownGap"] - EPS
                        and (not heard or self.acc_s > c["HeardRise"]       # the bike's own speed too, but in a real pull
                             or v * self.gear_k(self.gear + 1) > c["DownRpm"] * LAND)):
                    if heard:
                        self.vh = vs = max(vs, vg)   # out of a slip: the heard speed is 1st's at the slip's rpm
                    self.dip_ref = min(0.0, self.level_db())   # where ShiftDip starts from (its floor DIP_FLOOR under)
                    self.gear += 1
                    self.shift_left = c["ShiftTime"]
                    self.shift_rpm0 = self.rpm
                    in_shift = True
                    self.since_up = 0.0
                    self.since_shift = 0.0
                    self.low_t = 0.0
                else:
                    low = self.gear > 0 and vg * k < c["DownRpm"]
                    self.low_t = self.low_t + dt if low else 0.0
                    if (low and self.low_t >= c["DownHold"] - EPS and not (c["DownHeld"] and self.held)
                            and vs * self.gear_k(self.gear - 1) < c["ShiftLo"] and self.since_shift >= c["DownGap"] - EPS):
                        self.gear -= 1
                        self.since_shift = 0.0
                        self.low_t = 0.0
            else:
                self.low_t = 0.0
                if heard:
                    if (c["CoastDown"] > 0.0 and self.gear > 0 and vs * k < c["CoastDown"]
                            and self.since_shift >= (c["StopGap"] if c["StopShift"] else c["DownGap"]) - EPS
                            and not (c["StopShift"] and v < c["ClutchSpeed"]
                                     and self.stop_t + c["BlipTime"] > c["StopHold"] + EPS)):
                        self.gear -= 1             # a down-shift with a blip
                        self.since_shift = 0.0
                        self.blip_left = c["BlipTime"]
                elif (self.gear > 0 and self.rpm * self.rpm > v * v * k * self.gear_k(self.gear - 1)
                      and self.since_shift >= c["DownGap"] - EPS):
                    # coasting: to the gear whose rpm is nearer the engine's (silent: the rpm doesn't rise when shut)
                    self.gear -= 1
                    self.since_shift = 0.0
        # the rpm
        rg = vs * self.gear_k(self.gear)
        idle = c["IdleRpm"]
        if self.clutch:
            target, tau = idle, c["RpmDown"]
            self.coasting = False
        elif in_shift:
            if c["ShiftTime"] - self.shift_left < c["FlareTime"]:
                target, tau = self.shift_rpm0 * (1.0 + c["Flare"]), c["FlareTau"]
            else:
                target, tau = max(rg, idle), c["ShiftFall"]
            self.coasting = False
        elif throttle:
            target = max(rg, idle)
            if self.gear == 0:
                sf = slip
                T = c["LaunchFlareTime"]
                if c["LaunchFlare"] > 0.0 and 0.0 <= self.flare_t < T:    # the launch rev on the slip (2026-11-06a)
                    sf = slip * (1.0 + c["LaunchFlare"] * (0.5 + 0.5 * math.cos(math.pi * self.flare_t / T)))
                target = max(target, sf)       # the clutch slips until 1st takes over
            tau = c["RpmUp"] if target > self.rpm else c["RpmDown"]
            self.coasting = False
        elif heard:
            if self.blip_left > EPS:
                target, tau = max(rg * (1.0 + c["Blip"]), idle), c["BlipTau"]
            else:
                target, tau = max(rg * (1.0 - c["LashDip"]), idle), c["LashTau"]
                if target > self.rpm:
                    target = self.rpm
            self.coasting = True
        else:
            if not self.coasting:
                self.coast_ref = self.rpm * (1.0 - c["LashDip"])
                self.coasting = True
            self.coast_ref -= (c["BrakeFall"] if braking else c["CoastFall"]) * dt
            target = max(self.coast_ref, rg * (1.0 - c["LashDip"]), idle)
            if target > self.rpm:
                target = self.rpm
            tau = c["LashTau"]
        new = self.rpm + (target - self.rpm) * (1.0 - math.exp(-dt / tau))
        if self.clutch and new < self.rpm - c["ClutchFall"] * dt:
            new = self.rpm - c["ClutchFall"] * dt
        top_rpm = self.rpm * math.exp(c["RiseRate"] * dt)
        if new > top_rpm:
            new = top_rpm
        self.rpm = new
        # the heard rpm's wander: dw = -w dt / tau + sd sqrt(2 dt / tau) n, n of unit variance (uniform x sqrt 3); with
        # WanderSteady (test 47) only while the throttle is steady, else settling to 0 (the number drawn all the same)
        n = self.noise()
        steady = (on and not in_shift and not self.clutch and not self.held and pull < WANDER_PULL
                  and self.rpm > c["IdleRpm"] + c["IdleFade"][1])
        if c["WanderSteady"] > 0.0 and not steady:
            self.wander_raw -= self.wander_raw * (1.0 - math.exp(-dt / c["WanderSteady"]))
        else:
            self.wander_raw += (-self.wander_raw * dt / c["WanderTau"]
                                + c["Wander"] * math.sqrt(2.0 * dt / c["WanderTau"]) * 1.7320508 * n)
        lim = c["WanderMax"]                   # the 2026-10-31a build: the walk held softly under WanderMax before the smoothing
        heard = lim * math.tanh(self.wander_raw / lim) if lim > 0.0 else self.wander_raw
        if c["WanderSmooth"] > 0.0:            # test 47: the hand smooth (the engine's inertia), no frame-to-frame jitter
            self.wander += (heard - self.wander) * (1.0 - math.exp(-dt / c["WanderSmooth"]))
        else:
            self.wander = heard
        self.steady = steady
        # the family: on load once the rider's load is over OnAbove; off load once the rider's demand (the throttle,
        # unsmoothed) has stayed under OffBelow for OffHold s
        if self.on_sel:
            self.off_timer = self.off_timer + dt if lwant < c["OffBelow"] else 0.0
            if self.off_timer >= c["OffHold"] - EPS:
                self.on_sel, self.off_timer = False, 0.0
        elif self.rload > c["OnAbove"] or (self.gear == 0 and lwant > c["OnAbove"]):
            self.on_sel = True
        fam_on = self.on_sel and not (c["ShiftFamily"] and in_shift)
        d = dt / c["FamilyTime"]
        if self.rpm <= c["IdleRpm"] + c["IdleFade"][0]:
            self.fam_w = 1.0 if fam_on else 0.0            # both families silent: no crossfade to wait for
        else:
            self.fam_w = min(1.0, self.fam_w + d) if fam_on else max(0.0, self.fam_w - d)
        self.in_shift = in_shift
        # each family's loop
        self.fam_on.step(dt, self.rpm, c, in_shift)
        if self.fam_off:
            self.fam_off.step(dt, self.rpm, c, in_shift)
        return self.mix()

    def level_db(self):
        """The overall level in dB re full load at LevelRpm."""
        c = self.c
        db = c["RpmDb"] * math.log2(self.rpm / c["LevelRpm"]) + c["LoadDb"] * (min(1.0, self.rload) - 1.0)
        return c["LevelScale"] * max(c["IdleDb"], db) + c["LevelOffset"]

    def idle_level(self):
        """The level the idle plays at (gain): the one-shots' idle parts are matched to it."""
        return min(1.0, 10 ** ((self.c["LevelScale"] * self.c["IdleDb"] + self.c["LevelOffset"]) / 20))

    def mix(self):
        """{loop name: (gain 0..1, pitch ratio)}."""
        c = self.c
        lo, hi = math.log(c["IdleRpm"] + c["IdleFade"][0]), math.log(c["IdleRpm"] + c["IdleFade"][1])
        f = min(1.0, max(0.0, (math.log(self.rpm) - lo) / (hi - lo)))
        w_idle, w_run = math.cos(f * math.pi / 2), math.sin(f * math.pi / 2)
        if self.fam_off:
            w_on, w_off = math.sin(self.fam_w * math.pi / 2), math.cos(self.fam_w * math.pi / 2)
        else:
            w_on, w_off = 1.0, 0.0
        p2 = {self.idle[0]: w_idle * w_idle}           # gains add in power (a loop in both families is one voice)
        base = {self.idle[0]: self.idle[1]}
        for fam, w in ((self.fam_on, w_on), (self.fam_off, w_off)):
            if fam is None:
                continue
            for i, g in fam.gains():
                n, b = fam.loops[i]
                base[n] = b
                p2[n] = p2.get(n, 0.0) + (w_run * w * g) ** 2
        level = 10 ** (self.heard_db() / 20)   # 0 dB at most (test 46), before the crossfades: equal power through them
        hand = 10 ** (c["WanderLevel"] * 100.0 * self.wander / 20) if c["WanderLevel"] else 1.0   # test 47: the wander's level
        in_band = self.rpm < c["IdleRpm"] + c["IdleFade"][1]
        out = {}
        for n, q in p2.items():
            p = self.rpm / base[n]
            g = level
            if n != self.idle[0]:
                p *= 1.0 + self.wander
                g *= hand
            if not (in_band and (n == self.idle[0] or n in self.lowest)):
                p = min(c["MaxPitch"], max(c["MinPitch"], p))
            out[n] = (min(1.0, math.sqrt(q) * g), p)   # (q is 1 at most: the level's ceiling holds each loop's)
        return out

    def dip_shape(self):
        """ShiftDip's share now, 0..1: from the last up-shift's clutch-in, in over ShiftDipTime's first quarter, out over
        its last third (cosine ramps), full between."""
        T, t = self.c["ShiftDipTime"], self.since_up
        if T <= 0.0 or t <= 0.0 or t >= T:
            return 0.0
        a, r = 0.25 * T, T / 3.0
        if t < a:
            return 0.5 - 0.5 * math.cos(math.pi * t / a)
        if t > T - r:
            return 0.5 + 0.5 * math.cos(math.pi * (t - (T - r)) / r)
        return 1.0

    def heard_db(self):
        """The level law held at 0 dB, less an up-shift's throttle-off dip (ShiftDip, test 47), at most DIP_FLOOR under
        the level at its clutch-in (never under that, unless the law itself is)."""
        db = min(0.0, self.level_db())
        dip = self.c["ShiftDip"] * self.dip_shape() if self.c["ShiftDip"] > 0.0 else 0.0
        if dip > 0.0:
            floor = self.dip_ref - DIP_FLOOR
            db = db - dip if db - dip >= floor else min(db, floor)
        return db


# --- The off values' check: each build's off values give that build's model, frame for frame, over the demo ride, a
# random ride in the harness's game and five stops. The expected files hold those builds' frames, written from their own
# engine_model.py (by --write-expected) as hashes of 500 frames each:
#   - 2026-10-31a (the 2026-11-01a build's StopShift and ShiftDraw off): StopShift=0 with ShiftDraw (2000, 2900), and
#     IdleDb -17.2 (the 2026-11-02a build's), 0c3df02's model, check_off_2026-10-31a.txt (its hashes as written with 0c3df02's
#     own -17.2; only its header's JSON is newer);
#   - 2026-11-01a (the 2026-11-02a build's IdleDb off): IdleDb -17.2, 993f582's model, check_off_2026-11-01a.txt;
#   - 2026-11-02a (the 2026-11-06a build's four off): IdleDb -11, ShiftTime 0.35, ShiftDipTime 0.24, LaunchFlare 0,
#     f0253e8's model, check_off_2026-11-02a.txt.
# Each build's set carries the later builds' off values too (0c3df02's and 993f582's ShiftTime and ShiftDipTime were 0.35 and
# 0.24 and they had no LaunchFlare; their models take unknown keys), so the older files' hashes stand; only their headers'
# JSON is newer.
OFF_31A = {"StopShift": 0, "ShiftDraw": [2000.0, 2900.0], "IdleDb": -17.2, "ShiftTime": 0.35, "ShiftDipTime": 0.24, "LaunchFlare": 0.0}
OFF_01A = {"IdleDb": -17.2, "ShiftTime": 0.35, "ShiftDipTime": 0.24, "LaunchFlare": 0.0}
OFF_02A = {"IdleDb": -11.0, "ShiftTime": 0.35, "ShiftDipTime": 0.24, "LaunchFlare": 0.0}
OFF_BUILDS = {   # --off NAME: (the off values, the expected file here, the build, the commit its model is from)
    "31a": (OFF_31A, "check_off_2026-10-31a.txt", "2026-10-31a", "0c3df02"),
    "01a": (OFF_01A, "check_off_2026-11-01a.txt", "2026-11-01a", "993f582"),
    "02a": (OFF_02A, "check_off_2026-11-02a.txt", "2026-11-02a", "f0253e8"),
}
CHECK_ON = [("On1400", 1400.0), ("On1700", 1700.0), ("On2000", 2000.0), ("On2400", 2400.0), ("On2800", 2800.0), ("On3300", 3300.0)]
CHECK_OFF = [("Off1400", 1400.0), ("Off1800", 1800.0), ("Off2300", 2300.0), ("Off2800", 2800.0)]
CHECK_IDLE = ("Idle", 860.0)
CHECK_BLOCK = 500
CHECK_STOPS = {   # the harness's game: (seconds, key) with W forward, S back (braking), - nothing
    "coast": [(12, "W"), (5, "-")],
    "brake": [(12, "W"), (0.6, "S"), (4.4, "-")],
    "letoff": [(12, "W"), (0.5, "-"), (6, "W"), (0.3, "-"), (6, "W")],
    "brake_tap": [(12, "W"), (0.15, "S"), (6, "W")],
    "coast_brake": [(12, "W"), (0.7, "-"), (0.5, "S"), (3.8, "-")],
}


def _demo_ride():
    """The demo ride (render.py's, 31 s at 60 fps): (dt, speed, forward, braking) a frame."""
    out = []
    for f in range(31 * 60):
        t = f / 60.0
        if t < 6.0:
            v, fwd, brk = 0.0, 0.0, False
        elif t < 16.0:
            v, fwd, brk = 900.0 * min(1.0, max(0.0, (t - 6.15) / 3.2)) ** 1.15, 1.0, False
        elif t < 19.0:
            v, fwd, brk = 350.0 + 550.0 * math.exp(-(t - 16.0) / 1.2), 0.0, False
        elif t < 22.0:
            v0 = 350.0 + 550.0 * math.exp(-3.0 / 1.2)
            v, fwd, brk = v0 + (900.0 - v0) * min(1.0, (t - 19.0) / 2.6) ** 1.1, 1.0, False
        elif t < 25.0:
            v, fwd, brk = max(0.0, 900.0 * (1.0 - (t - 22.0) / 2.4)), 0.0, True
        else:
            v, fwd, brk = 0.0, 0.0, False
        out.append((1.0 / 60.0, v, fwd, brk))
    return out


def _game_ride(script, dt=0.006):
    """The harness's game (fake_game.c's g_gameCurve): the plugin's throttle from a tenth, +dt/3 on W, at most Lead 0.2 over
    the measured speed, -dt/2 off the key, -dt/0.4 braking; the bike 900 x it; the speed the plugin reads lags it by 0.2 s."""
    out, T, vp = [], 0.0, 0.0
    for dur, key in script:
        for _ in range(int(round(dur / dt))):
            fwd, brk = key == "W", key == "S"
            if fwd:
                T = min(max(T, 0.1) + dt / 3.0, vp / 900.0 + 0.2, 1.0)
            elif brk:
                T = max(0.0, T - dt / 0.4)
            else:
                T = max(0.0, T - dt / 2.0)
            vp += (900.0 * T - vp) * (1.0 - math.exp(-dt / 0.2))
            out.append((dt, vp, 1.0 if fwd else 0.0, brk and vp > 10.0))
    return out


def check_rides():
    """{name: [(dt, speed, forward, braking)]}: the demo ride, a random ride (60 segments of 0.1-6 s, W three times in five,
    seed 7) and the five stops, the last six in the harness's game."""
    import random
    rnd = random.Random(7)
    script = [(rnd.uniform(0.1, 6), rnd.choice("WWW-S")) for _ in range(60)]
    rides = {"demo": _demo_ride(), "random": _game_ride(script)}
    rides.update({name: _game_ride(s) for name, s in CHECK_STOPS.items()})
    return rides


def check_frames(engine_cls, cfg, ride):
    """Each frame of the ride as text (the gear, rpm, clutch, heard level, every loop's gain and pitch, exactly), and the
    gear changes [(frame, from, to, rpm, blip, clutch)]."""
    e = engine_cls(CHECK_ON, CHECK_OFF, CHECK_IDLE, cfg)
    frames, changes, gear = [], [], e.gear
    for i, (dt, v, fwd, brk) in enumerate(ride):
        rpm0 = e.rpm
        mix = e.step(dt, v, fwd, brk, False)
        frames.append("%d %r %d %r %s" % (e.gear, e.rpm, e.clutch, e.heard_db(),
                                          " ".join("%s:%r,%r" % (n, g, p) for n, (g, p) in sorted(mix.items()))))
        if e.gear != gear:
            changes.append((i, gear + 1, e.gear + 1, round(rpm0), e.blip_left > EPS, bool(e.clutch)))
        gear = e.gear
    return frames, changes


def _blocks(frames):
    import hashlib
    return [hashlib.sha256("\n".join(frames[i:i + CHECK_BLOCK]).encode()).hexdigest()[:16] for i in range(0, len(frames), CHECK_BLOCK)]


def _load_model(path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("engine_model_other", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Engine


def _off_words(off):
    """The off values as the check's line says them: "StopShift=0, ShiftDraw=2000,2900, IdleDb=-17.2"."""
    return ", ".join("%s=%s" % (k, ",".join("%g" % x for x in v) if isinstance(v, (list, tuple)) else "%g" % v) for k, v in off.items())


def write_expected(model_path, out_path, build="31a"):
    """The expected file from another model (that build's own engine_model.py: 0c3df02's for 31a, 993f582's for 01a, f0253e8's for 02a), run with
    that build's off values."""
    off, _, name, commit = OFF_BUILDS[build]
    engine_cls = _load_model(model_path)
    lines = ["# engine_model.py --check-off: the %s build's model (%s's tools/sound/engine_model.py) over these rides," % (name, commit),
             "# run with %s; each frame as check_frames() writes it, %d frames a hash (sha256's first 16)." % (json.dumps(off), CHECK_BLOCK)]
    for rname, ride in check_rides().items():
        frames, changes = check_frames(engine_cls, off, ride)
        lines.append("ride %s frames %d changes %d" % (rname, len(frames), len(changes)))
        lines.append("blocks %s %s" % (rname, " ".join(_blocks(frames))))
        for c in changes:
            lines.append("change %s %d %d->%d %d%s%s" % (rname, c[0], c[1], c[2], c[3], " blip" if c[4] else "", " clutch" if c[5] else ""))
    with open(out_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return 0


def check_off(path=None, against=None, build=None):
    """0 if each build's off values give that build's model's frames on every ride: against its expected file (block hashes,
    the gear changes) or, with against, another model file frame by frame. build None: every build (each with its own file;
    with against or path, 31a as before)."""
    if build is None and (against or path):
        build = "31a"
    if build is None:
        return 1 if any([check_off(None, None, b) for b in OFF_BUILDS]) else 0
    off, file_name, name, _ = OFF_BUILDS[build]
    words = "%s against the %s build's model" % (_off_words(off), name)
    bad = 0
    if against:
        other = _load_model(against)
        for rname, ride in check_rides().items():
            a, _ = check_frames(Engine, off, ride)
            b, _ = check_frames(other, off, ride)
            diff = sum(1 for x, y in zip(a, b) if x != y) + abs(len(a) - len(b))
            print("%s: %d frames, %d differing" % (rname, len(a), diff))
            bad += diff
        print("check-off against %s: %s (%s)" % (against, "the same, frame for frame" if not bad else "%d frames differ" % bad, _off_words(off)))
        return 1 if bad else 0
    want, changes = {}, {}
    with open(path or os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)) as fh:
        for ln in fh:
            w = ln.split()
            if not w or w[0].startswith("#"):
                continue
            if w[0] == "ride":
                want[w[1]] = {"frames": int(w[3])}
                changes[w[1]] = []
            elif w[0] == "blocks":
                want[w[1]]["blocks"] = w[2:]
            elif w[0] == "change":
                changes[w[1]].append(" ".join(w[2:]))
    total = 0
    for rname, ride in check_rides().items():
        frames, ch = check_frames(Engine, off, ride)
        got = _blocks(frames)
        exp = want.get(rname, {"frames": -1, "blocks": []})
        nb = sum(1 for x, y in zip(got, exp["blocks"]) if x != y) + abs(len(got) - len(exp["blocks"]))
        mine = ["%d %d->%d %d%s%s" % (c[0], c[1], c[2], c[3], " blip" if c[4] else "", " clutch" if c[5] else "") for c in ch]
        same = mine == changes.get(rname)
        total += len(frames)
        print("%s %s: %d frames (%d expected), %d of %d blocks of %d differing, %d gear changes %s" % (
            name, rname, len(frames), exp["frames"], nb, len(exp["blocks"]), CHECK_BLOCK, len(ch), "as expected" if same else "NOT as expected"))
        bad += nb + (len(frames) != exp["frames"]) + (not same)
    print("check-off: %s over %d frames (%s)" % ("the same, frame for frame" if not bad else "DIFFERENT", total, words))
    return 1 if bad else 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="The engine model (the plugin's C twin follows it). --check-off: each build's off values "
                                 "against that build's frames (2026-10-31a: StopShift=0, ShiftDraw 2000,2900, IdleDb -17.2; "
                                 "2026-11-01a: IdleDb -17.2; 2026-11-02a: IdleDb -11, ShiftTime 0.35, ShiftDipTime 0.24, "
                                 "LaunchFlare 0; the older two with the later builds' off values too).")
    ap.add_argument("--check-off", action="store_true", help="the off values against check_off_2026-10-31a.txt, check_off_2026-11-01a.txt and check_off_2026-11-02a.txt "
                    "(exit 1 if any frame differs); --off NAME: only that build's")
    ap.add_argument("--off", choices=sorted(OFF_BUILDS), help="the build: 31a (0c3df02's model), 01a (993f582's) or 02a (f0253e8's); with --write-expected "
                    "31a by default")
    ap.add_argument("--against", metavar="MODEL", help="with --check-off: compare frame by frame with another engine_model.py instead "
                    "(the --off build's values, 31a by default)")
    ap.add_argument("--expected", metavar="FILE", help="with --check-off: the expected file (default: the --off build's file here)")
    ap.add_argument("--write-expected", metavar="MODEL", help="write the --off build's expected file from that build's engine_model.py "
                    "(0c3df02's for 31a, 993f582's for 01a, f0253e8's for 02a)")
    ap.add_argument("--out", metavar="FILE", help="with --write-expected: where (default: the --off build's file here)")
    a = ap.parse_args()
    if a.write_expected:
        b = a.off or "31a"
        here = os.path.join(os.path.dirname(os.path.abspath(__file__)), OFF_BUILDS[b][1])
        sys.exit(write_expected(a.write_expected, a.out or here, b))
    if a.check_off:
        sys.exit(check_off(a.expected, a.against, a.off))
    ap.print_help()
