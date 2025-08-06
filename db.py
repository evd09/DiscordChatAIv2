import sqlite3

DB_FILE = "data/botdata.db"

def connect():
    return sqlite3.connect(DB_FILE)

def setup():
    with connect() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS user_personality (
                guild_id TEXT,
                user_id TEXT,
                persona TEXT,
                PRIMARY KEY (guild_id, user_id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS trivia_scores (
                guild_id TEXT,
                user_id TEXT,
                correct INTEGER DEFAULT 0,
                wrong INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )
        """)
        conn.commit()

def set_persona(guild_id, user_id, persona):
    with connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO user_personality (guild_id, user_id, persona) VALUES (?, ?, ?)",
            (guild_id, user_id, persona)
        )
        conn.commit()

def get_persona(guild_id, user_id):
    with connect() as conn:
        row = conn.execute(
            "SELECT persona FROM user_personality WHERE guild_id=? AND user_id=?",
            (guild_id, user_id)
        ).fetchone()
        return row[0] if row else "friendly"

def set_trivia_score(guild_id, user_id, correct, wrong):
    with connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO trivia_scores (guild_id, user_id, correct, wrong) VALUES (?, ?, ?, ?)",
            (guild_id, user_id, correct, wrong)
        )
        conn.commit()

def get_trivia_score(guild_id, user_id):
    with connect() as conn:
        row = conn.execute(
            "SELECT correct, wrong FROM trivia_scores WHERE guild_id=? AND user_id=?",
            (guild_id, user_id)
        ).fetchone()
        return (row[0], row[1]) if row else (0, 0)

def get_leaderboard(guild_id):
    with connect() as conn:
        return conn.execute(
            "SELECT user_id, correct, wrong FROM trivia_scores WHERE guild_id=?",
            (guild_id,)
        ).fetchall()

setup()
