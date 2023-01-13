import asyncio
import discord
from discord.ext import commands
import os

import colorama
from colorama import init, Fore, Style

colorama.init(autoreset=True)


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="-", intents=intents)

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.environ["JAMESPY_TOKEN"])

asyncio.run(main())