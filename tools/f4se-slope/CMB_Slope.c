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
 * CMB_GroundNormalX/Y/Z (the ground under the player, for parking the bike).
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
 *   this is here, where the player's own value can be read.
 *
 *   Ground: the controller keeps the normal of the ground the player stands on (its
 *   support normal, controller+0x1E0) and Havok's character state (on the ground,
 *   jumping, in the air, ...; controller+0x2C0, in the hknpCharacterContext whose state
 *   manager is at +0x2B8). On the ground, the normal goes into CMB_GroundNormalX/Y/Z
 *   every IntervalMs (otherwise Z is 0): the controller script lays the parked bike on
 *   that plane.
 *
 *   Tilt: the worn bike is skinned to one bone of the rider (COM or AnimObjectA), so
 *   the animation moves it and its own node's transform does nothing. What the plugin
 *   turns instead is the skin's bind (BSSkin::BoneData, the mesh -> bone transform):
 *   the mesh is turned about the rider's feet before it goes onto the bone, so the bike
 *   pitches and rolls with the ground (smoothed, at most CMB_TiltLive degrees, eased
 *   back to level in the air) and still follows every move of the animation. The plugin
 *   holds a reference on the BoneData while it's changed and puts it back afterwards.
 *   Which way round the game stores its rotation matrices is read off the bike's own
 *   skin (whose bind we know) and the player's 3D (whose heading we know).
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

/* RTTI names (MSVC mangled) of the objects we look for. */
#define RTTI_PLAYER     ".?AVPlayerCharacter@@"
#define RTTI_CONTROLLER ".?AVbhkCharacterController@@"
#define RTTI_PROXY      ".?AVhknpCharacterProxy@@"
#define RTTI_STATES     ".?AVhknpCharacterStateManager@@"
#define RTTI_NODE       ".?AVNiNode@@"
#define RTTI_GEOMETRY   ".?AVBSGeometry@@"
#define RTTI_SKIN       ".?AVInstance@BSSkin@@"
#define RTTI_BONE_DATA  ".?AVBoneData@BSSkin@@"

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
static unsigned g_normalOffset = 0x1E0;   /* controller: support normal (0 = no ground, no tilt) */
static unsigned g_stateOffset = 0x2C0;    /* controller: Havok character state (0 = don't read) */
static float g_smoothing = 0.12f;         /* seconds: how quickly the tilt follows the ground */
static char g_shapePrefix[64] = "CMB_BikeWorn";
enum { LAYOUT_UNKNOWN = -1, LAYOUT_FILE = 0, LAYOUT_TRANSPOSED = 1, LAYOUT_DISAGREE = 2 };
static int g_layoutSetting = LAYOUT_UNKNOWN;   /* Layout=auto */

static volatile bool g_dataReady;
static uintptr_t g_slopeGlobal, g_cameraGlobal;   /* TESGlobal * */
static uintptr_t g_tiltGlobal, g_groundGlobals[3];
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

/* Ground under the player. */
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
static float g_tiltN[3] = { 0.0f, 0.0f, 1.0f };   /* smoothed ground normal (world) */
static float g_tiltNow, g_tiltMax;      /* degrees: this frame, most this ride */
static LARGE_INTEGER g_qpcFrequency, g_lastFrameTime;
static int g_walkBudget;
static uintptr_t g_refused[8];          /* skins found unfit: not looked at again */
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
	GetPrivateProfileStringA("Tilt", "NormalOffset", "0x1E0", value, sizeof(value), ini);
	g_normalOffset = (unsigned)strtoul(value, NULL, 0) & ~3u;
	GetPrivateProfileStringA("Tilt", "StateOffset", "0x2C0", value, sizeof(value), ini);
	g_stateOffset = (unsigned)strtoul(value, NULL, 0) & ~3u;
	GetPrivateProfileStringA("Tilt", "Smoothing", "0.12", value, sizeof(value), ini);
	g_smoothing = strtof(value, NULL);
	if (!(g_smoothing >= 0.0f && g_smoothing <= 2.0f))
		g_smoothing = 0.12f;
	GetPrivateProfileStringA("Tilt", "Shapes", "CMB_BikeWorn", g_shapePrefix, sizeof(g_shapePrefix), ini);
	GetPrivateProfileStringA("Tilt", "Layout", "auto", value, sizeof(value), ini);
	g_layoutSetting = _stricmp(value, "file") == 0 ? LAYOUT_FILE : _stricmp(value, "transposed") == 0 ? LAYOUT_TRANSPOSED : LAYOUT_UNKNOWN;
	Log("settings: %s", ini);
	Log("  slope: Target=%s SlopeOffset=0x%X%s SlopeUnit=%s ExpectedDegrees=%g  Probe=%d IntervalMs=%lu DumpPointers=%d",
	    g_target == TARGET_PROXY ? "proxy" : "controller", g_slopeOffset, g_slopeOffset ? "" : " (unknown: reading only)",
	    g_unit == UNIT_RADIANS ? "radians" : g_unit == UNIT_DEGREES ? "degrees" : "cosine", g_expectedDegrees,
	    g_probe, (unsigned long)g_interval, g_dumpPointerCount);
	Log("  camera: Setting=%s", g_cameraSettingName);
	Log("  tilt: NormalOffset=0x%X StateOffset=0x%X Smoothing=%g Shapes=%s Layout=%s", g_normalOffset, g_stateOffset,
	    g_smoothing, g_shapePrefix, g_layoutSetting == LAYOUT_FILE ? "file" : g_layoutSetting == LAYOUT_TRANSPOSED ? "transposed" : "auto");
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
	g_slopeGlobal = FindGlobal(prefix, shift, SLOPE_GLOBAL_ID, SLOPE_GLOBAL_EDITOR_ID);
	g_cameraGlobal = FindGlobal(prefix, shift, CAMERA_GLOBAL_ID, CAMERA_GLOBAL_EDITOR_ID);
	g_tiltGlobal = FindGlobal(prefix, shift, TILT_GLOBAL_ID, TILT_GLOBAL_EDITOR_ID);
	static const char *ground[3] = { "CMB_GroundNormalX", "CMB_GroundNormalY", "CMB_GroundNormalZ" };
	for (int i = 0; i < 3; i++)
		g_groundGlobals[i] = FindGlobal(prefix, shift, GROUND_GLOBAL_ID + (uint32_t)i, ground[i]);
	if (!g_groundGlobals[0] || !g_groundGlobals[1] || !g_groundGlobals[2])
		g_groundGlobals[0] = g_groundGlobals[1] = g_groundGlobals[2] = 0;
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

/* The BoneData of every bike shape under `node` (the player's 3D). */
static void FindSkins(uintptr_t node, int depth, uintptr_t found[], const char *names[], int *count)
{
	if (depth > 16 || --g_walkBudget < 0 || *count >= MAX_SKINS)
		return;
	if (IsA(node, RTTI_GEOMETRY)) {
		const char *name = ObjectName(node);
		size_t n = strlen(g_shapePrefix);
		if (!name || !n || _strnicmp(name, g_shapePrefix, n) != 0)
			return;
		uintptr_t skin = ReadPtr(node + OFF_SKIN_INSTANCE);
		uintptr_t data = skin && IsA(skin, RTTI_SKIN) ? ReadPtr(skin + OFF_SKIN_BONE_DATA) : 0;
		if (!data || !IsA(data, RTTI_BONE_DATA))
			return;
		for (int i = 0; i < *count; i++)
			if (found[i] == data)
				return;
		names[*count] = name;
		found[(*count)++] = data;
		return;
	}
	if (!IsA(node, RTTI_NODE) || !Accessible(node + OFF_CHILDREN, 0x10, false))
		return;
	uintptr_t children = ReadPtr(node + OFF_CHILDREN);
	unsigned used = *(const uint16_t *)(node + OFF_CHILDREN_USED);
	unsigned cap = *(const uint16_t *)(node + OFF_CHILDREN_CAP);
	if (!children || used > cap || !Accessible(children, used * 8u, false))
		return;
	for (unsigned i = 0; i < used; i++) {
		uintptr_t child = ((const uintptr_t *)children)[i];
		if (child)
			FindSkins(child, depth + 1, found, names, count);
	}
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

static void LetGoAll(const char *why)
{
	while (g_skinCount)
		LetGo(g_skinCount - 1, why);
	g_tiltN[0] = g_tiltN[1] = 0.0f;
	g_tiltN[2] = 1.0f;
	g_lastFrameTime.QuadPart = 0;
	g_tiltMax = g_tiltNow = 0.0f;
}

/* Every IntervalMs while the bike may tilt: hold the skins of the bike the player wears
 * now, let go of any that are gone (taken off, or the 3D was rebuilt). */
static void SyncSkins(uintptr_t player)
{
	uintptr_t found[MAX_SKINS];
	const char *names[MAX_SKINS];
	int count = 0;
	uintptr_t loaded = player ? ReadPtr(player + OFF_REFR_LOADED) : 0;
	uintptr_t root = loaded ? ReadPtr(loaded + OFF_LOADED_ROOT) : 0;
	g_walkBudget = 4000;
	if (root)
		FindSkins(root, 0, found, names, &count);
	for (int i = g_skinCount - 1; i >= 0; i--) {
		bool still = false;
		for (int j = 0; j < count; j++)
			still |= found[j] == g_skins[i].boneData;
		if (!still)
			LetGo(i, "no longer worn");
	}
	for (int j = 0; j < count && g_skinCount < MAX_SKINS; j++) {
		bool held = false;
		for (int i = 0; i < g_skinCount; i++)
			held |= g_skins[i].boneData == found[j];
		if (!held && !Refused(found[j]))
			HoldSkin(found[j], names[j]);
	}
	if (g_layoutFromRoot == LAYOUT_UNKNOWN && player) {
		g_layoutFromRoot = LayoutFromRoot(player);
		if (g_layoutFromRoot != LAYOUT_UNKNOWN)
			Log("tilt: the player's 3D says the game's matrices are %s", LayoutName(g_layoutFromRoot));
	}
	DecideLayout();
}

/* The rotation (x' = R x, row-major 3x3) that tips straight up over to `up` (in the
 * rider's frame: x right, y forward, z up), by at most `maxRadians`. Returns the angle. */
static float TiltRotation(const float up[3], float maxRadians, float R[9])
{
	float angle = acosf(up[2] > 1.0f ? 1.0f : up[2]);
	float ax = -up[1], ay = up[0];   /* axis: (0,0,1) x up, level */
	float len = sqrtf(ax * ax + ay * ay);
	if (angle > maxRadians)
		angle = maxRadians;
	if (len < 1e-6f || angle < 1e-5f) {
		static const float identity[9] = { 1, 0, 0, 0, 1, 0, 0, 0, 1 };
		memcpy(R, identity, sizeof(identity));
		return 0.0f;
	}
	ax /= len;
	ay /= len;
	float c = cosf(angle), s = sinf(angle), t = 1.0f - c;
	/* Rodrigues, axis (ax, ay, 0). */
	R[0] = c + t * ax * ax;  R[1] = t * ax * ay;      R[2] = s * ay;
	R[3] = t * ax * ay;      R[4] = c + t * ay * ay;  R[5] = -s * ax;
	R[6] = -s * ay;          R[7] = s * ax;           R[8] = c;
	return angle;
}

/* Every frame while riding: ease towards the ground under the player and turn the
 * bike's mesh by that before it goes onto its bone. */
static void FrameTilt(void)
{
	float maxDegrees = GlobalValue(g_tiltGlobal);
	if (!g_skinCount || !(maxDegrees > 0.0f) || (g_layout != LAYOUT_FILE && g_layout != LAYOUT_TRANSPOSED))
		return;
	uintptr_t player = Player();
	if (!player || !Accessible(player + OFF_REFR_HEADING, 4, false))
		return;
	LARGE_INTEGER now;
	QueryPerformanceCounter(&now);
	float dt = g_lastFrameTime.QuadPart && g_qpcFrequency.QuadPart
	           ? (float)(now.QuadPart - g_lastFrameTime.QuadPart) / (float)g_qpcFrequency.QuadPart : 0.0f;
	g_lastFrameTime = now;
	if (!(dt >= 0.0f) || dt > 0.25f)
		dt = 0.25f;

	float target[3] = { 0.0f, 0.0f, 1.0f }, n[3];
	bool airborne;
	if (ReadGround(FindController(player, false), n, &airborne) && !airborne)
		memcpy(target, n, sizeof(target));
	float k = g_smoothing > 0.0f ? 1.0f - expf(-dt / g_smoothing) : 1.0f;
	float len = 0.0f;
	for (int i = 0; i < 3; i++) {
		g_tiltN[i] += (target[i] - g_tiltN[i]) * k;
		len += g_tiltN[i] * g_tiltN[i];
	}
	len = sqrtf(len);
	if (!(len > 0.5f)) {
		g_tiltN[0] = g_tiltN[1] = 0.0f;
		g_tiltN[2] = len = 1.0f;
	}
	for (int i = 0; i < 3; i++)
		g_tiltN[i] /= len;

	/* Into the rider's frame: heading h, forward (sin h, cos h), right (cos h, -sin h). */
	float h = *(const float *)(player + OFF_REFR_HEADING);
	if (!isfinite(h))
		return;
	float sh = sinf(h), ch = cosf(h);
	float up[3] = { g_tiltN[0] * ch - g_tiltN[1] * sh, g_tiltN[0] * sh + g_tiltN[1] * ch, g_tiltN[2] };
	float R[9];
	float angle = TiltRotation(up, maxDegrees / 57.29578f, R);
	g_tiltNow = angle * 57.29578f;
	if (g_tiltNow > g_tiltMax) {
		if (g_tiltMax < 5.0f && g_tiltNow >= 5.0f)
			Log("tilt: the bike follows the ground (%.1f deg now)", g_tiltNow);
		g_tiltMax = g_tiltNow;
	}

	for (int k2 = 0; k2 < g_skinCount; k2++) {
		const HeldSkin *hs = &g_skins[k2];
		for (int b = 0; b < hs->count; b++) {
			const uint8_t *orig = hs->original[b];
			uint8_t *live = (uint8_t *)(hs->bones + (uintptr_t)b * BONE_SIZE);
			const float *o = (const float *)(orig + OFF_BONE_ROT);
			float A[9], B[9];
			for (int i = 0; i < 3; i++)
				for (int j = 0; j < 3; j++)
					A[i * 3 + j] = g_layout == LAYOUT_FILE ? o[i * 4 + j] : o[j * 4 + i];
			/* Mesh -> bone after the turn: B = A R. */
			for (int i = 0; i < 3; i++)
				for (int j = 0; j < 3; j++)
					B[i * 3 + j] = A[i * 3] * R[j] + A[i * 3 + 1] * R[3 + j] + A[i * 3 + 2] * R[6 + j];
			float *w = (float *)(live + OFF_BONE_ROT);
			for (int i = 0; i < 3; i++)
				for (int j = 0; j < 3; j++)
					w[i * 4 + j] = g_layout == LAYOUT_FILE ? B[i * 3 + j] : B[j * 3 + i];
			/* The culling sphere (bone space) turns about the mesh origin, which the bone
			 * sees at the transform's translation: grow it by the most its centre moves. */
			const float *centre = (const float *)orig, *pos = (const float *)(orig + OFF_BONE_POS);
			float dx = centre[0] - pos[0], dy = centre[1] - pos[1], dz = centre[2] - pos[2];
			float radius = *(const float *)(orig + OFF_BONE_RADIUS);
			*(float *)(live + OFF_BONE_RADIUS) = radius + 2.0f * sqrtf(dx * dx + dy * dy + dz * dz) * sinf(angle * 0.5f);
		}
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

	float degrees = GlobalValue(g_slopeGlobal);
	float tilt = GlobalValue(g_tiltGlobal);
	bool riding = degrees > 0.0f || GlobalValue(g_cameraGlobal) > 0.0f || tilt > 0.0f;
	bool scan = (int32_t)(now - g_nextScan) >= 0;
	uintptr_t ctrl, proxy;
	uintptr_t target = FindChain(scan, &ctrl, &proxy);

	/* The ground under the player, for the controller script to park the bike on;
	 * Z = 0 while they aren't on the ground (or it can't be told). */
	float n[3];
	bool airborne;
	if (g_groundGlobals[0]) {
		if (ReadGround(ctrl, n, &airborne) && !airborne)
			for (int i = 0; i < 3; i++)
				SetGlobal(g_groundGlobals[i], n[i]);
		else
			SetGlobal(g_groundGlobals[2], 0.0f);
	}

	if (tilt > 0.0f)
		SyncSkins(Player());
	else if (g_skinCount)
		LetGoAll("got off");

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
		memset(g_refused, 0, sizeof(g_refused));
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
