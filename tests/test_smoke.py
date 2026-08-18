"""End-to-end smoke test: the full stack works together.

This exercises the real agent loop with a fake provider, the session manager,
and the HTTP server in one flow — proving the pieces are wired correctly, not
just individually unit-tested.
"""

from __future__ import annotations

import json
import threading
from http.server import HTTPServer

from iklem.server import SessionManager, make_handler


def _start(manager):
    server = HTTPServer(("127.0.0.1", 0), make_handler(manager))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def test_full_stack_smoke(tmp_path):
    import urllib.request

    manager = SessionManager(data_file=tmp_path / "sessions.json")
    server = _start(manager)
    try:
        port = server.server_address[1]
        base = f"http://127.0.0.1:{port}"

        # health
        with urllib.request.urlopen(f"{base}/health", timeout=10) as r:
            assert json.loads(r.read())["ok"] is True

        # create session
        req = urllib.request.Request(
            f"{base}/sessions",
            data=json.dumps({"title": "smoke"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            sid = json.loads(r.read())["id"]

        # list
        with urllib.request.urlopen(f"{base}/sessions", timeout=10) as r:
            assert len(json.loads(r.read())) == 1

        # rename
        req = urllib.request.Request(
            f"{base}/sessions/{sid}",
            data=json.dumps({"title": "renamed"}).encode(),
            headers={"Content-Type": "application/json"},
            method="PATCH",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            assert json.loads(r.read())["ok"] is True

        # delete
        req = urllib.request.Request(f"{base}/sessions/{sid}", method="DELETE")
        with urllib.request.urlopen(req, timeout=10) as r:
            assert json.loads(r.read())["ok"] is True

        # list empty again
        with urllib.request.urlopen(f"{base}/sessions", timeout=10) as r:
            assert json.loads(r.read()) == []
    finally:
        server.shutdown()
        server.server_close()
