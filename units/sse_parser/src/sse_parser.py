"""Incremental Server-Sent Events parser for streaming LLM responses.

Feed it whatever bytes arrived; it yields only complete events and keeps the
half-line remainder for the next chunk. Splitting on newlines without buffering is
the classic streaming bug - a token gets cut across two network reads and vanishes.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Event:
    data: str = ""
    event: str = "message"
    id: str | None = None
    retry: int | None = None


@dataclass
class SSEParser:
    buffer: str = ""
    _lines: list[str] = field(default_factory=list)

    def feed(self, chunk: str) -> list[Event]:
        """Append a chunk and return every event completed by it."""
        self.buffer += chunk
        events: list[Event] = []
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            line = line.rstrip("\r")
            if line == "":
                event = self._flush()
                if event is not None:
                    events.append(event)
            else:
                self._lines.append(line)
        return events

    def close(self) -> list[Event]:
        """Finish the stream, emitting any event not terminated by a blank line."""
        if self.buffer:
            self._lines.append(self.buffer.rstrip("\r"))
            self.buffer = ""
        event = self._flush()
        return [event] if event is not None else []

    def _flush(self) -> Event | None:
        if not self._lines:
            return None
        event = Event()
        data_parts: list[str] = []
        for line in self._lines:
            if line.startswith(":"):
                continue
            field_name, _, value = line.partition(":")
            value = value[1:] if value.startswith(" ") else value
            if field_name == "data":
                data_parts.append(value)
            elif field_name == "event":
                event.event = value
            elif field_name == "id":
                event.id = value
            elif field_name == "retry" and value.isdigit():
                event.retry = int(value)
        self._lines = []
        if not data_parts and event.event == "message" and event.id is None:
            return None
        event.data = "\n".join(data_parts)
        return event


def is_done(event: Event, sentinel: str = "[DONE]") -> bool:
    """Whether this event is the stream terminator many LLM APIs send."""
    return event.data.strip() == sentinel
