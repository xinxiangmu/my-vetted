# context_assembler

Assemble prompt context from prioritised sections under a budget

`import context_assembler` - effects: pure

Verified: mutation kill rate 75% (9/12 mutants caught).

## API

- `estimate_tokens(text: str)`
- `Section()`
- `Assembled.complete()`
- `assemble(sections: list[Section], budget: int, counter: Callable[[str], int], separator: str)`
- `report(result: Assembled)` - One line stating what the model actually received.

## Usage

Lifted from the tests, so it cannot go stale.

```python
# everything fits
r = assemble([sec('a', 10), sec('b', 10)], budget=100, counter=len)
assert r.used == ['a', 'b']
assert r.complete

# priority decides order
r = assemble([sec('low', 5, priority=90), sec('high', 5, priority=10)], budget=100, counter=len)
assert r.used == ['high', 'low']
```
