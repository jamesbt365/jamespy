import asyncio
import discord
import random
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def choose(self, ctx, *options):
        if len(options) < 2:
            await ctx.send("Not enough options to choose from.")
        else:
            chosen_option = random.choice(options)
            await ctx.send(f"{chosen_option}")


async def setup(bot):
    await bot.add_cog(Utility(bot))
