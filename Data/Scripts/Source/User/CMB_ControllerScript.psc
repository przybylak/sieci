Scriptname CMB_ControllerScript extends Quest
{Commonwealth Motorbike - the brain of the mod.
Handles getting on and off the bike, riding speed, player controls while
riding, companions, parking, calling the bike and the side bag.

There is no real vehicle physics here. While riding, the player wears the bike
as a non-playable armor piece, moves faster through SpeedMult and has jumping,
sprinting and (optionally) combat disabled. The parked bike is a normal
Activator reference that gets moved around and enabled/disabled.
Riding also cuts fall damage, ends in deep water and (optionally) when an enemy
hits you.}

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
	{Non-playable armor that shows the bike under the player while riding. It hangs off the
	rider's COM bone, so it turns with the seated rider.}
	Armor Property CMB_BikeRiderArmorFrame Auto Const Mandatory
	{The same bike planted on the ground (AnimObjectA bone): for riding without the seated
	pose, with a weapon drawn, or when CMB_BikeFollowsRider is 0.}
	Potion Property CMB_BikeKeys Auto Const Mandatory
	{The keys aid item. Favorite it to a hotkey to get on and off quickly.}
	Message Property CMB_KeysMenu Auto Const Mandatory
	{Shown when the keys are used and the bike is not nearby. Buttons: Call it here / Open side bag / Cancel.}
	ActorValue Property SpeedMult Auto Const Mandatory
	ActorValue Property CarryWeight Auto Const Mandatory
	Armor Property Pipboy Auto Const Mandatory
	{Vanilla Pip-Boy (00021B3B). The keys are only handed out once the player has one, i.e. after leaving Vault 111.}
	FormList Property CMB_FuelItems Auto Const Mandatory
	{What the bike burns. Flamer Fuel (000CAC78) by default; add items in xEdit to accept more.}
	Spell Property CMB_SwimWatchAbility Auto Const Mandatory
	{Hidden ability whose effects report swimming (IsSwimming, SetSwimming) and being in
	water at all (IsInWater, SetInWater).}
	ActorValue Property FallingDamageMod Auto Const Mandatory
	{Vanilla (000BA43D). Percent less fall damage, as the Acrobat's legendary effect uses.}
	ActorValue Property Health Auto Const Mandatory
	{Vanilla (000002D4).}
EndGroup

Group Settings
	GlobalVariable Property CMB_SpeedPercent Auto Const Mandatory
	{Riding speed as a percentage of the rider's current speed. Default 250.}
	GlobalVariable Property CMB_CompanionMode Auto Const Mandatory
	{0 = companions run alongside (same speed boost, pulled along if left behind). 1 = companions ride along (hidden while riding). Default 0: hiding companions is riskier during their quests and scenes.}
	GlobalVariable Property CMB_AllowCombat Auto Const Mandatory
	{1 = weapons and VATS stay usable while riding. Default 0.}
	GlobalVariable Property CMB_ForceThirdPerson Auto Const Mandatory
	{1 = switch to third person when getting on, so the bike is visible. Default 1.}
	GlobalVariable Property CMB_UseRiderPose Auto Const Mandatory
	{1 = seated riding animations while riding, when CMB_RiderPose.esp is installed. 0 = never. Default 1.}
	GlobalVariable Property CMB_CatchUpDistance Auto Const Mandatory
	{Companions running alongside further away than this are moved up behind the player. 0 = never. Default 2500.}
	GlobalVariable Property CMB_UseFuel Auto Const Mandatory
	{1 = riding burns fuel (CMB_FuelItems), from the side bag first, then the player. Default 1.}
	GlobalVariable Property CMB_FuelDistance Auto Const Mandatory
	{Distance ridden per unit of fuel, in game units (about 70 units = 1 m). Default 21000, about 300 m.}
	GlobalVariable Property CMB_FallDamageCut Auto Const Mandatory
	{Percent less fall damage while riding (0-100, 100 = none). Default 75.}
	GlobalVariable Property CMB_DismountOnHit Auto Const Mandatory
	{1 = a big enough hit from an enemy knocks you off the bike. Default 1.}
	GlobalVariable Property CMB_FreeFallDamage Auto Const Mandatory
	{Falls while riding that cost less than this percent of your max health cost nothing
	(the health comes straight back). 0 = off. Default 20.}
	GlobalVariable Property CMB_KnockOffDamage Auto Const Mandatory
	{How big: percent of your max health, from one hit or several within about a second.
	Power attacks and explosions always count. 0 = any hit. Default 10.}
	GlobalVariable Property CMB_BikeFollowsRider Auto Const Mandatory
	{1 = the worn bike hangs off the seated rider and turns with them. 0 = it stays planted on the
	ground (the older look: the rider can twist on it). Default 1.}
EndGroup

Group Optional
	Sound Property CMB_EngineStartSound Auto Const
	Sound Property CMB_EngineStopSound Auto Const
	Sound Property CMB_EngineIdleSound Auto Const
	{Looping. Crossfaded with the cruise loop by how fast you're going.}
	Sound Property CMB_EngineCruiseSound Auto Const
	{Looping.}
	GlobalVariable Property CMB_EngineVolume Auto Const
	{Engine volume, 0-100. Default 70.}
	GlobalVariable Property CMB_RidingCameraDistance Auto Const
	{How far back the third-person camera sits while riding, in game units (the game's own
	is about 150). Needs F4SE and CMB_CameraF4SE. 0 = leave the camera alone. Default 300.}
	GlobalVariable Property CMB_MaxSlope Auto Const
	{Steepest slope you can ride up, in degrees. Needs F4SE and the CMB_Slope.dll plugin.
	0 = the game's own limit. Default 60.}
	GlobalVariable Property CMB_SlopeLive Auto Const
	{What CMB_Slope.dll reads: CMB_MaxSlope while riding, 0 otherwise. Set by this script.}
EndGroup

; ---------------------------------------------------------------------------
; Constants
; ---------------------------------------------------------------------------

int Property TimerTick = 1 AutoReadOnly
int Property TimerKeys = 2 AutoReadOnly
int Property TimerDelivery = 3 AutoReadOnly
int Property TimerEngine = 4 AutoReadOnly
int Property TimerShore = 5 AutoReadOnly
int Property TimerHitGrace = 6 AutoReadOnly
float Property HitGraceTime = 3.0 AutoReadOnly
{Hits don't knock you off for this long after getting on.}
float Property ShoreDelay = 3.0 AutoReadOnly
{After a swim, the bike rolls up this long after you're out of deep water.}
float Property ShoreRetryInterval = 10.0 AutoReadOnly
int Property MaxShoreWaits = 10 AutoReadOnly
{Still in water after this many ShoreDelays (30 s): bring the bike anyway.}
float Property ShoreBikeDistance = 200.0 AutoReadOnly
{How far past the player, away from the water, the bike rolls up.}
int Property TimerReloadPose = 9 AutoReadOnly
float Property ReloadPoseDelay = 1.0 AutoReadOnly
{After loading a save mid-ride: the player's animation graph may not be ready at once.}
int Property TimerCleanup = 7 AutoReadOnly
float Property CleanupDelay = 1.5 AutoReadOnly
{After any dismount: by then a ride tick that was already running has finished.}
int Property TimerPoseRetry = 8 AutoReadOnly
float Property PoseRetryInterval = 2.0 AutoReadOnly
int Property MaxPoseRetries = 10 AutoReadOnly
string Property FootstepEvent = "FootLeft" AutoReadOnly
{Standing walk/run clips send it; the seated riding clips don't.}
float Property EngineStartLength = 2.4 AutoReadOnly
{The start sound ends on idle; the loops take over after it.}
float Property CruiseSpeed = 700.0 AutoReadOnly
{Units per second at which only the cruise loop is heard.}
float Property TickInterval = 1.0 AutoReadOnly
float Property DeliveryRetryInterval = 20.0 AutoReadOnly
float Property MountRange = 350.0 AutoReadOnly
float Property ParkSideOffset = 110.0 AutoReadOnly
float Property CallAheadDistance = 220.0 AutoReadOnly
float Property FollowerScanRange = 4000.0 AutoReadOnly
float Property MinSpeedPercent = 100.0 AutoReadOnly
float Property MaxSpeedPercent = 500.0 AutoReadOnly
float Property ParkedModelYaw = 180.0 AutoReadOnly
float Property MaxTickDistance = 5000.0 AutoReadOnly
{More than this between two ticks is a teleport (door, fast travel), not riding, so it burns no fuel.}
int Property LowFuelWarning = 3 AutoReadOnly
string Property RiderPosePlugin = "CMB_RiderPose.esp" AutoReadOnly
int Property RiderFlavorID = 0x800 AutoReadOnly
{CMB_AnimFlavorRider in CMB_RiderPose.esp.}
int Property KeysStackSize = 2 AutoReadOnly
{Two keys, so using one never empties the stack and the favorites hotkey survives.}
string Property DeepWaterMessage = "The motorbike can't go into deep water." AutoReadOnly
string Property HeadTrackingVariable = "bAllowHeadTracking" AutoReadOnly
{Behaviour graph switch for looking at people: it twists the chest, pulling the hands off the grips.}

; ---------------------------------------------------------------------------
; Runtime state
; ---------------------------------------------------------------------------

bool riding = false
bool busy = false
int engineIdle = 0
int engineCruise = 0
bool keysDelivered = false
bool riderPoseApplied = false
float playerSpeedDelta = 0.0
InputEnableLayer rideLayer
float fuelDistance = 0.0
float lastX = 0.0
float lastY = 0.0
bool hasLastPos = false
bool swimming = false
bool inWater = false
bool bikeWaitsForShore = false
int shoreWaits = 0
float swimExitX = 0.0
float swimExitY = 0.0
bool footstepsWatched = false
bool hitGrace = false
float healthMark = 1.0
bool poseRetryWaiting = false
int poseRetries = 0
bool combatHinted = false
float fallDamageDelta = 0.0
Actor[] stowedFollowers
Actor[] boostedFollowers
float[] boostedDeltas

; ---------------------------------------------------------------------------
; Lifecycle
; ---------------------------------------------------------------------------

Event OnInit()
	EnsureArrays()
	WatchSwimming()
	WatchFalls()
	TryDeliverKeys()
EndEvent

; Called by CMB_PlayerAliasScript every time a save is loaded.
Function OnGameReloaded()
	EnsureArrays()
	busy = false
	hasLastPos = false
	WatchSwimming()
	WatchFalls()
	if bikeWaitsForShore && !swimming
		StartTimer(ShoreDelay, TimerShore)
	endif
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
			; Right after a load the flavour can be refused (the graph isn't up yet),
			; so put it back on once the game is running.
			footstepsWatched = false
			StartTimer(ReloadPoseDelay, TimerReloadPose)
		endif
		; The camera setting isn't saved: a restarted game has the player's own again.
		CallCamera(true)
		SetSlopeLive(true)
		RegisterForPlayerTeleport()
		hitGrace = false
		healthMark = PlayerRef.GetValuePercentage(Health)
		WatchForHits()
		WatchFootsteps()
		StartTimer(TickInterval, TimerTick)
		; Sounds don't survive a load, and their old instance numbers mean nothing now.
		engineIdle = 0
		engineCruise = 0
		StartEngineLoops()
	endif
	RefreshHotkey()
EndFunction

; The optional F4SE scripts live on this quest too. Looking them up by name
; keeps this script compiling and running without F4SE.
Function RefreshHotkey()
	ScriptObject hotkey = CastAs("CMB_HotkeyF4SE")
	if hotkey
		hotkey.CallFunction("RegisterHotkey", new Var[0])
	endif
EndFunction

; Steeper slopes (optional, F4SE plugin CMB_Slope.dll): it watches CMB_SlopeLive and
; raises the player's slope limit while it isn't 0.
Function SetSlopeLive(bool abRiding)
	if CMB_SlopeLive
		float degrees = 0.0
		if abRiding && CMB_MaxSlope
			degrees = CMB_MaxSlope.GetValue()
		endif
		CMB_SlopeLive.SetValue(degrees)
	endif
EndFunction

; Riding camera (optional, F4SE): true = move it back, false = put it back.
; Returns true when the camera limit changed and third person needs re-entering.
bool Function CallCamera(bool abRiding)
	ScriptObject camera = CastAs("CMB_CameraF4SE")
	if !camera
		return false
	endif
	Var[] params = new Var[1]
	params[0] = 0.0
	if CMB_RidingCameraDistance
		params[0] = CMB_RidingCameraDistance.GetValue()
	endif
	if abRiding
		return camera.CallFunction("ApplyRidingCamera", params) as bool
	endif
	camera.CallFunction("RestoreCamera", params)
	return false
EndFunction

Function CallGearRestore(string asFunction)
	ScriptObject gear = CastAs("CMB_GearRestoreF4SE")
	if gear
		Var[] params = new Var[1]
		params[0] = PlayerRef
		gear.CallFunction(asFunction, params)
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
	; Claim the delivery before calling anything: OnInit, a teleport and the retry
	; timer can all get here at once, and every call below lets another one run.
	keysDelivered = true
	if PlayerRef.GetItemCount(Pipboy) > 0 && !PlayerRef.IsInInterior()
		CancelTimer(TimerDelivery)
		if !riding
			UnregisterForPlayerTeleport()
		endif
		GiveKeysIfMissing(false)
		Debug.Notification("Use the Motorbike Keys (Aid) to call your motorbike.")
		Log("Keys delivered.")
	else
		keysDelivered = false
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

; F4SE and MCM hotkeys. Menus (including the console) pause the game; dialogue
; doesn't, so check scenes too.
Function HotkeyPressed()
	if !Utility.IsInMenuMode() && !PlayerRef.IsInScene()
		ToggleRide()
	endif
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

	bool cameraMoved = CallCamera(true)
	if CMB_ForceThirdPerson.GetValue() > 0.0
		if cameraMoved
			; Coming into third person again picks up the new camera distance
			; (hidden by the fade).
			Game.ForceFirstPerson()
		endif
		Game.ForceThirdPerson()
	endif
	BikeRef.Disable()
	CallGearRestore("RememberSlot")
	ApplyRiderPose()
	EquipBike()
	ApplyControls()
	playerSpeedDelta = ApplySpeed(PlayerRef)
	ApplyFallDamageCut()
	HandleFollowersOnMount()

	riding = true
	hasLastPos = false
	combatHinted = false
	RegisterForPlayerTeleport()
	healthMark = PlayerRef.GetValuePercentage(Health)
	hitGrace = true
	StartTimer(HitGraceTime, TimerHitGrace)
	WatchForHits()
	poseRetries = 0
	poseRetryWaiting = false
	WatchFootsteps()
	SetSlopeLive(true)
	StartTimer(TickInterval, TimerTick)
	PlaySound(CMB_EngineStartSound)
	StartTimer(EngineStartLength, TimerEngine)
	Log("Mounted. SpeedMult +" + playerSpeedDelta + ", stowed " + stowedFollowers.Length + ", running " + boostedFollowers.Length)

	Game.FadeOutGame(false, true, 0.0, 0.35)
	busy = false
	if FuelEnabled()
		Debug.Notification("Fuel: " + CountFuel())
	endif
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
	elseif swimming
		busy = false
		Debug.Notification(DeepWaterMessage)
		return
	endif
	BikeRef.Disable()
	PlaceBike(CallAheadDistance, 60.0)
	BikeRef.Enable(true)
	bikeWaitsForShore = false
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
	bikeWaitsForShore = false
	; Restart the swim watch: its effect ends (not swimming) and starts again if you are.
	PlayerRef.RemoveSpell(CMB_SwimWatchAbility)
	swimming = false
	inWater = false
	WatchSwimming()
	; Clear the riding flavour even if the script lost track of it.
	if Game.IsPluginInstalled(RiderPosePlugin)
		PlayerRef.ChangeAnimFlavor()
		PlayerRef.AttemptAnimationSetSwitch()
	endif
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
	elseif aiTimerID == TimerEngine && riding
		StartEngineLoops()
	elseif aiTimerID == TimerShore
		BringBikeAfterSwim()
	elseif aiTimerID == TimerHitGrace
		hitGrace = false
	elseif aiTimerID == TimerCleanup
		CleanUpAfterRide()
	elseif aiTimerID == TimerPoseRetry
		poseRetryWaiting = false
	elseif aiTimerID == TimerReloadPose
		if riding && riderPoseApplied && !busy
			SwitchToRiderFlavor("after loading")
			WatchFootsteps()
		endif
	elseif aiTimerID == TimerTick && riding
		RideTick()
		if riding
			StartTimer(TickInterval, TimerTick)
		endif
	endif
EndEvent

Event OnPlayerTeleport()
	if riding
		hasLastPos = false
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
		AutoDismount("You leave the motorbike parked outside.", false)
		return
	elseif PlayerRef.IsInPowerArmor()
		AutoDismount("You can't ride in power armor. The motorbike is parked nearby.", false)
		return
	elseif PlayerRef.GetSitState() != 0
		AutoDismount("The motorbike is parked nearby.", false)
		return
	elseif swimming
		; Normally SetSwimming has done this already.
		DismountIntoWater()
		return
	elseif CMB_AllowCombat.GetValue() == 0.0 && PlayerRef.IsWeaponDrawn()
		; Weapons are off while riding, so this shouldn't happen; if something drew one
		; anyway, holstering is blocked too. Get off rather than stay stuck like that.
		AutoDismount("You can't ride with your weapon out.", true)
		return
	endif
	; Every call below lets other threads run, and one of them can end the ride
	; (deep water, a hit, the keys). So check again before each step that changes
	; something: a tick that carried on would put the bike back on, or move the
	; parked bike indoors.
	float stepDistance = TrackMovement()
	if !StillRiding()
		return
	endif
	if !BurnFuel(stepDistance)
		AutoDismount("Your motorbike ran out of fuel.", true)
		return
	endif
	UpdateEngineSound(stepDistance)

	; The disabled bike follows the player, so it can be dropped here at any moment.
	if !StillRiding()
		return
	endif
	ShadowPlayer()
	CatchUpFollowers()

	; Also swaps between the two bikes when a weapon is drawn or put away.
	if !StillRiding()
		return
	endif
	EquipBike()
	if !riding
		; The ride ended while the bike was going on: take it off again.
		RemoveBikeArmor()
		return
	endif
	if riderPoseApplied
		; The graph can switch it back on (dialogue, for one).
		PlayerRef.SetAnimationVariableBool(HeadTrackingVariable, false)
		if !footstepsWatched
			WatchFootsteps()
		endif
	endif
	CombatHint()
	; Damage is counted from here: what one hit, or a quick run of them, took.
	healthMark = PlayerRef.GetValuePercentage(Health)
EndFunction

; ---------------------------------------------------------------------------
; Riding setup and teardown
; ---------------------------------------------------------------------------

bool Function StillRiding()
	return riding && !busy
EndFunction

string Function GetMountBlocker()
	if PlayerRef.IsInPowerArmor()
		return "You can't ride a motorbike in power armor."
	elseif PlayerRef.IsInInterior()
		return "There's no room to ride in here."
	elseif PlayerRef.GetSitState() != 0
		return "You need to stand up first."
	elseif swimming
		return DeepWaterMessage
	elseif PlayerRef.IsWeaponDrawn()
		; Fighting controls are off while riding, so the weapon couldn't be put away:
		; you'd ride standing with it out (the weapon animations have no seated version).
		return "Put your weapon away first."
	elseif FuelEnabled() && CountFuel() < 1
		return "Your motorbike is out of fuel. It runs on Flamer Fuel (carried or in the side bag)."
	endif
	return ""
EndFunction

; Undo everything riding changed on the player and companions.
; Placing the bike is the caller's job.
Function FinishRide()
	CancelTimer(TimerTick)
	UnregisterForPlayerTeleport()

	CancelTimer(TimerEngine)
	StopEngineLoops()
	UnregisterForHitEvent(PlayerRef)
	UnregisterForAnimationEvent(PlayerRef, FootstepEvent)
	footstepsWatched = false

	RemoveBikeArmor()
	CallGearRestore("RestoreSlot")
	CallCamera(false)
	SetSlopeLive(false)
	ClearRiderPose()
	ReleaseControls()
	RemoveSpeed(PlayerRef, playerSpeedDelta)
	playerSpeedDelta = 0.0
	RemoveFallDamageCut()
	HandleFollowersOnDismount()

	if riding
		PlaySound(CMB_EngineStopSound)
	endif
	riding = false
	StartTimer(CleanupDelay, TimerCleanup)
EndFunction

; Safety net after every dismount: whatever a ride tick that was still running
; did, the bike comes off and head tracking is back on.
Function CleanUpAfterRide()
	if riding || busy
		return
	endif
	RemoveBikeArmor()
	PlayerRef.SetAnimationVariableBool(HeadTrackingVariable, true)
EndFunction

; abParkBesidePlayer: park next to the player (they're outdoors and standing).
; Otherwise the bike stays at the last outdoor spot it shadowed.
Function AutoDismount(string asMessage, bool abParkBesidePlayer)
	; Another thread may have ended the ride since the caller checked.
	if busy || !riding
		return
	endif
	busy = true
	if abParkBesidePlayer
		ParkBesidePlayer()
	else
		BikeRef.Enable()
	endif
	FinishRide()
	busy = false
	Debug.Notification(asMessage)
	Log("Auto-dismounted: " + asMessage)
EndFunction

Function ParkBesidePlayer()
	PlaceBike(0.0, ParkSideOffset)
	BikeRef.Enable()
EndFunction

Function ShadowPlayer()
	PlaceBike(0.0, ParkSideOffset)
EndFunction

; Puts the parked bike forward/right of the player, facing the way they face.
; The game's motorcycle model points along -Y, hence the half turn.
Function PlaceBike(float afForward, float afRight)
	float angle = PlayerRef.GetAngleZ()
	BikeRef.MoveTo(PlayerRef, OffsetX(angle, afForward, afRight), OffsetY(angle, afForward, afRight), 0.0, false)
	BikeRef.SetAngle(0.0, 0.0, angle + ParkedModelYaw)
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
	rideLayer.EnableSprinting(false)
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

; Percent less fall damage while riding: the bike's suspension takes the drops
; the riding speed makes you take. Exactly what was added comes off again.
Function ApplyFallDamageCut()
	float cut = CMB_FallDamageCut.GetValue()
	if cut < 0.0
		cut = 0.0
	elseif cut > 100.0
		cut = 100.0
	endif
	if cut > 0.0
		PlayerRef.ModValue(FallingDamageMod, cut)
	endif
	fallDamageDelta = cut
EndFunction

Function RemoveFallDamageCut()
	if fallDamageDelta != 0.0
		PlayerRef.ModValue(FallingDamageMod, -fallDamageDelta)
	endif
	fallDamageDelta = 0.0
EndFunction

; Two versions of the worn bike. CMB_BikeRiderArmor hangs off the rider's COM
; bone, so it turns with them when the game twists the body away from the root
; (turning on the spot, talking), but it only lines up with the seated pose.
; CMB_BikeRiderArmorFrame stands on the ground (AnimObjectA): for riding without
; the seated pose, with a weapon drawn (standing poses), or by choice.
Armor Function WantedBikeArmor()
	if riderPoseApplied && CMB_BikeFollowsRider.GetValue() > 0.0 && !PlayerRef.IsWeaponDrawn()
		return CMB_BikeRiderArmor
	endif
	return CMB_BikeRiderArmorFrame
EndFunction

Function EquipBike()
	Armor wanted = WantedBikeArmor()
	Armor other = CMB_BikeRiderArmor
	if wanted == CMB_BikeRiderArmor
		other = CMB_BikeRiderArmorFrame
	endif
	if !PlayerRef.IsEquipped(wanted)
		if PlayerRef.GetItemCount(wanted) == 0
			PlayerRef.AddItem(wanted, 1, true)
		endif
		PlayerRef.EquipItem(wanted, true, true)
	endif
	RemoveArmor(other)
EndFunction

Function RemoveBikeArmor()
	RemoveArmor(CMB_BikeRiderArmor)
	RemoveArmor(CMB_BikeRiderArmorFrame)
EndFunction

Function RemoveArmor(Armor akArmor)
	int count = PlayerRef.GetItemCount(akArmor)
	if count > 0
		PlayerRef.UnequipItem(akArmor, false, true)
		PlayerRef.RemoveItem(akArmor, count, true)
	endif
EndFunction

; ---------------------------------------------------------------------------
; Swimming, hits and fights
; ---------------------------------------------------------------------------

; The ability's effect runs while its IsSwimming condition holds. Adding it again
; does nothing, so this is safe on every load (and covers saves from before it existed).
Function WatchSwimming()
	PlayerRef.AddSpell(CMB_SwimWatchAbility, false)
EndFunction

; Called by CMB_SwimWatchEffectScript when the player starts and stops swimming.
; Shallow water doesn't count: riding through it is fine.
Function SetSwimming(bool abSwimming)
	swimming = abSwimming
	if abSwimming && riding && !busy
		DismountIntoWater()
	elseif !abSwimming
		; Where deep water ended: the bike rolls up on the far side of the player from here.
		swimExitX = PlayerRef.GetPositionX()
		swimExitY = PlayerRef.GetPositionY()
		if bikeWaitsForShore
			shoreWaits = 0
			StartTimer(ShoreDelay, TimerShore)
		endif
	endif
EndFunction

; Called by CMB_SwimWatchEffectScript on CMB_WadeWatchEffect: in water at any depth.
; Riding through shallow water is fine; this only decides when the bike comes back.
Function SetInWater(bool abInWater)
	inWater = abInWater
	if !abInWater && bikeWaitsForShore && !swimming
		; Out of the water: a few seconds on dry land, then the bike.
		StartTimer(ShoreDelay, TimerShore)
	endif
EndFunction

; Deep water ends the ride. The bike stays hidden: where it shadowed the player
; a moment ago can be mid-air (riding off a ledge into a lake), so instead it
; rolls up next to the player once they're out of the water (BringBikeAfterSwim).
Function DismountIntoWater()
	if busy || !riding
		return
	endif
	busy = true
	FinishRide()
	bikeWaitsForShore = true
	busy = false
	Debug.Notification(DeepWaterMessage)
	Log("Auto-dismounted: " + DeepWaterMessage)
EndFunction

; A few seconds out of deep water: bring the bike over, the way calling it does.
; Indoors it waits until the player is outside again.
Function BringBikeAfterSwim()
	if !bikeWaitsForShore || riding || swimming
		return
	endif
	if busy || PlayerRef.IsInInterior()
		StartTimer(ShoreRetryInterval, TimerShore)
		return
	endif
	if inWater && shoreWaits < MaxShoreWaits
		; Still wading: wait for dry land (SetInWater restarts this), checking now and then
		; in case the in-water report never comes.
		shoreWaits += 1
		StartTimer(ShoreDelay, TimerShore)
		return
	endif
	busy = true
	bikeWaitsForShore = false
	; Past the player, away from where they came out of deep water: that side is land.
	float dx = PlayerRef.GetPositionX() - swimExitX
	float dy = PlayerRef.GetPositionY() - swimExitY
	float away = Math.Sqrt(dx * dx + dy * dy)
	if away > 50.0
		BikeRef.MoveTo(PlayerRef, dx / away * ShoreBikeDistance, dy / away * ShoreBikeDistance, 0.0, false)
		BikeRef.SetAngle(0.0, 0.0, PlayerRef.GetAngleZ() + ParkedModelYaw)
	else
		PlaceBike(CallAheadDistance, 60.0)
	endif
	BikeRef.Enable(true)
	busy = false
	Log("Bike brought back after a swim (" + away + " units from the deep water, in water: " + inWater + ").")
	Debug.Notification("Your motorbike rolls up.")
EndFunction

; Hit events are one-shot: OnHit registers again for the next one.
Function WatchForHits()
	if riding && CMB_DismountOnHit.GetValue() > 0.0
		RegisterForHitEvent(PlayerRef)
	endif
EndFunction

; Only a big hit from an enemy knocks you off: a power attack, an explosion, or
; at least CMB_KnockOffDamage percent of your max health since the last tick
; (one hit, or several close together). Not in the first seconds after getting on.
Event OnHit(ObjectReference akTarget, ObjectReference akAggressor, Form akSource, Projectile akProjectile, \
		bool abPowerAttack, bool abSneakAttack, bool abBashAttack, bool abHitBlocked, string apMaterial)
	if !riding
		return
	endif
	Actor attacker = akAggressor as Actor
	if busy || hitGrace || !attacker || attacker == PlayerRef || !attacker.IsHostileToActor(PlayerRef)
		WatchForHits()
		return
	endif
	; Let the damage land before reading health.
	Utility.Wait(0.1)
	if !riding
		return
	elseif busy
		WatchForHits()
		return
	endif
	float lost = (healthMark - PlayerRef.GetValuePercentage(Health)) * 100.0
	float threshold = CMB_KnockOffDamage.GetValue()
	bool explosion = akSource as Explosion
	if abPowerAttack || explosion || threshold <= 0.0 || lost >= threshold
		Log("Knocked off: lost " + lost + "% health, power attack " + abPowerAttack + ", explosion " + explosion)
		AutoDismount("You're knocked off the motorbike.", true)
	else
		WatchForHits()
	endif
EndEvent

; Falls while riding: every one is logged (for tuning), and small ones cost
; nothing: under CMB_FreeFallDamage percent of max health comes straight back.
; Bigger ones still hurt, less by CMB_FallDamageCut.
Function WatchFalls()
	RegisterForRemoteEvent(PlayerRef, "OnPlayerFallLongDistance")
EndFunction

Event Actor.OnPlayerFallLongDistance(Actor akSender, float afDamage)
	if !riding || afDamage <= 0.0
		return
	endif
	float fraction = PlayerRef.GetValuePercentage(Health)
	if fraction <= 0.0
		return
	endif
	float percent = afDamage / (PlayerRef.GetValue(Health) / fraction) * 100.0
	float free = CMB_FreeFallDamage.GetValue()
	Log("Fall while riding: " + afDamage + " damage, " + percent + "% of max health" + Ternary(percent < free, ", given back", ""))
	if percent < free
		; Let the damage land first: restoring before it does would do nothing.
		Utility.Wait(0.2)
		PlayerRef.RestoreValue(Health, afDamage)
	endif
EndEvent

string Function Ternary(bool abCondition, string asYes, string asNo)
	if abCondition
		return asYes
	endif
	return asNo
EndFunction

; The seated clips have no footsteps; the standing ones do. Footsteps while the
; rider pose should be on mean the switch to the seated clips hasn't happened
; (seen once after getting on straight out of the water), so try it again, every
; couple of seconds, a few times at most.
Function WatchFootsteps()
	if riding && riderPoseApplied
		; Fails while the player's 3D isn't loaded; the ride tick tries again.
		footstepsWatched = RegisterForAnimationEvent(PlayerRef, FootstepEvent)
	endif
EndFunction

Event OnAnimationEvent(ObjectReference akSource, string asEventName)
	if !riding || busy || !riderPoseApplied || poseRetryWaiting || PlayerRef.IsWeaponDrawn()
		return
	endif
	if poseRetries >= MaxPoseRetries
		UnregisterForAnimationEvent(PlayerRef, FootstepEvent)
		Log("Rider pose still not showing after " + poseRetries + " tries; giving up for this ride.")
		return
	endif
	poseRetryWaiting = true
	StartTimer(PoseRetryInterval, TimerPoseRetry)
	poseRetries += 1
	SwitchToRiderFlavor("standing footsteps while riding: applying the rider pose again, try " + poseRetries)
EndEvent

; Once per fight, when weapons are off while riding: say how to get off.
Function CombatHint()
	if !PlayerRef.IsInCombat()
		combatHinted = false
	elseif !combatHinted
		combatHinted = true
		if CMB_AllowCombat.GetValue() == 0.0
			Debug.Notification("You're in a fight! Use the Motorbike Keys (or your hotkey) to get off.")
		endif
	endif
EndFunction

; The seated pose is an animation flavour: the player keeps its own archetype
; (and so every other animation). CMB_RiderPose.esp adds subgraph entries that
; also need the flavour keyword and search the CMB_Rider clip folder first.
; It's built on the player's PC (tools/rider/make_rider_plugin.py), so the
; keyword is looked up by file rather than filled in as a property.
Function ApplyRiderPose()
	if CMB_UseRiderPose.GetValue() < 1.0 || !Game.IsPluginInstalled(RiderPosePlugin)
		return
	endif
	if SwitchToRiderFlavor("getting on")
		riderPoseApplied = true
	endif
EndFunction

; Puts the rider flavour on and asks the graph to switch. Clearing it first makes
; it a change even when the save already carried the flavour.
bool Function SwitchToRiderFlavor(string asWhy)
	Keyword flavor = Game.GetFormFromFile(RiderFlavorID, RiderPosePlugin) as Keyword
	if !flavor
		return false
	endif
	PlayerRef.ChangeAnimFlavor()
	if PlayerRef.ChangeAnimFlavor(flavor)
		Log("Rider pose applied (" + asWhy + ").")
	else
		Log("ChangeAnimFlavor refused the rider flavour (" + asWhy + "; weapon out " + PlayerRef.IsWeaponDrawn() + ", 3D loaded " + PlayerRef.Is3DLoaded() + ").")
	endif
	PlayerRef.AttemptAnimationSetSwitch()
	; Looking at people twists the chest and pulls the hands off the grips.
	PlayerRef.SetAnimationVariableBool(HeadTrackingVariable, false)
	return true
EndFunction

Function ClearRiderPose()
	if riderPoseApplied
		PlayerRef.ChangeAnimFlavor() ; None clears the flavour
		PlayerRef.AttemptAnimationSetSwitch()
		PlayerRef.SetAnimationVariableBool(HeadTrackingVariable, true) ; the graph's default
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
		; Companions in power armor or in a scene (their quest, a conversation)
		; can't be tucked away safely, so they run alongside instead.
		if rideAlong && !follower.IsInPowerArmor() && !follower.IsInScene()
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
		if runner && !runner.IsDead() && !runner.IsDisabled() && !runner.IsInScene() && runner.GetDistance(PlayerRef) > maxDistance
			runner.MoveTo(PlayerRef, OffsetX(angle, -300.0, -100.0), OffsetY(angle, -300.0, -100.0), 0.0, true)
		endif
		i += 1
	endwhile
EndFunction

; ---------------------------------------------------------------------------
; Fuel
; ---------------------------------------------------------------------------

bool Function FuelEnabled()
	return CMB_UseFuel.GetValue() > 0.0
EndFunction

int Function CountFuel()
	return SideBagRef.GetItemCount(CMB_FuelItems) + PlayerRef.GetItemCount(CMB_FuelItems)
EndFunction

; Burns fuel for the distance ridden since the last tick.
; Returns false when the tank ran dry.
; Horizontal distance since the last tick; 0 for the first tick and for teleports.
float Function TrackMovement()
	float x = PlayerRef.GetPositionX()
	float y = PlayerRef.GetPositionY()
	float stepDistance = 0.0
	if hasLastPos
		float dx = x - lastX
		float dy = y - lastY
		stepDistance = Math.Sqrt(dx * dx + dy * dy)
		if stepDistance >= MaxTickDistance
			stepDistance = 0.0
		endif
	endif
	lastX = x
	lastY = y
	hasLastPos = true
	return stepDistance
EndFunction

bool Function BurnFuel(float afStepDistance)
	if !FuelEnabled()
		return true
	endif
	fuelDistance += afStepDistance

	float perUnit = CMB_FuelDistance.GetValue()
	if perUnit <= 0.0
		return true
	endif
	bool burned = false
	while fuelDistance >= perUnit
		if !ConsumeOneFuel()
			fuelDistance = 0.0
			return false
		endif
		fuelDistance -= perUnit
		burned = true
	endwhile
	if burned
		int left = CountFuel()
		if left <= LowFuelWarning
			Debug.Notification("Motorbike fuel low: " + left + " left.")
		endif
	endif
	return true
EndFunction

; Takes one unit of fuel, from the side bag first, then the player.
bool Function ConsumeOneFuel()
	int size = CMB_FuelItems.GetSize()
	int i = 0
	while i < size
		Form fuel = CMB_FuelItems.GetAt(i)
		if fuel && SideBagRef.GetItemCount(fuel) > 0
			SideBagRef.RemoveItem(fuel, 1, true)
			return true
		elseif fuel && PlayerRef.GetItemCount(fuel) > 0
			PlayerRef.RemoveItem(fuel, 1, true)
			return true
		endif
		i += 1
	endwhile
	return false
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
	float volume = EngineVolume()
	if akSound && volume > 0.0
		int instance = akSound.Play(PlayerRef)
		if instance > 0
			Sound.SetInstanceVolume(instance, volume)
		endif
	endif
EndFunction

float Function EngineVolume()
	if !CMB_EngineVolume
		return 0.7
	endif
	float volume = CMB_EngineVolume.GetValue() / 100.0
	if volume < 0.0
		return 0.0
	elseif volume > 1.0
		return 1.0
	endif
	return volume
EndFunction

; Two loops play while riding: idle and cruise, crossfaded by speed each tick.
Function StartEngineLoops()
	StopEngineLoops()
	if EngineVolume() <= 0.0
		return
	endif
	if CMB_EngineIdleSound
		engineIdle = CMB_EngineIdleSound.Play(PlayerRef)
	endif
	if CMB_EngineCruiseSound
		engineCruise = CMB_EngineCruiseSound.Play(PlayerRef)
	endif
	UpdateEngineSound(0.0)
EndFunction

Function StopEngineLoops()
	if engineIdle > 0
		Sound.StopInstance(engineIdle)
	endif
	if engineCruise > 0
		Sound.StopInstance(engineCruise)
	endif
	engineIdle = 0
	engineCruise = 0
EndFunction

Function UpdateEngineSound(float afStepDistance)
	float volume = EngineVolume()
	float load = afStepDistance / (CruiseSpeed * TickInterval)
	if load > 1.0
		load = 1.0
	endif
	if engineIdle > 0
		Sound.SetInstanceVolume(engineIdle, volume * (1.0 - 0.85 * load))
	endif
	if engineCruise > 0
		Sound.SetInstanceVolume(engineCruise, volume * load)
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
