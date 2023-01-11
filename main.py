import discord
from discord.ext import commands

import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='-', intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_message(message):
    print(f"{message.author}: {message.content}")

bot.run(os.environ['JAMESPY_TOKEN'])