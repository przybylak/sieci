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
		Controller.HotkeyPressed("the F4SE hotkey")
	endif
EndEvent

; MCM's keybinds and buttons call a function on the controller quest, and may land on this
; script rather than CMB_ControllerScript (test 30: "Failed to call member function
; HeadlampPressed on CMB_HotkeyF4SE"): relayed.
Function HotkeyPressed()
	Controller.HotkeyPressed("the MCM hotkey")
EndFunction

Function HeadlampPressed()
	Controller.HeadlampPressed()
EndFunction

Function RefreshHotkey()
	RegisterHotkey()
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
