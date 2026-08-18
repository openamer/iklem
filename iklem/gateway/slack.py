"""Slack channel — a channel plugin using the Slack Web API.

Dependency-free (urllib). Uses the Slack `conversations.history` polling
model, mirroring the Telegram channel. Requires IKLEM_SLACK_TOKEN and
IKLEM_SLACK_CHANNEL. Reports honest errors when configuration is missing.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from iklem.gateway.base import Channel


class SlackChannel(Channel):
    name = "slack"

    def __init__(self, token: str | None = None, channel: str | None = None) -> None:
        self.token = token or os.environ.get("IKLEM_SLACK_TOKEN", "")
        self.channel = channel or os.environ.get("IKLEM_SLACK_CHANNEL", "")
        self._last_ts = "0"

    def _api(self, method: str, **params) -> dict:
        url = f"https://slack.com/api/{method}"
        data = {k: v for k, v in params.items()}
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def start(self, agent) -> None:
        if not self.token:
            print("✗ Slack channel: no IKLEM_SLACK_TOKEN set")
            return
        if not self.channel:
            print("✗ Slack channel: no IKLEM_SLACK_CHANNEL set")
            return
        print(f"✓ Slack channel polling #{self.channel} (Ctrl+C to stop)")
        while True:
            try:
                resp = self._api(
                    "conversations.history",
                    channel=self.channel,
                    oldest=self._last_ts,
                )
            except (urllib.error.URLError, urllib.error.HTTPError) as e:
                print(f"✗ Slack poll error: {e}")
                time.sleep(5)
                continue
            if not resp.get("ok"):
                print(f"✗ Slack API error: {resp.get('error')}")
                time.sleep(5)
                continue
            for msg in resp.get("messages", []):
                self._last_ts = max(self._last_ts, msg.get("ts", self._last_ts))
                text = msg.get("text", "")
                if not text or msg.get("bot_id"):
                    continue
                result = agent.respond(text)
                reply = result.content if result.ok else f"✗ {result.error}"
                try:
                    self._api(
                        "chat.postMessage",
                        channel=self.channel,
                        text=reply,
                    )
                except (urllib.error.URLError, urllib.error.HTTPError) as e:
                    print(f"✗ Slack send error: {e}")
            time.sleep(3)
