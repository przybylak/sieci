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
    public static readonly FormKey AmmoFlamerFuel = Fo4(0x0CAC78);

    // Record types of the vanilla forms above, for the property type check.
    public static string Describe(FormKey key) =>
        key == PlayerRef ? "PlacedNpc"
        : key == XMarker ? "Static"
        : key == HumanRace ? "Race"
        : key == SpeedMult || key == CarryWeight ? "ActorValueInformation"
        : key == Pipboy ? "Armor"
        : key == AnimArchetypePlayer ? "Keyword"
        : key == AmmoFlamerFuel ? "Ammunition"
        : "unknown";
}

public static class Program
{
    public const string PluginName = "CommonwealthMotorbike.esp";

    // Paths are relative to Data\Meshes. The user provides both files (docs/ASSETS.md):
    // the parked bike is an unmodified copy of the vanilla motorcycle, the worn
    // one is that mesh skinned to the Root bone in Outfit Studio.
    public const string ParkedBikeModel = @"CMB\CMB_BikeParked.nif";
    public const string WornBikeModel = @"CMB\CMB_BikeWorn.nif";
    public const string KeysModel = @"CMB\CMB_Keys.nif";

    // Biped slot the worn bike occupies; whatever else uses it gets unequipped
    // while riding. 58 clashed with Eli's Armour Compendium bags. 57 is an
    // "Unnamed" slot (60 would also be free in some setups, but it's the
    // slot named "Pipboy"). Change it here if another mod of yours uses 57.
    public const BipedObjectFlag BikeSlot = BipedObjectFlag.Unnamed57;

    public static int Main(string[] args)
    {
        if (args.Length == 2 && args[0] == "--dump")
        {
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
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(output))!);
        mod.WriteToBinary(output);
        Console.WriteLine($"Wrote {output}");
        Dump(output);
        return 0;
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
        var gRiderPose = Global(mod, "CMB_UseRiderPose", 0);
        var gCatchUp = Global(mod, "CMB_CatchUpDistance", 2500);
        var gBagCapacity = Global(mod, "CMB_BagCapacity", 60);
        var gHotkey = Global(mod, "CMB_HotkeyCode", 48);
        var gUseFuel = Global(mod, "CMB_UseFuel", 1);
        var gFuelDistance = Global(mod, "CMB_FuelDistance", 21000); // ~300 m per unit (about 70 units = 1 m)

        // --- What the bike burns ---
        var fuelItems = mod.FormLists.AddNew("CMB_FuelItems");
        fuelItems.Items.Add(new FormLink<IFallout4MajorRecordGetter>(Vanilla.AmmoFlamerFuel));

        // --- Keyword for the experimental rider pose ---
        var kwRider = mod.Keywords.AddNew("CMB_AnimArchetypeRider");
        kwRider.Type = Keyword.TypeEnum.AnimArchetype;
        kwRider.Color = System.Drawing.Color.FromArgb(0, 0, 0, 0); // CNAM is a required field

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
            Obj("CMB_AnimArchetypeRider", kwRider),
            Obj("AnimArchetypePlayer", Vanilla.AnimArchetypePlayer));
        // Optional: only does anything with F4SE and the compiled CMB_HotkeyF4SE.pex.
        var hotkey = Script("CMB_HotkeyF4SE",
            Obj("Controller", quest),
            Obj("CMB_HotkeyCode", gHotkey));

        quest.VirtualMachineAdapter = new QuestAdapter
        {
            Version = 6,
            ObjectFormat = 2,
            Scripts = new ExtendedList<ScriptEntry> { controller, hotkey },
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
                IScriptFloatPropertyGetter f => f.Data.ToString(),
                _ => p.GetType().Name,
            };
            Console.WriteLine($"{indent}  {p.Name} = {value}");
        }
    }
}
