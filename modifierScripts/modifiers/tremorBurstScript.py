from modifierScripts.GlobalRegistry import *
from everythingexcepthim import process_effects, resolve_value
from UnitProfileCode import ProfileData

@register_modifier
class TremorBurstHandler(ModifierHandler):
    name = "tremorburst"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        value = resolve_value(value, acquired_values)
        target = kwargs.get("target") or modifier_target

        for _ in range(value):
            if log is not None:
                log.append(f"{symbol['stagger']} {modifier_target.name} Has been Tremor Bursted! {symbol['stagger']}")
            await process_effects(target, modifier_target, kwargs["dice"], "when_burst",
                                  roll_container, kwargs["source_page"], kwargs["damage"], kwargs["stagger"],
                                  log, pageusetype=kwargs["pageusetype"], data=kwargs["data"], interaction=kwargs["interaction"])
            await process_effects(modifier_target, target, kwargs["dice"], "on_burst",
                                  roll_container, kwargs["source_page"], kwargs["damage"], kwargs["stagger"],
                                  log, pageusetype=kwargs["pageusetype"], data=kwargs["data"], interaction=kwargs["interaction"])