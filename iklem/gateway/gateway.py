"""The gateway — one process that fans out to every configured channel.

This is the platform-breadth idea made concrete: instead of running each
channel separately, a single `iklem gateway` process starts every channel
that has credentials configured, sharing one agent (and thus one memory,
history, and tool set) across all of them.
"""

from __future__ import annotations

import os
import threading

from iklem.core.agent import Agent
from iklem.gateway.base import Channel


def _configured_channels(agent: Agent) -> list[Channel]:
    """Build the list of channels that have credentials configured."""
    channels: list[Channel] = []

    if os.environ.get("IKLEM_TELEGRAM_TOKEN"):
        from iklem.gateway.telegram import TelegramChannel

        channels.append(TelegramChannel())

    if os.environ.get("IKLEM_SLACK_TOKEN") and os.environ.get("IKLEM_SLACK_CHANNEL"):
        from iklem.gateway.slack import SlackChannel

        channels.append(SlackChannel())

    if os.environ.get("IKLEM_DISCORD_TOKEN") and os.environ.get("IKLEM_DISCORD_CHANNEL"):
        from iklem.gateway.discord import DiscordChannel

        channels.append(DiscordChannel())

    if os.environ.get("IKLEM_WHATSAPP_TOKEN") and os.environ.get("IKLEM_WHATSAPP_PHONE_ID"):
        from iklem.gateway.whatsapp import WhatsAppChannel

        channels.append(WhatsAppChannel())

    if os.environ.get("IKLEM_SIGNAL_NUMBER"):
        from iklem.gateway.signal import SignalChannel

        channels.append(SignalChannel())

    return channels


def run_gateway(agent: Agent) -> int:
    """Start every configured channel in its own thread, sharing one agent."""
    channels = _configured_channels(agent)
    if not channels:
        print("✗ no channels configured — set a channel token (e.g. IKLEM_TELEGRAM_TOKEN)")
        return 1

    print(f"✓ gateway starting {len(channels)} channel(s)")
    threads = []
    for channel in channels:
        t = threading.Thread(
            target=channel.start,
            args=(agent,),
            name=f"channel-{channel.name}",
            daemon=True,
        )
        t.start()
        threads.append(t)
        print(f"  • {channel.name}")

    print("(Ctrl+C to stop)")
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        pass
    return 0
