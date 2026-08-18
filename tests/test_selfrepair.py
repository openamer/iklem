"""Tests for self-inspection and self-repair."""

from __future__ import annotations

from iklem.selfextend import (
    fix_extension,
    list_extensions,
    read_extension,
    write_extension,
)

GOOD = (
    'DESCRIPTION = "Add two numbers."\n'
    "def run(a: str, b: str) -> str:\n"
    "    return str(int(a) + int(b))\n"
)

BUGGY = (
    'DESCRIPTION = "Add two numbers."\n'
    "def run(a: str, b: str) -> str:\n"
    "    return str(int(a) - int(b))  # bug: subtracts instead of adds\n"
)


def test_list_and_read_extension(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    write_extension("add", GOOD)
    exts = list_extensions()
    assert ("add", "Add two numbers.") in exts
    code = read_extension("add")
    assert "def run" in code


def test_fix_extension_rewrites(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    write_extension("add", BUGGY)
    ok, msg = fix_extension("add", GOOD)
    assert ok
    assert "fixed" in msg
    # The fixed source is now the good version (adds, not subtracts).
    code = read_extension("add")
    assert "int(a) + int(b)" in code
    assert "int(a) - int(b)" not in code


def test_fix_extension_rejects_broken_fix(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    write_extension("add", GOOD)
    ok, msg = fix_extension("add", "def run():\n    raise RuntimeError('x')\n")
    assert not ok
    assert "rejected" in msg
    # Previous version is intact.
    code = read_extension("add")
    assert "def run" in code


def test_fix_nonexistent_extension_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    ok, msg = fix_extension("ghost", GOOD)
    assert not ok
    assert "does not exist" in msg


def test_fix_invalidates_bytecode_cache(tmp_path, monkeypatch):
    """A fixed extension must be re-imported fresh, not served from .pyc."""
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    from iklem.tools.registry import tool_by_name

    write_extension("add", BUGGY)
    assert tool_by_name("add").fn("2", "3") == "-1"  # buggy behavior

    fix_extension("add", GOOD)
    assert tool_by_name("add").fn("2", "3") == "5"  # fixed behavior
