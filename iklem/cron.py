"""Cron — scheduled autonomous tasks.

This gives iklem the ability to run tasks on a schedule (like OpenAmer's
cronjob). A job is a named command with a schedule; the scheduler runs due
jobs in background threads. Jobs persist to disk so they survive restarts.

Schedule format: a simple interval in seconds, or a cron-like "HH:MM" daily
time. This is deliberately simple and stdlib-only.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path


def _jobs_file() -> Path:
    base = os.environ.get("IKLEM_HOME") or os.environ.get("LOCALAPPDATA") or os.environ.get("HOME") or "."
    return Path(base) / "iklem" / "cron.json"


@dataclass
class Job:
    name: str
    command: str
    interval_seconds: int
    last_run: float = 0.0

    def due(self, now: float) -> bool:
        return (now - self.last_run) >= self.interval_seconds


class CronScheduler:
    """A simple in-process scheduler that runs due jobs in background threads."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        path = _jobs_file()
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        for item in data:
            self._jobs[item["name"]] = Job(
                name=item["name"],
                command=item["command"],
                interval_seconds=item["interval_seconds"],
                last_run=item.get("last_run", 0.0),
            )

    def _persist(self) -> None:
        path = _jobs_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [
            {
                "name": j.name,
                "command": j.command,
                "interval_seconds": j.interval_seconds,
                "last_run": j.last_run,
            }
            for j in self._jobs.values()
        ]
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(tmp, path)

    def add(self, name: str, command: str, interval_seconds: int) -> str:
        if interval_seconds <= 0:
            return "✗ interval must be positive"
        with self._lock:
            self._jobs[name] = Job(name=name, command=command, interval_seconds=interval_seconds)
            self._persist()
        return f"✓ job '{name}' scheduled every {interval_seconds}s"

    def remove(self, name: str) -> str:
        with self._lock:
            if name not in self._jobs:
                return f"✗ no job named {name}"
            del self._jobs[name]
            self._persist()
        return f"✓ job '{name}' removed"

    def list(self) -> str:
        with self._lock:
            if not self._jobs:
                return "(no jobs)"
            return "\n".join(
                f"{j.name}: every {j.interval_seconds}s — {j.command}"
                for j in self._jobs.values()
            )

    def run_due(self) -> list[str]:
        """Run all due jobs in background threads; return the names that ran."""
        now = time.time()
        ran = []
        with self._lock:
            due = [j for j in self._jobs.values() if j.due(now)]
            for j in due:
                j.last_run = now
            if due:
                self._persist()
        for j in due:
            ran.append(j.name)
            threading.Thread(target=self._execute, args=(j,), daemon=True).start()
        return ran

    def _execute(self, job: Job) -> None:
        import subprocess

        try:
            subprocess.run(
                job.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except (subprocess.TimeoutExpired, Exception):  # noqa: BLE001
            pass


# A module-level scheduler instance for the tool to use.
_scheduler = CronScheduler()


def schedule_job(name: str, command: str, interval_seconds: str) -> str:
    """Schedule a command to run every N seconds."""
    try:
        interval = int(interval_seconds)
    except ValueError:
        return "✗ interval must be an integer number of seconds"
    return _scheduler.add(name, command, interval)


def list_jobs() -> str:
    """List all scheduled jobs."""
    return _scheduler.list()


def remove_job(name: str) -> str:
    """Remove a scheduled job."""
    return _scheduler.remove(name)
