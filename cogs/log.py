import asyncio
import discord
from discord.ext import commands
from discord import Embed

import colorama
from colorama import init, Fore, Style

colorama.init(autoreset=True)


def read_words_from_file(file_path):
    words = []
    with open(file_path) as f:
        for line in f:
            words.append(line.strip())
    return words


badlist = read_words_from_file("./cogs/lists/badwords.txt")
fixlist = read_words_from_file("./cogs/lists/fixwords.txt")
cameralist = read_words_from_file("./cogs/lists/cameras.txt")


class Log(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO: log most other events.

    @commands.Cog.listener()
    async def on_message(self, message):
        # This following segment ignores mudae and mudae commands in the mudae channel of discord.gg/osu
        if message.author.id == 432610292342587392:
            return
        if message.content.startswith("$") and message.channel.id == 850342078034870302:
            return

        messagewords = message.content.lower().split(" ")
        blacklisted_words = [word for word in messagewords if any(j in word and word not in fixlist for j in badlist)]
        if blacklisted_words:
            print(f"Flagged for bad word(s): {Style.BRIGHT}{Fore.RED}" + ", ".join(blacklisted_words))
            print(f"{Fore.LIGHTBLACK_EX}[{message.guild}] [#{message.channel}]{Fore.RESET} {message.author}: {Style.BRIGHT}{Fore.RED}{message.content}")
        else:
            print(f"{Fore.LIGHTBLACK_EX}[{message.guild}] [#{message.channel}]{Fore.RESET} {message.author}: {message.content}")

        if message.author.id != self.bot.user.id:
            if any(f" {word} " in f" {message.content.lower()} " for word in cameralist):
                embed = Embed(
                    title=f"Server: {message.guild}",
                    description=f"A message sent in **#{message.channel.name}** by **{message.author}**: {message.content}",
                    color=0x00FF00)
                await self.bot.get_user(326444255361105920).send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        print(
            f"{Style.DIM}{Fore.LIGHTRED_EX}[{message.guild}] [#{message.channel}] A message from {Style.RESET_ALL}{message.author}{Style.DIM}{Fore.LIGHTRED_EX} was deleted: {message.content}"
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content == after.content:
          return
        if (before.author.id == 250717919221252117):  # ignore oink because bombing spams the log.
          return

        print(f"{Fore.CYAN}[{before.guild}] [#{before.channel}] A message from {Fore.RESET}{before.author}{Fore.CYAN} was edited:")
        print(f"{Fore.CYAN}BEFORE: {before.author}: {before.content}")
        print(f"{Fore.CYAN}AFTER:  {after.author}: {after.content}")


async def setup(bot):
    await bot.add_cog(Log(bot))
