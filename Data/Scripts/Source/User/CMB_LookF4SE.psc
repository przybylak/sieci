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

; 2026-11-16a (C3, build A): the seat's colour (slot 11) and the 3D helmets' right-side follow. None (an older ESP) = 11 slots,
; the right tank's "Same as the left" the left's own index (2026-11-15b).
Group Look_C3
	GlobalVariable Property CMB_Look_Seat Auto Const
	{0xC08: the seat, an index into CMB_LookOptions_Seat (0 = as it came, the dark brown leather; 1-14 the colours).}
	int[] Property TankRightOf Auto Const
	{Per TankL option: the TankR option with the same key (0-16 the same index; the 3D helmets and the skull, TankL 17-19, are
	TankR 18-20, after "Same as the left"). "Same as the left" resolves through it.}
	float[] Property SeatV Auto Const
	{Per Seat option: its row's V of seat_p.dds ((row + 0.5) / 16, the CNAM its two entries carry); -1 for option 0 (the
	stock seat: its own files, no palette, nothing written).}
EndGroup

; 2026-11-21a (C4, art build B): the wear (slot 12), the front fender badge (13) and the headlamp's lens (14). None (an older
; ESP) = 12 slots (2026-11-17a). Plain swaps, no colour index: Compose takes their entries as the ESP has them.
Group Look_C4
	GlobalVariable Property CMB_Look_Wear Auto Const
	{0xC50: the wear (0 = as it came: the overlay shells on their invisible own files).}
	GlobalVariable Property CMB_Look_FrontFender Auto Const
	{0xC51: the front fender's badge (0 = none).}
	GlobalVariable Property CMB_Look_Headlamp Auto Const
	{0xC52: the headlamp's colour (0 = warm: front_glow's own files); the beam is the controller's.}
EndGroup

; The composed look: every slot's chosen swap's entries in slot order (the right tank's "Same as the
; left", 17, is the left's choice; with CMB_LookOn 0 every slot's option 0, the identities, which put
; a loaded bike back to stock), set into CMB_LookSwap. composedCount its entries, composedActive true
; if any slot is off its option 0. 2026-11-16a: the seat's entries with its V (SeatV, as a coloured entry and its echo: the worn
; bike's own mods may have put the target on already).
int composedCount = 0
bool composedActive = false

; 2026-11-08a: the slots by number (no constants here: check_plugin asks for every property filled):
; 0 TankL, 1 TankR, 2 Fender, 3 Paint, 4 Mirrors, 5 Rims, 6 Tyres, 7 Plate, 8 PlateText (CMB_LookSwapLists
; holds these nine), 9 PlateInk, 10 PlateBack (no swaps). The plate text's 1 is "None" (off.bgsm); its
; 0, "The plate's own", has no swap, so CMB_LookSwaps_PlateText's entry k - 1 is option k. The plate's
; colours are 16 (plate_p.dds: 16 background rows a design; plate_text_p.dds: 16 inks).
; 2026-11-16a (C3): 11 Seat. CMB_LookSwapLists holds twelve, index = slot: 9 and 10 are empty placeholders (the plate's colour
; slots still have no swaps), 11 the Seat's (index = option). The right tank's swap list skips "Same as the left" (17), so
; its options 18-20 (the 3D helmets, the skull) are its entries 17-19. An older ESP: nine lists, no seat.
; 2026-11-21a (C4): 12 Wear, 13 FrontFender, 14 Headlamp (CMB_LookSwapLists 15, index = slot; each index = option, plain
; entries). The tank options 21-22 of the right (Nuka-Cola, Red Rocket) are its entries 20-21, the left's 20-21 its own.

; 2026-11-08a: the look's colour values (V, a palette row's centre: an entry's colorIndex, and the
; fixed globals CMB_Slope.dll copies into the worn bike's materials), set by Colours(); -1 = none. The
; globals are written for the worn bike only (ApplyWorn, ApplyWornColours: the look it is put on with),
; never by the parked or first-person bike's compose, whose look the worn bike may not wear yet.
float paintV = -1.0       ; Free colour: (shade x 256 + round(hue x 255 / 359) + 0.5) / 1024 of paint_hue_p.dds
float rimV = -1.0         ; a body-colour rim: the paint's row of paint_p.dds ((row + 0.5) / 64), or paintV
float plateV = -1.0       ; a plate design: ((design - 1) x 16 + background + 0.5) / 256 of plate_p.dds
float textV = -1.0        ; a plate text: (ink + 0.5) / 16 of plate_text_p.dds
bool rimHue = false       ; a body-colour rim with Free colour: its targets swapped for their hue twins
; 2026-11-15a ([Look] MountQuick): the options Colours() read them for (Paint, Rims, Plate, the plate text as shown; -1 with
; CMB_LookOn 0 or an older ESP), set with the V's: the key of a WornIndex pass (IndexKey).
int chosenPaint = -1
int chosenRims = -1
int chosenPlate = -1
int chosenText = -1
; 2026-11-16a (C3): the seat's option and its V (SeatV; -1 the stock seat, Customise off or an older ESP), set by Colours() with
; the others. Not one of the "colours" Colours() returns: the seat's mods carry their V (CNAM), so the worn bike's equip needs
; no F4SE swap for it; Compose and WornIndex write it so no path leaves the seat at colour index 0.
int chosenSeat = -1
float seatValue = -1.0

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
	elseif aiSlot == 11
		return CMB_Look_Seat   ; 2026-11-16a: None with an older ESP (its slot then composes nothing)
	elseif aiSlot == 12
		return CMB_Look_Wear   ; 2026-11-21a: these three None with an older ESP (past CMB_LookSwapLists' 12 there anyway)
	elseif aiSlot == 13
		return CMB_Look_FrontFender
	elseif aiSlot == 14
		return CMB_Look_Headlamp
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

; 2026-11-15a (test 54): CMB_LookOptions' bit 32768, the plugin's [Look] KitDefer, and 65536, its MountQuick; false without the
; global or the plugin (2026-11-14a).
bool Function LookOptionOn(int aiBit)
	if !CMB_LookOptions
		return false
	endif
	return ((CMB_LookOptions.GetValue() as int) / aiBit) % 2 == 1
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

; Option aiChoice's entry in the slot's swap list (-1: none). 2026-11-16a: the right tank's list skips "Same as the left" (17,
; no swap), so its options past it are one entry earlier (18-20 at 17-19; an older ESP has none past 17).
int Function SwapIndex(int aiSlot, int aiChoice)
	if aiSlot == 8
		return aiChoice - 1
	elseif aiSlot == 1 && aiChoice >= 17
		if aiChoice == 17
			return -1
		endif
		return aiChoice - 1
	endif
	return aiChoice
EndFunction

; aiChoice if the slot has that option, else 0 (its stock look). 2026-11-16a: an option with no entry in its list (SwapIndex
; -1: an unresolved "Same as the left") is the stock look too, as it was while TankR's list ended at 16.
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
	int at = SwapIndex(aiSlot, aiChoice)
	if !swaps || at < 0 || at >= swaps.GetSize()
		return 0
	endif
	return aiChoice
EndFunction

; 2026-11-16a (C3): "Same as the left" for the left's option aiLeft: the right's option with the same key (TankRightOf); with an
; older ESP (TankRightOf None) or past its end the left's own index (the old rule: both lists agree on 0-16).
int Function RightOf(int aiLeft)
	if TankRightOf && aiLeft >= 0 && aiLeft < TankRightOf.Length
		return TankRightOf[aiLeft]
	endif
	return aiLeft
EndFunction

; The slot's choice as composed (as the controller's LookChoice with abResolved): 0 with CMB_LookOn 0,
; the right tank's 17 the left's (2026-11-16a: through RightOf), the plate text as shown (TextShown: with CMB_LookOn 0 the stock
; plate's own, "None", so a loaded bike's text goes back to none).
int Function Chosen(int aiSlot)
	GlobalVariable g = SlotGlobal(aiSlot)
	int i = 0
	if g && LookOn()
		i = g.GetValue() as int
		if aiSlot == 1 && i == 17 && CMB_Look_TankL
			i = RightOf(InRange(0, CMB_Look_TankL.GetValue() as int))
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
	int paint = -1   ; 2026-11-15a: kept with the V's (chosenPaint .. chosenText; the same calls in the same order)
	int rims = -1
	int plate = -1
	int text = -1
	int seat = -1    ; 2026-11-16a: the seat's option and V (SeatValueOf), after the four (no call between the members' sets)
	float seat_v = -1.0
	if LookOn() && CMB_LookPaintV
		paint = Chosen(3)
		int row = PaintRowOf(paint)
		if row == -1
			paint_v = HueV()
		endif
		rims = Chosen(5)
		if RimBody && RimBodyTargets && rims > 0 && rims < RimBody.Length && RimBody[rims] == 1
			if paint_v >= 0.0
				rim_v = paint_v
				hue = RimBodyHueTargets && RimBodyHueTargets.Length == RimBodyTargets.Length
			elseif row >= 0
				rim_v = (row + 0.5) / 64.0
			endif
		endif
		plate = Chosen(7)
		if plate >= 1
			int back = Chosen(10) - 1
			if back < 0
				back = PlateOwn(PlateOwnBack, plate)
			endif
			if back >= 0 && back < 16
				plate_v = ((plate - 1) * 16 + back + 0.5) / 256.0
			endif
		endif
		text = Chosen(8)
		if text > 1
			int ink = Chosen(9) - 1
			if ink < 0
				ink = PlateOwn(PlateOwnInk, plate)
			endif
			if ink >= 0 && ink < 16
				text_v = (ink + 0.5) / 16.0
			endif
		endif
	endif
	if LookOn() && SeatV
		seat = Chosen(11)
		seat_v = SeatValueOf(seat)
	endif
	paintV = paint_v
	rimV = rim_v
	plateV = plate_v
	textV = text_v
	rimHue = hue
	chosenPaint = paint
	chosenRims = rims
	chosenPlate = plate
	chosenText = text
	chosenSeat = seat
	seatValue = seat_v
	return paint_v >= 0.0 || rim_v >= 0.0 || plate_v >= 0.0 || text_v >= 0.0
EndFunction

; 2026-11-16a (C3): a Seat option's V (SeatV: its seat_p.dds row's, the CNAM of its two entries), -1 for the stock seat (option
; 0), past SeatV's end or without it (an older ESP).
float Function SeatValueOf(int aiSeat)
	if SeatV && aiSeat >= 0 && aiSeat < SeatV.Length
		return SeatV[aiSeat]
	endif
	return -1.0
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

; The slot's V for its entries (-1 none; the rims' only on the body-colour targets; 2026-11-16a: the seat's on its entries
; that swap to another file, i.e. both of options 1-14's).
float Function SlotV(int aiSlot)
	if aiSlot == 3
		return paintV
	elseif aiSlot == 5
		return rimV
	elseif aiSlot == 7
		return plateV
	elseif aiSlot == 8
		return textV
	elseif aiSlot == 11
		return seatValue
	endif
	return -1.0
EndFunction

; For the log lines: ", colours: paint <V> rims <V> plate <V> text <V>" ("" with an older ESP); 2026-11-16a: " seat <V>" after
; them with the C3 ESP (SeatV there).
string Function ColoursText()
	if !CMB_LookPaintV
		return ""
	endif
	return ", colours: paint " + VText(paintV) + " rims " + VText(rimV) + " plate " + VText(plateV) + " text " + VText(textV) + SeatText(seatValue)
EndFunction

string Function SeatText(float afValue)
	if !SeatV
		return ""
	endif
	return " seat " + VText(afValue)
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
		if swaps && swaps.GetSize() > 0   ; 2026-11-16a: the plate colours' empty placeholders (9, 10) compose nothing, as before
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
					elseif v < 0.0 || (s == 5 && body < 0) || (s == 11 && !OwnEntry(e))
						all.Add(e)   ; (2026-11-16a: a seat entry onto its own file keeps the ESP's)
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
	bool menuShut = true
	if KitDeferOn()
		menuShut = ExamineClosed(asFrom)   ; 2026-11-15a ([Look] KitDefer): never into the parked bike's live 3D under the workbench menu
	endif
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
	if BikeRef.Is3DLoaded() && menuShut
		applied = Applied(BikeRef.ApplyMaterialSwap(CMB_LookSwap, false))
	elseif !menuShut
		; review (2026-11-15a): the workbench menu still listed after ExamineClosed's 100 waits: the swap kept for the bike's
		; next 3D load (SetMaterialSwap above), never put on its live 3D under the menu
		Log("Look: the parked bike's swap kept for its next load, not put on now: the workbench menu is still open (" + asFrom + ", KitDefer)")
	endif
	string kept = ""
	if !composedActive
		kept = "; the stock look: none kept on the bike"
	endif
	Log("Look: the parked bike's swap holds " + composedCount + " entries, " + applied + " applied now (" + asFrom + ")" + kept + ColoursText())
	return applied
EndFunction

; 2026-11-15a ([Look] KitDefer, CMB_LookOptions 32768; test 54: both crashes, a null read in d3d11 from the world's deferred
; pre-pass, came in the frame the field kit's "Plate background" put this swap on the parked bike's live 3D under the armour
; bench's menu; the MCM's Apply and the kit's own end, outside that menu, never crashed): while the workbench menu
; (ExamineMenu) is open, the compose and the swap wait for its close. The controller's LookModded no longer calls ApplyParked
; there (the session's end puts the look on), so this only holds a caller that comes in while the menu is still closing (the
; kit left before the menu's close event). Utility.Wait doesn't return in menu mode: the first one comes back after the
; close; at most 100 (10 s outside menu mode) in case the menu stays listed. Nothing when the menu isn't open.
bool Function ExamineClosed(string asFrom)
	if !UI.IsMenuOpen("ExamineMenu")
		return true
	endif
	float at = Utility.GetCurrentRealTime()
	Log("Look: the parked bike's swap waits for the workbench menu to close (" + asFrom + ", KitDefer)")
	int n = 0
	while n < 100 && UI.IsMenuOpen("ExamineMenu")
		Utility.Wait(0.1)
		n += 1
	endwhile
	if UI.IsMenuOpen("ExamineMenu")
		return false   ; review (2026-11-15a): still open after 100 waits: ApplyParked keeps the swap for the next load only
	endif
	Log("Look: the workbench menu closed " + (Utility.GetCurrentRealTime() - at) + " s later: the parked bike's swap now (" + asFrom + ", KitDefer)")
	return true
EndFunction

; Review (2026-11-15a): KitDefer by the plugin's bit (CMB_LookOptions 32768), and always without the plugin
; (F4SE.GetPluginVersion("CMB_Slope") -1: a game or save without CMB_Slope keeps the ESP's 4031): the parked bike's swap
; never goes onto its live 3D under the workbench menu there either.
bool Function KitDeferOn()
	return LookOptionOn(32768) || F4SE.GetPluginVersion("CMB_Slope") < 0
EndFunction

; KitDeferOn for the controller (LookF4SEText): "1" or "0".
string Function KitDeferText()
	if KitDeferOn()
		return "1"
	endif
	return "0"
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
; 2026-11-16a (C3): the seat (11), its entries onto another file (OwnEntry), with SeatV's V both ways: the ESP's own entries
; carry that V (CNAM), so putting them back is the same V, never NoIndex. Never the MountQuick probe (a restart keeps its V:
; it can't tell that the others' indexes are gone).
string Function IndexSlot(int aiSlot, float afV, bool abHue, bool abRestore)
	if afV < 0.0
		return ""
	endif
	MatSwap sw = ChosenSwap(aiSlot)
	if !sw
		return ""
	endif
	float index = afV
	if abRestore && aiSlot != 11
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
		bool carries = aiSlot != 5 && (aiSlot != 11 || OwnEntry(e))
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
	endif
	if !indexProbe && aiSlot != 5 && aiSlot != 11 && !abRestore && carried > 0
		indexProbe = sw   ; 2026-11-15a ([Look] MountQuick): every entry of a paint, plate or text option carries the index
		indexProbeV = index
	endif
	if changed > 0
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
	elseif aiSlot == 11
		return "Seat"
	endif
	return "slot " + aiSlot
EndFunction

; The four slots indexed (abRestore: put back) with the values Colours() just reckoned, as one text ("" nothing looked at);
; indexChanges the entries changed (for the log only). The values are taken into locals first, before any call (another
; thread's Colours may set the members again: the same values). 2026-11-16a: and the seat, after them (SeatV's V; nothing with
; the stock seat or an older ESP).
int indexChanges = 0
string Function IndexAll(bool abRestore)
	float paint_v = paintV
	float rim_v = rimV
	float plate_v = plateV
	float text_v = textV
	float seat_v = seatValue
	bool hue = rimHue
	indexChanges = 0
	indexProbe = None   ; 2026-11-15a: the pass's first indexed paint, plate or text swap (MountQuick's check)
	indexProbeV = -1.0
	string text = IndexSlot(3, paint_v, false, abRestore) + IndexSlot(5, rim_v, hue, abRestore)
	text += IndexSlot(7, plate_v, false, abRestore) + IndexSlot(8, text_v, false, abRestore)
	text += IndexSlot(11, seat_v, false, abRestore)
	if text != ""
		text += ", colours: paint " + VText(paint_v) + " rims " + VText(rim_v) + " plate " + VText(plate_v) + " text " + VText(text_v) + SeatText(seat_v)
	endif
	return text
EndFunction

; ---- 2026-11-15a ([Look] MountQuick, CMB_LookOptions 65536; test 54: getting on 0.85 s slower than 10a, the fade to the
; equip 2.30 s median against 1.35 s; this pass's 40-odd reads and GetRemapData calls at every getting on with nothing changed,
; "Paint 4 as they were plate 2 as they were Plate text 2 as they were"): a pass that leaves the chosen options' swaps holding
; the look's indexes is remembered (IndexKey: the options and the V's, as Colours() read them; indexProbe: one of the swaps it
; indexed, with its index). The next WriteWornIndexes with the same key reads that one swap (one GetRemapData): its index still
; there, the pass is skipped (the other swaps are untouched since: only a pass edits them, and every pass, put-back and load
; forgets the key first); else (a restart gave the ESP's back) the pass as before. A look whose only colour is a body-colour
; rim's has no probe: the pass as before. Off (no 65536): the pass at every call (2026-11-14a; the key is forgotten, never used).
string wornIndexKey = ""         ; the key of the last pass whose swaps still hold its indexes ("" none known)
MatSwap wornIndexProbe = None    ; one of its swaps (a paint, plate or text option's: every entry carries the index)
float wornIndexProbeV = -1.0     ; ...and that index
int wornIndexPasses = 0          ; passes begun (a pass ending after another began remembers nothing)
MatSwap indexProbe = None        ; IndexAll's first indexed paint, plate or text swap, and its index
float indexProbeV = -1.0

string Function IndexKey()
	return "paint " + chosenPaint + " " + paintV + ", rims " + chosenRims + " " + rimV + " " + rimHue + ", plate " + chosenPlate + " " + plateV + ", text " + chosenText + " " + textV + ", seat " + chosenSeat + " " + seatValue
EndFunction

; 1: asKey is the remembered pass's and its probe still holds its index (the pass not needed); 0 no pass remembered or another
; look; -1 remembered, but the probe's index isn't there (the key forgotten).
int Function IndexesKept(string asKey)
	if wornIndexKey == "" || asKey != wornIndexKey || !wornIndexProbe
		return 0
	endif
	MatSwap:RemapData[] entries = wornIndexProbe.GetRemapData()
	if entries && entries.Length > 0 && entries[0].colorIndex == wornIndexProbeV
		return 1
	endif
	wornIndexKey = ""
	return -1
EndFunction

; After a pass begun as number aiPass with the key asKey: remembered when no other pass began meanwhile and it indexed a probe.
Function IndexesRemember(int aiPass, string asKey)
	if aiPass == wornIndexPasses && indexProbe
		wornIndexKey = asKey
		wornIndexProbe = indexProbe
		wornIndexProbeV = indexProbeV
	else
		wornIndexKey = ""
	endif
EndFunction

; The controller's LookAfterLoad with MountQuick when LoadWornIndexes isn't called: the swaps in memory may be another save's
; look's (or, after a restart, the ESP's): nothing remembered. Returns 0.
int Function ForgetWornIndexes()
	wornIndexPasses += 1
	wornIndexKey = ""
	return 0
EndFunction

; The controller's WornColoursWrite with [Look] WornIndex (bit 4096), before the worn bike's equip: WriteWornColours (the
; values into the plugin's globals: its writer still colours a worn 3D the game built before the indexes were in, as after a
; load) and the same values into the chosen options' swaps. 1 if the look has a colour, else 0. 2026-11-15a (MountQuick): the
; values only when the swaps hold them already (IndexesKept).
int Function WriteWornIndexes()
	bool any = Colours()
	bool quick = LookOptionOn(65536)
	string key = ""
	if quick
		key = IndexKey()
		int kept = IndexesKept(key)
		if kept == 1
			WriteColours()
			Log("Look: the worn bike's colour indexes before its equip (WornIndex): in its options' swaps since the last pass, the look unchanged (MountQuick)" + ColoursText())
			if any
				return 1
			endif
			return 0
		elseif kept == -1
			Log("Look: the worn bike's colour indexes: the last pass's are gone from its options' swaps (a restart?): written again (MountQuick)")
		endif
	endif
	wornIndexPasses += 1
	int pass = wornIndexPasses
	wornIndexKey = ""
	string text = IndexAll(false)
	if quick
		IndexesRemember(pass, key)
	endif
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
	wornIndexPasses += 1   ; 2026-11-15a: the swaps put back: no pass remembered (MountQuick)
	wornIndexKey = ""
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
	wornIndexPasses += 1   ; 2026-11-15a: a load: what was remembered is another session's or another save's (MountQuick)
	int pass = wornIndexPasses
	wornIndexKey = ""
	if !index && (options / 16384) % 2 == 0
		return -2
	endif
	Colours()
	string key = ""
	if index && (options / 65536) % 2 == 1
		key = IndexKey()
	endif
	string text = IndexAll(!index)
	if key != ""
		IndexesRemember(pass, key)
	endif
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
