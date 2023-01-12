import discord
from discord.ext import commands
import logging
import os

import colorama
from colorama import init, Fore, Style

colorama.init(autoreset=True)


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="-", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

# TODO: move these to a seperate file
# TODO: catch blacklisted words
# TODO: log most other events.

@bot.event
async def on_message(message):
    print(f"{Fore.LIGHTBLACK_EX}[{message.guild}] [#{message.channel}]{Fore.RESET} {message.author}: {message.content}")
# i think i can do better here
@bot.event
async def on_message_delete(message):
    print(f"{Style.DIM}{Fore.LIGHTRED_EX}[{message.guild}] [#{message.channel}] A message from {Style.RESET_ALL}{message.author}{Style.DIM}{Fore.LIGHTRED_EX} was deleted: {message.content}")


@bot.event
async def on_message_edit(before, after):
    if before.content == after.content:
        return

    # Might try and trim this down to 2 lines while still looking good.
    # TODO: ignore bots, typically they don't need to be tracked.
    print(f"{Fore.CYAN}[{before.guild}] [#{before.channel}] A message from {Fore.RESET}{before.author}{Fore.CYAN} was edited:")
    print(f"{Fore.CYAN}BEFORE: {before.author}: {before.content}")
    print(f"{Fore.CYAN}AFTER:  {after.author}: {after.content}")


bot.run(os.environ["JAMESPY_TOKEN"])