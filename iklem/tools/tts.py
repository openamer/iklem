"""Text-to-speech tool — convert text to audio (optional dependency).

This gives iklem the ability to speak, like OpenAmer's text_to_speech. It
uses the system's built-in TTS on Windows (PowerShell) or macOS (say);
otherwise it reports an honest error.
"""

from __future__ import annotations

import os
import subprocess
import tempfile


def speak(text: str) -> str:
    """Convert text to speech and play it (or save to a file).

    Uses the platform's built-in TTS. Returns a confirmation or an honest
    error.
    """
    if not text.strip():
        return "✗ empty text"

    system = os.name
    try:
        if system == "nt":
            # Windows: use PowerShell's System.Speech.
            script = (
                "Add-Type -AssemblyName System.Speech; "
                "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                f"$s.Speak([Console]::In.ReadToEnd())"
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                input=text,
                text=True,
                capture_output=True,
                timeout=60,
            )
        elif system == "posix" and os.uname().sysname == "Darwin":
            subprocess.run(["say", text], capture_output=True, timeout=60)
        else:
            return "✗ TTS not supported on this platform"
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return f"✗ TTS failed: {e}"

    return f"✓ spoke {len(text)} chars"


def speak_to_file(text: str, path: str) -> str:
    """Convert text to speech and save it to an audio file (WAV on Windows)."""
    if not text.strip():
        return "✗ empty text"
    p = os.path.abspath(os.path.expanduser(path))
    if os.name == "nt":
        script = (
            "Add-Type -AssemblyName System.Speech; "
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$s.SetOutputToWaveFile('{p}'); "
            "$s.Speak([Console]::In.ReadToEnd()); "
            "$s.Dispose()"
        )
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                input=text,
                text=True,
                capture_output=True,
                timeout=60,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return f"✗ TTS failed: {e}"
        return f"✓ saved speech to {p}"
    return "✗ speak_to_file only supported on Windows"
