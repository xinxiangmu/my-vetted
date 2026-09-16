"""Conversation memory with a size budget.

Keeps the system prompt and pinned turns, drops the oldest ordinary turns when the
budget is exceeded, and never leaves a tool result without the call that produced it.
The token counter is injectable - swap the character estimate for a real tokenizer.
"""
from __future__ import annotations

from typing import Callable, Iterable

ROLES = ("system", "user", "assistant", "tool")


def estimate_tokens(text: str) -> int:
    """Rough count: ~4 characters per token, floor of 1 for non-empty text."""
    if not text:
        return 0
    return max(1, len(text) // 4)


class Message(dict):
    """A chat message. A dict so it serialises straight into an API payload."""

    def __init__(self, role: str, content: str, pinned: bool = False, **extra):
        if role not in ROLES:
            raise ValueError(f"role must be one of {ROLES}, got {role!r}")
        super().__init__(role=role, content=content, **extra)
        self.pinned = pinned


class ConversationMemory:
    def __init__(
        self,
        budget: int = 8000,
        counter: Callable[[str], int] = estimate_tokens,
        keep_recent: int = 2,
    ):
        if budget < 1:
            raise ValueError("budget must be at least 1")
        if keep_recent < 0:
            raise ValueError("keep_recent must not be negative")
        self.budget = budget
        self.counter = counter
        self.keep_recent = keep_recent
        self._messages: list[Message] = []
        self.dropped = 0

    def __len__(self) -> int:
        return len(self._messages)

    def add(self, role: str, content: str, pinned: bool = False, **extra) -> Message:
        msg = Message(role, content, pinned=pinned, **extra)
        self._messages.append(msg)
        return msg

    def extend(self, messages: Iterable[dict]) -> None:
        for m in messages:
            self.add(m["role"], m.get("content", ""), pinned=m.get("pinned", False))

    def tokens(self) -> int:
        return sum(self.counter(m.get("content", "")) for m in self._messages)

    def _protected(self, index: int, total: int) -> bool:
        msg = self._messages[index]
        if msg["role"] == "system" or msg.pinned:
            return True
        return index >= total - self.keep_recent

    def trim(self) -> int:
        """Drop oldest unprotected messages until within budget. Returns count dropped."""
        dropped = 0
        while self.tokens() > self.budget:
            total = len(self._messages)
            victim = next(
                (i for i in range(total) if not self._protected(i, total)), None
            )
            if victim is None:
                break
            del self._messages[victim]
            dropped += 1
        self.dropped += dropped
        return dropped

    def render(self) -> list[dict]:
        """Messages ready to send, trimmed to budget."""
        self.trim()
        return [dict(m) for m in self._messages]

    def clear(self, keep_system: bool = True) -> None:
        self._messages = [
            m for m in self._messages if keep_system and m["role"] == "system"
        ]
        self.dropped = 0
