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
	{Looping. Crossfaded with the cruise loop by how fast you're going (with CMB_Slope.dll driving
	the engine sound, the plugin's first loop: PluginDrivesSound).}
	Sound Property CMB_EngineCruiseSound Auto Const
	{Looping. The plugin's fourth (On2000): the package's CMB_EngineCruiseLP.wav is the on-load
	2000 rpm loop since test 44.}
	GlobalVariable Property CMB_EngineVolume Auto Const
	{Engine volume, 0-100. Default 90 (70 up to test 46).}
	GlobalVariable Property CMB_RidingCameraDistance Auto Const
	{How far back the third-person camera sits while riding, in game units (the game's own
	is about 150). Needs F4SE and the CMB_Slope.dll plugin. 0 = leave the camera alone. Default 450.}
	GlobalVariable Property CMB_CameraLive Auto Const
	{What CMB_Slope.dll reads: CMB_RidingCameraDistance while riding, 0 otherwise. Set by this script.}
	GlobalVariable Property CMB_MaxSlope Auto Const
	{Steepest slope you can ride up, in degrees. Needs F4SE and the CMB_Slope.dll plugin.
	0 = the game's own limit. Default 45 (on foot the game allows 47).}
	GlobalVariable Property CMB_SlopeLive Auto Const
	{What CMB_Slope.dll reads: CMB_MaxSlope while riding, 0 otherwise. Set by this script.}
	GlobalVariable Property CMB_MaxTilt Auto Const
	{The most the bike and the rider pitch with the ground while riding, in degrees (needs
	F4SE and the CMB_Slope.dll plugin; 45 follows any slope you can climb). The parked bike
	pitches up to ParkMaxPitch and rolls up to ParkMaxRoll. 0 = always level, parked too.
	Default 45.}
	GlobalVariable Property CMB_TiltLive Auto Const
	{What CMB_Slope.dll reads: CMB_MaxTilt while riding, 0 otherwise. Set by this script.}
	GlobalVariable Property CMB_GroundNormalX Auto Const
	GlobalVariable Property CMB_GroundNormalY Auto Const
	GlobalVariable Property CMB_GroundNormalZ Auto Const
	{CMB_Slope.dll writes the ground under the player here (the normal of its plane, averaged
	over the last moments on the ground); Z is 0 while the player isn't on the ground, or
	without the plugin.}
	GlobalVariable Property CMB_ParkX Auto Const
	GlobalVariable Property CMB_ParkY Auto Const
	GlobalVariable Property CMB_ParkZ Auto Const
	GlobalVariable Property CMB_ParkAngle Auto Const
	GlobalVariable Property CMB_ParkUpX Auto Const
	GlobalVariable Property CMB_ParkUpY Auto Const
	GlobalVariable Property CMB_ParkUpZ Auto Const
	{While riding, CMB_Slope.dll writes where the bike can be parked: on the ground just ridden,
	a bike length behind the player (position, angle, and the up its wheels give it).
	UpZ is 0 when there's no such spot, or without the plugin.}
	GlobalVariable Property CMB_TrackSlope Auto Const
	{While riding, CMB_Slope.dll writes how steep (degrees) the ground here is: the slope of
	the track just ridden (about a wheelbase), and once that's 20 or more, the face's own from
	the ground's normal (riding across a face, or turned on it). 0 otherwise, or without the
	plugin.}
	GlobalVariable Property CMB_TurnRadius Auto Const
	GlobalVariable Property CMB_StandTurnRate Auto Const
	{Steering (CMB_Slope.dll reads them, the MCM sets them): the tightest turn at riding speed,
	and how fast the bike is walked round when stopped. Here only to bring old defaults up to
	date (UpgradeSettings).}
	GlobalVariable Property CMB_HeadlampMode Auto Const
	{The MCM's headlamp: 0 off, 1 on while riding, 2 on at night (19:00 to 6:30). The hotkey
	sets it to 1 or 0.}
	GlobalVariable Property CMB_HeadlampLive Auto Const
	{1 while the headlamp should be lit: CMB_Slope.dll (optional, F4SE) shows its light while
	it is. Written on getting on, every tick and on getting off.}
	Light Property CMB_HeadlampLight Auto Const
	{The headlamp's beam: a spotlight placed at the rider on getting on (the game keeps no
	add-on node of a worn mesh, test 30), enabled while the lamp is lit, and kept at the lens
	by CMB_Slope.dll (optional, F4SE). Removed on getting off.}
	Light Property CMB_HeadlampLightShadow Auto Const
	{The same, casting shadows.}
	GlobalVariable Property CMB_HeadlampShadows Auto Const
	{MCM: 1 = the shadow-casting beam is placed instead.}
	GlobalVariable Property CMB_HeadlampRefHi Auto Const
	GlobalVariable Property CMB_HeadlampRefLo Auto Const
	{The placed light's form id for CMB_Slope.dll, its high and low 16 bits (0 when there is
	none).}
	ObjectReference Property GroundProbeRef Auto Const
	{An XMarker in CMB_HoldingCell. Without the plugin, it feels for the navmesh around the
	parked bike to tilt it.}
	GlobalVariable Property CMB_RoomAskX Auto Const
	GlobalVariable Property CMB_RoomAskY Auto Const
	GlobalVariable Property CMB_RoomAskZ Auto Const
	GlobalVariable Property CMB_RoomAsk Auto Const
	GlobalVariable Property CMB_RoomAnswer Auto Const
	GlobalVariable Property CMB_RoomClear Auto Const
	{Test 41: whether a spot has room for the parked bike, asked of CMB_Slope.dll (optional, F4SE)
	before the bike is brought there (RollBikeUp, RoomAt). This script writes the spot (AskX/Y/Z,
	at the player's height, and since test 43 the heading, CMB_RoomAskAngle) and then the ask's
	number (Ask); the plugin answers in Answer (the number: room; minus it: none) and Clear (with
	room, how far below the asked Z the ground is, minus for above; with none, how far along its
	ray the nearest hit was, on the bike's 110 (test 43: a hit on a side ray of the bike-shaped box
	scaled to its length), or the ground's offset when that refused it (minus for above), exactly
	-1 with no ground within 100 of the asked Z, exactly -2 when the plugin's rays aren't working
	there, which counts as not checked, exactly -3 (test 44, the plugin's [Room] Line) when the
	line from the player to the spot is blocked: a fence or a wall between them). Not Mandatory:
	an ESP from before test 41 leaves them None, and no spot is checked.}
	GlobalVariable Property CMB_RoomAskAngle Auto Const
	{Test 43: the spot's heading, the player's GetAngleZ in degrees, written with the spot before
	the ask's number, so CMB_Slope.dll checks a bike-shaped box along it ([Room] Box: 110 fore and
	aft, 40 to the sides) instead of eight level rays 110 out (test 42: a passage under about 220
	wide never had room, even where the bike fits lengthwise). The ESP's value, -1000, is none
	written (an older script): the eight rays. Not Mandatory: an ESP from before test 43 leaves it
	None, and the spot is asked about without a heading, as before. Test 46: with room, the plugin
	may have slid the spot or turned it 90 ([Room] Slide: the box had a hit), and CMB_RoomAskX/Y and
	this then hold where it found room: read back after a room answer (RoomAt).}
	GlobalVariable Property CMB_RoomOptions Auto Const
	GlobalVariable Property CMB_RoomPitch Auto Const
	GlobalVariable Property CMB_RoomRoll Auto Const
	GlobalVariable Property CMB_RoomGround Auto Const
	{Test 46 (test 45's 12 calls, 5 fine), written by CMB_Slope.dll. Options: its [Room] keys for this
	script, bit 1 Around (the four spots around the player after the seven ahead) and bit 2 (its
	LineFallback=0: a call with no spot with room nor one to take for the most room is refused, the
	bike not brought); 0, or no plugin, is test 45's build. Pitch and Roll: with each answer, the
	ground's tilt under the parked bike's wheels at the spot with room, or at a refused one a call
	can take for the most room ([Room] ParkTilt; -1000 none), and Ground that spot's ground height
	with it; SettleBike sets the brought bike to them where it stays on the spot. Not Mandatory: an
	ESP from before test 46 leaves them None, and nothing changes.}
	GlobalVariable Property CMB_RoomAskKind Auto Const
	{2026-11-01a (test 47: a call put the bike on the very edge of a truck's hood), read by
	CMB_Slope.dll: what a room ask is, written with the spot before the ask's number on every ask
	(RoomAt), 0 included, so a 1 never carries over. 0: a spot, as before; 1: the navmesh point a
	call's snap found, asked about as a navmesh point (a level line from the player, a drop off what
	they stand on, no step test: the plugin's [Room] SnapSpot). Not Mandatory: an ESP from before
	2026-11-01a leaves it None, and no navmesh point is asked about.}
	GlobalVariable Property CMB_RiderPoseOff Auto Const
	{2026-11-01a (test 47's floating rider), written by CMB_Slope.dll ([Tilt] PoseCheck): the raw
	seconds the rider's clips have been off the seat, 0 while seated, and at a ride's start and end
	(never written with PoseCheck=0). Read at each ride tick (CheckRiderPose) and compared with
	CMB_PoseOffAfter (3.0): once it is that long, the rider pose is applied again, one more way in for
	the footstep watch's retries (the same count and gate). Not Mandatory: an ESP from before
	2026-11-01a leaves it None, and only the footstep watch retries, as in build 2026-10-31a.}
	Light Property CMB_TailLight Auto Const
	{2026-11-01a (test 47: the tail lamp "is on, but it's not producing light"; an emissive shell
	lights nothing): a shadowless red spotlight placed at the rider once CMB_Slope.dll is seen
	working, handed over and removed with the headlamp; the plugin keeps it at the tail lamp, aimed
	back and down, brighter while braking ([TailLight]).}
	GlobalVariable Property CMB_TailRefHi Auto Const
	GlobalVariable Property CMB_TailRefLo Auto Const
	{The placed tail light's form id for CMB_Slope.dll, its high and low 16 bits (0 when there is
	none), as CMB_HeadlampRefHi/Lo.}
	GlobalVariable Property CMB_TailLightMode Auto Const
	{MCM "Tail lamp lights the road": 1 = the tail light is placed (default); 0 = none, as in build
	2026-10-31a. Not Mandatory, as the three above: an ESP from before 2026-11-01a leaves them None,
	and no tail light is placed.}
	MovableStatic Property CMB_BikeView Auto Const
	{2026-11-01a (test 47: "in 1st person the bike model isn't even visible"): an unskinned copy of the
	riding bike (CMB_BikeView.nif), placed at the rider, handed over and removed with the tail light;
	CMB_Slope.dll shows it in first person only and places it every frame through the worn bike's
	per-part maps ([View]).}
	GlobalVariable Property CMB_ViewRefHi Auto Const
	GlobalVariable Property CMB_ViewRefLo Auto Const
	{The placed first-person bike's form id for CMB_Slope.dll, its high and low 16 bits (0 when there
	is none).}
	GlobalVariable Property CMB_FirstPersonBike Auto Const
	{MCM "Bike in first person": 1 = the first-person bike is placed (default); 0 = none, as in build
	2026-10-31a. Not Mandatory, as the three above: an ESP from before 2026-11-01a leaves them None,
	and no first-person bike is placed.}
	Perk Property CMB_RiderSteadyPerk Auto Const
	{Test 47: Mod Incoming Stagger x0 while riding (CMB_RiderSteady). None (an older ESP): staggered as in 2026-10-31a.}
	GlobalVariable Property CMB_RiderSteady Auto Const
	{MCM "Steady in the saddle": 1 = hits don't stagger the rider (default); 0 = as 2026-10-31a.}
	GlobalVariable Property CMB_PoseReactionWindow Auto Const
	{MCM "Pose re-check pause after a hit (s)", 3 by default (0 to 5): a standing footstep (the
	footstep watch) or a CMB_RiderPoseOff reading (CheckRiderPose) doesn't apply the rider pose again
	within this long of a hit taken or an item used, or while the stagger watch says staggered: a hit
	reaction or a stagger plays standing clips, and that isn't the pose lost. 0 = applied again on any
	standing footstep, as 2026-10-31a. Not Mandatory: None (an older ESP) reads as 0.}
	GlobalVariable Property CMB_PoseOffAfter Auto Const
	{The seconds off the seat (CMB_RiderPoseOff, the plugin's raw count) from which CheckRiderPose
	applies the rider pose again: 3.0, longer than any stagger (2 s at most) or hit reaction. Not
	Mandatory: None (an older ESP), and CMB_RiderPoseOff is None with it.}
	Spell Property CMB_StaggerWatchAbility Auto Const
	{Test 47's stagger watch: a hidden ability whose effect (CMB_StaggerWatchEffectScript) runs while
	the player is staggered (IsStaggered) and tells this script (NoteStagger); given on getting on,
	taken on getting off. Ability conditions are checked about once a second, so a shorter stagger
	may be missed: it verifies "Steady in the saddle", it doesn't measure staggers. Not Mandatory:
	None (an older ESP), no watch.}
	Sound Property CMB_EngineOn1400Sound Auto Const
	Sound Property CMB_EngineOn1700Sound Auto Const
	Sound Property CMB_EngineOn2400Sound Auto Const
	Sound Property CMB_EngineOn2800Sound Auto Const
	Sound Property CMB_EngineOn3300Sound Auto Const
	Sound Property CMB_EngineOff1400Sound Auto Const
	Sound Property CMB_EngineOff1800Sound Auto Const
	Sound Property CMB_EngineOff2300Sound Auto Const
	Sound Property CMB_EngineOff2800Sound Auto Const
	{Test 44: the nine riding loops beside the idle and the cruise (On2000) ones, on load and off
	load at the rpm in their names, looping. Played at no volume with the other two at the end of
	the start sound and handed to CMB_Slope.dll, which pitches and levels all eleven each frame
	(PluginDrivesSound); stopped again when it doesn't take them. Not Mandatory: an ESP from
	before test 44 leaves them None, and the two loops' crossfade plays, as before.}
	GlobalVariable Property CMB_SndLoop01 Auto Const
	GlobalVariable Property CMB_SndLoop02 Auto Const
	GlobalVariable Property CMB_SndLoop03 Auto Const
	GlobalVariable Property CMB_SndLoop04 Auto Const
	GlobalVariable Property CMB_SndLoop05 Auto Const
	GlobalVariable Property CMB_SndLoop06 Auto Const
	GlobalVariable Property CMB_SndLoop07 Auto Const
	GlobalVariable Property CMB_SndLoop08 Auto Const
	GlobalVariable Property CMB_SndLoop09 Auto Const
	GlobalVariable Property CMB_SndLoop10 Auto Const
	GlobalVariable Property CMB_SndLoop11 Auto Const
	GlobalVariable Property CMB_SndGen Auto Const
	GlobalVariable Property CMB_SndDriven Auto Const
	{Test 44: the engine loops handed to CMB_Slope.dll (optional, F4SE). This script writes each
	loop's instance id to SndLoop01..11 in the order of the plugin's [Sound] Loops line
	(EngineLoopCount: the idle, on load 1400, 1700, 2000 (the cruise loop), 2400, 2800, 3300, off
	load 1400, 1800, 2300, 2800), then a new number in SndGen, last: a new set of loops, or with all
	eleven 0 none (the ride is over, or the set withdrawn). The plugin answers in SndDriven: the
	number when it drives that set, minus it when it declines it (its log says why), 0 when it has
	let go. Not Mandatory: an ESP from before test 44 leaves them None, and the two loops' crossfade
	plays.}
EndGroup

; Test 47's stagger watch: CMB_StaggerWatchEffectScript calls this with true when the player is
; staggered and false when the stagger is over (the ability is on the player only while riding:
; Mount gives it, FinishRide takes it). Log only, and the reaction window's "while staggered"
; (CMB_PoseReactionWindow): it verifies "Steady in the saddle" (no line with Steady on is expected).
; 2026-11-02a (test 48: 8 staggers with Steady on, the clips back on the seat by themselves 0.3-1.1 s
; later every time): the line names the perk given (SteadyNow), the ride counts its staggers (the
; getting off's "Hit events this ride" line), and nothing is done during a stagger (a flavour switch
; there would cut its end, test 48's camera); its end's line comes StaggerOverDelay later with the
; plugin's reading of the clips (StaggerOverLine).
Function NoteStagger(bool abStaggered)
	float now = Utility.GetCurrentRealTime()
	if abStaggered
		if !riding
			return
		endif
		if staggerOverPending   ; the last one's end still to tell: told now, not with this one's clips
			staggerOverPending = false
			CancelTimer(TimerStaggerOver)
			Log("Staggered while riding: the stagger over after " + Tenths(staggerLasted) + " s; staggered again " + Tenths(now - staggeredAt - staggerLasted) + " s later.")
		endif
		staggered = true
		staggeredAt = now
		rideStaggers += 1
		Log("Staggered while riding (Steady " + SteadyNow() + "): the stagger watch saw it.")
	elseif staggered
		staggered = false
		if staggeredAt > now
			staggeredAt = now   ; an earlier session's stamp
		endif
		staggerLasted = now - staggeredAt
		if riding && CMB_RiderPoseOff
			staggerOverPending = true
			StartTimer(StaggerOverDelay, TimerStaggerOver)
		else
			Log("Staggered while riding: the stagger over after " + Tenths(staggerLasted) + " s.")
		endif
	endif
EndFunction

; 2026-11-01a, the bike's own sounds besides the engine (test 47: "currently the sound used is
; default character jump effect", "another sound would be when bike is crossing a water"): the
; rider's own jump and landing sounds muted while riding, a landing sound on the landing clips'
; first event at the plugin's level, and a water loop the plugin drives. None is Mandatory: an ESP
; from before 2026-11-01a leaves them None, and nothing plays (as the 2026-10-31a build).
Group Bike_Effects
	GlobalVariable Property CMB_FxVolume Auto Const
	{MCM "Bike effects volume", 0-100 (90; 0 none): landings and the water loop. 0x884, read by
	CMB_Slope.dll every frame for the water loop, and by this script at each landing.}
	GlobalVariable Property CMB_FxMuteRider Auto Const
	{MCM "Mute the rider's own jump and landing sounds": 1 = the player's own footstep sounds
	(AudioCategoryFSTplayer: the shoes' jump and landing sounds) muted while riding (default); 0 = as
	the 2026-10-31a build. Read on getting on.}
	GlobalVariable Property CMB_FxLandOn Auto Const
	{MCM "Landing sound": 1 = the bike's landing sound (default); 0 = none, as the 2026-10-31a build.}
	GlobalVariable Property CMB_FxWaterOn Auto Const
	{MCM "Water sound": 1 = the water loop (needs CMB_Slope.dll; default); 0 = none, as the
	2026-10-31a build. Read on getting on.}
	SoundCategory Property AudioCategoryFSTplayer Auto Const
	{Vanilla (000F5FFC): the player's own footsteps, jumps and landings; Mute() on getting on,
	UnMute() on every way off (CMB_FxMuteRider).}
	FormList Property CMB_FxLandSounds Auto Const
	{The landing set: 0 light, 1 heavy, 2 the clunk on top of a heavy one, 3 into water, 4 into
	water heavy (the game's own sound descriptors by reference).}
	FormList Property CMB_FxLandSoundsAlt Auto Const
	{The second landing set for an A/B (set CMB_FxLandPick to 1 in the console).}
	FormList Property CMB_FxWaterLoops Auto Const
	{The water loop candidates (CMB_FxWaterPick picks one, read on getting on).}
	GlobalVariable Property CMB_FxLandPick Auto Const
	{0 = CMB_FxLandSounds (default), 1 = CMB_FxLandSoundsAlt: the console's A/B of the landing set.}
	GlobalVariable Property CMB_FxWaterPick Auto Const
	{The index into CMB_FxWaterLoops of the water loop played (0 default; 0-3), read on getting on.}
	GlobalVariable Property CMB_FxWaterId Auto Const
	{0x885: the water loop's instance id for CMB_Slope.dll, written by this script on getting on (the
	loop played at no volume); 0 = none.}
	GlobalVariable Property CMB_FxDriven Auto Const
	{0x886: the plugin's answer: the id when it drives the water loop, minus it when it declines
	(its log says why).}
	GlobalVariable Property CMB_FxAir Auto Const
	{0x887: the plugin's flight state: 0 on the ground, 1 a flight of [Fx] AirMin (0.35 s) or more,
	2 for AirHold (0.3 s) after that flight's landing, then 0.}
	GlobalVariable Property CMB_FxLandSeq Auto Const
	{0x888: counts the plugin's flights (one more at each take-off past AirMin), started from the
	global's own value at each ride's start, so a save's number never repeats.}
	GlobalVariable Property CMB_FxLandLevel Auto Const
	{0x889: the landing's level 0-1 from the fall's speed (2-3: into water), written by the plugin
	through the flight and at the landing; -1 (the ESP's, no plugin, or [Fx] Land=0): no cue, this
	script's own level.}
	GlobalVariable Property CMB_FxLandPlayed Auto Const
	{0x88A: the flight whose landing sound this script played last, written by it after playing it
	(the plugin logs how long after the landing).}
EndGroup

; 2026-11-02a (test 48: "Steady in the saddle" didn't stop the staggers, the camera stuck after the
; first stimpak, the arm stretched while eating): Steady's second record and its console A/B, the
; item-use window, the camera's recovery after a use (script-only, 0x896-0x899), and the count of
; items used, for CMB_Slope.dll (fixed ID 0x893). None is Mandatory: an older ESP leaves them None,
; and each change stays off (as the 2026-11-01a build).
Group Rider_Pose_Fixes
	Perk Property CMB_RiderSteadyPerk2 Auto Const
	{Test 48: Mod Incoming Stagger x0 with two condition tabs and EPFB 0, as the game's mod_armor_LessStagger.}
	GlobalVariable Property CMB_RiderSteadyWay Auto Const
	{Test 48: which perk Steady gives: 1 = CMB_RiderSteadyPerk2 (default); 2 = the game's mod_armor_LessStagger
	(00245AFE, one step less); 0 = 2026-11-01a's CMB_RiderSteadyPerk (three tabs). None (an older ESP): 0.}
	GlobalVariable Property CMB_PoseUseWindow Auto Const
	{Test 48 (IAF's use clip cut by the Pip-Boy check, the camera stuck): no pose re-apply within this many seconds of an
	item used while riding, counted from the Pip-Boy's or favourites' close when it was used in one (an animation mod plays
	the use clip after the menus close). 0 or None = as 2026-11-01a: the item stamps the hit window at the use, and the
	Pip-Boy check ignores it.}
	GlobalVariable Property CMB_UseCameraFix Auto Const
	{Test 48: 1 = after an item's use, a camera whose switch is off or that is stuck out of 0/7/8 is entered again, then a
	notification; 0 or None = no recovery (the check line stays).}
	GlobalVariable Property CMB_RiderItemUse Auto Const
	{Test 48: 0x893, a count of the items used while riding (1-999, then 1 again), written at the use or the menu's close;
	read by CMB_Slope.dll ([Tilt] UseLetGo) to let go of the hands while the use clip plays. None: never written.}
EndGroup

; 2026-11-02a (test 48: 10 brakes for knock-over asks not answered in time): the player's combat
; state for CMB_Slope.dll (fixed ID 0x894). Not Mandatory: an older ESP leaves it None.
Group Ram_Fixes
	GlobalVariable Property CMB_RamCombat Auto Const
	{Test 48: 0x894, 1 while the player is in combat, for the plugin ([Ram] PendingFoe=2). Not Mandatory: None = never
	written.}
EndGroup

; 2026-11-02a (test 48: the landing and water sounds played but went unheard): our own sound
; records over the game's files (the switch and the three lists, script-only, 0x8AB-0x8AE) and
; the landings' loudness range (fixed ID 0x895, the plugin quotes it). None is Mandatory: an older
; ESP leaves them None, and the game's own records and the 18 dB range stay (2026-11-01a).
Group Fx_Own_Records
	GlobalVariable Property CMB_FxOwnSounds Auto Const
	{MCM "Bike sounds through the mod's own records": 1 = the landing and water sounds through our own records over the
	game's files (no static attenuation, full level out to 600 like the engine); 0 = the game's own records, as the
	2026-11-01a build. Read at each landing and on getting on.}
	GlobalVariable Property CMB_FxLandRange Auto Const
	{MCM "Landing loudness range (dB)": the softest landing this many dB under the hardest (10; 18 = the 2026-11-01a build).
	At a fixed ID, 0x895: CMB_Slope.dll's landing lines quote it.}
	FormList Property CMB_FxLandSoundsOwn Auto Const
	{Our own landing set (CMB_FxOwnSounds 1), CMB_FxLandSounds' slots: 0 light, 1 heavy, 2 the clunk, 3 into water, 4 into
	water heavy.}
	FormList Property CMB_FxLandSoundsAltOwn Auto Const
	{Our own second landing set, CMB_FxLandSoundsAlt's slots (CMB_FxLandPick 1).}
	FormList Property CMB_FxWaterLoopsOwn Auto Const
	{Our own water loops, CMB_FxWaterLoops' slots (CMB_FxWaterPick picks one, read on getting on).}
EndGroup

; 2026-11-06a (test 49's answer): the rider's two fixes (script-only globals 0x8B5, 0x8B6) and the
; sound's (the landings without metal, 0x8B7-0x8B9; the water loop's choice at the fixed ID 0x8B4,
; which the plugin reads too; the mod's own wet-road loop 0x8A9). None is Mandatory: an older ESP
; leaves them None, and each stays as the 2026-11-02a build.
Group Rider_Fixes_51
	GlobalVariable Property CMB_KnockOffPower Auto Const
	{MCM "Power attacks throw you off": 1 = every power attack knocks you off (the 2026-11-02a build);
	0 (the default) = a power attack is a hit like any other, under Big hit's rule. Explosions always
	do. None (an older ESP) = 1.}
	GlobalVariable Property CMB_RiderUseOwn Auto Const
	{Console: 1 (the default) = only the player's own item uses are watched (the favourites through
	CMB_HotkeyF4SE), so another mod's dummy potion isn't read as one; 0 or None = every potion equipped,
	as the 2026-11-02a build.}
EndGroup
Group Fx_Fixes_51
	GlobalVariable Property CMB_FxLandDull Auto Const
	{MCM "Landing sounds without metal": 1 (the default) = CMB_FxLandSoundsDull: a tyre thump, on big
	drops a heavy dull thud under it; into water a splash, on big drops a heavier one with a thud.
	0 or None = the 2026-11-02a build's sets (a metal clunk on big drops). Read at each landing.}
	GlobalVariable Property CMB_FxThudDb Auto Const
	{Console: the dull set's thud on big drops, this many dB under the landing's level (-11). Unused
	with CMB_FxLandDull 0.}
	FormList Property CMB_FxLandSoundsDull Auto Const
	{The landings without metal (CMB_FxLandDull 1): 0 light, 1 heavy, 2 the PA dirt thud, 3 into water,
	4 into water heavy, 5 the PA water thud.}
	GlobalVariable Property CMB_FxWaterLoop Auto Const
	{MCM "Water sound loop": 0 = the spray, as the 2026-11-02a build (CMB_FxWaterPick); 1 = the churn;
	2 (the default) = the mod's own wet road. At a fixed ID, 0x8B4: CMB_Slope.dll reads it for the
	loop's trim and its line. Read on getting on.}
	Sound Property CMB_FxWaterRoad Auto Const
	{0x8A9 CMB_FxWaterRoadLPSD, the mod's own wet-road loop (CMB_FxWaterLoop 2).}
EndGroup

; 2026-11-07a (the customisation build, C1): the Customise session at the bike, the field kit and the
; looks (badges on both tank sides and the rear fender, the paint, the mirrors). The records follow
; tools/esp-generator/look_options.json. None is Mandatory: an older ESP leaves them None, and then
; there is no Customise button and the bike looks as the 2026-11-06a build.
Group Look_C1
	Armor Property CMB_BikeLook Auto Const
	{0x8CE, the bike's look as a playable item (slot 57, the five look attach points): held only
	while you customise, so the armour menu lists it. None = no Customise.}
	GlobalVariable Property CMB_LookCode Auto Const
	{At a fixed ID, 0x8AF: CMB_Slope.dll reads it for the worn and first-person bikes' mirrors. Bits
	0-1 the mirror (0 none, 1 stock, 2 under the bars egg, 3 under the bars D), bit 2 set (a choice
	was made), bits 3-6 the rim style (2026-11-08a: 0 the cast rim, 1-7 the styles, LookRimStyle),
	bits 7-8 kept for later builds. 0 = the plugin's own [Look] Mirrors. Written only by ApplyLook.}
	GlobalVariable Property CMB_LookOn Auto Const
	{MCM "Customise at the bike": 1 (the default) = the parked bike's menu has Customise and the
	chosen look is put on every bike; 0 or None = no button, nothing attached on getting on, the
	parked and first-person bikes back to stock, CMB_LookCode 0 (the 2026-11-06a build).}
	GlobalVariable Property CMB_LookFree Auto Const
	{MCM "Free customising (no field kit, no cost)": 1 shows the MCM's dropdowns per slot; 0 (the
	default) hides them. The MCM's "Apply the look" applies either way.}
	GlobalVariable Property CMB_Look_TankL Auto Const
	{The left tank badge: an index into CMB_LookOptions_TankL (0 = stock, the winged wheel).}
	GlobalVariable Property CMB_Look_TankR Auto Const
	{The right tank badge: an index into CMB_LookOptions_TankR; 17 (the default) = "Same as the left",
	resolved wherever a look is composed. Any other right option ends the link; 17 restores it.}
	GlobalVariable Property CMB_Look_Fender Auto Const
	{The rear fender badge: an index into CMB_LookOptions_Fender (0 = none, the patch invisible).}
	GlobalVariable Property CMB_Look_Paint Auto Const
	{The paint: an index into CMB_LookOptions_Paint (0 = Factory, the oxblood; 44 the colour-index
	test).}
	GlobalVariable Property CMB_Look_Mirrors Auto Const
	{The mirrors: an index into CMB_LookOptions_Mirrors (0 stock, 1 under the bars egg, 2 under the
	bars D, 3 none).}
	GlobalVariable Property CMB_LookFactionSet Auto Const
	{MCM "Faction set" (0 = none, 1-11): at "Apply the look" sets the paint, both tank badges (the
	right following) and the fender badge to one faction's, then goes back to 0.}
	GlobalVariable Property CMB_KitMode Auto Const
	{MCM "Field kit": 0 (the default) = automatic (2026-11-09a, [Look] KitHeld: the armour bench, then
	the game's own; the one that worked is remembered in CMB_KitWorked), 1 the toolbox, 2 the toolbox
	with the armour bench's keyword (tests: the toolbox can't be sat in), 3 the armour bench, 4 the
	game's armour bench (WorkbenchArmorA).}
	GlobalVariable Property CMB_KitWorked Auto Const
	{Console: the field kit mode automatic found working (-1, the default, = none yet: it starts at
	the armour bench; a 1 or 2 from an older build is forgotten).}
	GlobalVariable Property CMB_KitBagLink Auto Const
	{MCM "Parts from the side bag": 1 (the default) = outside your settlements the field kit counts the
	side bag's components; 0 = only yours (and a settlement's workshop).}
	FormList Property CMB_LookCategories Auto Const
	{The five option lists in slot order (0 TankL, 1 TankR, 2 Fender, 3 Paint, 4 Mirrors); in each, an
	option's index is the CMB_Look_<slot> value.}
	Furniture Property CMB_FieldKit Auto Const
	{0x8CF, kit mode 1: the toolbox (the game's by path) with an armour bench's data and our keyword.}
	Furniture Property CMB_FieldKitArmorKw Auto Const
	{0x8D0, kit mode 2: the same with the armour bench's own keywords too (a test of the menu's list).}
	Furniture Property CMB_FieldKitBench Auto Const
	{0x8D1, kit mode 3: the armour bench's model by path, its own marker and keywords plus ours.}
	MovableStatic Property CMB_FieldKitBox Auto Const
	{0x8D2, the toolbox at the bench's foot in kit mode 3.}
	Keyword Property WorkshopItemKeyword Auto Const
	{054BA6: a kit in one of your settlements is linked to its workshop with it (and the next).}
	Keyword Property LinkedWorkbenchContainerKeyword Auto Const
	{1D1BEF: the bench's container link (the workshop's, or the side bag's elsewhere).}
	Keyword Property LocTypeWorkshopSettlement Auto Const
	{083C9A: a settlement's location.}
	Quest Property WorkshopParentQuest Auto Const
	{02058E WorkshopParent: its GetWorkshopFromLocation finds the settlement's workshop.}
	ActorValue Property WorkshopPlayerOwned Auto Const
	{00033C: a workshop the player owns.}
	Sound Property DRScToolboxBOpen Auto Const
	{1B0652: the toolbox opening.}
	int[] Property LookSetPaint Auto Const
	{Per faction set (index = CMB_LookFactionSet, 0 unused): its Paint index.}
	int[] Property LookSetTank Auto Const
	{Per faction set: the left tank's index of its badge (the right follows: 17).}
	int[] Property LookSetFender Auto Const
	{Per faction set: the fender's index of the same badge.}
	string[] Property LookKeys Auto Const
	{"<slot>:<key>" for every option, slot-major in slot order (the log's names; look_options.json).}
	int[] Property LookSlotStart Auto Const
	{Each slot's first index in LookKeys (five entries).}
EndGroup

; 2026-11-08a (C2): rims, tyres, the paint's hue, the plates (look_options.json's entries "since"
; 2026-11-08a: slots 5-10 Rims, Tyres, Plate, PlateText, PlateInk, PlateBack). None is Mandatory:
; an older ESP leaves them None, and then the bike looks as the 2026-11-07a build.
Group Look_C2
	GlobalVariable Property CMB_Look_Rims Auto Const
	{0xA1B: the rims, an index into CMB_LookOptions_Rims (0 = stock, the cast rims; 1-5 a cast
	finish, 6-47 a style and finish).}
	GlobalVariable Property CMB_Look_Tyres Auto Const
	{0xA1C: the tyres (0 black, as they came; 1 whitewall, 2 red line).}
	GlobalVariable Property CMB_Look_Plate Auto Const
	{0xA1D: the licence plate's design (0 = stock, the plain plate; 1-12 the designs).}
	GlobalVariable Property CMB_Look_PlateText Auto Const
	{0xA1E: the plate's text (0 = the plate's own, 1 none, 2-61 the texts; 48-61 crude).}
	GlobalVariable Property CMB_Look_PlateInk Auto Const
	{0xA1F: the plate's letters' colour (0 = the plate's own, 1-16 the colours).}
	GlobalVariable Property CMB_Look_PlateBack Auto Const
	{0xA20: the plate's background colour (0 = the plate's own, 1-16 the colours).}
	GlobalVariable Property CMB_LookHue Auto Const
	{0xA18, MCM "Paint hue" (0-359, default 210): the Free colour paint's hue (Paint 45 only).}
	GlobalVariable Property CMB_LookShade Auto Const
	{0xA19, MCM "Paint shade" (0 deep, 1 normal (the default), 2 light, 3 pastel).}
	GlobalVariable Property CMB_LookPlateCrude Auto Const
	{0xA1A, MCM "Crude plate texts" (1, the default, = offered; 0 = the crude recipes hidden and a
	plate wearing one shows its own text).}
	int[] Property LookRimStyle Auto Const
	{Per Rims option: 0 the cast rim, 1-7 the styles (CMB_LookCode bits 3-6).}
	int[] Property LookTextCrude Auto Const
	{Per PlateText option: 1 a crude text, else 0.}
	int[] Property LookPlateOwnText Auto Const
	{Per Plate option: its own text's PlateText index (1 = None).}
	int[] Property LookSetPlate Auto Const
	{Per faction set: its Plate index (-1 unchanged).}
EndGroup

; 2026-11-09a (test 50's answer): the Pip-Boy's flag for the first-person tip (0xBF2, which CMB_Slope.dll reads too) and
; the gentle wet-road loop (0xBF3). None is Mandatory: an older ESP leaves them None (2026-11-08a).
Group Fixes_54
	GlobalVariable Property CMB_ViewMenu Auto Const
	{1 while the Pip-Boy is open on the bike, else 0: CMB_Slope.dll's [View] TipMenu gives no tip then. At a fixed ID,
	0xBF2. None = 2026-11-08a.}
	Sound Property CMB_FxWaterRoadSoft Auto Const
	{0xBF3 CMB_FxWaterRoadSoftLPSD, the gentle wet-road loop (CMB_FxWaterLoop 3). None: 3 plays the wet road (2).}
EndGroup

; 2026-11-09a, test 51's fixes: the plugin's [Look] switches for this script (0xBF4) and the game's armour bench (field kit
; mode 4). None = 2026-11-09a as of t54-merge.
Group Fixes_55
	GlobalVariable Property CMB_LookOptions Auto Const
	{CMB_Slope.dll's [Look] switches (bits 1 FastMount, 2 KitHeld, 4 ParkedReload, 8 PaletteIndex, 16 MountGuard, 32 HueFree;
	64 the plugin writes the worn bike's colours; since 2026-11-10a 128 KitStash, 256 KitRetry, 512 MountEarly, 1024
	WornColoursFirst, 2048 HueSwap). At a fixed ID, 0xBF4; 4031 in the plugin (63 in 2026-11-09a's).}
	Furniture Property WorkbenchArmorA Auto Const
	{Fallout4.esm 0x12EA9B, the game's armour bench: field kit mode 4. None: no mode 4.}
EndGroup

; 2026-11-10a, test 52's fixes: CMB_Slope.dll's word to the scripts. None = 2026-11-09a.
Group Fixes_56
	GlobalVariable Property CMB_RiderQuickUse Auto Const
	{0xBF5: count * 16 + slot of a potion's quickkey the plugin took at speed (QuickUse); CMB_HotkeyF4SE uses the item.}
	GlobalVariable Property CMB_RideReady Auto Const
	{0xBF6: 1 when the ride's worn bike is held and coloured and the rider seated (RideReady); Mount fades in on it.}
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
float Property MaxSettleDistance = 400.0 AutoReadOnly
{The parked bike snaps to walkable ground, unless that's farther than this.}
float Property SpotSettleMax = 30.0 AutoReadOnly
{Test 44: called by Sanctuary's houses, the bike was checked with room at a spot and then moved
about 250 by SettleBike's snap to the nearest navmesh (MaxSettleDistance 400), into a hedge. The
brought bike at a spot the plugin found room at (its ground known from CMB_RoomClear) keeps the
snap only if it lands within this of the checked spot's ground; farther, the snap is undone: the
bike is put back on the checked spot, level on its ground (the smaller change than trying the
next spot, which would need a snap per spot; the spots after it were not the plugin's choice).
Each such settle is logged ("The bike settled N from the checked spot"). 0: the snap taken as
far as MaxSettleDistance, as in test 44's build. Test 47: with the plugin's [Room] SnapNext
(CMB_RoomOptions bit 8; test 46's calls onto a wrecked sedan and a truck, the snaps 89 and 207)
a spot with room whose snap would go farther than this is not walkable, and the next spot is asked
(PickBikeSpot, SnapOff): the putting back is left for when no other spot passes.}
float Property SpotSnapReach = 300.0 Auto
{2026-11-01a (the plugin's [Room] SnapSpot, CMB_RoomOptions bit 16; test 47's call from on top of the
red truck: no spot passed, spot 10 had room on the hood, its navmesh snap 129 from it, and the bike was
put back on the hood's edge): when nothing passes, the place the first such spot's navmesh snap found
is asked about as a navmesh point (CMB_RoomAskKind 1) before that spot is taken as before, if it lies
over SpotSettleMax and at most this far from the spot (test 46's snaps were 89 and 207, test 47's 129).}
float Property ParkBackWithin = 136.0 AutoReadOnly
{Test 47 (the plugin's [Room] ParkCheck, CMB_RoomOptions bit 4; test 46: got on facing a house's
window at point blank and off 2 s later, and the bike went in beside the worn one, through the
window): a ride that moved the player less than this from where they got on (about the bike's
wheelbase, its axles 136.3 apart) puts the bike back where it stood before getting on, as it
stood (ParkWhereItStood). Not with the player standing where it stood (ParkBackFore,
ParkBackSide).}
float Property ParkBackFore = 128.0 AutoReadOnly
{Review of test 47's build (ParkWhereItStood): a short ride toward where the parked bike stood
(got on from 100 beside it, 100 ridden its way) put it back on the player. It goes back only if
the player is at least this far from where it stood along its heading (the plugin's [Room]
Fore, 110, and the player's capsule radius, 18), or ParkBackSide across it, as the plugin's
Slide keeps its box off the player; else its spot is asked about (ParkChecked).}
float Property ParkBackSide = 58.0 AutoReadOnly
{Across the bike's heading, as ParkBackFore along it (the plugin's [Room] Side, 40, and the
capsule radius, 18).}
float Property MaxGroundStep = 30.0 AutoReadOnly
{The ground under the player, carried over to the bike beside them, may be this much
higher or lower there; more and the bike is parked level at the player's height (one
contact normal, carried 110 units, is no good on rock or at a curb: test 7).}
float Property ParkMaxRoll = 10.0 AutoReadOnly
{The parked bike leans sideways at most this much...}
float Property MaxDismountSlope = 45.0 AutoReadOnly
{Getting off is refused on ground steeper than this: no getting off anywhere you couldn't
stand (walking tops out at 47). Test 9 got off on a 60 deg rock face; test 13, with 50 here,
on 47 and 49 deg ones.}
float Property ParkMaxPitch = 45.0 AutoReadOnly
{...and pitches at most this much: the same 45 CMB_Slope.dll parks on (test 11: a 30 here
left a bike on a 45 deg track spot floating at one end).}
float Property ProbeAlong = 70.0 AutoReadOnly
{Without the plugin, the navmesh is felt for this far in front of and behind the parked
bike's middle (it's about 200 long)...}
float Property ProbeAcross = 35.0 AutoReadOnly
{...and this far to each side (it's about 75 wide).}
float Property ProbeTolerance = 50.0 AutoReadOnly
{A probe the navmesh pulls further sideways than this says nothing about the ground there.}
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
int Property TimerPipboyCheck = 12 AutoReadOnly
float Property PipboyCheckDelay = 0.6 AutoReadOnly
{2026-11-01a (test 47's stim "skirt"): the plugin's reading of the clips is looked at this long
after the Pip-Boy closes while riding (PipboyPoseCheck)...}
float Property PipboyPoseOff = 0.3 AutoReadOnly
{...and over this many seconds off the seat (CMB_RiderPoseOff) applies the rider pose again at once.}
float Property TailRetireAfter = 2.5 AutoReadOnly
{2026-11-01a: an old tail light is deleted this long after its handover (the headlamp's 2.5 s)...}
float Property ViewRetireAfter = 4.0 AutoReadOnly
{...and an old first-person bike this long: past the plugin's [View] HandoverTime (1.0 s), which
keeps the old one shown until the new one has had its 3D that long.}
float Property StaggerHoldMax = 10.0 AutoReadOnly
{2026-11-01a: the stagger watch's "staggered" holds the pose's re-checks off at most this long (a
stagger lasts 2 s at most): an end the watch never told can't hold them off for the ride.}
string Property PipboyMenuName = "PipboyMenu" AutoReadOnly
string Property FavoritesMenuName = "FavoritesMenu" AutoReadOnly
{The two menus logged while riding (test 47: an item used from either), watched only then.}
float Property EngineStartLength = 2.4 AutoReadOnly
{The start sound ends on idle; the loops take over after it.}
float Property CruiseSpeed = 700.0 AutoReadOnly
{Units per second at which only the cruise loop is heard.}
bool Property PluginDrivesSound = true AutoReadOnly
{Test 44: true: with CMB_Slope.dll (F4SE) and an ESP that has the CMB_Snd globals, eleven engine
loops play from the end of the start sound (the idle and cruise ones as before, nine more at no
volume) and are handed to the plugin, which sets each one's pitch and level every frame from an
rpm, gear and load model of the bike's speed and the forward key (its [Sound] section); since test
46 the plugin puts the MCM's engine volume in their levels too (BSSoundHandle::SetVolume, the value
Sound.SetInstanceVolume sets), so the script makes no call on them while it offers them or the
plugin drives them (UpdateEngineSound). Without the plugin, with an
older ESP, or when the plugin declines them or lets go of them (its log says why), the idle and
cruise loops play crossfaded by speed once a tick, as before. False: that crossfade only, as before
test 44. A script constant, as CheckBikeSpot is.}
int Property EngineLoopCount = 11 AutoReadOnly
{The loops handed over, in the order of the CMB_SndLoop globals and the plugin's [Sound] Loops
line: 0 the idle (860 rpm), 1-6 on load (1400, 1700, 2000, 2400, 2800, 3300), 7-10 off load
(1400, 1800, 2300, 2800). The cruise loop is number 3 (On2000).}
int Property CruiseLoop = 3 AutoReadOnly
int Property MaxSoundId = 16777216 AutoReadOnly
{2^24: a float holds every whole number below it exactly, so a larger instance id can't be written
to a global; the loops aren't handed over then, and the crossfade plays.}
float Property SoundAnswerWait = 0.5 AutoReadOnly
{The plugin's answer to a new set of loops is waited for this long, polled every SoundPollInterval:
counted polls, a frame or more each, so the plugin gets ten frames even through a slow one. It
answers within a frame or two; none in this long means no plugin (or one from before test 44), and
the crossfade plays.}
float Property SoundPollInterval = 0.05 AutoReadOnly
bool Property StopEngineAtDeath = true AutoReadOnly
{Test 44's audit of the ways a ride ends: a death ends in a load, which stops every sound, but till
then the engine idled on beside the body through the death camera. True: the ride tick that finds
the rider dead stops the engine loops (nothing else: the load undoes the rest). False: they play on
until the load, as before test 44.}
float Property TickInterval = 1.0 AutoReadOnly
float Property DeliveryRetryInterval = 20.0 AutoReadOnly
float Property MountRange = 350.0 AutoReadOnly
float Property ParkSideOffset = 110.0 AutoReadOnly
float Property CallAheadDistance = 220.0 AutoReadOnly
bool Property CheckBikeSpot = true AutoReadOnly
{Test 41: the bike brought from Diamond City's door stood in the gate's chain-link fence each
time (191-452 units from the door): RollBikeUp put it 220 ahead and 60 to the right of the
player with no look at what was there. True: the BikeSpots are tried in order and the first
with room is taken, CMB_Slope.dll saying which have it (the CMB_Room globals; without the
plugin, or an older ESP, no answer comes and the first spot is taken as before). False: the
first spot, as before test 41. A script constant, not a GlobalVariable: it's a developer's
switch for comparing builds, nothing a player sets, and a global would need the generator and
the MCM to know it.}
int Property BikeSpots = 7 AutoReadOnly
{The spots tried for the brought bike, in order (SpotForward, SpotRight): 220 ahead and 60
right (the old spot, so nothing changes where it has room), the same 60 left, 150 ahead and 60
right or left (nearer: a gate's fence runs across the way), 300 ahead and 60 right or left
(past a narrow spot), and 100 straight ahead (as close as the bike stands without being under
the player's nose); then, for a bring from a door, where the bike waited: the rider parked it
there, so it's always acceptable.}
int Property AroundSpots = 4 AutoReadOnly
{Test 46 (test 45: every spot was ahead, where the fence or the wall the player faced was): with
the plugin's [Room] Around (CMB_RoomOptions bit 1), when none of the BikeSpots has room these are
asked too: 100 behind and 110 right (beside the player, its nose 10 ahead of them), the same on
the left, 120 behind turned across the player's heading (SpotTurn), and 220 straight behind.}
float Property RoomAnswerWait = 0.5 AutoReadOnly
{One spot's answer is waited for this long, polled every RoomPollInterval. The plugin answers
within a frame or two; none in this long means no plugin, and the first spot is taken untested,
as before test 41.}
float Property RoomPollInterval = 0.05 AutoReadOnly
bool Property RetryUncheckedSpot = true AutoReadOnly
{Test 43 (the user's thought on test 42's build): the first spot answered "not checked"
(CMB_RoomClear -2: the plugin's test ray hasn't passed yet, right after a load) is asked about
again once, RoomRaysWait later, from where the player is by then; the plugin tries its test ray
again for that ask ([Room] RaysRetry). Not checked again: a bring leaves the bike where it
waited (the rider parked it there), a call takes the first spot untested. False: the first spot
untested at once, as before test 43. Not seen in a test yet (test 42: the rays answered at once
after each of four loads).}
float Property RoomRaysWait = 1.5 AutoReadOnly
{The wait before that second ask: about three times the 0.49 s the plugin's test ray came after
its first frame with the player in test 42. Without the plugin no -2 comes, so that case still
costs RoomAnswerWait.}
bool Property CallTakesBestSpot = true AutoReadOnly
{Test 43 (the user's thought on test 42's build): a call with room at none of the BikeSpots takes
the one with the most room, the largest CMB_RoomClear among the spots refused for a hit along a
ray (or the ground under 100 below, which SettleBike puts the bike on), rather than the first:
outside Diamond City's gate the first is the fence. A bring still leaves the bike where it
waited. False: the first spot, as before test 43. Test 45's review: a spot refused for its ground
below had no box checked, and on an open slope it was the one taken; the plugin (with [Room] Line)
now checks the box at such a spot too, its CMB_RoomClear the box's nearest hit when that is less,
so the spot taken here has always been looked at.}
float Property FollowerScanRange = 4000.0 AutoReadOnly
float Property MinSpeedPercent = 100.0 AutoReadOnly
float Property MaxSpeedPercent = 500.0 AutoReadOnly
float Property ParkedModelYaw = 180.0 AutoReadOnly
float Property MaxTickDistance = 5000.0 AutoReadOnly
{More than this between two ticks is a teleport (door, fast travel), not riding, so it burns no fuel.}
float Property FastTravelMinutes = 5.0 AutoReadOnly
{On the tick that finds the player indoors or in a walled town, more game minutes than this
since the last tick outdoors is a fast travel, fewer a door (test 39: a fast travel into Diamond
City said the bike was parked outside, while it stayed where the fast travel set off, at Sanctuary). A
tick is a second, 20 game seconds at the game's timescale of 20; a fast travel takes game hours.}
float Property DoorBringDistance = 6000.0 AutoReadOnly
{The bike left outside a door is brought to the player who comes out within this of it (about
85 m, a cell and a half): the same door, or another of the same building or town. Farther off
it stays there; calling it still works.}
int Property TimerTeleport = 10 AutoReadOnly
float Property TeleportCheckInterval = 0.5 AutoReadOnly
{Test 40: OnPlayerTeleport comes while the player is still where the teleport started, and they're
moved seconds later, during the loading screen (Diamond City: the bike was brought to the gate on
the way in and never on the way out). So the event only notes the teleport, and what it means is
decided once it's over: when the loading screen closes, or, with none seen, when this timer, which
looks every half second (a tick's worth of riding), finds the player moved.}
int Property TeleportSettleChecks = 3 AutoReadOnly
{No loading screen seen and the player not moved after this many looks (1.5 s): it's decided
anyway. A script's MoveTo is over within a frame or two.}
int Property TeleportMaxChecks = 120 AutoReadOnly
{It's decided after this many looks whatever else (60 s of play): a loading screen whose close
never came.}
float Property TeleportMoved = 1500.0 AutoReadOnly
{Moved: farther than this from where the event saw the player (riding covers at most about 900 units
between two looks), or into another worldspace, or in or out of doors. Doors and fast travel are
much farther.}
string Property LoadingMenuName = "LoadingMenu" AutoReadOnly
int Property TimerBusyWatch = 11 AutoReadOnly
float Property BusyWatchTime = 10.0 AutoReadOnly
{Test 40: the keys used outside Diamond City left no line, and a busy left set would have turned
them away in silence. Busy held longer than this is logged, with who holds it, and let go. Getting
on takes about a second; the longest hold seen, bringing the bike with its navmesh probes while a
loading screen was up (test 40, 15:33:04-08), took 4 s. A menu seen open meanwhile starts the
count again: Utility.Wait doesn't run in menus, so the holder can be waiting in one. Off with
WatchBusy 0.}
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
; Test 44, the loops handed to the plugin (PluginDrivesSound): all eleven instance ids in the
; CMB_SndLoop globals' order (the idle's and the cruise's too), None while only those two play.
int[] engineLoops
; StopEngineLoops counts here: a start or a hand-off that finds it changed was overtaken by a ride
; end or a newer start, whose stop has taken the loops back.
int engineSet = 0
int sndGen = 0         ; the last number written to CMB_SndGen
int offeredGen = 0     ; the number the CMB_Snd globals hold a set of loops for (0: none)
bool soundDriven = false
int drivenGen = 0      ; the set the plugin drives while soundDriven
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
; 2026-11-02a (test 48; pose.md 1.4, 2.4, 2.5, 4.2). Steady: the perk this script gave (None: none; a
; perk on the player it didn't give is never taken off), and its "already on the player" line said.
; The ride's hit events, power attacks and staggers (log only: the getting off's "Hit events this
; ride" line).
; The use window: real time an item's use clip can start (the use, or the Pip-Boy's or favourites'
; close when it was used in one), what it was, the item whose "left alone" line was logged; an item
; used in a menu, timed from its close; a menu of the two open. The camera check after a use: its
; tries while a menu is open, the view entered again at the last check (looked at again
; UseCameraRecheck later), the notification shown this ride. The stagger's end, its line still to
; come (StaggerOverLine). First person's footsteps line said this ride.
Perk steadyGiven
bool steadyKeptSaid = false
int rideHits = 0
int ridePowerHits = 0
int rideStaggers = 0
float itemAt = -100.0
string itemWhat = ""
float itemLeft = -200.0
bool itemInMenu = false
bool riderMenuOpen = false
int useCameraTries = 0
bool useCameraFixed = false
bool useCameraNoted = false
float staggerLasted = 0.0
bool staggerOverPending = false
bool firstFootSaid = false
float hitLoggedAt = -100.0   ; test 47: the last "Hit while riding" line (one a second at most)
float mountedAt = 0.0   ; test 47: real time of the ride's start (the engine's hand-over line says how long it took)
string mountedHow = "getting on"   ; ...and what started it: getting on, or a load into a ride
; Test 47 (the rider "like a skirt" when hit): the reaction window (CMB_PoseReactionWindow). Real
; time of the last hit taken or item used while riding, which it was, and the stagger watch's word;
; the footstep watch and CheckRiderPose leave standing clips alone within the window, one line a
; reaction (reactionLeft: the reaction whose line was logged).
float reactionAt = -100.0
string reactionWhat = "a hit"
float reactionLeft = -200.0
bool staggered = false
float staggeredAt = 0.0
float itemLoggedAt = -100.0   ; the last "Used ... while riding" line (one a second at most)
int poseRetries = 0
bool combatHinted = false
float fallDamageDelta = 0.0
float groundX = 0.0
float groundY = 0.0
float groundZ = 1.0
; Saves from before a default changed get the new one once, if they still have the old.
int settingsVersion = 0
WorldSpace lastWorld          ; InClosedWorld's answer, kept until the worldspace changes
bool lastWorldClosed = false
float lastOutdoorTime = 0.0   ; game days, at the last ride tick that found the player outdoors
; The ride ended through a door: the bike waits outside it, in this worldspace, and comes to
; the player when they're out again near it (BringBikeFromDoor).
bool bikeAtDoor = false
WorldSpace doorWorld
; Test 40's fast travel into Diamond City put the bike beside the player in the town. Now it's
; marked as waiting at a door all the same, in the open worldspace of the last tick outdoors, and
; brought from wherever it is the next time the player is outdoors there (LeaveBikeOutside).
bool bikeInside = false
WorldSpace lastOpenWorld      ; the worldspace of the last ride tick that found the player outdoors
; A teleport OnPlayerTeleport noted and HandleTeleport hasn't handled yet: where the event saw the
; player (not known after a load: the first look decides), when, and how many looks since.
bool teleportPending = false
bool teleportFromKnown = false
WorldSpace teleportFromWorld
bool teleportFromInside = false
float teleportFromX = 0.0
float teleportFromY = 0.0
float teleportAt = 0.0        ; real seconds
int teleportChecks = 0
bool teleportSkipLogged = false
bool noCellLogged = false
; The loading screen (OnMenuOpenCloseEvent): up now, and seen up while the teleport was pending.
bool loadingOpen = false
bool loadingSeen = false
; Test 41's switch: true decides a teleport in OnPlayerTeleport itself, as up to test 40
; (DecideTeleportsAtOnce, from the console). False, the default, waits for it to be over.
bool teleportsAtOnce = false
; Who holds busy, and since when (real seconds), for the lines of the presses it turns away.
string busyBy = ""
float busySince = 0.0
; The busy watch (BusyWatchTime): counted from here (the claim, or a menu seen open since), and
; its switch (WatchBusy, from the console; false, the default, watches).
float busyWatchFrom = 0.0
bool busyWatchOff = false
; What SetTiltLive last wrote to CMB_TiltLive, for RideTick's look at it (CheckTiltLive); not known
; until it has written, as in a save from before it was kept.
float tiltLiveWritten = 0.0
bool tiltLiveKnown = false
; Test 41: the bike's slot is read a tick after the equip (EquipBike, RideTick).
bool wornSlotToLog = false
; The last room ask's number (RoomAt), so each is new.
int roomAskNo
float spotX   ; the spot PickBikeSpot found room at: its world x, y and the player's heading then (test 41: placed there, not where the player is by the time the asks are answered)
float spotY
float spotAngle
bool spotKnown = false
; Test 44: the checked spot's ground (the asked height less CMB_RoomClear, with room), for
; SettleBike's SpotSettleMax; spotGroundKnown false for a spot taken without room (the most room,
; or not checked).
float spotGround
bool spotGroundKnown = false
; The last answer's CMB_RoomClear (RoomAt; 0 when there was none), for CallTakesBestSpot.
float lastRoomClear = 0.0
; Test 46: a room answer's spot and heading read back (the plugin's [Room] Slide may have moved or
; turned it), and the ground's tilt under the wheels there (its ParkTilt; lastRoomTilted false
; without one); spotPitch/spotRoll/spotTiltKnown the chosen spot's, for SettleBike.
float lastRoomX
float lastRoomY
float lastRoomAngle
float lastRoomPitch
float lastRoomRoll
float lastRoomGround
bool lastRoomTilted = false
; 2026-11-01a: where the last SnapOff's navmesh snap took the probe (the plugin's [Room] SnapSpot asks about it).
float snapX
float snapY
float snapZ
float spotPitch
float spotRoll
bool spotTiltKnown = false
; Test 46: the last RollBikeUp found no spot and brought nothing (a call refused: the plugin's
; [Room] LineFallback=0).
bool rollRefused = false
; Test 47 (the plugin's [Room] ParkCheck): where the bike stood, and how, and where the player was
; when they got on (Mount), for getting off after a ride that went nowhere (ParkWhereItStood).
bool mountSpotKnown = false
float mountBikeX
float mountBikeY
float mountBikeZ
float mountBikeAX
float mountBikeAY
float mountBikeAZ
float mountPlayerX
float mountPlayerY
float mountPlayerZ
Actor[] stowedFollowers
Actor[] boostedFollowers
float[] boostedDeltas

; ---------------------------------------------------------------------------
; Lifecycle
; ---------------------------------------------------------------------------

Event OnInit()
	UpgradeSettings()
	EnsureArrays()
	WatchSwimming()
	WatchFalls()
	; Kept for good: one event per loading screen, and a teleport waits for its close.
	RegisterForMenuOpenCloseEvent(LoadingMenuName)
	; 2026-11-01a: a new game started after a ride in the same session: the player's own footstep sounds back (a
	; category's mute may outlive the game it was set in, as a load's may: LoadedOffTheBike).
	if AudioCategoryFSTplayer
		AudioCategoryFSTplayer.UnMute()
	endif
	TryDeliverKeys()
EndEvent

; Called by CMB_PlayerAliasScript every time a save is loaded.
Function OnGameReloaded()
	UpgradeSettings()
	EnsureArrays()
	; Test 41's two console switches, so every log says which rules it ran with.
	Log("Switches: teleports decided " + Ternary(teleportsAtOnce, "at once, in the event (DecideTeleportsAtOnce 1)", "once they're over") + ", busy watch " + Ternary(busyWatchOff, "off (WatchBusy 0).", "on (" + BusyWatchTime + " s)."))
	if busy
		; A save made while something held it (a loading screen allows saving): let go.
		Log("Loaded with busy held (" + busyBy + "): let go.")
	endif
	busy = false
	hasLastPos = false
	; In case the save was made during a loading screen: its close won't come.
	loadingOpen = false
	loadingSeen = false
	RegisterForMenuOpenCloseEvent(LoadingMenuName)
	if !teleportsAtOnce && (teleportPending || (bikeAtDoor && !riding))
		; Test 40: the exit autosave, loaded, brought the bike within a second (the save holds the
		; player outside already). A teleport pending in the save is looked at in the same way.
		bool atDoor = bikeAtDoor && !riding
		teleportPending = true
		teleportFromKnown = false
		teleportChecks = 0
		teleportSkipLogged = false
		teleportAt = Utility.GetCurrentRealTime()
		Log("Loaded with " + Ternary(atDoor, "the bike waiting at a door", "a teleport pending") + ": looked at once the load is over.")
		StartTimer(TeleportCheckInterval, TimerTeleport)
	endif
	WatchSwimming()
	WatchFalls()
	; Test 47 (the build-27b check): the ram script's cooldown and refusal stamps are real seconds,
	; which start again with each game launch: none from before a load means anything after it
	; (DropStaleStamps only dropped those later than now). Before the ride's StartRide below.
	CallRam("ClearStamps")
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
	; Before the ride's setup below: its engine sound offer waits up to SoundAnswerWait for the
	; plugin's answer (test 44), which held the hotkey up on every load into a ride.
	RefreshHotkey()

	if !riding && headlampRef
		RemoveHeadlamp()
	endif
	if !riding
		; 2026-11-01a: nothing a save carries from a ride stays on off the bike.
		LoadedOffTheBike()
		ParkGuardAfterLoad()   ; 2026-11-09a: a parked bike the save kept hidden (ParkGuard) looked at again
	endif
	if riding
		; Input layers and the engine's cached movement speed do not reliably
		; survive a reload, so put the riding setup back in place.
		ApplyControls()
		RefreshMovement(PlayerRef)
		; 2026-11-01a: the rider's own footstep sounds muted again (a load may or may not keep a
		; category's mute) and the landing cues registered again (FxStartRide).
		fxCueEventsOn = false
		FxStartRide()
		UpdateSteady("after loading")
		staggered = false   ; a save made mid-stagger: the watch's effect starts again if it still is
		reactionAt = -100.0
		itemAt = -100.0          ; 2026-11-02a: no use window across a load (real time starts again), no menu open
		itemInMenu = false
		riderMenuOpen = false
		CacheFavourites()        ; 2026-11-06a: the favourites as the save has them (CMB_RiderUseOwn)
		staggerOverPending = false
		RideWatchesOn()
		if riderPoseApplied
			; Right after a load the flavour can be refused (the graph isn't up yet),
			; so put it back on once the game is running.
			footstepsWatched = false
			StartTimer(ReloadPoseDelay, TimerReloadPose)
		endif
		SetCameraLive(true)
		SetSlopeLive(true)
		SetTiltLive(true)
		CallRam("StartRide")
		if !headlampRef
			PlaceHeadlamp()
		endif
		SetHeadlampLive(true)
		RegisterForPlayerTeleport()
		; Saves from before it was kept have 0 here, which the first door would read as a fast
		; travel. Only those: a newer save keeps the last tick's time, and the load takes none.
		if lastOutdoorTime <= 0.0
			lastOutdoorTime = Utility.GetCurrentGameTime()
		endif
		hitGrace = false
		healthMark = PlayerRef.GetValuePercentage(Health)
		WatchForHits()
		WatchFootsteps()
		; 2026-11-01a: the save's reading isn't this session's (the plugin starts again at 0).
		if CMB_RiderPoseOff
			CMB_RiderPoseOff.SetValue(0.0)
		endif
		; The tail light and the first-person bike: the save's references, told to the plugin again.
		TwinsAfterLoad()
		StartTimer(TickInterval, TimerTick)
		; Sounds don't survive a load, and their old instance numbers mean nothing now.
		engineIdle = 0
		engineCruise = 0
		fxWaterLoop = 0
		; Test 44: nor the plugin's eleven, nor its hold on them. The CMB_Snd globals still hold the
		; save's set (offeredGen says so): StartEngineLoops' stop withdraws it before the new one.
		engineLoops = None
		soundDriven = false
		mountedAt = Utility.GetCurrentRealTime()
		mountedHow = "loading into the ride"
		StartEngineLoops()
		FxStartWaterLoop()
	elseif bikeAtDoor
		; The bike waits at a door: the way out is watched for (as riding's is, put back here).
		RegisterForPlayerTeleport()
	endif
	; 2026-11-07a: a Customise session in the save (a crash, or a save made in it) ended, a stray look
	; item taken back, and the chosen look put on again (the composed swap isn't kept by the save).
	LookAfterLoad()
EndFunction

; Defaults that changed: a save that still has the old value gets the new one, once.
; (Global values are kept in the save, so a new default in the plugin doesn't reach it.)
Function UpgradeSettings()
	if settingsVersion < 1
		; Test 6 asked for the riding camera farther back: 300 became 450.
		if CMB_RidingCameraDistance && CMB_RidingCameraDistance.GetValue() == 300.0
			CMB_RidingCameraDistance.SetValue(450.0)
			Log("Riding camera distance: the old default 300 is now 450.")
		endif
		settingsVersion = 1
	endif
	if settingsVersion < 2
		; Test 8: the rider doesn't tilt with the bike, so the riding tilt went from 30 to 15.
		if CMB_MaxTilt && CMB_MaxTilt.GetValue() == 30.0
			CMB_MaxTilt.SetValue(15.0)
			Log("Bike tilt: the old default 30 is now 15.")
		endif
		settingsVersion = 2
	endif
	if settingsVersion < 3
		; Test 11: steering felt like a truck. The turning radius is now the one at riding speed
		; (tighter when slower), 300 became 180; turning when stopped 20 became 60.
		if CMB_TurnRadius && CMB_TurnRadius.GetValue() == 300.0
			CMB_TurnRadius.SetValue(180.0)
			Log("Turning radius: the old default 300 is now 180.")
		endif
		if CMB_StandTurnRate && CMB_StandTurnRate.GetValue() == 20.0
			CMB_StandTurnRate.SetValue(60.0)
			Log("Turning when stopped: the old default 20 is now 60.")
		endif
		settingsVersion = 3
	endif
	if settingsVersion < 4
		; Test 20: with the Sketchfab bike's long front the wheel went into rock faces at 15; 20 keeps it
		; out of more of them, the hands drifting off the grips by half a unit a degree.
		if CMB_MaxTilt && CMB_MaxTilt.GetValue() == 15.0
			CMB_MaxTilt.SetValue(20.0)
			Log("Bike tilt: the old default 15 is now 20.")
		endif
		settingsVersion = 4
	endif
	if settingsVersion < 5
		; Test 24: a road bike shouldn't climb the hill by Vault 111; 60 became 45 (on foot the
		; game allows 47).
		if CMB_MaxSlope && CMB_MaxSlope.GetValue() == 60.0
			CMB_MaxSlope.SetValue(45.0)
			Log("Steepest slope while riding: the old default 60 is now 45.")
		endif
		settingsVersion = 5
	endif
	if settingsVersion < 6
		; Test 29: the rider tilts with the bike now, and the bike pitches about the ground under
		; it, so the pitch can follow any slope you can climb: 20 became 45.
		if CMB_MaxTilt && CMB_MaxTilt.GetValue() == 20.0
			CMB_MaxTilt.SetValue(45.0)
			Log("Bike tilt: the old default 20 is now 45.")
		endif
		settingsVersion = 6
	endif
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

; Bike tilt (optional, F4SE plugin CMB_Slope.dll): it tilts the worn bike with the
; ground, by at most CMB_TiltLive degrees, while that isn't 0. (The parked bike is tilted
; here: see SettleBike.)
Function SetTiltLive(bool abRiding)
	if CMB_TiltLive
		float degrees = 0.0
		if abRiding && CMB_MaxTilt
			degrees = CMB_MaxTilt.GetValue()
		endif
		CMB_TiltLive.SetValue(degrees)
		tiltLiveWritten = degrees
		tiltLiveKnown = true
	endif
EndFunction

; Test 40's load (15:23:42): the bars turned and the wheels spun, but the bike stood upright
; through the turns and the rider sat straight up, no tilt and no torso lean. That is the
; plugin's path for CMB_TiltLive at 0, and no script path was found that leaves it so while
; riding; the plugin now logs that state ("tilt: riding with CMB_TiltLive at ..."). So each ride
; tick looks too: anything but what SetTiltLive wrote is logged and put back. Compared with what
; was written, not with CMB_MaxTilt, so the MCM's tilt still takes effect the next time you get
; on (the putting back reads it, as getting on does).
Function CheckTiltLive()
	if !tiltLiveKnown || !CMB_TiltLive
		return
	endif
	float reads = CMB_TiltLive.GetValue()
	if reads == tiltLiveWritten || busy || !riding   ; looked at again after the call: a dismount that ran meanwhile wrote 0 on purpose
		return
	endif
	SetTiltLive(true)
	Log("CMB_TiltLive read " + reads + " while riding, put back to " + tiltLiveWritten + ".")
EndFunction

; The headlamp (optional, F4SE plugin CMB_Slope.dll): it lights the lamp while
; CMB_HeadlampLive is 1. The mode decides: on, off, or on at night; the hotkey's say
; (headlampOverride) comes first while it stands.
Function SetHeadlampLive(bool abRiding)
	if !CMB_HeadlampLive
		return
	endif
	bool ruleLit = false
	if CMB_HeadlampMode
		int mode = CMB_HeadlampMode.GetValue() as int
		ruleLit = mode == 1 || (mode == 2 && IsNight())
	endif
	if ruleLit != headlampRuleLit
		; Dusk, dawn or the MCM changed the answer: the hotkey's say is over.
		headlampRuleLit = ruleLit
		headlampOverride = 0
	endif
	float want = 0.0
	if abRiding
		if headlampOverride == 2 || (headlampOverride == 0 && ruleLit)
			want = 1.0
		endif
	else
		headlampOverride = 0
	endif
	if CMB_HeadlampLive.GetValue() != want
		CMB_HeadlampLive.SetValue(want)
		if headlampRef
			if want > 0.0
				headlampRef.Enable()
			else
				headlampRef.Disable()
			endif
		endif
		if headlampRefOld && want == 0.0
			headlampRefOld.Disable()
		endif
		if want > 0.0
			Log("Headlamp lit.")
		else
			Log("Headlamp out.")
		endif
	endif
EndFunction

; The beam: a light reference placed at the rider while riding (the game keeps no add-on node
; of a worn mesh, test 30); disabled until the lamp is lit; CMB_Slope.dll keeps it at the lens.
ObjectReference headlampRef = None
; The one before a handover, retired a moment later (test 33: moving the one reference at
; every cell crossing reloaded its 3D and the beam flickered; now a fresh one is placed in
; the player's cell once the bike is two cells from the old one's, the plugin keeps the old
; one lit until the new one's 3D is in, and the old one is deleted 2.5 s later).
ObjectReference headlampRefOld = None
int lampCellX = 0
int lampCellY = 0
float lampPlacedAt = 0.0
float lampRetireAt = 0.0
; The hotkey's say while riding (test 32: it wrote the MCM's mode, so one press wiped "On at
; night" and the lamp lit by day): 0 none, 1 off, 2 on; cleared on getting off and whenever
; the mode's own answer changes (dusk, dawn, the MCM).
int headlampOverride = 0
bool headlampRuleLit = false

Function PlaceHeadlamp()
	RemoveHeadlamp()
	if !CMB_HeadlampLight || !CMB_HeadlampRefHi || !CMB_HeadlampRefLo
		return
	endif
	Light lamp = HeadlampForm()
	headlampRef = PlayerRef.PlaceAtMe(lamp, 1, false, true, false)
	if headlampRef
		TellPluginHeadlamp()
		Log("Headlamp light placed (" + headlampRef.GetFormID() + ").")
	else
		Log("Headlamp light could not be placed.")
	endif
EndFunction

Light Function HeadlampForm()
	Light lamp = CMB_HeadlampLight
	if CMB_HeadlampLightShadow && CMB_HeadlampShadows && CMB_HeadlampShadows.GetValue() > 0.0
		lamp = CMB_HeadlampLightShadow
	endif
	return lamp
EndFunction

; The plugin learns the current reference's form id from two globals (16 bits each), and
; notes where it was placed.
Function TellPluginHeadlamp()
	int id = headlampRef.GetFormID()
	CMB_HeadlampRefHi.SetValue(Math.LogicalAnd(Math.RightShift(id, 16), 65535) as float)
	CMB_HeadlampRefLo.SetValue(Math.LogicalAnd(id, 65535) as float)
	lampCellX = Math.Floor(PlayerRef.GetPositionX() / 4096.0)
	lampCellY = Math.Floor(PlayerRef.GetPositionY() / 4096.0)
	lampPlacedAt = Utility.GetCurrentRealTime()
EndFunction

; A fresh reference at the player, lit if the lamp is; the old one retired after 2.5 s (the
; plugin has long parked it by then: it does so as soon as the new one's 3D is in).
Function HandOverHeadlamp()
	Light lamp = HeadlampForm()
	if !lamp
		return
	endif
	bool lit = CMB_HeadlampLive && CMB_HeadlampLive.GetValue() > 0.0
	ObjectReference fresh = PlayerRef.PlaceAtMe(lamp, 1, false, !lit, false)
	if !fresh
		return
	endif
	RetireOldHeadlamp()
	headlampRefOld = headlampRef
	headlampRef = fresh
	TellPluginHeadlamp()
	lampRetireAt = lampPlacedAt + 2.5
	Log("Headlamp light handed over (" + fresh.GetFormID() + ") in cell " + lampCellX + ", " + lampCellY + ".")
	HandOverTwins()   ; 2026-11-01a: the tail light and the first-person bike, at the same moment
EndFunction

Function RetireOldHeadlamp()
	if headlampRefOld
		headlampRefOld.Disable()
		headlampRefOld.Delete()
		headlampRefOld = None
	endif
EndFunction

; The light reference stays in the cell it was placed in (test 32: the beam went after 25 s
; of riding, that cell unloaded behind the bike while the plugin moved only its 3D): it is
; moved along into the player's cell as the bike crosses into another, and moved to the
; player if its 3D is gone while the lamp is lit.
Function FollowHeadlamp()
	if !headlampRef || !riding
		return
	endif
	float now = Utility.GetCurrentRealTime()
	; Test 46: the two stamps are kept in the save and the real-time clock starts again with each
	; launch: after a load into a ride with the lamp kept, a stamp later than now is an earlier
	; session's, and held off the 3D check (and the old lamp's retirement) until the clock caught up.
	if lampPlacedAt > now
		lampPlacedAt = now
	endif
	if lampRetireAt > now + 2.5
		lampRetireAt = now
	endif
	if headlampRefOld && now >= lampRetireAt
		RetireOldHeadlamp()
	endif
	int cx = Math.Floor(PlayerRef.GetPositionX() / 4096.0)
	int cy = Math.Floor(PlayerRef.GetPositionY() / 4096.0)
	if Math.Abs(cx - lampCellX) >= 2 || Math.Abs(cy - lampCellY) >= 2
		; Two cells on from where it was placed: the next crossing could unload that cell.
		HandOverHeadlamp()
	elseif CMB_HeadlampLive && CMB_HeadlampLive.GetValue() > 0.0 && now - lampPlacedAt > 1.5 && !headlampRef.Is3DLoaded()
		headlampRef.MoveTo(PlayerRef)
		lampPlacedAt = now
		Log("Headlamp light moved to the player: its 3D was gone.")
	endif
EndFunction

Function RemoveHeadlamp()
	if CMB_HeadlampRefHi
		CMB_HeadlampRefHi.SetValue(0.0)
	endif
	if CMB_HeadlampRefLo
		CMB_HeadlampRefLo.SetValue(0.0)
	endif
	if headlampRef
		headlampRef.Disable()
		headlampRef.Delete()
		headlampRef = None
	endif
	RetireOldHeadlamp()
	RemoveTwins()   ; 2026-11-01a: the tail light and the first-person bike go with it
EndFunction

; ---------------------------------------------------------------------------
; 2026-11-01a: two more carried references, the headlamp's way (test 47): the tail lamp's light
; ("you can tell it's on, but it's not producing light": CMB_TailLight, a shadowless red spot) and
; the bike in first person ("in 1st person the bike model isn't even visible": CMB_BikeView, an
; unskinned copy of the bike). Placed at the rider on the first ride tick at which the plugin is
; seen working (PluginAlive), each only with its MCM switch on (CMB_TailLightMode,
; CMB_FirstPersonBike, read then: "takes effect the next time you get on"); their form ids go to the
; plugin in two globals each (16 bits, as the headlamp's), and the plugin keeps them at the bike
; (its [TailLight] and [View]). Handed over with the headlamp, or two cells on from where they were
; placed when there is no headlamp reference; the old one retired TailRetireAfter (tail) or
; ViewRetireAfter (view) later (the plugin keeps it in place until the new one's 3D is in);
; removed with the headlamp. The headlamp's own code is unchanged.
; ---------------------------------------------------------------------------
ObjectReference tailRef = None
ObjectReference tailRefOld = None
ObjectReference viewRef = None
ObjectReference viewRefOld = None
bool twinsPlaced = false
int twinCellX = 0
int twinCellY = 0
float twinPlacedAt = 0.0
float tailRetireAt = 0.0
float viewRetireAt = 0.0

; Without the plugin no light or view bike is placed: CMB_GroundNormalZ is zeroed on getting on and
; only CMB_Slope.dll writes it (a light placed without it would sit lit where it was put).
bool Function PluginAlive()
	return CMB_GroundNormalZ && CMB_GroundNormalZ.GetValue() > 0.0
EndFunction

bool Function TailWanted()
	return CMB_TailLight && CMB_TailRefHi && CMB_TailRefLo && CMB_TailLightMode && CMB_TailLightMode.GetValue() > 0.0
EndFunction

bool Function ViewWanted()
	return CMB_BikeView && CMB_ViewRefHi && CMB_ViewRefLo && CMB_FirstPersonBike && CMB_FirstPersonBike.GetValue() > 0.0
EndFunction

Function TellPluginTwin(ObjectReference akRef, GlobalVariable akHi, GlobalVariable akLo)
	int id = 0
	if akRef
		id = akRef.GetFormID()
	endif
	akHi.SetValue(Math.LogicalAnd(Math.RightShift(id, 16), 65535) as float)
	akLo.SetValue(Math.LogicalAnd(id, 65535) as float)
EndFunction

Function NoteTwinCell()
	twinCellX = Math.Floor(PlayerRef.GetPositionX() / 4096.0)
	twinCellY = Math.Floor(PlayerRef.GetPositionY() / 4096.0)
	twinPlacedAt = Utility.GetCurrentRealTime()
EndFunction

; From the ride tick (once per ride). Each PlaceAtMe lets another thread run: a ride that ended
; meanwhile takes the fresh reference away again here. FinishRide clears the twins (RemoveTwins,
; which alone sets twinsPlaced false) well before it sets riding false, so both are tested.
Function PlaceTwins()
	twinsPlaced = true
	NoteTwinCell()
	if TailWanted() && !tailRef
		ObjectReference freshTail = PlayerRef.PlaceAtMe(CMB_TailLight, 1, false, false, false)
		if freshTail && (!riding || !twinsPlaced)
			DeleteRef(freshTail)
			return
		elseif freshTail
			tailRef = freshTail
			TellPluginTwin(tailRef, CMB_TailRefHi, CMB_TailRefLo)
			Log("Tail light placed (" + freshTail.GetFormID() + ").")
		else
			Log("Tail light could not be placed.")
		endif
	endif
	if ViewWanted() && !viewRef
		ObjectReference freshView = PlayerRef.PlaceAtMe(CMB_BikeView, 1, false, false, false)
		if freshView && (!riding || !twinsPlaced)
			DeleteRef(freshView)
			return
		elseif freshView
			viewRef = freshView
			TellPluginTwin(viewRef, CMB_ViewRefHi, CMB_ViewRefLo)
			LookOnView()   ; 2026-11-07a: the chosen look on it, from a timer (none with a stock look)
			Log("First-person bike placed (" + freshView.GetFormID() + ").")
		else
			Log("First-person bike could not be placed.")
		endif
	endif
EndFunction

; From HandOverHeadlamp, or FollowTwins without a headlamp reference: a fresh one of each placed at
; the player, the current one kept as the old one for the plugin's handover.
Function HandOverTwins()
	if !twinsPlaced || (!tailRef && !viewRef)
		return
	endif
	RetireOldTwins(true)
	NoteTwinCell()
	if tailRef
		ObjectReference freshTail = PlayerRef.PlaceAtMe(CMB_TailLight, 1, false, false, false)
		if freshTail && (!riding || !twinsPlaced)
			DeleteRef(freshTail)
			return
		elseif freshTail
			tailRefOld = tailRef
			tailRef = freshTail
			TellPluginTwin(tailRef, CMB_TailRefHi, CMB_TailRefLo)
			tailRetireAt = twinPlacedAt + TailRetireAfter
		endif
	endif
	if viewRef
		ObjectReference freshView = PlayerRef.PlaceAtMe(CMB_BikeView, 1, false, false, false)
		if freshView && (!riding || !twinsPlaced)
			DeleteRef(freshView)
			return
		elseif freshView
			viewRefOld = viewRef
			viewRef = freshView
			TellPluginTwin(viewRef, CMB_ViewRefHi, CMB_ViewRefLo)
			LookOnView()   ; 2026-11-07a: as PlaceTwins
			viewRetireAt = twinPlacedAt + ViewRetireAfter
		endif
	endif
	Log("Tail light and first-person bike handed over (" + Ternary(tailRef != None, "tail " + FormIdText(tailRef), "no tail") + ", " + Ternary(viewRef != None, "view " + FormIdText(viewRef), "no view") + ") in cell " + twinCellX + ", " + twinCellY + ".")
EndFunction

string Function FormIdText(ObjectReference akRef)
	if !akRef
		return "none"
	endif
	return "" + akRef.GetFormID()
EndFunction

; abNow: whatever their time (a new handover, getting off); else each once its time is up.
Function RetireOldTwins(bool abNow)
	float now = Utility.GetCurrentRealTime()
	if tailRefOld && (abNow || now >= tailRetireAt)
		ObjectReference oldTail = tailRefOld
		tailRefOld = None
		DeleteRef(oldTail)
	endif
	if viewRefOld && (abNow || now >= viewRetireAt)
		ObjectReference oldView = viewRefOld
		viewRefOld = None
		DeleteRef(oldView)
	endif
EndFunction

Function DeleteRef(ObjectReference akRef)
	if akRef
		akRef.Disable()
		akRef.Delete()
	endif
EndFunction

; Each ride tick (RideTick, after FollowHeadlamp): the old ones retired once their time is up; two
; cells on without a headlamp reference (whose handover takes them along otherwise), a handover of
; their own; and one whose 3D is gone 1.5 s after it was placed is moved to the player (the
; headlamp's recovery).
Function FollowTwins()
	if !riding || !twinsPlaced
		return
	endif
	float now = Utility.GetCurrentRealTime()
	; Stamps are real seconds, which start again with each launch (as the headlamp's, test 46).
	if twinPlacedAt > now
		twinPlacedAt = now
	endif
	if tailRetireAt > now + ViewRetireAfter
		tailRetireAt = now
	endif
	if viewRetireAt > now + ViewRetireAfter
		viewRetireAt = now
	endif
	RetireOldTwins(false)
	int cx = Math.Floor(PlayerRef.GetPositionX() / 4096.0)
	int cy = Math.Floor(PlayerRef.GetPositionY() / 4096.0)
	if Math.Abs(cx - twinCellX) >= 2 || Math.Abs(cy - twinCellY) >= 2
		HandOverTwins()
		return
	endif
	if now - twinPlacedAt <= 1.5
		return
	endif
	if tailRef && !tailRef.Is3DLoaded()
		tailRef.MoveTo(PlayerRef)
		twinPlacedAt = now
		Log("Tail light moved to the player: its 3D was gone.")
	endif
	if viewRef && !viewRef.Is3DLoaded()
		viewRef.MoveTo(PlayerRef)
		twinPlacedAt = now
		Log("First-person bike moved to the player: its 3D was gone.")
		LookOnView()   ; 2026-11-07a: its new 3D is stock (ApplyTo's swap isn't kept): the look again
	endif
EndFunction

; Getting off (RemoveHeadlamp), a load off the bike: none left, the plugin told.
Function RemoveTwins()
	twinsPlaced = false
	if CMB_TailRefHi && CMB_TailRefLo
		TellPluginTwin(None, CMB_TailRefHi, CMB_TailRefLo)
	endif
	if CMB_ViewRefHi && CMB_ViewRefLo
		TellPluginTwin(None, CMB_ViewRefHi, CMB_ViewRefLo)
	endif
	ObjectReference a = tailRef
	ObjectReference b = viewRef
	tailRef = None
	viewRef = None
	DeleteRef(a)
	DeleteRef(b)
	RetireOldTwins(true)
EndFunction

; A load into a ride: the save's references are told to the plugin again (it starts afresh after a
; load), the old ones retired, the stamps this session's. None in the save: placed at the next tick.
Function TwinsAfterLoad()
	RetireOldTwins(true)
	twinsPlaced = tailRef != None || viewRef != None
	if tailRef && CMB_TailRefHi && CMB_TailRefLo
		TellPluginTwin(tailRef, CMB_TailRefHi, CMB_TailRefLo)
	endif
	if viewRef && CMB_ViewRefHi && CMB_ViewRefLo
		TellPluginTwin(viewRef, CMB_ViewRefHi, CMB_ViewRefLo)
	endif
	if twinsPlaced
		NoteTwinCell()
		Log("Tail light and first-person bike from the save told to the plugin again (" + Ternary(tailRef != None, "tail " + FormIdText(tailRef), "no tail") + ", " + Ternary(viewRef != None, "view " + FormIdText(viewRef), "no view") + ").")
	endif
EndFunction

bool Function IsNight()
	float days = Utility.GetCurrentGameTime()
	float hour = (days - Math.Floor(days)) * 24.0
	return hour < 6.5 || hour >= 19.0
EndFunction

; The headlamp hotkey (MCM): on or off while riding, until getting off or the next dusk or
; dawn; the MCM's mode stays as it is.
Function HeadlampPressed()
	if !CMB_HeadlampMode || !CMB_HeadlampLive || !riding
		return
	endif
	bool lit = CMB_HeadlampLive.GetValue() > 0.0
	if lit
		headlampOverride = 1
	else
		headlampOverride = 2
	endif
	SetHeadlampLive(riding)
	if riding
		if lit
			Debug.Notification("Headlamp off")
		else
			Debug.Notification("Headlamp on")
		endif
	endif
EndFunction

; Riding camera (optional, F4SE plugin CMB_Slope.dll): it raises the game's camera
; distance setting to CMB_CameraLive while that isn't 0, and puts the player's own back.
; (Papyrus can set INI settings but not read them, so the plugin does it.)
Function SetCameraLive(bool abRiding)
	if CMB_CameraLive
		float distance = 0.0
		if abRiding && CMB_RidingCameraDistance
			distance = CMB_RidingCameraDistance.GetValue()
		endif
		CMB_CameraLive.SetValue(distance)
	endif
EndFunction

; Knocking enemies over (test 40's wish; CMB_RamScript on this quest, with CMB_Slope.dll): its
; 0.1 s poll runs only while riding. StartRide in Mount and after a load while riding (what the
; ram globals hold then is old news), EndRide in FinishRide, which every way off goes through
; (EmergencyReset too). The switches are the MCM's "Knock enemies over" (CMB_RamEnemies) and
; [Ram] Enabled in CMB_Slope.ini; without the script nothing is called, and that is logged.
Function CallRam(string asFunction)
	ScriptObject ram = CastAs("CMB_RamScript")
	if ram
		ram.CallFunction(asFunction, new Var[0])
	else
		Log("Ram: CMB_RamScript is not on the quest: " + asFunction + " not called, nobody is knocked over.")
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

; 2026-11-07a (the customisation build): the look on the parked, first-person and (when the game
; refuses the worn bike's mods) worn bikes is F4SE's material swaps, in CMB_LookF4SE on this quest.
; Without it (no F4SE) nothing is called, logged once a session; returns its answer (-1 without it).
; akRef: ApplyTo's reference; asFrom: ApplyParked's "from" for its line.
int Function CallLookF4SE(string asFunction, ObjectReference akRef = None, string asFrom = "")
	ScriptObject look = CastAs("CMB_LookF4SE")
	if !look
		if !lookNoF4seSaid
			lookNoF4seSaid = true
			Log("Look: no CMB_LookF4SE (F4SE): the parked and first-person bikes stay stock")
		endif
		return -1
	endif
	Var[] params
	if asFunction == "ApplyParked"
		params = new Var[1]
		params[0] = asFrom
	elseif asFunction == "ApplyTo" || asFunction == "InFurniture"
		params = new Var[1]
		params[0] = akRef
	else
		params = new Var[0]
	endif
	return look.CallFunction(asFunction, params) as int
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
		UpdateTeleportWatch()
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
; Test 40: tries with the keys outside Diamond City left no line, so it's not known whether any
; use reached the script. Every use is logged now, and HandleKeys logs what it did.
Function RequestKeysAction()
	Log("Keys used (t " + Utility.GetCurrentRealTime() + ").")
	GiveKeysIfMissing(true)
	StartTimer(0.1, TimerKeys)
EndFunction

; F4SE and MCM hotkeys. Menus (including the console) pause the game; dialogue
; doesn't, so check scenes too. asFrom says which (test 40: every press is logged, an ignored one
; too).
Function HotkeyPressed(string asFrom = "the hotkey")
	MountPressNow()   ; 2026-11-10a (test 52): the press's time, for getting on's times line (MountEarly)
	if Utility.IsInMenuMode()
		Log("Hotkey (" + asFrom + ") ignored: in a menu.")
	elseif PlayerRef.IsInScene()
		Log("Hotkey (" + asFrom + ") ignored: in a scene.")
	else
		ToggleRide(asFrom)
	endif
EndFunction

; Hotkey behaviour: get off, get on, or call the bike over if it's not nearby.
Function ToggleRide(string asFrom)
	; Nothing to ride before the keys turn up (pre-war intro, Vault 111).
	if !keysDelivered
		Log("Hotkey (" + asFrom + ") ignored: the keys aren't handed out yet.")
		return
	endif
	bool near = IsBikeNearPlayer()
	Log("Hotkey (" + asFrom + "): " + PressState(near) + ".")
	if busy
		Log("Hotkey ignored: busy (" + BusyText() + ").")
		return
	endif
	if riding
		Log("Hotkey: getting off.")
		Dismount()
	elseif near
		; First, even with a door mark left set (the player came out far from the bike and walked
		; back to it): beside the bike the press gets on, it doesn't move the bike.
		Log("Hotkey: the bike beside the player: getting on.")
		Mount()
	else
		if bikeAtDoor
			Log("Hotkey: the bike waits at a door: bringing it.")
			if BringBikeFromDoor(asFrom)
				; It waited outside the door the player came out of: it's here now, the next press
				; gets on. Left where it waited (no spot with room), the mark is cleared and the
				; press goes on to a call, which takes the spot a call takes (test 43: the one with
				; the most room, CallTakesBestSpot; else the first).
				return
			endif
		endif
		Log("Hotkey: calling the bike.")
		CallBike()
	endif
EndFunction

; The state a keys use or a hotkey press found, for its log line.
string Function PressState(bool abNear)
	string text = "riding " + riding + ", busy " + busy
	if busy
		text += " (" + BusyText() + ")"
	endif
	text += ", the bike near " + abNear + " / at a door " + bikeAtDoor
	if bikeAtDoor
		text += " (in " + doorWorld + Ternary(bikeInside, ", kept hidden where the player went in", "") + ")"
	endif
	return text + ", the player in " + PlaceText(PlayerRef.GetParentCell(), PlayerRef.GetWorldSpace())
EndFunction

; Where the player is, for the log: the worldspace outdoors, the cell indoors.
string Function PlaceText(Cell akCell, WorldSpace akWorld)
	if !akCell
		return "no cell (in transit)"
	elseif akCell.IsInterior()
		return "" + akCell + ", indoors"
	endif
	return "" + akWorld
EndFunction

; Right after each claim of busy: who holds it, and since when; and the busy watch started (one
; timer, restarted by every claim, so it looks at the latest).
Function NoteBusy(string asWho)
	busyBy = asWho
	; Being noted (the time read below lets other threads run): the watch leaves this claim be.
	busyWatchFrom = -1.0
	busySince = Utility.GetCurrentRealTime()
	busyWatchFrom = busySince
	if !busyWatchOff
		StartTimer(BusyWatchTime, TimerBusyWatch)
	endif
EndFunction

; Test 40 (the busy watch): busy held BusyWatchTime by the latest claim is logged and let go. A
; menu open now counts it again from now; a claim made since the timer started, or a menu seen,
; leaves what's left of it to wait; a claim being noted starts the watch again itself. Busy is
; looked at again after the last call: from there to the let-go nothing else can run.
Function BusyWatchFired()
	if !busy || busyWatchOff
		return
	endif
	bool menu = Utility.IsInMenuMode()
	float now = Utility.GetCurrentRealTime()
	if !busy || busyWatchFrom < 0.0
		return
	endif
	if menu
		busyWatchFrom = now
	endif
	float left = BusyWatchTime - (now - busyWatchFrom)
	if left > 0.0
		StartTimer(left, TimerBusyWatch)
		return
	endif
	busy = false
	Log("Busy held " + (now - busySince) + " s (" + busyBy + "): let go.")
EndFunction

; Console, test 41's switch: cqf CMB_ControllerQuest WatchBusy 0 turns the busy watch off (busy is
; then held for as long as its holder runs, as up to test 40); 1 (the default) turns it on. Kept in
; the save.
Function WatchBusy(int aiOn)
	busyWatchOff = aiOn == 0
	if busyWatchOff
		CancelTimer(TimerBusyWatch)
	elseif busy
		busyWatchFrom = Utility.GetCurrentRealTime()
		StartTimer(BusyWatchTime, TimerBusyWatch)
	endif
	Log("Busy watch " + Ternary(busyWatchOff, "off (as up to test 40).", "on: busy held over " + BusyWatchTime + " s is let go."))
EndFunction

string Function BusyText()
	return busyBy + ", " + (Utility.GetCurrentRealTime() - busySince) + " s"
EndFunction

Function Mount()
	if customising
		; 2026-11-07a: the field kit is out (BeginCustomise): its session ends first.
		Log("Getting on ignored: customising.")
		return
	endif
	if riding || busy
		Log("Getting on ignored: " + Ternary(riding, "riding already.", "busy (" + BusyText() + ")."))
		return
	endif
	; Claim the lock before calling anything on other objects: those calls let
	; other threads (hotkey, timer, activation) run in between.
	busy = true
	mounting = true   ; 2026-11-09a (test 51): to "Mounted." (ApplyLook's parked compose waits; no parked reload)
	NoteBusy("getting on")
	string blocker = GetMountBlocker()
	if blocker != ""
		busy = false
		mounting = false
		ParkedLookDueNow("getting on refused")   ; 2026-11-09a: a look put on meanwhile, on the bike still standing
		Debug.Notification(blocker)
		Log("Getting on refused: " + blocker)
		return
	endif
	; 2026-11-09a: a parked bike kept hidden (ParkGuard) is the ride's now. The review of 2026-11-09a (A3): only once getting on
	; goes ahead (a refused one left the bike hidden with no poll).
	ParkGuardEnd("getting on")
	EnsureArrays()
	; 2026-11-09a (test 51's black screen; the plugin's [Look] MountGuard, CMB_LookOptions bit 16): the parked bike's
	; look work under way waited for (ParkedLookWait), then this attempt numbered and watched (MountWatch: the fade-in at
	; MountWatchdog, the give-up at MountGiveUp), and after the wait, the disable and the worn bike's equip, an attempt
	; the watchdog gave up is undone (MountUndo). Without the bit: none of it (2026-11-09a as of t54-merge).
	bool guarded = LookOption(16)
	int ticket = 0
	if guarded
		ParkedLookWait()
		ticket = MountWatchStart()
	endif
	mountStage = "the wait"
	; 2026-11-10a (test 52: getting on 3-5 s; the plugin's [Look] MountEarly, CMB_LookOptions bit 512): the worn bike equipped
	; right after the fade, the screen back when the plugin says the bike is ready, the non-visual rest after it (MountEarly).
	; Without the bit: 2026-11-09a's order, below.
	if LookOption(512)
		MountEarly(guarded, ticket)
		return
	endif

	Game.FadeOutGame(true, true, 0.0, 0.25, true)
	; The plugin moves the camera within a tenth of a second: the wait covers it.
	SetCameraLive(true)
	Utility.Wait(0.3)
	if guarded && MountStopped(ticket)
		MountUndo(ticket)
		return
	endif
	mountStage = "the camera"

	if CMB_ForceThirdPerson.GetValue() > 0.0
		if CMB_CameraLive && CMB_CameraLive.GetValue() > 0.0
			; Coming into third person again picks up the new camera distance
			; (hidden by the fade).
			Game.ForceFirstPerson()
		endif
		Game.ForceThirdPerson()
	endif
	; Test 47 (the plugin's [Room] ParkCheck): where the bike stands and the player is now, for a
	; getting off after a ride that went nowhere (ParkWhereItStood).
	mountSpotKnown = !BikeRef.IsDisabled() && BikeRef.Is3DLoaded()
	if mountSpotKnown
		mountBikeX = BikeRef.GetPositionX()
		mountBikeY = BikeRef.GetPositionY()
		mountBikeZ = BikeRef.GetPositionZ()
		mountBikeAX = BikeRef.GetAngleX()
		mountBikeAY = BikeRef.GetAngleY()
		mountBikeAZ = BikeRef.GetAngleZ()
		mountPlayerX = PlayerRef.GetPositionX()
		mountPlayerY = PlayerRef.GetPositionY()
		mountPlayerZ = PlayerRef.GetPositionZ()
	endif
	mountStage = "the parked bike's disable"
	BikeRef.Disable()
	if guarded && MountStopped(ticket)
		MountUndo(ticket)
		return
	endif
	mountStage = "the gear and the pose"
	CallGearRestore("RememberSlot")
	ApplyRiderPose()
	mountStage = "the look"
	LookSync("getting on")   ; 2026-11-07a: an MCM change since the look was last put on
	mountStage = "the worn bike"
	EquipBike()
	if guarded && MountStopped(ticket)
		MountUndo(ticket)
		return
	endif
	mountStage = "the rest"
	ApplyControls()
	playerSpeedDelta = ApplySpeed(PlayerRef)
	ApplyFallDamageCut()
	HandleFollowersOnMount()

	riding = true
	UpdateSteady("getting on")
	hasLastPos = false
	lastOutdoorTime = Utility.GetCurrentGameTime()
	combatHinted = false
	ForgetDoor()
	RegisterForPlayerTeleport()
	healthMark = PlayerRef.GetValuePercentage(Health)
	hitGrace = true
	StartTimer(HitGraceTime, TimerHitGrace)
	; 2026-11-01a: no reaction yet this ride (the reaction window), and the watches that feed it.
	reactionAt = -100.0
	reactionLeft = -200.0
	staggered = false
	; 2026-11-02a: no item used yet this ride, no menu open, the ride's counts and its once-a-ride lines afresh.
	itemAt = -100.0
	itemLeft = -200.0
	itemInMenu = false
	riderMenuOpen = false
	CacheFavourites()   ; 2026-11-06a: the favourites at getting on (CMB_RiderUseOwn)
	useCameraTries = 0
	useCameraFixed = false
	useCameraNoted = false
	staggerOverPending = false
	firstFootSaid = false
	rideHits = 0
	ridePowerHits = 0
	rideStaggers = 0
	RideWatchesOn()
	WatchForHits()
	poseRetries = 0
	poseRetryWaiting = false
	mountedAt = Utility.GetCurrentRealTime()
	mountedHow = "getting on"
	WatchFootsteps()
	; 2026-11-01a: the rider's own footstep sounds muted, the landing cues watched (CMB_FxMuteRider,
	; CMB_FxLandOn; the water loop starts with the engine's loops, TimerEngine).
	FxStartRide()
	SetSlopeLive(true)
	SetTiltLive(true)
	CallRam("StartRide")
	SetRamCombat(PlayerRef.IsInCombat())   ; 2026-11-02a: the plugin's PendingFoe=2 from the start, not a tick later
	PlaceHeadlamp()
	SetHeadlampLive(true)
	; Whatever is there is old (or from a game with the plugin): it writes them again at once.
	if CMB_GroundNormalZ
		CMB_GroundNormalZ.SetValue(0.0)
	endif
	if CMB_ParkUpZ
		CMB_ParkUpZ.SetValue(0.0)
	endif
	if CMB_RiderPoseOff
		CMB_RiderPoseOff.SetValue(0.0)   ; 2026-11-01a: an earlier ride's reading isn't this one's
	endif
	StartTimer(TickInterval, TimerTick)
	PlaySound(CMB_EngineStartSound)
	StartTimer(EngineStartLength, TimerEngine)
	Log("Mounted. SpeedMult +" + playerSpeedDelta + ", stowed " + stowedFollowers.Length + ", running " + boostedFollowers.Length)
	mountStage = ""   ; 2026-11-09a: MountWatch ends
	mounting = false

	Game.FadeOutGame(false, true, 0.0, 0.35)
	busy = false
	if FuelEnabled()
		Debug.Notification("Fuel: " + CountFuel())
	endif
	APWatchRideStart()   ; test 46: AP once at getting on (after the fade: its reads take a few frames)
EndFunction

; ---------------------------------------------------------------------------
; 2026-11-09a (test 51's black screen, s2 19:50:57 and s3 20:00:15): getting on guarded (the plugin's [Look] MountGuard,
; CMB_LookOptions bit 16). Test 51: a second activation during the first's 2-3 s of look work queued a second parked-bike
; box; Ride on one faded the screen out and kept it so, the other opened behind the fade, and its menu mode held Mount's
; Utility.Wait (and every timer) until a key answered it (s3: 57 s; s2: never). So: one activation at a time
; (ActivationBegin/End, CMB_BikeActivatorScript), no look work before the menu (the activator), getting on waits for the
; parked bike's look work (ParkedLookWait), and a watchdog (MountWatch, its own thread: CallFunctionNoWait) counts menu
; time too (Utility.WaitMenuMode): MountWatchdog after the fade it fades back in, naming Mount's stage and the menus open;
; MountGiveUp after it, out of every menu, it gives the ride up, and Mount, when it goes on, undoes what it did (MountUndo).
; ---------------------------------------------------------------------------
float Property ActivationStale = 60.0 AutoReadOnly
{An activation still noted this long after its start is old (a load mid-activation): the next one goes ahead.}
float Property MountLookWait = 3.0 AutoReadOnly
{Getting on waits up to this long for the parked bike's look work under way (ApplyLook's ApplyParked and what follows).}
float Property MountLookStep = 0.1 AutoReadOnly
float Property MountWatchdog = 8.0 AutoReadOnly
{Not mounted this long after getting on's fade (menu time counted): faded back in, and the stage and menus logged.}
float Property MountGiveUp = 25.0 AutoReadOnly
{...and this long after it, out of every menu: the ride given up (MountUndo when Mount goes on). Not past the worn
bike's equip: from there the ride goes on.}
float Property MountWatchStep = 0.25 AutoReadOnly

int activationTicket = 0       ; the latest activation's number (ActivationBegin)
float activationAt = -1.0      ; its real time while its menu or choice is under way (-1 none)
int mountTicket = 0            ; the latest getting on's number (MountWatchStart)
string mountStage = ""         ; where Mount is ("" outside it, and after "Mounted.")
float mountWatchFrom = 0.0     ; the real time of its fade
int mountGivenUp = 0           ; the attempt the watchdog gave up (0 none)
string mountGivenUpAt = ""     ; ...at this stage
int lookParkedWork = 0         ; parked look work under way (ApplyLook's ApplyParked and ParkedLookAfter, ParkedLookDueNow)
bool parkedLookDue = false     ; (FastMount) a look put on while getting on or riding: the parked bike's at its enable

; CMB_BikeActivatorScript, first: this activation's number, or 0 refused (logged). Checked and set with no call out
; between, so of two presses one passes: refused while another activation's menu or choice is under way (activationAt
; under ActivationStale old; over a second negative, real time from another launch, is old too, though a load clears it:
; LookAfterLoad), or while busy, riding or customising. The time is read before the check (two presses' reads can land
; in either order: a few milliseconds negative is the other press), the line written after it.
int Function ActivationBegin()
	float now = Utility.GetCurrentRealTime()
	float age = now - activationAt
	string why = ""
	if activationAt >= 0.0 && age > -1.0 && age < ActivationStale
		why = "again"
	elseif busy
		why = "busy"
	elseif riding
		why = "riding"
	elseif customising
		why = "customising"
	else
		activationTicket += 1
		activationAt = now
		return activationTicket
	endif
	if why == "again"
		Log("Parked bike activated again " + age + " s into the last activation (its menu or choice under way): ignored")
	elseif why == "busy"
		Log("Parked bike activated while busy (" + BusyText() + "): ignored")
	else
		Log("Parked bike activated while " + why + ": ignored")
	endif
	return 0
EndFunction

; CMB_BikeActivatorScript, after the choice's call returned: that activation is over (a later one's number keeps its own).
Function ActivationEnd(int aiTicket)
	if aiTicket == activationTicket
		activationAt = -1.0
	endif
EndFunction

; Mount, before its fade: the parked bike's look work under way (another thread's ApplyLook: its compose and what follows
; it, the reload included) waited for, up to MountLookWait, in MountLookStep steps; its line only when it waited.
Function ParkedLookWait()
	if lookParkedWork <= 0
		return
	endif
	float from = Utility.GetCurrentRealTime()
	float waited = 0.0
	while lookParkedWork > 0 && waited < MountLookWait
		Utility.Wait(MountLookStep)
		waited = Utility.GetCurrentRealTime() - from
	endwhile
	if lookParkedWork > 0
		Log("Getting on: waited " + waited + " s for the parked bike's look (still under way: getting on all the same)")
	else
		Log("Getting on: waited " + waited + " s for the parked bike's look")
	endif
EndFunction

; Mount, right before its fade: the attempt numbered, and its watchdog started on a thread of its own. Returns the number.
int Function MountWatchStart()
	mountTicket += 1
	int ticket = mountTicket
	mountGivenUp = 0
	mountGivenUpAt = ""
	mountStage = "the wait"
	mountWatchFrom = Utility.GetCurrentRealTime()
	Var[] params = new Var[1]
	params[0] = ticket
	CallFunctionNoWait("MountWatch", params)
	return ticket
EndFunction

; Mount's checks after its wait, the disable and the worn bike's equip: this attempt was given up (or a later one began).
bool Function MountStopped(int aiTicket)
	return aiTicket != mountTicket || mountGivenUp == aiTicket
EndFunction

; The watchdog (MountWatchStart's thread): while its attempt is the latest and not mounted, every MountWatchStep of real
; time, menus included (WaitMenuMode, where Mount's Wait and every timer stop). Ends at "Mounted.", a later attempt, the
; give-up, or real time from another launch (a load).
Function MountWatch(int aiTicket)
	bool fadedIn = false
	bool lateSaid = false
	while aiTicket == mountTicket && mountStage != "" && mountGivenUp != aiTicket
		Utility.WaitMenuMode(MountWatchStep)
		bool menu = Utility.IsInMenuMode()
		float t = Utility.GetCurrentRealTime() - mountWatchFrom
		string stage = mountStage
		if t < 0.0
			return
		endif
		if aiTicket == mountTicket && stage != "" && mountGivenUp != aiTicket
			if !fadedIn && t >= MountWatchdog
				fadedIn = true
				string open = LookF4SEText("MenusOpenText")
				Game.FadeOutGame(false, true, 0.0, 0.35)
				string menus = "menu mode " + Ternary(menu, "yes", "no")
				if open != ""
					menus += ", open: " + open
				endif
				Log("Getting on: not mounted " + t + " s after its fade (at " + stage + "; " + menus + "): faded back in (the watchdog)")
			elseif t >= MountGiveUp && !menu
				if stage == "the rest"
					if !lateSaid
						lateSaid = true
						Log("Getting on: not mounted " + t + " s after its fade (at the rest: past the worn bike, the ride goes on): not given up")
					endif
				else
					MountGiveUpNow(aiTicket, t, stage)
				endif
			endif
		endif
	endwhile
EndFunction

; The watchdog's give-up (out of every menu): the attempt marked (Mount's next check undoes it), busy and the activation
; let go, the camera back.
Function MountGiveUpNow(int aiTicket, float afAfter, string asStage)
	mountGivenUp = aiTicket
	mountGivenUpAt = asStage
	mounting = false
	if busy && busyBy == "getting on"
		busy = false
	endif
	activationAt = -1.0   ; its activation's thread is still in Mount: the next press goes ahead
	SetCameraLive(false)
	Game.FadeOutGame(false, true, 0.0, 0.35)
	Log("Getting on given up " + afAfter + " s after its fade (at " + asStage + "): the ride not started")
	Debug.Notification("The motorbike couldn't be got on. Try again.")
EndFunction

; Mount, at a check that found its attempt given up: what it did so far undone (the parked bike enabled where it stood if
; it was disabled, the worn bike off, the slot's own gear back, the pose cleared). An attempt overtaken by a later one only
; stops (the later one's state is left).
Function MountUndo(int aiTicket)
	if aiTicket != mountTicket
		Log("Getting on: an earlier attempt went on after a later one began: stopped there")
		return
	endif
	string stage = mountGivenUpAt
	mountStage = ""
	mounting = false
	bool claimed = !busy
	if claimed
		busy = true
		NoteBusy("undoing a getting on")
	endif
	if claimed && !riding && BikeRef.IsDisabled()
		EnableParked(false, 0, 0.0, true)   ; where it stood, the player at it to get on (the review's A1: not counted)
	else
		ParkedLookDueNow("getting on undone")
	endif
	RemoveBikeArmor()
	CallGearRestore("RestoreSlot")
	ClearRiderPose()
	SetCameraLive(false)
	Game.FadeOutGame(false, true, 0.0, 0.35)
	Log("Getting on: undone after the watchdog gave up (at " + stage + ")")
	if claimed
		busy = false
	endif
EndFunction

; ---------------------------------------------------------------------------
; 2026-11-10a (test 52: getting on 3-5 s, 3.4 s of black; the plugin's [Look] MountEarly, CMB_LookOptions bit 512): Mount's
; order changed. Test 52 (13:42:05): the worn bike was equipped 1.3-1.8 s into Mount (after the camera's 0.3 s, the camera,
; 11 position reads, the disable, the gear's slot and the pose) and its 3D held about 0.5 s after that; then about 60 more
; calls (followers, Steady, the teleport, the watches, the ram, the headlamp) took 1.3 s behind the black till "Mounted.".
; Now: (1) the fade and the camera as before; (2) the gear's slot remembered and the worn bike equipped at once, its look
; synced first (EquipBike's own LookSync), its 3D loading while the rest goes on (the armour the pose will want: EquipBike's
; abPoseAhead); (3) what is left of the
; camera's 0.3 s; (4) the camera forces, the spot read, the parked bike's disable, the pose; (5) the controls, the speed,
; the rider's footsteps muted, riding, the slope and the tilt live, the ride tick and the engine's start; (6) the screen
; back when the plugin writes CMB_RideReady 1 (the worn bike held and coloured, the rider seated: its [Look] RideReady),
; polled every MountReadyStep, or after MountReadyWait real seconds all the same (no plugin, RideReady=0, a bike that
; never comes); (7) the rest in 2026-11-09a's order, "Mounted.", busy freed, and the stage times in one line
; (MountStageLine). MountGuard's checks (MountStopped, MountUndo) after the equip, the wait, the disable and the pose
; (2026-11-09a's after its wait, disable and equip: each stage MountWatch can give up at has one after it); past them the
; ride goes on ("the rest"). A hotkey or an activation meanwhile is refused as busy, as before. What comes later than
; before: a follower stowed, the headlamp placed, hits, item uses, the landing cues and the door watched, all within about a
; second of the screen.
; ---------------------------------------------------------------------------
float Property MountReadyWait = 1.0 AutoReadOnly
{MountEarly: the screen back at most this long (real seconds) after the controls, CMB_RideReady 1 or not.}
float Property MountReadyStep = 0.05 AutoReadOnly
float Property MountPressFresh = 5.0 AutoReadOnly
{A press's time older than this at getting on's fade isn't that getting on's (the times line then starts at the fade).}

float mountPressAt = -1.0      ; the real time of the latest press that can get on (HotkeyPressed, the activator's Ride)

; HotkeyPressed and CMB_BikeActivatorScript's Ride: the press's time, for MountEarly's times line only.
Function MountPressNow()
	mountPressAt = Utility.GetCurrentRealTime()
EndFunction

; Mount with MountEarly (bit 512), from its fade on (its guards, ParkGuardEnd, ParkedLookWait and MountWatchStart done).
Function MountEarly(bool abGuarded, int aiTicket)
	Game.FadeOutGame(true, true, 0.0, 0.25, true)
	; The plugin moves the camera within a tenth of a second: the 0.3 s below cover it.
	SetCameraLive(true)
	float tFade = Utility.GetCurrentRealTime()
	float tPress = -1.0
	if mountPressAt >= 0.0 && tFade - mountPressAt >= 0.0 && tFade - mountPressAt < MountPressFresh
		tPress = mountPressAt
	endif
	mountPressAt = -1.0
	if CMB_RideReady
		CMB_RideReady.SetValue(0.0)   ; this ride's word only (the plugin writes 0 at a ride's start too)
	endif
	mountStage = "the gear"
	CallGearRestore("RememberSlot")
	; The look (an MCM change since it was last put on): EquipBike's own LookSync, first thing at the equip (Mount's own, right
	; before it in 2026-11-09a, read the same 15-50 globals once more with nothing between).
	mountStage = "the worn bike"
	EquipBike(true)
	float tEquip = Utility.GetCurrentRealTime()
	if abGuarded && MountStopped(aiTicket)
		MountUndo(aiTicket)
		return
	endif
	mountStage = "the wait"
	float left = 0.3 - (tEquip - tFade)
	if left > 0.0
		Utility.Wait(left)
	endif
	if abGuarded && MountStopped(aiTicket)
		MountUndo(aiTicket)
		return
	endif
	mountStage = "the camera"
	if CMB_ForceThirdPerson.GetValue() > 0.0
		if CMB_CameraLive && CMB_CameraLive.GetValue() > 0.0
			Game.ForceFirstPerson()   ; third person again picks up the new camera distance (hidden by the fade)
		endif
		Game.ForceThirdPerson()
	endif
	; Test 47 (the plugin's [Room] ParkCheck): where the bike stands and the player is now (ParkWhereItStood).
	mountSpotKnown = !BikeRef.IsDisabled() && BikeRef.Is3DLoaded()
	if mountSpotKnown
		mountBikeX = BikeRef.GetPositionX()
		mountBikeY = BikeRef.GetPositionY()
		mountBikeZ = BikeRef.GetPositionZ()
		mountBikeAX = BikeRef.GetAngleX()
		mountBikeAY = BikeRef.GetAngleY()
		mountBikeAZ = BikeRef.GetAngleZ()
		mountPlayerX = PlayerRef.GetPositionX()
		mountPlayerY = PlayerRef.GetPositionY()
		mountPlayerZ = PlayerRef.GetPositionZ()
	endif
	mountStage = "the parked bike's disable"
	BikeRef.Disable()
	if abGuarded && MountStopped(aiTicket)
		MountUndo(aiTicket)
		return
	endif
	mountStage = "the pose"
	ApplyRiderPose()
	float tPose = Utility.GetCurrentRealTime()
	if abGuarded && MountStopped(aiTicket)
		MountUndo(aiTicket)   ; the stage before "the rest" checked too (MountWatch gives up at any other)
		return
	endif
	mountStage = "the rest"
	ApplyControls()
	playerSpeedDelta = ApplySpeed(PlayerRef)
	fxCueBusy = false   ; FxStartRide's first half (the rider's footsteps muted); its landing cues after the screen
	FxMuteRider()
	riding = true
	SetSlopeLive(true)
	SetTiltLive(true)
	StartTimer(TickInterval, TimerTick)   ; the ride tick waits out busy (RideTick)
	PlaySound(CMB_EngineStartSound)
	StartTimer(EngineStartLength, TimerEngine)
	int readyHow = RideReadyWait()
	float tReady = Utility.GetCurrentRealTime()
	mountStage = ""   ; MountWatch ends: the screen is back
	Game.FadeOutGame(false, true, 0.0, 0.35)
	float tScreen = Utility.GetCurrentRealTime()

	ApplyFallDamageCut()
	HandleFollowersOnMount()
	UpdateSteady("getting on")
	hasLastPos = false
	lastOutdoorTime = Utility.GetCurrentGameTime()
	combatHinted = false
	ForgetDoor()
	RegisterForPlayerTeleport()
	healthMark = PlayerRef.GetValuePercentage(Health)
	hitGrace = true
	StartTimer(HitGraceTime, TimerHitGrace)
	reactionAt = -100.0
	reactionLeft = -200.0
	staggered = false
	itemAt = -100.0
	itemLeft = -200.0
	itemInMenu = false
	riderMenuOpen = false
	CacheFavourites()   ; 2026-11-06a: the favourites at getting on (CMB_RiderUseOwn)
	useCameraTries = 0
	useCameraFixed = false
	useCameraNoted = false
	staggerOverPending = false
	firstFootSaid = false
	rideHits = 0
	ridePowerHits = 0
	rideStaggers = 0
	RideWatchesOn()
	WatchForHits()
	poseRetries = 0
	poseRetryWaiting = false
	mountedAt = Utility.GetCurrentRealTime()
	mountedHow = "getting on"
	WatchFootsteps()
	FxWatchCues()   ; FxStartRide's second half: the landing cues watched
	CallRam("StartRide")
	SetRamCombat(PlayerRef.IsInCombat())   ; 2026-11-02a: the plugin's PendingFoe=2 from the start, not a tick later
	PlaceHeadlamp()
	SetHeadlampLive(true)
	; Whatever is there is old (or from a game with the plugin): it writes them again at once.
	if CMB_GroundNormalZ
		CMB_GroundNormalZ.SetValue(0.0)
	endif
	if CMB_ParkUpZ
		CMB_ParkUpZ.SetValue(0.0)
	endif
	if CMB_RiderPoseOff
		CMB_RiderPoseOff.SetValue(0.0)   ; 2026-11-01a: an earlier ride's reading isn't this one's
	endif
	Log("Mounted. SpeedMult +" + playerSpeedDelta + ", stowed " + stowedFollowers.Length + ", running " + boostedFollowers.Length)
	float tMounted = Utility.GetCurrentRealTime()
	mounting = false
	busy = false
	if FuelEnabled()
		Debug.Notification("Fuel: " + CountFuel())
	endif
	APWatchRideStart()   ; test 46: AP once at getting on (after the fade: its reads take a few frames)
	MountStageLine(tPress, tFade, tEquip, tPose, tReady, readyHow, tScreen, tMounted)
EndFunction

; MountEarly's step 6: CMB_RideReady polled every MountReadyStep for MountReadyWait real seconds at most. 1 it came, 0 it
; didn't (waited out), -1 no CMB_RideReady (an older ESP: waited out), -2 real time went back (a load from another
; session: no more waiting).
int Function RideReadyWait()
	float from = Utility.GetCurrentRealTime()
	float waited = 0.0
	while waited < MountReadyWait
		if CMB_RideReady && CMB_RideReady.GetValue() >= 1.0
			return 1
		endif
		Utility.Wait(MountReadyStep)
		waited = Utility.GetCurrentRealTime() - from
		if waited < 0.0
			return -2
		endif
	endwhile
	if !CMB_RideReady
		return -1
	elseif CMB_RideReady.GetValue() >= 1.0
		return 1
	endif
	return 0
EndFunction

; MountEarly's stage times, real seconds from the press (or from the fade without a press's time): "Getting on: the press
; 0.00, the fade 0.31, the equip 0.52, the pose 0.95, ready 1.18 (CMB_RideReady after 0.66 s), the screen back 1.53,
; Mounted 2.41 (real seconds)". CMB_RideReady's time counts from the equip.
Function MountStageLine(float afPress, float afFade, float afEquip, float afPose, float afReady, int aiReadyHow, float afScreen, float afMounted)
	float t0 = afPress
	string text = "Getting on: the press 0.00, the fade " + Hundredths(afFade - t0)
	if afPress < 0.0
		t0 = afFade
		text = "Getting on: the fade 0.00 (no press's time)"
	endif
	string how = "CMB_RideReady after " + Hundredths(afReady - afEquip) + " s"
	if aiReadyHow == 0
		how = "no CMB_RideReady within MountReadyWait, " + Tenths(MountReadyWait) + " s"
	elseif aiReadyHow == -1
		how = "no CMB_RideReady global (an older ESP): MountReadyWait"
	elseif aiReadyHow == -2
		how = "the wait cut short: real time went back"
	endif
	Log(text + ", the equip " + Hundredths(afEquip - t0) + ", the pose " + Hundredths(afPose - t0) + ", ready " + Hundredths(afReady - t0) + " (" + how + "), the screen back " + Hundredths(afScreen - t0) + ", Mounted " + Hundredths(afMounted - t0) + " (real seconds)")
EndFunction

; A CMB_LookF4SE function's text answer ("" without it: no F4SE).
string Function LookF4SEText(string asFunction)
	ScriptObject look = CastAs("CMB_LookF4SE")
	if !look
		return ""
	endif
	return look.CallFunction(asFunction, new Var[0]) as string
EndFunction

Function Dismount()
	if !riding || busy
		Log("Getting off ignored: " + Ternary(!riding, "not riding.", "busy (" + BusyText() + ")."))
		return
	endif
	if CMB_TrackSlope && CMB_TrackSlope.GetValue() > MaxDismountSlope
		Debug.Notification("Too steep to get off here.")
		Log("Getting off refused: the ground is " + CMB_TrackSlope.GetValue() + " deg steep.")
		return
	endif
	busy = true
	NoteBusy("getting off")

	Game.FadeOutGame(true, true, 0.0, 0.25, true)
	Utility.Wait(0.3)

	ParkBesidePlayer()
	FinishRide()
	Log("Dismounted.")

	Game.FadeOutGame(false, true, 0.0, 0.35)
	busy = false
EndFunction

; Bring the parked bike to the player (outdoors only). Each refusal is logged with its reason and
; the message shown (test 40).
Function CallBike()
	if riding || busy
		Log("Calling the bike ignored: " + Ternary(riding, "riding.", "busy (" + BusyText() + ")."))
		return
	endif
	busy = true
	NoteBusy("calling the bike")
	string refusal = ""
	string notice = ""
	if PlayerRef.IsInInterior()
		refusal = "indoors"
		notice = "You can only call your motorbike outdoors."
	elseif InClosedWorld()
		refusal = "in an enclosed worldspace (" + lastWorld + ")"
		notice = "There's no room for your motorbike here."
	elseif swimming
		refusal = "swimming"
		notice = DeepWaterMessage
	endif
	if refusal != ""
		busy = false
		Debug.Notification(notice)
		Log("Calling the bike refused: " + refusal + ": " + notice)
		return
	endif
	RollBikeUp(false, true)
	if rollRefused
		; Test 46 (the plugin's [Room] LineFallback=0): no spot with room around the player, nor one
		; to take for the most room: the bike stays where it was rather than past a fence or inside
		; a house (test 45's calls 1, 6 and 8).
		busy = false
		notice = "There's no room for your motorbike here."
		Debug.Notification(notice)
		Log("Calling the bike refused: no spot with room around the player (the spot lines above say why): " + notice)
		return
	endif
	PlaySound(CMB_EngineStopSound)
	busy = false
	Log("Bike called to the player.")
	Debug.Notification("Your motorbike rolls up.")
EndFunction

; In front of the player, a little to their right, on the ground: calling the bike, and
; bringing it from a door. The caller holds busy. Test 41: the first of the BikeSpots with room
; (PickBikeSpot). abFromDoor: the bike waits outside a door the rider parked it at, so with
; room at none of them it's left there (false then); a call takes the one with the most room
; (test 43, CallTakesBestSpot), or the first spot as before. Test 46: with none of those either
; and the plugin's [Room] LineFallback=0, nothing is brought: rollRefused, the bike shown again
; where it was if it was shown, false. 2026-11-09a (abCall): a call brings a bike kept hidden (ParkGuard) wherever it waits:
; its hold ends here, once the call goes ahead (the review of 2026-11-09a, A3: ended before the refusals, a refused call left
; it hidden with no poll); refused, it stays held.
bool Function RollBikeUp(bool abFromDoor = false, bool abCall = false)
	rollRefused = false
	bool wasShown = !BikeRef.IsDisabled()
	; Disabled before the asks: standing where it waited, the bike would be in its own way at a
	; spot over it (a disabled reference has no collision).
	BikeRef.Disable()
	int spot = PickBikeSpot(abFromDoor)
	if spot == -2
		rollRefused = true
		if wasShown
			EnableParked(false, 0, 0.0, true)   ; where it stood shown till this call's Disable (the review's A1: the player not counted)
		endif
		return false
	endif
	if abCall
		ParkGuardEnd("calling it")
	endif
	if spot < 0
		; Where it waited: the shadow move put it there at the rider's height, and LeaveBikeOutside
		; only showed it. Shown again, and settled on the ground there like any park.
		EnableParked(false, 3)
	else
		PlaceOnSpot(spot)
	endif
	bikeWaitsForShore = false
	ForgetDoor()
	return spot >= 0
EndFunction

; The bike at the spot PickBikeSpot chose: at the place the spot was checked at (spotX/Y/Angle), not
; where the player is by now (a player running out of a gate has moved a good way in the asks' half
; seconds, and the spot with room was the one asked about), at the player's height, shown, and
; settled (test 44: the snap measured against the checked spot, SpotSettleMax). A call, a bring and
; (test 47) a checked park.
Function PlaceOnSpot(int aiSpot)
	if spotKnown
		BikeRef.MoveTo(PlayerRef, spotX - PlayerRef.GetPositionX(), spotY - PlayerRef.GetPositionY(), 0.0, false)
		BikeRef.SetAngle(0.0, 0.0, spotAngle + ParkedModelYaw)
	else
		PlaceBike(SpotForward(aiSpot), SpotRight(aiSpot))
	endif
	; The review of 2026-11-09a (A2): a spot chosen around the player (by its offset, or the plugin's Slide off them): the guard
	; without the player.
	if spotKnown && spotGroundKnown
		EnableParked(true, 2, 0.0, true)
	else
		EnableParked(true, 3, 0.0, true)
	endif
EndFunction

; Test 47 (the plugin's [Room] SnapNext; test 46's calls onto a wrecked sedan and onto the truck the
; player stood on: the spot with room on the wreck, the navmesh snap 89 and 207 from it, the bike
; put back there): how far the navmesh snap takes the bike put at (afX, afY) at the player's height,
; as PlaceOnSpot puts it, from its checked spot (afX, afY, afGround), as SettleBike measures it;
; abFlat (no ground known) along the ground only. GroundProbeRef stands in for the bike, which stays
; where it is (disabled, during the asks). -1 without the probe.
float Function SnapOff(float afX, float afY, float afGround, bool abFlat)
	if !GroundProbeRef
		return -1.0
	endif
	GroundProbeRef.MoveTo(PlayerRef, afX - PlayerRef.GetPositionX(), afY - PlayerRef.GetPositionY(), 0.0, false)
	GroundProbeRef.MoveToNearestNavmeshLocation()
	; 2026-11-01a: the place it found, kept before the probe goes back (the plugin's [Room] SnapSpot).
	snapX = GroundProbeRef.GetPositionX()
	snapY = GroundProbeRef.GetPositionY()
	snapZ = GroundProbeRef.GetPositionZ()
	float sx = snapX - afX
	float sy = snapY - afY
	float sz = snapZ - afGround
	GroundProbeRef.MoveTo(HoldingMarkerRef)
	if abFlat
		sz = 0.0
	endif
	return Math.Sqrt(sx * sx + sy * sy + sz * sz)
EndFunction

; Test 41: the first of the BikeSpots with room, by the plugin's word on each (RoomAt), or -1
; for a bring whose spots all lack room: the bike stays where it waited. Each spot is the
; player's position offset as PlaceBike puts the bike, at the player's height, asked about with
; the player's heading (test 43). A spot the plugin doesn't answer about (no plugin, or an older
; ESP without the globals) ends the asking: the first spot is taken untested as before test 41,
; unless this is a bring and a spot was already refused, when where it waited is the surer
; place. Test 43: the first spot answered "not checked" (the plugin's rays not working yet, right
; after a load) is asked about once more RoomRaysWait later (RetryUncheckedSpot), and a call with
; room at none takes the one with the most room (CallTakesBestSpot). Test 46 (test 45's calls by
; fences and walls): with the plugin's [Room] Around (CMB_RoomOptions), the AroundSpots after the
; seven, each with its own heading (SpotTurn); a spot with room is taken where the plugin found it
; (slid or turned: RoomAt reads it back); and with its LineFallback=0 a call with no spot to take
; returns -2, refused (each spot that could be taken for the most room has a clear line; the first
; spot was past the fence or inside the house). Every try is logged, and the choice. Test 47: with
; the plugin's [Room] SnapNext (CMB_RoomOptions bit 8; test 46's calls onto a wrecked sedan and a
; truck) a spot with room whose navmesh snap goes past SpotSettleMax (SnapOff) is not walkable and
; the next is asked; the first such is taken only when nothing else passes (a call's most-room
; spot first if its own snap passes), and a bring takes it rather than where it waited. abPark
; (getting off, the plugin's [Room] ParkCheck, ParkChecked): the AroundSpots only, beside and behind
; the player, no most room; -1 with none of them to take (the bike parked as before). 2026-11-01a:
; with the plugin's [Room] SnapSpot (CMB_RoomOptions bit 16) a call or a bring that would take that
; first spot as before asks first about the place its navmesh snap found (SpotSnapReach at most from
; it), as a navmesh point, and takes it with room there and its own snap within SpotSettleMax.
; 2026-11-06a: with the plugin's [Room] SnapBest (CMB_RoomOptions bit 32; test 49's calls from on
; top of a truck) a call with no spot with room does the same for the most room when its own snap
; goes past SpotSettleMax, before the most room is taken as before.
int Function PickBikeSpot(bool abFromDoor, bool abPark = false)
	spotKnown = false
	spotGroundKnown = false
	spotTiltKnown = false
	if !CheckBikeSpot
		if abPark
			return -1
		endif
		return 0
	endif
	string who = "The bike's spot: "
	if abPark
		who = "The parked bike's spot: "
	endif
	float angle = PlayerRef.GetAngleZ()
	float px = PlayerRef.GetPositionX()
	float py = PlayerRef.GetPositionY()
	float pz = PlayerRef.GetPositionZ()
	; Test 43: the spot with the most room so far, for a call (CallTakesBestSpot).
	int bestSpot = -1
	float bestX = 0.0
	float bestY = 0.0
	float bestAngle = 0.0
	float bestClear = 0.0
	; Test 46: its ground and tilt, measured by the plugin ([Room] ParkTilt).
	bool bestTilted = false
	float bestPitch = 0.0
	float bestRoll = 0.0
	float bestGround = 0.0
	; 2026-11-09a (SnapOrder): its ground as the plugin wrote it, with a tilt or without (0: none).
	float bestGroundSeen = 0.0
	; Test 47 (SnapNext): the first spot with room whose navmesh snap went too far, as it was read.
	bool snapNext = RoomOption(8) && SpotSettleMax > 0.0
	int farSpot = -1
	float farX = 0.0
	float farY = 0.0
	float farAngle = 0.0
	float farGround = 0.0
	float farPitch = 0.0
	float farRoll = 0.0
	bool farTilted = false
	; 2026-11-01a (the plugin's [Room] SnapSpot): that spot's snap, and where it took the probe.
	float farSnap = 0.0
	float farSnapX = 0.0
	float farSnapY = 0.0
	bool unanswered = false
	int spots = BikeSpots
	int spot = 0
	if abPark
		spot = BikeSpots
		spots = BikeSpots + AroundSpots
	endif
	while spot < spots
		float forward = SpotForward(spot)
		float right = SpotRight(spot)
		float x = px + OffsetX(angle, forward, right)
		float y = py + OffsetY(angle, forward, right)
		float heading = angle + SpotTurn(spot)
		int room = 0
		if spot == 0 && RetryUncheckedSpot
			room = RoomAt(x, y, pz, spot, heading, ": asked again in " + Tenths(RoomRaysWait) + " s.")
			if room == -2
				; Test 43: no verdict yet (the plugin's test ray hasn't passed, right after a load;
				; its RaysRetry tries it again for the next ask). Asked about once more, from where
				; the player is by then (the later spots too): the first answer said nothing about
				; the old place.
				Utility.Wait(RoomRaysWait)
				angle = PlayerRef.GetAngleZ()
				px = PlayerRef.GetPositionX()
				py = PlayerRef.GetPositionY()
				pz = PlayerRef.GetPositionZ()
				x = px + OffsetX(angle, forward, right)
				y = py + OffsetY(angle, forward, right)
				heading = angle + SpotTurn(spot)
				room = RoomAt(x, y, pz, spot, heading)
				if room == -2 || room == 0
					if abFromDoor
						Log("The bike's spot: where it waited (spot 1 not checked twice: the plugin's rays aren't working here).")
						return -1
					endif
					; A call: the first spot untested, as with the switch off (below).
					room = 0
				endif
			endif
		else
			room = RoomAt(x, y, pz, spot, heading)
		endif
		if room == -2
			; Not checked (the plugin's rays): as no answer, as before test 43.
			room = 0
		endif
		if room > 0
			; Test 46: where the plugin found room (its [Room] Slide may have moved or turned the spot).
			spotX = lastRoomX
			spotY = lastRoomY
			spotAngle = lastRoomAngle
			spotKnown = true
			; With room CMB_RoomClear is how far under the asked height (the player's, pz) the ground is.
			spotGround = pz - lastRoomClear
			spotGroundKnown = true
			; Test 46: the ground's tilt under the wheels there (the plugin's [Room] ParkTilt).
			spotPitch = lastRoomPitch
			spotRoll = lastRoomRoll
			spotTiltKnown = lastRoomTilted
			string moved = ""
			float turned = lastRoomAngle - heading
			while turned > 180.0
				turned -= 360.0
			endwhile
			while turned < -180.0
				turned += 360.0
			endwhile
			if Math.Abs(lastRoomX - x) > 0.5 || Math.Abs(lastRoomY - y) > 0.5 || Math.Abs(turned) > 0.05
				moved = ", where the plugin found room (" + Whole(Math.Sqrt((lastRoomX - x) * (lastRoomX - x) + (lastRoomY - y) * (lastRoomY - y))) + " from the asked spot, turned " + Whole(turned) + ")"
			endif
			float snap = -1.0
			if snapNext
				snap = SnapOff(spotX, spotY, spotGround, false)
			endif
			if snap <= SpotSettleMax
				Log(who + (spot + 1) + " (" + SpotText(spot) + "), heading " + Whole(spotAngle) + moved + ".")
				return spot
			endif
			; Test 47 (SnapNext): off the navmesh (on a wreck, a truck's bed): the next spot.
			Log("Bike's spot " + (spot + 1) + " (" + SpotText(spot) + "): its navmesh snap " + Whole(snap) + " from it, over " + Whole(SpotSettleMax) + ": not walkable, the next spot asked (the plugin's [Room] SnapNext).")
			if farSpot < 0
				farSpot = spot
				farX = spotX
				farY = spotY
				farAngle = spotAngle
				farGround = spotGround
				farPitch = spotPitch
				farRoll = spotRoll
				farTilted = spotTiltKnown
				farSnap = snap
				farSnapX = snapX
				farSnapY = snapY
			endif
			spotKnown = false
			spotGroundKnown = false
			spotTiltKnown = false
		elseif room < 0 && CallTakesBestSpot && !abFromDoor && !abPark && lastRoomClear > 0.0 && lastRoomClear <= 200.0 && lastRoomClear > bestClear
			; Refused for a hit along a ray (a share of the plugin's Fore, which the INI allows up to
			; 200) or the ground under 100 below: the most room so far. The ground above (minus),
			; none within 100 (-1), no clear line (-3) and not checked (-2) don't count. Test 45's
			; review: the plugin checks the box at a spot refused for its ground below too (with
			; [Room] Line), its Clear the box's nearest hit when that is less, so none taken here is
			; unchecked.
			bestSpot = spot
			bestX = x
			bestY = y
			bestAngle = heading
			bestClear = lastRoomClear
			bestTilted = lastRoomTilted
			bestPitch = lastRoomPitch
			bestRoll = lastRoomRoll
			bestGround = lastRoomGround
			bestGroundSeen = lastRoomGroundSeen
		elseif room == 0
			if farSpot >= 0
				; Test 47: no answer after a spot with room whose snap went too far: that one (below).
				unanswered = true
				spot = spots
			elseif abPark
				Log(who + "as before (spot " + (spot + 1) + " not checked).")
				return -1
			elseif abFromDoor && spot > 0
				Log("The bike's spot: where it waited (spot " + (spot + 1) + " not checked, the earlier ones without room).")
				return -1
			else
				Log("The bike's spot: 1 (" + SpotText(0) + "), not checked, as before test 41.")
				return 0
			endif
		endif
		spot += 1
		if spot == BikeSpots && RoomOption(1) && !abPark
			; Test 46 (the plugin's [Room] Around): beside and behind the player too.
			spots = BikeSpots + AroundSpots
		endif
	endwhile
	; 2026-11-09a (SnapOrder): the most room's snaps measured in 3-D on its ground when the plugin wrote one (with a tilt, or without).
	bool snapOrder = RoomOption(64)
	float bestGroundUse = bestGround
	bool bestFlat = !bestTilted
	if snapOrder && !bestTilted && bestGroundSeen != 0.0
		bestGroundUse = bestGroundSeen
		bestFlat = false
	endif
	if farSpot >= 0 && snapOrder
		; 2026-11-09a, the plugin's [Room] SnapOrder (CMB_RoomOptions bit 64; test 50's call from the truck bed, 14:50:03: spot 10 room
		; off the navmesh, spot 9 refused but the most room, its snap measured flat for want of a tilt, the bike put on the truck): a
		; call with a spot with room off the navmesh asks in this order: 1, that spot's navmesh point (SnapSpot); 2, the most room by
		; its snap measured in 3-D on the ground the plugin wrote for it (taken below, its line as before); 3, the most room's navmesh
		; point (SnapBest); 4, that first spot as before. A checked spot with room beats one that had none.
		if RoomOption(16) && !abPark && CMB_RoomAskKind && farSnap > SpotSettleMax && farSnap <= SpotSnapReach
			string orderLabel = "Bike's spot " + (farSpot + 1) + "'s navmesh point (" + Whole(farSnap) + " from it)"
			int orderRoom = RoomAt(farSnapX, farSnapY, pz, farSpot, farAngle, ".", orderLabel, 1)
			if orderRoom > 0
				float orderAgain = SnapOff(lastRoomX, lastRoomY, pz - lastRoomClear, false)
				if orderAgain <= SpotSettleMax
					spotX = lastRoomX
					spotY = lastRoomY
					spotAngle = lastRoomAngle
					spotKnown = true
					spotGround = pz - lastRoomClear
					spotGroundKnown = true
					spotPitch = lastRoomPitch
					spotRoll = lastRoomRoll
					spotTiltKnown = lastRoomTilted
					if bestSpot >= 0 && !unanswered
						Log(who + orderLabel + ", heading " + Whole(spotAngle) + ": room, walkable (its own snap " + Whole(orderAgain) + "): taken before the most room (spot " + (bestSpot + 1) + ", none there) (the plugin's [Room] SnapOrder).")
					else
						Log(who + orderLabel + ", heading " + Whole(spotAngle) + ": room, walkable (its own snap " + Whole(orderAgain) + "): taken (the plugin's [Room] SnapSpot).")
					endif
					return farSpot
				endif
				Log(orderLabel + ": its own navmesh snap " + Whole(orderAgain) + ", over " + Whole(SpotSettleMax) + ".")
			endif
		endif
		if bestSpot >= 0 && !unanswered
			float orderSnap = SnapOff(bestX, bestY, bestGroundUse, bestFlat)
			if orderSnap > SpotSettleMax
				Log("Bike's spot " + (bestSpot + 1) + " (" + SpotText(bestSpot) + "), the most room: its navmesh snap " + Whole(orderSnap) + " from it" + Ternary(bestFlat, "", " in 3-D on its ground") + ", over " + Whole(SpotSettleMax) + ": not walkable either.")
				if RoomOption(32) && CMB_RoomAskKind && SpotSettleMax > 0.0 && SnapBestTry(who, bestSpot, bestX, bestY, bestAngle, pz, orderSnap, "the first spot with room as before (the plugin's [Room] SnapOrder)")
					return bestSpot
				endif
				bestSpot = -1
			endif
		else
			bestSpot = -1
		endif
		if bestSpot < 0
			spotX = farX
			spotY = farY
			spotAngle = farAngle
			spotKnown = true
			spotGround = farGround
			spotGroundKnown = true
			spotPitch = farPitch
			spotRoll = farRoll
			spotTiltKnown = farTilted
			Log(who + (farSpot + 1) + " (" + SpotText(farSpot) + "), heading " + Whole(spotAngle) + ": the first with room, its navmesh snap too far, and no other spot passes (the plugin's [Room] SnapOrder): taken as before.")
			return farSpot
		endif
	elseif farSpot >= 0
		; Test 47 (SnapNext): a call's most-room spot first, if its own snap passes (test 46's truck:
		; the spots beside it refused for the ground below, a step down, the spots on it with room).
		if bestSpot >= 0 && !unanswered
			float bestSnap = SnapOff(bestX, bestY, bestGround, !bestTilted)
			if bestSnap > SpotSettleMax
				Log("Bike's spot " + (bestSpot + 1) + " (" + SpotText(bestSpot) + "), the most room: its navmesh snap " + Whole(bestSnap) + " from it, over " + Whole(SpotSettleMax) + ": not walkable either.")
				bestSpot = -1
			endif
		else
			bestSpot = -1
		endif
		if bestSpot < 0 && RoomOption(16) && !abPark && CMB_RoomAskKind && farSnap > SpotSettleMax && farSnap <= SpotSnapReach
			; 2026-11-01a: test 47's call from on top of the red truck (20:04:16): spot 10 room on the hood, its snap 129 off,
			; the bike put back on the hood's edge. The place the snap found, asked about as a navmesh point (the plugin's
			; [Room] SnapSpot: a level line from the player, a drop off what they stand on, no step test), and taken if it
			; has room and its own snap stays within SpotSettleMax.
			string pointLabel = "Bike's spot " + (farSpot + 1) + "'s navmesh point (" + Whole(farSnap) + " from it)"
			int pointRoom = RoomAt(farSnapX, farSnapY, pz, farSpot, farAngle, ".", pointLabel, 1)
			if pointRoom > 0
				float again = SnapOff(lastRoomX, lastRoomY, pz - lastRoomClear, false)
				if again <= SpotSettleMax
					spotX = lastRoomX
					spotY = lastRoomY
					spotAngle = lastRoomAngle
					spotKnown = true
					spotGround = pz - lastRoomClear
					spotGroundKnown = true
					spotPitch = lastRoomPitch
					spotRoll = lastRoomRoll
					spotTiltKnown = lastRoomTilted
					Log(who + pointLabel + ", heading " + Whole(spotAngle) + ": room, walkable (its own snap " + Whole(again) + "): taken (the plugin's [Room] SnapSpot).")
					return farSpot
				endif
				Log(pointLabel + ": its own navmesh snap " + Whole(again) + ", over " + Whole(SpotSettleMax) + ".")
			endif
		endif
		if bestSpot < 0
			spotX = farX
			spotY = farY
			spotAngle = farAngle
			spotKnown = true
			spotGround = farGround
			spotGroundKnown = true
			spotPitch = farPitch
			spotRoll = farRoll
			spotTiltKnown = farTilted
			Log(who + (farSpot + 1) + " (" + SpotText(farSpot) + "), heading " + Whole(spotAngle) + ": the first with room, its navmesh snap too far, and no other spot passes (the plugin's [Room] SnapNext): taken as before.")
			return farSpot
		endif
	endif
	if abFromDoor
		Log("The bike's spot: where it waited (none of the " + spots + " has room).")
		return -1
	endif
	if abPark
		Log(who + "as before (none of the " + AroundSpots + " beside and behind the player has room either).")
		return -1
	endif
	if bestSpot >= 0
		; 2026-11-06a: test 49's calls from on top of a modded truck (12:05:13, 12:06:09): no spot had room, the most room was on
		; the truck 70 below the player, its navmesh snap 166 and 193 to the street, and the bike was put back on the truck. With
		; the plugin's [Room] SnapBest (CMB_RoomOptions bit 32): the most room's own snap first, and past SpotSettleMax the place
		; it found asked as a navmesh point, taken with room there and its own snap within SpotSettleMax. Off (bit 32 clear:
		; SnapBest=0, an older plugin, or no CMB_RoomAskKind): the most room taken as before.
		if RoomOption(32) && CMB_RoomAskKind && SpotSettleMax > 0.0 && !unanswered
			; 2026-11-09a: the block in SnapBestTry (SnapOrder asks it too); with SnapOrder the snap in 3-D on its ground when known.
			if SnapBestTry(who, bestSpot, bestX, bestY, bestAngle, pz, SnapOff(bestX, bestY, bestGroundUse, bestFlat), "the most room as before (the plugin's [Room] SnapBest)")
				return bestSpot
			endif
		endif
		Log("The bike's spot: " + (bestSpot + 1) + " (" + SpotText(bestSpot) + "), heading " + Whole(bestAngle) + ", the most room of the " + spots + " (the nearest hit " + Whole(bestClear) + " along a ray, on the bike's 110, or the ground " + Whole(bestClear) + " below; none has room, a call takes the most room).")
		spotX = bestX
		spotY = bestY
		spotAngle = bestAngle
		spotKnown = true
		if bestTilted
			; Test 46 (the plugin's [Room] ParkTilt; test 45's call 11, its most-room spot left level by
			; a coarse navmesh): its ground and tilt known, it's settled as a checked spot.
			spotGround = bestGround
			spotGroundKnown = true
			spotPitch = bestPitch
			spotRoll = bestRoll
			spotTiltKnown = true
		endif
		return bestSpot
	endif
	if RoomOption(2)
		; Test 46 (the plugin's [Room] LineFallback=0): nothing to take; the first spot was past the
		; fence, inside the house or beyond the rubble (test 45's calls 1, 6 and 8).
		Log("The bike's spot: none of the " + spots + " has room, and none to take for the most room (a hit along its box or the ground below, each with a clear line): the call is refused.")
		return -2
	endif
	Log("The bike's spot: 1 (" + SpotText(0) + "), none of the " + spots + " has room (a call takes the first, as before test 41).")
	return 0
EndFunction

; 2026-11-06a's SnapBest (the plugin's [Room] SnapBest, CMB_RoomOptions bit 32), PickBikeSpot's block till 2026-11-09a, a
; function since (its SnapOrder asks it too): the most room (aiSpot at afX, afY, heading afAngle) whose own snap afSnap (just
; measured: snapX/snapY hold where it took the probe) is past SpotSettleMax and within SpotSnapReach: the place it found asked about
; as a navmesh point, taken with room there and its own snap within SpotSettleMax (true, spotX... set). Else false, and past
; SpotSettleMax a line ending "its navmesh point not taken: " + asElse.
bool Function SnapBestTry(string asWho, int aiSpot, float afX, float afY, float afAngle, float afZ, float afSnap, string asElse)
	if !(afSnap > SpotSettleMax && afSnap <= SpotSnapReach)
		return false
	endif
	float mostX = snapX
	float mostY = snapY
	string mostLabel = "Bike's spot " + (aiSpot + 1) + "'s navmesh point, the most room's (" + Whole(afSnap) + " from it)"
	int mostRoom = RoomAt(mostX, mostY, afZ, aiSpot, afAngle, ".", mostLabel, 1)
	if mostRoom > 0
		float mostAgain = SnapOff(lastRoomX, lastRoomY, afZ - lastRoomClear, false)
		if mostAgain <= SpotSettleMax
			spotX = lastRoomX
			spotY = lastRoomY
			spotAngle = lastRoomAngle
			spotKnown = true
			spotGround = afZ - lastRoomClear
			spotGroundKnown = true
			spotPitch = lastRoomPitch
			spotRoll = lastRoomRoll
			spotTiltKnown = lastRoomTilted
			Log(asWho + mostLabel + ", heading " + Whole(spotAngle) + ": room, walkable (its own snap " + Whole(mostAgain) + "): taken (the plugin's [Room] SnapBest).")
			return true
		endif
		Log(mostLabel + ": its own navmesh snap " + Whole(mostAgain) + ", over " + Whole(SpotSettleMax) + ".")
	endif
	Log("Bike's spot " + (aiSpot + 1) + ", the most room: its navmesh snap " + Whole(afSnap) + ", over " + Whole(SpotSettleMax) + ", its navmesh point not taken: " + asElse + ".")
	return false
EndFunction

; Test 46: a bit of CMB_RoomOptions, the plugin's [Room] keys for this script (1 Around, 2 a call
; with no spot refused); false without the global or the plugin (0: test 45's build).
bool Function RoomOption(int aiBit)
	if !CMB_RoomOptions
		return false
	endif
	int options = CMB_RoomOptions.GetValue() as int
	return (options / aiBit) % 2 == 1
EndFunction

; 2026-11-09a (test 51): a bit of CMB_LookOptions (0xBF4), the plugin's [Look] switches for this script (1 FastMount, 2
; KitHeld, 4 ParkedReload, 8 PaletteIndex, 16 MountGuard, 32 HueFree; 64 the plugin writes the worn bike's colours; since
; 2026-11-10a 128 KitStash, 256 KitRetry, 512 MountEarly, 1024 WornColoursFirst, 2048 HueSwap); the ESP's 4031 without the
; plugin. false without the global (an older ESP: 2026-11-09a as of t54-merge).
bool Function LookOption(int aiBit)
	if !CMB_LookOptions
		return false
	endif
	int options = CMB_LookOptions.GetValue() as int
	return (options / aiBit) % 2 == 1
EndFunction

; 2026-11-09a (test 51): Mount's start to its "Mounted." line (the mount unit sets it, the kitpaint unit reads it).
bool mounting = false

; 2026-11-09a (test 51): hooks the round's units fill; nothing calls them yet (step 0).
; After a parked look's apply (asFrom: who applied it, aiApplied: the entries applied): the kitpaint unit's (ParkedReload).
; [Look] ParkedReload (bit 4): the parked bike's 3D loaded again for its colours (ParkedReload, after KitTidy).
Function ParkedLookAfter(string asFrom, int aiApplied)
	if aiApplied > 0 && LookOption(4)
		ParkedReload(asFrom)
	endif
EndFunction

; The MCM's hue or shade moved (asFrom: who noticed): the kitpaint unit's (HueFree).
; [Look] HueFree (bit 32), first in LookSync (the activation, getting on, the worn equip) and LookApplyFromMcm: the MCM's
; "Paint hue" (whole, 0-359) and "Paint shade" (0-3) read against what was last seen (-1 at first: the first read only
; records). Moved with Paint not "Free colour" and no faction set pending: Paint becomes "Free colour" (the hue only
; colours that paint; test 51 moved it three times and nothing changed). A faction set pending (chosen with it) wins:
; the hue is recorded, Paint left. Off: nothing (the record dropped, so turning it on starts afresh). The review of
; 2026-11-09a: (A4) the record is also made where the look is put on (ApplyLook's LookHueRecord, a load's included), so the
; first move after a load of an older save, or after the switch is turned on, counts; (A5) Paint is recorded with them, and a
; Paint chosen since the record (with the move, in the same MCM visit) wins as a set does.
int lookHueSeen = -1
int lookShadeSeen = -1
int lookPaintSeen = -1   ; the review of 2026-11-09a (A5): Paint as last seen or put on (-1: none)

; The MCM's hue and shade, whole and clamped as LookHueFromMcm clamps them.
int Function LookHueRead()
	int h = Math.Floor(CMB_LookHue.GetValue() + 0.5)
	if h < 0
		h = 0
	elseif h > 359
		h = 359
	endif
	return h
EndFunction

int Function LookShadeRead()
	int sh = Math.Floor(CMB_LookShade.GetValue() + 0.5)
	if sh < 0
		sh = 0
	elseif sh > 3
		sh = 3
	endif
	return sh
EndFunction

; The review of 2026-11-09a (A4, A5; ApplyLook's first line): the look as put on recorded for LookHueWanted: Paint always (a
; field kit's, a faction set's or a clamp's Paint is no choice made with a later move), the hue and shade only when nothing is
; recorded (a save from before this build, HueFree just turned on: the first move after it counts; a move not yet seen,
; which a save keeps, isn't taken as the record). Off: nothing (LookHueWanted drops the record).
Function LookHueRecord()
	if !LookOption(32) || !CMB_LookHue || !CMB_LookShade || !CMB_Look_Paint
		return
	endif
	int h = LookHueRead()
	int sh = LookShadeRead()
	int paint = LookChoice(LookSlotPaint, false)
	if lookHueSeen < 0 || lookShadeSeen < 0
		lookHueSeen = h
		lookShadeSeen = sh
	endif
	lookPaintSeen = paint
EndFunction

Function LookHueWanted(string asFrom)
	if !LookOption(32) || !CMB_LookHue || !CMB_LookShade || !CMB_Look_Paint
		lookHueSeen = -1
		lookShadeSeen = -1
		lookPaintSeen = -1
		return
	endif
	int h = LookHueRead()
	int sh = LookShadeRead()
	int paint = LookChoice(LookSlotPaint, false)
	; Read and recorded with no call between (another thread's read sees this one's record).
	int hueWas = lookHueSeen
	int shadeWas = lookShadeSeen
	int paintWas = lookPaintSeen
	lookHueSeen = h
	lookShadeSeen = sh
	lookPaintSeen = paint
	if hueWas < 0 || shadeWas < 0 || (h == hueWas && sh == shadeWas)
		return
	endif
	string moved = "hue"
	string hues = "" + hueWas + " -> " + h
	if h == hueWas
		moved = "shade"
		hues = "" + h
	endif
	string shades = LookShadeName(sh)
	if sh != shadeWas
		shades = LookShadeName(shadeWas) + " -> " + shades
	endif
	string said = "Look: the MCM's paint " + moved + " moved (" + hues + ", shade " + shades + ") (" + asFrom + ")"
	int set = 0
	if CMB_LookFactionSet
		set = CMB_LookFactionSet.GetValue() as int
	endif
	if set >= 1
		Log(said + ": faction set " + set + " chosen with it wins: Paint left")
	elseif paint != LookPaintFree && paintWas >= 0 && paint != paintWas
		; The review of 2026-11-09a (A5): a Paint chosen with it (since the record) wins, as a set does.
		Log(said + ": Paint " + LookName(LookSlotPaint, paint) + " (" + paint + ") chosen with it wins: Paint left")
	elseif paint != LookPaintFree
		CMB_Look_Paint.SetValue(LookPaintFree as float)
		lookPaintSeen = LookPaintFree
		Log(said + ": Paint is now \"Free colour\"")
	endif
EndFunction

; The parked look's work due now, not waiting for getting off (asFrom: who asks): the mount unit's.
; 2026-11-09a (test 51, getting on 5-6 s; [Look] FastMount, bit 1): a look put on while getting on or riding (ApplyLook's
; parkedLookDue) composed on the parked bike now, still disabled: SetMaterialSwap keeps it, so the enable that follows loads
; the bike with it ("0 applied now"). Nothing when none is due. EnableParked's first line (every enable of the parked bike),
; Mount's refusal and its undo.
Function ParkedLookDueNow(string asFrom)
	if !parkedLookDue
		return
	endif
	parkedLookDue = false
	lookParkedWork += 1
	CallLookF4SE("ApplyParked", None, asFrom)
	if lookParkedWork > 0
		lookParkedWork -= 1
	endif
EndFunction

; Asks CMB_Slope.dll whether the parked bike has room at (afX, afY, afZ), facing afAngle (the
; player's heading, test 43: the plugin checks a bike-shaped box along it): 1 room, -1 none, -2
; not checked (the plugin's rays aren't working there; test 43, before it 0), 0 no answer in
; RoomAnswerWait (no plugin, or an older ESP without the globals). The ask's number is new each
; time, above what the global holds (a save keeps the globals), so an old answer can't be read
; as this one. lastRoomClear is the answer's CMB_RoomClear (0 with none). asUnchecked ends the
; "not checked" line (PickBikeSpot's retry says so there). Busy is the caller's: the waits are
; inside its hold. Test 46: with room, lastRoomX/Y/Angle are where the plugin found it (read back
; from CMB_RoomAskX/Y/Angle: its [Room] Slide may have moved or turned the spot; as asked with an
; older plugin), and lastRoomPitch/Roll the ground's tilt under the wheels there (CMB_RoomPitch and
; Roll, lastRoomTilted; -1000 none: its ParkTilt off, or an older plugin or ESP). Test 47: asSpot
; names a spot that isn't one of the BikeSpots in its lines (ParkChecked's "The park spot (...)").
; 2026-11-01a: aiKind is CMB_RoomAskKind's value for the ask (1: a navmesh point, the plugin's [Room] SnapSpot; 2026-11-09a: 2
; the parked bike's guard, ParkGuard; 3 the same without the player, the review of 2026-11-09a).
int Function RoomAt(float afX, float afY, float afZ, int aiSpot, float afAngle, string asUnchecked = ".", string asSpot = "", int aiKind = 0)
	string try = "Bike's spot " + (aiSpot + 1) + " (" + SpotText(aiSpot) + "): "
	if asSpot != ""
		try = asSpot + ": "
	endif
	lastRoomClear = 0.0
	lastRoomX = afX
	lastRoomY = afY
	lastRoomAngle = afAngle
	lastRoomTilted = false
	if !CMB_RoomAskX || !CMB_RoomAskY || !CMB_RoomAskZ || !CMB_RoomAsk || !CMB_RoomAnswer || !CMB_RoomClear
		Log(try + "not checked (the ESP has no CMB_Room globals).")
		return 0
	endif
	int n = CMB_RoomAsk.GetValue() as int
	if n < roomAskNo
		n = roomAskNo
	endif
	n += 1
	if n > 1000000
		; Well within a float's whole numbers; a wrap is never seen (a few asks a door).
		n = 1
	endif
	roomAskNo = n
	CMB_RoomAskX.SetValue(afX)
	CMB_RoomAskY.SetValue(afY)
	CMB_RoomAskZ.SetValue(afZ)
	if CMB_RoomAskAngle
		; Before the number, like the spot: the plugin reads them all once the number is new.
		CMB_RoomAskAngle.SetValue(afAngle)
	endif
	if CMB_RoomAskKind
		; 2026-11-01a (the plugin's [Room] SnapSpot): what the ask is (1: a navmesh point), before the number too, on every
		; ask, 0 included, so a 1 never carries over.
		CMB_RoomAskKind.SetValue(aiKind as float)
	endif
	if CMB_RoomPitch && CMB_RoomRoll
		; Test 46: none until the plugin measures one for this answer (an older plugin never does).
		CMB_RoomPitch.SetValue(-1000.0)
		CMB_RoomRoll.SetValue(-1000.0)
	endif
	CMB_RoomAsk.SetValue(n as float)
	; Counted polls, not summed waits: ten 0.05s don't add up to 0.5 exactly in a float.
	int polls = (RoomAnswerWait / RoomPollInterval + 0.5) as int
	int poll = 0
	while poll < polls
		Utility.Wait(RoomPollInterval)
		poll += 1
		int answer = CMB_RoomAnswer.GetValue() as int
		if answer == n
			float clear = CMB_RoomClear.GetValue()
			lastRoomClear = clear
			; Test 46: where the plugin found room, and the ground's tilt there.
			lastRoomX = CMB_RoomAskX.GetValue()
			lastRoomY = CMB_RoomAskY.GetValue()
			if CMB_RoomAskAngle
				lastRoomAngle = CMB_RoomAskAngle.GetValue()
			endif
			string tilt = RoomTiltRead()
			if clear < 0.0
				Log(try + "room (the ground " + Whole(-clear) + " above" + tilt + ").")
			else
				Log(try + "room (the ground " + Whole(clear) + " below" + tilt + ").")
			endif
			return 1
		elseif answer == -n
			; Clear says why (the plugin's word): exactly -2 the plugin's rays aren't working there
			; (right after a load, before its test ray passes): that is no verdict, so not checked;
			; exactly -1 no ground within 100 of the asked height (a hole, or over a roof's edge);
			; other values under 0 the ground that far above the spot (over 60: a stair or a
			; bank); else how far along a ray the nearest hit was (on the bike's 110), or the
			; ground's offset below when that refused it. Test 43: the plugin writes -2 and -1 as
			; exact floats; before, everything under -1.5 read as not checked, so a spot under a
			; rise ended the asking (the first spot taken untested, or where it waited) instead of
			; going on to the next.
			float clear = CMB_RoomClear.GetValue()
			lastRoomClear = clear
			; Test 46: a spot a call can take for the most room comes with its ground's tilt too.
			string tilt = RoomTiltRead()
			if clear == -2.0
				Log(try + "not checked (the plugin's rays aren't working here)" + asUnchecked)
				return -2
			elseif clear == -3.0
				; Test 44 (the plugin's [Room] Line): a fence or a wall between the player and the spot.
				Log(try + "none (no clear line from the player to it).")
			elseif clear == -4.0
				; 2026-11-09a (the plugin's [Room] ActorRoom; its ParkGuard's ask, kind 2): an actor in the spot's place,
				; or anyone, the player too, in the parked bike's. Without this the -4 would read as the ground 4 above.
				if aiKind == 2 || aiKind == 3
					Log(try + "none (someone in its place).")
				else
					Log(try + "none (an actor in its place).")
				endif
			elseif clear == -1.0
				Log(try + "none (no ground within reach of the spot).")
			elseif clear < 0.0
				Log(try + "none (the ground " + Whole(-clear) + " above the spot).")
			else
				Log(try + "none (the nearest hit " + Whole(clear) + " along a ray, on the bike's 110, or the ground " + Whole(clear) + " off" + tilt + ").")
			endif
			return -1
		endif
	endwhile
	; The literal, not the float: Papyrus prints 0.500000 (RoomAnswerWait).
	Log(try + "not checked (no answer in 0.5 s).")
	return 0
EndFunction

; The BikeSpots, then (test 46) the AroundSpots: the player's forward and right offsets as
; PlaceBike takes them, and the heading's turn from the player's (SpotTurn).
float Function SpotForward(int aiSpot)
	if aiSpot < 2
		return CallAheadDistance
	elseif aiSpot < 4
		return 150.0
	elseif aiSpot < 6
		return 300.0
	elseif aiSpot < 7
		return 100.0
	elseif aiSpot < 9
		return -100.0   ; beside the player, the nose 10 ahead of them
	elseif aiSpot < 10
		return -120.0   ; behind, across: 80 to 160 behind them
	endif
	return -CallAheadDistance
EndFunction

float Function SpotRight(int aiSpot)
	if aiSpot == 7
		return ParkSideOffset
	elseif aiSpot == 8
		return -ParkSideOffset
	elseif aiSpot >= 6
		return 0.0
	elseif aiSpot % 2 == 0
		return 60.0
	endif
	return -60.0
EndFunction

float Function SpotTurn(int aiSpot)
	if aiSpot == 9
		return 90.0
	endif
	return 0.0
EndFunction

; "220 ahead, 60 right", "220 ahead, 60 left", "100 ahead"; test 46's "100 behind, 110 right",
; "120 behind, across", "220 behind".
string Function SpotText(int aiSpot)
	float forward = SpotForward(aiSpot)
	float right = SpotRight(aiSpot)
	string text = Whole(forward) + " ahead"
	if forward < 0.0
		text = Whole(-forward) + " behind"
	endif
	if right > 0.0
		text += ", " + Whole(right) + " right"
	elseif right < 0.0
		text += ", " + Whole(-right) + " left"
	endif
	if SpotTurn(aiSpot) != 0.0
		text += ", across"
	endif
	return text
EndFunction

; 2026-11-09a (the plugin's [Room] SnapOrder): the ground it wrote for any answer, with a tilt or without (0: none; PickBikeSpot's
; bestGroundSeen, the most room's 3-D snap). RoomTiltRead's.
float lastRoomGroundSeen = 0.0

; Test 46: the ground's tilt under the wheels at the spot just answered (the plugin's [Room]
; ParkTilt: CMB_RoomPitch over -1000) into lastRoomPitch/Roll/Ground and lastRoomTilted, and its
; words for the spot's line ("" without).
string Function RoomTiltRead()
	lastRoomGroundSeen = 0.0
	if CMB_RoomGround
		lastRoomGroundSeen = CMB_RoomGround.GetValue()
	endif
	lastRoomTilted = false
	if !CMB_RoomPitch || !CMB_RoomRoll || !CMB_RoomGround || CMB_RoomPitch.GetValue() <= -999.0
		return ""
	endif
	lastRoomPitch = CMB_RoomPitch.GetValue()
	lastRoomRoll = CMB_RoomRoll.GetValue()
	lastRoomGround = CMB_RoomGround.GetValue()
	lastRoomTilted = true
	return ", its wheels' ground at pitch " + Tenths(Math.Abs(lastRoomPitch)) + Ternary(lastRoomPitch < 0.0, " down", " up") + ", roll " + Tenths(Math.Abs(lastRoomRoll))
EndFunction

; A value to the nearest whole unit ("12", "-3"): Papyrus prints floats with six decimals.
string Function Whole(float afValue)
	if afValue >= 0.0
		return "" + ((afValue + 0.5) as int)
	endif
	return "" + ((afValue - 0.5) as int)
EndFunction

; A value of 0 or more to one decimal ("1.5"), as CMB_RamScript prints them.
string Function Tenths(float afValue)
	int tenths = (afValue * 10.0 + 0.5) as int
	if tenths < 0
		tenths = 0
	endif
	return (tenths / 10) + "." + (tenths % 10)
EndFunction

; The bike left outside a door (LeaveBikeOutside) comes to the player when they're next
; outdoors in an open worldspace, in the one it waits in and within DoorBringDistance of it:
; once the teleport out is over (HandleTeleport; test 40: decided in the event, it still saw
; Diamond City and brought nothing), after a load, or when the keys or the hotkey are used
; (asWho says which). Quietly, as calling it does but with no sound or message: it was parked
; there. Test 39: ridden up Diamond City's narrow
; stairwell to the gate, the bike was left where it was last put, 110 units to the rider's
; right at their height and not settled, inside or behind the wall: coming out, the tester
; found no bike in front of the gate or in the square. True if it came. Coming out of the
; same door the player is often within MountRange of the spot it was left at, and that spot
; is the one in the wall, so it's brought then too; a player who walked back to the bike gets
; on instead (ToggleRide and HandleKeys try the bike beside them first, and getting on clears
; the mark). Every refusal is logged with its reason (test 40: they were silent). Test 41: it
; goes to the first of the bike's spots with room, or stays where it waited when none has
; (RollBikeUp); true then too, it's as the rider left it.
bool Function BringBikeFromDoor(string asWho)
	if !bikeAtDoor
		return false
	elseif riding || busy
		Log("Bike not brought from the door (" + asWho + "): " + Ternary(riding, "riding.", "busy (" + BusyText() + ")."))
		return false
	endif
	busy = true
	NoteBusy("bringing the bike from a door")
	string refusal = ""
	if PlayerRef.IsInInterior()
		refusal = "indoors"
	elseif InClosedWorld()
		refusal = "in an enclosed worldspace (" + lastWorld + ")"
	elseif swimming
		refusal = "swimming"
	elseif lastWorld != doorWorld
		; InClosedWorld has just read the player's worldspace into lastWorld.
		refusal = "in " + lastWorld + ", the bike waits in " + doorWorld
	endif
	if refusal != ""
		busy = false
		Log("Bike not brought from the door (" + asWho + "): " + refusal + ".")
		return false
	endif
	if bikeInside
		; It came in with the player (LeaveBikeOutside): brought from there, whatever the distance.
		; Where it waits is inside: with room at no spot, the spot a call takes (test 43: the one
		; with the most room, CallTakesBestSpot; else the first).
		RollBikeUp(false)
		if rollRefused
			; Test 46: no spot with room around the player (the plugin's [Room] LineFallback=0): it
			; stays hidden, still marked; a press goes on to a call, which says so.
			busy = false
			Log("Bike not brought (" + asWho + ") from where the player went in: no spot with room around the player, kept hidden.")
			return false
		endif
		busy = false
		Log("Bike brought (" + asWho + ") from where the player went in, kept hidden there: outdoors in " + doorWorld + " again.")
		return true
	endif
	; The bike too: a tick that slipped past the ride's re-check can have put it beside the
	; player after the mark was set, inside the town. A distance across worldspaces means
	; nothing, so it's left to calling, which brings it from anywhere.
	WorldSpace bikeWorld = BikeRef.GetWorldSpace()
	if bikeWorld != doorWorld
		busy = false
		Log("The bike marked at a door in " + doorWorld + " is in " + bikeWorld + ": not brought, calling it brings it.")
		return false
	endif
	float distance = PlayerRef.GetDistance(BikeRef)
	if distance > DoorBringDistance
		busy = false
		Log("Out " + distance + " units from the door the bike waits at: it stays there.")
		return false
	endif
	bool moved = RollBikeUp(true)
	busy = false
	if moved
		Log("Bike brought from the door it waited at, " + distance + " units away.")
	else
		Log("The bike is left where it waited, " + distance + " units away: no spot with room found (the spot lines above say why).")
	endif
	return moved
EndFunction

; The bike is with the player again (getting on, calling it, bringing it): it no longer waits
; at a door.
Function ForgetDoor()
	if bikeAtDoor
		bikeAtDoor = false
		bikeInside = false
		doorWorld = None
		UpdateTeleportWatch()
	endif
EndFunction

; OnPlayerTeleport is wanted while riding (a door or a fast travel ends the ride), while the
; keys wait to be handed out (the first time the player is outdoors) and while the bike waits
; at a door (it's brought when the player comes out); not otherwise.
Function UpdateTeleportWatch()
	if riding || !keysDelivered || bikeAtDoor
		RegisterForPlayerTeleport()
	else
		UnregisterForPlayerTeleport()
	endif
EndFunction

Function OpenSideBag()
	; Opening a container that sits in another cell works with a plain Activate.
	SideBagRef.Activate(PlayerRef, true)
EndFunction

; Console escape hatch: undoes everything riding changed, whatever state we're in.
Function EmergencyReset()
	if customising || lookKit || lookBox
		; 2026-11-07a: a Customise session that lost its way ended, the field kit put away.
		customising = true
		lookEnding = false
		EndCustomise("the emergency reset")
	endif
	teleportPending = false
	CancelTimer(TimerTeleport)
	CancelTimer(TimerTick)
	CancelTimer(TimerKeys)
	UnregisterForPlayerTeleport()
	busy = true
	NoteBusy("the emergency reset")
	if !PlayerRef.IsInInterior() && !InClosedWorld()
		ParkBesidePlayer()
		ForgetDoor()
	elseif riding
		; Indoors or in a walled town: the bike is still shadowing the last outdoor spot, outside
		; the door that was taken.
		LeaveBikeOutside(true)
	endif
	FinishRide()
	RemoveBikeArmor(true)   ; 2026-11-09a (test 51, FastMount): a clean slate: the kept worn bike dropped too
	; 2026-11-01a: whatever the script lost track of, the player's own footstep sounds are back.
	if AudioCategoryFSTplayer
		AudioCategoryFSTplayer.UnMute()
		fxMuted = false
	endif
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
		FxStartWaterLoop()   ; 2026-11-01a: after the engine's offer, outside busy (its wait holds nothing up)
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
	elseif aiTimerID == TimerTeleport
		CheckTeleport()
	elseif aiTimerID == TimerBusyWatch
		BusyWatchFired()
	elseif aiTimerID == TimerAPWatch
		APWatchPoll()
	elseif aiTimerID == TimerPipboyCheck
		PipboyPoseCheck()
	elseif aiTimerID == TimerUseCamera
		UseCameraCheck()   ; 2026-11-02a
	elseif aiTimerID == TimerStaggerOver
		StaggerOverLine()   ; 2026-11-02a
	elseif aiTimerID == TimerKit
		KitTick()   ; 2026-11-07a: the field kit's session, once a second
	elseif aiTimerID == TimerLook
		LookFollowUp()   ; 2026-11-07a: the look on the first-person and worn bikes, outside busy
	elseif aiTimerID == TimerParkGuard
		ParkGuardTick()   ; 2026-11-09a: the parked bike kept hidden (ParkGuard), outside busy
	endif
EndEvent

; Test 40: the event comes while the player is still where the teleport started; they're moved
; seconds later, during the loading screen. Decided here, the way out of Diamond City still saw the
; town and brought no bike, the way in still saw the gate and brought it there, and a fast
; travel's ride tick put the bike beside the player after the move ("left hidden"). So it's only
; noted here, with where the player is now; what it means is decided once it's over
; (HandleTeleport): when the loading screen closes, or when a look finds the player moved
; (CheckTeleport). Ride ticks wait for it.
Event OnPlayerTeleport()
	if teleportsAtOnce
		DecideTeleportNow()
		return
	endif
	if teleportPending
		Log("Teleport seen again (t " + Utility.GetCurrentRealTime() + ") before the last one was handled: the first reading kept.")
		return
	endif
	; Claimed before calling anything: every call below lets another thread run.
	teleportPending = true
	teleportFromKnown = true
	teleportChecks = 0
	teleportSkipLogged = false
	; The loading screen may be up already.
	loadingSeen = loadingOpen
	teleportAt = Utility.GetCurrentRealTime()
	Cell here = PlayerRef.GetParentCell()
	teleportFromWorld = PlayerRef.GetWorldSpace()
	teleportFromInside = here && here.IsInterior()
	teleportFromX = PlayerRef.GetPositionX()
	teleportFromY = PlayerRef.GetPositionY()
	Log("Teleport seen (t " + teleportAt + "): the player in " + PlaceText(here, teleportFromWorld) + " at (" + teleportFromX + ", " + teleportFromY + "); riding " + riding + ", bike at a door " + bikeAtDoor + ".")
	StartTimer(TeleportCheckInterval, TimerTeleport)
EndEvent

; As up to test 40 (the switch, DecideTeleportsAtOnce): decided in the event itself.
Function DecideTeleportNow()
	if riding
		hasLastPos = false
		RideTick()
		return
	endif
	if !keysDelivered
		TryDeliverKeys()
	endif
	BringBikeFromDoor("the teleport")
EndFunction

; The loading screen, watched for good (OnInit, OnGameReloaded): a pending teleport is handled
; when it closes, with the player where the teleport took them.
Event OnMenuOpenCloseEvent(string asMenuName, bool abOpening)
	if asMenuName == LookMenuName
		LookMenu(abOpening)   ; 2026-11-07a: the field kit's armour menu, registered only while customising
		return
	endif
	if asMenuName == PipboyMenuName || asMenuName == FavoritesMenuName
		RiderMenu(asMenuName, abOpening)   ; 2026-11-01a, registered only while riding
		return
	endif
	if asMenuName != LoadingMenuName
		return
	endif
	loadingOpen = abOpening
	if abOpening
		if teleportPending
			loadingSeen = true
		endif
		Log("Loading screen up" + Ternary(teleportPending, ", a teleport pending.", "."))
	elseif !teleportPending
		Log("Loading screen over.")
	elseif PlayerRef.GetParentCell()
		Log("Loading screen over.")
		HandleTeleport("the loading screen closed")
	else
		; Not somewhere yet: the looks go on, by the player's place alone.
		loadingSeen = false
		Log("Loading screen over, the player in no cell yet: the next look decides.")
		StartTimer(TeleportCheckInterval, TimerTeleport)
	endif
EndEvent

; Every TeleportCheckInterval while a teleport is pending: has the player arrived? It waits while
; the loading screen or any menu is up, while the player is in no cell, and once a loading screen
; was seen until it closes (OnMenuOpenCloseEvent decides then). Otherwise it decides when the
; player is seen moved, or after TeleportSettleChecks looks without (a teleport with no loading
; screen, or an event sent after the move), and after TeleportMaxChecks whatever else.
Function CheckTeleport()
	if !teleportPending
		return
	endif
	teleportChecks += 1
	Cell here = PlayerRef.GetParentCell()
	bool menu = Utility.IsInMenuMode()
	WorldSpace world = PlayerRef.GetWorldSpace()
	string how = ""
	if teleportChecks >= TeleportMaxChecks
		how = "the " + (TeleportMaxChecks * TeleportCheckInterval) as int + " s cap, look " + teleportChecks
	elseif here && !loadingOpen && !menu && !loadingSeen
		bool inside = here.IsInterior()
		float dx = PlayerRef.GetPositionX() - teleportFromX
		float dy = PlayerRef.GetPositionY() - teleportFromY
		float distance = Math.Sqrt(dx * dx + dy * dy)
		if !teleportFromKnown
			how = "look " + teleportChecks + ", after loading a save"
		elseif world != teleportFromWorld
			how = "look " + teleportChecks + ": moved into another worldspace"
		elseif inside != teleportFromInside
			how = "look " + teleportChecks + ": moved " + Ternary(inside, "indoors", "outdoors")
		elseif distance > TeleportMoved
			how = "look " + teleportChecks + ": moved " + distance + " units"
		elseif teleportChecks >= TeleportSettleChecks
			how = "look " + teleportChecks + ": not moved in " + (TeleportSettleChecks * TeleportCheckInterval * 1000.0) as int + " ms, no loading screen seen"
		endif
	endif
	if how == ""
		StartTimer(TeleportCheckInterval, TimerTeleport)
	else
		HandleTeleport(how)
	endif
EndFunction

; The teleport is over: decided now, with the player where it took them. Riding, the ride tick
; looks (a door or a fast travel into a place the bike can't go ends the ride); otherwise the keys
; are handed out if they're still to come, and the bike waiting at a door is brought.
Function HandleTeleport(string asHow)
	if !teleportPending
		return
	endif
	bool fromLoad = !teleportFromKnown
	; No call between the test and the clear: two threads can't both get past.
	teleportPending = false
	CancelTimer(TimerTeleport)
	; Riding: the tick below now, the timer's next a tick after it. The timer's own, due any
	; moment, would run beside this one (test 40's 15:31:35 had two ticks at once, one putting the
	; bike back on while the other ended the ride), so it's stopped first, before the log line's
	; calls.
	bool tickNow = riding
	if tickNow
		CancelTimer(TimerTick)
	endif
	if teleportPending
		; A new teleport came in between, and its look was just cancelled: looked at again, and
		; the ticks go on (they wait for it).
		StartTimer(TeleportCheckInterval, TimerTeleport)
		if tickNow && riding
			StartTimer(TickInterval, TimerTick)
		endif
		return
	endif
	Log("Teleport handled (" + asHow + ", " + (Utility.GetCurrentRealTime() - teleportAt) + " s after it): the player in " + PlaceText(PlayerRef.GetParentCell(), PlayerRef.GetWorldSpace()) + "; riding " + riding + ", bike at a door " + bikeAtDoor + ".")
	if riding
		hasLastPos = false
		RideTick()
		if riding
			StartTimer(TickInterval, TimerTick)
		endif
	else
		if !keysDelivered
			TryDeliverKeys()
		endif
		if bikeAtDoor
			BringBikeFromDoor(Ternary(fromLoad, "the load", "the teleport"))
		endif
	endif
EndFunction

; Console, test 41's switch: cqf CMB_ControllerQuest DecideTeleportsAtOnce 1 decides a teleport
; in OnPlayerTeleport itself, before the player is moved, as up to test 40; 0 (the default) waits
; for it to be over. Kept in the save.
Function DecideTeleportsAtOnce(int aiAtOnce)
	teleportsAtOnce = aiAtOnce != 0
	teleportPending = false
	CancelTimer(TimerTeleport)
	Log("Teleports decided " + Ternary(teleportsAtOnce, "at once, in the event (as up to test 40).", "once they're over (test 41)."))
EndFunction

Function HandleKeys()
	; Wait doesn't count time spent in menus, so this also waits for the
	; Pip-Boy to close when the keys were used from there.
	Utility.Wait(0.1)
	bool near = IsBikeNearPlayer()
	Log("Keys: " + PressState(near) + ".")
	if busy
		Log("Keys ignored: busy (" + BusyText() + ").")
		return
	endif
	if riding
		Log("Keys: getting off.")
		Dismount()
	elseif near
		; First, as in ToggleRide: beside the bike the keys get on, whatever door mark is left.
		Log("Keys: the bike beside the player: getting on.")
		Mount()
	else
		if bikeAtDoor
			Log("Keys: the bike waits at a door: bringing it.")
			if BringBikeFromDoor("the keys")
				; It waited outside the door the player came out of: it's here now, the next use gets
				; on. Left where it waited (no spot with room), the mark is cleared and the use goes
				; on to the menu, whose call takes the spot a call takes (test 43: the one with the
				; most room, CallTakesBestSpot; else the first).
				return
			endif
		endif
		Log("Keys: the menu.")
		int choice = CMB_KeysMenu.Show()
		Log("Keys menu: " + KeysMenuChoice(choice) + ".")
		if choice == 0
			CallBike()
		elseif choice == 1
			OpenSideBag()
		endif
	endif
EndFunction

string Function KeysMenuChoice(int aiChoice)
	if aiChoice == 0
		return "Call it here"
	elseif aiChoice == 1
		return "Open side bag"
	elseif aiChoice == 2
		return "Cancel"
	endif
	return "no answer (" + aiChoice + ")"
EndFunction

; Runs every second while riding, and once a teleport is over (HandleTeleport).
Function RideTick()
	if busy || !riding
		return
	endif
	if StopEngineAtDeath && (engineIdle > 0 || engineCruise > 0) && PlayerRef.IsDead()
		; Test 44: the death camera, before the load that ends the ride (StopEngineAtDeath).
		StopEngineLoops()
		Log("Engine sound: the rider is dead: the engine loops stopped (the load that follows ends the ride).")
	endif
	CheckTiltLive()
	if wornSlotToLog
		; Test 41: the bike's slot, read a tick after the equip (EquipBike).
		wornSlotToLog = false
		CallGearRestore("LogWornSlots")
	endif
	; Test 40: a tick between a teleport's event and the player's move still sees the place being
	; left, and its shadow move can land after the move (the bike beside the player in Diamond
	; City, 15:31:35). Until the teleport is handled, the bike stays where the last tick put it.
	if teleportPending
		if !teleportSkipLogged
			teleportSkipLogged = true
			Log("Ride tick skipped: a teleport is pending (the bike stays where the last tick put it).")
		endif
		return
	endif

	; Things the bike can't follow you into. The bike has been shadowing the
	; player, so it's left at the last outdoor spot we saw (a walled town's gate
	; is a load door like any interior's).
	float now = Utility.GetCurrentGameTime()
	; One read of the cell. A player in transit has none, and IsInInterior and InClosedWorld both
	; read that as outdoors: nothing is done until they're somewhere.
	Cell here = PlayerRef.GetParentCell()
	if !here && !teleportsAtOnce
		if !noCellLogged
			noCellLogged = true
			Log("Ride tick: the player is in no cell (in transit): nothing done.")
		endif
		return
	endif
	noCellLogged = false
	if (here && here.IsInterior()) || InClosedWorld()
		; A door takes no more than a tick, a fast travel game hours (FastTravelMinutes).
		float minutes = (now - lastOutdoorTime) * 1440.0
		DismountGoingIn(minutes > FastTravelMinutes, minutes)
		return
	endif
	lastOutdoorTime = now
	lastOpenWorld = lastWorld   ; InClosedWorld has just read it
	if PlayerRef.IsInPowerArmor()
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
	SetHeadlampLive(true)
	FollowHeadlamp()
	; 2026-11-01a: the tail light and the first-person bike, once the plugin is seen at work (it
	; writes CMB_GroundNormalZ, which getting on zeroes), then kept with the rider (FollowTwins).
	if !twinsPlaced && PluginAlive() && StillRiding()
		PlaceTwins()
	endif
	FollowTwins()

	; The disabled bike follows the player, so it can be dropped here at any moment.
	if !StillRiding()
		return
	endif
	; Test 39: a tick that found the player outdoors above and gets here after a door would put
	; the bike beside them inside. Look again: the teleport's own tick, or the next, ends the ride.
	; Test 40: and not while a teleport is pending (the player can still be outside).
	if teleportPending || PlayerRef.IsInInterior() || InClosedWorld()
		return
	endif
	ShadowPlayer()
	CatchUpFollowers()

	; Also swaps between the two bikes when a weapon is drawn or put away.
	if !StillRiding()
		return
	endif
	if LookRimsMoved() || wornRefit
		; 2026-11-08a: CMB_LookCode's rim style isn't the worn bike's mods' (ApplyLook moved it): put on
		; again, so the mods follow the look (one place equips mid-ride: here). 2026-11-09a (test 51, FastMount):
		; or the kept worn bike was found with fewer mods after its equip (WornModsCheck, its line): put on afresh.
		if LookRimsMoved()
			Log("Look: the rims' style changed while riding (" + LookName(LookSlotRims, lookRimMods) + " worn, CMB_LookCode's style " + lookRimCode + "): the worn bike put on again with the look's mods")
		endif
		wornRefit = false
		RemoveBikeArmor()
	endif
	EquipBike()
	if !riding
		; The ride ended while the bike was going on: take it off again.
		RemoveBikeArmor()
		return
	endif
	UpdateSteady("the MCM switch")   ; 2026-11-01a: an MCM change is taken up mid-ride
	if riderPoseApplied
		; The graph can switch it back on (dialogue, for one).
		PlayerRef.SetAnimationVariableBool(HeadTrackingVariable, false)
		if !footstepsWatched
			WatchFootsteps()
		endif
		CheckRiderPose()
	endif
	if !fxCueEventsOn
		FxWatchCues()   ; 2026-11-01a: failed while the 3D wasn't loaded (as WatchFootsteps)
	endif
	FxWaterTick()
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
	elseif PlayerRef.IsInInterior() || InClosedWorld()
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

; Outdoor worldspaces that are enclosed places, where there's no room to ride either (test 39's
; wish: "dungeons or close spaces like sewers" shouldn't take the bike; those are interiors and
; are refused by IsInInterior, but the walled towns and arenas are worldspaces of their own):
; Diamond City (its two worldspaces), Goodneighbor, the pre-war Sanctuary of the intro, Far
; Harbor's memory simulation, and Nuka-World's market and amphitheater. The open worlds (the
; Commonwealth, Far Harbor's island, Nuka-World's park) and other mods' worldspaces stay open.
; Looked up by file (Mutagen's FormKeys for the three masters; a DLC that isn't installed is
; skipped), and worked out again only when the worldspace changes.
bool Function InClosedWorld()
	WorldSpace here = PlayerRef.GetWorldSpace()
	if here == lastWorld
		return lastWorldClosed
	endif
	lastWorld = here
	lastWorldClosed = false
	if !here
		return false
	endif
	if here == Game.GetFormFromFile(0x000F93, "Fallout4.esm") as WorldSpace || here == Game.GetFormFromFile(0x000F94, "Fallout4.esm") as WorldSpace
		lastWorldClosed = true   ; DiamondCityFX, DiamondCity
	elseif here == Game.GetFormFromFile(0x054BD5, "Fallout4.esm") as WorldSpace || here == Game.GetFormFromFile(0x0A7FF4, "Fallout4.esm") as WorldSpace
		lastWorldClosed = true   ; Goodneighbor, SanctuaryHillsWorld
	elseif Game.IsPluginInstalled("DLCCoast.esm") && here == Game.GetFormFromFile(0x004EA4, "DLCCoast.esm") as WorldSpace
		lastWorldClosed = true   ; DLC03VRWorldspace
	elseif Game.IsPluginInstalled("DLCNukaWorld.esm") && (here == Game.GetFormFromFile(0x052931, "DLCNukaWorld.esm") as WorldSpace || here == Game.GetFormFromFile(0x053C58, "DLCNukaWorld.esm") as WorldSpace)
		lastWorldClosed = true   ; NukaWorldAmphitheater, NukaWorldMarket
	endif
	if lastWorldClosed
		Log("In an enclosed worldspace (" + here + "): no riding, no calling the bike.")
	endif
	return lastWorldClosed
EndFunction

; Undo everything riding changed on the player and companions.
; Placing the bike is the caller's job.
Function FinishRide()
	CancelTimer(TimerTick)
	UnregisterForPlayerTeleport()

	CancelTimer(TimerEngine)
	StopEngineLoops()
	; 2026-11-01a: every way off passes here (the swim, the knock-off, doors, fast travel, the
	; reset): the rider's own footstep sounds back, the landing cues and the water loop stopped,
	; and the item, menu and stagger watches off.
	FxEndRide()
	RideWatchesOff()
	UnregisterForHitEvent(PlayerRef)
	UnregisterForAnimationEvent(PlayerRef, FootstepEvent)
	footstepsWatched = false

	RemoveBikeArmor()
	CallGearRestore("RestoreSlot")
	SetCameraLive(false)
	SetSlopeLive(false)
	SetTiltLive(false)
	CallRam("EndRide")
	SetRamCombat(false)   ; 2026-11-02a: no fight told while not riding
	SetHeadlampLive(false)
	RemoveHeadlamp()
	if CMB_ParkUpZ
		CMB_ParkUpZ.SetValue(0.0)   ; that spot is used up
	endif
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
	UpdateSteady("getting off")
	; Test 44: a ride end overlapping the start (the hotkey or the keys just after getting on, deep
	; water) found its loops still in their Play above, ids not yet kept, and StartEngineLoops looked
	; at riding before this: stopped again now (nothing to do when none plays). A start that looks
	; after this stops them itself (StartEngineLoops, OfferEngineLoops).
	StopEngineLoops()
	; Watched again if the bike waits at a door or the keys are still to come.
	UpdateTeleportWatch()
	StartTimer(CleanupDelay, TimerCleanup)
	APWatchRideEnd()   ; test 46: off the bike, AP logged for a while
EndFunction

; Safety net after every dismount: whatever a ride tick that was still running
; did, the bike comes off and head tracking is back on.
Function CleanUpAfterRide()
	if riding || busy
		return
	endif
	RemoveBikeArmor()
	PlayerRef.SetAnimationVariableBool(HeadTrackingVariable, true)
	UpdateSteady("the clean-up after the ride")
EndFunction

; abParkBesidePlayer: park next to the player (they're outdoors and standing).
; Otherwise the bike stays at the last outdoor spot it shadowed.
Function AutoDismount(string asMessage, bool abParkBesidePlayer)
	; Another thread may have ended the ride since the caller checked.
	if busy || !riding
		return
	endif
	busy = true
	NoteBusy("getting off by itself")
	if abParkBesidePlayer
		ParkBesidePlayer()
	else
		EnableParked(false, 0)
	endif
	FinishRide()
	busy = false
	Debug.Notification(asMessage)
	Log("Auto-dismounted: " + asMessage)
EndFunction

; The player went in where the bike can't follow (an interior, a walled town). Through a door
; the bike waits outside it and comes to them when they're out again near it
; (BringBikeFromDoor); after a fast travel it stays where the fast travel set off, and calling it
; works (test 39's 01:41:37). A bike that came in with the player is brought the next time
; they're outdoors (LeaveBikeOutside), so that's what they're told, a fast travel or not.
Function DismountGoingIn(bool abFastTravel, float afMinutes)
	; Another thread may have ended the ride since the caller checked.
	if busy || !riding
		return
	endif
	busy = true
	NoteBusy("getting off going in")
	; Test 41: logged here, past the claim, not in RideTick: at 15:57:50 and 15:59:19 the 1 s tick
	; and HandleTeleport's own tick both found the player inside and both logged it, while only the
	; first got past the check above.
	Log("Gone in " + afMinutes + " game minutes after the last tick outdoors: " + Ternary(abFastTravel, "a fast travel.", "a door."))
	bool keptInside = LeaveBikeOutside(!abFastTravel)
	FinishRide()
	busy = false
	string notice = "You leave the motorbike parked outside."
	if abFastTravel && !keptInside
		notice = "Your motorbike stays where you set off."
	endif
	Debug.Notification(notice)
	Log("Auto-dismounted: " + notice)
EndFunction

; The bike has been shadowing the player outdoors, disabled: it's shown where it was last put,
; and through a door (abAtDoor) marked as waiting there, with its worldspace. If a tick put it
; beside the player after the teleport (a door taken between that tick's look and the bike's
; move), it's in there with them: it stays hidden. Test 40 had that after a fast travel into
; Diamond City, the teleport's tick racing the move; that tick waits for the teleport now
; (RideTick), and if it happens all the same, the bike is marked as waiting at a door in the
; open worldspace of the last tick outdoors and is brought, from in there, the next time the
; player is outdoors in it (BringBikeFromDoor): true then. Saves from before that worldspace was
; kept, and the switch (DecideTeleportsAtOnce), leave it to calling, as before.
bool Function LeaveBikeOutside(bool abAtDoor)
	WorldSpace world = BikeRef.GetWorldSpace()
	bool cameIn = false
	if world
		cameIn = world == PlayerRef.GetWorldSpace()
	else
		cameIn = BikeRef.GetParentCell() == PlayerRef.GetParentCell()
	endif
	if cameIn
		if lastOpenWorld && !teleportsAtOnce
			bikeAtDoor = true
			doorWorld = lastOpenWorld
			bikeInside = true
			Log("The bike was put beside the player after they went in: kept hidden, brought to them the next time they're outdoors in " + lastOpenWorld + ", wherever that is.")
			return true
		endif
		Log("The bike was put beside the player after they went in: left hidden, calling it outdoors brings it.")
		return false
	endif
	EnableParked(false, 0)
	if abAtDoor && world
		bikeAtDoor = true
		doorWorld = world
		Log("The bike waits outside the door, in " + world + ".")
	endif
	return false
EndFunction

Function ParkBesidePlayer()
	; Test 47 (the plugin's [Room] ParkCheck, CMB_RoomOptions bit 4; test 46's getting off nosed into a
	; house's window, the bike through it): a ride that went nowhere puts the bike back where it
	; stood; else its spot is asked about as a call's, and moved or replaced where the plugin says.
	if riding && RoomOption(4)
		if ParkWhereItStood() || ParkChecked()
			return
		endif
	endif
	if ParkOnTrack()
		return
	endif
	PlaceBike(0.0, ParkSideOffset)
	EnableParked(false, 1, 0.0, true)   ; ParkSideOffset beside the player (the review of 2026-11-09a: the player not counted)
EndFunction

; Test 47 (the plugin's [Room] ParkCheck): a ride that moved the player less than ParkBackWithin
; from where they got on puts the bike back where it stood then, as it stood (Mount kept both):
; test 46's tester got on facing a house's window at point blank and got off 2 s later, and the
; parked bike went in beside the worn one, through the window. False if it wasn't seen standing
; at getting on, or the ride went farther, or (review of test 47's build) the player now stands
; where it stood: within ParkBackFore of it along its heading and ParkBackSide across it.
bool Function ParkWhereItStood()
	if !mountSpotKnown
		return false
	endif
	float dx = PlayerRef.GetPositionX() - mountPlayerX
	float dy = PlayerRef.GetPositionY() - mountPlayerY
	float dz = PlayerRef.GetPositionZ() - mountPlayerZ
	float moved = Math.Sqrt(dx * dx + dy * dy + dz * dz)
	if moved >= ParkBackWithin
		return false
	endif
	float heading = mountBikeAZ - ParkedModelYaw
	float bx = PlayerRef.GetPositionX() - mountBikeX
	float by = PlayerRef.GetPositionY() - mountBikeY
	float along = bx * Math.Sin(heading) + by * Math.Cos(heading)
	float across = bx * Math.Cos(heading) - by * Math.Sin(heading)
	if Math.Abs(along) < ParkBackFore && Math.Abs(across) < ParkBackSide
		Log("Parked bike not put back where it stood: the ride moved the player " + Whole(moved) + ", under " + Whole(ParkBackWithin) + ", but they stand where it stood (" + Whole(along) + " along its heading, " + Whole(across) + " across it): its spot asked about instead (the plugin's [Room] ParkCheck).")
		return false
	endif
	; 2026-11-09a (the plugin's [Room] ParkBack, CMB_RoomOptions bit 128; test 50's third knock-off, put back here with no
	; look 0.5 s before the crash, three raiders about): the old spot asked about first, as a call's (actors no room with its
	; ActorRoom). None: its spot asked about instead (ParkChecked). Not checked or no answer: put back as before.
	if RoomOption(128)
		float backHeading = heading
		if backHeading < 0.0
			backHeading += 360.0
		endif
		if RoomAt(mountBikeX, mountBikeY, mountBikeZ, -1, backHeading, ".", "The parked bike's old spot") == -1
			Log("Parked bike not put back where it stood: its old spot asked about first (the plugin's [Room] ParkBack): no room there (the line above says why): its spot asked about instead.")
			return false
		endif
	endif
	; MoveTo first: the bike may be in another cell (it waits in the holding cell).
	BikeRef.MoveTo(PlayerRef, mountBikeX - PlayerRef.GetPositionX(), mountBikeY - PlayerRef.GetPositionY(), mountBikeZ - PlayerRef.GetPositionZ(), false)
	BikeRef.SetAngle(mountBikeAX, mountBikeAY, mountBikeAZ)
	EnableParked(false, 0, 0.0, true)   ; the player ParkBackFore or ParkBackSide off it (the review's A2: not counted)
	Log("Parked bike put back where it stood before getting on: the ride moved the player " + Whole(moved) + " from where they got on, under " + Whole(ParkBackWithin) + " (the plugin's [Room] ParkCheck).")
	return true
EndFunction

; Test 47 (the plugin's [Room] ParkCheck): the parked bike's spot, the track just ridden's (as
; ParkOnTrack takes it, heading the way it went) or beside the player (as PlaceBike puts it), asked
; about as a call's spot is (RoomAt: the box along its heading; the plugin's Slide may move or turn
; it). The bike is disabled while riding, so it isn't in its own way. Room as asked: false, and the
; caller parks there as before. Room where the plugin moved or turned it: the bike there, settled as
; a brought bike on its checked spot (PlaceOnSpot). None: the AroundSpots, beside and behind the
; player (PickBikeSpot's park), the first with room taken. False with none of those either, or no
; answer: parked as before. Test 46: getting off nosed into a house, the spot beside the worn bike
; was through the window.
bool Function ParkChecked()
	float heading = PlayerRef.GetAngleZ()
	float x = PlayerRef.GetPositionX() + OffsetX(heading, 0.0, ParkSideOffset)
	float y = PlayerRef.GetPositionY() + OffsetY(heading, 0.0, ParkSideOffset)
	float z = PlayerRef.GetPositionZ()
	string what = "beside the player"
	if CMB_ParkX && CMB_ParkY && CMB_ParkZ && CMB_ParkAngle && CMB_ParkUpZ && CMB_ParkUpZ.GetValue() >= 0.5
		x = CMB_ParkX.GetValue()
		y = CMB_ParkY.GetValue()
		z = CMB_ParkZ.GetValue()
		heading = CMB_ParkAngle.GetValue() - ParkedModelYaw
		what = "the track just ridden"
	endif
	if heading < 0.0
		heading += 360.0
	endif
	int room = RoomAt(x, y, z, -1, heading, ".", "The park spot (" + what + ")")
	if room == 1
		float turned = lastRoomAngle - heading
		while turned > 180.0
			turned -= 360.0
		endwhile
		while turned < -180.0
			turned += 360.0
		endwhile
		float slid = Math.Sqrt((lastRoomX - x) * (lastRoomX - x) + (lastRoomY - y) * (lastRoomY - y))
		if slid <= 0.5 && Math.Abs(turned) <= 0.05
			Log("The parked bike's spot: " + what + ", as before (room there).")
			return false
		endif
		spotX = lastRoomX
		spotY = lastRoomY
		spotAngle = lastRoomAngle
		spotKnown = true
		spotGround = z - lastRoomClear
		spotGroundKnown = true
		spotPitch = lastRoomPitch
		spotRoll = lastRoomRoll
		spotTiltKnown = lastRoomTilted
		Log("The parked bike's spot: " + what + ", heading " + Whole(spotAngle) + ", where the plugin found room (" + Whole(slid) + " from the asked spot, turned " + Whole(turned) + ").")
		PlaceOnSpot(-1)
		return true
	elseif room != -1
		; Not checked (the plugin's rays, -2) or no answer (0): as before.
		Log("The parked bike's spot: " + what + ", as before (not checked).")
		return false
	endif
	int spot = PickBikeSpot(false, true)
	if spot < 0
		return false
	endif
	PlaceOnSpot(spot)
	return true
EndFunction

; With CMB_Slope.dll: on the ground just ridden, a bike length behind the player, facing
; the way it went. The plugin keeps the track of where the player's feet were on the
; ground and works out the spot and the bike's slant from it (CMB_ParkX/Y/Z, Angle, Up).
; False without the plugin, or with no such spot (a short ride, a turn just before
; stopping, in the air).
bool Function ParkOnTrack()
	if !riding
		return false   ; the spot is from the last ride (an emergency reset, say)
	endif
	if !CMB_ParkX || !CMB_ParkY || !CMB_ParkZ || !CMB_ParkAngle || !CMB_ParkUpX || !CMB_ParkUpY || !CMB_ParkUpZ
		return false
	endif
	groundZ = CMB_ParkUpZ.GetValue()
	if groundZ < 0.5
		return false
	endif
	groundX = CMB_ParkUpX.GetValue()
	groundY = CMB_ParkUpY.GetValue()
	float x = CMB_ParkX.GetValue()
	float y = CMB_ParkY.GetValue()
	float z = CMB_ParkZ.GetValue()
	; MoveTo first: the bike may be in another cell (it waits in the holding cell).
	BikeRef.MoveTo(PlayerRef, x - PlayerRef.GetPositionX(), y - PlayerRef.GetPositionY(), z - PlayerRef.GetPositionZ(), false)
	EnableParked(false, 4, CMB_ParkAngle.GetValue(), true)   ; 145 from the player's feet (the review's B1: not counted)
	return true
EndFunction

; The spot next to the player can be in mid-air or inside the rock on steep ground, so
; the parked bike is put on the ground there and tilted to match, keeping its heading:
; - on the nearest navmesh (walkable ground), tilted by four navmesh probes around it;
; - where the navmesh is too coarse to tilt by, its height is no better (test 8: half in
;   the rock): abBesidePlayer, level at the player's height; otherwise level on it;
; - no navmesh near (steep rock): abBesidePlayer, the plane under the player's feet
;   carried over to the bike, if that moves it at most MaxGroundStep up or down;
;   otherwise level where it was put.
; Test 44: abChecked, the brought bike at a spot the plugin found room at (spotX/Y, spotGround):
; a snap farther than SpotSettleMax from it is undone, the bike put back there level. Test 46:
; with the ground's tilt the plugin measured under the wheels there (spotTiltKnown, its [Room]
; ParkTilt), the bike that stays on the checked spot (the snap kept or undone) is tilted by it
; instead: test 45's call 11 was left level where the navmesh was too coarse to tilt by, call
; 10's roll was held to ParkMaxRoll's 10.
Function SettleBike(bool abBesidePlayer = false, bool abChecked = false)
	float angle = BikeRef.GetAngleZ()
	float x = BikeRef.GetPositionX()
	float y = BikeRef.GetPositionY()
	float z = BikeRef.GetPositionZ()
	BikeRef.MoveToNearestNavmeshLocation()
	if abChecked && SpotSettleMax > 0.0
		float sx = BikeRef.GetPositionX() - spotX
		float sy = BikeRef.GetPositionY() - spotY
		float sz = BikeRef.GetPositionZ() - spotGround
		float off = Math.Sqrt(sx * sx + sy * sy + sz * sz)
		if off > SpotSettleMax
			BikeRef.SetPosition(spotX, spotY, spotGround)
			if spotTiltKnown
				Log("The bike settled " + Whole(off) + " from the checked spot (the navmesh snap), over " + Whole(SpotSettleMax) + ": put back on the checked spot, on its ground.")
				TiltBikeAsMeasured(angle)
				return
			endif
			BikeRef.SetAngle(0.0, 0.0, angle)
			Log("The bike settled " + Whole(off) + " from the checked spot (the navmesh snap), over " + Whole(SpotSettleMax) + ": put back on the checked spot, level on its ground.")
			return
		endif
		Log("The bike settled " + Whole(off) + " from the checked spot (the navmesh snap, " + Whole(SpotSettleMax) + " at most).")
		if spotTiltKnown
			TiltBikeAsMeasured(angle)
			return
		endif
	endif
	float dx = BikeRef.GetPositionX() - x
	float dy = BikeRef.GetPositionY() - y
	float dz = BikeRef.GetPositionZ() - z
	if dx * dx + dy * dy + dz * dz > MaxSettleDistance * MaxSettleDistance
		BikeRef.SetPosition(x, y, z)
		if abBesidePlayer && GroundFromPlugin() && LayOnPlayerGround(angle)
			return
		endif
		BikeRef.SetAngle(0.0, 0.0, angle)
		Log("No walkable ground near the parked bike: left where it was put, level.")
		return
	endif
	if GroundFromNavmesh(angle)
		TiltParkedBike(angle, "the navmesh around it")
	elseif abBesidePlayer
		BikeRef.SetPosition(x, y, z)
		BikeRef.SetAngle(0.0, 0.0, angle)
		Log("Parked bike left level at the player's height.")
	else
		BikeRef.SetAngle(0.0, 0.0, angle)
	endif
EndFunction

; 2026-11-09a (the plugin's [Room] ParkGuard, CMB_RoomOptions bit 256; test 50's crash 0.5 s after the third knock-off: a
; stack overflow in Havok's all-hits collector, an NPC's skeleton on the stack, the bike just enabled where it stood with three
; raiders about; KO1's and KO2's spots had "an actor there (skeleton.nif), passed"). Every enable of the parked bike: its
; place asked about first (CMB_RoomAskKind 2: anyone in its box grown by the plugin's GuardMargin, the player too). No one,
; not checked or no answer: enabled (abFade), then the settle that followed each enable before (aiSettle: 0 none, 1
; SettleBike(true), 2 SettleBike(false, true), 3 SettleBike(), 4 TiltParkedBike(afAngle) on the track just ridden), and, as a
; settle can move it up to MaxSettleDistance, asked again: someone in its place now, hidden again. Someone: kept hidden (no
; collision) and looked at again every ParkGuardPoll (ParkGuardTick). Without bit 256: enabled at once (2026-11-08a). Busy is
; the caller's. The bike in another worldspace than the player's (a door, a fast travel) isn't asked about: its place
; isn't loaded around them. The review of 2026-11-09a (A1, A2, B1: the player held the bike at getting off's park on a bend,
; a call's spot 6 100 ahead, ParkWhereItStood's 58-73 across, the field kit's stand): the player counts only within the bike's
; own box (the plugin's Fore and Side and their capsule: ParkBackFore and ParkBackSide, as the placements keep it off them),
; GuardMargin grows it for everyone else; abPlaced (a place the script chose clear of the player: getting off's park, a call's,
; a bring's or the shore's spot, the guard's own move, the bike again where it stood: a refused call, a getting on undone):
; the player not counted at all, at the ask and after the settle (CMB_RoomAskKind 3, the plugin's CMB_RoomOptions bit 512; an
; older plugin: kind 2). The hold's polls count the player (they may have walked into the hidden bike's place since).
bool parkHeld = false
bool parkHeldFade = false
int parkHeldSettle = 0
float parkHeldAngle = 0.0
float parkHeldGX = 0.0
float parkHeldGY = 0.0
float parkHeldGZ = 0.0
float parkHeldSince = 0.0
bool parkHeldMoved = false
bool parkGuardMoving = false   ; ParkGuardTick's new spot being placed: a hold there keeps the first one's time and its "once"

Function EnableParked(bool abFade, int aiSettle, float afAngle = 0.0, bool abPlaced = false)
	ParkedLookDueNow("the bike's enable")   ; 2026-11-09a (test 51, FastMount): a look put on while riding, on it first
	parkHeld = false
	if !RoomOption(256) || BikeRef.GetWorldSpace() != PlayerRef.GetWorldSpace()
		BikeRef.Enable(abFade)
		ParkSettle(aiSettle, afAngle)
		return
	endif
	int kind = 2
	if abPlaced && RoomOption(512)
		kind = 3
	endif
	if ParkGuardAsk(kind) == -1
		ParkGuardHold(abFade, aiSettle, afAngle, "someone in its place")
		return
	endif
	BikeRef.Enable(abFade)
	ParkSettle(aiSettle, afAngle)
	ParkGuardAfterSettle(aiSettle, kind)
EndFunction

; The settle that followed the enable (EnableParked's aiSettle).
Function ParkSettle(int aiSettle, float afAngle)
	if aiSettle == 1
		SettleBike(true)
	elseif aiSettle == 2
		SettleBike(false, true)
	elseif aiSettle == 3
		SettleBike()
	elseif aiSettle == 4
		TiltParkedBike(afAngle, "the track just ridden")
	endif
EndFunction

; The plugin's word on the parked bike's place where it stands now: 1 no one, -1 someone, -2 not checked, 0 no answer. aiKind:
; 2 the player counted (in the bike's own box), 3 not (EnableParked's abPlaced).
int Function ParkGuardAsk(int aiKind)
	float heading = BikeRef.GetAngleZ() - ParkedModelYaw
	if heading < 0.0
		heading += 360.0
	endif
	return RoomAt(BikeRef.GetPositionX(), BikeRef.GetPositionY(), BikeRef.GetPositionZ(), -1, heading, ".", "The parked bike's place", aiKind)
EndFunction

; After a settle that may have moved it (any but 0): someone in its place now, hidden again and held (the settle done). aiKind:
; the enable's own ask's (the settle is part of placing it).
Function ParkGuardAfterSettle(int aiSettle, int aiKind)
	if aiSettle == 0
		return
	endif
	if ParkGuardAsk(aiKind) == -1
		BikeRef.Disable()
		Log("The parked bike settled into someone's place (the plugin's [Room] ParkGuard): hidden again.")
		ParkGuardHold(false, 0, 0.0, "settled into someone's place")
	endif
EndFunction

; Kept hidden: the enable and its settle wait (the track's tilt keeps its ground, TiltParkedBike's groundX/Y/Z).
Function ParkGuardHold(bool abFade, int aiSettle, float afAngle, string asWhy)
	BikeRef.Disable()
	parkHeld = true
	parkHeldFade = abFade
	parkHeldSettle = aiSettle
	parkHeldAngle = afAngle
	parkHeldGX = groundX
	parkHeldGY = groundY
	parkHeldGZ = groundZ
	if !parkGuardMoving
		parkHeldSince = Utility.GetCurrentRealTime()
	endif
	parkHeldMoved = parkGuardMoving
	; The literals, not the floats: Papyrus prints 0.500000 (ParkGuardPoll, ParkGuardWait). The review of 2026-11-09a (A6): a
	; hold from ParkGuardTick's move polls every ParkGuardWait.
	Log("The parked bike kept hidden: " + asWhy + " (the plugin's [Room] ParkGuard): looked at again every " + Ternary(parkHeldMoved, "2 s", "0.5 s") + ".")
	if parkHeldMoved
		StartTimer(ParkGuardWait, TimerParkGuard)
	else
		StartTimer(ParkGuardPoll, TimerParkGuard)
	endif
EndFunction

; The hold ended by another way of bringing the bike (getting on, a call: the caller's busy).
Function ParkGuardEnd(string asWhy)
	if !parkHeld
		return
	endif
	parkHeld = false
	CancelTimer(TimerParkGuard)
	Log("The parked bike's guard ended after " + Whole(Utility.GetCurrentRealTime() - parkHeldSince) + " s: " + asWhy + " (ParkGuard).")
EndFunction

; ParkGuardPoll: clear, shown with the kept settle (and asked again after it); still taken past ParkGuardMax, once a new spot
; beside or behind the player (PickBikeSpot's park: AroundSpots, each asked about with the plugin's ActorRoom; found, placed
; there, which guards again), else it waits, looked at every ParkGuardWait. Not checked (the plugin's rays, after a load):
; held, till ParkGuardMax, then shown as before. The player gone elsewhere (a fast travel, a door): left there hidden, the
; next call brings it.
Function ParkGuardTick()
	if !parkHeld
		return
	endif
	if riding || busy
		StartTimer(ParkGuardPoll, TimerParkGuard)   ; tried again at the next poll
		return
	endif
	busy = true
	NoteBusy("the parked bike's guard")
	float held = Utility.GetCurrentRealTime() - parkHeldSince
	if BikeRef.GetWorldSpace() != PlayerRef.GetWorldSpace() || PlayerRef.GetDistance(BikeRef) > 4096.0
		parkHeld = false
		busy = false
		Log("The parked bike kept hidden after " + Whole(held) + " s: the player went elsewhere: it waits there hidden; calling it brings it (ParkGuard).")
		return
	endif
	int answer = ParkGuardAsk(2)   ; the player counted (in its own box): they may have walked into its place since
	if answer == 1 || answer == 0 || (answer == -2 && held >= ParkGuardMax)
		parkHeld = false
		BikeRef.Enable(parkHeldFade)
		groundX = parkHeldGX
		groundY = parkHeldGY
		groundZ = parkHeldGZ
		ParkSettle(parkHeldSettle, parkHeldAngle)
		Log("The parked bike shown after " + Whole(held) + " s: " + Ternary(answer == 1, "its place clear", "its place not checked") + " (ParkGuard).")
		ParkGuardAfterSettle(parkHeldSettle, 2)
		busy = false
		return
	endif
	if answer == -1 && held >= ParkGuardMax && !parkHeldMoved
		parkHeldMoved = true
		int spot = PickBikeSpot(false, true)
		if spot >= 0
			parkHeld = false
			Log("The parked bike still kept hidden after " + Whole(held) + " s: a spot beside or behind the player with room (ParkGuard).")
			parkGuardMoving = true
			PlaceOnSpot(spot)
			parkGuardMoving = false
			busy = false
			return
		endif
		Log("The parked bike still kept hidden after " + Whole(held) + " s: no spot beside or behind the player is free; it waits (calling it brings it).")
	endif
	busy = false
	if parkHeldMoved
		StartTimer(ParkGuardWait, TimerParkGuard)
	else
		StartTimer(ParkGuardPoll, TimerParkGuard)
	endif
EndFunction

; A save made while the bike was kept hidden: the poll again (a load ends a save's timers' meaning).
Function ParkGuardAfterLoad()
	if parkHeld
		Log("The parked bike was kept hidden when the game was saved (ParkGuard): looked at again.")
		StartTimer(ParkGuardPoll, TimerParkGuard)
	endif
EndFunction

; Test 46 (CMB_Slope.dll's [Room] ParkTilt): the brought bike on its checked spot tilted to the
; ground the plugin measured under its wheels there (spotPitch, spotRoll: the pitch held to 45, the
; roll to its [Room] ParkRoll, 20 by default, rather than ParkMaxRoll's 10), keeping its heading
; afAngle; level if CMB_MaxTilt is 0, as every park.
Function TiltBikeAsMeasured(float afAngle)
	if CMB_MaxTilt && CMB_MaxTilt.GetValue() <= 0.0
		BikeRef.SetAngle(0.0, 0.0, afAngle)
		Log("Parked bike level on the checked spot (tilting turned off).")
		return
	endif
	BikeRef.SetAngle(spotPitch, spotRoll, afAngle)
	Log("Parked bike tilted to the ground under its wheels (the plugin's, on the checked spot): pitch " + spotPitch + ", roll " + spotRoll + ".")
EndFunction

; The ground under the player as CMB_Slope.dll sees it now, into groundX/Y/Z.
; False without the plugin, or while the player isn't on the ground.
bool Function GroundFromPlugin()
	if !CMB_GroundNormalX || !CMB_GroundNormalY || !CMB_GroundNormalZ
		return false
	endif
	groundZ = CMB_GroundNormalZ.GetValue()
	if groundZ < 0.17
		return false
	endif
	groundX = CMB_GroundNormalX.GetValue()
	groundY = CMB_GroundNormalY.GetValue()
	float norm = Math.Sqrt(groundX * groundX + groundY * groundY + groundZ * groundZ)
	groundX = groundX / norm
	groundY = groundY / norm
	groundZ = groundZ / norm
	return true
EndFunction

; The bike stands next to the player: the ground under their feet (a plane through them
; with the normal groundX/Y/Z) says how high the ground is under the bike and how it
; leans. False if that would move the bike more than MaxGroundStep up or down: the
; ground there isn't that plane.
bool Function LayOnPlayerGround(float afAngle)
	float x = BikeRef.GetPositionX()
	float y = BikeRef.GetPositionY()
	float rise = -(groundX * (x - PlayerRef.GetPositionX()) + groundY * (y - PlayerRef.GetPositionY())) / groundZ
	if Math.Abs(rise) > MaxGroundStep
		Log("The ground under the player would put the parked bike " + rise + " up: not trusting it.")
		return false
	endif
	BikeRef.SetPosition(x, y, PlayerRef.GetPositionZ() + rise)
	TiltParkedBike(afAngle, "the ground under the player")
	return true
EndFunction

; Without the plugin: four probes around the parked bike, each moved to the nearest
; navmesh; the plane through them is the ground (groundX/Y/Z). False where the navmesh
; is too coarse to tell (a probe pulled far sideways) or too steep to be ground.
bool Function GroundFromNavmesh(float afAngle)
	if !GroundProbeRef
		return false
	endif
	float[] px = new float[4]
	float[] py = new float[4]
	float[] pz = new float[4]
	float bikeX = BikeRef.GetPositionX()
	float bikeY = BikeRef.GetPositionY()
	bool ok = true
	int i = 0
	while i < 4 && ok
		; Front, back, right, left of the bike's middle.
		float along = 0.0
		float across = 0.0
		if i == 0
			along = ProbeAlong
		elseif i == 1
			along = -ProbeAlong
		elseif i == 2
			across = ProbeAcross
		else
			across = -ProbeAcross
		endif
		float ox = OffsetX(afAngle, along, across)
		float oy = OffsetY(afAngle, along, across)
		GroundProbeRef.MoveTo(BikeRef, ox, oy, 0.0, false)
		GroundProbeRef.MoveToNearestNavmeshLocation()
		px[i] = GroundProbeRef.GetPositionX()
		py[i] = GroundProbeRef.GetPositionY()
		pz[i] = GroundProbeRef.GetPositionZ()
		float sx = px[i] - bikeX - ox
		float sy = py[i] - bikeY - oy
		ok = sx * sx + sy * sy <= ProbeTolerance * ProbeTolerance
		i += 1
	endwhile
	GroundProbeRef.MoveTo(HoldingMarkerRef)
	if !ok
		Log("The navmesh around the parked bike is too coarse to tilt it by: left level.")
		return false
	endif
	; along = front - back, across = right - left; the ground's normal is across x along.
	float ax = px[0] - px[1]
	float ay = py[0] - py[1]
	float az = pz[0] - pz[1]
	float bx = px[2] - px[3]
	float by = py[2] - py[3]
	float bz = pz[2] - pz[3]
	float nx = by * az - bz * ay
	float ny = bz * ax - bx * az
	float nz = bx * ay - by * ax
	float norm = Math.Sqrt(nx * nx + ny * ny + nz * nz)
	if norm < 1.0 || nz / norm < 0.17
		Log("The navmesh around the parked bike doesn't make a slope: left level.")
		return false
	endif
	groundX = nx / norm
	groundY = ny / norm
	groundZ = nz / norm
	return true
EndFunction

; Pitch and roll for the parked bike from groundX/Y/Z (the pitch at most ParkMaxPitch degrees,
; the roll at most ParkMaxRoll, each clamped on its own; level if CMB_MaxTilt is 0), keeping
; its heading afAngle. A reference is turned by its heading (Z) last, after
; pitch (X) and roll (Y) about its own axes, each clockwise the game's way: X > 0 tips
; its +Y end down, Y > 0 lifts its +X side.
Function TiltParkedBike(float afAngle, string asFrom)
	float nx = groundX
	float ny = groundY
	float nz = groundZ
	if (CMB_MaxTilt && CMB_MaxTilt.GetValue() <= 0.0) || nz > 0.9999
		; Tilting turned off altogether, or flat ground.
		BikeRef.SetAngle(0.0, 0.0, afAngle)
		Log("Parked bike level on " + asFrom + ".")
		return
	endif
	if nz < 0.01
		nz = 0.01   ; a wall: the pitch comes out at the limit below
	endif
	; The normal in the bike's own frame: turned back by its heading. Pitch and roll are
	; clamped each on its own (scaling the normal down would shrink the pitch with the roll).
	float c = Math.Cos(afAngle)
	float s = Math.Sin(afAngle)
	float pitch = Math.Atan((s * nx + c * ny) / nz)
	if pitch > ParkMaxPitch
		pitch = ParkMaxPitch
	elseif pitch < -ParkMaxPitch
		pitch = -ParkMaxPitch
	endif
	float across = c * nx - s * ny
	if across > 1.0
		across = 1.0
	elseif across < -1.0
		across = -1.0
	endif
	float roll = -Math.Asin(across)
	if roll > ParkMaxRoll
		roll = ParkMaxRoll
	elseif roll < -ParkMaxRoll
		roll = -ParkMaxRoll
	endif
	BikeRef.SetAngle(pitch, roll, afAngle)
	Log("Parked bike tilted to " + asFrom + ": pitch " + pitch + ", roll " + roll + ".")
EndFunction

; The disabled bike follows the player while riding, beside them. Test 40: a teleport whose event
; came after the tick's last look would have the bike put beside the player at the far end
; (PlaceBike reads where they are, after the move): looked at once more, right before the move.
Function ShadowPlayer()
	if teleportsAtOnce
		PlaceBike(0.0, ParkSideOffset)
		return
	endif
	float angle = PlayerRef.GetAngleZ()
	float x = OffsetX(angle, 0.0, ParkSideOffset)
	float y = OffsetY(angle, 0.0, ParkSideOffset)
	if teleportPending || !StillRiding()
		return
	endif
	BikeRef.MoveTo(PlayerRef, x, y, 0.0, false)
	BikeRef.SetAngle(0.0, 0.0, angle + ParkedModelYaw)
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

Function EquipBike(bool abPoseAhead = false)
	Armor wanted = WantedBikeArmor()
	; 2026-11-10a ([Look] MountEarly): Mount equips before its pose: the armour the pose will want (RiderPoseAhead). A
	; mismatch is the ride tick's to put right, as any (its EquipBike).
	if abPoseAhead && wanted != CMB_BikeRiderArmor && RiderPoseAhead()
		wanted = CMB_BikeRiderArmor
	endif
	Armor other = CMB_BikeRiderArmor
	if wanted == CMB_BikeRiderArmor
		other = CMB_BikeRiderArmorFrame
	endif
	if !PlayerRef.IsEquipped(wanted)
		; 2026-11-09a (test 51, getting on 5-6 s; the plugin's [Look] FastMount, CMB_LookOptions bit 1): the kept armour
		; (EquipKept). Without the bit: 2026-11-09a's as of t54-merge, below.
		wornFast = LookOption(1)
		if wornFast
			EquipKept(wanted)
			RemoveArmor(other)
			return
		elseif KeptLook(wanted) != ""
			RemoveArmor(wanted, true)   ; one kept while the bit was on: dropped, so the look's mods go on a fresh one
		endif
		if PlayerRef.GetItemCount(wanted) == 0
			PlayerRef.AddItem(wanted, 1, true)
		endif
		; 2026-11-08a: an MCM change since the look was last put on (free mode without Apply, or Customise
		; at the bike switched) put on first, as at getting on, so a swap mid-ride (a weapon drawn, a hit)
		; gives this armour mods of the look CMB_LookCode's rim style and the colour values are of.
		LookSync("the worn bike's equip")
		lookWorn = lookApplied
		; 2026-11-07a: the chosen look's mods on it before it goes on (no call with a stock look).
		int refused = AttachLook(wanted, true)
		; 2026-11-10a (test 52, Free colour blue on the first ride; the plugin's [Look] WornColoursFirst, bit 1024): the colour
		; values written before the equip, so the plugin's first write into the new shapes is this look's (WornColoursWrite).
		bool first = LookOption(1024)
		int written = -2
		if first
			written = WornColoursWrite()
		endif
		PlayerRef.EquipItem(wanted, true, true)
		; Test 41: read right after the equip, the slot said nothing twice (16:00:13, 16:01:37) while
		; the bike showed: the biped hadn't taken the armor yet. Read a tick later (RideTick).
		wornSlotToLog = true
		wornRefused = refused > 0
		if wornRefused
			WornLookRefused(refused)   ; the composed swap, its colours included
		elseif first && written != -2 && written <= 0
			lookColoursWorn = false   ; 2026-11-10a: no colour (the values cleared above) or no F4SE: WornLookColours' own outcome, no call
		elseif LookColoursOn() || lookColoursWorn
			WornLookColours()   ; 2026-11-08a: the look's colours, or the last ones taken off (neither with a stock look: no call)
		endif
	endif
	RemoveArmor(other)
EndFunction

; abDrop (2026-11-09a, EmergencyReset): out of the inventory even with FastMount.
Function RemoveBikeArmor(bool abDrop = false)
	RemoveArmor(CMB_BikeRiderArmor, abDrop)
	RemoveArmor(CMB_BikeRiderArmorFrame, abDrop)
EndFunction

; 2026-11-09a (test 51, [Look] FastMount, bit 1): unequipped and kept with its mods (EquipKept puts it on again with no
; attach while the look is the one they carry), unless abDrop. Without the bit, and dropped: out of the inventory
; (2026-11-09a as of t54-merge), what it carried forgotten.
Function RemoveArmor(Armor akArmor, bool abDrop = false)
	if !abDrop && LookOption(1)
		if PlayerRef.IsEquipped(akArmor)
			PlayerRef.UnequipItem(akArmor, false, true)
		endif
		return
	endif
	int count = PlayerRef.GetItemCount(akArmor)
	if count > 0
		PlayerRef.UnequipItem(akArmor, false, true)
		PlayerRef.RemoveItem(akArmor, count, true)
	endif
	KeptForget(akArmor)
EndFunction

; ---------------------------------------------------------------------------
; 2026-11-09a (test 51, getting on 5-6 s: AttachLook 2 s and the worn bike's F4SE colour swap 2 s behind the fade, the swap
; again 3 s later): the worn bike's two armours kept between rides (the plugin's [Look] FastMount, CMB_LookOptions bit 1).
; They are NonPlayable, weight 0 and value 0, so no menu lists them. Each remembers the look its mods were put on with
; (lookApplied at its attach), its Rims option (lookRimMods, for LookRimsMoved), the mods the game refused (the F4SE swap
; instead) and its mods as F4SE counts them after its attach (WornModsCheck). The worn colours: the values written at the
; equip (CMB_LookF4SE's WriteWornColours); with the plugin's bit 64 it copies them into the worn bike, else the F4SE swap
; once, after the fade (LookFollowUp). EmergencyReset drops them.
; ---------------------------------------------------------------------------
string wornLookRider = ""      ; CMB_BikeRiderArmor's mods: the look they carry ("" none known: put on afresh)
string wornLookFrame = ""      ; CMB_BikeRiderArmorFrame's
int wornRimsRider = 0          ; their Rims option
int wornRimsFrame = 0
int wornRefusedRider = 0       ; the mods the game refused at their attach
int wornRefusedFrame = 0
int wornTakenRider = -1        ; their mods as F4SE counted them after their attach (-1 not yet)
int wornTakenFrame = -1
bool wornFast = false          ; the worn bike was last put on with FastMount (EquipKept)
bool wornCountDue = false      ; LookFollowUp: the worn bike's mods counted (WornModsCheck)
Armor wornCountArmor           ; ...on this armour (the one that equip put on)
bool wornRefit = false         ; fewer mods found: the ride tick puts the worn bike on afresh

; EquipBike with FastMount: akArmor (not equipped) put on. Kept with the look as it stands now (after LookSync): equipped,
; no attach. Else any stale one removed, a fresh one added, the look's mods attached (AttachLook, as before), and what it
; carries remembered. Then the colour values written once, and after the fade (TimerLook, outside busy): the F4SE swap if
; the mods were refused or (no bit 64) the look has colours, and the mods counted.
Function EquipKept(Armor akArmor)
	LookSync("the worn bike's equip")
	int count = PlayerRef.GetItemCount(akArmor)
	int refused = 0
	bool active = LookActive()   ; a stock look: no mods on it, none to count
	; 2026-11-10a (test 52, Free colour blue on the first ride: the paint's V came 0.33 s after the shapes were held; the
	; plugin's [Look] WornColoursFirst, bit 1024): the colour values written before the equip (WornColoursWrite), its answer
	; kept for the swap below. Without the bit: after it (2026-11-09a).
	bool first = LookOption(1024)
	int written = -2
	if count == 1 && KeptLook(akArmor) == lookApplied
		lookWorn = lookApplied
		lookRimMods = KeptRims(akArmor)
		refused = KeptRefused(akArmor)
		if first
			written = WornColoursWrite()
		endif
		PlayerRef.EquipItem(akArmor, true, true)
		if active
			Log("Look: the worn bike's kept mods (the look unchanged): no attach")
		endif
	else
		if count > 0
			PlayerRef.RemoveItem(akArmor, count, true)   ; its mods are another look's (or found fewer)
		endif
		PlayerRef.AddItem(akArmor, 1, true)
		lookWorn = lookApplied
		refused = AttachLook(akArmor, true)
		KeptRemember(akArmor, lookApplied, lookRimMods, refused)
		if first
			written = WornColoursWrite()
		endif
		PlayerRef.EquipItem(akArmor, true, true)
	endif
	; Test 41: the slot read a tick later (RideTick).
	wornSlotToLog = true
	wornRefused = refused > 0
	if wornRefused
		WornLookRefused(refused)   ; the composed swap, after the fade
	endif
	if !first
		written = WornColoursWrite()
	endif
	if written != -2
		lookColoursWorn = written == 1
		; 2026-11-10a (the plugin's [Look] HueSwap, bit 2048): with the plugin writing the colours (bit 64), Free colour's
		; F4SE swap once after the fade too (WornHueSwap).
		if written == 1 && !wornRefused && (!LookOption(64) || WornHueSwap())
			wornSwapDue = true   ; ApplyWornColours, once
			if LookOption(64)
				Log("Look: Free colour on the worn bike: the plugin writes it, and the F4SE swap once after the fade too (HueSwap)")
			endif
		endif
	endif
	if active
		wornCountDue = true
		wornCountArmor = akArmor
	endif
	if wornCountDue || wornSwapDue
		StartTimer(WornSwapAgain, TimerLook)
	endif
EndFunction

; 2026-11-10a (test 52), EquipBike and EquipKept: the look's colour values into the plugin's fixed globals (CMB_LookF4SE's
; WriteWornColours: 1 a colour, 0 none, the globals -1; -1 no F4SE) when the look has colours or the last ones are to be
; cleared; -2 neither (no call). With [Look] WornColoursFirst (bit 1024) before the equip, else after it (2026-11-09a).
int Function WornColoursWrite()
	if LookColoursOn() || lookColoursWorn
		return CallLookF4SE("WriteWornColours")
	endif
	return -2
EndFunction

; 2026-11-10a (test 52, Free colour rode blue: the plugin's raw write of the paint's V may come after the game set the
; material up for drawing; test 51 showed an F4SE swap does change a live 3D), EquipKept with the plugin's bit 64: with
; [Look] HueSwap (bit 2048) and Free colour's paint (CMB_LookF4SE's CMB_LookPaintV at 0 or more, as just written), the F4SE
; swap once after the fade too (LookFollowUp's ApplyWornColours). Off, or another paint: the plugin's write alone (2026-11-09a).
bool Function WornHueSwap()
	if !LookOption(2048)
		return false
	endif
	ScriptObject look = CastAs("CMB_LookF4SE")
	GlobalVariable paintV = None
	if look
		paintV = look.GetPropertyValue("CMB_LookPaintV") as GlobalVariable
	endif
	return paintV && paintV.GetValue() >= 0.0
EndFunction

; 2026-11-10a ([Look] MountEarly), EquipBike(abPoseAhead): Mount equips before its pose. True when ApplyRiderPose will put
; the riding pose on (the MCM's pose on, CMB_RiderPose.esp and its flavour keyword there) and the bike would then follow the
; rider (WantedBikeArmor's CMB_BikeRiderArmor: CMB_BikeFollowsRider on, no weapon drawn).
bool Function RiderPoseAhead()
	if riderPoseApplied || CMB_UseRiderPose.GetValue() < 1.0 || CMB_BikeFollowsRider.GetValue() <= 0.0 || PlayerRef.IsWeaponDrawn() || !Game.IsPluginInstalled(RiderPosePlugin)
		return false
	endif
	return (Game.GetFormFromFile(RiderFlavorID, RiderPosePlugin) as Keyword) != None
EndFunction

; LookFollowUp (after the fade, outside busy): the worn bike's mods counted. The first count after an attach is what it
; carries; a later equip of it found with fewer: its line, forgotten, and the ride tick puts it on afresh (wornRefit).
Function WornModsCheck()
	Armor worn = wornCountArmor
	if !worn || !PlayerRef.IsEquipped(worn)
		return   ; swapped since (a weapon drawn): that equip counts its own
	endif
	int n = CallLookF4SE("WornModCount")
	if n < 0
		return   ; no F4SE, or the slot empty yet
	endif
	int taken = KeptTaken(worn)
	if taken < 0
		KeptTakenSet(worn, n)
	elseif n < taken
		Log("Look: the worn bike's kept mods: " + n + " of " + taken + " after the equip: put on again with the look's mods")
		KeptForget(worn)
		wornRefit = true
	endif
EndFunction

string Function KeptLook(Armor akArmor)
	if akArmor == CMB_BikeRiderArmor
		return wornLookRider
	endif
	return wornLookFrame
EndFunction

int Function KeptRims(Armor akArmor)
	if akArmor == CMB_BikeRiderArmor
		return wornRimsRider
	endif
	return wornRimsFrame
EndFunction

int Function KeptRefused(Armor akArmor)
	if akArmor == CMB_BikeRiderArmor
		return wornRefusedRider
	endif
	return wornRefusedFrame
EndFunction

int Function KeptTaken(Armor akArmor)
	if akArmor == CMB_BikeRiderArmor
		return wornTakenRider
	endif
	return wornTakenFrame
EndFunction

Function KeptTakenSet(Armor akArmor, int aiTaken)
	if akArmor == CMB_BikeRiderArmor
		wornTakenRider = aiTaken
	else
		wornTakenFrame = aiTaken
	endif
EndFunction

Function KeptRemember(Armor akArmor, string asLook, int aiRims, int aiRefused)
	if akArmor == CMB_BikeRiderArmor
		wornLookRider = asLook
		wornRimsRider = aiRims
		wornRefusedRider = aiRefused
		wornTakenRider = -1
	else
		wornLookFrame = asLook
		wornRimsFrame = aiRims
		wornRefusedFrame = aiRefused
		wornTakenFrame = -1
	endif
EndFunction

Function KeptForget(Armor akArmor)
	KeptRemember(akArmor, "", 0, 0)
EndFunction

; ---------------------------------------------------------------------------
; Customising (2026-11-07a)
; ---------------------------------------------------------------------------

; The customisation build (C1; tools/esp-generator/look_options.json is its one table of slots and
; options). The parked bike's Customise button (CMB_BikeActivatorScript, choice 2) starts a session
; (BeginCustomise): the bike's look item CMB_BikeLook in the inventory with the current look on it
; (AttachLook), the field kit out of the side bag beside the bike (PlaceKit) with its components
; linked (LinkKit), and the player at the kit's armour menu. Each mod made there comes back as
; OnPlayerModArmorWeapon (CMB_PlayerAliasScript -> LookModded), which sets that slot's CMB_Look_<slot>.
; The menu's close ends it (EndCustomise): the item taken back, the kit put away, the look put on
; the bikes (ApplyLook). The worn bike gets the look's mods at getting on (EquipBike -> AttachLook), the
; parked and first-person bikes one composed material swap (CMB_LookF4SE, F4SE), and the plugin hides
; the worn and first-person mirrors by CMB_LookCode. Every slot starts on the stock look; with
; CMB_LookOn 0 (or an older ESP: these properties None) there is no button and nothing is called on
; any bike: the 2026-11-06a bike.

string Property LookMenuName = "ExamineMenu" AutoReadOnly
{The armour bench's menu (the field kit opens it).}
int Property LookSlots = 11 AutoReadOnly
{The slots, in CMB_LookCategories' order: 0 the left tank badge, 1 the right, 2 the rear fender badge,
3 the paint, 4 the mirrors; since 2026-11-08a 5 the rims, 6 the tyres, 7 the plate, 8 the plate's text,
9 its letters' colour, 10 its background colour (an older ESP has the first five only: the others'
globals None, nothing done for them).}
int Property LookSlotTankL = 0 AutoReadOnly
int Property LookSlotTankR = 1 AutoReadOnly
int Property LookSlotFender = 2 AutoReadOnly
int Property LookSlotPaint = 3 AutoReadOnly
int Property LookSlotMirrors = 4 AutoReadOnly
int Property LookSlotRims = 5 AutoReadOnly
int Property LookSlotTyres = 6 AutoReadOnly
int Property LookSlotPlate = 7 AutoReadOnly
int Property LookSlotPlateText = 8 AutoReadOnly
int Property LookSlotPlateInk = 9 AutoReadOnly
int Property LookSlotPlateBack = 10 AutoReadOnly
int Property LookFollowLeft = 17 AutoReadOnly
{The right tank's option "Same as the left" (its default): the left's choice, wherever a look is put on.}
int Property LookPaintFree = 45 AutoReadOnly
{2026-11-08a: Paint's option "Free colour" (the MCM's hue and shade; CMB_LookF4SE composes its colour).}
int Property LookTextOwn = 0 AutoReadOnly
int Property LookTextNone = 1 AutoReadOnly
{The plate text's "The plate's own" (its default: the design's own text, LookPlateOwnText) and "None".}
float Property KitSpotSide = 52.0 AutoReadOnly
{Where the player stands at the kit: this far out from the bike's middle, on the side they stood on
(the parked half width at the tank, about 16, the capsule and a gap), facing the bike.}
float Property KitMarkerForward = 20.0 AutoReadOnly
float Property KitMarkerRight = -30.0 AutoReadOnly
{The toolbox's furniture marker in its own frame (CMB_FieldKit's SNAM): 20 ahead of it and 30 to its
left, facing its front. The toolbox is placed so that the marker is the player's spot.}
float Property KitBenchSide = 110.0 AutoReadOnly
{Kit mode 3: the armour bench's middle this far out from the bike's middle (t49's bench), facing it.}
float Property KitBoxForward = 0.0 AutoReadOnly
float Property KitBoxRight = -100.0 AutoReadOnly
{Kit mode 3: the toolbox (CMB_FieldKitBox) here in the bench's frame, beside its left end.}
float Property KitTickInterval = 1.0 AutoReadOnly
int Property KitSnapTicks = 4 AutoReadOnly
{Seconds (ticks out of menus) without the menu and not in the kit: one SnapIntoInteraction.}
int Property KitGiveUpTicks = 6 AutoReadOnly
{Seconds without the menu: automatic tries the next mode (1, then 3), a forced mode ends the session.}
float Property KitWatchdog = 2.0 AutoReadOnly
{After the menu was seen: this long out of every menu and out of the kit ends the session.}
float Property LookViewDelay = 0.1 AutoReadOnly
{The look on a first-person bike just placed or handed over (the plugin shows it after its 3D has
been there 1.0 s, [View] HandoverTime): from a timer, outside the ride tick and busy.}
float Property WornSwapAgain = 1.0 AutoReadOnly
{The worn bike's F4SE swap (when its mods were refused) once more this long after the equip: right
after it the armour's 3D may not be on the player yet.}
float Property LookRetryDelay = 0.5 AutoReadOnly
float Property KitLeaveWait = 1.0 AutoReadOnly
{Automatic's next mode: the wait after the old kit is put away with the player still in it.}

bool customising = false       ; a Customise session is on (BeginCustomise to EndCustomise)
bool lookEnding = false        ; EndCustomise is running (it runs once)
ObjectReference lookKit        ; the furniture the player uses: the toolbox (modes 1, 2) or the bench (3)
ObjectReference lookBox        ; mode 3: the toolbox at the bench's foot
int kitMode = 0                ; the kit mode of this attempt (1-3)
bool kitAuto = false           ; CMB_KitMode 0: automatic (1, then 3; the one that worked remembered)
bool lookMenuSeen = false      ; the armour menu was seen open in this session
bool kitMenuGuess = false      ; a menu was up while the player was in the kit, with no ExamineMenu event
float lookSince = 0.0          ; real time of the session's start
float kitSince = 0.0           ; ...and of this attempt's activation
int kitTicks = 0               ; this attempt's ticks out of menus
bool kitSwitching = false      ; NextKitMode is putting this attempt away and placing the next (one thread)
bool kitSnapped = false
bool kitEntered = false
float kitOutSince = -1.0       ; after the menu: since when the player is out of every menu and the kit
int lookChanged = 0            ; slots changed in this session
int lookEvents = 0             ; OnPlayerModArmorWeapon events for the look item in this session
bool kitBagLinked = false      ; the side bag is the kit's container (LinkKit)
int bagBefore = 0              ; ...and its item count then
string lookWsWhy = ""          ; BikeWorkshop's reason for no workshop
string lookNotice = ""         ; CustomiseBlocker's notification, if the player should see one
bool lookNoF4seSaid = false    ; "no CMB_LookF4SE" logged this session
bool lookWasActive = false     ; the bikes were last given a non-stock look (so the stock one is put back)
string lookApplied = ""        ; LookState() when ApplyLook last ran ("" not yet): LookSync's test
bool lookViewDue = false       ; LookFollowUp: the look on the first-person bike
bool wornSwapDue = false       ; LookFollowUp: the worn bike's F4SE swap again
bool wornRefused = false       ; the worn bike's mods were refused at its last equip (the F4SE swap instead)
int lookCrudeSaid = -1         ; 2026-11-08a: the crude plate text last logged as shown as the plate's own (-1 none)
int lookRimMods = 0            ; 2026-11-08a: the Rims option the worn bike's mods carry (AttachLook at its equip)
int lookRimCode = 0            ; 2026-11-08a: the rim style CMB_LookCode names (ApplyLook; 0 the cast rim, also with Customise off)
string lookWorn = ""           ; 2026-11-08a: lookApplied when the worn bike was last put on (the look its mods carry)
bool lookColoursWorn = false   ; 2026-11-08a: the worn bike was last given colours (the colour values may be set): the next equip clears them

; MCM "Customise at the bike" (CMB_LookOn 1) with the look's records there.
bool Function LookIsOn()
	return CMB_LookOn && CMB_LookCategories && CMB_LookOn.GetValue() > 0.0
EndFunction

GlobalVariable Function LookGlobal(int aiSlot)
	if aiSlot == LookSlotTankL
		return CMB_Look_TankL
	elseif aiSlot == LookSlotTankR
		return CMB_Look_TankR
	elseif aiSlot == LookSlotFender
		return CMB_Look_Fender
	elseif aiSlot == LookSlotPaint
		return CMB_Look_Paint
	elseif aiSlot == LookSlotMirrors
		return CMB_Look_Mirrors
	elseif aiSlot == LookSlotRims
		return CMB_Look_Rims
	elseif aiSlot == LookSlotTyres
		return CMB_Look_Tyres
	elseif aiSlot == LookSlotPlate
		return CMB_Look_Plate
	elseif aiSlot == LookSlotPlateText
		return CMB_Look_PlateText
	elseif aiSlot == LookSlotPlateInk
		return CMB_Look_PlateInk
	elseif aiSlot == LookSlotPlateBack
		return CMB_Look_PlateBack
	endif
	return None
EndFunction

; The slot's option list (CMB_LookOptions_<slot>: the OMODs, index = the choice). None past
; CMB_LookCategories' end (an older ESP's five lists).
FormList Function LookList(int aiSlot)
	if !CMB_LookCategories || aiSlot < 0 || aiSlot >= CMB_LookCategories.GetSize()
		return None
	endif
	return CMB_LookCategories.GetAt(aiSlot) as FormList
EndFunction

; The slot's choice: its global, or 0 (the stock look) when it is missing or past its list. With
; abResolved the right tank's "Same as the left" (17) is the left's choice (the two lists agree on 0-16),
; and (2026-11-08a) the plate text as shown: "The plate's own" (0) is the plate's own text
; (LookPlateOwnText: "None", 1, on the stock plate), and so is a crude one while "Crude plate texts"
; (CMB_LookPlateCrude) is off, said once a change.
int Function LookChoice(int aiSlot, bool abResolved)
	GlobalVariable g = LookGlobal(aiSlot)
	if !g
		return 0
	endif
	int i = g.GetValue() as int
	if abResolved && aiSlot == LookSlotPlateText
		return LookTextShown(i)
	endif
	if i == 0
		return 0   ; the stock look: no list looked at (getting on with it reads the globals only)
	endif
	if abResolved && aiSlot == LookSlotTankR && i == LookFollowLeft
		return LookChoice(LookSlotTankL, true)
	endif
	FormList options = LookList(aiSlot)
	if i < 0 || (options && i >= options.GetSize())
		return 0
	endif
	return i
EndFunction

; 2026-11-08a: the plate text shown for the choice aiChosen (LookChoice's abResolved).
int Function LookTextShown(int aiChosen)
	int i = aiChosen
	FormList options = LookList(LookSlotPlateText)
	if i < 0 || (options && i >= options.GetSize())
		i = LookTextOwn
	endif
	if i != LookTextOwn && LookTextIsCrude(i) && CMB_LookPlateCrude && CMB_LookPlateCrude.GetValue() <= 0.0
		int own = LookPlateOwnTextOf(LookChoice(LookSlotPlate, true))
		if lookCrudeSaid != i
			lookCrudeSaid = i
			Log("Look: the plate text " + LookName(LookSlotPlateText, i) + " is crude and \"Crude plate texts\" is off: the plate's own (" + LookName(LookSlotPlateText, own) + ")")
		endif
		return own
	endif
	lookCrudeSaid = -1
	if i == LookTextOwn
		return LookPlateOwnTextOf(LookChoice(LookSlotPlate, true))
	endif
	return i
EndFunction

bool Function LookTextIsCrude(int aiText)
	return LookTextCrude && aiText >= 0 && aiText < LookTextCrude.Length && LookTextCrude[aiText] == 1
EndFunction

; A plate design's own text (a PlateText index; "None", 1, for the stock plate and when unknown).
int Function LookPlateOwnTextOf(int aiPlate)
	if LookPlateOwnText && aiPlate >= 0 && aiPlate < LookPlateOwnText.Length
		return LookPlateOwnText[aiPlate]
	endif
	return LookTextNone
EndFunction

; A look other than the stock one is chosen (and Customise at the bike is on). The 2026-11-08a slots
; count as chosen (resolving nothing): the plate text's default "The plate's own" is stock even where
; it shows as "None".
bool Function LookActive()
	if !LookIsOn()
		return false
	endif
	int s = 0
	while s < LookSlots
		if LookChoice(s, s < LookSlotRims) != 0
			return true
		endif
		s += 1
	endwhile
	return false
EndFunction

; CMB_LookCode's mirror bits: Mirrors' options 0 stock, 1 egg, 2 D, 3 none are the plugin's 1, 2, 3, 0.
int Function LookMirrorCode()
	return (LookChoice(LookSlotMirrors, false) + 1) % 4
EndFunction

; 2026-11-08a: CMB_LookCode as ApplyLook writes it with Customise at the bike on: bit 2 set, the
; mirror (bits 0-1) and the rim style (bits 3-6: 0 the cast rim, 1-7 the styles, LookRimStyle; the
; plugin hides the other styles' shapes on the worn and first-person bikes).
int Function LookCodeNow()
	return 4 + LookMirrorCode() + 8 * LookRimStyleOf(LookChoice(LookSlotRims, false))
EndFunction

int Function LookRimStyleOf(int aiRims)
	if LookRimStyle && aiRims >= 0 && aiRims < LookRimStyle.Length && LookRimStyle[aiRims] >= 0 && LookRimStyle[aiRims] <= 15
		return LookRimStyle[aiRims]
	endif
	return 0
EndFunction

; 2026-11-08a: the chosen look may carry a colour CMB_LookF4SE composes (Free colour, a rim's body
; colour, a plate design, a plate text): the worn bike is given it after each equip (its own mods
; carry none). Reads the globals only (no call); CMB_LookF4SE's ApplyWornColours decides.
bool Function LookColoursOn()
	if !CMB_Look_Rims || !LookActive()
		return false
	endif
	return LookChoice(LookSlotPaint, false) == LookPaintFree || LookChoice(LookSlotRims, false) != 0 || LookChoice(LookSlotPlate, false) != 0 || LookChoice(LookSlotPlateText, false) != 0
EndFunction

; 2026-11-08a: riding while CMB_LookCode names a rim style other than the one the worn bike's mods carry
; (ApplyLook moved it: "Apply the look" with another rim style, or Customise at the bike off and a load).
; The plugin would show only that style's rim, whose material the mods leave invisible (and the cast rim's
; mods set off.bgsm, which no F4SE swap can match if the engine renamed it), so the ride tick puts the worn
; bike on again: its mods follow the look. An MCM change without Apply moves nothing (EquipBike puts it on
; first). Script variables only.
bool Function LookRimsMoved()
	return riding && CMB_Look_Rims && lookRimCode != LookRimStyleOf(lookRimMods)
EndFunction

; 2026-11-08a: the look as it stands is the one the worn bike was put on with, so CMB_LookF4SE's composed
; swap (its colour values) fits the worn bike's materials.
bool Function LookIsWorn()
	return LookState() == lookWorn
EndFunction

string Function LookSlotText(int aiSlot)
	if aiSlot == LookSlotTankL
		return "tank left"
	elseif aiSlot == LookSlotTankR
		return "tank right"
	elseif aiSlot == LookSlotFender
		return "fender"
	elseif aiSlot == LookSlotPaint
		return "paint"
	elseif aiSlot == LookSlotMirrors
		return "mirrors"
	elseif aiSlot == LookSlotRims
		return "rims"
	elseif aiSlot == LookSlotTyres
		return "tyres"
	elseif aiSlot == LookSlotPlate
		return "plate"
	elseif aiSlot == LookSlotPlateText
		return "plate text"
	elseif aiSlot == LookSlotPlateInk
		return "plate letters"
	endif
	return "plate background"
EndFunction

; 2026-11-08a: a slot the ESP has (an older one: the first five only).
bool Function LookSlotThere(int aiSlot)
	return aiSlot < LookSlotRims || LookGlobal(aiSlot) != None
EndFunction

; 2026-11-08a: the slots without a material swap (the plate's colours: CMB_LookF4SE composes them).
bool Function LookSlotColour(int aiSlot)
	return aiSlot == LookSlotPlateInk || aiSlot == LookSlotPlateBack
EndFunction

; An option's name for the log: its "<slot>:<key>" in LookKeys (look_options.json's keys).
string Function LookName(int aiSlot, int aiIndex)
	if LookKeys && LookSlotStart && aiSlot >= 0 && aiSlot < LookSlotStart.Length && aiIndex >= 0
		int j = LookSlotStart[aiSlot] + aiIndex
		if j < LookKeys.Length
			return LookKeys[j]
		endif
	endif
	return "option " + aiIndex
EndFunction

; The look as chosen (the right tank's 17 as itself), for the log.
string Function LookNow()
	string text = ""
	int s = 0
	while s < LookSlots
		if LookSlotThere(s)
			if s > 0
				text += ", "
			endif
			text += LookSlotText(s) + " " + LookName(s, LookChoice(s, false))
		endif
		s += 1
	endwhile
	return text
EndFunction

; The current non-stock choices as mods on an item in the player's inventory: the worn bike before it
; goes on (abWorn: not the mirrors, which the plugin hides by CMB_LookCode, nor the plate's colours,
; whose mods carry no swap: CMB_LookF4SE colours the worn bike), or the look item at the field kit
; (every slot, the right tank as itself or, while it follows, as the left; the plate text as shown, so
; the menu's preview shows a design's own text). Nothing with CMB_LookOn 0 or every slot stock (the
; 2026-11-06a path: no call). Returns how many were refused.
int Function AttachLook(Armor akArmor, bool abWorn)
	if abWorn
		lookRimMods = 0
	endif
	if !akArmor || !LookActive()
		return 0
	endif
	int wanted = 0
	int took = 0
	int s = 0
	while s < LookSlots
		if !abWorn || (s != LookSlotMirrors && !LookSlotColour(s))
			int i = LookChoice(s, true)
			if s == LookSlotPlateText && i == LookTextNone && LookChoice(s, false) == LookTextOwn
				i = 0   ; the plate's own text is "None": the overlay's own material already shows none
			endif
			if abWorn && s == LookSlotRims
				lookRimMods = i
			endif
			FormList options = LookList(s)
			if i > 0 && options
				ObjectMod om = options.GetAt(i) as ObjectMod
				if om
					wanted += 1
					if PlayerRef.AttachModToInventoryItem(akArmor, om)
						took += 1
					endif
				endif
			endif
		endif
		s += 1
	endwhile
	if wanted > 0
		if abWorn
			Log("Look: " + took + " of " + wanted + " mods on the worn bike")
		else
			Log("Customise: the bike's look item holds the current look: " + took + " of " + wanted + " mods")
		endif
	endif
	return wanted - took
EndFunction

; EquipBike: the game refused some of the worn bike's mods (it is NonPlayable): the composed F4SE swap
; on the player instead (its sources are the bike's own files only), now and once more a moment later.
Function WornLookRefused(int aiRefused)
	if wornFast
		; 2026-11-09a (test 51, FastMount): once, from TimerLook after the fade (EquipKept starts it): right after the
		; equip the armour's 3D isn't on the player yet, so the first of 2026-11-08a's two swaps fell on nothing.
		Log("Look: " + aiRefused + " refused on the worn bike (AttachModToInventoryItem): the F4SE swap instead, after the fade")
		wornSwapDue = true
		return
	endif
	int applied = CallLookF4SE("ApplyWorn")
	lookColoursWorn = applied >= 0   ; 2026-11-08a: ApplyWorn wrote the colour values
	if applied < 0
		Log("Look: " + aiRefused + " refused on the worn bike (AttachModToInventoryItem), and no CMB_LookF4SE (F4SE): the worn bike stays stock")
		return
	endif
	Log("Look: " + aiRefused + " refused on the worn bike (AttachModToInventoryItem): the F4SE swap instead, " + applied + " entries applied")
	wornSwapDue = true
	StartTimer(WornSwapAgain, TimerLook)
EndFunction

; 2026-11-08a, EquipBike (the worn bike's mods taken) and LookAfterLoad: the look's colours (Free colour,
; a rim's body colour, the plate's design and text colours) aren't in the mods' swaps, so CMB_LookF4SE
; puts the composed swap, with its colour indices, on the player: now and once more a moment later, as
; WornLookRefused. It does nothing (-2) when the look composes no colour but set the colour values to
; -1 (the last ride's taken off); nothing without F4SE (-1).
Function WornLookColours()
	int applied = CallLookF4SE("ApplyWornColours")
	lookColoursWorn = applied >= 0
	if applied < 0
		return
	endif
	wornSwapDue = true
	StartTimer(WornSwapAgain, TimerLook)
EndFunction

; PlaceTwins and HandOverTwins: a first-person bike just placed gets the look from a timer (outside
; the ride tick and busy). Nothing with the stock look: a fresh one is stock.
Function LookOnView()
	if LookActive()
		lookViewDue = true
		StartTimer(LookViewDelay, TimerLook)
	endif
EndFunction

; TimerLook: the first-person bike's look and the worn bike's F4SE swap, while riding and outside busy.
Function LookFollowUp()
	if !riding
		lookViewDue = false
		wornSwapDue = false
		wornCountDue = false
		return
	endif
	if busy
		StartTimer(LookRetryDelay, TimerLook)
		return
	endif
	if wornCountDue
		; 2026-11-09a (test 51, FastMount): the kept worn bike's mods counted; found fewer, its swap waits for the
		; fresh one the ride tick puts on
		wornCountDue = false
		WornModsCheck()
		if wornRefit
			wornSwapDue = false
		endif
	endif
	if wornSwapDue
		wornSwapDue = false
		string again = "ApplyWorn"
		if !wornRefused
			again = "ApplyWornColours"   ; 2026-11-08a: only the colours were due (the mods were taken)
		endif
		; 2026-11-08a: the colours only while the look is the one the worn bike was put on with (another
		; look's colour values don't fit its materials: they wait for its next equip)
		if wornRefused || LookIsWorn()
			int applied = CallLookF4SE(again)
			if wornFast
				; 2026-11-09a (test 51, FastMount): the only swap (ApplyWornColours logs its own line)
				if wornRefused
					lookColoursWorn = applied >= 0   ; ApplyWorn wrote the colour values
					if applied >= 0
						Log("Look: the worn bike's F4SE swap (its mods refused): " + applied + " entries applied")
					endif
				endif
			elseif applied >= 0
				Log("Look: the worn bike's F4SE swap again: " + applied + " entries applied")
			endif
		endif
	endif
	if lookViewDue
		lookViewDue = false
		ObjectReference view = viewRef
		if view
			CallLookF4SE("ApplyTo", view)
		endif
	endif
EndFunction

; What the bikes show as the MCM stands: "off" with Customise at the bike off (every bike stock),
; else "on" and each slot's choice as put on (the right tank's "Same as the left" as the left's; the
; plate text as shown, so "Crude plate texts" switched over a crude text counts), and (2026-11-08a)
; with Free colour the MCM's hue and shade.
string Function LookState()
	if !LookIsOn()
		return "off"
	endif
	string text = "on"
	int s = 0
	while s < LookSlots
		text += " " + LookChoice(s, true)
		s += 1
	endwhile
	if LookChoice(LookSlotPaint, false) == LookPaintFree && CMB_LookHue && CMB_LookShade
		text += " hue " + CMB_LookHue.GetValue() + " " + CMB_LookShade.GetValue()
	endif
	return text
EndFunction

; Getting on (Mount) and the parked bike's activation (CMB_BikeActivatorScript): the look put on
; again if the MCM changed it since ApplyLook last ran (Customise at the bike switched, or a choice
; changed without "Apply the look"), so the parked bike, CMB_LookCode's mirror and the worn bike
; agree. Nothing when it matches (the globals read, no call on any bike), nor in a session (its end
; puts the look on).
Function LookSync(string asFrom)
	LookHueWanted(asFrom)   ; 2026-11-09a ([Look] HueFree): the MCM's hue or shade moved since chooses Free colour
	if (!CMB_LookCode && !CMB_LookOn) || customising
		return   ; an older ESP (no look), or a session
	endif
	if LookState() != lookApplied
		ApplyLook(asFrom)
	endif
EndFunction

; The chosen look put on the bikes: CMB_LookCode for the plugin (the worn and first-person bikes'
; mirrors and, since 2026-11-08a, rim style: CMB_LookOn ? LookCodeNow() : 0), the parked bike's
; composed swap (kept on it; the colour values for the plugin are the worn bike's, written at its equip),
; and the first-person bike when one is out. While riding, a rim style moved puts the worn bike on again
; at the next ride tick (LookRimsMoved); the rest of the worn look waits for its next equip. With the
; stock look and nothing to put back, CMB_LookCode only (no call on any bike: 2026-11-06a's).
Function ApplyLook(string asFrom)
	if !CMB_LookCode && !CMB_LookOn
		return   ; an older ESP: no look
	endif
	LookHueRecord()   ; the review of 2026-11-09a (A4, A5; [Look] HueFree): the look as put on, for LookHueWanted
	lookApplied = LookState()
	bool active = LookActive()
	float code = 0.0
	lookRimCode = 0
	if LookIsOn()
		code = LookCodeNow() as float
		lookRimCode = ((code as int) / 8) % 16   ; bits 3-6 (LookRimsMoved)
	endif
	if CMB_LookCode
		CMB_LookCode.SetValue(code)
	endif
	if !active && !lookWasActive
		return
	endif
	lookWasActive = active
	Log("Look: put on (" + asFrom + "): " + LookNow() + Ternary(LookIsOn(), "", " (Customise at the bike is off: the stock look)") + "; CMB_LookCode " + (code as int))
	if LookOption(1) && (mounting || riding)
		; 2026-11-09a (test 51, getting on 5-6 s; [Look] FastMount, bit 1): the parked bike is disabled (getting on,
		; riding), so its compose (2 s at getting on in test 51, "0 applied now") waits for its enable: EnableParked's
		; ParkedLookDueNow. Without the bit: composed now on the disabled bike, its swap kept.
		parkedLookDue = true
		Log("Look: the parked bike's swap at its enable (" + Ternary(riding, "riding", "getting on") + ")")
	else
		; 2026-11-09a (test 51): counted (Mount's ParkedLookWait), and then the kitpaint unit's ParkedLookAfter.
		parkedLookDue = false
		lookParkedWork += 1
		int applied = CallLookF4SE("ApplyParked", None, asFrom)
		ParkedLookAfter(asFrom, applied)
		if lookParkedWork > 0
			lookParkedWork -= 1
		endif
	endif
	if riding && viewRef
		lookViewDue = true
		StartTimer(LookViewDelay, TimerLook)
	endif
EndFunction

; OnGameReloaded: a session in the save ended (the kit put away), a stray look item taken back, the
; look put on again (the composed swap's entries aren't kept by the save), and the worn bike's F4SE
; swap again if its mods were refused (the load gives the player new 3D).
Function LookAfterLoad()
	lookNoF4seSaid = false
	lookCrudeSaid = -1   ; 2026-11-08a: said again in this session's log
	lookViewDue = false
	wornSwapDue = false
	; 2026-11-09a (test 51): no count of parked look work, after-the-fade check or activation from before the load is true
	; now (the load's own ApplyLook below counts afresh)
	lookParkedWork = 0
	wornCountDue = false
	activationAt = -1.0
	if customising || lookKit || lookBox
		customising = true
		lookEnding = false
		EndCustomise("a load", false)
	endif
	int stray = TakeLookItem()
	if stray > 0
		Log("Look: a stray CMB_BikeLook taken back after the load (" + stray + ").")
	endif
	ApplyLook("load")
	; 2026-11-08a: or its colours, while the look is the one the worn bike was put on with (else its mods
	; keep their look, the save's colour values theirs, till its next equip: a moved rim style at the next
	; ride tick, LookRimsMoved). 2026-11-09a (test 51, FastMount): as at its equip, the colours not when the
	; plugin writes them (bit 64: the save's colour values are the worn bike's); the swap, if any, once.
	if riding && (wornRefused || (LookColoursOn() && lookWorn == lookApplied && !(wornFast && LookOption(64))))
		wornSwapDue = true
		StartTimer(ReloadPoseDelay, TimerLook)
	endif
EndFunction

int Function TakeLookItem()
	if !CMB_BikeLook
		return 0
	endif
	int n = PlayerRef.GetItemCount(CMB_BikeLook)
	if n > 0
		PlayerRef.RemoveItem(CMB_BikeLook, n, true)
	endif
	return n
EndFunction

; Why a session can't start now ("" if it can); lookNotice the player's notification, if any.
string Function CustomiseBlocker()
	lookNotice = ""
	string missing = ""
	if !CMB_LookOn
		missing += " CMB_LookOn"
	endif
	if !CMB_LookCode
		missing += " CMB_LookCode"
	endif
	if !CMB_BikeLook
		missing += " CMB_BikeLook"
	endif
	if !CMB_LookCategories
		missing += " CMB_LookCategories"
	endif
	int s = 0
	while s < LookSlots
		if !LookSlotThere(s)
			; 2026-11-08a's slots: an older ESP has none (the bike as the 2026-11-07a build)
		elseif !LookGlobal(s)
			missing += " the " + LookSlotText(s) + " global"
		elseif CMB_LookCategories && !LookList(s)
			missing += " the " + LookSlotText(s) + " list"
		endif
		s += 1
	endwhile
	if missing != ""
		return "the look's records are missing:" + missing + " (an older ESP, whose third button is Cancel)."
	elseif CMB_LookOn.GetValue() <= 0.0
		return "Customise at the bike is off (CMB_LookOn 0)."
	elseif PlayerRef.IsInCombat()
		lookNotice = "Not in a fight."
		return "in a fight."
	elseif swimming
		lookNotice = "Not while swimming."
		return "swimming."
	endif
	return ""
EndFunction

; The parked bike's Customise (CMB_BikeActivatorScript, choice 2).
Function BeginCustomise()
	if riding || busy || customising
		Log("Customise refused: " + Ternary(riding, "riding.", Ternary(customising, "customising already.", "busy (" + BusyText() + ").")))
		return
	endif
	; Claimed before calling anything: every call below lets another thread run.
	busy = true
	NoteBusy("customising")
	string blocker = CustomiseBlocker()
	if blocker != ""
		busy = false
		Log("Customise refused: " + blocker)
		if lookNotice != ""
			Debug.Notification(lookNotice)
		endif
		return
	endif
	lookSince = Utility.GetCurrentRealTime()
	lookChanged = 0
	lookEvents = 0
	lookMenuSeen = false
	kitMenuGuess = false
	kitBagLinked = false
	lookEnding = false
	kitSwitching = false
	TakeLookItem()
	PlayerRef.AddItem(CMB_BikeLook, 1, true)
	AttachLook(CMB_BikeLook, false)
	int m = 0
	if CMB_KitMode
		m = CMB_KitMode.GetValue() as int
	endif
	; 2026-11-09a (test 51): [Look] KitHeld (CMB_LookOptions bit 2), read once a session; off: 2026-11-08a's ladder below.
	kitHeldOn = LookOption(2)
	kitMenuAt = -1.0
	kitInAtOpen = false
	kitRemembered = false
	kitClosing = false
	if kitHeldOn
		kitAuto = m < 1 || m > 4
		if kitAuto
			m = KitStartMode()
		endif
	else
		kitAuto = m < 1 || m > 3
		if kitAuto
			m = 1
			if CMB_KitWorked
				int worked = CMB_KitWorked.GetValue() as int
				if worked >= 1 && worked <= 3
					m = worked
				endif
			endif
		endif
	endif
	kitMode = m
	customising = true
	RegisterForMenuOpenCloseEvent(LookMenuName)
	bool ready = PrepareKit()
	if !ready && kitAuto && kitHeldOn
		int next = KitNextMode(kitMode)
		if next > 0
			KitForget("not placed")
			Log("Field kit: mode " + kitMode + ": not placed: trying mode " + next)
			kitMode = next
			ready = PrepareKit()
		endif
	elseif !ready && kitAuto && kitMode < 3
		Log("Field kit: mode " + kitMode + ": not placed: trying mode 3")
		kitMode = 3
		ready = PrepareKit()
	endif
	busy = false
	if !ready
		EndCustomise("the field kit couldn't be placed")
		Debug.Notification("The field kit couldn't be used here.")
		return
	endif
	GoToKit()
EndFunction

Furniture Function KitForm(int aiMode)
	if aiMode == 2
		return CMB_FieldKitArmorKw
	elseif aiMode == 3
		return CMB_FieldKitBench
	elseif aiMode == 4
		return WorkbenchArmorA   ; 2026-11-09a (test 51, [Look] KitHeld): the game's own armour bench
	endif
	return CMB_FieldKit
EndFunction

string Function KitModeText(int aiMode)
	if aiMode == 2
		return "the toolbox with the armour bench's keyword"
	elseif aiMode == 3
		return "the armour bench"
	elseif aiMode == 4
		return "the game's armour bench"
	endif
	return "the toolbox"
EndFunction

; Placed, linked and watched (the kit's OnExitFurniture); false if it couldn't be placed.
bool Function PrepareKit()
	if !PlaceKit(kitMode) || !customising
		KitTidy()
		return false
	endif
	LinkKit()
	RegisterForRemoteEvent(lookKit, "OnExitFurniture")
	return true
EndFunction

; The player to the kit (Activate: the armour menu opens there), and the session's ticks.
Function GoToKit()
	kitTicks = 0
	kitSnapped = false
	kitEntered = false
	kitOutSince = -1.0
	kitSince = Utility.GetCurrentRealTime()
	ObjectReference kit = lookKit
	if kit
		if kitStashRef
			KitStashBack(kit)   ; 2026-11-10a ([Look] KitStash): the pre-link read back (mode 4 too)
		endif
		kit.Activate(PlayerRef)
	endif
	StartTimer(KitTickInterval, TimerKit)
EndFunction

; The field kit beside the bike, on the side the player stands on (they reached the bike from there).
; The player's spot is KitSpotSide out from the bike's middle, facing it; modes 1 and 2 put the toolbox
; so that its marker is that spot; mode 3 the armour bench KitBenchSide out, facing the bike, and the
; toolbox at its foot (2026-11-09a: mode 4, the game's armour bench, the same). The toolbox opens there, with its
; sound: out of the side bag.
bool Function PlaceKit(int aiMode)
	Furniture form = KitForm(aiMode)
	if !form
		Log("Customise: no " + Ternary(aiMode == 2, "CMB_FieldKitArmorKw", Ternary(aiMode == 3, "CMB_FieldKitBench", Ternary(aiMode == 4, "WorkbenchArmorA", "CMB_FieldKit"))) + " in the plugin: field kit mode " + aiMode + " can't be placed.")
		return false
	endif
	float heading = BikeRef.GetAngleZ() - ParkedModelYaw
	float bikeX = BikeRef.GetPositionX()
	float bikeY = BikeRef.GetPositionY()
	float across = (PlayerRef.GetPositionX() - bikeX) * Math.Cos(heading) - (PlayerRef.GetPositionY() - bikeY) * Math.Sin(heading)
	float side = 1.0
	if across < 0.0
		side = -1.0
	endif
	float facing = heading - side * 90.0   ; from the player's side toward the bike
	float z = PlayerRef.GetPositionZ()
	float x
	float y
	if aiMode >= 3
		x = bikeX + OffsetX(heading, 0.0, side * KitBenchSide)
		y = bikeY + OffsetY(heading, 0.0, side * KitBenchSide)
	else
		float standX = bikeX + OffsetX(heading, 0.0, side * KitSpotSide)
		float standY = bikeY + OffsetY(heading, 0.0, side * KitSpotSide)
		x = standX - OffsetX(facing, KitMarkerForward, KitMarkerRight)
		y = standY - OffsetY(facing, KitMarkerForward, KitMarkerRight)
	endif
	ObjectReference kit = PlaceKitPart(form, x, y, z, facing)
	if !kit
		Log("Customise: field kit mode " + aiMode + " (" + KitModeText(aiMode) + ") could not be placed.")
		return false
	endif
	lookKit = kit
	ObjectReference toolbox = kit
	if aiMode >= 3 && CMB_FieldKitBox
		lookBox = PlaceKitPart(CMB_FieldKitBox, x + OffsetX(facing, KitBoxForward, KitBoxRight), y + OffsetY(facing, KitBoxForward, KitBoxRight), z, facing)
		toolbox = lookBox
	endif
	if toolbox
		toolbox.PlayGamebryoAnimation("Open", true)
		if DRScToolboxBOpen
			DRScToolboxBOpen.Play(toolbox)
		endif
	endif
	Log("Customise: field kit mode " + aiMode + " (" + KitModeText(aiMode) + ") at " + Whole(x) + ", " + Whole(y) + ", " + Ternary(side > 0.0, "right", "left") + " of the bike")
	return true
EndFunction

ObjectReference Function PlaceKitPart(Form akForm, float afX, float afY, float afZ, float afAngle)
	ObjectReference part = PlayerRef.PlaceAtMe(akForm, 1, false, true, false)
	if part
		part.SetPosition(afX, afY, afZ)
		part.SetAngle(0.0, 0.0, afAngle)
		part.Enable()
		part.WaitFor3DLoad()
	endif
	return part
EndFunction

; The kit's components: in one of the player's settlements its workshop (both keywords, so either
; reading of the engine finds it); elsewhere, with CMB_KitBagLink 1, the side bag as its container.
; 2026-11-10a (test 52): then, with [Look] KitStash and Global Stash by SKK, KitStash (SKK's stash instead, when SKK would
; link the kit). Every placed kit comes here once: this attempt's pre-link and KitRetry start afresh.
Function LinkKit()
	kitBagLinked = false
	kitStashRef = None
	kitLinkWs = None
	kitRetried = false
	ObjectReference kit = lookKit
	if !kit
		return
	endif
	ObjectReference ws = BikeWorkshop(kit)
	if ws && WorkshopItemKeyword && LinkedWorkbenchContainerKeyword
		kit.SetLinkedRef(ws, WorkshopItemKeyword)
		kit.SetLinkedRef(ws, LinkedWorkbenchContainerKeyword)
		Log("Customise: the settlement's workshop " + ws.GetFormID() + " linked (both keywords)")
		kitLinkWs = ws
		KitStash(kit, true)
		return
	endif
	Log("Customise: not in one of your settlements (" + lookWsWhy + ").")
	if LinkedWorkbenchContainerKeyword && (!CMB_KitBagLink || CMB_KitBagLink.GetValue() > 0.0)
		kit.SetLinkedRef(SideBagRef, LinkedWorkbenchContainerKeyword)
		bagBefore = SideBagRef.GetItemCount()
		kitBagLinked = true
		Log("Customise: the side bag linked as the bench's container (" + bagBefore + " items)")
	else
		Log("Customise: no workshop here and the bag not linked: your own components only")
	endif
	KitStash(kit, false)
EndFunction

; t49's: the workshop of the player's settlement the kit stands in, or None (lookWsWhy says why).
; CastAs, CallFunction and GetPropertyValue are ScriptObject's: no workshop script is compiled against.
ObjectReference Function BikeWorkshop(ObjectReference akBench)
	lookWsWhy = ""
	if !LocTypeWorkshopSettlement || !WorkshopParentQuest || !WorkshopPlayerOwned
		lookWsWhy = "no workshop records in the plugin"
		return None
	endif
	Location loc = PlayerRef.GetCurrentLocation()
	if !loc || !loc.HasKeyword(LocTypeWorkshopSettlement)
		lookWsWhy = "no settlement location"
		return None
	endif
	ScriptObject wp = WorkshopParentQuest.CastAs("WorkshopParentScript")
	if !wp
		lookWsWhy = "no WorkshopParentScript"
		return None
	endif
	Var[] args = new Var[1]
	args[0] = loc
	ObjectReference ws = wp.CallFunction("GetWorkshopFromLocation", args) as ObjectReference
	if !ws
		lookWsWhy = "no workshop for the location"
		return None
	endif
	if !akBench.IsWithinBuildableArea(ws)
		lookWsWhy = "not in its build area"
		return None
	endif
	ScriptObject wss = ws.CastAs("WorkshopScript")
	bool owned = wss && (wss.GetPropertyValue("OwnedByPlayer") as bool)
	if !owned && ws.GetValue(WorkshopPlayerOwned) <= 0.0
		lookWsWhy = "not yours"
		return None
	endif
	return ws
EndFunction

; The player in the kit: F4SE's furniture reference (CMB_LookF4SE), else any furniture (GetSitState).
bool Function InKit()
	ObjectReference kit = lookKit
	if !kit
		return false
	endif
	int answer = CallLookF4SE("InFurniture", kit)
	if answer >= 0
		return answer > 0
	endif
	return PlayerRef.GetSitState() != 0
EndFunction

; TimerKit, once a second while customising. Before the menu: one SnapIntoInteraction at
; KitSnapTicks if the player isn't in the kit; at KitGiveUpTicks automatic tries the next mode, a
; forced one ends the session. After the menu (or mods seen without its event): out of every menu and
; out of the kit for KitWatchdog ends it (its close or leaving the kit normally ends it first).
Function KitTick()
	if !customising || lookEnding || kitSwitching
		return   ; kitSwitching: the old attempt's tick; the next mode's GoToKit starts its own
	endif
	bool menu = Utility.IsInMenuMode()
	bool inKit = InKit()
	float now = Utility.GetCurrentRealTime()
	if !customising || lookEnding || kitSwitching
		return
	endif
	if inKit && !kitEntered
		kitEntered = true
		Log("Field kit: mode " + kitMode + ": entered (after " + Tenths(now - kitSince) + " s)")
	endif
	if !lookMenuSeen && menu && inKit && !kitMenuGuess
		kitMenuGuess = true
		Log("Field kit: mode " + kitMode + ": a menu open in the kit and no " + LookMenuName + " event")
	endif
	if !lookMenuSeen && !menu
		kitTicks += 1
		if kitTicks == KitSnapTicks && !inKit && !kitSnapped
			kitSnapped = true
			bool snapped = PlayerRef.SnapIntoInteraction(lookKit)
			Log("Field kit: mode " + kitMode + ": not in it after " + KitSnapTicks + " s: SnapIntoInteraction " + snapped)
		elseif kitTicks >= KitGiveUpTicks
			if kitMenuGuess || lookEvents > 0
				; A menu in the kit, or mods made, without the menu's event: the session goes on as if seen.
				lookMenuSeen = true
				Log("Field kit: mode " + kitMode + ": no " + LookMenuName + " event, but " + Ternary(lookEvents > 0, "" + lookEvents + " mod events", "a menu in the kit") + ": the session goes on")
			elseif !NextKitMode("no menu after " + KitGiveUpTicks + " s")
				EndCustomise("no menu after " + KitGiveUpTicks + " s")
				Debug.Notification("The field kit couldn't be used here.")
				return
			else
				return   ; the next mode's ticks have started
			endif
		endif
	endif
	if lookMenuSeen
		if menu || inKit
			kitOutSince = -1.0
		elseif kitOutSince < 0.0
			kitOutSince = now
		elseif now - kitOutSince >= KitWatchdog
			EndCustomise("watchdog")
			return
		endif
	endif
	if customising && !lookEnding && !kitSwitching
		StartTimer(KitTickInterval, TimerKit)
	endif
EndFunction

; Automatic only: this attempt put away quietly and the next mode tried (KitNextMode: 1, then 3; 2026-11-09a's [Look]
; KitHeld: 3, then 4, and the mode forgotten if it was the remembered one). False if there is none, or it couldn't be
; placed. One thread only (the tick, the kit's exit and, with KitHeld, the menu's fast close can come here, and every
; call below lets the other run): the first one switches, with the old attempt's tick cancelled; the other returns true
; (nothing for it to do).
bool Function NextKitMode(string asWhy)
	if kitSwitching
		return true   ; the other thread is switching (it has set the next kitMode or will)
	endif
	if kitHeldOn
		KitForget(asWhy)
	endif
	int next = KitNextMode(kitMode)
	if next <= 0
		return false
	endif
	kitSwitching = true
	CancelTimer(TimerKit)
	Log("Field kit: mode " + kitMode + ": " + asWhy + ": trying mode " + next)
	bool wasIn = InKit()
	KitTidy()
	if wasIn
		Utility.Wait(KitLeaveWait)   ; out of the old kit's furniture first, or the next activation can be lost
	endif
	if !customising || lookEnding
		kitSwitching = false
		return true   ; ended meanwhile (a load): nothing more to do here
	endif
	kitMode = next
	if kitHeldOn
		; The next attempt starts afresh (with KitHeld this can come after the old attempt's menu was seen).
		lookMenuSeen = false
		kitMenuGuess = false
		kitMenuAt = -1.0
		kitInAtOpen = false
		kitRemembered = false
	endif
	bool ready = PrepareKit()
	kitSwitching = false
	if !ready
		return false
	endif
	GoToKit()
	return true
EndFunction

; OnMenuOpenCloseEvent's ExamineMenu (registered only while customising). 2026-11-09a's [Look] KitHeld: the open
; remembers nothing (it says whether the player is in the kit); the close is KitMenuDone's.
Function LookMenu(bool abOpening)
	if !customising || lookEnding
		return
	endif
	if kitHeldOn
		if kitSwitching
			return   ; the old attempt's menu: the next mode is being placed
		endif
		if abOpening
			if !lookMenuSeen
				float at = Utility.GetCurrentRealTime()
				if !lookMenuSeen && customising && !lookEnding && !kitSwitching
					lookMenuSeen = true
					kitMenuAt = at
					kitInAtOpen = InKit()
					Log("Field kit: mode " + kitMode + ": the menu open after " + Tenths(at - kitSince) + " s" + Ternary(kitInAtOpen, ", the player in the kit", ", not in the kit"))
				endif
			endif
		elseif lookMenuSeen && !kitClosing
			KitMenuDone("the menu closed")
		endif
		return
	endif
	if abOpening
		if !lookMenuSeen
			lookMenuSeen = true
			Log("Field kit: mode " + kitMode + ": the menu open after " + Tenths(Utility.GetCurrentRealTime() - kitSince) + " s")
			if kitAuto && CMB_KitWorked
				CMB_KitWorked.SetValue(kitMode as float)
				Log("Field kit: mode " + kitMode + " worked: remembered (CMB_KitWorked " + kitMode + ")")
			endif
		endif
	elseif lookMenuSeen
		EndCustomise("the menu closed")
	endif
EndFunction

Event ObjectReference.OnExitFurniture(ObjectReference akSender, ObjectReference akActionRef)
	if !customising || lookEnding || kitSwitching || kitClosing || akSender != lookKit || akActionRef != PlayerRef
		return   ; kitClosing (KitHeld): the menu's close is deciding
	endif
	if !lookMenuSeen && lookEvents == 0 && NextKitMode("left it before the menu")
		return
	endif
	if kitHeldOn && lookMenuSeen
		KitMenuDone("left the field kit")   ; 2026-11-09a: left before the menu's close event: the same verdict
		return
	endif
	EndCustomise("left the field kit")
EndEvent

; CMB_PlayerAliasScript's OnPlayerModArmorWeapon: a mod made at a workbench. Only the look item's,
; in a session, with the menu up (the attaches at the session's start aren't choices).
Function LookModded(Form akBase, ObjectMod akMod)
	if !customising || lookEnding || !CMB_BikeLook || akBase != CMB_BikeLook
		return
	endif
	if !lookMenuSeen && !Utility.IsInMenuMode()
		return
	endif
	lookEvents += 1
	if lookEvents == 1 && kitHeldOn
		KitRemember("a change made")   ; 2026-11-09a ([Look] KitHeld): the first mod event proves the mode
	endif
	int s = 0
	while s < LookSlots
		FormList options = LookList(s)
		int i = -1
		if options && akMod
			i = options.Find(akMod)
		endif
		if i >= 0
			GlobalVariable g = LookGlobal(s)
			if g
				if (g.GetValue() as int) != i
					lookChanged += 1
				endif
				g.SetValue(i as float)
			endif
			if LookSlotColour(s)
				; 2026-11-08a: a plate colour's mod carries no swap, so the menu can't preview it: the
				; parked bike beside the kit is re-composed at once instead.
				int applied = CallLookF4SE("ApplyParked", None, "the field kit")
				Log("Customise: " + LookSlotText(s) + " = " + LookName(s, i) + " (" + i + ")" + Ternary(applied >= 0, ": the parked bike re-composed", ""))
			else
				Log("Customise: " + LookSlotText(s) + " = " + LookName(s, i) + " (" + i + ")")
			endif
			return
		endif
		s += 1
	endwhile
	string id = "none"
	if akMod
		id = "" + akMod.GetFormID()
	endif
	Log("Customise: a mod not in the bike's lists: " + id)
EndFunction

; The session's end (it runs once): the look item taken back, the kit put away, the look put on the
; bikes (not with abApply false: LookAfterLoad puts it on itself).
Function EndCustomise(string asWhy, bool abApply = true)
	if !customising || lookEnding
		return
	endif
	lookEnding = true
	CancelTimer(TimerKit)
	UnregisterForMenuOpenCloseEvent(LookMenuName)
	float lasted = Utility.GetCurrentRealTime() - lookSince
	TakeLookItem()
	if kitBagLinked
		kitBagLinked = false
		int after = SideBagRef.GetItemCount()
		Log("Customise: components from the bag: " + (bagBefore - after) + " (" + bagBefore + " -> " + after + " items)")
	endif
	KitTidy()
	customising = false
	lookEnding = false
	if lookMenuSeen && lookEvents == 0
		Log("Customise: the menu was open and no mod event came (OnPlayerModArmorWeapon)")
	endif
	Log("Customise: " + asWhy + " after " + Tenths(lasted) + " s, " + lookChanged + " changes; the look: " + LookNow())
	if CMB_Look_TankR && LookChoice(LookSlotTankR, false) == LookFollowLeft
		Log("Customise: the right tank badge follows the left: " + LookName(LookSlotTankL, LookChoice(LookSlotTankL, false)))
	endif
	if abApply
		ApplyLook("the field kit")
	endif
EndFunction

; The kit put away: the toolbox closes, both links undone, faded out and deleted (the box too).
Function KitTidy()
	ObjectReference kit = lookKit
	ObjectReference box = lookBox
	lookKit = None
	lookBox = None
	ObjectReference toolbox = kit
	if box
		toolbox = box
	endif
	if kit
		UnregisterForRemoteEvent(kit, "OnExitFurniture")
	endif
	if toolbox
		toolbox.PlayGamebryoAnimation("Close", true)
	endif
	if kit
		if WorkshopItemKeyword
			kit.SetLinkedRef(None, WorkshopItemKeyword)
		endif
		if LinkedWorkbenchContainerKeyword
			kit.SetLinkedRef(None, LinkedWorkbenchContainerKeyword)
		endif
		kit.Disable(true)
		kit.Delete()
	endif
	if box
		box.Disable(true)
		box.Delete()
	endif
EndFunction

; ---------------------------------------------------------------------------
; 2026-11-10a (test 52): the field kit and Global Stash by SKK: [Look] KitStash (CMB_LookOptions bit 128), KitRetry (256)
; ---------------------------------------------------------------------------
; Test 52: 12 of 12 automatic tries closed at once, each with SKK_GSSMainScript.TransferFrom on the kit. Global Stash by
; SKK's OnPlayerUseWorkBench leaves a bench alone only when it has SKK_GSSKeyword and its WorkshopItemKeyword link is SKK's
; stash; any other bench (every placed kit is a new one) it disables (the menu closes), links to the stash and enables
; again, when its options say so (WorkshopAutoTransfer in a settlement, LinkStandaloneWorkbench elsewhere). And KitHeld
; counted the player in the kit at that 0.17-s menu's open as the mode working. KitStash: the kit linked as SKK would link
; it, before the activation. KitRetry (with KitHeld): a menu closed under KitFastClose with no change made never counts;
; the same kit is used once more, and a second such close goes to the next mode. Both off: 2026-11-09a's.

float Property KitFastClose = 0.5 AutoReadOnly
{KitRetry: a menu closed sooner than this after its open (real time), with no change made, never counts as the mode
working, wherever the player was: the same kit is used once more (KitRetryNow, once an attempt), then the next mode.}
float Property KitRetryWait = 2.0 AutoReadOnly
{KitRetry: how long KitRetryNow waits (real time, menus included) for the kit enabled again, its 3D loaded and the player
out of it (SKK's handler enables it again once it has linked it).}
float Property KitRetryPoll = 0.1 AutoReadOnly
float Property KitRetrySettle = 0.3 AutoReadOnly
{KitRetry: then this long more before the kit is used again.}
string Property SkkPlugin = "SKKGlobalStashScrapping.esp" AutoReadOnly
int Property SkkKeywordID = 0x001763 AutoReadOnly       ; KYWD SKK_GSSKeyword
int Property SkkStashID = 0x000FAE AutoReadOnly         ; the stash (a container reference)
int Property SkkAutoTransferID = 0x00175A AutoReadOnly  ; GLOB WorkshopAutoTransfer (a bench in a settlement)
int Property SkkStandaloneID = 0x00175E AutoReadOnly    ; GLOB LinkStandaloneWorkbench (a bench elsewhere)

ObjectReference kitStashRef    ; KitStash: SKK's stash this attempt's kit is linked to (None: not linked); GoToKit reads it back
ObjectReference kitLinkWs      ; the settlement's workshop LinkKit linked this attempt's kit to (the read-back's line names it)
bool kitRetried = false        ; KitRetry: this attempt's kit used again already (once an attempt; LinkKit clears it)

; KitStash (LinkKit, after its own links; abInSettlement: the kit got the settlement's workshop). Only with Global Stash by
; SKK installed: Game.IsPluginInstalled first, and without it nothing else is called (no GetFormFromFile error lines). With
; SKK's option for this kind of bench on (a global that isn't found counts as on: SKK would link it), the kit linked to
; SKK's stash by both keywords and given SKK_GSSKeyword, as SKK's own LinkWorkbench leaves every bench it has linked: its
; handler then returns at its first check and the menu stays. The bag's count is moot then (the components are the
; stash's, where SKK keeps them). KitTidy clears both links before the delete.
Function KitStash(ObjectReference akKit, bool abInSettlement)
	if !akKit || !LookOption(128) || !Game.IsPluginInstalled(SkkPlugin)
		return
	endif
	if !WorkshopItemKeyword || !LinkedWorkbenchContainerKeyword
		Log("Field kit: Global Stash by SKK: no workbench keywords in the plugin: not linked")
		return
	endif
	Keyword skk = Game.GetFormFromFile(SkkKeywordID, SkkPlugin) as Keyword
	ObjectReference stash = Game.GetFormFromFile(SkkStashID, SkkPlugin) as ObjectReference
	if !skk || !stash
		Log("Field kit: Global Stash by SKK: installed, but its keyword or stash isn't there (another version?): not linked")
		return
	endif
	if !(stash.GetBaseObject() as Container)   ; review A1: 0xFAE a reference, but not a container's (another version's numbering)
		Log("Field kit: Global Stash by SKK: installed, but its stash " + KitHex56(stash.GetFormID()) + " isn't a container (another version?): not linked")
		return
	endif
	GlobalVariable option
	string optionText = "its auto transfer"
	if abInSettlement
		option = Game.GetFormFromFile(SkkAutoTransferID, SkkPlugin) as GlobalVariable
	else
		option = Game.GetFormFromFile(SkkStandaloneID, SkkPlugin) as GlobalVariable
		optionText = "its standalone workbench link"
	endif
	if option && option.GetValue() <= 0.0
		Log("Field kit: Global Stash by SKK: " + optionText + " off: not linked (it won't touch the kit)")
		return
	endif
	akKit.SetLinkedRef(stash, WorkshopItemKeyword)
	akKit.SetLinkedRef(stash, LinkedWorkbenchContainerKeyword)
	akKit.AddKeyword(skk)
	kitStashRef = stash
	kitBagLinked = false
	string onText = optionText + " on"
	if !option
		onText = optionText + "'s global not found: counted as on"
	endif
	Log("Field kit: Global Stash by SKK: the kit linked to its stash first (SKK_GSSKeyword " + KitHex56(skk.GetFormID()) + ", the stash " + KitHex56(stash.GetFormID()) + "; " + onText + "): its workbench handler leaves the kit alone")
EndFunction

; KitStash, right before GoToKit's activation (every mode, the game's armour bench too, and KitRetry's): the pre-link read
; back, since the game's WorkbenchScript could link the kit again after its load; not the stash: both links made again.
Function KitStashBack(ObjectReference akKit)
	ObjectReference stash = kitStashRef
	if !akKit || !stash || !WorkshopItemKeyword || !LinkedWorkbenchContainerKeyword
		return
	endif
	ObjectReference linked = akKit.GetLinkedRef(WorkshopItemKeyword)
	if linked == stash
		Log("Field kit: mode " + kitMode + ": the kit's link at the activation: the stash")
		return
	endif
	string was = "none"
	if linked && linked == kitLinkWs
		was = "the settlement's workshop " + linked.GetFormID()
	elseif linked
		was = "" + linked.GetFormID()
	endif
	akKit.SetLinkedRef(stash, WorkshopItemKeyword)
	akKit.SetLinkedRef(stash, LinkedWorkbenchContainerKeyword)
	Log("Field kit: mode " + kitMode + ": the kit's link at the activation: " + was + ": relinked after its load")
EndFunction

; KitRetry (KitMenuDone: a fast close, afHeld s after the open, with no change made, at afClosedAt; asIn: where the player
; was), once an attempt: the same kit used again. SKK's handler disables a bench it hasn't linked (that closed the menu),
; links it and enables it again; a bench it has linked stays open on its next use (test 52, 13:50:51). So: up to
; KitRetryWait, in KitRetryPoll steps (WaitMenuMode: real time, menus included), for the kit enabled again, its 3D loaded
; and the player out of it (an activation while still in it can be lost, as NextKitMode's KitLeaveWait says), then
; KitRetrySettle, and GoToKit again (the read-back, the activation, the attempt's ticks afresh) with the menu's open
; forgotten (lookMenuSeen, kitMenuAt, kitInAtOpen, kitMenuGuess). The caller holds kitClosing: the kick's exit and a late
; close are ignored meanwhile. KitTick's timer stops till that GoToKit (its watchdog, out of the kit and every menu for
; KitWatchdog, would end the session meanwhile). True: nothing more for KitMenuDone (used again, or the session ended or
; moved on meanwhile); false: the kit not back in time, KitMenuDone goes on to the next mode (2026-11-09a's path). The
; retry's own fast close goes to the next mode too (KitMenuDone).
bool Function KitRetryNow(float afClosedAt, float afHeld, string asIn)
	kitRetried = true
	CancelTimer(TimerKit)
	ObjectReference kit = lookKit
	string head = "Field kit: mode " + kitMode + ": the menu closed " + Hundredths(afHeld) + " s after it opened, no change: under KitFastClose " + Tenths(KitFastClose) + " s, " + asIn
	bool wasOff = false
	bool back = false
	float waited = Utility.GetCurrentRealTime() - afClosedAt
	while !back
		if !kit || !customising || lookEnding || kitSwitching || lookKit != kit
			return true
		endif
		if kit.IsDisabled()
			wasOff = true
		elseif kit.Is3DLoaded() && !InKit()
			back = true
		endif
		if !back
			if waited >= KitRetryWait
				string why = "the kit still disabled"
				if !kit.IsDisabled()
					why = Ternary(kit.Is3DLoaded(), "the player still in it", "its 3D not loaded")
				endif
				Log(head + ": not used again (KitRetry): " + why + " after " + Tenths(waited) + " s")
				return false
			endif
			kitOutSince = -1.0
			Utility.WaitMenuMode(KitRetryPoll)
			waited = Utility.GetCurrentRealTime() - afClosedAt
		endif
	endwhile
	kitOutSince = -1.0
	Utility.WaitMenuMode(KitRetrySettle)
	if !customising || lookEnding || kitSwitching || lookKit != kit
		return true
	endif
	lookMenuSeen = false
	kitMenuGuess = false
	kitMenuAt = -1.0
	kitInAtOpen = false
	string ready = "not disabled, the player out of it after "
	if wasOff
		ready = "enabled again after "
	endif
	Log(head + ": the kit used again (KitRetry), " + ready + Tenths(waited) + " s")
	if kitStashRef
		; Review A1: KitStash's pre-link closed fast all the same (SKK took it for no link of its own and linked the kit
		; itself, or a Tab-out): the retry keeps the kit's link as it is now, so GoToKit's read-back never puts the pre-link
		; back over SKK's own.
		ObjectReference linked = None
		if WorkshopItemKeyword
			linked = kit.GetLinkedRef(WorkshopItemKeyword)
		endif
		string now = "none"
		if linked && linked == kitStashRef
			now = "the stash"
		elseif linked
			now = "" + linked.GetFormID() + ", not the pre-link's stash"
		endif
		Log("Field kit: mode " + kitMode + ": the pre-linked kit closed fast all the same: the retry keeps its link as it is (" + now + "), no read-back")
		kitStashRef = None
	endif
	GoToKit()
	return true
EndFunction

; Eight hex digits of a FormID (FE... and FF... ones are negative in Papyrus), as the plugin's log and F4SE's name forms.
string Function KitHex56(int aiValue)
	int v = aiValue
	int top = 0
	if v < 0
		v = v + 2147483647 + 1
		top = 8
	endif
	string out = ""
	int k = 0
	while k < 8
		int d = v % 16
		if k == 7
			d += top
		endif
		out = KitHexDigit56(d) + out
		v = v / 16
		k += 1
	endwhile
	return out
EndFunction

string Function KitHexDigit56(int aiDigit)
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

; ---------------------------------------------------------------------------
; 2026-11-09a (test 51): the field kit's [Look] KitHeld (CMB_LookOptions bit 2) and the parked bike's ParkedReload (bit 4)
; ---------------------------------------------------------------------------
; Test 51: the toolbox (mode 1) can't be sat in; its menu opened 0.1 s after the activation and closed with the failed
; entry, and the open alone remembered it. With KitHeld a mode counts only after its menu stayed open KitMenuHeld, a mod
; event came, or the player was in the kit (at the menu's open or its close); a fast close with none of those tries the
; next mode. Automatic: the armour bench (3), then the game's own (4, WorkbenchArmorA); a remembered 1 or 2 is forgotten.
; KitHeld 0: 2026-11-08a's (the toolbox, then the bench; remembered on the menu's open).

float Property KitMenuHeld = 2.0 AutoReadOnly
{KitHeld: a menu open this long (real time: timers don't run in it) counts as the mode working.}

bool kitHeldOn = false         ; KitHeld for this session (BeginCustomise reads CMB_LookOptions once)
float kitMenuAt = -1.0         ; KitHeld: real time of this attempt's menu open (-1: no open event, KitTick's guess)
bool kitInAtOpen = false       ; KitHeld: the player in the kit when the menu opened
bool kitRemembered = false     ; KitHeld: this attempt's "worked" said (KitRemember once an attempt)
bool kitClosing = false        ; KitHeld: KitMenuDone deciding (the kit's exit leaves it be)

; Automatic's first mode with KitHeld: the remembered 3 or 4 (4 only with WorkbenchArmorA filled), else the armour bench
; (3). A remembered 1 or 2 (the toolbox, remembered on its menu's open alone) is forgotten: CMB_KitWorked -1, so once.
int Function KitStartMode()
	if !CMB_KitWorked
		return 3
	endif
	int worked = CMB_KitWorked.GetValue() as int
	if worked == 1 || worked == 2
		CMB_KitWorked.SetValue(-1.0)
		Log("Field kit: CMB_KitWorked " + worked + " (" + KitModeText(worked) + ", remembered on its menu's open alone) forgotten: automatic starts at the armour bench")
	elseif worked == 4 && WorkbenchArmorA
		return 4
	endif
	return 3
EndFunction

; The mode automatic tries after aiMode, 0 for none (and for a forced mode). KitHeld: the armour bench (3), then the
; game's (4, if WorkbenchArmorA is filled), then none; off: 2026-11-08a's 1 (or 2), then 3, then none.
int Function KitNextMode(int aiMode)
	if !kitAuto
		return 0
	endif
	if aiMode < 3
		return 3
	elseif kitHeldOn && aiMode == 3 && WorkbenchArmorA
		return 4
	endif
	return 0
EndFunction

; KitHeld: this attempt's mode worked (asWhy: "a change made", "its menu open 4.2 s", "the player in it"); automatic
; remembers it in CMB_KitWorked. Once an attempt.
Function KitRemember(string asWhy)
	if kitRemembered
		return
	endif
	kitRemembered = true
	if kitAuto && CMB_KitWorked
		CMB_KitWorked.SetValue(kitMode as float)
		Log("Field kit: mode " + kitMode + " worked (" + asWhy + "): remembered (CMB_KitWorked " + kitMode + ")")
	else
		Log("Field kit: mode " + kitMode + " worked (" + asWhy + ")")
	endif
EndFunction

; KitHeld: this attempt's mode failed (asWhy); automatic forgets it if it was the remembered one (the next session
; starts at the armour bench again).
Function KitForget(string asWhy)
	if !kitAuto || !CMB_KitWorked
		return
	endif
	if (CMB_KitWorked.GetValue() as int) == kitMode
		CMB_KitWorked.SetValue(-1.0)
		Log("Field kit: CMB_KitWorked " + kitMode + " forgotten (" + asWhy + ")")
	endif
EndFunction

; KitHeld, the menu's close (or the kit left, asEnd says which) after the menu was seen: worked (a mod event came, the
; menu stayed open KitMenuHeld, or the player was in the kit at its open, in KitTick's menu without its event, or now):
; KitRemember, and the session ends; else it closed at once: the line, the next mode (NextKitMode: the remembered mode
; forgotten first), or with none the session ends. One thread: kitClosing (the caller checks it; set here before any
; call that lets another thread run). 2026-11-10a's [Look] KitRetry: a close under KitFastClose with no change made never
; counts as worked: the first one the same kit used again (KitRetryNow, once an attempt), the second the next mode.
Function KitMenuDone(string asEnd)
	kitClosing = true
	float held = -1.0
	float now = Utility.GetCurrentRealTime()
	if kitMenuAt >= 0.0
		held = now - kitMenuAt
	endif
	bool inNow = InKit()
	if !customising || lookEnding || kitSwitching
		kitClosing = false
		return
	endif
	; 2026-11-10a (test 52, [Look] KitRetry, CMB_LookOptions bit 256): a menu closed under KitFastClose with no change made
	; (Global Stash by SKK's handler shut a bench it hadn't linked in 0.17 s) never counts as "worked" by the player being in
	; the kit, the retry's own close included (test 52 remembered a kicked mode): the first one uses the same kit again
	; (KitRetryNow below), the second goes to the next mode with the remembered mode forgotten (NextKitMode's KitForget).
	bool fast = false
	if lookEvents == 0 && held >= 0.0 && held < KitFastClose
		fast = LookOption(256)
	endif
	if lookEvents > 0 || held >= KitMenuHeld || ((kitInAtOpen || kitMenuGuess || inNow) && !fast)
		if lookEvents > 0
			KitRemember("a change made")
		elseif held >= KitMenuHeld
			KitRemember("its menu open " + Tenths(held) + " s")
		else
			KitRemember("the player in it")
		endif
		kitClosing = false
		EndCustomise(asEnd)
		return
	endif
	if fast
		string inText = "the player never in the kit"
		if kitInAtOpen
			inText = "the player in the kit at its open doesn't count"
		elseif kitMenuGuess || inNow
			inText = "the player in the kit doesn't count"
		endif
		if !kitRetried
			if KitRetryNow(now, held, inText)
				kitClosing = false
				return   ; used again (its menu's open and close decide), or the session ended meanwhile
			endif
		else
			Log("Field kit: mode " + kitMode + ": the menu closed again " + Hundredths(held) + " s after it opened, no change: under KitFastClose " + Tenths(KitFastClose) + " s, " + inText + ": used again once already (KitRetry): this mode doesn't work here")
		endif
	else
		Log("Field kit: mode " + kitMode + ": the menu closed " + Tenths(held) + " s after it opened, no change made, the player never in the kit: this mode doesn't work here")
	endif
	bool switched = NextKitMode("its menu closed at once")
	kitClosing = false
	if !switched
		EndCustomise("the menu closed at once")
		Debug.Notification("The field kit couldn't be used here.")
	endif
EndFunction

; ParkedReload (ParkedLookAfter: a look put on the parked bike outside a ride, entries applied): test 51's parked bike
; stayed grey after an MCM apply (the runtime swap's palette entries), green once its 3D was loaded again after a ride.
; So its 3D is loaded again the same way: hidden, then shown. Never while riding, getting on (mounting), busy or customising,
; nor on a bike not shown. Behind the pause menu (the MCM) the wait between them lasts until the menu's close. The review of
; 2026-11-09a (A1): shown again at once, not through EnableParked: its ParkGuard ask counted the player, who stands at the bike
; at every reload (the field kit's stand 52 out, the activation, the MCM beside it), and hid it in front of them; it stood
; there solid till this Disable, so no one is inside its place.
Function ParkedReload(string asFrom)
	string why = ""
	if riding
		why = "riding"
	elseif mounting
		why = "getting on"
	elseif busy
		why = "busy (" + BusyText() + ")"
	elseif customising
		why = "customising"
	endif
	if why == ""
		; Claimed before calling anything: every call below lets another thread run.
		busy = true
		NoteBusy("the parked bike's look")
		if !BikeRef || BikeRef.IsDisabled() || !BikeRef.Is3DLoaded()
			busy = false
			why = "the bike not shown"
		endif
	endif
	if why != ""
		Log("Look: the parked bike's 3D not loaded again (" + asFrom + ", ParkedReload): " + why)
		return
	endif
	BikeRef.Disable()
	; The wait EnableParked's room ask made (RoomPollInterval): behind the pause menu it returns at the menu's close, so the
	; enable loads the 3D outside the menu as before.
	Utility.Wait(RoomPollInterval)
	ParkedLookDueNow("the bike's enable")
	BikeRef.Enable(false)
	busy = false
	Log("Look: the parked bike's 3D loaded again for its colours (" + asFrom + ", ParkedReload)")
EndFunction

; MCM "Apply the look" (CMB_MCMRelay.LookApply): a faction set (1-11) first (the paint and both tanks'
; and the fender's badge, the right following; since 2026-11-08a the set's plate, if it has one, with
; the plate's own text and colours), then every slot clamped to its list and the Free colour's hue
; (0-359, whole) and shade (0-3), then put on (the ridden bike's worn look at the next getting on).
; Also the way back to stock with free customising off.
Function LookApplyFromMcm()
	LookHueWanted("the MCM")   ; 2026-11-09a ([Look] HueFree): the hue or shade moved chooses Free colour (a set here wins)
	if !CMB_LookCode || !CMB_LookCategories
		Log("Look: from the MCM: no look records (an older ESP): nothing done.")
		return
	endif
	int set = 0
	if CMB_LookFactionSet
		set = CMB_LookFactionSet.GetValue() as int
	endif
	if set >= 1
		if LookSetPaint && LookSetTank && LookSetFender && set < LookSetPaint.Length && set < LookSetTank.Length && set < LookSetFender.Length && CMB_Look_Paint && CMB_Look_TankL && CMB_Look_TankR && CMB_Look_Fender
			CMB_Look_Paint.SetValue(LookSetPaint[set] as float)
			CMB_Look_TankL.SetValue(LookSetTank[set] as float)
			CMB_Look_TankR.SetValue(LookFollowLeft as float)
			CMB_Look_Fender.SetValue(LookSetFender[set] as float)
			Log("Look: faction set " + set + ": paint " + LookName(LookSlotPaint, LookSetPaint[set]) + " (" + LookSetPaint[set] + "), tanks " + LookName(LookSlotTankL, LookSetTank[set]) + " (" + LookSetTank[set] + "), fender " + LookName(LookSlotFender, LookSetFender[set]) + " (" + LookSetFender[set] + ")" + LookSetPlateNow(set))
		else
			Log("Look: faction set " + set + " is not among the plugin's sets: nothing set.")
		endif
		CMB_LookFactionSet.SetValue(0.0)
	endif
	int s = 0
	while s < LookSlots
		GlobalVariable g = LookGlobal(s)
		FormList options = LookList(s)
		if g && options
			float value = g.GetValue()
			int i = value as int
			if i < 0 || i >= options.GetSize() || value != (i as float)
				int stock = 0
				if s == LookSlotTankR
					stock = LookFollowLeft
				endif
				Log("Look: from the MCM: " + LookSlotText(s) + " " + value + " is no option: " + LookName(s, stock) + " (" + stock + ")")
				g.SetValue(stock as float)
			endif
		endif
		s += 1
	endwhile
	Log("Look: from the MCM: " + LookNow())
	LookHueFromMcm()
	ApplyLook("the MCM")
EndFunction

; 2026-11-08a, LookApplyFromMcm's faction set: its plate (LookSetPlate, -1 = none: unchanged) with the
; plate's own text, letters and background; returns the line's ", plate ..." ("" with an older ESP).
string Function LookSetPlateNow(int aiSet)
	if !CMB_Look_Plate || !LookSetPlate
		return ""
	endif
	int plate = -1
	if aiSet >= 0 && aiSet < LookSetPlate.Length
		plate = LookSetPlate[aiSet]
	endif
	FormList options = LookList(LookSlotPlate)
	if plate < 0 || (options && plate >= options.GetSize())
		return ", plate unchanged"
	endif
	CMB_Look_Plate.SetValue(plate as float)
	int s = LookSlotPlateText
	while s <= LookSlotPlateBack
		GlobalVariable g = LookGlobal(s)
		if g
			g.SetValue(0.0)
		endif
		s += 1
	endwhile
	return ", plate " + LookName(LookSlotPlate, plate) + " (" + plate + ") with its own text and colours"
EndFunction

; 2026-11-08a, LookApplyFromMcm: the MCM's "Paint hue" (whole, 0-359) and "Paint shade" (0-3) clamped,
; and said (they colour the paint only with Paint "Free colour").
Function LookHueFromMcm()
	if !CMB_LookHue || !CMB_LookShade
		return
	endif
	float hue = CMB_LookHue.GetValue()
	int h = Math.Floor(hue + 0.5)
	if h < 0
		h = 0
	elseif h > 359
		h = 359
	endif
	if hue != (h as float)
		CMB_LookHue.SetValue(h as float)
	endif
	float shade = CMB_LookShade.GetValue()
	int sh = Math.Floor(shade + 0.5)
	if sh < 0
		sh = 0
	elseif sh > 3
		sh = 3
	endif
	if shade != (sh as float)
		CMB_LookShade.SetValue(sh as float)
	endif
	Log("Look: from the MCM: paint hue " + h + " shade " + LookShadeName(sh) + Ternary(LookChoice(LookSlotPaint, false) == LookPaintFree, "", " (used with Paint \"Free colour\" only)"))
EndFunction

string Function LookShadeName(int aiShade)
	if aiShade == 0
		return "Deep"
	elseif aiShade == 1
		return "Normal"
	elseif aiShade == 2
		return "Light"
	endif
	return "Pastel"
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
	if riding
		; 2026-11-01a: the game's own IsInWater, for comparing with the plugin's depth ("fx: into the water").
		Log("In water while riding (the wade watch): " + abInWater)
	endif
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
	NoteBusy("getting off into deep water")
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
	if busy || PlayerRef.IsInInterior() || InClosedWorld()
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
	NoteBusy("bringing the bike after a swim")
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
	EnableParked(true, 3, 0.0, true)   ; ShoreBikeDistance or CallAheadDistance from the player (not counted)
	ForgetDoor()
	busy = false
	Log("Bike brought back after a swim (" + away + " units from the deep water, in water: " + inWater + ").")
	Debug.Notification("Your motorbike rolls up.")
EndFunction

; Hit events are one-shot: OnHit registers again for the next one. 2026-11-01a: also with
; "Thrown off when hit" off while the reaction window is on (CMB_PoseReactionWindow over 0: a hit's
; standing clips are told from a lost pose by it); with both at 0 nothing registers (2026-10-31a).
Function WatchForHits()
	if riding && (CMB_DismountOnHit.GetValue() > 0.0 || ReactionWindow() > 0.0)
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
	; 2026-11-02a: the ride's hit events and power attacks, every one delivered (the "Hit while riding"
	; lines are one a second at most): Steady's A/B as a ratio, at getting off (RideWatchesOff). The
	; registration is one-shot and comes back after the hostile path's wait, so hits within about 0.1 s
	; of an enemy's are not seen, and with both switches of WatchForHits off none is (the line says so).
	if akAggressor != PlayerRef
		rideHits += 1
		if abPowerAttack
			ridePowerHits += 1
		endif
	endif
	; 2026-11-01a: any hit starts the reaction window, before the hitGrace return (test 47's episode
	; A, the rider standing 1.4 s after getting on in a fight, was inside hitGrace).
	reactionAt = Utility.GetCurrentRealTime()
	reactionWhat = "a hit"
	Actor attacker = akAggressor as Actor
	if busy || hitGrace || !attacker || attacker == PlayerRef || !attacker.IsHostileToActor(PlayerRef)
		if hitGrace && attacker && attacker != PlayerRef
			LogHit(abPowerAttack, abHitBlocked, "in the first " + (HitGraceTime as int) + " s after getting on: not counted")
		endif
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
	; 2026-11-01a: the hit may have come only for the reaction window, "Thrown off when hit" off.
	bool knockOffs = CMB_DismountOnHit.GetValue() > 0.0
	; 2026-11-06a (test 49: every power attack outside the grace threw the rider off, 6 of 6 at 1.8-2.5% health): with
	; the MCM's "Power attacks throw you off" off (CMB_KnockOffPower 0, the default) a power attack is a hit like any
	; other, judged by Big hit's share; explosions always throw off. On (1), or an older ESP without the global: every
	; power attack does, as the 2026-11-02a build.
	bool powerThrows = !CMB_KnockOffPower || CMB_KnockOffPower.GetValue() > 0.0
	if knockOffs && ((abPowerAttack && powerThrows) || explosion || threshold <= 0.0 || lost >= threshold)
		Log("Knocked off: lost " + lost + "% health, power attack " + abPowerAttack + ", explosion " + explosion)
		AutoDismount("You're knocked off the motorbike.", true)
	else
		string notOff = Ternary(knockOffs, "not knocked off", "not knocked off (the MCM's Thrown off when hit is off)")
		if knockOffs && abPowerAttack
			notOff = "not knocked off (a power attack under Big hit's " + Tenths(threshold) + "%: the MCM's Power attacks throw you off is off)"
		endif
		LogHit(abPowerAttack, abHitBlocked, "lost " + Tenths(lost) + "% health since the last tick: " + notOff)
		WatchForHits()
	endif
EndEvent

; Test 47: a hit that doesn't knock the rider off, logged one a second at most (test 47's rider pose
; was disturbed for 2.3 s, 1.4 s after getting on in a fight, and nothing said whether a hit did it).
Function LogHit(bool abPowerAttack, bool abBlocked, string asWhat)
	float now = Utility.GetCurrentRealTime()
	if now - hitLoggedAt >= 1.0 || now < hitLoggedAt
		hitLoggedAt = now
		Log("Hit while riding: power attack " + abPowerAttack + ", blocked " + abBlocked + ", " + asWhat + ".")
	endif
EndFunction

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

; 2026-11-01a: three handlers share this event, in this order. First the bike's landing cues
; (JumpDown, SyncRight, SyncLeft: LandingCue), which return at once: the footstep watch below would
; take every SyncRight of the seated clips for a standing footstep. Then the footstep watch, which
; leaves standing clips alone within the reaction window (a hit, an item used, a stagger:
; CMB_PoseReactionWindow; 0 = as 2026-10-31a).
Event OnAnimationEvent(ObjectReference akSource, string asEventName)
	if asEventName == LandCueEvent || asEventName == LandSyncEvent || asEventName == LandSyncEvent2
		LandingCue(asEventName)
		return
	endif
	if !riding || busy || !riderPoseApplied || poseRetryWaiting || PlayerRef.IsWeaponDrawn()
		return
	endif
	; 2026-11-02a (test 48: in first person 10 re-applies in 20 s, the first-person graph's walk clips'
	; footsteps): the plugin's [Tilt] PoseFirstPerson writes CMB_RiderPoseOff -1 in first person (the
	; Pip-Boy's too), where the third-person clips aren't measured; its footsteps are left alone. With
	; PoseFirstPerson=0 or an older plugin it is never negative: as 2026-11-01a.
	if CMB_RiderPoseOff && CMB_RiderPoseOff.GetValue() < 0.0
		if !firstFootSaid
			firstFootSaid = true
			Log("Standing footsteps in first person: the first-person clips, not the pose: left alone (the plugin's PoseFirstPerson).")
		endif
		return
	endif
	if poseRetries >= MaxPoseRetries
		UnregisterForAnimationEvent(PlayerRef, FootstepEvent)
		Log("Rider pose still not showing after " + poseRetries + " tries; giving up for this ride.")
		return
	endif
	if InReaction("Standing footsteps")
		return
	endif
	poseRetryWaiting = true
	StartTimer(PoseRetryInterval, TimerPoseRetry)
	poseRetries += 1
	SwitchToRiderFlavor("standing footsteps while riding: applying the rider pose again, try " + poseRetries)
EndEvent

; Test 47: the plugin's word on the clips (CMB_RiderPoseOff, its [Tilt] PoseCheck: the raw seconds
; the clips have been off the seat, by the knees' height), at every ride tick from the first,
; TickInterval after getting on. The footstep watch only hears a lost pose once standing walk clips
; play; a bike standing or turning on the spot sends none. Once the reading is CMB_PoseOffAfter (3 s,
; longer than any stagger or hit reaction) or more, and outside the reaction window, the rider pose
; is applied again as the footstep watch does: the same count (MaxPoseRetries a ride), the same gate
; (no try within PoseRetryInterval of the last, by either). Weapon out: the standing clips are meant
; (the ground-planted bike), nothing done. No plugin, PoseCheck=0 or an older ESP: the global stays 0
; or None, and nothing is done (2026-10-31a).
Function CheckRiderPose()
	if !CMB_RiderPoseOff || poseRetryWaiting || busy || !riding || !riderPoseApplied
		return
	endif
	float off = CMB_RiderPoseOff.GetValue()
	float after = 3.0
	if CMB_PoseOffAfter
		after = CMB_PoseOffAfter.GetValue()
	endif
	if off <= 0.0 || off < after || poseRetries >= MaxPoseRetries || PlayerRef.IsWeaponDrawn()
		return
	endif
	if InReaction("The clips " + Tenths(off) + " s off the seat")
		return
	endif
	poseRetryWaiting = true
	StartTimer(PoseRetryInterval, TimerPoseRetry)
	poseRetries += 1
	SwitchToRiderFlavor("the plugin reads the clips off the seat for " + Tenths(off) + " s: applying the rider pose again, try " + poseRetries)
EndFunction

; The MCM's "Pose re-check pause after a hit (s)": 0 when off or with an older ESP.
float Function ReactionWindow()
	if !CMB_PoseReactionWindow
		return 0.0
	endif
	return CMB_PoseReactionWindow.GetValue()
EndFunction

; True within the reaction window: CMB_PoseReactionWindow seconds of a hit taken or an item used
; while riding, or while the stagger watch says staggered. Its standing clips are a reaction, not
; the pose lost, so asWhat (the footstep watch's or CheckRiderPose's word) is left alone; one line
; a reaction. Off (0, or an older ESP): never, as 2026-10-31a.
; 2026-11-02a (test 48: the Pip-Boy check cut an animation mod's stimpak clip 0.6 s into it, its
; prop held 15 minutes and the camera stuck): first the use window, CMB_PoseUseWindow seconds from
; when an item's use clip can start (itemAt: the use, or the menu's close), whatever the hit window
; says; one line an item. 0 or None: as 2026-11-01a.
bool Function InReaction(string asWhat)
	float now = Utility.GetCurrentRealTime()
	if itemAt > now
		itemAt = -100.0   ; an earlier session's stamp
	endif
	float useWin = UseWindow()
	if useWin > 0.0 && now - itemAt < useWin
		if itemAt != itemLeft
			itemLeft = itemAt
			Log(asWhat + " " + Tenths(now - itemAt) + " s after " + itemWhat + " was used: its use clip, not the pose: left alone.")
		endif
		return true
	endif
	float window = ReactionWindow()
	if window <= 0.0
		return false
	endif
	if reactionAt > now
		reactionAt = -100.0   ; an earlier session's stamp (the real-time clock starts again at each launch)
	endif
	string note = ""
	float which = 0.0
	if staggered && staggeredAt > now
		staggeredAt = now   ; an earlier session's stamp
	endif
	if staggered && now - staggeredAt < StaggerHoldMax
		note = "while staggered"
		which = staggeredAt
	elseif now - reactionAt < window
		note = Tenths(now - reactionAt) + " s after " + reactionWhat
		which = reactionAt
	else
		return false
	endif
	if which != reactionLeft
		reactionLeft = which
		Log(asWhat + " " + note + ": a hit reaction or stagger, not the pose: left alone.")
	endif
	return true
EndFunction

; 2026-11-02a (test 48: 8 staggers with Steady on, 4 of 4 power attacks): which perk Steady gives, by the
; console's CMB_RiderSteadyWay: 1 = CMB_RiderSteadyPerk2 (x0, two condition tabs and EPFB 0, as the game's
; only Mod Incoming Stagger perk; the default), 2 = that perk itself, mod_armor_LessStagger (00245AFE, Add
; -1: a stagger one step less), by its FormID at runtime, 0 = 2026-11-01a's CMB_RiderSteadyPerk (x0,
; three tabs). An older ESP (no global, or no second perk): CMB_RiderSteadyPerk, as 2026-11-01a.
Perk Function SteadyWanted()
	int way = 0
	if CMB_RiderSteadyWay
		way = CMB_RiderSteadyWay.GetValue() as int
	endif
	if way == 1 && CMB_RiderSteadyPerk2
		return CMB_RiderSteadyPerk2
	elseif way == 2
		Perk game = Game.GetFormFromFile(0x00245AFE, "Fallout4.esm") as Perk
		if game
			return game
		endif
	endif
	return CMB_RiderSteadyPerk
EndFunction

; The perk's name for the log (its editor ID isn't there at runtime).
string Function SteadyName(Perk akPerk)
	if !akPerk
		return "none"
	elseif akPerk == CMB_RiderSteadyPerk2
		return "CMB_RiderSteadyPerk2"
	elseif akPerk == CMB_RiderSteadyPerk
		return "CMB_RiderSteadyPerk"
	endif
	return "the game's mod_armor_LessStagger (00245AFE)"
EndFunction

string Function SteadyWayText(Perk akPerk)
	if akPerk == CMB_RiderSteadyPerk2
		return "x0, two tabs"
	elseif akPerk == CMB_RiderSteadyPerk
		return "2026-11-01a's x0, three tabs"
	endif
	return "the game's -1"
EndFunction

; Steady as it stands, for the stagger and the ride's lines: "on: CMB_RiderSteadyPerk2, x0, two tabs".
string Function SteadyNow()
	if steadyGiven
		return "on: " + SteadyName(steadyGiven) + ", " + SteadyWayText(steadyGiven)
	elseif steadyKeptSaid
		return "on: the game's mod_armor_LessStagger, an armour lining's"
	endif
	return "off"
EndFunction

; Test 47 ("Steady in the saddle", CMB_RiderSteady): a hidden perk, Mod Incoming Stagger x0, on the
; player while riding and off them otherwise. Called on getting on, at every ride tick (an MCM change
; is taken up mid-ride), on getting off, by the clean-up after it and after a load (a save made
; mid-ride carries the perk, and one made off the bike must not). An older ESP (no perk): nothing.
; 2026-11-02a: the perk SteadyWanted picks. Only the perk this script gave is taken off (steadyGiven):
; never a game perk already on the player (an armour lining's 00245AFE is left as it is), and either
; of ours that a save carried, or that a CMB_RiderSteadyWay change left, is taken off when it isn't the
; one wanted.
Function UpdateSteady(string asWhy)
	if !CMB_RiderSteadyPerk
		return
	endif
	Perk want = None
	if riding && CMB_RiderSteady && CMB_RiderSteady.GetValue() > 0.0
		want = SteadyWanted()
	endif
	if steadyGiven && steadyGiven != want
		PlayerRef.RemovePerk(steadyGiven)
		Log("Steady in the saddle: off (" + asWhy + "): " + SteadyName(steadyGiven) + " taken off.")
		steadyGiven = None
	endif
	; ours, carried by a save (11-01a's has no steadyGiven) or given before a CMB_RiderSteadyWay change
	if CMB_RiderSteadyPerk != want && PlayerRef.HasPerk(CMB_RiderSteadyPerk)
		PlayerRef.RemovePerk(CMB_RiderSteadyPerk)
		Log("Steady in the saddle: CMB_RiderSteadyPerk taken off (" + asWhy + "): not the one wanted.")
	endif
	if CMB_RiderSteadyPerk2 && CMB_RiderSteadyPerk2 != want && PlayerRef.HasPerk(CMB_RiderSteadyPerk2)
		PlayerRef.RemovePerk(CMB_RiderSteadyPerk2)
		Log("Steady in the saddle: CMB_RiderSteadyPerk2 taken off (" + asWhy + "): not the one wanted.")
	endif
	if want && !steadyGiven
		if PlayerRef.HasPerk(want)
			if want == CMB_RiderSteadyPerk || want == CMB_RiderSteadyPerk2
				steadyGiven = want   ; ours from a save: ours to take off
			elseif !steadyKeptSaid
				steadyKeptSaid = true
				Log("Steady in the saddle: " + SteadyName(want) + " is on the player already (an armour lining's): left as it is.")
			endif
		else
			PlayerRef.AddPerk(want, false)
			steadyGiven = want
			Log("Steady in the saddle: on (" + asWhy + "): " + SteadyName(want) + " (" + SteadyWayText(want) + ").")
		endif
	endif
EndFunction

; Test 47's diagnostics while riding, log only: items used (a remote OnItemEquipped on the player),
; the Pip-Boy and the favourites opening and closing, and the stagger watch. On at getting on and
; after a load into a ride, off at every way off (FinishRide).
Function RideWatchesOn()
	RegisterForRemoteEvent(PlayerRef, "OnItemEquipped")
	RegisterForMenuOpenCloseEvent(PipboyMenuName)
	RegisterForMenuOpenCloseEvent(FavoritesMenuName)
	if CMB_ViewMenu   ; 2026-11-09a: no Pip-Boy open yet (getting on, a load into a ride); None = an older ESP
		CMB_ViewMenu.SetValue(0.0)
	endif
	if CMB_StaggerWatchAbility
		PlayerRef.AddSpell(CMB_StaggerWatchAbility, false)
	endif
	QuickWatchTell(true)   ; 2026-11-10a, test 52: QuickUse's watch while riding
EndFunction

; 2026-11-10a (test 52, QuickUse): CMB_HotkeyF4SE's watch of CMB_RiderQuickUse on or off (through CastAs: this script
; runs without F4SE; without the helper or the global, an older ESP's, there is none), not waited for.
Function QuickWatchTell(bool abOn)
	if !CMB_RiderQuickUse
		return
	endif
	ScriptObject hotkey = CastAs("CMB_HotkeyF4SE")
	if hotkey
		Var[] args = new Var[1]
		args[0] = abOn
		hotkey.CallFunctionNoWait("QuickWatch", args)
	endif
EndFunction

Function RideWatchesOff()
	UnregisterForRemoteEvent(PlayerRef, "OnItemEquipped")
	UnregisterForMenuOpenCloseEvent(PipboyMenuName)
	UnregisterForMenuOpenCloseEvent(FavoritesMenuName)
	if CMB_ViewMenu   ; 2026-11-09a: off the bike in the Pip-Boy (its close isn't seen now)
		CMB_ViewMenu.SetValue(0.0)
	endif
	CancelTimer(TimerPipboyCheck)   ; a Pip-Boy check still to come is moot
	if CMB_StaggerWatchAbility
		PlayerRef.RemoveSpell(CMB_StaggerWatchAbility)
	endif
	staggered = false
	; 2026-11-02a: a camera check still to come is moot; a stagger's end still to tell is told now;
	; the ride's counts (Steady's A/B: way 1 ideally 0 staggers, power attacks included); no menu open,
	; no item in one.
	CancelTimer(TimerUseCamera)
	CancelTimer(TimerStaggerOver)
	if staggerOverPending
		staggerOverPending = false
		Log("Staggered while riding: the stagger over after " + Tenths(staggerLasted) + " s.")
	endif
	if CMB_DismountOnHit.GetValue() > 0.0 || ReactionWindow() > 0.0
		Log("Hit events this ride: " + rideHits + " (" + ridePowerHits + " power attacks; one at a time: hits within about a tenth of a second of an enemy's are not seen), staggers " + rideStaggers + " (Steady " + SteadyNow() + ").")
	else
		Log("Hits this ride: not watched (Thrown off when hit and the pose pause both off), staggers " + rideStaggers + " (Steady " + SteadyNow() + ").")
	endif
	itemInMenu = false
	riderMenuOpen = false
	steadyKeptSaid = false
	QuickWatchTell(false)   ; 2026-11-10a, test 52: QuickUse's watch off
	quickItem = None
EndFunction

; Test 47 ("using stim on bike ... like a skirt"): an item used while riding. Potions only (the
; stims, chems, food and drink; the bike's own armour is equipped too), one line a second at most.
; It starts the reaction window as a hit does.
Event Actor.OnItemEquipped(Actor akSender, Form akBaseObject, ObjectReference akReference)
	if !riding || !(akBaseObject as Potion)
		return
	endif
	; 2026-11-10a (test 52, QuickUse): CMB_HotkeyF4SE's own equip of a potion whose hotkey the plugin took at speed (its
	; QuickUsed came just before, within 2 s): the player's own use whatever CMB_RiderUseOwn finds, and its line below never
	; held back by the one-a-second limit. Then the use window and CMB_RiderItemUse as for any use (an animation mod's
	; decoration clip may follow, as after the Pip-Boy).
	bool quick = quickItem && akBaseObject == quickItem && Utility.GetCurrentRealTime() - quickAt <= 2.0
	if quick
		quickItem = None
	endif
	; 2026-11-06a (test 49: another mod's dummy potion right after a load went into the use watch, and the camera's
	; check after it forced the view for nothing): with CMB_RiderUseOwn 1 only the player's own uses count. The player
	; uses a potion in the Pip-Boy or the favourites (a menu open) or by a favourites hotkey (the item in a favourite
	; slot, or in the cache of them: a stack's last one leaves its slot as it is used); an item equipped outside both, or
	; a nameless one, is another mod's: logged, then no reaction window, no use window, no CMB_RiderItemUse, no camera
	; check. CMB_RiderUseOwn 0, an older ESP without it, or no F4SE: every potion, as the 2026-11-02a build.
	if !quick && !riderMenuOpen && CMB_RiderUseOwn && CMB_RiderUseOwn.GetValue() > 0.0 && ItemOwnUse(akBaseObject) == 0
		float at = Utility.GetCurrentRealTime()
		if at - itemOwnLoggedAt >= 1.0 || at < itemOwnLoggedAt
			itemOwnLoggedAt = at
			Log("Used " + akBaseObject + " while riding: not from the Pip-Boy, the favourites or a hotkey (another mod's item, a dummy's kind): left out of the use watch (CMB_RiderUseOwn 1).")
		endif
		return
	endif
	float now = Utility.GetCurrentRealTime()
	reactionAt = now
	reactionWhat = "an item used"
	if quick || now - itemLoggedAt >= 1.0 || now < itemLoggedAt
		itemLoggedAt = now
		Log("Used " + akBaseObject + " while riding.")
	endif
	; 2026-11-02a: the use window (and the plugin's signal, CMB_RiderItemUse) from when its use clip can
	; start: an animation mod plays it after the menus close, so an item used in the Pip-Boy or the
	; favourites is timed from that close (RiderMenu), one used outside them from now (another menu, the
	; console's say, has no close watched: from now too).
	itemWhat = "" + akBaseObject
	if riderMenuOpen
		itemInMenu = true
	else
		ItemSignal("")
	endif
EndEvent

; 2026-11-10a (test 52, QuickUse): CMB_HotkeyF4SE's word on a potion's quickkey the plugin took from the game at speed
; (aiValue: CMB_RiderQuickUse = count * 16 + aiSlot, aiSlot 1-12 as F4SE's GetFavorites lists them), told before it equips
; the item. aiCount: the stack as it stood; over 0: the script equips it now (the Pip-Boy's path: applied at once, no engine
; clip), marked for OnItemEquipped; else nothing used, said why. Only CMB_HotkeyF4SE calls it.
Form quickItem = None
float quickAt = -100.0

Function QuickUsed(Form akItem, int aiSlot, int aiValue, int aiCount)
	if akItem as Potion && aiCount > 0
		quickItem = akItem
		quickAt = Utility.GetCurrentRealTime()
		Log("Used " + akItem + " by its hotkey at speed: equipped by the script (QuickUse, slot " + aiSlot + ").")
	elseif akItem as Potion
		Log("Not used: " + akItem + " by its hotkey at speed: none left, the stack's last one gone (QuickUse, slot " + aiSlot + ", CMB_RiderQuickUse " + aiValue + ").")
	elseif akItem
		Log("Not used by its hotkey at speed: slot " + aiSlot + " holds " + akItem + " now, not a potion (QuickUse, CMB_RiderQuickUse " + aiValue + ").")
	else
		Log("Not used by its hotkey at speed: slot " + aiSlot + " is empty now (QuickUse, CMB_RiderQuickUse " + aiValue + ").")
	endif
EndFunction

; 2026-11-06a: CMB_RiderUseOwn's helpers, through CMB_HotkeyF4SE (F4SE's FavoritesManager; this script runs without
; F4SE). ItemOwnUse: 1 the player's own (a favourite, or in the cache of them), 0 another mod's (nameless, or in no
; favourite slot), -1 unknown (no favourites list: counted), -2 without the helper (counted). CacheFavourites: the
; favourites as they stand, kept by the helper (at getting on, after a load into a ride, at each menu's close).
float itemOwnLoggedAt = -100.0

int Function ItemOwnUse(Form akItem)
	ScriptObject hotkey = CastAs("CMB_HotkeyF4SE")
	if !hotkey
		return -2
	endif
	Var[] args = new Var[1]
	args[0] = akItem
	return hotkey.CallFunction("ItemOwnUse", args) as int
EndFunction

Function CacheFavourites()
	if !CMB_RiderUseOwn || CMB_RiderUseOwn.GetValue() <= 0.0
		return
	endif
	ScriptObject hotkey = CastAs("CMB_HotkeyF4SE")
	if hotkey
		hotkey.CallFunction("CacheFavourites", new Var[0])
	endif
EndFunction

; Test 47: the Pip-Boy and the favourites while riding, log only; and 0.6 s after the Pip-Boy
; closes, the plugin's reading (PipboyPoseCheck), with the reaction window on.
Function RiderMenu(string asMenuName, bool abOpening)
	if !riding
		return
	endif
	string what = "Pip-Boy"
	if asMenuName == FavoritesMenuName
		what = "Favourites"
	endif
	Log(what + Ternary(abOpening, " opened", " closed") + " while riding.")
	; 2026-11-02a: an item used in it is timed from this close (ItemSignal); with the use window on, no
	; Pip-Boy check for this close: the clips off the seat after it are the item's use clip.
	riderMenuOpen = abOpening
	; 2026-11-09a (test 50: the first-person tip ran in the Pip-Boy, its camera a first person): CMB_ViewMenu 1 while
	; the Pip-Boy is open on the bike, so the plugin's [View] TipMenu holds the tip off; set before the returns below.
	if CMB_ViewMenu && asMenuName == PipboyMenuName
		if abOpening
			CMB_ViewMenu.SetValue(1.0)
		else
			CMB_ViewMenu.SetValue(0.0)
		endif
	endif
	if !abOpening
		CacheFavourites()   ; 2026-11-06a: favourites change only in menus (CMB_RiderUseOwn)
	endif
	if !abOpening && itemInMenu
		itemInMenu = false
		ItemSignal("in the " + what)
		if UseWindow() > 0.0
			return
		endif
	endif
	if asMenuName == PipboyMenuName
		if abOpening
			CancelTimer(TimerPipboyCheck)
		elseif ReactionWindow() > 0.0
			StartTimer(PipboyCheckDelay, TimerPipboyCheck)
		endif
	endif
EndFunction

; Test 47's second guess at the stim's "skirt": the Pip-Boy's round trip leaving the seated pose
; disturbed. PipboyCheckDelay after it closes, a reading of the clips off the seat (CMB_RiderPoseOff
; over PipboyPoseOff) applies the rider pose again at once, as one of the footstep watch's tries
; (its count, and its gate set after). No hit is expected right after a menu, so the reaction window
; doesn't hold it; its switch does (CMB_PoseReactionWindow 0: no menu check, as 2026-10-31a).
Function PipboyPoseCheck()
	if !riding || busy || !riderPoseApplied || !CMB_RiderPoseOff || ReactionWindow() <= 0.0 || Utility.IsInMenuMode()
		return
	endif
	float off = CMB_RiderPoseOff.GetValue()
	if off <= PipboyPoseOff || poseRetries >= MaxPoseRetries || PlayerRef.IsWeaponDrawn()
		return
	endif
	; 2026-11-02a: through InReaction with the use window on (an item used outside the Pip-Boy shortly
	; before it was opened; one used in it skips this check: RiderMenu). 0: as 2026-11-01a.
	if UseWindow() > 0.0 && InReaction("The Pip-Boy closed and the clips are off the seat")
		return
	endif
	poseRetryWaiting = true
	StartTimer(PoseRetryInterval, TimerPoseRetry)
	poseRetries += 1
	SwitchToRiderFlavor("the Pip-Boy closed and the clips are off the seat for " + Tenths(off) + " s: applying the rider pose again, try " + poseRetries)
EndFunction

; ---------------------------------------------------------------------------
; 2026-11-02a (test 48): the item-use window, the camera after a use, the stagger's end
; ---------------------------------------------------------------------------

int Property TimerUseCamera = 50 AutoReadOnly
float Property UseCameraDelay = 6.0 AutoReadOnly
{2026-11-02a (test 48: the camera stuck after the first stimpak, its switch and zoom gone for 14 s till
getting off): the camera is looked at this long after an item's use clip can start (ItemSignal), log
only ("After ... was used: the camera switch on, looking on, moving on, the camera state 8"), retried
every UseCameraRetry while a menu is open, UseCameraMaxTries at most; with CMB_UseCameraFix 1 a stuck one
is put right (UseCameraCheck).}
float Property UseCameraRetry = 1.0 AutoReadOnly
int Property UseCameraMaxTries = 10 AutoReadOnly
float Property UseCameraRecheck = 2.0 AutoReadOnly
{After the view is entered again, looked at once more this long later: still held, a notification
(once a ride) tells the way out, getting off and on.}
int Property TimerStaggerOver = 51 AutoReadOnly
float Property StaggerOverDelay = 0.5 AutoReadOnly
{2026-11-02a (pose.md 1.5): the plugin's reading of the clips (CMB_RiderPoseOff) this long after a
stagger's end, for its line: back on the seat by themselves (all 8 of test 48's), or still off.}
int Property TimerKit = 52 AutoReadOnly
{2026-11-07a: the field kit's session, a tick a second while customising (KitTick).}
int Property TimerLook = 53 AutoReadOnly
{2026-11-07a: the look put on the first-person bike after its placing or hand-over, and the worn
bike's F4SE swap after the equip or a load (LookFollowUp), each outside busy.}
int Property TimerParkGuard = 54 AutoReadOnly
{2026-11-09a (the plugin's [Room] ParkGuard): the parked bike kept hidden while someone is in its
place, looked at again (ParkGuardTick), outside busy.}
float Property ParkGuardPoll = 0.5 AutoReadOnly
{... every this long while held.}
float Property ParkGuardMax = 15.0 AutoReadOnly
{... and still taken this long after it was hidden: once, a new spot beside or behind the player
(PickBikeSpot's park); none free, it waits, looked at every ParkGuardWait.}
float Property ParkGuardWait = 2.0 AutoReadOnly

; The console's CMB_PoseUseWindow (6; 0 or an older ESP: 0, as 2026-11-01a).
float Function UseWindow()
	if !CMB_PoseUseWindow
		return 0.0
	endif
	return CMB_PoseUseWindow.GetValue()
EndFunction

; The console's CMB_UseCameraFix (1; 0 or an older ESP: 0, no recovery).
int Function UseCameraFix()
	if !CMB_UseCameraFix
		return 0
	endif
	return CMB_UseCameraFix.GetValue() as int
EndFunction

; An item's use clip may start now (asWhere: "in the Pip-Boy", "in the Favourites"; "" for a use
; outside them): the use window from now (InReaction), the plugin's signal (CMB_RiderItemUse, a count
; 1-999, then 1 again: its [Tilt] UseLetGo lets go of the hands while the clip plays) and the camera's
; check UseCameraDelay on.
Function ItemSignal(string asWhere)
	itemAt = Utility.GetCurrentRealTime()
	if CMB_RiderItemUse
		int n = (CMB_RiderItemUse.GetValue() as int) % 999 + 1
		CMB_RiderItemUse.SetValue(n as float)
	endif
	if UseWindow() > 0.0 && asWhere != ""
		Log("Used " + itemWhat + " " + asWhere + ": its use clip may follow: the pose left alone for " + Tenths(UseWindow()) + " s.")
	endif
	useCameraTries = 0
	useCameraFixed = false
	StartTimer(UseCameraDelay, TimerUseCamera)
EndFunction

; F4SE's camera state through CMB_HotkeyF4SE (this script runs without F4SE): 0 first person, 7 and 8
; third person (F4SE's Game.psc lists the rest); -2 without the helper.
int Function CameraState()
	ScriptObject hotkey = CastAs("CMB_HotkeyF4SE")
	if !hotkey
		return -2
	endif
	return hotkey.CallFunction("CameraState", new Var[0]) as int
EndFunction

; The game's own camera views, which nothing stuck makes (F4SE's GameCamera states): 1 auto vanity, 2
; VATS, 3 free, 4 iron sights or a scope, 6 the tween menu, 11 bleedout, 12 dialogue.
bool Function GameCameraView(int aiState)
	return aiState == 1 || aiState == 2 || aiState == 3 || aiState == 4 || aiState == 6 || aiState == 11 || aiState == 12
EndFunction

string Function CameraStateText(int aiState)
	if aiState == -2
		return "unknown (no F4SE helper)"
	elseif aiState == 0
		return "0 (first person)"
	elseif aiState == 7 || aiState == 8
		return aiState + " (third person)"
	endif
	return aiState + " (neither first nor third person)"
EndFunction

; UseCameraDelay after an item's use: the camera's switch, looking and moving controls and its
; state, logged. With CMB_UseCameraFix 1, outside menus and the game's own views, a camera whose
; switch is off or stuck in a transition, furniture or mount state (5, 9, 10) has its view entered
; again, which resets the camera's state machine (no flavour switch: that was test 48's fault);
; UseCameraRecheck later, still held means another mod's input layer, which no script can release: a
; notification (once a ride) tells the way out. 0: the line only. The game's own views (1 auto
; vanity, 2 VATS, 3 free, 4 iron sights or a scope, 6 the tween menu, 11 bleedout, 12 dialogue) are
; waited out like a menu, at the check and at the recheck: never forced.
Function UseCameraCheck()
	if !riding
		return
	endif
	if Utility.IsInMenuMode()
		useCameraTries += 1
		if useCameraTries < UseCameraMaxTries
			StartTimer(UseCameraRetry, TimerUseCamera)
		else
			Log("After " + itemWhat + " was used: the camera not looked at (a menu open " + useCameraTries + " times).")
		endif
		return
	endif
	bool camSwitch = Game.IsCamSwitchControlsEnabled()
	int camState = CameraState()
	if GameCameraView(camState)
		useCameraTries += 1
		if useCameraTries < UseCameraMaxTries
			StartTimer(UseCameraRetry, TimerUseCamera)
		else
			useCameraFixed = false
			Log("After " + itemWhat + " was used: the camera in the game's own view, state " + camState + ": not looked at (" + useCameraTries + " times).")
		endif
		return
	endif
	string line = "the camera switch " + Ternary(camSwitch, "on", "OFF") + ", looking " + Ternary(Game.IsLookingControlsEnabled(), "on", "OFF") + ", moving " + Ternary(Game.IsMovementControlsEnabled(), "on", "OFF") + ", the camera state " + CameraStateText(camState)
	bool stuck = !camSwitch || camState == 5 || camState == 9 || camState == 10
	if useCameraFixed
		useCameraFixed = false
		if !stuck
			Log("After " + itemWhat + " was used, " + Tenths(UseCameraRecheck) + " s after the view was entered again: " + line + ": free.")
			return
		endif
		Log("After " + itemWhat + " was used, " + Tenths(UseCameraRecheck) + " s after the view was entered again: " + line + ": still held (another mod's input layer: getting off and on frees it).")
		if !useCameraNoted
			useCameraNoted = true
			Debug.Notification("An item animation still holds the camera: get off and on to free it.")
		endif
		return
	endif
	Log("After " + itemWhat + " was used: " + line + ".")
	if !stuck || UseCameraFix() < 1
		return
	endif
	if camState == 0
		Game.ForceFirstPerson()
	else
		Game.ForceThirdPerson()
	endif
	useCameraFixed = true
	Log("After " + itemWhat + " was used: " + Ternary(camSwitch, "the camera state stuck", "the camera switch off") + " with no use clip left to play: the view entered again (CMB_UseCameraFix 1).")
	StartTimer(UseCameraRecheck, TimerUseCamera)
EndFunction

; StaggerOverDelay after a stagger's end: its line, with the plugin's reading of the clips (pose.md
; 1.5: a re-seat would only be safe now, and test 48 shows none is needed; none is made).
Function StaggerOverLine()
	if !staggerOverPending
		return
	endif
	staggerOverPending = false
	string seat = ""
	if CMB_RiderPoseOff
		float off = CMB_RiderPoseOff.GetValue()
		if off < 0.0
			seat = "; in first person (the clips not measured there)"
		elseif off <= 0.0
			seat = "; the clips back on the seat by themselves"
		else
			seat = "; the clips still off the seat for " + Tenths(off) + " s (CheckRiderPose takes it at CMB_PoseOffAfter)"
		endif
	endif
	Log("Staggered while riding: the stagger over after " + Tenths(staggerLasted) + " s" + seat + ".")
EndFunction

; A load off the bike (OnGameReloaded): nothing a save made mid-ride, or an older build's, carries
; stays on (the perk, the stagger watch, the player's footstep sounds muted, a placed tail light or
; first-person bike).
Function LoadedOffTheBike()
	UpdateSteady("loaded off the bike")
	if CMB_StaggerWatchAbility
		PlayerRef.RemoveSpell(CMB_StaggerWatchAbility)
	endif
	staggered = false
	if AudioCategoryFSTplayer
		AudioCategoryFSTplayer.UnMute()
	endif
	fxMuted = false
	if tailRef || tailRefOld || viewRef || viewRefOld
		RemoveTwins()
	endif
EndFunction

; Once per fight, when weapons are off while riding: say how to get off. 2026-11-02a: also every tick
; (TickInterval, 1 s) the player's combat for the plugin's [Ram] PendingFoe=2 (CMB_RamCombat).
Function CombatHint()
	bool fighting = PlayerRef.IsInCombat()   ; the one call, as before
	SetRamCombat(fighting)
	if !fighting
		combatHinted = false
	elseif !combatHinted
		combatHinted = true
		if CMB_AllowCombat.GetValue() == 0.0
			Debug.Notification("You're in a fight! Use the Motorbike Keys (or your hotkey) to get off.")
		endif
	endif
EndFunction

; 2026-11-02a (test 48: 10 brakes for knock-over asks pending at the front wheel, 4 of them first asks
; deep in a fight): CMB_RamCombat 1 while the player is in combat, written only when it changes (and
; logged then), read by CMB_Slope.dll's [Ram] PendingFoe=2: a medium race whose ask is pending at the
; wheel is passed. False on getting off. An older ESP (None): never written, PendingFoe=2 acts as 1.
Function SetRamCombat(bool abOn)
	if CMB_RamCombat && (CMB_RamCombat.GetValue() > 0.5) != abOn
		CMB_RamCombat.SetValue(abOn as float)
		Log("Ram: the player " + Ternary(abOn, "in combat", "out of combat") + " (CMB_RamCombat " + (abOn as int) + ").")
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
; The AP watch (test 46, diagnostics)
; ---------------------------------------------------------------------------

; Test 45: after the rides the AP bar stayed at 77% through 30 s of walking, then at 0 for a
; minute: no drain and no refill, while the sprint's drain worked ("it has happened for a
; while"). Nothing in the mod touches AP, and what keeps the game's refill off isn't known. The
; player's AP, its rate and the rate's mult (value and base) and whether they sprint are logged
; ("AP: 77.0 of 100.0 (77% of its max), rate 5.0 (base 5.0), mult 100.0 (base 100.0), sprinting
; no; 12 s after getting off."): once at each getting on, and off the bike every APWatchEvery
; seconds for APWatchTime seconds after getting off, and past that while AP is under its max (a
; line no different from the last one only every APWatchQuiet polls) and once when it's back at
; it. CMB_Slope.dll's [Diag] APWatch logs the refill's gates in the game beside it ("AP watch
; (...)" in CMB_Slope.log).
Group AP_Watch
	ActorValue Property ActionPoints Auto Const
	{Vanilla (000002D5). Test 46's AP watch only: unfilled (an older ESP), there's none.}
	ActorValue Property ActionPointsRate Auto Const
	{Vanilla (000002D8).}
	ActorValue Property ActionPointsRateMult Auto Const
	{Vanilla (00000359).}
EndGroup

int Property TimerAPWatch = 46 AutoReadOnly
float Property APWatchTime = 120.0 AutoReadOnly
{Test 46: how long after getting off AP is logged every APWatchEvery seconds, whatever it is.
0 = no AP lines at all, as before test 46.}
float Property APWatchEvery = 2.0 AutoReadOnly
int Property APWatchQuiet = 10 AutoReadOnly
{Past APWatchTime, while AP is under its max: a line no different from the last one logged only
every this many polls (20 s).}

; Real seconds at getting off; one later than now is an earlier session's (kept in the save: the
; clock starts again with each launch) and counts as past APWatchTime.
float apWatchFrom = 0.0
string apWatchLast = ""   ; past APWatchTime, the last poll's line while AP was under its max
int apWatchSame = 0       ; polls since a line was logged, past APWatchTime

bool Function APWatchReady()
	return APWatchTime > 0.0 && ActionPoints && ActionPointsRate && ActionPointsRateMult
EndFunction

string Function SignedTenths(float afValue)
	if afValue < 0.0
		return "-" + Tenths(-afValue)
	endif
	return Tenths(afValue)
EndFunction

string Function APText(float afShare)
	return "AP: " + SignedTenths(PlayerRef.GetValue(ActionPoints)) + " of " + SignedTenths(PlayerRef.GetBaseValue(ActionPoints)) + " (" + Whole(afShare * 100.0) + "% of its max), rate " + SignedTenths(PlayerRef.GetValue(ActionPointsRate)) + " (base " + SignedTenths(PlayerRef.GetBaseValue(ActionPointsRate)) + "), mult " + SignedTenths(PlayerRef.GetValue(ActionPointsRateMult)) + " (base " + SignedTenths(PlayerRef.GetBaseValue(ActionPointsRateMult)) + "), sprinting " + Ternary(PlayerRef.IsSprinting(), "yes", "no")
EndFunction

; Getting on (the end of Mount): the line once; the poll stops (off the bike only).
Function APWatchRideStart()
	CancelTimer(TimerAPWatch)
	if APWatchReady()
		Log(APText(PlayerRef.GetValuePercentage(ActionPoints)) + "; getting on.")
	endif
EndFunction

; Getting off (FinishRide, every way off): the poll starts.
Function APWatchRideEnd()
	if APWatchReady()
		apWatchFrom = Utility.GetCurrentRealTime()
		apWatchLast = ""
		apWatchSame = 0
		StartTimer(APWatchEvery, TimerAPWatch)
	endif
EndFunction

Function APWatchPoll()
	if riding || !APWatchReady()
		return
	endif
	float now = Utility.GetCurrentRealTime()
	if apWatchFrom > now
		apWatchFrom = now - APWatchTime
	endif
	float since = now - apWatchFrom
	float share = PlayerRef.GetValuePercentage(ActionPoints)
	if since < APWatchTime
		Log(APText(share) + "; " + Whole(since) + " s after getting off.")
	elseif share < 0.995
		string text = APText(share)
		if text != apWatchLast || apWatchSame >= APWatchQuiet - 1
			Log(text + "; " + Whole(since) + " s after getting off, under its max.")
			apWatchSame = 0
		else
			apWatchSame += 1
		endif
		apWatchLast = text
	elseif apWatchLast != ""
		Log(APText(share) + "; " + Whole(since) + " s after getting off, back at its max.")
		apWatchLast = ""
		apWatchSame = 0
	endif
	if !riding
		StartTimer(APWatchEvery, TimerAPWatch)
	endif
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
		return 0.9
	endif
	float volume = CMB_EngineVolume.GetValue() / 100.0
	if volume < 0.0
		return 0.0
	elseif volume > 1.0
		return 1.0
	endif
	return volume
EndFunction

; Two loops play while riding: idle and cruise, crossfaded by speed each tick. Test 44
; (PluginDrivesSound): nine more join them and CMB_Slope.dll takes all eleven (OfferEngineLoops);
; when it doesn't, the crossfade plays as before. abOffer false: the two only, not offered (the
; plugin let go of the eleven mid-ride: UpdateEngineSound).
Function StartEngineLoops(bool abOffer = true)
	StopEngineLoops()
	if EngineVolume() <= 0.0
		return
	endif
	int set = engineSet
	if CMB_EngineIdleSound
		engineIdle = CMB_EngineIdleSound.Play(PlayerRef)
	endif
	if CMB_EngineCruiseSound
		engineCruise = CMB_EngineCruiseSound.Play(PlayerRef)
	endif
	UpdateEngineSound(0.0)
	if !PluginDrivesSound
		return
	elseif !riding
		; Test 44: the ride ended while the two were starting, and its stop may have come before
		; their ids did: stopped now, not left playing on.
		StopEngineLoops()
	elseif abOffer && engineSet == set
		OfferEngineLoops(set)
	endif
EndFunction

; Test 44: the nine more loops, each at no volume at once (the plugin brings each in at its own
; level), the eleven ids to the CMB_SndLoop globals in order and the generation last (the plugin
; reads them all once it's new); then the plugin's answer in CMB_SndDriven, waited for
; SoundAnswerWait. Run from the TimerEngine event or the load's OnGameReloaded, outside busy, so the
; waits hold up nothing; a ride end meanwhile (FinishRide's stop, which counts engineSet up) ends
; it. aiSet: engineSet when the two loops were started.
Function OfferEngineLoops(int aiSet)
	if !SoundGlobalsThere()
		Log("Engine sound: the script's crossfade (the ESP has no CMB_Snd globals or the nine loops for the plugin).")
		return
	endif
	int[] ids = new int[11]
	ids[0] = engineIdle
	ids[CruiseLoop] = engineCruise
	engineLoops = ids
	int i = 1
	while i < EngineLoopCount
		if i != CruiseLoop
			int id = LoopSound(i).Play(PlayerRef)
			; Kept at once, so a stop from here on finds it.
			ids[i] = id
			if id > 0
				Sound.SetInstanceVolume(id, 0.0)
			endif
			if engineSet != aiSet
				; A ride end (or a newer start) came between the plays: its stop may have missed the
				; latest. Stopped here; the two as well if the ride is over.
				StopExtraLoops(ids)
				if !riding
					StopEngineLoops()
				endif
				return
			endif
		endif
		i += 1
	endwhile
	; Each id goes to a float: whole numbers under 2^24 are exact. A play that failed (0) or a
	; larger id can't be handed over.
	i = 0
	while i < EngineLoopCount
		if ids[i] <= 0 || ids[i] >= MaxSoundId
			int bad = ids[i]
			; Dropped before the log line, whose call lets a stop run: then engineLoops is no longer ours.
			DropExtraLoops()
			Log("Engine sound: the script's crossfade (loop " + (i + 1) + ", " + LoopName(i) + ", has the instance id " + bad + ": " + Ternary(bad <= 0, "it didn't play", "too large for a global") + ").")
			return
		endif
		i += 1
	endwhile
	int gen = NextSoundGen()
	; Before the writes, so a stop between them withdraws what they wrote.
	offeredGen = gen
	i = 0
	while i < EngineLoopCount
		LoopGlobal(i).SetValue(ids[i] as float)
		if engineSet != aiSet
			return   ; that stop has withdrawn the set
		endif
		i += 1
	endwhile
	CMB_SndGen.SetValue(gen as float)
	; Counted polls, not summed waits (as RoomAt): ten 0.05s don't add up to 0.5 exactly in a float.
	int polls = (SoundAnswerWait / SoundPollInterval + 0.5) as int
	int poll = 0
	while poll < polls
		Utility.Wait(SoundPollInterval)
		poll += 1
		float answer = CMB_SndDriven.GetValue()
		; Looked at after both calls, with none between this and what's done below.
		if engineSet != aiSet
			; A ride end or a newer start: its stop has taken the loops back and withdrawn the set.
			return
		endif
		if answer == (gen as float)
			; Claimed before the call below, which lets a ride tick run: its UpdateEngineSound
			; mustn't crossfade the idle and cruise loops from here on. Test 46: nor is their volume
			; put on them: the plugin's SetVolume carries the MCM's engine volume in each level (the
			; value SetInstanceVolume sets, which would undo the level), read every frame.
			soundDriven = true
			drivenGen = gen
			Log("Engine sound: the plugin drives the " + EngineLoopCount + " loops (generation " + gen + ", answered in poll " + poll + ", " + Tenths(Utility.GetCurrentRealTime() - mountedAt) + " s after " + mountedHow + "), the engine volume in their levels.")
			return
		elseif answer == -(gen as float)
			DropExtraLoops()
			Log("Engine sound: the script's crossfade (the plugin declined generation " + gen + ": see its log).")
			return
		endif
	endwhile
	DropExtraLoops()
	; The literal, not the float: Papyrus prints 0.500000 (SoundAnswerWait).
	Log("Engine sound: the script's crossfade (the plugin didn't answer in 0.5 s, generation " + gen + ").")
EndFunction

; Test 44: the handed-over set falls back to the crossfade: the nine more loops stopped, the idle
; and cruise ones kept, and the set withdrawn from the globals.
Function DropExtraLoops()
	; Taken and withdrawn before any call that lets another thread run: both are still this set's.
	int[] ids = engineLoops
	engineLoops = None
	WithdrawLoops()
	if ids
		StopExtraLoops(ids)
	endif
EndFunction

; The nine besides the idle's (0) and the cruise's: those two are engineIdle and engineCruise.
Function StopExtraLoops(int[] akIds)
	int i = 1
	while i < akIds.Length
		if i != CruiseLoop && akIds[i] > 0
			Sound.StopInstance(akIds[i])
		endif
		i += 1
	endwhile
EndFunction

; Test 44: the globals cleared and a new generation with no loops in it, so the plugin lets go of
; the last set (CMB_SndDriven 0) and makes no call on those ids again. Only when they hold one.
Function WithdrawLoops()
	if offeredGen == 0 || !SoundGlobalsThere()
		return
	endif
	; Cleared before the writes (calls that let another thread run): withdrawn once.
	offeredGen = 0
	int i = 0
	while i < EngineLoopCount
		LoopGlobal(i).SetValue(0.0)
		i += 1
	endwhile
	CMB_SndGen.SetValue(NextSoundGen() as float)
EndFunction

; A number not used before, as RoomAt's asks are: the global's (a save's, after a load) or the last
; one written, whichever is larger, plus one. Well within a float's whole numbers; a wrap at a million
; is never seen (two or three a ride).
int Function NextSoundGen()
	int n = CMB_SndGen.GetValue() as int
	if n < sndGen
		n = sndGen
	endif
	n += 1
	if n > 1000000
		n = 1
	endif
	sndGen = n
	return n
EndFunction

; Test 44: the ESP's globals and loops for the plugin (an ESP from before test 44 has none).
bool Function SoundGlobalsThere()
	if !CMB_SndGen || !CMB_SndDriven
		return false
	endif
	int i = 0
	while i < EngineLoopCount
		if !LoopGlobal(i) || !LoopSound(i)
			return false
		endif
		i += 1
	endwhile
	return true
EndFunction

; The loops in the order of the CMB_SndLoop globals and the plugin's [Sound] Loops line.
Sound Function LoopSound(int aiLoop)
	if aiLoop == 0
		return CMB_EngineIdleSound
	elseif aiLoop == 1
		return CMB_EngineOn1400Sound
	elseif aiLoop == 2
		return CMB_EngineOn1700Sound
	elseif aiLoop == 3
		return CMB_EngineCruiseSound
	elseif aiLoop == 4
		return CMB_EngineOn2400Sound
	elseif aiLoop == 5
		return CMB_EngineOn2800Sound
	elseif aiLoop == 6
		return CMB_EngineOn3300Sound
	elseif aiLoop == 7
		return CMB_EngineOff1400Sound
	elseif aiLoop == 8
		return CMB_EngineOff1800Sound
	elseif aiLoop == 9
		return CMB_EngineOff2300Sound
	elseif aiLoop == 10
		return CMB_EngineOff2800Sound
	endif
	return None
EndFunction

GlobalVariable Function LoopGlobal(int aiLoop)
	if aiLoop == 0
		return CMB_SndLoop01
	elseif aiLoop == 1
		return CMB_SndLoop02
	elseif aiLoop == 2
		return CMB_SndLoop03
	elseif aiLoop == 3
		return CMB_SndLoop04
	elseif aiLoop == 4
		return CMB_SndLoop05
	elseif aiLoop == 5
		return CMB_SndLoop06
	elseif aiLoop == 6
		return CMB_SndLoop07
	elseif aiLoop == 7
		return CMB_SndLoop08
	elseif aiLoop == 8
		return CMB_SndLoop09
	elseif aiLoop == 9
		return CMB_SndLoop10
	elseif aiLoop == 10
		return CMB_SndLoop11
	endif
	return None
EndFunction

string Function LoopName(int aiLoop)
	if aiLoop == 0
		return "Idle"
	elseif aiLoop <= 6
		return "On" + LoopRpm(aiLoop)
	endif
	return "Off" + LoopRpm(aiLoop)
EndFunction

int Function LoopRpm(int aiLoop)
	if aiLoop == 0
		return 860
	elseif aiLoop == 1 || aiLoop == 7
		return 1400
	elseif aiLoop == 2
		return 1700
	elseif aiLoop == 3
		return 2000
	elseif aiLoop == 4
		return 2400
	elseif aiLoop == 5 || aiLoop == 10
		return 2800
	elseif aiLoop == 6
		return 3300
	elseif aiLoop == 8
		return 1800
	endif
	return 2300
EndFunction

; Every loop it started stopped, and their ids forgotten. Test 44: the set handed to the plugin
; withdrawn first (so it lets go before the ids die), and the nine more stopped too.
Function StopEngineLoops()
	engineSet += 1
	soundDriven = false
	int[] ids = engineLoops
	engineLoops = None
	WithdrawLoops()
	if engineIdle > 0
		Sound.StopInstance(engineIdle)
	endif
	if engineCruise > 0
		Sound.StopInstance(engineCruise)
	endif
	engineIdle = 0
	engineCruise = 0
	if ids
		StopExtraLoops(ids)
	endif
EndFunction

Function UpdateEngineSound(float afStepDistance)
	if soundDriven
		; Test 44: the plugin pitches and levels the eleven; since test 46 the MCM's volume too (it
		; reads CMB_EngineVolume every frame), so nothing here touches them. A plugin that has let go
		; of them (CMB_SndDriven no longer the generation: its log says why) left its last pitch and
		; level on each, so the two the crossfade plays are started afresh, the others stopped.
		float driven = CMB_SndDriven.GetValue()
		if !soundDriven
			; A stop came during the call (a ride end, or a newer start): nothing here is ours now.
			return
		elseif driven != (drivenGen as float)
			Log("Engine sound: the plugin let go of generation " + drivenGen + " (CMB_SndDriven reads " + Whole(driven) + "): the script's crossfade, its two loops started afresh.")
			StartEngineLoops(false)
		endif
		return
	elseif engineLoops
		; Test 46: a set being offered (OfferEngineLoops, till its answer): the plugin may already be
		; bringing them in by SetVolume from the levels StartEngineLoops left (the idle at the engine
		; volume, the cruise silent), which a crossfade here would undo. Declined or unanswered, the
		; set is dropped (engineLoops None) and the crossfade goes on from the next tick.
		return
	endif
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


; ---------------------------------------------------------------------------
; 2026-11-01a: the bike's own sounds besides the engine (test 47: "sound when jumping off of a ledge
; or anything else, currently the sound used is default character jump effect, another sound would
; be when bike is crossing a water"). The game's own sounds, by reference (the Bike_Effects group's
; lists; docs/ASSETS.md's borrowed list). Off values, each the 2026-10-31a build: CMB_FxMuteRider 0,
; CMB_FxLandOn 0, CMB_FxWaterOn 0, CMB_FxVolume 0.
; ---------------------------------------------------------------------------
string Property LandCueEvent = "JumpDown" AutoReadOnly
{The landing clips' own event (the shoes' landing sound's footstep tag): every landing clip but the
female soft running one.}
string Property LandSyncEvent = "SyncRight" AutoReadOnly
{The female soft running landing has only its sync markers at its start: a landing cue while the
plugin says a flight has just ended (CMB_FxAir 2).}
string Property LandSyncEvent2 = "SyncLeft" AutoReadOnly
{The same landing's next sync marker (0.133 s): the fallback should a trigger at exactly 0.0 not fire.}
float Property FxCueWait = 0.05 AutoReadOnly
{A sync cue while the plugin still says "in the air": its landing frame may come just after the
clip's first event.}
float Property FxLandDefault = 0.5 AutoReadOnly
{The landing's level without the plugin's (CMB_FxLandLevel -1: no plugin, or its [Fx] Land=0).}
float Property FxLandFloorDb = -18.0 AutoReadOnly
{The level of a landing at level 0+, in dB under full; full at 1.}
float Property FxLandHeavy = 0.45 AutoReadOnly
{From this level the heavy tyre thump (slot 1) instead of the light one (slot 0)...}
float Property FxLandBig = 0.6 AutoReadOnly
{...and from this one the clunk on top (slot 2, FxClunkDb under), or the heavy splash into water (4).}
float Property FxClunkDb = -4.0 AutoReadOnly
float Property FxAnswerWait = 0.5 AutoReadOnly
{The plugin's answer to the water loop (CMB_FxDriven) is waited for this long, polled every
SoundPollInterval, as the engine loops' is.}
float Property FxAuditionLoop = 3.0 AutoReadOnly
{FxAudition plays a water loop this long.}
bool fxMuted = false
bool fxCueBusy = false
bool fxCueEventsOn = false
int fxSeqSeen = -1
int fxWaterLoop = 0
int fxWaterSet = 0   ; counted up by each stop: a start that finds it changed was overtaken by a ride end

float Function FxVolume()
	if !CMB_FxVolume
		return 0.0
	endif
	float v = CMB_FxVolume.GetValue() / 100.0
	if v < 0.0
		return 0.0
	elseif v > 1.0
		return 1.0
	endif
	return v
EndFunction

; 2026-11-02a (test 48: the landing and water sounds played and went unheard): our own sound records over
; the game's files (Fx_Own_Records), MCM "Bike sounds through the mod's own records". Off, or an ESP
; without them: the game's own records (the borrowed lists), as the 2026-11-01a build. Read at each
; landing, and for the water loop on getting on.
bool Function FxOwn()
	return CMB_FxOwnSounds && CMB_FxOwnSounds.GetValue() != 0.0
EndFunction

; aiKind 0 the landing set, 1 the second set, 2 the water loops; abOwn our records or the game's.
; None for one the ESP hasn't.
FormList Function FxList(int aiKind, bool abOwn)
	if abOwn
		if aiKind == 0
			return CMB_FxLandSoundsOwn
		elseif aiKind == 1
			return CMB_FxLandSoundsAltOwn
		endif
		return CMB_FxWaterLoopsOwn
	elseif aiKind == 0
		return CMB_FxLandSounds
	elseif aiKind == 1
		return CMB_FxLandSoundsAlt
	endif
	return CMB_FxWaterLoops
EndFunction

; The set a landing plays from: ours unless CMB_FxOwnSounds is 0 or the ESP has none; CMB_FxLandPick
; 1 the second set (the game's second set, or the first, as before, when there's no own one).
; 2026-11-06a: the landings without metal first (FxDull: the MCM's "Landing sounds without metal").
FormList Function FxLandSet()
	if FxDull()
		return CMB_FxLandSoundsDull
	endif
	int kind = 0
	if CMB_FxLandPick && CMB_FxLandPick.GetValue() == 1.0
		kind = 1
	endif
	FormList set = None
	if FxOwn()
		set = FxList(kind, true)
	endif
	if !set
		set = FxList(kind, false)
	endif
	if !set
		set = CMB_FxLandSounds
	endif
	return set
EndFunction

; 2026-11-06a (test 49: big landings "like an empty barrel or a microwave", the car-metal clunk on top):
; MCM "Landing sounds without metal" (CMB_FxLandDull 1, the default): CMB_FxLandSoundsDull, a tyre thump,
; on big drops the power-armour dirt thud FxThudDb() under the heavy tyre; into water a splash, on big
; drops a heavy one with the power-armour water thud under it. 0, or an ESP without the three: the
; 2026-11-02a build's sets (CMB_FxLandPick picks). Read at each landing.
bool Function FxDull()
	return CMB_FxLandDull && CMB_FxLandSoundsDull && CMB_FxLandDull.GetValue() != 0.0
EndFunction

; Console CMB_FxThudDb: the dull set's thud this many dB under the landing's volume (-11: its loudest 50 ms
; 1 dB over the 2026-11-02a clunk's at -4, over in 0.2 s where the clunk rang 0.63 s; -12 the clunk's
; exactly), -40 to 0. Read at each landing.
float Function FxThudDb()
	if !CMB_FxThudDb
		return -11.0
	endif
	float d = CMB_FxThudDb.GetValue()
	if d > 0.0
		return 0.0
	elseif d < -40.0
		return -40.0
	endif
	return d
EndFunction

; MCM "Landing loudness range (dB)": the softest landing this many dB under the hardest, 0-60 (10;
; the 2026-11-01a build's 18, FxLandFloorDb, without the global).
float Function FxLandRange()
	if !CMB_FxLandRange
		return -FxLandFloorDb
	endif
	float r = CMB_FxLandRange.GetValue()
	if r < 0.0
		return 0.0
	elseif r > 60.0
		return 60.0
	endif
	return r
EndFunction

; On getting on and after a load into a ride. The water loop starts from the engine's start timer,
; after StartEngineLoops (its wait outside busy), and after the load's StartEngineLoops.
Function FxStartRide()
	fxCueBusy = false   ; a save made while a cue waited would keep it set
	FxMuteRider()
	FxWatchCues()
EndFunction

; Every way a ride ends (FinishRide: the emergency reset passes it too).
Function FxEndRide()
	FxUnmuteRider()
	if fxCueEventsOn
		fxCueEventsOn = false
		UnregisterForAnimationEvent(PlayerRef, LandCueEvent)
		UnregisterForAnimationEvent(PlayerRef, LandSyncEvent)
		UnregisterForAnimationEvent(PlayerRef, LandSyncEvent2)
	endif
	FxStopWaterLoop()
	; The plugin's last level is this ride's: back to the ESP's -1 (no cue), so a later game without the plugin plays
	; FxLandDefault, as the MCM says; the plugin writes its own again at the next ride's start.
	if CMB_FxLandLevel
		CMB_FxLandLevel.SetValue(-1.0)
	endif
EndFunction

; CMB_FxMuteRider (MCM "Mute the rider's own jump and landing sounds"): the game's category of the
; player's own footsteps, AudioCategoryFSTplayer, muted while riding.
Function FxMuteRider()
	if !AudioCategoryFSTplayer || !CMB_FxMuteRider
		return
	endif
	; A load may or may not keep a category's mute, and a Mute may count rather than set: cleared
	; first, so it is never on twice.
	AudioCategoryFSTplayer.UnMute()
	fxMuted = false
	if CMB_FxMuteRider.GetValue() != 0.0
		AudioCategoryFSTplayer.Mute()
		fxMuted = true
		Log("Bike sounds: the rider's own footstep sounds muted while riding (AudioCategoryFSTplayer).")
	endif
EndFunction

Function FxUnmuteRider()
	if fxMuted && AudioCategoryFSTplayer
		fxMuted = false
		AudioCategoryFSTplayer.UnMute()
		Log("Bike sounds: the rider's own footstep sounds back.")
	endif
EndFunction

; The landing cues (CMB_FxLandOn: switched on, watched from the next ride tick; switched off, each
; cue reads it, LandingCue). Fails while the player's 3D isn't loaded; the ride tick tries again (as
; WatchFootsteps).
Function FxWatchCues()
	if !riding || fxCueEventsOn || !CMB_FxLandOn || CMB_FxLandOn.GetValue() == 0.0 || !CMB_FxLandSounds
		return
	endif
	bool a = RegisterForAnimationEvent(PlayerRef, LandCueEvent)
	bool b = RegisterForAnimationEvent(PlayerRef, LandSyncEvent)
	bool c = RegisterForAnimationEvent(PlayerRef, LandSyncEvent2)
	fxCueEventsOn = a && b && c
	if !riding && fxCueEventsOn
		; The ride ended meanwhile: FxEndRide may have looked before this.
		fxCueEventsOn = false
		UnregisterForAnimationEvent(PlayerRef, LandCueEvent)
		UnregisterForAnimationEvent(PlayerRef, LandSyncEvent)
		UnregisterForAnimationEvent(PlayerRef, LandSyncEvent2)
	endif
EndFunction

; From OnAnimationEvent, before its footstep watch. The plugin's flight state (CMB_FxAir: 1 in the
; air past its AirMin, 2 just landed) and its flights' number (CMB_FxLandSeq) say whether a cue is a
; landing, and which; fxCueBusy, claimed before any call, makes two cues of one clip play once.
; CMB_FxLandOn is read once it is claimed: switched off mid-ride, the cues stay watched and play nothing.
;   JumpDown: a landing clip: played unless that flight's sound was played already (its SyncRight).
;   SyncRight/SyncLeft: only right after a flight not yet played: in the air still, waited for once
;   (FxCueWait); played once the plugin says landed.
; No plugin: CMB_FxAir stays 0 and the level -1, so a JumpDown plays at FxLandDefault, a sync marker
; never.
Function LandingCue(string asEventName)
	if fxCueBusy || !riding
		return
	endif
	fxCueBusy = true
	if !CMB_FxLandOn || CMB_FxLandOn.GetValue() == 0.0
		fxCueBusy = false
		return
	endif
	float air = 0.0
	int seq = 0
	if CMB_FxAir && CMB_FxLandSeq
		air = CMB_FxAir.GetValue()
		seq = CMB_FxLandSeq.GetValue() as int
	endif
	bool play = false
	if asEventName == LandCueEvent
		play = !(air > 0.0 && seq == fxSeqSeen)
	elseif air > 0.0 && seq != fxSeqSeen
		if air < 1.5
			Utility.Wait(FxCueWait)
			air = CMB_FxAir.GetValue()
			seq = CMB_FxLandSeq.GetValue() as int
		endif
		play = air > 1.5 && seq != fxSeqSeen
	endif
	if play && riding
		fxSeqSeen = seq
		float level = -1.0
		if CMB_FxLandLevel
			level = CMB_FxLandLevel.GetValue()
		endif
		if level < 0.0
			level = FxLandDefault
		endif
		int played = PlayLanding(level, asEventName)
		if CMB_FxLandPlayed
			; 2026-11-02a: minus the flight's number for a level-0 cue (nothing played; the plugin's line
			; says "silent by the script (level 0)", where test 48's 7 such cues read "played").
			if played == 0
				CMB_FxLandPlayed.SetValue(-(seq as float))
			else
				CMB_FxLandPlayed.SetValue(seq as float)
			endif
		endif
	endif
	fxCueBusy = false
EndFunction

; afLevel 0-1 from the fall's speed, 2-3 into water. The volume: the bike effects volume x
; 10^(-range x (1 - level) / 20), the range the MCM's (FxLandRange: 10 dB; 18 = FxLandFloorDb, the
; 2026-11-01a build); the light thump under FxLandHeavy, the heavy one from it, and the clunk on top
; from FxLandBig; into water the splash, or the heavy one from FxLandBig. Through our own records
; or the game's (FxLandSet). 2026-11-06a, the set without metal (FxDull): from FxLandBig the thud
; (slot 2; into water slot 5 under the heavy splash) FxThudDb() under, no clunk. Returns 1 when it
; played, 0 at level 0 (nothing to play: the silent cue), -1 for nothing played otherwise (the bike
; effects volume 0).
int Function PlayLanding(float afLevel, string asCue)
	float fx = FxVolume()
	bool water = afLevel >= 2.0
	float level = afLevel
	if water
		level -= 2.0
	endif
	if level > 1.0
		level = 1.0
	endif
	if level <= 0.0
		return 0
	elseif fx <= 0.0
		return -1
	endif
	FormList set = FxLandSet()
	bool dull = set && set == CMB_FxLandSoundsDull
	bool own = set && (set == CMB_FxLandSoundsOwn || set == CMB_FxLandSoundsAltOwn || dull)
	float range = FxLandRange()
	float volume = fx * Math.Pow(10.0, -range * (1.0 - level) / 20.0)
	int first = 0
	if water
		first = 3
		if level >= FxLandBig
			first = 4
		endif
	elseif level >= FxLandHeavy
		first = 1
	endif
	int id = FxPlay(set.GetAt(first) as Sound, volume)
	int extra = 0
	float extraDb = FxClunkDb
	int extraSlot = 2
	if dull
		if level >= FxLandBig
			if water
				extraSlot = 5
			endif
			extraDb = FxThudDb()
			extra = FxPlay(set.GetAt(extraSlot) as Sound, volume * Math.Pow(10.0, extraDb / 20.0))
		endif
	elseif !water && level >= FxLandBig
		extra = FxPlay(set.GetAt(2) as Sound, volume * Math.Pow(10.0, FxClunkDb / 20.0))
	endif
	int r = (range + 0.5) as int
	string article = Ternary(r == 8 || r == 11 || r == 18, "an ", "a ")
	string extraText = ""
	if extra > 0
		extraText = Ternary(dull, ", the thud " + extra + " (" + Whole(extraDb) + " dB)", ", the clunk " + extra)
	endif
	Log("Bike sounds: landing (" + asCue + ") at level " + Hundredths(level) + Ternary(water, " into water", "") + " (" + Ternary(own, "our records", "the game's records") + Ternary(dull, ", no metal", "") + ", " + article + r + " dB range): sound " + first + " instance " + id + extraText + ", volume " + Thousandths(volume) + ".")
	return 1
EndFunction

int Function FxPlay(Sound akSound, float afVolume)
	if !akSound
		return 0
	endif
	int id = akSound.Play(PlayerRef)
	if id > 0
		Sound.SetInstanceVolume(id, afVolume)
	endif
	return id
EndFunction

; 2026-11-06a: MCM "Water sound loop" (CMB_FxWaterLoop, read on getting on) picks it: 1 the churn (our
; record, CMB_FxWaterLoopsOwn's slot 3), 2 the mod's own wet road (CMB_FxWaterRoad); 0, another value,
; a record the ESP hasn't or no global: as the 2026-11-02a build (CMB_FxWaterPick's from the set).
; 2026-11-09a (test 50: the wet road heard as static): 3 the gentle wet road (CMB_FxWaterRoadSoft, the
; MCM's "Wet road, gentle", the default); 3 without that record (None) plays 2's wet road.
; The water loop (CMB_FxWaterOn, CMB_FxWaterPick, read on getting on): played at no volume, its id
; to the plugin (CMB_FxWaterId), which brings it in by the water's depth over the feet and the speed
; (as the engine's loops) and answers in CMB_FxDriven: the id, or minus it when it declines. No
; answer in FxAnswerWait: stopped (it needs CMB_Slope.dll). From the engine's start timer and the
; load's setup, outside busy.
Function FxStartWaterLoop()
	FxStopWaterLoop()
	if !riding || !CMB_FxWaterOn || CMB_FxWaterOn.GetValue() == 0.0 || !CMB_FxWaterLoops || !CMB_FxWaterId || !CMB_FxDriven || FxVolume() <= 0.0
		return
	endif
	int set = fxWaterSet
	; 2026-11-02a: our own loops over the game's files unless CMB_FxOwnSounds is 0 or the ESP has none
	FormList loops = CMB_FxWaterLoops
	if FxOwn() && CMB_FxWaterLoopsOwn
		loops = CMB_FxWaterLoopsOwn
	endif
	string records = Ternary(loops == CMB_FxWaterLoopsOwn, " (our records)", " (the game's records)")
	int pick = 0
	if CMB_FxWaterPick
		pick = CMB_FxWaterPick.GetValue() as int
	endif
	if pick < 0 || pick >= loops.GetSize()
		pick = 0
	endif
	Sound loop = None
	string what = " " + pick + records
	int kind = 0
	if CMB_FxWaterLoop
		kind = CMB_FxWaterLoop.GetValue() as int
	endif
	if kind == 1 && CMB_FxWaterLoopsOwn && CMB_FxWaterLoopsOwn.GetSize() > 3
		loop = CMB_FxWaterLoopsOwn.GetAt(3) as Sound
		what = ": the churn (CMB_FxWaterLoop 1)"
	elseif kind == 2 && CMB_FxWaterRoad
		loop = CMB_FxWaterRoad
		what = ": the wet road (CMB_FxWaterLoop 2)"
	elseif kind == 3 && CMB_FxWaterRoadSoft
		loop = CMB_FxWaterRoadSoft
		what = ": the gentle wet road (CMB_FxWaterLoop 3)"
	elseif kind == 3 && CMB_FxWaterRoad
		loop = CMB_FxWaterRoad
		what = ": the wet road (CMB_FxWaterLoop 3, no gentle record: 2's)"
	endif
	if !loop
		loop = loops.GetAt(pick) as Sound
		what = " " + pick + records
	endif
	if !loop
		return
	endif
	int id = loop.Play(PlayerRef)
	if fxWaterSet != set || !riding
		; A ride end came during the play: its stop missed this one.
		if id > 0
			Sound.StopInstance(id)
		endif
		return
	endif
	if id <= 0 || id >= MaxSoundId
		if id > 0
			Sound.StopInstance(id)
		endif
		Log("Bike sounds: the water loop" + what + " didn't play (instance " + id + ").")
		return
	endif
	Sound.SetInstanceVolume(id, 0.0)
	fxWaterLoop = id
	CMB_FxWaterId.SetValue(id as float)
	int polls = (FxAnswerWait / SoundPollInterval + 0.5) as int
	int poll = 0
	while poll < polls && fxWaterLoop == id
		Utility.Wait(SoundPollInterval)
		poll += 1
		float answer = CMB_FxDriven.GetValue()
		if fxWaterLoop != id
			return   ; a ride end (or a newer start) has stopped it
		elseif answer == (id as float)
			Log("Bike sounds: the plugin drives the water loop" + what + " (instance " + id + ", poll " + poll + ").")
			return
		elseif answer == -(id as float)
			Log("Bike sounds: the plugin declined the water loop (see its log): stopped.")
			FxStopWaterLoop()
			return
		endif
	endwhile
	if fxWaterLoop == id
		Log("Bike sounds: no answer from the plugin in 0.5 s: the water loop stopped (it needs CMB_Slope.dll).")
		FxStopWaterLoop()
	endif
EndFunction

Function FxStopWaterLoop()
	fxWaterSet += 1
	int id = fxWaterLoop
	fxWaterLoop = 0
	if CMB_FxWaterId && CMB_FxWaterId.GetValue() != 0.0
		CMB_FxWaterId.SetValue(0.0)
	endif
	; The plugin's answer to that loop goes with it: instance ids can repeat after a load, and a new loop with the
	; save's id must not read the save's answer as its own (FxStartWaterLoop's poll, FxWaterTick).
	if CMB_FxDriven && CMB_FxDriven.GetValue() != 0.0
		CMB_FxDriven.SetValue(0.0)
	endif
	if id > 0
		Sound.StopInstance(id)
	endif
EndFunction

; Each ride tick: a water loop the plugin let go of after its answer (CMB_FxDriven minus the id: 30 of its calls
; refused in a row, so it can't set the loop's level any more) is stopped, as one declined at the start is.
Function FxWaterTick()
	if fxWaterLoop > 0 && CMB_FxDriven && CMB_FxDriven.GetValue() == -(fxWaterLoop as float)
		Log("Bike sounds: the plugin let go of the water loop (instance " + fxWaterLoop + ", see its log): stopped.")
		FxStopWaterLoop()
	endif
EndFunction

; 2026-11-02a (test 48: every audition was typed with the console open, and the console pauses the
; game: all of them played into the pause, none was heard).
float Property FxAuditionDelay = 0.5 AutoReadOnly
{An audition plays this long after the menus close (Utility.Wait's timer doesn't run in menu mode).}
float Property FxAuditionGap = 2.5 AutoReadOnly
{Auditions typed together play this far apart, in the order typed; so do the sounds of -1 and -2.}
int fxAuditionQueued = 0   ; the slots auditions waiting or playing hold: the next one typed takes the slot after them

; Console: cqf CMB_ControllerQuest FxAudition N, then close the console: it plays FxAuditionDelay s after
; the menus close, those typed together FxAuditionGap s apart in the order typed. 0-4 the landing set,
; 10-14 the second set, 20-23 the water loops (FxAuditionLoop s each), through our own records; the
; same plus 100 (100-104, 110-114, 120-123) through the game's own records, the 2026-11-01a build's.
; -1: every one of ours in turn (14, about 47 s), -2: every one of the game's; each holds the queue's
; slots for its whole sequence, so one typed with it starts after it. At the bike effects volume (100
; if it's 0). Instance 0: it didn't play (a file that didn't resolve, a condition, or not a sound).
; 2026-11-06a, -3: the landings as heard (PlayLanding, the set in use: FxLandSet), small to big at
; levels 0.1, 0.3, 0.5, 0.7 and 1.0 onto the ground, then 0.3 and 1.0 into water, FxAuditionGap s
; apart (about 15 s), each logged as "landing (audition)", at the bike effects volume and the MCM's range.
Function FxAudition(int aiWhich)
	int slots = 1
	if aiWhich == -1 || aiWhich == -2
		slots = ((14.0 * FxAuditionGap + 4.0 * FxAuditionLoop) / FxAuditionGap) as int + 1   ; 19: its 47 s in gaps, rounded up
	elseif aiWhich == -3
		slots = 7
	endif
	int slot = fxAuditionQueued   ; claimed before any call (a call lets another audition's thread run): the order kept
	fxAuditionQueued += slots
	bool menu = Utility.IsInMenuMode()
	float wait = FxAuditionDelay + slot * FxAuditionGap
	if menu
		Log("Bike sounds: audition " + aiWhich + ": waiting for the menus to close (the console pauses the game); it plays " + Hundredths(wait) + " s after.")
	endif
	Utility.Wait(wait)
	if slots == 1
		fxAuditionQueued -= 1
	endif
	if aiWhich == -1 || aiWhich == -2
		int kind = 0
		while kind < 3
			int n = 5
			if kind == 2
				n = 4
			endif
			int i = 0
			while i < n
				FxAuditionOne(kind, i, aiWhich == -1, menu)
				Utility.Wait(FxAuditionGap)
				i += 1
			endwhile
			kind += 1
		endwhile
		fxAuditionQueued -= slots   ; the sequence over: its slots given back
		return
	endif
	if aiWhich == -3
		FxAuditionLandings(menu)
		fxAuditionQueued -= slots
		return
	endif
	int code = aiWhich % 100
	int set = code / 10
	int slotIn = code % 10
	if aiWhich < 0 || aiWhich >= 200 || set > 2 || slotIn > 4 || (set == 2 && slotIn > 3)
		Log("Bike sounds: audition " + aiWhich + ": no such sound (0-4, 10-14, 20-23 ours; 100 more the game's; -1 all of ours, -2 all of the game's; -3 the landings as heard).")
		return
	endif
	FxAuditionOne(set, slotIn, aiWhich < 100, menu)
EndFunction

; FxAudition -3 (2026-11-06a): seven landings through PlayLanding, FxAuditionGap s apart, as a ride hears them.
Function FxAuditionLandings(bool abAfterMenu)
	Log("Bike sounds: audition -3: the landings as heard (" + Ternary(FxDull(), "without metal", "the 2026-11-02a build's sets") + "), levels 0.1, 0.3, 0.5, 0.7, 1.0, then 0.3 and 1.0 into water" + Ternary(abAfterMenu, ", after the menus closed", "") + ".")
	int i = 0
	while i < 7
		float level = 0.1 + 0.2 * i
		if i == 4
			level = 1.0
		elseif i == 5
			level = 2.3
		elseif i == 6
			level = 3.0
		endif
		if PlayLanding(level, "audition") < 0
			Log("Bike sounds: audition -3: the bike effects volume is 0: nothing played.")
			return
		endif
		if i < 6
			Utility.Wait(FxAuditionGap)
		endif
		i += 1
	endwhile
EndFunction

; One audition: our record or the game's for that list's slot, at the bike effects volume (100 if it's
; 0), its line, a water loop stopped after FxAuditionLoop s.
Function FxAuditionOne(int aiKind, int aiSlot, bool abOwn, bool abAfterMenu)
	float fx = FxVolume()
	if fx <= 0.0
		fx = 1.0
	endif
	FormList list = FxList(aiKind, abOwn)
	Sound s = None
	if list && aiSlot < list.GetSize()
		s = list.GetAt(aiSlot) as Sound
	endif
	int id = FxPlay(s, fx)
	int code = aiKind * 10 + aiSlot
	if !abOwn
		code += 100
	endif
	Log("Bike sounds: audition " + code + " (" + Ternary(abOwn, "our record", "the game's record") + ", " + FxSlotName(aiKind, aiSlot) + "): " + s + " instance " + id + ", volume " + Thousandths(fx) + Ternary(abAfterMenu, ", after the menus closed", "") + ".")
	if id > 0 && aiKind == 2
		Utility.Wait(FxAuditionLoop)
		Sound.StopInstance(id)
	endif
EndFunction

; The slots' names for the audition lines (the lists' order).
string Function FxSlotName(int aiKind, int aiSlot)
	if aiKind == 2
		if aiSlot == 0
			return "spray"
		elseif aiSlot == 1
			return "large spray"
		elseif aiSlot == 2
			return "wet road"   ; 2026-11-06a: 0x8A9 CMB_FxWaterRoadLPSD, the mod's own loop (the stream's file wasn't in the game)
		endif
		return "churn"
	elseif aiSlot == 0
		return "light tyre"
	elseif aiKind == 1
		if aiSlot == 1
			return "heavy thud"
		elseif aiSlot == 2
			return "barrel clunk"
		elseif aiSlot == 3
			return "medium splash"
		endif
		return "heavy water thud"
	elseif aiSlot == 1
		return "heavy tyre"
	elseif aiSlot == 2
		return "clunk"
	elseif aiSlot == 3
		return "splash"
	endif
	return "heavy splash"
EndFunction

; A value of 0 or more to two decimals ("0.47"), to three ("0.298"): Papyrus prints six.
string Function Hundredths(float afValue)
	int n = (afValue * 100.0 + 0.5) as int
	if n < 0
		n = 0
	endif
	return (n / 100) + "." + Ternary(n % 100 < 10, "0", "") + (n % 100)
EndFunction

string Function Thousandths(float afValue)
	int n = (afValue * 1000.0 + 0.5) as int
	if n < 0
		n = 0
	endif
	int f = n % 1000
	return (n / 1000) + "." + Ternary(f < 100, Ternary(f < 10, "00", "0"), "") + f
EndFunction
