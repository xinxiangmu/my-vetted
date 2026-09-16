import pytest

from batch_iter import batched, chunk_by, dedupe, take, windowed


def counter(n):
    """A generator, so laziness is observable."""
    for i in range(n):
        yield i


def test_batched_splits_evenly():
    assert list(batched(range(6), 2)) == [[0, 1], [2, 3], [4, 5]]


def test_batched_final_batch_is_short():
    assert list(batched(range(5), 2)) == [[0, 1], [2, 3], [4]]


def test_batched_size_larger_than_input():
    assert list(batched([1, 2], 10)) == [[1, 2]]


def test_batched_empty_input():
    assert list(batched([], 3)) == []


def test_batched_rejects_zero_size():
    with pytest.raises(ValueError):
        list(batched([1], 0))


def test_batched_is_lazy():
    gen = batched(counter(1000), 2)
    assert next(gen) == [0, 1]


def test_windowed_slides_by_one():
    assert list(windowed(range(4), 2)) == [[0, 1], [1, 2], [2, 3]]


def test_windowed_respects_step():
    assert list(windowed(range(5), 2, step=2)) == [[0, 1], [2, 3]]


def test_windowed_yields_nothing_when_input_too_short():
    assert list(windowed([1, 2], 3)) == []


def test_windowed_exact_length_yields_one():
    assert list(windowed([1, 2, 3], 3)) == [[1, 2, 3]]


def test_windowed_rejects_zero_size():
    with pytest.raises(ValueError):
        list(windowed([1], 0))


def test_windowed_rejects_zero_step():
    with pytest.raises(ValueError):
        list(windowed([1, 2], 2, step=0))


def test_dedupe_keeps_first_occurrence():
    assert list(dedupe([1, 2, 1, 3, 2])) == [1, 2, 3]


def test_dedupe_preserves_order():
    assert list(dedupe(["b", "a", "b"])) == ["b", "a"]


def test_dedupe_with_key():
    rows = [{"id": 1, "v": "a"}, {"id": 1, "v": "b"}, {"id": 2, "v": "c"}]
    assert [r["v"] for r in dedupe(rows, key=lambda r: r["id"])] == ["a", "c"]


def test_dedupe_empty():
    assert list(dedupe([])) == []


def test_chunk_by_groups_consecutive():
    assert list(chunk_by([1, 1, 2, 2, 1], key=lambda x: x)) == [[1, 1], [2, 2], [1]]


def test_chunk_by_does_not_sort():
    out = list(chunk_by("aabba", key=str))
    assert len(out) == 3


def test_chunk_by_empty():
    assert list(chunk_by([], key=str)) == []


def test_chunk_by_single_group():
    assert list(chunk_by([5, 5, 5], key=lambda x: x)) == [[5, 5, 5]]


def test_take_returns_prefix():
    assert take(range(10), 3) == [0, 1, 2]


def test_take_more_than_available():
    assert take([1, 2], 10) == [1, 2]


def test_take_zero():
    assert take(range(10), 0) == []


def test_take_rejects_negative():
    with pytest.raises(ValueError):
        take([1], -1)


def test_take_does_not_exhaust_source():
    gen = counter(100)
    take(gen, 2)
    assert next(gen) == 2
