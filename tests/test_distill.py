"""Tests for deterministic skill distillation."""

from __future__ import annotations

from iklem.core.agent import Agent, _slugify
from iklem.providers.base import Provider, ProviderResult, ToolCall


class _FakeProvider(Provider):
    name = "fake"

    def __init__(self, results):
        self._results = list(results)

    def complete(self, messages, tools=None):
        if self._results:
            return self._results.pop(0)
        return ProviderResult(content="", ok=False, error="no more results")


def test_slugify():
    assert _slugify("Deploy the app to GitHub") == "deploy-the-app-to-github"


def test_multi_tool_task_distills_skill(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    provider = _FakeProvider(
        [
            ProviderResult(tool_calls=[ToolCall(name="current_date", arguments={})]),
            ProviderResult(tool_calls=[ToolCall(name="system_info", arguments={})]),
            ProviderResult(content="done", ok=True),
        ]
    )
    agent = Agent(provider=provider, persist_history=False)
    agent.respond("check the system status")

    from iklem.memory.skills import SkillRegistry
    from iklem.memory.store import MemoryStore

    reg = SkillRegistry(MemoryStore())
    names = reg.names()
    assert "check-the-system-status" in names


def test_single_tool_task_does_not_distill(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    provider = _FakeProvider(
        [
            ProviderResult(tool_calls=[ToolCall(name="current_date", arguments={})]),
            ProviderResult(content="today", ok=True),
        ]
    )
    agent = Agent(provider=provider, persist_history=False)
    agent.respond("what is today")

    from iklem.memory.skills import SkillRegistry
    from iklem.memory.store import MemoryStore

    reg = SkillRegistry(MemoryStore())
    assert "what-is-today" not in reg.names()
