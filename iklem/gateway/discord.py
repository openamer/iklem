"""Discord channel — a channel plugin using the Discord REST API.

Dependency-free (urllib). Polls the channel's messages via the REST API
(`/channels/{id}/messages`) and replies via `createMessage`. Requires
IKLEM_DISCORD_TOKEN and IKLEM_DISCORD_CHANNEL. Reports honest errors when
configuration is missing.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from iklem.gateway.base import Channel


class DiscordChannel(Channel):
    name = "discord"

    def __init__(self, token: str | None = None, channel: str | None = None) -> None:
        self.token = token or os.environ.get("IKLEM_DISCORD_TOKEN", "")
        self.channel = channel or os.environ.get("IKLEM_DISCORD_CHANNEL", "")
        self._last_id = "0"

    def _api(self, method: str, path: str, payload: dict | None = None) -> dict:
        url = f"https://discord.com/api/v10{path}"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8") if payload else None,
            headers={
                "Authorization": f"Bot {self.token}",
                "Content-Type": "application/json",
            },
            method=method,
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def start(self, agent) -> None:
        if not self.token:
            print("✗ Discord channel: no IKLEM_DISCORD_TOKEN set")
            return
        if not self.channel:
            print("✗ Discord channel: no IKLEM_DISCORD_CHANNEL set")
            return
        print(f"✓ Discord channel polling #{self.channel} (Ctrl+C to stop)")
        while True:
            try:
                messages = self._api(
                    "GET", f"/channels/{self.channel}/messages?limit=10"
                )
            except (urllib.error.URLError, urllib.error.HTTPError) as e:
                print(f"✗ Discord poll error: {e}")
                time.sleep(5)
                continue
            for msg in reversed(messages):
                if msg.get("author", {}).get("bot"):
                    continue
                if msg["id"] <= self._last_id:
                    continue
                self._last_id = msg["id"]
                text = msg.get("content", "")
                if not text:
                    continue
                result = agent.respond(text)
                reply = result.content if result.ok else f"✗ {result.error}"
                try:
                    self._api(
                        "POST",
                        f"/channels/{self.channel}/messages",
                        {"content": reply},
                    )
                except (urllib.error.URLError, urllib.error.HTTPError) as e:
                    print(f"✗ Discord send error: {e}")
            time.sleep(3)
