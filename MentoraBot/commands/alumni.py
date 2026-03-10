import discord
from discord import app_commands
from discord.ext import commands
from database import cursor, conn


class Alumni(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------------- REGISTER ALUMNI ----------------
    @app_commands.command(name="register_alumni", description="Register as an alumni")
    @app_commands.describe(
        name="Your Name",
        graduation_year="Graduation Year",
        job_role="Current Job Role",
        industry="Industry You Work In",
        skills="Your Skills (comma separated)"
    )
    async def register_alumni(
        self,
        interaction: discord.Interaction,
        name: str,
        graduation_year: str,
        job_role: str,
        industry: str,
        skills: str
    ):

        await interaction.response.defer(ephemeral=True)

        try:
            clean_skills = skills.lower().replace(" ", "")

            cursor.execute("""
                REPLACE INTO alumni
                (discord_id, name, graduation_year, job_role, industry, skills)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(interaction.user.id),
                name,
                graduation_year,
                job_role.lower(),
                industry.lower(),
                clean_skills
            ))

            conn.commit()

            # Assign roles
            alumni_role = discord.utils.get(interaction.guild.roles, name="alumni")
            student_role = discord.utils.get(interaction.guild.roles, name="student")

            if alumni_role:
                await interaction.user.add_roles(alumni_role)

            if student_role and student_role in interaction.user.roles:
                await interaction.user.remove_roles(student_role)

            await interaction.followup.send(
                "✅ Alumni Registered & Role Assigned!",
                ephemeral=True
            )

        except Exception as e:
            print("Register Alumni Error:", e)
            await interaction.followup.send(
                "⚠️ Something went wrong while registering.",
                ephemeral=True
            )

    # ---------------- SET AVAILABILITY ----------------
    @app_commands.command(name="set_availability", description="Set your mentorship availability")
    @app_commands.describe(status="True = Available, False = Busy")
    async def set_availability(self, interaction: discord.Interaction, status: bool):

        await interaction.response.defer(ephemeral=True)

        try:
            cursor.execute(
                "SELECT * FROM alumni WHERE discord_id = ?",
                (str(interaction.user.id),)
            )
            alumni = cursor.fetchone()

            if not alumni:
                await interaction.followup.send(
                    "❌ You are not registered as alumni.",
                    ephemeral=True
                )
                return

            availability_value = 1 if status else 0

            cursor.execute(
                "UPDATE alumni SET availability = ? WHERE discord_id = ?",
                (availability_value, str(interaction.user.id))
            )

            conn.commit()

            if status:
                message = "🟢 You are now AVAILABLE for mentorship."
            else:
                message = "🔴 You are now marked as BUSY."

            await interaction.followup.send(message, ephemeral=True)

        except Exception as e:
            print("Availability Error:", e)
            await interaction.followup.send(
                "⚠️ Something went wrong while updating availability.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Alumni(bot))
