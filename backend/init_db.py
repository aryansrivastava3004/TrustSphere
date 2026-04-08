import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    user_id TEXT UNIQUE,
    bio TEXT,
    password TEXT,
    role TEXT,
    rating REAL DEFAULT 0,
    total_reviews INTEGER DEFAULT 0,
    trust_score REAL DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reviewer_id INTEGER,
    reviewed_user_id INTEGER,
    rating INTEGER,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seeker_id INTEGER,
    collaborator_id INTEGER,
    service TEXT,
    price REAL,
    status TEXT DEFAULT 'pending'
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS disputes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER,
    user1_id INTEGER,
    user2_id INTEGER,
    reason TEXT,
    status TEXT DEFAULT 'open',
    admin_decision TEXT
)
""")

conn.commit()
conn.close()

print("Database ready ✅")
