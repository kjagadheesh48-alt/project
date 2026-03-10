import os
import discord
from discord import app_commands
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def setup(bot):

    @bot.tree.command(
        name="summarize_session",
        description="Summarize last mentorship discussion in this channel"
    )
    async def summarize_session(interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        try:
            channel = interaction.channel

            # Only allow inside mentorship channels
            if not channel.name.startswith("mentorship"):
                await interaction.followup.send(
                    "❌ This command works only inside mentorship channels.",
                    ephemeral=True
                )
                return

            messages = []
            async for msg in channel.history(limit=20):
                if not msg.author.bot:
                    messages.append(f"{msg.author.display_name}: {msg.content}")

            if not messages:
                await interaction.followup.send(
                    "❌ Not enough messages to summarize.",
                    ephemeral=True
                )
                return

            messages.reverse()
            conversation_text = "\n".join(messages)

            prompt = f"""
            Summarize this mentorship conversation.

            Provide:
            1. Main discussion topics
            2. Advice given
            3. Action steps for student

            Conversation:
            {conversation_text}
            """

            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            summary = completion.choices[0].message.content

            await interaction.followup.send(summary[:1900], ephemeral=True)

        except Exception as e:
            print("Session AI Error:", e)
            await interaction.followup.send(
                "⚠️ AI summary failed.",
                ephemeral=True
            )
