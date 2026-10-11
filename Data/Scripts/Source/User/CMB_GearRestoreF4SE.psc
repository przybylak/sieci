Scriptname CMB_GearRestoreF4SE extends Quest
{OPTIONAL - needs F4SE (and F4SE's script sources to compile).
Attach to CMB_ControllerQuest next to CMB_ControllerScript.
Whatever you wear in the bike's biped slot comes off when you get on; this
remembers it and puts it back on when you get off. Without F4SE that gear
just stays in your inventory.}

Armor Property CMB_BikeRiderArmor Auto Const Mandatory
int Property BikeSlotIndex Auto Const Mandatory
{The bike's biped slot minus 30 (slot 57 = 27). Filled by the plugin generator from BikeSlot.}

Form rememberedItem = None

Function RememberSlot(Actor akActor)
	rememberedItem = None
	Actor:WornItem worn = akActor.GetWornItem(BikeSlotIndex)
	if worn && worn.item && worn.item != CMB_BikeRiderArmor
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
