Scriptname CMB_LookF4SE extends Quest
{OPTIONAL - needs F4SE (and F4SE's script sources to compile). Since the 2026-11-07a build.
Attach to CMB_ControllerQuest next to CMB_ControllerScript.
Puts the chosen look (the badges, the paint, the mirrors) on the parked bike and the first-person
bike through one composed material swap, CMB_LookSwap, and on the worn bike when the game refuses
the look's mods there. Without F4SE the parked and first-person bikes stay stock.}

CMB_ControllerScript Property Controller Auto Const
{CMB_ControllerQuest, for the log.}
ObjectReference Property BikeRef Auto Const
{The parked bike (CMB_BikeRef): it keeps the composed swap (SetMaterialSwap).}
MatSwap Property CMB_LookSwap Auto Const
{0x8D3, empty in the plugin: filled with every slot's chosen entries (SetRemapData).}
FormList Property CMB_LookSwapLists Auto Const
{The five swap lists in slot order (TankL, TankR, Fender, Paint, Mirrors); index = the slot's
choice (TankR's 17, "Same as the left", has none: the left's is used).}
GlobalVariable Property CMB_LookOn Auto Const
{0 or None: every slot's option 0 (the identities), the 2026-11-06a look.}
GlobalVariable Property CMB_Look_TankL Auto Const
GlobalVariable Property CMB_Look_TankR Auto Const
GlobalVariable Property CMB_Look_Fender Auto Const
GlobalVariable Property CMB_Look_Paint Auto Const
GlobalVariable Property CMB_Look_Mirrors Auto Const

; The composed look: every slot's chosen swap's entries in slot order (the right tank's "Same as the
; left", 17, is the left's choice; with CMB_LookOn 0 every slot's option 0, the identities, which put
; a loaded bike back to stock), set into CMB_LookSwap. composedCount its entries, composedActive true
; if any slot is off its option 0.
int composedCount = 0
bool composedActive = false

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
	endif
	return None
EndFunction

int Function Chosen(int aiSlot, FormList akSwaps)
	if !CMB_LookOn || CMB_LookOn.GetValue() <= 0.0
		return 0
	endif
	GlobalVariable g = SlotGlobal(aiSlot)
	if !g
		return 0
	endif
	int i = g.GetValue() as int
	if aiSlot == 1 && i == 17 && CMB_Look_TankL
		i = CMB_Look_TankL.GetValue() as int
	endif
	if i < 0 || i >= akSwaps.GetSize()
		return 0
	endif
	return i
EndFunction

MatSwap:RemapData[] Function Compose()
	composedCount = 0
	composedActive = false
	if !CMB_LookSwap || !CMB_LookSwapLists
		return None
	endif
	MatSwap:RemapData[] all = new MatSwap:RemapData[0]
	int slots = CMB_LookSwapLists.GetSize()
	int s = 0
	while s < slots
		FormList swaps = CMB_LookSwapLists.GetAt(s) as FormList
		if swaps
			int i = Chosen(s, swaps)
			if i != 0
				composedActive = true
			endif
			MatSwap sw = swaps.GetAt(i) as MatSwap
			if sw
				MatSwap:RemapData[] entries = sw.GetRemapData()
				int j = 0
				while entries && j < entries.Length
					all.Add(entries[j])
					j += 1
				endwhile
			endif
		endif
		s += 1
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
	Log("Look: the parked bike's swap holds " + composedCount + " entries, " + applied + " applied now (" + asFrom + ")" + kept)
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
	Log("Look: the first-person bike: " + applied + " of " + composedCount + " entries applied")
	return applied
EndFunction

; The worn bike, when AttachModToInventoryItem was refused: the swap on the player (its sources are
; the bike's own files only, so nothing else the player wears matches).
int Function ApplyWorn()
	Actor player = Game.GetPlayer()
	MatSwap:RemapData[] all = Compose()
	if !all || !player
		return 0
	endif
	return Applied(player.ApplyMaterialSwap(CMB_LookSwap, false))
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
