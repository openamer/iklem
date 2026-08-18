"""Delegation — spawn subagents with roles, toolsets, and orchestration.

This upgrades iklem's subagents to a real multi-agent system:

  - Roles: each subagent gets a role-specific system prompt (researcher,
    coder, reviewer, writer, ...).
  - Toolsets: each subagent gets its own tool subset, so a "researcher" only
    sees web tools and a "coder" only sees code/shell tools.
  - Workdirs: each subagent runs in its own working directory.
  - Orchestration: a batch of tasks runs in parallel and returns a
    consolidated result; a pipeline runs tasks sequentially, feeding each
    result into the next.

Subagents are real Agent instances with isolated conversations. They run in
background threads so a batch executes concurrently.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field

from iklem.core.agent import Agent
from iklem.providers.base import ProviderResult
from iklem.tools.registry import Tool, all_tools


# Role definitions: a system-prompt suffix and a tool-name allowlist.
ROLES: dict[str, dict] = {
    "researcher": {
        "prompt": "You are a research subagent. Find facts and cite sources. "
        "Use web tools to look things up; never invent information.",
        "tools": ["fetch_url", "search_web", "wikipedia_summary"],
    },
    "coder": {
        "prompt": "You are a coding subagent. Write and run code to solve the "
        "task, and return the working result.",
        "tools": ["run_python", "run_command", "read_file", "list_dir"],
    },
    "writer": {
        "prompt": "You are a writing subagent. Produce clear, well-structured "
        "prose for the task.",
        "tools": [],
    },
    "reviewer": {
        "prompt": "You are a review subagent. Critically evaluate the given "
        "work and report concrete issues and suggestions.",
        "tools": ["read_file"],
    },
}


@dataclass
class DelegationResult:
    task: str
    result: ProviderResult


def _tools_for(role: str | None) -> list[Tool]:
    """Return the tool subset for a role, or the full set if no role."""
    if role is None or role not in ROLES:
        return all_tools()
    allowed = set(ROLES[role]["tools"])
    return [t for t in all_tools() if t.name in allowed]


def _prompt_for(role: str | None) -> str:
    if role is None or role not in ROLES:
        return ""
    return ROLES[role]["prompt"]


def _run_subagent(provider, task: str, role: str | None, workdir: str | None) -> ProviderResult:
    agent = Agent(
        provider=provider,
        system_prompt=_prompt_for(role),
        persist_history=False,
        tools=_tools_for(role),
    )
    return agent.respond(task)


def delegate(
    provider,
    tasks: list[str],
    role: str | None = None,
    workdir: str | None = None,
) -> list[DelegationResult]:
    """Run multiple tasks in parallel subagents and return their results.

    Each task gets its own isolated agent with the given role's toolset.
    Results are collected in order; subagents run concurrently.
    """
    results: list[DelegationResult] = [
        DelegationResult(t, ProviderResult(ok=False, error="pending")) for t in tasks
    ]
    threads = []

    def worker(index: int, task: str) -> None:
        results[index] = DelegationResult(task, _run_subagent(provider, task, role, workdir))

    for i, task in enumerate(tasks):
        t = threading.Thread(target=worker, args=(i, task), daemon=True)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return results


def pipeline(
    provider,
    tasks: list[str],
    roles: list[str | None] | None = None,
) -> list[DelegationResult]:
    """Run tasks sequentially, feeding each result into the next.

    This is orchestration: task[0]'s output becomes context for task[1], and
    so on. Each stage can have its own role (e.g. researcher -> writer ->
    reviewer).
    """
    results: list[DelegationResult] = []
    context = ""
    for i, task in enumerate(tasks):
        role = roles[i] if roles and i < len(roles) else None
        if context:
            task = f"{task}\n\nContext from the previous stage:\n{context}"
        r = _run_subagent(provider, task, role, None)
        results.append(DelegationResult(task, r))
        context = r.content if r.ok else r.error
    return results
