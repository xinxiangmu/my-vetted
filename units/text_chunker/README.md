# text_chunker

Split long text into overlapping chunks on sentence boundaries

`import text_chunker` - effects: pure

Verified: mutation kill rate 75% (9/12 mutants caught).

## API

- `chunk(text: str, size: int, overlap: int)` - Chunks of at most `size` characters, each repeating `overlap` from the last.
- `total_chars(chunks: list[str])`

## Usage

Lifted from the tests, so it cannot go stale.

```python
# empty text yields nothing
assert chunk('') == []
assert chunk('   \n  ') == []

# short text is one chunk
assert chunk('hello world', size=100, overlap=10) == ['hello world']
```
