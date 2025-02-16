from flask import Blueprint, request
from flask_socketio import emit, disconnect
from flask_jwt_extended import decode_token
from app import socketio  # ✅ Use the globally initialized socketio instance
from app.services.preprocessing import preprocess_text, analyze_sentiment
# socket_bp = Blueprint("socket_routes", __name__)
from app.model import SentimentModel, CommentModel

# @socketio.on("connect")
# def handle_connect():
#     """Handles WebSocket connection with JWT authentication"""
#     token = request.args.get("token")  # Get token from query params

#     if not token:
#         emit("error", {"message": "Missing authentication token"}, broadcast=False)
#         disconnect()
#         return

#     try:
#         decoded_token = decode_token(token)
#         user_name = decoded_token.get("sub")  # JWT subject (user_name)
#         print(f"User {user_name} connected via WebSocket")
#         emit("message", {"msg": f"Welcome, {user_name}!"})  # Send welcome message
#     except:
#         emit("error", {"message": "Invalid or expired token"}, broadcast=False)
#         disconnect()

# @socketio.on("message")
# def handle_message(data):
#     """Handles WebSocket messages"""
#     print("Received message:", data)
#     emit("message", {"msg": "Message received!"}, broadcast=True)



# @socketio.on("new_reply")
# def handle_new_reply(data):
#     """Handles new replies and emits to all users"""
#     comment_id = data.get("comment_id")
#     reply_user_id = data.get("reply_user_id")
#     reply_text = data.get("reply_text")

#     if not comment_id or not reply_user_id or not reply_text:
#         emit("error", {"message": "Missing required fields"}, broadcast=False)
#         return

#     try:
#         # Store reply in DB
#         success = CommentModel.add_reply(comment_id, reply_user_id, reply_text)

#         if success:
#             # Emit the new reply to all connected clients
#             emit("new_reply", {
#                 "comment_id": comment_id,
#                 "reply_user_id": reply_user_id,
#                 "reply_text": reply_text
#             }, broadcast=True)
#         else:
#             emit("error", {"message": "Failed to add reply. Comment not found."}, broadcast=False)

#     except Exception as e:
#         emit("error", {"message": str(e)}, broadcast=False)
