Scriptname ScriptObject Native Hidden
{Declaration-only stub for syntax checking. NOT the real Bethesda source.}

Function GotoState(string asNewState) native
string Function GetState() native
Var Function CallFunction(string asFuncName, Var[] aParams) native
ScriptObject Function CastAs(string asScriptName) native
Function StartTimer(float afInterval, int aiTimerID = 0) native
Function CancelTimer(int aiTimerID = 0) native
Function RegisterForPlayerTeleport() native
Function UnregisterForPlayerTeleport() native
Function AddInventoryEventFilter(Form akFilter) native
Function RemoveAllInventoryEventFilters() native

Event OnInit()
EndEvent
Event OnTimer(int aiTimerID)
EndEvent
Event OnPlayerTeleport()
EndEvent
Function RegisterForHitEvent(ScriptObject akTarget, ScriptObject akAggressorFilter = None, Form akSourceFilter = None, Form akProjectileFilter = None, int aiPowerFilter = -1, int aiSneakFilter = -1, int aiBashFilter = -1, int aiBlockFilter = -1, bool abMatch = true) native
Function UnregisterForHitEvent(ScriptObject akTarget, ScriptObject akAggressorFilter = None, Form akSourceFilter = None, Form akProjectileFilter = None, int aiPowerFilter = -1, int aiSneakFilter = -1, int aiBashFilter = -1, int aiBlockFilter = -1, bool abMatch = true) native
Event OnHit(ObjectReference akTarget, ObjectReference akAggressor, Form akSource, Projectile akProjectile, bool abPowerAttack, bool abSneakAttack, bool abBashAttack, bool abHitBlocked, string apMaterial)
EndEvent
