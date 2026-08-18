"""Delegation — spawn subagents to work on tasks in parallel.

This gives iklem the ability to delegate a task to a subagent (a fresh agent
with its own conversation) and get the result back. Subagents run in
background threads, so multiple tasks can run concurrently.

This is a lightweight version of OpenAmer's delegate_task: it spawns a new
Agent with the same provider and runs a single prompt, returning the result.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field

from iklem.core.agent import Agent
from iklem.providers.base import ProviderResult


@dataclass
class DelegationResult:
    task: str
    result: ProviderResult


def _run_subagent(provider, task: str, system_prompt: str) -> ProviderResult:
    agent = Agent(provider=provider, system_prompt=system_prompt, persist_history=False)
    return agent.respond(task)


def delegate(provider, tasks: list[str], system_prompt: str = "") -> list[DelegationResult]:
    """Run multiple tasks in parallel subagents and return their results.

    Each task gets its own agent (isolated conversation). Results are
    collected in order. This is synchronous (waits for all), but the
    subagents run concurrently.
    """
    results: list[DelegationResult] = [DelegationResult(t, ProviderResult(ok=False, error="pending")) for t in tasks]
    threads = []

    def worker(index: int, task: str) -> None:
        results[index] = DelegationResult(task, _run_subagent(provider, task, system_prompt))

    for i, task in enumerate(tasks):
        t = threading.Thread(target=worker, args=(i, task), daemon=True)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return results
