from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
# from flask_socketio import SocketIO
from app.config import Config

# Initialize extensions
mongo = PyMongo()
# socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    """Flask application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize plugins
    mongo.init_app(app)
    CORS(app)
    # socketio.init_app(app)

    # Register Blueprints
    # from app.routes.auth_routes import auth_bp
    # from app.routes.comment_routes import comment_bp
    # from app.routes.ml_routes import ml_bp

    # app.register_blueprint(auth_bp, url_prefix="/auth")
    # app.register_blueprint(comment_bp, url_prefix="/comments")
    # app.register_blueprint(ml_bp, url_prefix="/ml")

    return app
