import os

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load model only once
model = SentenceTransformer("all-MiniLM-L6-v2")

# Store JD embedding globally
_jd_embedding = None


def initialize_jd(jd_text):
    global _jd_embedding
    _jd_embedding = model.encode(
        [jd_text],
        convert_to_numpy=True
    )


def encode_all_candidates(candidate_texts):
    """
    Encode all candidates at once using batch processing.
    This is 50-100x faster than encoding one at a time.
    """
    return model.encode(
        candidate_texts,
        convert_to_numpy=True,
        batch_size=256,
        show_progress_bar=True
    )


def encode_all_candidates_cached(candidate_texts, cache_path="outputs/candidate_embeddings.npy"):
    """
    Encode candidates once and reuse the embeddings on later runs.
    This makes repeated execution much faster.
    """
    if os.path.exists(cache_path):
        embeddings = np.load(cache_path)
        if len(embeddings) == len(candidate_texts):
            print(f"Loaded cached embeddings from {cache_path}")
            return embeddings

        print("Cached embeddings count does not match candidates. Rebuilding cache...")

    embeddings = encode_all_candidates(candidate_texts)
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    np.save(cache_path, embeddings)
    print(f"Saved embeddings cache to {cache_path}")
    return embeddings


def get_semantic_scores_bulk(candidate_embeddings):
    """
    Compute cosine similarity for all candidates at once.
    Returns a list of float scores.
    """
    similarities = cosine_similarity(
        _jd_embedding,
        candidate_embeddings
    )[0]  # shape: (num_candidates,)

    return [float(s) for s in similarities]


def get_semantic_score(candidate_text):
    """
    Single candidate scoring — kept for backward compatibility.
    Use encode_all_candidates + get_semantic_scores_bulk for bulk use.
    """
    candidate_embedding = model.encode(
        [candidate_text],
        convert_to_numpy=True
    )
    similarity = cosine_similarity(
        _jd_embedding,
        candidate_embedding
    )[0][0]

    return float(similarity)
