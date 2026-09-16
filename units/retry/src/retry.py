"""Retry with exponential backoff.

Sleep and jitter are injectable, so retry policy is testable without waiting.
"""
from __future__ import annotations

import time
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")


class RetryExhausted(Exception):
    """Raised when every attempt failed. Carries the last exception."""

    def __init__(self, attempts: int, last: BaseException):
        super().__init__(f"all {attempts} attempts failed: {last!r}")
        self.attempts = attempts
        self.last = last


def backoff_delays(
    attempts: int,
    base: float = 0.5,
    factor: float = 2.0,
    cap: float = 30.0,
) -> list[float]:
    """Delays between attempts. One fewer than `attempts` - the first is immediate."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    if base <= 0:
        raise ValueError("base must be positive")
    delays = []
    d = base
    for _ in range(attempts - 1):
        delays.append(min(d, cap))
        d *= factor
    return delays


def retry(
    fn: Callable[[], T],
    attempts: int = 3,
    base: float = 0.5,
    factor: float = 2.0,
    cap: float = 30.0,
    retry_on: Iterable[type[BaseException]] = (Exception,),
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Call fn until it returns. Re-raises immediately for non-retryable errors."""
    retry_on = tuple(retry_on)
    delays = backoff_delays(attempts, base, factor, cap)
    last: BaseException | None = None
    for i in range(attempts):
        try:
            return fn()
        except retry_on as exc:
            last = exc
            if i < len(delays):
                sleep(delays[i])
    raise RetryExhausted(attempts, last)
