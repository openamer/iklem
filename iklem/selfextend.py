"""Safe self-extension — the agent can write its own tools, with guardrails.

This is the "provably improves with use" axis made real at the code level:
the agent can create a new tool by writing a Python file into a sandbox
directory (never the core), and the tool is verified before it becomes
available. A broken extension is rolled back automatically, so the agent
cannot break itself.

Convention: an extension file defines a `run(...)` function (its parameters
become the tool's parameters) and a module-level `DESCRIPTION` string.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


def _extensions_dir() -> Path:
    base = os.environ.get("IKLEM_HOME") or os.environ.get("LOCALAPPDATA") or os.environ.get("HOME") or "."
    return Path(base) / "iklem" / "self_extensions"


def write_extension(name: str, code: str) -> tuple[bool, str]:
    """Write a new tool extension, verify it, and roll back on failure.

    Returns (ok, message). The extension is only kept if it imports cleanly
    and exposes a callable `run` plus a `DESCRIPTION` string.
    """
    if not name or not name.replace("_", "").isalnum():
        return (False, f"invalid tool name: {name!r}")

    directory = _extensions_dir()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.py"

    # Write to a temp file first, then verify, then atomically move.
    tmp = directory / f".{name}.tmp.py"
    tmp.write_text(code, encoding="utf-8")

    ok, message, _ = _verify(tmp, name)
    if not ok:
        tmp.unlink(missing_ok=True)
        return (False, message)

    # Atomic promote: only a verified extension becomes live.
    os.replace(tmp, path)
    return (True, f"tool '{name}' added and verified")


def _verify(path: Path, name: str) -> tuple[bool, str, object | None]:
    """Import a candidate extension and check it has the right shape.

    Returns (ok, description, run_fn). The run function is returned directly
    (not via sys.modules) so concurrent callers never see a stale module.
    """
    module_name = f"iklem_selfext_{name}"
    # Invalidate any cached module AND its bytecode cache, so a fixed
    # extension is re-imported fresh (otherwise the old .pyc wins).
    sys.modules.pop(module_name, None)
    pycache = path.parent / "__pycache__"
    if pycache.is_dir():
        for stale in pycache.glob(f"{name}.*.pyc"):
            stale.unlink(missing_ok=True)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return (False, "could not load module", None)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as e:  # noqa: BLE001 — a broken extension must not crash
        return (False, f"import failed: {e}", None)

    run = getattr(module, "run", None)
    if not callable(run):
        return (False, "extension must define a callable run(...)", None)
    description = getattr(module, "DESCRIPTION", "")
    if not isinstance(description, str) or not description:
        return (False, "extension must define a DESCRIPTION string", None)
    return (True, description, run)


def load_extensions() -> list[tuple[str, str, object]]:
    """Load all verified extensions as (name, description, fn) triples."""
    directory = _extensions_dir()
    if not directory.is_dir():
        return []
    loaded = []
    for path in sorted(directory.glob("*.py")):
        if path.name.startswith("."):
            continue
        name = path.stem
        ok, description, run = _verify(path, name)
        if ok and run is not None:
            loaded.append((name, description, run))
    return loaded


def list_extensions() -> list[tuple[str, str]]:
    """List all extension files as (name, description) — including broken ones."""
    directory = _extensions_dir()
    if not directory.is_dir():
        return []
    result = []
    for path in sorted(directory.glob("*.py")):
        if path.name.startswith("."):
            continue
        name = path.stem
        ok, description, _ = _verify(path, name)
        result.append((name, description if ok else f"(broken: {description})"))
    return result


def read_extension(name: str) -> str | None:
    """Return the source code of an extension, or None if it does not exist."""
    if not name or not name.replace("_", "").isalnum():
        return None
    path = _extensions_dir() / f"{name}.py"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def fix_extension(name: str, code: str) -> tuple[bool, str]:
    """Rewrite an existing extension, verify it, and roll back on failure.

    This is how the agent fixes a bug in a tool it created: it reads the
    source, rewrites it, and the new version is only promoted if it verifies.
    A broken fix is rolled back, leaving the previous version intact.
    """
    if not name or not name.replace("_", "").isalnum():
        return (False, f"invalid tool name: {name!r}")

    directory = _extensions_dir()
    path = directory / f"{name}.py"
    if not path.exists():
        return (False, f"tool '{name}' does not exist")

    # Write the candidate to a temp file and verify before promoting.
    tmp = directory / f".{name}.tmp.py"
    tmp.write_text(code, encoding="utf-8")
    ok, message, _ = _verify(tmp, name)
    if not ok:
        tmp.unlink(missing_ok=True)
        return (False, f"fix rejected (previous version kept): {message}")

    os.replace(tmp, path)
    return (True, f"tool '{name}' fixed and verified")
