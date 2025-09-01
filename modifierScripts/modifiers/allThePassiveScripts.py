from modifierScripts.GlobalRegistry import *
from everythingexcepthim import process_effects, applystatus
from UnitProfileCode import ProfileData

@register_modifier
class AddPassiveHandler(ModifierHandler):
    name = "addpassive"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        if value not in modifier_target.passives:
            modifier_target.passives.append(value)

        if log is not None:
            log.append(f"🌀 {modifier_target.name} gains passive: {value}")


@register_modifier
class RemovePassiveHandler(ModifierHandler):
    name = "removepassive"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        if value in modifier_target.passives:
            modifier_target.passives.remove(value)
            if log is not None:
                log.append(f"⛔ {modifier_target.name} loses passive: {value}")



@register_modifier
class RevealPassiveHandler(ModifierHandler):
    name = "revealpassive"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        if value in modifier_target.passives:
            data = kwargs["data"]
            if "passives" in data and value in data["passives"]:
                data["passives"][value]["hidden"] = False
                if log is not None:
                    log.append(f"👁 {modifier_target.name} reveals passive: {value}")