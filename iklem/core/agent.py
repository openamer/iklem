"""The agent loop — turns a user message into a grounded answer.

This is what makes iklem an agent rather than a chatbot: when the model
requests a tool call, the loop executes the tool, feeds the result back, and
lets the model answer from real data instead of guessing. The loop iterates
until the model produces a final answer (or a safety cap is hit).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from iklem.providers.base import Message, Provider, ProviderResult, ToolCall
from iklem.tools.registry import all_tools, tool_by_name


def _tool_schema(tool) -> dict:
    """Build an OpenAI/Ollama-style tool schema from a Tool."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    }


@dataclass
class Agent:
    """An agent: a provider, a tool set, and a conversation history."""

    provider: Provider
    system_prompt: str = (
        "You are iklem, a helpful personal AI agent with access to tools. "
        "You MUST call a tool to learn any fact about the real world — the "
        "current date, the current time, system information, or file contents. "
        "Never guess or invent a date, time, or fact. If a tool exists for the "
        "question, call it and answer from its result."
    )
    history: list[Message] = field(default_factory=list)
    max_tool_rounds: int = 5

    def respond(self, user: str) -> ProviderResult:
        """Respond to a user message, calling tools as needed."""
        messages = [Message(role="system", content=self.system_prompt)]
        messages.extend(self.history)
        messages.append(Message(role="user", content=user))

        tools = all_tools()
        schemas = [_tool_schema(t) for t in tools]

        for _ in range(self.max_tool_rounds):
            result = self.provider.complete(messages, tools=schemas)
            if not result.ok:
                return result

            if not result.tool_calls:
                # Final answer.
                self.history.append(Message(role="user", content=user))
                self.history.append(Message(role="assistant", content=result.content))
                return result

            # Execute tool calls and append results for the next round.
            messages.append(
                Message(
                    role="assistant",
                    content=result.content or "",
                    tool_name=result.tool_calls[0].name if result.tool_calls else None,
                )
            )
            for tc in result.tool_calls:
                output = self._run_tool(tc)
                messages.append(
                    Message(
                        role="tool",
                        content=output,
                        tool_name=tc.name,
                    )
                )

        # Safety cap: the model kept calling tools without answering.
        return ProviderResult(
            ok=False,
            error="tool-call loop exceeded the safety cap",
        )

    def _run_tool(self, call: ToolCall) -> str:
        tool = tool_by_name(call.name)
        if tool is None:
            return f"(unknown tool: {call.name})"
        try:
            result = tool.fn(**call.arguments)
        except TypeError as e:
            return f"(tool error: {e})"
        except Exception as e:  # noqa: BLE001 — a tool must never crash the loop
            return f"(tool error: {e})"
        if not isinstance(result, str):
            result = json.dumps(result, ensure_ascii=False)
        return result
