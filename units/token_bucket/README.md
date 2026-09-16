# token_bucket

Token bucket rate limiter with injectable clock

`import token_bucket` - effects: time

Verified: mutation kill rate 83% (10/12 mutants caught).

## API

- `TokenBucket(capacity: int, refill_per_sec: float, clock: Callable[[], float])` - Allows `capacity` bursts, refilling at `refill_per_sec` tokens per second.
- `TokenBucket.tokens()`
- `TokenBucket.take(n: int)` - Consume n tokens. Returns False and consumes nothing if short.
- `TokenBucket.wait_time(n: int)` - Seconds until n tokens are available. 0.0 if available now.

## Usage

Lifted from the tests, so it cannot go stale.

```python
# starts full
clock = FakeClock()
b = TokenBucket(capacity=5, refill_per_sec=1.0, clock=clock)
assert b.tokens == 5.0

# take consumes
clock = FakeClock()
b = TokenBucket(capacity=5, refill_per_sec=1.0, clock=clock)
assert b.take(2) is True
assert b.tokens == 3.0
```
