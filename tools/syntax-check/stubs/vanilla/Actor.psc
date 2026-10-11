Scriptname Actor extends ObjectReference Native Hidden
Function EquipItem(Form akItem, bool abPreventRemoval = false, bool abSilent = false) native
Function UnequipItem(Form akItem, bool abPreventEquip = false, bool abSilent = false) native
bool Function IsEquipped(Form akItem) native
bool Function IsInPowerArmor() native
bool Function IsDead() native
bool Function IsPlayerTeammate() native
bool Function IsInScene() native
int Function GetSitState() native
Function ChangeAnimArchetype(Keyword apKeyword = None) native
Function AttemptAnimationSetSwitch() native
Function EvaluatePackage(bool abResetAI) native
Event OnPlayerLoadGame()
EndEvent
