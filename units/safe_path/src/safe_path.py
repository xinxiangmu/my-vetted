"""Confine a user-supplied path to a base directory.

Path traversal is the failure this prevents: a request for `../../etc/passwd`, or a
Windows absolute path, or a symlink pointing outside the base. Validate before any
read or write that takes a name from outside the program.
"""
from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

UNSAFE_NAME = re.compile(r'[\x00-\x1f<>:"|?*]')
RESERVED_WINDOWS = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


class UnsafePath(Exception):
    """The requested path escapes the base directory or is otherwise unusable."""


def safe_name(name: str, fallback: str = "file") -> str:
    """Reduce a string to a single usable filename component."""
    cleaned = UNSAFE_NAME.sub("_", name).strip().strip(".")
    cleaned = cleaned.replace("/", "_").replace("\\", "_")
    if not cleaned:
        return fallback
    stem = cleaned.split(".")[0].upper()
    if stem in RESERVED_WINDOWS:
        cleaned = f"_{cleaned}"
    return cleaned[:255]


def safe_join(base: str | Path, *parts: str) -> Path:
    """Join under `base` and verify the result stays inside it.

    Raises UnsafePath for traversal, absolute components, and symlinked escapes.
    """
    root = Path(base).resolve()
    for part in parts:
        if not part:
            raise UnsafePath("empty path component")
        if PurePosixPath(part).is_absolute() or re.match(r"^[A-Za-z]:", part):
            raise UnsafePath(f"absolute component not allowed: {part!r}")
        if "\x00" in part:
            raise UnsafePath("null byte in path")

    candidate = root.joinpath(*parts).resolve()
    if candidate != root and root not in candidate.parents:
        raise UnsafePath(f"path escapes base directory: {candidate}")
    return candidate


def is_inside(base: str | Path, target: str | Path) -> bool:
    """Whether `target` resolves to something inside `base`."""
    root = Path(base).resolve()
    candidate = Path(target).resolve()
    return candidate == root or root in candidate.parents
