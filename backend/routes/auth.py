from flask import Blueprint, request, jsonify
import sqlite3
import bcrypt
import jwt
import datetime

auth_bp = Blueprint("auth", __name__)
SECRET = "secret123"

# REGISTER
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO users (name, user_id, bio, password, role)
        VALUES (?, ?, ?, ?, ?)
        """, (data["name"], data["user_id"], data["bio"], hashed, data["role"]))

        conn.commit()
    except:
        return jsonify({"error": "User exists"}), 400

    conn.close()
    return jsonify({"msg": "Registered"})

# LOGIN
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE user_id=?", (data["user_id"],))
    user = cur.fetchone()

    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.checkpw(data["password"].encode(), user[4]):
        return jsonify({"error": "Wrong password"}), 401

    token = jwt.encode(
        {"id": user[0], "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)},
        SECRET,
        algorithm="HS256"
    )

    return jsonify({"token": token})
