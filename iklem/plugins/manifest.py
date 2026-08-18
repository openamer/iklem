"""Plugin manifest and registry — "everything is a plugin".

This is the idea taken from the deepseek-harness lineage: a narrow core that
discovers and orchestrates plugins, never hard-coding a specific channel or
tool. A plugin is a self-contained unit with a manifest.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class PluginManifest:
    """Declares what a plugin is and what it provides."""

    name: str
    kind: str  # "channel" | "tool" | "provider"
    version: str = "0.1.0"
    description: str = ""


@dataclass
class Plugin:
    manifest: PluginManifest
    handler: Callable[..., Any] = field(repr=False)


class PluginRegistry:
    """Discovers and holds plugins, keyed by (kind, name)."""

    def __init__(self) -> None:
        self._plugins: dict[tuple[str, str], Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        key = (plugin.manifest.kind, plugin.manifest.name)
        self._plugins[key] = plugin

    def get(self, kind: str, name: str) -> Plugin | None:
        return self._plugins.get((kind, name))

    def of_kind(self, kind: str) -> list[Plugin]:
        return [p for (k, _), p in self._plugins.items() if k == kind]

    def __len__(self) -> int:
        return len(self._plugins)
