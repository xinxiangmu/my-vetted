# conversation_memory

Chat memory with token budget, pinned turns, oldest-first trim

`import conversation_memory` - effects: pure

Verified: mutation kill rate 92% (11/12 mutants caught).

## API

- `estimate_tokens(text: str)` - Rough count: ~4 characters per token, floor of 1 for non-empty text.
- `Message(role: str, content: str, pinned: bool)` - A chat message. A dict so it serialises straight into an API payload.
- `ConversationMemory(budget: int, counter: Callable[[str], int], keep_recent: int)`
- `ConversationMemory.add(role: str, content: str, pinned: bool)`
- `ConversationMemory.extend(messages: Iterable[dict])`
- `ConversationMemory.tokens()`
- `ConversationMemory.trim()` - Drop oldest unprotected messages until within budget. Returns count dropped.
- `ConversationMemory.render()` - Messages ready to send, trimmed to budget.
- `ConversationMemory.clear(keep_system: bool)`

## Usage

Lifted from the tests, so it cannot go stale.

```python
# estimate is zero for empty
assert estimate_tokens('') == 0

# estimate is at least one for short text
assert estimate_tokens('ab') == 1
```
