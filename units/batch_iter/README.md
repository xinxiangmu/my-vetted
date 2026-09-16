# batch_iter

Lazy batching, sliding windows, dedupe and grouping over iterables

`import batch_iter` - effects: pure

Verified: mutation kill rate 83% (10/12 mutants caught).

## API

- `batched(items: Iterable[T], size: int)` - Consecutive lists of at most `size`. The final batch may be shorter.
- `windowed(items: Iterable[T], size: int, step: int)` - Sliding windows of exactly `size`. Yields nothing if the input is shorter.
- `dedupe(items: Iterable[T], key: Callable[[T], Any] | None)` - First occurrence wins, original order preserved.
- `chunk_by(items: Iterable[T], key: Callable[[T], Any])` - Group consecutive items sharing a key. Does not sort first.
- `take(items: Iterable[T], n: int)` - First n items, without consuming more of the source than needed.

## Usage

Lifted from the tests, so it cannot go stale.

```python
# batched splits evenly
assert list(batched(range(6), 2)) == [[0, 1], [2, 3], [4, 5]]

# batched final batch is short
assert list(batched(range(5), 2)) == [[0, 1], [2, 3], [4]]
```
