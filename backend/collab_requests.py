from flask import Blueprint, request, jsonify
import sqlite3
from config import Config
from auth_middleware import token_required  # Fixed: flat import, not utils.auth_middleware

request_bp = Blueprint("requests", __name__)


@request_bp.route("/create", methods=["POST"])
@token_required
def create_request():
    data = request.json
    if not data or not all(k in data for k in ("collaborator_id", "service", "price")):
        return jsonify({"error": "Missing fields"}), 400

    # Prevent requesting yourself
    if int(data["collaborator_id"]) == request.user["id"]:
        return jsonify({"error": "You cannot send a request to yourself"}), 400

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

    # Verify collaborator exists
    cur.execute("SELECT id FROM users WHERE id=? AND role='collaborator'", (data["collaborator_id"],))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "Collaborator not found"}), 404

    cur.execute("""
    INSERT INTO requests (seeker_id, collaborator_id, service, price)
    VALUES (?, ?, ?, ?)
    """, (request.user["id"], data["collaborator_id"], data["service"], data["price"]))

    conn.commit()
    req_id = cur.lastrowid
    conn.close()

    return jsonify({"msg": "Request sent", "id": req_id})


@request_bp.route("/my", methods=["GET"])
@token_required
def my_requests():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
    SELECT req.*, 
           s.name as seeker_name, s.user_id as seeker_uid,
           c.name as collaborator_name, c.user_id as collaborator_uid
    FROM requests req
    JOIN users s ON req.seeker_id = s.id
    JOIN users c ON req.collaborator_id = c.id
    WHERE req.seeker_id=? OR req.collaborator_id=?
    ORDER BY req.id DESC
    """, (request.user["id"], request.user["id"]))

    reqs = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(reqs)


@request_bp.route("/update/<int:id>", methods=["POST"])
@token_required
def update_request(id):
    data = request.json
    if not data or "status" not in data:
        return jsonify({"error": "Missing status"}), 400

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

    cur.execute("SELECT seeker_id, collaborator_id, status FROM requests WHERE id=?", (id,))
    req = cur.fetchone()
    if not req:
        conn.close()
        return jsonify({"error": "Request not found"}), 404

    seeker_id, collaborator_id, current_status = req
    user_id = request.user["id"]
    new_status = data["status"]

    # FIX: Role-based status transitions
    # Collaborator can accept or reject a pending request
    if new_status in ("accepted", "rejected"):
        if user_id != collaborator_id:
            conn.close()
            return jsonify({"error": "Only the collaborator can accept or reject requests"}), 403
        if current_status != "pending":
            conn.close()
            return jsonify({"error": "Only pending requests can be accepted or rejected"}), 400

    # Either party can mark as completed once accepted
    elif new_status == "completed":
        if user_id not in (seeker_id, collaborator_id):
            conn.close()
            return jsonify({"error": "Unauthorized"}), 403
        if current_status != "accepted":
            conn.close()
            return jsonify({"error": "Only accepted requests can be marked as completed"}), 400

    else:
        conn.close()
        return jsonify({"error": "Invalid status. Allowed: accepted, rejected, completed"}), 400

    cur.execute("UPDATE requests SET status=? WHERE id=?", (new_status, id))
    conn.commit()
    conn.close()

    return jsonify({"msg": "Request updated"})
