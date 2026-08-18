"""Tests for the swarm relay persistence."""

from __future__ import annotations

from iklem.swarm.relay import _RelayStore


def test_relay_persists_to_disk(tmp_path):
    data_file = tmp_path / "relay.json"
    store = _RelayStore(data_file=data_file)
    store.add({"node_id": "a", "kind": "skill", "content": "x"})

    # A fresh store reading the same file should see the packet.
    store2 = _RelayStore(data_file=data_file)
    assert len(store2.all()) == 1
    assert store2.all()[0]["node_id"] == "a"


def test_relay_survives_corrupt_file(tmp_path):
    data_file = tmp_path / "relay.json"
    data_file.write_text("{not valid json", encoding="utf-8")
    store = _RelayStore(data_file=data_file)
    assert store.all() == []
