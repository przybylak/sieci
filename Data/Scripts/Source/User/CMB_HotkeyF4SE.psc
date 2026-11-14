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
; 2026-11-14a (test 53: a stimpak by number key at speed never healed). QuickCut: when the plugin could not take a potion's
; number key from the game (QuickUse off, the hook not reached), it cuts the game's use clip at its props before the item
; came and, once the clip is seen over, writes -(count * 16 + slot): QuickCutUse equips that slot's potion as QuickUse does,
; unless the game used that very potion itself (a chem is applied at its key and its signal can come after the cut), seen
; by this script's own OnItemEquipped. The script's own equips are marked and never taken for the game's (the skeptic's
; finding 1). quickLastCount: the last write's count, so a write missed between two looks is said (finding 3); 0 after
; this script's own -1 (the plugin's next count is 1), -1 not known (a save of an older build, the watch off).
int quickLastCount = -1
Form quickOwnItem = None
float quickOwnAt = -100.0
Form lastPotion = None
float lastPotionAt = -100.0

Function QuickWatch(bool abOn)
	CancelTimer(TimerQuickUse)
	GlobalVariable quick = Controller.CMB_RiderQuickUse
	bool was = quickWatching
	quickWatching = abOn && quick != None
	if quickWatching
		if !was || quick.GetValue() == 0.0
			quick.SetValue(-1.0)   ; on: the plugin takes presses from now; none was taken before (it was 0)
			quickSeen = -1
			quickLastCount = 0
		endif   ; on already (a load into a ride: the save's watch): its last value kept, so a press since is still seen
		RegisterForRemoteEvent(Controller.PlayerRef, "OnItemEquipped")   ; 2026-11-14a: the game's own uses, for QuickCutUse
		StartTimer(QuickUsePoll, TimerQuickUse)
	elseif quick
		quick.SetValue(0.0)   ; off: every quickkey the game's own again
	endif
	if was && !quickWatching
		UnregisterForRemoteEvent(Controller.PlayerRef, "OnItemEquipped")
	endif
EndFunction

Event OnTimer(int aiTimerID)
	if aiTimerID != TimerQuickUse || !quickWatching
		return
	endif
	int value = Controller.CMB_RiderQuickUse.GetValue() as int
	if value != quickSeen
		quickSeen = value
		QuickCountSeen(value)   ; 2026-11-14a: a write missed between two looks said
		if value > 0   ; -1 and 0 are the watch's own words, no press
			QuickUse(value)
		elseif value <= -16   ; 2026-11-14a, QuickCut: off this timer, so the 0.1-s look goes on through its wait (finding 3)
			Var[] cut = new Var[1]
			cut[0] = -value
			CallFunctionNoWait("QuickCutUse", cut)
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
		QuickEquip(potion)
	endif
EndFunction

; 2026-11-14a: the plugin's writes count 1, 2, ... (999, then 1 again) over a ride; one more than the last plus one is a
; write this script never saw (written over within its look): said by the controller, that press's item not used.
Function QuickCountSeen(int aiValue)
	int size = aiValue
	if size < 0
		size = -size
	endif
	if size < 16
		if aiValue == -1
			quickLastCount = 0   ; the watch on afresh: the plugin's next count is 1
		else
			quickLastCount = -1  ; off
		endif
		return
	endif
	int count = size / 16
	if quickLastCount >= 0 && count != quickLastCount % 999 + 1
		Var[] args = new Var[3]
		args[0] = quickLastCount
		args[1] = count
		args[2] = aiValue
		Controller.CallFunctionNoWait("QuickGap", args)
	endif
	quickLastCount = count
EndFunction

; 2026-11-14a (QuickCut): aiValue = count * 16 + slot of the plugin's -(count * 16 + slot). The game's own use of that potion
; within 2.0 s (this script's OnItemEquipped) means it was used: not again; else after 0.3 s, looked at once more (2.5 s),
; then equipped as QuickUse does. The controller is told first (QuickUsed, the value negative), as for QuickUse.
Function QuickCutUse(int aiValue)
	int slot = aiValue % 16
	Form item = None
	Form[] slots = FavoritesManager.GetFavorites()
	if slots && slot >= 1 && slot <= slots.Length
		item = slots[slot - 1]
	endif
	Potion potion = item as Potion
	int count = 0
	if potion
		if QuickGameUsed(potion, 2.0)
			count = -1
		else
			Utility.Wait(0.3)
			if !quickWatching
				count = -2   ; the ride over meanwhile: nothing used (said in the log, review)
			elseif QuickGameUsed(potion, 2.5)
				count = -1
			else
				count = Controller.PlayerRef.GetItemCount(potion)
			endif
		endif
	endif
	Var[] args = new Var[4]
	args[0] = item
	args[1] = slot
	args[2] = -aiValue
	args[3] = count
	Controller.CallFunctionNoWait("QuickUsed", args)
	if potion && count > 0
		QuickEquip(potion)
	endif
EndFunction

bool Function QuickGameUsed(Potion akPotion, float afWithin)
	return lastPotion == akPotion && Utility.GetCurrentRealTime() - lastPotionAt <= afWithin
EndFunction

; The script's own equip (QuickUse, QuickCut), marked first so its OnItemEquipped isn't taken for the game's own use.
Function QuickEquip(Potion akPotion)
	quickOwnItem = akPotion
	quickOwnAt = Utility.GetCurrentRealTime()
	Controller.PlayerRef.EquipItem(akPotion, false, true)
EndFunction

; 2026-11-14a: the potions the game itself uses while the watch is on (registered in QuickWatch), for QuickCutUse.
Event Actor.OnItemEquipped(Actor akSender, Form akBaseObject, ObjectReference akReference)
	if !quickWatching || !(akBaseObject as Potion)
		return
	endif
	float now = Utility.GetCurrentRealTime()
	if quickOwnItem && akBaseObject == quickOwnItem && now - quickOwnAt <= 2.0
		quickOwnItem = None   ; this script's own equip
		return
	endif
	lastPotion = akBaseObject
	lastPotionAt = now
EndEvent
