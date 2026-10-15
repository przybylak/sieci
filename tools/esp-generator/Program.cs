// Generates CommonwealthMotorbike.esp: every record the mod's scripts need,
// with scripts attached and all properties filled, so nobody has to build the
// plugin by hand in the Creation Kit.
//
//   dotnet run -c Release -- <output.esp>          write the plugin
//   dotnet run -c Release -- --dump <plugin.esp>   print what a plugin contains
//
// Vanilla form IDs below were checked against Mutagen.Bethesda.FormKeys.Fallout4
// (generated from the real Fallout4.esm), except PlayerRef (00000014), which is
// the engine's hard-coded player reference.

using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Records;
using Mutagen.Bethesda.Strings;
using Noggog;

namespace CmbEspGenerator;

public static class Vanilla
{
    static FormKey Fo4(uint id) => new(ModKey.FromFileName("Fallout4.esm"), id);

    public static readonly FormKey PlayerRef = Fo4(0x000014);
    public static readonly FormKey XMarker = Fo4(0x00003B);
    public static readonly FormKey HumanRace = Fo4(0x013746);
    public static readonly FormKey SpeedMult = Fo4(0x0002DA);
    public static readonly FormKey CarryWeight = Fo4(0x0002DC);
    public static readonly FormKey FallingDamageMod = Fo4(0x0BA43D);
    public static readonly FormKey Health = Fo4(0x0002D4);
    public static readonly FormKey Pipboy = Fo4(0x021B3B);
    public static readonly FormKey AnimArchetypePlayer = Fo4(0x06B508);
    public static readonly FormKey HumanRaceSubGraphData = Fo4(0x166729);
    public static readonly FormKey AmmoFlamerFuel = Fo4(0x0CAC78);
    public static readonly FormKey AudioCategorySFX = Fo4(0x0172A1);
    public static readonly FormKey SOMMono02000 = Fo4(0x07E5DC);

    // Record types of the vanilla forms above, for the property type check.
    public static string Describe(FormKey key) =>
        key == PlayerRef ? "PlacedNpc"
        : key == XMarker ? "Static"
        : key == HumanRace ? "Race"
        : key == SpeedMult || key == CarryWeight || key == FallingDamageMod || key == Health ? "ActorValueInformation"
        : key == Pipboy ? "Armor"
        : key == AnimArchetypePlayer ? "Keyword"
        : key == AmmoFlamerFuel ? "Ammunition"
        : key == AudioCategorySFX ? "SoundCategory"
        : key == SOMMono02000 ? "SoundOutputModel"
        : "unknown";
}

public static class Program
{
    public const string PluginName = "CommonwealthMotorbike.esp";

    // Paths are relative to Data\Meshes. tools/rider/build_bike_meshes.py makes them from
    // the vanilla motorcycle (docs/ASSETS.md): the parked bike is an unmodified copy, the
    // worn ones are that mesh turned to face forward and skinned to the rider's COM bone
    // (male and female seat heights) or to the AnimObjectA bone on the ground.
    public const string ParkedBikeModel = @"CMB\CMB_BikeParked.nif";
    public const string WornBikeModel = @"CMB\CMB_BikeWorn.nif";
    public const string RiderBikeModel = @"CMB\CMB_BikeWornRider.nif";
    public const string RiderBikeModelFemale = @"CMB\CMB_BikeWornRiderF.nif";
    public const string KeysModel = @"CMB\CMB_Keys.nif";

    // Biped slot the worn bike occupies; whatever else uses it gets unequipped
    // while riding. 58 clashed with Eli's Armour Compendium bags. 57 is an
    // "Unnamed" slot (60 would also be free in some setups, but it's the
    // slot named "Pipboy"). Change it here if another mod of yours uses 57.
    public const BipedObjectFlag BikeSlot = BipedObjectFlag.Unnamed57;
    // The headlamp piece's own slot (test 32: as a second addon in the bike's slot it never reached the
    // player's 3D; the biped keeps one part per slot). CMB_GearRestoreF4SE puts this slot's gear back too.
    public const BipedObjectFlag LampSlot = BipedObjectFlag.Unnamed58;
    public static int LampSlotIndex => System.Numerics.BitOperations.TrailingZeroCount((uint)LampSlot);
    // F4SE counts slots from 30: slot 57 is index 27, the flag's bit number.
    public static int BikeSlotIndex => System.Numerics.BitOperations.TrailingZeroCount((uint)BikeSlot);

    public static int Main(string[] args)
    {
        if (args.Length == 2 && args[0] == "--dump")
        {
            Dump(args[1]);
            return 0;
        }
        if (args.Length == 2 && args[0] == "--rider-template")
        {
            if (Path.GetFileName(args[1]) != RiderPluginName)
            {
                Console.Error.WriteLine($"The template must be called {RiderPluginName}.");
                return 1;
            }
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(args[1]))!);
            BuildRiderTemplate().WriteToBinary(args[1]);
            Console.WriteLine($"Wrote {args[1]}");
            Dump(args[1]);
            return 0;
        }
        var output = args.Length == 1 ? args[0] : PluginName;
        if (Path.GetFileName(output) != PluginName)
        {
            Console.Error.WriteLine($"The plugin must be called {PluginName} (scripts and docs refer to it).");
            return 1;
        }
        var mod = Build();
        var dataDir = Path.GetDirectoryName(Path.GetFullPath(output))!;
        Directory.CreateDirectory(dataDir);
        mod.WriteToBinary(output);
        Console.WriteLine($"Wrote {output}");
        WriteMcm(mod, dataDir);
        Dump(output);
        return 0;
    }

    // The seated rider pose lives in its own small light plugin, built on the player's PC
    // by tools/rider/make_rider_plugin.py from this template: it copies the player's
    // third-person MT subgraph entries from their load order in place of the placeholder
    // below, and writes the matching AnimTextData. Separate because its masters depend
    // on the load order (e.g. the Unofficial Patch's keywords).
    public const string RiderPluginName = "CMB_RiderPose.esp";
    public const string RiderFolder = @"Actors\Character\Animations\MT\CMB_Rider";
    public const string TemplatePlaceholderGraph = "CMB_TEMPLATE_PLACEHOLDER";

    static Fallout4Mod BuildRiderTemplate()
    {
        var mod = new Fallout4Mod(ModKey.FromFileName(RiderPluginName), Fallout4Release.Fallout4);
        mod.ModHeader.Stats.NextFormID = 0x800;
        mod.ModHeader.Author = "Commonwealth Motorbike";
        mod.ModHeader.Description = "Seated riding animations for Commonwealth Motorbike.";
        mod.IsSmallMaster = true;

        // Form ID 0x800: the controller script looks it up with GetFormFromFile.
        var flavor = mod.Keywords.AddNew("CMB_AnimFlavorRider");
        flavor.Type = Keyword.TypeEnum.AnimFlavor;
        flavor.Color = System.Drawing.Color.FromArgb(0, 0, 0, 0); // CNAM is a required field

        // Additive race: its subgraph entries are added to HumanRaceSubGraphData (where the
        // human animation setup lives) the way the DLCs add theirs; HumanRace isn't edited.
        var race = mod.Races.AddNew("CMB_RiderSubgraphData");
        race.SubgraphAdditiveRace.SetTo(Vanilla.HumanRaceSubGraphData);
        var placeholder = new Subgraph
        {
            BehaviorGraph = TemplatePlaceholderGraph,
            Role = Subgraph.SubgraphRole.MT,
        };
        placeholder.ActorKeywords.Add(new FormLink<IKeywordGetter>(Vanilla.AnimArchetypePlayer));
        placeholder.ActorKeywords.Add(flavor);
        placeholder.AnimationPaths.Add(RiderFolder);
        race.Subgraphs.Add(placeholder);
        return mod;
    }

    // Mod Configuration Menu (needs MCM + F4SE; harmless without). Written from the same
    // build as the plugin so the form IDs always match.
    static void WriteMcm(Fallout4Mod mod, string dataDir)
    {
        const string modName = "CommonwealthMotorbike";
        string Form(IMajorRecordGetter r) => $"{PluginName}|{r.FormKey.ID:X}";
        IMajorRecordGetter Rec(string editorId) => mod.EnumerateMajorRecords().First(r => r.EditorID == editorId);
        var quest = Form(Rec("CMB_ControllerQuest"));
        object Global(string editorId) => new { sourceType = "GlobalValue", sourceForm = Form(Rec(editorId)) };
        object Slider(string text, string help, string global, float min, float max, float step) => new
        {
            type = "slider", text, help,
            valueOptions = new { min, max, step, sourceType = "GlobalValue", sourceForm = Form(Rec(global)) },
        };
        object Switcher(string text, string help, string global) => new { type = "switcher", text, help, valueOptions = Global(global) };
        object Section(string text) => new { type = "section", text };
        // Global functions on CMB_MCMRelay (tests 30 and 31: MCM called the quest's other scripts).
        object Call(string function) => new { type = "CallGlobalFunction", script = "CMB_MCMRelay", function, @params = Array.Empty<object>() };
        object Button(string text, string help, string function) => new { type = "button", text, help, action = Call(function) };

        var config = new
        {
            modName,
            displayName = "Commonwealth Motorbike",
            minMcmVersion = 2,
            pluginRequirements = new[] { PluginName },
            content = new object[]
            {
                Section("Riding"),
                Slider("Speed (%)", "Riding speed as a percentage of your normal speed. Takes effect the next time you get on. Above about 350 the world may not load in fast enough.",
                    "CMB_SpeedPercent", 100, 500, 10),
                Switcher("Seated riding animations", "Needs CMB_RiderPose.esp (make_rider_pose.bat). Off: you run in place over the bike. Takes effect the next time you get on.", "CMB_UseRiderPose"),
                Switcher("Switch to third person", "Switch to third person when getting on, so you see the bike.", "CMB_ForceThirdPerson"),
                Slider("Steepest slope while riding", "How steep a slope you can ride up, in degrees (on foot the game allows 47; 45 keeps a road bike off rock faces). Needs F4SE and the CMB_Slope.dll plugin. 0 = the same as on foot. Takes effect the next time you get on.",
                    "CMB_MaxSlope", 0, 80, 1),
                Slider("Riding camera distance", "How far back the third-person camera sits while riding (the game's own is about 150). Needs F4SE and the CMB_Slope.dll plugin. 0 = leave the camera alone. Takes effect the next time you get on.",
                    "CMB_RidingCameraDistance", 0, 1000, 25),
                Slider("Turning radius", "The tightest turn the bike makes at riding speed, in game units (about 70 = 1 m): no turning on the spot. Slower, it turns tighter (the next setting). Needs F4SE and the CMB_Slope.dll plugin. 0 = turn like on foot.",
                    "CMB_TurnRadius", 0, 600, 10),
                Slider("Turning radius at walking pace", "The tightest turn when the bike is barely moving; it widens to the turning radius above as you speed up. Needs F4SE and the CMB_Slope.dll plugin.",
                    "CMB_TurnRadiusSlow", 0, 300, 10),
                Slider("Turning when stopped (deg/s)", "How fast the bike can be walked round when it isn't moving (and the least it turns at any speed). Needs F4SE and the CMB_Slope.dll plugin.",
                    "CMB_StandTurnRate", 0, 180, 10),
                Slider("Bike tilts with the ground (max degrees)", "While riding, the bike and the rider pitch with the ground by at most this much (needs F4SE and the CMB_Slope.dll plugin; 45 follows any slope you can climb). Takes effect the next time you get on.",
                    "CMB_MaxTilt", 0, 50, 1),
                Switcher("Allow combat while riding", "Weapons and VATS stay usable while riding. Takes effect the next time you get on.", "CMB_AllowCombat"),
                Switcher("Thrown off when hit", "A big hit from an enemy knocks you off the bike, so you can fight back. Off: you keep riding; a hint says how to get off when a fight starts.", "CMB_DismountOnHit"),
                Slider("Big hit (% of max health)", "How much of your max health a hit (or several within about a second) must take to knock you off. Power attacks and explosions always do. 0 = any hit. Not in the first 3 seconds after getting on.",
                    "CMB_KnockOffDamage", 0, 50, 5),
                Slider("Less fall damage (%)", "How much less fall damage you take while riding. 100 = none. Takes effect the next time you get on.",
                    "CMB_FallDamageCut", 0, 100, 5),
                Slider("Free small falls (% of max health)", "Falls while riding that would cost less than this much of your max health cost nothing. Bigger falls still hurt (less, by the setting above). 0 = off. Every fall while riding is logged.",
                    "CMB_FreeFallDamage", 0, 100, 5),
                Switcher("Bike turns with the rider", "On: the bike hangs off the seated rider, so it turns with you on the spot and in conversations. Off: it stays planted on the ground (the rider can twist on it). Takes effect the next time you get on.", "CMB_BikeFollowsRider"),
                Section("Fuel"),
                Switcher("Use fuel", "Riding burns Flamer Fuel, from the side bag first, then your inventory.", "CMB_UseFuel"),
                Slider("Distance per Flamer Fuel", "In game units; about 70 units = 1 m. 21000 = about 300 m. Lower = thirstier.",
                    "CMB_FuelDistance", 3500, 70000, 3500),
                Section("Companions"),
                new
                {
                    type = "stepper", text = "Companions",
                    help = "Run alongside: they get the same speed boost. Ride along: they're hidden while you ride (riskier during their quests and scenes).",
                    valueOptions = new { options = new[] { "Run alongside", "Ride along (hidden)" }, sourceType = "GlobalValue", sourceForm = Form(Rec("CMB_CompanionMode")) },
                },
                Slider("Catch-up distance", "Companions running alongside further away than this are moved up behind you. 0 = never.",
                    "CMB_CatchUpDistance", 0, 10000, 250),
                Section("Side bag"),
                Slider("Side bag capacity", "Pounds with F4SE (items without it). 0 = unlimited.", "CMB_BagCapacity", 0, 500, 10),
                Section("Sound"),
                Slider("Engine volume", "0 = silent. The engine loops pick it up the next time you get on.", "CMB_EngineVolume", 0, 100, 5),
                Section("Headlamp"),
                new
                {
                    type = "stepper", text = "Headlamp",
                    help = "The bike's headlamp (needs F4SE and the CMB_Slope.dll plugin): off, on while riding, or on at night (19:00 to 6:30). The hotkey below switches it while you ride.",
                    valueOptions = new { options = new[] { "Off", "On", "On at night" }, sourceType = "GlobalValue", sourceForm = Form(Rec("CMB_HeadlampMode")) },
                },
                new { type = "hotkey", id = "ToggleHeadlamp", text = "Headlamp on / off", help = "Switches the headlamp while riding, until you get off or the next dusk or dawn; the setting above stays as it is." },
                Switcher("Headlamp casts shadows", "The beam casts shadows (costlier: the game runs only a few shadow lights at once). Takes effect the next time you get on.", "CMB_HeadlampShadows"),
                Section("Hotkeys"),
                new { type = "hotkey", id = "ToggleRide", text = "Get on / off / call the bike", help = "If you use this, set the built-in hotkey below to 0 so the key doesn't fire twice." },
                Slider("Built-in hotkey (scan code)", "The F4SE hotkey that works without MCM. 48 = B, 34 = G, 47 = V, 0 = off. Press Apply after changing it.",
                    "CMB_HotkeyCode", 0, 211, 1),
                Button("Apply built-in hotkey", "Re-registers the built-in hotkey after changing it.", "RefreshHotkey"),
                Section("Troubleshooting"),
                Button("Give me the keys", "For alternative starts that skip the Pip-Boy: hands over the Motorbike Keys now.", "ForceGiveKeys"),
                Button("Emergency reset", "Gets you off the bike and undoes everything riding changed: speed, controls, animations, hidden companions.", "EmergencyReset"),
            },
        };
        var keybinds = new
        {
            modName,
            keybinds = new object[]
            {
                new { id = "ToggleRide", desc = "Motorbike: get on / off / call", action = Call("HotkeyPressed") },
                new { id = "ToggleHeadlamp", desc = "Motorbike: headlamp on / off", action = Call("HeadlampPressed") },
            },
        };
        var dir = Path.Combine(dataDir, "MCM", "Config", modName);
        Directory.CreateDirectory(dir);
        var json = new System.Text.Json.JsonSerializerOptions { WriteIndented = true };
        File.WriteAllText(Path.Combine(dir, "config.json"), System.Text.Json.JsonSerializer.Serialize(config, json) + "\n");
        File.WriteAllText(Path.Combine(dir, "keybinds.json"), System.Text.Json.JsonSerializer.Serialize(keybinds, json) + "\n");
        Console.WriteLine($"Wrote {dir}");
    }

    static Fallout4Mod Build()
    {
        var mod = new Fallout4Mod(ModKey.FromFileName(PluginName), Fallout4Release.Fallout4);
        // ESL-compatible form IDs (0x800-0xFFF) so the plugin can be light-flagged.
        mod.ModHeader.Stats.NextFormID = 0x800;
        mod.ModHeader.Author = "Commonwealth Motorbike";
        mod.ModHeader.Description = "Rideable motorbike: call it, ride it, park it. Side bag and companions included.";
        mod.IsSmallMaster = true;

        // --- Settings (console: set <name> to <value>) ---
        var gSpeed = Global(mod, "CMB_SpeedPercent", 250);
        // Run alongside by default: hiding companions is riskier during their quests and scenes.
        var gCompanionMode = Global(mod, "CMB_CompanionMode", 0);
        var gAllowCombat = Global(mod, "CMB_AllowCombat", 0);
        var gThirdPerson = Global(mod, "CMB_ForceThirdPerson", 1);
        // 1 = seated riding animations when CMB_RiderPose.esp is installed, 0 = never.
        var gRiderPose = Global(mod, "CMB_UseRiderPose", 1);
        var gCatchUp = Global(mod, "CMB_CatchUpDistance", 2500);
        var gBagCapacity = Global(mod, "CMB_BagCapacity", 60);
        var gHotkey = Global(mod, "CMB_HotkeyCode", 48);
        var gUseFuel = Global(mod, "CMB_UseFuel", 1);
        var gFuelDistance = Global(mod, "CMB_FuelDistance", 21000); // ~300 m per unit (about 70 units = 1 m)

        // --- What the bike burns ---
        var fuelItems = mod.FormLists.AddNew("CMB_FuelItems");
        fuelItems.Items.Add(new FormLink<IFallout4MajorRecordGetter>(Vanilla.AmmoFlamerFuel));

        // --- Menus (button order matters: the scripts read the index) ---
        var msgParked = MessageBox(mod, "CMB_ParkedMenu", "Motorbike", "What do you want to do?",
            "Ride", "Open side bag", "Cancel");
        var msgKeys = MessageBox(mod, "CMB_KeysMenu", "Motorbike", "Your motorbike isn't nearby.",
            "Call it here", "Open side bag", "Cancel");

        // --- Controller quest (created early so other records can point at it) ---
        var quest = mod.Quests.AddNew("CMB_ControllerQuest");
        if (quest.FormKey.ID != 0x80D)
            throw new InvalidOperationException($"CMB_ControllerQuest must be 0x80D (CMB_MCMRelay.psc looks it up), got {quest.FormKey.ID:X}");

        // --- Worn bike: hangs off the seated rider (the ground-planted one is further down) ---
        var armor = WornBike(mod, "CMB_BikeRiderAA", "CMB_BikeRiderArmor", RiderBikeModel, RiderBikeModelFemale);

        // --- Keys: aid item + script effect ---
        var keysEffect = mod.MagicEffects.AddNew("CMB_BikeKeysEffect");
        keysEffect.Name = "Motorbike Keys";
        keysEffect.Flags = MagicEffect.Flag.NoDuration | MagicEffect.Flag.NoMagnitude | MagicEffect.Flag.NoArea
            | MagicEffect.Flag.HideInUI | MagicEffect.Flag.Painless;
        keysEffect.Archetype = new MagicEffectArchetype { Type = MagicEffectArchetype.TypeEnum.Script };
        keysEffect.CastType = CastType.FireAndForget;
        keysEffect.TargetType = TargetType.Self;
        keysEffect.CastingSoundLevel = SoundLevel.Silent; // using the keys shouldn't alert enemies
        keysEffect.DualCastScale = 1; // CK default
        keysEffect.VirtualMachineAdapter = Vmad(Script("CMB_KeysEffectScript", Obj("Controller", quest)));

        var keys = mod.Ingestibles.AddNew("CMB_BikeKeys");
        keys.Name = "Motorbike Keys";
        keys.Description = "Use near the bike to get on, or anywhere outdoors to call it. Use while riding to get off.";
        keys.ObjectBounds = new ObjectBounds();
        keys.Model = new Model { File = KeysModel };
        keys.Weight = 0;
        keys.Value = 0;
        keys.Flags = Ingestible.Flag.NoAutoCalc;
        keys.Effects.Add(new Effect
        {
            BaseEffect = keysEffect.ToNullableLink(),
            Data = new EffectData { Magnitude = 0, Area = 0, Duration = 0 },
        });

        // --- Parked bike and side bag ---
        var bikeBase = mod.Activators.AddNew("CMB_BikeActivator");
        bikeBase.Name = "Motorbike";
        bikeBase.ActivateTextOverride = "Use";
        bikeBase.ObjectBounds = Bounds(120, 120, 0, 120);
        bikeBase.Model = new Model { File = ParkedBikeModel };
        bikeBase.VirtualMachineAdapter = Vmad(Script("CMB_BikeActivatorScript",
            Obj("Controller", quest),
            Obj("CMB_ParkedMenu", msgParked)));

        var bagBase = mod.Containers.AddNew("CMB_SideBagContainer");
        bagBase.Name = "Side Bag";
        bagBase.ObjectBounds = Bounds(30, 30, 0, 30);
        bagBase.Model = new Model { File = ParkedBikeModel }; // never rendered, it stays in the holding cell
        bagBase.Weight = 0;
        bagBase.VirtualMachineAdapter = Vmad(Script("CMB_SideBagScript",
            Obj("CMB_BagCapacity", gBagCapacity),
            Obj("PlayerRef", Vanilla.PlayerRef)));

        // --- Holding cell: where the bike starts and companions wait while hidden ---
        var cell = new Cell(mod.GetNextFormKey(), Fallout4Release.Fallout4)
        {
            EditorID = "CMB_HoldingCell",
            Name = "Motorbike Holding Cell",
            Flags = Cell.Flag.IsInteriorCell,
            Lighting = new CellLighting(),
        };
        var bikeRef = Placed(mod, cell, "CMB_BikeRef", bikeBase.FormKey, new P3Float(0, 0, 0));
        var bagRef = Placed(mod, cell, "CMB_SideBagRef", bagBase.FormKey, new P3Float(400, 0, 0));
        var markerRef = Placed(mod, cell, "CMB_HoldingMarkerRef", Vanilla.XMarker, new P3Float(0, 400, 0));
        AddInteriorCell(mod, cell);

        // --- Engine sounds (added last so earlier form IDs stay put) ---
        // tools/sound/make_engine_sounds.py writes the files to Data\Sound\FX\CMB.
        var sndStart = EngineSound(mod, "CMB_EngineStartSD", "CMB_EngineStart.wav", loop: false);
        var sndStop = EngineSound(mod, "CMB_EngineStopSD", "CMB_EngineStop.wav", loop: false);
        var sndIdle = EngineSound(mod, "CMB_EngineIdleLPSD", "CMB_EngineIdleLP.wav", loop: true);
        var sndCruise = EngineSound(mod, "CMB_EngineCruiseLPSD", "CMB_EngineCruiseLP.wav", loop: true);
        var gEngineVolume = Global(mod, "CMB_EngineVolume", 70);

        // --- Riding safety and the ground-planted bike (also last, for the same reason) ---
        var gFallCut = Global(mod, "CMB_FallDamageCut", 75);   // percent less fall damage while riding
        var gDismountOnHit = Global(mod, "CMB_DismountOnHit", 1);
        var gFollowsRider = Global(mod, "CMB_BikeFollowsRider", 1);
        var armorFrame = WornBike(mod, "CMB_BikeRiderFrameAA", "CMB_BikeRiderArmorFrame", WornBikeModel, WornBikeModel);

        // A hidden ability whose effect runs while the player is swimming (deep water only).
        var swimEffect = WatchEffect(mod, "CMB_SwimWatchEffect", "Motorbike swim watch", quest, wading: false);

        var swimAbility = mod.Spells.AddNew("CMB_SwimWatchAbility");
        swimAbility.Name = "Motorbike swim watch";
        swimAbility.ObjectBounds = new ObjectBounds();
        swimAbility.Type = SpellType.Ability;
        swimAbility.CastType = CastType.ConstantEffect;
        swimAbility.TargetType = TargetType.Self;
        swimAbility.Flags = SpellDataFlag.ManualCostCalc;
        swimAbility.Effects.Add(WatchEntry(swimEffect, Condition.Function.IsSwimming));

        // Feels for the ground around the parked bike (navmesh), to tilt it, when CMB_Slope.dll
        // isn't there to say what the ground under the player is like. (Was CMB_DrySpotMarkerRef,
        // no longer used; same record, so the form IDs after it don't move.)
        var probeRef = Placed(mod, cell, "CMB_GroundProbeRef", Vanilla.XMarker, new P3Float(0, -400, 0));

        // Percent of max health a hit (or a quick run of hits) must take to knock you off.
        var gKnockOff = Global(mod, "CMB_KnockOffDamage", 10);
        // Falls while riding costing less than this percent of max health cost nothing.
        var gFreeFall = Global(mod, "CMB_FreeFallDamage", 20);

        // Second swim-watch effect: in water at any depth (IsInWater), so the bike rolls up
        // once the player is on dry land rather than while they're still wading.
        var wadeEffect = WatchEffect(mod, "CMB_WadeWatchEffect", "Motorbike wade watch", quest, wading: true);
        swimAbility.Effects.Add(WatchEntry(wadeEffect, Condition.Function.IsInWater));

        // How far back the third-person camera sits while riding (CMB_Slope.dll, needs F4SE).
        var gCamera = Global(mod, "CMB_RidingCameraDistance", 450);

        // Steeper slopes (F4SE plugin CMB_Slope.dll, tools/f4se-slope). The plugin finds
        // CMB_SlopeLive by its form ID (0x82A) and editor ID: keep these two in this order.
        var gMaxSlope = Global(mod, "CMB_MaxSlope", 45);
        var gSlopeLive = Global(mod, "CMB_SlopeLive", 0);
        if (gSlopeLive.FormKey.ID != 0x82A)
            throw new InvalidOperationException($"CMB_SlopeLive must be 0x82A (CMB_Slope.dll looks for it), got {gSlopeLive.FormKey.ID:X}");
        // The riding camera distance for the same plugin (CMB_RidingCameraDistance while riding).
        var gCameraLive = Global(mod, "CMB_CameraLive", 0);
        if (gCameraLive.FormKey.ID != 0x82B)
            throw new InvalidOperationException($"CMB_CameraLive must be 0x82B (CMB_Slope.dll looks for it), got {gCameraLive.FormKey.ID:X}");
        // The bike tilts with the ground, by at most CMB_MaxTilt degrees: CMB_TiltLive is that while
        // riding (the plugin tilts the worn bike), and the plugin writes the ground under the player
        // into CMB_GroundNormalX/Y/Z (the script lays the parked bike on it). Fixed IDs, 0x82C-0x82F.
        var gTiltLive = Global(mod, "CMB_TiltLive", 0);
        var gGround = new[] { "X", "Y", "Z" }.Select(axis => Global(mod, "CMB_GroundNormal" + axis, 0)).ToArray();
        if (gTiltLive.FormKey.ID != 0x82C || gGround[0].FormKey.ID != 0x82D || gGround[2].FormKey.ID != 0x82F)
            throw new InvalidOperationException($"CMB_TiltLive and CMB_GroundNormalX/Y/Z must be 0x82C-0x82F (CMB_Slope.dll looks for them), got {gTiltLive.FormKey.ID:X}, {gGround[0].FormKey.ID:X}");
        var gMaxTilt = Global(mod, "CMB_MaxTilt", 45);
        // Where to park: on the ground just ridden (the plugin writes these while riding).
        // Fixed IDs too, 0x831-0x837; ParkUpZ 0 = no spot.
        var gPark = new[] { "X", "Y", "Z", "Angle", "UpX", "UpY", "UpZ" }.Select(n => Global(mod, "CMB_Park" + n, 0)).ToArray();
        if (gPark[0].FormKey.ID != 0x831 || gPark[6].FormKey.ID != 0x837)
            throw new InvalidOperationException($"CMB_ParkX..CMB_ParkUpZ must be 0x831-0x837 (CMB_Slope.dll looks for them), got {gPark[0].FormKey.ID:X}");
        // How steep the ground just ridden is (the plugin writes it while riding): the script
        // refuses getting off on a face too steep to stand on. Fixed ID 0x838.
        var gTrackSlope = Global(mod, "CMB_TrackSlope", 0);
        if (gTrackSlope.FormKey.ID != 0x838)
            throw new InvalidOperationException($"CMB_TrackSlope must be 0x838 (CMB_Slope.dll looks for it), got {gTrackSlope.FormKey.ID:X}");
        // Steering (the plugin reads these, the MCM sets them): the tightest turn at riding speed,
        // how fast the bike can be turned round when stopped, and the tightest turn at walking
        // pace. Fixed IDs 0x839, 0x83A, 0x83B.
        var gTurnRadius = Global(mod, "CMB_TurnRadius", 180);
        var gStandTurn = Global(mod, "CMB_StandTurnRate", 60);
        var gTurnSlow = Global(mod, "CMB_TurnRadiusSlow", 50);
        if (gTurnRadius.FormKey.ID != 0x839 || gStandTurn.FormKey.ID != 0x83A || gTurnSlow.FormKey.ID != 0x83B)
            throw new InvalidOperationException($"CMB_TurnRadius, CMB_StandTurnRate and CMB_TurnRadiusSlow must be 0x839-0x83B (CMB_Slope.dll looks for them), got {gTurnRadius.FormKey.ID:X}, {gStandTurn.FormKey.ID:X}, {gTurnSlow.FormKey.ID:X}");

        // --- The headlamp (test 29's wish): the MCM's mode, the live switch the plugin reads, and the
        // lights the game hangs on the worn bike's add-on nodes (CMB_Headlamp 31985, CMB_HeadlampShadow 31986).
        var gHeadlampMode = Global(mod, "CMB_HeadlampMode", 2);   // 0 off, 1 on while riding, 2 on at night
        var gHeadlampLive = Global(mod, "CMB_HeadlampLive", 0);   // 1 while the lamp should be lit (CMB_Slope.dll reads it)
        if (gHeadlampMode.FormKey.ID != 0x83C || gHeadlampLive.FormKey.ID != 0x83D)
            throw new InvalidOperationException($"CMB_HeadlampMode and CMB_HeadlampLive must be 0x83C-0x83D (CMB_Slope.dll looks for them), got {gHeadlampMode.FormKey.ID:X}, {gHeadlampLive.FormKey.ID:X}");
        var lampLight = Headlamp(mod, "CMB_HeadlampLight", false);
        var lampLightShadow = Headlamp(mod, "CMB_HeadlampLightShadow", true);
        HeadlampNode(mod, "CMB_HeadlampAddOn", HeadlampNodeIndex, lampLight);
        HeadlampNode(mod, "CMB_HeadlampShadowAddOn", HeadlampNodeIndex + 1, lampLightShadow);
        // Test 30: the game keeps no add-on node of a worn mesh, so the controller script places the light
        // as a reference and tells the plugin its form id (two globals: the high and low 16 bits), and the
        // plugin keeps it at the lens.
        var gHeadlampShadows = Global(mod, "CMB_HeadlampShadows", 0);
        var gHeadlampRefHi = Global(mod, "CMB_HeadlampRefHi", 0);
        var gHeadlampRefLo = Global(mod, "CMB_HeadlampRefLo", 0);
        if (gHeadlampShadows.FormKey.ID != 0x842 || gHeadlampRefHi.FormKey.ID != 0x843 || gHeadlampRefLo.FormKey.ID != 0x844)
            throw new InvalidOperationException($"CMB_HeadlampShadows, CMB_HeadlampRefHi and CMB_HeadlampRefLo must be 0x842-0x844 (CMB_Slope.dll looks for them), got {gHeadlampShadows.FormKey.ID:X}, {gHeadlampRefHi.FormKey.ID:X}, {gHeadlampRefLo.FormKey.ID:X}");
        // One nif per bone the bike hangs off (its root carries a Prn naming it, and the bike's own
        // skin-to-bone transform, so the nodes sit at the lens): the seated bike's COM, male and female
        // seat heights, and the planted bike's AnimObjectA.
        AddLampAddon(mod, armor, "CMB_BikeRiderLampAA", "CMB\\CMB_BikeLamp.nif", "CMB\\CMB_BikeLampF.nif");
        AddLampAddon(mod, armorFrame, "CMB_BikeRiderFrameLampAA", "CMB\\CMB_BikeLampFrame.nif", "CMB\\CMB_BikeLampFrame.nif");

        // --- Controller quest ---
        quest.Name = "Commonwealth Motorbike";
        quest.Data = new QuestData
        {
            Flags = Quest.Flag.StartGameEnabled,
            Priority = 50,
            Type = Quest.TypeEnum.None,
        };
        const uint playerAliasId = 0;
        quest.Aliases ??= new ExtendedList<AQuestAlias>();
        quest.Aliases.Add(new QuestReferenceAlias
        {
            ID = playerAliasId,
            Name = "Player",
            Flags = 0,
            ForcedReference = new FormLinkNullable<IPlacedGetter>(Vanilla.PlayerRef),
        });

        var controller = Script("CMB_ControllerScript",
            Obj("PlayerRef", Vanilla.PlayerRef),
            Obj("BikeRef", bikeRef),
            Obj("SideBagRef", bagRef),
            Obj("HoldingMarkerRef", markerRef),
            Obj("CMB_BikeRiderArmor", armor),
            Obj("CMB_BikeRiderArmorFrame", armorFrame),
            Obj("CMB_SwimWatchAbility", swimAbility),
            Obj("FallingDamageMod", Vanilla.FallingDamageMod),
            Obj("Health", Vanilla.Health),
            Obj("CMB_BikeKeys", keys),
            Obj("CMB_KeysMenu", msgKeys),
            Obj("SpeedMult", Vanilla.SpeedMult),
            Obj("CarryWeight", Vanilla.CarryWeight),
            Obj("Pipboy", Vanilla.Pipboy),
            Obj("CMB_FuelItems", fuelItems),
            Obj("CMB_SpeedPercent", gSpeed),
            Obj("CMB_CompanionMode", gCompanionMode),
            Obj("CMB_AllowCombat", gAllowCombat),
            Obj("CMB_ForceThirdPerson", gThirdPerson),
            Obj("CMB_UseRiderPose", gRiderPose),
            Obj("CMB_CatchUpDistance", gCatchUp),
            Obj("CMB_UseFuel", gUseFuel),
            Obj("CMB_FuelDistance", gFuelDistance),
            Obj("CMB_EngineStartSound", sndStart),
            Obj("CMB_EngineStopSound", sndStop),
            Obj("CMB_EngineIdleSound", sndIdle),
            Obj("CMB_EngineCruiseSound", sndCruise),
            Obj("CMB_EngineVolume", gEngineVolume),
            Obj("CMB_FallDamageCut", gFallCut),
            Obj("CMB_HeadlampMode", gHeadlampMode),
            Obj("CMB_HeadlampLive", gHeadlampLive),
            Obj("CMB_HeadlampLight", lampLight),
            Obj("CMB_HeadlampLightShadow", lampLightShadow),
            Obj("CMB_HeadlampShadows", gHeadlampShadows),
            Obj("CMB_HeadlampRefHi", gHeadlampRefHi),
            Obj("CMB_HeadlampRefLo", gHeadlampRefLo),
            Obj("CMB_DismountOnHit", gDismountOnHit),
            Obj("CMB_BikeFollowsRider", gFollowsRider),
            Obj("CMB_KnockOffDamage", gKnockOff),
            Obj("CMB_FreeFallDamage", gFreeFall),
            Obj("CMB_RidingCameraDistance", gCamera),
            Obj("CMB_MaxSlope", gMaxSlope),
            Obj("CMB_SlopeLive", gSlopeLive),
            Obj("CMB_CameraLive", gCameraLive),
            Obj("CMB_MaxTilt", gMaxTilt),
            Obj("CMB_TiltLive", gTiltLive),
            Obj("CMB_GroundNormalX", gGround[0]),
            Obj("CMB_GroundNormalY", gGround[1]),
            Obj("CMB_GroundNormalZ", gGround[2]),
            Obj("CMB_ParkX", gPark[0]),
            Obj("CMB_ParkY", gPark[1]),
            Obj("CMB_ParkZ", gPark[2]),
            Obj("CMB_ParkAngle", gPark[3]),
            Obj("CMB_ParkUpX", gPark[4]),
            Obj("CMB_ParkUpY", gPark[5]),
            Obj("CMB_ParkUpZ", gPark[6]),
            Obj("CMB_TrackSlope", gTrackSlope),
            Obj("CMB_TurnRadius", gTurnRadius),
            Obj("CMB_StandTurnRate", gStandTurn),
            Obj("GroundProbeRef", probeRef));
        // Optional: only does anything with F4SE and the compiled CMB_HotkeyF4SE.pex.
        var hotkey = Script("CMB_HotkeyF4SE",
            Obj("Controller", quest),
            Obj("CMB_HotkeyCode", gHotkey));
        // Optional too: puts slot-57 gear back on after a ride (F4SE's GetWornItem).
        var gear = Script("CMB_GearRestoreF4SE",
            Obj("Controller", quest),
            Obj("CMB_BikeRiderArmor", armor),
            Obj("CMB_BikeRiderArmorFrame", armorFrame),
            Int("BikeSlotIndex", BikeSlotIndex),
            Int("LampSlotIndex", LampSlotIndex));

        quest.VirtualMachineAdapter = new QuestAdapter
        {
            Version = 6,
            ObjectFormat = 2,
            Scripts = new ExtendedList<ScriptEntry> { controller, hotkey, gear },
            Aliases = new ExtendedList<QuestFragmentAlias>
            {
                new QuestFragmentAlias
                {
                    Property = new ScriptObjectProperty
                    {
                        Name = "",
                        Object = new FormLink<IFallout4MajorRecordGetter>(quest.FormKey),
                        Alias = (short)playerAliasId,
                    },
                    Version = 6,
                    ObjectFormat = 2,
                    Scripts = new ExtendedList<ScriptEntry> { Script("CMB_PlayerAliasScript") },
                },
            },
        };

        return mod;
    }

    // ---------------------------------------------------------------------
    // Record helpers
    // ---------------------------------------------------------------------

    static GlobalFloat Global(Fallout4Mod mod, string editorId, float value)
    {
        var global = new GlobalFloat(mod.GetNextFormKey(), Fallout4Release.Fallout4)
        {
            EditorID = editorId,
            Data = value,
            OutputChar = true, // writes FNAM 'f'; xEdit and the CK treat it as required
        };
        mod.Globals.Add(global);
        return global;
    }

    // A hidden constant script effect for CMB_SwimWatchAbility (CMB_SwimWatchEffectScript).
    static MagicEffect WatchEffect(Fallout4Mod mod, string editorId, string name, Quest quest, bool wading)
    {
        var effect = mod.MagicEffects.AddNew(editorId);
        effect.Name = name;
        effect.Flags = MagicEffect.Flag.NoDuration | MagicEffect.Flag.NoMagnitude | MagicEffect.Flag.NoArea
            | MagicEffect.Flag.HideInUI | MagicEffect.Flag.Painless | MagicEffect.Flag.NoHitEvent;
        effect.Archetype = new MagicEffectArchetype { Type = MagicEffectArchetype.TypeEnum.Script };
        effect.CastType = CastType.ConstantEffect;
        effect.TargetType = TargetType.Self;
        effect.CastingSoundLevel = SoundLevel.Silent;
        effect.DualCastScale = 1;
        effect.VirtualMachineAdapter = wading
            ? Vmad(Script("CMB_SwimWatchEffectScript", Obj("Controller", quest), Bool("Wading", true)))
            : Vmad(Script("CMB_SwimWatchEffectScript", Obj("Controller", quest)));
        return effect;
    }

    // The ability's entry for a watch effect: it runs while `function` == 1 on the player.
    static Effect WatchEntry(MagicEffect effect, Condition.Function function) => new()
    {
        BaseEffect = effect.ToNullableLink(),
        Data = new EffectData { Magnitude = 0, Area = 0, Duration = 0 },
        Conditions = new ExtendedList<Condition>
        {
            new ConditionFloat
            {
                Data = new FunctionConditionData { Function = function, RunOnType = Condition.RunOnType.Subject },
                CompareOperator = CompareOperator.EqualTo,
                ComparisonValue = 1,
            },
        },
    };

    // A non-playable armor in the bike's slot showing one of the worn bike meshes.
    static Armor WornBike(Fallout4Mod mod, string addonId, string armorId, string maleModel, string femaleModel)
    {
        var arma = mod.ArmorAddons.AddNew(addonId);
        arma.BodyTemplate = new BodyTemplate { FirstPersonFlags = BikeSlot };
        arma.Race.SetTo(Vanilla.HumanRace);
        arma.Priority = new GenderedItem<byte>(0, 0);
        arma.WeightSliderEnabled = new GenderedItem<bool>(false, false);
        arma.WorldModel = new GenderedItem<Model?>(
            new Model { File = maleModel },
            new Model { File = femaleModel });

        var armor = mod.Armors.AddNew(armorId);
        armor.MajorFlags |= Armor.MajorFlag.NonPlayable;
        armor.Name = "Motorbike";
        armor.ObjectBounds = new ObjectBounds();
        armor.BipedBodyTemplate = new BipedBodyTemplate { FirstPersonFlags = BikeSlot | LampSlot };
        armor.Race.SetTo(Vanilla.HumanRace);
        armor.Armatures.Add(new ArmorAddonModel { AddonIndex = 0, ArmorAddon = arma.ToNullableLink() });
        armor.Value = 0;
        armor.Weight = 0;
        return armor;
    }

    // The headlamp's beam: a spotlight like the game's own power armor headlamp (test 31: with
    // attenuation 1/1/1 and 55 degrees ours lit nothing; the game's lights all have Constant 0,
    // Scalar 1, Exponent 2, FOV 70-100, radius 1420-2130), warm white, 30 m, 70 degrees, dynamic,
    // brighter than the stock lamp (fade 2); the second the shadow-casting kind. Hung on the lamp
    // nif's add-on nodes by the game, or placed as a reference by the controller script.
    const uint HeadlampNodeIndex = 31985;
    static Light Headlamp(Fallout4Mod mod, string editorId, bool shadow)
    {
        var light = mod.Lights.AddNew(editorId);
        light.ObjectBounds = new ObjectBounds();
        light.Time = -1;
        light.Radius = 2130;
        light.Color = System.Drawing.Color.FromArgb(0, 255, 241, 224);
        light.Flags = (Light.Flag)1 | (shadow ? Light.Flag.ShadowSpotlight : Light.Flag.NonShadowSpotlight);   // 1: Dynamic (it moves)
        light.FalloffExponent = 1.0f;
        light.FOV = 70.0f;
        light.NearClip = 10.0f;
        light.FlickerPeriod = 0.0f;
        light.FlickerIntensityAmplitude = 0.0f;
        light.FlickerMovementAmplitude = 0.0f;
        light.Constant = 0.0f;
        light.Scalar = 1.0f;
        light.Exponent = 2.0f;
        light.GodRaysNearClip = 0.0f;
        light.Value = 0;
        light.Weight = 0.0f;
        light.FadeValue = 2.0f;
        return light;
    }

    // The headlamp's add-on nodes ride in an unskinned nif of their own (CMB_BikeLamp.nif), a second
    // armor addon of the bike's armor: the game keeps an unskinned worn nif's nodes, not a skinned
    // one's (tests 30 and 31), and hangs the ADDN records' lights on them. Made after every record
    // with a fixed form id (the plugin's globals), so none of those move.
    static void AddLampAddon(Fallout4Mod mod, Armor armor, string addonId, string maleModel, string femaleModel)
    {
        var lampArma = mod.ArmorAddons.AddNew(addonId);
        lampArma.BodyTemplate = new BodyTemplate { FirstPersonFlags = LampSlot };
        lampArma.Race.SetTo(Vanilla.HumanRace);
        lampArma.Priority = new GenderedItem<byte>(0, 0);
        lampArma.WeightSliderEnabled = new GenderedItem<bool>(false, false);
        lampArma.WorldModel = new GenderedItem<Model?>(new Model { File = maleModel }, new Model { File = femaleModel });
        armor.Armatures.Add(new ArmorAddonModel { AddonIndex = (ushort)armor.Armatures.Count, ArmorAddon = lampArma.ToNullableLink() });
    }

    static AddonNode HeadlampNode(Fallout4Mod mod, string editorId, uint nodeIndex, Light light)
    {
        var node = mod.AddonNodes.AddNew(editorId);
        node.ObjectBounds = new ObjectBounds();
        node.NodeIndex = nodeIndex;
        node.Light.SetTo(light);
        node.MasterParticleSystemCap = 0;
        node.Flags = AddonNode.Flag.AlwaysLoaded;
        return node;
    }

    static Message MessageBox(Fallout4Mod mod, string editorId, string title, string text, params string[] buttons)
    {
        var msg = mod.Messages.AddNew(editorId);
        msg.Name = title;
        msg.Description = text;
        msg.Flags = Message.Flag.MessageBox;
        foreach (var b in buttons)
            msg.MenuButtons.Add(new MessageButton { Text = b });
        return msg;
    }

    static ObjectBounds Bounds(short halfX, short halfY, short minZ, short maxZ) => new()
    {
        First = new P3Int16((short)-halfX, (short)-halfY, minZ),
        Second = new P3Int16(halfX, halfY, maxZ),
    };

    static FormKey Placed(Fallout4Mod mod, Cell cell, string editorId, FormKey baseForm, P3Float position)
    {
        var placed = new PlacedObject(mod.GetNextFormKey(), Fallout4Release.Fallout4)
        {
            EditorID = editorId,
            Position = position,
            Rotation = new P3Float(0, 0, 0),
        };
        placed.Base.SetTo(baseForm);
        // Persistent: the scripts move these references around and need them loaded at all times.
        placed.MajorRecordFlagsRaw |= (int)PlacedObject.DefaultMajorFlag.Persistent;
        cell.Persistent.Add(placed);
        return placed.FormKey;
    }

    static void AddInteriorCell(Fallout4Mod mod, Cell cell)
    {
        // Interior cells live in block (id % 10), sub-block ((id / 10) % 10).
        var id = (int)cell.FormKey.ID;
        var blockNumber = id % 10;
        var subBlockNumber = (id / 10) % 10;
        var block = mod.Cells.Records.FirstOrDefault(b => b.BlockNumber == blockNumber);
        if (block == null)
        {
            block = new CellBlock { BlockNumber = blockNumber, GroupType = GroupTypeEnum.InteriorCellBlock };
            mod.Cells.Records.Add(block);
        }
        var subBlock = block.SubBlocks.FirstOrDefault(s => s.BlockNumber == subBlockNumber);
        if (subBlock == null)
        {
            subBlock = new CellSubBlock { BlockNumber = subBlockNumber, GroupType = GroupTypeEnum.InteriorCellSubBlock };
            block.SubBlocks.Add(subBlock);
        }
        subBlock.Cells.Add(cell);
    }

    // ---------------------------------------------------------------------
    // Script (VMAD) helpers
    // ---------------------------------------------------------------------

    static VirtualMachineAdapter Vmad(params ScriptEntry[] scripts) => new()
    {
        Version = 6,
        ObjectFormat = 2,
        Scripts = new ExtendedList<ScriptEntry>(scripts),
    };

    static ScriptEntry Script(string name, params ScriptProperty[] properties) => new()
    {
        Name = name,
        Flags = ScriptEntry.Flag.Local,
        Properties = new ExtendedList<ScriptProperty>(properties),
    };

    static ScriptObjectProperty Obj(string name, IMajorRecordGetter target) => Obj(name, target.FormKey);

    // Alias must be -1 for a plain object: with 0, a property pointing at a quest
    // would be read as that quest's alias 0 instead of the quest itself.
    static ScriptIntProperty Int(string name, int value) => new()
    {
        Name = name,
        Flags = ScriptProperty.Flag.Edited,
        Data = value,
    };

    static ScriptBoolProperty Bool(string name, bool value) => new()
    {
        Name = name,
        Flags = ScriptProperty.Flag.Edited,
        Data = value,
    };

    static SoundDescriptor EngineSound(Fallout4Mod mod, string editorId, string file, bool loop)
    {
        var sound = mod.SoundDescriptors.AddNew(editorId);
        sound.Category.SetTo(Vanilla.AudioCategorySFX);
        sound.OutputModel.SetTo(Vanilla.SOMMono02000); // mono, heard up to ~2000 units away
        sound.SoundFiles.Add($@"FX\CMB\{file}");     // relative to Data\Sound
        sound.Data = new SoundDescriptorStandardData { Priority = 128 };
        sound.LoopAndRumble = new SoundLoopAndRumble
        {
            Loop = loop ? SoundDescriptor.LoopType.Loop : SoundDescriptor.LoopType.None,
        };
        return sound;
    }

    static ScriptObjectProperty Obj(string name, FormKey target) => new()
    {
        Name = name,
        Flags = ScriptProperty.Flag.Edited,
        Object = new FormLink<IFallout4MajorRecordGetter>(target),
        Alias = -1,
    };

    // ---------------------------------------------------------------------
    // Read a plugin back and print it, to check what was written.
    // ---------------------------------------------------------------------

    static void Dump(string path)
    {
        using var mod = Fallout4Mod.CreateFromBinaryOverlay(path, Fallout4Release.Fallout4);
        var types = mod.EnumerateMajorRecords().ToDictionary(r => r.FormKey, r => r.Registration.ClassType.Name);
        Console.WriteLine($"{mod.ModKey}  masters: {string.Join(", ", mod.ModHeader.MasterReferences.Select(m => m.Master))}  " +
                          $"light: {mod.IsSmallMaster}  records: {types.Count}");
        foreach (var rec in mod.EnumerateMajorRecords().OrderBy(r => r.FormKey.ID))
        {
            Console.WriteLine($"  {rec.FormKey.ID:X6} {rec.Registration.ClassType.Name,-20} {rec.EditorID}");
            var vmad = rec switch
            {
                IActivatorGetter a => a.VirtualMachineAdapter,
                IContainerGetter c => c.VirtualMachineAdapter,
                IMagicEffectGetter m => m.VirtualMachineAdapter,
                IQuestGetter q => (IAVirtualMachineAdapterGetter?)q.VirtualMachineAdapter,
                _ => null,
            };
            if (vmad != null)
                foreach (var s in vmad.Scripts)
                    PrintScript(s, "      ", types);
            if (rec is IRaceGetter race)
            {
                if (!race.SubgraphAdditiveRace.IsNull)
                    Console.WriteLine($"      additive to {race.SubgraphAdditiveRace.FormKey}");
                foreach (var sg in race.Subgraphs)
                    Console.WriteLine($"      subgraph {sg.Role} {sg.Perspective} [{string.Join(", ", sg.ActorKeywords.Select(k => k.FormKey))}] " +
                                      $"targets [{string.Join(", ", sg.TargetKeywords.Select(k => k.FormKey))}] " +
                                      $"{sg.BehaviorGraph} paths [{string.Join(", ", sg.AnimationPaths)}]");
            }
            if (rec is IQuestGetter quest && quest.VirtualMachineAdapter != null)
                foreach (var alias in quest.VirtualMachineAdapter.Aliases)
                {
                    Console.WriteLine($"      alias {alias.Property.Alias} -> {alias.Property.Object.FormKey}");
                    foreach (var s in alias.Scripts)
                        PrintScript(s, "        ", types);
                }
        }
    }

    // Property lines read: "<name> = <FormKey> (alias <n>) <record type>".
    // tools/esp-generator/check_plugin.py parses this to compare against the .psc files.
    static void PrintScript(IScriptEntryGetter s, string indent, IReadOnlyDictionary<FormKey, string> types)
    {
        Console.WriteLine($"{indent}script {s.Name}");
        foreach (var p in s.Properties)
        {
            var value = p switch
            {
                IScriptObjectPropertyGetter o =>
                    $"{o.Object.FormKey} (alias {o.Alias}) {types.GetValueOrDefault(o.Object.FormKey, Vanilla.Describe(o.Object.FormKey))}",
                IScriptFloatPropertyGetter f => $"{f.Data} Float",
                IScriptIntPropertyGetter i => $"{i.Data} Int",
                IScriptBoolPropertyGetter b => $"{b.Data} Bool",
                _ => p.GetType().Name,
            };
            Console.WriteLine($"{indent}  {p.Name} = {value}");
        }
    }
}
