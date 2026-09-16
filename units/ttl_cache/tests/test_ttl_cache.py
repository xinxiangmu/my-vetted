import pytest

from ttl_cache import TTLCache


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def make(maxsize=10, ttl=60.0):
    clock = FakeClock()
    return TTLCache(maxsize=maxsize, ttl=ttl, clock=clock), clock


def test_set_then_get():
    c, _ = make()
    c.set("a", 1)
    assert c.get("a") == 1


def test_missing_key_returns_default():
    c, _ = make()
    assert c.get("nope", "fallback") == "fallback"


def test_entry_expires_after_ttl():
    c, clock = make(ttl=10.0)
    c.set("a", 1)
    clock.advance(10.0)
    assert c.get("a") is None


def test_entry_survives_until_ttl():
    c, clock = make(ttl=10.0)
    c.set("a", 1)
    clock.advance(9.0)
    assert c.get("a") == 1


def test_per_entry_ttl_overrides_default():
    c, clock = make(ttl=100.0)
    c.set("a", 1, ttl=5.0)
    clock.advance(6.0)
    assert c.get("a") is None


def test_lru_eviction_at_maxsize():
    c, _ = make(maxsize=2)
    c.set("a", 1)
    c.set("b", 2)
    c.set("c", 3)
    assert c.get("a") is None
    assert c.get("b") == 2
    assert c.get("c") == 3


def test_get_refreshes_recency():
    c, _ = make(maxsize=2)
    c.set("a", 1)
    c.set("b", 2)
    c.get("a")
    c.set("c", 3)
    assert c.get("a") == 1
    assert c.get("b") is None


def test_contains_respects_expiry():
    c, clock = make(ttl=5.0)
    c.set("a", 1)
    assert "a" in c
    clock.advance(5.0)
    assert "a" not in c


def test_len_excludes_expired():
    c, clock = make(ttl=5.0)
    c.set("a", 1)
    c.set("b", 2)
    clock.advance(5.0)
    assert len(c) == 0


def test_purge_reports_count():
    c, clock = make(ttl=5.0)
    c.set("a", 1)
    c.set("b", 2)
    clock.advance(5.0)
    assert c.purge() == 2


def test_delete_reports_whether_present():
    c, _ = make()
    c.set("a", 1)
    assert c.delete("a") is True
    assert c.delete("a") is False


def test_hit_and_miss_counters():
    c, _ = make()
    c.set("a", 1)
    c.get("a")
    c.get("b")
    assert (c.hits, c.misses) == (1, 1)


def test_clear_resets_counters():
    c, _ = make()
    c.set("a", 1)
    c.get("a")
    c.clear()
    assert (len(c), c.hits, c.misses) == (0, 0, 0)


def test_get_or_set_computes_once():
    c, _ = make()
    calls = {"n": 0}

    def factory():
        calls["n"] += 1
        return "value"

    assert c.get_or_set("k", factory) == "value"
    assert c.get_or_set("k", factory) == "value"
    assert calls["n"] == 1


def test_rejects_bad_maxsize():
    with pytest.raises(ValueError):
        TTLCache(maxsize=0)


def test_rejects_bad_ttl():
    with pytest.raises(ValueError):
        TTLCache(ttl=0)
