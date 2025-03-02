from flask import Blueprint, jsonify
from app.model import CommentModel  
from bson.objectid import ObjectId

from flask import Blueprint, request
from app.services.preprocessing import preprocess_text, analyze_sentiment
from app.model import CommentModel, SentimentModel
import datetime
from datetime import timezone

from app import socketio
from flask_socketio import emit,join_room

comment_bp = Blueprint("comments", __name__)  # Define Blueprint

@comment_bp.route("/<int:video_id>/comments", methods=["GET"])
def get_comments(video_id):
    """Fetch all comments for a particular video ID."""
    comments = CommentModel.get_comments_by_video(video_id)  # Convert to string for MongoDB
    
    if comments:
        return jsonify(comments), 200
    return


@comment_bp.route("/<comment_id>/comment", methods=["GET"])
def get_comments_by_commentId(comment_id):
    """Fetch all comments for a particular comment ID."""
    object_id = ObjectId(comment_id)
    comments = CommentModel.get_comment_by_id(object_id)  # Convert to string for MongoDB
    
    if comments:
        return jsonify(comments), 200
    else:
        return jsonify({"error": "No comments found for this video"}), 404 
    

@comment_bp.route("/<comment_id>/replies", methods=["GET"])
def get_replies_by_commentId(comment_id):
    """Fetch all comments for a particular video ID."""
    try:
        object_id = ObjectId(comment_id)
    
        replies = CommentModel.get_replies(object_id)  # Retrieve replies from the database

        if not replies:  # Check if there are no replies
            return jsonify({"message": "No replies found for this comment"}), 200

        return jsonify(replies), 200
    except Exception as e:
        print(f"Error fetching replies for comment {comment_id}: {e}")
        return jsonify({"error": "Unable to fetch replies"}), 500

@comment_bp.route("/cluster/<int:video_id>/<cluster>", methods=["GET"])
def get_comments_by_cluster(video_id, cluster):
    """API to fetch comments filtered by video_id and cluster number."""
    cluster = int(cluster)
    try:
        comments = CommentModel.get_comments_by_cluster(video_id, cluster)
        return jsonify({"success": True, "comments": comments}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@comment_bp.route("/<user_id>/<int:video_id>", methods=["GET"])
def get_comments_by_videoId_userId(video_id, user_id):
    """API to fetch comments filtered by video_id and user ID."""
    try:
        comments = CommentModel.get_comments_by_user(video_id, user_id)
        return jsonify({"success": True, "comments": comments}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@comment_bp.route("/unique_clusters/<int:video_id>", methods=["GET"])
def get_unique_clusters(video_id):
    """API to fetch unique clusters and one sample comment from each cluster."""
    try:
        clusters = CommentModel.get_unique_clusters_with_sample(video_id)
        return jsonify({"success": True, "clusters": clusters}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# @comment_bp.route("/add_comment", methods=["POST"])
# def add_comment():
#     """API to process a new comment"""
    
#     # Step 1: Parse request data
#     data = request.json
#     comment_text = data.get("comment_text")
#     video_id = data.get("video_id")
#     user_id = data.get("user_id")

#     if not comment_text or not video_id or not user_id:
#         return jsonify({"error": "Missing required fields"}), 400

#     try:
#         # Step 2: Generate embedding & sentiment
#         embedding = preprocess_text(comment_text)
#         sentiment = analyze_sentiment(comment_text)
#         cluster = -1  # Default until clustering is applied
#         timestamp = datetime.datetime.now(timezone.utc).isoformat()
#         # Step 3: Get existing sentiment stats for the video
#         sentiments = SentimentModel.get_sentiment_by_video_id(video_id)

#         if sentiments:
#             positive = sentiments.get("positive", 0)
#             negative = sentiments.get("negative", 0)
#             neutral = sentiments.get("neutral", 0)
#         else:
#             positive, negative, neutral = 0, 0, 0  # Default values

#         # Step 4: Update sentiment counts
#         if sentiment == "positive":
#             positive += 1
#         elif sentiment == "negative":
#             negative += 1
#         else:
#             neutral += 1

#         # Step 5: Update sentiment in DB
#         SentimentModel.add_sentiment(video_id, positive, negative, neutral)

#         # Step 6: Store comment in DB
#         CommentModel.add_comment(video_id, user_id, comment_text, embedding, cluster, sentiment,timestamp)

#         return jsonify({"message": "Comment processed successfully!"}), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



# @comment_bp.route("/add_reply/<string:comment_id>", methods=["POST"])
# def add_reply(comment_id):
#     """API to add a reply to a comment."""
#     data = request.json
#     reply_user_id = data.get("reply_user_id")
#     reply_text = data.get("reply_text")
#     timestamp = datetime.datetime.now(timezone.utc).isoformat()

#     if not reply_user_id or not reply_text:
#         return jsonify({"error": "Missing required fields"}), 400

#     success = CommentModel.add_reply(comment_id, reply_user_id, reply_text,timestamp)
    
#     if success:
#         return jsonify({"message": "Reply added successfully"}), 200
#     else:
#         return jsonify({"error": "Failed to add reply. Comment not found."}), 404



@comment_bp.route("/<int:video_id>/add", methods=["POST"])
def add_comment(video_id):
    data = request.json
    comment_text = data.get("comment_text")
    user_id = data.get("user_id")

    # print(data)

    if not comment_text or not user_id:
        return jsonify({"error": "Missing required fields"}), 400
    
    # print(data)

    try:
        embedding = preprocess_text(comment_text)
        sentiment = analyze_sentiment(comment_text)
        cluster = -1  # Default cluster
        timestamp = datetime.datetime.now(timezone.utc).isoformat()

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

        comment_id = CommentModel.add_comment(video_id, user_id, comment_text, embedding, cluster, sentiment, timestamp)

        new_comment = {
            "_id": str(comment_id),
            "user_id": user_id,
            "video_id": video_id,
            "comment": comment_text,
            "cluster": cluster,
            "sentiment": sentiment,
            "timestamp": timestamp,
            "replies": []
        }

        socketio.emit("receive_comment", new_comment, room=f"video_{video_id}")

        # print(data)

        return jsonify({"success": True, "comment": new_comment}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add a new reply to a comment
@comment_bp.route("/<comment_id>/reply", methods=["POST"])
def add_reply(comment_id):
    data = request.json
    reply_user_id = data.get("reply_user_id")
    reply_text = data.get("reply_text")

    if not reply_text or not reply_user_id:
        return jsonify({"error": "Missing required fields"}), 400

    timestamp = datetime.datetime.now(timezone.utc).isoformat()

    try:
        success = CommentModel.add_reply(comment_id, reply_user_id, reply_text, timestamp)

        new_reply = {
            "_id": str(success),
            "comment_id": comment_id,
            "reply_user_id": reply_user_id,
            "reply_text": reply_text,
            "timestamp": timestamp
        }

        socketio.emit("receive_reply", new_reply, room=f"comment_{comment_id}")

        return jsonify({"success": True, "reply": new_reply}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Socket.io: Join room per video
@socketio.on("join")
def on_join(data):
    video_id = data["video_id"]
    join_room(f"video_{video_id}")

# Socket.io: Handle new comment event
@socketio.on("new_comment")
def handle_new_comment(data):
    video_id = data["video_id"]
    emit("receive_comment", data, room=f"video_{video_id}")

# Socket.io: Handle new reply event
@socketio.on("new_reply")
def handle_new_reply(data):
    comment_id = data["comment_id"]
    emit("receive_reply", data, room=f"comment_{comment_id}")