"""Node identity and the swarm transport.

A node is an iklem install with an identity (id + secret). Nodes exchange
signed KnowledgePackets over a relay. The relay is untrusted: it only stores
and forwards packets; authenticity comes from the HMAC signature, so a node
verifies every packet it receives against the shared secret.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from iklem.swarm.packet import KnowledgePacket


@dataclass
class Node:
    """A swarm node: an identity plus a secret for signing/verifying."""

    node_id: str
    secret: str

    @classmethod
    def from_env(cls) -> "Node":
        node_id = os.environ.get("IKLEM_NODE_ID", "anonymous")
        secret = os.environ.get("IKLEM_SWARM_SECRET", "dev-secret")
        return cls(node_id=node_id, secret=secret)

    def sign(self, kind: str, content: str) -> KnowledgePacket:
        pkt = KnowledgePacket(node_id=self.node_id, kind=kind, content=content)
        pkt.sign(self.secret)
        return pkt

    def verify(self, pkt: KnowledgePacket) -> bool:
        return pkt.verify(self.secret)


class RelayClient:
    """Talks to a swarm relay over HTTP.

    The relay is a dumb store-and-forward: POST to publish a packet, GET to
    list packets. All trust is in the packet signature, not the relay.
    """

    def __init__(self, relay_url: str) -> None:
        self.relay_url = relay_url.rstrip("/")

    def publish(self, pkt: KnowledgePacket) -> bool:
        payload = {
            "node_id": pkt.node_id,
            "kind": pkt.kind,
            "content": pkt.content,
            "timestamp": pkt.timestamp,
            "signature": pkt.signature,
        }
        req = urllib.request.Request(
            f"{self.relay_url}/packets",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status == 200
        except (urllib.error.URLError, urllib.error.HTTPError):
            return False

    def list(self) -> list[KnowledgePacket]:
        req = urllib.request.Request(f"{self.relay_url}/packets")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError):
            return []
        packets = []
        for item in data:
            pkt = KnowledgePacket(
                node_id=item["node_id"],
                kind=item["kind"],
                content=item["content"],
                timestamp=item.get("timestamp", 0.0),
                signature=item.get("signature", ""),
            )
            packets.append(pkt)
        return packets
