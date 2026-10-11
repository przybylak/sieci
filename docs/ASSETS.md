# Assets

The mod needs no new art. It reuses Fallout 4's own (rusted) motorcycle. Two stages:

- **Stage 1 (required):** a *wearable* copy of the motorcycle mesh, so the bike can be drawn under the player while riding.
- **Stage 2 (experimental, optional):** a seated pose, so the rider sits instead of running in place over the bike.

## Stage 1: the worn bike mesh

The parked bike uses the vanilla motorcycle nif unchanged. The *worn* copy has to be converted. Armor meshes in Fallout 4 must be **skinned** (every vertex weighted to a skeleton bone); an unweighted mesh on an armor will crash the game.

### Extract the vanilla mesh

1. In the CK, find the motorcycle static (Object Window → `WorldObjects → Static`, filter `motorcycle`) and note its model path.
2. Extract that nif from `Data\Fallout4 - Meshes.ba2` with Archive2 (`Tools\Archive2\Archive2.exe` → open the ba2 → find the path → Extract).
   If it isn't there, try `Fallout4 - MeshesExtra.ba2`.

### Convert it in Outfit Studio

1. Start Outfit Studio, `File → New Project`. Use any Fallout 4 reference/template if it asks; it only provides the skeleton. Then `File → Import → From NIF…` → the motorcycle nif.
2. **Orientation and position.** Actors face **+Y** and stand at the origin.
   - Rotate the bike so the front wheel points to +Y (`Shape → Rotate`/`Transform`, usually 90° around Z if it points along X).
   - Move it so the wheels touch Z = 0 and the seat sits roughly over X = 0, Y = 0.
   - A standing player's pelvis is ~70 units up, and the vanilla bike's seat is lower. That's fine; the seated pose in Stage 2 brings the rider down.
3. **Skinning.** In the Bones tab, add the bone **`Root`** (right-click → Add Bone). With `Root` selected, paint the *whole* mesh at full strength until everything is fully weighted.
   Do this for every shape in the nif (frame, wheels, glass, …).
   - `Root` follows the actor's position and heading but not the animation's bobbing, so the bike stays planted.
     If `Root` isn't offered, use `COM` (the bike will bob a little with the run cycle).
4. Delete any reference body shape so only the bike shapes remain.
5. `File → Export → To NIF…` → `Data\Meshes\CMB\CMB_BikeWorn.nif`.

### Check it in NifSkope

Open `CMB_BikeWorn.nif` and confirm:

- each shape is a `BSTriShape`/`BSSubIndexTriShape` with a `BSSkin::Instance` (it's skinned);
- each shape's `BSLightingShaderProperty` **Name** still holds the original `.bgsm` material path.
  If it's empty, copy it from the original nif, otherwise the bike renders pink or untextured;
- there is no collision object left over (`bhkNPCollisionObject`). Delete it if there is.

### Quick in-game look before scripting

`help CMB 4` in the console shows your forms. Then `player.equipitem <CMB_BikeRiderArmor form id>` lets you look at the worn bike directly:

| Symptom | Fix |
|---|---|
| bike rotated 90°/180° | rotate in Outfit Studio and export again |
| bike floats / sinks | adjust Z in Outfit Studio |
| invisible | the ARMA race isn't HumanRace, or ARMA and ARMO slots don't match |
| pink / white | material path lost, see NifSkope step |
| CTD when equipping | unweighted vertices: weight *every* shape fully |

Unequip with `player.unequipitem <id>` and remove with `player.removeitem <id> 1`.

## Stage 2 (experimental): seated rider pose

> **Status: untested idea.** It's based on how Fallout 4's animation subgraphs are documented to work, but nobody has confirmed it in game for this mod yet. The mod is fully usable without it (keep `CMB_UseRiderPose` at 0).

### How it's meant to work

Fallout 4 picks animation folders through *subgraph data* on the race. An actor with an extra archetype keyword can be pointed at an extra folder searched *before* the vanilla one, and any clip found there replaces the vanilla clip with the same name.

So:

1. While riding, the controller calls `ChangeAnimArchetype(CMB_AnimArchetypeRider)` and `AttemptAnimationSetSwitch()` on the player.
   On dismount it restores `AnimArchetypePlayer`.
2. A new HumanRace subgraph entry for that keyword searches `Actors\Character\Animations\CMB_Rider\` first.
3. That folder holds copies of a single **vanilla seated loop** saved under the names of the walk/run/turn/idle clips.
   No animation authoring is needed, just file copies.

### Steps

1. **Keyword:** `Miscellaneous → Keyword → New`, `CMB_AnimArchetypeRider`, type **Anim Archetype**.
   Set it (and the vanilla `AnimArchetypePlayer`) on the controller script's properties.
2. **Find the player's third-person MT entry.** Open `HumanRace`, go to the subgraph/behaviour data section, and find the entry with
   Actor Keywords containing `AnimArchetypePlayer`, Perspective *3rd*, Role *MT*. Note its **Paths** list.
3. **Duplicate that entry.** Change its Actor Keywords to `CMB_AnimArchetypeRider` (plus whatever non-archetype keywords the original had), and add
   `Actors\Character\Animations\CMB_Rider\` as the *first* path, keeping the original paths after it.
   > This edits the vanilla `HumanRace`, which many mods also touch. If something stops animating, check for a
   > race conflict in xEdit and forward the other mod's changes.
4. **Extract animations:** Archive2 → `Fallout4 - Animations.ba2` → extract the folders named in the Paths from step 2.
5. **Pick a seated loop.** A bar-stool sitting idle works best, because its hips are about as high as a motorcycle seat.
   A chair-sitting idle is the fallback. They live under the furniture animation folders. Preview candidates in the CK's preview window if unsure.
6. **Generate the folder:**

   ```
   python tools/make_rider_pose.py --vanilla-dir <extracted folder from step 2> --pose <seated clip.hkx> --out "<Data>/Meshes/Actors/Character/Animations/CMB_Rider" --dry-run
   ```

   Check the list (only walk/run/turn/idle clips), then run it again without `--dry-run`.
7. In game: `set CMB_UseRiderPose to 1` and get on the bike.

### If it doesn't work

| Symptom | Likely cause |
|---|---|
| no change at all | subgraph entry not matching (keyword type, perspective or role differs), or the folder path is wrong |
| T-pose / frozen player | the copied clip doesn't fit the graph. Try a different seated clip, or narrow the file list |
| stuck in pose after getting off | `AnimArchetypePlayer` property not filled. Run the emergency reset from TESTING.md |

The proper long-term answer is real riding animations (lean, idle with a foot down, mount/dismount). That needs an animator and a Fallout 4 Havok pipeline (3ds Max + Havok Content Tools, or a Blender HKX workflow). See the roadmap in the README.
