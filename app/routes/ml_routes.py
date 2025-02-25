from flask import Blueprint, jsonify, request
from app.model import SentimentModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.model import CommentModel
from app.services.preprocessing import preprocess_text
from app.services.ml_service import cluster
from app.model import ClusterReplyModel

import datetime
from datetime import timezone

ml_bp = Blueprint("ml", __name__)




@ml_bp.route("/sentiment/<int:video_id>", methods=["GET"])
def get_sentiment(video_id):
    """Fetch sentiment count for a particular video ID."""
    sentiment_data = SentimentModel.get_sentiment_by_video_id(video_id)
    print(sentiment_data)
    if sentiment_data:
        return jsonify(sentiment_data), 200
    else:
        return jsonify({"error": "No sentiment data found for this video"}), 404


@ml_bp.route('/test-chatbot/<int:video_id>', methods=["POST"])
def test_preprocessing(video_id):
    """Processes a query and finds the most relevant comments based on similarity."""
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"error": "Query is required"}), 400

    query_embedding = np.array(preprocess_text(query))
    records = CommentModel.get_non_empty_embedding_data(video_id)

    if not records:
        return jsonify({"message": "No comments found for this video."}), 404

    similarities = []
    for record in records:
        embedding = np.array(record["embedding"])
        similarity = cosine_similarity(query_embedding.reshape(1, -1), embedding.reshape(1, -1))[0][0]
        similarities.append((record, similarity))

    # Sort and filter top matches
    similarities.sort(key=lambda x: x[1], reverse=True)
    threshold = 0.35
    top_comments = [record for record, score in similarities[:5] if score >= threshold]

    # Remove the "embedding" key from the response
    for comment in top_comments:
        comment.pop("embedding", None)

    return jsonify(top_comments)

@ml_bp.route('/get_clusters/<int:video_id>', methods=["GET"])
def get_clusters(video_id):
    """Fetches comments for a video, performs clustering, and updates cluster IDs."""
    records = CommentModel.get_non_empty_embedding_data(video_id)

    if not records:
        return jsonify({"message": "No comments found for this video."}), 404

    embeddings = [record["embedding"] for record in records if "embedding" in record]
    clusters_list = cluster(embeddings)  # Call the clustering function

    # Prepare bulk update list
    bulk_updates = [
        {"_id": record["_id"], "cluster": cluster_id}
        for record, cluster_id in zip(records, clusters_list)
    ]

    # Update cluster assignments in DB
    CommentModel.bulk_update_clusters(bulk_updates)

    return jsonify({"message": "Clusters updated successfully."})


@ml_bp.route('/reply_cluster/<int:video_id>/<int:cluster_no>', methods=["POST"])
def reply_cluster(video_id,cluster_no):
    data = request.json
    reply_text = data.get("reply_text")
    creator_id = data.get("creator_id")
    timestamp = timestamp = datetime.datetime.now(timezone.utc).isoformat()

    if not reply_text:
        return jsonify({"error": "Reply is required"}), 400
    
    try:
        result = ClusterReplyModel.add_cluster_reply(cluster_no,video_id,creator_id, reply_text, timestamp)
        return jsonify({"message": "Reply added successfully!"}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ml_bp.route('/get_cluster_replies/<int:video_id>/<int:cluster_no>', methods=["GET"])
def get_cluster_replies(video_id,cluster_no):
    try:
        results = ClusterReplyModel.get_replies_by_cluster_videoId(video_id,cluster_no)
        return jsonify(results), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@ml_bp.route('/get_all_cluster_replies/<int:video_id>/<creator_id>', methods=["GET"])
def get_All_cluster_replies(video_id,creator_id):
    try:
        results = ClusterReplyModel.get_Allreplies_by_creatorId_videoId(video_id,creator_id)
        return jsonify(results), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


