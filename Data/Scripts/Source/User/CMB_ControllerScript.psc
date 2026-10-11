Scriptname CMB_ControllerScript extends Quest
{Commonwealth Motorbike - the brain of the mod.
Handles getting on and off the bike, riding speed, player controls while
riding, companions, parking, calling the bike and the side bag.

There is no real vehicle physics here. While riding, the player wears the bike
as a non-playable armor piece, moves faster through SpeedMult and has jumping,
sprinting and (optionally) combat disabled. The parked bike is a normal
Activator reference that gets moved around and enabled/disabled.}

; ---------------------------------------------------------------------------
; Properties (filled in the Creation Kit, see docs/BUILD_GUIDE.md)
; ---------------------------------------------------------------------------

Group Required_References
	Actor Property PlayerRef Auto Const Mandatory
	ObjectReference Property BikeRef Auto Const Mandatory
	{The parked bike: a persistent CMB_BikeActivator reference placed in CMB_HoldingCell.}
	ObjectReference Property SideBagRef Auto Const Mandatory
	{The side bag: a persistent CMB_SideBagContainer reference placed in CMB_HoldingCell.}
	ObjectReference Property HoldingMarkerRef Auto Const Mandatory
	{An XMarker in CMB_HoldingCell. Companions riding along wait here while hidden.}
EndGroup

Group Required_Forms
	Armor Property CMB_BikeRiderArmor Auto Const Mandatory
	{Non-playable armor that shows the bike under the player while riding.}
	Potion Property CMB_BikeKeys Auto Const Mandatory
	{The keys aid item. Favorite it to a hotkey to get on and off quickly.}
	Message Property CMB_KeysMenu Auto Const Mandatory
	{Shown when the keys are used and the bike is not nearby. Buttons: Call it here / Open side bag / Cancel.}
	ActorValue Property SpeedMult Auto Const Mandatory
	ActorValue Property CarryWeight Auto Const Mandatory
	Armor Property Pipboy Auto Const Mandatory
	{Vanilla Pip-Boy (00021B3B). The keys are only handed out once the player has one, i.e. after leaving Vault 111.}
EndGroup

Group Settings
	GlobalVariable Property CMB_SpeedPercent Auto Const Mandatory
	{Riding speed as a percentage of the rider's current speed. Default 250.}
	GlobalVariable Property CMB_CompanionMode Auto Const Mandatory
	{0 = companions run alongside (same speed boost, pulled along if left behind). 1 = companions ride along (hidden while riding). Default 1.}
	GlobalVariable Property CMB_AllowCombat Auto Const Mandatory
	{1 = weapons and VATS stay usable while riding. Default 0.}
	GlobalVariable Property CMB_ForceThirdPerson Auto Const Mandatory
	{1 = switch to third person when getting on, so the bike is visible. Default 1.}
	GlobalVariable Property CMB_UseRiderPose Auto Const Mandatory
	{1 = swap to the seated rider animation set while riding (needs the optional rider pose files). Default 0.}
	GlobalVariable Property CMB_CatchUpDistance Auto Const Mandatory
	{Companions running alongside further away than this are moved up behind the player. 0 = never. Default 2500.}
EndGroup

Group Optional
	Keyword Property CMB_AnimArchetypeRider Auto Const
	{Animation archetype keyword for the rider pose. Only used when CMB_UseRiderPose is 1.}
	Keyword Property AnimArchetypePlayer Auto Const
	{Vanilla player archetype (0006B508). Restored after riding when the rider pose was used.}
	Sound Property CMB_EngineStartSound Auto Const
	Sound Property CMB_EngineStopSound Auto Const
EndGroup

; ---------------------------------------------------------------------------
; Constants
; ---------------------------------------------------------------------------

int Property TimerTick = 1 AutoReadOnly
int Property TimerKeys = 2 AutoReadOnly
int Property TimerDelivery = 3 AutoReadOnly
float Property TickInterval = 1.0 AutoReadOnly
float Property DeliveryRetryInterval = 20.0 AutoReadOnly
float Property MountRange = 350.0 AutoReadOnly
float Property ParkSideOffset = 110.0 AutoReadOnly
float Property CallAheadDistance = 220.0 AutoReadOnly
float Property FollowerScanRange = 4000.0 AutoReadOnly
float Property MinSpeedPercent = 100.0 AutoReadOnly
float Property MaxSpeedPercent = 500.0 AutoReadOnly
int Property KeysStackSize = 2 AutoReadOnly
{Two keys, so using one never empties the stack and the favorites hotkey survives.}

; ---------------------------------------------------------------------------
; Runtime state
; ---------------------------------------------------------------------------

bool riding = false
bool busy = false
bool keysDelivered = false
bool riderPoseApplied = false
float playerSpeedDelta = 0.0
InputEnableLayer rideLayer
Actor[] stowedFollowers
Actor[] boostedFollowers
float[] boostedDeltas

; ---------------------------------------------------------------------------
; Lifecycle
; ---------------------------------------------------------------------------

Event OnInit()
	EnsureArrays()
	TryDeliverKeys()
EndEvent

; Called by CMB_PlayerAliasScript every time a save is loaded.
Function OnGameReloaded()
	EnsureArrays()
	busy = false
	if keysDelivered
		GiveKeysIfMissing(true)
	else
		TryDeliverKeys()
	endif

	CMB_SideBagScript bag = SideBagRef as CMB_SideBagScript
	if bag
		bag.OnGameReloaded()
	endif

	if riding
		; Input layers and the engine's cached movement speed do not reliably
		; survive a reload, so put the riding setup back in place.
		ApplyControls()
		RefreshMovement(PlayerRef)
		if riderPoseApplied
			PlayerRef.AttemptAnimationSetSwitch()
		endif
		RegisterForPlayerTeleport()
		StartTimer(TickInterval, TimerTick)
	endif

	; The optional F4SE hotkey script lives on this quest too. Looking it up by
	; name keeps this script compiling and running without F4SE.
	ScriptObject hotkey = CastAs("CMB_HotkeyF4SE")
	if hotkey
		hotkey.CallFunction("RegisterHotkey", new Var[0])
	endif
EndFunction

; ---------------------------------------------------------------------------
; Public entry points
; ---------------------------------------------------------------------------

bool Function IsRiding()
	return riding
EndFunction

; The keys arrive the first time the player is outdoors with a Pip-Boy, so a new
; game's pre-war intro and Vault 111 are left alone. Existing saves get them
; the next time the player is outside.
Function TryDeliverKeys()
	if keysDelivered
		return
	endif
	if PlayerRef.GetItemCount(Pipboy) > 0 && !PlayerRef.IsInInterior()
		keysDelivered = true
		CancelTimer(TimerDelivery)
		if !riding
			UnregisterForPlayerTeleport()
		endif
		GiveKeysIfMissing(false)
		Debug.Notification("Use the Motorbike Keys (Aid) to call your motorbike.")
		Log("Keys delivered.")
	else
		RegisterForPlayerTeleport()
		StartTimer(DeliveryRetryInterval, TimerDelivery)
	endif
EndFunction

; Console fallback, e.g. for alternative-start mods without a Pip-Boy:
;   cqf CMB_ControllerQuest ForceGiveKeys
Function ForceGiveKeys()
	keysDelivered = true
	CancelTimer(TimerDelivery)
	GiveKeysIfMissing(false)
EndFunction

; Called by the keys' magic effect. Work is deferred to a timer so the effect
; can finish right away, and so a menu opened from the Pip-Boy shows after it closes.
Function RequestKeysAction()
	GiveKeysIfMissing(true)
	StartTimer(0.1, TimerKeys)
EndFunction

; Hotkey behaviour: get off, get on, or call the bike over if it's not nearby.
Function ToggleRide()
	; Nothing to ride before the keys turn up (pre-war intro, Vault 111).
	if busy || !keysDelivered
		return
	endif
	if riding
		Dismount()
	elseif IsBikeNearPlayer()
		Mount()
	else
		CallBike()
	endif
EndFunction

Function Mount()
	if riding || busy
		return
	endif
	; Claim the lock before calling anything on other objects: those calls let
	; other threads (hotkey, timer, activation) run in between.
	busy = true
	string blocker = GetMountBlocker()
	if blocker != ""
		busy = false
		Debug.Notification(blocker)
		return
	endif
	EnsureArrays()

	Game.FadeOutGame(true, true, 0.0, 0.25, true)
	Utility.Wait(0.3)

	if CMB_ForceThirdPerson.GetValue() > 0.0
		Game.ForceThirdPerson()
	endif
	BikeRef.Disable()
	if PlayerRef.GetItemCount(CMB_BikeRiderArmor) == 0
		PlayerRef.AddItem(CMB_BikeRiderArmor, 1, true)
	endif
	PlayerRef.EquipItem(CMB_BikeRiderArmor, true, true)
	ApplyRiderPose()
	ApplyControls()
	playerSpeedDelta = ApplySpeed(PlayerRef)
	HandleFollowersOnMount()

	riding = true
	RegisterForPlayerTeleport()
	StartTimer(TickInterval, TimerTick)
	PlaySound(CMB_EngineStartSound)
	Log("Mounted. SpeedMult +" + playerSpeedDelta + ", stowed " + stowedFollowers.Length + ", running " + boostedFollowers.Length)

	Game.FadeOutGame(false, true, 0.0, 0.35)
	busy = false
EndFunction

Function Dismount()
	if !riding || busy
		return
	endif
	busy = true

	Game.FadeOutGame(true, true, 0.0, 0.25, true)
	Utility.Wait(0.3)

	ParkBesidePlayer()
	FinishRide()
	Log("Dismounted.")

	Game.FadeOutGame(false, true, 0.0, 0.35)
	busy = false
EndFunction

; Bring the parked bike to the player (outdoors only).
Function CallBike()
	if riding || busy
		return
	endif
	busy = true
	if PlayerRef.IsInInterior()
		busy = false
		Debug.Notification("You can only call your motorbike outdoors.")
		return
	endif
	float angle = PlayerRef.GetAngleZ()
	BikeRef.Disable()
	BikeRef.MoveTo(PlayerRef, OffsetX(angle, CallAheadDistance, 60.0), OffsetY(angle, CallAheadDistance, 60.0), 0.0, true)
	BikeRef.Enable(true)
	PlaySound(CMB_EngineStopSound)
	busy = false
	Log("Bike called to the player.")
	Debug.Notification("Your motorbike rolls up.")
EndFunction

Function OpenSideBag()
	; Opening a container that sits in another cell works with a plain Activate.
	SideBagRef.Activate(PlayerRef, true)
EndFunction

; Console escape hatch: undoes everything riding changed, whatever state we're in.
Function EmergencyReset()
	CancelTimer(TimerTick)
	CancelTimer(TimerKeys)
	UnregisterForPlayerTeleport()
	busy = true
	if !PlayerRef.IsInInterior()
		ParkBesidePlayer()
	elseif riding
		; Indoors: the bike is still shadowing the last outdoor spot.
		BikeRef.Enable()
	endif
	FinishRide()
	busy = false
	Game.FadeOutGame(false, true, 0.0, 0.1)
	Log("Emergency reset.")
	Debug.Notification("Motorbike: reset done.")
EndFunction

; ---------------------------------------------------------------------------
; Timers and events
; ---------------------------------------------------------------------------

Event OnTimer(int aiTimerID)
	if aiTimerID == TimerDelivery
		TryDeliverKeys()
	elseif aiTimerID == TimerKeys
		HandleKeys()
	elseif aiTimerID == TimerTick && riding
		RideTick()
		if riding
			StartTimer(TickInterval, TimerTick)
		endif
	endif
EndEvent

Event OnPlayerTeleport()
	if riding
		RideTick()
	elseif !keysDelivered
		TryDeliverKeys()
	endif
EndEvent

Function HandleKeys()
	; Wait doesn't count time spent in menus, so this also waits for the
	; Pip-Boy to close when the keys were used from there.
	Utility.Wait(0.1)
	if busy
		return
	endif
	if riding
		Dismount()
	elseif IsBikeNearPlayer()
		Mount()
	else
		int choice = CMB_KeysMenu.Show()
		if choice == 0
			CallBike()
		elseif choice == 1
			OpenSideBag()
		endif
	endif
EndFunction

; Runs every second while riding, and right after any teleport.
Function RideTick()
	if busy || !riding
		return
	endif

	; Things the bike can't follow you into. The bike has been shadowing the
	; player, so it's left at the last outdoor spot we saw.
	if PlayerRef.IsInInterior()
		AutoDismount("You leave the motorbike parked outside.")
		return
	elseif PlayerRef.IsInPowerArmor()
		AutoDismount("You can't ride in power armor. The motorbike is parked nearby.")
		return
	elseif PlayerRef.GetSitState() != 0
		AutoDismount("The motorbike is parked nearby.")
		return
	endif

	; The disabled bike follows the player, so it can be dropped here at any moment.
	ShadowPlayer()
	CatchUpFollowers()

	if !PlayerRef.IsEquipped(CMB_BikeRiderArmor)
		PlayerRef.EquipItem(CMB_BikeRiderArmor, true, true)
	endif
EndFunction

; ---------------------------------------------------------------------------
; Riding setup and teardown
; ---------------------------------------------------------------------------

string Function GetMountBlocker()
	if PlayerRef.IsInPowerArmor()
		return "You can't ride a motorbike in power armor."
	elseif PlayerRef.IsInInterior()
		return "There's no room to ride in here."
	elseif PlayerRef.GetSitState() != 0
		return "You need to stand up first."
	endif
	return ""
EndFunction

; Undo everything riding changed on the player and companions.
; Placing the bike is the caller's job.
Function FinishRide()
	CancelTimer(TimerTick)
	UnregisterForPlayerTeleport()

	int armorCount = PlayerRef.GetItemCount(CMB_BikeRiderArmor)
	if armorCount > 0
		PlayerRef.UnequipItem(CMB_BikeRiderArmor, false, true)
		PlayerRef.RemoveItem(CMB_BikeRiderArmor, armorCount, true)
	endif
	ClearRiderPose()
	ReleaseControls()
	RemoveSpeed(PlayerRef, playerSpeedDelta)
	playerSpeedDelta = 0.0
	HandleFollowersOnDismount()

	if riding
		PlaySound(CMB_EngineStopSound)
	endif
	riding = false
EndFunction

Function AutoDismount(string asMessage)
	busy = true
	BikeRef.Enable()
	FinishRide()
	busy = false
	Debug.Notification(asMessage)
	Log("Auto-dismounted: " + asMessage)
EndFunction

Function ParkBesidePlayer()
	float angle = PlayerRef.GetAngleZ()
	BikeRef.MoveTo(PlayerRef, OffsetX(angle, 0.0, ParkSideOffset), OffsetY(angle, 0.0, ParkSideOffset), 0.0, true)
	BikeRef.Enable()
EndFunction

Function ShadowPlayer()
	float angle = PlayerRef.GetAngleZ()
	BikeRef.MoveTo(PlayerRef, OffsetX(angle, 0.0, ParkSideOffset), OffsetY(angle, 0.0, ParkSideOffset), 0.0, true)
EndFunction

Function ApplyControls()
	if rideLayer
		rideLayer.Delete()
	endif
	rideLayer = InputEnableLayer.Create()
	bool noCombat = CMB_AllowCombat.GetValue() == 0.0
	; Movement, looking, menus, activation and favorites stay enabled.
	; Arguments: movement, fighting, camSwitch, looking, sneaking, menu,
	; activate, journalTabs, VATS, favorites, running.
	rideLayer.DisablePlayerControls(false, noCombat, false, false, true, false, false, false, noCombat, false, false)
	rideLayer.EnableJumping(false)
	; EnableSprinting isn't in the official function list, so it's called by
	; name: if it doesn't exist that only logs an error instead of breaking
	; the compile, and sprinting simply stays allowed.
	Var[] sprintArgs = new Var[1]
	sprintArgs[0] = false
	rideLayer.CallFunction("EnableSprinting", sprintArgs)
EndFunction

Function ReleaseControls()
	if rideLayer
		rideLayer.Delete()
		rideLayer = None
	endif
EndFunction

; Returns how much SpeedMult was added, so exactly that can be taken away later.
float Function ApplySpeed(Actor akActor)
	float percent = CMB_SpeedPercent.GetValue()
	if percent < MinSpeedPercent
		percent = MinSpeedPercent
	elseif percent > MaxSpeedPercent
		percent = MaxSpeedPercent
	endif
	float current = akActor.GetValue(SpeedMult)
	float delta = current * (percent / 100.0 - 1.0)
	if delta != 0.0
		akActor.ModValue(SpeedMult, delta)
		RefreshMovement(akActor)
	endif
	return delta
EndFunction

Function RemoveSpeed(Actor akActor, float afDelta)
	if afDelta != 0.0
		akActor.ModValue(SpeedMult, -afDelta)
		RefreshMovement(akActor)
	endif
EndFunction

; SpeedMult changes only kick in once the engine recalculates movement speed.
; Nudging carry weight forces that recalculation.
Function RefreshMovement(Actor akActor)
	akActor.ModValue(CarryWeight, 0.1)
	akActor.ModValue(CarryWeight, -0.1)
EndFunction

Function ApplyRiderPose()
	if CMB_UseRiderPose.GetValue() > 0.0 && CMB_AnimArchetypeRider && AnimArchetypePlayer
		PlayerRef.ChangeAnimArchetype(CMB_AnimArchetypeRider)
		PlayerRef.AttemptAnimationSetSwitch()
		riderPoseApplied = true
	endif
EndFunction

Function ClearRiderPose()
	if riderPoseApplied
		; The player's normal archetype is AnimArchetypePlayer, not "none".
		PlayerRef.ChangeAnimArchetype(AnimArchetypePlayer)
		PlayerRef.AttemptAnimationSetSwitch()
		riderPoseApplied = false
	endif
EndFunction

; ---------------------------------------------------------------------------
; Companions
; ---------------------------------------------------------------------------

; Teammates close to the player who are actually following them.
Actor[] Function GetRideableFollowers()
	Actor[] result = new Actor[0]
	Actor[] followers = Game.GetPlayerFollowers()
	if followers == None
		return result
	endif
	int i = 0
	while i < followers.Length
		Actor follower = followers[i]
		if follower && follower != PlayerRef && !follower.IsDead() && !follower.IsDisabled() && follower.IsPlayerTeammate()
			if follower.Is3DLoaded() && follower.GetDistance(PlayerRef) < FollowerScanRange
				result.Add(follower)
			endif
		endif
		i += 1
	endwhile
	return result
EndFunction

Function HandleFollowersOnMount()
	stowedFollowers.Clear()
	boostedFollowers.Clear()
	boostedDeltas.Clear()

	bool rideAlong = CMB_CompanionMode.GetValue() == 1.0
	Actor[] followers = GetRideableFollowers()
	int i = 0
	while i < followers.Length
		Actor follower = followers[i]
		; Companions in power armor can't be tucked away safely, so they run instead.
		if rideAlong && !follower.IsInPowerArmor()
			follower.Disable()
			follower.MoveTo(HoldingMarkerRef)
			stowedFollowers.Add(follower)
		else
			boostedFollowers.Add(follower)
			boostedDeltas.Add(ApplySpeed(follower))
		endif
		i += 1
	endwhile
EndFunction

Function HandleFollowersOnDismount()
	EnsureArrays()
	float angle = PlayerRef.GetAngleZ()

	int i = 0
	while i < stowedFollowers.Length
		Actor rider = stowedFollowers[i]
		if rider
			; Step off behind the player, on the opposite side to the parked bike.
			rider.MoveTo(PlayerRef, OffsetX(angle, -120.0, -90.0 - 60.0 * i), OffsetY(angle, -120.0, -90.0 - 60.0 * i), 0.0, true)
			rider.Enable()
			rider.EvaluatePackage(false)
		endif
		i += 1
	endwhile
	stowedFollowers.Clear()

	int j = 0
	while j < boostedFollowers.Length
		Actor runner = boostedFollowers[j]
		if runner
			RemoveSpeed(runner, boostedDeltas[j])
		endif
		j += 1
	endwhile
	boostedFollowers.Clear()
	boostedDeltas.Clear()
EndFunction

Function CatchUpFollowers()
	float maxDistance = CMB_CatchUpDistance.GetValue()
	if maxDistance <= 0.0
		return
	endif
	float angle = PlayerRef.GetAngleZ()
	int i = 0
	while i < boostedFollowers.Length
		Actor runner = boostedFollowers[i]
		if runner && !runner.IsDead() && !runner.IsDisabled() && runner.GetDistance(PlayerRef) > maxDistance
			runner.MoveTo(PlayerRef, OffsetX(angle, -300.0, -100.0), OffsetY(angle, -300.0, -100.0), 0.0, true)
		endif
		i += 1
	endwhile
EndFunction

; ---------------------------------------------------------------------------
; Helpers
; ---------------------------------------------------------------------------

Function EnsureArrays()
	if stowedFollowers == None
		stowedFollowers = new Actor[0]
	endif
	if boostedFollowers == None
		boostedFollowers = new Actor[0]
	endif
	if boostedDeltas == None
		boostedDeltas = new float[0]
	endif
EndFunction

Function GiveKeysIfMissing(bool abSilent)
	int have = PlayerRef.GetItemCount(CMB_BikeKeys)
	if have < KeysStackSize
		PlayerRef.AddItem(CMB_BikeKeys, KeysStackSize - have, abSilent)
	endif
EndFunction

bool Function IsBikeNearPlayer()
	if BikeRef.IsDisabled() || PlayerRef.IsInInterior() || !BikeRef.Is3DLoaded()
		return false
	endif
	return PlayerRef.GetDistance(BikeRef) <= MountRange
EndFunction

; Shows up in Papyrus.0.log when Papyrus logging is enabled (see docs/TESTING.md).
Function Log(string asMessage)
	Debug.Trace("[CMB] " + asMessage)
EndFunction

Function PlaySound(Sound akSound)
	if akSound
		akSound.Play(PlayerRef)
	endif
EndFunction

; World-space offsets for MoveTo, given the player's heading and how far
; forward/right of them we want something. Heading 0 = north (+Y), clockwise.
float Function OffsetX(float afAngle, float afForward, float afRight)
	return Math.Sin(afAngle) * afForward + Math.Cos(afAngle) * afRight
EndFunction

float Function OffsetY(float afAngle, float afForward, float afRight)
	return Math.Cos(afAngle) * afForward - Math.Sin(afAngle) * afRight
EndFunction
