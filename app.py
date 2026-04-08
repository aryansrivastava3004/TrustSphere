from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import sqlite3
import os

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Auto-initialize database on startup (needed for Render/cloud deployments)
def init_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, user_id TEXT UNIQUE,
        bio TEXT, password TEXT, role TEXT, rating REAL DEFAULT 0,
        total_reviews INTEGER DEFAULT 0, trust_score REAL DEFAULT 0)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT, reviewer_id INTEGER,
        reviewed_user_id INTEGER, rating INTEGER, comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT, seeker_id INTEGER,
        collaborator_id INTEGER, service TEXT, price REAL, status TEXT DEFAULT 'pending')""")
    cur.execute("""CREATE TABLE IF NOT EXISTS disputes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, request_id INTEGER,
        user1_id INTEGER, user2_id INTEGER, reason TEXT,
        status TEXT DEFAULT 'open', admin_decision TEXT)""")
    conn.commit()
    conn.close()

init_db()

# Import routes (flat structure — no routes/ subfolder needed)
from auth import auth_bp
from reviews import review_bp
from collab_requests import request_bp
from disputes import dispute_bp
from users import user_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(review_bp, url_prefix="/api/reviews")
app.register_blueprint(request_bp, url_prefix="/api/requests")
app.register_blueprint(dispute_bp, url_prefix="/api/disputes")
app.register_blueprint(user_bp, url_prefix="/api/users")

@app.route("/")
def home():
    return jsonify({"message": "Backend running 🚀"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
