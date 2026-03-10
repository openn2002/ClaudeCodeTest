"""
Step 3 — HiggsfieldClient

Uploads Nicole's reference image + voiceover audio to Higgsfield,
calls the InfiniteTalk model (image + audio → lip-synced talking head),
polls for completion, and downloads the result.

Primary model: InfiniteTalk (unlimited length, portrait + audio → video)
Fallback model: Kling AI Avatar (up to 15s, good for testing on lower credit spend)
"""

import os
import time
import requests
from pathlib import Path

import higgsfield_client as hf

from config import (
    HIGGSFIELD_API_KEY,
    HIGGSFIELD_MODEL_INFINITETALK,
    HIGGSFIELD_MODEL_KLING_AVATAR,
    HIGGSFIELD_POLL_INTERVAL_SEC,
    HIGGSFIELD_TIMEOUT_SEC,
    OUTPUT_DIR,
)


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
        use_fallback_model:  If True, use Kling Avatar (15s max) instead of InfiniteTalk

    Returns:
        Absolute path to the downloaded .mp4 file
    """
    if not HIGGSFIELD_API_KEY:
        raise EnvironmentError(
            "HF_KEY is not set. "
            "Set it as 'your-key-id:your-key-secret' (Creator plan required)."
        )

    os.environ["HF_KEY"] = HIGGSFIELD_API_KEY
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    model = (
        HIGGSFIELD_MODEL_KLING_AVATAR if use_fallback_model
        else HIGGSFIELD_MODEL_INFINITETALK
    )
    print(f"[Higgsfield] Using model: {model}")

    # Upload assets to Higgsfield's asset store
    print(f"[Higgsfield] Uploading image: {image_path}")
    image_asset = hf.upload_image(image_path)

    print(f"[Higgsfield] Uploading audio: {audio_path}")
    audio_asset = hf.upload_file(audio_path)

    # Submit the generation job
    print("[Higgsfield] Submitting generation job...")
    controller = hf.submit(
        model,
        arguments={
            "image":      image_asset,   # uploaded portrait
            "audio":      audio_asset,   # uploaded voiceover
            # InfiniteTalk specific — adjust if model path uses different arg names
            "motion_intensity": 0.6,     # 0.0 = minimal movement, 1.0 = expressive
            "expression":       "natural",
        },
    )

    # Poll for completion
    print("[Higgsfield] Waiting for video generation", end="", flush=True)
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

    # Retrieve result
    result    = controller.get()
    video_url = result.get("video_url") or result.get("url") or result.get("output")

    if not video_url:
        raise ValueError(f"Could not find video URL in Higgsfield response: {result}")

    # Download the video
    out_path = str(Path(OUTPUT_DIR) / output_filename)
    print(f"[Higgsfield] Downloading video → {out_path}")
    video_data = requests.get(video_url, timeout=120)
    video_data.raise_for_status()

    with open(out_path, "wb") as f:
        f.write(video_data.content)

    print(f"[Higgsfield] Saved: {out_path}")
    return out_path
