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

; 2026-11-02a (test 48: the camera stuck after a stimpak): F4SE's camera state for the controller's
; check after an item's use (0 first person, 7 and 8 third person), called through CastAs so the
; controller runs without F4SE.
int Function CameraState()
	return Game.GetCameraState()
EndFunction

; 2026-11-06a (test 49: another mod's dummy potion after a load): F4SE's favourites for the controller's
; OnItemEquipped (CMB_RiderUseOwn). 1 the item is the player's own to use: in a favourite slot, or in the cache
; of them (a stack's last stimpak leaves its slot as it is used by its hotkey); 0 not (a nameless form, listed
; nowhere, or in no slot: another mod's EquipItem); -1 unknown (no favourites list).
Form[] favouritesCache

int Function ItemOwnUse(Form akItem)
	if !akItem || akItem.GetName() == ""
		return 0
	endif
	Form[] slots = FavoritesManager.GetFavorites()
	if slots && slots.Find(akItem) >= 0
		return 1
	endif
	if favouritesCache && favouritesCache.Find(akItem) >= 0
		return 1
	endif
	if !slots
		return -1
	endif
	return 0
EndFunction

; Called by the controller at getting on, after a load into a ride and at each Pip-Boy or Favourites close
; (favourites change only in menus).
Function CacheFavourites()
	favouritesCache = FavoritesManager.GetFavorites()
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
