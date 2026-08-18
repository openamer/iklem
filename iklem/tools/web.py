"""Web tools — let the agent reach the real internet.

These tools let iklem fetch a URL and search the web, so it can answer
questions about the world instead of guessing. All network access is
best-effort and reports honest errors.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request


def fetch_url(url: str) -> str:
    """Fetch a URL and return its text content (truncated to 4000 chars)."""
    if not url.startswith(("http://", "https://")):
        return f"(invalid URL: {url})"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "iklem/0.1"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read(4000)
    except urllib.error.HTTPError as e:
        return f"(HTTP {e.code} for {url})"
    except urllib.error.URLError as e:
        return f"(network error for {url}: {e.reason})"
    text = data.decode("utf-8", errors="replace")
    return text


def search_wikipedia(query: str) -> str:
    """Search Wikipedia and return the top result summaries.

    Uses the public Wikipedia API (no key, no CAPTCHA). Returns the title and
    a short extract for the top matches.
    """
    url = (
        "https://en.wikipedia.org/w/api.php?action=query&list=search"
        "&srlimit=5&format=json&srsearch=" + urllib.parse.quote(query)
    )
    req = urllib.request.Request(url, headers={"User-Agent": "iklem/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError) as e:
        return f"(search error: {e})"

    results = data.get("query", {}).get("search", [])
    if not results:
        return "(no results)"
    lines = []
    for r in results[:5]:
        title = r.get("title", "")
        snippet = re.sub(r"<[^>]+>", "", r.get("snippet", "")).strip()
        lines.append(f"{title}: {snippet}")
    return "\n".join(lines)
