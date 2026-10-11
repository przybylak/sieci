Scriptname ScriptObject Native Hidden
{Declaration-only stub (vanilla + F4SE additions) for syntax checking. NOT the real source.}

Function GotoState(string asNewState) native
string Function GetState() native
Var Function CallFunction(string asFuncName, Var[] aParams) native
ScriptObject Function CastAs(string asScriptName) native
Function StartTimer(float afInterval, int aiTimerID = 0) native
Function CancelTimer(int aiTimerID = 0) native
Function RegisterForPlayerTeleport() native
Function UnregisterForPlayerTeleport() native

; F4SE
Function RegisterForKey(int key) native
Function UnregisterForKey(int key) native

Event OnInit()
EndEvent
Event OnTimer(int aiTimerID)
EndEvent
Event OnPlayerTeleport()
EndEvent

; F4SE
Event OnKeyDown(int keyCode)
EndEvent
Event OnKeyUp(int keyCode, float time)
EndEvent
