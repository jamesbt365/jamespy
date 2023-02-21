import asyncio
import discord
import random
from discord.ext import commands
from discord import Embed


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='lob')
    async def lob(self, ctx):
        with open('./cogs/lists/loblist.txt', 'r') as file:
            loblist = file.readlines()
        lob = random.choice(loblist).strip()
        await ctx.send(lob)

async def setup(bot):
    await bot.add_cog(General(bot))
