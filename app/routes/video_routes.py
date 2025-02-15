from flask import Blueprint, request, jsonify
from pymongo.errors import DuplicateKeyError
from app.model import VideoModel


video_bp = Blueprint('video_routes', __name__)

@video_bp.route('/add_video', methods=['POST'])
def add_video():
    """API to add a new video"""
    data = request.json  # Get JSON data from request
    result = VideoModel.add_video(
        video_ID=data.get("video_id"),
        description=data.get("description"),
        title=data.get("title"),
        duration=data.get("duration"),
        creator_id=data.get("creator_id")
    )
    return jsonify(result)

@video_bp.route('/videos', methods=['GET'])
def get_videos():
    """API to fetch all videos"""
    return jsonify(VideoModel.get_all_videos())

@video_bp.route('/video/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """API to fetch a single video by video_id"""
    return jsonify(VideoModel.get_video_by_id(video_id))
