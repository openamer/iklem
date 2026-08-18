"""Shell tool — let the agent run a command and read its output.

This is the most powerful (and most dangerous) tool: it executes a shell
command. It is deliberately conservative: a short timeout, a small output
cap, and it never runs interactively. The agent should use it for read-only
inspection, not destructive actions.
"""

from __future__ import annotations

import subprocess


def run_command(command: str) -> str:
    """Run a shell command and return its stdout+stderr (truncated to 4000 chars).

    Runs with a 30s timeout. Returns the combined output and exit code.
    """
    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return "(command timed out after 30s)"
    except Exception as e:  # noqa: BLE001
        return f"(command error: {e})"

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
