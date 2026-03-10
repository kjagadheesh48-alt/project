import discord
from discord import app_commands
from discord.ext import commands
from database import cursor, conn

class Register(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------------- REGISTER STUDENT ----------------
    @app_commands.command(name="register_student", description="Register as a student")
    async def register_student(
        self,
        interaction: discord.Interaction,
        name: str,
        department: str,
        year: str,
        interest: str
    ):

        # Save to database (explicit columns = safer)
        cursor.execute("""
            REPLACE INTO students 
            (discord_id, name, department, year, interests)
            VALUES (?, ?, ?, ?, ?)
        """, (str(interaction.user.id), name, department, year, interest.lower()))

        conn.commit()

        # Assign role
        role = discord.utils.get(interaction.guild.roles, name="student")
        alumni_role = discord.utils.get(interaction.guild.roles, name="alumni")

        if role:
            await interaction.user.add_roles(role)

        # Remove alumni role if exists
        if alumni_role and alumni_role in interaction.user.roles:
            await interaction.user.remove_roles(alumni_role)

        await interaction.response.send_message(
            "✅ Student Registered & Role Assigned!",
            ephemeral=True
        )

    # ---------------- REGISTER ALUMNI ----------------
    @app_commands.command(name="register_alumni", description="Register as an alumni")
    async def register_alumni(
        self,
        interaction: discord.Interaction,
        name: str,
        graduation_year: str,
        job_role: str,
        industry: str
    ):

        cursor.execute("""
            REPLACE INTO alumni 
            (discord_id, name, graduation_year, job_role, industry)
            VALUES (?, ?, ?, ?, ?)
        """, (str(interaction.user.id), name, graduation_year, job_role.lower(), industry.lower()))

        conn.commit()

        # Assign role
        role = discord.utils.get(interaction.guild.roles, name="alumni")
        student_role = discord.utils.get(interaction.guild.roles, name="student")

        if role:
            await interaction.user.add_roles(role)

        # Remove student role if exists
        if student_role and student_role in interaction.user.roles:
            await interaction.user.remove_roles(student_role)

        await interaction.response.send_message(
            "✅ Alumni Registered & Role Assigned!",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Register(bot))
