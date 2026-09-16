# jsonl_log

Append-only JSONL event log, survives a crashed run

`import jsonl_log` - effects: fs

Verified: mutation kill rate 83% (10/12 mutants caught).

## API

- `JSONLLog(path: str | Path, clock: Callable[[], float] | None, redact: Callable[[Any], Any] | None)`
- `JSONLLog.append(event: str)` - Write one record. Returns the record as written.
- `JSONLLog.read(skip_broken: bool)` - Every readable record. A truncated final line is skipped by default.
- `JSONLLog.iter_records(skip_broken: bool)`
- `JSONLLog.count(event: str | None)`
- `JSONLLog.filter()`
- `JSONLLog.tail(n: int)`
- `JSONLLog.clear()`

## Usage

Lifted from the tests, so it cannot go stale.

```python
# append then read
log = JSONLLog(tmp_path / 'run.jsonl')
log.append('start', step=1)
assert log.read() == [{'event': 'start', 'step': 1}]

# append returns the record
log = JSONLLog(tmp_path / 'run.jsonl')
assert log.append('start', step=1) == {'event': 'start', 'step': 1}
```
