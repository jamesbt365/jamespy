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

    def get_sensor_information(self):
        process = subprocess.Popen(['sensors'], stdout=subprocess.PIPE)
        output, _ = process.communicate()
        output = output.decode('utf-8')

        sensor_info = {}

        lines = output.split('\n')
        current_group = None
        for line in lines:
            if 'Adapter:' in line:
                current_group = previous_line.strip()
            elif '°C' in line and ':' in line:
                sensor_name, temperature = line.split(':')
                sensor_name = sensor_name.strip()
                temperature = temperature.strip().split()[0]

                if current_group:
                    if current_group not in sensor_info:
                        sensor_info[current_group] = []
                    sensor_info[current_group].append((sensor_name, temperature))
            previous_line = line

        return sensor_info

    @commands.command(name='temp')
    @commands.is_owner()
    async def get_sensor_temperatures(self, ctx):
        sensor_data = self.get_sensor_information()

        sorted_sensor_data = dict(sorted(sensor_data.items(), key=lambda x: x[0]))

        embed = discord.Embed(title="Sensor Information")

        for group, sensors in sorted_sensor_data.items():
            field_value = ""
            for sensor in sensors:
                sensor_name, temperature = sensor
                field_value += f'{sensor_name}: {temperature}\n'
            embed.add_field(name=group, value=field_value, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='who-roles')
    @commands.has_guild_permissions(manage_messages=True)
    async def who_has_role(self, ctx, role_name, onlyid=False):
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        if role is None:
            await ctx.send(f"Role '{role_name}' not found.")
        else:
            users_with_role = role.members
            total_count = len(users_with_role)

            if total_count == 0:
                await ctx.send(f"No users found with the '{role_name}' role.")
            else:
                user_list = ""

                for member in users_with_role:
                    if onlyid:
                        user_list += f"{member.id}\n"
                    else:
                        user_list += f"{member.name} (ID: {member.id})\n"

                response = f"Total count of users with the '{role_name}' role: {total_count}\n"
                response += f"{'User IDs' if onlyid else 'Users'} with the '{role_name}' role:\n{user_list}"
                await ctx.send(response)



async def setup(bot):
    await bot.add_cog(Meta(bot))
