from functools import wraps
from flask import request, jsonify
import jwt
from config import Config


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Token missing"}), 401

        # Strip "Bearer " prefix if present
        if token.startswith("Bearer "):
            token = token[7:]

        try:
            data = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
            request.user = data
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated
