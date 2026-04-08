from flask import Blueprint, request, jsonify
import sqlite3
from config import Config
from utils.auth_middleware import token_required

review_bp = Blueprint("reviews", __name__)


@review_bp.route("/add", methods=["POST"])
@token_required
def add_review():
    data = request.json
    if not data or not all(k in data for k in ("user_id", "rating", "comment")):
        return jsonify({"error": "Missing fields"}), 400

    rating = int(data["rating"])
    if not (1 <= rating <= 5):
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO reviews (reviewer_id, reviewed_user_id, rating, comment)
    VALUES (?, ?, ?, ?)
    """, (request.user["id"], data["user_id"], rating, data["comment"]))

    cur.execute("SELECT rating, total_reviews FROM users WHERE id=?", (data["user_id"],))
    user = cur.fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    new_total = user[1] + 1
    new_rating = ((user[0] * user[1]) + rating) / new_total
    trust_score = round(new_rating * 20, 2)  # Maps 1–5 → 20–100

    cur.execute("""
    UPDATE users SET rating=?, total_reviews=?, trust_score=?
    WHERE id=?
    """, (new_rating, new_total, trust_score, data["user_id"]))

    conn.commit()
    conn.close()

    return jsonify({"msg": "Review added", "new_trust_score": trust_score})


@review_bp.route("/user/<int:user_id>", methods=["GET"])
def get_reviews(user_id):
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
    SELECT r.*, u.name as reviewer_name
    FROM reviews r
    JOIN users u ON r.reviewer_id = u.id
    WHERE r.reviewed_user_id=?
    ORDER BY r.created_at DESC
    """, (user_id,))

    reviews = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(reviews)
