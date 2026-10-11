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

Event OnInit()
EndEvent
Event OnTimer(int aiTimerID)
EndEvent
Event OnPlayerTeleport()
EndEvent
