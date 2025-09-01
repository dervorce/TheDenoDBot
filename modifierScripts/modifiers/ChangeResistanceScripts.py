from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData

@register_modifier
class OverWriteResistanceHandler(ModifierHandler):
    name = "overwriteresistance"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        if not isinstance(value, dict):
            return

        physical_resistances = {"slash", "pierce", "blunt"}

        for res, res_value in value.items():
            resolved_value = resolve_value(res_value, acquired_values)

            if res in physical_resistances:
                modifier_target.resistances[res] = resolved_value
                dict_name = "resistances"
            else:
                modifier_target.sin_resistances[res] = resolved_value
                dict_name = "sin_resistances"

            if log := kwargs.get("log"):
                log.append(f"🛡 {modifier_target.name} sets {dict_name} '{res}' to {resolved_value}")

@register_modifier
class IncreaseResistancesHandler(ModifierHandler):
    name = "increaseresistance"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        if not isinstance(value, dict):
            return

        physical_resistances = {"slash", "pierce", "blunt"}

        for res, res_value in value.items():
            resolved_value = (resolve_value(res_value, acquired_values)) / 10

            if res in physical_resistances:
                balls = modifier_target.resistances[res]
                modifier_target.resistances[res] = balls + resolved_value
                dict_name = "resistances"
            else:
                balls = modifier_target.sin_resistances[res]
                modifier_target.sin_resistances[res] = balls + resolved_value
                dict_name = "sin_resistances"

            if log := kwargs.get("log"):
                log.append(f"🛡 {modifier_target.name} sets {dict_name} '{res}' to {resolved_value}")

@register_modifier
class LowerResistanceHandler(ModifierHandler):
    name = "lowerresistance"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        if not isinstance(value, dict):
            return

        physical_resistances = {"slash", "pierce", "blunt"}

        for res, res_value in value.items():
            resolved_value = (resolve_value(res_value, acquired_values)) / 10

            if res in physical_resistances:
                balls = modifier_target.resistances[res] - resolved_value
                modifier_target.resistances[res] = balls
                dict_name = "resistances"
            else:
                balls = modifier_target.sin_resistances[res] - resolved_value
                modifier_target.sin_resistances[res] = balls
                dict_name = "sin_resistances"

            if log := kwargs.get("log"):
                log.append(f"🛡 {modifier_target.name} sets {dict_name} '{res}' to {balls}")