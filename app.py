from flask import jsonify
from dotenv import load_dotenv
import os

load_dotenv()

from app import create_app, socketio

app = create_app()


@app.route("/api")
def get_data():
    return jsonify({"message": "Hello from Flask!", "status": "success"})
