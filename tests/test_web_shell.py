"""Tests for the web and shell tools."""

from __future__ import annotations

from iklem.tools.shell import run_command
from iklem.tools.web import fetch_url


def test_fetch_url_rejects_non_http():
    assert "invalid URL" in fetch_url("not-a-url")


def test_fetch_url_unreachable_reports_error():
    result = fetch_url("http://127.0.0.1:1/nothing")
    assert result.startswith("(")


def test_run_command_returns_output():
    result = run_command("echo hello")
    assert "hello" in result
    assert "exit code 0" in result


def test_run_command_reports_failure():
    result = run_command("exit 3")
    assert "exit code 3" in result
