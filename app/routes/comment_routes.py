from flask import Blueprint, jsonify
from app.model import CommentModel  
from bson.objectid import ObjectId

from flask import Blueprint, request, jsonify
from app.services.preprocessing import preprocess_text, analyze_sentiment
from app.model import CommentModel, SentimentModel

comment_bp = Blueprint("comments", __name__)  # Define Blueprint

@comment_bp.route("/<int:video_id>/comments", methods=["GET"])
def get_comments(video_id):
    """Fetch all comments for a particular video ID."""
    comments = CommentModel.get_comments_by_video(video_id)  # Convert to string for MongoDB
    
    if comments:
        return jsonify(comments), 200
    else:
        return jsonify({"error": "No comments found for this video"}), 404
    



comment_bp = Blueprint("comment_routes", __name__)

@comment_bp.route("/add_comment", methods=["POST"])
def process_comment():
    """API to process a new comment"""
    
    # Step 1: Parse request data
    data = request.json
    comment_text = data.get("comment_text")
    video_id = data.get("video_id")
    user_id = data.get("user_id")

    if not comment_text or not video_id or not user_id:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Step 2: Generate embedding & sentiment
        embedding = preprocess_text(comment_text)
        sentiment = analyze_sentiment(comment_text)
        cluster = -1  # Default until clustering is applied

        # Step 3: Get existing sentiment stats for the video
        sentiments = SentimentModel.get_sentiment_by_video_id(video_id)

        if sentiments:
            positive = sentiments.get("positive", 0)
            negative = sentiments.get("negative", 0)
            neutral = sentiments.get("neutral", 0)
        else:
            positive, negative, neutral = 0, 0, 0  # Default values

        # Step 4: Update sentiment counts
        if sentiment == "positive":
            positive += 1
        elif sentiment == "negative":
            negative += 1
        else:
            neutral += 1

        # Step 5: Update sentiment in DB
        SentimentModel.add_sentiment(video_id, positive, negative, neutral)

        # Step 6: Store comment in DB
        CommentModel.add_comment(video_id, user_id, comment_text, embedding, cluster, sentiment)

        return jsonify({"message": "Comment processed successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@comment_bp.route("/add_reply/<string:comment_id>", methods=["POST"])
def add_reply(comment_id):
    """API to add a reply to a comment."""
    data = request.json
    reply_user_id = data.get("reply_user_id")
    reply_text = data.get("reply_text")

    if not reply_user_id or not reply_text:
        return jsonify({"error": "Missing required fields"}), 400

    success = CommentModel.add_reply(comment_id, reply_user_id, reply_text)
    
    if success:
        return jsonify({"message": "Reply added successfully"}), 200
    else:
        return jsonify({"error": "Failed to add reply. Comment not found."}), 404