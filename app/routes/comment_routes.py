from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from app.models import CommentModel, SentimentModel, SummaryModel
from app.services.preprocessing import preprocess_text, analyze_sentiment
from app import socketio
import datetime
from datetime import timezone

comment_bp = Blueprint("comments", __name__)


@comment_bp.route("/<int:video_id>/comments", methods=["GET"])
def get_comments(video_id):
    comments = CommentModel.get_comments_by_video(video_id)
    return jsonify(comments), 200


@comment_bp.route("/<comment_id>/comment", methods=["GET"])
def get_comments_by_commentId(comment_id):
    comment = CommentModel.get_comment_by_id(comment_id)
    if comment:
        return jsonify(comment), 200
    return jsonify({"error": "Comment not found"}), 404


@comment_bp.route("/<comment_id>/replies", methods=["GET"])
def get_replies_by_commentId(comment_id):
    try:
        replies = CommentModel.get_replies(ObjectId(comment_id))
        if replies is None:
            return jsonify({"error": "Comment not found"}), 404
        return jsonify(replies), 200
    except Exception as e:
        return jsonify({"error": "Unable to fetch replies"}), 500


@comment_bp.route("/cluster/<int:video_id>/<cluster>", methods=["GET"])
def get_comments_by_cluster(video_id, cluster):
    cluster = int(cluster)
    try:
        comments = CommentModel.get_comments_by_cluster(video_id, cluster)
        return jsonify({"success": True, "comments": comments}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@comment_bp.route("/<user_id>/<int:video_id>", methods=["GET"])
def get_comments_by_videoId_userId(video_id, user_id):
    try:
        comments = CommentModel.get_comments_by_user(video_id, user_id)
        return jsonify({"success": True, "comments": comments}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@comment_bp.route("/unique_clusters/<int:video_id>", methods=["GET"])
def get_unique_clusters(video_id):
    try:
        clusters = CommentModel.get_unique_clusters_with_sample(video_id)
        return jsonify({"success": True, "clusters": clusters}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@comment_bp.route("/<int:video_id>/add", methods=["POST"])
def add_comment(video_id):
    data = request.json
    comment_text = data.get("comment_text")
    user_id = data.get("user_id")

    if not comment_text or not user_id:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        embedding = preprocess_text(comment_text)
        sentiment = analyze_sentiment(comment_text)
        cluster = -1
        timestamp = datetime.datetime.now(timezone.utc).isoformat()

        sentiments = SentimentModel.get_sentiment_by_video_id(video_id) or {}
        positive = sentiments.get("positive", 0)
        negative = sentiments.get("negative", 0)
        neutral = sentiments.get("neutral", 0)

        if sentiment == "positive":
            positive += 1
        elif sentiment == "negative":
            negative += 1
        else:
            neutral += 1

        SentimentModel.add_sentiment(video_id, positive, negative, neutral)
        comment_id = CommentModel.add_comment(
            video_id, user_id, comment_text, embedding, cluster, sentiment, timestamp
        )

        new_comment = {
            "_id": str(comment_id),
            "user_id": user_id,
            "video_id": video_id,
            "comment": comment_text,
            "cluster": cluster,
            "sentiment": sentiment,
            "timestamp": timestamp,
            "replies": [],
        }
        socketio.emit("receive_comment", new_comment, room=f"video_{video_id}")

        # Update the rolling summary in the background (non-blocking)
        _update_summary_background(video_id, comment_text, current_app._get_current_object())

        return jsonify({"success": True, "comment": new_comment}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _update_summary_background(video_id, new_comment_text, app):
    """Spawn a background greenlet to update the rolling summary."""
    def _task():
        with app.app_context():
            try:
                from app.services.summary_service import generate_full_summary, update_rolling_summary
                cached = SummaryModel.get_summary(video_id)
                if cached and cached.get("summary"):
                    updated = update_rolling_summary(cached["summary"], new_comment_text)
                    new_count = (cached.get("comment_count") or 0) + 1
                    SummaryModel.upsert_summary(video_id, updated, new_count)
                # If no cached summary yet, skip — it will be generated on next GET /getsummary
            except Exception:
                pass  # Summary update failure must never affect comment posting

    try:
        import eventlet
        eventlet.spawn(_task)
    except Exception:
        pass  # Fallback: skip if eventlet not available


@comment_bp.route("/<comment_id>/reply", methods=["POST"])
def add_reply(comment_id):
    data = request.json
    reply_user_id = data.get("reply_user_id")
    reply_text = data.get("reply_text")

    if not reply_text or not reply_user_id:
        return jsonify({"error": "Missing required fields"}), 400

    timestamp = datetime.datetime.now(timezone.utc).isoformat()
    try:
        reply_id = CommentModel.add_reply(comment_id, reply_user_id, reply_text, timestamp)
        new_reply = {
            "_id": str(reply_id),
            "comment_id": comment_id,
            "reply_user_id": reply_user_id,
            "reply_text": reply_text,
            "timestamp": timestamp,
        }
        socketio.emit("receive_reply", new_reply, room=f"comment_{comment_id}")
        return jsonify({"success": True, "reply": new_reply}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500