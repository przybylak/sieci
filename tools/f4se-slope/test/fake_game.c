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
static uint8_t *g_parkGlobals[7], *g_trackSlope, *g_turnRadius, *g_turnStand, *g_turnSlow, *g_controls;
static uint8_t *g_thirdState;   /* ThirdPersonState: zoom target +0xE8, current +0xEC */
static uint8_t *g_moveHandler;  /* MovementHandler: its vtable read-only, as in the game */

/* The input and the movement, as the game does them (tests 12-14): the MovementHandler sets
 * PlayerControls' move input from the held keys (style 0: both halves every frame; style 1:
 * adds the change on a press or release; style 2, as the game does: the input cleared to
 * (+0, +0) every frame outside the handler, then each held key sets its own half). The
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
	LARGE_INTEGER frequency, last, now;
	QueryPerformanceFrequency(&frequency);
	QueryPerformanceCounter(&last);
	while ((int32_t)(GetTickCount() - end) < 0) {
		QueryPerformanceCounter(&now);
		if (g_onFrame)
			g_onFrame((float)(now.QuadPart - last.QuadPart) / (float)frequency.QuadPart);
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
	if (speed < 0.0f && !(g_honour & 16))
		speed = 0.0f;
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

static void InputTests(void)
{
	float *head = (float *)(g_player + 0xC8), from, p0[2];
	printf("input hook: a side key from a stop creeps round a small circle:\n");
	g_camYaw = *head;
	g_handlerStyle = 2;
	g_honour = 8;
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
	CHECK(crept > 25.0f && crept < 60.0f, "creeping forward at %.0f a second (about 42: round a 40 circle), not driven off", crept);
	CHECK(MoveInput()[0] == 0.0f && MoveInput()[1] > 0.0f && MoveInput()[1] < 0.1f, "the game gets no side input, a little forward (%.3f)", MoveInput()[1]);
	CHECK(((float *)(g_controls + 0x5C))[1] == MoveInput()[1], "and its movement used that (+5C)");
	Keys(1.0f, 1.0f);
	RunFrames(300);
	CHECK(MoveInput()[0] == 1.0f && MoveInput()[1] == 1.0f, "forward and right: left alone");
	Keys(0.0f, 0.0f);
	RunFrames(600);

	printf("input hook: back gets the game nothing; the movement output is turned round (this game honours that):\n");
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

	printf("input hook: a game that ignores the output's rotation but backs up on a negative speed (after a load, tried again):\n");
	Send(3, 1);   /* PostLoadGame */
	g_honour = 16;
	RunFrames(400);
	g_camYaw = *head;
	from = *head;
	Mark(p0);
	float most = 0.0f;
	Keys(0.0f, -1.0f);
	for (int i = 0; i < 12; i++) {
		RunFrames(100);
		float a = Along(p0, from);
		most = a > most ? a : most;
	}
	Mark(p0);
	RunFrames(1000);
	along = Along(p0, from);
	CHECK(along < -50.0f && along > -120.0f, "turned round didn't back it up; the negative speed backs it up %.0f in a second", along);
	CHECK(most < 30.0f, "the wrong way was dropped quickly (at most %.0f forward)", most);
	Keys(0.0f, 0.0f);
	RunFrames(300);

	printf("input hook: a game that honours neither: back brakes:\n");
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
	g_rideSlope = 40.0f;
	g_onFrame = RideAlong;
	RunFrames(1500);
	g_onFrame = NULL;
	RunFrames(300);
	ez = PlayerPos()[2] - sinf(40.0f / DEG) * behind;
	CHECK(Park(6) > 0.6f && fabsf(Park(2) - ez) < 1.0f, "a spot on the steep track too (z %.1f, expected %.1f; up z %.3f)", Park(2), ez, Park(6));

	printf("tilt: riding up a 10 deg slope, the ground's normal all over the place:\n");
	SetTilt(30.0f);
	g_noise = 40.0f;
	g_rideSpeed = 300.0f;
	g_rideSlope = 10.0f;
	g_onFrame = RideAlong;
	RunFrames(2000);
	float R[9];
	AppliedRotation(R);
	float pitch = asinf(R[7]) * DEG;
	CHECK(fabsf(pitch - 10.0f) < 1.5f, "pitched by the track: %.1f deg (10)", pitch);
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
	g_rideSlope = 0.0f;
	g_onFrame = RideAlong;
	RunFrames(1300);
	SetNormalTowards(back, 60.0f);
	g_rideSlope = 60.0f;
	RunFrames(900);
	g_onFrame = NULL;
	RunFrames(300);
	CHECK(fabsf(*(float *)(g_trackSlope + 0x30) - 60.0f) < 2.0f, "CMB_TrackSlope says %.1f deg (the script won't let you off)", *(float *)(g_trackSlope + 0x30));
	float fdx = Park(0) - PlayerPos()[0], fdy = Park(1) - PlayerPos()[1], fdz = Park(2) - PlayerPos()[2];
	CHECK(Park(6) > 0.9f && sqrtf(fdx * fdx + fdy * fdy + fdz * fdz) > 140.0f,
	      "the spot is back down on the flat (up z %.2f, %.0f away)", Park(6), sqrtf(fdx * fdx + fdy * fdy + fdz * fdz));
	SetNormal(0.0f, 0.0f, 1.0f);

	printf("tilt: up a 10 deg slope, then turned on the spot:\n");
	SetTilt(30.0f);
	SetNormalTowards(back, 10.0f);
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
	CHECK(fabsf(asinf(R[7]) * DEG - 10.0f) < 1.0f, "a quarter turn: the pitch holds (%.1f deg)", asinf(R[7]) * DEG);
	*head = heading0 + 3.14159f;
	RunFrames(800);
	AppliedRotation(R);
	CHECK(fabsf(asinf(R[7]) * DEG - 10.0f) < 1.0f, "a half turn: still holds, no flip (%.1f deg)", asinf(R[7]) * DEG);
	*head = heading0;
	SetTilt(0.0f);
	RunFrames(300);

	printf("steering: a 300 turning radius, 20 deg/s when stopped:\n");
	*(float *)(g_turnRadius + 0x30) = 300.0f;
	*(float *)(g_turnStand + 0x30) = 20.0f;
	SetNormal(0.0f, 0.0f, 1.0f);
	g_rideSlope = 0.0f;
	RunFrames(300);
	g_steerTarget = heading0 + 1.5708f;   /* the player pulls round to the right */
	g_onFrame = SteerTowards;
	RunFrames(1000);
	g_onFrame = NULL;
	float turned = (*head - heading0) * DEG;
	CHECK(turned > 5.0f && turned < 30.0f, "stopped: turned %.1f deg in a second (about 20), not 90", turned);
	float from = *head;   /* the plugin won't let the heading jump back either: start from here */
	g_steerTarget = from + 1.5708f;
	g_steerMove = 300.0f;
	g_onFrame = SteerTowards;
	RunFrames(1000);
	g_onFrame = NULL;
	turned = (*head - from) * DEG;
	CHECK(turned > 25.0f && turned < 62.0f, "at 300 a second: turned %.1f deg in a second (at most 57), not 90", turned);
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
	g_onFrame = NULL;

	*(float *)(g_turnRadius + 0x30) = 0.0f;
	RunFrames(200);
	*head = heading0 + 1.5708f;
	RunFrames(200);
	CHECK(fabsf(*head - heading0 - 1.5708f) < 0.001f, "turning radius 0: steering left alone");
	*head = heading0;

	printf("steepness: turned sideways on a 60 deg face, and a level ride with a wild normal:\n");
	SetNormalTowards(back, 60.0f);
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
	g_noise = 70.0f;
	g_onFrame = RideAlong;
	RunFrames(1500);
	g_onFrame = NULL;
	g_noise = 0.0f;
	RunFrames(300);
	CHECK(*(float *)(g_trackSlope + 0x30) < 10.0f, "level, normal all over the place: %.1f deg (not refused)", *(float *)(g_trackSlope + 0x30));

	printf("park: along a steep side slope:\n");
	SetNormal(0.0f, 0.0f, 1.0f);
	g_onFrame = RideAlong;
	RunFrames(1300);   /* level ground first */
	const float sideways[3] = { cosf(HEADING), -sinf(HEADING), 0.0f };
	SetNormalTowards(sideways, 40.0f);   /* then a 40 deg slope falling away to the right, ridden level */
	RunFrames(1300);
	g_onFrame = NULL;
	RunFrames(300);
	CHECK(Park(6) > 0.934f, "the spot is back where the ground leans 20 deg or less across the bike (up z %.3f)", Park(6));
	SetNormal(0.0f, 0.0f, 1.0f);

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
}

static float g_expectRoll;   /* the INI's MaxRoll for this run */

/* Where the bone sees the seat (mesh point (0, 0, 74)): A P + t, read the game's way round. */
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
	SetTilt(30.0f);
	RunFrames(1500);
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
	RunFrames(3000);   /* the published normal is an average over the last 0.6 s or so */
	CHECK(fabsf(Ground(2) - 0.93969f) < 0.01f && fabsf(Ground(0) + 0.34202f * forward[0]) < 0.01f,
	      "CMB_GroundNormal, averaged, follows the slope (%.3f, %.3f, %.3f)", Ground(0), Ground(1), Ground(2));

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
	RunFrames(1500);
	AppliedRotation(R);
	float tilted = acosf(R[8] > 1.0f ? 1.0f : R[8]) * DEG;
	CHECK(fabsf(tilted - g_expectRoll) < 0.5f, "rolled %.2f deg, the most MaxRoll allows", tilted);
	CHECK(g_expectRoll == 0.0f || (R[6] < -0.1f && fabsf(R[7]) < 0.01f), "right side down (right goes to z %.3f), no pitch", R[6]);

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
	ZoomTests();

	printf("%s\n", g_failures ? "FAILED" : "all ok");
	return g_failures ? 1 : 0;
}
