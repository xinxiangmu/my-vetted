# env_config

Typed environment variable reading with required checks

`import env_config` - effects: env

Verified: mutation kill rate 83% (10/12 mutants caught).

## API

- `ConfigError()` - A required setting is absent, or a present setting has the wrong shape.
- `get_str(name: str, default, env: Mapping[str, str] | None)`
- `get_int(name: str, default, env: Mapping[str, str] | None)`
- `get_float(name: str, default, env: Mapping[str, str] | None)`
- `get_bool(name: str, default, env: Mapping[str, str] | None)`
- `get_list(name: str, default, separator: str, env: Mapping[str, str] | None)`
- `require_all(names: list[str], env: Mapping[str, str] | None)` - Check every required setting at startup, and report all of them at once.

## Usage

Lifted from the tests, so it cannot go stale.

```python
# get str returns value
assert get_str('NAME', env=ENV) == 'vetted'

# get str uses default when absent
assert get_str('NOPE', default='fallback', env=ENV) == 'fallback'
```
