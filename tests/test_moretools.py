"""Tests for the new file, http, util, and process tools."""

from __future__ import annotations

from iklem.tools.files import copy_file, delete_file, move_file, search_files, write_file
from iklem.tools.http import http_request
from iklem.tools.util import json_parse, math_eval, random_number, random_uuid, world_time


def test_write_and_search_file(tmp_path):
    p = tmp_path / "note.txt"
    assert write_file(str(p), "hello world").startswith("✓")
    # search_files returns matching file paths (content contains "hello").
    assert "note.txt" in search_files("hello", str(tmp_path))


def test_copy_move_delete(tmp_path):
    src = tmp_path / "a.txt"
    src.write_text("x")
    assert copy_file(str(src), str(tmp_path / "b.txt")).startswith("✓")
    assert move_file(str(tmp_path / "b.txt"), str(tmp_path / "c.txt")).startswith("✓")
    assert delete_file(str(tmp_path / "c.txt")).startswith("✓")


def test_math_eval():
    assert math_eval("2 + 3 * 4") == "14"
    assert math_eval("2 ** 10") == "1024"


def test_math_eval_rejects_code():
    assert math_eval("__import__('os')").startswith("✗")


def test_json_parse():
    assert '"a"' in json_parse('{"a": 1}')


def test_random_tools():
    assert random_uuid()
    n = int(random_number("1", "10"))
    assert 1 <= n <= 10


def test_world_time():
    assert world_time("Europe/Berlin")
    assert world_time("Not/AZone").startswith("✗")


def test_http_request_invalid():
    assert http_request("not-a-url").startswith("✗")
