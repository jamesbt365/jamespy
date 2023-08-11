import discord
import io
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
