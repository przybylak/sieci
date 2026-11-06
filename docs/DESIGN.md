# Design notes

## The core problem

Fallout 4 has no player-driven vehicles. Skyrim's horse riding isn't usable in Fallout 4 as-is:
there's no `ActorTypeHorse`, no rider animations, and modders report that mount prompts fail
with "You cannot do that right now". The engine *does* still carry mount/vehicle plumbing,
because Vertibird rides use it, and several existing mods build on that (see the README).

## Approaches considered

| Approach | How | Why not (for now) |
|---|---|---|
| **A. Worn bike + speed (chosen)** | Player "wears" the bike as armor; SpeedMult boost; input layer blocks jump/sprint/combat | Not real physics, and the game has no riding animations, so the mod generates its own seated clips. But every piece is a documented, stable Papyrus API, so it's the most likely to work first time |
| B. Mount system (Vertibird plumbing) | Make the bike an actor with race mount data, ride it like a creature | Needs reverse-engineering what the existing mount mods did. Known side effects (face bug on dismount, companion issues). Good candidate for a v2 |
| C. Power-armor framework | Bike is a power-armor-like furniture you enter | Inherits power armor's camera, HUD and fusion-core mechanics, and the mesh would need to be a PA-style skinned set |
| D. Furniture + `SetVehicle` | Player sits in a furniture marker attached to a moving bike actor | Steering the vehicle actor from player input isn't possible in vanilla Papyrus |
| E. Moving a reference every frame | Script repositions a bike reference under the player | Papyrus can't update every frame; `TranslateTo` lags and jitters |

## How approach A works

```
          ┌──────── parked ────────┐                    ┌──────── riding ─────────┐
 Keys / Activate ─► CMB_BikeRef (Activator)   Mount ►   CMB_BikeRef disabled, shadows player
                    enabled in the world               Player wears CMB_BikeRiderArmor
                                                       SpeedMult × CMB_SpeedPercent
                                                       InputEnableLayer: no jump/sprint/sneak(/combat)
                                                       Companions boosted (mode 0, default) or hidden (mode 1)
                                                       Flamer Fuel burned per distance ridden
                                                       FallingDamageMod + CMB_FallDamageCut
                                              ◄ Dismount / interior or walled town / power armor / furniture /
                                                deep water / an enemy's hit (optional)
```

- **Keys:** handed out the first time the player is outdoors with a Pip-Boy, so a new game's pre-war intro and Vault 111 are left alone. The player keeps two keys, so using one never empties the stack (an empty stack would lose its favorites hotkey).
- **Where it can't go:** interiors (every dungeon and sewer is one), and since test 39 the enclosed places the game builds as outdoor worldspaces of their own: Diamond City (DiamondCityFX and DiamondCity), Goodneighbor, the pre-war Sanctuary of the intro, Far Harbor's memory simulation (DLC03VRWorldspace) and Nuka-World's market and amphitheater (`InClosedWorld`, the forms looked up by file from Mutagen's FormKeys, a DLC not installed skipped, worked out again only when the worldspace changes). The open worlds (the Commonwealth, Far Harbor's island, Nuka-World's park) and other mods' worldspaces stay open. In all of those, and in power armor, getting on and calling the bike are refused. Riding in through a load door ("You leave the motorbike parked outside.") leaves the bike at the last outdoor spot it shadowed, marked since test 40 as waiting at that door, with its worldspace (kept in the save; a load watches for the way out again). When the player is next outdoors in an open worldspace, the one it waits in, within `DoorBringDistance` of it (6000 units, about 85 m, a cell and a half: the same door, or another of the same building or town), on the teleport out or on the next use of the keys or the hotkey, it is brought where calling puts it (220 ahead, 60 to the right, settled on the ground; since test 41 the first of seven spots with room, below), quietly: no engine sound and no message, only the Papyrus log's "Bike brought from the door it waited at, N units away."; brought by the keys or the hotkey, their next use gets on. Test 39: ridden up Diamond City's stairwell to the gate, the bike was left where the ride's tick had last put it, 110 units to the rider's right at their height and not settled, inside or behind the wall, and coming out the tester found no bike in front of the gate or in the square. Test 41: brought three times from that door, 191 to 452 units away, the bike stood in the gate's chain-link fence and gate each time: the spot was fixed, 220 ahead and 60 to the right of the player, with no look at what was there, and outside Diamond City's door that spot is the fenced gate. So since test 41 the spot is checked for room first (`CheckBikeSpot`, a script constant, a developer's switch: false gives the fixed spot back): `RollBikeUp`, which a call goes through too, disables the bike (standing where it waited it would be in its own way at a spot over it) and tries seven spots in order (`BikeSpots`, each at the player's height: 220 ahead and 60 right, the old spot, so nothing changes where it has room; 220 ahead and 60 left; 150 ahead and 60 right or left, nearer, a gate's fence running across the way; 300 ahead and 60 right or left, past a narrow spot; 100 straight ahead, as close as the bike stands without being under the player's nose), asking `CMB_Slope.dll` about each through the CMB_Room globals (the section *The brought bike's spot* below: the plugin's rays, answered within a frame or two, the script polling every 0.05 s for 0.5 s; since test 43 with the player's heading too, `CMB_RoomAskAngle`, so the plugin checks a bike-shaped box along it) and takes the first with room, every try logged ("Bike's spot N (220 ahead, 60 right): room (the ground N below)." or "none (the nearest hit N along a ray, on the bike's 110, or the ground N off)." or "none (no ground within 100 of the spot)." or, since test 43, "none (the ground N above the spot).": the plugin writes -2 and -1 as exact floats, and the script took everything under -1.5 for "not checked" before, so a spot under a rise ended the asking, then "The bike's spot: N (…), heading A."). A first spot answered "not checked (the plugin's rays aren't working here)" (right after a load, before the plugin's test ray passes) is asked about once more since test 43 (`RetryUncheckedSpot`, a script constant: false gives test 42's way back), `RoomRaysWait` (1.5 s, about three times the 0.49 s the test ray came after the plugin's first frame with the player in test 42) later and from where the player is by then, the plugin casting its test ray again for that ask (`[Room] RaysRetry`): "…: not checked (the plugin's rays aren't working here): asked again in 1.5 s."; not checked twice, a bring leaves the bike where it waited ("The bike's spot: where it waited (spot 1 not checked twice: the plugin's rays aren't working here).") and a call takes the first spot untested; a "not checked" at a later spot counts as no answer, as before. With room at none of the seven a bike brought from a door is left where it waited, shown again and settled on the ground there (it was never settled: the shadow move put it there at the rider's height): "The bike's spot: where it waited (none of the 7 has room)." and "The bike is left where it waited, N units away: no spot with room found (the spot lines above say why)." in place of "Bike brought"; the rider parked it there, so it's always acceptable, and the bring counts as done, the mark cleared, so calling it works; a call, with nowhere to fall back to, takes the spot with the most room since test 43 (`CallTakesBestSpot`, a script constant: false gives the first spot as before; outside Diamond City's gate the first is the fence): the largest `CMB_RoomClear` among the spots refused for a hit along a ray, 200 at most (a share of the plugin's `Fore`, which the INI allows up to 200), or for the ground 61 to 100 below, which `SettleBike` puts the bike on ("The bike's spot: N (…), heading A, the most room of the 7 (the nearest hit K along a ray, on the bike's 110, or the ground K below; none has room, a call takes the most room)."), and the first spot only when none was refused that way. Since test 46, with the plugin's `[Room] Around` (which it tells the script through `CMB_RoomOptions`), four more spots are asked after the seven, beside and behind the player (`AroundSpots`: test 45's fences, walls and rubble were all in front, where the seven are), and with its `LineFallback=0` a call with none of the eleven to take is refused, the bike left where it was ("There's no room for your motorbike here."), where test 45's calls 1, 6 and 8 took the first spot, past a fence, inside a house, beyond rubble (*The brought bike's spot* below). No answer in 0.5 s (no plugin, which the script has no other way to see, so that costs one wait a call or a bring; or an ESP from before test 41, whose properties for the globals are None: "not checked (the ESP has no CMB_Room globals)") ends the asking: the first spot untested, as before test 41, unless this is a bring and an earlier spot was already refused, when where it waited is the surer place ("The bike's spot: where it waited (spot N not checked, the earlier ones without room)."). A bike that came in with the player, kept hidden there, has no outside spot to wait at and takes a call's way. Farther off it stays where it is, still marked ("Out N units from the door the bike waits at: it stays there."), and calling it works. Out of the same door the player often lands within reach of the spot it was left at, and that is the spot in the wall, so it's brought then too; walked back to it, the keys and the hotkey get on (they try the bike beside the player first), which clears the mark. The bike's own worldspace is checked as well: one that a late tick put in the town with the player isn't brought, a distance across worldspaces meaning nothing ("The bike marked at a door in ... is in ...: not brought, calling it brings it."). Getting on, calling the bike, its return after a swim and the emergency reset outdoors clear the mark. A fast travel in says "Your motorbike stays where you set off." instead and leaves the bike where the fast travel set off, unmarked; calling it works (test 39: a fast travel from Sanctuary into Diamond City said it was parked outside, while it stayed at Sanctuary). The tick that finds the player inside tells the two apart by the game time since the last tick that found them outdoors: more than `FastTravelMinutes` (5 game minutes) is a fast travel, less a door (a tick is a second, 20 game seconds at the game's timescale of 20, and a fast travel takes game hours; the log: "Gone in N game minutes after the last tick outdoors: a fast travel." or "a door.", once since test 41: the tick logged it before `DismountGoingIn` claimed `busy`, and at test 41's 15:57:50 and 15:59:19 the 1 s tick and the teleport handling's own tick both got there, one outcome but two lines; `DismountGoingIn` logs it past the claim now); a fast travel of under 5 game minutes counts as a door, which is harmless, the bike being near. The time is set on getting on and kept in the save (a save from before it was kept starts it at the load). The ride's tick also looks again right before it moves the bike to the player (test 39's stairwell: a tick that had found the player outdoors could run on past the door), and should one put the bike in beside them anyway, the bike stays hidden and calling it outdoors brings it. Since test 41 a teleport is decided once it's over, not in `OnPlayerTeleport`: test 40 found the event comes while the player is still where the teleport started, and they're moved seconds later, during the loading screen, so the way out of Diamond City still saw the town and brought no bike (three times), the way in still saw the gate and brought it there, and a fast travel's ride tick put the bike beside the player after the move ("left hidden"). The event only notes it, with where the player is ("Teleport seen (t …): the player in …"; a second one before the first is handled keeps the first reading). The controller watches the loading screen for good (`RegisterForMenuOpenCloseEvent` on `LoadingMenu`, in OnInit and at every load) and decides when it closes with the player in a cell, or, with none seen, when a look every half second (`TeleportCheckInterval`) finds the player moved: into another worldspace, in or out of doors, or over 1500 units from where the event saw them (`TeleportMoved`: riding covers at most about 900 between two looks); with no loading screen and no move after 3 looks (1.5 s: a script's MoveTo is over within a frame or two), and after 120 looks (60 s: a close that never came) whatever else ("Teleport handled (how, N s after it): the player in …"). Meanwhile the ride's tick waits ("Ride tick skipped: a teleport is pending") and does nothing while the player is in no cell, which `IsInInterior` and `InClosedWorld` would read as outdoors; once decided, riding, the tick runs at once with the timer's own stopped around it (test 40's 15:31:35 had two ticks at once, one putting the bike back on while the other ended the ride), and on foot the keys are handed out if still to come and the bike waiting at a door is brought. A save loaded with the bike waiting at a door, or with a teleport pending, is looked at the same way at once (test 40: the exit autosave, loaded, brought the bike within a second, the save having the player outside already); a loading screen open in the save is forgotten. A bike a late tick put in beside the player anyway is kept hidden and brought, wherever it is, the next time they're outdoors in the open worldspace of the last tick outdoors. Every refusal to bring it is logged with its reason ("Bike not brought from the door (who): reason."; test 40's were silent). `cqf CMB_ControllerQuest DecideTeleportsAtOnce 1` decides in the event again, with test 40's tick, door and load rules, for an A/B; it's kept in the save, and every load's "Switches:" line says which way both of test 41's switches are set.
- **Parked bike:** a persistent Activator reference. It lives in a holding cell until first called, then wherever you leave it.
- **While riding:** the parked reference is disabled and moved next to the player every second. If you go indoors, the bike is re-enabled where you last were outside (and, through a door, brought to you when you come out near it: above).
- **Deep water:** the controller gives the player a hidden ability, `CMB_SwimWatchAbility`, whose effect has the condition `IsSwimming == 1`, so it starts when the player starts swimming and ends when they stop (`CMB_SwimWatchEffectScript` reports both). Swimming ends the ride with "The motorbike can't go into deep water." The bike stays hidden until you're out of the water altogether: a second effect on the same ability, with `IsInWater == 1` (any depth, wading too), reports that. Three seconds after you're on dry land the bike rolls up 200 units past you, on the side away from where you stopped swimming, which is the land side (indoors it waits until you're outside; if the in-water report never ends, it comes after 30 s anyway). Crossing a river can end the ride several times; that's by design. Leaving it where it last followed you didn't work: after riding off a ledge into a lake, that spot was in mid-air, and Papyrus can't tell whether the player is on the ground. Getting on and calling the bike are refused while swimming. Paddling-depth water isn't swimming, so it stays rideable. The ability is added on every load (adding it again does nothing).
- **Falls:** `FallingDamageMod` (the actor value the Acrobat's legendary effect raises: percent less fall damage) goes up by `CMB_FallDamageCut` (default 75) while riding, and exactly that comes off again. A no-fall-damage perk (`crNoFallDamage`) would be all or nothing, so the actor value it is. On top of that, small falls are free: the controller registers for the player's `OnPlayerFallLongDistance` event (as a remote event) and, while riding, logs every fall's damage and gives it straight back (`RestoreValue`, a moment after it lands) when it's under `CMB_FreeFallDamage` percent of max health (default 20). Ordinary drops cost nothing; a cliff still hurts. The Vault 111 cliff took about 42% with the 75% cut. Landings use the seated jump clips.
- **Knocking enemies over (F4SE plugin):** since test 41, hostile actors the bike hits at speed are knocked over and take a little damage, the bike losing some speed at each; the section *Knocking enemies over* below has the protocol.
- **Fights:** with `CMB_DismountOnHit` (default 1) the controller registers for hit events on the player (one-shot, re-registered after each). A big hit from an actor hostile to the player ends the ride and parks the bike beside them: a power attack, an explosion, or at least `CMB_KnockOffDamage` percent of max health (default 10) lost since the last tick, so a quick run of small hits adds up. Health is read as a fraction of the maximum (`GetValuePercentage`), a moment after the hit lands. Hits in the first 3 seconds after getting on never count. A bloatfly's sting doesn't knock you off; a raider's shotgun blast at close range does. Otherwise, the first tick of a fight (`IsInCombat`) with weapons off shows a hint once: use the keys to get off.
- **Speed:** `ModValue(SpeedMult, delta)` with the exact delta remembered and removed later, so other speed effects stay intact. A ±0.1 carry-weight nudge forces the engine to apply the new speed (a known SpeedMult quirk).
- **Companions:** mode 0 (default) gives them the same speed boost and moves them up behind you if they fall behind. Mode 1 (opt-in) disables them and parks them in the holding cell, then puts them back behind you on dismount. That's riskier: disabling a companion during their quest or a scene (Heather, Dogmeat, Sim Settlements 2 characters…) can break it. So companions in a scene or in power armor are never hidden or teleported, whatever the mode.
- **Fuel:** every tick, the horizontal distance since the last tick is added up (jumps over 5000 units are teleports and don't count). Every `CMB_FuelDistance` units (default 21000, about 300 m) one item from `CMB_FuelItems` is used, from the side bag first, then the player. The list holds Flamer Fuel by default. Running dry parks the bike where you stand; with no fuel you can't get on. Fast travel costs nothing, and Survival disables it anyway.
- **Worn bike slot:** biped slot 57. Whatever else is worn in that slot comes off while riding. With F4SE, `CMB_GearRestoreF4SE` reads it first (`GetWornItem`) and re-equips it after the ride; vanilla Papyrus can't read what's in a slot, so without F4SE it stays in the inventory. 58 clashed with Eli's Armour Compendium bags, and 60 is the slot named "Pipboy", so 57 it is.
- **Side bag:** a container in the holding cell, opened remotely with `Activate`. Capacity is checked in `OnItemAdded`. F4SE's `Form.GetWeight()` is called *by name* (`CallFunction`), so F4SE stays optional; without it the cap counts items via `GetItemCount(None)`.
- **Save/load:** a player alias forwards `OnPlayerLoadGame`, and the controller re-applies the input layer, speed refresh and timer; a `busy` the save held is let go, and logged with its holder. With F4SE, since test 41 the plugin starts an in-game load as a cold one does (test 40: after a load on the bike at 15:23:42 the bars turned and the wheels spun, but the bike stood upright through the turns and the rider sat up, until he got off and on; at a cold load nothing is held at `PostLoadGame`, at an in-game load the old holds went on into the loaded 3D, the arms' chains with them): at `PostLoadGame` (or `NewGame`) everything held is let go of and held afresh at the first sync, after one line of what was held, the three globals before and after, the tilt and the lean, the ground and the rays, the torso's lean and where the player and the 3D root were ("load: a save loaded (PostLoadGame); before it riding …"); the first tick says whether the ride resumed. The rider's world check keeps only a yes since then, a no tried again every sync and given up after 3 s. 2.5 s into a ride a load started (past the latest re-attach of the head's shapes after a load, 1.57 s of wall time in tests 35 to 39, and the riding pose put back 1.0 s after it) a line says what is held and written ("load: 2.5 s into the ride after the load: …: resumed", or "not resumed:" and why), and what didn't resume is let go and held afresh once, as getting off and on does: the bike's skins when one was refused or their bone can't be read (the refusals forgotten), the rider when nothing of it is held or its chains or lean were given up, with the latches that kept it from being held (the block, the world check, the skeleton wait); never the tilt (no `ResetTilt`: the suspension, the lean's filter and the ride's start stay as they are). At 6 s the line again, for the log alone. The one state of the plugin that gives test 40's picture is `CMB_TiltLive` at 0 with the slope or the camera on: the tilt is off, so the bike is kept level and the rider let go while the moving parts run (the harness's mode 9 shows it on test 40's DLL and this one alike; the filter held in the air leaves the bike level but the rider held and leaning, and the rider's latches leave the bike leaning 14 degrees). Nothing of the plugin's sets that global, so riding with it at 0 (or NaN) is logged, once a ride, after 2 s in a ride a load started and 5 s otherwise (getting on sets the camera about a second before the tilt), and again when it comes back ("tilt: riding with CMB_TiltLive at 0 for N s …"). Why it read 0 then isn't known: the script sets it only with the camera and the slope (Mount, OnGameReloaded's riding branch, FinishRide), and a save taken inside Mount's second would still finish Mount after the load. Since test 41 the script's ride tick also compares it with what it last wrote and puts it back ("CMB_TiltLive read X while riding, put back to Y." in the Papyrus log), so the plugin's line, which waits 2 s (5 s outside a load), then means the script's tick isn't running. The log of the session before is kept as `CMB_Slope_prev.log`, one generation, moved aside just before the new log is opened (test 40: the game was restarted after that load, and the log that would have said why was gone); the first line gives the date and says whether it was kept (or why not).
- **Threading:** Papyrus lets other threads into a script whenever it calls another object, so every entry point claims the `busy` flag *before* its first such call. Keys, hotkey, activation and the ride timer then can't interleave. Key delivery works the same way: `keysDelivered` is set before anything else is called (and cleared again if the player isn't outdoors with a Pip-Boy yet), so OnInit, a teleport and the retry timer arriving together can't hand the keys out twice. The ride tick can't claim `busy` (it would block the swim and hit handlers for its whole run), so it checks `riding && !busy` again before each step that changes something: a tick that carried on after the ride ended once put the bike back on after a swim. As a safety net, 1.5 s after every dismount both bike armors come off and head tracking goes back on if you aren't riding again. Since test 41 every claim notes who holds `busy` and since when, and a `busy` held over `BusyWatchTime` (10 s) is logged with its holder and let go ("Busy held N s (who): let go."; test 40: the keys used outside Diamond City left no line, and a `busy` left set would have turned them away in silence): one timer, restarted by every claim, watches the latest; a menu seen open starts the count again, since `Utility.Wait` doesn't run in menus and the holder can be waiting in one; getting on takes about a second, and the longest hold seen, bringing the bike with its navmesh probes while a loading screen was up, 4 s. `cqf CMB_ControllerQuest WatchBusy 0` turns it off. Every use of the keys, every hotkey press (the F4SE one or the MCM's, an ignored one too: in a menu, in a scene, before the keys are handed out) and every activation of the parked bike is logged with what it found (riding, busy and who holds it, the bike near or at a door, where the player is) and what it did, every refusal to get on, get off or call the bike with its reason and the message shown, and the keys' effect logs its own early returns (no controller set, used on someone other than the player).
- **Riding animations:** while riding, the player gets the animation flavour keyword `CMB_AnimFlavorRider` (`ChangeAnimFlavor`, cleared on dismount and re-applied after a load). `CMB_RiderPose.esp` adds an additive race whose subgraph entries are copies of every third-person holstered entry for the player (from `HumanRaceSubGraphData` and every additive race in the load order, the Unofficial Patch's crippled-limb ones included), each with that keyword added and `MT\CMB_Rider` searched first. The game picks the entry matching the most keywords, so each copy beats its original while the keyword is on. HumanRace isn't edited, so race mods (LooksMenu Customization Compendium and the like) don't conflict. The plugin and its AnimTextData are built on the player's PC from their load order, so the controller finds the plugin with `Game.IsPluginInstalled` and gets the keyword with `GetFormFromFile`. The clips copy the vanilla clip each one replaces (in the player's own folder order: Player, Confident, Neutral) for length, root motion and events, so the game's movement logic doesn't change. The worn bike leans with the rider in turns. Hit reactions and staggers are in the same MT entries (their 25 clips, `MT\Neutral\Hit*`, `Stagger*` and `Animations\HitChestBack`, are in every MT entry's AnimationFileData), so seated versions with those names would be picked up by the same copied entries; none ship yet. Details: [ASSETS.md](ASSETS.md).
- **Bike and rider stay together:** the player's movement graph (`MTBehavior.hkx`) has a `BSRootTwistModifier` whose `rootTwistAngle` is bound to the graph's `Direction` variable. When the character turns on the spot or faces someone in dialogue, it twists the body away from the root. A bike on `AnimObjectA`, a bone under the root on the ground, stays put while the rider turns on it, and the hands leave the grips. So the bike now hangs off `COM`, the bone the whole body hangs from, at the exact transform `COM` has in the seated clips (`CMB_RiderSeat.json`, per sex). In the clips it sits exactly where the `AnimObjectA` bike did (within the few millimetres of suspension bounce), and when the game twists the body, the bike turns with it. That only lines up with the seated pose, so the controller switches to the ground-planted `AnimObjectA` version (`CMB_BikeRiderArmorFrame`) without the rider pose, with a weapon drawn (standing poses) or with `CMB_BikeFollowsRider 0`. Head tracking (`bAllowHeadTracking`, on by default in the graph) twists the chest towards whoever you look at, so it's switched off while seated and back on afterwards.
- **Throttle (F4SE plugin):** the game's own speed is there at once and gone at once (test 21: 60 to 800 units a second
  in about a second on W, back to 60 in 0.75 s off it). The input hook shapes it: the speed, as a fraction of the top,
  builds up evenly over `Accel` (3 s) from a tenth on the forward key, rolls off over `Coast` (2 s) after it, and back
  brakes it off over `Brake` (0.4 s) before the reverse starts; a side key alone creeps only once it has rolled off. The
  game takes the speed from the input vector's length, and bends upward with it (test 22: 0.10 gave 90 of 930 units a
  second, 0.33 158, 0.66 464, 0.85 720), so the plugin writes the input that gives the speed it wants, from that curve
  inverted, and scales the whole vector in the keys' direction (a side key with forward had made it a unit long and the
  speed full at once). On its own clock: the input hooks run with the input, not once a frame (test 22: a third of the
  frames, so the frame time integrated there made every ramp three times as long). The throttle never runs more than
  `Lead` (0.2 of the top) ahead of the measured speed along the heading (test 23: from a stop the game's speed lagged it
  for a second and then surged to catch up; stuck on a hillside with W held it sat at 0.8 and would have lunged once
  free; since test 43 but for two holds, sliding along a face, `SlideHold`, and after a landing, `LandHold`: the *Tilt*
  bullet below), and back reverses only once that speed is under `BackBelow` (30 units a second): braked off and still
  rolling on, the game gets nothing (test 23: the reverse push started at 500 and left a roll back after the stop).
  Since the 2026-11-06a build a pull-away from rest has a curve of its own (test 49: "slow in the first second"): from
  rest (forward newly pressed under a tenth of the top) the throttle starts at `LaunchFrom` (0.25, an input of 0.44) and
  closes on the top as 1 - (1 - t) e^(-dt / `LaunchTau`) (1.5 s), never slower than 0.45 / `Accel` a second, while the
  `Lead` cap allows `LaunchLead` (0.45). Test 49's 30 launches showed the game giving about 110 u/s^2 under 80 u/s to
  inputs up to 0.5, which the even ramp from a tenth sat in for its first 0.8 s. A stall (under 20 a second on the
  0.05 s measure 0.6 s on: pinned on a kerb or a hillside, 0-10 there; an ordinary pull-away is at 40-60 by then on the
  0.2 s measure and about 60 on the 0.05 s one, so the first threshold, 60 on the 0.2 s measure, ended most of test 49's
  launches as stuck: the review's DR3; mode 23's ride 2b drives the game's curve, 110 u/s^2 under 80)
  ends it with the cap back to `Lead` at once (test 23's lunge guard), as a let-go or a brake does; at the top, or for
  something ahead, the allowance falls to `Lead` over 0.3 s. One line a launch: "launch: from rest: 0.3 of the top after
  0.37 s, half after 0.83 s, 0.9 after 2.84 s (the throttle from 0.25 closing on the top over 1.5 s, the cap's lead
  0.45: LaunchTau); the cap bound 0.00 s" (the harness's), or "launch: ended after 0.60 s: under 20 a second (stuck
  against something): the cap back to Lead". Re-accelerating at speed keeps the even ramp; `LaunchTau=0` is the
  2026-11-02a build. Since the 2026-11-01a build also a brake key (test 47's wish: "something like spacebar would be
  nice"; back brakes only once forward is let go, the game's move vector carrying one y): `[Steer] BrakeKey` (-1, the
  MCM's "Brake key" on its Hotkeys page, the global `CMB_BrakeKey`, 57 = Space in a new save and also with an ESP
  without it; or a DirectInput scan code, 256-260 the mouse buttons, the numpad's digits by their NumLock-on keys (the
  layout's `MapVirtualKeyA` gives the arrows for them); W, A, S and D refused; 0 none, the 2026-10-31a build), read on
  getting on (the MCM's value at each ride's start; its line again whenever the code read changes, a refused one too).
  `AfterInput` polls it with the move keys and holds it 0.1 s as it holds them; it is read by user32's
  `GetAsyncKeyState`, found by `GetProcAddress` on the first ride (the DLL imports nothing more), and only while the
  game has the foreground window (the harness exports its own `CMB_TestKeyState`, found the same way). Held, it beats a
  held forward and brakes as back does (the throttle off over `Brake`), and once braked off it gives the game (-0, -0)
  whatever its keys say: the bike holds still, forward held through it waits and pulls away from a tenth when it is let
  go, and there is no reverse or creep while it is held (back still backs up once it is let go). A move key kept over
  the game's (0, 0) reads (test 19's 0.2 s) within 0.35 s of the brake key isn't held: W, S or a side key let go with it
  neither pulls away, reverses nor starts a creep. The climb's and the slide's cut, the landing's hold, the brake rule
  (the brake light, the engine's braking) and the sound's inputs read it as they read back (the cut lines say "the brake
  key"). Space is free while riding: the game's only use of it is the jump, which `ApplyControls` turns off for the ride
  and on again after (README's "jumping ... blocked"); off the bike it jumps as always, and the plugin reads it only
  with the input hook active, never in a menu. Its line on getting on: "  steer: BrakeKey=-1: the MCM's CMB_BrakeKey 57,
  Space (VK 0x20): brakes as back does while rolling, holds the bike still once stopped (no reverse, no creep)"; a
  ride's first press: "steer: the brake key (Space) held at 903 u/s: braking".
- **U-turns:** vanilla's 180° reversals (`walk_to_walk_l180` etc.) brake to a stop, spin round and set off the other way. The riding versions keep vanilla's length, events, total turn and distance, but follow a leaning arc at an even pace, with the heading round by vanilla's `startAllowRotation` event, when the game's own steering takes over. The turn direction comes from each source clip's yaw (`MT\Neutral\walk_to_walk_l180` actually turns right).
- **Parked bike facing:** the vanilla motorcycle model points along −Y, so the parked bike is placed with a 180° yaw on top of the player's heading.
- **Engine sound:** a start sound, then looping sounds played on the player; a stop sound on dismount. The loops are restarted after a load, since sound instances don't survive one. Up to test 43 two loops (idle ~900 rpm, cruise ~2700 rpm) crossfaded every tick by the distance covered since the last one (`Sound.SetInstanceVolume`), synthesised (`tools/sound/make_engine_sounds.py`, a 45° V-twin firing pattern, nothing sampled). Since test 44's build, eleven loops made from a recording of a V-twin cruiser (demodave's, *The sound* below), which `CMB_Slope.dll` pitches and fades every frame from a gearbox model; without the plugin (or the Address Library) the same crossfade of two of them, the idle (860 rpm) and the cruise (2000): *Engine sound* below.
- **MCM:** `config.json`/`keybinds.json` bind the menu straight to the globals (`GlobalValue` sources), plus buttons and an MCM hotkey that call global functions on `CMB_MCMRelay` (`CallGlobalFunction`; they fetch the controller by form id: MCM's `CallFunction` on the quest picked another of its scripts, tests 30-31). The generator writes them, so their form IDs always match the plugin.
- **Hotkeys:** without F4SE, favorite the keys (an aid item) and use the favorites hotkey. With F4SE, `CMB_HotkeyF4SE` adds a real key. The controller finds it with `CastAs` by name, so the core scripts don't depend on F4SE.

## Engine limits to keep in mind

- **Speed ceiling:** the world streams in cells around you. Much past ~3× run speed, LOD pop-in and load stutter get bad, so the script clamps at 5×.
- **No physics:** no momentum, no ramps; the lean in turns is animation only. The "bike" moves exactly like a fast person: it climbs what a person can climb and is stopped by what stops a person.
- **Collision:** while riding, your collision is still a person-sized capsule.
- **Placement:** getting off, the bike is parked in this order (since test 47, with the plugin's `[Room] ParkCheck`, it is first put back where it stood when the ride moved the player less than a wheelbase and they don't stand there now, else the spot below is checked for room as a call's is: *The brought bike's spot* below):
  1. *(F4SE plugin)* **On the ground just ridden.** While riding, `CMB_Slope.dll` keeps a track of where the player's feet were on the ground (a point every 8 units; more than 0.4 s in the air, a jump of over 150 units, or a new ride starts it again). The bike's middle goes at the first place back along it that's 145 units from the player's feet in a straight line, so it never lands on them, even after a U-turn, and no steeper than 45° over the 40 units either side (each half, so not across the foot of a rock face; test 9 got off on a 60° face, and the bike now goes back down to where it could stand), nor leaning more than 20° across the bike (test 10: parked along a 60° side slope, the parked roll capped at 10° left one side in the air); it faces the way the track ran there and is pitched by it (the points 40 units either side along it), sits at the track's height, and rolls with the track's averaged ground normal there (with the part along the bike taken out). The plugin writes the spot into `CMB_ParkX/Y/Z`, `CMB_ParkAngle` and `CMB_ParkUpX/Y/Z` every 0.1 s while riding; `ParkUpZ` is 0 when there's no spot (a track shorter than that, the player not at its end) and the log says why on getting off. The script uses it only while riding, and clears it when the ride ends (an emergency reset after a ride parks beside you). Test 8: four parks on the track, all right, one on steep rock at 28° pitch; the two that fell back (a turn just before stopping, a track that came back to the player) were refusals the rule above no longer makes. The plugin also writes how steep the ground here is into `CMB_TrackSlope`, and getting off is refused above 45° ("Too steep to get off here."): nowhere you couldn't stand on foot (walking tops out at the controller's 47°; test 13, with the limit at 50°, let the player off on 47° and 49° faces). How steep: the track's own slope over the last 120 units, whichever way the rider faces, and once that's 20° or more, also the face's own from the averaged ground normal, whichever is more. Test 10 showed why both: the slope along the heading read 45° riding diagonally up a 60° face and nothing at all when turned sideways on it, so getting off was never refused; the normal alone reads steeper than 50° on about 3% of level riding (curbs), so it only counts on a slope. On getting off the plugin logs the spot it last wrote and how long before (test 9 logged a later recalculation instead).
  2. **Beside the player, on the navmesh:** to your right, snapped to the nearest navmesh, tilted by four probes (the persistent XMarker `CMB_GroundProbeRef`) snapped to the navmesh in front of, behind and to both sides of it. A probe pulled more than 50 units sideways means the navmesh is too coarse there, and then its height is no better either (test 8: half in the rock): the bike stays level at the player's height beside them.
  3. **No navmesh within 400 units:** the plane under the player's feet carried over to the bike's spot, but only if that moves it at most 30 units (`MaxGroundStep`) up or down; otherwise it stays level at the player's height. Test 7 showed why: the plane came from one contact normal, so 110 units away it put the bike 1 m above a rock bulge and sank it to the tank beside a curb. The plugin now publishes the normal averaged over the last 0.6 s on the ground (`CMB_GroundNormalX/Y/Z`, Z = 0 off the ground) rather than one frame's.

  The parked pitch is at most 45° (`ParkMaxPitch`, the same limit the plugin parks on: test 11 parked on a 45° track spot with the script stopping at 30°, one end in the air) and the roll at most 10° (`ParkMaxRoll`), each clamped on its own (scaling the normal down to the limit used to take pitch away whenever there was roll too); `CMB_MaxTilt` 0 parks it level. A reference's angles turn it by its heading last, after pitch (X) and roll (Y) in its own frame, clockwise the game's way (X > 0 tips its +Y end down), so pitch = atan(n·forward / n·up) and roll = −asin(n·right) with the normal turned into the bike's frame (test 7: five parks, pitch and roll the right way). Calling the bike or the roll-up after a swim use step 2 without the player's ground. Next to walls it can still clip; calling it again (keys → Call) re-places it.
- **Slopes (F4SE plugin):** how steep a slope you can walk up is a limit kept by the player's character controller and its Havok proxy; no INI or game setting holds it, and Papyrus can't reach it. `CMB_Slope.dll` (`tools/f4se-slope`, plain C, built with MinGW) does, for Fallout 4 1.11.240 with F4SE 0.7.9 only: the game addresses it uses (player, load order, `LookupFormByID`, INI settings) come from F4SE 0.7.9's own source for that runtime, and F4SE won't load it on any other version. F4SE calls it every frame on the main thread (a permanent task). It reads `CMB_SlopeLive` (the controller sets it to `CMB_MaxSlope`, default 45° since test 24 (60 climbed the hill by Vault 111; on foot the game allows 47), while you ride, and 0 otherwise) and finds the player's controller (`bhkCharProxyController`, in the process data at +0x3E0 in 1.11.240) and Havok proxy (`hknpBSCharacterProxy`, controller+0x470) by their C++ type information, checking every pointer before reading it. While riding it writes the limit at the place `CMB_Slope.ini` names, every frame, never below the game's own, and only if the value there is what the INI expects; the original goes back afterwards. Where it is: the first round (read only) found Havok's reflection data for `maxSlope` (radians in the construction info of both the proxy and the rigid-body character, 0x94 and 0x80) but no slope-like value in the live proxy's first 0x300 bytes, and `bhkCharProxyController+0x418` holding exactly cos 47°. The second round wrote there, guarded by that 47°, and logged what changed on getting on, during the ride and on getting off: in test 6 the limit went 47° → 60° and back on four rides, the game never set it back, and steeper climbs worked. A save loaded on the bike keeps the riding value in the controller (test 24: 60° on foot for the rest of the session), so a value equal to the one the plugin last wrote is taken as its own again and put back at the dismount. The 47° guard stays, against game updates. `Probe=1` in the INI still logs the layouts and the "what changed" diffs (`My Games\Fallout4\F4SE\CMB_Slope.log`); it's off by default now. `tools/f4se-slope/test` runs the DLL under Wine against a stand-in for the game: fake player, controller and proxy objects with MSVC-style type information at the real addresses, and a fake F4SE. Since test 41 a low face at the capsule raises the limit for a moment (test 40: off-road north of Red Rocket the bike stopped dead four times in three minutes at fallen trunks and stumps, 900 to near 0 in half a second, stuck 1 to 3 s; each time the controller's ground normal read 35 to 65 degrees, the trunk's side, while the wheels' rays read 5 to 20: the capsule, 18 units round at the bike's middle, meets the trunk between the wheels, the 47-degree limit makes that contact a wall, and the face rays, which start at half a wheel radius and need the axle-height one, saw nothing lower than about 30 there). Two rays from the capsule at 4 and 10 above the feet along the pitched axis (and two more lines 12 to either side once the bike is stalled) look for a face; when one is within the capsule's radius (+0x370, else 18) + 6 + a tenth of a second of the speed, isn't an actor (layers 30 and 8), has nothing `ClimbTop` above the feet within 45 past it (0: the wheel radius + 2, 31.9; a face that rises past that is a step taller than a wheel, or a slope that goes on), the face rays see no wall (nor, since test 43, a face alongside in the last half second, `CLIMB_ALONG`: test 42's boost put the capsule up the foot of a rail the bike was going along, 20:55:51, "climb: … a face alongside, N deg off the heading (…, the face rays' verdict)") and the wheels' line is pitched `ClimbMaxPitch` at most (22, test 41's answer: trunks and stumps only, not ledges on rocky slopes; the four stops read 5 to 20 under the wheels, test 40's rock pile 31 to 37 stays refused), the limit goes to `ClimbBoost` (85: a round log 30 across meets the capsule at acos(3/33) = 84.8 degrees, and the stuck readings are all under it) while forward is held, and back to the riding one `ClimbHold` (0.3 s) after the face was last seen. It's off at once on back, the creep, forward let go, something at `ClimbTop`, a wall, a face alongside, getting off and a load (a slot still holding the boost after a load is taken back as the plugin's while riding, or given the game's value back on foot), and given up after `ClimbMax` (1.5 s) stalled with it on, until the bike has moved 60 along its heading or forward is pressed again; it needs the limit to be the plugin's (with the MCM's slope at 0, none). When the 10 ray misses, a short ray down from 2 short of the 4 ray's hit tells a slope grazed (ground within 2 under it) from a face. Meanwhile the `Lead` cap's floor is `ClimbThrottle` (0.4 of the top) rather than 0.1 (stuck at a trunk, `Lead` held the throttle to 0.2, about 180 units a second of push, and how fast the capsule climbs goes with its push); the cap itself stays, against test 23's lunge. A sharp step (a stump's upright side, 17 to 32 high) meets the capsule's upright side, which no limit climbs (`ClimbStep`): with the boost on 0.25 s and the bike still under 40 units a second along its heading, three rays straight down at 3, 12 and 21 past the face find its top (the highest hit, over 4 above the feet and `ClimbTop` at most, not an actor), two rays up check there's room for the capsule (its height from +0x374, 128) over the top and over where it will stand, and the controller is put up by the top + 1.5 and 4 on through `GetPositionImpl` and `SetPositionImpl`, as the reverse moves it (test 39: those steps worked): only ever up, twice an obstacle at most (two more once the bike is 60 from the last step's place, at a ride's start or a load; pressing forward again restarts the boost, not the steps), 0.25 s apart, and a step the feet haven't half followed within 0.1 s is logged as not taken. The log's "climb:" lines, from a hand of 10 refilled one every 6 s, say each boost and its end ("a low face at the capsule …: the climb limit 47 -> 85", "over it", "cut", "off", "given up"), each step ("stepped up", "no step:" and why, "the step up didn't take"), the capsule's fields once a ride, and, stuck with forward held and nothing climbed, why not, once a stall; the settings' "  climb:" line says which are on. `Climb=0` gives the limit as before test 41 and `ClimbStep=0` the boost alone, both read again on getting on. Test 44: the capsule went up a wooden road barrier (22:47:39, `0000DD7E_Physics`) and a guard rail lying as the border of a brush pile (22:48:57, `GRailStrShort01`, "a low face at the capsule …: 27 ahead at 4, 27 at 10 (90 deg), nothing at 31.9 within 72 …: the climb limit 47 -> 85"), 25 to 30 high, under the wheel radius + 2, and the bike sat astride it, the wheels in the air either side ("bike shouldn't be able to get on them - it just gets stuck halfway through"). So since test 45 (`ClimbMaxTop`, 18) a face with something 18 above the feet within 45 past it, judged while the boost is off and only when nothing is at `ClimbTop`, is climbed only if it is round, narrow or a step up (`ClimbBeam`; test 45's review, keeping test 42's "trunks, stumps ok"): round if it recedes toward its foot, the ray at 4 meeting it further on than the one at 10 (the face over 100 degrees: 117 to 123 for a log 25 to 30 across lying on the ground; an upright rail reads 90); narrow if a ray at 18 two capsule radii (36) to either side of the line, from as far back and reaching three times that past the face, passes it (a stump; a rail met up to about 58 degrees off square still meets both); a step up if a ray straight down at the 4 ray's hit plus the axles' 136.3 (along the heading, through actors) finds the ground 18 or more over the ground at the face's foot. That foot is read by a ray down 2 short of the 4 ray's hit (from 2 over it to 38 under; the line under the hit along the bike's pitch if it finds nothing), and the ray a wheelbase on starts `ClimbTop` + 8 over it plus `ClimbMaxPitch`'s rise over the run (safely over any top under `ClimbTop`, whichever way the ground slopes) and ends `ClimbTop` + 8 under it. Test 45's review of the first build: its ground line ran from the feet along the rear wheel's ray's slope, 36.7 long, stretched 4.3 times to the far point, so a step of 18 to 31.9 onto level ground read as a beam on a rise of a few degrees (a 25 step past 2.9) and, downhill, the ray down started inside the step. Else it is a rail or a beam with a drop behind it (`CLIMB_BEAM`: no boost, and once stuck "climb: stopped with forward held (…): not climbed: a beam with a drop behind it, not a step up: something at 18 above the feet N ahead (what, layer N; ClimbMaxTop), not round (N deg at its foot) and long (the rays 36 to either side meet it too), and a wheelbase on, N ahead, the ground N over the ground at its foot (what, layer N)", or "… no ground from N over the ground at its foot to N under it"). A boost's "a low face at the capsule" line says which let the face through: "; at 18 N ahead: round, receding toward its foot (ClimbMaxTop)", "…: narrow, the ray 36 to the left passes it (ClimbMaxTop)" or "…: a step up, the ground N over the ground at its foot N ahead (ClimbMaxTop)". A log sunk in the ground so that its face doesn't recede at its foot reads upright, and with the ground behind it lower is a beam (`ClimbMaxTop=0` lets it through, and the rails with it); a rail whose foot is set back under its face (a beam on posts that the ray at 4 meets behind it) would read round and be climbed as in test 44's build. Before any of that, a low face with something at 1.5 or 2 `ClimbTop`s (48, 64) above the feet within 45 past it, not an actor, is a barrier's foot with its bar beyond, out of the reach of the rays at 18 and 31.9 (test 44's 22:47:39, the front wheel's ray 65 up on it): `CLIMB_BAR`, no boost, and once stuck "… not climbed: a bar beyond the low face: something at 48 above the feet N ahead (what, layer N; ClimbMaxTop), where the capsule would hang on the face under it (a barrier)". The barrier at 22:47:39 was mounted with the boost off, sliding along it at 880 a second; the rule doesn't stop that, but it stops the boosts that flickered on it afterwards (85 for 0.1 to 0.3 s), and the hung-up reverse (the backing below) gets the bike off. Whether the guard rail of 22:48:57 is now refused depends on whether the brush pile behind it reads as ground 18 or more up, which the log can't tell. The "  climb:" line gains "; a face with something 18 above the feet within 45 past it climbed only if round (receding toward its foot), narrow (a ray at 18 two capsule radii to a side passes it) or a step up (a ray down a wheelbase past it finds the ground that high over the ground at its foot) (ClimbMaxTop: a log, a stump or a step, not a rail or a beam with a drop behind it), and a low face with something 1.5 or 2 ClimbTops above the feet within 45 past it not climbed (a barrier's bar)", and `ClimbMaxTop=0` ("any face under ClimbTop climbed, a beam with a drop behind it too (ClimbMaxTop=0, test 44's build)"), read again on getting on, is test 44's climbing. Test 45 (at 2:56.4 of its video a raised guard rail met at an angle, `0000DE21_Physics`, and at 9:48.9 a picket fence's post, `L1_PicketFenceB_Post01`, both "at 18 16 ahead: narrow, the ray 36 to the right passes it (ClimbMaxTop) … the climb limit 47 -> 85", and the bike went onto the rail and along the fence with its side in it: a ray at 18 passes under a rail's beam, between posts or between pickets; at 5:24.0 a guard rail lying on the ground, `0000DDA0_Physics`, "61 ahead at 4, 61 at 10 (95 deg), nothing at 31.9", its top under 18, was climbed by design, and the bike rode along on top of it). So since test 46 the narrow test casts its side rays at up to three heights (`NarrowHeights`, 3): `ClimbMaxTop`, 6 over it (24) and the face's top less 4 (`ClimbFaceTop`: a ray straight down 1.5 past where the ray at 18 met the face, from `ClimbTop` + 2 over its foot; `ClimbTop` less 4 if that finds none), each height counted only where the line's own ray at it meets the face, under `ClimbTop` and 2 or more from the others (`ClimbRayHeight`, `ClimbNarrow`), and the face is narrow only if one side passes at every height: a stump still is, while a rail met at an angle or a fence's post meets the side rays at 24 (the beam's line "… long (the rays 36 to either side meet it too, cast at 18 and 24; a side's at 18 passes it, at 24 meets it (NarrowHeights)) …", a boost's "…: narrow, the ray 36 to the left passes it at 18 and 24 (ClimbMaxTop, NarrowHeights)"). A fence met under about 30 degrees off the heading lies past the side rays' reach (they meet a line up to about 58 degrees off square) and can still read narrow at every height: test 45's at 9:48.9 read 24 off, so that one may not be fixed (a second cause, not confirmed: the face rays' verdict there likely turned to "under the bike: an obstacle" as the front wheel's ray met the post 77 above the feet, which let the boost in). `NarrowHeights=2` casts at 18 and 24, 1 (or 0) the one ray at 18 of test 45's build. And a face under `ClimbMaxTop` that everything else would climb is judged last (`ClimbBeamLow`, 8: `ClimbLowBeam`, `CLIMB_LOWBEAM`, judged while the boost is off and only when `ClimbBeamLow` is under `ClimbMaxTop`): not climbed if its top (`ClimbFaceTop` again, 1.5 past where the ray at 4 met it, from `ClimbMaxTop` + 2 over its foot) is 8 or more over its foot, it is upright (80 to 100 degrees between the hits at 4 and 10, and between the nearer of them and a ray at its top less 2: a log's face recedes toward its foot under its middle and leans back over it, so one under 17 across reads under 100 at its foot and over 100 or under 80 at its top), long (not narrow at 10 and at its top less 2) and thin (a ray straight down two capsule radii, 36, past its face, from `ClimbMaxTop` + 8 over its foot plus `ClimbMaxPitch`'s rise over that run to `ClimbMaxTop` + 8 under it, finds the ground under half its top over its foot, or none: "climb: stopped with forward held (…): not climbed: a low beam with a drop behind it: its top 13.0 over the ground at its foot 18 ahead (what, layer N; ClimbBeamLow 8), upright (90 deg at its foot, 90 at its top) and long (the rays 36 to either side meet it too, cast at 11), and 36 past its face, N ahead, the ground 0.0 over the ground at its foot (what, layer N)"). A kerb or a step (its top going on), a log and a stump still climb, the boost's line saying which ("; its top 12.0 over its foot: a step up, the ground 12.0 over its foot 36 past its face (ClimbBeamLow)", "…: not upright (93 deg at its foot, 67 at its top), a log (ClimbBeamLow)", "…: narrow, the ray 36 to the left passes it at 9 (ClimbBeamLow)", "…: too low to tell (ClimbBeamLow)"). The "  climb:" line's narrow clause reads "narrow (rays two capsule radii to a side pass it at 18, 6 over it and the face's top less 4, each where it is within the face (NarrowHeights=3))" and a clause of `ClimbBeamLow`'s follows ("; a lower face, its top 8 or more over its foot, not climbed either if upright (80 to 100 deg at its foot and at its top), long (not narrow at 10 and its top less 2) and thin (the ground two capsule radii past its face under half its top over its foot): a rail lying on the ground (ClimbBeamLow), a kerb, a step, a log or a stump still climbed", or "; any lower face climbed (ClimbBeamLow=0)"); both keys are read again on getting on, and `ClimbBeamLow=0` is test 45's build. Test 46 (2:24.3 and 2:30.8 of its video, a wooden road barrier met at a shallow angle, `0000DE40_Physics`: "at 18 29 ahead: narrow, the ray 36 to the left passes it at 18 and 24 (ClimbMaxTop, NarrowHeights) … the climb limit 47 -> 85", and the bike went across and along it; its six other narrow climbs, fallen boards, logs, rocks and a tyre pile, looked right) hit the gap left open above: the side rays started 36 to a side and 36 back of where the line's own ray met the face and went along the heading, so with a line under about 32 degrees off the heading one side's ray began beyond it and passed it at every height (in the fake game the left one at 18 degrees, as the real log's "left"). So since test 47 (`NarrowBoth`, 1; `ClimbNarrowAcross`) each side's ray at each height starts where the line's own ray met the face, two capsule radii (36) out from it along the face's level hit normal, turned to face the bike, and 36 to the side along the face's line, and goes into it along the normal three times that (108): a rail meets both sides at any angle, a post or a stump neither, and the face is narrow only if both sides pass it at every height (`narrowPass` 3). The normal is the hit's at `ClimbMaxTop` (`ClimbBeam`; the hit at 4 if that has none) and for `ClimbBeamLow`'s narrow test the hit's at 4 (`ClimbLowBeam`, so it goes by `NarrowBoth` too), both kept by `ClimbRays`; with none usable (not a unit vector, the ride's normals found bad, or a face within about 15 degrees of level) the heading's square stands in for its line. A face judged long says which side passed ("long (the ray 36 to the left passes it, the one to the right meets it, cast at 18 and 24) …" where both met it, as before, "the rays 36 to either side meet it too"; `NarrowLongWords`) and how they were cast ("; the side rays cast across its face, its line 18 deg off the heading (NarrowBoth)", or "…across the heading, no usable normal (NarrowBoth)"), and a boost's line "…; at 18 52 ahead: narrow, the rays 36 to either side across its face pass it at 18 and 24 (ClimbMaxTop, NarrowHeights, NarrowBoth)" ("…across its heading" without a normal; `ClimbBeamLow`'s "; its top 12.0 over its foot: narrow, the rays 36 to either side across its face pass it at 9 (ClimbBeamLow, NarrowBoth)"). The cost: a face wider than about 72 along its line met off its middle (a wide stump, a big rock), which one side passes, is long now and climbs only as a step up; round logs are judged round before the narrow test and are unaffected. Which of test 46's six still read narrow the log can't say (the old test stopped at the first side that passed, the left tried first, and five passed on the left); the tyre pile at 18:55:42 passed on the right, so its left ray met it, and it likely reads long now, climbed only if the ground a wheelbase on is 18 or more up (the bike went 38 up onto it, so plausibly). `NarrowBoth=0` is test 46's test; it and `UnderBikeTop` (*Tilt* below) are on a "  rails:" settings line of their own ("  rails: the narrow test's side rays cast across the face (into it along its level hit normal, two capsule radii to either side along its line), narrow only if both sides pass it: a post or a stump, not a rail met at a shallow angle (NarrowBoth=1); …", or "the narrow test's side rays cast along the heading, one side passing it enough (NarrowBoth=0, test 46's build)"), logged with the steer lines or alone when only these two change, and read again on getting on. Two more of test 45's were traced and left as they are: up a wrecked car at 5:28 to 5:36 (`FusionFlea01`, layer 29) every trace line says "climb off": the capsule went up the car's body at ground normals of 29 and 44.5 degrees, within the game's 47, the face rays holding the throttle at 55% ("an obstacle lower than 1.5 wheel radii (83 deg)", then "under the bike: an obstacle" with the front wheel's ray 109 up on it), so a fix belongs to the obstacle verdict (since test 47 `UnderBikeTop`, *Tilt* below, makes such a verdict a wall while the rear wheel's ground is level with the feet; whether it was at 5:28 the log can't tell); and off a porch through its iron railing at 7:33 there is no face-ray line at all: the face rays are three rays on the centre line, which balusters with gaps wider than a ray let through (whether the capsule went through a gap or the railing has no collision the log can't tell; rays across the bike's width would be needed). The face rays' lines come from a hand of 20 refilled one every 3 s since test 41 (test 40's 60 a ride were spent in two minutes off-road, and the next three stops had none), and "nothing ahead now" names the verdict that stood and for how long.
- **Tilt (F4SE plugin):** animations don't know the ground's angle, so `CMB_Slope.dll` tilts the worn bike. The ground: the test-6 diffs showed a unit vector at `bhkCharProxyController+0x1E0` that is (0, 0, 1) on flat ground and follows the slope while riding, the controller's support normal (just after its up vector at +0x1D0, as in Skyrim's `bhkCharacterController`). Havok's character state (0 on the ground, 1 jumping, 2 in the air, 3 climbing, 4 flying, 5 swimming, 6 floating) is at +0x2C0, in the `hknpCharacterContext` embedded at +0x2A0: its state manager pointer is at +0x2B8 and its max acceleration, speed and gain (625, 20, 1) at +0x2CC; the plugin reads the state only if that state manager pointer is really a `hknpCharacterStateManager`. The bike: it's skinned to one bone (COM or AnimObjectA), so the animation moves it and its own node's transform does nothing; but the skin's bind, `BSSkin::BoneData` (mesh → bone, read per frame for skinning), can be turned. Finding the bike: in test 7 a walk of the player's 3D root found no shape named `CMB_BikeWorn*` on any ride, so the plugin now also looks through the biped (`Actor::biped` +0x428: `BipedAnim::root` +0x08, then 44 objects of 0x58 from +0x10, each with its armor addon at +0x18 and its 3D, `partClone`, at +0x30; F4SE's own layout, and its `GetWornItem` reads the same array) and walks every equipped armor addon's 3D, and it accepts a shape by its skin as well as its name: one bone, with the COM bike's bind (the rotation below and a translation of about (−74.5, 0, 0)). Test 8 found it every ride by its bind: the game renames the worn shape to "<armor name> (armor ID)[n]/<addon name> (addon ID)", so `Shapes=` never matches; the biped route also takes any part whose armor addon is one of ours, so the planted variant (AnimObjectA, identity bind) is found too. If a ride finds nothing for a second, the log says what it saw: the root, every type of object met and how many, the shapes (name, type, skin and bone data types, bone count), the biped's root and slot 57's addon and part, and the part's parents up to the root. Holding a skin: the plugin holds a reference on their `BoneData` (so it can't be freed under it) and every frame turns the mesh before it goes onto its bone. The pitch comes first from two rays cast down at the wheels' contact patches (the axles from the parts file; each starts above the most the ground can rise to its wheel on a climbable slope, tan 50 degrees of the wheel's reach, and ends 160 below the feet, a hit above that rise being a branch or a ceiling, not the ground: test 30's front ray, from 70 above the feet, started inside rock on a 33 degree climb and found the ground beneath, 15 degrees short; since test 29, where the track lagged half a wheelbase at a lip or a crest and the bike sank into slopes; since test 40 both pass through actors, their capsules, layer 30, and bodies, 8: test 39, a radstag in front of the bike, the front ray hit its capsule 107 above the feet, and with the pitch's target at 40 to 44 and a lift of 33 the bike reared up at it for 0.6 s; the face rays still stop at one ahead, so the throttle still eases off short of it, and with `Trace=1` the log says "rays: a ground ray passed through ... an actor, not the ground", once a second at most): the line between the two hits, the median of the last three frames of it (a one-frame hole or lip doesn't count), with the bike lifted onto that line when the ground between the wheels is above the capsule's contact (a dip, a lip under the front; up to 60 units; lowered only by the suspension's droop, below: test 31's 40 left the front wheel in boulder faces). Where the rays have no word while riding, the lift is held with the pitch for 3 s before it eases to 0 (3 s covers a slow back-off, and a tunnel's ceiling, which throws the hits away for as long as it lasts, must not float the bike on a stale lift; test 38: backing off a station wagon the front wheel had climbed, the rays missed, the roof being above the front ray's allowed rise, the pitch was held at 41.5 while the lift fell from 34 to 0 within a quarter second, so the rear wheel, 26 below the pivot at that pitch, went under the ground: "going back was putting half of the bike underground"); the "rays: the wheels' rays" lines (one a second at most, from a hand of 10 lines refilled by one every 6 s, 10 a minute sustained, full again on each ride, and while backing from a hand of their own, so the backing tests always get theirs: test 39 had spent the 30 a ride of old by 01:35:02, before the backing tests began; the lines for a hit thrown away likewise) give each ray's hit, what it hit and its layer, under a pitch of 25 degrees or more or with a wheel hanging at its droop, and a hit thrown away as above a ray's rise says what it was (the collapsed roof at 10:48:43 of test 38, where the rear ray found something 30 below the roof the capsule stood on, is what they are for). Where a ray misses (no Address Library, a ledge, nothing under a wheel but actors) the pitch is the slope of the track just ridden (the player's feet now and 120 units back along the track, about a wheelbase, measured along the heading so reversing down a hill still lifts the nose): test 9's trace showed the support normal swinging from −60° to +67° and flipping sign within half a second even on Sanctuary's roads, which no filter fixes, while the track is the capsule's own path, already smoothed by its radius, lagging about half a wheelbase. It holds in the air (counted only after 50 ms off the ground: test 29's state flapped air/ground every frame for a third of a second over bumps, and the tilt's samples went with it) and, where the rays miss, standing still and while turning: the track's direction is used only while the bike is moving (a track point in the last 0.3 s) and that movement is along the heading (forward) or against it (a real reverse, which keeps the nose up backing down a hill); turned on the spot, the last movement points backwards just like a reverse, and test 10 saw the pitch flip from −61° to +50° there. A front hit above its rise with the rear on the ground is a face, not a slope: a forward ray at axle height (`WallAhead`, from under the rider to 10 units past the front axle) that hits something on the way cuts the throttle's input for a quarter of a second (logged as "rays: a face ahead of the front wheel"), so the bike stops short of a boulder face it can't climb instead of riding its front wheel into it (test 31); turning away or backing off is still the rider's. Test 32 found that word came with the face already at the wheel (16 to 81 ahead), so `FaceRays` looks ahead every frame the throttle is on: two rays forward along the bike's pitched axis, at axle height and at 1.8 wheel radii, as far as `FaceLook` seconds (0.3) of the speed past the front wheel; both hitting at about the same distance is a face (the slope between the two hits, over the bike's pitch, at or past the climb limit: a slope under it puts the upper hit further on by its rise over its tangent, a step lower than the wheel's top misses the upper ray), and the throttle is multiplied by the distance left to it over the look-ahead, nothing at the wheel, so the bike eases off and stops short. Small bumps (test 33: the tyres sank into small hills, stones and curbs that passed under a wheel before the median and the spring reacted): on top of the filtered lift, whichever wheel would sit below its own ray's hit, with the pitch and lift as applied, is lifted out, and that bump lift settles as the filtered values catch up or the bump passes; the lift stays capped at 60. Test 34: it rose 60 units in a frame and launched the bike, so the bump part was rate-limited (`BumpRise`, 0.12 s); test 35 launched it again, the whole lift up within 0.2 s (3 to 36.8 in a quarter second at 900 units a second), since the filtered part rose on top of the bump's. So now the whole lift, filtered part and bump together, rises at most `LiftRate` (120) units a second (0 = unlimited; `BumpRise` is gone), the bump part goes straight to the deficit under its wheel, never above it, and settles over `BumpSettle` (0.45 s); it is capped at `BumpMax` (30, a wheel radius), and at 1.5 radii while an obstacle verdict is in force, kept that wide while the bump is above `BumpMax` so the hold lapsing can't drop the lift in a frame (test 35: the obstacle rule passed a 35 to 45-unit stone while the bump stopped at 30; the pitch takes the wheel onto a step within a third of a second, so the bump is the first instant's share and the rate bounds it anyway, and the wider cap seldom shows). Test 36 found the bike "still stiff, nothing like suspension" and asked for one: the wheels following the ground, the frame and rider following them through a spring and damper. `Suspension` (1) does that: each wheel sits on its own ray's hit, moved against the frame along the bike's up by what it lacks from where the frame holds it, up into the frame over a bump by `SuspTravel` (10) units at most and down into a hole by `SuspDroop` (4; test 38: at -10 the sliders left the stanchions, whose lowest vertices sit at z 58 to 62 inside sliders topping at 69.9, an overlap of 8, and the rear axle leaves the swingarm the same way; the front sat at full droop a tenth of the moving time); the wheel shapes' maps carry the offset, before the tilt, along the steering axis for the front wheel and the lower fork (test 38: the move ran along the bike's z while the fork is raked 29 degrees, so at the full 10 the sliders sat 4.9 off the stanchions' line, "forks were getting out of tubes"); a wheel compresses within 0.03 s and extends over `SuspExtend` (0.1 s; test 38: following its ray both ways within 0.03 s the front was past half its travel 43% of the moving time and flipped 10 and more within a quarter second in a fifth of the samples, "like there was no weight behind it"); the rear up by `SuspCompressRear` (4) at most, its mudguard being on the frame, not the swingarm: test 37 found the tyre within 10 of it, touching at the closest; the front's offset is carried by the lower fork's shapes too, the sliders, mudguard, caliper, axle and boots the converter names `_fork` since test 38, so the axle stays in the fork ends and the mudguard over the tyre: in test 37 they stayed with the bars and at +10 the tyre went into the mudguard), and the frame's lift follows the wheels' line through a spring of `SuspFrequency` (2) hertz with the damping ratio `SuspDamping` (0.6: a step is met with a compression and a rebound of a tenth of it; 0.5, a rebound of a sixth, was "great, maybe a tad too soft" in test 37; 1 is no rebound) instead of the 0.15 s filter; what a wheel's travel can't take of a bump feeds the bump lift as before, `LiftRate` still caps the frame's rise, and the frame sinks at most `SuspDroop` below the ground's contact, on a drop's rebound (which then shows as the wheels compressing a few units) or where the line between the hits runs below the contact (a crest, a bump under the rider: test 38 found both wheels hanging at -10 at a stop with the frame held at the contact). The trace line carries the wheels' offsets ("susp F +3.2 R -0.4"). `Suspension=0` is the filter and the bump alone, as before. Test 42, off a high ledge with W held, 1.0 s in the air: the bike nearly stopped, 881 to 544 to 398 within 0.4 s of the landing and back at 90% only 1.41 s later, the `Lead` cap following the game's own landing cut down, and the suspension stayed extended (F −3.0 R −3.0) where "it should sink on the suspension and carry on". Since test 43 a landing is the first frame on the ground after `LandAir` (0.3 s: the 0.46 to 0.65 s hops count, test 29's flaps don't) or more in the air by the plugin's own count (the track's air time is cleared at 0.4 s), the fall's speed the mean of the last three frames in the air (the landing frame's own move left out: it holds the ground's snap), and a last frame in the air that moved over 300 (a load into the air) is none. With forward held at the landing the `Lead` cap is left off for `LandHold` (0.5 s), the throttle where the jump left it, and after that while the cap would still bind and the speed is still coming back (the 0.05 s speed over the 0.2 s one by a twentieth of the top), a second more at most: the measured speed lags the game's recovery by about 0.2 s, and a cap met halfway through it is the same dip again; it ends early with the speed along under `LandStop` (0.25) of the top (a landing against something: the cap is back within about 0.28 s of a dead stop; the dips at test 42's landings bottomed at 0.44), on back, forward let go or another landing, and `WallAhead`'s cut, the face rays' ease and a hit's hold apply throughout. With `LandSink` (1, in `[Tilt]`) the frame sinks on the suspension by the fall: the front `SuspTravel` times the fall over `LandSpeed` (700 a second, the plugin's gravity of 686 over a second's fall, rounded; all of it at that or faster), the rear `SuspCompressRear` at most, as a kick on the frame's own spring (`SuspFrequency`, `SuspDamping`, the damping taken at 0.95 at most so there is a first dip to aim at), stepped by the spring's own solution over each frame's time, so 30 or 190 frames a second give the same dip: the whole sink at +0.09 s, back through the line by +0.31 s, a tenth of it over at +0.40 s, settled by +0.55 s, rising back no faster than `LiftRate`. It goes on what is applied (the bike's and its parts' transforms, the lamp, the rider's lift and pitch and its level check, and the wheels' targets, which come out compressed by it so their caps hold), never on the filtered lift, the median, the track, the wheels' history or the pitch's filter, so the bump's deficit and the droop's floor see the frame as it would be without it, and the rays keep the unsunk pitch. It needs `Suspension=1`, the tilt and the parts file's wheels; a fall under a twentieth of `LandSpeed` sinks nothing. One line a landing, from a hand of 10: "landing: N s in the air, the fall N a second: the throttle kept at N for 0.5 s (the Lead cap off; the measured speed N at the landing), the frame sunk N at the front wheel and N at the rear (the nose N deg down)", its words otherwise "the throttle held to the measured speed as before (LandHold=0)", "not held (forward not held)", "not held (the speed along N under LandStop's 0.25 of the top)" (slow already: the hold would end at once), "not sunk (LandSink=0)", "(Suspension=0)", "(no fall to speak of)" and the like; then "landing: the hold over after N s: the speed along N at its lowest (+N s), N now" or "the hold ended after N s: …" with why; the trace's lift reads "lift N (landing N, nose N)" while the sink lasts, the throttle line ", landing hold N s left" or ", landing hold on while the speed comes back". `LandHold=0` with `LandSink=0` is test 42's build, the landing's line aside. The face rays are at axle height and 1.5 radii now (test 34's wish: ride over a fallen tree or a knee-high stone while slowing): something at axle height and nothing at 1.5 radii (the upper ray cast further than the axle ray by the run a face at `ObstacleAngle` needs for the extra half radius, 15 units at 50 degrees, so what it misses is lower than 1.5 radii indeed: test 38 cast it as far as the axle ray, and on a 54-degree face its hit lay 11 further on, past the ray's end) is a lower-only obstacle, ridden over at `ObstacleThrottle` (0.55; 0.4 crawled in test 37) with the bump lift if its slope, the one between the half-radius and axle hits, is `LowObstacleAngle` (60) or steeper, and left to the suspension and the bump lift under that (test 38: the holds to 55% were mostly five low rock faces of 50 to 57 degrees, just over ObstacleAngle, that the bike rides over anyway); something at both is a wall if the slope between the hits, over the bike's pitch, is `WallAngle` (55) or steeper, the throttle eased off to nothing at the wheel as before, an obstacle if it is under that but at or past `ObstacleAngle` (50, or the climb limit if that is higher: test 37's ride had ten of its 39 throttle holds on faces of 45 to 49 degrees, over the rays' climb value of 45, which the controller climbs at 47), and nothing if it is a slope the bike climbs. A raw obstacle verdict whose axle-height hit is at or behind the front wheel's edge (test 37: 16 of the holds, the hit 0 to 105 behind the edge, the ground under the pitched bike) sets the hold below, for `WallAhead` and the bump cap, but leaves the throttle free: the bike is on it already, the suspension's to take. The verdict has state since test 35 (the bike stopped at a knee-high stone first and then rode over it: once it was on the thing the rays' hit lay 63 to 126 behind the front wheel's edge and the verdict flipped wall, obstacle, wall from frame to frame): a hit half a wheel radius or more behind the front wheel's edge, with the front wheel's own down-ray finding the ground half a radius or more above the capsule's contact, is under the bike, not ahead of it, an obstacle and never a wall (stopped against a wall the bike sits with the wheel's edge at the face, a unit or two either way: still a wall; a wall the bike has nosed or turned into, its front wheel through it with the ground flat under that wheel, is a wall too: a review of the first cut found the rays alone couldn't tell the two apart); on top of one with `ObstacleThrottle` 0 the throttle is free, there being nothing ahead to stop short of; an obstacle verdict stays in force `ObstacleHold` (1 s) after the rays last said obstacle, and while it does a wall needs the hit ahead of the wheel for `WallFrames` (5) frames running before it counts (an obstacle till then, which doesn't renew the hold); the "rays:" lines are logged on a change of verdict (a quarter second apart at least) or once a second, 60 a ride, and the verdict is dropped when the rays stop being cast (standing, no throttle), so a stop and a start on open ground says nothing; the front down-ray's own quarter-second cut (`WallAhead`, above) defers to an obstacle in force the same way; and the "rays:" lines name what the axle-height ray hit and its collision layer, as the reverse rays do (test 35: bushes with food items stopped the bike like a wall; the rays use the character controller's filter, 30, already). Test 46 (2:20.45 of its video, a wooden road barrier, `0000DE41_Physics`: "-16 past the front wheel … held to 55% (under the bike, the front wheel 49 up on it: an obstacle, not a wall)", and the bike rode on top of it; at 16:45.2 a guard rail, `GRailStrShort01`, met square at low speed, the front wheel 55 up on it, straddled till backed off at 16:50.7; at 12:43.3 a swing set, 62 up): that rule took any hit behind the wheel's edge with the front wheel up on something for a thing under the bike, however high. So since test 47 (`UnderBikeTop`, 1) a verdict at or behind the front wheel's edge, wall or obstacle (a pitched ray reading a rail's top says obstacle), is under the bike only while the front wheel's ray finds it `ClimbTop` (31.9) or less over the feet, or the rear wheel's ray finds the ground half a radius or more off them (the rear wheel up on the thing too, or the feet up on it over the ground behind: test 35's stone, the ground 40 up under both wheels, is as before), or the hit is an actor (layers 30 and 8, the rams' as before); otherwise it is a face the front wheel is in, over what a climb takes: a wall at once, with no 55% hold and no "obstacle for now" (its hit stays behind the edge, so `WallFrames`' count would never start), the throttle none, to be backed off: "rays: a wall ahead (90 deg): -29 past the front wheel at axle height (…), the throttle eased to 0% (behind the wheel's edge, the front wheel 49 up on it, over ClimbTop's 31.9, the rear wheel's ground 0 over the feet: a face the front wheel is in, a wall; UnderBikeTop) (a stop from 10 needs 40 past the front wheel: WallStop)" (the line's note grew from 96 to 200 bytes, so the "nosed into" note is no longer cut off either). The front wheel's height is taken over the line through the rear wheel's ground and the feet, not in world height (review: on a uniform 18 to 22 degree uphill the slope alone put the front axle's ground over 31.9 with the rear wheel's under half a radius off the feet, so a log the boost would take was a wall); on a slope of over about 20 degrees the rear wheel's ground lies half a radius off the feet anyway, so the old rule holds there. `UnderBikeTop=0`, on the "  rails:" line with `NarrowBoth` ("…, under the bike, an obstacle, however high (UnderBikeTop=0, test 46's build)"), is test 46's rule. Test 42, riding beside a railing ("it should go alongside"): three times in three minutes a rail beside the bike, the heading 17 to 28 degrees into it (GRailEnd02, GRailStrShort01), was a wall or an obstacle ahead by its steepness, and the speed went 897 to 359 and 909 to 31; once the capsule grazed the rail the game kept about half the speed (850 to 358, 683 to 338 with the input at full) and the `Lead` cap followed it down, so a graze ended in a stop 0.5 to 1.0 s later. Since test 43 each ray keeps the pick's hit normal too (`bhkPickData`+0x70, the normal of the `hknpCollisionResult` at +0x60 whose layer the plugin already read at +0xAC; zeros on a miss), and the ride's first face logs it ("rays: the pick's hit normal at the first face (…), length N, N deg off the heading, the rays' slope N: usable", or "…: not a unit vector: faces judged by their steepness alone", which leaves the rest of the ride as before). A face whose line lies under `FaceAlong` (30) degrees off the heading by that normal is alongside: its normal's level part 0.5 or more (steeper than 30 degrees, not a ramp's top), facing the bike, not an actor's capsule or body (layers 30 and 8 stay across, for the rams and the brakes), and with `FaceAlongRays` (1) confirmed by two more rays at axle height 24 either side of the one that hit (the capsule's 18 + 6; the one toward the face starts no further over than half the face's distance across there, so it doesn't start behind a face being slid along), both hitting, as far apart along them as a face under `FaceAlong` puts them (83 at 30 degrees): a post or a trunk the ray grazed, its normal oblique, has a side ray miss it and stays across ("… (alongside by its normal, N deg off the heading, but the rays either side don't say so: toward it found nothing within N, away hit N along)" on its line). A face alongside is left alone whatever its steepness, as the controller slides along it: no ease, no verdict, no obstacle hold renewed, no wall frames counted ("rays: a face alongside, N deg off the heading: N past the front wheel at axle height (what, layer N), its normal (…): left alone", and "nothing ahead now (was a face alongside, …)"); `WallAhead` doesn't cut the throttle at one either ("rays: a face alongside at the front wheel (N deg off the heading, …): the throttle not cut", a second apart at most: a building's wall beside the bike would cut it a quarter second at a time), and the climb's boost isn't given at it. 30: the rails read 17 to 28, a clean slide keeps the cosine of the angle of the speed, and at full throttle the cap binds only past 26.6 degrees. What the game still takes at contact the slide's hold covers: with forward held, the keys passed on, no wall verdict, no cut at the front wheel, no climb boost, and a face alongside seen in the last half second or the velocity `SlideAngle` (15) degrees or more off the heading at over 60 a second (test 42: turns read 8 off at most, the slides 23 to 44), the `Lead` cap may not pull the throttle under what it was when it would first have bound, for `SlideHold` (1 s) at most; it holds, never raises, never from a stop, one hold a slide (one that ran its time gives no other till the evidence has gone), and ends with its time, the evidence, a wall verdict, the cut, the boost, back, forward let go or the throttle down to a tenth ("slide: along a face N deg off the heading (what, layer N, seen N s ago), the velocity N deg off the heading: the throttle held at N for up to 1 s (the speed along N would have capped it at N)", "slide: no face alongside seen in the last half second, …" on the velocity alone, "slide: over after N s: why (…)", from a hand of 10; the throttle trace ", slide held N for N s", and no "held to the measured speed" word while it holds). `FaceAlong=0` with `SlideHold=0` is test 42's build exactly, the normal's line aside. Test 45 (5:57.7 of its video: a raised rail met square at 905, "a wall ahead (84 deg): 187 past the front wheel … eased to 68%", the bike going 905 to 175 in about 0.55 s, then "-11 past the front wheel … eased to 0%" with its front wheel in the rail): the face rays' reach, `FaceLook`'s 0.3 s of the speed past the front wheel, is shorter than a stop from full speed. So since test 46 (`WallStop`, 0.6) a wall's ease starts from the distance a stop needs past the front wheel (`WallStopNeed`): the speed squared over twice `WallStop` times the brake's rate (`FullSpeed` / `Brake`, 2250 a second a second at 900 and 0.4; 0.6 of it, 1350, about what test 45's stop made with the input still at 30 to 68%), plus a tenth of a second of the speed (the input's and the game's lag) and 10: 400 at 900, 73 at 300. Within it the throttle is none; past it the ease runs over the look-ahead's span as before, (the distance left less that) over the span. When the need is longer than the reach (from about 515 a second) and nothing is at axle height within it, the two face rays (at axle height and 1.5 wheel radii) are cast again as far past the front wheel as the need, for a wall dead ahead only: not an actor (layers 30 and 8; `WallStop` doesn't apply to actors at all, so the rams' brakes are as they were), nor a face alongside by its normal (under `FaceAlong` off the heading, whatever the rays either side would say), so riding along a rail is as it was. Since the review the stop's ease leaves out the same faces: one alongside by its normal that the rays either side don't confirm (a wall verdict with "(alongside by its normal, …, but the rays either side don't say so …)") keeps `FaceLook`'s ease, as test 45's build (09:30:22.316, a station wagon 22 degrees off at 909, 278 past the front wheel: "eased to 99%", then "a face alongside, 17 deg: left alone" and ridden past; `WallStop`'s 0% for the frames between, about 0.25 s of no input at full speed, would have cost some 300 a second; 09:39:38.691's Tracker, 6 degrees off at 919, the same). The wall's line adds " (a stop from 883 needs 387 past the front wheel: WallStop)", with ", looked for that far, past FaceLook's reach" for a hit of the longer cast, and the "  steer:" line a clause before `FaceAlong`'s ("a wall dead ahead (not an actor) eased by the distance a stop needs: the speed squared over twice 0.6 of the brake's rate (FullSpeed / Brake, 2250 a second a second), a tenth of a second of the speed and 10, the throttle none within it, and looked for that far past the front wheel when FaceLook's reach is shorter, a face alongside by its normal not (WallStop)", or "a wall eased by FaceLook's reach alone, to nothing at the wheel (WallStop=0)"). Every wall but an actor or a face alongside by its normal now stops the bike about 10 short of the front wheel's edge, not at it, at any speed (since test 47 about 40: `WallStopShort`, below). `WallStop=0`, read again on getting on, is test 45's ease. Test 46 ("now I was getting slowed down or randomly stopped by objects and world geometry"): `WallStop` cut the throttle 81 times in 857 s of riding, 75 of them to 0%, the speed down a median 520 a second within 1.5 s; 47 came from the longer rays, and in 47 of the 62 with a "nothing ahead now" after them the wall was gone within 0.2 s (median 0.1): fences, mailbox stands, stumps, rubble, stairs, deer fences and precombined geometry the bike was steering past, seen 200 to 400 past the front wheel at 870 to 920 (ten in one minute in Sanctuary, six of them down to 105 to 187), and 3 of the yeses not knocked over were braked for under 450 after such a cut. The longer rays reached only the need while the ease runs from the need and the span down to the need, so a wall first showed where the throttle is none: a cut from 100% to 0 in one frame (the build-27b review had said so). Since test 47 five more `[Steer]` keys, each 0 giving test 46's part and all five at 0 test 46's `WallStop` exactly (`ReadLeanSettings`, read again on getting on). `WallStopReach` (1): the longer rays reach the need and `FaceLook`'s span past the front wheel, cast whenever `FaceLook`'s own reach finds nothing at axle height, not only when the need is past it, so the ease runs from where a wall is first seen down to the need: 810 past the front wheel at 900 (with `WallStopPersist`), 45 at rest (10 in test 46; a wall that close is a wall verdict, which refuses the climb's boost, `CLIMB_WALL`, and the bike stops 40 short of it anyway; while the boost is on the rays are test 46's, so a wall further off doesn't end it on the way over a trunk). `WallStopPersist` (0.15 s): a run of WallStop frames (`g_stopSince`; a gap of 0.1 s ends it) whose wall was first seen by the longer rays past `FaceLook`'s reach is held to a floor falling from all of the throttle to half over 0.15 s, so it takes the throttle under half only once it has stayed that long, a glimpse of 0.1 s leaving two thirds; such a wall's need has 0.15 s of the speed more (135 at 900: 535 in all), so one that stays is still stopped for in time. Since the review of test 47's build the floor holds only while the wall is still past the need: one first seen between the need and its extra (a rail that comes into the rays' line 420 past the front wheel at 900, the need 400 and the extra 535) had no room for the floor's time, and wherever the floor holds the throttle over what holds the speed (under the top, the bike still gaining) it starts the run-down up to 0.3 s of (1 − speed / `FullSpeed`) later (0.1 s at 600), so such a wall is now cut at the need at the latest, as test 46's build did with its rays reaching the need; at the top the floor's 50 to 100% is already under the speed's own input, so the run-down starts at once either way (the harness's, toward the input's speed at 1500 a second a second, stops 40 short of such a rail with the floor or without it). `WallStopNear` (0 since the review of test 47's build, 1 in its first build): the same floor for a wall first seen within `FaceLook`'s reach at a speed whose stop needs more than that reach (from about 515 a second, where any wall there was a cut to nothing at once) and at least 0.15 s of the speed and a wheel radius past the front wheel (165 at 900: test 46's 15:47.9, precombined geometry behind a lawn flamingo, 0.3 s at 0%, 916 to 164); nearer, or slower, it counts at once as before (a rail met square, a boulder's face). Such a wall can't be stopped for in time, and below the top speed the floor delays the run-down as above, so one that stays is met faster; replayed it kept 4 of test 46's 81 cuts, so its default is now its off value, 0, test 46's build. `WallStopArc` (90 degrees): while turning the longer rays go along the arc the bike's rate of turn puts it on (`CastArc`: two chords, to the arc's points at half and the whole of the reach; the heading's rate smoothed over 0.1 s in `FaceRays`, afresh after a gap of 0.2 s, a jump of over 1.5 radians taken for a load or a door), not straight along the heading: at 900 and 26 degrees a second (the median at test 46's cuts) a straight ray 530 long (test 46's reach from the rider) ends 70 off the bike's path, one 950 long 230. Where the arc would turn more than 90 degrees over their reach (at 900 from about 85 degrees a second; 6 of test 46's 47 cuts by the longer rays came at 85 to 227) they are left out, `FaceLook`'s own reach still looking, but for a wall already being eased, which stays looked for along the arc up to half a turn (the speed falling in a turn puts the arc over the limit, and losing the wall would free the throttle at it); a face alongside by its normal, along the heading or along the chord that met it, is left out as before. The chords leave the heading's line at once, so they meet things within `FaceLook`'s reach, or beside the front wheel, that the straight rays pass (the review of test 47's build: a post 28 inside a turn at 300 and 30 degrees a second, 50 past the front wheel, was a cut to nothing at once with no floor, at a speed where test 46's build cast no longer rays): since then such a hit counts only past `FaceLook`'s reach, or, for a wall already being eased (followed along the arc as it comes nearer, so the throttle isn't freed at it), ahead of the front wheel; straight rays are as before. `WallStopShort` (10): the need is never under a wheel radius and 10 past the front wheel's edge, 40 with the 29.9 radius (test 46's 16:43, a guard rail met square at low speed: at 202 the need was 45, 62 ahead still gave 26%, and as the need fell to its 10 at rest the bike crept on till the front tyre was up on the rail), so every WallStop stop now ends about 40 short of the face, not 10. The wall's line says which ("(a stop from 900 needs 535 past the front wheel: 400, and 0.15 s of the speed for a wall first seen past FaceLook's reach (WallStopPersist), seen by the longer rays, 810 past it (WallStopReach); held to 80% till it has stayed 0.15 s, seen 0.06 s (WallStopPersist), or till it is at the need: WallStop)", with `WallStopNear=1` "…; held to 100% till it has stayed 0.15 s, seen 0.00 s (WallStopNear): WallStop)", ", along the turn's arc, +26 deg/s (WallStopArc)"), and the "  steer:" line's clause grows to match ("…, a tenth of a second of the speed and 10, never under a wheel radius and 10 (WallStopShort), the throttle none within it, and looked for that and FaceLook's span past the front wheel whenever FaceLook's reach finds nothing (while the climb's boost is on, that far when FaceLook's reach is shorter), the ease running from there down to it (WallStopReach), a face alongside by its normal not (WallStop); a wall first seen past FaceLook's reach held to a floor falling from all of the throttle to half over 0.15 s, under half only once it has stayed that long, and only while it is past the need, its need 0.15 s of the speed more (WallStopPersist), one first seen within FaceLook's reach not (WallStopNear=0); the longer rays cast along the arc the bike's turning puts it on, left out where it turns more than 90 deg over their reach (WallStopArc)"). Test 46's 15:47.9 had no line of its own because a verdict was logged only on a change of its kind, or once a second: since test 47 one that goes into or out of WallStop, or to another thing holding the throttle at least 20 points lower than the last line said, is logged as a change of kind is (a quarter second apart at least, from the same hand), "… (the verdict moved: the last line had FakeWall at 84%)". The cost: one or two more rays a frame at any speed, four while turning with a hit. Test 46's 81 cuts replayed, each thing in view as long as its log says, with the rules since the review of test 47's build: if the 22 first seen at the end of test 46's reach were in line from further off (the longer rays then see them at their own reach, with the floor's room), 58 would still take the throttle under 50% (about 49 once the long rays' hits the arc passes more than 60 from are dropped; 43 of the 66 at 600 a second or more; Sanctuary's minute 10 to 7), 15 of them real low-speed stops (the guard rail, a tyre pile); if each was first seen where test 46's rays first saw it, 75 (about 60). (Test 47's first build: 49, about 42, at worst 71; the floor between the need and its extra and `WallStopNear` made the difference.) These count the throttle, not the speed: at the top the floor's half or more is already under the speed's own input, so a glimpse costs the speed it costs under a cut there; what saves the speed is the ease starting at the longer reach and the arc. Once a ride's track has given a pitch, it holds rather than going back to the normal. Only for the first metre of a ride (no wheelbase of track yet) does the pitch come from the normal, turned into the rider's frame; the roll always does. Those are the median of the last 0.25 s (a one-frame contact with a curb or a lip of rock doesn't count). Each is capped (pitch at `CMB_TiltLive`, the MCM's `CMB_MaxTilt` while riding, default 45° since test 29, the climb limit, after 20 since test 20 and 15 before: at 20 the front wheel went into anything steeper by the difference; roll at `MaxRoll`, default 0, since a two-wheeler stays upright across a slope: test 8 showed the bike rolling under an upright rider). On top of the ground's roll the bike leans into its turns (test 31's wish): from atan(v·ω / g), the lean a real bike needs at that speed and turning rate (g in the game's units, 687), faded in from 50 to 150 units/s so a creep turn stays upright. Test 32: a side key asks 300 degrees a second at once, so the atan sat at the cap and the roll jumped 18 degrees between quarter seconds; now the turning rate is smoothed over `LeanSmooth` (0.45 s) first, v·ω/g under `LeanDead` (0.08) gives nothing (a small correction barely leans), the lean is `LeanGain` (0.5) of the physical one, capped at `MaxLean` (14), and it changes at most `LeanRate` (30) degrees a second, all read again on getting on; the rider, held on the bike, leans with it, and the head is kept level with the horizon (`HeadLevel=1`: the head's bones, and the plain shapes under them, get the roll turned back out about the head's node, so the eyes stay on the road; its pitch still goes with the bike), and follows its target through a critically damped spring (ω = 3/`Smoothing`, settling in about 0.25 s; smoothing followed by a rate cap saw-toothed in test 29 whenever the source changed) at most `MaxRate` 90° a second. The filter starts from level on every getting-on (test 9: rides ended by taking the bike off kept the last pitch into the next ride). The turn is about the contact under the rider (`PivotHeight` and `PivotForward` 0 since test 29): while the rider stayed level the pivot was the seat (74 up, 12 ahead), since turning about the feet moved the seat about 18 units from under her at 15° (test 8: off the seat, hands off the bars); now that the rider tilts with the bike the seat stays under her either way, and a pivot at the seat pushed the lower wheel into the ground by 74·sin(pitch), which is why test 29 saw the bike sink into slopes. So the skin's rotation becomes A·R and its translation t + A(P − R·P), P the pivot. The culling sphere grows by the most its centre can move. `Trace=1` logs the normal, state, raw, median, smoothed and applied angles every 0.25 s. The rider tilts too (`Rider=1`, since test 23, where the bike pitched 20° under a level rider with the hands in the air): the F4SE task runs before the animation writes the bones, so the skeleton can't be turned, but every skinned shape of the player's 3D except the bike's (the body, the outfit, the head, the hair: `BSSkin::Instance` at `BSGeometry+0x140`, its bone nodes in the `tArray<NiAVObject *>` at +0x28, read back as NiAVObjects, its `BoneData` at +0x40) gets its skin-to-bone transforms rewritten each frame so that, with the bones where they were last frame (`NiAVObject` world transform at +0x70, position +0xA0, scale +0xAC; the root's checked against the player's position first), the mesh lands where the bike's tilt about the pivot would put it: the tilt R about P goes to world through the bike's bind and the COM's world transform (Rw about Pw), and for a bone with world (N, n, s) the map y → C y + c with C = Nᵀ Rw N, c = Nᵀ(Rw(n − Pw) + Pw − n)/s goes in front of the bind; the culling sphere grows by its centre's move. The game's own `BoneData` is shared with the model cache and every NPC wearing the same mesh, so it's never written: the instance is pointed at a copy of ours (the game's vtable, a reference count that never reaches zero, the transforms in a buffer of ours; the copies are kept for reuse, never freed) while riding and back at the original after, with references held on the instance and the shape meanwhile. Plain shapes under the bones (a holstered weapon, the Pip-Boy) get the same map in front of their own local transform (+0x30), from their parent's world transform. One frame behind the animation: the riding pose barely changes from frame to frame. A bone entry may have an empty culling sphere (test 24: the CBBE vault suit's SPINE1 has no vertices and a radius of 0, and the whole suit was refused and left level while the body under it pitched, tearing the rider); it's accepted and its sphere left empty. All or nothing: a skinned shape that can't be held (the log names the bone and the check) leaves the whole rider level for the ride, plain shapes included. Test 25 lost about 30 fps with the rider held (70 shapes, 27 skinned), even standing still, while the bike's own tilt had cost nothing; so nothing is written while the tilt is level (the originals put back once), `[Tilt] RiderSkinned`, `RiderPlain`, `RiderSwap` (0 = write the game's own bone data in place) and `RiderWrite` (0 = hold but never write) tell the costs apart and are read again on every mount, and the trace's `time:` line gives the frame's cost in microseconds (the whole frame, the bike's part, the rider's, the skin sync, averaged and the worst) and the memory queries a frame. Test 26's A/B found the whole cost in those queries: one `VirtualQuery` costs about 100 µs on the tester's PC (the kernel sizing a region of a huge committed heap), the plugin's accessibility checks made 39 a frame with the rider held (3.5 ms, r = 0.98 against the frame time), 11 without, and 45 per skin sync (4.5 ms every 0.1 s, the hitch behind the 10 fps lost even with the tilt off). So the region cache (256 entries) is kept across frames and emptied only on a load or a new game, when the player's 3D root changes or a held shape goes; each entry lapses on its own 30 s and a stagger (its index in seconds, modulo 30) after it was read, and is read again when next asked for, so the re-check is spread over half a minute (test 27: a 5 s backstop's flush cost 23 queries a sync, 2-6 ms; test 37: the 30 s flush that replaced it re-walked the rider's 88 regions in one sync, a 12-16 ms stutter every half minute; the "time:" line's "(N at most)" is the most queries one sync made); the rider's per-frame path checks nothing (every node, skin and shape was checked when held, the shapes and skin instances are retained, and the 3D is walked again every 0.1 s; a bone whose node can't be read, or whose world transform can't be inverted, such as a hidden bone scaled to 0 (test 27: the backpack's bone 16 refused the whole shape and the rider stayed level all session), is left at its own transform and logged with its values, and the all-or-nothing rule is for bone data only; the correction uses a true 3x3 inverse rather than the transpose, since a cloth bone's world transform (test 28: the backpack's `Cloth_BN_Purse_*`) is sheared, not orthonormal, and such bones are carried along all the same); each sync also checks that a held shape's skin instance is still the one held and still points at the plugin's copy (test 28: a decal split from the suit after the game gave it a new instance), re-pointing it or holding the shape again with the new instance otherwise; a decal the game clones from a held shape, its skin pointing at the plugin's copy, is held from that shape's own level data (test 29: held from the tilted copy it would have tilted twice, and been pointed back at a frozen tilted copy at the let-go), bone data of the game's own that is a copy of the plugin's tilted entries is put level from the originals and treated as the original from then on, and the copies' reference counts balance the game's smart pointers (a reference taken for the instance when a copy is swapped in, the game's own dropped when it drops one), so a copy whose count is back at its base is reused rather than a new one taken each ride; the rider's block is cleared when a ride starts and on a load (test 27: it carried into the next ride when nothing was held at the dismount); the movement-output hook, which may run on another thread, remembers four regions of its own for 5 s; and the `time:` line counts the queries per sync as well. The rider's shapes are left alone while the tilt is within a deadband (level under half a degree, tilted again over one: the applied pitch wobbles a degree on ordinary ground). On getting off (or when the bike comes off, or the 3D is rebuilt) the original goes back and the reference is released. Which way round the game stores rotation matrices is read twice: the COM bike's bind is known (`[[0,0,1],[0,1,0],[-1,0,0]]` in the nif, the inverse of COM's seated bind), and the player's 3D root is turned only by the player's heading, which takes +Y to (sin h, cos h, 0); if the two disagree the bike isn't tilted. A skin entry that isn't a rigid transform is left alone. On the ground the normal also goes into `CMB_GroundNormalX/Y/Z` (Z = 0 otherwise), for parking.
- **The rider's copies and decals (F4SE plugin, since the 2026-11-01a build; it replaces the decal and reuse rules in the paragraph above):** test 47's "floating" rider (pose.jpg: upright, the arms out straight, "a restart fixed it") was the pool of 320 copies of the rider's bone data run dry at 19:55:00.981, after which every ride of the session stayed level. The plugin had held every blood decal of two fights, a copy each; the game put each decal back on its owner's copy at every sync (21,528 log lines, 31% of the log), and every such re-point moved one of two counts by one, a smart pointer's on the owner's copy or the plugin's own on the decal's, so no copy's count came back to the base and none was reused (453 holds against 320 slots, at least 176 stranded). Since then, each with its key in `[Tilt]` (read again on getting on; 0 is the 2026-10-31a build's way): **`DecalsFollow`** a skinned shape whose skin is on a held shape's copy or data with that shape's bone count (the game's clone of its skin), or that is named `Decal` and shares its data with another skin in the walk (a decal made before the ride, at its first sync), follows its owner and is never held, written or counted toward the 160 shapes (decals are listed apart, up to 160 of them); a held shape found back on another copy of ours is held again rather than taken for the game's copy (the old branch wrote the owner's copy level for a frame); one line a ride per owner names the followers and the first one's type. **`ReuseByWalk`** a copy is reused once no skin in the sync's walk of the player's 3D points at it and no held part keeps it, whatever its count (with more shapes than the walk lists, by the count as before). **`PoolWait`** a pool with no copy free leaves the rider level only until one is, the hold tried again every second; every getting off logs the census ("the copies: N made of 320, N held, N still pointed at, N free (counts over the base: a to b)", which tells which way the game re-points), counted before the copies are let go (N held: the ride's; the review of the 2026-11-01a build: it ran after, so always 0 held) and logged with nothing held too. **`OrphanRestore`** each copy remembers the game's data it stood in for (a copy made for a copy: that one's), with a reference of its own till the slot is taken again; a skin left on a copy no held shape owns (a shape the game rebuilt from a held one, test 47's 19:50:16.8) is held from that data and put back on it at the let-go, so the copy comes free; a decal held so is let go as a follower at the next sync and follows from then on (the review of the 2026-11-01a build: the sync's walk still had it on its freed copy, so it was held again at once, every sync, while the game left it there). The game pointing such a skin back at the orphan copy it had when held is put back on ours as a re-point of its original is, with the same lines (the checker's finding 2; since the 2026-11-02a build); before, the sync took the orphan for another copy of ours and held the shape again every 0.1 s. Let go while it is still there (with `RepointEveryFrame=0`, within 0.1 s of the game's re-point), it is put on the game's own data and the orphan's reference given back, as from ours ("rider: X's skin back on the orphan copy at the let-go (the game's re-point not undone yet): put on its own data (got off)"); before, it was left on the orphan ("... no longer points at our bone data: left as it is"). **`RepointEveryFrame`** every frame, before the rider is written, a held skin the game pointed back at its own data is put on ours again with the sync's counts; the let-go's line says in how many of the frames it was found so. `[Diag] RepointLines` (3) logs the first three re-points of each held shape a ride, then one summary every 10 s while any went unlogged and each shape's total at its let-go (0: every one logged, no summary: the 2026-10-31a build's lines with RepointEveryFrame=0 too; with it on, a re-point is caught every frame, so up to a line a frame per shape); `[Diag] RiderCopies` (320) sizes the pool (at most 640), a test hook. The harness's mode 18 (`decals`) plays logs.md's scenarios D1-D10 with the "game" re-syncing its decals every frame, each under both ways the game might re-point (a smart pointer's, a raw store), and reproduces the drain with the 2026-10-31a build's keys; D7b, a decal left on the body's copy of the ride before and never re-synced: held once from it, let go once, then following.
- **The clips' knees: the pose check and the seat watch (F4SE plugin, since the 2026-11-01a build):** every frame of a ride the bike is held in, from 1.0 s in, the plugin reads the higher of the skeleton's two knees (`RLeg_Calf`, `LLeg_Calf`, found by name under the third-person root once a ride, with a reference of its own) over the player's position. The nodes carry the clips' pose (the plugin writes its copies of the skins' data, never the nodes), so the reading is the same whether or not the rider is held, as in test 47's pose.jpg, where it wasn't. Seated it reads 60-68 in every one of the 212 riding clips; a standing clip's higher knee is 38 at the median and 55 at most; under `[Tilt] SeatKneeMin` (52) for two frames is off the seat, at or over it for two frames back on. With `[Tilt] PoseCheck=1` the global `CMB_RiderPoseOff` (0x877) carries the raw seconds the clips have been off the seat, 0 while on it and at a ride's start and end (and when no frame has measured for 0.3 s); the controller compares them with its own `CMB_PoseOffAfter` (3 s, longer than any stagger or hit reaction) and applies the riding pose again. `PoseCheck=0` never writes the global, so the script never acts on it; an ESP without the global gets one line, "rider: no CMB_RiderPoseOff (an older ESP): the pose check is off". In first person (the Pip-Boy too) the third-person skeleton stands, the knees at 38 from the first frame to the last (test 48: 47.6 s "off the seat", and the footstep watch gave up after 10 tries), so with `[Tilt] PoseFirstPerson=1` (since the 2026-11-02a build) the knees aren't measured there: a spell off the seat ends unlogged and `CMB_RiderPoseOff` reads -1 till third person, which the controller's footstep watch reads as "first person: leave its footsteps alone"; one line a ride, "rider: first person: the clips' knees not measured there (...): CMB_RiderPoseOff -1 till third person (PoseFirstPerson)", and the ride's total at getting off. The knee nodes are found again when ours is the last reference to them (a fresh 3D on the same root). `PoseFirstPerson=0` measures in first person too. The seat watch logs, with the bike on COM only (the ground-planted bind has no skirt), "rider: the clips off the seat (the knees up to 38 over the ground point, seated 65): standing clips at 140 a second (the rider held)" and "the clips back on the seat after 0.62 s", at most six pairs in 10 s and then a summary, and at getting off "off the seat N times this ride, T s in all, the longest L s (time)"; and once a ride, 1.0 s in, "the clips' hands L/R from the grips", a calibration line nothing reads.
- **Steering (F4SE plugin):** a person turns on the spot; a bike can't (test 10: pulling back spun it round and the rider rode towards the camera). Every frame while riding, `CMB_Slope.dll` lets the player's heading (`TESObjectREFR::rot.z`) change at most speed / R radians a second, or `CMB_StandTurnRate` degrees a second (MCM "Turning when stopped", default 60) when that's faster; the speed is the player's own, smoothed over 0.2 s. The radius grows with speed, R = R_slow + (R_fast − R_slow)·min(speed / 900, 1): `CMB_TurnRadiusSlow` at walking pace (MCM "Turning radius at walking pace", default 50 units) to `CMB_TurnRadius` at riding speed and above (MCM "Turning radius", default 180, about 2.5 m; 0 = off); `[Steer] FullSpeed` sets the 900. Test 11 found one fixed radius (300) "like a truck": too wide at low speed and when stopped, and about 60% of it wanted at speed; a save with the old 300 and 20 gets 180 and 60 once. Whatever the game turned beyond that in a frame is dropped, and next frame it asks again from where the plugin left it, so the camera can swing round freely while the bike follows at its own pace (test 11: no sliding sideways). Test 33: a key asks the whole clamp at once (the mouse asks a little each frame), and A/D made a snake; so the turning rate asked, clamped, eases in through a low-pass, and the heading moves by the eased rate, never beyond what was asked (no overshoot) and not at all while the eased rate still points the other way. Test 34: 0.35 s felt heavy; the low-pass is `TurnEaseIn` (0.14 s) while the rate asked grows the same way and `TurnEaseOut` (0.08 s) when the key is let go or reversed, and the lean's `LeanRate` is 50 so it keeps up. A door or fast travel (a jump of over 300 units) starts again from the game's heading. **Turning from a stop and reversing (input hook):** holstered in third person, the game turns the player to face where the move keys point (from the camera) and moves them forward along their facing. Test 12 showed what that does to a bike: a side key alone from a standstill drove it forward at up to full speed (median 200, up to 930 units/s) while the clamp turned it at 60°/s; holding back with the heading held drove it *forward* along the old heading (78 samples, never backwards). The move input is `PlayerControls::data.moveInputVec` (`g_playerControls` +0x44 x, strafe; +0x48 y, +1 forward, −1 back; found in test 11 with the trace's key presses, laid out as CommonLibF4's `PlayerControlsData`: look input +0x4C, normalised +0x54, last frame's move +0x5C and look +0x64). Written from the F4SE task it never took effect: the game sets it again from the held keys every frame and the movement had already used it (`prevMoveVec` read −1, not the −0.3 written). So the plugin now wraps the `MovementHandler`'s event functions: `PlayerControls::movementHandler` (+0x1E0, or found in its handler list at +0x90), checked to be exactly a `MovementHandler` (a struct in the game, `.?AUMovementHandler@@`, like all its input handlers: test 13's build looked for a class and never found it) whose data reference (+0x10) is `PlayerControls`+0x44 and whose vtable is where 1.11.240 has it (+0x2571B38; read off the user's Fallout4.exe, with the constructor setting +0x1E0 and +0x10 as above); three entries of its vtable are swapped (`OnThumbstickEvent` 4, `OnButtonEvent` 8, `PerFrameUpdate` 9, the same in F4SE's `BSInputEventUser` and CommonLibF4; in the game 4 and 8 are MovementHandler's own, 9 the base one), no code is patched, and the originals are logged. After each call the input is changed before the movement update reads it:
  - **back** (y < −0.2): (0, 0), so the game doesn't drive off. The plugin holds the heading and backs the bike up at `BackSpeed` (80 units/s); with a side key the rear goes that way and the nose the other (as a car reverses), round the walking-pace circle as it moves, at most at the stopped rate. The controls' output to the movement, `IMovementPlayerControls::GetControllerOutput` (`PlayerControls`+0x30's vtable, +0x2571AA0 in 1.11.240, entry 1), is wrapped too: its `PlayerControlsMovementData` (CommonLibF4) has movementRotation +0x00 (always 0 in test 14: along the facing), rotationSpeed +0x10 (z up to ±4 while turning), movementSpeed +0x20 (2 riding, 0.06–0.3 creeping, 0 with no input) and targetAngle +0x30 (z: the heading wanted, radians, absolute); while backing the plugin sets the target angle to its own heading and the turning and speed to 0. The game's movement only ever goes forward along the facing: test 15 turned it round (rotation z = π) and gave it a negative speed, and the player didn't move either way. Of the character controller's own, test 14 found `velocityMod` (+0x180) moved the bike −6 units/s, `SetLinearVelocityImpl` (vfunc 0x3A) not at all, and steps through `SetPositionImpl` (0x34) −75 units/s but through walls and objects; test 16 found `pushDelta` (+0x1B0) doesn't move it either (the game only adds to it from contacts and clears it). So `BackPush=auto` makes steps through `SetPositionImpl`, each only after rays cast with the game's own picking say the way back is clear, kept if the bike really goes back (more than 30% of `BackSpeed` 0.6 s into holding back, counted from when it has stopped rolling forward and not while something behind stops it), else back brakes:
    - the ground 55 units behind the rider (clear of their own body; at most 45° away) and under the rear, `BackClearance` back (test 16 found the vanilla bike's rear about 130 back, touching a car: 150; test 42, "way too far": with the Sketchfab bike, at 150 the bike stopped with 56 free behind the tyre at a rail, 20:55:53, and about 86 on a 33° slope, 20:59:43; so since test 43 the default, 0, is the rear tyre's back edge by the parts file, |`RearAxle` y| + `WheelRadius`, 70.4 on the Sketchfab bike, plus `BackMargin`, 25: the step's 4 at most, the ray's end being the point judged, and a hand's width, nothing on the bike overhanging the tyre, whose rearmost point is the mesh's, 70.3 back, the fender ending at 64.2; 95 in all, never under 60, so a stop leaves 25 to 29 free behind the tyre, and still 150 without a parts file, or with `BackClearance=150`, test 42's behaviour; logged once the parts file is read and at each push's start from a hand of 10, "reverse: the rear's clearance 95 from the parts file (the tyre's back edge 70 behind the rider + 25)"), and between them, following the ground so a slope isn't taken for a wall, nothing at knee height 20 units either side of the bike or at chest height in the middle (the rays for the ground, these two and the one under the feet below, pass through actors since test 40; the knee and chest rays don't, so Dogmeat behind still stops the bike). The feet follow the slope up or down. Level or going down, a ray from 2 units above the feet at the step point (the capsule's bottom is a hemisphere, so its skin is about at the feet there; if the ray starts inside it anyway and the player's filter reports that, the hit is at the start and goes unused, as does the ground at the feet) finds the ground under the step; more than 20 below is a drop: no step. Hung up since test 45 (test 44: astride the wooden road barrier at 22:47:42.9 the ground just behind the feet was 28 to 32 under them, and every push stopped "the ground drops away under the step, 1 units back" till the tester wriggled the bike off; after a grill at 22:54:03, 32): both wheels' rays finding the ground more than 10 under the feet (`WheelRays`: the capsule held up between them; a wheel's droop is 4) or forward stalled at a face at the capsule that isn't an actor (`ClimbRays`, so only with `Climb=1`), in the last 3 s and within 40 of where it was said (forgotten at a ride's start and on a load), the ray under the step reaches 60 under the feet (`BackHungDrop` + 20) instead of 38, and a drop of up to `BackHungDrop` (40) under it is stepped down ("reverse: hung up (both wheels' rays found the ground under the feet, 30 at the front and 30 at the rear, 0.4 s ago): the ground 30 under the step backed off onto (BackHungDrop 40; over 20 a drop otherwise)", or "(forward stalled at a face at the capsule (what, layer N, N ahead at 4), …)", a second apart at most); deeper, or nothing within the 60, is a drop still, the stop's line ending "(50 down, over BackHungDrop's 40 though hung up)" or "(none within 60 under the feet, hung up)", where up to test 44 a drop over 38 wasn't seen by the ray at all and the bike backed on. The rear tyre's ray (`BackLedge`, below) is as before. `BackHungDrop` (0, or 20 to 80: between them is read as 20) prints on a "  reverse:" line of its own ("  reverse: BackHungDrop=40: hung up (both wheels' rays finding the ground over 10 under the feet, or forward stalled at a face at the capsule, in the last 3 s and within 40 of there), a drop of up to 40 under the step is backed off (20 otherwise)"), read again on getting on, and 0 ("more than 20 under the step is a drop, hung up or not (test 44's build)") is test 44's backing. Since test 43, with a parts file and `BackLedge` (1), one more ray down where the rear tyre's back edge will be after the step, from 60 over the slope 55 back's line there to 60 under it (the line, not the feet: a 40° slope down puts the ground 59 to 62 under the feet there, which a ray to 60 under the feet would read as no ground, a stop the steps never made before): more than 20 under that line, or no ground, stops the bike with the tyre's edge a step short of the lip ("reverse: stopped: the ground drops away under the rear tyre, N units back (the ground N there, N below the slope 55 back's line)", "no ground under the rear tyre, …"), since with the clearance at 95 rather than 150 the rule under the step alone would have let the tyre hang 62 to 67 over a ledge first. On a slope the line follows the ground, and a 50° break between the 55 ray and the tyre reads 15 to 19 under it, no stop; a lip already between 55 back and the tyre's edge when the push starts reads to the 55 ray as a slope, and the rule under the step stops the bike there as before. No "too steep under the rear tyre": every clause is a new way to stop. `BackClearance=150` with `BackLedge=0` is test 42's backing exactly, the log aside. With `BackFollow=0` (test 40's rule; since test 41 it's below) a gap under the feet is closed only while the controller doesn't hold itself supported (its supported bit, 0x400 of the flags at +0x300, clear, or its state not on the ground): the feet go down to a hover of 0.5 over the ground (`BackSink`, 0, is how far below that hover), at most 3 a frame and never up; with the controller supported the gap is its own hover and the slope's step stands. Test 39, on a level road: all 15 gaps closed there (0.4 to 2.4 under the feet) came with the controller holding itself supported (state 0, the bit set), and each was followed by it in the air within 0.01 to 0.75 s, the player dropping 20 to 37 through the road's collision and climbing back over about 0.8 s, the bike sinking into the road, while backing with no step the gaps read 0.0 to 0.2, the controller's own hover; till then a gap of more than 0.3 was closed onto the ground (plus `BackSink`) whatever the controller said. Not uphill: there the ray would start inside a curb or the slope (a box is ignored from inside and the ray finds the ground beneath it, which would read as a drop on a slab or pull the feet into a curb), and the feet never float. The controller still says "in the air" much of the time while it's stepped (test 16: 15% of the backing, once for 3.5 s; test 17: 34%; test 18, with the feet pushed 1.5 units into the ground: 49%, 16 s on a 10° slope with its support normal frozen, and 3.3 s after a 20-unit step down with the feet long since on the ground), with no fall damage from it; what SetPositionImpl does to the proxy's support isn't known. So while the rays put the feet on the ground (within 4 units under them, or going uphill) their word goes over the controller's for the track and the pitch, with the slope behind as the ground's normal (level across), so the bike pitches with the slope it backs down and the track is there for parking; a guard that waited for the controller to land was taken out (it had been dead since fc5a278, and on that hillside it would have stalled the reverse for 16 s). The log's "rays:" lines show the gap under the feet, the step's dz, the rays' word and the controller's state, support count, fakeSupport, inAirPreMove and flags (CommonLibF4's +0x388, +0x43E, +0x442, +0x300), and `BackSink` and `BackSupportCheck` (its CheckSupportImpl after each step) are there to try (`BackWarp` was dropped: SetPositionImpl ignores its third argument, test 19). Test 19 (defaults) read 43% in the air on the hillside: state 2 goes with bit 0x400 of the flags clear and inAirPreMove 1, state 0 with the bit set; the bit is what CheckSupportImpl clears on entry and sets from the proxy's contact manifold, and the support count was 1–10 either way, so the rays line now also shows that bit, the proxy's manifold size (+0x18) and its +0x12C. A ray down through a pile of things passed through (a broken fence's bits, test 18) is followed up to 8 times, 4 units past each, and counts as a hit if that runs out (it read as no ground, a drop); not when the last thing passed was an actor (a ground ray's): each actor passed takes a try since test 40, and the point counted would be the actor's, a radstag's back read as the ground again, so that ray has found nothing (a pile of clutter under an actor still ends on the clutter). No steps either after 0.45 s in the air: it lands first (test 17: the state flips every 0.2 s on rough ground). Since test 41, going back level or down, each step follows the ground over `BackFollow` (10) units centred on the step's middle, the controller supported or not (test 40: "backing up makes the camera shake a bit", downhill only; the whole picture shook while the bike stayed put on screen, the background jumping about 5 px at 1080p at -80 a second, the bike's applied pitch smooth, 12.0 to 8.9 over 1.3 s, while the controller's own ground normal flickered between samples and the rays went between on the ground and not: the step took the slope 55 back while the controller held itself supported, on brows 4 to 19 units ahead of the ground under the feet, and once it said it was in the air the gap to close was mostly 0, in 47 of 69 such lines, so the game's gravity carried the bike down in hops, and the camera follows the controller's height). Two more rays down, from 8 above the feet to 52 below, 5 either side of the step's middle, give the slope, (behind − ahead) / `BackFollow`, and the step's dz is that times the step. Steeper than 50 degrees down or 27 up across the window is an edge, not followed; a window ray finding no ground keeps the last slope for 0.1 s, then takes the slope 55 back; and with the ground 55 behind less than 2 above the feet the way counts as level, not uphill (in the model, on a ripple the branch kept switching to uphill, where the steps only ever add, and the feet climbed 0.58 in 3 s). Unsupported, a gap is closed only down to the controller's own clearance (the gap it kept after a step while supported, averaged over 0.25 s and read afresh at each push's start, 0.5 at least, less `BackSink`), over `BackClose` (0.1 s), at most 120 a second and 3 a step, never up: at test 40's flips into the air (gaps of 5.3 and 2.0, its own) nothing is closed. Centred on the step's middle rather than its end, the window cuts a corner of 0.5 at most over a brow or a dip (0.58 at the end) and halves the drift long frames give on a ripple. Uphill keeps the slope 55 back, as before. The "rays:" lines (`Trace=1`) say how each step's dz was had ("follow N by the window (the ground N ahead, N behind over 10), own N, closing N", "held", "by the slope 55 back", "an edge"), a "height:" line after each splits the height change into the plugin's and the game's and gives the largest change of the vertical speed from one step to the next, the supported share and the controller's own velocity (`GetLinearVelocityImpl`), each flip of the controller's support is logged at most once a second, and each push's start with the capsule's size and the controller's gravity field (+0x330, raw). The settings print on their own "  reverse:" line (`BackClearance`, `BackMargin` and `BackLedge` on a second since test 43), read again on getting on, and the "rays:" lines give the clearance in use and the ray under the tyre ("… under the rear (95), +0 under the tyre (74)"); `BackFollow=0` gives test 40's rule back exactly. The camera's height is left alone: the plugin doesn't own it, the shake is the capsule's hops, and smoothing it would lag real drops.
    - with a side key the turn is checked first, along the heading it would turn to; if that way isn't clear it backs up straight, and if that isn't either it neither turns nor moves (test 16: turning without looking swung the rear into a car). Braking, or stopped, it doesn't turn at all.
    - the rays use the player's collision filter (`bhkPickData` castQuery filter info, +0x0C, set to `kCharController`, 30), and pass through only phantoms: triggers (12), acoustic spaces (21), actor zones (22: test 16 stopped at one on a flat slab, test 17 passed through it), projectile zones (23), gas traps (24) and door detection (37), and, since test 37, the phantoms the character controller's own collides-with list holds as well, which a tripwire or a gas cloud would present as a wall: spells (7), cloud traps (16), the query and pick layers 38 to 46, living-and-dead actors (52), trap triggers (54) and character bumpers (56); and what the capsule pushes aside or steps over: clutter (4), weapons (5), small debris (19), shell casings (25), dead bodies (32) and water (11: the ground ray then finds the bed, so deep water is a drop) (the hit's layer, +0xAC & 0x7F). Test 36 showed the pick's filter isn't the capsule's own: food bushes (layer 15, non-collidable), a fire truck's navcut shape (49) and a dog (8, biped), none of which the player walks into, read as walls and stopped the bike. So the solid set is the character controller's own collision layer record, `COLL` 0008877F in Fallout4.esm (`BGSCollisionLayer`: `TESForm`, 0x20 bytes, then `TESDescription`, 0x18 (a vtable, a file offset, a chunk offset and a localized string), then the collision index at +0x38, a debug colour, flags, a name and the collides-with array at +0x50, the record 0x68 bytes; test 37's build had the description at 0x10 and read 874 at +0x30, so the 0x10 and 8-byte layouts are tried after this one now and the log says what each read), read once a load at the rays' test and taken only if it validates (the index 30, 1 to 64 entries, each a `BGSCollisionLayer` with an index under 64; the log's "rays: the character controller's collision layer ... collides with layers ..." line lists them): a hit is solid only if its layer is in that list, the phantoms and the backed-over layers above still passed. Without a record that reads, the built-in table: everything but 8, 15, 49 and 64 and over (test 17: a chain-link fence is layer 26, transparent small, and is in the list). A hit on the rider's own 3D (the player's root or anything under it: the capsule, the body, the worn bike) is passed through: the face rays start at the player's position, inside the capsule, and test 36 read it as an obstacle a unit past their start, 125 behind the front wheel's edge, four times, the throttle held for a second each (the walk from the hit up to the player's root goes 24 parents since test 37: the arm bones sit 10 and more deep, past the 8 the first cut walked). The filter works as hoped: the world pick uses the world's own collision filter with the layer given at +0x0C unless `customCollideLayers` (+0xC8) is set (test 17, read in the game). The rays that look for the ground pass through actors too since test 40, their capsules (30, a layer the controller collides with) and bodies (8, passed by the solid set already): the wheels' two rays, the ground just behind and under the rear and the ray under the feet here, and the rays' test ray beside the bike (below); the face rays, `WallAhead` and the knee and chest rays don't, so an actor ahead or behind still slows or stops the bike (test 39's radstag: "a wall ahead ... (SkeletonExport, layer 30), the throttle eased to 0%"). A stop is logged with what was hit, its layer and where.
    - the picking is `bhkPickData` (ctor, `SetStartEnd`, which takes game units, `Reset`, `HasHit`, `GetHitFraction`) and `TESObjectCELL::Pick` on the player's parent cell (+0xB8), found by CommonLibF4's IDs in F4SE's Address Library (`version-1-11-240-0.bin`: a count, then {id, offset} pairs sorted by id; looked for next to the plugin and in the game's `Data\F4SE\Plugins`, since with Mod Organizer the plugin's folder is its mod's). Test 16 confirmed all six in the game, and that one reused `bhkPickData` holds exactly one Havok world reference (the pick adds one to the new world and drops the old). After every load one ray down beside the bike must find the ground about where the player stands, else back brakes and the test is tried again 3 s later (it passes through actors: a dog beside the bike isn't the ground, nor a reason to switch the rays off).

    `BackPush=ray`, `delta`, `mod`, `velocity` or `position` use only that one (`position`: test 14's steps without rays). Each load tries again.
  - **a side key alone, slow or stopped** (|y| ≤ 0.2, below `CreepBelow`, 100 units/s): (0, c), a crawl forward, while the plugin turns the heading at `CMB_StandTurnRate` × x. c is learnt while riding (up when slower than wanted, down when faster, at 1.5/s) so the crawl goes at the rate × `CreepRadius` (55 units: about 58 units/s at 60°/s; 25 after test 13's "barely moving forward", then a bit more after tests 14 and 15). Rough ground takes much more than the flat and is threshold-like (test 17: nothing at 0.53, 58 units/s at 0.62 on a rock; 0.10 on the flat), so the input may wind up to 1; stuck against something it winds up too, and once free the bike surged (test 17: 3.4 s at up to 336 units/s while the input decayed from 0.90). So when the bike goes faster than twice the speed wanted, the input is cut: wound up past the last value that crept at about that speed (as a rule the ground it was stuck on), to between half that value and it (what the speed says, input × wanted / speed, is often far too low: the quick estimate spikes as the bike pops free, and test 18 cut to 0.05 and 0.02 and crawled at half speed for a second); started at that value and surging anyway (the rock's value on the flat), to what the speed says; never up. Again 0.12 s later if still too fast, but not while the speed is still falling from the last cut (test 18's 0.07 → 0.02 was that) nor in the air (a fall isn't the input's doing). That last good value is learnt only while the speed is steady (a surge passing through the right speed doesn't poison it), is where the next creep starts from (test 18 started one from a cut 0.02, 1.5 s before it moved), and eases back to `CreepInput` over 15 s off the side key (rough ground's value would surge on the flat): the bike goes round a small circle instead of driving off. `Creep=0` turns it on the spot.
  - **anything with forward in it:** left alone (the speed-dependent clamp, which test 12 found right).

  Before each call the game gets back the value it last left there itself, unless something else changed it since, so this works whether the game sets the input or adds to it. Test 14 showed what "something else" is: the game clears the input to (0, 0) every frame outside these functions, then each held key sets its own half. A (0, 0) of the plugin's looked just like that clear, so the stale value went back in every frame: a side key let go of while backing stuck, into the creep afterwards too. The plugin's zeros are now written as −0.0 and compared bit for bit, so the game's +0.0 clear is told apart. Test 19 found that clear landing *after* the held key's event on some frames (two input batches in a frame, the key's event in the first, would do it): a later call then read (0, 0), the mode dropped to pass, the creep's wind-up was undone by the off-the-key rule, and the movement got (0, 0), every other frame for 3.5 s. So a (0, 0) reading within 0.2 s of real keys is taken as those keys still held (a key let go of lasts 0.2 s longer; a different key takes over at once; the keys kept are never what's given back to the game as its own value), and the input is written once more right before the game works it into the movement, inside the `GetControllerOutput` wrap, so a late clear can't reach the movement. The trace counts mode changes and says when the keys were kept. With `Trace=1`, every 0.25 s while backing or creeping the log says what the keys asked, what the game got, what its movement last used (+0x5C; test 14: always what the game got, so the timing is right) and where the bike went, and what the movement update got from the controls (the game's, and the plugin's when it changed them). If anything isn't where it's expected, the log says so and the keys are left alone (the plain clamp: back turns the bike round, slowly).
- **Camera (F4SE plugin):** `CMB_Slope.dll` also moves the third-person camera farther back while riding (`CMB_RidingCameraDistance`, default 450 units since test 6 asked for more than 300; the game's own is about 150; global values live in the save, so a save that still has the old 300 is moved to 450 once on loading). How far the camera normally sits is the game setting `fVanityModeMaxDist` (`[Camera]`), also the farthest the mouse wheel zooms out. The controller sets `CMB_CameraLive` while riding; the plugin finds the setting in the game's INI setting list, remembers the player's value, raises it (never lowers it) and puts it back afterwards. In memory only: no INI file is written. Papyrus can set INI settings (`Utility.SetINIFloat`, a vanilla `debugOnly` function) but nothing can read them, so restoring the player's own value needs the plugin; a first attempt as a Papyrus script called a `GetINIFloat` that doesn't exist. While getting on (under the fade) the controller goes to first person and back, in case the setting is only read when third person starts. Near trees the camera's collision still pulls it in. Getting on also zooms the third-person camera all the way out (test 8 asked for it) and getting off puts the zoom back: the zoom is a fraction (0 nearest, 1 farthest) in the game's `ThirdPersonState` (the camera's current state, or `PlayerCamera::cameraStates[7/8]`; `g_playerCamera` from F4SE), at +0xE8 (target) and +0xEC (current) by CommonLibF4's layout, which F4SE doesn't have, so the plugin writes them only if both read as fractions, logs them either way, and sets them for 2 s after getting on (in case entering third person under the fade puts the saved zoom back) and then leaves the mouse wheel alone.
- **Rider pose check:** once, getting on straight out of the water, the seated clips took about 13 s to appear. The seated clips have no footsteps and the standing ones do, so while riding the controller listens for the `FootLeft` animation event: footsteps while the rider pose should be on mean the switch hasn't happened, and it applies the flavour and `AttemptAnimationSetSwitch` again, every 2 s, up to 10 times per ride, logging each try. Applying it clears the flavour first, so it counts as a change even when a save already carried it. After loading a save mid-ride it's applied 1 s after the game is running rather than straight from `OnPlayerLoadGame`: right at load, `ChangeAnimFlavor` was refused once and only the footstep check (12 s later) fixed it. The footstep registration fails while the player's 3D isn't loaded, so the ride tick retries it. Since 2026-11-01a (test 47's floating rider, which was the plugin's bone-data pool running full, not the flavour: every ride from 19:55 was left level) the plugin also reads the clips: `CMB_RiderPoseOff` (0x877, its `[Tilt] PoseCheck`) holds the raw seconds the clips' knees have been under `SeatKneeMin` (52) over the ground point, which seated clips never are, and the controller reads it at every ride tick (`CheckRiderPose`): once it is `CMB_PoseOffAfter` (3 s, longer than any stagger or hit reaction) or more it applies the flavour again, sharing the footstep watch's count and 2 s gate, so a pose lost while the bike stands or turns on the spot (no footsteps) is caught within about 4 s. Both leave standing clips alone for `CMB_PoseReactionWindow` (3 s, the MCM's "Pose re-check pause after a hit") after a hit, an item used or while the stagger watch says staggered: those are reactions, not the pose lost (one line a reaction, "... a hit reaction or stagger, not the pose: left alone"); for it hits are watched while riding with "Thrown off when hit" off too, and the knock-off rule itself is still `CMB_DismountOnHit`'s. 0.6 s after the Pip-Boy closes a reading over 0.3 s applies the pose again at once (the Pip-Boy's round trip, one guess at test 47's stim "skirt"). `CMB_PoseReactionWindow` 0 is 2026-10-31a's footstep watch and no menu check; `PoseCheck=0` leaves the global at 0. Diagnostics, log only: "Hit while riding: ..." (one a second), "Used [Potion ...] while riding" (a remote `OnItemEquipped`), the Pip-Boy and favourites opening and closing, "Staggered while riding (Steady on|off)" from a stagger watch ability (`CMB_StaggerWatchAbility`, `IsStaggered`, given on getting on, taken on getting off), and the engine hand-over's ", N s after getting on" (19:56:25 of test 47 would have read 13.4: a stalled script engine). Since 2026-11-02a (test 48: eight staggers with "Steady in the saddle" on, four of four power attacks; the camera stuck after the first stimpak, Immersive Animation Framework's use idle cut 0.6 s in by the Pip-Boy check's re-apply) "Steady in the saddle" gives the perk `CMB_RiderSteadyWay` picks (1, `CMB_RiderSteadyPerk2`: Mod Incoming Stagger x0 with two condition tabs and entry point function 0, as the game's own `mod_armor_LessStagger`; 2, that game perk itself by FormID, 00245AFE, one step less; 0, the 2026-11-01a build's three-tab record) and takes off only what it gave (an armour lining's game perk is left alone: "... is on the player already (an armour lining's): left as it is."); the ride counts the hit events by others it is sent, their power attacks and the staggers ("Hit events this ride: N (M power attacks; one at a time: hits within about a tenth of a second of an enemy's are not seen), staggers K (Steady on: ...)", at getting off, for the A/B: the hit registration is one-shot and comes back after the hostile path's 0.1 s wait; with "Thrown off when hit" and the pose pause both off "Hits this ride: not watched (...)"); a stagger's end is logged with the plugin's reading half a second later ("Staggered while riding: the stagger over after N s; the clips back on the seat by themselves.") and nothing is done during it. An item used while riding opens a use window (`CMB_PoseUseWindow`, 6 s) from when its use clip can start (the use, or the Pip-Boy's or favourites' close when it was used there: an animation mod plays it after the menus close): no re-apply of any kind in it, `PipboyPoseCheck` included (it isn't even scheduled for that close), one line an item ("Standing footsteps 0.8 s after [Form <...>] was used: its use clip, not the pose: left alone."), and the item bumps `CMB_RiderItemUse` (0x893, 1-999 then 1) for the plugin's `UseLetGo`. 6 s after each use the camera's switch, looking and moving controls and `CMB_HotkeyF4SE`'s `Game.GetCameraState()` are logged ("After [Form <...>] was used: the camera switch on, looking on, moving on, the camera state 8 (third person)."); a camera left without its switch, or stuck in a transition, furniture or mount state (5, 9, 10), has its view entered again (`ForceFirstPerson` or `ForceThirdPerson`, `CMB_UseCameraFix` 1), checked again 2 s later, then the notification "An item animation still holds the camera: get off and on to free it." once a ride; the game's own views (1-4, 6, 11 and 12: VATS, a scope, dialogue and the like) are waited out like a menu at both checks, never forced ("After ... was used: the camera in the game's own view, state 12: not looked at (10 times)."). The footstep watch ignores first-person footsteps by the plugin's `CMB_RiderPoseOff` -1 ("Standing footsteps in first person: the first-person clips, not the pose: left alone (the plugin's PoseFirstPerson)."). `CMB_PoseUseWindow` 0, `CMB_UseCameraFix` 0 and `CMB_RiderSteadyWay` 0 are the 2026-11-01a build's.
- **Weapons:** fighting controls are off while riding (unless `CMB_AllowCombat` is 1), and that also blocks putting a weapon away. Getting on with a weapon out left it out for good: the weapon's standing animations took over, with no seated version, and the planted bike stayed behind. So getting on is refused with a weapon out ("Put your weapon away first."), whatever `CMB_AllowCombat` says, and if a weapon is out mid-ride with combat off, the ride ends. F4SE has `DrawWeapon` but nothing to put one away.

## Known risks

| Risk | Mitigation |
|---|---|
| Another mod's gear in slot 57 comes off while riding | Check with FO4Edit, change `BikeSlot` in the generator (see BUILD_GUIDE) |
| Hiding a companion during their own quest or a scene | Run-alongside is the default; even in ride-along mode, companions in a scene are left alone |
| The seated clips don't play | They need `CMB_RiderPose.esp` and its AnimTextData (`make_rider_pose.bat`); without them the rider runs in place over the bike, which is harmless |
| Hand-written AnimTextData differs from what the Creation Kit would write | Built from the copied entry's own Creation Kit files; only our clips' records change, in the same format (round-trip tested on 109 files, IDs reproduce a CK-built mod's). Root-motion keys within 1 unit / 0.6° of the clip |
| Another animation mod adds player entries later | Its entries aren't copied until `make_rider_pose.bat` runs again; until then the rider stands while that mod's entry applies |
| Remote `Activate` of the bag container doesn't open the menu | Fallback: move the container next to the bike when opening it (small script change) |
| Rider pose breaks animations | A flavour keyword only adds entries that need it, nothing else changes; `set CMB_UseRiderPose to 0`, untick `CMB_RiderPose.esp`, or `player.caf` (clear flavour) |
| Uninstalling mid-ride | Documented: dismount or reset first |
| Standing clips with the bike on `COM` | Any clip without a seated version shows a standing pose. Since 2026-11-01a staggers are off while riding ("Steady in the saddle", `CMB_RiderSteady`: a hidden perk, `CMB_RiderSteadyPerk`, Mod Incoming Stagger x0, added on getting on and removed on every way off and after a load off the bike; test 48: eight staggers got through it, so since 2026-11-02a `CMB_RiderSteadyPerk2`, two condition tabs as the game's own stagger lining, with `CMB_RiderSteadyWay` to try the game's perk or the old record). Hit reactions (HitReactionBehavior's 18 clips, a full state of MTBehavior's MTJump_SM) and idles other mods play on use still stand up for their length; the plugin logs each ("the clips off the seat"). The jump, fall and land clips are seated; without them (not extracted, ASSETS.md) a bump at speed swings the bike sideways. `set CMB_BikeFollowsRider to 0` avoids it |
| Engine sound silent | The sound file path format (`FX\CMB\...`, relative to `Data\Sound`) couldn't be checked against a vanilla record here. If it's silent, that's the first suspect |
| The engine sound's game side is unproven (test 44's build): a Papyrus instance id taken as the `BSSoundHandle`'s sound id, `FadeTo`'s attenuation as hundredths of a dB, the MCM's volume (`Sound.SetInstanceVolume`) as scaling that attenuation rather than replacing it, `SetFrequency` taking ratios over 1 (test 44 drove every set, 11 of 11 loops playing, and test 45's tester confirmed the attenuation and the volume by disassembly); since test 46 `BSSoundHandle::SetVolume` at +0x162E160, that disassembly's, not yet read from a real Address Library | The plugin asks `IsPlaying` of every loop before it takes a set and declines one where none plays; it counts every call that fails, lets go after 30 in a row on one loop (the script then plays its crossfade afresh) and pitches down only once a ratio over 1 is refused; its lines say each. A library without `SetVolume` there declines every set ("… doesn't match this game (ID 2267057 …, BSSoundHandle::SetVolume)"), and the crossfade plays. `[Sound] Drive=0` gives the crossfade, `PluginDrivesSound` false in the script test 43's two loops, except the death stop (`StopEngineAtDeath`) and the files' new audio (*Engine sound* below) |
| AP not refilling after rides (tests 45 and 46) | The mod never touches AP. `[Diag] APWatch` (test 46's build) logs the game's refill gates off the bike, read only; since test 47 the AP regen delay at `[[Actor+0x300]+0x10]+0x68`, AP's (test 46's build read +0x64, Stamina's: the build-27b check found the game's `GetRegenDelay` mapping AP to +0x68 and Stamina to +0x64, so that gate could never read shut), with no key: a plain fix. Test 46's AP test ran wholly after the console's `tai` (AI processing off), which alone stops every refill and every timed effect (`ProcessLists::Update` returns at once and nothing advances the actors' clock), and test 45's likely did too; so most likely there is no AP bug, and test 47 checks it with AI on (TESTING.md row 17r, with test 46's radiation indicator that stayed on) |
| MCM hotkey and the built-in F4SE hotkey on the same key | Toggles twice. The MCM help text says to set the built-in one to 0 |
| The ram's engine side is unproven: the actor behind a 3D at +0x110, `PushActorAway`'s force, the script's round trip | The plugin logs how it found the first actor of a ride (or why not) and each refused race with its flags, and brakes for anything without a yes; the MCM switch or `[Ram] Enabled=0` brakes for everyone, as before test 41. Since test 43 the robots' FormList is read as guardedly (a layout read wrong refuses the whole list, the gates standing: `Robots=0` does the same), and the script logs how far each pushed actor moved |
| `Kill(PlayerRef)` may give no experience on 1.11.240 (since 2026-11-01a the knock-over that takes an enemy's last health kills it, `CMB_RamKills`) | Test 48 confirmed it: 12 bike kills, +0 each. Since 2026-11-02a the killing hit is the player's `CMB_RamKillSpell` (MCM "Kill experience" 1, `Spell.Cast`; 2 `DoCombatSpellApply`; 0 `Kill(PlayerRef)`), with `Kill(PlayerRef)` 0.3 s later should it not kill, and the push's line gives the gain ("(+N: the game's, Spell.Cast)"); untested in the game. Before: The kill's line and the push's 0.5 s line ("dead, the killer the player, the player's experience A -> B") and the HUD's popup tell in one test; a "NOT dead after Kill" line means the engine refused it. Fallback, next round: a spell the player casts (`CMB_RamKillSpell`, a Value Modifier on Health), whose kill goes through a weapon's path. The MCM's "Knock-overs can kill" off is 2026-10-31a's (never the last point of health) |
| The game renames the bike's part shapes (since the 2026-10-31a build the needle, the lights and the mirrors are told by their names) | The role line on getting on says for each shape whether it was told "by its name" or "by its sphere"; with the names lost the riding bike looks as `[Parts] RolesByName=0` makes it (the needle at rest, the lights and the dial always lit, all three mirrors), nothing worse |
| Without F4SE or `CMB_Slope.dll`, or before the plugin's first frame of a ride, the riding bike shows every mirror variant at once, both lights' shells lit and the dial's backlight (the plugin hides them from its first tilt frame) | Known, not changed this round: the same dependency as 27c's lamp ring; the parked bike is unaffected; F4SE is needed for the moving parts anyway |
| The MCM's "Steepest slope while riding", "Riding camera distance" and "Bike tilts with the ground" all at 0 (each slider allows it): the plugin tells a ride by those three globals (`CMB_SlopeLive`, `CMB_CameraLive`, `CMB_TiltLive`), so it never holds the riding bike, and the bike shows as without the plugin: every mirror variant, both lights' shells and the dial's backlight lit, the needle at rest (27c's, the same setup: the wheels and bars still, the lamp's ring lit) | Known, not changed this round: any one of the three above 0 is enough (none is 0 by default); a ride signal of its own, a global the script sets on getting on, would need a script and ESP change. TESTING.md says so under the look's keys |
| Without the input hook the brake light comes on late, about a third of a second into a hard brake, near the stop (it reads the sound's measured speed, 0.2 s, and its rate, 0.25 s) | Known, not changed this round: with the hook (the default) it lights in the frame of the back key; a faster rate for the light alone is possible later |
| The mirrors show a daytime sky at night, if the game doesn't dim a cube's reflection after dark (untested) | Known: TESTING asks; a darker cube or a lower env scale for the mirrors' materials would fix it |
| `[Look] Mirrors` other than 1 gives the riding bike one style and the parked bike the stock one (the plugin never touches the parked bike's 3D) | Known, as designed this round: the parked nif carries the other two hidden for a later bench preview or swap |
| The mirrors' cube shows the sky sideways (no Fallout 4 file at hand says which face the game takes as up) | `Textures\CMB\Bike\mirror_cube_zup_e.dds`, the same sky with +Z up, copied over `mirror_cube_e.dds` (since 2026-11-02a the mirrors name the game's `Shared\Cubemaps\MetalBrushed02Cube_e.dds`, and our two cubes are only in the optional "2026-11-01a look (A-B)" folder) |
| The material files aren't found (a mod manager's folder, a typo) | The bike shows magenta (test 47: the game doesn't fall back to the nif blocks); install `Materials\CMB\Bike` with the meshes; `harley_meshes.py --bgsm 0` builds meshes that name none |
| A loading screen whose close never comes leaves a teleport pending (the ride's ticks wait for it) | Decided after 60 s of looks whatever else; a load starts the looks afresh; `DecideTeleportsAtOnce 1` for the old way |

## Spinning wheels and turning bars (F4SE plugin, the Sketchfab build)

Only `Root` and `COM` can move in Fallout 4 animations; every other bone keeps its fixed offset from its parent and can
only rotate. A wheel can only spin around a bone's own pivot, so animating one would need a bone on each axle, which
the skeleton doesn't have (a custom `skeleton.hkx` would have to be merged with every other skeleton mod). The tilt
went another way, and the moving parts ride on it: the plugin rewrites each worn shape's mesh-to-bone transform every
frame, which is a free rigid transform per shape, no bone needed. So `harley_meshes.py` splits the model into twelve
shapes: three static (metal, matte, glass), four that turn with the bars (the fork tubes, triple clamps, bars, grips,
levers, mirrors and headlight, by shading, the lamp's lit parts the fourth), three of the fork's lower end (the
sliders, the front mudguard, the brake caliper, the axle and the fork boots, by shading: they turn with the bars and
ride up and down with the front wheel's suspension travel since test 38, when the tyre went into the mudguard and
the axle left the fork ends at +10), and the two wheels (one matte shape each, black rims as on the real thing).
A piece goes with the bars (`role_of`) if its centre is no more than 16 behind the steering head (the forks, the
fender, the headlight; of those, the fork's lower end if its centre is below `FORK_SPLIT_Z`, 66 on the parked model,
the ground at 0: the sliders' centres are at z 41, the mudguard's 50, the caliper's 31, the axle's 30 and the rubber
boots' 63, the chrome fork tubes' 69 and the lower triple clamp's 86, so the line goes between the boots and the
tubes; compressed 10 the boots' tops reach z 80, a unit under the clamp), or up at bar height no more than 45 behind it (the risers, the clamp, the speedo, the mirrors
reaching back over the tank), or, off the centre line (|x| over 12), no more than 65: the grips, levers, switch
housings and the left mirror sit 45 to 57 behind the head on this model (the bars sweep back), and with one line at 45
they stayed with the frame while the bars turned (test 35: the hands turned, the grips stayed; 590 vertices of bar end
in the fixed shapes); the longer reach is for the sides only because the tank's chrome filler cap, on the centre line
55 behind the head, has its centre just above bar height too. `FrontMinY` (below) comes out of the shapes' spheres (the
fork's count with the bar assembly's), so the plugin needs nothing new for it.
Each shape's map in the bike's own space is a spin about its axle (the wheels), then the turn about the steering axis
(the front wheel, the lower fork and the bar assembly), then the suspension offset (the rear wheel along the bike's up, the front wheel and
the lower fork along the steering axis, scaled so the rise is the offset), then the tilt about the seat; mesh to bone is the bind applied to that, and
each shape's culling sphere is grown by how far the map moves its centre.

A piece is a wheel's by geometry, not by where its centre is: it lies inside the wheel's drum and either runs round the
axle (tyre, rim, disc, hub, pulley, 250 degrees or more) or is a spoke from the hub out to the rim on the centre plane
(test 20 sorted the spokes and rim bands by their centres and the rims seemed to spin away from the tyres); a brake
caliper sits inside the drum too, but off to one side and short of the hub, so it stays with the forks. The wheels'
pieces get 2.5 times their area's share of the triangles, being the roundest things in view. Two parts that meet along
a seam are decimated apart, and the simplifier doesn't keep a border where it is (a third of the tyre's border vertices
came off it), so the parts came apart along their seams (test 21: the tyre looked loose on the rim): each decimated
piece's border vertices are put back on the nearest original border vertex. A material's parts are welded together
first (a tyre's halves share the tread's centre line), and the model's single-plane bits are drawn double-sided.

**Since the 2026-10-31a build: 28 shapes, told by their names.** The model is split further for its textures and materials
(*The bike's look* below): 28 shapes a worn nif instead of 12, eight fixed (`static_*`), the tail and brake lights'
shells (`rear_*`), ten in the bar assembly (`front_*`: chrome, black, glass, the lamp's lit parts, the dial, its
backlight, the needle and three mirrors), four of the lower fork (`fork_*`) and each wheel's tyre and rim apart
(`wheelF_*`, `wheelR_*`). The plugin tells each one's role by its name first (`[Parts] RolesByName=1`; first fit
wins): a name ending `_front_needle` is the needle, `_front_glow` the lamp's lit parts, `_front_dialglow` the dial's
backlight, `_rear_tail` the running light, `_rear_brake` the brake light, `_front_mirrorStock`,
`_front_mirrorUnderEgg` or `_front_mirrorUnderD` a mirror of the bar assembly (`[Look] Mirrors` 1, 2 or 3), and a
name containing `_fork` is the lower fork, `_wheelF` or `_wheelR` a wheel, `_front_` the bar assembly, `_static_`
fixed; a name with no tag falls to the rules below (`_fork`, then the sphere), and 27c's own names give 27c's roles
either way. The roles that move need the parts file as before (without it nothing moves); the lights' and the
mirrors' specks don't. The names have to reach the plugin: test 8 saw the game rename the main worn shape, while the
part shapes have kept theirs since test 37 (the `_fork` rule has relied on it since test 38), and the role line on
getting on says how each was told ("CMB_BikeWornRider_front_needle is the speedometer's needle ... [needle, by its
name]"): one of the new labels "by its sphere" means the names were lost, and the bike shows as `RolesByName=0` does
with these meshes (the needle at rest, both lights and the backlight always lit, all three mirrors). The plugin held
16 shapes at most (twelve since test 38, `MAX_SKINS`) and silently left any more where they were (a frozen wheel or
bar part); it holds 48 now, its ring of refused shapes as many, and logs one line a ride naming any past the 48
("tilt: N bike shape(s) past the 48 this plugin holds, left where they are"). The 28 cost the plugin
about 9 microseconds a frame more than 27c's twelve (16.8 against 8.2 in the harness's fake game under Wine) (the trace's "time:" line says "bike <avg>/<max> for N
shape(s)"); the game's own cost is the draw calls, 28 where there were 12. And the lower triple clamp turns with the
bars now (it stayed with the frame since the Sketchfab build, the fork tubes turning through it): `role_of` measured
"16 behind the steering head" at the head's height, while the axis rakes back, so at the clamp's height (z 69 worn)
the axis is already 15.6 further back; a piece within 8 behind the raked axis at its own height, above `SteerPoint`,
joins the bar assembly now (six pieces, 1,340 triangles: the lower clamp, glTF mesh 74, its two pinch bolts and the stem nut under it, mesh 73, and a cable from the left bar, mesh 65; "16 behind the raked axis", tried first, took in the coil and wiring under the tank's nose too; 27c's rule decides everything else, and nothing new rides the fork's
travel). `FrontMinY` comes out of the shapes' spheres as before: 31.3 in 27c, 31.7 now (the under-bar mirrors' spheres at y 38.5 and `static_engine`'s at 24.9), every role
the same either way.

Which shape is what, the plugin tells by the culling sphere the converter writes into each shape's `BSSkin::BoneData`
(test 8 found the game renaming the worn shape, so names weren't relied on): a sphere on an axle is a wheel, one ahead of `FrontMinY` is the bar
assembly, the rest are fixed; the lower fork's three shapes, whose spheres sit ahead of `FrontMinY` too, the plugin
tells by the `_fork` in their names first (the Sketchfab bike's shapes keep their names, test 37's log shows:
"CMB_BikeWornRiderF_front_metal" and the rest). The axles, the wheel radius, the steering axis (through the fork tubes, raked 24 degrees
on this model), `FrontMinY` and, since test 39, `Grip` (the +x grip's centre, the wrist roll's pivot) come from `CMB_BikeParts.ini`, which the converter writes next to the meshes in the
worn bike's space; without the file nothing moves, and the vanilla bike, a single shape, never does. The wheels turn
by the distance ridden along the heading (`speedAlong / radius`, so they run backwards when reversing and stop at a
stop). The bars go over by the rider's turning: the heading's rate, smoothed over 0.1 s, its sign flipped while backing up (test 38: backing with a side key the rear goes the key's way and the nose the other, as a car reverses, so the bars followed the nose: "when going back and turning left motorcycle handlebars should also turn left"; the rear goes where the front wheel points), maps to the bar angle
(`BarAngle`, 20 degrees since test 20 asked for more than 10, full from `BarFullAt` 90 degrees a second since test 22, where at 45 every heading correction took them all the way while the straight-riding clips kept the hands at the straight grips; a creep turn from a stop at 60 is two thirds),
eased over 0.15 s, and to `BarAtSpeed` (0.6) of it from 150 to 400 units a second, since a bike's bars barely move at speed and
the game's lean clips, posed with the bars at that fraction, play then; the turn-on-the-spot clips have the bars at full lock. The riding clips keep the hands at the straight grips in every pose (since test 29; before, the lean, turn, start and
stop clips were posed with the bars turned and the hands at the turned grips, which put the hands off the bars in every
blend and heading correction), and the plugin turns the hands with the bars: the hand and finger bones' maps get the
bars' rotation about the steering axis (taken to world through the bike's bind and COM) in front of the tilt, and each
arm gets a two-bone solve (test 30: a forearm turned part way about the axis stretched at the elbow): the shoulder (the
upper arm's node) stays, the wrist (the hand's node) goes to the grip turned with the bars, the elbow (the first forearm
bone's node) swings to keep both bones' lengths (straight at most) in the plane `ArmPole` gives (1.1, -0.3, -0.9 in the bike's space for the right arm since test 41, the left mirrored in x, projected across the shoulder-to-grip line: out as much as down and a little back; test 38's 0.35, -0.3, -1.0 is mostly down, a little out and back; test 38: the elbows stood out at shoulder height, the arm running almost level from the shoulder, because the clips' pole pointed mostly sideways and the plugin kept the clips' plane, so every bit of bend the shorter reach added pushed the elbow further out, where riders on a bike of this shape have the elbows bent and tucked under the shoulders; 0,0,0 keeps the clips' own plane as before; test 40: at 0.35, -0.3, -1.0 the upper arm went down and forward and the forearm rose 14 to 18 degrees to the grip, where the tester's sketches have the elbows a little out and low and the forearms level, and his answer put the level forearm first. Both can't be had without moving the shoulders or the grips: the grips sit 9 to 11 below the shoulders, and an upper arm hanging straight down drops its whole 18.2. The pole only picks the plane about the shoulder-to-grip line, so poles that give the same elbow give the same arm, and how far out the elbow may go sets how flat the forearm gets: an emulation of the plugin's solve on the rig and the clips (within 0.6 degrees of test 40's first solve) searched about 1.0, -0.3, -1.0 for the flattest forearm with the elbow at most a unit further out than there (14.2; wide elbows were test 38's complaint), and at 1.1, -0.3, -0.9 the elbow is 14.1 out of the shoulder and 11 below it, the upper arm 37 to 38 degrees below level and the forearm rising 3.7 degrees to the grip at the walk clip and 5.9 at the run (1.0, -0.3, -1.0: 13.2 out, 12 below, 6.2 and 8.7; test 40's: 9 out, 15 below, 14.4 and 17.7), the wrist's turn from the clips' pose at the straight bars 17.5 and 16.2 degrees (10.8 and 9.8 at test 40's). The inside arm in a turn, on the side the bars turn to, whose grip comes back toward the shoulder, folds outward with the elbow out and its wrist turns more (52 degrees at 12 of the bars at the run clip, 31 at test 40's pole), so its pole fades to `ArmPoleTurn` (test 40's 0.35, -0.3, -1.0) as the bars turn its way, both taken as directions, all of it at `ArmPoleTurnBars` (10) degrees: the inside wrist 21 degrees at 4 of the bars, 24 at 8 and 31 at 12, the inside elbow coming in about 4 units over the first 10 degrees, the outside arm keeping `ArmPole` (its wrist 18 at 12, 29 at test 40's pole). The arm lines give the elbow from the shoulder, the upper arm below level and the forearm's pitch seen from the side, in the bike's space, with the pole used and the fade's share, at the first solve and, once a hold, riding over 300 for a second with the bars straight, the arms still and the lean final ("rider: the arms riding"); `ArmPoleTurn=0,0,0` or `ArmPoleTurnBars=0` is no fade, and with `ArmPole=0.35,-0.3,-1.0` test 40's arms exactly), and the upper arm's bones get
the rotation that swings the elbow, the forearm's (ForeArm1-3, ForeTwist1-2) the one that takes the old elbow-to-wrist
line to the new one. With no chain found for a side, its forearm bones get 0.55 of the turn as before; `RiderHands=0`
turns it all off. A cable from the bars to the engine goes with whichever side its middle is on, so its far end opens
a small gap in a turn. Shapes are held on any ride once there are moving parts, tilt setting or not.

The upper body (test 32: the clips pose the arms locked straight, the grips at 100% of the arms' reach, so a turn
put the far grip out of reach and the wrist stretched, the solver able only to straighten): the bones above the
pelvis (the spine, the chest, the collarbones, the neck; role 5) get a map of their own before the tilt, a forward
lean about the lowest spine bone's joint (SPINE1) by `TorsoLean` degrees, or, by default, by the least that brings
the straight grips to `ArmReach` (0.80; 0.88 gave 6 to 9 degrees in test 38, about 1.4% of the reach a degree, and the tester asked for more: "character should lean forward a bit more") of the arms' reach (a bisection over 0 to 30 degrees at the first frame a
chain is found, logged with the reach before and after), a twist about the vertical through that joint by
`TorsoTwist` (0.75) of the bars' angle, the chest turning the way the bars do (the far shoulder forward; test 36: at
0.4 the inner arm folded tight at full lock, its elbow out and back, the chest only 5 degrees round, while the inner
grip comes back by the grip's radius and the inner shoulder should go back with it), and a lean toward the inside of
the turn about the forward axis through the same joint by `TorsoSideLean` (0.25) degrees per degree of the bars
(test 36: "the body doesn't lean or shift sideways, so the arms have no room"); the sense of each rotation is
checked on a vector rather than assumed of the axis-angle routine. The wrist (test 37: with the hand keeping the clips'
orientation turned with the bars while the lean and the re-solved elbow swung the forearm, it read 25 degrees from
the clips' pose at the straight bars and 42 to 46 on the inner wrist with the bars 8 over): the hand, the fingers
with it, is rolled round the grip's axis (the bike's lateral axis through its bone, the bars' turn in front), so the
palm stays on the round grip and the fingers stay wrapped, and since test 40 the roll is the one that lays the hand's
long axis, seen along the grip, along the forearm (the solved elbow to the wrist), `HandPitch` (0) degrees above it
(+ = the knuckles up on either hand: about the bike's +x, so the left's angle about its outward axis is negated),
`WristRoll` (1.0) of the way. The long axis is the knuckle line, from the hand's joint to the middle finger's first
knuckle (`Finger31`, 7.6 units off in the vanilla skeleton's reference pose), 5.8 degrees off the bone's x and, seen
along the grip, 4.8 above it, toward the back of the hand. Test 39: "cat paw", the fists bent down at the wrist. The
roll was `WristRoll` of the forearm's own twist about the grip's axis, which kept whatever bend the clips gave the
hand against the forearm, and the clips gave the hand a fixed frame, the fingers 39 degrees below level whatever the
forearm did; once `ArmReach` 0.80 and `ArmPole` had the forearms about level, the bend showed (at rest the wrist
turned 15 to 17 degrees from the clips' pose, rolled 10 to 17). The clips lay the same axis along their own forearm
since test 40 (`HAND_PITCH` in `riding_anims.py`, 0, the match for `HandPitch`; ASSETS.md), so at 0 and 0 the plugin
keeps the clips' wrists and rolls a hand only as far as its own forearm swings from theirs. The pivot is the grip's
centre (`Grip` in the parts file; test 38: it was the hand's node, 6.5 units from the grip's centre, so the palm's grip point swung 2 x 6.5 x sin(theta/2) off the bar, 1.5 units at the ride's 13 degrees): the roll moves the wrist round the grip, so the arm is solved again to the wrist the roll puts there and the angle read off that forearm, a secant step on the angle still to go each pass (the wrist's swing turns the forearm back a little: in the clips each plain pass leaves about a seventh, in the harness about a quarter), till it is within 0.2 degrees, six passes at most, the pass nearest kept, its forearm the one written and its roll the hand's, so they meet at the wrist; with no Grip line the pivot is the hand's node, the wrist stays where it is, and one reading does. What
the arm's one-time log line carries is the roll, the hand's axis against the forearm's and the wrist's turn from the
clips' pose, the angle between the hand's map and the forearm's ("the wrist turned N deg from the clips' pose, the
hand rolled N round the grip, aligned with the forearm: its axis N deg above the forearm's seen along the grip
(HandPitch N)"), and at the ride's end a line per wrist says the largest turn of the ride, with the bars, the reach
and the roll at that moment (test 37's second line, at the first 8 degrees of bars, said nothing of the straight
bars' 25 nor of full lock), "on the steady frames" since test 40: the arm chains still (under 5 units a frame), the
grip at 50 to 103% of the reach, a second or more from the ride's start and from a jump of the player, and the clips
holding the hand at the bars, their wrist within 12 units of the grip's centre (the riding clips put it 6.5 from it;
without a Grip line that check isn't made). Test 39: the ride that ended in a fast travel into Diamond City logged
136.7 degrees at 101% of the reach and 161.0 at 116%, rolled 94.4 and -131.4, from menu or loading frames: the
Pip-Boy's map was open for the fast travel, the arms still for seconds at a time, the raise moving the clips' wrist
tens of units off the grip. Each arm is then solved from
the shoulder as the torso moved it (the chain carried rigidly first, the grip where the bars put it), its maps
composed with the torso's; the head's joint goes with the torso and takes the twist but neither the lean nor the side lean (the rider
keeps the head up and level), then the head-level counter-roll about the moved joint; plain shapes under those bones go along.
A bone whose name gives it no part takes its nearest ancestor's (up to 8 parents, as the head's own walk): the body's
skin helpers, Belly_skin and UpperBelly_skin under the spine, the breasts under the chest, the shoulder fat under the
collarbones, the upper-arm fat under the upper arm's twist bone and the rib helpers, were left where the clips put
them while the torso leaned and the arms swung (test 38's pose study, rendered on the real rig before test 39: at 14
degrees of lean the shoulders' verts strayed 7 units, a hump on the upper back and the shoulders caved in; 12 at 25);
the hold logs which bones took which part ("rider: ...: N bones with no part by name take their parents'").
With the torso active the rider is written every frame, level or not. `RiderHands=0` turns it off with the rest.

**Item uses: the hands let go (F4SE plugin, since the 2026-11-02a build).** Test 48's "food made arm stretched": an
animation mod's use clip (Immersive Animation Framework's, after the Pip-Boy closed) took the hand to the mouth while
the plugin held it on the grip, and the skin stretched between the held bones and the clip's. The controller counts
the items used while riding in `CMB_RiderItemUse` (0x893, fixed: the DLL reads it). A change of it arms a watch for
`[Tilt] UseLetGo` seconds (4): a hand of the clips more than `UseHandOff` (30) from its grip (riding they read 9 to
22), or the knees off the seat, is the use clip. While it plays the hands and the upper body's lean, twist and side
lean are the clips' and the rider only tilts with the bike, as with `RiderHands=0`; the hold is eased out and back in
over `UseBlend` seconds (0.3): the upper body's angles scaled, each arm bone's map blended with the identity about the
bone's own place (a normalised quaternion blend, exact at both ends). It ends 0.2 s after the hands are back and the
knees seated, or `UseMax` seconds (8) after the item. Props in a hand (the syringe) go with the hand, tilt and all: at
14 degrees of lean an untilted prop would float 24 units off it. With no use clip (no animation mod) nothing changes
("rider: no use clip within 4 s of the item: the hands held as they were"). The lean isn't solved while a clip plays
(a reading with the hand at the mouth would set the riding lean wrong for the rest of the ride), and in first person
the hands aren't read for the clip (the standing third-person skeleton would read as one at every item). Lines: "rider:
an item used (CMB_RiderItemUse 1): its use clip looked for over 4 s (UseLetGo)", "rider: the use clip began 0.42 s
after the item (the hands 43/12 from the grips): the hands and upper body the clips' (UseLetGo)", "rider: the use clip
over after 1.72 s: the hands back on the grips", and at getting off "rider: 1 use clip(s) this ride, the hands let go
1.7 s in all (UseLetGo)". `UseLetGo=0`, or an ESP without the global ("rider: no CMB_RiderItemUse (an older ESP): the
hands are held through item uses", once a session), is the 2026-11-01a build. In the harness's mode 13 (`arms`) the
plugin's frame costs the same with it on and off (92.6 and 95.0 us a frame).

**Items at speed, the food arm and other mods' items (2026-11-06a).** Test 49 at 12:17:45: the use clip took the
locomotion for about half a second (773 -> 189 u/s) and the `Lead` cap followed the speed down (0.95 -> 0.42), 1.4-1.9 s
more under 0.9 of the top. `[Steer] UseBlockAbove` (150): the animation graph wrapper `LandSoft` installs (the player's
IAnimationGraphManagerHolder, slot 1) also matches `[Steer] UseBlockEvents` (`dyn_ActivationAllowMovement`, up to 4
names) and returns false at speed, so the mod's `PlayIdle` fails (it retries 4 times 0.1 s apart) and the item is used
with no clip and no speed lost; recorded in the graph ring (the speed in its `sent`) and logged on the main thread, one
line an item with its retries counted ("rider: the graph's dyn_ActivationAllowMovement at 799 u/s (an item's use clip):
refused, the speed kept (UseBlockAbove 150); 4 more refused in the next 0.4 s (the animation mod's retries)"), "passed"
once a ride. `[Steer] UseHold` (2 s), the backstop: the seat watch's off-the-seat or the use watch's start at
`UseHoldFrom` (200) or more with forward held leaves the cap off (a cap that began to bind within 0.5 s undone to
`SlideRestore`'s), over at the earliest 0.2 s after the clips are back on the seat, as soon as the cap no longer binds
or the speed stops rising, at most 0.6 s more; ended by the back or brake key, forward let go, a face ahead or
`UseHold`'s time ("throttle: held at 1.00 through standing clips at 859 a second (an item's use clip or a hit's: the
Lead cap off for up to 2 s, UseHold)", the trace's ", use hold 1.3 s left"). The food arm (test 49 at 12:17:38): the
third-person skeleton's first frame after the Pip-Boy stands (knees 38, the hands 36/36; 14 such one-frame readings in
test 49, each within 0.011 s of "view: third person"), so `[Tilt] PoseViewSettle` (0.1 s) skips the knees and hands that
long after first person (`CMB_RiderPoseOff` -1 meanwhile, so the footstep guard reads -1 too), `[Tilt] UseRearm` (1 s)
takes a second clip start within `min(item + UseLetGo, end + UseRearm)` (test 49's real clip came 0.17 s after the false
end), and `[Tilt] UseBackTime` (0.4 s, 0.2 before) of the hands back and the knees seated ends a clip. Other mods'
items: `OnItemEquipped` leaves out a potion equipped with no menu open that is nameless or in no favourites slot (F4SE's
`FavoritesManager.GetFavorites`, through `CMB_HotkeyF4SE`, and a cache refreshed at getting on, after a load and at each
menu's close; a None list counts the item, as before): "Used [Form <...>] while riding: not from the Pip-Boy, the
favourites or a hotkey (another mod's item, a dummy's kind): left out of the use watch (CMB_RiderUseOwn 1)." The
console's `CMB_RiderUseOwn` 0 (0x8B6) watches every potion again. The off values (`UseBlockAbove=0`, `UseHold=0`,
`PoseViewSettle=0`, `UseRearm=0`, `UseBackTime=0.2`) are the 2026-11-02a build.

**Power attacks, and the build-49 check's findings 1, 2 and 5 (2026-11-06a).** Every power attack of test 49 threw the
rider off: the knock-off rule is now `knockOffs && ((power && CMB_KnockOffPower) || explosion || BigHit <= 0 || lost >=
BigHit)`, the MCM's Riding "Power attacks throw you off" (`CMB_KnockOffPower`, 0x8B5) off by default; a power attack
ridden through says so ("Hit while riding: power attack True, blocked False, lost 4.0% health since the last tick: not
knocked off (a power attack under Big hit's 10.0%: the MCM's Power attacks throw you off is off)."). Finding 1: off the
bike the lamp's reference is let go ("lamp: the light reference let go (got off): looked up afresh"): the lamp code runs
only with skins, so Hi/Lo 0 was never seen and the stale pointer was promoted at the next ride's first look. Finding 2:
`[Tilt] PoseOffRewrite` compares with the global itself, not the plugin's last word, so a script's 0 after a load or a
mount in first person is written -1 again ("rider: CMB_RiderPoseOff read 0, not the plugin's -1 (the script zeroed it: a
load, or getting on in first person): written again (PoseOffRewrite)"). Finding 5: the eye's far/near log on two
thresholds (out past `EyeMax`, back under 0.8 x `EyeMax`), the log only. Finding 4 (a companion's first ask in a fight
may be passed until its no) is left for a later build, its caveat as documented. Test 49's fall at 12:42:51 cost twice
test 48's curve (an 836 drop, 101 health, 2.0-2.3 x): TESTING asks whether the difficulty changed; nothing of the fall
code changed.

The lean is solved 1.3 s into the ride (`TorsoSolveFrom`; half a second before test 40: at test 39's ride starts the
reading at 0.8 or 0.9 s caught the getting-on still blending out, and a rider who rode off at once never gave another
reading of the riding pose, so that one was final) and again every half second till it is final, and each run of
readings keeps the solve from the largest reach seen: a reading has to beat it by half a percent (the same pose reads a
hair either way from frame to frame), and one of the riding pose, 99% or more, replaces it in any case, the later being
the more settled. The lean is final once two readings of the riding pose agree within a degree, or 3 s into the run with
the best seen (counted from half a second before the run's first good reading, if that came later: test 39's second fast
travel read 92% for 2.5 s). Test 33's first ride solved 15 degrees at 100% in the frame the rider was held, before the
pose had settled. Test 39: the last reading of a ride's first 3 s was final, and one ride's start ended final at 97%
(12.2 degrees) with 14.4 at 100% a second before; after a jump the first reading of 95% or more was final at once
(below); and at five of its six ride starts the first reading, 0.8 or 0.9 s in, read 100% with 15.9 to 21.1 degrees, the
getting-on still blending out (14.6 half a second later, all five times), so one reading of the riding pose isn't final
on its own. Not while the arm chains' joints are on the move (over 10 units in a frame, relative to the bike's bone) nor
while the grips' distance as the clips pose it is under 95% of the arms' reach (the riding clips put them at 100%; a
menu or a raised arm poses them nearer: test 37's tester opened the Pip-Boy a second after getting on, the arm bones
moved 40.7 in a frame, the grips read 82% and the 0 lean solved from that stuck for five minutes, through a fast
travel); the short reach is logged once ("not solved yet") and tried again every half second, and after 20 s of it the
solve is taken as it comes (another mod's clips may pose the grips nearer), and not as final: the reach is measured
again every half second, the lean solved again when it moves by over 3%, and once the riding pose is there a fresh run
of readings starts from it, the best kept as above ("the riding pose came: solved again"; test 38: a Pip-Boy held open
over 20 s right after getting on would have locked the 0 lean in for the ride). The solve starts afresh after a load and
whenever the whole rider is let go and held again (a knock-off, the skeleton wait), and again, the lean kept meanwhile
and a fresh run of readings begun, after a jump of the player over 300 units from a ground frame (a door, a fast travel:
test 38 found a fast travel on the bike leaves the rider's shapes held and loads nothing, so the lean was never solved
again after one; 300, the steering's own door and fast-travel threshold, not the park track's 150: a hop at speed lands
over 150 from its last track point, and a cell load's stall can carry a frame that far, so neither counts). Since test
40 the run after a jump starts from the solve before it, when that came from a reading of 95% or more and wasn't taken
as it comes: a reading has to beat it by the half percent, or be one of the riding pose (which replaces it, final at
once if it agrees within a degree with a kept solve of the riding pose), and 3 s on the kept solve is final as it
stands. Test 39: the grips read the riding pose's 100% only with the bike stopped (96 to 98% riding), and both fast
travels arrived moving, the grips at 92 to 95%, so the first reading of 95% after each was kept, 11.1 and 11.4 degrees
for the rest of the ride against the riding pose's 14.6, and a run started from nothing would still have ended final on
a moving reading, 11 to 12 degrees. A solve taken as it comes isn't kept (test 38's Pip-Boy start at 82%): after the
jump the readings start from nothing. The final lean is always logged: the leaned line says ", final" (and, after a
jump, "solved again after a jump of N units (a door, a fast travel)"), or, 3 s into a run with no better reading, "the
upper body's lean final at N deg, solved at N% of the reach as the clips pose it, the best reading of the T s since" the
ride's start, the jump, the riding pose came or the rider held again (the seconds from the run's real start), or, the
kept solve standing after a jump, "the upper body's lean final at N deg: the solve from before a jump of N units (a
door, a fast travel) stands". The fingers (test 33: the tips of both hands stretched into spikes two or three finger
lengths long since the plugin began moving the hand bones, test 30): the hold now logs each hands shape's bones with
their part and their node's distance from the hand's, and the trace carries the arm bones' biggest move between frames,
to tell a bone that isn't mapped like the hand from a node the game rewrites after the plugin reads it. Test 34's dump
named the cause: of the hands' 36 bones only the two hand bones have a node; the 34 finger and forearm bones live only
in the actor's flattened bone tree, so the plugin left them where the animation had them while the palm went to the
grip, and the skin between was the spike. F4SE's `BSSkin::Instance` keeps the nodes at +0x10 (null for those) and, at
+0x28, a pointer to every bone's world transform, node or not (`worldTransforms`); the plugin reads the bone array where
its entries are NiAVObjects and the other array where its entries read as transforms (`SkinBoneTransforms`), holds a
bone with no node through its own transform (`TransformWorld`: the rotation, the position at +0x30, the scale at +0x3C,
as a node's world transform at +0x70 is laid out), and gives it its part once every shape is held by where it sits
(`NodelessRoles`; since test 41 first by the node it sits on: a bone within `NodelessNear` of a node that has a part, 2
units, takes that node's part, the nearest if several, and is written by that part's map through its own transform; the
nodes with a part are gathered once a hold from every held shape, the arms' chains, the head and the spine named too;
then, on no such node, by the hands' nodes as since test 34: within 30 of a hand and beyond it, away from the elbow, a
finger with the hand's part; behind it along the forearm within the forearm's length, the forearm's; anything else is
carried with the tilt alone), logged per shape: "rider: shape: N bones without a node, held through their own
transforms: N with the left hand, N with the right, N with a forearm, N carried with the tilt alone, N with the head, N
with the upper body, N with an upper arm; N placed by the node they sit on, within 2 of it (NodelessNear): the head N,
the upper body N, the hands N, the forearms N, the upper arms N" (the old fields first, in their old order; "none placed
by the node they sit on (NodelessNear=0)" with it off). Test 41: the vanilla Hard Hat (`FHardHat:0`, 780 verts) is
skinned to HEAD, 28.5% of the weight, the front, and to Head_skin, 71.5%, the dome and the back, HEAD's child at (0, 0,
0) in the skeleton in use and a bone with no node in the rider's skeleton; so the hands' rules carried it with the tilt
alone ("1 bones without a node …: 1 carried with the tilt alone" at every hold) while HEAD took the upper body's lean,
about 14 degrees about SPINE1, and the level head, the dome stayed where an upright head would be and the front followed
the head forward: "helmet is sitting in 'default' position being stretched forward with character tilt". The glasses
(`FGlasses:0`) and most vanilla headwear are weighted to Head_skin the same way, and Neck_skin sits on Neck for collars
and scarves. On their node they take its part now (the hat's line: "1 with the head; 1 placed by the node they sit on"),
written as the node's own, so the hat moves in one piece, and a helper of the hands' skins on a hand's node the hand's.
2: the skin helpers sit on their node, and the nearest node-less bone the hands' rules are for, the wrist end of the
forearm, is 6 from the hand; `NodelessNear=0` (read again on getting on with the other rider switches) is test 41's
build. A side whose hand is found but whose shoulder or elbow is missing is a half-built skeleton (test 35: the first
hold after a save load ran 0.1 s before the game replaced the shapes, found both hands and neither shoulder, and the
suit had 49 bones without a node, 43 of them carried with the tilt alone; the re-hold found everything): nothing is
held, the hold is tried again every 0.1 s for up to a second, and then held as it is, once a ride (a skeleton that lacks
a shoulder for good isn't waited for again at every re-hold); the hands' bone listing is logged once per hold that
stands, from the sync, so a hold that waited lists them once. The trace's jump stat is relative to the bike's bone now
(the bike's own motion swamped it). The grip itself moves out to x 24.5 in the clips' fit (the hands sat 7 units inboard
of the bar ends, at the lever clamps), which widens the arms.

The headlamp (test 29's wish): the model's own was a plain can whose centre sat 20 units behind the steering head, past
`role_of`'s 16, so it never turned with the forks. `harley_meshes.py` drops its pieces (the lens, two bezel rings, the
face and the bucket: everything wholly inside the lamp's cylinder) and lathes a 5.75-inch LED unit in their place, 15
units across on the fork bracket, in the bar assembly: a gloss-black bucket, a chrome bezel and reflector dish, a
projector with a lit face, a lit running-light ring and a shallow glass lens (the lit parts are a `glow` kind:
`Own_Emit`, the emissive colour white at 6, no reflection, so they show whenever the bike does). The lit parts are a
shape of their own (`front_glow`, told by a culling sphere under 12 units within 20 of the parts file's `LampPoint`) and
the plugin shrinks it to a speck through its skin map while the lamp is off (test 30: the ring shone day and night); the
parked nif has them plain white. Since the 2026-10-31a build the shape is told by its name first (`_front_glow`) and the
speedometer's dial is lit with the lamp: its backlight (`front_dialglow`, *The bike's look*) is shrunk to a speck in
place (about its own centre, so it stays inside the dial) whenever the lamp's parts are, and always with `[Speedo]
Backlight=0`; the ring keeps 27c's speck about the bike's origin. The beam is a real light. The first try hung it on a
`BSValueNode` under the worn nif's root (an ADDN record's light goes on a value node whose value is the record's node
index: `CMB_Headlamp` 31985, a plain spotlight, warm white, radius 1400, 55 degrees, fade 1.5, dynamic;
`CMB_HeadlampShadow` 31986 the shadow-casting kind), and test 30 showed the game keeps only a worn nif's skinned shapes,
lifted straight under the actor's 3D root: the node never reaches the player's 3D. So the controller script places the
light as a reference (`PlaceAtMe`, the shadow-casting one with the MCM's switch) on getting on, disabled until the lamp
is lit, deleted on getting off, and tells the plugin its form id in two globals (`CMB_HeadlampRefHi`/`Lo`, 0x843/0x844,
the high and low 16 bits: a float global holds 16 bits exactly, not a 0xFF-prefixed id); the plugin looks the reference
up, and every frame writes its 3D root's local and world transforms to the lens, taken through the same map as the bar
assembly's shape (the bars' turn, the tilt, the lift, the bind, the COM bone), the beam down the root's `BeamAxis` (+X
by default, Gamebryo's light direction, an INI setting because it's untried) dipped `Pitch` degrees, and carries the
world transforms beneath it along (the game doesn't walk a still reference's 3D every frame). A save loaded or a new
game makes new forms, so since the 2026-11-02a build the plugin lets go of the light reference's pointer at the load and
looks the id up afresh ("lamp: the light reference let go (a save loaded): looked up afresh"); before, with the same id
after a load, it read and wrote through the old one (the checker's finding 1; test 48 had no load mid-ride). The value
nodes stayed in the nifs a while (under the bone the bike hangs off, then in the lamp piece below), in case nodes named
for a bone were kept: a node the game does keep is placed the same way (its hidden flag, NiAVObject's flags bit 0 at
+0x108, cleared; +0x100 is the collision object, which test 30's build wrote to) and the reference is parked 20000 below
then; no nif carries them since test 35, and that path is dormant. `CMB_HeadlampLive` (0x83D) says whether it's lit: the
controller script sets it from the MCM's mode (off, on, on at night: 19:00 to 6:30 by `Utility.GetCurrentGameTime`) on
getting on, every tick and on getting off, enabling or disabling the reference with it, and the MCM hotkey toggles the
mode. The MCM's actions are global functions on `CMB_MCMRelay` (`CallGlobalFunction`), which fetch the controller by
form id: MCM's `CallFunction` picks any script on the quest (tests 30 and 31 saw it land on `CMB_HotkeyF4SE` and
`CMB_GearRestoreF4SE`), so those two scripts relay the calls too, and `CMB_RamScript` (the quest's fourth script since
test 41) relays them for console calls. What the game attached to the reference's 3D is logged (`lamp:` lines). Test 31:
the placed light was found and moved, and lit nothing, even straight from the console; the records were far from the
game's own (constant attenuation 1 where every vanilla light has 0, radius 1400 against the power armor lamp's 1420 with
fade 1.27 and a 70-degree cone, near clip 10), so they're made like `defaultPowerArmorHeadlampLight` now (radius 2130,
70 degrees, near clip 10, constant 0, scalar 1, exponent 2, fade 2), and the plugin writes the reference's world bound
(+0xB0) along with its transforms, since the renderer culls by it. Second try alongside, on the tester's lead (the
Pip-Boy flashlight mods light from an unskinned worn mesh): an unskinned lamp piece, `CMB_BikeLamp.nif`, a second armor
addon on both bike armors (`CMB_BikeRiderLampAA`, `CMB_BikeRiderFrameLampAA`): one three-vertex speck of a shape so the
nif isn't empty, and the two value nodes at the lens under its root. Unskinned, it goes under the actor's 3D as it is,
nodes and all, so the engine's own ADDN path should light its nodes; the plugin finds them by name and places them at
the lens the same way (the reference is then parked). Test 32 answered: the placed reference lights (the record's values
did it), and the lamp piece never arrived. The reference's beam went after 25 s of riding: the reference stays in the
cell it was placed in, the plugin moves only its 3D, and that cell unloads behind the bike; so the controller's tick
moves the reference into the player's cell whenever the player's cell differs from its own (`MoveTo`), and to the player
if its 3D is gone while the lamp is lit; the plugin logs when the reference's 3D goes while the lamp is wanted and when
it's back. Test 33: every `MoveTo` reloaded the reference's 3D and the beam flickered, 67 times in 8 minutes. So the
reference is left where it is until the bike is two cells from the cell it was placed in (the loaded grid reaches two
cells out), and then the controller places a fresh one at the player instead (`HandOverHeadlamp`: lit if the lamp is,
its id into the globals, the old one deleted 2.5 s later); the plugin keeps the old one at the lens until the new one's
3D is in, parks it then, and drops it, so the beam never goes out between them. The lights themselves reach 3000 at fade
2.4 (the tester's ask: further and a fifth brighter). Test 34 measured the remaining flicker: 13 events in 110 s of
night riding, one to three frames each, none at a handover, every one on a frame with a bump lift, a pitch spike or a
turn at full speed; on those frames the light, written from the bike's transform of the frame before, sat 10 to 60 units
behind the lens inside the lamp housing, and the bike shadowed its own beam. So the light goes `Ahead` (28) units along
the beam from the lens, outside the housing, moved on by `Lead` (1) frames of the bike's speed along the heading, the
old light of a handover stays at the lens `HandoverFrames` (5) frames after the new one has its 3D, and the bar
assembly's, the lower fork's and front wheel's shapes cast no shadow (the nif's shader flag), so nothing of the bike's
front end can shadow the beam. The records reached 4000 at 85 degrees and fade 2.7 after test 34 (further and a bit
wider at the same brightness); test 35 found the beam a bit too wide and a little too bright, so they are 78 degrees and
fade 2.4 now, the radius 4000 kept. The no-shadow flag is the worn nifs' only: `harley_meshes.py` cleared it by name in
every output, so the parked bike's front end lost its sun shadow too (test 35); the parked bike has no beam to shadow
and keeps it. The lamp piece (tests 32 to 35): the biped keeps one part per slot, and it shared the bike's, so it got
its own (slot 58, `LampSlot`, which `CMB_GearRestoreF4SE` restored like 57) and, like the Pip-Boy's mesh, a `Prn` string
on its root naming the bone to hang it on (COM for the seated bike, `AnimObjectA` for the planted one: three nifs,
`CMB_BikeLamp.nif`, `CMB_BikeLampF.nif` and `CMB_BikeLampFrame.nif`), its nodes at the lens in that bone's space through
the bike's own skin-to-bone transform, their +X down the beam, `BSX` flags for add-on nodes that move, and a
`P-AttachLightOverride` connect point at the lens (the way a helmet lamp takes the Pip-Boy's light over). The hotkey
(test 32: it wrote the MCM's mode, so one press wiped "On at night" and the lamp lit by day) is a say of its own now,
`headlampOverride` in the controller: off or on while riding, cleared on getting off and whenever the mode's own answer
changes (dusk, dawn, the MCM). Test 33: the piece still never reached the player's 3D, and the Pip-Boy's light stayed on
the Pip-Boy; so the plugin's walk said once a ride whether anything named `CMB_BikeLamp*` was on the player's 3D at all,
and `CMB_GearRestoreF4SE` logged what the biped held in slots 57 and 58 once the bike was on (`GetWornItem`), to tell an
unworn piece from one the engine loaded and dropped. Test 34: "Slot 58: nothing" and nothing named `CMB_BikeLamp*` on
the 3D, every mount, in the frame the bike went on; test 35 read the slots again two ticks in and got "Slot 58: nothing"
there too, so it was no timing gap: the game never took the addon. The placed reference meanwhile, 28 ahead of the lens
and led a frame, the front end shadowless, rode 3.5 minutes of night with no blackout, with shadows and without. So the
lamp piece is dropped: the two armor addons (`CMB_BikeRiderLampAA`, `CMB_BikeRiderFrameLampAA`), the slot, the three
nifs, the gear-restore script's slot-58 handling (it still logs slot 57; since test 41 a tick after the equip rather
than at it: read at once it said "Slot 57: nothing" twice, 16:00:13 and 16:01:37, while the bike showed, the biped not
having taken the armor yet), the plugin's `CMB_BikeLamp*` sighting line and the tick-2 slot read. The ADDN records
(`CMB_HeadlampAddOn` and `CMB_HeadlampShadowAddOn`, node indices 31985 and 31986) and the plugin's add-on-node path
stay, dormant: no nif carries those indices now, and the reference path that works is left as it is.

Up to 27c the shading had no material files: each shape's `BSLightingShaderProperty` carried its textures and flags,
the metal ones environment-mapped with the game's default outdoor cubemap. Test 20 showed the first palette's chrome
(light grey, full specular, full mask) as flat white in the sun: a bright cubemap reflected in full is white. Chrome
was then a mid grey with the reflection at 60 per cent, the headlight lens darker and duller, and the tank badge satin
black instead of the tan that showed as a patch. Since the 2026-10-31a build every shape names a material file and has real
textures: *The bike's look*.

## The bike's look (since the 2026-10-31a build: textures, material files, the speedometer, the tail and brake light, mirrors)

The tester's notes after 27c: "work on model of bike itself - to make it the best it can look, and if
possible with actually working speedometer, mirrors and back light". Up to 27c the model was coloured by part name:
the download has no textures, so `harley_meshes.py` gave every vertex of a material the centre of that material's
block in a 128 x 8 palette (fourteen blocks), which left no texture detail at all, a flat normal map and meaningless
tangents, in twelve shapes with no material files, the smoothness written as Skyrim's 0-999 glossiness (90, 30, 110,
30: out of Fallout 4's 0..1, part of why everything looked uniformly shiny). Since the 2026-10-31a build the bike has real
UV-mapped textures, a material file per shape, a speedometer whose needle the plugin turns, a tail light lit while
riding that brightens on braking, mirrors that show a sky, and two more mirror styles to choose from. The workbench
customisation (colours, parts) is for later, and this build leaves its hooks: one material per surface a player might
recolour, the paint kept as a layer of its own, the tyre and rim apart, the variants mechanism and the plugin's room
for 48 shapes.

**The shapes.** Each worn nif has the 30 shapes below (28 up to the 2026-10-31a build: the brake discs became shapes of
their own in the 2026-11-01a build), named `<stem>_<label>` (stems `CMB_BikeWorn`,
`CMB_BikeWornRider`, `CMB_BikeWornRiderF`), split by what the shader needs (chrome and paint want different cube
maps) and by what a workbench may one day swap. The parked nif has 27 of them, named `CMB_Bike_<label>` (27c's parked shapes
had another stem): not the two lights' shells nor the dial's backlight, which light only on the riding bike; the
two under-bar mirrors are in it hidden by their node flag (ready for a bench preview or a parked swap), beside the
vanilla shape, hidden as before. Since the 2026-11-01a build the same 30 are also in `CMB_BikeView.nif`, the bike in
first person (unskinned, under a hidden node; *Stages* below).

| label | moves as (plugin role) | what | shader, cube x scale |
|---|---|---|---|
| `static_paint` | fixed | tank, rear fender | env, dielectric x0.5 |
| `static_chrome` | fixed | covers, filler cap, tail bezel, plate frame, bolts | env, chrome x1 |
| `static_exhaust` | fixed | both pipes and mufflers | env, chrome x1 |
| `static_engine` | fixed | crankcase, cylinders, heads, air cleaner, covers, starter, oil filter | env, dielectric x0.3 |
| `static_black` | fixed | frame, swingarm, plate and housings, the other black parts | default |
| `static_seat` | fixed | the seat | default |
| `static_glass` | fixed | tail lens, rear signals' lenses, rear reflectors (alpha, as 27c) | env, glass x1 |
| `static_badge` | fixed | the tank badges and the rear emblem: our own winged wheel and roundel (alpha test) | env, chrome x0.8 |
| `rear_tail` | running light (TAIL) | a shell 0.25 over the tail lens | glow, deep red x2.5 |
| `rear_brake` | brake light (BRAKE) | a shell 0.5 over the tail lens and both rear signals | glow, deep red x8 |
| `front_chrome` | bars (FRONT) | bar chrome, the lamp's bezel and reflector, signal housings, the clamp's bolts | env, chrome x1 |
| `front_black` | bars | bars, grips, controls, risers, both triple clamps, the speedo's cup, the lamp's bucket | default |
| `front_glass` | bars | front signal lenses, the lamp's lens (alpha) | env, glass x1 |
| `front_glow` | the lamp (GLOW) | the lamp's LED ring and projector face, as 27c | emissive white x6 |
| `front_dial` | bars | our dial face and its hub cap | default |
| `front_dialglow` | the dial's backlight (GLOW + backlight) | a lit copy of the face's marks, 0.25 over it | glow, warm white x1.5 |
| `front_needle` | the needle (NEEDLE) | the needle and its counterweight, 0.5 over the face | glow, orange x1.5 on the blade (its own material: the dial's art and a glow map), lit always |
| `front_mirrorStock`, `front_mirrorUnderEgg`, `front_mirrorUnderD` | bars, `[Look] Mirrors` 1, 2, 3 | the model's mirrors; the two under-bar styles | env, our mirror cube x2.0 (x1.5 up to the 2026-10-31a build) |
| `fork_chrome`, `fork_paint`, `fork_black`, `fork_glass` | lower fork (FORK) | as 27c's three fork shapes, the front fender's paint apart | as their kinds |
| `wheelF_tyre`, `wheelF_rim`, `wheelR_tyre`, `wheelR_rim` | the wheels (WHEEL_F, WHEEL_R) | tyre with the hub and the disc's bolts (the disc its own shape since the 2026-11-01a build); rim with the spoke trims (rim styles later) | env, dielectric x0.25 / x0.4, double-sided |
| `wheelF_disc`, `wheelR_disc` | the wheels (WHEEL_F, WHEEL_R), by the names' `_wheelF` / `_wheelR` | our drilled brake disc (`bike_pieces.disc_pieces`, our art; since the 2026-11-01a build) | env, dielectric x0.4, one texture set for both (`textures_of`) |

The model's own triangles are 27c's but for the blank dial face (glTF mesh 9, 24 triangles), the three closed pieces
the volume guard cuts again (+2,756: *The coachline, the seat and the brake discs* below) and the two disc plates ours
replace (-2,660), with ours added (the dial, the needle, the shells, the under-bar mirrors, the discs): 238,831
triangles and 237,171 vertices in a worn nif with the UV seams (the 2026-10-31a build: 230,815 and 230,363; 27c:
224,515 and 146,410), the largest shape `static_black` at 48,658 (the build's cap 60,000, the game's 65,535). 30 draw
calls where the 2026-10-31a build had 28 and 27c 12, and the fixed shapes' shadow passes.

**Material files.** Each shape names one: the riding bike's `Materials\CMB\Bike\<mat>_worn.bgsm` (emissive and glow
maps as the material says; the bar assembly, the lower fork and the front wheel cast no shadow, as test 34 needed for
the lamp's beam), the parked bike's `Materials\CMB\Bike\<mat>.bgsm` (shadows on, nothing lit). `<mat>` is the label:
30 materials, 57 files (none for the parked bike of the two shells and the backlight, which the parked nif leaves out;
`check_bike_meshes.py` fails a file no nif names). When a nif names a material file the game takes the shading from it and
ignores the nif block's values but for the block-only bits (Skinned); the game reads the material file and doesn't
fall back to the block when it is missing (test 47: the bike went magenta); the block's values serve tools and
`--bgsm 0`. The files are written by
`tools/rider/bgsm.py` (version 2; it re-writes 19 real material files byte for byte from their values), and a material file
is what a workbench's material swap (MSWP) replaces later. `harley_meshes.py --bgsm 0` writes 27c's empty names, and
`--uvs none` (the build's emergency fallback) 27c's palette, renamed `Textures\CMB\CMB_Bike_d/_n/_s.dds`.

**Textures.** One texture set per material, `Textures\CMB\Bike\<mat>_d.dds`, `_n`, `_s` (and `_g` for the lit ones),
on a UV atlas made for that shape after the decimation (one atlas for the whole bike packs to 15% of its area): Blender's
Smart UV projection (66 degrees) per surface, so no island mixes chrome and paint, the hero surfaces given more of the
atlas, the islands packed; the seams split vertices (each label's count is checked between the texture stage and the
build). Baked from the 1.3-million-triangle model onto each shape: the normal (in object space, then re-encoded into
the tangent frame nifly itself writes into the nif, so the game reads it back as baked: a normal encoded with our frames and decoded with the ones read back from a written nif is 0.39 degrees off RMS over all 460,726 vertices, 0.001 at the well-conditioned ones; the check's bar is 2), ambient
occlusion with the whole bike as occluder, convexity (for edges and wear) and which source mesh each texel came from;
then authored procedurally (nothing came with the model): the oxblood paint `7a1118` with a clear coat, a faint flake
and orange peel and a twin cream coachline (since the 2026-11-01a build two offsets of one traced curve, *The
coachline, the seat and the brake discs* below), kept as a layer of its own for colours later; chrome dark and near mirror-
smooth (test 20's flat white was a light diffuse at a "smoothness" of 90); the exhaust with a faint heat tint near
the heads, on its own smooth normals; the engine in black wrinkle finish with its fins' edges machined bright; the
frame in satin powder coat; leather grain on the seat; the tyres' tread from the model with a scrubbed contact band;
discs with a polished band and a heat ring (the model's, up to the 2026-10-31a build; since the 2026-11-01a build our
own discs on their own art, below); gloss black rims with machined spoke faces; a plain plate; the lenses in
27c's colours and alphas.
Where the result differs from a first design: each texel's surface comes from the
glTF mesh its bake hit, not the piece's majority (a welded piece keeps its rim's machined faces), the engine's
machined edges come from a convexity bake of the full model held to the cylinders' height (curvature on the atlas
can't see across islands), the ambient occlusion is in every baked `_d`, the mirror glass keeps its convex vertex
normals unbaked (the model's glass is flat), and the 1 to 2% of texels where the UVs run along the normal, and
nifly's own tangent frame is noise, get a flat normal. Two changes after the first renders: the exhaust keeps its own
smooth normals too (`bake_normals` false: on about a tenth of its texels the bake's rays started inside the model's
pipe, where the decimated pipe lies more than the cage's 0.3 inside it, and came back reversed; the authoring fell back
to the shape's normal there and the chrome's reflection broke into patches along the pipes), and the discs lost their
turning grooves (at a pitch of 0.09 they were finer than the 0.15-unit texel of the wheels' atlas and beat into a
wavy moire). Formats as the vanilla files': `_d` BC1 (BC3 where there's alpha), `_n` BC5 with DirectX's green,
`_s` BC5 (red the specular, green the smoothness), `_g` BC1, legacy FourCC headers, full mip chains, no BC7. 2048 for
the paint, chrome, engine and black sets (their `_s` at 1024), 1024 for most, 256 to 512 for the small ones:
88.6 MB in 93 files since the 2026-11-01a build (the budget 93 files and 89 MB: the discs' one 1024 set, 3.3 MB,
over the 2026-10-31a build's 85.3 MB in 90; the four 2048 sets 9.3 MB each, twelve 1024 sets 3.3). The cubes: chrome `Shared\Cubemaps\MetalChrome01Cube_e`, paint, engine,
tyres and rims `mipblur_DefaultOutside1_dielectric`, lenses `shinyglass_e` (vanilla's), and the mirrors' ours,
`Textures\CMB\Bike\mirror_cube_e.dds` (below; `mirror_cube_zup_e.dds` ships beside it). Since the 2026-11-02a build the
mirrors name the game's `Shared\Cubemaps\MetalBrushed02Cube_e.dds` and the chrome reflects at env 6 with specular 2
and screen-space reflections (*The chrome, the mirrors' cube and the disc bore* below): the main Data ships no mirror
cube, 91 files and 86.6 MB.

**Conventions.** Smoothness 0..1 in the block and the material, and the `_s` map's green modulates it; FO4's flag
bits (27c set SF1 0x100 and SF2 0x8000, which are Skyrim's receive-shadows and envmap-light-fade but FO4's
RGB_Falloff and Dismemberment); `rootMaterialNameID` -1 (27c's pointed at an unrelated string); the nif's UVs run down
(v = 1 - Blender's). The worn nifs' positions are half floats (0.0625 apart near 128 units), so every overlay sits at
least 0.25 off the surface under it (the dial's backlight +0.25, the needle +0.5, its hub cap above that, the tail
shell +0.25, the brake shell +0.5) and the build checks the gaps in the nif's own half floats (in half floats 0.21 for the backlight over the face, 0.46 and 0.19 for the needle over the face and the backlight, 0.24 for the tail shell, 0.50 for the brake shell over the lenses and 0.25 over the tail shell; the build wants 0.9 of each nominal as built and 0.4 in half floats).

**Stages.** `tools/rider/build_bike.sh` (ASSETS.md): `export` (`harley_meshes.py --stage export`: the finished shapes
into a stage folder), `art` (`bike_art.py`: our dial, badge, lens patterns and the mirror's cube faces, with a drawn
stroke font, so no font file), `textures` (`bike_textures.py` in Blender: the UVs, the bakes, the DDS files and both
material files per material; `ONLY=` does part of it, and a per-label cache keeps what's done), `build`
(`harley_meshes.py --stage build`: the nifs with the stage's UVs and the material names, `CMB_BikeParts.ini`,
`CMB_BikeFit.json`; since the 2026-11-01a build also `CMB_BikeView.nif`, the bike in first person: the worn nif's 30
shapes with the same vertices in the bike's own space, in full precision, the worn materials and shadow flags,
unskinned, named `CMB_BikeView_<label>` under one NiNode `CMB_BikeView` whose flag bit 0 hides it, under a
BSFadeNode root, no collision; the plugin shows and places a script-placed copy in first person, where the game hides
the worn bike; `--view 0` leaves it out), `check` (`check_bike_meshes.py`: every shape, flag, material, texture and overlay, the brand words,
and `CMB_BikeParts.ini`'s 27c keys and `CMB_BikeFit.json` against a reference build) and `fallback`. The textures take
about 28 minutes from scratch on four shared cores (a rerun redoes only what changed: seconds for the art, 12 to
16 minutes when only the authoring did), each `harley_meshes.py` stage 65 to 90 s and the check about 15 s. Since the
2026-11-01a build the export rewrites a shape's file only when its arrays changed (`np.savez_compressed` stamps the
time, and the texture stage keys its caches on the files' bytes: a rewrite of the same shapes had re-keyed every
bake), so an export that changes one shape costs only that shape's bakes and the labels it occludes. `CMB_BikeFit.json` and every 27c key of `CMB_BikeParts.ini` come out as
27c's, byte for byte, but `FrontMinY` (above), so the riding clips, the hands and the steering are as they were.

**No brand on it.** The textures are authored, not copied, and draw no text: the badges are our own winged wheel (a
ten-spoke wheel with five feathers a wing, chrome on black enamel) and a roundel, the plate is plain. The model's own
geometry carries embossed logo relief (the air cleaner's cover, the derby and timer covers, the tank badges, the rear
emblem), which a normal bake would copy: the texture stage checks those regions of `_n` and flattens what it finds
(nothing was found: close-ups of the covers, glTF meshes 40, 41, 42, 45, 16, 97, 103 and 24, show no lettering or
emblem relief, and the badges are our art, not baked; the air cleaner's and the derby and timer covers' baked normals
are low-passed anyway, features under about 1.2 units flattened, which took out smooth curvature and screw heads). The shapes, materials and textures are named `CMB_Bike*` and `CMB\Bike\*`, and `check_bike_meshes.py`
looks for the maker's and the model's names in every byte of the output.

**27c's look back.** The new plugin drives 27c's meshes as 27c's did (their names give 27c's roles; none of the new
roles is there to switch), so copying 27c's `Meshes\CMB` and `Textures\CMB` back over this build's gives 27c's bike
with this build's plugin; `Materials\CMB` is then unused. With this build's meshes, every new key off but
`RolesByName` (the table in TESTING.md) leaves no needle, no lit tail, brake or dial and the stock mirror: 27c's bike
with the new textures and the lower triple clamp turning with the bars (both come with the meshes, no key).
`RolesByName` stays 1 for that: at 0 (for 27c's meshes) none of the new parts is told apart, and with this build's
meshes every one shows (the needle at rest, both shells and the backlight lit, all three mirrors), whatever the other
keys say.

### The coachline, the seat and the brake discs (the 2026-11-01a build)

Test 47's look notes: the tank's cream double line "wobbly", broken where it turns at the tank's rear end; the seat's
texture "in the air a bit"; "the models for the brake plates were low quality". Each is a build-time change with an
off value that gives the 2026-10-31a bike back byte for byte (checked: a build with all of them off makes the
2026-10-31a nifs, `CMB_BikeFit.json` and `CMB_BikeParts.ini` again, the same bytes), and the optional MO2 folder
"Commonwealth Motorbike - 2026-10-31a look (A-B)" (2026-10-31a's `Meshes\CMB`, `Textures\CMB\Bike` and
`Materials\CMB\Bike`, which belong together: the UV atlases are the meshes') switches the whole look back in game.

**The coachline.** 2026-10-31a's line was the iso-lines of a distance field on a 0.25-unit grid of the tank's
projected outline: a staircase outline at that pitch gives an inset line that follows its corners (a wave of up to
0.08 units, about 1.5 texels, every 2 to 3 units, half the 0.16-wide line), its width was measured in projection, and
the side mask (the surface within about 56 degrees of the side) faded it where the tank's surface folds under itself
at the rear, over the seat's nose: the break. Now (`bike_textures.coachline_v2`) the tank's own triangles are
rasterised on (y, z) at 0.02 units, the outline traced (marching squares) and smoothed, one curve C traced at a
distance of inset + gap + radius inside it, and the two lines drawn as C's outward offsets at `radius` and `radius` +
`gap`: parallel by construction, every corner rounded (1 and 1.55 units), the acute rear tip a U. The width, 0.26, is
measured on the surface (the field's slope across the line), the edge box-filtered over the texel's footprint, and the
line drawn on the tank's outer layer only, faded only where the surface grazes the side view (|n_x| under 0.05 to
0.15): no fade at the crease. Off value: no `radius` in `bike_materials.json`'s pinstripe entry and `width` 0.16.

**The seat (the volume guard).** The seat's piping cord (the welt along the seam between its top and sides: glTF mesh
25's second piece, a closed tube 0.5 x 0.15) was cut by the simplifier from 2,368 to 210 triangles and kept 0.34 of its
volume, so it stood out of the seat as fins at random angles: the "texture in the air". An audit of all the model's
pieces found two more closed pieces crushed that far (glTF 46 in `static_black`, 0.21; glTF 45 in `static_engine`,
0.32); every other closed piece kept 0.62 or more. `harley_meshes.py`'s volume guard (`--volume-guard 1`, the
default) cuts a closed piece of at least 0.05 cubic units that keeps under 0.6 of its volume again from the source, at
twice its target each time, till it keeps 0.8 (or keeps it whole), unless that would take its shape past 55,000
vertices in the nifs (the decimation's welded vertices times 2.25, the most a 2026-10-31a shape grew to with its seams,
2.14, and a margin: none came near). This build: the welt 210 -> 576 triangles (0.91 of its volume), glTF 46 464 ->
2,816 (0.93), glTF 45 34 -> 72 (0.91); `static_black` 48,658 vertices with its seams. `--volume-guard 0` is the
2026-10-31a cut.

**The brake discs.** The model's discs (glTF meshes 78 and 100) have a 36 to 48 segment outline, and the decimation
had turned their faces into long thin triangles from the rim to octagonal holes, shaded by averaged normals (the
source is dented): a lumpy plate with studs for holes. Ours (`bike_pieces.disc_pieces`, `--disc ours`, the default) is
a drilled disc: a 96-segment outline, the friction band (0.7 to 1 of the outer radius) in 24 cells of 15 degrees each
with a drilled hole (radius 0.0266 of the outer radius) at 0.33 or 0.67 across the band, alternating, and the carrier
in 6 cells with a round window each; both faces, every hole's wall, the rim and the bore, flat normals split at the
edges, watertight, 3,960 triangles a disc. It sits exactly where the model's plate was: on the axle the plugin spins the
wheel about, between the plate's two faces (parked x 5.80 to 6.15 at the front, 6.96 to 7.28 at the rear: where the
caliper's pads are), out to the plate's outer radius about that axle (13.73, 12.55), its bore just inside the five
bolt heads on the carrier (1.96, 1.88), which stay the model's and spin with the tyre's shape as since test 41. Each
disc is a shape of its own, `wheelF_disc` and `wheelR_disc`: the plugin gives them the wheels' roles by the names'
`_wheelF` and `_wheelR` tags, so they spin, steer and ride the suspension exactly as the tyres (no plugin change; the
harness checks the maps are the tyres' to 1e-6 every frame). Their art (`bike_art.draw_disc`, one 1024 set for both,
the layout in fractions of the outer radius): machined steel `8a8d92` on the band with a polished pad track and a
faint straw-blue heat ring, a satin carrier `4a4c50`, a bright chamfer round every hole, the rim and the bore (the
walls take the UVs of a 0.04-wide ring at their edge, which the art paints as the chamfer), concentric turning grooves
in `_n` at a pitch of 0.18 units (6.7 texels: 2026-10-31a's 0.09 on the wheels' atlas was under a texel and moired).
With `[Parts] RolesByName=0` (27c's sphere rules, for 27c's meshes) the discs' spheres sit 6.4 and 7.5 off the axles,
past the rule's 6: they would not spin, which is why that switch is for 27c's meshes only. `--disc model` keeps the
model's discs in the tyres' shapes (28 shapes, 2026-10-31a's).

### The chrome, the mirrors' cube and the disc bore (the 2026-11-02a build)

Test 48: the chrome "too dull, matte, not as shiny"; the game's mirror cube (the optional folder) "looks better, but not
ideal"; and the 2026-11-01a review's ring of the wrong colour round the front disc's bore. The mirrors' three materials
(and their `_worn`) name the game's `Shared\Cubemaps\MetalBrushed02Cube_e.dds` (cube shorthand MB, by path, nothing
copied), with env 2.0 and the glass 6e7276 kept: the combination the tester called better; our MR cube is written only
if a material names it, so the main Data ships no mirror cube (`mirror_cube_e.dds` and `mirror_cube_zup_e.dds` are only
in the optional folder now). The four chrome materials (static_chrome, static_exhaust, front_chrome, fork_chrome): env
1.0 -> 6.0, specular mult 1.0 -> 2.0, and screen-space reflections on (`ssr`, the BGSM's alone: SHADER_KEYS takes it,
the nif's block keeps none). The game tints a cube's reflection by the colour map; our chrome's is 0.042 linear, so env
1 reflected about 4% of the cube ("matte"), env 6 about 24%, the game's own mirror's figure. No texture was re-authored.
The brake discs' bore: `DISC_HUB_REF` 0.15 -> 0.142, and the geometry cuts the bore there too (`disc_pieces` bore
"shared", a ValueError if it would cut the bolt heads; the bolts' least radius is 0.143 of the outer radius on the
front, 0.150 on the rear), so art and geometry agree and the front disc's light ring at the bore is gone (in 2026-11-01a
the wall colour ran 3-4 texels outside the geometry's bore). `--disc-bore bolts` (`build_bike.sh`'s `DISC_BORE=bolts`,
written into the stage manifest and refused by the art and build stages if they differ) with 2026-11-01a's
`bike_materials.json` rebuilds that build's 157 files byte for byte. Because the discs are occluders in every nearby
label's bake, every label was re-baked and the occlusion of eight materials (static_chrome, fork_chrome, fork_black,
static_black and the four wheel rim and tyre maps, `_d` and `_s`) moved by a few levels on about 1% of their texels (at
most 19 levels): physically right, invisible in practice. `Textures\CMB\Bike` is 91 files, 86.6 MB (93 and 88.6 in
2026-11-01a: the two mirror cubes gone). The optional MO2 folder "Commonwealth Motorbike - 2026-11-01a look (A-B)" holds
2026-11-01a's bytes of every art file this build changes or drops (40 files, 70 MB: the five nifs, 21 DDS and 14 BGSMs),
so over the new Data it gives that build's look exactly; it replaces both 2026-11-01a folders. The packager's guard
(`guard_optional.py`, outside the repository) refuses a `CMB_BikeFit.json` anywhere (the build-48 check: the 2026-10-31a
look folder shipped one), a file that isn't nif, dds, bgsm or bgem in an optional folder, and a `CMB_BikeParts.ini` that
isn't Data's. The previews (`look_render.py`) use a stand-in for the game's cubes, so the chrome's brightness and the
mirrors in game are the tester's to judge (TESTING's T3 and T4).

### The chrome and the wheels toned down (the 2026-11-06a build)

Test 49: the chrome now "too bright, pearly, smudged", the discs and rims too white. The game multiplies a cube's
reflection by the colour map: env 1 (2026-11-01a) reflected about 4% of the cube, dull; env 6 about 24%, pearly; the
four chrome materials (static_chrome, static_exhaust, front_chrome, fork_chrome) are now env 2.5 and specular 1.5 with
screen-space reflections off (they smeared on the small curved parts), and the eight rim and disc materials (wheelF_rim,
wheelR_rim, wheelF_disc, wheelR_disc, each with `_worn`) env 0.4 -> 0.25 and specular 1.0 -> 0.75. Only the BGSM fields
and the nifs' shader blocks changed: every DDS (91 files) is 2026-11-02a's byte for byte, the badge (0.8) and the
mirrors (MB, 2.0) unchanged. `check_bike_meshes.py` checks the new values (`CHROME_ENV, CHROME_SPEC, CHROME_SSR` and
`WHEEL_ENV, WHEEL_SPEC`) and, with `--look-reference`, that the chrome's and the wheels' 21 maps are the reference's.
The optional MO2 folder "Commonwealth Motorbike - 2026-11-02a look (A-B)" holds 2026-11-02a's bytes of the 21 files this
build changes (16 BGSM and the 5 nifs, 43.5 MB), so over the new Data it gives that build's look exactly; it replaces
"2026-11-01a look (A-B)". The previews (`look_render.py`, a stand-in cube and no screen-space reflections) show the
exhaust a little less bright and the bolts and discs less mirror-white; the game's result is the tester's (T-L4; Q-C2
asks the cubes' brightness for a number next round).

### The speedometer

The model's speedometer is a blank disc (glTF mesh 9, 7.4 across in its cup, facing the rider). It's dropped, and
`bike_pieces.py` puts our own dial in its plane: a black face with cream numerals from 0 to 80 mph every 10 over 240
degrees (0 at eight o'clock, 40 straight up, 80 at four), ticks every 1, 5 and 10, an arc and "MPH" (`bike_art.py`);
a needle, an orange-red tapered blade from the hub to the numerals with a black counterweight, 0.5 over the face in a
shape of its own, modelled at the 0 mark; a hub cap over it. The plugin turns the needle about the dial's normal each
frame: theta = `NeedleZero` + min(`NeedleMax`, `NeedlePerMph` x `Scale` x 0.0319563 x s) degrees, where s is the
bike's speed along its heading (u/s, the steering's measure, or the look's own when the steering is off) smoothed over
`[Speedo] Tau` (0.3 s; 0 follows it at once) and 0.0319563 the mph in a unit a second (1 unit = 1.4286 cm). It turns
clockwise as the rider sees it: a turn of -theta about `NeedleAxis`, which points from the dial toward the rider (a
positive turn about an axis is anticlockwise seen from where the axis points); then with the bars, then the tilt.
`CMB_BikeParts.ini` gives it: `NeedlePoint` (the hub at the needle's height, 0.38, 64.93, 99.11), `NeedleAxis`
(0, -0.8346, 0.5509: the dial's normal), `NeedleZero` 0, `NeedleMax` 240, `NeedlePerMph` 3; without them (27c's file)
the needle is never turned. The needle's culling sphere is centred on its pivot (radius 3.98; the needle reaches 2.97), so
the sweep never leaves it. The trace's "parts:" line ends `ndl=<degrees>`.

`[Speedo] Scale` (1.75) is the dial's gearing. At 250% speed the bike rides at about 900 units a second, 12.9 m/s,
28.8 mph: true, but it reads slow against how fast the ride looks and sounds (the engine's gears and its heard speed
were set to the reference rides' pace, *The engine sound*), so 1.75 puts 900 u/s at 50 (50.3) on the dial;
`Scale=1` is the game world's true speed. `[Speedo] Needle=0` shrinks the needle to a speck at its hub (27c had
none).

With the lamp lit the dial's marks glow: `front_dialglow` is a copy of the face 0.25 over it (radius 3.6, inside the
bezel's chamfer) with the face's texture and a glow map that lights only the numerals and ticks, warm white x1.5;
the plugin shrinks it to a speck about its own centre whenever the lamp's lit parts are (the lamp off, the MCM's mode
or its hotkey) and always with `[Speedo] Backlight=0`. The needle doesn't go dark with it: its own material
(`front_needle`, the dial's art with a glow map lighting only the blade, `bike_art.py`'s `front_dial_g.png`) glows a
modest orange (1, 0.12, 0.03) x1.5 all the time on the riding bike, so it reads at night with or without the lamp
(the parked bike's material is unlit). That is the simpler of the two ways weighed: the other, a lit copy
of the needle the plugin would show and hide with the backlight, needs a 29th shape. `Needle=0` takes the glow away
with the needle, and `Backlight=0` still leaves the dial's face as 27c's (27c had no needle). The harness (mode
`look`): the needle at 15.10 degrees at 90 u/s (the formula 15.10) and 150.98 at 900 (150.99), 50.40 at 300 while
turning at 30 degrees a second with the bars at -12 (50.33), a pure turn about `NeedleAxis` against `front_black`
throughout; 240 at most with `Scale=3`; back to 0 within 3 s of a stop.

### The tail and brake light

The model's tail lens (a 7.3 x 2.4 piece of glTF mesh 95 under the rear fender's tip, facing back) stays in
`static_glass` as before: the plain red lens, which is what shows when the shells are hidden. Over it, `rear_tail`:
the lens's face and the first 0.6 of its side wall pushed out 0.25 along their normals (the rest of the wall is inside
the chrome bezel; a stray sliver of the lens piece that reached 26 units forward under the fender is dropped, it would
glow), a deep red (1, 0.012, 0.006) x2.5 through a glow map of three LED cells with Fresnel rings. And `rear_brake`: the same
at 0.5, grown 1.02 about the lens's middle, and both rear signals' lenses (mesh 34, round, 5.4 across: run, brake and
turn lamps in one, as on bikes built for the US), a deep red (1, 0.005, 0.0025) x8, about three times as bright
(the first values, (1, 0.08, 0.05) at x2.5 and x10, came out salmon-pink in the renders: at x10 the green and blue
pass where a tone curve turns red toward white; with the green and blue near 0 the brake stays red under a
per-channel curve such as the game's, `look_render.py --view-transform Standard`, while its default AgX view still
pales any bright red). FO4 can't change a shape's emissive from outside without
reverse-engineering its shader property in memory, so the lights are switched the way the lamp's ring is: the plugin
shrinks the shell to a speck through its skin map, now about the shape's own centre so the speck stays inside the lamp
(x -> 0.001 M x + m + 0.999 M c, c the shape's sphere centre in the bike's space: the sphere stays put). The running
light is lit whenever the bike is ridden (`[Tail] Glow=0`: never, the plain lens as in 27c). The brake light follows
the engine sound's brake rule, moved into a function of its own and run every riding frame whether the sound plays
or not: with the input hook, the back key read under 0.1 s ago at over 10 u/s; without it, over 10 u/s and slowing by
more than 1000 u/s a second; held `[Tail] BrakeHold` (0.3 s) after the rule lets go, against flicker; `[Tail]
Brake=0` never lights it. A door or a fast travel (a jump of over 300 units in a frame) and a load start the measured
speed and its rate afresh, so arriving moving doesn't read as a hard brake (the review of the 2026-10-31a build: it did,
for about 0.4 s, with the steering off or without the hook). The trace's "parts:" line ends `brk=0/1`. In the harness: with the input hook lit in the frame of the back key at 600 u/s and out 0.60 s after letting go
(0.29 s with `BrakeHold=0`), never with `Brake=0`; without the hook lit 0.34 s into a 2250 u/s² brake from 900 and
never in a 450 coast nor after a jump of 5000 arriving at 300 u/s. That lag without the hook is known and left this round (the sound's speed and rate are slow). No light is
cast (no light reference: the shells only glow, which costs nothing; until 2026-11-01a: see *The tail lamp's light*), and the parked bike has neither shell.

### The mirrors

Fallout 4 cannot show a real reflection in a mirror. It has no way to render the scene a second time into a
texture for a shape like this, and its screen-space reflections reflect only what is already on the screen, while a
mirror shows what is behind the camera. So the glass reflects a cube map, as chrome does, looked up along the
reflection of the view: ours, `Textures\CMB\Bike\mirror_cube_e.dds` (`bike_art.py`: a clear sky from zenith blue to a
pale horizon with soft clouds and a sun, hazy hills on the horizon, a dark ground with a haze band, continuous across
the faces; Direct3D's face order and orientation, +Y up; `mirror_cube_zup_e.dds` is the same sky with +Z up, for a
one-file swap if the game shows the sky sideways: none of the Fallout 4 files at hand says which the game wants). The stock
mirrors (glTF meshes 58 and 59: housings, stems, glass) are a shape of their own, the glass a mid grey (`6e7276`) with
full smoothness at an env scale of 2.0, as the game's own mirror (its colour map tints the cube: test 47's near-black
glass, `08090a` at 1.5, showed black; the 2026-10-31a previews had added the cube untinted), and its normals bent convex (as from a sphere 36 behind the glass: 0.9 to 10.7 degrees off the
flat), so the sky shows as a gradient that moves with the bike and the head, not as one flat colour.

The reference rides show mirrors hung under the bar ends, and two styles of them are modelled (`bike_pieces.py`): an
egg-shaped and a D-shaped (teardrop) glass 13.5 x 8 in a cup 15 x 9.5 with a rolled lip, 3 deep inboard and 2
outboard, on a stalk from a boss and lock nut under the switch housing to a ball at the cup's back; the head's centre
at (+-33, 37, 84.5) in the worn bike's space, its top at 89 under the fingers, the glass facing back, turned 15
degrees in and tipped 18 up so the rider sees the road behind (2 further out than first planned: at full lock the
inner one came within 0.1 of the tank). The least gap to the tank with the bars at either lock: 1.93
for the egg and 1.73 for the D, the inner mirror at full lock (the stock mirror's 7.4 or more). The riding bike carries all three; the plugin shows the one `[Look]
Mirrors` names (1 the stock one, as 27c; 2 the egg; 3 the D; 0 none) and shrinks the others to specks. The parked bike
keeps the stock mirror whatever the setting this round: the plugin never touches the parked bike's 3D (its other two
mirrors are in its nif, hidden by their node flag, for a later bench preview or a parked swap).

### Seeing it before the game: `look_render.py`

`tools/rider/look_render.py` renders the built nifs in Blender's Cycles (Blender as a Python module, on the CPU), shaded
the way Fallout 4's lighting shader does as far as is cheap, so the bike can be looked at before the tester does. It
reads the nifs through PyNifly and, when a shape's shader name is a material file under the Data folder, the material
file (else the nif block: `--bgsm 0` renders the nif blocks' own values, as a build with `harley_meshes.py --bgsm 0`
would look); it decodes the DDS files itself (texture2ddecoder);
base colour from `_d` (its alpha for blend and test), the normal from `_n` (DirectX green, BC5's blue rebuilt, through
Blender's tangents: nifly's are the same frame for smooth detail), specular `_s` red x the specular colour and
multiplier, smoothness `_s` green x the material's (a GGX highlight from the sun alone); the environment-mapped
shapes lit by a lookup of their cube along the reflection vector x `_d`'s colour x `_s` red x env scale (weighted by
Fresnel on the dielectric cube; `--env-albedo 1`, the default since the 2026-11-01a build: test 47 showed the game
tints the cube by the colour map, the near-black mirror glass showing black, where the 2026-10-31a previews, which
added the lookup untinted, showed a sky; `--env-albedo 0` is the old way), and nothing reflected by tracing rays, as
in the game; our cube decoded from its DDS (`--cube-up`),
the vanilla cubes (not on the build machine) by procedural stand-ins; emissive = `_g` x colour x multiplier (colour x
multiplier without a glow map), lighting nothing else; shapes without Cast_Shadows casting none, single-sided ones
culled from behind. On the riding bike it does what the plugin does on a frame: the roles by name, the needle turned
to a dial reading, the bars turned, the lamp's parts and the backlight lit only with the lamp, the brake shell only
braking, the mirror `[Look] Mirrors` names. Day (sun and sky) and night (a moon, the lamp on with its beam a spot light
where the plugin puts the game's, the cubes' share at 0.3: whether the game dims them at night is untested). The views
(`--list-views`): both three-quarters, both sides, the cockpit with the needle at 0 and 50, the dial close up, the tail
lit and braking, three at night, the mirrors (each style from the rider's eye and from outside), close-ups of the
tank, engine, front wheel and seat (and a sheet of them), full lock both ways from above, the parked bike; a frame
whose state is the same as an earlier one's is copied, not rendered again (27c's needle-less cockpits, say). At 1280
x 800, 10 samples and the denoiser, a view takes 11 to 39 s at the lowest priority on four cores shared with other
builds (27c's bike 11 to 23 s, this build's 16 to 39 s at a load of 5 to 8 and 11 to 24 s at 3 to 4; reading the nif
and decoding the textures 2 to 14 s first).
The denoiser prefilters its albedo and normal guides (`--prefilter ACCURATE`, the default, about 4 s a view): with
the cheaper FAST prefilter the guides' own noise on the sunlit clear coat told it to keep the noise, and the paint
showed a fine sparkle at a distance that the game, which doesn't sample, never has. `--compare` makes a before/after
sheet. Its default view transform, AgX, turns any very bright colour toward white (the brake light reads pink in it
whatever its hue); `--view-transform Standard` clips each channel, nearer the game's per-channel tone curve, for
judging a light's colour. What it can't show: the game's tone mapping and eye
adaptation, its ambient light and fog, the real vanilla cubes, screen-space reflections, mip and BC1 shimmer at a
distance.

### The tail lamp's light

Since the 2026-11-01a build (test 47: "you can tell it's on, but it's not producing light"). The shells above only
glow: an emissive material lights nothing around it in Fallout 4, and the game keeps no add-on node of a worn nif
(test 30), so, as for the headlamp since test 32, the light is a reference of its own. The controller script places
`CMB_TailLight` (a LIGH: radius 220, about 3 m; colour 255/24/10, the shell's red; Dynamic and NonShadowSpotlight, a
120-degree cone; fade 0.75) at the player on the first riding tick with a ground normal from the plugin (so never in a
game without it; with the MCM's "Tail lamp lights the road" on), hands it over with the headlamp every two cells (on
its own two cells on when there is no headlamp reference) and deletes the old one 2.5 s later; its form id goes
to the plugin in `CMB_TailRefHi/Lo` (0x872, 0x873; 16 bits each, both 0 none), the headlamp's way. The script writes
Hi, then Lo, so for a frame the pair can be the new high half over the old low one, at a 65,536-id boundary of the
placed references some other reference's id; the plugin takes a changed id only when two frames running read it (each
handover a frame later), both 0 at once (the review of the 2026-11-01a build: such a frame carried that reference, wrote
its place, and parked the old copy as a second handover; the headlamp's own reader is as it was). The plugin carries
it with code of its own (the headlamp's paths are untouched: `LensWorld` is now a wrapper over `PointWorld`, the same
arithmetic in the same order, and the harness's `lamp:` checks pass unchanged): each riding frame its 3D goes to the
tail shell's culling centre ((0.33, -64.22, 54.31) on this bike, or `[TailLight] Point`) with the tilt only (the lamp is
on the frame, no bar turn), `Back` (8) along the beam, which points straight back and `Pitch` (30) degrees down along
the root's `[Lamp] BeamAxis` (+x, the headlamp's measured convention), led by `[Lamp] Lead` frames of the speed: the
light at (0.33, -71.15, 50.31) in the bike's space. A spot, not an omni light: the lamp sits 55 to 65 behind the seated
rider's back, and a shadowless omni of radius 220 would paint her back and the seat red (x3 braking); with the axis 30
degrees down and a 120-degree cone the cone's upper edge is 30 degrees above level behind the bike, the rider about
150 degrees off the axis, and its lower edge straight down at the light, so the plate, the fender's tip and the rear
tyre's back are lit. It is lit while riding with `[Tail] Glow=1` or the brake light on, and parked far below
otherwise (said once per change: "tail: the light reference ... parked far below (Glow=0 and no brake)"), and on a
ride whose bike isn't read in the frame (no bike skin held, the skins' matrix layout untold or disagreeing: "... (the
bike's bone isn't held)"; the review of the 2026-11-01a build: it stayed lit where the script placed it, one more at
each handover). The light and the view bike (below) are let go of, their roots' references given back and their
pointers and ids forgotten, at every getting off and every load, whatever else is held then (the review: only when a
bike skin or a rider shape was still held, so a ride whose skins went first, with no rider held, kept pointers to
references the script then deletes into the next ride or the loaded game). Brightness:
on its 3D's first frame the plugin finds the root's NiLight child and reads its diffuse colour (+0x12C, three floats)
and dimmer (+0x144) as the base (CommonLibF4's layout; accepted only as a colour, each channel 0 to 16 and their sum
over 0.01, else never written); each frame it writes the colour times `RunGain` (1), `BrakeGain` (3) while the brake
light is lit, switched in the same frame as the shell. What it wrote is read back the next frame: if the game put it
back, one line a ride ("tail: the game set the light's colour back (read ... after writing ...): ... try [TailLight]
BrakeBy=dimmer"), and `BrakeBy=dimmer` writes the dimmer instead (0.75 x 3 = 2.25 braking). That write is the
untested part: whether a NiLight's colour or dimmer reaches the renderer after the light is made is what test 48
answers; the running light works either way. The trace's "parts:" line ends ` tl=` (the gain written, 0 parked).
`[TailLight] Enabled=0` parks it every frame and never writes its colour (the lens glows and lights nothing, as the
2026-10-31a build); the MCM's "Tail lamp lights the road" off (`CMB_TailLightMode` 0) places no reference at all; an
older ESP (no 0x872/0x873) says "tail: no CMB_TailRefHi/Lo (an older ESP)" once and nothing else changes. The
2026-10-31a paragraph above ("No light is cast") describes that build. In the harness (mode `view`): the light's root,
its local and the reference's own place 0.000 from the expected point through the bind, the COM and the tilt, its +x
0.0001 off the beam; the colour exactly the base riding, (3.0000, 0.2824, 0.1176) in the frame the back key lights the
shell, back to the base in the frame the shell goes out; `[Tail] Brake=0` never brighter, `Glow=0` parked with no key
and lit x3 with it, `Enabled=0` parked a whole ride with the brake and the colour never touched; a handover to a
reference whose 3D comes 0.3 s late keeps the old one at the point till then; the game putting the colour back before
each frame gives the line once; `BrakeBy=dimmer` 2.25 and 0.75; a ride with the tilt at 0 (the bike's skins held for
the parts file, no rider) whose bike's skins go with the ride on: the light parked at once, said once, then let go of
at a load on that ride and at the getting off (a line each, the light's and the view bike's roots back at their base
references, the census said too); a handover whose high half is written a frame before its low one, the pair naming a
placed crate with its 3D for that frame: the crate not moved and never named, the old light at the point the frame
after, then the handover as usual, and back the same way with the frame between naming nothing: no "isn't a placed
reference" line (both failing on the DLL without the two-frame rule); mode `roomold` (test 42's ESP) the one line.

### The bike in first person

Since the 2026-11-01a build (test 47: "in 1st person the bike model isn't even visible"). In first person the game
hides the player's whole third-person 3D (its root culled), and every bike shape is under it, so nothing the plugin
does to the worn bike can show there. A first-person model (MOD4/MOD5 on the armor addon) was ruled out: it would be
skinned to the first-person skeleton, whose pose comes from a graph with no holstered riding clips at all, drawn with
the first-person field of view (80 against the world's 70: its wheels and the ground would disagree), and bent by the
look-up and look-down additives. Instead a third carried reference, `CMB_BikeView` (an MSTT, `CMB\CMB_BikeView.nif`:
the worn nif's shapes with their vertices, materials and shadow flags, unskinned, each named `CMB_BikeView_<label>`,
under one node `CMB_BikeView` whose hidden bit is set in the file, so a placed copy without the plugin is invisible; no
collision), placed, handed over and deleted by the script as the tail light is (`CMB_ViewRefHi/Lo`, 0x874, 0x875; the
old one deleted 4.0 s after a handover). The plugin shows it only while the camera's current state is a
`FirstPersonState` (PlayerCamera+0x28; third person, VATS, the free and dialogue cameras keep it hidden and parked) and
the bike is ridden with its skins held. Its root goes to the bike's own place each frame, the bike's bone (COM) and
bind: x -> sb Nb (A x + t) + nb, led by `[View] Lead` frames of the speed along the heading and of the turning about the
vertical (the renderer draws a frame late, as the headlamp found in test 34). When its 3D first appears the plugin
finds `[View] Node` under it and each shape `<Node>_<label>`, and matches it to the held worn skin whose name ends
`_<label>` (all of this bike's are unique); each frame each view shape takes the map its worn shape got that frame
before its speck (`FrameTilt` keeps it: the wheels' spin, the bars and the fork's travel, the needle, the tilt and the
lift), as its local transform in the bike's space, and is hidden by the same rules (bit 0, or with `[Look] Cull=0` the
same speck about its centre); a shape with no match stays at the bike's own place. Local and world are both written
(the game may or may not walk the reference's 3D), each shape's world bound from its model bound (BSGeometry +0x120),
the node's and the root's a sphere round the shown ones (the renderer culls the whole by it), and previousWorld
(+0xC0) is the world written the frame before, for the root, the node and every shape (temporal anti-aliasing and
frame generation read motion from it; a placed object the game doesn't move would otherwise smear), and the reference's
own position is kept at the root's, as the headlamp's (the game's distance fade and cell go by it). At a handover the
old copy stays shown at the same transforms until the new one has had its 3D `[View] HandoverTime` (1.0 s, longer than
a fresh reference's fade-in); two copies at bit-identical transforms draw the same pixels, so the bike never blinks;
then the old one's node is hidden and its root parked. The game may stop updating the hidden third-person skeleton in
first person: with `[View] Stale=1` the plugin compares the COM bone's move with the player's each frame, and the bone
still (its place under 0.01 and its turn bit for bit the same: COM sits straight above the player's origin, so by its
place alone a live bone turning on the spot read as still, the review of the 2026-11-01a build) for 3 frames while the
player moved more than 0.3 or turned more than 0.01 rad is stale; then the
bone's world is the player's place and heading times where it sat on the player the last live frame (the identity, the
bike's origin at the player's, if there was none this ride), back on its word after 2 frames of it moving; only in
first person, and the headlamp's and the tail light's lens go by the same word (`BikeWorld`), identical in third
person. Probes for the next round (`[View] Trace=1`): on entering first person and every 2 s in it, "view: first
person: the eye at (x, y, z) in the bike's space" (the camera root, PlayerCamera+0x20), the skeleton live or stale, the
shapes shown and culled, the root's fade (+0x118) and PlayerCharacter+0xDFE bit 4. Expected from the probe's estimates:
the eye about (0, 3, 121) on the bike, the dial 66 away and 19.5 degrees below the line of sight, the front tyre's top
33 below, the nearest geometry over 30 from the eye (past the 15 near plane). No arms: the game draws none with the
weapon away, which the rider's pose needs (combat while riding is off by default, and a drawn weapon dismounts), so
the grips are empty; with "Allow combat while riding" on, a first-person gun may cross the bars. `[View] Enabled=0`
keeps it hidden (and the stale fallback off: always the bone's word), as the 2026-10-31a build; the MCM's "Bike in
first person" off places none; an older ESP says "view: no CMB_ViewRefHi/Lo (an older ESP)" once. The next round's
material swaps (customisation) must reach the view reference too: it is its own placed object. In the harness (mode
`view`): third person hidden (the node's bit set, the root far below) with the worn bike as before; first person shown
within one frame; the dial's point and the rear axle 0.0000 and 0.0005 from where the worn shapes' live bone data put
them, every shown shape's centre within 0.0005 and the five the worn bike hides culled; each world bound at its model
bound (0.0000 off), the root's (radius 109) holding them; the probe's eye (0.0, 3.0, 121.0), the fake's; previousWorld
exact over 30 frames at 600; turning at 30 degrees a second with the bars at -12, the steering head and the front rim
0.0000 and 0.0010 off; the needle's tip at 900 (151 degrees) 0.0000 off; the brake shell shown in the frame the worn
one lights; `Mirrors=2` swapping the mirrors after getting on again; the world frozen at 600: the stale line on the
third frame, 0.5 s on the root 0.000 from the player's place times its place before, back on the skeleton's word two
frames after it moves; turning on the spot at 60 degrees a second with the skeleton live, no stale line; `Stale=0`
the frozen word; `Lead=1` 3.12 ahead for a 5.1 ms frame of 600 (3.06), along the
heading; a handover with the new 3D 0.3 s late: the old one hidden 1.009 s after the new one's came (1.0 to two
frames), never both hidden; `Enabled=0` hidden all along. The plugin's frame in first person in the harness: 102 us
average (the bike's part 28 us for 29 shapes), against mode `look`'s third person.

**Your eye on the seat (2026-11-02a).** Test 48's eye probe showed the first-person camera over the bike's own origin at
a stop (12 behind and 3 under a seated rider's eye) and falling back by 58 ms of the speed (median of 41 samples over
850 u/s, the same at 160 and 224 fps: a time, not a frame), so at full speed it sat over the rear wheel, 64 behind.
Whether the camera trails or the third-person bone leads can't be told from the log; the fix works for either. Every
frame the view bike is shown, `EyeInBike` puts the camera root's world (PlayerCamera+0x20, +0xA0) into the bike's space
(x = A^T((Nb^-1 (e - nb)) / sb - t), the probe's maths), and `ViewEyeOffset` gives the view bike's node the offset d =
eye - EyeAt on the bike's own axes (across only with `EyeSide=1`), followed with `EyeSmooth` (0.05 s) fore-aft and
across and `EyeSmoothZ` (0.25 s, so a kerb still shows as the bike rising under you) in height, taken at once on the
first frame shown, and 0 while the eye is more than `EyeMax` (150) from `EyeAt` (switching into first person, a menu's
camera: "view: the eye 473 from EyeAt (more than EyeMax 150: the camera isn't on the bike): the view bike at its own
place", then "view: the eye within EyeMax again (N from EyeAt): the view bike under it"). The root, and the
reference's own place (the game's fade and cell go by it), stay at the bike's place; only the node moves, and the
shapes' worlds are w + s W (l + d). `EyeAt=0,12,128` is the riding clips' run-pose head on this bike (the hips at y -5,
z 73) plus the standing camera's offset from the standing head. `ViewPut` with `d == NULL` (`[View] Eye=0`) is the
2026-11-01a code path line for line. The probe line adds the offset, the eye's lag in ms at speed, and the bike's origin
and the eye from the player's place along the heading (which of the two is off the player's place): "...; the view
bike moved (0.0, -47.0, -3.0) on its own axes to put EyeAt there; at 600 u/s the eye 58 ms behind the bike's bone; from
your place along your heading: the bike's origin (...), the eye (...)". In the harness: stopped at the fake's eye (0,
3, 121) the view bike moves (0, -9, -7); at 900 u/s with the eye 58 ms behind, (0, -64, -3); in game expect about (0,
-11, -3) at a stop and (0, -64, -3) at full speed. The first-person frame cost is unchanged (110 us with `Eye=1`, 117
us with `Eye=0`, 115 us on the 2026-11-01a DLL). The headlamp's beam goes by the bone, so in first person it leads the
view bike by about 64 at full speed (a light, likely invisible; known).

**The tip, the riding field of view and the eye's globals (2026-11-06a).** Test 49: looking level in first person the
bike was out of view (the dial 29 degrees and the grips 51 under the eye line). Three fixed-ID globals the MCM and the
console write and the plugin reads (0x8B0-0x8B3, with `CMB_FxWaterLoop` 0x8B4 all five or none: "globals: the
2026-11-06a build's 5 found, CMB_ViewTip to CMB_FxWaterLoop (...)"):
- **The tip** (`CMB_ViewTip`, 20): once each time you go into first person on the bike (and after a load in it) the view
  eases down to 20 degrees by relative writes to the player's look pitch (`+0xC0`, + down), smoothstep over `[View]
  TipTime` (0.4 s); the pitch is read from the camera root's world rotation, the axis that lies best along the heading
  (`CameraPitch`). Already that far down: left as it is. It stops at the player's own look (the pitch not as it left
  it), third person, the eye far or 0. A self-check 0.1 s and 1 degree in: under 30% followed for 3 frames, undone and
  no tip that session ("view: the camera didn't follow the player's pitch (+0xC0): the view left as it was (no tip this
  session)"); the wrong way, undone and flipped once ("view: the player's pitch is the other way round: flipped (the tip
  goes on)"). "view: looked 20 deg down on getting into first person (from level; the camera now 20 deg down)"; the
  probe adds "; looking N deg down (the camera)".
- **The riding field of view** (`CMB_ViewFov`, 0 = off; 60-120): built, off by default. The world FOV's field in
  PlayerCamera is found once by its value (the one place in +0x100..+0x1F0 holding `fDefaultWorldFOV` followed by
  `fDefault1stPersonFOV`, else `[View] FovOffset`; an ambiguous or missing match leaves it alone), eased to the value
  over `FovTime` (0.3 s) while riding in first person and back on every way out (third person, getting off, a load,
  Tick's watch); a value we didn't write is left alone that ride; the game's settings are never written ("camera: the
  world FOV 70 -> 90 while riding in first person (CMB_ViewFov)", "camera: the world FOV back to 70 (third person)").
- **The eye's globals** (`CMB_ViewEyeForward`, `CMB_ViewEyeUp`, 0): added to `[View] EyeAt` (clamped -30..30 and
  -30..20, then EyeAt's own ranges) every frame; both 0 is `EyeAt` bit for bit. A change is logged once it has held 0.5
  s ("view: the eye now at (0, 12, 118) on the bike: [View] EyeAt (0, 12, 128), CMB_ViewEyeForward 0, CMB_ViewEyeUp
  -10"). An older ESP: "view: no CMB_ViewTip to CMB_ViewEyeUp (an older ESP): no tip, the game's FOV, EyeAt as the
  INI's". The four at 0 leave the player's pitch and the FOV field bitwise as the 2026-11-02a build did (the harness's
  off-value check).

### Hidden parts culled

Since the 2026-11-01a build (the 2026-10-31a build note's question: cull hidden shapes by their flag?). A hidden part
is a speck inside where it is (`Speck`), still culling-tested, skinned and drawn every frame. With `[Look] Cull=1` the
plugin also sets bit 0 of its NiAVObject flags (+0x108: app culled, which the culling pass checks before the bound,
skinned or not; first person hides the whole bike that way, and the parked nif's hidden mirrors are hidden by that
bit in the file) while the look's rules hide it: the mirrors not chosen, the brake shell while not braking, the
dial's backlight and the lamp's glow with the lamp off. The speck stays as a backstop. Each held skin keeps its
geometry (a reference of ours) and the flags it had; the bit is set or put back to the file's each frame only when it
differs (the game's other bits never touched), set again whenever it's found cleared (one line a ride: "look: the
game cleared the cull flag on ..."; a re-attached 3D is new shapes, held afresh), and bit 0 is put back as it was on
letting go. It saves almost nothing: by day with the lamp off and `Mirrors=1`, five shapes (the egg and D mirrors, the
brake shell, the backlight and the glow: 5 draws, 4,594 vertices and 6,077 triangles against the bike's 231 k, none in
a shadow pass); if the frame rate is short, the lever is the bike's triangles, not this. `Cull=0`: specks only, the
flags never touched (the 2026-10-31a build); the look line on getting on says `Cull=`. In the harness (mode `view`):
those five culled and still specks, the others not, every other bit (0xE << 32) as it was; the brake shell's bit
cleared in the frame the back key lights it and set again after; the game clearing the egg's bit: set again the next
frame, one line; getting off: every flag word back exactly; `Cull=0`: a ride with the brake and the lamp never changes
a flag word. Since the 2026-11-06a build `Cull=0` is the default: test 49's frame-rate A/B measured no gain (174-176
against 175-180 frames a second, inside the scatter); the code is kept and `Cull=1` is the 2026-11-02a build (mode
`look`: `[Look]` without `Cull` changes no worn shape's flag word through a ride with the brake and the lamp).

**The log's rate limits and the frame-rate line (2026-11-02a).** `[View] StaleLines=3`: the "third-person skeleton
stopped" and "moves again" pair is logged at most 3 times in any 10 s, then one count line ("view: the third-person
skeleton: N more stop(s) and move(s) again in the last 10 s (StaleLines=3: not logged one by one)"), and the ride's
total at its let-go ("view: the third-person skeleton: 10 stop(s) this ride, the first 3 logged one by one
(StaleLines=3)"; the build-48 check's finding 5); 0 logs every one. `[Diag] FpsLine=1`: every riding frame (`FrameTilt`)
is counted in quarter seconds of the plugin's clock; every 10 s the median of the quarter seconds' rates, their range,
`[Look] Cull`, first or third person and stopped or moving are logged as "time: the last 10 s: 189 frames a second
(median of the 39 quarter seconds, 187 to 191), Cull=1, first person, stopped and moving" (not "time: frame", which the
decal checks count); a gap over half a second starts afresh. It makes test 48's Cull A/B readable without an FPS
counter (test 48 had `Cull=1` on every ride, so nothing to compare). 0: no such line.

## Knocking enemies over (F4SE plugin and `CMB_RamScript`)

Test 40's wish; test 41's answers: on by default, the smaller robots count (protectrons, eyebots, Mr. Handy and Gutsy,
assaultrons) and so do the mutant hounds, the sentry bot and the super mutants don't, a tenth of their health is fine,
and the bike should lose speed at a hit. The plugin sees what's ahead; only Papyrus can push an actor and damage it
(`PushActorAway`, `DamageValue`) or tell a hostile one from a companion. So the two talk through globals of
CommonwealthMotorbike.esp, as the headlamp's reference is handed over: a float global holds 16 bits exactly, so a form
id goes as its two halves, and each message carries a number that changes, written last, so the reader tells a new one
from the last and reads the rest after it. `CMB_RamScript` is a script of its own on the controller quest, so its 0.1 s
poll and the controller's work never wait on each other's lock; the controller starts the poll on getting on and after a
load while riding (`StartRide`) and stops it in `FinishRide`, which every way off the bike goes through (`EndRide`),
through `CastAs` by name, logging it if the script isn't there ("Ram: CMB_RamScript is not on the quest: ...": an old
plugin file).

| Form (ID) | Written by | Holds |
|---|---|---|
| `CMB_RamSeenHi`, `CMB_RamSeenLo` (0x845, 0x846) | the plugin | the actor's form id, its high and low 16 bits |
| `CMB_RamSeen` (0x847) | the plugin, after the halves | the ask's number: 1 to 2^23 - 1 (exact in a float), going on from the save's at each ride's start; two asks `AskGap` (0.12 s) apart at least since test 41, and since test 43 each once the one before it is answered (`AskAnswered`) |
| `CMB_RamOk` (0x848) | the script | the ask's number for a yes, minus it for a no; 0 at a ride's start and end |
| `CMB_RamHitSpeed` (0x849) | the plugin | the bike's speed at the hit, units a second |
| `CMB_RamHit` (0x84A) | the plugin, after the speed | the number of the ask said yes to: the hit, told 0.12 s apart at least |
| `CMB_RamEnemies` (0x84B) | the MCM ("Knock enemies over") | 1 on (the default), 0 off: read by both |
| `CMB_RamMinSpeed` (0x84C) | the MCM ("Knock over from (speed)", 100 to 1500) | 450 units a second, half riding speed: read by both |
| `CMB_RamDamage` (0x84D) | the MCM ("Knock-over damage", 0 to 50) | 10, percent of max health at riding speed: the script's |
| `CMB_RamTooBig` (0x84E) | the generator | the races never knocked over (a FormList of 15) |
| `CMB_RamRobots` (0x856; test 43) | the generator | the robot races let past the plugin's size and No Knockdowns gates (a FormList of 4: ProtectronRace 0DFB33, EyeBotRace 0A563A, HandyRace 0359F4 for Mr. Handy, Mister Gutsy and Nanny, AssaultronRace 0D8417); read by the plugin only |

The plugin finds 0x845 to 0x84C by ID, all or none ("rams: not all of CMB_RamSeenHi to CMB_RamMinSpeed are there": an
older plugin file, and nobody is knocked over); the generator checks each of the ten forms' IDs, since a form created
before them would move them all (and `CMB_RamRobots`', created after the room's globals so that none of these moved). An
actor is seen by the actor ray, at axle height, `ActorLook` (0.8 s) of the speed past the front wheel (720 units at 900,
so the answer, the script's poll and a few engine calls, 100 to 200 ms, is in before the face rays' 0.3 s reach gets
there), or by the face rays, and found from the 3D the ray hit: the reference at the root node's user data (+0x110), a
form of type 0x41 checked by its type information, whose 3D root is the one hit, not the player. It's asked about only
if its race's size class is `MaxSize` (1, medium) or less and, with `NoKnockdowns` (1), the race isn't flagged No
Knockdowns (both read only once the rider's own race has read as a playable one of a size; else neither is checked, and
the script's list still applies); otherwise it's braked for as before ("rams: ... is too big (MaxSize)" or "can't be
knocked down (No Knockdowns)", with the race and its flags). Since test 43 the races in `CMB_RamRobots` pass both gates
(`Robots`, 1; test 42: the protectrons' ProtectronRace reads large with No Knockdowns, flags 42E08901, and they were
braked for 7 times, where test 41 wanted the smaller robots knocked over; `MaxSize=2` or `NoKnockdowns=0` would ask
about every large race not in `CMB_RamTooBig`, yao guai, mirelurks, radscorpions). The plugin looks it up at 0x856 with
the ram's globals and reads it as it reads them: its form type (0x5E) and type information (`BGSListForm`), the
`BSTArray<TESForm *>` at +0x20 (CommonLibF4's layout), 1 to 16 entries, each a race by its form type and type
information; at the first that isn't, the whole list is refused and the gates stand for every race, so a layout read
wrong is test 42's behaviour, not a crash ("rams: CMB_RamRobots: 4 races pass the size and No Knockdowns gates:
ProtectronRace (large, flags 42E08901, No Knockdowns), …", "rams: CMB_RamRobots can't be read (…): the size and No
Knockdowns gates stand" or "rams: CMB_RamRobots isn't there (an older ESP): …"; read again at each ride's start, logged
when its verdict changes), and the ask's line names it ("(race ProtectronRace: large, No Knockdowns, in
CMB_RamRobots)"). The script says yes only to one that is hostile to the player and isn't the player, dead, a companion
(a teammate or in `CurrentCompanionFaction`), essential, a child, in power armor, of a race in `CMB_RamTooBig` (the
super mutants and the behemoth, deathclaws, mirelurk queens, Liberty Prime, sentry bots, yao guai, vertibirds, the three
turret races, radscorpions, brahmin, synth gorillas and power armor; DLC races can't be listed without their masters,
and the size limit covers them) or knocked over in the last 3 s (one still down in the path is braked for); a refusal is
logged once in 10 s per actor and reason. No answer in `AskAgain` (0.4 s): asked again; after a no, `AskAgainNo` (1 s).
Two asks are told `AskGap` (0.12 s) apart at least, over the script's 0.1 s poll, as the hits are (test 41: five asks
went unread in packs, the Papyrus log's "Ram: N of the plugin's asks went unread": a second animal seen 46 to 120 ms
after the first, ask 14 a coyote and ask 15 a wolf 46 ms later, replaced the first's number before the poll read it; the
plugin dropped the first and asked again when it next saw it, so no hit was lost, but it was asked twice and answered
late). An actor seen inside the gap, or behind one still waiting, waits in its entry ("rams: X (race …) seen N past the
front wheel at N a second (the actor ray): its ask waits N ms for the one before it, so the script's 0.1 s poll reads
both"), braked for meanwhile as an unanswered one is, and `RamFrame` tells the oldest waiting ask once the gap has
passed, before the hits ("rams: X's ask told the script (ask N) N ms after it was seen, N ms after the ask before it");
one answered meanwhile, a late answer to its earlier ask, has nothing left to ask, and an entry waiting to ask is never
evicted. The script reads the newest ask each poll and needed no change. Test 42's packs (LvlViciousDog, coyotes in that
load order: 39 asks, 10 knocked over) showed the rest: the answers took 234 ms at the median (448 at most) while the
asks went out 120 ms apart, the script answering the newest it had read, and a dog not yet answered was braked for as a
wall at the very millisecond of its ask (20:47:05.987), so the pack stopped the bike ("dogs were strange: some knocked
over, some stopped the bike"). Since test 43 (`AskAnswered`, 1) the next ask is told only once the one before it is
answered, yes or no, or `AskAgain` after it unanswered, so a script that stalls can't hold the queue ("rams: … its ask
waits for the answer to ask N (AskAnswered)", "rams: X's ask told the script (ask N) N ms after it was seen, N ms after
the answer to ask N", and once a ride "rams: ask N (X) unanswered for N ms: the next ask told anyway"), and the script
polls again 0.03 s after an answer (`PollAfterDecide`; 0.1 gives test 42's) to meet the next. And (`AskFree`, 0.5 s) an
actor whose ask is pending, told or waiting its turn, is let by as for a yes while its race was read small or medium
(`MaxSize`; a listed robot that reads large isn't; since test 45 one is, with `FaceActors`), at `CMB_RamMinSpeed`, under
`AskFree` since its first ask was wanted and short of the hit's `Lead` point: the rays cast through it and the throttle
stays open ("rams: X ahead (N past the front wheel at N a second): its ask pending for N ms, the throttle kept (AskFree,
a small race)"); past any of those, or once the script has said no to it (a re-ask after a no, `AskAgainNo`, may come as
soon as 0.1 s later), it is braked for as before ("rams: X N past the front wheel, no answer in N ms: braked for"), so
the one actor whose answer didn't make it stops the bike, not the pack. 0.5 covers every answer measured, and
`ActorLook`'s 0.8 s leaves the face rays' 0.3 s to ease off once it lapses. For a yes at `CMB_RamMinSpeed` or faster the
throttle stays open, and the hit is told `Lead` (0.06 s) of the speed before the front wheel's edge reaches the actor
(54 units at 900: with the script's 30 to 150 ms the push comes between 90 past the edge and 18 short of it, and the
rider's capsule meets the actor some 110 past it); for `Pass` (1 s) after it the rays let its capsule by, the face rays,
the actor ray and `WallAhead` casting again past it (at most 3 at once), so a second actor or a wall behind it is still
seen (a ray stopping at the first actor never asked about a second one 50 behind it in time, and hid a wall). Two hits
are told 0.12 s apart at least, over the script's 0.1 s poll, the later one waiting, and an entry still to tell its hit
is never dropped. At the hit the throttle is held to `HitKeep` (0.85 since the 2026-11-02a build, 0.6 before) of the
speed at the hit for `HitHold` (0.25 s; 0.4 before), 765 a second from 900 (540 before), then builds up again as from a
slow ride (`Accel`, `Lead`); a second hit within the hold holds it to the lower (since 2026-11-02a a hit within
`HitChain` of the last shares the pack's dip: below). Since test 43 a yes is kept `YesKeep` (10 s) after it was given
even with the actor out of sight (test 42: a pack's dog back 9.5 s after its yes was asked again and braked for
meanwhile; its "throttle free" line then ends "(said yes to N s ago, kept)"), the script keeping its last 32 yeses for
it (16 before; `Remember()` makes the arrays anew at any other length), and for `HitGrace` (1 s) after a hit at
`CMB_RamMinSpeed` or faster a yes is knocked over at any speed: the dip after a hit, `HitKeep`'s hold and the game's own
bump, is the hit's, not a slow ride's (test 42's 10 "under 450" lines all came within a second of a hit or of a brake
for an ask not yet answered, the pack's second dog braked for at 400 after the first went over at 700; "rams: X hit at N
a second, N past the front wheel: under CMB_RamMinSpeed's 450, but N s after a hit at N: knocked over all the same
(HitGrace); told the script (ask N)"). A hit inside the grace doesn't renew it, and it is told with its own speed, so
the push is at its floor when slow. The script reads the hit before the asks (a tick that pushed or answered reads it
again at once), pushes the actor away from the rider with a force of 3 at `CMB_RamMinSpeed` rising to 8 at 900, 10 at
most (`PushActorAway`'s scale isn't known: a first guess, to tune from the log), and takes `CMB_RamDamage` percent of
its max health times the speed over 900, held to 0.5 to 1.5 (5% at the slowest and 15% at 1350 or faster with the
default 10). Up to 2026-10-31a never the last of it; since 2026-11-01a (test 47: "you can't kill an enemy while on the
bike, just take them down to the last bit of health": the raider FF0198E6 knocked over 17 times, held at 1.0 twice) a
hit that would leave under `KillBelow` (1.0) calls `Kill(PlayerRef)` with the MCM's "Knock-overs can kill" on
(`CMB_RamKills`, the default): the death event carries the player as the killer, so the experience, kill quests and the
Story Manager's kill events are the player's as for a shot (`DamageValue` names nobody, `KillSilent` sends no event,
`KillEssential` would clear the essential flag); the refusals stand (companions, essential characters, children,
non-hostiles, power armor and the big races are never knocked over at all), and the push's 0.5 s line says who killed it
("dead, the killer the player|someone else|nobody", with the player's experience before and after for the bike's kill,
or "NOT dead after Kill"). `StartRide`'s line says which way the switch was ("the last of it a kill (the player's)" or
"never the last of it"). Off, the damage and every branch are 2026-10-31a's; `StartRide`'s line names the switch either
way, and the push measurement notes a death either way. Test 48's 12 bike kills by `Kill(PlayerRef)` gave +0 experience:
Kill credits the kill but skips the damage path where the game rewards it. Since 2026-11-02a the killing hit is
`CMB_RamKillSpell` (0x89B: Fire and Forget on the target, one effect, `CMB_RamKillEffect` 0x89A, a hostile, painless,
no-hit-effect Value Modifier of Health at 100000), cast by the player (`Spell.Cast(PlayerRef, target)`, the MCM's "Kill
experience" 1, `CMB_RamKillXP`) or applied as the player's combat spell (2, `DoCombatSpellApply`), so the game's own
reward comes as for a shot; `Kill(PlayerRef)` follows 0.3 s later should the spell not have killed ("...: the player's
last hit (Spell.Cast) didn't kill it in 0.3 s (health N): Kill(PlayerRef) after it (no experience)."); 0 is the
2026-11-01a build's `Kill(PlayerRef)`. `DeathNote` logs the victim's level and the gain with whose it is ("dead, the
killer the player, its level N, the player's experience A -> B (+N: the game's, Spell.Cast)", or "(+0.0: none
(Spell.Cast: try "Kill experience" 2))"). Since test 43 three more actor rays, actors only and with no verdict, looking
only while the actor ray does (at 0.8 of `CMB_RamMinSpeed` or faster) and as far: one `HighRay` (96, the grips' height)
up for fliers (test 42's eyebot, its capsule between about 45 and 114 up, was seen only by the wheels' rays down, "a
ground ray passed through skeletonExport (layer 30)", and never asked about), and two at axle height `SideRays` (20) to
each side for flankers (20 plus an animal's capsule radius of about 25: 45 off the line, where the rider's capsule of 18
would brush it; test 42's hound was hit 67 behind the front wheel's edge, the mesh's wheel over it before it crossed the
centre line). An actor one of them sees that the actor ray didn't in the same frame is asked about, its hit told at
`Lead` and let by for `Pass` as at the centre ("(the high actor ray, 96 up)", "(the right actor ray)", "(the left actor
ray)" in the lines); one said no to bumps the capsule as before, and nothing further out to the side is seen. The
plugin's "rams:" lines in `CMB_Slope.log` say each step (seen and asked, the answer, the hit and the slowing, let by,
gone), the script's "Ram:" lines in the Papyrus log the answer, the push and the damage. `[Ram] Enabled=0` in
`CMB_Slope.ini` (the developer's switch, read again on getting on with the other `[Ram]` keys) asks about nobody and
brakes for everyone, as before test 41; the MCM's "Knock enemies over" is the player's; `HitHold=0` or `HitKeep=1` keeps
the speed at a hit; `AskGap=0` tells every ask as the actor is seen, as test 41's build did (with `AskAnswered=0` since
test 43). Test 43's seven, `AskAnswered`, `AskFree`, `YesKeep`, `HitGrace`, `HighRay`, `SideRays` and `Robots`, print on
a second "  ram:" line, each at 0 giving test 42's path for its own part (all seven at 0, test 42's knocking over
exactly, the log aside). Test 41 showed what the game had to: "rams: actors are found from their 3D: 'skeleton.nif'
(layer 30) gives actor 0001A4D7 (user data +0x110)", 16 hits told and 16 knocked over (feral dogs, coyotes, mutated
wolves, a radstag) at 497 to 934 a second with a force of 3.5 to 8.4, the distance they fly fine, and the round trip in
time for the hits (one answer took 541 ms). Test 42 showed that a vanilla robot race does carry the No Knockdowns flag
(ProtectronRace, large, 42E08901: hence `CMB_RamRobots`), and 17 knocked over in all (10 dogs, raiders 5 times, the
hound once and a shrew) with a force of 3.7 to 8.4. Still for the game to show: whether `PushActorAway` moves a No
Knockdowns race or a hovering eyebot at all. Since test 43 the script logs how far each pushed actor has moved at the
first poll 0.5 s or more after the push, by the real time (`PushMeasureAfter`; 0 gives test 42's): "Ram: X 0.5 s after
the push: moved N units."; one that doesn't move says the robots need another way (a stagger, or the brake as before the
list).

Test 44 (22:47 to 22:50: wolves, coyotes and vicious dogs in packs, and a protectron): of the dogs 26 were knocked
over or let through and 9 braked for ("some dogs just stopped the bike"): 7 "N past the front wheel, no answer in 25-234
ms: braked for", five first seen at or past the wheel (from the side, or queued behind the pack's asks, one at a time
and 200 to 300 ms each), two seen 177 and 191 out and answered after the bike, at 560 to 710 a second, reached them;
and 2 "under CMB_RamMinSpeed's 450" right after one of those. The protectron stopped the bike twice head-on ("protectron
stops bike when I'm aiming to ride through middle of it"): hit at 22:49:56.189 and at 22:50:13.906, it was ridden at
again 3.3 s and 3.9 s later, its entry still the old hit's, which lasts until `Pass` + 3 s, so `RamSeen` ignored it,
the actor ray's sightings too, `RamFree` refused it with `Pass` over, and the face rays called it "a wall ahead (82
deg): 260 past the front wheel at axle height (skeleton.nif, layer 30)"; the yes came once the entry had gone, at hit +
4 s, with the bike slowed to 72 and 444 by then by the brake and its capsule: "under 450: braked for". So since test 45
three more keys, on a third "  ram:" line (the two before word for word as they were), each at 0 test 44's path for
its own part. `PendingPass` (1): a small race (size 0: dogs, wolves, coyotes) whose ask is still pending at the `Lead`
point, at `CMB_RamMinSpeed` (or one of its graces) and never said no to, is passed (`RamPassOk`): let by as for a yes,
the throttle kept and the rays through it ("rams: X at the front wheel (N past it at N a second), its ask pending for
N ms: passed, its hit told when the yes comes (PendingPass, a small race)"); its yes (`RamPassHit`, from `RamFrame`)
tells the hit at the speed it was passed at and slows the bike as any hit does (`HitKeep`, `HitHold`), renewing
`HitGrace` when that speed was `CMB_RamMinSpeed` or more, told the hits' 0.12 s after one before it ("rams: X hit on
its yes, N ms after it was passed at the front wheel at N a second (PendingPass): told the script (ask N)", or "…, N
ms after the hit told before it: told the script once 120 ms have passed (ask N), so its 0.1 s poll reads both"); a
no, or no answer within `Pass` of the pass ("rams: X passed at the front wheel N ms ago, no answer since: the pass over
(Pass), braked for if ahead"), and it is braked for as before, one pass an approach; an entry mid-pass is never
evicted, and a medium or large race pending at the wheel is braked for as before, as the plan asked. `FaceActors` (1):
in `RamSeen` an actor whose hit was `Pass` or more ago and that comes back after half a second or more out of the rays
(`RAM_RESEEN`) is a new approach, its entry begun afresh and asked again ("rams: X seen again N past the front wheel
(the actor ray), N s after its hit, N s out of the rays: asked afresh (FaceActors)"; the script's yes went with the
push), one still in the rays after `Pass` (left standing at the wheel) braked for as before; back under
`RAM_SCRIPT_COOLDOWN` (3.3 s: `CMB_RamScript`'s `Cooldown` of 3 s, timed from its push 0.1-0.3 s after the hit is told)
after the hit, it stays the hit's, braked for as before, and is asked afresh when next seen once that is over ("…: asked
afresh 3.3 s after the hit, once the script's cooldown is over (FaceActors), braked for till then", then "rams: X seen N
past the front wheel (…), N s after its hit, the script's cooldown over: asked afresh (FaceActors)"), the speed this
approach first saw it at kept for `SeenGrace` (the review of test 45's build: asked afresh 1-3 s after the hit, it was
"knocked over less than 3 s ago", braked for, and never kept to again); and `AskFree` covers a race
in `CMB_RamRobots` of any size ("(AskFree, a large race in CMB_RamRobots)"), so the protectron, large, is no wall or
obstacle verdict while its ask is pending. `SeenGrace` (1.5 s, 0 to 5): `RamFastEnough` takes the entry and also
accepts, for `SeenGrace` after it, the speed this approach first saw the actor at (a sighting after half a second out
of the rays is a new first), as `HitGrace` does after a hit ("…: under CMB_RamMinSpeed's 450, but first seen N s ago
at N: knocked over all the same (SeenGrace)" in the hit's line); such a hit doesn't renew `HitGrace`, and a yes under
`CMB_RamMinSpeed` past both graces is braked for still, so the MCM's speed keeps its meaning. The third line reads
"  ram: PendingPass=1 FaceActors=1 SeenGrace=1.5: a small race whose ask is still pending at the front wheel passed,
its hit told when the yes comes; an actor hit and seen again asked afresh once the script's cooldown is over, a CMB_RamRobots race kept to
while its ask is pending (AskFree); CMB_RamMinSpeed judged by the speed an actor was first seen at for 1.5 s after",
each part's off form ending "as in test 44's build"; all three at 0 are test 44's knocking over exactly, the log aside.

Test 48 (2026-11-02a): it lost 40% of the speed at every knock-over for about 1.5 s, and a pack's hits compounded (0.6 x
0.68 = 0.41 at the second of two 0.5 s apart; the bike stopped). The hold is now 85% for 0.25 s and a pack shares one
dip (`HitChain`, 1.0 s, 0 to 5): a hit within `HitChain` of the last is held to `HitKeep` of the speed before the pack's
first hit, the hold renewed ("... the throttle held to 85% of it (765 a second) for 0.25 s (HitChain: of the 900 before
the pack's first hit, 0.30 s ago)"); 0 is the 2026-11-01a build's "the lower of two". Test 48's 10 brakes for asks
pending at the wheel were all medium races at the `Lead` point, 6 of them actors said yes to earlier in the ride and 3-4
first asks deep in a fight, and the brake took 2 u/s off before the hit: `PendingFoe` (2, 0 to 2) passes them as
`PendingPass` passes small races, from the ride's roster of the script's answers (32 entries, its last word wins, kept
for the ride) or, with 2, from the controller's `CMB_RamCombat` (0x894, written from `PlayerRef.IsInCombat()` at its 1 s
tick, at getting on and 0 at getting off: "Ram: the player in combat (CMB_RamCombat 1)."): "rams: X at the front wheel
(N past it at N a second), its ask pending for N ms: passed, its hit told when the yes comes (PendingFoe: a medium race,
said yes to 4.1 s ago this ride)" or "(PendingFoe: a medium race, the player in combat)"; a no while passed brakes at
once ("...: braked for (passed at the front wheel N ms ago)") and stays for the ride, so never anyone said no to this
ride; with 2 a companion's first ask in a fight is passed until its no (the script's answer, about 0.1-0.2 s), never
knocked over. Dogmeat is never asked (No Knockdowns). `PendingFoe=1` uses the roster only; 0 is the 2026-11-01a build's
brake. A fourth "  ram:" line follows the three before word for word: "  ram: HitChain=1 PendingFoe=2: a pack's hits one
dip, HitKeep of the speed at its first (hits 1 s apart or less); a medium race whose ask is pending at the front wheel
passed if said yes to this ride, or with the player in combat (CMB_RamCombat), braked for only on a no" (with an ESP
without `CMB_RamCombat`: "..., CMB_RamCombat not there (an older ESP): as PendingFoe=1"). A dip line a hit measures
`g_speedAlong`'s least in the second after it, so the next test separates the hold from the bump into the pushed body:
"rams: X's hit at 900 a second: the speed's low 817 (0.91 of it) 0.44 s after it; the throttle held to 85% for 0.25 s"
(under half: "...: the rest is the game's (the bike into the pushed body, a stagger, a wall)"; a chained hit: "held to
85% of the speed before the pack's first hit (HitChain)"). `HitKeep=0.6 HitHold=0.4 HitChain=0 PendingFoe=0` is the
2026-11-01a build's knocking over exactly, the log aside. In the harness (mode `hits`, 22, new): a hit at 900 holds the
input at 0.905 (85%; 0.730 at 60%), above it again 0.27 s after and full again 0.54 s after (1.17 and 1.44 s on the
2026-11-01a build); two hits 0.30 s apart, the least input after the second 0.905 (0.835 with `HitChain=0`); the
roster's re-ask passed and hit at 857 with the throttle full (`PendingFoe=0`: braked to 0.117, hit at 400).

Test 45 ("dogs still were inconsistent"): the dog FF0215FA and the wolf FF020983 were refused "knocked over less than 3
s ago" at 4:26 to 4:34 and 10:20 of its video (asks 58 to 62, 67 and 68: "is not to be knocked over, the script says:
braked for"), with nothing knocked over in the session before 10:49, and went over normally from 11:08, once four new
knock-overs had cycled the script's four-slot ring. That ring (`knocked[]`, `knockedAt[]`) and the refusals'
(`refusedKeys[]`, `refusedAt[]`) are stamped with `Utility.GetCurrentRealTime()`, which starts again with every launch,
and are kept in the save: the tester's save was made in test 41's session right after knocking over these very dogs, so
their stamps lay in the new session's future, where "now - at < 3" held (test 44 shows the same at 22:41:58), and the
refusals' stamps hid most of those lines (`RefusalIsNews` said no). Since test 46 `DropStaleStamps` clears any
knock-over, refusal or push stamp later than now wherever they are read (`StartRide`, `KnockedWithin`, `RefusalIsNews`,
`MeasurePushes`), logging "Ram: N stale knock-over/refusal stamps from an earlier session cleared." once when there were
some, and `StartRide` clears the refusals' ring at every getting on, as it clears the pushes and the yeses (the
knock-over ring is kept, so an actor knocked over just before a quick get-off and on is still in its 3 s). No switch: a plain
fix, and Papyrus only, so the harness has no test of it. The controller's headlamp stamps, real time kept in the save
too, are reset the same way (`FollowHeadlamp`: `lampPlacedAt` later than now, `lampRetireAt` later than now + 2.5 s);
its `teleportAt`, `busySince` and `busyWatchFrom` are reset on a load or used only while busy.

Test 46 showed it working ("Ram: 8 stale knock-over/refusal stamps from an earlier session cleared." at the load, no
"less than 3 s ago" refusal, FF0215FA, refused so in tests 44 and 45, knocked over five times; 27 of its 32 knock-overs
came with AI processing off, after the console's `tai`, the animals standing still), and the build-27b check named what it
leaves: only a stamp later than now is dropped, so an earlier session's that happens to fall in this session's last 3 s
(`Cooldown`) still counts. Since test 47 the controller's `OnGameReloaded` calls the ram script's `ClearStamps` at every
load, before a ride's `StartRide`: `Utility.GetCurrentRealTime()` starts again with each launch, so no stamp from before a
load means anything after it, and every one, the cooldown's knock-overs, the refusals' log stamps and the pushes not yet
measured, is cleared, "Ram: N knock-over/refusal stamps from before the load cleared." when there were some
(`DropStaleStamps` stays where the stamps are read). Without the ram script on the quest each load logs "Ram:
CMB_RamScript is not on the quest: ClearStamps not called, nobody is knocked over.". No switch, Papyrus only, as before.

## WallStop beside the turn, the climb's boost and barriers on legs (F4SE plugin, 2026-11-01a)

Test 47 rode Sanctuary's loop at full speed: 86 WallStop lines cut the throttle to 0%, 56 of them at 150 or more with the
hit ahead of the front wheel (*Tilt* above has WallStop itself). Ten were the longer rays while the climb's boost was on
("looked for that far, past FaceLook's reach": `bool longer = !g_climbOn` made them straight, as far as the raw need and with
no floor), 28 were FaceLook's own straight rays meeting things beside the curve the bike was on (at the 100 to 285 deg/s it
turns at speed the straight line leaves its path within FaceLook's reach: 120 off it 294 from the rider at 150 deg/s and
889), and three boosts over kerbs were cut by such walls. Two keys answer them, each read again on getting on, each 0 giving
the 2026-10-31a build:

- **`[Steer] WallStopClimb=1`**: while the boost is on the longer rays are as without it (`longer = !g_climbOn ||
  g_wallStopClimb`: their reach, `WallStopArc`'s arc, `WallStopPersist`'s floor and its words), and the climb's wall test
  counts only the face rays' own walls (`g_faceWallClimb`: not one the longer rays see past FaceLook's reach, nor one only
  one path meets, below; `ClimbRays`' `CLIMB_WALL` needs it). A far wall then neither cuts a boost on its way over a kerb
  nor refuses one (in 2026-10-31a a WallStop verdict 600 ahead also refused a kerb's boost); a wall within FaceLook's reach
  still does, unless only one of FaceArc's paths meets it and WallStop isn't already easing it.
- **`[Steer] FaceArc=90`** (deg): FaceLook's three rays are cast again along the arc the heading's rate puts the bike on
  (`CastArcEx`: 2 to 4 chords, one a 0.3 rad turn at most, each ray cut where the arc has turned FaceArc, never left out),
  after the straight ones and before the longer rays. The merge: a straight hit at or behind the front wheel's edge, or an
  actor, keeps the straight verdict (UnderBikeTop, the obstacle at the wheel, under the bike, the rams); else the arc's hit
  past the wheel (or beside it, for a raw wall already being eased: the review's xCounts care) is the verdict, alongside by
  the heading or the chord's heading and confirmed along that chord (`FaceAlongConfirmed` from its start), though an arc hit
  that is neither a raw wall nor alongside gives way to a raw wall the straight rays meet; else, where the arc's axle ray
  stopped short of the front wheel's edge or the arc ends before it (turning hard at low speed: nothing says the bike passes
  the wall), the straight verdict as in 2026-10-31a; else a raw wall the straight rays alone meet keeps their hits; a
  straight obstacle that is neither a wall nor alongside gets no verdict. A wall
  both paths meet (each raw: past the wheel, its hits at axle height and 1.5 radii `WallAngle` or steeper, not alongside by
  its normal) is WallStop's as before; one only one path meets (`faceOneOnly`) gets FaceLook's own ease, its distance over
  FaceLook's span, never WallStop's cut. A wall already being eased by WallStop stays WallStop's when only one path still
  meets it: braking in a turn tightens the arc (the rate over a falling speed) till it curls away from a wall the bike still
  goes into, as the longer rays keep a wall being eased along their arc (the harness's first run had the bike 18 into the
  rail met while turning without it). That is the same wall (the review of this build: any WallStop run alive took every
  one-path wall to WallStop's cut, at the far wall's need): the run's object (`g_stopObj`, kept with `g_stopBeyond` and
  `g_stopEase` on each of its frames), or any wall while FaceLook's own rays fed the run (a guard rail is several
  objects). A wall only one path meets while WallStop eases another, farther one gets FaceLook's ease held to no more than
  that run's last ("…, the throttle eased to 47% (75% by itself, held to WallStop's for the wall it is easing: FaceArc); the
  straight rays only, beside the turn's arc: FaceLook's ease (FaceArc), …"), and keeps the run alive: the longer rays aren't
  cast past it, and the far wall let go would be met again with a fresh floor. Arc hits on actors are left out. Up to 12
  casts more a frame while turning.

Every wall line (`rays: … ahead`) now ends with which rays saw it and the heading's rate: "; the straight rays, the heading's
rate +12 deg/s", "; along the turn's arc (FaceArc), the straight rays meeting it too, …", "; along the turn's arc only:
FaceLook's ease (FaceArc), …", "; the straight rays only, beside the turn's arc: FaceLook's ease (FaceArc), …", or for a wall
already being eased "…, a wall already being eased: WallStop's (FaceArc)"; the longer rays' lines keep their own words. A
verdict passing from one path to both, or back, is logged as a change (the `moved` rule). The settings line adds "; while
the climb's boost is on, as without it, a wall they see past FaceLook's reach neither refusing nor cutting the boost
(WallStopClimb)" (off: "(while the climb's boost is on, that far when FaceLook's reach is shorter: WallStopClimb=0)") and
"FaceLook's rays along the turn's arc too, as far as it turns 90 deg: a wall both meet eased by WallStop, one only one meets
by FaceLook's own ease (FaceArc)" (off: "FaceLook's rays straight along the heading: the straight rays alone (FaceArc=0)").
Replayed on test 47's log (`cuts.py`), about 19 of the 38 cuts by the longer rays and the straight ones go, about 9 stay
(the long low rail of 19:46:33, the guard rail and things at the wheel among them) and about 10 can't be told; test 48's
lines, with the rate in each, decide. The 18 to 22 cuts by the longer rays' arc sweeping onto a thing already inside the
need are not addressed.

**`[Steer] ClimbLegs=145`** (deg; test 47's 19:46, wooden road barriers met at 10 to 30 deg read "108 ahead at 4, 105 at 10
(108 deg) … at 18 132 ahead: round, receding toward its foot (ClimbMaxTop)" and were climbed: the rays at 4 and 10 met a
leg leaning that way, and a log's lower half reads 104 to 141 deg for logs 18 to 60 across, so the angle alone can't tell
them apart). `ClimbBeam`'s round face (100 to ClimbLegs deg at its foot, with something at ClimbMaxTop) is a log only if it
is solid at 4: `ClimbOnLegs` casts rays two capsule radii (36) to either side along the face's line (its level normal at
ClimbMaxTop if usable, else at 4, else the heading's square, as `ClimbNarrowAcross`), from where the line's own ray at 4,
10 and ClimbMaxTop met it, 36 out, level into it for 108; one side passing under it at 4 and meeting it at 10 or 18 is a
beam on legs (`MAXTOP_LEGS`, `CLIMB_LEGS`: no boost, as a beam). A log (solid at 4 both sides), its end, a stump and the
ground or a kerb under the side ray at 4 are not legs. A barrier met at 20 deg slides along and never stalls, so it gets a
line of its own while not stalled, once per object per 2 s: "climb: a low face at the capsule (…): … (107 deg), nothing at
31.9 within N; at 18 N ahead: round at its foot but on legs (the ray 36 to the left across its face passes under it at 4,
meets it at 18; ClimbLegs): not climbed"; stalled, "not climbed: a beam on legs: …". A log the test passed says so in its
boost's line ("…: round, receding toward its foot (ClimbMaxTop); solid at 4 to either side across its face, not on legs
(ClimbLegs)"). The climb's settings line ends "; a face round at its foot (100 to 145 deg) climbed as a log only if the
rays two capsule radii to either side across it meet it at 4 wherever they meet it higher (ClimbLegs: a log, not a beam on
legs)" (off: "…climbed as a log without asking (ClimbLegs=0)"), with ClimbMaxTop on. 145 leaves the overhangs (150 and up)
alone. A log lying across a dip, 4 or more off the ground 36 along, reads as legs (test 48 asks for log times);
`ClimbBeamLow`'s faces under 18 and a judgement while a kerb's boost is on are unchanged.

The harness (mode wall, 19, 34 checks with the four every mode makes, on mode climb's world and `[Steer]` with the three
keys written so each ride can rewrite it to 0): turning at 100 deg/s at 900, a post on the heading's line 200 past the
front wheel (beside the turn) is FaceLook's ease, 76% (FaceArc=0: WallStop's 0%), one on FaceLook's arc 200 past it is
"along the turn's arc only" under 76% and falling (FaceArc=0: nothing seen, the throttle full); the boost on at a log,
the post beside the turn doesn't cut it (FaceArc=0: "a wall ahead (the face rays' verdict)"); at 40 deg/s a rail across
the heading is met by both, cut to 0% within a frame 250 past the front wheel at 900 (inside the need: met), stopped 5
short 100 past it at 400; the review's three: turning at 60 deg/s at 900 with the speed held, a wall staying 670 ahead
eased by WallStop seen by the longer rays, then a post 100 across (another object) on the heading's line 200 past the front
wheel: FaceLook's ease held to the far wall's, about 47% (the build before: "a wall already being eased: WallStop's", cut
to 0% at once), and the far wall's run kept through it, no fresh floor after (before: the cut lost the far wall, the
throttle full); at 60, turning as hard as the plugin lets (about 56 deg/s, the arc's 90 deg ending before the front
wheel), a rail 20 past the front wheel is WallStop's 0%, "the straight rays" (before: FaceLook's 87%); at 100 deg/s a
ramp rising at 35 deg on the arc and the post on the heading's line: the post FaceLook's ease, 75% (before: dropped for the
ramp's no verdict, the throttle full); the boost on at a log, a rail 650 past the front wheel is first seen 650 past it by the longer
rays with the floor, the trace's "climb 85 for", the boost never cut, "over it" after (WallStopClimb=0: first seen
within 405, at 149 as the log slowed the bike, cut to nothing); the rail first, then the log: the boost let on
(WallStopClimb=0: refused); a barrier on legs met square and at 18 deg not climbed, its lines, held (ClimbLegs=0: round,
the boost); a log 25 across met at 30 and 18 deg climbed, not legs. Mode climb keeps its 125 with the new defaults, the
same checks with run-to-run jitter in their figures: of its 97 wall lines 61 are FaceLook's, all "the straight rays",
and 36 the longer rays'; none took the arc's path.

### Narrow things, kerbs and rails (F4SE plugin, 2026-11-02a)

Test 48: two full stops a minute, mostly at mailboxes, lamps and signs beside curving roads (48 WallStop cuts to 0%
ahead of the front wheel in 36.9 minutes); 53 holds to `ObstacleThrottle`'s 0.55 at kerbs, a median tenth of the speed
lost each, quartiles up to half; and "stopping me randomly" alongside rails, slide holds that came late or were ended by
a wall verdict (21 in 37 minutes, 12 of them full stops from speed). Four keys in `[Steer]`, each read again on getting
on, each at 0 the 2026-11-01a build:
- **`WallStopNarrow`** (40, 0 to 120) tests a WallStop wall for width with two rays parallel to the way the axle ray met
  it, 40 to either side, from twice that before the hit to half past it, on all three ray paths (the longer rays'
  chord, FaceArc's chord or the straight ray along the heading). A thing both pass (or that meets an actor's layer) is
  narrow and gets FaceLook's own ease, ahead over span, never WallStop's cut ("(narrow: the rays 40 to either side of
  its path pass it: FaceLook's ease, not WallStop's (WallStopNarrow))"); while another object's WallStop run is alive
  it is held to that run's ease and keeps it alive ("(N% by itself, held to WallStop's for the wall it is easing:
  WallStopNarrow)"), and it neither refuses nor cuts the climb's boost. An object found wide stays wide 0.5 s, no side
  rays meanwhile; a cut's line says why it is wide ("(wide: the ray 40 to the right meets it 12 nearer, the one to the
  left passes: WallStopNarrow)", "(wide: the rays 40 to either side of its path meet it, the left level with the hit,
  the right 12 nearer: WallStopNarrow)", "(wide: found so 0.25 s ago: WallStopNarrow)"). A post ridden straight at is
  eased and bumped, not stopped 40 short (TESTING's question T1). With no key, a WallStop run cut under a fifth on the
  wall the last line had at half or more is logged once more ("(the verdict moved: the last line had mailboxStand02 at
  100%)").
- **`LowObstacleThrottle`** (0.85, 0 to 1): the "lower than 1.5 wheel radii" verdict alone holds the throttle to it
  ("(LowObstacleThrottle)"); faces under `WallAngle`, walls held back for now and the cases under the bike keep
  `ObstacleThrottle`, and `ObstacleThrottle=0` still stops at all of them.
- **`SlideRestore`** (0.5 s, 0 to 2): `AfterInput`'s cap branch records the throttle when the `Lead` cap begins to bind
  (a bind after a frame without it is a new one); `SlideHoldCap` starts the hold from that value if it was within
  `SlideRestore` and higher, and puts the throttle back up to it ("; back up from 0.55 to what it was when the cap began
  to bind 0.33 s before (SlideRestore)" inside the hold line's parenthesis).
- **`FaceAlongKeep`** (1.0 s, 0 to 3; only with `FaceAlongRays=1`): a face the side rays no longer confirm stays
  alongside for `FaceAlongKeep` after its last confirmation while it is the same object, its normal still says
  alongside (under `FaceAlong`) and its hit is ahead of the front wheel; only a real confirmation renews it ("left alone
  (the rays either side don't say so now; the same face confirmed 0.01 s ago: FaceAlongKeep)"). A 35-degree turn into
  the same rail is a wall.

In the harness (mode `wall`, 19): 52 checks (34 + 18: WallNarrowTests 10, SlideTests50 6, LowObstacleTests50 2), each
new one failing on the 2026-11-01a DLL and passing as that build with its key at 0; the drive-1 review ride's post is
placed by a frame hook once the far wall's input has stayed in 0.15-0.68 for 0.2 s (the load-sensitive check of the
2026-11-01a merge, hardened).

### Narrow by its own reference, rails at 1.5 radii, and the sidestep (F4SE plugin, 2026-11-06a)

Test 49: a mailbox ridden at head-on read wide by its own side ray (the ray 40 out met the mailbox itself 130 out) and
the bike stopped dead; the tester wanted a sidestep to the open side. The build-49 check's finding 3: the side rays only
at axle height, so a rail over its posts read narrow. Both keys 0 run 2026-11-02a's `WallNarrow` and its notes
untouched.
- **`[Steer] WallNarrowSame`** (1): `RefFor3D` finds the placed reference of a ray's hit (any TESObjectREFR in the user
  data, up the parents). A side ray meeting the hit's own reference casts a far ray 2 W out (80); that one passing
  leaves the side open ("same"). Its window (2 W before to W/2 past) is moved along by where the side ray met the thing,
  so it holds where a straight face through the hit and that meeting is at 2 W out: a long wall, fence or car flank met
  at a slant still reads wide (WallStop's stop), as in 2026-11-02a; only a thing that ends within 80 on that side reads
  narrow (the review's DR1: with the side ray's own window a long face 45-63 deg off square read narrow on its nearer
  side, and a face's end 14-27 deg off square; mode 19's ride 4b, a jersey barrier 50 deg off square, stops). Wide: a
  met ray that isn't the same, or both sides closed, at one height or across the two. The notes name the side ray's
  object and reference: "(narrow: the ray 40 to the right meets it level with the hit, its own reference 0003A1B0, the
  one 80 out passes; the one to the left passes: FaceLook's ease, not WallStop's (WallStopNarrow))", "..., and the one
  80 out too", "..., another reference (0003A1B3)", "..., no reference". The both-open narrow note is 2026-11-02a's text
  exactly.
- **`[Steer] WallNarrowHigh`** (1): the side pair is cast at 1.5 wheel radii too ("the rays 40 to either side of its
  path at 1.5 radii meet it ..."), so a rail over posts is a wall.
- **`[Steer] Sidestep`** (40 deg/s; `SidestepMost` 12, `SidestepShift` 60, `SidestepFrom` 250): a narrow verdict ahead
  of the front wheel (FaceRays' narrow branch) offers a sidestep; FrameSteer takes it in its PASS branch with no side
  key (`|x| > 0.05` on a fresh read), no turn asked, at `SidestepFrom` or more. The side: the rays' open side, else the
  face's slant, the turn, the right. Three rays to that side must be clear (both open: the other side tried): level out
  of the capsule by `SidestepShift` and its radius (78: a flank, rail or wall beside the bike); from the capsule's edge
  on that side to the lane's edge along the step's own chord, to where Sidestep's law reaches `SidestepShift` at this
  speed (538-560 at 900, 360 at 250), capped at the lane ray's reach; and `SidestepShift` to that side along the old
  line to 2 W past the hit (the review's DR2: that last ray alone never crossed a rail parallel at 20-60 across and
  started inside a car's flank at 45). Else "sidestep: none for PostA: the right (both open) is taken: the ray out 78 to
  its right met Sedan02_Postwar 45 across", "... the ray from the capsule's right edge to its lane (60 across in 538)
  met GuardRail01 152 along" or "... the ray 60 to its right met StationWagon02 541 along". The plugin owns the heading
  for at most 2 s: OUT at `Sidestep` to `SidestepMost`, HOLD, BACK once the capsule's measured place across (smoothed
  0.05 s) plus what BACK adds reaches `SidestepShift`; clamped by speed over the turn radius, not eased (the ease would
  hold the heading still at the turn back). While it runs FaceArc is off and the longer rays look along the old line. A
  wide wall verdict, an actor ahead, a side key, the brake or the game's own target moved by the mouse ends it
  ("sidestep: let go after 0.10 s: a side key (the capsule 1 across)"). Never for walls, cars or people. Lines:
  "sidestep: PostA (layer 1) narrow 790 past the front wheel at 899: to the right, both sides open: the right, up to 12
  deg at 40 deg/s for 60 across (Sidestep)" and "sidestep: over after 0.71 s: the heading back on its line, the capsule
  57 to the right of the hit's line, ...". In the harness 57 across, at most 12.0 degrees, over after 0.71 s. The
  settings are a line of their own after the lean steer line ("  steer (2026-11-06a): ..."): that line is 3641
  characters and the harness reads 4096 a line. In the harness (mode `wall`, 19): 75 checks (52 + 23), mode 19 riding
  `Sidestep=0` for its 52 older rides (2026-11-02a's driving), the sidestep rides 40; the frame cost 42.4 us against
  39.3 (+3 us, within the +10 us budget); the drive unit's 20 fail on 2026-11-02a's DLL (54 ok, 18 FAIL) but the off
  values' own, the review's 3 (ride 4b, the two rides 9b) on the units' merged DLL.

## Landings (F4SE plugin, since the 2026-11-01a build)

Test 47: "character still stops/stutters when jumping off high ledge" (and test 42's 17p before it). After each drop of
about 4 m at full speed the bike fell to about half its speed for about 0.7 s (937 → 486 on the 0.2 s measure, 300-390 on
the raw positions) and came back, a quarter second of travel lost, with the plugin's throttle and input at 1.00 all the
way. Test 43's `LandHold` had taken the plugin's own share off (the Lead cap following the speed down); what was left is
the game's. The player's behaviour graph (`MTBehavior.hkx`, read with the scratch tools, nothing of it in the repo) has
the landings as wildcard transitions of its jump state machine: `jumpLand`, `jumpLandToRun` and `jumpLandToWalk` go to
the soft landing states, which set `bGraphDriven` (the hops of 0.35-0.56 s kept 94-98 % of their speed);
`jumpImpactLand` and `jumpImpactLandToRun` go to the hard ones, which set `bAnimationDriven`: the movement then follows
the landing clip's root motion, about 410 units a second whatever the speed (the riding SpeedMult doesn't apply to root
motion), until the clip's `jumpEndToRun` leaves the state 0.1 s in and the graph's 0.5 s sync blend brings the speed
back. The engine picks the hard one for a fall of somewhere between about 210 and 290 units (or 0.56-0.67 s; test 47's
logs can't tell which). Shortening the clips saves at most 0.1 s, a clip with root motion at the bike's speed is one
fixed speed for every landing, and holding the controller's fall height would take fall damage with it; so:

**`[Steer] LandSoft=1`**: while riding, the game's hard landings go to the graph as its soft ones. The plugin wraps
PlayerCharacter's `IAnimationGraphManagerHolder::NotifyAnimationGraphImpl` (vtable slot 1 of the holder's sub-object):
the base is found in the player's class hierarchy by its RTTI name, its `mdisp` is the sub-object's offset (+0x48 in
CommonLibF4's layout), and the wrapper goes on only if that sub-object's vtable has a complete object locator naming
`PlayerCharacter` at that offset and its slot 1 is in the game's image ("graph: the player's
IAnimationGraphManagerHolder isn't where its RTTI says (...): the game's landings as they come" otherwise). Only
PlayerCharacter's own vtable for that base is patched, so no NPC passes through it, and off the bike the wrapper is one
test and the game's own call. Riding, it reads the event's name (a `BSFixedString`: a pool entry, the text after its
0x18 header, a shallow entry followed to its leaf, a wide one left alone), and `jumpImpactLandToRun` goes on as
`jumpLandToRun`, `jumpImpactLand` as `jumpLandToRun` when moving (forward held, or the speed along `LandStop` of the top
or more) and as `jumpLand` at a standstill. The caller's string is never written: the original gets a `BSFixedString` of
the plugin's own. The soft names are the game's string pool entries: with `LandSoftNames=pool` (the default) asked of
`BSStringPool::GetEntry` (CommonLibF4's ID 2268729) once, at the first ride with `LandSoft=1` (with `LandSoft=0` the
game's function isn't called: only the wrapped slot is), only when the Address Library has the
five game objects the engine sound cross-checks where the plugin has them and the function is in the game's code (a line
before the call says where); otherwise, and with `LandSoftNames=game`, taken from the game's own first `jumpLandToRun`
and `jumpLand` of the session, each with a reference of the plugin's (the count in the entry's flags, as CommonLibF4's
`acquire`), and a hard landing before that goes through as it comes. Fall damage is the engine's own at the landing,
apart from the graph, and the Papyrus fall-damage path is unchanged. The wrapper may run off the main thread: it reads
memory through the per-thread readable check the movement output's hook uses, records each landing and fall event in a
ring of eight (its sequence written last), and logs nothing; the frame side matches the events with its own landings
(an event may come a frame before the landing the plugin sees, or after it, within 0.3 s). The lines: "landing: the
game's jumpImpactLandToRun (+0.00 s, after jumpRunningFall at -0.72 s), passed to the graph as jumpLandToRun (LandSoft)"
(or "a soft landing: as it is", "passed as it is (LandSoft=0)", "passed as it is (no name for the soft landing yet: ...)",
the pool's case "LandSoftNames=pool gave none: the game's own first one names it",
or with no landing of the plugin's within 0.3 s); "landing: no landing event from the game seen by the hook in 0.3 s
(LandSoft can't act on it in this game: tell us)" once a ride, three a session, the one thing only the game can settle;
the landing line gains the drop, "the fall 334 a second (286 below its highest point)" (the highest z since the first
frame in the air), and the hold's end line its lowest on the 0.05 s measure. `LandSoft=0` is the 2026-10-31a build's
landing: the wrapper passes everything through as it comes and only tells. LandHold, LandAir, LandStop, LandSink and
LandSpeed are as they were; the seated hard-landing clips stay for `LandSoft=0` and for a game the plugin can't hook.

The harness: the fake player's class has the holder as a base at +0x48 with its own vtable, whose slot 1 is the fake
graph. The fake graph counts what it gets by name and, as the game's graph, starts the landing cut (the speed times 0.35
for 0.45 s, test 42's) on the hard landings only: the cut moved there from the fall's landing, which now sends the
game's event through the holder's vtable (`jumpImpactLandToRun` for the 180 drop's 497 a second, the soft one for
backing's 60 drop, `jumpRunningFall` at the take-off). Mode full's Address Library has `GetEntry` and the five
cross-checked objects. In mode full, with no new frames: the 180 drop at the top speed reaches the graph as
`jumpLandToRun`, the string pool's entry, with no cut, the hold's end at 0.9 of the landing's speed or more (test 47's
were at 0.52), the drop 180 ± 5, +0.1 to +0.45 s at 0.9 of the speed; with `LandSoft=0` (and LandHold, LandSink and
`[Fx] Land` off) the graph gets `jumpImpactLandToRun`, the cut runs and the old checks of test 42's landing pass as
before; the landing against something gets the soft one; the wrapper is put on once and `GetEntry` called twice; off the
bike a hard landing reaches the graph as it is, with no line. Mode 21 (its library has no `GetEntry`): its first ride, with
`LandSoft=0` (the start's 1 rewritten before it), doesn't ask the pool; at the next, with `LandSoft=1`, the pool's line
says so, a hard landing before any soft one goes through as it is ("no name for the soft landing yet"), the game's
`jumpLandToRun` is kept (its entry's count 3 → 4), then a hard landing reaches the graph as it, a `jumpImpactLand` at rest
as `jumpLandToRun`, and as `jumpLand` once that is the game's own too. Mode transposed: with the holder's `mdisp` moved
to 0x50 the wrapper isn't put on and the line says why.

## Bike sounds: landing and water (the controller and the F4SE plugin, since the 2026-11-01a build)

Test 47's last two wishes: "sound when jumping off of a ledge or anything else, currently the sound used is default
character jump effect, another sound would be when bike is crossing a water". The user's condition: in this build if
the game's own sounds can be used. They are, by FormID, unchanged: the controller plays them from three FormLists of
ours (`CMB_FxLandSounds`, `CMB_FxLandSoundsAlt`, `CMB_FxWaterLoops`), so their categories and output models are the
game's (docs/ASSETS.md "Borrowed from the game" lists them, to be swapped for our own). The rider's own jump and landing
sound is the shoes' (the seated jump and landing clips keep the vanilla `JumpUp` and `JumpDown` footstep tags; nothing
in the graph acts on them): the controller mutes the player's footstep category while riding (MCM "Mute the rider's own
jump and landing sounds"). The Papyrus side is the controller's (the mute, playing the landing, starting the water loop
and handing its id over, the audition); the plugin's side, here, tells the script when a flight lands and how hard, and
drives the water loop. They talk through seven fixed-ID globals of the ESP (0x884-0x88A; an older ESP has none: "the fx
globals 0 of 7 found ...: none used, no landing cue, no water loop", and nothing of this happens):

| Global | Written by | Holds |
|---|---|---|
| `CMB_FxVolume` (884) | the MCM, "Bike effects volume" (90) | percent; the water loop's level and the script's landing level are times it |
| `CMB_FxWaterId` (885) | the script: the water loop's instance id at getting on (after the engine's start, outside `busy`) and after a load into a ride; 0 at `FinishRide` and `EmergencyReset` | 0 none: the plugin lets go |
| `CMB_FxDriven` (886) | the plugin, at the hand-over (the script writes it 0 with each stop: instance ids can repeat after a load) | the id: driven; minus it: declined (`[Fx] Water=0`, no usable Address Library, the loop not playing, 30 refused calls in a row). The script polls it for 0.5 s and stops a declined or unanswered loop, and one declined later (the 30 calls) at its next ride tick |
| `CMB_FxAir` (887) | the plugin | 0 on the ground; 1 once the bike has been `AirMin` (0.35 s) in the air (a flight); 2 for `AirHold` (0.3 s) after its landing, then 0; 0 at a ride's start and end, and for a last frame in the air over 300 (a load, a teleport) |
| `CMB_FxLandSeq` (888) | the plugin | the flight's number, one more at each take-off past AirMin, from the global's own value at each ride's start (a save's numbers never repeat) |
| `CMB_FxLandLevel` (889) | the plugin | the landing's level 0-1 by the fall's speed at the landing, `clamp((fall - LandFrom) / (LandFull - LandFrom))` (40, 400), written through the flight when it moved by 0.01 and at the landing; 2 more into water deeper than 2; -1 no cue (the ESP's, `Land=0` from the ride's start, and the script's at each ride's end, so a game without the plugin never reads a stale level): the script's own level |
| `CMB_FxLandPlayed` (88A) | the script, after playing a flight's landing sound | the flight's number; minus it for a level-0 cue (nothing played, since 2026-11-02a); the plugin logs the delay |

AirMin is past LandAir's 0.3 s on purpose: the fall transition blends the run clip out over 0.25 s, and its sync markers
must not read as a landing. The script plays the sound on the landing clip's first event (`JumpDown`, or the sync
markers while `CMB_FxAir` says a flight has just ended: the female soft running landing has no `JumpDown`), at the level
the plugin left. The landing's lines: "fx: landing cue 3 after 0.68 s in the air (the fall 208 a second): level 0.47
(-5.3 dB at the script's -10 dB floor; -9.5 at the 2026-11-01a build's -18), onto the ground" (or "into water 12.3
deep"), "fx: no landing cue after 0.32 s in the air (a hop under AirMin 0.35: no flight), ...", "fx: the script played
cue 3's landing sound 0.031 s after the landing" ("late" over 0.1 s), "fx: the script played cue 3's landing sound 0.000
s before the landing (a cue event before the plugin's landing frame)" when `CMB_FxLandPlayed` already holds the flight's
number at the plugin's landing frame (no 2 s wait then: a cue event that came first, or a late one of the last landing's
clip read in this flight), or after 2 s "fx: cue 3's landing sound not played by the script (...)". Test 47's ten
landings with a fall would have read 0.07 to 0.82 (the 4 m drop: the heavy tyre and the clunk).

The controller's side (`CMB_ControllerScript`, the `Bike_Effects` group's properties; each part has an MCM switch whose
off value is 2026-10-31a's):

- **The rider's own jump and landing sound.** The seated landing clips keep the vanilla `JumpDown` and `JumpUp` events,
  footstep tags that only make the shoes' sound (nothing in MTBehavior.hkx acts on them). On getting on and after a
  load into a ride the controller mutes the game's `AudioCategoryFSTplayer` (0F5FFC, the player's own footsteps),
  `UnMute` first so a load's or a counted mute is never on twice; `FinishRide` (every way off) unmutes it, and the
  emergency reset, a load off the bike and a new game unmute it whatever the script believes. `CMB_FxMuteRider` (MCM
  "Mute the rider's own jump and landing sounds"); `SoundCategory`'s Papyrus side is the Creation Kit wiki's (no source
  here to audit).
- **The landing.** The plugin judges the flight and the level (its `[Fx]` section); the script plays the sound on the
  landing clip's first event. While riding it registers for `JumpDown` (every landing clip but the female soft running
  one) and the sync markers `SyncRight` and `SyncLeft` (that clip has only those at its start), and dispatches them
  first in `OnAnimationEvent`, ahead of the footstep watch, which would take every `SyncRight` of the seated clips for a
  standing footstep. It reads the plugin's globals (the table above) and writes the flight it played to
  `CMB_FxLandPlayed`, and the plugin logs the latency. The rule (`LandingCue`, `fxCueBusy` claimed first, so two cues of
  one clip play once): a `JumpDown` plays unless that flight's sound has played; a sync marker plays only right after a
  flight not yet played, waiting 0.05 s once if the plugin still says airborne. Without the plugin `CMB_FxAir` stays 0
  and the level -1: a `JumpDown` plays at 0.5, a sync marker never. `PlayLanding`: volume = the bike effects volume
  (`CMB_FxVolume`, 90) x 10^(-range x (1 - level) / 20), the range the MCM's (`CMB_FxLandRange`, 10 dB; 18 the
  2026-11-01a build's); the light tyre thump under 0.45, the heavy one from it, the metal clunk on top from 0.6 (4 dB
  under); into water the splash, the heavy one from 0.6. `CMB_FxLandOn` (MCM "Landing sound": read by each cue once
  `fxCueBusy` is claimed, so off takes effect at once; on, the cues are watched from the next ride tick); `set
  CMB_FxLandPick to 1` plays the second list.
- **The water.** From the engine's start timer, after the engine's loops are offered (outside `busy`, so the wait holds
  nothing up), and after a load into a ride: `CMB_FxWaterLoops[CMB_FxWaterPick]` is played on the player at volume 0 and
  its instance id written to `CMB_FxWaterId`; the plugin answers in `CMB_FxDriven` (the id: driven by the water's depth
  over the feet and the speed; minus it: declined, and the script stops it), waited for 0.5 s as the engine's loops are,
  then stopped. The plugin asks `IsPlaying` of it each frame for up to 0.35 s from its first look, as of the engine's
  loops (a streamed loop can take a few frames to start: the engine's took about 70 ms in test 47), and only then
  declines ("declined (it doesn't play, 0.35 s after its first look)"; the driven line says "; playing 0.05 s after its
  first look" when it waited). A ride end during the play is caught by a counter (`fxWaterSet`), as `engineSet` does for the engine.
  `FinishRide` stops it and writes 0. `CMB_FxWaterOn` (MCM "Water sound"), read on getting on. While riding the wade
  watch's `IsInWater` is logged too ("In water while riding (the wade watch): True"), to compare with the plugin's depth.
- **The audition.** `cqf CMB_ControllerQuest FxAudition N` plays a candidate at the effects volume (100 if it is 0): 0-4
  the landing list, 10-14 the second list, 20-23 the water loops for 3 s; instance 0 means it didn't play. Since
  2026-11-02a (test 48 typed all three batches with the console open, the game paused) it waits for the menus to close
  ("Bike sounds: audition -1: waiting for the menus to close (the console pauses the game); it plays 0.50 s after."),
  then plays 0.5 s later, those typed together 2.5 s apart; the codes are our own records, plus 100 the game's (100-104,
  110-114, 120-123), -1 every one of ours and -2 every one of the game's (14 each, about 47 s; each holds the queue for
  its whole sequence, so `-1` and `-2` typed together play one after the other); each line names the record, the
  instance id and ", after the menus closed".
- **Next:** a take-off sound needs the plugin to play sounds itself (`BSAudioManager::GetSoundHandle`'s arguments,
  unknown); then our own sound files.

**Heard at last (test 48; since the 2026-11-02a build).** Test 48's landings and water played (18 landings with
instance ids, the water loop driven 463 s) and weren't heard: the borrowed records' own static attenuation (4.9 to
17.2 dB: the light tyre 11.9, the stream loop 17.2), their output models' fade at the riding camera's 450 (about 40% for
the light tyre's), and the script's -18 dB floor put a light landing about 37 dB under its file, the heaviest 13, the
water loop 22, 25 dB or more under the engine. So the mod has 13 sound records of its own over the game's files by path
(0x89E-0x8AA, `CMB_Fx*SD`: static attenuation 0, `AudioCategorySFX`, the game's pitch and loudness variation kept,
through `CMB_SOMMonoFx` 0x89D, the engine's model's fields: full to 600), in three lists in the borrowed lists' slots
(`CMB_FxLandSoundsOwn`, `CMB_FxLandSoundsAltOwn`, `CMB_FxWaterLoopsOwn`, 0x8AB-0x8AD; docs/ASSETS.md's second table);
nothing of the game's is copied, the game resolves the paths in its own archives. `CMB_FxOwnSounds` (MCM "Bike sounds
through the mod's own records", 1) picks ours or the game's (`FxOwn`, `FxList`, `FxLandSet`; 0: the game's records,
the landings at once, the water at the next getting on). The landing volume is `fx x 10^(-range x (1 - level) / 20)`
with the MCM's range (`CMB_FxLandRange` 10, fixed 0x895: the plugin reads it for its line, "level 0.47 (-5.3 dB at the
script's -10 dB floor)"; an older ESP: 18). With range 10 a light landing is about 27 dB louder than in test 48, a full
one 12, the water loop 18. `[Fx] WaterGain` (0 dB) scales the water loop (-6: x0.501). A level-0 cue writes
`CMB_FxLandPlayed` minus the flight's number and plays nothing, and the plugin says so ("fx: cue 3 silent by the
script (level 0), 0.036 s after the landing") rather than "played". Papyrus: "Bike sounds: landing (SyncRight) at
level 0.34 (our records, a 10 dB range): sound 0 instance 9864, volume 0.421." (with the switch off "(the game's
records, an 18 dB range)").

The water: in water when the player's loaded data's `currentWaterType` (+0x10) is a `TESWaterForm` and its
`relevantWaterHeight` (+0x18) is over the feet by more than half a unit (`WaterSource=loaded`), or by the character
controller's `waterHeight` (+0x320, `WaterSource=controller`); what either holds in 1.11.240 isn't known yet, so each
entry logs both and the swim height, and each ride's start the dry readings ("fx: into the water at 640 u/s: 12.3 deep
(the surface ... by the loaded data, type ...; ... by the controller; its swim height ...)"). The driven loop's level is
`sqrt(depth / WaterFull) x (WaterStill + (1 - WaterStill) x speed / WaterSpeedFull)` (each at most 1; 40, 0.15, 600),
one-pole up over WaterRise (0.08 s) and down over WaterFall (0.4 s), with a splash at an entry after half a second dry at
WaterSplashSpeed (300) or faster, WaterSplash (6 dB) over it decaying over WaterSplashTime (0.35 s), times the bike
effects volume, sent by SetVolume when it moved by the game's 0.001 and once at 0 when silent (nothing to aim at and
under 0.01); its pitch from 0.85 standing to 1.0 at WaterSpeedFull (down only), by SetFrequency over `[Sound] PitchStep`
while it sounds. The calls are BSSoundHandle's, through the Address Library the engine sound checks
(`SoundLibraryReady`), on counters of their own. At volume 90: 20 deep at 600 a second 0.64 (the splash's peak 0.91 at
+0.2 s), at 200 0.28, standing 0.10. A load lets go of the loop (it doesn't survive one); the save's id, already answered
in `CMB_FxDriven`, is left alone and the script's new one handed over. `[Fx] Water=0` is the 2026-10-31a build's (no
water loop); `[Fx] Land=0` drops only the plugin's cue (`CMB_FxLandLevel` -1: the script's own fixed level,
`FxLandDefault` 0.5, on the landings whose clips send `JumpDown`), so 31a's silent landings are the MCM's "Landing
sound" off; the MCM's switches off (Landing sound, Water sound, the mute, the volume at 0) are the 2026-10-31a build's.

The harness: mode full's landing rides check the cue with no new frames (`CMB_FxAir` 1 at 0.35 s in the air, the number
one more, the level written in the flight, at the landing the level by the logged fall within 0.01 and `CMB_FxAir` 2, 0
by +0.3 s, the latency line when the fake writes `CMB_FxLandPlayed` 0.03 s after the landing, nothing of it with
`Land=0`, no flight for the 0.2 s hop). Mode 21 plays the script's water loop through an Address Library of its own
whose sound functions count the loop's calls apart from the engine's (its `IsPlaying` false for the loop's first three
looks, a streamed loop starting late): the hand-over at the fourth look, one SetVolume(0)
while dry and nothing else, into water 20 deep at 640 (the first volume a frame in, the splash's peak, 0.636 and the
pitch 1.0 by +2 s), slowed to 200 (0.276, the pitch 0.90), out of it (0 within 1.5 s), `Water=0` (declined, no call),
a loop that never plays (declined 0.35 to 0.5 s after the script's write), `WaterSource=controller` (the same numbers), no
water type (never in water), a load on the bike (the save's loop gone: no `IsPlaying` on its id), and a drop into water
(the level 2 more; the fake script's `CMB_FxLandPlayed` written at the landing's own frame, before the plugin's look:
the "before the landing" line, no "not played" line). Mode roomold (test 42's ESP): the one line, nothing else.

**Without metal, the splash and the wet road (test 49; the 2026-11-06a build).** Test 49 heard the big landings as a
metal barrel or a microwave, no splash at all, and the water as "frying" (the stream loop's waterfall hiss), flat in
level at the pond's speeds. The build-49 check (Q-L) found three of our records naming files the game doesn't have:
0x8A1 and 0x8A2 now name `Data\Sound\FX\FST\Player\Water\FST_Water_Jump_Down_01/02.wav` (the light splash) and
`Data\Sound\FX\PHY\Generic\PHY_Generic_Water_Medium_01-03.wav` (the heavy), and 0x8A9 is renamed `CMB_FxWaterRoadLPSD`,
our own wet-road loop `FX\CMB\CMB_FxWaterRoadLP.wav` (looped, `CMB_SOMMonoFx`). The MCM's "Landing sounds without metal"
(`CMB_FxLandDull`, 0x8B7, on) plays the list `CMB_FxLandSoundsDull` (0x8B9: the light and heavy tyre, the power armor's
dirt thud, the two splashes, its water thud): a tyre thump, from `FxLandBig` (0.6) the dirt thud at `CMB_FxThudDb` (-11
dB, 0x8B8; its loudest 50 ms 1 dB over the old clunk's, over in 0.2 s where the clunk rang 0.63 s) under the heavy tyre;
into water a splash, from 0.6 the heavy splash with the water thud ("Bike sounds: landing (SyncRight) at level 0.62 (our
records, no metal, a 10 dB range): sound 1 instance 9864, the thud 9865 (-11 dB), volume 0.584."); off, the 2026-11-02a
build's sets. The water law: (speed / `WaterSpeedFull`)^`WaterCurve`, 900 and 2 (600 and 1 before), on the level only
(the pitch stays linear): -2.6 dB at 750, -8.8 at 450, -12.3 at 300, full at the top speed (in test 49's pond the bike
sat at 750 or more 85% of the time, where the old law was flat). The MCM's "Water sound loop" (`CMB_FxWaterLoop`, fixed
0x8B4: 2 the wet road, 1 the churn, 0 the 2026-11-02a build's `CMB_FxWaterPick`) picks the loop on getting on, and the
plugin trims it at each take-over (`WaterChurnDb` -8, `WaterRoadDb` 0; "fx: the water loop (id N) driven (CMB_FxDriven
N): ...; the wet road (CMB_FxWaterLoop 2), WaterRoadDb +0 dB"), its law on a second `  fx:` settings line. The wet road
is made by `tools/sound/make_water_loop.py` (numpy only) from the tester's example, "Cars driving on a wet road 3"
(Pixabay 101246, freesound_community, the Pixabay Content License: used inside the mod, the recording never in the
repository or the package): three stretches cut, filtered, levelled to -23 dB A-weighted and looped, 7.90 s, 44.1 kHz
mono, its centroid 1763 Hz (the example's 1863), the wrap within the loop's own 90th percentile in spectrum and level; a
second run is byte-identical. `FxAudition -3` plays the landings as heard: levels 0.1, 0.3, 0.5, 0.7, 1.0, then 0.3 and
1.0 into water, 2.5 s apart. In the harness: mode `fx` 41 checks (35 + 6: the second line, the law at 640 0.371 and at
300 0.156 where 02a gave 0.636 and 0.366, the churn 0.253, the wet road 0.636, loop 0 with no words), roomold one more
(no trim words with an older ESP).

## The brought bike's spot (F4SE plugin and the controller)

Test 41: brought from Diamond City's door, the bike stood in the gate's chain-link fence each time (*Where it can't go*
above has what the controller does about it). The controller now tries spots and asks the plugin whether each has
room, through six more globals of CommonwealthMotorbike.esp, written and read as the ram's are (the generator checks
their IDs the same way; the controller's properties for them aren't Mandatory, so an ESP from before test 41 leaves
them None and no spot is checked). Test 42 saw it work (the bike outside Diamond City, not in the fence), and the
user's thoughts on it made test 43's changes: the spot checked as the bike will stand there, a box along the heading,
a call with room nowhere taking the spot with the most room, an ask the rays couldn't answer tried again, and the
script reading the answer's exact values.

| Form (ID) | Written by | Holds |
|---|---|---|
| `CMB_RoomAskX`, `CMB_RoomAskY`, `CMB_RoomAskZ` (0x84F to 0x851) | the script | the spot, at the player's height; since test 46 the plugin writes X and Y back with a room answer when its `[Room] Slide` moved the spot |
| `CMB_RoomAskAngle` (0x855; test 43) | the script, with the spot | the spot's heading, the player's `GetAngleZ` in degrees, which the bike is placed with (since test 46 written back by the plugin, as X and Y, when `Slide` turned the spot); -1000, the ESP's value, is none written (an older script): a heading of exactly 0 or -1 stays one, and `GetAngleZ`'s range (0 to 360 or ±180) isn't known |
| `CMB_RoomAsk` (0x852) | the script, after the spot | the ask's number: one above the global's or the script's last, whichever is higher (a save keeps the globals), so an old answer is never read as this one |
| `CMB_RoomClear` (0x854) | the plugin | with room, how far below the asked height the ground is (minus for above); with none, how far along its ray the nearest hit is (since test 43, with the box, that share of its ray on the bike's `Fore`, 110), the ground's offset when that is what refused it (minus for above; since test 45, with `[Room] Line`, from the player's ground: the asked height unless the player is in the air), exactly -1 with no ground within 100 of the asked height (since test 46, with `[Room] Tilted`, within 100 above or 100 plus the spot's distance times tan `GroundSlope` below), exactly -2 when the rays aren't working here, exactly -3 (since test 45) when the line from the player to the spot is blocked |
| `CMB_RoomAnswer` (0x853) | the plugin, after Clear | the ask's number for room, minus it for none |
| `CMB_RoomOptions` (0x86D; test 46) | the plugin, at the start, with its settings and with every answer | its `[Room]` keys for the script: 1 for `Around`, plus 2 for `LineFallback=0`, since test 47 plus 4 for `ParkCheck` and 8 for `SnapNext` (15 at the defaults); 0, the ESP's value (no plugin), is test 45's script |
| `CMB_RoomPitch`, `CMB_RoomRoll` (0x86E, 0x86F; test 46) | the plugin, with each answer (the script writes -1000 before each ask) | the ground's tilt under the parked bike's wheels at the spot with room, or at a refused one a call can take for the most room (`[Room] ParkTilt`), degrees as `SetAngle` takes them, the pitch held to 45 and the roll to `ParkRoll`; -1000 none measured |
| `CMB_RoomGround` (0x870; test 46) | the plugin, with them | that spot's ground height, with a tilt |

The plugin finds 0x84F to 0x854 all or none ("room: no CMB_Room globals (an older ESP): the bike's spot isn't checked"),
and since test 43 `CMB_RoomAskAngle` (0x855) apart from them, only when the six are there (without it, an ESP of test
42's build, "room: no CMB_RoomAskAngle (an older ESP): the spot checked without a heading, the eight rays as before test
43", after `FindGlobal`'s own "isn't a global" line). Every frame, riding or not, with a player in a cell, it reads the
number; a new one (not the one answered already: after a load the loaded save's last answer is the one given, so a save
made between an ask and its answer, the door's autosave, still gets its answer) gets its rays, once: one down through
the spot, 100 above the asked height to 100 below, for the ground; then from 50 above that ground (over a curb or a
rail of clutter, under a counter or a sign) eight level rays and one up to 120 (the bike's and the rider's height). Up
to test 42 the eight were the four axes and the four diagonals out to 110 (the parked bike's length, 196 from the front
wheel's edge to the rear's, halved plus 12), since the spot came with no heading: a passage under 220 wide never had
room, even where the bike fits lengthwise. Since test 43, with the heading the script gives and `[Room] Box` (1), they
are a bike-shaped box along it: `Fore` (110) ahead and behind the spot (the parked model is centred, 98 each way, so
fore and aft are the same; not the worn frame's axles, which put the rider over the origin), `Side` (40: the parked
bike's half width at the bars, 29.4, plus about 10) to each side, and the four corners (117 out), as `GetAngleZ` turns
(forward (sin a, cos a), right (cos a, −sin a), the plugin's own heading convention too). A hit is judged by its share
of its ray, and Clear is that share of `Fore`, so the script compares a side hit with a fore one on the bike's length
(a side hit at 35 of 40 nearly fits: 96; a fore hit at 60 of 110 puts the nose 38 into a wall: 60); on a tie the axis's
ray is named, not the corner beside it (a wall square to the heading meets both at the same share). Without a heading
(-1000 or no global) or with `Box=0`, the eight rays and their values are test 42's. All of them use the wheel rays'
filter and, like them, through actors (a settler standing there isn't a wall:
"; an actor there (name), passed" on the line). Room: all nine find nothing and the ground is within 60 of the asked
height (a curb is 20; a drop or a rise past 60 is a ledge, a stair or a roof, not the spot). One line per ask: "room:
ask N at (x, y, z), heading A: room (the ground N below the spot)" (", heading A" since test 43, when one is given), or
"none, something N along +x (name, layer N)" (with the box "something 35 along the right (of 40: 96 on the bike's 110)
(name, layer N)", the rays fore, aft, the right, the left, fore-right, fore-left, aft-right and aft-left), "none, the
ground N below the spot (name, layer N), over 60" (or "above"), "none, no ground within 100 above or below the spot"
or "none, the rays aren't working here (the test ray beside the player): not looked at" (answered -2 rather than
guessed), the eight rays' lines ending "(no heading given: the eight rays)" with `Box=1` and "(Box=0: the eight rays,
the heading not used)" with a heading but `Box=0`. The rays are untrusted after a load until the test ray beside the
player passes, which up to test 42 only riding's own 3 s retry (test 16's rubble and bridges) cast again, so on foot an
ask then was answered -2 till the script gave up on the spot; since test 43 (`[Room] RaysRetry`, 1) such an ask casts
the test ray again for itself ("room: ask N: the rays weren't trusted (the test ray N s ago): tried again for it", then
the test ray's own line), one test ray an ask at most, riding's cadence untouched, and the script asks about the first
spot once more 1.5 s after a -2 (*Where it can't go* above). Since test 43 `CMB_Slope.ini` has a `[Room]` section
(`Box`, `Side`, `Fore`, `RaysRetry`, on a "  room:" settings line, read again on getting on; `Box=0` and `RaysRetry=0`
give test 42's build). The script (`RoomAt`) writes the spot, its heading (since test 43, when the property is filled)
and the number and polls every 0.05 s (`RoomPollInterval`) for 0.5 s (`RoomAnswerWait`; the plugin answers within a
frame or two): "Bike's spot N (220 ahead, 60 right): room (the ground N below)." or "none (the nearest hit N along a
ray, on the bike's 110, or the ground N off).", "none (the ground N above the spot).", "none (no ground within 100 of
the spot).", "not checked (the plugin's rays aren't working here)." (Clear exactly -2 and -1 since test 43: before it
the script read anything under -1.5 as not checked, so a spot under a rise, the ground over 60 above, ended the asking
instead of going on to the next), "not checked (no answer in 0.5 s)" (no plugin) or "not checked (the ESP has no
CMB_Room globals)". The harness plays the script's asks in its mode room (82 checks: a clear spot, a wall 60 along +x,
an actor's capsule passed, a hole, a spot 80 over the ground, a roof 115 up, an ask repeated or 0 ignored, and after a
load with the rays not working -2 for a spot asked then; since test 43 the ask right after it tried again and answered
room, a passage 100 wide with room along the heading and none across it, and none by the eight rays with no heading
given, one 70 wide refused at 35 along the right with Clear 96.25, a wall across the heading at 100 refused and at 120
not, the ground 80 above refused with Clear -80, `Box=0` the eight rays with a heading given, and `RaysRetry=0` -2
twice with no test ray until the 3 s retry; since test 45 the line, the ground below and the slope), and its mode roomold (40) an
ESP of test 42's build, the six globals and no CMB_RoomAskAngle, the 100-wide passage refused by the eight rays; its
mode ram has the ESP without the globals.

Test 44, four calls by Sanctuary's houses (22:54:49 to 22:55:42; "it either was placed in fence/bush or behind a
wall"): the first fine (spots 1 to 3 refused at L1_PicketFenceB, 85 to 105 of 110, spot 4 beside the fence on the
player's side); the second "room (the ground 21 below)" at spot 1 and the bike through the picket fence, which lay
between the player and the spot, out of the box's reach at the spot; the third, the player facing a house's wall, spot
1 inside the house, "room (the ground 34 above)" being its floor, within the 60, and the box at 50 over that floor
finding the room empty; the fourth, the player in a hedge, spot 3 "room (the ground 45 above)" and the bike found 250
from it when the tester got on: `SettleBike`'s `MoveToNearestNavmeshLocation` after the check (`MaxSettleDistance`
400). Since test 45, three `[Room]` keys, on a "  room:" line of their own ("  room: Line=50 GroundNear=25
GroundSlope=25: a clear line asked for from the player to the spot, that high over the ground under each (the player's
by a ray down under them); the spot's ground within 25 of the player's, or by a slope of up to 25 deg to the spot, the
ground along the line stepping by no more than 25"; read again on getting on). With `Line` (50, 0 to 150), after the ground
ray at the spot, a ray down at the player from 20 over the feet to 100 under finds their ground (none: the asked
height, "the asked height: none under them" in the line), and a line from `Line` over it to `Line` over the spot's
ground, through actors as the box (a settler in the way isn't a wall), must be clear: something on it is no spot,
`CMB_RoomClear` exactly -3 (`ROOM_NO_LINE`), "room: ask N at (x, y, z), heading A: none, no clear line from the player:
something 112 along the 224 to the spot (what, layer N), 50 over the ground under each (the player's Z, the spot's
Z)". The line comes before the ground's offset, so a spot refused for its ground has a clear line, and a call's
most-room choice, which takes only a `CMB_RoomClear` over 0 (a hit along a ray, or the ground below), never takes a
spot behind a wall. Then
the spot's ground must be within `GroundNear` (25, 5 to 100; a curb is 20, the floor 34 up was let through by 60) of
the player's ("none, the ground 34 above the player's (what, layer N), over 25; a clear line from the player"); every
answer past both ends "; a clear line from the player (224 long, 50 over each ground), the spot's ground 21 below the
player's (within 25)". Test 45's review: by `GroundNear` alone every spot on an open slope was refused (the spots 300
ahead past 25 at 4.8 deg, the nearest, 100 ahead, past 14), and a call then took one whose box was never checked (a
spot refused for its ground never reached the box). With `GroundSlope` (25, 0 to 45 degrees; with `Line` only) the
ground may be off by `GroundNear` plus the spot's distance times its tangent (131 for the spot 220 ahead) when the
ground along the line, a ray down from the line every 25 at most (`ROOM_PROFILE_STEP`), steps by no more than
`GroundNear` between two of them, the player's ground and the spot's at the ends (or by the slope's own rise between
them, if more): a slope has room ("..., the spot's ground 59 above the player's (over 25: within 131 (25 and 25 deg over
the 228 to it), the ground followed every 23 along it, no step over 25)"); a floor, a hedge's top or a ledge is a step
and none ("...; a clear line from the player; not a slope: a step of 34 up 174 along it (what, layer N), over 25"; one
past the slope's allowance "over 131 (25 and 25 deg over the 228 to it)"). A spot refused for its ground below, which
the most-room choice can take, has its box checked at that ground ("; checked at its ground: clear", or the box's hit,
`CMB_RoomClear` then the less of the two), so the call never takes a spot nothing was looked at. `GroundSlope=0` is
within `GroundNear` as in test 45's first build (the box still checked). `Line=0` measures `GroundNear` from the asked
height, leaves `GroundSlope` and the box at a ground-refused spot out, and with `GroundNear=60` is test 44's spot check
exactly. The hedge is the script's: `SpotSettleMax` (30, a constant of the controller's; 0 = the snap taken up
to `MaxSettleDistance` as in test 44's build). `PickBikeSpot` keeps the ground of a spot with room (the asked height
less `CMB_RoomClear`, `spotGround`); `RollBikeUp` hands `SettleBike` that checked spot, and after the navmesh snap a
bike more than 30 from its ground (in 3D) is put back there, level: "The bike settled N from the checked spot (the
navmesh snap), over 30: put back on the checked spot, level on its ground."; otherwise "The bike settled N from the
checked spot (the navmesh snap, 30 at most)." and on as before. Undoing the snap was the smaller change: trying the
next spot would need a snap per spot. A spot taken without room (the most room, or not checked) settles as before.
`RoomAt` reads -3 as "Bike's spot K (…): none (no clear line from the player to it).". Still open: with every spot
refused and none taken for the most room (the player facing a wall up close), a call takes spot 1 as before test 41,
which in the house's case can put the bike inside again (since test 46 such a call is refused, below). The harness
(modes room and roomold, `RoomLineTests`): a
fence 90 high halfway between the player and the spot, none and -3; a floor 34 over the ground at the spot, none and
-34 (a step of 34 up on the way); the spot's ground 21 below past an edge, room, and with the fence between, none by the
line; asks 5 and 15 made against the player's ground (a spot at the player's height past an 80 drop, "the ground 80
below the player's", a step of 80 down on the way, the eight rays at its ground clear; a disc 80 up, still -80); and in
room, `Line=0` with `GroundNear=60` written and read on getting on, the fence, the floor and the 21 behind the fence with
room again, a spot 80 over the ground refused in test 44's words; then (`RoomSlopeTests`) a 15 deg open slope rising
ahead and falling ahead, spots 1, 6 and 7 with room by the slope (the ground 59, 80 and 27 above or below), the player
in a hedge (a disc 45 over the ground, 120 round) and spot 3 on its top, none by a step of 45 up, though within the
slope's 100 there; and `GroundSlope=0` read on getting on, downhill spot 1 none by its ground 59 below with its box
checked (clear, Clear 59; a wall 30 ahead of it, Clear 30), uphill none, -59, no box.

Test 45, twelve calls (14:48 to 16:53 of its video; 5 fine, uphill among them: call 9 "room (the ground 60 above)" by
`GroundSlope`). With a fence, a wall or rubble right in front of the player (calls 1, 6 and 8) every spot ahead had no
clear line, and the call took the first, "none of the 7 has room (a call takes the first, as before test 41)": 220 ahead
and 60 right, past the fence, inside the house, beyond the rubble, the navmesh snap leaving the bike in the hedge, nose
into the wall, out of sight. With the most-room fallback's box hit at 59 and 78 of its 110 (calls 2 and 4), the bike was
set down with its nose 51 into the picket fence and 32 into the wall. Downhill (calls 10 and 11) the spots' ground lay
over 100 below ("no ground within 100") or past the slope's allowance, and the box's level rays from 50 over the spot's
ground met the slope behind it (aft-left at 30 to 89 along), so the calls fell back to a spot 300 ahead and 84 below
with a rock in its box, its roll held at the script's 10, and to one 73 below left level ("the navmesh around the parked
bike is too coarse to tilt it by: left level"). Since test 46 five `[Room]` keys and `ParkRoll`, on a third "  room:"
line ("  room: Around=1 LineFallback=0 Slide=1 Tilted=1 ParkTilt=1 ParkRoll=20: spots beside and behind the player asked
after the seven ahead; a call with no spot with room nor a most-room one (with a clear line) is refused, the bike not
brought; a box with a hit slid away from it by what it lacks and 10, else turned 90 either way, and checked again; the
spot's ground looked for down to 100 and its distance times tan GroundSlope, the box tilted with the ground under its
ends; the brought bike tilted to the ground under its wheels, its roll up to 20"; read again on getting on; each key's
off value gives test 45's part), and four more globals after the nine engine loops' descriptors (`CMB_RoomOptions`,
`CMB_RoomPitch`, `CMB_RoomRoll`, `CMB_RoomGround`, 0x86D to 0x870: the plugin finds them by ID apart from the seven,
`ROOM_MORE_ID`, and the generator checks them; the engine's output model, made after them, is 0x871; without them "room:
no CMB_RoomOptions to CMB_RoomGround (an older ESP): the script's spots, its call's fallback and the brought bike's tilt
as in test 45's build"; the controller's properties for them aren't Mandatory).

`Around` and `LineFallback` are the script's to act on, so the plugin tells it through `CMB_RoomOptions` (bit 1
`Around`, bit 2 a call refused; written at the start, with the settings and with every answer, so a save's value never
outlives a session; `RoomOption`). With bit 1, when none of the seven has room, `PickBikeSpot` asks four more
(`AroundSpots`, 4): 100 behind and 110 to the right (`ParkSideOffset`), beside the player with its nose 10 ahead of
them; the same on the left; 120 behind turned 90, across the player's heading (`SpotTurn`), 80 to 160 behind them; and
220 straight behind ("Bike's spot 8 (100 behind, 110 right): …", "9 (100 behind, 110 left)", "10 (120 behind, across)",
"11 (220 behind)"), each with its own heading in `CMB_RoomAskAngle`. With bit 2 (`LineFallback=0`) a call with no spot
with room and none to take for the most room (a `CMB_RoomClear` over 0, which only a spot with a clear line can have)
gets -2 from `PickBikeSpot`: "The bike's spot: none of the 11 has room, and none to take for the most room (a hit along
its box or the ground below, each with a clear line): the call is refused."; `RollBikeUp` shows the bike again where it
was if it was shown (`rollRefused`), and `CallBike` says "There's no room for your motorbike here." ("Calling the bike
refused: no spot with room around the player (the spot lines above say why): …"); a bring from a door still leaves the
bike where it waited, and one that came in with the player stays hidden there ("Bike not brought (…) from where the
player went in: no spot with room around the player, kept hidden."), a later call saying so. `LineFallback=1` takes the
first spot as before.

In the plugin `RoomFrame` became `RoomLook` (one spot's ground, line, slope and box into a `RoomSpot`), run for the
asked spot and, with `Slide`, for it moved or turned. A box with a hit on one of its eight rays, its line and ground
passed, is slid away from the hit by what that ray lacked plus 10 (`ROOM_SLIDE_MARGIN`: a fore hit at 70 of 110, 50 back
along the heading; a side or corner hit along that ray's line) and, no room there, turned 90 to the right, then to the
left, about the same spot (along the fence or the wall it faced); a move or a turn that would stand the box on the
player (their capsule within it, `RoomBoxOnPlayer`) isn't tried. Each try is checked in full, line, ground and box, and
logged ("room: ask N: slid 50 back along its heading to (x, y): room (…)", "forward along its heading", "to its left",
"back and to its right" and so on, "room: ask N: turned 90 to the right, heading H: none, …", "…: not tried, the box
would stand on the player"); the first with room is the answer, its spot and heading written back to `CMB_RoomAskX`/`Y`
and `CMB_RoomAskAngle` before the answer and `CMB_RoomClear` its ground's, which `RoomAt` reads back after a room answer
(as asked with an older plugin): "The bike's spot: N (…), heading H, where the plugin found room (50 from the asked
spot, turned 0).". With `Tilted` (and `Line` and `GroundSlope`) the spot's ground is looked for down to 100 plus the
spot's distance from the player times tan `GroundSlope` ("no ground within 100 above or 204 below the spot"; the
script's "none (no ground within reach of the spot)."; since the review a spot refused for its ground below that lies
deeper than 100 under the asked height, which only this deeper look finds, isn't one a call takes for the most room:
its depth as `CMB_RoomClear`, up to 200 for the script, outranked every near-fit box, and `ParkTilt`'s measured ground
would have kept the bike at a ledge's or a step's foot 130 to 200 below the player; so `CMB_RoomClear` -1, as test 45's
build, whose ray didn't reach it, no box and no tilt, "…; 160 under the asked height, past the 100 a call's most room
takes (Tilted's deeper look found it): not one to take", the script's line the same "no ground within reach"), and the
box's eight rays follow the ground under its ends
(`RoomBoxTilt`: a ray down at `Fore` ahead and behind and at `Side` to each side, from `GroundNear` plus a `GroundSlope`
slope's rise there to as far under; along each axis a slope where both ends are found and the spot's ground lies within
`GroundNear` of the line between them, so a wall's top or a ditch at one end leaves that axis level: "; the box tilted
with the ground under its ends (-25 deg along its heading, 0 across)"). With `ParkTilt` a spot with room, or a refused
one a call can take for the most room (its box cast, Clear over 0: call 11 was one), gets the ground under the parked
bike (`RoomParkTilt`: a ray down under each wheel's contact, 68 ahead of and behind its middle, the parts file's axles
136.3 apart, and 35 to each side, the script's `ProbeAcross`), the plane through the four giving the pitch and the roll
as the script's `TiltParkedBike` takes them from a normal (the nose up on a rise ahead, the bike leaning the way the
ground falls), the pitch held to 45 (`ParkMaxPitch`) and the roll to `ParkRoll` (20, 0 to 45), into `CMB_RoomPitch`,
`CMB_RoomRoll` and `CMB_RoomGround` ("; parked tilted to the ground under its wheels: pitch -25.0, roll 20.0 (its 30.0
held to ParkRoll's 20)", or "; not tilted for parking: no ground under its front wheel within 88", "…: the ground under
its wheels makes no slope"; -1000 none). `ParkRoll` 20 is a judgement: a cruiser on its side stand leans about 10
degrees on the level, and much past 20 across a slope it would tip off the stand (the stand uphill) or over onto it
(downhill); the other parks (getting off, the ridden track, after a swim) keep the script's `ParkMaxRoll` 10. The script
reads the tilt with each answer (`RoomTiltRead`: "Bike's spot N (…): room (the ground N below, its wheels' ground at
pitch 25.0 down, roll 0.0)."), keeps the chosen spot's (`spotPitch`, `spotRoll`, `spotTiltKnown`), and `SettleBike`
tilts the brought bike to it whenever it stays on the checked spot, the navmesh snap kept within `SpotSettleMax` or
undone ("… over 30: put back on the checked spot, on its ground.", then `TiltBikeAsMeasured`: "Parked bike tilted to the
ground under its wheels (the plugin's, on the checked spot): pitch P, roll R.", or "Parked bike level on the checked
spot (tilting turned off)." with `CMB_MaxTilt` at 0), in place of the level put-back and of the navmesh probes (the
coarse navmesh's "left level"); a most-room spot with a measured tilt is now settled as a checked spot, on its measured
ground. The harness (mode room, 103 checks, 21 more; `RoomPickPlayed` plays the script's spot choice in C,
`RoomAroundTests`, mode room only): a fence 90 high across the player's front 35 ahead, the seven ahead with no clear
line and spot 8 (100 behind, 110 right) with room; a wall 30 ahead and the ground ending 40 behind the player, all
eleven none and the call refused (-2); a box with a hit at 70 slid 50 back to room, or turned where the slide would
stand it on the player; a 25 degree slope falling ahead, spot 1's ground 103 below found, its box tilted -25 along,
room, `CMB_RoomPitch` -25; a 30 degree cross slope, the roll 30 held to 20; a 36 degree slope, spot 1 refused (its
ground past the 131 allowed) and, 160 under the asked height, not one to take (Clear -1, no box, no tilt), spot 7 (100
ahead, its ground 73 below) a most-room spot with pitch -36; then every key off, test 45's choices again (the
fence's call taking spot 1); asks 10 and 13 of the older checks now find room by turning and sliding, and mode roomold's
ESP has none of the four (one line, nothing written: 41 checks, 1 more). Not exercised: the script's own paths (the
refused call, the read-back, the tilt in `SettleBike`), only compiled.

Test 46, eleven calls, every one bringing the bike (3 slid by the plugin 32 to 71 from the asked spot, 5 behind the player,
spots 8 and 9). Two things were left. Getting off at 13:52 to 13:56: the tester got on facing a house's window at point
blank ("the front hit 80 above the feet … pitch 30.5 deg") and got off about 2 s later; the bike was parked beside the worn
one as always, through the window, its navmesh snap failed ("No Navmesh found, object not moved"), and it stood inside the
house. And two calls whose spot with room was on a car: at 14:32, beside a wrecked sedan, spot 9 "room (the ground 30 above
the spot)" by the slope, and at 17:06, the player standing on Red Rocket's red truck, spot 7 "room (the ground 17 below the
spot)"; the snap went 89 and 207 from them, over `SpotSettleMax`, and the bike was put back on the checked spot, on the
wreck and on the truck. There the snap was right: the checked spot was off the navmesh. Since test 47 two more `[Room]`
keys, the script's to act on as `Around` is (`CMB_RoomOptions` bit 4 `ParkCheck`, bit 8 `SnapNext`; `RoomWriteOptions`),
on a fourth "  room:" line ("  room: ParkCheck=1 SnapNext=1: getting off, the bike put back where it stood when the ride
moved the player less than a wheelbase from where they got on, else its spot asked about as a call's (slid or turned),
with no room there the spots beside and behind the player; a spot with room whose navmesh snap goes past the script's
SpotSettleMax isn't walkable: the next spot asked, the checked spot taken only when none passes", the off parts "getting
off, the bike parked on the track or beside the player unchecked (ParkCheck=0, test 46's build)" and "a spot with room
taken whatever its navmesh snap, the bike put back on it past SpotSettleMax (SnapNext=0, test 46's build)"; read again
on getting on).

With bit 4, getting off a ride (`ParkBesidePlayer`, before the ridden track and the spot beside): `Mount` keeps where the
bike stood and how (its position and angles, when it was shown and loaded) and where the player stood, and a ride that
moved the player less than `ParkBackWithin` (136, about the wheelbase: the axles 136.3 apart) from there puts the bike back
exactly where it stood, nothing asked (`ParkWhereItStood`: "Parked bike put back where it stood before getting on: the
ride moved the player N from where they got on, under 136 (the plugin's [Room] ParkCheck)."), but not (the review of test
47's build: got on from 100 beside it and rode 100 its way, the bike went back onto the player) when the player now
stands where it stood, within `ParkBackFore` (128: the plugin's `Fore` 110 and the capsule's 18) of it along its heading
and `ParkBackSide` (58: `Side` 40 and 18) across it, as the plugin's `Slide` keeps its box off the player ("Parked bike
not put back where it stood: the ride moved the player N, under 136, but they stand where it stood (N along its heading,
N across it): its spot asked about instead (the plugin's [Room] ParkCheck)."), its spot then asked about as below. Past that `ParkChecked`
asks about the parked bike's spot as a call's is (`RoomAt`, the box along its heading; the bike is disabled while riding,
so it isn't in its own way): the ridden track's spot, heading the way it went (`CMB_ParkX`/`Y`/`Z`, `CMB_ParkAngle`, when
the plugin has one), or 110 to the player's right (`ParkSideOffset`): "The park spot (the track just ridden): room (…)."
or "The park spot (beside the player): none (…)." (`RoomAt`'s new `asSpot` names it). Room as asked: parked there as
before ("The parked bike's spot: the track just ridden, as before (room there)."). Room where the plugin's `Slide` moved or
turned it: the bike there, settled as a brought bike on its checked spot ("The parked bike's spot: beside the player,
heading H, where the plugin found room (N from the asked spot, turned T)."; `PlaceOnSpot`, the placing `RollBikeUp` did,
now shared by calls, brings and this). No room: `PickBikeSpot`'s park (`abPark`), the four `AroundSpots` beside and
behind the player only, no most room, the first with room taken ("The parked bike's spot: 8 (100 behind, 110 right),
heading H."); with none of them "The parked bike's spot: as before (none of the 4 beside and behind the player has room
either)." and the park as before, which an unchecked or unanswered ask gets too ("…, as before (not checked).").

With bit 8 (`SnapNext`) a spot with room whose navmesh snap would land farther than `SpotSettleMax` (30) from it isn't
walkable: `SnapOff` puts the probe marker (`CMB_GroundProbeRef`) where `PlaceOnSpot` would put the bike, at the player's
height, snaps it to the navmesh (`MoveToNearestNavmeshLocation`) and measures it against the checked spot as `SettleBike`
does (along the ground only with no ground known), the bike staying disabled through the asks: "Bike's spot N (…): its
navmesh snap N from it, over 30: not walkable, the next spot asked (the plugin's [Room] SnapNext).", and the next spot is
asked. With none passing, a call takes its most-room spot if that one's own snap passes ("Bike's spot N (…), the most
room: its navmesh snap N from it, over 30: not walkable either." if not), else the first spot with room, put back on it as
in test 46 ("The bike's spot: N (…), heading H: the first with room, its navmesh snap too far, and no other spot passes
(the plugin's [Room] SnapNext): taken as before.", "The parked bike's spot: …" getting off); so does an ask left
unanswered after such a spot, and a bring from a door takes it rather than leaving the bike where it waited. Whether a
player standing on a wreck should have the bike up there with them is a judgement: it now comes to the ground beside them
if any spot there passes. An ESP without `CMB_RoomOptions` keeps test 46's park and calls. The harness (mode room, 117
checks, 14 more; `ParkPlayed` and `RoomParkTests` replay the script's park, and `RoomPickPlayedEx` its call with
`SnapNext`, in C against the plugin's room answers, a fake "no navmesh here" disc, `SnapPlayed`, standing in for the
game's navmesh): getting on facing a wall at point blank and off where the player got on, the bike back where it stood,
nothing asked; a ride of 100 onto where the bike stood, the spot beside asked instead (the review); a ride of 140 nosed into a wall with no track spot, the spot beside slid 100 back; a ride of 450 with a wall
30 to the right of the track's spot, slid 20 to its left; the track's spot on a step 45 up, none, spot 8 taken;
`ParkCheck=0`, the spot beside unasked, in the wall, as test 46's bike through the window; a call with no navmesh within 60
of spot 1 (the sedan), spot 2 taken; one standing on a truck's bed with no navmesh within 270, spots 1 to 4 with room but
not walkable and spot 5, off it, taken; no navmesh within 400, spot 1 put back on as before; the most-room spot taken when
its own snap passes; `SnapNext=0`, spot 1 as before; `CMB_RoomOptions` 15 (12 with test 47's two alone, 11 and 7 with one
of them off); and mode roomold (42, 1 more) an ESP without `CMB_RoomOptions`, its getting off asking nothing. Not
exercised: the script itself (the harness can't run Papyrus; its choices are replayed in C), only compiled.

2026-11-01a, `[Room] SnapSpot=1` (`CMB_RoomOptions` bit 16, with the ESP's `CMB_RoomAskKind`, 0x876; test 47's call from on
top of the red truck at 20:04:16: no spot passed, every line from the player to the spots around blocked by the truck
itself, spot 10 had room on the hood with its navmesh snap 129 off, and the bike was put back on the hood's edge). A plain
ask at the place the snap found would likely have been refused too: the line from 50 over the player's ground descends
through the truck's top, and the hood-to-ground drop is a step. So `SnapOff` keeps where the snap took the probe
(`snapX/Y/Z`), `PickBikeSpot` keeps the first such spot's (`farSnap`, `farSnapX/Y`), and when no other spot passes it asks
about that place as a navmesh point before taking the spot as before: `RoomAt(…, aiKind = 1)` writes `CMB_RoomAskKind` (0
on every other ask, before the number, so a 1 never carries over), only for a call or a bring (not getting off), with
`CMB_RoomOptions` bit 16 and the snap over `SpotSettleMax` and at most `SpotSnapReach` (300, a new auto property) from the
spot. The plugin (`RoomFrame` reads the kind with the ask; `RoomLook(…, navPoint)`, with `Line` only) judges it with the
line level from `Line` over the player's ground when the point's ground is lower (so it passes over what they stand on, a
wall or a house between still blocking it), its ground up to `GroundNear` above theirs or down to 100 below (a drop off
what they stand on; deeper, -1), no step test along the line; the box, `Slide`, the turns and `ParkTilt` as for any spot.
Its lines: "room: ask N at (…), heading H (a navmesh point): room (the ground 70 below the spot); a navmesh point: a level
line from the player (250 long, 50 over their ground), its ground 70 below theirs (a drop off what they stand on, 100 at
most)…", "… (a navmesh point): none, no clear line from the player: something 120 along the 250 to the spot (…), a level
line 50 over their ground (…; the spot's N: a navmesh point)", "… (a navmesh point): none, the ground 120 below the
player's (…), over the 100 a drop off what they stand on may be (a navmesh point); a level line from the player". With room
there and its own snap within `SpotSettleMax` the controller takes it: "The bike's spot: Bike's spot 10's navmesh point
(129 from it), heading 311: room, walkable (its own snap 0): taken (the plugin's [Room] SnapSpot)." (else "…: its own
navmesh snap N, over 30." and the spot as before). The settings are on a fifth "  room:" line ("  room: SnapSpot=1: a
call's first spot with room off the navmesh, when nothing else passes: the point its navmesh snap found asked about as a
navmesh point (a level line from the player, a drop off what they stand on, no step test) before it is taken as before
(SnapSpot)", off "…: the first with room taken as before (SnapSpot=0)"), so test 47's line reads as it did. An ESP without
`CMB_RoomAskKind` gets "room: no CMB_RoomAskKind (an older ESP): no navmesh point asked for (SnapSpot)" once and no bit 16.
Accepted: from a truck 75 up the level line passes over a fence lower than 50 over the player's ground, which they could
jump anyway; a drop of up to 100 is taken (the most-room rule already took spots 84 below at 20:03:52). The harness (mode
room, 126 checks, 9 more): `CMB_RoomOptions` 31 with `SnapSpot=1` (28, 27 and 23 with test 46's and 47's
keys off), 15 with it 0; the player on a disc 75 up, 140 round: a point 250 ahead none as any spot ("a step of 75 down 150
along it"), room as a navmesh point (Clear 75, the level line's words); 160 ahead no clear line as any spot (the disc's top
in the line), room as a navmesh point; a wall 200 high 120 ahead no line either way; the ground 120 below too deep (-1);
`SnapSpot=0`, a navmesh point judged as any spot; `RoomPickPlayedEx` plays the step (the hole's edge along the spot's
line): no navmesh within 400, the place 400 out along spot 1's line asked and taken (12 asks), `SnapSpot=0` spot 1 as
before (11). Mode roomold (43, 1 more): no bit 16, the one line, an ask with the kind written 1 judged as any spot.

Test 49's calls from the red truck: with no spot with room the most room was taken, its own navmesh snap never asked
about. Since the 2026-11-06a build `[Room] SnapBest=1` (`CMB_RoomOptions` bit 32, with `SnapSpot` and `CMB_RoomAskKind`)
has PickBikeSpot's most-room branch ask the most room's navmesh point first (unless the plugin has gone unanswered):
"Bike's spot 1's navmesh point, the most room's (... from it), heading ...: room, walkable (its own snap ...): taken
(the plugin's [Room] SnapBest)." or "Bike's spot 1, the most room: its navmesh snap ..., over ..., its navmesh point not
taken: the most room as before (the plugin's [Room] SnapBest).". `[Room] SnapDrop` (250, 100 before) lets a navmesh
point's ground lie that far under the player's (RoomLook's `groundOk` and `tooDeep`), so a call from a roof or a rock up
to 250 high comes down to the navmesh below. The settings line: "  room: SnapBest=1 SnapDrop=250: ...". The harness's
truck needed a second disc (the cab on the bed); mode room 131 (126 + 5: the truck to the street, SnapDrop=100's
refusal, the settings line, the options 63, the most room on the navmesh; `CMB_RoomOptions` 31/28/27/23 -> 63/60/59/55),
`SnapBest=0` 31 and 11 asks as before; 2026-11-01a's SnapSpot checks run at `SnapDrop=100`.

## The engine sound (F4SE plugin, the controller and `tools/sound`)

Up to test 43 the engine was two synthesised loops crossfaded by speed (*How approach A works* above). Test 44's build
gives it a recorded sound and a gearbox: the controller plays eleven loops and hands them to `CMB_Slope.dll`, which
sets each one's pitch and level every frame from a model of the engine's rpm, gear and load; when the plugin doesn't
take them (not installed, no Address Library or one of another game version, `[Sound] Drive=0`, an ESP from before),
the controller crossfades two of them, the idle and the cruise, once a tick as before.

**The sound.** Thirteen files in `Data\Sound\FX\CMB`, all made by `tools/sound` from one recording: demodave's "Harley
Davidson Sportster - Idling with Engine Revs" (Freesound 502690, Creative Commons 0, credited as a courtesy), its right
channel only (its two channels are one signal 23.2 ms apart, so a mix of them doubled every pulse: the "echo-y" of the
second demo). The start (0.25 to 2.6 s of it), the stop (158.6 to 160.6 s) and the idle loop (92.0 to 98.3 s, 860 rpm)
are cut from it. Six loops on load (1400, 1700, 2000, 2400, 2800 and 3300 rpm) and three with the throttle shut (1400,
1800, 2800) lay its real firing pulses at each rpm's firing times, each pulse drawn at random from those recorded
nearest that rpm; the fourth shut one (2300) is 18 flattened pieces of its falls. Each riding loop is then tone-matched
to three on-board videos of a V-twin cruiser, someone else's and measured only (third-octave shape, a brightness law, the
half-order line pattern; the numbers are stored in the tools). The user heard the set as demo D, a 31 s ride rendered
through the same model (`tools/sound/render.py`), and chose it for the game ("I would go with demo D to see how it
behaves in game"). Neither the recording nor the files are in the repository (`tools/sound/README.md`; rebuilt from the
downloaded recording, all 13 match demo D's byte for byte; since test 46 that is with `HOT=0`, the package's being
2.5 dB hotter, *The levels* below); the package carries them, the 2000 rpm loop on load as
`CMB_EngineCruiseLP.wav`, the file the cruise SNDR has always played. The repository keeps its own four, the synthesised
`CMB_EngineIdleLP`, `CMB_EngineCruiseLP` (~2700 rpm), `CMB_EngineStart` and `CMB_EngineStop`, as the fallback; the nine
other loops exist only in the package. A build from the repository alone has no full set for the plugin: the ESP's nine
SNDRs name files that aren't there, and what follows depends on what `Sound.Play` gives for them, which no test has
shown yet. If it gives 0 or less (no instance), the controller's check of the ids stops at the first, before anything is
offered: "Engine sound: the script's crossfade (loop 2, On1400, has the instance id 0: it didn't play)." and the two
synthesised loops crossfade, as in test 43. If it gives the id of an instance that plays nothing, that check passes it
(it looks only at the ids' range) and the plugin takes the set ("playing 2 of 11" at 0.35 s, or 11 of 11 if the game
counts the silent ones as playing) and drives it, with two loops to hear: the idle near the idle's rpm, and the
synthesised cruise, pitched as the 2000 rpm loop (so about a third high), only on load between about 1840 and 2190 rpm,
the top speed's cruise among them; past the idle's fade, silence everywhere else on load and all through a roll-off.
`[Sound] Drive=0` (every set declined) gives such a build the crossfade either way.

**The model** is `tools/sound/engine_model.py`; `CMB_Slope.c` carries its C twin, from `ENGINE_MAX_GEARS` to
`EngineMix` byte for byte the `cmb_engine.h` that follows the Python within 0.006 rpm over six rides (test 44's build;
since test 45, with the heard speed below, the C and the Python agree within 0.010 rpm and in every gear over five game
profiles and the seven stretches of test 44's ride replayed, in the new settings and in test 44's). Four gears with
the reference rides' steps (1.35, 1.28, 1.21), each gear's speed at the shift point scaled by `[Steer] FullSpeed` /
900, so 4th cruises at the top speed at 1937 rpm (the user's three chosen stretches of the "daily" ride run at medians
of 1814 to 2056); up-shifts at 2500 at full throttle and 2200 with a steady key, 1.25 s apart at least, each a 0.35 s
clutch gap with a flare and a fall, the throttle-shut loops playing through it (the rides' shifts are 28 to 35%
darker); a down-shift under 1750 with the throttle on (1475 since test 45, after a second under it). With the throttle
shut the rpm dips 3.2% and then falls 70 rpm a second at most (150 since test 45; 300 braking), never rising: the
game's own coast (900 to 0 in 2 s) is far harder than a real roll-off. The clutch goes in near the stop and the engine
falls to the idle, 860 (at 900 rpm a second at most; 750 since test 45). That is test 44's model, the gears and rpm
tied to the bike's own speed; since test 45 they follow a heard speed instead (below). The inputs are the bike's speed
along the heading (the steering's, smoothed over 0.2 s; with the steering off the plugin measures its own the same
way; its size, so backing up idles), the forward key and braking (back while moving forward faster than 10), read from
the input hook as the climb and the landing read them (with the hook off, forward while the speed holds or rises,
braking while it falls faster than the game's coast), and since test 45 whether the plugin holds the throttle for
something ahead (`SoundInputs`' `held`: the face rays easing or holding it, a wall at the front wheel in the last
quarter second, a ram's hit hold, the climb's boost). The idle loop fades out between 1010 and 1190 rpm; above it one
loop plays in each family, on load and throttle shut, the one whose stretch holds the rpm, with a 0.05 s hand-over at
a boundary (two loops of one engine at one rpm phase against each other: the second demo's "fluctuation"); the family
follows the rider's throttle over 0.08 s. Each loop's pitch is rpm / its base (0.85 to 1.17 with these bases, held
within 0.75 and 1.25), the family loops' with a slow random wander of 0.6% (the daily ride's cruise wanders 0.48 to
0.69%; since test 47 2.5% over 1.5 s, smoothed, the level moving with it, only while the throttle is steady, since 27c's
reply 5.5%, held softly under 6% and smoothed over 0.5 s: *The throttle
hand* below); the level is the paris ride's law (9.6 dB an rpm doubling, on load 5 dB over shut, the idle 17.2 under) scaled
by 0.3, what the other two rides' cameras give: the idle 5.2 dB under full load at 3000 rpm (0.7 since test 45,
below; 1 and +5 dB since test 46, *The levels*). Every constant is a key
of `CMB_Slope.ini`'s `[Sound]` section at the model's value, its measured basis beside
it, and so is the loop table (family:base rpm, in the order of the globals), so a verdict on the sound in the game
changes only the INI; they are read again on getting on, on two "  sound:" settings lines (three since test 45, four since test 47,
five since the 2026-11-01a build).

**The heard speed** (since test 45). Test 44's verdict: "engine sound itself is okay, but the way it's implemented is
horrid - it's not natural whatsoever - please go back to reference videos and see how real bike behaves". The pipeline
was right (7 sets driven, 11 of 11 loops; the rpm tracked from the recording's audio matched the trace's at a median
ratio of 0.998), so what was heard was the model as written, and against the paris ride, measured the same way, it was
the game's bike that did everything 2 to 3 times faster: 900 a second in about 3 s from a stop, stopped about 2 s after
a let-up. Tied to that speed, every pull-away was alike, 1.5 to 2 s flat at the slip's 1500 (the `Lead` cap keeps the
bike under 333 for 1.25 s) and then a sprint through 1st and 2nd in 2 s (paris: the rpm rising at once from 1250 to
1500 at a median 370 rpm a second, the first shift at a median 2.6 s at 2000 to 2900); at the top speed a frame under
813 (1750 in 4th) made a down-shift and the up-shift 0.5 s later, 21 surges in 123 s and 79 in the session, most of them
in the second after the face rays, a ram's hold or the climb's boost had eased the throttle (paris: none while the speed
holds); after a let-up the gears ticked down silently in about a second and the clutch dropped the engine to idle as
the bike stopped (paris: -150 rpm a second for 4 to 9 s, often a blip near the end); and every state sat within 2.6 dB
(paris: a pull 11.6 dB over the idle, 4.4 over a roll-off; the cameras of the other two rides compressed it, and 0.3
copied the cameras). The bike's motion is left as it is (making it slower changes how riding feels, the tester's call);
with `HeardSpeed` (1) the engine follows a heard speed `vh` (the trace's "heard N", the gear lines' "heard N u/s")
instead. With the throttle on it rises at most `HeardRise` (140) units a second per second toward the bike's speed,
in 1st toward it + `HeardLead` (150: the clutch slipping before the wheels go, so the launch climbs from the key while
the game's bike still creeps; since test 45's review only in a launch, from the clutch's last going in till the bike
passes `ClutchSpeed`, or a real pull, the bike gaining faster than `HeardRise`, and an up-shift needs the bike's own
speed to land the next gear 3% over `DownRpm` unless it pulls so: with the lead and the slip at a steady 215 to 445 u/s
1st's rpm passed `ShiftLo` while 2nd sat under `DownRpm`, and the gear went 1, 2, 1 every 2 to 3 s; now one gear holds
at any steady speed, 1st at the slip's rpm), and follows a slower bike over `HeardTau` (0.8 s), so a 10% dip moves the rpm a few per
cent; the rider's load is full while the bike is `HeardPull` (60) or more ahead of it, the cruise load once it has
caught up. With the throttle shut it falls `CoastFall` (150; `BrakeFall`, 300, braking) rpm a second in its gear, never
under the bike's speed, the rpm following it from the lash's dip; under `CoastDown` (1700) a down-shift with a blip, the
throttle opened and the rpm `Blip` (0.09) over the new gear's for `BlipTime` (0.3 s, time constant `BlipTau`, 0.05;
paris: +27% in 0.3 s, +5 dB); the clutch goes in once the bike itself is under `ClutchSpeed` (150) or 1st's heard rpm
under `ClutchIn`, the heard speed then the bike's, and the engine falls to the idle at `ClutchFall` (750). The throttle
on with the bike under `ClutchSpeed` is 1st. The launch's slip starts at `LaunchDraw`'s point (1250 to 1500), drawn
afresh at each press of forward, and climbs `LaunchRise` (350) rpm a second at `HeardRise` till 1st's rpm takes over; an
up-shift out of the slip takes the heard speed to 1st's at the slip's rpm, so the drop to 2nd is the real gear step;
each pull also draws its full-throttle up-shift point from `ShiftDraw` (2300 to 3000 since the 2026-11-01a build; 2000 to
2900 before: *The stops* below). The draws come from the wander's
LCG in a stream of their own (`WanderSeed` ^ 0x9E3779B9, `EngineDraw`), so they don't hang on how many frames have
passed, and each set starts it afresh: every ride's first pull shifts at 2634 with its slip from 1293 (2429 with 2000 to 2900). With the throttle
on a down-shift needs the gear's rpm under `DownRpm` (1475: 4th's cruise is 1937, a 10% dip 1743) for `DownHold` (1 s),
and with `DownHeld` (1) none comes while `held` is true (test 44: in the second before its 79 pairs, the face rays
easing or holding the throttle 30 times, a ram's hold 24, the climb's boost 17). HeardRise was taken at 140 rather
than the 150 the plan named: at 150 2nd climbed 519 rpm a second, just past paris's 200 to 500. The level is
`LevelScale` 0.7 (paris's own law at 0.7 of its range): a pull 7.9 dB over the idle (paris 11.6), the throttle closing
3.5 dB from a pull plus the lash and about 2 from a steady key (paris -4 to -5). So the whole engine is quieter against
the game than in test 44's build: the cruise 6.2 dB under full load where it was 2.6, the idle at rest 12.0 where it
was 5.2 (`FadeTo`'s 1204 at rest, where it was 516); the MCM's engine volume may need raising
(test 45: raised to 100 and still "too quiet"; since test 46 louder, *The levels* below). Test 44's ride replayed
through both models (its speed and keys every 0.25 s at 60 fps; test 44's model replayed so matches the game's own
trace rpm at a median ratio of 1.000): the rise to the first shift 372 rpm a second (test 44's 484 after the flat 1500;
paris 370), the first shift a median 3.25 s after the key at 2433, from 2112 to 2889 over the pulls (2.19 s and 2374,
every pull alike; paris 2.6 s and 2370; 2.78 s and 2381 before test 45's review, 12 of the 13 pulls the same, the 13th,
the bike slowed to 234 with the key held, no longer shifting at 224 u/s), 2nd climbing 486 rpm a second (875; paris 200 to 500), the last up-shift about 6 s after
the key, two down-shifts with the key held at speed, both after the bike had lost about half its speed (36), the fall in
gear after a let-up -146 rpm a second (-87; paris -150), the clutch at about 1750 with four blips over the coasts (1825;
paris about 1970), and the pull 7.9 dB over the idle and 4.3 over a coast (2.8 and 1.2; paris 11.6 and 4.4). Key taps
under the replay's 0.25 s don't show in it. `tools/sound/render.py --ride` renders a recorded ride (a CSV
t,speed,forward,braking[,held]) through the model: demo E is 51 s of test 44's ride rendered so. The third "  sound:"
line names every key and what is on ("  sound: HeardSpeed=1 HeardRise=140 … DownHold=1 DownHeld=1: the engine follows
a heard speed (up at most HeardRise, down with engine braking after a let-up); the launch's slip climbs from each pull's
start; each pull's up-shift point drawn; a down-shift with the throttle on after DownHold under DownRpm, none while the
throttle is held for something ahead"; a `LaunchDraw` or `ShiftDraw` that isn't two rising numbers is named on the
first line's "not understood" list), and `HeardSpeed=0` with `CoastFall=70`, `DownRpm=1750`, `ClutchFall=900`,
`LevelScale=0.3`, `LaunchDraw=0,0`, `LaunchRise=0`, `ShiftDraw=0,0`, `DownHold=0` and `DownHeld=0` is test 44's model
exactly, each off part named on the line ("the engine follows the bike's own speed (HeardSpeed=0, as up to test 44)",
"a flat launch slip at IdleRpm + Launch", "every pull's up-shift at ShiftRpm", "a down-shift with the throttle on at
once under DownRpm"); with `HeardSpeed=0` the heard-speed keys do nothing but `HeardRise`, which still sets
`LaunchRise`'s climb, and with `HeardSpeed=1` `ClutchDecel` and `FullAccel` do nothing (`AccelTau` smooths the speed's
change that tells a real pull). The harness's
mode sound checks it (below).

**The levels** (since test 46). Test 45's verdict: "engine still cuts off when changing a gear I believe; I had to set
engine sound to 100 because it was too quiet, also it feels like sound isn't as 'punchy' as it should". Its tester
measured all 108 up-shifts of the recording with two holes each, 80 to 140 ms and 430 to 480 ms after the gear line (a
median -12 to -18 dB, about 0.1 s under -10 dB), and single ones at the hand-overs inside a family, the first pull's at
0:18.1, 0:19.0 and 0:20.0 where the rpm crossed 1543, 1844 and 2191; the same ride rendered offline has none. By
disassembly: `BSSoundHandle::FadeTo` runs every fade over 100 ms at least (25 was 100), a straight line in hundredths of
a dB from where it finds the loop, so a loop brought back from 10000 (-100 dB) stays inaudible for most of it while the
loop leaving falls under -30 dB within 20 ms: a hole at every family switch (two an up-shift with `ShiftFamily=1`, 0.35
s apart) and every hand-over, and every level change lagged 0.1 s. And the game plays the loops faithfully (the cruise's
timbre within 1% of the render's): quiet because the files are (-13.5 dBFS RMS, a crest of 12.5 dB where the reference
rides' is 9.2 to 11.7), the law kept the cruise at -6.1 dB with a pull only 1.6 over it in the game (paris about 4), the
instance volume tops out at 1 (the tester's 100), and the engine played through `SOMMono02000`, full only within 150 of
the bike, with the camera, most likely the listener, about 450 out. So since test 46 (`[Sound] SetVolume`, 1) each
loop's level is set by `BSSoundHandle::SetVolume` (Address Library ID 2267057, at +0x162E160 by the disassembly), the
value `Sound.SetInstanceVolume` sets: it posts audio message 13 with the volume × 1000 (truncated), which the audio
thread applies at once, with no ramp, whenever it moved by 0.001 or more, clamped to 1e-5 to 1, entering the voice as
2000 × log10 of it beside FadeTo's attenuation. Every frame `SoundSend` sends each loop's gain × the engine volume
(`SoundEngineVolume`: `CMB_EngineVolume` / 100, 0 to 1, read every frame, 0.7 without the global, 0.9 since test 47)
when it moved by 0.001 or more; a loop under 0.001 gets `SetVolume(0)` once and no pitch while silent; `FirstFade` is
the plugin's own straight ramp from the levels the script left (the idle at the engine volume, the rest silent) to the
model's, which it follows meanwhile; `FadeTo` isn't called (each set's loops are played afresh, no attenuation on them),
nor are `Fade` and `LevelStep` used. A change of the MCM's volume is heard at once ("sound: the engine volume 0.70 ->
1.00 (CMB_EngineVolume 100): in every loop's level from this frame"). More calls than FadeTo's: a level moving 0.001
sends, about 160 a second through a pull at the harness's 6 ms frames (2339 in a ride of 21.6 s, 1395 of them
`SetVolume`), 11 a second at a steady cruise (about 75 since test 47, the level moving with the throttle hand); each
only posts a message. `SetVolume` is the sixth of the library's cross-checks, called at its fixed RVA as
`LookupFormByID` is (so the in-the-code check doesn't apply to it), and checked whatever the key says; its RVA is
unconfirmed against a real library (the harness's copies are its own fake; the tester's log has SetFrequency, 2267059,
at +0x162E220 and IsPlaying, 2267046, at +0x162DE60, and 0x162E160 lies between them as its ID does): a library that has
it elsewhere declines every set ("… doesn't match this game (ID 2267057 gives 0x… where the plugin has 0x0162E160,
BSSoundHandle::SetVolume): the script's crossfade drives the engine", then "sound: generation N declined (the Address
Library at … hasn't BSSoundHandle::SetVolume where the plugin has it): …"), with no fallback to `FadeTo`: the script no
longer puts a volume on the loops, so without `SetVolume` the nine would stay silent. The script and the plugin
therefore go together: test 46's script with an older plugin leaves the nine silent, and test 45's with this plugin
overwrites its levels with the bare engine volume. `SetVolume=0` is test 45's `FadeTo` driving, the engine volume put on
every loop by `SetVolume` 0.15 s after the take-over (`SND_MASTER_DELAY`; test 45's script did it with
`SetInstanceVolume` at its first look at the answer) and on each change of it, the first settings line ending "; their
levels by FadeTo (SetVolume=0, as test 45), the engine volume by SetVolume" (with `SetVolume=1` "; their levels by
SetVolume, at once, the engine volume in them (Fade and LevelStep unused)"); with `LevelScale=0.7` and `LevelOffset=0`
it is test 45's levels as well. The level law gains `LevelOffset` (5 dB, -60 to 60, on the model's line) and a ceiling
of 0 dB on the overall level, before the crossfades (clamping each loop on its own would bump a crossfade at the ceiling
by up to 1.9 dB), so each loop's gain is 1 at most; `LevelScale` goes to 1, paris's own law. By `engine_model.py` (the
demo ride's windows and the states): the cruise (900 u/s in 4th, 1937 rpm) at -3.8 dB (-6.1 at test 45's 0.7 and 0); a
full-load pull from about 2100 rpm at the ceiling, 3.8 over the cruise (2400 rpm: 1.9 over it before the ceiling); the
pull from rest's windows 2.6 over the cruise (2.1); a roll-off 2.6 to 3.1 under it (1.9 to 2.2); the idle at -12.2 dB,
8.4 under the cruise (5.9; -12.0 in test 45, so the start and stop sounds meet it as they did). Test 48's answer (the
2026-11-02a build: "make it louder when idle", "when bike stops on obstacle it goes fully quiet"): `IdleDb` -11 (-17.2
before), the idle at -6.0 dB, 2.5 under test 48's cruise (-3.5 at 1990 rpm) where it was 8.7 under, and exactly where
the start and stop sounds' idle parts meet it (their last 0.3 s and first 0.5 s 6.0 dB under the loops: since test 45
each start dropped 6.2 dB into the idle and each stop rose 6.2 out of it). The floor holds every state under it: the
throttle shut under about 1945 rpm, the cruise's load under 1650, a full-load launch under 1360 (8% of the random ride's
frames, by 6.2 dB at most); the cruise and every pull are untouched; a roll-off to a stop stays at -6.0 dB.
`IdleDb=-17.2` is the 2026-11-01a build's model exactly (`engine_model.py --check-off`, its second file). The targets
conflict: a cruise near -2 and a pull 3 to 4 dB over it can't both hold under 0 dB; `LevelOffset` 6.8 puts the cruise at
-2 and every pull within 2 dB of it, and (0.7, 4) gives a cruise of -2.1 with a full-load pull 2.1 over it, (1, 4) -4.8
and 4.8. Two more changes have no key. The files are hotter (`tools/sound/hot_loops.py`, the last stage of `run_all.sh`,
`HOT=0` to leave it out: +2.5 dB, then a memoryless curve, the identity up to -6 dBFS and a cubic flattening at -1 dBFS
where the loops' own peaks land, so each wrap stays exactly as seamless as built): the RMS 2.3 to 2.5 dB up, the crest
10.0 to 10.3 dB, 6 to 9% of each loop's samples through the curve, its distortion 13 to 17 dB under the on-load loops'
own 4 to 16 kHz and 23 to 26 under the others' (`build_loops.py`'s look-ahead limiter would leave it 20 to 24 dB under,
the alternative if the pulses sound gritty; `tools/sound/README.md` has the table). And the thirteen engine sounds play
through the ESP's own output model, `CMB_SOMMonoEngine` (0x871): `SOMMono02000`'s 50/20/5/0 % curve with its distances
scaled, full level out to 600 (past the camera) and the curve from there to 4000; Attenuates With Distance only, Uses
HRTF, the reverb send 100, no static attenuation, no effect chain, the speaker grid mono to L and R and no fade-in.
Those last fields are guesses (there is no `Fallout4.esm` here to copy `SOMMono02000`'s from: compare them in xEdit if
the engine is placed or reverberates differently from test 45), and the generator reads the written ESP back and
compares the model and each sound's link field by field ("read back: 1 output model(s) and 13 sounds as written";
`check_plugin.py`: "checked 13 engine sounds: output model CMB_SOMMonoEngine (000871), its fields as written"; Mutagen
keeps the reverb send as a fraction of 255, so the byte 100 is written as 100/255). The only ways back are test 45's
files and the generator (the descriptors back on `Vanilla.SOMMono02000`, or the model's distances at 150 and 2000). The
build-27b check then read all 311 output models of the tester's `Fallout4.esm`: `SOMMono02000` (0x7E5DC) has the reverb
send 5 (25 of the 26 plain `SOMMonoNNNNN` use 5, their `_verb` twins 40, the vertibird's riding layers 20, the player's
own third-person model 30, the highest in the game 70: at 100 the engine was far wetter than any world sound wherever
the area has reverb), a static attenuation (VNAM) of 0 (all 311 have one, 258 of them 0), no output values (ONAM: none
of the 220 Uses HRTF models has any, only Defined Speaker Output's carry them) and the fade-in curve 0/50/80/95 (unused
with a 0-0 fade-in, and what 207 vanilla models write there). So since test 47 `CMB_SOMMonoEngine` is `SOMMono02000`
exactly but for its fade-out distances, 600 to 4000 (Bethesda's `SOMMono01500Player3rd`, which 101 of the player's own
third-person sounds use, is full out to 500 for the same camera, so 600 is in line), and the generator's read-back and
`check_plugin.py` expect exactly "flags AttenuatesWithDistance reverb 5 type UsesHrtf static 0 channels none fade-in 0-0
[0,50,80,95] fade-out 600-4000 [50,20,5,0] effect-chain none"; test 46's had the reverb 100, no VNAM, the three ONAM
rows and the fade-in curve 100/100/100/100 (its tester said nothing of echo, most of that ride in the open). No key
either: the generator is the way back. The repository still tracks only the four synthesised files of *The sound* above:
the package takes the thirteen from the build.

**The throttle hand and the up-shift's dip** (since test 47). Test 46's verdict: "engine sounds way better, it doesn't
fluctuates at all which also isn't ideal, bike engine RPM always either rises or decreases, slowly or fast depending on
mantle and gear". Its 124 up-shifts had no hole left (the median level around one dipping 2.4 dB at most, per shift a
median 0 ms under -10 dB in the 550 ms after the gear line where test 45's had 50), and its tester settled the MCM's
engine volume at 90 (from the save's 35). In 4 s windows of steady riding (in gear, the trend under 2% in 4 s, taken out)
the game's rpm wobbled 0.64% and its level 0.16 dB, about 0.4% with the note's tracker taken out (the old wander, 0.006
over 0.8 s, gives 0.38%), where the real rides give 1.02% and 0.34 dB (autumn), 1.41 and 0.43 (daily) and 2.36 and 0.81
(paris): a rider's hand and the road move the speed a little all the time, the rpm and the load with it. And a real
up-shift dips about 5.5 dB as the throttle closes (paris, 55 shifts, about 0.3 s under -3 dB), the game's 2.4, the rpm's
fall alone, a full-load pull sitting at the 0 dB ceiling. So since test 47 the wander is the throttle hand, with four more
`[Sound]` keys on a fourth "  sound:" line, each 0 test 46's part (`Wander=0.006`, `WanderTau=0.8`, `WanderLevel=0`,
`WanderSteady=0`, `WanderSmooth=0` and `ShiftDip=0` together are test 46's sound exactly: the Python twin matches test
46's model to the last digit over a 32 s ride). The walk is larger and slower (`Wander` 0.025, `WanderTau` 1.5: the note's 0.02 to 0.025 over 1.5 to 2, its
top, as the smoothing takes some) and smoothed with a time constant of `WanderSmooth` (0.2 s, the engine's inertia: the
bare walk moves the pitch 15.7 cents rms in 0.1 s, which no hand does; smoothed 6.8, test 46's 5.1) before it is heard
(`wanderRaw`, then `wander`); the family loops' level moves with it, `WanderLevel` dB per 1% (0.3: the rides' 0.30 to 0.34
dB per 1%, the rpm's and the load's together; a rise louder and more loaded, a fall lighter; the idle's level and pitch
never wander), on each family loop's gain after the ceiling (`EngineMix`'s `hand`); and it runs only while the throttle is
steady (`steady`: forward held, no up-shift's gap, the clutch out, over the idle's band, 1190 rpm, the rider's load under a
quarter of the way from the cruise's to full, `ENGINE_WANDER_PULL`, and the plugin not holding the throttle for something
ahead), elsewhere (a pull, a let-up, a shift, the idle, a wall's ease) settling to 0 with a time constant of `WanderSteady`
(0.25 s) and growing again from 0 by its own walk, the random number drawn every frame either way. At each up-shift's
clutch-in (`dipRef`, the level there, at most 0 dB) a throttle-off dip of `ShiftDip` (4 dB) over `ShiftDipTime` (0.24 s;
`EngineDipShape`: in over its first quarter, full, out over its last third, cosine ramps) comes off the level after the 0
dB ceiling (`EngineHeardDb`), so it is heard at the top of a pull, through `SetVolume` at once: a dip, not a hole, never
taking the level more than 6 dB under where it was at the clutch-in (`ENGINE_DIP_FLOOR`) unless the law itself goes
under that. By `engine_model.py` (900 u/s in 4th with the key held, 4 s windows with the trend out, 4 seeds, 392
windows): the heard rpm 1.02% (median; the autumn ride's 1.02), the level 0.30 dB, 0.30 dB per 1%, the hand 0.00%
through a pull from rest; test 46's values 0.39% and a flat level. Through a pull from rest (the level against its mean
0.25 to 0.05 s before the clutch-in): a shift at the ceiling -4.0 dB, 0.15 s under -3 dB; one drawn lower -4.7 to -5.0
with the rpm's own fall, 0.17 s; the pull's last, into the cruise, -6.2, at the floor (its load falling to the cruise's
too); test 46's values -0.9 and -0.4, none under -3 dB but that last, -3.6. The fourth line reads (since the 2026-10-31a build,
below) "  sound: WanderLevel=0.3 WanderSteady=0.25 WanderSmooth=0.5 WanderMax=0.06 ShiftDip=4 ShiftDipTime=0.24: the
wander (the throttle hand) only while the throttle is steady, settling to 0 in a pull, a let-up, a shift and the idle,
smoothed, held softly under WanderMax, the family loops' level moving with it; a throttle-off dip at each up-shift's
clutch-in, at most 6 dB under the level there" (off: "the wander everywhere (WanderSteady=0, as test 46)", "unsmoothed
(WanderSmooth=0, as test 46)", "unheld (WanderMax=0, as 27c)", "the level not moving with it (WanderLevel=0, as test
46)", "no dip at an up-shift (ShiftDip=0, as test 46)"), the model's line has "Wander=0.055 WanderTau=1.5" (27c's
"Wander=0.025"), and the trace's engine word ends " hand +1.23%" (the wander, in % of the heard rpm, whenever `Wander`
is over 0). The level moving at a cruise means a `SetVolume` most frames on the one loop heard: about 75 calls a second
at a steady cruise in the harness (152 in 2 s, 122 of them `SetVolume`; 145 and 117 since the 2026-10-31a build), where test 46's
made about 11. `render.py`'s level column is still the law
before the ceiling, so it shows neither the dip nor the hand's level. And the engine volume's default is 90: the
generator's `CMB_EngineVolume` (70 up to test 46), the controller's fallback without the global and the plugin's (0.9); a
new save starts there, an old one keeps its own.

**The hand at 3 to 5%** (the 2026-10-31a build). Build 27c's notes gave the hand as "about 1% in rpm and 0.3 dB in level", and its
tester, before riding it, answered: "1% won't be really noticeable - 3-5% probably would be better". That 1% was the 4 s
windows with the trend taken out, the measure that put the real rides at 0.9 to 2.3%; it takes out most of a swing as
slow as this one. Against the cruise's own mean (`engine_model.py`, 900 u/s in 4th with the key held, 5 seeds of 392 s;
a swing's peak: an excursion's largest deviation, a new excursion once past the other side by 0.5%) 27c's heard rpm
already had an sd of 2.4%, its swings peaking 2.5% off (median; half of them 1.5 to 3.9%, 1 in 10 past 5.0, 1 in 17 past
6, 8.3 at most). Its walk scaled up until the swings sit at 3 to 5% would pass 6% often: a Gaussian walk whose swings
peak 3.1% (median; 0.035 over 1.0 s, smoothed 0.5) has 1 in 9 past 6% and reaches 10%. So the walk is larger (`Wander`
0.055, `WanderTau` 1.5 as before), held softly under `WanderMax` before the smoothing (0.06: `wanderMax` × tanh(walk /
`wanderMax`), between `wanderRaw` and `wander`; 0 unheld) and smoothed longer (`WanderSmooth` 0.5 s, so that it moves no
faster than 27c's although it is larger); `WanderLevel` stays 0.3 dB per 1% (the rides' ratio at any size; the hold keeps
the level's swing within 1.8 dB, where 27c's reached 2.5). Measured the same way: the heard rpm's sd 3.1%, its swings
peaking 3.4% off (median; half of them 2.0 to 4.7%, 1 in 10 past 5.35, 1 in 43 past 6, 6.3 at most against the cruise's
mean, the hand itself never 6), a swing's rise or fall 2.1% to each side of its middle (median, between turns of 1%;
27c 1.55) over 1.6 s (27c 1.1); the pitch moving 6.2 cents rms in 0.1 s (p99 16.6; 27c 6.8 and 17.5; the bare walk 24);
the level's sd 0.93 dB, its swings peaking 1.0 dB (median; p90 1.6), 1.9 at most (27c 0.71, 0.74, 1.5 and 2.5); in the 4
s windows 1.16% and 0.35 dB (27c 1.02 and 0.31), 0.30 dB per 1%; the hand 0 through a pull from rest and the up-shifts'
dips the same (within 0.03 dB). The bigger hand meets no clamp: the loop playing is chosen by the engine's rpm
(`EngineFamilyStep` gets `s->rpm`), so the hand starts no hand-over, and in a steady cruise at any speed from 160 to
1200 u/s (3 seeds, 60 s each) the heard loops' pitch stays within 0.86 and 1.16 (`MinPitch`, `MaxPitch` 0.75 and 1.25
never reached; the plugin has no rev limiter, and the top loop, On3300, plays only over 3040 rpm, where no steady cruise
goes); the one ceiling met is the 0 dB one, at 2200 to 2600 rpm (a low gear at 360 and 420 u/s, 4th past 1100 u/s),
where the hand's rise in level is flattened, 4.6% of the steady frames (27c 3.7%). After a let-up at 900 u/s the hand
goes back at 3.9%/s at its fastest (the median of 200 let-ups; 10.6 the fastest), under the coast's fall: the heard rpm
never rose with the throttle shut in its gear (27c: in 2 of 200, +1.7%/s). The twin and the plugin's model (cut from
`CMB_Slope.c`, built with gcc) agree over a 32 s ride (rest, a pull, a 20 s cruise, a let-up, a pull again; 953 frames
with the hand on) to 0.007 rpm, 5e-8 in the wander, 8e-6 in a gain and 4e-6 in a pitch, no gear or steady frame apart,
at the defaults, at 27c's values, deep in the hold (`Wander` 0.15) and unsmoothed; `Wander=0.025 WanderSmooth=0.2
WanderMax=0` is 27c's twin to the last digit over that ride, and test 46's six with `WanderMax=0` test 46's.

**The up-shifts and the stops** (the 2026-11-01a build). Test 47's verdict on the gears: "rpm could be slightly higher the
closer it is to shifting gear" and "the sound could indicate that gears are shifted down". Its session 1 shifted 1->2 at a
median 2355 rpm (n 74), 2->3 at 2347 and 3->4 at 2289: each pull draws its full-throttle point uniformly from `ShiftDraw`
(2000 to 2900, median 2450), a fifth of the draws under `ShiftLo`'s 2200, and the engine lags its gear by about 50 rpm.
`ShiftDraw` is 2300,3000 now: over 40 pulls of the harness's game 1->2 at a median 2607 (p10-p90 2356-2929, 2951 at most),
2->3 at 2596, +250 rpm, about 10%; 3->4 stays at 2343, all 3rd has at the bike's top speed (900 × 2500/960), which no draw
can lift without moving the gearbox the tester likes (4th's 1937 at the cruise), so 3rd now sits at its top for a median
0.63 s before 3->4 (0.13 before; `MinShiftGap`'s 1.25 s from 2->3 still running) and the pull to 4th takes about 0.7 s
longer. The heard loops stay within 0.742-1.174 through the pulls (the flare at the highest shift 2951 × 1.05 on Off2800,
1.107; the wander is 0 through a pull and a gap). The stops: a roll to a stop gave one blip at most (19:40:31.5, let go at
886 u/s in 4th; 19:40:33.106 "gear 3 at 224 u/s, 1668 rpm, heard 790 u/s, a blip", the clutch 0.25 s later, its line
swallowed by the lines' 0.25 s), and a braked one the clutch straight from 4th (19:41:23.05 back at 777 u/s, heard 891;
19:41:23.609 "gear 1 at 145 u/s, 1738 rpm, heard 145 u/s (clutch in)", 0.56 s after the brake). With the throttle shut the
heard speed fell only `CoastFall` rpm a second in its gear, 70 u/s² in 4th (140 braking), where the game's bike loses 450
coasting and 2250 braking, so it never got through `CoastDown`'s bands (790, 653 and 510 u/s in 4th, 3rd and 2nd) before
the clutch took the bike's own `ClutchSpeed`; the coast's down-shift already blipped, it never had the time. With
`StopShift` (1), once the throttle has been shut `StopAfter` (0.3 s; braking at once) the heard speed falls toward a slower
bike at least `HeardStop` (300 u/s², about 4.3 m/s²; the game's coast, 6.4, is a firm real stop) or `HeardBrake` (600,
about 8.6) braking; the down-shifts with the throttle shut come `StopGap` (0.4 s: paris's blip, 0.3 s, n 21, and a pull of
the lever, a judgement: the reference rides' down-shift spacing isn't among the numbers kept) apart rather than `DownGap`'s
0.5; the clutch may wait up to `StopHold` (0.4 s) after the bike's own `ClutchSpeed` for the heard speed or a running blip,
and a blip that would end later isn't started (`EngineStep`: `shutT`, `stopT`; the same lines in `engine_model.py`). The
lash dip, the blip's shape and level (the 0 dB ceiling, as the coast's blip had), the throttle-on rules and the wander are
as they were. The twin over the harness's game (6 ms frames, from the let-go or the press):

| ride | 2026-10-31a | the 2026-11-01a defaults |
|---|---|---|
| let go at the cruise (900, 4th) | 4->3 blip at +1.60 (1667 rpm, the bike 270); the clutch 3->1 at +1.87 (2202); the idle at +3.89 | blips 4->3, 3->2 and 2->1 at +0.60, +1.06 and +1.53 (1730, 1812 and 1835 rpm; the bike 714, 513 and 300); the clutch at +1.83 in 1st (2134, the bike 165); the idle at +3.77 |
| brake (S 0.6 s) from the cruise | the clutch 4->1 at +0.59 (1750, the bike 150); the idle at +2.02 | blips 4->3 and 3->2 at +0.22 and +0.62 (1790, 1631); the clutch from 2nd at +0.98 (1632, the bike 21); the idle at +2.26 |
| coast 0.7 s, then brake 0.5 s | the clutch 4->1 at +1.13 | blips at +0.60 and +1.00; the clutch from 2nd at +1.53 |
| a 0.5 s let-off at the cruise | no shift | no shift (`StopAfter`; at 0 a 4->3 blip at +0.46, 3->4 1.4 s later) |
| a 0.15 s brake tap | no shift | no shift |

The rpm of a roll to a stop is a sawtooth, as real down-shifts make it (1937 -> 1753 | 2120 -> 1812 | 2223 -> 1835 | 2304,
then the clutch's fall), and the pitch through the coast and the brake stays within 0.736-1.196 at a gain over 0.05 (0.740-1.210
before). After the bike's own stop the sound goes on for at most `StopHold` before the clutch (it was at the bike's 150); a
let-off longer than about 0.6 s now drops a gear with a blip and changes up again about 1.4 s after forward (session 1 had
9 such let-offs in 21 minutes; `StopAfter=0.6` leaves all but the longest as before). In the plugin every key is read
0.1 s past its last read (`AfterInput`), so a brake tap is heard 0.1 s longer than it lasts: a tap of back at the cruise
over about 0.08 s now blips 4->3 and changes up again (HeardBrake's 600 takes the heard speed under 4th's band in 0.18 s;
the harness's 0.15 s tap does), where the twin's 0.15 s tap had none: the harness taps for 0.05 s. Forward is kept 0.2 s
over the game's (0, 0) reads too (test 19), so a let-off is heard 0.3 s shorter than it lasts, and a half-second let-off
sounds as before even at `StopAfter=0`. The clutch going in is a gear line in 1st too ("sound: gear 1 at 165 u/s, 2134 rpm, heard 165
u/s (clutch in)"), and a fifth settings line names the six ("  sound: StopShift=1 HeardStop=300 HeardBrake=600 StopGap=0.4
StopHold=0.4 StopAfter=0.3: a stop shifts down a gear at a time, each with a blip (…)"; `StopShift=0`: "a stop as the
2026-10-31a build (the heard speed falls CoastFall, BrakeFall braking, rpm a second; a gear, then the clutch)";
`HeardSpeed=0`: "nothing (StopShift needs HeardSpeed=1: the stops as test 44)"). `StopShift=0` with `ShiftDraw=2000,2900`
is the 2026-10-31a build's model exactly: `engine_model.py --check-off` runs it over the demo ride, a random 60-segment ride
in the harness's game and five stops (44,136 frames) against the 2026-10-31a model's frames (`check_off_2026-10-31a.txt`,
written from 0c3df02's `engine_model.py`): none differs; and the C cut from `CMB_Slope.c` with the off values gives
0c3df02's C exactly over the same rides. The harness's mode sound checks the pulls, the stops, the brake key's stop, the
off values and `StopAfter=0` (*What has been verified*).

**The hand-over** goes through thirteen more globals of CommonwealthMotorbike.esp, written and read as the room's are
(fixed IDs the generator checks; the controller's properties for them and for the nine new loops aren't Mandatory, so
an ESP from before test 44 leaves them None and the controller plays its two loops as before):

| Form (ID) | Written by | Holds |
|---|---|---|
| `CMB_SndLoop01` to `CMB_SndLoop11` (0x857 to 0x861) | the controller | the loops' instance ids from `Sound.Play`, in the `Loops` order: the idle; on load 1400, 1700, 2000, 2400, 2800, 3300; the throttle shut 1400, 1800, 2300, 2800. Whole numbers under 2^24, which a float holds exactly; 0 = none |
| `CMB_SndGen` (0x862) | the controller, after the ids | the set's number: one above the global's or the controller's last, whichever is higher (a save keeps the globals, as with the room's asks); a new number with all eleven at 0 withdraws the set |
| `CMB_SndDriven` (0x863) | the plugin | the number when it drives that set, minus it when it declines, 0 when it has let go |

The nine new loops are SNDRs after the globals (`CMB_EngineOn1400LPSD` to `CMB_EngineOff2800LPSD`, 0x864 to 0x86C,
looping, each playing `CMB_Engine<name>LP.wav`); the cruise SNDR (0x81B) still plays `CMB_EngineCruiseLP.wav`, in the
package the set's On2000 loop, what 4th gear turns at riding speed, so the crossfade's cruise is that loop too.
Since test 46 all thirteen engine sounds play through an output model of the ESP's own, `CMB_SOMMonoEngine` (0x871, made
after the room's four globals so that no form ID moves; *The levels* above), and the plugin also finds
`CMB_EngineVolume` (0x81C, the MCM's engine volume) for its levels: "sound: found CMB_SndLoop01 to CMB_SndLoop11,
CMB_SndGen and CMB_SndDriven (…), CMB_EngineVolume (FExxx81C)", or "; no CMB_EngineVolume (0x81C): the engine volume
taken as the MCM's default, 70" (90 since test 47).

The controller (`StartEngineLoops` and `OfferEngineLoops`, from the engine timer at a ride's start or from the load's
`OnGameReloaded`, outside busy) plays the idle and the cruise as before, then (`PluginDrivesSound`, true) the nine
others, each put at volume 0 at once, writes the eleven ids and the number last, and polls `CMB_SndDriven` every 0.05 s,
ten polls (counted, not a summed wait: a slow frame after a load doesn't use them up). Its number: "Engine sound: the
plugin drives the 11 loops (generation N, answered in poll P)." and the MCM's volume on all eleven, the plugin having
given each its own level first; since test 46 "…, answered in poll P), the engine volume in their levels." and no call
at all on a set the script offers or the plugin drives (the plugin's `SetVolume` carries the MCM's volume, the value
`SetInstanceVolume` sets, which would undo the level; `drivenVolume` and `SetLoopsVolume` are gone, and a save from
before logs one harmless Papyrus warning for the missing variable).
Minus it, or nothing in the ten: the nine stopped, the set withdrawn (the zeros and a
new number, so the plugin can't take it up late) and the crossfade: "Engine sound: the script's crossfade (the plugin
declined generation N: see its log)." or "(the plugin didn't answer in 0.5 s, generation N)."; a loop that didn't play,
an id too large for a float, or an ESP without the globals and the nine, the crossfade with nothing offered ("(loop K,
NAME, has the instance id X: it didn't play)", "(the ESP has no CMB_Snd globals or the nine loops for the plugin)").
While the plugin drives, `UpdateEngineSound` only put a changed MCM volume on the eleven up to test 45 (since test
46 nothing, and while an offer is out it skips its crossfade, which could undo the plugin's starting levels); should
the plugin let go
mid-ride (its log says why), the two loops are started afresh rather than left at its last pitch and level: "Engine
sound: the plugin let go of generation N (CMB_SndDriven reads X): the script's crossfade, its two loops started afresh."
`StopEngineLoops` withdraws the set before it stops the eleven, so the plugin lets go before their ids die. Every ride
end reaches it through `FinishRide`: the dismounts by the hotkey and the keys, the auto-dismounts (power armor, sitting
down, a weapon drawn, out of fuel, knocked off), the swim, a door or a fast travel indoors, the emergency reset and a
load (which withdraws the save's set before it offers a new one); since test 44's build the rider's death too, stopped
there and then (`RideTick`, behind `StopEngineAtDeath`, true): "Engine sound: the rider is dead: the engine loops
stopped (the load that follows ends the ride)." (before, nothing stopped them till that load). `PluginDrivesSound` false
is test 43's two loops, except the death stop (`StopEngineAtDeath`) and the files' new audio (the package's idle,
cruise, start and stop are the recorded set's): no global touched, no other loop played.

The plugin (`SoundFrame`, every frame after the steering) finds the thirteen globals all or none ("sound: found
CMB_SndLoop01 to CMB_SndLoop11, CMB_SndGen and CMB_SndDriven (FExxx857-FExxx863)", or "sound: not all of CMB_SndLoop01
to CMB_SndDriven are there (an older CommonwealthMotorbike.esp): the script's crossfade drives the engine", and the
driver never runs). A new number with ids in it is answered once. `Drive=0` or a set with an id missing is declined at
once ("sound: generation N declined (CMB_SndLoop05 is 0: the set isn't whole): CMB_SndDriven -N, the script's crossfade
drives the engine"). With the Address Library good (below; the riding globals aren't checked, since the controller offers a set only while
riding and withdraws it at every ride's end), `IsPlaying` is asked of each loop every frame for up to
0.35 s, and the set taken once all play, or at that time if any does ("sound: generation N: loops 1056 1057 … playing 11
of 11"); none playing is declined, since that most likely means an instance id isn't the sound's id. Taken, every loop's
first pitch and level is sent (a loop heard faded to its level over `FirstFade`, 400 ms: the controller plays the idle
at full till then and the model's idle is 5.2 dB under that, so for 0.4 s after the start the idle settles rather than
steps down), then the number written back: "sound: generation N driven (CMB_SndDriven N): 11 loops' pitch and level from
the engine model, the speed and the keys from the steering; FadeTo's attenuation taken as hundredths of a dB (0 = full,
10000 = -100 dB: an assumption), 25 ms fades, the first of each loop heard over 400 ms". Then each frame the model's
step and mix, and per loop `SetFrequency` only when the ratio has moved more than `PitchStep` (0.003, 5 cents) and
`FadeTo` (over `Fade`, 25 ms) only when the attenuation has moved more than `LevelStep` (30, 0.3 dB) since what the game
took; a silent loop gets `FadeTo(10000)` once and no pitch. That is `[Sound] SetVolume=0`; since test 46 the levels
go by `SetVolume` (*The levels* above), and the driven line reads "…; the levels by SetVolume (applied at once, no
fade, no FadeTo), the engine volume folded in (CMB_EngineVolume 70: x0.70, read every frame), the first 400 ms a
straight ramp from the script's levels (the idle at the engine volume, the rest silent)". The harness's ride of
about 12 s from rest through the gears
to a stop makes about 1150 calls; a steady cruise about 8 a second on the one loop heard (the wander; about 75 since
test 47, the level moving too), rest none. Gear
changes are logged, 4 a second at most ("sound: gear 2 at 557 u/s, 2366 rpm", " (clutch in)" at the stop; since test
45 with the heard speed, "sound: gear 2 at 896 u/s, 2394 rpm, heard 540 u/s", ", a blip" on a coast's down-shift,
"sound: gear 3 at 306 u/s, 1667 rpm, heard 790 u/s, a blip", and "sound: gear 1 at 150 u/s, 2130 rpm, heard 150 u/s
(clutch in)" at the stop; since the 2026-11-01a build the clutch going in is a line in 1st too, "sound: gear 1 at 165 u/s,
2134 rpm, heard 165 u/s (clutch in)"), the trace line ends with "engine g4 1937 rpm load 0.46" (since test 45 "engine g4 1937 rpm
load 0.45 heard 900", since test 47 "… heard 900 hand +1.23%", since the 2026-11-01a build " blip" while a down-shift's blip
runs and " clutch" while the clutch is in), and letting go sums the drive up. A hand-over more than 6 s after the ride's
start also gets "sound: generation N handed over 13.4 s after the ride's start (usually 3)" (the 2026-11-01a build, logs
only: test 47's hand-overs came 3.1 s after the mount, and a script stalled past that now shows in this log too). At a ride's end, the controller's `StopEngineLoops` putting
the ids to 0: "sound: generation N let go (the ids went to 0, generation N+1): driven N s, N calls (SetFrequency N,
FadeTo N: each posts its change to the audio thread), 860-2499 rpm, gears used 1 2 3 4" (since test 46 "(SetFrequency
N, FadeTo 0, SetVolume N: …)"); "(a new set, generation
N)", "(a load: the loops don't survive it)"; no call after it. Test 44's build said "…, FadeTo N), 0 failed, …": its
tester disassembled the two and found that each only posts a message to the audio thread, nothing in it to fail, so
since test 45 the line counts no failures, and one returning false would be named inside the parenthesis (", N
returned false"). After a load the set is forgotten, and one already answered (`CMB_SndDriven` at its number or minus
it: the save's own, whose ids mean nothing now or name other sounds) is left alone ("sound: generation N already
answered (CMB_SndDriven N: a save's set, its ids from before the save): left alone"); the controller's next is taken,
whether it comes before the plugin's first frame after the load or after. A call that returns false still counts: 30
in a row on one loop (half a second) and the plugin stops driving, the loops left as they were and `CMB_SndDriven`
minus the number ("sound: loop K (id N): 30 calls in a row returned false (they only post a message: not expected):
generation N no longer driven (CMB_SndDriven -N), the loops left as they were; N calls (SetFrequency N, FadeTo N), N
returned false, in N s"; the controller then plays its crossfade afresh).
`SetFrequency` refusing a ratio over 1 but taking one under gives "sound: pitch over 1 refused: the loops pitched down
only (…)", and none over 1 for the session.

**The Address Library** is the rays' file (`version-1-11-240-0.bin`, next to the plugin, then in the game's
`Data\F4SE\Plugins`, or `[Sound] Library`), read at the first hand-over (no cost when riding never starts) and again
only when `Library` changes or no file was found. The three functions are `BSSoundHandle::SetFrequency` (CommonLibF4's
ID 2267059), `FadeTo` (2267074) and `IsPlaying` (2267046), called with a handle built per call from the instance id
({soundID, assumeSuccess 0, state 1}, CommonLibF4's 8 bytes; MS x64, the handle in rcx). The file is trusted only when
its size is 8 + 16 × its count, five IDs give the RVAs this plugin has from F4SE 0.7.9's source
(PlayerCamera::Singleton 4796065 at 0x030E6E58, TESDataHandler::Singleton 4796135 at 0x030E7100,
PlayerControls::Singleton 4799306 at 0x031F0B80, INISettingCollection::Singleton 2704108 at 0x0344B4B8,
INIPrefSettingCollection::Singleton 2703234 at 0x0339FAE0: a library of another game version fails here), and the
three lie in an executable section of the game by its PE headers (its .text; since test 46 a sixth ID is checked as
well, *The levels* above); else one line why, and every set is
declined: "sound: no Address Library at …", "… is not the expected format (N bytes, not 8 + 16 x its count N) …", "…
doesn't match this game (ID N gives 0x… where the plugin has 0x…, …) …", "sound: BSSoundHandle::SetFrequency (ID
2267059) at +0x… isn't in the game's code (…) …". Found: "sound: the Address Library at … (N ids) matches this game
(…); BSSoundHandle::SetFrequency +0x…, FadeTo +0x…, IsPlaying +0x…, in .text".

**Assumptions test 44 tells:** a Papyrus instance id is the handle's sound id (`IsPlaying`'s count says); `FadeTo`'s
attenuation is in hundredths of a dB (the levels against the game's other sounds); `Sound.SetInstanceVolume` and that
attenuation multiply (if the volume replaced it, moving the MCM's slider mid-ride would bring the silent loops in);
`SetFrequency` takes ratios over 1 (else the clamp line); the game neither culls nor restarts a loop at volume 0; and
the nine may blip for a frame between their `Play` and the volume-0 call. Test 45's tester answered two by
disassembling the game: `FadeTo`'s attenuation is in hundredths of a dB (its fade at least 100 ms, linear in dB from
where it finds the loop), and the instance volume enters the voice as 2000 × log10 of it beside that attenuation, so
the two multiply.

The harness plays the controller's side in its mode sound (54 checks in test 44's build, 61 since test 45, 63 since its
review, 74 since test 46, 82 since test 47, the same 82 since the 2026-10-31a build, 91 since the 2026-11-01a build):
the settings lines (three since test 45) and the globals line; riding with nothing handed over, no call and no library
read (as in the other 16 modes, whose counts are unchanged); declines for no library, a cross-check 8 off, one cut
short, `SetFrequency` in its data and `Drive=0`; a good library taken within two frames, with the `IsPlaying` line; at
rest the idle at 1204 (0.7 × −17.2 dB; 516, 0.3 × −17.2, in test 44's build) at pitch 1 and the other ten at 10000; full
throttle from rest logging gears 2, 3 and 4 at 2394 rpm (heard 540 u/s, the bike 896), 2383 (729, 900) and 2317 (900,
900), the heard speed shifting long after the bike reached its top speed (a few rpm either way from run to run: the
fake's frame timing moves the speed the plugin reads), where the Python twin fed with the plugin's throttle and its 0.2
s speed lag shifts at 2393 (540, 896), 2381 (729, 900) and 2316 (900, 900), the first pull's shift point drawn at 2429;
at the top speed On2000 alone at a pitch of about 0.973 (1937/2000 = 0.9685, the wander within 0.03) and about 611 (617
expected, −6.17 dB), the trace's "| engine g4 19.. rpm load … heard 900"; every call a move past the thresholds, a
steady cruise under 20 calls a second (under 5 with `Wander=0`); since test 45 a 0.3 s tap of the key at the cruise with
no gear change (test 44: 4 to 3 on the press, back 0.5 s later), and a let-up at the cruise to a stop falling in 4th
with engine braking, every down-shift a blip, the clutch at the bike's 150 u/s from over 1600 rpm (2123; the twin: a
blip 4 to 3 at 1667, the clutch at 2202), then the idle; since test 45's review forward held 12 s from rest with the
fake no faster than 300 and then 360 u/s (a lower MCM Speed: 100% gives 360), each a new set, with no gear change at
all, the trace's last "| engine g1 2043 rpm … heard 300" and "g1 2193 … heard 360" (the twin the same; 9f61073's DLL
fails both, 1 to 2 and back every 2 s); the ids to 0, `CMB_SndDriven` 0, no call after and the let-go line's new words
with no failures counted; a set with one id 0 declined; a changed `Loops` line, `LevelScale` and `FirstFade` read on
getting on; since test 45 test 44's settings (`HeardSpeed=0`, `CoastFall=70`, `DownRpm=1750`, `LevelScale=0.3`,
`ClutchFall=900`, `LaunchDraw=0,0`, `LaunchRise=0`, `ShiftDraw=0,0`, `DownHold=0`, `DownHeld=0`) read on getting on
giving test 44's model again, each part named so on the third line, the idle at 516, the gears at 557 u/s and 2368 rpm,
887 and 2917, 900 and 2344 (test 44's twin: 556/2365, 887/2918, 900/2344) with no heard speed in their lines, On2000 at
268 (264); a load with the controller's next set after the plugin's first frame and before it; the over-1 clamp; the
ride ending with the ids still set; a set offered off the bike. Not checked there: the give-up after 30 calls returning
false, the keys read from the speed, the gear lines' limit, the gears scaled by `FullSpeed`, a set taken with only some
loops playing, and `held` from the face rays, a ram or the climb. Since test 46 the fake game takes `SetVolume` as the
game does (the volume truncated to thousandths, applied at once, clamped to 1e-5 to 1) and `FadeTo` by the game's rule
(100 ms at least, linear in dB from the current attenuation), plays the script's starting levels and has a
`CMB_EngineVolume` at 70, and run.sh's `[Sound]` has `SetVolume=1`, `LevelScale=1` and `LevelOffset=5`; the eleven more
checks: a library with SetVolume's ID 8 off declined, nothing called; the take-over's 11 `SetVolume`s and no `FadeTo`,
the idle's first at 0.7 (the script's level) and FirstFade's ramp near halfway at 0.2 s; at rest the idle at 0.3508
(-6.0 dB × 0.7; since the 2026-11-02a build, `IdleDb` -11: `IdleDb=-17.2` 0.1718, the built-in default without the key
0.3508, the summed gain through a coast to a stop 0.499-0.503 from +2.5 s and through a brake 0.500 from +1.5 s, the
2026-11-01a build's 0.243-0.244); the MCM's 100, 0 and 70 within two frames, one line each; full throttle from rest (6
family switches, 7 hand-overs) with the loops' power sum within 0.06 dB of the level asked, never under -1 dB, and no
`FadeTo`; On2000 at the cruise at 0.451 (-3.81 dB × 0.7); `SetVolume=0` with test 45's levels showing test 45's holes on
the same pull (down to -35 dB, 1.3 s of the 8 under -10 dB), the engine volume put on all eleven 0.15 s after the
take-over and on a change of it; and the older checks' numbers in the new levels. Since test 47 run.sh's `[Sound]`
writes `Wander` 0.025 and `WanderTau`, `WanderLevel`, `WanderSteady`, `WanderSmooth` and `ShiftDip` at their defaults,
so a ride can turn them off, and the fake keeps its engine volume at 70, as a save would; the fake records the heard
level and the up-shifts' moments through a pull and On2000's pitch and level through a cruise (`SndDips`,
`SndWanderWindows`, `SndHandMax`). The eight more checks: the fourth settings line; the first pull's dips, -4.02, -4.01
and -6.05 dB against the 0.2 s before, 0.150, 0.150 and 0.529 s under -3 dB (the twin -4.0, -4.0 and -6.2); no hand
through the pull (the trace's " hand " 0.00% in 1st to 3rd); a 32 s cruise in 8 windows of 4 s, On2000's pitch 0.99% and
its level 0.30 dB moving together, 0.30 dB per 1% (the twin 1.02, 0.30 and 0.30), and the trace's hand up to 4.66%
there; and a ride at test 46's six values, its line so, its up-shifts -0.87, -0.41 and -3.60 dB, none under -3 but the
last, and its cruise 23 calls in 2 s, all on On2000, at 0.9701 and 0.4510. Changed: the cruise's pitch and level, which
move together now (0.9902, +2.25% of wander, and 0.4880, +0.68 dB for +0.67), the steady cruise's calls (152 in 2 s of
385 frames, 122 `SetVolume`, one a frame at most, and 30 `SetFrequency`), the `Wander=0` ride's strings, and test 44's
ride with the six at test 46's values. Since the 2026-10-31a build run.sh's `[Sound]` writes `Wander` 0.055,
`WanderSmooth` 0.5 and `WanderMax` 0.06, which the rides at test 46's and test 44's values turn to 0 with the rest
(seven keys), and the fake also measures the whole 32 s cruise against its own mean (`SndWanderWhole`). No check more;
the ones the bigger hand moves, around its numbers (the twin's 32 s cruises over 150 seeds giving the spread: 4 s
windows 0.87 to 1.55%, the level 0.26 to 0.47 dB, the sd against the mean 2.3 to 3.7%, the hand at most 4.8 to 5.9%, 2nd
to 98th percentile): the fourth line with `WanderMax=0.06` and "held softly under WanderMax" (test 46's: `WanderMax=0`,
"unheld (WanderMax=0, as 27c)"), the model's line with "Wander=0.055"; On2000 at the cruise within 6.5% of 0.9685 (7
before; 0.9903 and 0.9808, +2.26 and +1.27%, its level +0.73 and +0.44 dB for +0.68 and +0.38 expected, in two runs);
the 32 s cruise's windows 0.8 to 1.7% (0.6 to 1.6 before) and 0.2 to 0.55 dB (0.15 to 0.6), 1.13 and 1.08%, 0.35 and
0.33 dB, 0.30 dB per 1%, and now its sd against its mean 2.2 to 4.0% (2.50 both runs) and at most 7.5% off it (4.51,
4.47); the trace's hand 4.5 to 6% (over 0.5 before: 5.33 and 5.31, 4.66 to 4.72 in 27c's). The steady cruise's calls:
145 and 135 in 2 s, 117 and 111 `SetVolume`, 28 and 24 `SetFrequency`. Since the 2026-11-01a build run.sh's `[Sound]`
writes `ShiftDraw` 2300,3000 and `StopShift`, `HeardStop`, `HeardBrake`, `StopGap`, `StopHold` and `StopAfter` at their
defaults, and the harness exports `CMB_TestKeyState` for the brake key (Space held through it). Changed: the first
pull's gear lines, now 2598 (heard 585, the bike 900), 2586 (790, 900) and 2344 (900, 900) (the twin 2599, 2587 and
2343; the first shift point drawn at 2634), its dips -4.02, -4.01 and -5.46 dB (the twin -4.0, -4.0 and -5.7); no hand
through the pull is checked in 1st and 2nd (3rd sits at its top a moment now, the throttle steady: the hand grows
there); the let-go at the cruise, now "gear 3 at 725 u/s, 1727 rpm, … a blip", 2 at 1811 (525 u/s, +0.46 s), 1 at 1836
(313, +0.47), then "gear 1 at 178 u/s, 2133 rpm, … (clutch in)" 0.30 s later (the twin 1730, 1812, 1835 and 2134; each
0.38 s apart at least, the clutch 0.25 to 0.40 s after the last); test 44's ride with the fifth line's "nothing
(StopShift needs HeardSpeed=1 …)". The nine more: the fifth settings line; the trace's " blip" and " clutch"; an 0.8 s
let-off at the cruise (the throttle shut 0.5 s as the engine reads it: forward is kept 0.2 s over (0, 0) reads and held
0.1 s) and a 0.05 s tap of back with no gear line, where `StopAfter=0` blips 4->3 at 1731 (the twin 1734); back 0.6 s at
the cruise (0.7 s as the engine reads it), blips 3 and 2 at 1796 and 1636 rpm 0.40 s apart, the clutch from 2nd at 1285
0.40 s after and 0.40 s after the bike's own 150 (the twin 1790, 1631 and 1525 with 0.7 s of braking; 1632 with 0.6);
the same with forward held and Space (the brake key) for 0.6 s, 1797, 1635 and 1448; the hand-over line 7 s after the
ride's start (none 3 s after); and `StopShift=0` with `ShiftDraw=2000,2900` giving the 2026-10-31a build's line, its
pull at 2394, 2384 and 2317 and its stop, one blip 4->3 at 1668 and the clutch at 2051. Not a check, printed: a 0.15 s
tap of back at the cruise (0.25 s of braking as the engine reads it) blips 4->3 and changes up again. Mode backing (46
checks before) has ten more for the brake key: its line on getting on; at 900 with forward held, Space 0.6 s takes the
input to 0 in 0.39 s (0.40 ±0.03) and the bike under 150, the first press's line once, and both let go together the
throttle stays off; stopped with both held 1 s the bike moves 0.0 with (-0, -0) every frame and no push back, both let
go no lurch, and Space let go with forward held it pulls away (204 in a second); Space with S held no reverse, then S
alone backs up (-113 in 1.5 s); Space and S let go together no push back, Space and A no creep; `BrakeKey=0` its line
and Space doing nothing at 900; `BrakeKey=31` refused, S still backing up; the MCM's 0 then 31 a line each, its 75 "Num
4 (VK 0x64)" and braking on that key. Mode roomold (an ESP without the 2026-11-01a build's globals) has one:
"BrakeKey=-1: no CMB_BrakeKey in the ESP: 57, Space".

**Test 49's answer (the 2026-11-06a build).** "Idle could be a slightly louder"; a longer gear-change sound; a punchier
take-off. `IdleDb` -9 (-11 before, in both twins: the C and `engine_model.py`): the idle at -4.0 dB, level with the
cruise (-3.8 at 1937 rpm); the floor now holds the throttle shut under 2250 rpm, so a let-off at the cruise keeps its
level (the off family's timbre and the rpm's dip still tell it); the start and stop sounds step 2 dB into and out of it
(rebuilding the one-shots at -4 is left for a test that hears it). An up-shift's gap `ShiftTime` 0.55 s (0.35) with
`ShiftDipTime` 0.4 (0.24): the off family through 0.55 s of each gap, the dip 0.24 s under -3 dB, the shift points as
before, no cut-out (the summed level moves at most 0.51 dB a frame). The launch rev (`LaunchFlare` 0.5 over
`LaunchFlareTime` 1.2 s): a press in 1st in a launch, the bike under `ClutchSpeed`, revs the slip x (1 + 0.5 x a cosine
share 1 -> 0): 1938 rpm and -1.1 dB at +0.5 s where 2026-11-02a had 1432 and -5.2; only 1st's rpm target moves (the gear
decisions read the slip itself), so the gear schedule is the tester's. A sixth settings line says it ("  sound:
LaunchFlare=0.5 LaunchFlareTime=1.2: a launch press revs the slip LaunchFlare over itself, fading out over
LaunchFlareTime s (the gears as before)"; at 0 "... no launch rev (LaunchFlare=0, as the 2026-11-02a build)").
`engine_model.py --check-off` now checks three builds' off values, the 2026-11-02a build's four (`IdleDb=-11`,
`ShiftTime=0.35`, `ShiftDipTime=0.24`, `LaunchFlare=0`) against f0253e8's own model frame for frame. In the harness
(mode `sound`, 100 checks, 5 more): the idle at rest 0.4410 (0.4417 = 0.7 x 10^(-4/20)); the launch rev's heard rpm at
most 1936 in the first 0.8 s, 1936 at +0.5 s (the twin 1938), the summed level there 0.618 (the twin 0.62); at the four
off values 1435 rpm at +0.5 s, at most 1613, the family switches 0.355, 0.350, 0.350 s apart and the dips 0.149 s under
-3 dB; at the defaults the up-shifts' switches 0.552, 0.550, 0.552 s apart and the dips -4.02, -4.01, -6.07 dB, 0.248,
0.247, 0.294 s under -3 dB; the floor through a coast to a stop 0.629-0.633 (2026-11-02a 0.501).

## What has been verified without the game

| Check | How | Result |
|---|---|---|
| Plugin file structure | independent byte-level parser (group/record/subrecord sizes) | ok |
| Record layouts | compared field by field with xEdit's `wbDefinitionsFO4.pas` (MGEF, QUST VMAD, GLOB, KYWD, MESG, ALCH, ARMO, ARMA) | match after fixing GLOB `FNAM` and KYWD `CNAM` |
| Sound records | byte layout compared with xEdit's SNDR definition (descriptor type, loop flag, priority); since the 2026-11-02a build `check_plugin.py` also checks the 13 `CMB_Fx*SD` (each one's file count, first file, static attenuation 0, category 0172A1, loop flag, on `CMB_SOMMonoFx`), the three own lists' slots, the three borrowed lists unchanged and no SoundDescriptor on another model; the generator throws if any form's ID is over 0xF00 (the ESL range's reserve) | ok; 198 records, HEDR's next ID 0x8AF; "checked 13 engine sounds: output model CMB_SOMMonoEngine (000871), its fields as written; checked 13 effect sounds: output model CMB_SOMMonoFx (00089D), static 0, the game's files by path" (the 2026-11-01a ESP fails it); since the 2026-11-06a build 208 records, next ID 0x8BA (10 new at 0x8B0-0x8B9, none at 0x8AF, which is kept for the customisation build's `CMB_LookCode`: the generator throws if any form takes it), the three re-pointed records (0x8A1, 0x8A2 and 0x8A9 `CMB_FxWaterRoadLPSD`) and the nine globals' values checked: "checked 13 effect sounds: output model CMB_SOMMonoFx (00089D), static 0, 12 the game's files by path and 1 the mod's own (CMB_FxWaterRoadLPSD)" (the 2026-11-02a ESP fails it) |
| Engine sounds | the synthesised set: loops checked for seamless wrap-around, waveform and spectrogram inspected. The recorded set (test 44's build): `tools/sound` run again from the downloaded recording, all 13 files byte for byte the set of demo D and `render.py` giving demo D again byte for byte; measured against the reference rides (the octave shape 0.45 dB rms from the user's three stretches over the riding, every loop's wrap seamless and at its base, under 5% of its cycles with a near twin). The model: the plugin's C twin byte for byte `cmb_engine.h`, which follows `engine_model.py` within 0.006 rpm over six rides, and the harness's gears where the Python's are (*The engine sound* above). Since test 45 (the heard speed): the C and the Python within 0.010 rpm and in every gear over five game profiles and the seven stretches of test 44's ride replayed (its speed and keys every 0.25 s), in the new settings and in test 44's; test 44's model so replayed matches the game's own trace rpm at a median ratio of 1.000, and the new one against paris as *The heard speed* says. Since test 46: the hotter files (`hot_loops.py`) moving `build_loops.py`'s seam check by under 0.7 points on every loop and each wrap's step as it was (0.34 to 2.18 times the median step), the RMS 2.3 to 2.5 dB up; `--gain 0` writes every file back byte for byte and two runs agree; the engine's output model read back from the written ESP field by field, and `check_plugin.py` failing HEAD's ESP and a dump with the distances at 150-2000 and one sound back on 07E5DC. Since test 47: `engine_model.py` at test 46's six values (`Wander=0.006 WanderTau=0.8`, the four new at 0) the old model exactly over a 32 s ride; at the defaults the hand 1.02% and 0.30 dB in 4 s windows at the cruise over 392 windows and 0.00% through a pull, the dips -4.0 dB at the ceiling and -6.2 into the cruise, and the harness's C the same within the fake's frame timing (0.99% and 0.30 dB over 32 s; -4.02, -4.01 and -6.05 dB); the output model read back as `SOMMono02000`'s fields but the distances, and `check_plugin.py` expecting exactly that line | ok; the user heard demo D, the set through the model as a ride, and chose it; test 44 in the game: every set driven as designed (11 of 11 loops, the rpm heard in the recording 0.998 of the trace's), the model "not natural"; test 45's heard speed untested in the game (demo E: 51 s of test 44's ride through it); test 45 in the game: 4 rides driven, 41,407 calls, none failed, the timbre within 1% of the render's, the cut-outs at the gear changes and hand-overs `FadeTo`'s (its tester's disassembly); test 46 in the game: 7 rides driven, 80,424 calls (SetFrequency 30,954, SetVolume 49,470, FadeTo 0), none failed, `SetVolume`'s place confirmed in the tester's own library (2267057 at 0x162E160), no cut-out left at 124 up-shifts (the median dip 2.4 dB, a median 0 ms under -10 dB), the cruise "doesn't fluctuate at all"; since test 47 (the throttle hand, the up-shift's dip, the output model `SOMMono02000`'s) untested in the game; since the 2026-11-01a build `StopShift=0` with `ShiftDraw=2000,2900` the old model exactly (`engine_model.py --check-off`: 0 of 44,136 frames over the demo ride, a random 60-segment ride and five stops, against 0c3df02's model), the C and the Python the same gear changes at the same frames over the same rides at the defaults (rpm within 0.03), and the C at the off values 0c3df02's C exactly; since the 2026-11-02a build `IdleDb=-17.2` the 2026-11-01a build's model exactly (`--check-off`: 0 of 44,136 frames against 993f582's model, and the 2026-10-31a check as before), the C and the Python within 0.028 rpm, 0.0003 dB and 0.00003 of the summed gain over the same rides at the defaults and at -17.2; since the 2026-11-06a build the 2026-11-02a build's four off values (`IdleDb=-11`, `ShiftTime=0.35`, `ShiftDipTime=0.24`, `LaunchFlare=0`) its model exactly (`--check-off`, three lines "the same, frame for frame over 44136 frames": 31a, 01a, 02a), the C's launch rev within 3 rpm of the twin's (1936 and 1938 at +0.5 s); the wet-road loop's own checks (`make_water_loop.py`: 8 of 8, the wrap's spectral, level and sample steps within the loop's own 90th/99th percentiles, the centroid within 15% of the example's, the band shares, the level at -23 dB A within 0.1, the peak under -3 dBFS) and a second run byte-identical |
| Rider-pose plugin builder | run on a stand-in load order (Mutagen-built `Fallout4.esm` with the player's real folder lists, recovered from the AnimTextData IDs, plus an Unofficial-Patch-like additive race with its own keyword), output read back with Mutagen | right entries copied, extra master added, keywords remapped, AnimTextData found for every entry and written |
| AnimTextData | ID formula reproduces all 8 files of a Creation Kit-built mod and 110 vanilla IDs; all 109 reference files parse and re-write byte for byte; folder search order matches all 193 male / 191 female resolved clips | ok |
| Compiled scripts | Caprica, Fallout 4 target: header v3.9, game 2, for all 11 scripts (`CMB_RamScript` since test 41, `CMB_StaggerWatchEffectScript` since 2026-11-01a) | ok; `CMB_RamScript` ran in test 41 (16 hits told, 16 knocked over) |
| Slope plugin | `tools/f4se-slope/test/run.sh`: the DLL loaded under Wine by a stand-in game and F4SE (objects with MSVC RTTI at the 1.11.240 addresses): finds the globals, the controller and the proxy; sets and restores the limit and the camera distance; sets the limit again on the very next frame when the game resets it; never less steep, the camera never closer than the player's own; leaves an unexpected value alone (the 47° guard); a new controller after a load; the controller gone mid-ride; read-only without the offset (the camera still works); refuses another game version. Tilt: a fake player 3D and biped with the bike's skin at COM's real bind: an averaged ground normal (Z 0 in the air); holds the skin while riding and turns its mesh up onto a 20° uphill normal (nose up, still a rotation, the seat where it was, culling sphere grown); ignores a one-frame 40° jump; pitches by the track (10° up a slope whose normal jumps up to 40° every frame, and backwards down it, still nose up), holds standing still and through a quarter and a half turn on the spot (no flip); starts level after a ride ended by taking the bike off; rolls a 45° side slope only as far as `MaxRoll` (10 in one run, 0 in another); holds in the air; puts the skin back byte for byte and releases it on getting off; lets go when the bike is taken off mid-ride (deleted with the last reference); leaves non-rigid skin data alone; finds the bike through the biped alone, by its bind under another name, and the planted variant as our armor addon's shape (and keeps it while tilted, when its bind no longer looks like COM's: a hold-and-drop loop the harness caught); logs what it saw when there's no bike; the same with transposed matrices; no tilt when skin and 3D disagree. Track: a spot 145 units back after riding up a 10° slope (position, angle and up exact), up a 40° one and after a U-turn, back down on the flat after a 60° rock face (whose slope `CMB_TrackSlope` reports, also turned sideways on it, but not on a level ride with a wild normal), back where the ground leans 20° or less across the bike after riding along a 40° side slope, none after a drop or a teleport. Zoom: all the way out on getting on, the player's after 2 s, back on getting off, left alone when the values aren't fractions Steering: 20°/s when stopped, at most speed/radius moving, the radius from 50 at walking pace to 180 at riding speed with 60°/s stopped, left alone with radius 0. Input hook: a stand-in `MovementHandler` with its vtable on a read-only page (as in the game) that sets the move input from the held keys every frame, or adds the change on a press or release, and a movement that turns towards the keys and moves forward along the facing: its button, thumbstick and per-frame functions wrapped (and the movement output, watched); a side key from a stop turns the bike 60°/s and creeps it (stuck against something, the input winds up to 1 and once free the surge is cut within a fraction of a second, 35 units at twice the game's gain, then it creeps on; in a game that clears the input again after the keys on every frame, the creep goes on, the movement gets ours, and a key let go of stops it within the 0.2 s the keys are kept; on rough ground that only moves above an input of 0.5 it winds up to 0.56 and creeps at 55; back on the flat, no surge from that) at about 26 units/s (the game gets (0, 0.029)); the handler a struct, both vtables at 1.11.240's addresses; a game that clears the input every frame and sets each held key's half: a side key let go of while backing doesn't stick, nor creep afterwards, forward and right left alone; back gets the game (−0, −0), steps after rays (through the Address Library file the test writes, fake picking with collision layers) back the bike up at 80 units/s, facing forward, back and right swings the nose left; the adding handler isn't left driving forward on release; after a load a test ray that finds no ground is tried again 3 s later; it stops 150 short of a wall, a chain-link fence (layer 26) and a drop, passes through a trigger volume and backs over a tin can (layer 4) and a pile of six bits of clutter under the rear, backs down a 30° slope with the wheels on the ground and the track kept (a park spot) while the controller says in the air all the way, and with a car beside its rear, back and right swings the rear only until its corner reaches the car, then stops (straight back would hit it too) and back and left swings it away; in a game that doesn't honour SetPosition, back brakes, and 3 s later from a stop the method is tried again and backs up; a back press at 900 with a side key while the bike still slides gives no verdict (test 20's first press cost it reverse for the session), and from a stop the method is kept; not riding, the keys go through. Moving parts (the `[Parts]` section and three more shapes with their own skins, their culling spheres on the axles and ahead of the steering head): told apart as the wheels and the bar assembly; riding forward 45 units both wheels turn 1.5 rad with the top going forward and the fixed part isn't spun; a right turn from a stop puts the bar assembly over 10° to the right (its sphere grown by the little its centre moves) and the front wheel with it, still spinning, the fixed part not turned; a left turn 10° left; stopped, straight again; rolled back 40 units the rear wheel turns 1.3 rad the other way. Since then (tests 29 to 38) the checks have grown with each round: the wheel rays and the lift, the face rays' verdicts (a wall, an obstacle held at 55%, one at the wheel left free, a 52-degree face an obstacle and a 45-degree one none, a hit on the rider's own 3D passed), the COLL record read at the 0x18 layout with the phantoms it holds passed, the suspension (a front step compressed and rebounding, the rear rising at most 4), the torso lean's solve waiting out a raised arm and a short reach, the wrist rolled about the grip's axis, the lower fork turned and offset with the front wheel, and the region cache's spread (no sync re-querying more than 25 regions over 40 s, counted through the DLL's import table); test 38's round: the front wheel and fork moved along the steering axis, a hole leaving a wheel at its droop, extension slower than compression, the frame sinking by the droop with both hits below the contact, the lift held when the rays miss, the bars the key's way backing up, low faces of 52 degrees given no verdict and of 65 one, the elbow bent the pole's way, the grip's centre kept on the bar with the wrist swung round it, the lean taken as it comes and solved again when the riding pose comes or after a 1000-unit jump, the lean's cap past the old 15 degrees, the lift still held at 2.5 s without a word and gone by 4.5, the bars staying the key's way when the back key is let go with a side key held, no re-solve of the lean on a hop or a frame's stall, the thrown-away wheel-ray line naming the other ray's hit, the arm line's grip distance the clips', a Belly_skin bone under the spine leaning with it and a thigh helper under the pelvis not; test 39's round: backing with no step's gap closed while the controller holds itself supported and closed to 0.5 over the ground, 3 a frame at most, while it doesn't, an actor's capsule over the front wheel passed by the wheels' rays (no pitch, no lift) while one ahead still eases the throttle, twenty actor surfaces piled over the front wheel read as nothing rather than the eighth, the wheels' lines from a hand of 10 refilled one per 6 s with a backing hand of its own, the hand's long axis along the forearm within a tenth of a degree and `HandPitch` 10 on either hand, the lean final on two agreeing readings of the riding pose, a 95% start re-solved to the 100% figure, the solve kept through a 1000-unit jump and final as it stands, a start taken as it comes solved again after a jump, and the ride's wrist max leaving out a reach of 120% and a Pip-Boy raise held still; test 41's round, in five modes of their own (mode 0 takes about 507 s of the 600 a call may run), the new checks failing on the DLL before each: load (43: the session before's log kept and named on the first line; a load into a ride held afresh within 2.5 s in each case the plan suspected, the 3D replaced in place or 150000 units off, the body's bone data half built, the bike's skin with no transforms to read yet, the arm and spine nodes rebuilt, where test 40's DLL never held the rider again, left the frame level or wrote stale bones; `CMB_TiltLive` left at 0 by a load, test 40's picture, logged and gone once it's set; a load into the air, the bike level but the rider leaned), climb (50, with a model of the capsule stopping at a face: round logs 22 and 30 across climbed at 85 and the limit back to 47, both stuck with `Climb=0`; a 40 step, a wall, an actor, a 35-degree rise and the foot of a slope given no boost, the step, the actor and the rise with their lines; the boost cut by getting off and by loads on the bike and on foot; given up after 1.5 s stalled with the MCM at 60; 80 face-ray verdict changes still logged past the 60th; a stump 26 high stepped up 27.5 and 4 on, two steps logged as not taken where `SetPosition` isn't honoured, no step with something 90 over the top, none with `ClimbStep=0`), ram (42: asked once and the hit told 0.06 s of the speed before the wheel, braked for with no answer, a no, a race too big or flagged No Knockdowns, the MCM off and under `CMB_RamMinSpeed`; let by for `Pass`; a wall 20 behind a yes seen through it and stopped short of; two actors 50 apart both hit, told 0.12 s apart; the throttle held at the input for 540 a second for 0.4 s; `Enabled=0`; a placed object's 3D no actor), arms (19: the arm line's five figures against the written bones within 0.05, the inside elbow 0.5 of the way to `ArmPoleTurn` at 5 degrees of the bars and all of it at 12, the outside one on `ArmPole`, mirrored for the right arm, the riding line once a hold at 450 a second and not at 200, the fade on the ride-end wrist line, `ArmPoleTurn=0,0,0`) and backing (27, with the controller falling at 686 units a second squared when unsupported: a brow and a dip followed within 0.48, against 8.9 by test 40's rule; down 20 degrees in the air every step moved by the plugin, the vertical speed's change per step 2.2 at the 99th percentile against 45; a gap of 2.0 kept, its own; a ripple averaged out; an edge not followed; a window ray missing covered by the slope 55 back; `BackFollow=0` test 40's rule); test 41's second round, after its report: full (349, 8 more: a hat shape skinned to HEAD, to a node-less Head_skin whose own transform copies HEAD's world every frame, and to a node-less bone 10 above the head: Head_skin's written world equal to HEAD's within 0.05 units and 0.1 degrees through the torso's lean and in the roll ride with the level head, the bone 10 above carried with the tilt alone, the hold's line "1 with the head; 1 placed by the node they sit on", the hands' line with its old fields and 0 placed by a node, and with `NodelessNear=0` Head_skin carried with the tilt alone while HEAD's joint goes 7.4 forward, test 41's stretched hat), ram (52, 10 more: the settings line with AskGap; "no CMB_Room globals" once, the ESP without them; a pack with the second actor seen 50 ms after the first, the asks told 0.124 s apart and the script's 0.1 s poll, played with its phase against the asks fixed, reading both, 0 unread, two hits, the "its ask waits" and "ask told the script" lines; with `AskGap=0` written and read again on getting on, the second ask 0.058 s after the first, one unread, the first actor asked twice, no "waits" line) and room (22: the section above); test 42's round (test 43's build): climb (69, 19 more: riding beside a railing, the fake's picks giving each hit its normal at +0x70 and its capsule a slide that keeps 0.4 of the motion along a face from contact, its speed following the game's input curve so the cap binds as in the game: a plane at 60 degrees to the heading still a wall, stopped short of; at 10 degrees no wall or obstacle line, one "a face alongside, 10 deg off the heading" line and the input full to contact, then 498 along it in the second after contact, one "slide: along a face" and one "slide: over after" line, no "held to the measured speed" within 0.8 s and no climb boost; `SlideHold=0` 274 in that second, under 0.65 of it, three "held" lines and no slide line; `FaceAlong=0` a wall as before; `FaceAlongRays=0` alongside by the normal alone; a plane at 40 degrees a wall; a post 20 wide with a normal 15 degrees off, a side ray missing it, a wall with the "but the rays either side don't say so" words; picks giving zero normals: the "not a unit vector" line once and walls as before; a step 15 high across the way with a tall face 12 degrees off the heading 127 past the axis at it: held at the step, no boost, one "not climbed: a face alongside, 12 deg off the heading (FakeWall, layer 1, the face rays' verdict)" line, both failing with the `CLIMB_ALONG` clause taken out), full (367, 18 more: the landing, inside the suspension's ride, the fake's ground 180 lower past an edge and its speed cut to 0.35 for 0.45 s after a landing as the game's: no landing line from a 0.2 s hop; off the drop, 0.72 s in the air and the fall about 490 a second, one line with the throttle kept and the frame sunk, the input full for the half second after it, no "held to the measured speed" within 0.75 s, the wheels at +6.9 and +3.5 within 0.15 s and the seat 4.8 down at its lowest, back by +0.6 s; `LandHold=0` and `LandSink=0` the input down to 0.72 within 0.4 s and the wheels still; frozen at the landing, the hold ended by the speed under `LandStop` within 0.35 s and the bike under 450 a second once free; and the backing checks at a wall, a pile, a fence, a car's corner and a drop edited in place for the clearance of 92 from the parts file, 66.6 + 25, with no new riding), backing (40, 13 more: with the parts file, a rail 20 to 40 high 100 behind stopped at with it 91.8 behind the rider, 25 behind the tyre, and the clearance's line and the tyre's trace; a ledge 25 deep 90 behind stopped at by the tyre's ray with the edge 66.6 behind, then with `BackLedge=0` by the rule under the step with the tyre 66.5 over it; `BackClearance=150` 150 short of a wall again; the physics-lite fall's landing not sunk with `Suspension=0` and no throttle kept; a slow landing, forward pressed 0.25 s into a fall of 60, "the throttle not held (the speed along 109 under LandStop's 0.25 of the top)" and no "stopped by something"), ram (89, 37 more: the second settings line; the robots' list read and its races named, a listed race with No Knockdowns asked and hit, `Robots=0` and a list holding a non-race refused; the pack's asks told once answered, the "told anyway" line once for a script that never answers; an actor stepping in 250 past the wheel kept at full input by `AskFree`, about 0.6 with it off; a yes kept out of sight and its hit on the first ask, asked twice with `YesKeep=0`; two hits 230 apart at full speed with `CMB_RamMinSpeed` 650, the second by `HitGrace`, one with it off; an actor 60 to 130 up seen by the high ray and one 30 to the right by the right ray, neither with its key at 0; the test-41 rides with `AskAnswered=0`), room (47, 25 more: the section above), roomold (29, a mode of its own: the section above) and sound (54, a mode of its own since test 44's build: *The engine sound* above), mode full taking about 529 s of the 560 the harness gives a mode; test 44's round (test 45's build): climb (87, 18 more: the "  climb:" line's `ClimbMaxTop` clause; a rail 27 high, its top 10 deep with flat ground behind, no boost and no step up, the bike held at it and one "a beam with a drop behind it … not round (90 deg at its foot) and long (the rays 36 to either side meet it too) … the ground 0.0 over the ground at its foot" line; a step 25 high whose top runs on 400 boosted ("a step up, the ground 25.0 over the ground at its foot") and stepped up onto, +26.5 with the feet 25.0 up, then "over it"; since the review the same step on a 4 degree slope up to it and down to it (its top level, "the ground 25.1" and "24.9"), boosted and stepped up onto as on the flat; round logs 25 and 30 across (the fake's rays see a circle) boosted and over, "round, receding toward its foot"; a stump 25 high and 30 across, "narrow, the ray 36 to the left passes it", stepped up onto; a barrier, a foot 8 high and a bar from 40 to 65 25 past its face, no boost, held at the foot, one "a bar beyond the low face: something at 48 above the feet 43 ahead" line, and with `ClimbMaxTop=0` boosted at the foot as in test 44's build; the fake's capsule now measures its feet over the ground where they stood before the frame's move, so one held at a face on a slope down no longer creeps up it; the climb mode's INI at `ClimbMaxTop=0` so every check before it runs under test 44's rule, these rides writing 18 and back), backing (46, 6 more: the "  reverse:" line; a beam 30 high and 40 deep under the capsule backed off, about 200 units with the feet on the ground behind, one "hung up" line and no "drops away"; a beam 50 high stopped at with "(50 down, over …)"; with `BackHungDrop=0` the 30 beam a stop as in test 44's build, then 40 again), ram (110, 21 more: the third "  ram:" line; a wolf, a small race, stepping in 60 past the wheel passed with the input at 1.000 and hit -129 past it on its yes, with `PendingPass=0` the input down to about 0.12 and the "no answer in" line; a medium actor hit, pushed and back 250 ahead 3.48 s later asked afresh with no wall line and hit at 892; back 2.73 s later, inside the fake script's `Cooldown` (a no under 3 s after its push, 0.2 s after the hit), braked for as the hit's, asked afresh 3.29 s after the hit with no cooldown no, and hit at 190 by `SeenGrace`, which with 9f61073's plugin got the cooldown no at 2.74 s; with `FaceActors=0` "a wall ahead (SkeletonExport, layer 30)" and a stop short; the protectron's race large with `CMB_RamMinSpeed` 650, hit at 607 by `SeenGrace`, with it at 0 "under 650: not knocked over"; the large protectron kept to by `AskFree`, no wall line, hit at 859; HitGrace's off ride writing `SeenGrace=0` too), room (82, 36 more: the "  room:" line; a fence 90 high halfway to the spot, none and -3; a floor 34 up at the spot, none and -34; the spot's ground 21 below past an edge with room, and with the fence between none by the line; asks 5 and 15 made against the player's ground; `Line=0` with `GroundNear=60` read on getting on, test 44's answers again; since the review a 15 degree slope rising and falling ahead, spots 1, 6 and 7 with room, a hedge 45 high refused as a step, and with `GroundSlope=0` the downhill spot refused with its box checked and the uphill one without), roomold (40, 10 more: the line's rides on test 42's ESP), sound (63, 9 more: *The engine sound* above; since the review forward held at a steady 300 and 360 in one gear throughout), the 11 others unchanged, mode full 530 s of the 560; test 45's round (test 46's build): climb (103, 16 more: a guard rail met at 40 degrees, its beam from 20 to 28 over the ground, and a picket fence's post, the rays at 18 to the sides passing under the rail, both not narrow by the rays at 24, held at the post with no boost and the beam's line naming the heights, and with `NarrowHeights=1` the boost on as in test 45's build; a rail lying on the ground, 13 high and 10 deep, held with one "a low beam with a drop behind it" line, and with `ClimbBeamLow=0` boosted; a kerb 12 high, a round log 16 across and a stump 12 high still climbed, each with its word; the fake game's speed change limited (1500 down, 400 up a second a second) for a rail dead ahead at 900, first seen 378 past the front wheel by the longer cast, the throttle 0 at once and the front wheel's edge 10 from it at the closest, with `WallStop=0` seen at 268, eased to 99% and the wheel at it; the same rail appearing 187 ahead, 0% (`WallStop=0`: 73%, test 45's 68%); a face 20 degrees off the heading alongside as before, no wall line; since the review a post whose normal reads 15 degrees off, the rays either side missing it, first seen within `FaceLook`'s reach and eased by it (over 50%, no `WallStop` word), climb 104, 17 more), riderinplace (17, 7 more: the AP watch's first line at once on getting off with the four gates and the modifiers, none while riding, the window's lines and its end, silence after, a line per change, `APWatch=0` none, nothing written), room (103, 21 more: the section above), roomold (41, 1 more: no test-46 globals, one line, nothing written) and sound (74, 11 more: *The engine sound* above), the 12 others unchanged, mode full 528.5 s of the 560 (529.5 before this build's review fixes); test 46's round (test 47's build): climb (123, 19 more: a raised rail 1100 ahead at 900 first seen 768 past the front wheel by the longer rays, eased from 100%, the input over 0.78 through its first 0.3 s and the front wheel's edge stopping 40 from it; a rail 187 past the front wheel held to `WallStopNear`'s floor, 0.54 at the least for 0.14 s, then 0, and 0 at once with it off (its default since the review); a post 200 ahead gone after 0.1 s with a rail 70 behind it, the verdict's move logged; a rail 400 ahead for 0.1 s, the input 0.67 at the least, 0 with `WallStopPersist=0`; turning at 40 degrees a second past a rail 160 wide 600 ahead, no wall line and full input, cut with `WallStopArc=0`; a rail met at 200 stopped 40.0 short, 10.6 with `WallStopShort=0`; a wooden barrier 27 high met 18 degrees off the heading, no boost and the beam's line naming the side rays across its face, boosted with `NarrowBoth=0`; a fallen board 40 across met 10 from its end narrow still and climbed; a face with the front wheel 49 up on it and the rear level, standing (8 in 2 s) with the "a face the front wheel is in" line, rolling on at 55% with `UnderBikeTop=0`, and under the bike as before with the ground 40 up under both wheels, the feet 20 up, or the front wheel only 25 up; changed: test 46's own WallStop rides run with the five keys off, and the stump's, the post's and the low stump's narrow words), riderinplace (18, 1 more: the AP delay read at +0x68, AP's, 1.50, not the 9.00 decoy at +0x64), room (116, 13 more: *The brought bike's spot* above), roomold (42, 1 more: the same) and sound (82, 8 more: *The engine sound* above), the 12 others unchanged, mode full not timed again; test 47's review: climb (125, 2 more: back at about 870 after the 0.1 s glimpse, a rail placed 20 past the need (short of its extra) cut within 0.1 s and stopped 40 short, the floor only while it is past the need; turning at 40 degrees a second at 900, a post 20 across on the longer rays' first chord 150 past the front wheel, inside `FaceLook`'s reach, gone after 0.1 s, no WallStop line and the input 0.9 or more; both fail with test 47's first build, which also stopped 40 short of that rail, the harness's run-down going toward the input's speed; changed: the glimpse ride's rail 600 past the front wheel, not 400 (0 with `WallStopPersist=0` at 400 as before), the 187 rail's floor ridden with `WallStopNear=1` written, its default now 0, and the rides' wait after each 1 s, not 2.5, the mode 543 s, 610 before), room (117, 1 more: got on 100 behind where the bike stood across the way and rode 100 onto that spot, the spot beside asked, room as asked, not put back on the player), the 15 others unchanged, mode full 535 s of the 560 (the whole `run.sh` call, its build and Wine's start in it); the 2026-10-31a build (*The bike's look*): a new mode, look (50 checks: a fake bike of its own with the 28 new shapes, 27c's twelve and a ride of 50: every shape held and its role by its name, and with `RolesByName=0` 27c's rules, 27c's names giving 27c's roles either way; the needle at 90 and 900 u/s within a degree of the formula, clockwise, a pure turn about `NeedleAxis` while the bars turn, back to 0 after a stop, capped at `NeedleMax`; the brake light lit in the frame of the back key at 600 u/s and out `BrakeHold` after, never with `Brake=0`, and by the slowing alone without the input hook, but not for a jump of 5000 (a door, a fast travel) arriving at 300 u/s; the specks of `Glow=0`, `Backlight=0` and `Needle=0`, the lamp's ring and the dial's backlight with `SetHeadlamp`, each `Mirrors` value; every key off at once (`RolesByName` left at 1) giving 27c's look; 48 of the 50 held with one line naming the two left), the 17 others unchanged; the 2026-11-01a build (test 47's answer): full (381, 14 more: the landings with `LandSoft`, the game's hard landing passed to the graph as its soft one, the hold over at 1.00 of the landing's speed (0.94 on the 0.05 s measure) and 316 travelled from +0.1 to +0.45 s where the cut gives 110, `LandSoft=0` the cut as before; the landing cue, `CMB_FxAir` 1 at 0.354 s in the air, the level 1.00 at the landing and `CMB_FxAir` 0 by +0.313 s, the fake script's `CMB_FxLandPlayed` 0.027 s after, no flight for the 0.2 s hop, `Land=0` the level -1 throughout; test 29's decal checks changed for `OrphanRestore`: the decal back on the body's own data and the old copy free), transposed (76, 1 more: the graph wrapper's guard; changed: the game's bone data holds 3 references with `OrphanRestore`), arms (23, 4 more: the seat watch, one off and one back line for a 1.51 s standing, none in the first 1.0 s, none with the ground-planted bind), backing (56, 10 more: the brake key, the input to 0 in about 0.39 s, the bike held still with (-0, -0) every frame, pulling away with W once Space is let go, no lurch when both are let go together, S alone still backing up, `BrakeKey=0` and a move key's refusal; the review's: Space and S let go together no push back, Space and A no creep, the MCM's 0 then 31 a line each, its 75 "Num 4" braking), room (126, 9 more: `SnapSpot`'s navmesh point, its level line and ground window, the played pick's point 400 out, `CMB_RoomOptions` with bit 16, `SnapSpot=0`'s pick), roomold (49, 7 more: the older ESP's one line each for the pose check, the brake key, the room's ask kind and the fx globals, and the tail light's and the view's three), sound (91, 9 more: *The engine sound* above: `ShiftDraw` 2300,3000's pulls, `StopShift`'s blips and clutch on a let-go and a braked stop, the brake key's, `StopAfter=0`, the old values, the hand-over gap line), look (53, 3 more: the two brake discs' roles by their names and their maps equal to their tyres' while the wheels turn and the bars are at -8 deg), and four new modes, each check failing on the 2026-10-31a DLL or with its key off but the off values' own: decals (18; 67: logs.md's D1-D10 under the game's smart and raw re-points, the decals following their owner and not held, the copies reused by the walk, a full pool waited for, orphans put back, the re-points every frame and their rate-limited lines, test 47's drain reproduced with the 2026-10-31a keys and `RiderCopies=40`, the knees' raw seconds in `CMB_RiderPoseOff`, the review's D7b (a decal left on an orphan copy, held once, then following) and the census at a getting off with nothing held; *How approach A works*: the rider's copies and decals), wall (19; 34, 30 its own: *WallStop beside the turn* above), view (20; 58, 54 its own: the tail lamp's light kept at the lamp, 3x braking, `BrakeBy=dimmer`, the view bike shown within a frame of first person, every shape within 0.0005 of the worn bike's, the stale fallback and the review's turning on the spot with it live, `Lead`, the handovers, `Cull`'s flags, each key off, the review's ride with the tilt at 0 whose bike's skins go first, a load on it and the getting off with nothing held, and its handover whose high half comes a frame before the low, the pair naming a crate for that frame) and fx (21; 29, 25 its own: the water loop handed over at its fourth look (the fake's `IsPlaying` false for the first three), a loop that never plays declined at 0.35 s, driven by the depth and the speed with its splash, `Water=0`, `WaterSource=controller`, a load on the bike, a drop into water with an early `CMB_FxLandPlayed`, `LandSoft=0`'s first ride with no pool asked, the soft landings named from the game's own events); climb (125) and ram (110) as before with the new keys at their defaults, the 10 others unchanged, mode full 533 s and climb 541 s of the 560 (the whole `run.sh` call, two modes at a time); since the 2026-11-02a build (test 48's answer) a new mode and 97 more checks, each failing on the 2026-11-01a DLL or with its key off but the off values' own: hits (22; 22: the 2026-11-02a build's 3 globals found, the fourth ram line at load with the three before word for word, the defaults' hold at 85% for 0.25 s, the dip line and its "the rest is the game's", `HitChain` on and off, the roster's yes on and off, combat on and a No Knockdowns race in combat, a no while passed and the next approach braked, `PendingPass=0`), arms (33, 10 more: `UseLetGo`'s watch, the clip's let-go and ease, a prop in the hand, the clip's end and `UseMax`, no clip, the ride's line, `UseLetGo=0`), view (82, 24 more: the seat watch's first person, -1 within two frames, the knees not counted, back in third person, `PoseFirstPerson=0`; the eye: the settings line, the first frame's offset, only the node moved, 58 ms behind at 900, `EyeSmooth`, `EyeSide`, `EyeMax` out and back, a switch's far first frame with no lag in its probe and the next, near frame's offset at once, a handover, `Eye=0` bitwise 0; `StaleLines=3` and the ride's total, `FpsLine` every 10 s within 5% of the fake's rate, both off), look (55, 2 more: the light reference let go at a load and looked up afresh, the beam on the new reference), decals (77, 10 more: D7b's orphan re-pointed back on ours, never held again, under the smart, raw and `RepointEveryFrame=0` re-points; a let-go inside `RepointEveryFrame=0`'s window put on the body's own data, the orphan's reference given back), roomold (52, 3 more: the older ESP's 0 of 3 globals, no `CMB_RiderItemUse`, the fourth ram line without `CMB_RamCombat`), wall (52, 18 more: *Narrow things, kerbs and rails* above), sound (95, 4 more: the idle at `IdleDb=-11` and -17.2, the built-in default, the floor through a coast and a brake), fx (35, 6 more: `WaterGain=-6` and 0, the silent cue, the 10 dB range, the range at 18) and full (382, 1 more: the 180 drop's landing at the 10 dB range); mode 11 (ram) rides with `HitKeep=0.6 HitChain=0 PendingFoe=0` written, its 110 checks the off values', mode 0 with `LowObstacleThrottle=0`, mode 10 with `WallStopNarrow=0`; since the 2026-11-06a build (test 49's answer) a new mode and 81 more checks, each failing on the 2026-11-02a DLL (f0253e8's, or step 0's, which only looks the new globals up) or with its key off but the off values' own (the review fixes' 7 on the units' merged DLL): launch (23, new; 12: the 5 globals found, the curve's throttle at 0.25 / 0.45 s and its line, the lagging game's line, the stall's line, the at-speed ride, the settings line, `LaunchTau=0`; 13 with the review's: the game's 110 u/s^2 under 80 not ended as stuck), wall (75, 23 more: the mailbox narrow by its own reference, the car "and the one 80 out too", "another reference", "no reference", the rail at 1.5 radii, the settings lines, the sidestep's start, path, gap, over and side, its three cancels, two "none for", an actor ahead; `WallNarrowSame=0` and `WallNarrowHigh=0`; the review's three: a long face 50 deg off square wide by the far ray, a rail along the path and a car's flank abeam taking that side by the rays across), room (131, 5 more: the truck to the street, `SnapDrop=100`, the settings line and options 63, the most room on the navmesh; `SnapBest=0`), roomold (54, 2 more: the older ESP's 0 of 5 globals, no water trim words), arms (36, 3 more: the settle after first person and the rearm, the use hold through a standing clip at the top, `UseHold=0` with the seat watch's 2026-11-02a values), view (103, 21 more: the tip's 15 (the four globals 0 bitwise unchanged, the tip from level once an entry, the probe, already down, the player's own look, the flipped pitch, the camera that doesn't follow, the FOV not found and found, eased and put back on every way out, another writer, the eye globals and their clamps, back to 0 bitwise), the eye log's hysteresis, -1 through the settle, `PoseOffRewrite`; the review's three: no tip back from aiming or VATS, the FOV at the player's own not written, the FOV put back after another writer), look (57, 2 more: `Cull=0` by default, the lamp let go at getting off), sound (100, 5 more: the sixth line, the launch rev, the 2026-11-02a off values' pull, the code's defaults), fx (42, 7 more: the second `[Fx]` line at the start and on getting on, the law at 640 and 300, the churn's trim, the wet road's words, loop 0 untrimmed, the use idle refused at 800 and passed stopped) | 1562 checks ok in 24 modes (full 382, probe 10, guard 8, wrongversion 4, transposed 76, disagree 6, backpush 6, riderinplace 18, riderheldonly 8, load 43, climb 125, wall 75, ram 110, backing 56, arms 36, room 131, roomold 54, decals 77, sound 100, look 57, view 103, fx 42, hits 22, launch 13); 1481 in 23 at the 2026-11-02a build (wall 52, arms 33, room 126, roomold 52, sound 95, look 55, view 82, fx 35 and the rest as now), 1381 in 22 at the 2026-11-01a build (full 381, wall 34, arms 23, roomold 49, decals 67, sound 91, look 53, view 58, fx 29 and the rest as now), 1356 before its review's fixes, 1136 in 18 at the 2026-10-31a build, 1086 in 17 at test 47's build, 1083 before test 47's review fixes, 1041 at test 46's build, 1039 before its review fixes, 984 at test 45's build, 944 before the review's fixes, 884 in 17 after test 44's sound, 830 in 16 after test 43's round, 689 in 15 after test 41's second round, 649 in 14 after test 41's first round, 467 in 9 at test 40, 189 at test 19); in the game: slope limit and camera work (tests 6, 7); test 10: the filter reset and the zoom work, the track pitch much steadier but flipping on turns (fixed), steep-face refusal never fired (fixed); test 11: steep refusal works (12 refusals on faces, none on roads), 6 of 6 parks on the track, steering works but too wide (made speed-dependent), pitch flips down from 18 to 3; test 12: speed-dependent turning right, both steep parks right; the -0.3 written from the task never reached the movement and back drove forward (hence the input hook); test 13: the hook never installed (the handler is a struct, `.?AU`), and getting off was allowed on 47° and 49° faces (limit now 45°); test 14: hook in, timing right, creep works, steep refusal at 61°; a side key stuck while backing (fixed), SetPosition backed up through walls (dropped from auto); test 15: no stuck key, creep on target (made a bit faster), the movement output turned round or at a negative speed doesn't move the player (hence pushDelta, then steps after rays); test 16: pushDelta doesn't move it, the steps after rays back up at 78-82 units/s and stop at cars, fences, rocks and trees, but turning swung the rear into a car (now checked), an invisible volume stopped it on a flat slab (now passed through by layer), and stepping down a steep slope left it in the air (now it lands first); test 17: filter 30 works, the slab's "nothing" was an actor zone (passed through), stops at trees, fences, rocks, no rear clipping; a chain-link fence (layer 26) was passed through (now solid), the bike in the air a third of the time backing downhill (now held on the ground), the creep wound up while stuck (now capped); test 18: stops at fences, barrels, a slab's side and Dogmeat, all named; up a 20-unit slab step and the Vault 111 platform; the creep gets going on rocks within a second and holds; a cut after a snag went too low (bounded now) and the controller said in the air half the time with the feet on the ground (the rays' word now goes for the track and the pitch); test 19: the pitch follows the rays' word in the air, bodies and a tire backed over, three snags each cut within a sample; the game's clear landing after the keys stalled a creep for 3.5 s (the keys are kept 0.2 s now, and the input written again before the movement) |
| Parked bike tilt | `tools/f4se-slope/test/parked_tilt.py`: the script's pitch and roll, put through the game's Euler order (heading last, then pitch and roll in the bike's frame), for 2000 random headings and slopes up to 10° (inside both caps); 2000 parks on a track up to 45° steep and 20° across (the bike's length along the line between its wheels, with the roll capped at 10°); a 60° face at an angle (pitch and roll each at its own cap); an uphill park facing the slope | the bike's up lands on the ground's normal (error 1e-16), its length along the track (2e-15), the 60° face at 45° pitch and 10° roll, nose up uphill; in the game (test 7) the tilt went the right way, the height was wrong (one-frame normal carried 110 units: fixed by parking on the track) |
| API stubs | `tools/syntax-check/audit_stubs.py` against Bethesda's and F4SE's own script sources (F4SE's repository) | no differences (it caught the camera script's nonexistent `GetINIFloat`) |
| Riding clips | `verify_clips.py`: length, frames, control events and root motion identical to each vanilla clip (U-turns: same length, total turn and distance); all 95 bones; unit rotations; 106 clips per set. Hands on the grips exactly (IK), and since test 40 their long axis, the knuckle line, along the forearm seen along the grip (the build prints the most it leaves: 0.1 degrees in the riding and idle poses, up to 1.6 for a frame of the stops and starts); hips on the seat for the male and CBBE bodies | ok |
| Worn bike mesh | posed with the clips and rendered with the skinned body (`preview.py`) | lines up |
| Sketchfab model | `harley_meshes.py` on Nieve5677's glTF: the four nifs read back (twelve shapes each since test 38, 28 since the 2026-10-31a build: the row below, three at first, the vanilla shape hidden in the parked one with its 18 collision blocks kept, textures and alpha on the right shapes, the skin round trip within 0.01), the palette DDS files read back with Pillow; the rider posed to `CMB_BikeFit.json` and rendered on it (`preview.py --fit`) in the cruise, run, lean and idle poses | hips on the seat behind the tank, hands on the grips with the arms nearly straight, feet on the mid pegs, the left foot down at a stop; the clips rebuilt for it pass `verify_clips.py` as before |
| Bike look (the 2026-10-31a build) | `check_bike_meshes.py` over the built Data tree: 28 shapes a worn nif, 25 parked (the two under-bar mirrors hidden) beside the hidden vanilla shape, at most 60,000 vertices each, the names and their tags, every material file read back by PyNifly's own reader and compared with the nif block, every texture there with its format and full mips, the UVs in 0..1, the overlays' gaps in the nifs' half floats, the needle's sphere on its pivot and its rest on the 0 mark, the mirrors' gap to the tank at either lock, no 0x100 or 0x8000 flag, smoothness at most 1, no root material, `CMB_BikeParts.ini`'s 27c keys and `CMB_BikeFit.json` byte for byte 27c's, no brand word in any byte; the texture stage's normals through a nif written and read back; `look_render.py`'s renders of 27c's bike and this one, view by view (*The bike's look*) | every check passes (230,363 vertices, 230,815 triangles, 85.3 MB of DDS); the normals' round trip 0.39 degrees RMS (the bar 2); 27c's bike and this one rendered with the same settings (the five sets, the dial close up, the lights again under the per-channel Standard view, a before/after sheet) and looked at against the plan's list: the chrome dark with the cube in it, no flat white; the paint glossy with its reflection and coachline; no seam or smear at 1280 x 800; the dial legible with the needle on 0 and on 50, and lit at night with the backlight; the brake deep red and plainly brighter than the tail by day and at night (its rear signals light too); every mirror a sky-to-ground gradient (the under-bar ones mostly ground with a band of sky at the top); both under-bar mirrors clear of the tank at full lock; no brand mark. Fixed on the way: the renderer's sparkle on the paint (the denoiser's prefilter), the exhaust's patchy reflections (its own normals) and the discs' moire (no grooves) |
| Bike look (the 2026-11-01a build) | `check_bike_meshes.py` over the built Data tree with the stage's manifest (`--stage-dir`): 30 shapes a worn nif and 27 parked beside the hidden vanilla shape; the view nif `CMB_BikeView.nif`'s 30, unskinned, no skin or collision block, under the node `CMB_BikeView` hidden by its flag bit 0, its vertices the parked nif's turned into the bike's space (the bar 1e-4) and the worn nif's within their half floats, the worn materials; the volume guard's closed pieces (the bar 0.6 of a piece's volume); our discs against the model's plates (within 0.05 in x and outer radius); the mirror glass's mean in its `_d` (90-140 sRGB); the budget (93 files, 89 MB); 57 material files read back; `CMB_BikeParts.ini`'s keys and `CMB_BikeFit.json` byte for byte the 2026-10-31a build's; the off values (`--volume-guard 0 --disc model` and that build's materials) rebuilding its nifs byte for byte; harness mode look 53 | every check passes (237,171 vertices and 238,831 triangles a worn nif, `static_black` 48,658 vertices under the guard's 55,000 cap; 88.6 MB of DDS in 93 files); the view nif's vertices 0.000008 off the parked nif's turned round and 0.031 off the worn nif's; 182 closed pieces cut, the least keeping 0.62; the discs' x ranges the plates' and their outer radii 13.730 and 12.559 against 13.727 and 12.554; the mirror glass 113 in all three; the new checks fail on the 2026-10-31a build's tree (no view nif, the glass 9, the least volume 0.21); before and after renders looked at: the coachline straight and even with a round turn at its rear end, a bead along the seat's seam, the discs round and drilled, the mirrors a silvered sky by day |
| Bike look (the 2026-11-02a build) | `check_bike_meshes.py` over the built tree with the stage's manifest and the 2026-11-01a build's tree as the look reference (`--look-reference`); `--disc-bore bolts` with 2026-11-01a's `bike_materials.json` from a copy of its stage; `guard_optional.py` on the package's Data and the optional folder | 61 PASS, 0 FAIL (57 PASS and 4 FAIL on the 2026-11-01a build's own tree: the mirrors' 6 materials on the game's cube at env 2, the chrome's 8 at env 6, spec 2, SSR on, the bore at 0.142 of the outer radius (front 1.9492 of 13.727, rear 1.7827 of 12.554), the face ring from the bore out the carrier's colour (9 off; 40 in 2026-11-01a)); the chrome's 12 textures 2026-11-01a's within the bake's occlusion change (0.4 to 1.1% of the texels, at most 19 levels; a BC5 reader, equal to texture2ddecoder's); the bolts rebuild 157 of 157 files byte-identical to 2026-11-01a's; the guard refuses 2026-11-01a's package (its 2026-10-31a look folder's `CMB_BikeFit.json`) and passes the new folder (40 files); renders looked at: the chrome polished and silvery, nothing blown to white in the preview's light |
| Bike look (the 2026-11-06a build) | `check_bike_meshes.py` over the built tree with the stage's manifest and the 2026-11-02a build's tree as the look reference (`--look-reference`: the chrome's and the wheels' 21 maps byte-identical to it), the chrome's four materials at env 2.5, specular 1.5, SSR off and the eight wheel materials at env 0.25, specular 0.75; the 155 files against 2026-11-02a's: 21 differ (16 BGSM, 5 nifs), every DDS, `CMB_BikeParts.ini` and `CMB_BikeFit.json` byte-identical; `guard_optional.py` on the new Data and the optional folder | 62 PASS, 0 FAIL (60 PASS and 2 FAIL on the 2026-11-02a build's tree: the two look checks); the folder "2026-11-02a look (A-B)" 21 files, 43,471,117 bytes, each equal to the 2026-11-02a package's; the guard "Data and 1 optional folder(s) (21 file(s)) ok" |
| Bike on COM | the skin read back and posed at the seated `COM` transform lands on the model (0.0000); posed through all walk/run/turn/idle clips of both sets next to the `AnimObjectA` bike | apart by at most the bounce: 0.35 units (5 mm, sprinting) |
| Head-tracking default | `bAllowHeadTracking`'s initial value read from `MTBehavior.hkx`'s variable set | 1 (on) |
| Script data (VMAD) | independent decoder: every property, alias -1 on object properties, alias script on the Player alias | ok |
| Vanilla form IDs | Mutagen's FormKey list generated from the real `Fallout4.esm` | all match |
| Plugin properties vs scripts | `check_plugin.py`: names, record types, Mandatory properties | ok |
| Papyrus syntax and types | Caprica against hand-written API stubs | ok |
| Engine functions used | the less common ones checked one by one on the Fallout 4 CK wiki (input layers, teleport events, `GetSitState`, `GetPlayerFollowers`, `CallFunction`, inventory filters, `ChangeAnimFlavor`, `IsPluginInstalled`, `Sound.SetInstanceVolume`/`StopInstance`, F4SE's `GetWornItem`…); the rest are core functions vanilla scripts use everywhere. `EnableSprinting` confirmed present in the target game version | ok |

**Not verified:** anything only the game can show. That covers whether it loads, the speed feel, whether the subgraph entries win the way the documentation describes, the Creation Kit animation-data step, companion hiding, opening the bag remotely, and save/load behaviour; since the 2026-10-31a build also the bike's look in
the game's own light and tone mapping, whether the shapes' names reach the plugin, which way up the game reads the
mirrors' cube, whether it dims cube reflections at night, and the shapes' cost in frame time (28 at the 2026-10-31a
build, 30 since 2026-11-01a, and the first-person bike's second set); since the 2026-11-02a build also whether
`CMB_RiderSteadyPerk2` stops power attacks' staggers, whether `Spell.Cast` of the kill spell gives the game's
experience, whether Immersive Animation Framework's camera is freed by the use window, the sound records' loudness in
game, the chrome's brightness and the game cube in the mirrors; since the 2026-11-06a build also whether the
riding camera's turn reads as the mouse and lets every sidestep go, whether Sanctuary's mailboxes have a reference of
their own, the game's low end at a launch (about 110 u/s^2 under 80 u/s in test 49), whether the item animation mod's
`PlayIdle` reaches the graph slot the plugin refuses (and whether Jet's effect comes with its clip refused), F4SE's
`GetFavorites` on 1.11.240, whether the camera follows the look pitch at `+0xC0` and the world FOV's field, the
jump-down splash's path (Q-W2), the wet road's level against the engine, and the toned-down chrome.
