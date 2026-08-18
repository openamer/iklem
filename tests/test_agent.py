"""Tests for the provider and agent loop — honest error reporting + tool calling."""

from __future__ import annotations

from iklem.core.agent import Agent
from iklem.providers.base import Message, Provider, ProviderResult, ToolCall


class _FakeProvider(Provider):
    name = "fake"

    def __init__(self, results: list[ProviderResult]) -> None:
        self._results = list(results)
        self.calls: list[list[Message]] = []

    def complete(self, messages: list[Message], tools=None) -> ProviderResult:
        self.calls.append(messages)
        if self._results:
            return self._results.pop(0)
        return ProviderResult(content="", ok=False, error="no more results")


def test_agent_returns_provider_result():
    agent = Agent(provider=_FakeProvider([ProviderResult(content="hi", ok=True)]))
    result = agent.respond("hello")
    assert result.ok
    assert result.content == "hi"


def test_agent_appends_history_on_success():
    agent = Agent(provider=_FakeProvider([ProviderResult(content="hi", ok=True)]))
    agent.respond("hello")
    assert len(agent.history) == 2  # user + assistant


def test_agent_does_not_append_history_on_failure():
    agent = Agent(
        provider=_FakeProvider([ProviderResult(content="", ok=False, error="boom")])
    )
    result = agent.respond("hello")
    assert not result.ok
    assert result.error == "boom"
    assert len(agent.history) == 0


def test_agent_includes_system_prompt():
    agent = Agent(
        provider=_FakeProvider([ProviderResult(content="hi", ok=True)]),
        system_prompt="You are a test.",
    )
    agent.respond("hello")
    messages = agent.provider.calls[0]
    assert messages[0].role == "system"
    assert messages[0].content == "You are a test."
    assert messages[-1].role == "user"
    assert messages[-1].content == "hello"


def test_agent_executes_tool_call_then_answers():
    """The model first asks for the date, then answers from the tool result."""
    provider = _FakeProvider(
        [
            ProviderResult(tool_calls=[ToolCall(name="current_date", arguments={})]),
            ProviderResult(content="Today is 2026-08-18.", ok=True),
        ]
    )
    agent = Agent(provider=provider)
    result = agent.respond("what is today's date?")
    assert result.ok
    assert result.content == "Today is 2026-08-18."
    # The second call should have received a tool result message.
    second_messages = provider.calls[1]
    roles = [m.role for m in second_messages]
    assert "tool" in roles


def test_agent_unknown_tool_returns_error():
    provider = _FakeProvider(
        [
            ProviderResult(tool_calls=[ToolCall(name="does_not_exist", arguments={})]),
            ProviderResult(content="I couldn't do that.", ok=True),
        ]
    )
    agent = Agent(provider=provider)
    result = agent.respond("do something")
    assert result.ok
    # The tool result fed back should mention the unknown tool.
    tool_msgs = [m for m in provider.calls[1] if m.role == "tool"]
    assert tool_msgs
    assert "unknown tool" in tool_msgs[0].content
