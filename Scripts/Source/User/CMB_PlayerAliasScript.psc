Scriptname CMB_PlayerAliasScript extends ReferenceAlias
{Goes on the Player alias of CMB_ControllerQuest. Lets the controller
re-apply riding state after a save is loaded.}

Event OnPlayerLoadGame()
	CMB_ControllerScript controller = GetOwningQuest() as CMB_ControllerScript
	if controller
		controller.OnGameReloaded()
	endif
EndEvent
