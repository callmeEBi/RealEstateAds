import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if SECRET_KEY is None:
        # In production, we require a secret key to be set.
        # For development, we provide a fallback but warn.
        if os.environ.get("FLASK_ENV") == "production":
            raise ValueError(
                "SECRET_KEY must be set in environment for production. "
                "Generate one with: python -c 'import os; print(os.urandom(24).hex())'"
            )
        else:
            # Development fallback (still better than a hardcoded default)
            SECRET_KEY = os.urandom(24).hex()
            print(
                "WARNING: No SECRET_KEY set; using a random one for this session. "
                "Set a fixed SECRET_KEY in .env for consistent sessions."
            )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///app.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

