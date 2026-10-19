Scriptname CMB_RamScript extends Quest
{Commonwealth Motorbike: hostile actors the bike hits at speed are knocked over and take a
little damage (test 40's wish). Needs F4SE and CMB_Slope.dll, whose rays see what is ahead:
the plugin asks about an actor it sees (CMB_RamSeenHi/Lo, its form id's two halves, then
CMB_RamSeen, the ask's number), this script answers in CMB_RamOk (the number: yes; minus the
number: no), and the plugin keeps the throttle open only for a yes. When the bike is about to
hit that actor at CMB_RamMinSpeed or faster, the plugin says so (CMB_RamHitSpeed, then
CMB_RamHit = the ask's number) and this script pushes it away from the rider. Without the
plugin the globals never change and nothing happens.
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
slowest, up to one and a half times faster). It never kills. Default 10 (test 40: fine).}
GlobalVariable Property CMB_RamSeenHi Auto Const Mandatory
GlobalVariable Property CMB_RamSeenLo Auto Const Mandatory
GlobalVariable Property CMB_RamSeen Auto Const Mandatory
GlobalVariable Property CMB_RamOk Auto Const Mandatory
GlobalVariable Property CMB_RamHitSpeed Auto Const Mandatory
GlobalVariable Property CMB_RamHit Auto Const Mandatory

int Property TimerPoll = 1 AutoReadOnly
float Property PollInterval = 0.1 AutoReadOnly
{The plugin tells two hits at least 0.12 s apart, longer than this poll, and a hit told while
this script pushes or answers is read right after (OnTimer).}
float Property FullSpeed = 900.0 AutoReadOnly
{The plugin's FullSpeed: riding speed at the default CMB_SpeedPercent.}
float Property ForceAtMinSpeed = 3.0 AutoReadOnly
float Property ForceAtFullSpeed = 8.0 AutoReadOnly
float Property MaxForce = 10.0 AutoReadOnly
{PushActorAway's scale is unknown in game: these are a first guess, to tune from the log.}
float Property Cooldown = 3.0 AutoReadOnly
{Seconds before the same actor can be knocked over again: one that is still down in the
bike's path gets a no, and the bike brakes for it.}
float Property RefusalLogEvery = 10.0 AutoReadOnly
{The plugin asks again a second after a no: one line per actor and reason this often.}

bool polling = false
int lastSeen = 0
int lastHit = 0
; The last 16 yeses: the ask's number and its actor (the plugin's hit names the number). The
; plugin keeps 8 actors and takes a yes to either of an actor's last two asks, and an answer
; slower than the ask again (0.4 s) takes two slots for one actor: with 4, an actor the plugin
; then said was hit could already be pushed out, and wasn't knocked over (review of the build
; for test 41). 8 actors times 2.
int[] okEvents
Actor[] okActors
string[] okNames
int okNext = 0
; The last few knocked over, for the cooldown.
Actor[] knocked
float[] knockedAt
int knockedNext = 0
; The last few refusals logged (the actor's id and the reason), so each is logged once in
; RefusalLogEvery seconds even when two actors take turns.
string[] refusedKeys
float[] refusedAt
int refusedNext = 0

Function Remember()
	if !okEvents || okEvents.Length != 16
		okEvents = new int[16]
		okActors = new Actor[16]
		okNames = new string[16]
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
EndFunction

; Getting on, and after a load while riding: what the globals hold now is old news. The log
; says which way the MCM's switch was, and the speed and the damage read with it (a change
; made mid-ride isn't logged).
Function StartRide()
	Remember()
	int i = 0
	while i < okEvents.Length
		okEvents[i] = 0
		okActors[i] = None
		i += 1
	endwhile
	lastSeen = CMB_RamSeen.GetValue() as int
	lastHit = CMB_RamHit.GetValue() as int
	CMB_RamOk.SetValue(0.0)
	if CMB_RamEnemies.GetValue() > 0.0
		Log("Ram: on from " + ((CMB_RamMinSpeed.GetValue() + 0.5) as int) + " a second, " + ((CMB_RamDamage.GetValue() + 0.5) as int) + "% of their health.")
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
EndFunction

Event OnTimer(int aiTimerID)
	if aiTimerID != TimerPoll || !polling
		return
	endif
	Remember()
	if CMB_RamEnemies.GetValue() > 0.0
		; The hit first: it can't wait.
		bool slow = CheckHit()
		int seen = CMB_RamSeen.GetValue() as int
		if seen != lastSeen
			Decide(seen)
			slow = true
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
	if polling
		StartTimer(PollInterval, TimerPoll)
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

; The push first (it can't wait), away from the rider: harder the faster the bike, force 3 at
; CMB_RamMinSpeed rising to 8 at 900, never over 10. Then a little damage, never the last of
; its health. (Test 40: the bike losing speed at the hit is the plugin's.)
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
	PlayerRef.PushActorAway(target, force)
	; The damage: CMB_RamDamage percent of its max health at 900, times speed / 900 held to
	; 0.5-1.5, so 5% at the slowest and 15% at 1350 or faster with the default 10.
	float hp = target.GetValue(Health)
	float fraction = target.GetValuePercentage(Health)
	float damage = 0.0
	if fraction > 0.0 && hp > 1.0
		float share = speed / FullSpeed
		if share < 0.5
			share = 0.5
		elseif share > 1.5
			share = 1.5
		endif
		damage = hp / fraction * CMB_RamDamage.GetValue() / 100.0 * share
		if damage > hp - 1.0
			damage = hp - 1.0
		endif
		if damage > 0.0
			target.DamageValue(Health, damage)
		else
			damage = 0.0
		endif
	endif
	knocked[knockedNext] = target
	knockedAt[knockedNext] = Utility.GetCurrentRealTime()
	knockedNext = (knockedNext + 1) % knocked.Length
	Log("Ram: " + name + " knocked over at " + ((speed + 0.5) as int) + " a second (ask " + aiAsk + "): force " + Tenths(force) + ", " + Tenths(damage) + " damage, health " + Tenths(hp) + " -> " + Tenths(hp - damage) + ".")
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
