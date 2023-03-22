import asyncio
import discord
import re
import unicodedata
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

patterns = [
re.compile(r"\b\w*j\s*\d*\W*?a+\W*\d*\W*?m+\W*\d*\W*?e+\W*\d*\W*?s+\W*\d*\W*?\w*\b", re.IGNORECASE | re.UNICODE),
re.compile(r"\b\w*b\s*\d*\W*?t+\W*\d*\W*?3+\W*\d*\W*?6+\W*\d*\W*?5+\W*\d*\W*?\w*\b", re.IGNORECASE | re.UNICODE),
]


class Log(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ############################### MESSAGES ###############################

    @commands.Cog.listener()
    async def on_message(self, message):
        # This following segment ignores mudae and mudae commands in the mudae channel of discord.gg/osu
        if message.author.id == 432610292342587392:
            return
        if message.content.startswith("$") and message.channel.id == 850342078034870302:
            return
        for pattern in patterns:
            if not message.guild or message.author.id == 158567567487795200:
                break  # skip messages from the specified user or DMs.
            if re.search(pattern, unicodedata.normalize('NFKD', message.content)):
                embed = Embed(
                    title=f"A pattern was matched!",
                    description=f"**{message.channel.mention}** by **{message.author}**: {message.content} \n\n [Jump to message!]({message.jump_url})",
                    color=0x00FF00)
                await self.bot.get_user(158567567487795200).send(f"In {message.guild.name} {message.channel.mention} you were mentioned by {message.author} (ID:{message.author.id})", embed=embed)
                break

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
        if user.bot:
            return
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
    async def on_member_remove(self, member):
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

    ############################### VOICE ###############################

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            if after.channel is not None:
                if before.channel is not None and after.channel.guild == before.channel.guild:
                    print(f"{Fore.GREEN}[{after.channel.guild}]: {member.name} switched from #{before.channel} to #{after.channel}")
                else:
                    print(f"{Fore.GREEN}[{after.channel.guild}]: {member.name} joined #{after.channel}")
            else:
                print(f"{Fore.GREEN}[{before.channel.guild}]: {member.name} left #{before.channel}")

async def setup(bot):
    await bot.add_cog(Log(bot))
