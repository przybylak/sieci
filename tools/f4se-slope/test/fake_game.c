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
#define RAM_FORMID            (0xFE000000u | (LIGHT_INDEX << 12) | 0x845u)   /* CMB_RamSeenHi, SeenLo, Seen, Ok, HitSpeed, Hit, Enemies, MinSpeed */
#define RAM_ACTOR_FORMID      0xFF004D69u   /* the actor ahead: a created reference (test 40's super mutant's id), all 32 bits */
#define RAM_ACTOR2_FORMID     0xFF004D6Au   /* a second one, behind it (mode 11: the hits' spacing) */
#define LAMP_REF2_FORMID      0xFF001235u   /* the fresh one of a handover (test 33) */
#define COLL_CHAR_FORMID      0x0008877Fu   /* Fallout4.esm's collision layer record for L_CHARCONTROLLER (test 36) */
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

/* Test 37: the plugin's VirtualQuery calls (its region cache's misses), counted through its
 * import table, and the most in one frame of the harness. The 30 s flush of that cache
 * re-walked the rider's 88 regions in the next sync (12-16 ms, a stutter every half
 * minute); each entry lapses on its own now, the re-check spread over 30 s. */
static int g_vqCalls, g_vqFrameMax;
static bool g_vqHooked;
static SIZE_T WINAPI CountingVirtualQuery(LPCVOID p, PMEMORY_BASIC_INFORMATION mbi, SIZE_T n)
{
	g_vqCalls++;
	return VirtualQuery(p, mbi, n);
}
/* One named import of the loaded DLL pointed at ours (the import address table's slot). */
static bool HookImport(HMODULE dll, const char *name, void *with)
{
	uint8_t *base = (uint8_t *)dll;
	IMAGE_NT_HEADERS64 *nt = (IMAGE_NT_HEADERS64 *)(base + ((IMAGE_DOS_HEADER *)base)->e_lfanew);
	IMAGE_DATA_DIRECTORY *dir = &nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];
	if (!dir->VirtualAddress)
		return false;
	for (IMAGE_IMPORT_DESCRIPTOR *imp = (IMAGE_IMPORT_DESCRIPTOR *)(base + dir->VirtualAddress); imp->Name; imp++) {
		IMAGE_THUNK_DATA64 *names = (IMAGE_THUNK_DATA64 *)(base + imp->OriginalFirstThunk), *slots = (IMAGE_THUNK_DATA64 *)(base + imp->FirstThunk);
		for (; names->u1.AddressOfData; names++, slots++) {
			if (names->u1.Ordinal & IMAGE_ORDINAL_FLAG64)
				continue;
			if (strcmp((const char *)((IMAGE_IMPORT_BY_NAME *)(base + names->u1.AddressOfData))->Name, name) != 0)
				continue;
			DWORD old;
			if (!VirtualProtect(&slots->u1.Function, sizeof(slots->u1.Function), PAGE_READWRITE, &old))
				return false;
			slots->u1.Function = (ULONGLONG)(uintptr_t)with;
			VirtualProtect(&slots->u1.Function, sizeof(slots->u1.Function), old, &old);
			return true;
		}
	}
	return false;
}

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
static uint8_t *g_lampRef2, *g_lampRef2Loaded, *g_lampRef2Root;
static uint8_t *g_collChar;    /* BGSCollisionLayer COLL 0008877F: what the character controller collides with */
static bool g_collHidden;      /* one test: the form lookup finds no such record */
static uint8_t *g_handsShape, *g_handsSkin, *g_handsData, *g_handsBones, *g_handsXf[5], g_handsBonesOriginal[5 * 0x50];
static uint8_t *g_partData[4], *g_partBones[4];   /* the Harley build's moving parts: front wheel, rear wheel, bar assembly, the lower fork (test 38) */
static uint8_t g_partBonesOriginal[4][0x50];
static bool g_handRaised;         /* the left hand swung up about the elbow, 20% nearer the shoulder (a Pip-Boy raise: test 37's lean solved from it) */
static float g_handReach;         /* 0: the hand where the clips pose it (98.5% of the arm's reach); else swung about the elbow, in the arm's plane, to this share of the reach (test 39: the lean's readings of 95% and 100%) */
static bool g_handFar;            /* the arm raised up and back, straight (a menu or a load's pose: test 39's ride-end wrist line read 116% of the reach) */
static bool g_armRight;           /* the arm's three nodes named and placed as the right arm's, mirrored across the bike's x = 0 (z -> 120 - z in the actor's frame here), the right hand's rotation: test 39's HandPitch on the other hand */
static float g_handRot[2][9];     /* the hand's rotation in the actor's frame, the left's and the right's: the clips' (ClipsHand) */
/* The rider: the body skinned to two bones, the COM the bike hangs off, a plain shape (the
 * Pip-Boy's) under a bone of its own. Their world transforms follow the player (SyncFakeWorld). */
static uint8_t *g_bodyShape, *g_bodySkin, *g_bodyData, *g_bodyBones, *g_bodyNodes[12], *g_comNode, *g_pipboyBone, *g_pipboyShape, *g_npcRoot;
static uint8_t g_bodyBonesOriginal[12 * 0x50], g_pipboyLocalOriginal[0x40];
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
static float PlayerHeading(void);
static void FakeGetPosition(uint8_t *self, float *out, bool centre)
{
	(void)self; (void)centre;
	for (int i = 0; i < 3; i++)
		out[i] = PlayerPosition()[i] * HAVOK;
	out[3] = 0.0f;
}
static int g_setPositions;   /* the calls so far: the plugin's pushes (the reverse by steps after rays) */
/* Mode 12: each of the plugin's steps, recorded while g_rec is set: its dz and length, when
 * (QPC seconds), the feet's z after it and their height over the ground there (FakeGroundAt),
 * and the z the fake's own fall had done by then (g_physGame, the game's share). */
#define REC_MAX 4096
static bool g_rec;
static int g_recN;
static float g_recDz[REC_MAX], g_recStep[REC_MAX], g_recZ[REC_MAX], g_recGap[REC_MAX], g_recGame[REC_MAX], g_recU[REC_MAX];
static double g_recT[REC_MAX];
static float g_physGame;
static float FakeGroundAt(float x, float y);
static float ProfileU(float x, float y);
static void FakeSetPosition(uint8_t *self, const float *p, bool centre, bool warp)
{
	(void)self; (void)centre; (void)warp;
	g_setPositions++;
	bool rec = g_rec && g_recN < REC_MAX && (g_honour & 4);
	if (rec) {
		LARGE_INTEGER now, frequency;
		QueryPerformanceCounter(&now);
		QueryPerformanceFrequency(&frequency);
		g_recDz[g_recN] = p[2] / HAVOK - PlayerPosition()[2];
		g_recStep[g_recN] = hypotf(p[0] / HAVOK - PlayerPosition()[0], p[1] / HAVOK - PlayerPosition()[1]);
		g_recT[g_recN] = (double)now.QuadPart / (double)frequency.QuadPart;
	}
	if (g_honour & 4)
		for (int i = 0; i < 3; i++)
			PlayerPosition()[i] = p[i] / HAVOK;
	if (rec) {
		const float *q = PlayerPosition();
		g_recZ[g_recN] = q[2];
		g_recGap[g_recN] = q[2] - FakeGroundAt(q[0], q[1]);
		g_recGame[g_recN] = g_physGame;
		g_recU[g_recN] = ProfileU(q[0], q[1]);
		g_recN++;
	}
}
static void FakeGetVelocity(uint8_t *self, float *out) { (void)self; memcpy(out, g_fakeVel, 16); }

/* The world the rays see: flat ground at g_groundZ (none past the drop's edge, when there's
 * one, layer 13 terrain), up to three vertical planes (walls, layer 1 static, or a trigger
 * volume, layer 12) facing the bike, and a shelf (a horizontal disc of radius 60, layer 1,
 * g_shelfHeight above the ground, g_shelfAhead ahead of the player along their heading: the
 * front wheel's down-ray reading a face taller than the wheel climbs, test 35; or an actor's
 * top, layer 30, test 39). The game's
 * picking: bhkPickData (ours: start +0x20, end +0x30, hit +0x60, fraction +0x64, the hit's
 * layer +0xAC, world +0xC0), TESObjectCELL::Pick, found through an Address Library file the
 * test writes next to the plugin. */
/* top: this high above the ground, 0 = no top (a wall); bottom: from this high up (a rail at
 * axle height), 0 = from the ground; follow: 0 = where point and normal say, else this far
 * ahead of the player along their heading, facing them, wherever they go (test 35: a face
 * behind the front wheel's edge, the bike on top of a thing it climbed). */
/* what: the hit's 3D object (NULL: FakeWall, or nothing for a trigger); test 36's self-hit is the player's root. */
/* slant: 0 = a vertical face; else the face rises away from the player at this many degrees
 * from the horizontal, its foot on the plane's line at ground level (test 37: a hillside of
 * 47 degrees, which the rays read between the axle and 1.5 radii as 47). */
typedef struct { bool on; float point[2], normal[2]; uint32_t layer; float top, bottom, follow, slant; uint8_t *what; } FakePlane;
static bool g_shelfOn;
static float g_shelfHeight, g_shelfAhead, g_shelfRadius = 60.0f;   /* a disc this high over the ground (a hole this deep in it when negative: test 38), this far ahead of the player along their heading, of this radius */
static uint32_t g_shelfLayer = 1;  /* the disc's layer, and its 3D (NULL: FakeShelf): test 39's radstag is layer 30, "SkeletonExport" */
static uint8_t *g_shelfWhat;
static float g_groundZ = 100.0f;
static float g_slopeK, g_slopeO[2], g_slopeD[2];   /* the ground rises g_slopeK per unit along g_slopeD from g_slopeO */
static bool g_kinkOn;             /* mode 10 (test 40's finding 8): past g_kinkAt along g_slopeD from g_slopeO the ground is flat at the slope's height there (down a slope onto the flat) */
static float g_kinkAt;
/* Mode 12 (test 40's finding 6): the ground along g_slopeD from g_slopeO a profile through up to
 * 12 points (u along it, z over g_groundZ), level before the first and past the last, in place
 * of the plane's slope; and a ripple of g_rippleAmp over g_rippleWave units along it that only
 * vertical rays see (the feet's, the window's and the wheels'). Off in the other modes. */
static bool g_profileOn;
static int g_profileN;
static float g_profileU[12], g_profileZ[12], g_rippleAmp, g_rippleWave = 4.0f;
static float ProfileU(float x, float y) { return (x - g_slopeO[0]) * g_slopeD[0] + (y - g_slopeO[1]) * g_slopeD[1]; }
static float ProfileZ(float u)
{
	if (g_profileN <= 0 || u <= g_profileU[0])
		return g_profileN > 0 ? g_profileZ[0] : 0.0f;
	for (int i = 1; i < g_profileN; i++)
		if (u <= g_profileU[i]) {
			float du = g_profileU[i] - g_profileU[i - 1];
			return du > 0.0f ? g_profileZ[i - 1] + (g_profileZ[i] - g_profileZ[i - 1]) * (u - g_profileU[i - 1]) / du : g_profileZ[i];
		}
	return g_profileZ[g_profileN - 1];
}
static float ProfileGround(float x, float y, bool ripple)
{
	float u = ProfileU(x, y), z = g_groundZ + ProfileZ(u);
	if (ripple && g_rippleAmp != 0.0f && g_rippleWave > 0.0f)
		z += g_rippleAmp * sinf(6.2831853f * u / g_rippleWave);
	return z;
}
/* Where the ray a..b first crosses the profile's ground, as a fraction of the way (2: nowhere):
 * a vertical ray at once (with the ripple), any other piecewise, the profile being straight
 * between the fractions where the ray passes its points. */
static float ProfileHit(const float *a, const float *b)
{
	if (a[0] == b[0] && a[1] == b[1]) {
		if (b[2] == a[2])
			return 2.0f;
		float t = (ProfileGround(a[0], a[1], true) - a[2]) / (b[2] - a[2]);
		return t >= 0.0f && t <= 1.0f ? t : 2.0f;
	}
	float ua = ProfileU(a[0], a[1]), ub = ProfileU(b[0], b[1]), ts[14];
	int n = 0;
	ts[n++] = 0.0f;
	for (int i = 0; i < g_profileN; i++)
		if ((g_profileU[i] - ua) * (g_profileU[i] - ub) < 0.0f)
			ts[n++] = (g_profileU[i] - ua) / (ub - ua);
	ts[n++] = 1.0f;
	for (int i = 1; i < n; i++)
		for (int j = i; j > 0 && ts[j] < ts[j - 1]; j--) {
			float q = ts[j];
			ts[j] = ts[j - 1];
			ts[j - 1] = q;
		}
	for (int i = 0; i + 1 < n; i++) {
		float t0 = ts[i], t1 = ts[i + 1];
		float f0 = a[2] + (b[2] - a[2]) * t0 - g_groundZ - ProfileZ(ua + (ub - ua) * t0);
		float f1 = a[2] + (b[2] - a[2]) * t1 - g_groundZ - ProfileZ(ua + (ub - ua) * t1);
		if ((f0 >= 0.0f) != (f1 >= 0.0f))
			return f0 == f1 ? t0 : t0 + (t1 - t0) * f0 / (f0 - f1);
	}
	return 2.0f;
}
static bool g_dropOn, g_frozen;   /* g_frozen: the movement can't move the player (stuck against something) */
static float g_creepDrag;         /* rough ground: only the input above this moves the player */
static int g_pileCount;           /* a pile of clutter (layer 4): this many surfaces 5 apart above the ground, within 60 of g_pilePoint */
static uint32_t g_pileLayer = 4;  /* ... of this layer, and this 3D (NULL: none): a pile of actors' surfaces (layer 30, test 40's review) */
static uint8_t *g_pileWhat;
static float g_pilePoint[2];
static FakePlane g_planes[3];
/* Mode 10's stage-2 checks only (R4): plane i's top as a flat surface at its top over the
 * ground, from its face to this far past it (0: none, as everywhere else), seen by rays coming
 * down onto it (stage 2's rays down find a step's top there). */
static float g_planeTopDepth[3];
static float g_dropPoint[2], g_dropDir[2];
static uint8_t *g_wallObj, *g_groundObj, *g_shelfObj, *g_actorObj, g_fakeWorld[64];
static uint8_t *g_ramGlobalsFake[8], *g_ramActor, *g_ramActor2, *g_actorObj2, *g_raceHuman, *g_raceMedium, *g_raceBig, *g_raceNoKnock;
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
	if (den != 0.0f || g_profileOn) {
		float tg = g_profileOn ? ProfileHit(a, b) : (g_groundZ + g_slopeK * ((a[0] - g_slopeO[0]) * g_slopeD[0] + (a[1] - g_slopeO[1]) * g_slopeD[1]) - a[2]) / den;
		float x = a[0] + (b[0] - a[0]) * tg, y = a[1] + (b[1] - a[1]) * tg;
		bool ground = !g_dropOn || (x - g_dropPoint[0]) * g_dropDir[0] + (y - g_dropPoint[1]) * g_dropDir[1] < 0.0f;
		if (g_shelfOn && g_shelfHeight < 0.0f) {   /* a hole (test 38): within the shelf's disc the ground is the shelf's plane, that far down */
			float h = PlayerHeading(), cx = PlayerPosition()[0] + sinf(h) * g_shelfAhead, cy = PlayerPosition()[1] + cosf(h) * g_shelfAhead;
			if (hypotf(x - cx, y - cy) < g_shelfRadius)
				ground = false;
		}
		if (g_kinkOn && (x - g_slopeO[0]) * g_slopeD[0] + (y - g_slopeO[1]) * g_slopeD[1] > g_kinkAt)
			ground = false;   /* past the kink: the flat's, below */
		if (tg >= 0.0f && tg <= 1.0f && ground) {
			t = tg;
			what = g_groundObj;
			layer = 13;
		}
	}
	if (g_kinkOn && b[2] != a[2]) {
		float zk = g_groundZ + g_slopeK * g_kinkAt, tf = (zk - a[2]) / (b[2] - a[2]);
		float x = a[0] + (b[0] - a[0]) * tf, y = a[1] + (b[1] - a[1]) * tf;
		if (tf >= 0.0f && tf <= 1.0f && tf < t && (x - g_slopeO[0]) * g_slopeD[0] + (y - g_slopeO[1]) * g_slopeD[1] >= g_kinkAt) {
			t = tf;
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
			what = g_pileWhat;
			layer = g_pileLayer;
		}
	}
	if (g_shelfOn && b[2] != a[2]) {
		float tp = (g_groundZ + g_shelfHeight - a[2]) / (b[2] - a[2]);
		float h = PlayerHeading(), cx = PlayerPosition()[0] + sinf(h) * g_shelfAhead, cy = PlayerPosition()[1] + cosf(h) * g_shelfAhead;
		float x = a[0] + (b[0] - a[0]) * tp, y = a[1] + (b[1] - a[1]) * tp;
		if (tp >= 0.0f && tp <= 1.0f && tp < t && hypotf(x - cx, y - cy) < g_shelfRadius) {
			t = tp;
			what = g_shelfWhat ? g_shelfWhat : g_shelfObj;
			layer = g_shelfLayer;
		}
	}
	for (int i = 0; i < 3; i++) {
		const FakePlane *w = &g_planes[i];
		if (!w->on)
			continue;
		float point[2] = { w->point[0], w->point[1] }, normal[2] = { w->normal[0], w->normal[1] };
		if (w->follow != 0.0f) {   /* resolved per cast: wherever the player is now, facing them */
			float h = PlayerHeading(), fx = sinf(h), fy = cosf(h);
			point[0] = PlayerPosition()[0] + fx * w->follow;
			point[1] = PlayerPosition()[1] + fy * w->follow;
			normal[0] = -fx;
			normal[1] = -fy;
		}
		float cot = w->slant > 0.0f ? 1.0f / tanf(w->slant / DEG) : 0.0f;   /* a slanted face sits further from the player the higher up: its surface is where the distance to the foot line equals the height over the ground times the cotangent */
		float da = (a[0] - point[0]) * normal[0] + (a[1] - point[1]) * normal[1] + (a[2] - g_groundZ) * cot;
		float db = (b[0] - point[0]) * normal[0] + (b[1] - point[1]) * normal[1] + (b[2] - g_groundZ) * cot;
		if (!(da > 0.0f && db <= 0.0f))
			continue;
		float tp = da / (da - db), z = a[2] + (b[2] - a[2]) * tp;
		if (w->top > 0.0f && z > g_groundZ + w->top)
			continue;   /* over the top of it */
		if (w->bottom > 0.0f && z < g_groundZ + w->bottom)
			continue;   /* under it */
		if (tp < t) {
			t = tp;
			what = w->what ? w->what : w->layer == 12 ? NULL : g_wallObj;
			layer = w->layer;
		}
	}
	for (int i = 0; i < 3; i++) {   /* the planes' flat tops (mode 10's stage 2): a ray coming down onto one */
		const FakePlane *w = &g_planes[i];
		if (!w->on || g_planeTopDepth[i] <= 0.0f || w->top <= 0.0f || w->follow != 0.0f)
			continue;
		float zt = g_groundZ + w->top;
		if (!(a[2] > zt && b[2] <= zt))
			continue;
		float tp = (zt - a[2]) / (b[2] - a[2]), x = a[0] + (b[0] - a[0]) * tp, y = a[1] + (b[1] - a[1]) * tp;
		float sd = (x - w->point[0]) * w->normal[0] + (y - w->point[1]) * w->normal[1];   /* + in front of the face */
		if (sd <= 0.0f && sd >= -g_planeTopDepth[i] && tp < t) {
			t = tp;
			what = w->what ? w->what : g_wallObj;
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

/* A setting changed in this run's CMB_Slope.ini (next to the plugin, the working directory): the
 * plugin reads some again on getting on. */
static void RewriteIni(const char *from, const char *to)
{
	static char buf[16384], out[16384];
	FILE *f = fopen("CMB_Slope.ini", "rb");
	if (!f) {
		printf("  (no CMB_Slope.ini here to rewrite)\n");
		return;
	}
	size_t n = fread(buf, 1, sizeof(buf) - 1, f);
	fclose(f);
	buf[n] = 0;
	char *at = strstr(buf, from);
	if (!at) {
		printf("  (%s not in CMB_Slope.ini)\n", from);
		return;
	}
	size_t head = (size_t)(at - buf);
	memcpy(out, buf, head);
	out[head] = 0;
	strcat(out, to);
	strcat(out, at + strlen(from));
	f = fopen("CMB_Slope.ini", "wb");
	if (f) {
		fwrite(out, 1, strlen(out), f);
		fclose(f);
	}
}
static void SetHeadlamp(float on) { *(float *)(g_headlampLive + 0x30) = on; }
static void SetLampRef(uint32_t id) { *(float *)(g_headlampRefHi + 0x30) = (float)(id >> 16); *(float *)(g_headlampRefLo + 0x30) = (float)(id & 0xFFFFu); }
static float Ground(int i) { return *(float *)(g_groundGlobals[i] + 0x30); }
static float Park(int i) { return *(float *)(g_parkGlobals[i] + 0x30); }
static float *PlayerPos(void) { return (float *)(g_player + 0xD0); }
static float *PlayerPosition(void) { return PlayerPos(); }
static float PlayerHeading(void) { return *(const float *)(g_player + 0xC8); }
static void SetNormal(float x, float y, float z)
{
	float *n = (float *)(g_controller + 0x1E0);
	n[0] = x; n[1] = y; n[2] = z; n[3] = 0.03f;
}
static void SetState(int state) { *(int32_t *)(g_controller + 0x2C0) = state; }
/* The controller's supported bit (0x400 of its flags at +0x300, CheckSupportImpl's word in the
 * game; test 19): clear in this fake unless a test sets it. */
static void SetSupported(bool on)
{
	uint32_t *flags = (uint32_t *)(g_controller + 0x300);
	*flags = on ? (*flags | 0x400u) : (*flags & ~0x400u);
}
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
	if (id == LAMP_REF2_FORMID)
		return (uintptr_t)g_lampRef2;
	if (id == COLL_CHAR_FORMID)
		return g_collHidden ? 0 : (uintptr_t)g_collChar;
	if (id >= RAM_FORMID && id < RAM_FORMID + 8)
		return (uintptr_t)g_ramGlobalsFake[id - RAM_FORMID];
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
	*(float *)(g_controller + 0x370) = 0.257175f;   /* the capsule's radius (18.0 units), height (128.0), step height (31.0) and cast depth (33.5), as the round-1 dump read them (test 40's finding 8) */
	*(float *)(g_controller + 0x374) = 1.8288f;
	*(float *)(g_controller + 0x424) = 0.442912f;
	*(float *)(g_controller + 0x430) = 0.479206f;
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
	static const char *ram[8] = { "CMB_RamSeenHi", "CMB_RamSeenLo", "CMB_RamSeen", "CMB_RamOk", "CMB_RamHitSpeed", "CMB_RamHit", "CMB_RamEnemies", "CMB_RamMinSpeed" };
	for (int i = 0; i < 8; i++)
		g_ramGlobalsFake[i] = NewGlobal(RAM_FORMID + (uint32_t)i, ram[i]);
	*(float *)(g_ramGlobalsFake[6] + 0x30) = 1.0f;     /* the MCM's defaults */
	*(float *)(g_ramGlobalsFake[7] + 0x30) = 450.0f;
	*(float *)(g_ramGlobalsFake[2] + 0x30) = 57.0f;    /* a save's: the plugin's asks go on from it */
	/* The collision layer records (test 36): the character controller's, with what it collides
	 * with (Fallout4.esm's list: not clutter (4), bipeds (8), non-collidable (15), dead bipeds (32)
	 * or navcut (49); test 37: the phantoms it does hold, spells (7), cloud traps (16), the
	 * query and pick layers 38 to 46, living-and-dead actors (52), trap triggers (54) and
	 * character bumpers (56), which the rays must pass through all the same). TESForm (0x20)
	 * and TESDescription (0x18, as in the game: test 37 found the index at +0x30 reading 874),
	 * then the index at +0x38 and the collides-with array at +0x50 (entries, capacity, count);
	 * the record 0x68 bytes. */
	{
		static const char *coll[] = { ".?AVBGSCollisionLayer@@", ".?AVTESForm@@", ".?AVTESDescription@@" };
		static const uint32_t with[] = { 1, 2, 3, 7, 9, 10, 12, 13, 14, 16, 17, 18, 20, 21, 22, 26, 27, 28, 29, 30, 31, 33, 35, 36,
		                                 38, 39, 40, 41, 42, 43, 44, 45, 46, 52, 54, 56 };
		void **vtColl = MakeClass(coll, 3);
		uint8_t **entries = (uint8_t **)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
		int n = (int)(sizeof(with) / sizeof(with[0]));
		for (int i = 0; i < n; i++) {
			uint8_t *layer = (uint8_t *)NewObject(vtColl, 0x68);
			*(uint32_t *)(layer + 0x14) = 0x00088700u | with[i];
			*(uint32_t *)(layer + 0x38) = with[i];
			entries[i] = layer;
		}
		g_collChar = (uint8_t *)NewObject(vtColl, 0x68);
		*(uint32_t *)(g_collChar + 0x14) = COLL_CHAR_FORMID;
		*(uint32_t *)(g_collChar + 0x38) = 30;
		*(uint8_t ***)(g_collChar + 0x50) = entries;
		*(uint32_t *)(g_collChar + 0x58) = 64;   /* the capacity */
		*(uint32_t *)(g_collChar + 0x60) = (uint32_t)n;
	}
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
	g_shelfObj = NewNode(vtNode, "FakeShelf", 0);
	g_actorObj = NewNode(vtNode, "SkeletonExport", 0);   /* an actor's capsule, as test 39's radstag named it */
	{
		/* The actor behind it (finding 7): its 3D's user data (+0x110) is the Actor, whose loaded
		 * 3D root is that node; a race (TESRace: data at +0x180, flags +0x1A0, size +0x1AC, editor
		 * ID +0x3A0) of each kind the rams look at; the rider's race HumanRace. */
		static const char *actorNames[] = { ".?AVActor@@", ".?AVTESObjectREFR@@", ".?AVTESForm@@" };
		static const char *raceNames[] = { ".?AVTESRace@@", ".?AVTESForm@@" };
		void **vtActor = MakeClass(actorNames, 3), **vtRace = MakeClass(raceNames, 2);
		uint8_t **races[4] = { &g_raceHuman, &g_raceMedium, &g_raceBig, &g_raceNoKnock };
		static const char *raceIds[4] = { "HumanRace", "RaiderTestRace", "SupermutantBehemothRace", "ProtectronTestRace" };
		static const uint32_t raceSizes[4] = { 1, 1, 3, 1 }, raceFlags[4] = { 0x3, 0x100, 0x100, 0x400100 };
		for (int i = 0; i < 4; i++) {
			uint8_t *r = (uint8_t *)NewObject(vtRace, 0x800);
			*(uint32_t *)(r + 0x14) = 0x00013746u + (uint32_t)i;
			r[0x1A] = 0x11;
			*(uint32_t *)(r + 0x1A0) = raceFlags[i];
			*(uint32_t *)(r + 0x1AC) = raceSizes[i];
			*(uint8_t **)(r + 0x3A0) = NewString(raceIds[i]);
			*races[i] = r;
		}
		g_ramActor = (uint8_t *)NewObject(vtActor, 0x1000);
		*(uint32_t *)(g_ramActor + 0x14) = RAM_ACTOR_FORMID;
		g_ramActor[0x1A] = 0x41;
		uint8_t *actorLoaded = (uint8_t *)VirtualAlloc(NULL, 0x100, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
		*(uint8_t **)(actorLoaded + 0x08) = g_actorObj;
		*(uint8_t **)(g_ramActor + 0xF0) = actorLoaded;
		*(uint8_t **)(g_ramActor + 0x418) = g_raceMedium;
		*(uint8_t **)(g_actorObj + 0x110) = g_ramActor;
		*(uint8_t **)(g_player + 0x418) = g_raceHuman;
		/* A second one (mode 11, test 41's check of the hits' spacing: two raiders one behind the
		 * other), its 3D named as test 40's settler's was, "skeleton.nif", which the rider's own
		 * root is called too: only the pointer tells them apart. */
		g_actorObj2 = NewNode(vtNode, "skeleton.nif", 0);
		g_ramActor2 = (uint8_t *)NewObject(vtActor, 0x1000);
		*(uint32_t *)(g_ramActor2 + 0x14) = RAM_ACTOR2_FORMID;
		g_ramActor2[0x1A] = 0x41;
		uint8_t *actorLoaded2 = (uint8_t *)VirtualAlloc(NULL, 0x100, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
		*(uint8_t **)(actorLoaded2 + 0x08) = g_actorObj2;
		*(uint8_t **)(g_ramActor2 + 0xF0) = actorLoaded2;
		*(uint8_t **)(g_ramActor2 + 0x418) = g_raceMedium;
		*(uint8_t **)(g_actorObj2 + 0x110) = g_ramActor2;
	}
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
	g_bodyNodes[0] = NewNode(vtNode, "NPC Pelvis [Pelv]", 2);   /* a skin helper under it (test 38's pose study) */
	g_bodyNodes[1] = NewNode(vtNode, "NPC Spine [Spn0]", 0);
	g_bodyNodes[2] = NewNode(vtNode, "NPC Spine1 [Spn1]", 2);   /* in the skin with no vertices of its own (test 24); a skin helper under it (test 38's pose study) */
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
	/* The body's skin helpers (test 38's pose study: Belly_skin and its kind were left where
	 * the clips put them while the torso leaned, a hump on the upper back): a bone whose name
	 * gives no part takes the first found up its node parents. Belly_skin under SPINE1 takes
	 * the upper body; LLeg_Thigh_skin under the pelvis has no part anywhere up its chain (the
	 * pelvis, the NPC root, the skeleton's root) and is carried with the tilt alone. */
	g_bodyNodes[10] = NewNode(vtNode, "Belly_skin", 0);
	AddChild(g_bodyNodes[2], g_bodyNodes[10]);
	*(uint8_t **)(g_bodyNodes[10] + 0x28) = g_bodyNodes[2];
	g_bodyNodes[11] = NewNode(vtNode, "LLeg_Thigh_skin", 0);
	AddChild(g_bodyNodes[0], g_bodyNodes[11]);
	*(uint8_t **)(g_bodyNodes[11] + 0x28) = g_bodyNodes[0];
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
	/* The fresh reference of a handover: the same again, its 3D not in yet. */
	g_lampRef2 = (uint8_t *)NewObject(MakeClass(refNames, 3), 0x200);
	g_lampRef2[0x1A] = 0x40;
	*(uint32_t *)(g_lampRef2 + 0x14) = LAMP_REF2_FORMID;
	g_lampRef2Loaded = (uint8_t *)VirtualAlloc(NULL, 0x100, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	*(uint8_t **)(g_lampRef2 + 0xF0) = g_lampRef2Loaded;
	g_lampRef2Root = NewNode(vtNode, "CMB_HeadlampLight", 2);
	{
		uint8_t *light2 = NewNode(vtNode, "Light", 0);
		AddChild(g_lampRef2Root, light2);
		*(uint8_t **)(light2 + 0x28) = g_lampRef2Root;
		float *rr2 = (float *)(g_lampRef2Root + 0x30);
		rr2[0] = rr2[5] = rr2[10] = 1.0f;
		rr2[15] = 1.0f;
	}
	*(uint8_t **)(g_lampRef2Loaded + 0x08) = NULL;
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
	 * cache, as the game shares it with every NPC in the mesh) and its twelve bones. */
	g_bodySkin = (uint8_t *)NewObject(vtSkin, 0x100);
	*(int32_t *)(g_bodySkin + 0x08) = 1;
	*(uint8_t **)(g_bodyShape + 0x140) = g_bodySkin;
	g_bodyData = (uint8_t *)NewObject(vtBone, 0x100);
	*(int32_t *)(g_bodyData + 0x08) = 2;
	*(uint8_t **)(g_bodySkin + 0x40) = g_bodyData;
	g_bodyBones = (uint8_t *)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	*(uint8_t **)(g_bodyData + 0x10) = g_bodyBones;
	*(uint32_t *)(g_bodyData + 0x18) = 12;
	*(uint32_t *)(g_bodyData + 0x20) = 12;
	uint8_t **bodyList = (uint8_t **)VirtualAlloc(NULL, 0x100, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	for (int i = 0; i < 12; i++)
		bodyList[i] = g_bodyNodes[i];
	*(uint8_t ***)(g_bodySkin + 0x28) = bodyList;
	*(uint32_t *)(g_bodySkin + 0x30) = 12;
	*(uint32_t *)(g_bodySkin + 0x38) = 12;
	/* A blood decal on the body: its own shape, a skin instance cloned from the body's (the same
	 * bone list; it points wherever the body's points when it's made: test 29). Not in the 3D yet. */
	g_decalShape = NewNode(vtTri, "BloodDecal:0", 0);
	*(uint8_t **)(g_decalShape + 0x28) = npcRoot;
	g_decalSkin = (uint8_t *)NewObject(vtSkin, 0x100);
	*(int32_t *)(g_decalSkin + 0x08) = 1;
	*(uint8_t **)(g_decalShape + 0x140) = g_decalSkin;
	*(uint8_t ***)(g_decalSkin + 0x28) = bodyList;
	*(uint32_t *)(g_decalSkin + 0x30) = 12;
	*(uint32_t *)(g_decalSkin + 0x38) = 12;
	/* The hands (test 34): a skin whose finger bones have no node, only a world transform of
	 * their own in the actor's flattened bone tree. As the game lays it out: the nodes at +0x10
	 * (null for those) and a pointer to every bone's world transform at +0x28 (into the node
	 * for a bone with one). Five bones: two fingers beyond the hand, the wrist end of the
	 * forearm behind it, the hand (LArm_Hand's node), and a stray bone far from any hand. */
	g_handsShape = NewNode(vtTri, "NakedHands:0", 0);
	AddChild(npcRoot, g_handsShape);
	*(uint8_t **)(g_handsShape + 0x28) = npcRoot;
	g_handsSkin = (uint8_t *)NewObject(vtSkin, 0x100);
	*(int32_t *)(g_handsSkin + 0x08) = 1;
	*(uint8_t **)(g_handsShape + 0x140) = g_handsSkin;
	g_handsData = (uint8_t *)NewObject(vtBone, 0x100);
	*(int32_t *)(g_handsData + 0x08) = 2;
	*(uint8_t **)(g_handsSkin + 0x40) = g_handsData;
	g_handsBones = (uint8_t *)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	*(uint8_t **)(g_handsData + 0x10) = g_handsBones;
	*(uint32_t *)(g_handsData + 0x18) = 5;
	*(uint32_t *)(g_handsData + 0x20) = 5;
	uint8_t **handsNodes = (uint8_t **)VirtualAlloc(NULL, 0x100, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	uint8_t **handsXfs = (uint8_t **)VirtualAlloc(NULL, 0x100, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	for (int i = 0; i < 5; i++) {
		handsNodes[i] = i == 3 ? g_bodyNodes[5] : NULL;
		g_handsXf[i] = i == 3 ? g_bodyNodes[5] + 0x70 : (uint8_t *)VirtualAlloc(NULL, 0x40, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
		handsXfs[i] = g_handsXf[i];
	}
	*(uint8_t ***)(g_handsSkin + 0x10) = handsNodes;
	*(uint32_t *)(g_handsSkin + 0x18) = 5;
	*(uint32_t *)(g_handsSkin + 0x20) = 5;
	*(uint8_t ***)(g_handsSkin + 0x28) = handsXfs;
	*(uint32_t *)(g_handsSkin + 0x30) = 5;
	*(uint32_t *)(g_handsSkin + 0x38) = 5;

	/* The moving parts of the Harley build: four more shapes under the bike's node, each
	 * with its own skin and bone data (the same bind; their culling spheres on the axles
	 * and ahead of the steering head, which is how the plugin tells them apart; the lower
	 * fork's sits low at the front too, and its name says what it is: test 38). */
	static const char *partNames[4] = { "CMB_BikeWornRider_wheelF", "CMB_BikeWornRider_wheelR", "CMB_BikeWornRider_front_metal", "CMB_BikeWornRider_fork_metal" };
	for (int i = 0; i < 4; i++) {
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

static float Dist3(const float a[3], const float b[3]);

/* The plugin's long axis of the hand in the hand bone's own frame (its g_handAxis: the hand's
 * joint to the middle finger's knuckle on the vanilla skeleton), [0] the left, [1] the right. */
static const float g_handAxisLocal[2][3] = { { 0.99489f, 0.08131f, 0.05994f }, { 0.99487f, 0.08146f, -0.05990f } };

/* The clips' hand as test 39 found it (riding_anims.py's Rider._arm: the fingers (+-0.18, 0.75,
 * -0.62) in the bike's space, 39 deg below level, the palm down, frame_from_axes with the
 * hint (0, 0.55, 0.85)), turned so the hand's long axis lies along those fingers, taken to the
 * actor's frame through the bike's bind (the bike hangs off COM, which turns with the heading
 * alone here): out g_handAxisLocal = the bind's map of the fingers. */
static void ClipsHand(int side, float out[9])
{
	static const float A[9] = { 0, 0, 1, 0, 1, 0, -1, 0, 0 };   /* the bike's skin-to-bone rotation (SetLayouts) */
	const float *a = g_handAxisLocal[side];
	float sg = side ? 1.0f : -1.0f, x[3] = { 0.18f * sg, 0.75f, -0.62f }, hint[3] = { 0.0f, 0.55f, 0.85f }, y[3], z[3], H[9], C[9], HC[9];
	float lx = sqrtf(x[0] * x[0] + x[1] * x[1] + x[2] * x[2]), hx = 0.0f, ly;
	for (int i = 0; i < 3; i++) {
		x[i] /= lx;
		hx += hint[i] * x[i];
	}
	for (int i = 0; i < 3; i++)
		y[i] = hint[i] - hx * x[i];
	ly = sqrtf(y[0] * y[0] + y[1] * y[1] + y[2] * y[2]);
	for (int i = 0; i < 3; i++)
		y[i] /= ly;
	z[0] = x[1] * y[2] - x[2] * y[1];
	z[1] = x[2] * y[0] - x[0] * y[2];
	z[2] = x[0] * y[1] - x[1] * y[0];
	for (int i = 0; i < 3; i++) {
		H[i * 3] = x[i];
		H[i * 3 + 1] = y[i];
		H[i * 3 + 2] = z[i];
	}
	/* C: the least rotation taking the long axis a to the bone's x (Rodrigues about a x e_x). */
	float ax[3] = { 0.0f, a[2], -a[1] }, la = sqrtf(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]), sn = sqrtf(ax[1] * ax[1] + ax[2] * ax[2]) / la, c = a[0] / la, k = 1.0f - c;
	float ls = sqrtf(ax[1] * ax[1] + ax[2] * ax[2]);
	for (int i = 0; i < 3; i++)
		ax[i] /= ls;
	C[0] = c + ax[0] * ax[0] * k;         C[1] = ax[0] * ax[1] * k - ax[2] * sn; C[2] = ax[0] * ax[2] * k + ax[1] * sn;
	C[3] = ax[1] * ax[0] * k + ax[2] * sn; C[4] = c + ax[1] * ax[1] * k;         C[5] = ax[1] * ax[2] * k - ax[0] * sn;
	C[6] = ax[2] * ax[0] * k - ax[1] * sn; C[7] = ax[2] * ax[1] * k + ax[0] * sn; C[8] = c + ax[2] * ax[2] * k;
	MulM3(H, C, HC);
	MulM3(A, HC, out);
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
	/* The left hand about where the left grip is, the shoulder and the elbow behind it with
	 * the arm nearly straight, as the riding clips pose it (the grip at 98.5% of the arm's
	 * reach; test 38: the lean isn't solved under 95%), or, raised, swung up about the elbow
	 * (the forearm's length kept) to 80% of it: a Pip-Boy raise; or swung about the elbow to
	 * another share of the reach (g_handReach), or far off (g_handFar). Its rotation the clips'
	 * (test 39: the fingers 39 deg below the bike's forward, whatever the forearm does). With
	 * g_armRight the arm is the right one, mirrored. */
	static const float handOff[3] = { -20, 75, 120 }, handRaisedOff[3] = { -4.32f, 69.77f, 132.41f };
	static const float upperOff[3] = { -18, 42, 148 }, elbowOff[3] = { -22.5f, 57.5f, 133 };   /* the shoulder and the elbow */
	float hand[3], upper[3] = { upperOff[0], upperOff[1], upperOff[2] }, elbow[3] = { elbowOff[0], elbowOff[1], elbowOff[2] };
	memcpy(hand, g_handRaised ? handRaisedOff : handOff, sizeof(hand));
	if (g_handFar) {
		/* Up and back from the shoulder, straight: the leaned shoulder (it goes forward and
		 * down) is then further from the hand than the arm reaches. */
		static const float d[3] = { 0.0f, -0.65f, 0.76f };
		float L1 = Dist3(upperOff, elbowOff), L2 = Dist3(elbowOff, handOff), ld = sqrtf(d[1] * d[1] + d[2] * d[2]);
		for (int i = 0; i < 3; i++) {
			elbow[i] = upperOff[i] + L1 * d[i] / ld;
			hand[i] = upperOff[i] + (L1 + L2) * d[i] / ld;
		}
	} else if (g_handReach > 0.0f) {
		/* The elbow opened or closed in the arm's plane, the forearm's length kept: the angle
		 * at the elbow from the law of cosines. */
		float u[3], w0[3], v[3], L1 = Dist3(upperOff, elbowOff), L2 = Dist3(elbowOff, handOff), r = g_handReach * (L1 + L2), wu = 0.0f, lv;
		float c = (L1 * L1 + L2 * L2 - r * r) / (2.0f * L1 * L2), sn;
		c = c > 1.0f ? 1.0f : c < -1.0f ? -1.0f : c;
		sn = sqrtf(1.0f - c * c);
		for (int i = 0; i < 3; i++) {
			u[i] = (upperOff[i] - elbowOff[i]) / L1;
			w0[i] = handOff[i] - elbowOff[i];
			wu += w0[i] * u[i];
		}
		for (int i = 0; i < 3; i++)
			v[i] = w0[i] - wu * u[i];
		lv = sqrtf(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
		for (int i = 0; i < 3; i++)
			hand[i] = elbowOff[i] + L2 * (c * u[i] + sn * v[i] / lv);
	}
	if (g_armRight) {
		hand[2] = 120.0f - hand[2];
		upper[2] = 120.0f - upper[2];
		elbow[2] = 120.0f - elbow[2];
	}
	float handRot[9];
	MulM3(heading, g_handRot[g_armRight ? 1 : 0], handRot);
	Apply3(heading, hand, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[5], handRot, pos, 1.0f);
	Apply3(heading, upper, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[6], heading, pos, 1.0f);
	Apply3(heading, elbow, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[7], heading, pos, 1.0f);
	{
		/* The hands' bones without nodes: their own world transforms, with the hand (test 34),
		 * along the forearm's line from the hand in use. */
		float u[3] = { hand[0] - elbow[0], hand[1] - elbow[1], hand[2] - elbow[2] }, lu = sqrtf(u[0] * u[0] + u[1] * u[1] + u[2] * u[2]);
		static const float along[5] = { 6.0f, 10.0f, -6.0f, 0.0f, 60.0f };
		for (int k = 0; k < 3; k++)
			u[k] /= lu;
		for (int i = 0; i < 5; i++) {
			if (i == 3 || !g_handsXf[i])
				continue;
			float o[3] = { hand[0] + along[i] * u[0], hand[1] + along[i] * u[1], hand[2] + along[i] * u[2] };
			Apply3(heading, o, off);
			for (int k = 0; k < 3; k++)
				pos[k] = pp[k] + off[k];
			StoreRotation((float *)g_handsXf[i], heading, g_rootTransposed);
			memcpy(g_handsXf[i] + 0x30, pos, 12);
			*(float *)(g_handsXf[i] + 0x3C) = 1.0f;
		}
	}
	static const float headOff[3] = { 0, -2, 160 }, jawOff[3] = { 0, 3, 152 };   /* the head's joint and a face bone under it */
	Apply3(heading, headOff, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[8], heading, pos, 1.0f);
	Apply3(heading, jawOff, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[9], heading, pos, 1.0f);
	static const float bellyOff[3] = { 0, 12, 92 }, thighOff[3] = { 8, 5, 60 };   /* the skin helpers: the belly ahead of and below the spine's joint, the thigh under the pelvis (test 38's pose study) */
	Apply3(heading, bellyOff, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[10], heading, pos, 1.0f);
	Apply3(heading, thighOff, off);
	for (int i = 0; i < 3; i++)
		pos[i] = pp[i] + off[i];
	SetWorld(g_bodyNodes[11], heading, pos, 1.0f);
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
	 * (the front axle (0.4, 99.6, 29.9), the rear (0.4, -36.7, 29.9), the bar assembly's (1, 85, 57),
	 * the lower fork's (0, 85, 45): ahead of the steering head like the bar assembly's, so
	 * only its name tells the plugin it rides with the front wheel). */
	static const float spheres[4][4] = { { -44.27f, 99.6f, -0.4f, 31.0f }, { -44.27f, -36.7f, -0.4f, 31.0f }, { -17.17f, 85.0f, -1.0f, 60.0f }, { -29.17f, 85.0f, 0.0f, 30.0f } };
	for (int i = 0; i < 4; i++) {
		float *pb = (float *)g_partBones[i];
		memcpy(pb, spheres[i], sizeof(spheres[i]));
		StoreRotation(pb + 4, skinToBone, skinTransposed);
		pb[16] = -74.17f; pb[17] = 0.0f; pb[18] = 0.0f; pb[19] = 1.0f;
		memcpy(g_partBonesOriginal[i], g_partBones[i], sizeof(g_partBonesOriginal[i]));
	}
	/* The rider's body: its bones with binds of their own (the last two the skin helpers of test
	 * 38's pose study); the Pip-Boy's shape's own transform. */
	static const float bindRot[12][9] = { { 0, 0, 1, 0, 1, 0, -1, 0, 0 }, { 1, 0, 0, 0, 0, -1, 0, 1, 0 }, { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, { 0, 1, 0, -1, 0, 0, 0, 0, 1 }, { 1, 0, 0, 0, 1, 0, 0, 0, 1 },
	                                      { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, { 1, 0, 0, 0, 1, 0, 0, 0, 1 }, { 1, 0, 0, 0, 1, 0, 0, 0, 1 } };
	static const float bindPos[12][3] = { { 0, 0, -70 }, { 3, -95, 0 }, { 0, -100, 0 }, { 0, -120, 0 }, { 10, 20, -90 }, { 20, -75, -120 }, { 18, -42, -148 }, { 26, -56, -132 }, { 0, 2, -160 }, { 0, -3, -152 }, { 0, -12, -92 }, { -8, -5, -60 } };
	static const float bodySpheres[12][4] = { { 0, 0, 20, 40 }, { 0, 0, 30, 50 }, { 0, 0, 0, 0 }, { 0, 0, 5, 10 }, { 0, 0, 0, 8 }, { 0, 0, 0, 12 }, { 0, 0, 0, 14 }, { 0, 0, 0, 12 }, { 0, 0, 0, 14 }, { 0, 0, 0, 6 }, { 0, 0, 0, 10 }, { 0, 0, 0, 10 } };   /* the third: no vertices */
	for (int i = 0; i < 12; i++) {
		float *bb = (float *)(g_bodyBones + i * 0x50);
		memcpy(bb, bodySpheres[i], sizeof(bodySpheres[i]));
		StoreRotation(bb + 4, bindRot[i], skinTransposed);
		bb[16] = bindPos[i][0]; bb[17] = bindPos[i][1]; bb[18] = bindPos[i][2]; bb[19] = 1.0f;
	}
	memcpy(g_bodyBonesOriginal, g_bodyBones, sizeof(g_bodyBonesOriginal));
	{
		/* The hands' bones: fingers 6 and 10 beyond the hand along the forearm's line, the
		 * wrist end of the forearm 6 back, the hand, a stray bone 60 beyond. */
		static const float handOff[3] = { -20, 75, 120 }, u[3] = { 0.1139f, 0.7975f, -0.5924f };
		static const float along[5] = { 6.0f, 10.0f, -6.0f, 0.0f, 60.0f };
		static const float eye[9] = { 1, 0, 0, 0, 1, 0, 0, 0, 1 };
		for (int i = 0; i < 5; i++) {
			float *hb = (float *)(g_handsBones + i * 0x50);
			hb[0] = hb[1] = hb[2] = 0.0f;
			hb[3] = 6.0f;
			StoreRotation(hb + 4, eye, skinTransposed);
			for (int k = 0; k < 3; k++)
				hb[16 + k] = -(handOff[k] + along[i] * u[k]);
			hb[19] = 1.0f;
		}
		memcpy(g_handsBonesOriginal, g_handsBones, sizeof(g_handsBonesOriginal));
	}
	float *pl = (float *)(g_pipboyShape + 0x30);
	static const float tenDeg[9] = { 0.98481f, -0.17365f, 0, 0.17365f, 0.98481f, 0, 0, 0, 1 };
	StoreRotation(pl, tenDeg, rootTransposed);
	pl[12] = 1.0f; pl[13] = 2.0f; pl[14] = 3.0f; pl[15] = 1.0f;
	memcpy(g_pipboyLocalOriginal, pl, sizeof(g_pipboyLocalOriginal));
	ClipsHand(0, g_handRot[0]);
	ClipsHand(1, g_handRot[1]);
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

static double g_cappedSeconds;   /* the frames' times summed as the plugin caps them (0.05 s each): what a rate a second may have risen by */
static float g_slopeMin = 1.0f;  /* the steepest climb limit (the smallest cosine) the controller held after any frame since this was last set (test 40's finding 8) */
static int g_staleFrames;        /* mode 9: frames the 3D's world transforms stay behind the player's place after a load to another place (test 35: 0.26 s) */
static void RunFrames(int ms)
{
	DWORD end = GetTickCount() + (DWORD)ms;
	LARGE_INTEGER frequency, last, now;
	QueryPerformanceFrequency(&frequency);
	QueryPerformanceCounter(&last);
	while ((int32_t)(GetTickCount() - end) < 0) {
		QueryPerformanceCounter(&now);
		float dt = (float)(now.QuadPart - last.QuadPart) / (float)frequency.QuadPart;
		g_cappedSeconds += dt > 0.05f ? 0.05 : dt;
		int queries = g_vqCalls;
		if (g_onFrame)
			g_onFrame(dt);
		last = now;
		if (g_staleFrames > 0)
			g_staleFrames--;   /* the world a frame behind (only mode 9 sets it) */
		else
			SyncFakeWorld();
		((void (*)(Task *))g_task->vtbl[1])(g_task);
		if (g_controller && *(float *)(g_controller + CTRL_SLOPE_OFFSET) < g_slopeMin)
			g_slopeMin = *(float *)(g_controller + CTRL_SLOPE_OFFSET);
		if (g_vqCalls - queries > g_vqFrameMax)
			g_vqFrameMax = g_vqCalls - queries;   /* the plugin's memory queries this frame, hooks and task together (test 37) */
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

/* The whole map the plugin put on a shape in the bike's own space, x -> M x + m: the rotation
 * as above, the translation the bind undone the same way, m = A^T (t' - t) (the plugin writes
 * t' = t + A m). */
static void AppliedMapOf(const uint8_t *orig, const uint8_t *live, float M[9], float m[3])
{
	const float *o = (const float *)(orig + 0x10), *t = (const float *)(orig + 0x40), *tl = (const float *)(live + 0x40);
	float A[9], d[3] = { tl[0] - t[0], tl[1] - t[1], tl[2] - t[2] };
	AppliedRotationOf(orig, live, M);
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++)
			A[i * 3 + j] = g_skinTransposed ? o[j * 4 + i] : o[i * 4 + j];
	for (int i = 0; i < 3; i++)
		m[i] = A[i] * d[0] + A[3 + i] * d[1] + A[6 + i] * d[2];
}

/* A wheel's travel against the frame (the suspension, test 36): how far its map takes its axle
 * from where the frame's own map (the fixed part's) would hold it, along the frame's up; up
 * into the frame positive, dropped out of it negative. */
static const float g_axles[2][3] = { { 0.4f, 99.6f, 29.9f }, { 0.4f, -36.7f, 29.9f } };
static void PartMove(int part, const float point[3], float out[3])   /* a part's map against the frame's at a bike-space point, in the frame's own space (the tilt undone) */
{
	float M[9], m[3], F[9], f[3], a[3], b[3];
	AppliedMapOf(g_partBonesOriginal[part], g_partBones[part], M, m);
	AppliedMapOf(g_bonesOriginal, g_bones, F, f);
	Apply3(M, point, a);
	Apply3(F, point, b);
	float d[3] = { a[0] + m[0] - b[0] - f[0], a[1] + m[1] - b[1] - f[1], a[2] + m[2] - b[2] - f[2] };
	for (int i = 0; i < 3; i++)
		out[i] = d[0] * F[i] + d[1] * F[3 + i] + d[2] * F[6 + i];   /* F^T d */
}
static float PartTravel(int part, const float point[3])   /* the move along the frame's up */
{
	float d[3];
	PartMove(part, point, d);
	return d[2];
}
/* How far a part's move at the point leaves the line it should run along (test 38: the front
 * wheel's and the lower fork's the steering axis, the rear wheel's the bike's up): the move's
 * part across the unit axis. */
static float MoveOffAxis(int part, const float point[3], const float axis[3])
{
	float d[3];
	PartMove(part, point, d);
	float along = d[0] * axis[0] + d[1] * axis[1] + d[2] * axis[2], all = d[0] * d[0] + d[1] * d[1] + d[2] * d[2];
	return sqrtf(all - along * along > 0.0f ? all - along * along : 0.0f);
}
static float WheelTravel(int part)
{
	return PartTravel(part, g_axles[part]);
}

/* A rotation's angle (degrees) and unit axis. */
static float RotationAngle(const float M[9], float axis[3])
{
	float v[3] = { M[7] - M[5], M[2] - M[6], M[3] - M[1] }, l = sqrtf(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
	for (int i = 0; i < 3; i++)
		axis[i] = l > 1e-6f ? v[i] / l : 0.0f;
	float c = 0.5f * (M[0] + M[4] + M[8] - 1.0f);
	return acosf(c > 1.0f ? 1.0f : c < -1.0f ? -1.0f : c) * DEG;
}

/* How far a wheel's map moves its axle (its culling sphere's centre) in all. */
static float WheelMove(int part)
{
	float M[9], m[3], a[3];
	AppliedMapOf(g_partBonesOriginal[part], g_partBones[part], M, m);
	Apply3(M, g_axles[part], a);
	return sqrtf((a[0] + m[0] - g_axles[part][0]) * (a[0] + m[0] - g_axles[part][0]) + (a[1] + m[1] - g_axles[part][1]) * (a[1] + m[1] - g_axles[part][1])
	           + (a[2] + m[2] - g_axles[part][2]) * (a[2] + m[2] - g_axles[part][2]));
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
static void MapBoneAt(const uint8_t *xf, const uint8_t *orig, const uint8_t *copy, const float X[3], float out[3]);
static void MapBone(const uint8_t *node, const uint8_t *orig, const uint8_t *copy, const float X[3], float out[3])
{
	MapBoneAt(node + 0x70, orig, copy, X, out);
}

/* The rotation a held bone's rewritten entry puts on the world before the tilt, Mh (the
 * bone's map is the tilt Rw after it; test 38: the hand's roll round the grip): Mh d = Rw^T
 * (m(X + d) - m(X)), a column at a time. */
static void BoneRotationBefore(const uint8_t *node, const uint8_t *orig, const uint8_t *copy, const float X[3], const float Rw[9], float Mh[9])
{
	float m0[3], m1[3];
	MapBone(node, orig, copy, X, m0);
	for (int j = 0; j < 3; j++) {
		float Xd[3] = { X[0], X[1], X[2] }, d[3];
		Xd[j] += 10.0f;
		MapBone(node, orig, copy, Xd, m1);
		for (int i = 0; i < 3; i++)
			d[i] = (m1[i] - m0[i]) / 10.0f;
		for (int i = 0; i < 3; i++)
			Mh[i * 3 + j] = Rw[i] * d[0] + Rw[3 + i] * d[1] + Rw[6 + i] * d[2];   /* Rw^T d */
	}
}

/* How many lines of the plugin's log hold the text: the log is where the plugin writes it,
 * My Documents\My Games\Fallout4\F4SE\CMB_Slope.log, or next to the DLL (test 38: the lean's
 * "not solved yet" line, the solve coming again after a load). */
static FILE *OpenLog(void)
{
	static char path[MAX_PATH];
	FILE *f = path[0] ? fopen(path, "rb") : NULL;
	if (!f) {
		HMODULE shell = LoadLibraryA("shell32.dll");
		HRESULT (WINAPI *folder)(HWND, int, HANDLE, DWORD, LPSTR) = shell ? (HRESULT (WINAPI *)(HWND, int, HANDLE, DWORD, LPSTR))(void *)GetProcAddress(shell, "SHGetFolderPathA") : NULL;
		if (folder && folder(NULL, 0x8005, NULL, 0, path) >= 0) {   /* CSIDL_PERSONAL | CSIDL_FLAG_CREATE, as the plugin asks */
			strncat(path, "\\My Games\\Fallout4\\F4SE\\CMB_Slope.log", sizeof(path) - strlen(path) - 1);
			f = fopen(path, "rb");
		}
		if (!f) {   /* next to the DLL (where the plugin puts it when My Documents can't be had: this harness under Wine) */
			HMODULE dll = GetModuleHandleA("CMB_Slope.dll");
			if (dll && GetModuleFileNameA(dll, path, sizeof(path))) {
				char *dot = strrchr(path, '.');
				if (dot)
					strcpy(dot, ".log");
				f = fopen(path, "rb");
			}
		}
	}
	if (!f)
		printf("  (no CMB_Slope.log to read, in My Documents or next to the DLL)\n");
	return f;
}
static int LogLines(const char *text)
{
	static char line[4096];
	FILE *f = OpenLog();
	if (!f)
		return -1;
	int n = 0;
	while (fgets(line, sizeof(line), f))
		if (strstr(line, text))
			n++;
	fclose(f);
	return n;
}

/* A number the plugin logged, read back: the float right after the text, from the last line of
 * the log that has the text with a float after it (NAN when none does; review of test 38's
 * build: the arm's logged reach checked against the clips). */
static float LastLogNumber(const char *after)
{
	static char line[4096];
	FILE *f = OpenLog();
	if (!f)
		return NAN;
	float value = NAN;
	size_t len = strlen(after);
	while (fgets(line, sizeof(line), f))
		for (const char *at = strstr(line, after); at; at = strstr(at + 1, after)) {
			char *end;
			float v = strtof(at + len, &end);
			if (end != at + len) {
				value = v;
				break;
			}
		}
	fclose(f);
	return value;
}

/* The "leaned" lines after the log's last line holding marker: how far into the ride the first
 * was solved ("...; N s into the ride"), how many there are and how many of them say final. */
static float LeanedSince(const char *marker, int *count, int *finals)
{
	static char line[4096];
	FILE *f = OpenLog();
	*count = *finals = 0;
	if (!f)
		return NAN;
	float first = NAN;
	while (fgets(line, sizeof(line), f)) {
		if (strstr(line, marker)) {
			first = NAN;
			*count = *finals = 0;
			continue;
		}
		const char *at = strstr(line, " s into the ride");
		if (!strstr(line, "the upper body leaned ") || !at)
			continue;
		const char *s = at;
		while (s > line && s[-1] != ' ')
			s--;
		if (!*count)
			first = strtof(s, NULL);
		(*count)++;
		if (strstr(at, "s into the ride, final"))
			(*finals)++;
	}
	fclose(f);
	return first;
}

/* The same through a bare world transform (a bone with no node, test 34). */
static void MapBoneAt(const uint8_t *xf, const uint8_t *orig, const uint8_t *copy, const float X[3], float out[3])
{
	float N[9], A[9], B[9], v[3], u[3], p[3], q[3], Bp[3], Nq[3];
	LoadRotation((const float *)xf, N, g_rootTransposed);
	LoadRotation((const float *)(orig + 0x10), A, g_skinTransposed);
	LoadRotation((const float *)(copy + 0x10), B, g_skinTransposed);
	const float *n = (const float *)(xf + 0x30), *a = (const float *)(orig + 0x40), *b = (const float *)(copy + 0x40);
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

/* The angle, degrees, between the solved elbow's offset from the shoulder-to-wrist line (the
 * bones' maps of the three joints, after the tilt) and a direction projected across that line
 * (test 38's ArmPole, or the clips' own plane, tilted alike); *off the offset's length. */
static float ElbowPlaneOff(const float mS[3], const float mE[3], const float mW[3], const float dir[3], float *off)
{
	float u[3], n[3], d[3], eu = 0.0f, du = 0.0f, lu, ln, ld, c;
	for (int i = 0; i < 3; i++)
		u[i] = mW[i] - mS[i];
	lu = sqrtf(u[0] * u[0] + u[1] * u[1] + u[2] * u[2]);
	for (int i = 0; i < 3; i++) {
		u[i] /= lu;
		eu += (mE[i] - mS[i]) * u[i];
		du += dir[i] * u[i];
	}
	for (int i = 0; i < 3; i++) {
		n[i] = mE[i] - mS[i] - eu * u[i];
		d[i] = dir[i] - du * u[i];
	}
	ln = sqrtf(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
	ld = sqrtf(d[0] * d[0] + d[1] * d[1] + d[2] * d[2]);
	if (off)
		*off = ln;
	if (ln < 1e-4f || ld < 1e-4f)
		return 180.0f;
	c = (n[0] * d[0] + n[1] * d[1] + n[2] * d[2]) / (ln * ld);
	return acosf(c > 1.0f ? 1.0f : c < -1.0f ? -1.0f : c) * DEG;
}

/* The bars' turn as the plugin builds it (test 29): about the steering axis through the
 * steering point (run.sh's SteerAxis and SteerPoint), both taken to world through the bike's
 * bind A and the COM bone N (loaded here too), by barNow degrees: x -> Q x + q. */
static void BarTurnMap(float barNow, float A[9], float N[9], float Q[9], float q[3])
{
	static const float steerAxis[3] = { 0, -0.4f, 0.9165f }, steerPoint[3] = { 0, 87.6f, 51.4f };
	float len = sqrtf(steerAxis[1] * steerAxis[1] + steerAxis[2] * steerAxis[2]);
	float axisB[3] = { 0, steerAxis[1] / len, steerAxis[2] / len }, Aa[3], axisW[3], Ap[3], Bp[3], NBp[3], qW[3], Qq[3];
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
}

/* The left grip's centre in world before the bars' turn, as the plugin builds it from the
 * parts' Grip (run.sh's, the +x grip's; the left is x mirrored) through the bind and the bone:
 * 6 units from the hand's node along the fingers, as the clips place the hand (test 38). */
static void GripWorld(float G[3])
{
	static const float grip[3] = { -56.45f, 79.79f, 54.85f };
	float A[9], N[9], AG[3], BG[3], NBG[3];
	LoadRotation((const float *)(g_bonesOriginal + 0x10), A, g_skinTransposed);
	LoadRotation((const float *)(g_comNode + 0x70), N, g_rootTransposed);
	Apply3(A, grip, AG);
	for (int i = 0; i < 3; i++)
		BG[i] = AG[i] + ((const float *)(g_bonesOriginal + 0x40))[i];
	Apply3(N, BG, NBG);
	for (int i = 0; i < 3; i++)
		G[i] = NBG[i] + ((const float *)(g_comNode + 0xA0))[i];
}

/* How far a bone's map puts the point X from the bars' turn of it, then the tilt. */
static float TurnedOff(const float X[3], const float mX[3], const float Q[9], const float q[3], const float Rw[9], const float Pw[3])
{
	float QX[3], e[3], Re[3];
	Apply3(Q, X, QX);
	for (int i = 0; i < 3; i++)
		e[i] = QX[i] + q[i] - Pw[i];
	Apply3(Rw, e, Re);
	for (int i = 0; i < 3; i++)
		Re[i] += Pw[i];
	return Dist3(mX, Re);
}

/* The angle about the unit axis g, degrees, from a's direction to b's, both seen along g
 * (projected on the plane normal to it): the plugin's measure for the wrist roll (test 39). */
static float AngleAboutDeg(const float a[3], const float b[3], const float g[3])
{
	float da = a[0] * g[0] + a[1] * g[1] + a[2] * g[2], db = b[0] * g[0] + b[1] * g[1] + b[2] * g[2], pa[3], pb[3], c[3];
	for (int i = 0; i < 3; i++) {
		pa[i] = a[i] - da * g[i];
		pb[i] = b[i] - db * g[i];
	}
	c[0] = pa[1] * pb[2] - pa[2] * pb[1];
	c[1] = pa[2] * pb[0] - pa[0] * pb[2];
	c[2] = pa[0] * pb[1] - pa[1] * pb[0];
	return atan2f(c[0] * g[0] + c[1] * g[1] + c[2] * g[2], pa[0] * pb[0] + pa[1] * pb[1] + pa[2] * pb[2]) * DEG;
}

/* The hand's long axis against the solved forearm, seen along the grip's axis (test 39): the
 * angle about the bike's +x (through the bind and the bone, then the bars' turn Q) from the
 * forearm's line to the hand's long axis, degrees, + = the hand above it, the knuckles up, on
 * either hand. The hand's long axis: the plugin's (g_handAxisLocal) through the hand's node,
 * then the hand's map before the tilt, Mh; the forearm: its bone's map of the elbow and the
 * clips' wrist, mE and mW (after the tilt: Rw undone). *clips: the same for the clips' hand
 * turned with the bars alone. */
static float HandAboveForearm(int side, const float Mh[9], const float mE[3], const float mW[3], const float Rw[9], const float Q[9], float *clips)
{
	float A[9], N[9], Nh[9], ex[3] = { 1.0f, 0.0f, 0.0f }, Ae[3], xb[3], x[3], hw[3], hm[3], hq[3], d[3], f[3], lx;
	LoadRotation((const float *)(g_bonesOriginal + 0x10), A, g_skinTransposed);
	LoadRotation((const float *)(g_comNode + 0x70), N, g_rootTransposed);
	LoadRotation((const float *)(g_bodyNodes[5] + 0x70), Nh, g_rootTransposed);
	Apply3(A, ex, Ae);
	Apply3(N, Ae, xb);
	Apply3(Q, xb, x);
	lx = sqrtf(x[0] * x[0] + x[1] * x[1] + x[2] * x[2]);
	for (int i = 0; i < 3; i++)
		x[i] /= lx;
	Apply3(Nh, g_handAxisLocal[side], hw);
	Apply3(Mh, hw, hm);
	Apply3(Q, hw, hq);
	for (int i = 0; i < 3; i++)
		d[i] = mW[i] - mE[i];
	for (int i = 0; i < 3; i++)
		f[i] = Rw[i] * d[0] + Rw[3 + i] * d[1] + Rw[6 + i] * d[2];   /* Rw^T d */
	if (clips)
		*clips = AngleAboutDeg(f, hq, x);
	return AngleAboutDeg(f, hm, x);
}

/* The clips' own bend plane: the elbow's offset from the shoulder-to-wrist line as the clips
 * pose the arm (the plugin keeps it with ArmPole=0,0,0, carried by the upper body's map). */
static void ClipsElbowOffset(const float S[3], const float E[3], const float W[3], float n0[3])
{
	float w0[3], v1[3], lw2 = 0.0f, k = 0.0f;
	for (int i = 0; i < 3; i++) {
		w0[i] = W[i] - S[i];
		v1[i] = E[i] - S[i];
		lw2 += w0[i] * w0[i];
	}
	for (int i = 0; i < 3; i++)
		k += v1[i] * w0[i] / lw2;
	for (int i = 0; i < 3; i++)
		n0[i] = v1[i] - k * w0[i];
}

/* Test 41: the pole the plugin should bend an arm toward, in the bike's space as it uses it
 * (the left's x mirrored): ArmPole, and for the inside arm (the left with the bars over to the
 * left, +; the right with them to the right) faded toward ArmPoleTurn by k = |bars| / turnBars,
 * 1 at most, both normalised first. Returns k. */
static float ExpectedPole(int side, float bars, const float pole[3], const float turn[3], float turnBars, float out[3])
{
	float la = sqrtf(pole[0] * pole[0] + pole[1] * pole[1] + pole[2] * pole[2]), lt = sqrtf(turn[0] * turn[0] + turn[1] * turn[1] + turn[2] * turn[2]), k = 0.0f;
	bool inside = side ? bars < 0.0f : bars > 0.0f;
	if (inside && la > 0.001f && lt > 0.001f && turnBars > 0.0f) {
		k = fabsf(bars) / turnBars;
		k = k > 1.0f ? 1.0f : k;
	}
	for (int i = 0; i < 3; i++)
		out[i] = k > 0.0f ? (1.0f - k) * pole[i] / la + k * turn[i] / lt : pole[i];
	if (!side)
		out[0] = -out[0];
	return k;
}

/* The fake's arm (the left, or the mirrored right with g_armRight) as the plugin wrote it: the
 * joints' maps (after the tilt), and the figures the plugin's arm lines give (test 41) read off
 * them in the bike's space (the tilt undone, then the COM bone and the bind): the elbow from the
 * shoulder (out on the arm's own side, forward, below), the upper arm below level, the forearm's
 * pitch to the wrist seen from the side (+ rising). */
typedef struct { float mS[3], mE1[3], mE2[3], mW2[3], mW3[3], fig[5]; } ArmNow;
static void ExpectedTilt(float Rw[9], float Pw[3]);
static void ReadArmNow(ArmNow *a)
{
	const uint8_t *copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
	float S[3], E[3], Wr[3], Rw[9], Pw[3], A[9], N[9], d[2][3], b[3], n[3], v[2][3];
	memcpy(S, g_bodyNodes[6] + 0xA0, 12);
	memcpy(E, g_bodyNodes[7] + 0xA0, 12);
	memcpy(Wr, g_bodyNodes[5] + 0xA0, 12);
	MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, S, a->mS);
	MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, E, a->mE1);
	MapBone(g_bodyNodes[7], g_bodyBonesOriginal + 7 * 0x50, copyNow + 7 * 0x50, E, a->mE2);
	MapBone(g_bodyNodes[7], g_bodyBonesOriginal + 7 * 0x50, copyNow + 7 * 0x50, Wr, a->mW2);
	MapBone(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, Wr, a->mW3);
	ExpectedTilt(Rw, Pw);
	LoadRotation((const float *)(g_bonesOriginal + 0x10), A, g_skinTransposed);
	LoadRotation((const float *)(g_comNode + 0x70), N, g_rootTransposed);
	for (int i = 0; i < 3; i++) {
		d[0][i] = a->mE1[i] - a->mS[i];
		d[1][i] = a->mW2[i] - a->mE2[i];
	}
	for (int k = 0; k < 2; k++) {
		for (int i = 0; i < 3; i++)
			b[i] = Rw[i] * d[k][0] + Rw[3 + i] * d[k][1] + Rw[6 + i] * d[k][2];   /* Rw^T: the tilt undone */
		for (int i = 0; i < 3; i++)
			n[i] = N[i] * b[0] + N[3 + i] * b[1] + N[6 + i] * b[2];
		for (int i = 0; i < 3; i++)
			v[k][i] = A[i] * n[0] + A[3 + i] * n[1] + A[6 + i] * n[2];
	}
	float lu = sqrtf(v[0][0] * v[0][0] + v[0][1] * v[0][1] + v[0][2] * v[0][2]);
	a->fig[0] = g_armRight ? v[0][0] : -v[0][0];
	a->fig[1] = v[0][1];
	a->fig[2] = -v[0][2];
	a->fig[3] = asinf(-v[0][2] / lu) * DEG;
	a->fig[4] = atan2f(v[1][2], v[1][1]) * DEG;
}

/* The written elbow's angle off a pole given in the bike's space as the plugin uses it (taken
 * to world through the bind and the COM bone, then tilted like the rest); *off the elbow's
 * offset from the shoulder-to-wrist line. */
static float ArmPlaneOff(const ArmNow *a, const float poleBike[3], float *off)
{
	float A[9], N[9], Rw[9], Pw[3], Ap[3], Np[3], poleT[3];
	LoadRotation((const float *)(g_bonesOriginal + 0x10), A, g_skinTransposed);
	LoadRotation((const float *)(g_comNode + 0x70), N, g_rootTransposed);
	ExpectedTilt(Rw, Pw);
	Apply3(A, poleBike, Ap);
	Apply3(N, Ap, Np);
	Apply3(Rw, Np, poleT);
	return ElbowPlaneOff(a->mS, a->mE2, a->mW3, poleT, off);
}

/* The last log line holding text, in a static buffer (NULL when none). */
static const char *LastLogLine(const char *text)
{
	static char line[4096], found[4096];
	FILE *f = OpenLog();
	bool any = false;
	if (!f)
		return NULL;
	while (fgets(line, sizeof(line), f))
		if (strstr(line, text)) {
			memcpy(found, line, sizeof(found));
			any = true;
		}
	fclose(f);
	return any ? found : NULL;
}

/* An arm line's figures (test 41), read after "from" in the last log line holding marker: the
 * elbow's out, forward and below, the upper arm below level, the forearm's pitch, and the pole;
 * *fade how far it says the pole was faded (0 when it doesn't say). */
static bool LoggedArmFigures(const char *marker, const char *from, float fig[5], float pole[3], float *fade)
{
	const char *line = LastLogLine(marker), *at = line ? strstr(line, from) : NULL;
	*fade = 0.0f;
	for (at = at ? strstr(at, "the elbow ") : NULL; at; at = strstr(at + 1, "the elbow "))   /* past "the elbow moved" */
		if (sscanf(at, "the elbow %f out, %f forward, %f below the shoulder (the upper arm %f deg below level), the forearm %f deg", &fig[0], &fig[1], &fig[2], &fig[3], &fig[4]) == 5)
			break;
	if (!at)
		return false;
	const char *p = strstr(at, "the pole (");
	if (!p || sscanf(p, "the pole (%f, %f, %f)", &pole[0], &pole[1], &pole[2]) != 3)
		return false;
	const char *close = strchr(p, ')');
	float k;
	int used = 0;
	if (close && sscanf(close, "), %f of the way to ArmPoleTurn%n", &k, &used) == 1 && used > 0)
		*fade = k;
	return true;
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

/* The game's bike rolling on backwards under its momentum once the back key is let go (the
 * keys still read, a creep's forward drive and all): in test 38 the plugin's smoothed speed
 * read backward for a third of a second into the creep, which this fake's instant stop never
 * showed. Momentum, since the fake's movement has none: its velocity along the heading,
 * g_momentumV (set to the backing speed as the key goes), follows the velocity the movement
 * itself gives this frame (the creep's drive, wound up against the shortfall as it is) over
 * g_momentumTau, and the player is moved by the difference. It takes over from the plugin's
 * own push (the reverse by steps, SetPosition here), which goes on for the 0.1 s the back
 * key's read is held: a roll on top of that push read 160 a second, over CreepBelow, and the
 * mode went to the pass-through instead of the creep; and a roll added to the creep's drive
 * was outrun by the drive's wind-up within a quarter second, too soon for the old flip to
 * show more than a few degrees. */
static float g_momentumV, g_momentumTau;
static int g_momentumPushes;   /* g_setPositions as of the last frame */
static void BackingMomentum(float dt)
{
	float p0[2] = { PlayerPos()[0], PlayerPos()[1] };
	FakeGameFrame(dt);
	if (g_setPositions != g_momentumPushes) {   /* the plugin pushed since the last frame: its push is the motion */
		g_momentumPushes = g_setPositions;
		return;
	}
	if (!(dt > 0.0f) || !(g_momentumTau > 0.0f))
		return;
	float h = *(float *)(g_player + 0xC8), sh = sinf(h), ch = cosf(h);
	float demand = ((PlayerPos()[0] - p0[0]) * sh + (PlayerPos()[1] - p0[1]) * ch) / dt;
	g_momentumV += (demand - g_momentumV) * (1.0f - expf(-dt / g_momentumTau));
	PlayerPos()[0] += sh * (g_momentumV - demand) * dt;
	PlayerPos()[1] += ch * (g_momentumV - demand) * dt;
}

/* The game's frame, with the most the player's z fell in one frame (from this call to the next:
 * the plugin's task between them steps the reverse) since g_zDropMax was cleared and g_zLast
 * set (the reverse's steps closing a gap under the feet: 3 a frame at most). */
static float g_zDropMax, g_zLast;
static void WatchDrops(float dt)
{
	float z = PlayerPos()[2];
	if (g_zLast - z > g_zDropMax)
		g_zDropMax = g_zLast - z;
	g_zLast = z;
	FakeGameFrame(dt);
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
	CHECK(*(int32_t *)(g_partData[0] + 0x08) == 3 && *(int32_t *)(g_partData[1] + 0x08) == 3 && *(int32_t *)(g_partData[2] + 0x08) == 3 && *(int32_t *)(g_partData[3] + 0x08) == 3,
	      "the four parts' skins are held (references %d %d %d %d)", *(int32_t *)(g_partData[0] + 0x08), *(int32_t *)(g_partData[1] + 0x08), *(int32_t *)(g_partData[2] + 0x08), *(int32_t *)(g_partData[3] + 0x08));
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
	AppliedRotationOf(g_partBonesOriginal[3], g_partBones[3], M);
	CHECK(IsIdentity(M) && fabsf(atan2f(M[7], M[4])) < 0.01f, "the lower fork (named _fork; test 38) not spun with the wheels, the bars straight (%.3f rad about the axle)", atan2f(M[7], M[4]));
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
	AppliedRotationOf(g_partBonesOriginal[3], g_partBones[3], M);
	AppliedRotationOf(g_partBonesOriginal[2], g_partBones[2], N);
	for (int i = 0; i < 3; i++)   /* D = M N^T: the fork's rotation over the bar assembly's */
		for (int j = 0; j < 3; j++)
			D[i * 3 + j] = M[i * 3] * N[j * 3] + M[i * 3 + 1] * N[j * 3 + 1] + M[i * 3 + 2] * N[j * 3 + 2];
	float forkAxis[3], forkOver = RotationAngle(D, forkAxis);
	CHECK(fabsf(TurnAbout(M) - bar) < 1.0f && forkOver < 0.5f, "the lower fork turned with the bars (%.1f deg), no spin: its rotation is the bar assembly's (%.2f deg between them)", TurnAbout(M), forkOver);
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
	if (g_haveParts)
		CHECK(BarAngle() < -5.0f, "and the bars to the right, the key's way, though the nose swings left (%.1f deg; test 38: they followed the nose)", BarAngle());
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

	/* Review of test 38's build: with the back key let go and a side key still held, the creep
	 * turns the heading the key's way while the smoothed speed still reads backward for a
	 * third of a second (the game's bike rolls on under its momentum: BackingMomentum here,
	 * once the plugin's own push has stopped), and the bars' flip on that speed (g_speedAlong
	 * < -10) swung them full lock the other way for about 0.4 s before they came back. The flip
	 * is on the back mode alone now: sampled every 50 ms, the bars stay the key's way (or pass
	 * through zero toward it), never the opposite sign beyond 3 deg, and the mode goes to the
	 * creep. */
	printf("input hook: the back key let go of with the side key still held, the bike rolling on backwards for a moment (review of test 38's build: the bars flipped on the smoothed speed, full lock the other way for a third of a second): the bars stay the key's way, the mode goes to the creep:\n");
	for (int side = 0; side < 2; side++) {
		float key = side ? -1.0f : 1.0f;   /* right, then left */
		Keys(key, -1.0f);
		RunFrames(1000);
		float barBacking = BarAngle(), worst = 0.0f, barAt[14];
		int creepBefore = LogLines(" | creep");
		from = *head;
		Mark(p0);
		Keys(key, 0.0f);
		g_momentumV = -80.0f;   /* backing at 80, the momentum following the creep's drive over half a second: the smoothed speed reads backward for the game's third of a second */
		g_momentumTau = 0.5f;
		g_momentumPushes = g_setPositions;
		g_onFrame = BackingMomentum;
		for (int i = 0; i < 14; i++) {
			RunFrames(50);
			barAt[i] = BarAngle();
			float against = key * barAt[i];   /* the right key's bars are negative (the left's positive): positive here is against the key */
			if (i < 10 && against > worst)
				worst = against;
		}
		g_onFrame = FakeGameFrame;
		if (g_haveParts)
			CHECK(key * barBacking < -5.0f && worst < 3.0f && key * barAt[13] < -5.0f,
			      "%s let go of, %s held: the bars from %.1f deg backing, at most %.1f deg against the key in the first half second (under 3: the key's way, or through zero toward it), %.1f at 0.7 s, the key's way again",
			      "back", side ? "left" : "right", barBacking, worst, barAt[13]);
		CHECK(LogLines(" | creep") > creepBefore && key * Turned(from) > 5.0f && g_momentumV > 0.0f,
		      "and the mode went to the creep (%d trace line%s say so): the nose %.0f deg the key's way, %.0f from where the key was let go of in the 0.7 s (the fake's momentum spent: %+.0f a second along the heading)",
		      LogLines(" | creep") - creepBefore, LogLines(" | creep") - creepBefore == 1 ? "" : "s", key * Turned(from), Moved(p0), g_momentumV);
		Keys(0.0f, 0.0f);
		RunFrames(500);
	}

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

	printf("input hook: a face 700 ahead, W held: the throttle eased off, the bike stops short of it (FaceLook 0.3):\n");
	{
		float fwd2[2] = { sinf(from), cosf(from) };
		Mark(p0);
		FakePlane *face = &g_planes[0];
		face->point[0] = p0[0] + fwd2[0] * 700.0f;
		face->point[1] = p0[1] + fwd2[1] * 700.0f;
		face->normal[0] = -fwd2[0];
		face->normal[1] = -fwd2[1];
		face->layer = 1;
		face->on = true;
		Keys(0.0f, 1.0f);
		RunFrames(6000);
		float left = (face->point[0] - PlayerPos()[0]) * fwd2[0] + (face->point[1] - PlayerPos()[1]) * fwd2[1];
		CHECK(Moved(p0) > 300.0f && left > 100.0f && left < 220.0f, "rides %.0f and stops with the front wheel short of the face (%.0f from the rider to the face; the wheel's front is 130 ahead)", Moved(p0), left);
		Keys(0.0f, 0.0f);
		RunFrames(300);
		face->on = false;

		printf("input hook: an obstacle 700 ahead, 40 high (under 1.5 wheel radii), W held: ridden over at the held throttle (ObstacleThrottle 0.55):\n");
		Mark(p0);
		face->point[0] = p0[0] + fwd2[0] * 700.0f;
		face->point[1] = p0[1] + fwd2[1] * 700.0f;
		face->top = 40.0f;
		face->on = true;
		Keys(0.0f, 1.0f);
		RunFrames(4000);
		left = (face->point[0] - PlayerPos()[0]) * fwd2[0] + (face->point[1] - PlayerPos()[1]) * fwd2[1];
		CHECK(Moved(p0) > 700.0f && left < 0.0f, "rides on over it: %.0f in 4 s, the obstacle %.0f behind", Moved(p0), -left);
		Keys(0.0f, 0.0f);
		RunFrames(300);
		face->on = false;
		face->top = 0.0f;

		/* Test 35's verdicts with state. First a reference: full throttle for 2 s from a stop. */
		RunFrames(2500);   /* rolled off, at rest */
		Mark(p0);
		Keys(0.0f, 1.0f);
		RunFrames(2000);
		float fullRun = Moved(p0);
		Keys(0.0f, 0.0f);
		RunFrames(2500);
		float groundZ0 = g_groundZ;
		printf("input hook: a face between the rider and the front wheel's edge, the ground 40 up under the wheels (the bike on top of a thing it climbed; test 35), W held: an obstacle, not a wall:\n");
		Mark(p0);
		g_groundZ = groundZ0 + 40.0f;   /* the wheel rays find the ground 40 above the capsule's contact: the front wheel is on the thing */
		face->follow = 60.0f;   /* 60 ahead of the rider wherever they go: 70 behind the front wheel's edge, at any height */
		face->on = true;
		Keys(0.0f, 1.0f);
		RunFrames(2000);
		CHECK(fabsf(Moved(p0) - 0.55f * fullRun) <= 0.15f * fullRun, "rolls on at the obstacle's throttle: %.0f in 2 s (0.55 of %.0f at full throttle, within 15%%; a wall at the wheel would have held it)", Moved(p0), fullRun);
		printf("input hook: the same face with the ground flat under the wheels (a wall the bike has nosed or turned into, its front wheel through it; review): an obstacle for the hold's second, then a wall, the throttle cut:\n");
		g_groundZ = groundZ0;
		Mark(p0);
		RunFrames(1500);   /* the hold lapses after a second (an obstacle for now doesn't renew it) */
		float onTheHold = Moved(p0);
		Mark(p0);
		RunFrames(1000);
		CHECK(onTheHold > 60.0f && Moved(p0) < 30.0f && MoveInput()[1] == 0.0f, "rolled %.0f on the hold's second, then stands: %.0f in the next second, no forward input (%.3f)", onTheHold, Moved(p0), MoveInput()[1]);
		printf("input hook: the hold in force (the face under the bike on the step), then a wall fixed 125 ahead of the rider (its hit 4.5 behind the wheel's edge: the edge itself, neither under the bike nor ahead of the wheel), the bike held by the game's collision: an obstacle for now, a wall once the hold has lapsed (ObstacleHold 1):\n");
		g_groundZ = groundZ0 + 40.0f;
		RunFrames(600);   /* obstacle verdicts again: the hold in force */
		g_frozen = true;   /* against the wall: the bike can't move */
		g_groundZ = groundZ0;
		face->follow = 0.0f;
		face->point[0] = PlayerPos()[0] + fwd2[0] * 125.0f;
		face->point[1] = PlayerPos()[1] + fwd2[1] * 125.0f;
		face->normal[0] = -fwd2[0];
		face->normal[1] = -fwd2[1];
		RunFrames(500);
		float forNow = MoveInput()[1];
		RunFrames(800);
		CHECK(forNow > 0.02f && MoveInput()[1] == 0.0f, "half a second in still the obstacle's share (forward input %.2f), 1.3 s in a wall and no forward input (%.3f): the obstacle for now didn't renew the hold", forNow, MoveInput()[1]);
		printf("input hook: the hold in force, then a wall fixed 145 ahead of the rider (15 ahead of the wheel's edge), the bike rolling: a wall after WallFrames (5) frames of it, the bike stops at once:\n");
		g_frozen = false;
		g_groundZ = groundZ0 + 40.0f;
		face->follow = 60.0f;
		RunFrames(600);   /* rolling at the obstacle's share, the hold in force */
		g_groundZ = groundZ0;
		face->follow = 0.0f;
		face->point[0] = PlayerPos()[0] + fwd2[0] * 145.0f;   /* 15 ahead of the edge: five frames' travel at the share's speed with a margin (test 36's 5 wasn't one when a frame ran long: the hit fell behind the edge before the fifth frame, and the bike rolled through as an obstacle for now) */
		face->point[1] = PlayerPos()[1] + fwd2[1] * 145.0f;
		Mark(p0);
		RunFrames(500);
		CHECK(Moved(p0) < 50.0f, "stops within the half second (%.0f; the obstacle's share would have made 100 and more): a wall ahead of the wheel counts after 5 frames running", Moved(p0));
		printf("input hook: a wall fixed 120 ahead of the rider (9.5 behind the wheel's edge, within half a radius), the ground 40 up, the bike held: a wall still, the hit at the edge, not under the bike:\n");
		Keys(0.0f, 0.0f);
		face->on = false;
		RunFrames(1500);   /* at rest, the hold long lapsed */
		g_groundZ = groundZ0 + 40.0f;
		g_frozen = true;
		face->point[0] = PlayerPos()[0] + fwd2[0] * 120.0f;
		face->point[1] = PlayerPos()[1] + fwd2[1] * 120.0f;
		face->on = true;
		Keys(0.0f, 1.0f);
		RunFrames(600);
		CHECK(MoveInput()[1] == 0.0f, "no forward input (%.3f): a hit 9.5 behind the wheel's edge is a wall at the wheel", MoveInput()[1]);
		printf("input hook: the hold in force, then a load (PostLoadGame): the verdict's state starts afresh, a wall at the edge is a wall at once:\n");
		g_frozen = false;
		face->follow = 60.0f;
		RunFrames(600);   /* on the step, the hold in force */
		Send(3, 1);   /* PostLoadGame: a new ride's state */
		g_frozen = true;
		g_groundZ = groundZ0;
		face->follow = 0.0f;
		face->point[0] = PlayerPos()[0] + fwd2[0] * 125.0f;
		face->point[1] = PlayerPos()[1] + fwd2[1] * 125.0f;
		RunFrames(400);
		CHECK(MoveInput()[1] == 0.0f, "no forward input 0.4 s after the load (%.3f): no hold carried over", MoveInput()[1]);
		Keys(0.0f, 0.0f);
		g_frozen = false;
		face->on = false;
		g_camYaw = *head;
		RunFrames(1500);
		printf("input hook: the front wheel's down-ray reads a face taller than the wheel climbs (a shelf 140 above the feet over the front axle), a rail at axle height 60 ahead: the throttle cut (WallAhead):\n");
		Mark(p0);
		g_shelfOn = true;
		g_shelfHeight = 140.0f;   /* over the rise the ray accepts: 99.6 x 1.1918 + 10 = 128.7 */
		g_shelfAhead = 99.6f;
		FakePlane *rail = &g_planes[1];
		rail->follow = 60.0f;
		rail->bottom = 20.0f;   /* from 20 to 35 above the ground: the axle-height ray hits it, the ones at half a radius and 1.5 radii don't (no obstacle verdict) */
		rail->top = 35.0f;
		rail->layer = 1;
		rail->on = true;
		int thrownBefore = LogLines("thrown away"), rearNamedBefore = LogLines("; the rear wheel's ray hit FakeGround (layer 13)");
		Keys(0.0f, 1.0f);
		RunFrames(2000);
		CHECK(Moved(p0) < 100.0f, "the bike stands: %.0f in 2 s (no obstacle in force)", Moved(p0));
		/* Review of test 38's build: both wheel rays are cast before either is judged, so the
		 * line about the front's hit thrown away (the shelf, 140 over the feet, above the ray's
		 * rise of 129) says what the rear's ray found in that very state: the ground. */
		int thrown = LogLines("thrown away") - thrownBefore, rearNamed = LogLines("; the rear wheel's ray hit FakeGround (layer 13)") - rearNamedBefore;
		CHECK(thrown >= 1 && rearNamed == thrown,
		      "the log: %d \"rays: the front wheel's ray hit ... thrown away\" line%s in the 2 s (one a second), each naming the rear wheel's ray's hit on the ground in the same state (%d; review: both rays cast before either is judged)",
		      thrown, thrown == 1 ? "" : "s", rearNamed);
		printf("input hook: the same with an obstacle lower than 1.5 radii 200 ahead of the rider as well (70 ahead of the wheel's edge, past the down-ray's own forward ray: the face rays' verdict, in force): the throttle held to the obstacle's share:\n");
		rail->on = false;
		face->follow = 200.0f;
		face->top = 40.0f;   /* the axle-height ray hits it, the one at 1.5 radii passes over: an obstacle by height, wherever it is */
		face->on = true;
		Mark(p0);
		RunFrames(2000);
		CHECK(fabsf(Moved(p0) - 0.55f * fullRun) <= 0.15f * fullRun, "rolls on at the obstacle's throttle: %.0f in 2 s (0.55 of %.0f at full throttle, within 15%%)", Moved(p0), fullRun);
		/* Test 37: 16 of 39 holds had the hit at or behind the wheel's edge, the ground under
		 * the pitched bike. Such a verdict sets the hold (the shelf's cut still deferred to it)
		 * but leaves the throttle free. */
		printf("input hook: the same obstacle 60 ahead of the rider (70 behind the wheel's edge: the bike is on it; test 37), the shelf's down-ray face still deferring to the hold: the throttle free:\n");
		face->follow = 60.0f;
		Mark(p0);
		RunFrames(2000);
		CHECK(Moved(p0) > 0.85f * fullRun, "rolls on at full throttle: %.0f in 2 s (%.0f at full throttle; the share would have made %.0f)", Moved(p0), fullRun, 0.55f * fullRun);
		Keys(0.0f, 0.0f);
		RunFrames(300);
		face->on = false;
		face->follow = face->top = 0.0f;
		rail->follow = rail->bottom = rail->top = 0.0f;
		g_shelfOn = false;
		g_groundZ = groundZ0;
		RunFrames(2500);   /* rolled off, at rest */

		/* Test 37: ten of 39 holds were faces of 45 to 49 degrees, which the controller climbs
		 * at 47. ObstacleAngle (50): a slanted plane, its foot 130 ahead of the rider wherever
		 * they go and rising away at the angle, which the rays read between the axle and 1.5
		 * radii as the angle itself (the hits 23 to 28 past the wheel's edge at axle height). */
		printf("input hook: a face of 47 deg ahead (a slanted plane, its foot 130 ahead of the rider; test 37), W held 2 s: under ObstacleAngle (50), no verdict, full throttle:\n");
		Mark(p0);
		face->follow = 130.0f;
		face->slant = 47.0f;
		face->on = true;
		Keys(0.0f, 1.0f);
		RunFrames(2000);
		CHECK(Moved(p0) > 0.85f * fullRun, "rides %.0f in 2 s (%.0f at full throttle)", Moved(p0), fullRun);
		Keys(0.0f, 0.0f);
		face->on = false;
		RunFrames(2500);   /* rolled off, at rest */
		printf("input hook: the same face at 52 deg: an obstacle (over ObstacleAngle, under WallAngle 55), the throttle held to 0.55:\n");
		Mark(p0);
		face->slant = 52.0f;
		face->on = true;
		Keys(0.0f, 1.0f);
		RunFrames(2000);
		CHECK(fabsf(Moved(p0) - 0.55f * fullRun) <= 0.15f * fullRun, "rides %.0f in 2 s (0.55 of %.0f at full throttle, within 15%%)", Moved(p0), fullRun);
		Keys(0.0f, 0.0f);
		face->on = false;
		RunFrames(2500);   /* rolled off, at rest */
		/* Test 38: the holds to 55% were mostly five low rock faces of 50 to 57 deg, "lower than
		 * 1.5 wheel radii" by the upper ray's reach rather than the thing's height (cast as far as
		 * the axle ray, on a 54 deg face its hit lay 11 further on, often past the ray's end). The
		 * upper ray now reaches the half radius' run at ObstacleAngle further (12.6 at 50 deg, and
		 * 2 over), and a lower-only face holds the throttle only from LowObstacleAngle (60). */
		printf("input hook: a low face of 52 deg, 40 tall (nothing at 1.5 radii, 44.9 up, however long the ray), its foot 150 ahead of the rider (test 38): under LowObstacleAngle (60), no verdict, full throttle:\n");
		Mark(p0);
		face->follow = 150.0f;
		face->slant = 52.0f;
		face->top = 40.0f;
		face->on = true;
		Keys(0.0f, 1.0f);
		RunFrames(2000);
		CHECK(Moved(p0) > 0.85f * fullRun, "rides %.0f in 2 s (%.0f at full throttle)", Moved(p0), fullRun);
		Keys(0.0f, 0.0f);
		face->on = false;
		RunFrames(2500);   /* rolled off, at rest */
		printf("input hook: the same low face at 65 deg: an obstacle lower than 1.5 wheel radii, the throttle held to 0.55:\n");
		Mark(p0);
		face->slant = 65.0f;
		face->on = true;
		Keys(0.0f, 1.0f);
		RunFrames(2000);
		CHECK(fabsf(Moved(p0) - 0.55f * fullRun) <= 0.15f * fullRun, "rides %.0f in 2 s (0.55 of %.0f at full throttle, within 15%%)", Moved(p0), fullRun);
		Keys(0.0f, 0.0f);
		face->on = false;
		RunFrames(2500);   /* rolled off, at rest */
		printf("input hook: a tall face of 52 deg (60 tall: the upper ray, reaching 14.6 past the axle ray's end, finds its hit 11.7 past the axle's): a face under WallAngle, an obstacle, the throttle held to 0.55:\n");
		Mark(p0);
		face->slant = 52.0f;
		face->top = 60.0f;
		face->on = true;
		Keys(0.0f, 1.0f);
		RunFrames(2000);
		CHECK(fabsf(Moved(p0) - 0.55f * fullRun) <= 0.15f * fullRun, "rides %.0f in 2 s (0.55 of %.0f at full throttle, within 15%%)", Moved(p0), fullRun);
		Keys(0.0f, 0.0f);
		face->on = false;
		face->slant = face->follow = face->top = 0.0f;
		RunFrames(2500);   /* rolled off, at rest */

		/* Test 36: the pick's filter 30 isn't the capsule's own, and things the capsule never
		 * meets (food bushes, layer 15; a fire truck's navcut shape, 49; Dogmeat, 8) read as
		 * walls. The rays stop only at what the character controller's collision layer record
		 * collides with (the fake's lists 36 layers; 4, 8, 15, 32 and 49 aren't among them), bar
		 * the phantoms (test 37: a trap trigger, 54, is in the list, and a tripwire would have
		 * presented as a wall). */
		static const uint32_t through[4] = { 15, 49, 8, 54 };
		static const char *throughWhat[4] = { "a food bush (layer 15, non-collidable)", "a fire truck's navcut shape (layer 49)", "a dog (layer 8, biped)", "a tripwire's trigger (layer 54, trap trigger)" };
		static const char *throughWhy[4] = { "not in the character controller's collides-with list (test 36)", "not in the list (test 36)", "not in the list (test 36)", "in the list, but a phantom (test 37)" };
		for (int i = 0; i < 4; i++) {
			printf("input hook: %s 400 ahead, W held 2 s: %s, ridden through at full throttle:\n", throughWhat[i], throughWhy[i]);
			Mark(p0);
			face->point[0] = p0[0] + fwd2[0] * 400.0f;
			face->point[1] = p0[1] + fwd2[1] * 400.0f;
			face->normal[0] = -fwd2[0];
			face->normal[1] = -fwd2[1];
			face->layer = through[i];
			face->on = true;
			Keys(0.0f, 1.0f);
			RunFrames(2000);
			left = (face->point[0] - PlayerPos()[0]) * fwd2[0] + (face->point[1] - PlayerPos()[1]) * fwd2[1];
			CHECK(Moved(p0) > 0.85f * fullRun && left < -100.0f, "rides %.0f in 2 s (%.0f at full throttle), the plane %.0f behind", Moved(p0), fullRun, -left);
			Keys(0.0f, 0.0f);
			face->on = false;
			RunFrames(2500);   /* rolled off, at rest */
		}
		printf("input hook: a hit on the rider's own 3D (the player's root, layer 30) 2 ahead of the player, where the face rays start (the capsule itself; test 36), W held 2 s: passed through, full throttle:\n");
		Mark(p0);
		face->follow = 2.0f;
		face->layer = 30;
		face->what = g_root;
		face->on = true;
		Keys(0.0f, 1.0f);
		RunFrames(2000);
		CHECK(Moved(p0) > 0.85f * fullRun, "rides %.0f in 2 s (%.0f at full throttle)", Moved(p0), fullRun);
		Keys(0.0f, 0.0f);
		face->on = false;
		RunFrames(2500);   /* rolled off, at rest */
		printf("input hook: the same hit on something else's 3D (layer 30, in the list): a wall at the wheel, the bike held:\n");
		Mark(p0);
		face->what = NULL;
		face->on = true;
		Keys(0.0f, 1.0f);
		RunFrames(600);
		CHECK(Moved(p0) < 40.0f && MoveInput()[1] == 0.0f, "stands: %.0f in 0.6 s, no forward input (%.3f)", Moved(p0), MoveInput()[1]);
		Keys(0.0f, 0.0f);
		face->on = false;
		RunFrames(300);
		/* Test 39's radstag: the ground's rays pass through actors now (the wheels' rays read
		 * the ground under it, the tilt's tests check the pitch); the face rays don't, so one
		 * ahead still stops the bike. */
		printf("input hook: an actor in front (test 39's radstag: its capsule's face 60 ahead of the rider, layer 30, \"SkeletonExport\", its top 100 above the feet over the front wheel's ray spot), W held: the face rays still see it, the bike held:\n");
		Mark(p0);
		face->follow = 60.0f;
		face->top = 100.0f;
		face->what = g_actorObj;
		face->on = true;
		g_shelfOn = true;
		g_shelfHeight = 100.0f;
		g_shelfAhead = 99.6f;
		g_shelfRadius = 40.0f;
		g_shelfLayer = 30;
		g_shelfWhat = g_actorObj;
		int facedBefore = LogLines("(SkeletonExport, layer 30), the throttle eased to");
		Keys(0.0f, 1.0f);
		RunFrames(1200);   /* the verdict's line comes a second after the last "rays:" line at most (the one saying the last face had gone) */
		CHECK(Moved(p0) < 40.0f && MoveInput()[1] == 0.0f && LogLines("(SkeletonExport, layer 30), the throttle eased to") > facedBefore,
		      "stands: %.0f in 1.2 s, no forward input (%.3f); a \"rays: a wall ahead\" line names SkeletonExport (layer 30), the throttle eased (%d new)",
		      Moved(p0), MoveInput()[1], LogLines("(SkeletonExport, layer 30), the throttle eased to") - facedBefore);
		Keys(0.0f, 0.0f);
		face->on = false;
		face->follow = face->top = 0.0f;
		face->what = NULL;
		face->layer = 1;
		g_shelfOn = false;
		g_shelfHeight = g_shelfAhead = 0.0f;
		g_shelfRadius = 60.0f;
		g_shelfLayer = 1;
		g_shelfWhat = NULL;
		RunFrames(300);
		printf("input hook: no COLL record to read (the form lookup finds none) and a load: the built-in table, a food bush (15) still ridden through, a tree (layer 9) a face the bike stops short of:\n");
		g_collHidden = true;
		Send(3, 1);   /* PostLoadGame: the rays' test ray again, the record read again with it */
		RunFrames(400);
		g_camYaw = *head;
		Mark(p0);
		face->point[0] = p0[0] + fwd2[0] * 400.0f;
		face->point[1] = p0[1] + fwd2[1] * 400.0f;
		face->layer = 15;
		face->on = true;
		Keys(0.0f, 1.0f);
		RunFrames(2000);
		left = (face->point[0] - PlayerPos()[0]) * fwd2[0] + (face->point[1] - PlayerPos()[1]) * fwd2[1];
		CHECK(Moved(p0) > 0.85f * fullRun && left < -100.0f, "the bush: rides %.0f in 2 s (%.0f at full throttle), the plane %.0f behind", Moved(p0), fullRun, -left);
		Keys(0.0f, 0.0f);
		face->on = false;
		RunFrames(2500);   /* rolled off, at rest */
		Mark(p0);
		face->point[0] = p0[0] + fwd2[0] * 700.0f;
		face->point[1] = p0[1] + fwd2[1] * 700.0f;
		face->layer = 9;
		face->on = true;
		Keys(0.0f, 1.0f);
		RunFrames(6000);
		left = (face->point[0] - PlayerPos()[0]) * fwd2[0] + (face->point[1] - PlayerPos()[1]) * fwd2[1];
		CHECK(Moved(p0) > 300.0f && left > 100.0f && left < 220.0f, "the tree: rides %.0f and stops with the front wheel short of it (%.0f from the rider)", Moved(p0), left);
		Keys(0.0f, 0.0f);
		RunFrames(300);
		face->on = false;
		face->layer = 1;
		g_collHidden = false;
		Send(3, 1);   /* the record back for what follows: read again at the next test ray */
		RunFrames(400);
		g_camYaw = *head;
		RunFrames(2000);   /* at rest */
	}

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

	/* Test 39, a level road (01:38:27-54, 01:39:27-42): every one of the 15 gaps the steps
	 * closed (+0.4 to +2.4, the step's dz -0.4 to -2.44) came with the controller holding
	 * itself supported (state 0, the supported bit), and each was followed by it in the air
	 * within 0.75 s, the player dropping 20 to 37 through the road. A supported controller's
	 * gap is its own now; an unsupported one's feet go down to 0.5 over the ground. */
	printf("input hook: backing on level ground with a gap of 1.5 under the feet at the step (a hole of radius 20 round the feet: the ground 55 behind and the wheels' contacts outside it), the controller holding itself supported (state 0, the supported bit; test 39): the step's dz 0, the feet stay:\n");
	FlatGround();
	g_shelfOn = true;
	g_shelfHeight = -1.5f;
	g_shelfAhead = 0.0f;
	g_shelfRadius = 20.0f;
	SetState(0);
	SetSupported(true);
	float z0 = PlayerPos()[2];
	Mark(p0);
	int raysBefore = LogLines("  rays (filter");
	Keys(0.0f, -1.0f);
	RunFrames(1000);
	float gapLogged = LastLogNumber("feet gap "), dzLogged = LastLogNumber("step dz ");
	CHECK(Moved(p0) > 40.0f && fabsf(PlayerPos()[2] - z0) < 0.05f, "backs up %.0f in a second, the feet %+.2f from where they were (the gap the controller's own)", Moved(p0), PlayerPos()[2] - z0);
	CHECK(LogLines("  rays (filter") > raysBefore && fabsf(gapLogged - 1.5f) < 0.15f && fabsf(dzLogged) < 0.005f,
	      "the trace's rays line still gives the gap and the step: feet gap %+.1f, step dz %+.2f (not -1.5)", gapLogged, dzLogged);
	Keys(0.0f, 0.0f);
	RunFrames(300);
	g_shelfOn = false;
	g_shelfHeight = 0.0f;
	g_shelfRadius = 60.0f;
	/* Test 41 (finding 6): the gap is closed over BackClose (0.1 s), 120 a second and 3 a step at
	 * most, down to the controller's own clearance (here the hover, 0.5: the push starts with it
	 * unsupported), no longer at once (test 40's rule: the 2.0 in one frame, then 3 a frame). */
	printf("input hook: the same with the supported bit clear and the ground 2.5 below the feet (a level plane), then 7.5 more: the feet go down to 0.5 over it, the gap closed over 0.1 s, 3 a frame at most:\n");
	SetSupported(false);
	g_groundZ = PlayerPos()[2] - 2.5f;
	g_zDropMax = 0.0f;
	g_zLast = PlayerPos()[2];
	g_onFrame = WatchDrops;
	Keys(0.0f, -1.0f);
	RunFrames(1000);
	float hover = PlayerPos()[2] - g_groundZ, dropped = g_zDropMax;
	CHECK(fabsf(hover - 0.5f) < 0.05f && dropped > 0.05f && dropped < 0.5f, "the feet %.2f over the ground after a second (0.5), %.2f the most in a frame (0.10 at 5 ms frames, 0.30 at 16; test 40's rule: the 2.0 at once)",
	      hover, dropped);
	g_groundZ = PlayerPos()[2] - 7.5f;
	g_zDropMax = 0.0f;
	g_zLast = PlayerPos()[2];
	RunFrames(1000);
	hover = PlayerPos()[2] - g_groundZ;
	CHECK(fabsf(hover - 0.5f) < 0.05f && g_zDropMax > 0.3f && g_zDropMax < 1.5f, "the feet %.2f over the ground after a second (0.5), %.2f the most in a frame (0.37 at 5 ms frames, 1.1 at 16, never over 3; test 40's rule: 3, the cap)",
	      hover, g_zDropMax);
	Keys(0.0f, 0.0f);
	g_onFrame = FakeGameFrame;
	RunFrames(300);
	FlatGround();

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
	CHECK(turnedBy > -12.0f && turnedBy < -1.0f && inside > -0.5f,   /* the corner lands on the car's face itself: a rounding's worth either side (one run in three read -0.0) */
	      "the rear swings right until its corner reaches the car (%.1f deg, %.1f units clear), not into it", turnedBy, inside);
	CHECK(Moved(p0) < 40.0f, "then it stops: angled at the car, straight back would hit it too (moved %.0f)", Moved(p0));
	Mark(p0);
	from = *head;
	Keys(-1.0f, -1.0f);
	RunFrames(700);
	float barBack = BarAngle();
	RunFrames(800);
	CHECK(Turned(from) > 20.0f && Moved(p0) > 60.0f, "back and left: the rear swings away from it (%.0f deg), backing up again (%.0f)",
	      Turned(from), Moved(p0));
	if (g_haveParts)
		CHECK(barBack > 5.0f, "and the bars to the left, the key's way, the nose swinging right (%.1f deg at 0.7 s; test 38)", barBack);
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
	*head = from;

	/* Test 39: the wheels' 30 "rays:" lines a ride were spent by 01:35:02, before the backing
	 * tests. A hand of 10 now, one more every 6 s, one a second at most, and a hand of its own
	 * while backing. A new ride on a 30 deg slope (the wheels' pitch 30, a line a second while
	 * the hand lasts): lines at 0 to 10 s (the 10 and the one refilled meanwhile) and at 12
	 * (the next refill: the hand spent); back held for 2 s from the sample that saw that 12th
	 * line, a line a second from the backing hand (at 13 and 14; the lines till 0.8 s after
	 * the key, the back mode outlasting it by a sample or two, count as backing); then the
	 * riding hand's next at 18. The times are the wall clock's, as the plugin's own clock goes
	 * (the log read between the samples counts in it too), at the end of the 0.2 s sample a
	 * line came in. */
	printf("input hook: the wheels' \"rays:\" lines from a hand of 10, one more every 6 s, one of its own while backing (test 39: the 30 a ride were spent before the backing tests): a new ride on a 30 deg slope, back held for 2 s once the riding hand is spent:\n");
	g_slopeK = tanf(30.0f / DEG);
	g_slopeO[0] = PlayerPos()[0];
	g_slopeO[1] = PlayerPos()[1];
	g_slopeD[0] = sinf(from);
	g_slopeD[1] = cosf(from);
	g_groundZ = PlayerPos()[2];
	int linesBase = LogLines("rays: the wheels' rays"), lines = 0;
	float lineAt[24], backFrom = -1.0f;
	bool lineBacking[24];
	LARGE_INTEGER qf, q0, q1;
	QueryPerformanceFrequency(&qf);
	QueryPerformanceCounter(&q0);
	SetLive(60.0f);
	for (float now = 0.0f; now < 18.8f; ) {   /* 18.8 s in samples of 0.2 s */
		Keys(0.0f, backFrom >= 0.0f && now < backFrom + 2.0f ? -1.0f : 0.0f);
		RunFrames(200);
		QueryPerformanceCounter(&q1);
		now = (float)(q1.QuadPart - q0.QuadPart) / (float)qf.QuadPart;
		int c = LogLines("rays: the wheels' rays") - linesBase;
		for (; lines < c && lines < 24; lines++) {
			lineAt[lines] = now;
			lineBacking[lines] = backFrom >= 0.0f && now < backFrom + 2.8f;
		}
		if (backFrom < 0.0f && lines >= 12)
			backFrom = now;
	}
	Keys(0.0f, 0.0f);
	int backLines = 0, firstAfter = -1;
	for (int k = 12; k < lines; k++) {
		if (lineBacking[k])
			backLines++;
		else if (firstAfter < 0)
			firstAfter = k;
	}
	float t0 = lines > 0 ? lineAt[0] : 0.0f;
	CHECK(lines >= 12 && lineAt[10] - t0 > 9.6f && lineAt[10] - t0 < 11.0f && lineAt[11] - lineAt[10] > 1.5f && lineAt[11] - lineAt[10] < 2.5f && backFrom - t0 < 12.8f,
	      "riding: the first 11 lines a second apart (the 11th %.1f s after the first), the 12th %.1f s after the 11th (2: the hand spent, the next refill at 12)",
	      lines > 10 ? lineAt[10] - t0 : -1.0f, lines > 11 ? lineAt[11] - lineAt[10] : -1.0f);
	CHECK(backLines == 2, "backing with the riding hand spent: %d line%s in the 2 s from the backing hand (2: at 13 and 14 s)", backLines, backLines == 1 ? "" : "s");
	CHECK(firstAfter > 0 && lineAt[firstAfter] - lineAt[11] > 5.5f && lineAt[firstAfter] - lineAt[11] < 6.7f,
	      "after the back key the riding hand's next line %.1f s after its 12th (6: one more every 6 s; %d lines in all)", firstAfter > 0 ? lineAt[firstAfter] - lineAt[11] : -1.0f, lines);
	g_onFrame = NULL;
	FlatGround();
	*head = from;
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
	/* Measured rather than waited for: the plugin keeps the keys 0.2 s (test 19), and a fixed
	 * 0.3 s wait failed once in three loaded all-mode runs (a slow frame under Wine). Polled
	 * every 25 ms for a second; it must be back within 0.6 s. */
	DWORD letGo = GetTickCount(), putBack = 0;
	while (GetTickCount() - letGo < 1000) {
		RunFrames(25);
		if (mod[0] == 0.0f && mod[1] == 0.0f && *modTime == 0.0f) {
			putBack = GetTickCount() - letGo;
			break;
		}
	}
	CHECK(putBack > 0 && putBack <= 600, "letting go: velocityMod and its time put back %.2f s after the keys (they're kept 0.2 s)", putBack / 1000.0);
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
		CHECK(lean > 2.0f && lean < 15.0f, "leaning into the turn, right side down (%.1f deg: LeanGain 0.5 of the physical lean, smoothed and rate-limited, at most MaxLean 14)", lean);
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
	CHECK(turned > 9.0f && turned < 38.0f, "stopped: %.1f deg in half a second (about 14: the keys' turning rate eases in over TurnEase 0.35 s)", turned);
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

/* The roll in the spine joint's map, read off its own bone entry (test 36's side lean): a
 * point 20 to the rider's right of the joint mapped with the joint, the tilt undone, and how
 * far up it went, in degrees; positive toward the turn the bars are over to (the right side
 * up when the bars are left, barNow > 0: the chest's top toward the inner grip). The twist
 * about the vertical doesn't change a point's height, so it drops out. */
static float SpineRollToward(const uint8_t *copy, const float right[3], const float Rw[9], float barNow)
{
	float pivot[3], P[3], mP[3], mPivot[3], d[3], e[3];
	memcpy(pivot, g_bodyNodes[2] + 0xA0, 12);
	for (int i = 0; i < 3; i++)
		P[i] = pivot[i] + 20.0f * right[i];
	MapBone(g_bodyNodes[2], g_bodyBonesOriginal + 2 * 0x50, copy + 2 * 0x50, P, mP);
	MapBone(g_bodyNodes[2], g_bodyBonesOriginal + 2 * 0x50, copy + 2 * 0x50, pivot, mPivot);
	for (int i = 0; i < 3; i++)
		d[i] = mP[i] - mPivot[i];
	for (int i = 0; i < 3; i++)
		e[i] = Rw[i] * d[0] + Rw[3 + i] * d[1] + Rw[6 + i] * d[2];   /* Rw^T d: the tilt undone */
	float s = e[2] / 20.0f;
	s = s > 1.0f ? 1.0f : s < -1.0f ? -1.0f : s;
	return asinf(s) * DEG * (barNow < 0.0f ? -1.0f : 1.0f);
}

static void SeatInBone(const uint8_t *bone, float out[3])
{
	const float *o = (const float *)(bone + 0x10), *t = (const float *)(bone + 0x40);
	for (int i = 0; i < 3; i++)
		out[i] = t[i] + 74.0f * (g_skinTransposed ? o[2 * 4 + i] : o[i * 4 + 2]);
}
/* The frame's lift as the seat shows it, signed along the bike's up (the seat is the pivot in
 * these runs, PivotHeight 74: the tilt leaves it in place, the lift alone moves it). */
static float SeatLift(void)
{
	float before[3], now[3], lift = 0.0f;
	const float *o = (const float *)(g_bonesOriginal + 0x10);
	SeatInBone(g_bonesOriginal, before);
	SeatInBone(g_bones, now);
	for (int i = 0; i < 3; i++)
		lift += (now[i] - before[i]) * (g_skinTransposed ? o[2 * 4 + i] : o[i * 4 + 2]);
	return lift;
}

/* The left wrist's turn from the clips' pose as the plugin wrote it this frame (the hand's map
 * against the forearm's, before the tilt), degrees, and in share the grip's distance from the
 * leaned shoulder over the arm's reach, percent (the clips' wrist turned with the bars, then
 * tilted): what the ride's-end line takes them as (test 39). */
static float WristTurnNow(float *share)
{
	float Rw3[9], Pw3[3], S[3], Ef[3], Wf[3], mS[3], Mh[9], Rf[9], Rft[9], Res[9], ax[3], Ag[9], Ng[9], Qg[9], qg[3], QW[3], target[3];
	const uint8_t *copyF = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
	ExpectedTilt(Rw3, Pw3);
	memcpy(S, g_bodyNodes[6] + 0xA0, 12);
	memcpy(Ef, g_bodyNodes[7] + 0xA0, 12);
	memcpy(Wf, g_bodyNodes[5] + 0xA0, 12);
	MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyF + 6 * 0x50, S, mS);
	BoneRotationBefore(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyF + 5 * 0x50, Wf, Rw3, Mh);
	BoneRotationBefore(g_bodyNodes[7], g_bodyBonesOriginal + 7 * 0x50, copyF + 7 * 0x50, Ef, Rw3, Rf);
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 3; j++)
			Rft[i * 3 + j] = Rf[j * 3 + i];
	MulM3(Rft, Mh, Res);
	BarTurnMap(BarAngle(), Ag, Ng, Qg, qg);
	Apply3(Qg, Wf, QW);
	for (int i = 0; i < 3; i++)
		QW[i] += qg[i] - Pw3[i];
	Apply3(Rw3, QW, target);
	for (int i = 0; i < 3; i++)
		target[i] += Pw3[i];
	*share = Dist3(mS, target) / (Dist3(S, Ef) + Dist3(Ef, Wf)) * 100.0f;
	return RotationAngle(Res, ax);
}

/* The clips' left wrist (the hand's node) from the grip's centre, before the bars' turn. */
static float WristOffGrip(void)
{
	float W[3], G[3];
	memcpy(W, g_bodyNodes[5] + 0xA0, 12);
	GripWorld(G);
	return Dist3(W, G);
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
	CHECK(bodyDataNow && bodyDataNow != g_bodyData && *(void **)bodyDataNow == *(void **)g_bodyData && *(uint32_t *)(bodyDataNow + 0x20) == 12,
	      "the body's skin instance points at the plugin's own copy of its bone data (the game's vtable, 12 bones)");
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
		float A[9], N[9], Q[9], q[3], R2[9], t2[3], before[3], after[3], G[3], mG[3];
		BarTurnMap(barNow, A, N, Q, q);
		ExpectedTilt(Rw, Pw);
		MulM3(Rw, Q, R2);
		Apply3(Rw, q, t2);
		for (int i = 0; i < 3; i++)
			t2[i] += Pw[i] - (Rw[i * 3] * Pw[0] + Rw[i * 3 + 1] * Pw[1] + Rw[i * 3 + 2] * Pw[2]);
		const uint8_t *copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
		/* The grip's centre (test 38: the hand is rolled round the grip about it, so it stays on
		 * the turned grip while the wrist, 6 units from it along the fingers, swings round it;
		 * till then the pivot was the wrist, and the palm swung off the bar). */
		GripWorld(G);
		MapBone(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, G, mG);
		memcpy(before, g_bodyNodes[5] + 0xA0, 12);
		MapBone(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, before, after);
		float off = TurnedOff(G, mG, Q, q, Rw, Pw), wristOff = TurnedOff(before, after, Q, q, Rw, Pw);
		float tiltOnly = TiltedOff(G, mG, Rw, Pw);
		CHECK(off < 0.1f && tiltOnly > 2.0f && LogLines("the wrist roll's pivot") == 1,
		      "the hand's bones carry the grip's centre round the steering axis by the bar angle, then the tilt (%.3f off; %.1f from the tilt alone; the parts line names it the wrist roll's pivot)", off, tiltOnly);
		{
			/* And the hand's rotation: the bars' turn, then a roll about the grip's axis (the
			 * bike's x through the bind, the bone and the turn; test 38's WristRoll). */
			float Mh[9], Qt[9], Dh[9], ex[3] = { -1.0f, 0.0f, 0.0f }, Ae[3], gb[3], rollAxis[3];
			BoneRotationBefore(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, before, Rw, Mh);
			for (int i = 0; i < 3; i++)
				for (int j = 0; j < 3; j++)
					Qt[i * 3 + j] = Q[j * 3 + i];
			MulM3(Qt, Mh, Dh);   /* the roll seen before the bars' turn: about the grip's axis as the clips have it */
			Apply3(A, ex, Ae);
			Apply3(N, Ae, gb);
			float roll = RotationAngle(Dh, rollAxis), axisOff = acosf(fabsf(rollAxis[0] * gb[0] + rollAxis[1] * gb[1] + rollAxis[2] * gb[2]) > 1.0f ? 1.0f : fabsf(rollAxis[0] * gb[0] + rollAxis[1] * gb[1] + rollAxis[2] * gb[2])) * DEG;
			CHECK(roll < 0.5f || axisOff < 10.0f, "the hand's rotation is the bars' turn and a roll of %.1f deg about the grip's axis (the roll's axis %.1f deg off it; WristRoll 1.0)", roll, roll < 0.5f ? 0.0f : axisOff);
			/* The wrist swings round the grip's centre by that roll: 2 r sin(roll / 2) off the
			 * bars' turn of it, r its distance from the centre across the grip's axis. */
			float dG[3] = { before[0] - G[0], before[1] - G[1], before[2] - G[2] }, lg = sqrtf(gb[0] * gb[0] + gb[1] * gb[1] + gb[2] * gb[2]);
			float along = (dG[0] * gb[0] + dG[1] * gb[1] + dG[2] * gb[2]) / lg, r = sqrtf(dG[0] * dG[0] + dG[1] * dG[1] + dG[2] * dG[2] - along * along);
			float swing = 2.0f * r * sinf(roll / DEG / 2.0f);
			CHECK(roll > 1.0f && wristOff > 0.3f && fabsf(wristOff - swing) < 0.05f,
			      "the wrist, %.1f from the grip's centre (%.1f of it across the grip's axis), swung %.2f off the bars' turn of it: rolled round the grip, not about itself (2 x %.1f x sin(%.1f / 2) = %.2f)",
			      Dist3(before, G), r, wristOff, r, roll, swing);
		}
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
			/* The shoulder goes with the upper body's twist (test 32): about the spine's joint, by
			 * TorsoTwist (0.75 since test 36; 0.4 folded the inner arm tight at full lock) of the
			 * bars' angle, the chest turning the way the bars do (left here), so the left shoulder
			 * swings back and out; and with its side lean (test 36), TorsoSideLean (0.25) of the
			 * bars' angle about the forward axis through the joint, the chest's top toward the
			 * inner grip, so the right side goes up in this left turn; its distance from the
			 * joint is kept. TorsoLean=0 in this run's INI: no forward lean yet. */
			float pivot[3], twist = 0.75f * barNow / DEG, ct = cosf(twist), stw = sinf(twist), rel[3], Sx[3];
			float hNow = *headNow, fw[3] = { sinf(hNow), cosf(hNow), 0.0f }, rt[3] = { cosf(hNow), -sinf(hNow), 0.0f };
			float sideLean = 0.25f * barNow / DEG, cs = cosf(sideLean), ss = sinf(sideLean);
			memcpy(pivot, g_bodyNodes[2] + 0xA0, 12);
			for (int i = 0; i < 3; i++)
				rel[i] = S[i] - pivot[i];
			float a = rel[0] * rt[0] + rel[1] * rt[1], b = rel[0] * fw[0] + rel[1] * fw[1], c2 = rel[2];   /* right, forward, up of the joint */
			float a2 = a * cs - c2 * ss, c3 = a * ss + c2 * cs;   /* the side lean: right -> up */
			for (int i = 0; i < 3; i++)
				rel[i] = a2 * rt[i] + b * fw[i] + (i == 2 ? c3 : 0.0f);
			Sx[0] = ct * rel[0] - stw * rel[1] + pivot[0];
			Sx[1] = stw * rel[0] + ct * rel[1] + pivot[1];
			Sx[2] = rel[2] + pivot[2];
			CHECK(TiltedOff(Sx, mS, Rw, Pw) < 0.1f && TiltedOff(S, mS, Rw, Pw) > 0.5f,
			      "the arm's solve: the shoulder swung with the upper body's twist, %.1f deg about the spine's joint, and its side lean of %.1f (%.3f off that; %.2f from where the clips had it)", twist * DEG, sideLean * DEG, TiltedOff(Sx, mS, Rw, Pw), TiltedOff(S, mS, Rw, Pw));
			CHECK(Dist3(mE1, mE2) < 0.1f, "the upper arm and the forearm meet at the elbow (%.3f apart)", Dist3(mE1, mE2));
			CHECK(Dist3(mW2, mW3) < 0.1f && TurnedOff(Wr, mW2, Q, q, Rw, Pw) > 0.3f, "the forearm and the hand meet at the rolled wrist, %.2f off the bars' turn of the clips' (%.3f apart; the forearm solved again to it)", TurnedOff(Wr, mW2, Q, q, Rw, Pw), Dist3(mW2, mW3));
			{
				/* Test 39: the hand's long axis along the forearm seen along the turned grip's
				 * axis, the bars over (the clips' hand, turned with them alone, well off it). */
				float Mh2[9], clipsOff;
				BoneRotationBefore(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, Wr, Rw, Mh2);
				float up = HandAboveForearm(0, Mh2, mE2, mW2, Rw, Q, &clipsOff);
				CHECK(fabsf(up) < 1.5f && fabsf(clipsOff) > 10.0f, "the bars over %.1f deg: the hand's long axis, seen along the turned grip, %.2f deg off the solved forearm's (within 1.5; the clips' hand turned with the bars %.1f off it)", barNow, up, clipsOff);
			}
			CHECK(fabsf(Dist3(mE1, mS) - Dist3(E, S)) < 0.05f && fabsf(Dist3(mW2, mE2) - Dist3(Wr, E)) < 0.05f,
			      "the bones keep their lengths (%.1f and %.1f)", Dist3(mE1, mS), Dist3(mW2, mE2));
			CHECK(TiltedOff(E, mE2, Rw, Pw) > 0.3f, "the elbow moved (%.2f): the arm bent to reach", TiltedOff(E, mE2, Rw, Pw));
			{
				/* Test 38's ArmPole (the left arm's x mirrored): the elbow's offset from the
				 * shoulder-to-wrist line goes the pole's way, the pole taken to world through the
				 * bike's bind and the bone like the grip's axis (here the fake's bind turns the
				 * bike's x down, so the pole points mostly out to the left, not down) and tilted
				 * like the rest; no longer the clips' own plane, carried by the upper body's twist
				 * and side lean, which lies well away from it. Test 41: ArmPole 1.1,-0.3,-0.9, and
				 * this left arm is the inside one in this left turn, so its pole is faded toward
				 * ArmPoleTurn 0.35,-0.3,-1.0 by the bars' angle over ArmPoleTurnBars 10 (mode 13
				 * has the fade's own checks, the outside arm among them). */
				static const float armPole[3] = { 1.1f, -0.3f, -0.9f }, armPoleTurn[3] = { 0.35f, -0.3f, -1.0f };
				float poleM[3], Ap[3], Np[3], poleT[3], n0[3], Tr[9], Tn[3], n0T[3], offLen;
				float fadeK = ExpectedPole(0, barNow, armPole, armPoleTurn, 10.0f, poleM);
				Apply3(A, poleM, Ap);
				Apply3(N, Ap, Np);
				Apply3(Rw, Np, poleT);
				ClipsElbowOffset(S, E, Wr, n0);
				BoneRotationBefore(g_bodyNodes[2], g_bodyBonesOriginal + 2 * 0x50, copyNow + 2 * 0x50, pivot, Rw, Tr);
				Apply3(Tr, n0, Tn);
				Apply3(Rw, Tn, n0T);
				float poleOff = ElbowPlaneOff(mS, mE2, mW3, poleT, &offLen), clipsOff = ElbowPlaneOff(mS, mE2, mW3, n0T, NULL);
				CHECK(poleOff < 1.0f && offLen > 2.0f && clipsOff > 5.0f && fadeK > 0.5f,
				      "the elbow bent the pole's way: its offset from the shoulder-to-wrist line (%.1f) %.1f deg off ArmPole 1.1,-0.3,-0.9 faded %.2f of the way to ArmPoleTurn 0.35,-0.3,-1.0 (the inside arm, the bars %.1f over), taken through the bind and the bone (the clips' own plane %.1f deg from it)",
				      offLen, poleOff, fadeK, barNow, clipsOff);
			}
			/* Test 36's side lean, read off the spine joint's own map: a roll toward the turn of
			 * TorsoSideLean (0.25) of the bars' angle. */
			float roll = SpineRollToward(copyNow, rt, Rw, barNow);
			CHECK(fabsf(roll - 0.25f * fabsf(barNow)) < 0.3f,
			      "the upper body leaned into the turn: the spine's map rolls %.2f deg toward it, the chest's top to the inner grip (TorsoSideLean 0.25 of the bars' %.1f: %.2f)", roll, fabsf(barNow), 0.25f * fabsf(barNow));
			/* The hands' bones with no node (test 34): held through their own world transforms;
			 * the fingers go with the hand, the wrist end of the forearm with the forearm, a
			 * stray bone far from the hands with the tilt alone. */
			const uint8_t *handsCopy = *(const uint8_t **)(*(uint8_t **)(g_handsSkin + 0x40) + 0x10);
			CHECK(handsCopy && memcmp(handsCopy, g_handsBonesOriginal, sizeof(g_handsBonesOriginal)) != 0, "the hands' skin (two bones with nodes of 36, in the game) held and written");
			if (handsCopy) {
				float P[3], mX[3], mRef[3];
				const char *parts[5] = { "a finger", "the other finger", "the forearm's wrist end", "", "a stray bone" };
				for (int i = 0; i < 5; i++) {
					if (i == 3)
						continue;
					memcpy(P, g_handsXf[i] + 0x30, 12);
					MapBoneAt(g_handsXf[i], g_handsBonesOriginal + i * 0x50, handsCopy + i * 0x50, P, mX);
					if (i == 4) {
						CHECK(TiltedOff(P, mX, Rw, Pw) < 0.05f, "%s with no node, far from the hands: carried with the tilt alone (%.3f off)", parts[i], TiltedOff(P, mX, Rw, Pw));
					} else {
						int ref = i == 2 ? 7 : 5;
						MapBone(g_bodyNodes[ref], g_bodyBonesOriginal + ref * 0x50, copyNow + ref * 0x50, P, mRef);
						CHECK(Dist3(mX, mRef) < 0.1f, "%s with no node, held through its own transform, goes with the %s (%.3f apart)", parts[i], ref == 7 ? "forearm" : "hand", Dist3(mX, mRef));
					}
				}
			}
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

	if (g_haveParts) {
		printf("tilt: the upper body leaned forward for the arms' reach (TorsoLean=-1 for a ride; ArmReach 0.80 since test 38, 0.88 before):\n");
		RewriteIni("TorsoLean=0", "TorsoLean=-1");   /* read again on getting on */
		int inheritedBefore = LogLines("Belly_skin with the upper body");
		SetTilt(0.0f);
		RunFrames(300);
		SetTilt(30.0f);
		RunFrames(600);
		float Rw2[9], Pw2[3], S[3], E[3], Wr[3], Hd[3], Up[3], pivot[3], mS[3], mE1[3], mE2[3], mW2[3], mW3[3], mH[3], mUp[3], d0[3], Rd[3], TP[3], upT[3];
		const uint8_t *copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
		ExpectedTilt(Rw2, Pw2);
		memcpy(S, g_bodyNodes[6] + 0xA0, 12);
		memcpy(E, g_bodyNodes[7] + 0xA0, 12);
		memcpy(Wr, g_bodyNodes[5] + 0xA0, 12);
		memcpy(Hd, g_bodyNodes[8] + 0xA0, 12);
		memcpy(pivot, g_bodyNodes[2] + 0xA0, 12);
		for (int i = 0; i < 3; i++)
			Up[i] = Hd[i] + (i == 2 ? 10.0f : 0.0f);
		MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, S, mS);
		MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, E, mE1);
		MapBone(g_bodyNodes[7], g_bodyBonesOriginal + 7 * 0x50, copyNow + 7 * 0x50, E, mE2);
		MapBone(g_bodyNodes[7], g_bodyBonesOriginal + 7 * 0x50, copyNow + 7 * 0x50, Wr, mW2);
		MapBone(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, Wr, mW3);
		MapBone(g_bodyNodes[8], g_bodyBonesOriginal + 8 * 0x50, copyNow + 8 * 0x50, Hd, mH);
		MapBone(g_bodyNodes[8], g_bodyBonesOriginal + 8 * 0x50, copyNow + 8 * 0x50, Up, mUp);
		/* The grip: the clips' wrist turned with the bars, the hand's target before the wrist
		 * roll, which swings the wrist itself round the grip's centre (test 38) and, by test
		 * 39's roll into line with the forearm, by a good deal here (the fake's hand is 48 deg
		 * off its forearm seen along the grip). */
		float reach = Dist3(S, E) + Dist3(E, Wr), was = Dist3(S, Wr) / reach, ratio, rolledAt = Dist3(mS, mW3) / reach;
		{
			float Ag[9], Ng[9], Qg[9], qg[3], QW[3], target[3];
			BarTurnMap(BarAngle(), Ag, Ng, Qg, qg);
			Apply3(Qg, Wr, QW);
			for (int i = 0; i < 3; i++)
				QW[i] += qg[i] - Pw2[i];
			Apply3(Rw2, QW, target);
			for (int i = 0; i < 3; i++)
				target[i] += Pw2[i];
			ratio = Dist3(mS, target) / reach;
		}
		CHECK(was > 0.9f && ratio > 0.78f && ratio < 0.82f, "the grip %.0f%% of the arms' reach from the shoulder (%.0f%% as the clips pose it; ArmReach 0.80; the rolled wrist %.0f%%)", ratio * 100.0f, was * 100.0f, rolledAt * 100.0f);
		for (int i = 0; i < 3; i++)
			d0[i] = pivot[i] - Pw2[i];
		Apply3(Rw2, d0, Rd);
		for (int i = 0; i < 3; i++)
			TP[i] = Rd[i] + Pw2[i];
		CHECK(TiltedOff(S, mS, Rw2, Pw2) > 1.0f && fabsf(Dist3(mS, TP) - Dist3(S, pivot)) < 0.1f,
		      "the shoulder swung forward about the spine's joint (%.1f; its distance from the joint %.1f, was %.1f)", TiltedOff(S, mS, Rw2, Pw2), Dist3(mS, TP), Dist3(S, pivot));
		{
			/* The body's skin helpers (test 38's pose study: Belly_skin and its kind, whose names
			 * say nothing to the parts, were left where the clips put them while the torso
			 * leaned, a hump on the upper back): a bone with no part by name takes the first
			 * found up its node parents, 8 at most. Belly_skin, under SPINE1, leans with the
			 * upper body about the joint like the shoulder; LLeg_Thigh_skin, under the pelvis
			 * with no part anywhere up its chain, is carried with the tilt alone; the hold's
			 * line names the one and not the other. */
			float B[3], mB[3], T[3], mT[3];
			memcpy(B, g_bodyNodes[10] + 0xA0, 12);
			memcpy(T, g_bodyNodes[11] + 0xA0, 12);
			MapBone(g_bodyNodes[10], g_bodyBonesOriginal + 10 * 0x50, copyNow + 10 * 0x50, B, mB);
			MapBone(g_bodyNodes[11], g_bodyBonesOriginal + 11 * 0x50, copyNow + 11 * 0x50, T, mT);
			CHECK(TiltedOff(B, mB, Rw2, Pw2) > 1.0f && fabsf(Dist3(mB, TP) - Dist3(B, pivot)) < 0.1f,
			      "Belly_skin, no part by name, under SPINE1: swung forward about the spine's joint with the upper body, as its parent's part says (%.1f; its distance from the joint %.1f, was %.1f)",
			      TiltedOff(B, mB, Rw2, Pw2), Dist3(mB, TP), Dist3(B, pivot));
			CHECK(TiltedOff(T, mT, Rw2, Pw2) < 0.1f, "LLeg_Thigh_skin, no part by name or up its chain, under the pelvis: carried with the tilt alone (%.3f off)", TiltedOff(T, mT, Rw2, Pw2));
			CHECK(LogLines("Belly_skin with the upper body") > inheritedBefore && LogLines("LLeg_Thigh_skin") == 0,
			      "the hold's line says a bone with no part by name took its parent's: \"Belly_skin with the upper body\" (%d line%s this ride), and never names LLeg_Thigh_skin",
			      LogLines("Belly_skin with the upper body") - inheritedBefore, LogLines("Belly_skin with the upper body") - inheritedBefore == 1 ? "" : "s");
		}
		CHECK(Dist3(mE1, mE2) < 0.1f && Dist3(mW2, mW3) < 0.1f, "the chain stays joined at the elbow and the wrist, the hand on the grip (%.3f, %.3f apart)", Dist3(mE1, mE2), Dist3(mW2, mW3));
		CHECK(fabsf(Dist3(mE1, mS) - Dist3(E, S)) < 0.05f && fabsf(Dist3(mW2, mE2) - Dist3(Wr, E)) < 0.05f,
		      "the bones keep their lengths (%.1f and %.1f)", Dist3(mE1, mS), Dist3(mW2, mE2));
		float poleT[3], n0[3], Np0[3];
		{
			/* The elbow, re-solved for the shorter reach, goes the pole's way here too (test 38:
			 * the straight bars and the lean are the tester's video). */
			float A[9], N[9], poleM[3] = { -1.1f, -0.3f, -0.9f }, Ap[3], offLen;   /* test 41's ArmPole, the bars straight: no fade */
			LoadRotation((const float *)(g_bonesOriginal + 0x10), A, g_skinTransposed);
			LoadRotation((const float *)(g_comNode + 0x70), N, g_rootTransposed);
			Apply3(A, poleM, Ap);
			Apply3(N, Ap, Np0);
			Apply3(Rw2, Np0, poleT);
			ClipsElbowOffset(S, E, Wr, n0);
			float poleOff = ElbowPlaneOff(mS, mE2, mW3, poleT, &offLen);
			CHECK(poleOff < 1.0f && offLen > 2.0f, "the elbow bent the pole's way with the lean: its offset from the shoulder-to-wrist line (%.1f) %.1f deg off ArmPole", offLen, poleOff);
		}
		{
			static const float ten[3] = { 0, 0, 10 };
			Apply3(Rw2, ten, upT);
			CHECK(TiltedOff(Hd, mH, Rw2, Pw2) > 1.0f && fabsf(mUp[0] - mH[0] - upT[0]) < 0.05f && fabsf(mUp[1] - mH[1] - upT[1]) < 0.05f && fabsf(mUp[2] - mH[2] - upT[2]) < 0.05f,
			      "the head's joint goes forward with the upper body (%.1f) and the head keeps its own pitch, not leaned with it", TiltedOff(Hd, mH, Rw2, Pw2));
		}
		{
			/* The wrist roll (test 37: 25 deg of wrist turn at the straight bars, the forearm
			 * swung by the lean and the re-solved elbow, the hand keeping the clips' orientation):
			 * the hand's map, the bars straight, is no longer the identity but a roll about the
			 * grip's axis (the bike's x through the bind and the bone) by the forearm's twist
			 * about it, so the wrist's turn from the clips' pose is only the forearm's swing. */
			float Mh[9], A[9], N[9], ex[3] = { -1.0f, 0.0f, 0.0f }, Ae[3], gb[3], rollAxis[3], Qa[9], qa[3], Aa[9], Na[9];
			LoadRotation((const float *)(g_bonesOriginal + 0x10), A, g_skinTransposed);
			LoadRotation((const float *)(g_comNode + 0x70), N, g_rootTransposed);
			Apply3(A, ex, Ae);
			Apply3(N, Ae, gb);
			BoneRotationBefore(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, Wr, Rw2, Mh);
			float roll = RotationAngle(Mh, rollAxis);
			float axisOff = acosf(fabsf(rollAxis[0] * gb[0] + rollAxis[1] * gb[1] + rollAxis[2] * gb[2]) > 1.0f ? 1.0f : fabsf(rollAxis[0] * gb[0] + rollAxis[1] * gb[1] + rollAxis[2] * gb[2])) * DEG;
			/* Test 39 ("cat paw"): the roll lays the hand's long axis along the forearm seen
			 * along the grip (the solved elbow to the wrist), where the forearm's own twist
			 * about the grip kept the clips' bend; the fake's hand has the clips' frame, the
			 * long axis 39 deg below the bike's forward. */
			BarTurnMap(BarAngle(), Aa, Na, Qa, qa);
			float clipsOff, up = HandAboveForearm(0, Mh, mE2, mW2, Rw2, Qa, &clipsOff), logged = LastLogNumber("its axis ");
			CHECK(roll > 1.0f && axisOff < 10.0f && fabsf(up) < 1.5f && fabsf(clipsOff) > 10.0f,
			      "the hand rolled %.1f deg about the grip's axis (the roll's axis %.1f deg off it): its long axis, seen along the grip, %.2f deg off the solved forearm's (within 1.5; the clips' hand %.1f off it; WristRoll 1.0, HandPitch 0)", roll, axisOff, up, clipsOff);
			CHECK(fabsf(logged - up) < 0.3f, "the ride's \"arm solved\" line says the hand's axis %.1f deg above the forearm's (the pose's %.2f)", logged, up);
			{
				/* The pivot (test 38): the grip's centre stays where the bars (straight, within
				 * their creep) have it, the wrist swings round it. */
				float Q[9], q[3], G[3], mG[3];
				BarTurnMap(BarAngle(), A, N, Q, q);
				GripWorld(G);
				MapBone(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, G, mG);
				CHECK(TurnedOff(G, mG, Q, q, Rw2, Pw2) < 0.1f && TurnedOff(Wr, mW3, Q, q, Rw2, Pw2) > 0.3f && Dist3(mW2, mW3) < 0.1f,
				      "the grip's centre stays on the grip (%.3f off the bars' turn of it) and the hand still meets the forearm at the wrist, swung %.2f round the grip by the roll (%.3f apart)",
				      TurnedOff(G, mG, Q, q, Rw2, Pw2), TurnedOff(Wr, mW3, Q, q, Rw2, Pw2), Dist3(mW2, mW3));
				/* Review of test 38's build: the arm's log line keeps the grip's distance from
				 * the shoulder (the first pass's reach, the hand's clip position turned by the
				 * bars); the roll's passes aim at the rolled wrist, a unit or two off it, and
				 * the line carried that. Read back from the ride's line, with the bars it logged
				 * (straight, within their creep); the shoulder's map holds the lean. */
				float barsLogged = LastLogNumber("arm solved (the bars "), gripLogged = LastLogNumber("the grip "), Qc[9], qc[3], QW[3], target[3];
				BarTurnMap(barsLogged, A, N, Qc, qc);
				Apply3(Qc, Wr, QW);
				for (int i = 0; i < 3; i++)
					QW[i] += qc[i] - Pw2[i];
				Apply3(Rw2, QW, target);
				for (int i = 0; i < 3; i++)
					target[i] += Pw2[i];
				CHECK(fabsf(barsLogged) < 1.0f && fabsf(gripLogged - Dist3(mS, target)) < 0.3f,
				      "the ride's \"arm solved\" line says the grip %.1f from the shoulder (the bars %.1f deg): the clips' hand turned by those bars is %.1f from the leaned shoulder, within 0.3 (the rolled wrist %.1f from it: the first pass's reach is the one logged, not the roll's)",
				      gripLogged, barsLogged, Dist3(mS, target), Dist3(mS, mW3));
			}
			printf("tilt: the wrist roll off and the elbows in the clips' own planes (WristRoll=0, ArmPole=0,0,0 for a ride):\n");
			RewriteIni("WristRoll=1.0", "WristRoll=0");
			RewriteIni("ArmPole=1.1,-0.3,-0.9", "ArmPole=0,0,0");
			SetTilt(0.0f);
			RunFrames(300);
			SetTilt(30.0f);
			RunFrames(600);
			copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
			ExpectedTilt(Rw2, Pw2);
			MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, S, mS);
			MapBone(g_bodyNodes[7], g_bodyBonesOriginal + 7 * 0x50, copyNow + 7 * 0x50, E, mE2);
			MapBone(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, Wr, mW3);
			BoneRotationBefore(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, Wr, Rw2, Mh);
			float noRoll = RotationAngle(Mh, rollAxis);
			CHECK(TiltedOff(S, mS, Rw2, Pw2) > 1.0f && noRoll < 0.5f, "the upper body still leaned (the shoulder %.1f forward), the hand's map the bars' turn alone again (the identity at the straight bars, within the bars' creep: %.2f deg)", TiltedOff(S, mS, Rw2, Pw2), noRoll);
			{
				/* ArmPole=0,0,0: the old elbow, in the plane the clips pose it in, carried by the
				 * upper body's lean (the spine joint's own map, read off its bone entry). */
				float Tr[9], Tn[3], n0T[3], offLen;
				BoneRotationBefore(g_bodyNodes[2], g_bodyBonesOriginal + 2 * 0x50, copyNow + 2 * 0x50, pivot, Rw2, Tr);
				Apply3(Tr, n0, Tn);
				Apply3(Rw2, Tn, n0T);
				Apply3(Rw2, Np0, poleT);
				float clipsOff = ElbowPlaneOff(mS, mE2, mW3, n0T, &offLen), poleOff = ElbowPlaneOff(mS, mE2, mW3, poleT, NULL);
				CHECK(clipsOff < 1.0f && offLen > 2.0f && poleOff > 5.0f, "ArmPole=0,0,0: the elbow in the clips' own plane again, carried by the lean (its offset %.1f, %.1f deg off that plane; the pole's %.1f deg away)", offLen, clipsOff, poleOff);
			}
			RewriteIni("WristRoll=0", "WristRoll=1.0");
			RewriteIni("ArmPole=0,0,0", "ArmPole=1.1,-0.3,-0.9");
		}
		{
			/* Test 39's HandPitch: the hand's long axis that many degrees above the forearm's line
			 * seen along the grip, the knuckles up (about the bike's +x on either hand: the left's
			 * own outward axis is -x, so its angle about that is negated); the grip's centre still
			 * on the grip, the hand still meeting the forearm at the wrist. */
			printf("tilt: the hand pitched 10 deg up from the forearm (HandPitch=10 for a ride):\n");
			RewriteIni("HandPitch=0", "HandPitch=10");
			SetTilt(0.0f);
			RunFrames(300);
			SetTilt(30.0f);
			RunFrames(600);
			float Mh[9], Ap[9], Np[9], Qp[9], qp[3], Ep[3], Wp[3], mEp[3], mWp[3], mW3p[3], G[3], mG[3];
			copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
			ExpectedTilt(Rw2, Pw2);
			memcpy(Ep, g_bodyNodes[7] + 0xA0, 12);
			memcpy(Wp, g_bodyNodes[5] + 0xA0, 12);
			MapBone(g_bodyNodes[7], g_bodyBonesOriginal + 7 * 0x50, copyNow + 7 * 0x50, Ep, mEp);
			MapBone(g_bodyNodes[7], g_bodyBonesOriginal + 7 * 0x50, copyNow + 7 * 0x50, Wp, mWp);
			MapBone(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, Wp, mW3p);
			BoneRotationBefore(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, Wp, Rw2, Mh);
			BarTurnMap(BarAngle(), Ap, Np, Qp, qp);
			GripWorld(G);
			MapBone(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, G, mG);
			float up = HandAboveForearm(0, Mh, mEp, mWp, Rw2, Qp, NULL), logged = LastLogNumber("its axis ");
			CHECK(fabsf(up - 10.0f) < 1.5f && fabsf(logged - up) < 0.3f && LogLines("(HandPitch 10)") >= 1,
			      "the left hand's long axis %.2f deg above the solved forearm's seen along the grip (10, within 1.5: the knuckles up; the arm's line says %.1f, HandPitch 10)", up, logged);
			CHECK(TurnedOff(G, mG, Qp, qp, Rw2, Pw2) < 0.1f && Dist3(mWp, mW3p) < 0.1f, "the grip's centre still on the grip (%.3f off the bars' turn of it), the hand still meeting the forearm at the wrist (%.3f apart)", TurnedOff(G, mG, Qp, qp, Rw2, Pw2), Dist3(mWp, mW3p));
			RewriteIni("HandPitch=10", "HandPitch=0");
		}
		{
			/* The bisection's cap, 30 deg since test 38 (15 before): ArmReach=0.5 for a ride needs
			 * about 20 here (the fake's reach moves about 2.5% a degree), which the old cap would
			 * have stopped at 15. The lean read off the shoulder's swing about the spine's joint:
			 * the chord 2 d sin(lean / 2). */
			printf("tilt: the lean's cap at 30 deg (ArmReach=0.5 for a ride: about 20 deg needed here, over the old cap of 15):\n");
			RewriteIni("ArmReach=0.80", "ArmReach=0.5");
			SetTilt(0.0f);
			RunFrames(300);
			SetTilt(30.0f);
			RunFrames(1500);
			copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
			ExpectedTilt(Rw2, Pw2);
			MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, S, mS);
			float chord = TiltedOff(S, mS, Rw2, Pw2), dj = Dist3(S, pivot), half = dj > 0.001f ? chord / (2.0f * dj) : 0.0f;
			float lean = 2.0f * asinf(half > 1.0f ? 1.0f : half) * DEG, logged = LastLogNumber("the upper body leaned ");
			/* The chord over the shoulder's distance from the joint reads a little under the lean
			 * (the fake's shoulder sits 18 to the side, off the lean's axis: about 0.96 of it), so
			 * the plugin's own figure is the one held to the window, the pose's to agree with it. */
			CHECK(logged > 15.5f && logged < 30.5f && fabsf(lean - logged) < 1.5f, "the upper body leaned %.1f deg by the log (%.1f by the shoulder's chord %.1f about the joint %.1f away): past the old cap of 15, within 30", logged, lean, chord, dj);
			RewriteIni("ArmReach=0.5", "ArmReach=0.80");
		}
		RewriteIni("TorsoLean=-1", "TorsoLean=0");
		SetTilt(0.0f);
		RunFrames(300);
		SetTilt(30.0f);
		RunFrames(600);
		copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
		ExpectedTilt(Rw2, Pw2);   /* this ride's tilt */
		MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, S, mS);
		CHECK(TiltedOff(S, mS, Rw2, Pw2) < 0.05f, "TorsoLean=0 again on the next ride: the shoulder where the clips have it (%.3f off)", TiltedOff(S, mS, Rw2, Pw2));
	}

	if (g_haveParts) {
		/* Test 37's Pip-Boy: opened a second after getting on, it moved the arm bones 40.7 in
		 * a frame and put the grips at 82% of the reach, and the lean solved from that pose (0)
		 * stuck for five minutes, through a fast travel. The solve waits while the clips' reach
		 * is short of the riding pose's (under 95%), logs it once, comes once the hand is back,
		 * and comes again after a load. */
		printf("tilt: the upper body's lean not solved while the grips are short of the riding pose's reach (the left hand raised to 80%% of it; TorsoLean=-1 for a ride):\n");
		RewriteIni("TorsoLean=0", "TorsoLean=-1");
		g_handRaised = true;
		int leanedBefore = LogLines("deg forward about the spine's joint"), waitBefore = LogLines("not solved yet");
		SetTilt(0.0f);
		RunFrames(300);
		SetTilt(30.0f);
		RunFrames(3000);
		float Rw2[9], Pw2[3], S[3], mS[3];
		const uint8_t *copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
		ExpectedTilt(Rw2, Pw2);
		memcpy(S, g_bodyNodes[6] + 0xA0, 12);
		MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, S, mS);
		CHECK(TiltedOff(S, mS, Rw2, Pw2) < 0.05f, "3 s in, no lean: the shoulder where the clips have it (%.3f off the tilt alone)", TiltedOff(S, mS, Rw2, Pw2));
		CHECK(LogLines("deg forward about the spine's joint") == leanedBefore && LogLines("not solved yet") == waitBefore + 1,
		      "the log: no \"leaned\" line this ride, one \"not solved yet\" line (%d and %d more)", LogLines("deg forward about the spine's joint") - leanedBefore, LogLines("not solved yet") - waitBefore);
		/* Test 38: a Pip-Boy held open over 20 s right after getting on (the map browsed for a
		 * fast travel) had the solve taken as it comes with the grips at 82%, a lean of 0, and
		 * that was final, so the full-lock over-reach was back for the whole ride. Taken as it
		 * comes the solve isn't final now: measured again every half second, and once the riding
		 * pose is there the lean is solved from it. */
		printf("tilt: 20 s of it: the lean taken as it comes (0, not final), solved again once the riding pose is there (test 38):\n");
		int comesBefore = LogLines("taken as it comes"), cameBefore = LogLines("the riding pose came: solved again");
		RunFrames(19000);   /* 22 s into the ride: the wait began at the first try, half a second in */
		copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
		MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, S, mS);
		CHECK(TiltedOff(S, mS, Rw2, Pw2) < 0.05f && LogLines("taken as it comes") == comesBefore + 1 && LogLines("deg forward about the spine's joint") == leanedBefore + 1,
		      "22 s in: the lean taken as it comes, 0 from the raised hand's 79%% (the shoulder %.3f off the tilt alone), one \"leaned\" line saying so (%d, %d)",
		      TiltedOff(S, mS, Rw2, Pw2), LogLines("taken as it comes") - comesBefore, LogLines("deg forward about the spine's joint") - leanedBefore);
		{
			/* Test 40: a run after a jump starts from the solve before it, but not from one taken
			 * as it comes (test 38's Pip-Boy start): the short start, then a jump of 1000 units
			 * from a ground frame along the slope's contour with the hand still raised, then the
			 * grips at 95%: the lean solved again from that reading. */
			printf("tilt: taken as it comes, then a jump of 1000 units and the grips at 95%%: not kept, solved again from the 95%% reading (test 40):\n");
			int jumpWas = LogLines("solved again after a jump of 1000 units (a door, a fast travel)"), leanedWas = LogLines("deg forward about the spine's joint");
			for (int k = 0; k < 3; k++)
				PlayerPos()[k] += right[k] * 1000.0f;
			g_handRaised = false;
			g_handReach = 0.952f;
			RunFrames(1000);
			copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
			ExpectedTilt(Rw2, Pw2);
			memcpy(S, g_bodyNodes[6] + 0xA0, 12);   /* the shoulder went with the player */
			MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, S, mS);
			CHECK(LogLines("solved again after a jump of 1000 units (a door, a fast travel)") == jumpWas + 1 && LogLines("deg forward about the spine's joint") == leanedWas + 1 &&
			      fabsf(LastLogNumber("% of the arms' reach with the bars straight (") - 95.0f) < 0.6f && LastLogNumber("the upper body leaned ") > 1.0f && TiltedOff(S, mS, Rw2, Pw2) > 1.0f,
			      "within the second: a \"leaned\" line saying \"solved again after a jump of 1000 units\" (%d), %.1f deg from the %.0f%% reading (the shoulder %.1f forward)",
			      LogLines("solved again after a jump of 1000 units (a door, a fast travel)") - jumpWas, LastLogNumber("the upper body leaned "), LastLogNumber("% of the arms' reach with the bars straight ("), TiltedOff(S, mS, Rw2, Pw2));
			g_handReach = 0.0f;
		}
		/* A new ride for the riding pose's coming: the hand raised from its start, 21.5 s. */
		SetTilt(0.0f);
		RunFrames(300);
		g_handRaised = true;
		leanedBefore = LogLines("deg forward about the spine's joint");
		cameBefore = LogLines("the riding pose came: solved again");
		comesBefore = LogLines("taken as it comes");
		SetTilt(30.0f);
		RunFrames(21500);
		ExpectedTilt(Rw2, Pw2);
		memcpy(S, g_bodyNodes[6] + 0xA0, 12);
		CHECK(LogLines("taken as it comes") == comesBefore + 1 && LogLines("deg forward about the spine's joint") == leanedBefore + 1,
		      "a new ride with the hand raised: taken as it comes again by 21.5 s (%d, %d)", LogLines("taken as it comes") - comesBefore, LogLines("deg forward about the spine's joint") - leanedBefore);
		g_handRaised = false;
		RunFrames(1000);
		copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
		MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, S, mS);
		CHECK(TiltedOff(S, mS, Rw2, Pw2) > 1.0f && LogLines("the riding pose came: solved again") == cameBefore + 1 && LogLines("deg forward about the spine's joint") == leanedBefore + 2,
		      "the hand back on the grip: the riding pose came and the lean was solved again within the second, its readings started again (final 3 s on, the best of them: test 39) (the shoulder %.1f forward, %d \"leaned\" lines, %d saying the pose came)",
		      TiltedOff(S, mS, Rw2, Pw2), LogLines("deg forward about the spine's joint") - leanedBefore, LogLines("the riding pose came: solved again") - cameBefore);
		/* Test 38: a fast travel on the bike (10:49:47 to 51) left all 60 shapes held and sent no
		 * PostLoadGame, and the lean of the ride's start stood for the whole ride after it; the
		 * track code's jump of over 150 units (a door, a fast travel, a teleport) now has the
		 * lean solved again, kept as it is meanwhile. */
		/* Review of test 38's build: a hop at speed lands over 150 from its last track point
		 * (the track's own jump threshold), and a cell load's stall can carry a frame that far;
		 * both would have logged "a fast travel" and started the lean's wait over. The lean is
		 * solved again after a jump over 300 from a ground frame only (the track still cleared
		 * at 150): a hop of 200 in the air (0.3 s, under TRACK_MAX_AIR 0.4), one of 350 (over
		 * 300: the air frame before it is what spares the lean), then 200 in one frame on the
		 * ground. All of it to the rider's right, along the contour of the 20 deg slope the ride
		 * is on: the ground stays at the feet, and the dip and step checks later on flatten the
		 * ground at the slope's origin, where the rider's feet must still be. */
		printf("tilt: a hop at speed (in the air 0.3 s, landing 200 units on, then one landing 350 on) and a stall on the ground (200 units in one frame): the lean kept, no \"solved again after a jump\" line (review of test 38's build: both would have logged a fast travel):\n");
		int jumpBefore = LogLines("solved again after a jump");
		const float *along = right;
		for (int hop = 0; hop < 2; hop++) {
			float d = hop ? 350.0f : 200.0f;
			SetState(2);
			for (int i = 0; i < 6; i++) {
				for (int k = 0; k < 3; k++)
					PlayerPos()[k] += along[k] * d / 6.0f;
				RunFrames(50);
			}
			SetState(0);
			RunFrames(1500);
			CHECK(LogLines("solved again after a jump") == jumpBefore && LogLines("deg forward about the spine's joint") == leanedBefore + 2,
			      "a hop of %.0f units in the air: no \"solved again after a jump\" line in the 1.5 s after landing, no new \"leaned\" line (%d, %d)",
			      d, LogLines("solved again after a jump") - jumpBefore, LogLines("deg forward about the spine's joint") - leanedBefore);
		}
		for (int k = 0; k < 3; k++)
			PlayerPos()[k] += along[k] * 200.0f;
		RunFrames(1500);
		CHECK(LogLines("solved again after a jump") == jumpBefore && LogLines("deg forward about the spine's joint") == leanedBefore + 2,
		      "a stall of 200 units in one frame on the ground: no line either in 1.5 s (%d, %d)",
		      LogLines("solved again after a jump") - jumpBefore, LogLines("deg forward about the spine's joint") - leanedBefore);
		/* The jump re-arms the solve (test 38); since test 40 its run starts from the solve
		 * before it, this ride's from the riding pose's coming (98.5%, kept), and with the hand
		 * raised after the jump (a short reading, as test 39's 92% after its second fast travel)
		 * no reading beats it: 3 s on, final, the line saying it stands. */
		printf("tilt: a jump of 1000 units in the ride (a door, a fast travel: the shapes stay held, no PostLoadGame), the hand raised after it: the solve from before the jump stands, final 3 s on (tests 38, 40):\n");
		int standsBefore = LogLines("the solve from before a jump of 1000 units (a door, a fast travel) stands");
		PlayerPos()[0] += 1000.0f;
		g_handRaised = true;
		RunFrames(3500);
		copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
		ExpectedTilt(Rw2, Pw2);
		memcpy(S, g_bodyNodes[6] + 0xA0, 12);   /* the shoulder went with the player */
		MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, S, mS);
		CHECK(LogLines("the solve from before a jump of 1000 units (a door, a fast travel) stands") == standsBefore + 1 && LogLines("solved again after a jump") == jumpBefore &&
		      LogLines("deg forward about the spine's joint") == leanedBefore + 2 && TiltedOff(S, mS, Rw2, Pw2) > 1.0f && LastLogNumber("(the grips at ") < 85.0f,
		      "3.5 s on: a line saying the solve from before the jump of 1000 units stands (%d), no \"leaned\" line (%d in all), the grips at %.0f%% then, the rider still held and written, leaning (the shoulder %.1f forward)",
		      LogLines("the solve from before a jump of 1000 units (a door, a fast travel) stands") - standsBefore, LogLines("deg forward about the spine's joint") - leanedBefore, LastLogNumber("(the grips at "), TiltedOff(S, mS, Rw2, Pw2));
		g_handRaised = false;
		Send(3, 1);   /* PostLoadGame: the ride starts afresh, the lean solved again */
		RunFrames(1500);
		copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
		ExpectedTilt(Rw2, Pw2);
		MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, S, mS);
		CHECK(TiltedOff(S, mS, Rw2, Pw2) > 1.0f && LogLines("deg forward about the spine's joint") == leanedBefore + 3,
		      "after a load the lean is solved again (the shoulder %.1f forward, %d \"leaned\" lines)", TiltedOff(S, mS, Rw2, Pw2), LogLines("deg forward about the spine's joint") - leanedBefore);
		RewriteIni("TorsoLean=-1", "TorsoLean=0");
		SetTilt(0.0f);
		RunFrames(300);
		SetTilt(30.0f);
		RunFrames(600);
	}

	if (g_haveParts) {
		/* Test 36's side lean turned off for a ride (TorsoSideLean=0, read again on getting
		 * on): the bars over as before, the spine's map rolls nothing, the twist stays. */
		printf("tilt: the upper body's side lean off (TorsoSideLean=0 for a ride):\n");
		RewriteIni("TorsoSideLean=0.25", "TorsoSideLean=0");
		SetTilt(0.0f);
		RunFrames(300);
		SetTilt(30.0f);
		RunFrames(600);
		g_turnOnSpot = -1.0472f;
		g_onFrame = TurnOnTheSpot;
		RunFrames(1500);
		float Rw2[9], Pw2[3], S[3], mS[3], hNow = *headNow, rt[3] = { cosf(hNow), -sinf(hNow), 0.0f };
		const uint8_t *copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
		ExpectedTilt(Rw2, Pw2);
		float bar = BarAngle(), roll = SpineRollToward(copyNow, rt, Rw2, bar);
		memcpy(S, g_bodyNodes[6] + 0xA0, 12);
		MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, S, mS);
		CHECK(fabsf(bar) > 8.0f && fabsf(roll) < 0.1f, "the bars over %.1f deg, the spine's map rolls %.2f deg: no side lean", bar, roll);
		CHECK(TiltedOff(S, mS, Rw2, Pw2) > 0.5f, "the shoulder still swung with the twist (%.2f off the tilt alone)", TiltedOff(S, mS, Rw2, Pw2));
		g_turnOnSpot = 1.0472f;
		RunFrames(1500);
		g_onFrame = NULL;
		*headNow = headingBefore;
		RunFrames(1000);
		RewriteIni("TorsoSideLean=0", "TorsoSideLean=0.25");
		SetTilt(0.0f);
		RunFrames(300);
		SetTilt(30.0f);
		RunFrames(600);
	}

	if (g_haveParts) {
		/* Test 39's HandPitch on the other hand: the arm's three nodes named and placed as the
		 * right arm's for a ride (mirrored across the bike's x = 0), the right hand's rotation
		 * the clips'. TorsoTwist and TorsoSideLean off for it (the fake's spine sits well off the
		 * bike's middle, so the mirrored shoulder is far below its joint and the twist would
		 * carry it out of reach), the bars over to the right for the hands to be solved. The
		 * knuckles up is about the bike's +x on both hands. */
		printf("tilt: the right hand pitched 10 deg up from the forearm (the arm mirrored to the right for a ride, HandPitch=10, the bars over to the right):\n");
		static const char *rightNames[3] = { "RArm_Hand [RHnd]", "RArm_UpperArm [RUar]", "RArm_ForeArm1 [RLar]" };
		uint8_t *leftNames[3];
		int rightBefore = LogLines("rider: the right arm solved");
		RewriteIni("HandPitch=0", "HandPitch=10");
		RewriteIni("TorsoTwist=0.75", "TorsoTwist=0");
		RewriteIni("TorsoSideLean=0.25", "TorsoSideLean=0");
		SetTilt(0.0f);
		RunFrames(300);
		for (int i = 0; i < 3; i++) {
			leftNames[i] = *(uint8_t **)(g_bodyNodes[5 + i] + 0x10);
			*(uint8_t **)(g_bodyNodes[5 + i] + 0x10) = NewString(rightNames[i]);
		}
		g_armRight = true;
		SyncFakeWorld();
		SetTilt(30.0f);
		RunFrames(300);
		g_turnOnSpot = 1.0472f;   /* turning right at 60 deg/s: the bars go over to the right */
		g_onFrame = TurnOnTheSpot;
		RunFrames(1500);
		{
			float Rw3[9], Pw3[3], Mh[9], Ar[9], Nr[9], Qr[9], qr[3], Er[3], Wrr[3], mEr[3], mWr[3], mW3r[3], G[3], mG[3];
			static const float gripR[3] = { 56.45f, 79.79f, 54.85f };   /* run.sh's Grip, the +x grip's centre: the right's own */
			const uint8_t *copyR = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
			float bar = BarAngle();
			ExpectedTilt(Rw3, Pw3);
			memcpy(Er, g_bodyNodes[7] + 0xA0, 12);
			memcpy(Wrr, g_bodyNodes[5] + 0xA0, 12);
			MapBone(g_bodyNodes[7], g_bodyBonesOriginal + 7 * 0x50, copyR + 7 * 0x50, Er, mEr);
			MapBone(g_bodyNodes[7], g_bodyBonesOriginal + 7 * 0x50, copyR + 7 * 0x50, Wrr, mWr);
			MapBone(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyR + 5 * 0x50, Wrr, mW3r);
			BoneRotationBefore(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyR + 5 * 0x50, Wrr, Rw3, Mh);
			BarTurnMap(bar, Ar, Nr, Qr, qr);
			{
				float AG[3], BG[3], NBG[3];
				Apply3(Ar, gripR, AG);
				for (int i = 0; i < 3; i++)
					BG[i] = AG[i] + ((const float *)(g_bonesOriginal + 0x40))[i];
				Apply3(Nr, BG, NBG);
				for (int i = 0; i < 3; i++)
					G[i] = NBG[i] + ((const float *)(g_comNode + 0xA0))[i];
			}
			MapBone(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyR + 5 * 0x50, G, mG);
			float clipsOff, up = HandAboveForearm(1, Mh, mEr, mWr, Rw3, Qr, &clipsOff), logged = LastLogNumber("its axis ");
			CHECK(bar < -8.0f && LogLines("rider: the right arm solved") == rightBefore + 1 && LogLines("right shoulder found, elbow found, hand found") >= 1,
			      "the bars over %.1f deg, the arm solved as the right one (%d \"right arm solved\" line)", bar, LogLines("rider: the right arm solved") - rightBefore);
			CHECK(fabsf(up - 10.0f) < 1.5f && fabsf(logged - up) < 0.3f && fabsf(clipsOff - 10.0f) > 10.0f,
			      "the right hand's long axis %.2f deg above the solved forearm's seen along the turned grip (10, within 1.5: the knuckles up as on the left; the arm's line says %.1f; the clips' hand %.1f)", up, logged, clipsOff);
			CHECK(TurnedOff(G, mG, Qr, qr, Rw3, Pw3) < 0.1f && Dist3(mWr, mW3r) < 0.1f, "the right grip's centre on the turned grip (%.3f off), the hand meeting the forearm at the wrist (%.3f apart)", TurnedOff(G, mG, Qr, qr, Rw3, Pw3), Dist3(mWr, mW3r));
		}
		g_turnOnSpot = -1.0472f;
		RunFrames(1500);
		g_onFrame = NULL;
		*headNow = headingBefore;
		SetTilt(0.0f);
		RunFrames(300);
		for (int i = 0; i < 3; i++)
			*(uint8_t **)(g_bodyNodes[5 + i] + 0x10) = leftNames[i];
		g_armRight = false;
		SyncFakeWorld();
		RewriteIni("HandPitch=10", "HandPitch=0");
		RewriteIni("TorsoTwist=0", "TorsoTwist=0.75");
		RewriteIni("TorsoSideLean=0", "TorsoSideLean=0.25");
		SetTilt(30.0f);
		RunFrames(600);
	}

	if (g_haveParts) {
		/* Test 39: after two fast travels the first reading of 95% was kept, final, 11.1 and 11.4
		 * deg against the riding pose's 14.6 at 100%. Each run of readings keeps the solve from
		 * the largest reach and is final on two agreeing readings of the riding pose (99% or
		 * more) or 3 s in. A ride whose grips read 100% throughout (the hand swung about the
		 * elbow to 99.9% of the reach), then one at 95% for its first second and 100% after. */
		printf("tilt: the lean's best reading kept (test 39): a ride whose grips read 100%% throughout, then one at 95%% for its first second and 100%% after:\n");
		RewriteIni("TorsoLean=0", "TorsoLean=-1");
		g_handReach = 0.999f;
		{
			/* Test 40: at five of test 39's six ride starts the first reading, 0.8 or 0.9 s in,
			 * caught the getting-on blending out (15.9 to 21.1 deg at 100%, 14.6 at 1.3 s), so the
			 * lean is first solved TorsoSolveFrom (1.3 s) into the ride. The other rides here
			 * keep test 39's half second, which their timings were made for. */
			RewriteIni("TorsoSolveFrom=0.5", "TorsoSolveFrom=1.3");
			SetTilt(0.0f);
			RunFrames(300);
			SetTilt(30.0f);
			RunFrames(2500);
			/* Read from the ride's own settings line on (the log's lines are counted from the
			 * file, which the ride before may still be adding to). */
			int lines = 0, finals = 0;
			float firstAt = LeanedSince("solved from 1.3 s into the ride (TorsoSolveFrom)", &lines, &finals);
			CHECK(lines >= 1 && firstAt >= 1.25f && firstAt < 1.6f && finals == 1,
			      "TorsoSolveFrom=1.3: the ride's first lean solved %.1f s in (1.3, the getting-on's blend past), %d \"leaned\" line%s, final by 2.5 s (%d)",
			      firstAt, lines, lines == 1 ? "" : "s", finals);
			RewriteIni("TorsoSolveFrom=1.3", "TorsoSolveFrom=0.5");
		}
		int finalBefore = LogLines("s into the ride, final");
		SetTilt(0.0f);
		RunFrames(300);
		SetTilt(30.0f);
		RunFrames(1500);
		float leanFull = LastLogNumber("the upper body leaned ");
		CHECK(LogLines("s into the ride, final") == finalBefore + 1 && LastLogNumber("% of the arms' reach with the bars straight (") > 99.0f,
		      "100%% throughout: the lean %.1f deg, final within 1.5 s (two readings of the riding pose that agree; %d \"final\" line)", leanFull, LogLines("s into the ride, final") - finalBefore);
		{
			/* Test 39's ride ended by a fast travel into Diamond City: its wrist line read 136.7
			 * and 161.0 deg, the grip at 101% and 116% of the reach: menu or loading frames. The
			 * ride's largest comes from the steady frames alone now. The arm raised up and back
			 * for half a second (the leaned shoulder further from the hand than the arm reaches),
			 * then back on the grip, then the ride's end. */
			float farShare, raisedShare, onOff = WristOffGrip();
			g_handFar = true;
			RunFrames(500);
			float farTurn = WristTurnNow(&farShare);
			g_handFar = false;
			RunFrames(500);
			/* Test 40: the Pip-Boy's map open for test 39's fast travel held the arms still for
			 * seconds at a time, and the left's 136.7 deg came at 101% of the reach, inside the
			 * band. A frame counts only with the clips holding the hand at the bars now, their
			 * wrist within 12 of the grip's centre (the riding clips put it 6.5 off; the fake's
			 * 6). The hand raised about the elbow for half a second (the fake's Pip-Boy raise,
			 * test 37's), still: the clips' wrist about 20 off the grip's centre, the grip well
			 * inside the band, so only that check leaves those frames out. */
			g_handReach = 0.0f;
			g_handRaised = true;
			RunFrames(500);
			float raisedTurn = WristTurnNow(&raisedShare), raisedOff = WristOffGrip();
			g_handRaised = false;
			g_handReach = 0.999f;
			RunFrames(500);
			int maxBefore = LogLines("wrist turned at most");
			SetTilt(0.0f);
			RunFrames(300);
			float maxTurn = LastLogNumber("wrist turned at most "), maxShare = LastLogNumber("the grip at ");
			CHECK(farShare > 105.0f && farTurn > maxTurn + 5.0f && maxShare >= 50.0f && maxShare <= 103.0f && LogLines("wrist turned at most") == maxBefore + 1,
			      "the arm up and back: the grip at %.0f%% of the reach from the leaned shoulder, the wrist turned %.1f deg; the ride's end line: at most %.1f deg, the grip at %.0f%% (the far frames left out)", farShare, farTurn, maxTurn, maxShare);
			CHECK(onOff < 12.0f && raisedOff > 15.0f && raisedOff < 30.0f && raisedShare >= 50.0f && raisedShare <= 103.0f && raisedTurn > maxTurn + 5.0f,
			      "the hand raised (test 40): the clips' wrist %.1f off the grip's centre (%.1f in the riding pose), the grip at %.0f%% of the reach, the wrist turned %.1f deg; the ride's end line's %.1f leaves those frames out", raisedOff, onOff, raisedShare, raisedTurn, maxTurn);
		}
		g_handReach = 0.952f;   /* 95%, a hair over its threshold */
		SetTilt(30.0f);
		RunFrames(1000);
		float leanShort = LastLogNumber("the upper body leaned ");
		int againBefore = LogLines("solved again: the riding pose read 100% (95%");
		finalBefore = LogLines("s into the ride, final");
		g_handReach = 0.999f;
		RunFrames(1500);
		float leanAfter = LastLogNumber("the upper body leaned ");
		CHECK(fabsf(leanShort - leanFull) > 1.0f && fabsf(leanAfter - leanFull) < 0.5f && LogLines("solved again: the riding pose read 100% (95%") == againBefore + 1 && LogLines("s into the ride, final") == finalBefore + 1,
		      "95%% for the first second: %.1f deg, kept till the riding pose read 100%% (\"solved again\"), then %.1f deg, final (the 100%% ride's %.1f, within 0.5)", leanShort, leanAfter, leanFull);
		{
			/* Test 40: in test 39 the grips read the riding pose's 100% only with the bike
			 * stopped, and both fast travels arrived moving, the grips at 92 to 95%, so the run
			 * after the jump, started empty, ended final on a moving reading (11 to 12 deg
			 * against the ride's 14.6). The run after a jump starts from the solve before it now.
			 * This ride's lean final at 100%, then a jump of 1000 units from a ground frame along
			 * the slope's contour (the ground stays at the feet) and the grips at 95% for 4 s: the
			 * solve from before the jump stands, final, the pose's lean within 0.1 deg of it. */
			printf("tilt: the lean through a jump (test 40): final at 100%%, a jump of 1000 units, the grips at 95%% for 4 s: the solve from before the jump stands, final:\n");
			float Rw4[9], Pw4[3], S4[3], mS4[3];
			const uint8_t *copy4 = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
			ExpectedTilt(Rw4, Pw4);
			memcpy(S4, g_bodyNodes[6] + 0xA0, 12);
			MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copy4 + 6 * 0x50, S4, mS4);
			float chordBefore = TiltedOff(S4, mS4, Rw4, Pw4);
			int standsBefore = LogLines("the solve from before a jump of 1000 units (a door, a fast travel) stands, 100% of the reach"), leanedBefore4 = LogLines("deg forward about the spine's joint");
			g_handReach = 0.952f;
			for (int k = 0; k < 3; k++)
				PlayerPos()[k] += right[k] * 1000.0f;
			RunFrames(4000);
			copy4 = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
			ExpectedTilt(Rw4, Pw4);
			memcpy(S4, g_bodyNodes[6] + 0xA0, 12);   /* the shoulder went with the player */
			MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copy4 + 6 * 0x50, S4, mS4);
			float chordAfter = TiltedOff(S4, mS4, Rw4, Pw4), poseLean = chordBefore > 0.01f ? leanAfter * chordAfter / chordBefore : 0.0f, stood = LastLogNumber("the upper body's lean final at ");
			CHECK(LogLines("the solve from before a jump of 1000 units (a door, a fast travel) stands, 100% of the reach") == standsBefore + 1 && LogLines("deg forward about the spine's joint") == leanedBefore4 &&
			      fabsf(stood - leanAfter) < 0.1f && fabsf(poseLean - leanAfter) < 0.1f && LastLogNumber("(the grips at ") > 94.5f,
			      "4 s on: \"the solve from before a jump of 1000 units ... stands, 100%%\" (%d line), final at %.1f deg (%.1f before the jump; the pose's %.2f by the shoulder's swing), no \"leaned\" line (%d), the grips at %.0f%% then",
			      LogLines("the solve from before a jump of 1000 units (a door, a fast travel) stands, 100% of the reach") - standsBefore, stood, leanAfter, poseLean, LogLines("deg forward about the spine's joint") - leanedBefore4, LastLogNumber("(the grips at "));
			g_handReach = 0.999f;
			RunFrames(1000);
			CHECK(LogLines("deg forward about the spine's joint") == leanedBefore4, "final: the riding pose back at 100%% solves nothing more (%d \"leaned\" lines)", LogLines("deg forward about the spine's joint") - leanedBefore4);
		}
		g_handReach = 0.0f;
		RewriteIni("TorsoLean=-1", "TorsoLean=0");
		SetTilt(0.0f);
		RunFrames(300);
		SetTilt(30.0f);
		RunFrames(600);
	}

	printf("tilt: a hold against a half-built skeleton (test 35: right after a save load the arms' shoulders were missing for 0.1 s): nothing held till the arms are whole, for a second at most:\n");
	{
		uint8_t **bodyList = *(uint8_t ***)(g_bodySkin + 0x28);
		bodyList[6] = NULL;   /* LArm_UpperArm's node gone from the body's skin: the left hand and elbow there, the shoulder not */
		SetTilt(0.0f);
		RunFrames(300);
		SetTilt(30.0f);
		RunFrames(500);
		CHECK(*(uint8_t **)(g_bodySkin + 0x40) == g_bodyData && *(int32_t *)(g_bodySkin + 0x08) == 1 && memcmp(g_bodyBones, g_bodyBonesOriginal, sizeof(g_bodyBonesOriginal)) == 0,
		      "half a second in: the body not held, its bone data untouched (the hold waits for the skeleton)");
		CHECK(*(uint8_t **)(g_handsSkin + 0x40) == g_handsData && *(int32_t *)(g_handsSkin + 0x08) == 1 && memcmp(g_handsBones, g_handsBonesOriginal, sizeof(g_handsBonesOriginal)) == 0,
		      "nothing written to the hands' skin either, its instance let go (references %d)", *(int32_t *)(g_handsSkin + 0x08));
		bodyList[6] = g_bodyNodes[6];   /* the game finished the skeleton */
		RunFrames(300);
		uint8_t *heldData = *(uint8_t **)(g_bodySkin + 0x40);
		CHECK(heldData && heldData != g_bodyData && *(int32_t *)(g_bodySkin + 0x08) == 2, "the node back within the second: the rider held on the next try (references %d)", *(int32_t *)(g_bodySkin + 0x08));
		if (heldData && heldData != g_bodyData) {
			float before[3], after[3], Rw3[9], Pw3[3];
			const uint8_t *copy3 = *(const uint8_t **)(heldData + 0x10);
			ExpectedTilt(Rw3, Pw3);
			WorldOfBone(g_bodyNodes[0], g_bodyBonesOriginal, probes[1], before);
			WorldOfBone(g_bodyNodes[0], copy3, probes[1], after);
			CHECK(TiltedOff(before, after, Rw3, Pw3) < 0.05f, "and tilted with the bike (%.3f off)", TiltedOff(before, after, Rw3, Pw3));
			if (g_haveParts) {
				/* The upper arm has its part in the arm's chain again: with the bars over, the
				 * shoulder swings with the upper body's twist, off the tilt alone. */
				float S[3], mS[3];
				g_turnOnSpot = -1.0472f;
				g_onFrame = TurnOnTheSpot;
				RunFrames(1500);
				copy3 = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
				ExpectedTilt(Rw3, Pw3);
				memcpy(S, g_bodyNodes[6] + 0xA0, 12);
				MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copy3 + 6 * 0x50, S, mS);
				CHECK(fabsf(BarAngle()) > 8.0f && TiltedOff(S, mS, Rw3, Pw3) > 0.5f,
				      "LArm_UpperArm has its part in the arm's chain again: the bars over %.1f deg, the shoulder swung with the twist (%.2f off the tilt alone)", BarAngle(), TiltedOff(S, mS, Rw3, Pw3));
				g_turnOnSpot = 1.0472f;
				RunFrames(1500);
				g_onFrame = NULL;
				*headNow = headingBefore;
				RunFrames(1000);
			}
		}
		printf("tilt: the skeleton still half built after a second: held as it is:\n");
		bodyList[6] = NULL;
		SetTilt(0.0f);
		RunFrames(300);
		SetTilt(30.0f);
		RunFrames(1300);
		heldData = *(uint8_t **)(g_bodySkin + 0x40);
		CHECK(heldData && heldData != g_bodyData && *(int32_t *)(g_bodySkin + 0x08) == 2, "held anyway after the second (references %d)", *(int32_t *)(g_bodySkin + 0x08));
		bodyList[6] = g_bodyNodes[6];
		SetTilt(0.0f);
		RunFrames(300);
		SetTilt(30.0f);
		RunFrames(600);
		CHECK(*(uint8_t **)(g_bodySkin + 0x40) != g_bodyData, "the node back and the rider held again for what follows");
	}

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
			RunFrames(100);
			/* A handover (test 33): the script names a fresh reference whose 3D isn't in yet; the
			 * old one stays at the lens meanwhile, and is parked once the new one's 3D is in. */
			SetLampRef(LAMP_REF2_FORMID);
			RunFrames(200);
			memcpy(rw, g_lampRefRoot + 0xA0, 12);
			roff = sqrtf((rw[0] - e[0]) * (rw[0] - e[0]) + (rw[1] - e[1]) * (rw[1] - e[1]) + (rw[2] - e[2]) * (rw[2] - e[2]));
			CHECK(roff < 0.1f, "handed over to a reference with no 3D yet: the old one still at the lens (%.3f off)", roff);
			*(uint8_t **)(g_lampRef2Loaded + 0x08) = g_lampRef2Root;   /* the new one's 3D in */
			RunFrames(200);
			memcpy(rw, g_lampRef2Root + 0xA0, 12);
			roff = sqrtf((rw[0] - e[0]) * (rw[0] - e[0]) + (rw[1] - e[1]) * (rw[1] - e[1]) + (rw[2] - e[2]) * (rw[2] - e[2]));
			CHECK(roff < 0.1f && ((const float *)(g_lampRefRoot + 0xA0))[2] < -10000.0f,
			      "the new one's 3D in: the new at the lens (%.3f off), the old parked far below (z %.0f)", roff, ((const float *)(g_lampRefRoot + 0xA0))[2]);
			*(uint8_t **)(g_lampRef2Loaded + 0x08) = NULL;
			SetLampRef(LAMP_REF_FORMID);
			RunFrames(200);
			/* The light placed Ahead units along the beam from the lens (test 34: inside the
			 * housing on fast frames, the beam blacked out); read again on getting on. */
			RewriteIni("Ahead=0", "Ahead=28");
			SetTilt(0.0f);
			RunFrames(300);
			SetTilt(30.0f);
			RunFrames(400);
			{
				/* 28 along the beam the root itself points (its +X, read back after the remount:
				 * the bars may sit at another angle now), from the lens placed before. */
				float ex2[3], rw2[3], rW2[9], axisNow[3];
				memcpy(rw2, g_lampRefRoot + 0xA0, 12);
				LoadRotation((const float *)(g_lampRefRoot + 0x70), rW2, g_rootTransposed);
				axisNow[0] = rW2[0]; axisNow[1] = rW2[3]; axisNow[2] = rW2[6];
				for (int i = 0; i < 3; i++)
					ex2[i] = e[i] + 28.0f * axisNow[i];
				/* The ride restarted for the setting: its tilt and bars settle a little differently,
				 * so the direction is checked loosely (within about 8 degrees: 400 ms into the remount
				 * it has read up to 3.3 with another run loading the machine), the distance tightly. */
				CHECK(Dist3(rw2, ex2) < 4.0f && fabsf(Dist3(rw2, e) - 28.0f) < 0.6f, "Ahead=28: the reference 28 along the beam from the lens (%.2f off the beam's line; %.1f from the lens)", Dist3(rw2, ex2), Dist3(rw2, e));
			}
			RewriteIni("Ahead=28", "Ahead=0");
			SetTilt(0.0f);
			RunFrames(300);
			SetTilt(30.0f);
			RunFrames(300);
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
		CHECK(decalCopy && memcmp(*(uint8_t **)(decalCopy + 0x10), *(uint8_t **)(bodyCopy + 0x10), 12 * 0x50) == 0,
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
	/* The rays' test ray tried again on level ground at the feet first: since the jump of 1000
	 * units off the slope's contour and the load after it, the test ray beside the bike has
	 * found nothing, and a failed one waits 3 s, so whether the dip's first tenth of a second
	 * had rays hung on that wait's phase (the rides test 40 added moved it past the check). */
	FlatGround();
	RunFrames(3100);
	if (g_haveParts) {   /* the bump lift and the lift rate on for this test (off in the run's INI: the other checks expect the filtered lift alone) */
		RewriteIni("BumpMax=0", "BumpMax=30");
		RewriteIni("LiftRate=0", "LiftRate=120");
		SetTilt(0.0f);
		RunFrames(300);
		SetTilt(30.0f);
		RunFrames(600);
	}
	g_groundZ = PlayerPos()[2] + 10.0f;
	RunFrames(100);
	SeatInBone(g_bonesOriginal, seatBefore);
	SeatInBone(g_bones, seatNow);
	float lifted = sqrtf((seatNow[0] - seatBefore[0]) * (seatNow[0] - seatBefore[0]) + (seatNow[1] - seatBefore[1]) * (seatNow[1] - seatBefore[1]) + (seatNow[2] - seatBefore[2]) * (seatNow[2] - seatBefore[2]));
	CHECK(g_picks == 0 || (lifted > 9.0f && lifted < 10.6f), "a tenth of a second in: lifted %.1f already (the bump fills the wheel's deficit at once, under LiftRate 120 a second: 12 would be allowed; test 34's rise in a frame launched the bike)", lifted);
	RunFrames(250);
	SeatInBone(g_bones, seatNow);
	lifted = sqrtf((seatNow[0] - seatBefore[0]) * (seatNow[0] - seatBefore[0]) + (seatNow[1] - seatBefore[1]) * (seatNow[1] - seatBefore[1]) + (seatNow[2] - seatBefore[2]) * (seatNow[2] - seatBefore[2]));
	CHECK(g_picks == 0 || lifted < 10.6f, "0.35 s in: %.1f, never over the step while it lasts (review: the bump lift settling slower than the filtered lift rose overshot by a fifth)", lifted);
	RunFrames(450);
	SeatInBone(g_bones, seatNow);
	lifted = sqrtf((seatNow[0] - seatBefore[0]) * (seatNow[0] - seatBefore[0]) + (seatNow[1] - seatBefore[1]) * (seatNow[1] - seatBefore[1]) + (seatNow[2] - seatBefore[2]) * (seatNow[2] - seatBefore[2]));
	CHECK(g_picks == 0 || (lifted > 9.0f && lifted < 11.5f), "the bike lifted %.1f (10), level", lifted);
	g_groundZ = PlayerPos()[2] - 10.0f;   /* a crest: the ground below the contact */
	RunFrames(800);
	SeatInBone(g_bones, seatNow);
	lifted = sqrtf((seatNow[0] - seatBefore[0]) * (seatNow[0] - seatBefore[0]) + (seatNow[1] - seatBefore[1]) * (seatNow[1] - seatBefore[1]) + (seatNow[2] - seatBefore[2]) * (seatNow[2] - seatBefore[2]));
	CHECK(lifted < 0.5f, "on a crest (the ground 10 below): not lowered (%.1f)", lifted);
	g_groundZ = PlayerPos()[2];
	if (g_haveParts) {
		/* A 30 unit step (a wheel radius, BumpMax): the lift paced by LiftRate (test 35: the
		 * bump lift's +34 in a quarter second at 900 units a second jumped the bike). */
		printf("tilt: a 30 unit step under the wheels (BumpMax 30): the lift rises at LiftRate 120 a second:\n");
		RunFrames(600);
		g_cappedSeconds = 0.0;   /* the time this run's frames took, as the plugin caps a frame (a frame is 5 to 7 ms here: 0.1 s is 15 to 20 of them, plus a part of one; review: a stall over 50 ms counts as 50) */
		g_groundZ = PlayerPos()[2] + 30.0f;
		RunFrames(100);
		float took = (float)g_cappedSeconds;
		SeatInBone(g_bones, seatNow);
		lifted = sqrtf((seatNow[0] - seatBefore[0]) * (seatNow[0] - seatBefore[0]) + (seatNow[1] - seatBefore[1]) * (seatNow[1] - seatBefore[1]) + (seatNow[2] - seatBefore[2]) * (seatNow[2] - seatBefore[2]));
		CHECK(g_picks == 0 || (lifted > 120.0f * took - 3.0f && lifted < 120.0f * took + 2.0f && lifted < 20.0f),
		      "a tenth of a second in (%.3f s): lifted %.1f (%.1f at 120 a second; the deficit would have it at 30 at once)", took, lifted, 120.0f * took);
		RunFrames(150);
		SeatInBone(g_bones, seatNow);
		lifted = sqrtf((seatNow[0] - seatBefore[0]) * (seatNow[0] - seatBefore[0]) + (seatNow[1] - seatBefore[1]) * (seatNow[1] - seatBefore[1]) + (seatNow[2] - seatBefore[2]) * (seatNow[2] - seatBefore[2]));
		CHECK(g_picks == 0 || (lifted > 27.0f && lifted < 30.6f), "a quarter second in: lifted %.1f (30 over 0.25 s), never over the step", lifted);
		RunFrames(600);
		SeatInBone(g_bones, seatNow);
		lifted = sqrtf((seatNow[0] - seatBefore[0]) * (seatNow[0] - seatBefore[0]) + (seatNow[1] - seatBefore[1]) * (seatNow[1] - seatBefore[1]) + (seatNow[2] - seatBefore[2]) * (seatNow[2] - seatBefore[2]));
		CHECK(g_picks == 0 || (lifted > 29.0f && lifted < 31.0f), "the bike lifted %.1f (30), level", lifted);
		g_groundZ = PlayerPos()[2];
		RunFrames(800);
		RewriteIni("BumpMax=30", "BumpMax=0");
		RewriteIni("LiftRate=120", "LiftRate=0");
		SetTilt(0.0f);
		RunFrames(300);
		SetTilt(30.0f);
		RunFrames(600);
	}
	if (g_haveParts) {
		/* Test 36's suspension (the bumps no longer launch the bike, but it was "still stiff,
		 * nothing like suspension"): the wheels follow the ground within SuspTravel of the frame,
		 * the frame's lift follows the wheels' line through a spring and damper (2 Hz, a damping
		 * ratio of 0.5: a step met with a rebound of a sixth of it) instead of the filter, and the
		 * bump lift takes only what the travel can't. The bump and the rate on as the game has
		 * them; the old checks above and below keep their first-order numbers (Suspension=0). */
		printf("tilt: a suspension (Suspension=1: 2 Hz, damping 0.5, travel 10; the bump and the rate on): a 10 unit step under both wheels, the frame overshoots and settles:\n");
		RewriteIni("Suspension=0", "Suspension=1");
		RewriteIni("BumpMax=0", "BumpMax=30");
		RewriteIni("LiftRate=0", "LiftRate=120");
		SetTilt(0.0f);
		RunFrames(300);
		SetTilt(30.0f);
		RunFrames(600);
		g_groundZ = PlayerPos()[2] + 10.0f;
		float peak = 0.0f, peakAt = 0.0f, peakF = 0.0f, peakR = 0.0f;
		for (int i = 0; i < 10; i++) {   /* the first half second, sampled every 50 ms: the rebound's peak (at 0.29 s for 2 Hz damped 0.5) */
			RunFrames(50);
			SeatInBone(g_bones, seatNow);
			lifted = sqrtf((seatNow[0] - seatBefore[0]) * (seatNow[0] - seatBefore[0]) + (seatNow[1] - seatBefore[1]) * (seatNow[1] - seatBefore[1]) + (seatNow[2] - seatBefore[2]) * (seatNow[2] - seatBefore[2]));
			if (lifted > peak) {
				peak = lifted;
				peakAt = 0.05f * (float)(i + 1);
				peakF = WheelTravel(0);
				peakR = WheelTravel(1);
			}
		}
		CHECK(g_picks == 0 || (peak > 10.5f && peak < 12.5f), "the seat's peak in the first half second: %.1f (the sample %.2f s in; the 10 step and a rebound of a sixth of it: 11.6)", peak, peakAt);
		CHECK(g_picks == 0 || (peakF < 1.5f && peakR < 1.5f && peakF > 10.0f - peak - 0.5f && peakR > 10.0f - peak - 0.5f),
		      "at the peak the wheels are back near the frame, their extension over SuspExtend (0.1) lagging the overshoot (test 38; within 0.03 s they sat at the overshoot, %.1f): front %+.1f, rear %+.1f", 10.0f - peak, peakF, peakR);
		RunFrames(1000);
		SeatInBone(g_bones, seatNow);
		lifted = sqrtf((seatNow[0] - seatBefore[0]) * (seatNow[0] - seatBefore[0]) + (seatNow[1] - seatBefore[1]) * (seatNow[1] - seatBefore[1]) + (seatNow[2] - seatBefore[2]) * (seatNow[2] - seatBefore[2]));
		CHECK(g_picks == 0 || (lifted > 9.5f && lifted < 10.5f), "settled by 1.5 s: the seat %.1f up (10)", lifted);
		CHECK(g_picks == 0 || (fabsf(WheelTravel(0)) < 1.0f && fabsf(WheelTravel(1)) < 1.0f), "the wheels back against the frame: front %+.1f, rear %+.1f", WheelTravel(0), WheelTravel(1));
		float grown = *(float *)(g_partBones[0] + 0x0C) - 31.0f;
		CHECK(g_picks == 0 || fabsf(grown - WheelMove(0)) < 0.3f, "the front wheel's culling sphere grown by its axle's move (%.1f for %.1f)", grown, WheelMove(0));
		g_groundZ = PlayerPos()[2];
		RunFrames(1500);
		printf("tilt: a step of 8 under the rear wheel only (a shelf of radius 30 over the rear axle; the front axle 136 ahead): the rear wheel rises SuspCompressRear (4) into the frame at most, its mudguard being on the frame (test 37):\n");
		g_shelfOn = true;
		g_shelfHeight = 8.0f;
		g_shelfAhead = -36.7f;
		g_shelfRadius = 30.0f;
		const float steer[3] = { 0.0f, -0.4f, 0.9165f }, up[3] = { 0.0f, 0.0f, 1.0f };   /* the run's SteerAxis (a unit vector) and the bike's up */
		float peakRear = 0.0f, frontAtRear = 0.0f, rearOff = 0.0f;
		for (int i = 0; i < 10; i++) {
			RunFrames(50);
			float r = WheelTravel(1);
			if (r > peakRear) {
				peakRear = r;
				rearOff = MoveOffAxis(1, g_axles[1], up);
			}
		}
		frontAtRear = WheelTravel(0);
		CHECK(g_picks == 0 || (peakRear > 3.5f && peakRear < 4.2f), "the rear wheel pushed up into the frame by %.1f at most in the half second (the 8 step, capped at 4; the frame takes the rest)", peakRear);
		CHECK(g_picks == 0 || rearOff < 0.3f, "the rear wheel's move runs along the bike's up (%.2f off it; test 38)", rearOff);
		CHECK(g_picks == 0 || fabsf(frontAtRear) < 1.0f, "the front wheel with the frame at the half second (%+.1f)", frontAtRear);
		g_shelfOn = false;
		g_shelfRadius = 60.0f;
		g_groundZ = PlayerPos()[2];
		RunFrames(1500);
		printf("tilt: a step of 8 under the front wheel only (a shelf over the front axle): the front wheel takes it within its travel, the frame the wheel line's share:\n");
		g_shelfOn = true;
		g_shelfHeight = 8.0f;
		g_shelfAhead = 99.6f;
		float peakFront = 0.0f, forkAtPeak = 0.0f, wheelOff = 0.0f, forkOff = 0.0f, wheelY = 0.0f, forkY = 0.0f, firstFront = 0.0f;
		for (int i = 0; i < 10; i++) {
			RunFrames(50);
			float f = WheelTravel(0);
			if (i == 0)
				firstFront = f;
			if (f > peakFront) {
				float d[3];
				peakFront = f;
				forkAtPeak = PartTravel(3, g_axles[0]);
				wheelOff = MoveOffAxis(0, g_axles[0], steer);
				forkOff = MoveOffAxis(3, g_axles[0], steer);
				PartMove(0, g_axles[0], d);
				wheelY = d[1];
				PartMove(3, g_axles[0], d);
				forkY = d[1];
			}
		}
		float rearB = WheelTravel(1);
		SeatInBone(g_bones, seatNow);
		float seatB = sqrtf((seatNow[0] - seatBefore[0]) * (seatNow[0] - seatBefore[0]) + (seatNow[1] - seatBefore[1]) * (seatNow[1] - seatBefore[1]) + (seatNow[2] - seatBefore[2]) * (seatNow[2] - seatBefore[2]));
		CHECK(g_picks == 0 || (peakFront > 5.0f && peakFront < 8.3f), "the front wheel pushed up into the frame by %.1f at most in the half second (the 8 step, within the travel of 10; less as the pitch takes the frame onto it)", peakFront);
		CHECK(g_picks == 0 || fabsf(forkAtPeak - peakFront) < 0.5f, "the lower fork rides with the front wheel's travel: %.1f up at the wheel's peak (test 38)", forkAtPeak);
		CHECK(g_picks == 0 || (wheelOff < 0.3f && forkOff < 0.3f && fabsf(wheelY + 0.4f / 0.9165f * peakFront) < 0.3f && fabsf(forkY + 0.4f / 0.9165f * forkAtPeak) < 0.3f),
		      "both moves run along the steering axis (0, -0.4, 0.9165), the move's z the offset (test 38: along z the raked fork left its tubes' line): %.2f and %.2f off the axis, y %.2f and %.2f (%.2f)",
		      wheelOff, forkOff, wheelY, forkY, -0.4f / 0.9165f * peakFront);
		CHECK(g_picks == 0 || firstFront > 3.5f, "the step up taken at once: the front wheel %.1f up at the first sample, 50 ms in (compression within 0.03 s; SuspExtend eases the extension alone: test 38)", firstFront);
		CHECK(g_picks == 0 || fabsf(rearB) < 1.0f, "the rear wheel stays with the frame (%+.1f)", rearB);
		CHECK(g_picks == 0 || (seatB > 1.0f && seatB < 5.0f), "the frame lifted %.1f at the half second (the wheel line at the contact: 8 x 36.7/136.3 = 2.2)", seatB);
		g_shelfOn = false;
		g_groundZ = PlayerPos()[2];
		RunFrames(1500);
		printf("tilt: a step of 25 under the front wheel only: the front wheel's travel saturates at 10 and the frame takes the rest:\n");
		g_shelfOn = true;
		g_shelfHeight = 25.0f;
		peakFront = 0.0f;
		for (int i = 0; i < 10; i++) {
			RunFrames(50);
			float f = WheelTravel(0);
			if (f > peakFront)
				peakFront = f;
		}
		SeatInBone(g_bones, seatNow);
		float seatC = sqrtf((seatNow[0] - seatBefore[0]) * (seatNow[0] - seatBefore[0]) + (seatNow[1] - seatBefore[1]) * (seatNow[1] - seatBefore[1]) + (seatNow[2] - seatBefore[2]) * (seatNow[2] - seatBefore[2]));
		CHECK(g_picks == 0 || (peakFront > 9.0f && peakFront < 10.2f), "the front wheel's travel saturates at %.1f (10)", peakFront);
		CHECK(g_picks == 0 || seatC > seatB + 2.0f, "the frame takes the rest: the seat %.1f up at the half second (%.1f with the 8 step; the bump lift the 15 over the travel, then the pitch and the wheel line)", seatC, seatB);
		g_shelfOn = false;
		g_shelfHeight = g_shelfAhead = 0.0f;
		g_groundZ = PlayerPos()[2];
		RunFrames(1500);
		/* Test 38: "forks were getting out of tubes" (at -10 the sliders were off the stanchions,
		 * whose overlap with them is 8 at rest) and "the look of it was a bit too much, like there
		 * was no weight behind it" (each wheel followed its ray within 0.03 s both ways). SuspDroop
		 * (4): a wheel drops below the frame by that at most; SuspExtend (0.1): it extends over
		 * that long, compressing within 0.03 s still; and the frame sinks by the droop at most
		 * where the wheels' line runs below the capsule's contact. */
		printf("tilt: a hole of 30 under the front wheel (a disc of radius 60 over the front axle; SuspDroop 4, SuspExtend 0.1; test 38): the wheel drops to the droop, not 10, and takes longer than 0.1 s to get there:\n");
		g_shelfOn = true;
		g_shelfHeight = -30.0f;
		g_shelfAhead = 99.6f;
		LARGE_INTEGER qf, q0, q1;
		QueryPerformanceFrequency(&qf);
		QueryPerformanceCounter(&q0);
		float fell = -1.0f;
		for (int i = 0; i < 60 && fell < 0.0f; i++) {   /* sampled every 10 ms or so, by the wall clock (the plugin's own frame times): when the front wheel's offset first reaches -3.5 */
			RunFrames(10);
			QueryPerformanceCounter(&q1);
			if (WheelTravel(0) < -3.5f)
				fell = (float)(q1.QuadPart - q0.QuadPart) / (float)qf.QuadPart;
		}
		CHECK(g_picks == 0 || (fell > 0.12f && fell < 0.5f), "the front wheel's offset reached -3.5 after %.2f s (within 0.5 of the droop: 0.21 at SuspExtend 0.1; 0.06 at the old 0.03)", fell);
		RunFrames(1000);
		CHECK(g_picks == 0 || fabsf(WheelTravel(0) + 4.0f) < 0.3f, "the front wheel hangs %.1f below the frame (-4, the droop; -10 before test 38)", WheelTravel(0));
		CHECK(g_picks == 0 || (WheelTravel(1) < 0.3f && WheelTravel(1) > -4.3f), "the rear within its droop (%+.1f: the frame sunk 4 and pitched 12 deg down, the line at the contact 8 below)", WheelTravel(1));
		g_shelfOn = false;
		g_shelfHeight = g_shelfAhead = 0.0f;
		g_groundZ = PlayerPos()[2];
		RunFrames(1500);
		printf("tilt: the ground 10 below the contact under both wheels (a crest, a bump under the rider; test 38: both wheels hung at -10 with the frame held at the contact): the frame sinks by the droop (4) and no further, the wheels at their droop:\n");
		g_groundZ = PlayerPos()[2] - 10.0f;
		RunFrames(1000);
		CHECK(g_picks == 0 || (SeatLift() < -3.5f && SeatLift() > -4.5f), "the frame %.1f down (-4)", SeatLift());
		CHECK(g_picks == 0 || (fabsf(WheelTravel(0) + 4.0f) < 0.3f && fabsf(WheelTravel(1) + 4.0f) < 0.3f), "the wheels %+.1f and %+.1f against it (-4: the ground 6 further down is out of their reach)", WheelTravel(0), WheelTravel(1));
		g_groundZ = PlayerPos()[2];
		RunFrames(1500);
		printf("tilt: the wheel rays' word lost with the bike lifted 30 and pitched 20 deg (a 20 deg slope 30 above the contact, then nothing within the rays' reach; test 38: backing off a station wagon the rays missed, the lift fell to 0 under the held pitch and the rear wheel went under the ground): the lift held with the pitch for 3 s, then eased off:\n");
		SetNormalTowards(back, 20.0f);
		SetGroundTowards(back, 20.0f);
		g_groundZ = PlayerPos()[2] + 30.0f;
		RunFrames(1500);
		AppliedRotation(R);
		float liftOn = SeatLift(), pitchOn = acosf(R[8] > 1.0f ? 1.0f : R[8]) * DEG;
		g_groundZ = PlayerPos()[2] - 300.0f;   /* the rays end 160 below the feet: no word */
		RunFrames(500);
		AppliedRotation(R);
		float liftHeld = SeatLift(), pitchHeld = acosf(R[8] > 1.0f ? 1.0f : R[8]) * DEG;
		CHECK(g_picks == 0 || (liftOn > 27.0f && liftOn < 33.0f && pitchOn > 17.0f && pitchOn < 23.0f), "lifted %.1f and pitched %.1f deg on the rays' word (30, 20)", liftOn, pitchOn);
		CHECK(g_picks == 0 || (fabsf(liftHeld - liftOn) < 3.0f && fabsf(pitchHeld - pitchOn) < 1.0f), "half a second without a word: the lift held at %.1f with the pitch at %.1f deg", liftHeld, pitchHeld);
		RunFrames(2000);
		CHECK(g_picks == 0 || fabsf(SeatLift() - liftOn) < 3.0f, "2.5 s without a word: the lift still held at %.1f with the pitch (3 s, a slow back-off's worth; the first cut's 1.5 s was tight)", SeatLift());
		RunFrames(2000);
		CHECK(g_picks == 0 || SeatLift() < 5.0f, "4.5 s without a word: the lift eased off to %.1f (under 5: a tunnel's ceiling throws the rays' hits away for as long as it lasts, and a stale lift would float the bike through it)", SeatLift());
		SetNormal(0.0f, 0.0f, 1.0f);
		FlatGround();
		RunFrames(1500);
		/* Test 39, 01:34:11.5: a radstag in front of the bike, the front wheel's ray hit its
		 * capsule 107 above the feet ("SkeletonExport, layer 30"), and the pitch's target read
		 * 40 to 44 with a lift of 33 for about 0.6 s: the bike reared up at it. The ground's
		 * rays pass through actors now (the face rays still stop at one: the input hook's
		 * tests, where the throttle casts them). */
		printf("tilt: an actor over the front wheel's ray spot (a disc of radius 40 over the front axle, layer 30, \"SkeletonExport\", its top 100 above the feet), the ground flat under it, riding at 100 a second (test 39's radstag): the wheels' rays pass through it, the bike level and not lifted:\n");
		g_shelfOn = true;
		g_shelfHeight = 100.0f;
		g_shelfAhead = 99.6f;
		g_shelfRadius = 40.0f;
		g_shelfLayer = 30;
		g_shelfWhat = g_actorObj;
		int passedBefore = LogLines("rays: a ground ray passed through SkeletonExport (layer 30)");
		int wheelsNamedBefore = LogLines("(SkeletonExport, layer 30), the rear");
		g_rideSpeed = 100.0f;
		g_rideSlope = 0.0f;
		g_onFrame = RideAlong;
		float worstPitch = 0.0f, worstLift = 0.0f;
		for (int i = 0; i < 10; i++) {   /* a second, sampled every 0.1 s (the bike reared up within 0.15 s in test 39) */
			RunFrames(100);
			AppliedRotation(R);
			float p = acosf(R[8] > 1.0f ? 1.0f : R[8]) * DEG, l = fabsf(SeatLift());
			worstPitch = p > worstPitch ? p : worstPitch;
			worstLift = l > worstLift ? l : worstLift;
		}
		g_onFrame = NULL;
		g_rideSpeed = 0.0f;
		CHECK(g_picks == 0 || (worstPitch < 2.0f && worstLift < 3.0f), "the bike's pitch %.1f deg at most, the lift %.1f at most (within 2 and 3 of level; through the actor's top the front ray would read 100 up: 36 deg, a lift of 27)", worstPitch, worstLift);
		CHECK(g_picks == 0 || (LogLines("rays: a ground ray passed through SkeletonExport (layer 30)") > passedBefore && LogLines("(SkeletonExport, layer 30), the rear") == wheelsNamedBefore),
		      "the log: a ground ray passed through SkeletonExport (layer 30), an actor, and no wheels' rays line names it");
		g_shelfOn = false;
		g_shelfHeight = g_shelfAhead = 0.0f;
		g_shelfRadius = 60.0f;
		g_shelfLayer = 1;
		g_shelfWhat = NULL;
		FlatGround();
		RunFrames(1500);
		/* Review of test 40's first build: each actor passed takes one of a ray's 8 tries since
		 * test 39, and a ray that ran out of them counted the last point it passed as a hit, an
		 * actor's. Twenty actor surfaces 5 apart (5 to 100 up) over the front wheel's spot, the
		 * bike standing: the front ray runs out on them, and that is no hit now (no word from
		 * the wheels that frame), where the 8th surface, 65 up, read as the ground: 25 deg of
		 * pitch and a lift of 17. */
		printf("tilt: twenty actor surfaces (layer 30, 5 apart, 5 to 100 up) over the front wheel's spot, standing: the front ray runs out of its tries on them: no hit, the bike level:\n");
		{
			float h = PlayerHeading();
			g_pilePoint[0] = PlayerPos()[0] + sinf(h) * 99.6f;
			g_pilePoint[1] = PlayerPos()[1] + cosf(h) * 99.6f;
		}
		g_pileCount = 20;
		g_pileLayer = 30;
		g_pileWhat = g_actorObj;
		worstPitch = worstLift = 0.0f;
		for (int i = 0; i < 10; i++) {
			RunFrames(100);
			AppliedRotation(R);
			float p = acosf(R[8] > 1.0f ? 1.0f : R[8]) * DEG, l = fabsf(SeatLift());
			worstPitch = p > worstPitch ? p : worstPitch;
			worstLift = l > worstLift ? l : worstLift;
		}
		CHECK(g_picks == 0 || (worstPitch < 2.0f && worstLift < 3.0f), "the bike's pitch %.1f deg at most, the lift %.1f at most over a second (within 2 and 3 of level; the 8th surface taken for the ground would read 25 deg, a lift of 17)", worstPitch, worstLift);
		g_pileCount = 0;
		g_pileLayer = 4;
		g_pileWhat = NULL;
		RunFrames(500);
		RewriteIni("Suspension=1", "Suspension=0");
		RewriteIni("BumpMax=30", "BumpMax=0");
		RewriteIni("LiftRate=120", "LiftRate=0");
		SetTilt(0.0f);
		RunFrames(300);
		SetTilt(30.0f);
		RunFrames(600);
	}

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
		CHECK(decalCopy && decalCopy != g_bodyData && *(int32_t *)(g_decalSkin + 0x08) == 1 && memcmp(*(uint8_t **)(decalCopy + 0x10), g_bodyBonesOriginal, 12 * 0x50) == 0,
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
	/* Test 37: the region cache's flush every 30 s had the next sync re-query every region
	 * the rider's walk touches at once (88, 12-16 ms). Each entry lapses on its own now, 30 s
	 * and a stagger after it was read (the cache was last emptied when the bike's skins went,
	 * a second or two ago): 40 s of this ride, the rider held, see a third of them lapse and
	 * read again, a few in a sync. The plugin's VirtualQuery calls are counted through its
	 * import table, the most in any one frame. */
	printf("tilt: 40 s on the bike with the rider held: the region cache's entries lapse one by one, not all in one sync (test 37):\n");
	CHECK(g_vqHooked, "the plugin's VirtualQuery import counted");
	g_vqFrameMax = 0;
	int queries0 = g_vqCalls;
	RunFrames(40000);
	CHECK(g_vqFrameMax <= 25 && g_vqCalls - queries0 >= 1, "no frame's sync re-queried more than 25 regions (the most in one frame %d, %d over the 40 s; the old flush gave 88 at once)",
	      g_vqFrameMax, g_vqCalls - queries0);
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
		/* Test 38's wrist roll with no Grip= in this run's parts: the old pivot, the hand's own
		 * node, which stays on the turned grip while the hand rolls about it; the parts line
		 * says so. */
		printf("rider switches: the bars turned with no Grip= in the parts (the wrist rolls about the hand's node, as before test 38):\n");
		g_turnOnSpot = -1.0472f;   /* turning left at 60 deg/s: the bars go over */
		g_onFrame = TurnOnTheSpot;
		RunFrames(1500);
		g_onFrame = NULL;
		float barNow = BarAngle(), A[9], N[9], Q[9], q[3], Mh[9], Qt[9], Dh[9], rollAxis[3], W[3], mW[3];
		const uint8_t *copyNow = *(const uint8_t **)(*(uint8_t **)(g_bodySkin + 0x40) + 0x10);
		BarTurnMap(barNow, A, N, Q, q);
		ExpectedTilt(Rw, Pw);
		memcpy(W, g_bodyNodes[5] + 0xA0, 12);
		MapBone(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, W, mW);
		BoneRotationBefore(g_bodyNodes[5], g_bodyBonesOriginal + 5 * 0x50, copyNow + 5 * 0x50, W, Rw, Mh);
		for (int i = 0; i < 3; i++)
			for (int j = 0; j < 3; j++)
				Qt[i * 3 + j] = Q[j * 3 + i];
		MulM3(Qt, Mh, Dh);
		float roll = RotationAngle(Dh, rollAxis);
		CHECK(fabsf(barNow) > 8.0f && roll > 1.0f && TurnedOff(W, mW, Q, q, Rw, Pw) < 0.1f && LogLines("the wrist rolls about the hand's node") == 1,
		      "the bars over %.1f deg, the hand rolled %.1f deg: the wrist itself stays on the turned grip (%.3f off the bars' turn of it), the parts line says the wrist rolls about the hand's node",
		      barNow, roll, TurnedOff(W, mW, Q, q, Rw, Pw));
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

/* ---- Mode 9: loads into a ride (finding 2 of test 40) -------------------------------------
 * After an in-game load on the bike the lean was lost: the bike upright through the turns, the
 * rider sitting up, the bars and the wheels still going; getting off and on fixed it, and the
 * log was gone with a restart. These ride a circle at 400 units/s on a 300 turn radius and load
 * (PostLoadGame) in it, each time with the 3D the load hands over changed in one way. */

/* The log of the session before: a marker where the plugin will open its log (its rule: in My
 * Documents\My Games\Fallout4\F4SE if it can be written there, else next to the DLL), written
 * before the DLL is loaded; it must find it in CMB_Slope_prev.log. */
static char g_markerPath[MAX_PATH];
static void WriteLogMarker(const char *dllPath)
{
	char path[MAX_PATH];
	FILE *f = NULL;
	HMODULE shell = LoadLibraryA("shell32.dll");
	HRESULT (WINAPI *folder)(HWND, int, HANDLE, DWORD, LPSTR) = shell ? (HRESULT (WINAPI *)(HWND, int, HANDLE, DWORD, LPSTR))(void *)GetProcAddress(shell, "SHGetFolderPathA") : NULL;
	if (folder && folder(NULL, 0x8005, NULL, 0, path) >= 0) {   /* CSIDL_PERSONAL | CSIDL_FLAG_CREATE, as the plugin asks */
		strncat(path, "\\My Games\\Fallout4\\F4SE", sizeof(path) - strlen(path) - 1);
		CreateDirectoryA(path, NULL);
		strncat(path, "\\CMB_Slope.log", sizeof(path) - strlen(path) - 1);
		f = fopen(path, "w");
	}
	if (!f && GetFullPathNameA(dllPath, sizeof(path), path, NULL)) {
		char *dot = strrchr(path, '.');
		if (dot)
			strcpy(dot, ".log");
		f = fopen(path, "w");
	}
	if (!f)
		return;
	fputs("12:00:00.000 the session before's last line (fake_game mode 9's marker)\n", f);
	fclose(f);
	snprintf(g_markerPath, sizeof(g_markerPath), "%s", path);
}
static void LogRotationTests(void)
{
	char prev[MAX_PATH + 16], line[512] = "";
	printf("the log of the session before:\n");
	size_t n = strlen(g_markerPath);
	snprintf(prev, sizeof(prev), "%.*s_prev.log", n > 4 ? (int)(n - 4) : 0, g_markerPath);
	FILE *f = n ? fopen(prev, "rb") : NULL;
	bool marker = f && fgets(line, sizeof(line), f) && strstr(line, "fake_game mode 9's marker");
	if (f)
		fclose(f);
	CHECK(marker, "the marker written before the load is in CMB_Slope_prev.log");
	f = OpenLog();
	line[0] = 0;
	if (f) {
		if (!fgets(line, sizeof(line), f))
			line[0] = 0;
		fclose(f);
	}
	CHECK(strstr(line, "the session before's log kept as CMB_Slope_prev.log") && strstr(line, ", started 20"),
	      "the new log's first line gives the day and says so: %.160s", line);
}

static void CircleRide(float dt)
{
	float *head = (float *)(g_player + 0xC8);
	PlayerPos()[0] += sinf(*head) * 400.0f * dt;
	PlayerPos()[1] += cosf(*head) * 400.0f * dt;
	*head += 0.3f;   /* the game asks for more turn than the radius allows: the plugin clamps it */
}
/* The game's re-attached armor after a load: a new shape and skin instance for the body, on the
 * original (shared) bone data and the same skeleton nodes; the old one detached. */
static void ReplaceBody(void)
{
	uint8_t *old = g_bodyShape, *oldSkin = g_bodySkin;
	RemoveChild(g_npcRoot, old);
	uint8_t *shape = NewNode(*(void ***)old, "BaseMaleBody:0", 0);
	uint8_t *skin = (uint8_t *)NewObject(*(void ***)oldSkin, 0x100);
	*(int32_t *)(skin + 0x08) = 1;
	*(uint8_t **)(skin + 0x40) = g_bodyData;
	*(uint8_t **)(skin + 0x28) = *(uint8_t **)(oldSkin + 0x28);
	*(uint32_t *)(skin + 0x30) = 12;
	*(uint32_t *)(skin + 0x38) = 12;
	*(uint8_t **)(shape + 0x140) = skin;
	*(uint8_t **)(shape + 0x28) = g_npcRoot;
	AddChild(g_npcRoot, shape);
	g_bodyShape = shape;
	g_bodySkin = skin;
}
static void ReplaceHands(void)
{
	uint8_t *old = g_handsShape, *oldSkin = g_handsSkin;
	RemoveChild(g_npcRoot, old);
	uint8_t *shape = NewNode(*(void ***)old, "NakedHands:0", 0);
	uint8_t *skin = (uint8_t *)NewObject(*(void ***)oldSkin, 0x100);
	memcpy(skin + 0x08, oldSkin + 0x08, 0xF8);
	*(int32_t *)(skin + 0x08) = 1;
	*(uint8_t **)(skin + 0x40) = g_handsData;
	*(uint8_t **)(shape + 0x140) = skin;
	*(uint8_t **)(shape + 0x28) = g_npcRoot;
	AddChild(g_npcRoot, shape);
	g_handsShape = shape;
	g_handsSkin = skin;
}
/* Case 6: the bike's skin given new bone data at the load whose transforms aren't there yet (the
 * entries pointer 0), as a skin caught half built; filled in by FillBikeData 0.15 s later. */
static uint8_t *ReplaceBikeData(void)
{
	uint8_t *inst = *(uint8_t **)(g_bikeShape + 0x140), *was = *(uint8_t **)(inst + 0x40);
	uint8_t *data = (uint8_t *)NewObject(*(void ***)was, 0x100);
	memcpy(data + 0x08, was + 0x08, 0xF8);
	*(int32_t *)(data + 0x08) = 2;      /* the skin and the model cache */
	*(uint8_t **)(data + 0x10) = NULL;  /* the transforms not filled in yet */
	*(uint8_t **)(inst + 0x40) = data;
	return data;
}
/* Case 7: the skeleton's arm and spine nodes replaced by new ones (the same names and places),
 * the old ones detached, the body's and the kept hands' bone lists pointed at the new ones: a
 * load that rebuilds those nodes while a shape held before it is kept. */
static void ReplaceArmAndSpineNodes(void)
{
	static const int which[5] = { 1, 2, 5, 6, 7 };   /* the spine's two, the hand, the upper arm, the forearm */
	uint8_t **bodyList = *(uint8_t ***)(g_bodySkin + 0x28);
	uint8_t **handsNodes = *(uint8_t ***)(g_handsSkin + 0x10), **handsXfs = *(uint8_t ***)(g_handsSkin + 0x28);
	for (int k = 0; k < 5; k++) {
		int i = which[k];
		uint8_t *old = g_bodyNodes[i];
		uint16_t kids = *(uint16_t *)(old + 0x132);
		uint8_t *node = NewNode(*(void ***)old, "", kids ? 4 : 0);
		*(uint8_t **)(node + 0x10) = *(uint8_t **)(old + 0x10);   /* the same name */
		memcpy(node + 0x18, old + 0x18, 0x10);
		memcpy(node + 0x30, old + 0x30, 0xF0);   /* the transforms, local and world */
		for (unsigned c = 0; c < kids; c++) {    /* the children (a skin helper) go with it */
			uint8_t *child = (*(uint8_t ***)(old + 0x128))[c];
			AddChild(node, child);
			*(uint8_t **)(child + 0x28) = node;
		}
		*(uint16_t *)(old + 0x132) = 0;
		RemoveChild(g_npcRoot, old);
		*(uint8_t **)(old + 0x28) = NULL;   /* detached: its world stays where the load left it */
		AddChild(g_npcRoot, node);
		*(uint8_t **)(node + 0x28) = g_npcRoot;
		g_bodyNodes[i] = node;
		bodyList[i] = node;
		if (i == 5) {
			handsNodes[3] = node;
			handsXfs[3] = g_handsXf[3] = node + 0x70;
		}
	}
}
/* How the ride looks after a load: the bike's lean, the body's skin, the torso's lean. */
typedef struct {
	int leaned, finals, level, loads, resumed, looks;
} RideCounts;
static void CountRide(RideCounts *c)
{
	c->leaned = LogLines("the upper body leaned ");
	c->finals = LogLines("s into the ride, final") + LogLines("upper body's lean final");
	c->level = LogLines("held, level");
	c->loads = LogLines("load: a save loaded (PostLoadGame)");
	c->resumed = LogLines("load: the ride resumed ");
	c->looks = LogLines("load: 2.5 s into the ride after the load");
}
static float BikeLean(void)
{
	float R[9];
	AppliedRotation(R);
	return asinf(R[2] > 1.0f ? 1.0f : R[2] < -1.0f ? -1.0f : R[2]) * DEG;
}
static float ShoulderOff(bool *replica)
{
	float Rw[9], Pw[3], S[3], mS[3];
	uint8_t *dataNow = *(uint8_t **)(g_bodySkin + 0x40);
	*replica = dataNow && dataNow != g_bodyData;
	if (!*replica)
		return -1.0f;
	const uint8_t *copyNow = *(const uint8_t **)(dataNow + 0x10);
	ExpectedTilt(Rw, Pw);
	memcpy(S, g_bodyNodes[6] + 0xA0, 12);
	MapBone(g_bodyNodes[6], g_bodyBonesOriginal + 6 * 0x50, copyNow + 6 * 0x50, S, mS);
	return TiltedOff(S, mS, Rw, Pw);
}
static void RideReport(const char *what, const RideCounts *before, bool aLoad)
{
	RideCounts now;
	CountRide(&now);
	bool replica;
	float bikeLean = BikeLean(), shoulderOff = ShoulderOff(&replica);
	int leaned = now.leaned - before->leaned, finals = now.finals - before->finals, level = now.level - before->level;
	printf("  %s: the bike leaning %.1f deg into the turn; the body's skin on %s; the shoulder %.1f off the tilt alone (the torso's lean); %d \"leaned\" lines, %d final; %d \"held, level\" traces; last lean %.1f\n",
	       what, bikeLean, replica ? "the plugin's copy (held)" : "the game's own data (not held)", shoulderOff, leaned, finals, level, LastLogNumber("the upper body leaned "));
	CHECK(fabsf(bikeLean) > 2.0f, "%s: the bike leans into the turn (%.1f deg)", what, bikeLean);
	CHECK(replica && shoulderOff > 1.0f && shoulderOff < 20.0f, "%s: the rider held and leaned forward (the shoulder %.1f off the tilt alone; 9.9 getting on)", what, shoulderOff);
	CHECK(finals >= 1, "%s: a final lean (%d)", what, finals);
	if (aLoad)
		CHECK(now.loads - before->loads == 1 && now.resumed - before->resumed == 1 && now.looks - before->looks == 1,
		      "%s: one line each of the load, the ride resumed and the look 2.5 s in (%d, %d, %d)", what, now.loads - before->loads,
		      now.resumed - before->resumed, now.looks - before->looks);
}
static void LoadIntoRideTests(void)
{
	*(float *)(g_turnRadius + 0x30) = 300.0f;
	*(float *)(g_turnStand + 0x30) = 20.0f;
	SetNormal(0.0f, 0.0f, 1.0f);
	SetState(0);
	FlatGround();
	printf("loads into a ride (finding 2 of test 40): getting on, riding round in a circle:\n");
	RideCounts c;
	CountRide(&c);
	SetLive(60.0f);
	SetCamera(300.0f);
	SetTilt(30.0f);
	g_onFrame = CircleRide;
	RunFrames(4500);
	RideReport("getting on", &c, false);

	const char *names[7] = {
		"1 a load in place (the body's 3D replaced, the hands' kept)",
		"2 a load 150000 units off (the 3D's world 25 frames behind; the body replaced, the hands kept)",
		"3 a load in place with nothing kept (the body and the hands replaced)",
		"4 a load 150000 units off, nothing kept, 3 frames behind",
		"5 a load in place, the body's new bone data half built for 0.15 s (a zero rotation in bone 0)",
		"6 a load in place, the bike's skin given new bone data with no transforms to read for 0.15 s",
		"7 a load in place, the hands kept and the arm and spine nodes rebuilt (the old ones detached)" };
	for (int k = 0; k < 7; k++) {
		printf("loads into a ride: %s:\n", names[k]);
		CountRide(&c);
		int unbuilt = LogLines("has no bone transforms to read yet");
		g_onFrame = NULL;
		Send(3, 1);   /* PostLoadGame */
		if (k == 1 || k == 3) {
			PlayerPos()[0] += 150000.0f;
			g_staleFrames = k == 3 ? 3 : 25;   /* 25: past the first 100 ms tick for sure */
		}
		ReplaceBody();
		if (k == 2 || k == 3)
			ReplaceHands();
		if (k == 6)
			ReplaceArmAndSpineNodes();
		g_onFrame = CircleRide;
		if (k == 4) {
			uint8_t keep[0x50];
			memcpy(keep, g_bodyBones, 0x50);
			memset(g_bodyBones + 0x10, 0, 0x30);   /* bone 0's rotation not filled in yet */
			RunFrames(150);
			memcpy(g_bodyBones, keep, 0x50);
			RunFrames(6350);
		} else if (k == 5) {
			uint8_t *data = ReplaceBikeData();
			RunFrames(150);
			*(uint8_t **)(data + 0x10) = g_bones;   /* filled in */
			RunFrames(2850);
			int refs = *(int32_t *)(data + 0x08);
			CHECK(refs == 3 && LogLines("has no bone transforms to read yet") - unbuilt == 1,
			      "%s: the refusal said once (%d) and the skin held again by 3 s (references %d)", names[k], LogLines("has no bone transforms to read yet") - unbuilt, refs);
			RunFrames(3500);
		} else {
			RunFrames(6500);
		}
		RideReport(names[k], &c, true);
	}

	/* 8: the tester's picture of test 40 (the bars turning, the wheels spinning, the bike upright
	 * through the turns and the rider sitting up) is what the plugin does with CMB_TiltLive at 0
	 * and the slope or the camera on: the tilt left at 0 by the load (the script didn't set it),
	 * then set 4 s later. Said in the log, both ways; nothing of the plugin's own to bring back. */
	printf("loads into a ride: 8 a load with CMB_TiltLive left at 0 (the slope and the camera on), set 4 s later:\n");
	CountRide(&c);
	int zero = LogLines("riding with CMB_TiltLive at 0 for "), back = LogLines("tilt: CMB_TiltLive reads 30 now"), off = LogLines("; not resumed: the tilt off (CMB_TiltLive 0");
	g_onFrame = NULL;
	Send(3, 1);
	ReplaceBody();
	SetTilt(0.0f);
	g_onFrame = CircleRide;
	float wheelBefore[9], wheelAfter[9];
	AppliedRotationOf(g_partBonesOriginal[0], g_partBones[0], wheelBefore);
	RunFrames(4000);
	AppliedRotationOf(g_partBonesOriginal[0], g_partBones[0], wheelAfter);
	bool replica;
	float lean0 = BikeLean(), bars0 = BarAngle(), shoulder0 = ShoulderOff(&replica);
	(void)shoulder0;
	printf("  the tilt at 0: the bike leaning %.1f deg, the bars %.1f deg, the wheel's map %s, the body's skin on %s\n", lean0, bars0,
	       memcmp(wheelBefore, wheelAfter, sizeof(wheelBefore)) ? "turning" : "standing", replica ? "the plugin's copy" : "the game's own data");
	CHECK(fabsf(lean0) < 0.5f && fabsf(bars0) > 0.5f && memcmp(wheelBefore, wheelAfter, sizeof(wheelBefore)) && !replica,
	      "the tilt at 0 after the load: the bike level (%.1f deg), the bars over (%.1f deg) and the wheels turning, the rider not held: the tester's picture", lean0, bars0);
	CHECK(LogLines("riding with CMB_TiltLive at 0 for ") - zero == 1 && LogLines("; not resumed: the tilt off (CMB_TiltLive 0") - off == 1,
	      "and the log says so: the tilt global's line (%d) and the look 2.5 s in naming it (%d)", LogLines("riding with CMB_TiltLive at 0 for ") - zero,
	      LogLines("; not resumed: the tilt off (CMB_TiltLive 0") - off);
	SetTilt(30.0f);   /* the script's late set */
	RunFrames(4000);
	float lean1 = BikeLean(), shoulder1 = ShoulderOff(&replica);
	CHECK(fabsf(lean1) > 2.0f && replica && shoulder1 > 1.0f && LogLines("tilt: CMB_TiltLive reads 30 now") - back == 1,
	      "set 4 s later: the bike leans (%.1f deg), the rider held and leaned (the shoulder %.1f off), and the line that it came back", lean1, shoulder1);

	/* 9: the other way the bike could stand upright through the turns, the tilt's filter held in
	 * the air after the load (the controller saying so, the rays finding no ground): the bike
	 * level, but the rider still held and leaned forward, so not the tester's picture. */
	printf("loads into a ride: 9 a load into the air (the controller in the air, no ground for the rays) for 4 s:\n");
	g_onFrame = NULL;
	Send(3, 1);
	ReplaceBody();
	SetState(2);
	g_groundZ = PlayerPos()[2] - 2000.0f;
	g_onFrame = CircleRide;
	RunFrames(4000);
	float lean2 = BikeLean(), shoulder2 = ShoulderOff(&replica);
	CHECK(fabsf(lean2) < 2.0f && replica && shoulder2 > 1.0f && shoulder2 < 20.0f,
	      "in the air: the bike level (%.1f deg) but the rider held and leaned forward (the shoulder %.1f off the tilt alone): not the tester's picture", lean2, shoulder2);
	SetState(0);
	FlatGround();
	RunFrames(2500);
	float lean3 = BikeLean();
	CHECK(fabsf(lean3) > 2.0f, "on the ground again: the bike leans into the turn (%.1f deg)", lean3);

	g_onFrame = NULL;
	SetTilt(0.0f);
	SetLive(0.0f);
	SetCamera(0.0f);
	RunFrames(500);
}

/* --- Climbing low things (test 40's finding 8; mode 10) ------------------------------------
 * The player's capsule (radius 18) stopped by what it meets, as f8's capsule model has it: a
 * contact steeper than the limit the controller holds now (acos of *Slope()) is a wall, so the
 * axis is held 18 short of the face; within the limit, the push into the contact slides the
 * capsule up it (the push times sin a cos a, the contact's angle held), and once the feet are at
 * the top less 0.5 it is let through, on top, till the axis is past the far side. The contact's
 * angle: acos((18 - T/2)/(18 + T/2)) for a round log T across, acos(1 - T/18) for a sharp step
 * of T (90 from 18 up: the capsule's upright side). Only the planes given a kind here, and only
 * in mode 10 (R4); the feet follow the rays' ground there (a slope, the kink) with the lift. */
enum { CAP_NONE, CAP_LOG, CAP_STEP };
#define CAPSULE_R 18.0f
static bool g_capsuleOn;
static int g_capKind[3];
static float g_capDepth[3];     /* how far the thing reaches past its face, for when the axis is past it */
static float g_feetLift;        /* the feet over the ground: onto what the capsule climbed */
static int g_capHeld;           /* frames the capsule was held at a face it couldn't climb */
static float GroundZAt(float x, float y)
{
	float u = (x - g_slopeO[0]) * g_slopeD[0] + (y - g_slopeO[1]) * g_slopeD[1];
	if (g_kinkOn && u > g_kinkAt)
		u = g_kinkAt;
	return g_groundZ + g_slopeK * u;
}
static float ContactAngle(int kind, float T)
{
	if (kind == CAP_LOG)
		return acosf((CAPSULE_R - 0.5f * T) / (CAPSULE_R + 0.5f * T)) * DEG;
	return T >= CAPSULE_R ? 90.0f : acosf(1.0f - T / CAPSULE_R) * DEG;
}
static void CapsuleStop(const float before[2])
{
	float *p = PlayerPos(), lift = 0.0f;
	float raised = p[2] - GroundZAt(p[0], p[1]);   /* the feet over the ground now: the plugin's SetPosition (stage 2's step up) may have put them up since the last frame */
	for (int i = 0; i < 3; i++) {
		const FakePlane *w = &g_planes[i];
		if (!w->on || !g_capKind[i] || w->follow != 0.0f)
			continue;
		float T = w->top > 0.0f ? w->top : 10000.0f;
		float s = (p[0] - w->point[0]) * w->normal[0] + (p[1] - w->point[1]) * w->normal[1];
		if (s > CAPSULE_R + 0.05f || s < -g_capDepth[i])
			continue;   /* not touching it, or the axis past its far side */
		float have = g_planeTopDepth[i] > 0.0f && raised > g_feetLift ? raised : g_feetLift;   /* a step up counts only at a thing with a top (stage 2's checks; R4) */
		if (have >= T - 0.5f) {
			lift = fmaxf(lift, T);   /* on top of it: let through */
			continue;
		}
		float sb = (before[0] - w->point[0]) * w->normal[0] + (before[1] - w->point[1]) * w->normal[1];
		float a = ContactAngle(g_capKind[i], T) / DEG, push = sb - s > 0.0f ? sb - s : 0.0f, up = have;
		if (s < CAPSULE_R) {   /* held at the contact */
			p[0] += w->normal[0] * (CAPSULE_R - s);
			p[1] += w->normal[1] * (CAPSULE_R - s);
		}
		if (a <= acosf(*Slope()) + 1e-4f)
			up += push * sinf(a) * cosf(a);   /* within the limit: slid up it */
		else
			g_capHeld++;
		lift = fmaxf(lift, up);
	}
	g_feetLift = lift;
	p[2] = GroundZAt(p[0], p[1]) + g_feetLift;
}
static void ClimbFrame(float dt)
{
	float before[2] = { PlayerPos()[0], PlayerPos()[1] };
	FakeGameFrame(dt);
	if (g_capsuleOn)
		CapsuleStop(before);
}
/* One frame of the game and the plugin, no wait (a cut within a frame). */
static void OneFrame(void)
{
	if (g_onFrame)
		g_onFrame(0.005f);
	SyncFakeWorld();
	((void (*)(Task *))g_task->vtbl[1])(g_task);
	if (*Slope() < g_slopeMin)
		g_slopeMin = *Slope();
}
/* Plane i a thing `ahead` units ahead of the player's axis, facing them, `top` tall above the
 * ground (0: no top), of a capsule kind, reaching `depth` past its face. */
static FakePlane *Obstacle(int i, float ahead, float top, int kind, float depth, uint32_t layer, uint8_t *what)
{
	FakePlane *w = &g_planes[i];
	float h = PlayerHeading(), fx = sinf(h), fy = cosf(h);
	memset(w, 0, sizeof(*w));
	w->point[0] = PlayerPos()[0] + fx * ahead;
	w->point[1] = PlayerPos()[1] + fy * ahead;
	w->normal[0] = -fx;
	w->normal[1] = -fy;
	w->layer = layer;
	w->top = top;
	w->what = what;
	w->on = true;
	g_capKind[i] = kind;
	g_capDepth[i] = depth;
	g_planeTopDepth[i] = 0.0f;   /* no top the rays down see, unless a stage-2 check gives it one */
	g_capHeld = 0;
	return w;
}
static float FaceGap(const FakePlane *w)   /* the axis to the face, + in front of it */
{
	return (PlayerPos()[0] - w->point[0]) * w->normal[0] + (PlayerPos()[1] - w->point[1]) * w->normal[1];
}
static void ClearObstacles(void)
{
	for (int i = 0; i < 3; i++) {
		g_planes[i].on = false;
		g_capKind[i] = CAP_NONE;
		g_planeTopDepth[i] = 0.0f;
	}
	g_feetLift = 0.0f;
	PlayerPos()[2] = GroundZAt(PlayerPos()[0], PlayerPos()[1]);
}
/* W held up to ms: the seconds until the axis is past the thing's far side (-1: it isn't). */
static float RideAt(const FakePlane *w, float depth, int ms)
{
	Keys(0.0f, 1.0f);
	for (int t = 0; t < ms; t += 50) {
		RunFrames(50);
		if (FaceGap(w) < -depth)
			return (float)(t + 50) / 1000.0f;
	}
	return -1.0f;
}
/* W held up to ms until the climb's boost is in the slot: the seconds it took (-1: never). */
static float UntilBoost(float boostCos, int ms)
{
	Keys(0.0f, 1.0f);
	for (int t = 0; t < ms; t += 25) {
		RunFrames(25);
		if (Near(*Slope(), boostCos))
			return (float)(t + 25) / 1000.0f;
	}
	return -1.0f;
}
static void RollOff(void)   /* W let go of, the obstacles gone, rolled off to a stop */
{
	Keys(0.0f, 0.0f);
	ClearObstacles();
	RunFrames(2500);
}
static void GetOffAndOn(float degrees)
{
	Keys(0.0f, 0.0f);
	SetLive(0.0f);
	SetCamera(0.0f);
	SetTilt(0.0f);
	RunFrames(400);
	SetLive(degrees);
	SetCamera(300.0f);
	SetTilt(30.0f);
	RunFrames(1000);
}
static int FaceLines(void) { return LogLines("past the front wheel at axle height") + LogLines("rays: nothing ahead now"); }

/* Stage 2 (test 41, ClimbStep; plan check 9): a sharp step 26 high and 60 deep, a stump. Its
 * contact is on the capsule's upright side (acos(1 - 26/18): 90), so no limit climbs it; its top
 * is a flat surface the plugin's rays down find (g_planeTopDepth, these checks only), and the
 * capsule model takes the feet put up by SetPosition as on top of it. Each part on a ride of its
 * own, so the climb's hand of 10 lines is full at its start. */
static void ClimbStepTests(void)
{
	float *head = (float *)(g_player + 0xC8), cos85 = cosf(85.0f / DEG);
	FakePlane *w;
	float passed;

	printf("climb, stage 2 (ClimbStep=1): a sharp step 26 high and 60 deep 400 ahead (its contact on the capsule's upright side), its top where rays down find it, SetPosition honoured, W held: stepped up 27.5 and 4 on, at most twice, over it:\n");
	GetOffAndOn(45.0f);
	g_camYaw = *head;
	CHECK(LogLines("a sharp step the limit can't take stepped up onto (ClimbStep=1)") >= 1 && LogLines("low things up to 31.9 above the feet climbed with the limit at 85 deg while forward is held, sharp steps up to it stepped up onto") >= 1,
	      "the settings line and the ride's capsule line say ClimbStep=1");
	{
		int step0 = LogLines("climb: stepped up 27.5 (the top 26.0 at "), over0 = LogLines("climb: over it after"), after0 = LogLines(", after 1 step up): the climb limit back to 47");
		int noStep0 = LogLines("climb: no step:"), didnt0 = LogLines("climb: the step up didn't take"), sets0 = g_setPositions;
		g_slopeMin = 1.0f;
		w = Obstacle(0, 400.0f, 26.0f, CAP_STEP, 60.0f, 1, NULL);
		g_planeTopDepth[0] = 60.0f;
		g_rec = true;
		g_recN = 0;
		passed = RideAt(w, 60.0f, 4000);
		g_rec = false;
		float steepest = g_slopeMin;
		RunFrames(500);
		int steps = g_recN;
		bool sized = steps > 0;
		for (int i = 0; i < steps; i++)
			sized = sized && fabsf(g_recDz[i] - 27.5f) <= 0.5f && fabsf(g_recStep[i] - 4.0f) <= 0.05f;
		CHECK(passed > 0.0f, "over it within 4 s (%.2f s; the capsule held at it %d frames)", passed, g_capHeld);
		CHECK(steps >= 1 && steps <= 2 && sized && g_setPositions - sets0 == steps, "stepped up %d time(s) (SetPosition called %d), each by the top + 1.5 (%.2f) and 4 on (%.2f)",
		      steps, g_setPositions - sets0, steps ? g_recDz[0] : 0.0f, steps ? g_recStep[0] : 0.0f);
		CHECK(LogLines("climb: stepped up 27.5 (the top 26.0 at ") - step0 == steps && LogLines("climb: over it after") - over0 == 1 && LogLines(", after 1 step up): the climb limit back to 47") - after0 == (steps == 1) &&
		      LogLines("climb: no step:") == noStep0 && LogLines("climb: the step up didn't take") == didnt0,
		      "a \"stepped up 27.5 (the top 26.0 at ...\" line a step (%d), one \"over it ... after 1 step up\" (%d), no \"no step\" or \"didn't take\" line",
		      LogLines("climb: stepped up 27.5 (the top 26.0 at ") - step0, LogLines("climb: over it after") - over0);
		CHECK(Near(steepest, cos85) && Near(*Slope(), COS47), "the boost at it (the steepest limit %.2f deg), 47 again after (%.2f deg)", acosf(steepest) * DEG, acosf(*Slope()) * DEG);
		RollOff();
	}

	printf("climb, stage 2: the same step with SetPosition not honoured, W held: two steps asked, both said not to have taken, given up after 1.5 s stalled, 47; forward pressed again: the boost again, no more steps at this obstacle:\n");
	GetOffAndOn(45.0f);
	g_camYaw = *head;
	{
		int sets0 = g_setPositions, didnt0 = LogLines("climb: the step up didn't take"), given0 = LogLines("climb: given up after"), made0 = LogLines(", 2 steps up made): not again");
		int low0 = LogLines("climb: a low face at the capsule");
		g_honour = 0;
		w = Obstacle(0, 400.0f, 26.0f, CAP_STEP, 60.0f, 1, NULL);
		g_planeTopDepth[0] = 60.0f;
		passed = RideAt(w, 60.0f, 3500);
		CHECK(passed < 0.0f && FaceGap(w) > 17.0f && g_setPositions - sets0 == 2 && LogLines("climb: the step up didn't take") - didnt0 == 2,
		      "held at it (the axis %.1f from its face): 2 steps asked (%d), both said not to have taken (%d)", FaceGap(w), g_setPositions - sets0, LogLines("climb: the step up didn't take") - didnt0);
		CHECK(LogLines("climb: given up after") - given0 == 1 && LogLines(", 2 steps up made): not again") - made0 == 1 && Near(*Slope(), COS47),
		      "given up (%d line, \"2 steps up made\"), back to 47 (%.2f deg)", LogLines("climb: given up after") - given0, acosf(*Slope()) * DEG);
		RunFrames(1000);
		CHECK(LogLines("climb: a low face at the capsule") - low0 == 1 && Near(*Slope(), COS47), "W still held 1 s: not again (%d boost line), 47 (%.2f deg)", LogLines("climb: a low face at the capsule") - low0, acosf(*Slope()) * DEG);
		Keys(0.0f, 0.0f);
		RunFrames(300);
		int sets1 = g_setPositions;
		float took = UntilBoost(cos85, 1000);
		RunFrames(1500);
		CHECK(took > 0.0f && g_setPositions == sets1, "forward pressed again: the boost on again (%.2f s), but no step (SetPosition called %d more): two an obstacle", took, g_setPositions - sets1);
		Keys(0.0f, 0.0f);
		g_honour = 4;
		RollOff();
	}

	printf("climb, stage 2: the same step with something 90 over its top (no room for the capsule's 128), W held: no step, \"no room above it\", given up:\n");
	GetOffAndOn(45.0f);
	g_camYaw = *head;
	{
		int sets0 = g_setPositions, room0 = LogLines("climb: no step: no room above it (FakeShelf, layer 1, 90 over the top 26.0"), given0 = LogLines("climb: given up after");
		w = Obstacle(0, 400.0f, 26.0f, CAP_STEP, 60.0f, 1, NULL);
		g_planeTopDepth[0] = 60.0f;
		g_shelfOn = true;   /* a disc 116 over the ground, 10 to 60 ahead of the player wherever they are: over the step's top, not over the axis or a wheel */
		g_shelfHeight = 116.0f;
		g_shelfAhead = 35.0f;
		g_shelfRadius = 25.0f;
		passed = RideAt(w, 60.0f, 3500);
		CHECK(passed < 0.0f && FaceGap(w) > 17.0f && g_setPositions == sets0, "held at it (the axis %.1f from its face), no SetPosition (%d)", FaceGap(w), g_setPositions - sets0);
		CHECK(LogLines("climb: no step: no room above it (FakeShelf, layer 1, 90 over the top 26.0") - room0 == 1 && LogLines("climb: given up after") - given0 == 1,
		      "one \"no step: no room above it (FakeShelf, layer 1, 90 over the top 26.0 ...\" line (%d), given up (%d)",
		      LogLines("climb: no step: no room above it (FakeShelf, layer 1, 90 over the top 26.0") - room0, LogLines("climb: given up after") - given0);
		Keys(0.0f, 0.0f);
		g_shelfOn = false;
		g_shelfHeight = g_shelfAhead = 0.0f;
		g_shelfRadius = 60.0f;
		RollOff();
	}

	printf("climb, stage 2: ClimbStep=0 written (read again on getting on), the same step, SetPosition honoured, W held: no step, held, given up (the boost alone, as stage 1 shipped):\n");
	RewriteIni("Climb=1\n", "Climb=1\nClimbStep=0\n");
	GetOffAndOn(45.0f);
	g_camYaw = *head;
	{
		int sets0 = g_setPositions, given0 = LogLines("climb: given up after"), step0 = LogLines("climb: stepped up"), noStep0 = LogLines("climb: no step:");
		CHECK(LogLines("; sharp steps not stepped up onto (ClimbStep=0) (read again on getting on)") >= 1, "the settings line says ClimbStep=0");
		w = Obstacle(0, 400.0f, 26.0f, CAP_STEP, 60.0f, 1, NULL);
		g_planeTopDepth[0] = 60.0f;
		passed = RideAt(w, 60.0f, 3500);
		CHECK(passed < 0.0f && FaceGap(w) > 17.0f && g_setPositions == sets0 && LogLines("climb: stepped up") == step0 && LogLines("climb: no step:") == noStep0 && LogLines("climb: given up after") - given0 == 1,
		      "held at it (the axis %.1f from its face), no SetPosition (%d), no step line, given up (%d)", FaceGap(w), g_setPositions - sets0, LogLines("climb: given up after") - given0);
		Keys(0.0f, 0.0f);
		RollOff();
	}
	RewriteIni("ClimbStep=0", "ClimbStep=1");
	GetOffAndOn(45.0f);
	g_camYaw = *head;
}

static void ClimbTests(void)
{
	float *head = (float *)(g_player + 0xC8), cos85 = cosf(85.0f / DEG), passed;
	*(float *)(g_turnRadius + 0x30) = 180.0f;   /* steering on: the input hook (and the throttle) with it */
	*(float *)(g_turnSlow + 0x30) = 50.0f;
	*(float *)(g_turnStand + 0x30) = 60.0f;
	SetNormal(0.0f, 0.0f, 1.0f);
	SetState(0);
	FlatGround();
	g_camYaw = *head;
	g_handlerStyle = 2;
	g_honour = 4;
	g_capsuleOn = true;
	Keys(0.0f, 0.0f);
	g_onFrame = ClimbFrame;
	printf("climbing low things (test 40's finding 8): getting on with the MCM's 45 (the game's own 47 kept), on flat ground:\n");
	SetLive(45.0f);
	SetCamera(300.0f);
	SetTilt(30.0f);
	RunFrames(1500);
	CHECK(Near(*Slope(), COS47), "riding: the limit the game's own 47 (%.2f deg)", acosf(*Slope()) * DEG);
	CHECK(LogLines("climb: the capsule radius 18.0, height 128.0 (controller+0x370/+0x374); its step height 31.0, mod 0.00 for 0.00 s (+0x424/+0x428/+0x42C), cast depth 33.5 (+0x430); low things up to 31.9 above the feet") == 1,
	      "the ride's capsule line: radius 18.0, height 128.0, step height 31.0, cast depth 33.5, low things up to 31.9 (the wheel radius + 2)");
	CHECK(LogLines("  climb: low things at the capsule climbed (Climb=1): the slope limit raised to 85 deg") == 1, "the settings line says Climb=1 and 85 deg");
	int low0 = LogLines("climb: a low face at the capsule"), over0 = LogLines("climb: over it");
	g_slopeMin = 1.0f;
	Keys(0.0f, 1.0f);
	RunFrames(2000);
	CHECK(LogLines("climb: a low face at the capsule") == low0 && Near(g_slopeMin, COS47), "flat ground, W held 2 s: no boost (the steepest limit %.2f deg)", acosf(g_slopeMin) * DEG);
	RollOff();

	printf("climb: a round log 22 across 600 ahead (it meets the capsule at acos(7/29) = 76 deg, over the 47: test 40's stops), W held: the limit at 85 at the capsule, over it, back to 47:\n");
	g_slopeMin = 1.0f;
	FakePlane *w = Obstacle(0, 600.0f, 22.0f, CAP_LOG, 22.0f, 1, NULL);
	passed = RideAt(w, 22.0f, 3000);
	float steepest = g_slopeMin;
	RunFrames(500);
	CHECK(passed > 0.0f, "passed within 3 s (%.2f s; the capsule held at it %d frame(s))", passed, g_capHeld);
	CHECK(Near(steepest, cos85), "the steepest limit written cos 85 (%.2f deg)", acosf(steepest) * DEG);
	CHECK(Near(*Slope(), COS47), "back to 47 within 0.5 s of passing (%.2f deg)", acosf(*Slope()) * DEG);
	CHECK(LogLines("climb: a low face at the capsule") - low0 == 1 && LogLines("climb: over it") - over0 == 1, "one \"low face\" line and one \"over it\" line (%d, %d)",
	      LogLines("climb: a low face at the capsule") - low0, LogLines("climb: over it") - over0);
	RollOff();
	printf("climb: a round log 30 across (acos(3/33) = 84.8 deg, just within 85), W held: over it:\n");
	g_slopeMin = 1.0f;
	w = Obstacle(0, 600.0f, 30.0f, CAP_LOG, 30.0f, 1, NULL);
	passed = RideAt(w, 30.0f, 3000);
	steepest = g_slopeMin;
	RunFrames(500);
	CHECK(passed > 0.0f && Near(steepest, cos85) && Near(*Slope(), COS47), "passed within 3 s (%.2f s), at 85 deg (%.2f), back to 47 (%.2f)", passed, acosf(steepest) * DEG, acosf(*Slope()) * DEG);
	RollOff();

	printf("climb: the same two logs with Climb=0 written (read again on getting on): the bike stays stuck at both, the limit 47:\n");
	RewriteIni("Climb=1", "Climb=0");
	GetOffAndOn(45.0f);
	for (int k = 0; k < 2; k++) {
		float T = k ? 30.0f : 22.0f;
		low0 = LogLines("climb: a low face at the capsule");
		g_slopeMin = 1.0f;
		w = Obstacle(0, 600.0f, T, CAP_LOG, T, 1, NULL);
		passed = RideAt(w, T, 3000);
		CHECK(passed < 0.0f && FaceGap(w) > 17.0f && Near(g_slopeMin, COS47) && LogLines("climb: a low face at the capsule") == low0,
		      "the log %.0f across: held at it after 3 s (the axis %.1f from its face, held %d frames), the steepest limit %.2f deg", T, FaceGap(w), g_capHeld, acosf(g_slopeMin) * DEG);
		RollOff();
	}
	RewriteIni("Climb=0", "Climb=1");
	GetOffAndOn(45.0f);

	printf("climb: a sharp step 40 high (taller than ClimbTop 31.9, lower than the face rays' 1.5 wheel radii, 44.9), W held: held, 47 throughout, one \"something at 31.9\" line:\n");
	int tall0 = LogLines("not climbed: something at 31.9 above the feet");
	low0 = LogLines("climb: a low face at the capsule");
	g_slopeMin = 1.0f;
	w = Obstacle(0, 600.0f, 40.0f, CAP_STEP, 400.0f, 1, NULL);
	passed = RideAt(w, 400.0f, 5000);
	CHECK(passed < 0.0f && FaceGap(w) > 17.0f && g_capHeld > 100, "held at it (the axis %.1f from its face, %d frames held)", FaceGap(w), g_capHeld);
	CHECK(Near(g_slopeMin, COS47) && LogLines("climb: a low face at the capsule") == low0, "the limit 47 every frame (the steepest %.2f deg), no boost", acosf(g_slopeMin) * DEG);
	CHECK(LogLines("not climbed: something at 31.9 above the feet") - tall0 == 1, "one \"not climbed: something at 31.9 above the feet\" line (%d)", LogLines("not climbed: something at 31.9 above the feet") - tall0);
	RollOff();

	printf("climb: a wall 700 ahead, W held: stops short of it as before (the face rays), the limit 47:\n");
	g_slopeMin = 1.0f;
	float p0[2];
	Mark(p0);
	w = Obstacle(0, 700.0f, 0.0f, CAP_STEP, 400.0f, 1, NULL);
	Keys(0.0f, 1.0f);
	RunFrames(5000);
	CHECK(Moved(p0) > 300.0f && FaceGap(w) > 100.0f && FaceGap(w) < 220.0f && Near(g_slopeMin, COS47), "rides %.0f and stops %.0f from the wall (the front wheel's edge 130 ahead), the steepest limit %.2f deg",
	      Moved(p0), FaceGap(w), acosf(g_slopeMin) * DEG);
	RollOff();

	printf("climb: an actor's body 600 ahead (layer 30, SkeletonExport, 22 high), W held: held, no boost, \"not climbed: an actor\":\n");
	int actor0 = LogLines("not climbed: an actor (SkeletonExport, layer 30)");
	low0 = LogLines("climb: a low face at the capsule");
	g_slopeMin = 1.0f;
	w = Obstacle(0, 600.0f, 22.0f, CAP_STEP, 30.0f, 30, g_actorObj);
	passed = RideAt(w, 30.0f, 4000);
	CHECK(passed < 0.0f && Near(g_slopeMin, COS47) && LogLines("climb: a low face at the capsule") == low0 && LogLines("not climbed: an actor (SkeletonExport, layer 30)") - actor0 == 1,
	      "held at it (%.1f from it), the limit 47 (the steepest %.2f deg), one \"not climbed: an actor\" line (%d)", FaceGap(w), acosf(g_slopeMin) * DEG,
	      LogLines("not climbed: an actor (SkeletonExport, layer 30)") - actor0);
	RollOff();

	printf("climb: the 22 log 450 ahead on a 35 deg rise (the wheels' line pitched 35, over ClimbMaxPitch 22: test 40's rock pile read 31-37), W held: no boost, \"pitched 35\":\n");
	{
		float h = *head, fx = sinf(h), fy = cosf(h), feet = PlayerPos()[2], k = tanf(35.0f / DEG);
		int pitched0 = LogLines("not climbed: the wheels' line pitched 35");
		low0 = LogLines("climb: a low face at the capsule");
		w = Obstacle(0, 450.0f, 22.0f, CAP_LOG, 22.0f, 1, NULL);
		g_slopeK = k;   /* rising along the heading, the log's foot on its line */
		g_slopeD[0] = fx;
		g_slopeD[1] = fy;
		g_slopeO[0] = w->point[0];
		g_slopeO[1] = w->point[1];
		g_groundZ = feet + 450.0f * k;
		float back[3] = { -fx, -fy, 0.0f };
		SetNormalTowards(back, 35.0f);
		g_slopeMin = 1.0f;
		passed = RideAt(w, 22.0f, 4000);
		CHECK(passed < 0.0f && Near(g_slopeMin, COS47) && LogLines("climb: a low face at the capsule") == low0 && LogLines("not climbed: the wheels' line pitched 35") - pitched0 == 1,
		      "held at it (%.1f from it), the limit 47 (the steepest %.2f deg), one \"not climbed: the wheels' line pitched 35\" line (%d)", FaceGap(w), acosf(g_slopeMin) * DEG,
		      LogLines("not climbed: the wheels' line pitched 35") - pitched0);
		Keys(0.0f, 0.0f);
		ClearObstacles();
		SetNormal(0.0f, 0.0f, 1.0f);
		FlatGround();
		RunFrames(2500);
	}

	printf("climb: down a 20 deg slope onto flat ground, W held 3 s: no boost (the rays pitched down with the bike meet the flat at about the bike's pitch):\n");
	{
		float h = *head, fx = sinf(h), fy = cosf(h), feet = PlayerPos()[2], k = tanf(20.0f / DEG);
		low0 = LogLines("climb: a low face at the capsule");
		g_slopeK = -k;   /* falling along the heading, flat from 300 ahead */
		g_slopeD[0] = fx;
		g_slopeD[1] = fy;
		g_slopeO[0] = PlayerPos()[0] + fx * 300.0f;
		g_slopeO[1] = PlayerPos()[1] + fy * 300.0f;
		g_groundZ = feet - 300.0f * k;
		g_kinkOn = true;
		g_kinkAt = 0.0f;
		float ahead[3] = { fx, fy, 0.0f };
		SetNormalTowards(ahead, 20.0f);
		g_slopeMin = 1.0f;
		Mark(p0);
		Keys(0.0f, 1.0f);
		RunFrames(3000);
		CHECK(Moved(p0) > 400.0f && Near(g_slopeMin, COS47) && LogLines("climb: a low face at the capsule") == low0, "rode %.0f onto the flat (the feet %.0f below the start), the limit 47 (the steepest %.2f deg)",
		      Moved(p0), feet - PlayerPos()[2], acosf(g_slopeMin) * DEG);
		Keys(0.0f, 0.0f);
		RunFrames(2500);
		g_kinkOn = false;
		SetNormal(0.0f, 0.0f, 1.0f);
		FlatGround();
	}

	printf("climb: a sharp step 25 high 400 ahead (its contact on the capsule's upright side: no limit climbs it, stage 2's), W held: the boost on, then cut by getting off:\n");
	w = Obstacle(0, 400.0f, 25.0f, CAP_STEP, 400.0f, 1, NULL);
	float took = UntilBoost(cos85, 3000);
	RunFrames(300);
	CHECK(took > 0.0f && Near(*Slope(), cos85), "the boost on at the step (%.2f s), 85 still written 0.3 s on (%.2f deg)", took, acosf(*Slope()) * DEG);
	int cut0 = LogLines("climb: cut after");
	SetLive(0.0f);
	SetCamera(0.0f);
	SetTilt(0.0f);
	RunFrames(300);
	CHECK(Near(*Slope(), COS47) && LogLines(": the ride's end") > 0 && LogLines("climb: cut after") > cut0, "got off during it: 47 on foot (%.2f deg), \"cut ... the ride's end\"", acosf(*Slope()) * DEG);
	Keys(0.0f, 0.0f);
	SetLive(45.0f);
	SetCamera(300.0f);
	SetTilt(30.0f);
	RunFrames(1000);
	printf("climb: the boost on at the step, a load (the controller kept, 85 in it), W let go, then off:\n");
	took = UntilBoost(cos85, 2000);
	int taken0 = LogLines("holds our climb boost's value");
	Send(3, 1);   /* PostLoadGame */
	Keys(0.0f, 0.0f);
	RunFrames(500);
	CHECK(took > 0.0f && Near(*Slope(), COS47) && LogLines("holds our climb boost's value") - taken0 == 1, "after the load the slot's 85 taken back as ours, the riding 47 written (%.2f deg)", acosf(*Slope()) * DEG);
	SetLive(0.0f);
	SetCamera(0.0f);
	SetTilt(0.0f);
	RunFrames(400);
	CHECK(Near(*Slope(), COS47), "then off: 47 on foot (%.2f deg; test 24's 60 kept on foot after a load)", acosf(*Slope()) * DEG);
	g_camYaw = *head;
	printf("climb: the boost on at the step, a load into a save on foot (the controller kept, 85 in it):\n");
	SetLive(45.0f);
	SetCamera(300.0f);
	SetTilt(30.0f);
	RunFrames(1000);
	took = UntilBoost(cos85, 2000);
	int still0 = LogLines("was still there after a load");
	Send(3, 1);   /* PostLoadGame, and not riding after it */
	SetLive(0.0f);
	SetCamera(0.0f);
	SetTilt(0.0f);
	Keys(0.0f, 0.0f);
	RunFrames(400);
	CHECK(took > 0.0f && Near(*Slope(), COS47) && LogLines("was still there after a load") - still0 == 1, "47 on foot after the load (%.2f deg), \"the climb's boost ... was still there after a load\"", acosf(*Slope()) * DEG);
	g_camYaw = *head;
	printf("climb: on with the MCM at 60, the boost at the step: 85, the throttle let up to 0.4, given up after 1.5 s stalled, back to 60, not again till forward is pressed again:\n");
	SetLive(60.0f);
	SetCamera(300.0f);
	SetTilt(30.0f);
	RunFrames(1000);
	CHECK(Near(*Slope(), 0.5f), "on: cos 60 (%.2f deg)", acosf(*Slope()) * DEG);
	int given0 = LogLines("climb: given up after"), trace0 = LogLines(" | climb 85 for ");
	low0 = LogLines("climb: a low face at the capsule");
	took = UntilBoost(cos85, 1000);
	RunFrames(1250);   /* from rest the throttle comes up from 0.1 over Accel 3 s: 0.4 by 0.9 s, the trace's line a quarter second apart */
	float throttle = LastLogNumber("throttle: speed ");
	CHECK(took > 0.0f && Near(*Slope(), cos85) && throttle >= 0.39f, "the boost on (%.2f s), 85 written; the throttle %.2f of the top, held to the speed (0) but let up to ClimbThrottle", took, throttle);
	CHECK(LogLines(" | climb 85 for ") > trace0, "the trace says \" | climb 85 for ...\" (%d lines)", LogLines(" | climb 85 for ") - trace0);
	RunFrames(1250);
	CHECK(LogLines("climb: given up after") - given0 == 1 && Near(*Slope(), 0.5f), "given up (%d line), back to 60 (%.2f deg)", LogLines("climb: given up after") - given0, acosf(*Slope()) * DEG);
	RunFrames(1500);
	CHECK(LogLines("climb: a low face at the capsule") - low0 == 1 && Near(*Slope(), 0.5f), "W still held 1.5 s: not again (%d boost line), 60 (%.2f deg)", LogLines("climb: a low face at the capsule") - low0, acosf(*Slope()) * DEG);
	Keys(0.0f, 0.0f);
	RunFrames(300);
	took = UntilBoost(cos85, 1000);
	CHECK(took > 0.0f && LogLines("climb: a low face at the capsule") - low0 == 2, "forward pressed again: on again (%.2f s)", took);
	int back0 = LogLines(": the back key");
	Keys(0.0f, -1.0f);
	OneFrame();
	float afterBack = *Slope();
	RunFrames(300);
	CHECK(Near(afterBack, 0.5f) && LogLines(": the back key") - back0 == 1, "back pressed: off within the frame (%.2f deg), \"cut ... the back key\"", acosf(afterBack) * DEG);
	Keys(0.0f, 0.0f);
	RunFrames(1500);
	ClearObstacles();
	GetOffAndOn(45.0f);
	g_camYaw = *head;

	/* Test 40: the face rays' 60 lines a ride were spent by 15:41:29.711 (2 + 58), and the
	 * stops after it had none: a hand of 20, one more every 3 s. 80 verdict changes in a ride:
	 * an obstacle lower than 1.5 radii 150 ahead (20 past the front wheel's edge, within the
	 * rays' reach at any speed over 50), there 0.3 s and gone 0.6 s, 40 times: each change a
	 * line under the old cap (the "nothing ahead now" line comes 0.25 s after it's gone, and the
	 * next verdict's needs 0.25 s after that), so its 60 are spent by the 60th change. */
	printf("climb: 80 face-ray verdict changes in one ride (an obstacle 150 ahead there 0.3 s and gone 0.6 s, 40 times), W held: lines still written after the 60th change:\n");
	{
		FakePlane *o = &g_planes[1];
		memset(o, 0, sizeof(*o));
		o->follow = 150.0f;
		o->top = 40.0f;
		o->layer = 1;
		int lines0 = FaceLines(), at60 = 0, named0 = LogLines("rays: nothing ahead now (was an obstacle, 90 deg, FakeWall, layer 1, for 0.");
		Keys(0.0f, 1.0f);
		for (int c = 0; c < 40; c++) {
			if (c == 30)
				at60 = FaceLines();
			o->on = true;
			RunFrames(300);
			o->on = false;
			RunFrames(600);
		}
		int all = FaceLines() - lines0, late = FaceLines() - at60;
		CHECK(late >= 1 && all >= 20 && all <= 20 + 36 / 3 + 2, "%d face-ray lines in the 36 s (a hand of 20, one more every 3 s), %d of them after the 60th change (the old 60 a ride: none)", all, late);
		CHECK(LogLines("rays: nothing ahead now (was an obstacle, 90 deg, FakeWall, layer 1, for 0.") > named0, "\"nothing ahead now\" names the verdict that stood: its angle, what, layer and how long (%d)",
		      LogLines("rays: nothing ahead now (was an obstacle, 90 deg, FakeWall, layer 1, for 0.") - named0);
		Keys(0.0f, 0.0f);
		memset(o, 0, sizeof(*o));
		RunFrames(2500);
	}
	ClimbStepTests();
	SetLive(0.0f);
	SetCamera(0.0f);
	SetTilt(0.0f);
	RunFrames(400);
	CHECK(Near(*Slope(), COS47), "got off at the end: 47 (%.2f deg)", acosf(*Slope()) * DEG);
	g_onFrame = NULL;
	g_capsuleOn = false;
}

/* Test 41's arms (finding 5): ArmPole 1.1,-0.3,-0.9 (the forearms near level, the tester's
 * sketch), and the inside arm's pole faded toward ArmPoleTurn 0.35,-0.3,-1.0 (test 40's) as the
 * bars turn its way, all of it at ArmPoleTurnBars 10; the arm lines' new figures read back
 * against the bones written. run.sh gives this run BarAngle=20 (the game's), so the bars reach
 * 5 and 12 deg on the spot (BarFullAt 45: 11.25 and 27 deg/s), and TorsoLean=8, so the arms are
 * solved with the bars straight. */
static const float g_armPoleIni[3] = { 1.1f, -0.3f, -0.9f }, g_armPoleTurnIni[3] = { 0.35f, -0.3f, -1.0f };

/* Turned on the spot at rate deg/s (+ right, - left) for ms, the bars over then; the arm's
 * elbow against the pole the fade gives for the bars measured (k), and against the plain
 * ArmPole and ArmPoleTurn. */
static float ArmTurn(float rate, int ms, float turnBars, const float turn[3], float *k, float *offExpected, float *offPole, float *offTurn, float *offLen)
{
	g_turnOnSpot = rate / DEG;
	g_onFrame = TurnOnTheSpot;
	RunFrames(ms);
	float bar = BarAngle(), expected[3], plain[3], turned[3];
	ArmNow a;
	ReadArmNow(&a);
	int side = g_armRight ? 1 : 0;
	*k = ExpectedPole(side, bar, g_armPoleIni, turn, turnBars, expected);
	memcpy(plain, g_armPoleIni, sizeof(plain));
	memcpy(turned, g_armPoleTurnIni, sizeof(turned));
	if (!side)
		plain[0] = -plain[0], turned[0] = -turned[0];
	*offExpected = ArmPlaneOff(&a, expected, offLen);
	*offPole = ArmPlaneOff(&a, plain, NULL);
	*offTurn = ArmPlaneOff(&a, turned, NULL);
	return bar;
}

/* Back the other way for as long, then the heading put back exactly and the bars let come
 * straight. */
static void ArmTurnBack(float rate, int ms, float heading)
{
	g_turnOnSpot = -rate / DEG;
	RunFrames(ms);
	g_onFrame = NULL;
	*(float *)(g_player + 0xC8) = heading;
	RunFrames(1000);
}

/* Getting on and off for this run: the slope, the camera and the tilt together (the settings
 * are read again when the ride starts, and the ride's end logs the wrist lines). */
static void ArmsGetOn(int ms)
{
	SetLive(60.0f);
	SetCamera(300.0f);
	SetTilt(30.0f);
	RunFrames(ms);
}

static void ArmsGetOff(int ms)
{
	SetLive(0.0f);
	SetCamera(0.0f);
	SetTilt(0.0f);
	RunFrames(ms);
}

static void ArmTests(void)
{
	static const float none[3] = { 0.0f, 0.0f, 0.0f };
	float *head = (float *)(g_player + 0xC8), heading0 = *head, k, offE, offP, offT, offLen, bar;
	SetNormal(0.0f, 0.0f, 1.0f);
	SetState(0);
	FlatGround();
	printf("arms (test 41): getting on, standing, the bars straight (TorsoLean 8):\n");
	ArmsGetOn(2000);   /* the fixed lean set at TorsoSolveFrom (1.3 s): the arms solved with the bars straight from then */
	CHECK(LogLines("the elbows bent toward (1.1, -0.3, -0.9) in the bike's space, the left mirrored (ArmPole), the inside arm's (the side the bars turn to) faded toward (0.35, -0.3, -1) as they turn, all of it at 10 deg of the bars (ArmPoleTurn, ArmPoleTurnBars)") >= 1,
	      "the lean settings line names ArmPole 1.1,-0.3,-0.9, ArmPoleTurn 0.35,-0.3,-1 and ArmPoleTurnBars 10");
	{
		ArmNow a;
		float fig[5], pole[3], fade, worst = 0.0f;
		ReadArmNow(&a);
		bool got = LoggedArmFigures("rider: the left arm solved", "rider: the left arm solved", fig, pole, &fade);
		for (int i = 0; got && i < 5; i++)
			worst = fabsf(fig[i] - a.fig[i]) > worst ? fabsf(fig[i] - a.fig[i]) : worst;
		printf("  the arm line: the elbow %.1f out, %.1f forward, %.1f below, the upper arm %.1f deg below level, the forearm %+.1f deg; the bones: %.2f, %.2f, %.2f, %.2f, %+.2f\n",
		       got ? fig[0] : NAN, got ? fig[1] : NAN, got ? fig[2] : NAN, got ? fig[3] : NAN, got ? fig[4] : NAN, a.fig[0], a.fig[1], a.fig[2], a.fig[3], a.fig[4]);
		CHECK(got && worst < 0.2f, "the arm line's elbow (out, forward, below), upper arm and forearm figures match the bones written within 0.2 (worst %.3f)", worst);
		CHECK(got && fabsf(pole[0] + 1.1f) < 0.006f && fabsf(pole[1] + 0.3f) < 0.006f && fabsf(pole[2] + 0.9f) < 0.006f && fade == 0.0f,
		      "and its pole is ArmPole, the left's x mirrored, not faded: (%.2f, %.2f, %.2f)", got ? pole[0] : NAN, got ? pole[1] : NAN, got ? pole[2] : NAN);
		float plain[3] = { -g_armPoleIni[0], g_armPoleIni[1], g_armPoleIni[2] }, turned[3] = { -g_armPoleTurnIni[0], g_armPoleTurnIni[1], g_armPoleTurnIni[2] };
		float off = ArmPlaneOff(&a, plain, &offLen), offOld = ArmPlaneOff(&a, turned, NULL);
		CHECK(off < 1.0f && offLen > 2.0f && offOld > 3.0f, "the elbow bent ArmPole's way (%.2f deg off it, offset %.1f; test 40's pole %.1f deg away)", off, offLen, offOld);
	}

	printf("arms: the bars turned 5 deg to the left (the left arm inside), then 5 to the right (outside):\n");
	bar = ArmTurn(-11.25f, 1500, 10.0f, g_armPoleTurnIni, &k, &offE, &offP, &offT, &offLen);
	printf("  the bars %.2f deg: k %.3f, the elbow %.2f deg off the faded pole, %.2f off ArmPole, %.2f off ArmPoleTurn (offset %.1f)\n", bar, k, offE, offP, offT, offLen);
	CHECK(bar > 4.5f && bar < 5.5f && k > 0.45f && k < 0.55f && offE < 1.0f && offLen > 2.0f && offP > 2.0f && offT > 2.0f,
	      "at %.1f deg of the bars the inside elbow is %.2f deg off ArmPole faded %.2f of the way (k = |bars| / 10), %.1f off ArmPole and %.1f off ArmPoleTurn", bar, offE, k, offP, offT);
	bar = ArmTurn(11.25f, 3000, 10.0f, g_armPoleTurnIni, &k, &offE, &offP, &offT, &offLen);
	printf("  the bars %.2f deg: k %.3f, the elbow %.2f deg off ArmPole (offset %.1f)\n", bar, k, offP, offLen);
	CHECK(bar < -4.5f && bar > -5.5f && k == 0.0f && offP < 1.0f && offLen > 2.0f, "at %.1f deg the outside elbow keeps ArmPole (%.2f deg off it)", bar, offP);
	ArmTurnBack(11.25f, 1500, heading0);

	printf("arms: the bars turned 12 deg to the left, then 12 to the right:\n");
	bar = ArmTurn(-27.0f, 1500, 10.0f, g_armPoleTurnIni, &k, &offE, &offP, &offT, &offLen);
	printf("  the bars %.2f deg: k %.3f, the elbow %.2f deg off ArmPoleTurn, %.2f off ArmPole (offset %.1f)\n", bar, k, offT, offP, offLen);
	CHECK(bar > 11.5f && bar < 12.5f && k == 1.0f && offT < 1.0f && offLen > 2.0f && offP > 2.0f, "at %.1f deg of the bars the inside elbow has all of ArmPoleTurn (%.2f deg off it, %.1f off ArmPole)", bar, offT, offP);
	bar = ArmTurn(27.0f, 3000, 10.0f, g_armPoleTurnIni, &k, &offE, &offP, &offT, &offLen);
	printf("  the bars %.2f deg: the elbow %.2f deg off ArmPole (offset %.1f)\n", bar, offP, offLen);
	CHECK(bar < -11.5f && bar > -12.5f && offP < 1.0f && offLen > 0.3f && offT > 2.0f, "at %.1f deg the outside elbow keeps ArmPole (%.2f deg off it, %.1f off ArmPoleTurn; the arm near straight, its grip gone forward: the offset %.1f)", bar, offP, offT, offLen);
	ArmTurnBack(27.0f, 1500, heading0);

	printf("arms: riding straight at 200 a second, then at 450 (the arms' riding line, once a hold, over 300 for a second):\n");
	int ridingBefore = LogLines("rider: the arms riding");
	float radius0 = *(float *)(g_turnRadius + 0x30), stand0 = *(float *)(g_turnStand + 0x30);
	*(float *)(g_turnRadius + 0x30) = 300.0f;   /* steering on for the ride: the plugin measures the speed there */
	*(float *)(g_turnStand + 0x30) = 20.0f;
	g_rideSpeed = 200.0f;
	g_rideSlope = 0.0f;
	g_noise = 0.0f;
	g_onFrame = RideAlong;
	RunFrames(2000);
	int slow = LogLines("rider: the arms riding") - ridingBefore;
	g_rideSpeed = 450.0f;
	RunFrames(2500);
	int fast = LogLines("rider: the arms riding") - ridingBefore;
	{
		ArmNow a;
		float fig[5], pole[3], fade, worst = 0.0f;
		ReadArmNow(&a);
		bool got = LoggedArmFigures("rider: the arms riding", "the left arm: ", fig, pole, &fade);
		for (int i = 0; got && i < 5; i++)
			worst = fabsf(fig[i] - a.fig[i]) > worst ? fabsf(fig[i] - a.fig[i]) : worst;
		const char *line = LastLogLine("rider: the arms riding");
		CHECK(slow == 0 && fast == 1 && got && worst < 0.2f && line && strstr(line, "the right arm not solved"),
		      "none at 200, one at 450 (%d, %d): the left arm's figures within 0.2 of the bones (worst %.3f), the forearm %+.1f deg; the fake's right arm not solved", slow, fast, worst, got ? fig[4] : NAN);
	}
	RunFrames(1500);
	CHECK(LogLines("rider: the arms riding") - ridingBefore == 1, "and no second one this hold (%d)", LogLines("rider: the arms riding") - ridingBefore);
	g_onFrame = NULL;
	RunFrames(500);
	*(float *)(g_turnRadius + 0x30) = radius0;   /* steering off again: the turns on the spot are the game's */
	*(float *)(g_turnStand + 0x30) = stand0;
	*head = heading0;
	RunFrames(500);

	printf("arms: getting off: the ride's wrist line says how far the pole was faded:\n");
	int wristBefore = LogLines("rider: the left wrist turned at most");
	ArmsGetOff(400);
	{
		const char *line = LastLogLine("rider: the left wrist turned at most");
		float bars = NAN, logged = NAN, expected[3];
		const char *b = line ? strstr(line, "(the bars ") : NULL;
		const char *p = line ? strstr(line, "the elbow's pole ") : NULL;
		if (b)
			bars = strtof(b + strlen("(the bars "), NULL);
		if (p)
			logged = strtof(p + strlen("the elbow's pole "), NULL);
		float want = ExpectedPole(0, bars, g_armPoleIni, g_armPoleTurnIni, 10.0f, expected);
		CHECK(LogLines("rider: the left wrist turned at most") == wristBefore + 1 && p && strstr(p, "of the way to ArmPoleTurn") && fabsf(logged - want) < 0.02f,
		      "the left wrist's line: the pole %.2f of the way to ArmPoleTurn at its max (the bars %.1f: %.2f)", logged, bars, want);
	}

	printf("arms: ArmPoleTurn=0,0,0 for a ride (no fade), the bars 12 deg to the left:\n");
	RewriteIni("ArmPoleTurn=0.35,-0.3,-1.0", "ArmPoleTurn=0,0,0");
	ArmsGetOn(900);
	CHECK(LogLines("the inside arm's not faded as the bars turn (ArmPoleTurn 0,0,0)") >= 1, "the lean settings line says the inside arm isn't faded (ArmPoleTurn 0,0,0)");
	bar = ArmTurn(-27.0f, 1500, 10.0f, none, &k, &offE, &offP, &offT, &offLen);
	printf("  the bars %.2f deg: the elbow %.2f deg off ArmPole, %.2f off test 40's pole (offset %.1f)\n", bar, offP, offT, offLen);
	CHECK(bar > 11.5f && k == 0.0f && offP < 1.0f && offT > 2.0f && offLen > 2.0f, "at %.1f deg of the bars the inside elbow keeps ArmPole (%.2f deg off it): no fade", bar, offP);
	ArmTurnBack(27.0f, 1500, heading0);
	ArmsGetOff(300);
	RewriteIni("ArmPoleTurn=0,0,0", "ArmPoleTurn=0.35,-0.3,-1.0");

	/* The right arm (the fake's arm mirrored, as mode 0's HandPitch ride does it; TorsoLean,
	 * TorsoTwist and TorsoSideLean off: the mirrored shoulder sits far below the spine's joint):
	 * the inside one with the bars over to the right. */
	printf("arms: the arm mirrored to the right for a ride, the bars 12 deg to the right (the right arm inside), then to the left:\n");
	static const char *rightNames[3] = { "RArm_Hand [RHnd]", "RArm_UpperArm [RUar]", "RArm_ForeArm1 [RLar]" };
	uint8_t *leftNames[3];
	RewriteIni("TorsoLean=8", "TorsoLean=0");
	RewriteIni("TorsoTwist=0.75", "TorsoTwist=0");
	RewriteIni("TorsoSideLean=0.25", "TorsoSideLean=0");
	for (int i = 0; i < 3; i++) {
		leftNames[i] = *(uint8_t **)(g_bodyNodes[5 + i] + 0x10);
		*(uint8_t **)(g_bodyNodes[5 + i] + 0x10) = NewString(rightNames[i]);
	}
	g_armRight = true;
	SyncFakeWorld();
	ArmsGetOn(600);
	bar = ArmTurn(27.0f, 1500, 10.0f, g_armPoleTurnIni, &k, &offE, &offP, &offT, &offLen);
	printf("  the bars %.2f deg: k %.3f, the elbow %.2f deg off ArmPoleTurn (mirrored), %.2f off ArmPole (offset %.1f)\n", bar, k, offT, offP, offLen);
	CHECK(bar < -11.5f && k == 1.0f && offT < 1.0f && offP > 2.0f && offLen > 2.0f, "at %.1f deg of the bars the right arm is the inside one: all of ArmPoleTurn, x not mirrored (%.2f deg off it)", bar, offT);
	bar = ArmTurn(-27.0f, 3000, 10.0f, g_armPoleTurnIni, &k, &offE, &offP, &offT, &offLen);
	printf("  the bars %.2f deg: the elbow %.2f deg off ArmPole (offset %.1f)\n", bar, offP, offLen);
	CHECK(bar > 11.5f && k == 0.0f && offP < 1.0f && offLen > 0.3f && offT > 2.0f, "at %.1f deg the right arm is outside: ArmPole (%.2f deg off it, %.1f off ArmPoleTurn; near straight, the offset %.1f)", bar, offP, offT, offLen);
	ArmTurnBack(-27.0f, 1500, heading0);
	ArmsGetOff(300);
	for (int i = 0; i < 3; i++)
		*(uint8_t **)(g_bodyNodes[5 + i] + 0x10) = leftNames[i];
	g_armRight = false;
	SyncFakeWorld();
	RewriteIni("TorsoLean=0", "TorsoLean=8");
	RewriteIni("TorsoTwist=0", "TorsoTwist=0.75");
	RewriteIni("TorsoSideLean=0", "TorsoSideLean=0.25");
}

/* Mode 11 (test 40's finding 7, the ram; test 41's answers): CMB_RamScript, played by the
 * harness. 1 says yes 150 ms after an ask, 2 never answers, 3 says no 150 ms after (an ask
 * made before then is answered instead, as the script reads only the last one); on a hit it
 * "pushes" that actor (its plane taken away) 80 ms later, or, with g_ramStays, the actor stays
 * at the front wheel (a plane 100 ahead of the rider). Two actors: FF004D69 on g_ramPlanes[0]
 * and FF004D6A on [1]. */
#define RAM_HITS_KEPT 4
#define RAM_SAMPLES 400
typedef struct { int ask, who; float speed, ahead, clock, pushIn; } RamHitSeen;
static int g_ramScript, g_ramAsks, g_ramBadAsks, g_ramHits, g_ramLastSeen, g_ramLastHit, g_ramAnswerFor, g_ramFirstAsk, g_ramAsksOf[2];
static int g_ramAskNumber[16], g_ramAskWho[16];   /* the asks seen, and whom each was about */
static float g_ramClock, g_ramAskedAt = -1.0f, g_ramAskTimes[16], g_ramMinInput, g_ramMinAfter;
static RamHitSeen g_ramSeenHits[RAM_HITS_KEPT];
static float g_ramSampleT[RAM_SAMPLES], g_ramSampleIn[RAM_SAMPLES];   /* the input after the first hit, against the seconds since it */
static int g_ramSamples;
static bool g_ramStays;
static FakePlane *g_ramPlanes[2];
static float RamGlobal(int i) { return *(float *)(g_ramGlobalsFake[i] + 0x30); }
static float RamPlaneAhead(int i)   /* past the front wheel's edge (FrontAxle 99.6 + the radius 29.9) */
{
	const FakePlane *p = g_ramPlanes[i];
	return (PlayerPos()[0] - p->point[0]) * p->normal[0] + (PlayerPos()[1] - p->point[1]) * p->normal[1] - (99.6f + 29.9f);
}
static void FakeRamScript(float dt)
{
	g_ramClock += dt;
	int seen = (int)RamGlobal(2);
	if (seen != g_ramLastSeen) {
		g_ramLastSeen = seen;
		uint32_t id = ((uint32_t)RamGlobal(0) << 16) | (uint32_t)RamGlobal(1);
		int who = id == RAM_ACTOR_FORMID ? 0 : id == RAM_ACTOR2_FORMID ? 1 : -1;
		if (who < 0)
			g_ramBadAsks++;
		else
			g_ramAsksOf[who]++;
		if (!g_ramAsks)
			g_ramFirstAsk = seen;
		if (g_ramAsks < 16) {
			g_ramAskTimes[g_ramAsks] = g_ramClock;
			g_ramAskNumber[g_ramAsks] = seen;
			g_ramAskWho[g_ramAsks] = who;
		}
		g_ramAsks++;
		g_ramAskedAt = g_ramClock;
		g_ramAnswerFor = seen;
	}
	if (g_ramAskedAt >= 0.0f && g_ramClock - g_ramAskedAt >= 0.15f) {
		if (g_ramScript == 1 || g_ramScript == 3)
			*(float *)(g_ramGlobalsFake[3] + 0x30) = g_ramScript == 1 ? (float)g_ramAnswerFor : -(float)g_ramAnswerFor;
		g_ramAskedAt = -1.0f;
	}
	float in = MoveInput()[1];
	if (g_ramPlanes[0] && g_ramPlanes[0]->on && !g_ramHits && g_ramPlanes[0]->follow == 0.0f) {
		float ahead = RamPlaneAhead(0);
		if (ahead < 600.0f && ahead > 0.0f && in < g_ramMinInput)
			g_ramMinInput = in;   /* the last 600 before the first hit */
	}
	if (g_ramHits) {
		float since = g_ramClock - g_ramSeenHits[0].clock;
		if (since < 0.5f && in < g_ramMinAfter)
			g_ramMinAfter = in;   /* the half second after it */
		if (g_ramSamples < RAM_SAMPLES && since < 3.0f) {
			g_ramSampleT[g_ramSamples] = since;
			g_ramSampleIn[g_ramSamples++] = in;
		}
	}
	int hit = (int)RamGlobal(5);
	if (hit != g_ramLastHit) {
		g_ramLastHit = hit;
		if (g_ramHits < RAM_HITS_KEPT) {
			RamHitSeen *h = &g_ramSeenHits[g_ramHits];
			h->ask = hit;
			h->who = -1;
			for (int i = 0; i < g_ramAsks && i < 16; i++)
				if (g_ramAskNumber[i] == hit)
					h->who = g_ramAskWho[i];
			h->speed = RamGlobal(4);
			h->ahead = h->who >= 0 && g_ramPlanes[h->who] ? RamPlaneAhead(h->who) : 0.0f;
			h->clock = g_ramClock;
			h->pushIn = 0.08f;
		}
		g_ramHits++;
	}
	for (int k = 0; k < g_ramHits && k < RAM_HITS_KEPT; k++) {
		RamHitSeen *h = &g_ramSeenHits[k];
		if (h->pushIn < 0.0f)
			continue;
		h->pushIn -= dt;
		FakePlane *p = h->who >= 0 ? g_ramPlanes[h->who] : NULL;
		if (h->pushIn < 0.0f && p) {
			if (g_ramStays)
				p->follow = 100.0f;   /* stays at the front wheel: 100 ahead of the rider, wherever they go */
			else
				p->on = false;   /* pushed away */
		}
	}
}
static void RamGameFrame(float dt)
{
	if (g_ramScript)
		FakeRamScript(dt);
	FakeGameFrame(dt);
}

/* The plugin's input for a speed (its InputForSpeed, from test 22's measurements): what the
 * throttle held to a share of the top writes. */
static float PluginInputFor(float speed)
{
	static const float in[] = { 0.00f, 0.10f, 0.16f, 0.33f, 0.51f, 0.66f, 0.85f, 0.95f, 1.00f };
	static const float out[] = { 0.00f, 0.097f, 0.116f, 0.170f, 0.302f, 0.499f, 0.774f, 0.912f, 1.00f };
	if (!(speed > 0.0f))
		return 0.0f;
	for (int i = 1; i < 9; i++)
		if (speed <= out[i])
			return in[i - 1] + (speed - out[i - 1]) / (out[i] - out[i - 1]) * (in[i] - in[i - 1]);
	return 1.0f;
}

/* Actor `who` `dist` ahead along the heading, a capsule face 120 high (layer 30, its 3D the
 * actor's), on plane `who`. */
static void RamPlace(int who, float dist)
{
	float hh = PlayerHeading(), fw[2] = { sinf(hh), cosf(hh) };
	FakePlane *p = &g_planes[who];
	memset(p, 0, sizeof(*p));
	p->point[0] = PlayerPos()[0] + fw[0] * dist;
	p->point[1] = PlayerPos()[1] + fw[1] * dist;
	p->normal[0] = -fw[0];
	p->normal[1] = -fw[1];
	p->layer = 30;
	p->top = 120.0f;
	p->what = who ? g_actorObj2 : g_actorObj;
	p->on = true;
	g_ramPlanes[who] = p;
}

/* The bookkeeping cleared, the script as asked; ridden with W at keysY for ms. */
static void RamGo(float keysY, int script, int ms)
{
	g_ramAsks = g_ramBadAsks = g_ramHits = g_ramSamples = 0;
	g_ramAsksOf[0] = g_ramAsksOf[1] = 0;
	g_ramAskedAt = -1.0f;
	g_ramLastSeen = (int)RamGlobal(2);
	g_ramLastHit = (int)RamGlobal(5);
	g_ramMinInput = g_ramMinAfter = 2.0f;
	g_ramScript = script;
	Keys(0.0f, keysY);
	RunFrames(ms);
}

static void RamRide(float dist, float keysY, int script, int ms)
{
	g_ramPlanes[1] = NULL;
	RamPlace(0, dist);
	RamGo(keysY, script, ms);
}

static void RamRideEnd(void)
{
	Keys(0.0f, 0.0f);
	for (int i = 0; i < 3; i++) {
		g_planes[i].on = false;
		g_planes[i].follow = 0.0f;
	}
	g_ramScript = 0;
	g_ramStays = false;
	RunFrames(3000);   /* rolled off, at rest */
}

static void RamUpToSpeed(float keysY)
{
	Keys(0.0f, keysY);
	RunFrames(3500);
}

/* Off and on again (the [Ram] keys are read again on getting on). */
static void RamGetOffAndOn(void)
{
	Keys(0.0f, 0.0f);
	SetLive(0.0f);
	SetCamera(0.0f);
	SetTilt(0.0f);
	RunFrames(400);
	SetLive(45.0f);
	SetCamera(300.0f);
	SetTilt(30.0f);
	RunFrames(1000);
}

/* Finding 7 (test 40's wish): a hostile actor the bike hits at speed is knocked over. */
static void RamTests(void)
{
	float *head = (float *)(g_player + 0xC8), p0[2], left;
	*(float *)(g_turnRadius + 0x30) = 180.0f;   /* steering on: the input hook (and the throttle) with it */
	*(float *)(g_turnSlow + 0x30) = 50.0f;
	*(float *)(g_turnStand + 0x30) = 60.0f;
	SetNormal(0.0f, 0.0f, 1.0f);
	SetState(0);
	FlatGround();
	g_camYaw = *head;
	g_handlerStyle = 2;
	g_honour = 4;
	Keys(0.0f, 0.0f);
	g_onFrame = RamGameFrame;
	printf("rams: getting on, on flat ground: the settings line, the globals found:\n");
	SetLive(45.0f);
	SetCamera(300.0f);
	SetTilt(30.0f);
	RunFrames(1500);
	CHECK(LogLines("  ram: Enabled=1 ActorLook=0.8 Lead=0.06 Pass=1 MaxSize=1 NoKnockdowns=1 AskAgain=0.4 AskAgainNo=1 HitKeep=0.6 HitHold=0.4: on, the bike losing speed at a hit") == 1 &&
	      LogLines("rams: not all of CMB_RamSeenHi") == 0, "the ram settings line at load (on, HitKeep 0.6 for 0.4 s), the globals all found");

	printf("rams: the actor 1500 ahead (layer 30, its 3D's user data an Actor FF004D69 of a medium race), at full speed, the script says yes: asked once, the throttle open, the hit told %g s of the speed before the wheel, pushed:\n", 0.06);
	RamUpToSpeed(1.0f);
	float fullIn = MoveInput()[1];
	int asksBefore = LogLines("rams: FF004D69 (race RaiderTestRace: medium) seen"), seenBefore = (int)RamGlobal(2);
	Mark(p0);
	RamRide(1500.0f, 1.0f, 1, 1900);
	float rodeOn = Moved(p0);
	char okLine[96], hitLine[96];
	snprintf(okLine, sizeof(okLine), "may be knocked over, the script says (ask %d)", seenBefore + 1);
	snprintf(hitLine, sizeof(hitLine), "told the script (ask %d)", seenBefore + 1);
	const RamHitSeen *h0 = &g_ramSeenHits[0];
	CHECK(g_ramAsks == 1 && g_ramBadAsks == 0 && g_ramFirstAsk == seenBefore + 1, "asked once (%d), about FF004D69 (%d other), ask %d", g_ramAsks, g_ramBadAsks, g_ramFirstAsk);
	CHECK(LogLines("asked the script (ask 58)") == 1, "the ride's first ask was 58: on from the save's 57");
	CHECK(g_ramHits == 1 && h0->ask == g_ramFirstAsk && h0->speed > 850.0f && h0->speed < 950.0f, "one hit (%d), of ask %d, at %.0f a second", g_ramHits, h0->ask, h0->speed);
	CHECK(h0->ahead > 0.06f * 900.0f - 25.0f && h0->ahead < 0.06f * 900.0f + 10.0f, "told %.0f before the front wheel's edge reached it (Lead: %.0f)", h0->ahead, 0.06f * 900.0f);
	CHECK(g_ramMinInput >= 0.97f * fullIn, "the throttle open all the way in (the least input %.3f of %.3f within 600 of it)", g_ramMinInput, fullIn);
	CHECK(rodeOn > 1500.0f, "rode on through: %.0f in 1.9 s", rodeOn);
	CHECK(LogLines("rams: FF004D69 (race RaiderTestRace: medium) seen") == asksBefore + 1 && LogLines(hitLine) == 1 &&
	      LogLines("rams: FF004D69 gone from the rays") >= 1 && LogLines(okLine) == 1,
	      "the log: seen, may be knocked over, hit, gone");
	/* Test 41's answer: the bike loses speed at the hit, the throttle held to 60% of the speed
	 * at the hit for 0.4 s: the input the plugin writes for that (its curve), then up again. */
	float held = PluginInputFor(0.6f * h0->speed / 900.0f), heldMax = -1.0f, heldMin = 2.0f, freeAt = -1.0f;
	for (int i = 0; i < g_ramSamples; i++) {
		float t = g_ramSampleT[i], in = g_ramSampleIn[i];
		if (t >= 0.05f && t <= 0.35f) {
			heldMax = in > heldMax ? in : heldMax;
			heldMin = in < heldMin ? in : heldMin;
		}
		if (t > 0.05f && freeAt < 0.0f && in > held + 0.005f)
			freeAt = t;
	}
	CHECK(fabsf(heldMax - held) < 0.01f && fabsf(heldMin - held) < 0.01f, "the speed lost at the hit: 0.05 to 0.35 s after it the input %.3f to %.3f, the plugin's for 60%% of %.0f (%.3f; %.3f at full)", heldMin, heldMax, h0->speed,
	      held, fullIn);
	CHECK(freeAt > 0.37f && freeAt < 0.55f, "held for 0.4 s: the input above it again %.2f s after the hit", freeAt);
	CHECK(LogLines("told the script (ask 58); the throttle held to 60% of it (") == 1, "the hit's line says so (\"...told the script (ask 58); the throttle held to 60%% of it (N a second) for 0.40 s\")");
	RunFrames(2500);
	CHECK(MoveInput()[1] >= 0.97f * fullIn, "then built up again: 2.5 s later the input %.3f (%.3f at full)", MoveInput()[1], fullIn);
	RamRideEnd();

	printf("rams: the same, the script never answers: braked for as before, asked again every 0.4 s:\n");
	RamUpToSpeed(1.0f);
	RamRide(1500.0f, 1.0f, 2, 3500);
	left = RamPlaneAhead(0);
	CHECK(g_ramHits == 0 && left > -15.0f && left < 80.0f && MoveInput()[1] < 0.05f, "no hit (%d), stops %.1f short of it at the front wheel, next to no input (%g)", g_ramHits, left, MoveInput()[1]);
	CHECK(g_ramAsks >= 4 && g_ramAsks <= 12, "asked %d times in 3.5 s", g_ramAsks);
	RamRideEnd();

	printf("rams: the script says no: braked for, asked again a second later at the soonest (AskAgainNo):\n");
	RamUpToSpeed(1.0f);
	RamRide(1500.0f, 1.0f, 3, 3500);
	left = RamPlaneAhead(0);
	CHECK(g_ramHits == 0 && left > -15.0f && left < 80.0f && MoveInput()[1] < 0.05f, "no hit (%d), stops %.1f short, next to no input (%g)", g_ramHits, left, MoveInput()[1]);
	CHECK(g_ramAsks >= 2 && g_ramAskTimes[1] - g_ramAskTimes[0] > 0.95f, "asked %d times, the second %.2f s after the first", g_ramAsks, g_ramAsks >= 2 ? g_ramAskTimes[1] - g_ramAskTimes[0] : 0.0f);
	RamRideEnd();

	uint8_t *races[2] = { g_raceBig, g_raceNoKnock };
	const char *lines[2] = { "is too big (MaxSize)", "can't be knocked down (No Knockdowns)" };
	for (int i = 0; i < 2; i++) {
		printf("rams: an actor of a race %s: never asked about, braked for:\n", i ? "flagged No Knockdowns" : "of size 3 (extra large; MaxSize 1)");
		*(uint8_t **)(g_ramActor + 0x418) = races[i];
		int before = LogLines(lines[i]);
		RamUpToSpeed(1.0f);
		RamRide(1500.0f, 1.0f, 1, 3000);
		left = RamPlaneAhead(0);
		CHECK(g_ramAsks == 0 && g_ramHits == 0 && left > -15.0f && left < 80.0f, "no ask (%d), no hit, stops %.0f short", g_ramAsks, left);
		CHECK(LogLines(lines[i]) == before + 1, "one line: \"%s\"", lines[i]);
		RamRideEnd();
	}
	*(uint8_t **)(g_ramActor + 0x418) = g_raceMedium;

	printf("rams: CMB_RamEnemies 0 (the MCM's switch off): never asked about, braked for:\n");
	*(float *)(g_ramGlobalsFake[6] + 0x30) = 0.0f;
	RamUpToSpeed(1.0f);
	RamRide(1500.0f, 1.0f, 1, 3000);
	left = RamPlaneAhead(0);
	CHECK(g_ramAsks == 0 && g_ramHits == 0 && left > -15.0f && left < 80.0f, "no ask (%d), no hit, stops %.0f short", g_ramAsks, left);
	RamRideEnd();
	*(float *)(g_ramGlobalsFake[6] + 0x30) = 1.0f;

	printf("rams: at about 315 a second (W at 0.35; CMB_RamMinSpeed 450), the script says yes: too slow, braked for, no hit:\n");
	int slowBefore = LogLines("under CMB_RamMinSpeed's 450");
	RamUpToSpeed(0.35f);
	RamRide(900.0f, 0.35f, 1, 4000);
	left = RamPlaneAhead(0);
	CHECK(g_ramAsks >= 1 && g_ramHits == 0 && left > -15.0f && left < 80.0f, "asked (%d), no hit (%d), stops %.0f short", g_ramAsks, g_ramHits, left);
	CHECK(LogLines("under CMB_RamMinSpeed's 450") == slowBefore + 1, "one \"under CMB_RamMinSpeed\" line");
	RamRideEnd();

	printf("rams: hit, but the actor stays at the front wheel (not pushed away): let by for Pass (1 s), then braked for:\n");
	g_ramStays = true;
	RamUpToSpeed(1.0f);
	int stillBefore = LogLines("after the hit: let by");
	RamRide(1500.0f, 1.0f, 1, 1800);
	float since = g_ramClock - g_ramSeenHits[0].clock, inWithin = MoveInput()[1], heldStays = PluginInputFor(0.6f * g_ramSeenHits[0].speed / 900.0f);
	CHECK(g_ramHits == 1 && since > 0.2f && since < 0.95f && inWithin >= heldStays - 0.01f, "%.2f s after the hit the input is %.3f (open: the hit's 60%% hold, %.3f, or on its way up from it)", since, inWithin, heldStays);
	RunFrames(1200);
	since = g_ramClock - g_ramSeenHits[0].clock;
	CHECK(since > 1.1f && MoveInput()[1] == 0.0f, "%.2f s after it, none (%.3f): braked for", since, MoveInput()[1]);
	CHECK(LogLines("after the hit: let by") >= stillBefore + 2, "\"still ... after the hit: let by\" lines (%d)", LogLines("after the hit: let by") - stillBefore);
	RamRideEnd();

	printf("rams: a yes, with a wall (layer 1) 20 behind the actor: the face rays see the wall through it, the bike eased off for the wall before it reached the actor (hit, if at all, well under 900) and stopped short of the wall:\n");
	RamUpToSpeed(1.0f);
	FakePlane *wall = &g_planes[2];
	{
		float hh = PlayerHeading(), fw[2] = { sinf(hh), cosf(hh) };
		memset(wall, 0, sizeof(*wall));
		wall->point[0] = PlayerPos()[0] + fw[0] * 1520.0f;
		wall->point[1] = PlayerPos()[1] + fw[1] * 1520.0f;
		wall->normal[0] = -fw[0];
		wall->normal[1] = -fw[1];
		wall->layer = 1;
		wall->on = true;
	}
	int wallBefore = LogLines("(FakeWall, layer 1), the throttle eased to"), passBefore = LogLines("an actor to be knocked over");
	RamRide(1500.0f, 1.0f, 1, 4000);
	left = (PlayerPos()[0] - wall->point[0]) * wall->normal[0] + (PlayerPos()[1] - wall->point[1]) * wall->normal[1] - (99.6f + 29.9f);
	CHECK(g_ramAsks == 1 && (g_ramHits == 0 || g_ramSeenHits[0].speed < 600.0f) && left > -15.0f && left < 80.0f && MoveInput()[1] < 0.05f,
	      "asked (%d); %d hit(s)%s%.0f; stops %.0f short of the wall, next to no input (%g)", g_ramAsks, g_ramHits, g_ramHits ? ", at " : "", g_ramHits ? g_ramSeenHits[0].speed : 0.0f, left, MoveInput()[1]);
	CHECK(LogLines("(FakeWall, layer 1), the throttle eased to") > wallBefore && LogLines("an actor to be knocked over") > passBefore,
	      "\"rays: a wall ahead\" lines name FakeWall (%d new), and a ray passed through the actor (%d)", LogLines("(FakeWall, layer 1), the throttle eased to") - wallBefore,
	      LogLines("an actor to be knocked over") - passBefore);
	RamRideEnd();

	printf("rams: two actors 50 apart (FF004D69 at 1500, FF004D6A at 1550; HitHold=0 written, read again on getting on): both asked (the actor ray through the first), both hit, told 0.12 s apart at least, the throttle open throughout:\n");
	RewriteIni("HitHold=0.4", "HitHold=0");
	RamGetOffAndOn();
	CHECK(LogLines("HitKeep=0.6 HitHold=0: on, the speed kept at a hit (HitHold=0 or HitKeep=1) (read again on getting on)") == 1, "the settings line again: HitHold=0, the speed kept");
	RamUpToSpeed(1.0f);
	fullIn = MoveInput()[1];
	int queuedBefore = LogLines("so its 0.1 s poll reads both");
	g_ramPlanes[1] = NULL;
	RamPlace(0, 1500.0f);
	RamPlace(1, 1550.0f);
	RamGo(1.0f, 1, 2200);
	const RamHitSeen *h1 = &g_ramSeenHits[1];
	h0 = &g_ramSeenHits[0];
	float gap = h1->clock - h0->clock;
	CHECK(g_ramAsksOf[0] == 1 && g_ramAsksOf[1] == 1 && g_ramBadAsks == 0, "asked once about each (%d, %d; %d other)", g_ramAsksOf[0], g_ramAsksOf[1], g_ramBadAsks);
	CHECK(g_ramHits == 2 && h0->who == 0 && h1->who == 1, "two hits (%d): FF004D69's first, then FF004D6A's (%d, %d)", g_ramHits, h0->who, h1->who);
	CHECK(gap >= 0.115f && gap < 0.2f, "told %.3f s apart (at least 0.12: the script's 0.1 s poll reads both)", gap);
	CHECK(LogLines("so its 0.1 s poll reads both") == queuedBefore + 1 && LogLines("rams: FF004D6A's hit told the script (ask") == 1, "the second hit waited: a \"so its 0.1 s poll reads both\" line, then \"FF004D6A's hit told the script\"");
	CHECK(g_ramMinInput >= 0.97f * fullIn && g_ramMinAfter >= 0.97f * fullIn, "HitHold=0: the throttle open all the way in (%.3f) and through both hits (%.3f; %.3f at full)", g_ramMinInput, g_ramMinAfter, fullIn);
	RamRideEnd();
	RewriteIni("HitHold=0", "HitHold=0.4");

	printf("rams: [Ram] Enabled=0 written (read again on getting on): never asked about, braked for as before test 41:\n");
	RewriteIni("Enabled=1", "Enabled=0");
	RamGetOffAndOn();
	CHECK(LogLines("  ram: Enabled=0 ") == 1 && LogLines("off, no actor asked about, every one braked for as before test 41 (read again on getting on)") == 1, "the settings line: off");
	RamUpToSpeed(1.0f);
	RamRide(1500.0f, 1.0f, 1, 3000);
	left = RamPlaneAhead(0);
	CHECK(g_ramAsks == 0 && g_ramHits == 0 && left > -15.0f && left < 80.0f && MoveInput()[1] < 0.05f, "no ask (%d), no hit, stops %.0f short, next to no input (%g)", g_ramAsks, left, MoveInput()[1]);
	RamRideEnd();
	RewriteIni("Enabled=0", "Enabled=1");
	RamGetOffAndOn();

	printf("rams: the 3D's user data a placed object, not an actor: never asked about, one line:\n");
	static const char *refrNames[] = { ".?AVTESObjectREFR@@", ".?AVTESForm@@" };
	uint8_t *refr = (uint8_t *)NewObject(MakeClass(refrNames, 2), 0x200);
	refr[0x1A] = 0x40;
	*(uint8_t **)(g_actorObj + 0x110) = refr;
	int lostBefore = LogLines("gives no actor: the user data of 'SkeletonExport' (+0x110) is a .?AVTESObjectREFR@@ (form type 0x40)");
	Send(3, 1);   /* a load: a new ride, the "first time" lines again */
	RunFrames(400);
	RamUpToSpeed(1.0f);
	RamRide(1500.0f, 1.0f, 1, 3000);
	left = RamPlaneAhead(0);
	CHECK(g_ramAsks == 0 && left > -15.0f && left < 80.0f, "no ask (%d), stops %.0f short", g_ramAsks, left);
	CHECK(LogLines("gives no actor: the user data of 'SkeletonExport' (+0x110) is a .?AVTESObjectREFR@@ (form type 0x40)") == lostBefore + 1, "one \"gives no actor\" line");
	RamRideEnd();
	*(uint8_t **)(g_actorObj + 0x110) = g_ramActor;
	g_ramPlanes[0] = g_ramPlanes[1] = NULL;
	g_onFrame = NULL;
}

/* ------------------------------------------------------------------------- */
/* Mode 12: backing level or down follows the ground (test 40's finding 6)   */
/* ------------------------------------------------------------------------- */

/* The ground under a point, as the vertical rays see it: the profile (with its ripple) when one
 * is on, else the plane. */
static float FakeGroundAt(float x, float y)
{
	if (g_profileOn)
		return ProfileGround(x, y, true);
	return g_groundZ + g_slopeK * ((x - g_slopeO[0]) * g_slopeD[0] + (y - g_slopeO[1]) * g_slopeD[1]);
}

/* A physics-lite controller (test 40's in-air phase, opt-in): while it isn't supported it falls
 * at 686 units/s^2 and stops on the ground; pushed under the ground it's put back on it (the
 * depth kept); its supported bit and state (+0x300's 0x400, +0x2C0) by the feet within 0.3 of
 * the ground (g_physBit -1) or held set (1, state 0) or clear (0, state 2); its velocity's z
 * what GetLinearVelocityImpl gives. Without g_physOn only the bit and the state are set: the
 * plugin's steps alone move the feet up and down. */
static bool g_physOn, g_physSup;
static int g_physBit = 1;
static float g_physV, g_physUnder;
static void BackingFrame(float dt)
{
	FakeGameFrame(dt);
	float *p = PlayerPos(), g = FakeGroundAt(p[0], p[1]);
	if (g_physOn) {
		float z0 = p[2];
		if (p[2] < g) {
			if (g - p[2] > g_physUnder)
				g_physUnder = g - p[2];
			p[2] = g;
			g_physV = 0.0f;
		} else if (!g_physSup) {
			g_physV -= 686.0f * dt;
			p[2] += g_physV * dt;
			if (p[2] < g) {
				p[2] = g;
				g_physV = 0.0f;
			}
		}
		g_physGame += p[2] - z0;
	}
	g_physSup = g_physBit >= 0 ? g_physBit == 1 : p[2] - g <= 0.3f;
	if (g_physSup)
		g_physV = 0.0f;
	SetSupported(g_physSup);
	SetState(g_physSup ? 0 : 2);
	g_fakeVel[2] = g_physV * HAVOK;
}

/* The ground from the player along the way back, a profile of segments, each {len, deg}: `len`
 * units at `deg` down (0: level), level before the player and past the last. */
static void BackProfile(const float (*seg)[2], int n)
{
	float h = PlayerHeading(), u = 0.0f, z = 0.0f;
	g_slopeO[0] = PlayerPos()[0];
	g_slopeO[1] = PlayerPos()[1];
	g_slopeD[0] = -sinf(h);
	g_slopeD[1] = -cosf(h);
	g_slopeK = 0.0f;
	g_groundZ = PlayerPos()[2];
	g_profileN = 0;
	g_profileU[g_profileN] = 0.0f;
	g_profileZ[g_profileN++] = 0.0f;
	for (int i = 0; i < n && g_profileN < 12; i++) {
		u += seg[i][0];
		z -= seg[i][0] * tanf(seg[i][1] / DEG);
		g_profileU[g_profileN] = u;
		g_profileZ[g_profileN++] = z;
	}
	g_rippleAmp = 0.0f;
	g_profileOn = true;
}
static void BackLevel(void)   /* flat ground where the player is, no profile */
{
	g_profileOn = false;
	g_profileN = 0;
	g_rippleAmp = 0.0f;
	g_shelfOn = false;
	g_shelfHeight = g_shelfAhead = 0.0f;
	g_shelfRadius = 60.0f;
	FlatGround();
}

/* Back held for ms, every step recorded; then let go (the keys are kept 0.2 s) and at rest. */
static void BackRecord(int ms)
{
	g_recN = 0;
	g_physGame = 0.0f;
	g_physUnder = 0.0f;
	g_rec = true;
	Keys(0.0f, -1.0f);
	RunFrames(ms);
	g_rec = false;
}
static void BackLetGo(void)
{
	Keys(0.0f, 0.0f);
	RunFrames(500);
}

/* Over the recorded steps k0..k1-1: the most the feet were off the ground (signed, the worst),
 * the share of steps whose dz was 0 (under 0.005), the game's share of the height lost, the 99th
 * percentile and the largest change of the vertical speed from one step to the next (the z after
 * a step over the time since the one before), and the largest |dz| over the step's length. */
typedef struct { float worstGap, zeroShare, gameShare, dv99, dvMax, slopeMax, dzMax, descent; int n; } BackStats;
static int CmpFloat(const void *a, const void *b) { float x = *(const float *)a, y = *(const float *)b; return x < y ? -1 : x > y; }
static BackStats BackStatsOf(int k0, int k1)
{
	static float dv[REC_MAX];
	BackStats st;
	memset(&st, 0, sizeof(st));
	if (k0 < 1)
		k0 = 1;
	if (k1 > g_recN)
		k1 = g_recN;
	int zeros = 0, ndv = 0;
	float vzPrev = 0.0f;
	bool havePrev = false;
	for (int k = k0; k < k1; k++) {
		st.n++;
		if (fabsf(g_recGap[k]) > fabsf(st.worstGap))
			st.worstGap = g_recGap[k];
		zeros += fabsf(g_recDz[k]) < 0.005f;
		if (fabsf(g_recDz[k]) > st.dzMax)
			st.dzMax = fabsf(g_recDz[k]);
		if (g_recStep[k] > 0.05f && fabsf(g_recDz[k]) / g_recStep[k] > st.slopeMax)
			st.slopeMax = fabsf(g_recDz[k]) / g_recStep[k];
		double t = g_recT[k] - g_recT[k - 1];
		if (t > 0.0005) {
			float vz = (g_recZ[k] - g_recZ[k - 1]) / (float)t;
			if (havePrev)
				dv[ndv++] = fabsf(vz - vzPrev);
			vzPrev = vz;
			havePrev = true;
		}
	}
	if (k1 > k0) {
		st.descent = g_recZ[k1 - 1] - g_recZ[k0 - 1];
		st.gameShare = st.descent != 0.0f ? (g_recGame[k1 - 1] - g_recGame[k0 - 1]) / st.descent : 0.0f;
	}
	st.zeroShare = st.n ? (float)zeros / (float)st.n : 0.0f;
	if (ndv) {
		qsort(dv, ndv, sizeof(float), CmpFloat);
		st.dv99 = dv[(int)(0.99f * (float)(ndv - 1))];
		st.dvMax = dv[ndv - 1];
	}
	return st;
}
static int BackFirstPast(float u)   /* the first recorded step with the feet past u along the profile */
{
	for (int k = 0; k < g_recN; k++)
		if (g_recU[k] > u)
			return k;
	return g_recN;
}

static const float g_browDip[5][2] = { { 40.0f, 0.0f }, { 80.0f, 10.0f }, { 100.0f, 30.0f }, { 180.0f, 10.0f }, { 60.0f, 0.0f } };   /* test 40's slopes, about 6 to 32 deg (the analysis's model) */
static const float g_slope20[2][2] = { { 20.0f, 0.0f }, { 400.0f, 20.0f } };

/* N1: down a brow and a dip with the controller supported all the way, no physics (the plugin's
 * steps alone move the feet). */
static BackStats BackBrowDip(void)
{
	BackLevel();
	BackProfile(g_browDip, 5);
	g_physOn = false;
	g_physBit = 1;
	RunFrames(300);
	BackRecord(5300);
	BackLetGo();
	return BackStatsOf(1, BackFirstPast(440.0f));
}
/* N2: down 20 deg with the controller in the air all the way (its bit clear, state 2), the
 * physics-lite fall on: test 40's in-air phase. Measured on the slope, 30 to 400 along. */
static BackStats BackInTheAir(void)
{
	BackLevel();
	BackProfile(g_slope20, 2);
	g_physOn = true;
	g_physBit = 0;
	RunFrames(300);
	BackRecord(5000);
	BackLetGo();
	g_physOn = false;
	g_physBit = 1;
	return BackStatsOf(BackFirstPast(30.0f), BackFirstPast(390.0f));
}
/* N3: level, a hole of 2.0 round the feet (radius 20: the window's, the feet's rays in it, the
 * ground 55 behind and the wheels' contacts outside), supported for 1 s, then the bit clear and
 * state 2 for 0.5 s (a flip into the air): how far the feet moved after the flip. */
static float BackFlip(void)
{
	BackLevel();
	g_shelfOn = true;
	g_shelfHeight = -2.0f;
	g_shelfAhead = 0.0f;
	g_shelfRadius = 20.0f;
	g_physOn = false;
	g_physBit = 1;
	RunFrames(300);
	BackRecord(1000);
	int k0 = g_recN;
	float z0 = PlayerPos()[2], worst = 0.0f;
	g_physBit = 0;
	g_rec = true;
	RunFrames(500);
	g_rec = false;
	for (int k = k0; k < g_recN; k++)
		if (fabsf(g_recZ[k] - z0) > fabsf(worst))
			worst = g_recZ[k] - z0;
	BackLetGo();
	g_physBit = 1;
	BackLevel();
	return worst;
}

/* N6: a ledge 15 down 20 behind, the fake's controller supported by its feet (within 0.3) and
 * falling when not: the worst gap after a step on the upper ground, the gap over the lower one
 * at the end (99: never got past) and the largest step down. */
static float BackLedge(float *lowerGap, float *dzMax)
{
	static const float ledge[3][2] = { { 20.0f, 0.0f }, { 0.002f, 89.9924f }, { 200.0f, 0.0f } };   /* 15 down over 0.002 */
	BackLevel();
	BackProfile(ledge, 3);
	g_physOn = true;
	g_physBit = -1;
	RunFrames(300);
	BackRecord(1500);
	float upper = 0.0f;
	int kPast = BackFirstPast(29.0f);
	for (int k = 0; k < kPast; k++)
		if (g_recU[k] < 20.0f && fabsf(g_recGap[k]) > fabsf(upper))
			upper = g_recGap[k];
	*lowerGap = kPast < g_recN ? PlayerPos()[2] - FakeGroundAt(PlayerPos()[0], PlayerPos()[1]) : 99.0f;
	*dzMax = BackStatsOf(1, g_recN).dzMax;
	BackLetGo();
	g_physOn = false;
	g_physBit = 1;
	BackLevel();
	return upper;
}

static void BackingTests(void)
{
	float *head = (float *)(g_player + 0xC8);
	*(float *)(g_turnRadius + 0x30) = 180.0f;   /* steering on: the input hook with it */
	*(float *)(g_turnSlow + 0x30) = 50.0f;
	*(float *)(g_turnStand + 0x30) = 60.0f;
	SetNormal(0.0f, 0.0f, 1.0f);
	BackLevel();
	g_physOn = false;
	g_physBit = 1;
	g_camYaw = *head;
	g_handlerStyle = 2;
	g_honour = 4;
	Keys(0.0f, 0.0f);
	g_onFrame = BackingFrame;
	printf("backing: getting on: the reverse's settings line:\n");
	SetLive(60.0f);
	SetCamera(300.0f);
	SetTilt(30.0f);
	RunFrames(1500);
	CHECK(LogLines("  reverse: BackFollow=10 BackClose=0.1: going back level or down, each step follows the ground's slope over 10 units centred on its middle") == 1,
	      "BackFollow=10 BackClose=0.1 at load, said in plain words");

	printf("backing (N1): down a brow and a dip (flat 40, 10 deg for 80, 30 for 100, 10 for 180, flat 60), the controller supported all the way, no physics: the feet kept on the ground:\n");
	int startsBefore = LogLines("reverse: a push back starts, the controller supported; its capsule radius 18.0, height 128.0, step height 31.0, cast depth 33.5 (+0x370/+0x374/+0x424/+0x430), gravity ");
	int windowBefore = LogLines("by the window (the ground ");
	BackStats n1 = BackBrowDip();
	CHECK(n1.n > 200 && g_recU[g_recN - 1] > 400.0f && fabsf(n1.worstGap) < 0.7f, "the feet %+.2f from the ground at the worst over %d steps, back %.0f (the window's corner cut at 10 to 30 deg is 0.5)",
	      n1.worstGap, n1.n, g_recU[g_recN - 1]);
	CHECK(LogLines("reverse: a push back starts, the controller supported; its capsule radius 18.0, height 128.0, step height 31.0, cast depth 33.5 (+0x370/+0x374/+0x424/+0x430), gravity ") == startsBefore + 1,
	      "one push-start line: the controller supported, its capsule's radius, height, step height and cast depth, its gravity");
	CHECK(LogLines("by the window (the ground ") > windowBefore + 10, "the trace's rays lines say the step followed the window (%d lines)", LogLines("by the window (the ground ") - windowBefore);

	printf("backing (N2): down 20 deg with the controller in the air all the way (its bit clear, state 2), the fake's controller falling at 686 a second squared when over the ground: the plugin carries it down, not the game's gravity:\n");
	int heightBefore = LogLines("  height: z ");
	BackStats n2 = BackInTheAir();
	CHECK(n2.n > 200 && n2.zeroShare <= 0.10f, "the step's dz 0 in %.0f%% of %d steps (test 40's rule: most; 47 of 69 in-air lines read -0.00)", 100.0f * n2.zeroShare, n2.n);
	CHECK(n2.descent < -100.0f && n2.gameShare <= 0.10f, "the game's fall did %.0f%% of the %.0f down", 100.0f * n2.gameShare, -n2.descent);
	CHECK(n2.dv99 <= 10.0f, "the vertical speed changed %.1f a second from one step to the next at the 99th percentile (%.1f at most)", n2.dv99, n2.dvMax);
	float oursLogged = LastLogNumber("(ours "), gameLogged = LastLogNumber("the game's ");
	CHECK(LogLines("  height: z ") > heightBefore + 10 && oursLogged < -3.0f && fabsf(gameLogged) < 0.15f * fabsf(oursLogged),
	      "the trace's height lines (%d) split it: the last ours %+.1f, the game's %+.1f", LogLines("  height: z ") - heightBefore, oursLogged, gameLogged);

	printf("backing (N3): level, a gap of 2.0 under the feet (a hole round them) kept with the controller supported for 1 s, then it says it's in the air: nothing closed (its own clearance is 2.0):\n");
	int flipsBefore = LogLines("reverse: the controller in the air after ");
	float n3 = BackFlip();
	CHECK(fabsf(n3) < 0.1f, "the feet %+.2f from where they were in the 0.5 s after the flip (test 40's rule: down 1.5 at once)", n3);
	CHECK(LogLines("reverse: the controller in the air after ") == flipsBefore + 1 && LogLines("s supported (gap +2.0, own +2.0): closing 0.00 (flip 1 of this push)") >= 1,
	      "the flip's line: in the air after about 1 s supported (gap +2.0, own +2.0): closing 0.00 (flip 1 of this push)");

	printf("backing (N5): level with a ripple of 0.5 over 4 units under the vertical rays, supported: the window averages it out:\n");
	BackLevel();
	BackProfile(NULL, 0);
	g_rippleAmp = 0.5f;
	g_rippleWave = 4.0f;
	RunFrames(300);
	float z5 = PlayerPos()[2];
	BackRecord(3000);
	BackStats n5 = BackStatsOf(1, g_recN);
	float drift5 = PlayerPos()[2] - z5, off5 = 0.0f, longSteps = 0.0f;
	int nLong = 0;
	for (int k = 0; k < g_recN; k++) {
		if (fabsf(g_recZ[k] - z5) > fabsf(off5))
			off5 = g_recZ[k] - z5;
		if (g_recStep[k] > 1.0f) {   /* a frame of over 12 ms (Wine's are 5 mostly): such a step may be off by 0.1 of it, the window's slope here 0.1 at most */
			longSteps += g_recStep[k];
			nLong++;
		}
	}
	BackLetGo();
	CHECK(n5.n > 100 && fabsf(drift5) < 0.3f + 0.1f * longSteps && fabsf(off5) < 0.3f + 0.1f * longSteps, "after 3 s the feet %+.2f from the start (%+.2f at the most) over %d steps (within 0.3, and 0.1 of each of the %d steps over 1 long: %.2f more)",
	      drift5, off5, n5.n, nLong, 0.1f * longSteps);
	CHECK(n5.slopeMax <= 0.12f, "no step's dz over %.2f of its length (the window's slope on this ripple is 0.10 at most, the ripple's own 0.79; %.3f the largest dz)", n5.slopeMax, n5.dzMax);
	BackLevel();

	printf("backing (N6): an edge, a ledge 15 down 20 behind, the fake's controller supported by its feet and falling when not: no follow over it (the feet never pushed into the ground above it), gravity and the capped closing take it down:\n");
	int edgeBefore = LogLines(": an edge (the ground ");
	float lowerGap, dzMax, upper = BackLedge(&lowerGap, &dzMax);
	CHECK(fabsf(upper) < 0.05f, "on the upper ground the feet %+.2f from it after a step at the worst (the window across the ledge reads 1.5 down a unit: an edge, no follow)", upper);
	CHECK(lowerGap < 0.5f && lowerGap > -0.5f && g_physUnder < 0.5f, "past it, down on the lower ground: %+.2f over it at the end, %.2f under it at the most", lowerGap, g_physUnder);
	CHECK(dzMax <= 3.001f, "no step down more than 3 (%.2f the most)", dzMax);
	printf("  (%d \"an edge\" lines in the trace; the edge lasts about 0.2 s, the trace every 0.25 s)\n", LogLines(": an edge (the ground ") - edgeBefore);
	BackLevel();

	printf("backing (N7): level, a pit 3 across 6 behind the player (no ground within 52 under the window's ray behind the step): the slope 55 back after 0.1 s, the feet level:\n");
	g_shelfOn = true;
	g_shelfHeight = -100.0f;
	g_shelfAhead = -6.0f;
	g_shelfRadius = 3.0f;
	RunFrames(300);
	float z7 = PlayerPos()[2];
	int fallbackBefore = LogLines("by the slope 55 back (a window ray found no ground for over 0.1 s)");
	BackRecord(1500);
	float off7 = 0.0f;
	for (int k = 0; k < g_recN; k++)
		if (fabsf(g_recZ[k] - z7) > fabsf(off7))
			off7 = g_recZ[k] - z7;
	BackLetGo();
	CHECK(g_recN > 50 && fabsf(off7) < 0.05f && LogLines("by the slope 55 back (a window ray found no ground for over 0.1 s)") > fallbackBefore,
	      "backs %d steps, the feet %+.2f from level at the most, the trace says the slope 55 back", g_recN, off7);
	BackLevel();

	printf("backing: BackFollow=0 rewritten, off and on again: test 40's rule back (the checks above catch it):\n");
	RewriteIni("BackFollow=10", "BackFollow=0");
	GetOffAndOn(60.0f);
	CHECK(LogLines("  reverse: BackFollow=0 BackClose=0.1: going back level or down, each step follows the slope 55 back, and unsupported the gap is closed to 0.5 over the ground, 3 a step at most (test 40's rule) (read again on getting on)") == 1,
	      "the settings line again, BackFollow=0: test 40's rule");
	BackStats o1 = BackBrowDip();
	CHECK(fabsf(o1.worstGap) > 3.0f, "N1 with test 40's rule: the feet %+.2f from the ground at the worst (the slope 55 back ahead of the ground on the brow)", o1.worstGap);
	BackStats o2 = BackInTheAir();
	CHECK(o2.zeroShare > 0.3f && o2.gameShare > 0.5f && o2.dv99 > 10.0f, "N2 with test 40's rule: dz 0 in %.0f%% of the steps, the game's fall %.0f%% of the way down, the vertical speed's change %.1f at the 99th percentile",
	      100.0f * o2.zeroShare, 100.0f * o2.gameShare, o2.dv99);
	float o3 = BackFlip();
	CHECK(o3 < -1.0f, "N3 with test 40's rule: the feet %+.2f after the flip (closed to the hover)", o3);
	float oGap, oDz, o6 = BackLedge(&oGap, &oDz);
	CHECK(o6 < -0.05f, "N6 with test 40's rule: the feet %+.2f under the upper ground after a step at the worst (the slope 55 back going down from 55 before the ledge)", o6);
	CHECK(LogLines("; the slope 55 back (BackFollow=0), own ") > 5, "its rays lines say so");

	printf("backing: BackFollow=10 again:\n");
	RewriteIni("BackFollow=0", "BackFollow=10");
	GetOffAndOn(60.0f);
	CHECK(LogLines("  reverse: BackFollow=10 BackClose=0.1: going back level or down, each step follows the ground's slope over 10 units centred on its middle") == 2 &&
	      LogLines("at most 120 a second and 3 a step (read again on getting on)") == 1, "read again on getting on");
	SetLive(0.0f);
	SetCamera(0.0f);
	SetTilt(0.0f);
	RunFrames(400);
	g_onFrame = NULL;
}

int main(int argc, char **argv)
{
	const char *dllPath = argc > 1 ? argv[1] : "CMB_Slope.dll";
	int mode = argc > 2 ? atoi(argv[2]) : 0;   /* 0 = full test, 1 = probe only, 2 = wrong game version */
	g_haveParts = mode == 0 || mode == 7 || mode == 8 || mode == 9 || mode == 10 || mode == 11 || mode == 13;   /* run.sh gives those a [Parts] section */
	g_base = (uintptr_t)GetModuleHandleA(NULL);
	if ((uintptr_t)g_space > g_base + 0x00300000u || (uintptr_t)g_space + sizeof(g_space) < g_base + RVA_INI_SETTINGS + 8) {
		printf("image layout doesn't cover the game addresses (g_space at +0x%llx)\n", (unsigned long long)((uintptr_t)g_space - g_base));
		return 2;
	}
	(void)g_members;
	BuildGame();
	SetLayouts(mode == 4, mode == 4 || mode == 5);   /* 4: transposed matrices, 5: skin and 3D disagree */
	g_expectRoll = mode == 0 ? 10.0f : 0.0f;          /* run.sh gives the full test MaxRoll=10 */

	if (mode == 9)
		WriteLogMarker(dllPath);   /* the session before's log, for the plugin to keep */
	HMODULE dll = LoadLibraryA(dllPath);
	if (!dll) { printf("can't load %s\n", dllPath); return 2; }
	g_vqHooked = HookImport(dll, "VirtualQuery", (void *)CountingVirtualQuery);   /* its memory queries counted (test 37) */
	const uint32_t *version = (const uint32_t *)GetProcAddress(dll, "F4SEPlugin_Version");
	bool (*load)(const F4SEInterface *) = (bool (*)(const F4SEInterface *))GetProcAddress(dll, "F4SEPlugin_Load");
	printf("version data and load function:\n");
	CHECK(version && load, "exports present");
	CHECK(version && version[0] == 1 && strcmp((const char *)(version + 2), "CMB_Slope") == 0, "F4SEPlugin_Version: data version 1, name CMB_Slope");
	const uint32_t *compatible = version + 2 + 128 + 2;
	CHECK(compatible[0] == 0x010B0F00u && compatible[1] == 0, "compatible with 1.11.240 only");

	if (mode == 0 || mode == 9 || mode == 10 || mode == 11 || mode == 12 || mode == 13)
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
	if (mode == 10) {
		Send(10, 1);   /* GameDataReady */
		RunFrames(300);
		ClimbTests();
		printf("%s\n", g_failures ? "FAILED" : "all ok");
		return g_failures ? 1 : 0;
	}
	if (mode == 11) {
		Send(10, 1);   /* GameDataReady */
		RunFrames(300);
		RamTests();
		printf("%s\n", g_failures ? "FAILED" : "all ok");
		return g_failures ? 1 : 0;
	}
	if (mode == 12) {
		Send(10, 1);   /* GameDataReady */
		RunFrames(300);
		BackingTests();
		printf("%s\n", g_failures ? "FAILED" : "all ok");
		return g_failures ? 1 : 0;
	}
	if (mode == 13) {
		Send(10, 1);   /* GameDataReady */
		RunFrames(300);
		ArmTests();
		printf("%s\n", g_failures ? "FAILED" : "all ok");
		return g_failures ? 1 : 0;
	}
	if (mode == 9) {
		Send(10, 1);   /* GameDataReady */
		RunFrames(300);
		LogRotationTests();
		LoadIntoRideTests();
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
	/* Test 40's finding 8: the climb's boost is on by default, and nothing in this run is a low
	 * face at the capsule (the 40-high obstacle and the 52 deg face 60 tall rise past ClimbTop,
	 * the walls have no top): no limit steeper than the run's own (65, the new controller's) was
	 * ever written. Mode 10 has the climb's own checks. */
	CHECK(g_slopeMin >= cosf(65.0f / DEG) - 1e-5f && LogLines("climb: a low face at the capsule") == 0, "the climb's boost never on in the full run: the steepest limit %.2f deg (the run's own 65), %d \"low face\" lines",
	      acosf(g_slopeMin) * DEG, LogLines("climb: a low face at the capsule"));

	printf("%s\n", g_failures ? "FAILED" : "all ok");
	return g_failures ? 1 : 0;
}
