from flask import Blueprint, request, jsonify
import sqlite3
from config import Config
from utils.auth_middleware import token_required

review_bp = Blueprint("reviews", __name__)


@review_bp.route("/add", methods=["POST"])
@token_required
def add_review():
    data = request.json

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO reviews (reviewer_id, reviewed_user_id, rating, comment)
    VALUES (?, ?, ?, ?)
    """, (request.user["id"], data["user_id"], data["rating"], data["comment"]))

    cur.execute("SELECT rating, total_reviews FROM users WHERE id=?", (data["user_id"],))
    user = cur.fetchone()

    new_total = user[1] + 1
    new_rating = ((user[0] * user[1]) + data["rating"]) / new_total
    trust_score = round(new_rating * 20, 2)

    cur.execute("""
    UPDATE users SET rating=?, total_reviews=?, trust_score=?
    WHERE id=?
    """, (new_rating, new_total, trust_score, data["user_id"]))

    conn.commit()
    conn.close()

    return jsonify({"msg": "Review added"})
