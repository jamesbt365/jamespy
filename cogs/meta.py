from discord.ext import commands
import discord
import subprocess

class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='shutdown-front', hidden=True)
    @commands.is_owner()
    async def shutdown_front(self, ctx):
        await ctx.send('Bot is shutting down...')
        await ctx.bot.close()



async def setup(bot):
    await bot.add_cog(Meta(bot))
