"""Git tools — the agent can commit and push its own changes, safely.

This lets iklem push its own improvements to GitHub. Safety boundaries:
  - It only operates inside the iklem repo (never an arbitrary directory).
  - The token is read from IKLEM_GITHUB_TOKEN (never hardcoded in code).
  - Every operation reports real git output, never a fabricated result.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def _repo_root() -> Path:
    """The iklem repository root (where .git lives)."""
    import iklem

    return Path(iklem.__file__).parent.parent


def _run(args: list[str], timeout: int = 60) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=_repo_root(),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return (1, "(git timed out)")
    except FileNotFoundError:
        return (1, "(git not found)")
    out = (proc.stdout or "") + (proc.stderr or "")
    return (proc.returncode, out.strip())


def git_status() -> str:
    """Return the git status of the iklem repo."""
    code, out = _run(["status", "--short"])
    return out if out else "(clean working tree)"


def git_diff() -> str:
    """Return the uncommitted diff of the iklem repo (truncated)."""
    code, out = _run(["diff", "--stat"])
    if not out:
        return "(no changes)"
    return out[:2000]


def git_commit(message: str) -> str:
    """Commit all changes with the given message."""
    if not message.strip():
        return "✗ commit message must be non-empty"
    code, out = _run(["add", "-A"])
    if code != 0:
        return f"✗ git add failed: {out}"
    code, out = _run(["commit", "-m", message])
    if code != 0:
        return f"✗ commit failed: {out}"
    return f"✓ committed: {out.splitlines()[0] if out else message}"


def git_push() -> str:
    """Push committed changes to the remote, using IKLEM_GITHUB_TOKEN if set."""
    token = os.environ.get("IKLEM_GITHUB_TOKEN", "")
    if token:
        # Push via a token-authenticated URL (never persisted in the repo).
        code, out = _run(["remote", "get-url", "origin"])
        url = out.strip()
        if url.startswith("https://"):
            auth_url = url.replace("https://", f"https://{token}@", 1)
            code, out = _run(["push", auth_url, "HEAD"])
        else:
            code, out = _run(["push"])
    else:
        code, out = _run(["push"])
    if code != 0:
        return f"✗ push failed: {out}"
    return f"✓ pushed: {out}"
