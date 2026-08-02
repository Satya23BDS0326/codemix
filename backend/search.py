import os
import faiss
import pickle
import numpy as np

from backend.retriever import get_embedding
from backend.codemix import normalize_for_alignment
from backend.language_detector import detect_language

VECTOR_PATH = "data/vector_store"
if not os.path.exists(f"{VECTOR_PATH}/index.faiss"):
    VECTOR_PATH = "backend/data/vector_store"

BM25_WEIGHT = 0.4
DENSE_WEIGHT = 0.6

index = faiss.read_index(f"{VECTOR_PATH}/index.faiss")

with open(f"{VECTOR_PATH}/chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

with open(f"{VECTOR_PATH}/bm25.pkl", "rb") as f:
    bm25 = pickle.load(f)

tfidf_vec = None
vec_path = "backend/data/tfidf_vectorizer.pkl"
if os.path.exists(vec_path):
    with open(vec_path, "rb") as f:
        tfidf_vec = pickle.load(f)


def _min_max_normalize(scores):
    scores = np.array(scores, dtype="float32")
    if scores.max() - scores.min() < 1e-9:
        return np.zeros_like(scores)
    return (scores - scores.min()) / (scores.max() - scores.min())


def _get_query_embedding(query: str) -> np.ndarray:
    target_dim = index.d

    if target_dim == 768:
        original_vec = get_embedding(query)
        normalized_query = normalize_for_alignment(query)
        if normalized_query == query:
            return original_vec
        normalized_vec = get_embedding(normalized_query)
        return (original_vec + normalized_vec) / 2.0
    else:
        if tfidf_vec is not None:
            vec = tfidf_vec.transform([query]).toarray()[0].astype("float32")
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            if len(vec) == target_dim:
                return vec

        vec = np.zeros((target_dim,), dtype="float32")
        return vec


def search(query, k=3, return_scores=False):
    lang = detect_language(query)

    q_vec = np.array([_get_query_embedding(query)]).astype("float32")
    candidate_pool = min(len(chunks), max(k * 5, 20))

    distances, indices = index.search(q_vec, candidate_pool)

    dense_scores_raw = -distances[0]
    dense_scores = _min_max_normalize(dense_scores_raw)

    tokenized_query = query.lower().split()
    bm25_scores_all = bm25.get_scores(tokenized_query)
    bm25_scores_candidates = [bm25_scores_all[i] for i in indices[0]]
    bm25_scores = _min_max_normalize(bm25_scores_candidates)

    combined = (BM25_WEIGHT * bm25_scores) + (DENSE_WEIGHT * dense_scores)

    ranked = sorted(
        zip(indices[0], combined),
        key=lambda x: x[1],
        reverse=True
    )[:k]

    results = [chunks[idx] for idx, _ in ranked]

    if return_scores:
        return results, [float(score) for _, score in ranked], lang

    return results
