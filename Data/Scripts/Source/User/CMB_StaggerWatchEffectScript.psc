Scriptname CMB_StaggerWatchEffectScript extends ActiveMagicEffect
{Goes on the effect of the hidden CMB_StaggerWatchAbility that the controller gives the player
while riding. The effect's condition, IsStaggered == 1, starts it when the player is staggered
and ends it when the stagger is over (checked about once a second).}

CMB_ControllerScript Property Controller Auto Const Mandatory
{CMB_ControllerQuest}

Event OnEffectStart(Actor akTarget, Actor akCaster)
	Controller.NoteStagger(true)
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	Controller.NoteStagger(false)
EndEvent
