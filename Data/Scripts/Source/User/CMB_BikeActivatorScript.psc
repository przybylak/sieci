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
	; 2026-11-09a (test 51's black screen; the plugin's [Look] MountGuard, CMB_LookOptions bit 16): one activation at a
	; time (the controller's ActivationBegin refuses a press while another's menu or choice is under way, so no second box
	; opens behind getting on's fade), the menu first, and the look synced after it for choices 1-3 only (Ride's is
	; Mount's own LookSync). Without the bit: 2026-11-09a's order as of t54-merge (the look, then the menu).
	bool guarded = Controller.LookOption(16)
	int ticket = 0
	if guarded
		ticket = Controller.ActivationBegin()
		if ticket <= 0
			return
		endif
	else
		; 2026-11-07a: the bike's look as the MCM has it now (nothing if unchanged since it was put on).
		Controller.LookSync("the bike's activation")
	endif
	int choice = CMB_ParkedMenu.Show()
	; Test 40: every use of the bike is logged, with what it did (0 ride, 1 side bag, 2 customise, 3 cancel).
	Controller.Log("Parked bike activated: choice " + choice + ".")
	if guarded && choice != 0
		Controller.LookSync("the bike's activation")
	endif
	if choice == 0
		Controller.Mount()
	elseif choice == 1
		Controller.OpenSideBag()
	elseif choice == 2
		Controller.BeginCustomise()
	endif
	if guarded
		Controller.ActivationEnd(ticket)
	endif
EndEvent
