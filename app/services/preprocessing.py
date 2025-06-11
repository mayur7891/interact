import pickle
import pandas as pd
import os
import re

# Define paths
pickle_sentiment_path = "app/pickles/sentiment_pipeline.pkl"
pickle_sbert_path = "app/pickles/sbert_pipeline.pkl"

# Ensure pickle files exist
if not os.path.exists(pickle_sentiment_path):
    raise FileNotFoundError(f"Pickle file not found: {pickle_sentiment_path}")

if not os.path.exists(pickle_sbert_path):
    raise FileNotFoundError(f"Pickle file not found: {pickle_sbert_path}")

# Load pickle files safely
with open(pickle_sentiment_path, "rb") as f:
    sentiment_analyzer, tokenizer = pickle.load(f)

with open(pickle_sbert_path, "rb") as f:
    sbert_model = pickle.load(f)

def truncate_comment(comment):
    tokens = tokenizer.encode(comment, truncation=True, max_length=512)
    return tokenizer.decode(tokens, skip_special_tokens=True)

def analyze_sentiment(comment):
    if pd.isna(comment) or not isinstance(comment, str) or comment.strip() == "":
        return "neutral", 0.0

    truncated_comment = truncate_comment(comment)

    try:
        result = sentiment_analyzer(truncated_comment)[0]
        sentiment = result["label"].lower()
    except Exception as e:
        print(f"Error processing comment: {comment[:50]}... | Error: {e}")
        sentiment = "neutral"

    return sentiment

def preprocess_text(text):
    text = re.sub(r"[^A-Za-z0-9.,!?(){}[\]\"'@#&%+=<>*/-]+", " ", text)
    text = text.lower().strip() 
    if len(text) == 0:
        return []
    text_embedding = sbert_model.encode(text, normalize_embeddings=True).tolist()
    return text_embedding
