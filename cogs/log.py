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


class Log(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO: log most other events.

    ############################### MESSAGES ###############################

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

    ############################### REACTIONS ###############################

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        print(f"{Fore.MAGENTA}[{reaction.message.guild}] [#{reaction.message.channel}] {user.name} added a reaction: {reaction.emoji}")

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        print(f"{Fore.MAGENTA}[{reaction.message.guild}] [#{reaction.message.channel}] {user.name} removed a reaction: {reaction.emoji}")

    @commands.Cog.listener()
    async def on_reaction_clear_emoji(self, reaction):
         print(f"{Fore.MAGENTA}[{reaction.message.guild}] [#{reaction.message.channel}] The {reaction.emoji} was cleared from {reaction.message}")

    @commands.Cog.listener()
    async def on_reaction_clear(self, message, reactions):
        print(f"{Fore.MAGENTA}[{message.guild}] [#{message.channel}] All reactions were cleared from message \"{message.author}: {message.content}\"")

    ############################### MEMBERS ###############################

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{Fore.YELLOW}[{member.guild}] {member.name} (ID:{member.id}) has joined!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{Fore.YELLOW}[{member.guild}] {member.name} (ID:{member.id}) has left!")


    ############################### CHANNELS ###############################

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        print(f"{Fore.BLUE}[{channel.guild}] #{channel.name} was created!")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        print(f"{Fore.BLUE}[{channel.guild}] #{channel.name} was deleted!")

    ############################### THREADS ###############################

    @commands.Cog.listener()
    async def on_thread_create(self, thread):
        print(f"{Fore.LIGHTBLUE_EX}[{thread.guild}] #{thread.name} was created in #{thread.parent}!")

    @commands.Cog.listener()
    async def on_thread_remove(self, thread):
        print(f"{Fore.LIGHTBLUE_EX}[{thread.guild}] #{thread.name} was deleted from #{thread.parent}!")


async def setup(bot):
    await bot.add_cog(Log(bot))
