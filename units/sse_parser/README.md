# sse_parser

Incremental SSE parser for streaming LLM responses

`import sse_parser` - effects: pure

Verified: mutation kill rate 100% (12/12 mutants caught).

## API

- `Event()`
- `SSEParser.feed(chunk: str)` - Append a chunk and return every event completed by it.
- `SSEParser.close()` - Finish the stream, emitting any event not terminated by a blank line.
- `is_done(event: Event, sentinel: str)` - Whether this event is the stream terminator many LLM APIs send.

## Usage

Lifted from the tests, so it cannot go stale.

```python
# single event
p = SSEParser()
events = p.feed('data: hello\n\n')
assert [e.data for e in events] == ['hello']

# two events in one chunk
p = SSEParser()
events = p.feed('data: a\n\ndata: b\n\n')
assert [e.data for e in events] == ['a', 'b']
```
