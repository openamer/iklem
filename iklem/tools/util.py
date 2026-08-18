"""Utility tools — JSON, math, timezones, and random values."""

from __future__ import annotations

import json
import math
import random
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo


def json_parse(text: str) -> str:
    """Parse a JSON string and return it pretty-printed."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return f"✗ invalid JSON: {e}"
    return json.dumps(data, indent=2, ensure_ascii=False)


def math_eval(expression: str) -> str:
    """Evaluate a safe arithmetic expression (+, -, *, /, **, %, parentheses)."""
    # Only allow a whitelist of characters to prevent code execution.
    allowed = set("0123456789+-*/().% e")
    if not all(c in allowed for c in expression):
        return "✗ expression contains disallowed characters"
    try:
        result = eval(expression, {"__builtins__": {}}, {})  # noqa: S307 — whitelisted
    except Exception as e:  # noqa: BLE001
        return f"✗ evaluation error: {e}"
    return str(result)


def world_time(timezone: str) -> str:
    """Return the current time in a given IANA timezone (e.g. 'Europe/Berlin')."""
    try:
        tz = ZoneInfo(timezone)
    except Exception:  # noqa: BLE001
        return f"✗ unknown timezone: {timezone}"
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")


def random_uuid() -> str:
    """Return a random UUID v4."""
    return str(uuid.uuid4())


def random_number(low: str, high: str) -> str:
    """Return a random integer between low and high (inclusive)."""
    try:
        lo, hi = int(low), int(high)
    except ValueError:
        return "✗ low and high must be integers"
    if lo > hi:
        lo, hi = hi, lo
    return str(random.randint(lo, hi))
