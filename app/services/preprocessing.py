import pandas as pd
import re

# ---------------------------------------------------------------------------
# Sentiment model — loaded directly via transformers (no pickle)
# ---------------------------------------------------------------------------
sentiment_pipeline = None
try:
    from transformers import pipeline as hf_pipeline
    sentiment_pipeline = hf_pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        truncation=True,
        max_length=512,
    )
    print("Sentiment model loaded.")
except Exception as e:
    print(f"WARNING: Could not load sentiment model: {e}")

# ---------------------------------------------------------------------------
# SBERT model — loaded directly via sentence-transformers (no pickle)
# Embeddings in DB are 384-dim → all-MiniLM-L6-v2
# ---------------------------------------------------------------------------
sbert_model = None
try:
    from sentence_transformers import SentenceTransformer
    sbert_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    print("SBERT model loaded.")
except Exception as e:
    print(f"WARNING: Could not load SBERT model: {e}")


def analyze_sentiment(comment):
    if pd.isna(comment) or not isinstance(comment, str) or comment.strip() == "":
        return "neutral"
    if sentiment_pipeline is None:
        return "neutral"
    try:
        result = sentiment_pipeline(comment[:512])[0]
        label = result["label"].lower()
        # distilbert SST-2 returns POSITIVE / NEGATIVE only
        if label == "positive":
            return "positive"
        elif label == "negative":
            return "negative"
        return "neutral"
    except Exception as e:
        print(f"Sentiment error: {e}")
        return "neutral"


def preprocess_text(text):
    text = re.sub(r"[^A-Za-z0-9.,!?(){}[\]\"'@#&%+=<>*/-]+", " ", text)
    text = text.lower().strip()
    if not text:
        return []
    if sbert_model is None:
        return []
    return sbert_model.encode(text, normalize_embeddings=True).tolist()