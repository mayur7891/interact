from app import create_app
from flask import jsonify,request
from app.model import CommentModel
from app.routes.ml_routes import ml_bp
from app.routes.comment_routes import comment_bp
import numpy as np


app = create_app()



@app.route("/api")
def get_data():
    return jsonify({"message": "Hello from Flask!", "status": "success"})


app.register_blueprint(ml_bp, url_prefix="/ml")
app.register_blueprint(comment_bp, url_prefix="/comments")


if __name__ == "__main__":
    app.run(debug=True)

