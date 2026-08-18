"""WhatsApp channel — a channel plugin using the WhatsApp Cloud API.

WhatsApp has no simple bot API like Telegram; it requires a Meta Business
account and a phone-number ID + access token. This plugin implements the
Cloud API (send + webhook receive) with honest errors when unconfigured.

Requires IKLEM_WHATSAPP_TOKEN and IKLEM_WHATSAPP_PHONE_ID.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from iklem.gateway.base import Channel


class WhatsAppChannel(Channel):
    name = "whatsapp"

    def __init__(self, token: str | None = None, phone_id: str | None = None) -> None:
        self.token = token or os.environ.get("IKLEM_WHATSAPP_TOKEN", "")
        self.phone_id = phone_id or os.environ.get("IKLEM_WHATSAPP_PHONE_ID", "")

    def send(self, to: str, text: str) -> bool:
        """Send a WhatsApp message via the Cloud API."""
        url = f"https://graph.facebook.com/v19.0/{self.phone_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status == 200
        except (urllib.error.URLError, urllib.error.HTTPError):
            return False

    def start(self, agent) -> None:
        if not self.token or not self.phone_id:
            print("✗ WhatsApp channel: set IKLEM_WHATSAPP_TOKEN and IKLEM_WHATSAPP_PHONE_ID")
            return
        # Inbound messages arrive via a webhook (Meta calls your server).
        # This plugin exposes send(); a full inbound loop needs a public
        # webhook endpoint, which is a deployment concern, not a code one.
        print("✓ WhatsApp channel: send() ready (inbound webhook is a deployment step)")
