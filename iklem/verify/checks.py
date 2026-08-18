"""The "does not break" axis: verification over fabrication.

Every state-changing operation returns a verifiable result. Nothing here
claims success it cannot prove — a failed check raises or returns an honest
error instead of a fabricated "ok".
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CheckResult:
    """The honest outcome of a verification check."""

    ok: bool
    detail: str

    def __bool__(self) -> bool:
        return self.ok


def check(condition: bool, detail: str) -> CheckResult:
    """Return a CheckResult instead of asserting — callers decide how to react."""
    return CheckResult(ok=condition, detail=detail)


def require(condition: bool, detail: str) -> None:
    """Raise on a failed precondition. Use for invariants that must hold."""
    if not condition:
        raise RuntimeError(detail)
