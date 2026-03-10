"""
Step 3 — HiggsfieldClient

Generates a lip-synced talking-head video from a portrait image + audio file.
Supports two backends:

  "segmind"    — Pay-per-generation via Segmind (~$0.86/video, no subscription).
                 Works with any Higgsfield plan including Ultimate. ← DEFAULT
                 https://www.segmind.com/models/higgsfield-speech2video

  "higgsfield" — Official Higgsfield SDK. Requires Creator plan ($149/mo).
                 Uses InfiniteTalk (unlimited length) or Kling Avatar (≤15s).

Set HIGGSFIELD_BACKEND env var to choose: "segmind" (default) or "higgsfield"
"""

import os
import time
import requests
from pathlib import Path

from config import (
    HIGGSFIELD_API_KEY,
    HIGGSFIELD_BACKEND,
    SEGMIND_API_KEY,
    HIGGSFIELD_MODEL_INFINITETALK,
    HIGGSFIELD_MODEL_KLING_AVATAR,
    HIGGSFIELD_POLL_INTERVAL_SEC,
    HIGGSFIELD_TIMEOUT_SEC,
    OUTPUT_DIR,
)

# Segmind endpoint for Higgsfield Speech2Video
SEGMIND_ENDPOINT = "https://api.segmind.com/v1/higgsfield-speech2video"


def generate_video(
    image_path: str,
    audio_path: str,
    output_filename: str = "raw_video.mp4",
    use_fallback_model: bool = False,
) -> str:
    """
    Generate a lip-synced talking head video from a portrait image + audio.

    Args:
        image_path:          Path to Nicole's reference portrait image (.jpg/.png)
        audio_path:          Path to the voiceover .mp3 file
        output_filename:     Name for the downloaded video file
        use_fallback_model:  (higgsfield backend only) Use Kling Avatar (15s max)

    Returns:
        Absolute path to the downloaded .mp4 file
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if HIGGSFIELD_BACKEND == "segmind":
        return _segmind(image_path, audio_path, output_filename)
    elif HIGGSFIELD_BACKEND == "higgsfield":
        return _higgsfield_sdk(image_path, audio_path, output_filename, use_fallback_model)
    else:
        raise ValueError(f"Unknown HIGGSFIELD_BACKEND: {HIGGSFIELD_BACKEND!r}")


# ── Segmind backend (pay-per-generation, no Creator plan needed) ──────────────

def _segmind(image_path: str, audio_path: str, output_filename: str) -> str:
    """
    Call Segmind's hosted Higgsfield Speech2Video API.

    No subscription required — pay per generation (~$0.86/video).
    Get a free API key at: https://www.segmind.com/
    Set SEGMIND_API_KEY env var.

    Segmind accepts image + audio as base64-encoded strings.
    """
    if not SEGMIND_API_KEY:
        raise EnvironmentError(
            "SEGMIND_API_KEY is not set. "
            "Get a free API key at segmind.com (pay-per-use, no subscription)."
        )

    import base64

    def _b64(path: str) -> str:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    print(f"[Higgsfield/Segmind] Encoding image: {image_path}")
    print(f"[Higgsfield/Segmind] Encoding audio: {audio_path}")

    payload = {
        "image":             _b64(image_path),
        "audio":             _b64(audio_path),
        "motion_intensity":  0.6,
        "expression":        "natural",
        # Segmind may expose additional parameters — check their docs for latest
    }

    headers = {
        "x-api-key":    SEGMIND_API_KEY,
        "Content-Type": "application/json",
    }

    print("[Higgsfield/Segmind] Submitting generation job...")
    resp = requests.post(
        SEGMIND_ENDPOINT,
        headers=headers,
        json=payload,
        timeout=HIGGSFIELD_TIMEOUT_SEC,
    )

    if resp.status_code != 200:
        raise RuntimeError(
            f"Segmind API error {resp.status_code}: {resp.text[:500]}"
        )

    # Segmind returns the video as binary content directly (not a URL)
    out_path = str(Path(OUTPUT_DIR) / output_filename)
    with open(out_path, "wb") as f:
        f.write(resp.content)

    print(f"[Higgsfield/Segmind] Saved: {out_path}")
    return out_path


# ── Official Higgsfield SDK backend (requires Creator plan, $149/mo) ──────────

def _higgsfield_sdk(
    image_path: str,
    audio_path: str,
    output_filename: str,
    use_fallback_model: bool,
) -> str:
    """
    Use the official higgsfield-client SDK.
    Requires: pip install higgsfield-client + Creator plan API key.
    """
    try:
        import higgsfield_client as hf
    except ImportError:
        raise ImportError(
            "higgsfield-client is not installed. Run: pip install higgsfield-client"
        )

    if not HIGGSFIELD_API_KEY:
        raise EnvironmentError(
            "HF_KEY is not set. Format: 'key-id:key-secret'. "
            "Requires Higgsfield Creator plan ($149/mo)."
        )

    os.environ["HF_KEY"] = HIGGSFIELD_API_KEY

    model = (
        HIGGSFIELD_MODEL_KLING_AVATAR if use_fallback_model
        else HIGGSFIELD_MODEL_INFINITETALK
    )
    print(f"[Higgsfield SDK] Using model: {model}")

    print(f"[Higgsfield SDK] Uploading image: {image_path}")
    image_asset = hf.upload_image(image_path)

    print(f"[Higgsfield SDK] Uploading audio: {audio_path}")
    audio_asset = hf.upload_file(audio_path)

    print("[Higgsfield SDK] Submitting generation job...")
    controller = hf.submit(
        model,
        arguments={
            "image":            image_asset,
            "audio":            audio_asset,
            "motion_intensity": 0.6,
            "expression":       "natural",
        },
    )

    print("[Higgsfield SDK] Waiting for completion", end="", flush=True)
    elapsed = 0
    for status in controller.poll_request_status():
        print(".", end="", flush=True)
        if isinstance(status, hf.Completed):
            print(" done.")
            break
        if isinstance(status, hf.Failed):
            raise RuntimeError(f"Higgsfield generation failed: {status}")
        elapsed += HIGGSFIELD_POLL_INTERVAL_SEC
        if elapsed >= HIGGSFIELD_TIMEOUT_SEC:
            raise TimeoutError(
                f"Higgsfield generation did not complete within {HIGGSFIELD_TIMEOUT_SEC}s."
            )
        time.sleep(HIGGSFIELD_POLL_INTERVAL_SEC)

    result    = controller.get()
    video_url = result.get("video_url") or result.get("url") or result.get("output")

    if not video_url:
        raise ValueError(f"Could not find video URL in Higgsfield response: {result}")

    out_path = str(Path(OUTPUT_DIR) / output_filename)
    print(f"[Higgsfield SDK] Downloading video → {out_path}")
    video_data = requests.get(video_url, timeout=120)
    video_data.raise_for_status()

    with open(out_path, "wb") as f:
        f.write(video_data.content)

    print(f"[Higgsfield SDK] Saved: {out_path}")
    return out_path
