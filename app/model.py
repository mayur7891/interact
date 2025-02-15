from datetime import datetime, timezone
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from app import mongo
from pymongo.errors import DuplicateKeyError
from pymongo import UpdateOne

class CommentModel:
    """Handles comment-related database operations."""

    @staticmethod
    def add_comment(video_id, user_id, comment_text, embedding, cluster, sentiment):
        """Insert a new comment into the database."""
        comment_data = {
            "video_id": video_id,
            "user_id": user_id,
            "comment": comment_text,
            "embedding": embedding,  # List of floats
            "cluster": cluster,
            "sentiment": sentiment,  # "positive", "negative", "neutral"
            "replies": [],
            "timestamp": datetime.now(timezone.utc)
        }
        result = mongo.db.comments.insert_one(comment_data)
        return str(result.inserted_id)

    @staticmethod
    def get_comments_by_video(video_id):
        """Fetch paginated comments for a specific video."""
        comments = mongo.db.comments.find({"video_id": video_id}) \
                                    .sort("timestamp", -1) 
        return [{**comment, "_id": str(comment["_id"])} for comment in comments]

    @staticmethod # needs to be updated (video and comment id)
    def add_reply(comment_id, reply_user_id, reply_text):
        """Add a reply to a specific comment."""
        reply_data = {
            "reply_id": str(ObjectId()),
            "reply": reply_text,
            "reply_user_id": reply_user_id,
            "timestamp": datetime.now(timezone.utc)
        }
        result = mongo.db.comments.update_one(
            {"_id": ObjectId(comment_id)},
            {"$push": {"replies": reply_data}}
        )
        return result.modified_count > 0  # Returns True if the update was successful

    @staticmethod
    def get_comment_by_id(comment_id):
        """Fetch a single comment by ID."""
        comment = mongo.db.comments.find_one({"_id": ObjectId(comment_id)})
        if comment:
            comment["_id"] = str(comment["_id"])  # Convert ObjectId to string
        return comment
    
    @staticmethod
    def get_non_empty_embedding_data(video_id):
        """Fetch comments for a video that have a non-empty embedding."""
        comments_cursor = mongo.db.comments.find(
            {"video_id": video_id, "embedding": {"$exists": True, "$ne": []}}
        )
        comments = list(comments_cursor)  # Convert cursor to a list

        return [{**comment, "_id": str(comment["_id"])} for comment in comments]

    @staticmethod
    def bulk_update_clusters(updates):
        bulk_ops = [
        UpdateOne(
                {"_id": ObjectId(update["_id"])},  # ✅ Convert `_id` to ObjectId
                {"$set": {"cluster": int(update["cluster"])}}  # ✅ Ensure `cluster` is an int
            )
            for update in updates
        ]

        if bulk_ops:
            mongo.db.comments.bulk_write(bulk_ops)  





class SentimentModel:
    """ Handles percentage of sentiments viz. positive, negative and neutral"""
    @staticmethod
    def add_sentiment(video_id, positive=0, negative=0, neutral=0):
        """Insert a new comment into the database."""
        sentiment_data ={ "$set": {
            "video_id": video_id,
            "positive":positive,
            "negative":negative,
            "neutral":neutral
        }}

        result = mongo.db.sentimentDetail.update_one(
            {"video_id": video_id},  # Match the video ID
            sentiment_data,
            upsert=True  # If not found, insert a new entry
        )
        return result.upserted_id if result.upserted_id else "Updated"
    
    @staticmethod
    def get_sentiment_by_video_id(video_id):
        """Fetch sentiment data for a given video ID."""
        sentiment = mongo.db.sentimentDetail.find_one(
            {"video_id": video_id}, 
            {"_id": 0, "positive": 1, "negative": 1, "neutral": 1}  # Exclude _id, video_id
        )
        return sentiment if sentiment else None
    


# mongo.db.videos.create_index("video_id", unique=True)

class VideoModel:
    """Handles video data"""

    @staticmethod
    def add_video(video_ID, description, title, duration, creator_id):
        """Inserts new video data, ensuring video_id is unique"""
        video_data = {
            "video_id": video_ID,
            "description": description,
            "title": title,
            "duration": duration,
            "creator_id": creator_id
        }

        try:
            result = mongo.db.videos.insert_one(video_data)
            return {"message": "Video added successfully", "video_id": str(result.inserted_id)}
        except DuplicateKeyError:
            return {"error": "video_id already exists"}  # Prevent duplicate insertion
        
    @staticmethod
    def get_all_videos():
        """Fetches all videos from the database"""
        videos = mongo.db.videos.find({}, {"_id": 0})  # Excluding MongoDB's default _id field
        return list(videos)

    @staticmethod
    def get_video_by_id(video_ID):
        """Fetches a single video by video_id"""
        video = mongo.db.videos.find_one({"video_id": video_ID}, {"_id": 0})  # Exclude _id field

        if video:
            return video
        else:
            return {"error": "Video not found"}
        


        