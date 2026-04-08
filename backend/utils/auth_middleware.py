from functools import wraps
from flask import request, jsonify
import jwt
from config import Config


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from headers
        if "Authorization" in request.headers:
            token = request.headers["Authorization"]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            # Decode token
            data = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
            request.user = data  # attach user info to request

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401

        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated
