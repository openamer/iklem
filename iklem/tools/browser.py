"""Browser tools — a real, interactive browser via Playwright (optional).

This upgrades iklem from "extract text" to a full browser agent: navigate,
click, type, fill forms, take screenshots, and read links — the operations
OpenAmer's browser can do. Uses Playwright if installed; otherwise reports an
honest error.

Requires: pip install playwright && playwright install chromium
"""

from __future__ import annotations

import threading

# A single shared browser page, kept alive across tool calls so the agent can
# navigate -> click -> read in sequence (like a real browser session).
_lock = threading.Lock()
_page = None
_playwright = None


def _get_page():
    global _page, _playwright
    if _page is not None:
        return _page
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    _playwright = sync_playwright().start()
    browser = _playwright.chromium.launch(headless=True)
    _page = browser.new_page()
    return _page


def _require_playwright():
    try:
        import playwright  # noqa: F401
    except ImportError:
        return None
    return True


def browse(url: str) -> str:
    """Open a URL in a real browser and return the rendered text content."""
    if _require_playwright() is None:
        return "✗ playwright not installed — run: pip install playwright && playwright install chromium"
    if not url.startswith(("http://", "https://")):
        return f"✗ invalid URL: {url}"
    with _lock:
        page = _get_page()
        if page is None:
            return "✗ playwright not installed"
        try:
            page.goto(url, timeout=30000)
            text = page.inner_text("body")
        except Exception as e:  # noqa: BLE001
            return f"✗ browse failed: {e}"
    if len(text) > 4000:
        text = text[:4000] + "…(truncated)"
    return text


def browser_click(selector: str) -> str:
    """Click an element on the current page by CSS selector or text."""
    if _require_playwright() is None:
        return "✗ playwright not installed"
    with _lock:
        page = _get_page()
        if page is None:
            return "✗ playwright not installed"
        try:
            page.click(selector, timeout=10000)
        except Exception as e:  # noqa: BLE001
            return f"✗ click failed: {e}"
    return f"✓ clicked {selector}"


def browser_type(selector: str, text: str) -> str:
    """Type text into an input field on the current page."""
    if _require_playwright() is None:
        return "✗ playwright not installed"
    with _lock:
        page = _get_page()
        if page is None:
            return "✗ playwright not installed"
        try:
            page.fill(selector, text)
        except Exception as e:  # noqa: BLE001
            return f"✗ type failed: {e}"
    return f"✓ typed into {selector}"


def browser_submit(selector: str) -> str:
    """Submit a form (press Enter) on the current page."""
    if _require_playwright() is None:
        return "✗ playwright not installed"
    with _lock:
        page = _get_page()
        if page is None:
            return "✗ playwright not installed"
        try:
            page.press(selector, "Enter")
        except Exception as e:  # noqa: BLE001
            return f"✗ submit failed: {e}"
    return f"✓ submitted {selector}"


def browser_links() -> str:
    """Return the links (text + href) on the current page."""
    if _require_playwright() is None:
        return "✗ playwright not installed"
    with _lock:
        page = _get_page()
        if page is None:
            return "✗ playwright not installed"
        try:
            links = page.eval_on_selector_all(
                "a",
                "els => els.map(e => (e.innerText.trim() + ' -> ' + e.href).slice(0,120))",
            )
        except Exception as e:  # noqa: BLE001
            return f"✗ links failed: {e}"
    if not links:
        return "(no links)"
    return "\n".join(links[:50])


def browser_screenshot(path: str) -> str:
    """Take a screenshot of the current page and save it to a file."""
    if _require_playwright() is None:
        return "✗ playwright not installed"
    with _lock:
        page = _get_page()
        if page is None:
            return "✗ playwright not installed"
        try:
            page.screenshot(path=path)
        except Exception as e:  # noqa: BLE001
            return f"✗ screenshot failed: {e}"
    return f"✓ screenshot saved to {path}"
