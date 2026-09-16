# json_store

Atomic JSON file read/write/update/append

`import json_store` - effects: env, fs

Verified: mutation kill rate 80% (8/10 mutants caught).

## API

- `StoreError()` - The file exists but does not hold usable JSON.
- `read(path: str | Path, default: Any)` - Read JSON. Returns `default` if the file does not exist.
- `write(path: str | Path, data: Any, indent: int)` - Write JSON atomically. Creates parent directories as needed.
- `update(path: str | Path, changes: dict, indent: int)` - Merge `changes` into the stored object and write it back.
- `append(path: str | Path, item: Any, indent: int)` - Append to the stored list and write it back.

## Usage

Lifted from the tests, so it cannot go stale.

```python
# read missing returns default
assert read(tmp_path / 'nope.json', default={'a': 1}) == {'a': 1}

# write then read roundtrip
p = tmp_path / 'data.json'
write(p, {'name': 'vetted', 'n': 3})
assert read(p) == {'name': 'vetted', 'n': 3}
```
