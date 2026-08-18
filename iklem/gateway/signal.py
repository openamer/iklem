"""Signal channel — a channel plugin using the Signal CLI (signal-cli).

Signal has no official bot API; the standard approach is `signal-cli`, a
command-line client that speaks the Signal protocol. This plugin shells out
to signal-cli to send messages, with honest errors when it is not installed.

Requires IKLEM_SIGNAL_NUMBER and signal-cli on PATH.
"""

from __future__ import annotations

import os
import subprocess

from iklem.gateway.base import Channel


class SignalChannel(Channel):
    name = "signal"

    def __init__(self, number: str | None = None) -> None:
        self.number = number or os.environ.get("IKLEM_SIGNAL_NUMBER", "")

    def send(self, to: str, text: str) -> bool:
        """Send a Signal message via signal-cli."""
        try:
            proc = subprocess.run(
                ["signal-cli", "-a", self.number, "send", "-m", text, to],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return proc.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def start(self, agent) -> None:
        if not self.number:
            print("✗ Signal channel: set IKLEM_SIGNAL_NUMBER")
            return
        # Check signal-cli is available.
        try:
            subprocess.run(["signal-cli", "--version"], capture_output=True, timeout=10)
        except FileNotFoundError:
            print("✗ Signal channel: signal-cli not found on PATH")
            return
        print("✓ Signal channel: send() ready (inbound receive is a deployment step)")
