"""The engine's rpm and each loop's pitch and level from the bike's speed and throttle.

This is the reference the plugin's C port follows (tools/f4se-slope: the same constants, the same order of operations,
one call per frame). Speeds are game units per second (900 u/s = the bike's top speed, about 46 km/h).

The constants are calibrated to an Iron 883 on the road (the reference rides: "daily", the ride the user pointed to as
the right sound, whose three example stretches ride at median 1800-2060 rpm; "autumn" and "paris", two more; measured
only, nothing of them is in a loop). Every constant's measured basis is in the comments on DEFAULTS below. Revised
after measuring this model's first demo against the reference: the full-throttle up-shift at 2500 rpm with the gears scaled by 2500/3000 (each gear's rpm per
u/s unchanged), MinShiftGap 1.25 s, the level law's own reference LevelRpm 3000, ShiftFamily 1; the rpm rises at most
RiseRate in log rpm a second (the per-frame pitch step leaving idle); in 1st gear the raw demand switches the on family
and below the idle's fade band the family weight jumps (no closed-throttle loop at a launch); a slow random wander of
the family loops' pitch (Wander, WanderTau; an LCG the C twin reproduces).

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
  LevelScale * max(IdleDb, RpmDb * log2(rpm / LevelRpm) + LoadDb * (rider load - 1)).
LevelScale 0.3 is what the daily and autumn cameras deliver (0.29-0.36 of paris's range): idle -5.2 dB, full load
at 3000 rpm 0 dB."""
import math

DEFAULTS = dict(
    # --- the engine at rest and pulling away
    IdleRpm=860.0,        # the user's choice: demodave's idle loop (the one called perfect) fires every 140.7 ms
                          # = 853 rpm; the reference rides' warm idle is 922-1060 (980 suggested), not used
    Launch=640.0,         # clutch slip at full key = 860 + 640 = 1500: paris 1418 (1196-1575), daily 1440-1665
    ClutchIn=1900.0,      # the reference rides' clutch-in falls start at ~1970 (1640-2218, paris); here 1st gear's rpm at
                          # the speed where the clutch goes in (422 u/s, ~1 s before the game's coast stops the bike)
    ClutchFall=900.0,     # rpm/s at most, clutch in: paris -730 mean (-500..-1000), autumn -900..-1100
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
    DownRpm=1750.0,       # paris down-shifts start 2004 (IQR 1570-2500); with the throttle on only
    MinShiftGap=1.25,     # s between up-shifts: the shortest measured town gap (1.25-1.85, median 1.55, n 12); with the
                          # 2500 shift point 2nd reaches 2500 at 750 u/s
    DownGap=0.5,          # s after any shift before a down-shift (and an up-shift): without it braking made three
                          # down-shifts in 0.58 s
    ShiftCatch=0.9,       # the engine within 10 % of the up-shift point (it lags its gear by ~0.1 s pulling: 4.5 %)
    # --- the up-shift's clutch gap (measured on the model as on the ride)
    ShiftTime=0.35,       # s: paris gap 0.30 (IQR 0.30-0.40), daily fall 0.39 (0.19-0.73)
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
    CoastFall=70.0,       # rpm/s at most when coasting: daily roll-offs -44..-96 (median -70); model -66..-83
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
    # constant WanderTau, sd Wander) from a 32-bit LCG (bit-identical in C); the gearbox never sees it
    Wander=0.006, WanderTau=0.8,   # without it the cruise was dead flat (0.027 %); the daily's cruise track wanders
                                   # 0.48-0.69 % over 2.4-5.8 s and 0.29-0.36 % around a 2 s moving mean; these give
                                   # 0.45 % and 0.32 % measured the same way (39 seeds); autumn 0.41-0.73 %
    WanderSeed=12345,
    # --- level, dB re full load at LevelRpm: LevelScale * max(IdleDb, RpmDb log2(rpm/LevelRpm) + LoadDb (load - 1))
    LevelScale=0.3,       # the daily/autumn cameras deliver 0.29-0.36 of paris's range; idle -> full +5.2 dB
    RpmDb=9.6, LoadDb=5.0, IdleDb=-17.2,   # paris (linear): 9.6 dB per rpm doubling, on - off 5.0 dB, idle -17.2
    LevelRpm=3000.0,      # the level law's own reference (it was ShiftRpm; moving the shift point to 2500 must not
                          # make all riding 0.76 dB louder against the idle)
)
EPS = 1e-4      # timer comparisons: float and double agree when a time is a whole number of frames


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
        self.lcg = int(self.c["WanderSeed"]) & 0xFFFFFFFF

    def noise(self):
        """uniform in [-1, 1) from a 32-bit LCG (Numerical Recipes' constants): the C twin draws the same numbers."""
        self.lcg = (self.lcg * 1664525 + 1013904223) & 0xFFFFFFFF
        return (self.lcg >> 8) / 8388608.0 - 1.0

    def gear_k(self, g):
        """rpm per unit of speed in gear g: each gear's entry is its speed at ShiftRpm."""
        return self.c["ShiftRpm"] / self.c["Gears"][g]

    def step(self, dt, speed, forward, braking=False):
        """speed: measured (u/s); forward: the forward key held (0/1) or the throttle fraction."""
        c = self.c
        v = abs(speed)
        accel = (speed - self.speed_prev) / max(dt, 1e-4)
        self.speed_prev = speed
        self.acc_s += (accel - self.acc_s) * (1.0 - math.exp(-dt / c["AccelTau"]))
        # the rider's demand: forward held and gaining speed = full; held at a steady speed = cruise; off = closed
        if braking or forward <= 0.0:
            want = 0.0
        else:
            want = min(1.0, c["CruiseLoad"] + max(0.0, self.acc_s) / c["FullAccel"]) * forward
        tau = c["LoadRise"] if want > self.rload else c["LoadFall"]
        self.rload += (want - self.rload) * (1.0 - math.exp(-dt / tau))
        pull = min(1.0, max(0.0, (self.rload - c["CruiseLoad"]) / (1.0 - c["CruiseLoad"])))
        self.since_up += dt
        self.since_shift += dt
        if self.shift_left > 0.0:
            self.shift_left -= dt
        in_shift = self.shift_left > EPS
        eng_want = 0.0 if in_shift else want
        tau = c["LoadRise"] if eng_want > self.load else c["LoadFall"]
        self.load += (eng_want - self.load) * (1.0 - math.exp(-dt / tau))
        throttle = want > 0.0
        top = len(c["Gears"]) - 1
        k0 = self.gear_k(0)
        self.clutch = (not throttle) and v * k0 < c["ClutchIn"] and (
            braking or self.acc_s < -c["ClutchDecel"] or v * k0 < c["IdleRpm"] + c["Launch"])
        # the gear
        if self.clutch:
            self.gear = 0
            self.shift_left = 0.0
            in_shift = False
        elif not in_shift:
            k = self.gear_k(self.gear)
            if throttle:
                up_at = c["ShiftLo"] + (c["ShiftRpm"] - c["ShiftLo"]) * pull
                if (self.gear < top and v * k > up_at and self.rpm > c["ShiftCatch"] * up_at
                        and v * self.gear_k(self.gear + 1) > c["DownRpm"] and self.since_up >= c["MinShiftGap"] - EPS
                        and self.since_shift >= c["DownGap"] - EPS):
                    self.gear += 1
                    self.shift_left = c["ShiftTime"]
                    self.shift_rpm0 = self.rpm
                    in_shift = True
                    self.since_up = 0.0
                    self.since_shift = 0.0
                elif (self.gear > 0 and v * k < c["DownRpm"] and v * self.gear_k(self.gear - 1) < c["ShiftLo"]
                      and self.since_shift >= c["DownGap"] - EPS):
                    self.gear -= 1
                    self.since_shift = 0.0
            elif (self.gear > 0 and self.rpm * self.rpm > v * v * k * self.gear_k(self.gear - 1)
                  and self.since_shift >= c["DownGap"] - EPS):
                # coasting: to the gear whose rpm is nearer the engine's (silent: the rpm doesn't rise when shut)
                self.gear -= 1
                self.since_shift = 0.0
        # the rpm
        rg = v * self.gear_k(self.gear)
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
                target = max(target, idle + c["Launch"] * min(1.0, forward))    # the clutch slips until 1st takes over
            tau = c["RpmUp"] if target > self.rpm else c["RpmDown"]
            self.coasting = False
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
        # the heard rpm's wander: dw = -w dt / tau + sd sqrt(2 dt / tau) n, n of unit variance (uniform x sqrt 3)
        self.wander += (-self.wander * dt / c["WanderTau"]
                        + c["Wander"] * math.sqrt(2.0 * dt / c["WanderTau"]) * 1.7320508 * self.noise())
        # the family: on load once the rider's load is over OnAbove; off load once the rider's demand (the throttle,
        # unsmoothed) has stayed under OffBelow for OffHold s
        if self.on_sel:
            self.off_timer = self.off_timer + dt if want < c["OffBelow"] else 0.0
            if self.off_timer >= c["OffHold"] - EPS:
                self.on_sel, self.off_timer = False, 0.0
        elif self.rload > c["OnAbove"] or (self.gear == 0 and want > c["OnAbove"]):
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
        return c["LevelScale"] * max(c["IdleDb"], db)

    def idle_level(self):
        """The level the idle plays at (gain): the one-shots' idle parts are matched to it."""
        return 10 ** (self.c["LevelScale"] * self.c["IdleDb"] / 20)

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
        level = 10 ** (self.level_db() / 20)
        in_band = self.rpm < c["IdleRpm"] + c["IdleFade"][1]
        out = {}
        for n, q in p2.items():
            p = self.rpm / base[n]
            if n != self.idle[0]:
                p *= 1.0 + self.wander
            if not (in_band and (n == self.idle[0] or n in self.lowest)):
                p = min(c["MaxPitch"], max(c["MinPitch"], p))
            out[n] = (math.sqrt(q) * level, p)
        return out
