"""Tests for staged self-modification."""

from __future__ import annotations

from iklem.selfmodify import _resolve_target, self_modify


def test_resolve_target_rejects_outside_package():
    try:
        _resolve_target("../../etc/passwd")
        assert False, "should have raised"
    except ValueError as e:
        assert "outside" in str(e)


def test_resolve_target_rejects_missing():
    try:
        _resolve_target("does_not_exist.py")
        assert False, "should have raised"
    except ValueError as e:
        assert "does not exist" in str(e)


def test_self_modify_rejects_outside_package():
    result = self_modify("../../etc/passwd", "x")
    assert result.startswith("✗")


def test_self_modify_rejects_missing_file():
    result = self_modify("does_not_exist.py", "x")
    assert result.startswith("✗")
