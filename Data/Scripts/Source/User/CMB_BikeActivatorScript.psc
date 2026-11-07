Scriptname CMB_BikeActivatorScript extends ObjectReference
{Goes on the CMB_BikeActivator base object (the parked motorbike).
Activating it offers: Ride / Open side bag / Customise / Cancel (Customise since the 2026-11-07a
build, shown while CMB_LookOn is 1).}

CMB_ControllerScript Property Controller Auto Const Mandatory
{CMB_ControllerQuest}
Message Property CMB_ParkedMenu Auto Const Mandatory
{Buttons in this order: Ride / Open side bag / Customise / Cancel (Customise hidden while
CMB_LookOn is 0, the others keeping their numbers).}

Event OnActivate(ObjectReference akActionRef)
	if akActionRef != Controller.PlayerRef
		return
	endif
	; 2026-11-07a: the bike's look as the MCM has it now (nothing if unchanged since it was put on).
	Controller.LookSync("the bike's activation")
	int choice = CMB_ParkedMenu.Show()
	; Test 40: every use of the bike is logged, with what it did (0 ride, 1 side bag, 2 customise, 3 cancel).
	Controller.Log("Parked bike activated: choice " + choice + ".")
	if choice == 0
		Controller.Mount()
	elseif choice == 1
		Controller.OpenSideBag()
	elseif choice == 2
		Controller.BeginCustomise()
	endif
EndEvent
