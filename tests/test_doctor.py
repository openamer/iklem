"""Tests for the doctor command."""

from __future__ import annotations

from iklem.doctor import run_doctor


def test_doctor_returns_checks():
    checks = run_doctor()
    names = [c[0] for c in checks]
    assert "python" in names
    assert "iklem import" in names
    assert "data dir" in names


def test_doctor_python_is_ok():
    checks = run_doctor()
    python_check = next(c for c in checks if c[0] == "python")
    assert python_check[1] is True
