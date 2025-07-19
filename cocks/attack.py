# pyright: reportMissingImports=false
import copy
import discord
from discord.ext import commands
from discord import app_commands
from him import process_effects
from everythingexcepthim import (load_json , update_profiles ,get_rigged_roll,resetinvokeables,save_json , get_sp_bonus ,resource ,calculate_damage ,autocomplete_page_names ,autocomplete_profile_names ,get_extra_targets ,applystatus)
from THECORE import (PAGE_PATH ,PROFILE_PATH, symbol)
class AttackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #@app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="attack")
    @app_commands.describe(attacker="Attacker name", target="Target name", page="Page to use")
    @app_commands.autocomplete(
        page=autocomplete_page_names,
        target=autocomplete_profile_names,
        attacker=autocomplete_profile_names
    )

    async def attack(self, interaction: discord.Interaction, attacker: str, target: str, page: str):

        profiles = load_json(PROFILE_PATH)
        pages = load_json(PAGE_PATH)
        a = profiles.get(attacker)
        t = profiles.get(target)
        atk_page = pages.get(page)
        pageusetype = "Attack"
        if not all([a, t, atk_page]):
            await interaction.response.send_message("Invalid input.")
            return
        if page not in a.get("hand", []) or a.get("light", 0) < atk_page.get("light_cost", 1):
            await interaction.response.send_message("Page not usable or insufficient light.")
            return

        log = []
        process_effects(a, t, None, "on_use", source_page=atk_page, log=log,pageusetype=pageusetype)
        resource(a,atk_page)
        dice_copy = copy.deepcopy(atk_page["dice"])

        for dice in dice_copy:
            if dice.get("invokeable",False) and not dice.get("invoked",False):
                log.append(
                    f"{attacker}'s {symbol['invokeable_'+dice.get('type','none')]} Invokeable {dice.get('type','none')} {symbol['invokeable_'+dice.get('type','none')]} is Uninvoked and does nothing"
                )                
                continue
            if a.get("is_staggered"):
                base_roll = 0
                roll = 0
            else:
                min_val = dice["min"]
                max_val = dice["max"]

                base_roll = min_val if min_val > max_val else get_rigged_roll(a, min_val, max_val)

                roll_val = [base_roll]
                dice.setdefault("used_triggers", [])
                process_effects(a, t, dice, "on_roll", roll_val, log=log,pageusetype=pageusetype)
                roll = max(0, roll_val[0] + get_sp_bonus(a.get("sp", 0)))

            evade_queue = t.get("evade_queue", [])
            if evade_queue:
                evade = evade_queue[0]
                if t.get("is_staggered"):
                    evade_base = 0
                else:
                    min_val = evade["min"]
                    max_val = evade["max"]
                    base_roll = min_val if min_val > max_val else get_rigged_roll(a, min_val, max_val)
                evade_roll_val = [evade_base]
                evade.setdefault("used_triggers", [])
                process_effects(t, a, evade, "on_roll", evade_roll_val, log=log,pageusetype=pageusetype)
                evade_roll = max(0, evade_roll_val[0] + get_sp_bonus(a.get("sp", 0)))



                if evade_roll >= roll:
                    evade.setdefault("used_triggers", [])
                    log.append(f"{target}'s {symbol['evade']}evade ({symbol['evade']}{evade_roll}) dodges {attacker}'s {symbol[dice.get('type','none')]}{dice.get('type','none')} ({symbol[dice.get('type','none')]}{roll}) → +3 stagger recovery")
                    process_effects(t, a, evade, "on_evade", log=log,pageusetype=pageusetype)
                    t["stagger"] += 3
                
                    continue
                else:
                    t["evade_queue"] = t.get("evade_queue", [])[1:]

            if dice.get("type") in ["evade", "guard"]:
                log.append(f"{attacker}'s {symbol[dice.get('type','none')]}{dice.get('type','none')} is defensive and does nothing unopposed.")
                continue

            dice.setdefault("used_triggers", [])

            attackweight = atk_page.get("attackweight", 1)
            indiscriminate = atk_page.get("indiscriminate", False)
            attacker_faction = "Enemy" if "Enemy" in a.get("faction", []) else "Player"


            all_targets = [t] + get_extra_targets(t, profiles, attacker_faction, attackweight, indiscriminate)

            for hit_target in all_targets:
                dmg = calculate_damage(roll, hit_target, dice)
                stagger = calculate_damage(roll, hit_target, dice, stagger=True)
                dmgcont = [dmg]
                staggercont = [stagger]
                process_effects(a, hit_target, dice, "before_on_hit", [base_roll], damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                process_effects(hit_target, a, dice, "before_when_hit", [base_roll], damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                dmg = dmgcont[0]
                stagger = staggercont[0]
                hit_target["hp"] -= dmg
                hit_target["stagger"] -= stagger
                log.append(f"{attacker} hits {hit_target['name']} for {symbol[dice.get('type','none')]}{dmg} HP and {symbol[dice.get('type','none')]}{stagger} Stagger using {symbol[dice.get('type','none')]}{dice.get('type','none')} (Roll: {symbol[dice.get('type','none')]}{roll}, OG Roll: {symbol[dice.get('type','none')]}{base_roll}).")
                applystatus(a, hit_target, dice, [base_roll], dmgcont, staggercont,atk_page,log=log,pageusetype=pageusetype)
                dmgcont = [dmg]
                staggercont = [stagger]
                process_effects(a, hit_target, dice, "on_hit", [base_roll], damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)
                process_effects(hit_target, a, dice, "when_hit", [base_roll], damage=dmgcont, stagger=staggercont, log=log,pageusetype=pageusetype)

        a["light"] -= atk_page.get("light_cost", 1)
        process_effects(a, t, None, "after_attack", source_page=atk_page, log=log,pageusetype=pageusetype)
        resetinvokeables(atk_page)
        save_json(PAGE_PATH,pages)
        a["hand"].remove(page)
        update_profiles({p['name']: p for p in all_targets + [a]})
        embed = discord.Embed(
            title=f"⚔️ {attacker} attacks {target} using {page}!",
            description="Combat breakdown:",
            color=discord.Color.red()
        )
        for entry in log:
            if len(entry) > 1024:
                entry = entry[:1021] + "..."
            embed.add_field(name="•", value=entry, inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    cog = AttackCog(bot)
    await bot.add_cog(cog)
