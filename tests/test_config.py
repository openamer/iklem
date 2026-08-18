"""Tests for config persistence."""

from __future__ import annotations

from iklem.server import _load_config, _save_config


def test_config_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    _save_config({"IKLEM_OLLAMA_MODEL": "test-model"})
    cfg = _load_config()
    assert cfg["IKLEM_OLLAMA_MODEL"] == "test-model"


def test_config_empty_when_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert _load_config() == {}
