from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash, check_password_hash

from app import mongo


class UserModel:

    @staticmethod
    def add_user(user_name, password, is_creator):
        try:
            result = mongo.db.users.insert_one({
                "user_name": user_name,
                "password": generate_password_hash(password),
                "isCreator": is_creator,
            })
            return {"message": "User registered successfully", "user_id": str(result.inserted_id)}
        except DuplicateKeyError:
            return {"error": "Username already exists"}

    @staticmethod
    def get_user(user_name):
        user = mongo.db.users.find_one({"user_name": user_name}, {"_id": 0, "password": 0})
        return user if user else {"error": "User not found"}

    @staticmethod
    def verify_user(user_name, password):
        user = mongo.db.users.find_one({"user_name": user_name})
        if user and check_password_hash(user["password"], password):
            return {"isCreator": user["isCreator"]}
        return None
