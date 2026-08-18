"""iklem doctor — diagnose the health of an iklem install.

This is the "does not break" axis made concrete: a single command that checks
every dependency and reports exactly what is wrong, with real evidence, so a
broken install can be fixed instead of guessed at.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


def _check(name: str, ok: bool, detail: str) -> tuple[str, bool, str]:
    return (name, ok, detail)


def run_doctor() -> list[tuple[str, bool, str]]:
    """Run all health checks and return (name, ok, detail) triples."""
    checks: list[tuple[str, bool, str]] = []

    # Python
    checks.append(_check("python", True, f"{platform.python_version()} ({sys.executable})"))

    # iklem importable
    try:
        import iklem  # noqa: F401

        checks.append(_check("iklem import", True, f"version {iklem.__version__}"))
    except Exception as e:  # noqa: BLE001
        checks.append(_check("iklem import", False, str(e)))

    # Ollama reachable
    ollama_url = os.environ.get("IKLEM_OLLAMA_URL", "http://localhost:11434")
    try:
        req = urllib.request.Request(f"{ollama_url}/api/version", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        checks.append(_check("ollama", True, f"version {data.get('version', '?')}"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        checks.append(_check("ollama", False, f"{ollama_url} unreachable: {e}"))

    # Data directory writable
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("HOME") or "."
    data_dir = Path(base) / "iklem"
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        probe = data_dir / ".write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        checks.append(_check("data dir", True, str(data_dir)))
    except OSError as e:
        checks.append(_check("data dir", False, str(e)))

    # signal-cli (optional)
    try:
        subprocess.run(["signal-cli", "--version"], capture_output=True, timeout=5)
        checks.append(_check("signal-cli", True, "installed"))
    except (FileNotFoundError, subprocess.TimeoutExpired):
        checks.append(_check("signal-cli (optional)", True, "not installed — Signal channel disabled"))

    return checks


def main() -> int:
    checks = run_doctor()
    all_ok = True
    for name, ok, detail in checks:
        mark = "✓" if ok else "✗"
        if not ok:
            all_ok = False
        print(f"  {mark} {name}: {detail}")
    print()
    if all_ok:
        print("✓ iklem is healthy")
        return 0
    print("✗ some checks failed — fix the items above")
    return 1
