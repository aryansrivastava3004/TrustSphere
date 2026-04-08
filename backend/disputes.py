from flask import Blueprint, request, jsonify
import sqlite3
from config import Config
from auth_middleware import token_required  # Fixed: flat import, not utils.auth_middleware

dispute_bp = Blueprint("disputes", __name__)


@dispute_bp.route("/raise", methods=["POST"])
@token_required
def raise_dispute():
    data = request.json
    if not data or not all(k in data for k in ("request_id", "user2_id", "reason")):
        return jsonify({"error": "Missing fields"}), 400

    # Prevent raising a dispute against yourself
    if int(data["user2_id"]) == request.user["id"]:
        return jsonify({"error": "You cannot raise a dispute against yourself"}), 400

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

    # FIX: Verify the request exists and the current user is part of it
    cur.execute("SELECT seeker_id, collaborator_id FROM requests WHERE id=?", (data["request_id"],))
    req = cur.fetchone()
    if not req:
        conn.close()
        return jsonify({"error": "Request not found"}), 404

    if request.user["id"] not in (req[0], req[1]):
        conn.close()
        return jsonify({"error": "You are not part of this request"}), 403

    # FIX: Verify user2 exists
    cur.execute("SELECT id FROM users WHERE id=?", (data["user2_id"],))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "Target user not found"}), 404

    cur.execute("""
    INSERT INTO disputes (request_id, user1_id, user2_id, reason)
    VALUES (?, ?, ?, ?)
    """, (data["request_id"], request.user["id"], data["user2_id"], data["reason"]))

    conn.commit()
    conn.close()

    return jsonify({"msg": "Dispute raised"})


@dispute_bp.route("/my", methods=["GET"])
@token_required
def my_disputes():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
    SELECT d.*, u1.name as user1_name, u2.name as user2_name
    FROM disputes d
    JOIN users u1 ON d.user1_id = u1.id
    JOIN users u2 ON d.user2_id = u2.id
    WHERE d.user1_id=? OR d.user2_id=?
    ORDER BY d.id DESC
    """, (request.user["id"], request.user["id"]))

    disputes = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(disputes)
