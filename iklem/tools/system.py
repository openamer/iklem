"""Real tools the agent can call to learn the truth instead of guessing.

These are the tools that make iklem an agent rather than a chatbot: they
reach into the real world (time, date, filesystem, system) and return facts.
"""

from __future__ import annotations

import datetime
import os
import platform
from pathlib import Path


def current_time() -> str:
    """Return the current local time (HH:MM:SS)."""
    return datetime.datetime.now().strftime("%H:%M:%S")


def current_date() -> str:
    """Return today's date (ISO format, e.g. 2026-08-18)."""
    return datetime.date.today().isoformat()


def current_datetime() -> str:
    """Return the full current date and time."""
    return datetime.datetime.now().isoformat(timespec="seconds")


def system_info() -> str:
    """Return basic system information (OS, machine, Python)."""
    return (
        f"OS: {platform.system()} {platform.release()}; "
        f"machine: {platform.machine()}; "
        f"python: {platform.python_version()}"
    )


def read_file(path: str) -> str:
    """Read a text file and return its contents (truncated to 4000 chars)."""
    p = Path(path).expanduser()
    if not p.exists():
        return f"(file not found: {path})"
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return f"(error reading {path}: {e})"
    if len(text) > 4000:
        text = text[:4000] + "\n…(truncated)"
    return text


def list_dir(path: str = ".") -> str:
    """List the entries in a directory."""
    p = Path(path).expanduser()
    if not p.is_dir():
        return f"(not a directory: {path})"
    try:
        entries = sorted(os.listdir(p))
    except OSError as e:
        return f"(error listing {path}: {e})"
    return "\n".join(entries) if entries else "(empty directory)"
