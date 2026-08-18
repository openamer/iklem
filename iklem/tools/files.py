"""File tools — write, search, and manage files.

These fill the gap between read_file/list_dir (read-only) and full file
management. The agent can now write files, search their contents, and
copy/move/delete — the operations a real coding agent needs.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path


def write_file(path: str, content: str) -> str:
    """Write text content to a file, creating parent directories as needed."""
    p = Path(path).expanduser()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    except OSError as e:
        return f"✗ error writing {path}: {e}"
    return f"✓ wrote {len(content)} chars to {path}"


def search_files(pattern: str, path: str = ".") -> str:
    """Search file contents for a substring (case-insensitive) under a directory."""
    p = Path(path).expanduser()
    if not p.is_dir():
        return f"✗ not a directory: {path}"
    matches = []
    try:
        for f in p.rglob("*"):
            if not f.is_file():
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if pattern.lower() in text.lower():
                matches.append(str(f))
    except OSError as e:
        return f"✗ error searching: {e}"
    if not matches:
        return "(no matches)"
    return "\n".join(matches[:50])


def copy_file(src: str, dst: str) -> str:
    """Copy a file from src to dst."""
    s = Path(src).expanduser()
    d = Path(dst).expanduser()
    if not s.exists():
        return f"✗ source not found: {src}"
    try:
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s, d)
    except OSError as e:
        return f"✗ copy failed: {e}"
    return f"✓ copied {src} -> {dst}"


def move_file(src: str, dst: str) -> str:
    """Move (rename) a file from src to dst."""
    s = Path(src).expanduser()
    d = Path(dst).expanduser()
    if not s.exists():
        return f"✗ source not found: {src}"
    try:
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(s), str(d))
    except OSError as e:
        return f"✗ move failed: {e}"
    return f"✓ moved {src} -> {dst}"


def delete_file(path: str) -> str:
    """Delete a file (or empty directory)."""
    p = Path(path).expanduser()
    if not p.exists():
        return f"✗ not found: {path}"
    try:
        if p.is_dir():
            p.rmdir()
        else:
            p.unlink()
    except OSError as e:
        return f"✗ delete failed: {e}"
    return f"✓ deleted {path}"
