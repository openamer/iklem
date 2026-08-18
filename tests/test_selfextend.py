"""Tests for safe self-extension."""

from __future__ import annotations

from iklem.selfextend import load_extensions, write_extension
from iklem.tools.registry import all_tools, tool_by_name


GOOD = (
    'DESCRIPTION = "Add two numbers."\n'
    "def run(a: str, b: str) -> str:\n"
    "    return str(int(a) + int(b))\n"
)

BROKEN = "def run():\n    raise RuntimeError('boom')\n"

NO_RUN = "DESCRIPTION = 'no run function'\n"


def test_write_valid_extension(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    ok, msg = write_extension("add", GOOD)
    assert ok
    assert "verified" in msg


def test_write_broken_extension_rolls_back(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    ok, msg = write_extension("broken", BROKEN)
    assert not ok
    # The broken file must not be promoted.
    assert not (tmp_path / "iklem" / "self_extensions" / "broken.py").exists()


def test_write_extension_without_run_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    ok, msg = write_extension("norun", NO_RUN)
    assert not ok


def test_extension_appears_in_all_tools(tmp_path, monkeypatch):
    monkeypatch.setenv("IKLEM_HOME", str(tmp_path))
    write_extension("add", GOOD)
    tool = tool_by_name("add")
    assert tool is not None
    assert tool.fn("2", "3") == "5"


def test_self_extend_tool_is_registered():
    assert tool_by_name("self_extend") is not None
