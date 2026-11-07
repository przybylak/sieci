Scriptname Actor extends ObjectReference Native Hidden
Function EquipItem(Form akItem, bool abPreventRemoval = false, bool abSilent = false) native
Function UnequipItem(Form akItem, bool abPreventEquip = false, bool abSilent = false) native
bool Function IsEquipped(Form akItem) native
bool Function IsInPowerArmor() native
bool Function IsDead() native
bool Function IsPlayerTeammate() native
bool Function IsInScene() native
int Function GetSitState() native
bool Function ChangeAnimArchetype(Keyword apKeyword = None) native
bool Function ChangeAnimFlavor(Keyword apKeyword = None) native
Function AttemptAnimationSetSwitch() native
Function EvaluatePackage(bool abResetAI) native
Event OnPlayerLoadGame()
EndEvent
bool Function IsInCombat() native
bool Function IsSprinting() native
bool Function IsHostileToActor(Actor akActor) native
bool Function IsWeaponDrawn() native
bool Function AddSpell(Spell akSpell, bool abVerbose = true) native
bool Function RemoveSpell(Spell akSpell) native
Function AddPerk(Perk akPerk, bool abNotify = false) native
Function RemovePerk(Perk akPerk) native
bool Function HasPerk(Perk akPerk) native
Event OnPlayerFallLongDistance(float afDamage)
EndEvent
Event OnItemEquipped(Form akBaseObject, ObjectReference akReference)
EndEvent
bool Function IsEssential() native
bool Function IsInFaction(Faction akFaction) native
Race Function GetRace() native
bool Function IsChild() native
Function Kill(Actor akKiller = None) native
Actor Function GetKiller() native
ActorBase Function GetLeveledActorBase() native
Function DoCombatSpellApply(Spell akSpell, ObjectReference akTarget) native
int Function GetLevel() native
bool Function SnapIntoInteraction(ObjectReference akTarget) native
Event OnPlayerModArmorWeapon(Form akBaseObject, ObjectMod akModBaseObject)
EndEvent
