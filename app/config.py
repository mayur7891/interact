import os

class Config:
    """Configuration settings for the Flask app."""
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    JWT_SECRET_KEY = "your_jwt_secret_key_here"
    MONGO_URI = "mongodb+srv://Ash781:mayur123@dummy.76pbm.mongodb.net/dummy?retryWrites=true&w=majority"

