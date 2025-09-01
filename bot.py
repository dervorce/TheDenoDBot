# pyright: reportMissingImports=false
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import asyncio
import traceback
import io
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from discord import File
from ProfileManager import ProfileManager
from THECORE import (bot, tree, ProfileMan)
import modifierScripts.modifiers as modifiers


async def load_all_extensions():
    for filename in os.listdir("cocks"):
        if filename.endswith(".py") and not filename.startswith("_"):
            ext = f"cocks.{filename[:-3]}"
            try:
                await bot.load_extension(ext)
                print(f"✅ Loaded: {ext}")
            except Exception as e:
                print(f"❌ Failed to load {ext}:\n{e}")


@bot.event
async def on_message(message):
    if message.author.id in [412329858471821314]:
        await message.delete()
        if "cp" in message.content.lower() or ("old lungs" in message.content.lower() and message.author.id in [1375130091725783150]):
            try:
                await message.delete()
                await message.author.send("Im going to touch you")
            except discord.Forbidden:
                print(f"Couldn’t DM {message.author} — probably has DMs closed.")
    # if "ping em john" in message.content.lower():
    #     asyncio.sleep(2)
    #     await message.channel.send("<@766780916580220938> ping em john")
    await bot.process_commands(message)
@bot.event
async def on_ready():
    synced = await tree.sync()
    print(f"✅ Synced {len(synced)} commands.")

    print("\n📋 Slash Commands Loaded:")
    for cmd in synced:
        print(f"- /{cmd.name}")
    print(f"Logged in as {bot.user}")
@bot.event
async def on_error(event, *args, **kwargs):
    channel = None

    for arg in args:
        if isinstance(arg, discord.Interaction):
            channel = arg.channel
            break
        elif hasattr(arg, 'channel'):
            channel = arg.channel
            break

    if channel:
        try:
            await channel.send(file=discord.File("its_denos_fault.png"))
        except Exception as e:
            print(f"Failed to send error image: {e}")

    traceback.print_exc()
@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    

    effect_id = globals().get("CURRENT_EFFECT_ID", "No effect ID tracked.")
    tb = traceback.format_exc()

    try:
        # Try sending error as short message (if small enough)
        full_text = f"💢 Global Error (Effect ID):\n```{effect_id}```\nTraceback:\n```{tb}```"
        if len(full_text) < 2000:
            await interaction.followup.send(full_text, ephemeral=True)
        else:
            # Too long? Send as file instead
            file = File(io.StringIO(tb), filename="traceback.txt")
            await interaction.followup.send(
                content=f"💢 Global Error (Effect ID): `{effect_id}`\nTraceback too long — see file:",
                file=file,
                ephemeral=True
            )
    except discord.errors.InteractionResponded:
        try:
            # If already responded, use followup
            file = File(io.StringIO(tb), filename="traceback.txt")
            await interaction.followup.send(
                content=f"💢 Global Error (Effect ID): `{effect_id}`\nTraceback too long — see file:",
                file=file,
                ephemeral=True
            )
        except Exception as e:
            print("Failed to send followup error:", e)

    # Always print in console too
    print("=== APP CMD ERROR ===")
    print(tb)

    # Send the image as a meme after
    try:
        file = File("images/its_denos_fault.png")
        if interaction.response.is_done():
            await interaction.followup.send(file=file, ephemeral=True)
        else:
            await interaction.followup.send(file=file, ephemeral=True)
    except Exception as e:
        print(f"Failed to send error image: {e}")

async def main():
    load_dotenv()
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("this MORON really forgot his bot token, this could NOT have been me brah 💀💀💀 bro is NOT getting hired at software development, bro is COOKED, mods kill this guy with hammers and sneak poison in his drinks, expire his ass and send him to the gulag")

    modifiers.load_modifiers()
    await load_all_extensions()

    print(list(ProfileMan.profiles.keys()))
    await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if str(e).startswith("asyncio.run() cannot be called"):
            import nest_asyncio
            nest_asyncio.apply()
            asyncio.get_event_loop().run_until_complete(main())
        else:
            raise

