"""
knowledge_base.py - Load error profiles, vectorize with TF-IDF, and rank by cosine similarity.
"""

import json

from analyzer import compute_idf, tfidf_vector, cosine_from_vectors
from text_processor import tokenize


def with_bigrams(tokens: list[str]) -> list[str]:
    """Append bigrams to token list to capture phrases."""
    return tokens + [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]


def entry_text(entry: dict) -> str:
    """Combine entry fields into a single text document for vectorization."""
    parts = [entry["ten"], " ".join(entry["error_type"]),
             entry["trieu_chung"], " ".join(entry["thong_bao_mau"])]
    return " ".join(parts)


class KnowledgeBase:
    def __init__(self, entries: list[dict], use_bigrams: bool = True):
        self.entries = entries
        self.use_bigrams = use_bigrams
        docs = [self._tokens(entry_text(e)) for e in entries]
        self.idf = compute_idf(docs)
        self.vectors = [tfidf_vector(d, self.idf) for d in docs]

    def _tokens(self, text: str) -> list[str]:
        # Strip accents so queries match regardless of diacritics
        tokens = tokenize(text, keep_accents=False)
        return with_bigrams(tokens) if self.use_bigrams else tokens

    def search(self, query: str) -> list[tuple[float, dict]]:
        """Score all entries against query and return (score, entry) sorted in descending order."""
        q_vec = tfidf_vector(self._tokens(query), self.idf)
        scored = [(cosine_from_vectors(q_vec, v), e)
                  for v, e in zip(self.vectors, self.entries)]
        scored.sort(key=lambda item: item[0], reverse=True)
        return scored


def load_knowledge_base(path: str, use_bigrams: bool = True) -> KnowledgeBase:
    with open(path, encoding="utf-8") as f:
        return KnowledgeBase(json.load(f), use_bigrams=use_bigrams)
