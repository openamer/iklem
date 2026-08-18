"""Self-inspection and self-repair tools — the agent reads and fixes its own tools.

This closes the last gap: the agent can list its self-created tools, read
their source, find bugs, and rewrite them — with the same verify + rollback
guardrails as creation. It can only touch the sandbox, never the core.
"""

from __future__ import annotations

from iklem.selfextend import (
    fix_extension,
    list_extensions,
    read_extension,
    write_extension,
)


def self_extend(name: str, code: str) -> str:
    """Create a new tool from Python code (sandboxed + verified)."""
    ok, message = write_extension(name, code)
    return f"✓ {message}" if ok else f"✗ {message}"


def list_my_tools() -> str:
    """List the tools I created myself (name + description)."""
    exts = list_extensions()
    if not exts:
        return "(no self-created tools)"
    return "\n".join(f"{name}: {desc}" for name, desc in exts)


def read_my_tool(name: str) -> str:
    """Return the source code of one of my self-created tools."""
    code = read_extension(name)
    return code if code is not None else f"(no tool named {name})"


def fix_my_tool(name: str, code: str) -> str:
    """Rewrite one of my self-created tools to fix a bug (verified + rollback)."""
    ok, message = fix_extension(name, code)
    return f"✓ {message}" if ok else f"✗ {message}"
