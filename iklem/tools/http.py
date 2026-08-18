"""HTTP tools — full request methods and weather.

Extends fetch_url (GET only) with POST/PUT/DELETE and a weather lookup via
the free open-meteo API (no key required).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


def http_request(url: str, method: str = "GET", body: str = "") -> str:
    """Make an HTTP request (GET/POST/PUT/DELETE) and return the response text."""
    method = method.upper()
    if method not in ("GET", "POST", "PUT", "DELETE", "PATCH"):
        return f"✗ unsupported method: {method}"
    if not url.startswith(("http://", "https://")):
        return f"✗ invalid URL: {url}"
    data = body.encode("utf-8") if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"User-Agent": "iklem/0.1", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read(4000).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return f"✗ HTTP {e.code} for {url}"
    except urllib.error.URLError as e:
        return f"✗ network error for {url}: {e.reason}"
    return text


def weather(city: str) -> str:
    """Return current weather for a city using the free open-meteo API.

    Uses geocoding to resolve the city to coordinates, then fetches current
    conditions. No API key required.
    """
    # Geocode the city.
    geo_url = (
        "https://geocoding-api.open-meteo.com/v1/search?count=1&format=json&name="
        + urllib.parse.quote(city)
    )
    try:
        with urllib.request.urlopen(geo_url, timeout=30) as resp:
            geo = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError) as e:
        return f"✗ geocoding error: {e}"

    results = geo.get("results", [])
    if not results:
        return f"✗ city not found: {city}"
    r = results[0]
    lat, lon = r["latitude"], r["longitude"]
    name = r.get("name", city)

    # Fetch current weather.
    w_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
    )
    try:
        with urllib.request.urlopen(w_url, timeout=30) as resp:
            w = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError) as e:
        return f"✗ weather error: {e}"

    cur = w.get("current", {})
    temp = cur.get("temperature_2m", "?")
    hum = cur.get("relative_humidity_2m", "?")
    wind = cur.get("wind_speed_10m", "?")
    return (
        f"{name}: {temp}°C, humidity {hum}%, wind {wind} km/h"
    )
