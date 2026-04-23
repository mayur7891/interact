import umap
import hdbscan


def cluster(embeddings):
    reducer = umap.UMAP(n_components=5, random_state=42)
    reduced_embeddings = reducer.fit_transform(embeddings)

    clusterer = hdbscan.HDBSCAN(min_cluster_size=5, prediction_data=True)
    clusterer.fit(reduced_embeddings)
    return clusterer.labels_