import sqlite3, os

BASE = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE, "data", "health.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS reports(
        ward TEXT,
        rainfall REAL,
        ph REAL,
        turbidity REAL,
        cases INTEGER,
        risk TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_report(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO reports VALUES (?,?,?,?,?,?)", data)
    conn.commit()
    conn.close()

def get_reports():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    rows = c.execute("SELECT * FROM reports").fetchall()
    conn.close()
    return rows