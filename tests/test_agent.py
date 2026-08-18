"""Tests for the provider and agent loop — honest error reporting."""

from __future__ import annotations

from iklem.core.agent import Agent
from iklem.providers.base import Message, Provider, ProviderResult


class _FakeProvider(Provider):
    name = "fake"

    def __init__(self, result: ProviderResult) -> None:
        self._result = result
        self.calls: list[list[Message]] = []

    def complete(self, messages: list[Message]) -> ProviderResult:
        self.calls.append(messages)
        return self._result


def test_agent_returns_provider_result():
    agent = Agent(provider=_FakeProvider(ProviderResult(content="hi", ok=True)))
    result = agent.respond("hello")
    assert result.ok
    assert result.content == "hi"


def test_agent_appends_history_on_success():
    agent = Agent(provider=_FakeProvider(ProviderResult(content="hi", ok=True)))
    agent.respond("hello")
    assert len(agent.history) == 2  # user + assistant


def test_agent_does_not_append_history_on_failure():
    agent = Agent(
        provider=_FakeProvider(ProviderResult(content="", ok=False, error="boom"))
    )
    result = agent.respond("hello")
    assert not result.ok
    assert result.error == "boom"
    assert len(agent.history) == 0


def test_agent_includes_system_prompt():
    agent = Agent(
        provider=_FakeProvider(ProviderResult(content="hi", ok=True)),
        system_prompt="You are a test.",
    )
    agent.respond("hello")
    messages = agent.provider.calls[0]
    assert messages[0].role == "system"
    assert messages[0].content == "You are a test."
    assert messages[-1].role == "user"
    assert messages[-1].content == "hello"
