"""Persistent conversation history — the agent remembers past turns.

This is the second half of "provably improves with use": memory stores facts,
history stores the conversation itself. Both survive restarts, so a fresh
iklem session continues where the last one left off.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from iklem.providers.base import Message


def _history_file() -> Path:
    env = os.environ.get("IKLEM_HOME")
    base = env or os.environ.get("LOCALAPPDATA") or os.environ.get("HOME") or "."
    return Path(base) / "iklem" / "history.json"


def load_history(limit: int = 50) -> list[Message]:
    """Load the most recent conversation turns (up to `limit` messages)."""
    path = _history_file()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    messages = []
    for item in data:
        messages.append(
            Message(
                role=item.get("role", "user"),
                content=item.get("content", ""),
            )
        )
    return messages[-limit:]


def save_history(messages: list[Message], limit: int = 50) -> None:
    """Persist the conversation history (atomically, capped at `limit`)."""
    path = _history_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {"role": m.role, "content": m.content}
        for m in messages[-limit:]
        if m.role in ("user", "assistant")
    ]
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, path)
