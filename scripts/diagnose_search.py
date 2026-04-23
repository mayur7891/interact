import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from app import create_app, mongo
from app.services.preprocessing import preprocess_text
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = create_app()
with app.app_context():
    # 1. Check video_ids and embedding counts
    print("=== DB DIAGNOSIS ===")
    total = mongo.db.comments.count_documents({})
    print(f"Total comments: {total}")

    comments_sample = list(mongo.db.comments.find({}, {"video_id": 1, "comment": 1, "embedding": 1}).limit(5))
    for c in comments_sample:
        emb = c.get("embedding", [])
        print(f"  video_id={repr(c.get('video_id'))} type={type(c.get('video_id')).__name__} emb_len={len(emb) if emb else 0} comment={c.get('comment','')[:40]}")

    # 2. Count per video_id
    print("\n=== video_id distribution ===")
    pipeline = [{"$group": {"_id": "$video_id", "count": {"$sum": 1}}}]
    for doc in mongo.db.comments.aggregate(pipeline):
        print(f"  video_id={repr(doc['_id'])} type={type(doc['_id']).__name__} count={doc['count']}")

    # 3. Try fetching for video_id=1 (int) vs "1" (string)
    print("\n=== Fetch test for int(1) vs str('1') ===")
    int_count = mongo.db.comments.count_documents({"video_id": 1, "embedding": {"$exists": True, "$ne": []}})
    str_count = mongo.db.comments.count_documents({"video_id": "1", "embedding": {"$exists": True, "$ne": []}})
    print(f"  video_id=1 (int) with embeddings: {int_count}")
    print(f"  video_id='1' (str) with embeddings: {str_count}")

    # 4. Test embedding generation
    print("\n=== Embedding test ===")
    query = "Been a fan since the 80s, still love it"
    emb = preprocess_text(query)
    print(f"  Query embedding length: {len(emb)}")

    # 3b. Test new query (embedding.0 $exists)
    dot0_count = mongo.db.comments.count_documents({"video_id": 1, "embedding.0": {"$exists": True}})
    print(f"  video_id=1 with embedding.0 $exists (NEW query): {dot0_count}")

    # 5. Simulate the full search for video_id=1 with lowered threshold
    print("\n=== Cosine similarity test (int video_id=1, NEW query) ===")
    records = list(mongo.db.comments.find({"video_id": 1, "embedding.0": {"$exists": True}}, {"comment": 1, "embedding": 1}))
    print(f"  Records found: {len(records)}")
    if records:
        q_emb = np.array(emb)
        embeddings = np.array([r["embedding"] for r in records])
        scores = cosine_similarity(q_emb.reshape(1, -1), embeddings)[0]
        print(f"  Score range: min={scores.min():.4f} max={scores.max():.4f} mean={scores.mean():.4f}")
        print(f"  Above 0.35: {(scores >= 0.35).sum()}")
        print(f"  Above 0.2: {(scores >= 0.2).sum()}")
        print(f"  Above 0.1: {(scores >= 0.1).sum()}")
        # Show top 3
        top_idx = scores.argsort()[::-1][:3]
        print("  Top 3 results:")
        for i in top_idx:
            print(f"    score={scores[i]:.4f} | {records[i].get('comment','')[:60]}")
