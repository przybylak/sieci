Scriptname Utility Native Hidden
Function Wait(float afSeconds) native global
bool Function IsInMenuMode() native global
Var Function CallGlobalFunction(string asScriptName, string asFuncName, Var[] aParams) native global
; F4SE: game settings by "name:section" (in memory; nothing is written to the INI files)
float Function GetINIFloat(string ini) native global
Function SetINIFloat(string ini, float value) native global debugOnly
