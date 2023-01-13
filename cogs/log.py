import asyncio
import discord
from discord.ext import commands

import colorama
from colorama import init, Fore, Style

colorama.init(autoreset=True)

class Log(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

# TODO: catch blacklisted words
# TODO: log most other events.

  @commands.Cog.listener()
  async def on_message(self, message):
    print(f"{Fore.LIGHTBLACK_EX}[{message.guild}] [#{message.channel}]{Fore.RESET} {message.author}: {message.content}")

  @commands.Cog.listener()
  async def on_message_delete(self, message):
    print(f"{Style.DIM}{Fore.LIGHTRED_EX}[{message.guild}] [#{message.channel}] A message from {Style.RESET_ALL}{message.author}{Style.DIM}{Fore.LIGHTRED_EX} was deleted: {message.content}")

  @commands.Cog.listener()
  async def on_message_edit(self, before, after):
    if before.content == after.content:
        return

    # TODO: ignore oink bot.
    print(f"{Fore.CYAN}[{before.guild}] [#{before.channel}] A message from {Fore.RESET}{before.author}{Fore.CYAN} was edited:")
    print(f"{Fore.CYAN}BEFORE: {before.author}: {before.content}")
    print(f"{Fore.CYAN}AFTER:  {after.author}: {after.content}")

async def setup(bot):
  await bot.add_cog(Log(bot))