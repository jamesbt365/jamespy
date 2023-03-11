import asyncio
import discord
import os
import json

from discord.ext import commands
from discord import Embed


class Snippet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.snippets = {}

    def get_guild_snippets(self, guild_id):
        if guild_id not in self.snippets:
            self.snippets[guild_id] = {}
            try:
                with open(f'config/snippet_storage/{guild_id}_snippets.json', 'r') as f:
                    self.snippets[guild_id] = json.load(f)
            except json.JSONDecodeError:
                self.snippets[guild_id] = {}
            except FileNotFoundError:
                pass
        return self.snippets[guild_id]

    def save_guild_snippets(self, guild_id):
        with open(f'config/snippet_storage/{guild_id}_snippets.json', 'w') as f:
            json.dump(self.snippets[guild_id], f, indent=4)

    @commands.command(name='set-snippet')
    @commands.has_permissions(manage_messages=True)
    async def set_snippet(self, ctx, name: str, title: str, *description):
        guild_id = str(ctx.guild.id)
        snippets = self.get_guild_snippets(guild_id)
        if "<" in name or ">" in name or "`" in name:
            return await ctx.send("Snippet names cannot contain `<`, `>`, or backticks.")
        name_lower = name.lower()
        snippets[name_lower] = {
            'title': title,
            'description': ' '.join(description).replace('\\n', '\n')
        }
        self.save_guild_snippets(guild_id)
        await ctx.send(f'Set the `{name}` snippet correctly!')

    @commands.command(name='snippet')
    async def snippet(self, ctx, name: str):
        guild_id = str(ctx.guild.id)
        snippets = self.get_guild_snippets(guild_id)
        if '`' in name:
            return await ctx.send('Backticks are a blacklisted character.')
        name_lower = name.lower()
        try:
            snippet = snippets[name_lower]
        except KeyError:
            return await ctx.send(f'No snippet was found with the name `{name}`.')
        embed = discord.Embed(
            title=snippet['title'],
            description=snippet['description'],
        )
        await ctx.send(embed=embed)

    @commands.command(name='remove-snippet', aliases=["removesnippet", "delete-snippet", "deletesnippet"])
    @commands.has_permissions(manage_messages=True)
    async def remove_snippet(self, ctx, name: str):
        guild_id = str(ctx.guild.id)
        snippets = self.get_guild_snippets(guild_id)
        name_lower = name.lower()
        if '`' in name:
            return await ctx.send('Backticks are a blacklisted character.')
        if name_lower not in snippets:
            return await ctx.send(f'No snippet found with the name `{name}`')
        del snippets[name_lower]
        self.save_guild_snippets(guild_id)
        await ctx.send(f'Snippet `{name}` removed successfully!')

    @commands.command(name='list-snippets', aliases=["list-snippet", "snippet-list", "snippets-list"])
    async def list_snippets(self, ctx):
        guild_id = str(ctx.guild.id)
        snippets = self.get_guild_snippets(guild_id)
        if not snippets:
            return await ctx.send('This server currently doesn\'t have any snippets.')
        snippet_list = '\n'.join(f"`{name}`" for name in snippets)
        embed = discord.Embed(
            title='Snippets',
            description=snippet_list,
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Snippet(bot))
