import os
import discord
from discord import app_commands
from groq import Groq
from database import cursor

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def setup(bot):

    @bot.tree.command(
        name="career_suggest",
        description="Get AI career suggestions based on your interests"
    )
    async def career_suggest(interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        try:
            # Get student info
            cursor.execute(
                "SELECT interests, skills FROM students WHERE discord_id = ?",
                (str(interaction.user.id),)
            )
            student = cursor.fetchone()

            if not student:
                await interaction.followup.send(
                    "❌ You must register as a student first.",
                    ephemeral=True
                )
                return

            interests, skills = student

            prompt = f"""
            A student has the following:

            Interests: {interests}
            Skills: {skills}

            Suggest:
            1. Three suitable career paths
            2. Required skills to improve
            3. One certification/course recommendation for each

            Keep answer clear and structured.
            """

            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            reply = completion.choices[0].message.content

            await interaction.followup.send(reply[:1900], ephemeral=True)

        except Exception as e:
            print("Career AI Error:", e)
            await interaction.followup.send(
                "⚠️ AI service temporarily unavailable.",
                ephemeral=True
            )
