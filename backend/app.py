from flask import Flask, jsonify
from flask_cors import CORS
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Import routes (flat structure — no routes/ subfolder needed)
from auth import auth_bp
from reviews import review_bp
from collab_requests import request_bp
from disputes import dispute_bp
from users import user_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(review_bp, url_prefix="/api/reviews")
app.register_blueprint(request_bp, url_prefix="/api/requests")
app.register_blueprint(dispute_bp, url_prefix="/api/disputes")
app.register_blueprint(user_bp, url_prefix="/api/users")

@app.route("/")
def home():
    return jsonify({"message": "Backend running 🚀"})

if __name__ == "__main__":
    app.run(debug=True)
