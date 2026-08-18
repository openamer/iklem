"""Skill distillation and refinement — the second half of the learning loop.

A skill is a named, versioned unit of procedural knowledge. Skills are
distilled from hard tasks and refined on reuse, so the agent gets better the
longer it runs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from iklem.memory.store import MemoryStore


@dataclass
class Skill:
    name: str
    description: str
    version: int = 1
    steps: list[str] = field(default_factory=list)

    def refine(self, new_step: str) -> None:
        """Add a step learned from reuse, bumping the version."""
        if new_step not in self.steps:
            self.steps.append(new_step)
            self.version += 1


class SkillRegistry:
    """A durable registry of skills, backed by the memory store."""

    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def add(self, skill: Skill) -> None:
        self.store.set(f"skill:{skill.name}", _serialize(skill))

    def get(self, name: str) -> Skill | None:
        raw = self.store.get(f"skill:{name}")
        return _deserialize(raw) if raw else None

    def names(self) -> list[str]:
        return [
            k.removeprefix("skill:")
            for k in self.store.keys()
            if k.startswith("skill:")
        ]


def _serialize(skill: Skill) -> str:
    import json

    return json.dumps(
        {
            "name": skill.name,
            "description": skill.description,
            "version": skill.version,
            "steps": skill.steps,
        }
    )


def _deserialize(raw: str) -> Skill:
    import json

    d = json.loads(raw)
    return Skill(
        name=d["name"],
        description=d["description"],
        version=d.get("version", 1),
        steps=d.get("steps", []),
    )
