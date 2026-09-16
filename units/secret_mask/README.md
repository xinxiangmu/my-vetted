# secret_mask

Redact credentials in logs, dicts and prompts

`import secret_mask` - effects: pure

Verified: mutation kill rate 100% (12/12 mutants caught).

## API

- `is_secret_key(key: str)`
- `mask_value(value: str, keep: int)` - Replace a value with MASK, optionally keeping the last `keep` characters.
- `mask_text(text: str)` - Redact credential-shaped substrings in free text.
- `mask_data(data: Any, keep: int)` - Walk dicts and lists, masking values whose key name looks like a secret.

## Usage

Lifted from the tests, so it cannot go stale.

```python
# recognises secret key names
assert is_secret_key('PASSWORD')
assert is_secret_key('db_password')
assert is_secret_key('Authorization')

# ordinary key names are not secrets
assert not is_secret_key('username')
assert not is_secret_key('host')
```
