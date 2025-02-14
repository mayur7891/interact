import os

class Config:
    """Configuration settings for the Flask app."""

    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

    # MongoDB settings (Use environment variables for security)
    MONGO_USER = os.getenv("MONGO_USER", "mayur")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "mayur7891")
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = os.getenv("MONGO_PORT", "27017")
    MONGO_DBNAME = os.getenv("MONGO_DBNAME", "dummy")

    # Construct the MongoDB URI
    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DBNAME}"

    # Debug mode (set to False in production)
    DEBUG = True
