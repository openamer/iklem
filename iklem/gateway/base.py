"""Channel abstraction — a channel is a plugin that carries a conversation.

The CLI is one channel. This module defines the interface so more channels
(Telegram, Discord, …) can be added as plugins without touching the core.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Channel(ABC):
    """A conversation surface. Implementations are channel plugins."""

    name: str = "base"

    @abstractmethod
    def start(self, agent: Any) -> None:
        """Start the channel, routing messages to the agent."""
        raise NotImplementedError
