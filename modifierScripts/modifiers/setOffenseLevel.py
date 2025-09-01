from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData

@register_modifier
class SetOffenseLevelHandler(ModifierHandler):
    name = "setoffenselevel"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        if not isinstance(value, dict):
            return

        source = value.get("source")
        modifier_value = value.get("modifier")

        if source is None or modifier_value is None or modifier_target is None:
            print("this shit is malformed inside of setoffenselevel")
            return

        resolved_value = resolve_value(modifier_value, acquired_values)

        if not hasattr(modifier_target, "offense_level_sources"):
            modifier_target.offense_level_sources = {}

        modifier_target.offense_level_sources[source] = resolved_value
        modifier_target.calc_total_offense_level()

        # # Optional: log it
        # if log := kwargs.get("log"):
        #     log.append(
        #         f"⚡ {modifier_target.name} sets offense level source '{source}' to {resolved_value}"
        #     )

@register_modifier
class SetDefenseLevelHandler(ModifierHandler):
    name = "setdefenselevel"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        if not isinstance(value, dict):
            return

        source = value.get("source")
        modifier_value = value.get("modifier")

        if source is None or modifier_value is None or modifier_target is None:
            print("this shit is malformed inside of setdefenselevel")
            return

        resolved_value = resolve_value(modifier_value, acquired_values)

        if not hasattr(modifier_target, "defense_level_sources"):
            modifier_target.defense_level_sources = {}

        modifier_target.defense_level_sources[source] = resolved_value
        modifier_target.calc_total_defense_level()

        # # Optional: log it
        # if log := kwargs.get("log"):
        #     log.append(
        #         f"⚡ {modifier_target.name} sets offense level source '{source}' to {resolved_value}"
        #     )