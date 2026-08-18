"""Tests for the HTTP server and session manager."""

from __future__ import annotations

import json
import threading
from http.server import HTTPServer

from iklem.server import SessionManager, make_handler


def _start_server(manager):
    server = HTTPServer(("127.0.0.1", 0), make_handler(manager))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def _manager(tmp_path):
    return SessionManager(data_file=tmp_path / "sessions.json")


def test_session_create_and_list(tmp_path):
    manager = _manager(tmp_path)
    sid = manager.create("Test")
    sessions = manager.list()
    assert len(sessions) == 1
    assert sessions[0]["id"] == sid
    assert sessions[0]["title"] == "Test"


def test_session_chat_unknown_session(tmp_path):
    manager = _manager(tmp_path)
    result = manager.chat("nonexistent", "hello")
    assert "error" in result


def test_session_persists_across_restart(tmp_path):
    manager = _manager(tmp_path)
    sid = manager.create("Persisted")
    # A fresh manager reading the same file should see the session.
    manager2 = _manager(tmp_path)
    sessions = manager2.list()
    assert len(sessions) == 1
    assert sessions[0]["id"] == sid
    assert sessions[0]["title"] == "Persisted"


def test_health_endpoint(tmp_path):
    manager = _manager(tmp_path)
    server = _start_server(manager)
    try:
        import urllib.request

        port = server.server_address[1]
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=10) as r:
            data = json.loads(r.read())
        assert data["ok"] is True
    finally:
        server.shutdown()
        server.server_close()


def test_sessions_endpoint_roundtrip(tmp_path):
    manager = _manager(tmp_path)
    server = _start_server(manager)
    try:
        import urllib.request

        port = server.server_address[1]
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/sessions",
            data=json.dumps({"title": "My session"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            created = json.loads(r.read())
        assert "id" in created

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/sessions", timeout=10) as r:
            sessions = json.loads(r.read())
        assert len(sessions) == 1
        assert sessions[0]["title"] == "My session"
    finally:
        server.shutdown()
        server.server_close()
