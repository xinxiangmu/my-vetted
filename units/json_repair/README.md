# json_repair

Recover JSON from LLM output: fences, prose, trailing commas, truncation

`import json_repair` - effects: pure

Verified: mutation kill rate 92% (11/12 mutants caught).

## API

- `UnrepairableJSON()` - No JSON-shaped payload could be recovered from the text.
- `strip_fences(text: str)` - Return the contents of the first code fence, or the text unchanged.
- `find_payload(text: str)` - The outermost {...} or [...] span, ignoring surrounding prose.
- `close_unbalanced(payload: str)` - Append the brackets a truncated response never got to write.
- `repair(text: str)` - Best-effort repair of a JSON string. Does not parse it.
- `loads(text: str, default: Any)` - Parse JSON from messy text. Returns `default` only if `default` was given.

## Usage

Lifted from the tests, so it cannot go stale.

```python
# clean json parses
assert loads('{"a": 1}') == {'a': 1}

# strips json fence
assert loads('```json\n{"a": 1}\n```') == {'a': 1}
```
