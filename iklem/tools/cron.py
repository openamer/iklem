"""Cron tools — the agent schedules and manages its own recurring tasks."""

from __future__ import annotations

from iklem.cron import list_jobs, remove_job, schedule_job


def cron_schedule(name: str, command: str, interval_seconds: str) -> str:
    """Schedule a command to run every N seconds."""
    return schedule_job(name, command, interval_seconds)


def cron_list() -> str:
    """List all scheduled jobs."""
    return list_jobs()


def cron_remove(name: str) -> str:
    """Remove a scheduled job."""
    return remove_job(name)
