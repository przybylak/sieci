Scriptname CMB_SideBagScript extends ObjectReference
{Goes on the CMB_SideBagContainer base object.
Limits how much fits in the side bag, using the CMB_BagCapacity global:
 - with F4SE installed, the limit is in pounds;
 - without F4SE, the limit is the number of items.
Raise it from the console with:  set CMB_BagCapacity to 200
0 or less means unlimited.}

GlobalVariable Property CMB_BagCapacity Auto Const Mandatory
Actor Property PlayerRef Auto Const Mandatory

float currentWeight = 0.0
int f4seState = -1 ; -1 = not checked yet, 0 = missing, 1 = present

Event OnInit()
	; Fallout 4 only sends inventory events once a filter is set. None = everything.
	AddInventoryEventFilter(None)
EndEvent

; Called by the controller after every save load.
Function OnGameReloaded()
	f4seState = -1
	RemoveAllInventoryEventFilters()
	AddInventoryEventFilter(None)
	if GetItemCount(None) == 0
		currentWeight = 0.0
	endif
EndFunction

Event OnItemAdded(Form akBaseItem, int aiItemCount, ObjectReference akItemReference, ObjectReference akSourceContainer)
	float capacity = CMB_BagCapacity.GetValue()
	int overflow = 0

	if HasF4SE()
		float itemWeight = GetItemWeight(akBaseItem)
		currentWeight += itemWeight * aiItemCount
		if capacity > 0.0 && currentWeight > capacity && itemWeight > 0.0
			overflow = Math.Ceiling((currentWeight - capacity) / itemWeight)
		endif
	elseif capacity > 0.0
		int itemsInBag = GetItemCount(None)
		int maxItems = capacity as int
		if itemsInBag > maxItems
			overflow = itemsInBag - maxItems
		endif
	endif

	if overflow > 0
		if overflow > aiItemCount
			overflow = aiItemCount
		endif
		ReturnOverflow(akBaseItem, akItemReference, overflow, akSourceContainer)
		ReportFull(capacity)
	endif
EndEvent

Event OnItemRemoved(Form akBaseItem, int aiItemCount, ObjectReference akItemReference, ObjectReference akDestContainer)
	if HasF4SE()
		currentWeight -= GetItemWeight(akBaseItem) * aiItemCount
	endif
	if currentWeight < 0.0 || GetItemCount(None) == 0
		currentWeight = 0.0
	endif
EndEvent

Function ReturnOverflow(Form akBaseItem, ObjectReference akItemReference, int aiCount, ObjectReference akSourceContainer)
	ObjectReference target = akSourceContainer
	if target == None
		target = PlayerRef
	endif
	if akItemReference && aiCount == 1
		RemoveItem(akItemReference, 1, true, target)
	else
		RemoveItem(akBaseItem, aiCount, true, target)
	endif
EndFunction

Function ReportFull(float afCapacity)
	if HasF4SE()
		Debug.Notification("The side bag is full (" + Math.Floor(afCapacity) + " lbs max).")
	else
		Debug.Notification("The side bag is full (" + Math.Floor(afCapacity) + " items max).")
	endif
EndFunction

; F4SE is optional, so it is detected and called by name instead of being a
; compile-time dependency.
bool Function HasF4SE()
	if f4seState < 0
		Var version = Utility.CallGlobalFunction("F4SE", "GetVersionRelease", new Var[0])
		if version == None
			f4seState = 0
		else
			f4seState = 1
		endif
	endif
	return f4seState == 1
EndFunction

float Function GetItemWeight(Form akItem)
	if akItem == None
		return 0.0
	endif
	Var weight = akItem.CallFunction("GetWeight", new Var[0])
	if weight == None
		return 0.0
	endif
	return weight as float
EndFunction
