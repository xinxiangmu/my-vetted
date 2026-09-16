"""Expose Python callables to an LLM as tools, and dispatch its calls back.

Schemas are derived from the signature and type hints, so the declaration an agent
sees cannot drift from the function it actually calls.
"""
from __future__ import annotations

import inspect
from typing import Any, Callable

JSON_TYPES = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


class ToolError(Exception):
    """The model asked for an unknown tool, or called a known one wrongly."""


def build_schema(fn: Callable) -> dict:
    """An OpenAI/Anthropic-style tool declaration read off the signature."""
    sig = inspect.signature(fn)
    hints = getattr(fn, "__annotations__", {})
    properties: dict[str, dict] = {}
    required: list[str] = []
    for name, param in sig.parameters.items():
        if name in ("self", "cls") or param.kind in (
            param.VAR_POSITIONAL, param.VAR_KEYWORD
        ):
            continue
        prop = {"type": JSON_TYPES.get(hints.get(name), "string")}
        properties[name] = prop
        if param.default is inspect.Parameter.empty:
            required.append(name)
    doc = (inspect.getdoc(fn) or "").split("\n")[0]
    return {
        "name": fn.__name__,
        "description": doc,
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable] = {}

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def register(self, fn: Callable, name: str | None = None) -> Callable:
        """Register a callable. Usable as a decorator."""
        key = name or fn.__name__
        if key in self._tools:
            raise ToolError(f"tool {key!r} is already registered")
        self._tools[key] = fn
        return fn

    def unregister(self, name: str) -> bool:
        return self._tools.pop(name, None) is not None

    def schemas(self) -> list[dict]:
        return [build_schema(fn) for fn in self._tools.values()]

    def call(self, name: str, arguments: dict | None = None) -> Any:
        """Dispatch one tool call, validating names and required arguments first."""
        fn = self._tools.get(name)
        if fn is None:
            known = ", ".join(sorted(self._tools)) or "none"
            raise ToolError(f"unknown tool {name!r}; registered: {known}")
        arguments = arguments or {}
        sig = inspect.signature(fn)
        allowed = set(sig.parameters)
        unexpected = set(arguments) - allowed
        if unexpected:
            raise ToolError(f"{name}: unexpected arguments {sorted(unexpected)}")
        missing = [
            p for p, param in sig.parameters.items()
            if param.default is inspect.Parameter.empty and p not in arguments
        ]
        if missing:
            raise ToolError(f"{name}: missing required arguments {missing}")
        return fn(**arguments)
