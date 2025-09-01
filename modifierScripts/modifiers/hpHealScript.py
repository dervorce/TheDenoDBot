from modifierScripts.GlobalRegistry import *
from everythingexcepthim import applystatus, resolve_value
from UnitProfileCode import ProfileData

@register_modifier
class TakeHPDamageHandler(ModifierHandler):
    name = "recoverhp"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        value = resolve_value(value, acquired_values)
        modifier_target.heal_hp(value)
        if log is not None:
            if value >= 0:
                log.append(f"{symbol['buff']} {modifier_target.name} heals {value} HP from effect. {symbol['buff']}")
        await applystatus(kwargs["source"], modifier_target, kwargs["dice"], roll_container,
                          kwargs["damage"], kwargs["stagger"], kwargs["source_page"],
                          log=log, pageusetype=kwargs["pageusetype"], data=kwargs["data"], effect=effect)

