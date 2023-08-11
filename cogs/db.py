import discord
from discord.ext import commands
import sqlite3
import datetime
import re

# TODO: at some point I want to log usernames and nickname changes, message purge isn't logged yet and a few other select things I want to monitor closer.

class database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connection = sqlite3.connect('data/databases/data.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS msgs (guild_id INTEGER NULL, channel_id INTEGER, message_id INTEGER, user_id INTEGER, content TEXT, timestamp TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS msg_edits (guild_id INTEGER NULL, channel_id INTEGER, message_id INTEGER, user_id INTEGER, old_content TEXT, new_content TEXT, timestamp TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS msg_deletions (guild_id INTEGER NULL, channel_id INTEGER, message_id INTEGER, user_id INTEGER, content TEXT, timestamp TEXT)')
        self.connection.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild:
            guild_id = message.guild.id
            channel_id = message.channel.id
        else:
            guild_id = None
            channel_id = message.channel.id

        try:
            if str(message.author.id) == "370728608752205824" and message.embeds:
                embed = message.embeds[0]
                if embed.title.startswith("Unbanned"):
                    await message.add_reaction("✅")
        except Exception as e:
            print(e)
        message_id = message.id
        user_id = message.author.id
        content = message.content
        timestamp = datetime.datetime.utcnow().isoformat()
        self.cursor.execute('INSERT INTO msgs (guild_id, channel_id, message_id, user_id, content, timestamp) VALUES (?, ?, ?, ?, ?, ?)', (guild_id, channel_id, message_id, user_id, content, timestamp))
        self.connection.commit()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.author.id == 370728608752205824 and reaction.message.embeds and reaction.emoji == "✅" and user != self.bot.user:
            embed = reaction.message.embeds[0]
            if embed.title.startswith("Unbanned"):
                mention_regex = r'<@!?(\d+)>'
                match = re.search(mention_regex, reaction.message.embeds[0].description)
                if match:
                    user_id = int(match.group(1))
                    guild_id = reaction.message.guild.id
                    author_id = reaction.message.author.id

                    # Check if the user is already a member of the guild
                    member = reaction.message.guild.get_member(user_id)
                    if member is not None:
                        await reaction.message.reply(f"{user.mention} <@{user_id}> is already in the guild!")
                        return

                    # Check the count of join_tracks for the author_id
                    self.cursor.execute('SELECT COUNT(*) FROM join_tracks WHERE author_id = ?', (user.id,))
                    count = self.cursor.fetchone()[0]
                    if count >= 20:
                        await reaction.message.reply(f"{user.mention} you are already tracking 20 users.")
                        return

                    # Check if the join_track entry already exists
                    self.cursor.execute('SELECT * FROM join_tracks WHERE guild_id = ? AND author_id = ? AND user_id = ?', (guild_id, user.id, user_id))
                    existing = self.cursor.fetchone()
                    if existing:
                        await reaction.message.reply(f"{user.mention} you are already tracking <@{user_id}>.")
                    else:
                        # Insert the join_track entry into the database
                        timestamp = datetime.datetime.utcnow().isoformat()
                        self.cursor.execute('INSERT INTO join_tracks (guild_id, author_id, user_id, timestamp) VALUES (?, ?, ?, ?)', (guild_id, user.id, user_id, timestamp))
                        self.connection.commit()
                        await reaction.message.reply(f"{user.mention} <@{user_id}> has been added to tracking list.")





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
