"""Split long text into overlapping chunks that fit a size budget.

Prefers to break on paragraph, then sentence, then whitespace, so chunks stay
readable instead of cutting words in half.
"""
from __future__ import annotations

import re

# CJK sentences carry no trailing space, so the break is the punctuation itself.
SENTENCE_END = re.compile(r"(?<=[.!?])\s+|(?<=[。！？])")


def _split_points(text: str) -> list[str]:
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    pieces: list[str] = []
    for para in paras:
        pieces.extend(s for s in SENTENCE_END.split(para) if s.strip())
    return pieces


def _hard_split(piece: str, size: int) -> list[str]:
    """A single piece longer than the budget: break on whitespace, else mid-word."""
    out: list[str] = []
    while len(piece) > size:
        cut = piece.rfind(" ", 0, size)
        if cut <= 0:
            cut = size
        out.append(piece[:cut].strip())
        piece = piece[cut:].lstrip()
    if piece:
        out.append(piece)
    return out


def chunk(text: str, size: int = 1000, overlap: int = 100) -> list[str]:
    """Chunks of at most `size` characters, each repeating `overlap` from the last."""
    if size < 1:
        raise ValueError("size must be at least 1")
    if overlap < 0:
        raise ValueError("overlap must not be negative")
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")

    text = text.strip()
    if not text:
        return []

    pieces: list[str] = []
    for piece in _split_points(text):
        pieces.extend(_hard_split(piece, size) if len(piece) > size else [piece])

    chunks: list[str] = []
    current = ""
    for piece in pieces:
        candidate = f"{current} {piece}".strip() if current else piece
        if len(candidate) <= size:
            current = candidate
            continue
        if current:
            chunks.append(current)
            tail = current[-overlap:] if overlap else ""
            carried = f"{tail} {piece}".strip() if tail else piece
            # A full-size piece leaves no room for the overlap; keep the size bound.
            current = carried if len(carried) <= size else piece
        else:
            current = piece
    if current:
        chunks.append(current)
    return chunks


def total_chars(chunks: list[str]) -> int:
    return sum(len(c) for c in chunks)
