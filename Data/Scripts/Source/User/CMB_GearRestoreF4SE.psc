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
int Property LampSlotIndex = 0 Auto Const
{The headlamp piece's biped slot minus 30 (slot 58 = 28; 0 = none). Filled by the generator from LampSlot.}

Form rememberedItem = None
Form rememberedLampItem = None

Function RememberSlot(Actor akActor)
	rememberedItem = None
	rememberedLampItem = None
	Actor:WornItem worn = akActor.GetWornItem(BikeSlotIndex)
	if worn && worn.item && worn.item != CMB_BikeRiderArmor && worn.item != CMB_BikeRiderArmorFrame
		rememberedItem = worn.item
	endif
	if LampSlotIndex > 0
		worn = akActor.GetWornItem(LampSlotIndex)
		if worn && worn.item && worn.item != CMB_BikeRiderArmor && worn.item != CMB_BikeRiderArmorFrame && worn.item != rememberedItem
			rememberedLampItem = worn.item
		endif
	endif
EndFunction

Function RestoreSlot(Actor akActor)
	Form item = rememberedItem
	Form lampItem = rememberedLampItem
	rememberedItem = None
	rememberedLampItem = None
	if item && akActor.GetItemCount(item) > 0 && !akActor.IsEquipped(item)
		akActor.EquipItem(item, false, true)
	endif
	if lampItem && akActor.GetItemCount(lampItem) > 0 && !akActor.IsEquipped(lampItem)
		akActor.EquipItem(lampItem, false, true)
	endif
EndFunction

; What the biped holds in the bike's and the lamp piece's slots once the bike is on (test 33:
; the lamp piece's nodes were never found on the player's 3D).
Function LogWornSlots(Actor akActor)
	LogSlot(akActor, BikeSlotIndex)
	if LampSlotIndex > 0
		LogSlot(akActor, LampSlotIndex)
	endif
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
	Controller.HotkeyPressed()
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
