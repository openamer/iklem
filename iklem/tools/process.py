"""Process tools — list and manage running processes."""

from __future__ import annotations

import subprocess


def list_processes() -> str:
    """List running processes (name + PID), most memory-heavy first."""
    if subprocess.os.name == "nt":
        cmd = ["tasklist", "/FO", "CSV", "/NH"]
    else:
        cmd = ["ps", "-eo", "pid,comm", "--sort=-rss"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "✗ could not list processes"
    lines = out.stdout.strip().splitlines()
    if not lines:
        return "(no processes)"
    return "\n".join(lines[:50])


def kill_process(pid: str) -> str:
    """Terminate a process by its PID."""
    try:
        pid_int = int(pid)
    except ValueError:
        return f"✗ invalid PID: {pid}"
    if subprocess.os.name == "nt":
        cmd = ["taskkill", "/F", "/PID", str(pid_int)]
    else:
        cmd = ["kill", "-9", str(pid_int)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "✗ could not kill process"
    if r.returncode != 0:
        return f"✗ kill failed: {r.stderr.strip() or r.stdout.strip()}"
    return f"✓ killed process {pid_int}"
