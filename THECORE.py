# pyright: reportMissingImports=false
import os
import discord
from discord.ext import commands
import asyncio
import ProfileManager

DATA_DIR = "data"
PROFILE_PATH = "data/profiles/profiles.json"
PAGE_PATH = "data/pages"
BUFF_PATH = os.path.join(DATA_DIR, "buffs.json")
PASSIVE_PATH = os.path.join(DATA_DIR, "passives.json")
GIFT_PATH = os.path.join(DATA_DIR, "gifts.json")
RES_PATH = os.path.join(DATA_DIR, "resource.json")
INV_PATH = os.path.join(DATA_DIR,"inventory.json")
SHOP_PATH = os.path.join(DATA_DIR,"shopdata.json")
PASSHOP_PATH = os.path.join(DATA_DIR,"passiveshop.json")
PRESET_PATH = os.path.join(DATA_DIR,"presets.json")
MD_PATH = os.path.join(DATA_DIR,"MD.json")
BOX_PATH = os.path.join(DATA_DIR,"StorageBox.json")
SUPPORT_PATH = os.path.join(DATA_DIR,"support.json")
ACTION_PATH = os.path.join(DATA_DIR,"actionlist.json")

from functools import wraps
megalock = asyncio.Lock()
def lock_command(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with megalock:
            return await func(*args, **kwargs)
    return wrapper

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

ProfileMan = ProfileManager.ProfileManager("data/profiles")  # folder containing .json files
ProfileMan.load_profiles()
ProfileMan.save_profiles("data/profiles/profiles.json")

symbol = {
    "slash": "<:slash:1390618685311422544>",
    "pierce": "<:pierce:1390618708115853382>",
    "blunt": "<:blunt:1390618624523243530>",
    "guard": "<:guard:1390618649621958738>",
    "evade": "<:evade:1390618663349915659>",
    "invokeable_slash": "<:invokeable_slash:1395884468174196766>",
    "invokeable_pierce": "<:invokeable_pierce:1395884548444786709>",
    "invokeable_blunt": "<:invokeable_guard:1395884493977554997>",
    "invokeable_guard": "<:invokeable_guard:1395884530388303973>",
    "invokeable_evade": "<:invokeable_evade:1395884513581727855>",
    "stagger": "<:stagger:1390624005593239643>",
    "buff": "<:buff:1390625150440837130>",
    "light": "<:light:1390625996520030248>",
    "sanity": "<:sanity:1390636680226013204>",
    "Poise": "<:Poise:1392216950184214648>",
    "Charge": "<:Charge:1392216933868240987>",
    "Tremor": "<:Tremor:1392216852037373952>",
    "Rupture": "<:Rupture:1392216911839887461>",
    "Bleed": "<:Bleed:1392216870681055352>",
    "Sinking": "<:Sinking:1392216889731711046>",
    "Burn": "<:Burn:1392216803832238150>",
    "Attack Power Up": "<:AttackPowerUp:1392219124200898793>",
    "Haste": "<:Haste:1392219422378164305>",
    "none": " "
}
__all__ = ["bot", "intents", "tree", "PAGE_PATH", "PASSIVE_PATH", "PROFILE_PATH", "RES_PATH", "BUFF_PATH", "GIFT_PATH","BOX_PATH","MD_PATH", "symbol"]
# maps field name to the source dict

