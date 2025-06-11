# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (Fixes OpenCV `libGL.so.1` error)
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 curl

# Install Python dependencies
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt 

# Install WebSocket support for Flask-SocketIO
RUN pip install gevent-websocket  

# Copy the rest of the application
COPY . .  

# Create pickles directory
RUN mkdir -p /app/pickles

# Download pickle files from Google Cloud Storage
RUN curl -o /app/pickles/sentiment_pipeline.pkl https://storage.googleapis.com/interact-452615-pickles/sentiment_pipeline.pkl
RUN curl -o /app/pickles/sbert_pipeline.pkl https://storage.googleapis.com/interact-452615-pickles/sbert_pipeline.pkl
RUN curl -o /app/pickles/hdbscan_model.pkl https://storage.googleapis.com/interact-452615-pickles/hdbscan_model.pkl
RUN curl -o /app/pickles/umap_reducer.pkl https://storage.googleapis.com/interact-452615-pickles/umap_reducer.pkl

# Set environment variables
ENV PORT=8080
EXPOSE 8080 

# Start Gunicorn with Gevent worker for Flask-SocketIO
CMD ["gunicorn", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-b", "0.0.0.0:8080", "main:app"]

