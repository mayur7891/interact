import os
from app import create_app, socketio
from flask import jsonify
from app.routes.ml_routes import ml_bp
from app.routes.comment_routes import comment_bp
from app.routes.video_routes import video_bp
from app.routes.auth_routes import user_bp

app = create_app()

@app.route("/api")
def get_data():
    return jsonify({"message": "Hello from Flask!", "status": "success"})

# Register Blueprints
app.register_blueprint(ml_bp, url_prefix="/ml")
app.register_blueprint(comment_bp, url_prefix="/comments")
app.register_blueprint(video_bp, url_prefix='/video')
app.register_blueprint(user_bp, url_prefix='/auth')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # Cloud Run requires port 8080
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)  # Fix SocketIO issues
