from flask import Blueprint, jsonify
import sqlite3
from config import Config

user_bp = Blueprint("users", __name__)


# -------------------------------
# GET ALL USERS
# -------------------------------
@user_bp.route("/", methods=["GET"])
def get_users():
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT * FROM users")
        users = [dict(row) for row in cur.fetchall()]

        conn.close()

        return jsonify(users)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------
# GET SINGLE USER PROFILE
# -------------------------------
@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = cur.fetchone()

        conn.close()

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify(dict(user))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------
# GET COLLABORATORS (SELLERS)
# -------------------------------
@user_bp.route("/collaborators", methods=["GET"])
def get_collaborators():
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
        SELECT * FROM users
        WHERE role='collaborator'
        ORDER BY trust_score DESC
        """)

        users = [dict(row) for row in cur.fetchall()]

        conn.close()

        return jsonify(users)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
