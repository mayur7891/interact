from flask_socketio import emit, join_room
from app import socketio


@socketio.on("join")
def on_join(data):
    video_id = data["video_id"]
    join_room(f"video_{video_id}")


@socketio.on("new_comment")
def handle_new_comment(data):
    video_id = data["video_id"]
    emit("receive_comment", data, room=f"video_{video_id}")


@socketio.on("new_reply")
def handle_new_reply(data):
    comment_id = data["comment_id"]
    emit("receive_reply", data, room=f"comment_{comment_id}")
