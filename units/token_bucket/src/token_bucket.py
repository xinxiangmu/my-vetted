"""Token bucket rate limiter.

Injectable clock, so callers can test throttling without sleeping.
"""
from __future__ import annotations

import time
from typing import Callable


class TokenBucket:
    """Allows `capacity` bursts, refilling at `refill_per_sec` tokens per second."""

    def __init__(
        self,
        capacity: int,
        refill_per_sec: float,
        clock: Callable[[], float] = time.monotonic,
    ):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        if refill_per_sec <= 0:
            raise ValueError("refill_per_sec must be positive")
        self.capacity = capacity
        self.refill_per_sec = refill_per_sec
        self._clock = clock
        self._tokens = float(capacity)
        self._last = clock()

    def _refill(self) -> None:
        now = self._clock()
        elapsed = now - self._last
        if elapsed > 0:
            self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_per_sec)
            self._last = now

    @property
    def tokens(self) -> float:
        self._refill()
        return self._tokens

    def take(self, n: int = 1) -> bool:
        """Consume n tokens. Returns False and consumes nothing if short."""
        if n < 1:
            raise ValueError("n must be at least 1")
        self._refill()
        if self._tokens < n:
            return False
        self._tokens -= n
        return True

    def wait_time(self, n: int = 1) -> float:
        """Seconds until n tokens are available. 0.0 if available now."""
        self._refill()
        if self._tokens >= n:
            return 0.0
        return (n - self._tokens) / self.refill_per_sec
