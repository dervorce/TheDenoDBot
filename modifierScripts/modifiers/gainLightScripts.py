from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value, process_effects
from UnitProfileCode import ProfileData

@register_modifier
class GainLightHandler(ModifierHandler):
    name = "gainlight"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        value = resolve_value(value, acquired_values)
        modifier_target.heal_light(value)
        await process_effects(modifier_target, None, kwargs["dice"], "on_lightgain",
                              roll_container, kwargs["source_page"], kwargs["damage"], kwargs["stagger"],
                              log, pageusetype=kwargs["pageusetype"], data=kwargs["data"],
                              interaction=kwargs["interaction"])
        if log is not None:
            log.append(
                f"{symbol['light']} {modifier_target.name} gains {value} light. {symbol['light']}")

@register_modifier
class GainLightIgnoreLimitsHandler(ModifierHandler):
    name = "gainlightignoremax"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        value = resolve_value(value, acquired_values)
        modifier_target.heal_light(value, True)
        await process_effects(modifier_target, None, kwargs["dice"], "on_lightgain",
                              roll_container, kwargs["source_page"], kwargs["damage"], kwargs["stagger"],
                              log, pageusetype=kwargs["pageusetype"], data=kwargs["data"],
                              interaction=kwargs["interaction"])
        if log is not None:
            log.append(
                f"{symbol['light']} {modifier_target.name} gains {value} light (ignoring max light capacity. {symbol['light']}")


@register_modifier
class GainLightNextTurn(ModifierHandler):
    name = "gainlightnext"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        value = resolve_value(value, acquired_values)
        modifier_target.nextturn["light"] += value
        if log is not None:
            log.append(
                f"{symbol['light']} {modifier_target.name} will gain {value} light next turn. {symbol['light']}")
