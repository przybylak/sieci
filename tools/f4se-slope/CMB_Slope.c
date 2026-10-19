/*
 * CMB_Slope: Commonwealth Motorbike's F4SE plugin. While you ride it lets you climb
 * steeper slopes than on foot, moves the third-person camera farther back and tilts
 * the bike to match the ground.
 *
 * Fallout 4 1.11.240 with F4SE 0.7.9 only: the game addresses and structure offsets
 * below come from F4SE 0.7.9's own source for that runtime, and F4SE only loads the
 * plugin on the game versions listed in F4SEPlugin_Version.
 *
 * The controller script talks to it through globals of CommonwealthMotorbike.esp:
 * CMB_SlopeLive (the steepest slope in degrees while riding, 0 otherwise),
 * CMB_CameraLive (the camera distance while riding, 0 otherwise), CMB_TiltLive (the
 * most the bike may tilt, in degrees, while riding, 0 otherwise) and, the other way,
 * CMB_GroundNormalX/Y/Z (the ground under the player) and CMB_ParkX/Y/Z/Angle/UpX/UpY/UpZ
 * (where to park the bike), for parking.
 * F4SE calls the plugin every frame on the game's main thread (a permanent task):
 *
 *   Slope: how steep a slope a character can walk up is a limit kept by its character
 *   controller (bhkCharProxyController+0x418, the cosine of 47 degrees; found with this
 *   plugin's probe, tests 5 and 6); nothing in Papyrus reaches it. The plugin finds the
 *   player's controller and proxy by their C++ type information (RTTI), checking every
 *   pointer before reading it, and while riding writes the limit at the place given in
 *   CMB_Slope.ini (Target, SlopeOffset, SlopeUnit), only ever steeper than the game's
 *   own, and only if the value there is what's expected (ExpectedDegrees). Every frame
 *   while riding, in case the game sets it back; the original goes back afterwards. While a
 *   low face (a fallen trunk, a stump) is at the capsule with forward held, the limit goes to
 *   ClimbBoost for a moment, so the capsule climbs what its 47 deg would make a wall (test 40;
 *   ClimbRays); a sharp step no limit takes, the capsule still stuck at it, is stepped up onto
 *   (ClimbStepUp).
 *
 *   Camera: the game setting fVanityModeMaxDist:Camera (where the third-person camera
 *   sits, the farthest the mouse wheel zooms out) is raised to CMB_CameraLive while
 *   riding and put back afterwards. Papyrus can set INI settings but not read them, so
 *   this is here, where the player's own value can be read. The third-person zoom goes
 *   all the way out on getting on and back to the player's on getting off.
 *
 *   Ground: the controller keeps the normal of the ground the player stands on (its
 *   support normal, controller+0x1E0) and Havok's character state (on the ground,
 *   jumping, in the air, ...; controller+0x2C0, in the hknpCharacterContext whose state
 *   manager is at +0x2B8). The normal, averaged over the last 0.6 s on the ground, goes
 *   into CMB_GroundNormalX/Y/Z every IntervalMs (Z 0 off the ground). While riding, the
 *   plugin keeps a track of where the player's feet were on the ground, and writes a
 *   parking spot on it into the CMB_Park globals: the first place back along it that's
 *   a bike length and a half from the player in a straight line and no steeper than 45
 *   degrees, facing and pitched the way the track ran there: ground that was really
 *   ridden on, and not across a slope steeper than 20 degrees. CMB_TrackSlope gets how
 *   steep the ground here is (the track's own slope, and the face's from the averaged
 *   normal once the track says it's a slope), for refusing to get off on a face too steep
 *   to stand on.
 *
 *   Tilt: the worn bike is skinned to one bone of the rider (COM or AnimObjectA), so
 *   the animation moves it and its own node's transform does nothing. What the plugin
 *   turns instead is the skin's bind (BSSkin::BoneData, the mesh -> bone transform).
 *   The bike's shapes are found under the player's 3D root and through the biped (every
 *   equipped armor addon's 3D), by name, by the COM bike's bind, or as one of our own
 *   armor addons (the game renames the shapes); if a ride finds none for a second, what
 *   was there is logged. The bind: the mesh is turned about the seat before it goes onto
 *   the bone, so the bike pitches with the ground (the slope of the track just ridden,
 *   over about a wheelbase: the support normal is too noisy for it; smoothed and
 *   rate-limited, at most CMB_TiltLive degrees, roll at most MaxRoll, held in the air),
 *   keeps its seat and bars under the rider (who doesn't tilt) and still
 *   follows every move of the animation. The plugin
 *   holds a reference on the BoneData while it's changed and puts it back afterwards.
 *   Which way round the game stores its rotation matrices is read off the bike's own
 *   skin (whose bind we know) and the player's 3D (whose heading we know).
 *
 *   Steering: a bike can't turn on the spot. While riding, the player's heading may change
 *   at most speed / radius radians a second, or CMB_StandTurnRate degrees a second when
 *   that is faster; whatever the game turned beyond that in a frame is dropped. The radius
 *   grows with speed, from CMB_TurnRadiusSlow at walking pace to CMB_TurnRadius at riding
 *   speed (FullSpeed). The move keys are changed before the game uses them (its
 *   MovementHandler's event functions are wrapped: three vtable entries): a side key alone
 *   from a stop creeps round a small circle instead of riding off, and back gets
 *   the game nothing (it would drive forward) while the plugin backs the bike up, facing
 *   forward, through what the movement update gets from the controls (the movement turned
 *   round, or its speed made negative: whichever is found to move it), or else just stops it.
 *   Going back level or down, each step follows the ground's slope over BackFollow units under
 *   it, the controller supported or not (test 40: downhill the camera shook, the game's gravity
 *   carrying the bike down in hops once the controller said it was in the air).
 *
 *   Knocking enemies over (test 40's wish): an actor the rays see ahead is asked about through
 *   the CMB_Ram globals; for one CMB_RamScript says yes to, at CMB_RamMinSpeed or faster, the
 *   throttle stays open, the hit is told a moment before the front wheel reaches it (the script
 *   pushes it away) and the bike loses some speed (test 41); anything else is braked for as
 *   before. [Ram] Enabled=0 or the MCM's "Knock enemies over" off: never.
 *
 * With Probe=1 it also logs (Documents\My Games\Fallout4\F4SE\CMB_Slope.log) the
 * layout of the controller, the proxy and the objects listed in DumpPointers, then on
 * getting on, 1 and 3 seconds into the ride and on getting off, what changed: that's
 * how the slope limit's and the ground normal's places were found. The log of the session
 * before is kept as CMB_Slope_prev.log (test 40: the game restarted after the load that lost
 * the lean, and the log that would have said why was gone).
 *
 * Built with MinGW-w64 (tools/f4se-slope/build.sh). Plain C: F4SE's plugin interface
 * is plain structs and function pointers, and the one C++ object F4SE calls into (the
 * task) is a vtable laid out by hand. tools/f4se-slope/test runs it under Wine
 * against a stand-in for the game.
 */

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shlobj.h>
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PLUGIN_VERSION 3
#define RUNTIME_1_11_240 0x010B0F00u

/* --- Game addresses (RVAs) and layouts for runtime 1.11.240, from F4SE 0.7.9 --- */
#define RVA_PLAYER            0x032DD370u   /* GameReferences.cpp: g_player */
#define RVA_DATA_HANDLER      0x030E7100u   /* GameData.cpp: g_dataHandler */
#define RVA_LOOKUP_FORM       0x00311B80u   /* GameForms.cpp: LookupFormByID */
#define RVA_INI_SETTINGS      0x0344B4B8u   /* GameSettings.cpp: g_iniSettings */
#define RVA_INI_PREF_SETTINGS 0x0339FAE0u   /* GameSettings.cpp: g_iniPrefSettings */
#define RVA_PLAYER_CAMERA     0x030E6E58u   /* GameCamera.cpp: g_playerCamera */
#define RVA_PLAYER_CONTROLS   0x031F0B80u   /* GameInput.cpp: g_playerControls */
#define RVA_MOVE_HANDLER_VTBL 0x02571B38u   /* MovementHandler's vtable (read off Fallout4.exe 1.11.240, test 13) */
#define RVA_CONTROLS_IMOVE_VTBL 0x02571AA0u /* PlayerControls' IMovementPlayerControls vtable (the same) */
#define OFF_ACTOR_PROCESS     0x300         /* Actor::middleProcess (AIProcess *) */
#define OFF_PROCESS_DATA      0x08          /* AIProcess::unk08 (process data) */
#define OFF_DH_LOADED_MODS    (0xFB0 + 0x10) /* DataHandler::modList.loadedMods */
#define OFF_DH_LIGHT_MODS     (0xFB0 + 0x28) /* DataHandler::modList.lightMods */
#define OFF_ARRAY_ENTRIES     0x00          /* tArray::entries */
#define OFF_ARRAY_CAPACITY    0x08          /* tArray::capacity (UInt32) */
#define OFF_ARRAY_COUNT       0x10          /* tArray::count */
#define OFF_MOD_NAME          0x70          /* ModInfo::name[MAX_PATH] */
#define OFF_MOD_INDEX         0x370         /* ModInfo::modIndex (UInt8) */
#define OFF_MOD_LIGHT_INDEX   0x372         /* ModInfo::lightIndex (UInt16) */
#define OFF_FORM_ID           0x14          /* TESForm::formID */
#define OFF_FORM_TYPE         0x1A          /* TESForm::formType */
#define FORM_TYPE_GLOB        11
#define FORM_TYPE_REFR        0x40          /* TESObjectREFR */
#define OFF_GLOBAL_EDITOR_ID  0x20          /* TESGlobal::editorID */
#define OFF_GLOBAL_VALUE      0x30          /* TESGlobal::value */
#define OFF_SETTINGS_LIST     0x120         /* SettingCollectionList::data (Node *) */
#define OFF_SETTING_DATA      0x08          /* Setting::data */
#define OFF_SETTING_NAME      0x10          /* Setting::name */
#define OFF_REFR_HEADING      0xC8          /* TESObjectREFR::rot.z (radians) */
#define OFF_REFR_LOADED       0xF0          /* TESObjectREFR::unkF0 (LoadedData *) */
#define OFF_LOADED_ROOT       0x08          /* LoadedData::rootNode (third-person 3D) */
#define OFF_REFCOUNT          0x08          /* NiRefObject::m_uiRefCount */
#define OFF_OBJECT_NAME       0x10          /* NiObjectNET::m_name (StringCache::Entry *) */
#define OFF_STRING_STATE      0x08          /* StringCache::Entry::state */
#define OFF_STRING_EXTERN     0x10          /* StringCache::Entry::externData */
#define OFF_STRING_DATA       0x18          /* StringCache::Entry::data */
#define STRING_EXTERNAL       0x4000u
#define STRING_WIDE           0x8000u
#define OFF_WORLD_ROT         0x70          /* NiAVObject::m_worldTransform.rot (3 rows of 4 floats) */
#define OFF_WORLD_BOUND       0xB0          /* NiAVObject::m_worldBound (centre, radius) */
#define OFF_CHILDREN          0x128         /* NiNode::m_children.m_data */
#define OFF_CHILDREN_CAP      0x130         /* NiNode::m_children.m_arrayBufLen (UInt16) */
#define OFF_CHILDREN_USED     0x132         /* NiNode::m_children.m_emptyRunStart (UInt16) */
#define OFF_SKIN_INSTANCE     0x140         /* BSGeometry::skinInstance */
#define OFF_SKIN_BONE_DATA    0x40          /* BSSkin::Instance::boneData */
#define OFF_BONE_TRANSFORMS   0x10          /* BSSkin::BoneData::transforms (tArray) */
#define BONE_SIZE             0x50          /* BoneTransforms: sphere centre, radius, NiTransform */
#define OFF_BONE_RADIUS       0x0C
#define OFF_BONE_ROT          0x10          /* NiTransform::rot: 3 rows of 4 floats */
#define OFF_BONE_POS          0x40          /* NiTransform::pos */
#define OFF_PARENT            0x28          /* NiAVObject::m_parent */
#define OFF_LOCAL_ROT         0x30          /* NiAVObject::m_localTransform: rot (3 rows of 4), pos +0x30, scale +0x3C */
#define OFF_WORLD_POS         0xA0          /* NiAVObject::m_worldTransform.pos (its rot is OFF_WORLD_ROT) */
#define OFF_WORLD_SCALE       0xAC
#define OFF_SKIN_BONES        0x28          /* BSSkin::Instance::bones (tArray<NiAVObject *>), one per bone entry */
#define OFF_REFR_POS          0xD0          /* TESObjectREFR::pos */
#define OFF_ACTOR_BIPED       0x428         /* Actor::biped (BSTSmartPointer<BipedAnim>) */
#define OFF_BIPED_ROOT        0x08          /* BipedAnim::root */
#define OFF_BIPED_OBJECTS     0x10          /* BipedAnim::object[44] */
#define BIPED_OBJECT_SIZE     0x58          /* BIPOBJECT */
#define BIPED_SLOTS           44
#define OFF_BIPOBJ_ADDON      0x18          /* BIPOBJECT::armorAddon */
#define OFF_BIPOBJ_CLONE      0x30          /* BIPOBJECT::partClone */
#define BIKE_SLOT_INDEX       27            /* biped slot 57 (slots start at 30) */
#define OFF_CAMERA_STATE      0x28          /* TESCamera::cameraState (the current one) */
#define OFF_CAMERA_STATES     0xE0          /* PlayerCamera::cameraStates[] */
#define CAMERA_THIRD_PERSON1  7             /* kCameraState_ThirdPerson1, ThirdPerson2 */

/* --- Our side --- */
#define ESP_NAME              "CommonwealthMotorbike.esp"
#define SLOPE_GLOBAL_ID       0x82Au        /* CMB_SlopeLive, set by CMB_ControllerScript */
#define SLOPE_GLOBAL_EDITOR_ID "CMB_SlopeLive"
#define CAMERA_GLOBAL_ID      0x82Bu        /* CMB_CameraLive, likewise */
#define CAMERA_GLOBAL_EDITOR_ID "CMB_CameraLive"
#define CAMERA_SETTING        "fVanityModeMaxDist:Camera"
#define TILT_GLOBAL_ID        0x82Cu        /* CMB_TiltLive, set by CMB_ControllerScript */
#define TILT_GLOBAL_EDITOR_ID "CMB_TiltLive"
#define GROUND_GLOBAL_ID      0x82Du        /* CMB_GroundNormalX, Y, Z: 82D, 82E, 82F (we write these) */
#define PARK_GLOBAL_ID        0x831u        /* CMB_ParkX, Y, Z, Angle, UpX, UpY, UpZ: 831-837 (we write these) */
#define SLOPE_TRACK_GLOBAL_ID 0x838u        /* CMB_TrackSlope (we write it) */
#define TURN_RADIUS_GLOBAL_ID 0x839u        /* CMB_TurnRadius (MCM): the tightest turn while riding, 0 = off */
#define TURN_STAND_GLOBAL_ID  0x83Au        /* CMB_StandTurnRate (MCM): degrees a second when stopped */
#define TURN_SLOW_GLOBAL_ID   0x83Bu        /* CMB_TurnRadiusSlow (MCM): the tightest turn at walking pace */
#define HEADLAMP_GLOBAL_ID    0x83Du        /* CMB_HeadlampLive (CMB_ControllerScript): 1 while the headlamp should be lit */
#define HEADLAMP_REF_HI_ID    0x843u        /* CMB_HeadlampRefHi: the light reference the script placed, its form id's high 16 bits */
#define HEADLAMP_REF_LO_ID    0x844u        /* CMB_HeadlampRefLo: the low 16 bits (both 0: none) */
#define RAM_GLOBAL_ID         0x845u        /* CMB_RamSeenHi, SeenLo, Seen, Ok, HitSpeed, Hit, Enemies, MinSpeed: 845-84C (knocking enemies over, CMB_RamScript) */
#define RAM_GLOBALS           8
#define OFF_AV_USER_DATA      0x110         /* NiAVObject::userData: the reference whose 3D this is (CommonLibF4; F4SE 0.7.9's unk110) */
#define FORM_TYPE_ACHR        0x41          /* Actor */
#define FORM_TYPE_RACE        0x11          /* TESRace */
#define OFF_ACTOR_RACE        0x418         /* Actor::race (F4SE 0.7.9, CommonLibF4) */
#define OFF_RACE_FLAGS        0x1A0         /* TESRace::data (+0x180, F4SE's unk170 block and CommonLibF4's RACE_DATA) .flags (+0x20) */
#define OFF_RACE_SIZE         0x1AC         /* ... .raceSize (+0x2C): 0 small, 1 medium, 2 large, 3 extra large */
#define OFF_RACE_EDITOR_ID    0x3A0         /* TESRace::editorId (BSFixedString; both agree) */
#define RACE_PLAYABLE         0x1u
#define RACE_NO_KNOCKDOWNS    0x00400000u   /* RACE DATA flags (xEdit): 'No Knockdowns' */
#define RAM_MAX_ASK           8388607       /* the asks count 1 to 2^23 - 1, exact in a float, then from 1 again */
#define OFF_AV_FLAGS          0x108         /* NiAVObject::flags (bit 0: hidden, app culled); +0x100 is the collision object (test 30); [Lamp] FlagsOffset= overrides */
#define OFF_MOVE_INPUT        0x44          /* PlayerControls: moveInputVec x (strafe), y (forward +1, back -1) */
#define OFF_PREV_MOVE         0x5C          /* PlayerControls: prevMoveVec (what the movement used last) */
#define OFF_CONTROLS_IMOVE    0x30          /* PlayerControls' IMovementPlayerControls base (CommonLibF4) */
#define OFF_CONTROLS_HANDLERS 0x90          /* PlayerControls::handlers (BSTArray<PlayerInputHandler *>) */
#define OFF_CONTROLS_MOVEMENT 0x1E0         /* PlayerControls::movementHandler (CommonLibF4) */
#define OFF_HANDLER_DATA      0x10          /* PlayerInputHandler::data (PlayerControlsData &) */
#define VF_THUMBSTICK         4             /* BSInputEventUser::OnThumbstickEvent (F4SE, CommonLibF4) */
#define VF_BUTTON             8             /* BSInputEventUser::OnButtonEvent */
#define VF_PER_FRAME          9             /* PlayerInputHandler::PerFrameUpdate */
#define VF_CONTROLLER_OUTPUT  1             /* IMovementPlayerControls::GetControllerOutput */
#define OFF_CTRL_VELOCITY_MOD 0x180         /* bhkCharacterController::velocityMod (hkVector4f, CommonLibF4) */
#define OFF_CTRL_VELOCITY_TIME 0x308        /* bhkCharacterController::velocityTime */
#define VF_CTRL_GET_POSITION  0x33          /* bhkCharacterController::GetPositionImpl(hkVector4f &, bool) */
#define VF_CTRL_SET_POSITION  0x34          /* ::SetPositionImpl(const hkVector4f &, bool centre, bool warp) */
#define VF_CTRL_GET_VELOCITY  0x39          /* ::GetLinearVelocityImpl(hkVector4f &) */
#define VF_CTRL_SET_VELOCITY  0x3A          /* ::SetLinearVelocityImpl(const hkVector4f &) */
#define HAVOK_SCALE           0.0142875f    /* game units -> Havok's (bhkWorld's scale) */
#define OFF_CTRL_PUSH_DELTA   0x1B0         /* bhkCharacterController::pushDelta (hkVector4f, CommonLibF4) */
#define OFF_CTRL_FLAGS        0x300         /* bhkCharacterController::flags (CommonLibF4; logged while backing) */
#define OFF_CTRL_SUPPORT_COUNT 0x388        /* ::supportCount */
#define OFF_CTRL_FAKE_SUPPORT 0x43E         /* ::fakeSupport (bool) */
#define OFF_CTRL_IN_AIR_PRE_MOVE 0x442      /* ::inAirPreMove (bool) */
#define VF_CTRL_CHECK_SUPPORT 0x3E          /* ::CheckSupportImpl() */
#define OFF_REFR_CELL         0xB8          /* TESObjectREFR::parentCell (F4SE, CommonLibF4) */
#define ADDRESS_LIBRARY       "version-1-11-240-0.bin"   /* F4SE's Address Library for 1.11.240 */
#define ID_PICK_CTOR          2230668u      /* bhkPickData::bhkPickData (CommonLibF4's IDs) */
#define ID_PICK_SET_START_END 2236622u      /* bhkPickData::SetStartEnd(const NiPoint3 &, const NiPoint3 &) */
#define ID_PICK_RESET         2277761u      /* bhkPickData::Reset */
#define ID_PICK_HAS_HIT       2277770u      /* bhkPickData::HasHit */
#define ID_PICK_HIT_FRACTION  2277771u      /* bhkPickData::GetHitFraction */
#define ID_CELL_PICK          2200263u      /* TESObjectCELL::Pick(bhkPickData &) -> NiAVObject * */
#define PICK_DATA_SIZE        0xE0          /* sizeof(bhkPickData) */
#define OFF_PICK_FILTER       0x0C          /* bhkPickData: castQuery's collision filter info (0 after the ctor) */
#define OFF_PICK_HIT_LAYER    0xAC          /* bhkPickData: the hit's collision filter info (layer & 0x7F; test 16) */
#define LAYER_CHAR_CONTROLLER 30            /* COL_LAYER::kCharController: hit what the player's capsule would */
#define LAYER_BIPED           8             /* COL_LAYER::kBiped: an actor's body */
#define COLL_CHAR_CONTROLLER  0x0008877Fu   /* Fallout4.esm's COLL record for that layer: what the capsule collides with (test 36) */
#define OFF_COLL_INDEX        0x38          /* BGSCollisionLayer::collisionIdx: TESForm (0x20), TESDescription (0x18), then it (test 37: +0x30 read 874) */
#define OFF_COLL_COLLIDES     0x50          /* BGSCollisionLayer::collidesWith (BSTArray<BGSCollisionLayer *>), after debugColor, flags and the name */

/* RTTI names (MSVC mangled) of the objects we look for. */
#define RTTI_PLAYER     ".?AVPlayerCharacter@@"
#define RTTI_CONTROLLER ".?AVbhkCharacterController@@"
#define RTTI_PROXY      ".?AVhknpCharacterProxy@@"
#define RTTI_STATES     ".?AVhknpCharacterStateManager@@"
#define RTTI_NODE       ".?AVNiNode@@"
#define RTTI_GEOMETRY   ".?AVBSGeometry@@"
#define RTTI_SKIN       ".?AVInstance@BSSkin@@"
#define RTTI_BONE_DATA  ".?AVBoneData@BSSkin@@"
#define RTTI_AVOBJECT   ".?AVNiAVObject@@"
#define RTTI_ARMA       ".?AVTESObjectARMA@@"
#define RTTI_CAMERA     ".?AVPlayerCamera@@"
#define RTTI_THIRD      ".?AVThirdPersonState@@"
#define RTTI_CONTROLS   ".?AVPlayerControls@@"
#define RTTI_CELL       ".?AVTESObjectCELL@@"
#define RTTI_REFR       ".?AVTESObjectREFR@@"
#define RTTI_ACTOR      ".?AVActor@@"
#define RTTI_RACE       ".?AVTESRace@@"
#define RTTI_COLLISION_LAYER ".?AVBGSCollisionLayer@@"
#define RTTI_MOVE_HANDLER ".?AUMovementHandler@@"  /* a struct in the game, like all its input handlers (test 13) */
#define RTTI_MOVE_HANDLER_CLASS ".?AVMovementHandler@@"

/* ------------------------------------------------------------------------- */
/* F4SE plugin interface (f4se/PluginAPI.h, 0.7.9)                            */
/* ------------------------------------------------------------------------- */

typedef uint32_t PluginHandle;

typedef struct {
	uint32_t f4seVersion;
	uint32_t runtimeVersion;
	uint32_t editorVersion;
	uint32_t isEditor;
	void *(*QueryInterface)(uint32_t id);
	PluginHandle (*GetPluginHandle)(void);
	uint32_t (*GetReleaseIndex)(void);
	const void *(*GetPluginInfo)(const char *name);
	const char *(*GetSaveFolderName)(void);
} F4SEInterface;

enum { kInterface_Messaging = 1, kInterface_Task = 5 };

typedef struct {
	const char *sender;
	uint32_t type;
	uint32_t dataLen;
	void *data;
} F4SEMessage;

typedef void (*F4SEEventCallback)(F4SEMessage *msg);

typedef struct {
	uint32_t interfaceVersion;
	bool (*RegisterListener)(PluginHandle listener, const char *sender, F4SEEventCallback handler);
	bool (*Dispatch)(PluginHandle sender, uint32_t messageType, void *data, uint32_t dataLen, const char *receiver);
	void *(*GetEventDispatcher)(uint32_t dispatcherId);
} F4SEMessagingInterface;

enum {
	kMessage_PostLoadGame = 3,
	kMessage_NewGame = 8,
	kMessage_GameDataReady = 10,
};

typedef struct {
	uint32_t interfaceVersion;
	void (*AddTask)(void *task);
	void (*AddUITask)(void *task);
	void (*AddTaskPermanent)(void *task);
} F4SETaskInterface;

typedef struct {
	uint32_t dataVersion;
	uint32_t pluginVersion;
	char name[256];
	char author[256];
	uint32_t addressIndependence;
	uint32_t structureIndependence;
	uint32_t compatibleVersions[16];
	uint32_t seVersionRequired;
	uint32_t reservedNonBreaking;
	uint32_t reservedBreaking;
	uint8_t reserved[512];
} F4SEPluginVersionData;

/* Hardcoded addresses, game structures: only the runtime listed here. */
__declspec(dllexport) F4SEPluginVersionData F4SEPlugin_Version = {
	1,                      /* dataVersion */
	PLUGIN_VERSION,
	"CMB_Slope",
	"Commonwealth Motorbike",
	0,                      /* addressIndependence */
	0,                      /* structureIndependence */
	{ RUNTIME_1_11_240, 0 },
	0, 0, 0, { 0 }
};

/* ITaskDelegate as MSVC lays it out: a vtable of { scalar deleting destructor, Run }.
 * Permanent tasks are never deleted, but the destructor is there all the same. */
typedef struct Task { void **vtbl; } Task;

/* ------------------------------------------------------------------------- */
/* State                                                                     */
/* ------------------------------------------------------------------------- */

static HMODULE g_module;
static uintptr_t g_base, g_imageEnd;
static FILE *g_log;

/* Settings (CMB_Slope.ini) */
static int g_probe;
enum { TARGET_CONTROLLER, TARGET_PROXY };
static int g_target = TARGET_CONTROLLER;
static unsigned g_slopeOffset;          /* 0 = unknown: only read */
enum { UNIT_COSINE, UNIT_RADIANS, UNIT_DEGREES };
static int g_unit = UNIT_COSINE;
static float g_expectedDegrees;         /* 0 = any plausible value */
static DWORD g_interval = 100;          /* ms between full checks */
static int g_dumpPointers[8];           /* controller offsets whose objects get dumped too */
static int g_dumpPointerCount;
static char g_cameraSettingName[64] = CAMERA_SETTING;
static int g_zoomOut = 1;                 /* 1 = zoom all the way out on getting on */
static unsigned g_zoomTargetOffset = 0xE8, g_zoomCurrentOffset = 0xEC;   /* ThirdPersonState, 0..1 */
static unsigned g_normalOffset = 0x1E0;   /* controller: support normal (0 = no ground, no tilt) */
static unsigned g_stateOffset = 0x2C0;    /* controller: Havok character state (0 = don't read) */
static float g_smoothing = 0.25f;         /* seconds: how quickly the tilt follows the ground */
static float g_medianTime = 0.25f;        /* seconds of samples the median is taken over */
static float g_maxRate = 90.0f;           /* degrees per second at most */
static float g_maxRoll;                   /* degrees: a two-wheeler stays upright across a slope */
static float g_maxLean = 14.0f;             /* [Tilt] MaxLean: the lean into turns, at most (0: none) */
static float g_leanRate = 50.0f;            /* [Tilt] LeanRate: the lean changes at most this fast, degrees a second (test 32: 18 deg jumps between quarter seconds; test 34: 30 lagged the eased key turn) */
static float g_leanSmooth = 0.45f;          /* [Tilt] LeanSmooth: the turning rate is smoothed over this many seconds for the lean (a key asks 300 deg/s at once) */
static float g_leanDead = 0.08f;            /* [Tilt] LeanDead: v w / g (the tangent of the physical lean) under this gives none: a small correction barely leans */
static float g_leanGain = 0.5f;             /* [Tilt] LeanGain: the lean as this fraction of the physical atan(v w / g) */
static float g_leanNow, g_yawForLean;       /* the lean applied (rate-limited), and the turning rate smoothed for it */
static int g_headLevel = 1;                 /* [Tilt] HeadLevel: the head kept level as the bike rolls */
/* TorsoSolveFrom: how far into a ride (or a load's hold) the lean is first solved, seconds.
 * Test 39: at five of its six ride starts the first reading, 0.8 or 0.9 s in, caught the
 * getting-on still blending out, the grips at 100% with 15.9 to 21.1 deg, and the next, at 1.3
 * or 1.4 s, read the riding pose's 14.6 every time; a rider who rides off at once gives no
 * second reading of the riding pose (riding, the grips read 96 to 98%), so the blend's lean was
 * final 3 s in (review of test 40's second build). Half a second before test 40. */
static float g_torsoSolveFrom;
static float g_torsoLeanSetting = -1.0f;    /* [Tilt] TorsoLean: degrees the upper body leans forward (-1: enough to bring the grips to ArmReach of the arms' reach) */
static float g_armReach = 0.80f;            /* [Tilt] ArmReach: where the grips sit, as a fraction of the arms' reach, with the bars straight (test 38: 0.88 gave 6 to 9 deg of lean, about 1.4% of the reach a degree, and "character should lean forward a bit more"; 0.80 gives about 14) */
static float g_torsoTwist = 0.75f;          /* [Tilt] TorsoTwist: the upper body turns this fraction of the bars' angle toward the far grip (test 36: at 0.4 the inner arm folded tight at full lock, the elbow out and back; the inner grip comes back by the grip's radius and the inner shoulder should go back with it) */
static float g_torsoSideLean = 0.25f;       /* [Tilt] TorsoSideLean: and leans toward the inside of the turn by this many degrees per degree of the bars (test 36: the body didn't lean or shift sideways, so the inner arm had no room) */
static float g_torsoLean;                   /* this ride: degrees forward, from TorsoLean or solved for ArmReach */
static bool g_torsoLeanSet;
static int g_torsoTries;
static float g_faceLook = 0.3f;             /* [Steer] FaceLook: a face ahead is looked for this many seconds of the speed past the front wheel (0: off) */
static float g_turnEaseIn = 0.14f;          /* [Steer] TurnEaseIn: the turning rate the keys ask eases in over this many seconds (test 33: a snake on A/D; test 34: 0.35 felt heavy) */
static float g_turnEaseOut = 0.08f;         /* [Steer] TurnEaseOut: ... and out over this many seconds when the key is let go */
static float g_yawEased;                    /* the eased turning rate (radians a second) */
static float g_liftRate = 120.0f;           /* [Tilt] LiftRate: the whole lift (the wheels onto the ground, plus a bump) rises at most this many units a second (0: unlimited; test 35: +34 in a quarter second at 900 u/s jumped the bike) */
static float g_bumpMax = 30.0f;             /* [Tilt] BumpMax: a wheel's bump lift is never more than this in one go (a wheel radius; 1.5 radii while an obstacle is being ridden over) */
static float g_bumpSettle = 0.45f;          /* [Tilt] BumpSettle: and settles over this many seconds as the filtered values catch up or the bump passes */
static int g_suspension = 1;                /* [Tilt] Suspension: the wheels follow the ground within SuspTravel of the frame, the frame's lift on a spring and damper (test 36's wish) */
static float g_suspFrequency = 2.0f;        /* [Tilt] SuspFrequency: the spring's natural frequency, hertz */
static float g_suspDamping = 0.6f;          /* [Tilt] SuspDamping: its damping ratio (1: no rebound; test 37: 0.5 was "a tad too soft") */
static float g_suspTravel = 10.0f;          /* [Tilt] SuspTravel: units a wheel may rise into the frame at most (its drop is SuspDroop since test 38) */
static float g_liftVel;                     /* the lift spring's velocity (units a second) */
static float g_wheelOffset[2];              /* each wheel's move against the frame along the bike's up (front, rear): up into it over a bump, down into a hole */
static float g_wallAngle = 55.0f;           /* [Steer] WallAngle: a face this steep or steeper, solid at axle height and 1.5 radii, is a wall */
static float g_obstacleAngle = 50.0f;       /* [Steer] ObstacleAngle: a face this steep or steeper (or the climb limit, if that is higher) is an obstacle; under it, a slope the bike climbs (test 37) */
static float g_lowObstacleAngle = 60.0f;    /* [Steer] LowObstacleAngle: a lower-only obstacle (the axle ray hits, the one at 1.5 radii doesn't) holds the throttle only at this angle or steeper, never under the climb limit (test 38: five low rock faces of 50 to 57 deg held it) */
static float g_obstacleThrottle = 0.55f;    /* [Steer] ObstacleThrottle: an obstacle lower than 1.5 radii, or a face under WallAngle, holds the throttle to this share (0: stop; test 37: 0.4 crawled) */
static float g_obstacleHold = 1.0f;         /* [Steer] ObstacleHold: an obstacle verdict stays in force this many seconds after the rays last said obstacle */
static int g_wallFrames = 5;                /* [Steer] WallFrames: while an obstacle verdict is in force, a wall must be seen ahead of the wheel this many frames running before it counts */
static float g_faceObstacleAt = -100.0f;    /* when the face rays last said obstacle (the verdict in force for ObstacleHold after) */
static int g_wallSeen;                      /* frames running the face rays' raw verdict has been a wall with its hit ahead of the wheel */
static int g_faceKind;                      /* the face rays' last verdict: 0 nothing, 1 an obstacle, 2 a wall (a line is logged when it changes) */
static float g_faceNoneSince = -1.0f;       /* since when the rays have found nothing after a verdict (logged as gone after a quarter second: at the rays' reach a hit comes and goes by the frame) */
static float g_bumpLift, g_liftSmooth;      /* the bump lift now; the filtered lift the bump sits on */
static float g_wheelZ[2];                   /* this frame's raw ray hits under the wheels (front, rear), above the feet */
static bool g_wheelZOk;
static float g_torsoSolvedAt = -100.0f;     /* when the upper body's lean was last solved; solved again for the ride's first 3 s (the pose settles) */
static bool g_torsoFinal;
static float g_torsoRetryAt;                /* the solve not tried before this: the grips short of the riding pose's reach, tried again every half second (test 37) */
static float g_torsoWaitSince = -1.0f;      /* when the solve first found the grips short of the riding pose's reach this ride (-1: not yet) */
static bool g_torsoWaitLogged;              /* the "not solved yet" line, once a ride */
static bool g_torsoAsItComes;               /* 20 s of that: the solve taken as it comes, and not final: measured again every half second till the riding pose is there (test 38) */
static float g_torsoLastR0 = -1.0f;         /* the grips' reach as the clips posed it at the last solve (-1: none this ride): taken as it comes, solved again when it moves by over 3% */
static float g_torsoSeqAt;                  /* when this run of readings began (the ride's start, a jump, the riding pose come after "as it comes"): the best of them is kept, final 3 s on (test 39); moved on when the run's first reading came late */
static float g_torsoSeqFrom;                /* ... and when it really began, never moved: the seconds the final lines give (review of test 40's first build: a late first reading made "3.0 s since the jump" of 5.5) */
static float g_torsoBestR0 = -1.0f;         /* the grips' reach as the clips posed it for the solve kept in this run (-1: none yet) */
static bool g_torsoKept;                    /* this run began from the solve kept before a jump of the player, and no reading has beaten it yet (test 40) */
static const char *g_torsoSeqWhat = "the ride's start";   /* what began the run, for the final line */
static char g_torsoRearmWhy[96];            /* what has the lean solved again without being let go of meanwhile ("a jump of N units (a door, a fast travel)"; test 38), for the next lean line; empty: nothing */
static float g_armMoveNow;                  /* the arm chains' joints' biggest move since last frame, relative to the bike's bone (test 37: a Pip-Boy raise moved the arm bones 40.7 in a frame and the lean was solved from that pose) */
static bool g_armMoveOk;                    /* measured this frame (the joints had positions last frame too) */
static float g_armMoveLast[2][3][3];        /* each chain's shoulder, elbow and wrist last frame, relative to the bike's bone */
static uint8_t g_armMoveLastOk[2][3];
static float g_wristRoll = 1.0f;            /* [Tilt] WristRoll: the hand rolled round the grip's axis this share of the way to its long axis lying in line with the forearm, seen along the grip's axis (0: the hand keeps the clips' orientation, turned with the bars; test 37: 25 deg of wrist turn at the straight bars; test 39: "cat paw", the clips' hand bent down at the wrist kept) */
static float g_handPitch;                   /* [Tilt] HandPitch: the hand's long axis this many degrees above the forearm's line, seen along the grip (+ = the knuckles up, either hand; test 39) */
static float g_armPole[3] = { 1.1f, -0.3f, -0.9f };    /* [Tilt] ArmPole: the way the elbows bend, in the bike's space, the right arm's (the left mirrored in x); 0,0,0: each arm's own plane as the clips pose it (test 38: the elbows stood out at shoulder height; test 40, in the arm emulation: the forearm rose 14 to 18 deg to the grip at 0.35,-0.3,-1.0, and the tester wants it level) */
static float g_armPoleTurn[3] = { 0.35f, -0.3f, -1.0f };   /* [Tilt] ArmPoleTurn: the pole the inside arm (the one on the side the bars turn to) fades to as the bars turn (test 41: with the elbow out, the inside wrist turned 16 to 21 deg more with the bars 4 to 12 over); 0,0,0: no fade */
static float g_armPoleTurnBars = 10.0f;     /* [Tilt] ArmPoleTurnBars: the bars' degrees at which the inside arm has all of ArmPoleTurn (0 to 45; 0: no fade) */
static float g_wristMax[2] = { -1.0f, -1.0f };   /* each side's largest wrist turn from the clips' pose this ride (-1: no arm solved yet), with the bars, the reach and the roll at that moment, logged at the ride's end */
static float g_wristMaxBar[2], g_wristMaxReach[2], g_wristMaxRoll[2], g_wristMaxFade[2];
static bool g_armsRidingLogged;             /* the arms' riding line (test 41), once a hold like the arm lines */
static float g_armsFastSince = -1.0f;       /* since when the speed has been over 300 (-1: not now), for that line */
static float g_jumpAt = -100.0f;            /* when the last jump of the player re-armed the lean's solve (RearmTorsoSolve): the wrist's max leaves out the second after it (test 39) */
static float g_suspCompressRear = 4.0f;     /* [Tilt] SuspCompressRear: the rear wheel rises into the frame at most this much (its mudguard is on the frame; test 37: the tyre within 10 of it) */
static float g_suspDroop = 4.0f;            /* [Tilt] SuspDroop: a wheel drops below the frame at most this much, both wheels, and the frame sinks under the ground's contact by it at most (test 38: at -10 the sliders were off the stanchions) */
static float g_suspExtend = 0.1f;           /* [Tilt] SuspExtend: a wheel extends away from the frame over this many seconds (compression takes 0.03; test 38: "like there was no weight behind it") */
static float g_wheelWordAt = -100.0f;       /* when the wheel rays last had a word: without one the lift is held with the pitch for 3 s before it eases off (test 38: the station wagon) */
/* A hand of log lines: up to LOG_HAND_SIZE in hand, one more every LOG_HAND_EVERY seconds (10 a
 * minute at most, sustained), filled again on each ride (LogHandTake, LogHandFill). Test 39:
 * the wheel rays' 30 lines a ride were spent by 01:35:02, before the backing tests began. A
 * hand may have a size and a pace of its own (0: these); the face rays' is 20, one every 3 s. */
#define LOG_HAND_SIZE  10.0f
#define LOG_HAND_EVERY 6.0f
typedef struct { float lines, at, size, every; } LogHand;
static LogHand g_wheelHand[2] = { { LOG_HAND_SIZE, 0.0f, 0.0f, 0.0f }, { LOG_HAND_SIZE, 0.0f, 0.0f, 0.0f } };   /* the wheel rays' "rays:" lines (the hits under a steep pitch): [0] riding, [1] backing (INPUT_BACK), so the backing tests always get theirs; each line one a second at most besides (test 38: the roof and ledge cases) */
static LogHand g_wheelThrownHand[2] = { { LOG_HAND_SIZE, 0.0f, 0.0f, 0.0f }, { LOG_HAND_SIZE, 0.0f, 0.0f, 0.0f } };   /* the same for the hits thrown away */
static float g_wheelLoggedAt = -100.0f, g_wheelThrownAt = -100.0f;
static float g_rideStartClock;
static float g_jumpMax;                     /* the arm bones' biggest move between frames since the last trace line (test 33: stretched fingers) */
static char g_jumpName[96];
static float g_faceEase = 1.0f;             /* this frame: what a face ahead leaves of the throttle (1: nothing ahead) */
static float g_holdWaitSince;               /* when a hold first found an arm's chain half built and let go to wait for the skeleton (test 35); 0 = no wait on */
static bool g_holdWaitExpired;              /* the wait ran its second this ride: a skeleton that lacks a shoulder for good isn't waited for again at every re-hold (review) */
/* The face rays' lines (test 40: their 60 a ride were spent by 15:41:29.711, 2 at the ride's
 * start and 58 in two minutes off-road through a fast travel, and the next three stops had none):
 * from a hand of 20, one more every 3 s (LogHand). */
static LogHand g_faceHand = { 20.0f, 0.0f, 20.0f, 3.0f };
static float g_faceLoggedAt = -100.0f;
static float g_faceSince = -1.0f;           /* when the verdict in force began (its kind went from none to one), for the "nothing ahead now" line */
static float g_faceLastSlope;               /* the last verdict's angle, and what the axle-height ray hit then, and its layer */
static char g_faceLastWhat[64];
static uint32_t g_faceLastLayer;
/* Climbing low things (test 40, finding 8: off-road with forward held the bike stopped dead at
 * fallen trunks and stumps four times in three minutes, 900 to near 0 in half a second): the
 * player's capsule meets a trunk under the bike's middle, between the wheel rays, and the
 * controller's 47 deg limit makes its contact a wall. While a low face is at the capsule the
 * limit is raised to ClimbBoost for a moment (ClimbRays). The settings, [Steer]: */
static int g_climb = 1;                     /* Climb: 1 = on, 0 = never (as before test 41) */
static float g_climbBoost = 85.0f;          /* ClimbBoost: the limit while it's on, degrees (a round log 30 across meets the capsule at acos(3/33) = 84.8) */
static float g_climbTopSetting;             /* ClimbTop: nothing this high above the feet may be ahead (0: the wheel radius + 2, 31.9) */
static float g_climbMaxPitch = 22.0f;       /* ClimbMaxPitch: the wheels' line no steeper than this (test 40: the four stops read 5-20, the rock pile 31-37) */
static float g_climbHold = 0.3f;            /* ClimbHold: on for this long after the last frame a low face was seen */
static float g_climbMax = 1.5f;             /* ClimbMax: given up after this long stalled with it on */
static float g_climbThrottle = 0.4f;        /* ClimbThrottle: the Lead cap's floor while it's on (0.1 otherwise) */
static int g_climbStep = 1;                 /* ClimbStep: 1 = a sharp step the boost can't take is stepped up onto (stage 2, ClimbStepUp), 0 = never (stage 1 alone) */
/* ... and the state: */
static bool g_climbOn;                      /* on: the slot holds g_climbValue */
static float g_climbValue;                  /* ClimbBoost in the slot's unit, never less steep than the riding value (ApplySlope) */
static bool g_climbValueOk;                 /* g_climbValue worked out for the riding value, and steeper than it */
static float g_climbSince, g_climbSeenAt;   /* when it went on; the last frame a low face qualified */
static float g_climbStalled;                /* seconds on with the speed along under 40, running */
static float g_climbFeet0, g_climbFeetTop, g_climbSpeed0, g_climbPos0[2];   /* the feet's height and the speed when it went on, the feet's highest since, where it went on */
static bool g_climbCool;                    /* given up: no new boost until the bike has moved 60 along its heading or forward is pressed again */
static float g_climbCoolAt, g_climbCoolPos[2];
static float g_stallSince = -1.0f;          /* forward held, the throttle held to the measured speed (Lead) and the speed along under 80 since then (-1: not) */
static float g_stallSpeed;                  /* the speed along then: 15 more and it's a start from rest gaining speed, not a stall (the window starts again) */
static bool g_climbRideLogged;              /* the ride's capsule line */
static float g_capsuleRadius = 18.0f;       /* controller+0x370 in game units, read once a ride (10-30, else 18) */
static float g_capsuleHeight = 128.0f;      /* controller+0x374 in game units, read with it (60-250, else 128): the room a step up needs over the top */
static LogHand g_climbHand = { LOG_HAND_SIZE, 0.0f, 0.0f, 0.0f };   /* the climb lines: 10, one more every 6 s */
static float g_climbRefusedAt = -100.0f;    /* the last "stopped with forward held" line, and its reason (one a stall, again if the reason changes, a second apart at least) */
static int g_climbRefusedWhy = -1;
/* Stage 2's steps up (ClimbStepUp): */
static int g_stepCount;                     /* made at this obstacle: 2 at most, afresh once the bike is 60 from the last one's place, a ride's start or a load */
static int g_stepsThisBoost;                /* made while this boost was on, for its "over it" and "given up" lines */
static float g_stepAt = -100.0f, g_stepTriedAt = -100.0f;   /* the last step made, and the last look for one (a step's rays at most every 0.25 s) */
static float g_stepPos[2];                  /* where the last one was made */
static bool g_stepCheck;                    /* the last step's rise still to be seen: within 0.1 s the feet must have risen half of it */
static float g_stepZ0, g_stepWant, g_stepRose;   /* the feet's height before it, the rise asked for, the most risen since */
static bool g_stepRefusedSaid;              /* this boost's "no step" line said (one a boost) */
static void ClimbOff(const char *why);
static const char *ClimbWord(void);
struct ClimbLineS;
static bool ClimbStepUp(uintptr_t player, uintptr_t ctrl, uintptr_t cell, const struct ClimbLineS *L, const float pos[3], float sh, float ch, float top);   /* defined with the reverse's controller functions */
static void ClimbStepSeen(const float pos[3]);
static float g_headingNow;                  /* the player's heading this frame (FrameTilt), for the head's counter-roll */
static float g_wallAheadAt = -100.0f;       /* when the front ray last found a face ahead (the throttle is cut for a quarter second after) */
static int g_wallLogs;
static float g_wallLoggedAt = -100.0f;
static const char *g_rayWhat;               /* what the last ray hit (its 3D's name), for the log (CastRay) */
static uintptr_t g_rayObj;                  /* ... and that 3D (NiAVObject *; 0: none), for the actor behind it (rams) */
static uint32_t g_rayLayer;                 /* the last hit's collision layer */
static uintptr_t g_rayLetBy[3];             /* the 3D roots of actors the bike is to knock over (rams): the face rays and WallAhead pass through them, to see what is behind */
static int g_rayLetByCount;
static uintptr_t g_riderRoot;               /* the player's 3D root this frame: a hit on it or under it is the rider's own body, capsule or bike, passed through (test 36) */
static float g_pivotHeight = 74.0f;       /* the seat (the rider's hips) above the feet */
static int g_trace;                       /* 1 = log the tilt every 0.25 s while riding */
static int g_steer = 1;                   /* 1 = limit how fast the bike turns (CMB_TurnRadius) */
static float g_fullSpeed = 900.0f;        /* units a second at which the turning radius is CMB_TurnRadius */
static int g_reverse = 1;                 /* 1 = holding back backs the bike up instead of turning it round */
static int g_inputHook = 1;               /* 1 = change the move input before the game uses it (creep, reverse) */
static int g_ramOn = 1;                   /* [Ram] Enabled: hostile actors the bike hits at speed are knocked over (with CMB_RamScript) */
static float g_ramLook = 0.8f;            /* ActorLook: the actor ray looks this many seconds of the speed past the front wheel */
static float g_ramLead = 0.06f;           /* Lead: the hit is told this many seconds of the speed before the front wheel's edge reaches the actor */
static float g_ramPass = 1.0f;            /* Pass: for this long after the hit the rays let the actor's capsule by */
static int g_ramMaxSize = 1;              /* MaxSize: the largest race size knocked over (0 small, 1 medium, 2 large, 3 extra large) */
static int g_ramNoKnockdowns = 1;         /* NoKnockdowns: races flagged No Knockdowns are left to the brakes */
static float g_ramAskAgain = 0.4f;        /* AskAgain: no answer this long, asked again */
static float g_ramAskAgainNo = 1.0f;      /* AskAgainNo: after a no, asked again this long after the ask at the soonest */
static float g_ramHitKeep = 0.6f;         /* HitKeep: at a hit the throttle is held to this share of the speed ... */
static float g_ramHitHold = 0.4f;         /* HitHold: ... for this many seconds (test 41's answer: the bike should lose speed on a hit; 0 = not) */
static int g_creep = 1;                   /* 1 = a side key from a stop creeps forward round a CreepRadius circle */
static float g_creepStart = 0.1f;         /* the first forward input tried for the creep (then learnt) */
/* The throttle (test 21: the game's own speed is there at once and gone at once): forward
 * builds up over Accel seconds, rolls on after the key for Coast seconds, and back brakes
 * it off over Brake seconds before the reverse starts. */
static int g_throttleOn = 1;
static float g_accel = 3.0f, g_coast = 2.0f, g_brake = 0.4f;
static float g_throttle;                   /* 0..1, the speed as a fraction of the top: built up, rolled off, braked */
static float g_throttleMag = 1.0f;         /* the forward key's own size (a stick's), kept while coasting */
static bool g_throttleWrote;               /* this frame's input is the throttle's */
static double g_throttleAt;                /* when the throttle last moved (its own clock: the hooks don't run once a frame) */
static double g_forwardAt = -100.0, g_backAt = -100.0;   /* when the forward and back keys were last read */
static float g_lead = 0.2f;                /* how far (of the top) the throttle may run ahead of the measured speed */
static float g_backBelow = 30.0f;          /* back reverses only once the bike moves slower than this (units/s) */
static bool g_throttleCapped;
static float g_barAtSpeed = 0.6f;          /* the bars go over this much of BarAngle at speed (from 150 to 400 units/s) */
static float g_pivotForward = 12.0f;       /* the tilt's pivot this far ahead of the seat (towards the bars: the hands drift less) */
static float InputForSpeed(float speed);   /* defined with the input hook */
static double SecondsNow(void);            /* the same */
static float g_keys[2];                    /* the keys as read (defined with the input hook below) */
static bool g_inputActive;                 /* the input hook is live (defined with it below) */
static float g_creepBelow = 100.0f;       /* a side key alone creeps below this speed */
static float g_creepRadius = 55.0f;       /* the creep goes round this circle (test 15: a bit more than 40) */
static float g_backSpeed = 80.0f;         /* units a second the bike is pushed back */
enum { PUSH_DELTA, PUSH_RAYSTEP, PUSH_MOD, PUSH_VELOCITY, PUSH_POSITION, PUSH_BRAKE };
static int g_backPushFirst = PUSH_RAYSTEP;   /* BackPush: the method to start with */
static bool g_backPushAuto = true;        /* BackPush=auto: steps after rays, else brake */
static float g_backClearance = 150.0f;    /* this far behind the rider must be clear (test 16: the rear is about 130 back) */
static float g_backSink;                  /* BackSink: units the feet go below the hover when closing a gap (0: to the hover, BACK_HOVER over the ground) */
#define BACK_HOVER 0.5f                   /* closing a gap under the feet, they go this far over the ground (test 39: backing with no step the controller's own hover read 0.0 to 0.2, and every gap closed onto the ground with the controller supported was followed by it in the air and the player through the road) */
static float g_backFollow = 10.0f;        /* BackFollow: going back level or down, the step follows the ground's slope over this many units centred on the middle of the step, the controller supported or not (test 40's finding 6; 0: test 40's rule, the slope 55 back and the gap closed to the hover when unsupported) */
static float g_backClose = 0.1f;          /* BackClose: unsupported, a gap over the controller's own clearance is closed over this many seconds (at most 120 a second and 3 a step) */
static int g_backSupportCheck;            /* BackSupportCheck: call the controller's CheckSupportImpl after a step */
static char g_shapePrefix[64] = "CMB_BikeWorn";
enum { LAYOUT_UNKNOWN = -1, LAYOUT_FILE = 0, LAYOUT_TRANSPOSED = 1, LAYOUT_DISAGREE = 2 };
static int g_layoutSetting = LAYOUT_UNKNOWN;   /* Layout=auto */

static volatile bool g_dataReady;
static uintptr_t g_slopeGlobal, g_cameraGlobal;   /* TESGlobal * */
static uintptr_t g_tiltGlobal, g_groundGlobals[3], g_parkGlobals[7], g_trackSlopeGlobal;
static uintptr_t g_turnRadiusGlobal, g_turnStandGlobal, g_turnSlowGlobal;
static uintptr_t g_headlampGlobal, g_headlampRefGlobals[2];
static uintptr_t g_ramGlobals[8];   /* CMB_RamSeenHi, SeenLo, Seen (we write), Ok (the script), HitSpeed, Hit (we write), Enemies, MinSpeed (MCM) */
static uintptr_t g_lampRef;                 /* the light reference the script placed (CMB_HeadlampRefHi/Lo), looked up once per id */
static uint32_t g_lampRefId;
static uintptr_t g_lampRefOld;              /* the one before, kept lit at the lens until the new one's 3D is in (test 33: the beam flickered at every move) */
static uint32_t g_lampRefOldId;
static float g_lampRefOldSince;
static bool g_lampRefLogged, g_lampRefParked, g_lampRefHad3D, g_lampRefGoneLogged;
static float g_wheelHist[3];                /* the wheels' pitch over the last three frames: a median drops a one-frame hole */
static int g_wheelHistAt, g_wheelHistN;

/* The headlamp's light (test 29's wish): the game hangs the ADDN's light on an add-on node
 * (BSValueNode) in the worn bike's nif. The node is put at the lens every frame, with the
 * bars' turn and the tilt, while CMB_HeadlampLive is 1, and hidden (and sunk far below the
 * world) otherwise; its own transform and flags go back on letting go. Two nodes: the plain
 * light's and the shadow-casting light's ([Lamp] Shadows= picks one, the other stays hidden). */
typedef struct {
	uintptr_t node;
	uint8_t saved[0x40];
	uint64_t savedFlags;
	bool lit, placed;
} LampNode;
static LampNode g_lamp[2];
static int g_lampEnabled = 1, g_lampShadows, g_lampBeamAxis, g_lampBeamSign = 1, g_lampLogged;
static float g_lampPitch;
static float g_lampAhead = 28.0f;           /* [Lamp] Ahead: the light placed this far along the beam from the lens (test 34: inside the housing on fast frames, the beam blacked out) */
static float g_lampLead = 1.0f;             /* [Lamp] Lead: and moved on by this many frames of the bike's speed (the renderer lights with the transform a frame late) */
static int g_lampHandoverFrames = 5;        /* [Lamp] HandoverFrames: at a handover the old light stays at the lens this many frames after the new one has its 3D */
static int g_lampRefNewFrames;              /* frames the new reference has had its 3D during a handover */
static uint32_t g_lampFlagsOff = OFF_AV_FLAGS;
static char g_lampNodeName[2][48] = { "CMB_Headlamp", "CMB_HeadlampShadow" };
static float g_lampPoint[3], g_lampAxis[3] = { 0.0f, 1.0f, 0.0f };
static bool g_lampOk;
static uint32_t g_ourPrefix, g_ourMask;   /* our plugin's form IDs: (id & mask) == prefix */
static DWORD g_lastGlobalTry;
static bool g_globalsMissingLogged;

/* The chain to the proxy, as found last time (offsets, so it's re-read every check). */
static int g_ctrlWhere = -1;            /* 0 = process data, 1 = process, 2 = player */
static int g_ctrlOff = -1;
static int g_proxyOff1 = -1, g_proxyOff2 = -1;
static DWORD g_nextScan;                /* full searches are slow: not more often than this */
static bool g_ctrlMissingLogged, g_proxyMissingLogged;

/* Slope: what we changed. */
static bool g_applied;
static uintptr_t g_appliedTarget;
static float g_originalValue, g_writtenValue;
static int g_revertCount;
static bool g_badValueLogged;

/* Camera: what we changed. */
static uintptr_t g_cameraSetting;
static bool g_cameraApplied;
static float g_cameraOriginal, g_cameraWritten;
static bool g_zoomRiding, g_zoomTouched, g_zoomDumped;
static uintptr_t g_zoomState;
static float g_zoomOldTarget, g_zoomOldCurrent;
static DWORD g_zoomUntil;

/* Probe snapshots. */
#define SNAP_OBJECTS 10
typedef struct { char label[48]; uintptr_t obj; int size; uint8_t bytes[0x600]; } Snapshot;
static Snapshot g_snaps[SNAP_OBJECTS];
static int g_snapCount;
static bool g_dumpedThisLoad;
static bool g_wasRiding;
static DWORD g_mountTime;
static int g_ridingSnapsDone;

static DWORD g_lastTick;

/* Steering: the heading we last let the player have, how fast they're going. */
static bool g_steerHave;
static float g_steerHeading, g_steerPos[3], g_speed, g_speedAlong, g_steerRadius;
static float g_steerWanted, g_steerAllowed;   /* the biggest turn asked for / allowed since the last trace (deg/s) */
enum { INPUT_PASS, INPUT_BACK, INPUT_CREEP };
static int g_inputMode;                       /* INPUT_*: what the move keys are made into (input hook) */
static float g_creepInput = 0.1f;             /* the forward input that creeps at the wanted speed (learnt) */
static float g_creepGood = 0.1f;              /* the input last seen creeping at about the speed wanted */
static float g_speedAlongFast;                /* g_speedAlong with less smoothing (0.05 s), for catching a surge */
static float g_creepCutAt, g_creepCutSpeed;   /* the creep input may be cut again from then; the speed at the last cut */
static int g_steerClamped;                    /* frames clamped since the last trace */
static float g_controlsLast[20];
static float g_controlsLogged;

/* Ground under the player: this frame's reading, and an average over the last moments
 * on the ground (a single contact normal can be a curb's edge or a bump of rock). */
#define GROUND_AVERAGE_TIME 0.6f
static float g_frameDt;
static bool g_riding;
static bool g_groundOk, g_groundAir;
/* Backing up in steps (the reverse, further down): the rays' word on the ground under the feet. */
static bool g_rayGrounded;          /* this frame's rays put the feet on the ground (whatever the controller says) */
static float g_rayNormal[3];        /* the ground's normal by the rays then (the slope behind, level across) */
static float g_groundN[3], g_avgN[3] = { 0.0f, 0.0f, 1.0f };
static float g_avgAge;                  /* seconds of ground in the average (capped) */

/* The track: where the player's feet were on the ground while riding, newest last. The
 * parked bike goes on it, a bike length behind the player: ground they really rode on. */
typedef struct { float p[3], n[3]; } TrackPoint;
#define TRACK_POINTS 128
#define TRACK_SPACING 8.0f              /* units between points */
#define TRACK_MAX_AIR 0.4f              /* longer in the air (a drop): the track starts again */
#define PARK_DISTANCE 145.0f            /* the parked bike's middle this far from the player's feet */
#define PARK_SPAN 40.0f                 /* its heading and pitch from the track this far either side */
#define PARK_MAX_SLOPE 45.0f            /* no steeper than this: further back along the track if need be */
#define PARK_MAX_CROSS 20.0f            /* nor leaning more than this across the bike */
#define PARK_STEP 16.0f
#define PARK_SEARCH 1000.0f             /* how far back to look for such a spot */
#define TRACK_PITCH_BACK 120.0f         /* riding pitch: the track's slope over about a wheelbase */
static TrackPoint g_track[TRACK_POINTS];
static int g_trackHead, g_trackCount;
static bool g_trackPitchOk;             /* this frame: the slope of the track just ridden, along the heading */
static float g_trackPitch;
static bool g_hadTrackPitch;            /* since the track (re)started: hold rather than use the normal */
static float g_trackAddedAt = -100.0f;  /* when the newest track point was added (g_clock) */
static bool g_trackSteepOk;             /* this frame: how steep the track itself is (degrees) */
static float g_trackSteep;
static float g_airTime;
static bool g_parkValid;                /* the last spot worked out, for the log on getting off */
static float g_parkSpot[7];
static const char *g_parkWhy = "";
static float g_parkPublished[7] = { 0 }, g_parkPublishedAt = -100.0f;   /* the last good spot written, and when */

static uintptr_t g_stateCtrl;           /* the controller the state check below was made on */
static bool g_stateTrusted;
static int g_lastState = -1, g_stateLogs;

/* Tilt: the worn bike's skins we hold, and what they were. The Harley build has twelve
 * shapes since test 38: three static, four that turn with the bars, three of the lower fork
 * (with the bars and the front wheel's travel) and the two wheels. */
#define MAX_SKINS 16
#define MAX_BONES 4
enum { ROLE_UNKNOWN = -1, ROLE_NONE, ROLE_WHEEL_F, ROLE_WHEEL_R, ROLE_FRONT, ROLE_GLOW, ROLE_FORK };   /* GLOW: the headlamp's lit parts, with the bar assembly; FORK: the lower fork legs, the front mudguard and the caliper, with the bars and the front wheel's travel */
typedef struct {
	uintptr_t boneData;                 /* BSSkin::BoneData, with a reference of ours */
	uintptr_t bones;                    /* its BoneTransforms */
	int count;
	uint8_t original[MAX_BONES][BONE_SIZE];
	char name[48];
	int role;                           /* which moving part it is (ROLE_*), told by its culling sphere */
	float centre[3];                    /* its culling sphere's centre in the bike's own space */
	uintptr_t skin;                     /* its BSSkin::Instance */
	uintptr_t node;                     /* the bone it's bound to (COM), through the instance's bone list; 0 if not found */
} HeldSkin;
static HeldSkin g_skins[MAX_SKINS];
static int g_skinCount;

/* The rider (test 23: on a slope the bike pitched and the rider stayed level, the hands in
 * the air). The plugin runs before the animation writes the bones, so it can't pitch the
 * skeleton; what it can do is what it does for the bike: skin data. Every skinned shape of
 * the player's 3D but the bike's (the body, the outfit, the head, the hair) gets its
 * skin-to-bone transforms rewritten each frame so that, with the bones where they were last
 * frame, the mesh lands where the bike's tilt about the pivot would put it. The game's own
 * bone data is shared with every NPC wearing the same mesh (and the model cache), so it's
 * never written: each held shape's skin instance is pointed at a copy of ours while riding
 * and back after. Plain shapes under the bones (a holstered weapon, the Pip-Boy) get the same
 * map in front of their own transform. */
#define MAX_RIDER 160
#define MAX_RIDER_BONES 320
#define REPLICA_REFS 0x100000
typedef struct {
	uintptr_t shape;                    /* BSGeometry, a reference of ours */
	uintptr_t skin;                     /* BSSkin::Instance, a reference of ours; 0 for a plain shape */
	uintptr_t original;                 /* the instance's own BoneData, put back on letting go */
	uintptr_t replica;                  /* ours, in its place while held */
	uint8_t *live;                      /* the replica's transforms (count x BONE_SIZE), or the shape's local transform */
	uint8_t *saved;                     /* what they were */
	uint8_t *skip;                      /* per bone: 1 = left as it is (its node can't be read, or isn't a rigid transform) */
	uint8_t *arm;                      /* each bone's part in the arms (ArmRole), for the bars' turn */
	uintptr_t xforms;                  /* the skin's array of each bone's world transform pointer, for bones without a node (test 34) */
	float *lastPos;                    /* each bone's node position last frame, relative to the bike's bone (the jump stat, test 33) */
	bool lastPosOk;
	uintptr_t nodes;                    /* the instance's bone nodes (NiAVObject * each) */
	int count;
	char name[40];
	char inherited[600];                /* the bones given their parents' part, for the hold's line (test 38's pose study; a body's ten helpers fit) */
	int inheritedN, inheritedListed;
} RiderPart;
static RiderPart *OwnerOfReplica(uintptr_t data);
static bool IsReplica(uintptr_t data);
static RiderPart g_rider[MAX_RIDER];
static int g_riderCount;
typedef struct { uintptr_t obj; uint8_t *entries; int capacity; bool inUse; } Replica;
static Replica g_replicas[MAX_RIDER * 2];   /* never freed: a reference the game still holds must never find them gone */
static int g_replicaCount;
static int g_riderTilt = 1;
static int g_riderSkinned = 1, g_riderPlain = 1, g_riderSwap = 1, g_riderWrite = 1;   /* A/B switches (test 25: 30 fps lost) */
static int g_riderHands = 1;                /* the hands (and part of the forearms) turn with the bars (test 29: the clips keep them at the straight grips) */
static float g_liftNow;                     /* the bike (and rider) lifted this much along the bike's up: the wheels onto the ground between the rays, and over a bump */
static bool g_wheelPitchOk;                 /* this frame: both wheel rays hit, g_wheelPitch is their pitch, g_wheelLift the lift */
static float g_wheelPitch, g_wheelLift;
static float g_pitchVel, g_rollVel;         /* the damped filter's velocities (degrees a second) */
static float g_airFor;                      /* how long the controller has said "in the air" (hysteresis: test 29's state flapped every frame) */
static int g_wheelRaysMissed;               /* for the trace */
static bool g_riderIdle;                    /* the originals are in place: nothing written since */
static bool g_riderLevel = true;            /* the tilt is within the deadband: the rider's shapes are left as they are */
static bool NodeWorld(uintptr_t node, float N[9], float n[3], float *s, float Ni[9]);   /* defined with the rider */
static bool TransformWorld(uintptr_t xf, float N[9], float n[3], float *s, float Ni[9]);   /* defined with the rider */
static void NodelessRoles(void);
static bool Invert3(const float *a, float *out);
static float CastRay(uintptr_t cell, const float a[3], const float b[3]);   /* defined with the reverse's rays */
static float CastRayGround(uintptr_t cell, const float a[3], const float b[3]);   /* the same, passing through actors */
static bool RaysReady(uintptr_t player);
static uint8_t ArmRole(const char *name);
static bool NodeWorldChecked(uintptr_t node, float N[9], float n[3], float *s, float Ni[9]);
static char g_iniPath[MAX_PATH];
/* Where the frame time goes (test 25: about 7 ms a frame lost on the bike): QPC around the
 * frame, the bike's part, the rider's and the skin sync, averaged and the worst, per trace line. */
typedef struct { double sum, max; int n; } Timing;
static Timing g_tFrame, g_tTilt, g_tRider, g_tSync;
static int g_queries, g_queryFrames;        /* VirtualQuery calls (the region cache's misses), and frames */
static bool g_riderWorldChecked, g_riderWorldOk, g_riderBoneWarned;
static bool g_riderBlocked;                 /* this ride: a skinned shape couldn't be held, so none is (a part-tilted rider tears) */
static float g_riderPivot[3];
static bool g_riderApplied;                 /* this frame: the rider's shapes carried by the tilt */
/* A load into a ride (finding 2 of test 40: after an in-game load on the bike the lean was lost,
 * and the log that would have told which latch had fired was overwritten at the next start). */
static float g_riderWorldFailSince = -1.0f; /* when the 3D root's world first read away from the player this ride (-1: it hasn't): asked again every sync, kept as a no only after 3 s */
static bool g_loadPending;                  /* a save loaded or a new game: the next tick says whether the ride resumed */
static float g_loadAt = -100.0f;            /* when (g_clock) */
static bool g_rideFromLoad;                 /* this ride was started by a load: the once-a-ride lines say so */
static int g_loadLook;                      /* the looks taken at that ride: 2.5 s in (and the re-hold), then 6 s in (the log only) */
static bool g_riderBikeOk;                  /* FrameRider's last word on the bike's bone: readable */
static bool g_torsoNoChain;                 /* the upper body's lean given up for want of an arm chain */
static int g_skinsUnbuilt;                  /* bike skins refused for having no bone transforms to read yet, since g_refused was last cleared */
static int g_skinsRefused;                  /* bike skins refused for any reason, likewise */
static float g_tickSlope, g_tickCamera, g_tickTilt;   /* the three riding globals as the last tick read them: what they were before a load */
static float g_tiltZeroSince = -1.0f;       /* riding with CMB_TiltLive at 0 (the slope or the camera on) since then (-1: it isn't) */
static int g_tiltZeroSaid;                  /* this ride: 1 that's been said, 2 and that it came back */
static int g_logRotated;                    /* the session before's log: 1 kept as CMB_Slope_prev.log, -1 it couldn't be, 0 there was none */
static unsigned long g_logRotateError;

/* The moving parts (CMB_BikeParts.ini, written by harley_meshes.py next to the meshes, in
 * the worn bike's own space: +Y forward, Z up). A shape whose culling sphere sits on an
 * axle is a wheel and spins with the distance ridden; one whose sphere is ahead of
 * FrontMinY is the bar assembly and turns about the steering axis with the rider's
 * turning. Without the file nothing on the bike moves, as before. */
static bool g_partsOk;
static char g_partsFile[MAX_PATH];
static float g_frontAxle[3], g_rearAxle[3], g_wheelRadius, g_steerPoint[3], g_steerAxis[3], g_frontMinY, g_barAngle;
static bool g_gripOk;                    /* Grip in the parts file: the +x grip's centre (the left is x mirrored), the wrist roll's pivot (test 38: without it the hand rolls about its own node, 6.5 units from the grip's centre, and the palm swings off the bar) */
static float g_grip[3];
static float g_barFullAt = 45.0f;        /* deg/s of turning at which the bars are fully over */
static float g_wheelAngle;               /* the wheels' spin, radians */
static float g_barNow, g_headingRate;    /* the bars' turn now (degrees, + left); the rider's turning (deg/s) */
static float g_lastHeading;
static bool g_haveLastHeading;
static int g_layout = LAYOUT_UNKNOWN;   /* how the game stores rotations, once known */
static int g_layoutFromSkin = LAYOUT_UNKNOWN, g_layoutFromRoot = LAYOUT_UNKNOWN;
#define TILT_SAMPLES 64
typedef struct { float pitch, roll, time; } TiltSample;
static TiltSample g_tiltSamples[TILT_SAMPLES];
static int g_tiltSampleHead, g_tiltSampleCount;
static float g_pitchSmooth, g_rollSmooth;   /* degrees, after the median and smoothing */
static float g_pitchNow, g_rollNow;         /* degrees, applied (after the rate limit and caps) */
static float g_clock, g_lastTrace;          /* seconds of frames */
static float g_tiltNow, g_tiltMax;      /* degrees: this frame, most this ride */
static LARGE_INTEGER g_qpcFrequency, g_lastFrameTime;
static int g_walkBudget;
static uintptr_t g_refused[8];          /* skins found unfit: not looked at again */
static int g_emptySyncs;                /* checks in a row this ride that found no bike */
static bool g_rideDiagnosed, g_rideRouteLogged;
static int g_refusedCount;

/* Accessible()'s memory regions, kept across frames (the scene graph walk reads thousands
 * of pointers; asking Windows about each one would cost milliseconds); each with the tick
 * it was read at, good for 30 s and a stagger of its own (ForgetRegions). */
typedef struct { uintptr_t start, end; bool writable; DWORD at; } Region;
#define REGIONS 256
static Region g_regions[REGIONS];
static int g_regionCount, g_regionNext;
static DWORD g_regionTick;                  /* the frame's tick, for the entries' ages (set once a frame: the lookup runs thousands of times) */
static int g_syncQueries, g_syncQueriesMax; /* VirtualQuery calls inside the skin syncs, per trace line: in all, and the most in one sync */

/* ------------------------------------------------------------------------- */
/* Log and settings                                                          */
/* ------------------------------------------------------------------------- */

static void Log(const char *fmt, ...)
{
	if (!g_log)
		return;
	SYSTEMTIME t;
	GetLocalTime(&t);
	fprintf(g_log, "%02u:%02u:%02u.%03u ", t.wHour, t.wMinute, t.wSecond, t.wMilliseconds);
	va_list args;
	va_start(args, fmt);
	vfprintf(g_log, fmt, args);
	va_end(args);
	fputc('\n', g_log);
	fflush(g_log);
}

/* " (T s into the ride, after a load)" for a once-a-ride line in a ride a load started (finding
 * 2 of test 40: which of these had fired could not be told from the log). One per Log call. */
static const char *AfterLoadNote(void)
{
	static char note[48];
	if (!g_rideFromLoad)
		return "";
	snprintf(note, sizeof(note), " (%.1f s into the ride, after a load)", (float)g_clock - g_rideStartClock);
	return note;
}

/* The log of the session before kept as CMB_Slope_prev.log, one generation (test 40: the game
 * was restarted after the load that lost the lean, and its log was gone): moved aside just
 * before the new one is opened in its place. */
static void RotateLog(const char *path)
{
	char prev[MAX_PATH];
	size_t n = strlen(path);
	if (GetFileAttributesA(path) == INVALID_FILE_ATTRIBUTES)
		return;
	if (n >= 4 && _stricmp(path + n - 4, ".log") == 0)
		n -= 4;
	if (n + sizeof("_prev.log") > sizeof(prev))
		return;
	memcpy(prev, path, n);
	strcpy(prev + n, "_prev.log");
	if (MoveFileExA(path, prev, MOVEFILE_REPLACE_EXISTING)) {
		g_logRotated = 1;
	} else {
		g_logRotated = -1;
		g_logRotateError = GetLastError();
	}
}

static void OpenLog(void)
{
	char path[MAX_PATH];
	if (SUCCEEDED(SHGetFolderPathA(NULL, CSIDL_PERSONAL | CSIDL_FLAG_CREATE, NULL, SHGFP_TYPE_CURRENT, path))) {
		strncat(path, "\\My Games\\Fallout4\\F4SE", sizeof(path) - strlen(path) - 1);
		CreateDirectoryA(path, NULL);
		strncat(path, "\\CMB_Slope.log", sizeof(path) - strlen(path) - 1);
		RotateLog(path);
		g_log = fopen(path, "w");
	}
	if (!g_log) {
		/* Next to the DLL instead. */
		GetModuleFileNameA(g_module, path, sizeof(path));
		char *dot = strrchr(path, '.');
		if (dot)
			strcpy(dot, ".log");
		RotateLog(path);
		g_log = fopen(path, "w");
	}
}

static void ReadParts(const char *ini);
static void ReadLampSettings(const char *ini);

static float IniFloat(const char *ini, const char *section, const char *key, float fallback, float lo, float hi)
{
	char value[64], def[32];
	snprintf(def, sizeof(def), "%g", fallback);
	GetPrivateProfileStringA(section, key, def, value, sizeof(value), ini);
	float v = strtof(value, NULL);
	return v >= lo && v <= hi ? v : fallback;
}

/* A vector key, "x,y,z", each within 10; anything else gives the fallback. */
static void IniVec(const char *ini, const char *section, const char *key, const float fallback[3], float out[3])
{
	char value[128];
	float v[3];
	GetPrivateProfileStringA(section, key, "", value, sizeof(value), ini);
	if (sscanf(value, "%f,%f,%f", &v[0], &v[1], &v[2]) == 3 && isfinite(v[0]) && isfinite(v[1]) && isfinite(v[2]) &&
	    fabsf(v[0]) <= 10.0f && fabsf(v[1]) <= 10.0f && fabsf(v[2]) <= 10.0f)
		memcpy(out, v, sizeof(v));
	else
		memcpy(out, fallback, sizeof(v));
}

/* The inside arm's fade (test 41) is on: both poles given and ArmPoleTurnBars over 0. */
static bool ArmFadeOn(void)
{
	return fabsf(g_armPole[0]) + fabsf(g_armPole[1]) + fabsf(g_armPole[2]) > 0.001f && fabsf(g_armPoleTurn[0]) + fabsf(g_armPoleTurn[1]) + fabsf(g_armPoleTurn[2]) > 0.001f &&
	       g_armPoleTurnBars > 0.0f;
}

/* One arm's pole now, in the bike's space, the right arm's sense (the caller mirrors the
 * left's x), and how far it is faded (0 to 1). Test 41: ArmPole 1.1,-0.3,-0.9 puts the elbows
 * out, the forearms near level (the tester's sketch), but the arm on the side the bars turn
 * to, whose grip comes back toward the shoulder, then folds out and the wrist turns more: in
 * the arm emulation (arms/arms.py, test 41's scratch) the inside wrist 52 deg from the clips'
 * pose with the bars 12 over at a run, against 31 at test 40's pole. So that arm's pole fades
 * to ArmPoleTurn (test 40's own) as the bars turn its way, k = |bars| / ArmPoleTurnBars, 1 at
 * most, the two normalised first so the fade goes by direction alone: the inside wrist 21 deg
 * at 4 deg of the bars (12 at test 40's pole) and 31 at 12 (test 40's own there), and the
 * outside arm keeps ArmPole (18 deg at 12 against test 40's 29). The left arm is the inside one
 * with the bars over to the left (+). */
static float ArmPoleNow(int side, float out[3])
{
	memcpy(out, g_armPole, sizeof(g_armPole));
	bool inside = side ? g_barNow < 0.0f : g_barNow > 0.0f;
	if (!ArmFadeOn() || !inside)
		return 0.0f;
	float k = fabsf(g_barNow) / g_armPoleTurnBars;
	if (k > 1.0f)
		k = 1.0f;
	if (k <= 0.0f)
		return 0.0f;
	float la = sqrtf(g_armPole[0] * g_armPole[0] + g_armPole[1] * g_armPole[1] + g_armPole[2] * g_armPole[2]);
	float lt = sqrtf(g_armPoleTurn[0] * g_armPoleTurn[0] + g_armPoleTurn[1] * g_armPoleTurn[1] + g_armPoleTurn[2] * g_armPoleTurn[2]);
	for (int i = 0; i < 3; i++)
		out[i] = (1.0f - k) * g_armPole[i] / la + k * g_armPoleTurn[i] / lt;
	return k;
}

/* The lean into turns, the upper body and the face look-ahead, read again on every mount (an
 * A/B needs no restart). */
static void ReadLeanSettings(const char *ini, bool log)
{
	static const float poleDefault[3] = { 1.1f, -0.3f, -0.9f }, poleTurnDefault[3] = { 0.35f, -0.3f, -1.0f };
	float was[21] = { g_maxLean, g_leanRate, g_leanSmooth, g_leanDead, g_leanGain, g_torsoLeanSetting, g_armReach, g_torsoTwist, g_faceLook, (float)g_headLevel, g_torsoSideLean, g_wristRoll, g_armPole[0], g_armPole[1], g_armPole[2], g_handPitch, g_torsoSolveFrom,
	                  g_armPoleTurn[0], g_armPoleTurn[1], g_armPoleTurn[2], g_armPoleTurnBars };
	g_maxLean = IniFloat(ini, "Tilt", "MaxLean", 14.0f, 0.0f, 45.0f);
	g_leanRate = IniFloat(ini, "Tilt", "LeanRate", 50.0f, 0.0f, 1000.0f);
	g_leanSmooth = IniFloat(ini, "Tilt", "LeanSmooth", 0.45f, 0.0f, 5.0f);
	g_leanDead = IniFloat(ini, "Tilt", "LeanDead", 0.08f, 0.0f, 2.0f);
	g_leanGain = IniFloat(ini, "Tilt", "LeanGain", 0.5f, 0.0f, 2.0f);
	g_headLevel = (int)GetPrivateProfileIntA("Tilt", "HeadLevel", 1, ini) != 0;
	g_torsoLeanSetting = IniFloat(ini, "Tilt", "TorsoLean", -1.0f, -1.0f, 30.0f);
	g_torsoSolveFrom = IniFloat(ini, "Tilt", "TorsoSolveFrom", 1.3f, 0.0f, 5.0f);
	g_armReach = IniFloat(ini, "Tilt", "ArmReach", 0.80f, 0.5f, 1.0f);
	g_torsoTwist = IniFloat(ini, "Tilt", "TorsoTwist", 0.75f, 0.0f, 1.0f);
	g_torsoSideLean = IniFloat(ini, "Tilt", "TorsoSideLean", 0.25f, 0.0f, 1.0f);
	g_wristRoll = IniFloat(ini, "Tilt", "WristRoll", 1.0f, 0.0f, 1.0f);
	g_handPitch = IniFloat(ini, "Tilt", "HandPitch", 0.0f, -45.0f, 45.0f);
	IniVec(ini, "Tilt", "ArmPole", poleDefault, g_armPole);
	IniVec(ini, "Tilt", "ArmPoleTurn", poleTurnDefault, g_armPoleTurn);
	g_armPoleTurnBars = IniFloat(ini, "Tilt", "ArmPoleTurnBars", 10.0f, 0.0f, 45.0f);
	g_faceLook = IniFloat(ini, "Steer", "FaceLook", 0.3f, 0.0f, 3.0f);
	float wasMore[18] = { g_turnEaseIn, g_turnEaseOut, g_liftRate, g_bumpMax, g_bumpSettle, g_wallAngle, g_obstacleThrottle, g_obstacleHold, (float)g_wallFrames,
	                      (float)g_suspension, g_suspFrequency, g_suspDamping, g_suspTravel, g_obstacleAngle, g_suspCompressRear, g_suspDroop, g_suspExtend, g_lowObstacleAngle };
	g_turnEaseIn = IniFloat(ini, "Steer", "TurnEaseIn", 0.14f, 0.0f, 3.0f);
	g_turnEaseOut = IniFloat(ini, "Steer", "TurnEaseOut", 0.08f, 0.0f, 3.0f);
	g_liftRate = IniFloat(ini, "Tilt", "LiftRate", 120.0f, 0.0f, 2000.0f);
	g_bumpMax = IniFloat(ini, "Tilt", "BumpMax", 30.0f, 0.0f, 60.0f);
	g_bumpSettle = IniFloat(ini, "Tilt", "BumpSettle", 0.45f, 0.0f, 5.0f);
	g_suspension = (int)GetPrivateProfileIntA("Tilt", "Suspension", 1, ini) != 0;
	g_suspFrequency = IniFloat(ini, "Tilt", "SuspFrequency", 2.0f, 0.5f, 5.0f);
	g_suspDamping = IniFloat(ini, "Tilt", "SuspDamping", 0.6f, 0.2f, 1.0f);
	g_suspTravel = IniFloat(ini, "Tilt", "SuspTravel", 10.0f, 0.0f, 30.0f);
	g_suspCompressRear = IniFloat(ini, "Tilt", "SuspCompressRear", 4.0f, 0.0f, 30.0f);
	g_suspDroop = IniFloat(ini, "Tilt", "SuspDroop", 4.0f, 0.0f, 30.0f);
	g_suspExtend = IniFloat(ini, "Tilt", "SuspExtend", 0.1f, 0.03f, 1.0f);
	g_wallAngle = IniFloat(ini, "Steer", "WallAngle", 55.0f, 20.0f, 90.0f);
	g_obstacleAngle = IniFloat(ini, "Steer", "ObstacleAngle", 50.0f, 20.0f, 80.0f);
	g_lowObstacleAngle = IniFloat(ini, "Steer", "LowObstacleAngle", 60.0f, 20.0f, 89.0f);
	g_obstacleThrottle = IniFloat(ini, "Steer", "ObstacleThrottle", 0.55f, 0.0f, 1.0f);
	g_obstacleHold = IniFloat(ini, "Steer", "ObstacleHold", 1.0f, 0.2f, 5.0f);
	g_wallFrames = (int)GetPrivateProfileIntA("Steer", "WallFrames", 5, ini);
	if (g_wallFrames < 1 || g_wallFrames > 30)
		g_wallFrames = 5;
	/* Climbing low things (test 40, finding 8), read again on getting on like the face rays'
	 * keys (an A/B needs no restart). */
	float wasClimb[8] = { (float)g_climb, g_climbBoost, g_climbTopSetting, g_climbMaxPitch, g_climbHold, g_climbMax, g_climbThrottle, (float)g_climbStep };
	g_climb = (int)GetPrivateProfileIntA("Steer", "Climb", 1, ini) != 0;
	g_climbBoost = IniFloat(ini, "Steer", "ClimbBoost", 85.0f, 47.0f, 89.0f);
	g_climbTopSetting = IniFloat(ini, "Steer", "ClimbTop", 0.0f, 0.0f, 60.0f);
	g_climbMaxPitch = IniFloat(ini, "Steer", "ClimbMaxPitch", 22.0f, 0.0f, 60.0f);
	g_climbHold = IniFloat(ini, "Steer", "ClimbHold", 0.3f, 0.05f, 3.0f);
	g_climbMax = IniFloat(ini, "Steer", "ClimbMax", 1.5f, 0.2f, 10.0f);
	g_climbThrottle = IniFloat(ini, "Steer", "ClimbThrottle", 0.4f, 0.1f, 1.0f);
	g_climbStep = (int)GetPrivateProfileIntA("Steer", "ClimbStep", 1, ini) != 0;   /* stage 2 (test 41), with the boost only */
	float nowClimb[8] = { (float)g_climb, g_climbBoost, g_climbTopSetting, g_climbMaxPitch, g_climbHold, g_climbMax, g_climbThrottle, (float)g_climbStep };
	/* The light's placing, read again on getting on as well (an A/B needs no restart). */
	g_lampAhead = IniFloat(ini, "Lamp", "Ahead", 28.0f, -100.0f, 200.0f);
	g_lampLead = IniFloat(ini, "Lamp", "Lead", 1.0f, 0.0f, 5.0f);
	g_lampHandoverFrames = (int)GetPrivateProfileIntA("Lamp", "HandoverFrames", 5, ini);
	if (g_lampHandoverFrames < 0 || g_lampHandoverFrames > 100)
		g_lampHandoverFrames = 5;
	float nowMore[18] = { g_turnEaseIn, g_turnEaseOut, g_liftRate, g_bumpMax, g_bumpSettle, g_wallAngle, g_obstacleThrottle, g_obstacleHold, (float)g_wallFrames,
	                      (float)g_suspension, g_suspFrequency, g_suspDamping, g_suspTravel, g_obstacleAngle, g_suspCompressRear, g_suspDroop, g_suspExtend, g_lowObstacleAngle };
	float now[21] = { g_maxLean, g_leanRate, g_leanSmooth, g_leanDead, g_leanGain, g_torsoLeanSetting, g_armReach, g_torsoTwist, g_faceLook, (float)g_headLevel, g_torsoSideLean, g_wristRoll, g_armPole[0], g_armPole[1], g_armPole[2], g_handPitch, g_torsoSolveFrom,
	                  g_armPoleTurn[0], g_armPoleTurn[1], g_armPoleTurn[2], g_armPoleTurnBars };
	bool changed = false;
	for (int i = 0; i < 18; i++)
		changed = changed || wasMore[i] != nowMore[i];
	for (int i = 0; i < 21; i++)
		changed = changed || was[i] != now[i];
	for (int i = 0; i < 8; i++)
		changed = changed || wasClimb[i] != nowClimb[i];
	if (log || changed) {
		char torso[96], pole[96], fade[200];
		if (g_torsoLeanSetting < 0.0f)
			snprintf(torso, sizeof(torso), "leaned forward as needed, solved from %g s into the ride (TorsoSolveFrom)", g_torsoSolveFrom);
		else
			snprintf(torso, sizeof(torso), "leaned %g deg forward", g_torsoLeanSetting);
		if (fabsf(g_armPole[0]) + fabsf(g_armPole[1]) + fabsf(g_armPole[2]) > 0.001f)
			snprintf(pole, sizeof(pole), "toward (%g, %g, %g) in the bike's space, the left mirrored", g_armPole[0], g_armPole[1], g_armPole[2]);
		else
			snprintf(pole, sizeof(pole), "in their own planes as the clips pose them");
		if (ArmFadeOn())
			snprintf(fade, sizeof(fade), ", the inside arm's (the side the bars turn to) faded toward (%g, %g, %g) as they turn, all of it at %g deg of the bars (ArmPoleTurn, ArmPoleTurnBars)",
			         g_armPoleTurn[0], g_armPoleTurn[1], g_armPoleTurn[2], g_armPoleTurnBars);
		else
			snprintf(fade, sizeof(fade), ", the inside arm's not faded as the bars turn (%s)",
			         fabsf(g_armPole[0]) + fabsf(g_armPole[1]) + fabsf(g_armPole[2]) <= 0.001f ? "ArmPole 0,0,0" : g_armPoleTurnBars <= 0.0f ? "ArmPoleTurnBars 0" : "ArmPoleTurn 0,0,0");
		Log("  lean: into turns up to %g deg (MaxLean), at most %g deg/s (LeanRate), the turning rate over %g s (LeanSmooth), none under %g (LeanDead), %g of the physical lean (LeanGain); "
		    "the head %s (HeadLevel); the upper body %s (TorsoLean), the grips at %g of the arms' reach (ArmReach), turned %g of the bars (TorsoTwist), leaned %g deg into the turn per degree of the bars (TorsoSideLean); "
		    "the hands rolled round the grips %g of the way to their long axes lying in line with the forearms seen along the grips (WristRoll), %g deg above them, the knuckles up (HandPitch), the elbows bent %s (ArmPole)%s; a face ahead looked for %g s of the speed (FaceLook)%s",
		    g_maxLean, g_leanRate, g_leanSmooth, g_leanDead, g_leanGain, g_headLevel ? "kept level" : "tilting with the bike", torso, g_armReach, g_torsoTwist, g_torsoSideLean, g_wristRoll, g_handPitch, pole, fade, g_faceLook,
		    log ? "" : " (read again on getting on)");
		Log("  steer: the keys' turning rate eases in over %g s and out over %g s (TurnEaseIn, TurnEaseOut); a wall is a face of %g deg or more (WallAngle), an obstacle one of %g deg or more, or the climb limit if that is higher (ObstacleAngle), "
		    "a lower-only one (nothing at 1.5 wheel radii) one of %g deg or more (LowObstacleAngle), holding the throttle to %g (ObstacleThrottle), its verdict in force for %g s after the rays last saw one (ObstacleHold), in which a wall counts only after %d frames seen ahead of the wheel (WallFrames); "
		    "the lift rises at most %g units a second (LiftRate), a wheel's bump lift at most %g in one go and settles over %g s (BumpMax, BumpSettle); "
		    "the suspension %s (Suspension), the frame's lift on a spring of %g Hz with a damping ratio of %g, the wheels rising at most %g into the frame, the rear %g, dropping at most %g below it (the frame sinking by that at most), extending over %g s (SuspFrequency, SuspDamping, SuspTravel, SuspCompressRear, SuspDroop, SuspExtend); "
		    "the light %g ahead of the lens, led by %g frames of the speed, the old one kept %d frames at a handover (Ahead, Lead, HandoverFrames)",
		    g_turnEaseIn, g_turnEaseOut, g_wallAngle, g_obstacleAngle, g_lowObstacleAngle, g_obstacleThrottle, g_obstacleHold, g_wallFrames, g_liftRate, g_bumpMax, g_bumpSettle,
		    g_suspension ? "on" : "off", g_suspFrequency, g_suspDamping, g_suspTravel, g_suspCompressRear, g_suspDroop, g_suspExtend, g_lampAhead, g_lampLead, g_lampHandoverFrames);
		char top[32];
		if (g_climbTopSetting > 0.0f)
			snprintf(top, sizeof(top), "%g", g_climbTopSetting);
		else
			snprintf(top, sizeof(top), "the wheel radius + 2");
		char step[300];
		if (g_climbStep)
			snprintf(step, sizeof(step), "; a sharp step the limit can't take stepped up onto (ClimbStep=1): 0.25 s into the boost with the speed along still under 40, its top (over 4 and ClimbTop at most) found by three rays down "
			         "and room for the capsule over it, the controller put up by the top + 1.5 and 4 on, twice an obstacle at most, 0.25 s apart");
		else
			snprintf(step, sizeof(step), "; sharp steps not stepped up onto (ClimbStep=0)");
		if (g_climb)
			Log("  climb: low things at the capsule climbed (Climb=1): the slope limit raised to %g deg (ClimbBoost) while a face at the capsule has nothing %s above the feet behind it (ClimbTop) and forward is held, "
			    "the wheels' line pitched %g deg at most (ClimbMaxPitch), for %g s after the face was last seen (ClimbHold), given up after %g s stalled (ClimbMax), the throttle let up to %g of the top meanwhile (ClimbThrottle)%s%s",
			    g_climbBoost, top, g_climbMaxPitch, g_climbHold, g_climbMax, g_climbThrottle, step, log ? "" : " (read again on getting on)");
		else
			Log("  climb: low things at the capsule not climbed (Climb=0): the slope limit stays the riding one, and nothing stepped up onto either (ClimbStep goes with the boost)%s", log ? "" : " (read again on getting on)");
	}
}

/* Knocking enemies over (test 40's wish; [Ram]), read at the start and again on getting on (an
 * A/B needs no restart). */
static void ReadRamSettings(const char *ini, bool log)
{
	float was[10] = { (float)g_ramOn, g_ramLook, g_ramLead, g_ramPass, (float)g_ramMaxSize, (float)g_ramNoKnockdowns, g_ramAskAgain, g_ramAskAgainNo, g_ramHitKeep, g_ramHitHold };
	g_ramOn = (int)GetPrivateProfileIntA("Ram", "Enabled", 1, ini) != 0;
	g_ramLook = IniFloat(ini, "Ram", "ActorLook", 0.8f, 0.0f, 3.0f);
	g_ramLead = IniFloat(ini, "Ram", "Lead", 0.06f, 0.0f, 1.0f);
	g_ramPass = IniFloat(ini, "Ram", "Pass", 1.0f, 0.0f, 5.0f);
	g_ramMaxSize = (int)GetPrivateProfileIntA("Ram", "MaxSize", 1, ini);
	if (g_ramMaxSize < 0 || g_ramMaxSize > 3)
		g_ramMaxSize = 1;
	g_ramNoKnockdowns = (int)GetPrivateProfileIntA("Ram", "NoKnockdowns", 1, ini) != 0;
	g_ramAskAgain = IniFloat(ini, "Ram", "AskAgain", 0.4f, 0.1f, 5.0f);
	g_ramAskAgainNo = IniFloat(ini, "Ram", "AskAgainNo", 1.0f, 0.1f, 10.0f);
	g_ramHitKeep = IniFloat(ini, "Ram", "HitKeep", 0.6f, 0.0f, 1.0f);
	g_ramHitHold = IniFloat(ini, "Ram", "HitHold", 0.4f, 0.0f, 3.0f);
	float now[10] = { (float)g_ramOn, g_ramLook, g_ramLead, g_ramPass, (float)g_ramMaxSize, (float)g_ramNoKnockdowns, g_ramAskAgain, g_ramAskAgainNo, g_ramHitKeep, g_ramHitHold };
	bool changed = false;
	for (int i = 0; i < 10; i++)
		changed = changed || was[i] != now[i];
	if (log || changed)
		Log("  ram: Enabled=%d ActorLook=%g Lead=%g Pass=%g MaxSize=%d NoKnockdowns=%d AskAgain=%g AskAgainNo=%g HitKeep=%g HitHold=%g: %s%s", g_ramOn, g_ramLook, g_ramLead,
		    g_ramPass, g_ramMaxSize, g_ramNoKnockdowns, g_ramAskAgain, g_ramAskAgainNo, g_ramHitKeep, g_ramHitHold,
		    !g_ramOn ? "off, no actor asked about, every one braked for as before test 41"
		    : g_ramHitHold > 0.0f && g_ramHitKeep < 1.0f ? "on, the bike losing speed at a hit" : "on, the speed kept at a hit (HitHold=0 or HitKeep=1)",
		    log ? "" : " (read again on getting on)");
}

/* Backing level or down a slope (test 40's finding 6: "backing up makes the camera shake a
 * bit", downhill only), read at the start and again on getting on (an A/B needs no restart).
 * BackFollow=0 gives test 40's rule back exactly. */
static void ReadBackSettings(const char *ini, bool log)
{
	float was[2] = { g_backFollow, g_backClose };
	g_backFollow = IniFloat(ini, "Steer", "BackFollow", 10.0f, 0.0f, 40.0f);
	g_backClose = IniFloat(ini, "Steer", "BackClose", 0.1f, 0.0f, 2.0f);
	if (!log && was[0] == g_backFollow && was[1] == g_backClose)
		return;
	if (g_backFollow > 0.0f)
		Log("  reverse: BackFollow=%g BackClose=%g: going back level or down, each step follows the ground's slope over %g units centred on its middle, "
		    "the controller supported or not; unsupported, a gap over the controller's own clearance (the gap it kept while supported, %g at least, less BackSink) "
		    "is closed over %g s, at most 120 a second and 3 a step%s",
		    g_backFollow, g_backClose, g_backFollow, BACK_HOVER, g_backClose, log ? "" : " (read again on getting on)");
	else
		Log("  reverse: BackFollow=0 BackClose=%g: going back level or down, each step follows the slope 55 back, and unsupported the gap is closed to %g over "
		    "the ground, 3 a step at most (test 40's rule)%s", g_backClose, BACK_HOVER, log ? "" : " (read again on getting on)");
}

/* The rider's switches, read again on every mount (an A/B needs no restart; test 25). */
static void ReadRiderSwitches(bool log)
{
	const char *ini = g_iniPath;
	int was[5] = { g_riderTilt, g_riderSkinned, g_riderPlain, g_riderSwap, g_riderWrite };
	g_riderTilt = (int)GetPrivateProfileIntA("Tilt", "Rider", 1, ini);
	g_riderSkinned = (int)GetPrivateProfileIntA("Tilt", "RiderSkinned", 1, ini);
	g_riderPlain = (int)GetPrivateProfileIntA("Tilt", "RiderPlain", 1, ini);
	g_riderSwap = (int)GetPrivateProfileIntA("Tilt", "RiderSwap", 1, ini);
	g_riderWrite = (int)GetPrivateProfileIntA("Tilt", "RiderWrite", 1, ini);
	int hadHands = g_riderHands;
	g_riderHands = (int)GetPrivateProfileIntA("Tilt", "RiderHands", 1, ini);
	if (log || was[0] != g_riderTilt || was[1] != g_riderSkinned || was[2] != g_riderPlain || was[3] != g_riderSwap || was[4] != g_riderWrite || hadHands != g_riderHands)
		Log("  rider: Rider=%d RiderSkinned=%d RiderPlain=%d RiderSwap=%d RiderWrite=%d RiderHands=%d%s", g_riderTilt, g_riderSkinned, g_riderPlain,
		    g_riderSwap, g_riderWrite, g_riderHands, log ? "" : " (read again on getting on)");
	ReadLeanSettings(ini, false);
}

static void ReadSettings(void)
{
	char ini[MAX_PATH], value[256];
	GetModuleFileNameA(g_module, ini, sizeof(ini));
	char *dot = strrchr(ini, '.');
	if (!dot)
		return;
	strcpy(dot, ".ini");
	snprintf(g_iniPath, sizeof(g_iniPath), "%s", ini);
	GetPrivateProfileStringA("Slope", "Target", "controller", value, sizeof(value), ini);
	g_target = _stricmp(value, "proxy") == 0 ? TARGET_PROXY : TARGET_CONTROLLER;
	GetPrivateProfileStringA("Slope", "SlopeOffset", "", value, sizeof(value), ini);
	g_slopeOffset = (unsigned)strtoul(value, NULL, 0);
	GetPrivateProfileStringA("Slope", "SlopeUnit", "cosine", value, sizeof(value), ini);
	g_unit = _stricmp(value, "radians") == 0 ? UNIT_RADIANS : _stricmp(value, "degrees") == 0 ? UNIT_DEGREES : UNIT_COSINE;
	GetPrivateProfileStringA("Slope", "ExpectedDegrees", "0", value, sizeof(value), ini);
	g_expectedDegrees = strtof(value, NULL);
	g_probe = (int)GetPrivateProfileIntA("Slope", "Probe", 0, ini);
	g_interval = (DWORD)GetPrivateProfileIntA("Slope", "IntervalMs", 100, ini);
	if (g_interval < 16)
		g_interval = 16;
	GetPrivateProfileStringA("Slope", "DumpPointers", "", value, sizeof(value), ini);
	for (char *p = value; *p && g_dumpPointerCount < 8;) {
		char *end;
		unsigned long off = strtoul(p, &end, 0);
		if (end == p)
			break;
		if (off < 0x1000 && !(off & 7))
			g_dumpPointers[g_dumpPointerCount++] = (int)off;
		p = end;
		while (*p == ',' || *p == ' ')
			p++;
	}
	GetPrivateProfileStringA("Camera", "Setting", CAMERA_SETTING, g_cameraSettingName, sizeof(g_cameraSettingName), ini);
	g_zoomOut = (int)GetPrivateProfileIntA("Camera", "ZoomOut", 1, ini);
	GetPrivateProfileStringA("Camera", "ZoomTargetOffset", "0xE8", value, sizeof(value), ini);
	g_zoomTargetOffset = (unsigned)strtoul(value, NULL, 0) & ~3u;
	GetPrivateProfileStringA("Camera", "ZoomCurrentOffset", "0xEC", value, sizeof(value), ini);
	g_zoomCurrentOffset = (unsigned)strtoul(value, NULL, 0) & ~3u;
	GetPrivateProfileStringA("Tilt", "NormalOffset", "0x1E0", value, sizeof(value), ini);
	g_normalOffset = (unsigned)strtoul(value, NULL, 0) & ~3u;
	GetPrivateProfileStringA("Tilt", "StateOffset", "0x2C0", value, sizeof(value), ini);
	g_stateOffset = (unsigned)strtoul(value, NULL, 0) & ~3u;
	GetPrivateProfileStringA("Tilt", "Smoothing", "0.25", value, sizeof(value), ini);
	g_smoothing = strtof(value, NULL);
	if (!(g_smoothing >= 0.0f && g_smoothing <= 2.0f))
		g_smoothing = 0.25f;
	GetPrivateProfileStringA("Tilt", "MedianTime", "0.25", value, sizeof(value), ini);
	g_medianTime = strtof(value, NULL);
	if (!(g_medianTime >= 0.0f && g_medianTime <= 1.0f))
		g_medianTime = 0.25f;
	GetPrivateProfileStringA("Tilt", "MaxRate", "90", value, sizeof(value), ini);
	g_maxRate = strtof(value, NULL);
	if (!(g_maxRate >= 0.0f && g_maxRate <= 10000.0f))
		g_maxRate = 90.0f;
	GetPrivateProfileStringA("Tilt", "MaxRoll", "0", value, sizeof(value), ini);
	g_maxRoll = strtof(value, NULL);
	if (!(g_maxRoll >= 0.0f && g_maxRoll <= 45.0f))
		g_maxRoll = 0.0f;
	ReadLeanSettings(ini, true);
	GetPrivateProfileStringA("Tilt", "PivotHeight", "0", value, sizeof(value), ini);
	g_pivotHeight = strtof(value, NULL);
	if (!(g_pivotHeight >= -50.0f && g_pivotHeight <= 200.0f))
		g_pivotHeight = 0.0f;
	GetPrivateProfileStringA("Tilt", "PivotForward", "0", value, sizeof(value), ini);
	g_pivotForward = strtof(value, NULL);
	if (!(g_pivotForward >= -50.0f && g_pivotForward <= 100.0f))
		g_pivotForward = 0.0f;
	g_trace = (int)GetPrivateProfileIntA("Tilt", "Trace", 0, ini);
	g_steer = (int)GetPrivateProfileIntA("Steer", "Enabled", 1, ini);
	GetPrivateProfileStringA("Steer", "FullSpeed", "900", value, sizeof(value), ini);
	g_fullSpeed = strtof(value, NULL);
	if (!(g_fullSpeed > 0.0f && g_fullSpeed < 100000.0f))
		g_fullSpeed = 900.0f;
	g_reverse = (int)GetPrivateProfileIntA("Steer", "Reverse", 1, ini);
	g_inputHook = (int)GetPrivateProfileIntA("Steer", "InputHook", 1, ini);
	g_creep = (int)GetPrivateProfileIntA("Steer", "Creep", 1, ini);
	GetPrivateProfileStringA("Steer", "CreepInput", "0.1", value, sizeof(value), ini);
	g_creepStart = strtof(value, NULL);
	if (!(g_creepStart >= 0.02f && g_creepStart <= 1.0f))
		g_creepStart = 0.1f;
	g_creepInput = g_creepGood = g_creepStart;
	GetPrivateProfileStringA("Steer", "CreepBelow", "100", value, sizeof(value), ini);
	g_creepBelow = strtof(value, NULL);
	if (!(g_creepBelow >= 0.0f && g_creepBelow <= 1000.0f))
		g_creepBelow = 100.0f;
	GetPrivateProfileStringA("Steer", "CreepRadius", "55", value, sizeof(value), ini);
	g_creepRadius = strtof(value, NULL);
	if (!(g_creepRadius >= 0.0f && g_creepRadius <= 1000.0f))
		g_creepRadius = 55.0f;
	GetPrivateProfileStringA("Steer", "BackSpeed", "80", value, sizeof(value), ini);
	g_backSpeed = strtof(value, NULL);
	if (!(g_backSpeed > 0.0f && g_backSpeed <= 400.0f))
		g_backSpeed = 80.0f;
	GetPrivateProfileStringA("Steer", "BackPush", "auto", value, sizeof(value), ini);
	static const char *const pushValues[] = { "delta", "ray", "mod", "velocity", "position", "off" };
	g_backPushAuto = true;
	g_backPushFirst = PUSH_RAYSTEP;
	for (int i = 0; i <= PUSH_BRAKE; i++)
		if (_stricmp(value, pushValues[i]) == 0) {
			g_backPushAuto = false;
			g_backPushFirst = i;
		}
	GetPrivateProfileStringA("Steer", "BackClearance", "150", value, sizeof(value), ini);
	g_backClearance = strtof(value, NULL);
	if (!(g_backClearance >= 80.0f && g_backClearance <= 500.0f))
		g_backClearance = 150.0f;
	GetPrivateProfileStringA("Steer", "BackSink", "0", value, sizeof(value), ini);
	g_backSink = strtof(value, NULL);
	if (!(g_backSink >= -5.0f && g_backSink <= 5.0f))
		g_backSink = 0.0f;
	g_backSupportCheck = (int)GetPrivateProfileIntA("Steer", "BackSupportCheck", 0, ini);
	g_throttleOn = (int)GetPrivateProfileIntA("Steer", "Throttle", 1, ini);
	GetPrivateProfileStringA("Steer", "Accel", "3.0", value, sizeof(value), ini);
	g_accel = strtof(value, NULL);
	if (!(g_accel >= 0.0f && g_accel <= 10.0f))
		g_accel = 3.0f;
	GetPrivateProfileStringA("Steer", "Coast", "2.0", value, sizeof(value), ini);
	g_coast = strtof(value, NULL);
	if (!(g_coast >= 0.0f && g_coast <= 10.0f))
		g_coast = 2.0f;
	GetPrivateProfileStringA("Steer", "Brake", "0.4", value, sizeof(value), ini);
	g_brake = strtof(value, NULL);
	if (!(g_brake >= 0.0f && g_brake <= 5.0f))
		g_brake = 0.4f;
	GetPrivateProfileStringA("Steer", "Lead", "0.2", value, sizeof(value), ini);
	g_lead = strtof(value, NULL);
	if (!(g_lead >= 0.0f && g_lead <= 1.0f))
		g_lead = 0.2f;
	GetPrivateProfileStringA("Steer", "BackBelow", "30", value, sizeof(value), ini);
	g_backBelow = strtof(value, NULL);
	if (!(g_backBelow >= 0.0f && g_backBelow <= 1000.0f))
		g_backBelow = 30.0f;
	GetPrivateProfileStringA("Tilt", "Shapes", "CMB_BikeWorn", g_shapePrefix, sizeof(g_shapePrefix), ini);
	GetPrivateProfileStringA("Tilt", "Layout", "auto", value, sizeof(value), ini);
	g_layoutSetting = _stricmp(value, "file") == 0 ? LAYOUT_FILE : _stricmp(value, "transposed") == 0 ? LAYOUT_TRANSPOSED : LAYOUT_UNKNOWN;
	Log("settings: %s", ini);
	Log("  slope: Target=%s SlopeOffset=0x%X%s SlopeUnit=%s ExpectedDegrees=%g  Probe=%d IntervalMs=%lu DumpPointers=%d",
	    g_target == TARGET_PROXY ? "proxy" : "controller", g_slopeOffset, g_slopeOffset ? "" : " (unknown: reading only)",
	    g_unit == UNIT_RADIANS ? "radians" : g_unit == UNIT_DEGREES ? "degrees" : "cosine", g_expectedDegrees,
	    g_probe, (unsigned long)g_interval, g_dumpPointerCount);
	Log("  camera: Setting=%s ZoomOut=%d ZoomTargetOffset=0x%X ZoomCurrentOffset=0x%X", g_cameraSettingName, g_zoomOut,
	    g_zoomTargetOffset, g_zoomCurrentOffset);
	Log("  tilt: NormalOffset=0x%X StateOffset=0x%X Smoothing=%g MedianTime=%g MaxRate=%g MaxRoll=%g PivotHeight=%g PivotForward=%g Rider=%d Trace=%d Shapes=%s Layout=%s",
	    g_normalOffset, g_stateOffset, g_smoothing, g_medianTime, g_maxRate, g_maxRoll, g_pivotHeight, g_pivotForward, g_riderTilt, g_trace, g_shapePrefix,
	    g_layoutSetting == LAYOUT_FILE ? "file" : g_layoutSetting == LAYOUT_TRANSPOSED ? "transposed" : "auto");
	static const char *const pushValueNames[] = { "delta", "ray", "mod", "velocity", "position", "off" };
	Log("  steer: Enabled=%d FullSpeed=%g InputHook=%d Creep=%d CreepInput=%g CreepBelow=%g CreepRadius=%g Reverse=%d BackSpeed=%g "
	    "BackPush=%s BackClearance=%g BackSink=%g BackSupportCheck=%d Throttle=%d Accel=%g Coast=%g Brake=%g Lead=%g BackBelow=%g",
	    g_steer, g_fullSpeed, g_inputHook, g_creep, g_creepStart, g_creepBelow, g_creepRadius, g_reverse, g_backSpeed,
	    g_backPushAuto ? "auto" : pushValueNames[g_backPushFirst], g_backClearance, g_backSink, g_backSupportCheck,
	    g_throttleOn, g_accel, g_coast, g_brake, g_lead, g_backBelow);
	ReadBackSettings(ini, true);
	ReadRamSettings(ini, true);
	ReadRiderSwitches(true);
	ReadParts(ini);
	ReadLampSettings(ini);
}

static bool ReadVec(const char *file, const char *key, float out[3])
{
	char value[128];
	GetPrivateProfileStringA("Parts", key, "", value, sizeof(value), file);
	return sscanf(value, "%f,%f,%f", &out[0], &out[1], &out[2]) == 3 && isfinite(out[0]) && isfinite(out[1]) && isfinite(out[2]);
}

static float ReadNum(const char *file, const char *key, float fallback)
{
	char value[64];
	GetPrivateProfileStringA("Parts", key, "", value, sizeof(value), file);
	float v = strtof(value, NULL);
	return value[0] && isfinite(v) ? v : fallback;
}

/* The moving parts: [Parts] File= names the file (relative to the DLL's folder; the default
 * is the meshes' folder), and the keys can also sit in this INI itself. */
static void ReadParts(const char *ini)
{
	char value[MAX_PATH];
	GetPrivateProfileStringA("Parts", "File", "..\\..\\Meshes\\CMB\\CMB_BikeParts.ini", value, sizeof(value), ini);
	if (value[0] && value[1] != ':' && value[0] != '\\') {
		snprintf(g_partsFile, sizeof(g_partsFile), "%s", ini);
		char *slash = strrchr(g_partsFile, '\\');
		snprintf(slash ? slash + 1 : g_partsFile, sizeof(g_partsFile) - (slash ? (size_t)(slash + 1 - g_partsFile) : 0), "%s", value);
	} else {
		snprintf(g_partsFile, sizeof(g_partsFile), "%s", value);
	}
	const char *file = GetFileAttributesA(g_partsFile) != INVALID_FILE_ATTRIBUTES ? g_partsFile : ini;
	g_partsOk = ReadVec(file, "FrontAxle", g_frontAxle) && ReadVec(file, "RearAxle", g_rearAxle) &&
	            ReadVec(file, "SteerPoint", g_steerPoint) && ReadVec(file, "SteerAxis", g_steerAxis);
	g_gripOk = ReadVec(file, "Grip", g_grip);
	g_wheelRadius = ReadNum(file, "WheelRadius", 0.0f);
	g_frontMinY = ReadNum(file, "FrontMinY", 0.0f);
	g_barAngle = ReadNum(file, "BarAngle", 0.0f);
	g_lampOk = ReadVec(file, "LampPoint", g_lampPoint);
	if (!ReadVec(file, "LampAxis", g_lampAxis) || !(fabsf(g_lampAxis[0]) + fabsf(g_lampAxis[1]) + fabsf(g_lampAxis[2]) > 0.5f)) {
		g_lampAxis[0] = 0.0f;
		g_lampAxis[1] = 1.0f;
		g_lampAxis[2] = 0.0f;
	}
	g_barFullAt = ReadNum(ini, "BarFullAt", 90.0f);
	g_barAtSpeed = ReadNum(ini, "BarAtSpeed", 0.6f);
	if (!(g_barAtSpeed >= 0.0f && g_barAtSpeed <= 1.0f))
		g_barAtSpeed = 0.6f;
	float len = sqrtf(g_steerAxis[0] * g_steerAxis[0] + g_steerAxis[1] * g_steerAxis[1] + g_steerAxis[2] * g_steerAxis[2]);
	if (!(len > 0.5f) || !(g_wheelRadius > 5.0f && g_wheelRadius < 100.0f))
		g_partsOk = false;
	if (!(g_barAngle >= 0.0f && g_barAngle <= 45.0f))
		g_barAngle = 0.0f;
	if (!(g_barFullAt >= 5.0f && g_barFullAt <= 720.0f))
		g_barFullAt = 45.0f;
	if (g_partsOk) {
		for (int i = 0; i < 3; i++)
			g_steerAxis[i] /= len;
		char grip[128];
		if (g_gripOk)
			snprintf(grip, sizeof(grip), "the +x grip's centre at (%.1f, %.1f, %.1f), the wrist roll's pivot (Grip; the left mirrored in x)", g_grip[0], g_grip[1], g_grip[2]);
		else
			snprintf(grip, sizeof(grip), "no Grip: the wrist rolls about the hand's node, as before test 38");
		Log("  parts (%s): wheels of radius %.1f on axles at y %.1f and %.1f, the bar assembly beyond y %.1f turning up to %g deg "
		    "about the axis through (%.1f, %.1f, %.1f) along (%.2f, %.2f, %.2f), fully over from %g deg/s of turning, %g of it at speed; %s",
		    file == ini ? "in the settings" : g_partsFile, g_wheelRadius, g_frontAxle[1], g_rearAxle[1], g_frontMinY, g_barAngle,
		    g_steerPoint[0], g_steerPoint[1], g_steerPoint[2], g_steerAxis[0], g_steerAxis[1], g_steerAxis[2], g_barFullAt, g_barAtSpeed, grip);
	} else {
		Log("  parts: none (%s not found or incomplete): nothing on the bike moves", g_partsFile);
	}
	if (g_lampOk)
		Log("  headlamp: the lens at (%.1f, %.1f, %.1f) in the bike's space, the beam along (%.2f, %.2f, %.2f)",
		    g_lampPoint[0], g_lampPoint[1], g_lampPoint[2], g_lampAxis[0], g_lampAxis[1], g_lampAxis[2]);
}

static void ReadLampSettings(const char *ini)
{
	char value[64];
	g_lampEnabled = (int)GetPrivateProfileIntA("Lamp", "Enabled", 1, ini) != 0;
	g_lampShadows = (int)GetPrivateProfileIntA("Lamp", "Shadows", 0, ini) != 0;
	GetPrivateProfileStringA("Lamp", "BeamAxis", "x", value, sizeof(value), ini);
	const char *v = value;
	g_lampBeamSign = 1;
	if (*v == '-') {
		g_lampBeamSign = -1;
		v++;
	} else if (*v == '+') {
		v++;
	}
	g_lampBeamAxis = (*v == 'y' || *v == 'Y') ? 1 : (*v == 'z' || *v == 'Z') ? 2 : 0;
	GetPrivateProfileStringA("Lamp", "Pitch", "0", value, sizeof(value), ini);
	g_lampPitch = (float)atof(value);
	if (!(g_lampPitch > -45.0f && g_lampPitch < 45.0f))
		g_lampPitch = 0.0f;
	g_lampAhead = IniFloat(ini, "Lamp", "Ahead", 28.0f, -100.0f, 200.0f);
	g_lampLead = IniFloat(ini, "Lamp", "Lead", 1.0f, 0.0f, 5.0f);
	g_lampHandoverFrames = (int)GetPrivateProfileIntA("Lamp", "HandoverFrames", 5, ini);
	if (g_lampHandoverFrames < 0 || g_lampHandoverFrames > 100)
		g_lampHandoverFrames = 5;
	GetPrivateProfileStringA("Lamp", "FlagsOffset", "0x108", value, sizeof(value), ini);
	g_lampFlagsOff = (uint32_t)strtoul(value, NULL, 0);
	if (g_lampFlagsOff < 0x30 || g_lampFlagsOff > 0x1F0 || (g_lampFlagsOff & 7))
		g_lampFlagsOff = OFF_AV_FLAGS;
	GetPrivateProfileStringA("Lamp", "Node", "CMB_Headlamp", g_lampNodeName[0], sizeof(g_lampNodeName[0]), ini);
	GetPrivateProfileStringA("Lamp", "ShadowNode", "CMB_HeadlampShadow", g_lampNodeName[1], sizeof(g_lampNodeName[1]), ini);
	Log("  headlamp: %s; the %s light's node ('%s'), the beam along the node's %c%c axis, pitched down %g deg; flags at +0x%X",
	    g_lampEnabled ? "on" : "off (Enabled=0)", g_lampShadows ? "shadow-casting" : "plain", g_lampNodeName[g_lampShadows ? 1 : 0],
	    g_lampBeamSign < 0 ? '-' : '+', "xyz"[g_lampBeamAxis], g_lampPitch, g_lampFlagsOff);
}

/* ------------------------------------------------------------------------- */
/* Safe memory access                                                        */
/* ------------------------------------------------------------------------- */

static bool Accessible(uintptr_t p, size_t n, bool write)
{
	if (p < 0x10000 || p > 0x7FFFFFFEFFFFull || n > 0x100000)
		return false;
	int stale = -1;   /* the first entry past its time: absent, and its slot the next query's */
	for (int i = 0; i < g_regionCount; i++) {
		const Region *r = &g_regions[i];
		if (g_regionTick - r->at >= 30000u + 1000u * (DWORD)(i % 30)) {
			if (stale < 0)
				stale = i;
			continue;
		}
		if (p >= r->start && p + n <= r->end && (r->writable || !write))
			return true;
	}
	MEMORY_BASIC_INFORMATION mbi;
	g_queries++;
	if (VirtualQuery((const void *)p, &mbi, sizeof(mbi)) != sizeof(mbi))
		return false;
	if (mbi.State != MEM_COMMIT || (mbi.Protect & (PAGE_GUARD | PAGE_NOACCESS)))
		return false;
	DWORD writable = PAGE_READWRITE | PAGE_EXECUTE_READWRITE;
	DWORD readable = PAGE_READONLY | PAGE_READWRITE | PAGE_WRITECOPY | PAGE_EXECUTE_READ |
	                 PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY;
	if (!(mbi.Protect & (write ? writable : readable)))
		return false;
	uintptr_t end = (uintptr_t)mbi.BaseAddress + mbi.RegionSize;
	Region *r = &g_regions[stale >= 0 ? stale : g_regionCount < REGIONS ? g_regionCount++ : (g_regionNext++ % REGIONS)];
	r->start = (uintptr_t)mbi.BaseAddress;
	r->end = end;
	r->writable = (mbi.Protect & writable) != 0;
	r->at = g_regionTick;
	return p + n <= end;
}

/* Test 26: one VirtualQuery costs about 100 us on the tester's PC (the kernel sizing a
 * region of a huge committed heap), so emptying the cache every frame cost 11 queries a
 * frame on the bike and 39 with the rider held (3.5 ms), and 45 a skin sync (4.5 ms every
 * 0.1 s). The cache is kept across frames: emptied on a load or a new game and when the
 * player's 3D changes (every entry's time starts afresh), and in case the game gave a region
 * back each entry is good for 30 s plus a stagger of its own (its index in seconds, modulo
 * 30), then treated as absent and read again when next asked for, so the re-validation is
 * spread over 30 s (test 27: a 5 s backstop's flush cost 2-6 ms a time; test 37: the 30 s
 * flush that replaced it re-walked the rider's 88 regions in the next sync, 12-16 ms at
 * once, a stutter every half minute). Everything the plugin touches lives in the game's
 * heaps, which it never unmaps. */
static void ForgetRegions(void)
{
	g_regionCount = 0;
	g_regionNext = 0;
	g_regionTick = GetTickCount();
}

static double Clock(void)
{
	LARGE_INTEGER now;
	QueryPerformanceCounter(&now);
	return g_qpcFrequency.QuadPart ? (double)now.QuadPart / (double)g_qpcFrequency.QuadPart : 0.0;
}

static void TimeAdd(Timing *t, double start)
{
	double d = Clock() - start;
	t->sum += d;
	if (d > t->max)
		t->max = d;
	t->n++;
}

static double TimeAvgUs(const Timing *t)
{
	return t->n ? t->sum / t->n * 1e6 : 0.0;
}

static bool InImage(uintptr_t p, size_t n)
{
	/* Written so that p + n can't overflow (p near 2^64 from a null minus 8). */
	return p >= g_base && p < g_imageEnd && n <= g_imageEnd - p;
}

static uintptr_t ReadPtr(uintptr_t p)
{
	if ((p & 7) || !Accessible(p, 8, false))
		return 0;
	return *(const uintptr_t *)p;
}

/* ------------------------------------------------------------------------- */
/* RTTI                                                                      */
/* ------------------------------------------------------------------------- */

typedef struct {
	uint32_t signature;   /* 1 on x64 */
	uint32_t offset;
	uint32_t cdOffset;
	int32_t typeDescriptor;
	int32_t classDescriptor;
	int32_t self;
} CompleteObjectLocator;

/* The object's complete object locator, if it's a polymorphic object of the game. */
static const CompleteObjectLocator *GetCOL(uintptr_t obj)
{
	uintptr_t vtbl = ReadPtr(obj);
	if (vtbl < 8 || (vtbl & 7) || !InImage(vtbl - 8, 8))
		return NULL;
	uintptr_t col = *(const uintptr_t *)(vtbl - 8);
	if (!InImage(col, sizeof(CompleteObjectLocator)) || (col & 3))
		return NULL;
	const CompleteObjectLocator *c = (const CompleteObjectLocator *)col;
	if (c->signature != 1 || g_base + (uintptr_t)c->self != col)
		return NULL;
	if (!InImage(g_base + c->typeDescriptor, 24) || !InImage(g_base + c->classDescriptor, 16))
		return NULL;
	return c;
}

static const char *TypeName(int32_t typeDescriptor)
{
	/* TypeDescriptor: vtable pointer, spare, then the mangled name. */
	return (const char *)(g_base + typeDescriptor + 16);
}

static const char *ObjectTypeName(uintptr_t obj)
{
	const CompleteObjectLocator *c = GetCOL(obj);
	return c ? TypeName(c->typeDescriptor) : NULL;
}

/* True if the object is of class `mangled` or derives from it. */
static bool IsA(uintptr_t obj, const char *mangled)
{
	const CompleteObjectLocator *c = GetCOL(obj);
	if (!c)
		return false;
	const uint32_t *hierarchy = (const uint32_t *)(g_base + c->classDescriptor);
	uint32_t count = hierarchy[2];
	uintptr_t array = g_base + hierarchy[3];
	if (count == 0 || count > 128 || !InImage(array, count * 4u))
		return false;
	size_t len = strlen(mangled) + 1;
	for (uint32_t i = 0; i < count; i++) {
		uintptr_t base = g_base + ((const uint32_t *)array)[i];
		if (!InImage(base, 4))
			continue;
		int32_t td = *(const int32_t *)base;
		if (InImage(g_base + td + 16, len) && memcmp(TypeName(td), mangled, len) == 0)
			return true;
	}
	return false;
}

/* ------------------------------------------------------------------------- */
/* The live global                                                           */
/* ------------------------------------------------------------------------- */

typedef uintptr_t (*LookupFormByID_t)(uint32_t formID);

/* Our plugin's runtime form ID prefix: FExxx for a light plugin, xx for a full one. */
static bool FindOurPlugin(uint32_t *prefix, uint32_t *shift)
{
	uintptr_t dh = ReadPtr(g_base + RVA_DATA_HANDLER);
	if (!dh)
		return false;
	for (int light = 1; light >= 0; light--) {
		uintptr_t arr = dh + (light ? OFF_DH_LIGHT_MODS : OFF_DH_LOADED_MODS);
		uintptr_t entries = ReadPtr(arr + OFF_ARRAY_ENTRIES);
		if (!entries || !Accessible(arr + OFF_ARRAY_COUNT, 4, false))
			continue;
		uint32_t count = *(const uint32_t *)(arr + OFF_ARRAY_COUNT);
		if (count > 4096)
			continue;
		for (uint32_t i = 0; i < count; i++) {
			uintptr_t mod = ReadPtr(entries + 8u * i);
			if (!mod || !Accessible(mod + OFF_MOD_NAME, MAX_PATH, false) || !Accessible(mod + OFF_MOD_INDEX, 4, false))
				continue;
			if (_stricmp((const char *)(mod + OFF_MOD_NAME), ESP_NAME) != 0)
				continue;
			if (light) {
				uint16_t index = *(const uint16_t *)(mod + OFF_MOD_LIGHT_INDEX);
				*prefix = 0xFE000000u | ((uint32_t)index << 12);
				*shift = 12;
			} else {
				*prefix = (uint32_t)*(const uint8_t *)(mod + OFF_MOD_INDEX) << 24;
				*shift = 24;
			}
			Log("%s is loaded as a %s plugin: form IDs %08X", ESP_NAME, light ? "light" : "full", *prefix);
			return true;
		}
	}
	return false;
}

static uintptr_t FindGlobal(uint32_t prefix, uint32_t shift, uint32_t localId, const char *editorId)
{
	uint32_t id = prefix | (shift == 12 ? (localId & 0xFFFu) : localId);
	uintptr_t form = ((LookupFormByID_t)(g_base + RVA_LOOKUP_FORM))(id);
	if (!form || !Accessible(form, 0x38, false) || *(const uint8_t *)(form + OFF_FORM_TYPE) != FORM_TYPE_GLOB) {
		Log("form %08X isn't a global (an older %s?): %s does nothing", id, ESP_NAME, editorId);
		return 0;
	}
	uintptr_t edid = ReadPtr(form + OFF_GLOBAL_EDITOR_ID);
	if (edid && Accessible(edid, strlen(editorId) + 1, false) && strcmp((const char *)edid, editorId) != 0) {
		Log("form %08X is the global '%.40s', not %s: it does nothing", id, (const char *)edid, editorId);
		return 0;
	}
	Log("found %s (%08X)", editorId, id);
	return form;
}

static void FindGlobals(void)
{
	uint32_t prefix, shift;
	if (!FindOurPlugin(&prefix, &shift)) {
		Log("%s not found in the load order: nothing to do", ESP_NAME);
		g_globalsMissingLogged = true;
		return;
	}
	g_ourPrefix = prefix;
	g_ourMask = shift == 12 ? 0xFFFFF000u : 0xFF000000u;
	g_slopeGlobal = FindGlobal(prefix, shift, SLOPE_GLOBAL_ID, SLOPE_GLOBAL_EDITOR_ID);
	g_cameraGlobal = FindGlobal(prefix, shift, CAMERA_GLOBAL_ID, CAMERA_GLOBAL_EDITOR_ID);
	g_tiltGlobal = FindGlobal(prefix, shift, TILT_GLOBAL_ID, TILT_GLOBAL_EDITOR_ID);
	static const char *ground[3] = { "CMB_GroundNormalX", "CMB_GroundNormalY", "CMB_GroundNormalZ" };
	for (int i = 0; i < 3; i++)
		g_groundGlobals[i] = FindGlobal(prefix, shift, GROUND_GLOBAL_ID + (uint32_t)i, ground[i]);
	if (!g_groundGlobals[0] || !g_groundGlobals[1] || !g_groundGlobals[2])
		g_groundGlobals[0] = g_groundGlobals[1] = g_groundGlobals[2] = 0;
	static const char *park[7] = { "CMB_ParkX", "CMB_ParkY", "CMB_ParkZ", "CMB_ParkAngle", "CMB_ParkUpX", "CMB_ParkUpY", "CMB_ParkUpZ" };
	bool all = true;
	for (int i = 0; i < 7; i++)
		all &= (g_parkGlobals[i] = FindGlobal(prefix, shift, PARK_GLOBAL_ID + (uint32_t)i, park[i])) != 0;
	if (!all)
		memset(g_parkGlobals, 0, sizeof(g_parkGlobals));
	g_trackSlopeGlobal = FindGlobal(prefix, shift, SLOPE_TRACK_GLOBAL_ID, "CMB_TrackSlope");
	g_turnRadiusGlobal = FindGlobal(prefix, shift, TURN_RADIUS_GLOBAL_ID, "CMB_TurnRadius");
	g_turnStandGlobal = FindGlobal(prefix, shift, TURN_STAND_GLOBAL_ID, "CMB_StandTurnRate");
	g_turnSlowGlobal = FindGlobal(prefix, shift, TURN_SLOW_GLOBAL_ID, "CMB_TurnRadiusSlow");
	g_headlampGlobal = FindGlobal(prefix, shift, HEADLAMP_GLOBAL_ID, "CMB_HeadlampLive");
	g_headlampRefGlobals[0] = FindGlobal(prefix, shift, HEADLAMP_REF_HI_ID, "CMB_HeadlampRefHi");
	g_headlampRefGlobals[1] = FindGlobal(prefix, shift, HEADLAMP_REF_LO_ID, "CMB_HeadlampRefLo");
	static const char *ram[RAM_GLOBALS] = { "CMB_RamSeenHi", "CMB_RamSeenLo", "CMB_RamSeen", "CMB_RamOk", "CMB_RamHitSpeed", "CMB_RamHit", "CMB_RamEnemies", "CMB_RamMinSpeed" };
	bool allRam = true;
	for (int i = 0; i < RAM_GLOBALS; i++)
		allRam &= (g_ramGlobals[i] = FindGlobal(prefix, shift, RAM_GLOBAL_ID + (uint32_t)i, ram[i])) != 0;
	if (!allRam) {
		memset(g_ramGlobals, 0, sizeof(g_ramGlobals));
		Log("rams: not all of CMB_RamSeenHi to CMB_RamMinSpeed are there (an older %s?): enemies aren't knocked over", ESP_NAME);
	}
	g_globalsMissingLogged = true;   /* found or not, don't look again */
}

static float GlobalValue(uintptr_t global)
{
	return global ? *(const float *)(global + OFF_GLOBAL_VALUE) : 0.0f;
}

static void SetGlobal(uintptr_t global, float value)
{
	if (global)
		*(float *)(global + OFF_GLOBAL_VALUE) = value;
}

/* ------------------------------------------------------------------------- */
/* Player -> character controller -> Havok proxy                             */
/* ------------------------------------------------------------------------- */

static uintptr_t ScanFor(uintptr_t obj, int size, const char *mangled, int *offOut)
{
	if (!obj)
		return 0;
	for (int off = 0; off + 8 <= size; off += 8) {
		uintptr_t p = ReadPtr(obj + off);
		if (p && IsA(p, mangled)) {
			*offOut = off;
			return p;
		}
	}
	return 0;
}

static uintptr_t Player(void)
{
	uintptr_t player = ReadPtr(g_base + RVA_PLAYER);
	return player && IsA(player, RTTI_PLAYER) ? player : 0;
}

static uintptr_t FindController(uintptr_t player, bool scan)
{
	uintptr_t process = ReadPtr(player + OFF_ACTOR_PROCESS);
	uintptr_t data = process ? ReadPtr(process + OFF_PROCESS_DATA) : 0;
	uintptr_t where[3] = { data, process, player };
	static const int sizes[3] = { 0x1000, 0x400, 0x1000 };
	static const char *names[3] = { "process data", "process", "player" };

	if (g_ctrlWhere >= 0 && where[g_ctrlWhere]) {
		uintptr_t c = ReadPtr(where[g_ctrlWhere] + g_ctrlOff);
		if (c && IsA(c, RTTI_CONTROLLER))
			return c;
	}
	if (!scan)
		return 0;
	for (int w = 0; w < 3; w++) {
		int off;
		uintptr_t c = ScanFor(where[w], sizes[w], RTTI_CONTROLLER, &off);
		if (c) {
			if (w != g_ctrlWhere || off != g_ctrlOff)
				Log("character controller %s at %s+0x%X", ObjectTypeName(c), names[w], off);
			g_ctrlWhere = w;
			g_ctrlOff = off;
			return c;
		}
	}
	return 0;
}

static uintptr_t FindProxy(uintptr_t ctrl, bool scan)
{
	if (g_proxyOff1 >= 0) {
		uintptr_t p = ReadPtr(ctrl + g_proxyOff1);
		if (p && g_proxyOff2 >= 0)
			p = ReadPtr(p + g_proxyOff2);
		if (p && IsA(p, RTTI_PROXY))
			return p;
	}
	if (!scan)
		return 0;
	int off;
	uintptr_t p = ScanFor(ctrl, 0x1000, RTTI_PROXY, &off);
	if (p) {
		g_proxyOff1 = off;
		g_proxyOff2 = -1;
		Log("Havok proxy %s at controller+0x%X", ObjectTypeName(p), off);
		return p;
	}
	/* One level down: controller -> some object -> proxy. */
	for (int o1 = 0; o1 + 8 <= 0x1000; o1 += 8) {
		uintptr_t q = ReadPtr(ctrl + o1);
		if (!q || !GetCOL(q))
			continue;
		p = ScanFor(q, 0x400, RTTI_PROXY, &off);
		if (p) {
			g_proxyOff1 = o1;
			g_proxyOff2 = off;
			Log("Havok proxy %s at (controller+0x%X: %s)+0x%X", ObjectTypeName(p), o1, ObjectTypeName(q), off);
			return p;
		}
	}
	return 0;
}

/* ------------------------------------------------------------------------- */
/* Probe: what the log needs for finding the slope limit                      */
/* ------------------------------------------------------------------------- */

static void DumpObject(const char *label, uintptr_t obj, int size)
{
	Log("--- %s %p (%s), first 0x%X bytes: floats that look like values, pointers to typed objects",
	    label, (void *)obj, ObjectTypeName(obj) ? ObjectTypeName(obj) : "?", size);
	for (int off = 0; off < size; off += 4) {
		if (!Accessible(obj + off, 4, false))
			break;
		if ((off & 7) == 0) {
			uintptr_t p = ReadPtr(obj + off);
			const char *name = p ? ObjectTypeName(p) : NULL;
			if (name) {
				Log("  +0x%03X  -> %s", off, name);
				off += 4;
				continue;
			}
		}
		float f = *(const float *)(obj + off);
		uint32_t bits = *(const uint32_t *)(obj + off);
		if (!isfinite(f) || f == 0.0f || fabsf(f) < 1e-5f || fabsf(f) > 1e6f)
			continue;
		if (f > 0.0f && f < 1.0f)
			Log("  +0x%03X  %.6f  (%08X)  = cos %.2f deg", off, f, bits, acosf(f) * 57.29578f);
		else
			Log("  +0x%03X  %.6f  (%08X)", off, f, bits);
	}
}

static bool NameHas(const char *name, const char *part)
{
	for (; *name; name++) {
		const char *a = name, *b = part;
		while (*a && *b && (*a | 0x20) == (*b | 0x20)) {
			a++;
			b++;
		}
		if (!*b)
			return true;
	}
	return false;
}

static void ProbeSettings(void)
{
	static const uint32_t lists[2] = { RVA_INI_SETTINGS, RVA_INI_PREF_SETTINGS };
	static const char *labels[2] = { "INI", "INI prefs" };
	int total = 0;
	for (int l = 0; l < 2; l++) {
		uintptr_t coll = ReadPtr(g_base + lists[l]);
		uintptr_t node = coll ? ReadPtr(coll + OFF_SETTINGS_LIST) : 0;
		for (int guard = 0; node && guard < 20000; guard++) {
			uintptr_t setting = ReadPtr(node);
			uintptr_t name = setting ? ReadPtr(setting + OFF_SETTING_NAME) : 0;
			if (name && Accessible(name, 2, false)) {
				const char *n = (const char *)name;
				total++;
				if (NameHas(n, "slope") || NameHas(n, "climb") || NameHas(n, "incline"))
					Log("%s setting %.80s = %g", labels[l], n,
					    n[0] == 'f' ? *(const float *)(setting + OFF_SETTING_DATA) : (double)*(const int32_t *)(setting + OFF_SETTING_DATA));
			}
			node = ReadPtr(node + 8);
		}
	}
	Log("looked through %d INI settings for slope/climb/incline", total);
}

/* Havok's reflection data names its classes' members; if the game kept it for the
 * character proxy, "maxSlope" is there with its offset (hkClassMember: name, class,
 * enum, type, subtype, cArraySize, flags, offset at +0x1E). */
/* The game's data sections (readable, not code), where strings and tables live. */
static int DataSections(uintptr_t starts[], uintptr_t ends[], int max)
{
	const IMAGE_DOS_HEADER *dos = (const IMAGE_DOS_HEADER *)g_base;
	const IMAGE_NT_HEADERS64 *nt = (const IMAGE_NT_HEADERS64 *)(g_base + dos->e_lfanew);
	const IMAGE_SECTION_HEADER *sec = IMAGE_FIRST_SECTION(nt);
	int n = 0;
	for (unsigned i = 0; i < nt->FileHeader.NumberOfSections && n < max; i++, sec++) {
		DWORD c = sec->Characteristics;
		if (!(c & IMAGE_SCN_MEM_READ) || (c & IMAGE_SCN_MEM_EXECUTE) || (c & IMAGE_SCN_MEM_DISCARDABLE))
			continue;
		uintptr_t start = g_base + sec->VirtualAddress;
		uintptr_t end = start + sec->Misc.VirtualSize;
		/* Whole section mapped and readable? Check page by page once. */
		bool ok = true;
		for (uintptr_t p = start; p < end && ok; p += 0x1000)
			ok = Accessible(p, 1, false);
		if (!ok)
			continue;
		starts[n] = start;
		ends[n] = end;
		n++;
	}
	return n;
}

static void ProbeReflection(void)
{
	static const char needle[] = "maxSlope";
	uintptr_t starts[16], ends[16];
	int sections = DataSections(starts, ends, 16);
	int found = 0;
	for (int s = 0; s < sections; s++)
	for (uintptr_t p = starts[s]; p + sizeof(needle) <= ends[s] && found < 8; p++) {
		if (*(const char *)p != 'm' || memcmp((const void *)p, needle, sizeof(needle) - 1) != 0)
			continue;
		found++;
		Log("string \"%.40s\" at +0x%llX", (const char *)p, (unsigned long long)(p - g_base));
		for (int t = 0; t < sections; t++)
		for (uintptr_t q = starts[t]; q + 0x28 <= ends[t]; q += 8) {
			if (*(const uintptr_t *)q != p)
				continue;
			const uint8_t *m = (const uint8_t *)q;
			Log("  referenced at +0x%llX: type %u subtype %u flags %04X offset 0x%X",
			    (unsigned long long)(q - g_base), m[0x18], m[0x19], *(const uint16_t *)(m + 0x1C), *(const uint16_t *)(m + 0x1E));
			char hex[3 * 0x28 + 1];
			for (int b = 0; b < 0x28; b++)
				sprintf(hex + 3 * b, "%02X ", m[b]);
			Log("    raw: %s", hex);
			/* The neighbouring members of the same class, if this is a member table. */
			for (int k = -12; k <= 12; k++) {
				uintptr_t e = q + (intptr_t)k * 0x28;
				if (k == 0 || e < starts[t] || e + 0x28 > ends[t])
					continue;
				uintptr_t n = *(const uintptr_t *)e;
				if (!InImage(n, 2) || !Accessible(n, 2, false))
					continue;
				const char *s = (const char *)n;
				int len = 0;
				while (len < 64 && n + len < g_imageEnd &&
				       ((s[len] >= 'a' && s[len] <= 'z') || (s[len] >= 'A' && s[len] <= 'Z') ||
				        (s[len] >= '0' && s[len] <= '9') || s[len] == '_'))
					len++;
				if (len < 2 || n + len >= g_imageEnd || s[len] != 0)
					continue;
				Log("    member %+d: %.40s  offset 0x%X", k, s, *(const uint16_t *)(e + 0x1E));
			}
		}
	}
	if (!found)
		Log("no \"maxSlope\" string in the game: no Havok reflection for it");
}

/* ------------------------------------------------------------------------- */
/* The work                                                                  */
/* ------------------------------------------------------------------------- */

/* ------------------------------------------------------------------------- */
/* Probe snapshots: the objects' bytes now, and what changed since last time   */
/* ------------------------------------------------------------------------- */

static void SnapAdd(const char *label, uintptr_t obj, int size)
{
	if (!obj || g_snapCount >= SNAP_OBJECTS)
		return;
	Snapshot *s = &g_snaps[g_snapCount++];
	strncpy(s->label, label, sizeof(s->label) - 1);
	s->label[sizeof(s->label) - 1] = 0;
	s->obj = obj;
	s->size = size > (int)sizeof(s->bytes) ? (int)sizeof(s->bytes) : size;
	for (int off = 0; off < s->size; off += 4)
		*(uint32_t *)(s->bytes + off) = Accessible(obj + off, 4, false) ? *(const uint32_t *)(obj + off) : 0;
}

/* The objects to watch: controller, proxy, and the controller's pointers in DumpPointers. */
static void SnapCollect(uintptr_t ctrl, uintptr_t proxy)
{
	g_snapCount = 0;
	SnapAdd("controller", ctrl, 0x600);
	SnapAdd("proxy", proxy, 0x600);
	for (int i = 0; i < g_dumpPointerCount; i++) {
		char label[48];
		snprintf(label, sizeof(label), "controller+0x%X", g_dumpPointers[i]);
		uintptr_t obj = ReadPtr(ctrl + g_dumpPointers[i]);
		if (obj)
			SnapAdd(label, obj, 0x200);
		else
			Log("%s is empty", label);
	}
}

static void LogValue(const char *prefix, int off, uint32_t bits)
{
	float f;
	memcpy(&f, &bits, 4);
	if (isfinite(f) && f > 0.0f && f < 1.0f)
		Log("%s+0x%03X  %.6f  (%08X)  = cos %.2f deg", prefix, off, f, bits, acosf(f) * 57.29578f);
	else if (isfinite(f) && fabsf(f) >= 1e-5f && fabsf(f) <= 1e6f)
		Log("%s+0x%03X  %.6f  (%08X)", prefix, off, f, bits);
	else
		Log("%s+0x%03X  %08X", prefix, off, bits);
}

/* Still the same objects as in the snapshot? (A load or cell change replaces them.) */
static bool SnapsMatch(uintptr_t ctrl, uintptr_t proxy)
{
	return g_snapCount >= 1 && g_snaps[0].obj == ctrl && (g_snapCount < 2 || !proxy || g_snaps[1].obj == proxy);
}

/* Takes a fresh look at every watched object and logs the 4-byte values that changed. */
static void SnapDiff(const char *when)
{
	Log("=== %s: what changed", when);
	for (int i = 0; i < g_snapCount; i++) {
		Snapshot *s = &g_snaps[i];
		int changed = 0;
		for (int off = 0; off < s->size; off += 4) {
			if (!Accessible(s->obj + off, 4, false))
				break;
			uint32_t now = *(const uint32_t *)(s->obj + off);
			uint32_t was = *(const uint32_t *)(s->bytes + off);
			if (now == was)
				continue;
			if (changed++ < 80) {
				char prefix[80];
				float wf;
				memcpy(&wf, &was, 4);
				snprintf(prefix, sizeof(prefix), "  %s (was %.6g) ", s->label, wf);
				LogValue(prefix, off, now);
			}
			*(uint32_t *)(s->bytes + off) = now;
		}
		Log("  %s: %d value(s) changed%s", s->label, changed, changed > 80 ? " (first 80 shown)" : "");
	}
}

/* ------------------------------------------------------------------------- */
/* Slope limit                                                               */
/* ------------------------------------------------------------------------- */

/* The stored value <-> degrees, and which of two values allows steeper slopes. */
static float ToDegrees(float v)
{
	return g_unit == UNIT_COSINE ? acosf(v) * 57.29578f : g_unit == UNIT_RADIANS ? v * 57.29578f : v;
}

static float FromDegrees(float degrees)
{
	return g_unit == UNIT_COSINE ? cosf(degrees / 57.29578f) : g_unit == UNIT_RADIANS ? degrees / 57.29578f : degrees;
}

static bool Plausible(float v)
{
	return g_unit == UNIT_COSINE ? (v > 0.0f && v < 1.0f) : g_unit == UNIT_RADIANS ? (v > 0.1f && v < 1.6f) : (v > 5.0f && v < 90.0f);
}

static bool AsExpected(float v)
{
	if (g_expectedDegrees <= 0.0f)
		return true;
	float tolerance = g_unit == UNIT_DEGREES ? 0.06f : 0.001f;
	return fabsf(v - FromDegrees(g_expectedDegrees)) <= tolerance;
}

static float Steeper(float a, float b)
{
	/* A smaller cosine, or a bigger angle, lets you climb more. */
	return g_unit == UNIT_COSINE ? (a < b ? a : b) : (a > b ? a : b);
}

static const char *TargetName(void)
{
	return g_target == TARGET_PROXY ? "proxy" : "controller";
}

/* The object holding the limit, re-found through the cached chain (and searched for
 * when `scan`). */
static uintptr_t FindChain(bool scan, uintptr_t *ctrlOut, uintptr_t *proxyOut)
{
	uintptr_t player = Player();
	uintptr_t ctrl = player ? FindController(player, scan) : 0;
	uintptr_t proxy = ctrl ? FindProxy(ctrl, scan) : 0;
	if (ctrlOut)
		*ctrlOut = ctrl;
	if (proxyOut)
		*proxyOut = proxy;
	if (!player)
		return 0;
	if (scan && !proxy) {
		g_nextScan = GetTickCount() + 3000;
		if (!ctrl && !g_ctrlMissingLogged) {
			g_ctrlMissingLogged = true;
			Log("no character controller found near the player (yet); trying every 3 s");
		} else if (ctrl && !g_proxyMissingLogged) {
			g_proxyMissingLogged = true;
			Log("controller found but no %s under it; what it points to:", RTTI_PROXY);
			DumpObject("character controller", ctrl, 0x600);
		}
	}
	return g_target == TARGET_PROXY ? proxy : ctrl;
}

/* The climb's boost value for this ride (test 40, finding 8): ClimbBoost in the slot's unit,
 * never less steep than the riding value; usable only if it is steeper than that. */
static void SetClimbValue(void)
{
	g_climbValue = Steeper(FromDegrees(g_climbBoost), g_writtenValue);
	g_climbValueOk = g_climb && g_climbValue != g_writtenValue;
}

/* One of ours in the slot: the riding value or the climb's boost (which a dismount or a load
 * during a boost leaves there; test 24 left 60 deg on foot that way). */
static bool OursInSlot(float v)
{
	return v == g_writtenValue || (g_climbValueOk && v == g_climbValue);
}

static void RestoreSlope(uintptr_t target)
{
	if (!g_applied) {
		/* Not ours since a load, but the climb's boost value still in the slot (a load during a
		 * boost into a save on foot): the game's own back. That value is ours alone, and the
		 * target is the one found now. */
		if (g_climbValueOk && target && g_slopeOffset && Plausible(g_originalValue)) {
			float *slot = (float *)(target + g_slopeOffset);
			if (Accessible((uintptr_t)slot, 4, true) && *slot == g_climbValue) {
				*slot = g_originalValue;
				Log("slope limit back to %.2f deg (the climb's boost, %.2f deg, was still there after a load)", ToDegrees(g_originalValue), ToDegrees(g_climbValue));
			}
		}
		return;
	}
	if (target && target == g_appliedTarget) {
		float *slot = (float *)(target + g_slopeOffset);
		if (Accessible((uintptr_t)slot, 4, true) && OursInSlot(*slot)) {
			*slot = g_originalValue;
			Log("slope limit back to %.2f deg (the game set it back %d time(s) during the ride)",
			    ToDegrees(g_originalValue), g_revertCount);
		}
	}
	g_applied = false;
	g_appliedTarget = 0;
}

/* Riding: write the limit (first time: check the value there first). */
static void ApplySlope(uintptr_t target, float degrees)
{
	if (!target || !g_slopeOffset)
		return;
	if (g_applied && target != g_appliedTarget) {
		/* A different object (load, cell change): it has the game's own limit. */
		g_applied = false;
		g_appliedTarget = 0;
	}
	float *slot = (float *)(target + g_slopeOffset);
	if (!Accessible((uintptr_t)slot, 4, true))
		return;
	if (!g_applied) {
		float current = *slot;
		if (g_writtenValue != 0.0f && OursInSlot(current) && Plausible(g_originalValue) && !AsExpected(current)) {
			/* Our own riding value, still there after a load (test 24: a save loaded on the bike
			 * kept 60 deg on foot for the rest of the session): ours again, put back at the dismount.
			 * The climb's boost likewise (a load during a boost): the riding value goes back. */
			bool boost = current != g_writtenValue;
			g_writtenValue = Steeper(FromDegrees(degrees), g_originalValue);
			SetClimbValue();
			g_applied = true;
			g_appliedTarget = target;
			g_revertCount = 0;
			Log("%s+0x%X holds our %s (%.2f deg) from before the load: taken as ours again, %.2f deg while riding, back to %.2f deg at the dismount",
			    TargetName(), g_slopeOffset, boost ? "climb boost's value" : "riding value", ToDegrees(current), ToDegrees(g_writtenValue), ToDegrees(g_originalValue));
			*slot = g_writtenValue;
			return;
		}
		if (!Plausible(current) || !AsExpected(current)) {
			if (!g_badValueLogged)
				Log("%s+0x%X holds %g (%.2f deg), not the expected %g deg: not touching it",
				    TargetName(), g_slopeOffset, current, Plausible(current) ? ToDegrees(current) : 0.0f, g_expectedDegrees);
			g_badValueLogged = true;
			return;
		}
		g_originalValue = current;
		g_writtenValue = Steeper(FromDegrees(degrees), current);   /* only ever steeper than the game's */
		SetClimbValue();
		g_applied = true;
		g_appliedTarget = target;
		g_revertCount = 0;
		Log("riding: slope limit at %s+0x%X %.2f -> %.2f deg", TargetName(), g_slopeOffset,
		    ToDegrees(current), ToDegrees(g_writtenValue));
		*slot = g_writtenValue;
	} else {
		/* The riding value, or the climb's boost while it's on (ClimbRays, earlier in the same
		 * frame); the game's setting it back is whatever is neither. */
		float want = g_climbOn && g_climbValueOk ? g_climbValue : g_writtenValue;
		if (*slot != want) {
			if (!OursInSlot(*slot) && g_revertCount++ == 0)
				Log("the game set the slope limit back to %.2f deg; setting it again every frame while riding",
				    ToDegrees(*slot));
			*slot = want;
		}
	}
}

/* ------------------------------------------------------------------------- */
/* Camera                                                                    */
/* ------------------------------------------------------------------------- */

static uintptr_t FindSetting(const char *wanted)
{
	static const uint32_t lists[2] = { RVA_INI_SETTINGS, RVA_INI_PREF_SETTINGS };
	for (int l = 0; l < 2; l++) {
		uintptr_t coll = ReadPtr(g_base + lists[l]);
		uintptr_t node = coll ? ReadPtr(coll + OFF_SETTINGS_LIST) : 0;
		for (int guard = 0; node && guard < 20000; guard++) {
			uintptr_t setting = ReadPtr(node);
			uintptr_t name = setting ? ReadPtr(setting + OFF_SETTING_NAME) : 0;
			if (name && Accessible(name, strlen(wanted) + 1, false) && _stricmp((const char *)name, wanted) == 0)
				return setting;
			node = ReadPtr(node + 8);
		}
	}
	return 0;
}

static void UpdateCamera(void)
{
	float distance = GlobalValue(g_cameraGlobal);
	if (!g_cameraSetting) {
		if (distance <= 0.0f)
			return;
		g_cameraSetting = FindSetting(g_cameraSettingName);
		if (!g_cameraSetting) {
			Log("camera: no %s setting in the game: leaving the camera alone", g_cameraSettingName);
			g_cameraGlobal = 0;
			return;
		}
	}
	float *value = (float *)(g_cameraSetting + OFF_SETTING_DATA);
	if (!Accessible((uintptr_t)value, 4, true))
		return;
	if (distance > 0.0f) {
		if (!g_cameraApplied) {
			g_cameraOriginal = *value;
			g_cameraWritten = distance > g_cameraOriginal ? distance : g_cameraOriginal;   /* only ever farther */
			g_cameraApplied = true;
			Log("camera: %s %g -> %g while riding", g_cameraSettingName, g_cameraOriginal, g_cameraWritten);
		}
		if (*value != g_cameraWritten)
			*value = g_cameraWritten;
	} else if (g_cameraApplied) {
		if (*value == g_cameraWritten)
			*value = g_cameraOriginal;
		g_cameraApplied = false;
		Log("camera: %s back to %g", g_cameraSettingName, g_cameraOriginal);
	}
}

/* ------------------------------------------------------------------------- */
/* Ground under the player                                                   */
/* ------------------------------------------------------------------------- */

/* The controller's support normal (straight up on flat ground), and whether Havok has
 * the character jumping or in the air. False if there's nothing believable there. */
static bool ReadGround(uintptr_t ctrl, float n[3], bool *airborne)
{
	*airborne = false;
	if (!ctrl || !g_normalOffset || !Accessible(ctrl + g_normalOffset, 12, false))
		return false;
	const float *v = (const float *)(ctrl + g_normalOffset);
	float len = sqrtf(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
	if (!isfinite(len) || fabsf(len - 1.0f) > 0.02f || v[2] / len < 0.17f)   /* steeper than 80 deg: a wall */
		return false;
	for (int i = 0; i < 3; i++)
		n[i] = v[i] / len;

	/* The state is an int in Havok's character context, whose state manager pointer
	 * sits just before it: only read it if that pointer is what it should be. */
	if (g_stateOffset >= 8 && ctrl != g_stateCtrl) {
		g_stateCtrl = ctrl;
		bool trusted = Accessible(ctrl + g_stateOffset, 4, false) && IsA(ReadPtr(ctrl + g_stateOffset - 8), RTTI_STATES);
		if (trusted != g_stateTrusted || g_lastState == -1)
			Log(trusted ? "ground: character state at controller+0x%X (state manager just before it)"
			            : "ground: no state manager at controller+0x%X - 8: not reading the character state", g_stateOffset);
		g_stateTrusted = trusted;
		g_lastState = -2;
	}
	if (g_stateTrusted && g_stateOffset) {
		int32_t state = *(const int32_t *)(ctrl + g_stateOffset);
		if (state != g_lastState && g_skinCount && g_stateLogs < 40) {
			g_stateLogs++;
			static const char *names[] = { "on the ground", "jumping", "in the air", "climbing", "flying", "swimming", "floating" };
			Log("ground: character state %d (%s)", (int)state, state >= 0 && state <= 6 ? names[state] : "?");
		}
		g_lastState = state;
		*airborne = state != 0 && state != 3;   /* climbing is on something */
	}
	return true;
}

/* ------------------------------------------------------------------------- */
/* Tilt: the worn bike's skin                                                */
/* ------------------------------------------------------------------------- */

/* The text of a BSFixedString (StringCache::Entry *), or NULL. */
static const char *EntryString(uintptr_t entry)
{
	for (int guard = 0; entry && guard < 4; guard++) {
		if (!Accessible(entry, OFF_STRING_DATA + 1, false))
			return NULL;
		uint32_t state = *(const uint32_t *)(entry + OFF_STRING_STATE);
		if (!(state & STRING_EXTERNAL))
			return (state & STRING_WIDE) ? NULL : (const char *)(entry + OFF_STRING_DATA);
		entry = ReadPtr(entry + OFF_STRING_EXTERN);
	}
	return NULL;
}

static const char *ObjectName(uintptr_t obj)
{
	const char *name = EntryString(ReadPtr(obj + OFF_OBJECT_NAME));
	return name && Accessible((uintptr_t)name, 48, false) ? name : NULL;
}

/* The bike hanging off COM: its skin-to-bone rotation is [[0,0,1],[0,1,0],[-1,0,0]] in
 * the nif (the inverse of COM's seated bind, CMB_RiderSeat.json), so it shows whether the
 * game keeps a matrix the nif's way round (x' = R x) or transposed. Other skins: unknown. */
static int LayoutFromSkin(const uint8_t *bone)
{
	const float *r = (const float *)(bone + OFF_BONE_ROT);   /* r[row * 4 + column] */
	if (fabsf(r[5] - 1.0f) > 0.01f || fabsf(r[0]) > 0.01f || fabsf(r[10]) > 0.01f ||
	    fabsf(fabsf(r[2]) - 1.0f) > 0.01f || fabsf(r[8] + r[2]) > 0.02f)
		return LAYOUT_UNKNOWN;
	return r[2] > 0.0f ? LAYOUT_FILE : LAYOUT_TRANSPOSED;
}

/* The player's 3D root is turned by their heading h only, and an actor faces +Y: so its
 * rotation takes +Y to (sin h, cos h, 0). Which index that's in says which way round. */
static int LayoutFromRoot(uintptr_t player)
{
	uintptr_t loaded = ReadPtr(player + OFF_REFR_LOADED);
	uintptr_t root = loaded ? ReadPtr(loaded + OFF_LOADED_ROOT) : 0;
	if (!root || !IsA(root, RTTI_NODE) || !Accessible(root + OFF_WORLD_ROT, 0x30, false) ||
	    !Accessible(player + OFF_REFR_HEADING, 4, false))
		return LAYOUT_UNKNOWN;
	float h = *(const float *)(player + OFF_REFR_HEADING);
	const float *w = (const float *)(root + OFF_WORLD_ROT);
	float s = sinf(h), c = cosf(h);
	if (!isfinite(h) || fabsf(s) < 0.3f || fabsf(w[10] - 1.0f) > 0.05f || fabsf(w[0] - c) > 0.1f || fabsf(w[5] - c) > 0.1f)
		return LAYOUT_UNKNOWN;   /* a heading that doesn't tell, or not upright */
	if (fabsf(w[1] - s) < 0.1f && fabsf(w[4] + s) < 0.1f)
		return LAYOUT_FILE;      /* column 1 = (w[1], w[5], w[9]) is the forward direction */
	if (fabsf(w[1] + s) < 0.1f && fabsf(w[4] - s) < 0.1f)
		return LAYOUT_TRANSPOSED;
	return LAYOUT_UNKNOWN;
}

static const char *LayoutName(int layout)
{
	return layout == LAYOUT_FILE ? "as in the nif (x' = R x)" : layout == LAYOUT_TRANSPOSED ? "transposed (x' = x R)" : "unknown";
}

static void DecideLayout(void)
{
	int layout = g_layoutSetting;
	if (layout == LAYOUT_UNKNOWN) {
		if (g_layoutFromSkin != LAYOUT_UNKNOWN && g_layoutFromRoot != LAYOUT_UNKNOWN && g_layoutFromSkin != g_layoutFromRoot)
			layout = LAYOUT_DISAGREE;
		else
			layout = g_layoutFromSkin != LAYOUT_UNKNOWN ? g_layoutFromSkin : g_layoutFromRoot;
	}
	if (layout == g_layout)
		return;
	g_layout = layout;
	if (layout == LAYOUT_DISAGREE)
		Log("tilt: the bike's skin says the game's matrices are %s, the player's 3D says %s: not tilting"
		    " (Layout=file or Layout=transposed in CMB_Slope.ini overrides)", LayoutName(g_layoutFromSkin), LayoutName(g_layoutFromRoot));
	else if (layout != LAYOUT_UNKNOWN)
		Log("tilt: the game's rotation matrices are %s (%s)", LayoutName(layout),
		    g_layoutSetting != LAYOUT_UNKNOWN ? "CMB_Slope.ini" : g_layoutFromSkin != LAYOUT_UNKNOWN && g_layoutFromRoot != LAYOUT_UNKNOWN
		    ? "the bike's skin and the player's 3D agree" : g_layoutFromSkin != LAYOUT_UNKNOWN ? "from the bike's skin" : "from the player's 3D");
}

static void Release(uintptr_t obj)
{
	if (InterlockedDecrement((volatile LONG *)(obj + OFF_REFCOUNT)) == 0) {
		void **vtbl = *(void ***)obj;
		((void (*)(uintptr_t))vtbl[1])(obj);   /* NiRefObject::DeleteThis */
	}
}

static void RestoreSkin(const HeldSkin *h)
{
	for (int b = 0; b < h->count; b++) {
		uint8_t *live = (uint8_t *)(h->bones + (uintptr_t)b * BONE_SIZE);
		memcpy(live + OFF_BONE_RADIUS, h->original[b] + OFF_BONE_RADIUS, 4);
		memcpy(live + OFF_BONE_ROT, h->original[b] + OFF_BONE_ROT, 0x30);
		memcpy(live + OFF_BONE_POS, h->original[b] + OFF_BONE_POS, 12);
	}
}

/* Does this look like a skin's bone entry: a bounding sphere and a rigid transform? */
static bool LooksLikeBone(const uint8_t *bone)
{
	const float *r = (const float *)(bone + OFF_BONE_ROT), *pos = (const float *)(bone + OFF_BONE_POS);
	float radius = *(const float *)(bone + OFF_BONE_RADIUS);
	if (!(radius > 0.0f && radius < 10000.0f))
		return false;
	for (int i = 0; i < 3; i++) {
		if (!(fabsf(pos[i]) < 10000.0f))
			return false;
		for (int j = 0; j < 3; j++) {
			float d = r[i * 4] * r[j * 4] + r[i * 4 + 1] * r[j * 4 + 1] + r[i * 4 + 2] * r[j * 4 + 2];
			if (!(fabsf(d - (i == j ? 1.0f : 0.0f)) < 0.01f))
				return false;
		}
	}
	return true;
}

/* The skin instance's bone nodes, one per bone entry (BSSkin::Instance::bones), where they're
 * expected and, failing that, in the instance's other array; 0 if neither holds NiAVObjects. */
static uintptr_t SkinBoneNodes(uintptr_t skin, uint32_t count)
{
	static const uintptr_t candidates[2] = { OFF_SKIN_BONES, 0x10 };
	for (int k = 0; k < 2; k++) {
		uintptr_t array = skin + candidates[k];
		if (!skin || !Accessible(array, 0x18, false))
			continue;
		uintptr_t entries = ReadPtr(array + OFF_ARRAY_ENTRIES);
		uint32_t n = *(const uint32_t *)(array + OFF_ARRAY_COUNT);
		if (!entries || n != count || !Accessible(entries, (size_t)count * 8, false))
			continue;
		bool ok = true;
		for (uint32_t b = 0; b < count && ok; b++) {
			uintptr_t node = ((const uintptr_t *)entries)[b];
			ok = !node || IsA(node, RTTI_AVOBJECT);
		}
		if (ok)
			return entries;
	}
	return 0;
}

/* The skin instance's other array: a pointer to each bone's world transform (F4SE's
 * BSSkin::Instance::worldTransforms, "pointers to the corresponding bone's"), which the engine
 * keeps for every bone, node or not: test 34's finger bones (34 of the hands' 36) had no node
 * and were left where the animation had them while the palm went to the grip, the skin
 * between them a spike. The entries must read as transforms; 0 if the array isn't one. */
static uintptr_t SkinBoneTransforms(uintptr_t skin, uint32_t count, uintptr_t nodes)
{
	static const uintptr_t candidates[2] = { OFF_SKIN_BONES, 0x10 };
	for (int k = 0; k < 2; k++) {
		uintptr_t array = skin + candidates[k];
		if (!skin || !Accessible(array, 0x18, false))
			continue;
		uintptr_t entries = ReadPtr(array + OFF_ARRAY_ENTRIES);
		uint32_t n = *(const uint32_t *)(array + OFF_ARRAY_COUNT);
		if (!entries || entries == nodes || n != count || !Accessible(entries, (size_t)count * 8, false))
			continue;
		/* Every entry null or a readable, finite transform (a bone the clips never drive may sit
		 * with a zero scale: it is skipped on its own at the hold, not the whole array), and at
		 * least one that reads as a proper transform. */
		bool ok = true;
		int proper = 0;
		for (uint32_t b = 0; b < count && ok; b++) {
			uintptr_t xf = ((const uintptr_t *)entries)[b];
			float N[9], pos[3], sc;
			if (!xf)
				continue;
			if (!Accessible(xf, 0x40, false)) {
				ok = false;
				break;
			}
			memcpy(pos, (const void *)(xf + (OFF_WORLD_POS - OFF_WORLD_ROT)), 12);
			ok = isfinite(pos[0]) && isfinite(pos[1]) && isfinite(pos[2]) && fabsf(pos[0]) < 1e7f && fabsf(pos[1]) < 1e7f && fabsf(pos[2]) < 1e7f;
			if (ok && TransformWorld(xf, N, pos, &sc, NULL))
				proper++;
		}
		if (ok && proper)
			return entries;
	}
	return 0;
}

static void Refuse(uintptr_t data)
{
	g_refused[g_refusedCount++ % 8] = data;
}

static bool Refused(uintptr_t data)
{
	for (int i = 0; i < 8; i++)
		if (g_refused[i] == data)
			return true;
	return false;
}

static void HoldSkin(uintptr_t data, uintptr_t skin, const char *name)
{
	uintptr_t array = data + OFF_BONE_TRANSFORMS;
	uintptr_t bones = ReadPtr(array + OFF_ARRAY_ENTRIES);
	if (!bones || !Accessible(array + OFF_ARRAY_COUNT, 4, false)) {
		/* Silent till test 41: a skin caught with its bone data half built stays refused till
		 * the next load (finding 2 of test 40), or till the look 2.5 s into a ride a load
		 * started. Once per bone data: Refused() stops the repeat. */
		Log("tilt: %s's skin has no bone transforms to read yet (count/entries unreadable): not touching it%s", name, AfterLoadNote());
		g_skinsUnbuilt++;
		g_skinsRefused++;
		Refuse(data);
		return;
	}
	uint32_t count = *(const uint32_t *)(array + OFF_ARRAY_COUNT);
	if (count == 0 || count > MAX_BONES || !Accessible(bones, count * BONE_SIZE, true)) {
		Log("tilt: %s has %u bones: not touching it%s", name, count, AfterLoadNote());
		g_skinsRefused++;
		Refuse(data);
		return;
	}
	for (uint32_t b = 0; b < count; b++)
		if (!LooksLikeBone((const uint8_t *)(bones + b * BONE_SIZE))) {
			Log("tilt: %s's skin data doesn't look like bone transforms: not touching it%s", name, AfterLoadNote());
			g_skinsRefused++;
			Refuse(data);
			return;
		}
	HeldSkin *h = &g_skins[g_skinCount++];
	InterlockedIncrement((volatile LONG *)(data + OFF_REFCOUNT));
	h->boneData = data;
	h->bones = bones;
	h->count = (int)count;
	h->role = ROLE_UNKNOWN;
	h->skin = skin;
	h->node = 0;
	uintptr_t nodes = SkinBoneNodes(skin, count);
	if (nodes) {
		float N[9], n[3], sc;
		uintptr_t node = ReadPtr(nodes);
		if (node && NodeWorldChecked(node, N, n, &sc, NULL))
			h->node = node;
	}
	memcpy(h->original, (const void *)bones, count * BONE_SIZE);
	snprintf(h->name, sizeof(h->name), "%s", name);
	int layout = LayoutFromSkin(h->original[0]);
	Log("tilt: holding the skin of %s (%u bone(s)); its bind says the game's matrices are %s", h->name, count, LayoutName(layout));
	if (layout != LAYOUT_UNKNOWN)
		g_layoutFromSkin = layout;
}

static void LetGo(int i, const char *why)
{
	HeldSkin *h = &g_skins[i];
	RestoreSkin(h);
	Release(h->boneData);
	Log("tilt: %s back level and let go (%s; most tilt this ride %.1f deg)", h->name, why, g_tiltMax);
	g_skins[i] = g_skins[--g_skinCount];
}

/* A new ride (or none): the filter starts from level. */
/* The upper body's lean solved afresh: at a ride's start, after a load or a new game, and
 * whenever the whole rider is let go and held again (test 37: a 0 lean solved with the Pip-Boy
 * up stuck for five minutes, through a fast travel, until a knock-off). */
static void ResetTorsoSolve(void)
{
	g_torsoNoChain = false;
	g_torsoLeanSet = g_torsoFinal = false;
	g_torsoLean = 0.0f;
	g_torsoTries = 0;
	g_torsoSolvedAt = -100.0f;
	g_torsoRetryAt = 0.0f;
	g_torsoWaitSince = -1.0f;
	g_torsoWaitLogged = g_torsoAsItComes = false;
	g_torsoLastR0 = -1.0f;
	g_torsoSeqAt = g_torsoSeqFrom = (float)g_clock;
	g_torsoBestR0 = -1.0f;
	g_torsoKept = false;
	g_torsoSeqWhat = "the ride's start";
	g_torsoRearmWhy[0] = 0;
	g_armMoveOk = false;
	memset(g_armMoveLastOk, 0, sizeof(g_armMoveLastOk));
	g_jumpAt = -100.0f;
}

/* The lean solved again without being let go of meanwhile: after a jump of the player (a
 * door, a fast travel, a teleport; why says which, with the jump's size, for the next solve's
 * line). Test 38: a fast travel on the bike (10:49:47 to 51) left all 60 shapes held and sent
 * no PostLoadGame, so the lean of the ride's start, solved through a Pip-Boy held open over
 * 20 s (the grips at 82%, the lean 0, final), stood for the whole ride after it. The lean
 * stays as it is till the new solve; the wait and the "as it comes" start over, and so does
 * the run of readings whose best is kept (test 39: the first reading at 95% after a fast travel
 * was taken as final, 11.1 and 11.4 deg against the riding pose's 14.6); the arm-move memory
 * starts over too (the joints jumped with the player).
 * Test 39 again: the grips read the riding pose's 100% only with the bike stopped (96 to 98%
 * riding), and both fast travels arrived moving (194 to 212 after 01:36:52, 860 to 900 after
 * 01:37:53), the grips at 92 to 95%, so a run started empty still ended final on a moving
 * reading, about 95% (11 to 12 deg against the ride start's 14.6). The jump doesn't change the
 * rider; the solve again is for a lean solved from a short pose (test 38's Pip-Boy start at
 * 82%). So a solve this run kept from a good reading (95% or more, not taken as it comes)
 * stays the run's best: a reading has to beat it by the usual half percent, or be one of the
 * riding pose (99% or more, which replaces it as ever, final on two that agree), and 3 s on,
 * counted as ever, it is final as it stands. One that was short (taken as it comes) is not
 * kept: the run starts empty. */
static void RearmTorsoSolve(const char *why)
{
	g_jumpAt = (float)g_clock;   /* the wrist's max leaves the second after it out, TorsoLean or not (test 39) */
	if (g_torsoLeanSetting >= 0.0f)
		return;   /* TorsoLean given: nothing is solved */
	bool keep = g_torsoLeanSet && !g_torsoAsItComes && g_torsoBestR0 >= 0.95f;   /* the solve before the jump, from a good reading (test 40) */
	g_torsoFinal = false;
	g_torsoTries = 0;
	g_torsoRetryAt = (float)g_clock + 0.5f;
	g_torsoWaitSince = -1.0f;
	g_torsoWaitLogged = g_torsoAsItComes = false;
	g_torsoLastR0 = -1.0f;
	g_torsoSeqAt = g_torsoSeqFrom = (float)g_clock;   /* a fresh run of readings, the best of it kept (test 39) */
	if (!keep)
		g_torsoBestR0 = -1.0f;   /* ... from nothing; else from the solve before the jump, its reading the one to beat */
	g_torsoKept = keep;
	g_torsoSeqWhat = "the jump";
	g_armMoveOk = false;
	memset(g_armMoveLastOk, 0, sizeof(g_armMoveLastOk));
	snprintf(g_torsoRearmWhy, sizeof(g_torsoRearmWhy), "%s", g_torsoLeanSet ? why : "");   /* a first solve isn't "again" */
}

/* A hand of log lines (LogHand): full, as at a ride's start. */
static void LogHandFill(LogHand *h)
{
	h->lines = h->size > 0.0f ? h->size : LOG_HAND_SIZE;
	h->at = (float)g_clock;
}

/* One line from the hand, if there is one: the hand refills by one every LOG_HAND_EVERY
 * seconds since it was last looked at, up to LOG_HAND_SIZE. Asked only when the line would
 * be logged otherwise (its own one-a-second gap passed), so a line not logged costs nothing. */
static bool LogHandTake(LogHand *h)
{
	float now = (float)g_clock, size = h->size > 0.0f ? h->size : LOG_HAND_SIZE;
	if (now > h->at)
		h->lines += (now - h->at) / (h->every > 0.0f ? h->every : LOG_HAND_EVERY);
	h->at = now;
	if (h->lines > size)
		h->lines = size;
	if (h->lines < 1.0f)
		return false;
	h->lines -= 1.0f;
	return true;
}

static void ResetTilt(void)
{
	g_tiltSampleCount = 0;
	g_pitchSmooth = g_rollSmooth = g_pitchNow = g_rollNow = 0.0f;
	g_pitchVel = g_rollVel = g_liftNow = g_liftSmooth = g_bumpLift = 0.0f;
	g_liftVel = g_wheelOffset[0] = g_wheelOffset[1] = 0.0f;   /* the suspension at rest */
	g_wheelWordAt = -100.0f;   /* no word yet: a ride whose rays never answer eases its lift off at once */
	g_rideStartClock = (float)g_clock;
	ResetTorsoSolve();
	g_wristMax[0] = g_wristMax[1] = -1.0f;
	g_tiltMax = g_tiltNow = 0.0f;
	g_wheelAngle = g_barNow = g_headingRate = 0.0f;
	g_leanNow = g_yawForLean = 0.0f;
	g_faceEase = 1.0f;
	g_faceObstacleAt = -100.0f;   /* no obstacle in force: the rays start afresh */
	g_wallSeen = 0;
	g_faceKind = 0;
	g_faceNoneSince = -1.0f;
	g_wallLogs = 0;   /* WallAhead's lines are capped per ride */
	LogHandFill(&g_faceHand);   /* the face rays' lines from a full hand again (test 40) */
	g_faceSince = -1.0f;
	ClimbOff("the ride started afresh");   /* the climb's boost off, its state afresh */
	LogHandFill(&g_climbHand);
	g_climbCool = false;
	g_stepCount = g_stepsThisBoost = 0;   /* stage 2's steps afresh */
	g_stepCheck = false;
	g_stepAt = g_stepTriedAt = -100.0f;
	g_stallSince = -1.0f;
	g_climbRideLogged = false;
	g_climbRefusedWhy = -1;
	for (int i = 0; i < 2; i++) {
		LogHandFill(&g_wheelHand[i]);
		LogHandFill(&g_wheelThrownHand[i]);
	}
	g_haveLastHeading = false;
	g_wheelHistN = g_wheelHistAt = 0;
}

/* 3x3 row-major helpers for the moving parts. */
static void Mul3(const float *a, const float *b, float *out)   /* out = a b (out apart from a and b) */
{
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++)
			out[i * 3 + j] = a[i * 3] * b[j] + a[i * 3 + 1] * b[3 + j] + a[i * 3 + 2] * b[6 + j];
}

static void MulV(const float *a, const float *v, float *out)   /* out = a v (out apart from v) */
{
	for (int i = 0; i < 3; i++)
		out[i] = a[i * 3] * v[0] + a[i * 3 + 1] * v[1] + a[i * 3 + 2] * v[2];
}

/* The rotation by `radians` about the unit axis u (Rodrigues). */
static void AxisRotation(const float *u, float radians, float *R)
{
	float c = cosf(radians), sn = sinf(radians), k = 1.0f - c;
	R[0] = c + u[0] * u[0] * k;         R[1] = u[0] * u[1] * k - u[2] * sn; R[2] = u[0] * u[2] * k + u[1] * sn;
	R[3] = u[1] * u[0] * k + u[2] * sn; R[4] = c + u[1] * u[1] * k;         R[5] = u[1] * u[2] * k - u[0] * sn;
	R[6] = u[2] * u[0] * k - u[1] * sn; R[7] = u[2] * u[1] * k + u[0] * sn; R[8] = c + u[2] * u[2] * k;
}

/* Put the rotation by `radians` about the unit axis u through the point P in front of the
 * map x -> M x + t: x -> M' x + t'. */
static void Turn(float *M, float *t, const float *u, const float *P, float radians)
{
	float R[9], M2[9], t2[3], RP[3];
	AxisRotation(u, radians, R);
	Mul3(R, M, M2);
	MulV(R, t, t2);
	MulV(R, P, RP);
	memcpy(M, M2, sizeof(M2));
	for (int i = 0; i < 3; i++)
		t[i] = t2[i] + P[i] - RP[i];
}

static const char *RoleName(int role)
{
	return role == ROLE_WHEEL_F ? "the front wheel" : role == ROLE_WHEEL_R ? "the rear wheel" : role == ROLE_FRONT ? "the bar assembly"
	     : role == ROLE_GLOW ? "the headlamp's lit parts (with the bar assembly; a speck while the lamp is off)"
	     : role == ROLE_FORK ? "the lower fork (with the bars and the front wheel's travel)" : "a fixed part";
}

/* Which moving part a held skin is: by where its culling sphere's centre lands in the
 * bike's own space (A^T (c - t), the bind undone), or, for the fork's lower end, by its name
 * ("_fork": the mesh tool names the lower fork legs, the front mudguard and the caliper so;
 * test 37: at +10 of travel the tyre went into the mudguard and the axle left the fork ends,
 * so they go with the front wheel's travel, and with the bars; its sphere sits ahead of the
 * steering head like the bar assembly's, so the name comes first). Needs the layout, so it's
 * done on the first tilt frame. */
static void DetectRole(HeldSkin *h)
{
	const float *o = (const float *)(h->original[0] + OFF_BONE_ROT), *t = (const float *)(h->original[0] + OFF_BONE_POS);
	const float *c = (const float *)h->original[0];
	float radius = *(const float *)(h->original[0] + OFF_BONE_RADIUS);
	float A[9], d[3] = { c[0] - t[0], c[1] - t[1], c[2] - t[2] };
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++)
			A[i * 3 + j] = g_layout == LAYOUT_FILE ? o[i * 4 + j] : o[j * 4 + i];
	for (int i = 0; i < 3; i++)
		h->centre[i] = A[i] * d[0] + A[3 + i] * d[1] + A[6 + i] * d[2];
	h->role = ROLE_NONE;
	if (g_partsOk && h->count == 1 && NameHas(h->name, "_fork"))
		h->role = ROLE_FORK;
	if (h->role == ROLE_NONE && g_partsOk && h->count == 1 && radius < 1.6f * g_wheelRadius) {
		float fx = h->centre[0] - g_frontAxle[0], fy = h->centre[1] - g_frontAxle[1], fz = h->centre[2] - g_frontAxle[2];
		float rx = h->centre[0] - g_rearAxle[0], ry = h->centre[1] - g_rearAxle[1], rz = h->centre[2] - g_rearAxle[2];
		if (fx * fx + fy * fy + fz * fz < 36.0f)
			h->role = ROLE_WHEEL_F;
		else if (rx * rx + ry * ry + rz * rz < 36.0f)
			h->role = ROLE_WHEEL_R;
	}
	if (h->role == ROLE_NONE && g_partsOk && h->count == 1 && h->centre[1] > g_frontMinY)
		h->role = ROLE_FRONT;
	if (h->role == ROLE_FRONT && g_lampOk && radius < 12.0f) {
		float lx = h->centre[0] - g_lampPoint[0], ly = h->centre[1] - g_lampPoint[1], lz = h->centre[2] - g_lampPoint[2];
		if (lx * lx + ly * ly + lz * lz < 400.0f)
			h->role = ROLE_GLOW;   /* test 30: the lit ring and face shone with the lamp off */
	}
	Log("tilt: %s is %s (its culling sphere's centre (%.0f, %.0f, %.0f) in the bike's space, radius %.0f)", h->name,
	    RoleName(h->role), h->centre[0], h->centre[1], h->centre[2], radius);
}

static void LetGoAllRider(const char *why);
static void LetGoLamp(int i, const char *why);
static void LetGoAll(const char *why)
{
	while (g_skinCount)
		LetGo(g_skinCount - 1, why);
	LetGoAllRider(why);
	LetGoLamp(0, why);
	LetGoLamp(1, why);
	g_riderWorldChecked = false;
	g_riderWorldFailSince = -1.0f;
	g_riderBlocked = false;
	g_holdWaitSince = 0.0f;
	g_holdWaitExpired = false;
	ResetTilt();
}

/* --- Finding the worn bike's skin ------------------------------------------
 * Two routes: everything under the player's 3D root, and the biped's equipped parts
 * (what's worn in each slot, wherever its 3D hangs). A shape counts if its name starts
 * with Shapes=, or, whatever its name, if it's skinned to one bone with the COM bike's
 * bind. When a ride finds nothing for a second, the walk is logged once. */

typedef struct {
	uintptr_t found[MAX_SKINS];
	uintptr_t skins[MAX_SKINS];
	const char *names[MAX_SKINS];
	int count;
	bool byBind[MAX_SKINS];
	/* The rider's: every other skinned shape (with its instance and bone data) and the plain ones. */
	uintptr_t riderShape[MAX_RIDER], riderSkin[MAX_RIDER], riderData[MAX_RIDER];
	const char *riderName[MAX_RIDER];
	int riderCount, riderOver;
	uintptr_t lamp[2];                  /* the headlamp's add-on nodes, by name */
} SkinList;

#define WALK_LINES 48
typedef struct {
	bool verbose;
	int nodes, geometries, deepest, cutOff;
	struct { const char *type; int count; } types[24];
	int typeCount;
	char lines[WALK_LINES][176];
	int lineCount;
} WalkStats;
static WalkStats g_walk;
static bool g_walkOurs;   /* walking the 3D of one of our own armor addons */

static void WalkLine(const char *fmt, ...)
{
	if (!g_walk.verbose || g_walk.lineCount >= WALK_LINES)
		return;
	va_list args;
	va_start(args, fmt);
	vsnprintf(g_walk.lines[g_walk.lineCount++], sizeof(g_walk.lines[0]), fmt, args);
	va_end(args);
}

static void CountType(const char *type)
{
	if (!g_walk.verbose)
		return;
	if (!type)
		type = "(no type information)";
	for (int i = 0; i < g_walk.typeCount; i++)
		if (g_walk.types[i].type == type || strcmp(g_walk.types[i].type, type) == 0) {
			g_walk.types[i].count++;
			return;
		}
	if (g_walk.typeCount < 24) {
		g_walk.types[g_walk.typeCount].type = type;
		g_walk.types[g_walk.typeCount++].count = 1;
	}
}

static const char *OrNone(const char *s)
{
	return s ? s : "-";
}

/* The COM bike's bind, either way round: one bone, rotation [[0,0,1],[0,1,0],[-1,0,0]]
 * (or its transpose), translation about (-74.5, 0, 0), the seat height. */
static bool IsComBikeBind(const uint8_t *bone)
{
	const float *pos = (const float *)(bone + OFF_BONE_POS);
	return LayoutFromSkin(bone) != LAYOUT_UNKNOWN && pos[0] < -68.0f && pos[0] > -81.0f &&
	       fabsf(pos[1]) < 2.0f && fabsf(pos[2]) < 2.0f;
}

static void AddSkin(SkinList *list, uintptr_t data, uintptr_t skin, const char *name, bool byBind)
{
	for (int i = 0; i < list->count; i++)
		if (list->found[i] == data)
			return;
	if (list->count >= MAX_SKINS)
		return;
	list->names[list->count] = name ? name : "(unnamed shape)";
	list->byBind[list->count] = byBind;
	list->skins[list->count] = skin;
	list->found[list->count++] = data;
}

static void AddRider(SkinList *list, uintptr_t shape, uintptr_t skin, uintptr_t data, const char *name)
{
	for (int i = 0; i < list->riderCount; i++)
		if (list->riderShape[i] == shape)
			return;
	if (list->riderCount >= MAX_RIDER) {
		list->riderOver++;
		return;
	}
	list->riderName[list->riderCount] = name ? name : "(unnamed shape)";
	list->riderSkin[list->riderCount] = skin;
	list->riderData[list->riderCount] = data;
	list->riderShape[list->riderCount++] = shape;
}

static void InspectShape(uintptr_t shape, int depth, SkinList *list)
{
	g_walk.geometries++;
	const char *name = ObjectName(shape);
	uintptr_t skin = ReadPtr(shape + OFF_SKIN_INSTANCE);
	uintptr_t data = skin && IsA(skin, RTTI_SKIN) ? ReadPtr(skin + OFF_SKIN_BONE_DATA) : 0;
	bool isBoneData = data && IsA(data, RTTI_BONE_DATA);
	int bones = -1;
	const uint8_t *bone0 = NULL;
	if (isBoneData && Accessible(data + OFF_BONE_TRANSFORMS + OFF_ARRAY_COUNT, 4, false)) {
		uint32_t count = *(const uint32_t *)(data + OFF_BONE_TRANSFORMS + OFF_ARRAY_COUNT);
		uintptr_t entries = ReadPtr(data + OFF_BONE_TRANSFORMS + OFF_ARRAY_ENTRIES);
		bones = count <= 1000 ? (int)count : -2;
		if (entries && count >= 1 && count <= 1000 && Accessible(entries, BONE_SIZE, false))
			bone0 = (const uint8_t *)entries;
	}
	size_t n = strlen(g_shapePrefix);
	bool byName = name && n && _strnicmp(name, g_shapePrefix, n) == 0;
	/* A skin we hold is tilted, so its bind no longer looks like COM's: it's still the bike. */
	bool held = false;
	for (int i = 0; i < g_skinCount; i++)
		held |= g_skins[i].boneData == data;
	bool byBind = !byName && bones == 1 && bone0 && (held || IsComBikeBind(bone0));
	bool byAddon = !byName && !byBind && g_walkOurs && bones >= 1 && bones <= MAX_BONES;
	if ((byName || byBind || byAddon) && isBoneData && bones >= 1)
		AddSkin(list, data, skin, name, byBind || byAddon);
	else if (!(byName || byBind || byAddon) && !held && g_riderTilt) {
		if (skin && isBoneData && bones >= 1 && bones <= MAX_RIDER_BONES)
			AddRider(list, shape, skin, data, name);
		else if (!skin)
			AddRider(list, shape, 0, 0, name);
	}
	WalkLine("  shape (depth %d) '%.40s' %s | skin %s | bone data %s | %d bone(s)%s", depth, OrNone(name),
	         OrNone(ObjectTypeName(shape)), skin ? OrNone(ObjectTypeName(skin)) : "none",
	         data ? OrNone(ObjectTypeName(data)) : "none", bones,
	         byName ? "  <- the bike (name)" : byBind ? "  <- the bike (COM bind)" : byAddon ? "  <- the bike (our armor addon)" : "");
}

static void Visit(uintptr_t obj, int depth, SkinList *list)
{
	if (--g_walkBudget < 0 || depth > 48) {
		g_walk.cutOff++;
		return;
	}
	g_walk.nodes++;
	if (depth > g_walk.deepest)
		g_walk.deepest = depth;
	CountType(g_walk.verbose ? ObjectTypeName(obj) : NULL);
	if (IsA(obj, RTTI_GEOMETRY)) {
		InspectShape(obj, depth, list);
		return;
	}
	if (!IsA(obj, RTTI_NODE) || !Accessible(obj + OFF_CHILDREN, 0x10, false))
		return;
	if (g_lampEnabled) {
		const char *nm = ObjectName(obj);
		for (int i = 0; nm && i < 2; i++)
			if (!list->lamp[i] && g_lampNodeName[i][0] && strcmp(nm, g_lampNodeName[i]) == 0)
				list->lamp[i] = obj;
	}
	uintptr_t children = ReadPtr(obj + OFF_CHILDREN);
	unsigned used = *(const uint16_t *)(obj + OFF_CHILDREN_USED);
	unsigned cap = *(const uint16_t *)(obj + OFF_CHILDREN_CAP);
	if (depth <= 1)
		WalkLine("  node (depth %d) '%.40s' %s, %u child slot(s)", depth, OrNone(ObjectName(obj)), OrNone(ObjectTypeName(obj)), used);
	if (!children || used > cap || !Accessible(children, used * 8u, false))
		return;
	for (unsigned i = 0; i < used; i++) {
		uintptr_t child = ((const uintptr_t *)children)[i];
		if (child)
			Visit(child, depth + 1, list);
	}
}

static void WalkFrom(uintptr_t root, SkinList *list, bool verbose)
{
	memset(&g_walk, 0, sizeof(g_walk));
	g_walk.verbose = verbose;
	g_walkBudget = 6000;
	if (root)
		Visit(root, 0, list);
}

static void LogWalk(const char *what)
{
	Log("tilt: %s: %d object(s), %d shape(s), deepest %d%s", what, g_walk.nodes, g_walk.geometries, g_walk.deepest,
	    g_walk.cutOff ? " (stopped early: too deep or too many)" : "");
	char line[600];
	int len = 0;
	for (int i = 0; i < g_walk.typeCount && len < (int)sizeof(line) - 80; i++)
		len += snprintf(line + len, sizeof(line) - len, "%s %s x%d", i ? "," : "", g_walk.types[i].type, g_walk.types[i].count);
	if (g_walk.typeCount)
		Log("tilt:   types:%s", line);
	for (int i = 0; i < g_walk.lineCount; i++)
		Log("tilt: %s", g_walk.lines[i]);
}

/* The player's 3D root (third person). */
static uintptr_t Root3D(uintptr_t player)
{
	uintptr_t loaded = player ? ReadPtr(player + OFF_REFR_LOADED) : 0;
	uintptr_t root = loaded ? ReadPtr(loaded + OFF_LOADED_ROOT) : 0;
	return root && IsA(root, RTTI_NODE) ? root : 0;
}

/* The player's biped (BipedAnim has no type information; its root must be a node). */
static uintptr_t Biped(uintptr_t player)
{
	uintptr_t biped = player ? ReadPtr(player + OFF_ACTOR_BIPED) : 0;
	if (!biped || !Accessible(biped, OFF_BIPED_OBJECTS + BIPED_SLOTS * BIPED_OBJECT_SIZE, false))
		return 0;
	return biped;
}

static bool OurForm(uintptr_t form)
{
	return form && g_ourMask && Accessible(form + OFF_FORM_ID, 4, false) &&
	       (*(const uint32_t *)(form + OFF_FORM_ID) & g_ourMask) == g_ourPrefix;
}

static uintptr_t BipedPart(uintptr_t biped, int slot, uintptr_t *addon)
{
	uintptr_t object = biped + OFF_BIPED_OBJECTS + (uintptr_t)slot * BIPED_OBJECT_SIZE;
	uintptr_t a = ReadPtr(object + OFF_BIPOBJ_ADDON);
	uintptr_t clone = ReadPtr(object + OFF_BIPOBJ_CLONE);
	if (addon)
		*addon = a;
	if (!a || !IsA(a, RTTI_ARMA) || !clone || !IsA(clone, RTTI_AVOBJECT))
		return 0;
	return clone;
}

/* Is `obj` under `ancestor`? (Through NiAVObject::m_parent.) */
static bool Under(uintptr_t obj, uintptr_t ancestor, char *chain, size_t chainSize)
{
	size_t len = 0;
	for (int i = 0; obj && i < 24; i++) {
		if (chain && len < chainSize - 1)
			len += snprintf(chain + len, chainSize - len, "%s'%.32s'", i ? " < " : "", OrNone(ObjectName(obj)));
		if (obj == ancestor)
			return true;
		obj = ReadPtr(obj + OFF_PARENT);
		if (obj && !IsA(obj, RTTI_AVOBJECT))
			break;
	}
	return false;
}

/* Every equipped armor part's 3D, walked. */
static void WalkBiped(uintptr_t biped, SkinList *list, bool verbose)
{
	memset(&g_walk, 0, sizeof(g_walk));
	g_walk.verbose = verbose;
	g_walkBudget = 6000;
	for (int slot = 0; slot < BIPED_SLOTS; slot++) {
		uintptr_t addon;
		uintptr_t clone = BipedPart(biped, slot, &addon);
		if (!clone)
			continue;
		int before = list->count;
		g_walkOurs = OurForm(addon);
		WalkLine(" slot %d (biped slot %d): part '%.40s' %s%s", slot, slot + 30, OrNone(ObjectName(clone)), OrNone(ObjectTypeName(clone)),
		         g_walkOurs ? " (our armor addon)" : "");
		Visit(clone, 0, list);
		g_walkOurs = false;
		if (list->count > before && !g_rideRouteLogged)
			Log("tilt: the bike is worn in biped slot %d", slot + 30);
	}
}

/* The biped, its root, and what's in slot 57 (and where its 3D hangs). */
static void LogBikeSlot(uintptr_t player, uintptr_t biped, uintptr_t root)
{
	uintptr_t broot = ReadPtr(biped + OFF_BIPED_ROOT);
	Log("tilt: biped %p, its root %p '%s' %s (%s the 3D root)", (void *)biped, (void *)broot,
	    broot ? OrNone(ObjectName(broot)) : "-", broot ? OrNone(ObjectTypeName(broot)) : "-", broot == root ? "is" : "isn't");
	uintptr_t addon = 0;
	uintptr_t clone = BipedPart(biped, BIKE_SLOT_INDEX, &addon);
	uintptr_t rawClone = ReadPtr(biped + OFF_BIPED_OBJECTS + (uintptr_t)BIKE_SLOT_INDEX * BIPED_OBJECT_SIZE + OFF_BIPOBJ_CLONE);
	Log("tilt: slot 57: armor addon %p %s (form %08X, type %d), part %p %s", (void *)addon, addon ? OrNone(ObjectTypeName(addon)) : "-",
	    addon && Accessible(addon + OFF_FORM_ID, 8, false) ? *(const uint32_t *)(addon + OFF_FORM_ID) : 0,
	    addon && Accessible(addon + OFF_FORM_TYPE, 1, false) ? *(const uint8_t *)(addon + OFF_FORM_TYPE) : -1,
	    (void *)rawClone, rawClone ? OrNone(ObjectTypeName(rawClone)) : "-");
	if (clone) {
		char chain[700];
		bool underRoot = Under(clone, root, chain, sizeof(chain));
		Log("tilt: slot 57's part, up its parents: %s (%s the 3D root)", chain, underRoot ? "reaches" : "doesn't reach");
	}
	(void)player;
}

static void Diagnose(uintptr_t player)
{
	SkinList none = { .count = 0 };
	uintptr_t root = Root3D(player);
	Log("tilt: a second into the ride and no bike shape found; what's there:");
	Log("tilt: player 3D root %p '%s' %s", (void *)root, root ? OrNone(ObjectName(root)) : "-", root ? OrNone(ObjectTypeName(root)) : "-");
	WalkFrom(root, &none, true);
	LogWalk("under the 3D root");
	uintptr_t biped = Biped(player);
	if (!biped) {
		Log("tilt: no biped at Actor+0x%X", OFF_ACTOR_BIPED);
		return;
	}
	LogBikeSlot(player, biped, root);
	WalkBiped(biped, &none, true);
	LogWalk("the biped's equipped parts");
}

/* Every IntervalMs while the bike may tilt: hold the skins of the bike the player wears
 * now, let go of any that are gone (taken off, or the 3D was rebuilt). */
/* --- The rider's shapes ------------------------------------------------------- */

static void Retain(uintptr_t obj)
{
	InterlockedIncrement((volatile LONG *)(obj + OFF_REFCOUNT));
}

/* The game's 3 rows of 4 floats <-> a rotation x' = R x (row-major), the layout known. */
static void ReadRot(const float *rows, float R[9])
{
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++)
			R[i * 3 + j] = g_layout == LAYOUT_FILE ? rows[i * 4 + j] : rows[j * 4 + i];
}

static void WriteRot(float *rows, const float R[9])
{
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++)
			rows[g_layout == LAYOUT_FILE ? i * 4 + j : j * 4 + i] = R[i * 3 + j];
}

static void Transpose3(const float *a, float *out)
{
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++)
			out[i * 3 + j] = a[j * 3 + i];
}

/* A transform as the game keeps it (rows at +0, position at +0x30, scale at +0x3C): rigid? */
static bool LooksLikeTransform(const uint8_t *t)
{
	const float *r = (const float *)t, *pos = (const float *)(t + 0x30);
	float scale = *(const float *)(t + 0x3C);
	if (!(scale > 0.001f && scale < 1000.0f))
		return false;
	for (int i = 0; i < 3; i++) {
		if (!(fabsf(pos[i]) < 100000.0f))
			return false;
		for (int j = 0; j < 3; j++) {
			float d = r[i * 4] * r[j * 4] + r[i * 4 + 1] * r[j * 4 + 1] + r[i * 4 + 2] * r[j * 4 + 2];
			if (!(fabsf(d - (i == j ? 1.0f : 0.0f)) < 0.01f))
				return false;
		}
	}
	return true;
}

/* A rider's bone entry: a sphere (empty allowed: test 24's suit had a bone with no vertices
 * and a radius of 0, and the whole suit was left level) and a rigid transform. False with
 * the reason. */
static bool RiderBoneOk(const uint8_t *bone, char *why, size_t size)
{
	const float *r = (const float *)(bone + OFF_BONE_ROT), *pos = (const float *)(bone + OFF_BONE_POS);
	float radius = *(const float *)(bone + OFF_BONE_RADIUS);
	if (!(radius >= 0.0f && radius < 10000.0f)) {
		snprintf(why, size, "sphere radius %g", radius);
		return false;
	}
	for (int i = 0; i < 3; i++) {
		if (!(fabsf(pos[i]) < 10000.0f)) {
			snprintf(why, size, "position (%g, %g, %g)", pos[0], pos[1], pos[2]);
			return false;
		}
		for (int j = 0; j < 3; j++) {
			float d = r[i * 4] * r[j * 4] + r[i * 4 + 1] * r[j * 4 + 1] + r[i * 4 + 2] * r[j * 4 + 2];
			if (!(fabsf(d - (i == j ? 1.0f : 0.0f)) < 0.01f)) {
				snprintf(why, size, "rotation rows %d and %d (dot %g, rows (%g, %g, %g) (%g, %g, %g) (%g, %g, %g))", i, j, d,
				         r[0], r[1], r[2], r[4], r[5], r[6], r[8], r[9], r[10]);
				return false;
			}
		}
	}
	return true;
}

/* A node readable, and its world transform one? For the hold: each frame then reads without asking. */
static bool NodeWorldChecked(uintptr_t node, float N[9], float n[3], float *s, float Ni[9])
{
	return node && !(node & 7) && Accessible(node + OFF_WORLD_ROT, 0x40, false) && NodeWorld(node, N, n, s, Ni);
}

/* A skinned shape of the rider: can it be held? False with the reason (the first bone that fails). */
static bool RiderSkinOk(uintptr_t skin, uintptr_t data, char *why, size_t size)
{
	uintptr_t array = data + OFF_BONE_TRANSFORMS;
	uintptr_t bones = ReadPtr(array + OFF_ARRAY_ENTRIES);
	uint32_t count = Accessible(array + OFF_ARRAY_COUNT, 4, false) ? *(const uint32_t *)(array + OFF_ARRAY_COUNT) : 0;
	if (!bones || count < 1 || count > MAX_RIDER_BONES || !Accessible(bones, count * BONE_SIZE, false)) {
		snprintf(why, size, "%u bones, or their transforms can't be read", count);
		return false;
	}
	if (!Accessible(skin + OFF_SKIN_BONE_DATA, 8, true)) {
		snprintf(why, size, "its skin instance can't be written");
		return false;
	}
	/* The data is one of our copies (a decal cloned from a held shape, test 29): its entries
	 * are the tilted ones (a cloth bone's isn't a rotation then); the owner's level ones are
	 * what the bones are checked by. */
	const uint8_t *level = NULL;
	if (IsReplica(data)) {
		RiderPart *owner = OwnerOfReplica(data);
		if (owner && owner->count == (int)count)
			level = owner->saved;
	}
	for (uint32_t b = 0; b < count; b++) {
		char reason[200];
		if (!RiderBoneOk(level ? level + b * BONE_SIZE : (const uint8_t *)(bones + b * BONE_SIZE), reason, sizeof(reason))) {
			snprintf(why, size, "bone %u of %u: %s", b, count, reason);
			return false;
		}
	}
	uintptr_t nodes = SkinBoneNodes(skin, count);
	if (!nodes) {
		snprintf(why, size, "its skin instance doesn't list its %u bones where expected", count);
		return false;
	}
	(void)nodes;   /* a node that can't be read, or isn't rigid, leaves its bone alone (HoldRider): no reason to refuse */
	return true;
}

/* A node's world transform (rotation as x' = N x, position, scale), if it reads as one. No
 * accessibility check (test 26: a VirtualQuery a bone was the frame's whole cost): the node
 * was read at hold time, and the player's 3D is walked again every 0.1 s. */
/* A world transform as the game lays one out (NiTransform: the rotation, the position at
 * +0x30, the scale at +0x3C): a node's at +0x70, or a bone's own in the actor's flattened
 * bone tree (test 34: the hands' finger bones have no node, only that). */
static bool TransformWorld(uintptr_t xf, float N[9], float n[3], float *s, float Ni[9])
{
	if (!xf || (xf & 3))
		return false;
	ReadRot((const float *)xf, N);
	memcpy(n, (const void *)(xf + (OFF_WORLD_POS - OFF_WORLD_ROT)), 12);
	*s = *(const float *)(xf + (OFF_WORLD_SCALE - OFF_WORLD_ROT));
	if (!(*s > 0.001f && *s < 1000.0f) || !isfinite(n[0]) || !isfinite(n[1]) || !isfinite(n[2]))
		return false;
	/* Any invertible matrix will do (a cloth bone's isn't orthonormal); a hidden bone's, all
	 * zeros, won't. The inverse goes out, for the correction (once a frame a bone). */
	float own[9];
	for (int i = 0; i < 9; i++)
		if (!isfinite(N[i]) || fabsf(N[i]) > 1000.0f)
			return false;
	return Invert3(N, Ni ? Ni : own);
}

static bool NodeWorld(uintptr_t node, float N[9], float n[3], float *s, float Ni[9])
{
	if (!node || (node & 7))
		return false;
	return TransformWorld(node + OFF_WORLD_ROT, N, n, s, Ni);
}

/* A held part's bone b: its node's world transform, or, with no node, the bone's own. */
static bool BoneWorld(const uintptr_t *nodes, const uintptr_t *xforms, uint32_t b, float N[9], float n[3], float *s, float Ni[9])
{
	if (nodes[b])
		return NodeWorld(nodes[b], N, n, s, Ni);
	return xforms && xforms[b] && TransformWorld(xforms[b], N, n, s, Ni);
}

/* The inverse of a 3x3, false if it has none (|det| under 1e-4). */
static bool Invert3(const float *a, float *out)
{
	float c0 = a[4] * a[8] - a[5] * a[7], c1 = a[5] * a[6] - a[3] * a[8], c2 = a[3] * a[7] - a[4] * a[6];
	float det = a[0] * c0 + a[1] * c1 + a[2] * c2;
	if (!(fabsf(det) > 1e-4f))
		return false;
	float inv = 1.0f / det;
	out[0] = c0 * inv;                               out[1] = (a[2] * a[7] - a[1] * a[8]) * inv; out[2] = (a[1] * a[5] - a[2] * a[4]) * inv;
	out[3] = c1 * inv;                               out[4] = (a[0] * a[8] - a[2] * a[6]) * inv; out[5] = (a[2] * a[3] - a[0] * a[5]) * inv;
	out[6] = c2 * inv;                               out[7] = (a[1] * a[6] - a[0] * a[7]) * inv; out[8] = (a[0] * a[4] - a[1] * a[3]) * inv;
	return true;
}

/* The world map z -> R z + t in the frame of a node with world (N, n, s) and inverse Ni:
 * y -> C y + c, C = Ni R N, c = Ni (R n + t - n) / s. A true inverse, not the transpose: a cloth
 * bone's world transform isn't orthonormal (test 28: the backpack's purse bones). */
static void Correction(const float N[9], const float Ni[9], const float n[3], float s, const float R[9], const float t[3], float C[9], float c[3])
{
	float T[9], Rn[3], e[3];
	Mul3(R, N, T);
	Mul3(Ni, T, C);
	MulV(R, n, Rn);
	for (int i = 0; i < 3; i++)
		e[i] = Rn[i] + t[i] - n[i];
	MulV(Ni, e, c);
	for (int i = 0; i < 3; i++)
		c[i] /= s;
}

/* The maps' composition: first z -> Q z + q, then z -> R z + t: z -> (R Q) z + (R q + t). */
static void Compose(const float R[9], const float t[3], const float Q[9], const float q[3], float out[9], float outT[3])
{
	float Rq[3];
	Mul3(R, Q, out);
	MulV(R, q, Rq);
	for (int i = 0; i < 3; i++)
		outT[i] = Rq[i] + t[i];
}

/* How much of the bars' turn a bone gets, by its name (FO4's: "LArm_Hand [LHnd]",
 * "RArm_ForeArm3 [RLar3]", "LArm_Finger22 [LF22]"...): the hands and fingers all of it, the
 * forearm less and less towards the elbow (a cheap IK; the clips keep the hands at the straight
 * grips since test 29). */
/* A bone's part in the arms, from its name (LArm_UpperArm, RArm_ForeArm2, LArm_Hand, ...):
 * 1 the upper arm (and its twist bones), 2 the forearm (and its twist bones), 3 the hand and
 * fingers; +0x10 for the right arm. 0: not an arm bone. */
static uint8_t ArmRole(const char *name)
{
	if (!name)
		return 0;
	const char *p = strstr(name, "Arm_");
	if (!p || p == name)
		return 0;
	uint8_t side = (p[-1] == 'R' || p[-1] == 'r') ? 0x10 : 0;
	p += 4;
	if (strncmp(p, "Hand", 4) == 0 || strncmp(p, "Finger", 6) == 0)
		return 3 | side;
	if (strncmp(p, "ForeArm", 7) == 0 || strncmp(p, "ForeTwist", 9) == 0)
		return 2 | side;
	if (strncmp(p, "UpperArm", 8) == 0 || strncmp(p, "UpperTwist", 10) == 0)
		return 1 | side;
	return 0;
}

/* The two-bone solve of each arm (test 30: a forearm turned part way about the steering axis
 * stretched at the elbow): the shoulder (the upper arm's node) stays, the elbow (the first
 * forearm bone's node) swings in the plane ArmPole gives (or, without one, its own), the wrist
 * (the hand's node) lands on the grip turned with the bars. The nodes are noted as the rider's
 * shapes are held. */
typedef struct { uintptr_t upper, elbow, hand; } ArmChain;
typedef struct {
	bool ok; float R1[9], t1[3], R2[9], t2[3]; float L1, L2, reach, elbowMove;   /* world maps, before the tilt: the upper arm's and the forearm's (or, for the head, R1/t1 alone) */
	float wrist[3];                     /* the hand's node as the clips have it (the roll's pivot without a Grip in the parts file) */
	float fore[3];                      /* the solved forearm, the elbow to the wrist's target, world (before the tilt) */
	float upper[3];                     /* the solved upper arm, the shoulder to the elbow, world (before the tilt): the arm lines' figures (test 41) */
	float fade, turn, pole[3];          /* how far the pole was faded to ArmPoleTurn (0 to 1), the wrist's turn from the clips' pose, degrees, and the pole used (the bike's space, the left's x mirrored): the riding line */
	bool rolled; float Rh[9], th[3], roll;   /* the hand's map with the wrist roll (WristRoll), and the roll, degrees */
	float handUp;                       /* the hand's long axis above the forearm's line seen along the grip, degrees, the knuckles-up sense (HandPitch's), once rolled */
} ArmMap;
/* The hand's long axis in its own bone's frame, [0] the left, [1] the right: from the hand's
 * joint to the middle finger's first (LArm_Finger31, RArm_Finger31: the finger's own place in
 * the hand's frame, 7.6 units off), measured on the vanilla skeleton (skeleton.hkx's reference
 * pose; test 39). 5.8 deg off the bone's x: seen along the grip the knuckles' line runs 4.8 deg
 * above that x, toward the back of the hand. The clips (Rider._arm in riding_anims.py,
 * HAND_AXIS) lay this same axis along their forearm, HAND_PITCH above it, so at HandPitch 0 the
 * roll only follows the plugin's forearm where it differs from the clips' (the first clips of
 * test 40 laid the bone's x along it, and every hand was rolled 4.8 deg knuckles-down). The
 * node's world rotation takes it to world (x' = N x, the layout read as for every node). */
static const float g_handAxis[2][3] = { { 0.99489f, 0.08131f, 0.05994f }, { 0.99487f, 0.08146f, -0.05990f } };
static ArmChain g_arm[2];
static uintptr_t g_headNode;                /* the head's bone (HEAD), the joint the head is kept level about */
static uintptr_t g_torsoNode;               /* the lowest spine bone (SPINE1): the joint the upper body leans and twists about */
static bool g_armLogged[2];                 /* the arm's solve logged once a hold */

/* Each side's largest wrist turn this ride, at the ride's end (test 37: the one-time line with
 * the bars 8 deg over came at the first 8 deg, short of full lock, and said nothing of the 25
 * deg at the straight bars). */
static void LogWristMax(void)
{
	for (int side = 0; side < 2; side++) {
		if (g_wristMax[side] < 0.0f)
			continue;
		char fade[64];   /* test 41: how far the elbow's pole was faded to ArmPoleTurn then (the inside arm's) */
		if (ArmFadeOn())
			snprintf(fade, sizeof(fade), ", the elbow's pole %.2f of the way to ArmPoleTurn", g_wristMaxFade[side]);
		else
			snprintf(fade, sizeof(fade), ", the elbow's pole not faded");
		Log("rider: the %s wrist turned at most %.1f deg from the clips' pose this ride, on the steady frames (the bars %.1f deg over, the grip at %.0f%% of the reach, the hand rolled %.1f round the grip%s%s)",
		    side ? "right" : "left", g_wristMax[side], g_wristMaxBar[side], g_wristMaxReach[side], g_wristMaxRoll[side], g_wristRoll > 0.0f ? ", aligned with the forearm" : "; WristRoll 0", fade);
		g_wristMax[side] = -1.0f;
	}
}

/* The arm line's words for the wrist roll (test 39). */
static void RollWords(const ArmMap *am, char *out, size_t size)
{
	if (am->rolled) {
		char way[48] = "";
		if (g_wristRoll < 1.0f)
			snprintf(way, sizeof(way), ", WristRoll %g of the way", g_wristRoll);
		snprintf(out, size, "the hand rolled %.1f round the grip, aligned with the forearm: its axis %.1f deg above the forearm's seen along the grip (HandPitch %g%s)", am->roll, am->handUp, g_handPitch, way);
	} else if (g_wristRoll > 0.0f) {
		snprintf(out, size, "the hand not rolled (its long axis or the forearm along the grip's axis, or no hand to read)");
	} else {
		snprintf(out, size, "the hand not rolled (WristRoll 0: the clips' orientation, turned with the bars)");
	}
}

/* An arm's figures in the bike's own space (x to the rider's right, y forward, z up; test 41,
 * the tester's sketches: the elbow low and a little out, the forearm level): the elbow from the
 * shoulder, out (the arm's own side), forward and below; the upper arm's angle below level; the
 * forearm's pitch to the wrist seen from the side (+ rising), all from the solved vectors
 * (world, before the tilt) taken back through the bike's bone and its bind. */
static void ArmFigures(const ArmMap *am, int side, const float At[9], const float Nbi[9], float f[5])
{
	float a[3], u[3], b[3], v[3];
	MulV(Nbi, am->upper, a);
	MulV(At, a, u);
	MulV(Nbi, am->fore, b);
	MulV(At, b, v);
	float lu = sqrtf(u[0] * u[0] + u[1] * u[1] + u[2] * u[2]), sn = lu > 0.001f ? -u[2] / lu : 0.0f;
	f[0] = side ? u[0] : -u[0];
	f[1] = u[1];
	f[2] = -u[2];
	f[3] = asinf(sn > 1.0f ? 1.0f : sn < -1.0f ? -1.0f : sn) * 57.29578f;
	f[4] = atan2f(v[2], v[1]) * 57.29578f;
}

/* Those figures in words, with the pole the arm bent toward (the bike's space, as used: the
 * left's x mirrored) and how far it was faded. */
static void ArmFigureWords(const ArmMap *am, int side, const float At[9], const float Nbi[9], const float pole[3], char *out, size_t size)
{
	float f[5], p[3] = { pole[0], pole[1], pole[2] };
	char faded[48] = "";
	ArmFigures(am, side, At, Nbi, f);
	if (am->fade >= 0.005f) {
		snprintf(faded, sizeof(faded), ", %.2f of the way to ArmPoleTurn", am->fade);
	} else {   /* none to speak of (the bars within a hair of straight): ArmPole as given, not the blend's unit vector */
		p[0] = side ? g_armPole[0] : -g_armPole[0];
		p[1] = g_armPole[1];
		p[2] = g_armPole[2];
	}
	snprintf(out, size, "the elbow %.1f out, %.1f forward, %.1f below the shoulder (the upper arm %.1f deg below level), the forearm %+.1f deg to the wrist seen from the side (+ rising), the pole (%.2f, %.2f, %.2f)%s",
	         f[0], f[1], f[2], f[3], f[4], p[0], p[1], p[2], faded);
}

/* 5 for the upper body's bones above the pelvis, which lean and twist with the torso: the
 * spine (SPINE1, SPINE2), the chest, the collarbones and the neck. */
static uint8_t TorsoRole(const char *name)
{
	if (!name)
		return 0;
	if (NameHas(name, "spine") || NameHas(name, "chest") || NameHas(name, "collarbone") || NameHas(name, "clavicle") || NameHas(name, "neck"))
		return 5;
	return 0;
}

static bool TorsoPivotName(const char *name)
{
	return name && NameHas(name, "spine1");
}

/* The head's bone by name (HEAD, or Skyrim's NPC Head). */
static bool HeadName(const char *name)
{
	if (!name)
		return false;
	if (_strnicmp(name, "HEAD", 4) == 0 && (name[4] == 0 || name[4] == ' ' || name[4] == '['))
		return true;
	return strstr(name, "NPC Head") != NULL;
}

/* 4 for the head's bone and whatever hangs under it (the face, the eyes, a helmet's node). */
static uint8_t HeadRole(uintptr_t node)
{
	uintptr_t up = node;
	for (int depth = 0; depth < 8 && up; depth++) {
		if (HeadName(ObjectName(up)))
			return 4;
		up = ReadPtr(up + OFF_PARENT);
		if (up && !IsA(up, RTTI_AVOBJECT))
			up = 0;
	}
	return 0;
}

/* A bone with no part by name takes its nearest ancestor's (test 38's pose study: the body's
 * skin helpers, Belly_skin and UpperBelly_skin under the spine, the breasts under the chest,
 * the shoulder fat under the collarbones, the upper-arm fat under the upper arm's twist bone
 * and the rib helpers, have names that say nothing and were left where the clips put them
 * while the torso leaned and the arms swung: at 14 degrees of lean the shoulders' verts
 * strayed 7 units, a hump on the upper back and the shoulders caved in; at 25, 12). Up
 * through the parents, 8 at most, to the first with a part by name; the head's own walk
 * (HeadRole) has gone first. */
static uint8_t AncestorRole(uintptr_t node)
{
	uintptr_t up = ReadPtr(node + OFF_PARENT);
	for (int depth = 0; depth < 8 && up; depth++) {
		if (!IsA(up, RTTI_AVOBJECT))
			return 0;
		const char *name = ObjectName(up);
		uint8_t role = ArmRole(name);
		if (!role)
			role = TorsoRole(name);
		if (role)
			return role;
		up = ReadPtr(up + OFF_PARENT);
	}
	return 0;
}

static const char *RoleWord(uint8_t role)
{
	int kind = role & 0xF;
	bool right = (role & 0x10) != 0;
	return kind == 5 ? "the upper body" : kind == 4 ? "the head" : kind == 3 ? (right ? "the right hand" : "the left hand") : kind == 2 ? (right ? "the right forearm" : "the left forearm")
	     : kind == 1 ? (right ? "the right upper arm" : "the left upper arm") : "-";
}

static void NoteArmNode(uint8_t role, uintptr_t node, const char *name)
{
	if (!role || !name || !node)
		return;
	ArmChain *c = &g_arm[(role & 0x10) ? 1 : 0];
	const char *p = strstr(name, "Arm_");
	if (!p)
		return;
	p += 4;
	if (!c->upper && strncmp(p, "UpperArm", 8) == 0)
		c->upper = node;
	else if (!c->elbow && strncmp(p, "ForeArm1", 8) == 0)
		c->elbow = node;
	else if (!c->hand && strncmp(p, "Hand", 4) == 0)
		c->hand = node;
}

/* The least rotation taking a's direction to b's. */
static void RotationBetween(const float a[3], const float b[3], float R[9])
{
	static const float identity[9] = { 1, 0, 0, 0, 1, 0, 0, 0, 1 };
	float la = sqrtf(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]), lb = sqrtf(b[0] * b[0] + b[1] * b[1] + b[2] * b[2]);
	memcpy(R, identity, sizeof(identity));
	if (la < 1e-4f || lb < 1e-4f)
		return;
	float u[3] = { a[0] / la, a[1] / la, a[2] / la }, v[3] = { b[0] / lb, b[1] / lb, b[2] / lb };
	float axis[3] = { u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0] };
	float s = sqrtf(axis[0] * axis[0] + axis[1] * axis[1] + axis[2] * axis[2]), c = u[0] * v[0] + u[1] * v[1] + u[2] * v[2];
	if (s < 1e-5f) {
		if (c > 0.0f)
			return;
		float p[3] = { fabsf(u[0]) < 0.9f ? 1.0f : 0.0f, fabsf(u[0]) < 0.9f ? 0.0f : 1.0f, 0.0f };   /* opposite: a half turn about a perpendicular */
		float d = p[0] * u[0] + p[1] * u[1] + p[2] * u[2];
		for (int i = 0; i < 3; i++)
			p[i] -= d * u[i];
		float lp = sqrtf(p[0] * p[0] + p[1] * p[1] + p[2] * p[2]);
		for (int i = 0; i < 3; i++)
			p[i] /= lp;
		AxisRotation(p, 3.14159265f, R);
		return;
	}
	for (int i = 0; i < 3; i++)
		axis[i] /= s;
	AxisRotation(axis, atan2f(s, c), R);
}

/* With a torso map (Tr, tt): the arm is first carried by the upper body's lean and twist (the
 * shoulder, the elbow and the wrist with it), then solved from there to the grip, which stays
 * where the bars put it; the bones' maps come out composed with the torso's. poleW: the way
 * the elbow bends, a unit vector in world (NULL: the arm's own plane). toff: the hand's
 * target moved by this from the turned grip (NULL: not at all; the wrist roll's second pass,
 * test 38). */
static bool SolveArm(const ArmChain *chain, const float Q[9], const float q[3], const float Tr[9], const float tt[3], bool torso, const float poleW[3], const float toff[3], ArmMap *out)
{
	float N[9], S[3], E[3], W[3], sc;
	out->ok = false;
	if (!chain->upper || !chain->elbow || !chain->hand)
		return false;
	if (!NodeWorld(chain->upper, N, S, &sc, NULL) || !NodeWorld(chain->elbow, N, E, &sc, NULL) || !NodeWorld(chain->hand, N, W, &sc, NULL))
		return false;
	float QW[3], T[3], d[3], v1[3], v2[3];
	MulV(Q, W, QW);
	memcpy(out->wrist, W, sizeof(out->wrist));
	out->rolled = false;
	for (int i = 0; i < 3; i++)
		T[i] = QW[i] + q[i] + (toff ? toff[i] : 0.0f);   /* the grip turned with the bars: where the hand goes, torso or not */
	if (torso) {
		float S2[3], E2t[3], W2[3];
		MulV(Tr, S, S2);
		MulV(Tr, E, E2t);
		MulV(Tr, W, W2);
		for (int i = 0; i < 3; i++) {
			S[i] = S2[i] + tt[i];
			E[i] = E2t[i] + tt[i];
			W[i] = W2[i] + tt[i];
		}
	}
	for (int i = 0; i < 3; i++) {
		d[i] = T[i] - S[i];
		v1[i] = E[i] - S[i];
		v2[i] = W[i] - E[i];
	}
	float dl = sqrtf(d[0] * d[0] + d[1] * d[1] + d[2] * d[2]);
	float L1 = sqrtf(v1[0] * v1[0] + v1[1] * v1[1] + v1[2] * v1[2]), L2 = sqrtf(v2[0] * v2[0] + v2[1] * v2[1] + v2[2] * v2[2]);
	if (L1 < 1.0f || L2 < 1.0f || dl < 0.001f)
		return false;
	float u[3] = { d[0] / dl, d[1] / dl, d[2] / dl };
	float reach = L1 + L2 - 0.01f;
	if (dl > reach)
		dl = reach;   /* straight at most (the hand goes on to the grip regardless) */
	float a = (L1 * L1 - L2 * L2 + dl * dl) / (2.0f * dl), h2 = L1 * L1 - a * a, h = h2 > 0.0f ? sqrtf(h2) : 0.0f;
	/* The bend plane (test 38: the elbows stood out at shoulder height, the arm running
	 * almost level from the shoulder, where riders on a bike of this shape have them bent
	 * and tucked under the shoulders, the upper arms 35 to 45 deg below level; the plane
	 * kept here till then was the clips' own, from an IK pole pointing mostly sideways, so
	 * every bit of bend the shorter reach added pushed the elbow further out): the elbow
	 * goes the way ArmPole points, projected across the shoulder-to-grip line; with no pole,
	 * or one within 5 deg of that line, the elbow's offset from the shoulder-to-wrist line
	 * now, kept. */
	float n[3], ln = 0.0f;
	if (poleW) {
		float pu = poleW[0] * u[0] + poleW[1] * u[1] + poleW[2] * u[2];
		for (int i = 0; i < 3; i++)
			n[i] = poleW[i] - pu * u[i];
		ln = sqrtf(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
		if (ln < 0.0872f)   /* the sine of 5 deg: the pole along the arm says nothing of the plane */
			ln = 0.0f;
	}
	if (ln == 0.0f) {
		float w0[3] = { W[0] - S[0], W[1] - S[1], W[2] - S[2] };
		float lw2 = w0[0] * w0[0] + w0[1] * w0[1] + w0[2] * w0[2], k = lw2 > 1e-6f ? (v1[0] * w0[0] + v1[1] * w0[1] + v1[2] * w0[2]) / lw2 : 0.0f;
		for (int i = 0; i < 3; i++)
			n[i] = v1[i] - k * w0[i];
		if (n[0] * n[0] + n[1] * n[1] + n[2] * n[2] < 1e-4f) {
			n[0] = 0.0f;
			n[1] = 0.0f;
			n[2] = -1.0f;   /* a straight arm: bend downwards */
		}
		float nu = n[0] * u[0] + n[1] * u[1] + n[2] * u[2];
		for (int i = 0; i < 3; i++)
			n[i] -= nu * u[i];
		ln = sqrtf(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
		if (ln < 1e-4f) {
			float z[3] = { 0.0f, 0.0f, -1.0f };
			float zu = z[2] * u[2];
			for (int i = 0; i < 3; i++)
				n[i] = z[i] - zu * u[i];
			ln = sqrtf(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
			if (ln < 1e-4f)
				return false;
		}
	}
	for (int i = 0; i < 3; i++)
		n[i] /= ln;
	float E2[3], v1n[3], v2n[3], R1S[3], R2E[3];
	for (int i = 0; i < 3; i++) {
		E2[i] = S[i] + a * u[i] + h * n[i];
		v1n[i] = E2[i] - S[i];
		v2n[i] = T[i] - E2[i];
	}
	out->L1 = L1;
	out->L2 = L2;
	memcpy(out->fore, v2n, sizeof(out->fore));
	memcpy(out->upper, v1n, sizeof(out->upper));
	out->reach = sqrtf(d[0] * d[0] + d[1] * d[1] + d[2] * d[2]);
	out->elbowMove = sqrtf((E2[0] - E[0]) * (E2[0] - E[0]) + (E2[1] - E[1]) * (E2[1] - E[1]) + (E2[2] - E[2]) * (E2[2] - E[2]));
	RotationBetween(v1, v1n, out->R1);
	RotationBetween(v2, v2n, out->R2);
	MulV(out->R1, S, R1S);
	MulV(out->R2, E, R2E);
	for (int i = 0; i < 3; i++) {
		out->t1[i] = S[i] - R1S[i];
		out->t2[i] = E2[i] - R2E[i];
	}
	if (torso) {   /* the torso's map first, then the swing */
		float Rc[9], tc[3];
		Compose(out->R1, out->t1, Tr, tt, Rc, tc);
		memcpy(out->R1, Rc, sizeof(Rc));
		memcpy(out->t1, tc, sizeof(tc));
		Compose(out->R2, out->t2, Tr, tt, Rc, tc);
		memcpy(out->R2, Rc, sizeof(Rc));
		memcpy(out->t2, tc, sizeof(tc));
	}
	out->ok = true;
	return true;
}

static float Dist3f(const float a[3], const float b[3])
{
	return sqrtf((a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]) + (a[2] - b[2]) * (a[2] - b[2]));
}

/* The grips' distance from the shoulders swung forward by lean degrees about the spine's
 * joint, over the arms' reach, averaged over the chains found (the bars straight: the hands
 * are on the grips as the clips pose them). */
static float GripReachAt(float lean, const float pivot[3], const float rightW[3], float sign, const float S[2][3], const float W[2][3], const float reach[2], int sides)
{
	float Rl[9], sum = 0.0f;
	AxisRotation(rightW, sign * lean / 57.29578f, Rl);
	for (int k = 0; k < sides; k++) {
		float rel[3] = { S[k][0] - pivot[0], S[k][1] - pivot[1], S[k][2] - pivot[2] }, Rr[3], S2[3];
		MulV(Rl, rel, Rr);
		for (int i = 0; i < 3; i++)
			S2[i] = Rr[i] + pivot[i];
		sum += Dist3f(S2, W[k]) / reach[k];
	}
	return sum / (float)sides;
}

/* How far the wrist is turned from the clips' pose, degrees: the hand's map Mh (the bars' turn
 * Qb, and the wrist roll since test 37), the forearm's its swing (R2, with the torso's map in
 * it), so the wrist's relative rotation changes by R2^T Mh, whose angle this is (test 36: the
 * inner arm looked broken at full lock; the next log says whether the wrist kinks). */
static float WristTurn(const float R2[9], const float Mh[9])
{
	float R2t[9], M[9];
	Transpose3(R2, R2t);
	Mul3(R2t, Mh, M);
	float c = 0.5f * (M[0] + M[4] + M[8] - 1.0f);
	return acosf(c > 1.0f ? 1.0f : c < -1.0f ? -1.0f : c) * 57.29578f;
}

/* The angle about the unit axis g, radians, that takes a's direction to b's, both seen along g
 * (projected on the plane normal to it; the wrist roll's measure since test 39). False when
 * either lies within 6 deg of g: seen along it, it has no direction to speak of. */
static bool AngleAbout(const float a[3], const float b[3], const float g[3], float *angle)
{
	float da = a[0] * g[0] + a[1] * g[1] + a[2] * g[2], db = b[0] * g[0] + b[1] * g[1] + b[2] * g[2], pa[3], pb[3];
	for (int i = 0; i < 3; i++) {
		pa[i] = a[i] - da * g[i];
		pb[i] = b[i] - db * g[i];
	}
	float la = sqrtf(pa[0] * pa[0] + pa[1] * pa[1] + pa[2] * pa[2]), lb = sqrtf(pb[0] * pb[0] + pb[1] * pb[1] + pb[2] * pb[2]);
	float na = sqrtf(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]), nb = sqrtf(b[0] * b[0] + b[1] * b[1] + b[2] * b[2]);
	if (!(la > 0.1f * na) || !(lb > 0.1f * nb) || na < 1e-6f || nb < 1e-6f)
		return false;
	float c[3] = { pa[1] * pb[2] - pa[2] * pb[1], pa[2] * pb[0] - pa[0] * pb[2], pa[0] * pb[1] - pa[1] * pb[0] };
	*angle = atan2f(c[0] * g[0] + c[1] * g[1] + c[2] * g[2], pa[0] * pb[0] + pa[1] * pb[1] + pa[2] * pb[2]);
	return true;
}

/* The arm chains' joints' (the shoulder, the elbow, the wrist) biggest move since last frame,
 * relative to the bike's bone (test 34: the bike's own motion swamps a world figure), for the
 * lean solve's guard: the Pip-Boy raise of test 37 moved the arm bones 40.7 in a frame and the
 * lean was solved from the raised pose. Measured every frame the bike's bone can be read;
 * false while a joint can be read this frame but not yet last frame (a fresh hold, the first
 * frame of a ride). With no joint to read at all there's nothing to wait for (true, the move
 * 0): the solve's own count then gives the chain up as before. */
static bool ArmChainMove(const float nb[3], float *move)
{
	bool measured = false, readable = false;
	*move = 0.0f;
	for (int side = 0; side < 2; side++) {
		const uintptr_t joints[3] = { g_arm[side].upper, g_arm[side].elbow, g_arm[side].hand };
		for (int j = 0; j < 3; j++) {
			float N[9], p[3], s, rel[3];
			bool ok = joints[j] && NodeWorld(joints[j], N, p, &s, NULL);
			if (ok) {
				readable = true;
				for (int i = 0; i < 3; i++)
					rel[i] = p[i] - nb[i];
				if (g_armMoveLastOk[side][j]) {
					float d = Dist3f(rel, g_armMoveLast[side][j]);
					if (d > *move)
						*move = d;
					measured = true;
				}
				memcpy(g_armMoveLast[side][j], rel, sizeof(rel));
			}
			g_armMoveLastOk[side][j] = ok;
		}
	}
	return measured || !readable;
}

/* The run's kept solve final, 3 s into the run with no reading better (test 39). After a jump
 * whose run began from the solve before it (test 40), the line says that solve stands, with
 * its reading, in place of the "solved again" line the jump would have had. The seconds are
 * the run's own since it really began (the ride's start, the jump, the rider held again, the
 * riding pose come), not its count moved on for a late first reading (review of test 40's
 * first build). r0: the reading now. */
static void TorsoFinalAsKept(float r0)
{
	float since = (float)g_clock - g_torsoSeqFrom;
	g_torsoFinal = true;
	if (g_torsoKept && g_torsoRearmWhy[0])
		Log("rider: the upper body's lean final at %.1f deg: the solve from before %s stands, %.0f%% of the reach as the clips pose it, no reading of the %.1f s since beating it (the grips at %.0f%% now)",
		    g_torsoLean, g_torsoRearmWhy, g_torsoBestR0 * 100.0f, since, r0 * 100.0f);
	else
		Log("rider: the upper body's lean final at %.1f deg, solved at %.0f%% of the reach as the clips pose it, the best reading of the %.1f s since %s (the grips at %.0f%% now)",
		    g_torsoLean, g_torsoBestR0 * 100.0f, since, g_torsoSeqWhat, r0 * 100.0f);
	g_torsoKept = false;
	g_torsoRearmWhy[0] = 0;   /* said */
}

/* The upper body's forward lean for this ride: TorsoLean degrees, or, by default, the least
 * that brings the straight grips to ArmReach of the arms' reach (test 32: the arms were
 * locked straight as the clips pose them, the grips at 100% of the reach, so a turn put the
 * far grip out of reach and the wrist stretched). Bisection, up to 30 degrees (test 38: 0.88
 * of the reach took 6 to 9, about 1.4% a degree, so 0.80 takes about 14, and the references
 * have the torso 30 to 40 deg forward of vertical; the 15 of old would cap ArmReach at
 * about 0.78 on that rider). Needs a chain:
 * tried again next frame otherwise, for 300 tries without one. Not solved while the arms
 * are on the move (over 10 in a frame) or while the clips' own reach is short of the riding
 * pose's (under 95%: the riding clips put the grips at 100%); neither is a try. Test 37: the
 * tester opened the Pip-Boy a second after getting on, the arm bones moved 40.7 in a frame,
 * the grips read 82% of the reach, and the 0 lean solved from that pose stuck for five
 * minutes. The short reach is tried again every half second, and after 20 s of it the solve
 * is taken as it comes (another mod's clips may well pose the grips nearer); test 38: a
 * Pip-Boy held open over 20 s right after getting on (the map browsed for a fast travel)
 * did just that, the grips at 82%, the lean 0, and the solve was final, so the full-lock
 * over-reach was back for the whole ride. Taken as it comes, the solve isn't final: the
 * reach is measured again every half second, the lean solved again when the reach has moved
 * by more than 3% since the last solve, and once the riding pose is there (95%) a fresh run
 * of readings starts from it, as after a jump of the player (RearmTorsoSolve) or at the
 * ride's start.
 * Test 39: after a jump the first reading of 95% or more was kept, final at once, and at a
 * ride's start the last of its first 3 s: after two fast travels the grips read 95% and the
 * lean was 11.1 and 11.4 deg for the rest
 * of the ride, against the riding pose's 14.6 at 100%, and one ride's start ended final at 97%
 * (12.2, 01:41:42) with 14.4 at 100% a second before. Now each run of readings keeps the
 * solve from the largest reach seen (a reading of the riding pose, 99% or more, replaces
 * one before it in any case: the later is the more settled) and is final once two readings of
 * the riding pose in a row agree within a degree, or 3 s into the run with the best seen (a
 * run whose first good reading came late counted from half a second before it). Not
 * on the first 99% reading: at five of test 39's six ride starts the first reading, 0.8 or
 * 0.9 s in, read 100% with 15.9 to 21.1 deg, the getting-on still blending out (14.6 half a
 * second later, all five times). A reading short of the kept one changes nothing. A run begun
 * by a jump of the player starts from the solve before it when that came from a good reading
 * (test 40: RearmTorsoSolve), and ends final on it if no reading beats it. */
static void SolveTorsoLean(void)
{
	float Nt[9], pivot[3], st;
	if (g_torsoLeanSetting >= 0.0f) {
		g_torsoSolvedAt = (float)g_clock;
		g_torsoLean = g_torsoLeanSetting;
		g_torsoLeanSet = g_torsoFinal = true;
		Log("rider: the upper body leaned %.1f deg forward (TorsoLean), turned %g of the bars' angle and leaned %g deg per degree of it into a turn (TorsoTwist, TorsoSideLean)", g_torsoLean, g_torsoTwist, g_torsoSideLean);
		return;
	}
	if (!g_armMoveOk || g_armMoveNow > 10.0f)
		return;   /* the arms on the move (a Pip-Boy raise, a hit): next frame */
	g_torsoSolvedAt = (float)g_clock;
	float rightW[3] = { cosf(g_headingNow), -sinf(g_headingNow), 0.0f }, fwdW[3] = { sinf(g_headingNow), cosf(g_headingNow), 0.0f }, upW[3] = { 0, 0, 1 }, Rl[9], probe[3];
	float S[2][3], W[2][3], reach[2];
	int sides = 0;
	if (NodeWorld(g_torsoNode, Nt, pivot, &st, NULL)) {
		for (int side = 0; side < 2; side++) {
			const ArmChain *c = &g_arm[side];
			float N[9], E[3], sc;
			if (!c->upper || !c->elbow || !c->hand || !NodeWorld(c->upper, N, S[sides], &sc, NULL) || !NodeWorld(c->elbow, N, E, &sc, NULL) || !NodeWorld(c->hand, N, W[sides], &sc, NULL))
				continue;
			float L1 = Dist3f(S[sides], E), L2 = Dist3f(E, W[sides]);
			if (L1 < 1.0f || L2 < 1.0f)
				continue;
			reach[sides] = L1 + L2;
			sides++;
		}
	}
	if (!sides) {
		if (++g_torsoTries > 300) {   /* the tries without a chain (test 38: the solve comes again through a ride now, so the count is of these alone) */
			g_torsoLean = 0.0f;
			g_torsoLeanSet = g_torsoFinal = true;
			g_torsoNoChain = true;
			Log("rider: no arm chain to lean the upper body for: it stays as the clips pose it%s", AfterLoadNote());
		}
		return;
	}
	/* Which way AxisRotation leans forward: the way that takes the up vector towards the front. */
	AxisRotation(rightW, 1.0f / 57.29578f, Rl);
	MulV(Rl, upW, probe);
	float sign = probe[0] * fwdW[0] + probe[1] * fwdW[1] >= 0.0f ? 1.0f : -1.0f;
	float r0 = GripReachAt(0.0f, pivot, rightW, sign, S, W, reach, sides), lean = 0.0f, inRun = (float)g_clock - g_torsoSeqAt;
	char note[200];
	note[0] = 0;
	if (r0 < 0.95f && !g_torsoAsItComes) {
		if (g_torsoBestR0 >= 0.95f) {
			/* A solve of this run kept already (test 39), or the one from before a jump (test
			 * 40): a short reading changes nothing, and 3 s into the run the kept one is final. */
			if (inRun >= 3.0f)
				TorsoFinalAsKept(r0);
			g_torsoRetryAt = (float)g_clock + 0.5f;
			return;
		}
		if (g_torsoWaitSince < 0.0f)
			g_torsoWaitSince = (float)g_clock;
		if ((float)g_clock - g_torsoWaitSince < 20.0f) {
			if (!g_torsoWaitLogged) {
				g_torsoWaitLogged = true;
				Log("rider: the upper body's lean not solved yet: the grips at %.0f%% of the reach as the clips pose it (the riding pose puts them at 100%%: a menu, a raised arm?), tried again every half second", r0 * 100.0f);
			}
			g_torsoRetryAt = (float)g_clock + 0.5f;
			return;
		}
		g_torsoAsItComes = true;
		snprintf(note, sizeof(note), "; taken as it comes after 20 s with the grips short of the riding pose's reach, measured again every half second");
	} else if (g_torsoAsItComes) {
		/* Taken as it comes earlier (test 38): the riding pose come, a fresh run of readings
		 * from it (test 39: its first reading isn't final); the grips still short, solved again
		 * when the reach has moved by over 3%. */
		if (r0 >= 0.95f) {
			g_torsoAsItComes = false;
			g_torsoSeqAt = g_torsoSeqFrom = (float)g_clock;
			g_torsoBestR0 = -1.0f;
			g_torsoSeqWhat = "the riding pose came";
			inRun = 0.0f;
			snprintf(note, sizeof(note), "; the riding pose came: solved again");
		} else if (fabsf(r0 - g_torsoLastR0) > 0.03f) {
			snprintf(note, sizeof(note), "; taken as it comes still, the grips' reach moved from %.0f%% to %.0f%% as the clips pose it: solved again", g_torsoLastR0 * 100.0f, r0 * 100.0f);
		} else {
			g_torsoRetryAt = (float)g_clock + 0.5f;
			return;
		}
	}
	bool riding = r0 >= 0.99f, run = !g_torsoAsItComes;   /* a reading of the riding pose; a reading of a run (not taken as it comes) */
	if (run && g_torsoBestR0 >= 0.0f && !riding && r0 < g_torsoBestR0 + 0.005f) {
		/* No better than the solve kept (by half a percent: the same pose reads a hair either
		 * way frame to frame): it stands; 3 s into the run it's final. */
		if (inRun >= 3.0f)
			TorsoFinalAsKept(r0);
		return;
	}
	g_torsoLastR0 = r0;
	if (r0 > g_armReach) {
		float lo = 0.0f, hi = 30.0f;
		if (GripReachAt(hi, pivot, rightW, sign, S, W, reach, sides) > g_armReach) {
			lean = hi;
		} else {
			for (int it = 0; it < 24; it++) {
				float mid = 0.5f * (lo + hi);
				if (GripReachAt(mid, pivot, rightW, sign, S, W, reach, sides) > g_armReach)
					lo = mid;
				else
					hi = mid;
			}
			lean = hi;
		}
	}
	bool replaced = false;
	if (run) {
		/* The best of the run (test 39): final on two readings of the riding pose in a row that
		 * agree within a degree, or 3 s into the run. */
		replaced = g_torsoBestR0 >= 0.0f;
		if (!replaced && inRun > 0.5f) {
			/* The run's first reading late (the arms on the move, the grips short a while: test
			 * 39's second fast travel read 92% for 2.5 s, then 95%): its 3 s counted as if from
			 * half a second before it, so the pose still gets its readings. */
			g_torsoSeqAt = (float)g_clock - 0.5f;
			inRun = 0.5f;
		}
		if ((riding && g_torsoBestR0 >= 0.99f && fabsf(lean - g_torsoLean) <= 1.0f) || inRun >= 3.0f)
			g_torsoFinal = true;
		if (replaced) {
			size_t used = strlen(note);
			if (riding)
				snprintf(note + used, sizeof(note) - used, "; solved again: the riding pose read %.0f%% (%.0f%% for the solve before, %.1f deg)", r0 * 100.0f, g_torsoBestR0 * 100.0f, g_torsoLean);
			else
				snprintf(note + used, sizeof(note) - used, "; solved again: the grips read %.0f%%, more than the %.0f%% of the solve before (%.1f deg)", r0 * 100.0f, g_torsoBestR0 * 100.0f, g_torsoLean);
		}
		g_torsoBestR0 = r0;
		g_torsoKept = false;   /* beaten: the solve before the jump is gone */
	}
	bool changed = !g_torsoLeanSet || fabsf(lean - g_torsoLean) > 0.3f, rearmed = g_torsoRearmWhy[0] != 0;
	g_torsoLean = lean;
	g_torsoLeanSet = true;
	if (changed || rearmed || g_torsoFinal)   /* after a jump the line comes even with the lean unchanged: it says the solve was made; and the final one always (test 39) */
		Log("rider: the upper body leaned %.1f deg forward about the spine's joint: the grips at %.0f%% of the arms' reach with the bars straight (%.0f%% as the clips pose it; ArmReach %g, %d arm%s; %.1f s into the ride%s%s%s%s), turned %g of the bars' angle and leaned %g deg per degree of it into a turn (TorsoTwist, TorsoSideLean)",
		    lean, GripReachAt(lean, pivot, rightW, sign, S, W, reach, sides) * 100.0f, r0 * 100.0f, g_armReach, sides, sides == 1 ? "" : "s",
		    (float)g_clock - g_rideStartClock, g_torsoFinal ? ", final" : "", note, rearmed ? "; solved again after " : "", g_torsoRearmWhy, g_torsoTwist, g_torsoSideLean);
	else if (replaced)
		Log("rider: the upper body's lean solved again: the grips read %.0f%% as the clips pose them, %.1f deg as before (%.1f s into the ride)", r0 * 100.0f, lean, (float)g_clock - g_rideStartClock);
	g_torsoRearmWhy[0] = 0;
}

/* The world map (before the tilt) an arm bone gets for the bars' turn: the hand and fingers
 * the turn itself (rolled round the grip into line with the forearm, WristRoll, when that side's
 * arm is solved), the upper arm and the forearm their side's solve, or, with no chain to
 * solve, the forearm part of the turn (the old way). False: no map. */
static bool ArmMapFor(uint8_t role, bool hands, const ArmMap arm[4], const float Qb[9], const float qb[3], const float axisW[3], const float qW[3], float R[9], float t[3])
{
	if (!role)
		return false;
	int side = (role & 0x10) ? 1 : 0, kind = role & 0xF;
	if (kind == 4 || kind == 5) {   /* the head (arm[2] holds its map) and the upper body (arm[3]) */
		const ArmMap *m = &arm[kind == 4 ? 2 : 3];
		if (!m->ok)
			return false;
		memcpy(R, m->R1, sizeof(float) * 9);
		memcpy(t, m->t1, sizeof(float) * 3);
		return true;
	}
	if (!hands)
		return false;
	if (kind == 3) {
		if (arm[side].ok && arm[side].rolled) {
			memcpy(R, arm[side].Rh, sizeof(float) * 9);
			memcpy(t, arm[side].th, sizeof(float) * 3);
		} else {
			memcpy(R, Qb, sizeof(float) * 9);
			memcpy(t, qb, sizeof(float) * 3);
		}
		return true;
	}
	if (arm[side].ok) {
		memcpy(R, kind == 1 ? arm[side].R1 : arm[side].R2, sizeof(float) * 9);
		memcpy(t, kind == 1 ? arm[side].t1 : arm[side].t2, sizeof(float) * 3);
		return true;
	}
	if (kind == 2) {
		float Qq[3];
		AxisRotation(axisW, 0.55f * g_barNow / 57.29578f, R);
		MulV(R, qW, Qq);
		for (int i = 0; i < 3; i++)
			t[i] = qW[i] - Qq[i];
		return true;
	}
	return false;
}

/* saved -> live: the transform (rows at +rotOff, position at +posOff) with C, c put in front. */
static void PutInFront(const uint8_t *saved, uint8_t *live, int rotOff, int posOff, const float C[9], const float c[3])
{
	float A[9], B[9], p[3], Cp[3];
	ReadRot((const float *)(saved + rotOff), A);
	Mul3(C, A, B);
	WriteRot((float *)(live + rotOff), B);
	memcpy(p, saved + posOff, 12);
	MulV(C, p, Cp);
	for (int i = 0; i < 3; i++)
		((float *)(live + posOff))[i] = Cp[i] + c[i];
}

/* A BoneData of ours for a shape: the game's vtable (it's one of them to the game), a
 * reference count that never reaches zero (the game's last reference must never delete it),
 * its transforms in a buffer of ours. Reused once nothing of the game refers to it. */
static Replica *TakeReplica(uintptr_t original, int count)
{
	/* Reused once nothing of the game refers to it: at or under the base count (the game's
	 * smart-pointer assignment lets one go when it points a skin elsewhere; test 29: a count
	 * one under the base kept slots from ever being reused). */
	Replica *r = NULL;
	for (int i = 0; i < g_replicaCount && !r; i++)
		if (!g_replicas[i].inUse && g_replicas[i].capacity >= count &&
		    *(const volatile uint32_t *)(g_replicas[i].obj + OFF_REFCOUNT) <= REPLICA_REFS)
			r = &g_replicas[i];
	if (!r) {
		if (g_replicaCount >= (int)(sizeof(g_replicas) / sizeof(g_replicas[0])))
			return NULL;
		int capacity = count < 32 ? 32 : count;
		uint8_t *block = (uint8_t *)VirtualAlloc(NULL, 0x40 + (size_t)capacity * BONE_SIZE, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
		if (!block)
			return NULL;
		r = &g_replicas[g_replicaCount++];
		r->obj = (uintptr_t)block;
		r->entries = block + 0x40;
		r->capacity = capacity;
	}
	uint8_t *o = (uint8_t *)r->obj;
	memset(o, 0, 0x40);
	*(uintptr_t *)o = ReadPtr(original);
	*(uint32_t *)(o + OFF_REFCOUNT) = REPLICA_REFS;
	*(uint8_t **)(o + OFF_BONE_TRANSFORMS + OFF_ARRAY_ENTRIES) = r->entries;
	*(uint32_t *)(o + OFF_BONE_TRANSFORMS + 8) = (uint32_t)count;
	*(uint32_t *)(o + OFF_BONE_TRANSFORMS + OFF_ARRAY_COUNT) = (uint32_t)count;
	r->inUse = true;
	return r;
}

static void FreeReplica(uintptr_t obj)
{
	for (int i = 0; i < g_replicaCount; i++)
		if (g_replicas[i].obj == obj)
			g_replicas[i].inUse = false;
}

/* Which held part's copy this is, if any (test 29: a blood decal cloned from the suit came
 * with the suit's skin instance, pointing at our copy). */
static RiderPart *OwnerOfReplica(uintptr_t data)
{
	for (int i = 0; i < g_riderCount; i++)
		if (g_rider[i].replica && g_rider[i].replica == data)
			return &g_rider[i];
	return NULL;
}

static bool IsReplica(uintptr_t data)
{
	for (int i = 0; i < g_replicaCount; i++)
		if (g_replicas[i].obj == data)
			return true;
	return false;
}

/* NiAVObject's world transform where it's expected? The player's 3D root sits at the player.
 * Only a yes is kept for the ride (finding 2 of test 40): after a load to another place the
 * 3D's world can read a frame or more behind the player (test 35: 0.26 s), so a no is asked
 * again every sync and kept only after 3 s of it, when it's the layout itself that's not as
 * expected (test 23). Nothing of the rider is held meanwhile. */
static bool RiderWorldOk(uintptr_t player)
{
	if (g_riderWorldChecked)
		return g_riderWorldOk;
	uintptr_t root = Root3D(player);
	if (!root || !Accessible(root + OFF_WORLD_ROT, 0x40, false) || !Accessible(player + OFF_REFR_POS, 12, false))
		return false;
	const float *w = (const float *)(root + OFF_WORLD_POS), *p = (const float *)(player + OFF_REFR_POS);
	float s = *(const float *)(root + OFF_WORLD_SCALE);
	float d = sqrtf((w[0] - p[0]) * (w[0] - p[0]) + (w[1] - p[1]) * (w[1] - p[1]) + (w[2] - p[2]) * (w[2] - p[2]));
	if (isfinite(d) && d < 64.0f && s > 0.2f && s < 5.0f) {
		if (g_riderWorldFailSince >= 0.0f)
			Log("rider: the player's 3D root reads at the player now, %.2f s after it didn't: the rider held", (float)g_clock - g_riderWorldFailSince);
		g_riderWorldChecked = g_riderWorldOk = true;
		g_riderWorldFailSince = -1.0f;
		return true;
	}
	if (g_riderWorldFailSince < 0.0f) {
		g_riderWorldFailSince = (float)g_clock;
		Log("rider: the player's 3D root reads as at (%.0f, %.0f, %.0f), scale %g, the player at (%.0f, %.0f, %.0f), %.0f apart (%.1f s into the ride%s): not held yet, tried again every sync for 3 s",
		    w[0], w[1], w[2], s, p[0], p[1], p[2], d, (float)g_clock - g_rideStartClock, g_rideFromLoad ? ", after a load" : "");
	}
	if ((float)g_clock - g_riderWorldFailSince >= 3.0f) {
		g_riderWorldChecked = true;
		g_riderWorldOk = false;
		Log("rider: the player's 3D root still reads as at (%.0f, %.0f, %.0f), scale %g, the player at (%.0f, %.0f, %.0f), after 3 s: not NiAVObject's"
		    " world transform as expected; the rider stays level%s", w[0], w[1], w[2], s, p[0], p[1], p[2], AfterLoadNote());
	}
	return false;
}

/* The hands' bones (test 33: the fingers stretched into spikes): each bone's part and how far
 * its node sits from its side's hand node, to see whether every finger bone is read and mapped
 * like the hand. */
static void LogHandBones(const char *name, const uintptr_t *nodes, const uintptr_t *xforms, const uint8_t *skip, const uint8_t *arm, int count)
{
	char line[440];
	int len = 0;
	line[0] = 0;
	for (int b = 0; b < count; b++) {
		uintptr_t node = nodes[b];
		float N[9], n[3], H[3], sc, dist = -1.0f;
		int side = (arm[b] & 0x10) ? 1 : 0;
		if (!skip[b] && g_arm[side].hand && BoneWorld(nodes, xforms, (uint32_t)b, N, n, &sc, NULL) && NodeWorld(g_arm[side].hand, N, H, &sc, NULL))
			dist = Dist3f(n, H);
		len += snprintf(line + len, sizeof(line) - len, "%s%d %.26s (%s)", len ? ", " : "", b, node ? OrNone(ObjectName(node)) : skip[b] ? "(no node)" : "(no node, its own transform)",
		                skip[b] ? "left as it is" : node ? RoleWord(arm[b]) : "part given with the hands");
		if (dist >= 0.0f)
			len += snprintf(line + len, sizeof(line) - len, " %.1f from the hand", dist);
		if (len > 330 || b + 1 == count) {
			Log("rider:   %s's bones: %s", name, line);
			len = 0;
			line[0] = 0;
		}
	}
}

static void HoldRider(uintptr_t shape, uintptr_t skin, uintptr_t data, const char *name)
{
	RiderPart *p = &g_rider[g_riderCount];
	memset(p, 0, sizeof(*p));
	if (skin) {
		uintptr_t array = data + OFF_BONE_TRANSFORMS;
		uintptr_t bones = ReadPtr(array + OFF_ARRAY_ENTRIES);
		uint32_t count = Accessible(array + OFF_ARRAY_COUNT, 4, false) ? *(const uint32_t *)(array + OFF_ARRAY_COUNT) : 0;
		char why[300];
		if (!RiderSkinOk(skin, data, why, sizeof(why))) {
			Log("rider: %s can't be held (%s)", name, why);
			Refuse(shape);
			return;
		}
		uintptr_t nodes = SkinBoneNodes(skin, count);
		uintptr_t xforms = SkinBoneTransforms(skin, count, nodes);
		Replica *r = g_riderSwap ? TakeReplica(data, (int)count) : NULL;
		if (g_riderSwap && !r) {
			Log("rider: %s not held: no room for a copy of its bone data (%d copies in use)", name, g_replicaCount);
			Refuse(shape);
			return;
		}
		if (!g_riderSwap && !Accessible(bones, count * BONE_SIZE, true)) {
			Log("rider: %s not held: its bone data can't be written in place", name);
			Refuse(shape);
			return;
		}
		p->saved = (uint8_t *)malloc(count * BONE_SIZE);
		p->skip = (uint8_t *)calloc(count, 1);
		p->arm = (uint8_t *)calloc(count, 1);
		p->lastPos = (float *)calloc(count, 12);
		p->lastPosOk = false;
		if (!p->saved || !p->skip || !p->arm) {
			Log("rider: %s not held: out of memory", name);
			free(p->saved);
			free(p->skip);
			free(p->arm);
			free(p->lastPos);
			if (r)
				FreeReplica(r->obj);
			Refuse(shape);
			return;
		}
		memcpy(p->saved, (const void *)bones, count * BONE_SIZE);
		/* The data is one of our copies (test 29: the game cloned the suit's skin instance for a
		 * blood decal, our copy and all): the originals are the owning part's, and the decal is
		 * pointed back where the game left it on letting go. */
		if (IsReplica(data)) {
			RiderPart *owner = OwnerOfReplica(data);
			if (owner && owner->count == (int)count) {
				memcpy(p->saved, owner->saved, count * BONE_SIZE);
				Log("rider: %s's skin points at the copy made for %s (cloned from it): held from that shape's own data", name, owner->name);
			} else {
				Log("rider: %s's skin points at a copy of ours that no held shape owns: held from the copy as it is", name);
			}
		}
		/* A bone whose node can't be read, or whose world transform isn't a rigid one (a hidden
		 * bone scaled to 0, say), is left at its own transform (test 27: the backpack's bone 16
		 * refused the whole shape, and the rider stayed level all session). */
		int inheritedLen = 0;
		p->inherited[0] = 0;
		p->inheritedN = p->inheritedListed = 0;
		for (uint32_t b = 0; b < count; b++) {
			uintptr_t node = ((const uintptr_t *)nodes)[b];
			float N[9], n[3], sc;
			if (!node) {
				/* No node: held through the bone's own world transform if the skin carries
				 * one (its part in the arms is given once every shape is held, by where it
				 * sits against the hands); left as it is otherwise. */
				uintptr_t xf = xforms ? ((const uintptr_t *)xforms)[b] : 0;
				if (!xf || !TransformWorld(xf, N, n, &sc, NULL))
					p->skip[b] = 1;
			} else if (!Accessible(node + OFF_WORLD_ROT, 0x40, false)) {
				p->skip[b] = 1;
				Log("rider: %s's bone %u of %u: its node %p can't be read; that bone is left as it is", name, b, count, (void *)node);
			} else if (!NodeWorld(node, N, n, &sc, NULL)) {
				const float *w = (const float *)(node + OFF_WORLD_ROT);
				p->skip[b] = 1;
				Log("rider: %s's bone %u of %u ('%.32s'): its node's world transform can't be inverted, a hidden bone? (rows (%g, %g, %g) (%g, %g, %g) (%g, %g, %g), "
				    "position (%g, %g, %g), scale %g); that bone is left as it is", name, b, count, OrNone(ObjectName(node)),
				    w[0], w[1], w[2], w[4], w[5], w[6], w[8], w[9], w[10], w[12], w[13], w[14], w[15]);
			} else {
				p->arm[b] = ArmRole(ObjectName(node));
				NoteArmNode(p->arm[b], node, ObjectName(node));
				if (!p->arm[b])
					p->arm[b] = HeadRole(node);
				if (!p->arm[b])
					p->arm[b] = TorsoRole(ObjectName(node));
				if (!p->arm[b]) {
					p->arm[b] = AncestorRole(node);   /* the body's skin helpers, by their parents (test 38's pose study) */
					if (p->arm[b] && inheritedLen < (int)sizeof(p->inherited) - 60) {
						inheritedLen += snprintf(p->inherited + inheritedLen, sizeof(p->inherited) - inheritedLen, "%s%.24s with %s", inheritedLen ? ", " : "", OrNone(ObjectName(node)), RoleWord(p->arm[b]));
						p->inheritedListed++;
					}
					if (p->arm[b])
						p->inheritedN++;
				}
				if (p->arm[b] == 4 && !g_headNode && HeadName(ObjectName(node)))
					g_headNode = node;
				if (p->arm[b] == 5 && !g_torsoNode && TorsoPivotName(ObjectName(node)))
					g_torsoNode = node;
			}
		}
		/* The hands' bones are logged from SyncRider, once the hold is known to stand (test 33:
		 * the fingers stretched into spikes; a hold that waits for the skeleton logs nothing). */
		if (r) {
			memcpy(r->entries, (const void *)bones, count * BONE_SIZE);
			p->live = r->entries;
			p->replica = r->obj;
		} else {
			p->live = (uint8_t *)bones;   /* RiderSwap=0: the game's own, written in place (an A/B: NPCs in the same mesh get it too) */
			p->replica = 0;
		}
		p->original = data;
		p->nodes = nodes;
		p->xforms = xforms;
		p->count = (int)count;
		p->skin = skin;
		Retain(skin);
		Retain(shape);
		if (r) {
			Retain(r->obj);   /* the skin instance's reference to it, as the game would take one */
			*(volatile uintptr_t *)(skin + OFF_SKIN_BONE_DATA) = r->obj;
		}
	} else {
		uintptr_t parent = ReadPtr(shape + OFF_PARENT);
		if (!Accessible(shape + OFF_LOCAL_ROT, 0x40, true) || !LooksLikeTransform((const uint8_t *)(shape + OFF_LOCAL_ROT)) ||
		    !parent || !IsA(parent, RTTI_AVOBJECT) || !Accessible(parent + OFF_WORLD_ROT, 0x40, false)) {
			Refuse(shape);
			return;
		}
		p->saved = (uint8_t *)malloc(0x40);
		p->arm = (uint8_t *)calloc(1, 1);
		p->lastPos = NULL;
		p->lastPosOk = false;
		if (!p->saved || !p->arm) {
			free(p->saved);
			free(p->arm);
			Refuse(shape);
			return;
		}
		memcpy(p->saved, (const void *)(shape + OFF_LOCAL_ROT), 0x40);
		p->live = (uint8_t *)(shape + OFF_LOCAL_ROT);
		p->count = 1;
		/* Under a hand or forearm bone (the Pip-Boy's, a ring's): it turns with the bars as that bone does. */
		uintptr_t up = parent;
		for (int depth = 0; depth < 12 && up && p->arm[0] == 0; depth++) {   /* 12: the Pip-Boy's screen sits deep under the forearm (test 31) */
			p->arm[0] = ArmRole(ObjectName(up));
			if (!p->arm[0] && HeadName(ObjectName(up)))
				p->arm[0] = 4;
			if (!p->arm[0])
				p->arm[0] = TorsoRole(ObjectName(up));
			up = ReadPtr(up + OFF_PARENT);
			if (up && !IsA(up, RTTI_AVOBJECT))
				up = 0;
		}
		Retain(shape);
	}
	p->shape = shape;
	snprintf(p->name, sizeof(p->name), "%s", name ? name : "(unnamed shape)");
	g_riderCount++;
}

static void LetGoRider(int i, const char *why)
{
	RiderPart *p = &g_rider[i];
	if (p->skin && !p->replica) {
		if (Accessible((uintptr_t)p->live, (size_t)p->count * BONE_SIZE, true))
			memcpy(p->live, p->saved, (size_t)p->count * BONE_SIZE);
		Release(p->skin);
	} else if (p->skin) {
		memcpy(p->live, p->saved, (size_t)p->count * BONE_SIZE);   /* level again: anything else still pointing at the copy sees the originals */
		if (Accessible(p->skin + OFF_SKIN_BONE_DATA, 8, true) && *(const volatile uintptr_t *)(p->skin + OFF_SKIN_BONE_DATA) == p->replica) {
			*(volatile uintptr_t *)(p->skin + OFF_SKIN_BONE_DATA) = p->original;
			InterlockedDecrement((volatile LONG *)(p->replica + OFF_REFCOUNT));   /* the instance's reference, given back */
		} else {
			Log("rider: %s's skin no longer points at our bone data: left as it is (%s)", p->name, why);
		}
		FreeReplica(p->replica);
		Release(p->skin);
	} else if (Accessible((uintptr_t)p->live, 0x40, true)) {
		memcpy(p->live, p->saved, 0x3C);
	}
	Release(p->shape);
	free(p->saved);
	free(p->skip);
	free(p->arm);
	free(p->lastPos);
	g_rider[i] = g_rider[--g_riderCount];
}

/* quiet: no summary line (a hold let go to wait for the skeleton, every 0.1 s). */
static void LetGoAllRiderWhy(const char *why, bool quiet)
{
	memset(g_arm, 0, sizeof(g_arm));
	g_headNode = 0;
	g_torsoNode = 0;
	g_armLogged[0] = g_armLogged[1] = false;
	g_armsRidingLogged = false;
	int had = g_riderCount;
	while (g_riderCount)
		LetGoRider(g_riderCount - 1, why);
	if (had && !quiet) {
		Log("rider: %d shape(s) back as they were and let go (%s)", had, why);
		LogWristMax();
	}
	if (had) {
		ResetTorsoSolve();   /* held afresh, solved afresh: a knock-off, a skeleton wait (test 37); not a fast travel on the bike, which leaves the shapes held and sends no PostLoadGame (test 38: the lean is solved again after the jump instead, RearmTorsoSolve) */
		g_torsoSeqWhat = "the rider held again";   /* for the final line (review of test 40's first build: it said "the ride's start" for a hold 300 s in); a getting-off's ResetTilt makes it the ride's start again */
	}
}

static void LetGoAllRider(const char *why)
{
	LetGoAllRiderWhy(why, false);
}

/* Names, a line at a time (test 24's list was cut at 400 characters). */
static void LogNames(const char *prefix, const SkinList *list, const bool *pick, bool skinned)
{
	char line[360];
	size_t len = 0;
	int shown = 0;
	for (int j = 0; j < list->riderCount; j++) {
		if (!pick[j])
			continue;
		const char *name = list->riderName[j] && list->riderName[j][0] ? list->riderName[j] : "(unnamed)";
		char item[120];
		if (skinned) {
			uintptr_t array = list->riderData[j] + OFF_BONE_TRANSFORMS;
			uint32_t count = Accessible(array + OFF_ARRAY_COUNT, 4, false) ? *(const uint32_t *)(array + OFF_ARRAY_COUNT) : 0;
			snprintf(item, sizeof(item), "%.80s (%u bones)", name, count);
		} else {
			snprintf(item, sizeof(item), "%.80s", name);
		}
		if (len && len + strlen(item) + 2 > sizeof(line) - 1) {
			Log("%s%s", prefix, line);
			len = 0;
		}
		len += (size_t)snprintf(line + len, sizeof(line) - len, "%s%s", len ? ", " : "", item);
		shown++;
	}
	if (len)
		Log("%s%s", prefix, line);
}

/* The bike's own skin? The walk from the 3D root sees a bike shape that's found only through
 * the biped (the planted variant: no COM bind, renamed by the game) before it knows it's the
 * bike's, and offers it as the rider's; it's the bike's once the biped walk has said so. */
static bool BikeSkin(const SkinList *list, uintptr_t skin)
{
	if (!skin)
		return false;
	for (int i = 0; i < list->count; i++)
		if (list->skins[i] == skin)
			return true;
	for (int k = 0; k < g_skinCount; k++)
		if (g_skins[k].skin == skin)
			return true;
	return false;
}

static void SyncRider(uintptr_t player, const SkinList *list, bool wanted)
{
	int gone = 0;
	for (int i = g_riderCount - 1; i >= 0; i--) {
		RiderPart *p = &g_rider[i];
		bool still = false;
		for (int j = 0; wanted && j < list->riderCount && !still; j++)
			still = list->riderShape[j] == p->shape;
		if (still && BikeSkin(list, p->skin))
			still = false;   /* the bike's after all */
		if (still && p->skin) {
			/* The game may give a shape a new skin instance (a decal's, test 28), or point the
			 * instance back at its own bone data: ours again, or held again with the new one. */
			uintptr_t skinNow = *(const uintptr_t *)(p->shape + OFF_SKIN_INSTANCE);   /* the shape is ours to keep */
			if (skinNow != p->skin) {
				Log("rider: %s's skin instance was replaced by the game: held again with the new one", p->name);
				still = false;
			} else if (p->replica) {
				uintptr_t dataNow = *(const volatile uintptr_t *)(p->skin + OFF_SKIN_BONE_DATA);
				if (dataNow == p->original) {
					Retain(p->replica);
					*(volatile uintptr_t *)(p->skin + OFF_SKIN_BONE_DATA) = p->replica;
					Log("rider: the game pointed %s's skin back at its own bone data: ours again", p->name);
				} else if (dataNow != p->replica) {
					/* New bone data of the game's own: if it's a copy of our tilted entries (test
					 * 29), its entries are put level from the originals and it's the original now. */
					uintptr_t array = dataNow + OFF_BONE_TRANSFORMS;
					uintptr_t entries = dataNow && IsA(dataNow, RTTI_BONE_DATA) ? ReadPtr(array + OFF_ARRAY_ENTRIES) : 0;
					uint32_t n = entries && Accessible(array + OFF_ARRAY_COUNT, 4, false) ? *(const uint32_t *)(array + OFF_ARRAY_COUNT) : 0;
					if (entries && n == (uint32_t)p->count && Accessible(entries, n * BONE_SIZE, true) &&
					    memcmp((const void *)entries, p->live, n * BONE_SIZE) == 0) {
						memcpy((void *)entries, p->saved, n * BONE_SIZE);
						p->original = dataNow;
						Retain(p->replica);
						*(volatile uintptr_t *)(p->skin + OFF_SKIN_BONE_DATA) = p->replica;
						Log("rider: the game gave %s's skin a copy of our tilted bone data: put level, and ours again", p->name);
					} else {
						Log("rider: %s's skin points at bone data that's neither ours nor its old own: held again", p->name);
						still = false;
					}
				}
			}
		}
		if (!still) {
			LetGoRider(i, wanted ? "no longer on the rider" : "the tilt is off");
			gone++;
		}
	}
	if (gone && wanted)
		ForgetRegions();   /* something of the 3D went */
	if (gone)
		Log("rider: %d shape(s) back as they were and let go (%s), %d still held", gone, wanted ? "no longer on the rider" : "the tilt is off", g_riderCount);
	if (!wanted || g_riderBlocked || !list->riderCount || !RiderWorldOk(player))
		return;
	/* All or nothing: a skinned shape that can't be held leaves the rider level (test 24: the
	 * suit stayed level while the body under it pitched, and the rider tore). */
	for (int j = 0; j < list->riderCount; j++) {
		if (!list->riderSkin[j] || !g_riderSkinned || BikeSkin(list, list->riderSkin[j]))
			continue;
		bool held = false;
		for (int i = 0; i < g_riderCount && !held; i++)
			held = g_rider[i].shape == list->riderShape[j];
		char why[300];
		if (held || RiderSkinOk(list->riderSkin[j], list->riderData[j], why, sizeof(why)))
			continue;
		Log("rider: %s can't be held (%s): the rider stays level this ride%s", list->riderName[j] ? list->riderName[j] : "(unnamed shape)", why, AfterLoadNote());
		g_riderBlocked = true;
		LetGoAllRider("a shape of the rider can't be held");
		return;
	}
	if (list->riderOver) {
		Log("rider: more than %d shapes on the rider (%d over): the rider stays level this ride%s", MAX_RIDER, list->riderOver, AfterLoadNote());
		g_riderBlocked = true;
		LetGoAllRider("too many shapes");
		return;
	}
	if (!g_riderCount) {
		memset(g_arm, 0, sizeof(g_arm));   /* the chains are found again with the shapes */
		g_headNode = 0;
		g_torsoNode = 0;
	}
	int before = g_riderCount, skinned = 0;
	bool waited = g_holdWaitSince != 0.0f;   /* this pass is a retry of a hold that found the skeleton half built */
	bool pickSkinned[MAX_RIDER], pickPlain[MAX_RIDER];
	memset(pickSkinned, 0, sizeof(pickSkinned));
	memset(pickPlain, 0, sizeof(pickPlain));
	for (int j = 0; j < list->riderCount; j++) {
		uintptr_t shape = list->riderShape[j];
		if (g_riderCount >= MAX_RIDER)
			break;
		if (list->riderSkin[j] ? !g_riderSkinned || BikeSkin(list, list->riderSkin[j]) : !g_riderPlain)
			continue;
		bool held = false;
		for (int i = 0; i < g_riderCount && !held; i++)
			held = g_rider[i].shape == shape;
		if (held || (!list->riderSkin[j] && Refused(shape)))   /* a skinned one refused before is checked afresh above */
			continue;
		int was = g_riderCount;
		HoldRider(shape, list->riderSkin[j], list->riderData[j], list->riderName[j]);
		if (g_riderCount > was) {
			if (list->riderSkin[j]) {
				skinned++;
				pickSkinned[j] = true;
			} else {
				pickPlain[j] = true;
			}
		} else if (list->riderSkin[j]) {
			g_riderBlocked = true;   /* checked above and still not held: nothing of the rider, then */
			Log("rider: %s couldn't be held after all: the rider stays level this ride%s", list->riderName[j] ? list->riderName[j] : "(unnamed shape)", AfterLoadNote());
			LetGoAllRider("a shape of the rider can't be held");
			return;
		}
	}
	/* Test 35: the first hold right after a save load ran against a half-built skeleton (the
	 * shoulders missing from both arms' chains, 49 of the suit's bones without a node), which
	 * the game had replaced 0.1 s later. A side whose hand was found but whose shoulder or
	 * elbow wasn't is an arm still being built (a side with no hand at all is a skin without
	 * arms): nothing of the rider is held for now, and the hold is tried again every sync, for
	 * a second at most; then it's held as it is. A complete hold ends the wait. */
	if (skinned) {
		char missing[120] = "";
		int ml = 0;
		for (int side = 0; side < 2; side++) {
			if (!g_arm[side].hand || (g_arm[side].upper && g_arm[side].elbow))
				continue;
			if (!g_arm[side].upper)
				ml += snprintf(missing + ml, sizeof(missing) - ml, "%s%s shoulder missing", ml ? ", " : "", side ? "right" : "left");
			if (!g_arm[side].elbow)
				ml += snprintf(missing + ml, sizeof(missing) - ml, "%s%s elbow missing", ml ? ", " : "", side ? "right" : "left");
		}
		if (ml && !g_holdWaitExpired) {
			if (!waited) {
				g_holdWaitSince = (float)g_clock > 0.0f ? (float)g_clock : 1e-6f;
				Log("rider: the skeleton isn't complete yet (%s): nothing of the rider held; tried again every 0.1 s, for a second at most", missing);
			}
			if ((float)g_clock - g_holdWaitSince < 1.0f) {
				LetGoAllRiderWhy("the skeleton isn't complete yet", true);
				return;
			}
			Log("rider: the arms' chains are still incomplete after a second: held as they are (and not waited for again this ride)%s", AfterLoadNote());
			g_holdWaitExpired = true;
		}
		g_holdWaitSince = 0.0f;
		for (int i = before; i < g_riderCount; i++) {   /* the hands' bones and the bones given their parents' part, once per hold that stands (review: a hold waiting for the skeleton logged the latter at every retry) */
			if (g_rider[i].skin && NameHas(g_rider[i].name, "hand"))
				LogHandBones(g_rider[i].name, (const uintptr_t *)g_rider[i].nodes, (const uintptr_t *)g_rider[i].xforms, g_rider[i].skip, g_rider[i].arm, g_rider[i].count);
			if (g_rider[i].inheritedN)
				Log("rider: %s: %d bone%s with no part by name take%s %s parent's part (test 38's pose study: the body's skin helpers were left where the clips put them, a hump on the upper back): %s%s",
				    g_rider[i].name, g_rider[i].inheritedN, g_rider[i].inheritedN == 1 ? "" : "s", g_rider[i].inheritedN == 1 ? "s" : "", g_rider[i].inheritedN == 1 ? "its" : "their",
				    g_rider[i].inherited, g_rider[i].inheritedListed < g_rider[i].inheritedN ? ", ..." : "");
		}
	}
	if (g_riderCount != before) {
		Log("rider: holding %d more shape(s) of the rider to tilt with the bike (%d skinned, %d plain), %d in all", g_riderCount - before,
		    skinned, g_riderCount - before - skinned, g_riderCount);
		if (skinned)
			LogNames("rider:   skinned: ", list, pickSkinned, true);
		if (g_riderCount - before - skinned)
			LogNames("rider:   plain: ", list, pickPlain, false);
		NodelessRoles();
		Log("rider:   the arms' chains: left shoulder %s, elbow %s, hand %s; right shoulder %s, elbow %s, hand %s; the head %s; the spine's joint %s",
		    g_arm[0].upper ? "found" : "missing", g_arm[0].elbow ? "found" : "missing", g_arm[0].hand ? "found" : "missing",
		    g_arm[1].upper ? "found" : "missing", g_arm[1].elbow ? "found" : "missing", g_arm[1].hand ? "found" : "missing", g_headNode ? "found" : "missing",
		    g_torsoNode ? "found" : "missing");
		char roles[480] = "";
		int rl = 0;
		for (int i = 0; i < g_riderCount && rl < (int)sizeof(roles) - 70; i++)
			if (!g_rider[i].skin && g_rider[i].arm[0])
				rl += snprintf(roles + rl, sizeof(roles) - rl, "%s%s (%s)", rl ? ", " : "", g_rider[i].name, RoleWord(g_rider[i].arm[0]));
		if (rl)
			Log("rider:   plain shapes moving with the arms or the head: %s", roles);
	}
}

/* Bones without a node (test 34: the hands' fingers and the wrist end of the forearm) get
 * their part in the arms by where they sit against the hands' nodes: within 30 of a hand and
 * beyond it (away from the elbow), a finger: the hand's part; behind it along the forearm,
 * within the forearm's length, the forearm's; anything else is carried with the tilt alone. */
static void NodelessRoles(void)
{
	for (int i = 0; i < g_riderCount; i++) {
		RiderPart *p = &g_rider[i];
		if (!p->skin || !p->xforms)
			continue;
		int hand[2] = { 0, 0 }, fore = 0, alone = 0, total = 0;
		for (int b = 0; b < p->count; b++) {
			if (p->skip[b] || ((const uintptr_t *)p->nodes)[b])
				continue;
			float N[9], n[3], sc;
			if (!TransformWorld(((const uintptr_t *)p->xforms)[b], N, n, &sc, NULL)) {
				p->skip[b] = 1;
				memcpy(p->live + (size_t)b * BONE_SIZE, p->saved + (size_t)b * BONE_SIZE, BONE_SIZE);   /* its own entry again */
				continue;
			}
			total++;
			uint8_t role = 0;
			float best = 1e9f;
			for (int side = 0; side < 2; side++) {
				float Nh[9], H[3], E[3], sh;
				if (!g_arm[side].hand || !NodeWorld(g_arm[side].hand, Nh, H, &sh, NULL))
					continue;
				float d = Dist3f(n, H);
				if (d >= best)
					continue;
				float along = 0.0f, L2 = 0.0f;
				if (g_arm[side].elbow && NodeWorld(g_arm[side].elbow, Nh, E, &sh, NULL)) {
					float u[3] = { H[0] - E[0], H[1] - E[1], H[2] - E[2] };
					L2 = sqrtf(u[0] * u[0] + u[1] * u[1] + u[2] * u[2]);
					if (L2 > 1.0f)
						along = ((n[0] - H[0]) * u[0] + (n[1] - H[1]) * u[1] + (n[2] - H[2]) * u[2]) / L2;   /* + beyond the hand, - back towards the elbow */
				}
				uint8_t r = 0;
				if (d < 30.0f && along >= -3.0f)
					r = (uint8_t)(3 | (side ? 0x10 : 0));
				else if (along < 0.0f && -along <= L2 + 5.0f && d < L2 + 10.0f)
					r = (uint8_t)(2 | (side ? 0x10 : 0));
				if (r) {
					best = d;
					role = r;
				}
			}
			p->arm[b] = role;
			if ((role & 0xF) == 3)
				hand[(role & 0x10) ? 1 : 0]++;
			else if ((role & 0xF) == 2)
				fore++;
			else
				alone++;
		}
		if (total)
			Log("rider: %s: %d bones without a node, held through their own transforms: %d with the left hand, %d with the right, %d with a forearm, %d carried with the tilt alone",
			    p->name, total, hand[0], hand[1], fore, alone);
	}
}

static void RestoreRider(void)
{
	for (int i = 0; i < g_riderCount; i++) {
		RiderPart *p = &g_rider[i];
		if (p->skin && (p->replica || Accessible((uintptr_t)p->live, (size_t)p->count * BONE_SIZE, true)))
			memcpy(p->live, p->saved, (size_t)p->count * BONE_SIZE);
		else if (!p->skin && Accessible((uintptr_t)p->live, 0x40, true))
			memcpy(p->live, p->saved, 0x3C);
	}
}

/* Every frame, after the bike: the rider's shapes carried by the same tilt R about the same
 * pivot P (the bike's own space), taken to world through the bike's bind and bone. */
static void FrameRider(bool tilt, const float R[9], const float P[3])
{
	if (!g_riderCount)
		return;
	HeldSkin *bike = NULL;
	for (int k = 0; k < g_skinCount; k++)
		if (g_skins[k].node && (!bike || (bike->role != ROLE_NONE && g_skins[k].role == ROLE_NONE)))
			bike = &g_skins[k];
	float Nb[9], nb[3], sb, Nbi[9];
	bool bikeOk = bike && NodeWorld(bike->node, Nb, nb, &sb, Nbi);
	g_riderBikeOk = bikeOk;   /* for the look after a load */
	/* The arm chains' move this frame, for the lean solve's guard (test 37): measured whether
	 * or not the rider is written, so the first solve has a settled frame behind it. */
	g_armMoveOk = bikeOk && ArmChainMove(nb, &g_armMoveNow);
	/* The arms' riding line waits for the speed over 300 for a second (test 41). */
	if (g_speed > 300.0f) {
		if (g_armsFastSince < 0.0f)
			g_armsFastSince = (float)g_clock;
	} else {
		g_armsFastSince = -1.0f;
	}
	/* Level: the originals are right and nothing need be written. With a deadband (test 26: the
	 * applied pitch wobbles a degree on ordinary ground): level under half a degree, tilted
	 * again over one. The bars turned (the hands follow them) or the bike lifted count too. */
	if (g_riderLevel ? g_tiltNow > 1.0f : g_tiltNow < 0.5f)
		g_riderLevel = !g_riderLevel;
	/* The upper body (test 32: the arms were locked straight at rest, the grips at the arms'
	 * full reach, so a turn put the far grip out of reach): leaned forward about the lowest
	 * spine bone's joint by TorsoLean degrees, or, by default, by enough to bring the grips to
	 * ArmReach of the reach (solved once a ride, as soon as a chain is found), turned
	 * toward the far grip by TorsoTwist of the bars' angle and leaned into the turn by
	 * TorsoSideLean of it (test 36: the inner arm folded tight at full lock with the body
	 * neither leaning nor shifting sideways); the arms are solved from the moved shoulders
	 * and the hands stay on the grips. With it the rider is written every frame, level or
	 * not. */
	if (g_riderHands && g_partsOk && g_torsoNode && (float)g_clock - g_rideStartClock >= g_torsoSolveFrom && (float)g_clock >= g_torsoRetryAt &&
	    (!g_torsoLeanSet || (!g_torsoFinal && (float)g_clock - g_torsoSolvedAt >= 0.5f)))
		SolveTorsoLean();   /* TorsoSolveFrom in (1.3 s), and again every half second till final, the best reading kept: the pose settles (test 33's first ride solved 15 deg at 100%; test 39: the first reading at 95% after a jump kept for good); not while the arms move or the grips are short of the riding pose's reach (test 37); taken as it comes, every half second till the riding pose is there (test 38) */
	bool torso = g_riderHands && g_partsOk && g_torsoNode && g_torsoLeanSet && (g_torsoLean > 0.05f || ((g_torsoTwist > 0.0f || g_torsoSideLean > 0.0f) && fabsf(g_barNow) > 0.3f));
	bool hands = g_riderHands && g_partsOk && (fabsf(g_barNow) > 0.3f || torso);
	bool level = g_riderLevel && !hands && fabsf(g_liftNow) < 0.5f;
	bool ready = (tilt || hands) && g_riderTilt && g_riderWrite && !level && bikeOk;
	g_riderApplied = ready;
	if (!ready) {
		if (tilt && g_riderTilt && g_skinCount && !level && !bike && !g_riderBoneWarned) {
			g_riderBoneWarned = true;
			Log("rider: the bike's bone can't be read (its skin instance doesn't list it where expected): the rider stays level%s", AfterLoadNote());
		}
		if (!g_riderIdle) {
			RestoreRider();
			g_riderIdle = true;
		}
		return;
	}
	g_riderIdle = false;
	/* The bike's own map, x -> R (x - P) + P + lift (its own space), taken to world through
	 * the bind (A, t) and the bone (Nb, nb, sb): z -> Rw z + tw. */
	float A[9], t[3], At[9], AP[3], Pbone[3], T9[9], ARA[9], Pw[3], Rw[9], NP[3], tw[3], liftBike[3] = { 0.0f, 0.0f, g_liftNow }, liftW[3], AL[3];
	ReadRot((const float *)(bike->original[0] + OFF_BONE_ROT), A);
	memcpy(t, bike->original[0] + OFF_BONE_POS, 12);
	Transpose3(A, At);
	MulV(A, P, AP);
	for (int i = 0; i < 3; i++)
		Pbone[i] = AP[i] + t[i];
	MulV(Nb, Pbone, NP);
	for (int i = 0; i < 3; i++)
		Pw[i] = sb * NP[i] + nb[i];
	Mul3(A, R, T9);
	Mul3(T9, At, ARA);
	Mul3(Nb, ARA, T9);
	Mul3(T9, Nbi, Rw);
	MulV(A, liftBike, AL);
	MulV(Nb, AL, liftW);
	float RwPw[3];
	MulV(Rw, Pw, RwPw);
	for (int i = 0; i < 3; i++)
		tw[i] = Pw[i] - RwPw[i] + sb * liftW[i];
	memcpy(g_riderPivot, Pw, sizeof(g_riderPivot));
	/* The bars' turn, for the hands: about the steering axis through the steering point, in
	 * world, by the bar angle (or a part of it, nearer the elbow), before the tilt. */
	float axisW[3] = { 0, 0, 0 }, qW[3] = { 0, 0, 0 };
	if (hands) {
		float Aa[3], Ap[3], Bp[3], NBp[3];
		MulV(A, g_steerAxis, Aa);
		MulV(Nb, Aa, axisW);
		float len = sqrtf(axisW[0] * axisW[0] + axisW[1] * axisW[1] + axisW[2] * axisW[2]);
		if (len > 0.0001f)
			for (int i = 0; i < 3; i++)
				axisW[i] /= len;
		MulV(A, g_steerPoint, Ap);
		for (int i = 0; i < 3; i++)
			Bp[i] = Ap[i] + t[i];
		MulV(Nb, Bp, NBp);
		for (int i = 0; i < 3; i++)
			qW[i] = sb * NBp[i] + nb[i];
	}
	/* The upper body's map (world, before the tilt): the lean about the rider's sideways axis,
	 * the side lean about the forward axis and the twist about the vertical, all through the
	 * spine's joint, the lean first. The sense of each is checked on a vector rather than
	 * assumed of AxisRotation. */
	float Tr[9] = { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, tt[3] = { 0, 0, 0 }, Rt[9] = { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, pivot[3] = { 0, 0, 0 };
	if (torso) {
		float Nt[9], st, Rl[9], Rs[9], Rsl[9], probe[3], Tp[3];
		float rightW[3] = { cosf(g_headingNow), -sinf(g_headingNow), 0.0f }, fwdW[3] = { sinf(g_headingNow), cosf(g_headingNow), 0.0f }, upW[3] = { 0, 0, 1 };
		if (!NodeWorld(g_torsoNode, Nt, pivot, &st, NULL)) {
			torso = false;
		} else {
			AxisRotation(rightW, g_torsoLean / 57.29578f, Rl);
			MulV(Rl, upW, probe);
			if (probe[0] * fwdW[0] + probe[1] * fwdW[1] < 0.0f)   /* that leant back: the other way */
				AxisRotation(rightW, -g_torsoLean / 57.29578f, Rl);
			float twist = g_torsoTwist * g_barNow / 57.29578f;
			AxisRotation(upW, twist, Rt);
			MulV(Rt, fwdW, probe);
			if (twist != 0.0f && (probe[0] * rightW[0] + probe[1] * rightW[1]) * g_barNow > 0.0f)   /* the chest turns the way the bars do (+ left) */
				AxisRotation(upW, -twist, Rt);
			/* The side lean (test 36): the chest's top toward the inner grip, the side the bars turn to. */
			float side = g_torsoSideLean * g_barNow / 57.29578f;
			AxisRotation(fwdW, side, Rs);
			MulV(Rs, upW, probe);
			if (side != 0.0f && (probe[0] * rightW[0] + probe[1] * rightW[1]) * g_barNow > 0.0f)   /* the top went to the outside: the other way */
				AxisRotation(fwdW, -side, Rs);
			Mul3(Rs, Rl, Rsl);
			Mul3(Rt, Rsl, Tr);
			MulV(Tr, pivot, Tp);
			for (int i = 0; i < 3; i++)
				tt[i] = pivot[i] - Tp[i];
		}
	}
	/* The bars' turn about that axis, and each arm's solve (the shoulder goes with the upper
	 * body, the elbow swings, the wrist lands on the turned grip). */
	float Qb[9] = { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, qb[3] = { 0, 0, 0 };
	ArmMap arm[4];
	for (int i = 0; i < 4; i++)
		arm[i].ok = arm[i].rolled = false;
	if (torso) {
		memcpy(arm[3].R1, Tr, sizeof(Tr));
		memcpy(arm[3].t1, tt, sizeof(tt));
		arm[3].ok = true;
	}
	if (hands) {
		float Qq[3];
		AxisRotation(axisW, g_barNow / 57.29578f, Qb);
		MulV(Qb, qW, Qq);
		for (int i = 0; i < 3; i++)
			qb[i] = qW[i] - Qq[i];
		bool steady = g_armMoveOk && g_armMoveNow < 5.0f && (float)g_clock - g_rideStartClock >= 1.0f && (float)g_clock - g_jumpAt >= 1.0f;   /* a frame the wrist's max may come from (test 39) */
		for (int side = 0; side < 2; side++) {
			ArmMap *am = &arm[side];
			/* The elbow's way (ArmPole, the left mirrored in x; the inside arm's faded toward
			 * ArmPoleTurn as the bars turn, test 41), taken to world through the bike's bind and
			 * bone like the grip's axis below; none with ArmPole=0,0,0. */
			float poleS[3], fade = ArmPoleNow(side, poleS);
			float poleM[3] = { side ? poleS[0] : -poleS[0], poleS[1], poleS[2] }, Apole[3], poleW[3];
			MulV(A, poleM, Apole);
			MulV(Nb, Apole, poleW);
			float lp = sqrtf(poleW[0] * poleW[0] + poleW[1] * poleW[1] + poleW[2] * poleW[2]);
			bool havePole = lp > 0.001f;
			if (havePole)
				for (int i = 0; i < 3; i++)
					poleW[i] /= lp;
			SolveArm(&g_arm[side], Qb, qb, Tr, tt, torso, havePole ? poleW : NULL, NULL, am);
			if (!am->ok)
				continue;
			/* The grip's centre G (Grip in the parts file, the left mirrored in x), in world before
			 * the bars' turn like the clips' wrist (am->wrist): the wrist roll's pivot, and what the
			 * clips' wrist is measured from for the wrist's max below. */
			float gripW[3] = { 0.0f, 0.0f, 0.0f };
			if (g_gripOk) {
				float Gm[3] = { side ? g_grip[0] : -g_grip[0], g_grip[1], g_grip[2] }, AG[3], BG[3], NBG[3];
				MulV(A, Gm, AG);
				for (int i = 0; i < 3; i++)
					BG[i] = AG[i] + t[i];
				MulV(Nb, BG, NBG);
				for (int i = 0; i < 3; i++)
					gripW[i] = sb * NBG[i] + nb[i];
			}
			if (g_wristRoll > 0.0f) {
				/* The wrist roll (test 37: 25 deg of wrist turn at the straight bars once the lean
				 * and the re-solved elbow had swung the forearm, the hand keeping the clips'
				 * orientation turned with the bars): the hand rolled round the grip's axis (the
				 * bike's lateral axis, outward on each side, through the bike's bone; the bars'
				 * turn Qb goes in front), so the palm stays on the round grip and the fingers stay
				 * wrapped. Test 39: "cat paw", the fists bent down at the wrist. The roll was the
				 * forearm's own twist about that axis (Qb^T R2), which kept whatever bend the clips
				 * gave the hand against the forearm, and the clips gave the hand a fixed frame,
				 * the fingers 39 deg below level whatever the forearm did: with ArmReach 0.80 and
				 * ArmPole the forearms run about level, and the bend showed (logged at rest: the
				 * wrist turned 15 to 17 deg, rolled 10 to 17). Now the roll is the one that lays
				 * the hand's long axis (the hand's joint to the middle finger's knuckle,
				 * g_handAxis, through the hand's node) along the forearm as seen along the grip's
				 * axis (both projected on the plane normal to it; the forearm the solved elbow to
				 * the wrist the roll puts there), HandPitch degrees above it (the knuckles up: about
				 * the bike's +x on either side, so the left's angle about its outward axis, -x, is
				 * negated), WristRoll of the way (the tester's suggestion). The pivot is the grip's
				 * centre G (Grip in the parts file, taken to world like the steering point; test
				 * 38: it was the hand's node, 6.5 units from the grip's centre, so the palm's grip
				 * point swung off the bar): the wrist goes to W' = G + Rg (W - G), the arm is
				 * solved again to it (the hand's target moved by Qb (W' - W)), the angle read off
				 * that forearm, and so on, a secant step on the angle still to go each pass (the
				 * wrist's swing turns the forearm back a little: in the clips each plain pass
				 * leaves about a seventh, in the harness about a quarter), till it is within 0.2
				 * deg, six passes at most, the pass nearest kept: its forearm the one written and
				 * its roll the hand's, so they meet at the wrist. The hand's map is Qb Rg x + Qb (G
				 * - Rg G) + qb, which keeps G on the turned grip. Without a Grip the pivot is the
				 * hand's node and the wrist stays where it is: one reading does. The wrist's turn
				 * from the clips' pose (the hand's map against the forearm's) is what the log
				 * carries. */
				float ex[3] = { side ? 1.0f : -1.0f, 0.0f, 0.0f }, Ae[3], gb[3], Qbt[9], Rg[9], RgP[3], QW[3], gripPivot[3], Nh[9], hn[3], hs, hw[3], fq[3], alpha;
				MulV(A, ex, Ae);
				MulV(Nb, Ae, gb);
				float lg = sqrtf(gb[0] * gb[0] + gb[1] * gb[1] + gb[2] * gb[2]);
				bool aligned = false;
				if (lg > 0.0001f && NodeWorld(g_arm[side].hand, Nh, hn, &hs, NULL)) {
					for (int i = 0; i < 3; i++)
						gb[i] /= lg;
					MulV(Nh, g_handAxis[side], hw);   /* the clips' hand's long axis, world */
					Transpose3(Qb, Qbt);
					MulV(Qbt, am->fore, fq);          /* the forearm seen from the turned grip */
					aligned = AngleAbout(hw, fq, gb, &alpha);
				}
				if (aligned) {
					float pitch = (side ? g_handPitch : -g_handPitch) / 57.29578f;   /* about gb */
					float theta = g_wristRoll * (alpha + pitch);
					if (g_gripOk) {
						float dW[3], RdW[3], toff[3];
						memcpy(gripPivot, gripW, sizeof(gripPivot));
						float reach0 = am->reach;   /* the grip's distance from the shoulder, for the log: the passes below aim at the rolled wrist, a unit or two off it (review) */
						ArmMap best = *am;          /* the pass nearest its own reading: none rolled yet, the angle still to go the whole of theta */
						float bestTheta = 0.0f, bestLeft = fabsf(theta), thPrev = 0.0f, leftPrev = theta;
						for (int pass = 0; pass < 6 && bestLeft >= 0.0035f; pass++) {
							ArmMap again;
							AxisRotation(gb, theta, Rg);
							for (int i = 0; i < 3; i++)
								dW[i] = am->wrist[i] - gripPivot[i];
							MulV(Rg, dW, RdW);
							for (int i = 0; i < 3; i++)
								RdW[i] = gripPivot[i] + RdW[i] - am->wrist[i];   /* W' - W */
							MulV(Qb, RdW, toff);
							if (!SolveArm(&g_arm[side], Qb, qb, Tr, tt, torso, havePole ? poleW : NULL, toff, &again))
								break;
							MulV(Qbt, again.fore, fq);
							if (!AngleAbout(hw, fq, gb, &alpha))
								break;
							float left = g_wristRoll * (alpha + pitch) - theta;   /* the roll still to go by this pass's forearm */
							if (fabsf(left) < bestLeft) {
								best = again;
								bestTheta = theta;
								bestLeft = fabsf(left);
							}
							float slope = (left - leftPrev) / (theta - thPrev), step = left;
							if (slope < -0.05f) {   /* the secant: where the angle still to go comes to 0 */
								step = -left / slope;
								if (fabsf(step) > 3.0f * fabsf(left))
									step = step > 0.0f ? 3.0f * fabsf(left) : -3.0f * fabsf(left);
							}
							thPrev = theta;
							leftPrev = left;
							theta += step;
						}
						*am = best;
						theta = bestTheta;
						am->reach = reach0;
					} else {
						memcpy(gripPivot, am->wrist, sizeof(gripPivot));
					}
					AxisRotation(gb, theta, Rg);
					Mul3(Qb, Rg, am->Rh);
					MulV(Rg, gripPivot, RgP);
					for (int i = 0; i < 3; i++)
						RgP[i] = gripPivot[i] - RgP[i];
					MulV(Qb, RgP, QW);
					for (int i = 0; i < 3; i++)
						am->th[i] = QW[i] + qb[i];
					am->roll = theta * 57.29578f;
					am->rolled = true;
					/* The hand's axis against the forearm's line as written, the knuckles-up sense. */
					MulV(Qbt, am->fore, fq);
					float after = AngleAbout(hw, fq, gb, &alpha) ? (theta - alpha) * 57.29578f : 0.0f;
					am->handUp = side ? after : -after;
				}
			}
			float wrist = WristTurn(am->R2, am->rolled ? am->Rh : Qb), reachShare = am->reach / (am->L1 + am->L2) * 100.0f, roll = am->rolled ? am->roll : 0.0f;
			am->fade = fade;   /* set here: the roll's passes above copy in a fresh solve */
			am->turn = wrist;
			/* The ride's largest, logged at its end, from the steady frames alone (test 39: the
			 * ride that ended in a fast travel into Diamond City logged 136.7 deg at 101% of the
			 * reach and 161.0 at 116%, rolled 94.4 and -131.4: menu or loading frames): the arm
			 * chains measured and not on the move (under 5 a frame), the grip at 50 to 103% of
			 * the reach, and a second or more from the ride's start and from a jump of the player.
			 * Test 40: and the clips holding the hand at the bars, their wrist (the hand's node as
			 * they pose it) within 12 units of the grip's centre, both turned with the bars by the
			 * same map, so it is their distance before it. The riding clips put the wrist 6.5 from
			 * it (6 along the fingers, 2.5 to the back of the hand); the Pip-Boy's raise moves it
			 * tens of units off (test 37: the arm bones 40.7 in a frame), and a loading frame's
			 * pose likewise: in test 39 the Pip-Boy's map was open for the fast travel, 01:41:00
			 * to 01:41:14, the arms still for seconds at a time, and the left's 136.7 deg came at
			 * 101% of the reach, inside the band (the rides' own maxima read 66 to 102%, the last
			 * ride's 39.3 at 102% a real one). Without a Grip line there is no centre to measure
			 * from: the other gates alone. */
			bool atBars = !g_gripOk || Dist3f(am->wrist, gripW) <= 12.0f;
			if (steady && atBars && reachShare >= 50.0f && reachShare <= 103.0f && wrist > g_wristMax[side]) {
				g_wristMax[side] = wrist;
				g_wristMaxBar[side] = g_barNow;
				g_wristMaxReach[side] = reachShare;
				g_wristMaxRoll[side] = roll;
				g_wristMaxFade[side] = fade;
			}
			if (!g_armLogged[side]) {
				char rolled[200], figures[320];   /* RollWords' longest, WristRoll under 1 and every figure at its widest, is 176 (review of test 40's first build: 160 cut it, at 161 to 169); ArmFigureWords' about 250 at its widest */
				g_armLogged[side] = true;
				RollWords(am, rolled, sizeof(rolled));
				ArmFigureWords(am, side, At, Nbi, poleM, figures, sizeof(figures));
				Log("rider: the %s arm solved (the bars %.1f deg, the upper body %.1f deg forward): upper arm %.1f, forearm %.1f, the grip %.1f from the shoulder (%.0f%% of the reach), the elbow moved %.1f, the wrist turned %.1f deg from the clips' pose, %s; %s",
				    side ? "right" : "left", g_barNow, torso ? g_torsoLean : 0.0f, am->L1, am->L2, am->reach, reachShare, am->elbowMove, wrist, rolled, figures);
			}
			memcpy(am->pole, poleM, sizeof(poleM));
		}
		/* The arms riding (test 41): the first solve logged above comes at getting on, the idle
		 * clip's pose, where the tester's sketches are of the riding one (the run clip in the
		 * video). Once a hold, at speed (over 300 for a second), the bars straight (within 1
		 * deg), the arms still (under 5 a frame) and the lean final: both arms' figures as the
		 * arm line has them, the wrist's turn and the hand's roll. */
		if (!g_armsRidingLogged && (arm[0].ok || arm[1].ok) && g_armsFastSince >= 0.0f && (float)g_clock - g_armsFastSince >= 1.0f && fabsf(g_barNow) <= 1.0f &&
		    g_armMoveOk && g_armMoveNow < 5.0f && g_torsoFinal) {
			char words[2][420];
			g_armsRidingLogged = true;
			for (int side = 0; side < 2; side++) {
				ArmMap *am = &arm[side];
				if (!am->ok) {
					snprintf(words[side], sizeof(words[side]), "the %s arm not solved", side ? "right" : "left");
					continue;
				}
				char figures[320];
				ArmFigureWords(am, side, At, Nbi, am->pole, figures, sizeof(figures));
				snprintf(words[side], sizeof(words[side]), "the %s arm: %s, the wrist turned %.1f deg from the clips' pose, the hand rolled %.1f round the grip", side ? "right" : "left", figures, am->turn,
				         am->rolled ? am->roll : 0.0f);
			}
			Log("rider: the arms riding (%.0f a second for %.1f s, the bars %.1f deg, the upper body %.1f deg forward%s): %s; %s", g_speed, (float)g_clock - g_armsFastSince, g_barNow, torso ? g_torsoLean : 0.0f,
			    AfterLoadNote(), words[0], words[1]);
		}
	}
	/* The head: its joint goes where the upper body's lean, side lean and twist put it, turned
	 * with the twist but neither pitched with the lean nor rolled with the side lean (the rider
	 * keeps the head up and level), and, with HeadLevel
	 * (test 31's wish), turned back by the bike's roll about that joint (the face, the eyes, a
	 * helmet with it), before the tilt; the pitch still goes with the bike. */
	bool levelHead = g_headLevel && fabsf(g_rollNow) > 0.3f;
	if (g_headNode && (torso || levelHead)) {
		float Nh[9], hp[3], sh, fwd[3] = { sinf(g_headingNow), cosf(g_headingNow), 0.0f }, Rp[3], hp2[3], Th[3];
		if (NodeWorld(g_headNode, Nh, hp, &sh, NULL)) {
			float Rh[9] = { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, th[3] = { 0, 0, 0 };
			MulV(Tr, hp, Th);
			for (int i = 0; i < 3; i++)
				hp2[i] = Th[i] + tt[i];   /* the joint, moved with the upper body */
			if (torso) {
				memcpy(Rh, Rt, sizeof(Rh));
				MulV(Rt, hp, Rp);
				for (int i = 0; i < 3; i++)
					th[i] = hp2[i] - Rp[i];
			}
			if (levelHead) {
				float Rl2[9], tl[3], Rr[9], tr[3];
				AxisRotation(fwd, -g_rollNow / 57.29578f, Rl2);
				MulV(Rl2, hp2, Rp);
				for (int i = 0; i < 3; i++)
					tl[i] = hp2[i] - Rp[i];
				Compose(Rl2, tl, Rh, th, Rr, tr);
				memcpy(Rh, Rr, sizeof(Rh));
				memcpy(th, tr, sizeof(th));
			}
			memcpy(arm[2].R1, Rh, sizeof(Rh));
			memcpy(arm[2].t1, th, sizeof(th));
			arm[2].ok = true;
		}
	}
	for (int i = 0; i < g_riderCount; i++) {
		RiderPart *p = &g_rider[i];
		float N[9], n[3], s, Ni[9], C[9], c[3];
		if (p->skin) {
			for (int b = 0; b < p->count; b++) {
				if (p->skip[b])
					continue;   /* never written: still its own */
				uintptr_t node = ((const uintptr_t *)p->nodes)[b];
				const uint8_t *saved = p->saved + (size_t)b * BONE_SIZE;
				uint8_t *live = p->live + (size_t)b * BONE_SIZE;
				if (!BoneWorld((const uintptr_t *)p->nodes, (const uintptr_t *)p->xforms, b, N, n, &s, Ni)) {
					memcpy(live, saved, BONE_SIZE);
					continue;
				}
				if (p->lastPos) {   /* the arm bones' biggest move between frames, relative to the bike's bone (test 33; test 34: the bike's own motion swamped it) */
					float *lp = p->lastPos + 3 * b, rel[3] = { n[0] - nb[0], n[1] - nb[1], n[2] - nb[2] };
					int kind = p->arm[b] & 0xF;
					if (p->lastPosOk && kind >= 1 && kind <= 3) {
						float dj = Dist3f(rel, lp);
						if (dj > g_jumpMax) {
							g_jumpMax = dj;
							snprintf(g_jumpName, sizeof(g_jumpName), "%.24s's %s%.32s", p->name, node ? "" : "nodeless bone ", node ? OrNone(ObjectName(node)) : "");
						}
					}
					memcpy(lp, rel, 12);
				}
				float Qa[9], qa[3], R2[9], t2[3];
				if (ArmMapFor(p->arm[b], hands, arm, Qb, qb, axisW, qW, Qa, qa)) {
					Compose(Rw, tw, Qa, qa, R2, t2);
					Correction(N, Ni, n, s, R2, t2, C, c);
				} else {
					Correction(N, Ni, n, s, Rw, tw, C, c);
				}
				PutInFront(saved, live, OFF_BONE_ROT, OFF_BONE_POS, C, c);
				/* The culling sphere (bone space) goes to C centre + c: grown by the move. */
				const float *centre = (const float *)saved;
				float moved[3], radius = *(const float *)(saved + OFF_BONE_RADIUS);
				MulV(C, centre, moved);
				float dx = moved[0] + c[0] - centre[0], dy = moved[1] + c[1] - centre[1], dz = moved[2] + c[2] - centre[2];
				*(float *)(live + OFF_BONE_RADIUS) = radius > 0.0f ? radius + sqrtf(dx * dx + dy * dy + dz * dz) : radius;   /* an empty sphere stays empty */
			}
			p->lastPosOk = true;
		} else {
			uintptr_t parent = *(const uintptr_t *)(p->shape + OFF_PARENT);   /* the shape is ours to keep: readable */
			if (!NodeWorld(parent, N, n, &s, Ni)) {
				memcpy(p->live, p->saved, 0x3C);
				continue;
			}
			float Qa[9], qa[3], R2[9], t2[3];
			if (ArmMapFor(p->arm[0], hands, arm, Qb, qb, axisW, qW, Qa, qa)) {
				Compose(Rw, tw, Qa, qa, R2, t2);
				Correction(N, Ni, n, s, R2, t2, C, c);
			} else {
				Correction(N, Ni, n, s, Rw, tw, C, c);
			}
			PutInFront(p->saved, p->live, 0, 0x30, C, c);
		}
	}
}

/* The lens in the world, with the bars' turn and the tilt (M, m: the bar assembly's map in the
 * bike's space), through the bike's bind and bone, and the frame to put a light node in: the
 * beam (the lamp's axis dipped Pitch degrees) along the node's BeamAxis, up kept near the
 * bike's, a right-handed set whichever axis the beam is. */
static bool LensWorld(const HeldSkin *bike, const float Nb[9], const float nb[3], float sb, const float M[9], const float m[3], float w[3], float W[9])
{
	float A[9], t[3], L[3], AL[3], bone[3], Nbone[3];
	ReadRot((const float *)(bike->original[0] + OFF_BONE_ROT), A);
	memcpy(t, bike->original[0] + OFF_BONE_POS, 12);
	MulV(M, g_lampPoint, L);
	for (int k = 0; k < 3; k++)
		L[k] += m[k];
	MulV(A, L, AL);
	for (int k = 0; k < 3; k++)
		bone[k] = AL[k] + t[k];
	MulV(Nb, bone, Nbone);
	for (int k = 0; k < 3; k++)
		w[k] = sb * Nbone[k] + nb[k];
	static const float xAxis[3] = { 1.0f, 0.0f, 0.0f };
	float Qp[9], f[3], u[3] = { 0.0f, 0.0f, 1.0f }, r[3], F[9], MF[9], AMF[9];
	AxisRotation(xAxis, -g_lampPitch / 57.29578f, Qp);
	MulV(Qp, g_lampAxis, f);
	float fl = sqrtf(f[0] * f[0] + f[1] * f[1] + f[2] * f[2]);
	for (int k = 0; k < 3; k++)
		f[k] /= fl > 0.0001f ? fl : 1.0f;
	r[0] = f[1] * u[2] - f[2] * u[1];
	r[1] = f[2] * u[0] - f[0] * u[2];
	r[2] = f[0] * u[1] - f[1] * u[0];   /* right = forward x up */
	float rl = sqrtf(r[0] * r[0] + r[1] * r[1] + r[2] * r[2]);
	if (rl < 0.0001f) {
		r[0] = 1.0f;
		r[1] = r[2] = 0.0f;
		rl = 1.0f;
	}
	for (int k = 0; k < 3; k++)
		r[k] /= rl;
	u[0] = r[1] * f[2] - r[2] * f[1];
	u[1] = r[2] * f[0] - r[0] * f[2];
	u[2] = r[0] * f[1] - r[1] * f[0];   /* up = right x forward */
	const float *cols[3];
	float nr[3] = { -r[0], -r[1], -r[2] }, nu[3] = { -u[0], -u[1], -u[2] }, nf[3] = { -f[0], -f[1], -f[2] };
	if (g_lampBeamAxis == 0) {
		cols[0] = f; cols[1] = nr; cols[2] = u;
	} else if (g_lampBeamAxis == 1) {
		cols[0] = r; cols[1] = f; cols[2] = u;
	} else {
		cols[0] = r; cols[1] = nu; cols[2] = f;
	}
	if (g_lampBeamSign < 0) {   /* the beam the other way, and one more column flipped to keep the hand */
		cols[g_lampBeamAxis] = nf;
		int o = (g_lampBeamAxis + 1) % 3;
		cols[o] = cols[o] == r ? nr : cols[o] == nr ? r : cols[o] == u ? nu : u;
	}
	for (int row = 0; row < 3; row++)
		for (int col = 0; col < 3; col++)
			F[row * 3 + col] = cols[col][row];
	Mul3(M, F, MF);
	Mul3(A, MF, AMF);
	Mul3(Nb, AMF, W);
	return true;
}

/* A node's transform written (the game's rows), local or world. */
static void WriteTransform(uintptr_t node, uint32_t at, const float R[9], const float t[3], float scale)
{
	float *rows = (float *)(node + at);
	for (int row = 0; row < 3; row++)
		for (int col = 0; col < 3; col++)
			rows[row * 4 + col] = g_layout == LAYOUT_FILE ? R[row * 3 + col] : R[col * 3 + row];
	memcpy(rows + 12, t, 12);
	rows[15] = scale;
}

/* The world transforms under a node written from its own: what the game's update would do
 * (a placed light's 3D isn't walked by it every frame). */
static void PropagateWorld(uintptr_t node, const float W[9], const float w[3], float s, int depth)
{
	if (depth > 4 || !IsA(node, RTTI_NODE) || !Accessible(node + OFF_CHILDREN, 0x10, false))
		return;
	uintptr_t children = ReadPtr(node + OFF_CHILDREN);
	unsigned used = *(const uint16_t *)(node + OFF_CHILDREN_USED), cap = *(const uint16_t *)(node + OFF_CHILDREN_CAP);
	if (!children || used > cap || used > 32 || !Accessible(children, used * 8u, false))
		return;
	for (unsigned i = 0; i < used; i++) {
		uintptr_t c = ((const uintptr_t *)children)[i];
		if (!c || !IsA(c, RTTI_AVOBJECT) || !Accessible(c + OFF_LOCAL_ROT, 0x90, true))
			continue;
		float L[9], l[3], Wc[9], Wl[3], wc[3], sc;
		ReadRot((const float *)(c + OFF_LOCAL_ROT), L);
		memcpy(l, (const void *)(c + OFF_LOCAL_ROT + 0x30), 12);
		sc = *(const float *)(c + OFF_LOCAL_ROT + 0x3C);
		Mul3(W, L, Wc);
		MulV(W, l, Wl);
		for (int k = 0; k < 3; k++)
			wc[k] = w[k] + s * Wl[k];
		WriteTransform(c, OFF_WORLD_ROT, Wc, wc, s * sc);
		memcpy((void *)(c + OFF_WORLD_BOUND), wc, 12);
		PropagateWorld(c, Wc, wc, s * sc, depth + 1);
	}
}

/* The headlamp's light every frame. An add-on node the game kept (none in test 30: the
 * loader keeps only a worn nif's skinned shapes) is put at the lens, with the bars' turn and
 * the tilt, through the bike's bind and bone, the beam along its BeamAxis, while the lamp is
 * lit; hidden and sunk 20000 below otherwise. The light reference the controller script
 * placed (its form id in CMB_HeadlampRefHi/Lo) does the job without a node: its 3D is put at
 * the lens, the world transforms beneath it with it, while it's loaded (the script disables
 * it when the lamp is off); it's parked far below when a kept node does the lighting. */
/* Where the light itself goes: Ahead units along the beam from the lens (test 34: on fast
 * frames the light fell inside the lamp housing, which shadowed its own beam for a frame) and
 * Lead frames of the bike's speed on along the heading (the renderer lights with the
 * transform a frame late). */
static void BeamPlace(float w[3], const float W[9])
{
	for (int k = 0; k < 3; k++)
		w[k] += g_lampAhead * W[k * 3 + g_lampBeamAxis] * (float)g_lampBeamSign;
	if (g_lampLead > 0.0f && g_frameDt > 0.0f && g_speedAlongFast > 0.0f) {
		float dt = g_frameDt > 0.05f ? 0.05f : g_frameDt;   /* a hitch frame mustn't throw the light ahead */
		float on = g_speedAlongFast * dt * g_lampLead;
		w[0] += sinf(g_headingNow) * on;
		w[1] += cosf(g_headingNow) * on;
	}
}

/* A reference's 3D root, if it has one that can be written. */
static uintptr_t RefRoot3D(uintptr_t ref)
{
	if (!ref || !Accessible(ref + OFF_REFR_LOADED, 8, false))
		return 0;
	uintptr_t loaded = ReadPtr(ref + OFF_REFR_LOADED);
	uintptr_t root = loaded ? ReadPtr(loaded + OFF_LOADED_ROOT) : 0;
	return root && IsA(root, RTTI_AVOBJECT) && Accessible(root + OFF_LOCAL_ROT, 0xC0, true) ? root : 0;
}

static void FrameLamp(bool tilt, const float R[9], const float P[3])
{
	const HeldSkin *bike = NULL;
	for (int k = 0; k < g_skinCount; k++)
		if (g_skins[k].node && (!bike || (bike->role != ROLE_NONE && g_skins[k].role == ROLE_NONE)))
			bike = &g_skins[k];
	float Nb[9], nb[3], sb, Nbi[9];
	bool ready = bike && g_lampOk && NodeWorld(bike->node, Nb, nb, &sb, Nbi);
	bool want = g_lampEnabled && GlobalValue(g_headlampGlobal) > 0.5f;
	float M[9] = { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, m[3] = { 0, 0, 0 };
	if (ready) {
		if (g_partsOk)
			Turn(M, m, g_steerAxis, g_steerPoint, g_barNow / 57.29578f);
		if (tilt) {
			float M2[9], m2[3], RP[3];
			Mul3(R, M, M2);
			MulV(R, m, m2);
			MulV(R, P, RP);
			memcpy(M, M2, sizeof(M2));
			for (int i = 0; i < 3; i++)
				m[i] = m2[i] + P[i] - RP[i];
			m[2] += g_liftNow;
		}
	}
	bool nodeLit = false;
	for (int i = 0; i < 2; i++) {
		LampNode *l = &g_lamp[i];
		if (!l->node)
			continue;
		bool lit = want && (i == 1) == (g_lampShadows != 0);
		uintptr_t parent = ReadPtr(l->node + OFF_PARENT);
		float Np[9], np[3], sp, Npi[9];
		bool placeable = ready && parent && NodeWorld(parent, Np, np, &sp, Npi);
		float *rows = (float *)(l->node + OFF_LOCAL_ROT), *pos = rows + 12, *scale = rows + 15;
		volatile uint64_t *flags = (volatile uint64_t *)(l->node + g_lampFlagsOff);
		if (lit && !placeable) {
			/* Wanted, but nowhere to put it (no parts file with the lens, the bike's bone unread):
			 * left where the nif put it and shown. */
			if (l->placed || !l->lit) {
				memcpy(rows, l->saved, 0x40);
				*flags = l->savedFlags;
				if (!l->lit)
					Log("lamp: '%s' lit where the nif put it (%s)", g_lampNodeName[i],
					    !g_lampOk ? "no LampPoint in the parts file" : !bike ? "the bike's bone isn't held" : "its parent's transform can't be read");
				l->lit = true;
				l->placed = false;
			}
			nodeLit = true;
			continue;
		}
		if (!lit) {
			if (l->lit || !l->placed) {
				memcpy(rows, l->saved, 0x30);
				pos[0] = pos[1] = 0.0f;
				pos[2] = -20000.0f;   /* far below the world: lights nothing even if the flag doesn't cull it */
				*scale = 1.0f;
				*flags = l->savedFlags | 1u;
				if (l->lit)
					Log("lamp: '%s' out", g_lampNodeName[i]);
				l->lit = false;
				l->placed = true;
			}
			continue;
		}
		float w[3], W[9], Lr[9], d[3], lp[3];
		LensWorld(bike, Nb, nb, sb, M, m, w, W);
		BeamPlace(w, W);
		Mul3(Npi, W, Lr);          /* local = parent^-1 world */
		for (int k = 0; k < 3; k++)
			d[k] = w[k] - np[k];
		MulV(Npi, d, lp);
		for (int k = 0; k < 3; k++)
			lp[k] /= sp > 0.0001f ? sp : 1.0f;
		WriteTransform(l->node, OFF_LOCAL_ROT, Lr, lp, 1.0f);
		*flags = l->savedFlags & ~(uint64_t)1;
		nodeLit = true;
		if (!l->lit) {
			Log("lamp: '%s' lit: the light at (%.0f, %.0f, %.0f) in the world (%g along the beam from the lens), the beam along (%.2f, %.2f, %.2f)", g_lampNodeName[i], g_lampAhead,
			    w[0], w[1], w[2], W[0 * 3 + g_lampBeamAxis] * g_lampBeamSign, W[1 * 3 + g_lampBeamAxis] * g_lampBeamSign, W[2 * 3 + g_lampBeamAxis] * g_lampBeamSign);
			l->lit = true;
			l->placed = true;
		}
	}

	/* The light reference the script placed. */
	uint32_t id = (((uint32_t)GlobalValue(g_headlampRefGlobals[0]) & 0xFFFFu) << 16) | ((uint32_t)GlobalValue(g_headlampRefGlobals[1]) & 0xFFFFu);
	if (id != g_lampRefId) {
		/* A handover (test 33: the script places a fresh reference in the player's cell two
		 * cells on and retires the old one 2.5 s later): the old one is kept at the lens until
		 * the new one has its 3D, then parked, so the beam never goes out between them. */
		if (g_lampRef && g_lampRefHad3D && id) {
			g_lampRefOld = g_lampRef;
			g_lampRefOldId = g_lampRefId;
			g_lampRefOldSince = (float)g_clock;
			g_lampRefNewFrames = 0;
		}
		g_lampRefId = id;
		g_lampRef = 0;
		g_lampRefLogged = g_lampRefParked = g_lampRefHad3D = g_lampRefGoneLogged = false;
		if (id) {
			uintptr_t form = ((LookupFormByID_t)(g_base + RVA_LOOKUP_FORM))(id);
			if (form && Accessible(form, 0x100, false) && *(const uint8_t *)(form + OFF_FORM_TYPE) == FORM_TYPE_REFR && IsA(form, RTTI_REFR) &&
			    Accessible(form + OFF_REFR_POS, 12, true))
				g_lampRef = form;
			else
				Log("lamp: form %08X (CMB_HeadlampRefHi/Lo) isn't a placed reference: the beam can't be moved", id);
		}
	}
	if (g_lampRefOld) {
		uintptr_t oldRoot = RefRoot3D(g_lampRefOld), newRoot = g_lampRef ? RefRoot3D(g_lampRef) : 0;
		const char *why = NULL;
		bool park = false;
		g_lampRefNewFrames = newRoot ? g_lampRefNewFrames + 1 : 0;
		if (!oldRoot)
			why = "its 3D is gone";
		else if ((float)g_clock - g_lampRefOldSince > 2.0f)
			why = "2 s passed", park = true;
		else if (g_lampRefNewFrames > g_lampHandoverFrames || !ready || !want)
			why = newRoot ? "the new one has had its 3D for the HandoverFrames" : !want ? "the lamp is out" : "the lens can't be placed", park = true;
		if (park) {
			static const float identity[9] = { 1, 0, 0, 0, 1, 0, 0, 0, 1 };
			float below[3] = { 0.0f, 0.0f, -20000.0f };
			WriteTransform(oldRoot, OFF_LOCAL_ROT, identity, below, 1.0f);
			WriteTransform(oldRoot, OFF_WORLD_ROT, identity, below, 1.0f);
			memcpy((void *)(oldRoot + OFF_WORLD_BOUND), below, 12);
			PropagateWorld(oldRoot, identity, below, 1.0f, 0);
		}
		if (why) {
			Log("lamp: the light handed over from %08X to %08X: the old one %s (%s)", g_lampRefOldId, g_lampRefId, park ? "parked" : "dropped", why);
			g_lampRefOld = 0;
		} else {
			float w[3], W[9];
			LensWorld(bike, Nb, nb, sb, M, m, w, W);
			BeamPlace(w, W);
			WriteTransform(oldRoot, OFF_LOCAL_ROT, W, w, 1.0f);
			WriteTransform(oldRoot, OFF_WORLD_ROT, W, w, 1.0f);
			memcpy((void *)(oldRoot + OFF_WORLD_BOUND), w, 12);
			PropagateWorld(oldRoot, W, w, 1.0f, 0);
		}
	}
	if (!g_lampRef)
		return;
	uintptr_t loaded = ReadPtr(g_lampRef + OFF_REFR_LOADED);
	uintptr_t root = loaded ? ReadPtr(loaded + OFF_LOADED_ROOT) : 0;
	if (!root || !IsA(root, RTTI_AVOBJECT) || !Accessible(root + OFF_LOCAL_ROT, 0xC0, true)) {
		/* Not loaded: the lamp is off (the script disabled it), not in yet, or its cell has gone
		 * (test 32: the beam went after 25 s of riding, the reference left in the cell it was
		 * placed in; the script moves it into the player's cell now). Said once each time. */
		if (g_lampRefHad3D && want && !g_lampRefGoneLogged) {
			g_lampRefGoneLogged = true;
			Log("lamp: the light reference %08X has no 3D now while the lamp is wanted (its cell unloaded?): no beam until the script moves it to the player", g_lampRefId);
		}
		g_lampRefHad3D = false;
		return;
	}
	if (!g_lampRefHad3D) {
		g_lampRefHad3D = true;
		if (g_lampRefGoneLogged) {
			g_lampRefGoneLogged = false;
			Log("lamp: the light reference %08X has its 3D again", g_lampRefId);
		}
	}
	float w[3], W[9];
	const float *pos = (const float *)(g_lampRef + OFF_REFR_POS);
	if (nodeLit || !ready) {
		if (!g_lampRefParked) {
			static const float identity[9] = { 1, 0, 0, 0, 1, 0, 0, 0, 1 };
			float below[3] = { pos[0], pos[1], -20000.0f };
			WriteTransform(root, OFF_LOCAL_ROT, identity, below, 1.0f);
			WriteTransform(root, OFF_WORLD_ROT, identity, below, 1.0f);
			PropagateWorld(root, identity, below, 1.0f, 0);
			g_lampRefParked = true;
			Log("lamp: the light reference %08X parked far below (%s)", g_lampRefId, nodeLit ? "the game kept the add-on node, which does the lighting" : "the lens can't be placed yet");
		}
		return;
	}
	LensWorld(bike, Nb, nb, sb, M, m, w, W);
	BeamPlace(w, W);
	WriteTransform(root, OFF_LOCAL_ROT, W, w, 1.0f);
	WriteTransform(root, OFF_WORLD_ROT, W, w, 1.0f);
	memcpy((void *)(root + OFF_WORLD_BOUND), w, 12);   /* the bound's centre with it (the renderer culls by it) */
	PropagateWorld(root, W, w, 1.0f, 0);
	memcpy((void *)(g_lampRef + OFF_REFR_POS), w, 12);
	g_lampRefParked = false;
	if (!g_lampRefLogged) {
		g_lampRefLogged = true;
		unsigned used = IsA(root, RTTI_NODE) && Accessible(root + OFF_CHILDREN, 0x10, false) ? *(const uint16_t *)(root + OFF_CHILDREN_USED) : 0;
		uintptr_t children = used ? ReadPtr(root + OFF_CHILDREN) : 0;
		char kids[240] = "";
		int len = 0;
		if (children && used && Accessible(children, used * 8u, false))
			for (unsigned k = 0; k < used && k < 8 && len < (int)sizeof(kids) - 70; k++) {
				uintptr_t c = ((const uintptr_t *)children)[k];
				len += snprintf(kids + len, sizeof(kids) - len, "%s%s '%.24s'", k ? ", " : ": ", c ? OrNone(ObjectTypeName(c)) : "(null)", c ? OrNone(ObjectName(c)) : "");
			}
		Log("lamp: the light reference %08X the script placed: its 3D '%.32s' (%s, %u child(ren)%s) put at (%.0f, %.0f, %.0f) each frame (%g along the beam from the lens), the beam along (%.2f, %.2f, %.2f)",
		    g_lampRefId, OrNone(ObjectName(root)), OrNone(ObjectTypeName(root)), used, kids, w[0], w[1], w[2], g_lampAhead,
		    W[0 * 3 + g_lampBeamAxis] * g_lampBeamSign, W[1 * 3 + g_lampBeamAxis] * g_lampBeamSign, W[2 * 3 + g_lampBeamAxis] * g_lampBeamSign);
	}
}

static uintptr_t g_lastRoot;

static void LetGoLamp(int i, const char *why)
{
	LampNode *l = &g_lamp[i];
	if (!l->node)
		return;
	if (Accessible(l->node + OFF_LOCAL_ROT, 0x40, true))
		memcpy((void *)(l->node + OFF_LOCAL_ROT), l->saved, 0x40);
	if (Accessible(l->node + g_lampFlagsOff, 8, true))
		*(volatile uint64_t *)(l->node + g_lampFlagsOff) = l->savedFlags;
	Log("lamp: '%s' put back and let go (%s)", g_lampNodeName[i], why);
	Release(l->node);
	memset(l, 0, sizeof(*l));
}

static void HoldLamp(int i, uintptr_t node)
{
	LampNode *l = &g_lamp[i];
	uintptr_t parent = ReadPtr(node + OFF_PARENT);
	if (!Accessible(node + OFF_LOCAL_ROT, 0x40, true) || !Accessible(node + g_lampFlagsOff, 8, true) ||
	    !parent || !IsA(parent, RTTI_AVOBJECT) || !Accessible(parent + OFF_WORLD_ROT, 0x40, false)) {
		if (!(g_lampLogged & (1 << i))) {
			g_lampLogged |= 1 << i;
			Log("lamp: '%s' found but can't be held (its transform, its flags or its parent can't be read)", g_lampNodeName[i]);
		}
		return;
	}
	memset(l, 0, sizeof(*l));
	l->node = node;
	memcpy(l->saved, (const void *)(node + OFF_LOCAL_ROT), 0x40);
	l->savedFlags = *(const volatile uint64_t *)(node + g_lampFlagsOff);
	Retain(node);
	/* What hangs off it (the game's light, if the add-on node took): logged for the next round. */
	unsigned used = Accessible(node + OFF_CHILDREN, 0x10, false) ? *(const uint16_t *)(node + OFF_CHILDREN_USED) : 0;
	uintptr_t children = used ? ReadPtr(node + OFF_CHILDREN) : 0;
	char kids[240] = "";
	int len = 0;
	if (children && used && Accessible(children, used * 8u, false))
		for (unsigned k = 0; k < used && k < 8 && len < (int)sizeof(kids) - 70; k++) {
			uintptr_t c = ((const uintptr_t *)children)[k];
			len += snprintf(kids + len, sizeof(kids) - len, "%s%s '%.24s'", k ? ", " : ": ", c ? OrNone(ObjectTypeName(c)) : "(null)", c ? OrNone(ObjectName(c)) : "");
		}
	Log("lamp: holding '%s' (%s under '%.32s', flags %#llx, %u child(ren)%s)", g_lampNodeName[i], OrNone(ObjectTypeName(node)),
	    OrNone(ObjectName(parent)), (unsigned long long)l->savedFlags, used, kids);
}

static void SyncSkins(uintptr_t player, bool riderWanted)
{
	SkinList list = { .count = 0 };
	uintptr_t root = Root3D(player);
	if (root != g_lastRoot) {
		g_lastRoot = root;
		ForgetRegions();   /* a rebuilt 3D: the old nodes' memory may be gone */
	}
	WalkFrom(root, &list, false);
	int fromRoot = list.count;
	uintptr_t biped = Biped(player);
	if (biped)
		WalkBiped(biped, &list, false);
	if (list.count && !g_rideRouteLogged) {
		g_rideRouteLogged = true;
		Log("tilt: found %d bike shape(s): %s%s", list.count,
		    fromRoot ? "under the 3D root" : "only through the biped (not under the 3D root)",
		    list.byBind[0] ? ", by its COM bind or its armor addon (not its name)" : "");
		if (!fromRoot)
			LogBikeSlot(player, biped, root);
	}
	if (list.count)
		g_emptySyncs = 0;
	else if (++g_emptySyncs == 10 && !g_rideDiagnosed) {
		g_rideDiagnosed = true;
		Diagnose(player);
	}

	for (int i = g_skinCount - 1; i >= 0; i--) {
		bool still = false;
		for (int j = 0; j < list.count; j++)
			still |= list.found[j] == g_skins[i].boneData;
		if (!still) {
			LetGo(i, "no longer worn");
			ForgetRegions();   /* something of the 3D went */
		}
	}
	for (int j = 0; j < list.count && g_skinCount < MAX_SKINS; j++) {
		bool held = false;
		for (int i = 0; i < g_skinCount; i++)
			held |= g_skins[i].boneData == list.found[j];
		if (!held && !Refused(list.found[j]))
			HoldSkin(list.found[j], list.skins[j], list.names[j]);
	}
	for (int i = 0; i < 2; i++) {
		if (g_lamp[i].node && g_lamp[i].node != list.lamp[i])
			LetGoLamp(i, list.lamp[i] ? "the node was replaced" : "no longer worn");
		if (!g_lamp[i].node && list.lamp[i] && g_skinCount)
			HoldLamp(i, list.lamp[i]);
	}
	SyncRider(player, &list, riderWanted && g_riderTilt);
	if (g_layoutFromRoot == LAYOUT_UNKNOWN && player) {
		g_layoutFromRoot = LayoutFromRoot(player);
		if (g_layoutFromRoot != LAYOUT_UNKNOWN)
			Log("tilt: the player's 3D says the game's matrices are %s", LayoutName(g_layoutFromRoot));
	}
	DecideLayout();
}

/* The rotation (x' = R x, row-major 3x3) in the rider's frame (x right, y forward, z up):
 * pitch about x (nose up when > 0), then roll about the pitched y (up to the right when > 0). */
static void TiltRotation(float pitchDeg, float rollDeg, float R[9])
{
	float a = pitchDeg / 57.29578f, b = rollDeg / 57.29578f;
	float ca = cosf(a), sa = sinf(a), cb = cosf(b), sb = sinf(b);
	/* Rx(a) Ry(b) */
	R[0] = cb;        R[1] = 0.0f; R[2] = sb;
	R[3] = sa * sb;   R[4] = ca;   R[5] = -sa * cb;
	R[6] = -ca * sb;  R[7] = sa;   R[8] = ca * cb;
}

static int CompareFloats(const void *a, const void *b)
{
	float x = *(const float *)a, y = *(const float *)b;
	return (x > y) - (x < y);
}

/* The median of the samples taken in the last g_medianTime seconds (pitch or roll). */
static float RecentMedian(int which)
{
	float values[TILT_SAMPLES];
	int n = 0;
	for (int i = 0; i < g_tiltSampleCount; i++) {
		const TiltSample *t = &g_tiltSamples[(g_tiltSampleHead - 1 - i + TILT_SAMPLES) % TILT_SAMPLES];
		if (g_clock - t->time > g_medianTime && n)
			break;
		values[n++] = which ? t->roll : t->pitch;
	}
	if (!n)
		return 0.0f;
	qsort(values, (size_t)n, sizeof(float), CompareFloats);
	return n & 1 ? values[n / 2] : 0.5f * (values[n / 2 - 1] + values[n / 2]);
}

static float Clamp(float v, float limit)
{
	return v > limit ? limit : v < -limit ? -limit : v;
}

/* Every frame while riding: the ground's pitch and roll under the rider, filtered (a
 * median drops one-frame contacts with a curb or a lip of rock, then smoothing, then a
 * rate limit), capped, and put on the bike's mesh before it goes onto its bone: turned
 * about the seat, so the seat and bars stay under the rider (who doesn't tilt). */
static void FrameTilt(void)
{
	float maxDegrees = GlobalValue(g_tiltGlobal);
	bool tilt = maxDegrees > 0.0f;
	if (!g_skinCount || (!tilt && !g_partsOk) || (g_layout != LAYOUT_FILE && g_layout != LAYOUT_TRANSPOSED))
		return;
	uintptr_t player = Player();
	if (!player || !Accessible(player + OFF_REFR_HEADING, 4, false))
		return;
	float h = *(const float *)(player + OFF_REFR_HEADING);
	if (!isfinite(h))
		return;
	g_headingNow = h;

	/* The moving parts: the wheels spin with the distance ridden (back when reversing); the
	 * bars go over with the rider's turning (the heading grows turning right), smoothed. */
	float rate = 0.0f;
	if (g_haveLastHeading && g_frameDt > 0.0f) {
		float dh = h - g_lastHeading;
		while (dh > 3.14159265f)
			dh -= 6.2831853f;
		while (dh < -3.14159265f)
			dh += 6.2831853f;
		if (fabsf(dh) < 1.5f)   /* a bigger jump is a door or a load, not a turn */
			rate = dh / g_frameDt * 57.29578f;
	}
	g_lastHeading = h;
	g_haveLastHeading = true;
	if (g_frameDt > 0.0f) {
		/* Across the back mode's edge the nose's swing changes sense (backing, a side key swings
		 * it against the key; creeping, with it), and so does the flip below: the smoothed rate
		 * is re-expressed at the edge so the bars' input is continuous (review: it carried the
		 * old sign for 70 ms, and the bars twitched a few degrees against the key at every
		 * release of the back key with a side key held). */
		static int lastMode = INPUT_PASS;
		if ((lastMode == INPUT_BACK) != (g_inputMode == INPUT_BACK))
			g_headingRate = -g_headingRate;
		lastMode = g_inputMode;
		g_headingRate += (rate - g_headingRate) * (1.0f - expf(-g_frameDt / 0.1f));
		float f = g_headingRate / g_barFullAt;
		f = f > 1.0f ? 1.0f : f < -1.0f ? -1.0f : f;
		/* Backing up, a side key swings the rear its way and the nose the other (as a car
		 * reverses), so the heading rate runs against the key and the bars with it: test 38,
		 * forward the right key gave the bars negative (307 samples) and the left positive
		 * (274), reversing the left gave negative (39) and the right positive (14), "when going
		 * back and turning left motorcycle handlebars should also turn left". Flipped while
		 * backing, the bars go the key's way: where the front wheel points, the rear following. The back mode alone says backing:
		 * with the back key let go and a side key held, the creep turns the heading the key's
		 * way while the smoothed speed still reads backward for a third of a second, and a flip
		 * on the speed flapped the bars full lock and back (review). */
		if (g_inputMode == INPUT_BACK)
			f = -f;
		/* Less at speed (a bike's bars barely move there, and the game's lean clips, posed
		 * with the bars at BarAtSpeed of the angle, play then): full to 150 units/s, down to
		 * BarAtSpeed of it by 400. */
		float atSpeed = (g_speed - 150.0f) / 250.0f;
		atSpeed = atSpeed < 0.0f ? 0.0f : atSpeed > 1.0f ? 1.0f : atSpeed;
		float barTarget = g_partsOk ? -g_barAngle * f * (1.0f - (1.0f - g_barAtSpeed) * atSpeed) : 0.0f;
		g_barNow += (barTarget - g_barNow) * (1.0f - expf(-g_frameDt / 0.15f));
		if (g_partsOk) {
			g_wheelAngle -= g_speedAlong / g_wheelRadius * g_frameDt;   /* forward: the top of the wheel goes forward */
			if (g_wheelAngle > 3.14159265f)
				g_wheelAngle -= 6.2831853f;
			else if (g_wheelAngle < -3.14159265f)
				g_wheelAngle += 6.2831853f;
		}
	}

	/* The ground's normal in the rider's frame: heading h, forward (sin h, cos h), right (cos h, -sin h). */
	bool onGround = g_groundOk && !g_groundAir;
	float rawPitch = 0.0f, rawRoll = 0.0f;
	if (!tilt) {
		g_pitchSmooth = g_rollSmooth = g_pitchNow = g_rollNow = 0.0f;   /* the tilt is off: level */
		onGround = false;
	}
	if (onGround) {
		float sh = sinf(h), ch = cosf(h);
		float ux = g_groundN[0] * ch - g_groundN[1] * sh, uy = g_groundN[0] * sh + g_groundN[1] * ch, uz = g_groundN[2];
		rawPitch = atan2f(-uy, uz) * 57.29578f;   /* ground rising ahead leans the normal back */
		rawRoll = atan2f(ux, uz) * 57.29578f;
		TiltSample *t = &g_tiltSamples[g_tiltSampleHead];
		t->pitch = rawPitch;
		t->roll = rawRoll;
		t->time = g_clock;
		g_tiltSampleHead = (g_tiltSampleHead + 1) % TILT_SAMPLES;
		if (g_tiltSampleCount < TILT_SAMPLES)
			g_tiltSampleCount++;
	} else {
		g_tiltSampleCount = 0;   /* in the air: start the normal's median afresh on landing */
	}
	/* Pitch: the slope of the track just ridden (test 9: the support normal swings tens of
	 * degrees from frame to frame, even on a road); the normal's median only until there's
	 * a wheelbase of track. In the air, and standing still, it holds. */
	float medianPitch = onGround ? RecentMedian(0) : 0.0f, medianRoll = onGround ? RecentMedian(1) : 0.0f;
	bool useWheels = g_wheelPitchOk && onGround;   /* the rays under the wheels: no lag at a lip or a crest (test 29) */
	bool useNormal = !useWheels && !g_trackPitchOk && onGround && !g_hadTrackPitch;   /* only before the track has said anything */
	const char *source = !tilt ? "off" : useWheels ? "wheels" : g_trackPitchOk ? "track" : useNormal ? "normal" : "held";
	if (tilt) {
		float maxRoll = g_maxRoll < maxDegrees ? g_maxRoll : maxDegrees;
		float targetPitch = useWheels ? Clamp(g_wheelPitch, maxDegrees) : g_trackPitchOk ? Clamp(g_trackPitch, maxDegrees)
		                  : useNormal ? Clamp(medianPitch, maxDegrees) : g_pitchSmooth;
		/* Leaning into turns (test 31's wish: the rider in line with the bike in bends): the
		 * centripetal lean atan(v w / g) for the speed and the turning rate (g 687 units/s^2,
		 * 70 units a metre), none at a creep and full from 150 units/s, at most MaxLean, on top
		 * of the ground's roll; the rider leans with the bike. */
		float lean = 0.0f;
		if (g_maxLean > 0.0f && onGround) {
			/* Test 32: a side key asks 300 deg/s at once and the atan sat at the cap, the roll
			 * jumping 18 deg between quarter seconds. The turning rate is smoothed over
			 * LeanSmooth, a small correction (v w / g under LeanDead) gives nothing, the lean is
			 * LeanGain of the physical one, and it changes at most LeanRate a second. */
			float v = g_speed > 0.0f ? g_speed : 0.0f, dtl = g_frameDt > 0.05f ? 0.05f : g_frameDt;
			if (dtl > 0.0f)
				g_yawForLean += (g_headingRate - g_yawForLean) * (1.0f - expf(-dtl / (g_leanSmooth > 0.01f ? g_leanSmooth : 0.01f)));
			float x = v * (g_yawForLean / 57.29578f) / 687.0f;
			float xd = x > g_leanDead ? x - g_leanDead : x < -g_leanDead ? x + g_leanDead : 0.0f;
			float fade = (v - 50.0f) / 100.0f;
			fade = fade < 0.0f ? 0.0f : fade > 1.0f ? 1.0f : fade;
			float target = Clamp(atanf(xd) * 57.29578f * g_leanGain * fade, g_maxLean);
			float step = g_leanRate > 0.0f ? g_leanRate * dtl : 1000.0f, d = target - g_leanNow;
			g_leanNow += d > step ? step : d < -step ? -step : d;
			lean = g_leanNow;
		} else if (g_maxLean <= 0.0f) {
			g_leanNow = g_yawForLean = 0.0f;
		}
		float targetRoll = onGround ? Clamp(medianRoll, maxRoll) + lean : g_rollSmooth;
		g_pitchSmooth = targetPitch;
		g_rollSmooth = targetRoll;
		/* A critically damped spring to the target (test 29: smoothing then a rate cap saw-sawed
		 * when the source switched), its speed capped at MaxRate. */
		float w = g_smoothing > 0.01f ? 3.0f / g_smoothing : 300.0f, cap = g_maxRate > 0.0f ? g_maxRate : 1000.0f;
		float dt = g_frameDt > 0.05f ? 0.05f : g_frameDt;
		g_pitchVel += (w * w * (targetPitch - g_pitchNow) - 2.0f * w * g_pitchVel) * dt;
		g_rollVel += (w * w * (targetRoll - g_rollNow) - 2.0f * w * g_rollVel) * dt;
		g_pitchVel = Clamp(g_pitchVel, cap);
		g_rollVel = Clamp(g_rollVel, cap);
		g_pitchNow += g_pitchVel * dt;
		g_rollNow += g_rollVel * dt;
		/* The lift: the wheels onto the ground between the rays when it's above the capsule's
		 * contact (a dip, a lip under the front), up to 60 (a ditch's wheels bridge it: test 31);
		 * down by the suspension's droop at most (test 38: stopped on uneven ground both wheels
		 * hung at -10 with the frame held at the contact, the line between the hits running
		 * below it, a crest or a bump under the rider; sunk by SuspDroop the frame lets the
		 * wheels reach the ground, and a landing's undershoot shows as the wheels compressing a
		 * few units), never with Suspension=0 (on a crest the bike sits on it, as before). */
		float liftFloor = g_suspension ? -g_suspDroop : 0.0f, targetLift;
		if (useWheels) {
			g_wheelWordAt = (float)g_clock;
			targetLift = g_wheelLift > 60.0f ? 60.0f : g_wheelLift < liftFloor ? liftFloor : g_wheelLift;
		} else if ((float)g_clock - g_wheelWordAt < 3.0f) {
			/* No word from the rays: the lift is held with the pitch (the spring, or the filter
			 * below, rests on it) for 3 s, then eased off as before. Not for good: a tunnel's
			 * ceiling throws the rays' hits away for as long as it lasts, and while a pitch held
			 * stale is a few degrees a stale lift would float the bike through it; 3 s covers a
			 * slow back-off (the first cut's 1.5 s was tight for one: review). Whether the pitch
			 * is held or the track's slope stands in makes no odds here: backing off the car the
			 * track just ridden was the bonnet's 41 deg. Test 38, backing off a
			 * station wagon the front wheel had climbed: the rays missed (the car's roof sat above
			 * the front ray's allowed rise), the pitch was kept at 41.5 while the lift fell from
			 * 33.9 to 0 within a quarter second, so the frame dropped to the capsule's contact with
			 * the nose still 41 deg up and the rear wheel went under the ground: "going back was
			 * putting half of the bike underground". */
			targetLift = g_liftSmooth;
		} else {
			targetLift = 0.0f;
		}
		float dtb = g_frameDt > 0.05f ? 0.05f : g_frameDt;
		if (g_suspension) {
			/* A suspension (test 36's wish: "the frame and rider follow the wheels through a spring
			 * and damper, compressing and rebounding over bumps"): the lift follows the wheels' line
			 * through a spring of SuspFrequency hertz with the damping ratio SuspDamping, so a step
			 * is met with a compression and a rebound (0.5: a sixth of the step over); the rate cap
			 * below still bounds the rise. Never below the droop under the ground's contact: the
			 * rebound of a drop ends with the wheels on the ground at their droop, not in it. */
			float w = 6.2831853f * g_suspFrequency;
			g_liftVel += (w * w * (targetLift - g_liftSmooth) - 2.0f * g_suspDamping * w * g_liftVel) * dtb;
			g_liftSmooth += g_liftVel * dtb;
			if (g_liftSmooth < liftFloor) {
				g_liftSmooth = liftFloor;
				if (g_liftVel < 0.0f)
					g_liftVel = 0.0f;
			}
		} else {
			g_liftSmooth += (targetLift - g_liftSmooth) * (1.0f - expf(-g_frameDt / 0.15f));
			g_liftVel = 0.0f;
		}
		/* A bump (test 33: the tyres sank into small hills, stones and curbs that passed under a
		 * wheel before the median and the spring reacted): whichever wheel would sit below its
		 * own ray's hit, with the pitch and lift as applied, is lifted out, and that lift
		 * settles over BumpSettle as the filtered values catch up or the bump passes. */
		float bump = 0.0f, tp = tanf(g_pitchNow / 57.29578f);
		bool bumpOn = g_bumpMax > 0.0f && g_bumpSettle > 0.0f;
		/* With the suspension, the bump takes only what a wheel's travel can't; the rear's
		 * upward travel is SuspCompressRear at most (its mudguard is on the frame: test 37
		 * found the tyre within 10 units of it, the closest touching), the frame the rest. */
		float compressRear = g_suspCompressRear < g_suspTravel ? g_suspCompressRear : g_suspTravel;
		float travel[2] = { g_suspension ? g_suspTravel : 0.0f, g_suspension ? compressRear : 0.0f };
		if (bumpOn && useWheels && g_wheelZOk) {
			for (int i = 0; i < 2; i++) {
				float bottom = g_liftSmooth + (i == 0 ? g_frontAxle[1] : g_rearAxle[1]) * tp, deficit = g_wheelZ[i] - bottom - travel[i];
				if (deficit > bump)
					bump = deficit;
			}
			/* A wheel radius at most in one go (test 34: 60 in a frame launched the bike); while
			 * an obstacle verdict is in force, 1.5 radii, as high as the face rays let an obstacle
			 * be (test 35: a 35 to 45 unit stone passed as one and the lift stopped at 30, the
			 * tyre 15 units into it). */
			float cap = g_bumpMax;
			bool wide = (float)g_clock - g_faceObstacleAt < g_obstacleHold || g_bumpLift > g_bumpMax;   /* and kept while the lift is above BumpMax: the rate below paces rises only, and the hold lapsing mustn't drop it in a frame (review) */
			if (wide && 1.5f * g_wheelRadius > cap)
				cap = 1.5f * g_wheelRadius;
			if (bump > cap)
				bump = cap;
		}
		/* Straight to the wheel's deficit while the step lasts (never above what's left to lift:
		 * no overshoot), back down over BumpSettle once it's gone; the rate below paces the rise. */
		if (!bumpOn)
			g_bumpLift = 0.0f;
		else if (bump > 0.0f)
			g_bumpLift = bump;
		else
			g_bumpLift += (bump - g_bumpLift) * (1.0f - expf(-dtb / g_bumpSettle));
		if (g_bumpLift < 0.05f)
			g_bumpLift = 0.0f;
		/* The whole lift rises at most LiftRate units a second (test 35: the bump lift's +34 in
		 * a quarter second at 900 units a second jumped the bike); down it goes as it likes. */
		float targetNow = g_liftSmooth + g_bumpLift;
		if (targetNow > 60.0f)
			targetNow = 60.0f;
		if (g_liftRate > 0.0f && targetNow > g_liftNow) {
			float most = g_liftNow + g_liftRate * dtb;
			g_liftNow = targetNow < most ? targetNow : most;
		} else {
			g_liftNow = targetNow;
		}
		/* The wheels follow the ground (test 36's wish: "the wheels would follow the ground"):
		 * each sits on its own ray's hit, moved against the frame by what it lacks from where
		 * the frame, lifted and pitched as applied this frame, holds it, up into the frame over
		 * a bump by SuspTravel at most (the rear by SuspCompressRear: its mudguard is on the
		 * frame), down into a hole by SuspDroop at most (test 38: at -10 the sliders were off
		 * the stanchions, whose overlap with them is 8 at rest, and the rear axle leaves the
		 * swingarm the same way; the front sat at full droop a tenth of the moving time).
		 * Compression within 0.03 s (a bump mustn't put the tyre into the frame; a one-frame
		 * ray hole doesn't flick it), extension over SuspExtend (test 38: "like there was no
		 * weight behind it": the front past half its travel 43% of the moving time, moving 10
		 * and more within a quarter second in a fifth of the samples); eased back over 0.2 s
		 * when the rays have no word or the bike is in the air. */
		for (int i = 0; i < 2; i++) {
			float target = 0.0f, tau = 0.2f;
			if (!g_suspension) {
				g_wheelOffset[i] = 0.0f;
				continue;
			}
			if (useWheels && g_wheelZOk && g_suspTravel > 0.0f) {
				float bottom = g_liftNow + (i == 0 ? g_frontAxle[1] : g_rearAxle[1]) * tp, compress = i == 0 ? g_suspTravel : compressRear;
				target = g_wheelZ[i] - bottom;
				target = target > compress ? compress : target < -g_suspDroop ? -g_suspDroop : target;
				tau = target < g_wheelOffset[i] ? g_suspExtend : 0.03f;
			}
			g_wheelOffset[i] += (target - g_wheelOffset[i]) * (1.0f - expf(-dtb / tau));
		}
	} else {
		g_liftNow = g_liftSmooth = g_bumpLift = g_liftVel = 0.0f;
		g_wheelOffset[0] = g_wheelOffset[1] = 0.0f;
	}

	float R[9];
	TiltRotation(g_pitchNow, g_rollNow, R);
	float c = (R[0] + R[4] + R[8] - 1.0f) * 0.5f;
	float angle = acosf(c > 1.0f ? 1.0f : c < -1.0f ? -1.0f : c);
	g_tiltNow = angle * 57.29578f;
	if (g_tiltNow > g_tiltMax) {
		if (g_tiltMax < 5.0f && g_tiltNow >= 5.0f)
			Log("tilt: the bike follows the ground (%.1f deg now)", g_tiltNow);
		g_tiltMax = g_tiltNow;
	}
	if (g_trace && g_clock - g_lastTrace >= 0.25f) {
		g_lastTrace = g_clock;
		char susp[48] = "";
		if (g_suspension)
			snprintf(susp, sizeof(susp), " | susp F %+.1f R %+.1f", g_wheelOffset[0], g_wheelOffset[1]);
		Log("trace: normal (%.3f, %.3f, %.3f) state %d%s | raw pitch %.1f roll %.1f | median %.1f %.1f | track %s%.1f | wheels %s%.1f lift %.1f (%d missed) | pitch from %s | target %.1f %.1f | applied %.1f %.1f | speed %.0f (%+.0f along the heading), radius %.0f, turn asked %.0f allowed %.0f deg/s, clamped %d%s%s%s",
		    g_groundN[0], g_groundN[1], g_groundN[2], g_lastState, onGround ? "" : " (off the ground)", rawPitch, rawRoll,
		    medianPitch, medianRoll, g_trackPitchOk ? "" : "(none) ", g_trackPitchOk ? g_trackPitch : 0.0f,
		    g_wheelPitchOk ? "" : "(none) ", g_wheelPitchOk ? g_wheelPitch : 0.0f, g_liftNow, g_wheelRaysMissed, source,
		    g_pitchSmooth, g_rollSmooth, g_pitchNow, g_rollNow, g_speed, g_speedAlong, g_steerRadius, g_steerWanted, g_steerAllowed,
		    g_steerClamped, g_inputMode == INPUT_BACK ? " | back" : g_inputMode == INPUT_CREEP ? " | creep" : "", susp, ClimbWord());
		g_wheelRaysMissed = 0;
		if (g_jumpMax > 0.5f)
			Log("trace: the arm bones' biggest move between frames %.1f (%s)", g_jumpMax, g_jumpName);
		g_jumpMax = 0.0f;
		if (g_throttleOn && g_inputActive)
			Log("throttle: speed %.2f of the top, input %.2f (keys %.2f, %.2f%s%s)", g_throttle, InputForSpeed(g_throttle),
			    g_keys[0], g_keys[1], g_throttleWrote ? ", the game gets the throttle's" : "", g_throttleCapped ? ", held to the measured speed" : "");
		if (g_partsOk)
			Log("parts: bars %+.1f deg (turning %+.0f deg/s), wheels at %.2f rad", g_barNow, g_headingRate, g_wheelAngle);
		if (g_riderCount)
			Log(g_riderApplied ? "rider: %d shape(s) tilted with the bike about (%.0f, %.0f, %.0f)" : "rider: %d shape(s) held, level",
			    g_riderCount, g_riderPivot[0], g_riderPivot[1], g_riderPivot[2]);
		Log("time: frame %.0f us avg, %.0f max, over %d (bike %.0f/%.0f, rider %.0f/%.0f); sync %.0f us avg, %.0f max, over %d, %.1f queries each (%d at most); %.2f memory queries a frame in all",
		    TimeAvgUs(&g_tFrame), g_tFrame.max * 1e6, g_tFrame.n, TimeAvgUs(&g_tTilt), g_tTilt.max * 1e6, TimeAvgUs(&g_tRider), g_tRider.max * 1e6,
		    TimeAvgUs(&g_tSync), g_tSync.max * 1e6, g_tSync.n, g_tSync.n ? (double)g_syncQueries / g_tSync.n : 0.0, g_syncQueriesMax,
		    g_queryFrames ? (double)g_queries / g_queryFrames : 0.0);
		memset(&g_tFrame, 0, sizeof(g_tFrame));
		memset(&g_tTilt, 0, sizeof(g_tTilt));
		memset(&g_tRider, 0, sizeof(g_tRider));
		memset(&g_tSync, 0, sizeof(g_tSync));
		g_queries = g_queryFrames = g_syncQueries = g_syncQueriesMax = 0;
		g_steerWanted = 0.0f;
		g_steerClamped = 0;
	}

	/* Each shape's map in the bike's own space, x -> M x + m: a wheel spun about its axle
	 * (the x axis through it), the front wheel, the lower fork and the bar assembly then
	 * turned about the steering axis, a wheel moved by its suspension offset (before the
	 * tilt, so it ends up along the tilted up; the lower fork by the front wheel's, no spin):
	 * the rear wheel along the bike's up, the front wheel and the lower fork along the
	 * steering axis, scaled so the move's z is the offset (test 38: "forks were getting out
	 * of tubes": the move ran along z while the fork is raked, SteerAxis (0, -0.49, 0.87) 29
	 * deg off vertical, so at the full 10 the sliders sat 4.9 units off the stanchions' line;
	 * along the turn's own axis the move's order against the turn no longer matters), and
	 * everything turned about the seat P by the tilt,
	 * x -> R (x - P) + P. Mesh -> bone after that: rotation A M, translation t + A m.
	 * The culling sphere (bone space) is grown by how far the map moves its centre (the
	 * offset's move with it), so the seat and the sphere still cover what they did. */
	float P[3] = { 0.0f, g_pivotForward, g_pivotHeight };
	static const float xAxis[3] = { 1.0f, 0.0f, 0.0f }, zAxis[3] = { 0.0f, 0.0f, 1.0f };
	bool lampLit = !g_lampEnabled || GlobalValue(g_headlampGlobal) > 0.5f;   /* the lit parts follow the lamp (always on with the lamp system off) */
	double tBike = Clock();
	for (int k2 = 0; k2 < g_skinCount; k2++) {
		HeldSkin *hs = &g_skins[k2];
		if (hs->role == ROLE_UNKNOWN)
			DetectRole(hs);
		float M[9] = { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, m[3] = { 0, 0, 0 };
		if (hs->role == ROLE_WHEEL_F || hs->role == ROLE_WHEEL_R)
			Turn(M, m, xAxis, hs->role == ROLE_WHEEL_F ? g_frontAxle : g_rearAxle, g_wheelAngle);
		if (hs->role == ROLE_WHEEL_F || hs->role == ROLE_FRONT || hs->role == ROLE_GLOW || hs->role == ROLE_FORK)
			Turn(M, m, g_steerAxis, g_steerPoint, g_barNow / 57.29578f);
		if (hs->role == ROLE_WHEEL_R) {
			m[2] += g_wheelOffset[1];
		} else if (hs->role == ROLE_WHEEL_F || hs->role == ROLE_FORK) {
			if (g_steerAxis[2] > 0.3f) {   /* along the steering axis, the move's z the offset (an axis nearer flat than 73 deg would ask for a huge move: the old vertical one then) */
				float k = g_wheelOffset[0] / g_steerAxis[2];
				for (int i = 0; i < 3; i++)
					m[i] += k * g_steerAxis[i];
			} else {
				m[2] += g_wheelOffset[0];
			}
		}
		if (tilt) {
			float M2[9], m2[3], RP[3];
			Mul3(R, M, M2);
			MulV(R, m, m2);
			MulV(R, P, RP);
			memcpy(M, M2, sizeof(M2));
			for (int i = 0; i < 3; i++)
				m[i] = m2[i] + P[i] - RP[i];
			m[2] += g_liftNow;
		}
		if (hs->role == ROLE_GLOW && !lampLit)
			for (int i = 0; i < 9; i++)
				M[i] *= 0.001f;   /* a speck inside the bucket: out of sight while the lamp is off */
		(void)zAxis;
		for (int b = 0; b < hs->count; b++) {
			const uint8_t *orig = hs->original[b];
			uint8_t *live = (uint8_t *)(hs->bones + (uintptr_t)b * BONE_SIZE);
			const float *o = (const float *)(orig + OFF_BONE_ROT), *t = (const float *)(orig + OFF_BONE_POS);
			float A[9], B[9], Am[3];
			for (int i = 0; i < 3; i++)
				for (int j = 0; j < 3; j++)
					A[i * 3 + j] = g_layout == LAYOUT_FILE ? o[i * 4 + j] : o[j * 4 + i];
			Mul3(A, M, B);
			MulV(A, m, Am);
			float *w = (float *)(live + OFF_BONE_ROT), *pos = (float *)(live + OFF_BONE_POS);
			for (int i = 0; i < 3; i++)
				for (int j = 0; j < 3; j++)
					w[i * 4 + j] = g_layout == LAYOUT_FILE ? B[i * 3 + j] : B[j * 3 + i];
			for (int i = 0; i < 3; i++)
				pos[i] = t[i] + Am[i];
			/* The sphere's centre (bike space) goes to M c + m: grow the radius by the move. */
			float moved[3];
			MulV(M, hs->centre, moved);
			float dx = moved[0] + m[0] - hs->centre[0], dy = moved[1] + m[1] - hs->centre[1], dz = moved[2] + m[2] - hs->centre[2];
			float radius = *(const float *)(orig + OFF_BONE_RADIUS);
			*(float *)(live + OFF_BONE_RADIUS) = radius + sqrtf(dx * dx + dy * dy + dz * dz);
		}
	}
	TimeAdd(&g_tTilt, tBike);
	double tRider = Clock();
	FrameRider(tilt, R, P);
	FrameLamp(tilt, R, P);
	TimeAdd(&g_tRider, tRider);
}

/* ------------------------------------------------------------------------- */
/* Ground average and the ridden track (for parking)                         */
/* ------------------------------------------------------------------------- */

static void FrameTime(void)
{
	LARGE_INTEGER now;
	QueryPerformanceCounter(&now);
	float dt = g_lastFrameTime.QuadPart && g_qpcFrequency.QuadPart
	           ? (float)(now.QuadPart - g_lastFrameTime.QuadPart) / (float)g_qpcFrequency.QuadPart : 0.0f;
	g_lastFrameTime = now;
	g_frameDt = dt >= 0.0f && dt <= 0.25f ? dt : 0.25f;
	g_clock += g_frameDt;
}

static void TrackClear(void)
{
	g_trackHead = g_trackCount = 0;
	g_airTime = 0.0f;
	g_hadTrackPitch = false;
}

static const TrackPoint *TrackAt(int back)   /* 0 = newest */
{
	return &g_track[(g_trackHead - 1 - back + 2 * TRACK_POINTS) % TRACK_POINTS];
}

static float Distance(const float a[3], const float b[3])
{
	float dx = a[0] - b[0], dy = a[1] - b[1], dz = a[2] - b[2];
	return sqrtf(dx * dx + dy * dy + dz * dz);
}

static bool TrackPointAt(const float p[3], float along, float out[3]);

/* The slope of the track over the last TRACK_PITCH_BACK units, along the rider's heading
 * (so riding backwards down a hill still lifts the nose). */
static void TrackPitch(uintptr_t player, const float pos[3])
{
	float back[3], recent[3];
	if (!TrackPointAt(pos, TRACK_PITCH_BACK, back) || !Accessible(player + OFF_REFR_HEADING, 4, false))
		return;
	float vx = pos[0] - back[0], vy = pos[1] - back[1], dz = pos[2] - back[2];
	float horizontal = sqrtf(vx * vx + vy * vy);
	/* How steep the track itself is, whichever way the rider faces: for refusing to get
	 * off on a face too steep to stand on. */
	g_trackSteep = atan2f(fabsf(dz), horizontal) * 57.29578f;
	g_trackSteepOk = true;

	float h = *(const float *)(player + OFF_REFR_HEADING);
	if (!isfinite(h) || horizontal < 30.0f || !TrackPointAt(pos, 24.0f, recent))
		return;
	/* Standing still: hold. (Turned round on the spot, the last movement points backwards
	 * against the new heading just as a reverse does; a reverse is moving now.) */
	if (g_clock - g_trackAddedAt > 0.3f)
		return;
	/* Which way the bike just moved, against the way it faces: forward, backward (a real
	 * reverse), or neither (turned on the spot: test 10 flipped the pitch's sign there). */
	float sh = sinf(h), ch = cosf(h);
	float mx = pos[0] - recent[0], my = pos[1] - recent[1], moved = sqrtf(mx * mx + my * my);
	float along = vx * sh + vy * ch, way = moved > 1.0f ? (mx * sh + my * ch) / moved : 0.0f;
	if (way > 0.7f && along > 0.5f * horizontal)
		g_trackPitch = atan2f(dz, along) * 57.29578f;
	else if (way < -0.7f && along < -0.5f * horizontal)
		g_trackPitch = atan2f(-dz, -along) * 57.29578f;   /* reversing down a hill: the nose stays up */
	else
		return;   /* turning: hold */
	g_trackPitchOk = true;
	g_hadTrackPitch = true;
}

/* ------------------------------------------------------------------------- */
/* Knocking enemies over (test 40's wish)                                    */
/* ------------------------------------------------------------------------- */

/* An actor the rays see ahead is asked about (CMB_RamSeenHi/Lo: its form id's halves, then
 * CMB_RamSeen: the ask's number); CMB_RamScript answers in CMB_RamOk (the number: yes; minus
 * it: no). Only for a yes, at CMB_RamMinSpeed or faster, does the throttle stay open for it;
 * Lead seconds of the speed before the front wheel's edge reaches it the hit is told
 * (CMB_RamHitSpeed, then CMB_RamHit: the number of the ask said yes to) and the script pushes
 * it away; for Pass seconds after, its capsule is let by. Anything else about an actor (no
 * answer yet, a no, too slow, too big) is braked for as before.
 * Test 41: on by default ([Ram] Enabled is the developer's switch, the MCM's "Knock enemies
 * over" the player's); the bike loses speed at a hit (the tester's answer), the
 * throttle held to HitKeep of the speed at the hit for HitHold seconds (AfterInput); two hits
 * are told RAM_HIT_GAP apart at least, a later one waiting (the script polls every 0.1 s and
 * reads the last hit only: of two told within one poll the first would never be pushed); and
 * the face rays, the actor ray and WallAhead pass through an actor to be knocked over, so
 * what is behind it (a second raider, a wall, an actor said no to) is seen and asked about or
 * braked for in time, not only once the first is out of the way. */
#define RAM_HIT_GAP 0.12f   /* seconds between two writes of CMB_RamHit: over the script's 0.1 s poll */
enum { RAM_ASKING, RAM_YES, RAM_NO, RAM_HIT, RAM_TOO_BIG };
typedef struct {
	uintptr_t ref;
	uint32_t id;
	int ask, askPrev, okAsk;   /* the last two asks' numbers, and the one said yes to */
	int state;
	float askedAt, askPrevAt;  /* when the last two asks were made (an answer to either is timed from its own) */
	float askLoggedAt, answeredAt, seenAt, hitAt, hitSpeed, stillLoggedAt;
	bool slowLogged, freeLogged, goneLogged;
	bool toTell;               /* hit, not yet told: the hit before it was told under RAM_HIT_GAP ago */
} RamEntry;
static RamEntry g_rams[8];
static int g_ramAskNo;            /* the last ask's number (from CMB_RamSeen at each ride start) */
static int g_ramOkRead;           /* the CMB_RamOk last acted on */
static int g_ramRaceOk;           /* 0 not checked this ride, 1 the races read right (the rider's), -1 not */
static bool g_ramFoundLogged, g_ramLostLogged;
static float g_ramToldAt = -100.0f;      /* the last hit told (CMB_RamHit written) */
static float g_ramSlowUntil = -100.0f;   /* a hit's loss of speed: the throttle held to g_ramSlowTo (of the top) until then (AfterInput) */
static float g_ramSlowTo = 1.0f;

static bool RamReady(void)
{
	return g_ramOn && g_ramGlobals[0] && GlobalValue(g_ramGlobals[6]) > 0.5f;
}

static float RamMinSpeed(void)
{
	float v = GlobalValue(g_ramGlobals[7]);
	return v >= 0.0f && v < 100000.0f ? v : 450.0f;
}

/* At every ride start (a load starts one too): the numbering goes on from the global's, so an
 * answer to an ask of an earlier ride or save can't be taken for one of this ride's. A hit
 * still to tell and a loss of speed end with the ride. */
static void RamReset(void)
{
	memset(g_rams, 0, sizeof(g_rams));
	g_ramAskNo = g_ramGlobals[2] ? (int)GlobalValue(g_ramGlobals[2]) : 0;
	if (g_ramAskNo < 0 || g_ramAskNo >= RAM_MAX_ASK)
		g_ramAskNo = 0;
	g_ramOkRead = g_ramGlobals[3] ? (int)GlobalValue(g_ramGlobals[3]) : 0;
	g_ramRaceOk = 0;
	g_ramFoundLogged = g_ramLostLogged = false;
	g_ramToldAt = g_ramSlowUntil = -100.0f;
	g_ramSlowTo = 1.0f;
	g_rayLetByCount = 0;
}

static bool UnderOrAt(uintptr_t obj, uintptr_t root)
{
	for (int i = 0; obj && i < 24; i++) {
		if (obj == root)
			return true;
		obj = ReadPtr(obj + OFF_PARENT);
	}
	return false;
}

/* The actor whose 3D a ray hit: up the parents to a node whose user data (+0x110) holds a
 * reference, as the game's FindReferenceFor3D walks; taken only if that is an Actor (its form
 * type and RTTI) whose own loaded 3D root is that node or above the hit: a pointer that isn't
 * one can't pass. Not the rider. Why not in `why`. */
static uintptr_t ActorFor3D(uintptr_t hit, char *why, size_t whySize)
{
	uintptr_t obj = hit;
	for (int i = 0; obj && i < 24; i++) {
		if (!IsA(obj, RTTI_AVOBJECT))
			break;
		uintptr_t ref = ReadPtr(obj + OFF_AV_USER_DATA);
		if (ref) {
			if (!Accessible(ref, 0x20, false) || !GetCOL(ref)) {
				snprintf(why, whySize, "the user data of '%.40s' (+0x110) holds %p, not a form", OrNone(ObjectName(obj)), (void *)ref);
				return 0;
			}
			uint8_t type = *(const uint8_t *)(ref + OFF_FORM_TYPE);
			if (type != FORM_TYPE_ACHR || !IsA(ref, RTTI_ACTOR)) {
				snprintf(why, whySize, "the user data of '%.40s' (+0x110) is a %.40s (form type 0x%02X), not an actor", OrNone(ObjectName(obj)), OrNone(ObjectTypeName(ref)), type);
				return 0;
			}
			uintptr_t root = RefRoot3D(ref);
			if (!root || !UnderOrAt(hit, root)) {
				snprintf(why, whySize, "the user data of '%.40s' (+0x110) is actor %08X, whose 3D isn't above the hit", OrNone(ObjectName(obj)), *(const uint32_t *)(ref + OFF_FORM_ID));
				return 0;
			}
			if (ref == Player()) {
				snprintf(why, whySize, "the rider");
				return 0;
			}
			return ref;
		}
		obj = ReadPtr(obj + OFF_PARENT);
	}
	snprintf(why, whySize, "no reference in the user data (+0x110) of '%.40s' or above it", OrNone(ObjectName(hit)));
	return 0;
}

/* The actor behind a hit on an actor's capsule, logged the first time each way per ride. */
static uintptr_t RamActor(uintptr_t hit)
{
	char why[200];
	uintptr_t actor = ActorFor3D(hit, why, sizeof(why));
	if (actor && !g_ramFoundLogged) {
		g_ramFoundLogged = true;
		Log("rams: actors are found from their 3D: '%s' (layer 30) gives actor %08X (user data +0x110)", OrNone(ObjectName(hit)), *(const uint32_t *)(actor + OFF_FORM_ID));
	} else if (!actor && !g_ramLostLogged && strcmp(why, "the rider") != 0) {
		g_ramLostLogged = true;
		Log("rams: the 3D a ray hit ('%s', layer 30) gives no actor: %s; it's braked for", OrNone(ObjectName(hit)), why);
	}
	return actor;
}

static const char *RaceSizeName(int size)
{
	static const char *const names[4] = { "small", "medium", "large", "extra large" };
	return size >= 0 && size <= 3 ? names[size] : "unreadable";
}

/* An actor's race: its size class and flags (RACE DATA), its editor ID; -1 unreadable. */
static int RaceSize(uintptr_t actor, uint32_t *flags, const char **edid)
{
	*flags = 0;
	*edid = NULL;
	uintptr_t race = ReadPtr(actor + OFF_ACTOR_RACE);
	if (!race || !Accessible(race, OFF_RACE_EDITOR_ID + 8, false) || *(const uint8_t *)(race + OFF_FORM_TYPE) != FORM_TYPE_RACE || !IsA(race, RTTI_RACE))
		return -1;
	uint32_t size = *(const uint32_t *)(race + OFF_RACE_SIZE);
	*flags = *(const uint32_t *)(race + OFF_RACE_FLAGS);
	*edid = EntryString(ReadPtr(race + OFF_RACE_EDITOR_ID));
	return size <= 3 ? (int)size : -1;
}

/* Once a ride: the rider's own race must read as a playable one of a size class, or the
 * plugin sets no size limit (the script's CMB_RamTooBig still does). */
static void RamCheckRace(void)
{
	uint32_t flags = 0;
	const char *edid = NULL;
	uintptr_t player = Player();
	int size = player ? RaceSize(player, &flags, &edid) : -1;
	g_ramRaceOk = size >= 0 && (flags & RACE_PLAYABLE) ? 1 : -1;
	Log("rams: the rider's race reads %s: size %s, flags %08X%s", OrNone(edid), RaceSizeName(size), flags,
	    g_ramRaceOk > 0 ? ": races are read for the size limit" : " (not a playable race of a size): no size limit from the plugin, CMB_RamTooBig's only");
}

static RamEntry *RamEntryFor(uintptr_t ref, uint32_t id, bool add)
{
	RamEntry *unused = NULL, *oldest = NULL;
	for (int i = 0; i < 8; i++) {
		RamEntry *e = &g_rams[i];
		if (e->ref && e->ref == ref && e->id == id)
			return e;
		if (!e->ref && !unused)
			unused = e;
		if (!e->toTell && (!oldest || e->seenAt < oldest->seenAt))
			oldest = e;   /* never one whose hit is still to tell */
	}
	if (!add || (!unused && !oldest))
		return NULL;
	RamEntry *e = unused ? unused : oldest;
	memset(e, 0, sizeof(*e));
	e->ref = ref;
	e->id = id;
	e->askedAt = e->askPrevAt = e->askLoggedAt = -100.0f;
	return e;
}

static void RamAsk(RamEntry *e, float ahead, float v, const char *which, const char *race)
{
	if (++g_ramAskNo > RAM_MAX_ASK)
		g_ramAskNo = 1;
	bool first = e->ask == 0;
	e->askPrev = e->ask;
	e->askPrevAt = e->askedAt;
	e->ask = g_ramAskNo;
	e->askedAt = (float)g_clock;
	e->state = RAM_ASKING;
	SetGlobal(g_ramGlobals[0], (float)(e->id >> 16));
	SetGlobal(g_ramGlobals[1], (float)(e->id & 0xFFFFu));
	SetGlobal(g_ramGlobals[2], (float)e->ask);   /* last: the script reads the halves after it */
	if (first || (float)g_clock - e->askLoggedAt >= 5.0f) {
		e->askLoggedAt = (float)g_clock;
		Log("rams: %08X%s seen %.0f past the front wheel at %.0f a second (%s): asked the script (ask %d)%s", e->id, race, ahead, v, which, e->ask,
		    first ? "" : ", again: no answer, or a no a while ago");
	}
}

/* An actor seen ahead, by the actor ray or the face rays: asked about, unless too big. */
static void RamSeen(uintptr_t actor, float ahead, float v, const char *which)
{
	uint32_t id = *(const uint32_t *)(actor + OFF_FORM_ID);
	RamEntry *e = RamEntryFor(actor, id, true);
	if (!e)
		return;   /* all eight waiting to tell a hit: braked for */
	e->seenAt = (float)g_clock;
	if (e->state == RAM_TOO_BIG || e->state == RAM_HIT || e->state == RAM_YES)
		return;
	char race[96] = "";
	if (e->ask == 0) {
		if (g_ramRaceOk == 0)
			RamCheckRace();
		if (g_ramRaceOk > 0) {
			uint32_t flags = 0;
			const char *edid = NULL;
			int size = RaceSize(actor, &flags, &edid);
			bool noKnock = g_ramNoKnockdowns && (flags & RACE_NO_KNOCKDOWNS);
			if (size > g_ramMaxSize || size < 0 || noKnock) {
				e->state = RAM_TOO_BIG;
				Log("rams: %08X (race %s: size %s, flags %08X) %s: braked for as before", id, OrNone(edid), RaceSizeName(size), flags,
				    size < 0 ? "has a race that can't be read" : noKnock ? "can't be knocked down (No Knockdowns)" : "is too big (MaxSize)");
				return;
			}
			snprintf(race, sizeof(race), " (race %.40s: %s)", OrNone(edid), RaceSizeName(size));
		}
	}
	float wait = e->state == RAM_NO ? g_ramAskAgainNo : g_ramAskAgain;
	if (e->ask == 0 || (float)g_clock - e->askedAt >= wait)
		RamAsk(e, ahead, v, which, race);
}

/* The hit told: the speed, then the ask's number (the script reads the number first and the
 * speed after it). */
static void RamTell(RamEntry *e)
{
	SetGlobal(g_ramGlobals[4], e->hitSpeed);
	SetGlobal(g_ramGlobals[5], (float)e->okAsk);   /* last */
	g_ramToldAt = (float)g_clock;
	e->toTell = false;
}

/* Every frame while riding: the script's answers, a hit still to tell, and the entries' ends. */
static void RamFrame(void)
{
	if (!g_ramOn || !g_ramGlobals[0])
		return;
	float now = (float)g_clock;
	int ok = (int)GlobalValue(g_ramGlobals[3]);
	if (ok != g_ramOkRead) {
		g_ramOkRead = ok;
		int n = ok < 0 ? -ok : ok;
		for (int i = 0; n && i < 8; i++) {
			RamEntry *e = &g_rams[i];
			if (!e->ref || (e->ask != n && e->askPrev != n) || (e->state != RAM_ASKING && e->state != RAM_NO))
				continue;
			e->state = ok > 0 ? RAM_YES : RAM_NO;
			e->okAsk = ok > 0 ? n : 0;
			e->answeredAt = now;
			Log("rams: %08X %s (ask %d), %.0f ms after the ask", e->id, ok > 0 ? "may be knocked over, the script says" : "is not to be knocked over, the script says: braked for",
			    n, (now - (n == e->ask ? e->askedAt : e->askPrevAt)) * 1000.0f);
		}
	}
	/* A hit that waited (two within RAM_HIT_GAP): the earliest first, one a gap. */
	if (now - g_ramToldAt >= RAM_HIT_GAP) {
		RamEntry *next = NULL;
		for (int i = 0; i < 8; i++)
			if (g_rams[i].ref && g_rams[i].toTell && (!next || g_rams[i].hitAt < next->hitAt))
				next = &g_rams[i];
		if (next) {
			float before = now - g_ramToldAt;
			RamTell(next);
			Log("rams: %08X's hit told the script (ask %d) %.0f ms after the hit, %.0f ms after the one before it", next->id, next->okAsk, (now - next->hitAt) * 1000.0f,
			    before * 1000.0f);
		}
	}
	for (int i = 0; i < 8; i++) {
		RamEntry *e = &g_rams[i];
		if (!e->ref)
			continue;
		if (e->state == RAM_HIT) {
			if (!e->goneLogged && now - e->seenAt >= 0.1f) {
				e->goneLogged = true;
				Log("rams: %08X gone from the rays %.2f s after the hit", e->id, e->seenAt - e->hitAt > 0.0f ? e->seenAt - e->hitAt : 0.0f);
			}
			if (now - e->hitAt >= g_ramPass + 3.0f && !e->toTell)
				e->ref = 0;
		} else if (now - e->seenAt >= 3.0f) {
			e->ref = 0;   /* out of sight: asked afresh next time */
		}
	}
}

/* Test 41's answer: the bike loses speed at a hit. The throttle is held to HitKeep of the speed
 * at the hit for HitHold seconds (AfterInput), then builds up again from there as from a slow
 * ride (Accel, Lead); a second hit within the hold holds it to the lower. What was done, for
 * the hit's line, in `out`. */
static void RamSlow(float v, char *out, size_t size)
{
	*out = 0;
	if (!(g_ramHitHold > 0.0f) || !(g_ramHitKeep < 1.0f) || !(g_fullSpeed > 0.0f))
		return;
	if (!g_throttleOn) {
		snprintf(out, size, "; the speed is the game's (Throttle=0): not slowed");
		return;
	}
	float now = (float)g_clock, to = g_ramHitKeep * v / g_fullSpeed;
	if (now < g_ramSlowUntil && g_ramSlowTo < to)
		to = g_ramSlowTo;
	g_ramSlowTo = to;
	g_ramSlowUntil = now + g_ramHitHold;
	snprintf(out, size, "; the throttle held to %.0f%% of it (%.0f a second) for %.2f s", g_ramHitKeep * 100.0f, to * g_fullSpeed, g_ramHitHold);
}

/* An actor at axle height ahead (ahead: its hit past the front wheel's edge): true if the
 * throttle stays open for it (a yes at speed, or hit within Pass); tells the hit at Lead. */
static bool RamFree(uintptr_t actor, float ahead, float v)
{
	RamEntry *e = RamEntryFor(actor, *(const uint32_t *)(actor + OFF_FORM_ID), false);
	if (!e)
		return false;
	float now = (float)g_clock;
	e->seenAt = now;
	if (e->state == RAM_HIT) {
		if (now - e->hitAt >= g_ramPass)
			return false;
		if (now - e->stillLoggedAt >= 0.25f) {
			e->stillLoggedAt = now;
			Log("rams: %08X's capsule still %.0f past the front wheel %.2f s after the hit: let by", e->id, ahead, now - e->hitAt);
		}
		return true;
	}
	if (e->state != RAM_YES)
		return false;
	float least = RamMinSpeed();
	if (v < least) {
		if (!e->slowLogged) {
			e->slowLogged = true;
			Log("rams: %08X %.0f past the front wheel at %.0f a second, under CMB_RamMinSpeed's %.0f: not knocked over, braked for", e->id, ahead, v, least);
		}
		return false;
	}
	if (ahead <= v * g_ramLead) {
		e->state = RAM_HIT;
		e->hitAt = e->stillLoggedAt = now;
		e->hitSpeed = v;
		char slow[96];
		RamSlow(v, slow, sizeof(slow));
		bool waiting = false;
		for (int i = 0; i < 8; i++)
			waiting |= g_rams[i].ref && g_rams[i].toTell;
		if (!waiting && now - g_ramToldAt >= RAM_HIT_GAP) {
			RamTell(e);
			Log("rams: %08X hit at %.0f a second, %.0f past the front wheel: told the script (ask %d)%s", e->id, v, ahead, e->okAsk, slow);
		} else {
			e->toTell = true;   /* told by RamFrame once the gap is up */
			Log("rams: %08X hit at %.0f a second, %.0f past the front wheel, %.0f ms after the hit told before it: told the script once %.0f ms have passed "
			    "(ask %d), so its 0.1 s poll reads both%s", e->id, v, ahead, (now - g_ramToldAt) * 1000.0f, RAM_HIT_GAP * 1000.0f, e->okAsk, slow);
		}
		return true;
	}
	if (!e->freeLogged) {
		e->freeLogged = true;
		Log("rams: %08X ahead (%.0f past the front wheel at %.0f a second): to be knocked over, the throttle free", e->id, ahead, v);
	}
	return true;
}

/* A ray's hit on something, if it is an actor's capsule: the actor, else 0. */
static uintptr_t RamHitActor(uint32_t layer, uintptr_t obj)
{
	return layer == LAYER_CHAR_CONTROLLER && obj && RamReady() ? RamActor(obj) : 0;
}

/* The face rays, the actor ray and WallAhead pass through an actor to be knocked over (or just
 * hit), so that what is behind it is seen: its 3D root added to the rays' list (CastRay),
 * three at most. False if it can't be (no 3D, or the list full): the caller gives no verdict
 * then, as before the list. */
static bool RamLetByAdd(uintptr_t actor)
{
	uintptr_t root = RefRoot3D(actor);
	if (!root || g_rayLetByCount >= (int)(sizeof(g_rayLetBy) / sizeof(g_rayLetBy[0])))
		return false;
	g_rayLetBy[g_rayLetByCount++] = root;
	return true;
}

static bool RamLetByHas(uintptr_t obj)
{
	for (int i = 0; i < g_rayLetByCount; i++)
		if (UnderOrAt(obj, g_rayLetBy[i]))
			return true;
	return false;
}

/* The actor ray's look past an actor: one already said yes to at speed, or just hit, is passed
 * through (RamFree says so for the face rays; this one tells nothing). */
static bool RamLetsBy(uintptr_t actor, float v)
{
	RamEntry *e = RamEntryFor(actor, *(const uint32_t *)(actor + OFF_FORM_ID), false);
	if (!e)
		return false;
	float now = (float)g_clock;
	return (e->state == RAM_YES && v >= RamMinSpeed()) || (e->state == RAM_HIT && now - e->hitAt < g_ramPass);
}

/* Every frame: read the ground once (tilt, average, track all use it). */
/* Two rays down, at the front and rear wheels' contact points (the parts file's axles, the
 * bike's own space taken along the heading): the pitch between the two hits, and how far the
 * ground between them sits above the capsule's contact under the rider (the lift that puts
 * the wheels on it). No track lag at a lip or a crest (test 29: the leading wheel went into
 * the new slope). Both rays must hit within 70 units above and 160 below; else the track. */
/* The front ray found a surface higher than the front wheel could climb: a face ahead (test
 * 31: a boulder the capsule stepped up while the front wheel, a wheelbase ahead of it, went
 * into it) or a ceiling. A ray forward at axle height tells them apart; against a face the
 * throttle is cut while it's there (turning or backing off is still the rider's). Not while
 * an obstacle verdict is in force (FaceRays): on top of a stone the front wheel's ray reads
 * the stone's far side as a face (test 35: the bike stopped on everything it could ride over,
 * then went on), and the obstacle's throttle has it. */
static void WallAhead(uintptr_t cell, const float pos[3], float sh, float ch, float hitZ)
{
	float reach = g_frontAxle[1] + 10.0f;
	float a[3] = { pos[0], pos[1], pos[2] + g_wheelRadius }, b[3] = { pos[0] + sh * reach, pos[1] + ch * reach, pos[2] + g_wheelRadius };
	float f = CastRay(cell, a, b);
	if (!(f > 0.0f && f < 1.0f))
		return;
	/* An actor to be knocked over, or just hit: not a face to stop at; the ray again through
	 * it, for what is behind it (rams). */
	for (int n = 0; n < 3; n++) {
		uintptr_t actor = RamHitActor(g_rayLayer, g_rayObj);
		if (!actor || !RamFree(actor, f * reach - g_frontAxle[1] - g_wheelRadius, g_speedAlong))
			break;
		if (!RamLetByAdd(actor)) {
			g_rayLetByCount = 0;
			return;
		}
		f = CastRay(cell, a, b);
		if (!(f > 0.0f && f < 1.0f)) {
			g_rayLetByCount = 0;
			return;
		}
	}
	g_rayLetByCount = 0;
	bool obstacle = (float)g_clock - g_faceObstacleAt < g_obstacleHold;
	if ((float)g_clock - g_wallAheadAt > 1.0f && (float)g_clock - g_wallLoggedAt >= 1.0f && g_wallLogs < 20) {
		g_wallLogs++;
		g_wallLoggedAt = (float)g_clock;
		Log("rays: a face ahead of the front wheel (the ground %.0f above the feet at its contact; something %.0f ahead at axle height): %s", hitZ, f * reach,
		    obstacle ? "while an obstacle is being ridden over: left to the obstacle's throttle" : "the throttle cut while it's there");
	}
	if (!obstacle)
		g_wallAheadAt = (float)g_clock;
}

static void WheelRays(uintptr_t player, bool onGround)
{
	g_wheelPitchOk = false;
	g_wheelZOk = false;
	if (!g_riding || !onGround || !g_partsOk || !player || !Accessible(player + OFF_REFR_HEADING, 4, false) || !RaysReady(player))
		return;
	uintptr_t cell = ReadPtr(player + OFF_REFR_CELL);
	if (!cell || !IsA(cell, RTTI_CELL))
		return;
	const float *pos = (const float *)(player + OFF_REFR_POS);
	float h = *(const float *)(player + OFF_REFR_HEADING), sh = sinf(h), ch = cosf(h);
	float fy = g_frontAxle[1], ry = g_rearAxle[1], z[2] = { 0.0f, 0.0f };
	const float ys[2] = { fy, ry };
	/* Each ray starts above the most the ground can rise to its wheel on a climbable slope
	 * (tan 50 deg of the wheel's reach) and ends 160 below the feet; a hit above that rise is
	 * a branch or a ceiling, not the ground (test 30: from 70 above the feet the front ray
	 * started inside rock on a 33 deg climb and found the ground beneath, 15 deg short). */
	/* Both rays are cast before either is judged (review of test 38's build: the line about a
	 * hit thrown away can then say what the other ray found, which the collapsed-roof case
	 * needed from the rear in the very state the front was thrown away in). Each ray's hit
	 * and its layer are copied before the next cast. */
	/* The rays pass through actors (CastRayGround: their capsules, layer 30, and bodies, 8):
	 * test 39, 01:34:11.5, a radstag in front of the bike, the front ray hit its capsule 107
	 * above the feet ("SkeletonExport, layer 30"), and the pitch's target read 40 to 44 with a
	 * lift of 33 for about 0.6 s: the bike reared up at it. The face rays and WallAhead still
	 * stop at an actor's capsule, so one ahead still holds the throttle. */
	const char *what[2] = { "nothing within reach", "nothing within reach" };
	uint32_t layer[2] = { 0, 0 };
	float rise[2] = { 0.0f, 0.0f };
	bool hit[2] = { false, false }, over[2] = { false, false };
	for (int i = 0; i < 2; i++) {
		rise[i] = fabsf(ys[i]) * 1.1918f + 10.0f;
		float a[3] = { pos[0] + sh * ys[i], pos[1] + ch * ys[i], pos[2] + rise[i] + 20.0f };
		float b[3] = { a[0], a[1], pos[2] - 160.0f };
		float f = CastRayGround(cell, a, b);
		if (!(f > 0.0f && f < 1.0f))
			continue;
		hit[i] = true;
		what[i] = g_rayWhat && *g_rayWhat ? g_rayWhat : "unnamed";
		layer[i] = g_rayLayer;
		z[i] = a[2] + (b[2] - a[2]) * f - pos[2];
		over[i] = z[i] > rise[i];   /* something overhead, or a face ahead taller than a wheel climbs */
	}
	int hand = g_inputMode == INPUT_BACK ? 1 : 0;   /* backing: a hand of its own, so the backing tests always get their lines */
	for (int i = 0; i < 2; i++) {
		/* Logged, one a second (test 38: backing off a station wagon the rays missed, the car's
		 * roof above the front ray's allowed rise, and the log couldn't say what they had found),
		 * from a hand of 10 refilled by one every 6 s (LogHand). */
		if (!(hit[i] && over[i]) || (float)g_clock - g_wheelThrownAt < 1.0f || !LogHandTake(&g_wheelThrownHand[hand]))
			continue;
		int o = 1 - i;
		char other[200];
		if (hit[o])
			snprintf(other, sizeof(other), "the %s wheel's ray hit %s (layer %u) %.0f above the feet%s", o == 0 ? "front" : "rear", what[o], layer[o], z[o], over[o] ? ", over its rise too" : "");
		else
			snprintf(other, sizeof(other), "the %s wheel's ray found nothing within reach", o == 0 ? "front" : "rear");
		g_wheelThrownAt = (float)g_clock;
		Log("rays: the %s wheel's ray hit %s (layer %u) %.0f above the feet, over its rise of %.0f: thrown away (something overhead, or a face taller than a wheel climbs); %s",
		    i == 0 ? "front" : "rear", what[i], layer[i], z[i], rise[i], other);
	}
	/* As before: the front judged first, a miss or a hit over its rise ends the word. */
	if (!hit[0]) {
		g_wheelRaysMissed++;
		return;
	}
	if (over[0]) {
		g_wheelRaysMissed++;
		WallAhead(cell, pos, sh, ch, z[0]);
		return;
	}
	if (!hit[1] || over[1]) {
		g_wheelRaysMissed++;
		return;
	}
	float base = fy - ry;
	if (!(base > 10.0f))
		return;
	g_wheelZ[0] = z[0];
	g_wheelZ[1] = z[1];
	g_wheelZOk = true;
	float pitch = atan2f(z[0] - z[1], base) * 57.29578f;
	g_wheelHist[g_wheelHistAt] = pitch;
	g_wheelHistAt = (g_wheelHistAt + 1) % 3;
	if (g_wheelHistN < 3)
		g_wheelHistN++;
	if (g_wheelHistN == 3) {   /* the median of the last three: a one-frame hole or lip doesn't count */
		float x = g_wheelHist[0], y = g_wheelHist[1], w = g_wheelHist[2];
		pitch = x > y ? (y > w ? y : (x > w ? w : x)) : (x > w ? x : (y > w ? w : y));
	}
	g_wheelPitch = pitch;
	g_wheelLift = z[1] + (0.0f - ry) / base * (z[0] - z[1]);   /* the ground line at the contact under the rider */
	g_wheelPitchOk = true;
	/* The hits logged under a steep pitch, or where a wheel hangs at its droop with the pitch
	 * over 10 deg, one line a second (test 38's collapsed roof: pitch 36 to 41 from the wheels
	 * with the lift 0.3 to 1.2, the rear ray finding something about 30 below the capsule's
	 * contact while the front found 60 above, so the rear wheel sat under the roof the capsule
	 * stood on; whether the rear ray went through the roof or past its edge the log couldn't
	 * say). The offsets are last frame's. From a hand of 10 lines refilled by one every 6 s,
	 * one of its own while backing (LogHand; test 39: the 30 a ride were spent by 01:35:02,
	 * before the backing tests). */
	bool atDroop = g_suspension && g_suspDroop > 0.0f && fabsf(g_wheelPitch) > 10.0f && (g_wheelOffset[0] <= 0.2f - g_suspDroop || g_wheelOffset[1] <= 0.2f - g_suspDroop);
	if ((fabsf(g_wheelPitch) >= 25.0f || atDroop) && (float)g_clock - g_wheelLoggedAt >= 1.0f && LogHandTake(&g_wheelHand[hand])) {
		g_wheelLoggedAt = (float)g_clock;
		Log("rays: the wheels' rays: the front hit %.0f above the feet (%s, layer %u), the rear %.0f (%s, layer %u): pitch %.1f deg, the line at the contact %.1f",
		    z[0], what[0], layer[0], z[1], what[1], layer[1], g_wheelPitch, g_wheelLift);
	}
}

/* A face ahead, seen in time (test 32: the down-ray's word came with the face already at
 * the wheel, 16 to 81 ahead at axle height): two rays forward along the bike's pitched axis,
 * at axle height and near the top of the wheel, as far as FaceLook seconds of the speed past
 * the front wheel. Both hitting at about the same distance is a face (a slope under the climb
 * limit puts the upper hit further on by its rise over its tangent; a step lower than the
 * wheel's top misses the upper ray); the throttle is eased off with the distance left to it,
 * to nothing at the wheel, so the bike stops short. Turning or backing off is the rider's. */
/* The verdict has state (test 35: on top of a stone the rays read its far side, behind the
 * front wheel's edge, as a wall one frame and an obstacle the next, and the throttle went
 * 0%, 40%, 0%): a hit behind the wheel's edge is under the bike, an obstacle it has climbed
 * onto, never a wall; and for ObstacleHold seconds after an obstacle verdict a wall needs its
 * hit ahead of the wheel on WallFrames frames running before it counts (an obstacle till
 * then). A line is logged when the verdict's kind changes, else at most one a second. */
static void FaceRays(uintptr_t player, bool onGround)
{
	g_faceEase = 1.0f;
	int seen = g_wallSeen;   /* counts on only through frames whose raw verdict is a wall ahead of the wheel */
	g_wallSeen = 0;
	if (!g_riding || !onGround || !g_partsOk || g_faceLook <= 0.0f || !player || !Accessible(player + OFF_REFR_HEADING, 4, false) || !RaysReady(player) ||
	    (!(g_throttleOn && g_throttle > 0.0f) && g_speedAlong < 30.0f)) {   /* standing, backing, or no throttle: nothing to ease */
		g_faceKind = 0;   /* no rays cast: the verdict is over (review: a stop and a start on open ground said "nothing ahead now (was an obstacle)") */
		g_faceNoneSince = g_faceSince = -1.0f;
		return;
	}
	uintptr_t cell = ReadPtr(player + OFF_REFR_CELL);
	if (!cell || !IsA(cell, RTTI_CELL)) {
		g_faceKind = 0;   /* no rays either (review of test 36's build) */
		g_faceNoneSince = g_faceSince = -1.0f;
		return;
	}
	const float *pos = (const float *)(player + OFF_REFR_POS);
	float h = *(const float *)(player + OFF_REFR_HEADING), sh = sinf(h), ch = cosf(h);
	float p = g_pitchNow / 57.29578f, cp = cosf(p), sp = sinf(p);
	float fwd[3] = { sh * cp, ch * cp, sp }, up[3] = { -sh * sp, -ch * sp, cp };
	float R = g_wheelRadius > 1.0f ? g_wheelRadius : 30.0f, wheelFront = g_frontAxle[1] + R;
	float v = g_speedAlong > 0.0f ? g_speedAlong : 0.0f, span = v * g_faceLook + 5.0f, L = wheelFront + span;
	/* Two rays: at axle height and at 1.5 radii (test 34's wish: ride over a fallen tree or a
	 * knee-high stone while slowing). Nothing at axle height: nothing ahead. Something there
	 * and nothing at 1.5 radii: an obstacle lower than that, ridden over at ObstacleThrottle
	 * with the wheel's bump lift. Something at both: the slope between the hits, over the
	 * bike's pitch: WallAngle or steeper is a wall, the throttle eased off to nothing at the
	 * wheel; between ObstacleAngle (or the climb limit, if that is higher) and that, an
	 * obstacle; under it, a slope the bike climbs, no verdict (test 37: ten of 39 throttle
	 * holds were faces of 45 to 49 degrees, over the rays' climb value of 45, which the
	 * controller climbs at 47). The lower-only obstacle goes by LowObstacleAngle (test 38). */
	/* A third ray at half a radius tells a low obstacle from a slope whose hit at 1.5 radii
	 * lies beyond the rays' reach (review: a climbable slope's approach read as an obstacle). */
	float climb = GlobalValue(g_tiltGlobal);
	if (!(climb >= 20.0f))
		climb = 45.0f;
	float obstacleAngle = g_obstacleAngle > climb ? g_obstacleAngle : climb;
	float lowObstacleAngle = g_lowObstacleAngle > climb ? g_lowObstacleAngle : climb;
	/* The upper ray is cast further than the axle ray by the run a face at ObstacleAngle (or
	 * the climb limit) needs for the extra half radius, and 2 over: test 38 cast it as far as
	 * the axle ray, so on a 54 deg face its hit lay 15 / tan 54 = 11 units further on and often
	 * beyond the ray's end, and "lower than 1.5 radii" was the ray's reach, not the thing's
	 * height (the holds to 55% were mostly five low rock faces of 50 to 57 deg). A face the
	 * longer ray misses is lower than 1.5 radii indeed. The half-radius ray keeps L. */
	float L1 = L + 0.5f * R / tanf(obstacleAngle / 57.29578f) + 2.0f;
	float heights[3] = { R, 1.5f * R, 0.5f * R }, lengths[3] = { L, L1, L }, d[3];
	const char *hitWhat = NULL;   /* what the axle-height ray hit, and its layer (test 35: bushes with food items stopped the bike like a wall) */
	uint32_t hitLayer = 0;
	uintptr_t hitObj = 0;
	/* The actor ray: at axle height, ActorLook seconds of the speed past the front wheel, so the
	 * script's answer is in before the face rays reach the actor (rams); through one already to
	 * be knocked over, to the next (two raiders one behind the other: test 41's check of the
	 * hits' spacing). */
	g_rayLetByCount = 0;
	if (RamReady() && g_ramLook > g_faceLook && v >= 0.8f * RamMinSpeed()) {
		float La = wheelFront + v * g_ramLook + 5.0f, a[3], b[3];
		for (int k = 0; k < 3; k++) {
			a[k] = pos[k] + up[k] * R;
			b[k] = a[k] + fwd[k] * La;
		}
		for (int n = 0; n < 3; n++) {
			float f = CastRay(cell, a, b);
			uintptr_t actor = f > 0.0f && f < 1.0f ? RamHitActor(g_rayLayer, g_rayObj) : 0;
			if (!actor)
				break;
			RamSeen(actor, f * La - wheelFront, v, "the actor ray");
			if (!RamLetsBy(actor, v) || !RamLetByAdd(actor))
				break;
		}
		g_rayLetByCount = 0;
	}
	float ahead = 0.0f, slope = 0.0f;
	for (;;) {   /* once, or again past each actor let by (three at most: RamLetByAdd) */
		for (int i = 0; i < 3; i++) {
			float a[3], b[3];
			for (int k = 0; k < 3; k++) {
				a[k] = pos[k] + up[k] * heights[i];
				b[k] = a[k] + fwd[k] * lengths[i];
			}
			float f = CastRay(cell, a, b);
			d[i] = f > 0.0f && f < 1.0f ? f * lengths[i] : -1.0f;   /* the hit's distance: the fraction of its own ray's length */
			if (i == 0) {
				hitWhat = g_rayWhat;   /* before the next cast overwrites them */
				hitLayer = g_rayLayer;
				hitObj = d[0] >= 0.0f ? g_rayObj : 0;
			}
		}
		ahead = d[0] - wheelFront;
		/* An actor's capsule at axle height: asked about, and if it's to be knocked over at this
		 * speed (or was just hit), no verdict for it: the three rays again through it, for what
		 * is behind it (rams). */
		uintptr_t actor = d[0] >= 0.0f ? RamHitActor(hitLayer, hitObj) : 0;
		if (!actor)
			break;
		RamSeen(actor, ahead, v, "the face rays");
		if (!RamFree(actor, ahead, v))
			break;
		if (!RamLetByAdd(actor)) {
			g_rayLetByCount = 0;
			g_faceKind = 0;   /* three passed already: no verdict, the throttle free */
			g_faceNoneSince = g_faceSince = -1.0f;
			return;
		}
	}
	g_rayLetByCount = 0;
	const char *what = NULL;
	bool wall = false;
	if (d[0] >= 0.0f && d[1] < 0.0f) {
		/* Nothing at 1.5 radii: lower than that (the upper ray reaches where a face at
		 * ObstacleAngle would put its hit). The slope between half a radius and the axle says
		 * whether it holds the throttle: LowObstacleAngle or steeper (never under the climb
		 * limit); under it no verdict, the suspension and the bump lift take it (test 38: five
		 * low rock faces of 50 to 57 deg, just over ObstacleAngle, held the throttle, "some that
		 * should theoretically let me ride over them"). */
		if (d[2] >= 0.0f) {
			float run = d[0] - d[2];
			slope = g_pitchNow + atan2f(heights[0] - heights[2], run > 0.0f ? run : 0.0f) * 57.29578f;
			if (slope >= lowObstacleAngle)
				what = "an obstacle lower than 1.5 wheel radii";
		}
	} else if (d[0] >= 0.0f) {
		float run = d[1] - d[0];
		slope = g_pitchNow + atan2f(heights[1] - heights[0], run > 0.0f ? run : 0.0f) * 57.29578f;
		if (slope >= g_wallAngle) {   /* walls stay at WallAngle, wherever ObstacleAngle is set */
			wall = true;
			what = "a wall";
		} else if (slope >= obstacleAngle) {
			what = "a face under WallAngle, an obstacle";
		}
	}
	if (!what) {
		/* Nothing ahead (or a slope under the climb limit): the throttle free. Logged as gone
		 * once it has been for a quarter second (at the rays' reach a hit comes and goes by
		 * the frame as the speed, and with it the reach, changes). */
		if (g_faceKind) {
			if (g_faceNoneSince < 0.0f) {
				g_faceNoneSince = (float)g_clock;
			} else if ((float)g_clock - g_faceNoneSince >= 0.25f) {
				/* The verdict that stood, named (test 40: stop 1's "nothing ahead now" at 15:40:00.546
				 * ended a verdict that was never logged, and what it had been couldn't be told). */
				if (LogHandTake(&g_faceHand)) {
					g_faceLoggedAt = (float)g_clock;
					Log("rays: nothing ahead now (was %s, %.0f deg, %s, layer %u, for %.1f s): the throttle free", g_faceKind == 2 ? "a wall" : "an obstacle",
					    g_faceLastSlope, g_faceLastWhat[0] ? g_faceLastWhat : "unnamed", g_faceLastLayer, g_faceSince >= 0.0f ? g_faceNoneSince - g_faceSince : 0.0f);
				}
				g_faceKind = 0;
				g_faceSince = -1.0f;
			}
		}
		return;
	}
	g_faceNoneSince = -1.0f;
	/* The raw verdict, then the state: (a) a wall whose axle-height hit is behind the front
	 * wheel's edge, with the front wheel's down-ray finding the ground half a radius or more
	 * above the capsule's contact, is under the bike: an obstacle it has climbed onto (half a
	 * radius behind at least: stopped against a wall the bike sits at the edge itself, a unit
	 * or two either way; test 35's hits were 63 to 126 behind, the front wheel's ray 20 to 60
	 * up; without that, a wall the bike has nosed or turned into, its front wheel through it,
	 * is a wall still: review); (b) while an obstacle verdict is in force, a wall needs its
	 * hit ahead of the wheel on WallFrames frames running; (c) a raw obstacle verdict whose
	 * axle-height hit is at or behind the front wheel's edge is under the bike already (test
	 * 37: 16 of 39 throttle holds had the hit 0 to 105 behind the edge, the ground under the
	 * pitched bike): it sets the hold, for WallAhead and the bump cap, but leaves the throttle
	 * free, the suspension's to take. */
	char note[96] = "";
	bool forNow = false;   /* a wall held back by (b): it doesn't renew the hold, or a wall the bike stops at (its hit at the wheel's edge) would stay an obstacle for good */
	bool underBike = false, atWheel = !wall && ahead <= 0.0f;
	bool onIt = g_wheelZOk && g_wheelZ[0] > 0.5f * R;   /* the front wheel's ray lands well above the capsule's contact: the bike is on the thing */
	if (wall && ahead > 0.0f)
		g_wallSeen = seen + 1;
	if (wall && ahead < -0.5f * R && onIt) {
		wall = false;
		underBike = true;
		snprintf(note, sizeof(note), " (under the bike, the front wheel %.0f up on it: an obstacle, not a wall)", g_wheelZ[0]);
	} else if (wall && (float)g_clock - g_faceObstacleAt < g_obstacleHold && g_wallSeen < g_wallFrames) {
		wall = false;
		forNow = true;
		snprintf(note, sizeof(note), " (a wall only after %d frames ahead of the wheel: an obstacle for now)", g_wallFrames);
	} else if (wall && ahead < -0.5f * R) {
		snprintf(note, sizeof(note), " (behind the wheel's edge, but the front wheel's ray finds the ground %.0f up: a wall the bike has nosed into)", g_wheelZOk ? g_wheelZ[0] : 0.0f);
	} else if (atWheel) {
		snprintf(note, sizeof(note), " (at the wheel: the throttle free, the suspension's)");
	}
	if (!wall && !forNow)
		g_faceObstacleAt = (float)g_clock;
	float ease;
	if (wall)
		ease = ahead <= 0.0f ? 0.0f : ahead >= span ? 1.0f : ahead / span;
	else if (atWheel || (underBike && g_obstacleThrottle <= 0.0f))
		ease = 1.0f;   /* (c); and ObstacleThrottle=0 stops short of obstacles, but on top of one there's nothing ahead to stop short of (review) */
	else if (g_obstacleThrottle <= 0.0f)
		ease = ahead <= 0.0f ? 0.0f : ahead >= span ? 1.0f : ahead / span;   /* a wall held back as an obstacle for now, at the wheel: stopped at too */
	else
		ease = g_obstacleThrottle;
	g_faceEase = ease;
	int kind = wall ? 2 : 1;
	if (!g_faceKind)
		g_faceSince = (float)g_clock;   /* a verdict begins */
	g_faceLastSlope = slope;
	snprintf(g_faceLastWhat, sizeof(g_faceLastWhat), "%s", hitWhat && *hitWhat ? hitWhat : "");
	g_faceLastLayer = hitLayer;
	if (((kind != g_faceKind && (float)g_clock - g_faceLoggedAt >= 0.25f) || (float)g_clock - g_faceLoggedAt >= 1.0f) && LogHandTake(&g_faceHand)) {
		g_faceLoggedAt = (float)g_clock;
		Log("rays: %s ahead (%.0f deg): %.0f past the front wheel at axle height (%s, layer %u), the throttle %s %.0f%%%s", what, slope, ahead,
		    hitWhat && *hitWhat ? hitWhat : "unnamed", hitLayer, wall ? "eased to" : atWheel ? "left at" : "held to", ease * 100.0f, note);
	}
	g_faceKind = kind;
}

/* Climbing low things, stage 1 (test 40, finding 8: off-road north of Red Rocket, forward held,
 * the bike stopped dead four times in three minutes at fallen trunks and stumps, 900 to near 0
 * in half a second and stuck 1 to 3 s, the controller's ground normal reading 35-65 deg, the
 * trunk's side, while the wheels' rays read 5-20). What stops it is the player's capsule (radius
 * 18, controller+0x370): the bike is a wheelbase long, the trunk lies under its middle between
 * the wheels' rays, and the 47 deg limit makes the capsule's contact with it a wall. The face
 * rays start at half a wheel radius and need the axle-height ray to hit, so nothing lower than
 * about 30 at the capsule is seen. Two rays from the capsule's axis along the bike's pitched
 * axis, at 4 and 10 above the feet (4: 18 (1 - cos 47) = 5.7 is the lowest edge the 47 limit
 * can't take), every frame while forward is held; once stalled (the throttle held to the
 * measured speed, the speed along under 80, for 0.2 s) two more lines 12 to either side (test
 * 40's stump beside the bike). Their hits make a face if the pitch and the angle between them
 * come to the limit less 5 or more (or the ray at 10 finds nothing: a thing lower than that);
 * it is at the capsule if within its radius + 6 + a tenth of a second of the speed (the limit
 * written about 0.1 s before contact: 24 at rest, 114 at 900); it is not an actor (layers 30 and
 * 8); and it is low if a ray at ClimbTop above the feet finds nothing within 45 past it (a step
 * taller than a wheel radius, or a slope that goes on, is refused), the face rays have no wall
 * verdict and WallAhead no cut in the last quarter second, and the wheels' line is pitched
 * ClimbMaxPitch at most (test 41's answer: trunks and stumps, not ledges on rocky slopes; the
 * stops read 5-20, the rock pile 31-37). Then the limit goes to ClimbBoost (ApplySlope's keep-up,
 * later this frame) and stays there ClimbHold after the last such frame. Off at once on the back
 * key, the creep, forward let go, a hit at ClimbTop, a wall verdict, the ride's end, a load and
 * a ride's start; given up after ClimbMax stalled (the speed along under 40) with it on, and not
 * again till the bike has moved 60 along its heading or forward is pressed again. A sharp step
 * of 17 to 32 meets the capsule's upright side, which no limit climbs (f8's capsule model): stage
 * 2 steps up onto it (ClimbStepUp, with the reverse's controller functions; ClimbStep). */
enum { CLIMB_OK, CLIMB_NONE, CLIMB_ACTOR, CLIMB_TALL, CLIMB_WALL, CLIMB_CUT, CLIMB_NOWORD, CLIMB_PITCH, CLIMB_COOL };
typedef struct ClimbLineS {
	float side;                 /* across, + right */
	float d4, d10, dTop, angle; /* the hits' distances along the rays (-1: none), the face's angle */
	const char *what4, *whatTop;
	uint32_t layer4, layerTop;
	bool grazed;                /* nothing at 10, and ground just under the hit at 4: a slope grazed, its angle at most this */
	int why;                    /* CLIMB_*: what this line says */
} ClimbLine;

static float ClimbTop(void)
{
	return g_climbTopSetting > 0.0f ? g_climbTopSetting : (g_wheelRadius > 1.0f ? g_wheelRadius : 30.0f) + 2.0f;
}

static float NormalDegrees(float nz)
{
	return acosf(nz > 1.0f ? 1.0f : nz < -1.0f ? -1.0f : nz) * 57.29578f;
}

/* " | climb 85 for 0.21 s" (", 1 step up" once stage 2 has stepped in this boost) or
 * " | climb off" for the trace (nothing with Climb=0). */
static const char *ClimbWord(void)
{
	static char word[64];
	if (!g_climb)
		return "";
	if (g_climbOn)
		snprintf(word, sizeof(word), " | climb %.0f for %.2f s%s", g_climbBoost, (float)g_clock - g_climbSince,
		         g_stepsThisBoost == 1 ? ", 1 step up" : g_stepsThisBoost > 1 ? ", 2 steps up" : "");
	else
		snprintf(word, sizeof(word), " | climb off");
	return word;
}

/* The boost off at once, said with why (NULL: quietly). */
static void ClimbOff(const char *why)
{
	if (!g_climbOn)
		return;
	g_climbOn = false;
	if (why && LogHandTake(&g_climbHand))
		Log("climb: cut after %.2f s: %s", (float)g_clock - g_climbSince, why);
}

/* The ride's capsule, once (the round-1 dump read radius 0.257175 = 18.0 units, height 1.8288 =
 * 128, step height 0.442912 = 31.0, cast depth 0.479206 = 33.5): what the game uses its step
 * height for isn't known, and whether its mod or timer ever move. */
static void CapsuleFields(uintptr_t ctrl, float f[6])   /* +0x370, +0x374, +0x424, +0x428, +0x42C, +0x430 as they are (0: unreadable); the reverse's push start reads them too */
{
	static const unsigned offs[6] = { 0x370, 0x374, 0x424, 0x428, 0x42C, 0x430 };
	for (int i = 0; i < 6; i++) {
		f[i] = ctrl && Accessible(ctrl + offs[i], 4, false) ? *(const float *)(ctrl + offs[i]) : 0.0f;
		if (!isfinite(f[i]))
			f[i] = 0.0f;
	}
}
static void LogCapsule(uintptr_t ctrl)
{
	float f[6];
	CapsuleFields(ctrl, f);
	float r = f[0] / HAVOK_SCALE, height = f[1] / HAVOK_SCALE;
	bool ok = r >= 10.0f && r <= 30.0f;
	g_capsuleRadius = ok ? r : 18.0f;
	bool heightOk = height >= 60.0f && height <= 250.0f;
	g_capsuleHeight = heightOk ? height : 128.0f;   /* the room a step up needs (stage 2) */
	Log("climb: the capsule radius %.1f, height %.1f (controller+0x370/+0x374); its step height %.1f, mod %.2f for %.2f s (+0x424/+0x428/+0x42C), cast depth %.1f (+0x430); "
	    "low things up to %.1f above the feet climbed with the limit at %g deg while forward is held%s%s%s",
	    r, f[1] / HAVOK_SCALE, f[2] / HAVOK_SCALE, f[3], f[4], f[5] / HAVOK_SCALE, ClimbTop(), g_climbBoost, g_climbStep ? ", sharp steps up to it stepped up onto" : "",
	    ok ? "" : " (the radius isn't 10 to 30: 18 taken)", heightOk ? "" : " (the height isn't 60 to 250: 128 taken for a step's room)");
}

/* One climb ray from o, height above the feet along up, len along fwd: the hit's distance (-1:
 * none), what it hit and its layer. */
static void ClimbCast(uintptr_t cell, const float o[3], const float up[3], const float fwd[3], float height, float len, float *d, const char **what, uint32_t *layer)
{
	float a[3], b[3];
	for (int k = 0; k < 3; k++) {
		a[k] = o[k] + up[k] * height;
		b[k] = a[k] + fwd[k] * len;
	}
	float f = CastRay(cell, a, b);
	*d = f > 0.0f && f < 1.0f ? f * len : -1.0f;
	if (what)
		*what = *d >= 0.0f && g_rayWhat && *g_rayWhat ? g_rayWhat : "unnamed";
	if (layer)
		*layer = *d >= 0.0f ? g_rayLayer : 0;
}

/* What a line's word means, for the lines. */
static void ClimbWhy(int why, const ClimbLine *L, float top, char *out, size_t size)
{
	switch (why) {
	case CLIMB_ACTOR:
		snprintf(out, size, "an actor (%s, layer %u)", L ? L->what4 : "unnamed", L ? L->layer4 : 0);
		break;
	case CLIMB_TALL:
		snprintf(out, size, "something at %.1f above the feet %.0f ahead (%s, layer %u)", top, L ? L->dTop : 0.0f, L ? L->whatTop : "unnamed", L ? L->layerTop : 0);
		break;
	case CLIMB_WALL:
		snprintf(out, size, "a wall ahead (the face rays' verdict)");
		break;
	case CLIMB_CUT:
		snprintf(out, size, "the throttle cut at a face ahead of the front wheel (WallAhead)");
		break;
	case CLIMB_NOWORD:
		snprintf(out, size, "the wheels' rays have had no word for half a second");
		break;
	case CLIMB_PITCH:
		snprintf(out, size, "the wheels' line pitched %.1f (over ClimbMaxPitch, %g)", g_wheelPitch, g_climbMaxPitch);
		break;
	case CLIMB_COOL:
		snprintf(out, size, "cooldown (given up %.1f s ago: not again till the bike has moved 60 along its heading or forward is pressed again)", (float)g_clock - g_climbCoolAt);
		break;
	default:
		snprintf(out, size, "nothing low ahead of the capsule%s", g_faceKind == 2 ? " (the face rays hold it at a wall ahead)" : g_faceEase < 1.0f ? " (the face rays hold the throttle)" : "");
		break;
	}
}

static void ClimbOn(const ClimbLine *L, const float pos[3], float nz, float top)
{
	g_climbOn = true;
	g_climbSince = g_climbSeenAt = (float)g_clock;
	g_climbStalled = 0.0f;
	g_climbFeet0 = g_climbFeetTop = pos[2];
	g_climbSpeed0 = g_speedAlong;
	g_climbPos0[0] = pos[0];
	g_climbPos0[1] = pos[1];
	g_stepsThisBoost = 0;   /* stage 2: this boost's steps and its one "no step" line */
	g_stepRefusedSaid = false;
	if (!LogHandTake(&g_climbHand))
		return;
	char at10[24], side[40] = "";
	if (L->d10 >= 0.0f)
		snprintf(at10, sizeof(at10), "%.0f", L->d10);
	else
		snprintf(at10, sizeof(at10), "nothing");
	if (L->side != 0.0f)
		snprintf(side, sizeof(side), " (the line %.0f to the %s)", fabsf(L->side), L->side > 0.0f ? "right" : "left");
	Log("climb: a low face at the capsule (%s, layer %u)%s: %.0f ahead at 4, %s at 10 (%.0f deg), nothing at %.1f within %.0f; the wheels' pitch %.1f, the ground normal %.1f, speed %.0f: the climb limit %.0f -> %.0f",
	    L->what4, L->layer4, side, L->d4, at10, L->angle, top, L->d4 + 45.0f, g_wheelPitch, NormalDegrees(nz), g_speedAlong, ToDegrees(g_writtenValue), ToDegrees(g_climbValue));
}

/* ClimbHold since a low face was last seen: off, over it (the feet up or the bike on), or not. */
static void ClimbLapse(const float pos[3], float sh, float ch)
{
	if (!g_climbOn || (float)g_clock - g_climbSeenAt <= g_climbHold)
		return;
	g_climbOn = false;
	float rose = g_climbFeetTop - g_climbFeet0, on = (pos[0] - g_climbPos0[0]) * sh + (pos[1] - g_climbPos0[1]) * ch;
	if (!LogHandTake(&g_climbHand))
		return;
	if (rose >= 2.0f || on >= 20.0f)
		Log("climb: over it after %.2f s (the feet %.0f up, speed %.0f -> %.0f, %.0f on along the heading%s): the climb limit back to %.0f",
		    (float)g_clock - g_climbSince, rose, g_climbSpeed0, g_speedAlong, on, g_stepsThisBoost == 1 ? ", after 1 step up" : g_stepsThisBoost > 1 ? ", after 2 steps up" : "",
		    ToDegrees(g_writtenValue));
	else
		Log("climb: off after %.2f s: no low face at the capsule for %g s, the bike %.0f on along the heading and the feet %.0f up (turned off it?): the climb limit back to %.0f",
		    (float)g_clock - g_climbSince, g_climbHold, on, rose, ToDegrees(g_writtenValue));
}

/* Stalled with forward held and no boost: why not, with every climb ray's word; once a stall,
 * again if the reason changes (a second apart at least), from the climb's hand. */
static void ClimbRefused(int why, const ClimbLine *line, int lines, int best, float top, float nz)
{
	if (why == g_climbRefusedWhy || (float)g_clock - g_climbRefusedAt < 1.0f || !LogHandTake(&g_climbHand))
		return;
	g_climbRefusedWhy = why;
	g_climbRefusedAt = (float)g_clock;
	char reason[200], rays[900] = "", part[300];
	ClimbWhy(why, best >= 0 ? &line[best] : NULL, top, reason, sizeof(reason));
	for (int i = 0; i < lines; i++) {
		const ClimbLine *L = &line[i];
		char d4[96], d10[80], dt[96];
		if (L->d4 >= 0.0f)
			snprintf(d4, sizeof(d4), "%.0f (%s, layer %u)", L->d4, L->what4, L->layer4);
		else
			snprintf(d4, sizeof(d4), "nothing");
		if (L->d10 >= 0.0f)
			snprintf(d10, sizeof(d10), "%.0f (%.0f deg)", L->d10, L->angle);
		else if (L->grazed)
			snprintf(d10, sizeof(d10), "nothing (ground under the hit at 4: %.0f deg at most)", L->angle);
		else
			snprintf(d10, sizeof(d10), L->d4 >= 0.0f ? "nothing (90 deg)" : "nothing");
		if (L->dTop >= 0.0f)
			snprintf(dt, sizeof(dt), ", at %.1f %.0f (%s, layer %u)", top, L->dTop, L->whatTop, L->layerTop);
		else
			dt[0] = 0;
		snprintf(part, sizeof(part), "%s%s: at 4 %s, at 10 %s%s", i ? "; " : "", i == 0 ? "the centre" : i == 1 ? "12 to the left" : "12 to the right", d4, d10, dt);
		size_t used = strlen(rays);
		if (used + strlen(part) + 1 < sizeof(rays))
			memcpy(rays + used, part, strlen(part) + 1);
	}
	Log("climb: stopped with forward held (speed %.0f, along %+.0f, the throttle held to %.2f), the ground normal %.1f, the wheels' pitch %.1f: not climbed: %s; the rays: %s",
	    g_speed, g_speedAlong, g_throttle, NormalDegrees(nz), g_wheelPitch, reason, rays);
}

static void ClimbRays(uintptr_t player, uintptr_t ctrl, bool onGround, float nz)
{
	if (!g_riding || !g_climb) {
		ClimbOff(NULL);   /* the ride's end is said by the tick */
		g_stallSince = -1.0f;
		g_stepCheck = false;
		return;
	}
	if (!g_climbRideLogged && ctrl) {
		g_climbRideLogged = true;
		LogCapsule(ctrl);
	}
	if (!player || !Accessible(player + OFF_REFR_HEADING, 4, false) || !Accessible(player + OFF_REFR_POS, 12, false))
		return;
	const float *pos = (const float *)(player + OFF_REFR_POS);
	float h = *(const float *)(player + OFF_REFR_HEADING), sh = sinf(h), ch = cosf(h), clock = (float)g_clock;
	if (!isfinite(h) || !isfinite(pos[0]) || !isfinite(pos[1]) || !isfinite(pos[2]))
		return;
	double now = SecondsNow();
	bool back = g_inputActive && now - g_backAt < 0.1, forward = g_inputActive && !back && now - g_forwardAt < 0.1;
	/* Stage 2: the last step's rise seen, and a new obstacle's two steps once the bike is 60
	 * from where the last was made. */
	ClimbStepSeen(pos);
	if (g_stepCount > 0 && hypotf(pos[0] - g_stepPos[0], pos[1] - g_stepPos[1]) >= 60.0f)
		g_stepCount = 0;
	/* A give-up's cooldown ends once the bike has moved 60 along its heading, or forward is let
	 * go (to be pressed again). */
	if (g_climbCool && (!forward || (pos[0] - g_climbCoolPos[0]) * sh + (pos[1] - g_climbCoolPos[1]) * ch >= 60.0f))
		g_climbCool = false;
	if (forward && g_throttleCapped && g_speedAlong < 80.0f) {
		if (g_stallSince < 0.0f || g_speedAlong > g_stallSpeed + 15.0f) {   /* a start from rest is held to the measured speed too as it comes up (test 23's cap) */
			g_stallSince = clock;
			g_stallSpeed = g_speedAlong;
		}
	} else {
		g_stallSince = -1.0f;
		g_climbRefusedWhy = -1;   /* the next stall gets its line */
	}
	bool stalled = g_stallSince >= 0.0f && clock - g_stallSince >= 0.2f;
	if (g_climbOn) {
		const char *cut = back ? "the back key" : g_inputMode == INPUT_CREEP ? "the creep" : !forward ? "forward let go" : NULL;
		if (cut)
			ClimbOff(cut);
	}
	uintptr_t cell = 0;
	if (!forward || !(g_throttleOn && g_throttle > 0.0f) || g_inputMode != INPUT_PASS || !onGround || !g_partsOk || !g_applied || !g_climbValueOk ||
	    !RaysReady(player) || !(cell = ReadPtr(player + OFF_REFR_CELL)) || !IsA(cell, RTTI_CELL)) {
		ClimbLapse(pos, sh, ch);
		return;
	}
	float p = g_pitchNow / 57.29578f, cp = cosf(p), sp = sinf(p);
	float fwd[3] = { sh * cp, ch * cp, sp }, up[3] = { -sh * sp, -ch * sp, cp }, right[3] = { ch, -sh, 0.0f };
	float v = g_speedAlong > 0.0f ? g_speedAlong : 0.0f, reach = g_capsuleRadius + 6.0f + 0.1f * v, len = reach + 20.0f;
	float top = ClimbTop(), limit = ToDegrees(g_writtenValue);
	bool word = g_wheelPitchOk || clock - g_wheelWordAt < 0.5f;
	ClimbLine line[3];
	int lines = stalled ? 3 : 1, best = -1;
	for (int i = 0; i < lines; i++) {
		ClimbLine *L = &line[i];
		memset(L, 0, sizeof(*L));
		L->side = i == 0 ? 0.0f : i == 1 ? -12.0f : 12.0f;
		L->d10 = L->dTop = -1.0f;
		L->what4 = L->whatTop = "unnamed";
		L->why = CLIMB_NONE;
		float o[3];
		for (int k = 0; k < 3; k++)
			o[k] = pos[k] + right[k] * L->side;
		ClimbCast(cell, o, up, fwd, 4.0f, len, &L->d4, &L->what4, &L->layer4);
		if (L->d4 < 0.0f)
			continue;
		ClimbCast(cell, o, up, fwd, 10.0f, len, &L->d10, NULL, NULL);
		L->angle = L->d10 < 0.0f ? 90.0f : g_pitchNow + atan2f(6.0f, L->d10 - L->d4) * 57.29578f;
		if (L->d10 < 0.0f && L->d4 > 2.0f) {
			/* Nothing at 10: a thing lower than that, or the ray at 4 grazing ground that rises
			 * toward it (the bike still pitched down onto the flat after a descent: its hit 38
			 * ahead, the one at 10 past its reach, in the harness's check). A short ray down from
			 * 2 short of the hit tells them apart: ground under it within 2 is what the ray
			 * grazed, and the face is no steeper than the miss allows. */
			float a[3], b[3];
			for (int k = 0; k < 3; k++)
				a[k] = b[k] = o[k] + up[k] * 4.0f + fwd[k] * (L->d4 - 2.0f);
			a[2] += 0.5f;
			b[2] -= 2.0f;
			float f = CastRay(cell, a, b);
			if (f > 0.0f && f < 1.0f) {
				L->angle = g_pitchNow + atan2f(6.0f, len - L->d4) * 57.29578f;
				L->grazed = true;
			}
		}
		if (L->angle < limit - 5.0f || L->d4 > reach)
			continue;   /* a slope the limit climbs (flat ground after a descent among them), or not at the capsule yet */
		if (L->layer4 == LAYER_CHAR_CONTROLLER || L->layer4 == LAYER_BIPED) {
			L->why = CLIMB_ACTOR;
			continue;
		}
		ClimbCast(cell, o, up, fwd, top, L->d4 + 45.0f, &L->dTop, &L->whatTop, &L->layerTop);
		L->why = L->dTop >= 0.0f ? CLIMB_TALL : g_faceKind == 2 ? CLIMB_WALL : clock - g_wallAheadAt < 0.25f ? CLIMB_CUT
		       : !word ? CLIMB_NOWORD : g_wheelPitch > g_climbMaxPitch ? CLIMB_PITCH : g_climbCool ? CLIMB_COOL : CLIMB_OK;
	}
	for (int i = 0; i < lines; i++) {   /* the nearest that qualifies, else the nearest face at the capsule */
		if (line[i].why == CLIMB_NONE)
			continue;
		bool ok = line[i].why == CLIMB_OK, bestOk = best >= 0 && line[best].why == CLIMB_OK;
		if (best < 0 || (ok && !bestOk) || (ok == bestOk && line[i].d4 < line[best].d4))
			best = i;
	}
	int why = best >= 0 ? line[best].why : CLIMB_NONE;
	if (why == CLIMB_OK) {
		g_climbSeenAt = clock;
		if (!g_climbOn)
			ClimbOn(&line[best], pos, nz, top);
	} else if (g_climbOn && (why == CLIMB_TALL || why == CLIMB_WALL || why == CLIMB_CUT)) {
		char text[200];
		ClimbWhy(why, &line[best], top, text, sizeof(text));
		ClimbOff(text);
	}
	if (g_climbOn) {
		if (pos[2] > g_climbFeetTop)
			g_climbFeetTop = pos[2];
		g_climbStalled = g_speedAlong < 40.0f ? g_climbStalled + g_frameDt : 0.0f;
		/* Stage 2: still under 40 along 0.25 s into the boost, at a face that qualified this
		 * frame: a step up onto its top, if it has one the capsule fits over (ClimbStepUp). */
		if (g_climbStep && why == CLIMB_OK && clock - g_climbSince >= 0.25f && g_speedAlong < 40.0f && g_stepCount < 2 && !g_stepCheck &&
		    clock - g_stepAt >= 0.25f && clock - g_stepTriedAt >= 0.25f && ctrl) {
			g_stepTriedAt = clock;
			ClimbStepUp(player, ctrl, cell, &line[best], pos, sh, ch, top);
		}
		if (g_climbStalled >= g_climbMax) {
			g_climbOn = false;
			g_climbCool = true;
			g_climbCoolAt = clock;
			g_climbCoolPos[0] = pos[0];
			g_climbCoolPos[1] = pos[1];
			if (LogHandTake(&g_climbHand))
				Log("climb: given up after %.1f s stalled (normal %.1f%s): not again till the bike has moved 60 along its heading or forward is pressed again", g_climbStalled, NormalDegrees(nz),
				    g_stepsThisBoost == 1 ? ", 1 step up made" : g_stepsThisBoost > 1 ? ", 2 steps up made" : "");
		}
	}
	ClimbLapse(pos, sh, ch);
	if (stalled && !g_climbOn && why != CLIMB_OK)
		ClimbRefused(why, line, lines, best, top, nz);
}

static bool g_trackOnGround;   /* last frame's ground state, for the jump's re-solve below */

static void SampleGround(void)
{
	g_trackPitchOk = g_trackSteepOk = false;
	uintptr_t player = Player();
	g_riderRoot = Root3D(player);   /* before any ray this frame: a hit on it is the rider's own (test 36) */
	uintptr_t ctrl = player ? FindController(player, false) : 0;
	float n[3];
	bool air = false;
	g_groundOk = ReadGround(ctrl, n, &air);
	/* Backing up in steps, the controller may say it's in the air with the feet on the ground
	 * (test 18: 16 s on a 10 deg slope, its support normal frozen): then the rays' word goes,
	 * so the track and the pitch carry on. */
	if (g_rayGrounded && (air || !g_groundOk)) {
		air = false;
		g_groundOk = true;
		memcpy(n, g_rayNormal, sizeof(n));
	}
	/* In the air only after 50 ms of it (test 29: the state flapped air/ground every frame for
	 * a third of a second, and the tilt's samples went with it). */
	if (air)
		g_airFor += g_frameDt;
	else
		g_airFor = 0.0f;
	air = air && g_airFor >= 0.05f;
	g_groundAir = air;
	bool onGround = g_groundOk && !air;
	if (g_riding)
		RamFrame();   /* the script's answers and the hits still to tell, before this frame's rays act on them (rams) */
	WheelRays(player, onGround);
	FaceRays(player, onGround);
	ClimbRays(player, ctrl, onGround, onGround ? n[2] : g_groundN[2]);   /* the climb's boost decided before ApplySlope writes the limit, later this frame */
	if (onGround) {
		memcpy(g_groundN, n, sizeof(n));
		float k = g_avgAge > 0.0f ? 1.0f - expf(-g_frameDt / GROUND_AVERAGE_TIME) : 1.0f;
		float len = 0.0f;
		for (int i = 0; i < 3; i++) {
			g_avgN[i] += (n[i] - g_avgN[i]) * k;
			len += g_avgN[i] * g_avgN[i];
		}
		len = sqrtf(len);
		for (int i = 0; i < 3; i++)
			g_avgN[i] = len > 0.5f ? g_avgN[i] / len : n[i];
		g_avgAge = g_avgAge + g_frameDt < 10.0f ? g_avgAge + g_frameDt : 10.0f;
	}

	if (!g_riding || !player || !Accessible(player + OFF_REFR_POS, 12, false))
		return;
	if (!onGround) {
		g_airTime += g_frameDt;
		g_trackOnGround = false;
		if (g_airTime > TRACK_MAX_AIR) {
			TrackClear();
			g_avgAge = 0.0f;   /* a drop: the ground before it says nothing about after */
		}
		return;
	}
	g_airTime = 0.0f;
	bool groundLast = g_trackOnGround;
	g_trackOnGround = true;
	const float *pos = (const float *)(player + OFF_REFR_POS);
	if (!isfinite(pos[0]) || !isfinite(pos[1]) || !isfinite(pos[2]))
		return;
	if (g_trackCount) {
		const TrackPoint *last = TrackAt(0);
		float dx = pos[0] - last->p[0], dy = pos[1] - last->p[1];
		float jump = Distance(pos, last->p);
		if (jump > 150.0f) {
			TrackClear();   /* a door, fast travel, a teleport */
			/* The lean solved again after a real jump only: over 300 (the steering's own door and
			 * fast-travel threshold) and from a ground frame (a hop at speed lands over 150 from
			 * its last point, and a cell load's stall can carry a frame that far; review of test
			 * 38's build: both would have logged a fast travel and started the lean's wait over).
			 * Test 38: a fast travel on the bike leaves the rider's shapes held and sends no
			 * PostLoadGame, so the lean is solved again here. */
			if (jump > 300.0f && groundLast) {
				char why[96];
				snprintf(why, sizeof(why), "a jump of %.0f units (a door, a fast travel)", jump);
				RearmTorsoSolve(why);
			}
		} else if (dx * dx + dy * dy < TRACK_SPACING * TRACK_SPACING) {
			TrackPitch(player, pos);   /* standing still (or nearly): the same track, the same slope */
			return;
		}
	}
	TrackPoint *t = &g_track[g_trackHead];
	memcpy(t->p, pos, sizeof(t->p));
	memcpy(t->n, n, sizeof(t->n));
	g_trackAddedAt = g_clock;
	g_trackHead = (g_trackHead + 1) % TRACK_POINTS;
	if (g_trackCount < TRACK_POINTS)
		g_trackCount++;
	TrackPitch(player, pos);
}

/* A point on the track `along` units back along the ground from the player's feet `p`
 * (the track runs p, newest point, ..., oldest point). False past its end. */
static bool TrackPointAt(const float p[3], float along, float out[3])
{
	float travelled = 0.0f, prev[3] = { p[0], p[1], p[2] };
	for (int i = 0; i < g_trackCount; i++) {
		const TrackPoint *t = TrackAt(i);
		float seg = Distance(prev, t->p);
		if (seg > 0.0f && travelled + seg >= along) {
			float f = (along - travelled) / seg;
			for (int k = 0; k < 3; k++)
				out[k] = prev[k] + (t->p[k] - prev[k]) * f;
			return true;
		}
		travelled += seg;
		memcpy(prev, t->p, sizeof(prev));
	}
	return false;
}

/* Where the parked bike goes: on the track, its middle at the first place (walking back
 * along it) that's PARK_DISTANCE from the player's feet in a straight line, so it never
 * lands on them, even after a U-turn. Its heading and pitch come from the track's
 * direction there (PARK_SPAN either side), its height from the track, its roll from the
 * ground's normals there. out: x, y, z, the bike's angle (degrees, the game's heading
 * + 180: the model faces -Y), and its up. False if the track is too short, or the player
 * isn't at its end (in the air). */
static bool ParkSpot(uintptr_t player, float out[7], const char **why)
{
	*why = "no track yet (rode less than a bike length on the ground)";
	if (g_trackCount < 2 || !player || !Accessible(player + OFF_REFR_POS, 12, false))
		return false;
	const float *p = (const float *)(player + OFF_REFR_POS);
	if (Distance(p, TrackAt(0)->p) > 40.0f) {
		*why = "the player isn't on the track's end (in the air?)";
		return false;
	}
	float travelled = 0.0f, prev[3] = { p[0], p[1], p[2] }, c[3] = { 0 }, at = -1.0f;
	for (int i = 0; i < g_trackCount && at < 0.0f; i++) {
		const TrackPoint *t = TrackAt(i);
		float seg = Distance(prev, t->p), before = Distance(prev, p), after = Distance(t->p, p);
		if (seg > 0.0f && after >= PARK_DISTANCE && before < PARK_DISTANCE) {
			float f = (PARK_DISTANCE - before) / (after - before);   /* segments are short: linear is close */
			for (int k = 0; k < 3; k++)
				c[k] = prev[k] + (t->p[k] - prev[k]) * f;
			at = travelled + seg * f;
		}
		travelled += seg;
		memcpy(prev, t->p, sizeof(prev));
	}
	if (at < 0.0f) {
		*why = travelled < PARK_DISTANCE ? "the track is shorter than a bike length and a half"
		                                 : "the track never gets a bike length and a half from the player";
		return false;
	}
	/* From there on back along the track, the first spot no steeper than PARK_MAX_SLOPE
	 * (test 9: got off on a 60 deg rock face; the bike belongs where it could stand). */
	float total = 0.0f, a[3], up[3];
	bool crossed = false;
	memcpy(prev, p, sizeof(prev));
	for (int i = 0; i < g_trackCount; i++) {
		total += Distance(prev, TrackAt(i)->p);
		memcpy(prev, TrackAt(i)->p, sizeof(prev));
	}
	for (;; at += PARK_STEP) {
		if (at > total || at > PARK_DISTANCE + PARK_SEARCH) {
			*why = crossed ? "the track is steeper than 45 deg, or crosses a slope steeper than 20 deg, all the way back"
			               : "the track is steeper than 45 deg all the way back";
			return false;
		}
		if (!TrackPointAt(p, at, c) || Distance(c, p) < PARK_DISTANCE - 2.0f)
			continue;
		float ahead[3], behind[3];
		if (!TrackPointAt(p, at - PARK_SPAN, ahead))
			memcpy(ahead, c, sizeof(ahead));
		if (!TrackPointAt(p, at + PARK_SPAN, behind))
			memcpy(behind, TrackAt(g_trackCount - 1)->p, sizeof(behind));   /* the track's oldest point */
		for (int k = 0; k < 3; k++)
			a[k] = ahead[k] - behind[k];
		float len = sqrtf(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]);
		if (len < 20.0f || sqrtf(a[0] * a[0] + a[1] * a[1]) < 10.0f)
			continue;   /* no direction there */
		for (int k = 0; k < 3; k++)
			a[k] /= len;
		/* Both halves walkable, not just on average: at the foot of a rock face the span
		 * would average out half flat, half face. */
		float limit = sinf(PARK_MAX_SLOPE / 57.29578f), d1 = Distance(ahead, c), d2 = Distance(c, behind);
		if (fabsf(a[2]) > limit || (d1 > 1.0f && fabsf(ahead[2] - c[2]) / d1 > limit) ||
		    (d2 > 1.0f && fabsf(c[2] - behind[2]) / d2 > limit))
			continue;   /* too steep to stand a bike on */
		/* The ground's normals there, averaged. */
		float nsum[3] = { 0 };
		float along = 0.0f, prevp[3] = { p[0], p[1], p[2] };
		for (int i = 0; i < g_trackCount; i++) {
			const TrackPoint *t = TrackAt(i);
			along += Distance(prevp, t->p);
			memcpy(prevp, t->p, sizeof(prevp));
			if (along > at + PARK_SPAN)
				break;
			if (along >= at - PARK_SPAN)
				for (int k = 0; k < 3; k++)
					nsum[k] += t->n[k];
		}
		float nlen = sqrtf(nsum[0] * nsum[0] + nsum[1] * nsum[1] + nsum[2] * nsum[2]), dot = 0.0f;
		for (int k = 0; k < 3; k++) {
			up[k] = nlen > 0.0f ? nsum[k] / nlen : (k == 2 ? 1.0f : 0.0f);
			dot += up[k] * a[k];
		}
		/* Up at right angles to the bike's length: the track's direction sets the pitch. */
		float ulen = 0.0f;
		for (int k = 0; k < 3; k++) {
			up[k] -= dot * a[k];
			ulen += up[k] * up[k];
		}
		ulen = sqrtf(ulen);
		if (!(ulen > 0.1f) || up[2] / ulen < 0.5f)
			continue;
		for (int k = 0; k < 3; k++)
			up[k] /= ulen;
		/* Across the bike, the ground may lean only a little: the parked bike rolls at most
		 * 10 deg, so on a steep side slope one side hangs in the air (test 10). */
		float side = sqrtf(a[0] * a[0] + a[1] * a[1]);
		if (fabsf((up[0] * a[1] - up[1] * a[0]) / side) > sinf(PARK_MAX_CROSS / 57.29578f)) {
			crossed = true;
			continue;
		}
		break;
	}
	float heading = atan2f(a[0], a[1]) * 57.29578f;   /* the game's: 0 = +Y, clockwise */
	out[0] = c[0];
	out[1] = c[1];
	out[2] = c[2];
	out[3] = fmodf(heading + 180.0f + 360.0f, 360.0f);
	for (int k = 0; k < 3; k++)
		out[4 + k] = up[k];
	return true;
}

/* Every IntervalMs: the averaged ground normal (Z 0 off the ground) and, while riding,
 * the parking spot on the track (UpZ 0 when there's none). */
static void PublishGround(uintptr_t player)
{
	if (g_groundGlobals[0]) {
		if (g_groundOk && !g_groundAir && g_avgAge >= 0.25f)
			for (int i = 0; i < 3; i++)
				SetGlobal(g_groundGlobals[i], g_avgN[i]);
		else
			SetGlobal(g_groundGlobals[2], 0.0f);
	}
	if (!g_parkGlobals[0] || !g_riding)
		return;
	g_parkValid = ParkSpot(player, g_parkSpot, &g_parkWhy);
	if (g_parkValid) {
		for (int i = 0; i < 7; i++)
			SetGlobal(g_parkGlobals[i], g_parkSpot[i]);
		memcpy(g_parkPublished, g_parkSpot, sizeof(g_parkPublished));
		g_parkPublishedAt = g_clock;
	} else {
		SetGlobal(g_parkGlobals[6], 0.0f);
	}
}

/* On getting off: what the controller script had to park on, the last spot written (the
 * script reads it a moment before the ride ends; test 9 logged a later recalculation). */
static void LogParkSpot(void)
{
	if (!g_parkGlobals[0])
		return;
	float age = g_clock - g_parkPublishedAt;
	if (age < 2.0f) {
		Log("park: on getting off, the spot last written (%.1f s before): (%.0f, %.0f, %.0f), angle %.0f, up (%.2f, %.2f, %.2f)",
		    age, g_parkPublished[0], g_parkPublished[1], g_parkPublished[2], g_parkPublished[3],
		    g_parkPublished[4], g_parkPublished[5], g_parkPublished[6]);
		if (!g_parkValid)
			Log("park:   (by the time the ride ended it was gone: %s)", g_parkWhy);
	} else {
		Log("park: on getting off, no spot on the track: %s", g_parkWhy);
	}
}


/* The third-person camera state (ThirdPersonState): the current one if it is one,
 * otherwise whichever of the two third-person slots is. */
static uintptr_t ThirdPersonState(void)
{
	uintptr_t camera = ReadPtr(g_base + RVA_PLAYER_CAMERA);
	if (!camera || !IsA(camera, RTTI_CAMERA))
		return 0;
	uintptr_t state = ReadPtr(camera + OFF_CAMERA_STATE);
	if (state && IsA(state, RTTI_THIRD))
		return state;
	for (int i = CAMERA_THIRD_PERSON1 + 1; i >= CAMERA_THIRD_PERSON1; i--) {
		state = ReadPtr(camera + OFF_CAMERA_STATES + 8u * (unsigned)i);
		if (state && IsA(state, RTTI_THIRD))
			return state;
	}
	return 0;
}

static bool Fraction(float v)
{
	return v >= 0.0f && v <= 1.0001f;
}

/* Riding: the third-person zoom all the way out (a fraction of the way from the nearest to
 * the farthest, fVanityModeMaxDist, as in Skyrim; the offsets are CommonLibF4's, so the
 * values are only written if both read as fractions, and logged either way). For two
 * seconds after getting on it's set again, in case going into third person (under the
 * fade) puts the saved zoom back; after that the mouse wheel is the player's. Getting off:
 * the zoom from before. */
static void UpdateZoom(DWORD now, bool riding)
{
	if (!g_zoomOut || !g_zoomTargetOffset || !g_zoomCurrentOffset)
		return;
	if (riding && !g_zoomRiding) {
		g_zoomRiding = true;
		g_zoomTouched = false;
		g_zoomState = ThirdPersonState();
		if (!g_zoomState || !Accessible(g_zoomState + g_zoomTargetOffset, 4, true) ||
		    !Accessible(g_zoomState + g_zoomCurrentOffset, 4, true)) {
			Log("camera zoom: no third-person camera state found: leaving the zoom alone");
			return;
		}
		float *target = (float *)(g_zoomState + g_zoomTargetOffset), *current = (float *)(g_zoomState + g_zoomCurrentOffset);
		if (!g_zoomDumped) {
			g_zoomDumped = true;
			char line[400];
			int len = 0;
			for (unsigned off = 0xD0; off < 0x110 && len < (int)sizeof(line) - 24; off += 4)
				if (Accessible(g_zoomState + off, 4, false))
					len += snprintf(line + len, sizeof(line) - len, " +%X=%g", off, *(const float *)(g_zoomState + off));
			Log("camera zoom: %s at %p, floats:%s", ObjectTypeName(g_zoomState), (void *)g_zoomState, line);
		}
		if (!Fraction(*target) || !Fraction(*current)) {
			Log("camera zoom: target %g, current %g at +0x%X/+0x%X aren't fractions: leaving the zoom alone",
			    *target, *current, g_zoomTargetOffset, g_zoomCurrentOffset);
			return;
		}
		g_zoomOldTarget = *target;
		g_zoomOldCurrent = *current;
		g_zoomTouched = true;
		g_zoomUntil = now + 2000;
		Log("camera zoom: getting on, target %g current %g -> all the way out (1)", *target, *current);
	}
	if (riding && g_zoomTouched && (int32_t)(now - g_zoomUntil) < 0 && g_zoomState == ThirdPersonState()) {
		*(float *)(g_zoomState + g_zoomTargetOffset) = 1.0f;
		*(float *)(g_zoomState + g_zoomCurrentOffset) = 1.0f;
	}
	if (!riding && g_zoomRiding) {
		g_zoomRiding = false;
		if (g_zoomTouched && g_zoomState == ThirdPersonState()) {
			float *target = (float *)(g_zoomState + g_zoomTargetOffset), *current = (float *)(g_zoomState + g_zoomCurrentOffset);
			Log("camera zoom: getting off, target %g current %g -> back to %g", *target, *current, g_zoomOldTarget);
			*target = g_zoomOldTarget;
			*current = g_zoomOldCurrent;
		}
		g_zoomTouched = false;
	}
}

/* ------------------------------------------------------------------------- */
/* Input: the move keys, changed before the game moves the player            */
/* ------------------------------------------------------------------------- */

/* Holstered, in third person, the game turns the player to face where the move keys point
 * and moves them forward along it: back means "turn round and ride towards the camera", and
 * a side key alone from a standstill "ride off that way" (test 12: up to full speed, while
 * the steering clamp turned the bike at 60 deg/s; held to its heading, back drove it
 * forward). The move input is PlayerControls::data.moveInputVec (+0x44, test 11), set by
 * its MovementHandler from the key and stick events and read by the movement update later
 * in the frame, before F4SE's task runs (test 12: written from the task, the game had
 * already used -1). So the plugin wraps the MovementHandler's event functions (three
 * entries of its vtable swapped, no code patched; a struct in the game, .?AUMovementHandler@@,
 * test 13; its vtable where 1.11.240 has it) and changes the input right after the game
 * sets it:
 *   - back (y < -0.2): (0, 0), so the game doesn't drive off; the plugin pushes the bike
 *     back itself (below) and turns it;
 *   - a side key alone (|y| <= 0.2) below CreepBelow: (0, creep), a crawl forward round a
 *     CreepRadius circle while the plugin turns the heading at the stopped rate;
 *   - anything with forward in it: left alone (the speed-dependent clamp, test 12: fine).
 * Before each call the game gets back what it last left there itself, so this works whether
 * the game sets the input or adds to it. */
/* The wrappers pass on all four register arguments, whatever the original takes (F4SE and
 * CommonLibF4 agree on one event pointer, none, and (id, output)). */
typedef void (*Forward4)(uintptr_t, uintptr_t, uintptr_t, uintptr_t);
static void *g_origThumbstick, *g_origButton, *g_origPerFrame, *g_origOutput;
static uintptr_t g_moveHandler;     /* the MovementHandler we wrap */
static float *g_moveVec;            /* PlayerControls::data.moveInputVec */
static bool g_inputHooked, g_inputHookTried;
static bool g_inputActive;          /* riding, steering on: the filter is on */
static float g_rawMove[2];          /* what the game wants (as it last left the input itself) */
static float g_wroteMove[2];        /* what we left there instead */
static bool g_wrote;
static float g_keys[2];             /* the keys as taken (the raw ones, or the last ones kept) */
static float g_lastKeys[2], g_keysSeenAt = -100.0f;   /* the last keys that weren't (0, 0), and when */
static bool g_keysStuck;            /* this reading was (0, 0) and the last keys were taken instead */
static int g_modeChanges;           /* INPUT_* changes since the last trace line */
static float g_creepWant;           /* the creep speed wanted (units a second) */
static float g_inputLogged;
static float g_output[16];          /* the movement update's last PlayerControlsMovementData */
static int g_outputCalls;
static bool g_outputHooked;

/* What we write is told apart from the game's own by its bits: a zero is written as -0.0
 * (test 14: the game clears the input to +0.0 every frame outside these functions, then each
 * held key sets its own half; a (0, 0) of ours looked like that clear's, so a side key let go
 * of while backing was put back every frame and stuck, into the creep afterwards too). */
static bool StillOurs(void)
{
	return g_wrote && g_moveVec && memcmp(g_moveVec, g_wroteMove, sizeof(g_wroteMove)) == 0;
}

static void BeforeInput(void)
{
	/* Give the game back its own value, unless something else changed it since. */
	if (StillOurs()) {
		g_moveVec[0] = g_rawMove[0];
		g_moveVec[1] = g_rawMove[1];
	}
	g_wrote = false;
}

/* The game's speed for an input of a size, as a fraction of the top (test 22's log, SpeedMult
 * 2.5: 0.10 gave 90 of 930 units a second, 0.33 158, 0.66 464, 0.85 720), and its inverse:
 * the input that gives a speed. The curve bends upward, so ramping the input piled the speed
 * up at the end; the throttle ramps the speed and writes this. */
static const float kCurveIn[] = { 0.00f, 0.10f, 0.16f, 0.33f, 0.51f, 0.66f, 0.85f, 0.95f, 1.00f };
static const float kCurveOut[] = { 0.00f, 0.097f, 0.116f, 0.170f, 0.302f, 0.499f, 0.774f, 0.912f, 1.00f };

static float InputForSpeed(float speed)
{
	if (!(speed > 0.0f))
		return 0.0f;
	for (int i = 1; i < (int)(sizeof(kCurveOut) / sizeof(kCurveOut[0])); i++)
		if (speed <= kCurveOut[i])
			return kCurveIn[i - 1] + (speed - kCurveOut[i - 1]) / (kCurveOut[i] - kCurveOut[i - 1]) * (kCurveIn[i] - kCurveIn[i - 1]);
	return 1.0f;
}

static double SecondsNow(void)
{
	LARGE_INTEGER now;
	QueryPerformanceCounter(&now);
	return g_qpcFrequency.QuadPart ? (double)now.QuadPart / (double)g_qpcFrequency.QuadPart : 0.0;
}

static void AfterInput(void)
{
	float x = g_moveVec[0], y = g_moveVec[1];
	g_rawMove[0] = x;   /* the game's own, to give back to it (never the keys kept below) */
	g_rawMove[1] = y;
	/* A (0, 0) within 0.2 s of real keys is taken as those keys still held: the game clears
	 * the input on its own, and on some frames that clear comes after the held key's event
	 * and before a later call here, which then read (0, 0), dropped the mode and undid the
	 * creep's wind-up every other frame (test 19: 3.5 s turning with no creep). A key let go
	 * of lasts 0.2 s longer; a different key takes over at once. */
	g_keysStuck = false;
	if (g_inputActive && x == 0.0f && y == 0.0f && g_clock - g_keysSeenAt < 0.2f) {
		x = g_lastKeys[0];
		y = g_lastKeys[1];
		g_keysStuck = true;
	} else if (isfinite(x) && isfinite(y) && (x != 0.0f || y != 0.0f)) {
		g_lastKeys[0] = x;
		g_lastKeys[1] = y;
		g_keysSeenAt = g_clock;
	}
	g_keys[0] = x;
	g_keys[1] = y;
	g_throttleWrote = false;
	bool keysOk = g_inputActive && isfinite(x) && isfinite(y);
	bool forward = keysOk && y > 0.2f, back = keysOk && y < -0.2f;
	/* The throttle: the speed, as a fraction of the top, builds up over Accel seconds on the
	 * forward key (from a tenth: test 22 liked the start), rolls off over Coast seconds after
	 * it, and back brakes it off over Brake seconds; only once it's off does back reverse and
	 * a side key creep. On its own clock: these hooks run with the input, not once a frame
	 * (test 22: a third of the frames, so Accel came out three times longer). Off (Throttle=0),
	 * the keys go through as they are. */
	double now = SecondsNow();
	float dt = (float)(now - g_throttleAt);
	g_throttleAt = now;
	dt = !(dt > 0.0f) ? 0.0f : dt < 0.1f ? dt : 0.1f;   /* a long gap (a pause, a load, a hitch) counts for a tenth of a second at most */
	/* The game hands the keys over an axis at a time (a side key's event, then forward's), so a
	 * read of (1, 0) between two of (1, 1) isn't the forward key let go of: a key read within
	 * the last 100 ms is still held (the harness's forward-and-right sat at a tenth: the side
	 * key's read coasted off what the forward key's read had built). */
	if (keysOk && y > 0.2f)
		g_forwardAt = now;
	if (keysOk && y < -0.2f)
		g_backAt = now;
	back = keysOk && now - g_backAt < 0.1;
	forward = keysOk && !back && now - g_forwardAt < 0.1;
	if (keysOk && g_throttleOn) {
		if (forward) {
			if (g_throttle < 0.1f)
				g_throttle = 0.1f;
			g_throttle += dt / (g_accel > 0.05f ? g_accel : 0.05f);
			if (y > 0.2f)
				g_throttleMag = y;
		} else if (back) {
			g_throttle -= dt / (g_brake > 0.05f ? g_brake : 0.05f);
		} else {
			g_throttle -= dt / (g_coast > 0.05f ? g_coast : 0.05f);
		}
		g_throttle = g_throttle > 1.0f ? 1.0f : g_throttle < 0.0f ? 0.0f : g_throttle;
		/* Never far ahead of the bike (test 23: from a stop the game's speed lagged the throttle
		 * for a second and then surged to catch up; stuck on a hillside with W held, the throttle
		 * sat at 0.8 and would have lunged once free): at most Lead above the measured speed. */
		g_throttleCapped = false;
		if (g_lead > 0.0f && g_lead < 1.0f && g_fullSpeed > 0.0f && g_throttle > 0.1f) {
			/* The cap's floor is ClimbThrottle while the climb's boost is on (test 40: stuck at a
			 * trunk the cap held it to 0.20, an input of 0.37, about 180 u/s; how fast the capsule
			 * climbs goes with its push), 0.1 otherwise. */
			float measured = (g_speedAlong > 0.0f ? g_speedAlong : 0.0f) / g_fullSpeed, cap = measured + g_lead, least = g_climbOn ? g_climbThrottle : 0.1f;
			if (cap < least)
				cap = least;
			if (g_throttle > cap) {
				g_throttle = cap;
				g_throttleCapped = true;
			}
		}
		/* A knock-over (rams; test 41: "the bike should lose speed on a hit"): held to HitKeep of
		 * the speed at the hit for HitHold seconds (RamSlow), then built up again from there. */
		if (g_clock < g_ramSlowUntil && g_throttle > g_ramSlowTo)
			g_throttle = g_ramSlowTo;
	} else if (!keysOk || !g_throttleOn) {
		g_throttle = 0.0f;
	}
	bool rolling = g_throttleOn && g_throttle > 0.0f;
	/* Back reverses only once the bike has stopped (test 23: the reverse push started while
	 * the bike still rolled on at 500 and left a roll back after the stop); braked off and
	 * still rolling, the game gets nothing until then. */
	bool stopped = !g_throttleOn || g_speedAlong < g_backBelow;
	int mode = INPUT_PASS;
	if (keysOk) {
		if (back && !rolling && stopped)
			mode = g_reverse ? INPUT_BACK : INPUT_PASS;
		else if (!back && !forward && !rolling && y <= 0.2f && fabsf(x) > 0.05f && (g_inputMode == INPUT_CREEP || g_speed < g_creepBelow))
			mode = INPUT_CREEP;
	}
	if (mode != g_inputMode)
		g_modeChanges++;
	g_inputMode = mode;
	if (mode == INPUT_PASS) {
		if (rolling) {
			/* The input that gives the throttle's speed, the whole vector scaled to it (the
			 * game takes the speed from the vector's length: test 22's side key with forward
			 * made it a unit long and the speed full at once); its direction is the keys'
			 * (straight on with none, so the game turns on a side key while rolling). */
			float size = InputForSpeed(g_throttle) * (forward ? g_throttleMag : 1.0f);
			if ((float)g_clock - g_wallAheadAt < 0.25f)
				size = 0.0f;   /* a face ahead of the front wheel (WallAhead; not while an obstacle is being ridden over): no forward drive into it */
			size *= g_faceEase;   /* eased off towards a face seen ahead, or held to the obstacle's share (FaceRays) */
			float dx = x, dy = forward && y > 0.2f ? y : 1.0f;   /* a side key's own read: forward is still held */
			float len = sqrtf(dx * dx + dy * dy);
			if (!(len > 0.0f)) {
				dx = 0.0f;
				dy = len = 1.0f;
			}
			g_wroteMove[0] = dx == 0.0f ? copysignf(0.0f, -1.0f) : dx / len * size;
			g_wroteMove[1] = dy / len * size;
			memcpy(g_moveVec, g_wroteMove, sizeof(g_wroteMove));
			g_wrote = true;
			g_throttleWrote = true;
		} else if (back && !stopped && g_reverse) {
			g_wroteMove[0] = g_wroteMove[1] = copysignf(0.0f, -1.0f);   /* braked off, still rolling: nothing until it has stopped */
			memcpy(g_moveVec, g_wroteMove, sizeof(g_wroteMove));
			g_wrote = true;
			g_throttleWrote = true;
		}
		return;
	}
	g_throttle = 0.0f;
	g_wroteMove[0] = copysignf(0.0f, -1.0f);
	g_wroteMove[1] = mode == INPUT_CREEP && g_creep ? g_creepInput : copysignf(0.0f, -1.0f);
	memcpy(g_moveVec, g_wroteMove, sizeof(g_wroteMove));
	g_wrote = true;
}

static void HookThumbstick(uintptr_t self, uintptr_t a, uintptr_t b, uintptr_t c)
{
	bool ours = self == g_moveHandler;
	if (ours)
		BeforeInput();
	((Forward4)g_origThumbstick)(self, a, b, c);
	if (ours)
		AfterInput();
}

static void HookButton(uintptr_t self, uintptr_t a, uintptr_t b, uintptr_t c)
{
	bool ours = self == g_moveHandler;
	if (ours)
		BeforeInput();
	((Forward4)g_origButton)(self, a, b, c);
	if (ours)
		AfterInput();
}

static void HookPerFrame(uintptr_t self, uintptr_t a, uintptr_t b, uintptr_t c)
{
	bool ours = self == g_moveHandler;
	if (ours)
		BeforeInput();
	((Forward4)g_origPerFrame)(self, a, b, c);
	if (ours)
		AfterInput();
}

/* Readable memory, asked of Windows each time (the movement update may run on another
 * thread than the task, which owns the region cache). */
static __thread struct { uintptr_t start, end; DWORD at; } t_readable[4];
static __thread int t_readableNext;

static bool ReadableNow(uintptr_t p, size_t n)
{
	if (p < 0x10000)
		return false;
	DWORD now = GetTickCount();   /* a few regions remembered for 30 s, on this thread (test 26: the query is dear) */
	for (int i = 0; i < 4; i++)
		if (t_readable[i].end && p >= t_readable[i].start && p + n <= t_readable[i].end && now - t_readable[i].at < 30000)
			return true;
	MEMORY_BASIC_INFORMATION mbi;
	g_queries++;
	if (VirtualQuery((const void *)p, &mbi, sizeof(mbi)) != sizeof(mbi) || mbi.State != MEM_COMMIT ||
	    (mbi.Protect & (PAGE_GUARD | PAGE_NOACCESS)) || !(mbi.Protect & (PAGE_READONLY | PAGE_READWRITE | PAGE_WRITECOPY |
	    PAGE_EXECUTE_READ | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY)))
		return false;
	int slot = t_readableNext++ % 4;
	t_readable[slot].start = (uintptr_t)mbi.BaseAddress;
	t_readable[slot].end = (uintptr_t)mbi.BaseAddress + mbi.RegionSize;
	t_readable[slot].at = now;
	return p + n <= (uintptr_t)mbi.BaseAddress + mbi.RegionSize;
}

/* What the movement update gets from the player controls, PlayerControlsMovementData
 * (CommonLibF4): movementRotation +0x00 (always 0 in test 14: along the facing), rotationSpeed
 * +0x10 (z: turning, up to +-4), movementSpeed +0x20 (2 riding, 0.06-0.3 creeping, 0 with no
 * input) and targetAngle +0x30 (z: the heading wanted, radians). While backing up the plugin
 * holds the heading here (target angle = its own, no turning, no speed: it steers and moves
 * the bike itself). Test 15: the movement turned round (rotation z = pi) or a negative speed
 * didn't move the player at all: it only ever moves forward along the facing. With Trace=1
 * the result is logged. */
static float g_outputGame[16];      /* the game's own, before ours */
static void HookOutput(uintptr_t self, uintptr_t id, uintptr_t out, uintptr_t d)
{
	/* Right before the game works the input into its movement: ours again, whatever cleared
	 * it since the last key event (test 19: on some frames the game's own clear came after
	 * the last of the three calls above, and the movement got (0, 0)). */
	if (g_inputActive && (g_inputMode != INPUT_PASS || g_throttleWrote) && g_moveVec) {
		memcpy(g_moveVec, g_wroteMove, sizeof(g_wroteMove));
		g_wrote = true;
	}
	((Forward4)g_origOutput)(self, id, out, d);
	if ((out & 3) || !ReadableNow(out, sizeof(g_output)))
		return;
	float *o = (float *)out;
	memcpy(g_outputGame, o, sizeof(g_outputGame));
	if (g_inputActive && g_inputMode == INPUT_BACK && isfinite(o[14])) {
		o[0] = o[1] = o[2] = 0.0f;
		o[4] = o[5] = o[6] = 0.0f;
		o[8] = 0.0f;
		o[14] = g_steerHeading;
	}
	memcpy(g_output, o, sizeof(g_output));
	g_outputCalls++;
}

/* Not riding any more (or steering off): the game's own input back, nothing pushed. */
static void StopPush(void);
static void EndInput(void)
{
	g_inputActive = false;
	g_throttle = 0.0f;
	g_throttleWrote = false;
	if (StillOurs()) {
		g_moveVec[0] = g_rawMove[0];
		g_moveVec[1] = g_rawMove[1];
	}
	g_wrote = false;
	g_inputMode = INPUT_PASS;
	StopPush();
}

/* One vtable entry swapped for ours; the page's protection put back. */
static bool PatchSlot(uintptr_t slot, void *hook, void **orig)
{
	MEMORY_BASIC_INFORMATION mbi;
	if (VirtualQuery((const void *)slot, &mbi, sizeof(mbi)) != sizeof(mbi) || mbi.State != MEM_COMMIT)
		return false;
	DWORD exec = PAGE_EXECUTE | PAGE_EXECUTE_READ | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY, old;
	if (!VirtualProtect((void *)slot, 8, (mbi.Protect & exec) ? PAGE_EXECUTE_READWRITE : PAGE_READWRITE, &old))
		return false;
	*orig = *(void **)slot;
	*(void **)slot = hook;
	VirtualProtect((void *)slot, 8, old, &old);
	return true;
}

static bool IsExactly(uintptr_t obj, const char *mangled)
{
	const char *name = ObjectTypeName(obj);
	return name && strcmp(name, mangled) == 0;
}

static bool IsMovementHandler(uintptr_t obj)
{
	return IsExactly(obj, RTTI_MOVE_HANDLER) || IsExactly(obj, RTTI_MOVE_HANDLER_CLASS);
}

static uintptr_t FindMovementHandler(uintptr_t controls, const char **where)
{
	uintptr_t h = ReadPtr(controls + OFF_CONTROLS_MOVEMENT);
	if (h && IsMovementHandler(h)) {
		*where = "PlayerControls+0x1E0";
		return h;
	}
	uintptr_t list = controls + OFF_CONTROLS_HANDLERS;
	uintptr_t entries = ReadPtr(list + OFF_ARRAY_ENTRIES);
	uint32_t count = Accessible(list + OFF_ARRAY_COUNT, 4, false) ? *(const uint32_t *)(list + OFF_ARRAY_COUNT) : 0;
	for (uint32_t i = 0; entries && i < count && i < 64; i++) {
		h = ReadPtr(entries + 8 * i);
		if (h && IsMovementHandler(h)) {
			*where = "PlayerControls' handler list";
			return h;
		}
	}
	return 0;
}

/* Once, on the first ride: wrap the MovementHandler's thumbstick, button and per-frame
 * functions, if everything is where CommonLibF4 says (else log why and leave the keys alone:
 * no creep, no reverse, the plain steering clamp). With Trace=1 also the movement update's
 * view of the controls (IMovementPlayerControls::GetControllerOutput), log only. */
static void InstallInputHook(void)
{
	if (g_inputHookTried || !g_inputHook)
		return;
	uintptr_t controls = ReadPtr(g_base + RVA_PLAYER_CONTROLS);
	if (!controls || !IsA(controls, RTTI_CONTROLS))
		return;   /* not there yet: next time */
	g_inputHookTried = true;
	const char *where = "";
	uintptr_t handler = FindMovementHandler(controls, &where);
	if (!handler) {
		Log("input: no MovementHandler at PlayerControls+0x1E0 (%s there) or in its handler list: the move keys are left alone "
		    "(no creep, no reverse)", OrNone(ObjectTypeName(ReadPtr(controls + OFF_CONTROLS_MOVEMENT))));
		return;
	}
	uintptr_t data = ReadPtr(handler + OFF_HANDLER_DATA);
	uintptr_t vtbl = ReadPtr(handler);
	uintptr_t f[3] = { 0, 0, 0 };
	static const int slots[3] = { VF_THUMBSTICK, VF_BUTTON, VF_PER_FRAME };
	for (int i = 0; i < 3 && vtbl; i++)
		f[i] = ReadPtr(vtbl + 8 * slots[i]);
	if (data != controls + OFF_MOVE_INPUT || vtbl != g_base + RVA_MOVE_HANDLER_VTBL || !InImage(f[0], 1) || !InImage(f[1], 1) ||
	    !InImage(f[2], 1)) {
		Log("input: the MovementHandler (%s) isn't laid out as expected (data %p, PlayerControls+0x44 %p, vtable +0x%llX, "
		    "1.11.240's +0x%X): the move keys are left alone", where, (void *)data, (void *)(controls + OFF_MOVE_INPUT),
		    (unsigned long long)(vtbl - g_base), RVA_MOVE_HANDLER_VTBL);
		return;
	}
	g_moveHandler = handler;
	g_moveVec = (float *)(controls + OFF_MOVE_INPUT);
	g_rawMove[0] = g_moveVec[0];
	g_rawMove[1] = g_moveVec[1];
	bool ok = PatchSlot(vtbl + 8 * VF_THUMBSTICK, (void *)HookThumbstick, &g_origThumbstick);
	ok = PatchSlot(vtbl + 8 * VF_BUTTON, (void *)HookButton, &g_origButton) && ok;
	ok = PatchSlot(vtbl + 8 * VF_PER_FRAME, (void *)HookPerFrame, &g_origPerFrame) && ok;
	g_inputHooked = g_origButton != NULL;
	Log("input: MovementHandler (%s, vtable +0x%llX): thumbstick +0x%llX, button +0x%llX, per frame +0x%llX %s",
	    where, (unsigned long long)(vtbl - g_base), (unsigned long long)(f[0] - g_base), (unsigned long long)(f[1] - g_base),
	    (unsigned long long)(f[2] - g_base), ok ? "wrapped" : "NOT all wrapped (VirtualProtect failed)");

	uintptr_t base = controls + OFF_CONTROLS_IMOVE;
	const CompleteObjectLocator *c = GetCOL(base);
	uintptr_t vt2 = ReadPtr(base), out = vt2 ? ReadPtr(vt2 + 8 * VF_CONTROLLER_OUTPUT) : 0;
	if (!c || c->offset != OFF_CONTROLS_IMOVE || strcmp(TypeName(c->typeDescriptor), RTTI_CONTROLS) != 0 ||
	    vt2 != g_base + RVA_CONTROLS_IMOVE_VTBL || !InImage(out, 1)) {
		Log("input: PlayerControls+0x30 isn't its IMovementPlayerControls: the movement output isn't held while backing");
		return;
	}
	g_outputHooked = PatchSlot(vt2 + 8 * VF_CONTROLLER_OUTPUT, (void *)HookOutput, &g_origOutput);
	Log("input: IMovementPlayerControls::GetControllerOutput +0x%llX %s", (unsigned long long)(out - g_base),
	    g_outputHooked ? "wrapped (holds the heading while backing up)" : "NOT wrapped");
}

/* ------------------------------------------------------------------------- */
/* Reverse: pushing the bike back                                            */
/* ------------------------------------------------------------------------- */

/* Holding back, the game gets no input at all (it would drive forward), and the plugin backs
 * the bike up at BackSpeed itself: the game's movement only ever goes forward along the facing
 * (test 15: the movement output turned round, or at a negative speed, didn't move it). Of the
 * character controller's own, velocityMod (+0x180) and SetLinearVelocityImpl (vfunc 0x3A)
 * didn't move it (test 14), nor pushDelta (+0x1B0, test 16: the game only adds to it from
 * contacts and clears it), and a step through SetPositionImpl (0x34) did, but through walls.
 * So BackPush=auto makes steps through SetPositionImpl, each only after rays cast with the
 * game's own picking say the way back is clear (test 16: they stop it at cars, fences, rocks,
 * trees): ground just behind the rider and under the rear, nothing at knee height on either
 * side or at chest height between, along the heading it would back up on. With a side key the
 * turn is tried first; if that way isn't clear it backs up straight, and if that isn't either
 * it neither turns nor moves (test 16: turning without looking swung the rear into a car).
 * The step is kept only if the bike really goes back (more than 30% of BackSpeed 0.6 s into
 * holding back, counted from when it's stopped rolling forward and not while something
 * behind stops it); else back brakes. BackPush=delta, ray, mod, velocity or position use only
 * that one (position: the steps without rays, through walls). SetPositionImpl only once
 * GetPositionImpl (0x33) has given the player's position, which also says Havok's units (1/70
 * of the game's) or the game's. */
typedef void (*GetVecFn)(uintptr_t self, float *out);
typedef void (*SetVecFn)(uintptr_t self, const float *v);
typedef void (*GetPosFn)(uintptr_t self, float *out, bool centre);
typedef void (*SetPosFn)(uintptr_t self, const float *p, bool centre, bool warp);
static const char *const g_pushNames[] = { "pushDelta", "steps after rays", "velocityMod", "SetLinearVelocity", "SetPosition",
                                           "nothing (brake)" };
static int g_pushMethod = -1;       /* the way of backing up in use or on trial (-1: not started) */
static bool g_pushProven;           /* it moved the bike back */
static bool g_pushBlocked;          /* something behind stopped it this frame */
static bool g_pushOn;               /* backing up this frame */
static bool g_pushClock;            /* the trial's clock runs (the bike has stopped rolling forward) */
static uintptr_t g_pushCtrl;        /* pushing this controller (something to undo on letting go) */
static float g_pushHeld;            /* seconds the trial has run */
static float g_pushRetryAt;         /* after a failed trial: try the first way again from this time (0: no) */
static float g_savedMod[4], g_savedModTime;
static int g_ctrlCheck;             /* 0 not yet, 1 the controller's functions look right, -1 they don't */
static float g_havok = HAVOK_SCALE; /* game units -> the controller's */

static void *CtrlFunc(uintptr_t ctrl, int index)
{
	uintptr_t vtbl = ReadPtr(ctrl);
	uintptr_t f = vtbl ? ReadPtr(vtbl + 8 * index) : 0;
	return InImage(f, 1) ? (void *)f : NULL;
}

/* Checked once a session, by whichever of the reverse and the climb's step comes first: its
 * lines start with that caller's word ("reverse" or "climb"). */
static bool CheckControllerFuncs(uintptr_t ctrl, const float pos[3], const char *who)
{
	if (g_ctrlCheck)
		return g_ctrlCheck > 0;
	g_ctrlCheck = -1;
	GetPosFn get = (GetPosFn)CtrlFunc(ctrl, VF_CTRL_GET_POSITION);
	if (!get || !CtrlFunc(ctrl, VF_CTRL_SET_POSITION) || !CtrlFunc(ctrl, VF_CTRL_GET_VELOCITY) || !CtrlFunc(ctrl, VF_CTRL_SET_VELOCITY)) {
		Log("%s: the controller's vtable has no functions at 0x33/0x34/0x39/0x3A: not using them", who);
		return false;
	}
	/* Filled with nearly the player's position (half a unit off, in case it's a setter after
	 * all) and a marker in w that a getter overwrites. */
	__attribute__((aligned(16))) float out[16];
	memset(out, 0, sizeof(out));
	out[0] = (pos[0] + 0.5f) * HAVOK_SCALE;
	out[1] = pos[1] * HAVOK_SCALE;
	out[2] = pos[2] * HAVOK_SCALE;
	out[3] = 12345.0f;
	get(ctrl, out, false);
	float dh = 0.0f, dg = 0.0f;
	for (int i = 0; i < 3; i++) {
		dh += (out[i] / HAVOK_SCALE - pos[i]) * (out[i] / HAVOK_SCALE - pos[i]);
		dg += (out[i] - pos[i]) * (out[i] - pos[i]);
	}
	bool wrote = out[3] != 12345.0f && isfinite(out[0]) && isfinite(out[1]) && isfinite(out[2]);
	if (wrote && dh < 150.0f * 150.0f) {
		g_havok = HAVOK_SCALE;
		g_ctrlCheck = 1;
	} else if (wrote && dg < 150.0f * 150.0f) {
		g_havok = 1.0f;
		g_ctrlCheck = 1;
	}
	Log("%s: the controller's GetPositionImpl gives (%.3f, %.3f, %.3f, w %.3g) for the player at (%.0f, %.0f, %.0f): %s", who,
	    out[0], out[1], out[2], out[3], pos[0], pos[1], pos[2],
	    g_ctrlCheck < 0 ? "not the position: its functions aren't used" : g_havok < 1.0f ? "Havok's units" : "the game's units");
	return g_ctrlCheck > 0;
}

/* Climbing low things, stage 2 (test 40, finding 8: the stump beside the bike at 15:41:35.6,
 * stuck 1 to 3 s like the trunks): a sharp step of 17 to 32 meets the capsule's upright side,
 * which no climb limit takes (f8's capsule model), so the boost alone leaves the bike stuck at a
 * stump. ClimbRays calls this while the boost has been on 0.25 s and the speed along is still
 * under 40, with the line whose low face qualified this frame. Three rays straight down, 3, 12
 * and 21 past where the ray at 4 met the face, each from ClimbTop + 8 above the feet to 2 below
 * them (CastRay: an actor stops them, and isn't stepped onto), find the top: the highest hit,
 * which must be over 4 above the feet (a step lower than that the boost climbs) and ClimbTop at
 * most (the clearance ray at ClimbTop found nothing, but a top just over it can sit behind the
 * face). Two rays up, from the top's place and from where the capsule's axis goes, from 1 over
 * the top to the capsule's height (+0x374, 128) over where its feet go, must find nothing. Then
 * the controller is put up by the top + 1.5 and 4 on along the heading, through the reverse's
 * own GetPositionImpl and SetPositionImpl (test 39: its steps "(works)" 313 times; CheckController-
 * Funcs, whose one line says "climb:" when the step checks them first); only ever up, twice an
 * obstacle at most (afresh once the bike is 60 from the last step's place), 0.25 s apart. A step whose feet haven't risen by half
 * of it within 0.1 s is said (ClimbStepSeen). The reasons for no step are said once a boost.
 * Test 39's downward SetPosition put the capsule through a road; this one goes up only, onto a
 * top three rays found, with the room checked. */
static void ClimbNoStep(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
static void ClimbNoStep(const char *fmt, ...)
{
	if (g_stepRefusedSaid || !LogHandTake(&g_climbHand))
		return;
	g_stepRefusedSaid = true;
	char text[600];
	va_list args;
	va_start(args, fmt);
	vsnprintf(text, sizeof(text), fmt, args);
	va_end(args);
	Log("climb: no step: %s", text);
}

static bool ClimbStepUp(uintptr_t player, uintptr_t ctrl, uintptr_t cell, const ClimbLine *L, const float pos[3], float sh, float ch, float top)
{
	(void)player;
	static const float past[3] = { 3.0f, 12.0f, 21.0f };
	float p = g_pitchNow / 57.29578f, cp = cosf(p), sp = sinf(p);
	/* Where the ray at 4 met the face: ClimbRays' own ray, from the line's origin 4 up the
	 * pitched axis, d4 along it. */
	float hit[2] = { pos[0] + ch * L->side - sh * sp * 4.0f + sh * cp * L->d4, pos[1] - sh * L->side - ch * sp * 4.0f + ch * cp * L->d4 };
	float z[3], at[3][2], ahead[3], bestZ = -1000.0f;
	const char *what = "unnamed";
	uint32_t layer = 0;
	int best = -1;
	char reads[160] = "";
	for (int i = 0; i < 3; i++) {
		float a[3] = { hit[0] + sh * past[i], hit[1] + ch * past[i], pos[2] + top + 8.0f };
		float b[3] = { a[0], a[1], pos[2] - 2.0f };
		at[i][0] = a[0];
		at[i][1] = a[1];
		ahead[i] = (a[0] - pos[0]) * sh + (a[1] - pos[1]) * ch;
		float f = CastRay(cell, a, b);
		z[i] = f >= 0.0f && f < 1.0f ? a[2] + (b[2] - a[2]) * f - pos[2] : NAN;
		char one[24];
		if (isfinite(z[i]))
			snprintf(one, sizeof(one), "%s%.1f", i ? ", " : "", z[i]);
		else
			snprintf(one, sizeof(one), "%snothing", i ? ", " : "");
		strncat(reads, one, sizeof(reads) - strlen(reads) - 1);
		if (isfinite(z[i]) && z[i] > bestZ) {
			bestZ = z[i];
			best = i;
			what = g_rayWhat && *g_rayWhat ? g_rayWhat : "unnamed";
			layer = g_rayLayer;
		}
	}
	if (best < 0) {
		ClimbNoStep("nothing under the rays down at %.0f-%.0f ahead (from %.1f above the feet to 2 below them)", ahead[0], ahead[2], top + 8.0f);
		return false;
	}
	if (bestZ > top) {
		ClimbNoStep("the top %.1f (over ClimbTop, %.1f; %s, layer %u): the rays down at %.0f-%.0f ahead read %s", bestZ, top, what, layer, ahead[0], ahead[2], reads);
		return false;
	}
	if (bestZ <= 4.0f) {
		ClimbNoStep("the top %.1f (4 or less: nothing to step onto; %s, layer %u): the rays down at %.0f-%.0f ahead read %s", bestZ, what, layer, ahead[0], ahead[2], reads);
		return false;
	}
	if (layer == LAYER_CHAR_CONTROLLER || layer == LAYER_BIPED) {
		ClimbNoStep("the top %.1f is an actor's (%s, layer %u)", bestZ, what, layer);
		return false;
	}
	float rise = bestZ + 1.5f;
	float axis[2] = { pos[0] + sh * 4.0f, pos[1] + ch * 4.0f };
	for (int k = 0; k < 2; k++) {
		const float *xy = k == 0 ? at[best] : axis;
		float a[3] = { xy[0], xy[1], pos[2] + bestZ + 1.0f }, b[3] = { xy[0], xy[1], pos[2] + rise + g_capsuleHeight };
		float f = CastRay(cell, a, b);
		if (f >= 0.0f && f < 1.0f) {
			ClimbNoStep("no room above it (%s, layer %u, %.0f over the top %.1f %s; the capsule's height %.0f)", g_rayWhat && *g_rayWhat ? g_rayWhat : "unnamed", g_rayLayer,
			            1.0f + (b[2] - a[2]) * f, bestZ, k == 0 ? "where the rays down found it" : "where the capsule would stand", g_capsuleHeight);
			return false;
		}
	}
	if (!CheckControllerFuncs(ctrl, pos, "climb")) {
		ClimbNoStep("the controller's GetPositionImpl and SetPositionImpl can't be used (the check the reverse shares)");
		return false;
	}
	GetPosFn get = (GetPosFn)CtrlFunc(ctrl, VF_CTRL_GET_POSITION);
	SetPosFn set = (SetPosFn)CtrlFunc(ctrl, VF_CTRL_SET_POSITION);
	__attribute__((aligned(16))) float q[16] = { 0 };
	if (!get || !set) {
		ClimbNoStep("the controller's GetPositionImpl or SetPositionImpl is gone");
		return false;
	}
	get(ctrl, q, false);
	if (!isfinite(q[0]) || !isfinite(q[1]) || !isfinite(q[2])) {
		ClimbNoStep("GetPositionImpl gave (%g, %g, %g): not a position", q[0], q[1], q[2]);
		return false;
	}
	float clock = (float)g_clock;
	g_stepPos[0] = pos[0];   /* before the step: the fake's SetPositionImpl moves the player's own position at once */
	g_stepPos[1] = pos[1];
	g_stepZ0 = pos[2];
	g_stepWant = rise;
	g_stepRose = 0.0f;
	g_stepAt = clock;
	g_stepCheck = true;
	g_stepCount++;
	g_stepsThisBoost++;
	q[0] += sh * 4.0f * g_havok;
	q[1] += ch * 4.0f * g_havok;
	q[2] += rise * g_havok;   /* only ever up: the top is over 4 */
	set(ctrl, q, false, false);   /* the third argument is ignored (test 19) */
	if (LogHandTake(&g_climbHand))
		Log("climb: stepped up %.1f (the top %.1f at %.0f-%.0f ahead, the rays down reading %s; %s, layer %u) and 4 on, room for the capsule's %.0f over it [%d of 2]",
		    rise, bestZ, ahead[0], ahead[2], reads, what, layer, g_capsuleHeight, g_stepCount);
	return true;
}

/* A frame or more after a step: the feet's rise since. Half the step within 0.1 s, it took (the
 * "over it" line says the feet's rise); else said. */
static void ClimbStepSeen(const float pos[3])
{
	if (!g_stepCheck)
		return;
	float since = (float)g_clock - g_stepAt, rose = pos[2] - g_stepZ0;
	if (since <= 0.0f)
		return;   /* the step's own frame */
	if (rose > g_stepRose)
		g_stepRose = rose;
	if (g_stepRose >= 0.5f * g_stepWant) {
		g_stepCheck = false;
		return;
	}
	if (since < 0.1f)
		return;
	g_stepCheck = false;
	if (LogHandTake(&g_climbHand))
		Log("climb: the step up didn't take: the feet %.1f up at most in %.2f s, %.1f asked (SetPositionImpl not honoured, or the capsule put back)", g_stepRose, since, g_stepWant);
}

/* --- Rays, cast with the game's own picking (found through the Address Library) --- */

typedef void *(*PickCtorFn)(void *pick);
typedef void (*PickResetFn)(void *pick);
typedef void (*PickSetFn)(void *pick, const float *start, const float *end);
typedef bool (*PickHasHitFn)(const void *pick);
typedef float (*PickFractionFn)(const void *pick);
typedef uintptr_t (*CellPickFn)(uintptr_t cell, void *pick);
static PickCtorFn g_pickCtor;
static PickResetFn g_pickReset;
static PickSetFn g_pickSet;
static PickHasHitFn g_pickHasHit;
static PickFractionFn g_pickFraction;
static CellPickFn g_cellPick;
static int g_pickFuncs;             /* 0 not looked for, 1 found (and the pick data made), -1 not */
static int g_pickState;             /* 0 not tested (since a load), 1 rays work, -1 they can't be used */
static uint64_t g_solidMask;        /* the layers the rays stop at, a bit each, from the character controller's collision layer record (0: not read, the built-in table) */
static bool g_solidMaskRead;        /* the record read this load (at the rays' test) */
static __attribute__((aligned(16))) uint8_t g_pick[PICK_DATA_SIZE + 0x20];   /* one, reused: no world reference per ray */
static uint32_t g_rayFilter = LAYER_CHAR_CONTROLLER;   /* the rays' collision filter (0 = everything, if the test says) */
static float g_rayHit[3];           /* where the last ray's hit was (what it hit and its layer: g_rayWhat, g_rayLayer, with the tilt's state) */
static float g_rayGroundNear, g_rayGroundFar;   /* the ground just behind and under the rear, for the trace */
static float g_rayFeetGap = -99.0f, g_rayDz;   /* the feet ray's gap under the feet (-99: no ray) and the step's dz, for the trace */
static float g_pickRetryAt;         /* a failed test ray is tried again from then */
static float g_passedLogged = -100.0f;
static char g_wayWhy[200];          /* why the way back isn't clear (the last check) */
static bool g_wayQuiet;             /* checking a turn: say why only if it stops the bike too */
static float g_blockedLogged = -100.0f;

/* F4SE's Address Library (version-1-11-240-0.bin): a count, then {id, offset} pairs sorted by
 * id; the offset is from the game's image base. Looked for next to this plugin, then in the
 * game's Data\F4SE\Plugins (with Mod Organizer the plugin's own folder is its mod's). */
static FILE *OpenAddressLibrary(char *path, size_t size)
{
	GetModuleFileNameA(g_module, path, (DWORD)size);
	char *slash = strrchr(path, '\\');
	if (slash && (size_t)(slash + 1 - path) + sizeof(ADDRESS_LIBRARY) <= size) {
		strcpy(slash + 1, ADDRESS_LIBRARY);
		FILE *f = fopen(path, "rb");
		if (f)
			return f;
	}
	GetModuleFileNameA(NULL, path, (DWORD)size);
	slash = strrchr(path, '\\');
	const char *rest = "Data\\F4SE\\Plugins\\" ADDRESS_LIBRARY;
	if (slash && (size_t)(slash + 1 - path) + strlen(rest) + 1 <= size) {
		strcpy(slash + 1, rest);
		return fopen(path, "rb");
	}
	return NULL;
}

static uintptr_t AddressOf(FILE *f, uint64_t count, uint64_t id)
{
	uint64_t lo = 0, hi = count;
	while (lo < hi) {
		uint64_t mid = lo + (hi - lo) / 2, pair[2];
		if (_fseeki64(f, (long long)(8 + 16 * mid), SEEK_SET) != 0 || fread(pair, 16, 1, f) != 1)
			return 0;
		if (pair[0] == id)
			return InImage(g_base + (uintptr_t)pair[1], 16) ? g_base + (uintptr_t)pair[1] : 0;
		if (pair[0] < id)
			lo = mid + 1;
		else
			hi = mid;
	}
	return 0;
}

/* What a ray passes through. First the phantoms: triggers (12), acoustic spaces (21), actor
 * zones (22, test 17: the "nothing" test 16 stopped at on a flat slab), projectile zones (23),
 * gas traps (24) and door detection (37), and the ones the character controller's own
 * collides-with list holds as well (test 37: a tripwire or a gas cloud would present as a
 * wall): spells (7), cloud traps (16), the query and pick layers 38 to 46 (cone projectile,
 * camera, item picker, line of sight, pathing pick, custom picks, spell explosion 45,
 * dropping pick 46), living-and-dead actors (52), trap triggers (54) and character bumpers
 * (56); and what the capsule pushes aside or steps over: clutter (4), weapons (5), small
 * debris (19), shell casings (25), dead bodies (32), and water (11: the ground ray then
 * finds the bed, so deep water is a drop). Then the character controller's own collides-with
 * list (ReadSolidMask; test 36: the pick's filter 30 doesn't keep out what the capsule never
 * meets, and food bushes (15, non-collidable), a fire truck's navcut shape (49) and a dog (8,
 * biped) read as walls): solid only if the layer is in it. Without the list everything else
 * stops the bike (test 17: a chain-link fence is layer 26, transparent small, and was passed
 * through) but those three layers and 64 and over. */
static bool SolidLayer(uint32_t layer)
{
	switch (layer) {
	case 4: case 5: case 7: case 11: case 12: case 16: case 19: case 21: case 22: case 23: case 24: case 25: case 32: case 37:
	case 38: case 39: case 40: case 41: case 42: case 43: case 44: case 45: case 46: case 52: case 54: case 56:
		return false;
	default:
		break;
	}
	if (g_solidMask)
		return layer < 64 && ((g_solidMask >> layer) & 1u);
	return layer != 8 && layer != 15 && layer != 49 && layer < 64;
}

/* One candidate layout of the character controller's collision layer record: its collision
 * index at `idxAt`, its collides-with array at `arrayAt`. Taken only if every read is
 * accessible, the index is 30, the count 1 to 64 and no more than the capacity, and every
 * entry a BGSCollisionLayer whose own index (at the same offset) is under 64; else why not. */
static bool LayerMaskAt(uintptr_t form, uint32_t idxAt, uint32_t arrayAt, uint64_t *mask, char *why, size_t whySize)
{
	if (!Accessible(form + idxAt, 4, false) || !Accessible(form + arrayAt, OFF_ARRAY_COUNT + 4, false)) {
		snprintf(why, whySize, "the fields at +0x%X and +0x%X can't be read", idxAt, arrayAt);
		return false;
	}
	uint32_t idx = *(const uint32_t *)(form + idxAt);
	if (idx != LAYER_CHAR_CONTROLLER) {
		snprintf(why, whySize, "the collision index at +0x%X is %u, not %u", idxAt, idx, LAYER_CHAR_CONTROLLER);
		return false;
	}
	uintptr_t entries = ReadPtr(form + arrayAt + OFF_ARRAY_ENTRIES);
	uint32_t capacity = *(const uint32_t *)(form + arrayAt + OFF_ARRAY_CAPACITY);
	uint32_t count = *(const uint32_t *)(form + arrayAt + OFF_ARRAY_COUNT);
	if (count < 1 || count > 64 || count > capacity || !entries || !Accessible(entries, 8u * count, false)) {
		snprintf(why, whySize, "the collides-with array at +0x%X has %u entries (capacity %u%s)", arrayAt, count, capacity,
		         entries ? "" : ", no entries pointer");
		return false;
	}
	uint64_t m = 0;
	for (uint32_t i = 0; i < count; i++) {
		uintptr_t layer = *(const uintptr_t *)(entries + 8u * i);
		if (!layer || !IsA(layer, RTTI_COLLISION_LAYER) || !Accessible(layer + idxAt, 4, false)) {
			snprintf(why, whySize, "entry %u of the collides-with array at +0x%X isn't a BGSCollisionLayer", i, arrayAt);
			return false;
		}
		uint32_t li = *(const uint32_t *)(layer + idxAt);
		if (li >= 64) {
			snprintf(why, whySize, "entry %u's collision index at +0x%X is %u, not under 64", i, idxAt, li);
			return false;
		}
		m |= 1ull << li;
	}
	*mask = m;
	return true;
}

/* The layers the rays stop at (test 36: the pick's filter 30 isn't the capsule's own filter,
 * and food bushes (layer 15, non-collidable), a fire truck's navcut shape (49) and Dogmeat
 * (8) read as walls and stopped the bike): the character controller's own collision layer
 * record, COLL 0008877F in Fallout4.esm, lists what it collides with. BGSCollisionLayer is
 * TESForm (0x20 bytes), then TESDescription (0x18: a vtable, a file offset, a chunk offset
 * and a BGSLocalizedStringDL), then the collision index at +0x38, a debug colour, flags, a
 * name and the collides-with array at +0x50 (entries, capacity, count, as the other arrays
 * read here; the record is 0x68 bytes). Test 37: the first build tried +0x30 (it read 874)
 * and +0x28 (328138080), as if TESDescription were 0x10 or 8 bytes; those two layouts are
 * tried second and third now, and the log says what each read. Without a record that
 * validates, the built-in table (SolidLayer). Once per load, at the rays' test. */
static void ReadSolidMask(void)
{
	char why[640];
	uint64_t mask = 0;
	g_solidMask = 0;
	uintptr_t form = ((LookupFormByID_t)(g_base + RVA_LOOKUP_FORM))(COLL_CHAR_CONTROLLER);
	if (!form) {
		snprintf(why, sizeof(why), "no such form");
	} else if (!IsA(form, RTTI_COLLISION_LAYER)) {
		snprintf(why, sizeof(why), "the form is %.40s, not a BGSCollisionLayer", OrNone(ObjectTypeName(form)));
	} else {
		size_t len = 0;
		for (uint32_t back = 0; back <= 16 && !mask; back += 8) {   /* TESDescription 0x18, 0x10 or 8 bytes: the fields 0, 8 or 16 earlier */
			char one[200];
			if (LayerMaskAt(form, OFF_COLL_INDEX - back, OFF_COLL_COLLIDES - back, &mask, one, sizeof(one)))
				break;
			len += (size_t)snprintf(why + len, sizeof(why) - len, "%s%s", len ? "; " : "", one);
		}
	}
	if (!mask) {
		Log("rays: COLL %08X can't be read as the character controller's collision layer (%s): the built-in layer table", COLL_CHAR_CONTROLLER, why);
		return;
	}
	char list[256];
	size_t len = 0;
	int n = 0;
	for (uint32_t layer = 0; layer < 64; layer++) {
		if (!((mask >> layer) & 1u))
			continue;
		len += (size_t)snprintf(list + len, sizeof(list) - len, "%s%u", n ? " " : "", layer);
		n++;
	}
	g_solidMask = mask;
	Log("rays: the character controller's collision layer (COLL %08X) collides with layers %s (%d of them): the rays stop at those, bar the phantoms",
	    COLL_CHAR_CONTROLLER, list, n);
}

/* Is the hit's 3D the rider's own: the player's root (the capsule's shape is on it), or under
 * it (the body, the worn bike)? Test 36: the face rays start at the player's position, inside
 * the capsule, and read 'skeleton.nif' (layer 30, and the body's 8) as an obstacle a unit past
 * the rays' start, 125 behind the front wheel's edge, the throttle held to ObstacleThrottle.
 * Up through the parents, 24 at most (test 37: the arm bones sit 10 and more deep in the
 * skeleton, past the 8 the first build walked). */
static bool RidersOwn(uintptr_t obj)
{
	for (int i = 0; obj && i < 24; i++) {
		if (obj == g_riderRoot)
			return true;
		obj = ReadPtr(obj + OFF_PARENT);
		if (obj && !IsA(obj, RTTI_AVOBJECT))
			return false;
	}
	return false;
}

/* Set around a cast that looks for the ground (CastRayGround): actors are passed through, the
 * layers of their capsules (30, kCharController) and bodies (8, kBiped; already passed unless
 * the controller's collides-with list has it); dead bodies are 32, passed by every ray. */
static bool g_rayGround;
static float g_actorPassedLogged = -100.0f;

/* One ray from a to b (game units): the fraction along it where it first hits something solid
 * (1 if nothing), passing on through anything that isn't; what it hit in g_rayWhat, its layer
 * in g_rayLayer and where in g_rayHit. */
static float CastRay(uintptr_t cell, const float a[3], const float b[3])
{
	float from[3] = { a[0], a[1], a[2] }, done = 0.0f, t = 1.0f;
	float len = sqrtf((b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1]) + (b[2] - a[2]) * (b[2] - a[2]));
	bool lastActor = false;   /* the last thing passed was an actor (a ground ray's) */
	for (int tries = 0; tries < 8; tries++) {
		g_rayWhat = NULL;
		g_rayObj = 0;
		g_pickReset(g_pick);
		*(uint32_t *)(g_pick + OFF_PICK_FILTER) = g_rayFilter;
		g_pickSet(g_pick, from, b);
		uintptr_t obj = g_cellPick(cell, g_pick);
		if (!g_pickHasHit(g_pick))
			return 1.0f;
		float f = g_pickFraction(g_pick);
		f = isfinite(f) && f >= 0.0f && f <= 1.0f ? f : 0.0f;
		t = done + (1.0f - done) * f;
		g_rayLayer = *(const uint32_t *)(g_pick + OFF_PICK_HIT_LAYER) & 0x7F;
		for (int i = 0; i < 3; i++)
			g_rayHit[i] = a[i] + (b[i] - a[i]) * t;
		bool own = false;   /* the rider's own 3D: passed through like a layer that isn't solid (test 36) */
		bool let = false;   /* an actor the bike is to knock over: passed through by the face rays and WallAhead (rams) */
		if (obj && IsA(obj, RTTI_AVOBJECT)) {
			g_rayWhat = ObjectName(obj);
			g_rayObj = obj;
			own = RidersOwn(obj);
			let = !own && g_rayLetByCount > 0 && RamLetByHas(obj);
		}
		bool solid = !own && !let && SolidLayer(g_rayLayer);
		bool body = !own && !let && g_rayGround && (g_rayLayer == LAYER_CHAR_CONTROLLER || g_rayLayer == LAYER_BIPED);   /* an actor's capsule or body under a ground ray, solid to the filter or not (a body, 8, is passed as clutter otherwise) */
		bool actor = solid && body;
		if (solid && !actor)
			return t;
		lastActor = body;
		if (actor) {
			if (g_trace && g_clock - g_actorPassedLogged >= 1.0f) {   /* a clock of its own: an actor by the wheels every frame mustn't hide the other passes */
				g_actorPassedLogged = g_clock;
				Log("rays: a ground ray passed through %s (layer %u): an actor, not the ground", g_rayWhat && *g_rayWhat ? g_rayWhat : "unnamed", g_rayLayer);
			}
		} else if (g_trace && g_clock - g_passedLogged >= 1.0f) {
			g_passedLogged = g_clock;
			if (own)
				Log("reverse: a ray passed through the rider's own 3D (%s, layer %u)", g_rayWhat && *g_rayWhat ? g_rayWhat : "unnamed", g_rayLayer);
			else if (let)
				Log("rams: a ray passed through %s (layer %u): an actor to be knocked over", g_rayWhat && *g_rayWhat ? g_rayWhat : "unnamed", g_rayLayer);
			else
				Log("reverse: a ray passed through %s (layer %u)", g_rayWhat && *g_rayWhat ? g_rayWhat : "unnamed", g_rayLayer);
		}
		done = t + 4.0f / (len > 1.0f ? len : 1.0f);   /* on from past it */
		if (done >= 1.0f)
			return 1.0f;
		for (int i = 0; i < 3; i++)
			from[i] = a[i] + (b[i] - a[i]) * done;
	}
	/* Out of tries in a pile of things passed through: counted as a hit (test 18: a ray down
	 * through a broken fence's bits read as no ground, a drop). Not when the last thing passed
	 * was an actor (a ground ray's, CastRayGround): each actor passed takes a try since test 39,
	 * and the point counted would be the actor's, a radstag's back read as the ground again
	 * (review of test 40's first build): no hit, as if the ray had found nothing (the wheels'
	 * rays then have no word that frame: the track's pitch, or the pitch held, and the lift
	 * held for 3 s). A pile of clutter under an actor still ends on the clutter. */
	if (lastActor) {
		g_rayWhat = NULL;   /* nothing hit: the actor's name and layer aren't the ray's (RaysReady's line) */
		g_rayObj = 0;
		g_rayLayer = 0;
		return 1.0f;
	}
	return t;
}

/* A ray that looks for the ground: as CastRay, but through actors (g_rayGround). The wheels'
 * rays, the reverse's ground just behind and under the rear and its ray under the feet, and
 * the rays' test ray beside the bike; not the face rays, WallAhead or the reverse's knee and
 * chest rays, so an actor ahead or behind (Dogmeat) still stops or slows the bike. Test 39,
 * 01:34:11.5: a radstag in front, the front wheel's ray hit its capsule 107 above the feet
 * (SkeletonExport, layer 30), and the bike reared up at it for 0.6 s. */
static float CastRayGround(uintptr_t cell, const float a[3], const float b[3])
{
	g_rayGround = true;
	float f = CastRay(cell, a, b);
	g_rayGround = false;
	return f;
}

/* Once: the functions from the Address Library and the pick data made (one, reused, so no
 * Havok world reference is left behind per ray). Then, once per load: one ray down beside the
 * bike must find the ground about where the player stands, else rays aren't used. */
static bool FindPickFunctions(void)
{
	if (g_pickFuncs)
		return g_pickFuncs > 0;
	g_pickFuncs = -1;
	char path[MAX_PATH * 2];
	FILE *f = OpenAddressLibrary(path, sizeof(path));
	if (!f) {
		Log("reverse: no Address Library (%s, also looked for next to this plugin): no rays", path);
		return false;
	}
	uint64_t count = 0;
	uintptr_t ctor = 0, set = 0, reset = 0, hit = 0, fraction = 0, pick = 0;
	if (fread(&count, 8, 1, f) == 1 && count > 0 && count < 100000000u) {
		ctor = AddressOf(f, count, ID_PICK_CTOR);
		set = AddressOf(f, count, ID_PICK_SET_START_END);
		reset = AddressOf(f, count, ID_PICK_RESET);
		hit = AddressOf(f, count, ID_PICK_HAS_HIT);
		fraction = AddressOf(f, count, ID_PICK_HIT_FRACTION);
		pick = AddressOf(f, count, ID_CELL_PICK);
	}
	fclose(f);
	Log("reverse: Address Library %s (%llu ids): bhkPickData ctor +0x%llX, SetStartEnd +0x%llX, Reset +0x%llX, HasHit +0x%llX, "
	    "GetHitFraction +0x%llX, TESObjectCELL::Pick +0x%llX", path, (unsigned long long)count,
	    (unsigned long long)(ctor ? ctor - g_base : 0), (unsigned long long)(set ? set - g_base : 0),
	    (unsigned long long)(reset ? reset - g_base : 0), (unsigned long long)(hit ? hit - g_base : 0),
	    (unsigned long long)(fraction ? fraction - g_base : 0), (unsigned long long)(pick ? pick - g_base : 0));
	if (!ctor || !set || !reset || !hit || !fraction || !pick) {
		Log("reverse: a function missing: no rays");
		return false;
	}
	g_pickCtor = (PickCtorFn)ctor;
	g_pickSet = (PickSetFn)set;
	g_pickReset = (PickResetFn)reset;
	g_pickHasHit = (PickHasHitFn)hit;
	g_pickFraction = (PickFractionFn)fraction;
	g_cellPick = (CellPickFn)pick;
	memset(g_pick, 0, sizeof(g_pick));
	g_pickCtor(g_pick);
	g_pickFuncs = 1;
	return true;
}

static bool RaysReady(uintptr_t player)
{
	if (g_pickState < 0 && g_clock >= g_pickRetryAt)
		g_pickState = 0;   /* test 16: a first test on rubble or a bridge shouldn't turn rays off for the load */
	if (g_pickState)
		return g_pickState > 0;
	g_pickState = -1;
	g_pickRetryAt = g_clock + 3.0f;
	uintptr_t cell = ReadPtr(player + OFF_REFR_CELL);
	if (!FindPickFunctions())
		return false;
	if (!g_solidMaskRead) {   /* the layers the rays stop at: once per load, before the test ray goes by them */
		g_solidMaskRead = true;
		ReadSolidMask();
	}
	if (!cell || !IsA(cell, RTTI_CELL)) {
		Log("reverse: no parent cell: no rays");
		return false;
	}
	const float *pos = (const float *)(player + OFF_REFR_POS);
	float h = *(const float *)(player + OFF_REFR_HEADING);
	float a[3] = { pos[0] - sinf(h) * 60.0f, pos[1] - cosf(h) * 60.0f, pos[2] + 100.0f };
	float b[3] = { a[0], a[1], pos[2] - 100.0f };
	g_rayFilter = LAYER_CHAR_CONTROLLER;
	float down = CastRayGround(cell, a, b);   /* through actors: a dog beside the bike isn't the ground */
	if (!(down > 0.2f && down < 0.8f)) {
		g_rayFilter = 0;   /* the character's filter finds no ground: everything, then */
		down = CastRayGround(cell, a, b);
	}
	bool ok = down > 0.2f && down < 0.8f;
	Log("reverse: a test ray down beside the bike (filter %u) hit %s (layer %u) at %.2f of the way (the ground about where the "
	    "player stands is 0.2-0.8): %s; the pick data's world %p, collector %p", g_rayFilter,
	    g_rayWhat && *g_rayWhat ? g_rayWhat : down < 1.0f ? "something" : "nothing", down < 1.0f ? g_rayLayer : 0, down,
	    ok ? "rays work" : "not trusted (tried again in 3 s)", *(void **)(g_pick + 0xC0), *(void **)(g_pick + 0xD0));
	g_pickState = ok ? 1 : -1;
	return ok;
}

/* Does the controller hold itself supported: the supported bit (0x400 of its flags, set by
 * CheckSupportImpl from the manifold: test 19) and the character state on the ground (0; a
 * state not read, -1 or -2, leaves the bit to say)? Read as the backing trace line reads them. */
static bool ControllerSupported(uintptr_t ctrl)
{
	if (!ctrl || !Accessible(ctrl + OFF_CTRL_FLAGS, 4, false))
		return false;
	return (*(const uint32_t *)(ctrl + OFF_CTRL_FLAGS) & 0x400u) != 0 && g_lastState <= 0;
}

/* Backing level or down follows the ground (test 40's finding 6, "backing up makes the camera
 * shake a bit": the whole picture shook, the bike still on screen, the background jumping about
 * 5 px at 1080p at -80 a second, while the applied pitch was smooth, 12.0 -> 8.9 over
 * 15:43:05.7-07.0, and the controller's own ground normal flickered, its roll +9 -> -15 -> +10:
 * the camera followed the controller's height steps). Once the controller said it was in the
 * air, the step's dz was "close the gap to the hover", mostly 0 (-0.00 in 47 of 69 in-air rays
 * lines, the mean gap 0.34), and the game's gravity carried the bike down in hops (a model of
 * it, 200 steps a second at 686 u/s^2: 10-25 landings a second, the vertical speed swinging
 * between 0 and 25-50); supported, the slope 55 back ran ahead of the ground under the feet on
 * brows, 4-19 units over a stretch, and each of the three runs flipped into the air right after
 * one (15:42:52.171, 15:43:07.972, 15:43:18.250). Now each step follows the ground's slope over
 * BackFollow units centred on the middle of the step (two more rays, from 8 above the feet to 52
 * below), supported or not: a 10-unit window cuts a change of slope by 0.6 at most at test 40's
 * largest (about 6 to 32 deg) where the slope 55 back ran 4-19 ahead, its sum telescopes (the
 * follow keeps to the 10-averaged ground, no drift), and a ripple shorter than it is averaged
 * out. Unsupported, a gap is closed only down to the controller's own clearance, the gap after a
 * step while it was supported (an average over BACK_OWN_TAU), never under BACK_HOVER, over
 * BackClose: at test 40's flips (the gaps 5.3 and 2.0, its own) nothing is closed, where test
 * 40's rule took 4.8 and 1.5 at once, test 39's hazard. Steeper than 50 deg down (or 27 up) is an
 * edge: no follow that step, gravity and the capped closing take it. The harness's mode 12: down
 * a brow and a dip supported, the feet within 0.48 of the ground (test 40's rule: 8.9 under at
 * the brow); down 20 deg in the air all the way with a fake fall of 686 u/s^2, the step's dz 0 in
 * none of the steps and the fall 0% of the way down (71% and 91%), the vertical speed changing
 * 0.2-2.2 a second from one step to the next at the 99th percentile (43-45). */
enum { BACK_NONE, BACK_WINDOW, BACK_HELD, BACK_SLOPE55, BACK_EDGE, BACK_UP, BACK_OLD };
#define BACK_EDGE_DOWN 1.19f     /* tan 50 deg */
#define BACK_EDGE_UP 0.5f        /* 27 deg up */
#define BACK_HOLD 0.1f           /* a window ray finding no ground, its last slope is used this long, then the slope 55 back */
#define BACK_OWN_TAU 0.25f       /* the controller's own clearance: the gap after a step, over this many seconds of supported steps */
#define BACK_CLOSE_SPEED 120.0f  /* units a second the closing goes at most: about the landing speed of a fall of 10 */
#define BACK_LEVEL 2.0f          /* the ground 55 behind less than this above the feet: level (2 deg), the window followed */
static int g_backKind;                 /* how the last step's follow was had (BACK_...), for the trace */
static float g_backS, g_backSAt;       /* the window's last slope (units down per unit back, - down), and when */
static bool g_backSHave;
static float g_backOwn;                /* the controller's own clearance under the feet */
static bool g_backOwnSet;
static bool g_backFresh = true;        /* the next step starts a push (StopPush sets it) */
static float g_backFollowDz, g_backClosing, g_backAhead, g_backBehind;   /* the last step's follow and closing, and the window's ground ahead of the step's middle and behind it (from the feet) */
static bool g_backSupKnown, g_backSupPrev;   /* the controller's support at the last step of this push */
static double g_backSupSince;          /* since when it has been so */
static float g_backFlipLogged = -100.0f;
static int g_backFlips, g_backFlipsQuiet;   /* the flips this push, those since the last flip line not said */
/* The trace's height line (every 0.25 s while backing): the step being made (its dz is in the
 * player's z from the next step on), and the steps since the last line. */
static bool g_hgtHave, g_hgtVzHave;
static float g_hgtZ, g_hgtLineZ, g_hgtPendDz, g_hgtPendVel, g_hgtOurs, g_hgtDvMax, g_hgtVz, g_hgtVelMin, g_hgtVelMax;
static bool g_hgtPendSup, g_hgtPendHasVel;
static double g_hgtAt;
static int g_hgtCalls, g_hgtSup, g_hgtVels;

/* A push back starts: the window, the controller's own clearance and the flips start afresh;
 * the capsule's fields and its gravity said (Trace=1), as the climb's line reads them. */
static void BackPushStart(uintptr_t ctrl)
{
	g_backFresh = false;
	g_backSHave = g_backOwnSet = g_backSupKnown = false;
	g_backFlips = g_backFlipsQuiet = 0;
	g_hgtHave = false;
	g_backKind = BACK_NONE;
	if (!g_trace)
		return;
	float f[6];
	CapsuleFields(ctrl, f);
	float gravity = ctrl && Accessible(ctrl + 0x330, 4, false) ? *(const float *)(ctrl + 0x330) : NAN;
	Log("reverse: a push back starts, the controller %s; its capsule radius %.1f, height %.1f, step height %.1f, cast depth %.1f (+0x370/+0x374/+0x424/+0x430), "
	    "gravity %g (+0x330); %s",
	    ControllerSupported(ctrl) ? "supported" : "not supported", f[0] / HAVOK_SCALE, f[1] / HAVOK_SCALE, f[2] / HAVOK_SCALE, f[5] / HAVOK_SCALE, gravity,
	    g_backFollow > 0.0f ? "its own clearance is the first gap read if it's supported then, else the hover (0.5)"
	                        : "test 40's rule (BackFollow=0)");
}

/* Every backing step (the step made or not): the flips of the controller's support, said at most
 * once a second (Trace=1), and the height line's sums. dz: what this step moved the feet. */
static void BackStepDone(uintptr_t player, uintptr_t ctrl, float dz)
{
	bool sup = ControllerSupported(ctrl);
	double now = Clock();
	if (!g_backSupKnown) {
		g_backSupKnown = true;
		g_backSupPrev = sup;
		g_backSupSince = now;
	} else if (sup != g_backSupPrev) {
		float lasted = (float)(now - g_backSupSince);
		g_backSupPrev = sup;
		g_backSupSince = now;
		g_backFlips++;
		if (g_trace && g_clock - g_backFlipLogged >= 1.0f) {
			g_backFlipLogged = g_clock;
			char count[80], own[24];
			if (g_backFlipsQuiet)
				snprintf(count, sizeof(count), "flip %d of this push, %d since the last line not said", g_backFlips, g_backFlipsQuiet);
			else
				snprintf(count, sizeof(count), "flip %d of this push", g_backFlips);
			if (g_backOwnSet)
				snprintf(own, sizeof(own), "own %+.1f", g_backOwn);
			else
				snprintf(own, sizeof(own), "own not read yet");
			if (!sup)
				Log("reverse: the controller in the air after %.2f s supported (gap %+.1f, %s): closing %.2f (%s)", lasted, g_rayFeetGap, own, g_backClosing, count);
			else
				Log("reverse: the controller supported again after %.2f s in the air (gap %+.1f, %s) (%s)", lasted, g_rayFeetGap, own, count);
			g_backFlipsQuiet = 0;
		} else if (g_trace) {
			g_backFlipsQuiet++;
		}
	}
	if (!g_trace || !player || !Accessible(player + OFF_REFR_POS, 12, false))
		return;
	float z = ((const float *)(player + OFF_REFR_POS))[2];
	if (!isfinite(z))
		return;
	if (g_hgtHave && now - g_hgtAt < 0.001) {
		g_hgtPendDz += dz;   /* a second step this frame (a turn that wasn't clear, then straight back) */
		return;
	}
	float vel = 0.0f;
	bool hasVel = false;
	GetVecFn get = (GetVecFn)CtrlFunc(ctrl, VF_CTRL_GET_VELOCITY);
	if (get) {
		__attribute__((aligned(16))) float v[8] = { 0 };
		get(ctrl, v);
		vel = v[2] / g_havok;
		hasVel = isfinite(vel) && fabsf(vel) < 100000.0f;
	}
	if (!g_hgtHave) {
		g_hgtHave = true;
		g_hgtVzHave = false;
		g_hgtLineZ = z;
		g_hgtOurs = g_hgtDvMax = 0.0f;
		g_hgtCalls = g_hgtSup = g_hgtVels = 0;
	} else {
		/* The step before this one is in z now: into the line's sums. */
		float vz = (z - g_hgtZ) / (float)(now - g_hgtAt);
		if (g_hgtVzHave && fabsf(vz - g_hgtVz) > g_hgtDvMax)
			g_hgtDvMax = fabsf(vz - g_hgtVz);
		g_hgtVz = vz;
		g_hgtVzHave = true;
		g_hgtOurs += g_hgtPendDz;
		g_hgtCalls++;
		g_hgtSup += g_hgtPendSup;
		if (g_hgtPendHasVel) {
			if (!g_hgtVels || g_hgtPendVel < g_hgtVelMin)
				g_hgtVelMin = g_hgtPendVel;
			if (!g_hgtVels || g_hgtPendVel > g_hgtVelMax)
				g_hgtVelMax = g_hgtPendVel;
			g_hgtVels++;
		}
	}
	g_hgtZ = z;
	g_hgtAt = now;
	g_hgtPendDz = dz;
	g_hgtPendSup = sup;
	g_hgtPendVel = vel;
	g_hgtPendHasVel = hasVel;
}

/* The trace's height line, then the next line's sums start from the step being made. */
static void LogBackHeight(void)
{
	if (!g_hgtHave || g_hgtCalls <= 0)
		return;
	float dzAll = g_hgtZ - g_hgtLineZ;
	char vel[64];
	if (g_hgtVels)
		snprintf(vel, sizeof(vel), "the controller's velocity z %+.0f..%+.0f", g_hgtVelMin, g_hgtVelMax);
	else
		snprintf(vel, sizeof(vel), "the controller's velocity not read");
	Log("  height: z %+.1f (ours %+.1f over %d calls, the game's %+.1f); a call's vertical speed changed %.0f at most; supported %d of %d calls; %s",
	    dzAll, g_hgtOurs, g_hgtCalls, dzAll - g_hgtOurs, g_hgtDvMax, g_hgtSup, g_hgtCalls, vel);
	g_hgtLineZ = g_hgtZ;
	g_hgtOurs = g_hgtDvMax = 0.0f;
	g_hgtCalls = g_hgtSup = g_hgtVels = 0;
}

/* The step's dz going back level or down (dz holds the slope 55 back's on the way in): the window's
 * follow and, unsupported, the closing (BackFollow=0: test 40's rule, worked out by the caller,
 * only looked at here). feet: the ray under the step found the ground, `below` under the feet. */
static void BackFollowStep(uintptr_t cell, const float *pos, const float dir[2], float step, float groundNear, bool feet, float below, uintptr_t ctrl, float *dz)
{
	bool sup = ControllerSupported(ctrl);
	float dt = g_backSpeed > 0.0f ? step / g_backSpeed : 0.0f, follow, closing = 0.0f;
	if (g_backFollow <= 0.0f) {
		g_backKind = BACK_OLD;
		bool replaced = feet && !sup;
		follow = replaced ? 0.0f : *dz;
		closing = replaced ? -*dz : 0.0f;
	} else {
		float half = 0.5f * g_backFollow, g[2];
		bool hit = true;
		/* Centred on the step's middle, not its end: the follow then sums like the midpoint rule,
		 * the feet within 0.50 of the brow and dip's ground in a model of N1 against 0.58 (the
		 * corner cut itself is 0.50), and a long frame's step on the harness's ripple off by half
		 * as much (a model with 2% of the steps 1 to 3 long: the drift over 240 units 0.15 against
		 * 0.34 at the median). */
		for (int i = 0; i < 2; i++) {   /* 0: ahead of the step's middle (toward the bike's nose), 1: behind it */
			float d = 0.5f * step + (i ? half : -half);
			float a[3] = { pos[0] + dir[0] * d, pos[1] + dir[1] * d, pos[2] + 8.0f };
			float b[3] = { a[0], a[1], pos[2] - 52.0f };
			float f = CastRayGround(cell, a, b);
			g[i] = 8.0f - f * 60.0f;
			hit = hit && f < 1.0f;
		}
		g_backAhead = g[0];
		g_backBehind = g[1];
		float sl;
		if (hit) {
			sl = (g[1] - g[0]) / g_backFollow;
			g_backS = sl;
			g_backSAt = g_clock;
			g_backSHave = true;
			g_backKind = BACK_WINDOW;
		} else if (g_backSHave && g_clock - g_backSAt <= BACK_HOLD) {
			sl = g_backS;
			g_backKind = BACK_HELD;
		} else {
			sl = groundNear / 55.0f;
			g_backKind = BACK_SLOPE55;
		}
		if (g_backKind != BACK_SLOPE55 && (sl < -BACK_EDGE_DOWN || sl > BACK_EDGE_UP)) {
			g_backKind = BACK_EDGE;
			follow = 0.0f;
		} else {
			follow = sl * step;
		}
	}
	if (feet) {
		float after = below + follow;   /* the gap once this step's follow is made */
		if (!g_backOwnSet) {
			g_backOwn = sup ? after : BACK_HOVER;
			g_backOwnSet = true;
		} else if (sup && dt > 0.0f) {
			g_backOwn += (after - g_backOwn) * (1.0f - expf(-dt / BACK_OWN_TAU));
		}
		if (g_backFollow > 0.0f && !sup) {
			float excess = after - ((g_backOwn > BACK_HOVER ? g_backOwn : BACK_HOVER) - g_backSink);
			if (excess > 0.0f) {
				closing = g_backClose > 0.0f ? excess * (1.0f - expf(-dt / g_backClose)) : excess;
				if (closing > BACK_CLOSE_SPEED * dt)
					closing = BACK_CLOSE_SPEED * dt;
				if (closing > 3.0f)
					closing = 3.0f;
			}
		}
	}
	if (g_backFollow > 0.0f)
		*dz = follow - closing;   /* never up for the closing */
	g_backFollowDz = follow;
	g_backClosing = closing;
}

/* Is the way back clear for a step of `step` units along `heading`? The ground is found 55
 * units behind the rider (clear of their own body) and under the rear (BackClearance): there
 * must be some, and the rays at knee height on either side of the bike (20 units out) and at
 * chest height in the middle follow it between (so a slope behind isn't taken for a wall). The
 * feet go to the ground under the step, near the slope's (dz). Not while the bike is in the air
 * (test 16: steps down a steep slope left it unsupported for seconds): it lands first. Else why
 * not (logged once a second, with what the ray hit, its layer and where). The ground rays pass
 * through actors (CastRayGround), the knee and chest rays don't: Dogmeat behind stops it. */
static bool WayBackClear(uintptr_t player, uintptr_t ctrl, float heading, float step, float *dz)
{
	uintptr_t cell = ReadPtr(player + OFF_REFR_CELL);
	if (!cell || !IsA(cell, RTTI_CELL))
		return false;
	g_riderRoot = Root3D(player);   /* the step runs from the movement hook, maybe before this frame's SampleGround */
	const float *pos = (const float *)(player + OFF_REFR_POS);
	float dir[2] = { -sinf(heading), -cosf(heading) }, right[2] = { cosf(heading), -sinf(heading) };
	const char *why = NULL;
	bool hit = false;
	float at = 0.0f, behindNear = 55.0f, behindFar = g_backClearance, groundNear = 0.0f, groundFar = 0.0f;
	g_rayGrounded = false;
	g_rayFeetGap = -99.0f;
	g_backKind = BACK_NONE;
	{
		float a[3] = { pos[0] + dir[0] * behindNear, pos[1] + dir[1] * behindNear, pos[2] + 60.0f };
		float b[3] = { a[0], a[1], pos[2] - 60.0f };
		float f = CastRayGround(cell, a, b);
		if (f >= 1.0f) {
			why = "no ground just behind";
			at = behindNear;
		}
		groundNear = 60.0f - f * 120.0f;
		if (!why && fabsf(groundNear) > behindNear) {
			why = "too steep just behind";
			at = behindNear;
			hit = true;
		}
	}
	if (!why) {
		float a[3] = { pos[0] + dir[0] * behindFar, pos[1] + dir[1] * behindFar, pos[2] + behindFar * 0.7f };
		float b[3] = { a[0], a[1], pos[2] - behindFar * 1.2f };
		float f = CastRayGround(cell, a, b);
		if (f >= 1.0f) {
			why = "no ground under the rear (a drop)";
			at = behindFar;
		}
		groundFar = behindFar * 0.7f - f * behindFar * 1.9f;
	}
	static const float side[3] = { -20.0f, 20.0f, 0.0f }, height[3] = { 30.0f, 30.0f, 80.0f };
	for (int i = 0; i < 3 && !why; i++) {
		float len = behindFar + step;
		float a[3] = { pos[0] + dir[0] * behindNear + right[0] * side[i], pos[1] + dir[1] * behindNear + right[1] * side[i],
		               pos[2] + groundNear + height[i] };
		float b[3] = { pos[0] + dir[0] * len + right[0] * side[i], pos[1] + dir[1] * len + right[1] * side[i],
		               pos[2] + groundNear + (groundFar - groundNear) * (len - behindNear) / (behindFar - behindNear) + height[i] };
		float f = CastRay(cell, a, b);
		if (f < 1.0f) {
			why = i == 2 ? "something behind (chest height)" : i == 0 ? "something behind (knee height, left)"
			    : "something behind (knee height, right)";
			at = behindNear + f * (len - behindNear);
			hit = true;
		}
	}
	float slope = groundNear / behindNear * step;
	*dz = slope;   /* up or down a slope: with it */
	/* Test 41: with BackFollow on, the ground 55 behind less than BACK_LEVEL above the feet is
	 * level, not uphill (in the harness's ripple, 0.5 over 4 units on level ground, the slope 55
	 * back went up and down, the steps taking it when uphill and the window when not, and the
	 * feet climbed 0.58 in 3 s: the uphill steps only ever added). */
	bool uphill = slope > 0.0f && (g_backFollow <= 0.0f || groundNear > BACK_LEVEL);
	if (!why && uphill) {
		g_rayGrounded = true;   /* uphill the feet never float */
		g_backKind = BACK_UP;
	}
	if (!why && !uphill) {
		/* Level or going down: the ground under the step, from 2 units above the feet (the
		 * capsule's bottom is a hemisphere, so at the step point its skin is about at the feet;
		 * if the ray starts inside it anyway and the player's filter reports that, the hit is
		 * at the start and goes unused, as does the ground at the feet). A gap under the feet
		 * is closed while the controller doesn't hold itself supported: they go down to a
		 * hover of BACK_HOVER over the ground (BackSink further), at most 3 units a frame (test
		 * 16: the least time in the air; test 18: 1.5 units into it, the most, the controller
		 * losing its support). More than 20 down is a drop: no step. Not uphill: there the ray
		 * would start inside a curb or the slope (a box ignored from inside, the ray finds the
		 * ground beneath), and the feet never float. */
		/* Test 39, on a level road (01:38:27-54, 01:39:27-42): all 15 gaps closed there (+0.4
		 * to +2.4, the step's dz -0.4 to -2.44) came with the controller holding itself supported
		 * (state 0, the supported bit set), and each was followed by the controller in the air
		 * within 0.01 to 0.75 s, the player's z dropping 20 to 37 through the road's collision
		 * (the wheels' rays then found the ground 17 to 21 above the contact) and climbing back
		 * over about 0.8 s; backing with no step the gaps read 0.0 to 0.2, the controller's own
		 * hover. So a supported controller's gap is its own (the slope's dz stands), and an
		 * unsupported one's feet go to the hover, not onto the ground: the feet ray's ground
		 * plus BACK_HOVER, less BackSink, never up (the trace's rays line shows the gap and the
		 * step's dz either way). */
		/* Test 41: with BackFollow over 0 the step follows the window's slope instead, and the
		 * closing stops at the controller's own clearance (BackFollowStep, above). */
		float a[3] = { pos[0] + dir[0] * step, pos[1] + dir[1] * step, pos[2] + 2.0f };
		float b[3] = { a[0], a[1], pos[2] - 38.0f };
		float f = CastRayGround(cell, a, b), below = 0.0f;
		bool feet = false;
		if (f < 1.0f) {
			below = f * 40.0f - 2.0f;
			g_rayFeetGap = below;
			if (below > 20.0f) {
				why = "the ground drops away under the step";
				at = step;
			} else {
				g_rayGrounded = below > -1.5f && below < 4.0f;   /* -2: the capsule itself, no telling */
				feet = true;
				if (g_backFollow <= 0.0f && !ControllerSupported(ctrl)) {
					float down = below - BACK_HOVER + g_backSink;
					*dz = -(down < 0.0f ? 0.0f : down < 3.0f ? down : 3.0f);
				}
			}
		}
		if (!why)
			BackFollowStep(cell, pos, dir, step, groundNear, feet, below, ctrl, dz);
	}
	if (g_rayGrounded) {
		/* The ground's normal by the rays: the slope behind, level across. */
		float g = groundNear / behindNear, norm = sqrtf(g * g + 1.0f);
		g_rayNormal[0] = -dir[0] * g / norm;
		g_rayNormal[1] = -dir[1] * g / norm;
		g_rayNormal[2] = 1.0f / norm;
	}
	g_rayDz = *dz;
	g_rayGroundNear = groundNear;
	g_rayGroundFar = groundFar;
	if (why) {
		if (hit)
			snprintf(g_wayWhy, sizeof(g_wayWhy), "%s, %.0f units back (%s, layer %u, at %+.0f, %+.0f, %+.0f from the player)", why,
			         at, g_rayWhat && *g_rayWhat ? g_rayWhat : "unnamed", g_rayLayer, g_rayHit[0] - pos[0], g_rayHit[1] - pos[1],
			         g_rayHit[2] - pos[2]);
		else
			snprintf(g_wayWhy, sizeof(g_wayWhy), "%s, %.0f units back", why, at);
		if (!g_wayQuiet && g_clock - g_blockedLogged >= 1.0f) {
			g_blockedLogged = g_clock;
			Log("reverse: stopped: %s", g_wayWhy);
		}
	}
	return !why;
}

/* Undo what the method in use leaves behind (on letting go of back, or getting off). */
static void StopPush(void)
{
	uintptr_t ctrl = g_pushCtrl;
	g_backFresh = true;   /* the next step starts a push afresh (the window, the controller's own clearance) */
	g_pushCtrl = 0;
	g_pushOn = g_pushClock = false;
	g_pushHeld = 0.0f;
	if (!ctrl || !IsA(ctrl, RTTI_CONTROLLER))
		return;
	if (g_pushMethod == PUSH_DELTA && Accessible(ctrl + OFF_CTRL_PUSH_DELTA, 16, true)) {
		memset((void *)(ctrl + OFF_CTRL_PUSH_DELTA), 0, 16);
	} else if (g_pushMethod == PUSH_MOD && Accessible(ctrl + OFF_CTRL_VELOCITY_MOD, 16, true) &&
	    Accessible(ctrl + OFF_CTRL_VELOCITY_TIME, 4, true)) {
		memcpy((void *)(ctrl + OFF_CTRL_VELOCITY_MOD), g_savedMod, sizeof(g_savedMod));
		*(float *)(ctrl + OFF_CTRL_VELOCITY_TIME) = g_savedModTime;
	} else if (g_pushMethod == PUSH_VELOCITY) {
		GetVecFn get = (GetVecFn)CtrlFunc(ctrl, VF_CTRL_GET_VELOCITY);
		SetVecFn set = (SetVecFn)CtrlFunc(ctrl, VF_CTRL_SET_VELOCITY);
		__attribute__((aligned(16))) float v[8] = { 0 };
		if (get && set) {
			get(ctrl, v);
			if (isfinite(v[2])) {
				v[0] = v[1] = 0.0f;   /* no sliding on after letting go */
				set(ctrl, v);
			}
		}
	}
}

static bool PushStep(uintptr_t player, uintptr_t ctrl, float heading, float dt)
{
	float dir[2] = { -sinf(heading), -cosf(heading) };
	float v = g_backSpeed * g_havok;
	g_pushBlocked = false;
	switch (g_pushMethod) {
	case PUSH_DELTA: {
		float *d = (float *)(ctrl + OFF_CTRL_PUSH_DELTA);
		if (!Accessible((uintptr_t)d, 16, true))
			return false;
		if (g_pushCtrl != ctrl) {
			bool plausible = true;
			for (int i = 0; i < 4; i++)
				plausible = plausible && isfinite(d[i]) && fabsf(d[i]) < 1000.0f;
			if (!plausible) {
				Log("reverse: pushDelta (%g, %g, %g) doesn't look like a step", d[0], d[1], d[2]);
				return false;
			}
		}
		float step = HAVOK_SCALE * g_backSpeed * (dt < 0.05f ? dt : 0.05f);   /* Havok's units, as velocityMod */
		d[0] = dir[0] * step;
		d[1] = dir[1] * step;
		d[2] = d[3] = 0.0f;
		return true;
	}
	case PUSH_MOD: {
		float *mod = (float *)(ctrl + OFF_CTRL_VELOCITY_MOD), *t = (float *)(ctrl + OFF_CTRL_VELOCITY_TIME);
		if (!Accessible((uintptr_t)mod, 16, true) || !Accessible((uintptr_t)t, 4, true))
			return false;
		if (g_pushCtrl != ctrl) {
			bool plausible = isfinite(*t) && *t >= 0.0f && *t < 100.0f;
			for (int i = 0; i < 4; i++)
				plausible = plausible && isfinite(mod[i]) && fabsf(mod[i]) < 1000.0f;
			if (!plausible) {
				Log("reverse: velocityMod (%g, %g, %g) / velocityTime %g don't look like a velocity and a time", mod[0], mod[1],
				    mod[2], *t);
				return false;
			}
			memcpy(g_savedMod, mod, sizeof(g_savedMod));
			g_savedModTime = *t;
		}
		mod[0] = dir[0] * v;
		mod[1] = dir[1] * v;
		mod[2] = 0.0f;
		mod[3] = 0.0f;
		*t = 0.1f;
		return true;
	}
	case PUSH_VELOCITY: {
		GetVecFn get = (GetVecFn)CtrlFunc(ctrl, VF_CTRL_GET_VELOCITY);
		SetVecFn set = (SetVecFn)CtrlFunc(ctrl, VF_CTRL_SET_VELOCITY);
		__attribute__((aligned(16))) float vel[8] = { 0 };
		if (!get || !set)
			return false;
		get(ctrl, vel);
		if (!isfinite(vel[0]) || !isfinite(vel[1]) || !isfinite(vel[2]) || fabsf(vel[2]) > 1000.0f)
			return false;
		vel[0] = dir[0] * v;
		vel[1] = dir[1] * v;
		set(ctrl, vel);
		return true;
	}
	case PUSH_POSITION:
	case PUSH_RAYSTEP: {
		GetPosFn get = (GetPosFn)CtrlFunc(ctrl, VF_CTRL_GET_POSITION);
		SetPosFn set = (SetPosFn)CtrlFunc(ctrl, VF_CTRL_SET_POSITION);
		__attribute__((aligned(16))) float p[16] = { 0 };
		if (!get || !set || (g_pushMethod == PUSH_RAYSTEP && !FindPickFunctions()))
			return false;
		float stepGame = g_backSpeed * (dt < 0.05f ? dt : 0.05f), dz = 0.0f;   /* a few units a frame at most */
		if (g_pushMethod == PUSH_RAYSTEP && g_backFresh)
			BackPushStart(ctrl);
		if (g_pushMethod == PUSH_RAYSTEP && (!RaysReady(player) || !WayBackClear(player, ctrl, heading, stepGame, &dz))) {
			g_pushBlocked = true;
			BackStepDone(player, ctrl, 0.0f);
			return true;   /* stopped, not failed */
		}
		get(ctrl, p, false);
		if (!isfinite(p[0]) || !isfinite(p[1]) || !isfinite(p[2]))
			return false;
		p[0] += dir[0] * stepGame * g_havok;
		p[1] += dir[1] * stepGame * g_havok;
		p[2] += dz * g_havok;
		set(ctrl, p, false, false);   /* the third argument is ignored (test 19) */
		if (g_backSupportCheck) {
			void (*check)(uintptr_t) = (void (*)(uintptr_t))CtrlFunc(ctrl, VF_CTRL_CHECK_SUPPORT);
			if (check)
				check(ctrl);
		}
		if (g_pushMethod == PUSH_RAYSTEP)
			BackStepDone(player, ctrl, dz);
		return true;
	}
	default:
		return true;   /* brake: nothing */
	}
}

static void NextPush(const char *why)
{
	int next = PUSH_BRAKE;
	Log("reverse: %s %s: trying %s", g_pushNames[g_pushMethod], why, g_pushNames[next]);
	g_pushMethod = next;
}

/* Every frame while back is held: back the bike up, turning at `turn` radians a second (the
 * side key) if it can. Returns the heading it backed up along (the same if it didn't turn). */
static float PushBack(uintptr_t player, float heading, float turn, float dt)
{
	uintptr_t ctrl = FindController(player, false);
	if (g_pushMethod < 0)
		g_pushMethod = g_backPushFirst;
	/* A failed trial isn't for good (test 20: the first back press came at 900 units a second
	 * with a side key held, the trial saw the bike still rolling and called the method
	 * wrong, and reverse was dead for the session): from a stop, 3 s later, it's tried again. */
	if (g_pushMethod == PUSH_BRAKE && g_backPushAuto && !g_pushProven && g_pushRetryAt > 0.0f && g_clock >= g_pushRetryAt &&
	    g_speed < 20.0f && turn == 0.0f) {
		g_pushRetryAt = 0.0f;
		g_pushMethod = g_backPushFirst;
		StopPush();
		Log("reverse: trying %s again, from a stop this time", g_pushNames[g_pushMethod]);
	}
	if (!ctrl || g_pushMethod == PUSH_BRAKE)
		return heading;   /* braking: no turning either */
	if (g_pushCtrl && g_pushCtrl != ctrl)
		g_pushCtrl = 0;   /* a new controller (a load): nothing to undo on the old one */
	if (g_pushMethod != PUSH_MOD && g_pushMethod != PUSH_DELTA && !CheckControllerFuncs(ctrl, (const float *)(player + OFF_REFR_POS), "reverse")) {
		g_pushMethod = PUSH_BRAKE;
		Log("reverse: back brakes (the controller's functions can't be used)");
		return heading;
	}
	float used = heading;
	bool ok;
	if (g_pushMethod == PUSH_RAYSTEP) {
		/* The turn first; if that way isn't clear, straight back; else neither. */
		float turned = heading + turn * dt;
		g_wayQuiet = turn != 0.0f;
		ok = PushStep(player, ctrl, turned, dt);
		g_wayQuiet = false;
		if (ok && !g_pushBlocked) {
			used = turned;
		} else if (ok && turn != 0.0f) {
			char turnWhy[200];
			snprintf(turnWhy, sizeof(turnWhy), "%s", g_wayWhy);
			ok = PushStep(player, ctrl, heading, dt);
			if (ok && !g_pushBlocked && g_clock - g_blockedLogged >= 1.0f) {
				g_blockedLogged = g_clock;
				Log("reverse: not turning (that way: %s); backing up straight", turnWhy);
			}
		}
	} else {
		/* The others turn with how fast the bike really goes back. */
		float back = g_speedAlong < 0.0f ? -g_speedAlong / g_backSpeed : 0.0f;
		used = heading + turn * dt * (back > 1.0f ? 1.0f : back);
		ok = PushStep(player, ctrl, used, dt);
	}
	if (!ok) {
		StopPush();
		if (g_backPushAuto) {
			NextPush("can't be used");
		} else {
			Log("reverse: %s can't be used: back brakes", g_pushNames[g_pushMethod]);
			g_pushMethod = PUSH_BRAKE;
		}
		return heading;
	}
	g_pushCtrl = ctrl;
	g_pushOn = true;
	if (!g_pushClock && g_speed < 20.0f && turn == 0.0f)
		g_pushClock = true;   /* the trial starts once the bike is at rest, no side key */
	if (!g_pushClock || g_pushBlocked || turn != 0.0f)
		return used;   /* stopped by something behind, or swinging round: says nothing about the method */
	g_pushHeld += dt;
	if (g_pushProven)
		return used;
	const char *wrong = g_pushHeld < 0.25f ? NULL : g_speedAlong > 20.0f ? "moved the bike forward"
	                  : g_speed > 40.0f && fabsf(g_speedAlong) < 0.5f * g_speed ? "moved the bike sideways" : NULL;
	if (!wrong && g_pushHeld < 0.6f)
		return used;
	if (!wrong && g_speedAlong < -0.3f * g_backSpeed) {
		g_pushProven = true;
		Log("reverse: %s moves the bike back (%+.0f along the heading): kept", g_pushNames[g_pushMethod], g_speedAlong);
	} else if (g_backPushAuto) {
		char why[112];
		snprintf(why, sizeof(why), "%s (%+.0f along the heading, %.0f a second in all, after %.2f s)",
		         wrong ? wrong : "didn't move the bike back", g_speedAlong, g_speed, g_pushHeld);
		StopPush();
		NextPush(why);
		g_pushRetryAt = g_clock + 3.0f;
	} else {
		g_pushHeld = -1000.0f;   /* a fixed method: logged once, kept anyway */
		Log("reverse: %s didn't move the bike back (%+.0f along the heading after 0.6 s); kept (BackPush names it)",
		    g_pushNames[g_pushMethod], g_speedAlong);
	}
	return used;
}

/* The creep's forward input, learnt: up when slower than wanted, down when faster, at 1.5/s.
 * Rough ground takes much more than the flat and is threshold-like (test 17: nothing at 0.53,
 * 58 units/s at 0.62 on a rock; 0.10 on the flat), so the input may wind up; stuck against
 * something it winds up too (there's no telling that from rough ground), and once free the
 * bike surged (test 17: 3.4 s at up to 336 units/s while the input decayed from 0.90). So
 * when the bike goes faster than twice the speed wanted, the input is cut to the last value
 * that crept at about that speed (the ground it was stuck on, as a rule) or to what the speed
 * says (input x wanted / speed), whichever is less but not below half the good value, and
 * again 0.12 s later if it's still too fast (the speed estimate lags the cut): the surge
 * lasts a fraction of a second. The good
 * value is only learnt while the speed is steady (the quick and the slow estimates agree), so
 * a surge passing through the right speed doesn't poison it. */
static void AdaptCreep(float want)
{
	g_creepWant = want;
	if (want < 1.0f || g_frameDt <= 0.0f)
		return;
	if (g_speedAlongFast > 2.0f * want && g_clock >= g_creepCutAt && !g_groundAir &&
	    !(g_speedAlongFast < 0.7f * g_creepCutSpeed)) {
		/* Not in the air (a fall isn't the input's doing), and not while the speed is still
		 * falling from the last cut (test 18: a second cut on the lagging estimate, 0.07 to
		 * 0.02). Wound up past a good value, the cut stays between half that value and it
		 * (the quick estimate spikes as the bike pops free: test 18 cut to 0.05, a second of
		 * crawling at half speed); started at a good value that's wrong for this ground (the
		 * rock's on the flat), the speed's own word goes. Never up. */
		float cut = g_creepInput * want / g_speedAlongFast;
		if (g_creepInput > 1.2f * g_creepGood) {
			if (cut > g_creepGood)
				cut = g_creepGood;
			if (cut < 0.5f * g_creepGood)
				cut = 0.5f * g_creepGood;
		}
		if (cut < g_creepInput)
			g_creepInput = cut;
		g_creepCutAt = g_clock + 0.12f;
		g_creepCutSpeed = g_speedAlongFast;
	} else {
		float e = (want - g_speedAlongFast) / want;
		e = e > 1.0f ? 1.0f : e < -1.0f ? -1.0f : e;
		g_creepInput *= expf(1.5f * e * g_frameDt);
	}
	g_creepInput = g_creepInput < 0.02f ? 0.02f : g_creepInput > 1.0f ? 1.0f : g_creepInput;
	bool steady = fabsf(g_speedAlongFast - g_speedAlong) < 0.2f * want;
	if (steady && fabsf(g_speedAlong - want) < 0.3f * want)
		g_creepGood = g_creepInput;
}

/* ------------------------------------------------------------------------- */
/* Steering: no turning on the spot, a turning circle while moving           */
/* ------------------------------------------------------------------------- */

/* Every frame while riding: the game turns the player towards where the camera and the
 * movement keys point; a bike can't, so the heading may change at most speed / radius
 * (radians a second), or CMB_StandTurnRate when that's faster. Whatever the game turned
 * beyond that this frame is dropped; next frame it asks again from where we left it. With
 * the input hook: backing up or creeping round from a stop, the plugin alone turns it. */
static void FrameSteer(void)
{
	float radiusFast = GlobalValue(g_turnRadiusGlobal);
	uintptr_t player = Player();
	if (!g_steer || !g_riding || !(radiusFast > 0.0f) || !player || !Accessible(player + OFF_REFR_HEADING, 4, true) ||
	    !Accessible(player + OFF_REFR_POS, 12, false)) {
		g_steerHave = false;
		g_rayGrounded = false;
		EndInput();
		return;
	}
	InstallInputHook();
	g_inputActive = g_inputHooked;
	g_rayGrounded = false;
	float *h = (float *)(player + OFF_REFR_HEADING);
	const float *pos = (const float *)(player + OFF_REFR_POS);
	if (!isfinite(*h))
		return;
	if (g_steerHave) {
		float dx = pos[0] - g_steerPos[0], dy = pos[1] - g_steerPos[1], d = sqrtf(dx * dx + dy * dy);
		if (d > 300.0f) {
			g_steerHave = false;   /* a door, fast travel: start again from the game's heading */
		} else if (g_frameDt > 0.0f) {
			float k = 1.0f - expf(-g_frameDt / 0.2f);
			g_speed += (d / g_frameDt - g_speed) * k;
			/* Signed: forward along the heading, or backward (a reverse). */
			float along = (dx * sinf(g_steerHeading) + dy * cosf(g_steerHeading)) / g_frameDt;
			g_speedAlong += (along - g_speedAlong) * k;
			g_speedAlongFast += (along - g_speedAlongFast) * (1.0f - expf(-g_frameDt / 0.05f));
		}
	}
	memcpy(g_steerPos, pos, sizeof(g_steerPos));
	if (!g_steerHave) {
		g_steerHeading = *h;
		g_steerHave = true;
		g_speed = g_speedAlong = g_speedAlongFast = g_yawEased = 0.0f;
		return;
	}

	int mode = g_inputHooked ? g_inputMode : INPUT_PASS;
	if (mode != INPUT_CREEP) {
		/* Off the side key: the next creep starts from the last good value (not a wound-up or a
		 * cut one: test 18 started one at 0.02, 1.5 s before it moved), and that value eases
		 * back to CreepInput over about 15 s (rough ground's is that spot's; on the flat it would
		 * surge). */
		g_creepGood += (g_creepStart - g_creepGood) * (1.0f - expf(-g_frameDt / 15.0f));
		g_creepInput = g_creepGood;
		g_creepCutSpeed = 0.0f;
	}
	float inX = g_keys[0] > 1.0f ? 1.0f : g_keys[0] < -1.0f ? -1.0f : g_keys[0];
	if (!isfinite(inX))
		inX = 0.0f;
	if (mode != INPUT_BACK && (g_pushOn || g_pushCtrl))
		StopPush();

	/* The tightest turn grows with speed: walking pace turns tight, riding speed wide. */
	float radiusSlow = GlobalValue(g_turnSlowGlobal);
	if (!(radiusSlow > 0.0f) || radiusSlow > radiusFast)
		radiusSlow = radiusFast;
	float f = g_fullSpeed > 0.0f ? g_speed / g_fullSpeed : 1.0f;
	float radius = radiusSlow + (radiusFast - radiusSlow) * (f < 0.0f ? 0.0f : f > 1.0f ? 1.0f : f);
	const float twoPi = 6.2831853f;
	float wanted = remainderf(*h - g_steerHeading, twoPi);
	float rate = g_speed / radius, stand = GlobalValue(g_turnStandGlobal) / 57.29578f;
	if (!(stand >= 0.0f))
		stand = 0.0f;
	if (rate < stand)
		rate = stand;
	if (g_frameDt > 0.0f && fabsf(wanted) / g_frameDt * 57.29578f > g_steerWanted)
		g_steerWanted = fabsf(wanted) / g_frameDt * 57.29578f;
	g_steerAllowed = rate * 57.29578f;
	g_steerRadius = radius;
	if (mode == INPUT_BACK) {
		/* Backing up, the rear goes the way the side key says (the nose swings the other
		 * way, as a car reverses), round the walking-pace circle as it moves back, at most at
		 * the stopped rate. Only as it moves back: braking, or stopped by something, it holds. */
		float turn = g_backSpeed / radiusSlow;
		if (turn > stand)
			turn = stand;
		float used = PushBack(player, g_steerHeading, -inX * turn, g_frameDt);
		*h = fmodf(used + twoPi, twoPi);
		g_steerAllowed = turn * 57.29578f;
		if (fabsf(wanted) > 0.0001f)
			g_steerClamped++;
	} else if (mode == INPUT_CREEP) {
		/* A side key from a stop: turned at the stopped rate, crawling forward just fast
		 * enough to go round a CreepRadius circle (Creep=0: on the spot). */
		*h = fmodf(g_steerHeading + inX * stand * g_frameDt + twoPi, twoPi);
		g_steerAllowed = stand * 57.29578f;
		if (fabsf(wanted) > 0.0001f)
			g_steerClamped++;
		if (g_creep)
			AdaptCreep(fabsf(inX) * stand * g_creepRadius);
	} else {
		/* The turning rate the game asks (a key: the whole clamp at once; the mouse: a little
		 * each frame) eases in over TurnEase (test 33: A/D made a snake), never beyond the
		 * clamp, and the heading never overshoots what was asked. */
		float wantRate = g_frameDt > 0.0f ? wanted / g_frameDt : 0.0f;
		wantRate = wantRate > rate ? rate : wantRate < -rate ? -rate : wantRate;
		/* In over TurnEaseIn while the rate asked grows the same way, out over TurnEaseOut
		 * when the key is let go or reversed (test 34: one time constant felt heavy). */
		bool growing = fabsf(wantRate) > fabsf(g_yawEased) && wantRate * g_yawEased >= 0.0f;
		float tau = growing ? g_turnEaseIn : g_turnEaseOut;
		if (tau > 0.0f && g_frameDt > 0.0f)
			g_yawEased += (wantRate - g_yawEased) * (1.0f - expf(-g_frameDt / tau));
		else
			g_yawEased = wantRate;
		float eased = g_yawEased * g_frameDt, delta = wanted;
		if (eased * wanted <= 0.0f)
			delta = 0.0f;   /* the eased rate still the other way (or none): no turn this frame */
		else if (fabsf(eased) < fabsf(wanted))
			delta = eased;
		if (fabsf(delta) < fabsf(wanted)) {
			*h = fmodf(g_steerHeading + delta + twoPi, twoPi);
			g_steerClamped++;
		}
	}
	g_steerHeading = *h;
}

/* With Trace=1: the player controls' first floats, whenever they change (test 11 found the
 * move input that way), and every 0.25 s while backing up or creeping, what the keys asked,
 * what the game got, what the movement used (prevMoveVec, +0x5C) and where the bike went. */
static void TraceControls(void)
{
	uintptr_t controls = ReadPtr(g_base + RVA_PLAYER_CONTROLS);
	if (!g_trace || !g_riding || !controls || !IsA(controls, RTTI_CONTROLS) || !Accessible(controls + 0x40, 80, false))
		return;
	const float *prev = (const float *)(controls + OFF_PREV_MOVE);
	bool output = false;
	if (g_inputMode != INPUT_PASS && g_clock - g_inputLogged >= 0.25f) {
		g_inputLogged = g_clock;
		output = true;
		char modes[48] = "";
		if (g_modeChanges || g_keysStuck)
			snprintf(modes, sizeof(modes), " [mode changed %d times%s]", g_modeChanges, g_keysStuck ? ", keys kept" : "");
		g_modeChanges = 0;
		if (g_inputMode == INPUT_BACK) {
			Log("reverse: keys (%.2f, %.2f), the game gets (%.2f, %.2f), the movement last used (%.2f, %.2f); pushing back by %s%s; "
			    "moving %+.0f along the heading%s",
			    g_keys[0], g_keys[1], g_wroteMove[0], g_wroteMove[1], prev[0], prev[1],
			    g_pushNames[g_pushMethod < 0 ? g_backPushFirst : g_pushMethod],
			    g_pushProven ? " (works)" : g_pushMethod == PUSH_BRAKE ? "" : " (on trial)", g_speedAlong, modes);
			if (g_pushMethod == PUSH_RAYSTEP) {
				uintptr_t c = g_pushCtrl;
				bool fields = c && Accessible(c + OFF_CTRL_FLAGS, 4, false) && Accessible(c + OFF_CTRL_SUPPORT_COUNT, 4, false) &&
				              Accessible(c + OFF_CTRL_IN_AIR_PRE_MOVE, 1, false);
				uint32_t flags = fields ? *(const uint32_t *)(c + OFF_CTRL_FLAGS) : 0u;
				/* The proxy's manifold size (+0x18) and +0x12C, next to the supported bit (0x400 of the
				 * flags, set by CheckSupportImpl from the manifold: test 19). */
				uintptr_t proxy = c ? FindProxy(c, false) : 0;
				bool pfields = proxy && Accessible(proxy + 0x18, 4, false) && Accessible(proxy + 0x12C, 4, false);
				/* Test 41: how the step's dz was had (finding 6). */
				char follow[200] = "", own[24];
				if (g_backOwnSet)
					snprintf(own, sizeof(own), "own %+.1f", g_backOwn);
				else
					snprintf(own, sizeof(own), "own not read yet");
				if (g_backKind == BACK_WINDOW)
					snprintf(follow, sizeof(follow), "; follow %+.2f by the window (the ground %+.1f ahead, %+.1f behind over %g), %s, closing %.2f", g_backFollowDz,
					         g_backAhead, g_backBehind, g_backFollow, own, g_backClosing);
				else if (g_backKind == BACK_HELD)
					snprintf(follow, sizeof(follow), "; follow %+.2f held (a window ray found no ground: its slope %.2f s ago), %s, closing %.2f", g_backFollowDz,
					         g_clock - g_backSAt, own, g_backClosing);
				else if (g_backKind == BACK_SLOPE55)
					snprintf(follow, sizeof(follow), "; follow %+.2f by the slope 55 back (a window ray found no ground for over %g s), %s, closing %.2f", g_backFollowDz,
					         BACK_HOLD, own, g_backClosing);
				else if (g_backKind == BACK_EDGE)
					snprintf(follow, sizeof(follow), "; follow +0.00: an edge (the ground %+.1f ahead, %+.1f behind over %g), %s, closing %.2f", g_backAhead, g_backBehind,
					         g_backFollow, own, g_backClosing);
				else if (g_backKind == BACK_UP)
					snprintf(follow, sizeof(follow), "; uphill: the slope 55 back");
				else if (g_backKind == BACK_OLD)
					snprintf(follow, sizeof(follow), "; the slope 55 back (BackFollow=0), %s, closing %.2f", own, g_backClosing);
				Log("  rays (filter %u): the ground %+.0f just behind, %+.0f under the rear, feet gap %+.1f, step dz %+.2f, "
				    "%s%s%s; controller: state %d, supported bit %d, support count %u, fake support %d, in air pre-move %d, "
				    "flags %08X; proxy +18 %u, +12C %08X (%g)",
				    g_rayFilter, g_rayGroundNear, g_rayGroundFar, g_rayFeetGap, g_rayDz,
				    g_rayGrounded ? "on the ground by the rays" : "not grounded by the rays", g_pushBlocked ? "; stopped" : "", follow,
				    g_lastState, (flags & 0x400u) != 0, fields ? *(const uint32_t *)(c + OFF_CTRL_SUPPORT_COUNT) : 0,
				    fields ? *(const uint8_t *)(c + OFF_CTRL_FAKE_SUPPORT) : 0, fields ? *(const uint8_t *)(c + OFF_CTRL_IN_AIR_PRE_MOVE) : 0,
				    flags, pfields ? *(const uint32_t *)(proxy + 0x18) : 0u, pfields ? *(const uint32_t *)(proxy + 0x12C) : 0u,
				    pfields ? *(const float *)(proxy + 0x12C) : 0.0f);
				LogBackHeight();
			}
		} else
			Log("creep: keys (%.2f, %.2f), the game gets (%.2f, %.2f), the movement last used (%.2f, %.2f); moving %+.0f along the "
			    "heading (want %.0f)%s",
			    g_keys[0], g_keys[1], g_wroteMove[0], g_wroteMove[1], prev[0], prev[1], g_speedAlong, g_creepWant, modes);
	}
	if (g_clock - g_controlsLogged >= 0.25f) {
		const float *f = (const float *)(controls + 0x40);
		bool changed = false;
		for (int i = 0; i < 20; i++)
			changed |= isfinite(f[i]) && fabsf(f[i] - g_controlsLast[i]) > 0.05f;
		if (changed) {
			char line[600];
			int len = 0;
			for (int i = 0; i < 20 && len < (int)sizeof(line) - 24; i++) {
				len += snprintf(line + len, sizeof(line) - len, " +%X=%.3g", 0x40 + 4 * i, f[i]);
				g_controlsLast[i] = f[i];
			}
			g_controlsLogged = g_clock;
			Log("controls:%s", line);
			output = true;
		}
	}
	if (output && g_outputHooked) {
		const float *o = g_output, *g = g_outputGame;
		Log("movement output: rotation (%.2f, %.2f, %.2f), rotation speed (%.2f, %.2f, %.2f), speed %.3f, target angle (%.2f, %.2f, "
		    "%.2f) [%d calls]%s",
		    o[0], o[1], o[2], o[4], o[5], o[6], o[8], o[12], o[13], o[14], g_outputCalls,
		    memcmp(o, g, sizeof(g_output)) == 0 ? "" : " (ours; the game's: speed, target angle, rotation speed below)");
		if (memcmp(o, g, sizeof(g_output)) != 0)
			Log("  the game's: speed %.3f, target angle %.2f, rotation speed %.2f", g[8], g[14], g[6]);
		g_outputCalls = 0;
	}
}

/* ------------------------------------------------------------------------- */
/* Every frame / every IntervalMs                                            */
/* ------------------------------------------------------------------------- */

static bool AnyGlobal(void)
{
	return g_slopeGlobal || g_cameraGlobal || g_tiltGlobal || g_groundGlobals[0];
}

/* text added to the list in why, after a comma (nothing for an empty text). */
static void AddReason(char *why, size_t size, const char *text)
{
	size_t used = strlen(why);
	if (text[0] && used + 3 < size)
		snprintf(why + used, size - used, "%s%s", used ? ", " : "", text);
}

/* Where the ground stands for the tilt this frame, and whether the rays are working (for the
 * load lines: test 40's lost lean, a filter held in the air would keep the bike level). */
static const char *GroundWord(void)
{
	static char word[96];
	snprintf(word, sizeof(word), "the ground %s, the rays %s", !g_groundOk ? "not read" : g_groundAir ? "away (in the air)" : "under it",
	         g_pickState > 0 ? (g_rayGrounded ? "working (on the ground)" : "working") : g_pickState < 0 ? "not trusted yet" : "not tried yet");
	return word;
}

/* The look at a ride a load started (finding 2 of test 40): what's held and what isn't, in one
 * line. At the first look (2.5 s in) a hold that hasn't resumed is let go and held afresh, as
 * getting off and on does, once a load: the bike's skins when one was refused (the refusals are
 * forgotten, so it's held again at the sync) or their bone can't be read, the rider's shapes when
 * they aren't held or their chains or lean were given up, with the latches that keep them from
 * being held (the block, the world check, the skeleton wait). Not the tilt (no ResetTilt): the
 * suspension, the lean's filter and the ride's start stay as they are. CMB_TiltLive at 0 with the
 * slope or the camera on is said too (test 40, the tester: the bars turned and the wheels spun,
 * the bike upright through the turns and the rider sitting up, which is what the plugin does with
 * the tilt at 0), but nothing of the plugin's can bring it back: the script sets it. The second
 * look (6 s in) is the log alone. */
static void LoadLook(float degrees, float camera, float tiltGlobal)
{
	bool act = g_loadLook == 0, tilt = tiltGlobal > 0.0f;
	g_loadLook++;
	char bike[200], rider[240], other[200], item[160];
	bike[0] = rider[0] = other[0] = 0;
	if ((tilt || g_partsOk) && !g_skinCount)
		AddReason(bike, sizeof(bike), "no bike skin held");
	if (g_skinsRefused) {
		snprintf(item, sizeof(item), "%d bike skin(s) refused (%d with no bone transforms to read yet)", g_skinsRefused, g_skinsUnbuilt);
		AddReason(bike, sizeof(bike), item);
	}
	if (g_skinCount && g_riderCount && !g_riderBikeOk)
		AddReason(bike, sizeof(bike), "the bike's bone unreadable");
	if (tilt && g_riderTilt && (g_riderSkinned || g_riderPlain) && !g_riderCount) {
		snprintf(item, sizeof(item), "no shape of the rider held%s%s%s", g_riderBlocked ? " (blocked)" : "",
		         g_riderWorldFailSince >= 0.0f || (g_riderWorldChecked && !g_riderWorldOk) ? " (the 3D root's world off)" : "",
		         g_holdWaitSince != 0.0f ? " (waiting for the skeleton)" : "");
		AddReason(rider, sizeof(rider), item);
	}
	if (g_holdWaitExpired)
		AddReason(rider, sizeof(rider), "the arms' chains incomplete");
	if (g_torsoNoChain)
		AddReason(rider, sizeof(rider), "the upper body's lean given up for want of an arm chain");
	if (!tilt && (degrees > 0.0f || camera > 0.0f))
		AddReason(other, sizeof(other), g_partsOk ? "the tilt off (CMB_TiltLive 0 with the slope or the camera on: the bike kept level, the rider not held, the moving parts running; the script's to set)"
		                                          : "the tilt off (CMB_TiltLive 0 with the slope or the camera on: nothing of the bike or the rider held; the script's to set)");
	char why[700];
	why[0] = 0;
	AddReason(why, sizeof(why), bike);
	AddReason(why, sizeof(why), rider);
	AddReason(why, sizeof(why), other);
	Log("load: %.1f s into the ride after the load: %d bike skin(s), %d rider shape(s) held, the rider %s, the upper body's lean %s%.1f deg%s; the tilt pitch %.1f roll %.1f (the lean %.1f at %.0f units/s), the globals slope %g, camera %g, tilt %g, %s%s%s",
	    act ? 2.5f : 6.0f, g_skinCount, g_riderCount, !g_riderCount ? "not held" : g_skinCount && g_riderApplied ? "written" : "not written",
	    g_torsoLeanSet ? "" : "not yet solved, ", g_torsoLean, g_torsoFinal ? ", final" : "", g_pitchNow, g_rollNow, g_leanNow, g_speed,
	    degrees, camera, tiltGlobal, GroundWord(), why[0] ? "; not resumed: " : ": resumed", why);
	if (!act || (!bike[0] && !rider[0]))
		return;
	Log("load: what didn't resume let go and held afresh, as getting off and on does (once a load):%s%s",
	    bike[0] ? " the bike's skins" : "", rider[0] ? (bike[0] ? " and the rider" : " the rider") : "");
	if (bike[0]) {
		if (g_skinCount && g_riderCount && !g_riderBikeOk)
			while (g_skinCount)
				LetGo(g_skinCount - 1, "held afresh after the load");
		memset(g_refused, 0, sizeof(g_refused));
		g_skinsRefused = g_skinsUnbuilt = 0;
	}
	if (rider[0]) {
		LetGoAllRider("held afresh after the load");
		g_riderBlocked = false;
		g_riderWorldChecked = false;
		g_riderWorldFailSince = -1.0f;
		g_riderBoneWarned = false;
		g_holdWaitSince = 0.0f;
		g_holdWaitExpired = false;
		g_torsoNoChain = false;
		memset(g_refused, 0, sizeof(g_refused));   /* a plain shape of the rider refused before is tried again too */
	}
}

/* CMB_TiltLive at 0 while riding (the slope or the camera on), said once a ride, and said again
 * if it comes back (test 40: after a load the bike stood upright through the turns and the
 * rider sat up while the bars turned and the wheels spun, which is what the plugin does with the
 * tilt at 0; the script sets the three together after a load, and getting on the camera about a
 * second before the other two, so the tilt alone at 0 is the MCM's tilt set to 0, or the script
 * not having set it). After 2 s of it in a ride a load started, 5 s in any other (a get-on's
 * second is no news). Log only. */
static void WatchTiltGlobal(bool riding, float degrees, float camera, float tilt)
{
	if (!riding) {
		g_tiltZeroSince = -1.0f;
		g_tiltZeroSaid = 0;
		return;
	}
	if (!(tilt > 0.0f)) {   /* a NaN too: the tilt treats it as off */
		if (g_tiltZeroSince < 0.0f)
			g_tiltZeroSince = (float)g_clock;
		else if (!g_tiltZeroSaid && (float)g_clock - g_tiltZeroSince >= (g_rideFromLoad ? 2.0f : 5.0f)) {
			g_tiltZeroSaid = 1;
			Log("tilt: riding with CMB_TiltLive at %g for %.1f s (the slope %g, the camera %g%s): the bike is kept level and the rider isn't held, %s; "
			    "the MCM's tilt at 0 does this, or the script didn't set it", tilt, (float)g_clock - g_tiltZeroSince, degrees, camera,
			    g_rideFromLoad ? ", a ride a load started" : "", g_partsOk ? "only the moving parts run" : "nothing of the bike is moved");
		}
		return;
	}
	if (g_tiltZeroSaid == 1) {
		g_tiltZeroSaid = 2;
		Log("tilt: CMB_TiltLive reads %g now, %.1f s after it was 0: the tilt and the rider's hold go on", tilt, (float)g_clock - g_tiltZeroSince);
	}
	g_tiltZeroSince = -1.0f;
}

static void Tick(DWORD now)
{
	if (!AnyGlobal()) {
		if (g_globalsMissingLogged || now - g_lastGlobalTry < 2000)
			return;
		g_lastGlobalTry = now;
		FindGlobals();
		if (!AnyGlobal())
			return;
	}
	UpdateCamera();
	UpdateZoom(now, GlobalValue(g_cameraGlobal) > 0.0f);

	float degrees = GlobalValue(g_slopeGlobal);
	float tilt = GlobalValue(g_tiltGlobal);
	bool riding = degrees > 0.0f || GlobalValue(g_cameraGlobal) > 0.0f || tilt > 0.0f;
	bool scan = (int32_t)(now - g_nextScan) >= 0;
	uintptr_t ctrl, proxy;
	uintptr_t target = FindChain(scan, &ctrl, &proxy);

	/* The first tick after a load (finding 2 of test 40): did the ride resume? */
	float camera = GlobalValue(g_cameraGlobal);
	if (g_loadPending) {
		g_loadPending = false;
		g_rideFromLoad = riding;
		g_loadLook = 0;
		if (riding)
			Log("load: the ride resumed %.2f s after the load (slope %g, camera %g, tilt %g; before it %g, %g, %g)", (float)g_clock - g_loadAt, degrees, camera, tilt,
			    g_tickSlope, g_tickCamera, g_tickTilt);
		else
			Log("load: not riding after the load");
	}
	if (!riding)
		g_rideFromLoad = false;
	if (riding && !g_wasRiding) {   /* a new ride: said afresh */
		g_tiltZeroSince = -1.0f;
		g_tiltZeroSaid = 0;
	}
	WatchTiltGlobal(riding, degrees, camera, tilt);
	g_tickSlope = degrees;
	g_tickCamera = camera;
	g_tickTilt = tilt;

	/* A new ride starts a new track. */
	if (riding && !g_wasRiding) {
		TrackClear();
		ResetTilt();   /* test 9: a ride that ended by taking the bike off kept the last pitch */
		RamReset();
		g_parkValid = false;
		g_parkPublishedAt = -100.0f;
	}
	if (!riding && g_wasRiding) {
		ClimbOff("the ride's end");   /* RestoreSlope, below, puts the game's own back over either of ours */
		LogParkSpot();
		LogWristMax();   /* the ride's wrist turn, when the rider was let go quietly before the dismount */
	}
	g_riding = riding;
	PublishGround(Player());
	/* How steep the ground here is, for the script to refuse getting off on a face too steep
	 * to stand on: the track's own slope and, once that says it's a slope at all (20 deg),
	 * the face's from the averaged normal (riding across a face, or turned on it, the track
	 * reads less: test 10). On the level the normal is left out: a curb can fool it. */
	float steep = 0.0f;
	if (riding && g_trackSteepOk) {
		steep = g_trackSteep;
		if (steep >= 20.0f && g_groundOk && !g_groundAir && g_avgAge >= 0.25f) {
			float face = acosf(g_avgN[2] > 1.0f ? 1.0f : g_avgN[2]) * 57.29578f;
			if (face > steep)
				steep = face;
		}
	}
	SetGlobal(g_trackSlopeGlobal, steep);

	/* The skins are held while the tilt is on, or on any ride when the bike has moving parts
	 * (the tilt turned off in the menu still leaves the wheels spinning). */
	if (riding && !g_wasRiding) {
		ReadRiderSwitches(false);
		ReadRamSettings(g_iniPath, false);
		ReadBackSettings(g_iniPath, false);
		/* Test 27: the block of a ride carried into the next one when nothing was held at the
		 * dismount (the bike's skins had gone first): a ride starts afresh. */
		g_riderBlocked = false;
		g_riderWorldChecked = false;
		g_riderWorldFailSince = -1.0f;
		g_riderBoneWarned = false;
		g_holdWaitSince = 0.0f;
		g_holdWaitExpired = false;
	}
	/* Test 40 (finding 2): 2.5 s into a ride a load started, what hasn't resumed is let go and
	 * held afresh, once, as getting off and on does; 6 s in it's looked at again, for the log
	 * only. 2.5: past the latest re-attach of the head's shapes after a load (1.57 s of wall
	 * time in tests 35, 37, 38 and 39) and the riding pose put back 1.0 s after the load
	 * (ReloadPoseDelay). Before the sync, so what's let go is held again in this tick. */
	if (riding && g_rideFromLoad && g_loadLook < 2 && (float)g_clock - g_rideStartClock >= (g_loadLook ? 6.0f : 2.5f))
		LoadLook(degrees, camera, tilt);
	if (tilt > 0.0f || (riding && g_partsOk)) {
		double t0 = Clock();
		int q0 = g_queries;
		SyncSkins(Player(), tilt > 0.0f);
		TimeAdd(&g_tSync, t0);
		g_syncQueries += g_queries - q0;
		if (g_queries - q0 > g_syncQueriesMax)
			g_syncQueriesMax = g_queries - q0;
	} else {
		if (g_skinCount || g_riderCount)   /* test 24: the bike's skins had gone first, and the rider's stayed held */
			LetGoAll("got off");
		else
			ResetTilt();
		g_emptySyncs = 0;   /* the next ride looks (and reports) afresh */
		g_rideDiagnosed = g_rideRouteLogged = false;
	}

	if (g_probe && ctrl) {
		if (!g_dumpedThisLoad) {
			g_dumpedThisLoad = true;
			DumpObject("character controller", ctrl, 0x600);
			if (proxy)
				DumpObject("Havok proxy", proxy, 0x600);
			for (int i = 0; i < g_dumpPointerCount; i++) {
				char label[48];
				snprintf(label, sizeof(label), "controller+0x%X", g_dumpPointers[i]);
				uintptr_t obj = ReadPtr(ctrl + g_dumpPointers[i]);
				if (obj)
					DumpObject(label, obj, 0x200);
			}
			SnapCollect(ctrl, proxy);
		}
		if (!SnapsMatch(ctrl, proxy)) {
			Log("the watched objects were replaced (load or cell change): new baseline");
			SnapCollect(ctrl, proxy);
		}
		/* Before our own write, so it shows what the game changed by itself. */
		if (riding && !g_wasRiding) {
			SnapDiff("getting on (changes since the last look, before writing anything)");
			g_mountTime = now;
			g_ridingSnapsDone = 0;
		} else if (riding && g_ridingSnapsDone == 0 && now - g_mountTime >= 1000) {
			g_ridingSnapsDone = 1;
			SnapDiff("1 s into the ride");
		} else if (riding && g_ridingSnapsDone == 1 && now - g_mountTime >= 3000) {
			g_ridingSnapsDone = 2;
			SnapDiff("3 s into the ride");
		}
	}

	if (degrees > 0.0f && degrees < 89.0f)
		ApplySlope(target, degrees);
	else
		RestoreSlope(target);

	if (g_probe && ctrl && !riding && g_wasRiding) {
		SnapDiff("getting off (after putting the limit back)");
	}
	g_wasRiding = riding;
}

/* Every frame while riding: keep the limit written (cheap: cached chain only), tilt the bike. */
static void Frame(void)
{
	double t0 = Clock();
	FrameTime();
	FrameSteer();
	SampleGround();
	TraceControls();
	float degrees = GlobalValue(g_slopeGlobal);
	if (g_applied && degrees > 0.0f && degrees < 89.0f) {
		uintptr_t target = FindChain(false, NULL, NULL);
		if (target && target == g_appliedTarget)
			ApplySlope(target, degrees);
	}
	FrameTilt();
	TimeAdd(&g_tFrame, t0);
	g_queryFrames++;
}

static void *Task_Destroy(Task *self, unsigned flags)
{
	(void)flags;
	return self;
}

static void Task_Run(Task *self)
{
	(void)self;
	if (!g_dataReady)
		return;
	DWORD now = GetTickCount();
	g_regionTick = now;   /* the region cache's entries age against the frame's tick; each lapses on its own (test 37: the 30 s flush here re-walked the rider in one sync) */
	if (now - g_lastTick >= g_interval) {
		g_lastTick = now;
		Tick(now);
	}
	Frame();
}

static void *g_taskVtbl[2] = { (void *)Task_Destroy, (void *)Task_Run };
static Task g_task = { g_taskVtbl };

static void OnF4SEMessage(F4SEMessage *msg)
{
	ForgetRegions();
	switch (msg->type) {
	case kMessage_GameDataReady:
		g_dataReady = msg->data != NULL;
		Log("game data %s", g_dataReady ? "ready" : "loading");
		static bool probed;
		if (g_dataReady && g_probe && !probed) {
			probed = true;
			ProbeSettings();
			ProbeReflection();
		}
		break;
	case kMessage_PostLoadGame:
	case kMessage_NewGame: {
		/* Test 40 (finding 2): a load on the bike lost the lean, and the log said nothing of the
		 * load. What was held before it, and where the player and his 3D were. */
		bool newGame = msg->type == kMessage_NewGame;
		uintptr_t pl = Player(), root = pl ? Root3D(pl) : 0;
		const float *pp = pl && Accessible(pl + OFF_REFR_POS, 12, false) ? (const float *)(pl + OFF_REFR_POS) : NULL;
		const float *rw = root && Accessible(root + OFF_WORLD_POS, 12, false) ? (const float *)(root + OFF_WORLD_POS) : NULL;
		Log("load: %s; before it %s (the globals slope %g, camera %g, tilt %g), %d bike skin(s) and %d rider shape(s) held%s, the tilt pitch %.1f roll %.1f (the lean %.1f), %s, "
		    "the upper body's lean %s%.1f deg%s; the globals now slope %g, camera %g, tilt %g; the player at (%.0f, %.0f, %.0f), the 3D root at (%.0f, %.0f, %.0f)",
		    newGame ? "a new game (NewGame)" : "a save loaded (PostLoadGame)", g_wasRiding ? "riding" : "not riding", g_tickSlope, g_tickCamera, g_tickTilt,
		    g_skinCount, g_riderCount, g_riderBlocked ? " (the rider blocked)" : "", g_pitchNow, g_rollNow, g_leanNow, GroundWord(),
		    g_torsoLeanSet ? "" : "not yet solved, ", g_torsoLean, g_torsoFinal ? ", final" : "", GlobalValue(g_slopeGlobal), GlobalValue(g_cameraGlobal),
		    GlobalValue(g_tiltGlobal), pp ? pp[0] : 0.0f, pp ? pp[1] : 0.0f, pp ? pp[2] : 0.0f, rw ? rw[0] : 0.0f, rw ? rw[1] : 0.0f, rw ? rw[2] : 0.0f);
		/* An in-game load starts as a cold one does (test 40: at a cold load nothing is held at
		 * PostLoadGame; at an in-game load the old holds went on into the loaded 3D, the arms'
		 * chains with them): everything let go of now, and held afresh at the first sync. */
		ClimbOff("a load");   /* the slot's boost value is taken back as ours at the next apply (ApplySlope), or put back if not riding (RestoreSlope) */
		g_stepCount = 0;   /* stage 2: a step's place and rise mean nothing in the loaded world */
		g_stepCheck = false;
		if (g_skinCount || g_riderCount)
			LetGoAll(newGame ? "a new game" : "a save loaded");
		g_loadPending = true;
		g_loadAt = (float)g_clock;
		/* Fresh objects: find the chain again, and dump them once more. */
		g_applied = false;
		g_appliedTarget = 0;
		g_dumpedThisLoad = false;
		g_wasRiding = false;
		g_stateCtrl = 0;   /* the held skins are let go of on the next check: not in the new 3D */
		g_riderBlocked = false;
		g_riderWorldChecked = false;
		g_riderWorldFailSince = -1.0f;
		g_riderBoneWarned = false;
		g_holdWaitSince = 0.0f;
		g_holdWaitExpired = false;
		ResetTorsoSolve();                      /* the upper body's lean solved again for the loaded pose (test 37) */
		g_torsoRetryAt = (float)g_clock + 0.5f; /* after the next tick's fresh ride start, not before it */
		g_zoomRiding = g_zoomTouched = false;   /* a new camera: nothing of ours to put back */
		g_steerHave = false;                    /* steer from the loaded heading */
		g_pushCtrl = 0;                         /* the old controller is gone: nothing to undo */
		g_pushMethod = -1;                      /* try the ways to push back again */
		g_pickState = 0;                        /* the rays' test ray again (a new world) */
		g_pickRetryAt = 0.0f;
		g_solidMaskRead = false;                /* and the collision layer record read again with it */
		g_pushProven = false;
		g_pushRetryAt = 0.0f;
		memset(g_refused, 0, sizeof(g_refused));
		g_skinsRefused = g_skinsUnbuilt = 0;
		TrackClear();
		g_avgAge = 0.0f;
		break;
	}
	default:
		break;
	}
}

__declspec(dllexport) bool F4SEPlugin_Load(const F4SEInterface *f4se)
{
	OpenLog();
	SYSTEMTIME day;
	GetLocalTime(&day);   /* the lines' times carry no date */
	Log("CMB_Slope %d for Fallout 4 1.11.240 (F4SE %08X, runtime %08X), started %04u-%02u-%02u; %s", PLUGIN_VERSION,
	    f4se->f4seVersion, f4se->runtimeVersion, day.wYear, day.wMonth, day.wDay,
	    g_logRotated > 0 ? "the session before's log kept as CMB_Slope_prev.log"
	    : g_logRotated < 0 ? "the session before's log couldn't be kept as CMB_Slope_prev.log" : "no log of a session before");
	if (g_logRotated < 0)
		Log("  (MoveFileEx error %lu)", g_logRotateError);
	if (f4se->isEditor || f4se->runtimeVersion != RUNTIME_1_11_240) {
		Log("not the game version this was made for: staying off");
		return false;
	}
	g_base = (uintptr_t)GetModuleHandleA(NULL);
	const IMAGE_DOS_HEADER *dos = (const IMAGE_DOS_HEADER *)g_base;
	const IMAGE_NT_HEADERS64 *nt = (const IMAGE_NT_HEADERS64 *)(g_base + dos->e_lfanew);
	g_imageEnd = g_base + nt->OptionalHeader.SizeOfImage;
	QueryPerformanceFrequency(&g_qpcFrequency);
	ReadSettings();

	F4SEMessagingInterface *messaging = (F4SEMessagingInterface *)f4se->QueryInterface(kInterface_Messaging);
	F4SETaskInterface *tasks = (F4SETaskInterface *)f4se->QueryInterface(kInterface_Task);
	if (!messaging || !tasks || tasks->interfaceVersion < 2 || !tasks->AddTaskPermanent) {
		Log("F4SE's messaging or task interface is missing: staying off");
		return false;
	}
	messaging->RegisterListener(f4se->GetPluginHandle(), "F4SE", OnF4SEMessage);
	tasks->AddTaskPermanent(&g_task);
	Log("loaded");
	return true;
}

BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID reserved)
{
	(void)reserved;
	if (reason == DLL_PROCESS_ATTACH) {
		g_module = instance;
		DisableThreadLibraryCalls(instance);
	}
	return TRUE;
}
