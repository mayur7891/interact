from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from app.config import Config
from app.utils.db_utils import MongoDB

mongo = MongoDB()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")


def create_app():
    """Flask application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize MongoDB with connection pooling, retries, and indexes
    mongo.init_app(app)
    if not mongo.ping():
        print("WARNING: MongoDB connection failed! Check your URI.")

    CORS(app)
    jwt.init_app(app)
    socketio.init_app(app)

    # Register blueprints inside factory to avoid circular imports
    from app.routes.auth_routes import user_bp
    from app.routes.comment_routes import comment_bp
    from app.routes.video_routes import video_bp
    from app.routes.ml_routes import ml_bp
    from app.sockets import events  # noqa: F401 - registers socket handlers

    app.register_blueprint(ml_bp, url_prefix="/ml")
    app.register_blueprint(comment_bp, url_prefix="/comments")
    app.register_blueprint(video_bp, url_prefix="/video")
    app.register_blueprint(user_bp, url_prefix="/auth")

    return app
