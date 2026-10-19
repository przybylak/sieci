Scriptname CMB_GearRestoreF4SE extends Quest
{OPTIONAL - needs F4SE (and F4SE's script sources to compile).
Attach to CMB_ControllerQuest next to CMB_ControllerScript.
Whatever you wear in the bike's biped slot comes off when you get on; this
remembers it and puts it back on when you get off. Without F4SE that gear
just stays in your inventory.}

CMB_ControllerScript Property Controller Auto Const
{CMB_ControllerQuest, for MCM's calls that land here (test 31).}
Armor Property CMB_BikeRiderArmor Auto Const Mandatory
Armor Property CMB_BikeRiderArmorFrame Auto Const
{The ground-planted version of the worn bike.}
int Property BikeSlotIndex Auto Const Mandatory
{The bike's biped slot minus 30 (slot 57 = 27). Filled by the plugin generator from BikeSlot.}

Form rememberedItem = None

Function RememberSlot(Actor akActor)
	rememberedItem = None
	Actor:WornItem worn = akActor.GetWornItem(BikeSlotIndex)
	if worn && worn.item && worn.item != CMB_BikeRiderArmor && worn.item != CMB_BikeRiderArmorFrame
		rememberedItem = worn.item
	endif
EndFunction

Function RestoreSlot(Actor akActor)
	Form item = rememberedItem
	rememberedItem = None
	if item && akActor.GetItemCount(item) > 0 && !akActor.IsEquipped(item)
		akActor.EquipItem(item, false, true)
	endif
EndFunction

; What the biped holds in the bike's slot once the bike is on (test 33: a reading of the worn
; slots told an addon the game never took from a timing gap; the lamp piece and its own slot
; went after test 35, the bike's slot is still logged).
Function LogWornSlots(Actor akActor)
	LogSlot(akActor, BikeSlotIndex)
EndFunction

Function LogSlot(Actor akActor, int aiSlotIndex)
	if !Controller
		return
	endif
	Actor:WornItem worn = akActor.GetWornItem(aiSlotIndex)
	if worn && worn.item
		Controller.Log("Slot " + (aiSlotIndex + 30) + ": " + worn.item.GetName() + " (" + worn.item.GetFormID() + "), model " + worn.modelName)
	else
		Controller.Log("Slot " + (aiSlotIndex + 30) + ": nothing")
	endif
EndFunction

; MCM's keybinds and buttons may call this script instead of the controller (test 31): relayed.
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

; Test 41's console switches (cqf CMB_ControllerQuest ...), which can land on this script as
; EmergencyReset can: relayed.
Function DecideTeleportsAtOnce(int aiAtOnce)
	Controller.DecideTeleportsAtOnce(aiAtOnce)
EndFunction

Function WatchBusy(int aiOn)
	Controller.WatchBusy(aiOn)
EndFunction
