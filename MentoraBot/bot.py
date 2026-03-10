import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os

# database
from database import cursor, conn

# ------------------ LOAD ENV ------------------

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# ------------------ INTENTS ------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------ SETUP HOOK (LOAD EXTENSIONS + SYNC) ------------------

@bot.event
async def setup_hook():

    try:
        await bot.load_extension("commands.matching")
        await bot.load_extension("commands.ai_chat")
        await bot.load_extension("commands.career_ai")
        await bot.load_extension("commands.session_ai")
        await bot.load_extension("commands.resume_ai")
        await bot.load_extension("commands.interview_ai")
        await bot.load_extension("commands.admin_dashboard")
        await bot.load_extension("commands.weekly_report")

        print("Extensions Loaded")

    except Exception as e:
        print("Extension loading error:", e)

    # force slash command sync
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print("Sync failed:", e)

# ------------------ BOT READY ------------------

@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

# ------------------ REGISTER STUDENT ------------------

@bot.tree.command(name="register_student", description="Register as a student")
@app_commands.describe(
    name="Your Name",
    department="Your Department",
    year="Your Year",
    interests="Career Interests (comma separated)",
    skills="Your Skills (comma separated)"
)
async def register_student(interaction: discord.Interaction,
                           name: str,
                           department: str,
                           year: str,
                           interests: str,
                           skills: str):

    clean_interests = interests.lower().replace(" ", "")
    clean_skills = skills.lower().replace(" ", "")

    cursor.execute("""
        REPLACE INTO students
        (discord_id, name, department, year, interests, skills)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (str(interaction.user.id), name, department, year,
          clean_interests, clean_skills))

    conn.commit()

    role = discord.utils.get(interaction.guild.roles, name="student")

    if role:
        await interaction.user.add_roles(role)

    await interaction.response.send_message(
        "✅ Student Registered Successfully!",
        ephemeral=True
    )

# ------------------ REGISTER ALUMNI ------------------

@bot.tree.command(name="register_alumni", description="Register as an alumni")
@app_commands.describe(
    name="Your Name",
    graduation_year="Graduation Year",
    job_role="Current Job Role",
    industry="Industry You Work In",
    skills="Your Skills (comma separated)"
)
async def register_alumni(interaction: discord.Interaction,
                          name: str,
                          graduation_year: str,
                          job_role: str,
                          industry: str,
                          skills: str):

    clean_job = job_role.lower()
    clean_industry = industry.lower()
    clean_skills = skills.lower().replace(" ", "")

    cursor.execute("""
        REPLACE INTO alumni
        (discord_id, name, graduation_year, job_role, industry, skills)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (str(interaction.user.id), name, graduation_year,
          clean_job, clean_industry, clean_skills))

    conn.commit()

    alumni_role = discord.utils.get(interaction.guild.roles, name="alumni")
    student_role = discord.utils.get(interaction.guild.roles, name="student")

    if alumni_role:
        await interaction.user.add_roles(alumni_role)

    if student_role and student_role in interaction.user.roles:
        await interaction.user.remove_roles(student_role)

    await interaction.response.send_message(
        "✅ Alumni Registered Successfully!",
        ephemeral=True
    )

# ------------------ SET AVAILABILITY ------------------

@bot.tree.command(name="set_availability", description="Alumni: Set your availability")
@app_commands.describe(status="True = Available, False = Busy")
async def set_availability(interaction: discord.Interaction, status: bool):

    cursor.execute(
        "SELECT * FROM alumni WHERE discord_id = ?",
        (str(interaction.user.id),)
    )

    alumni = cursor.fetchone()

    if not alumni:
        await interaction.response.send_message(
            "✅ Alumni Registered Successfully!",
            ephemeral=True
        )
        return

    availability_value = 1 if status else 0

    cursor.execute(
        "UPDATE alumni SET availability = ? WHERE discord_id = ?",
        (availability_value, str(interaction.user.id))
    )

    conn.commit()

    message = "🟢 You are now AVAILABLE." if status else "🔴 You are now BUSY."

    await interaction.response.send_message(message, ephemeral=True)

# ------------------ BASIC FIND MENTOR ------------------

@bot.tree.command(name="find_mentor_basic", description="Find available alumni using role, industry or skills")
@app_commands.describe(interest="Your Career Interest")
async def find_mentor_basic(interaction: discord.Interaction, interest: str):

    search = interest.lower()

    cursor.execute("""
        SELECT name, graduation_year, job_role, industry, skills
        FROM alumni
        WHERE availability = 1
        AND (
            LOWER(job_role) LIKE ?
            OR LOWER(industry) LIKE ?
            OR LOWER(skills) LIKE ?
        )
    """, (f"%{search}%", f"%{search}%", f"%{search}%"))

    results = cursor.fetchall()

    if not results:
        await interaction.response.send_message(
            "❌ No available matching alumni found.",
            ephemeral=True
        )
        return

    response = "🎓 **Available Matching Alumni:**\n\n"

    for alum in results:
        response += (
            f"👤 Name: {alum[0]}\n"
            f"🎓 Batch: {alum[1]}\n"
            f"💼 Role: {alum[2]}\n"
            f"🏢 Industry: {alum[3]}\n"
            f"🛠 Skills: {alum[4]}\n\n"
        )

    await interaction.response.send_message(response, ephemeral=True)

# ------------------ RUN BOT ------------------

bot.run(TOKEN)