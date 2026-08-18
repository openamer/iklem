"""Delegation tool — the agent spawns a subagent for a task."""

from __future__ import annotations


def delegate_task(task: str) -> str:
    """Run a task in a fresh subagent and return its result.

    The subagent has its own isolated conversation. Returns the subagent's
    answer or an honest error.
    """
    # Lazy import to avoid a circular import (delegate -> agent -> registry).
    from iklem.delegate import delegate
    from iklem.providers.ollama import OllamaProvider

    provider = OllamaProvider()
    results = delegate(provider, [task])
    r = results[0].result
    return r.content if r.ok else f"✗ {r.error}"
