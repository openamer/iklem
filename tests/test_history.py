"""Tests for persistent conversation history."""

from __future__ import annotations

import os

from iklem.memory import history as history_store
from iklem.providers.base import Message


def test_history_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    msgs = [
        Message(role="user", content="hello"),
        Message(role="assistant", content="hi there"),
    ]
    history_store.save_history(msgs)
    loaded = history_store.load_history()
    assert len(loaded) == 2
    assert loaded[0].role == "user"
    assert loaded[0].content == "hello"
    assert loaded[1].content == "hi there"


def test_history_empty_when_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    assert history_store.load_history() == []


def test_history_caps_at_limit(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    msgs = [Message(role="user", content=f"m{i}") for i in range(100)]
    history_store.save_history(msgs, limit=10)
    loaded = history_store.load_history()
    assert len(loaded) == 10
    assert loaded[-1].content == "m99"
