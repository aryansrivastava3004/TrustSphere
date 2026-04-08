from flask import Blueprint, request, jsonify
import sqlite3
from config import Config
from utils.auth_middleware import token_required

request_bp = Blueprint("requests", __name__)


@request_bp.route("/create", methods=["POST"])
@token_required
def create_request():
    data = request.json
    if not data or not all(k in data for k in ("collaborator_id", "service", "price")):
        return jsonify({"error": "Missing fields"}), 400

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

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

    allowed_statuses = ["pending", "accepted", "rejected", "completed"]
    if data["status"] not in allowed_statuses:
        return jsonify({"error": f"Status must be one of {allowed_statuses}"}), 400

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

    # Only the collaborator or seeker involved can update
    cur.execute("SELECT seeker_id, collaborator_id FROM requests WHERE id=?", (id,))
    req = cur.fetchone()
    if not req:
        conn.close()
        return jsonify({"error": "Request not found"}), 404

    if request.user["id"] not in (req[0], req[1]):
        conn.close()
        return jsonify({"error": "Unauthorized"}), 403

    cur.execute("UPDATE requests SET status=? WHERE id=?", (data["status"], id))
    conn.commit()
    conn.close()

    return jsonify({"msg": "Request updated"})
