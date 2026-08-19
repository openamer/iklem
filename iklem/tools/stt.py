"""Speech-to-text tool — let iklem hear (optional dependency).

This closes the voice gap: iklem can speak (TTS) but could not hear. This
tool transcribes an audio file (or live microphone input) to text, like
hermes-agent's voice-memo transcription.

Primary backend: the `speech_recognition` library (supports Google, Sphinx,
and others). Falls back to Windows' built-in System.Speech recognition.
Reports an honest error if neither is available.

Requires (optional): pip install SpeechRecognition
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def transcribe_audio(path: str) -> str:
    """Transcribe an audio file (WAV/FLAC/etc.) to text.

    Uses SpeechRecognition if installed; otherwise Windows System.Speech.
    Returns the transcribed text or an honest error.
    """
    p = Path(path).expanduser()
    if not p.exists():
        return f"✗ audio file not found: {path}"

    # Primary: SpeechRecognition library.
    try:
        import speech_recognition as sr
    except ImportError:
        return _transcribe_windows(p)

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(str(p)) as source:
            audio = recognizer.record(source)
    except Exception as e:  # noqa: BLE001
        return f"✗ could not read audio: {e}"

    # Try Google (free, no key), then Sphinx (offline).
    try:
        return recognizer.recognize_google(audio)
    except Exception:  # noqa: BLE001
        try:
            return recognizer.recognize_sphinx(audio)
        except Exception as e:  # noqa: BLE001
            return f"✗ transcription failed: {e}"


def _transcribe_windows(path: Path) -> str:
    """Fallback: Windows System.Speech recognition (built-in, no install)."""
    if os.name != "nt":
        return "✗ SpeechRecognition not installed — run: pip install SpeechRecognition"
    script = (
        "Add-Type -AssemblyName System.Speech; "
        "$r = New-Object System.Speech.Recognition.SpeechRecognitionEngine; "
        "$r.SetInputToWaveFile([Console]::In.ReadToEnd().Trim()); "
        "$r.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar)); "
        "$result = $r.Recognize(); "
        "if ($result) { $result.Text } else { '' }"
    )
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            input=str(path),
            text=True,
            capture_output=True,
            timeout=60,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return f"✗ transcription failed: {e}"
    text = (proc.stdout or "").strip()
    return text if text else "✗ no speech recognized"


def listen(duration: str = "5") -> str:
    """Record from the microphone for N seconds and transcribe it.

    Uses SpeechRecognition's microphone support. Returns the text or an
    honest error.
    """
    try:
        import speech_recognition as sr
    except ImportError:
        return "✗ SpeechRecognition not installed — run: pip install SpeechRecognition pyaudio"
    try:
        seconds = int(duration)
    except ValueError:
        return "✗ duration must be an integer number of seconds"

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=seconds + 2, phrase_time_limit=seconds)
    except Exception as e:  # noqa: BLE001
        return f"✗ microphone error: {e}"

    try:
        return recognizer.recognize_google(audio)
    except Exception as e:  # noqa: BLE001
        return f"✗ transcription failed: {e}"
