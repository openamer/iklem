"""Tests for the upgraded delegation (roles, toolsets, orchestration)."""

from __future__ import annotations

from iklem.delegate import ROLES, _tools_for, delegate, pipeline
from iklem.providers.base import Provider, ProviderResult


class EchoProvider(Provider):
    """A fake provider that returns a fixed answer without calling tools."""

    def __init__(self, answer: str = "done"):
        self.answer = answer

    def complete(self, messages, tools=None):
        return ProviderResult(ok=True, content=self.answer)


def test_roles_defined():
    assert "researcher" in ROLES
    assert "coder" in ROLES
    assert "writer" in ROLES
    assert "reviewer" in ROLES


def test_tools_for_role_is_subset():
    researcher = _tools_for("researcher")
    names = {t.name for t in researcher}
    assert "search_web" in names
    assert "run_python" not in names  # researcher has no code tools


def test_tools_for_unknown_role_returns_full_set():
    full = _tools_for(None)
    assert len(full) > 10


def test_delegate_runs_tasks_in_parallel():
    provider = EchoProvider("ok")
    results = delegate(provider, ["a", "b", "c"])
    assert len(results) == 3
    assert all(r.result.ok for r in results)
    assert all(r.result.content == "ok" for r in results)


def test_pipeline_runs_sequentially():
    provider = EchoProvider("stage output")
    results = pipeline(provider, ["t1", "t2", "t3"])
    assert len(results) == 3
    assert all(r.result.ok for r in results)
