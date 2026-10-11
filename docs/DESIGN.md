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
                                              ◄ Dismount / interior / power armor / furniture
```

- **Keys:** handed out the first time the player is outdoors with a Pip-Boy, so a new game's pre-war intro and Vault 111 are left alone. The player keeps two keys, so using one never empties the stack (an empty stack would lose its favorites hotkey).
- **Parked bike:** a persistent Activator reference. It lives in a holding cell until first called, then wherever you leave it.
- **While riding:** the parked reference is disabled and moved next to the player every second. If you go indoors, the bike is simply re-enabled where you last were outside.
- **Speed:** `ModValue(SpeedMult, delta)` with the exact delta remembered and removed later, so other speed effects stay intact. A ±0.1 carry-weight nudge forces the engine to apply the new speed (a known SpeedMult quirk).
- **Companions:** mode 0 (default) gives them the same speed boost and moves them up behind you if they fall behind. Mode 1 (opt-in) disables them and parks them in the holding cell, then puts them back behind you on dismount. That's riskier: disabling a companion during their quest or a scene (Heather, Dogmeat, Sim Settlements 2 characters…) can break it. So companions in a scene or in power armor are never hidden or teleported, whatever the mode.
- **Fuel:** every tick, the horizontal distance since the last tick is added up (jumps over 5000 units are teleports and don't count). Every `CMB_FuelDistance` units (default 21000, about 300 m) one item from `CMB_FuelItems` is used, from the side bag first, then the player. The list holds Flamer Fuel by default. Running dry parks the bike where you stand; with no fuel you can't get on. Fast travel costs nothing, and Survival disables it anyway.
- **Worn bike slot:** biped slot 57. Whatever else is worn in that slot comes off while riding. With F4SE, `CMB_GearRestoreF4SE` reads it first (`GetWornItem`) and re-equips it after the ride; vanilla Papyrus can't read what's in a slot, so without F4SE it stays in the inventory. 58 clashed with Eli's Armour Compendium bags, and 60 is the slot named "Pipboy", so 57 it is.
- **Side bag:** a container in the holding cell, opened remotely with `Activate`. Capacity is checked in `OnItemAdded`. F4SE's `Form.GetWeight()` is called *by name* (`CallFunction`), so F4SE stays optional; without it the cap counts items via `GetItemCount(None)`.
- **Save/load:** a player alias forwards `OnPlayerLoadGame`, and the controller re-applies the input layer, speed refresh and timer.
- **Threading:** Papyrus lets other threads into a script whenever it calls another object, so every entry point claims the `busy` flag *before* its first such call. Keys, hotkey, activation and the ride timer then can't interleave.
- **Riding animations:** while riding, the player gets the animation flavour keyword `CMB_AnimFlavorRider` (`ChangeAnimFlavor`, cleared on dismount and re-applied after a load). `CMB_RiderPose.esm` adds an additive race whose subgraph entries need that keyword and search `MT\CMB_Rider\` before the player's usual folders, the way the DLCs add their animations. HumanRace isn't edited, so race mods (LooksMenu Customization Compendium and the like) don't conflict. The plugin is built on the player's PC from their `Fallout4.esm`, so the controller finds it with `Game.IsPluginInstalled` and gets the keyword with `GetFormFromFile`. The clips are generated from the vanilla holstered clips with the same names, lengths, root motion and events, so the game's movement logic doesn't change. The worn bike is skinned to `AnimObjectA`, so the clips also lean the bike in turns. Details: [ASSETS.md](ASSETS.md).
- **Parked bike facing:** the vanilla motorcycle model points along −Y, so the parked bike is placed with a 180° yaw on top of the player's heading.
- **Engine sound:** a start sound, then two looping sounds (idle ~900 rpm, cruise ~2700 rpm) played on the player and crossfaded every tick by the distance covered since the last one (`Sound.SetInstanceVolume`); a stop sound on dismount. The loops are restarted after a load, since sound instances don't survive one. The audio is synthesised (`tools/sound`), a 45° V-twin firing pattern, so nothing is sampled from anywhere.
- **MCM:** `config.json`/`keybinds.json` bind the menu straight to the globals (`GlobalValue` sources), plus buttons and an MCM hotkey that call the controller. The generator writes them, so their form IDs always match the plugin.
- **Hotkeys:** without F4SE, favorite the keys (an aid item) and use the favorites hotkey. With F4SE, `CMB_HotkeyF4SE` adds a real key. The controller finds it with `CastAs` by name, so the core scripts don't depend on F4SE.

## Engine limits to keep in mind

- **Speed ceiling:** the world streams in cells around you. Much past ~3× run speed, LOD pop-in and load stutter get bad, so the script clamps at 5×.
- **No physics:** no momentum, no ramps; the lean in turns is animation only. The "bike" moves exactly like a fast person: it climbs what a person can climb and is stopped by what stops a person.
- **Collision:** while riding, your collision is still a person-sized capsule.
- **Placement:** the parked bike is placed at your height, to your right. On slopes or next to walls it can float or clip; calling it again (keys → Call) re-places it.

## Known risks

| Risk | Mitigation |
|---|---|
| Another mod's gear in slot 57 comes off while riding | Check with FO4Edit, change `BikeSlot` in the generator (see BUILD_GUIDE) |
| Hiding a companion during their own quest or a scene | Run-alongside is the default; even in ride-along mode, companions in a scene are left alone |
| The seated clips don't play | They need `CMB_RiderPose.esm` and regenerated animation data (`generate_anim_info.bat`); without them the rider runs in place over the bike, which is harmless |
| `-GenerateAnimInfo` broken in the user's Creation Kit build | Reported for some next-gen CK updates. Fallback: write the `AnimTextData` entries directly, which needs vanilla samples of that format |
| Remote `Activate` of the bag container doesn't open the menu | Fallback: move the container next to the bike when opening it (small script change) |
| Rider pose breaks animations | A flavour keyword only adds entries that need it, nothing else changes; `set CMB_UseRiderPose to 0`, untick `CMB_RiderPose.esm`, or `player.caf` (clear flavour) |
| Uninstalling mid-ride | Documented: dismount or reset first |
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
| Rider-pose plugin builder | run on a stand-in `Fallout4.esm` (Mutagen-built, with player/female/1st-person/weapon/NPC entries), output read back with Mutagen | right entries copied, keywords and paths as intended, target keywords kept |
| Riding clips | `verify_clips.py`: length, frames, control events and root motion identical to each vanilla clip; all 95 bones; unit rotations. Hands on the grips exactly (IK); hips on the seat for the male and CBBE bodies | ok |
| Worn bike mesh | posed with the clips and rendered with the skinned body (`preview.py`) | lines up |
| Script data (VMAD) | independent decoder: every property, alias -1 on object properties, alias script on the Player alias | ok |
| Vanilla form IDs | Mutagen's FormKey list generated from the real `Fallout4.esm` | all match |
| Plugin properties vs scripts | `check_plugin.py`: names, record types, Mandatory properties | ok |
| Papyrus syntax and types | Caprica against hand-written API stubs | ok |
| Engine functions used | the less common ones checked one by one on the Fallout 4 CK wiki (input layers, teleport events, `GetSitState`, `GetPlayerFollowers`, `CallFunction`, inventory filters, `ChangeAnimFlavor`, `IsPluginInstalled`, `Sound.SetInstanceVolume`/`StopInstance`, F4SE's `GetWornItem`…); the rest are core functions vanilla scripts use everywhere. `EnableSprinting` confirmed present in the target game version | ok |

**Not verified:** anything only the game can show. That covers whether it loads, the speed feel, whether the subgraph entries win the way the documentation describes, the Creation Kit animation-data step, companion hiding, opening the bag remotely, and save/load behaviour.
