"""Tests for session search, vision, and TTS tools."""

from __future__ import annotations

from iklem.tools.session import search_sessions
from iklem.tools.tts import speak, speak_to_file
from iklem.tools.vision import describe_image


def test_search_sessions_empty_query():
    assert search_sessions("").startswith("✗")


def test_search_sessions_no_match(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    result = search_sessions("zzz_nonexistent_zzz")
    assert "no past conversation" in result


def test_search_sessions_finds_history(tmp_path, monkeypatch):
    import json

    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    d = tmp_path / "iklem"
    d.mkdir(parents=True)
    (d / "history.json").write_text(
        json.dumps([{"role": "user", "content": "my favorite color is blue"}])
    )
    result = search_sessions("blue")
    assert "blue" in result


def test_describe_image_no_endpoint(tmp_path, monkeypatch):
    monkeypatch.delenv("IKLEM_VISION_URL", raising=False)
    result = describe_image("nonexistent.png")
    assert result.startswith("✗")


def test_speak_empty():
    assert speak("").startswith("✗")


def test_speak_to_file_empty():
    assert speak_to_file("", "x.wav").startswith("✗")
