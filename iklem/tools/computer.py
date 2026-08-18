"""Computer-use tools — full desktop control (optional dependency).

This upgrades iklem from "click + type" to a complete desktop-control toolset:
move the mouse, scroll, press keys, use hotkeys, and read the mouse position.
Uses pyautogui if installed; otherwise reports an honest error.

Requires: pip install pyautogui
"""

from __future__ import annotations


def _require_pyautogui():
    try:
        import pyautogui  # noqa: F401
    except ImportError:
        return None
    return True


def screenshot() -> str:
    """Take a screenshot and return its file path."""
    if _require_pyautogui() is None:
        return "✗ pyautogui not installed — run: pip install pyautogui"
    import os
    import tempfile

    import pyautogui

    path = os.path.join(tempfile.gettempdir(), "iklem_screenshot.png")
    try:
        pyautogui.screenshot(path)
    except Exception as e:  # noqa: BLE001
        return f"✗ screenshot failed: {e}"
    return f"✓ screenshot saved to {path}"


def click(x: str, y: str) -> str:
    """Click at screen coordinates (x, y)."""
    if _require_pyautogui() is None:
        return "✗ pyautogui not installed — run: pip install pyautogui"
    import pyautogui

    try:
        pyautogui.click(int(x), int(y))
    except Exception as e:  # noqa: BLE001
        return f"✗ click failed: {e}"
    return f"✓ clicked ({x}, {y})"


def double_click(x: str, y: str) -> str:
    """Double-click at screen coordinates (x, y)."""
    if _require_pyautogui() is None:
        return "✗ pyautogui not installed"
    import pyautogui

    try:
        pyautogui.doubleClick(int(x), int(y))
    except Exception as e:  # noqa: BLE001
        return f"✗ double-click failed: {e}"
    return f"✓ double-clicked ({x}, {y})"


def right_click(x: str, y: str) -> str:
    """Right-click at screen coordinates (x, y)."""
    if _require_pyautogui() is None:
        return "✗ pyautogui not installed"
    import pyautogui

    try:
        pyautogui.rightClick(int(x), int(y))
    except Exception as e:  # noqa: BLE001
        return f"✗ right-click failed: {e}"
    return f"✓ right-clicked ({x}, {y})"


def move_mouse(x: str, y: str) -> str:
    """Move the mouse to screen coordinates (x, y)."""
    if _require_pyautogui() is None:
        return "✗ pyautogui not installed"
    import pyautogui

    try:
        pyautogui.moveTo(int(x), int(y))
    except Exception as e:  # noqa: BLE001
        return f"✗ move failed: {e}"
    return f"✓ moved to ({x}, {y})"


def mouse_position() -> str:
    """Return the current mouse position (x, y)."""
    if _require_pyautogui() is None:
        return "✗ pyautogui not installed"
    import pyautogui

    try:
        x, y = pyautogui.position()
    except Exception as e:  # noqa: BLE001
        return f"✗ position failed: {e}"
    return f"({x}, {y})"


def scroll(amount: str) -> str:
    """Scroll the mouse wheel (positive = up, negative = down)."""
    if _require_pyautogui() is None:
        return "✗ pyautogui not installed"
    import pyautogui

    try:
        pyautogui.scroll(int(amount))
    except Exception as e:  # noqa: BLE001
        return f"✗ scroll failed: {e}"
    return f"✓ scrolled {amount}"


def type_text(text: str) -> str:
    """Type text at the current cursor position."""
    if _require_pyautogui() is None:
        return "✗ pyautogui not installed — run: pip install pyautogui"
    import pyautogui

    try:
        pyautogui.write(text)
    except Exception as e:  # noqa: BLE001
        return f"✗ type failed: {e}"
    return f"✓ typed {len(text)} chars"


def press_key(key: str) -> str:
    """Press a single key (e.g. 'enter', 'tab', 'escape', 'a')."""
    if _require_pyautogui() is None:
        return "✗ pyautogui not installed"
    import pyautogui

    try:
        pyautogui.press(key)
    except Exception as e:  # noqa: BLE001
        return f"✗ press failed: {e}"
    return f"✓ pressed {key}"


def hotkey(keys: str) -> str:
    """Press a key combination (e.g. 'ctrl+s', 'ctrl+alt+t')."""
    if _require_pyautogui() is None:
        return "✗ pyautogui not installed"
    import pyautogui

    parts = [k.strip().lower() for k in keys.split("+") if k.strip()]
    if not parts:
        return "✗ no keys provided"
    try:
        pyautogui.hotkey(*parts)
    except Exception as e:  # noqa: BLE001
        return f"✗ hotkey failed: {e}"
    return f"✓ pressed {'+'.join(parts)}"
