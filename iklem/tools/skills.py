"""Skill tools — let the agent distill and reuse procedural knowledge.

This is the second half of the learning loop: memory stores facts, skills
store procedures. When the agent solves a hard task, it can save the steps as
a skill and reuse them later — so it genuinely gets better at recurring work.
"""

from __future__ import annotations

from iklem.memory.skills import Skill, SkillRegistry
from iklem.memory.store import MemoryStore


def _registry() -> SkillRegistry:
    return SkillRegistry(MemoryStore())


def save_skill(name: str, description: str, steps: str) -> str:
    """Save a skill (a reusable procedure) with its steps.

    `steps` is a newline-separated list of steps.
    """
    reg = _registry()
    step_list = [s.strip() for s in steps.split("\n") if s.strip()]
    reg.add(Skill(name=name, description=description, steps=step_list))
    return f"saved skill '{name}' ({len(step_list)} steps)"


def list_skills() -> str:
    """List all saved skills with their descriptions."""
    reg = _registry()
    names = reg.names()
    if not names:
        return "(no skills)"
    lines = []
    for n in names:
        skill = reg.get(n)
        if skill:
            lines.append(f"{n}: {skill.description}")
    return "\n".join(lines)


def get_skill(name: str) -> str:
    """Retrieve a saved skill's steps."""
    reg = _registry()
    skill = reg.get(name)
    if skill is None:
        return f"(no skill named {name})"
    steps = "\n".join(f"{i+1}. {s}" for i, s in enumerate(skill.steps))
    return f"{skill.name}: {skill.description}\n{steps}"
