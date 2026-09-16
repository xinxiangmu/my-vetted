import pytest

from retry import RetryExhausted, backoff_delays, retry


class Sleeper:
    def __init__(self):
        self.calls = []

    def __call__(self, seconds):
        self.calls.append(seconds)


def test_delays_are_one_fewer_than_attempts():
    assert len(backoff_delays(3)) == 2


def test_delays_grow_by_factor():
    assert backoff_delays(4, base=1.0, factor=2.0) == [1.0, 2.0, 4.0]


def test_delays_respect_cap():
    assert backoff_delays(4, base=10.0, factor=10.0, cap=25.0) == [10.0, 25.0, 25.0]


def test_single_attempt_has_no_delay():
    assert backoff_delays(1) == []


def test_rejects_zero_attempts():
    with pytest.raises(ValueError):
        backoff_delays(0)


def test_rejects_non_positive_base():
    with pytest.raises(ValueError):
        backoff_delays(3, base=0)


def test_returns_first_success_without_sleeping():
    s = Sleeper()
    assert retry(lambda: 42, sleep=s) == 42
    assert s.calls == []


def test_retries_until_success():
    s = Sleeper()
    state = {"n": 0}

    def flaky():
        state["n"] += 1
        if state["n"] < 3:
            raise RuntimeError("boom")
        return "ok"

    assert retry(flaky, attempts=5, base=1.0, sleep=s) == "ok"
    assert state["n"] == 3
    assert s.calls == [1.0, 2.0]


def test_raises_retry_exhausted_with_last_error():
    s = Sleeper()

    def always_fails():
        raise ValueError("nope")

    with pytest.raises(RetryExhausted) as exc:
        retry(always_fails, attempts=3, base=1.0, sleep=s)
    assert exc.value.attempts == 3
    assert isinstance(exc.value.last, ValueError)
    assert len(s.calls) == 2


def test_non_retryable_error_propagates_immediately():
    s = Sleeper()

    def bad():
        raise KeyError("fatal")

    with pytest.raises(KeyError):
        retry(bad, attempts=5, retry_on=(ValueError,), sleep=s)
    assert s.calls == []
