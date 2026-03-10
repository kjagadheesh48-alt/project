import os
import discord
from discord import app_commands
from database import cursor
import openpyxl
from datetime import datetime

ADMIN_SECRET = os.getenv("ADMIN_SECRET")

async def setup(bot):

    @bot.tree.command(
        name="admin_dashboard",
        description="View platform analytics and download report"
    )
    @app_commands.describe(
        key="Enter admin secret key"
    )
    async def admin_dashboard(interaction: discord.Interaction, key: str):

        await interaction.response.defer(ephemeral=True)

        if key != ADMIN_SECRET:
            await interaction.followup.send(
                "❌ Invalid admin key.",
                ephemeral=True
            )
            return

        # Fetch analytics
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM alumni")
        total_alumni = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM mentorship_requests")
        total_requests = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM mentorship_requests WHERE status = 'accepted'"
        )
        accepted_sessions = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(rating) FROM alumni")
        avg_rating = cursor.fetchone()[0] or 0

        avg_rating = round(avg_rating, 2)

        # Discord embed
        embed = discord.Embed(
            title="📊 Alumni Connect AI Dashboard",
            color=discord.Color.blue()
        )

        embed.add_field(name="👨‍🎓 Total Students", value=total_students)
        embed.add_field(name="🎓 Total Alumni", value=total_alumni)
        embed.add_field(name="📩 Total Requests", value=total_requests)
        embed.add_field(name="✅ Accepted Sessions", value=accepted_sessions)
        embed.add_field(name="⭐ Avg Alumni Rating", value=avg_rating)

        # ---------- CREATE EXCEL REPORT ----------

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Platform Analytics"

        sheet.append(["Metric", "Value"])
        sheet.append(["Total Students", total_students])
        sheet.append(["Total Alumni", total_alumni])
        sheet.append(["Total Mentorship Requests", total_requests])
        sheet.append(["Accepted Sessions", accepted_sessions])
        sheet.append(["Average Alumni Rating", avg_rating])

        # timestamp for file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mentora_report_{timestamp}.xlsx"

        filepath = f"./{filename}"
        workbook.save(filepath)

        file = discord.File(filepath)

        await interaction.followup.send(
            content="📥 Download the analytics report:",
            embed=embed,
            file=file,
            ephemeral=True
        )

        # optional cleanup
        try:
            os.remove(filepath)
        except:
            pass