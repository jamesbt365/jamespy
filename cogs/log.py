import asyncio
import discord
from discord.ext import commands
from discord import Embed
import re

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

cameralist = []
with open("./cogs/words/cameras.txt") as f:
    for line in f:
        cameralist.append(line.strip())
class Log(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

# TODO: log most other events.

  @commands.Cog.listener()
  async def on_message(self, message):
    messagewords = message.content.lower().split(" ")
    blacklisted_words = [word for word in messagewords if any(j in word and word not in fixlist for j in badlist)]
    if blacklisted_words:
        print(f"Flagged for bad word(s): {Style.BRIGHT}{Fore.RED}" + ", ".join(blacklisted_words))
        print(f"{Fore.LIGHTBLACK_EX}[{message.guild}] [#{message.channel}]{Fore.RESET} {message.author}: {Style.BRIGHT}{Fore.RED}{message.content}")
    else:
        print(f"{Fore.LIGHTBLACK_EX}[{message.guild}] [#{message.channel}]{Fore.RESET} {message.author}: {message.content}")
    if message.author.id != self.bot.user.id:
      if any(word in message.content.lower() for word in cameralist):
        embed = Embed(title=f"Server: {message.guild}", description=f"A message sent in **#{message.channel.name}** by **{message.author}**: {message.content}", color=0x00ff00)
        await self.bot.get_user(326444255361105920).send(embed=embed)

  @commands.Cog.listener()
  async def on_message_delete(self, message):
    print(f"{Style.DIM}{Fore.LIGHTRED_EX}[{message.guild}] [#{message.channel}] A message from {Style.RESET_ALL}{message.author}{Style.DIM}{Fore.LIGHTRED_EX} was deleted: {message.content}")

  @commands.Cog.listener()
  async def on_message_edit(self, before, after):
    if before.content == after.content:
        return
    if before.author.id == 250717919221252117: # ignore oink because bombing spams the log.
      return

    # TODO: ignore oink bot.
    print(f"{Fore.CYAN}[{before.guild}] [#{before.channel}] A message from {Fore.RESET}{before.author}{Fore.CYAN} was edited:")
    print(f"{Fore.CYAN}BEFORE: {before.author}: {before.content}")
    print(f"{Fore.CYAN}AFTER:  {after.author}: {after.content}")

async def setup(bot):
  await bot.add_cog(Log(bot))
