"""A swarm relay — a dumb store-and-forward HTTP server with persistence.

The relay holds no secrets and does no verification; it only stores and
returns packets. Authenticity is entirely in the packet signature, so the
relay can be untrusted. Packets are persisted to disk so the relay survives
restarts, and it can bind to a public interface (0.0.0.0) to serve nodes
beyond localhost.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Lock


def _default_data_file() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("HOME") or "."
    return Path(base) / "iklem" / "relay.json"


class _RelayStore:
    """Thread-safe packet store, persisted to disk."""

    def __init__(self, data_file: Path | None = None) -> None:
        self._packets: list[dict] = []
        self._lock = Lock()
        self._data_file = data_file or _default_data_file()
        self._load()

    def _load(self) -> None:
        if self._data_file.exists():
            try:
                self._packets = json.loads(self._data_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._packets = []

    def _persist(self) -> None:
        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._data_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._packets, indent=2), encoding="utf-8")
        os.replace(tmp, self._data_file)

    def add(self, packet: dict) -> None:
        with self._lock:
            self._packets.append(packet)
            self._persist()

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


def serve(host: str = "0.0.0.0", port: int = 8765, data_file: Path | None = None) -> None:
    store = _RelayStore(data_file)
    handler = make_handler(store)
    server = HTTPServer((host, port), handler)
    print(f"✓ swarm relay listening on http://{host}:{port}")
    print(f"  packets persisted to {store._data_file}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
