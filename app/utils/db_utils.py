from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


class MongoDB:
    """MongoDB connection manager with connection pooling, retry logic, and index management."""

    def __init__(self):
        self._client = None
        self._db = None

    def init_app(self, app):
        uri = app.config["MONGO_URI"]
        self._client = MongoClient(
            uri,
            maxPoolSize=app.config.get("MONGO_MAX_POOL_SIZE", 50),
            minPoolSize=app.config.get("MONGO_MIN_POOL_SIZE", 10),
            connectTimeoutMS=app.config.get("MONGO_CONNECT_TIMEOUT_MS", 5000),
            serverSelectionTimeoutMS=app.config.get("MONGO_SERVER_SELECTION_TIMEOUT_MS", 5000),
            socketTimeoutMS=app.config.get("MONGO_SOCKET_TIMEOUT_MS", 10000),
            retryWrites=True,
            retryReads=True,
        )
        self._db = self._client.get_default_database()
        self._ensure_indexes()

    @property
    def db(self):
        if self._db is None:
            raise RuntimeError("MongoDB not initialized. Call init_app() first.")
        return self._db

    @property
    def client(self):
        return self._client

    def _ensure_indexes(self):
        db = self._db
        db.comments.create_index([("video_id", ASCENDING)])
        db.comments.create_index([("video_id", ASCENDING), ("cluster", ASCENDING)])
        db.comments.create_index([("video_id", ASCENDING), ("user_id", ASCENDING)])
        db.comments.create_index([("video_id", ASCENDING), ("timestamp", ASCENDING)])
        db.videos.create_index([("video_id", ASCENDING)], unique=True)
        db.users.create_index([("user_name", ASCENDING)], unique=True)
        db.sentimentDetail.create_index([("video_id", ASCENDING)], unique=True)
        db.clusterReply.create_index([("video_id", ASCENDING), ("cluster_no", ASCENDING)])
        db.summaries.create_index([("video_id", ASCENDING)], unique=True)

    def ping(self):
        try:
            self._client.admin.command("ping")
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError):
            return False
