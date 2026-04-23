import datetime
from datetime import timezone

from app import mongo


class SummaryModel:

    @staticmethod
    def get_summary(video_id):
        return mongo.db.summaries.find_one(
            {"video_id": video_id},
            {"_id": 0, "summary": 1, "comment_count": 1, "last_updated": 1},
        )

    @staticmethod
    def upsert_summary(video_id, summary, comment_count):
        mongo.db.summaries.update_one(
            {"video_id": video_id},
            {"$set": {
                "summary": summary,
                "comment_count": comment_count,
                "last_updated": datetime.datetime.now(timezone.utc).isoformat(),
            }},
            upsert=True,
        )
