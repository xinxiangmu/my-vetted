"""Recover JSON from LLM output.

Models wrap JSON in prose or fences, trail commas, and get cut off mid-string when
they hit a token limit. `json.loads` fails on all three. This finds the payload and
repairs the common damage, so a truncated response degrades instead of exploding.
"""
from __future__ import annotations

import json
import re
from typing import Any

FENCE = re.compile(r"```(?:json|JSON)?\s*(.*?)```", re.DOTALL)
TRAILING_COMMA = re.compile(r",\s*([}\]])")


class UnrepairableJSON(Exception):
    """No JSON-shaped payload could be recovered from the text."""


def strip_fences(text: str) -> str:
    """Return the contents of the first code fence, or the text unchanged."""
    match = FENCE.search(text)
    return match.group(1).strip() if match else text.strip()


def find_payload(text: str) -> str:
    """The outermost {...} or [...] span, ignoring surrounding prose."""
    text = strip_fences(text)
    starts = [i for i in (text.find("{"), text.find("[")) if i >= 0]
    if not starts:
        raise UnrepairableJSON("no '{' or '[' in text")
    start = min(starts)
    opener = text[start]
    closer = "}" if opener == "{" else "]"
    end = text.rfind(closer)
    if end <= start:
        return text[start:]
    return text[start : end + 1]


def close_unbalanced(payload: str) -> str:
    """Append the brackets a truncated response never got to write."""
    stack: list[str] = []
    in_string = False
    escaped = False
    for ch in payload:
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch in "{[":
            stack.append(ch)
        elif ch in "}]" and stack:
            stack.pop()
    if in_string:
        payload += '"'
    return payload + "".join("}" if c == "{" else "]" for c in reversed(stack))


def repair(text: str) -> str:
    """Best-effort repair of a JSON string. Does not parse it."""
    payload = find_payload(text)
    payload = TRAILING_COMMA.sub(r"\1", payload)
    return close_unbalanced(payload)


def loads(text: str, default: Any = None) -> Any:
    """Parse JSON from messy text. Returns `default` only if `default` was given."""
    try:
        return json.loads(strip_fences(text))
    except json.JSONDecodeError:
        pass
    try:
        return json.loads(repair(text))
    except (json.JSONDecodeError, UnrepairableJSON) as exc:
        if default is not None:
            return default
        raise UnrepairableJSON(f"could not recover JSON: {exc}")
