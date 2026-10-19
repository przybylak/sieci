Scriptname CMB_MCMRelay Hidden
{MCM's keybinds and buttons call these global functions (tests 30 and 31: a CallFunction on
the controller quest landed on whichever of its scripts MCM picked). Each finds the controller
quest in CommonwealthMotorbike.esp (form 0x80D) and calls it.}

CMB_ControllerScript Function Controller() global
	return Game.GetFormFromFile(0x080D, "CommonwealthMotorbike.esp") as CMB_ControllerScript
EndFunction

Function HotkeyPressed() global
	CMB_ControllerScript c = Controller()
	if c
		c.HotkeyPressed("the MCM hotkey")
	endif
EndFunction

Function HeadlampPressed() global
	CMB_ControllerScript c = Controller()
	if c
		c.HeadlampPressed()
	endif
EndFunction

Function RefreshHotkey() global
	CMB_ControllerScript c = Controller()
	if c
		c.RefreshHotkey()
	endif
EndFunction

Function ForceGiveKeys() global
	CMB_ControllerScript c = Controller()
	if c
		c.ForceGiveKeys()
	endif
EndFunction

Function EmergencyReset() global
	CMB_ControllerScript c = Controller()
	if c
		c.EmergencyReset()
	endif
EndFunction
