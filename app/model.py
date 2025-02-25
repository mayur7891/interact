import datetime
from datetime import timezone
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from app import mongo
from pymongo.errors import DuplicateKeyError
from pymongo import UpdateOne
from werkzeug.security import generate_password_hash, check_password_hash
import jwt


class CommentModel:
    """Handles comment-related database operations."""

    @staticmethod
    def add_comment(video_id, user_id, comment_text, embedding, cluster, sentiment,timestamp):
        """Insert a new comment into the database."""
        comment_data = {
            "video_id": video_id,
            "user_id": user_id,
            "comment": comment_text,
            "embedding": embedding,  # List of floats
            "cluster": cluster,
            "sentiment": sentiment,  # "positive", "negative", "neutral"
            "replies": [],
            "timestamp": timestamp
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
    def add_reply(comment_id, reply_user_id, reply_text, reply_id):
        """Add a reply to a specific comment."""
        reply_data = {
            "reply_id": reply_id,
            "reply_text": reply_text,
            "reply_user_id": reply_user_id,
        }
        result = mongo.db.comments.update_one(
            {"_id": ObjectId(comment_id)},
            {"$push": {"replies": reply_data}}
        )
        return reply_id  # Returns True if the update was successful

    @staticmethod
    def get_replies(comment_id):
        """Fetch the replies list of a specific comment by _id."""
        comment = mongo.db.comments.find_one({"_id": ObjectId(comment_id)}, {"replies": 1})
        if comment:
            return comment.get("replies", [])  # Return replies list or empty if none
        return None  # Return None if comment not found

    @staticmethod
    def get_comment_by_id(comment_id):
        """Fetch a single comment by ID."""
        comment = mongo.db.comments.find_one({"_id": ObjectId(comment_id)})
        if comment:
            comment["_id"] = str(comment["_id"])  # Convert ObjectId to string
        return {**comment, "_id": str(comment["_id"])}
    
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
    @staticmethod
    def get_comments_by_cluster(video_id, cluster):
        """Fetch comments filtered by video_id and cluster number, sorted by timestamp (latest first)."""
        comments = mongo.db.comments.find({"video_id": video_id, "cluster": cluster}) \
                                    .sort("timestamp", -1)  

        return [{**comment, "_id": str(comment["_id"])} for comment in comments]
    
    @staticmethod
    def get_comments_by_user(video_id, user_id):
        """Fetch comments filtered by video_id and cluster number, sorted by timestamp (latest first)."""
        comments = mongo.db.comments.find({"video_id": video_id, "user_id": user_id}) \
                                    .sort("timestamp", -1)  

        return [{**comment, "_id": str(comment["_id"])} for comment in comments]


    @staticmethod
    def get_unique_clusters_with_sample(video_id):
        """Fetch unique clusters and one comment from each cluster for a specific video."""
        pipeline = [
            {"$match": {"video_id": video_id}},  # Filter by video_id
            {"$group": {
                "_id": "$cluster",
                "sample_comment": {"$first": "$$ROOT"}  # Pick the first comment per cluster
            }},
            {"$project": {
                "_id": 0,
                "cluster": "$_id",
                "comment": {
                    "_id": {"$toString": "$sample_comment._id"},  # Convert ObjectId to string
                    "video_id": "$sample_comment.video_id",
                    "user_id": "$sample_comment.user_id",
                    "comment": "$sample_comment.comment",
                    "embedding": "$sample_comment.embedding",
                    "cluster": "$sample_comment.cluster",
                    "sentiment": "$sample_comment.sentiment",
                    "replies": "$sample_comment.replies",
                    "timestamp": "$sample_comment.timestamp"
                }
            }}
        ]

        clusters = list(mongo.db.comments.aggregate(pipeline))
        return clusters


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
        

class ClusterReplyModel:

    @staticmethod
    def add_cluster_reply(cluster_no,video_id,creator_id,reply_text,timestamp):
        query = {"video_id": video_id, "cluster_no": cluster_no}
        update = {
            "$push": {"replies": {"reply_text":reply_text,"timestamp":timestamp}},  # Append new reply
            "$setOnInsert": {"creator_id": creator_id,}  # Set only on insert
        }
        options = {"upsert": True}

        updated_doc = mongo.db.clusterReply.find_one_and_update(query, update, return_document=True, **options)
        return updated_doc
    
    @staticmethod
    def get_replies_by_cluster_videoId(video_id, cluster_no):
        """Fetch comments filtered by video_id and cluster number, sorted by timestamp (latest first)."""
        replies = mongo.db.clusterReply.find({"video_id": video_id, "cluster_no": cluster_no},{"_id":0,"replies":1})

        return replies
    
    @staticmethod
    def get_Allreplies_by_creatorId_videoId(video_id, creator_id):
        replies = mongo.db.clusterReply.find({"video_id": video_id, "creator_id": creator_id},{"_id":0,"cluster_no":1,"replies":1})
        return replies
        

# User Model




SECRET_KEY = "your_secret_key"  

class UserModel:
    """Handles user authentication & JWT-based authentication"""

    @staticmethod
    def add_user(user_name, password, is_creator):
        """Registers a new user with a hashed password"""
        user_data = {
            "user_name": user_name,
            "password": generate_password_hash(password),
            "isCreator": is_creator
        }

        try:
            result = mongo.db.users.insert_one(user_data)
            return {"message": "User registered successfully", "user_id": str(result.inserted_id)}
        except:
            return {"error": "Username already exists"}

    @staticmethod
    def generate_token(user_name):
        """Generates a JWT token for authenticated users"""
        payload = {
            "user_name": user_name,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # Token expires in 2 hours
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token

    @staticmethod
    def verify_user(user_name, password):
        """Verifies user credentials and returns a JWT token"""
        user = mongo.db.users.find_one({"user_name": user_name})

        if user and check_password_hash(user["password"], password):
            token = UserModel.generate_token(user_name)
            return {"message": "Login successful", "token": token, "isCreator": user["isCreator"]}
        else:
            return {"error": "Invalid username or password"}

    @staticmethod
    def decode_token(token):
        """Decodes the JWT token to get user info"""
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return decoded["user_name"]
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}

    """Handles user authentication & management"""

    @staticmethod
    def add_user(user_name, password, is_creator):
        """Registers a new user with a hashed password & unique username"""
        user_data = {
            "user_name": user_name,
            "password": generate_password_hash(password),  # Hash password before storing
            "isCreator": is_creator
        }

        try:
            result = mongo.db.users.insert_one(user_data)
            return {"message": "User registered successfully", "user_id": str(result.inserted_id)}
        except DuplicateKeyError:
            return {"error": "Username already exists"}

    @staticmethod
    def get_user(user_name):
        """Fetches a user by user_name"""
        user = mongo.db.users.find_one({"user_name": user_name}, {"_id": 0, "password": 0})  # Hide password

        if user:
            return user
        else:
            return {"error": "User not found"}

    @staticmethod
    def verify_user(user_name, password):
        """Verifies user credentials"""
        user = mongo.db.users.find_one({"user_name": user_name})

        if user and check_password_hash(user["password"], password):
            return {"message": "Login successful", "isCreator": user["isCreator"]}
        else:
            return {"error": "Invalid username or password"}