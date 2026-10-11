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
                                              ◄ Dismount / interior / power armor / furniture /
                                                deep water / an enemy's hit (optional)
```

- **Keys:** handed out the first time the player is outdoors with a Pip-Boy, so a new game's pre-war intro and Vault 111 are left alone. The player keeps two keys, so using one never empties the stack (an empty stack would lose its favorites hotkey).
- **Parked bike:** a persistent Activator reference. It lives in a holding cell until first called, then wherever you leave it.
- **While riding:** the parked reference is disabled and moved next to the player every second. If you go indoors, the bike is simply re-enabled where you last were outside.
- **Deep water:** the controller gives the player a hidden ability, `CMB_SwimWatchAbility`, whose effect has the condition `IsSwimming == 1`, so it starts when the player starts swimming and ends when they stop (`CMB_SwimWatchEffectScript` reports both). Swimming ends the ride with "The motorbike can't go into deep water." The bike stays hidden until you're out of the water altogether: a second effect on the same ability, with `IsInWater == 1` (any depth, wading too), reports that. Three seconds after you're on dry land the bike rolls up 200 units past you, on the side away from where you stopped swimming, which is the land side (indoors it waits until you're outside; if the in-water report never ends, it comes after 30 s anyway). Crossing a river can end the ride several times; that's by design. Leaving it where it last followed you didn't work: after riding off a ledge into a lake, that spot was in mid-air, and Papyrus can't tell whether the player is on the ground. Getting on and calling the bike are refused while swimming. Paddling-depth water isn't swimming, so it stays rideable. The ability is added on every load (adding it again does nothing).
- **Falls:** `FallingDamageMod` (the actor value the Acrobat's legendary effect raises: percent less fall damage) goes up by `CMB_FallDamageCut` (default 75) while riding, and exactly that comes off again. A no-fall-damage perk (`crNoFallDamage`) would be all or nothing, so the actor value it is. On top of that, small falls are free: the controller registers for the player's `OnPlayerFallLongDistance` event (as a remote event) and, while riding, logs every fall's damage and gives it straight back (`RestoreValue`, a moment after it lands) when it's under `CMB_FreeFallDamage` percent of max health (default 20). Ordinary drops cost nothing; a cliff still hurts. The Vault 111 cliff took about 42% with the 75% cut. Landings use the seated jump clips.
- **Fights:** with `CMB_DismountOnHit` (default 1) the controller registers for hit events on the player (one-shot, re-registered after each). A big hit from an actor hostile to the player ends the ride and parks the bike beside them: a power attack, an explosion, or at least `CMB_KnockOffDamage` percent of max health (default 10) lost since the last tick, so a quick run of small hits adds up. Health is read as a fraction of the maximum (`GetValuePercentage`), a moment after the hit lands. Hits in the first 3 seconds after getting on never count. A bloatfly's sting doesn't knock you off; a raider's shotgun blast at close range does. Otherwise, the first tick of a fight (`IsInCombat`) with weapons off shows a hint once: use the keys to get off.
- **Speed:** `ModValue(SpeedMult, delta)` with the exact delta remembered and removed later, so other speed effects stay intact. A ±0.1 carry-weight nudge forces the engine to apply the new speed (a known SpeedMult quirk).
- **Companions:** mode 0 (default) gives them the same speed boost and moves them up behind you if they fall behind. Mode 1 (opt-in) disables them and parks them in the holding cell, then puts them back behind you on dismount. That's riskier: disabling a companion during their quest or a scene (Heather, Dogmeat, Sim Settlements 2 characters…) can break it. So companions in a scene or in power armor are never hidden or teleported, whatever the mode.
- **Fuel:** every tick, the horizontal distance since the last tick is added up (jumps over 5000 units are teleports and don't count). Every `CMB_FuelDistance` units (default 21000, about 300 m) one item from `CMB_FuelItems` is used, from the side bag first, then the player. The list holds Flamer Fuel by default. Running dry parks the bike where you stand; with no fuel you can't get on. Fast travel costs nothing, and Survival disables it anyway.
- **Worn bike slot:** biped slot 57. Whatever else is worn in that slot comes off while riding. With F4SE, `CMB_GearRestoreF4SE` reads it first (`GetWornItem`) and re-equips it after the ride; vanilla Papyrus can't read what's in a slot, so without F4SE it stays in the inventory. 58 clashed with Eli's Armour Compendium bags, and 60 is the slot named "Pipboy", so 57 it is.
- **Side bag:** a container in the holding cell, opened remotely with `Activate`. Capacity is checked in `OnItemAdded`. F4SE's `Form.GetWeight()` is called *by name* (`CallFunction`), so F4SE stays optional; without it the cap counts items via `GetItemCount(None)`.
- **Save/load:** a player alias forwards `OnPlayerLoadGame`, and the controller re-applies the input layer, speed refresh and timer.
- **Threading:** Papyrus lets other threads into a script whenever it calls another object, so every entry point claims the `busy` flag *before* its first such call. Keys, hotkey, activation and the ride timer then can't interleave. Key delivery works the same way: `keysDelivered` is set before anything else is called (and cleared again if the player isn't outdoors with a Pip-Boy yet), so OnInit, a teleport and the retry timer arriving together can't hand the keys out twice. The ride tick can't claim `busy` (it would block the swim and hit handlers for its whole run), so it checks `riding && !busy` again before each step that changes something: a tick that carried on after the ride ended once put the bike back on after a swim. As a safety net, 1.5 s after every dismount both bike armors come off and head tracking goes back on if you aren't riding again.
- **Riding animations:** while riding, the player gets the animation flavour keyword `CMB_AnimFlavorRider` (`ChangeAnimFlavor`, cleared on dismount and re-applied after a load). `CMB_RiderPose.esp` adds an additive race whose subgraph entries are copies of every third-person holstered entry for the player (from `HumanRaceSubGraphData` and every additive race in the load order, the Unofficial Patch's crippled-limb ones included), each with that keyword added and `MT\CMB_Rider` searched first. The game picks the entry matching the most keywords, so each copy beats its original while the keyword is on. HumanRace isn't edited, so race mods (LooksMenu Customization Compendium and the like) don't conflict. The plugin and its AnimTextData are built on the player's PC from their load order, so the controller finds the plugin with `Game.IsPluginInstalled` and gets the keyword with `GetFormFromFile`. The clips copy the vanilla clip each one replaces (in the player's own folder order: Player, Confident, Neutral) for length, root motion and events, so the game's movement logic doesn't change. The worn bike leans with the rider in turns. Details: [ASSETS.md](ASSETS.md).
- **Bike and rider stay together:** the player's movement graph (`MTBehavior.hkx`) has a `BSRootTwistModifier` whose `rootTwistAngle` is bound to the graph's `Direction` variable. When the character turns on the spot or faces someone in dialogue, it twists the body away from the root. A bike on `AnimObjectA`, a bone under the root on the ground, stays put while the rider turns on it, and the hands leave the grips. So the bike now hangs off `COM`, the bone the whole body hangs from, at the exact transform `COM` has in the seated clips (`CMB_RiderSeat.json`, per sex). In the clips it sits exactly where the `AnimObjectA` bike did (within the few millimetres of suspension bounce), and when the game twists the body, the bike turns with it. That only lines up with the seated pose, so the controller switches to the ground-planted `AnimObjectA` version (`CMB_BikeRiderArmorFrame`) without the rider pose, with a weapon drawn (standing poses) or with `CMB_BikeFollowsRider 0`. Head tracking (`bAllowHeadTracking`, on by default in the graph) twists the chest towards whoever you look at, so it's switched off while seated and back on afterwards.
- **U-turns:** vanilla's 180° reversals (`walk_to_walk_l180` etc.) brake to a stop, spin round and set off the other way. The riding versions keep vanilla's length, events, total turn and distance, but follow a leaning arc at an even pace, with the heading round by vanilla's `startAllowRotation` event, when the game's own steering takes over. The turn direction comes from each source clip's yaw (`MT\Neutral\walk_to_walk_l180` actually turns right).
- **Parked bike facing:** the vanilla motorcycle model points along −Y, so the parked bike is placed with a 180° yaw on top of the player's heading.
- **Engine sound:** a start sound, then two looping sounds (idle ~900 rpm, cruise ~2700 rpm) played on the player and crossfaded every tick by the distance covered since the last one (`Sound.SetInstanceVolume`); a stop sound on dismount. The loops are restarted after a load, since sound instances don't survive one. The audio is synthesised (`tools/sound`), a 45° V-twin firing pattern, so nothing is sampled from anywhere.
- **MCM:** `config.json`/`keybinds.json` bind the menu straight to the globals (`GlobalValue` sources), plus buttons and an MCM hotkey that call the controller. The generator writes them, so their form IDs always match the plugin.
- **Hotkeys:** without F4SE, favorite the keys (an aid item) and use the favorites hotkey. With F4SE, `CMB_HotkeyF4SE` adds a real key. The controller finds it with `CastAs` by name, so the core scripts don't depend on F4SE.

## Engine limits to keep in mind

- **Speed ceiling:** the world streams in cells around you. Much past ~3× run speed, LOD pop-in and load stutter get bad, so the script clamps at 5×.
- **No physics:** no momentum, no ramps; the lean in turns is animation only. The "bike" moves exactly like a fast person: it climbs what a person can climb and is stopped by what stops a person.
- **Collision:** while riding, your collision is still a person-sized capsule.
- **Placement:** the parked bike is placed at your height, to your right. On slopes or next to walls it can float or clip; calling it again (keys → Call) re-places it.
- **Slopes:** how steep a slope you can climb is the character controller's maximum slope, which is native engine data: Papyrus can't change it for one actor. Two ways around it: a small F4SE plugin that raises the player's controller slope limit while riding (native code, built and tested against each game version through the Address Library), or a script that, while riding and stuck, nudges the player forward and up. The nudge means moving the player by script every fraction of a second, which fights the physics and can push you into geometry; not worth it. The plugin is the right way, but it's a separate piece of work that needs testing on the real game.
- **Bike on slopes:** the worn bike can roll and lean (animation), but it can't pitch to follow the ground: animations don't know the ground's angle. Same limit as the wheels below.
- **Camera:** the third-person camera distance is the player's (mouse wheel / zoom), and near trees the camera's collision pushes it in. Neither Papyrus nor F4SE 0.7.9 has a camera-distance function, and F4SE's `Utility.SetINIFloat` is debug-only. The settings are `[Camera]` values held by the game (`fVanityModeMaxDist`/`fVanityModeMinDist`, the mouse-wheel zoom limits, `fOverShoulderPosX`/`PosZ`, `fPitchZoomOutMaxDist`); the horse and vertibird variants only apply to real mounts. Setting them while riding and putting them back afterwards belongs in the same small F4SE plugin as the slope limit.
- **Rider pose check:** once, getting on straight out of the water, the seated clips took about 13 s to appear. The seated clips have no footsteps and the standing ones do, so while riding the controller listens for the `FootLeft` animation event: footsteps while the rider pose should be on mean the switch hasn't happened, and it applies the flavour and `AttemptAnimationSetSwitch` again, every 2 s, up to 10 times per ride, logging each try. Applying it clears the flavour first, so it counts as a change even when a save already carried it. After loading a save mid-ride it's applied 1 s after the game is running rather than straight from `OnPlayerLoadGame`: right at load, `ChangeAnimFlavor` was refused once and only the footstep check (12 s later) fixed it. The footstep registration fails while the player's 3D isn't loaded, so the ride tick retries it.
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
| Standing clips with the bike on `COM` | Any clip without a seated version (stagger, for one) shows a standing pose, and the bike follows it. The jump, fall and land clips are seated; without them (not extracted, ASSETS.md) a bump at speed swings the bike sideways. `set CMB_BikeFollowsRider to 0` avoids it |
| Engine sound silent | The sound file path format (`FX\CMB\...`, relative to `Data\Sound`) couldn't be checked against a vanilla record here. If it's silent, that's the first suspect |
| MCM hotkey and the built-in F4SE hotkey on the same key | Toggles twice. The MCM help text says to set the built-in one to 0 |

## Not doable: spinning wheels

Only `Root` and `COM` can move in Fallout 4 animations; every other bone keeps its fixed offset from its parent and can
only rotate. A wheel can only spin around a bone's own pivot, so it would need a bone sitting on each axle, about
70 units from the character's origin. The skeleton has none that can get there: the only free-standing bones under
`Root` are the camera bones at 120 units, and the weapon bones hang off the hand a few units away. The options left are a
custom `skeleton.hkx` with wheel bones (it would have to be merged with every other skeleton mod, Combined Arms
included) or a scrolling-texture wheel (always spinning, even standing still). Neither is worth it for now.

## What has been verified without the game

| Check | How | Result |
|---|---|---|
| Plugin file structure | independent byte-level parser (group/record/subrecord sizes) | ok |
| Record layouts | compared field by field with xEdit's `wbDefinitionsFO4.pas` (MGEF, QUST VMAD, GLOB, KYWD, MESG, ALCH, ARMO, ARMA) | match after fixing GLOB `FNAM` and KYWD `CNAM` |
| Sound records | byte layout compared with xEdit's SNDR definition (descriptor type, loop flag, priority) | ok |
| Engine sounds | loops checked for seamless wrap-around; waveform and spectrogram inspected | ok; how they *sound* is untested |
| Rider-pose plugin builder | run on a stand-in load order (Mutagen-built `Fallout4.esm` with the player's real folder lists, recovered from the AnimTextData IDs, plus an Unofficial-Patch-like additive race with its own keyword), output read back with Mutagen | right entries copied, extra master added, keywords remapped, AnimTextData found for every entry and written |
| AnimTextData | ID formula reproduces all 8 files of a Creation Kit-built mod and 110 vanilla IDs; all 109 reference files parse and re-write byte for byte; folder search order matches all 193 male / 191 female resolved clips | ok |
| Compiled scripts | Caprica, Fallout 4 target: header v3.9, game 2, for all 8 scripts | ok; not yet loaded in game |
| Riding clips | `verify_clips.py`: length, frames, control events and root motion identical to each vanilla clip (U-turns: same length, total turn and distance); all 95 bones; unit rotations; 106 clips per set. Hands on the grips exactly (IK); hips on the seat for the male and CBBE bodies | ok |
| Worn bike mesh | posed with the clips and rendered with the skinned body (`preview.py`) | lines up |
| Bike on COM | the skin read back and posed at the seated `COM` transform lands on the model (0.0000); posed through all walk/run/turn/idle clips of both sets next to the `AnimObjectA` bike | apart by at most the bounce: 0.35 units (5 mm, sprinting) |
| Head-tracking default | `bAllowHeadTracking`'s initial value read from `MTBehavior.hkx`'s variable set | 1 (on) |
| Script data (VMAD) | independent decoder: every property, alias -1 on object properties, alias script on the Player alias | ok |
| Vanilla form IDs | Mutagen's FormKey list generated from the real `Fallout4.esm` | all match |
| Plugin properties vs scripts | `check_plugin.py`: names, record types, Mandatory properties | ok |
| Papyrus syntax and types | Caprica against hand-written API stubs | ok |
| Engine functions used | the less common ones checked one by one on the Fallout 4 CK wiki (input layers, teleport events, `GetSitState`, `GetPlayerFollowers`, `CallFunction`, inventory filters, `ChangeAnimFlavor`, `IsPluginInstalled`, `Sound.SetInstanceVolume`/`StopInstance`, F4SE's `GetWornItem`…); the rest are core functions vanilla scripts use everywhere. `EnableSprinting` confirmed present in the target game version | ok |

**Not verified:** anything only the game can show. That covers whether it loads, the speed feel, whether the subgraph entries win the way the documentation describes, the Creation Kit animation-data step, companion hiding, opening the bag remotely, and save/load behaviour.
