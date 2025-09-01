from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData

@register_modifier
class LightCostChangeHandler(ModifierHandler):
    name = "lightcostchange"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        if not isinstance(value, dict):
            return

        hand = getattr(modifier_target, "hand", {})

        if "all" in value.keys():
            delta = value["all"]
            resolved_delta = resolve_value(delta, acquired_values)

            for pageEntry in hand:
                hand[pageEntry]["cost"] += resolved_delta

        for page, delta in value.items():
            resolved_delta = resolve_value(delta, acquired_values)
            hand = getattr(modifier_target, "hand", {})
            if page in hand:
                hand[page]["cost"] += resolved_delta
                if log := kwargs.get("log"):
                    log.append(f"💡 {modifier_target.name} changes {page} cost by {resolved_delta}")
