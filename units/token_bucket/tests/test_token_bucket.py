import pytest

from token_bucket import TokenBucket


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def test_starts_full():
    clock = FakeClock()
    b = TokenBucket(capacity=5, refill_per_sec=1.0, clock=clock)
    assert b.tokens == 5.0


def test_take_consumes():
    clock = FakeClock()
    b = TokenBucket(capacity=5, refill_per_sec=1.0, clock=clock)
    assert b.take(2) is True
    assert b.tokens == 3.0


def test_take_refuses_when_short_and_consumes_nothing():
    clock = FakeClock()
    b = TokenBucket(capacity=3, refill_per_sec=1.0, clock=clock)
    assert b.take(3) is True
    assert b.take(1) is False
    assert b.tokens == 0.0


def test_refills_over_time():
    clock = FakeClock()
    b = TokenBucket(capacity=10, refill_per_sec=2.0, clock=clock)
    b.take(10)
    clock.advance(3.0)
    assert b.tokens == 6.0


def test_refill_caps_at_capacity():
    clock = FakeClock()
    b = TokenBucket(capacity=4, refill_per_sec=5.0, clock=clock)
    b.take(4)
    clock.advance(100.0)
    assert b.tokens == 4.0


def test_wait_time_zero_when_available():
    clock = FakeClock()
    b = TokenBucket(capacity=5, refill_per_sec=1.0, clock=clock)
    assert b.wait_time(3) == 0.0


def test_wait_time_when_short():
    clock = FakeClock()
    b = TokenBucket(capacity=5, refill_per_sec=2.0, clock=clock)
    b.take(5)
    assert b.wait_time(4) == 2.0


def test_rejects_bad_capacity():
    with pytest.raises(ValueError):
        TokenBucket(capacity=0, refill_per_sec=1.0)


def test_rejects_bad_refill():
    with pytest.raises(ValueError):
        TokenBucket(capacity=1, refill_per_sec=0)


def test_rejects_bad_take():
    b = TokenBucket(capacity=2, refill_per_sec=1.0, clock=FakeClock())
    with pytest.raises(ValueError):
        b.take(0)
