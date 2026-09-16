"""Append-only JSONL event log for agent runs.

One JSON object per line, so a crashed run still leaves every event before the
crash readable, and a partially written last line can be skipped instead of
poisoning the whole file.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Iterator


class JSONLLog:
    def __init__(
        self,
        path: str | Path,
        clock: Callable[[], float] | None = None,
        redact: Callable[[Any], Any] | None = None,
    ):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._clock = clock
        self._redact = redact

    def append(self, event: str, **fields) -> dict:
        """Write one record. Returns the record as written."""
        if not event:
            raise ValueError("event name must not be empty")
        record: dict[str, Any] = {"event": event}
        if self._clock is not None:
            record["ts"] = self._clock()
        record.update(fields)
        if self._redact is not None:
            record = self._redact(record)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    def read(self, skip_broken: bool = True) -> list[dict]:
        """Every readable record. A truncated final line is skipped by default."""
        return list(self.iter_records(skip_broken=skip_broken))

    def iter_records(self, skip_broken: bool = True) -> Iterator[dict]:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    if skip_broken:
                        continue
                    raise

    def count(self, event: str | None = None) -> int:
        return sum(
            1 for r in self.iter_records() if event is None or r.get("event") == event
        )

    def filter(self, **match) -> list[dict]:
        return [
            r for r in self.iter_records()
            if all(r.get(k) == v for k, v in match.items())
        ]

    def tail(self, n: int = 10) -> list[dict]:
        if n < 1:
            raise ValueError("n must be at least 1")
        return self.read()[-n:]

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()
