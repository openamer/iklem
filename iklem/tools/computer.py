"""Computer-use tool — control the desktop (optional dependency).

This gives iklem the ability to take a screenshot and move/click the mouse,
like OpenAmer's computer_use. It uses pyautogui if installed; otherwise it
reports an honest error.

Requires: pip install pyautogui
"""

from __future__ import annotations


def screenshot() -> str:
    """Take a screenshot and return its file path."""
    try:
        import pyautogui
    except ImportError:
        return "✗ pyautogui not installed — run: pip install pyautogui"
    import os
    import tempfile

    path = os.path.join(tempfile.gettempdir(), "iklem_screenshot.png")
    try:
        pyautogui.screenshot(path)
    except Exception as e:  # noqa: BLE001
        return f"✗ screenshot failed: {e}"
    return f"✓ screenshot saved to {path}"


def click(x: str, y: str) -> str:
    """Click at screen coordinates (x, y)."""
    try:
        import pyautogui
    except ImportError:
        return "✗ pyautogui not installed — run: pip install pyautogui"
    try:
        pyautogui.click(int(x), int(y))
    except Exception as e:  # noqa: BLE001
        return f"✗ click failed: {e}"
    return f"✓ clicked ({x}, {y})"


def type_text(text: str) -> str:
    """Type text at the current cursor position."""
    try:
        import pyautogui
    except ImportError:
        return "✗ pyautogui not installed — run: pip install pyautogui"
    try:
        pyautogui.write(text)
    except Exception as e:  # noqa: BLE001
        return f"✗ type failed: {e}"
    return f"✓ typed {len(text)} chars"
