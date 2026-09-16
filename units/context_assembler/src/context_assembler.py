"""Assemble a prompt context from prioritised sections under a size budget.

When everything does not fit, low-priority sections are dropped whole and the
result says which ones - silent truncation reads as "I saw everything" when the
model did not.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, len(text) // 4)


@dataclass
class Section:
    name: str
    content: str
    priority: int = 50          # lower number is kept first
    required: bool = False      # never dropped; may overflow the budget
    truncatable: bool = False   # may be cut mid-way instead of dropped whole


@dataclass
class Assembled:
    text: str
    used: list[str] = field(default_factory=list)
    dropped: list[str] = field(default_factory=list)
    truncated: list[str] = field(default_factory=list)
    tokens: int = 0

    @property
    def complete(self) -> bool:
        return not self.dropped and not self.truncated


def _cut(content: str, allowance: int, counter: Callable[[str], int]) -> str:
    """Longest prefix of whole lines fitting the allowance."""
    if counter(content) <= allowance:
        return content
    kept: list[str] = []
    for line in content.splitlines():
        candidate = "\n".join(kept + [line])
        if counter(candidate) > allowance:
            break
        kept.append(line)
    return "\n".join(kept)


def assemble(
    sections: list[Section],
    budget: int = 8000,
    counter: Callable[[str], int] = estimate_tokens,
    separator: str = "\n\n",
) -> Assembled:
    if budget < 1:
        raise ValueError("budget must be at least 1")

    ordered = sorted(
        sections, key=lambda s: (not s.required, s.priority, s.name)
    )
    result = Assembled(text="")
    parts: list[str] = []
    spent = 0

    for section in ordered:
        cost = counter(section.content)
        if section.required:
            parts.append(section.content)
            result.used.append(section.name)
            spent += cost
            continue
        room = budget - spent
        if cost <= room:
            parts.append(section.content)
            result.used.append(section.name)
            spent += cost
        elif section.truncatable and room > 0:
            cut = _cut(section.content, room, counter)
            if cut:
                parts.append(cut)
                result.used.append(section.name)
                result.truncated.append(section.name)
                spent += counter(cut)
            else:
                result.dropped.append(section.name)
        else:
            result.dropped.append(section.name)

    result.text = separator.join(p for p in parts if p)
    result.tokens = counter(result.text)
    return result


def report(result: Assembled) -> str:
    """One line stating what the model actually received."""
    if result.complete:
        return f"context complete: {len(result.used)} sections, {result.tokens} tokens"
    bits = [f"context incomplete: {result.tokens} tokens"]
    if result.truncated:
        bits.append(f"truncated {', '.join(result.truncated)}")
    if result.dropped:
        bits.append(f"dropped {', '.join(result.dropped)}")
    return "; ".join(bits)
