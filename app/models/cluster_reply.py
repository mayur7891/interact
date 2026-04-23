from pymongo import ReturnDocument

from app import mongo


class ClusterReplyModel:

    @staticmethod
    def add_cluster_reply(cluster_no, video_id, creator_id, reply_text, timestamp):
        return mongo.db.clusterReply.find_one_and_update(
            {"video_id": video_id, "cluster_no": cluster_no},
            {
                "$push": {"replies": {"reply_text": reply_text, "timestamp": timestamp}},
                "$setOnInsert": {"creator_id": creator_id},
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def get_replies_by_cluster_videoId(video_id, cluster_no):
        return list(mongo.db.clusterReply.find(
            {"video_id": video_id, "cluster_no": cluster_no},
            {"_id": 0, "replies": 1},
        ))

    @staticmethod
    def get_all_replies_by_creator_video(video_id, creator_id):
        return list(mongo.db.clusterReply.find(
            {"video_id": video_id, "creator_id": creator_id},
            {"_id": 0, "cluster_no": 1, "replies": 1},
        ))
