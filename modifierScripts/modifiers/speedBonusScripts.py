from modifierScripts.GlobalRegistry import *
from everythingexcepthim import process_effects, applystatus
from UnitProfileCode import ProfileData

@register_modifier
class SpeedBonusPerStackHandler(ModifierHandler):
    name = "speed_bonus_per_stack"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        buff_name = effect.get("_buff_name")
        stack = modifier_target.buffs.get(buff_name, {}).get("stack", 0)
        bonus = stack * value
        modifier_target.current_speed += bonus

        if log is not None:
            log.append(f"💨 {modifier_target.name} gains +{bonus} speed from {stack} stack(s) of {buff_name}.")

@register_modifier
class SpeedBonusHandler(ModifierHandler):
    name = "speed_bonus"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        modifier_target.current_speed += value

        if log is not None:
            log.append(f"💨 {modifier_target.name} gains +{value} speed.")
