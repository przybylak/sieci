Scriptname ObjectReference extends Form Native Hidden
bool Function Activate(ObjectReference akActivator, bool abDefaultProcessingOnly = false) native
Function AddItem(Form akItemToAdd, int aiCount = 1, bool abSilent = false) native
Function RemoveItem(Form akItemToRemove, int aiCount = 1, bool abSilent = false, ObjectReference akOtherContainer = None) native
int Function GetItemCount(Form akItem = None) native
Function Enable(bool abFadeIn = false) native
Function Disable(bool abFadeOut = false) native
bool Function IsDisabled() native
bool Function Is3DLoaded() native
bool Function IsInInterior() native
Function MoveTo(ObjectReference akTarget, float afXOffset = 0.0, float afYOffset = 0.0, float afZOffset = 0.0, bool abMatchRotation = true) native
float Function GetDistance(ObjectReference akOther) native
float Function GetAngleZ() native
Form Function GetBaseObject() native
float Function GetValue(ActorValue akAV) native
Function ModValue(ActorValue akAV, float afAmount) native
Event OnActivate(ObjectReference akActionRef)
EndEvent
Event OnItemAdded(Form akBaseItem, int aiItemCount, ObjectReference akItemReference, ObjectReference akSourceContainer)
EndEvent
Event OnItemRemoved(Form akBaseItem, int aiItemCount, ObjectReference akItemReference, ObjectReference akDestContainer)
EndEvent
Event OnLoad()
EndEvent
