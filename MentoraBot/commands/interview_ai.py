import os
import discord
from discord import app_commands
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def setup(bot):

    @bot.tree.command(
        name="interview_prep",
        description="Generate AI interview questions"
    )
    @app_commands.describe(
        role="Job role (e.g., backend developer, data analyst)",
        level="Experience level (fresher / intern / experienced)"
    )
    async def interview_prep(
        interaction: discord.Interaction,
        role: str,
        level: str
    ):

        await interaction.response.defer(ephemeral=True)

        try:
            prompt = f"""
            Generate interview preparation questions.

            Job Role: {role}
            Experience Level: {level}

            Provide:
            1. 5 Technical Questions
            2. 3 HR Questions
            3. 2 Scenario-Based Questions
            4. 1 Coding Challenge

            Keep it structured and clear.
            """

            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            questions = completion.choices[0].message.content

            await interaction.followup.send(
                questions[:1900],
                ephemeral=True
            )

        except Exception as e:
            print("Interview AI Error:", e)
            await interaction.followup.send(
                "⚠️ AI interview generator failed.",
                ephemeral=True
            )
