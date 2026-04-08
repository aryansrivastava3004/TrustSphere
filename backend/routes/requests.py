from flask import Blueprint, request, jsonify
import sqlite3
from config import Config
from utils.auth_middleware import token_required

request_bp = Blueprint("requests", __name__)


@request_bp.route("/create", methods=["POST"])
@token_required
def create_request():
    data = request.json

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO requests (seeker_id, collaborator_id, service, price)
    VALUES (?, ?, ?, ?)
    """, (request.user["id"], data["collaborator_id"], data["service"], data["price"]))

    conn.commit()
    conn.close()

    return jsonify({"msg": "Request sent"})


@request_bp.route("/update/<int:id>", methods=["POST"])
@token_required
def update_request(id):
    data = request.json

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

    cur.execute("UPDATE requests SET status=? WHERE id=?", (data["status"], id))

    conn.commit()
    conn.close()

    return jsonify({"msg": "Request updated"})
