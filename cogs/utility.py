import discord
import random
import datetime
import io
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
            embed = discord.Embed(color=discord.Color.green())
            embed.set_author(icon_url=ctx.author.avatar.url, name=f"{ctx.author.name}'s Choice")
            embed.description = chosen_option
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self): 
        try:
            self.cursor.execute('SELECT DISTINCT guild_id FROM join_tracks')
            guild_ids = self.cursor.fetchall()

            # Iterate through each guild ID
            for guild_id_tuple in guild_ids:
                guild_id = guild_id_tuple[0]

                # Retrieve join tracks for the current guild
                self.cursor.execute('SELECT * FROM join_tracks WHERE guild_id = ?', (guild_id,))
                tracked_users = self.cursor.fetchall()

                # Retrieve the guild object
                guild = self.bot.get_guild(guild_id)
                if guild is None:
                    print(f"Invalid guild ID: {guild_id}")
                    continue

                print(f"Checking join tracks in guild: {guild.name} (ID: {guild.id})")

                # Iterate through tracked users
                for track in tracked_users:
                    author_id = track[1]
                    user_id = track[2]

                    # Retrieve user and author objects
                    user = guild.get_member(user_id)
                    author = self.bot.get_user(author_id)

                    if user is not None and author is not None:
                        print(f"Tracked User: {user.name} (ID: {user.id})")
                        print(f"Tracked in Guild: {guild.name} (ID: {guild.id})")
                        print(f"Tracked by User: {author.name} (ID: {author.id})")

                        # Send a message to the author
                        try:
                            await author.send(f"{user.name} has joined {guild.name}!")
                        except discord.Forbidden:
                            print(f"Failed to send message to {author.name}")

                        # Delete the join track entry
                        self.cursor.execute('DELETE FROM join_tracks WHERE guild_id = ? AND author_id = ? AND user_id = ?', (guild_id, author_id, user_id))
                        self.connection.commit()
                    else:
                        print(f"Invalid user ID: {user_id} or author ID: {author_id}")

            print("Finished checking join tracks.")
        except Exception as e:
            print(e)



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
            await ctx.send("You have reached the maximum snumber of tracked users.")
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


    @commands.command(name='dump-guild')
    @commands.has_permissions(manage_messages=True)
    async def dump_guild(self, ctx):
        try:
            guild = ctx.guild
            categories = guild.by_category() 
            permissions_str = "Channel and Category Permissions:\n"

            for category, channels in categories:
                if category is not None:
                    permissions_str += f"--- Category: {category.name} ---\n"
                    category_overwrites = category.overwrites

                    for target, overwrite in category_overwrites.items():
                        if isinstance(target, discord.Role):
                            target_name = f"Role: {target.name}"
                            target_color = target.color
                        elif isinstance(target, discord.Member):
                            target_name = f"Member: {target.display_name}"
                            target_color = None
                        else:
                            target_name = f"Unknown Target"
                            target_color = None

                        allowed = overwrite.pair()[0]
                        denied = overwrite.pair()[1]

                        permissions_str += f"{target_name}\nAllow: {allowed}\nDeny: {denied}\n\n"

                for channel in channels:
                    if isinstance(channel, discord.TextChannel):
                        overwrites = channel.overwrites

                        permissions_str += f"Permissions for #{channel.name}:\n"

                        for target, overwrite in overwrites.items():
                            if isinstance(target, discord.Role):
                                target_name = f"Role: {target.name}"
                                target_color = target.color
                            elif isinstance(target, discord.Member):
                                target_name = f"Member: {target.display_name}"
                                target_color = None
                            else:
                                target_name = f"Unknown Target"
                                target_color = None

                            allowed = overwrite.pair()[0]
                            denied = overwrite.pair()[1]

                            permissions_str += f"{target_name}\nAllow: {allowed}\nDeny: {denied}\n\n"

            voice_channels = guild.voice_channels

            for channel in voice_channels:
                overwrites = channel.overwrites

                permissions_str += f"Permissions for {channel.name} (Voice Channel):\n"

                for target, overwrite in overwrites.items():
                    if isinstance(target, discord.Role):
                        target_name = f"Role: {target.name}"
                        target_color = target.color
                    elif isinstance(target, discord.Member):
                        target_name = f"Member: {target.display_name}"
                        target_color = None
                    else:
                        target_name = f"Unknown Target"
                        target_color = None

                    allowed = overwrite.pair()[0]
                    denied = overwrite.pair()[1]

                    permissions_str += f"{target_name}\nAllow: {allowed}\nDeny: {denied}\n\n"

            file_data = io.BytesIO(permissions_str.encode()) 

            roles_str = "Roles and Role Permissions:\n"
            sorted_roles = sorted(guild.roles, key=lambda role: role.position, reverse=True)
            for role in sorted_roles:
                if role.name != "@everyone":
                    roles_str += f"Role: {role.name}\n"
                    roles_str += f"Color: {role.color}\n"
                    permissions = role.permissions
                    roles_str += f"Permissions: {permissions.value}\n\n"

            roles_file_data = io.BytesIO(roles_str.encode())
            roles_file = discord.File(roles_file_data, filename="roles.txt")

            perms_file = discord.File(file_data, filename="permissions.txt")
            await ctx.send(files=[roles_file, perms_file])
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(Utility(bot))
