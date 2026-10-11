# Build guide (Creation Kit)

This guide turns the scripts in `Scripts/Source/User/` into a working plugin,
`CommonwealthMotorbike.esp`. Expect 1–2 hours the first time. Every EditorID
starts with `CMB_` so you can find the mod's records by filtering on that.

Do the steps in order: properties can only be filled once the records they
point to exist.

## 0. Prerequisites

| What | Why | Where |
|---|---|---|
| Fallout 4 (PC) | - | Steam / GOG / Xbox PC |
| **Creation Kit for Fallout 4** | builds the plugin and compiles Papyrus | Steam → Library → Tools → "Fallout 4: Creation Kit" |
| Script sources | the compiler needs them | the CK ships `Data\Scripts\Source\Base\Base.zip`. Unzip it into `Data\Scripts\Source\Base\` if the CK hasn't already |
| F4SE (optional) | hotkey + weight-based side bag | f4se.silverlock.org. For the hotkey script you also need F4SE's script sources (`Data\Scripts\Source\F4SE` or merged into `Base`) |
| Outfit Studio (BodySlide) + NifSkope | turns the motorcycle into a wearable mesh | Nexus, see [ASSETS.md](ASSETS.md) |
| Archive2 | extracts vanilla meshes | ships with the CK in `Tools\Archive2\` |

## 1. Copy the scripts

Copy every `.psc` from `Scripts/Source/User/` into
`<Fallout 4>\Data\Scripts\Source\User\`.

Skip `CMB_HotkeyF4SE.psc` if you don't use F4SE. It won't compile without F4SE's sources, and nothing else depends on it.

## 2. Create the plugin

1. Start the CK, `File → Data…`, tick only `Fallout4.esm`, click OK.
2. Save right away as `CommonwealthMotorbike.esp`.

## 3. Globals (console-tweakable settings)

`Miscellaneous → Global → New`. Make every global **Float**, *not* Constant:

| EditorID | Value | Meaning |
|---|---|---|
| `CMB_SpeedPercent` | 250 | riding speed in % of the rider's current speed (script clamps to 100–500) |
| `CMB_CompanionMode` | 1 | 1 = companions ride along (hidden while riding), 0 = they run alongside with the same speed boost |
| `CMB_AllowCombat` | 0 | 1 = weapons and VATS stay usable while riding |
| `CMB_ForceThirdPerson` | 1 | switch to 3rd person when getting on |
| `CMB_UseRiderPose` | 0 | 1 = use the experimental seated animation set ([ASSETS.md](ASSETS.md#stage-2-experimental-seated-rider-pose)) |
| `CMB_CatchUpDistance` | 2500 | runners further than this (units) get moved up behind you; 0 = off |
| `CMB_BagCapacity` | 60 | side bag limit: lbs with F4SE, item count without; 0 = unlimited |
| `CMB_HotkeyCode` | 48 | F4SE hotkey, DirectX scan code (48 = B) |

## 4. Messages

`Miscellaneous → Message → New`. Tick **Message Box** for both. Button order matters, because the scripts read the button index.

**`CMB_ParkedMenu`**: title `Motorbike`, text `What do you want to do?`
Buttons: `Ride`, `Open side bag`, `Cancel`

**`CMB_KeysMenu`**: title `Motorbike`, text `Your motorbike isn't nearby.`
Buttons: `Call it here`, `Open side bag`, `Cancel`

## 5. Keys (aid item + effect)

1. **Magic effect** `CMB_BikeKeysEffect` (`Magic → Magic Effect → New`):
   - Effect Archetype: **Script**, Casting Type: **Fire and Forget**, Delivery: **Self**
   - Flags: *No Duration*, *No Magnitude*, *No Area*, *Painless*, and *Hide in UI* if your CK shows it
   - Papyrus Scripts → Add → `CMB_KeysEffectScript`.
     Fill the property `Controller` later (step 9), because the quest doesn't exist yet.
2. **Aid item** `CMB_BikeKeys` (`Items → Potion → New`):
   - Name `Motorbike Keys`, Weight 0, Value 0
   - Model: copy the model path from any vanilla key (`Items → Key`, open one, copy the model path)
   - Not Food/Medicine, no addiction
   - Effects: add `CMB_BikeKeysEffect`, magnitude 0, duration 0
   - Leave the "consume" sound empty, or pick a quiet one
3. *(optional)* **Recipe** `CMB_co_BikeKeys` (`Items → Constructible Object → New`) in case
   the keys are ever lost:
   - Created Object `CMB_BikeKeys`, count 2, workbench keyword `WorkbenchChemlab`, components e.g. 1 Steel + 1 Copper

The mod hands out the keys automatically, and tops you back up to two whenever one is used. Two keys means the stack never runs out, so a favorites hotkey bound to them keeps working.

## 6. The worn bike (armor)

You need the converted mesh from [ASSETS.md](ASSETS.md#stage-1-the-worn-bike-mesh) first.

1. **Armor Addon** `CMB_BikeRiderAA` (`Items → ArmorAddon → New`):
   - Race: `HumanRace`
   - Biped slot: **58** (an "unnamed" slot; pick another unnamed slot if one of your mods uses it)
   - Male & Female world model: `CMB\CMB_BikeWorn.nif`
   - No first-person model
2. **Armor** `CMB_BikeRiderArmor` (`Items → Armor → New`):
   - Name `Motorbike`, untick **Playable** (flag *Non-Playable*), so it never shows in your inventory
   - Biped slot 58 (the same slot as the addon), Armor Addons: `CMB_BikeRiderAA`
   - Weight 0, Value 0, Rating 0

## 7. The parked bike and side bag

1. **Activator** `CMB_BikeActivator` (`WorldObjects → Activator → New`):
   - Name `Motorbike`, Activate Text Override `Ride`
   - Model: the **vanilla motorcycle** nif as-is, since this one keeps its collision.
     Find it with the Object Window filter `motorcycle` under `WorldObjects → Static`, open it and copy its model path.
   - Papyrus Scripts → Add → `CMB_BikeActivatorScript`.
     Fill the properties in step 9.
2. **Container** `CMB_SideBagContainer` (`WorldObjects → Container → New`):
   - Name `Side Bag`, any small vanilla model (nobody ever sees it), not respawning
   - Papyrus Scripts → Add → `CMB_SideBagScript`, properties:
     `CMB_BagCapacity` → the global, `PlayerRef` → `PlayerRef` (Cell `(any)`, Ref `PlayerRef ('Player')`)

## 8. Holding cell

1. `World → Cell View`, pick Interiors, then `File → New Cell`: EditorID **`CMB_HoldingCell`** (no lighting template needed).
2. Drag into it from the Object Window:
   - `CMB_BikeActivator` → double-click the reference, Reference EditorID **`CMB_BikeRef`**, tick **Persistent**
   - `CMB_SideBagContainer` → Reference EditorID **`CMB_SideBagRef`**, tick **Persistent**
   - `XMarker` (`WorldObjects → Static → XMarker`) → Reference EditorID **`CMB_HoldingMarkerRef`**, tick **Persistent**

The bike starts out in this cell. In game you call it over with the keys the first time.

## 9. Controller quest

1. `Character → Quest → New`, ID **`CMB_ControllerQuest`**, name `Commonwealth Motorbike`
   - Tick **Start Game Enabled**; untick *Run Once*. Priority 50 is fine.
   - Click OK, then reopen it so the other tabs work.
2. **Quest Aliases** tab → right-click → New Reference Alias:
   - Name `Player`, **Specific Reference**: Cell `(any)`, Ref `PlayerRef ('Player')`
   - Alias Scripts → Add → `CMB_PlayerAliasScript` (no properties)
3. **Scripts** tab → Add → `CMB_ControllerScript`. Fill the properties. Every *Mandatory* one must be set:

   | Property | Value |
   |---|---|
   | `PlayerRef` | Cell `(any)`, Ref `PlayerRef ('Player')` (try **Auto-Fill All** first) |
   | `BikeRef` | Cell `CMB_HoldingCell`, Ref `CMB_BikeRef` |
   | `SideBagRef` | `CMB_SideBagRef` |
   | `HoldingMarkerRef` | `CMB_HoldingMarkerRef` |
   | `CMB_BikeRiderArmor`, `CMB_BikeKeys`, `CMB_KeysMenu` | the records with those names |
   | `SpeedMult`, `CarryWeight` | the vanilla actor values (Auto-Fill finds them) |
   | all `CMB_*` globals | the matching globals |
   | `AnimArchetypePlayer` | vanilla keyword `AnimArchetypePlayer` (0006B508), needed only for the rider pose |
   | `CMB_AnimArchetypeRider` | only for the rider pose, see ASSETS.md |
   | `CMB_EngineStartSound` / `CMB_EngineStopSound` | optional, any vanilla sound descriptor you like |

4. *(F4SE only)* Scripts tab → Add → `CMB_HotkeyF4SE`: `Controller` → `CMB_ControllerQuest`, `CMB_HotkeyCode` → the global.
5. Now go back and fill the remaining properties:
   - `CMB_BikeKeysEffect` → `CMB_KeysEffectScript.Controller` = `CMB_ControllerQuest`
   - `CMB_BikeActivator` → `CMB_BikeActivatorScript.Controller` = `CMB_ControllerQuest`, `CMB_ParkedMenu` = the message

## 10. Compile and save

- The CK compiles a script when you add it or edit it (`Gameplay → Papyrus Script Manager`, right-click → Compile).
  If anything fails, copy the full error text from the CK's output window. That's the most useful thing you can send back.
- **Possible compile issue:** `EnableSprinting` on `InputEnableLayer` is the one call I couldn't confirm in the
  official docs. If the compiler says it doesn't exist, delete that line from `ApplyControls()` in
  `CMB_ControllerScript.psc`. Sprinting then stays possible while riding, which is harmless but very fast.
- Save. Optionally flag the plugin as ESL (light) in xEdit to save a load-order slot. The mod has very few records, so that's safe.

## 11. Install

Copy into `Data\`:

```
CommonwealthMotorbike.esp
Scripts\CMB_*.pex                (the CK writes these to Data\Scripts\ when compiling)
Meshes\CMB\CMB_BikeWorn.nif
Meshes\Actors\Character\Animations\CMB_Rider\...   (only if you built the rider pose)
```

Enable the plugin in your mod manager, or in `plugins.txt` with a leading `*`. Then follow [TESTING.md](TESTING.md).
