Scriptname CMB_BikeActivatorScript extends ObjectReference
{Goes on the CMB_BikeActivator base object (the parked motorbike).
Activating it offers: Ride / Open side bag / Cancel.}

CMB_ControllerScript Property Controller Auto Const Mandatory
{CMB_ControllerQuest}
Message Property CMB_ParkedMenu Auto Const Mandatory
{Buttons in this order: Ride / Open side bag / Cancel.}

Event OnActivate(ObjectReference akActionRef)
	if akActionRef != Controller.PlayerRef
		return
	endif
	int choice = CMB_ParkedMenu.Show()
	; Test 40: every use of the bike is logged, with what it did (0 ride, 1 side bag, 2 cancel).
	Controller.Log("Parked bike activated: choice " + choice + ".")
	if choice == 0
		Controller.Mount()
	elseif choice == 1
		Controller.OpenSideBag()
	endif
EndEvent
