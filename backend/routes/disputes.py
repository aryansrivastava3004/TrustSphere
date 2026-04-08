from flask import Blueprint, request, jsonify
import sqlite3

dispute_bp = Blueprint("disputes", __name__)

@dispute_bp.route("/raise", methods=["POST"])
def raise_dispute():
    data = request.json

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO disputes (request_id, user1_id, user2_id, reason)
    VALUES (?, ?, ?, ?)
    """, (data["request_id"], data["user1_id"], data["user2_id"], data["reason"]))

    conn.commit()
    conn.close()

    return jsonify({"msg": "Dispute raised"})
