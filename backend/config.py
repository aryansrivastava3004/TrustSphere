import os

class Config:
    # -------------------------------
    # SECRET KEYS
    # -------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey123")
    JWT_SECRET = os.environ.get("JWT_SECRET", "secret123")

    # -------------------------------
    # DATABASE (SQLite)
    # -------------------------------
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, "database.db")

    # -------------------------------
    # DEBUG MODE
    # -------------------------------
    DEBUG = True
