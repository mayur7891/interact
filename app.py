from app import create_app  # ✅ Import socketio
from flask import jsonify, request
from app.model import CommentModel
from app.routes.ml_routes import ml_bp
from app.routes.comment_routes import comment_bp
from app.routes.video_routes import video_bp
from app.routes.auth_routes import user_bp
# from app.routes.socket_routes import socket_bp  # ✅ Import WebSocket routes



from flask_socketio import SocketIO, emit

app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*")
print("hello dvkdjvkxlkvlkxjvl")

@app.route("/api")
def get_data():
    records = CommentModel.get_comments_by_video(1)
    print(records)
    return jsonify({"message": "Hello from Flask!", "status": "success"})


# from app import socketio  # ✅ Use the globally initialized socketio instance
from app.services.preprocessing import preprocess_text, analyze_sentiment
from app.model import SentimentModel, CommentModel
import datetime
from datetime import timezone

@socketio.on("new_comment")
def handle_new_comment(data):
    """Handles new comments and emits to all users"""
    comment_text = data.get("comment_text")
    video_id = int(data.get("video_id"))
    user_id = data.get("user_id")

    print(video_id)
    print(comment_text)
    print(user_id)
    print(video_id)

    # if not comment_text or not video_id or not user_id:
    #     emit("error", {"message": "Missing required fields"}, broadcast=False)
    #     return

    try:
        # Process the comment
        embedding = preprocess_text(comment_text)
        sentiment = analyze_sentiment(comment_text)
        cluster = -1  # Default until clustering is applied
        timestamp = datetime.datetime.now(timezone.utc).isoformat()
        # Get existing sentiment stats
        sentiments = SentimentModel.get_sentiment_by_video_id(video_id)
        positive, negative, neutral = (sentiments or {}).get("positive", 0), (sentiments or {}).get("negative", 0), (sentiments or {}).get("neutral", 0)

        # Update sentiment counts
        if sentiment == "positive":
            positive += 1
        elif sentiment == "negative":
            negative += 1
        else:
            neutral += 1

        # Update sentiment in DB
        SentimentModel.add_sentiment(video_id, positive, negative, neutral)

        # Store comment in DB
        comment_id = CommentModel.add_comment(video_id, user_id, comment_text, embedding, cluster, sentiment,timestamp)
        # print(comment_id)

        # new_comment = CommentModel.get_comment_by_id(str(comment_id))
        new_comment = {
            "_id": str(comment_id),
            "user_id":user_id,
            "video_id":video_id,
            "comment": comment_text,
            "cluster":cluster,
            "sentiment":sentiment,
            "timestamp":timestamp,
            "replies":[]
        }
        print(new_comment)
        # Emit to all clients that a new comment is added
        emit("receive_comment", new_comment, broadcast=True)

    except Exception as e:
        print(e)
        emit("error", {"message": str(e)}, broadcast=False)

@socketio.on("new_reply")
def handle_new_reply(data):
    """Handles new replies and emits to all users"""
    comment_id = data.get("comment_id")
    reply_user_id = data.get("reply_user_id")
    reply_text = data.get("reply_text")
    timestamp = datetime.datetime.now(timezone.utc).isoformat()

    if not comment_id or not reply_user_id or not reply_text:
        emit("error", {"message": "Missing required fields"}, broadcast=False)
        return

    try:
        # Store reply in DB
        success = CommentModel.add_reply(comment_id, reply_user_id, reply_text, timestamp)

        # Emit new reply correctly
        emit("receive_reply", {
            "_id": str(success),  # Store correct reply ID
            "comment_id": comment_id,
            "reply_user_id": reply_user_id,
            "reply_text": reply_text,
            "timestamp": timestamp
        }, broadcast=True)

    except Exception as e:
        emit("error", {"message": str(e)}, broadcast=False)


# Register Blueprints
app.register_blueprint(ml_bp, url_prefix="/ml")
app.register_blueprint(comment_bp, url_prefix="/comments")
app.register_blueprint(video_bp, url_prefix='/video')
app.register_blueprint(user_bp, url_prefix='/auth')
# app.register_blueprint(socket_bp, url_prefix='/ws')  # ✅ Register WebSocket routes

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True) # ✅ Start WebSockets properly
