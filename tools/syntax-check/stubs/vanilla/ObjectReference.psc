Scriptname ObjectReference extends Form Native Hidden
bool Function Activate(ObjectReference akActivator, bool abDefaultProcessingOnly = false) native
Function AddItem(Form akItemToAdd, int aiCount = 1, bool abSilent = false) native
Function RemoveItem(Form akItemToRemove, int aiCount = 1, bool abSilent = false, ObjectReference akOtherContainer = None) native
int Function GetItemCount(Form akItem = None) native
Function Enable(bool abFadeIn = false) native
Function Disable(bool abFadeOut = false) native
bool Function IsDisabled() native
bool Function Is3DLoaded() native
Cell Function GetParentCell() native
ObjectReference Function PlaceAtMe(Form akFormToPlace, int aiCount = 1, bool abForcePersist = false, bool abInitiallyDisabled = false, bool abDeleteWhenAble = true) native
Function Delete() native
bool Function IsInInterior() native
WorldSpace Function GetWorldSpace() native
Function MoveTo(ObjectReference akTarget, float afXOffset = 0.0, float afYOffset = 0.0, float afZOffset = 0.0, bool abMatchRotation = true) native
float Function GetDistance(ObjectReference akOther) native
float Function GetAngleZ() native
float Function GetPositionX() native
float Function GetPositionY() native
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
Function SetAngle(float afXAngle, float afYAngle, float afZAngle) native
Function SetAnimationVariableBool(string asVariableName, bool abNewValue) native
bool Function GetAnimationVariableBool(string asVariableName) native
float Function GetValuePercentage(ActorValue akAV) native
Function RestoreValue(ActorValue akAV, float afAmount) native
float Function GetPositionZ() native
Function SetPosition(float afX, float afY, float afZ) native
Function MoveToNearestNavmeshLocation() native
