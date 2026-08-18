"""Ollama provider — a local model backend with native tool calling.

Ollama's /api/chat supports a `tools` parameter and returns
`message.tool_calls` when the model decides to call a tool. This provider
surfaces those tool calls so the agent loop can execute them.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from iklem.providers.base import Message, Provider, ProviderResult, ToolCall


class OllamaProvider(Provider):
    name = "ollama"

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        think: bool = False,
    ) -> None:
        self.model = model or os.environ.get("IKLEM_OLLAMA_MODEL", "deepseek-v4-flash:cloud")
        self.base_url = (
            base_url or os.environ.get("IKLEM_OLLAMA_URL", "http://localhost:11434")
        ).rstrip("/")
        self.think = think

    def complete(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> ProviderResult:
        payload: dict = {
            "model": self.model,
            "messages": [self._to_ollama(m) for m in messages],
            "stream": False,
            "think": self.think,
        }
        if tools:
            payload["tools"] = tools

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
                ok=False,
                error=f"ollama not reachable at {self.base_url}: {e.reason}",
            )
        except urllib.error.HTTPError as e:
            return ProviderResult(
                ok=False,
                error=f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}",
            )

        message = data.get("message", {})
        tool_calls = []
        for tc in message.get("tool_calls", []):
            fn = tc.get("function", {})
            name = fn.get("name", "")
            raw_args = fn.get("arguments", "{}") or "{}"
            if isinstance(raw_args, dict):
                args = raw_args
            else:
                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError:
                    args = {}
            tool_calls.append(ToolCall(name=name, arguments=args))

        content = message.get("content", "")
        return ProviderResult(content=content, ok=True, tool_calls=tool_calls)

    @staticmethod
    def _to_ollama(m: Message) -> dict:
        msg: dict = {"role": m.role, "content": m.content}
        if m.role == "tool":
            # Ollama expects tool results as a "tool" role message with the
            # tool name; we encode the name in content for simplicity.
            msg["content"] = m.content
        return msg
