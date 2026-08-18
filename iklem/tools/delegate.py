"""Delegation tools — the agent orchestrates subagents with roles and pipelines."""

from __future__ import annotations


def delegate_task(task: str) -> str:
    """Run a task in a fresh subagent and return its result."""
    from iklem.delegate import delegate
    from iklem.providers.ollama import OllamaProvider

    provider = OllamaProvider()
    results = delegate(provider, [task])
    r = results[0].result
    return r.content if r.ok else f"✗ {r.error}"


def delegate_with_role(task: str, role: str) -> str:
    """Run a task in a subagent with a specific role (researcher/coder/writer/reviewer)."""
    from iklem.delegate import delegate
    from iklem.providers.ollama import OllamaProvider

    provider = OllamaProvider()
    results = delegate(provider, [task], role=role)
    r = results[0].result
    return r.content if r.ok else f"✗ {r.error}"


def delegate_batch(tasks: str) -> str:
    """Run multiple tasks (one per line) in parallel subagents and return all results."""
    from iklem.delegate import delegate
    from iklem.providers.ollama import OllamaProvider

    task_list = [t.strip() for t in tasks.split("\n") if t.strip()]
    if not task_list:
        return "✗ no tasks provided"
    provider = OllamaProvider()
    results = delegate(provider, task_list)
    lines = []
    for i, r in enumerate(results):
        body = r.result.content if r.result.ok else f"✗ {r.result.error}"
        lines.append(f"[{i + 1}] {r.task}\n{body}")
    return "\n\n".join(lines)


def delegate_pipeline(tasks: str, roles: str) -> str:
    """Run tasks sequentially (one per line), feeding each result into the next.

    `roles` is a comma-separated list of roles (researcher/coder/writer/reviewer)
    matching the tasks in order.
    """
    from iklem.delegate import pipeline
    from iklem.providers.ollama import OllamaProvider

    task_list = [t.strip() for t in tasks.split("\n") if t.strip()]
    role_list = [r.strip() for r in roles.split(",") if r.strip()]
    if not task_list:
        return "✗ no tasks provided"
    provider = OllamaProvider()
    results = pipeline(provider, task_list, role_list or None)
    lines = []
    for i, r in enumerate(results):
        body = r.result.content if r.result.ok else f"✗ {r.result.error}"
        lines.append(f"[stage {i + 1}] {body}")
    return "\n\n".join(lines)
