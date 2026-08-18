"""Vision tool — describe an image (optional dependency).

This gives iklem the ability to "see" an image, like OpenAmer's
vision_analyze. It uses an OpenAI-compatible vision endpoint if configured;
otherwise it reports an honest error.

Requires: IKLEM_VISION_URL and IKLEM_VISION_KEY (or a local vision model).
"""

from __future__ import annotations

import base64
import json
import os
import urllib.request
from pathlib import Path


def describe_image(path: str) -> str:
    """Describe the contents of an image file using a vision model.

    Reads the image, sends it to a configured vision endpoint, and returns a
    text description. Returns an honest error if no vision endpoint is set.
    """
    url = os.environ.get("IKLEM_VISION_URL", "")
    key = os.environ.get("IKLEM_VISION_KEY", "")
    if not url:
        return (
            "✗ no vision endpoint configured — set IKLEM_VISION_URL and "
            "IKLEM_VISION_KEY to enable image understanding"
        )

    p = Path(path).expanduser()
    if not p.exists():
        return f"✗ image not found: {path}"

    try:
        data = p.read_bytes()
    except OSError as e:
        return f"✗ error reading image: {e}"

    b64 = base64.b64encode(data).decode("ascii")
    payload = {
        "model": os.environ.get("IKLEM_VISION_MODEL", "vision"),
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                ],
            }
        ],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        return f"✗ vision request failed: {e}"

    try:
        return result["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return "✗ unexpected vision response format"
