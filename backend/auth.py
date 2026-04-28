from flask import Blueprint, request, jsonify
import sqlite3
import bcrypt
import jwt
import datetime
from config import Config

auth_bp = Blueprint("auth", __name__)

SECRET = Config.JWT_SECRET


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        if not data or not all(k in data for k in ("name", "user_id", "bio", "password", "role")):
            return jsonify({"error": "Missing required fields"}), 400

        hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()

        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO users (name, user_id, bio, password, role)
        VALUES (?, ?, ?, ?, ?)
        """, (data["name"], data["user_id"], data["bio"], hashed, data["role"]))

        conn.commit()
        conn.close()

        return jsonify({"msg": "Registered successfully"})

    except sqlite3.IntegrityError:
        return jsonify({"error": "User ID already exists"}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data or not all(k in data for k in ("user_id", "password")):
        return jsonify({"error": "Missing credentials"}), 400

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE user_id=?", (data["user_id"],))
    user = cur.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.checkpw(data["password"].encode(), user[4].encode()):
        return jsonify({"error": "Wrong password"}), 401

    token = jwt.encode(
        {
            "id": user[0],
            "user_id": user[2],
            "name": user[1],
            "role": user[5],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
        },
        SECRET,
        algorithm="HS256"
    )

    return jsonify({
        "token": token,
        "user": {
            "id": user[0],
            "name": user[1],
            "user_id": user[2],
            "bio": user[3],
            "role": user[5],
            "rating": user[6],
            "total_reviews": user[7],
            "trust_score": user[8]
        }
    })
