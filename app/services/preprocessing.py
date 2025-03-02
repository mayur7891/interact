import pickle
import pandas as pd
import os
import re
from azure.storage.blob import BlobServiceClient

# Azure Storage details
STORAGE_ACCOUNT_NAME = "interact1234554321"
STORAGE_CONTAINER_NAME = "pickles"
CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=interact1234554321;AccountKey=fammTXpTZ+RskUuBAjqncq1oec2nVyRevgsCraRusTg9u7+kkp3rRSzC72Wy2q3AKfZkgm28sgUB+ASt8SyBEQ==;EndpointSuffix=core.windows.net "

# Function to download pickle files from Azure Blob Storage
def download_pickle(blob_name, local_path):
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=STORAGE_CONTAINER_NAME, blob=blob_name)
    
    # Download and save file locally
    with open(local_path, "wb") as f:
        f.write(blob_client.download_blob().readall())

# Define paths to store pickle files locally
local_sentiment_path = "app/pickles/sentiment_pipeline.pkl"
local_sbert_path = "app/pickles/sbert_pipeline.pkl"

# Ensure the directory exists
os.makedirs("app/pickles", exist_ok=True)

# Download pickle files from Azure
download_pickle("sentiment_pipeline.pkl", local_sentiment_path)
download_pickle("sbert_pipeline.pkl", local_sbert_path)

# Load the pickle files after downloading
with open(local_sentiment_path, "rb") as f:
    sentiment_analyzer, tokenizer = pickle.load(f)

with open(local_sbert_path, "rb") as f:
    sbert_model = pickle.load(f)

# Function to truncate text for tokenizer
def truncate_comment(comment):
    tokens = tokenizer.encode(comment, truncation=True, max_length=512)
    return tokenizer.decode(tokens, skip_special_tokens=True)

# Function to analyze sentiment
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

# Function to preprocess text and get SBERT embeddings
def preprocess_text(text):
    text = re.sub(r"[^A-Za-z0-9.,!?(){}[\]\"'@#&%+=<>*/-]+", " ", text)
    text = text.lower().strip()
    if len(text) == 0:
        return []
    text_embedding = sbert_model.encode(text, normalize_embeddings=True).tolist()
    return text_embedding