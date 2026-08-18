"""The self_modify tool — the agent changes its own core, gated by tests.

This is the safe path to core self-modification: the agent proposes a change
to a file inside the iklem package, and it is only promoted if the full test
suite passes. On failure it is rolled back automatically.
"""

from __future__ import annotations

from iklem.selfmodify import self_modify


def self_modify_tool(path: str, new_content: str) -> str:
    """Modify a core file, gated by the test suite (rollback on failure)."""
    return self_modify(path, new_content)
