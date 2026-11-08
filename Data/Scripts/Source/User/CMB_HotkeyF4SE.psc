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

; 2026-11-10a (test 52: a potion's hotkey at speed was never applied: the engine's animated use applies the item at its
; clip's event, about a second in, and UseStop cut the clip before it). QuickUse: CMB_Slope.dll ([Steer] QuickUse) takes a
; potion's quickkey from the game while riding at speed and writes CMB_RiderQuickUse = count * 16 + slot (count 1-999, slot
; 1-12). While riding (the controller's RideWatchesOn and RideWatchesOff) this script looks at it every 0.1 s; on a change
; it equips that slot's potion itself with Actor.EquipItem, the Pip-Boy's own path: applied at once, no engine clip. F4SE's
; GetFavorites lists the 12 slots in order, None for an empty one (F4SE's PapyrusFavoritesManager.cpp pushes favorites[0]
; to [11], the array the plugin reads), so slot N is index N - 1. The controller is told first, without waiting (QuickUsed:
; its line and the mark its OnItemEquipped reads), then the potion is equipped; a slot emptied since, another kind of item
; in it, or a stack's last one gone: told, nothing used. Without the global (an older ESP) no watch runs.
; The watch's word to the plugin (review A2/B2: a press at speed before the watch was on was taken from the game and
; never used): CMB_RiderQuickUse 0 = no watch (the ESP's value; the plugin gives every quickkey to the game), -1 = the
; watch on, no press yet. The plugin takes a press only while the global isn't 0, and writes count * 16 + slot over it.
int Property TimerQuickUse = 56 AutoReadOnly
float Property QuickUsePoll = 0.1 AutoReadOnly
bool quickWatching = false
int quickSeen = 0

Function QuickWatch(bool abOn)
	CancelTimer(TimerQuickUse)
	GlobalVariable quick = Controller.CMB_RiderQuickUse
	bool was = quickWatching
	quickWatching = abOn && quick != None
	if quickWatching
		if !was || quick.GetValue() == 0.0
			quick.SetValue(-1.0)   ; on: the plugin takes presses from now; none was taken before (it was 0)
			quickSeen = -1
		endif   ; on already (a load into a ride: the save's watch): its last value kept, so a press since is still seen
		StartTimer(QuickUsePoll, TimerQuickUse)
	elseif quick
		quick.SetValue(0.0)   ; off: every quickkey the game's own again
	endif
EndFunction

Event OnTimer(int aiTimerID)
	if aiTimerID != TimerQuickUse || !quickWatching
		return
	endif
	int value = Controller.CMB_RiderQuickUse.GetValue() as int
	if value != quickSeen
		quickSeen = value
		if value > 0   ; -1 and 0 are the watch's own words, no press
			QuickUse(value)
		endif
	endif
	if quickWatching
		StartTimer(QuickUsePoll, TimerQuickUse)
	endif
EndEvent

Function QuickUse(int aiValue)
	int slot = aiValue % 16
	Form item = None
	Form[] slots = FavoritesManager.GetFavorites()
	if slots && slot >= 1 && slot <= slots.Length
		item = slots[slot - 1]
	endif
	Potion potion = item as Potion
	int count = 0
	if potion
		count = Controller.PlayerRef.GetItemCount(potion)
	endif
	Var[] args = new Var[4]
	args[0] = item
	args[1] = slot
	args[2] = aiValue
	args[3] = count
	Controller.CallFunctionNoWait("QuickUsed", args)
	if potion && count > 0
		Controller.PlayerRef.EquipItem(potion, false, true)
	endif
EndFunction
