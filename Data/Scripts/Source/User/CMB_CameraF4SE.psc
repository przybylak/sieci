Scriptname CMB_CameraF4SE extends Quest
{OPTIONAL - needs F4SE (and F4SE's script sources to compile).
Attach to CMB_ControllerQuest next to CMB_ControllerScript.
Moves the third-person camera farther back while riding and puts it back afterwards.
How far the camera normally sits is the game setting fVanityModeMaxDist ([Camera]),
also the farthest the mouse wheel zooms out. F4SE's Utility.SetINIFloat changes it in
memory only: nothing is written to the INI files, and a restart resets it anyway.
SetINIFloat is debugOnly, which only means calls are dropped from scripts compiled in
release-final mode; these scripts aren't (Debug.Trace is debugOnly too).}

string Property MaxDistSetting = "fVanityModeMaxDist:Camera" AutoReadOnly

float originalMax = 0.0
float ridingMax = 0.0
bool applied = false

; Riding: the camera at least afDistance back (game units; 0 = leave it alone).
; Returns true when that moved the camera limit, so the caller can re-enter third
; person for it to take effect.
bool Function ApplyRidingCamera(float afDistance)
	if afDistance <= 0.0
		RestoreCamera(0.0)
		return false
	endif
	float current = Utility.GetINIFloat(MaxDistSetting)
	; Remember the player's own value, unless what's set now is ours from an earlier
	; ride (a save loaded in the same session keeps the in-memory setting).
	if !applied || current != ridingMax
		originalMax = current
	endif
	if originalMax <= 0.0
		Debug.Trace("[CMB] Camera: " + MaxDistSetting + " not found or 0; leaving the camera alone.")
		applied = false
		return false
	endif
	float target = afDistance
	if target < originalMax
		target = originalMax
	endif
	applied = true
	ridingMax = target
	if current == target
		return false
	endif
	Utility.SetINIFloat(MaxDistSetting, target)
	Debug.Trace("[CMB] Camera: " + MaxDistSetting + " " + current + " -> " + target + " while riding.")
	return true
EndFunction

; Back to the player's own distance (the argument is unused; it keeps both calls alike).
Function RestoreCamera(float afUnused)
	if !applied
		return
	endif
	applied = false
	if Utility.GetINIFloat(MaxDistSetting) == ridingMax
		Utility.SetINIFloat(MaxDistSetting, originalMax)
		Debug.Trace("[CMB] Camera: " + MaxDistSetting + " back to " + originalMax + ".")
	endif
EndFunction
