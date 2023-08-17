import asyncio
import discord
from discord.ext import commands
import os
import logging


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="-", intents=intents)
bot.remove_command('help')

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you inside your home."))


async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.environ["JAMESPY_TOKEN"])

asyncio.run(main())
