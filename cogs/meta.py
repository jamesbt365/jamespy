import asyncio
import discord
from discord.ext import commands
from discord import Embed


class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["github", "jamespy"])
    async def source(self, ctx):
        await ctx.send("<https://github.com/jamesbt365/jamespy>")

    @commands.command(name='shutdown', hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        # implement buttons to the command and i guess a flag to just shutdown without the embed and menu when i eventually add?
        await ctx.send('Bot is shutting down...')
        await ctx.bot.close()

async def setup(bot):
    await bot.add_cog(Meta(bot))
