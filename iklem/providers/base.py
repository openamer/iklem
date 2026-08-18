"""Provider abstraction — the model backend is a plugin.

A provider turns a conversation into a model response. The core stays
model-agnostic: it talks to this interface, never to a specific vendor.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Message:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class ProviderResult:
    """A model response, honestly reported."""

    content: str
    ok: bool = True
    error: str | None = None


class Provider(ABC):
    """A model backend. Implementations are provider plugins."""

    name: str = "base"

    @abstractmethod
    def complete(self, messages: list[Message]) -> ProviderResult:
        """Return a model response for the given messages."""
        raise NotImplementedError
