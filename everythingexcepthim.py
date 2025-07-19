# pyright: reportMissingImports=false
import random
import json
import re
import discord
from discord import app_commands
from him import process_effects
from THECORE import (PAGE_PATH ,  PASSIVE_PATH ,  PROFILE_PATH ,  RES_PATH ,  BUFF_PATH, symbol )
def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def resetinvokeables(page):
    for dice in page:
        if dice.get("invokeable",False):
            dice["invoked"] = False
        if dice.get("minchanges"):
            dice["min"] -= dice["minchanges"]
            del dice["minchanges"]
        if dice.get("maxhanges"):
            dice["max"] -= dice["maxhanges"]
            del dice["maxhanges"]

def update_profiles(batch: dict):
    """Batch update multiple profiles at once."""
    data = load_json(PROFILE_PATH)
    data.update(batch) 
    save_json(PROFILE_PATH, data)

def get_rigged_roll(profile, min_val, max_val):
    rig_config = load_json("data/rig_config.json")
    if not rig_config.get("enabled"):
        return random.randint(min_val, max_val)

    force_rolls = rig_config.get("force_rolls", {})
    name = profile.get("name")
    faction = "Player" if "Player" in profile.get("faction", []) else "Enemy"

    if name in force_rolls.get("profiles", {}):
        rule = force_rolls["profiles"][name]
    else:
        rule = force_rolls.get(faction, "normal")

    if rule == "max":
        return max_val
    elif rule == "min":
        return min_val
    elif isinstance(rule, int):
        return max(min_val, min(max_val, rule))
    else:
        return random.randint(min_val, max_val)

def resolve_dynamic_target(target: str, condition_targets: list, all_profiles: list):
    match = re.match(r"(highest|lowest)_(\w+)", target)
    if not match:
        return []  # Not a dynamic stat target

    direction, stat = match.groups()

    # Filter condition_targets from all_profiles
    candidates = [p for p in all_profiles if p in condition_targets]

    if not candidates:
        return []

    if direction == "highest":
        return [max(candidates, key=lambda p: p.get(stat, float("-inf")))]
    else:
        return [min(candidates, key=lambda p: p.get(stat, float("inf")))]
def pagepricegetter(tier):
    match tier:
        case "Paperback": 
            return random.randint(5000,10000)
        case "Hardcover": 
            return random.randint(15000,25000)
        case "Limited": 
            return random.randint(30000,50000)
        case "Objet D'Art": 
            return random.randint(50000,70000)
def get_sp_bonus(sp):
    return sp // 15 
def get_speed_bonus(a,t):
    aspeed = a.get("speed",0)
    tspeed = t.get("speed",0)
    return (aspeed-tspeed) / 3

def resource(profile, page):
    resources = load_json(RES_PATH)
    faction = "Player" if "Player" in profile.get("faction", []) else "Enemy"
    
    dice_list = page.get("dice", [])
    if not dice_list:
        return 

    resource = dice_list[0].get("sin")
    if not resource or resource == "none":
        return 

    if resource in resources[faction]:
        resources[faction][resource] += 1
    save_json(RES_PATH,resources)

def calculate_damage(roll, defender, dice, stagger=False):
    resist_type = "resistances" if not stagger else "stagger_resistances"
    resist = defender.get(resist_type, {}).get(dice.get("type"), 1.0)
    sin_resist = defender.get("sin_resistances", {}).get(dice.get("sin"), 1.0)
    return int(roll * resist * sin_resist)

async def autocomplete_page_names(interaction: discord.Interaction, current: str):
    pages = load_json(PAGE_PATH)
    current = current.lower()

    return [
        app_commands.Choice(name=page_name, value=page_name)
        for page_name in pages
        if current in page_name.lower()
    ][:25]
async def autocomplete_profile_names(interaction: discord.Interaction, current: str):
    profiles = load_json(PROFILE_PATH)
    current = current.lower()
    return [
        app_commands.Choice(name=profile_name, value=profile_name)
        for profile_name, profile in profiles.items()
        if current in profile_name.lower()
        and profile["is_active"]
    ][:25]


def get_extra_targets(main_target, profiles, attacker_faction, attackweight=1, indiscriminate=False):
    if attackweight <= 1:
        return []

    potential_targets = []
    for name, profile in profiles.items():
        if not profile.get("is_active", True):
            continue
        if name == main_target.get("name"):
            continue
        if not indiscriminate:
            if attacker_faction == "Player" and "Enemy" not in profile.get("faction", []):
                continue
            if attacker_faction == "Enemy" and "Player" not in profile.get("faction", []):
                continue
        potential_targets.append(profile)

    random.shuffle(potential_targets)
    return potential_targets[:attackweight - 1]

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