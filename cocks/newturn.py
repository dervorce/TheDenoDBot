# pyright: reportMissingImports=false
import random
import discord
from discord.ext import commands
from discord import app_commands
from everythingexcepthim import (load_json ,
    save_json ,
    update_profiles ,
    autocomplete_page_names ,
    autocomplete_profile_names)
from him import process_effects
from THECORE import (PAGE_PATH ,   PROFILE_PATH ,  RES_PATH,symbol )
class NewTurnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #@app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="newturn")
    async def newturn(self,interaction: discord.Interaction):
        profiles = load_json(PROFILE_PATH)
        pages = load_json(PAGE_PATH)
        turn_log = {}
        log = []
        for name, profile in profiles.items():
            profile["name"] = name
            if not profile.get("is_active", True):
                profile["hp"] = profile.get("max_hp", 0)
                profile["stagger"] = profile.get("max_stagger", 0)
                profile["sp"] = 0
                profile["light"] = profile.get("max_light")
                profile["is_staggered"] = False
                profile["hand"] = []
                profile["nextturn"]["light"] = 0
                profile["buffs"] = {}
                profile["resistances"] = profile["original_resistances"]
                profile["sin_resistances"] = profile["original_sin_resistances"]
            else:
                profile["_effect_limits"] = {}
                profile["speed"] = random.randint(profile.get("speed_min", 1), profile.get("speed_max", 10))
                gain = profile.get("light_gain", 1)
                gain += profile["nextturn"]["light"]
                profile["nextturn"]["light"] = 0
                if "buffs" in profile:
                    profile["buffs"] = {k: v for k, v in profile["buffs"].items() if isinstance(v, dict) and not v.get("volatile", False)}
                if "buffs" in profile["nextturn"]:
                    for buff_name, buff_data in profile["nextturn"]["buffs"].items():
                        existing = profile.setdefault("buffs", {}).get(buff_name)
                        if existing:
                            existing["stacks"] = existing.get("stacks", 0) + buff_data.get("stacks", 0)
                            if existing.get("countable",False):
                                existing["count"] = existing.get("count", 0) + buff_data.get("count", 0)
                            existing["volatile"] = existing.get("volatile", False) or buff_data.get("volatile", False)
                        else:
                            profile.setdefault("buffs", {})[buff_name] = buff_data
                    profile["nextturn"]["buffs"] = {}
                process_effects(profile, None, None, "newturn", log=log,pageusetype="newturn")
                log_drawn = []
                if profile.get("deck"):
                    draw_count = profile.get("pages_drawn", 1)
                    deck_counts = {}
                    for page in profile["deck"]:
                        deck_counts[page] = deck_counts.get(page, 0) + 1

                    log_drawn = []
                    for _ in range(draw_count):
                        hand_counts = {}
                        for page in profile.get("hand", []):
                            hand_counts[page] = hand_counts.get(page, 0) + 1
                        eligible_pages = [
                            page for page, max_count in deck_counts.items()
                            if hand_counts.get(page, 0) < max_count
                        ]

                        if not eligible_pages:
                            break

                        drawn = random.choice(eligible_pages)
                        profile.setdefault("hand", []).append(drawn)
                        hand_counts[drawn] = hand_counts.get(drawn, 0) + 1
                        log_drawn.append(drawn)
            


                profile["light"] = min(profile.get("light", 0) + gain, profile.get("max_light", 3))
                turn_log.setdefault(name, {
                    "gain": gain,
                    "speed": profile["speed"],
                    "draws": []
                })
                turn_log[name]["draws"].append(log_drawn)

            if profile.get("is_staggered"):
                profile["is_staggered"] = False
                profile["stagger"] = profile.get("max_stagger", 0)
                if "original_resistances" in profile:
                    profile["resistances"] = profile["original_resistances"]
                if "original_sin_resistances" in profile:
                    profile["sin_resistances"] = profile["original_sin_resistances"]
            
            profile["evade_queue"] = []
            update_profiles({name: profile})
        save_json(PAGE_PATH,pages)
        embed = discord.Embed(
        title="🎲 New Turn Begins!",
        description="LETS GO GAMBLING!",
        color=discord.Color.blurple()
        )

        for name, entry in turn_log.items():
            gain = entry["gain"]
            speed = entry["speed"]
            draws = ", ".join(f"*{card}*" for card in entry["draws"]) if entry["draws"] else "*No cards drawn*"

            value = f"{symbol['light']} Gains {gain} Light | 🎯 Speed: **{speed}**\n➕ Draws: {draws}"
            embed.add_field(name=f"🧍 {name}", value=value, inline=False)
        if log:
            embed.add_field(name=f"{symbol['buff']} Effects Log", value="\n".join(log), inline=False)
        await interaction.response.send_message(embed=embed)
    #@app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="combatstart")
    @app_commands.autocomplete(
        profile=autocomplete_profile_names,page=autocomplete_page_names
    )
    @app_commands.describe(profile = "Profile that used the page",page="page name to trigger combat_start from")
    async def combatstart(self,interaction: discord.Interaction,profile: str, page: str):
        pages = load_json(PAGE_PATH)
        profiles = load_json(PROFILE_PATH)
        log = []
        page = pages[page]
        profile = profiles[profile]
        process_effects(profile, None, None, "combat_start", source_page=page, log=log,pageusetype="CombatStart")
        save_json(PROFILE_PATH,profiles)
        save_json(PAGE_PATH,pages)

        await interaction.response.send_message(file=discord.File("whydoiexist.png"))

    
    #@app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="reset")
    async def reset(self,interaction: discord.Interaction):
        profiles = load_json(PROFILE_PATH)
        resources = load_json(RES_PATH)

        for name, profile in profiles.items():
            profile["hp"] = profile.get("max_hp", 0)
            profile["stagger"] = profile.get("max_stagger", 0)
            profile["sp"] = 0
            profile["light"] = profile.get("max_light", 0)
            profile["is_staggered"] = False
            profile["hand"] = []
            profile["nextturn"] = {"light": 0}
            profile["buffs"] = {}
            profile["resistances"] = profile.get("original_resistances", {})
            profile["sin_resistances"] = profile.get("original_sin_resistances", {})
            profile["is_active"] = False

        for faction, sins in resources.items():
            for sin_name in sins:
                sins[sin_name] = 0
        save_json(PROFILE_PATH,profiles)
        save_json(RES_PATH,resources)
        await interaction.response.send_message("Dantehhh, rewind it back dantehhhhhhh", ephemeral=False)
    #@app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="enable")
    async def enable(self,interaction: discord.Interaction, profile: str):
        profiles = load_json(PROFILE_PATH)
        if profile in profiles:
            profiles[profile]["is_active"] = True
        else:
            await interaction.response.send_message(f"{profile} doesn't exist", ephemeral=False)
            return
        save_json(PROFILE_PATH,profiles)
        await interaction.response.send_message(f"{profile} has been enabled", ephemeral=False)

async def setup(bot):
    cog = NewTurnCog(bot)
    await bot.add_cog(cog)

