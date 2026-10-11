Scriptname CMB_SwimWatchEffectScript extends ActiveMagicEffect
{Goes on the effects of the hidden CMB_SwimWatchAbility that the controller gives
the player. Each effect's condition starts it when the player gets in and ends it
when they get out: CMB_SwimWatchEffect has IsSwimming == 1 (deep water),
CMB_WadeWatchEffect has IsInWater == 1 (any water, wading too).}

CMB_ControllerScript Property Controller Auto Const Mandatory
{CMB_ControllerQuest}
bool Property Wading = false Auto Const
{True on CMB_WadeWatchEffect: reports being in water at all rather than swimming.}

Event OnEffectStart(Actor akTarget, Actor akCaster)
	Report(true)
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	Report(false)
EndEvent

Function Report(bool abIn)
	if Wading
		Controller.SetInWater(abIn)
	else
		Controller.SetSwimming(abIn)
	endif
EndFunction
