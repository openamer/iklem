"""The iklem HTTP server — exposes the agent as a JSON API.

This is the backend for the desktop app (and any other client). It is
stdlib-only (http.server) so it runs anywhere with no dependencies. Endpoints:

  GET  /health            -> {"ok": true, "version": ...}
  GET  /sessions          -> list of sessions
  POST /sessions          -> create a session
  GET  /sessions/<id>     -> messages in a session
  POST /sessions/<id>/chat -> send a message, get the agent's reply
  GET  /config            -> current config (redacted)
  POST /config            -> update config
"""

from __future__ import annotations

import json
import os
import threading
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from iklem.core.agent import Agent
from iklem.providers.base import Message


def _default_sessions_file() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("HOME") or "."
    return Path(base) / "iklem" / "sessions.json"


class SessionManager:
    """Holds multiple named conversations, each with its own agent.

    Sessions are persisted to disk (title + messages) so they survive a
    server restart. Agent objects are recreated lazily on first use.
    """

    def __init__(self, data_file: Path | None = None) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._data_file = data_file or _default_sessions_file()
        self._load()

    def _load(self) -> None:
        if not self._data_file.exists():
            return
        try:
            data = json.loads(self._data_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        for item in data:
            sid = item.get("id")
            if not sid:
                continue
            self._sessions[sid] = {
                "id": sid,
                "title": item.get("title", "New session"),
                "agent": None,  # recreated lazily
                "messages": item.get("messages", []),
            }

    def _persist(self) -> None:
        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        data = [
            {
                "id": s["id"],
                "title": s["title"],
                "messages": s["messages"],
            }
            for s in self._sessions.values()
        ]
        tmp = self._data_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(tmp, self._data_file)

    def _ensure_agent(self, session: dict[str, Any]) -> Agent:
        if session["agent"] is None:
            session["agent"] = _make_agent()
        return session["agent"]

    def create(self, title: str = "New session") -> str:
        sid = uuid.uuid4().hex[:12]
        with self._lock:
            self._sessions[sid] = {
                "id": sid,
                "title": title,
                "agent": _make_agent(),
                "messages": [],
            }
            self._persist()
        return sid

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            return [
                {"id": s["id"], "title": s["title"], "count": len(s["messages"])}
                for s in self._sessions.values()
            ]

    def get(self, sid: str) -> dict[str, Any] | None:
        with self._lock:
            return self._sessions.get(sid)

    def rename(self, sid: str, title: str) -> bool:
        session = self.get(sid)
        if session is None:
            return False
        with self._lock:
            session["title"] = title
            self._persist()
        return True

    def delete(self, sid: str) -> bool:
        with self._lock:
            if sid not in self._sessions:
                return False
            del self._sessions[sid]
            self._persist()
            return True

    def chat(self, sid: str, text: str) -> dict[str, Any]:
        session = self.get(sid)
        if session is None:
            return {"error": "session not found"}
        agent: Agent = self._ensure_agent(session)
        result = agent.respond(text)
        if not result.ok:
            return {"error": result.error}
        with self._lock:
            session["messages"].append({"role": "user", "content": text})
            session["messages"].append({"role": "assistant", "content": result.content})
            self._persist()
        return {"reply": result.content}

    def stream_chat(self, sid: str, text: str):
        """Yield reply chunks for a streaming response (no tool-calling)."""
        session = self.get(sid)
        if session is None:
            yield "(error: session not found)"
            return
        agent: Agent = self._ensure_agent(session)
        provider = agent.provider
        if not hasattr(provider, "stream"):
            # Fall back to a single non-streamed reply.
            result = agent.respond(text)
            yield result.content if result.ok else f"(error: {result.error})"
            return
        messages = [Message(role="system", content=agent.system_prompt)]
        messages.extend(agent.history)
        messages.append(Message(role="user", content=text))
        full = []
        for chunk in provider.stream(messages):
            full.append(chunk)
            yield chunk
        reply = "".join(full)
        with self._lock:
            session["messages"].append({"role": "user", "content": text})
            session["messages"].append({"role": "assistant", "content": reply})
            self._persist()


def _make_agent() -> Agent:
    from iklem.providers.ollama import OllamaProvider

    return Agent(provider=OllamaProvider())


def _read_config() -> dict[str, str]:
    """Return the current config, redacting secrets."""
    keys = [
        "IKLEM_OLLAMA_MODEL",
        "IKLEM_OLLAMA_URL",
        "IKLEM_NODE_ID",
        "IKLEM_RELAY_URL",
    ]
    config = {}
    for k in keys:
        v = os.environ.get(k)
        if v:
            config[k] = v
    # Redact any token-like values.
    for k in list(config):
        if "TOKEN" in k or "SECRET" in k or "KEY" in k:
            config[k] = "•••"
    return config


def make_handler(manager: SessionManager) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def _json(self, obj: Any, status: int = 200) -> None:
            body = json.dumps(obj).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

        def _read_body(self) -> dict:
            length = int(self.headers.get("Content-Length", 0))
            if length == 0:
                return {}
            return json.loads(self.rfile.read(length).decode("utf-8"))

        def do_OPTIONS(self) -> None:
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_GET(self) -> None:
            if self.path == "/health":
                self._json({"ok": True, "version": "0.1.0"})
            elif self.path == "/sessions":
                self._json(manager.list())
            elif self.path == "/config":
                self._json(_read_config())
            elif self.path.startswith("/sessions/"):
                sid = self.path.split("/")[2]
                session = manager.get(sid)
                if session is None:
                    self._json({"error": "session not found"}, 404)
                else:
                    self._json(session["messages"])
            else:
                self._json({"error": "not found"}, 404)

        def do_POST(self) -> None:
            if self.path == "/sessions":
                body = self._read_body()
                sid = manager.create(title=body.get("title", "New session"))
                self._json({"id": sid})
            elif self.path.endswith("/stream"):
                parts = self.path.split("/")
                sid = parts[2]
                body = self._read_body()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                for chunk in manager.stream_chat(sid, body.get("text", "")):
                    self.wfile.write(chunk.encode("utf-8"))
                    self.wfile.flush()
            elif self.path.endswith("/chat"):
                parts = self.path.split("/")
                sid = parts[2]
                body = self._read_body()
                result = manager.chat(sid, body.get("text", ""))
                if "error" in result:
                    self._json(result, 404)
                else:
                    self._json(result)
            else:
                self._json({"error": "not found"}, 404)

        def do_PATCH(self) -> None:
            # PATCH /sessions/<id>  -> rename
            parts = self.path.split("/")
            if len(parts) == 3 and parts[1] == "sessions":
                sid = parts[2]
                body = self._read_body()
                if manager.rename(sid, body.get("title", "")):
                    self._json({"ok": True})
                else:
                    self._json({"error": "session not found"}, 404)
            else:
                self._json({"error": "not found"}, 404)

        def do_DELETE(self) -> None:
            # DELETE /sessions/<id>  -> delete
            parts = self.path.split("/")
            if len(parts) == 3 and parts[1] == "sessions":
                sid = parts[2]
                if manager.delete(sid):
                    self._json({"ok": True})
                else:
                    self._json({"error": "session not found"}, 404)
            else:
                self._json({"error": "not found"}, 404)

        def log_message(self, *args) -> None:
            pass

    return Handler


def serve(host: str = "127.0.0.1", port: int = 8787) -> None:
    manager = SessionManager()
    server = HTTPServer((host, port), make_handler(manager))
    print(f"✓ iklem server listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
