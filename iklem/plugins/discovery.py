"""Dynamic plugin discovery — load plugins from a directory at runtime.

This makes "everything is a plugin" real: a plugin is a Python file in the
plugins directory that exposes a `PLUGIN` object (a PluginManifest + handler).
The core discovers and registers them without hard-coding any specific plugin.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from iklem.plugins.manifest import Plugin, PluginManifest, PluginRegistry


def _default_plugin_dir() -> Path:
    import os

    env = os.environ.get("IKLEM_PLUGIN_DIR")
    if env:
        return Path(env)
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("HOME") or "."
    return Path(base) / "iklem" / "plugins"


def discover_plugins(plugin_dir: Path | None = None) -> PluginRegistry:
    """Discover and register plugins from a directory.

    Each `.py` file in the directory may define a module-level `PLUGIN` object
    (a `Plugin`). Files without one are skipped silently. A broken plugin is
    reported but does not crash discovery.
    """
    registry = PluginRegistry()
    directory = plugin_dir or _default_plugin_dir()
    if not directory.is_dir():
        return registry

    for path in sorted(directory.glob("*.py")):
        if path.name.startswith("_"):
            continue
        plugin = _load_plugin_file(path)
        if plugin is not None:
            registry.register(plugin)
    return registry


def _load_plugin_file(path: Path) -> Plugin | None:
    module_name = f"iklem_plugin_{path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:  # noqa: BLE001 — a broken plugin must not crash discovery
        return None
    plugin = getattr(module, "PLUGIN", None)
    if isinstance(plugin, Plugin):
        return plugin
    return None
