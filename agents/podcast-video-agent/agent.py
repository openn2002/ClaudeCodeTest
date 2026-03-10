"""
Digital Wellness — Podcast Video Agent
=======================================
Turns a written podcast script into a branded video of Nicole (AI talking head)
using Higgsfield's InfiniteTalk model + ElevenLabs voice cloning.

Workflow:
    1. ScriptProcessor  — clean + validate script
    2. TTSGenerator     — script → nicole_voice.mp3 (ElevenLabs or OpenAI)
    3. HiggsfieldClient — image + audio → raw lip-synced video (InfiniteTalk)
    4. PostProcessor    — crop, lower-third, music → final exports

Usage:
    python agent.py --script scripts/glp1_muscle_loss.txt \\
                    --image  assets/nicole_portrait.jpg \\
                    --concept glp1-muscle-loss

    Or import and call run() directly from another orchestrator.

Environment variables required:
    HF_KEY                  — Higgsfield API key (format: "key-id:key-secret")
    ELEVENLABS_API_KEY      — ElevenLabs API key
    ELEVENLABS_VOICE_ID     — Nicole's cloned voice ID from ElevenLabs dashboard

Optional:
    TTS_PROVIDER            — "elevenlabs" (default) or "openai"
    OPENAI_API_KEY          — Required if TTS_PROVIDER=openai
    BG_MUSIC_PATH           — Path to background music file for post-processing
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from steps import script_processor, tts, higgsfield_client, post_processor


def run(
    script_text: str,
    image_path: str,
    concept_slug: str,
    target_seconds: int = 60,
    add_lower_third: bool = True,
    add_music: bool = True,
    use_fallback_model: bool = False,
) -> dict:
    """
    Run the full podcast video pipeline.

    Args:
        script_text:         Raw script (may contain [stage notes])
        image_path:          Path to Nicole's portrait image
        concept_slug:        Short name for filenames, e.g. "glp1-muscle-loss"
        target_seconds:      Target video length for length validation
        add_lower_third:     Burn in name/title overlay on final video
        add_music:           Mix background music into final video
        use_fallback_model:  Use Kling Avatar (15s) instead of InfiniteTalk (unlimited)

    Returns:
        dict with:
            concept_slug    — str
            word_count      — int
            estimated_secs  — float
            audio_path      — str (generated voiceover)
            raw_video_path  — str (Higgsfield output)
            exports         — dict[format_name → file_path]
            warnings        — list[str]
            completed_at    — ISO timestamp
    """
    print(f"\n{'='*60}")
    print(f"  Podcast Video Agent — {concept_slug}")
    print(f"{'='*60}\n")

    # ── Step 1: Process script ────────────────────────────────────────────────
    print("[1/4] Processing script...")
    script_result = script_processor.process(script_text, target_seconds=target_seconds)

    if script_result["warnings"]:
        for w in script_result["warnings"]:
            print(f"  ⚠  {w}")

    print(
        f"  → {script_result['word_count']} words, "
        f"~{script_result['estimated_secs']}s estimated"
    )

    # ── Step 2: Generate voiceover ────────────────────────────────────────────
    print("\n[2/4] Generating voiceover (TTS)...")
    audio_filename = f"{concept_slug}_voiceover.mp3"
    audio_path = tts.generate(
        clean_text=script_result["clean_text"],
        output_filename=audio_filename,
    )

    # ── Step 3: Generate video (Higgsfield) ───────────────────────────────────
    print("\n[3/4] Generating lip-synced video (Higgsfield)...")
    raw_video_path = higgsfield_client.generate_video(
        image_path=image_path,
        audio_path=audio_path,
        output_filename=f"{concept_slug}_raw.mp4",
        use_fallback_model=use_fallback_model,
    )

    # ── Step 4: Post-process exports ──────────────────────────────────────────
    print("\n[4/4] Post-processing exports...")
    exports = post_processor.process(
        raw_video_path=raw_video_path,
        concept_slug=concept_slug,
        add_lower_third=add_lower_third,
        add_music=add_music,
    )

    result = {
        "concept_slug":    concept_slug,
        "word_count":      script_result["word_count"],
        "estimated_secs":  script_result["estimated_secs"],
        "audio_path":      audio_path,
        "raw_video_path":  raw_video_path,
        "exports":         exports,
        "warnings":        script_result["warnings"],
        "completed_at":    datetime.utcnow().isoformat() + "Z",
    }

    print(f"\n{'='*60}")
    print(f"  ✓  Done: {concept_slug}")
    for fmt, path in exports.items():
        print(f"     {fmt:10s} → {path}")
    print(f"{'='*60}\n")

    return result


# ── CLI entrypoint ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Digital Wellness Podcast Video Agent"
    )
    parser.add_argument(
        "--script", required=True,
        help="Path to script .txt file (or pass '-' to read from stdin)"
    )
    parser.add_argument(
        "--image", required=True,
        help="Path to Nicole's portrait image (.jpg/.png)"
    )
    parser.add_argument(
        "--concept", required=True,
        help="Short concept slug for filenames, e.g. glp1-muscle-loss"
    )
    parser.add_argument(
        "--target-seconds", type=int, default=60,
        help="Target video length in seconds (for script length warning)"
    )
    parser.add_argument(
        "--no-lower-third", action="store_true",
        help="Skip burning in name/title lower-third overlay"
    )
    parser.add_argument(
        "--no-music", action="store_true",
        help="Skip background music mixing"
    )
    parser.add_argument(
        "--use-fallback-model", action="store_true",
        help="Use Kling Avatar (15s max) instead of InfiniteTalk (for testing)"
    )
    parser.add_argument(
        "--output-json",
        help="Optional path to save the result JSON"
    )
    args = parser.parse_args()

    # Read script
    if args.script == "-":
        script_text = sys.stdin.read()
    else:
        script_text = Path(args.script).read_text(encoding="utf-8")

    result = run(
        script_text=script_text,
        image_path=args.image,
        concept_slug=args.concept,
        target_seconds=args.target_seconds,
        add_lower_third=not args.no_lower_third,
        add_music=not args.no_music,
        use_fallback_model=args.use_fallback_model,
    )

    if args.output_json:
        Path(args.output_json).write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )
        print(f"Result saved to: {args.output_json}")

    return result


if __name__ == "__main__":
    main()
