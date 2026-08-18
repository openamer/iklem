"""The agent loop — turns a user message into a model response.

The loop is model-agnostic: it takes a Provider and a conversation, and
returns an honest result. It never fabricates a response when the provider
fails.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from iklem.providers.base import Message, Provider, ProviderResult


@dataclass
class Agent:
    """A minimal agent: a provider plus a conversation history."""

    provider: Provider
    system_prompt: str = "You are iklem, a helpful personal AI agent."
    history: list[Message] = field(default_factory=list)

    def respond(self, user: str) -> ProviderResult:
        """Respond to a user message, appending to history on success."""
        messages = [Message(role="system", content=self.system_prompt)]
        messages.extend(self.history)
        messages.append(Message(role="user", content=user))

        result = self.provider.complete(messages)

        if result.ok:
            self.history.append(Message(role="user", content=user))
            self.history.append(Message(role="assistant", content=result.content))
        return result
