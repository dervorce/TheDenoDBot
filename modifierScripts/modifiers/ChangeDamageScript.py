from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData

@register_modifier
class ChangeDamageHandler(ModifierHandler):
    name = "changedamage"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        damageblock = value
        damagetype = damageblock.get("type", [])
        damagesin = damageblock.get("sin", [])
        damagestagger = damageblock.get("stagger", False)
        damagemode = damageblock.get("mode", "mult")
        base_value = damageblock.get("value", 0)
        modded_damage = resolve_value(base_value, acquired_values)
        inverse_percent = damageblock.get("inverse_percent")

        if inverse_percent is not None:
            modded_damage = 1.0 - (modded_damage * inverse_percent)

        dice = kwargs.get("dice", {})
        damage = kwargs.get("damage")
        stagger = kwargs.get("stagger")

        if damage is None or stagger is None:
            return  # Nothing to modify

        type_match = not damagetype or dice.get("type") in damagetype
        sin_match = not damagesin or dice.get("sin") in damagesin

        if type_match and sin_match:
            if damagestagger:
                if damagemode == "add":
                    stagger[0] += modded_damage
                elif damagemode == "mult":
                    stagger[0] *= modded_damage
            else:
                if damagemode == "add":
                    damage[0] += modded_damage
                elif damagemode == "mult":
                    damage[0] *= modded_damage