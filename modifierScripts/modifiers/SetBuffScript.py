from modifierScripts.GlobalRegistry import *
from everythingexcepthim import resolve_value, process_effects
from UnitProfileCode import ProfileData

@register_modifier
class SetBuffHandler(ModifierHandler):
    name = "setbuff"

    async def apply(self, value, modifier_target : ProfileData, acquired_values, effect, log, roll_container, pagename, symbol, **kwargs):
        if not isinstance(value, dict):
            return


        target = kwargs.get("target") or modifier_target

        print(f"{modifier_target.name}: {value}")

        for buff_name, buff_data in value.items():
            print(f"{modifier_target.name}: has triggered the buff {self.name} with value {value} and {kwargs['buffs'].get(buff_name, {})} ")

            is_nextturn = buff_data.get("nextturn", False)
            # Determine target dict
            buff_dest = getattr(modifier_target, "nextturn", {}) if is_nextturn else getattr(modifier_target, "buffs",
                                                                                             {})
            if is_nextturn:
                modifier_target.nextturn = getattr(modifier_target, "nextturn", {})
                buff_dest = modifier_target.nextturn.setdefault("buffs", {})
            else:
                modifier_target.buffs = getattr(modifier_target, "buffs", {})
                buff_dest = modifier_target.buffs

            # Lookup buff template
            realbuff = kwargs["buffs"].get(buff_name, {})

            # Resolve values
            resolved_buff = {k: resolve_value(v, acquired_values) for k, v in buff_data.items() if k != "nextturn"}

            # Merge with existing buff
            if buff_name in buff_dest:
                existing = buff_dest[buff_name]
                if "stack" in resolved_buff:
                    existing["stack"] = resolved_buff["stack"]
                if "count" in resolved_buff:
                    existing["count"] = resolved_buff["count"]
                if "volatile" in resolved_buff:
                    existing["volatile"] = existing.get("volatile", False) or resolved_buff["volatile"]
            else:
                buff_dest[buff_name] = resolved_buff
                # Set defaults for countable buffs
                if realbuff.get("countable") and resolved_buff.get("count", 0) == 0:
                    buff_dest[buff_name]["count"] = 1
                if resolved_buff.get("stack", 0) == 0:
                    buff_dest[buff_name]["stack"] = 1

            # Validate buff (remove if depleted)
            buff = buff_dest.get(buff_name)
            if buff:
                if realbuff.get("countable", False):
                    count = buff.get("count")
                    if count is None or count <= 0:
                        del buff_dest[buff_name]
                        continue
                stack = buff.get("stack")
                if stack is None or stack <= 0:
                    del buff_dest[buff_name]
                    continue

                # Clamp max values
                if realbuff.get("max_stack", 99) < buff.get("stack", 0):
                    buff["stack"] = realbuff.get("max_stack", 99)
                if realbuff.get("countable", False) and realbuff.get("max_count", 99) < buff.get("count", 0):
                    buff["count"] = realbuff.get("max_count", 99)

            # Logging
            if log is not None and buff_name in buff_dest:
                stack = resolved_buff.get("stack", 0)
                count = resolved_buff.get("count", 0)
                main = f"{stack} stack" if stack != 0 else ""
                connect = " and " if stack != 0 and count != 0 else ""
                extras = f"{count} count" if count != 0 else ""
                buffemoji = symbol.get(buff_name, symbol.get("buff", "✨"))


                if stack != 0 or count != 0:
                    log.append(
                        f"{buffemoji} {buff_name} applied to {modifier_target.name} with {main}{connect}{extras}{' (next turn)' if is_nextturn else ''}. {buffemoji}")