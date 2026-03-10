"""
Step 2 — TTSGenerator

Converts clean script text to an audio file using either:
  • ElevenLabs (recommended — supports voice cloning of Nicole)
  • OpenAI TTS (fallback — no voice cloning, faster setup)

Returns: path to the generated .mp3 file
"""

import os
import requests
from pathlib import Path

from config import (
    TTS_PROVIDER,
    ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID,
    ELEVENLABS_MODEL, ELEVENLABS_SETTINGS,
    OPENAI_API_KEY, OPENAI_TTS_VOICE,
    OUTPUT_DIR,
)


def generate(clean_text: str, output_filename: str = "voiceover.mp3") -> str:
    """
    Convert text to speech and save to OUTPUT_DIR.

    Args:
        clean_text:       TTS-ready script string
        output_filename:  Name for the output audio file

    Returns:
        Absolute path to the saved .mp3 file
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = str(Path(OUTPUT_DIR) / output_filename)

    if TTS_PROVIDER == "elevenlabs":
        return _elevenlabs(clean_text, out_path)
    elif TTS_PROVIDER == "openai":
        return _openai(clean_text, out_path)
    else:
        raise ValueError(f"Unknown TTS_PROVIDER: {TTS_PROVIDER!r}")


# ── ElevenLabs ───────────────────────────────────────────────────────────────

def _elevenlabs(text: str, out_path: str) -> str:
    """
    Call ElevenLabs v1 TTS API with Nicole's cloned voice.

    To clone Nicole's voice:
      1. Go to elevenlabs.io → Voices → Add Voice → Instant Voice Clone
      2. Upload 1–5 min of clean Nicole audio
      3. Copy the Voice ID into ELEVENLABS_VOICE_ID env var
    """
    if not ELEVENLABS_API_KEY:
        raise EnvironmentError("ELEVENLABS_API_KEY is not set.")
    if not ELEVENLABS_VOICE_ID:
        raise EnvironmentError(
            "ELEVENLABS_VOICE_ID is not set. "
            "Create a cloned voice in the ElevenLabs dashboard and paste the ID."
        )

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key":   ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept":       "audio/mpeg",
    }
    payload = {
        "text":       text,
        "model_id":   ELEVENLABS_MODEL,
        "voice_settings": ELEVENLABS_SETTINGS,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()

    with open(out_path, "wb") as f:
        f.write(resp.content)

    print(f"[TTS] ElevenLabs audio saved → {out_path}")
    return out_path


# ── OpenAI TTS (fallback) ─────────────────────────────────────────────────────

def _openai(text: str, out_path: str) -> str:
    """
    Call OpenAI TTS API (no voice cloning — uses a preset voice).
    Good for prototyping; swap for ElevenLabs once Nicole's voice is cloned.
    """
    if not OPENAI_API_KEY:
        raise EnvironmentError("OPENAI_API_KEY is not set.")

    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=OPENAI_TTS_VOICE,
        input=text,
    )
    response.stream_to_file(out_path)

    print(f"[TTS] OpenAI audio saved → {out_path}")
    return out_path
