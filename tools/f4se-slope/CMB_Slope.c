/*
 * CMB_Slope: Commonwealth Motorbike's F4SE plugin. Lets the rider climb steeper
 * slopes than a person on foot.
 *
 * Fallout 4 1.11.240 with F4SE 0.7.9 only: the game addresses and structure offsets
 * below come from F4SE 0.7.9's own source for that runtime, and F4SE only loads the
 * plugin on the game versions listed in F4SEPlugin_Version.
 *
 * How it works. How steep a slope a character can walk up is a limit inside the
 * Havok character proxy that moves the player (hknpCharacterProxy, kept as the
 * cosine of the angle). Nothing in Papyrus reaches it. Every frame the plugin gets a
 * call on the game's main thread (F4SE's permanent task) and, a few times a second:
 *
 *   1. reads the global CMB_SlopeLive from CommonwealthMotorbike.esp: the controller
 *      script sets it to the riding slope limit in degrees while you ride, 0 otherwise;
 *   2. finds the player's character controller and its Havok proxy. Not by fixed
 *      offsets: it follows the player's process data and recognises each object by its
 *      C++ type information (RTTI), checking every pointer before reading it;
 *   3. while riding, lowers the proxy's slope limit cosine to cos(CMB_SlopeLive) (only
 *      ever steeper than the game's own), and puts the original back afterwards.
 *
 * Where in the proxy the limit lives isn't known from F4SE's source, so it comes from
 * CMB_Slope.ini (ProxySlopeOffset). Until that's set the plugin only reads: it logs
 * the proxy's layout, any slope-related INI settings and Havok's own reflection data
 * for "maxSlope" to Documents\My Games\Fallout4\F4SE\CMB_Slope.log, which is how the
 * offset gets found.
 *
 * Built with MinGW-w64 (tools/f4se-slope/build.sh). Plain C: F4SE's plugin interface
 * is plain structs and function pointers, and the one C++ object F4SE calls into (the
 * task) is a vtable we lay out by hand.
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

#define PLUGIN_VERSION 1
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
#define LIVE_GLOBAL_ID        0x82Au        /* CMB_SlopeLive, set by CMB_ControllerScript */
#define LIVE_GLOBAL_EDITOR_ID "CMB_SlopeLive"

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

static int g_probe = 1;                 /* log layouts until the offset is known */
static unsigned g_proxySlopeOffset;     /* from the INI; 0 = unknown, read only */
enum { UNIT_COSINE, UNIT_RADIANS, UNIT_DEGREES };
static int g_unit = UNIT_COSINE;        /* how the proxy stores the limit */
static DWORD g_interval = 100;          /* ms between checks */

static volatile bool g_dataReady;
static uintptr_t g_liveGlobal;          /* TESGlobal * of CMB_SlopeLive */
static DWORD g_lastGlobalTry;
static bool g_globalMissingLogged;

/* The chain to the proxy, as found last time (offsets, so it's re-read every check). */
static int g_ctrlWhere = -1;            /* 0 = process data, 1 = process, 2 = player */
static int g_ctrlOff = -1;
static int g_proxyOff1 = -1, g_proxyOff2 = -1;
static uintptr_t g_loggedProxy;         /* the proxy last dumped to the log */
static DWORD g_nextScan;                /* full searches are slow: not more often than this */
static bool g_ctrlMissingLogged, g_proxyMissingLogged;

/* What we changed. */
static bool g_applied;
static uintptr_t g_appliedProxy;
static float g_originalCos, g_writtenCos;
static bool g_revertLogged, g_badValueLogged;

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
	char ini[MAX_PATH], value[64];
	GetModuleFileNameA(g_module, ini, sizeof(ini));
	char *dot = strrchr(ini, '.');
	if (!dot)
		return;
	strcpy(dot, ".ini");
	GetPrivateProfileStringA("Slope", "ProxySlopeOffset", "", value, sizeof(value), ini);
	g_proxySlopeOffset = (unsigned)strtoul(value, NULL, 0);
	GetPrivateProfileStringA("Slope", "ProxySlopeUnit", "cosine", value, sizeof(value), ini);
	g_unit = _stricmp(value, "radians") == 0 ? UNIT_RADIANS : _stricmp(value, "degrees") == 0 ? UNIT_DEGREES : UNIT_COSINE;
	g_probe = (int)GetPrivateProfileIntA("Slope", "Probe", 1, ini);
	g_interval = (DWORD)GetPrivateProfileIntA("Slope", "IntervalMs", 100, ini);
	if (g_interval < 16)
		g_interval = 16;
	Log("settings: %s  ProxySlopeOffset=0x%X%s  ProxySlopeUnit=%s  Probe=%d  IntervalMs=%lu", ini, g_proxySlopeOffset,
	    g_proxySlopeOffset ? "" : " (unknown: reading only)",
	    g_unit == UNIT_RADIANS ? "radians" : g_unit == UNIT_DEGREES ? "degrees" : "cosine", g_probe, (unsigned long)g_interval);
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

static void FindLiveGlobal(void)
{
	uint32_t prefix, shift;
	if (!FindOurPlugin(&prefix, &shift)) {
		if (!g_globalMissingLogged)
			Log("%s not found in the load order: nothing to do", ESP_NAME);
		g_globalMissingLogged = true;
		return;
	}
	uint32_t id = prefix | (shift == 12 ? (LIVE_GLOBAL_ID & 0xFFFu) : LIVE_GLOBAL_ID);
	uintptr_t form = ((LookupFormByID_t)(g_base + RVA_LOOKUP_FORM))(id);
	if (!form || !Accessible(form, 0x38, false) || *(const uint8_t *)(form + OFF_FORM_TYPE) != FORM_TYPE_GLOB) {
		if (!g_globalMissingLogged)
			Log("form %08X isn't a global (an older %s?): nothing to do", id, ESP_NAME);
		g_globalMissingLogged = true;
		return;
	}
	uintptr_t edid = ReadPtr(form + OFF_GLOBAL_EDITOR_ID);
	if (edid && Accessible(edid, sizeof(LIVE_GLOBAL_EDITOR_ID), false) &&
	    strcmp((const char *)edid, LIVE_GLOBAL_EDITOR_ID) != 0) {
		Log("form %08X is the global '%.40s', not %s: nothing to do", id, (const char *)edid, LIVE_GLOBAL_EDITOR_ID);
		g_globalMissingLogged = true;
		return;
	}
	g_liveGlobal = form;
	Log("found %s (%08X)", LIVE_GLOBAL_EDITOR_ID, id);
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

static float Steeper(float a, float b)
{
	/* A smaller cosine, or a bigger angle, lets you climb more. */
	return g_unit == UNIT_COSINE ? (a < b ? a : b) : (a > b ? a : b);
}

static void Restore(uintptr_t proxy)
{
	if (!g_applied)
		return;
	if (proxy && proxy == g_appliedProxy) {
		float *slot = (float *)(proxy + g_proxySlopeOffset);
		if (Accessible((uintptr_t)slot, 4, true) && *slot == g_writtenCos) {
			*slot = g_originalCos;
			Log("slope limit back to %.1f deg", ToDegrees(g_originalCos));
		}
	}
	g_applied = false;
	g_appliedProxy = 0;
}

static void Tick(void)
{
	if (!g_dataReady)
		return;
	if (!g_liveGlobal) {
		DWORD now = GetTickCount();
		if (g_globalMissingLogged || now - g_lastGlobalTry < 2000)
			return;
		g_lastGlobalTry = now;
		FindLiveGlobal();
		if (!g_liveGlobal)
			return;
	}
	float degrees = *(const float *)(g_liveGlobal + OFF_GLOBAL_VALUE);

	DWORD now = GetTickCount();
	bool scan = (int32_t)(now - g_nextScan) >= 0;
	uintptr_t player = Player();
	uintptr_t ctrl = player ? FindController(player, scan) : 0;
	uintptr_t proxy = ctrl ? FindProxy(ctrl, scan) : 0;
	if (!proxy) {
		/* Loading, or the controller is being rebuilt. Keep what we changed on record:
		 * if the same proxy comes back it still has our value, and the original is
		 * still the one to restore. A different proxy (checked below) starts afresh. */
		if (scan && player) {
			g_nextScan = now + 3000;
			if (!ctrl && !g_ctrlMissingLogged) {
				g_ctrlMissingLogged = true;
				Log("no character controller found near the player (yet); trying every 3 s");
			} else if (ctrl && !g_proxyMissingLogged) {
				g_proxyMissingLogged = true;
				Log("controller found but no %s under it; what it points to:", RTTI_PROXY);
				DumpObject("character controller", ctrl, 0x600);
			}
		}
		return;
	}

	if (g_probe && proxy != g_loggedProxy && (g_proxySlopeOffset == 0 || g_loggedProxy == 0)) {
		g_loggedProxy = proxy;
		DumpObject("Havok proxy", proxy, 0x300);
		DumpObject("character controller", ctrl, 0x600);
	}
	if (!g_proxySlopeOffset)
		return;

	if (g_applied && proxy != g_appliedProxy) {
		/* A different proxy (load, cell change): it has the game's own limit. */
		g_applied = false;
		g_appliedProxy = 0;
	}
	float *slot = (float *)(proxy + g_proxySlopeOffset);
	if (!Accessible((uintptr_t)slot, 4, true))
		return;

	if (degrees > 0.0f && degrees < 89.0f) {
		float want = FromDegrees(degrees);
		if (!g_applied) {
			float current = *slot;
			if (!Plausible(current)) {
				if (!g_badValueLogged)
					Log("proxy+0x%X holds %g, not a slope limit in the configured unit: wrong ProxySlopeOffset or ProxySlopeUnit? Not touching it.",
					    g_proxySlopeOffset, current);
				g_badValueLogged = true;
				return;
			}
			g_originalCos = current;
			g_writtenCos = Steeper(want, current);   /* only ever steeper than the game's */
			g_applied = true;
			g_appliedProxy = proxy;
			g_revertLogged = false;
			Log("riding: slope limit %.1f -> %.1f deg", ToDegrees(current), ToDegrees(g_writtenCos));
			*slot = g_writtenCos;
		} else if (*slot != g_writtenCos) {
			if (!g_revertLogged)
				Log("the game set the slope limit back to %.1f deg; setting it again", ToDegrees(*slot));
			g_revertLogged = true;
			*slot = g_writtenCos;
		}
	} else {
		Restore(proxy);
	}
}

static void *Task_Destroy(Task *self, unsigned flags)
{
	(void)flags;
	return self;
}

static void Task_Run(Task *self)
{
	(void)self;
	DWORD now = GetTickCount();
	if (now - g_lastTick < g_interval)
		return;
	g_lastTick = now;
	Tick();
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
		/* Fresh objects: find the chain again, and log the new proxy once. */
		g_applied = false;
		g_appliedProxy = 0;
		g_loggedProxy = 0;
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
