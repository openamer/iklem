"""Tests for tools and channels — the plugin kinds beyond provider."""

from __future__ import annotations

from iklem.tools.base import builtin_tools, echo, word_count


def test_echo_tool():
    assert echo("hello") == "hello"


def test_word_count_tool():
    assert word_count("one two three") == 3


def test_builtin_tools_registered():
    tools = builtin_tools()
    names = {t.name for t in tools}
    assert "echo" in names
    assert "word_count" in names


def test_tool_is_callable():
    tool = builtin_tools()[0]
    assert callable(tool)
