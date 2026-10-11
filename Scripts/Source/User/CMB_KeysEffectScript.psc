Scriptname CMB_KeysEffectScript extends ActiveMagicEffect
{Goes on CMB_BikeKeysEffect, the magic effect of the Motorbike Keys aid item.
Using the keys: get off if riding, get on if the bike is close,
otherwise offer to call the bike over or open the side bag.}

CMB_ControllerScript Property Controller Auto Const Mandatory
{CMB_ControllerQuest}

Event OnEffectStart(Actor akTarget, Actor akCaster)
	if akTarget == Controller.PlayerRef
		Controller.RequestKeysAction()
	endif
EndEvent
