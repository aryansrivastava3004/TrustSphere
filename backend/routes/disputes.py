from flask import Blueprint, request, jsonify
import sqlite3
from config import Config
from utils.auth_middleware import token_required

dispute_bp = Blueprint("disputes", __name__)


@dispute_bp.route("/raise", methods=["POST"])
@token_required
def raise_dispute():
    data = request.json

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO disputes (request_id, user1_id, user2_id, reason)
    VALUES (?, ?, ?, ?)
    """, (data["request_id"], request.user["id"], data["user2_id"], data["reason"]))

    conn.commit()
    conn.close()

    return jsonify({"msg": "Dispute raised"})
