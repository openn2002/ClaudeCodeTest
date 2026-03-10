"""
Configuration for the Digital Wellness Podcast Video Agent.

Set all secrets via environment variables — never hardcode keys here.
"""

import os

# ── Higgsfield ───────────────────────────────────────────────────────────────
# !! IMPORTANT: API access requires the Creator plan ($149/mo) — NOT Ultimate ($49/mo).
#    If you're on Ultimate, use HIGGSFIELD_BACKEND = "segmind" below instead.
#
# Format: "key-id:key-secret"
HIGGSFIELD_API_KEY = os.environ.get("HF_KEY", "")

# Choose backend:
#   "higgsfield" — official SDK (requires Creator plan, $149/mo)
#   "segmind"    — pay-per-generation via Segmind (~$0.86/video, no subscription needed)
HIGGSFIELD_BACKEND = os.environ.get("HIGGSFIELD_BACKEND", "segmind")

# Segmind API key — get one free at segmind.com (pay-per-use, no subscription)
SEGMIND_API_KEY = os.environ.get("SEGMIND_API_KEY", "")

# Model paths (confirm exact strings in your Higgsfield Cloud dashboard)
# InfiniteTalk: image + audio → infinite-length lip-synced talking head video
HIGGSFIELD_MODEL_INFINITETALK = "higgsfield/lipsync/infinitetalk"
# Kling Avatar fallback: image + audio → up to 15s clip (for testing / lower cost)
HIGGSFIELD_MODEL_KLING_AVATAR  = "kling/avatar/v1/image-to-video"

# Polling
HIGGSFIELD_POLL_INTERVAL_SEC = 3
HIGGSFIELD_TIMEOUT_SEC       = 300   # 5 minutes max wait per generation

# ── TTS Provider ─────────────────────────────────────────────────────────────
# Options: "elevenlabs" | "openai"
TTS_PROVIDER = os.environ.get("TTS_PROVIDER", "elevenlabs")

# ElevenLabs — https://elevenlabs.io
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
# Voice ID for Nicole's cloned voice (create in ElevenLabs dashboard, paste ID here)
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "")
ELEVENLABS_MODEL    = "eleven_multilingual_v2"
ELEVENLABS_SETTINGS = {
    "stability":        0.5,
    "similarity_boost": 0.85,
    "style":            0.2,   # slight warmth/expressiveness
    "use_speaker_boost": True,
}

# OpenAI TTS (fallback — no voice cloning, but easier to get started)
OPENAI_API_KEY  = os.environ.get("OPENAI_API_KEY", "")
OPENAI_TTS_VOICE = "nova"   # Options: alloy, echo, fable, onyx, nova, shimmer

# ── Output ───────────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

# Export formats — produces one file per format
OUTPUT_FORMATS = {
    "reels":   {"aspect": "9:16",  "width": 1080, "height": 1920},  # TikTok / Instagram Reels
    "youtube": {"aspect": "16:9",  "width": 1920, "height": 1080},  # YouTube / horizontal
    "square":  {"aspect": "1:1",   "width": 1080, "height": 1080},  # Facebook
}

# Optional: path to background music file (mixed at -20dB under voice)
BACKGROUND_MUSIC_PATH = os.environ.get("BG_MUSIC_PATH", "")

# ── Brand ─────────────────────────────────────────────────────────────────────
BRAND_NAME      = "Digital Wellness"
PRESENTER_NAME  = "Nicole"
PRESENTER_TITLE = "Accredited Practising Dietitian"
WATERMARK_TEXT  = f"{PRESENTER_NAME}  |  {BRAND_NAME}"
