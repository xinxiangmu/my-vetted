# ttl_cache

LRU cache with per-entry TTL, injectable clock

`import ttl_cache` - effects: time

Verified: mutation kill rate 83% (10/12 mutants caught).

## API

- `TTLCache(maxsize: int, ttl: float, clock: Callable[[], float])` - Least-recently-used eviction at `maxsize`, plus time-based expiry.
- `TTLCache.purge()` - Drop expired entries. Returns how many were removed.
- `TTLCache.get(key, default)`
- `TTLCache.set(key, value, ttl: float | None)`
- `TTLCache.delete(key)`
- `TTLCache.clear()`
- `TTLCache.get_or_set(key, factory: Callable[[], Any], ttl: float | None)` - Return the cached value, computing and storing it on a miss.

## Usage

Lifted from the tests, so it cannot go stale.

```python
# set then get
c, _ = make()
c.set('a', 1)
assert c.get('a') == 1

# missing key returns default
c, _ = make()
assert c.get('nope', 'fallback') == 'fallback'
```
