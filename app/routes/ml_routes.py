import datetime
from datetime import timezone

import numpy as np
from flask import Blueprint, jsonify, request, current_app
from sklearn.metrics.pairwise import cosine_similarity

from app.models import SentimentModel, CommentModel, ClusterReplyModel, SummaryModel
from app.services.ml_service import cluster
from app.services.preprocessing import preprocess_text
from app.services.summary_service import (
    _call_gemini,
    generate_fallback_answer,
    generate_full_summary,
    update_rolling_summary,
)

ml_bp = Blueprint("ml", __name__)


@ml_bp.route("/sentiment/<int:video_id>", methods=["GET"])
def get_sentiment(video_id):
    sentiment_data = SentimentModel.get_sentiment_by_video_id(video_id)
    if sentiment_data:
        return jsonify(sentiment_data), 200
    return jsonify({"error": "No sentiment data found for this video"}), 404


@ml_bp.route("/test-chatbot/<int:video_id>", methods=["POST"])
def test_preprocessing(video_id):
    data = request.json
    query = data.get("query")
    if not query:
        return jsonify({"error": "Query is required"}), 400

    query_embedding = np.array(preprocess_text(query))
    current_app.logger.info(f"[Search] video_id={video_id} query='{query}' emb_len={len(query_embedding)}")

    records = CommentModel.get_non_empty_embedding_data(video_id)
    current_app.logger.info(f"[Search] records_with_embeddings={len(records)}")
    if not records:
        current_app.logger.warning(f"[Search] No comments with embeddings found for video_id={video_id}")
        return jsonify({"message": "No comments found for this video."}), 404

    # Batch cosine similarity
    embeddings = np.array([r["embedding"] for r in records])
    scores = cosine_similarity(query_embedding.reshape(1, -1), embeddings)[0]
    current_app.logger.info(f"[Search] score_min={scores.min():.4f} score_max={scores.max():.4f} score_mean={scores.mean():.4f}")

    threshold = 0.25
    indexed = [(records[i], float(scores[i])) for i in range(len(records)) if scores[i] >= threshold]
    indexed.sort(key=lambda x: x[1], reverse=True)
    current_app.logger.info(f"[Search] threshold={threshold} matched={len(indexed)}")
    top_comments = [r for r, _ in indexed[:5]]

    for comment in top_comments:
        comment.pop("embedding", None)

    return jsonify(top_comments)


@ml_bp.route("/get_clusters/<int:video_id>", methods=["GET"])
def get_clusters(video_id):
    records = CommentModel.get_non_empty_embedding_data(video_id)
    if not records:
        return jsonify({"message": "No comments found for this video."}), 404

    embeddings = [r["embedding"] for r in records]
    clusters_list = cluster(embeddings)

    bulk_updates = [
        {"_id": r["_id"], "cluster": int(c)}
        for r, c in zip(records, clusters_list)
    ]
    CommentModel.bulk_update_clusters(bulk_updates)
    return jsonify({"message": "Clusters updated successfully."})


@ml_bp.route("/reply_cluster/<int:video_id>/<int:cluster_no>", methods=["POST"])
def reply_cluster(video_id, cluster_no):
    data = request.json
    reply_text = data.get("reply_text")
    creator_id = data.get("creator_id")
    if not reply_text:
        return jsonify({"error": "Reply is required"}), 400

    timestamp = datetime.datetime.now(timezone.utc).isoformat()
    try:
        ClusterReplyModel.add_cluster_reply(cluster_no, video_id, creator_id, reply_text, timestamp)
        return jsonify({"message": "Reply added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ml_bp.route("/get_cluster_replies/<int:video_id>/<int:cluster_no>", methods=["GET"])
def get_cluster_replies(video_id, cluster_no):
    try:
        results = ClusterReplyModel.get_replies_by_cluster_videoId(video_id, cluster_no)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ml_bp.route("/get_all_cluster_replies/<int:video_id>/<creator_id>", methods=["GET"])
def get_all_cluster_replies(video_id, creator_id):
    try:
        results = ClusterReplyModel.get_all_replies_by_creator_video(video_id, creator_id)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ml_bp.route("/getsummary/<int:video_id>", methods=["GET"])
def get_summary(video_id):
    """
    Return the cached rolling summary for a video.
    If none exists, generate one from all comments (first call is slow).
    """
    current_app.logger.info("GET /ml/getsummary called", extra={"video_id": video_id})

    cached = SummaryModel.get_summary(video_id)
    if cached and cached.get("summary"):
        current_app.logger.info(
            "Returning cached summary",
            extra={"video_id": video_id, "summary_length": len(cached["summary"])},
        )
        return jsonify({"summary": cached["summary"]}), 200

    # No cached summary — generate from all existing comments
    comments = CommentModel.get_comments_by_video(video_id)
    if not comments:
        current_app.logger.info("No comments available for summary", extra={"video_id": video_id})
        return jsonify({"summary": "No comments yet for this video."}), 200

    try:
        texts = [c["comment"] for c in comments if c.get("comment")]
        current_app.logger.info(
            "Generating uncached summary",
            extra={"video_id": video_id, "comment_count": len(texts)},
        )
        summary = generate_full_summary(texts, video_id=video_id)
        if summary is None:
            # Another thread just generated it — return from cache
            cached = SummaryModel.get_summary(video_id)
            summary = cached.get("summary", "Summary generation in progress.") if cached else "Summary generation in progress."
            current_app.logger.info(
                "Summary request reused in-flight generation",
                extra={"video_id": video_id},
            )
            return jsonify({"summary": summary}), 200
        SummaryModel.upsert_summary(video_id, summary, len(texts))
        current_app.logger.info(
            "Summary persisted",
            extra={"video_id": video_id, "summary_length": len(summary)},
        )
        return jsonify({"summary": summary}), 200
    except Exception:
        current_app.logger.exception("Summary request failed", extra={"video_id": video_id})
        e = "Internal error while generating summary"
        return jsonify({"error": f"Failed to generate summary: {str(e)}"}), 500


@ml_bp.route("/ask/<int:video_id>", methods=["POST"])
def ask_assistant(video_id):
    """
    Answer a creator's question using the video's summary as context.
    Keeps the Gemini API key server-side only.
    """
    data = request.json or {}
    question = (data.get("question") or "").strip()
    current_app.logger.info(
        "POST /ml/ask called",
        extra={"video_id": video_id, "has_question": bool(question)},
    )
    if not question:
        return jsonify({"error": "question is required"}), 400

    cached = SummaryModel.get_summary(video_id)
    summary = cached.get("summary", "") if cached else ""
    if not summary:
        comments = CommentModel.get_comments_by_video(video_id)
        texts = [c["comment"] for c in comments if c.get("comment")]
        if not texts:
            current_app.logger.info("Ask failed because no comments exist", extra={"video_id": video_id})
            return jsonify({"error": "No comments available for this video yet."}), 404
        current_app.logger.info(
            "Ask endpoint bootstrapping summary",
            extra={"video_id": video_id, "comment_count": len(texts)},
        )
        summary = generate_full_summary(texts, video_id=video_id)
        if summary:
            SummaryModel.upsert_summary(video_id, summary, len(texts))

    prompt = (
        f"You are an AI assistant helping a content creator improve their content.\n"
        f"Here is a summary of viewer comments for their video:\n{summary}\n\n"
        f"Answer this question from the creator: {question}"
    )
    try:
        answer = _call_gemini(prompt)
        current_app.logger.info(
            "Ask endpoint answered successfully",
            extra={"video_id": video_id, "answer_length": len(answer)},
        )
        return jsonify({"answer": answer}), 200
    except Exception:
        current_app.logger.exception("Ask endpoint failed", extra={"video_id": video_id})
        fallback_answer = generate_fallback_answer(summary, question)
        return jsonify({"answer": fallback_answer, "fallback": True}), 200

