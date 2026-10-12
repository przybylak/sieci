/*
 * Test harness for CMB_Slope.dll: a stand-in for Fallout 4 1.11.240 and F4SE 0.7.9,
 * run under Wine (tools/f4se-slope/test/run.sh).
 *
 * The executable's image is made big enough (a large zero-filled section) that the
 * game addresses the plugin uses (player, data handler, LookupFormByID, INI settings)
 * fall inside it. Fake objects get MSVC-style RTTI (complete object locators, type
 * descriptors, class hierarchies) built inside the image, the way the game's are, so
 * the plugin's search and type checks run exactly as they would in the game. F4SE's
 * side is a fake interface that records the permanent task and the message listener.
 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define RVA_PLAYER            0x032DD370u
#define RVA_DATA_HANDLER      0x030E7100u
#define RVA_LOOKUP_FORM       0x00311B80u
#define RVA_INI_SETTINGS      0x0344B4B8u
#define RVA_INI_PREF_SETTINGS 0x0339FAE0u
#define RVA_RTTI_AREA         0x01000000u  /* where the fake RTTI goes, clear of the above */

#define PROXY_SLOPE_OFFSET    0x9C
#define CTRL_SLOPE_OFFSET     0x418        /* cos 47 deg, as in the real game (test 5) */
#define LIGHT_INDEX           5
#define SLOPE_GLOBAL_FORMID   (0xFE000000u | (LIGHT_INDEX << 12) | 0x82Au)
#define CAMERA_GLOBAL_FORMID  (0xFE000000u | (LIGHT_INDEX << 12) | 0x82Bu)
#define COS47                 0.68199836f

static uint8_t g_space[0x3600000];          /* the "game image" (in .bss) */
static uintptr_t g_base;
static uintptr_t g_rttiNext;
static int g_failures;

#define CHECK(cond, ...) do { if (cond) { printf("  ok   "); } else { printf("  FAIL "); g_failures++; } \
	printf(__VA_ARGS__); printf("\n"); } while (0)

/* --- MSVC RTTI, built inside the image --------------------------------------- */

static uintptr_t RttiAlloc(size_t n)
{
	uintptr_t p = (g_rttiNext + 15) & ~(uintptr_t)15;
	g_rttiNext = p + n;
	return p;
}

static uint32_t Rva(uintptr_t p) { return (uint32_t)(p - g_base); }

typedef struct { uint32_t td, nContained, mdisp, pdisp, vdisp, attr, chd; } BaseClassDescriptor;

/* A class with the given names, most-derived first; returns a vtable (first slot after the COL pointer). */
static void **MakeClass(const char **names, int n)
{
	uint32_t tds[16];
	for (int i = 0; i < n; i++) {
		uintptr_t td = RttiAlloc(16 + strlen(names[i]) + 1);
		strcpy((char *)(td + 16), names[i]);
		tds[i] = Rva(td);
	}
	uintptr_t chd = RttiAlloc(16);
	uintptr_t arr = RttiAlloc(4u * n);
	for (int i = 0; i < n; i++) {
		BaseClassDescriptor *b = (BaseClassDescriptor *)RttiAlloc(sizeof(BaseClassDescriptor));
		b->td = tds[i];
		b->chd = Rva(chd);
		((uint32_t *)arr)[i] = Rva((uintptr_t)b);
	}
	uint32_t *h = (uint32_t *)chd;
	h[0] = 0; h[1] = 0; h[2] = (uint32_t)n; h[3] = Rva(arr);
	uint32_t *col = (uint32_t *)RttiAlloc(24);
	col[0] = 1; col[1] = 0; col[2] = 0; col[3] = tds[0]; col[4] = Rva(chd); col[5] = Rva((uintptr_t)col);
	void **vt = (void **)RttiAlloc(8 * 6);
	vt[0] = col;
	return vt + 1;
}

static void *NewObject(void **vtbl, size_t size)
{
	uint8_t *o = (uint8_t *)VirtualAlloc(NULL, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	*(void ***)o = vtbl;
	return o;
}

/* --- Fake game objects --------------------------------------------------------- */

static uint8_t *g_global;      /* TESGlobal CMB_SlopeLive */
static uint8_t *g_cameraGlobal; /* TESGlobal CMB_CameraLive */
static uint8_t *g_controller;
static uint8_t *g_proxy;
static uint8_t *g_cameraSetting;
static void **g_vtProxy, **g_vtWrapper, **g_vtCtrl;

static float *Slope(void) { return (float *)(g_controller + CTRL_SLOPE_OFFSET); }
static float *ProxySlope(void) { return (float *)(g_proxy + PROXY_SLOPE_OFFSET); }
static float *CameraDist(void) { return (float *)(g_cameraSetting + 0x08); }
static void SetLive(float degrees) { *(float *)(g_global + 0x30) = degrees; }
static void SetCamera(float distance) { *(float *)(g_cameraGlobal + 0x30) = distance; }

static uintptr_t FakeLookupFormByID(uint32_t id)
{
	return id == SLOPE_GLOBAL_FORMID ? (uintptr_t)g_global : id == CAMERA_GLOBAL_FORMID ? (uintptr_t)g_cameraGlobal : 0;
}

static uint8_t *NewProxy(float cosine)
{
	uint8_t *proxy = (uint8_t *)NewObject(g_vtProxy, 0x400);
	/* Some plausible neighbours: friction, keep distance, strength, mass. */
	*(float *)(proxy + 0x80) = 0.0f;
	*(float *)(proxy + 0x84) = 0.0f;
	*(float *)(proxy + 0x90) = 0.05f;
	*(float *)(proxy + 0x94) = 0.1f;
	*(float *)(proxy + 0x98) = 1000.0f;
	*(float *)(proxy + PROXY_SLOPE_OFFSET) = cosine;
	*(float *)(proxy + 0xA0) = 1.0f;
	return proxy;
}

static void BuildGame(void)
{
	static const char *player[] = { ".?AVPlayerCharacter@@", ".?AVActor@@", ".?AVTESObjectREFR@@", ".?AVTESForm@@" };
	static const char *ctrl[] = { ".?AVbhkCharProxyController@@", ".?AVbhkCharacterController@@", ".?AVhkbCharacterController@@" };
	static const char *wrapper[] = { ".?AVbhkCharacterProxy@@", ".?AVbhkSerializable@@", ".?AVNiObject@@" };
	static const char *proxy[] = { ".?AVhknpBSCharacterProxy@@", ".?AVhknpCharacterProxy@@", ".?AVhkReferencedObject@@" };
	static const char *decoy[] = { ".?AVBSAnimationGraphManager@@", ".?AVBSIntrusiveRefCounted@@" };

	g_rttiNext = g_base + RVA_RTTI_AREA;
	void **vtPlayer = MakeClass(player, 4);
	g_vtCtrl = MakeClass(ctrl, 3);
	void **vtCtrl = g_vtCtrl;
	g_vtWrapper = MakeClass(wrapper, 3);
	g_vtProxy = MakeClass(proxy, 3);
	void **vtDecoy = MakeClass(decoy, 2);

	uint8_t *pl = (uint8_t *)NewObject(vtPlayer, 0x1000);
	uint8_t *process = (uint8_t *)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	uint8_t *data = (uint8_t *)VirtualAlloc(NULL, 0x2000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	*(uint8_t **)(pl + 0x300) = process;
	*(uint8_t **)(process + 0x08) = data;
	*(void **)(data + 0x40) = NewObject(vtDecoy, 0x100);     /* something else first */
	*(uintptr_t *)(data + 0x48) = 0x12345678;                 /* junk that isn't a pointer */
	g_controller = (uint8_t *)NewObject(vtCtrl, 0x1000);
	*(uint8_t **)(data + 0x3E0) = g_controller;
	*(float *)(g_controller + 0x154) = 0.7257f;
	*(float *)(g_controller + CTRL_SLOPE_OFFSET) = COS47;
	*(float *)(g_controller + 0x424) = 0.4429f;
	uint8_t *stateManager = (uint8_t *)NewObject(vtDecoy, 0x200);
	*(float *)(stateManager + 0x40) = 3.0f;
	*(uint8_t **)(g_controller + 0x2B8) = stateManager;
	uint8_t *wrap = (uint8_t *)NewObject(g_vtWrapper, 0x100);
	*(uint8_t **)(g_controller + 0x470) = wrap;
	g_proxy = NewProxy(0.70710678f);                          /* 45 degrees */
	*(uint8_t **)(wrap + 0x20) = g_proxy;
	*(uintptr_t *)(g_base + RVA_PLAYER) = (uintptr_t)pl;

	/* Load order: two light plugins, ours second. */
	uint8_t *dh = (uint8_t *)VirtualAlloc(NULL, 0x2000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	uint8_t **mods = (uint8_t **)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	const char *names[2] = { "ccBGSFO4001-PipBoy(Black).esl", "CommonwealthMotorbike.esp" };
	for (int i = 0; i < 2; i++) {
		mods[i] = (uint8_t *)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
		strcpy((char *)(mods[i] + 0x70), names[i]);
		*(uint16_t *)(mods[i] + 0x372) = (uint16_t)(i == 1 ? LIGHT_INDEX : 1);
	}
	*(uint8_t ***)(dh + 0xFB0 + 0x28) = mods;
	*(uint32_t *)(dh + 0xFB0 + 0x28 + 0x10) = 2;
	*(uintptr_t *)(g_base + RVA_DATA_HANDLER) = (uintptr_t)dh;

	g_global = (uint8_t *)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	g_global[0x1A] = 11;
	*(uint32_t *)(g_global + 0x14) = SLOPE_GLOBAL_FORMID;
	*(const char **)(g_global + 0x20) = "CMB_SlopeLive";
	g_cameraGlobal = (uint8_t *)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	g_cameraGlobal[0x1A] = 11;
	*(uint32_t *)(g_cameraGlobal + 0x14) = CAMERA_GLOBAL_FORMID;
	*(const char **)(g_cameraGlobal + 0x20) = "CMB_CameraLive";

	/* LookupFormByID: a jump to ours at the game's address. */
	uint8_t *stub = (uint8_t *)(g_base + RVA_LOOKUP_FORM);
	DWORD old;
	VirtualProtect((void *)((uintptr_t)stub & ~0xFFFull), 0x2000, PAGE_EXECUTE_READWRITE, &old);
	stub[0] = 0x48; stub[1] = 0xB8;                          /* mov rax, imm64 */
	*(uint64_t *)(stub + 2) = (uint64_t)(uintptr_t)FakeLookupFormByID;
	stub[10] = 0xFF; stub[11] = 0xE0;                        /* jmp rax */
	FlushInstructionCache(GetCurrentProcess(), stub, 12);

	/* INI settings: a list with one slope-ish name. */
	static const char *settingNames[3] = { "fJumpHeightMin:Movement", "fVanityModeMaxDist:Camera", "iSize W:Display" };
	uint8_t *coll = (uint8_t *)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	uint8_t *prev = NULL;
	for (int i = 2; i >= 0; i--) {
		uint8_t *setting = (uint8_t *)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
		*(float *)(setting + 0x08) = i == 1 ? 150.0f : 50.0f + i;
		*(const char **)(setting + 0x10) = settingNames[i];
		if (i == 1)
			g_cameraSetting = setting;
		uint8_t *node = setting + 0x100;
		*(uint8_t **)node = setting;
		*(uint8_t **)(node + 8) = prev;
		prev = node;
	}
	*(uint8_t **)(coll + 0x120) = prev;
	*(uintptr_t *)(g_base + RVA_INI_SETTINGS) = (uintptr_t)coll;
}

/* Havok-style reflection table for the probe to find (name, class, enum, type, subtype,
 * cArraySize, flags, offset, attributes). */
typedef struct {
	const char *name; const void *cls; const void *enm;
	uint8_t type, subtype; int16_t cArraySize; uint16_t flags, offset; const void *attrs;
} HkClassMember;
__attribute__((used)) static const HkClassMember g_members[3] = {
	{ "characterStrength", 0, 0, 13, 0, 0, 0, 0x98, 0 },
	{ "maxSlope", 0, 0, 13, 0, 0, 0, 0x5C, 0 },
	{ "penetrationRecoverySpeed", 0, 0, 13, 0, 0, 0, 0x60, 0 },
};

/* --- Fake F4SE --------------------------------------------------------------------- */

typedef struct { const char *sender; uint32_t type, dataLen; void *data; } Message;
typedef void (*Listener)(Message *);
typedef struct { void **vtbl; } Task;

static Listener g_listener;
static Task *g_task;

static bool RegisterListener(uint32_t handle, const char *sender, Listener l) { (void)handle; (void)sender; g_listener = l; return true; }
static bool Dispatch(uint32_t a, uint32_t b, void *c, uint32_t d, const char *e) { (void)a; (void)b; (void)c; (void)d; (void)e; return true; }
static void *GetEventDispatcher(uint32_t id) { (void)id; return NULL; }
static void AddTask(void *t) { (void)t; }
static void AddTaskPermanent(void *t) { g_task = (Task *)t; }

static struct { uint32_t v; void *reg, *disp, *ged; } g_messaging = { 1, (void *)RegisterListener, (void *)Dispatch, (void *)GetEventDispatcher };
static struct { uint32_t v; void *add, *addUI, *addPermanent; } g_tasks = { 2, (void *)AddTask, (void *)AddTask, (void *)AddTaskPermanent };

static void *QueryInterface(uint32_t id) { return id == 1 ? (void *)&g_messaging : id == 5 ? (void *)&g_tasks : NULL; }
static uint32_t GetPluginHandle(void) { return 7; }

typedef struct {
	uint32_t f4seVersion, runtimeVersion, editorVersion, isEditor;
	void *(*QueryInterface)(uint32_t);
	uint32_t (*GetPluginHandle)(void);
	void *a, *b, *c;
} F4SEInterface;

static void Send(uint32_t type, uintptr_t data)
{
	Message m = { "F4SE", type, 1, (void *)data };
	g_listener(&m);
}

static void RunFrames(int ms)
{
	DWORD end = GetTickCount() + (DWORD)ms;
	while ((int32_t)(GetTickCount() - end) < 0) {
		((void (*)(Task *))g_task->vtbl[1])(g_task);
		Sleep(5);
	}
}

static bool Near(float a, float b) { return fabsf(a - b) < 1e-5f; }

int main(int argc, char **argv)
{
	const char *dllPath = argc > 1 ? argv[1] : "CMB_Slope.dll";
	int mode = argc > 2 ? atoi(argv[2]) : 0;   /* 0 = full test, 1 = probe only, 2 = wrong game version */
	g_base = (uintptr_t)GetModuleHandleA(NULL);
	if ((uintptr_t)g_space > g_base + 0x00300000u || (uintptr_t)g_space + sizeof(g_space) < g_base + RVA_INI_SETTINGS + 8) {
		printf("image layout doesn't cover the game addresses (g_space at +0x%llx)\n", (unsigned long long)((uintptr_t)g_space - g_base));
		return 2;
	}
	(void)g_members;
	BuildGame();

	HMODULE dll = LoadLibraryA(dllPath);
	if (!dll) { printf("can't load %s\n", dllPath); return 2; }
	const uint32_t *version = (const uint32_t *)GetProcAddress(dll, "F4SEPlugin_Version");
	bool (*load)(const F4SEInterface *) = (bool (*)(const F4SEInterface *))GetProcAddress(dll, "F4SEPlugin_Load");
	printf("version data and load function:\n");
	CHECK(version && load, "exports present");
	CHECK(version && version[0] == 1 && strcmp((const char *)(version + 2), "CMB_Slope") == 0, "F4SEPlugin_Version: data version 1, name CMB_Slope");
	const uint32_t *compatible = version + 2 + 128 + 2;
	CHECK(compatible[0] == 0x010B0F00u && compatible[1] == 0, "compatible with 1.11.240 only");

	F4SEInterface f4se = { 0x00070090u, mode == 2 ? 0x010B0DD0u : 0x010B0F00u, 0, 0, QueryInterface, GetPluginHandle, 0, 0, 0 };
	bool loaded = load(&f4se);
	if (mode == 2) {
		CHECK(!loaded && !g_task, "wrong game version: refuses to load, no task");
		return g_failures ? 1 : 0;
	}
	CHECK(loaded && g_task && g_listener, "loads, registers a permanent task and a listener");

	printf("before game data is ready:\n");
	SetLive(60.0f);
	SetCamera(300.0f);
	RunFrames(300);
	CHECK(Near(*Slope(), COS47) && Near(*CameraDist(), 150.0f), "nothing touched");

	Send(10, 1);   /* GameDataReady */
	SetLive(0.0f);
	SetCamera(0.0f);
	RunFrames(400);
	printf("not riding:\n");
	CHECK(Near(*Slope(), COS47), "slope limit still the game's (47 deg)");
	CHECK(Near(*CameraDist(), 150.0f), "camera still 150");
	*(float *)(g_controller + 0x154) = 0.8f;   /* something the game changes before getting on */

	if (mode == 1) {
		SetLive(60.0f);
		SetCamera(300.0f);
		RunFrames(400);
		CHECK(Near(*Slope(), COS47), "probe only (no offset): riding doesn't change the slope limit");
		CHECK(Near(*CameraDist(), 300.0f), "the camera still works (got %g)", *CameraDist());
		SetLive(0.0f);
		SetCamera(0.0f);
		RunFrames(400);
		CHECK(Near(*CameraDist(), 150.0f), "and goes back (got %g)", *CameraDist());
		return g_failures ? 1 : 0;
	}
	if (mode == 3) {
		*Slope() = 0.6427876f;   /* 50 deg: not what the INI expects */
		SetLive(60.0f);
		RunFrames(400);
		CHECK(Near(*Slope(), 0.6427876f), "unexpected value (50 deg, expected 47): not touched (got %f)", *Slope());
		return g_failures ? 1 : 0;
	}

	printf("riding, 60 deg, camera 300:\n");
	SetLive(60.0f);
	SetCamera(300.0f);
	RunFrames(400);
	CHECK(Near(*Slope(), 0.5f), "slope limit cos 60 = 0.5 (got %f)", *Slope());
	CHECK(Near(*ProxySlope(), 0.70710678f), "the proxy isn't touched (target is the controller)");
	CHECK(Near(*CameraDist(), 300.0f), "camera 300 (got %g)", *CameraDist());

	printf("the game resets the slope limit:\n");
	*Slope() = COS47;
	((void (*)(Task *))g_task->vtbl[1])(g_task);   /* one frame */
	CHECK(Near(*Slope(), 0.5f), "set again on the very next frame (got %f)", *Slope());

	printf("getting off:\n");
	SetLive(0.0f);
	SetCamera(0.0f);
	RunFrames(400);
	CHECK(Near(*Slope(), COS47), "slope back to 47 deg (got %f)", *Slope());
	CHECK(Near(*CameraDist(), 150.0f), "camera back to 150 (got %g)", *CameraDist());

	printf("player's own camera farther than the riding one:\n");
	*CameraDist() = 400.0f;
	SetCamera(300.0f);
	RunFrames(300);
	CHECK(Near(*CameraDist(), 400.0f), "never closer than the player's own (got %g)", *CameraDist());
	SetCamera(0.0f);
	RunFrames(300);
	CHECK(Near(*CameraDist(), 400.0f), "and left at 400 (got %g)", *CameraDist());
	*CameraDist() = 150.0f;

	printf("riding with a gentler limit than the game's (30 deg):\n");
	SetLive(30.0f);
	RunFrames(400);
	CHECK(Near(*Slope(), COS47), "never less steep than the game's own (got %f)", *Slope());
	SetLive(0.0f);
	RunFrames(300);

	printf("a load builds a new controller:\n");
	uint8_t *oldCtrl = g_controller;
	uint8_t *data = *(uint8_t **)(*(uint8_t **)(*(uint8_t **)(g_base + RVA_PLAYER) + 0x300) + 0x08);
	g_controller = (uint8_t *)NewObject(g_vtCtrl, 0x1000);
	memcpy(g_controller + 8, oldCtrl + 8, 0x1000 - 8);
	*(uint8_t **)(data + 0x3E0) = g_controller;
	Send(3, 1);   /* PostLoadGame */
	SetLive(65.0f);
	RunFrames(400);
	CHECK(Near(*Slope(), cosf(65.0f / 57.29578f)), "new controller gets 65 deg (got %f)", *Slope());
	CHECK(Near(*(float *)(oldCtrl + CTRL_SLOPE_OFFSET), COS47), "the old one isn't touched");
	SetLive(0.0f);
	RunFrames(400);
	CHECK(Near(*Slope(), COS47), "and back to 47 deg (got %f)", *Slope());

	printf("the controller goes away mid-ride (loading screen):\n");
	SetLive(60.0f);
	RunFrames(300);
	*(uint8_t **)(data + 0x3E0) = NULL;
	RunFrames(400);
	CHECK(true, "no crash with the controller gone");
	*(uint8_t **)(data + 0x3E0) = g_controller;
	RunFrames(400);
	CHECK(Near(*Slope(), 0.5f), "found again and set (got %f)", *Slope());
	SetLive(0.0f);
	RunFrames(300);
	CHECK(Near(*Slope(), COS47), "and restored (got %f)", *Slope());

	printf("%s\n", g_failures ? "FAILED" : "all ok");
	return g_failures ? 1 : 0;
}
