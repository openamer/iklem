"""Tests for the code execution tool."""

from __future__ import annotations

from iklem.tools.code import run_python


def test_run_python_returns_output():
    result = run_python("print('hello')")
    assert "hello" in result
    assert "exit code 0" in result


def test_run_python_computes():
    result = run_python("print(2 + 3)")
    assert "5" in result


def test_run_python_reports_error():
    result = run_python("raise ValueError('boom')")
    assert "exit code 1" in result
