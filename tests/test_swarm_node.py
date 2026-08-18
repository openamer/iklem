"""Tests for the swarm node and relay — end-to-end packet exchange."""

from __future__ import annotations

import json
import threading
from http.server import HTTPServer

from iklem.swarm.node import Node, RelayClient
from iklem.swarm.relay import _RelayStore, make_handler


def _start_relay(store: _RelayStore) -> HTTPServer:
    server = HTTPServer(("127.0.0.1", 0), make_handler(store))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def test_node_sign_and_verify():
    node = Node(node_id="a", secret="s")
    pkt = node.sign("skill", "deploy steps")
    assert node.verify(pkt)


def test_node_rejects_foreign_secret():
    a = Node(node_id="a", secret="s1")
    b = Node(node_id="b", secret="s2")
    pkt = a.sign("skill", "deploy steps")
    assert not b.verify(pkt)


def test_relay_roundtrip():
    store = _RelayStore()
    server = _start_relay(store)
    try:
        port = server.server_address[1]
        client = RelayClient(f"http://127.0.0.1:{port}")

        node = Node(node_id="a", secret="s")
        pkt = node.sign("skill", "deploy steps")
        assert client.publish(pkt)

        packets = client.list()
        assert len(packets) == 1
        assert packets[0].content == "deploy steps"
        assert node.verify(packets[0])
    finally:
        server.shutdown()
        server.server_close()


def test_relay_list_empty_when_unreachable():
    client = RelayClient("http://127.0.0.1:1")  # nothing listening
    assert client.list() == []
