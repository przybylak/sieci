Scriptname CMB_LookF4SE extends Quest
{OPTIONAL - needs F4SE (and F4SE's script sources to compile). Since the 2026-11-07a build.
Attach to CMB_ControllerQuest next to CMB_ControllerScript.
Puts the chosen look (the badges, the paint, the mirrors; since 2026-11-08a the rims, the tyres and
the plate) on the parked bike and the first-person bike through one composed material swap,
CMB_LookSwap, and on the worn bike when the game refuses the look's mods there or (2026-11-08a) when
the look has colours its mods can't carry (Free colour, a rim's body colour, the plate's colours).
Without F4SE the parked and first-person bikes stay stock.}

CMB_ControllerScript Property Controller Auto Const
{CMB_ControllerQuest, for the log.}
ObjectReference Property BikeRef Auto Const
{The parked bike (CMB_BikeRef): it keeps the composed swap (SetMaterialSwap).}
MatSwap Property CMB_LookSwap Auto Const
{0x8D3, empty in the plugin: filled with every slot's chosen entries (SetRemapData).}
FormList Property CMB_LookSwapLists Auto Const
{The swap lists in slot order (TankL, TankR, Fender, Paint, Mirrors; since 2026-11-08a Rims, Tyres,
Plate, PlateText: nine, the plate's two colour slots have none); index = the slot's choice (TankR's
17, "Same as the left", has none: the left's is used; PlateText's 0, "The plate's own", has none:
its entry k - 1 is option k).}
GlobalVariable Property CMB_LookOn Auto Const
{0 or None: every slot's option 0 (the identities), the 2026-11-06a look.}
GlobalVariable Property CMB_Look_TankL Auto Const
GlobalVariable Property CMB_Look_TankR Auto Const
GlobalVariable Property CMB_Look_Fender Auto Const
GlobalVariable Property CMB_Look_Paint Auto Const
GlobalVariable Property CMB_Look_Mirrors Auto Const

; 2026-11-08a (C2): rims, tyres, the paint's hue, the plates. None (an older ESP) = the 2026-11-07a look.
Group Look_C2
	GlobalVariable Property CMB_Look_Rims Auto Const
	GlobalVariable Property CMB_Look_Tyres Auto Const
	GlobalVariable Property CMB_Look_Plate Auto Const
	GlobalVariable Property CMB_Look_PlateText Auto Const
	GlobalVariable Property CMB_Look_PlateInk Auto Const
	GlobalVariable Property CMB_Look_PlateBack Auto Const
	GlobalVariable Property CMB_LookHue Auto Const
	{0xA18: the Free colour paint's hue, 0-359.}
	GlobalVariable Property CMB_LookShade Auto Const
	{0xA19: 0 deep, 1 normal, 2 light, 3 pastel.}
	GlobalVariable Property CMB_LookPlateCrude Auto Const
	{0xA1A: 0 = a crude text composes as the plate's own.}
	GlobalVariable Property CMB_LookPaintV Auto Const
	{0xA14 (CMB_Slope.dll finds it by ID): the Free colour paint's V, -1 = don't write.}
	GlobalVariable Property CMB_LookRimV Auto Const
	{0xA15: a body-colour rim's V, -1 = don't write.}
	GlobalVariable Property CMB_LookPlateV Auto Const
	{0xA16: the plate's V(design, background), -1 = don't write (stock).}
	GlobalVariable Property CMB_LookPlateTextV Auto Const
	{0xA17: the plate text's V(ink), -1 = don't write.}
	int[] Property PaintRow Auto Const
	{Per Paint option: its paint_p.dds row (Factory 43, the test 29), -1 = the hue (45).}
	int[] Property RimBody Auto Const
	{Per Rims option: 1 = the body colour finish.}
	int[] Property TextCrude Auto Const
	{Per PlateText option: 1 = crude.}
	int[] Property PlateOwnText Auto Const
	{Per Plate option: its own text's PlateText index (1 = None).}
	int[] Property PlateOwnInk Auto Const
	{Per Plate option: its own letters' colour, 0-15.}
	int[] Property PlateOwnBack Auto Const
	{Per Plate option: its own background colour, 0-15 (-1 Stock: no palette).}
	string[] Property RimBodyTargets Auto Const
	{The 8 body-colour rim targets (look_options.json's rim_body_targets).}
	string[] Property RimBodyHueTargets Auto Const
	{Their Free colour twins, in the same order.}
EndGroup

; 2026-11-09a, test 51's fixes. None (an older ESP) = 2026-11-09a as of t54-merge.
Group Fixes_55
	GlobalVariable Property CMB_LookOptions Auto Const
	{0xBF4: CMB_Slope.dll's [Look] switches for the scripts (8 PaletteIndex: PaletteIndexOn); 63 in the plugin.}
	float[] Property RimFinishV Auto Const
	{Per Rims option: its finish's own palette V of rim_p.dds ((row + 0.5) / 8: satin 0.0625, gloss 0.1875, bronze 0.3125,
	gunmetal 0.4375), so Compose can give each palette entry its own V; -1 for the stock cast rim, chrome and body (the
	body colour's V is rimV).}
EndGroup

; The composed look: every slot's chosen swap's entries in slot order (the right tank's "Same as the
; left", 17, is the left's choice; with CMB_LookOn 0 every slot's option 0, the identities, which put
; a loaded bike back to stock), set into CMB_LookSwap. composedCount its entries, composedActive true
; if any slot is off its option 0.
int composedCount = 0
bool composedActive = false

; 2026-11-08a: the slots by number (no constants here: check_plugin asks for every property filled):
; 0 TankL, 1 TankR, 2 Fender, 3 Paint, 4 Mirrors, 5 Rims, 6 Tyres, 7 Plate, 8 PlateText (CMB_LookSwapLists
; holds these nine), 9 PlateInk, 10 PlateBack (no swaps). The plate text's 1 is "None" (off.bgsm); its
; 0, "The plate's own", has no swap, so CMB_LookSwaps_PlateText's entry k - 1 is option k. The plate's
; colours are 16 (plate_p.dds: 16 background rows a design; plate_text_p.dds: 16 inks).

; 2026-11-08a: the look's colour values (V, a palette row's centre: an entry's colorIndex, and the
; fixed globals CMB_Slope.dll copies into the worn bike's materials), set by Colours(); -1 = none. The
; globals are written for the worn bike only (ApplyWorn, ApplyWornColours: the look it is put on with),
; never by the parked or first-person bike's compose, whose look the worn bike may not wear yet.
float paintV = -1.0       ; Free colour: (shade x 256 + round(hue x 255 / 359) + 0.5) / 1024 of paint_hue_p.dds
float rimV = -1.0         ; a body-colour rim: the paint's row of paint_p.dds ((row + 0.5) / 64), or paintV
float plateV = -1.0       ; a plate design: ((design - 1) x 16 + background + 0.5) / 256 of plate_p.dds
float textV = -1.0        ; a plate text: (ink + 0.5) / 16 of plate_text_p.dds
bool rimHue = false       ; a body-colour rim with Free colour: its targets swapped for their hue twins

GlobalVariable Function SlotGlobal(int aiSlot)
	if aiSlot == 0
		return CMB_Look_TankL
	elseif aiSlot == 1
		return CMB_Look_TankR
	elseif aiSlot == 2
		return CMB_Look_Fender
	elseif aiSlot == 3
		return CMB_Look_Paint
	elseif aiSlot == 4
		return CMB_Look_Mirrors
	elseif aiSlot == 5
		return CMB_Look_Rims
	elseif aiSlot == 6
		return CMB_Look_Tyres
	elseif aiSlot == 7
		return CMB_Look_Plate
	elseif aiSlot == 8
		return CMB_Look_PlateText
	elseif aiSlot == 9
		return CMB_Look_PlateInk
	elseif aiSlot == 10
		return CMB_Look_PlateBack
	endif
	return None
EndFunction

bool Function LookOn()
	return CMB_LookOn && CMB_LookOn.GetValue() > 0.0
EndFunction

; 2026-11-09a (test 51): CMB_LookOptions' bit 8, the plugin's [Look] PaletteIndex (the controller's LookOption, here
; for this script); false without the global (an older ESP: 2026-11-09a as of t54-merge).
bool Function PaletteIndexOn()
	if !CMB_LookOptions
		return false
	endif
	int options = CMB_LookOptions.GetValue() as int
	return (options / 8) % 2 == 1
EndFunction

; The slot's global as it stands (0 with CMB_LookOn 0 or no global).
int Function Raw(int aiSlot)
	GlobalVariable g = SlotGlobal(aiSlot)
	if !g || !LookOn()
		return 0
	endif
	return g.GetValue() as int
EndFunction

; The slot's swap list (None for the plate's colour slots, and past an older ESP's five).
FormList Function SwapList(int aiSlot)
	if !CMB_LookSwapLists || aiSlot < 0 || aiSlot >= CMB_LookSwapLists.GetSize()
		return None
	endif
	return CMB_LookSwapLists.GetAt(aiSlot) as FormList
EndFunction

; Option aiChoice's entry in the slot's swap list (-1: none).
int Function SwapIndex(int aiSlot, int aiChoice)
	if aiSlot == 8
		return aiChoice - 1
	endif
	return aiChoice
EndFunction

; aiChoice if the slot has that option, else 0 (its stock look).
int Function InRange(int aiSlot, int aiChoice)
	if aiChoice <= 0
		return 0
	endif
	if aiSlot == 9 || aiSlot == 10
		if aiChoice > 16
			return 0
		endif
		return aiChoice
	endif
	FormList swaps = SwapList(aiSlot)
	if !swaps || SwapIndex(aiSlot, aiChoice) >= swaps.GetSize()
		return 0
	endif
	return aiChoice
EndFunction

; The slot's choice as composed (as the controller's LookChoice with abResolved): 0 with CMB_LookOn 0,
; the right tank's 17 the left's, the plate text as shown (TextShown: with CMB_LookOn 0 the stock plate's
; own, "None", so a loaded bike's text goes back to none).
int Function Chosen(int aiSlot)
	GlobalVariable g = SlotGlobal(aiSlot)
	int i = 0
	if g && LookOn()
		i = g.GetValue() as int
		if aiSlot == 1 && i == 17 && CMB_Look_TankL
			i = CMB_Look_TankL.GetValue() as int
		endif
	endif
	if aiSlot == 8
		return TextShown(i)
	endif
	return InRange(aiSlot, i)
EndFunction

; 2026-11-08a: the plate text shown: "The plate's own" (0) is the plate's own text (PlateOwnText; the
; stock plate's is "None"), and so is a crude one while "Crude plate texts" (CMB_LookPlateCrude) is off.
int Function TextShown(int aiChosen)
	int i = InRange(8, aiChosen)
	if i > 1 && TextCrude && i < TextCrude.Length && TextCrude[i] == 1 && CMB_LookPlateCrude && CMB_LookPlateCrude.GetValue() <= 0.0
		i = 0
	endif
	if i == 0
		int own = 1
		int plate = Chosen(7)
		if PlateOwnText && plate < PlateOwnText.Length
			own = PlateOwnText[plate]
		endif
		i = InRange(8, own)
		if i == 0
			i = 1
		endif
	endif
	return i
EndFunction

; A per-design array's entry (-1 when it isn't there: the material's own colour stays).
int Function PlateOwn(int[] akOwn, int aiPlate)
	if akOwn && aiPlate >= 0 && aiPlate < akOwn.Length
		return akOwn[aiPlate]
	endif
	return -1
EndFunction

int Function PaintRowOf(int aiPaint)
	if PaintRow && aiPaint >= 0 && aiPaint < PaintRow.Length
		return PaintRow[aiPaint]
	endif
	return -2   ; not known: no colour from the paint
EndFunction

int Function Clamp(int aiValue, int aiLow, int aiHigh)
	if aiValue < aiLow
		return aiLow
	elseif aiValue > aiHigh
		return aiHigh
	endif
	return aiValue
EndFunction

; Free colour's V from the MCM's hue (whole, 0-359) and shade (0 deep .. 3 pastel).
float Function HueV()
	float hue = 210.0
	if CMB_LookHue
		hue = CMB_LookHue.GetValue()
	endif
	float shade = 1.0
	if CMB_LookShade
		shade = CMB_LookShade.GetValue()
	endif
	int h = Clamp(Math.Floor(hue + 0.5), 0, 359)
	int sh = Clamp(Math.Floor(shade + 0.5), 0, 3)
	int row = sh * 256 + Math.Floor(h * 255.0 / 359.0 + 0.5)
	return (row + 0.5) / 1024.0
EndFunction

; 2026-11-08a: the four V of the look as chosen (no swap list read beyond the bounds); true if any is
; in use. All -1 with CMB_LookOn 0, every slot at its stock, or an older ESP (CMB_LookPaintV None).
; 2026-11-14a (test 53's "paint -1 rims -1 plate -1 text -1": two threads in this script at once, LookFollowUp's in
; ApplyWornColours' swap while PlaceTwins' second LookFollowUp composed): reckoned in locals, the five members set together at
; the end with no call between them, so no other thread ever reads them half reset (the same values in the same order of
; calls as 2026-11-10a's; no key).
bool Function Colours()
	float paint_v = -1.0
	float rim_v = -1.0
	float plate_v = -1.0
	float text_v = -1.0
	bool hue = false
	if LookOn() && CMB_LookPaintV
		int paint = Chosen(3)
		int row = PaintRowOf(paint)
		if row == -1
			paint_v = HueV()
		endif
		int rims = Chosen(5)
		if RimBody && RimBodyTargets && rims > 0 && rims < RimBody.Length && RimBody[rims] == 1
			if paint_v >= 0.0
				rim_v = paint_v
				hue = RimBodyHueTargets && RimBodyHueTargets.Length == RimBodyTargets.Length
			elseif row >= 0
				rim_v = (row + 0.5) / 64.0
			endif
		endif
		int plate = Chosen(7)
		if plate >= 1
			int back = Chosen(10) - 1
			if back < 0
				back = PlateOwn(PlateOwnBack, plate)
			endif
			if back >= 0 && back < 16
				plate_v = ((plate - 1) * 16 + back + 0.5) / 256.0
			endif
		endif
		if Chosen(8) > 1
			int ink = Chosen(9) - 1
			if ink < 0
				ink = PlateOwn(PlateOwnInk, plate)
			endif
			if ink >= 0 && ink < 16
				text_v = (ink + 0.5) / 16.0
			endif
		endif
	endif
	paintV = paint_v
	rimV = rim_v
	plateV = plate_v
	textV = text_v
	rimHue = hue
	return paint_v >= 0.0 || rim_v >= 0.0 || plate_v >= 0.0 || text_v >= 0.0
EndFunction

; The V's into the fixed globals CMB_Slope.dll reads for the worn bike (-1 = it writes nothing): the
; worn bike's composes only.
Function WriteColours()
	SetV(CMB_LookPaintV, paintV)
	SetV(CMB_LookRimV, rimV)
	SetV(CMB_LookPlateV, plateV)
	SetV(CMB_LookPlateTextV, textV)
EndFunction

Function SetV(GlobalVariable akGlobal, float afValue)
	if akGlobal && akGlobal.GetValue() != afValue
		akGlobal.SetValue(afValue)
	endif
EndFunction

; The slot's V for its entries (-1 none; the rims' only on the body-colour targets).
float Function SlotV(int aiSlot)
	if aiSlot == 3
		return paintV
	elseif aiSlot == 5
		return rimV
	elseif aiSlot == 7
		return plateV
	elseif aiSlot == 8
		return textV
	endif
	return -1.0
EndFunction

; For the log lines: ", colours: paint <V> rims <V> plate <V> text <V>" ("" with an older ESP).
string Function ColoursText()
	if !CMB_LookPaintV
		return ""
	endif
	return ", colours: paint " + VText(paintV) + " rims " + VText(rimV) + " plate " + VText(plateV) + " text " + VText(textV)
EndFunction

string Function VText(float afValue)
	if afValue < 0.0
		return "-1"
	endif
	return "" + afValue
EndFunction

; A coloured entry: a new struct (the MSWP's own data untouched), and its echoes queued: the same
; colour on whatever name the material carries once the engine's own swap (the worn bike's mods)
; put the target on (F4SE matches an entry's source against the material's name).
Function AddColoured(MatSwap:RemapData[] akAll, string[] akSources, MatSwap:RemapData[] akEchoes, string asSource, string asOriginal, string asTarget, float afV)
	MatSwap:RemapData e = new MatSwap:RemapData
	e.source = asSource
	e.target = asTarget
	e.colorIndex = afV
	akAll.Add(e)
	akSources.Add(asSource)
	QueueEcho(akEchoes, asOriginal, asTarget, afV)
	if asTarget != asOriginal
		QueueEcho(akEchoes, asTarget, asTarget, afV)
	endif
EndFunction

Function QueueEcho(MatSwap:RemapData[] akEchoes, string asSource, string asTarget, float afV)
	int k = 0
	while k < akEchoes.Length
		if akEchoes[k].source == asSource
			return   ; both wheels' or both bikes' entries share a target: one echo
		endif
		k += 1
	endwhile
	MatSwap:RemapData e = new MatSwap:RemapData
	e.source = asSource
	e.target = asTarget
	e.colorIndex = afV
	akEchoes.Add(e)
EndFunction

; 2026-11-09a (test 51, [Look] PaletteIndex): the runtime swap (F4SE's ApplyMaterialSwap) writes each entry's colorIndex
; into its material, and the paint's and rim finishes' entries carry none (no CNAM: 0, palette row 0, the grey parked bike
; after an MCM apply). So a palette entry gets its target's own V: Paint (slot 3), an option past Factory with a paint_p.dds
; row, (row + 0.5) / 64; Rims (slot 5) with a finish, RimFinishV ((row + 0.5) / 8 of rim_p.dds). -1: none (the entries
; as the MSWP holds them; Free colour and a body-colour rim keep SlotV's).
float Function OwnV(int aiSlot, int aiChoice)
	if aiSlot == 3 && aiChoice > 0
		int row = PaintRowOf(aiChoice)
		if row >= 0
			return (row + 0.5) / 64.0
		endif
	elseif aiSlot == 5 && RimFinishV && aiChoice >= 0 && aiChoice < RimFinishV.Length
		return RimFinishV[aiChoice]
	endif
	return -1.0
EndFunction

; A palette entry: its target is another file than its source and not the hidden one (a rim option's other styles'
; identities and its hidden cast rim keep no colour: 4 of a finish rim's 32 entries, all 4 of a paint's).
bool Function OwnEntry(MatSwap:RemapData akEntry)
	return akEntry.target != akEntry.source && akEntry.target != "CMB\\Bike\\off.bgsm"
EndFunction

MatSwap:RemapData[] Function Compose(bool abWorn = false)
	composedCount = 0
	composedActive = false
	Colours()
	if abWorn
		WriteColours()   ; 2026-11-08a: the worn bike's look only (a mid-ride Apply's parked compose doesn't)
	endif
	if !CMB_LookSwap || !CMB_LookSwapLists
		return None
	endif
	MatSwap:RemapData[] all = new MatSwap:RemapData[0]
	string[] sources = new string[0]
	MatSwap:RemapData[] echoes = new MatSwap:RemapData[0]
	bool paletteIndex = PaletteIndexOn()   ; 2026-11-09a (test 51): [Look] PaletteIndex, CMB_LookOptions bit 8
	int slots = CMB_LookSwapLists.GetSize()
	int s = 0
	while s < slots
		FormList swaps = CMB_LookSwapLists.GetAt(s) as FormList
		if swaps
			int i = Chosen(s)
			if (s < 5 && i != 0) || (s >= 5 && Raw(s) != 0)
				composedActive = true   ; (the plate text's "The plate's own" is stock even shown as "None")
			endif
			int at = SwapIndex(s, i)
			MatSwap sw = None
			if at >= 0 && at < swaps.GetSize()
				sw = swaps.GetAt(at) as MatSwap
			endif
			if sw
				float v = SlotV(s)
				float own = -1.0
				if v < 0.0 && paletteIndex
					own = OwnV(s, i)
				endif
				MatSwap:RemapData[] entries = sw.GetRemapData()
				int j = 0
				while entries && j < entries.Length
					MatSwap:RemapData e = entries[j]
					; 2026-11-14a ([Look] WornIndex): a body-colour rim's entry WriteWornIndexes pointed at its hue twin (the worn
					; bike's mods' own swap, edited in memory) composed as the ESP has it: its plain target (PlainBodyEntry), so
					; the parked and first-person bikes get 2026-11-10a's entries whatever the last ride's paint was
					if s == 5
						e = PlainBodyEntry(e)
					endif
					int body = -1
					if v >= 0.0 && s == 5
						body = RimBodyTargets.Find(e.target)
					endif
					if own >= 0.0 && OwnEntry(e)
						AddColoured(all, sources, echoes, e.source, e.target, e.target, own)
					elseif v < 0.0 || (s == 5 && body < 0)
						all.Add(e)
						sources.Add(e.source)
					else
						string target = e.target
						if body >= 0 && rimHue
							target = RimBodyHueTargets[body]
						endif
						AddColoured(all, sources, echoes, e.source, e.target, target, v)
					endif
					j += 1
				endwhile
			endif
		endif
		s += 1
	endwhile
	int k = 0
	while k < echoes.Length
		if sources.Find(echoes[k].source) < 0
			all.Add(echoes[k])
			sources.Add(echoes[k].source)
		endif
		k += 1
	endwhile
	CMB_LookSwap.SetRemapData(all)
	composedCount = all.Length
	return all
EndFunction

; 2026-11-14a ([Look] WornIndex): akEntry itself, or, when its target is one of RimBodyHueTargets (WriteWornIndexes renamed
; it), a new struct with the plain twin RimBodyTargets names in the same place and the colour index no ESP entry of a rim has
; (NoIndex); the form's own entry untouched.
MatSwap:RemapData Function PlainBodyEntry(MatSwap:RemapData akEntry)
	if !RimBodyTargets || !RimBodyHueTargets || RimBodyHueTargets.Length != RimBodyTargets.Length
		return akEntry
	endif
	int twin = RimBodyHueTargets.Find(akEntry.target)
	if twin < 0
		return akEntry
	endif
	MatSwap:RemapData e = new MatSwap:RemapData
	e.source = akEntry.source
	e.target = RimBodyTargets[twin]
	e.colorIndex = NoIndex()
	return e
EndFunction

int Function Applied(MatSwap:RemapData[] akDone)
	if akDone
		return akDone.Length
	endif
	return 0
EndFunction

; The parked bike: compose, keep (SetMaterialSwap: the game puts it on whenever the bike's 3D loads;
; the stock look keeps none) and apply now if its 3D is loaded. Returns the entries applied.
int Function ApplyParked(string asFrom = "")
	MatSwap:RemapData[] all = Compose()
	if !all || !BikeRef
		Log("Look: the parked bike: no CMB_LookSwap, swap lists or bike in the plugin (" + asFrom + ")")
		return 0
	endif
	if composedActive
		BikeRef.SetMaterialSwap(CMB_LookSwap)
	else
		BikeRef.SetMaterialSwap(None)
	endif
	int applied = 0
	if BikeRef.Is3DLoaded()
		applied = Applied(BikeRef.ApplyMaterialSwap(CMB_LookSwap, false))
	endif
	string kept = ""
	if !composedActive
		kept = "; the stock look: none kept on the bike"
	endif
	Log("Look: the parked bike's swap holds " + composedCount + " entries, " + applied + " applied now (" + asFrom + ")" + kept + ColoursText())
	return applied
EndFunction

; One reference (the first-person bike): wait for its 3D, then apply the composed swap.
int Function ApplyTo(ObjectReference akRef)
	if !akRef
		return 0
	endif
	MatSwap:RemapData[] all = Compose()
	if !all
		return 0
	endif
	akRef.WaitFor3DLoad()
	int applied = Applied(akRef.ApplyMaterialSwap(CMB_LookSwap, false))
	Log("Look: the first-person bike: " + applied + " of " + composedCount + " entries applied" + ColoursText())
	return applied
EndFunction

; The worn bike, when AttachModToInventoryItem was refused: the swap on the player (its sources are
; the bike's own files only, so nothing else the player wears matches).
int Function ApplyWorn()
	Actor player = Game.GetPlayer()
	MatSwap:RemapData[] all = Compose(true)
	if !all || !player
		return 0
	endif
	return Applied(player.ApplyMaterialSwap(CMB_LookSwap, false))
EndFunction

; 2026-11-08a, the controller's WornLookColours (the worn bike's mods taken, the look has colours they
; can't carry): ApplyWorn's composed swap, whose coloured entries (and their echoes) set the colours.
; -2 when the look composes no colour (nothing applied, the V globals -1).
int Function ApplyWornColours()
	if !Colours()
		WriteColours()
		return -2
	endif
	int applied = ApplyWorn()
	Log("Look: the worn bike's colours: " + applied + " entries applied (F4SE)" + ColoursText())
	return applied
EndFunction

; The controller's "in the field kit" (KitTick): 1 if the player uses akRef as furniture now.
int Function InFurniture(ObjectReference akRef)
	Actor player = Game.GetPlayer()
	if akRef && player && player.GetFurnitureReference() == akRef
		return 1
	endif
	return 0
EndFunction

Function Log(string asMessage)
	if Controller
		Controller.Log(asMessage)
	else
		Debug.Trace("[CMB] " + asMessage)
	endif
EndFunction

; MCM's buttons and the console's calls on the controller quest may land on this script rather than
; CMB_ControllerScript (tests 30, 31, 41), as on the other F4SE scripts: relayed.
Function HotkeyPressed()
	Controller.HotkeyPressed("the MCM hotkey")
EndFunction

Function HeadlampPressed()
	Controller.HeadlampPressed()
EndFunction

Function RefreshHotkey()
	Controller.RefreshHotkey()
EndFunction

Function ForceGiveKeys()
	Controller.ForceGiveKeys()
EndFunction

Function EmergencyReset()
	Controller.EmergencyReset()
EndFunction

Function DecideTeleportsAtOnce(int aiAtOnce)
	Controller.DecideTeleportsAtOnce(aiAtOnce)
EndFunction

Function WatchBusy(int aiOn)
	Controller.WatchBusy(aiOn)
EndFunction

Function LookApplyFromMcm()
	Controller.LookApplyFromMcm()
EndFunction

; 2026-11-09a (test 51, getting on 5-6 s; the controller's FastMount, CMB_LookOptions bit 1), the worn bike's equip: the
; look's colour values (Colours) into the fixed globals CMB_Slope.dll copies into the worn bike's materials (WriteColours):
; about a dozen reads, no compose and no swap. 1 if the look has a colour, else 0 (the globals -1: the last ones cleared).
; With the plugin's bit 64 that is all the worn bike needs; without it the controller's ApplyWornColours follows once,
; after the fade.
int Function WriteWornColours()
	bool any = Colours()
	WriteColours()
	if any
		return 1
	endif
	return 0
EndFunction

; ---- 2026-11-14a (test 53: Free colour drawn blue in third person on every ride but the one the game loaded into) ----------
; What third person drew was the worn paint material file's own lookup scale (0.3960, hue 210), though the plugin's write of
; the look's V into that very material read back for the whole ride; first person and the parked bike were right. The parked
; bike gets its colours from the game: its kept swap (CMB_LookSwap, F4SE-written entries with a colour index) applied by the
; game itself when its 3D loads. [Look] WornIndex (CMB_Slope.ini; CMB_LookOptions 4096) does the same for the worn bike: the
; look's V written, before the equip, as the colour remapping indexes of the chosen options' OWN material swaps, the very forms
; the worn bike's mods add (CMB_LookSwaps_<slot>, MakeOption), so the game builds the worn 3D with the colour. The forms are
; edited in memory only (F4SE's SetRemapData): a restart gives the ESP's back, and with WornIndex turned off after it was on
; this game session (CMB_LookOptions 16384, the plugin's) RestoreWornIndexes puts the chosen ones back before each equip.
; Off (no 4096, no 16384): none of this is called (2026-11-10a).

; The colour remapping index of an ESP entry without one (no CNAM), as F4SE reads it from the game: Paint's Factory swap's
; first entry (option 0, which nothing here edits). Read once and kept (the game's own value; -1 when it can't be read: then
; nothing is put back).
float noIndexValue = 0.0
bool noIndexKnown = false
float Function NoIndex()
	if noIndexKnown
		return noIndexValue
	endif
	FormList swaps = SwapList(3)
	MatSwap sw = None
	if swaps && swaps.GetSize() > 0
		sw = swaps.GetAt(0) as MatSwap
	endif
	MatSwap:RemapData[] entries = None
	if sw
		entries = sw.GetRemapData()
	endif
	if !entries || entries.Length == 0
		return -1.0
	endif
	noIndexValue = entries[0].colorIndex
	noIndexKnown = true
	return noIndexValue
EndFunction

; The slot's chosen option's own swap (as Compose takes it), or None.
MatSwap Function ChosenSwap(int aiSlot)
	FormList swaps = SwapList(aiSlot)
	if !swaps
		return None
	endif
	int at = SwapIndex(aiSlot, Chosen(aiSlot))
	if at < 0 || at >= swaps.GetSize()
		return None
	endif
	return swaps.GetAt(at) as MatSwap
EndFunction

; A body-colour rim's target's place in RimBodyTargets, or in RimBodyHueTargets when IndexSlot renamed it (-1: neither).
int Function BodyAt(string asTarget)
	if !RimBodyTargets
		return -1
	endif
	int at = RimBodyTargets.Find(asTarget)
	if at < 0 && RimBodyHueTargets && RimBodyHueTargets.Length == RimBodyTargets.Length
		at = RimBodyHueTargets.Find(asTarget)
	endif
	return at
EndFunction

; The slot's chosen swap with afV as its entries' colour index (abRestore: NoIndex, the ESP's), as Compose colours the
; parked bike's: every entry for the paint (3), the plate (7) and its text (8); for the rims (5) the body-colour entries
; only, pointed at their hue twins with abHue (Free colour), else at the plain targets. Nothing with afV under 0 (the slot
; carries no colour: its option is never edited). Read first, SetRemapData only on a difference (F4SE's Set clears and
; re-adds every entry: the others make the round trip with their own index). " <slot> <n> set" / " ... as they were".
string Function IndexSlot(int aiSlot, float afV, bool abHue, bool abRestore)
	if afV < 0.0
		return ""
	endif
	MatSwap sw = ChosenSwap(aiSlot)
	if !sw
		return ""
	endif
	float index = afV
	if abRestore
		index = NoIndex()
		if !noIndexKnown
			return " " + SlotName(aiSlot) + " not put back (no Factory swap to read the ESP's index from)"
		endif
	endif
	MatSwap:RemapData[] entries = sw.GetRemapData()
	int carried = 0
	int changed = 0
	int j = 0
	while entries && j < entries.Length
		MatSwap:RemapData e = entries[j]
		bool carries = aiSlot != 5
		string target = e.target
		if aiSlot == 5
			int body = BodyAt(e.target)
			if body >= 0
				carries = true
				target = RimBodyTargets[body]
				if abHue && !abRestore
					target = RimBodyHueTargets[body]
				endif
			endif
		endif
		if carries
			carried += 1
			if e.colorIndex != index || e.target != target
				e.colorIndex = index
				e.target = target
				changed += 1
			endif
		endif
		j += 1
	endwhile
	if changed > 0
		sw.SetRemapData(entries)
		indexChanges += changed
		return " " + SlotName(aiSlot) + " " + changed + " of " + carried + " set"
	endif
	return " " + SlotName(aiSlot) + " " + carried + " as they were"
EndFunction

string Function SlotName(int aiSlot)
	if aiSlot == 3
		return "Paint"
	elseif aiSlot == 5
		return "Rims"
	elseif aiSlot == 7
		return "Plate"
	elseif aiSlot == 8
		return "Plate text"
	endif
	return "slot " + aiSlot
EndFunction

; The four slots indexed (abRestore: put back) with the values Colours() just reckoned, as one text ("" nothing looked at);
; indexChanges the entries changed (for the log only). The values are taken into locals first, before any call (another
; thread's Colours may set the members again: the same values).
int indexChanges = 0
string Function IndexAll(bool abRestore)
	float paint_v = paintV
	float rim_v = rimV
	float plate_v = plateV
	float text_v = textV
	bool hue = rimHue
	indexChanges = 0
	string text = IndexSlot(3, paint_v, false, abRestore) + IndexSlot(5, rim_v, hue, abRestore)
	text += IndexSlot(7, plate_v, false, abRestore) + IndexSlot(8, text_v, false, abRestore)
	if text != ""
		text += ", colours: paint " + VText(paint_v) + " rims " + VText(rim_v) + " plate " + VText(plate_v) + " text " + VText(text_v)
	endif
	return text
EndFunction

; The controller's WornColoursWrite with [Look] WornIndex (bit 4096), before the worn bike's equip: WriteWornColours (the
; values into the plugin's globals: its writer still colours a worn 3D the game built before the indexes were in, as after a
; load) and the same values into the chosen options' swaps. 1 if the look has a colour, else 0.
int Function WriteWornIndexes()
	bool any = Colours()
	string text = IndexAll(false)
	WriteColours()
	if text != ""
		Log("Look: the worn bike's colour indexes before its equip (WornIndex):" + text)
	endif
	if any
		return 1
	endif
	return 0
EndFunction

; The controller's WornIndexRestore (WornIndex off after it was on: CMB_LookOptions 16384 without 4096), before the equip: the
; chosen options' swaps as the ESP has them; a line only when one was changed. The entries changed (0 none).
int Function RestoreWornIndexes()
	Colours()
	string text = IndexAll(true)
	int changed = indexChanges
	if changed > 0
		Log("Look: the worn bike's colour indexes put back as the ESP has them (WornIndex off):" + text)
	endif
	return changed
EndFunction

; The controller's LookAfterLoad: the options' swaps follow the loaded save's look (a 3D the game builds from them now is
; that look's): indexed with WornIndex (no globals written: the save's are the worn bike's), put back with only 16384. -2
; neither bit (nothing called), else the entries changed.
int Function LoadWornIndexes()
	int options = 0
	if CMB_LookOptions
		options = CMB_LookOptions.GetValue() as int
	endif
	bool index = (options / 4096) % 2 == 1
	if !index && (options / 16384) % 2 == 0
		return -2
	endif
	Colours()
	string text = IndexAll(!index)
	int changed = indexChanges
	if changed > 0
		if index
			Log("Look: the worn bike's colour indexes after the load (WornIndex):" + text)
		else
			Log("Look: the worn bike's colour indexes put back as the ESP has them after the load (WornIndex off):" + text)
		endif
	endif
	return changed
EndFunction

; 2026-11-09a (test 51's black screen; the controller's MountGuard watchdog, bit 16): the menus open now among those that
; can hold getting on up, comma-separated ("" none of them).
string Function MenusOpenText()
	string[] names = new string[7]
	names[0] = "MessageBoxMenu"
	names[1] = "PauseMenu"
	names[2] = "PipboyMenu"
	names[3] = "LoadingMenu"
	names[4] = "ExamineMenu"
	names[5] = "Console"
	names[6] = "FaderMenu"
	string text = ""
	int i = 0
	while i < names.Length
		if UI.IsMenuOpen(names[i])
			if text != ""
				text += ", "
			endif
			text += names[i]
		endif
		i += 1
	endwhile
	return text
EndFunction

; 2026-11-09a (test 51, FastMount), after the fade (the controller's LookFollowUp): how many mods the item in the worn
; bike's slot carries (F4SE GetWornItemMods on the slot CMB_GearRestoreF4SE's BikeSlotIndex names, as its RememberSlot and
; LogWornSlots read it). -1 without CMB_GearRestoreF4SE or the player, -2 nothing in the slot (not on yet).
int Function WornModCount()
	Actor player = Game.GetPlayer()
	ScriptObject gear = CastAs("CMB_GearRestoreF4SE")
	if !player || !gear
		return -1
	endif
	int slot = gear.GetPropertyValue("BikeSlotIndex") as int
	Actor:WornItem worn = player.GetWornItem(slot)
	if !worn || !worn.item
		return -2
	endif
	ObjectMod[] mods = player.GetWornItemMods(slot)
	if !mods
		return 0
	endif
	return mods.Length
EndFunction
