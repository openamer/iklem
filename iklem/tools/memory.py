"""Memory tools — let the agent remember and recall across sessions.

These tools wire the learning loop into the agent: the agent can persist a
fact (remember) and retrieve it later (recall), so it genuinely improves with
use instead of starting fresh every session.
"""

from __future__ import annotations

from iklem.memory.store import MemoryStore


def _store() -> MemoryStore:
    return MemoryStore()


def remember(key: str, value: str) -> str:
    """Persist a fact under a key so it survives across sessions."""
    store = _store()
    store.set(key, value)
    return f"remembered {key}"


def recall(key: str) -> str:
    """Retrieve a previously remembered fact by key."""
    store = _store()
    value = store.get(key)
    return value if value is not None else f"(no memory for {key})"


def list_memories() -> str:
    """List all remembered keys."""
    store = _store()
    keys = store.keys()
    return "\n".join(keys) if keys else "(no memories)"
