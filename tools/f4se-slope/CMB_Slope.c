/*
 * CMB_Slope: Commonwealth Motorbike's F4SE plugin. While you ride it lets you climb
 * steeper slopes than on foot, and moves the third-person camera farther back.
 *
 * Fallout 4 1.11.240 with F4SE 0.7.9 only: the game addresses and structure offsets
 * below come from F4SE 0.7.9's own source for that runtime, and F4SE only loads the
 * plugin on the game versions listed in F4SEPlugin_Version.
 *
 * The controller script tells it when you ride through two globals of
 * CommonwealthMotorbike.esp: CMB_SlopeLive (the steepest slope in degrees while riding,
 * 0 otherwise) and CMB_CameraLive (the camera distance while riding, 0 otherwise).
 * F4SE calls the plugin every frame on the game's main thread (a permanent task):
 *
 *   Slope: how steep a slope a character can walk up is a limit kept by its character
 *   controller and Havok proxy; nothing in Papyrus reaches it. The plugin finds the
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
 * With Probe=1 it also logs (Documents\My Games\Fallout4\F4SE\CMB_Slope.log) the
 * layout of the controller, the proxy and the objects listed in DumpPointers, then on
 * getting on, 1 and 3 seconds into the ride and on getting off, what changed: that's
 * how the slope limit's place is found.
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

#define PLUGIN_VERSION 2
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

/* --- Our side --- */
#define ESP_NAME              "CommonwealthMotorbike.esp"
#define SLOPE_GLOBAL_ID       0x82Au        /* CMB_SlopeLive, set by CMB_ControllerScript */
#define SLOPE_GLOBAL_EDITOR_ID "CMB_SlopeLive"
#define CAMERA_GLOBAL_ID      0x82Bu        /* CMB_CameraLive, likewise */
#define CAMERA_GLOBAL_EDITOR_ID "CMB_CameraLive"
#define CAMERA_SETTING        "fVanityModeMaxDist:Camera"

/* RTTI names (MSVC mangled) of the objects we look for. */
#define RTTI_PLAYER     ".?AVPlayerCharacter@@"
#define RTTI_CONTROLLER ".?AVbhkCharacterController@@"
#define RTTI_PROXY      ".?AVhknpCharacterProxy@@"

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
static int g_probe = 1;
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

static volatile bool g_dataReady;
static uintptr_t g_slopeGlobal, g_cameraGlobal;   /* TESGlobal * */
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
static DWORD g_lastTick;

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
	g_probe = (int)GetPrivateProfileIntA("Slope", "Probe", 1, ini);
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
	Log("settings: %s", ini);
	Log("  slope: Target=%s SlopeOffset=0x%X%s SlopeUnit=%s ExpectedDegrees=%g  Probe=%d IntervalMs=%lu DumpPointers=%d",
	    g_target == TARGET_PROXY ? "proxy" : "controller", g_slopeOffset, g_slopeOffset ? "" : " (unknown: reading only)",
	    g_unit == UNIT_RADIANS ? "radians" : g_unit == UNIT_DEGREES ? "degrees" : "cosine", g_expectedDegrees,
	    g_probe, (unsigned long)g_interval, g_dumpPointerCount);
	Log("  camera: Setting=%s", g_cameraSettingName);
}

/* ------------------------------------------------------------------------- */
/* Safe memory access                                                        */
/* ------------------------------------------------------------------------- */

static bool Accessible(uintptr_t p, size_t n, bool write)
{
	if (p < 0x10000 || p > 0x7FFFFFFEFFFFull)
		return false;
	MEMORY_BASIC_INFORMATION mbi;
	if (VirtualQuery((const void *)p, &mbi, sizeof(mbi)) != sizeof(mbi))
		return false;
	if (mbi.State != MEM_COMMIT || (mbi.Protect & (PAGE_GUARD | PAGE_NOACCESS)))
		return false;
	DWORD ok = write ? (PAGE_READWRITE | PAGE_EXECUTE_READWRITE)
	                 : (PAGE_READONLY | PAGE_READWRITE | PAGE_WRITECOPY | PAGE_EXECUTE_READ |
	                    PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY);
	if (!(mbi.Protect & ok))
		return false;
	return p + n <= (uintptr_t)mbi.BaseAddress + mbi.RegionSize;
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
	g_globalsMissingLogged = true;   /* found or not, don't look again */
}

static float GlobalValue(uintptr_t global)
{
	return global ? *(const float *)(global + OFF_GLOBAL_VALUE) : 0.0f;
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
/* Every frame / every IntervalMs                                            */
/* ------------------------------------------------------------------------- */

static void Tick(DWORD now)
{
	if (!g_slopeGlobal && !g_cameraGlobal) {
		if (g_globalsMissingLogged || now - g_lastGlobalTry < 2000)
			return;
		g_lastGlobalTry = now;
		FindGlobals();
		if (!g_slopeGlobal && !g_cameraGlobal)
			return;
	}
	UpdateCamera();

	float degrees = GlobalValue(g_slopeGlobal);
	bool riding = degrees > 0.0f || GlobalValue(g_cameraGlobal) > 0.0f;
	bool scan = (int32_t)(now - g_nextScan) >= 0;
	uintptr_t ctrl, proxy;
	uintptr_t target = FindChain(scan, &ctrl, &proxy);

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

/* Between full checks, while riding: keep the limit written (cheap: cached chain only). */
static void Frame(void)
{
	if (!g_applied)
		return;
	float degrees = GlobalValue(g_slopeGlobal);
	if (!(degrees > 0.0f && degrees < 89.0f))
		return;
	uintptr_t target = FindChain(false, NULL, NULL);
	if (target && target == g_appliedTarget)
		ApplySlope(target, degrees);
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
	if (now - g_lastTick < g_interval) {
		Frame();
		return;
	}
	g_lastTick = now;
	Tick(now);
}

static void *g_taskVtbl[2] = { (void *)Task_Destroy, (void *)Task_Run };
static Task g_task = { g_taskVtbl };

static void OnF4SEMessage(F4SEMessage *msg)
{
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
