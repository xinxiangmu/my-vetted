"""In-memory cache with per-entry expiry and a size bound.

Clock is injectable, so expiry is testable without sleeping.
"""
from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any, Callable

_MISS = object()


class TTLCache:
    """Least-recently-used eviction at `maxsize`, plus time-based expiry."""

    def __init__(
        self,
        maxsize: int = 128,
        ttl: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ):
        if maxsize < 1:
            raise ValueError("maxsize must be at least 1")
        if ttl <= 0:
            raise ValueError("ttl must be positive")
        self.maxsize = maxsize
        self.ttl = ttl
        self._clock = clock
        self._data: OrderedDict[Any, tuple[float, Any]] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def __len__(self) -> int:
        self.purge()
        return len(self._data)

    def __contains__(self, key) -> bool:
        return self.get(key, _MISS) is not _MISS

    def purge(self) -> int:
        """Drop expired entries. Returns how many were removed."""
        now = self._clock()
        dead = [k for k, (expires, _) in self._data.items() if expires <= now]
        for k in dead:
            del self._data[k]
        return len(dead)

    def get(self, key, default=None):
        entry = self._data.get(key)
        if entry is None:
            self.misses += 1
            return default
        expires, value = entry
        if expires <= self._clock():
            del self._data[key]
            self.misses += 1
            return default
        self._data.move_to_end(key)
        self.hits += 1
        return value

    def set(self, key, value, ttl: float | None = None) -> None:
        self.purge()
        life = self.ttl if ttl is None else ttl
        if life <= 0:
            raise ValueError("ttl must be positive")
        self._data[key] = (self._clock() + life, value)
        self._data.move_to_end(key)
        while len(self._data) > self.maxsize:
            self._data.popitem(last=False)

    def delete(self, key) -> bool:
        return self._data.pop(key, _MISS) is not _MISS

    def clear(self) -> None:
        self._data.clear()
        self.hits = 0
        self.misses = 0

    def get_or_set(self, key, factory: Callable[[], Any], ttl: float | None = None):
        """Return the cached value, computing and storing it on a miss."""
        found = self.get(key, _MISS)
        if found is not _MISS:
            return found
        value = factory()
        self.set(key, value, ttl)
        return value
