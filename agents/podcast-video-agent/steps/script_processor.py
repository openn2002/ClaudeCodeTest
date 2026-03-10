"""
Step 1 — ScriptProcessor

Takes a raw podcast script and prepares it for TTS:
  • Strips stage directions and notes
  • Estimates reading time
  • Warns if script is too long for a short-form video
  • Returns clean, audio-ready text
"""

import re


# Average speaking pace for a measured, warm podcast voice (words per minute)
SPEAKING_WPM = 140


def process(script: str, target_seconds: int = 60) -> dict:
    """
    Clean and validate a podcast script for TTS.

    Args:
        script:         Raw script text (may contain [stage notes], *emphasis*, etc.)
        target_seconds: Target video length in seconds (default 60s for short-form)

    Returns:
        dict with keys:
            clean_text      — TTS-ready string
            word_count      — int
            estimated_secs  — float
            warnings        — list[str]
    """
    warnings = []

    # Remove content inside square brackets (stage directions / notes)
    # e.g. [pause], [smile], [cut to B-roll]
    clean = re.sub(r'\[.*?\]', '', script)

    # Remove markdown emphasis (*bold*, _italic_)
    clean = re.sub(r'[*_]{1,2}(.+?)[*_]{1,2}', r'\1', clean)

    # Collapse multiple spaces / newlines into single spaces
    clean = re.sub(r'\s+', ' ', clean).strip()

    # Estimate reading time
    word_count     = len(clean.split())
    estimated_secs = (word_count / SPEAKING_WPM) * 60

    if estimated_secs > target_seconds * 1.1:
        warnings.append(
            f"Script is ~{estimated_secs:.0f}s at {SPEAKING_WPM} WPM — "
            f"target is {target_seconds}s. Consider trimming."
        )

    if word_count < 10:
        warnings.append("Script is very short — check input.")

    return {
        "clean_text":     clean,
        "word_count":     word_count,
        "estimated_secs": round(estimated_secs, 1),
        "warnings":       warnings,
    }
