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
	FormList Property CMB_FuelItems Auto Const Mandatory
	{What the bike burns. Flamer Fuel (000CAC78) by default; add items in xEdit to accept more.}
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
EndGroup

; ---------------------------------------------------------------------------
; Constants
; ---------------------------------------------------------------------------

int Property TimerTick = 1 AutoReadOnly
int Property TimerKeys = 2 AutoReadOnly
int Property TimerDelivery = 3 AutoReadOnly
int Property TimerEngine = 4 AutoReadOnly
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
	hasLastPos = false
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
			riderPoseApplied = false
			ApplyRiderPose()
		endif
		RegisterForPlayerTeleport()
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

	if CMB_ForceThirdPerson.GetValue() > 0.0
		Game.ForceThirdPerson()
	endif
	BikeRef.Disable()
	if PlayerRef.GetItemCount(CMB_BikeRiderArmor) == 0
		PlayerRef.AddItem(CMB_BikeRiderArmor, 1, true)
	endif
	CallGearRestore("RememberSlot")
	PlayerRef.EquipItem(CMB_BikeRiderArmor, true, true)
	ApplyRiderPose()
	ApplyControls()
	playerSpeedDelta = ApplySpeed(PlayerRef)
	HandleFollowersOnMount()

	riding = true
	hasLastPos = false
	RegisterForPlayerTeleport()
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
	endif
	BikeRef.Disable()
	PlaceBike(CallAheadDistance, 60.0)
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
	endif
	float stepDistance = TrackMovement()
	if !BurnFuel(stepDistance)
		AutoDismount("Your motorbike ran out of fuel.", true)
		return
	endif
	UpdateEngineSound(stepDistance)

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

	int armorCount = PlayerRef.GetItemCount(CMB_BikeRiderArmor)
	if armorCount > 0
		PlayerRef.UnequipItem(CMB_BikeRiderArmor, false, true)
		PlayerRef.RemoveItem(CMB_BikeRiderArmor, armorCount, true)
	endif
	CallGearRestore("RestoreSlot")
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

; abParkBesidePlayer: park next to the player (they're outdoors and standing).
; Otherwise the bike stays at the last outdoor spot it shadowed.
Function AutoDismount(string asMessage, bool abParkBesidePlayer)
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

; The seated pose is an animation flavour: the player keeps its own archetype
; (and so every other animation). CMB_RiderPose.esp adds subgraph entries that
; also need the flavour keyword and search the CMB_Rider clip folder first.
; It's built on the player's PC (tools/rider/make_rider_plugin.py), so the
; keyword is looked up by file rather than filled in as a property.
Function ApplyRiderPose()
	if CMB_UseRiderPose.GetValue() < 1.0 || !Game.IsPluginInstalled(RiderPosePlugin)
		return
	endif
	Keyword flavor = Game.GetFormFromFile(RiderFlavorID, RiderPosePlugin) as Keyword
	if flavor
		PlayerRef.ChangeAnimFlavor(flavor)
		PlayerRef.AttemptAnimationSetSwitch()
		riderPoseApplied = true
	endif
EndFunction

Function ClearRiderPose()
	if riderPoseApplied
		PlayerRef.ChangeAnimFlavor() ; None clears the flavour
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
