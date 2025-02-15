from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from app.config import Config

# Initialize extensions globally
mongo = PyMongo()
bcrypt = Bcrypt()
jwt = JWTManager()
  # ✅ Allow CORS for WebSockets


def create_app():
    """Flask application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize plugins
    mongo.init_app(app)
    bcrypt.init_app(app)
    CORS(app)
    jwt.init_app(app)
 

    return app
