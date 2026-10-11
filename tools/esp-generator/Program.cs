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
        : key == SpeedMult || key == CarryWeight ? "ActorValueInformation"
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

    // Paths are relative to Data\Meshes. tools/rider/build_bike_meshes.py makes both from
    // the vanilla motorcycle (docs/ASSETS.md): the parked bike is an unmodified copy, the
    // worn one is that mesh turned to face forward and skinned to the AnimObjectA bone.
    public const string ParkedBikeModel = @"CMB\CMB_BikeParked.nif";
    public const string WornBikeModel = @"CMB\CMB_BikeWorn.nif";
    public const string KeysModel = @"CMB\CMB_Keys.nif";

    // Biped slot the worn bike occupies; whatever else uses it gets unequipped
    // while riding. 58 clashed with Eli's Armour Compendium bags. 57 is an
    // "Unnamed" slot (60 would also be free in some setups, but it's the
    // slot named "Pipboy"). Change it here if another mod of yours uses 57.
    public const BipedObjectFlag BikeSlot = BipedObjectFlag.Unnamed57;
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
        object Call(string function) => new { type = "CallFunction", form = quest, scriptName = "CMB_ControllerScript", function, @params = Array.Empty<object>() };
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
                Switcher("Allow combat while riding", "Weapons and VATS stay usable while riding. Takes effect the next time you get on.", "CMB_AllowCombat"),
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

        // --- Worn bike ---
        var arma = mod.ArmorAddons.AddNew("CMB_BikeRiderAA");
        arma.BodyTemplate = new BodyTemplate { FirstPersonFlags = BikeSlot };
        arma.Race.SetTo(Vanilla.HumanRace);
        arma.Priority = new GenderedItem<byte>(0, 0);
        arma.WeightSliderEnabled = new GenderedItem<bool>(false, false);
        arma.WorldModel = new GenderedItem<Model?>(
            new Model { File = WornBikeModel },
            new Model { File = WornBikeModel });

        var armor = mod.Armors.AddNew("CMB_BikeRiderArmor");
        armor.MajorFlags |= Armor.MajorFlag.NonPlayable;
        armor.Name = "Motorbike";
        armor.ObjectBounds = new ObjectBounds();
        armor.BipedBodyTemplate = new BipedBodyTemplate { FirstPersonFlags = BikeSlot };
        armor.Race.SetTo(Vanilla.HumanRace);
        armor.Armatures.Add(new ArmorAddonModel { AddonIndex = 0, ArmorAddon = arma.ToNullableLink() });
        armor.Value = 0;
        armor.Weight = 0;

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
            Obj("CMB_EngineVolume", gEngineVolume));
        // Optional: only does anything with F4SE and the compiled CMB_HotkeyF4SE.pex.
        var hotkey = Script("CMB_HotkeyF4SE",
            Obj("Controller", quest),
            Obj("CMB_HotkeyCode", gHotkey));
        // Optional too: puts slot-57 gear back on after a ride (F4SE's GetWornItem).
        var gear = Script("CMB_GearRestoreF4SE",
            Obj("CMB_BikeRiderArmor", armor),
            Int("BikeSlotIndex", BikeSlotIndex));

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
                _ => p.GetType().Name,
            };
            Console.WriteLine($"{indent}  {p.Name} = {value}");
        }
    }
}
