"""Telegram channel — the second channel, proving the gateway abstraction.

This is a real channel plugin: it polls the Telegram Bot API and routes
messages to the agent. It is deliberately dependency-free (uses urllib, not
a Telegram SDK) so the core stays lean.

Requires IKLEM_TELEGRAM_TOKEN to be set. Without it, start() reports an
honest error instead of silently doing nothing.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from iklem.gateway.base import Channel


class TelegramChannel(Channel):
    name = "telegram"

    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.environ.get("IKLEM_TELEGRAM_TOKEN", "")
        self._offset = 0

    def _api(self, method: str, **params) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/{method}"
        if params:
            url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def start(self, agent) -> None:
        if not self.token:
            print("✗ Telegram channel: no IKLEM_TELEGRAM_TOKEN set")
            return
        print("✓ Telegram channel polling (Ctrl+C to stop)")
        while True:
            try:
                updates = self._api("getUpdates", offset=self._offset, timeout=30)
            except (urllib.error.URLError, urllib.error.HTTPError) as e:
                print(f"✗ Telegram poll error: {e}")
                time.sleep(5)
                continue
            for upd in updates.get("result", []):
                self._offset = upd["update_id"] + 1
                msg = upd.get("message")
                if not msg or "text" not in msg:
                    continue
                chat_id = msg["chat"]["id"]
                text = msg["text"]
                result = agent.respond(text)
                reply = result.content if result.ok else f"✗ {result.error}"
                try:
                    self._api("sendMessage", chat_id=chat_id, text=reply)
                except (urllib.error.URLError, urllib.error.HTTPError) as e:
                    print(f"✗ Telegram send error: {e}")
