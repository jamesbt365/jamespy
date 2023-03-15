import asyncio
import discord
from discord.ext import commands
import sqlite3
import datetime

# TODO: at some point I want to log usernames and nickname changes, message purge isn't logged yet and a few other select things I want to monitor closer.

class database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connection = sqlite3.connect('data/databases/data.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS msgs (id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id INTEGER NULL, channel_id INTEGER, message_id INTEGER, user_id INTEGER, content TEXT, timestamp TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS msg_edits (id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id INTEGER NULL, channel_id INTEGER, message_id INTEGER, user_id INTEGER, old_content TEXT, new_content TEXT, timestamp TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS msg_deletions (id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id INTEGER NULL, channel_id INTEGER, message_id INTEGER, user_id INTEGER, content TEXT, timestamp TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS join_tracks (id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id INTEGER NULL, author_id INTEGER, user_id INTEGER, timestamp TEXT)')
        self.connection.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild:
            guild_id = message.guild.id
            channel_id = message.channel.id
        else:
            guild_id = None
            channel_id = message.channel.id
        message_id = message.id
        user_id = message.author.id
        content = message.content
        timestamp = datetime.datetime.utcnow().isoformat()
        self.cursor.execute('INSERT INTO msgs (guild_id, channel_id, message_id, user_id, content, timestamp) VALUES (?, ?, ?, ?, ?, ?)', (guild_id, channel_id, message_id, user_id, content, timestamp))
        self.connection.commit()

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content == after.content:
            return
        if before.guild:
            guild_id = before.guild.id
            channel_id = before.channel.id
        else:
            guild_id = None
            channel_id = before.channel.id
        user_id = after.author.id
        message_id = before.id
        timestamp = datetime.datetime.utcnow().isoformat()
        self.cursor.execute('INSERT INTO msg_edits (guild_id, channel_id, message_id, user_id, old_content, new_content, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)', (guild_id, channel_id, message_id, user_id, before.content, after.content, timestamp))
        self.connection.commit()

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild:
            guild_id = message.guild.id
            channel_id = message.channel.id
        else:
            guild_id = None
            channel_id = message.channel.id
        message_id = message.id
        user_id = message.author.id if message.author else None
        timestamp = datetime.datetime.utcnow().isoformat()
        self.cursor.execute('INSERT INTO msg_deletions (guild_id, channel_id, message_id, user_id, content, timestamp) VALUES (?, ?, ?, ?, ?, ?)', (guild_id, channel_id, message_id, user_id, message.content, timestamp))
        self.connection.commit()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        user_id = member.id

        self.cursor.execute('SELECT author_id FROM join_tracks WHERE guild_id = ? AND user_id = ?', (guild_id, user_id))
        results = self.cursor.fetchall()

        if not results:
            return

        self.cursor.execute('DELETE FROM join_tracks WHERE guild_id = ? AND user_id = ?', (guild_id, user_id))
        self.connection.commit()

        # DM all users that were tracking the matched user.
        for result in results:
            author_id = result[0]
            try:
                author = await self.bot.fetch_user(author_id)
                await author.send(f"{member.mention} has joined {member.guild}!")
            except discord.Forbidden:
                continue


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.cursor.execute('SELECT * FROM join_tracks WHERE guild_id = ? AND author_id = ?', (member.guild.id, member.id))
        tracked_users = self.cursor.fetchall()

        self.cursor.execute('DELETE FROM join_tracks WHERE guild_id = ? AND author_id = ?', (member.guild.id, member.id))
        self.connection.commit()

        if tracked_users:
            for row in tracked_users:
                user_id = row[2]
                try:
                    user = await self.bot.fetch_user(user_id)
                    dm_channel = await user.create_dm()
                    await dm_channel.send(f"Sorry to inform you that the author of your tracked users has left the server.")
                except Exception as e:
                    print(f"Error sending DM to user {user_id}: {e}")

async def setup(bot):
    await bot.add_cog(database(bot))
