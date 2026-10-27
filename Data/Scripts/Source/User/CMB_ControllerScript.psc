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
	{Engine volume, 0-100. Default 70.}
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
far as MaxSettleDistance, as in test 44's build.}
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
float spotPitch
float spotRoll
bool spotTiltKnown = false
; Test 46: the last RollBikeUp found no spot and brought nothing (a call refused: the plugin's
; [Room] LineFallback=0).
bool rollRefused = false
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
		StartTimer(TickInterval, TimerTick)
		; Sounds don't survive a load, and their old instance numbers mean nothing now.
		engineIdle = 0
		engineCruise = 0
		; Test 44: nor the plugin's eleven, nor its hold on them. The CMB_Snd globals still hold the
		; save's set (offeredGen says so): StartEngineLoops' stop withdraws it before the new one.
		engineLoops = None
		soundDriven = false
		StartEngineLoops()
	elseif bikeAtDoor
		; The bike waits at a door: the way out is watched for (as riding's is, put back here).
		RegisterForPlayerTeleport()
	endif
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
		; Test 20: with the Harley's long front the wheel went into rock faces at 15; 20 keeps it
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
	if riding || busy
		Log("Getting on ignored: " + Ternary(riding, "riding already.", "busy (" + BusyText() + ")."))
		return
	endif
	; Claim the lock before calling anything on other objects: those calls let
	; other threads (hotkey, timer, activation) run in between.
	busy = true
	NoteBusy("getting on")
	string blocker = GetMountBlocker()
	if blocker != ""
		busy = false
		Debug.Notification(blocker)
		Log("Getting on refused: " + blocker)
		return
	endif
	EnsureArrays()

	Game.FadeOutGame(true, true, 0.0, 0.25, true)
	; The plugin moves the camera within a tenth of a second: the wait covers it.
	SetCameraLive(true)
	Utility.Wait(0.3)

	if CMB_ForceThirdPerson.GetValue() > 0.0
		if CMB_CameraLive && CMB_CameraLive.GetValue() > 0.0
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
	lastOutdoorTime = Utility.GetCurrentGameTime()
	combatHinted = false
	ForgetDoor()
	RegisterForPlayerTeleport()
	healthMark = PlayerRef.GetValuePercentage(Health)
	hitGrace = true
	StartTimer(HitGraceTime, TimerHitGrace)
	WatchForHits()
	poseRetries = 0
	poseRetryWaiting = false
	WatchFootsteps()
	SetSlopeLive(true)
	SetTiltLive(true)
	CallRam("StartRide")
	PlaceHeadlamp()
	SetHeadlampLive(true)
	; Whatever is there is old (or from a game with the plugin): it writes them again at once.
	if CMB_GroundNormalZ
		CMB_GroundNormalZ.SetValue(0.0)
	endif
	if CMB_ParkUpZ
		CMB_ParkUpZ.SetValue(0.0)
	endif
	StartTimer(TickInterval, TimerTick)
	PlaySound(CMB_EngineStartSound)
	StartTimer(EngineStartLength, TimerEngine)
	Log("Mounted. SpeedMult +" + playerSpeedDelta + ", stowed " + stowedFollowers.Length + ", running " + boostedFollowers.Length)

	Game.FadeOutGame(false, true, 0.0, 0.35)
	busy = false
	if FuelEnabled()
		Debug.Notification("Fuel: " + CountFuel())
	endif
	APWatchRideStart()   ; test 46: AP once at getting on (after the fade: its reads take a few frames)
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
	RollBikeUp()
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
; where it was if it was shown, false.
bool Function RollBikeUp(bool abFromDoor = false)
	rollRefused = false
	bool wasShown = !BikeRef.IsDisabled()
	; Disabled before the asks: standing where it waited, the bike would be in its own way at a
	; spot over it (a disabled reference has no collision).
	BikeRef.Disable()
	int spot = PickBikeSpot(abFromDoor)
	if spot == -2
		rollRefused = true
		if wasShown
			BikeRef.Enable(false)
		endif
		return false
	elseif spot < 0
		; Where it waited: the shadow move put it there at the rider's height, and LeaveBikeOutside
		; only showed it. Shown again, and settled on the ground there like any park.
		BikeRef.Enable(false)
		SettleBike()
	else
		; At the place the spot was checked at (spotX/Y/Angle), not where the player is by now: a
		; player running out of a gate has moved a good way in the asks' half seconds, and the spot
		; with room was the one asked about.
		if spotKnown
			BikeRef.MoveTo(PlayerRef, spotX - PlayerRef.GetPositionX(), spotY - PlayerRef.GetPositionY(), 0.0, false)
			BikeRef.SetAngle(0.0, 0.0, spotAngle + ParkedModelYaw)
		else
			PlaceBike(SpotForward(spot), SpotRight(spot))
		endif
		BikeRef.Enable(true)
		; Test 44: the snap measured against the checked spot (SpotSettleMax).
		SettleBike(false, spotKnown && spotGroundKnown)
	endif
	bikeWaitsForShore = false
	ForgetDoor()
	return spot >= 0
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
; spot was past the fence or inside the house). Every try is logged, and the choice.
int Function PickBikeSpot(bool abFromDoor)
	spotKnown = false
	spotGroundKnown = false
	spotTiltKnown = false
	if !CheckBikeSpot
		return 0
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
	int spots = BikeSpots
	int spot = 0
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
			Log("The bike's spot: " + (spot + 1) + " (" + SpotText(spot) + "), heading " + Whole(spotAngle) + moved + ".")
			return spot
		elseif room < 0 && CallTakesBestSpot && !abFromDoor && lastRoomClear > 0.0 && lastRoomClear <= 200.0 && lastRoomClear > bestClear
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
		elseif room == 0
			if abFromDoor && spot > 0
				Log("The bike's spot: where it waited (spot " + (spot + 1) + " not checked, the earlier ones without room).")
				return -1
			endif
			Log("The bike's spot: 1 (" + SpotText(0) + "), not checked, as before test 41.")
			return 0
		endif
		spot += 1
		if spot == BikeSpots && RoomOption(1)
			; Test 46 (the plugin's [Room] Around): beside and behind the player too.
			spots = BikeSpots + AroundSpots
		endif
	endwhile
	if abFromDoor
		Log("The bike's spot: where it waited (none of the " + spots + " has room).")
		return -1
	endif
	if bestSpot >= 0
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

; Test 46: a bit of CMB_RoomOptions, the plugin's [Room] keys for this script (1 Around, 2 a call
; with no spot refused); false without the global or the plugin (0: test 45's build).
bool Function RoomOption(int aiBit)
	if !CMB_RoomOptions
		return false
	endif
	int options = CMB_RoomOptions.GetValue() as int
	return (options / aiBit) % 2 == 1
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
; Roll, lastRoomTilted; -1000 none: its ParkTilt off, or an older plugin or ESP).
int Function RoomAt(float afX, float afY, float afZ, int aiSpot, float afAngle, string asUnchecked = ".")
	string try = "Bike's spot " + (aiSpot + 1) + " (" + SpotText(aiSpot) + "): "
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

; Test 46: the ground's tilt under the wheels at the spot just answered (the plugin's [Room]
; ParkTilt: CMB_RoomPitch over -1000) into lastRoomPitch/Roll/Ground and lastRoomTilted, and its
; words for the spot's line ("" without).
string Function RoomTiltRead()
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
	elseif aiTimerID == TimerTeleport
		CheckTeleport()
	elseif aiTimerID == TimerBusyWatch
		BusyWatchFired()
	elseif aiTimerID == TimerAPWatch
		APWatchPoll()
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
	UnregisterForHitEvent(PlayerRef)
	UnregisterForAnimationEvent(PlayerRef, FootstepEvent)
	footstepsWatched = false

	RemoveBikeArmor()
	CallGearRestore("RestoreSlot")
	SetCameraLive(false)
	SetSlopeLive(false)
	SetTiltLive(false)
	CallRam("EndRide")
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
		BikeRef.Enable()
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
	BikeRef.Enable()
	if abAtDoor && world
		bikeAtDoor = true
		doorWorld = world
		Log("The bike waits outside the door, in " + world + ".")
	endif
	return false
EndFunction

Function ParkBesidePlayer()
	if ParkOnTrack()
		return
	endif
	PlaceBike(0.0, ParkSideOffset)
	BikeRef.Enable()
	SettleBike(true)
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
	BikeRef.Enable()
	TiltParkedBike(CMB_ParkAngle.GetValue(), "the track just ridden")
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
		; Test 41: read right after the equip, the slot said nothing twice (16:00:13, 16:01:37) while
		; the bike showed: the biped hadn't taken the armor yet. Read a tick later (RideTick).
		wornSlotToLog = true
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
	BikeRef.Enable(true)
	SettleBike()
	ForgetDoor()
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
			Log("Engine sound: the plugin drives the " + EngineLoopCount + " loops (generation " + gen + ", answered in poll " + poll + "), the engine volume in their levels.")
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
