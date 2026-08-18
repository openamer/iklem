"""A minimal swarm relay — a dumb store-and-forward HTTP server.

The relay holds no secrets and does no verification; it only stores and
returns packets. Authenticity is entirely in the packet signature, so the
relay can be untrusted. This is a stdlib-only server (http.server) so it runs
anywhere with no dependencies.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Lock


class _RelayStore:
    """Thread-safe in-memory packet store."""

    def __init__(self) -> None:
        self._packets: list[dict] = []
        self._lock = Lock()

    def add(self, packet: dict) -> None:
        with self._lock:
            self._packets.append(packet)

    def all(self) -> list[dict]:
        with self._lock:
            return list(self._packets)


def make_handler(store: _RelayStore) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            if self.path != "/packets":
                self.send_error(404)
                return
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                packet = json.loads(body.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.send_error(400, "invalid JSON")
                return
            store.add(packet)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok": true}')

        def do_GET(self) -> None:
            if self.path != "/packets":
                self.send_error(404)
                return
            body = json.dumps(store.all()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args) -> None:
            # Silence default request logging.
            pass

    return Handler


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    store = _RelayStore()
    handler = make_handler(store)
    server = HTTPServer((host, port), handler)
    print(f"✓ swarm relay listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
