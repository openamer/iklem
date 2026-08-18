"""OpenAI-compatible provider — works with OpenAI, OpenRouter, and any
endpoint that speaks the OpenAI chat-completions protocol.

This is the first real provider plugin. It reports honest errors instead of
fabricating a response when the API call fails.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from iklem.providers.base import Message, Provider, ProviderResult


class OpenAICompatibleProvider(Provider):
    name = "openai-compatible"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("IKLEM_API_KEY", "")
        self.base_url = (
            base_url
            or os.environ.get("IKLEM_BASE_URL", "https://api.openai.com/v1")
        ).rstrip("/")
        self.model = model or os.environ.get("IKLEM_MODEL", "gpt-4o-mini")

    def complete(self, messages: list[Message]) -> ProviderResult:
        if not self.api_key:
            return ProviderResult(
                content="",
                ok=False,
                error="no API key — set IKLEM_API_KEY",
            )

        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return ProviderResult(
                content="",
                ok=False,
                error=f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}",
            )
        except urllib.error.URLError as e:
            return ProviderResult(content="", ok=False, error=f"network error: {e.reason}")

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            return ProviderResult(
                content="",
                ok=False,
                error=f"unexpected response shape: {e}",
            )
        return ProviderResult(content=content, ok=True)
