# semver

Semantic version parsing, comparison and bumping

`import semver` - effects: pure

Verified: mutation kill rate 83% (10/12 mutants caught).

## API

- `InvalidVersion()` - The string is not a semantic version.
- `Version.is_prerelease()`
- `Version.bump(part: str)` - Next version. Bumping drops any pre-release and build metadata.
- `parse(text: str)`
- `sort_key(version: Version)` - Build metadata is excluded from ordering, per the specification.
- `compare(a: str, b: str)` - -1 if a < b, 0 if equal, 1 if a > b.
- `satisfies(version: str, minimum: str)` - Whether `version` is at least `minimum`.
- `latest(versions: list[str])`

## Usage

Lifted from the tests, so it cannot go stale.

```python
# parses basic version
v = parse('1.2.3')
assert (v.major, v.minor, v.patch) == (1, 2, 3)

# parses leading v
assert parse('v2.0.1').minor == 0
```
