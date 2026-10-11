Scriptname CMB_SwimWatchEffectScript extends ActiveMagicEffect
{Goes on CMB_SwimWatchEffect, the effect of the hidden CMB_SwimWatchAbility that
the controller gives the player. The ability's condition (IsSwimming == 1) starts
the effect when the player starts swimming and ends it when they stop.}

CMB_ControllerScript Property Controller Auto Const Mandatory
{CMB_ControllerQuest}

Event OnEffectStart(Actor akTarget, Actor akCaster)
	Controller.SetSwimming(true)
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	Controller.SetSwimming(false)
EndEvent
