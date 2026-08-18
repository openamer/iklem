"""Tests for the gateway — channel fan-out."""

from __future__ import annotations

from iklem.gateway.gateway import _configured_channels


def test_no_channels_without_credentials(monkeypatch):
    for var in [
        "IKLEM_TELEGRAM_TOKEN",
        "IKLEM_SLACK_TOKEN",
        "IKLEM_SLACK_CHANNEL",
        "IKLEM_DISCORD_TOKEN",
        "IKLEM_DISCORD_CHANNEL",
    ]:
        monkeypatch.delenv(var, raising=False)
    channels = _configured_channels(agent=None)
    assert channels == []


def test_telegram_channel_when_token_set(monkeypatch):
    monkeypatch.setenv("IKLEM_TELEGRAM_TOKEN", "test-token")
    monkeypatch.delenv("IKLEM_SLACK_TOKEN", raising=False)
    monkeypatch.delenv("IKLEM_DISCORD_TOKEN", raising=False)
    channels = _configured_channels(agent=None)
    assert len(channels) == 1
    assert channels[0].name == "telegram"


def test_multiple_channels(monkeypatch):
    monkeypatch.setenv("IKLEM_TELEGRAM_TOKEN", "t")
    monkeypatch.setenv("IKLEM_SLACK_TOKEN", "s")
    monkeypatch.setenv("IKLEM_SLACK_CHANNEL", "c")
    monkeypatch.setenv("IKLEM_DISCORD_TOKEN", "d")
    monkeypatch.setenv("IKLEM_DISCORD_CHANNEL", "c")
    channels = _configured_channels(agent=None)
    names = {c.name for c in channels}
    assert names == {"telegram", "slack", "discord"}


def test_whatsapp_and_signal_channels(monkeypatch):
    monkeypatch.setenv("IKLEM_WHATSAPP_TOKEN", "w")
    monkeypatch.setenv("IKLEM_WHATSAPP_PHONE_ID", "p")
    monkeypatch.setenv("IKLEM_SIGNAL_NUMBER", "+123")
    channels = _configured_channels(agent=None)
    names = {c.name for c in channels}
    assert names == {"whatsapp", "signal"}
