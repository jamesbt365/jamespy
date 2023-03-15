import asyncio
import discord
import random
import datetime
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connection = bot.get_cog('database').connection
        self.cursor = bot.get_cog('database').cursor

    @commands.command()
    async def choose(self, ctx, *options):
        if len(options) < 2:
            await ctx.send("Not enough options to choose from.")
        else:
            chosen_option = random.choice(options)
            await ctx.send(f"{chosen_option}")

    @commands.command(name="track-user")
    @commands.guild_only()
    async def track_user(self, ctx, user: discord.User):
        # Check if the user is a member of the current server
        member = ctx.guild.get_member(user.id)
        if member is not None:
            await ctx.send(f"{user.mention} is a member of this server.")
            return

        self.cursor.execute('SELECT COUNT(*) FROM join_tracks WHERE author_id = ?', (ctx.author.id,))
        count = self.cursor.fetchone()[0]

        if count >= 20:
            await ctx.send("You have reached the maximum number of tracked users.")
        else:
            self.cursor.execute('SELECT * FROM join_tracks WHERE guild_id = ? AND author_id = ? AND user_id = ?', (ctx.guild.id, ctx.author.id, user.id))
            existing = self.cursor.fetchone()

            if existing:
                await ctx.send(f"{user.mention} is already in the database for this server.")
            else:
                self.cursor.execute('INSERT INTO join_tracks (guild_id, author_id, user_id, timestamp) VALUES (?, ?, ?, ?)', (ctx.guild.id, ctx.author.id, user.id, datetime.datetime.utcnow().isoformat()))
                self.connection.commit()
                await ctx.send(f"{user.mention} has been added to the database for this server.")

    @track_user.error
    async def track_user_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid user provided. Please provide a valid user.")

    @commands.command(name="tracked-users")
    @commands.guild_only()
    async def tracked_users(self, ctx):
        self.cursor.execute('SELECT user_id FROM join_tracks WHERE guild_id = ? AND author_id = ?', (ctx.guild.id, ctx.author.id))
        tracked_users = self.cursor.fetchall()

        if not tracked_users:
            await ctx.send("You are not currently tracking any users for this server.")
        else:
            description = "\n".join([f"{await self.bot.fetch_user(user_id[0])} (ID:{user_id[0]})" for user_id in tracked_users])
            embed = discord.Embed(title="Tracked Users", description=description)
            await ctx.send(embed=embed)


    @tracked_users.error
    async def tracked_users_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid user provided. Please provide a valid user.")


    @commands.command(name="remove-track")
    @commands.guild_only()
    async def remove_track(self, ctx, user: discord.User):
        self.cursor.execute('SELECT * FROM join_tracks WHERE guild_id = ? AND author_id = ? AND user_id = ?', (ctx.guild.id, ctx.author.id, user.id))
        existing = self.cursor.fetchone()

        if not existing:
            await ctx.send(f"You are currently not tracking {user.mention} on this server.")
            return

        self.cursor.execute('DELETE FROM join_tracks WHERE guild_id = ? AND author_id = ? AND user_id = ?', (ctx.guild.id, ctx.author.id, user.id))
        self.connection.commit()

        await ctx.send(f"You are no longer tracking {user.mention} on this server.")


    @remove_track.error
    async def remove_track_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid user provided. Please provide a valid user.")

async def setup(bot):
    await bot.add_cog(Utility(bot))
