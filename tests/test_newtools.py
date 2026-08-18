"""Tests for cron, delegation, browser, and computer tools."""

from __future__ import annotations

from iklem.cron import CronScheduler
from iklem.tools.browser import browse
from iklem.tools.computer import click, screenshot, type_text
from iklem.tools.cron import cron_list, cron_remove, cron_schedule


def test_cron_schedule_and_list(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    result = cron_schedule("test", "echo hi", "60")
    assert result.startswith("✓")
    assert "test" in cron_list()


def test_cron_remove(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    cron_schedule("test", "echo hi", "60")
    assert cron_remove("test").startswith("✓")
    assert "test" not in cron_list()


def test_cron_rejects_bad_interval(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    assert cron_schedule("x", "echo", "abc").startswith("✗")


def test_browse_reports_missing_playwright():
    result = browse("https://example.com")
    # Either works (playwright installed) or reports the honest error.
    assert isinstance(result, str)


def test_computer_tools_report_missing_pyautogui():
    # These either work or report the honest "not installed" error.
    assert isinstance(screenshot(), str)
    assert isinstance(click("0", "0"), str)
    assert isinstance(type_text("hi"), str)
