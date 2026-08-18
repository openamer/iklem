"""Browser tool — a real browser via Playwright (optional dependency).

This gives iklem the ability to actually navigate a web page, click, and read
the rendered result — not just fetch raw HTML. It uses Playwright if
installed; otherwise it reports an honest error telling the user how to
install it.

Requires: pip install playwright && playwright install chromium
"""

from __future__ import annotations


def browse(url: str) -> str:
    """Open a URL in a real browser and return the rendered text content."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return (
            "✗ playwright not installed — run: pip install playwright && "
            "playwright install chromium"
        )

    if not url.startswith(("http://", "https://")):
        return f"✗ invalid URL: {url}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            text = page.inner_text("body")
            browser.close()
    except Exception as e:  # noqa: BLE001
        return f"✗ browse failed: {e}"

    if len(text) > 4000:
        text = text[:4000] + "…(truncated)"
    return text
