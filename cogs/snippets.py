import asyncio
import discord
import os
import json

from discord.ext import commands
from discord import Embed


class Snippet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_to_snippets = {}

    def get_snippets(self, guild_id):
        if guild_id not in self.guild_to_snippets:
            self.guild_to_snippets[guild_id] = {}
            try:
                with open(f'config/snippet_storage/{guild_id}_snippets.json', 'r') as f:
                    self.guild_to_snippets[guild_id] = json.load(f)
            except json.JSONDecodeError:
                self.guild_to_snippets[guild_id] = {}
            except FileNotFoundError:
                pass

        return self.guild_to_snippets[guild_id]

    def save_snippets(self, guild_id):
        with open(f'config/snippet_storage/{guild_id}_snippets.json', 'w') as f:
            json.dump(self.guild_to_snippets[guild_id], f, indent=4)

    @commands.command(name='set-snippet')
    @commands.has_permissions(manage_messages=True)
    async def set_snippet(self, ctx, name: str, title: str, *description):
        snippets = self.get_snippets(ctx.guild.id)
        snippets[name] = {
            'title': title,
            'description': ' '.join(description).replace('\\n', '\n')
        }
        self.save_snippets(ctx.guild.id)

        embed = discord.Embed(
            title=title,
            description=''.join(description),
        )
        await ctx.send(f'Set the `{name}` snippet correctly!', embed=embed)

    @commands.command(name='snippet')
    async def snippet(self, ctx, name: str):
        snippets = self.get_snippets(ctx.guild.id)
        try:
            snippet = snippets[name]
        except KeyError:
            return await ctx.send(f'No snippet was found with the name `{name}`.')

        embed = discord.Embed(
            title=snippet['title'],
            description=snippet['description'],
        )
        
        #embed.set_image(url='https://cdn.discordapp.com/avatars/326444255361105920/4c0ce3b291650d44802fc9198a16c6d2.png?size=1024')
        await ctx.send(embed=embed)

    @commands.command(name='remove-snippet', aliases=["removesnippet", "delete-snippet", "deletesnippet"])
    @commands.has_permissions(manage_messages=True)
    async def remove_snippet(self, ctx, name: str):
        guild_id = str(ctx.guild.id)
        snippets = self.get_snippets(guild_id)
        if name not in snippets:
            return await ctx.send(f'No snippet found with the name `{name}`')

        del snippets[name]
        self.guild_to_snippets[guild_id] = snippets
        self.save_snippets(guild_id)
        await ctx.send(f'Snippet `{name}` removed successfully!')

    @commands.command(name='list-snippets', aliases=["list-snippet", "snippet-list", "snippets-list"])
    async def list_snippets(self, ctx):
        snippets = self.get_snippets(ctx.guild.id)
        if not snippets:
            return await ctx.send('This server currently doesn\'t have any snippets.')

        snippet_list = '\n'.join(f"`{name}`" for name in snippets)

        # Create the embed with the list of snippets in the description field
        embed = discord.Embed(
            title='Snippets',
            description=snippet_list,
            color=discord.Color.blue()
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Snippet(bot))