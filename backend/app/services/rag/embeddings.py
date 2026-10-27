import math
import re
import hashlib
from typing import List

VECTOR_DIM = 128

STOPWORDS = {
    "the", "a", "an", "in", "on", "at", "to", "for", "of", "with", "is", "was",
    "are", "were", "by", "from", "and", "or", "who", "what", "where", "when",
    "how", "why", "which", "this", "that", "these", "those", "it", "its"
}

def generate_text_embedding(text: str) -> List[float]:
    """
    Generates a deterministic 128-dimensional normalized dense embedding vector
    for multilingual historical text (English, Devanagari, Gujarati).
    Uses hashed character n-grams and term tokens with L2 normalization.
    """
    clean = text.lower().strip()
    if not clean:
        return [0.0] * VECTOR_DIM

    vector = [0.0] * VECTOR_DIM

    # Tokenize words and character 3-grams to capture Indic morphology and root stems
    raw_tokens = re.findall(r'[\w]+', clean)
    tokens = [t for t in raw_tokens if t not in STOPWORDS]
    if not tokens:
        tokens = raw_tokens

    for token in tokens:
        h = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16)
        idx = h % VECTOR_DIM
        weight = math.log(len(token) + 1.0)
        vector[idx] += weight

        # Subword character n-grams
        if len(token) >= 3:
            for i in range(len(token) - 2):
                ngram = token[i:i+3]
                nh = int(hashlib.sha256(ngram.encode('utf-8')).hexdigest(), 16)
                nidx = nh % VECTOR_DIM
                vector[nidx] += 0.5

    # L2 Normalization
    norm = math.sqrt(sum(x * x for x in vector))
    if norm > 0.0:
        vector = [round(x / norm, 5) for x in vector]

    return vector

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes cosine similarity between two normalized vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    return max(0.0, min(1.0, dot))
