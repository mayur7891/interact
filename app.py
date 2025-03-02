from app import create_app 
from flask import jsonify, request
from app.routes.ml_routes import ml_bp
from app.routes.comment_routes import comment_bp
from app.routes.video_routes import video_bp
from app.routes.auth_routes import user_bp
from flask_socketio import SocketIO, emit
from app.services.preprocessing import preprocess_text, analyze_sentiment
from app.model import SentimentModel, CommentModel
import datetime
from datetime import timezone


from app import socketio

app = create_app()

# socketio = SocketIO(app, cors_allowed_origins="*")
# print("hello dvkdjvkxlkvlkxjvl")

@app.route("/api")
def get_data():
    return jsonify({"message": "Hello from Flask!", "status": "success"})


# @socketio.on("new_comment")
# def handle_new_comment(data):
#     """Handles new comments and emits to all users"""
#     comment_text = data.get("comment_text")
#     video_id = int(data.get("video_id"))
#     user_id = data.get("user_id")

#     try:
#         # Process the comment
#         embedding = preprocess_text(comment_text)
#         sentiment = analyze_sentiment(comment_text)
#         cluster = -1  # Default until clustering is applied
#         timestamp = datetime.datetime.now(timezone.utc).isoformat()
#         # Get existing sentiment stats
#         sentiments = SentimentModel.get_sentiment_by_video_id(video_id)
#         positive, negative, neutral = (sentiments or {}).get("positive", 0), (sentiments or {}).get("negative", 0), (sentiments or {}).get("neutral", 0)

#         # Update sentiment counts
#         if sentiment == "positive":
#             positive += 1
#         elif sentiment == "negative":
#             negative += 1
#         else:
#             neutral += 1

#         # Update sentiment in DB
#         SentimentModel.add_sentiment(video_id, positive, negative, neutral)

#         # Store comment in DB
#         comment_id = CommentModel.add_comment(video_id, user_id, comment_text, embedding, cluster, sentiment,timestamp)
#         # print(comment_id)

#         # new_comment = CommentModel.get_comment_by_id(str(comment_id))
#         new_comment = {
#             "_id": str(comment_id),
#             "user_id":user_id,
#             "video_id":video_id,
#             "comment": comment_text,
#             "cluster":cluster,
#             "sentiment":sentiment,
#             "timestamp":timestamp,
#             "replies":[]
#         }
#         print(new_comment)
#         # Emit to all clients that a new comment is added
#         emit("receive_comment", new_comment, broadcast=True)

#     except Exception as e:
#         print(e)
#         emit("error", {"message": str(e)}, broadcast=False)

# @socketio.on("new_reply")
# def handle_new_reply(data):
#     """Handles new replies and emits to all users"""
#     comment_id = data.get("comment_id")
#     reply_user_id = data.get("reply_user_id")
#     reply_text = data.get("reply_text")
#     timestamp = datetime.datetime.now(timezone.utc).isoformat()

#     if not comment_id or not reply_user_id or not reply_text:
#         emit("error", {"message": "Missing required fields"}, broadcast=False)
#         return

#     try:
#         # Store reply in DB
#         success = CommentModel.add_reply(comment_id, reply_user_id, reply_text, timestamp)

#         # Emit new reply correctly
#         emit("receive_reply", {
#             "_id": str(success),  # Store correct reply ID
#             "comment_id": comment_id,
#             "reply_user_id": reply_user_id,
#             "reply_text": reply_text,
#             "timestamp": timestamp
#         }, broadcast=True)

#     except Exception as e:
#         emit("error", {"message": str(e)}, broadcast=False)


# Register Blueprints
app.register_blueprint(ml_bp, url_prefix="/ml")
app.register_blueprint(comment_bp, url_prefix="/comments")
app.register_blueprint(video_bp, url_prefix='/video')
app.register_blueprint(user_bp, url_prefix='/auth')

if __name__ == "__main__":
    socketio.run(app) # ✅ Start WebSockets properly
