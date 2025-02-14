import pickle
import os


pickle_hdbscan = os.path.abspath(os.path.join("app/pickles/hdbscan_model.pkl"))
pickle_umap = os.path.abspath(os.path.join("app/pickles/umap_reducer.pkl"))

with open(pickle_hdbscan, "rb") as f:
    hdbscan_model = pickle.load(f)

with open(pickle_umap, "rb") as f:
    umap_reducer = pickle.load(f)


def cluster(embeddings):
    reduced_embeddings = umap_reducer.fit_transform(embeddings)
    print(reduced_embeddings)
    hdbscan_model.fit(reduced_embeddings)
    return hdbscan_model.labels_