from app import mongo


class SentimentModel:

    @staticmethod
    def add_sentiment(video_id, positive=0, negative=0, neutral=0):
        result = mongo.db.sentimentDetail.update_one(
            {"video_id": video_id},
            {"$set": {
                "video_id": video_id,
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
            }},
            upsert=True,
        )
        return result.upserted_id if result.upserted_id else "Updated"

    @staticmethod
    def get_sentiment_by_video_id(video_id):
        return mongo.db.sentimentDetail.find_one(
            {"video_id": video_id},
            {"_id": 0, "positive": 1, "negative": 1, "neutral": 1},
        )
