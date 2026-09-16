"""Redact credentials before anything reaches a log, a report, or an LLM prompt.

Two layers: key-name matching for structured data, pattern matching for free text.
Neither is complete - this reduces accidental leaks, it is not a control that lets
you log secrets safely on purpose.
"""
from __future__ import annotations

import re
from typing import Any

MASK = "***"

SECRET_KEY_WORDS = (
    "password", "passwd", "secret", "token", "api_key", "apikey", "access_key",
    "private_key", "authorization", "auth", "credential", "session", "cookie",
)

PATTERNS = (
    re.compile(r"\b(sk-|ghp_|gho_|github_pat_)[A-Za-z0-9_\-]{8,}"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{8,}", re.IGNORECASE),
    re.compile(r"\b[A-Za-z0-9._%+\-]+:[^\s/@]{4,}@[A-Za-z0-9.\-]+"),  # user:pass@host
    re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]+"),  # JWT
)


def is_secret_key(key: str) -> bool:
    low = key.lower()
    return any(word in low for word in SECRET_KEY_WORDS)


def mask_value(value: str, keep: int = 0) -> str:
    """Replace a value with MASK, optionally keeping the last `keep` characters."""
    if keep < 0:
        raise ValueError("keep must not be negative")
    if keep == 0 or len(value) <= keep:
        return MASK
    return MASK + value[-keep:]


def mask_text(text: str) -> str:
    """Redact credential-shaped substrings in free text."""
    for pattern in PATTERNS:
        text = pattern.sub(MASK, text)
    return text


def mask_data(data: Any, keep: int = 0) -> Any:
    """Walk dicts and lists, masking values whose key name looks like a secret."""
    if isinstance(data, dict):
        out = {}
        for k, v in data.items():
            if is_secret_key(str(k)) and isinstance(v, (str, int, float)):
                out[k] = mask_value(str(v), keep)
            else:
                out[k] = mask_data(v, keep)
        return out
    if isinstance(data, list):
        return [mask_data(v, keep) for v in data]
    if isinstance(data, str):
        return mask_text(data)
    return data
