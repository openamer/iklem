"""Tests for the desktop-chat fixes: tool-calling in stream + session isolation."""

from __future__ import annotations

import json
import threading
from http.server import HTTPServer

from iklem.server import SessionManager, make_handler


def _start(manager):
    server = HTTPServer(("127.0.0.1", 0), make_handler(manager))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def test_stream_uses_agent_loop_with_tool_calling(tmp_path, monkeypatch):
    """The stream endpoint must call tools (be an agent), not just chat."""
    import urllib.request

    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    manager = SessionManager(data_file=tmp_path / "sessions.json")
    server = _start(manager)
    try:
        port = server.server_address[1]
        base = f"http://127.0.0.1:{port}"

        # Create a session.
        req = urllib.request.Request(
            f"{base}/sessions",
            data=json.dumps({"title": "t"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            sid = json.loads(r.read())["id"]

        # Ask for the current date — the agent MUST call current_date.
        req = urllib.request.Request(
            f"{base}/sessions/{sid}/stream",
            data=json.dumps({"text": "What is today's date? Answer with just the date."}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            reply = r.read().decode("utf-8")

        # The reply should contain a real date (YYYY-MM-DD), proving the agent
        # called the current_date tool rather than guessing or refusing.
        import re

        assert re.search(r"\d{4}-\d{2}-\d{2}", reply), f"no date in reply: {reply!r}"
    finally:
        server.shutdown()
        server.server_close()


def test_sessions_are_isolated(tmp_path, monkeypatch):
    """One session's messages must not leak into another session's agent."""
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    manager = SessionManager(data_file=tmp_path / "sessions.json")
    s1 = manager.create("one")
    s2 = manager.create("two")

    # Session 1 remembers "my name is Alice".
    manager.chat(s1, "My name is Alice.")

    # Session 2's agent must NOT have Alice in its history.
    agent2 = manager._ensure_agent(manager.get(s2))
    contents = " ".join(m.content for m in agent2.history)
    assert "Alice" not in contents
