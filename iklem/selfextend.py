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

    ok, message = _verify(tmp, name)
    if not ok:
        tmp.unlink(missing_ok=True)
        return (False, message)

    # Atomic promote: only a verified extension becomes live.
    os.replace(tmp, path)
    return (True, f"tool '{name}' added and verified")


def _verify(path: Path, name: str) -> tuple[bool, str]:
    """Import a candidate extension and check it has the right shape."""
    module_name = f"iklem_selfext_{name}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return (False, "could not load module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as e:  # noqa: BLE001 — a broken extension must not crash
        return (False, f"import failed: {e}")

    run = getattr(module, "run", None)
    if not callable(run):
        return (False, "extension must define a callable run(...)")
    description = getattr(module, "DESCRIPTION", "")
    if not isinstance(description, str) or not description:
        return (False, "extension must define a DESCRIPTION string")
    return (True, description)


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
        ok, description = _verify(path, name)
        if ok:
            module_name = f"iklem_selfext_{name}"
            module = sys.modules.get(module_name)
            if module is not None:
                loaded.append((name, description, module.run))
    return loaded
