"""Ollama provider — a local model backend, no API key required.

Ollama speaks a simple HTTP API on localhost:11434. This provider is the
simplest way to run iklem with a real model on your own machine, fully
offline and private.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from iklem.providers.base import Message, Provider, ProviderResult


class OllamaProvider(Provider):
    name = "ollama"

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        think: bool = False,
    ) -> None:
        self.model = model or os.environ.get("IKLEM_OLLAMA_MODEL", "qwen3:1.7b")
        self.base_url = (
            base_url or os.environ.get("IKLEM_OLLAMA_URL", "http://localhost:11434")
        ).rstrip("/")
        # Disable the "thinking" (chain-of-thought) block by default: on CPU
        # it can add tens of seconds of latency for no user-visible benefit.
        self.think = think

    def complete(self, messages: list[Message]) -> ProviderResult:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "think": self.think,
        }
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            return ProviderResult(
                content="",
                ok=False,
                error=f"ollama not reachable at {self.base_url}: {e.reason}",
            )
        except urllib.error.HTTPError as e:
            return ProviderResult(
                content="",
                ok=False,
                error=f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}",
            )

        try:
            content = data["message"]["content"]
        except (KeyError, TypeError) as e:
            return ProviderResult(
                content="",
                ok=False,
                error=f"unexpected response shape: {e}",
            )
        return ProviderResult(content=content, ok=True)
