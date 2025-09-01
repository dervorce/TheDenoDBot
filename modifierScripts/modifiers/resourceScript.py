from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData
import random

@register_modifier
class ResourceHandler(ModifierHandler):
    name = "resource"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        resources = kwargs["data"]["res"]

        resourceblock = kwargs["modifiers"].get("resource")
        amount = resolve_value(resourceblock.get("amount"), acquired_values)
        if amount is not None:
            faction1 = "Player" if "Player" == resourceblock.get("faction", "Player") else "Enemy"
            faction2 = modifier_target.PlayerOrEnemy
            if resourceblock.get("absolute", False):
                finalfaction = faction1
            else:
                finalfaction = "Player" if faction1 == faction2 else "Enemy"

            resource = resourceblock.get("sin")
            if resource.startswith("random"):
                resource = resource[6:]
                allsins = ["Wrath", "Sloth", "Envy", "Lust", "Pride", "Gluttony", "Gloom"]
                eligiblesins = list(set(allsins) - set(resourceblock.get("exclude", [])))
                for _ in range(int(resource)):
                    sin = random.choice(eligiblesins)
                    if sin in resources[finalfaction]:
                        resources[finalfaction][sin] += amount
                        if log is not None:
                            log.append(
                                f"{symbol['light']} {finalfaction} Faction gained {amount} bonus {sin} resources! {symbol['light']}")
            else:
                if resource in resources[finalfaction]:
                    resources[finalfaction][resource] += amount
                    if log is not None:
                        log.append(
                            f"{symbol['light']} {finalfaction} Faction gained {amount} bonus {resource} resources! {symbol['light']}")
