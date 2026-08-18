"""Session search — find past conversations and memories by keyword.

This gives iklem the ability to recall what was said in past sessions, like
OpenAmer's session_search. It searches the persisted history and memory for
matching text and returns the relevant excerpts.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def _data_dir() -> Path:
    base = os.environ.get("IKLEM_HOME") or os.environ.get("LOCALAPPDATA") or os.environ.get("HOME") or "."
    return Path(base) / "iklem"


def _read_json(path: Path) -> list:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def search_sessions(query: str) -> str:
    """Search past conversation history and memories for a keyword.

    Returns matching excerpts with their role, so the agent can recall what
    was discussed before instead of saying it does not know.
    """
    q = query.lower().strip()
    if not q:
        return "✗ empty query"

    hits: list[str] = []

    # Search history.
    history = _read_json(_data_dir() / "history.json")
    for item in history:
        content = item.get("content", "")
        if q in content.lower():
            role = item.get("role", "?")
            excerpt = content[:300]
            hits.append(f"[{role}] {excerpt}")

    # Search memory.
    memory = _read_json(_data_dir() / "memory.json")
    if isinstance(memory, dict):
        for key, value in memory.items():
            if q in str(key).lower() or q in str(value).lower():
                hits.append(f"[memory:{key}] {str(value)[:300]}")

    if not hits:
        return f"(no past conversation or memory matches '{query}')"
    return "\n\n".join(hits[:20])
