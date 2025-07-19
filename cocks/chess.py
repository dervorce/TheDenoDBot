# pyright: reportMissingImports=false
import json
import discord
from discord.ext import commands
from discord import app_commands
from everythingexcepthim import (load_json, autocomplete_profile_names)
from THECORE import (PASSIVE_PATH , INV_PATH, PROFILE_PATH, BUFF_PATH,symbol )
class ChessCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @app_commands.command(name="deckcheck")
    @app_commands.autocomplete(
        name=autocomplete_profile_names
    )
    @app_commands.describe(name="Character name")
    async def deckcheck(self,interaction: discord.Interaction, name: str):
        profiles = load_json(PROFILE_PATH)
        profile = profiles.get(name)

        if not profile:
            await interaction.response.send_message("Profile not found.")
            return

        deck = profile.get("deck", [])
        hand = profile.get("hand", [])
        light = profile.get("light", 0)
        max_light = profile.get("max_light", 3)

        embed = discord.Embed(
            title=f"🃏 Deck Check: {name}",
            color=discord.Color.gold()
        )

        embed.add_field(
            name=f"{symbol['light']} Light {symbol['light']}",
            value=f"{light}/{max_light}",
            inline=False
        )
        embed.add_field(
            name=f"{symbol['sanity']} Sanity {symbol['sanity']}",
            value=f"{profile.get('sp', 0)}",
            inline=False
        )
        embed.add_field(
            name="📥 Hand",
            value=", ".join(f"`{card}`" for card in hand) if hand else "*Empty hand*",
            inline=False
        )

        embed.add_field(
            name="📦 Deck",
            value=", ".join(f"`{card}`" for card in deck) if deck else "*Empty deck*",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="inventorycheck")
    @app_commands.autocomplete(
        name=autocomplete_profile_names
    )
    @app_commands.describe(name="Character name")
    async def inventorycheck(self,interaction: discord.Interaction, name: str):
        profiles = load_json(PROFILE_PATH)
        inventory = load_json(INV_PATH)
        profile = profiles.get(name)
        p_inv = inventory.get(name)

        if not profile:
            await interaction.response.send_message("Profile not found.")
            return
        if not p_inv:
            await interaction.response.send_message("Profile has no Inventory")
            return

        deck = profile.get("deck", [])
        equipped = p_inv.get("equipped", [])
        pages = p_inv.get("pages", [])
        ahn = p_inv.get("ahn", 0)

        embed = discord.Embed(
            title=f"🃏 Inventory Check: {name}",
            color=discord.Color.gold()
        )

        embed.add_field(
            name=f"{symbol['light']} Ahn {symbol['light']}",
            value=f"{name} has {ahn} Ahn",
            inline=False
        )
        embed.add_field(
            name="📥 Unequipped Pages",
            value=", ".join(f"`{card}`" for card in pages) if pages else "*Empty*",
            inline=False
        )
        embed.add_field(
                    name="📥 Equipped Pages",
                    value=", ".join(f"`{card}`" for card in equipped) if equipped else "*Empty*",
                    inline=False
                )

        embed.add_field(
            name="📦 Deck",
            value=", ".join(f"`{card}`" for card in deck) if deck else "*Empty deck*",
            inline=False
        )

        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="profilecheck")
    @app_commands.autocomplete(
        name=autocomplete_profile_names
    )
    @app_commands.describe(name="Character name")
    async def profilecheck(self,interaction: discord.Interaction, name: str):
        profiles = load_json(PROFILE_PATH)
        buffsreal = load_json(BUFF_PATH)
        profile = profiles.get(name)
        if not profile:
            await interaction.response.send_message("Profile not found.")
            return
        def fmt(d): return json.dumps(d, indent=2) if isinstance(d, dict) else str(d)
        embed = discord.Embed(
            title=f"📜 Profile of {name}",
            color=discord.Color.green()
        )

        embed.add_field(
            name="🧍 Vital Stats",
            value=(
                f"**HP**: {symbol['buff']}{profile.get('hp')}/{profile.get('max_hp')}\n"
                f"**Stagger**: {symbol['stagger']}{profile.get('stagger')}/{profile.get('max_stagger')} "
                f"({symbol['stagger']} Staggered: {'Yes' if profile.get('is_staggered', False) else 'No'})\n"
                f"**SP**: {symbol['sanity']}{profile.get('sp')}\n"
                f"**Light**: {symbol['light']}{profile.get('light')}/{profile.get('max_light')}\n"
                f"**Speed**: {symbol['buff']}{profile.get('speed')}"
            ),
            inline=False
        )

        embed.add_field(
            name="🛡️ Resistances",
            value=(
                f"**General**: `{json.dumps(profile.get('resistances'), indent=0)}`\n"
                f"**Stagger**: `{json.dumps(profile.get('stagger_resistances'), indent=0)}`\n"
                f"**Sin**: `{json.dumps(profile.get('sin_resistances'), indent=0)}`"
            ),
            inline=False
        )

        buffs = profile.get("buffs", {})
        buffs_fmt = ", ".join(
            [
                f"`{k} x{v.get('stacks', 1)} stacks{', x' + str(v.get('count')) + ' Count' if buffsreal[k].get('countable', False) else ''}`"
                for k, v in buffs.items()
            ]
        ) if buffs else "*None*"

        embed.add_field(
            name=f"{symbol['buff']} Buffs",
            value=buffs_fmt,
            inline=False
        )

        passives = profile.get("passives", [])
        embed.add_field(
            name=f"{symbol['sanity']} Passives",
            value=", ".join(f"`{p}`" for p in passives) if passives else "*None*",
            inline=False
        )

        embed.add_field(
            name="📘 Deck / 🤲 Hand",
            value=(
                f"**Deck**: {', '.join(f'`{card}`' for card in profile.get('deck', [])) or '*None*'}\n"
                f"**Hand**: {', '.join(f'`{card}`' for card in profile.get('hand', [])) or '*None*'}"
            ),
            inline=False
        )
        factions = profile.get("faction", [])
        faction_text = ", ".join(f"`{f}`" for f in factions) if factions else "*None*"
        embed.add_field(name="🎭 Factions", value=faction_text, inline=False)

        embed.set_footer(text=f"🟢 {'Active' if profile.get('is_active') else 'Inactive'}")

        await interaction.response.send_message(embed=embed)

    
    @app_commands.command(name="passivecheck")
    @app_commands.autocomplete(
        name=autocomplete_profile_names
    )
    @app_commands.describe(name="Character name")
    async def passivecheck(self,interaction: discord.Interaction, name: str):
        profiles = load_json(PROFILE_PATH)
        passives = load_json(PASSIVE_PATH)
        profile = profiles.get(name)

        if not profile:
            await interaction.response.send_message("Profile not found.")
            return

        passive_list = profile.get("passives", [])
        if not passive_list:
            await interaction.response.send_message(f"{name} has no passives.")
            return

        embed = discord.Embed(
            title=f"{symbol['sanity']} Passive Check: {name} {symbol['sanity']}",
            description="Known passives and their effects.",
            color=discord.Color.blue()
        )

        for passive_name in passive_list:
            data = passives.get(passive_name, {})

            if not data.get("hidden", False):
                desc = data.get("description", "*No description provided.*")
            else:
                desc = "You can not view this passive Yet"

            if data.get("hidden", False):
                name = "Hidden"
            else:
                name = passive_name
            embed.add_field(
                name=f"📘 {name}",
                value=desc,
                inline=False
            )

        await interaction.response.send_message(embed=embed)
async def setup(bot):
    cog = ChessCog(bot)
    await bot.add_cog(cog)

