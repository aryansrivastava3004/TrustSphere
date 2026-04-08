from flask import Blueprint, request, jsonify
import sqlite3
from config import Config

review_bp = Blueprint("reviews", __name__)


# -------------------------------
# ADD REVIEW
# -------------------------------
@review_bp.route("/add", methods=["POST"])
def add_review():
    try:
        data = request.json

        reviewer_id = data.get("reviewer_id")
        reviewed_user_id = data.get("user_id")
        rating = data.get("rating")
        comment = data.get("comment")

        if not all([reviewer_id, reviewed_user_id, rating]):
            return jsonify({"error": "Missing fields"}), 400

        conn = sqlite3.connect(Config.DATABASE_PATH)
        cur = conn.cursor()

        # Insert review
        cur.execute("""
        INSERT INTO reviews (reviewer_id, reviewed_user_id, rating, comment)
        VALUES (?, ?, ?, ?)
        """, (reviewer_id, reviewed_user_id, rating, comment))

        # Get current user rating
        cur.execute("""
        SELECT rating, total_reviews FROM users WHERE id=?
        """, (reviewed_user_id,))
        user = cur.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Calculate new rating
        new_total = user[1] + 1
        new_rating = ((user[0] * user[1]) + rating) / new_total

        # Simple trust score logic
        trust_score = round(new_rating * 20, 2)

        # Update user
        cur.execute("""
        UPDATE users
        SET rating=?, total_reviews=?, trust_score=?
        WHERE id=?
        """, (new_rating, new_total, trust_score, reviewed_user_id))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Review added successfully ✅",
            "new_rating": new_rating,
            "trust_score": trust_score
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------
# GET REVIEWS OF A USER
# -------------------------------
@review_bp.route("/user/<int:user_id>", methods=["GET"])
def get_reviews(user_id):
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
        SELECT * FROM reviews WHERE reviewed_user_id=?
        """, (user_id,))

        reviews = [dict(row) for row in cur.fetchall()]

        conn.close()

        return jsonify(reviews)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
