from modifierScripts.GlobalRegistry import *
from everythingexcepthim import process_effects, applystatus, attackhandler
from UnitProfileCode import ProfileData

@register_modifier
class ForceActionHandler(ModifierHandler):
    name = "forceaction"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        lookup = kwargs["lookup"]
        target = kwargs["target"]
        modifiers = kwargs["modifiers"]
        interaction = kwargs["interaction"]
        print(f"[DEBUG] inside of forceaction.apply, interaction is {interaction}")


        if target is not None:
            lookup["target"] = target.name
        await attackhandler(interaction, lookup[modifiers["forceaction"]["attacker"]],
                            lookup[modifiers["forceaction"]["target"]], modifiers["forceaction"]["page"], kwargs["data"])

