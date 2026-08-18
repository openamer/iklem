"""The swarm — nodes share curated, signed, leak-free knowledge.

This is the A2A idea: every iklem install is a node, and nodes exchange
knowledge over a relay. The core primitive is a signed, verifiable knowledge
packet — so a node can trust what it receives without trusting the relay.

This module implements the packet format and signing/verification. The relay
transport (GitHub, HTTP, etc.) is a separate concern and plugs in later.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field


@dataclass
class KnowledgePacket:
    """A signed unit of shareable knowledge.

    The signature is an HMAC over the canonical payload, keyed by the node's
    secret. A receiver with the shared secret can verify the packet was not
    tampered with in transit — "leak-free" means the payload is curated
    (no secrets/PII) before it is ever signed.
    """

    node_id: str
    kind: str  # "skill" | "memory" | "note"
    content: str
    timestamp: float = field(default_factory=time.time)
    signature: str = ""

    def canonical(self) -> str:
        """The exact bytes that get signed — order-stable, no whitespace drift."""
        return json.dumps(
            {
                "node_id": self.node_id,
                "kind": self.kind,
                "content": self.content,
                "timestamp": self.timestamp,
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    def sign(self, secret: str) -> None:
        self.signature = _hmac(self.canonical(), secret)

    def verify(self, secret: str) -> bool:
        if not self.signature:
            return False
        return hmac.compare_digest(self.signature, _hmac(self.canonical(), secret))


def _hmac(message: str, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()


def is_leak_free(content: str) -> bool:
    """A coarse, honest check that a packet carries no obvious secrets.

    This is a heuristic, not a guarantee — it flags common secret shapes so a
    node can refuse to sign/share them. Real redaction is layered on top.
    """
    lowered = content.lower()
    markers = [
        "api_key", "apikey", "password", "secret", "token",
        "-----begin", "ghp_", "sk-", "bearer ",
    ]
    return not any(m in lowered for m in markers)
