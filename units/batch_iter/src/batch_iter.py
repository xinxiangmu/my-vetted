"""Batching, windowing and de-duplication over iterables.

Streams throughout: nothing here loads the whole input into memory, so these work
on a file, a cursor, or a generator of API pages.
"""
from __future__ import annotations

from itertools import islice
from typing import Any, Callable, Iterable, Iterator, TypeVar

T = TypeVar("T")


def batched(items: Iterable[T], size: int) -> Iterator[list[T]]:
    """Consecutive lists of at most `size`. The final batch may be shorter."""
    if size < 1:
        raise ValueError("size must be at least 1")
    batch: list[T] = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def windowed(items: Iterable[T], size: int, step: int = 1) -> Iterator[list[T]]:
    """Sliding windows of exactly `size`. Yields nothing if the input is shorter."""
    if size < 1:
        raise ValueError("size must be at least 1")
    if step < 1:
        raise ValueError("step must be at least 1")
    window: list[T] = []
    since = 0
    for item in items:
        window.append(item)
        if len(window) > size:
            window.pop(0)
        if len(window) == size:
            if since == 0:
                yield list(window)
                since = step
            since -= 1
    return


def dedupe(items: Iterable[T], key: Callable[[T], Any] | None = None) -> Iterator[T]:
    """First occurrence wins, original order preserved."""
    seen: set = set()
    for item in items:
        k = item if key is None else key(item)
        if k in seen:
            continue
        seen.add(k)
        yield item


def chunk_by(items: Iterable[T], key: Callable[[T], Any]) -> Iterator[list[T]]:
    """Group consecutive items sharing a key. Does not sort first."""
    group: list[T] = []
    current: Any = object()
    for item in items:
        k = key(item)
        if group and k != current:
            yield group
            group = []
        current = k
        group.append(item)
    if group:
        yield group


def take(items: Iterable[T], n: int) -> list[T]:
    """First n items, without consuming more of the source than needed."""
    if n < 0:
        raise ValueError("n must not be negative")
    # islice stops after exactly n; a manual loop pulls one item too many and
    # silently drops it, which breaks the caller's remaining iterator.
    return list(islice(items, n))
