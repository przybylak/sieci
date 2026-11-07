Scriptname CMB_PlayerAliasScript extends ReferenceAlias
{Goes on the Player alias of CMB_ControllerQuest. Lets the controller
re-apply riding state after a save is loaded, and hears the mods made at
the field kit's armour menu (2026-11-07a).}

Event OnPlayerLoadGame()
	CMB_ControllerScript controller = GetOwningQuest() as CMB_ControllerScript
	if controller
		controller.OnGameReloaded()
	endif
EndEvent

; 2026-11-07a: a mod put on at a workbench; the controller keeps the bike's look item's (LookModded
; ignores every other item, and everything outside a Customise session).
Event OnPlayerModArmorWeapon(Form akBaseObject, ObjectMod akModBaseObject)
	CMB_ControllerScript controller = GetOwningQuest() as CMB_ControllerScript
	if controller
		controller.LookModded(akBaseObject, akModBaseObject)
	endif
EndEvent
