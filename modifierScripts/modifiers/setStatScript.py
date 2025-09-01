from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData

@register_modifier
class SetStatHandler(ModifierHandler):
    name = "setstat"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        if not isinstance(value, dict):
            return

        for stat, stat_value in value.items():
            resolved_value = resolve_value(stat_value, acquired_values)
            if hasattr(modifier_target, stat):
                setattr(modifier_target, stat, resolved_value)
            elif stat in modifier_target.__dict__:  # fallback for dict-like access
                modifier_target[stat] = resolved_value
            # optional: log if you want
            if log := kwargs.get("log"):
                log.append(f"⚡ {modifier_target.name} sets {stat} to {resolved_value}")