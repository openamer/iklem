"""The narrow core: runtime, agent loop, and cache-safe context.

The core is deliberately small. It discovers plugins, runs the agent loop,
and assembles context without mutating past context (prompt-cache safety).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from iklem.memory.store import MemoryStore
from iklem.plugins.discovery import discover_plugins
from iklem.plugins.manifest import PluginRegistry


@dataclass
class Turn:
    """One agent turn: a user message and the tool results it produced."""

    user: str
    results: list[str] = field(default_factory=list)


class Runtime:
    """The narrow waist — wires memory, plugins, and the loop together."""

    def __init__(self, memory: MemoryStore | None = None) -> None:
        self.memory = memory or MemoryStore()
        self.plugins: PluginRegistry = discover_plugins()

    def run_turn(self, user: str) -> Turn:
        """Run a single turn. Returns the turn with any tool results.

        This is the minimal loop: it does not fabricate a model response. It
        records the turn and returns it honestly. A real model backend is a
        provider plugin, added later — the core stays model-agnostic.
        """
        turn = Turn(user=user)
        return turn
