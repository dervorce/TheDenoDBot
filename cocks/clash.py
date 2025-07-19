# pyright: reportMissingImports=false
import copy
import discord
from discord.ext import commands
from discord import app_commands
from him import process_effects
from everythingexcepthim import (
    load_json ,
    update_profiles ,
    get_rigged_roll ,
    get_sp_bonus ,
    resource ,
    calculate_damage ,
    autocomplete_page_names ,
    autocomplete_profile_names ,
    get_extra_targets ,
     resetinvokeables, save_json,
    applystatus ,get_speed_bonus)
from THECORE import (PAGE_PATH ,  PROFILE_PATH , symbol)
class ClashCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #@app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="clash")
    @app_commands.describe(attacker="Attacker name", attacker_page="Attacker page", defender="Defender name", defender_page="Defender page")
    @app_commands.autocomplete(
        attacker_page=autocomplete_page_names,
        attacker=autocomplete_profile_names,
        defender_page=autocomplete_page_names,
        defender=autocomplete_profile_names
    )

    async def clash(self,interaction: discord.Interaction, attacker: str, attacker_page: str, defender: str, defender_page: str):
        
        profiles = load_json(PROFILE_PATH)
        pages = load_json(PAGE_PATH)
        a = profiles.get(attacker)
        d = profiles.get(defender)
        a_page = pages.get(attacker_page)
        d_page = pages.get(defender_page)
        pageusetype = "Clash"
        if not all([a, d, a_page, d_page]):
            await interaction.response.send_message("Invalid input.")
            return
        
        if attacker_page not in a.get("hand", []) or defender_page not in d.get("hand", []):
            await interaction.response.send_message("One or both pages not in hand.")
            return
        
        if a.get("light", 0) < a_page.get("light_cost", 1):
            await interaction.response.send_message(f"{attacker} lacks light to use {attacker_page}.")
            return

        log = []
        
        a["light"] -= a_page.get("light_cost", 1)
        d["light"] -= d_page.get("light_cost", 1)
        process_effects(a, d, None, "on_use", source_page=a_page, log=log,pageusetype=pageusetype)
        process_effects(d, a, None, "on_use", source_page=d_page, log=log,pageusetype=pageusetype)
        resource(a,a_page)
        resource(d,d_page)
        a_dice = copy.deepcopy(a_page["dice"])
        d_dice = copy.deepcopy(d_page["dice"])
        
        a_evade_queue = []
        d_evade_queue = []


        while a_dice or d_dice or a_evade_queue or d_evade_queue:
            a_die = a_evade_queue.pop(0) if a_evade_queue else (a_dice.pop(0) if a_dice else None)
            d_die = d_evade_queue.pop(0) if d_evade_queue else (d_dice.pop(0) if d_dice else None)
            

            if a_die and d_die:
                auninvoked = False
                duninvoked = False
                bothuninvoked = False
                if a_die.get("invokeable",False) and not a_die.get("invoked",False):
                    auninvoked = True
                    log.append(
                        f"{attacker}'s {symbol['invokeable_'+a_die.get('type','none')]} Invokeable {a_die.get('type','none')} {symbol['invokeable_'+a_die.get('type','none')]} is Uninvoked and does nothing"
                    )
                    
                if d_die.get("invokeable",False) and not d_die.get("invoked",False):
                    duninvoked = True
                    if auninvoked:
                        auninvoked = False
                        duninvoked = False
                        bothuninvoked = True
                    log.append(
                        f"{defender}'s {symbol['invokeable_'+d_die.get('type','none')]} Invokeable {d_die.get('type','none')} {symbol['invokeable_'+d_die.get('type','none')]} is Uninvoked and does nothing"
                    )
                if auninvoked:
                    d_dice.insert(0,d_die)
                    continue
                if duninvoked:
                    a_dice.insert(0,a_die)
                    continue
                if bothuninvoked:
                    continue

                if a.get("is_staggered"):
                    a_base = 0
                else:
                    min_val = a_die["min"]
                    max_val = a_die["max"]
                    a_base = min_val if min_val > max_val else get_rigged_roll(a, min_val, max_val)

                if d.get("is_staggered"):
                    d_base = 0
                else:
                    min_val = d_die["min"]
                    max_val = d_die["max"]
                    d_base = min_val if min_val > max_val else get_rigged_roll(d, min_val, max_val)

                
                a_roll_val = [a_base]
                d_roll_val = [d_base]
                a_die.setdefault("used_triggers", [])
                d_die.setdefault("used_triggers", [])
                
                process_effects(a, d, a_die, "on_roll", a_roll_val,source_page=a_page, log=log,pageusetype=pageusetype)
                process_effects(d, a, d_die, "on_roll", d_roll_val,source_page=d_page, log=log,pageusetype=pageusetype)
                a_roll = max(0, a_roll_val[0])
                d_roll = max(0, d_roll_val[0] + get_sp_bonus(d.get("sp", 0)))
                if a_die.get("type") not in ["evade"]:
                    a_roll + get_sp_bonus(a.get("sp", 0))
                else:
                    a_roll + get_speed_bonus(a,d)
                if d_die.get("type") not in ["evade"]:
                    d_roll + get_sp_bonus(d.get("sp", 0))
                else:
                    d_roll + get_speed_bonus(d,a)

                a_wins = a_roll > d_roll or (a_roll == d_roll and a_die.get("type") == "evade")
                d_wins = d_roll > a_roll or (d_roll == a_roll and d_die.get("type") == "evade")
                
                if a_wins and not d_wins:
                    
                    a_die.setdefault("used_triggers", [])
                    d_die.setdefault("used_triggers", [])
                    
                    if not a_die.get("type") in ["evade"]:
                        log.append(f"{attacker} won the clash against {defender} (Roll: {symbol[a_die.get('type','none')]}{a_roll} against {symbol[d_die.get('type','none')]}{d_roll})")
                        process_effects(a, d, a_die, "clash_win", [a_base],source_page=a_page, log=log,pageusetype=pageusetype)
                        process_effects(d, a, d_die, "clash_lose", [d_base],source_page=d_page, log=log,pageusetype=pageusetype)
                        a["sp"] += 5
                        a["light"] = min(a.get("light", 0) + 1, a.get("max_light", 3)) 
                        d["sp"] -= 5
                        a["sp"] = max(-45, min(45, a["sp"]))
                        d["sp"] = max(-45, min(45, d["sp"]))
                
                    dmg = 0 if a_die.get("type") in ["evade", "guard"] else a_roll
                    if d_die == "guard":
                        dmg = max(0, a_roll - d_roll)
                    stagger = 0 if a_die.get("type") == "evade" else a_roll
                    a_die.setdefault("used_triggers", [])
                    attackweight = a_page.get("attackweight", 1) 
                    indiscriminate = a_page.get("indiscriminate", False)
                    attacker_faction = "Enemy" if "Enemy" in a.get("faction", []) else "Player"
                    main_target = d
                    extra_targets = get_extra_targets(main_target, profiles, attacker_faction, attackweight, indiscriminate)
                    for hit_target in [main_target] + extra_targets:
                        dmg = calculate_damage(dmg, hit_target, a_die)
                        stagger = calculate_damage(stagger, hit_target, a_die, stagger=True)
                        dmgcont = [dmg]
                        staggercont = [stagger]
                        process_effects(a, hit_target, a_die, "before_on_hit", [a_base],source_page=a_page, damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                        process_effects(hit_target, a, a_die, "before_when_hit", [a_base], damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                        dmg = dmgcont[0]
                        stagger = staggercont[0]
                        hit_target["hp"] -= dmg
                        hit_target["stagger"] -= stagger
                        log.append(f"{attacker} hits {hit_target['name']} for {symbol[a_die.get('type','none')]}{dmg} HP and {symbol[a_die.get('type','none')]}{stagger} Stagger using {symbol[a_die.get('type','none')]}{a_die.get('type','none')} (Roll: {symbol[a_die.get('type','none')]}{a_roll}, {symbol[d_die.get('type','none')]}{d_roll})")
                        applystatus(a, hit_target, a_die, [a_base], [dmg], [stagger],a_page,log=log,pageusetype=pageusetype)
                        dmgcont = [dmg]
                        staggercont = [stagger]
                        process_effects(a, hit_target, a_die, "on_hit", [a_base],source_page=a_page, damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                        process_effects(hit_target, a, a_die, "when_hit", [a_base], damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                    if a_die.get("type") == "evade":
                        a_die.setdefault("used_triggers", [])
                        process_effects(a, d, a_die, "on_evade", [a_base],source_page=a_page, log=log,pageusetype=pageusetype)
                        a_evade_queue.insert(0, a_die)

                elif d_wins:
                    a_die.setdefault("used_triggers", [])
                    d_die.setdefault("used_triggers", [])
                    if not d_die.get("type") in ["evade"]:
                        log.append(f"{attacker} won the clash against {defender} (Roll: {symbol[a_die.get('type','none')]}{a_roll} against {symbol[d_die.get('type','none')]}{d_roll})")
                        process_effects(a, d, a_die, "clash_lose", [a_base],source_page=a_page, log=log,pageusetype=pageusetype)
                        process_effects(d, a, d_die, "clash_win", [d_base],source_page=d_page, log=log,pageusetype=pageusetype)
                        d["sp"] += 5
                        d["light"] = min(d.get("light", 0) + 1, d.get("max_light", 3)) 
                        a["sp"] -= 5
                        a["sp"] = max(-45, min(45, a["sp"]))
                        d["sp"] = max(-45, min(45, d["sp"]))
                    
                    dmg = 0 if d_die.get("type") in ["evade", "guard"] else d_roll
                    if a_die.get("type") == "guard":
                        dmg = max(0, d_roll - a_roll)
                    stagger = 0 if d_die.get("type") == "evade" else d_roll
                    d_die.setdefault("used_triggers", [])
                    attackweight = d_page.get("attackweight", 1)
                    indiscriminate = d_page.get("indiscriminate", False)
                    attacker_faction = "Enemy" if "Enemy" in d.get("faction", []) else "Player"
                    main_target = a
                    
                    extra_targets = get_extra_targets(main_target, profiles, attacker_faction, attackweight, indiscriminate)
                    for hit_target in [main_target] + extra_targets:
                        dmg = calculate_damage(dmg, hit_target, d_die)
                        stagger = calculate_damage(stagger, hit_target, d_die, stagger=True)
                        dmgcont = [dmg]
                        staggercont = [stagger]
                        process_effects(d, hit_target, d_die, "before_on_hit", [d_base],source_page=d_page, damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                        process_effects(hit_target, d, d_die, "before_when_hit", [d_base], damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                        dmg = dmgcont[0]
                        stagger = staggercont[0]
                        hit_target["hp"] -= dmg
                        hit_target["stagger"] -= stagger
                        log.append(f"{defender} hits {hit_target['name']} for {symbol[d_die.get('type','none')]}{dmg} HP and {symbol[d_die.get('type','none')]}{stagger} Stagger using {symbol[d_die.get('type','none')]}{d_die.get('type','none')} (Roll: {symbol[d_die.get('type','none')]}{d_roll}, {symbol[a_die.get('type','none')]}{a_roll})")
                        applystatus(d, hit_target, d_die, [d_base], [dmg], [stagger],d_page,log=log,pageusetype=pageusetype)
                        dmgcont = [dmg]
                        staggercont = [stagger]
                        process_effects(d, hit_target, d_die, "on_hit", [d_base],source_page=d_page, damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                        process_effects(hit_target, d, d_die, "when_hit", [d_base], damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)

                    if d_die.get("type") == "evade":
                        d_die.setdefault("used_triggers", [])
                        process_effects(d, a, d_die, "on_evade", [d_base],source_page=d_page)
                        d_evade_queue.insert(0, d_die)

                else:
                    
                    a_die.setdefault("used_triggers", [])
                    d_die.setdefault("used_triggers", [])
                    log.append(f"{attacker}'s {symbol[a_die.get('type','none')]}{a_die.get('type','none')} ({symbol[a_die.get('type','none')]}{a_roll}) ties with {defender}'s {symbol[d_die.get('type','none')]}{d_die.get('type','none')} ({symbol[d_die.get('type','none')]}{d_roll}) → No effect.")
                    process_effects(a, d, a_die, "clash_tie", [a_base],source_page=a_page, log=log,pageusetype=pageusetype)
                    process_effects(d, a, d_die, "clash_tie", [d_base],source_page=d_page, log=log,pageusetype=pageusetype)
                    
            elif a_die:
                if a_die.get("invokeable",False) and not a_die.get("invoked",False):
                    log.append(
                        f"{attacker}'s {symbol['invokeable_'+a_die.get('type','none')]} Invokeable {a_die.get('type','none')} {symbol['invokeable_'+a_die.get('type','none')]} is Uninvoked and does nothing"
                    )                    
                    continue
                if a.get("is_staggered"):
                    a_base = 0
                else:
                    min_val = a_die["min"]
                    max_val = a_die["max"]
                    a_base = min_val if min_val > max_val else get_rigged_roll(a, min_val, max_val)
                
                roll_val = [a_base]
                a_die.setdefault("used_triggers", [])
                process_effects(a, d, a_die, "on_roll", roll_val,source_page=a_page, log=log,pageusetype=pageusetype)
                roll = max(0, roll_val[0] + get_sp_bonus(a.get("sp", 0)))

                if a_die.get("type") in ["evade", "guard"]:
                    log.append(f"{attacker}'s {symbol[a_die.get('type','none')]}{a_die.get('type','none')} is defensive and does nothing unopposed.")
                    continue
                a_die.setdefault("used_triggers", [])
                attackweight = a_page.get("attackweight", 1)
                indiscriminate = a_page.get("indiscriminate", False)
                attacker_faction = "Enemy" if "Enemy" in a.get("faction", []) else "Player"
                main_target = d
                
                extra_targets = get_extra_targets(main_target, profiles, attacker_faction, attackweight, indiscriminate)
                for hit_target in [main_target] + extra_targets:
                    dmg = calculate_damage(roll, hit_target, a_die)
                    stagger = calculate_damage(roll, hit_target, a_die, stagger=True)
                    dmgcont = [dmg]
                    staggercont = [stagger]
                    process_effects(a, hit_target, a_die, "before_on_hit", [a_base],source_page=a_page, damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                    process_effects(hit_target, a, a_die, "before_when_hit", [a_base], damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                    dmg = dmgcont[0]
                    stagger = staggercont[0]
                    hit_target["hp"] -= dmg
                    hit_target["stagger"] -= stagger
                    log.append(f"{attacker} hits {hit_target['name']} for {symbol[a_die.get('type','none')]}{dmg} HP and {symbol[a_die.get('type','none')]}{stagger} Stagger using {symbol[a_die.get('type','none')]}{a_die.get('type','none')} (Roll: {symbol[a_die.get('type','none')]}{roll})")
                    applystatus(a, hit_target, a_die, [a_base], [dmg], [stagger],a_page,log=log,pageusetype=pageusetype)
                    dmgcont = [dmg]
                    staggercont = [stagger]
                    process_effects(a, hit_target, a_die, "on_hit", [a_base],source_page=a_page, damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                    process_effects(hit_target, a, a_die, "when_hit", [a_base], damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                
            elif d_die:
                if d_die.get("invokeable",False) and not d_die.get("invoked",False):
                    log.append(
                        f"{defender}'s {symbol['invokeable_'+d_die.get('type','none')]} Invokeable {d_die.get('type','none')} {symbol['invokeable_'+d_die.get('type','none')]} is Uninvoked and does nothing"
                    )                    
                    continue
                if d.get("is_staggered"):
                    d_base = 0
                else:
                    min_val = d_die["min"]
                    max_val = d_die["max"]
                    d_base = min_val if min_val > max_val else get_rigged_roll(d, min_val, max_val)



                
                roll_val = [d_base]
                d_die.setdefault("used_triggers", [])
                process_effects(d, a, d_die, "on_roll", roll_val,source_page=d_page, log=log,pageusetype=pageusetype)
                roll = max(0, roll_val[0] + get_sp_bonus(a.get("sp", 0)))

                if d_die.get("type") in ["evade", "guard"]:
                    log.append(f"{defender}'s {symbol[d_die.get('type','none')]}{d_die.get('type','none')} is defensive and does nothing unopposed.")
                    continue
                d_die.setdefault("used_triggers", [])
                attackweight = d_page.get("attackweight", 1)
                indiscriminate = d_page.get("indiscriminate", False)
                attacker_faction = "Enemy" if "Enemy" in d.get("faction", []) else "Player"
                main_target = a 

                extra_targets = get_extra_targets(main_target, profiles, attacker_faction, attackweight, indiscriminate)
                for hit_target in [main_target] + extra_targets:
                    dmg = calculate_damage(roll, hit_target, d_die)
                    stagger = calculate_damage(roll, hit_target, d_die, stagger=True)
                    dmgcont = [dmg]
                    staggercont = [stagger]
                    process_effects(d, hit_target, d_die, "before_on_hit", [d_base],source_page=d_page, damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                    process_effects(hit_target, d, d_die, "before_when_hit", [d_base], damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                    dmg = dmgcont[0]
                    stagger = staggercont[0]
                    hit_target["hp"] -= dmg
                    hit_target["stagger"] -= stagger
                    log.append(f"{defender} hits {hit_target['name']} for {symbol[d_die.get('type','none')]}{dmg} HP and {symbol[d_die.get('type','none')]}{stagger} Stagger using {symbol[d_die.get('type','none')]}{d_die.get('type','none')} (Roll: {symbol[d_die.get('type','none')]}{roll})")
                    applystatus(d, hit_target, d_die, [d_base], [dmg], [stagger],d_page,log=log,pageusetype=pageusetype)
                    dmgcont = [dmg]
                    staggercont = [stagger]
                    process_effects(d, hit_target, d_die, "on_hit", [d_base],source_page=d_page, damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                    process_effects(hit_target, d, d_die, "when_hit", [d_base], damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)

        
        process_effects(a, d, None, "after_attack", source_page=a_page, log=log,pageusetype=pageusetype)
        process_effects(d, a, None, "after_attack", source_page=d_page, log=log,pageusetype=pageusetype)
        resetinvokeables(a_page)
        resetinvokeables(d_page)

        a["hand"].remove(attacker_page)
        d["hand"].remove(defender_page)
        update_profiles({p['name']: p for p in [a, d] + extra_targets})
        save_json(PAGE_PATH,pages)
        embed = discord.Embed(
            title=f"⚔️ {attacker} clashes with {defender}!",
            description=f"{attacker} uses {attacker_page} | {defender} uses {defender_page}",
            color=discord.Color.orange()
        )
        for entry in log:
            if len(entry) > 1024:
                entry = entry[:1021] + "..."
            embed.add_field(name="•", value=entry, inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    cog = ClashCog(bot)
    await bot.add_cog(cog)