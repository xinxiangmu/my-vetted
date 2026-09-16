# safe_path

Confine user-supplied paths to a base directory

`import safe_path` - effects: fs

Verified: mutation kill rate 67% (8/12 mutants caught).

## API

- `UnsafePath()` - The requested path escapes the base directory or is otherwise unusable.
- `safe_name(name: str, fallback: str)` - Reduce a string to a single usable filename component.
- `safe_join(base: str | Path)` - Join under `base` and verify the result stays inside it.
- `is_inside(base: str | Path, target: str | Path)` - Whether `target` resolves to something inside `base`.

## Usage

Lifted from the tests, so it cannot go stale.

```python
# joins simple relative path
result = safe_join(tmp_path, 'docs', 'readme.md')
assert result == (tmp_path / 'docs' / 'readme.md').resolve()

# rejects parent traversal
with pytest.raises(UnsafePath):
    safe_join(tmp_path, '..', 'secrets.txt')
```
