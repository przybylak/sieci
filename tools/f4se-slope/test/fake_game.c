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
#define RVA_PLAYER_CAMERA     0x030E6E58u
#define RVA_RTTI_AREA         0x01000000u  /* where the fake RTTI goes, clear of the above */

#define PROXY_SLOPE_OFFSET    0x9C
#define CTRL_SLOPE_OFFSET     0x418        /* cos 47 deg, as in the real game (test 5) */
#define LIGHT_INDEX           5
#define SLOPE_GLOBAL_FORMID   (0xFE000000u | (LIGHT_INDEX << 12) | 0x82Au)
#define CAMERA_GLOBAL_FORMID  (0xFE000000u | (LIGHT_INDEX << 12) | 0x82Bu)
#define TILT_GLOBAL_FORMID    (0xFE000000u | (LIGHT_INDEX << 12) | 0x82Cu)
#define GROUND_GLOBAL_FORMID  (0xFE000000u | (LIGHT_INDEX << 12) | 0x82Du)   /* X, then Y, Z */
#define PARK_GLOBAL_FORMID    (0xFE000000u | (LIGHT_INDEX << 12) | 0x831u)   /* X, Y, Z, Angle, UpX, UpY, UpZ */
#define SLOPE_TRACK_FORMID    (0xFE000000u | (LIGHT_INDEX << 12) | 0x838u)
#define TURN_RADIUS_FORMID    (0xFE000000u | (LIGHT_INDEX << 12) | 0x839u)
#define TURN_STAND_FORMID     (0xFE000000u | (LIGHT_INDEX << 12) | 0x83Au)
#define TURN_SLOW_FORMID      (0xFE000000u | (LIGHT_INDEX << 12) | 0x83Bu)
#define HEADLAMP_FORMID       (0xFE000000u | (LIGHT_INDEX << 12) | 0x83Du)
#define HEADLAMP_REF_HI_FORMID (0xFE000000u | (LIGHT_INDEX << 12) | 0x843u)
#define HEADLAMP_REF_LO_FORMID (0xFE000000u | (LIGHT_INDEX << 12) | 0x844u)
#define LAMP_REF_FORMID       0xFF001234u   /* the light reference "the script placed" */
#define RVA_PLAYER_CONTROLS   0x031F0B80u
#define RVA_MOVE_HANDLER_VTBL 0x02571B38u  /* where 1.11.240 has them (test 13) */
#define RVA_CONTROLS_IMOVE_VTBL 0x02571AA0u
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
	void **vt = (void **)RttiAlloc(8 * 0x52);
	vt[0] = col;
	return vt + 1;
}

/* A second vtable of the same class, for a base at `offset` (its COL says so). */
static void **MakeSecondary(void **vtbl, uint32_t offset)
{
	const uint32_t *primary = (const uint32_t *)vtbl[-1];
	uint32_t *col = (uint32_t *)RttiAlloc(24);
	memcpy(col, primary, 24);
	col[1] = offset;
	col[5] = Rva((uintptr_t)col);
	void **vt = (void **)RttiAlloc(8 * 0x10);
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
static uint8_t *g_lampNode, *g_headlampLive, g_lampLocalOriginal[0x40];
static uint8_t *g_headlampRefHi, *g_headlampRefLo, *g_lampRef, *g_lampRefLoaded, *g_lampRefRoot, *g_lampRefLight;
static uint8_t *g_partData[3], *g_partBones[3];   /* the Harley build's moving parts: front wheel, rear wheel, bar assembly */
static uint8_t g_partBonesOriginal[3][0x50];
/* The rider: the body skinned to two bones, the COM the bike hangs off, a plain shape (the
 * Pip-Boy's) under a bone of its own. Their world transforms follow the player (SyncFakeWorld). */
static uint8_t *g_bodyShape, *g_bodySkin, *g_bodyData, *g_bodyBones, *g_bodyNodes[10], *g_comNode, *g_pipboyBone, *g_pipboyShape, *g_npcRoot;
static uint8_t g_bodyBonesOriginal[10 * 0x50], g_pipboyLocalOriginal[0x40];
static uint8_t *g_decalShape, *g_decalSkin;   /* a blood decal: the game clones the body's skin instance for it (test 29) */
static void **g_vtSkin;
static uint8_t *g_parkGlobals[7], *g_trackSlope, *g_turnRadius, *g_turnStand, *g_turnSlow, *g_controls;
static uint8_t *g_thirdState;   /* ThirdPersonState: zoom target +0xE8, current +0xEC */
static uint8_t *g_moveHandler;  /* MovementHandler: its vtable read-only, as in the game */

/* The input and the movement, as the game does them (tests 12-14, 19): the MovementHandler
 * sets PlayerControls' move input from the held keys (style 0: both halves every frame; style
 * 1: adds the change on a press or release; style 2, as the game does: the input cleared to
 * (+0, +0) every frame outside the handler, then each held key sets its own half; style 3: as
 * 2, then cleared again after the keys, before the per-frame call, as the game does on some
 * frames). The
 * controls' output to the movement (GetControllerOutput) comes from that: speed 2 x the
 * input, target angle where the keys point from the camera. The movement turns the player
 * towards the target angle and moves them along their facing (g_honour 8: turned by the
 * output's rotation z; 16: backwards when its speed is negative). And the controller's pushes,
 * honoured or not (g_honour: 1 velocityMod, 2 SetLinearVelocity, 4 SetPosition). */
#define HAVOK 0.0142875f
typedef struct { float x, y; int axis; } FakeEvent;   /* axis: 0 both, 1 x, 2 y */
static int g_handlerStyle, g_honour, g_outputCalls;
static float g_keyX, g_keyY, g_lastKeyX, g_lastKeyY, g_camYaw, g_fakeVel[4];
static void FakeOnButton(uint8_t *self, const FakeEvent *e)
{
	float *move = *(float **)(self + 0x10);
	if (g_handlerStyle == 1) {
		move[0] += e->x;
		move[1] += e->y;
	} else {
		if (e->axis != 2)
			move[0] = e->x;
		if (e->axis != 1)
			move[1] = e->y;
	}
}
static void FakeOnThumbstick(uint8_t *self, const FakeEvent *e) { (void)self; (void)e; }
static void FakePerFrame(uint8_t *self) { (void)self; }
static void FakeNothing(void) {}
static uint8_t *g_controlsForOutput, *g_playerForOutput;
static void FakeGetControllerOutput(uint8_t *self, uint32_t id, float *out)
{
	(void)self; (void)id;
	const float *move = (const float *)(g_controlsForOutput + 0x44);
	float mag = sqrtf(move[0] * move[0] + move[1] * move[1]);
	memset(out, 0, 64);
	out[8] = 2.0f * (mag > 1.0f ? 1.0f : mag);
	out[14] = mag > 0.01f ? g_camYaw + atan2f(move[0], move[1]) : *(const float *)(g_playerForOutput + 0xC8);
	g_outputCalls++;
}
static float *PlayerPosition(void);
static void FakeGetPosition(uint8_t *self, float *out, bool centre)
{
	(void)self; (void)centre;
	for (int i = 0; i < 3; i++)
		out[i] = PlayerPosition()[i] * HAVOK;
	out[3] = 0.0f;
}
static void FakeSetPosition(uint8_t *self, const float *p, bool centre, bool warp)
{
	(void)self; (void)centre; (void)warp;
	if (g_honour & 4)
		for (int i = 0; i < 3; i++)
			PlayerPosition()[i] = p[i] / HAVOK;
}
static void FakeGetVelocity(uint8_t *self, float *out) { (void)self; memcpy(out, g_fakeVel, 16); }

/* The world the rays see: flat ground at g_groundZ (none past the drop's edge, when there's
 * one, layer 13 terrain), and up to three vertical planes (walls, layer 1 static, or a trigger
 * volume, layer 12) facing the bike. The game's picking: bhkPickData (ours: start +0x20, end
 * +0x30, hit +0x60, fraction +0x64, the hit's layer +0xAC, world +0xC0), TESObjectCELL::Pick,
 * found through an Address Library file the test writes next to the plugin. */
typedef struct { bool on; float point[2], normal[2]; uint32_t layer; } FakePlane;
static float g_groundZ = 100.0f;
static float g_slopeK, g_slopeO[2], g_slopeD[2];   /* the ground rises g_slopeK per unit along g_slopeD from g_slopeO */
static bool g_dropOn, g_frozen;   /* g_frozen: the movement can't move the player (stuck against something) */
static float g_creepDrag;         /* rough ground: only the input above this moves the player */
static int g_pileCount;           /* a pile of clutter (layer 4): this many surfaces 5 apart above the ground, within 60 of g_pilePoint */
static float g_pilePoint[2];
static FakePlane g_planes[3];
static float g_dropPoint[2], g_dropDir[2];
static uint8_t *g_wallObj, *g_groundObj, g_fakeWorld[64];
static int g_picks;
static void *FakePickCtor(uint8_t *pick)
{
	memset(pick, 0, 0xE0);
	*(void **)(pick + 0xD0) = g_fakeWorld + 32;   /* a collector */
	return pick;
}
static void FakePickReset(uint8_t *pick) { *(int *)(pick + 0x60) = 0; *(float *)(pick + 0x64) = 1.0f; }
static void FakePickSetStartEnd(uint8_t *pick, const float *a, const float *b)
{
	memcpy(pick + 0x20, a, 12);
	memcpy(pick + 0x30, b, 12);
}
static bool FakePickHasHit(const uint8_t *pick) { return *(const int *)(pick + 0x60) != 0; }
static float FakePickFraction(const uint8_t *pick) { return *(const float *)(pick + 0x64); }
static uint8_t *FakeCellPick(uint8_t *cell, uint8_t *pick)
{
	(void)cell;
	const float *a = (const float *)(pick + 0x20), *b = (const float *)(pick + 0x30);
	float t = 2.0f;
	uint8_t *what = NULL;
	uint32_t layer = 0;
	float den = (b[2] - a[2]) - g_slopeK * ((b[0] - a[0]) * g_slopeD[0] + (b[1] - a[1]) * g_slopeD[1]);
	if (den != 0.0f) {
		float tg = (g_groundZ + g_slopeK * ((a[0] - g_slopeO[0]) * g_slopeD[0] + (a[1] - g_slopeO[1]) * g_slopeD[1]) - a[2]) / den;
		float x = a[0] + (b[0] - a[0]) * tg, y = a[1] + (b[1] - a[1]) * tg;
		bool ground = !g_dropOn || (x - g_dropPoint[0]) * g_dropDir[0] + (y - g_dropPoint[1]) * g_dropDir[1] < 0.0f;
		if (tg >= 0.0f && tg <= 1.0f && ground) {
			t = tg;
			what = g_groundObj;
			layer = 13;
		}
	}
	for (int i = 0; i < g_pileCount; i++) {
		float z = g_groundZ + 5.0f * (float)(i + 1);
		if (b[2] == a[2])
			continue;
		float tp = (z - a[2]) / (b[2] - a[2]);
		float x = a[0] + (b[0] - a[0]) * tp, y = a[1] + (b[1] - a[1]) * tp;
		if (tp >= 0.0f && tp <= 1.0f && tp < t && hypotf(x - g_pilePoint[0], y - g_pilePoint[1]) < 60.0f) {
			t = tp;
			what = NULL;
			layer = 4;
		}
	}
	for (int i = 0; i < 3; i++) {
		const FakePlane *w = &g_planes[i];
		if (!w->on)
			continue;
		float da = (a[0] - w->point[0]) * w->normal[0] + (a[1] - w->point[1]) * w->normal[1];
		float db = (b[0] - w->point[0]) * w->normal[0] + (b[1] - w->point[1]) * w->normal[1];
		if (da > 0.0f && db <= 0.0f && da / (da - db) < t) {
			t = da / (da - db);
			what = w->layer == 12 ? NULL : g_wallObj;
			layer = w->layer;
		}
	}
	*(int *)(pick + 0x60) = t <= 1.0f;
	*(float *)(pick + 0x64) = t <= 1.0f ? t : 1.0f;
	*(uint32_t *)(pick + 0xAC) = 0x12345600u | layer;   /* the layer in the low 7 bits */
	*(void **)(pick + 0xC0) = g_fakeWorld;
	g_picks++;
	return what;
}

/* F4SE's Address Library for 1.11.240, as the plugin reads it: a count, then {id, offset}
 * pairs sorted by id; the pick functions among some others. */
static void WriteAddressLibrary(void)
{
	struct { uint64_t id; void *f; } ours[] = {
		{ 2200263, (void *)FakeCellPick }, { 2230668, (void *)FakePickCtor }, { 2236622, (void *)FakePickSetStartEnd },
		{ 2277761, (void *)FakePickReset }, { 2277770, (void *)FakePickHasHit }, { 2277771, (void *)FakePickFraction },
	};
	FILE *f = fopen("version-1-11-240-0.bin", "wb");
	uint64_t count = 600;
	fwrite(&count, 8, 1, f);
	for (uint64_t id = 2200000, k = 0, n = 0; n < count; id += 300, n++) {
		uint64_t pair[2] = { id, 0x1000 + id };
		if (k < 6 && ours[k].id <= id) {
			pair[0] = ours[k].id;
			pair[1] = (uintptr_t)ours[k].f - g_base;
			k++;
			id = pair[0];
		}
		fwrite(pair, 16, 1, f);
	}
	fclose(f);
}
static void FakeSetVelocity(uint8_t *self, const float *v) { (void)self; if (g_honour & 2) memcpy(g_fakeVel, v, 16); }
static uint8_t g_bonesOriginal[0x50];
static int g_deleted;
static bool g_skinTransposed, g_rootTransposed;   /* how this "game" stores its rotations */

static float *Slope(void) { return (float *)(g_controller + CTRL_SLOPE_OFFSET); }
static float *ProxySlope(void) { return (float *)(g_proxy + PROXY_SLOPE_OFFSET); }
static float *CameraDist(void) { return (float *)(g_cameraSetting + 0x08); }
static void SetLive(float degrees) { *(float *)(g_global + 0x30) = degrees; }
static void SetCamera(float distance) { *(float *)(g_cameraGlobal + 0x30) = distance; }
static void SetTilt(float degrees) { *(float *)(g_tiltGlobal + 0x30) = degrees; }
static void SetHeadlamp(float on) { *(float *)(g_headlampLive + 0x30) = on; }
static void SetLampRef(uint32_t id) { *(float *)(g_headlampRefHi + 0x30) = (float)(id >> 16); *(float *)(g_headlampRefLo + 0x30) = (float)(id & 0xFFFFu); }
static float Ground(int i) { return *(float *)(g_groundGlobals[i] + 0x30); }
static float Park(int i) { return *(float *)(g_parkGlobals[i] + 0x30); }
static float *PlayerPos(void) { return (float *)(g_player + 0xD0); }
static float *PlayerPosition(void) { return PlayerPos(); }
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
	if (id == SLOPE_TRACK_FORMID)
		return (uintptr_t)g_trackSlope;
	if (id == TURN_RADIUS_FORMID)
		return (uintptr_t)g_turnRadius;
	if (id == TURN_STAND_FORMID)
		return (uintptr_t)g_turnStand;
	if (id == TURN_SLOW_FORMID)
		return (uintptr_t)g_turnSlow;
	if (id == HEADLAMP_FORMID)
		return (uintptr_t)g_headlampLive;
	if (id == HEADLAMP_REF_HI_FORMID)
		return (uintptr_t)g_headlampRefHi;
	if (id == HEADLAMP_REF_LO_FORMID)
		return (uintptr_t)g_headlampRefLo;
	if (id == LAMP_REF_FORMID)
		return (uintptr_t)g_lampRef;
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
	g_trackSlope = NewGlobal(SLOPE_TRACK_FORMID, "CMB_TrackSlope");
	g_turnRadius = NewGlobal(TURN_RADIUS_FORMID, "CMB_TurnRadius");     /* 0: steering off until a test sets it */
	g_turnStand = NewGlobal(TURN_STAND_FORMID, "CMB_StandTurnRate");
	g_turnSlow = NewGlobal(TURN_SLOW_FORMID, "CMB_TurnRadiusSlow");
	g_headlampLive = NewGlobal(HEADLAMP_FORMID, "CMB_HeadlampLive");
	g_headlampRefHi = NewGlobal(HEADLAMP_REF_HI_FORMID, "CMB_HeadlampRefHi");
	g_headlampRefLo = NewGlobal(HEADLAMP_REF_LO_FORMID, "CMB_HeadlampRefLo");
	static const char *controls[] = { ".?AVPlayerControls@@", ".?AVBSInputEventReceiver@@" };
	void **vtControls = MakeClass(controls, 2);
	g_controls = (uint8_t *)NewObject(vtControls, 0x300);
	*(uintptr_t *)(g_base + RVA_PLAYER_CONTROLS) = (uintptr_t)g_controls;
	g_controlsForOutput = g_controls;
	g_playerForOutput = g_player;
	/* PlayerControls' IMovementPlayerControls vtable and the MovementHandler's (a struct in
	 * the game) where 1.11.240 has them, on a page made read-only, as in the game. */
	void **vtMovement = (void **)(g_base + RVA_CONTROLS_IMOVE_VTBL);
	vtMovement[-1] = MakeSecondary(vtControls, 0x30)[-1];
	vtMovement[0] = (void *)FakeNothing;
	vtMovement[1] = (void *)FakeGetControllerOutput;
	*(void ***)(g_controls + 0x30) = vtMovement;
	static const char *movement[] = { ".?AUMovementHandler@@", ".?AVPlayerInputHandler@@", ".?AVBSInputEventUser@@" };
	void **vtHandler = (void **)(g_base + RVA_MOVE_HANDLER_VTBL);
	vtHandler[-1] = MakeClass(movement, 3)[-1];
	for (int i = 0; i < 10; i++)
		vtHandler[i] = (void *)FakeNothing;
	vtHandler[4] = (void *)FakeOnThumbstick;
	vtHandler[8] = (void *)FakeOnButton;
	vtHandler[9] = (void *)FakePerFrame;
	DWORD oldProtect;
	VirtualProtect((void *)((uintptr_t)vtHandler & ~(uintptr_t)0xFFF), 0x1000, PAGE_READONLY, &oldProtect);
	g_moveHandler = (uint8_t *)NewObject(vtHandler, 0x40);
	*(uint8_t **)(g_moveHandler + 0x10) = g_controls + 0x44;
	*(uint8_t **)(g_controls + 0x1E0) = g_moveHandler;
	g_vtCtrl[0x33] = (void *)FakeGetPosition;
	g_vtCtrl[0x34] = (void *)FakeSetPosition;
	g_vtCtrl[0x39] = (void *)FakeGetVelocity;
	g_vtCtrl[0x3A] = (void *)FakeSetVelocity;
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
	g_wallObj = NewNode(vtNode, "FakeWall", 0);
	g_groundObj = NewNode(vtNode, "FakeGround", 0);
	static const char *cell[] = { ".?AVTESObjectCELL@@", ".?AVTESForm@@" };
	*(void **)(g_player + 0xB8) = NewObject(MakeClass(cell, 2), 0x200);
	void **vtSkin = MakeClass(skin, 2), **vtBone = MakeClass(bone, 2);
	vtBone[1] = (void *)FakeDeleteThis;
	vtSkin[1] = (void *)FakeDeleteThis;
	g_vtSkin = vtSkin;
	g_root = NewNode(vtFade, "skeleton.nif", 8);
	uint8_t *loaded = (uint8_t *)VirtualAlloc(NULL, 0x100, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	*(uint8_t **)(loaded + 0x08) = g_root;
	*(uint8_t **)(pl + 0xF0) = loaded;
	uint8_t *npcRoot = NewNode(vtNode, "NPC Root [Root]", 16);
	g_npcRoot = npcRoot;
	AddChild(g_root, npcRoot);
	*(uint8_t **)(npcRoot + 0x28) = g_root;
	g_bodyShape = NewNode(vtTri, "BaseMaleBody:0", 0);
	AddChild(npcRoot, g_bodyShape);
	*(uint8_t **)(g_bodyShape + 0x28) = npcRoot;
	g_comNode = NewNode(vtNode, "COM", 0);
	AddChild(npcRoot, g_comNode);
	*(uint8_t **)(g_comNode + 0x28) = npcRoot;
	g_bodyNodes[0] = NewNode(vtNode, "NPC Pelvis [Pelv]", 0);
	g_bodyNodes[1] = NewNode(vtNode, "NPC Spine [Spn0]", 0);
	g_bodyNodes[2] = NewNode(vtNode, "NPC Spine1 [Spn1]", 0);   /* in the skin with no vertices of its own (test 24) */
	g_bodyNodes[3] = NewNode(vtNode, "NPC Neck [Neck]", 0);      /* its node scaled to 0: hidden (test 27's backpack bone) */
	g_bodyNodes[4] = NewNode(vtNode, "Cloth_BN_Purse_001", 0);   /* a cloth bone: its world matrix sheared, not orthonormal (test 28) */
	g_bodyNodes[5] = NewNode(vtNode, "LArm_Hand [LHnd]", 0);     /* a hand: turns with the bars (test 29) */
	g_bodyNodes[6] = NewNode(vtNode, "LArm_UpperArm [LUar]", 0); /* the shoulder and the elbow: the arm's two-bone solve (test 30) */
	g_bodyNodes[7] = NewNode(vtNode, "LArm_ForeArm1 [LLar]", 0);
	g_bodyNodes[8] = NewNode(vtNode, "HEAD", 2);                 /* the head, kept level as the bike rolls (test 31), and a face bone under it */
	g_bodyNodes[9] = NewNode(vtNode, "Face_Jaw", 0);
	for (int i = 0; i < 9; i++) {
		AddChild(npcRoot, g_bodyNodes[i]);
		*(uint8_t **)(g_bodyNodes[i] + 0x28) = npcRoot;
	}
	AddChild(g_bodyNodes[8], g_bodyNodes[9]);
	*(uint8_t **)(g_bodyNodes[9] + 0x28) = g_bodyNodes[8];
	g_pipboyBone = NewNode(vtNode, "PipboyBone", 2);
	AddChild(npcRoot, g_pipboyBone);
	*(uint8_t **)(g_pipboyBone + 0x28) = npcRoot;
	g_pipboyShape = NewNode(vtTri, "PipboyScreen", 0);
	AddChild(g_pipboyBone, g_pipboyShape);
	*(uint8_t **)(g_pipboyShape + 0x28) = g_pipboyBone;
	AddChild(g_root, NewNode(vtTri, "CMB_Unrelated", 0));   /* wrong name: left alone */
	g_bikeNode = NewNode(vtNode, "CMB_BikeWornRider.nif", 8);
	uint8_t *shape = NewNode(vtTri, "CMB_BikeWornRider", 0);
	g_bikeShape = shape;
	AddChild(g_bikeNode, shape);
	/* The headlamp's add-on node (BSValueNode in the game; a node by name here), where the
	 * nif puts it: at the lens in the bike's space, under the nif's root. */
	g_lampNode = NewNode(vtNode, "CMB_Headlamp", 0);
	AddChild(g_bikeNode, g_lampNode);
	*(uint8_t **)(g_lampNode + 0x28) = g_bikeNode;
	{
		float *rows = (float *)(g_lampNode + 0x30);
		rows[0] = rows[5] = rows[10] = 1.0f;
		rows[12] = 0.3f;
		rows[13] = 76.3f;
		rows[14] = 81.9f;
		rows[15] = 1.0f;
		memcpy(g_lampLocalOriginal, rows, 0x40);
	}
	/* The light reference the script places: a TESObjectREFR with loaded 3D (a root node with
	 * the light's node under it), looked up by its id. */
	static const char *refNames[] = { ".?AVTESObjectREFR@@", ".?AVTESForm@@", ".?AVBaseFormComponent@@" };
	g_lampRef = (uint8_t *)NewObject(MakeClass(refNames, 3), 0x200);
	g_lampRef[0x1A] = 0x40;
	*(uint32_t *)(g_lampRef + 0x14) = LAMP_REF_FORMID;
	g_lampRefLoaded = (uint8_t *)VirtualAlloc(NULL, 0x100, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	*(uint8_t **)(g_lampRef + 0xF0) = g_lampRefLoaded;
	g_lampRefRoot = NewNode(vtNode, "CMB_HeadlampLight", 2);
	g_lampRefLight = NewNode(vtNode, "Light", 0);
	AddChild(g_lampRefRoot, g_lampRefLight);
	*(uint8_t **)(g_lampRefLight + 0x28) = g_lampRefRoot;
	{
		float *lrows = (float *)(g_lampRefLight + 0x30);
		lrows[0] = lrows[5] = lrows[10] = 1.0f;
		lrows[14] = 5.0f;   /* the light 5 above its root */
		lrows[15] = 1.0f;
		float *rr = (float *)(g_lampRefRoot + 0x30);
		rr[0] = rr[5] = rr[10] = 1.0f;
		rr[15] = 1.0f;
	}
	*(uint8_t **)(g_lampRefLoaded + 0x08) = g_lampRefRoot;
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

	/* The player camera, in third person. */
	static const char *camera[] = { ".?AVPlayerCamera@@", ".?AVTESCamera@@" };
	static const char *third[] = { ".?AVThirdPersonState@@", ".?AVTESCameraState@@" };
	uint8_t *cam = (uint8_t *)NewObject(MakeClass(camera, 2), 0x200);
	g_thirdState = (uint8_t *)NewObject(MakeClass(third, 2), 0x200);
	*(float *)(g_thirdState + 0xE8) = 0.4f;
	*(float *)(g_thirdState + 0xEC) = 0.4f;
	*(uint8_t **)(cam + 0x28) = g_thirdState;
	*(uint8_t **)(cam + 0xE0 + 8 * 8) = g_thirdState;
	*(uintptr_t *)(g_base + RVA_PLAYER_CAMERA) = (uintptr_t)cam;
	uint8_t *instance = (uint8_t *)NewObject(vtSkin, 0x100);
	*(int32_t *)(instance + 0x08) = 1;
	*(uint8_t **)(shape + 0x140) = instance;
	g_boneData = (uint8_t *)NewObject(vtBone, 0x100);
	*(int32_t *)(g_boneData + 0x08) = 2;   /* the shape's skin and the model cache */
	*(uint8_t **)(instance + 0x40) = g_boneData;
	g_bones = (uint8_t *)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	*(uint8_t **)(g_boneData + 0x10) = g_bones;
	*(uint32_t *)(g_boneData + 0x18) = 1;
	*(uint32_t *)(g_boneData + 0x20) = 1;
	uint8_t **comList = (uint8_t **)VirtualAlloc(NULL, 0x100, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	comList[0] = g_comNode;
	*(uint8_t ***)(instance + 0x28) = comList;   /* BSSkin::Instance::bones: the one bone, COM */
	*(uint32_t *)(instance + 0x30) = 1;
	*(uint32_t *)(instance + 0x38) = 1;
	/* The rider's body: its own skin instance, bone data (references: the skin and the model
	 * cache, as the game shares it with every NPC in the mesh) and two bones. */
	g_bodySkin = (uint8_t *)NewObject(vtSkin, 0x100);
	*(int32_t *)(g_bodySkin + 0x08) = 1;
	*(uint8_t **)(g_bodyShape + 0x140) = g_bodySkin;
	g_bodyData = (uint8_t *)NewObject(vtBone, 0x100);
	*(int32_t *)(g_bodyData + 0x08) = 2;
	*(uint8_t **)(g_bodySkin + 0x40) = g_bodyData;
	g_bodyBones = (uint8_t *)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	*(uint8_t **)(g_bodyData + 0x10) = g_bodyBones;
	*(uint32_t *)(g_bodyData + 0x18) = 10;
	*(uint32_t *)(g_bodyData + 0x20) = 10;
	uint8_t **bodyList = (uint8_t **)VirtualAlloc(NULL, 0x100, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	for (int i = 0; i < 10; i++)
		bodyList[i] = g_bodyNodes[i];
	*(uint8_t ***)(g_bodySkin + 0x28) = bodyList;
	*(uint32_t *)(g_bodySkin + 0x30) = 10;
	*(uint32_t *)(g_bodySkin + 0x38) = 10;
	/* A blood decal on the body: its own shape, a skin instance cloned from the body's (the same
	 * bone list; it points wherever the body's points when it's made: test 29). Not in the 3D yet. */
	g_decalShape = NewNode(vtTri, "BloodDecal:0", 0);
	*(uint8_t **)(g_decalShape + 0x28) = npcRoot;
	g_decalSkin = (uint8_t *)NewObject(vtSkin, 0x100);
	*(int32_t *)(g_decalSkin + 0x08) = 1;
	*(uint8_t **)(g_decalShape + 0x140) = g_decalSkin;
	*(uint8_t ***)(g_decalSkin + 0x28) = bodyList;
	*(uint32_t *)(g_decalSkin + 0x30) = 10;
	*(uint32_t *)(g_decalSkin + 0x38) = 10;

	/* The moving parts of the Harley build: three more shapes under the bike's node, each
	 * with its own skin and bone data (the same bind; their culling spheres on the axles
	 * and ahead of the steering head, which is how the plugin tells them apart). */
	static const char *partNames[3] = { "CMB_BikeWornRider_wheelF", "CMB_BikeWornRider_wheelR", "CMB_BikeWornRider_front_metal" };
	for (int i = 0; i < 3; i++) {
		uint8_t *part = NewNode(vtTri, partNames[i], 0);
		AddChild(g_bikeNode, part);
		*(uint8_t **)(part + 0x28) = g_bikeNode;
		uint8_t *inst = (uint8_t *)NewObject(vtSkin, 0x100);
		*(uint8_t **)(part + 0x140) = inst;
		g_partData[i] = (uint8_t *)NewObject(vtBone, 0x100);
		*(int32_t *)(g_partData[i] + 0x08) = 2;
		*(uint8_t **)(inst + 0x40) = g_partData[i];
		g_partBones[i] = (uint8_t *)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
		*(uint8_t **)(g_partData[i] + 0x10) = g_partBones[i];
		*(uint32_t *)(g_partData[i] + 0x18) = 1;
		*(uint32_t *)(g_partData[i] + 0x20) = 1;
		*(int32_t *)(inst + 0x08) = 1;
		*(uint8_t ***)(inst + 0x28) = comList;
		*(uint32_t *)(inst + 0x30) = 1;
		*(uint32_t *)(inst + 0x38) = 1;
	}

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
static void MulM3(const float a[9], const float b[9], float out[9])
{
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++)
			out[i * 3 + j] = a[i * 3] * b[j] + a[i * 3 + 1] * b[3 + j] + a[i * 3 + 2] * b[6 + j];
}

static void Apply3(const float R[9], const float v[3], float out[3])
{
	for (int i = 0; i < 3; i++)
		out[i] = R[i * 3] * v[0] + R[i * 3 + 1] * v[1] + R[i * 3 + 2] * v[2];
}

static void SetWorld(uint8_t *node, const float rot[9], const float pos[3], float scale)
{
	StoreRotation((float *)(node + 0x70), rot, g_rootTransposed);
	memcpy(node + 0xA0, pos, 12);
	*(float *)(node + 0xAC) = scale;
}

/* The player's 3D follows the player: the root at the player, turned by the heading; the
 * bones at offsets of it (the spine leant back, the Pip-Boy's bone turned and scaled). */
static void SyncFakeWorld(void)
{
	float h = *(float *)(g_player + 0xC8), c = cosf(h), sn = sinf(h);
	const float heading[9] = { c, sn, 0, -sn, c, 0, 0, 0, 1 };
	const float *pp = PlayerPos();
	static const float comOff[3] = { 0, 0, 60 }, pelvOff[3] = { 0, -5, 70 }, spineOff[3] = { 0, -3, 95 }, spine1Off[3] = { 0, -2, 105 }, pipOff[3] = { 25, 8, 85 };
	static const float zero[9] = { 0, 0, 0, 0, 0, 0, 0, 0, 0 };
	static const float leanBack[9] = { 1, 0, 0, 0, 0.96593f, -0.25882f, 0, 0.25882f, 0.96593f };   /* 15 deg about x */
	static const float rx40[9] = { 1, 0, 0, 0, 0.76604f, -0.64279f, 0, 0.64279f, 0.76604f }, rz20[9] = { 0.93969f, -0.34202f, 0, 0.34202f, 0.93969f, 0, 0, 0, 1 };
	float off[3], pos[3], rot[9], pipTurn[9];
	SetWorld(g_root, heading, pp, 1.0f);
	SetWorld(g_bikeNode, heading, pp, 1.0f);   /* the worn nif's root sits at the actor's */
	Apply3(heading, comOff, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_comNode, heading, pos, 1.0f);
	Apply3(heading, pelvOff, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[0], heading, pos, 1.0f);
	MulM3(heading, leanBack, rot);
	Apply3(heading, spineOff, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[1], rot, pos, 1.0f);
	Apply3(heading, spine1Off, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[2], rot, pos, 1.0f);
	SetWorld(g_bodyNodes[3], zero, pos, 0.0f);   /* hidden: no rotation, scale 0 */
	static const float shear[9] = { 1.0f, 0.3f, 0.0f, 0.0f, 0.9f, 0.1f, 0.2f, 0.0f, 1.1f };   /* a cloth bone's: not orthonormal */
	static const float clothOff[3] = { -12, -18, 90 };
	MulM3(heading, shear, rot);
	Apply3(heading, clothOff, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[4], rot, pos, 1.0f);
	static const float handOff[3] = { -20, 75, 120 };   /* about where the left grip is */
	Apply3(heading, handOff, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[5], heading, pos, 1.0f);
	static const float upperOff[3] = { -18, 42, 148 }, elbowOff[3] = { -26, 56, 132 };   /* the shoulder and the elbow, the arm bent */
	Apply3(heading, upperOff, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[6], heading, pos, 1.0f);
	Apply3(heading, elbowOff, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[7], heading, pos, 1.0f);
	static const float headOff[3] = { 0, -2, 160 }, jawOff[3] = { 0, 3, 152 };   /* the head's joint and a face bone under it */
	Apply3(heading, headOff, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[8], heading, pos, 1.0f);
	Apply3(heading, jawOff, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[9], heading, pos, 1.0f);
	MulM3(rz20, rx40, pipTurn);
	MulM3(heading, pipTurn, rot);
	Apply3(heading, pipOff, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_pipboyBone, rot, pos, 0.9f);
}

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
	/* The parts' spheres, bone space: A c + t for the bike-space centres the parts file names
	 * (the front axle (0.4, 99.6, 29.9), the rear (0.4, -36.7, 29.9), the bar assembly's (1, 85, 57)). */
	static const float spheres[3][4] = { { -44.27f, 99.6f, -0.4f, 31.0f }, { -44.27f, -36.7f, -0.4f, 31.0f }, { -17.17f, 85.0f, -1.0f, 60.0f } };
	for (int i = 0; i < 3; i++) {
		float *pb = (float *)g_partBones[i];
		memcpy(pb, spheres[i], sizeof(spheres[i]));
		StoreRotation(pb + 4, skinToBone, skinTransposed);
		pb[16] = -74.17f; pb[17] = 0.0f; pb[18] = 0.0f; pb[19] = 1.0f;
		memcpy(g_partBonesOriginal[i], g_partBones[i], sizeof(g_partBonesOriginal[i]));
	}
	/* The rider's body: two bones with binds of their own; the Pip-Boy's shape's own transform. */
	static const float bindRot[10][9] = { { 0, 0, 1, 0, 1, 0, -1, 0, 0 }, { 1, 0, 0, 0, 0, -1, 0, 1, 0 }, { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, { 0, 1, 0, -1, 0, 0, 0, 0, 1 }, { 1, 0, 0, 0, 1, 0, 0, 0, 1 },
	                                      { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, { 1, 0, 0, 0, 1, 0, 0, 0, 1 } };
	static const float bindPos[10][3] = { { 0, 0, -70 }, { 3, -95, 0 }, { 0, -100, 0 }, { 0, -120, 0 }, { 10, 20, -90 }, { 20, -75, -120 }, { 18, -42, -148 }, { 26, -56, -132 }, { 0, 2, -160 }, { 0, -3, -152 } };
	static const float bodySpheres[10][4] = { { 0, 0, 20, 40 }, { 0, 0, 30, 50 }, { 0, 0, 0, 0 }, { 0, 0, 5, 10 }, { 0, 0, 0, 8 }, { 0, 0, 0, 12 }, { 0, 0, 0, 14 }, { 0, 0, 0, 12 }, { 0, 0, 0, 14 }, { 0, 0, 0, 6 } };   /* the third: no vertices */
	for (int i = 0; i < 10; i++) {
		float *bb = (float *)(g_bodyBones + i * 0x50);
		memcpy(bb, bodySpheres[i], sizeof(bodySpheres[i]));
		StoreRotation(bb + 4, bindRot[i], skinTransposed);
		bb[16] = bindPos[i][0]; bb[17] = bindPos[i][1]; bb[18] = bindPos[i][2]; bb[19] = 1.0f;
	}
	memcpy(g_bodyBonesOriginal, g_bodyBones, sizeof(g_bodyBonesOriginal));
	float *pl = (float *)(g_pipboyShape + 0x30);
	static const float tenDeg[9] = { 0.98481f, -0.17365f, 0, 0.17365f, 0.98481f, 0, 0, 0, 1 };
	StoreRotation(pl, tenDeg, rootTransposed);
	pl[12] = 1.0f; pl[13] = 2.0f; pl[14] = 3.0f; pl[15] = 1.0f;
	memcpy(g_pipboyLocalOriginal, pl, sizeof(g_pipboyLocalOriginal));
	SyncFakeWorld();
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
	LARGE_INTEGER frequency, last, now;
	QueryPerformanceFrequency(&frequency);
	QueryPerformanceCounter(&last);
	while ((int32_t)(GetTickCount() - end) < 0) {
		QueryPerformanceCounter(&now);
		if (g_onFrame)
			g_onFrame((float)(now.QuadPart - last.QuadPart) / (float)frequency.QuadPart);
		last = now;
		SyncFakeWorld();
		((void (*)(Task *))g_task->vtbl[1])(g_task);
		Sleep(5);
	}
}

static bool Near(float a, float b) { return fabsf(a - b) < 1e-5f; }

/* The rotation the plugin put on the bike's mesh: R = A^T A', with A and A' the bind
 * (mesh -> bone) before and now, read the way round this "game" stores them. */
static void AppliedRotationOf(const uint8_t *orig, const uint8_t *live, float R[9])
{
	const float *o = (const float *)(orig + 0x10), *w = (const float *)(live + 0x10);
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

static void AppliedRotation(float R[9]) { AppliedRotationOf(g_bonesOriginal, g_bones, R); }

/* A wheel's spin: its map is Rx(theta) (the tilt is level on the flat): theta from the matrix. */
static float WheelAngle(int part)
{
	float M[9];
	AppliedRotationOf(g_partBonesOriginal[part], g_partBones[part], M);
	return atan2f(M[7], M[4]);
}

/* The turn about the steering axis u in a rotation M: 2 sin(phi) u is M's antisymmetric part. */
static float TurnAbout(const float M[9])
{
	const float u[3] = { 0.0f, -0.4f, 0.9165f };
	float v[3] = { M[7] - M[5], M[2] - M[6], M[3] - M[1] };
	return asinf((v[0] * u[0] + v[1] * u[1] + v[2] * u[2]) * 0.5f) * DEG;
}

static void LoadRotation(const float *rows, float m[9], bool transposed);

/* Where a bone's rewritten entry takes the world point X: the point's mesh position through
 * the original entry and the node undone, then through the copy and the node (rigid ones). */
static void MapBone(const uint8_t *node, const uint8_t *orig, const uint8_t *copy, const float X[3], float out[3])
{
	float N[9], A[9], B[9], v[3], u[3], p[3], q[3], Bp[3], Nq[3];
	LoadRotation((const float *)(node + 0x70), N, g_rootTransposed);
	LoadRotation((const float *)(orig + 0x10), A, g_skinTransposed);
	LoadRotation((const float *)(copy + 0x10), B, g_skinTransposed);
	const float *n = (const float *)(node + 0xA0), *a = (const float *)(orig + 0x40), *b = (const float *)(copy + 0x40);
	for (int i = 0; i < 3; i++)
		v[i] = X[i] - n[i];
	for (int i = 0; i < 3; i++)
		u[i] = N[i] * v[0] + N[3 + i] * v[1] + N[6 + i] * v[2] - a[i];   /* N^T v - a */
	for (int i = 0; i < 3; i++)
		p[i] = A[i] * u[0] + A[3 + i] * u[1] + A[6 + i] * u[2];          /* A^T */
	Apply3(B, p, Bp);
	for (int i = 0; i < 3; i++)
		q[i] = Bp[i] + b[i];
	Apply3(N, q, Nq);
	for (int i = 0; i < 3; i++)
		out[i] = Nq[i] + n[i];
}

static float Dist3(const float a[3], const float b[3])
{
	return sqrtf((a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]) + (a[2] - b[2]) * (a[2] - b[2]));
}

static void RemoveChild(uint8_t *node, const uint8_t *child)
{
	uint16_t *used = (uint16_t *)(node + 0x132);
	uint8_t **kids = *(uint8_t ***)(node + 0x128);
	for (unsigned i = 0; i < *used; i++)
		if (kids[i] == child) {
			for (unsigned j = i + 1; j < *used; j++)
				kids[j - 1] = kids[j];
			(*used)--;
			return;
		}
}

static float BarAngle(void)
{
	float M[9], T[9], Q[9];
	AppliedRotationOf(g_partBonesOriginal[2], g_partBones[2], M);
	AppliedRotation(T);   /* the fixed part's map is the tilt alone; the bars' is the tilt after their turn */
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++)
			Q[i * 3 + j] = T[i] * M[j] + T[3 + i] * M[3 + j] + T[6 + i] * M[6 + j];
	return TurnAbout(Q);
}

static bool IsIdentity(const float R[9])
{
	return fabsf(R[0] - 1.0f) < 0.01f && fabsf(R[4] - 1.0f) < 0.01f && fabsf(R[8] - 1.0f) < 0.01f;
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

/* The ground the rays see, to match: a plane through the player's feet rising `degrees` the
 * way the normal leans back from (the normal leaning back = uphill ahead). */
static void SetGroundTowards(const float dir[3], float degrees)
{
	g_slopeK = tanf(degrees / DEG);
	g_slopeO[0] = PlayerPos()[0];
	g_slopeO[1] = PlayerPos()[1];
	g_slopeD[0] = -dir[0];
	g_slopeD[1] = -dir[1];
	g_groundZ = PlayerPos()[2];
}

/* Flat ground at the player's feet for the rays (a slope test leaves its plane behind). */
static void FlatGround(void)
{
	g_slopeK = 0.0f;
	g_groundZ = PlayerPos()[2];
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
	SetGroundTowards(back, 20.0f);
	SetTilt(30.0f);
	RunFrames(1500);
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

	printf("tilt: the planted bike (AnimObjectA, no COM bind) under another name:\n");
	float *b = (float *)g_bones;
	const float identity[9] = { 1, 0, 0, 0, 1, 0, 0, 0, 1 };
	StoreRotation(b + 4, identity, g_skinTransposed);
	b[16] = b[17] = b[18] = 0.0f;
	memcpy(g_bonesOriginal, g_bones, sizeof(g_bonesOriginal));
	SetTilt(30.0f);
	RunFrames(1500);
	AppliedRotation(R);
	CHECK(*BoneDataRefs() == 3 && fabsf(R[8] - 0.93969f) < 0.01f, "found as our armor addon's shape and tilted (references %d)", *BoneDataRefs());
	SetTilt(0.0f);
	RunFrames(300);
	CHECK(memcmp(g_bones, g_bonesOriginal, 0x50) == 0 && *BoneDataRefs() == 2, "put back and let go of");
	strcpy(name, "CMB_BikeWornRider");
	SetLayouts(g_skinTransposed, g_rootTransposed);

	printf("tilt: a ride that ends by taking the bike off, then a new one on flat ground:\n");
	SetNormalTowards(back, 20.0f);
	SetGroundTowards(back, 20.0f);
	SetTilt(30.0f);
	RunFrames(1500);
	(*rootUsed)--;
	uint8_t *keep = *slotPart;
	*slotPart = NULL;
	RunFrames(300);   /* let go of: no longer worn */
	SetTilt(0.0f);
	RunFrames(300);
	(*rootUsed)++;
	*slotPart = keep;
	SetNormal(0.0f, 0.0f, 1.0f);
	FlatGround();
	SetTilt(30.0f);
	RunFrames(200);
	AppliedRotation(R);
	CHECK(acosf(R[8] > 1.0f ? 1.0f : R[8]) * DEG < 2.0f, "starts level, not from the last ride's pitch (%.1f deg)", acosf(R[8] > 1.0f ? 1.0f : R[8]) * DEG);
	SetTilt(0.0f);
	RunFrames(300);

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
	FlatGround();
}

/* Riding along: up a slope at a steady speed (negative speed: backwards), the ground's
 * normal jumping about by up to g_noise degrees every frame, as the game's does. */
static float g_rideSpeed, g_rideSlope, g_noise;
static unsigned g_seed = 12345;
static float Random(void) { g_seed = g_seed * 1103515245u + 12345u; return (float)((g_seed >> 8) & 0xFFFF) / 65535.0f; }
static void RideAlong(float dt)
{
	if (g_noise > 0.0f) {
		float dir[3] = { cosf(Random() * 6.2832f), sinf(Random() * 6.2832f), 0.0f };
		SetNormalTowards(dir, Random() * g_noise);
	}
	float d = g_rideSpeed * dt;
	PlayerPos()[0] += sinf(HEADING) * cosf(g_rideSlope / DEG) * d;
	PlayerPos()[1] += cosf(HEADING) * cosf(g_rideSlope / DEG) * d;
	PlayerPos()[2] += sinf(g_rideSlope / DEG) * d;
}

/* The player pulling round towards g_steerTarget (the game asks for it every frame),
 * moving forward along the heading the plugin lets them have at g_steerMove. */
static float g_steerTarget, g_steerMove;
static void SteerTowards(float dt)
{
	float *head = (float *)(g_player + 0xC8);
	PlayerPos()[0] += sinf(*head) * g_steerMove * dt;
	PlayerPos()[1] += cosf(*head) * g_steerMove * dt;
	*head = g_steerTarget;
}

/* One frame of the game's input and movement, and of the pushes it honours. */
static void FakeGameFrame(float dt)
{
	void **vt = *(void ***)g_moveHandler;
	void (*onButton)(uint8_t *, const FakeEvent *) = (void (*)(uint8_t *, const FakeEvent *))vt[8];
	float *move = (float *)(g_controls + 0x44);
	if (g_handlerStyle == 0) {
		FakeEvent e = { g_keyX, g_keyY, 0 };
		if (g_keyX != 0.0f || g_keyY != 0.0f || g_lastKeyX != 0.0f || g_lastKeyY != 0.0f)
			onButton(g_moveHandler, &e);
	} else if (g_handlerStyle == 1) {
		FakeEvent e = { g_keyX - g_lastKeyX, g_keyY - g_lastKeyY, 0 };
		if (e.x != 0.0f || e.y != 0.0f)
			onButton(g_moveHandler, &e);
	} else {
		move[0] = move[1] = 0.0f;   /* the game's own clear, outside the handler */
		FakeEvent ex = { g_keyX, 0.0f, 1 }, ey = { 0.0f, g_keyY, 2 };
		if (g_keyX != 0.0f)
			onButton(g_moveHandler, &ex);
		if (g_keyY != 0.0f)
			onButton(g_moveHandler, &ey);
		if (g_handlerStyle == 3)
			move[0] = move[1] = 0.0f;   /* a second batch with no event: cleared again after the keys (test 19) */
	}
	g_lastKeyX = g_keyX;
	g_lastKeyY = g_keyY;
	((void (*)(uint8_t *))vt[9])(g_moveHandler);

	float *prev = (float *)(g_controls + 0x5C), out[16];
	prev[0] = move[0];
	prev[1] = move[1];
	uint8_t *imove = g_controls + 0x30;
	((void (*)(uint8_t *, uint32_t, float *))(*(void ***)imove)[1])(imove, 0, out);
	float *head = (float *)(g_player + 0xC8);
	float d = remainderf(out[14] - *head, 6.2831853f), step = 6.2831853f * dt;
	*head += d > step ? step : d < -step ? -step : d;
	float dir = *head + ((g_honour & 8) ? out[2] : 0.0f), speed = out[8];
	if ((speed < 0.0f && !(g_honour & 16)) || g_frozen)
		speed = 0.0f;
	if (speed > 0.0f)
		speed = speed > 2.0f * g_creepDrag ? speed - 2.0f * g_creepDrag : 0.0f;   /* the output is 2 x the input */
	PlayerPos()[0] += sinf(dir) * speed * 450.0f * dt;
	PlayerPos()[1] += cosf(dir) * speed * 450.0f * dt;
	float *mod = (float *)(g_controller + 0x180), *t = (float *)(g_controller + 0x308);
	if ((g_honour & 1) && *t > 0.0f) {
		PlayerPos()[0] += mod[0] / HAVOK * dt;
		PlayerPos()[1] += mod[1] / HAVOK * dt;
		*t = *t > dt ? *t - dt : 0.0f;
	}
	PlayerPos()[0] += g_fakeVel[0] / HAVOK * dt;
	PlayerPos()[1] += g_fakeVel[1] / HAVOK * dt;
	g_fakeVel[0] = g_fakeVel[1] = 0.0f;   /* the game's own next frame: no input, no velocity */
	float *push = (float *)(g_controller + 0x1B0);
	if (g_honour & 32) {
		PlayerPos()[0] += push[0] / HAVOK;
		PlayerPos()[1] += push[1] / HAVOK;
	}
	push[0] = push[1] = 0.0f;   /* used up */
}

static float Along(const float from[2], float heading)
{
	return (PlayerPos()[0] - from[0]) * sinf(heading) + (PlayerPos()[1] - from[1]) * cosf(heading);
}

/* After the U-turn: riding back the other way. */
static void UTurnBack(float dt)
{
	float d = g_rideSpeed * dt;
	PlayerPos()[0] -= sinf(HEADING) * d;
	PlayerPos()[1] -= cosf(HEADING) * d;
}

static void Keys(float x, float y) { g_keyX = x; g_keyY = y; }
static float *MoveInput(void) { return (float *)(g_controls + 0x44); }

/* The input hook: riding with radius 180 / 50 and 60 deg/s stopped already set. */
static float Turned(float from) { return remainderf(*(float *)(g_player + 0xC8) - from, 6.2831853f) * DEG; }
static void Mark(float p0[2]) { p0[0] = PlayerPos()[0]; p0[1] = PlayerPos()[1]; }
static float Moved(const float p0[2]) { return hypotf(PlayerPos()[0] - p0[0], PlayerPos()[1] - p0[1]); }

/* Riding by the keys, and for g_slideLeft seconds sliding to the right at 100 a second
 * (the bike still going after a back press at speed with a side key held). */
static float g_slideLeft;
static void SlideAndDrive(float dt)
{
	FakeGameFrame(dt);
	if (g_slideLeft > 0.0f) {
		float h = *(float *)(g_player + 0xC8);
		PlayerPos()[0] += cosf(h) * 100.0f * dt;
		PlayerPos()[1] -= sinf(h) * 100.0f * dt;
		g_slideLeft -= dt;
	}
}

/* Riding by the keys with the camera swinging left at 60 degrees a second (the bike turns after it). */
static void TurnWhileRiding(float dt)
{
	FakeGameFrame(dt);
	g_camYaw -= 1.0472f * dt;
}

/* Turned on the spot at g_turnOnSpot radians a second (the game turning the player; no keys). */
static float g_turnOnSpot;
static bool g_haveParts;   /* this run has a parts file (the bars turn, the wheels spin) */
static void TurnOnTheSpot(float dt)
{
	float *head = (float *)(g_player + 0xC8);
	*head = fmodf(*head + g_turnOnSpot * dt + 6.2831853f, 6.2831853f);
}

/* Rolling backwards at 80 a second, no keys. */
static void RollOn(float dt)   /* the game's own run-down after the brake: still going forward at 500 whatever the input */
{
	FakeGameFrame(dt);
	float h = *(float *)(g_player + 0xC8);
	PlayerPos()[0] += sinf(h) * 500.0f * dt;
	PlayerPos()[1] += cosf(h) * 500.0f * dt;
}

static void RollBack(float dt)
{
	FakeGameFrame(dt);
	float h = *(float *)(g_player + 0xC8);
	PlayerPos()[0] -= sinf(h) * 80.0f * dt;
	PlayerPos()[1] -= cosf(h) * 80.0f * dt;
}

/* The Harley build's moving parts ([Parts] in the INI for this run): the wheels spin with
 * the distance ridden and back when reversing, the bar assembly turns with the turning. */
static void PartsTests(void)
{
	float *head = (float *)(g_player + 0xC8), p0[2], R[9], M[9], N[9], D[9];
	printf("moving parts: wheels spin with the distance, the bars turn with the turning:\n");
	g_camYaw = *head;
	g_handlerStyle = 2;
	g_honour = 4;
	FlatGround();
	Keys(0.0f, 0.0f);
	g_onFrame = FakeGameFrame;
	RunFrames(500);
	CHECK(*(int32_t *)(g_partData[0] + 0x08) == 3 && *(int32_t *)(g_partData[1] + 0x08) == 3 && *(int32_t *)(g_partData[2] + 0x08) == 3,
	      "the three parts' skins are held (references %d %d %d)", *(int32_t *)(g_partData[0] + 0x08), *(int32_t *)(g_partData[1] + 0x08), *(int32_t *)(g_partData[2] + 0x08));
	Keys(0.0f, 0.1f);   /* forward at about 90 a second */
	RunFrames(800);
	Mark(p0);
	float a0 = WheelAngle(0), b0 = WheelAngle(1);
	RunFrames(500);
	float d = Moved(p0);
	float da = remainderf(WheelAngle(0) - a0, 6.2831853f), db = remainderf(WheelAngle(1) - b0, 6.2831853f);
	CHECK(d > 20.0f && fabsf(da + d / 29.9f) < 0.3f && fabsf(db + d / 29.9f) < 0.3f,
	      "riding forward %.0f: both wheels turned %.2f and %.2f rad (%.2f: the top of the wheel going forward)", d, da, db, -d / 29.9f);
	AppliedRotation(R);
	CHECK(IsIdentity(R) && fabsf(BarAngle()) < 1.0f, "the fixed part not spun, the bars straight (%.1f deg)", BarAngle());
	Keys(0.0f, 0.0f);
	RunFrames(600);
	Keys(1.0f, 0.0f);   /* a right turn from a stop: 60 deg/s */
	RunFrames(1200);
	float bar = BarAngle();
	CHECK(bar < -8.0f && bar > -11.0f, "turning right at 60 a second: the bar assembly over %.1f deg (10 to the right)", bar);
	CHECK(*(float *)(g_partBones[2] + 0x0C) > 60.0f && *(float *)(g_partBones[2] + 0x0C) < 62.0f,
	      "its culling sphere grown by the little its centre moves (%.2f from 60)", *(float *)(g_partBones[2] + 0x0C));
	AppliedRotationOf(g_partBonesOriginal[0], g_partBones[0], M);
	AppliedRotationOf(g_partBonesOriginal[1], g_partBones[1], N);
	for (int i = 0; i < 3; i++)   /* D = M N^T: the front wheel's turn over the rear's spin */
		for (int j = 0; j < 3; j++)
			D[i * 3 + j] = M[i * 3] * N[j * 3] + M[i * 3 + 1] * N[j * 3 + 1] + M[i * 3 + 2] * N[j * 3 + 2];
	CHECK(fabsf(TurnAbout(D) - bar) < 1.0f, "the front wheel turned with the bars (%.1f deg) and spinning", TurnAbout(D));
	AppliedRotation(R);
	CHECK(IsIdentity(R), "the fixed part not turned");
	Keys(-1.0f, 0.0f);
	RunFrames(1500);
	bar = BarAngle();
	CHECK(bar > 8.0f && bar < 11.0f, "turning left: %.1f deg (10 to the left)", bar);
	Keys(0.0f, 0.0f);
	RunFrames(1000);
	CHECK(fabsf(BarAngle()) < 1.0f, "stopped: the bars back straight (%.1f deg)", BarAngle());
	Keys(0.0f, 1.0f);   /* at speed the bars go over less: 60% of the angle past 400 units/s */
	RunFrames(3500);
	g_onFrame = TurnWhileRiding;   /* the camera swinging left at 60 deg/s, the bike following */
	RunFrames(1000);
	bar = BarAngle();
	CHECK(bar > 4.5f && bar < 7.5f, "turning left at speed: the bars over %.1f deg (6: 60%% of 10)", bar);
	g_onFrame = FakeGameFrame;
	Keys(0.0f, 0.0f);
	RunFrames(3000);
	g_onFrame = RollBack;   /* the game moving the bike backwards (as a reverse does): the wheels turn the other way */
	RunFrames(800);
	Mark(p0);
	b0 = WheelAngle(1);
	RunFrames(500);
	d = Moved(p0);
	db = remainderf(WheelAngle(1) - b0, 6.2831853f);
	CHECK(d > 15.0f && fabsf(db - d / 29.9f) < 0.3f, "rolling back %.0f: the rear wheel turned %.2f rad the other way (%.2f)", d, db, d / 29.9f);
	g_onFrame = FakeGameFrame;
	RunFrames(400);
	g_onFrame = NULL;
}

static void InputTests(void)
{
	float *head = (float *)(g_player + 0xC8), from, p0[2];
	printf("input hook: a side key from a stop creeps round a small circle:\n");
	g_camYaw = *head;
	g_handlerStyle = 2;
	g_honour = 4;
	FlatGround();   /* flat ground where the player is (the slope tests left them up a hill) */
	Keys(0.0f, 0.0f);
	g_onFrame = FakeGameFrame;
	RunFrames(400);
	CHECK((*(void ***)g_moveHandler)[8] != (void *)FakeOnButton && (*(void ***)g_moveHandler)[9] != (void *)FakePerFrame &&
	      (*(void ***)g_moveHandler)[4] != (void *)FakeOnThumbstick, "the MovementHandler's button, thumbstick and per-frame functions are wrapped (its vtable page read-only)");
	CHECK((*(void ***)(g_controls + 0x30))[1] != (void *)FakeGetControllerOutput && g_outputCalls > 0,
	      "and the movement output, the game's still called (%d calls)", g_outputCalls);
	from = *head;
	Keys(1.0f, 0.0f);
	RunFrames(2000);
	float turned = Turned(from);
	CHECK(turned > 95.0f && turned < 135.0f, "right from a stop: turned %.0f deg right in 2 s (60 a second)", turned);
	Mark(p0);
	RunFrames(1000);
	float crept = Moved(p0);
	CHECK(crept > 35.0f && crept < 80.0f, "creeping forward at %.0f a second (about 58: round a 55 circle), not driven off", crept);
	CHECK(MoveInput()[0] == 0.0f && MoveInput()[1] > 0.0f && MoveInput()[1] < 0.1f, "the game gets no side input, a little forward (%.3f)", MoveInput()[1]);
	CHECK(((float *)(g_controls + 0x5C))[1] == MoveInput()[1], "and its movement used that (+5C)");
	g_frozen = true;   /* against something: the bike can't move */
	RunFrames(2500);
	float stuck = MoveInput()[1];
	CHECK(stuck > 0.5f, "stuck against something: the creep input winds up (%.2f; rough ground needs that too)", stuck);
	g_frozen = false;
	Mark(p0);
	RunFrames(500);
	float surge = Moved(p0);
	Mark(p0);
	RunFrames(1000);
	CHECK(surge < 120.0f, "free again: the surge is cut within a fraction of a second (%.0f in the first half second, at twice the game's gain)", surge);
	CHECK(Moved(p0) > 30.0f && Moved(p0) < 90.0f, "then it creeps on at about 58 (%.0f in the next second)", Moved(p0));
	Keys(0.0f, 0.0f);
	RunFrames(500);
	printf("input hook: a game that clears the input again after the keys on every frame (test 19):\n");
	g_handlerStyle = 3;
	Keys(1.0f, 0.0f);
	RunFrames(1500);
	from = *head;
	Mark(p0);
	RunFrames(1000);
	CHECK(Turned(from) > 45.0f && Moved(p0) > 30.0f && Moved(p0) < 90.0f,
	      "the creep goes on: turned %.0f deg and crept %.0f in a second, the input winding up as it should", Turned(from), Moved(p0));
	CHECK(((float *)(g_controls + 0x5C))[1] > 0.0f, "the movement got ours (+5C %.3f), not the clear", ((float *)(g_controls + 0x5C))[1]);
	Keys(0.0f, 0.0f);
	RunFrames(400);
	from = *head;
	Mark(p0);
	RunFrames(500);
	CHECK(Moved(p0) < 0.5f && fabsf(Turned(from)) < 0.1f, "let go of: it stops within the 0.2 s the keys are kept (then moved %.1f, turned %.1f deg)", Moved(p0), Turned(from));
	g_handlerStyle = 2;
	RunFrames(300);

	printf("input hook: rough ground, where the creep needs an input of 0.56:\n");
	g_creepDrag = 0.5f;
	Keys(1.0f, 0.0f);
	RunFrames(3500);
	Mark(p0);
	RunFrames(1000);
	CHECK(Moved(p0) > 30.0f && Moved(p0) < 90.0f && MoveInput()[1] > 0.5f, "the input winds up and it creeps at about 58 (%.0f a second, input %.2f)", Moved(p0), MoveInput()[1]);
	g_creepDrag = 0.0f;
	Keys(0.0f, 0.0f);
	RunFrames(500);
	Keys(1.0f, 0.0f);
	RunFrames(500);
	Mark(p0);
	RunFrames(500);
	CHECK(Moved(p0) < 80.0f, "on the flat again: no surge from the rough ground's input (%.0f in half a second)", Moved(p0));
	Keys(1.0f, 1.0f);
	RunFrames(300);
	CHECK(MoveInput()[0] > 0.1f && MoveInput()[0] < 0.6f && fabsf(MoveInput()[1] - MoveInput()[0]) < 0.01f,
	      "forward and right: the keys' direction kept, the whole vector building up (%.2f, %.2f after 0.3 s)", MoveInput()[0], MoveInput()[1]);
	Keys(0.0f, 0.0f);
	RunFrames(2500);

	printf("input hook: the throttle (test 21: the game's speed came and went at once):\n");
	Keys(0.0f, 1.0f);
	RunFrames(500);
	Mark(p0);
	RunFrames(250);
	float early = Moved(p0) * 4.0f;
	CHECK(early > 60.0f && early < 600.0f, "half a second in: %.0f a second, building up (900 at the top)", early);
	RunFrames(3000);
	Mark(p0);
	RunFrames(250);
	float top = Moved(p0) * 4.0f;
	CHECK(top > 800.0f, "3.5 s in: %.0f a second, at the top", top);
	g_frozen = true;   /* against something, W still held (test 23: the throttle sat at 0.8 on a hillside) */
	RunFrames(2000);
	g_frozen = false;
	Mark(p0);
	RunFrames(250);
	float freed = Moved(p0) * 4.0f;
	CHECK(freed > 100.0f && freed < 450.0f, "stuck for 2 s with W held, then free: no lunge (%.0f a second in the first quarter second: the throttle held to the measured speed plus Lead)", freed);
	RunFrames(2500);
	Keys(0.0f, 0.0f);
	RunFrames(400);
	Mark(p0);
	RunFrames(250);
	float coasting = Moved(p0) * 4.0f;
	CHECK(coasting > 150.0f && coasting < 880.0f, "let go of: still rolling at %.0f a second after 0.4 s (coasting)", coasting);
	RunFrames(2500);
	Mark(p0);
	RunFrames(300);
	CHECK(Moved(p0) < 2.0f, "and stopped within the 2 s of coasting (moved %.1f)", Moved(p0));
	Keys(0.0f, 1.0f);
	RunFrames(2000);
	Mark(p0);
	from = *head;
	Keys(0.0f, -1.0f);   /* back while rolling: a brake first */
	RunFrames(300);
	float braking = Along(p0, from);
	CHECK(braking > 30.0f && braking < 240.0f, "back pressed while rolling: still rolling on, braking (%.0f on in the first 0.3 s, 270 unbraked)", braking);
	RunFrames(1500);
	float backed = Along(p0, from);
	CHECK(backed < braking - 40.0f, "then backing up (%.0f along the heading from the press)", backed);
	Keys(0.0f, 0.0f);
	RunFrames(600);
	Keys(0.0f, 0.0f);
	RunFrames(600);

	printf("input hook: back held while the bike still rolls on (the game's own run-down): no reverse until it has stopped (test 23):\n");
	Keys(0.0f, 1.0f);
	RunFrames(2000);
	Keys(0.0f, -1.0f);
	RunFrames(600);
	g_onFrame = RollOn;
	Mark(p0);
	from = *head;
	RunFrames(800);
	float rolledOn = Along(p0, from);
	CHECK(rolledOn > 380.0f && rolledOn < 420.0f, "rolling on at 500 for 0.8 s with S held: not pushed back meanwhile (%.0f along the heading, 400 unpushed)", rolledOn);
	g_onFrame = FakeGameFrame;
	Mark(p0);
	from = *head;
	RunFrames(1500);
	CHECK(Along(p0, from) < -40.0f, "stopped: then backing up (%.0f along the heading in 1.5 s)", Along(p0, from));
	Keys(0.0f, 0.0f);
	RunFrames(800);

	printf("input hook: back pressed at speed with a side key, the bike still sliding (test 20): no verdict on the method:\n");
	g_camYaw = *head;
	Keys(0.0f, 1.0f);   /* riding at 900 */
	RunFrames(1200);
	Keys(1.0f, -1.0f);  /* back and right while still going: the plugin stops the drive, the slide goes on */
	g_slideLeft = 0.6f;
	g_onFrame = SlideAndDrive;
	RunFrames(900);
	g_onFrame = FakeGameFrame;
	Keys(0.0f, 0.0f);
	RunFrames(400);

	printf("input hook: back gets the game nothing; the bike backs up in steps after rays (this game honours SetPosition):\n");
	g_camYaw = *head;
	from = *head;
	Mark(p0);
	Keys(0.0f, -1.0f);
	RunFrames(1500);
	CHECK(MoveInput()[0] == 0.0f && MoveInput()[1] == 0.0f && signbit(MoveInput()[1]), "the game gets (-0, -0): ours, told apart from its own clear");
	float along = Along(p0, from);
	CHECK(along < -60.0f, "backing up: %.0f along the heading in 1.5 s", along);
	Mark(p0);
	RunFrames(1000);
	along = Along(p0, from);
	CHECK(along < -60.0f && along > -100.0f, "the speed learnt: %.0f in the next second (80)", along);
	CHECK(fabsf(Turned(from)) < 0.01f, "facing forward all the way (%.2f deg off)", Turned(from));
	Keys(1.0f, -1.0f);
	RunFrames(1000);
	turned = Turned(from);
	CHECK(turned < -25.0f && turned > -75.0f, "back and right: the rear swings right, the nose %.0f deg left in a second", turned);
	Keys(0.0f, -1.0f);
	RunFrames(300);
	from = *head;
	RunFrames(500);
	CHECK(fabsf(Turned(from)) < 0.5f, "right let go of, still backing: the turning stops (%.2f deg), the key doesn't stick", Turned(from));
	Keys(0.0f, 0.0f);
	RunFrames(300);
	from = *head;
	Mark(p0);
	RunFrames(600);
	CHECK(Moved(p0) < 0.5f && fabsf(Turned(from)) < 0.1f, "back let go of: the bike stands, no creep from a stale side key (moved %.1f, turned %.1f deg)",
	      Moved(p0), Turned(from));

	printf("input hook: a game that adds the change on a press or release:\n");
	g_handlerStyle = 1;
	MoveInput()[0] = MoveInput()[1] = 0.0f;
	g_lastKeyX = g_lastKeyY = 0.0f;
	Keys(0.0f, -1.0f);
	RunFrames(300);
	CHECK(MoveInput()[0] == 0.0f && MoveInput()[1] == 0.0f, "back pressed: the game gets (0, 0)");
	Keys(0.0f, 0.0f);
	RunFrames(300);
	CHECK(MoveInput()[0] == 0.0f && MoveInput()[1] == 0.0f && !signbit(MoveInput()[1]), "released: its own (0, 0), not forward (got %.2f)", MoveInput()[1]);
	g_handlerStyle = 2;

	printf("input hook: after a load, a test ray that finds no ground is tried again 3 s later:\n");
	Send(3, 1);   /* PostLoadGame */
	RunFrames(400);
	g_camYaw = *head;
	from = *head;
	float ground = PlayerPos()[2];
	g_groundZ = ground - 500.0f;
	Mark(p0);
	int picks = g_picks;
	Keys(0.0f, -1.0f);
	RunFrames(1000);
	CHECK(Moved(p0) < 0.5f, "no ground under the test ray: back brakes (moved %.1f)", Moved(p0));
	g_groundZ = ground;
	RunFrames(4000);
	CHECK(g_picks > picks && Moved(p0) > 100.0f, "tried again: rays work, it backs up %.0f (%d rays)", Moved(p0), g_picks - picks);
	Keys(0.0f, 0.0f);
	RunFrames(300);

	printf("input hook: a wall 400 behind:\n");
	float back[2] = { -sinf(from), -cosf(from) }, right[2] = { cosf(from), -sinf(from) };
	Mark(p0);
	FakePlane *wall = &g_planes[0];
	wall->point[0] = p0[0] + back[0] * 400.0f;
	wall->point[1] = p0[1] + back[1] * 400.0f;
	wall->normal[0] = -back[0];
	wall->normal[1] = -back[1];
	wall->layer = 1;
	wall->on = true;
	Keys(0.0f, -1.0f);
	RunFrames(6000);
	float gap = (PlayerPos()[0] - wall->point[0]) * wall->normal[0] + (PlayerPos()[1] - wall->point[1]) * wall->normal[1];
	CHECK(Moved(p0) > 150.0f && gap > 145.0f && gap < 195.0f, "backs up %.0f and stops %.0f short of the wall (BackClearance 150)", Moved(p0), gap);
	Keys(0.0f, 0.0f);
	RunFrames(300);
	wall->on = false;

	printf("input hook: a trigger volume 80 behind (not solid):\n");
	Mark(p0);
	FakePlane *trigger = &g_planes[1];
	trigger->point[0] = p0[0] + back[0] * 80.0f;
	trigger->point[1] = p0[1] + back[1] * 80.0f;
	trigger->normal[0] = -back[0];
	trigger->normal[1] = -back[1];
	trigger->layer = 12;
	trigger->on = true;
	Keys(0.0f, -1.0f);
	RunFrames(2000);
	CHECK(Moved(p0) > 120.0f, "backs up through it (%.0f)", Moved(p0));
	Keys(0.0f, 0.0f);
	RunFrames(300);
	trigger->on = false;

	printf("input hook: a tin can (layer 4) 90 behind:\n");
	Mark(p0);
	FakePlane *can = &g_planes[1];
	can->point[0] = p0[0] + back[0] * 90.0f;
	can->point[1] = p0[1] + back[1] * 90.0f;
	can->normal[0] = -back[0];
	can->normal[1] = -back[1];
	can->layer = 4;
	can->on = true;
	Keys(0.0f, -1.0f);
	RunFrames(2000);
	CHECK(Moved(p0) > 120.0f, "backed over (%.0f)", Moved(p0));
	Keys(0.0f, 0.0f);
	RunFrames(300);
	can->on = false;

	printf("input hook: a pile of six bits of clutter 150 behind (the ray under the rear goes down through them):\n");
	Mark(p0);
	g_pilePoint[0] = p0[0] + back[0] * 150.0f;
	g_pilePoint[1] = p0[1] + back[1] * 150.0f;
	g_pileCount = 6;
	Keys(0.0f, -1.0f);
	RunFrames(2500);
	CHECK(Moved(p0) > 150.0f, "not taken for a drop: backs up over it (%.0f)", Moved(p0));
	Keys(0.0f, 0.0f);
	RunFrames(300);
	g_pileCount = 0;

	printf("input hook: a chain-link fence (layer 26) 300 behind:\n");
	Mark(p0);
	FakePlane *fence = &g_planes[0];
	fence->point[0] = p0[0] + back[0] * 300.0f;
	fence->point[1] = p0[1] + back[1] * 300.0f;
	fence->normal[0] = -back[0];
	fence->normal[1] = -back[1];
	fence->layer = 26;
	fence->on = true;
	Keys(0.0f, -1.0f);
	RunFrames(4000);
	gap = (PlayerPos()[0] - fence->point[0]) * fence->normal[0] + (PlayerPos()[1] - fence->point[1]) * fence->normal[1];
	CHECK(gap > 145.0f && gap < 195.0f, "stops %.0f short of it", gap);
	Keys(0.0f, 0.0f);
	RunFrames(300);
	fence->on = false;

	printf("input hook: down a 30 deg slope behind:\n");
	from = *head;
	Mark(p0);
	g_slopeK = -0.57735f;
	g_slopeO[0] = p0[0];
	g_slopeO[1] = p0[1];
	g_slopeD[0] = -sinf(from);
	g_slopeD[1] = -cosf(from);
	g_groundZ = PlayerPos()[2];
	SetState(2);   /* the controller says in the air all the way down (test 18) */
	Keys(0.0f, -1.0f);
	RunFrames(3000);
	float groundHere = g_groundZ + g_slopeK * ((PlayerPos()[0] - g_slopeO[0]) * g_slopeD[0] + (PlayerPos()[1] - g_slopeO[1]) * g_slopeD[1]);
	CHECK(Moved(p0) > 150.0f && PlayerPos()[2] - groundHere > -1.5f && PlayerPos()[2] - groundHere < 1.0f,
	      "backs down it %.0f, the wheels on the ground (%+.1f)", Moved(p0), PlayerPos()[2] - groundHere);
	CHECK(Park(6) > 0.5f, "the controller said in the air all the way, the rays said on the ground: the track kept (a park spot on the slope, up z %.2f)", Park(6));
	SetState(0);
	Keys(0.0f, 0.0f);
	RunFrames(300);
	g_slopeK = 0.0f;
	g_groundZ = PlayerPos()[2];

	printf("input hook: a car 35 to the right of the bike, back and right:\n");
	from = *head;
	Mark(p0);
	FakePlane *car = &g_planes[2];
	car->point[0] = p0[0] + right[0] * 35.0f;
	car->point[1] = p0[1] + right[1] * 35.0f;
	car->normal[0] = -right[0];
	car->normal[1] = -right[1];
	car->layer = 1;
	car->on = true;
	Keys(1.0f, -1.0f);
	RunFrames(2000);
	float turnedBy = Turned(from), h1 = *head;
	float corner[2] = { PlayerPos()[0] - sinf(h1) * 150.0f + cosf(h1) * 20.0f, PlayerPos()[1] - cosf(h1) * 150.0f - sinf(h1) * 20.0f };
	float inside = (corner[0] - car->point[0]) * car->normal[0] + (corner[1] - car->point[1]) * car->normal[1];
	CHECK(turnedBy > -12.0f && turnedBy < -1.0f && inside >= 0.0f,
	      "the rear swings right until its corner reaches the car (%.1f deg, %.1f units clear), not into it", turnedBy, inside);
	CHECK(Moved(p0) < 40.0f, "then it stops: angled at the car, straight back would hit it too (moved %.0f)", Moved(p0));
	Mark(p0);
	from = *head;
	Keys(-1.0f, -1.0f);
	RunFrames(1500);
	CHECK(Turned(from) > 20.0f && Moved(p0) > 60.0f, "back and left: the rear swings away from it (%.0f deg), backing up again (%.0f)",
	      Turned(from), Moved(p0));
	Keys(0.0f, 0.0f);
	RunFrames(300);
	car->on = false;

	printf("input hook: a drop 250 behind:\n");
	from = *head;
	back[0] = -sinf(from);
	back[1] = -cosf(from);
	Mark(p0);
	g_dropPoint[0] = p0[0] + back[0] * 250.0f;
	g_dropPoint[1] = p0[1] + back[1] * 250.0f;
	g_dropDir[0] = back[0];
	g_dropDir[1] = back[1];
	g_dropOn = true;
	Keys(0.0f, -1.0f);
	RunFrames(5000);
	float edge = (g_dropPoint[0] - PlayerPos()[0]) * back[0] + (g_dropPoint[1] - PlayerPos()[1]) * back[1];
	CHECK(Moved(p0) > 50.0f && edge > 135.0f && edge < 195.0f, "backs up %.0f and stops %.0f short of the edge (the rear wheel at it)", Moved(p0), edge);
	Keys(0.0f, 0.0f);
	RunFrames(300);
	g_dropOn = false;

	printf("input hook: a game that doesn't honour SetPosition: back brakes:\n");
	Send(3, 1);
	g_honour = 0;
	RunFrames(400);
	g_camYaw = *head;
	from = *head;
	Keys(0.0f, -1.0f);
	RunFrames(2200);
	Mark(p0);
	RunFrames(600);
	CHECK(Moved(p0) < 0.5f && MoveInput()[1] == 0.0f, "stands still (not driven forward), facing forward (%.2f deg off)", Turned(from));
	Keys(0.0f, 0.0f);
	RunFrames(300);

	printf("input hook: a failed trial is tried again from a stop 3 s later (the game honouring SetPosition now):\n");
	g_honour = 4;
	RunFrames(3200);
	from = *head;
	Mark(p0);
	Keys(0.0f, -1.0f);
	RunFrames(1500);
	along = Along(p0, from);
	CHECK(along < -60.0f, "backing up again: %.0f along the heading in 1.5 s", along);
	Keys(0.0f, 0.0f);
	RunFrames(300);

	printf("input hook: not riding, the keys go through:\n");
	SetLive(0.0f);
	RunFrames(400);
	Keys(0.0f, -1.0f);
	RunFrames(300);
	CHECK(MoveInput()[1] == -1.0f, "back reaches the game (%.2f)", MoveInput()[1]);
	Keys(0.0f, 0.0f);
	RunFrames(200);
	g_onFrame = NULL;
	*head = from;
	SetLive(60.0f);
	RunFrames(400);
}

/* BackPush=mod (its own run): the controller's velocityMod, and put back on letting go. */
static void BackPushModTests(void)
{
	float *head = (float *)(g_player + 0xC8), from, p0[2];
	float *mod = (float *)(g_controller + 0x180), *modTime = (float *)(g_controller + 0x308);
	printf("BackPush=mod: backing up by the controller's velocityMod:\n");
	*(float *)(g_turnRadius + 0x30) = 180.0f;
	*(float *)(g_turnSlow + 0x30) = 50.0f;
	*(float *)(g_turnStand + 0x30) = 60.0f;
	SetNormal(0.0f, 0.0f, 1.0f);
	FlatGround();
	SetState(0);
	SetLive(60.0f);
	g_handlerStyle = 2;
	g_honour = 1;
	g_camYaw = *head;
	g_onFrame = FakeGameFrame;
	RunFrames(600);
	from = *head;
	Mark(p0);
	Keys(0.0f, -1.0f);
	RunFrames(1500);
	float along = Along(p0, from);
	CHECK(along < -60.0f && along > -140.0f, "backed up %.0f along the heading in 1.5 s", along);
	Keys(0.0f, 0.0f);
	RunFrames(300);
	CHECK(mod[0] == 0.0f && mod[1] == 0.0f && *modTime == 0.0f, "letting go: velocityMod and its time put back");
	g_onFrame = NULL;
	SetLive(0.0f);
	RunFrames(300);
}

static float *Zoom(int current) { return (float *)(g_thirdState + (current ? 0xEC : 0xE8)); }

static void ZoomTests(void)
{
	printf("camera: zoom all the way out while riding:\n");
	SetCamera(0.0f);
	RunFrames(300);
	*Zoom(0) = *Zoom(1) = 0.4f;
	SetCamera(450.0f);
	RunFrames(500);
	CHECK(*Zoom(0) == 1.0f && *Zoom(1) == 1.0f, "getting on: zoomed out (target %g, current %g)", *Zoom(0), *Zoom(1));
	RunFrames(2000);
	*Zoom(0) = 0.7f;   /* the player zooms in a little with the mouse wheel */
	RunFrames(500);
	CHECK(*Zoom(0) == 0.7f, "after two seconds the zoom is the player's again (%g)", *Zoom(0));
	SetCamera(0.0f);
	RunFrames(300);
	CHECK(*Zoom(0) == 0.4f && *Zoom(1) == 0.4f, "getting off: the zoom from before (%g, %g)", *Zoom(0), *Zoom(1));

	printf("camera: zoom values that aren't fractions:\n");
	*Zoom(0) = *Zoom(1) = 150.0f;
	SetCamera(450.0f);
	RunFrames(500);
	CHECK(*Zoom(0) == 150.0f && *Zoom(1) == 150.0f, "left alone");
	SetCamera(0.0f);
	RunFrames(300);
	CHECK(*Zoom(0) == 150.0f, "and still left alone after");
	*Zoom(0) = *Zoom(1) = 0.4f;
}

static void TrackTests(void)
{
	const float back[3] = { -sinf(HEADING), -cosf(HEADING), 0.0f };
	printf("park: riding up a 10 deg slope, then stopping:\n");
	SetNormalTowards(back, 10.0f);
	SetGroundTowards(back, 10.0f);
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

	printf("park: riding up a 40 deg slope:\n");
	SetNormalTowards(back, 40.0f);
	SetGroundTowards(back, 40.0f);
	g_rideSlope = 40.0f;
	g_onFrame = RideAlong;
	RunFrames(1500);
	g_onFrame = NULL;
	RunFrames(300);
	ez = PlayerPos()[2] - sinf(40.0f / DEG) * behind;
	CHECK(Park(6) > 0.6f && fabsf(Park(2) - ez) < 1.0f, "a spot on the steep track too (z %.1f, expected %.1f; up z %.3f)", Park(2), ez, Park(6));

	printf("tilt: riding up a 10 deg slope, the ground's normal all over the place:\n");
	SetGroundTowards(back, 10.0f);   /* the rays see the slope itself; only the normal is noisy */
	SetTilt(30.0f);
	g_noise = 40.0f;
	g_rideSpeed = 300.0f;
	g_rideSlope = 10.0f;
	g_onFrame = RideAlong;
	RunFrames(2000);
	float R[9];
	AppliedRotation(R);
	float pitch = asinf(R[7]) * DEG;
	CHECK(fabsf(pitch - 10.0f) < 1.5f, "pitched by the track (by the rays under the wheels where they work): %.1f deg (10)", pitch);
	printf("tilt: backwards down that slope:\n");
	g_rideSpeed = -150.0f;   /* reversing back down the same slope */
	RunFrames(2000);
	AppliedRotation(R);
	pitch = asinf(R[7]) * DEG;
	CHECK(fabsf(pitch - 10.0f) < 1.5f, "still nose up, the ground rises ahead of it: %.1f deg", pitch);
	g_onFrame = NULL;
	g_noise = 0.0f;
	RunFrames(500);
	AppliedRotation(R);
	CHECK(fabsf(asinf(R[7]) * DEG - pitch) < 1.0f, "standing still: holds (%.1f deg)", asinf(R[7]) * DEG);
	SetTilt(0.0f);
	SetNormalTowards(back, 10.0f);
	g_rideSpeed = 300.0f;
	g_rideSlope = 10.0f;

	printf("park: up a 60 deg rock face, then getting off:\n");
	SetNormal(0.0f, 0.0f, 1.0f);
	FlatGround();
	g_rideSlope = 0.0f;
	g_onFrame = RideAlong;
	RunFrames(1300);
	SetNormalTowards(back, 60.0f);
	SetGroundTowards(back, 60.0f);
	g_rideSlope = 60.0f;
	RunFrames(900);
	g_onFrame = NULL;
	RunFrames(300);
	CHECK(fabsf(*(float *)(g_trackSlope + 0x30) - 60.0f) < 2.0f, "CMB_TrackSlope says %.1f deg (the script won't let you off)", *(float *)(g_trackSlope + 0x30));
	float fdx = Park(0) - PlayerPos()[0], fdy = Park(1) - PlayerPos()[1], fdz = Park(2) - PlayerPos()[2];
	CHECK(Park(6) > 0.9f && sqrtf(fdx * fdx + fdy * fdy + fdz * fdz) > 140.0f,
	      "the spot is back down on the flat (up z %.2f, %.0f away)", Park(6), sqrtf(fdx * fdx + fdy * fdy + fdz * fdz));
	SetNormal(0.0f, 0.0f, 1.0f);
	FlatGround();

	printf("tilt: up a 10 deg slope, then turned on the spot:\n");
	SetTilt(30.0f);
	SetNormalTowards(back, 10.0f);
	SetGroundTowards(back, 10.0f);
	g_rideSlope = 10.0f;
	g_rideSpeed = 300.0f;
	g_onFrame = RideAlong;
	RunFrames(1500);
	g_onFrame = NULL;
	RunFrames(300);
	float *head = (float *)(g_player + 0xC8), heading0 = *head;
	SetNormal(0.0f, 0.0f, 1.0f);   /* the normal says flat: must not be used now */
	*head = heading0 + 1.5708f;
	RunFrames(800);
	AppliedRotation(R);
	if (g_picks)   /* the rays under the wheels say what the ground does as the bike turns on it */
		CHECK(fabsf(asinf(R[7]) * DEG) < 1.5f, "a quarter turn: across the slope by the rays under the wheels, level (%.1f deg)", asinf(R[7]) * DEG);
	else
		CHECK(fabsf(asinf(R[7]) * DEG - 10.0f) < 1.0f, "a quarter turn: the pitch holds (%.1f deg)", asinf(R[7]) * DEG);
	*head = heading0 + 3.14159f;
	RunFrames(800);
	AppliedRotation(R);
	if (g_picks)
		CHECK(fabsf(asinf(R[7]) * DEG + 10.0f) < 1.5f, "a half turn: nose down the slope by the rays (%.1f deg)", asinf(R[7]) * DEG);
	else
		CHECK(fabsf(asinf(R[7]) * DEG - 10.0f) < 1.0f, "a half turn: still holds, no flip (%.1f deg)", asinf(R[7]) * DEG);
	*head = heading0;
	SetTilt(0.0f);
	RunFrames(300);

	printf("steering: a 300 turning radius, 20 deg/s when stopped:\n");
	*(float *)(g_turnRadius + 0x30) = 300.0f;
	*(float *)(g_turnStand + 0x30) = 20.0f;
	SetNormal(0.0f, 0.0f, 1.0f);
	FlatGround();
	g_rideSlope = 0.0f;
	RunFrames(300);
	g_steerTarget = heading0 + 1.5708f;   /* the player pulls round to the right */
	g_onFrame = SteerTowards;
	RunFrames(1000);
	g_onFrame = NULL;
	float turned = (*head - heading0) * DEG;
	CHECK(turned > 5.0f && turned < 30.0f, "stopped: turned %.1f deg in a second (about 20), not 90", turned);
	float from = *head;   /* the plugin won't let the heading jump back either: start from here */
	SetTilt(30.0f);
	g_steerTarget = from + 1.5708f;
	g_steerMove = 300.0f;
	g_onFrame = SteerTowards;
	RunFrames(1000);
	g_onFrame = NULL;
	turned = (*head - from) * DEG;
	CHECK(turned > 25.0f && turned < 62.0f, "at 300 a second: turned %.1f deg in a second (at most 57), not 90", turned);
	{
		float R2[9];
		AppliedRotation(R2);
		float lean = asinf(R2[2] > 1.0f ? 1.0f : R2[2] < -1.0f ? -1.0f : R2[2]) * DEG;
		CHECK(lean > 8.0f && lean < 21.0f, "leaning into the turn, right side down (%.1f deg; at most MaxLean 20)", lean);
	}
	SetTilt(0.0f);
	RunFrames(500);
	g_steerMove = 0.0f;
	printf("steering: the radius from 50 at walking pace to 180 at riding speed (900), 60 deg/s stopped:\n");
	*(float *)(g_turnRadius + 0x30) = 180.0f;
	*(float *)(g_turnSlow + 0x30) = 50.0f;
	*(float *)(g_turnStand + 0x30) = 60.0f;
	g_steerMove = 0.0f;
	g_steerTarget = *head;
	g_onFrame = SteerTowards;
	RunFrames(300);
	from = *head;
	g_steerTarget = from + 1.5708f;
	RunFrames(500);
	turned = (*head - from) * DEG;
	CHECK(turned > 20.0f && turned < 38.0f, "stopped: %.1f deg in half a second (about 30)", turned);
	from = *head;
	g_steerTarget = from + 1.5708f;
	g_steerMove = 300.0f;
	RunFrames(1000);
	turned = (*head - from) * DEG;
	CHECK(turned > 85.0f, "at 300 a second (radius about 93): the quarter turn done within a second (%.1f deg)", turned);
	g_onFrame = NULL;
	g_steerMove = 0.0f;

	InputTests();
	PartsTests();
	g_onFrame = NULL;

	*(float *)(g_turnRadius + 0x30) = 0.0f;
	RunFrames(200);
	*head = heading0 + 1.5708f;
	RunFrames(200);
	CHECK(fabsf(*head - heading0 - 1.5708f) < 0.001f, "turning radius 0: steering left alone");
	*head = heading0;

	printf("steepness: turned sideways on a 60 deg face, and a level ride with a wild normal:\n");
	SetNormalTowards(back, 60.0f);
	SetGroundTowards(back, 60.0f);
	g_rideSlope = 60.0f;
	g_rideSpeed = 300.0f;
	g_onFrame = RideAlong;
	RunFrames(800);
	g_onFrame = NULL;
	*head = heading0 + 1.5708f;
	RunFrames(400);
	CHECK(*(float *)(g_trackSlope + 0x30) > 55.0f, "turned on the face: still %.1f deg steep (refused)", *(float *)(g_trackSlope + 0x30));
	*head = heading0;
	g_rideSlope = 0.0f;
	FlatGround();
	g_noise = 70.0f;
	g_onFrame = RideAlong;
	RunFrames(1500);
	g_onFrame = NULL;
	g_noise = 0.0f;
	RunFrames(300);
	CHECK(*(float *)(g_trackSlope + 0x30) < 10.0f, "level, normal all over the place: %.1f deg (not refused)", *(float *)(g_trackSlope + 0x30));

	printf("park: along a steep side slope:\n");
	SetNormal(0.0f, 0.0f, 1.0f);
	FlatGround();
	g_onFrame = RideAlong;
	RunFrames(1300);   /* level ground first */
	const float sideways[3] = { cosf(HEADING), -sinf(HEADING), 0.0f };
	SetNormalTowards(sideways, 40.0f);   /* then a 40 deg slope falling away to the right, ridden level */
	SetGroundTowards(sideways, 40.0f);
	RunFrames(1300);
	g_onFrame = NULL;
	RunFrames(300);
	CHECK(Park(6) > 0.934f, "the spot is back where the ground leans 20 deg or less across the bike (up z %.3f)", Park(6));
	SetNormal(0.0f, 0.0f, 1.0f);
	FlatGround();

	printf("park: a U-turn just before stopping:\n");
	g_rideSlope = 0.0f;
	SetNormal(0.0f, 0.0f, 1.0f);
	g_onFrame = RideAlong;
	RunFrames(1000);
	g_onFrame = NULL;
	float *h = (float *)(g_player + 0xC8);
	heading0 = *h;
	for (int i = 1; i <= 18; i++) {   /* half a circle of radius ~50 */
		*h = heading0 + 3.14159265f * (float)i / 18.0f;
		PlayerPos()[0] += sinf(*h) * 8.7f;
		PlayerPos()[1] += cosf(*h) * 8.7f;
		RunFrames(20);
	}
	g_rideSpeed = 300.0f;
	g_onFrame = UTurnBack;
	RunFrames(250);   /* about 75 units back the other way */
	g_onFrame = NULL;
	RunFrames(300);
	*h = heading0;
	float dx = Park(0) - PlayerPos()[0], dy = Park(1) - PlayerPos()[1];
	CHECK(Park(6) > 0.9f && sqrtf(dx * dx + dy * dy) > 140.0f, "a spot on the track, a bike length and a half away (%.0f)", sqrtf(dx * dx + dy * dy));

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
	FlatGround();
}

static float g_expectRoll;   /* the INI's MaxRoll for this run */

/* Where the bone sees the seat (mesh point (0, 0, 74)): A P + t, read the game's way round. */
static void LoadRotation(const float *rows, float m[9], bool transposed)
{
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++)
			m[i * 3 + j] = transposed ? rows[j * 4 + i] : rows[i * 4 + j];
}

/* Where a point given to a bone's entry (bind rows at +0x10, position +0x40) lands in the world. */
static void WorldOfBone(const uint8_t *node, const uint8_t *entry, const float v[3], float out[3])
{
	float A[9], N[9], y[3], Ny[3];
	LoadRotation((const float *)(entry + 0x10), A, g_skinTransposed);
	Apply3(A, v, y);
	for (int i = 0; i < 3; i++)
		y[i] += ((const float *)(entry + 0x40))[i];
	LoadRotation((const float *)(node + 0x70), N, g_rootTransposed);
	Apply3(N, y, Ny);
	float s = *(const float *)(node + 0xAC);
	for (int i = 0; i < 3; i++)
		out[i] = s * Ny[i] + ((const float *)(node + 0xA0))[i];
}

/* Where a point of a plain shape (its local transform: rows, position +0x30, scale +0x3C) lands. */
static void WorldOfLocal(const uint8_t *parent, const uint8_t *local, const float q[3], float out[3])
{
	float L[9], N[9], y[3], Ny[3];
	LoadRotation((const float *)local, L, g_rootTransposed);
	Apply3(L, q, y);
	float sl = ((const float *)local)[15];
	for (int i = 0; i < 3; i++)
		y[i] = sl * y[i] + ((const float *)local)[12 + i];
	LoadRotation((const float *)(parent + 0x70), N, g_rootTransposed);
	Apply3(N, y, Ny);
	float s = *(const float *)(parent + 0xAC);
	for (int i = 0; i < 3; i++)
		out[i] = s * Ny[i] + ((const float *)(parent + 0xA0))[i];
}

/* The tilt the plugin put on the bike, in world: the rotation Rw about Pw, from the bike's
 * applied rotation (its own space), its bind and the COM's world transform (the pivot 74 up
 * the bike; PivotForward is 0 in these runs). */
static void ExpectedTilt(float Rw[9], float Pw[3])
{
	float R[9], A[9], At[9], T[9], ARA[9], N[9], Nt[9], AP[3], Pb[3], NP[3];
	static const float P[3] = { 0, 0, 74 };
	AppliedRotation(R);
	LoadRotation((const float *)(g_bonesOriginal + 0x10), A, g_skinTransposed);
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++)
			At[i * 3 + j] = A[j * 3 + i];
	Apply3(A, P, AP);
	for (int i = 0; i < 3; i++)
		Pb[i] = AP[i] + ((const float *)(g_bonesOriginal + 0x40))[i];
	LoadRotation((const float *)(g_comNode + 0x70), N, g_rootTransposed);
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++)
			Nt[i * 3 + j] = N[j * 3 + i];
	Apply3(N, Pb, NP);
	for (int i = 0; i < 3; i++)
		Pw[i] = *(const float *)(g_comNode + 0xAC) * NP[i] + ((const float *)(g_comNode + 0xA0))[i];
	MulM3(A, R, T);
	MulM3(T, At, ARA);
	MulM3(N, ARA, T);
	MulM3(T, Nt, Rw);
}

/* How far `after` is from where the tilt about Pw takes `before`. */
static float TiltedOff(const float before[3], const float after[3], const float Rw[9], const float Pw[3])
{
	float d[3], e[3];
	for (int i = 0; i < 3; i++)
		d[i] = before[i] - Pw[i];
	Apply3(Rw, d, e);
	float dx = after[0] - e[0] - Pw[0], dy = after[1] - e[1] - Pw[1], dz = after[2] - e[2] - Pw[2];
	return sqrtf(dx * dx + dy * dy + dz * dz);
}

static void SeatInBone(const uint8_t *bone, float out[3])
{
	const float *o = (const float *)(bone + 0x10), *t = (const float *)(bone + 0x40);
	for (int i = 0; i < 3; i++)
		out[i] = t[i] + 74.0f * (g_skinTransposed ? o[2 * 4 + i] : o[i * 4 + 2]);
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
	SetGroundTowards(back, 20.0f);   /* and the ground the rays see rises ahead */
	SetTilt(30.0f);
	RunFrames(400);
	AppliedRotation(R);
	float early = acosf(R[8] > 1.0f ? 1.0f : R[8]) * DEG;
	CHECK(g_picks == 0 || (early > 15.0f && early < 21.0f), "standing still, the pitch from the rays under the wheels within 0.4 s (%.1f deg; rays %d)", early, g_picks);
	RunFrames(1100);
	CHECK(*BoneDataRefs() == 3, "the skin is held (references %d)", *BoneDataRefs());
	AppliedRotation(R);
	CHECK(fabsf(R[2]) < 0.01f && fabsf(R[5] + 0.34202f) < 0.01f && fabsf(R[8] - 0.93969f) < 0.01f,
	      "the mesh's up turned to the ground: (%.3f, %.3f, %.3f), expected (0, -0.342, 0.940)", R[2], R[5], R[8]);
	CHECK(R[7] > 0.3f, "nose up (forward goes to z %.3f)", R[7]);
	CHECK(Orthonormal(R), "still a rotation");
	float seatBefore[3], seatNow[3];
	SeatInBone(g_bonesOriginal, seatBefore);
	SeatInBone(g_bones, seatNow);
	CHECK(fabsf(seatNow[0] - seatBefore[0]) < 0.01f && fabsf(seatNow[1] - seatBefore[1]) < 0.01f && fabsf(seatNow[2] - seatBefore[2]) < 0.01f,
	      "turned about the seat: it stays where the rider sits (%.2f, %.2f, %.2f)", seatNow[0], seatNow[1], seatNow[2]);
	CHECK(memcmp(g_bones + 0x40, g_bonesOriginal + 0x40, 12) != 0 && *(float *)(g_bones + 0x4C) == 1.0f, "translation moved, scale untouched");
	CHECK(*(float *)(g_bones + 0x0C) > 115.0f, "culling sphere grown (radius %.1f)", *(float *)(g_bones + 0x0C));

	printf("tilt: the rider pitches with the bike (Rider=1):\n");
	uint8_t *bodyDataNow = *(uint8_t **)(g_bodySkin + 0x40);
	CHECK(bodyDataNow && bodyDataNow != g_bodyData && *(void **)bodyDataNow == *(void **)g_bodyData && *(uint32_t *)(bodyDataNow + 0x20) == 10,
	      "the body's skin instance points at the plugin's own copy of its bone data (the game's vtable, 10 bones)");
	CHECK(bodyDataNow && *(uint32_t *)(bodyDataNow + 0x08) == 0x100001u, "the copy's reference count: the base and the instance's one (%#x)", bodyDataNow ? *(uint32_t *)(bodyDataNow + 0x08) : 0);
	CHECK(memcmp(g_bodyBones, g_bodyBonesOriginal, sizeof(g_bodyBonesOriginal)) == 0 && *(int32_t *)(g_bodyData + 0x08) == 2,
	      "the game's own bone data, shared with every NPC in that mesh, untouched (references %d)", *(int32_t *)(g_bodyData + 0x08));
	CHECK(*(int32_t *)(g_bodySkin + 0x08) == 2 && *(int32_t *)(g_bodyShape + 0x08) == 2 && *(int32_t *)(g_pipboyShape + 0x08) == 2,
	      "the instance and the shapes held (references %d, %d, %d)", *(int32_t *)(g_bodySkin + 0x08), *(int32_t *)(g_bodyShape + 0x08), *(int32_t *)(g_pipboyShape + 0x08));
	float Rw[9], Pw[3], worst = 0.0f, farthest = 0.0f;
	ExpectedTilt(Rw, Pw);
	const uint8_t *copy = bodyDataNow && *(const uint8_t **)(bodyDataNow + 0x10) ? *(const uint8_t **)(bodyDataNow + 0x10) : g_bodyBones;
	static const float probes[2][3] = { { 0, 0, 0 }, { 10, 20, 30 } };
	for (int b = 0; b < 3; b++)
		for (int k = 0; k < 2; k++) {
			float before[3], after[3];
			WorldOfBone(g_bodyNodes[b], g_bodyBonesOriginal + b * 0x50, probes[k], before);
			WorldOfBone(g_bodyNodes[b], copy + b * 0x50, probes[k], after);
			float off = TiltedOff(before, after, Rw, Pw);
			float moved = sqrtf((after[0] - before[0]) * (after[0] - before[0]) + (after[1] - before[1]) * (after[1] - before[1]) + (after[2] - before[2]) * (after[2] - before[2]));
			worst = off > worst ? off : worst;
			farthest = moved > farthest ? moved : farthest;
		}
	CHECK(worst < 0.05f && farthest > 5.0f, "the body's bones carry the mesh with the bike: points land within %.3f of the bike's tilt about its pivot (the farthest moved %.1f)", worst, farthest);
	CHECK(*(const float *)(copy + 0x50 + 0x0C) > *(const float *)(g_bodyBonesOriginal + 0x50 + 0x0C) + 1.0f,
	      "the spine's culling sphere grown (%.1f from %.1f)", *(const float *)(copy + 0x50 + 0x0C), *(const float *)(g_bodyBonesOriginal + 0x50 + 0x0C));
	CHECK(*(const float *)(copy + 2 * 0x50 + 0x0C) == 0.0f, "a bone with no vertices (sphere radius 0, test 24's suit) held with the rest, its sphere left empty");
	CHECK(memcmp(copy + 3 * 0x50, g_bodyBonesOriginal + 3 * 0x50, 0x50) == 0,
	      "a bone whose node is scaled to 0 (hidden; test 27's backpack) held with the rest and left as it is (the log says why)");
	{
		float before[3], after[3];
		WorldOfBone(g_bodyNodes[4], g_bodyBonesOriginal + 4 * 0x50, probes[1], before);
		WorldOfBone(g_bodyNodes[4], copy + 4 * 0x50, probes[1], after);
		float off = TiltedOff(before, after, Rw, Pw);
		CHECK(off < 0.05f && memcmp(copy + 4 * 0x50, g_bodyBonesOriginal + 4 * 0x50, 0x50) != 0,
		      "a cloth bone whose world matrix is sheared (not orthonormal; test 28's purse) carried with the rest, a true inverse (%.3f off)", off);
		WorldOfBone(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, probes[1], before);
		WorldOfBone(g_bodyNodes[5], copy + 5 * 0x50, probes[1], after);
		off = TiltedOff(before, after, Rw, Pw);
		CHECK(off < 0.05f, "the hand, the bars straight: carried like the rest (%.3f off)", off);
	}

	printf("tilt: the bars turned: the hand turns with them (test 29):\n");
	float *headNow = (float *)(g_player + 0xC8), headingBefore = *headNow;
	g_turnOnSpot = -1.0472f;   /* turning left at 60 deg/s: the bars go over */
	g_onFrame = TurnOnTheSpot;
	RunFrames(1500);
	float barNow = BarAngle();
	if (!g_haveParts)
		printf("  (no parts file in this run: nothing turns, the hand is carried like the rest)\n");
	else
		CHECK(fabsf(barNow) > 8.0f && fabsf(barNow) < 11.0f, "the bars over %.1f deg (10)", barNow);
	if (g_haveParts) {
		/* The hand's expected map: the bars' turn about the steering axis (world), then the tilt. */
		float A[9], N[9], Aa[3], axisW[3], Ap[3], Bp[3], NBp[3], qW[3], Q[9], Qq[3], q[3], R2[9], t2[3], before[3], after[3], e[3], d[3];
		static const float steerAxis[3] = { 0, -0.4f, 0.9165f }, steerPoint[3] = { 0, 87.6f, 51.4f };
		float len = sqrtf(steerAxis[1] * steerAxis[1] + steerAxis[2] * steerAxis[2]);
		float axisB[3] = { 0, steerAxis[1] / len, steerAxis[2] / len };
		LoadRotation((const float *)(g_bonesOriginal + 0x10), A, g_skinTransposed);
		LoadRotation((const float *)(g_comNode + 0x70), N, g_rootTransposed);
		Apply3(A, axisB, Aa);
		Apply3(N, Aa, axisW);
		Apply3(A, steerPoint, Ap);
		for (int i = 0; i < 3; i++)
			Bp[i] = Ap[i] + ((const float *)(g_bonesOriginal + 0x40))[i];
		Apply3(N, Bp, NBp);
		for (int i = 0; i < 3; i++)
			qW[i] = NBp[i] + ((const float *)(g_comNode + 0xA0))[i];
		/* Rodrigues about axisW by the bar angle. */
		float c = cosf(barNow / DEG), sn = sinf(barNow / DEG), k = 1.0f - c, *u = axisW;
		Q[0] = c + u[0] * u[0] * k; Q[1] = u[0] * u[1] * k - u[2] * sn; Q[2] = u[0] * u[2] * k + u[1] * sn;
		Q[3] = u[1] * u[0] * k + u[2] * sn; Q[4] = c + u[1] * u[1] * k; Q[5] = u[1] * u[2] * k - u[0] * sn;
		Q[6] = u[2] * u[0] * k - u[1] * sn; Q[7] = u[2] * u[1] * k + u[0] * sn; Q[8] = c + u[2] * u[2] * k;
		Apply3(Q, qW, Qq);
		for (int i = 0; i < 3; i++)
			q[i] = qW[i] - Qq[i];
		ExpectedTilt(Rw, Pw);
		MulM3(Rw, Q, R2);
		Apply3(Rw, q, t2);
		for (int i = 0; i < 3; i++)
			t2[i] += Pw[i] - (Rw[i * 3] * Pw[0] + Rw[i * 3 + 1] * Pw[1] + Rw[i * 3 + 2] * Pw[2]);
		const uint8_t *copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
		WorldOfBone(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, probes[1], before);
		WorldOfBone(g_bodyNodes[5], copyNow + 5 * 0x50, probes[1], after);
		Apply3(R2, before, e);
		for (int i = 0; i < 3; i++)
			d[i] = after[i] - e[i] - t2[i];
		float off = sqrtf(d[0] * d[0] + d[1] * d[1] + d[2] * d[2]);
		float tiltOnly = TiltedOff(before, after, Rw, Pw);
		CHECK(off < 0.1f && tiltOnly > 2.0f, "the hand's bones carry it round the steering axis by the bar angle, then the tilt (%.3f off; %.1f from the tilt alone)", off, tiltOnly);
		{
			/* The arm's two-bone solve (test 30): the shoulder stays, the chain stays joined at
			 * the elbow and the wrist, the bones keep their lengths, and the elbow moved. */
			float S[3], E[3], Wr[3], mS[3], mE1[3], mE2[3], mW2[3], mW3[3];
			memcpy(S, g_bodyNodes[6] + 0xA0, 12);
			memcpy(E, g_bodyNodes[7] + 0xA0, 12);
			memcpy(Wr, g_bodyNodes[5] + 0xA0, 12);
			MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, S, mS);
			MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, E, mE1);
			MapBone(g_bodyNodes[7], g_bodyBonesOriginal + 7 * 0x50, copyNow + 7 * 0x50, E, mE2);
			MapBone(g_bodyNodes[7], g_bodyBonesOriginal + 7 * 0x50, copyNow + 7 * 0x50, Wr, mW2);
			MapBone(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, Wr, mW3);
			CHECK(TiltedOff(S, mS, Rw, Pw) < 0.05f, "the arm's solve: the shoulder stays (%.3f off)", TiltedOff(S, mS, Rw, Pw));
			CHECK(Dist3(mE1, mE2) < 0.1f, "the upper arm and the forearm meet at the elbow (%.3f apart)", Dist3(mE1, mE2));
			CHECK(Dist3(mW2, mW3) < 0.1f, "the forearm and the hand meet at the wrist, on the turned grip (%.3f apart)", Dist3(mW2, mW3));
			CHECK(fabsf(Dist3(mE1, mS) - Dist3(E, S)) < 0.05f && fabsf(Dist3(mW2, mE2) - Dist3(Wr, E)) < 0.05f,
			      "the bones keep their lengths (%.1f and %.1f)", Dist3(mE1, mS), Dist3(mW2, mE2));
			CHECK(TiltedOff(E, mE2, Rw, Pw) > 0.3f, "the elbow moved (%.2f): the arm bent to reach", TiltedOff(E, mE2, Rw, Pw));
		}
		WorldOfBone(g_bodyNodes[0], g_bodyBonesOriginal, probes[1], before);
		WorldOfBone(g_bodyNodes[0], copyNow, probes[1], after);
		CHECK(TiltedOff(before, after, Rw, Pw) < 0.05f, "the pelvis only tilted");
	}
	g_turnOnSpot = 1.0472f;   /* and back the other way, to where it faced */
	RunFrames(1500);
	g_onFrame = NULL;
	*headNow = headingBefore;
	RunFrames(1000);   /* the bars straight again */

	printf("lamp: the headlamp's add-on node at the lens while CMB_HeadlampLive is 1, hidden while 0:\n");
	{
		/* Expected: the lens (0.3, 76.3, 81.9) in the bike's space, through the bind and COM,
		 * tilted as the bike is; the beam (bike +Y, dipped 0 here) along the node's +X. */
		static const float lens[3] = { 0.3f, 76.3f, 81.9f }, lensAhead[3] = { 0.3f, 77.3f, 81.9f };
		float Rw[9], Pw[3], w[3], wa[3], e[3], ea[3], H[9], Lr[9], HL[9], lp[3], actual[3], beam[3], axisX[3];
		SetHeadlamp(1.0f);
		RunFrames(400);
		ExpectedTilt(Rw, Pw);
		WorldOfBone(g_comNode, g_bonesOriginal, lens, w);
		WorldOfBone(g_comNode, g_bonesOriginal, lensAhead, wa);
		for (int i = 0; i < 3; i++) {
			e[i] = Pw[i] + Rw[i * 3] * (w[0] - Pw[0]) + Rw[i * 3 + 1] * (w[1] - Pw[1]) + Rw[i * 3 + 2] * (w[2] - Pw[2]);
			ea[i] = Pw[i] + Rw[i * 3] * (wa[0] - Pw[0]) + Rw[i * 3 + 1] * (wa[1] - Pw[1]) + Rw[i * 3 + 2] * (wa[2] - Pw[2]);
			beam[i] = ea[i] - e[i];
		}
		LoadRotation((const float *)(g_bikeNode + 0x70), H, g_rootTransposed);
		LoadRotation((const float *)(g_lampNode + 0x30), Lr, g_rootTransposed);
		memcpy(lp, g_lampNode + 0x60, 12);
		Apply3(H, lp, actual);
		for (int i = 0; i < 3; i++)
			actual[i] += ((const float *)(g_bikeNode + 0xA0))[i];
		MulM3(H, Lr, HL);
		axisX[0] = HL[0]; axisX[1] = HL[3]; axisX[2] = HL[6];
		float off = sqrtf((actual[0] - e[0]) * (actual[0] - e[0]) + (actual[1] - e[1]) * (actual[1] - e[1]) + (actual[2] - e[2]) * (actual[2] - e[2]));
		float boff = sqrtf((axisX[0] - beam[0]) * (axisX[0] - beam[0]) + (axisX[1] - beam[1]) * (axisX[1] - beam[1]) + (axisX[2] - beam[2]) * (axisX[2] - beam[2]));
		uint64_t flags = *(uint64_t *)(g_lampNode + 0x108);
		if (g_haveParts) {
			CHECK(off < 0.1f && !(flags & 1), "lit: the node at the lens, tilted with the bike (%.3f off), not hidden (flags %#llx)", off, (unsigned long long)flags);
			CHECK(boff < 0.02f && ((const float *)(g_lampNode + 0x30))[15] == 1.0f, "its +X axis down the beam (%.3f off), scale 1", boff);
		} else {
			CHECK(memcmp(g_lampNode + 0x30, g_lampLocalOriginal, 0x40) == 0 && !(flags & 1),
			      "lit, no parts file (no lens to put it at): left where the nif put it, not hidden (flags %#llx)", (unsigned long long)flags);
		}
		CHECK(*(int32_t *)(g_lampNode + 0x08) == 2, "held (references %d)", *(int32_t *)(g_lampNode + 0x08));
		SetHeadlamp(0.0f);
		RunFrames(300);
		flags = *(uint64_t *)(g_lampNode + 0x108);
		CHECK((flags & 1) && ((const float *)(g_lampNode + 0x60))[2] < -10000.0f, "out: hidden (flags %#llx) and sunk (z %.0f)", (unsigned long long)flags, ((const float *)(g_lampNode + 0x60))[2]);
		SetHeadlamp(1.0f);
		RunFrames(300);
		flags = *(uint64_t *)(g_lampNode + 0x108);
		memcpy(lp, g_lampNode + 0x60, 12);
		Apply3(H, lp, actual);
		for (int i = 0; i < 3; i++)
			actual[i] += ((const float *)(g_bikeNode + 0xA0))[i];
		off = sqrtf((actual[0] - e[0]) * (actual[0] - e[0]) + (actual[1] - e[1]) * (actual[1] - e[1]) + (actual[2] - e[2]) * (actual[2] - e[2]));
		if (g_haveParts)
			CHECK(!(flags & 1) && off < 0.1f, "lit again: back at the lens (%.3f off), not hidden", off);
		else
			CHECK(!(flags & 1) && memcmp(g_lampNode + 0x30, g_lampLocalOriginal, 0x40) == 0, "lit again: back where the nif put it, not hidden");

		printf("lamp: the light reference the script placed (CMB_HeadlampRefHi/Lo): moved to the lens when no add-on node does the lighting:\n");
		SetLampRef(LAMP_REF_FORMID);
		RunFrames(300);
		CHECK(((const float *)(g_lampRefRoot + 0xA0))[2] < -10000.0f, "with the node lit: the reference parked far below (z %.0f)", ((const float *)(g_lampRefRoot + 0xA0))[2]);
		RemoveChild(g_bikeNode, g_lampNode);   /* the node gone from the 3D: let go of at the next sync */
		RunFrames(400);
		CHECK(*(int32_t *)(g_lampNode + 0x08) == 1 && memcmp(g_lampNode + 0x30, g_lampLocalOriginal, 0x40) == 0, "the node gone: let go of, its transform back");
		if (g_haveParts) {
			float rw[3], rW[9], rl[3], cw[3], cW[9], cl[3], ex[3], axisX2[3];
			memcpy(rw, g_lampRefRoot + 0xA0, 12);
			memcpy(rl, g_lampRefRoot + 0x60, 12);
			LoadRotation((const float *)(g_lampRefRoot + 0x70), rW, g_rootTransposed);
			float roff = sqrtf((rw[0] - e[0]) * (rw[0] - e[0]) + (rw[1] - e[1]) * (rw[1] - e[1]) + (rw[2] - e[2]) * (rw[2] - e[2]));
			float loff = sqrtf((rl[0] - e[0]) * (rl[0] - e[0]) + (rl[1] - e[1]) * (rl[1] - e[1]) + (rl[2] - e[2]) * (rl[2] - e[2]));
			axisX2[0] = rW[0]; axisX2[1] = rW[3]; axisX2[2] = rW[6];
			float boff2 = sqrtf((axisX2[0] - beam[0]) * (axisX2[0] - beam[0]) + (axisX2[1] - beam[1]) * (axisX2[1] - beam[1]) + (axisX2[2] - beam[2]) * (axisX2[2] - beam[2]));
			CHECK(roff < 0.1f && loff < 0.1f, "the reference's 3D at the lens, world and local (%.3f, %.3f off)", roff, loff);
			CHECK(boff2 < 0.02f, "its +X axis down the beam (%.3f off)", boff2);
			memcpy(cw, g_lampRefLight + 0xA0, 12);
			memcpy(cl, g_lampRefLight + 0x60, 12);
			LoadRotation((const float *)(g_lampRefLight + 0x70), cW, g_rootTransposed);
			Apply3(rW, cl, ex);
			for (int i = 0; i < 3; i++)
				ex[i] += rw[i];
			float coff = sqrtf((cw[0] - ex[0]) * (cw[0] - ex[0]) + (cw[1] - ex[1]) * (cw[1] - ex[1]) + (cw[2] - ex[2]) * (cw[2] - ex[2]));
			float rdiff = 0.0f;
			for (int i = 0; i < 9; i++)
				rdiff += fabsf(cW[i] - rW[i]);
			CHECK(coff < 0.05f && rdiff < 0.01f, "the light's node under it carried along: its world transform the root's and its own (%.3f off)", coff);
			const float *rp = (const float *)(g_lampRef + 0xD0);
			CHECK(fabsf(rp[0] - e[0]) < 0.1f && fabsf(rp[1] - e[1]) < 0.1f && fabsf(rp[2] - e[2]) < 0.1f, "and the reference's own position at the lens");
			*(uint8_t **)(g_lampRefLoaded + 0x08) = NULL;   /* the script disabled it: no 3D */
			RunFrames(200);
			CHECK(true, "no 3D (disabled): nothing written, nothing wrong");
			*(uint8_t **)(g_lampRefLoaded + 0x08) = g_lampRefRoot;
		} else {
			CHECK(((const float *)(g_lampRefRoot + 0xA0))[2] < -10000.0f, "no parts file (no lens): the reference stays parked (z %.0f)", ((const float *)(g_lampRefRoot + 0xA0))[2]);
		}
		SetLampRef(0);
		AddChild(g_bikeNode, g_lampNode);   /* the node back for the rest of the ride */
		RunFrames(300);
	}

	printf("tilt: a blood decal cloned from the body (its skin points at our copy):\n");
	*(uint8_t **)(g_decalSkin + 0x40) = *(uint8_t **)(g_bodySkin + 0x40);   /* the game cloned the body's instance: our copy and all */
	*(uint32_t *)(*(uint8_t **)(g_bodySkin + 0x40) + 0x08) += 1;               /* with a reference, as a smart pointer takes one */
	AddChild(g_npcRoot, g_decalShape);
	RunFrames(400);
	{
		uint8_t *bodyCopy = *(uint8_t **)(g_bodySkin + 0x40), *decalCopy = *(uint8_t **)(g_decalSkin + 0x40);
		CHECK(decalCopy && decalCopy != bodyCopy && decalCopy != g_bodyData && *(int32_t *)(g_decalSkin + 0x08) == 2,
		      "the decal held with a copy of its own (references %d)", *(int32_t *)(g_decalSkin + 0x08));
		CHECK(decalCopy && memcmp(*(uint8_t **)(decalCopy + 0x10), *(uint8_t **)(bodyCopy + 0x10), 10 * 0x50) == 0,
		      "its bones carry it exactly as the body's (from the body's own data, not the tilted copy: no double tilt)");
	}
	{
		static const float q[3] = { 5, 0, 2 };
		float before[3], after[3];
		ExpectedTilt(Rw, Pw);   /* the tilt now (the turn on the spot changed it meanwhile) */
		WorldOfLocal(g_pipboyBone, g_pipboyLocalOriginal, q, before);
		WorldOfLocal(g_pipboyBone, g_pipboyShape + 0x30, q, after);
		float off = TiltedOff(before, after, Rw, Pw);
		CHECK(off < 0.05f && ((float *)(g_pipboyShape + 0x30))[15] == 1.0f && memcmp(g_pipboyShape + 0x30, g_pipboyLocalOriginal, 0x30) != 0,
		      "a plain shape under a bone (the Pip-Boy's, its bone scaled 0.9) carried through its own transform (%.3f off, scale untouched)", off);
	}
	RunFrames(3000);   /* the published normal is an average over the last 0.6 s or so */
	CHECK(fabsf(Ground(2) - 0.93969f) < 0.01f && fabsf(Ground(0) + 0.34202f * forward[0]) < 0.01f,
	      "CMB_GroundNormal, averaged, follows the slope (%.3f, %.3f, %.3f)", Ground(0), Ground(1), Ground(2));

	printf("tilt: a dip between the wheels (the ground 10 above the capsule's contact): the bike lifted onto it:\n");
	SetNormal(0.0f, 0.0f, 1.0f);
	g_slopeK = 0.0f;
	g_groundZ = PlayerPos()[2] + 10.0f;
	RunFrames(800);
	SeatInBone(g_bonesOriginal, seatBefore);
	SeatInBone(g_bones, seatNow);
	float lifted = sqrtf((seatNow[0] - seatBefore[0]) * (seatNow[0] - seatBefore[0]) + (seatNow[1] - seatBefore[1]) * (seatNow[1] - seatBefore[1]) + (seatNow[2] - seatBefore[2]) * (seatNow[2] - seatBefore[2]));
	CHECK(g_picks == 0 || (lifted > 9.0f && lifted < 11.0f), "the bike lifted %.1f (10), level", lifted);
	g_groundZ = PlayerPos()[2] - 10.0f;   /* a crest: the ground below the contact */
	RunFrames(800);
	SeatInBone(g_bones, seatNow);
	lifted = sqrtf((seatNow[0] - seatBefore[0]) * (seatNow[0] - seatBefore[0]) + (seatNow[1] - seatBefore[1]) * (seatNow[1] - seatBefore[1]) + (seatNow[2] - seatBefore[2]) * (seatNow[2] - seatBefore[2]));
	CHECK(lifted < 0.5f, "on a crest (the ground 10 below): not lowered (%.1f)", lifted);
	g_groundZ = PlayerPos()[2];

	printf("tilt: a one-frame jump in the ground (a curb's edge):\n");
	SetNormal(0.0f, 0.0f, 1.0f);
	RunFrames(1500);
	SetNormalTowards(back, 40.0f);
	((void (*)(Task *))g_task->vtbl[1])(g_task);
	((void (*)(Task *))g_task->vtbl[1])(g_task);
	SetNormal(0.0f, 0.0f, 1.0f);
	RunFrames(150);
	AppliedRotation(R);
	CHECK(acosf(R[8] > 1.0f ? 1.0f : R[8]) * DEG < 1.0f, "ignored (tilt %.2f deg)", acosf(R[8] > 1.0f ? 1.0f : R[8]) * DEG);

	printf("tilt: a 45 deg side slope (MaxRoll %g):\n", g_expectRoll);
	SetNormalTowards(right, 45.0f);   /* ground falls away to the right */
	SetGroundTowards(right, 45.0f);
	RunFrames(1500);
	AppliedRotation(R);
	float tilted = acosf(R[8] > 1.0f ? 1.0f : R[8]) * DEG;
	CHECK(fabsf(tilted - g_expectRoll) < 0.5f, "rolled %.2f deg, the most MaxRoll allows", tilted);
	CHECK(g_expectRoll == 0.0f || (R[6] < -0.1f && fabsf(R[7]) < 0.01f), "right side down (right goes to z %.3f), no pitch", R[6]);
	if (g_expectRoll > 0.0f) {
		/* The head kept level (test 31's wish): its bone turned back by the roll about its own
		 * joint, the face bone under it with it. */
		float Rw[9], Pw[3], H[3], J[3], up[3], mH[3], mUp[3], mJh[3], mJj[3];
		const uint8_t *copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
		ExpectedTilt(Rw, Pw);
		memcpy(H, g_bodyNodes[8] + 0xA0, 12);
		memcpy(J, g_bodyNodes[9] + 0xA0, 12);
		for (int i = 0; i < 3; i++)
			up[i] = H[i] + (i == 2 ? 10.0f : 0.0f);
		MapBone(g_bodyNodes[8], g_bodyBonesOriginal + 8 * 0x50, copyNow + 8 * 0x50, H, mH);
		MapBone(g_bodyNodes[8], g_bodyBonesOriginal + 8 * 0x50, copyNow + 8 * 0x50, up, mUp);
		MapBone(g_bodyNodes[8], g_bodyBonesOriginal + 8 * 0x50, copyNow + 8 * 0x50, J, mJh);
		MapBone(g_bodyNodes[9], g_bodyBonesOriginal + 9 * 0x50, copyNow + 9 * 0x50, J, mJj);
		CHECK(TiltedOff(H, mH, Rw, Pw) < 0.05f, "the head's joint goes with the bike (%.3f off)", TiltedOff(H, mH, Rw, Pw));
		CHECK(fabsf(mUp[0] - mH[0]) < 0.05f && fabsf(mUp[1] - mH[1]) < 0.05f && fabsf(mUp[2] - mH[2] - 10.0f) < 0.05f,
		      "and the head stays upright: a point 10 above the joint is still straight above it (%.3f, %.3f, %.3f)", mUp[0] - mH[0], mUp[1] - mH[1], mUp[2] - mH[2]);
		CHECK(Dist3(mJh, mJj) < 0.05f, "the face goes with the head (%.3f apart)", Dist3(mJh, mJj));
	}

	RunFrames(2500);
	float groundX = Ground(0);
	printf("tilt: in the air:\n");
	SetState(2);
	SetNormalTowards(forward, 10.0f);   /* stale normal: must not be used */
	RunFrames(1500);
	AppliedRotation(R);
	CHECK(fabsf(acosf(R[8] > 1.0f ? 1.0f : R[8]) * DEG - tilted) < 0.5f, "holds what it had on the ground (%.2f deg)", acosf(R[8] > 1.0f ? 1.0f : R[8]) * DEG);
	CHECK(Ground(2) == 0.0f && fabsf(Ground(0) - groundX) < 0.01f,
	      "in the air CMB_GroundNormalZ is 0, X and Y left alone (%.3f, %.3f, %.3f)", Ground(0), Ground(1), Ground(2));
	SetState(0);
	SetNormal(0.0f, 0.0f, 1.0f);
	g_slopeK = 0.0f;
	g_groundZ = PlayerPos()[2];
	RunFrames(300);

	printf("tilt: getting off:\n");
	SetTilt(0.0f);
	RunFrames(300);
	CHECK(memcmp(g_bones, g_bonesOriginal, 0x50) == 0, "the skin back exactly as it was");
	CHECK(*BoneDataRefs() == 2 && g_deleted == 0, "let go of (references %d)", *BoneDataRefs());
	CHECK(memcmp(g_lampNode + 0x30, g_lampLocalOriginal, 0x40) == 0 && *(uint64_t *)(g_lampNode + 0x108) == 0 && *(int32_t *)(g_lampNode + 0x08) == 1,
	      "the headlamp's node back where the nif put it, its flags as they were, let go of (references %d)", *(int32_t *)(g_lampNode + 0x08));
	CHECK(*(uint8_t **)(g_bodySkin + 0x40) == g_bodyData && *(int32_t *)(g_bodySkin + 0x08) == 1 && *(int32_t *)(g_bodyShape + 0x08) == 1 &&
	      memcmp(g_pipboyShape + 0x30, g_pipboyLocalOriginal, 0x40) == 0 && *(int32_t *)(g_pipboyShape + 0x08) == 1,
	      "the rider's skin pointed back at the game's bone data, the Pip-Boy's transform back, all let go of");
	{
		uint8_t *decalCopy = *(uint8_t **)(g_decalSkin + 0x40);
		CHECK(decalCopy && decalCopy != g_bodyData && *(int32_t *)(g_decalSkin + 0x08) == 1 && memcmp(*(uint8_t **)(decalCopy + 0x10), g_bodyBonesOriginal, 10 * 0x50) == 0,
		      "the decal pointed back where the game left it (the body's old copy), which reads level again");
		CHECK(*(uint32_t *)(decalCopy + 0x08) == 0x100001u, "that copy's references: the base and the decal's own (%#x): reusable once the decal lets go", *(uint32_t *)(decalCopy + 0x08));
	}
	*(uint16_t *)(g_npcRoot + 0x132) -= 1;   /* the decal gone again */
	*(uint8_t **)(g_decalSkin + 0x40) = g_bodyData;

	printf("tilt: the bike taken off mid-ride:\n");
	SetNormalTowards(back, 20.0f);
	SetGroundTowards(back, 20.0f);
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
	CHECK(*(uint8_t **)(g_bodySkin + 0x40) != g_bodyData, "the rider still held meanwhile (level)");
	SetTilt(0.0f);
	RunFrames(300);
	CHECK(*(uint8_t **)(g_bodySkin + 0x40) == g_bodyData && *(int32_t *)(g_bodySkin + 0x08) == 1 && memcmp(g_pipboyShape + 0x30, g_pipboyLocalOriginal, 0x40) == 0,
	      "and let go of at the dismount, though the bike's skins went first (test 24 kept it)");

	printf("tilt: a shape of the rider whose skin data isn't right: nothing of the rider is held:\n");
	float *bodyRows = (float *)(g_bodyBones + 0x10);
	float wasRow0 = bodyRows[0];
	bodyRows[0] = 2.0f;   /* the body's first bone: not a rotation any more */
	memcpy(g_bodyBonesOriginal, g_bodyBones, sizeof(g_bodyBonesOriginal));
	SetNormalTowards(back, 20.0f);
	SetGroundTowards(back, 20.0f);
	SetTilt(30.0f);
	RunFrames(800);
	CHECK(*BoneDataRefs() == 3, "the bike held and tilted (references %d)", *BoneDataRefs());
	CHECK(*(uint8_t **)(g_bodySkin + 0x40) == g_bodyData && *(int32_t *)(g_bodySkin + 0x08) == 1 && *(int32_t *)(g_bodyShape + 0x08) == 1,
	      "the body not held (the log says which bone and why)");
	CHECK(memcmp(g_pipboyShape + 0x30, g_pipboyLocalOriginal, 0x40) == 0 && *(int32_t *)(g_pipboyShape + 0x08) == 1,
	      "and nothing else of the rider either: all or nothing (a part-tilted rider tears)");
	SetTilt(0.0f);
	RunFrames(300);
	bodyRows[0] = wasRow0;
	memcpy(g_bodyBonesOriginal, g_bodyBones, sizeof(g_bodyBonesOriginal));
	SetTilt(30.0f);
	RunFrames(800);
	CHECK(*(uint8_t **)(g_bodySkin + 0x40) != g_bodyData && *(int32_t *)(g_bodySkin + 0x08) == 2, "the data right again: held on the next ride");
	SetTilt(0.0f);
	RunFrames(300);

	printf("tilt: the game gives the body a new skin instance, and points one back at its own bone data (test 28's decal):\n");
	SetTilt(30.0f);
	RunFrames(800);
	uint8_t *oldSkin = g_bodySkin;
	CHECK(*(uint8_t **)(oldSkin + 0x40) != g_bodyData && *(int32_t *)(oldSkin + 0x08) == 2, "held (the instance points at the copy, references %d)", *(int32_t *)(oldSkin + 0x08));
	uint8_t *newSkin = (uint8_t *)NewObject(g_vtSkin, 0x100);   /* the game's new instance for the shape: same bones, its own data */
	*(int32_t *)(newSkin + 0x08) = 1;
	*(uint8_t **)(newSkin + 0x40) = g_bodyData;
	*(uint8_t ***)(newSkin + 0x28) = *(uint8_t ***)(oldSkin + 0x28);
	*(uint32_t *)(newSkin + 0x30) = *(uint32_t *)(oldSkin + 0x30);
	*(uint32_t *)(newSkin + 0x38) = *(uint32_t *)(oldSkin + 0x38);
	*(uint8_t **)(g_bodyShape + 0x140) = newSkin;
	*(uint8_t **)(oldSkin + 0x40) = g_bodyData;   /* the game dropped the old instance: it points at its own data again */
	*(int32_t *)(oldSkin + 0x08) -= 1;
	g_bodySkin = newSkin;
	RunFrames(300);
	CHECK(*(uint8_t **)(newSkin + 0x40) != g_bodyData && *(uint8_t **)(newSkin + 0x40) != NULL && *(int32_t *)(newSkin + 0x08) == 2,
	      "the new instance held within a sync: it points at a copy (references %d)", *(int32_t *)(newSkin + 0x08));
	CHECK(*(int32_t *)(oldSkin + 0x08) == 0 && g_deleted == 1 && *(uint8_t **)(oldSkin + 0x40) == g_bodyData,
	      "the old one let go of and gone (deleted %d), its pointer left at the game's data", g_deleted);
	g_deleted = 0;
	uint8_t *ours = *(uint8_t **)(newSkin + 0x40);
	*(uint8_t **)(newSkin + 0x40) = g_bodyData;   /* the game points the instance back at its own data... */
	*(uint32_t *)(ours + 0x08) -= 1;             /* ...letting go of its reference to ours, as a smart pointer does */
	RunFrames(300);
	CHECK(*(uint8_t **)(newSkin + 0x40) == ours && *(uint32_t *)(ours + 0x08) == 0x100001u,
	      "pointed back at its own data by the game: ours again within a sync, with the reference taken again (%#x)", *(uint32_t *)(ours + 0x08));
	SetTilt(0.0f);
	RunFrames(300);
	CHECK(*(uint8_t **)(newSkin + 0x40) == g_bodyData && *(int32_t *)(newSkin + 0x08) == 1 && *(uint32_t *)(ours + 0x08) == 0x100000u,
	      "getting off: the game's data back, let go of, the copy at its base count (%#x)", *(uint32_t *)(ours + 0x08));

	printf("tilt: the rider blocked, then the bike taken off before the dismount (nothing held at it): the next ride starts afresh (test 27):\n");
	bodyRows[0] = 2.0f;
	memcpy(g_bodyBonesOriginal, g_bodyBones, sizeof(g_bodyBonesOriginal));
	SetTilt(30.0f);
	RunFrames(500);
	CHECK(*(int32_t *)(g_bodySkin + 0x08) == 1 && *BoneDataRefs() == 3, "blocked (the body not held), the bike held");
	*(uint16_t *)(g_root + 0x132) -= 1;   /* the bike's node leaves the 3D */
	uint8_t **slotPart2 = (uint8_t **)(g_biped + 0x10 + 27 * 0x58 + 0x30);
	*slotPart2 = NULL;
	*BoneDataRefs() -= 2;
	RunFrames(300);
	CHECK(g_deleted == 1, "the bike's skins gone first");
	SetTilt(0.0f);
	RunFrames(300);
	*(uint16_t *)(g_root + 0x132) += 1;
	*slotPart2 = g_bikeNode;
	*BoneDataRefs() = 2;
	g_deleted = 0;
	bodyRows[0] = wasRow0;
	memcpy(g_bodyBonesOriginal, g_bodyBones, sizeof(g_bodyBonesOriginal));
	SetTilt(30.0f);
	RunFrames(800);
	CHECK(*(uint8_t **)(g_bodySkin + 0x40) != g_bodyData && *(int32_t *)(g_bodySkin + 0x08) == 2 && *BoneDataRefs() == 3,
	      "the next ride holds the rider again (test 27 stayed level, the block carried over)");
	SetTilt(0.0f);
	RunFrames(300);

	printf("tilt: skin data that isn't what it should be:\n");
	float *rows = (float *)(g_bones + 0x10);
	rows[0] = 2.0f;   /* not a rotation any more */
	memcpy(g_bonesOriginal, g_bones, sizeof(g_bonesOriginal));
	SetNormalTowards(back, 20.0f);
	SetGroundTowards(back, 20.0f);
	SetTilt(30.0f);
	RunFrames(500);
	CHECK(memcmp(g_bones, g_bonesOriginal, 0x50) == 0 && *BoneDataRefs() == 2, "not touched, not held");
	SetTilt(0.0f);
	RunFrames(200);
}

/* The rider's A/B switches (test 25: 30 fps lost on the bike): RiderSwap=0 writes the game's
 * own bone data in place, RiderPlain=0 leaves the plain shapes alone (mode 7); RiderWrite=0
 * holds (and swaps) but never writes, RiderSkinned=0 leaves the skinned shapes alone (mode 8). */
static void RiderSwitchTests(int mode)
{
	const float back[3] = { -sinf(HEADING), -cosf(HEADING), 0.0f };
	printf("rider switches (%s):\n", mode == 7 ? "RiderSwap=0 RiderPlain=0" : "RiderWrite=0 RiderSkinned=0");
	SetNormalTowards(back, 20.0f);
	SetGroundTowards(back, 20.0f);
	SetTilt(30.0f);
	RunFrames(1500);
	CHECK(*BoneDataRefs() == 3, "the bike held and tilted (references %d)", *BoneDataRefs());
	if (mode == 7) {
		CHECK(*(uint8_t **)(g_bodySkin + 0x40) == g_bodyData && *(int32_t *)(g_bodySkin + 0x08) == 2,
		      "the body held without a swap: its skin instance still points at the game's bone data (references %d)", *(int32_t *)(g_bodySkin + 0x08));
		float Rw[9], Pw[3], worst = 0.0f;
		ExpectedTilt(Rw, Pw);
		static const float v[3] = { 10, 20, 30 };
		for (int b = 0; b < 3; b++) {
			float before[3], after[3];
			WorldOfBone(g_bodyNodes[b], g_bodyBonesOriginal + b * 0x50, v, before);
			WorldOfBone(g_bodyNodes[b], g_bodyBones + b * 0x50, v, after);
			float off = TiltedOff(before, after, Rw, Pw);
			worst = off > worst ? off : worst;
		}
		CHECK(memcmp(g_bodyBones, g_bodyBonesOriginal, sizeof(g_bodyBonesOriginal)) != 0 && worst < 0.05f,
		      "the game's own bone data written in place with the tilt (points within %.3f)", worst);
		CHECK(memcmp(g_pipboyShape + 0x30, g_pipboyLocalOriginal, 0x40) == 0 && *(int32_t *)(g_pipboyShape + 0x08) == 1,
		      "the plain shape left alone, not held");
	} else {
		CHECK(*(uint8_t **)(g_bodySkin + 0x40) == g_bodyData && *(int32_t *)(g_bodySkin + 0x08) == 1 &&
		      memcmp(g_bodyBones, g_bodyBonesOriginal, sizeof(g_bodyBonesOriginal)) == 0, "the body left alone, not held");
		CHECK(*(int32_t *)(g_pipboyShape + 0x08) == 2 && memcmp(g_pipboyShape + 0x30, g_pipboyLocalOriginal, 0x40) == 0,
		      "the plain shape held (references %d) but never written", *(int32_t *)(g_pipboyShape + 0x08));
	}
	SetTilt(0.0f);
	RunFrames(300);
	CHECK(memcmp(g_bodyBones, g_bodyBonesOriginal, sizeof(g_bodyBonesOriginal)) == 0 && *(int32_t *)(g_bodySkin + 0x08) == 1 &&
	      *(int32_t *)(g_pipboyShape + 0x08) == 1 && memcmp(g_pipboyShape + 0x30, g_pipboyLocalOriginal, 0x40) == 0 && *BoneDataRefs() == 2,
	      "getting off: everything back and let go of");
}

int main(int argc, char **argv)
{
	const char *dllPath = argc > 1 ? argv[1] : "CMB_Slope.dll";
	int mode = argc > 2 ? atoi(argv[2]) : 0;   /* 0 = full test, 1 = probe only, 2 = wrong game version */
	g_haveParts = mode == 0 || mode == 7 || mode == 8;   /* run.sh gives those a [Parts] section */
	g_base = (uintptr_t)GetModuleHandleA(NULL);
	if ((uintptr_t)g_space > g_base + 0x00300000u || (uintptr_t)g_space + sizeof(g_space) < g_base + RVA_INI_SETTINGS + 8) {
		printf("image layout doesn't cover the game addresses (g_space at +0x%llx)\n", (unsigned long long)((uintptr_t)g_space - g_base));
		return 2;
	}
	(void)g_members;
	BuildGame();
	SetLayouts(mode == 4, mode == 4 || mode == 5);   /* 4: transposed matrices, 5: skin and 3D disagree */
	g_expectRoll = mode == 0 ? 10.0f : 0.0f;          /* run.sh gives the full test MaxRoll=10 */

	HMODULE dll = LoadLibraryA(dllPath);
	if (!dll) { printf("can't load %s\n", dllPath); return 2; }
	const uint32_t *version = (const uint32_t *)GetProcAddress(dll, "F4SEPlugin_Version");
	bool (*load)(const F4SEInterface *) = (bool (*)(const F4SEInterface *))GetProcAddress(dll, "F4SEPlugin_Load");
	printf("version data and load function:\n");
	CHECK(version && load, "exports present");
	CHECK(version && version[0] == 1 && strcmp((const char *)(version + 2), "CMB_Slope") == 0, "F4SEPlugin_Version: data version 1, name CMB_Slope");
	const uint32_t *compatible = version + 2 + 128 + 2;
	CHECK(compatible[0] == 0x010B0F00u && compatible[1] == 0, "compatible with 1.11.240 only");

	if (mode == 0)
		WriteAddressLibrary();
	F4SEInterface f4se = { 0x00070090u, mode == 2 ? 0x010B0DD0u : 0x010B0F00u, 0, 0, QueryInterface, GetPluginHandle, 0, 0, 0 };
	bool loaded = load(&f4se);
	if (mode == 2) {
		CHECK(!loaded && !g_task, "wrong game version: refuses to load, no task");
		return g_failures ? 1 : 0;
	}
	CHECK(loaded && g_task && g_listener, "loads, registers a permanent task and a listener");
	if (mode == 6) {
		Send(10, 1);   /* GameDataReady */
		RunFrames(300);
		BackPushModTests();
		printf("%s\n", g_failures ? "FAILED" : "all ok");
		return g_failures ? 1 : 0;
	}
	if (mode == 7 || mode == 8) {
		Send(10, 1);   /* GameDataReady */
		RunFrames(300);
		RiderSwitchTests(mode);
		printf("%s\n", g_failures ? "FAILED" : "all ok");
		return g_failures ? 1 : 0;
	}
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

	printf("a save loaded on the bike: the controller lives on with the riding value in it (test 24):\n");
	SetLive(60.0f);
	RunFrames(300);
	CHECK(Near(*Slope(), 0.5f), "riding at 60 deg");
	Send(3, 1);   /* PostLoadGame: the plugin forgets what it applied; the controller still holds 0.5 */
	RunFrames(400);
	CHECK(Near(*Slope(), 0.5f), "after the load still 60 deg, taken as ours again");
	SetLive(0.0f);
	RunFrames(400);
	CHECK(Near(*Slope(), COS47), "and back to 47 deg at the dismount (got %f; test 24 kept 60 on foot)", *Slope());

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
	ZoomTests();

	printf("%s\n", g_failures ? "FAILED" : "all ok");
	return g_failures ? 1 : 0;
}
