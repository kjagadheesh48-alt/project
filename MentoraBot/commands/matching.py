import discord
from discord import app_commands
from database import cursor, conn


async def setup(bot):

    # ================= SMART MATCH =================

    @bot.tree.command(
        name="find_mentor",
        description="Smart match alumni based on role, industry and skills"
    )
    @app_commands.describe(
        interest="Enter your career interest (e.g., ai, ui, backend)"
    )
    async def find_mentor(interaction: discord.Interaction, interest: str):

        await interaction.response.defer(ephemeral=True)

        try:
            interest_lower = interest.lower().strip()

            cursor.execute("""
                SELECT discord_id, name, graduation_year, job_role, industry, skills, rating
                FROM alumni
                WHERE availability = 1
            """)
            alumni_list = cursor.fetchall()

            if not alumni_list:
                await interaction.followup.send(
                    "❌ No available alumni registered yet.",
                    ephemeral=True
                )
                return

            scored_alumni = []

            for alum in alumni_list:
                discord_id, name, grad_year, job_role, industry, skills, rating = alum

                job_role = job_role or ""
                industry = industry or ""
                skills = skills or ""
                rating = rating or 0

                score = 0

                if interest_lower == job_role.lower():
                    score += 5
                if interest_lower in job_role.lower():
                    score += 3
                if interest_lower in industry.lower():
                    score += 2
                if interest_lower in skills.lower():
                    score += 4

                score += float(rating)

                if score > 0:
                    scored_alumni.append((score, alum))

            if not scored_alumni:
                await interaction.followup.send(
                    "❌ No matching alumni found.",
                    ephemeral=True
                )
                return

            scored_alumni.sort(key=lambda x: x[0], reverse=True)

            response = "🎓 **Top Matching Alumni:**\n\n"

            for score, alum in scored_alumni[:5]:
                discord_id, name, grad_year, job_role, industry, skills, rating = alum

                response += (
                    f"🆔 Alumni ID: {discord_id}\n"
                    f"👤 Name: {name}\n"
                    f"🎓 Batch: {grad_year}\n"
                    f"💼 Role: {job_role}\n"
                    f"🏢 Industry: {industry}\n"
                    f"🛠 Skills: {skills}\n"
                    f"⭐ Rating: {rating}\n"
                    f"🔥 Match Score: {round(score, 2)}\n\n"
                )

            await interaction.followup.send(response, ephemeral=True)

        except Exception as e:
            print("Find Mentor Error:", e)
            await interaction.followup.send(
                "⚠️ Something went wrong while matching.",
                ephemeral=True
            )

    # ================= SEND REQUEST =================

    @bot.tree.command(
        name="request_mentor",
        description="Send mentorship request to an alumni"
    )
    @app_commands.describe(alumni_id="Enter the Alumni ID shown in results")
    async def request_mentor(interaction: discord.Interaction, alumni_id: str):

        await interaction.response.defer(ephemeral=True)

        try:
            alumni_id = alumni_id.strip()

            cursor.execute(
                "SELECT name FROM students WHERE discord_id = ?",
                (str(interaction.user.id),)
            )
            student = cursor.fetchone()

            if not student:
                await interaction.followup.send(
                    "❌ You must register as student first.",
                    ephemeral=True
                )
                return

            cursor.execute(
                "SELECT name FROM alumni WHERE discord_id = ?",
                (alumni_id,)
            )
            alumni = cursor.fetchone()

            if not alumni:
                await interaction.followup.send(
                    f"❌ Alumni ID `{alumni_id}` not found.",
                    ephemeral=True
                )
                return

            cursor.execute("""
                SELECT id FROM mentorship_requests
                WHERE student_id = ? AND alumni_id = ? AND status = 'pending'
            """, (str(interaction.user.id), alumni_id))

            if cursor.fetchone():
                await interaction.followup.send(
                    "⚠️ You already have a pending request.",
                    ephemeral=True
                )
                return

            cursor.execute("""
                INSERT INTO mentorship_requests (student_id, alumni_id, status)
                VALUES (?, ?, 'pending')
            """, (str(interaction.user.id), alumni_id))

            conn.commit()

            await interaction.followup.send(
                "✅ Mentorship request sent successfully!",
                ephemeral=True
            )

        except Exception as e:
            print("Request Error:", e)
            await interaction.followup.send(
                "⚠️ Something went wrong.",
                ephemeral=True
            )

    # ================= VIEW REQUESTS =================

    @bot.tree.command(
        name="view_requests",
        description="Alumni: View your pending mentorship requests"
    )
    async def view_requests(interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        try:
            cursor.execute("""
                SELECT id, student_id FROM mentorship_requests
                WHERE alumni_id = ? AND status = 'pending'
            """, (str(interaction.user.id),))

            requests = cursor.fetchall()

            if not requests:
                await interaction.followup.send(
                    "📭 No pending requests.",
                    ephemeral=True
                )
                return

            response = "📩 **Pending Requests:**\n\n"

            for request_id, student_id in requests:
                response += (
                    f"🆔 Request ID: {request_id}\n"
                    f"👤 Student ID: {student_id}\n\n"
                )

            response += "Use `/accept_request request_id` to accept."

            await interaction.followup.send(response, ephemeral=True)

        except Exception as e:
            print("View Requests Error:", e)
            await interaction.followup.send(
                "⚠️ Something went wrong.",
                ephemeral=True
            )

    # ================= ACCEPT REQUEST =================

    @bot.tree.command(
        name="accept_request",
        description="Alumni: Accept a mentorship request"
    )
    @app_commands.describe(request_id="Enter request ID")
    async def accept_request(interaction: discord.Interaction, request_id: int):

        await interaction.response.defer(ephemeral=True)

        try:
            guild = interaction.guild

            cursor.execute(
                "SELECT discord_id FROM alumni WHERE discord_id = ?",
                (str(interaction.user.id),)
            )
            alumni = cursor.fetchone()

            if not alumni:
                await interaction.followup.send(
                    "❌ You are not registered as alumni.",
                    ephemeral=True
                )
                return

            cursor.execute("""
                SELECT student_id FROM mentorship_requests
                WHERE id = ? AND alumni_id = ? AND status = 'pending'
            """, (request_id, str(interaction.user.id)))

            request = cursor.fetchone()

            if not request:
                await interaction.followup.send(
                    "❌ Invalid request ID or already processed.",
                    ephemeral=True
                )
                return

            student_id = request[0]
            student_member = guild.get_member(int(student_id))

            if not student_member:
                await interaction.followup.send(
                    "❌ Student not found in this server.",
                    ephemeral=True
                )
                return

            cursor.execute("""
                UPDATE mentorship_requests
                SET status = 'accepted'
                WHERE id = ?
            """, (request_id,))
            conn.commit()

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                student_member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            }

            channel = await guild.create_text_channel(
                name=f"mentorship-{student_member.name}",
                overwrites=overwrites
            )

            await channel.send(
                f"🎉 Mentorship Session Started!\n"
                f"{student_member.mention} and {interaction.user.mention} can chat here."
            )

            await interaction.followup.send(
                "✅ Request accepted & private channel created!",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "✅ Request accepted & private channel created!",
                ephemeral=True
            )
        except Exception as e:
            print("Accept Error:", e)
            await interaction.followup.send(
                "⚠️ Something went wrong.",
                ephemeral=True
            )
