# Assets

The mod needs no new art. It reuses Fallout 4's own (rusted) motorcycle. Two stages:

- **Stage 1 (required):** two copies of the motorcycle mesh, one to park and one to wear.
- **Stage 2 (experimental, optional):** a seated pose, so the rider sits instead of running in place over the bike.

All files go in `Data\Meshes\CMB\` (see `Data/Meshes/CMB/PUT_MESHES_HERE.txt`).

## Stage 1: the bike meshes

### Find and extract the vanilla motorcycle

Fallout 4 has two motorcycle models: the rusted one and a clean pre-war one. Each comes as a Static
(`Motorcycle01_Static` `0017935A`, `Motorcycle01_Prewar_Static` `0017AD86`) and as a movable static
(`Motorcycle01` `00188D4C`, `Motorcycle01_Prewar` `00188D2A`). **Use a Static's model**, either look; it has
fixed collision, while a movable static's physics could make the parked bike tip over. Use the same model for both copies below.

1. Get its model path: in the CK, Object Window → `WorldObjects → Static`, filter `Motorcycle01`, open the one you want and read the model path.
   In xEdit: `Fallout4.esm → Static → Motorcycle01_Static` (or `_Prewar_Static`) → `Model → MODL`.
2. Extract that nif from `Data\Fallout4 - Meshes.ba2` with Archive2 (`<Fallout 4>\Tools\Archive2\Archive2.exe`, open the ba2, find the path, Extract).
   If it isn't there, try `Fallout4 - MeshesExtra.ba2`.
   Bethesda Archive Extractor (BAE) works too and has a search box: search for `motorcycle`.

### The parked bike: just a copy

Save an **unmodified** copy as `Data\Meshes\CMB\CMB_BikeParked.nif`. Its textures and materials point at vanilla files, which the game already has.

### The worn bike: convert it

The *worn* copy has to be converted. Armor meshes in Fallout 4 must be **skinned** (every vertex weighted to a skeleton bone); an unweighted mesh on an armor will crash the game.

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

### The keys (optional)

Copy any vanilla key mesh to `Data\Meshes\CMB\CMB_Keys.nif`; it's only used for the 3D preview in the Pip-Boy.
Without it the keys work fine and just have no preview.

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

### Why this is the only route

The game has no motorcycle riding animations to borrow. `Fallout4.esm` does contain a keyword called `AnimsMotorcycle`
(`000AB732`), but nothing in the game uses it, and the animation archives contain no motorcycle clips. The only
motorcycle assets are the two parked-bike models (the rusted `Motorcycle01` and the clean pre-war `Motorcycle01_Prewar`).
So it's this file-copy trick or new animation work.

### Steps

The keyword `CMB_AnimArchetypeRider` (type Anim Archetype) is already in the plugin and wired to the controller,
together with the vanilla `AnimArchetypePlayer`. What's missing is the race edit and the animation files.

The race edit goes in a **separate small patch plugin** made with **FO4Edit (xEdit)**, not in the Creation Kit.
That keeps the main plugin conflict-free. xEdit also has no trouble using the light-flagged main plugin as a master,
which the Creation Kit is awkward about.

1. **Find the player's third-person MT entry.** In FO4Edit, load `Fallout4.esm` + `CommonwealthMotorbike.esp`.
   Open `Fallout4.esm → Race → HumanRace` and look through its subgraph data for the entry whose
   Actor Keywords contain `AnimArchetypePlayer`, with Perspective *3rd* and Role *MT*. Note its **Paths**.
2. **Make the patch.** Right-click `HumanRace` → *Copy as override into…* → new file `CMB_RiderPose.esp`
   (accept `CommonwealthMotorbike.esp` as a master; flag it ESL if offered).
   **Start from the winning HumanRace, not the vanilla one.** If another mod edits HumanRace (for example LooksMenu
   Customization Compendium), right-click *that mod's* HumanRace row in the comparison view and copy it as the override,
   so its changes are kept. Load the patch after it. If that mod later updates its HumanRace, redo this step.
3. **Add the entry.** In the override, duplicate the entry from step 1. In the copy:
   - replace `AnimArchetypePlayer` with `CMB_AnimArchetypeRider` in Actor Keywords (keep any other keywords);
   - add `Actors\Character\Animations\CMB_Rider\` as the **first** path, and keep the original paths after it.
4. **Extract animations:** Archive2 → `Fallout4 - Animations.ba2` → extract the folders named in the Paths from step 1.
5. **Pick a seated loop.** A bar-stool sitting idle works best, because its hips are about as high as a motorcycle seat.
   A chair-sitting idle is the fallback. They live under the furniture animation folders. Preview candidates in the CK's preview window if unsure.
6. **Generate the folder:**

   ```
   python tools/make_rider_pose.py --vanilla-dir <extracted folder from step 1> --pose <seated clip.hkx> --out "<Data>/Meshes/Actors/Character/Animations/CMB_Rider" --dry-run
   ```

   Check the list (only walk/run/turn/idle clips), then run it again without `--dry-run`.
7. Enable `CMB_RiderPose.esp` after `CommonwealthMotorbike.esp` and after anything else that edits HumanRace.
8. In game: `set CMB_UseRiderPose to 1` and get on the bike.

> **Don't** set `CMB_UseRiderPose` to 1 without the patch from step 3. Switching the player to an archetype
> that has no subgraph entry can leave them unable to walk properly (reported by other modders).
> If that happens, set it back to 0 and run the emergency reset.

### If it doesn't work

| Symptom | Likely cause |
|---|---|
| no change at all | subgraph entry not matching (keyword type, perspective or role differs), or the folder path is wrong |
| T-pose / frozen player | the copied clip doesn't fit the graph. Try a different seated clip, or narrow the file list |
| stuck in pose after getting off | `AnimArchetypePlayer` property not filled. Run the emergency reset from TESTING.md |

The proper long-term answer is real riding animations (lean, idle with a foot down, mount/dismount). That needs an animator and a Fallout 4 Havok pipeline (3ds Max + Havok Content Tools, or a Blender HKX workflow). See the roadmap in the README.
