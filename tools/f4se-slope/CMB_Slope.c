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
 *   while riding, in case the game sets it back; the original goes back afterwards.
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
 *
 * With Probe=1 it also logs (Documents\My Games\Fallout4\F4SE\CMB_Slope.log) the
 * layout of the controller, the proxy and the objects listed in DumpPointers, then on
 * getting on, 1 and 3 seconds into the ride and on getting off, what changed: that's
 * how the slope limit's and the ground normal's places were found.
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
#define OFF_ARRAY_COUNT       0x10          /* tArray::count */
#define OFF_MOD_NAME          0x70          /* ModInfo::name[MAX_PATH] */
#define OFF_MOD_INDEX         0x370         /* ModInfo::modIndex (UInt8) */
#define OFF_MOD_LIGHT_INDEX   0x372         /* ModInfo::lightIndex (UInt16) */
#define OFF_FORM_ID           0x14          /* TESForm::formID */
#define OFF_FORM_TYPE         0x1A          /* TESForm::formType */
#define FORM_TYPE_GLOB        11
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
static float g_pivotHeight = 74.0f;       /* the seat (the rider's hips) above the feet */
static int g_trace;                       /* 1 = log the tilt every 0.25 s while riding */
static int g_steer = 1;                   /* 1 = limit how fast the bike turns (CMB_TurnRadius) */
static float g_fullSpeed = 900.0f;        /* units a second at which the turning radius is CMB_TurnRadius */
static int g_reverse = 1;                 /* 1 = holding back backs the bike up instead of turning it round */
static int g_inputHook = 1;               /* 1 = change the move input before the game uses it (creep, reverse) */
static int g_creep = 1;                   /* 1 = a side key from a stop creeps forward round a CreepRadius circle */
static float g_creepStart = 0.1f;         /* the first forward input tried for the creep (then learnt) */
static float g_creepBelow = 100.0f;       /* a side key alone creeps below this speed */
static float g_creepRadius = 55.0f;       /* the creep goes round this circle (test 15: a bit more than 40) */
static float g_backSpeed = 80.0f;         /* units a second the bike is pushed back */
enum { PUSH_DELTA, PUSH_RAYSTEP, PUSH_MOD, PUSH_VELOCITY, PUSH_POSITION, PUSH_BRAKE };
static int g_backPushFirst = PUSH_RAYSTEP;   /* BackPush: the method to start with */
static bool g_backPushAuto = true;        /* BackPush=auto: steps after rays, else brake */
static float g_backClearance = 150.0f;    /* this far behind the rider must be clear (test 16: the rear is about 130 back) */
static float g_backSink;                  /* BackSink: units the feet go into the ground when closing a gap (0: onto it) */
static int g_backSupportCheck;            /* BackSupportCheck: call the controller's CheckSupportImpl after a step */
static char g_shapePrefix[64] = "CMB_BikeWorn";
enum { LAYOUT_UNKNOWN = -1, LAYOUT_FILE = 0, LAYOUT_TRANSPOSED = 1, LAYOUT_DISAGREE = 2 };
static int g_layoutSetting = LAYOUT_UNKNOWN;   /* Layout=auto */

static volatile bool g_dataReady;
static uintptr_t g_slopeGlobal, g_cameraGlobal;   /* TESGlobal * */
static uintptr_t g_tiltGlobal, g_groundGlobals[3], g_parkGlobals[7], g_trackSlopeGlobal;
static uintptr_t g_turnRadiusGlobal, g_turnStandGlobal, g_turnSlowGlobal;
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

/* Tilt: the worn bike's skins we hold, and what they were. */
#define MAX_SKINS 4
#define MAX_BONES 4
typedef struct {
	uintptr_t boneData;                 /* BSSkin::BoneData, with a reference of ours */
	uintptr_t bones;                    /* its BoneTransforms */
	int count;
	uint8_t original[MAX_BONES][BONE_SIZE];
	char name[48];
} HeldSkin;
static HeldSkin g_skins[MAX_SKINS];
static int g_skinCount;
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

/* Accessible()'s memory regions, for one frame (the scene graph walk reads thousands
 * of pointers; asking Windows about each one would cost milliseconds). */
typedef struct { uintptr_t start, end; bool writable; } Region;
static Region g_regions[16];
static int g_regionCount;

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

static void OpenLog(void)
{
	char path[MAX_PATH];
	if (SUCCEEDED(SHGetFolderPathA(NULL, CSIDL_PERSONAL | CSIDL_FLAG_CREATE, NULL, SHGFP_TYPE_CURRENT, path))) {
		strncat(path, "\\My Games\\Fallout4\\F4SE", sizeof(path) - strlen(path) - 1);
		CreateDirectoryA(path, NULL);
		strncat(path, "\\CMB_Slope.log", sizeof(path) - strlen(path) - 1);
		g_log = fopen(path, "w");
	}
	if (!g_log) {
		/* Next to the DLL instead. */
		GetModuleFileNameA(g_module, path, sizeof(path));
		char *dot = strrchr(path, '.');
		if (dot)
			strcpy(dot, ".log");
		g_log = fopen(path, "w");
	}
}

static void ReadSettings(void)
{
	char ini[MAX_PATH], value[256];
	GetModuleFileNameA(g_module, ini, sizeof(ini));
	char *dot = strrchr(ini, '.');
	if (!dot)
		return;
	strcpy(dot, ".ini");
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
	GetPrivateProfileStringA("Tilt", "PivotHeight", "74", value, sizeof(value), ini);
	g_pivotHeight = strtof(value, NULL);
	if (!(g_pivotHeight >= -50.0f && g_pivotHeight <= 200.0f))
		g_pivotHeight = 74.0f;
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
	Log("  tilt: NormalOffset=0x%X StateOffset=0x%X Smoothing=%g MedianTime=%g MaxRate=%g MaxRoll=%g PivotHeight=%g Trace=%d Shapes=%s Layout=%s",
	    g_normalOffset, g_stateOffset, g_smoothing, g_medianTime, g_maxRate, g_maxRoll, g_pivotHeight, g_trace, g_shapePrefix,
	    g_layoutSetting == LAYOUT_FILE ? "file" : g_layoutSetting == LAYOUT_TRANSPOSED ? "transposed" : "auto");
	static const char *const pushValueNames[] = { "delta", "ray", "mod", "velocity", "position", "off" };
	Log("  steer: Enabled=%d FullSpeed=%g InputHook=%d Creep=%d CreepInput=%g CreepBelow=%g CreepRadius=%g Reverse=%d BackSpeed=%g "
	    "BackPush=%s BackClearance=%g BackSink=%g BackSupportCheck=%d",
	    g_steer, g_fullSpeed, g_inputHook, g_creep, g_creepStart, g_creepBelow, g_creepRadius, g_reverse, g_backSpeed,
	    g_backPushAuto ? "auto" : pushValueNames[g_backPushFirst], g_backClearance, g_backSink, g_backSupportCheck);
}

/* ------------------------------------------------------------------------- */
/* Safe memory access                                                        */
/* ------------------------------------------------------------------------- */

static bool Accessible(uintptr_t p, size_t n, bool write)
{
	if (p < 0x10000 || p > 0x7FFFFFFEFFFFull || n > 0x100000)
		return false;
	for (int i = 0; i < g_regionCount; i++) {
		const Region *r = &g_regions[i];
		if (p >= r->start && p + n <= r->end && (r->writable || !write))
			return true;
	}
	MEMORY_BASIC_INFORMATION mbi;
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
	Region *r = &g_regions[g_regionCount < 16 ? g_regionCount++ : (int)((p >> 12) % 16)];
	r->start = (uintptr_t)mbi.BaseAddress;
	r->end = end;
	r->writable = (mbi.Protect & writable) != 0;
	return p + n <= end;
}

/* Called at the start of every frame: memory may have been freed since. */
static void ForgetRegions(void)
{
	g_regionCount = 0;
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

static void RestoreSlope(uintptr_t target)
{
	if (!g_applied)
		return;
	if (target && target == g_appliedTarget) {
		float *slot = (float *)(target + g_slopeOffset);
		if (Accessible((uintptr_t)slot, 4, true) && *slot == g_writtenValue) {
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
		if (!Plausible(current) || !AsExpected(current)) {
			if (!g_badValueLogged)
				Log("%s+0x%X holds %g (%.2f deg), not the expected %g deg: not touching it",
				    TargetName(), g_slopeOffset, current, Plausible(current) ? ToDegrees(current) : 0.0f, g_expectedDegrees);
			g_badValueLogged = true;
			return;
		}
		g_originalValue = current;
		g_writtenValue = Steeper(FromDegrees(degrees), current);   /* only ever steeper than the game's */
		g_applied = true;
		g_appliedTarget = target;
		g_revertCount = 0;
		Log("riding: slope limit at %s+0x%X %.2f -> %.2f deg", TargetName(), g_slopeOffset,
		    ToDegrees(current), ToDegrees(g_writtenValue));
		*slot = g_writtenValue;
	} else if (*slot != g_writtenValue) {
		if (g_revertCount++ == 0)
			Log("the game set the slope limit back to %.2f deg; setting it again every frame while riding",
			    ToDegrees(*slot));
		*slot = g_writtenValue;
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

static void HoldSkin(uintptr_t data, const char *name)
{
	uintptr_t array = data + OFF_BONE_TRANSFORMS;
	uintptr_t bones = ReadPtr(array + OFF_ARRAY_ENTRIES);
	if (!bones || !Accessible(array + OFF_ARRAY_COUNT, 4, false)) {
		Refuse(data);
		return;
	}
	uint32_t count = *(const uint32_t *)(array + OFF_ARRAY_COUNT);
	if (count == 0 || count > MAX_BONES || !Accessible(bones, count * BONE_SIZE, true)) {
		Log("tilt: %s has %u bones: not touching it", name, count);
		Refuse(data);
		return;
	}
	for (uint32_t b = 0; b < count; b++)
		if (!LooksLikeBone((const uint8_t *)(bones + b * BONE_SIZE))) {
			Log("tilt: %s's skin data doesn't look like bone transforms: not touching it", name);
			Refuse(data);
			return;
		}
	HeldSkin *h = &g_skins[g_skinCount++];
	InterlockedIncrement((volatile LONG *)(data + OFF_REFCOUNT));
	h->boneData = data;
	h->bones = bones;
	h->count = (int)count;
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
static void ResetTilt(void)
{
	g_tiltSampleCount = 0;
	g_pitchSmooth = g_rollSmooth = g_pitchNow = g_rollNow = 0.0f;
	g_tiltMax = g_tiltNow = 0.0f;
}

static void LetGoAll(const char *why)
{
	while (g_skinCount)
		LetGo(g_skinCount - 1, why);
	ResetTilt();
}

/* --- Finding the worn bike's skin ------------------------------------------
 * Two routes: everything under the player's 3D root, and the biped's equipped parts
 * (what's worn in each slot, wherever its 3D hangs). A shape counts if its name starts
 * with Shapes=, or, whatever its name, if it's skinned to one bone with the COM bike's
 * bind. When a ride finds nothing for a second, the walk is logged once. */

typedef struct {
	uintptr_t found[MAX_SKINS];
	const char *names[MAX_SKINS];
	int count;
	bool byBind[MAX_SKINS];
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

static void AddSkin(SkinList *list, uintptr_t data, const char *name, bool byBind)
{
	for (int i = 0; i < list->count; i++)
		if (list->found[i] == data)
			return;
	if (list->count >= MAX_SKINS)
		return;
	list->names[list->count] = name ? name : "(unnamed shape)";
	list->byBind[list->count] = byBind;
	list->found[list->count++] = data;
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
		AddSkin(list, data, name, byBind || byAddon);
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
static void SyncSkins(uintptr_t player)
{
	SkinList list = { .count = 0 };
	uintptr_t root = Root3D(player);
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
		if (!still)
			LetGo(i, "no longer worn");
	}
	for (int j = 0; j < list.count && g_skinCount < MAX_SKINS; j++) {
		bool held = false;
		for (int i = 0; i < g_skinCount; i++)
			held |= g_skins[i].boneData == list.found[j];
		if (!held && !Refused(list.found[j]))
			HoldSkin(list.found[j], list.names[j]);
	}
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

static float Toward(float from, float to, float maxStep)
{
	return to > from + maxStep ? from + maxStep : to < from - maxStep ? from - maxStep : to;
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
	if (!g_skinCount || !(maxDegrees > 0.0f) || (g_layout != LAYOUT_FILE && g_layout != LAYOUT_TRANSPOSED))
		return;
	uintptr_t player = Player();
	if (!player || !Accessible(player + OFF_REFR_HEADING, 4, false))
		return;
	float h = *(const float *)(player + OFF_REFR_HEADING);
	if (!isfinite(h))
		return;

	/* The ground's normal in the rider's frame: heading h, forward (sin h, cos h), right (cos h, -sin h). */
	bool onGround = g_groundOk && !g_groundAir;
	float rawPitch = 0.0f, rawRoll = 0.0f;
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
	bool useNormal = !g_trackPitchOk && onGround && !g_hadTrackPitch;   /* only before the track has said anything */
	const char *source = g_trackPitchOk ? "track" : useNormal ? "normal" : "held";
	float maxRoll = g_maxRoll < maxDegrees ? g_maxRoll : maxDegrees;
	float targetPitch = g_trackPitchOk ? Clamp(g_trackPitch, maxDegrees) : useNormal ? Clamp(medianPitch, maxDegrees) : g_pitchSmooth;
	float targetRoll = onGround ? Clamp(medianRoll, maxRoll) : g_rollSmooth;
	/* Capped before smoothing, so coming off a steep slope starts easing back at once. */
	float k = g_smoothing > 0.0f ? 1.0f - expf(-g_frameDt / g_smoothing) : 1.0f;
	g_pitchSmooth += (targetPitch - g_pitchSmooth) * k;
	g_rollSmooth += (targetRoll - g_rollSmooth) * k;
	float step = g_maxRate > 0.0f ? g_maxRate * g_frameDt : 1000.0f;
	g_pitchNow = Toward(g_pitchNow, g_pitchSmooth, step);
	g_rollNow = Toward(g_rollNow, g_rollSmooth, step);

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
		Log("trace: normal (%.3f, %.3f, %.3f) state %d%s | raw pitch %.1f roll %.1f | median %.1f %.1f | track %s%.1f | pitch from %s | smooth %.1f %.1f | applied %.1f %.1f | speed %.0f (%+.0f along the heading), radius %.0f, turn asked %.0f allowed %.0f deg/s, clamped %d%s",
		    g_groundN[0], g_groundN[1], g_groundN[2], g_lastState, onGround ? "" : " (off the ground)", rawPitch, rawRoll,
		    medianPitch, medianRoll, g_trackPitchOk ? "" : "(none) ", g_trackPitchOk ? g_trackPitch : 0.0f, source,
		    g_pitchSmooth, g_rollSmooth, g_pitchNow, g_rollNow, g_speed, g_speedAlong, g_steerRadius, g_steerWanted, g_steerAllowed,
		    g_steerClamped, g_inputMode == INPUT_BACK ? " | back" : g_inputMode == INPUT_CREEP ? " | creep" : "");
		g_steerWanted = 0.0f;
		g_steerClamped = 0;
	}

	/* Turned about the seat P (mesh space): x -> R (x - P) + P. Mesh -> bone after the turn:
	 * rotation A R, translation t + A (P - R P), so the seat lands where it always did. */
	float P[3] = { 0.0f, 0.0f, g_pivotHeight };
	float d[3];
	for (int i = 0; i < 3; i++)
		d[i] = P[i] - (R[i * 3] * P[0] + R[i * 3 + 1] * P[1] + R[i * 3 + 2] * P[2]);
	for (int k2 = 0; k2 < g_skinCount; k2++) {
		const HeldSkin *hs = &g_skins[k2];
		for (int b = 0; b < hs->count; b++) {
			const uint8_t *orig = hs->original[b];
			uint8_t *live = (uint8_t *)(hs->bones + (uintptr_t)b * BONE_SIZE);
			const float *o = (const float *)(orig + OFF_BONE_ROT), *t = (const float *)(orig + OFF_BONE_POS);
			float A[9], B[9];
			for (int i = 0; i < 3; i++)
				for (int j = 0; j < 3; j++)
					A[i * 3 + j] = g_layout == LAYOUT_FILE ? o[i * 4 + j] : o[j * 4 + i];
			for (int i = 0; i < 3; i++)
				for (int j = 0; j < 3; j++)
					B[i * 3 + j] = A[i * 3] * R[j] + A[i * 3 + 1] * R[3 + j] + A[i * 3 + 2] * R[6 + j];
			float *w = (float *)(live + OFF_BONE_ROT), *pos = (float *)(live + OFF_BONE_POS);
			for (int i = 0; i < 3; i++)
				for (int j = 0; j < 3; j++)
					w[i * 4 + j] = g_layout == LAYOUT_FILE ? B[i * 3 + j] : B[j * 3 + i];
			float seat[3];   /* where the bone sees the seat: A P + t */
			for (int i = 0; i < 3; i++) {
				pos[i] = t[i] + A[i * 3] * d[0] + A[i * 3 + 1] * d[1] + A[i * 3 + 2] * d[2];
				seat[i] = t[i] + A[i * 3] * P[0] + A[i * 3 + 1] * P[1] + A[i * 3 + 2] * P[2];
			}
			/* The culling sphere (bone space) turns about the seat: grow it by the most its centre moves. */
			const float *centre = (const float *)orig;
			float dx = centre[0] - seat[0], dy = centre[1] - seat[1], dz = centre[2] - seat[2];
			float radius = *(const float *)(orig + OFF_BONE_RADIUS);
			*(float *)(live + OFF_BONE_RADIUS) = radius + 2.0f * sqrtf(dx * dx + dy * dy + dz * dz) * sinf(angle * 0.5f);
		}
	}
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

/* Every frame: read the ground once (tilt, average, track all use it). */
static void SampleGround(void)
{
	g_trackPitchOk = g_trackSteepOk = false;
	uintptr_t player = Player();
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
	g_groundAir = air;
	bool onGround = g_groundOk && !air;
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
		if (g_airTime > TRACK_MAX_AIR) {
			TrackClear();
			g_avgAge = 0.0f;   /* a drop: the ground before it says nothing about after */
		}
		return;
	}
	g_airTime = 0.0f;
	const float *pos = (const float *)(player + OFF_REFR_POS);
	if (!isfinite(pos[0]) || !isfinite(pos[1]) || !isfinite(pos[2]))
		return;
	if (g_trackCount) {
		const TrackPoint *last = TrackAt(0);
		float dx = pos[0] - last->p[0], dy = pos[1] - last->p[1];
		if (Distance(pos, last->p) > 150.0f)
			TrackClear();   /* a door, fast travel, a teleport */
		else if (dx * dx + dy * dy < TRACK_SPACING * TRACK_SPACING) {
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
	int mode = INPUT_PASS;
	if (g_inputActive && isfinite(x) && isfinite(y)) {
		if (y < -0.2f)
			mode = g_reverse ? INPUT_BACK : INPUT_PASS;
		else if (y <= 0.2f && fabsf(x) > 0.05f && (g_inputMode == INPUT_CREEP || g_speed < g_creepBelow))
			mode = INPUT_CREEP;
	}
	if (mode != g_inputMode)
		g_modeChanges++;
	g_inputMode = mode;
	if (mode == INPUT_PASS)
		return;
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
static bool ReadableNow(uintptr_t p, size_t n)
{
	MEMORY_BASIC_INFORMATION mbi;
	if (p < 0x10000 || VirtualQuery((const void *)p, &mbi, sizeof(mbi)) != sizeof(mbi) || mbi.State != MEM_COMMIT ||
	    (mbi.Protect & (PAGE_GUARD | PAGE_NOACCESS)) || !(mbi.Protect & (PAGE_READONLY | PAGE_READWRITE | PAGE_WRITECOPY |
	    PAGE_EXECUTE_READ | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY)))
		return false;
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
	if (g_inputActive && g_inputMode != INPUT_PASS && g_moveVec) {
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
static float g_savedMod[4], g_savedModTime;
static int g_ctrlCheck;             /* 0 not yet, 1 the controller's functions look right, -1 they don't */
static float g_havok = HAVOK_SCALE; /* game units -> the controller's */

static void *CtrlFunc(uintptr_t ctrl, int index)
{
	uintptr_t vtbl = ReadPtr(ctrl);
	uintptr_t f = vtbl ? ReadPtr(vtbl + 8 * index) : 0;
	return InImage(f, 1) ? (void *)f : NULL;
}

static bool CheckControllerFuncs(uintptr_t ctrl, const float pos[3])
{
	if (g_ctrlCheck)
		return g_ctrlCheck > 0;
	g_ctrlCheck = -1;
	GetPosFn get = (GetPosFn)CtrlFunc(ctrl, VF_CTRL_GET_POSITION);
	if (!get || !CtrlFunc(ctrl, VF_CTRL_SET_POSITION) || !CtrlFunc(ctrl, VF_CTRL_GET_VELOCITY) || !CtrlFunc(ctrl, VF_CTRL_SET_VELOCITY)) {
		Log("reverse: the controller's vtable has no functions at 0x33/0x34/0x39/0x3A: not using them");
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
	Log("reverse: the controller's GetPositionImpl gives (%.3f, %.3f, %.3f, w %.3g) for the player at (%.0f, %.0f, %.0f): %s",
	    out[0], out[1], out[2], out[3], pos[0], pos[1], pos[2],
	    g_ctrlCheck < 0 ? "not the position: its functions aren't used" : g_havok < 1.0f ? "Havok's units" : "the game's units");
	return g_ctrlCheck > 0;
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
static __attribute__((aligned(16))) uint8_t g_pick[PICK_DATA_SIZE + 0x20];   /* one, reused: no world reference per ray */
static const char *g_rayWhat;       /* what the last ray hit (its 3D's name), for the log */
static uint32_t g_rayFilter = LAYER_CHAR_CONTROLLER;   /* the rays' collision filter (0 = everything, if the test says) */
static uint32_t g_rayLayer;         /* the last hit's collision layer */
static float g_rayHit[3];           /* and where it was */
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

/* What a bike can back through: with the player's collision filter every hit is something
 * the capsule collides with, except the phantoms: triggers (12), acoustic spaces (21), actor
 * zones (22, test 17: the "nothing" test 16 stopped at on a flat slab), projectile zones (23),
 * gas traps (24) and door detection (37); and what the capsule pushes aside or steps over:
 * clutter (4), weapons (5), small debris (19), shell casings (25), dead bodies (32), and water
 * (11: the ground ray then finds the bed, so deep water is a drop). Everything else stops it
 * (test 17: a chain-link fence is layer 26, transparent small, and was passed through). */
static bool SolidLayer(uint32_t layer)
{
	switch (layer) {
	case 4: case 5: case 11: case 12: case 19: case 21: case 22: case 23: case 24: case 25: case 32: case 37:
		return false;
	default:
		return true;
	}
}

/* One ray from a to b (game units): the fraction along it where it first hits something solid
 * (1 if nothing), passing on through anything that isn't; what it hit in g_rayWhat, its layer
 * in g_rayLayer and where in g_rayHit. */
static float CastRay(uintptr_t cell, const float a[3], const float b[3])
{
	float from[3] = { a[0], a[1], a[2] }, done = 0.0f, t = 1.0f;
	float len = sqrtf((b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1]) + (b[2] - a[2]) * (b[2] - a[2]));
	for (int tries = 0; tries < 8; tries++) {
		g_rayWhat = NULL;
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
		if (obj && IsA(obj, RTTI_AVOBJECT))
			g_rayWhat = ObjectName(obj);
		if (SolidLayer(g_rayLayer))
			return t;
		if (g_trace && g_clock - g_passedLogged >= 1.0f) {
			g_passedLogged = g_clock;
			Log("reverse: a ray passed through %s (layer %u)", g_rayWhat && *g_rayWhat ? g_rayWhat : "unnamed", g_rayLayer);
		}
		done = t + 4.0f / (len > 1.0f ? len : 1.0f);   /* on from past it */
		if (done >= 1.0f)
			return 1.0f;
		for (int i = 0; i < 3; i++)
			from[i] = a[i] + (b[i] - a[i]) * done;
	}
	/* Out of tries in a pile of things passed through: counted as a hit (test 18: a ray down
	 * through a broken fence's bits read as no ground, a drop). */
	return t;
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
	if (!cell || !IsA(cell, RTTI_CELL)) {
		Log("reverse: no parent cell: no rays");
		return false;
	}
	const float *pos = (const float *)(player + OFF_REFR_POS);
	float h = *(const float *)(player + OFF_REFR_HEADING);
	float a[3] = { pos[0] - sinf(h) * 60.0f, pos[1] - cosf(h) * 60.0f, pos[2] + 100.0f };
	float b[3] = { a[0], a[1], pos[2] - 100.0f };
	g_rayFilter = LAYER_CHAR_CONTROLLER;
	float down = CastRay(cell, a, b);
	if (!(down > 0.2f && down < 0.8f)) {
		g_rayFilter = 0;   /* the character's filter finds no ground: everything, then */
		down = CastRay(cell, a, b);
	}
	bool ok = down > 0.2f && down < 0.8f;
	Log("reverse: a test ray down beside the bike (filter %u) hit %s (layer %u) at %.2f of the way (the ground about where the "
	    "player stands is 0.2-0.8): %s; the pick data's world %p, collector %p", g_rayFilter,
	    g_rayWhat && *g_rayWhat ? g_rayWhat : down < 1.0f ? "something" : "nothing", down < 1.0f ? g_rayLayer : 0, down,
	    ok ? "rays work" : "not trusted (tried again in 3 s)", *(void **)(g_pick + 0xC0), *(void **)(g_pick + 0xD0));
	g_pickState = ok ? 1 : -1;
	return ok;
}

/* Is the way back clear for a step of `step` units along `heading`? The ground is found 55
 * units behind the rider (clear of their own body) and under the rear (BackClearance): there
 * must be some, and the rays at knee height on either side of the bike (20 units out) and at
 * chest height in the middle follow it between (so a slope behind isn't taken for a wall). The
 * feet go to the ground under the step, near the slope's (dz). Not while the bike is in the air
 * (test 16: steps down a steep slope left it unsupported for seconds): it lands first. Else why
 * not (logged once a second, with what the ray hit, its layer and where). */
static bool WayBackClear(uintptr_t player, float heading, float step, float *dz)
{
	uintptr_t cell = ReadPtr(player + OFF_REFR_CELL);
	if (!cell || !IsA(cell, RTTI_CELL))
		return false;
	const float *pos = (const float *)(player + OFF_REFR_POS);
	float dir[2] = { -sinf(heading), -cosf(heading) }, right[2] = { cosf(heading), -sinf(heading) };
	const char *why = NULL;
	bool hit = false;
	float at = 0.0f, behindNear = 55.0f, behindFar = g_backClearance, groundNear = 0.0f, groundFar = 0.0f;
	g_rayGrounded = false;
	g_rayFeetGap = -99.0f;
	{
		float a[3] = { pos[0] + dir[0] * behindNear, pos[1] + dir[1] * behindNear, pos[2] + 60.0f };
		float b[3] = { a[0], a[1], pos[2] - 60.0f };
		float f = CastRay(cell, a, b);
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
		float f = CastRay(cell, a, b);
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
	if (!why && slope > 0.0f)
		g_rayGrounded = true;   /* uphill the feet never float */
	if (!why && slope <= 0.0f) {
		/* Level or going down: the ground under the step, from 2 units above the feet (the
		 * capsule's bottom is a hemisphere, so at the step point its skin is about at the feet;
		 * if the ray starts inside it anyway and the player's filter reports that, the hit is
		 * at the start and goes unused, as does the ground at the feet). A gap under the feet
		 * is closed: they go onto the ground (plus BackSink), at most 3 units down a frame
		 * (test 16: the least time in the air; test 18: 1.5 units into it, the most, the
		 * controller losing its support). More than 20 down is a drop: no step. Not uphill:
		 * there the ray would start inside a curb or the slope (a box ignored from inside, the
		 * ray finds the ground beneath), and the feet never float. */
		float a[3] = { pos[0] + dir[0] * step, pos[1] + dir[1] * step, pos[2] + 2.0f };
		float b[3] = { a[0], a[1], pos[2] - 38.0f };
		float f = CastRay(cell, a, b);
		if (f < 1.0f) {
			float below = f * 40.0f - 2.0f;
			g_rayFeetGap = below;
			if (below > 20.0f) {
				why = "the ground drops away under the step";
				at = step;
			} else {
				g_rayGrounded = below > -1.5f && below < 4.0f;   /* -2: the capsule itself, no telling */
				if (below > 0.3f) {
					float down = below + g_backSink;
					*dz = -(down < 0.0f ? 0.0f : down < 3.0f ? down : 3.0f);
				}
			}
		}
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
		if (g_pushMethod == PUSH_RAYSTEP && (!RaysReady(player) || !WayBackClear(player, heading, stepGame, &dz))) {
			g_pushBlocked = true;
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
	if (!ctrl || g_pushMethod == PUSH_BRAKE)
		return heading;   /* braking: no turning either */
	if (g_pushCtrl && g_pushCtrl != ctrl)
		g_pushCtrl = 0;   /* a new controller (a load): nothing to undo on the old one */
	if (g_pushMethod != PUSH_MOD && g_pushMethod != PUSH_DELTA && !CheckControllerFuncs(ctrl, (const float *)(player + OFF_REFR_POS))) {
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
	if (!g_pushClock && g_speedAlong < 30.0f)
		g_pushClock = true;   /* the trial starts once the bike has stopped going forward */
	if (!g_pushClock || g_pushBlocked)
		return used;   /* stopped by something behind: says nothing about the method */
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
		g_speed = g_speedAlong = g_speedAlongFast = 0.0f;
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
	float allowed = rate * g_frameDt;
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
	} else if (fabsf(wanted) > allowed) {
		*h = fmodf(g_steerHeading + copysignf(allowed, wanted) + twoPi, twoPi);
		g_steerClamped++;
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
				Log("  rays (filter %u): the ground %+.0f just behind, %+.0f under the rear, feet gap %+.1f, step dz %+.2f, "
				    "%s%s; controller: state %d, supported bit %d, support count %u, fake support %d, in air pre-move %d, "
				    "flags %08X; proxy +18 %u, +12C %08X (%g)",
				    g_rayFilter, g_rayGroundNear, g_rayGroundFar, g_rayFeetGap, g_rayDz,
				    g_rayGrounded ? "on the ground by the rays" : "not grounded by the rays", g_pushBlocked ? "; stopped" : "",
				    g_lastState, (flags & 0x400u) != 0, fields ? *(const uint32_t *)(c + OFF_CTRL_SUPPORT_COUNT) : 0,
				    fields ? *(const uint8_t *)(c + OFF_CTRL_FAKE_SUPPORT) : 0, fields ? *(const uint8_t *)(c + OFF_CTRL_IN_AIR_PRE_MOVE) : 0,
				    flags, pfields ? *(const uint32_t *)(proxy + 0x18) : 0u, pfields ? *(const uint32_t *)(proxy + 0x12C) : 0u,
				    pfields ? *(const float *)(proxy + 0x12C) : 0.0f);
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

	/* A new ride starts a new track. */
	if (riding && !g_wasRiding) {
		TrackClear();
		ResetTilt();   /* test 9: a ride that ended by taking the bike off kept the last pitch */
		g_parkValid = false;
		g_parkPublishedAt = -100.0f;
	}
	if (!riding && g_wasRiding)
		LogParkSpot();
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

	if (tilt > 0.0f) {
		SyncSkins(Player());
	} else {
		if (g_skinCount)
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
	ForgetRegions();
	DWORD now = GetTickCount();
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
	case kMessage_NewGame:
		/* Fresh objects: find the chain again, and dump them once more. */
		g_applied = false;
		g_appliedTarget = 0;
		g_dumpedThisLoad = false;
		g_wasRiding = false;
		g_stateCtrl = 0;   /* the held skins are let go of on the next check: not in the new 3D */
		g_zoomRiding = g_zoomTouched = false;   /* a new camera: nothing of ours to put back */
		g_steerHave = false;                    /* steer from the loaded heading */
		g_pushCtrl = 0;                         /* the old controller is gone: nothing to undo */
		g_pushMethod = -1;                      /* try the ways to push back again */
		g_pickState = 0;                        /* the rays' test ray again (a new world) */
		g_pickRetryAt = 0.0f;
		g_pushProven = false;
		memset(g_refused, 0, sizeof(g_refused));
		TrackClear();
		g_avgAge = 0.0f;
		break;
	default:
		break;
	}
}

__declspec(dllexport) bool F4SEPlugin_Load(const F4SEInterface *f4se)
{
	OpenLog();
	Log("CMB_Slope %d for Fallout 4 1.11.240 (F4SE %08X, runtime %08X)", PLUGIN_VERSION,
	    f4se->f4seVersion, f4se->runtimeVersion);
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
