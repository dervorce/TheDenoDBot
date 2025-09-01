from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData

@register_modifier
class SpeedDiceHandler(ModifierHandler):
    name = "speeddice"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        delta = resolve_value(value, acquired_values)
        modifier_target.attackslot = getattr(modifier_target, "attackslot", 1) + delta
        modifier_target.attackslotchange = getattr(modifier_target, "attackslotchange", 0) + delta

        if log := kwargs.get("log"):
            log.append(f"⚡ {modifier_target.name} gains +{delta} attack slot (speed dice)")