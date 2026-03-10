import sqlite3

# Enable foreign key support
conn = sqlite3.connect("database.db", check_same_thread=False)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()


def setup_database():

    # ---------------- STUDENTS TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        discord_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT,
        year TEXT,
        interests TEXT,
        skills TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ---------------- ALUMNI TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alumni (
        discord_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        graduation_year TEXT,
        job_role TEXT,
        industry TEXT,
        skills TEXT,
        linkedin TEXT,
        availability INTEGER DEFAULT 1 CHECK(availability IN (0,1)),
        rating REAL DEFAULT 0,
        total_sessions INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ---------------- MENTORSHIP REQUESTS ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mentorship_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        alumni_id TEXT NOT NULL,
        status TEXT DEFAULT 'pending'
            CHECK(status IN ('pending','accepted','rejected')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(student_id) REFERENCES students(discord_id) ON DELETE CASCADE,
        FOREIGN KEY(alumni_id) REFERENCES alumni(discord_id) ON DELETE CASCADE
    )
    """)

    # ---------------- RATINGS TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumni_id TEXT NOT NULL,
        student_id TEXT NOT NULL,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        feedback TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(alumni_id) REFERENCES alumni(discord_id) ON DELETE CASCADE,
        FOREIGN KEY(student_id) REFERENCES students(discord_id) ON DELETE CASCADE
    )
    """)

    # ---------------- MESSAGES TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        username TEXT,
        channel_name TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ---------------- AI CLASSIFIED MESSAGE LOGS ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS message_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        role TEXT,
        channel_name TEXT,
        message TEXT,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ---------------- INDEXES ----------------
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alumni_role ON alumni(job_role)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alumni_industry ON alumni(industry)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alumni_skills ON alumni(skills)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alumni_availability ON alumni(availability)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_interest ON students(interests)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_requests_status ON mentorship_requests(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ratings_alumni ON ratings(alumni_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_category ON message_logs(category)")

    conn.commit()


def close_database():
    conn.commit()
    conn.close()


# Run automatically
setup_database()
