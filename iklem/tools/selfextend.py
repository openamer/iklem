"""The self_extend tool — lets the agent create its own tools safely.

This is the tool the agent calls to extend itself. It writes a new tool into
the sandbox, verifies it, and rolls back on failure. The agent can therefore
grow its own capabilities without ever touching the core.
"""

from __future__ import annotations

from iklem.selfextend import write_extension


def self_extend(name: str, code: str) -> str:
    """Create a new tool from Python code (sandboxed + verified).

    `code` must define a `run(...)` function and a `DESCRIPTION` string.
    Returns a confirmation or an honest error.
    """
    ok, message = write_extension(name, code)
    if ok:
        return f"✓ {message}"
    return f"✗ {message}"
