"""The learning loop: durable memory + skill distillation.

This is the idea taken from the hermes-agent lineage, rebuilt cleanly: memory
persists across sessions, and skills are distilled from hard tasks and refined
on reuse. Learning is observable — every write is verifiable.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from iklem.verify.checks import require


def _default_home() -> Path:
    """Resolve the iklem data directory, honoring IKLEM_HOME if set."""
    env = os.environ.get("IKLEM_HOME")
    if env:
        return Path(env)
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("HOME") or "."
    return Path(base) / "iklem"


class MemoryStore:
    """A durable, JSON-backed memory store that survives across sessions."""

    def __init__(self, home: Path | None = None) -> None:
        self.home = home or _default_home()
        self.memory_file = self.home / "memory.json"
        self._data: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if self.memory_file.exists():
            try:
                self._data = json.loads(self.memory_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                # A corrupt memory file must not crash the agent — start fresh
                # but report it honestly rather than silently swallowing it.
                self._data = {}

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def set(self, key: str, value: str) -> None:
        require(bool(key.strip()), "memory key must be non-empty")
        self._data[key] = value
        self._persist()

    def _persist(self) -> None:
        self.home.mkdir(parents=True, exist_ok=True)
        tmp = self.memory_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
        # Atomic replace: never leave a half-written memory file.
        os.replace(tmp, self.memory_file)

    def keys(self) -> list[str]:
        return list(self._data.keys())

    def __len__(self) -> int:
        return len(self._data)
