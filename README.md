# Interact - Social Media Comment Analysis Platform

A Flask-based web application for analyzing and clustering social media video comments using machine learning. Features real-time WebSocket communication, sentiment analysis, comment clustering, and AI-powered summarization.

## Features

- **Real-time Comment Analysis**: Process and analyze video comments in real-time
- **Sentiment Analysis**: Automatic sentiment classification using DistilBERT
- **Comment Clustering**: Group similar comments using UMAP and HDBSCAN
- **AI Summarization**: Generate intelligent summaries using Google Gemini
- **WebSocket Support**: Real-time updates and notifications
- **JWT Authentication**: Secure user authentication
- **MongoDB Integration**: Scalable document-based storage

## Tech Stack

- **Backend**: Flask, Flask-SocketIO
- **Database**: MongoDB
- **ML/AI**:
  - Sentiment: DistilBERT (transformers)
  - Embeddings: Sentence-BERT (all-MiniLM-L6-v2)
  - Clustering: UMAP + HDBSCAN
  - Summarization: Google Gemini API
- **Authentication**: JWT
- **Deployment**: Heroku-ready (Procfile included)

## Prerequisites

- Python 3.11+
- MongoDB (local or Atlas)
- Google Gemini API key (optional, for summarization)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd interact
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

Create a `.env` file with the following variables:

```env
# Required
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority

# Optional
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.5-flash

# MongoDB tuning (optional)
MONGO_MAX_POOL_SIZE=50
MONGO_MIN_POOL_SIZE=10
MONGO_CONNECT_TIMEOUT_MS=5000
MONGO_SERVER_SELECTION_TIMEOUT_MS=5000
MONGO_SOCKET_TIMEOUT_MS=10000
```

## Database Setup

The application automatically creates necessary indexes on startup. Ensure your MongoDB instance is accessible via the `MONGO_URI`.

For a free MongoDB instance, use [MongoDB Atlas](https://www.mongodb.com/atlas).

## Running Locally

1. Start the application:

```bash
python app.py
```

2. The API will be available at `http://localhost:5000`

3. API endpoint: `GET /api` - Health check

## API Endpoints

### Authentication

- `POST /auth/login` - User login
- `POST /auth/register` - User registration

### Videos

- `GET /video/videos` - Get all videos
- `POST /video/video` - Add new video
- `GET /video/video/<video_id>` - Get video details

### Comments

- `GET /comments/comments/<video_id>` - Get comments for video
- `POST /comments/comment` - Add new comment
- `DELETE /comments/comment/<comment_id>` - Delete comment

### ML Analysis

- `GET /ml/sentiment/<video_id>` - Get sentiment analysis
- `GET /ml/clusters/<video_id>` - Get comment clusters
- `GET /ml/summary/<video_id>` - Get AI summary

## WebSocket Events

The application uses SocketIO for real-time communication:

- `connect` - Client connection
- `disconnect` - Client disconnection
- `comment_added` - New comment notification
- `analysis_complete` - ML analysis completion

## Deployment

### Heroku (Free Tier)

1. Create a Heroku account and install Heroku CLI

2. Create a new app:

```bash
heroku create your-app-name
```

3. Set environment variables:

```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set JWT_SECRET_KEY=your-jwt-secret
heroku config:set MONGO_URI=your-mongodb-uri
heroku config:set GEMINI_API_KEY=your-gemini-key  # optional
```

4. Deploy:

```bash
git push heroku main
```

5. Scale the web dyno:

```bash
heroku ps:scale web=1
```

### Other Free Platforms

- **Render**: Supports Python web services with free tier
- **Railway**: Free tier for web applications
- **Fly.io**: Free tier with generous limits

For platforms other than Heroku, you may need to adjust the Procfile or create a Dockerfile.

## Project Structure

```
interact/
├── app.py                 # Main application entry point
├── Procfile              # Heroku deployment configuration
├── requirements.txt      # Python dependencies
├── runtime.txt          # Python version for Heroku
├── .env.example         # Environment variables template
├── app/
│   ├── __init__.py      # Flask app factory
│   ├── config.py        # Configuration settings
│   ├── models/          # Data models
│   ├── routes/          # API route handlers
│   ├── services/        # Business logic and ML services
│   ├── sockets/         # WebSocket event handlers
│   └── utils/           # Utility functions
└── scripts/             # Maintenance and diagnostic scripts
```

## ML Models

The application uses several ML models:

1. **Sentiment Analysis**: DistilBERT fine-tuned on SST-2 dataset
2. **Text Embeddings**: Sentence-BERT all-MiniLM-L6-v2 (384 dimensions)
3. **Dimensionality Reduction**: UMAP (5 components)
4. **Clustering**: HDBSCAN (minimum cluster size: 5)
5. **Summarization**: Google Gemini 2.5 Flash

Models are loaded on startup. If loading fails, features degrade gracefully.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub.
