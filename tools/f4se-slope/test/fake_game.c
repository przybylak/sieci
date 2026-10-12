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
#define TILT_GLOBAL_FORMID    (0xFE000000u | (LIGHT_INDEX << 12) | 0x82Cu)
#define GROUND_GLOBAL_FORMID  (0xFE000000u | (LIGHT_INDEX << 12) | 0x82Du)   /* X, then Y, Z */
#define PARK_GLOBAL_FORMID    (0xFE000000u | (LIGHT_INDEX << 12) | 0x831u)   /* X, Y, Z, Angle, UpX, UpY, UpZ */
#define HEADING               1.0f         /* radians: the player faces a bit north of east */
#define DEG                   57.29578f
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
static uint8_t *g_tiltGlobal, *g_groundGlobals[3];
static uint8_t *g_player, *g_root, *g_bikeNode, *g_bikeShape, *g_boneData, *g_bones, *g_biped;
static uint8_t *g_parkGlobals[7];
static uint8_t g_bonesOriginal[0x50];
static int g_deleted;
static bool g_skinTransposed, g_rootTransposed;   /* how this "game" stores its rotations */

static float *Slope(void) { return (float *)(g_controller + CTRL_SLOPE_OFFSET); }
static float *ProxySlope(void) { return (float *)(g_proxy + PROXY_SLOPE_OFFSET); }
static float *CameraDist(void) { return (float *)(g_cameraSetting + 0x08); }
static void SetLive(float degrees) { *(float *)(g_global + 0x30) = degrees; }
static void SetCamera(float distance) { *(float *)(g_cameraGlobal + 0x30) = distance; }
static void SetTilt(float degrees) { *(float *)(g_tiltGlobal + 0x30) = degrees; }
static float Ground(int i) { return *(float *)(g_groundGlobals[i] + 0x30); }
static float Park(int i) { return *(float *)(g_parkGlobals[i] + 0x30); }
static float *PlayerPos(void) { return (float *)(g_player + 0xD0); }
static void SetNormal(float x, float y, float z)
{
	float *n = (float *)(g_controller + 0x1E0);
	n[0] = x; n[1] = y; n[2] = z; n[3] = 0.03f;
}
static void SetState(int state) { *(int32_t *)(g_controller + 0x2C0) = state; }
static int32_t *BoneDataRefs(void) { return (int32_t *)(g_boneData + 0x08); }

static uintptr_t FakeLookupFormByID(uint32_t id)
{
	if (id >= GROUND_GLOBAL_FORMID && id < GROUND_GLOBAL_FORMID + 3)
		return (uintptr_t)g_groundGlobals[id - GROUND_GLOBAL_FORMID];
	if (id >= PARK_GLOBAL_FORMID && id < PARK_GLOBAL_FORMID + 7)
		return (uintptr_t)g_parkGlobals[id - PARK_GLOBAL_FORMID];
	return id == SLOPE_GLOBAL_FORMID ? (uintptr_t)g_global : id == CAMERA_GLOBAL_FORMID ? (uintptr_t)g_cameraGlobal
	     : id == TILT_GLOBAL_FORMID ? (uintptr_t)g_tiltGlobal : 0;
}

static void FakeDeleteThis(uint8_t *obj) { (void)obj; g_deleted++; }

static uint8_t *NewGlobal(uint32_t formId, const char *editorId)
{
	uint8_t *g = (uint8_t *)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	g[0x1A] = 11;
	*(uint32_t *)(g + 0x14) = formId;
	*(const char **)(g + 0x20) = editorId;
	return g;
}

/* A BSFixedString: StringCache::Entry { next, state, length, externData, data }. */
static uint8_t *NewString(const char *text)
{
	uint8_t *e = (uint8_t *)VirtualAlloc(NULL, 0x100, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	*(uint32_t *)(e + 0x08) = 3;
	*(uint32_t *)(e + 0x0C) = (uint32_t)strlen(text);
	strcpy((char *)(e + 0x18), text);
	return e;
}

/* NiAVObject-ish: name at +0x10; NiNode children (NiTArray) at +0x120. */
static uint8_t *NewNode(void **vtbl, const char *name, int capacity)
{
	uint8_t *n = (uint8_t *)NewObject(vtbl, 0x200);
	*(uint8_t **)(n + 0x10) = NewString(name);
	*(int32_t *)(n + 0x08) = 1;
	if (capacity) {
		*(void **)(n + 0x128) = VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
		*(uint16_t *)(n + 0x130) = (uint16_t)capacity;
	}
	return n;
}

static void AddChild(uint8_t *node, uint8_t *child)
{
	uint16_t *used = (uint16_t *)(node + 0x132);
	(*(uint8_t ***)(node + 0x128))[(*used)++] = child;
}

/* A 3x3 rotation into rows of 4 floats, the way round this "game" keeps it. */
static void StoreRotation(float *rows, const float m[9], bool transposed)
{
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++)
			rows[i * 4 + j] = transposed ? m[j * 3 + i] : m[i * 3 + j];
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
	g_player = pl;
	*(float *)(pl + 0xC8) = HEADING;
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
	static const char *states[] = { ".?AVhknpCharacterStateManager@@", ".?AVhkReferencedObject@@" };
	uint8_t *stateManager = (uint8_t *)NewObject(MakeClass(states, 2), 0x200);
	*(float *)(stateManager + 0x40) = 3.0f;
	*(uint8_t **)(g_controller + 0x2B8) = stateManager;
	SetNormal(0.0f, 0.0f, 1.0f);   /* flat ground, on it (state 0) */
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

	g_global = NewGlobal(SLOPE_GLOBAL_FORMID, "CMB_SlopeLive");
	g_cameraGlobal = NewGlobal(CAMERA_GLOBAL_FORMID, "CMB_CameraLive");
	g_tiltGlobal = NewGlobal(TILT_GLOBAL_FORMID, "CMB_TiltLive");
	static const char *ground[3] = { "CMB_GroundNormalX", "CMB_GroundNormalY", "CMB_GroundNormalZ" };
	for (int i = 0; i < 3; i++)
		g_groundGlobals[i] = NewGlobal(GROUND_GLOBAL_FORMID + (uint32_t)i, ground[i]);
	static const char *park[7] = { "CMB_ParkX", "CMB_ParkY", "CMB_ParkZ", "CMB_ParkAngle", "CMB_ParkUpX", "CMB_ParkUpY", "CMB_ParkUpZ" };
	for (int i = 0; i < 7; i++)
		g_parkGlobals[i] = NewGlobal(PARK_GLOBAL_FORMID + (uint32_t)i, park[i]);
	PlayerPos()[0] = -1200.0f;
	PlayerPos()[1] = 1280.0f;
	PlayerPos()[2] = 100.0f;

	/* The player's 3D: root (turned by the heading) -> body bits, and the worn bike's node
	 * -> its shape, skinned to COM with the bind of the real CMB_BikeWornRider.nif. */
	static const char *fade[] = { ".?AVBSFadeNode@@", ".?AVNiNode@@", ".?AVNiAVObject@@", ".?AVNiObject@@" };
	static const char *node[] = { ".?AVNiNode@@", ".?AVNiAVObject@@", ".?AVNiObject@@" };
	static const char *tri[] = { ".?AVBSSubIndexTriShape@@", ".?AVBSTriShape@@", ".?AVBSGeometry@@", ".?AVNiAVObject@@", ".?AVNiObject@@" };
	static const char *skin[] = { ".?AVInstance@BSSkin@@", ".?AVNiObject@@" };
	static const char *bone[] = { ".?AVBoneData@BSSkin@@", ".?AVNiObject@@" };
	void **vtFade = MakeClass(fade, 4), **vtNode = MakeClass(node, 3), **vtTri = MakeClass(tri, 5);
	void **vtSkin = MakeClass(skin, 2), **vtBone = MakeClass(bone, 2);
	vtBone[1] = (void *)FakeDeleteThis;
	g_root = NewNode(vtFade, "skeleton.nif", 8);
	uint8_t *loaded = (uint8_t *)VirtualAlloc(NULL, 0x100, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	*(uint8_t **)(loaded + 0x08) = g_root;
	*(uint8_t **)(pl + 0xF0) = loaded;
	uint8_t *npcRoot = NewNode(vtNode, "NPC Root [Root]", 4);
	AddChild(g_root, npcRoot);
	AddChild(npcRoot, NewNode(vtTri, "BaseMaleBody:0", 0));
	AddChild(npcRoot, NewNode(vtNode, "COM", 0));
	AddChild(g_root, NewNode(vtTri, "CMB_Unrelated", 0));   /* wrong name: left alone */
	g_bikeNode = NewNode(vtNode, "CMB_BikeWornRider.nif", 2);
	uint8_t *shape = NewNode(vtTri, "CMB_BikeWornRider", 0);
	g_bikeShape = shape;
	AddChild(g_bikeNode, shape);
	AddChild(g_root, g_bikeNode);
	*(uint8_t **)(shape + 0x28) = g_bikeNode;   /* NiAVObject::m_parent */
	*(uint8_t **)(g_bikeNode + 0x28) = g_root;

	/* The biped (no type information): root, then 44 objects of 0x58; the bike in slot 57
	 * (index 27): its armor addon at +0x18, its 3D at +0x30. */
	static const char *arma[] = { ".?AVTESObjectARMA@@", ".?AVTESForm@@", ".?AVBaseFormComponent@@" };
	uint8_t *addon = (uint8_t *)NewObject(MakeClass(arma, 3), 0x200);
	*(uint32_t *)(addon + 0x14) = 0xFE005801u;
	addon[0x1A] = 105;
	g_biped = (uint8_t *)VirtualAlloc(NULL, 0x2000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	*(uint8_t **)(g_biped + 0x08) = g_root;
	*(uint8_t **)(g_biped + 0x10 + 27 * 0x58 + 0x18) = addon;
	*(uint8_t **)(g_biped + 0x10 + 27 * 0x58 + 0x30) = g_bikeNode;
	*(uint8_t **)(pl + 0x428) = g_biped;
	uint8_t *instance = (uint8_t *)NewObject(vtSkin, 0x100);
	*(uint8_t **)(shape + 0x140) = instance;
	g_boneData = (uint8_t *)NewObject(vtBone, 0x100);
	*(int32_t *)(g_boneData + 0x08) = 2;   /* the shape's skin and the model cache */
	*(uint8_t **)(instance + 0x40) = g_boneData;
	g_bones = (uint8_t *)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	*(uint8_t **)(g_boneData + 0x10) = g_bones;
	*(uint32_t *)(g_boneData + 0x18) = 1;
	*(uint32_t *)(g_boneData + 0x20) = 1;

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


/* The rotations, stored the way round the test asks for. */
static void SetLayouts(bool skinTransposed, bool rootTransposed)
{
	g_skinTransposed = skinTransposed;
	g_rootTransposed = rootTransposed;
	float c = cosf(HEADING), s = sinf(HEADING);
	const float heading[9] = { c, s, 0, -s, c, 0, 0, 0, 1 };   /* +Y -> (sin h, cos h, 0) */
	StoreRotation((float *)(g_root + 0x70), heading, rootTransposed);
	const float skinToBone[9] = { 0, 0, 1, 0, 1, 0, -1, 0, 0 };
	float *b = (float *)g_bones;
	b[0] = -24.67f; b[1] = 17.0f; b[2] = 0.0f; b[3] = 115.0f;   /* culling sphere (bone space) */
	StoreRotation(b + 4, skinToBone, skinTransposed);
	b[16] = -74.17f; b[17] = 0.0f; b[18] = 0.0f; b[19] = 1.0f;  /* translation, scale */
	memcpy(g_bonesOriginal, g_bones, sizeof(g_bonesOriginal));
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

static void (*g_onFrame)(float dt);   /* moves the player, when a test rides somewhere */

static void RunFrames(int ms)
{
	DWORD end = GetTickCount() + (DWORD)ms;
	DWORD last = GetTickCount();
	while ((int32_t)(GetTickCount() - end) < 0) {
		DWORD now = GetTickCount();
		if (g_onFrame)
			g_onFrame((float)(now - last) / 1000.0f);
		last = now;
		((void (*)(Task *))g_task->vtbl[1])(g_task);
		Sleep(5);
	}
}

static bool Near(float a, float b) { return fabsf(a - b) < 1e-5f; }

/* The rotation the plugin put on the bike's mesh: R = A^T A', with A and A' the bind
 * (mesh -> bone) before and now, read the way round this "game" stores them. */
static void AppliedRotation(float R[9])
{
	const float *o = (const float *)(g_bonesOriginal + 0x10), *w = (const float *)(g_bones + 0x10);
	float A[9], B[9];
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++) {
			A[i * 3 + j] = g_skinTransposed ? o[j * 4 + i] : o[i * 4 + j];
			B[i * 3 + j] = g_skinTransposed ? w[j * 4 + i] : w[i * 4 + j];
		}
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++)
			R[i * 3 + j] = A[i] * B[j] + A[3 + i] * B[3 + j] + A[6 + i] * B[6 + j];
}

static bool Orthonormal(const float R[9])
{
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++) {
			float d = R[i * 3] * R[j * 3] + R[i * 3 + 1] * R[j * 3 + 1] + R[i * 3 + 2] * R[j * 3 + 2];
			if (fabsf(d - (i == j ? 1.0f : 0.0f)) > 1e-4f)
				return false;
		}
	return true;
}

static void SetNormalTowards(const float dir[3], float degrees)
{
	float s = sinf(degrees / DEG);
	SetNormal(s * dir[0], s * dir[1], cosf(degrees / DEG));
}

static int g_fewestRefs;
static void WatchRefs(float dt)
{
	(void)dt;
	if (*BoneDataRefs() < g_fewestRefs)
		g_fewestRefs = *BoneDataRefs();
}

/* The bike's 3D somewhere else than under the root, a different name, or nowhere. */
static void SkinRouteTests(void)
{
	const float back[3] = { -sinf(HEADING), -cosf(HEADING), 0.0f };
	uint8_t **slotPart = (uint8_t **)(g_biped + 0x10 + 27 * 0x58 + 0x30);
	uint16_t *rootUsed = (uint16_t *)(g_root + 0x132);
	float R[9];

	/* The junk test before left the skin refused: start over, as after loading a save. */
	SetLayouts(false, false);
	Send(3, 1);   /* PostLoadGame */
	RunFrames(300);

	printf("tilt: the bike only in the biped, not under the 3D root:\n");
	(*rootUsed)--;   /* the bike's node is the root's last child */
	*(uint8_t **)(g_bikeNode + 0x28) = NULL;
	SetNormalTowards(back, 20.0f);
	SetTilt(30.0f);
	RunFrames(800);
	AppliedRotation(R);
	CHECK(*BoneDataRefs() == 3 && fabsf(R[8] - 0.93969f) < 0.01f, "found through the biped and tilted (references %d)", *BoneDataRefs());
	SetTilt(0.0f);
	RunFrames(300);
	CHECK(memcmp(g_bones, g_bonesOriginal, 0x50) == 0 && *BoneDataRefs() == 2, "put back and let go of");
	(*rootUsed)++;
	*(uint8_t **)(g_bikeNode + 0x28) = g_root;

	printf("tilt: the bike's shape under another name:\n");
	char *name = (char *)(*(uint8_t **)(g_bikeShape + 0x10) + 0x18);
	strcpy(name, "Motorcycle:0");
	SetTilt(30.0f);
	RunFrames(800);
	CHECK(*BoneDataRefs() == 3, "found by its COM bind (references %d)", *BoneDataRefs());
	g_fewestRefs = 99;
	g_onFrame = WatchRefs;
	RunFrames(600);
	g_onFrame = NULL;
	AppliedRotation(R);
	CHECK(g_fewestRefs == 3 && fabsf(R[8] - 0.93969f) < 0.01f,
	      "and kept while tilted (its bind no longer looks like COM's): never let go and taken again (fewest references %d)", g_fewestRefs);
	SetTilt(0.0f);
	RunFrames(300);
	CHECK(*BoneDataRefs() == 2, "and let go of");
	strcpy(name, "CMB_BikeWornRider");

	printf("tilt: no bike anywhere:\n");
	(*rootUsed)--;
	uint8_t *part = *slotPart;
	*slotPart = NULL;
	SetTilt(30.0f);
	RunFrames(1600);
	CHECK(*BoneDataRefs() == 2 && memcmp(g_bones, g_bonesOriginal, 0x50) == 0, "nothing held, nothing changed (the log says what it saw)");
	SetTilt(0.0f);
	RunFrames(300);
	*slotPart = part;
	(*rootUsed)++;
	SetNormal(0.0f, 0.0f, 1.0f);
}

/* Riding along: up a slope at a steady speed. */
static float g_rideSpeed, g_rideSlope;
static void RideAlong(float dt)
{
	float d = g_rideSpeed * dt;
	PlayerPos()[0] += sinf(HEADING) * cosf(g_rideSlope / DEG) * d;
	PlayerPos()[1] += cosf(HEADING) * cosf(g_rideSlope / DEG) * d;
	PlayerPos()[2] += sinf(g_rideSlope / DEG) * d;
}

static void TrackTests(void)
{
	const float back[3] = { -sinf(HEADING), -cosf(HEADING), 0.0f };
	printf("park: riding up a 10 deg slope, then stopping:\n");
	SetNormalTowards(back, 10.0f);
	SetState(0);
	SetLive(60.0f);
	RunFrames(300);
	CHECK(Park(6) == 0.0f, "no spot before riding anywhere (up z %.2f)", Park(6));
	g_rideSpeed = 300.0f;
	g_rideSlope = 10.0f;
	g_onFrame = RideAlong;
	RunFrames(1500);
	g_onFrame = NULL;
	RunFrames(300);
	const float *p = PlayerPos();
	float behind = (80.0f + 210.0f) * 0.5f;   /* the bike's middle, along the ground */
	float ex = p[0] - sinf(HEADING) * cosf(10.0f / DEG) * behind, ey = p[1] - cosf(HEADING) * cosf(10.0f / DEG) * behind;
	float ez = p[2] - sinf(10.0f / DEG) * behind;
	CHECK(Park(6) > 0.9f, "a spot (up z %.3f)", Park(6));
	CHECK(fabsf(Park(0) - ex) < 1.0f && fabsf(Park(1) - ey) < 1.0f && fabsf(Park(2) - ez) < 1.0f,
	      "on the track a bike length back: (%.1f, %.1f, %.1f), expected (%.1f, %.1f, %.1f)", Park(0), Park(1), Park(2), ex, ey, ez);
	float angle = fmodf(HEADING * DEG + 180.0f, 360.0f);
	CHECK(fabsf(Park(3) - angle) < 0.5f, "facing the way ridden (angle %.1f, expected %.1f)", Park(3), angle);
	float n[3] = { -sinf(10.0f / DEG) * sinf(HEADING), -sinf(10.0f / DEG) * cosf(HEADING), cosf(10.0f / DEG) };
	CHECK(fabsf(Park(4) - n[0]) < 0.01f && fabsf(Park(5) - n[1]) < 0.01f && fabsf(Park(6) - n[2]) < 0.01f,
	      "up is the slope's normal (%.3f, %.3f, %.3f)", Park(4), Park(5), Park(6));

	printf("park: riding up a 45 deg slope:\n");
	SetNormalTowards(back, 45.0f);
	g_rideSlope = 45.0f;
	g_onFrame = RideAlong;
	RunFrames(1500);
	g_onFrame = NULL;
	RunFrames(300);
	ez = PlayerPos()[2] - sinf(45.0f / DEG) * behind;
	CHECK(Park(6) > 0.6f && fabsf(Park(2) - ez) < 1.0f, "a spot on the steep track too (z %.1f, expected %.1f; up z %.3f)", Park(2), ez, Park(6));

	printf("park: a drop (in the air for a second):\n");
	SetState(2);
	g_onFrame = RideAlong;
	g_rideSlope = 0.0f;
	RunFrames(1000);
	g_onFrame = NULL;
	SetState(0);
	RunFrames(300);
	CHECK(Park(6) == 0.0f, "the track starts again: no spot right after landing");

	printf("park: a teleport:\n");
	g_onFrame = RideAlong;
	RunFrames(1500);
	g_onFrame = NULL;
	RunFrames(300);
	CHECK(Park(6) > 0.9f, "a spot again after riding on");
	PlayerPos()[0] += 5000.0f;
	RunFrames(300);
	CHECK(Park(6) == 0.0f, "none after a teleport");
	SetLive(0.0f);
	RunFrames(300);
	SetNormal(0.0f, 0.0f, 1.0f);
}

static void TiltTests(void)
{
	const float forward[3] = { sinf(HEADING), cosf(HEADING), 0.0f }, back[3] = { -forward[0], -forward[1], 0.0f };
	const float right[3] = { cosf(HEADING), -sinf(HEADING), 0.0f };
	float R[9];

	printf("tilt: standing, not riding:\n");
	SetTilt(0.0f);
	SetNormal(0.0f, 0.0f, 1.0f);
	SetState(0);
	RunFrames(300);
	CHECK(Near(Ground(0), 0.0f) && Near(Ground(1), 0.0f) && Near(Ground(2), 1.0f), "ground normal (0, 0, 1) in CMB_GroundNormalX/Y/Z");
	CHECK(memcmp(g_bones, g_bonesOriginal, 0x50) == 0 && *BoneDataRefs() == 2, "the bike's skin untouched");

	printf("tilt: riding up a 20 deg slope:\n");
	SetNormalTowards(back, 20.0f);   /* uphill ahead: the ground's normal leans back */
	SetTilt(30.0f);
	RunFrames(800);
	CHECK(*BoneDataRefs() == 3, "the skin is held (references %d)", *BoneDataRefs());
	AppliedRotation(R);
	CHECK(fabsf(R[2]) < 0.01f && fabsf(R[5] + 0.34202f) < 0.01f && fabsf(R[8] - 0.93969f) < 0.01f,
	      "the mesh's up turned to the ground: (%.3f, %.3f, %.3f), expected (0, -0.342, 0.940)", R[2], R[5], R[8]);
	CHECK(R[7] > 0.3f, "nose up (forward goes to z %.3f)", R[7]);
	CHECK(Orthonormal(R), "still a rotation");
	CHECK(memcmp(g_bones + 0x40, g_bonesOriginal + 0x40, 16) == 0, "translation and scale untouched");
	CHECK(*(float *)(g_bones + 0x0C) > 115.0f, "culling sphere grown (radius %.1f)", *(float *)(g_bones + 0x0C));
	RunFrames(3000);   /* the published normal is an average over the last 0.6 s or so */
	CHECK(fabsf(Ground(2) - 0.93969f) < 0.01f && fabsf(Ground(0) + 0.34202f * forward[0]) < 0.01f,
	      "CMB_GroundNormal, averaged, follows the slope (%.3f, %.3f, %.3f)", Ground(0), Ground(1), Ground(2));

	printf("tilt: a 45 deg side slope, more than the 30 allowed:\n");
	SetNormalTowards(right, 45.0f);   /* ground falls away to the right */
	RunFrames(800);
	AppliedRotation(R);
	CHECK(fabsf(acosf(R[8]) * DEG - 30.0f) < 0.5f, "tilted 30 deg (%.2f)", acosf(R[8]) * DEG);
	CHECK(R[6] < -0.3f && fabsf(R[7]) < 0.01f, "right side down (right goes to z %.3f), no pitch", R[6]);

	RunFrames(2500);
	float groundX = Ground(0);
	printf("tilt: in the air:\n");
	SetState(2);
	SetNormalTowards(forward, 10.0f);   /* stale normal: must not be used */
	RunFrames(800);
	AppliedRotation(R);
	CHECK(R[8] > 0.9999f, "eased back to level (cos %.5f)", R[8]);
	CHECK(Ground(2) == 0.0f && fabsf(Ground(0) - groundX) < 0.01f,
	      "in the air CMB_GroundNormalZ is 0, X and Y left alone (%.3f, %.3f, %.3f)", Ground(0), Ground(1), Ground(2));
	SetState(0);
	SetNormal(0.0f, 0.0f, 1.0f);
	RunFrames(300);

	printf("tilt: getting off:\n");
	SetTilt(0.0f);
	RunFrames(300);
	CHECK(memcmp(g_bones, g_bonesOriginal, 0x50) == 0, "the skin back exactly as it was");
	CHECK(*BoneDataRefs() == 2 && g_deleted == 0, "let go of (references %d)", *BoneDataRefs());

	printf("tilt: the bike taken off mid-ride:\n");
	SetNormalTowards(back, 20.0f);
	SetTilt(30.0f);
	RunFrames(500);
	CHECK(*BoneDataRefs() == 3, "held");
	*(uint16_t *)(g_root + 0x132) -= 1;   /* the bike's node leaves the 3D (last child) */
	uint8_t **slotPart = (uint8_t **)(g_biped + 0x10 + 27 * 0x58 + 0x30);
	*slotPart = NULL;                     /* and the biped's slot 57 */
	*BoneDataRefs() -= 2;                 /* and the game drops its references */
	RunFrames(300);
	CHECK(g_deleted == 1 && memcmp(g_bones, g_bonesOriginal, 0x50) == 0, "put back, let go of, deleted with the last reference");
	*(uint16_t *)(g_root + 0x132) += 1;
	*slotPart = g_bikeNode;
	*BoneDataRefs() = 2;
	g_deleted = 0;
	SetTilt(0.0f);
	RunFrames(300);

	printf("tilt: skin data that isn't what it should be:\n");
	float *rows = (float *)(g_bones + 0x10);
	rows[0] = 2.0f;   /* not a rotation any more */
	memcpy(g_bonesOriginal, g_bones, sizeof(g_bonesOriginal));
	SetNormalTowards(back, 20.0f);
	SetTilt(30.0f);
	RunFrames(500);
	CHECK(memcmp(g_bones, g_bonesOriginal, 0x50) == 0 && *BoneDataRefs() == 2, "not touched, not held");
	SetTilt(0.0f);
	RunFrames(200);
}

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
	SetLayouts(mode == 4, mode == 4 || mode == 5);   /* 4: transposed matrices, 5: skin and 3D disagree */

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
	if (mode == 4 || mode == 5) {
		Send(10, 1);   /* GameDataReady */
		RunFrames(300);
		if (mode == 4) {
			TiltTests();
		} else {
			float fwd[3] = { -sinf(HEADING), -cosf(HEADING), 0.0f };
			SetNormalTowards(fwd, 20.0f);
			SetTilt(30.0f);
			RunFrames(600);
			CHECK(memcmp(g_bones, g_bonesOriginal, 0x50) == 0, "skin and 3D disagree about the matrices: the bike isn't tilted");
			SetTilt(0.0f);
			RunFrames(300);
			CHECK(*BoneDataRefs() == 2, "and let go of (references %d)", *BoneDataRefs());
		}
		printf("%s\n", g_failures ? "FAILED" : "all ok");
		return g_failures ? 1 : 0;
	}

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

	TiltTests();
	SkinRouteTests();
	TrackTests();

	printf("%s\n", g_failures ? "FAILED" : "all ok");
	return g_failures ? 1 : 0;
}
