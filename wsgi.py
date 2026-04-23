# wsgi.py

from app import create_app, socketio

app = create_app()

# This is what gunicorn should run
if __name__ != "__main__":
    application = app
