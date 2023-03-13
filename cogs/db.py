import asyncio
import discord
from discord.ext import commands
import sqlite3
import datetime

# TODO: at some point I want to log usernames and nickname changes, message purge isn't logged yet and a few other select things I want to monitor closer.

class database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connection = sqlite3.connect('data/databases/messages.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS msgs (id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id INTEGER NULL, channel_id INTEGER, message_id INTEGER, user_id INTEGER, content TEXT, timestamp TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS msg_edits (id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id INTEGER NULL, channel_id INTEGER, message_id INTEGER, user_id INTEGER, old_content TEXT, new_content TEXT, timestamp TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS msg_deletions (id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id INTEGER NULL, channel_id INTEGER, message_id INTEGER, user_id INTEGER, content TEXT, timestamp TEXT)')
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

async def setup(bot):
    await bot.add_cog(database(bot))
