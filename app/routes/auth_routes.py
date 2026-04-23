from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models import UserModel

user_bp = Blueprint("user_routes", __name__)


@user_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if not data.get("user_name") or not data.get("password"):
        return jsonify({"error": "Username and password are required"}), 400

    result = UserModel.add_user(
        user_name=data["user_name"],
        password=data["password"],
        is_creator=data.get("isCreator", False),
    )
    status = 201 if "user_id" in result else 400
    return jsonify(result), status


@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user_name = data.get("user_name")
    password = data.get("password")

    if not user_name or not password:
        return jsonify({"error": "Username and password are required"}), 400

    result = UserModel.verify_user(user_name, password)
    if result is None:
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user_name)
    return jsonify({
        "user_id": user_name,
        "message": "Login successful",
        "token": access_token,
        "isCreator": result.get("isCreator", False),
    }), 200


@user_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Logout successful"}), 200
