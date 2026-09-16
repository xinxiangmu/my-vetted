# retry

Retry with exponential backoff, injectable sleep

`import retry` - effects: time

Verified: mutation kill rate 100% (8/8 mutants caught).

## API

- `RetryExhausted(attempts: int, last: BaseException)` - Raised when every attempt failed. Carries the last exception.
- `backoff_delays(attempts: int, base: float, factor: float, cap: float)` - Delays between attempts. One fewer than `attempts` - the first is immediate.
- `retry(fn: Callable[[], T], attempts: int, base: float, factor: float, cap: float, retry_on: Iterable[type[BaseException]], sleep: Callable[[float], None])` - Call fn until it returns. Re-raises immediately for non-retryable errors.

## Usage

Lifted from the tests, so it cannot go stale.

```python
# delays are one fewer than attempts
assert len(backoff_delays(3)) == 2

# delays grow by factor
assert backoff_delays(4, base=1.0, factor=2.0) == [1.0, 2.0, 4.0]
```
