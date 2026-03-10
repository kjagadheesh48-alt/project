import os
import discord
from discord import app_commands
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def setup(bot):

    @bot.tree.command(
        name="resume_review",
        description="Get AI feedback on your resume (paste text)"
    )
    @app_commands.describe(resume_text="Paste your resume content here")
    async def resume_review(interaction: discord.Interaction, resume_text: str):

        await interaction.response.defer(ephemeral=True)

        try:
            prompt = f"""
            Analyze the following resume and provide:

            1. Strengths
            2. Weaknesses
            3. Missing important skills (if any)
            4. Suggestions to improve
            5. Overall rating out of 10

            Resume:
            {resume_text}
            """

            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            feedback = completion.choices[0].message.content

            await interaction.followup.send(
                feedback[:1900],
                ephemeral=True
            )

        except Exception as e:
            print("Resume AI Error:", e)
            await interaction.followup.send(
                "⚠️ AI resume analysis failed.",
                ephemeral=True
            )
