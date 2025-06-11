import pickle
import os

# Define paths
pickle_hdbscan = "app/pickles/hdbscan_model.pkl"
pickle_umap = "app/pickles/umap_reducer.pkl"

# Ensure files exist
if not os.path.exists(pickle_hdbscan):
    raise FileNotFoundError(f"Pickle file not found: {pickle_hdbscan}")

if not os.path.exists(pickle_umap):
    raise FileNotFoundError(f"Pickle file not found: {pickle_umap}")

# Load pickle files safely
with open(pickle_hdbscan, "rb") as f:
    hdbscan_model = pickle.load(f)

with open(pickle_umap, "rb") as f:
    umap_reducer = pickle.load(f)

def cluster(embeddings):
    reduced_embeddings = umap_reducer.fit_transform(embeddings)
    print(reduced_embeddings)
    hdbscan_model.fit(reduced_embeddings)
    return hdbscan_model.labels_
