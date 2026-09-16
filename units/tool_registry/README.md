# tool_registry

Expose Python callables as LLM tools and dispatch calls back

`import tool_registry` - effects: pure

Verified: mutation kill rate 100% (12/12 mutants caught).

## API

- `ToolError()` - The model asked for an unknown tool, or called a known one wrongly.
- `build_schema(fn: Callable)` - An OpenAI/Anthropic-style tool declaration read off the signature.
- `ToolRegistry()`
- `ToolRegistry.register(fn: Callable, name: str | None)` - Register a callable. Usable as a decorator.
- `ToolRegistry.unregister(name: str)`
- `ToolRegistry.schemas()`
- `ToolRegistry.call(name: str, arguments: dict | None)` - Dispatch one tool call, validating names and required arguments first.

## Usage

Lifted from the tests, so it cannot go stale.

```python
# schema uses function name
assert build_schema(add)['name'] == 'add'

# schema uses first docstring line
assert build_schema(add)['description'] == 'Add two numbers.'
```
