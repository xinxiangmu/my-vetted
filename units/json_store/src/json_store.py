"""Atomic JSON file storage.

Writes to a temp file in the same directory and replaces, so a crash mid-write
leaves the previous version intact rather than a truncated file.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


class StoreError(Exception):
    """The file exists but does not hold usable JSON."""


def read(path: str | Path, default: Any = None) -> Any:
    """Read JSON. Returns `default` if the file does not exist."""
    p = Path(path)
    if not p.exists():
        return default
    text = p.read_text(encoding="utf-8")
    if not text.strip():
        return default
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise StoreError(f"{p} is not valid JSON: {exc}")


def write(path: str | Path, data: Any, indent: int = 2) -> Path:
    """Write JSON atomically. Creates parent directories as needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=indent, ensure_ascii=False)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, p)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    return p


def update(path: str | Path, changes: dict, indent: int = 2) -> dict:
    """Merge `changes` into the stored object and write it back."""
    current = read(path, default={})
    if not isinstance(current, dict):
        raise StoreError(f"{path} holds {type(current).__name__}, not an object")
    current.update(changes)
    write(path, current, indent=indent)
    return current


def append(path: str | Path, item: Any, indent: int = 2) -> list:
    """Append to the stored list and write it back."""
    current = read(path, default=[])
    if not isinstance(current, list):
        raise StoreError(f"{path} holds {type(current).__name__}, not a list")
    current.append(item)
    write(path, current, indent=indent)
    return current
