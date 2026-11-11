"""Tests for analyzer.py. Usage: python test_analyzer.py"""

import math
from analyzer import (word_frequency, top_words, basic_stats, compute_tf, compute_idf,
                      tfidf_vector, tfidf_keywords, jaccard_similarity,
                      cosine_from_vectors, cosine_similarity)


def test_word_frequency_and_top_words():
    text = "Học phí học kỳ. Học phí cao."
    freq = word_frequency(text)
    assert freq["học"] == 3 and freq["phí"] == 2
    assert top_words(text, 1) == [("học", 3)]
    # Stopwords are removed
    assert "của" not in word_frequency("học phí của trường")


def test_basic_stats():
    stats = basic_stats("Hôm nay trời đẹp. Bạn đi học chưa? Tôi đi rồi!")
    assert stats["so_cau"] == 3
    assert stats["so_tu"] == 11          # Includes stopwords
    assert stats["do_dai_cau_tb"] == round(11 / 3, 2)


def test_basic_stats_empty():
    stats = basic_stats("")
    assert stats["so_tu"] == 0 and stats["so_cau"] == 0
    assert stats["do_dai_cau_tb"] == 0.0 and stats["do_da_dang_tu"] == 0.0


def test_tf_idf_basics():
    assert compute_tf([]) == {}
    assert compute_tf(["a", "a", "b"]) == {"a": 2 / 3, "b": 1 / 3}
    docs = [["học", "phí"], ["học", "bổng"]]
    idf = compute_idf(docs)
    # Rare words have higher IDF
    assert idf["phí"] > idf["học"]
    assert math.isclose(idf["học"], math.log(3 / 3) + 1)
    # Unseen words are omitted
    assert "xyz" not in tfidf_vector(["học", "xyz"], idf)


def test_tfidf_keywords():
    text = "Học phí đóng đầu kỳ. Học phí nộp muộn bị phạt. Điểm thi cuối kỳ."
    keywords = tfidf_keywords(text, 3)
    assert len(keywords) == 3
    scores = [s for _, s in keywords]
    assert scores == sorted(scores, reverse=True)      # Descending order
    assert tfidf_keywords("", 3) == []
    # Prioritize words distinctive to corpus
    corpus = ["bóng đá sân cỏ", "học phí học kỳ", "bóng đá trận đấu"]
    assert tfidf_keywords("học phí bóng đá", 1, corpus)[0][0] == "học"  # 'học' is rarer in corpus


def test_jaccard():
    assert jaccard_similarity("học phí kỳ", "học phí kỳ") == 1.0
    assert jaccard_similarity("học phí", "bóng đá") == 0.0
    assert jaccard_similarity("", "") == 0.0
    assert math.isclose(jaccard_similarity("học phí", "học bổng"), 1 / 3)


def test_cosine():
    assert math.isclose(cosine_similarity("học phí kỳ", "học phí kỳ"), 1.0)
    assert cosine_similarity("học phí", "bóng đá") == 0.0
    assert cosine_similarity("", "học") == 0.0
    assert math.isclose(cosine_from_vectors({"a": 1}, {"a": 5}), 1.0)   # Same direction
    assert cosine_from_vectors({"a": 1}, {"b": 1}) == 0.0


if __name__ == "__main__":
    test_word_frequency_and_top_words()
    test_basic_stats()
    test_basic_stats_empty()
    test_tf_idf_basics()
    test_tfidf_keywords()
    test_jaccard()
    test_cosine()
    print("Tất cả test analyzer đều qua!")