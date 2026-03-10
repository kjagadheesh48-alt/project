import discord
from discord import app_commands
from discord.ext import commands
from database import cursor, conn

class Rating(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rate_alumni")
    async def rate_alumni(self, interaction: discord.Interaction, alumni_id: str, rating: int, feedback: str):

        cursor.execute(
            "INSERT INTO ratings (alumni_id, student_id, rating, feedback) VALUES (?, ?, ?, ?)",
            (alumni_id, str(interaction.user.id), rating, feedback)
        )
        conn.commit()

        await interaction.response.send_message("⭐ Rating submitted!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Rating(bot))
