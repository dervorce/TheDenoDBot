from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value
from UnitProfileCode import ProfileData

@register_modifier
class StorageBoxHandler(ModifierHandler):
    name = "storagebox"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        lookup = kwargs["lookup"]
        if kwargs["target"] is not None:
            lookup["target"] = kwargs["target"].name

        for entry in value:
            resolved_name = lookup.get(entry.get("name"), entry.get("name"))
            valuename = entry.get("valuename")
            box = kwargs["data"].setdefault("StorageBox", {}).setdefault(resolved_name, {})

            if entry.get("value") == "Delete":
                box.pop(valuename, None)
                continue

            finalvalue = resolve_value(entry.get("value"), acquired_values)
            if entry.get("mode", "regular") != "add" and entry.get("mode", "regular") != "lower":
                box[valuename] = finalvalue
            if entry.get("mode", "regular") == "lower":
                box[valuename] -= finalvalue
            else:
                box.setdefault(valuename, 0)
                box[valuename] += finalvalue