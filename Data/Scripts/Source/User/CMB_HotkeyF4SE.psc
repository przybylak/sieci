Scriptname CMB_HotkeyF4SE extends Quest
{OPTIONAL - needs F4SE (and F4SE's script sources to compile).
Attach to CMB_ControllerQuest next to CMB_ControllerScript.
Press the hotkey to get on or off; if the bike is far away it gets called over.
Change the key with:  set CMB_HotkeyCode to <DirectX scan code> (0 = off)
then save and reload, or use the MCM menu. Default 48 (0x30) = B.}

CMB_ControllerScript Property Controller Auto Const Mandatory
{CMB_ControllerQuest}
GlobalVariable Property CMB_HotkeyCode Auto Const Mandatory

int registeredKey = 0

Event OnInit()
	RegisterHotkey()
EndEvent

; Also called by the controller after every save load.
Function RegisterHotkey()
	int wanted = CMB_HotkeyCode.GetValue() as int
	if registeredKey > 0 && registeredKey != wanted
		UnregisterForKey(registeredKey)
	endif
	if wanted > 0
		RegisterForKey(wanted)
	endif
	registeredKey = wanted
EndFunction

Event OnKeyDown(int keyCode)
	if keyCode == registeredKey
		Controller.HotkeyPressed()
	endif
EndEvent
