"""Tests for dynamic plugin discovery."""

from __future__ import annotations

from iklem.plugins.discovery import discover_plugins
from iklem.plugins.manifest import Plugin, PluginManifest


def _write_plugin(tmp_path, name, content):
    d = tmp_path / "plugins"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.py").write_text(content, encoding="utf-8")
    return d


def test_discovers_valid_plugin(tmp_path):
    d = _write_plugin(
        tmp_path,
        "hello",
        "from iklem.plugins.manifest import Plugin, PluginManifest\n"
        "PLUGIN = Plugin(manifest=PluginManifest(name='hello', kind='tool'), handler=lambda: 'hi')\n",
    )
    registry = discover_plugins(d)
    assert len(registry) == 1
    assert registry.get("tool", "hello") is not None


def test_skips_file_without_plugin(tmp_path):
    d = _write_plugin(tmp_path, "plain", "x = 1\n")
    registry = discover_plugins(d)
    assert len(registry) == 0


def test_skips_broken_plugin(tmp_path):
    d = _write_plugin(tmp_path, "broken", "raise RuntimeError('boom')\n")
    registry = discover_plugins(d)
    assert len(registry) == 0


def test_empty_dir_returns_empty_registry(tmp_path):
    d = tmp_path / "plugins"
    d.mkdir(parents=True, exist_ok=True)
    registry = discover_plugins(d)
    assert len(registry) == 0
