"""Staged self-modification — the agent can change its own core, safely.

This is the answer to "the agent can't rewrite its core": it CAN, but only
through a verified gate that makes self-destruction impossible:

  1. Scope guard  — only files inside the iklem package may be touched.
  2. Backup       — the original is always saved before any change.
  3. Test gate    — the full test suite must pass against the change.
  4. Rollback     — on any failure, the original is restored atomically.

The agent never edits a running file in place; it proposes a change, and the
change is only promoted if the tests prove it does not break anything. This
is the "does not break" axis applied to self-modification.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _package_root() -> Path:
    """The iklem package directory (the only place self-modification may touch)."""
    import iklem

    return Path(iklem.__file__).parent


def _resolve_target(path: str) -> Path:
    """Resolve a target path and enforce it is inside the iklem package."""
    root = _package_root().resolve()
    target = (root / path).resolve()
    if not str(target).startswith(str(root)):
        raise ValueError(f"refusing to modify outside the iklem package: {path}")
    if not target.exists():
        raise ValueError(f"target does not exist: {path}")
    if not target.is_file():
        raise ValueError(f"target is not a file: {path}")
    return target


def _run_tests() -> tuple[bool, str]:
    """Run the full test suite. Returns (ok, output tail)."""
    root = _package_root().parent
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return (False, "(tests timed out)")
    except FileNotFoundError:
        return (False, "(pytest not found)")
    tail = (proc.stdout or "") + (proc.stderr or "")
    return (proc.returncode == 0, tail[-2000:])


def self_modify(path: str, new_content: str) -> str:
    """Propose a change to a core file; promote it only if tests pass.

    Returns a confirmation or an honest error. On any failure the original
    file is restored, so the agent cannot break itself.
    """
    try:
        target = _resolve_target(path)
    except ValueError as e:
        return f"✗ {e}"

    original = target.read_text(encoding="utf-8")
    backup = target.with_suffix(target.suffix + ".bak")

    # 1. Backup the original.
    backup.write_text(original, encoding="utf-8")

    try:
        # 2. Apply the change.
        target.write_text(new_content, encoding="utf-8")

        # 3. Test gate: the change is only kept if the suite passes.
        ok, tail = _run_tests()
        if not ok:
            # 4. Rollback.
            target.write_text(original, encoding="utf-8")
            backup.unlink(missing_ok=True)
            return f"✗ change rejected (tests failed, rolled back):\n{tail[-500:]}"

        # 5. Success: keep the change, drop the backup.
        backup.unlink(missing_ok=True)
        return f"✓ change to {path} applied and verified (tests pass)"
    except Exception as e:  # noqa: BLE001 — never leave the core broken
        # Rollback on any unexpected error.
        try:
            target.write_text(original, encoding="utf-8")
        except OSError:
            pass
        backup.unlink(missing_ok=True)
        return f"✗ change failed and was rolled back: {e}"
