Scriptname CMB_RamScript extends Quest
{Commonwealth Motorbike: hostile actors the bike hits at speed are knocked over and take a
little damage (test 40's wish). Needs F4SE and CMB_Slope.dll, whose rays see what is ahead:
the plugin asks about an actor it sees (CMB_RamSeenHi/Lo, its form id's two halves, then
CMB_RamSeen, the ask's number), this script answers in CMB_RamOk (the number: yes; minus the
number: no), and the plugin keeps the throttle open only for a yes. When the bike is about to
hit that actor at CMB_RamMinSpeed or faster, the plugin says so (CMB_RamHitSpeed, then
CMB_RamHit = the ask's number) and this script pushes it away from the rider. Without the
plugin the globals never change and nothing happens. Since 2026-11-01a (test 47: "you can't kill
an enemy while on the bike, just take them down to the last bit of health"), with the MCM's
"Knock-overs can kill" (CMB_RamKills, on by default) a knock-over whose damage takes the last of
an actor's health kills it, the player the killer; off, never the last point of health, as in
build 2026-10-31a. Since 2026-11-02a (test 48: 12 kills by the bike, no experience: Kill(PlayerRef)
credits the kill but skips the game's damage path, where kill experience is given) that last hit
is the player's own damage, the spell CMB_RamKillSpell cast by the player, so the game rewards the
kill as its own: the MCM's "Kill experience" (CMB_RamKillXP) 1 = Spell.Cast (the default), 2 =
DoCombatSpellApply, 0 = Kill(PlayerRef), as the 2026-11-01a build; one still alive KillCheckAfter
(0.3 s) after the spell is killed by Kill(PlayerRef) all the same, so no kill is lost.
Attach to CMB_ControllerQuest; the controller calls StartRide and EndRide (through CastAs, so
without this script nothing is called). It is a script of its own so that its 0.1 s poll and
the controller's work never wait on each other's lock.
Switches: the MCM's "Knock enemies over" (CMB_RamEnemies) is the player's; [Ram] Enabled in
CMB_Slope.ini is the developer's.}

Actor Property PlayerRef Auto Const Mandatory
ActorValue Property Health Auto Const Mandatory
Faction Property CurrentCompanionFaction Auto Const Mandatory
{Vanilla (00023C01).}
FormList Property CMB_RamTooBig Auto Const Mandatory
{Races never knocked over. Test 40: super mutants (and behemoths) and sentry bots don't count;
the smaller robots and the mutant hounds do. Add races in xEdit.}
GlobalVariable Property CMB_RamEnemies Auto Const Mandatory
{MCM: 1 = hostile actors the bike hits at speed are knocked over. Default 1 (test 40: on).}
GlobalVariable Property CMB_RamMinSpeed Auto Const Mandatory
{MCM: only this fast or faster, game units a second (riding speed is about 900). Default 450.}
GlobalVariable Property CMB_RamDamage Auto Const Mandatory
{MCM: the damage at riding speed, percent of the actor's max health (half of it at the
slowest, up to one and a half times faster). It takes the last of an actor's health only with
CMB_RamKills on (then a kill, the player's); off, never. Default 10 (test 40: fine).}
GlobalVariable Property CMB_RamSeenHi Auto Const Mandatory
GlobalVariable Property CMB_RamSeenLo Auto Const Mandatory
GlobalVariable Property CMB_RamSeen Auto Const Mandatory
GlobalVariable Property CMB_RamOk Auto Const Mandatory
GlobalVariable Property CMB_RamHitSpeed Auto Const Mandatory
GlobalVariable Property CMB_RamHit Auto Const Mandatory
GlobalVariable Property CMB_RamKills Auto Const
{MCM "Knock-overs can kill" (test 47): 1 = a knock-over whose damage reaches the last of an
actor's health kills it, the player the killer (quests and crime as for a kill of the player's
own; the experience by "Kill experience", CMB_RamKillXP, since 2026-11-02a: Kill(PlayerRef) alone
gave none in test 48; protected actors die to it as to the player's own blows, essential ones are
never knocked over). 0 = never the last point of health, as in build 2026-10-31a. Not Mandatory:
an older ESP leaves it None, read as 0. Default 1.}
ActorValue Property Experience Auto Const
{Vanilla (000002C9), for the log only: the player's experience before a kill and 0.5 s after it.
None: not logged.}

; 2026-11-02a (test 48: 12 kills by the bike, no experience): the killing knock-over dealt as the
; player's own damage (script-only, 0x89B and 0x89C). Not Mandatory: an older ESP leaves them None,
; and a kill is Kill(PlayerRef), as the 2026-11-01a build.
Group Kill_Experience
	Spell Property CMB_RamKillSpell Auto Const
	{Test 48 (Kill(PlayerRef) gave no experience): the bike's killing hit dealt as the player's own. None: Kill(PlayerRef).}
	GlobalVariable Property CMB_RamKillXP Auto Const
	{MCM "Kill experience": 0 Kill(PlayerRef) only (2026-11-01a), 1 Spell.Cast by the player (default), 2 DoCombatSpellApply. None: 0.}
EndGroup

int Property TimerPoll = 1 AutoReadOnly
float Property PollInterval = 0.1 AutoReadOnly
{The plugin tells two hits at least 0.12 s apart, longer than this poll, and a hit told while
this script pushes or answers is read right after (OnTimer).}
float Property PollAfterDecide = 0.03 AutoReadOnly
{Test 43: the poll after an answer comes this soon instead of PollInterval: the plugin now tells
the next ask once the last is answered ([Ram] AskAnswered), a frame after it reads the answer,
so in a pack each ask would wait up to a whole poll for nothing (test 42: answers took 234 ms
median, the poll's share of it up to 100). 0.1 = PollInterval, as before test 43.}
float Property PushMeasureAfter = 0.5 AutoReadOnly
{Test 43: how far a pushed actor has moved this long after the push is logged ("Ram: X 0.5 s
after the push: moved N units"), measured at the first poll that late: test 42's protectrons
read No Knockdowns and were braked for, and whether PushActorAway moves such a race (or a
hovering eyebot) at all isn't known. 0 = not measured, as before test 43.}
float Property FullSpeed = 900.0 AutoReadOnly
{The plugin's FullSpeed: riding speed at the default CMB_SpeedPercent.}
float Property ForceAtMinSpeed = 3.0 AutoReadOnly
float Property ForceAtFullSpeed = 8.0 AutoReadOnly
float Property MaxForce = 10.0 AutoReadOnly
{PushActorAway's scale is unknown in game: these are a first guess, to tune from the log.}
float Property Cooldown = 3.0 AutoReadOnly
{Seconds before the same actor can be knocked over again: one that is still down in the
bike's path gets a no, and the bike brakes for it.}
float Property KillBelow = 1.0 AutoReadOnly
{Test 47: with CMB_RamKills on, a hit that would leave less than this much health kills (the
2026-10-31a floor, so every hit the floor held at 1.0 kills instead).}
float Property KillCheckAfter = 0.3 AutoReadOnly
{2026-11-02a: a kill by the spell (CMB_RamKillXP 1 or 2) checked this long after it, at the first
poll that late; still alive (the spell didn't reach it): Kill(PlayerRef), so no kill is lost, only
its experience.}
float Property RefusalLogEvery = 10.0 AutoReadOnly
{The plugin asks again a second after a no: one line per actor and reason this often.}

bool polling = false
int lastSeen = 0
int lastHit = 0
; The last 32 yeses: the ask's number and its actor (the plugin's hit names the number). The
; plugin keeps 8 actors and takes a yes to either of an actor's last two asks, and an answer
; slower than the ask again (0.4 s) takes two slots for one actor: with 4, an actor the plugin
; then said was hit could already be pushed out, and wasn't knocked over (review of the build
; for test 41). 8 actors times 2 was 16. Test 43: the plugin keeps a yes for 10 s even while the
; actor is out of sight ([Ram] YesKeep: a pack's dogs come back), and test 42's pack gave 7 yeses
; in 10 s (20:47:46-55): 16 could push out a yes the plugin still acts on, and its hit would then
; be on nobody this script said yes to (the bike let through with no push). Twice that.
int[] okEvents
Actor[] okActors
string[] okNames
int okNext = 0
; The last few knocked over, for the cooldown (real seconds; cleared on getting on, and a stamp
; later than now dropped as an earlier session's: test 46, DropStaleStamps; test 47: all cleared at
; every load, ClearStamps).
Actor[] knocked
float[] knockedAt
int knockedNext = 0
; The last few refusals logged (the actor's id and the reason), so each is logged once in
; RefusalLogEvery seconds even when two actors take turns.
string[] refusedKeys
float[] refusedAt
int refusedNext = 0
; Test 43: the last few pushed, for the measurement (PushMeasureAfter): who, from where, when
; (None once logged).
Actor[] pushed
string[] pushedNames
float[] pushedX
float[] pushedY
float[] pushedZ
float[] pushedAt
bool[] pushedKill
float[] pushedXp
; 2026-11-02a: how a kill was dealt (KillHow: 0 Kill(PlayerRef), 1 Spell.Cast, 2 DoCombatSpellApply,
; 3 Kill(PlayerRef) after a spell that didn't kill in KillCheckAfter), and whether that check is done.
int[] pushedHow
bool[] pushedChecked
int pushedNext = 0

Function Remember()
	; Test 43: 32 (was 16), and the test with it, or every poll would make them anew.
	if !okEvents || okEvents.Length != 32
		okEvents = new int[32]
		okActors = new Actor[32]
		okNames = new string[32]
		okNext = 0
	endif
	if !knocked || knocked.Length != 4
		knocked = new Actor[4]
		knockedAt = new float[4]
	endif
	if !refusedKeys || refusedKeys.Length != 4
		refusedKeys = new string[4]
		refusedAt = new float[4]
	endif
	if !pushed || pushed.Length != 4 || !pushedKill || !pushedHow || !pushedChecked
		pushed = new Actor[4]
		pushedNames = new string[4]
		pushedX = new float[4]
		pushedY = new float[4]
		pushedZ = new float[4]
		pushedAt = new float[4]
		pushedKill = new bool[4]
		pushedXp = new float[4]
		pushedHow = new int[4]
		pushedChecked = new bool[4]
		pushedNext = 0
	endif
EndFunction

; Getting on, and after a load while riding: what the globals hold now is old news. The log
; says which way the MCM's switch was, and the speed and the damage read with it (a change
; made mid-ride isn't logged).
Function StartRide()
	Remember()
	; Test 46: the stamps of an earlier session counted and logged before all are cleared below.
	DropStaleStamps(Utility.GetCurrentRealTime())
	int i = 0
	while i < okEvents.Length
		okEvents[i] = 0
		okActors[i] = None
		i += 1
	endwhile
	; Test 43: a push from before a load measures nothing (and the real-time clock starts again
	; with the game).
	i = 0
	while i < pushed.Length
		pushed[i] = None
		i += 1
	endwhile
	; Test 46: the refusals' log stamps start afresh with each ride; the cooldown's stamps are
	; kept (a dog knocked over just before a quick get-off and on is still in its 3 s), those
	; from an earlier session dropped by DropStaleStamps above (test 45: dogs refused "knocked
	; over less than 3 s ago" with nothing knocked over this session).
	i = 0
	while i < refusedKeys.Length
		refusedKeys[i] = ""
		refusedAt[i] = 0.0
		i += 1
	endwhile
	refusedNext = 0
	lastSeen = CMB_RamSeen.GetValue() as int
	lastHit = CMB_RamHit.GetValue() as int
	CMB_RamOk.SetValue(0.0)
	if CMB_RamEnemies.GetValue() > 0.0
		Log("Ram: on from " + ((CMB_RamMinSpeed.GetValue() + 0.5) as int) + " a second, " + ((CMB_RamDamage.GetValue() + 0.5) as int) + "% of their health, " + Ternary(Kills(), "the last of it a kill (the player's: " + KillHowText(KillHow()) + ")", "never the last of it") + ".")
	else
		Log("Ram: off (the MCM).")
	endif
	polling = true
	StartTimer(PollInterval, TimerPoll)
EndFunction

Function EndRide()
	polling = false
	CancelTimer(TimerPoll)
	CMB_RamOk.SetValue(0.0)
	; Test 43: a push not yet measured is measured now, however soon (getting off, a load).
	if PushMeasureAfter > 0.0 && pushed
		MeasurePushes(true)
	endif
EndFunction

Event OnTimer(int aiTimerID)
	if aiTimerID != TimerPoll || !polling
		return
	endif
	Remember()
	bool decided = false
	if CMB_RamEnemies.GetValue() > 0.0
		; The hit first: it can't wait.
		bool slow = CheckHit()
		int seen = CMB_RamSeen.GetValue() as int
		if seen != lastSeen
			Decide(seen)
			slow = true
			decided = true
		endif
		; A push or an answer takes several engine calls: a hit told meanwhile is read now,
		; not a poll later.
		if slow
			CheckHit()
		endif
	else
		; Switched off in the MCM: the plugin asks nothing, but whatever the globals hold
		; when it is switched on again is old news.
		lastSeen = CMB_RamSeen.GetValue() as int
		lastHit = CMB_RamHit.GetValue() as int
	endif
	if PushMeasureAfter > 0.0
		MeasurePushes(false)
	endif
	if polling
		if decided
			; Test 43: the plugin's next ask comes a frame after this answer is read (AskAnswered).
			StartTimer(PollAfterDecide, TimerPoll)
		else
			StartTimer(PollInterval, TimerPoll)
		endif
	endif
EndEvent

; True if there was a hit to act on.
bool Function CheckHit()
	int hit = CMB_RamHit.GetValue() as int
	if hit == lastHit
		return false
	endif
	lastHit = hit
	KnockOver(hit)
	return true
EndFunction

; The plugin writes the halves, then the number: read the number again after the halves, so
; the halves are the number's (a newer ask in between is read whole instead).
Function Decide(int aiSeen)
	int n = aiSeen
	int hi = CMB_RamSeenHi.GetValue() as int
	int lo = CMB_RamSeenLo.GetValue() as int
	int again = CMB_RamSeen.GetValue() as int
	int tries = 0
	while again != n && tries < 3
		n = again
		hi = CMB_RamSeenHi.GetValue() as int
		lo = CMB_RamSeenLo.GetValue() as int
		again = CMB_RamSeen.GetValue() as int
		tries += 1
	endwhile
	if lastSeen > 0 && n - lastSeen > 1
		Log("Ram: " + (n - lastSeen - 1) + " of the plugin's asks went unread (the plugin is at " + n + ").")
	endif
	lastSeen = n
	; 32 bits from two halves without overflowing an int: the high half's top bit is the sign
	; (FE... and FF... ids come out negative, as Papyrus holds them).
	int high = hi
	if high >= 32768
		high -= 65536
	endif
	Actor target = Game.GetForm(high * 65536 + lo) as Actor
	string why = WhyNot(target)
	string name = Hex4(hi) + Hex4(lo)
	if why == ""
		CMB_RamOk.SetValue(n as float)
		okEvents[okNext] = n
		okActors[okNext] = target
		okNames[okNext] = name
		okNext = (okNext + 1) % okEvents.Length
		Log("Ram: " + name + " may be knocked over (ask " + n + ").")
	else
		CMB_RamOk.SetValue(-n as float)
		if RefusalIsNews(name + " " + why)
			Log("Ram: " + name + " is not knocked over: " + why + " (ask " + n + ").")
		endif
	endif
EndFunction

; Never companions, neutrals, essentials, children or anyone in power armor; the big ones are
; in CMB_RamTooBig (test 40: super mutants and sentry bots among them).
string Function WhyNot(Actor akTarget)
	if !akTarget
		return "not an actor"
	elseif akTarget == PlayerRef
		return "the rider"
	elseif akTarget.IsDead()
		return "dead"
	elseif akTarget.IsPlayerTeammate() || akTarget.IsInFaction(CurrentCompanionFaction)
		return "a companion"
	elseif akTarget.IsEssential()
		return "essential"
	elseif akTarget.IsChild()
		return "a child"
	elseif !akTarget.IsHostileToActor(PlayerRef)
		return "not hostile"
	elseif akTarget.IsInPowerArmor()
		return "in power armor"
	elseif CMB_RamTooBig.HasForm(akTarget.GetRace())
		return "too big (its race is in CMB_RamTooBig)"
	elseif KnockedWithin(akTarget, Cooldown)
		return "knocked over less than " + (Cooldown as int) + " s ago"
	endif
	return ""
EndFunction

bool Function KnockedWithin(Actor akTarget, float afSeconds)
	float now = Utility.GetCurrentRealTime()
	DropStaleStamps(now)
	int i = 0
	while i < knocked.Length
		if knocked[i] == akTarget && now - knockedAt[i] < afSeconds
			return true
		endif
		i += 1
	endwhile
	return false
EndFunction

; True the first time in RefusalLogEvery seconds this actor is refused for this reason.
bool Function RefusalIsNews(string asKey)
	float now = Utility.GetCurrentRealTime()
	DropStaleStamps(now)
	int i = 0
	while i < refusedKeys.Length
		if refusedKeys[i] == asKey && now - refusedAt[i] < RefusalLogEvery
			return false
		endif
		i += 1
	endwhile
	refusedKeys[refusedNext] = asKey
	refusedAt[refusedNext] = now
	refusedNext = (refusedNext + 1) % refusedKeys.Length
	return true
EndFunction

; Test 46: Utility.GetCurrentRealTime() starts again with every game launch, and these stamps are
; kept in the save, so one from an earlier session can lie in this one's "future", where "now - at
; < Cooldown" held: test 45's dogs were refused "knocked over less than 3 s ago" by test 41's
; save's stamps until four new knock-overs had cycled the ring, and the refusals' log stamps hid
; the refusals (RefusalIsNews said no). A stamp later than now is from an earlier session: cleared
; wherever they're read (StartRide clears them all as well). No switch: a plain bug fix.
Function DropStaleStamps(float afNow)
	int n = 0
	int i = 0
	if knocked
		while i < knocked.Length
			if knockedAt[i] > afNow
				if knocked[i]
					n += 1
				endif
				knocked[i] = None
				knockedAt[i] = 0.0
			endif
			i += 1
		endwhile
	endif
	if refusedKeys
		i = 0
		while i < refusedKeys.Length
			if refusedAt[i] > afNow
				if refusedKeys[i] != ""
					n += 1
				endif
				refusedKeys[i] = ""
				refusedAt[i] = 0.0
			endif
			i += 1
		endwhile
	endif
	if pushed
		i = 0
		while i < pushed.Length
			if pushedAt[i] > afNow
				if pushed[i]
					n += 1
				endif
				pushed[i] = None
				pushedAt[i] = 0.0
			endif
			i += 1
		endwhile
	endif
	if n > 0
		Log("Ram: " + n + " stale knock-over/refusal stamps from an earlier session cleared.")
	endif
EndFunction

; Test 47 (the build-27b check): DropStaleStamps drops only the stamps later than now, so an
; earlier session's stamp that happens to fall in this session's last Cooldown seconds still
; counted. Utility.GetCurrentRealTime() starts again with each game launch, so no stamp from before
; a load means anything after it: the controller's OnGameReloaded calls this at every load (before
; a ride's StartRide), and all of them, the cooldown's, the refusals' log stamps and the pushes not
; yet measured, are cleared. No switch: a plain bug fix, as DropStaleStamps.
Function ClearStamps()
	Remember()
	int n = 0
	int i = 0
	while i < knocked.Length
		if knocked[i]
			n += 1
		endif
		knocked[i] = None
		knockedAt[i] = 0.0
		i += 1
	endwhile
	i = 0
	while i < refusedKeys.Length
		if refusedKeys[i] != ""
			n += 1
		endif
		refusedKeys[i] = ""
		refusedAt[i] = 0.0
		i += 1
	endwhile
	i = 0
	while i < pushed.Length
		if pushed[i]
			n += 1
		endif
		pushed[i] = None
		pushedAt[i] = 0.0
		i += 1
	endwhile
	if n > 0
		Log("Ram: " + n + " knock-over/refusal stamps from before the load cleared.")
	endif
EndFunction

; The push first (it can't wait), away from the rider: harder the faster the bike, force 3 at
; CMB_RamMinSpeed rising to 8 at 900, never over 10. Then a little damage: never the last of
; its health with CMB_RamKills off (2026-10-31a); with it on (the default), a hit that would leave
; under KillBelow kills it, the player the killer (test 47). (Test 40: the bike losing speed at the
; hit is the plugin's.)
Function KnockOver(int aiAsk)
	Actor target = None
	string name = ""
	int i = 0
	while i < okEvents.Length && !target
		if okEvents[i] == aiAsk && aiAsk != 0
			target = okActors[i]
			name = okNames[i]
			okEvents[i] = 0   ; one push per yes
		endif
		i += 1
	endwhile
	if !target
		Log("Ram: the plugin's hit (ask " + aiAsk + ") is on nobody this script said yes to.")
		return
	endif
	float speed = CMB_RamHitSpeed.GetValue()
	float least = CMB_RamMinSpeed.GetValue()
	; Where the speed is between MinSpeed (0) and 900 (1); twice that span at most. With
	; MinSpeed at 900 or over, every hit is at riding speed or faster: the riding force.
	float t = 1.0
	if FullSpeed > least
		t = (speed - least) / (FullSpeed - least)
	endif
	if t < 0.0
		t = 0.0
	elseif t > 2.0
		t = 2.0
	endif
	float force = ForceAtMinSpeed + (ForceAtFullSpeed - ForceAtMinSpeed) * t
	if force > MaxForce
		force = MaxForce
	endif
	int slot = -1
	if PushMeasureAfter > 0.0
		; Test 43: where it stood, for the measurement (MeasurePushes).
		slot = pushedNext
		pushed[slot] = target
		pushedNames[slot] = name
		pushedX[slot] = target.GetPositionX()
		pushedY[slot] = target.GetPositionY()
		pushedZ[slot] = target.GetPositionZ()
		pushedAt[slot] = Utility.GetCurrentRealTime()
		pushedKill[slot] = false
		pushedXp[slot] = -1.0
		pushedHow[slot] = 0
		pushedChecked[slot] = true   ; nothing to check but a spell's kill (below)
		pushedNext = (pushedNext + 1) % pushed.Length
	endif
	PlayerRef.PushActorAway(target, force)
	; The damage: CMB_RamDamage percent of its max health at 900, times speed / 900 held to
	; 0.5-1.5, so 5% at the slowest and 15% at 1350 or faster with the default 10. Test 47: with
	; CMB_RamKills on, a hit that would leave under KillBelow kills it, the player the killer;
	; off, never the last of its health (2026-10-31a).
	float hp = target.GetValue(Health)
	float fraction = target.GetValuePercentage(Health)
	float damage = 0.0
	bool kill = false
	bool kills = Kills()
	int how = 0
	if fraction > 0.0 && (hp > 1.0 || (kills && hp > 0.0))
		float share = speed / FullSpeed
		if share < 0.5
			share = 0.5
		elseif share > 1.5
			share = 1.5
		endif
		damage = hp / fraction * CMB_RamDamage.GetValue() / 100.0 * share
		if kills && damage > 0.0 && hp - damage < KillBelow
			kill = true
		elseif damage > hp - 1.0
			damage = hp - 1.0
		endif
		if kill
			float xp = -1.0
			if Experience
				xp = PlayerRef.GetValue(Experience)
			endif
			; 2026-11-02a (test 48: Kill(PlayerRef) gave no experience): the last hit the player's own
			; damage, the game's own kill reward with it; only with a measure slot (its KillCheckAfter
			; check, Kill(PlayerRef) should the spell not kill), else Kill(PlayerRef) as before.
			how = KillHow()
			if how > 0 && slot >= 0
				if how == 1
					CMB_RamKillSpell.Cast(PlayerRef, target)
				else
					PlayerRef.DoCombatSpellApply(CMB_RamKillSpell, target)
				endif
			else
				how = 0
				target.Kill(PlayerRef)
			endif
			if slot >= 0
				pushedKill[slot] = true
				pushedXp[slot] = xp
				pushedHow[slot] = how
				pushedChecked[slot] = how == 0
			endif
		elseif damage > 0.0
			target.DamageValue(Health, damage)
		else
			damage = 0.0
		endif
	endif
	knocked[knockedNext] = target
	knockedAt[knockedNext] = Utility.GetCurrentRealTime()
	knockedNext = (knockedNext + 1) % knocked.Length
	if kill && how > 0
		Log("Ram: " + name + " knocked over at " + ((speed + 0.5) as int) + " a second (ask " + aiAsk + "): force " + Tenths(force) + ", the hit's " + Tenths(damage) + " damage takes the last of its health (" + Tenths(hp) + "): the player's last hit (CMB_RamKillSpell, " + KillHowText(how) + ")" + ProtectedNote(target) + ".")
	elseif kill
		Log("Ram: " + name + " knocked over at " + ((speed + 0.5) as int) + " a second (ask " + aiAsk + "): force " + Tenths(force) + ", the hit's " + Tenths(damage) + " damage takes the last of its health (" + Tenths(hp) + "): killed, the player the killer (Kill: no experience)" + ProtectedNote(target) + ".")
	else
		Log("Ram: " + name + " knocked over at " + ((speed + 0.5) as int) + " a second (ask " + aiAsk + "): force " + Tenths(force) + ", " + Tenths(damage) + " damage, health " + Tenths(hp) + " -> " + Tenths(hp - damage) + ".")
	endif
EndFunction

; Test 47: the MCM's "Knock-overs can kill" (an older ESP: off).
bool Function Kills()
	return CMB_RamKills && CMB_RamKills.GetValue() > 0.0
EndFunction

; 2026-11-02a: the MCM's "Kill experience" (CMB_RamKillXP): how a killing knock-over is dealt. 1 =
; CMB_RamKillSpell.Cast by the player, 2 = PlayerRef.DoCombatSpellApply, 0 = Kill(PlayerRef) as the
; 2026-11-01a build (also with an older ESP: either property None, or a value out of 0-2).
int Function KillHow()
	int v = 0
	if CMB_RamKillXP
		v = CMB_RamKillXP.GetValue() as int
	endif
	if v < 0 || v > 2 || !CMB_RamKillSpell
		return 0
	endif
	return v
EndFunction

string Function KillHowText(int aiHow)
	if aiHow == 1
		return "Spell.Cast"
	elseif aiHow == 2
		return "DoCombatSpellApply"
	elseif aiHow == 3
		return "Kill(PlayerRef) after the spell"
	endif
	return "Kill(PlayerRef)"
EndFunction

; Test 47: a protected actor dies to the player's own blows, so to this kill too (the log says so).
string Function ProtectedNote(Actor akTarget)
	ActorBase base = akTarget.GetLeveledActorBase()
	if base && base.IsProtected()
		return " (protected: the game lets the player kill it)"
	endif
	return ""
EndFunction

string Function Ternary(bool abCondition, string asYes, string asNo)
	if abCondition
		return asYes
	endif
	return asNo
EndFunction

; Test 43: each push PushMeasureAfter old or more (abNow: every one still waiting, at the ride's
; end) logged with how far the actor has moved from where it stood at the push, in a straight
; line: test 42's protectrons read No Knockdowns, and whether PushActorAway moves such a race (or a
; hovering eyebot) isn't known. One that doesn't move says the robots need another way (a stagger,
; or the plugin's brake as before CMB_RamRobots).
Function MeasurePushes(bool abNow)
	float now = Utility.GetCurrentRealTime()
	DropStaleStamps(now)
	int i = 0
	while i < pushed.Length
		Actor target = pushed[i]
		; 2026-11-02a: a kill by the spell checked first (KillCheckAfter): still alive, Kill(PlayerRef).
		if target && !pushedChecked[i] && (abNow || now - pushedAt[i] >= KillCheckAfter)
			pushedChecked[i] = true
			if !target.IsDead()
				Log("Ram: " + pushedNames[i] + ": the player's last hit (" + KillHowText(pushedHow[i]) + ") didn't kill it in " + Tenths(now - pushedAt[i]) + " s (health " + Tenths(target.GetValue(Health)) + "): Kill(PlayerRef) after it (no experience).")
				pushedHow[i] = 3
				target.Kill(PlayerRef)
			endif
		endif
		if target && (abNow || now - pushedAt[i] >= PushMeasureAfter)
			pushed[i] = None
			float dx = target.GetPositionX() - pushedX[i]
			float dy = target.GetPositionY() - pushedY[i]
			float dz = target.GetPositionZ() - pushedZ[i]
			float moved = Math.Sqrt(dx * dx + dy * dy + dz * dz)
			Log("Ram: " + pushedNames[i] + " " + Tenths(now - pushedAt[i]) + " s after the push: moved " + ((moved + 0.5) as int) + " units" + DeathNote(target, pushedKill[i], pushedXp[i], pushedHow[i]) + ".")
		endif
		i += 1
	endwhile
EndFunction

; Test 47: whether the pushed actor is dead now, and who killed it (the dogs of test 47 "seemed to
; work": nothing logged whether the bike or a shot did it); after the bike's kill, the player's
; experience then and now (-1: Experience not filled). 2026-11-02a: the victim's level, the gain
; and how the kill was dealt (aiHow, KillHow's; "+0.0: none" after Spell.Cast says "Kill experience"
; 2 is the next to try).
string Function DeathNote(Actor akTarget, bool abKilled, float afXpBefore, int aiHow)
	if !akTarget.IsDead()
		if abKilled
			return "; NOT dead after Kill (health " + Tenths(akTarget.GetValue(Health)) + ")"
		endif
		return ""
	endif
	string who = "nobody"
	Actor killer = akTarget.GetKiller()
	if killer == PlayerRef
		who = "the player"
	elseif killer
		who = "someone else"
	endif
	string note = "; dead, the killer " + who
	if abKilled
		note += ", its level " + akTarget.GetLevel()
	endif
	if abKilled && afXpBefore >= 0.0 && Experience
		float xpNow = PlayerRef.GetValue(Experience)
		note += ", the player's experience " + Tenths(afXpBefore) + " -> " + Tenths(xpNow) + " (" + XpGain(xpNow - afXpBefore, aiHow) + ")"
	endif
	return note
EndFunction

; 2026-11-02a: the gain at a bike kill, and whose it is likely to be.
string Function XpGain(float afGain, int aiHow)
	string gain = "+" + Tenths(afGain)
	if afGain < 0.05
		if aiHow == 1
			return "+0.0: none (Spell.Cast: try \"Kill experience\" 2)"
		elseif aiHow == 2
			return "+0.0: none (DoCombatSpellApply)"
		endif
		return "+0.0: none (" + KillHowText(aiHow) + ")"
	elseif aiHow == 1 || aiHow == 2
		return gain + ": the game's, " + KillHowText(aiHow)
	elseif aiHow == 3
		return gain + ": " + KillHowText(aiHow)
	endif
	return gain + ": " + KillHowText(aiHow) + " (not the bike's: another kill or reward meanwhile)"
EndFunction

; A value of 0 or more to one decimal ("12.5"): Papyrus prints floats with six decimals.
string Function Tenths(float afValue)
	int tenths = (afValue * 10.0 + 0.5) as int
	if tenths < 0
		tenths = 0
	endif
	return (tenths / 10) + "." + (tenths % 10)
EndFunction

; Four hex digits of 0 to 65535, so the log names the actor as the plugin's log does.
string Function Hex4(int aiValue)
	string out = ""
	int v = aiValue
	int k = 0
	while k < 4
		out = HexDigit(v % 16) + out
		v = v / 16
		k += 1
	endwhile
	return out
EndFunction

string Function HexDigit(int aiDigit)
	if aiDigit < 10
		return "" + aiDigit
	elseif aiDigit == 10
		return "A"
	elseif aiDigit == 11
		return "B"
	elseif aiDigit == 12
		return "C"
	elseif aiDigit == 13
		return "D"
	elseif aiDigit == 14
		return "E"
	endif
	return "F"
EndFunction

Function Log(string asMessage)
	Debug.Trace("[CMB] " + asMessage)
EndFunction

; A call on CMB_ControllerQuest can land on any of its scripts (tests 30 and 31: MCM's, on
; CMB_HotkeyF4SE and CMB_GearRestoreF4SE), so a console cqf can land on this one, on that quest
; since test 41 (review of its build): relayed as there, through CMB_MCMRelay's lookup of the
; controller (this script has no property for it).
Function EmergencyReset()
	CMB_MCMRelay.EmergencyReset()
EndFunction

Function ForceGiveKeys()
	CMB_MCMRelay.ForceGiveKeys()
EndFunction

Function HotkeyPressed()
	CMB_MCMRelay.HotkeyPressed()
EndFunction

Function HeadlampPressed()
	CMB_MCMRelay.HeadlampPressed()
EndFunction

Function RefreshHotkey()
	CMB_MCMRelay.RefreshHotkey()
EndFunction

Function DecideTeleportsAtOnce(int aiAtOnce)
	CMB_ControllerScript c = CMB_MCMRelay.Controller()
	if c
		c.DecideTeleportsAtOnce(aiAtOnce)
	endif
EndFunction

Function WatchBusy(int aiOn)
	CMB_ControllerScript c = CMB_MCMRelay.Controller()
	if c
		c.WatchBusy(aiOn)
	endif
EndFunction
