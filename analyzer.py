"""
analyzer.py - Text analysis: word frequency, basic stats, TF-IDF keywords, and similarity.
"""

import math
from collections import Counter

from text_processor import tokenize, split_sentences


# ---------------------------------------------------------------------------
# 1. Word frequency and basic statistics
# ---------------------------------------------------------------------------

def word_frequency(text: str, remove_stopwords: bool = True) -> Counter:
    """Count word frequencies."""
    return Counter(tokenize(text, remove_stopwords=remove_stopwords))


def top_words(text: str, n: int = 10) -> list[tuple[str, int]]:
    """Return top n most frequent words as [(word, count), ...]."""
    return word_frequency(text).most_common(n)


def basic_stats(text: str) -> dict:
    """Calculate basic statistics without removing stopwords."""
    sentences = split_sentences(text)
    words = tokenize(text, remove_stopwords=False)

    num_words = len(words)
    num_sentences = len(sentences)
    unique_words = len(set(words))

    # Avoid division by zero for empty text
    avg_len = num_words / num_sentences if num_sentences else 0.0
    diversity = unique_words / num_words if num_words else 0.0

    return {
        "so_tu": num_words,
        "so_cau": num_sentences,
        "so_tu_khac_nhau": unique_words,
        "do_dai_cau_tb": round(avg_len, 2),
        "do_da_dang_tu": round(diversity, 2),
    }


# ---------------------------------------------------------------------------
# 2. TF-IDF
# ---------------------------------------------------------------------------
# TF (term frequency): term importance within document
# IDF (inverse document frequency): term rarity across corpus
# TF-IDF = TF * IDF: high value indicates distinctive keyword

def compute_tf(tokens: list[str]) -> dict[str, float]:
    """Compute term frequency (TF = word_count / total_tokens)."""
    total = len(tokens)
    if total == 0:
        return {}
    return {word: count / total for word, count in Counter(tokens).items()}


def compute_idf(documents: list[list[str]]) -> dict[str, float]:
    """Compute inverse document frequency: IDF = log((1 + N) / (1 + df)) + 1."""
    n_docs = len(documents)
    doc_freq = Counter()
    for doc in documents:
        doc_freq.update(set(doc))   # Count each term once per document
    return {
        word: math.log((1 + n_docs) / (1 + df)) + 1
        for word, df in doc_freq.items()
    }


def tfidf_vector(tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
    """Generate TF-IDF vector; ignore unseen words."""
    tf = compute_tf(tokens)
    return {word: tf_value * idf[word] for word, tf_value in tf.items() if word in idf}


def tfidf_keywords(text: str, n: int = 5, corpus: list[str] | None = None) -> list[tuple[str, float]]:
    """Extract top n TF-IDF keywords. Uses sentences as documents if corpus is None."""
    if corpus is None:
        documents = [tokenize(s) for s in split_sentences(text)]
    else:
        documents = [tokenize(d) for d in corpus]

    idf = compute_idf(documents)
    vector = tfidf_vector(tokenize(text), idf)

    # Sort by descending score, then alphabetically
    ranked = sorted(vector.items(), key=lambda item: (-item[1], item[0]))
    return [(word, round(score, 4)) for word, score in ranked[:n]]


# ---------------------------------------------------------------------------
# 3. Text similarity
# ---------------------------------------------------------------------------

def jaccard_similarity(text1: str, text2: str) -> float:
    """Compute Jaccard similarity: |A & B| / |A | B| between token sets."""
    a, b = set(tokenize(text1)), set(tokenize(text2))
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def cosine_from_vectors(v1: dict[str, float], v2: dict[str, float]) -> float:
    """Compute cosine similarity between two weight vectors."""
    shared = set(v1) & set(v2)
    dot = sum(v1[w] * v2[w] for w in shared)
    norm1 = math.sqrt(sum(x * x for x in v1.values()))
    norm2 = math.sqrt(sum(x * x for x in v2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def cosine_similarity(text1: str, text2: str) -> float:
    """Compute cosine similarity using word frequencies."""
    v1 = dict(Counter(tokenize(text1)))
    v2 = dict(Counter(tokenize(text2)))
    return cosine_from_vectors(v1, v2)