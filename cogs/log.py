import asyncio
import discord
from discord.ext import commands

import colorama
from colorama import init, Fore, Style

colorama.init(autoreset=True)

badlist = []
with open("./cogs/words/badwords.txt") as f:
    for line in f:
        badlist.append(line.strip())

fixlist = []
with open("./cogs/words/fixwords.txt") as f:
    for line in f:
        fixlist.append(line.strip())
class Log(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

# TODO: log most other events.

  @commands.Cog.listener()
  async def on_message(self, message):
    message_words = message.content.lower().split(" ")
    bad_words = set(badlist).intersection(message_words)
    fixed_words = set(fixlist).intersection(bad_words)
    if bad_words - fixed_words:
        print(f"Flagged for bad word(s): {Style.BRIGHT}{Fore.RED}{bad_words - fixed_words}")
        print(f"{Fore.LIGHTBLACK_EX}[{message.guild}] [#{message.channel}]{Fore.RESET} {message.author}: {Style.BRIGHT}{Fore.RED}{message.content}")
    else:
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
