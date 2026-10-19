Scriptname CMB_KeysEffectScript extends ActiveMagicEffect
{Goes on CMB_BikeKeysEffect, the magic effect of the Motorbike Keys aid item.
Using the keys: get off if riding, get on if the bike is close,
otherwise offer to call the bike over or open the side bag.}

CMB_ControllerScript Property Controller Auto Const Mandatory
{CMB_ControllerQuest}

; Test 40: the keys used outside Diamond City left no line, so it isn't known whether a use got
; this far. Each way out of here is logged now; the controller logs the use itself ("Keys used").
Event OnEffectStart(Actor akTarget, Actor akCaster)
	if !Controller
		Debug.Trace("[CMB] Keys effect started (target " + akTarget + "), but its Controller property is empty: nothing done.")
	elseif akTarget != Controller.PlayerRef
		Controller.Log("Keys effect started on " + akTarget + " (caster " + akCaster + "), not the player: nothing done.")
	else
		Controller.RequestKeysAction()
	endif
EndEvent
