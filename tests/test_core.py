"""Tests for the iklem core — verification over fabrication."""

from __future__ import annotations

import pytest

from iklem.memory.store import MemoryStore
from iklem.memory.skills import Skill, SkillRegistry
from iklem.verify.checks import CheckResult, check, require


def test_check_returns_honest_result():
    assert check(True, "ok") == CheckResult(ok=True, detail="ok")
    assert not check(False, "nope")
    assert check(False, "nope").detail == "nope"


def test_require_raises_on_failure():
    with pytest.raises(RuntimeError):
        require(False, "must hold")


def test_memory_persists_across_instances(tmp_path):
    a = MemoryStore(home=tmp_path)
    a.set("name", "Damir")
    # A fresh instance (new session) reads the same durable store.
    b = MemoryStore(home=tmp_path)
    assert b.get("name") == "Damir"


def test_memory_rejects_empty_key(tmp_path):
    store = MemoryStore(home=tmp_path)
    with pytest.raises(RuntimeError):
        store.set("", "value")


def test_skill_refine_bumps_version():
    s = Skill(name="deploy", description="Deploy the app")
    assert s.version == 1
    s.refine("run tests first")
    assert s.version == 2
    assert "run tests first" in s.steps


def test_skill_registry_roundtrip(tmp_path):
    store = MemoryStore(home=tmp_path)
    reg = SkillRegistry(store)
    reg.add(Skill(name="deploy", description="Deploy the app"))
    got = reg.get("deploy")
    assert got is not None
    assert got.name == "deploy"
    assert "deploy" in reg.names()
