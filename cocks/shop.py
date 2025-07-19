# pyright: reportMissingImports=false
import copy
import discord
import time
import random
from discord.ext import commands
from discord import app_commands
from him import process_effects
from everythingexcepthim import (load_json , save_json ,pagepricegetter )
from THECORE import (PAGE_PATH ,PROFILE_PATH, INV_PATH, SHOP_PATH,symbol)
class ShopCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sell")
    @app_commands.describe(owner="name",page="Page to sell")
    async def sell(self, interaction: discord.Interaction, owner: str, page: str):
        if page in ["Focused Strikes", "Charge and Cover", "Light Attack", "Light Defense", "Evade"]:
            await interaction.response.send_message(f"❌ Nuh Uh.")
            return
        shop = load_json(SHOP_PATH)
        inventory = load_json(INV_PATH)
        sold_page = shop.get(page)
        if page not in shop or page == "SHOP":
            await interaction.response.send_message(f"❌ That page doesn't exist.")
            return
        sellcost = pagepricegetter(sold_page.get("tier","Paperback")) / 2
        if owner not in inventory:
            await interaction.response.send_message(f"❌ That profile doesn't exist.")
            return
        if page not in inventory[owner]["pages"]:
            await interaction.response.send_message(f"❌ The profile does not own the page.")
            return
        if interaction.user.id != inventory[owner]["owner_id"] and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ That's not your profile.")
            return

        inventory[owner]["ahn"] += sellcost
        inventory[owner]["pages"].remove(page)
        save_json(INV_PATH,inventory)
        embed = discord.Embed(
            title=f"{owner} has sold {page} for {sellcost} Ahn",
            description=" ",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed)
   
   
    @app_commands.command(name="equip")
    @app_commands.describe(owner="name",page="Page to equip")
    async def equip(self, interaction: discord.Interaction, owner: str, page: str):

        inventory = load_json(INV_PATH)
        pages = load_json(PAGE_PATH) 
        profiles = load_json(PROFILE_PATH)
        if page not in pages or page == "SHOP":
            await interaction.response.send_message(f"❌ That page doesn't exist.")
            return
        if owner not in inventory or owner not in profiles:
            await interaction.response.send_message(f"❌ That profile doesn't exist.")
            return
        if page not in inventory[owner]["pages"] and page not in ["Focused Strikes", "Charge and Cover", "Light Attack", "Light Defense", "Evade"]:
            await interaction.response.send_message(f"❌ The profile does not own the page.")
            return
        if len(profiles[owner]["deck"]) >= 9:
            await interaction.response.send_message(f"❌ The profile's deck is maxxed.")
            return
        if interaction.user.id != inventory[owner]["owner_id"] and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ That's not your profile.")
            return
        if page not in ["Focused Strikes", "Charge and Cover", "Light Attack", "Light Defense", "Evade"]:
            inventory[owner]["pages"].remove(page)
            inventory[owner]["equipped"].append(page)
        profiles[owner]["deck"].append(page)
        save_json(INV_PATH,inventory)
        save_json(PROFILE_PATH,profiles)
        embed = discord.Embed(
            title=f"{owner} has equipped {page}!",
            description=" ",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed)
   
   
    @app_commands.command(name="unequip")
    @app_commands.describe(owner="name",page="Page to eunquip")
    async def unequip(self, interaction: discord.Interaction, owner: str, page: str):

        inventory = load_json(INV_PATH)
        pages = load_json(PAGE_PATH) 
        profiles = load_json(PROFILE_PATH)
        if page not in pages or page == "SHOP":
            await interaction.response.send_message(f"❌ That page doesn't exist.")
            return
        if owner not in inventory or owner not in profiles:
            await interaction.response.send_message(f"❌ That profile doesn't exist.")
            return
        if page not in inventory[owner]["equipped"] and page not in ["Focused Strikes", "Charge and Cover", "Light Attack", "Light Defense", "Evade"]:
            await interaction.response.send_message(f"❌ The profile isn't equipping the page.")
            return
        if interaction.user.id != inventory[owner]["owner_id"] and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ That's not your profile.")
            return
        if page not in ["Focused Strikes", "Charge and Cover", "Light Attack", "Light Defense", "Evade"]:
            inventory[owner]["pages"].append(page)
            inventory[owner]["equipped"].remove(page)
        profiles[owner]["deck"].remove(page)
        save_json(INV_PATH,inventory)
        save_json(PROFILE_PATH,profiles)
        embed = discord.Embed(
            title=f"{owner} has unequipped {page}!",
            description=" ",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed)
   
    @app_commands.command(name="buy")
    @app_commands.describe(owner="name",page="Page to buy")
    async def buy(self, interaction: discord.Interaction, owner: str, page: str):

        shop = load_json(SHOP_PATH)
        inventory = load_json(INV_PATH)
        theshop = shop["SHOP"]
        if page not in shop:
            await interaction.response.send_message(f"❌ That page doesn't exist.")
            return
        if page not in theshop["currentlyselling"]:
            await interaction.response.send_message(f"❌ That page is not being Sold.")
            return
        if owner not in inventory:
            await interaction.response.send_message(f"❌ That profile doesn't exist.")
            return
        buycost = theshop["currentlyselling"][page]
        if buycost > inventory[owner]["ahn"]:
            await interaction.response.send_message(f"❌ Too Expensive.")
            return
        if interaction.user.id != inventory[owner]["owner_id"] and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ That's not your profile.")
            return
        inventory[owner]["ahn"] -= buycost
        inventory[owner]["pages"].append(page)
        save_json(INV_PATH,inventory)
        embed = discord.Embed(
            title=f"{owner} has bought {page} for {buycost} Ahn",
            description=" ",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed)
    
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="refresh")
    async def refresh(self, interaction: discord.Interaction):

        shop = load_json(SHOP_PATH)
        theshop = shop["SHOP"]
        logs = []
        theshop["currentlyselling"] = {}
        cansell = theshop.get("cansell")
        random.shuffle(cansell)
        selling = cansell[:theshop["sellingamount"]]
        for page in selling:
            if page in shop:
                pageprice = pagepricegetter(shop[page].get("tier","Paperback"))
                theshop["currentlyselling"][page] = pageprice
                logs.append(f"{page} is being sold at {pageprice} Ahn!")


        save_json(SHOP_PATH,shop)
        embed = discord.Embed(
            title=f"The shop has been refreshed!",
            description=f"🕒 Refreshed <t:{int(time.time())}:R>",
            color=discord.Color.gold()
        )

        for section in logs:
            embed.add_field(
            name=f"{symbol['light']} New Shop Item: {symbol['light']}",
            value=section,
            inline=False
        )

        await interaction.response.send_message(embed=embed)
    @app_commands.command(name="linkprofile")
    @app_commands.describe(profile_name="Your profile name")
    async def linkprofile(self, interaction: discord.Interaction, profile_name: str):
        inventory = load_json(INV_PATH)

        if profile_name not in inventory:
            await interaction.response.send_message("❌ That profile doesn't exist.")
            return

        profile = inventory[profile_name]

        if "owner_id" in profile and profile["owner_id"] != interaction.user.id:
            await interaction.response.send_message("❌ This profile is already linked to another user.")
            return

        profile["owner_id"] = interaction.user.id
        save_json(INV_PATH, inventory)
        await interaction.response.send_message(f"✅ Profile **{profile_name}** has been linked to you!")
    @app_commands.command(name="unlinkprofile")
    @app_commands.describe(profile_name="Profile to unlink")
    @commands.has_permissions(administrator=True)
    async def unlinkprofile(self, interaction: discord.Interaction, profile_name: str):
        inventory = load_json(INV_PATH)

        if profile_name not in inventory:
            await interaction.response.send_message("❌ That profile doesn't exist.")
            return

        inventory[profile_name].pop("owner_id", None)
        save_json(INV_PATH, inventory)

        await interaction.response.send_message(f"✅ Unlinked **{profile_name}** from its owner.")


async def setup(bot):
    cog = ShopCog(bot)
    await bot.add_cog(cog)
