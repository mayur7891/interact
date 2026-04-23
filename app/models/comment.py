from bson.objectid import ObjectId
from pymongo import UpdateOne

from app import mongo


class CommentModel:

    @staticmethod
    def add_comment(video_id, user_id, comment_text, embedding, cluster, sentiment, timestamp):
        result = mongo.db.comments.insert_one({
            "video_id": video_id,
            "user_id": user_id,
            "comment": comment_text,
            "embedding": embedding,
            "cluster": cluster,
            "sentiment": sentiment,
            "replies": [],
            "timestamp": timestamp,
        })
        return str(result.inserted_id)

    @staticmethod
    def get_comments_by_video(video_id):
        comments = mongo.db.comments.find(
            {"video_id": video_id}, {"embedding": 0}
        ).sort("timestamp", -1)
        return [{**c, "_id": str(c["_id"])} for c in comments]

    @staticmethod
    def add_reply(comment_id, reply_user_id, reply_text, reply_id):
        mongo.db.comments.update_one(
            {"_id": ObjectId(comment_id)},
            {"$push": {"replies": {
                "reply_id": reply_id,
                "reply_text": reply_text,
                "reply_user_id": reply_user_id,
            }}},
        )
        return reply_id

    @staticmethod
    def get_replies(comment_id):
        comment = mongo.db.comments.find_one(
            {"_id": ObjectId(comment_id)}, {"replies": 1}
        )
        return comment.get("replies", []) if comment else None

    @staticmethod
    def get_comment_by_id(comment_id):
        comment = mongo.db.comments.find_one(
            {"_id": ObjectId(comment_id)}, {"embedding": 0}
        )
        if comment:
            comment["_id"] = str(comment["_id"])
        return comment

    @staticmethod
    def get_non_empty_embedding_data(video_id):
        # "embedding.0" $exists True correctly checks array has at least one element
        # ("$ne": [] does element-wise matching in MongoDB, not empty-array check)
        comments = list(mongo.db.comments.find(
            {"video_id": video_id, "embedding.0": {"$exists": True}}
        ))
        return [{**c, "_id": str(c["_id"])} for c in comments]

    @staticmethod
    def bulk_update_clusters(updates):
        if not updates:
            return
        bulk_ops = [
            UpdateOne(
                {"_id": ObjectId(u["_id"])},
                {"$set": {"cluster": int(u["cluster"])}},
            )
            for u in updates
        ]
        mongo.db.comments.bulk_write(bulk_ops)

    @staticmethod
    def get_comments_by_cluster(video_id, cluster):
        comments = mongo.db.comments.find(
            {"video_id": video_id, "cluster": cluster}, {"embedding": 0}
        ).sort("timestamp", -1)
        return [{**c, "_id": str(c["_id"])} for c in comments]

    @staticmethod
    def get_comments_by_user(video_id, user_id):
        comments = mongo.db.comments.find(
            {"video_id": video_id, "user_id": user_id}, {"embedding": 0}
        ).sort("timestamp", -1)
        return [{**c, "_id": str(c["_id"])} for c in comments]

    @staticmethod
    def get_unique_clusters_with_sample(video_id):
        pipeline = [
            {"$match": {"video_id": video_id}},
            {"$group": {
                "_id": "$cluster",
                "sample_comment": {"$first": "$$ROOT"},
            }},
            {"$project": {
                "_id": 0,
                "cluster": "$_id",
                "comment": {
                    "_id": {"$toString": "$sample_comment._id"},
                    "video_id": "$sample_comment.video_id",
                    "user_id": "$sample_comment.user_id",
                    "comment": "$sample_comment.comment",
                    "cluster": "$sample_comment.cluster",
                    "sentiment": "$sample_comment.sentiment",
                    "replies": "$sample_comment.replies",
                    "timestamp": "$sample_comment.timestamp",
                },
            }},
        ]
        return list(mongo.db.comments.aggregate(pipeline))
