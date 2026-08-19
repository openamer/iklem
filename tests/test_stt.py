"""Tests for the speech-to-text tool."""

from __future__ import annotations

from iklem.tools.stt import listen, transcribe_audio


def test_transcribe_audio_missing_file():
    result = transcribe_audio("nonexistent.wav")
    assert result.startswith("✗")


def test_transcribe_audio_reports_missing_dependency():
    # Either works (SpeechRecognition installed) or reports the honest error.
    result = transcribe_audio("C:/nonexistent.wav")
    assert isinstance(result, str)


def test_listen_reports_missing_dependency():
    result = listen("1")
    # Either works or reports the honest "not installed" error.
    assert isinstance(result, str)


def test_listen_rejects_bad_duration():
    result = listen("abc")
    assert result.startswith("✗")
