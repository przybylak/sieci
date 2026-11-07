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
bool Function Colours()
	paintV = -1.0
	rimV = -1.0
	plateV = -1.0
	textV = -1.0
	rimHue = false
	if !LookOn() || !CMB_LookPaintV
		return false
	endif
	int paint = Chosen(3)
	int row = PaintRowOf(paint)
	if row == -1
		paintV = HueV()
	endif
	int rims = Chosen(5)
	if RimBody && RimBodyTargets && rims > 0 && rims < RimBody.Length && RimBody[rims] == 1
		if paintV >= 0.0
			rimV = paintV
			rimHue = RimBodyHueTargets && RimBodyHueTargets.Length == RimBodyTargets.Length
		elseif row >= 0
			rimV = (row + 0.5) / 64.0
		endif
	endif
	int plate = Chosen(7)
	if plate >= 1
		int back = Chosen(10) - 1
		if back < 0
			back = PlateOwn(PlateOwnBack, plate)
		endif
		if back >= 0 && back < 16
			plateV = ((plate - 1) * 16 + back + 0.5) / 256.0
		endif
	endif
	if Chosen(8) > 1
		int ink = Chosen(9) - 1
		if ink < 0
			ink = PlateOwn(PlateOwnInk, plate)
		endif
		if ink >= 0 && ink < 16
			textV = (ink + 0.5) / 16.0
		endif
	endif
	return paintV >= 0.0 || rimV >= 0.0 || plateV >= 0.0 || textV >= 0.0
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
				MatSwap:RemapData[] entries = sw.GetRemapData()
				int j = 0
				while entries && j < entries.Length
					MatSwap:RemapData e = entries[j]
					int body = -1
					if v >= 0.0 && s == 5
						body = RimBodyTargets.Find(e.target)
					endif
					if v < 0.0 || (s == 5 && body < 0)
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
