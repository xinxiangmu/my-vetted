"""Typed environment variable reading.

Fails loudly at startup for a missing required setting, instead of failing at 3am
with a TypeError on None.
"""
from __future__ import annotations

import os
from typing import Mapping

_MISSING = object()
TRUE_WORDS = {"1", "true", "yes", "on"}
FALSE_WORDS = {"0", "false", "no", "off"}


class ConfigError(Exception):
    """A required setting is absent, or a present setting has the wrong shape."""


def get_str(name: str, default=_MISSING, env: Mapping[str, str] | None = None) -> str:
    source = os.environ if env is None else env
    raw = source.get(name)
    if raw is None or raw == "":
        if default is _MISSING:
            raise ConfigError(f"{name} is required but not set")
        return default
    return raw


def get_int(name: str, default=_MISSING, env: Mapping[str, str] | None = None) -> int:
    raw = get_str(name, default=_MISSING if default is _MISSING else None, env=env)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        raise ConfigError(f"{name} must be an integer, got {raw!r}")


def get_float(name: str, default=_MISSING, env: Mapping[str, str] | None = None) -> float:
    raw = get_str(name, default=_MISSING if default is _MISSING else None, env=env)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        raise ConfigError(f"{name} must be a number, got {raw!r}")


def get_bool(name: str, default=_MISSING, env: Mapping[str, str] | None = None) -> bool:
    raw = get_str(name, default=_MISSING if default is _MISSING else None, env=env)
    if raw is None:
        return default
    low = raw.strip().lower()
    if low in TRUE_WORDS:
        return True
    if low in FALSE_WORDS:
        return False
    raise ConfigError(f"{name} must be a boolean, got {raw!r}")


def get_list(
    name: str,
    default=_MISSING,
    separator: str = ",",
    env: Mapping[str, str] | None = None,
) -> list[str]:
    raw = get_str(name, default=_MISSING if default is _MISSING else None, env=env)
    if raw is None:
        return default
    return [part.strip() for part in raw.split(separator) if part.strip()]


def require_all(names: list[str], env: Mapping[str, str] | None = None) -> None:
    """Check every required setting at startup, and report all of them at once."""
    source = os.environ if env is None else env
    missing = [n for n in names if not source.get(n)]
    if missing:
        raise ConfigError(f"missing required settings: {', '.join(missing)}")
