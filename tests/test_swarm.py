"""Tests for the swarm packet — signing, verification, and leak-free checks."""

from __future__ import annotations

from iklem.swarm.packet import KnowledgePacket, is_leak_free


def test_packet_sign_and_verify():
    p = KnowledgePacket(node_id="node-a", kind="skill", content="deploy steps")
    p.sign("shared-secret")
    assert p.signature
    assert p.verify("shared-secret")


def test_packet_tamper_breaks_verification():
    p = KnowledgePacket(node_id="node-a", kind="skill", content="deploy steps")
    p.sign("shared-secret")
    p.content = "deploy steps (tampered)"
    assert not p.verify("shared-secret")


def test_packet_wrong_secret_fails():
    p = KnowledgePacket(node_id="node-a", kind="skill", content="deploy steps")
    p.sign("secret-1")
    assert not p.verify("secret-2")


def test_unsigned_packet_fails_verification():
    p = KnowledgePacket(node_id="node-a", kind="skill", content="deploy steps")
    assert not p.verify("shared-secret")


def test_leak_free_detects_secrets():
    assert not is_leak_free("my api_key is abc123")
    assert not is_leak_free("token: ghp_xxxx")
    assert is_leak_free("deploy the app with these steps")
