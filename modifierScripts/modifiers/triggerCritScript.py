from modifierScripts.GlobalRegistry import *
from everythingexcepthim import process_effects, applystatus, resolve_value
from UnitProfileCode import ProfileData
import random


@register_modifier
class TriggerCritHandler(ModifierHandler):
    name = "triggercrit"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        value = resolve_value(value, acquired_values)
        random_roll = random.uniform(1, 100)
        target = kwargs.get("target") or modifier_target

        if random_roll <= value:
            await process_effects(target, modifier_target, kwargs["dice"], "when_crit",
                                  roll_container, kwargs["source_page"], kwargs["damage"], kwargs["stagger"],
                                  log, pageusetype=kwargs["pageusetype"], data=kwargs["data"], interaction=kwargs["interaction"])
            await process_effects(modifier_target, target, kwargs["dice"], "on_crit",
                                  roll_container, kwargs["source_page"], kwargs["damage"], kwargs["stagger"],
                                  log, pageusetype=kwargs["pageusetype"], data=kwargs["data"], interaction=kwargs["interaction"])
            critdamagemult = 50
            if "critdamagemult" in kwargs["data"]["StorageBox"].get(kwargs["source"].name, {}):
                critdamagemult = kwargs["data"]["StorageBox"][kwargs["source"].name]["critdamagemult"]
            else:
                kwargs["data"]["StorageBox"].setdefault(kwargs["source"].name, {})["critdamagemult"] = 50
            kwargs["damage"][0] *= 1 + (0.01 * critdamagemult)
            kwargs["stagger"][0] *= 1 + (0.01 * critdamagemult)
            if log is not None:
                log.append(
                    f"{symbol['Poise']} {kwargs['source'].name} landed a CRITICAL HIT! {symbol['Poise']}")