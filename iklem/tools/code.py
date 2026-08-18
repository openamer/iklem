"""Code execution tool — run Python snippets safely.

This lets the agent actually execute code and return the result, rather than
just describing what code would do. It runs in a subprocess with a timeout
and output cap, so a runaway snippet cannot hang the agent.
"""

from __future__ import annotations

import subprocess
import sys


def run_python(code: str) -> str:
    """Execute a Python snippet and return its stdout+stderr (truncated).

    Runs with a 15s timeout. Returns the combined output and exit code.
    """
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return "(code timed out after 15s)"
    except Exception as e:  # noqa: BLE001
        return f"(code error: {e})"

    out = proc.stdout or ""
    err = proc.stderr or ""
    combined = out
    if err:
        combined += ("\n" if combined else "") + err
    if len(combined) > 4000:
        combined = combined[:4000] + "\n…(truncated)"
    if not combined:
        combined = f"(exit code {proc.returncode}, no output)"
    else:
        combined += f"\n(exit code {proc.returncode})"
    return combined
