"""Tool abstraction — a tool is a plugin the agent can call.

This proves the third plugin kind (channel, provider, tool). A tool is a
named, self-describing callable. The core discovers tools via the registry
and exposes them to the agent; it never hard-codes a specific tool.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    fn: Callable[..., Any]

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.fn(*args, **kwargs)


def echo(text: str) -> str:
    """Return the input unchanged — the simplest possible tool."""
    return text


def word_count(text: str) -> int:
    """Count words in a string."""
    return len(text.split())


def builtin_tools() -> list[Tool]:
    return [
        Tool(name="echo", description="Return the input unchanged.", fn=echo),
        Tool(name="word_count", description="Count words in a string.", fn=word_count),
    ]
