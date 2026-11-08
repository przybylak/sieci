// Generates CommonwealthMotorbike.esp: every record the mod's scripts need,
// with scripts attached and all properties filled, so nobody has to build the
// plugin by hand in the Creation Kit.
//
//   dotnet run -c Release -- <output.esp>          write the plugin
//   dotnet run -c Release -- --dump <plugin.esp>   print what a plugin contains
//   dotnet run -c Release -- --look-ids look_ids.txt   write the save-stable ID list (appends only)
//   dotnet run -c Release -- --recipe-bench CMB_WorkbenchBike <output.esp>   an A/B plugin: the look recipes on CMB_WorkbenchBike
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
using System.Text.Json;

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
    // Test 47's knock-over kills (CMB_RamScript logs the player's experience around a kill; Mutagen's Fallout4
    // FormKeys: Experience 0002C9).
    public static readonly FormKey Experience = Fo4(0x0002C9);
    // Test 46's AP watch (CMB_ControllerScript logs AP, its rate and the rate's mult; Mutagen's
    // Fallout4 FormKeys: ActionPoints 0002D5, ActionPointsRate 0002D8, ActionPointsRateMult 000359).
    public static readonly FormKey ActionPoints = Fo4(0x0002D5);
    public static readonly FormKey ActionPointsRate = Fo4(0x0002D8);
    public static readonly FormKey ActionPointsRateMult = Fo4(0x000359);
    public static readonly FormKey Pipboy = Fo4(0x021B3B);
    public static readonly FormKey AnimArchetypePlayer = Fo4(0x06B508);
    public static readonly FormKey HumanRaceSubGraphData = Fo4(0x166729);
    public static readonly FormKey AmmoFlamerFuel = Fo4(0x0CAC78);
    public static readonly FormKey AudioCategorySFX = Fo4(0x0172A1);
    public static readonly FormKey SOMMono02000 = Fo4(0x07E5DC);
    // 2026-11-01a, the bike's own sounds besides the engine (test 47: "currently the sound used is default character
    // jump effect"; "sound when bike is crossing a water"). Borrowed from the game by reference, not copied (ASSETS.md
    // "Borrowed from the game"), each checked against Mutagen's Fallout4 FormKeys. The player's own footsteps, jumps and
    // landings: CMB_ControllerScript mutes the category while riding (MCM "Mute the rider's own jump and landing sounds").
    public static readonly FormKey AudioCategoryFSTplayer = Fo4(0x0F5FFC);
    // CMB_FxLandSounds: 0 light (PHYRubberTireL 1D3313), 1 heavy (PHYRubberTireH 1D3312), 2 the clunk on a big drop
    // (PHYMetalAutoMediumH 05BAD7), 3 into water (FSTnpcWaterJumpDown 03C7A9), 4 into water, heavy (PHYWaterSplash 0452CE).
    public static readonly FormKey[] FxLandSounds =
    {
        Fo4(0x1D3313), Fo4(0x1D3312), Fo4(0x05BAD7), Fo4(0x03C7A9), Fo4(0x0452CE),
    };
    // CMB_FxLandSoundsAlt (console: set CMB_FxLandPick to 1): 0 light (PHYRubberTireL 1D3313), 1 heavy
    // (FSTArmorPowerHardLandingImpactDirt 20A0B9), 2 the clunk (PHYMetalBarrelH 1A8550), 3 into water (CWaterMedium
    // 089380), 4 into water, heavy (FSTArmorPowerHardLandingImpactWater 20A0B8).
    public static readonly FormKey[] FxLandSoundsAlt =
    {
        Fo4(0x1D3313), Fo4(0x20A0B9), Fo4(0x1A8550), Fo4(0x089380), Fo4(0x20A0B8),
    };
    // CMB_FxWaterLoops (console: set CMB_FxWaterPick to 0-3): AMBWaterfallSplatterSmallLP 1E4F2D,
    // AMBWaterfallSplatterLargeLP 1E4F2C, AMBWaterStream01LPSD 03D0A7, AMBWaterfallChurn 1E4F1B.
    public static readonly FormKey[] FxWaterLoops =
    {
        Fo4(0x1E4F2D), Fo4(0x1E4F2C), Fo4(0x03D0A7), Fo4(0x1E4F1B),
    };
    public static readonly FormKey CurrentCompanionFaction = Fo4(0x023C01);
    // Races never knocked over by the bike (CMB_RamTooBig; Mutagen's Fallout4 FormKeys): super
    // mutants (SuperMutantRace 01A009) and behemoths (SupermutantBehemothRace 0BB7D9), deathclaws,
    // mirelurk queens, Liberty Prime, sentry bots (SentryBotRace 0AE0B7), yao guai, vertibirds, the
    // three turret races, radscorpions, brahmin, synth gorillas, power armor. Test 40: super mutants
    // and the sentry bot don't count; the smaller robots (protectrons, eyebots, Mr. Handy and Gutsy,
    // assaultrons) and the mutant hounds (FEVHoundRace 090C33, dogs) do, so they are not listed.
    // DLC races can't be listed without their masters: the plugin's size limit covers them.
    public static readonly FormKey[] TooBigToKnockOver =
    {
        Fo4(0x01A009), Fo4(0x0BB7D9), Fo4(0x01DB4A), Fo4(0x0E12A6), Fo4(0x108019), Fo4(0x0AE0B7), Fo4(0x0A0F2F),
        Fo4(0x0D77E3), Fo4(0x0B28D3), Fo4(0x0B1F08), Fo4(0x1A6D64), Fo4(0x0636AB), Fo4(0x02047E), Fo4(0x0D9804), Fo4(0x01D31E),
    };
    // The robots knocked over all the same (CMB_RamRobots; Mutagen's Fallout4 FormKeys): ProtectronRace
    // 0DFB33, EyeBotRace 0A563A, HandyRace 0359F4 (Mr. Handy, Mister Gutsy and Nanny share it),
    // AssaultronRace 0D8417. Test 42: the protectron's race reads large with No Knockdowns, so CMB_Slope.dll's
    // gates braked for it (7 times) where test 40 wanted it knocked over; the plugin lets the races listed
    // here past those two gates ([Ram] Robots). Sentry bots and Liberty Prime stay in TooBigToKnockOver;
    // the synths (SynthGen1/2) are humanoid and not listed; the robobrain is DLC and can't be listed.
    public static readonly FormKey[] Robots =
    {
        Fo4(0x0DFB33), Fo4(0x0A563A), Fo4(0x0359F4), Fo4(0x0D8417),
    };
    // 2026-11-07a, the customisation build (C1), each checked against Mutagen's Fallout4 FormKeys 3.4.0. The field kit's
    // furniture keywords: WorkbenchArmorA (12EA9B)'s KWDA as the tester's checker read it (WorkbenchArmor 0657FF,
    // FurnitureForce3rdPerson 0A56D8, AnimFurnWorkbenchArmorA 14D04F, FurnitureScaleActorToOne 12F848, Workbench_General
    // 091FD4). The kit's links (the controller): WorkshopItemKeyword 054BA6, LinkedWorkbenchContainerKeyword 1D1BEF,
    // LocTypeWorkshopSettlement 083C9A, the quest WorkshopParent 02058E, the actor value WorkshopPlayerOwned 00033C, the
    // toolbox's sound DRScToolboxBOpen 1B0652. The mirrors' loose mods: ObjectTypeLooseMod 135C17, the transform MiscMod01
    // 248769 (as the game's miscmod_mod_armor_*). The recipes: the six components and the perk Armorer01 04B254
    // (look_options.json names them; LookRecords checks its IDs against these).
    public static readonly FormKey WorkbenchArmor = Fo4(0x0657FF);
    public static readonly FormKey FurnitureForce3rdPerson = Fo4(0x0A56D8);
    public static readonly FormKey AnimFurnWorkbenchArmorA = Fo4(0x14D04F);
    public static readonly FormKey FurnitureScaleActorToOne = Fo4(0x12F848);
    public static readonly FormKey WorkbenchGeneral = Fo4(0x091FD4);
    public static readonly FormKey WorkshopItemKeyword = Fo4(0x054BA6);
    public static readonly FormKey LinkedWorkbenchContainerKeyword = Fo4(0x1D1BEF);
    public static readonly FormKey LocTypeWorkshopSettlement = Fo4(0x083C9A);
    public static readonly FormKey ObjectTypeLooseMod = Fo4(0x135C17);
    public static readonly FormKey WorkshopParent = Fo4(0x02058E);
    public static readonly FormKey WorkshopPlayerOwned = Fo4(0x00033C);
    public static readonly FormKey DRScToolboxBOpen = Fo4(0x1B0652);
    public static readonly FormKey MiscMod01 = Fo4(0x248769);
    public static readonly FormKey Armorer01 = Fo4(0x04B254);
    // 2026-11-09a (test 51: the field kit never worked): the game's armour bench itself, WorkbenchArmorA (FURN 12EA9B), the
    // field kit's mode 4 (the controller's WorkbenchArmorA).
    public static readonly FormKey WorkbenchArmorA = Fo4(0x12EA9B);
    public static readonly IReadOnlyDictionary<string, FormKey> Components = new Dictionary<string, FormKey>
    {
        ["c_Adhesive"] = Fo4(0x01FAA5), ["c_Cloth"] = Fo4(0x1223C7), ["c_Oil"] = Fo4(0x01FAB4),
        ["c_Steel"] = Fo4(0x01FABD), ["c_Glass"] = Fo4(0x01FAA4), ["c_Screws"] = Fo4(0x03D294),
    };
    public static readonly IReadOnlyDictionary<string, FormKey> Perks = new Dictionary<string, FormKey> { ["Armorer01"] = Armorer01 };

    // Record types of the vanilla forms above, for the property type check.
    public static string Describe(FormKey key) =>
        key == PlayerRef ? "PlacedNpc"
        : key == XMarker ? "Static"
        : key == HumanRace || TooBigToKnockOver.Contains(key) || Robots.Contains(key) ? "Race"
        : key == SpeedMult || key == CarryWeight || key == FallingDamageMod || key == Health || key == Experience
            || key == ActionPoints || key == ActionPointsRate || key == ActionPointsRateMult ? "ActorValueInformation"
        : key == WorkshopPlayerOwned ? "ActorValueInformation"
        : key == Pipboy ? "Armor"
        : key == AnimArchetypePlayer || key == WorkbenchArmor || key == FurnitureForce3rdPerson || key == AnimFurnWorkbenchArmorA
            || key == FurnitureScaleActorToOne || key == WorkbenchGeneral || key == WorkshopItemKeyword
            || key == LinkedWorkbenchContainerKeyword || key == LocTypeWorkshopSettlement || key == ObjectTypeLooseMod ? "Keyword"
        : key == WorkshopParent ? "Quest"
        : key == WorkbenchArmorA ? "Furniture"
        : key == DRScToolboxBOpen ? "SoundDescriptor"
        : key == MiscMod01 ? "Transform"
        : Components.Values.Contains(key) ? "Component"
        : key == Armorer01 ? "Perk"
        : key == AmmoFlamerFuel ? "Ammunition"
        : key == AudioCategorySFX || key == AudioCategoryFSTplayer ? "SoundCategory"
        : FxLandSounds.Contains(key) || FxLandSoundsAlt.Contains(key) || FxWaterLoops.Contains(key) ? "SoundDescriptor"
        : key == SOMMono02000 ? "SoundOutputModel"
        : key == CurrentCompanionFaction ? "Faction"
        : "unknown";
}

// 2026-11-02a (test 48: the landing and water sounds played but went unheard, 13-37 dB under their files): the bike
// sounds' own records over the game's own sound files, by path (nothing is copied: the strings are the game's records'
// own, as the tester's Fallout4.esm stores them, letter case and all, so the game resolves them the same way). Each
// follows the game's record named beside it in all but four fields: our category AudioCategorySFX (0172A1, as the
// engine's), our output model CMB_SOMMonoFx, a static attenuation of 0, and no "alternate sound for". The frequency
// shift and variance and the dB variance are the game's record's, so the two differ only in those four (a clean A/B:
// MCM "Bike sounds through the mod's own records").
public static class FxOwn
{
    public sealed record Sound(string Id, string Follows, string[] Files, bool Loop, sbyte Shift, sbyte Variance, byte DbVariance);

    // In the order they are made (0x89E-0x8AA).
    public static readonly Sound[] Records =
    {
        new("CMB_FxTyreLightSD", "PHYRubberTireL 1D3313",
            new[] { @"data\Sound\FX\PHY\RubberTire\PHY_Rubber_Tire_L_01.wav", @"data\Sound\FX\PHY\RubberTire\PHY_Rubber_Tire_L_02.wav",
                    @"data\Sound\FX\PHY\RubberTire\PHY_Rubber_Tire_L_03.wav" }, false, 0, 5, 4),
        new("CMB_FxTyreHeavySD", "PHYRubberTireH 1D3312",
            new[] { @"data\Sound\FX\PHY\RubberTire\PHY_Rubber_Tire_H_02.wav", @"data\Sound\FX\PHY\RubberTire\PHY_Rubber_Tire_H_03.wav",
                    @"data\Sound\FX\PHY\RubberTire\PHY_Rubber_Tire_H_01.wav" }, false, 0, 4, 4),
        new("CMB_FxClunkSD", "PHYMetalAutoMediumH 05BAD7",
            new[] { @"data\Sound\FX\PHY\MetalAuto\PHY_Metal_Auto_Medium_H_01.wav", @"data\Sound\FX\PHY\MetalAuto\PHY_Metal_Auto_Medium_H_02.wav",
                    @"data\Sound\FX\PHY\MetalAuto\PHY_Metal_Auto_Medium_H_03.wav", @"data\Sound\FX\PHY\MetalAuto\PHY_Metal_Auto_Medium_H_04.wav" }, false, 0, 12, 2),
        // 2026-11-06a (test 49's check, Q-L): FSTnpcWaterJumpDown names Data\Sound\FX\FST\Water\Land\..., a folder that
        // isn't in any of the game's archives (the 2026-11-02a build played silence); the game has the two files only
        // under sound\fx\fst\player\water\, so this record no longer follows a game record's files: the same two files
        // where they are, written as the records above write theirs (.wav; the game resolves the .xwm).
        new("CMB_FxSplashSD", "the game's jump-down files, test 49: the old path isn't in the game",
            new[] { @"Data\Sound\FX\FST\Player\Water\FST_Water_Jump_Down_01.wav", @"Data\Sound\FX\FST\Player\Water\FST_Water_Jump_Down_02.wav" }, false, 0, 3, 0),
        // 2026-11-06a (test 49's check, Q-L): PHYWaterSplash names PHY_Water_M_01, a file that isn't in the game; the
        // game's medium water splash files instead (CWaterMedium's strings, as CMB_FxSplashMediumSD below), the fields as
        // before (variance 5, dB variance 2).
        new("CMB_FxSplashHeavySD", "the game's medium water splash files (CWaterMedium 089380's strings), test 49: PHYWaterSplash's file isn't in the game",
            new[] { @"Data\Sound\FX\PHY\Generic\PHY_Generic_Water_Medium_01.wav", @"Data\Sound\FX\PHY\Generic\PHY_Generic_Water_Medium_02.wav",
                    @"Data\Sound\FX\PHY\Generic\PHY_Generic_Water_Medium_03.wav" }, false, 0, 5, 2),
        new("CMB_FxThudHeavySD", "FSTArmorPowerHardLandingImpactDirt 20A0B9",
            new[] { @"data\Sound\FX\FST\ArmorPower\FST_ArmorPower_Land_3D_Dirt_02.wav", @"data\Sound\FX\FST\ArmorPower\FST_ArmorPower_Land_3D_Dirt_03.wav",
                    @"data\Sound\FX\FST\ArmorPower\FST_ArmorPower_Land_3D_Dirt_01.wav" }, false, 0, 5, 1),
        new("CMB_FxClunkBarrelSD", "PHYMetalBarrelH 1A8550",
            new[] { @"data\Sound\FX\PHY\MetalBarrel\PHY_Metal_Barrel_H_01.wav", @"data\Sound\FX\PHY\MetalBarrel\PHY_Metal_Barrel_H_02.wav",
                    @"data\Sound\FX\PHY\MetalBarrel\PHY_Metal_Barrel_H_03.wav", @"data\Sound\FX\PHY\MetalBarrel\PHY_Metal_Barrel_H_04.wav" }, false, 0, 10, 6),
        new("CMB_FxSplashMediumSD", "CWaterMedium 089380",
            new[] { @"Data\Sound\FX\PHY\Generic\PHY_Generic_Water_Medium_01.wav", @"Data\Sound\FX\PHY\Generic\PHY_Generic_Water_Medium_02.wav",
                    @"Data\Sound\FX\PHY\Generic\PHY_Generic_Water_Medium_03.wav" }, false, 0, 7, 3),
        new("CMB_FxThudWaterSD", "FSTArmorPowerHardLandingImpactWater 20A0B8",
            new[] { @"data\Sound\FX\FST\ArmorPower\FST_ArmorPower_Land_3D_Water_02.wav", @"data\Sound\FX\FST\ArmorPower\FST_ArmorPower_Land_3D_Water_03.wav",
                    @"data\Sound\FX\FST\ArmorPower\FST_ArmorPower_Land_3D_Water_01.wav" }, false, 0, 5, 1),
        new("CMB_FxWaterSprayLPSD", "AMBWaterfallSplatterSmallLP 1E4F2D",
            new[] { @"data\Sound\FX\AMB\Waterfall\AMB_WaterfallSplatter_Small_02_LP.wav", @"data\Sound\FX\AMB\Waterfall\AMB_WaterfallSplatter_Small_01_LP.wav" }, true, 15, 6, 0),
        new("CMB_FxWaterSprayLargeLPSD", "AMBWaterfallSplatterLargeLP 1E4F2C",
            new[] { @"data\Sound\FX\AMB\Waterfall\AMB_WaterfallSplatter_Large_01_LP.wav", @"data\Sound\FX\AMB\Waterfall\AMB_WaterfallSplatter_Large_02_LP.wav" }, true, -15, 6, 0),
        // 2026-11-06a (test 49's check, Q-L: AMBWaterStream01LPSD's amb_water_stream_01_lp isn't in the game): renamed
        // from CMB_FxWaterStreamLPSD, the mod's own wet-road loop, shipped loose at Data\Sound\FX\CMB\CMB_FxWaterRoadLP.wav
        // and named relative to Data\Sound as the engine's 13 name theirs. Slot 2 of CMB_FxWaterLoopsOwn as before.
        new("CMB_FxWaterRoadLPSD", "the mod's own wet-road loop (Pixabay 101246)",
            new[] { @"FX\CMB\CMB_FxWaterRoadLP.wav" }, true, 0, 0, 0),
        new("CMB_FxWaterChurnLPSD", "AMBWaterfallChurn 1E4F1B",
            new[] { @"data\Sound\FX\AMB\Waterfall\AMB_Waterfall_Churn_02_LP.wav", @"data\Sound\FX\AMB\Waterfall\AMB_Waterfall_Churn_01_LP.wav" }, true, 0, 6, 0),
    };

    // The lists, in the borrowed lists' slots (Vanilla.FxLandSounds, FxLandSoundsAlt, FxWaterLoops).
    public static readonly string[] Land = { "CMB_FxTyreLightSD", "CMB_FxTyreHeavySD", "CMB_FxClunkSD", "CMB_FxSplashSD", "CMB_FxSplashHeavySD" };
    public static readonly string[] LandAlt = { "CMB_FxTyreLightSD", "CMB_FxThudHeavySD", "CMB_FxClunkBarrelSD", "CMB_FxSplashMediumSD", "CMB_FxThudWaterSD" };
    public static readonly string[] Water = { "CMB_FxWaterSprayLPSD", "CMB_FxWaterSprayLargeLPSD", "CMB_FxWaterRoadLPSD", "CMB_FxWaterChurnLPSD" };
    // 2026-11-06a (test 49: the landings' metal clunk): CMB_FxLandSoundsDull, the MCM's "Landing sounds without metal":
    // the light and heavy tyre, the PA dirt thud, the splash, the heavy splash and the PA water thud.
    public static readonly string[] LandDull = { "CMB_FxTyreLightSD", "CMB_FxTyreHeavySD", "CMB_FxThudHeavySD", "CMB_FxSplashSD", "CMB_FxSplashHeavySD", "CMB_FxThudWaterSD" };

    // 2026-11-09a (test 50: the wet road heard as static): the gentle wet-road loop, the mod's own (the same recording as
    // CMB_FxWaterRoadLPSD, less hiss and more body), shipped loose at Data\Sound\FX\CMB\CMB_FxWaterRoadSoftLP.wav and named
    // relative to Data\Sound as that one. Not in Records (it would move every later ID) and in no list: made at 0xBF3,
    // after C2's block, and played by CMB_FxWaterLoop 3 through the controller's CMB_FxWaterRoadSoft.
    public static readonly Sound WaterRoadSoft = new("CMB_FxWaterRoadSoftLPSD", "the mod's own gentle wet-road loop (Pixabay 101246)",
        new[] { @"FX\CMB\CMB_FxWaterRoadSoftLP.wav" }, true, 0, 0, 0);
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
    // The first-person bike (2026-11-01a): an unskinned copy of the riding bike, shown in first person only.
    public const string BikeViewModel = @"CMB\CMB_BikeView.nif";

    // Biped slot the worn bike occupies; whatever else uses it gets unequipped
    // while riding. 58 clashed with Eli's Armour Compendium bags. 57 is an
    // "Unnamed" slot (60 would also be free in some setups, but it's the
    // slot named "Pipboy"). Change it here if another mod of yours uses 57.
    public const BipedObjectFlag BikeSlot = BipedObjectFlag.Unnamed57;
    // F4SE counts slots from 30: slot 57 is index 27, the flag's bit number.
    public static int BikeSlotIndex => System.Numerics.BitOperations.TrailingZeroCount((uint)BikeSlot);

    public static int Main(string[] args)
    {
        // 2026-11-08a: `--look-build <build>` first makes the look as that build had it: `--look-build 2026-11-07a` drops
        // every C2 entry of look_options.json, so the ESP and the MCM's files are 2026-11-07a's byte for byte (the off
        // value of the C2 build). The rest of the arguments as without it.
        if (args.Length >= 2 && args[0] == "--look-build")
        {
            if (!LookRecords.Builds.Contains(args[1]))
            {
                Console.Error.WriteLine($"--look-build {args[1]}: look_options.json knows {string.Join(" and ", LookRecords.Builds)}.");
                return 1;
            }
            LookRecords.Through = args[1];
            args = args[2..];
        }
        // 2026-11-09a (test 51, Q-K2): `--recipe-bench CMB_WorkbenchBike` first gives the 263 look recipes their BNAM back
        // (CMB_WorkbenchBike, as 2026-11-08a's): an A/B ESP only, never shipped. The rest of the arguments as without it.
        if (args.Length >= 2 && args[0] == "--recipe-bench")
        {
            if (args[1] != "CMB_WorkbenchBike")
            {
                Console.Error.WriteLine($"--recipe-bench {args[1]}: only CMB_WorkbenchBike (the look's own bench keyword).");
                return 1;
            }
            LookRecords.RecipeBench = true;
            args = args[2..];
        }
        if (args.Length == 2 && args[0] == "--dump")
        {
            Dump(args[1]);
            return 0;
        }
        // 2026-11-07a: tools/esp-generator/look_ids.txt, the save-stable IDs (appends only; check_plugin.py compares).
        if (args.Length == 2 && args[0] == "--look-ids")
        {
            LookRecords.WriteIds(Build(), args[1]);
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
        CheckSoundsReadBack(mod, output);
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
        // 2026-11-07a, the Look section: a control on a global (a switcher, or a stepper or dropdown of names), and MCM's
        // group keys ("Free customising" shows the per-slot choices: groupControl 1 on it, groupCondition 1 on them).
        var lookTable = LookRecords.LoadTable();
        var lookSlots = LookRecords.ReadSlots(lookTable).ToDictionary(s => s.Key);
        string[] Names(string slot) => lookSlots[slot].Options.Select(o => o.Name).ToArray();
        // 2026-11-08a: and a slider (range: min, max, step) in the group.
        object Look(string type, string text, string help, string global, string[]? options = null, int? groupControl = null, int? groupCondition = null,
                    (float Min, float Max, float Step)? range = null)
        {
            var c = new Dictionary<string, object> { ["type"] = type, ["text"] = text, ["help"] = help };
            if (groupControl is int gc)
                c["groupControl"] = gc;
            if (groupCondition is int g)
                c["groupCondition"] = g;
            c["valueOptions"] = range is var (min, max, step)
                ? new { min, max, step, sourceType = "GlobalValue", sourceForm = Form(Rec(global)) }
                : options == null ? Global(global) : new { options, sourceType = "GlobalValue", sourceForm = Form(Rec(global)) };
            return c;
        }
        // The Look section: 2026-11-07a's 11 controls, and since 2026-11-08a 20 (the crude switch outside the free-mode group;
        // in it the hue and shade after Paint, the rims, tyres and the plate's four after Mirrors). `--look-build 2026-11-07a`
        // writes 07a's 11 as they were.
        bool c2 = lookSlots.ContainsKey("Rims");
        var lookSection = new List<object>
        {
            Section("Look"),
            Look("switcher", "Customise at the bike", "A Customise button in the parked bike's menu: the field kit comes out of the side bag and you change the bike's badges, paint and mirrors at the armour menu. Off: no button, and the bike looks as it came.",
                "CMB_LookOn"),
            // 2026-11-09a (test 51: the field kit never worked): with C2's block a 5th option, the game's armour bench (the
            // controller's WorkbenchArmorA), and the toolbox ones named as tests.
            c2 ? Look("stepper", "Field kit", "Automatic uses an armour bench beside the bike, then the game's own armour bench if the first one's menu closes at once, and remembers the one that worked (its menu stayed open, or you made a change). The others force one: the toolbox ones are tests only (the game's toolbox can't be sat in).",
                     "CMB_KitMode", new[] { "Automatic", "Toolbox (a test: it can't be sat in)", "Toolbox, bench keyword (a test)", "Armour bench", "The game's armour bench" })
               : Look("stepper", "Field kit", "Automatic tries the toolbox, then an armour bench, and remembers the one that worked. The others force one (for a test).",
                     "CMB_KitMode", new[] { "Automatic", "Toolbox", "Toolbox (armour bench keyword)", "Armour bench" }),
            Look("switcher", "Parts from the side bag", "Outside your settlements the field kit uses the side bag's components as well as yours. Off: only yours (and a settlement's workshop).",
                "CMB_KitBagLink"),
        };
        if (c2)
            lookSection.Add(Look("switcher", "Crude plate texts", "Crude wasteland humour and mild swearing among the plate texts at the field kit. Off: they aren't offered, and a plate wearing one shows its own text (at the next getting on, activation or Apply).",
                "CMB_LookPlateCrude"));
        lookSection.AddRange(new[]
        {
            Look("switcher", "Free customising (no field kit, no cost)", "Choose the look here instead: the choices below, then \"Apply the look\". No field kit and no components. Off: the choices are hidden, and the bike keeps the look it has.",
                "CMB_LookFree", groupControl: 1),
            Look("dropdown", "Tank badge, left", "The badge on the tank's left side (Stock: the winged wheel, as it came).", "CMB_Look_TankL", Names("TankL"), groupCondition: 1),
            Look("dropdown", "Tank badge, right", "The badge on the tank's right side. \"Same as the left\" follows the left one.", "CMB_Look_TankR", Names("TankR"), groupCondition: 1),
            Look("dropdown", "Rear fender badge", "A badge on the rear fender (None: as it came).", "CMB_Look_Fender", Names("Fender"), groupCondition: 1),
            Look("dropdown", "Paint", "The tank's and fenders' paint and the coachline (Factory: the oxblood, as it came).", "CMB_Look_Paint", Names("Paint"), groupCondition: 1),
        });
        if (c2)
            lookSection.AddRange(new[]
            {
                // 2026-11-09a (test 51: Free colour "didn't do anything"): moving either chooses Free colour (the controller's
                // HueFree, CMB_LookOptions bit 32).
                Look("slider", "Paint hue", "The colour of the Free colour paint, round the colour wheel (0 red, 120 green, 240 blue). Moving it chooses Paint \"Free colour\" when you Apply (or at the next getting on).",
                    "CMB_LookHue", groupCondition: 1, range: (0, 359, 1)),
                Look("stepper", "Paint shade", "How deep or pale the Free colour paint is. Moving it chooses Paint \"Free colour\" when you Apply (or at the next getting on).", "CMB_LookShade",
                    lookTable.GetProperty("hue_palette").GetProperty("shades").EnumerateArray().Select(x => x[0].GetString()!).ToArray(), groupCondition: 1),
            });
        lookSection.Add(Look("stepper", "Mirrors", "The stock mirrors, mirrors under the bars (egg or D), or none.", "CMB_Look_Mirrors", Names("Mirrors"), groupCondition: 1));
        if (c2)
            lookSection.AddRange(new[]
            {
                Look("dropdown", "Rims", "The wheels' style and finish (Stock: the cast wheels, as they came). Body colour follows the paint.", "CMB_Look_Rims", Names("Rims"), groupCondition: 1),
                Look("stepper", "Tyres", "Black (as they came), whitewalls or a red line.", "CMB_Look_Tyres", Names("Tyres"), groupCondition: 1),
                Look("dropdown", "Plate", "The licence plate's design (Stock: the plain plate, as it came).", "CMB_Look_Plate", Names("Plate"), groupCondition: 1),
                Look("dropdown", "Plate text", "The plate's lettering. \"The plate's own\" is the design's; the crude ones show as the plate's own while \"Crude plate texts\" is off.",
                    "CMB_Look_PlateText", Names("PlateText"), groupCondition: 1),
                Look("dropdown", "Plate letters", "The letters' colour (\"The plate's own\": the design's).", "CMB_Look_PlateInk", Names("PlateInk"), groupCondition: 1),
                Look("dropdown", "Plate background", "The plate's colour (\"The plate's own\": the design's).", "CMB_Look_PlateBack", Names("PlateBack"), groupCondition: 1),
            });
        lookSection.AddRange(new[]
        {
            Look("dropdown", "Faction set", c2 ? "Sets the paint, all three badges and, for some factions, the plate to one faction's when you press Apply."
                                              : "Sets the paint and all three badges to one faction's when you press Apply.", "CMB_LookFactionSet",
                LookRecords.ReadSets(lookTable).Select(x => x.Name).ToArray(), groupCondition: 1),
            new Dictionary<string, object>
            {
                ["type"] = "button", ["text"] = "Apply the look",
                ["help"] = "Puts these choices on the bike now (the ridden bike at the next getting on).",
                ["groupCondition"] = 1, ["action"] = Call("LookApply"),
            },
        });

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
                // 2026-11-09a (test 50: obstacle detection too early): Caution, only with C2's block (the ESP's 0xBF1).
                c2 ? Slider("Caution (how early the bike eases off for obstacles, %)", "50, the default: the bike eases off from about 7 m at full speed and the throttle is gone at about 5 m; a post ahead is still found in time to steer round it. Higher: further from the obstacle (60: as the 2026-11-09a build, from about 8 m, the throttle gone at 6 m; 100: as the 2026-11-08a build, from about 11 m). A save keeps the value it has. Needs F4SE and the CMB_Slope.dll plugin.",
                    "CMB_Caution", 50, 100, 5) : null!,
                Slider("Bike tilts with the ground (max degrees)", "While riding, the bike and the rider pitch with the ground by at most this much (needs F4SE and the CMB_Slope.dll plugin; 45 follows any slope you can climb). Takes effect the next time you get on.",
                    "CMB_MaxTilt", 0, 50, 1),
                Switcher("Allow combat while riding", "Weapons and VATS stay usable while riding. Takes effect the next time you get on.", "CMB_AllowCombat"),
                Switcher("Bike in first person", "Shows the bike under you in first person (needs F4SE and CMB_Slope.dll). Takes effect the next time you get on.", "CMB_FirstPersonBike"),
                Slider("Look down on getting into first person (deg)", "Each time you go into first person on the bike, the view eases down this far so the dial and bars are in sight; look up whenever you like. 0 = the view left as it is (as before). Needs F4SE and CMB_Slope.dll.",
                    "CMB_ViewTip", 0, 45, 1),
                Slider("Field of view riding in first person", "The game's field of view while you ride in first person (more shows more of the bike, and widens the world too); back to yours as you get off or leave first person. 0 = your own, as before. Needs F4SE and CMB_Slope.dll.",
                    "CMB_ViewFov", 0, 120, 5),
                Slider("Eye forward on the bike", "Moves your seat in first person forward (+) or back (-), in game units. 0 = the plugin's EyeAt. At once.",
                    "CMB_ViewEyeForward", -30, 30, 1),
                Slider("Eye height on the bike", "Lower (-) brings the bike higher into view under you (its wheels lift off the road by as much in first person), higher (+) sinks it. 0 = the plugin's EyeAt. At once.",
                    "CMB_ViewEyeUp", -30, 20, 1),
                Switcher("Thrown off when hit", "A big hit from an enemy knocks you off the bike, so you can fight back. Off: you keep riding; a hint says how to get off when a fight starts.", "CMB_DismountOnHit"),
                Switcher("Power attacks throw you off", "On: an enemy's power attack knocks you off whatever it costs you (the 2026-11-02a build). Off: a power attack is a hit like any other: it knocks you off only when it takes the Big hit share of your health. Explosions always do. Needs \"Thrown off when hit\".", "CMB_KnockOffPower"),
                Switcher("Steady in the saddle", "Hits don't stagger you while riding (a stagger plays the standing animation, and the bike hangs round your hips). Explosions, and power attacks with \"Power attacks throw you off\" on, still knock you off with \"Thrown off when hit\" on. Off: staggered as on foot.", "CMB_RiderSteady"),
                Slider("Pose re-check pause after a hit (s)", "A hit, a stagger or an item used while riding can play a standing animation for a moment: that is a reaction, not the seated pose lost, so the pose isn't applied again for this long after one. 0 = applied again at any standing footstep, as before.",
                    "CMB_PoseReactionWindow", 0, 5, 0.5f),
                Slider("Big hit (% of max health)", "How much of your max health a hit (or several within about a second) must take to knock you off. Explosions always do, and power attacks with \"Power attacks throw you off\" on. 0 = any hit. Not in the first 3 seconds after getting on.",
                    "CMB_KnockOffDamage", 0, 50, 5),
                Switcher("Knock enemies over", "Hostile people, creatures and smaller robots the bike hits at speed are knocked over and take a little damage, and the bike loses some speed at each (needs F4SE and the CMB_Slope.dll plugin). Never companions, essential characters, anyone in power armor or the big ones (super mutants, behemoths, deathclaws, sentry bots, ...). Off: the bike brakes for them as for anyone.", "CMB_RamEnemies"),
                Slider("Knock over from (speed)", "How fast the bike must be going, in game units a second (riding speed is about 900 at Speed 250%). Slower, it brakes for them.",
                    "CMB_RamMinSpeed", 100, 1500, 50),
                Slider("Knock-over damage (% of their health)", "At riding speed; half that at the slowest, up to one and a half times faster. It takes their last point of health only with the setting below. 0 = none.",
                    "CMB_RamDamage", 0, 50, 5),
                Switcher("Knock-overs can kill", "A knock-over that takes an enemy's last health kills it, and the kill is yours: quests and the rest as if you had shot it, and the experience with \"Kill experience\" below on. Never companions or essential characters (they aren't knocked over at all). Off: the bike leaves them at their last point of health.", "CMB_RamKills"),
                Slider("Kill experience", "What a kill by the bike gives you: 1 = the game's own experience, as for a kill of yours (the bike's last hit is yours); 2 = the same another way, should 1 give none; 0 = none, as before.",
                    "CMB_RamKillXP", 0, 2, 1),
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
                Slider("Engine volume", "0 = silent. The engine follows it as you ride.", "CMB_EngineVolume", 0, 100, 5),
                Slider("Bike effects volume", "Landings and riding through water (the game's own sound files for now). 0 = none. The water follows it at once, a landing at the next one.",
                    "CMB_FxVolume", 0, 100, 5),
                Switcher("Bike sounds through the mod's own records", "Landings and the water through the mod's own sound records over the game's sound files: heard at the riding camera's distance. Off: the game's own records, as the 2026-11-01a build (much quieter: they fade with the camera's distance and carry their own attenuation): the landings only with \"Landing sounds without metal\" off, the water only with \"Water sound loop\" on its first choice (the others are the mod's own records either way). Landings at once, the water the next time you get on.", "CMB_FxOwnSounds"),
                Slider("Landing loudness range (dB)", "How far under the hardest landing the softest one sounds. 10 by default; 18 as the 2026-11-01a build; smaller makes small drops louder.",
                    "CMB_FxLandRange", 0, 30, 1),
                Switcher("Landing sounds without metal", "On: a tyre thump, and on big drops a heavy dull thud under it; into water a splash, and on big drops a heavier one with a thud. Off: as the 2026-11-02a build, a metal clunk on big drops.", "CMB_FxLandDull"),
                Switcher("Landing sound", "A tyre thump when the bike lands, louder the higher the drop, a heavier thud on big ones, a splash into water. Without F4SE one level.", "CMB_FxLandOn"),
                Switcher("Water sound", "Spray while riding through shallow water, by speed and depth (needs F4SE and the CMB_Slope.dll plugin). Takes effect the next time you get on.", "CMB_FxWaterOn"),
                // 2026-11-09a (test 50: the wet road heard as static): a 4th option, the gentle wet road (0xBF3), only with
                // C2's block.
                new
                {
                    type = "stepper", text = "Water sound loop",
                    help = c2 ? "Which water loop plays while riding through water. The first is the 2026-11-02a build's (the console's CMB_FxWaterPick); \"Wet road, gentle\" (since 2026-11-09a) is the mod's wet road with less hiss and more body. Takes effect the next time you get on."
                              : "Which water loop plays while riding through water. The first is the 2026-11-02a build's (the console's CMB_FxWaterPick). Takes effect the next time you get on.",
                    valueOptions = new { options = c2 ? new[] { "As the 2026-11-02a build (spray)", "Churning water", "Wet road (the mod's own)", "Wet road, gentle" }
                                                      : new[] { "As the 2026-11-02a build (spray)", "Churning water", "Wet road (the mod's own)" }, sourceType = "GlobalValue", sourceForm = Form(Rec("CMB_FxWaterLoop")) },
                },
                Switcher("Mute the rider's own jump and landing sounds", "While riding, your character's own footstep, jump and landing sounds are silent (the bike's take their place). Takes effect the next time you get on.", "CMB_FxMuteRider"),
                Section("Headlamp"),
                new
                {
                    type = "stepper", text = "Headlamp",
                    help = "The bike's headlamp (needs F4SE and the CMB_Slope.dll plugin): off, on while riding, or on at night (19:00 to 6:30). The hotkey below switches it while you ride.",
                    valueOptions = new { options = new[] { "Off", "On", "On at night" }, sourceType = "GlobalValue", sourceForm = Form(Rec("CMB_HeadlampMode")) },
                },
                new { type = "hotkey", id = "ToggleHeadlamp", text = "Headlamp on / off", help = "Switches the headlamp while riding, until you get off or the next dusk or dawn; the setting above stays as it is." },
                Switcher("Headlamp casts shadows", "The beam casts shadows (costlier: the game runs only a few shadow lights at once). Takes effect the next time you get on.", "CMB_HeadlampShadows"),
                Switcher("Tail lamp lights the road", "The tail lamp casts a small red light behind the bike, brighter while you brake (needs F4SE and CMB_Slope.dll). Takes effect the next time you get on.", "CMB_TailLightMode"),
            }.Concat(lookSection).Concat(new object[]
            {
                Section("Hotkeys"),
                new { type = "hotkey", id = "ToggleRide", text = "Get on / off / call the bike", help = "If you use this, set the built-in hotkey below to 0 so the key doesn't fire twice." },
                Slider("Built-in hotkey (scan code)", "The F4SE hotkey that works without MCM. 48 = B, 34 = G, 47 = V, 0 = off. Press Apply after changing it.",
                    "CMB_HotkeyCode", 0, 211, 1),
                Slider("Brake key (scan code)", "Brakes while riding, as S does, and holds the bike still once stopped (S still backs up). A DirectInput scan code: 57 = Space, 42 = Left Shift, 29 = Left Ctrl, 56 = Left Alt, 45 = X, 46 = C, 0 = none (only S brakes). The log names the key it read. Takes effect the next time you get on.",
                    "CMB_BrakeKey", 0, 211, 1),
                Button("Apply built-in hotkey", "Re-registers the built-in hotkey after changing it.", "RefreshHotkey"),
                Section("Troubleshooting"),
                Button("Give me the keys", "For alternative starts that skip the Pip-Boy: hands over the Motorbike Keys now.", "ForceGiveKeys"),
                Button("Emergency reset", "Gets you off the bike and undoes everything riding changed: speed, controls, animations, hidden companions.", "EmergencyReset"),
            }).Where(c => c != null).ToArray(),
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
        // The files go to Data\Sound\FX\CMB. Since test 44 they are the recorded set (tools/sound: the
        // start, the stop and the 860 rpm idle from demodave's recording, the riding loops resynthesised
        // from its pulses); tools/sound/make_engine_sounds.py writes the older synthesised set. The cruise
        // loop keeps its file name: in the recorded set CMB_EngineCruiseLP.wav is the on-load 2000 rpm loop
        // (what 4th gear turns at riding speed, the plugin's On2000), so the script's own crossfade works
        // with or without the plugin, and a build from the repository alone keeps its synthesised cruise.
        // The nine more the plugin drives are after the CMB_Snd globals below.
        var sndStart = EngineSound(mod, "CMB_EngineStartSD", "CMB_EngineStart.wav", loop: false);
        var sndStop = EngineSound(mod, "CMB_EngineStopSD", "CMB_EngineStop.wav", loop: false);
        var sndIdle = EngineSound(mod, "CMB_EngineIdleLPSD", "CMB_EngineIdleLP.wav", loop: true);
        var sndCruise = EngineSound(mod, "CMB_EngineCruiseLPSD", "CMB_EngineCruiseLP.wav", loop: true);
        var gEngineVolume = Global(mod, "CMB_EngineVolume", 90);   // test 47: the MCM's default 90 (70 up to test 46; test 46's tester settled at 90); a save keeps its own
        if (gEngineVolume.FormKey.ID != 0x81C)   // test 46: CMB_Slope.dll puts it on the engine's loops it drives, found by ID
            throw new InvalidOperationException($"CMB_EngineVolume must be 0x81C (CMB_Slope.dll looks for it), got {gEngineVolume.FormKey.ID:X}");

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

        // --- The headlamp (test 29's wish): the MCM's mode, the live switch the plugin reads, the two
        // lights (plain and shadow-casting), and the ADDN records that would hang them on a nif's add-on
        // nodes (CMB_Headlamp 31985, CMB_HeadlampShadow 31986). No nif carries those node indices since
        // the lamp piece went (test 35: its slot read "nothing" at tick 2 as well), so the ADDN records
        // and the plugin's add-on-node path are dormant; the light that works is the reference the
        // controller script places (below).
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
        // plugin keeps it at the lens. This is the path that lights the lamp (tests 32 to 35).
        var gHeadlampShadows = Global(mod, "CMB_HeadlampShadows", 0);
        var gHeadlampRefHi = Global(mod, "CMB_HeadlampRefHi", 0);
        var gHeadlampRefLo = Global(mod, "CMB_HeadlampRefLo", 0);
        if (gHeadlampShadows.FormKey.ID != 0x842 || gHeadlampRefHi.FormKey.ID != 0x843 || gHeadlampRefLo.FormKey.ID != 0x844)
            throw new InvalidOperationException($"CMB_HeadlampShadows, CMB_HeadlampRefHi and CMB_HeadlampRefLo must be 0x842-0x844 (CMB_Slope.dll looks for them), got {gHeadlampShadows.FormKey.ID:X}, {gHeadlampRefHi.FormKey.ID:X}, {gHeadlampRefLo.FormKey.ID:X}");

        // --- Knocking enemies over (test 40's wish): CMB_Slope.dll's rays see an actor ahead and ask
        // CMB_RamScript about it (SeenHi/Lo: its form id's halves; Seen: the ask's number), the script
        // answers in Ok (the number: yes; minus it: no), and the plugin tells the hit (HitSpeed, then
        // Hit: the number of the ask said yes to). Enemies and MinSpeed are the MCM's, read by both;
        // Damage the script's. Fixed IDs 0x845-0x84D, the list of races never knocked over 0x84E; test 43's
        // list of the robots let past the plugin's size and No Knockdowns gates, CMB_RamRobots, is 0x856
        // (after the room globals, below, so no ID here moves).
        // Test 40: on by default, 10% of their health is fine, from 450 a second (half riding speed).
        var gRam = new[] { "SeenHi", "SeenLo", "Seen", "Ok", "HitSpeed", "Hit" }.Select(n => Global(mod, "CMB_Ram" + n, 0)).ToArray();
        var gRamEnemies = Global(mod, "CMB_RamEnemies", 1);
        var gRamMinSpeed = Global(mod, "CMB_RamMinSpeed", 450);   // units a second; riding speed is about 900
        var gRamDamage = Global(mod, "CMB_RamDamage", 10);        // percent of the actor's max health at riding speed
        var ramTooBig = mod.FormLists.AddNew("CMB_RamTooBig");
        foreach (var race in Vanilla.TooBigToKnockOver)
            ramTooBig.Items.Add(new FormLink<IFallout4MajorRecordGetter>(race));
        // Each one checked: the plugin finds 0x845-0x84C by ID, and a form created before them here moves them all.
        var ramForms = gRam.Append(gRamEnemies).Append(gRamMinSpeed).Append(gRamDamage).Cast<IMajorRecordGetter>().Append(ramTooBig).ToArray();
        for (int i = 0; i < ramForms.Length; i++)
            if (ramForms[i].FormKey.ID != 0x845 + i)
                throw new InvalidOperationException($"{ramForms[i].EditorID} must be 0x{0x845 + i:X} (CMB_RamSeenHi..CMB_RamMinSpeed 0x845-0x84C, CMB_Slope.dll looks for them; CMB_RamDamage 0x84D, CMB_RamTooBig 0x84E), got {ramForms[i].FormKey.ID:X}");

        // --- The brought bike's spot (test 41): brought from Diamond City's door, the bike stood in the
        // gate's chain-link fence each time, at a fixed spot with no look at what was there. Before moving
        // it, CMB_ControllerScript asks CMB_Slope.dll whether a spot has room (RoomAskX/Y/Z: the spot, at
        // the player's height; RoomAsk: the ask's number), the plugin answers in RoomAnswer (the number:
        // room; minus it: none) and RoomClear (with room, how far below the asked Z the ground is; with
        // none, how far along its ray the nearest hit was (since test 43 on the bike's 110: a side ray's hit scaled
        // to the box's length), or the ground's offset, -1 with no ground within 100, -2 when the plugin's rays
        // aren't working there). Fixed IDs 0x84F-0x854, floats 0. The controller's
        // properties for them aren't Mandatory: an older ESP leaves them None and no spot is checked. Test 43:
        // the spot's heading too, CMB_RoomAskAngle 0x855 (below).
        var gRoom = new[] { "AskX", "AskY", "AskZ", "Ask", "Answer", "Clear" }.Select(n => Global(mod, "CMB_Room" + n, 0)).ToArray();
        for (int i = 0; i < gRoom.Length; i++)
            if (gRoom[i].FormKey.ID != 0x84F + i)
                throw new InvalidOperationException($"{gRoom[i].EditorID} must be 0x{0x84F + i:X} (CMB_RoomAskX..CMB_RoomClear 0x84F-0x854, CMB_Slope.dll looks for them), got {gRoom[i].FormKey.ID:X}");
        // Test 43: the spot's heading (degrees, the player's GetAngleZ), written by the controller with the spot
        // before the ask's number, so the plugin checks a bike-shaped box along it ([Room] Box: 110 fore and aft,
        // 40 to the sides) instead of eight level rays 110 out (test 42: a passage under about 220 wide never had
        // room). -1000 = none written (an older script): a heading of exactly 0 or -1 stays a heading, and
        // GetAngleZ's range (0-360 or +-180) isn't confirmed. The plugin finds it by ID apart from the six (an
        // ESP without it keeps the eight rays); the controller's property isn't Mandatory either.
        var gRoomAngle = Global(mod, "CMB_RoomAskAngle", -1000);
        if (gRoomAngle.FormKey.ID != 0x855)
            throw new InvalidOperationException($"CMB_RoomAskAngle must be 0x855 (CMB_Slope.dll looks for it), got {gRoomAngle.FormKey.ID:X}");
        // Test 43: the robots knocked over all the same (Vanilla.Robots: test 42's protectron reads large with No
        // Knockdowns and was braked for). Read by the plugin only ([Ram] Robots: the races in it pass its size and
        // No Knockdowns gates), by ID, so no script property; CMB_RamScript's own refusals (CMB_RamTooBig) stand.
        var ramRobots = mod.FormLists.AddNew("CMB_RamRobots");
        foreach (var race in Vanilla.Robots)
            ramRobots.Items.Add(new FormLink<IFallout4MajorRecordGetter>(race));
        if (ramRobots.FormKey.ID != 0x856)
            throw new InvalidOperationException($"CMB_RamRobots must be 0x856 (CMB_Slope.dll looks for it), got {ramRobots.FormKey.ID:X}");

        // --- The engine sound (test 44): CMB_Slope.dll pitches and levels the engine's loops each frame from
        // an rpm, gear and load model of the bike's speed and the forward key ([Sound]). The controller plays
        // the eleven loops (the idle, six on load, four off load) and writes each one's instance id to
        // CMB_SndLoop01..11 in the order of the plugin's [Sound] Loops line (idle 860; on 1400, 1700, 2000,
        // 2400, 2800, 3300; off 1400, 1800, 2300, 2800), 0 for none: ids are whole numbers under 2^24, which a
        // float holds exactly. Then it bumps CMB_SndGen (a new set of loops, or none: all eleven 0), last. The
        // plugin answers in CMB_SndDriven: the generation when it drives that set, minus it when it declines
        // (its log says why), 0 when it has let go. Fixed IDs 0x857-0x863, floats 0, right after
        // CMB_RamRobots so no ID above moves; the plugin finds them by ID. The controller's properties for
        // them aren't Mandatory: an older ESP leaves them None, and the script's own crossfade of the idle and
        // cruise loops plays, as before.
        var gSndLoop = Enumerable.Range(1, 11).Select(i => Global(mod, $"CMB_SndLoop{i:D2}", 0)).ToArray();
        var gSndGen = Global(mod, "CMB_SndGen", 0);
        var gSndDriven = Global(mod, "CMB_SndDriven", 0);
        var sndForms = gSndLoop.Append(gSndGen).Append(gSndDriven).ToArray();
        for (int i = 0; i < sndForms.Length; i++)
            if (sndForms[i].FormKey.ID != 0x857 + i)
                throw new InvalidOperationException($"{sndForms[i].EditorID} must be 0x{0x857 + i:X} (CMB_SndLoop01..CMB_SndLoop11 0x857-0x861, CMB_SndGen 0x862, CMB_SndDriven 0x863, CMB_Slope.dll looks for them), got {sndForms[i].FormKey.ID:X}");
        // The nine riding loops beside the idle and the cruise (On2000) ones, played at no volume until the
        // plugin brings each in. Their IDs fall where they do: only the controller's properties find them.
        var sndOn1400 = EngineSound(mod, "CMB_EngineOn1400LPSD", "CMB_EngineOn1400LP.wav", loop: true);
        var sndOn1700 = EngineSound(mod, "CMB_EngineOn1700LPSD", "CMB_EngineOn1700LP.wav", loop: true);
        var sndOn2400 = EngineSound(mod, "CMB_EngineOn2400LPSD", "CMB_EngineOn2400LP.wav", loop: true);
        var sndOn2800 = EngineSound(mod, "CMB_EngineOn2800LPSD", "CMB_EngineOn2800LP.wav", loop: true);
        var sndOn3300 = EngineSound(mod, "CMB_EngineOn3300LPSD", "CMB_EngineOn3300LP.wav", loop: true);
        var sndOff1400 = EngineSound(mod, "CMB_EngineOff1400LPSD", "CMB_EngineOff1400LP.wav", loop: true);
        var sndOff1800 = EngineSound(mod, "CMB_EngineOff1800LPSD", "CMB_EngineOff1800LP.wav", loop: true);
        var sndOff2300 = EngineSound(mod, "CMB_EngineOff2300LPSD", "CMB_EngineOff2300LP.wav", loop: true);
        var sndOff2800 = EngineSound(mod, "CMB_EngineOff2800LPSD", "CMB_EngineOff2800LP.wav", loop: true);

        // --- Test 46 (test 45's 12 calls by fences, a house and a hillside, 5 fine): CMB_Slope.dll tells the
        // controller its [Room] keys for the script in CMB_RoomOptions (bit 1 Around: four spots beside and behind
        // the player after the seven ahead; bit 2, its LineFallback=0: a call with no spot with room nor one to take
        // for the most room is refused) and, with each answer, the ground's tilt under the parked bike's wheels at
        // the spot with room (or a refused one a call can take for the most room) in CMB_RoomPitch and CMB_RoomRoll
        // (degrees as SetAngle takes them; -1000 none), that spot's ground height in CMB_RoomGround, which SettleBike
        // sets the brought bike to and on. Fixed IDs 0x86D-0x870, after the nine loops' descriptors so no ID
        // above moves; the plugin finds them by ID. The controller's properties aren't Mandatory: an older ESP
        // leaves them None, and the spots, the call's fallback and the tilt are test 45's.
        var gRoomOptions = Global(mod, "CMB_RoomOptions", 0);
        var gRoomPitch = Global(mod, "CMB_RoomPitch", -1000);
        var gRoomRoll = Global(mod, "CMB_RoomRoll", -1000);
        var gRoomGround = Global(mod, "CMB_RoomGround", 0);
        var roomMore = new[] { gRoomOptions, gRoomPitch, gRoomRoll, gRoomGround };
        for (int i = 0; i < roomMore.Length; i++)
            if (roomMore[i].FormKey.ID != 0x86D + i)
                throw new InvalidOperationException($"{roomMore[i].EditorID} must be 0x{0x86D + i:X} (CMB_RoomOptions, CMB_RoomPitch, CMB_RoomRoll, CMB_RoomGround 0x86D-0x870, CMB_Slope.dll looks for them), got {roomMore[i].FormKey.ID:X}");

        // The engine's own output model (test 45's answer), made last so every earlier form ID stays put (it comes
        // after the room globals 0x86D-0x870, so it is 0x871); all 13 engine sounds play through it. (2026-11-02a: the
        // check that every sound plays through its model comes after the bike sounds' own records, below.)
        var engineModel = OutputModel(mod, EngineModelId);
        foreach (var s in new[] { sndStart, sndStop, sndIdle, sndCruise, sndOn1400, sndOn1700, sndOn2400, sndOn2800, sndOn3300,
                                  sndOff1400, sndOff1800, sndOff2300, sndOff2800 })
            s.OutputModel.SetTo(engineModel);

        // --- 2026-11-01a (test 47's answer): the round's fixed IDs, 0x872-0x878, right after the engine's output model
        // (0x871) so no ID above moves; CMB_Slope.dll finds each by ID (its #defines and the harness's FORMIDs use these
        // numbers: renumber all three together). Floats, 0 but the brake key. The controller's properties for them aren't
        // Mandatory: an older ESP leaves them None, and each unit's change stays off (2026-10-31a).
        // TailRefHi/Lo: the tail lamp's light reference (CMB_TailLight, placed by the controller), its form id's high and
        // low 16 bits for the plugin, which keeps it at the lens (as CMB_HeadlampRefHi/Lo; both 0: none).
        var gTailRefHi = Global(mod, "CMB_TailRefHi", 0);
        var gTailRefLo = Global(mod, "CMB_TailRefLo", 0);
        // ViewRefHi/Lo: the first-person bike's reference (CMB_BikeView), the same way: the plugin shows it in first
        // person only and places it every frame.
        var gViewRefHi = Global(mod, "CMB_ViewRefHi", 0);
        var gViewRefLo = Global(mod, "CMB_ViewRefLo", 0);
        // RoomAskKind: what the controller's room ask is, written before the ask's number on every ask (0 a spot, as
        // before; 1 the navmesh point a call's snap found, asked about as a navmesh point: [Room] SnapSpot).
        var gRoomAskKind = Global(mod, "CMB_RoomAskKind", 0);
        // RiderPoseOff: the plugin writes it, the controller reads it ([Tilt] PoseCheck): the raw seconds the rider's
        // clips have been off the seat (0 while seated, and at a ride's start and end); the script compares it with
        // CMB_PoseOffAfter (3.0, below) before it applies the rider pose again.
        var gRiderPoseOff = Global(mod, "CMB_RiderPoseOff", 0);
        // BrakeKey: the MCM's "Brake key", a DirectInput scan code (57 = Space; 0 none, only S brakes), read by the
        // plugin at each ride's start ([Steer] BrakeKey=-1).
        var gBrakeKey = Global(mod, "CMB_BrakeKey", 57);
        var fixed49 = new[] { gTailRefHi, gTailRefLo, gViewRefHi, gViewRefLo, gRoomAskKind, gRiderPoseOff, gBrakeKey };
        for (int i = 0; i < fixed49.Length; i++)
            if (fixed49[i].FormKey.ID != 0x872 + i)
                throw new InvalidOperationException($"{fixed49[i].EditorID} must be 0x{0x872 + i:X} (CMB_TailRefHi, CMB_TailRefLo, CMB_ViewRefHi, CMB_ViewRefLo, CMB_RoomAskKind, CMB_RiderPoseOff, CMB_BrakeKey 0x872-0x878, CMB_Slope.dll looks for them), got {fixed49[i].FormKey.ID:X}");

        // --- 2026-11-01a's script-only forms, after the fixed IDs (only the scripts' properties find them, so their
        // IDs fall where they do). The MCM's switches, 1 by default, 0 = 2026-10-31a: a knock-over can take an enemy's
        // last health (CMB_RamScript), the tail lamp's light is placed, the first-person bike is placed.
        var gRamKills = Global(mod, "CMB_RamKills", 1);
        var gTailLightMode = Global(mod, "CMB_TailLightMode", 1);
        var gFirstPersonBike = Global(mod, "CMB_FirstPersonBike", 1);
        var tailLight = TailLight(mod);
        // The first-person bike: an unskinned copy of the riding bike (CMB_BikeView.nif), placed by the controller and
        // shown and placed by the plugin in first person only.
        var bikeView = mod.MovableStatics.AddNew("CMB_BikeView");
        bikeView.Model = new Model { File = BikeViewModel };
        bikeView.ObjectBounds = new ObjectBounds { First = new P3Int16(-45, -75, 0), Second = new P3Int16(45, 130, 115) };
        // "Steady in the saddle" (test 47: hits and staggers on the bike play standing clips, and the bike hangs round
        // the rider's hips): the MCM's switch (1, 0 = staggered as in 2026-10-31a) and the hidden perk the controller
        // gives the rider while riding, Mod Incoming Stagger x0 (Bethesda's mod_armor_LessStagger, 245AFE, is the same
        // entry point). No conditions: the script adds and removes it. Three condition tabs, as Mod Incoming Damage:
        // the perk owner, the attacker, the attacker's weapon.
        var gRiderSteady = Global(mod, "CMB_RiderSteady", 1);
        var steadyPerk = mod.Perks.AddNew("CMB_RiderSteadyPerk");
        steadyPerk.Name = "Steady in the saddle";
        steadyPerk.Playable = false;
        steadyPerk.Hidden = true;
        steadyPerk.NumRanks = 1;
        steadyPerk.Level = 0;
        steadyPerk.Trait = false;
        steadyPerk.Effects.Add(new PerkEntryPointModifyValue
        {
            Rank = 0,
            Priority = 0,
            EntryPoint = APerkEntryPointEffect.EntryType.ModIncomingStagger,
            PerkConditionTabCount = 3,
            Modification = PerkEntryPointModifyValue.ModificationType.Multiply,
            Value = 0f,
        });
        // The pose check's two numbers for the controller: no standing footstep or pose reading acted on within this
        // long (s) of a hit, an item used or a stagger (the MCM's "Pose re-check pause after a hit", 0 = as 2026-10-31a),
        // and the seconds off the seat (CMB_RiderPoseOff) at which the pose is applied again, longer than any stagger.
        var gPoseReactionWindow = Global(mod, "CMB_PoseReactionWindow", 3);
        var gPoseOffAfter = Global(mod, "CMB_PoseOffAfter", 3);
        // The stagger watch: a hidden ability whose effect runs while the player is staggered (IsStaggered), the swim
        // watch's way; its effect script tells the controller (NoteStagger). Given on getting on, taken on getting off.
        var staggerEffect = WatchEffect(mod, "CMB_StaggerWatchEffect", "Motorbike stagger watch", quest, wading: false, script: "CMB_StaggerWatchEffectScript");
        var staggerAbility = mod.Spells.AddNew("CMB_StaggerWatchAbility");
        staggerAbility.Name = "Motorbike stagger watch";
        staggerAbility.ObjectBounds = new ObjectBounds();
        staggerAbility.Type = SpellType.Ability;
        staggerAbility.CastType = CastType.ConstantEffect;
        staggerAbility.TargetType = TargetType.Self;
        staggerAbility.Flags = SpellDataFlag.ManualCostCalc;
        staggerAbility.Effects.Add(WatchEntry(staggerEffect, Condition.Function.IsStaggered));
        // --- 2026-11-01a, the bike's own sounds besides the engine (fxsound: a landing sound, a water loop, the rider's
        // own jump and landing sounds muted): the plugin's seven, fixed IDs 0x884-0x88A, right after the forms above so
        // no ID above moves; CMB_Slope.dll finds them by ID, all seven or none (its FX_GLOBAL_ID and the harness's
        // FX_FORMID use these numbers: renumber all three together). The controller's properties aren't Mandatory: an
        // older ESP leaves them None, and nothing plays (2026-10-31a).
        // FxVolume: the MCM's "Bike effects volume", 0-100 (90; 0 none): the plugin reads it every frame for the water
        // loop, the script at each landing.
        var gFxVolume = Global(mod, "CMB_FxVolume", 90);
        // FxWaterId: the water loop's instance id, written by the script on getting on (played at no volume), 0 none.
        var gFxWaterId = Global(mod, "CMB_FxWaterId", 0);
        // FxDriven: the plugin's answer: the id when it drives that loop, minus it when it declines (its log says why).
        var gFxDriven = Global(mod, "CMB_FxDriven", 0);
        // FxAir: the plugin's flight state: 0 on the ground, 1 once the bike has been [Fx] AirMin (0.35 s) in the air,
        // 2 for AirHold (0.3 s) after that flight's landing.
        var gFxAir = Global(mod, "CMB_FxAir", 0);
        // FxLandSeq: one more at each take-off past AirMin (a flight's number), the plugin's; it starts each ride from
        // the global's own value, so a save's number never repeats.
        var gFxLandSeq = Global(mod, "CMB_FxLandSeq", 0);
        // FxLandLevel: the landing's level 0-1 from the fall's speed, the plugin's, written through the flight and at the
        // landing, +2 into water; -1 (the ESP's, and [Fx] Land=0): no cue, the script's own level.
        var gFxLandLevel = Global(mod, "CMB_FxLandLevel", -1);
        // FxLandPlayed: the flight whose landing sound the script played last, written by the script; the plugin logs
        // how long after the landing that came.
        var gFxLandPlayed = Global(mod, "CMB_FxLandPlayed", 0);
        var fixedFx = new[] { gFxVolume, gFxWaterId, gFxDriven, gFxAir, gFxLandSeq, gFxLandLevel, gFxLandPlayed };
        for (int i = 0; i < fixedFx.Length; i++)
            if (fixedFx[i].FormKey.ID != 0x884 + i)
                throw new InvalidOperationException($"{fixedFx[i].EditorID} must be 0x{0x884 + i:X} (CMB_FxVolume, CMB_FxWaterId, CMB_FxDriven, CMB_FxAir, CMB_FxLandSeq, CMB_FxLandLevel, CMB_FxLandPlayed 0x884-0x88A, CMB_Slope.dll looks for them), got {fixedFx[i].FormKey.ID:X}");
        // The bike sounds' script-only forms, after the seven (only the controller's properties find them). The MCM's
        // switches, 1 by default, 0 = 2026-10-31a: the rider's own footstep sounds muted while riding, the landing sound,
        // the water loop. The picks, for the console: CMB_FxLandPick 1 = the second landing set, CMB_FxWaterPick the
        // water loop's index (read on getting on).
        var gFxMuteRider = Global(mod, "CMB_FxMuteRider", 1);
        var gFxLandOn = Global(mod, "CMB_FxLandOn", 1);
        var gFxWaterOn = Global(mod, "CMB_FxWaterOn", 1);
        var gFxLandPick = Global(mod, "CMB_FxLandPick", 0);
        var gFxWaterPick = Global(mod, "CMB_FxWaterPick", 0);
        // The game's own sound descriptors by FormID (Vanilla.FxLandSounds, FxLandSoundsAlt, FxWaterLoops), in lists so
        // our own can take their places later: nothing else names them.
        var fxLandSounds = mod.FormLists.AddNew("CMB_FxLandSounds");
        foreach (var s in Vanilla.FxLandSounds)
            fxLandSounds.Items.Add(new FormLink<IFallout4MajorRecordGetter>(s));
        var fxLandSoundsAlt = mod.FormLists.AddNew("CMB_FxLandSoundsAlt");
        foreach (var s in Vanilla.FxLandSoundsAlt)
            fxLandSoundsAlt.Items.Add(new FormLink<IFallout4MajorRecordGetter>(s));
        var fxWaterLoops = mod.FormLists.AddNew("CMB_FxWaterLoops");
        foreach (var s in Vanilla.FxWaterLoops)
            fxWaterLoops.Items.Add(new FormLink<IFallout4MajorRecordGetter>(s));

        // --- 2026-11-02a (test 48's answer): the round's fixed IDs, 0x893-0x895, right after the bike sounds' lists
        // (0x892) so no ID above moves; CMB_Slope.dll finds them by ID, all three or none (its RIDER_ITEM_USE_ID,
        // RAM_COMBAT_ID and FX_RANGE_ID and the harness's ITEM_USE_FORMID, RAM_COMBAT_FORMID and FX_RANGE_FORMID use these
        // numbers: renumber all three together). The controller's properties for them aren't Mandatory: an older ESP
        // leaves them None, and each change stays off (2026-11-01a). Their readers: the plugin's [Tilt] UseLetGo, its
        // [Ram] PendingFoe=2 and its landing lines.
        // RiderItemUse (test 48: the arm stretched while eating): the controller's count of the items used while riding,
        // 1-999 then 1 again, written at the use or at the Pip-Boy's or the favourites' close; the plugin lets go of the
        // hands while the item's use clip plays.
        var gRiderItemUse = Global(mod, "CMB_RiderItemUse", 0);
        // RamCombat (test 48: 10 brakes for asks not answered in time): 1 while the player is in combat, written by the
        // controller's CombatHint every tick; the plugin passes a medium race whose ask is pending.
        var gRamCombat = Global(mod, "CMB_RamCombat", 0);
        // FxLandRange (test 48: the landings played and not heard): the MCM's "Landing loudness range (dB)", 0-30 (10;
        // 18 = 2026-11-01a): the softest landing this many dB under the hardest; the controller at each landing, the
        // plugin for its landing lines.
        var gFxLandRange = Global(mod, "CMB_FxLandRange", 10);
        var fixed50 = new[] { gRiderItemUse, gRamCombat, gFxLandRange };
        for (int i = 0; i < fixed50.Length; i++)
            if (fixed50[i].FormKey.ID != 0x893 + i)
                throw new InvalidOperationException($"CMB_RiderItemUse, CMB_RamCombat and CMB_FxLandRange must be 0x893-0x895 (CMB_Slope.dll looks for them), got {string.Join(", ", fixed50.Select(g => $"{g.EditorID} {g.FormKey.ID:X}"))}");

        // --- 2026-11-02a's script-only forms, after the fixed IDs (only the scripts' properties find them, so their
        // IDs fall where they do).
        // Test 48 (8 "Staggered while riding (Steady on)", 4 of them power attacks): CMB_RiderSteadyPerk's entry had three
        // condition tabs (Mod Incoming Damage's owner/attacker/weapon) and no EPFB; the game's only Mod Incoming Stagger perk,
        // mod_armor_LessStagger (00245AFE), has two (the perk owner, the attacker) and EPFB 0x0000. CMB_RiderSteadyPerk stays as
        // it was (CMB_RiderSteadyWay 0 = the 2026-11-01a record); this one is the default.
        var steadyPerk2 = mod.Perks.AddNew("CMB_RiderSteadyPerk2");
        steadyPerk2.Name = "Steady in the saddle";
        steadyPerk2.Playable = false;
        steadyPerk2.Hidden = true;
        steadyPerk2.NumRanks = 1;
        steadyPerk2.Level = 0;
        steadyPerk2.Trait = false;
        steadyPerk2.Effects.Add(new PerkEntryPointModifyValue
        {
            Rank = 0,
            Priority = 0,
            PerkEntryID = 0,                 // EPFB 0x0000, as 245AFE (Mutagen's APerkEffect.PerkEntryID; null = no EPFB, as 11-01a)
            EntryPoint = APerkEntryPointEffect.EntryType.ModIncomingStagger,
            PerkConditionTabCount = 2,       // the perk owner, the attacker (245AFE's count)
            Modification = PerkEntryPointModifyValue.ModificationType.Multiply,
            Value = 0f,
        });
        // Which record Steady gives: 1 = CMB_RiderSteadyPerk2 (the default), 2 = the game's mod_armor_LessStagger (245AFE,
        // Add -1: one step less), 0 = the 2026-11-01a CMB_RiderSteadyPerk (three tabs). No MCM control: a console A/B.
        var gRiderSteadyWay = Global(mod, "CMB_RiderSteadyWay", 1);
        // Test 48 (the camera stuck after the first stimpak: an animation mod's use clip cut by the Pip-Boy check): no pose
        // re-apply within this many seconds of an item used while riding, from the menu's close when it was used in one
        // (0 = 2026-11-01a); and the camera's recovery after a use (1: the view entered again, then a notification; 0 none).
        // Console only.
        var gPoseUseWindow = Global(mod, "CMB_PoseUseWindow", 6);
        var gUseCameraFix = Global(mod, "CMB_UseCameraFix", 1);
        // Test 48 (12 kills by the bike, no experience): the bike's killing hit dealt as the player's own, a damage spell the
        // player casts (CMB_RamScript), so the game rewards the kill as one of the player's. The effect: Health down by the
        // magnitude, at once, no hit art or pain sound, not in the UI; an ordinary hit event (not NoHitEvent).
        var ramKillEffect = mod.MagicEffects.AddNew("CMB_RamKillEffect");
        ramKillEffect.Archetype = new MagicEffectArchetype { Type = MagicEffectArchetype.TypeEnum.ValueModifier };
        ((MagicEffectArchetype)ramKillEffect.Archetype).ActorValue.SetTo(Vanilla.Health);
        ramKillEffect.CastType = CastType.FireAndForget;
        ramKillEffect.TargetType = TargetType.TargetActor;
        ramKillEffect.Flags = MagicEffect.Flag.Hostile | MagicEffect.Flag.Detrimental | MagicEffect.Flag.Painless
            | MagicEffect.Flag.NoHitEffect | MagicEffect.Flag.NoDuration | MagicEffect.Flag.NoArea | MagicEffect.Flag.HideInUI;
        ramKillEffect.CastingSoundLevel = SoundLevel.Silent;
        ramKillEffect.DualCastScale = 1;
        var ramKillSpell = mod.Spells.AddNew("CMB_RamKillSpell");
        ramKillSpell.Name = "Motorbike knock-over";
        ramKillSpell.ObjectBounds = new ObjectBounds();
        ramKillSpell.Type = SpellType.Spell;
        ramKillSpell.CastType = CastType.FireAndForget;
        ramKillSpell.TargetType = TargetType.TargetActor;
        ramKillSpell.Flags = SpellDataFlag.ManualCostCalc | SpellDataFlag.IgnoreResistance | SpellDataFlag.NoAbsorbOrReflect;
        ramKillSpell.BaseCost = 0;
        ramKillSpell.Effects.Add(new Effect
        {
            BaseEffect = ramKillEffect.ToNullableLink(),
            Data = new EffectData { Magnitude = 100000, Area = 0, Duration = 0 },   // only cast when the knock-over's own damage already takes the last health
        });
        if (ramKillEffect.Archetype is not MagicEffectArchetype { Type: MagicEffectArchetype.TypeEnum.ValueModifier } arch
            || arch.ActorValue.FormKey != Vanilla.Health
            || ramKillEffect.Flags != (MagicEffect.Flag.Hostile | MagicEffect.Flag.Detrimental | MagicEffect.Flag.Painless
                                       | MagicEffect.Flag.NoHitEffect | MagicEffect.Flag.NoDuration | MagicEffect.Flag.NoArea | MagicEffect.Flag.HideInUI)
            || ramKillEffect.Flags.HasFlag(MagicEffect.Flag.NoHitEvent))
            throw new InvalidOperationException("CMB_RamKillEffect must be a Value Modifier of Health (0002D4), Hostile, Detrimental, Painless, NoHitEffect, NoDuration, NoArea and HideInUI, not NoHitEvent");
        if (ramKillSpell.Effects.Count != 1 || ramKillSpell.Effects[0].BaseEffect.FormKey != ramKillEffect.FormKey
            || ramKillSpell.Effects[0].Data?.Magnitude != 100000)
            throw new InvalidOperationException("CMB_RamKillSpell must have one effect, CMB_RamKillEffect at magnitude 100000");
        // MCM "Kill experience": 0 Kill(PlayerRef) (2026-11-01a, no experience), 1 Spell.Cast by the player (the default),
        // 2 DoCombatSpellApply (the same another way).
        var gRamKillXP = Global(mod, "CMB_RamKillXP", 1);
        // Test 48 (the landing and water sounds played but 13-37 dB under their files: the game's records' own static
        // attenuation and their output models' fade at the riding camera): our own records over the game's files by
        // path, through an output model of our own, a copy of the engine's (so the engine's stays the engine's).
        var fxModel = OutputModel(mod, FxModelId);
        var fxOwn = new Dictionary<string, SoundDescriptor>();
        foreach (var r in FxOwn.Records)
        {
            var s = FxSound(mod, r);
            s.OutputModel.SetTo(fxModel);
            fxOwn.Add(r.Id, s);
        }
        var fxLandSoundsOwn = mod.FormLists.AddNew("CMB_FxLandSoundsOwn");
        foreach (var id in FxOwn.Land)
            fxLandSoundsOwn.Items.Add(new FormLink<IFallout4MajorRecordGetter>(fxOwn[id].FormKey));
        var fxLandSoundsAltOwn = mod.FormLists.AddNew("CMB_FxLandSoundsAltOwn");
        foreach (var id in FxOwn.LandAlt)
            fxLandSoundsAltOwn.Items.Add(new FormLink<IFallout4MajorRecordGetter>(fxOwn[id].FormKey));
        var fxWaterLoopsOwn = mod.FormLists.AddNew("CMB_FxWaterLoopsOwn");
        foreach (var id in FxOwn.Water)
            fxWaterLoopsOwn.Items.Add(new FormLink<IFallout4MajorRecordGetter>(fxOwn[id].FormKey));
        // MCM "Bike sounds through the mod's own records": 1 = ours (the default), 0 = the game's own records (the
        // borrowed lists above), as 2026-11-01a.
        var gFxOwnSounds = Global(mod, "CMB_FxOwnSounds", 1);
        // Every sound plays through its own model: the engine's 13 (CMB_Engine*) through CMB_SOMMonoEngine, the effects'
        // (CMB_Fx*SD) through CMB_SOMMonoFx, and there is no other sound. Checked here and again after 2026-11-09a's block
        // (its gentle wet-road loop is made after the look).
        void CheckSoundModels()
        {
            foreach (var s in mod.SoundDescriptors)
            {
                var want = s.EditorID!.StartsWith("CMB_Engine") ? engineModel
                         : s.EditorID.StartsWith("CMB_Fx") && s.EditorID.EndsWith("SD") ? fxModel
                         : null;
                if (want == null)
                    throw new InvalidOperationException($"{s.EditorID}: a sound that is neither an engine sound (CMB_Engine*) nor a bike effect (CMB_Fx*SD)");
                if (s.OutputModel.FormKey != want.FormKey)
                    throw new InvalidOperationException($"{s.EditorID} doesn't play through {want.EditorID}: give it that output model");
            }
        }
        CheckSoundModels();

        // --- 2026-11-06a (test 49's answer): the round's fixed IDs, 0x8B0-0x8B4. 0x8AF is left unmade here: it is
        // CMB_LookCode's (LookRecords makes it there by FormKey since 2026-11-07a), so this block starts at 0x8B0 and
        // only CMB_LookCode may take 0x8AF (a throw at the end). CMB_Slope.dll finds the five by ID, all five or none (its
        // VIEW_TIP_ID, VIEW_FOV_ID, VIEW_EYE_FORWARD_ID, VIEW_EYE_UP_ID and FX_WATER_LOOP_ID and the harness's VIEW_TIP_FORMID ..
        // FX_WATER_LOOP_FORMID use these numbers: renumber all five together). The controller's properties aren't
        // Mandatory: an older ESP leaves them None, and each change stays off (2026-11-02a). Their readers: the plugin's
        // first-person view (the tip, the riding FOV, the eye's offsets) and the water loop's trim; the controller's
        // FxStartWaterLoop.
        mod.ModHeader.Stats.NextFormID = 0x8B0;
        // ViewTip (test 49: in first person the bike sat under the frame, the view level): the MCM's "Look down on getting
        // into first person (deg)", 0-45 (20; 0 = 2026-11-02a, the view left alone): the plugin eases the view down this far
        // once on entering first person on the bike.
        var gViewTip = Global(mod, "CMB_ViewTip", 20);
        // ViewFov: the MCM's "Field of view riding in first person", 0-120 (0 = the game's own, as 2026-11-02a; 1-59 read
        // as 0): the plugin's riding FOV in first person.
        var gViewFov = Global(mod, "CMB_ViewFov", 0);
        // ViewEyeForward, ViewEyeUp: the MCM's "Eye forward on the bike" (-30..30) and "Eye height on the bike" (-30..20)
        // and the console, added to [View] EyeAt's y and z (0 = the INI's EyeAt, 2026-11-02a).
        var gViewEyeForward = Global(mod, "CMB_ViewEyeForward", 0);
        var gViewEyeUp = Global(mod, "CMB_ViewEyeUp", 0);
        // FxWaterLoop (test 49: the water loop heard as a waterfall's frying): the MCM's "Water sound loop", 0 spray (the
        // 2026-11-02a build's, CMB_FxWaterPick), 1 churn, 2 the mod's own wet road (the 2026-11-06a to 2026-11-08a builds'
        // default), since 2026-11-09a 3 the gentle wet road (test 50: the wet road heard as static; CMB_FxWaterRoadSoftLPSD,
        // 0xBF3), the default; the controller's FxStartWaterLoop picks the loop, the plugin its trim and its line.
        // `--look-build 2026-11-07a` keeps 2 (that build's ESP byte for byte; it has no gentle loop).
        var gFxWaterLoop = Global(mod, "CMB_FxWaterLoop", LookRecords.Through == LookRecords.C1Build ? 2 : 3);
        var fixed51 = new[] { gViewTip, gViewFov, gViewEyeForward, gViewEyeUp, gFxWaterLoop };
        for (int i = 0; i < fixed51.Length; i++)
            if (fixed51[i].FormKey.ID != 0x8B0 + i)
                throw new InvalidOperationException($"CMB_ViewTip, CMB_ViewFov, CMB_ViewEyeForward, CMB_ViewEyeUp and CMB_FxWaterLoop must be 0x8B0-0x8B4 (CMB_Slope.dll looks for them), got {string.Join(", ", fixed51.Select(g => $"{g.EditorID} {g.FormKey.ID:X}"))}");

        // --- 2026-11-06a's script-only forms, after the fixed IDs (only the scripts' properties find them).
        // KnockOffPower (test 49: every power attack threw the rider off): the MCM's "Power attacks throw you off", 0 (off,
        // the default: a power attack is a hit like any other, Big hit's rule); 1 = 2026-11-02a (every power attack
        // knocks off). Explosions always do.
        var gKnockOffPower = Global(mod, "CMB_KnockOffPower", 0);
        // RiderUseOwn (test 49: another mod's dummy potion after a load read as an item used): 1 = only the player's own
        // uses watched (the favourites through CMB_HotkeyF4SE); 0 = every potion equipped, as 2026-11-02a. Console only.
        var gRiderUseOwn = Global(mod, "CMB_RiderUseOwn", 1);
        // FxLandDull (test 49: the landings' clunk heard as a metal barrel): the MCM's "Landing sounds without metal",
        // 1 = CMB_FxLandSoundsDull below (tyres, the PA dirt thud, the splashes and the PA water thud); 0 = the 2026-11-02a
        // build's sets. FxThudDb: the thud's level under the landing's, in dB (-11), console only.
        var gFxLandDull = Global(mod, "CMB_FxLandDull", 1);
        var gFxThudDb = Global(mod, "CMB_FxThudDb", -11);
        var fxLandSoundsDull = mod.FormLists.AddNew("CMB_FxLandSoundsDull");
        foreach (var id in FxOwn.LandDull)
            fxLandSoundsDull.Items.Add(new FormLink<IFallout4MajorRecordGetter>(fxOwn[id].FormKey));
        // The next fixed-ID form comes after these.

        // --- 2026-11-07a (the customisation build, C1): CMB_LookCode at the fixed 0x8AF (CMB_Slope.dll finds it by ID), then
        // 0x8BA-0xA13 in the order of look_options.json (save-stable: later builds only append, look_ids.txt): the look's
        // globals, keywords and attach points, the look item, the field kit's three furnitures and its box, the composed
        // swap, the mirrors' loose mods, a material swap, an object mod and a recipe per option, the lists. And in place:
        // the parked menu's Customise button, the riding armours' keyword and attach points (LookRecords).
        // 2026-11-08a (C2): then 0xA14-0xBF0 (LookRecords.BuildC2, look_options.json's entries "since": "2026-11-08a"): the
        // four colour values at fixed IDs, the MCM's hue, shade and crude switch, the six slots' globals and attach points,
        // Paint's option 45, the rims', tyres' and the plate's four slots' options, their lists; in place the look item's and
        // the riding armours' six more attach points, the template's six more option 0s, Paint's lists' 46th entries, the
        // lists of lists. `--look-build 2026-11-07a`: none of it (2026-11-07a's ESP byte for byte).
        var look = LookRecords.Build(mod, armor, armorFrame, msgParked);

        // --- 2026-11-09a (test 50's answer): the round's three forms, 0xBF1-0xBF3, right after C2's block (only with it:
        // `--look-build 2026-11-07a` makes none, so its ESP stays 2026-11-07a's byte for byte). CMB_Slope.dll finds the two
        // globals by ID, both or none (its CAUTION_ID and VIEW_MENU_ID and the harness's CAUTION_FORMID and
        // VIEW_MENU_FORMID use these numbers: renumber them together); the sound is save-stable through look_ids.txt. The
        // controller's two properties aren't Mandatory: an older ESP leaves them None (2026-11-08a). Their readers: the
        // plugin's obstacle easing (Caution, the MCM's slider) and the first-person tip's Pip-Boy rule (ViewMenu, which
        // the controller writes); the controller's FxStartWaterLoop (CMB_FxWaterLoop 3, the gentle wet road).
        SoundDescriptor? fxWaterRoadSoft = null;
        GlobalFloat? gViewMenu = null;
        if (look.HasC2)
        {
            if (mod.ModHeader.Stats.NextFormID != 0xBF1)
                throw new InvalidOperationException($"2026-11-09a's forms start at 0xBF1, after C2's block; the next ID is 0x{mod.ModHeader.Stats.NextFormID:X}");
            // Caution (test 50: obstacle detection too early): the MCM's "Caution (how early the bike eases off for
            // obstacles, %)", 50-100 (50; 60 = 2026-11-09a, 100 = 2026-11-08a): the plugin's FaceLook, WallStop and
            // WallStopPersist at it.
            // 2026-11-10a (test 52): 50 for a new save (60 = 2026-11-09a's; a save keeps its own value).
            var gCaution = Global(mod, "CMB_Caution", 50);
            // ViewMenu (test 50: the first-person tip ran in the Pip-Boy): 1 while the Pip-Boy is open on the bike (the
            // controller), else 0; the plugin's [View] TipMenu gives no tip then.
            gViewMenu = Global(mod, "CMB_ViewMenu", 0);
            // The gentle wet-road loop (test 50: the wet road heard as static): the mod's own, from the same recording as
            // CMB_FxWaterRoadLPSD, shipped loose at Data\Sound\FX\CMB\ and named relative to Data\Sound as 0x8A9's.
            // In no list: CMB_FxWaterLoop 3 plays it through the controller's own property, as 2 plays 0x8A9.
            fxWaterRoadSoft = FxSound(mod, FxOwn.WaterRoadSoft);
            fxWaterRoadSoft.OutputModel.SetTo(fxModel);
            var fixed54 = new IMajorRecordGetter[] { gCaution, gViewMenu, fxWaterRoadSoft };
            for (int i = 0; i < fixed54.Length; i++)
                if (fixed54[i].FormKey.ID != 0xBF1 + i)
                    throw new InvalidOperationException($"CMB_Caution and CMB_ViewMenu must be 0xBF1-0xBF2 (CMB_Slope.dll looks for them), CMB_FxWaterRoadSoftLPSD 0xBF3 (look_ids.txt), got {string.Join(", ", fixed54.Select(r => $"{r.EditorID} {r.FormKey.ID:X}"))}");
            CheckSoundModels();
        }

        // --- 2026-11-09a, test 51's answer: the round's one form, 0xBF4, right after 2026-11-09a's block (only with C2's
        // block: `--look-build 2026-11-07a` makes none). CMB_LookOptions: CMB_Slope.dll's [Look] switches for the scripts
        // (bits 1 FastMount, 2 KitHeld, 4 ParkedReload, 8 PaletteIndex, 16 MountGuard, 32 HueFree; 64 the plugin writes the
        // worn bike's colours), which the plugin writes at its start, with the settings and at getting on. The ESP's 63:
        // without the plugin the six script behaviours are on and the scripts colour the worn bike themselves. The plugin
        // finds it by ID (its LOOK_OPTIONS_ID and the harness's LOOK_OPTIONS_FORMID use this number: renumber them together).
        GlobalFloat? gLookOptions = null;
        if (look.HasC2)
        {
            if (mod.ModHeader.Stats.NextFormID != 0xBF4)
                throw new InvalidOperationException($"2026-11-09a's test 51 form starts at 0xBF4, after test 50's block; the next ID is 0x{mod.ModHeader.Stats.NextFormID:X}");
            // 2026-11-10a (test 52): 4031 = the six bits above + 128 KitStash, 256 KitRetry, 512 MountEarly, 1024
            // WornColoursFirst, 2048 HueSwap (63 + 3968: without the plugin the eleven script behaviours on, the scripts
            // colour the worn bike); the plugin at its defaults writes 4095. 63 = 2026-11-09a.
            gLookOptions = Global(mod, "CMB_LookOptions", 4031);
            if (gLookOptions.FormKey.ID != 0xBF4)
                throw new InvalidOperationException($"CMB_LookOptions must be 0xBF4 (CMB_Slope.dll looks for it), got {gLookOptions.FormKey.ID:X}");
        }

        // --- 2026-11-10a, test 52's answer: the round's two forms, 0xBF5-0xBF6, right after test 51's 0xBF4 (only with C2's
        // block: `--look-build 2026-11-07a` makes none). CMB_Slope.dll's word to the scripts: CMB_RiderQuickUse (count * 16
        // + slot of a potion's quickkey the plugin took at speed, [Steer] QuickUse; CMB_HotkeyF4SE uses the item) and
        // CMB_RideReady (1 when the ride's worn bike is held and coloured and the rider seated, [Look] RideReady; Mount fades
        // in on it). Both 0. The plugin finds them by ID (its QUICK_USE_ID and RIDE_READY_ID and the harness's
        // QUICK_USE_FORMID and RIDE_READY_FORMID use these numbers: renumber them together).
        GlobalFloat? gRiderQuickUse = null, gRideReady = null;
        if (look.HasC2)
        {
            if (mod.ModHeader.Stats.NextFormID != 0xBF5)
                throw new InvalidOperationException($"2026-11-10a's test 52 forms start at 0xBF5, after test 51's 0xBF4; the next ID is 0x{mod.ModHeader.Stats.NextFormID:X}");
            gRiderQuickUse = Global(mod, "CMB_RiderQuickUse", 0);
            gRideReady = Global(mod, "CMB_RideReady", 0);
            if (gRiderQuickUse.FormKey.ID != 0xBF5 || gRideReady.FormKey.ID != 0xBF6)
                throw new InvalidOperationException($"CMB_RiderQuickUse and CMB_RideReady must be 0xBF5-0xBF6 (CMB_Slope.dll looks for them), got {gRiderQuickUse.FormKey.ID:X}, {gRideReady.FormKey.ID:X}");
        }

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
            Obj("ActionPoints", Vanilla.ActionPoints),
            Obj("ActionPointsRate", Vanilla.ActionPointsRate),
            Obj("ActionPointsRateMult", Vanilla.ActionPointsRateMult),
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
            Obj("CMB_RoomAskX", gRoom[0]),
            Obj("CMB_RoomAskY", gRoom[1]),
            Obj("CMB_RoomAskZ", gRoom[2]),
            Obj("CMB_RoomAsk", gRoom[3]),
            Obj("CMB_RoomAnswer", gRoom[4]),
            Obj("CMB_RoomClear", gRoom[5]),
            Obj("CMB_RoomAskAngle", gRoomAngle),
            Obj("CMB_RoomOptions", gRoomOptions),
            Obj("CMB_RoomPitch", gRoomPitch),
            Obj("CMB_RoomRoll", gRoomRoll),
            Obj("CMB_RoomGround", gRoomGround),
            Obj("CMB_RoomAskKind", gRoomAskKind),
            Obj("CMB_RiderPoseOff", gRiderPoseOff),
            Obj("CMB_TailLight", tailLight),
            Obj("CMB_TailRefHi", gTailRefHi),
            Obj("CMB_TailRefLo", gTailRefLo),
            Obj("CMB_TailLightMode", gTailLightMode),
            Obj("CMB_BikeView", bikeView),
            Obj("CMB_ViewRefHi", gViewRefHi),
            Obj("CMB_ViewRefLo", gViewRefLo),
            Obj("CMB_FirstPersonBike", gFirstPersonBike),
            Obj("CMB_RiderSteadyPerk", steadyPerk),
            Obj("CMB_RiderSteady", gRiderSteady),
            Obj("CMB_PoseReactionWindow", gPoseReactionWindow),
            Obj("CMB_PoseOffAfter", gPoseOffAfter),
            Obj("CMB_StaggerWatchAbility", staggerAbility),
            Obj("CMB_FxVolume", gFxVolume),
            Obj("CMB_FxMuteRider", gFxMuteRider),
            Obj("CMB_FxLandOn", gFxLandOn),
            Obj("CMB_FxWaterOn", gFxWaterOn),
            Obj("AudioCategoryFSTplayer", Vanilla.AudioCategoryFSTplayer),
            Obj("CMB_FxLandSounds", fxLandSounds),
            Obj("CMB_FxLandSoundsAlt", fxLandSoundsAlt),
            Obj("CMB_FxWaterLoops", fxWaterLoops),
            Obj("CMB_FxLandPick", gFxLandPick),
            Obj("CMB_FxWaterPick", gFxWaterPick),
            Obj("CMB_FxWaterId", gFxWaterId),
            Obj("CMB_FxDriven", gFxDriven),
            Obj("CMB_FxAir", gFxAir),
            Obj("CMB_FxLandSeq", gFxLandSeq),
            Obj("CMB_FxLandLevel", gFxLandLevel),
            Obj("CMB_FxLandPlayed", gFxLandPlayed),
            Obj("CMB_RiderSteadyPerk2", steadyPerk2),
            Obj("CMB_RiderSteadyWay", gRiderSteadyWay),
            Obj("CMB_PoseUseWindow", gPoseUseWindow),
            Obj("CMB_UseCameraFix", gUseCameraFix),
            Obj("CMB_RiderItemUse", gRiderItemUse),
            Obj("CMB_RamCombat", gRamCombat),
            Obj("CMB_FxOwnSounds", gFxOwnSounds),
            Obj("CMB_FxLandRange", gFxLandRange),
            Obj("CMB_FxLandSoundsOwn", fxLandSoundsOwn),
            Obj("CMB_FxLandSoundsAltOwn", fxLandSoundsAltOwn),
            Obj("CMB_FxWaterLoopsOwn", fxWaterLoopsOwn),
            Obj("CMB_KnockOffPower", gKnockOffPower),
            Obj("CMB_RiderUseOwn", gRiderUseOwn),
            Obj("CMB_FxLandDull", gFxLandDull),
            Obj("CMB_FxThudDb", gFxThudDb),
            Obj("CMB_FxLandSoundsDull", fxLandSoundsDull),
            Obj("CMB_FxWaterLoop", gFxWaterLoop),
            Obj("CMB_FxWaterRoad", fxOwn["CMB_FxWaterRoadLPSD"]),
            // 2026-11-07a: the Look_C1 group (the session, the field kit, the looks), 29.
            Obj("CMB_BikeLook", look.BikeLook),
            Obj("CMB_LookCode", look.LookCode),
            Obj("CMB_LookOn", look.LookOn),
            Obj("CMB_LookFree", look.LookFree),
            Obj("CMB_Look_TankL", look.SlotGlobal("TankL")),
            Obj("CMB_Look_TankR", look.SlotGlobal("TankR")),
            Obj("CMB_Look_Fender", look.SlotGlobal("Fender")),
            Obj("CMB_Look_Paint", look.SlotGlobal("Paint")),
            Obj("CMB_Look_Mirrors", look.SlotGlobal("Mirrors")),
            Obj("CMB_LookFactionSet", look.FactionSet),
            Obj("CMB_KitMode", look.KitMode),
            Obj("CMB_KitWorked", look.KitWorked),
            Obj("CMB_KitBagLink", look.KitBagLink),
            Obj("CMB_LookCategories", look.Categories),
            Obj("CMB_FieldKit", look.FieldKit),
            Obj("CMB_FieldKitArmorKw", look.FieldKitArmorKw),
            Obj("CMB_FieldKitBench", look.FieldKitBench),
            Obj("CMB_FieldKitBox", look.FieldKitBox),
            Obj("WorkshopItemKeyword", Vanilla.WorkshopItemKeyword),
            Obj("LinkedWorkbenchContainerKeyword", Vanilla.LinkedWorkbenchContainerKeyword),
            Obj("LocTypeWorkshopSettlement", Vanilla.LocTypeWorkshopSettlement),
            Obj("WorkshopParentQuest", Vanilla.WorkshopParent),
            Obj("WorkshopPlayerOwned", Vanilla.WorkshopPlayerOwned),
            Obj("DRScToolboxBOpen", Vanilla.DRScToolboxBOpen),
            IntList("LookSetPaint", look.SetPaint),
            IntList("LookSetTank", look.SetTank),
            IntList("LookSetFender", look.SetFender),
            StringList("LookKeys", look.Keys),
            IntList("LookSlotStart", look.SlotStart),
            Obj("CMB_EngineOn1400Sound", sndOn1400),
            Obj("CMB_EngineOn1700Sound", sndOn1700),
            Obj("CMB_EngineOn2400Sound", sndOn2400),
            Obj("CMB_EngineOn2800Sound", sndOn2800),
            Obj("CMB_EngineOn3300Sound", sndOn3300),
            Obj("CMB_EngineOff1400Sound", sndOff1400),
            Obj("CMB_EngineOff1800Sound", sndOff1800),
            Obj("CMB_EngineOff2300Sound", sndOff2300),
            Obj("CMB_EngineOff2800Sound", sndOff2800),
            Obj("CMB_SndLoop01", gSndLoop[0]),
            Obj("CMB_SndLoop02", gSndLoop[1]),
            Obj("CMB_SndLoop03", gSndLoop[2]),
            Obj("CMB_SndLoop04", gSndLoop[3]),
            Obj("CMB_SndLoop05", gSndLoop[4]),
            Obj("CMB_SndLoop06", gSndLoop[5]),
            Obj("CMB_SndLoop07", gSndLoop[6]),
            Obj("CMB_SndLoop08", gSndLoop[7]),
            Obj("CMB_SndLoop09", gSndLoop[8]),
            Obj("CMB_SndLoop10", gSndLoop[9]),
            Obj("CMB_SndLoop11", gSndLoop[10]),
            Obj("CMB_SndGen", gSndGen),
            Obj("CMB_SndDriven", gSndDriven),
            Obj("GroundProbeRef", probeRef));
        // Knocking enemies over: does anything only with CMB_Slope.dll (F4SE), which writes the asks.
        var ram = Script("CMB_RamScript",
            Obj("PlayerRef", Vanilla.PlayerRef),
            Obj("Health", Vanilla.Health),
            Obj("CurrentCompanionFaction", Vanilla.CurrentCompanionFaction),
            Obj("CMB_RamTooBig", ramTooBig),
            Obj("CMB_RamEnemies", gRamEnemies),
            Obj("CMB_RamMinSpeed", gRamMinSpeed),
            Obj("CMB_RamDamage", gRamDamage),
            Obj("CMB_RamSeenHi", gRam[0]),
            Obj("CMB_RamSeenLo", gRam[1]),
            Obj("CMB_RamSeen", gRam[2]),
            Obj("CMB_RamOk", gRam[3]),
            Obj("CMB_RamHitSpeed", gRam[4]),
            Obj("CMB_RamHit", gRam[5]),
            Obj("CMB_RamKills", gRamKills),
            Obj("Experience", Vanilla.Experience),
            Obj("CMB_RamKillSpell", ramKillSpell),
            Obj("CMB_RamKillXP", gRamKillXP));
        // Optional: only does anything with F4SE and the compiled CMB_HotkeyF4SE.pex.
        var hotkey = Script("CMB_HotkeyF4SE",
            Obj("Controller", quest),
            Obj("CMB_HotkeyCode", gHotkey));
        // Optional too: puts slot-57 gear back on after a ride (F4SE's GetWornItem).
        var gear = Script("CMB_GearRestoreF4SE",
            Obj("Controller", quest),
            Obj("CMB_BikeRiderArmor", armor),
            Obj("CMB_BikeRiderArmorFrame", armorFrame),
            Int("BikeSlotIndex", BikeSlotIndex));
        // 2026-11-07a, optional too (F4SE's MatSwap and ApplyMaterialSwap): the chosen look on the parked and first-person
        // bikes through one composed swap, and on the worn bike when the game refuses the look's mods there.
        var lookF4se = Script("CMB_LookF4SE",
            Obj("Controller", quest),
            Obj("BikeRef", bikeRef),
            Obj("CMB_LookSwap", look.LookSwap),
            Obj("CMB_LookSwapLists", look.SwapLists),
            Obj("CMB_LookOn", look.LookOn),
            Obj("CMB_Look_TankL", look.SlotGlobal("TankL")),
            Obj("CMB_Look_TankR", look.SlotGlobal("TankR")),
            Obj("CMB_Look_Fender", look.SlotGlobal("Fender")),
            Obj("CMB_Look_Paint", look.SlotGlobal("Paint")),
            Obj("CMB_Look_Mirrors", look.SlotGlobal("Mirrors")));
        // 2026-11-08a (C2): the controller's Look_C2 group, 13, after LookSlotStart (the six slots' globals, the hue, the
        // shade, the crude switch; per Rims option its style, per PlateText option its crude flag, per Plate option its own
        // text, per faction set its plate), and CMB_LookF4SE's 21 after the C1 ten (the six globals, the three the MCM sets,
        // the four colour values; per Paint option its paint_p row, per Rims option its body finish, per PlateText option
        // its crude flag, per Plate option its own text, letters and background, the body-colour targets and their hue
        // twins). Not with `--look-build 2026-11-07a` (None in every one: the 2026-11-07a look).
        if (look.HasC2)
        {
            string[] c2Slots = { "Rims", "Tyres", "Plate", "PlateText", "PlateInk", "PlateBack" };
            ScriptProperty[] Globals(params string[] editorIds) => editorIds.Select(e => (ScriptProperty)Obj(e, look.C2Global(e))).ToArray();
            ScriptProperty[] SlotGlobals() => c2Slots.Select(k => (ScriptProperty)Obj(look.SlotOf(k).Global, look.SlotGlobal(k))).ToArray();
            controller.Properties.InsertRange(controller.Properties.FindIndex(p => p.Name == "LookSlotStart") + 1,
                SlotGlobals().Concat(Globals("CMB_LookHue", "CMB_LookShade", "CMB_LookPlateCrude")).Concat(new ScriptProperty[]
                {
                    IntList("LookRimStyle", look.RimStyle),
                    IntList("LookTextCrude", look.TextCrude),
                    IntList("LookPlateOwnText", look.PlateOwnText),
                    IntList("LookSetPlate", look.SetPlate),
                }));
            lookF4se.Properties.AddRange(SlotGlobals()
                .Concat(Globals("CMB_LookHue", "CMB_LookShade", "CMB_LookPlateCrude", "CMB_LookPaintV", "CMB_LookRimV", "CMB_LookPlateV", "CMB_LookPlateTextV"))
                .Concat(new ScriptProperty[]
                {
                    IntList("PaintRow", look.PaintRow),
                    IntList("RimBody", look.RimBody),
                    IntList("TextCrude", look.TextCrude),
                    IntList("PlateOwnText", look.PlateOwnText),
                    IntList("PlateOwnInk", look.PlateOwnInk),
                    IntList("PlateOwnBack", look.PlateOwnBack),
                    StringList("RimBodyTargets", look.RimBodyTargets.Select(t => t.Body)),
                    StringList("RimBodyHueTargets", look.RimBodyTargets.Select(t => t.Hue)),
                }));
            // 2026-11-09a: the controller's Fixes_54 group, 2, after CMB_FxWaterRoad: the Pip-Boy's flag for the
            // first-person tip (0xBF2) and the gentle wet-road loop (0xBF3). Not with `--look-build 2026-11-07a` (None:
            // 2026-11-08a's).
            controller.Properties.InsertRange(controller.Properties.FindIndex(p => p.Name == "CMB_FxWaterRoad") + 1, new ScriptProperty[]
            {
                Obj("CMB_ViewMenu", gViewMenu!),
                Obj("CMB_FxWaterRoadSoft", fxWaterRoadSoft!),
            });
            // 2026-11-09a, test 51: the controller's Fixes_55 group, 2, after CMB_FxWaterRoadSoft: the plugin's [Look]
            // switches (0xBF4) and the game's armour bench (Fallout4.esm 0x12EA9B, the field kit's mode 4); CMB_LookF4SE's
            // 2 at its end: the switches and, per Rims option, its finish's own palette V (RimFinishV). Not with
            // `--look-build 2026-11-07a` (None: 2026-11-09a as of t54-merge).
            controller.Properties.InsertRange(controller.Properties.FindIndex(p => p.Name == "CMB_FxWaterRoadSoft") + 1, new ScriptProperty[]
            {
                Obj("CMB_LookOptions", gLookOptions!),
                Obj("WorkbenchArmorA", Vanilla.WorkbenchArmorA),
            });
            lookF4se.Properties.AddRange(new ScriptProperty[]
            {
                Obj("CMB_LookOptions", gLookOptions!),
                FloatList("RimFinishV", look.RimFinishV),
            });
            // 2026-11-10a, test 52: the controller's Fixes_56 group, 2, after WorkbenchArmorA: the plugin's word to the
            // scripts (0xBF5-0xBF6). Not with `--look-build 2026-11-07a` (None: 2026-11-09a's).
            controller.Properties.InsertRange(controller.Properties.FindIndex(p => p.Name == "WorkbenchArmorA") + 1, new ScriptProperty[]
            {
                Obj("CMB_RiderQuickUse", gRiderQuickUse!),
                Obj("CMB_RideReady", gRideReady!),
            });
        }

        quest.VirtualMachineAdapter = new QuestAdapter
        {
            Version = 6,
            ObjectFormat = 2,
            Scripts = new ExtendedList<ScriptEntry> { controller, hotkey, gear, ram, lookF4se },
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

        // The ESL range's reserve (2026-11-02a): the customisation builds take their forms from 0x8BA (C1 up to 0xA13) and
        // keep 0xF01-0xFFF free, so no form of this generator may go past 0xF00.
        if (mod.EnumerateMajorRecords().FirstOrDefault(r => r.FormKey.ID > EslReserveFrom) is { } past)
            throw new InvalidOperationException($"{past.EditorID} is 0x{past.FormKey.ID:X}, past 0x{EslReserveFrom:X}: the light plugin's last IDs are kept free");
        // 0x8AF is CMB_LookCode's (kept free in 2026-11-06a; the customisation build makes it there by FormKey).
        if (mod.EnumerateMajorRecords().FirstOrDefault(r => r.FormKey.ID == LookCodeId) is not { EditorID: "CMB_LookCode" })
            throw new InvalidOperationException("0x8AF must be CMB_LookCode (CMB_Slope.dll looks for it), got " +
                                                (mod.EnumerateMajorRecords().FirstOrDefault(r => r.FormKey.ID == LookCodeId)?.EditorID ?? "nothing"));
        return mod;
    }

    // The highest form ID this generator may give (2026-11-02a): 0xF01-0xFFF stay free.
    const uint EslReserveFrom = 0xF00;
    // CMB_LookCode's fixed ID (kept free in 2026-11-06a; made there by FormKey since 2026-11-07a).
    public const uint LookCodeId = 0x8AF;

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

    // A hidden constant script effect for CMB_SwimWatchAbility (CMB_SwimWatchEffectScript), or with another
    // script for another watch (2026-11-01a: CMB_StaggerWatchAbility, CMB_StaggerWatchEffectScript).
    static MagicEffect WatchEffect(Fallout4Mod mod, string editorId, string name, Quest quest, bool wading,
                                   string script = "CMB_SwimWatchEffectScript")
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
            ? Vmad(Script(script, Obj("Controller", quest), Bool("Wading", true)))
            : Vmad(Script(script, Obj("Controller", quest)));
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
        armor.BipedBodyTemplate = new BipedBodyTemplate { FirstPersonFlags = BikeSlot };
        armor.Race.SetTo(Vanilla.HumanRace);
        armor.Armatures.Add(new ArmorAddonModel { AddonIndex = 0, ArmorAddon = arma.ToNullableLink() });
        armor.Value = 0;
        armor.Weight = 0;
        return armor;
    }

    // The headlamp's beam: a spotlight like the game's own power armor headlamp (test 31: with
    // attenuation 1/1/1 and 55 degrees ours lit nothing; the game's lights all have Constant 0,
    // Scalar 1, Exponent 2, FOV 70-100, radius 1420-2130), warm white, 30 m, 70 degrees, dynamic,
    // brighter than the stock lamp (fade 2); the second the shadow-casting kind. Placed as a
    // reference by the controller script (the ADDN records below would hang them on add-on nodes,
    // but no nif carries those since the lamp piece went, test 35).
    const uint HeadlampNodeIndex = 31985;
    static Light Headlamp(Fallout4Mod mod, string editorId, bool shadow)
    {
        var light = mod.Lights.AddNew(editorId);
        light.ObjectBounds = new ObjectBounds();
        light.Time = -1;
        light.Radius = 4000;   // test 34's ask: further and a bit wider at the same brightness (was 3000 / 70 deg / 2.4)
        light.Color = System.Drawing.Color.FromArgb(0, 255, 241, 224);
        light.Flags = (Light.Flag)1 | (shadow ? Light.Flag.ShadowSpotlight : Light.Flag.NonShadowSpotlight);   // 1: Dynamic (it moves)
        light.FalloffExponent = 1.0f;
        light.FOV = 78.0f;   // test 35: "a bit too wide and a little too bright" (was 85 / 2.7)
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
        light.FadeValue = 2.4f;
        return light;
    }

    // The tail lamp's light (test 47: "it's on, but it's not producing light"): a shadowless red spot at the lamp,
    // aimed back and 30 degrees down so it lights the road behind and not the rider's back; the plugin keeps it at the
    // lens and multiplies its colour by [TailLight] BrakeGain while braking.
    static Light TailLight(Fallout4Mod mod)
    {
        var light = mod.Lights.AddNew("CMB_TailLight");
        light.ObjectBounds = new ObjectBounds();
        light.Time = -1;
        light.Radius = 220;                                         // about 3 m: the road behind, the plate, the fender's tip
        light.Color = System.Drawing.Color.FromArgb(0, 255, 24, 10); // the shell's deep red
        light.Flags = (Light.Flag)1 | Light.Flag.NonShadowSpotlight; // Dynamic; no shadow (cheap, as the headlamp's plain one)
        light.FalloffExponent = 1.0f;
        light.FOV = 120.0f;
        light.NearClip = 5.0f;
        light.Constant = 0.0f; light.Scalar = 1.0f; light.Exponent = 2.0f;   // the game's own attenuation (test 31)
        light.FlickerPeriod = 0; light.FlickerIntensityAmplitude = 0; light.FlickerMovementAmplitude = 0;
        light.GodRaysNearClip = 0; light.Value = 0; light.Weight = 0;
        light.FadeValue = 0.75f;                                    // running; x3 braking = 2.25, as the shells' x2.5 / x8
        return light;
    }

    // An ADDN record: the game hangs its light on a BSValueNode whose value is the node index. The two
    // records stay (CMB_Slope.dll's add-on-node path looks for them), but no nif carries these indices
    // since the unskinned lamp piece went (test 35: the game never took that addon; the placed reference
    // lights the lamp), so the path is dormant.
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
    // The customisation build's records (2026-11-07a, C1), from look_options.json
    // ---------------------------------------------------------------------

    // tools/esp-generator/look_options.json (embedded in the generator, EspGenerator.csproj) is the one table of the look's
    // slots, options, badges, palette rows and faction sets. Every look record is made from it, in its order, and each ID
    // is checked against the table's own (an option's `ids`, a slot's `list_id` and `swaps_id`, `slot_lists`): the IDs are
    // save-stable (a save's CMB_Look_<slot> indices and the parked bike's swap keep their meaning), so a later build only
    // appends (at a list's end, IDs after 0xA13; look_ids.txt, `--look-ids`). check_plugin.py checks the written plugin
    // against the same table. Every slot's option 0 is the 2026-11-06a look; nothing here changes the bike until a script
    // attaches or applies a choice (CMB_LookOn 0: no Customise button, nothing attached).
    public sealed class LookRecords
    {
        // Since 2026-11-08a (C2) an option or a slot may carry `since` (the build that added it), a slot its own global's and
        // attach point's IDs (C1's are made in one run from FirstId), an option `crude` (PlateText), `rim_style` and `finish`
        // (Rims). A slot without swaps (the plate's two colour slots) has Swaps and SwapsId null and no sources.
        public sealed record Option(int Index, string Key, string Name, string Kind, float? Cnam, (string Component, uint Count)[] Cost,
                                    string? Perk, string? Loose, (string From, string To)[]? Swap, string?[] Ids,
                                    string? Since, bool Crude, int? RimStyle, string? Finish);
        public sealed record Slot(string Key, string Ap, string Name, string Global, int Default, string List, string? Swaps,
                                  string ListId, string? SwapsId, string[] Sources, Option[] Options,
                                  string? Since, string? GlobalId, string? ApId);
        public sealed record Set(int Index, string Key, string Name, int? Paint, int? TankLeft, int? TankRight, int? Fender, int? Plate);

        // The first ID after 2026-11-06a's forms; CMB_LookCode is LookCodeId (0x8AF), the one below it.
        public const uint FirstId = 0x8BA;
        // The builds the table knows: C1's entries carry no `since`, C2's "2026-11-08a". The generator's `--look-build <b>`
        // sets Through, and LoadTable drops every entry of a later build: `--look-build 2026-11-07a` makes 2026-11-07a's
        // ESP (and MCM) byte for byte, the off value of everything C2 adds.
        public const string C1Build = "2026-11-07a", C2Build = "2026-11-08a";
        public static readonly string[] Builds = { C1Build, C2Build };
        public static string Through = C2Build;
        // 2026-11-09a (test 51): `--recipe-bench CMB_WorkbenchBike` puts the recipes' BNAM back (MakeOption).
        public static bool RecipeBench;
        public const string ToolboxModel = @"SetDressing\Toolbox\Toolbox_Large.nif";                       // the game's, by path
        public const string BenchModel = @"Furniture\Workstations\WorkbenchArmor\WorkstationArmorB01.nif"; // WorkbenchArmorA's, by path
        public const string LooseModModel = @"Props\ModsPartBox\ModCrate.nif";                              // the game's loose mods'
        // The toolbox's bounds (the game's Loot_ToolboxLarge) and the bench's (WorkbenchArmorA), from the tester's dump.
        static ObjectBounds ToolboxBounds() => new() { First = new P3Int16(-17, -26, 0), Second = new P3Int16(13, 25, 34) };
        static ObjectBounds BenchBounds() => new() { First = new P3Int16(-71, -53, -7), Second = new P3Int16(98, 64, 87) };

        public Slot[] Slots { get; }
        public Set[] Sets { get; }
        LookRecords(Slot[] slots, Set[] sets) { Slots = slots; Sets = sets; }

        public GlobalFloat LookCode { get; private set; } = null!;
        public GlobalFloat LookOn { get; private set; } = null!;
        public GlobalFloat LookFree { get; private set; } = null!;
        public GlobalFloat FactionSet { get; private set; } = null!;
        public GlobalFloat KitMode { get; private set; } = null!;
        public GlobalFloat KitWorked { get; private set; } = null!;
        public GlobalFloat KitBagLink { get; private set; } = null!;
        public Keyword MaBike { get; private set; } = null!;
        public Keyword WorkbenchBike { get; private set; } = null!;
        public Armor BikeLook { get; private set; } = null!;
        public Furniture FieldKit { get; private set; } = null!;
        public Furniture FieldKitArmorKw { get; private set; } = null!;
        public Furniture FieldKitBench { get; private set; } = null!;
        public MovableStatic FieldKitBox { get; private set; } = null!;
        public MaterialSwap LookSwap { get; private set; } = null!;
        public FormList Categories { get; private set; } = null!;
        public FormList SwapLists { get; private set; } = null!;
        readonly Dictionary<string, GlobalFloat> slotGlobals = new();
        public GlobalFloat SlotGlobal(string slot) => slotGlobals[slot];
        // 2026-11-08a: the four colour values at fixed IDs and the three the MCM sets, by EditorID; the table's C2 parts the
        // fills read. HasC2 false (`--look-build 2026-11-07a`): none made, nothing filled.
        readonly Dictionary<string, GlobalFloat> c2Globals = new();
        public GlobalFloat C2Global(string editorId) => c2Globals[editorId];
        public bool HasC2 => Slots.Any(s => s.Since != null) || Slots.Any(s => s.Options.Any(o => o.Since != null));
        public Slot SlotOf(string key) => Slots.First(s => s.Key == key);
        public int[] PaintRow { get; private set; } = Array.Empty<int>();
        public int[] PlateOwnText { get; private set; } = Array.Empty<int>();
        public int[] PlateOwnInk { get; private set; } = Array.Empty<int>();
        public int[] PlateOwnBack { get; private set; } = Array.Empty<int>();
        public (string Body, string Hue)[] RimBodyTargets { get; private set; } = Array.Empty<(string, string)>();
        public int[] SetPlate => Sets.Select(s => s.Plate ?? -1).ToArray();
        public int[] RimStyle => SlotOf("Rims").Options.Select(o => o.RimStyle ?? 0).ToArray();
        public int[] RimBody => SlotOf("Rims").Options.Select(o => o.Finish == "body" ? 1 : 0).ToArray();
        // 2026-11-09a (test 51: the parked bike grey after an MCM apply): per Rims option, its finish's own palette V, (row +
        // 0.5) / 8 of rim_p.dds for a finish whose rim_finishes palette is a row (satin 0.0625, gloss 0.1875, bronze 0.3125,
        // gunmetal 0.4375); -1 for the stock cast rim (no finish), chrome (no palette) and body (Compose's rimV covers it).
        // look_wheels.py's finish_v without its body and bodyhue cases.
        public float[] RimFinishV { get; private set; } = Array.Empty<float>();
        public int[] TextCrude => SlotOf("PlateText").Options.Select(o => o.Crude ? 1 : 0).ToArray();
        // The controller's arrays: per faction set (index = CMB_LookFactionSet; 0 "(none)" -1) its Paint, left tank and fender
        // indices; "<slot>:<key>" for every option, slot-major; each slot's first index in Keys.
        public int[] SetPaint => Sets.Select(s => s.Paint ?? -1).ToArray();
        public int[] SetTank => Sets.Select(s => s.TankLeft ?? -1).ToArray();
        public int[] SetFender => Sets.Select(s => s.Fender ?? -1).ToArray();
        public string[] Keys => Slots.SelectMany(s => s.Options.Select(o => $"{s.Key}:{o.Key}")).ToArray();
        public int[] SlotStart => Slots.Select((s, i) => Slots.Take(i).Sum(x => x.Options.Length)).ToArray();

        // The embedded table.
        public static JsonElement LoadTable()
        {
            using var stream = typeof(LookRecords).Assembly.GetManifestResourceStream("look_options.json")
                ?? throw new InvalidOperationException("look_options.json isn't in the generator (EspGenerator.csproj embeds it)");
            using var doc = JsonDocument.Parse(stream);
            return Until(doc.RootElement, Through);
        }
        // The table up to a build: every entry (an array's element, an object's member) whose `since` is a later build than
        // `through` is dropped. Through 2026-11-07a that is every C2 entry (the six slots, Paint's option 45, paint row 43,
        // c2_ids, hue_palette; the C2-only sections the C1 code never reads stay), so the ESP is 2026-11-07a's.
        static JsonElement Until(JsonElement root, string through)
        {
            static bool Later(System.Text.Json.Nodes.JsonNode? n, string through) =>
                n is System.Text.Json.Nodes.JsonObject o && o.TryGetPropertyValue("since", out var s)
                && string.CompareOrdinal(s?.GetValue<string>(), through) > 0;
            static void Drop(System.Text.Json.Nodes.JsonNode? n, string through)
            {
                if (n is System.Text.Json.Nodes.JsonArray a)
                {
                    for (int i = a.Count - 1; i >= 0; i--)
                        if (Later(a[i], through)) a.RemoveAt(i); else Drop(a[i], through);
                }
                else if (n is System.Text.Json.Nodes.JsonObject o)
                {
                    foreach (var key in o.Select(p => p.Key).ToList())
                        if (Later(o[key], through)) o.Remove(key); else Drop(o[key], through);
                }
            }
            if (!Builds.Contains(through))
                throw new InvalidOperationException($"--look-build {through}: the table knows {string.Join(" and ", Builds)}");
            var node = System.Text.Json.Nodes.JsonNode.Parse(root.GetRawText())!;
            Drop(node, through);
            using var filtered = JsonDocument.Parse(node.ToJsonString());
            return filtered.RootElement.Clone();
        }
        static string? S(JsonElement e, string name) => e.GetProperty(name).ValueKind == JsonValueKind.Null ? null : e.GetProperty(name).GetString();
        static int? I(JsonElement e, string name) => e.GetProperty(name).ValueKind == JsonValueKind.Null ? null : e.GetProperty(name).GetInt32();
        // An optional field (C2's: absent from C1's entries).
        static JsonElement? Opt(JsonElement e, string name) => e.TryGetProperty(name, out var v) && v.ValueKind != JsonValueKind.Null ? v : null;
        static uint Id(string hex) => Convert.ToUInt32(hex, 16);

        public static Slot[] ReadSlots(JsonElement root) => root.GetProperty("slots").EnumerateArray().Select(s => new Slot(
            S(s, "key")!, S(s, "ap")!, S(s, "name")!, S(s, "global")!, s.GetProperty("default").GetInt32(), S(s, "list")!, S(s, "swaps"),
            S(s, "list_id")!, S(s, "swaps_id"), s.GetProperty("sources").EnumerateArray().Select(x => x.GetString()!).ToArray(),
            s.GetProperty("options").EnumerateArray().Select(o => new Option(
                o.GetProperty("index").GetInt32(), S(o, "key")!, S(o, "name")!, S(o, "kind")!,
                o.GetProperty("cnam").ValueKind == JsonValueKind.Null ? null : o.GetProperty("cnam").GetSingle(),
                o.GetProperty("cost").EnumerateArray().Select(c => (c[0].GetString()!, c[1].GetUInt32())).ToArray(),
                S(o, "perk"), S(o, "loose"),
                o.GetProperty("swap").ValueKind == JsonValueKind.Null ? null
                    : o.GetProperty("swap").EnumerateArray().Select(e => (e[0].GetString()!, e[1].GetString()!)).ToArray(),
                o.GetProperty("ids").EnumerateArray().Select(x => x.ValueKind == JsonValueKind.Null ? null : x.GetString()).ToArray(),
                Opt(o, "since")?.GetString(), Opt(o, "crude")?.GetBoolean() ?? false, Opt(o, "rim_style")?.GetInt32(), Opt(o, "finish")?.GetString()))
            .ToArray(), Opt(s, "since")?.GetString(), Opt(s, "global_id")?.GetString(), Opt(s, "ap_id")?.GetString())).ToArray();

        public static Set[] ReadSets(JsonElement root) => root.GetProperty("sets").EnumerateArray().Select(s => new Set(
            s.GetProperty("index").GetInt32(), S(s, "key")!, S(s, "name")!, I(s, "paint"), I(s, "tank_left"), I(s, "tank_right"), I(s, "fender"),
            Opt(s, "plate")?.GetInt32()))
            .ToArray();

        // The table's own rules, before anything is made from it.
        static void CheckTable(JsonElement root, Slot[] slots, Set[] sets)
        {
            var fail = new List<string>();
            foreach (var (name, fk) in Vanilla.Components)
                if (!root.GetProperty("components").TryGetProperty(name, out var v) || Id(v.GetString()!) != fk.ID)
                    fail.Add($"components.{name}: not {fk.ID:X6} (Vanilla.Components)");
            foreach (var (name, fk) in Vanilla.Perks)
                if (!root.GetProperty("perks").TryGetProperty(name, out var v) || Id(v.GetString()!) != fk.ID)
                    fail.Add($"perks.{name}: not {fk.ID:X6} (Vanilla.Perks)");
            // 2026-11-08a's kinds: hue (Paint 45), rim, tyre, design (Plate), text (PlateText), colour (PlateInk, PlateBack: an
            // object mod and a recipe, no swap). `follow` is TankR's last ("Same as the left") or PlateText's 0 (the plate's own).
            var kinds = new[] { "identity", "off", "badge", "paint", "mirror", "follow", "hue", "rim", "tyre", "design", "text", "colour" };
            foreach (var s in slots)
            {
                for (int i = 0; i < s.Options.Length; i++)
                {
                    var o = s.Options[i];
                    if (o.Index != i) fail.Add($"{s.Key}:{o.Key}: index {o.Index} at position {i}");
                    if (!kinds.Contains(o.Kind)) fail.Add($"{s.Key}:{o.Key}: kind {o.Kind}");
                    if ((o.Kind is "follow" or "colour") != (o.Swap == null) || (o.Swap == null) != (o.Ids[0] == null))
                        fail.Add($"{s.Key}:{o.Key}: only a `follow` or `colour` option has no swap (and no MSWP ID)");
                    if (o.Kind == "follow" && !(s.Key == "TankR" && i == s.Options.Length - 1) && !(s.Key == "PlateText" && i == 0))
                        fail.Add($"{s.Key}:{o.Key}: `follow` is only TankR's last option and PlateText's first");
                    if ((o.Kind == "colour") != (s.Swaps == null))
                        fail.Add($"{s.Key}:{o.Key}: a `colour` option is in a slot without swaps, and only there");
                    if (o.Crude && (s.Key != "PlateText" || o.Kind != "text"))
                        fail.Add($"{s.Key}:{o.Key}: only a plate text is crude");
                    if (o.Swap != null && !o.Swap.Select(e => e.From).SequenceEqual(s.Sources))
                        fail.Add($"{s.Key}:{o.Key}: its swap's sources aren't the slot's, in order");
                    foreach (var (c, _) in o.Cost)
                        if (!Vanilla.Components.ContainsKey(c)) fail.Add($"{s.Key}:{o.Key}: component {c}");
                    if (o.Perk != null && !Vanilla.Perks.ContainsKey(o.Perk)) fail.Add($"{s.Key}:{o.Key}: perk {o.Perk}");
                    if (o.Loose != null && s.Key != "Mirrors") fail.Add($"{s.Key}:{o.Key}: a loose mod outside the mirrors");
                    if (o.Since != null && o.Since != s.Since && s.Since != null) fail.Add($"{s.Key}:{o.Key}: since {o.Since}, its slot's {s.Since}");
                }
                var o0 = s.Options[0];
                if (!(o0.Kind is "identity" or "mirror" && o0.Swap!.All(e => e.From == e.To)) && !(o0.Kind == "follow" && s.Key == "PlateText")
                    && !(o0.Kind == "colour" && o0.Cost.Length == 0))
                    fail.Add($"{s.Key}: option 0 isn't the identity, PlateText's `follow` or a free `colour` (the 2026-11-07a look)");
                if (s.Default < 0 || s.Default >= s.Options.Length) fail.Add($"{s.Key}: default {s.Default}");
                if ((s.Swaps == null) != (s.SwapsId == null) || (s.Swaps == null) != (s.Sources.Length == 0))
                    fail.Add($"{s.Key}: a slot without swaps has no swap list and no sources, and only it");
            }
            // The colour slots last (the swap lists' list holds the others' in slot order: index = slot).
            var firstColour = Array.FindIndex(slots, s => s.Swaps == null);
            if (firstColour >= 0 && slots.Skip(firstColour).Any(s => s.Swaps != null))
                fail.Add("the slots without swaps (PlateInk, PlateBack) must be the last");
            var sources = slots.SelectMany(s => s.Sources.Select(src => (s.Key, src))).ToArray();
            foreach (var g in sources.GroupBy(x => x.src.ToLowerInvariant()).Where(g => g.Count() > 1))
                fail.Add($"the source {g.Key} is in {string.Join(" and ", g.Select(x => x.Key))}: a source belongs to one slot");
            for (int i = 0; i < sets.Length; i++)
                if (sets[i].Index != i || (i == 0) != (sets[i].Paint == null)) fail.Add($"set {sets[i].Key}: index {sets[i].Index} at {i}");
            if (slots.Any(s => s.Since != null) || slots.Any(s => s.Options.Any(o => o.Since != null)))
                CheckTableC2(root, slots, sets, fail);
            if (fail.Count > 0)
                throw new InvalidOperationException("look_options.json:\n  " + string.Join("\n  ", fail));
        }

        // 2026-11-08a: the second block's IDs (every one once, 0xA14 on, contiguous: c2_ids), C1's all below it, and the
        // C2 sections the fills read (the plates against the Plate options, the texts against PlateText's, the colours
        // against the colour slots', the rim styles and finishes, the paint rows of the Paint options).
        static void CheckTableC2(JsonElement root, Slot[] slots, Set[] sets, List<string> fail)
        {
            var c2 = root.GetProperty("c2_ids");
            uint first = Id(c2.GetProperty("first").GetString()!), last = Id(c2.GetProperty("last").GetString()!);
            var c2Ids = new List<(string What, string Id)>();
            foreach (var g in root.GetProperty("fixed_globals").EnumerateArray().Concat(root.GetProperty("script_globals").EnumerateArray()))
                c2Ids.Add((S(g, "edid")!, S(g, "id")!));
            foreach (var s in slots.Where(s => s.Since != null))
            {
                if (s.GlobalId == null || s.ApId == null) fail.Add($"{s.Key}: a C2 slot without global_id or ap_id");
                c2Ids.Add((s.Global, s.GlobalId ?? "-"));
            }
            foreach (var s in slots.Where(s => s.Since != null)) c2Ids.Add((s.Ap, s.ApId ?? "-"));
            foreach (var s in slots.Where(s => s.Since == null))
                foreach (var o in s.Options.Where(o => o.Since != null))
                    c2Ids.AddRange(o.Ids.Where(x => x != null).Select(x => ($"{s.Key}:{o.Key}", x!)));
            foreach (var s in slots.Where(s => s.Since != null))
                foreach (var o in s.Options)
                    c2Ids.AddRange(o.Ids.Where(x => x != null).Select(x => ($"{s.Key}:{o.Key}", x!)));
            foreach (var s in slots.Where(s => s.Since != null)) c2Ids.Add((s.List, s.ListId));
            foreach (var s in slots.Where(s => s.Since != null && s.SwapsId != null)) c2Ids.Add((s.Swaps!, s.SwapsId!));
            // In that order, the generator's: each ID the one after the last.
            for (int i = 0; i < c2Ids.Count; i++)
                if (c2Ids[i].Id == "-" || Id(c2Ids[i].Id) != first + (uint)i)
                    fail.Add($"{c2Ids[i].What}: {c2Ids[i].Id}, expected {first + (uint)i:X6} (C2's IDs from {first:X6} in the table's order, once each)");
            if (c2Ids.Count != c2.GetProperty("count").GetInt32() || first + (uint)c2Ids.Count - 1 != last
                || Id(c2.GetProperty("next").GetString()!) != last + 1)
                fail.Add($"c2_ids: {c2Ids.Count} IDs from {first:X6}, the table says {c2.GetProperty("count").GetInt32()} to {last:X6}");
            var c1Ids = slots.Where(s => s.Since == null).SelectMany(s => s.Options.Where(o => o.Since == null).SelectMany(o => o.Ids)
                .Append(s.ListId).Append(s.SwapsId)).Where(x => x != null).Select(x => Id(x!)).ToArray();
            if (c1Ids.Any(x => x >= first)) fail.Add($"a C1 ID at or past {first:X6} (C1's block ends below C2's)");
            if (root.GetProperty("fixed_globals").EnumerateArray().Any(g => g.GetProperty("value").GetSingle() != -1)) fail.Add("fixed_globals: a colour value's default isn't -1 (= don't write)");

            Slot Of(string key) => slots.First(s => s.Key == key);
            var paint = Of("Paint");
            var rows = root.GetProperty("paint_row_of_option").EnumerateArray().Select(x => x.GetInt32()).ToArray();
            if (rows.Length != paint.Options.Length || rows[0] != 43 || paint.Options.Any(o => (o.Kind == "hue") != (rows[o.Index] == -1)))
                fail.Add($"paint_row_of_option: {rows.Length} rows for {paint.Options.Length} Paint options (Factory 43, -1 only the hue)");
            var finishes = root.GetProperty("rim_finishes").EnumerateArray().Select(f => S(f, "key")!).ToArray();
            foreach (var o in Of("Rims").Options)
                if (o.RimStyle is not (>= 0 and <= 7) || (o.Index == 0) != (o.Finish == null) || (o.Finish != null && !finishes.Contains(o.Finish)))
                    fail.Add($"Rims:{o.Key}: rim_style {o.RimStyle} finish {o.Finish} (0-7; a rim_finishes key, Stock none)");
            var bodyTargets = root.GetProperty("rim_body_targets").EnumerateArray().Select(x => x[0].GetString()!).ToArray();
            var bodyUsed = Of("Rims").Options.Where(o => o.Finish == "body").SelectMany(o => o.Swap!.Select(e => e.To)).Where(t => t.Contains("_body")).Distinct();
            if (!bodyUsed.OrderBy(x => x).SequenceEqual(bodyTargets.OrderBy(x => x)))
                fail.Add("rim_body_targets: not the body-colour options' targets");
            var plates = root.GetProperty("plates").EnumerateArray().ToArray();
            var plate = Of("Plate");
            var text = Of("PlateText");
            for (int i = 0; i < Math.Max(plates.Length, plate.Options.Length); i++)
            {
                if (i >= plates.Length || i >= plate.Options.Length || plates[i].GetProperty("index").GetInt32() != i || S(plates[i], "key") != plate.Options[i].Key)
                { fail.Add($"plates[{i}]: not the Plate option {i}"); continue; }
                int own = plates[i].GetProperty("own_text").GetInt32(), ink = plates[i].GetProperty("own_ink").GetInt32(), back = plates[i].GetProperty("own_back").GetInt32();
                if (own < 1 || own >= text.Options.Length || text.Options[own].Crude || ink is < 0 or > 15 || back < (i == 0 ? -1 : 0) || back > 15)
                    fail.Add($"plates[{i}]: own text {own} (a PlateText index, not crude), ink {ink}, background {back} (0-15; Stock -1)");
            }
            var texts = root.GetProperty("plate_texts").EnumerateArray().ToArray();
            if (texts.Length != text.Options.Length - 2 || texts.Any(t => t.GetProperty("index").GetInt32() is var k && (k < 2 || k >= text.Options.Length
                    || text.Options[k].Key != S(t, "key") || text.Options[k].Kind != "text" || text.Options[k].Crude != (S(t, "set") == "crude"))))
                fail.Add("plate_texts: not PlateText's options 2 on (key, crude = the set `crude`)");
            var colours = root.GetProperty("plate_colours").EnumerateArray().ToArray();
            foreach (var s in slots.Where(s => s.Swaps == null))
                if (s.Options.Length != colours.Length + 1 || s.Options.Skip(1).Select(o => o.Key).Where((k, j) => k != S(colours[j], "key")).Any())
                    fail.Add($"{s.Key}: its options 1 on aren't plate_colours");
            foreach (var x in sets)
                if (x.Plate is int p && (p < 1 || p >= plate.Options.Length)) fail.Add($"set {x.Key}: plate {p}");
        }

        public static LookRecords Build(Fallout4Mod mod, Armor ridingArmor, Armor ridingArmorFrame, Message parkedMenu)
        {
            var root = LoadTable();
            var look = new LookRecords(ReadSlots(root), ReadSets(root));
            CheckTable(root, look.Slots, look.Sets);
            // The C1 block is made exactly as 2026-11-07a's, from the entries without `since` (C1's five slots and their
            // first options); C2's (BuildC2) follows it, then the in-place work over every slot.
            var c1 = look.Slots.Where(s => s.Since == null).Select(s => s with { Options = s.Options.Where(o => o.Since == null).ToArray() }).ToArray();
            if (mod.ModHeader.Stats.NextFormID != FirstId)
                throw new InvalidOperationException($"the look's records start at 0x{FirstId:X} (look_options.json's IDs), the next ID is 0x{mod.ModHeader.Stats.NextFormID:X}");
            var before = mod.EnumerateMajorRecords().Count();
            var made = new List<(IMajorRecordGetter Record, uint Id)>();   // each with the ID the table gives it
            uint head = FirstId;
            T Next<T>(T r) where T : IMajorRecordGetter { made.Add((r, head++)); return r; }
            T At<T>(T r, string id) where T : IMajorRecordGetter { made.Add((r, Id(id))); return r; }

            // The fixed one: CMB_LookCode at 0x8AF by FormKey (CMB_Slope.dll finds it by ID; the next ID stays 0x8BA). Bits 0-1
            // the mirror, bit 2 set, bits 3-6 the rim style (2026-11-08a: 0 the cast rim, 1-7 the styles; bits 7-8 kept for later
            // builds), written only by the controller's ApplyLook; 0 = the plugin's own [Look] Mirrors.
            look.LookCode = new GlobalFloat(new FormKey(mod.ModKey, LookCodeId), Fallout4Release.Fallout4)
            {
                EditorID = "CMB_LookCode",
                Data = 0,
                OutputChar = true,
            };
            mod.Globals.Add(look.LookCode);
            made.Add((look.LookCode, LookCodeId));
            // The MCM's and the scripts' globals: Customise at the bike (1; 0 = 2026-11-06a), free customising (0), each
            // slot's choice (the table's default: 0, the right tank 17 "Same as the left", 0, 0, 0), the faction set (0, a
            // one-shot at Apply), the kit's mode (0 automatic; 3 the armour bench), the mode automatic found (-1 none yet),
            // the side bag's parts (1).
            look.LookOn = Next(Global(mod, "CMB_LookOn", 1));
            look.LookFree = Next(Global(mod, "CMB_LookFree", 0));
            foreach (var s in c1)
                look.slotGlobals[s.Key] = Next(Global(mod, s.Global, s.Default));
            look.FactionSet = Next(Global(mod, "CMB_LookFactionSet", 0));
            look.KitMode = Next(Global(mod, "CMB_KitMode", 0));
            look.KitWorked = Next(Global(mod, "CMB_KitWorked", -1));
            look.KitBagLink = Next(Global(mod, "CMB_KitBagLink", 1));
            // The keywords: the bike's mod association (the object mods' target, the three armours' keyword), the field kit's
            // workbench keyword (every recipe's; type None as the game's WorkbenchArmor), C1's five attach points named for
            // the menu.
            look.MaBike = Next(Kw(mod, "CMB_ma_Bike", Keyword.TypeEnum.ModAssociation, null));
            look.WorkbenchBike = Next(Kw(mod, "CMB_WorkbenchBike", Keyword.TypeEnum.None, null));
            var aps = c1.ToDictionary(s => s.Key, s => Next(Kw(mod, s.Ap, Keyword.TypeEnum.AttachPoint, s.Name)));
            // The look as an item (held only while customising, so the armour menu lists it): playable, slot 57, the parked
            // nif, previewed small and turned (the test tunes the transform); its attach points and default template (each
            // slot's option 0) come with the in-place work, after the C2 block.
            var preview = Next(mod.Transforms.AddNew("CMB_BikeLookPreview"));
            preview.Scale = 0.45f;
            preview.Rotation = new P3Float(0, 0, 135);
            preview.ZoomMin = 0.5f;
            preview.ZoomMax = 1.5f;
            var item = WornBike(mod, "CMB_BikeLookAA", "CMB_BikeLook", ParkedBikeModel, ParkedBikeModel);
            Next(mod.ArmorAddons.First(a => a.EditorID == "CMB_BikeLookAA"));
            look.BikeLook = Next(item);   // after its addon (WornBike makes the two in that order)
            item.MajorFlags &= ~Armor.MajorFlag.NonPlayable;
            item.Description = "The bike's look. You hold it only while you customise.";
            item.ObjectBounds = Bounds(120, 120, 0, 120);
            item.WorldModel = new GenderedItem<ArmorModel?>(new ArmorModel { Model = new Model { File = ParkedBikeModel } }, null);
            item.PreviewTransform.SetTo(preview);
            item.Keywords = new() { look.MaBike };
            item.AttachParentSlots = new();
            // The field kit (custom 6.1, the plan's ladder): 1 the toolbox (the game's by path) with an armour bench's data, our
            // marker and keyword; 2 the same with the armour bench's own keywords too; 3 the armour bench's model by path with
            // its own marker and keywords plus ours, and the toolbox beside it as a movable static. No scripts on them.
            look.FieldKit = Next(Kit(mod, "CMB_FieldKit", ToolboxModel, ToolboxBounds(), new P3Float(-30, 20, 0),
                look.WorkbenchBike.FormKey, Vanilla.FurnitureForce3rdPerson, Vanilla.AnimFurnWorkbenchArmorA, Vanilla.FurnitureScaleActorToOne));
            look.FieldKitArmorKw = Next(Kit(mod, "CMB_FieldKitArmorKw", ToolboxModel, ToolboxBounds(), new P3Float(-30, 20, 0),
                look.WorkbenchBike.FormKey, Vanilla.FurnitureForce3rdPerson, Vanilla.AnimFurnWorkbenchArmorA, Vanilla.FurnitureScaleActorToOne,
                Vanilla.WorkbenchArmor, Vanilla.WorkbenchGeneral));
            look.FieldKitBench = Next(Kit(mod, "CMB_FieldKitBench", BenchModel, BenchBounds(), new P3Float(0, 0, 0),
                Vanilla.WorkbenchArmor, Vanilla.FurnitureForce3rdPerson, Vanilla.AnimFurnWorkbenchArmorA, Vanilla.FurnitureScaleActorToOne,
                Vanilla.WorkbenchGeneral, look.WorkbenchBike.FormKey));
            look.FieldKitBox = Next(mod.MovableStatics.AddNew("CMB_FieldKitBox"));
            look.FieldKitBox.Name = "Field kit";
            look.FieldKitBox.Model = new Model { File = ToolboxModel };
            look.FieldKitBox.ObjectBounds = ToolboxBounds();
            // The composed swap CMB_LookF4SE fills (SetRemapData) for the parked and first-person bikes: empty here.
            look.LookSwap = Next(mod.MaterialSwaps.AddNew("CMB_LookSwap"));
            // The mirrors' loose mods (the three mirrors; "None" is no part), as the game's armour loose mods.
            var loose = new Dictionary<string, MiscItem>();
            foreach (var o in c1.SelectMany(s => s.Options).Where(o => o.Loose != null))
            {
                var m = Next(mod.MiscItems.AddNew(o.Loose));
                m.Name = "Motorbike mirrors: " + char.ToLowerInvariant(o.Name[0]) + o.Name[1..];
                m.ObjectBounds = new ObjectBounds();
                m.Model = new Model { File = LooseModModel };
                m.PreviewTransform.SetTo(Vanilla.MiscMod01);
                m.Keywords = new() { new FormLink<IKeywordGetter>(Vanilla.ObjectTypeLooseMod) };
                m.Value = 5;
                m.Weight = 0.5f;
                loose.Add(o.Loose!, m);
            }
            // Per option, at the table's IDs: the material swap, the object mod and the recipe (MakeOption).
            var mods = new Dictionary<string, List<ArmorModification>>();
            var swaps = new Dictionary<string, List<MaterialSwap>>();
            foreach (var s in c1)
            {
                mods[s.Key] = new();
                swaps[s.Key] = new();
                foreach (var o in s.Options)
                    MakeOption(mod, look, s, o, aps[s.Key], loose, mods, swaps, made);
            }
            // The lists, index = choice: the options (the object mods) and the swaps (TankR's 17 entries: its 18th option has
            // none), then the two lists of lists in slot order.
            var optionLists = c1.Select(s => At(List(mod, s.List, mods[s.Key].Select(m => m.FormKey)), s.ListId)).ToList();
            var swapLists = c1.Select(s => At(List(mod, s.Swaps!, swaps[s.Key].Select(m => m.FormKey)), s.SwapsId!)).ToList();
            var slotLists = root.GetProperty("slot_lists");
            look.Categories = At(List(mod, slotLists.GetProperty("options")[0].GetString()!, optionLists.Select(l => l.FormKey)),
                                 slotLists.GetProperty("options")[1].GetString()!);
            look.SwapLists = At(List(mod, slotLists.GetProperty("swaps")[0].GetString()!, swapLists.Select(l => l.FormKey)),
                                slotLists.GetProperty("swaps")[1].GetString()!);

            // 2026-11-08a (C2): the second block, 0xA14 on (the table's c2_ids), after C1's lists.
            if (look.HasC2)
                BuildC2(mod, look, root, c1, aps, loose, mods, swaps, optionLists, swapLists, made);

            // In place, one loop over every slot (C1's five in their order, then C2's): the look item's attach points and its
            // default template (each slot's option 0, the stock look, on its attach point); the riding armours take the
            // look's mods (the keyword, the attach points; no template); C1's option lists and swap lists take C2's options
            // of their slots (Paint's 46th, Free colour); the lists of lists take C2's lists (the colour slots have no swaps).
            foreach (var s in look.Slots)
                item.AttachParentSlots.Add(aps[s.Key]);
            item.ObjectTemplates = new()
            {
                new ObjectTemplate<Armor.Property>
                {
                    Name = "Default",
                    Default = true,
                    Includes = new(look.Slots.Select(s => new ObjectTemplateInclude { Mod = mods[s.Key][0].ToLink<IAObjectModificationGetter>(), AttachPointIndex = 0 })),
                },
            };
            foreach (var a in new[] { ridingArmor, ridingArmorFrame })
            {
                a.Keywords ??= new();
                a.Keywords.Add(look.MaBike);
                a.AttachParentSlots ??= new();
                foreach (var s in look.Slots)
                    a.AttachParentSlots.Add(aps[s.Key]);
            }
            for (int i = 0; i < c1.Length; i++)
            {
                foreach (var m in mods[c1[i].Key].Skip(optionLists[i].Items.Count))
                    optionLists[i].Items.Add(new FormLink<IFallout4MajorRecordGetter>(m.FormKey));
                foreach (var w in swaps[c1[i].Key].Skip(swapLists[i].Items.Count))
                    swapLists[i].Items.Add(new FormLink<IFallout4MajorRecordGetter>(w.FormKey));
            }
            foreach (var l in optionLists.Skip(look.Categories.Items.Count))
                look.Categories.Items.Add(new FormLink<IFallout4MajorRecordGetter>(l.FormKey));
            foreach (var l in swapLists.Skip(look.SwapLists.Items.Count))
                look.SwapLists.Items.Add(new FormLink<IFallout4MajorRecordGetter>(l.FormKey));
            // The parked bike's menu: Customise (shown while CMB_LookOn is 1) between Open side bag and Cancel: 0 ride, 1 the
            // bag, 2 customise, 3 cancel (a hidden button keeps the others' indices).
            if (!parkedMenu.MenuButtons.Select(b => b.Text?.String).SequenceEqual(new[] { "Ride", "Open side bag", "Cancel" }))
                throw new InvalidOperationException("CMB_ParkedMenu's buttons aren't Ride, Open side bag, Cancel: Customise goes before Cancel");
            var customise = new MessageButton { Text = "Customise" };
            customise.Conditions.Add(Is(Condition.Function.GetGlobalValue, look.LookOn.FormKey, 1));
            parkedMenu.MenuButtons.Insert(2, customise);

            // Every record at the table's ID (C1's 347, C2's 477), none past the last list.
            var wrong = made.Where(x => x.Record.FormKey.ID != x.Id).ToArray();
            if (wrong.Length > 0)
                throw new InvalidOperationException("look records off their IDs (look_options.json): " +
                    string.Join(", ", wrong.Take(5).Select(x => $"{x.Record.EditorID} 0x{x.Record.FormKey.ID:X} (expected 0x{x.Id:X})")));
            var count = mod.EnumerateMajorRecords().Count() - before;
            if (count != made.Count || made.Select(x => x.Id).Distinct().Count() != made.Count)
                throw new InvalidOperationException($"{count} look records made, {made.Count} at the table's IDs");
            if (mod.ModHeader.Stats.NextFormID != made.Max(x => x.Id) + 1)
                throw new InvalidOperationException($"the next ID after the look is 0x{mod.ModHeader.Stats.NextFormID:X}, not 0x{made.Max(x => x.Id) + 1:X}");
            return look;
        }

        // Per option, at the table's IDs: the material swap (none for a `follow` or `colour` option), the object mod on the
        // slot's attach point (the swap added; the loose mod for a mirror), the recipe on CMB_WorkbenchBike (the components;
        // the perk for a paint colour or a rim style; 2026-11-08a: a crude plate text's GetGlobalValue CMB_LookPlateCrude == 1).
        static void MakeOption(Fallout4Mod mod, LookRecords look, Slot s, Option o, Keyword ap, Dictionary<string, MiscItem> loose,
                               Dictionary<string, List<ArmorModification>> mods, Dictionary<string, List<MaterialSwap>> swaps,
                               List<(IMajorRecordGetter Record, uint Id)> made)
        {
            T At<T>(T r, string id) where T : IMajorRecordGetter { made.Add((r, Id(id))); return r; }
            MaterialSwap? sw = null;
            if (o.Swap != null)
            {
                sw = At(mod.MaterialSwaps.AddNew($"CMB_sw_{s.Key}_{o.Key}"), o.Ids[0]!);
                foreach (var (from, to) in o.Swap)
                    sw.Substitutions.Add(new MaterialSubstitution { OriginalMaterial = from, ReplacementMaterial = to, ColorRemappingIndex = o.Cnam });
                swaps[s.Key].Add(sw);
            }
            var omod = At(new ArmorModification(mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = $"CMB_mod_{s.Key}_{o.Key}" }, o.Ids[1]!);
            omod.Name = o.Name;
            omod.AttachPoint.SetTo(ap);
            omod.TargetOmodKeywords = new() { look.MaBike };
            if (sw != null)
                omod.Properties.Add(new ObjectModFormLinkIntProperty<Armor.Property>
                {
                    Property = Armor.Property.MaterialSwaps,
                    Record = new FormLink<IFallout4MajorRecordGetter>(sw.FormKey),
                    FunctionType = ObjectModProperty.FormLinkFunctionType.Add,
                });
            if (o.Loose != null)
                omod.LooseMod.SetTo(loose[o.Loose]);
            mod.ObjectModifications.Add(omod);
            mods[s.Key].Add(omod);
            var cobj = At(mod.ConstructibleObjects.AddNew($"CMB_co_{s.Key}_{o.Key}"), o.Ids[2]!);
            cobj.CreatedObject.SetTo(omod.FormKey);
            // 2026-11-09a (test 51, Q-K2: the game's 722 armour mod recipes have no BNAM, ours had CMB_WorkbenchBike): no
            // workbench keyword, as the game's; set only through 2026-11-07a (C1's ESP byte for byte) or with
            // `--recipe-bench CMB_WorkbenchBike` (an A/B ESP, never shipped).
            if (Through == C1Build || RecipeBench)
                cobj.WorkbenchKeyword.SetTo(look.WorkbenchBike);
            if (o.Cost.Length > 0)
                cobj.Components = new(o.Cost.Select(c => new ConstructibleObjectComponent
                {
                    Component = new FormLink<IItemGetter>(Vanilla.Components[c.Component]),
                    Count = c.Count,
                }));
            if (o.Perk != null)
                cobj.Conditions.Add(Is(Condition.Function.HasPerk, Vanilla.Perks[o.Perk], 1));
            if (o.Crude)
                cobj.Conditions.Add(Is(Condition.Function.GetGlobalValue, look.C2Global("CMB_LookPlateCrude").FormKey, 1));
            cobj.CreatedObjectCounts = new() { new ConstructibleCreatedObjectCount { Count = 1, Priority = 0 } };
        }

        // 2026-11-08a (C2): the second block, in the table's order (c2_ids, from 0xA14; each record at its ID, checked by
        // Build): the four colour values at their fixed IDs (-1 = the plugin writes nothing), the three globals the MCM sets
        // (the hue 210, the shade 1, the crude texts 1), the six slots' globals (0, the stock look) and attach points, Paint's
        // option 45 (Free colour), each C2 slot's options (a swap, an object mod and a recipe; PlateText's 0 and the colour
        // slots' without a swap), the six option lists and the four swap lists (index = choice; PlateText's from its option 1).
        static void BuildC2(Fallout4Mod mod, LookRecords look, JsonElement root, Slot[] c1, Dictionary<string, Keyword> aps,
                            Dictionary<string, MiscItem> loose, Dictionary<string, List<ArmorModification>> mods,
                            Dictionary<string, List<MaterialSwap>> swaps, List<FormList> optionLists, List<FormList> swapLists,
                            List<(IMajorRecordGetter Record, uint Id)> made)
        {
            T At<T>(T r, string id) where T : IMajorRecordGetter { made.Add((r, Id(id))); return r; }
            var first = Id(root.GetProperty("c2_ids").GetProperty("first").GetString()!);
            if (mod.ModHeader.Stats.NextFormID != first)
                throw new InvalidOperationException($"C2's records start at 0x{first:X} (look_options.json's c2_ids), the next ID is 0x{mod.ModHeader.Stats.NextFormID:X}");
            foreach (var g in root.GetProperty("fixed_globals").EnumerateArray().Concat(root.GetProperty("script_globals").EnumerateArray()))
                look.c2Globals[S(g, "edid")!] = At(Global(mod, S(g, "edid")!, g.GetProperty("value").GetSingle()), S(g, "id")!);
            var c2 = look.Slots.Where(s => s.Since != null).ToArray();
            foreach (var s in c2)
                look.slotGlobals[s.Key] = At(Global(mod, s.Global, s.Default), s.GlobalId!);
            foreach (var s in c2)
                aps[s.Key] = At(Kw(mod, s.Ap, Keyword.TypeEnum.AttachPoint, s.Name), s.ApId!);
            foreach (var s in look.Slots.Where(s => s.Since == null))
                foreach (var o in s.Options.Where(o => o.Since != null))
                    MakeOption(mod, look, s, o, aps[s.Key], loose, mods, swaps, made);
            foreach (var s in c2)
            {
                mods[s.Key] = new();
                swaps[s.Key] = new();
                foreach (var o in s.Options)
                    MakeOption(mod, look, s, o, aps[s.Key], loose, mods, swaps, made);
            }
            foreach (var s in c2)
                optionLists.Add(At(List(mod, s.List, mods[s.Key].Select(m => m.FormKey)), s.ListId));
            foreach (var s in c2.Where(s => s.Swaps != null))
                swapLists.Add(At(List(mod, s.Swaps!, swaps[s.Key].Select(m => m.FormKey)), s.SwapsId!));
            // The fills' tables: the Paint options' palette rows, the plates' own text, letters and background, the body-colour
            // rims' targets and their Free colour twins.
            look.PaintRow = root.GetProperty("paint_row_of_option").EnumerateArray().Select(x => x.GetInt32()).ToArray();
            var plates = root.GetProperty("plates").EnumerateArray().ToArray();
            look.PlateOwnText = plates.Select(p => p.GetProperty("own_text").GetInt32()).ToArray();
            look.PlateOwnInk = plates.Select(p => p.GetProperty("own_ink").GetInt32()).ToArray();
            look.PlateOwnBack = plates.Select(p => p.GetProperty("own_back").GetInt32()).ToArray();
            look.RimBodyTargets = root.GetProperty("rim_body_targets").EnumerateArray().Select(x => (x[0].GetString()!, x[1].GetString()!)).ToArray();
            // 2026-11-09a (test 51): per Rims option its finish's palette V, rim_palette's rows ((row + 0.5) / its height, 8);
            // -1 without a finish, for chrome (palette null) and body ("body").
            int finishRows = root.GetProperty("rim_palette").GetProperty("size")[1].GetInt32();
            var finishRow = root.GetProperty("rim_finishes").EnumerateArray().ToDictionary(f => S(f, "key")!,
                f => f.GetProperty("palette").ValueKind == JsonValueKind.Number ? f.GetProperty("palette").GetInt32() : -1);
            look.RimFinishV = look.SlotOf("Rims").Options.Select(o => o.Finish != null && finishRow[o.Finish] >= 0
                ? (finishRow[o.Finish] + 0.5f) / finishRows : -1.0f).ToArray();
        }

        static Keyword Kw(Fallout4Mod mod, string editorId, Keyword.TypeEnum type, string? name)
        {
            var k = mod.Keywords.AddNew(editorId);
            k.Type = type;
            k.Color = System.Drawing.Color.FromArgb(0, 0, 0, 0); // CNAM is a required field
            if (name != null)
                k.Name = name;
            return k;
        }

        // A field kit: an armour bench's data (WBDT 7 in one byte, MNAM 0x40000001: the model flag and marker 0) with one
        // marker of our own (keyword none, entry points 0xFFFFFFFF, as WorkbenchArmorA's), named "Field kit".
        static Furniture Kit(Fallout4Mod mod, string editorId, string model, ObjectBounds bounds, P3Float marker, params FormKey[] keywords)
        {
            var f = mod.Furniture.AddNew(editorId);
            f.Name = "Field kit";
            f.ObjectBounds = bounds;
            f.Model = new Model { File = model };
            f.Keywords = new(keywords.Select(k => (IFormLinkGetter<IKeywordGetter>)new FormLink<IKeywordGetter>(k)));
            f.Flags = Furniture.Flag.HasModel;
            f.BenchType = Furniture.BenchTypes.Armor;
            f.WBDTDataTypeState = Furniture.WBDTDataType.Break0;
            f.MarkerParameters = new()
            {
                new FurnitureMarkerParameters
                {
                    Enabled = true,
                    Offset = marker,
                    RotationZ = 0,
                    Keyword = new FormLink<IKeywordGetter>(FormKey.Null),
                    EntryTypes = (Furniture.EntryParameterType)0xFF,
                    Unknown = new byte[] { 0xFF, 0xFF, 0xFF },
                },
            };
            return f;
        }

        static FormList List(Fallout4Mod mod, string editorId, IEnumerable<FormKey> items)
        {
            var list = mod.FormLists.AddNew(editorId);
            foreach (var i in items)
                list.Items.Add(new FormLink<IFallout4MajorRecordGetter>(i));
            return list;
        }

        // A condition on the subject (the player): <function>(<parameter>) == value.
        static ConditionFloat Is(Condition.Function function, FormKey parameter, float value) => new()
        {
            Data = new FunctionConditionData
            {
                Function = function,
                RunOnType = Condition.RunOnType.Subject,
                ParameterOneRecord = new FormLink<IFallout4MajorRecordGetter>(parameter),
            },
            CompareOperator = CompareOperator.EqualTo,
            ComparisonValue = value,
        };

        // look_ids.txt: every record at 0x8AF and from 0x8BA on, "EditorID ID" by ID. `--look-ids <file>` writes it and
        // refuses to change or drop a line already there (save-stable IDs: a later build only appends); check_plugin.py
        // fails when the plugin doesn't match the committed file.
        public static string[] IdLines(IModGetter mod) => mod.EnumerateMajorRecords()
            .Where(r => r.FormKey.ID == LookCodeId || r.FormKey.ID >= FirstId)
            .OrderBy(r => r.FormKey.ID).Select(r => $"{r.EditorID} {r.FormKey.ID:X6}").ToArray();

        public static void WriteIds(IModGetter mod, string path)
        {
            var lines = IdLines(mod);
            var kept = File.Exists(path) ? File.ReadAllLines(path).Where(l => l.Length > 0 && !l.StartsWith('#')).ToArray() : Array.Empty<string>();
            var changed = kept.Except(lines).ToArray();
            if (changed.Length > 0)
                throw new InvalidOperationException($"{path}: {changed.Length} line(s) would change or go (a later build only appends), the first: {changed[0]}");
            File.WriteAllText(path,
                "# CommonwealthMotorbike.esp's IDs from the customisation build on (2026-11-07a): CMB_LookCode at 0x8AF and every\n" +
                "# record from 0x8BA, \"EditorID ID\". Save-stable: a later build only appends. Written by the generator's --look-ids;\n" +
                "# check_plugin.py fails if the plugin doesn't match it.\n" +
                string.Join("\n", lines) + "\n");
            Console.WriteLine($"Wrote {path}: {lines.Length} IDs ({lines.Length - kept.Length} new)");
        }

        // The dump's lines for the look's record types (check_plugin.py reads them).
        public static void DumpLines(IMajorRecordGetter rec)
        {
            static string L<T>(IEnumerable<IFormLinkGetter<T>>? links) where T : class, IMajorRecordGetter =>
                "[" + string.Join(",", (links ?? Enumerable.Empty<IFormLinkGetter<T>>()).Select(l => l.FormKey)) + "]";
            static string F(float v) => v.ToString(System.Globalization.CultureInfo.InvariantCulture);
            switch (rec)
            {
                case IKeywordGetter k:
                    Console.WriteLine($"      keyword type {k.Type?.ToString() ?? "none"} name {k.Name?.String ?? "none"}");
                    break;
                case IArmorModificationGetter m:
                    var props = m.Properties.Select(p => p is IObjectModFormLinkIntPropertyGetter<Armor.Property> fl
                        ? $"{fl.Property}:{fl.FunctionType}:{fl.Record.FormKey}:{fl.Value}" : p.GetType().Name);
                    Console.WriteLine($"      omod ap {m.AttachPoint.FormKey} targets {L(m.TargetOmodKeywords)} loose {(m.LooseMod.IsNull ? "none" : m.LooseMod.FormKey.ToString())} " +
                                      $"properties [{string.Join(",", props)}] name {m.Name?.String ?? "none"}");
                    break;
                case IConstructibleObjectGetter c:
                    Console.WriteLine($"      cobj creates {c.CreatedObject.FormKey} bench {(c.WorkbenchKeyword.IsNull ? "none" : c.WorkbenchKeyword.FormKey.ToString())} " +
                                      $"counts [{string.Join(",", (c.CreatedObjectCounts ?? Enumerable.Empty<IConstructibleCreatedObjectCountGetter>()).Select(x => $"{x.Count}/{x.Priority}"))}]");
                    foreach (var x in c.Components ?? Enumerable.Empty<IConstructibleObjectComponentGetter>())
                        Console.WriteLine($"      component {x.Component.FormKey} {x.Count}");
                    foreach (var cond in c.Conditions)
                        Console.WriteLine($"      condition {Cond(cond)}");
                    break;
                case IMaterialSwapGetter w:
                    foreach (var x in w.Substitutions)
                        Console.WriteLine($"      entry {x.OriginalMaterial} -> {x.ReplacementMaterial} cnam {(x.ColorRemappingIndex is float v ? F(v) : "none")}");
                    break;
                case IFurnitureGetter f:
                    var markers = f.MarkerParameters ?? Array.Empty<IFurnitureMarkerParametersGetter>();
                    uint mnam = (uint)(f.Flags ?? default);
                    for (int i = 0; i < markers.Count; i++)
                        if (markers[i].Enabled) mnam |= 1u << i;
                    Console.WriteLine($"      furn bench {(int)f.BenchType} wbdt {(f.WBDTDataTypeState.HasFlag(Furniture.WBDTDataType.Break0) ? 1 : 2)} " +
                                      $"mnam {mnam:X8} markers {markers.Count} vmad {(f.VirtualMachineAdapter == null ? "none" : "yes")} keywords {L(f.Keywords)} model {f.Model?.File}");
                    for (int i = 0; i < markers.Count; i++)
                    {
                        var p = markers[i];
                        var unknown = p.Unknown.ToArray();
                        uint entry = (uint)p.EntryTypes | (unknown.Length == 3 ? (uint)unknown[0] << 8 | (uint)unknown[1] << 16 | (uint)unknown[2] << 24 : 0);
                        Console.WriteLine($"      marker {i} enabled {p.Enabled} offset {F(p.Offset.X)},{F(p.Offset.Y)},{F(p.Offset.Z)} rot {F(p.RotationZ)} " +
                                          $"keyword {(p.Keyword.IsNull ? "none" : p.Keyword.FormKey.ToString())} entry {entry:X8}");
                    }
                    break;
                case IMovableStaticGetter ms:
                    Console.WriteLine($"      model {ms.Model?.File} name {ms.Name?.String ?? "none"}");
                    break;
                case IMiscItemGetter misc:
                    Console.WriteLine($"      misc model {misc.Model?.File} preview {misc.PreviewTransform.FormKey} keywords {L(misc.Keywords)} " +
                                      $"value {misc.Value} weight {F(misc.Weight)} name {misc.Name?.String ?? "none"}");
                    break;
                case ITransformGetter t:
                    Console.WriteLine($"      transform position {F(t.Position.X)},{F(t.Position.Y)},{F(t.Position.Z)} rotation {F(t.Rotation.X)},{F(t.Rotation.Y)},{F(t.Rotation.Z)} " +
                                      $"scale {F(t.Scale)} zoom {F(t.ZoomMin)}-{F(t.ZoomMax)}");
                    break;
                case IArmorGetter a:
                    Console.WriteLine($"      armor playable {!a.MajorFlags.HasFlag(Armor.MajorFlag.NonPlayable)} keywords {L(a.Keywords)} aps {L(a.AttachParentSlots)} " +
                                      $"model {a.WorldModel?.Male?.Model?.File?.ToString() ?? "none"} preview {(a.PreviewTransform.IsNull ? "none" : a.PreviewTransform.FormKey.ToString())} " +
                                      $"armatures [{string.Join(",", a.Armatures.Select(x => x.ArmorAddon.FormKey))}] slot {a.BipedBodyTemplate?.FirstPersonFlags} name {a.Name?.String ?? "none"}");
                    foreach (var t in a.ObjectTemplates ?? Enumerable.Empty<IObjectTemplateGetter<Armor.Property>>())
                        Console.WriteLine($"      template default {t.Default} addon {t.AddonIndex} includes [{string.Join(",", t.Includes.Select(i => $"{i.Mod.FormKey}@{i.AttachPointIndex}"))}]");
                    break;
                case IArmorAddonGetter aa:
                    Console.WriteLine($"      addon slot {aa.BodyTemplate?.FirstPersonFlags} race {aa.Race.FormKey} model {aa.WorldModel?.Male?.File}|{aa.WorldModel?.Female?.File}");
                    break;
                case IMessageGetter msg:
                    for (int i = 0; i < msg.MenuButtons.Count; i++)
                    {
                        Console.WriteLine($"      button {i} conditions {msg.MenuButtons[i].Conditions.Count} text {msg.MenuButtons[i].Text?.String}");
                        foreach (var cond in msg.MenuButtons[i].Conditions)
                            Console.WriteLine($"      condition {Cond(cond)}");
                    }
                    break;
            }
        }

        static string Cond(IConditionGetter c) => c.Data is IFunctionConditionDataGetter d
            ? $"{d.Function} {d.ParameterOneRecord.FormKey} {c.CompareOperator} " +
              $"{(c is IConditionFloatGetter f ? f.ComparisonValue.ToString(System.Globalization.CultureInfo.InvariantCulture) : "global")} runon {d.RunOnType}"
            : c.Data.GetType().Name;
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

    // Array properties (2026-11-07a: the controller's look tables).
    static ScriptIntListProperty IntList(string name, IEnumerable<int> values) => new()
    {
        Name = name,
        Flags = ScriptProperty.Flag.Edited,
        Data = new ExtendedList<int>(values),
    };

    static ScriptStringListProperty StringList(string name, IEnumerable<string> values) => new()
    {
        Name = name,
        Flags = ScriptProperty.Flag.Edited,
        Data = new ExtendedList<string>(values),
    };

    // 2026-11-09a (test 51): CMB_LookF4SE's RimFinishV.
    static ScriptFloatListProperty FloatList(string name, IEnumerable<float> values) => new()
    {
        Name = name,
        Flags = ScriptProperty.Flag.Edited,
        Data = new ExtendedList<float>(values),
    };

    // The output model is set once CMB_SOMMonoEngine exists (OutputModel: made after every other record).
    static SoundDescriptor EngineSound(Fallout4Mod mod, string editorId, string file, bool loop)
    {
        var sound = mod.SoundDescriptors.AddNew(editorId);
        sound.Category.SetTo(Vanilla.AudioCategorySFX);
        sound.SoundFiles.Add($@"FX\CMB\{file}");     // relative to Data\Sound
        sound.Data = new SoundDescriptorStandardData { Priority = 128 };
        sound.LoopAndRumble = new SoundLoopAndRumble
        {
            Loop = loop ? SoundDescriptor.LoopType.Loop : SoundDescriptor.LoopType.None,
        };
        return sound;
    }

    // The engine's output model, since test 45's answer. Until then the engine played through the vanilla
    // SOMMono02000 (0x7E5DC): full level within 150 units, then a curve of 50/20/5/0 % out to 2000. The riding
    // camera sits about 450 out (fVanityModeMaxDist), and the listener is most likely the camera, so the engine
    // lost a few dB to distance alone. This is that model with its fade-out distances moved: full level out to
    // 600 (past the camera; Bethesda's SOMMono01500Player3rd, which 101 of the player's own 3rd-person sounds use,
    // is full out to 500), the same curve from there to 4000. Since test 47 everything else is SOMMono02000's own,
    // as the 27b build check read it from the tester's Fallout4.esm: flags Attenuates With Distance, Uses HRTF, the
    // reverb send 5 % (25 of the 26 plain SOMMonoNNNNN use 5, their _verb twins 40, the highest in Fallout4.esm 70;
    // 27b's 100 made the engine far wetter than any world sound wherever the area has reverb), a static attenuation
    // (VNAM) of 0, no output values (ONAM: none of the 220 vanilla Uses HRTF models has one), the fade-in curve
    // 0/50/80/95 (unused with a 0-0 fade-in, as written by 207 vanilla models), no effect chain. No INI can switch
    // this off: the generator's output model is the only way back (test 46's: reverb 100, no VNAM, the three ONAM
    // rows 100,100 / 100,0 / 0,100, the fade-in curve 100/100/100/100; or the descriptors on Vanilla.SOMMono02000).
    public const string EngineModelId = "CMB_SOMMonoEngine";
    public const float EngineModelFullTo = 600, EngineModelSilentAt = 4000;
    static readonly byte[] EngineModelCurve = { 50, 20, 5, 0 };
    static readonly byte[] EngineModelFadeIn = { 0, 50, 80, 95 };   // SOMMono02000's
    const byte EngineModelReverbSend = 5;                            // SOMMono02000's (test 46: 100)
    // The bike effects' output model (2026-11-02a): the engine's fields exactly, a record of its own so the engine's
    // stays the engine's and the effects' reach can move alone later.
    public const string FxModelId = "CMB_SOMMonoFx";

    // An output model with the engine's fields (EngineModelId, and since 2026-11-02a FxModelId).
    static SoundOutputModel OutputModel(Fallout4Mod mod, string editorId)
    {
        var model = mod.SoundOutputModels.AddNew(editorId);
        model.Data = new SoundOutputData
        {
            Flags = SoundOutputModel.Flag.AttenuatesWithDistance,
            // The field is xEdit's "Reverb Send %", a byte of 0-100; Mutagen reads a byte as a fraction of 255.
            ReverbSendPercent = new Percent(EngineModelReverbSend / 255.0),
        };
        model.Type = SoundOutputModel.TypeEnum.UsesHrtf;
        model.StaticAttenuation = 0;   // VNAM, present (all 311 vanilla models have it, 258 of them 0); no ONAM (OutputChannels left out)
        model.DynamicAttentuation = new DynamicAttentuationValues
        {
            FadeInDistanceStart = 0,
            FadeInDistanceEnd = 0,
            FadeOutDistanceStart = EngineModelFullTo,
            FadeOutDistanceEnd = EngineModelSilentAt,
            FadeInCurveValue1 = EngineModelFadeIn[0], FadeInCurveValue2 = EngineModelFadeIn[1],
            FadeInCurveValue3 = EngineModelFadeIn[2], FadeInCurveValue4 = EngineModelFadeIn[3],
            FadeOutCurveValue1 = EngineModelCurve[0], FadeOutCurveValue2 = EngineModelCurve[1],
            FadeOutCurveValue3 = EngineModelCurve[2], FadeOutCurveValue4 = EngineModelCurve[3],
        };
        return model;
    }

    // A bike effect of our own over the game's files (2026-11-02a, FxOwn): the game's record's fields but four (our
    // category AudioCategorySFX, our output model, set by the caller, static attenuation 0, no alternate).
    static SoundDescriptor FxSound(Fallout4Mod mod, FxOwn.Sound r)
    {
        var sound = mod.SoundDescriptors.AddNew(r.Id);
        sound.Category.SetTo(Vanilla.AudioCategorySFX);
        foreach (var f in r.Files)
            sound.SoundFiles.Add(f);                 // verbatim, as the game's own record stores it
        sound.Data = new SoundDescriptorStandardData
        {
            PercentFrequencyShift = r.Shift,
            PercentFrequencyVariance = r.Variance,
            Priority = 128,
            Variance = r.DbVariance,
            StaticAttenuation = 0,
        };
        sound.LoopAndRumble = new SoundLoopAndRumble
        {
            Loop = r.Loop ? SoundDescriptor.LoopType.Loop : SoundDescriptor.LoopType.None,
        };
        return sound;
    }

    // The output models and the sounds' links to them, read back from the written file and compared with the
    // records built, field for field (since test 45's answer, when the engine got its own model).
    static void CheckSoundsReadBack(Fallout4Mod built, string path)
    {
        using var back = Fallout4Mod.CreateFromBinaryOverlay(path, Fallout4Release.Fallout4);
        foreach (var m in built.SoundOutputModels)
        {
            var r = back.SoundOutputModels.FirstOrDefault(x => x.FormKey == m.FormKey);
            if (r == null || r.EditorID != m.EditorID || SopmLine(r) != SopmLine(m))
                throw new InvalidOperationException($"{m.EditorID} written as {SopmLine(m)}, read back as " +
                                                    (r == null ? "nothing" : $"{r.EditorID}: {SopmLine(r)}"));
        }
        foreach (var s in built.SoundDescriptors)
        {
            var r = back.SoundDescriptors.FirstOrDefault(x => x.FormKey == s.FormKey);
            if (r == null || r.OutputModel.FormKey != s.OutputModel.FormKey)
                throw new InvalidOperationException($"{s.EditorID}: written with the output model {s.OutputModel.FormKey}, read back with " +
                                                    (r == null ? "no record" : $"{r.OutputModel.FormKey}"));
        }
        Console.WriteLine($"read back: {built.SoundOutputModels.Count} output model(s) and {built.SoundDescriptors.Count} sounds as written");
    }

    // One line with every field of an output model: the dump prints it, check_plugin.py compares it with what
    // the generator writes, and Main compares the record read back with the one built.
    static string SopmLine(ISoundOutputModelGetter m)
    {
        static string Ch(ISoundOutputChannelGetter c) => $"{c.L},{c.R},{c.C},{c.LFE},{c.RL},{c.RR},{c.BL},{c.BR}";
        var a = m.DynamicAttentuation;
        var ch = m.OutputChannels;
        return $"flags {m.Data?.Flags} reverb {(m.Data == null ? "none" : $"{(int)Math.Round(m.Data.ReverbSendPercent.Value * 255)}")} " +
               $"type {m.Type?.ToString() ?? "none"} static {m.StaticAttenuation?.ToString() ?? "none"} " +
               (ch == null ? "channels none " : $"ch0 {Ch(ch.Channel0)} ch1 {Ch(ch.Channel1)} ch2 {Ch(ch.Channel2)} ") +
               (a == null ? "attenuation none " :
                   $"fade-in {a.FadeInDistanceStart}-{a.FadeInDistanceEnd} [{a.FadeInCurveValue1},{a.FadeInCurveValue2},{a.FadeInCurveValue3},{a.FadeInCurveValue4}] " +
                   $"fade-out {a.FadeOutDistanceStart}-{a.FadeOutDistanceEnd} [{a.FadeOutCurveValue1},{a.FadeOutCurveValue2},{a.FadeOutCurveValue3},{a.FadeOutCurveValue4}] ") +
               $"effect-chain {(m.EffectChain.IsNull ? "none" : m.EffectChain.FormKey.ToString())}";
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
            // The sounds' output model and the output models' fields (check_plugin.py reads both).
            if (rec is ISoundDescriptorGetter snd)
            {
                Console.WriteLine($"      output model {snd.OutputModel.FormKey} " +
                                  $"{types.GetValueOrDefault(snd.OutputModel.FormKey, Vanilla.Describe(snd.OutputModel.FormKey))}");
                // 2026-11-02a: the category, the static attenuation, the loop and the files (check_plugin.py reads them).
                var std = snd.Data as ISoundDescriptorStandardDataGetter;
                Console.WriteLine($"      sound category {(snd.Category.IsNull ? "none" : snd.Category.FormKey.ToString())} " +
                                  $"static {(std == null ? "none" : std.StaticAttenuation.ToString(System.Globalization.CultureInfo.InvariantCulture))} " +
                                  $"loop {snd.LoopAndRumble?.Loop.ToString() ?? "none"} files {snd.SoundFiles.Count}: {string.Join("; ", snd.SoundFiles)}");
            }
            if (rec is ISoundOutputModelGetter som)
                Console.WriteLine($"      sopm {SopmLine(som)}");
            if (rec is IRaceGetter race)
            {
                if (!race.SubgraphAdditiveRace.IsNull)
                    Console.WriteLine($"      additive to {race.SubgraphAdditiveRace.FormKey}");
                foreach (var sg in race.Subgraphs)
                    Console.WriteLine($"      subgraph {sg.Role} {sg.Perspective} [{string.Join(", ", sg.ActorKeywords.Select(k => k.FormKey))}] " +
                                      $"targets [{string.Join(", ", sg.TargetKeywords.Select(k => k.FormKey))}] " +
                                      $"{sg.BehaviorGraph} paths [{string.Join(", ", sg.AnimationPaths)}]");
            }
            // The perks' flags and entry points (2026-11-01a: CMB_RiderSteadyPerk reads "ModIncomingStagger Multiply 0 tabs 3";
            // 2026-11-02a: and EPFB, the entry's ID, empty when the record has none).
            if (rec is IPerkGetter perk)
            {
                Console.WriteLine($"      perk playable {perk.Playable} hidden {perk.Hidden} ranks {perk.NumRanks}");
                foreach (var e in perk.Effects)
                    Console.WriteLine(e is IPerkEntryPointModifyValueGetter v
                        ? $"      entry {v.EntryPoint} {v.Modification} {v.Value} tabs {v.PerkConditionTabCount} EPFB {v.PerkEntryID} conditions {v.Conditions.Count}"
                        : $"      effect {e.GetType().Name}");
            }
            // 2026-11-07a: the look's records (the object mods, recipes, swaps, the kit, the item, the menu's buttons).
            LookRecords.DumpLines(rec);
            // A global's value (2026-11-06a: check_plugin.py reads the round's nine).
            if (rec is IGlobalFloatGetter glob)
                Console.WriteLine($"      global value {glob.Data?.ToString(System.Globalization.CultureInfo.InvariantCulture) ?? "none"}");
            // The lists' entries (CMB_RamTooBig's races, CMB_FuelItems), one a line.
            if (rec is IFormListGetter list)
                foreach (var item in list.Items)
                    Console.WriteLine($"      item {item.FormKey} {types.GetValueOrDefault(item.FormKey, Vanilla.Describe(item.FormKey))}");
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
                // 2026-11-07a: the controller's look tables, the values without spaces.
                IScriptIntListPropertyGetter il => $"[{string.Join(",", il.Data)}] IntList",
                IScriptStringListPropertyGetter sl => $"[{string.Join(",", sl.Data)}] StringList",
                IScriptFloatListPropertyGetter fl => $"[{string.Join(",", fl.Data.Select(x => x.ToString(System.Globalization.CultureInfo.InvariantCulture)))}] FloatList",
                _ => p.GetType().Name,
            };
            Console.WriteLine($"{indent}  {p.Name} = {value}");
        }
    }
}
