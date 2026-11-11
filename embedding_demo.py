"""
embedding_demo.py - Compare word-count vs embedding similarity.
Requires: pip install sentence-transformers
"""

import sys
from analyzer import cosine_similarity, cosine_from_vectors

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

from sentence_transformers import SentenceTransformer

# Lightweight multilingual model runnable on CPU
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

documents = [
    "Học phí của một học kỳ là 12tr cho chương trình chuẩn.",
    "Sinh viên phải tham dự ít nhất 80% số buổi học.",
    "Đội tuyển bóng đá giành chiến thắng tối qua.",
]
queries = [
    "Mình phải đóng bao nhiêu tiền để đi học?",   # Query with low lexical overlap
    "Tiền học một kỳ là bao nhiêu?",
]

print("Đang tải mô hình (lần đầu sẽ hơi lâu)...")
model = SentenceTransformer(MODEL_NAME)

# encode() returns a vector for each sentence
doc_vectors = model.encode(documents)
query_vectors = model.encode(queries)


def to_dict(vector) -> dict:
    """Convert vector to dict {index: value} for cosine_from_vectors."""
    return {i: float(x) for i, x in enumerate(vector)}


print(f"\nMỗi câu được đổi thành vector {len(doc_vectors[0])} chiều.\n")

for q, q_vec in zip(queries, query_vectors):
    print("Câu hỏi:", q)
    for d, d_vec in zip(documents, doc_vectors):
        by_words = cosine_similarity(q, d)                              # Word-count based
        by_embedding = cosine_from_vectors(to_dict(q_vec), to_dict(d_vec))  # Embedding based
        print(f"  đếm từ: {by_words:.3f} | embedding: {by_embedding:.3f} | {d}")
    print()