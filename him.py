import random
import json
import math
import re
def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)
def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
def applystatus(attacker, attacked, atkdie,atkbase,atkdmg,atkstagger,atkpage, log,pageusetype="Clash"):
    if not attacked.get("is_staggered", False) and attacked["stagger"] < 1:
        log.append(f"{symbol['stagger']} {attacked.get('name', 'Unknown')} Has been Staggered! {symbol['stagger']}")
        attacked["is_staggered"] = True
        attacked["resistances"] = {k: 2.0 for k in attacked.get("resistances", {})}
        attacked["sin_resistances"] = {k: 2.0 for k in attacked.get("sin_resistances", {})}
    
    if attacked["hp"] <= 0 and attacked["is_active"]:
        attacked["is_active"] = False
        log.append(f"{symbol['stagger']} {attacked.get('name', 'Unknown')} Has been Killed! {symbol['stagger']}")
        process_effects(attacker, attacked, atkdie, "on_kill", atkbase, atkpage,damage=atkdmg, stagger=atkstagger, log=log,pageusetype=pageusetype)
        process_effects(attacked, attacker, atkdie, "on_death", atkbase, atkpage,damage=atkdmg, stagger=atkstagger, log=log,pageusetype=pageusetype)

from THECORE import (PAGE_PATH ,  PASSIVE_PATH ,  PROFILE_PATH ,  RES_PATH ,  BUFF_PATH ,  GIFT_PATH, symbol)
def process_effects(source, target, dice, trigger, roll_container=None, source_page=None, damage=None, stagger=None, log=None, pageusetype="Clash"):
    if log is None:
        log = []
    
    effects = []
    passives = load_json(PASSIVE_PATH)
    buffs = load_json(BUFF_PATH)
    profiles = load_json(PROFILE_PATH)
    gifts = load_json(GIFT_PATH)
    pages = load_json(PAGE_PATH)
    resources = load_json(RES_PATH)


    for gift_name, egogift in gifts.items():
        if egogift.get("acquired"):
            effects.extend(egogift.get("effects", []))

    for passive_name in source.get("passives", []):
        passive_data = passives.get(passive_name, {})
        effects.extend(passive_data.get("effects", []))

    for buff_name, buff_data in source.get("buffs", {}).items():
        buff_def = buffs.get(buff_name)
        if buff_def:
            for eff in buff_def.get("effects", []):
                eff = eff.copy()
                eff["_buff_name"] = buff_name
                effects.append(eff)

    if isinstance(source_page, dict):
        effects.extend(source_page.get("effects", []))

    if dice and isinstance(dice, dict):
        effects.extend(dice.get("effects", []))

    def evaluate_cond(profile):
            condition_blocks = effect.get("condition", [])
            if not isinstance(condition_blocks, list):
                condition_blocks = [condition_blocks]

            for cond in condition_blocks:
                if "sp_min" in cond and profile.get("sp", 0) < cond["sp_min"]:
                    return False
                if "sp_max" in cond and profile.get("sp", 0) > cond["sp_max"]:
                    return False
                if "hp_min" in cond and profile.get("hp", 0) < cond["hp_min"]:
                    return False
                if "hp_max" in cond and profile.get("hp", 0) > cond["hp_max"]:
                    return False
                if "speed_min" in cond and profile.get("speed", 0) < cond["speed_min"]:
                    return False
                if "speed_max" in cond and profile.get("speed", 0) > cond["speed_max"]:
                    return False
                page_name = next(
                    (k for k, v in pages.items() if v is source_page),
                    None
                )
                if "pagecheck" in cond and page_name != cond["pagecheck"]:
                    return False
                if "dice_type" in cond and dice and dice.get("type") not in cond["dice_type"]:
                    return False
                if "pageusetype" in cond and pageusetype not in cond["pageusetype"]:
                    return False

                if "factioncheck" in cond:
                    requested = cond["factioncheck"]
                    self_faction = source.get("faction", [])
                    target_faction = profile.get("faction", [])
                    match = False
                    for req in requested:
                        if req == "Player" and any(f in self_faction for f in target_faction):
                            match = True
                        elif req == "Enemy" and not any(f in self_faction for f in target_faction):
                            match = True
                        elif req in target_faction:
                            match = True
                    if not match:
                        return False

                if "absolutefactioncheck" in cond:
                    if not any(f in profile.get("faction", []) for f in cond["absolutefactioncheck"]):
                        return False

                if "stack_min" in cond:
                    b = cond["stack_min"]
                    if profile.get("buffs", {}).get(b["buff"], {}).get("stacks", 0) < b["value"]:
                        return False
                if "stack_max" in cond:
                    b = cond["stack_max"]
                    if profile.get("buffs", {}).get(b["buff"], {}).get("stacks", 0) > b["value"]:
                        return False
                if "count_min" in cond:
                    b = cond["count_min"]
                    if profile.get("buffs", {}).get(b["buff"], {}).get("count", 0) < b["value"]:
                        return False
                if "count_max" in cond:
                    b = cond["count_max"]
                    if profile.get("buffs", {}).get(b["buff"], {}).get("count", 0) > b["value"]:
                        return False
                if "ifstaggered" in cond and profile.get("is_staggered") is not True:
                    return False
                
                if "resource_min" in cond:
                    b = cond["resource_min"]
                    value = b["value"]
                    sin = b["sin"]
                    faction1 = "Player" if "Player" == b.get("faction", "Player") else "Enemy"
                    faction2 = "Player" if "Player" in source.get("faction",[]) else "Enemy"
                    if b.get("absolute", False):
                        finalfaction = faction1
                    else:
                        finalfaction = "Player" if faction1 == faction2 else "Enemy"
                    if resources[finalfaction][sin] < value:
                        return False
                    
                if "resource_max" in cond:
                    b = cond["resource_max"]
                    value = b["value"]
                    sin = b["sin"]
                    faction1 = "Player" if "Player" == b.get("faction", "Player") else "Enemy"
                    faction2 = "Player" if "Player" in modifier_target.get("faction",[]) else "Enemy"
                    if b.get("absolute", False):
                        finalfaction = faction1
                    else:
                        finalfaction = "Player" if faction1 == faction2 else "Enemy"
                    if resources[finalfaction][sin] > value:
                        return False

                        
            return True


    def handle_everyone_logic(effect, source, target, profiles, log, roll_container, acquired_values):
        condition_target_key = effect.get("conditionTarget", "self")
        modifier_target_key = effect.get("modifierTarget", "self")
        condition = effect.get("condition", {})
        modifiers = effect.get("modifiers", {})

        all_profiles = [p for p in profiles.values() if p.get("is_active", True)]
        if effect.get("filterfaction"):
            for profile in all_profiles[:]:
                requested = effect["filterfaction"]
                self_faction = source.get("faction", [])
                target_faction = profile.get("faction", [])
                match = False
                for req in requested:
                    if req == "Player" and any(f in self_faction for f in target_faction):
                        match = True
                    elif req == "Enemy" and not any(f in self_faction for f in target_faction):
                        match = True
                    elif req in target_faction:
                        match = True
                if not match:
                    all_profiles.remove(profile)

        if condition_target_key == "everyone" and modifier_target_key != "everyone":
            if all(evaluate_cond(p) for p in all_profiles):
                target_profile = source if modifier_target_key == "self" else target
                apply_modifiers(modifiers, target_profile, acquired_values, effect, log, roll_container)

        elif condition_target_key != "everyone" and modifier_target_key == "everyone":
            cond_profile = source if condition_target_key == "self" else target
            if evaluate_cond(cond_profile):
                for p in all_profiles:
                    apply_modifiers(modifiers, p, acquired_values, effect, log, roll_container)

        elif condition_target_key == "everyone" and modifier_target_key == "everyone":
            for p in all_profiles:
                if evaluate_cond(p):
                    apply_modifiers(modifiers, p, acquired_values, effect, log, roll_container)
    def resolve_value(val, acquired_values):
            if isinstance(val, str):
                return acquired_values.get(val)
            elif isinstance(val, (int, float)):
                return val
            return None

    def apply_modifiers(modifiers, modifier_target, acquired_values, effect, log, roll_container):
        # === Modifiers ===
    

        if roll_container is not None:
            if "setpower" in modifiers and "locked" not in roll_container:
                val = resolve_value(modifiers["setpower"], acquired_values)
                roll_container[0] = val
                roll_container.append("locked")
                if log is not None:
                    log.append(f"{symbol['buff']} {source.get('name', 'Unknown')}'s roll is SET to {val} and now locked. {symbol['buff']}")

            if "power_bonus" in modifiers and "locked" not in roll_container:
                bonus = resolve_value(modifiers["power_bonus"], acquired_values)
                roll_container[0] += bonus
                if log is not None:
                    log.append(f"{symbol['buff']} {source.get('name', 'Unknown')} gains +{bonus} power to their roll. {symbol['buff']}")

            if "power_bonus_per_stack" in modifiers and "locked" not in roll_container:
                buff_name = effect.get("_buff_name")
                stacks = source.get("buffs", {}).get(buff_name, {}).get("stacks", 0)
                bonus = stacks * modifiers["power_bonus_per_stack"]
                roll_container[0] += bonus
                if log is not None:
                    log.append(f"{symbol['buff']} {source.get('name', 'Unknown')} gains +{bonus} power from {stacks} stacks of {buff_name}. {symbol['buff']}")


        # HP damage
        val = resolve_value(modifiers.get("takehpdamage"), acquired_values)
        if val is not None:
            modifier_target["hp"] -= val
            applystatus(source, target, dice, roll_container, damage, stagger,source_page,log=log,pageusetype=pageusetype)
            if log is not None:
                if val >= 0:
                    log.append(f"{symbol['stagger']} {modifier_target.get('name', 'Unknown')} takes {val} HP damage from effect. {symbol['stagger']}")
                else:
                    log.append(f"{symbol['buff']} {modifier_target.get('name', 'Unknown')} heals {abs(val)} HP from effect. {symbol['buff']}")
                    
        # SP damage

        val = resolve_value(modifiers.get("takespdamage"), acquired_values)
        if val is not None:
            modifier_target["sp"] -= val
            modifier_target["sp"] = max(-45, modifier_target["sp"])
            modifier_target["sp"] = min(45, modifier_target["sp"])
            if log is not None:
                if val >= 0:
                    log.append(f"{symbol['sanity']} {modifier_target.get('name', 'Unknown')} takes {val} SP damage from effect. {symbol['sanity']}")
                else:
                    log.append(f"{symbol['sanity']} {modifier_target.get('name', 'Unknown')} heals {abs(val)} SP from effect. {symbol['sanity']}")


        # tremor burst
        val = resolve_value(modifiers.get("tremorburst"), acquired_values)
        if val is not None:
            for x in range(val):
                process_effects(target, source, dice, "when_burst", roll_container, source_page, damage, stagger, log,pageusetype=pageusetype)
                process_effects(source, target, dice, "on_burst", roll_container, source_page, damage, stagger, log,pageusetype=pageusetype)
                if log is not None:
                    log.append(f"{symbol['stagger']} {modifier_target.get('name', 'Unknown')} Has been Tremor Bursted! {symbol['stagger']}")

        
        # Stagger damage
        val = resolve_value(modifiers.get("takestaggerdamage"), acquired_values)
        if val is not None:
            modifier_target["stagger"] -= val
            applystatus(source, target, dice, roll_container, damage, stagger,source_page,log=log,pageusetype=pageusetype)            
            if log is not None:
                if val >= 0:
                    log.append(f"{symbol['stagger']} {modifier_target.get('name', 'Unknown')} takes {val} Stagger damage from effect. {symbol['stagger']}")
                else:
                    log.append(f"{symbol['buff']} {modifier_target.get('name', 'Unknown')} heals {abs(val)} Stagger from effect. {symbol['buff']}")
        
        
        # Max Stagger damage
        val = resolve_value(modifiers.get("lowermaxstagger"), acquired_values)
        if val is not None:
            modifier_target["max_stagger"] -= val
            modifier_target["max_stagger"] = max(1, modifier_target["max_stagger"])
            applystatus(source, target, dice, roll_container, damage, stagger,source_page,log=log,pageusetype=pageusetype)
            if log is not None:
                if val >= 0:
                    log.append(f"{symbol['stagger']} {modifier_target.get('name', 'Unknown')} takes {val} Max Stagger damage from effect. {symbol['stagger']}")
                else:
                    log.append(f"{symbol['buff']} {modifier_target.get('name', 'Unknown')} heals {abs(val)} Max Stagger from effect. {symbol['buff']}")
                    
        
        # Max hp damage
        val = resolve_value(modifiers.get("lowermaxhp"), acquired_values)
        if val is not None:
            modifier_target["max_hp"] -= val
            modifier_target["max_hp"] = max(1, modifier_target["max_hp"])
            applystatus(source, target, dice, roll_container, damage, stagger,source_page,log=log,pageusetype=pageusetype)
            if log is not None:
                if val >= 0:
                    log.append(f"{symbol['stagger']} {modifier_target.get('name', 'Unknown')} takes {val} Max HP damage from effect. {symbol['stagger']}")
                else:
                    log.append(f"{symbol['buff']} {modifier_target.get('name', 'Unknown')} heals {abs(val)} Max HP from effect. {symbol['buff']}")

        # Critical
        val = resolve_value(modifiers.get("triggercrit"), acquired_values)
        if val is not None:
            random_roll = random.uniform(1, 100)
            if random_roll <= val:
                process_effects(source,target,dice,"on_crit", roll_container, source_page, damage, stagger, log,pageusetype=pageusetype)
                process_effects(target,source,dice,"when_crit", roll_container, source_page, damage, stagger, log,pageusetype=pageusetype)
            if log is not None:
                log.append(f"{symbol['stagger']} {modifier_target.get('name', 'Unknown')} takes {val} Max HP damage from effect. {symbol['stagger']}")



       # Flat Damage
        if "flatdamage" in modifiers:
            flat_block = modifiers["flatdamage"]
            if isinstance(flat_block, dict):
                for dtype, dmg_data in flat_block.items():
                    if isinstance(dmg_data, (int, float, str)):
                        dmg_data = {"damage": dmg_data}

                    raw_dmg = resolve_value(dmg_data.get("damage"), acquired_values)
                    raw_stagger = resolve_value(dmg_data.get("stagger"), acquired_values)

                    if raw_dmg is None and raw_stagger is None:
                        continue

                    resist = 1.0
                    stagger_resist = 1.0
                    type_parts = dtype.split()
                    valid_physical = ["slash", "blunt", "pierce"]

                    for part in type_parts:
                        part = part.strip()

                        if part in valid_physical:
                            resist *= modifier_target.get("resistances", {}).get(part, 1.0)
                            stagger_resist *= modifier_target.get("stagger_resistances", {}).get(part, 1.0)
                        elif part in ["Pride", "Wrath", "Lust", "Sloth", "Gluttony", "Gloom", "Envy", "White", "Black"]:
                            resist *= modifier_target.get("sin_resistances", {}).get(part, 1.0)

                    if raw_dmg is not None:
                        final_dmg = int(raw_dmg * resist)
                        modifier_target["hp"] -= final_dmg
                        applystatus(source, target, dice, roll_container, damage, stagger,source_page,log=log,pageusetype=pageusetype)
                        if log is not None:
                            log.append(f"{symbol['stagger']} {modifier_target.get('name', 'Unknown')} takes {final_dmg} {dtype} HP damage (resisted from {raw_dmg}). {symbol['stagger']}")

                    if raw_stagger is not None:
                        if any(part in valid_physical for part in type_parts):
                            final_stagger = int(raw_stagger * stagger_resist)
                            modifier_target["stagger"] -= final_stagger
                            applystatus(source, target, dice, roll_container, damage, stagger,source_page,log=log,pageusetype=pageusetype)
                            if log is not None:
                                log.append(f"{symbol['stagger']} {modifier_target.get('name', 'Unknown')} takes {final_stagger} {dtype} Stagger damage (resisted from {raw_stagger}). {symbol['stagger']}")



      
        # light
        val = resolve_value(modifiers.get("gainlight"), acquired_values)
        if val is not None:
            modifier_target["light"] = min(modifier_target.get("light", 0) + val, modifier_target.get("max_light", 3))
            if log is not None:
                log.append(f"{symbol['light']} {modifier_target.get('name', 'Unknown')} gains {val} light. {symbol['light']}")


        # light next turn
        val = resolve_value(modifiers.get("gainlightnext"), acquired_values)
        if val is not None:
            modifier_target["nextturn"]["light"] += val
            if log is not None:
                log.append(f"{symbol['light']} {modifier_target.get('name', 'Unknown')} will gain {val} light next turn. {symbol['light']}")
                
        # resource
        if modifiers.get("resource"):
            resourceblock = modifiers.get("resource")
            resources = load_json(RES_PATH)
            amount = resolve_value(resourceblock.get("amount"), acquired_values)
            if amount is not None:
                faction1 = "Player" if "Player" == resourceblock.get("faction", "Player") else "Enemy"
                faction2 = "Player" if "Player" in modifier_target.get("faction",[]) else "Enemy"
                if resourceblock.get("absolute", False):
                    finalfaction = faction1
                else:
                    finalfaction = "Player" if faction1 == faction2 else "Enemy"
                
                resource = resourceblock.get("sin")

                if resource in resources[finalfaction]:
                    resources[finalfaction][resource] += amount
                if log is not None:
                    log.append(f"{symbol['light']} {finalfaction} Faction gained {amount} bonus {resource} resources! {symbol['light']}")
                save_json(RES_PATH,resources)

        # Speed bonus per stack (e.g., from Haste)
        if trigger == "newturn" and "speed_bonus_per_stack" in modifiers:
            buff_name = effect.get("_buff_name")
            stacks = modifier_target.get("buffs", {}).get(buff_name, {}).get("stacks", 0)
            bonus = stacks * modifiers["speed_bonus_per_stack"]
            modifier_target["speed"] += bonus
            if log is not None:
                log.append(f"💨 {modifier_target.get('name', 'Unknown')} gains +{bonus} speed from {stacks} stacks of {buff_name}.")

        if trigger == "newturn" and "speed_bonus" in modifiers:
            bonus = modifiers["speed_bonus"]
            modifier_target["speed"] += bonus
            if log is not None:
                log.append(f"💨 {modifier_target.get('name', 'Unknown')} gains +{bonus} speed")


        # draw pages
        draw_val = resolve_value(modifiers.get("draw"), acquired_values)
        if draw_val:
            deck = modifier_target.get("deck", [])
            hand = modifier_target.setdefault("hand", [])
            drawn_cards = []
            deck_counts = {}
            for page in deck:
                deck_counts[page] = deck_counts.get(page, 0) + 1
            for _ in range(draw_val):
                hand_counts = {}
                for page in hand:
                    hand_counts[page] = hand_counts.get(page, 0) + 1
                eligible_pages = [
                    page for page, max_count in deck_counts.items()
                    if hand_counts.get(page, 0) < max_count
                ]
                if not eligible_pages:
                    break 
                drawn = random.choice(eligible_pages)
                hand.append(drawn)
                drawn_cards.append(drawn)

            if log is not None and drawn_cards:
                log.append(f"📜 {modifier_target.get('name', 'Unknown')} draws: {', '.join(drawn_cards)}")
        else:
            if modifiers.get("draw") is not None:
                modifier_target["hand"].append(modifiers["draw"])

                
        # Discard Pages
        discard = modifiers.get("discard")
        if discard is not None:
            amount = discard.get("amount")
            mode = discard.get("mode")
            discard_val = resolve_value(amount, acquired_values)
            if discard_val:
                hand = modifier_target.setdefault("hand", [])
                discarded_cards = []
                for _ in range(discard_val):
                    if not hand:
                        break
                    if mode == "random":
                        discarded = random.choice(hand)
                    elif mode == "lowest":
                        sorted_hand = sorted(hand, key=lambda page: pages[page]["light_cost"])
                        discarded = sorted_hand[0]
                    elif mode == "highest":
                        sorted_hand = sorted(hand, key=lambda page: pages[page]["light_cost"], reverse=True)
                        discarded = sorted_hand[0]
                    hand.remove(discarded)
                    discarded_cards.append(discarded) 
                    process_effects(source,target,dice,"on_discard", roll_container, pages[discarded], damage, stagger, log,pageusetype=pageusetype)
                if log is not None and discarded_cards:
                    log.append(f"📜 {modifier_target.get('name', 'Unknown')} discards: {', '.join(discarded_cards)}")

        # MY FAVOURITES
        modifier_target.setdefault("passives", [])

        # Add passive
        if "addpassive" in modifiers:
            new_passive = modifiers["addpassive"]
            modifier_target["passives"].append(new_passive)

        # Remove passive
        if "removepassive" in modifiers:
            old_passive = modifiers["removepassive"]
            if old_passive in modifier_target["passives"]:
                modifier_target["passives"].remove(old_passive)

        # changedamage
        if "changedamage" in modifiers:
            damageblock = modifiers.get("changedamage")
            damagetype = damageblock.get("type",[])
            damagesin = damageblock.get("sin", [])
            damagestagger = damageblock.get("stagger", False)
            damagemode = damageblock.get("mode","mult")
            value = damageblock.get("value",0)
            modded_damage = resolve_value(value, acquired_values)
            inverse_percent = damageblock.get("inverse_percent", None)

            if inverse_percent is not None:
                modded_damage = 1.0 - (modded_damage * inverse_percent)

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
        # changedice
        if "changedice" in modifiers:
            changedice = modifiers["changedice"]
            index = changedice.get("dice")
            dice_list = source_page["dice"]

            target_die = dice_list[index]

            if "boostmin" in changedice:
                target_die["min"] += changedice["boostmin"]
                target_die["minchanges"] = target_die.get("minchanges",0) + changedice["boostmin"]
            if "boostmax" in changedice:
                target_die["max"] += changedice["boostmax"]
                target_die["maxchanges"] = target_die.get("maxchanges",0) + changedice["boostmax"]
            if "invoke" in changedice:
                target_die["invoked"] = True


        #  Get Buff Handling 
        if "getbuff" in modifiers:
            buff_block = modifiers["getbuff"]

            is_nextturn = buff_block.get("nextturn", False)
            buff_dest = modifier_target.setdefault("nextturn", {}).setdefault("buffs", {}) if is_nextturn else modifier_target.setdefault("buffs", {})

            for buff_name, buff_data in buff_block.items():
                if buff_name == "nextturn":
                    continue  
                realbuff = buffs.get(buff_name)
                
               
                resolved_buff = {}
                for k, v in buff_data.items():
                    resolved_buff[k] = resolve_value(v, acquired_values)
                
                if buff_name in buff_dest:
                    existing = buff_dest[buff_name]
                    if "stacks" in resolved_buff:
                        existing["stacks"] = existing.get("stacks", 0) + resolved_buff["stacks"]
                    if "count" in resolved_buff:
                        existing["count"] = existing.get("count", 0) + resolved_buff["count"]
                    if "volatile" in resolved_buff:
                        existing["volatile"] = existing.get("volatile", False) or resolved_buff["volatile"]
                else:
                    buff_dest[buff_name] = resolved_buff
                    if realbuff.get("countable") and resolved_buff.get("count", 0) == 0:
                        buff_dest[buff_name]["count"] = 1
                    if resolved_buff.get("stacks", 0) == 0:
                        buff_dest[buff_name]["stacks"] = 1

                if buff_name in buff_dest:
                    buff = buff_dest[buff_name]
                    
                    if realbuff.get("countable", False):
                        count = buff.get("count")
                        if count is None or count <= 0:
                            del buff_dest[buff_name]
                            continue

                    stacks = buff.get("stacks")
                    if stacks is None or stacks <= 0:
                        del buff_dest[buff_name]
                        continue

                if buff_name in buff_dest:
                    if realbuff.get("max_stack",99) < buff_dest[buff_name].get("stacks", 0):
                        buff_dest[buff_name]["stacks"] = realbuff.get("max_stack")
                    if realbuff.get("countable", False) and  realbuff.get("max_count",99) < buff_dest[buff_name].get("count", 0):
                        buff_dest[buff_name]["count"] = realbuff.get("max_count")

                if log is not None:
                    stack = resolved_buff.get("stacks", 0)
                    count = resolved_buff.get("count", 0)
                    main = f"{stack} stacks" if stack != 0 else ""
                    connect = f" and " if stack != 0 and count != 0 else ""
                    extras = f"{count} count" if count != 0 else ""
                    buffemoji = symbol.get(buff_name,symbol["buff"])
                    if stack != 0 or count != 0:
                        log.append(f"{buffemoji} {buff_name} applied to {modifier_target.get('name', 'Unknown')} with {main}{connect}{extras}{' (next turn)' if is_nextturn else ''}. {buffemoji}")



    for effect in effects:
        if effect.get("trigger") != trigger:
            continue
        effect_id = f"{trigger}_{json.dumps(effect)}"
        limit = effect.get("limit_per_turn")
        global CURRENT_EFFECT_ID
        CURRENT_EFFECT_ID = f"{trigger}_{json.dumps(effect)}"

        if limit is not None:
            effect_log = source.setdefault("_effect_limits", {})
            count = effect_log.get(effect_id, 0)
            
            if count >= limit:
                continue
            else:
                effect_log[effect_id] = count + 1

        acquired_values = {}
        get_block = effect.get("get", {})
        for key, transform in get_block.items():
            val = None

            if isinstance(transform, dict) and "value" in transform:
                gettarget = source
                if "targetOverride" in transform:
                    gettarget = target
                
                buff_name = key
                field = transform["value"]
                val = gettarget.get("buffs", {}).get(buff_name, {}).get(field)
                if val is None:
                    continue

                try:
                    val = int(val)
                except (TypeError, ValueError):
                    continue

                if "mult" in transform:
                    mult = 0.01 * transform["mult"] if isinstance(transform["mult"], int) else resolve_value(transform["mult"], acquired_values)
                    val *= mult
                if "max" in transform:
                    val = min(val, resolve_value(transform["max"],acquired_values))
                if "min" in transform:
                    val = max(val, resolve_value(transform["re"],acquired_values))
                if "fix" in transform:
                    val = math.floor(val)
                if "multbycountstack" in transform:
                    val *= gettarget.get("buffs", {}).get(buff_name, {}).get(transform["multbycountstack"])
                alias_key = f"{buff_name}_{field}"
                acquired_values[alias_key] = val
                continue

            if isinstance(transform, dict) and key in ["Pride", "Wrath", "Lust", "Sloth", "Gluttony", "Gloom", "Envy", "White", "Black"]:
                gettarget = source
                if "targetOverride" in transform:
                    gettarget = target
                faction1 = "Player" if "Player" == transform.get("faction", "Player") else "Enemy"
                faction2 = "Player" if "Player" in gettarget.get("faction",[]) else "Enemy"
                if transform.get("absolute", False):
                    finalfaction = faction1
                else:
                    finalfaction = "Player" if faction1 == faction2 else "Enemy"
                
                sin = key
                
                val = resources[finalfaction][sin]
                if val is None:
                    continue

                try:
                    val = int(val)
                except (TypeError, ValueError):
                    continue

                if "mult" in transform:
                    mult = 0.01 * transform["mult"] if isinstance(transform["mult"], int) else resolve_value(transform["mult"], acquired_values)
                    val *= mult
                if "max" in transform:
                    val = min(val, resolve_value(transform["max"],acquired_values))
                if "fix" in transform:
                    val = math.floor(val)
                alias_key = f"{sin}_resource"
                acquired_values[alias_key] = val
                continue
            
            elif key == "speedDifference":
                val = source.get("speed", 0) - target.get("speed", 0)
                if isinstance(transform, dict) and "max" in transform:
                    val = min(val, transform["max"])
                if val < 0:
                    val = 0

            elif key == "damagedealt":
                val = damage[0]
            elif key == "staggerdealt":
                val = stagger[0]
            elif key == "roll":
                val = roll_container[0] if roll_container else 0
            else:
                if key in source:
                    val = source[key]
            if val is None:
                continue 

            if isinstance(transform, str):
                if transform == "none":
                    val = val
                else:
                    value = resolve_value(transform,acquired_values)
                    val *= value
            
            if isinstance(transform, int):
                mult = 0.01 * transform
                val *= mult

            acquired_values[key] = val



        condition = effect.get("condition", {})
        modifiers = effect.get("modifiers", {})
        condition_target_key = effect.get("conditionTarget", "self")
        modifier_target_key = effect.get("modifierTarget", "self")

        condition_target = source if condition_target_key == "self" else target
        modifier_target = source if modifier_target_key == "self" else target
        random_match = re.match(r"random(\d+)", modifier_target_key)
        if random_match:
            try:
                amount = int(random_match.group(1))
            except ValueError:
                amount = 1

            eligible = []
            all_profiles = list(profiles.values())
            random.shuffle(all_profiles)
            for p in all_profiles:
                if not p.get("is_active", True):
                    continue

                evaluate_cond(p)

                eligible.append(p)
                if len(eligible) == amount:
                    break

            for mod_target in eligible:
                apply_modifiers(modifiers, mod_target, acquired_values, effect, log, roll_container)
            continue
        dynamic_match = re.match(r"(highest|lowest)_(\w+)", modifier_target_key)
        if dynamic_match:
            direction, stat = dynamic_match.groups()
            all_profiles = [p for p in profiles.values() if p.get("is_active", True)]
            
            if effect.get("filterfaction"):
                filtered = []
                requested = effect["filterfaction"]
                self_faction = source.get("faction", [])
                for profile in all_profiles:
                    target_faction = profile.get("faction", [])
                    match = False
                    for req in requested:
                        if req == "Player" and any(f in self_faction for f in target_faction):
                            match = True
                        elif req == "Enemy" and not any(f in self_faction for f in target_faction):
                            match = True
                        elif req in target_faction:
                            match = True
                    if match:
                        filtered.append(profile)
                all_profiles = filtered

            condition_blocks = effect.get("condition", [])
            if not isinstance(condition_blocks, list):
                condition_blocks = [condition_blocks]

        
            candidates = [p for p in all_profiles if evaluate_cond(p)]
            if candidates:
                newtarget = max(candidates, key=lambda p: p.get(stat, float("-inf"))) if direction == "highest" else min(candidates, key=lambda p: p.get(stat, float("inf")))
                apply_modifiers(modifiers,newtarget,acquired_values,effect,log,roll_container)
                continue

        if condition_target is None or modifier_target is None:
            continue
        if effect.get("once_per_instance") and dice is not None:
            if "_used_effects" not in dice:
                dice["_used_effects"] = set()
            effect_id = json.dumps(effect, sort_keys=True)
            if effect_id in dice["_used_effects"]:
                continue
            dice["_used_effects"].add(effect_id)
        if "everyone" in (condition_target_key, modifier_target_key):
            handle_everyone_logic(effect, source, target, profiles, log, roll_container, acquired_values)
            continue
        if evaluate_cond(condition_target):
            apply_modifiers(modifiers, modifier_target, acquired_values, effect, log, roll_container)