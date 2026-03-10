import os
import discord
from discord import app_commands
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

async def setup(bot):

    @bot.tree.command(
        name="ask_ai",
        description="Ask the AI anything"
    )
    @app_commands.describe(question="Your question for the AI")
    async def ask_ai(interaction: discord.Interaction, question: str):

        # Prevent interaction timeout
        await interaction.response.defer(ephemeral=True)

        try:
            completion = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant inside a Discord alumni mentorship server."
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                temperature=0.7,
                max_tokens=1024
            )

            reply = completion.choices[0].message.content

            # Discord message limit protection
            if len(reply) > 1900:
                reply = reply[:1900]

            await interaction.followup.send(
                reply,
                ephemeral=True
            )

        except Exception as e:
            print("AI ERROR:", e)

            await interaction.followup.send(
                "⚠️ AI service is temporarily unavailable.",
                ephemeral=True
            )