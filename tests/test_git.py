"""Tests for the git tools."""

from __future__ import annotations

from iklem.tools.git import git_commit, git_status


def test_git_status_returns_something():
    result = git_status()
    # Either a clean tree or a list of changes — never an error.
    assert isinstance(result, str)
    assert result


def test_git_commit_rejects_empty_message():
    result = git_commit("")
    assert result.startswith("✗")
