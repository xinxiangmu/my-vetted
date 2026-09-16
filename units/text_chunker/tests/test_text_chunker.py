import pytest

from text_chunker import chunk, total_chars


def test_empty_text_yields_nothing():
    assert chunk("") == []
    assert chunk("   \n  ") == []


def test_short_text_is_one_chunk():
    assert chunk("hello world", size=100, overlap=10) == ["hello world"]


def test_every_chunk_respects_size():
    text = ". ".join(f"sentence number {i}" for i in range(80))
    for c in chunk(text, size=120, overlap=20):
        assert len(c) <= 120


def test_long_text_produces_several_chunks():
    text = ". ".join(f"sentence number {i}" for i in range(80))
    assert len(chunk(text, size=120, overlap=20)) > 1


def test_overlap_repeats_tail_of_previous_chunk():
    text = ". ".join(f"sentence {i}" for i in range(40))
    chunks = chunk(text, size=100, overlap=25)
    assert chunks[1].startswith(chunks[0][-25:].strip()[:10])


def test_zero_overlap_does_not_repeat():
    text = ". ".join(f"sentence {i}" for i in range(40))
    chunks = chunk(text, size=100, overlap=0)
    assert total_chars(chunks) <= len(text) + len(chunks)


def test_word_longer_than_size_is_hard_split():
    chunks = chunk("x" * 250, size=100, overlap=0)
    assert len(chunks) == 3
    assert all(len(c) <= 100 for c in chunks)


def test_no_content_is_lost_without_overlap():
    text = "alpha beta gamma delta epsilon zeta eta theta"
    joined = " ".join(chunk(text, size=20, overlap=0))
    for word in text.split():
        assert word in joined


def test_rejects_zero_size():
    with pytest.raises(ValueError):
        chunk("abc", size=0)


def test_rejects_negative_overlap():
    with pytest.raises(ValueError):
        chunk("abc", size=10, overlap=-1)


def test_rejects_overlap_not_smaller_than_size():
    with pytest.raises(ValueError):
        chunk("abc", size=10, overlap=10)


def test_splits_on_chinese_sentence_ends():
    text = "第一句话。" * 30
    chunks = chunk(text, size=50, overlap=5)
    assert len(chunks) > 1
    assert all(len(c) <= 50 for c in chunks)


def test_total_chars_sums_chunks():
    assert total_chars(["ab", "cde"]) == 5
