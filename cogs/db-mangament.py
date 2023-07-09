import discord
from discord.ext import commands
import datetime
import os

class db_management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connection = bot.get_cog('database').connection
        self.cursor = bot.get_cog('database').cursor

    async def is_authorised_or_special_user(ctx):
        special_user_id = 158567567487795200
        if ctx.author.id == special_user_id:
            return True
        if ctx.author.guild_permissions.manage_messages:
            return True
        return False

    @commands.command()
    @commands.guild_only()
    @commands.check(is_authorised_or_special_user)
    async def findmsg(self, ctx, *args):
        if len(args) == 1:
            id = args[0]
            self.cursor.execute("SELECT user_id, channel_id, content, timestamp FROM msgs WHERE message_id = ? AND guild_id = ?", (id, ctx.guild.id))
            result = self.cursor.fetchone()

            if result:
                user_id, channel_id, content, timestamp = result
                user = await self.bot.fetch_user(user_id)
                channel = self.bot.get_channel(channel_id)
                timestamp = datetime.datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')

                max_length = 1000
                if len(content) > max_length:
                    content = content[:max_length] + '...'

                embed = discord.Embed(title="Message Found", color=discord.Color.green())
                embed.set_author(name=f"{user.display_name}#{user.discriminator} (ID:{user.id})", icon_url=user.avatar.url)
                embed.add_field(name="Channel:", value=channel.mention, inline=False)
                embed.add_field(name="Message Content:", value=content, inline=False)
                embed.set_footer(text=f"Message sent on: {timestamp} UTC")

                await ctx.send(embed=embed)
            else:
                await ctx.send("No messages could be found that match that ID.")


        elif len(args) == 2 and args[0] == '-g':
            id = args[1]
            if ctx.author.id != 158567567487795200:
                return await ctx.send('You are not authorised to check messages globally.')

            self.cursor.execute("SELECT user_id, channel_id, content, timestamp, guild_id FROM msgs WHERE message_id = ?", (id,))
            result = self.cursor.fetchone()
            content = result[0]
            print(content)

            if result:
                user_id, channel_id, content, timestamp, guild_id = result
                guild = self.bot.get_guild(guild_id)
                user = await self.bot.fetch_user(user_id)
                channel = self.bot.get_channel(channel_id)
                timestamp = datetime.datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')

                max_length = 1000
                if len(content) > max_length:
                    content = content[:max_length] + '...'

                embed = discord.Embed(title="Message Found", color=discord.Color.green())
                embed.set_author(name=f"{user.display_name}#{user.discriminator} (ID:{user.id})", icon_url=user.avatar.url)
                embed.add_field(name="Guild:", value=f"{guild.name} (ID:{guild_id})", inline=False)
                embed.add_field(name="Channel:", value=channel.mention, inline=False)
                embed.add_field(name="Message Content:", value=content, inline=False)
                embed.set_footer(text=f"Message sent on: {timestamp} UTC")

                await ctx.send(embed=embed)

        else:
            await ctx.send('Invalid command usage.')


    @commands.command()
    @commands.is_owner()
    async def dbstats(self, ctx):
        db_size = os.path.getsize("data/databases/data.db") / (1024 * 1024)
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()

        embed = discord.Embed(title="Database Stats", color=discord.Color.green())
        embed.add_field(name="Number of Tables", value=len(tables)-1, inline=False)

        for table in tables:
            if table[0] != 'sqlite_sequence':
                self.cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                count = self.cursor.fetchone()[0]
                embed.add_field(name=f"{table[0]}", value=f"{count} entries", inline=False)
        embed.set_footer(text=f"Database size: {db_size:.2f} MB")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def guildstats(self, ctx):
        # This is ugly and missing a lot of info, would also like to add a timeframe tool later on.
        total_messages = self.cursor.execute("SELECT COUNT(*) FROM msgs WHERE guild_id = ?", (ctx.guild.id,)).fetchone()[0]
        total_edits = self.cursor.execute("SELECT COUNT(*) FROM msg_edits WHERE guild_id = ?", (ctx.guild.id,)).fetchone()[0]
        total_deletions = self.cursor.execute("SELECT COUNT(*) FROM msg_deletions WHERE guild_id = ?", (ctx.guild.id,)).fetchone()[0]
        embed = discord.Embed(title=f"{ctx.guild.name} Stats")
        embed.add_field(name="Total Logged Messages", value=total_messages, inline=False)
        embed.add_field(name="Total Logged Edits", value=total_edits, inline=False)
        embed.add_field(name="Total Logged Deletions", value=total_deletions, inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(db_management(bot))

