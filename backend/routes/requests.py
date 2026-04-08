from flask import Blueprint, request, jsonify
import sqlite3

review_bp = Blueprint("reviews", __name__)

@review_bp.route("/add", methods=["POST"])
def add_review():
    data = request.json

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO reviews (reviewer_id, reviewed_user_id, rating, comment)
    VALUES (?, ?, ?, ?)
    """, (data["reviewer_id"], data["user_id"], data["rating"], data["comment"]))

    # UPDATE TRUST
    cur.execute("SELECT rating, total_reviews FROM users WHERE id=?", (data["user_id"],))
    user = cur.fetchone()

    new_reviews = user[1] + 1
    new_rating = ((user[0] * user[1]) + data["rating"]) / new_reviews
    trust_score = new_rating * 20

    cur.execute("""
    UPDATE users SET rating=?, total_reviews=?, trust_score=?
    WHERE id=?
    """, (new_rating, new_reviews, trust_score, data["user_id"]))

    conn.commit()
    conn.close()

    return jsonify({"msg": "Review added"})
