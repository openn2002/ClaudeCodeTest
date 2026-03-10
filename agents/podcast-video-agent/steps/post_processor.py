"""
Step 4 — PostProcessor

Takes the raw Higgsfield video and produces export-ready files:
  • Crops / pads to target aspect ratios (9:16 Reels, 16:9 YouTube, 1:1 square)
  • Optionally mixes in background music at -20dB
  • Optionally burns in a lower-third text overlay (name + title)
  • Outputs one .mp4 per format

Requires: ffmpeg installed and on PATH
    macOS:   brew install ffmpeg
    Ubuntu:  apt-get install ffmpeg
"""

import os
import subprocess
from pathlib import Path

from config import (
    OUTPUT_DIR,
    OUTPUT_FORMATS,
    BACKGROUND_MUSIC_PATH,
    PRESENTER_NAME,
    PRESENTER_TITLE,
    BRAND_NAME,
)


def process(
    raw_video_path: str,
    concept_slug: str,
    add_lower_third: bool = True,
    add_music: bool = True,
) -> dict[str, str]:
    """
    Export the raw video into all configured output formats.

    Args:
        raw_video_path:  Path to the Higgsfield output .mp4
        concept_slug:    Short name for the video concept (used in filename),
                         e.g. "glp1-muscle-loss"
        add_lower_third: Burn in "Nicole | Accredited Practising Dietitian" text
        add_music:       Mix background music at -20dB (requires BG_MUSIC_PATH)

    Returns:
        dict mapping format name → output file path
        e.g. {"reels": "/output/glp1-muscle-loss_reels.mp4", ...}
    """
    _check_ffmpeg()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    outputs = {}
    for fmt_name, fmt in OUTPUT_FORMATS.items():
        out_path = str(Path(OUTPUT_DIR) / f"{concept_slug}_{fmt_name}.mp4")
        _export(
            src=raw_video_path,
            dst=out_path,
            width=fmt["width"],
            height=fmt["height"],
            add_lower_third=add_lower_third,
            add_music=add_music,
        )
        outputs[fmt_name] = out_path
        print(f"[PostProcessor] Exported {fmt_name} → {out_path}")

    return outputs


# ── Internal helpers ──────────────────────────────────────────────────────────

def _export(
    src: str,
    dst: str,
    width: int,
    height: int,
    add_lower_third: bool,
    add_music: bool,
) -> None:
    """Build and run the ffmpeg command for one output format."""

    # Video filter chain
    vf_parts = [
        # Scale + pad to target resolution (letterbox / pillarbox as needed)
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black",
    ]

    if add_lower_third:
        # Teal background bar + white name text + grey title text
        # Positioned at the bottom ~20% of the frame
        bar_y    = int(height * 0.78)
        name_y   = bar_y + int(height * 0.025)
        title_y  = name_y + int(height * 0.04)
        font_sz_name  = max(18, int(height * 0.028))
        font_sz_title = max(14, int(height * 0.022))

        vf_parts += [
            # Semi-transparent teal bar
            f"drawbox=x=0:y={bar_y}:w={width}:h={int(height * 0.12)}"
            f":color=0x00C4CC@0.85:t=fill",
            # Presenter name
            f"drawtext=text='{PRESENTER_NAME}':"
            f"fontsize={font_sz_name}:fontcolor=white:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"x=(w-text_w)/2:y={name_y}",
            # Title line
            f"drawtext=text='{PRESENTER_TITLE}  |  {BRAND_NAME}':"
            f"fontsize={font_sz_title}:fontcolor=white@0.85:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
            f"x=(w-text_w)/2:y={title_y}",
        ]

    vf_str = ",".join(vf_parts)

    # Audio: mix voiceover with optional background music
    if add_music and BACKGROUND_MUSIC_PATH and os.path.exists(BACKGROUND_MUSIC_PATH):
        cmd = [
            "ffmpeg", "-y",
            "-i", src,
            "-i", BACKGROUND_MUSIC_PATH,
            "-filter_complex",
            f"[0:v]{vf_str}[v];"
            "[1:a]volume=-20dB,afade=t=out:st=0:d=2[music];"  # fade music in 2s at end
            "[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            dst,
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", src,
            "-vf", vf_str,
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            dst,
        ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg failed for {dst}:\n{result.stderr[-1000:]}"
        )


def _check_ffmpeg() -> None:
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    if result.returncode != 0:
        raise EnvironmentError(
            "ffmpeg is not installed or not on PATH.\n"
            "  macOS:  brew install ffmpeg\n"
            "  Ubuntu: apt-get install ffmpeg"
        )
