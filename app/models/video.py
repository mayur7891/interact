from pymongo.errors import DuplicateKeyError

from app import mongo


class VideoModel:

    @staticmethod
    def add_video(video_ID, description, title, duration, creator_id):
        try:
            result = mongo.db.videos.insert_one({
                "video_id": video_ID,
                "description": description,
                "title": title,
                "duration": duration,
                "creator_id": creator_id,
            })
            return {"message": "Video added successfully", "video_id": str(result.inserted_id)}
        except DuplicateKeyError:
            return {"error": "video_id already exists"}

    @staticmethod
    def get_all_videos():
        return list(mongo.db.videos.find({}, {"_id": 0}))

    @staticmethod
    def get_video_by_id(video_ID):
        video = mongo.db.videos.find_one({"video_id": video_ID}, {"_id": 0})
        return video if video else {"error": "Video not found"}
