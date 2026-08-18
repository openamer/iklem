"""Provider abstraction — the model backend is a plugin.

A provider turns a conversation into a model response, and can also emit
tool calls when given tool definitions. The core stays model-agnostic: it
talks to this interface, never to a specific vendor.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Message:
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    # For tool-call messages: the tool name and its arguments (JSON string).
    tool_name: str | None = None
    tool_call_id: str | None = None


@dataclass
class ToolCall:
    """A tool invocation the model requested."""

    name: str
    arguments: dict


@dataclass
class ProviderResult:
    """A model response, honestly reported.

    Either `content` is set (a plain answer) or `tool_calls` is non-empty
    (the model wants to call tools before answering).
    """

    content: str = ""
    ok: bool = True
    error: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)


class Provider(ABC):
    """A model backend. Implementations are provider plugins."""

    name: str = "base"

    @abstractmethod
    def complete(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> ProviderResult:
        """Return a model response (or tool calls) for the given messages."""
        raise NotImplementedError
