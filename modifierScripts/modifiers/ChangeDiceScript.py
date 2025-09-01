from modifierScripts.GlobalRegistry import *
from everythingexcepthim import process_effects, applystatus
from UnitProfileCode import ProfileData

@register_modifier
class ChangeDiceHandler(ModifierHandler):
    name = "changedice"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        changedice = value
        index = changedice.get("dice")
        dicelistcopy = kwargs.get("dicelistcopy", [])
        dice = kwargs.get("dice")
        source = kwargs.get("source", {})

        if not pagename:
            pagename = "Unknown Page"

        # Determine which dice to modify
        if index == "self":
            targets = [dice]
        elif index == "next":
            if dice in dicelistcopy and dicelistcopy.index(dice) + 1 < len(dicelistcopy):
                targets = [dicelistcopy[dicelistcopy.index(dice) + 1]]
            else:
                targets = []
        elif index == "all":
            targets = dicelistcopy
        else:
            try:
                targets = [dicelistcopy[index]]
            except (IndexError, TypeError):
                targets = []

        # Apply changes to each target die
        for target_die in targets:
            die_num = dicelistcopy.index(target_die) + 1 if dicelistcopy else "??"

            if "boostmin" in changedice:
                target_die["min"] = target_die.get("min", 0) + changedice["boostmin"]
                # if log is not None:
                    # log.append(
                    #     f"Dice number {die_num} of {modifier_target.name}'s {pagename} gains +{changedice['boostmin']} Min Value"
                    # )

            if "boostmax" in changedice:
                target_die["max"] = target_die.get("max", 0) + changedice["boostmax"]
                # if log is not None:
                #     log.append(
                #         f"Dice number {die_num} of {modifier_target.name}'s {pagename} gains +{changedice['boostmax']} Max Value"
                #     )

            if "invoke" in changedice:
                target_die["invoked"] = True
                if changedice.get("perminvoke", False):
                    target_die["perminvoked"] = True
                if log is not None:
                    log.append(
                        f"Dice number {die_num} of {modifier_target.name}'s {pagename} Is Invoked!"
                    )

            if "reuse" in changedice:
                target_die["reuse"] = target_die.get("reuse", 0) + 1