"""OpenAI-compatible provider — with tool calling.

Works with OpenAI, OpenRouter, and any endpoint speaking the OpenAI
chat-completions protocol. Surfaces tool calls so the agent loop can execute
them.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from iklem.providers.base import Message, Provider, ProviderResult, ToolCall


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

    def complete(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> ProviderResult:
        if not self.api_key:
            return ProviderResult(ok=False, error="no API key — set IKLEM_API_KEY")

        payload: dict = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        if tools:
            payload["tools"] = tools

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
                ok=False,
                error=f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}",
            )
        except urllib.error.URLError as e:
            return ProviderResult(ok=False, error=f"network error: {e.reason}")

        try:
            choice = data["choices"][0]["message"]
        except (KeyError, IndexError) as e:
            return ProviderResult(ok=False, error=f"unexpected response shape: {e}")

        tool_calls = []
        for tc in choice.get("tool_calls", []):
            fn = tc.get("function", {})
            name = fn.get("name", "")
            try:
                args = json.loads(fn.get("arguments", "{}") or "{}")
            except json.JSONDecodeError:
                args = {}
            tool_calls.append(ToolCall(name=name, arguments=args))

        return ProviderResult(
            content=choice.get("content", ""),
            ok=True,
            tool_calls=tool_calls,
        )
