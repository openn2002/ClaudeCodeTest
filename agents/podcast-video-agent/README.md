# Digital Wellness — Podcast Video Agent

Turns a written podcast script into a branded AI talking-head video,
using Segmind (Higgsfield lipsync) and ElevenLabs for voice.

---

## How It Works

```
Script text (.txt)
    │
    ▼
[1] ScriptProcessor   ── strips notes, validates length, estimates duration
    │
    ▼
[2] TTSGenerator       ── ElevenLabs (cloned voice) → voiceover.mp3
    │
    ▼
[3] HiggsfieldClient  ── portrait.jpg + voiceover.mp3 → Segmind API → raw_video.mp4
    │
    ▼
[4] PostProcessor      ── ffmpeg: crop/pad to 9:16 / 16:9 / 1:1 + lower-third + music
    │
    ▼
Output: concept-name_reels.mp4   ← drop this into Captions.AI for final captions/edits
        concept-name_youtube.mp4
        concept-name_square.mp4
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
# Also requires ffmpeg on PATH:
# macOS:  brew install ffmpeg
# Ubuntu: apt-get install ffmpeg
```

### 2. Set environment variables

Copy these into `.env` in the repo root:

```bash
# Video generation — Segmind (pay-per-use, ~$0.86/video, no subscription)
# Get a free API key at: https://www.segmind.com/
SEGMIND_API_KEY="your-segmind-api-key"

# Voice — ElevenLabs (clone your voice first, see step 3 below)
# Get a key at: https://elevenlabs.io
ELEVENLABS_API_KEY="your-elevenlabs-api-key"
ELEVENLABS_VOICE_ID="your-cloned-voice-id"

# Optional: background music to mix under the voiceover
BG_MUSIC_PATH="/path/to/background_track.mp3"
```

### 3. Clone your voice in ElevenLabs (one-time setup)

1. Go to [elevenlabs.io](https://elevenlabs.io) → **Voices** → **Add Voice** → **Instant Voice Clone**
2. Upload 1–5 minutes of clean audio of yourself (no background noise)
3. Copy the **Voice ID** from the dashboard
4. Paste it as `ELEVENLABS_VOICE_ID` in `.env`

### 4. Prepare a portrait photo

Supply a portrait image each time you run — `.jpg` or `.png`, good lighting,
front-facing. Pass it via `--image`. Change it whenever you like.

---

## Usage

### CLI

```bash
python agent.py \
  --script  scripts/glp1_muscle_loss.txt \
  --image   /path/to/your_portrait.jpg \
  --concept glp1-muscle-loss \
  --target-seconds 60
```

### Python

```python
from agent import run

result = run(
    script_text=open("scripts/glp1_muscle_loss.txt").read(),
    image_path="/path/to/your_portrait.jpg",
    concept_slug="glp1-muscle-loss",
    target_seconds=60,
)

print(result["exports"])
# {"reels": "output/glp1-muscle-loss_reels.mp4", ...}
```

---

## Output Files

| File | Format | Use |
|------|--------|-----|
| `{concept}_reels.mp4`     | 1080×1920 (9:16) | Drop into Captions.AI → TikTok / Instagram Reels |
| `{concept}_youtube.mp4`   | 1920×1080 (16:9) | YouTube |
| `{concept}_square.mp4`    | 1080×1080 (1:1)  | Facebook |
| `{concept}_raw.mp4`       | Original output  | Archive |
| `{concept}_voiceover.mp3` | Audio only       | Archive |

---

## Cost per Video

Segmind pricing for **Kling V2 Pro Avatar** is per-second of output video.

| Service | Cost |
|---------|------|
| Segmind — Kling V2 Pro Avatar | ~$6.40 per ~47s video (~$0.136/s) |
| ElevenLabs TTS | ~$0.30 per 30s script (Creator plan) |
| ffmpeg | Free |
| **Total (60s video)** | **~$8–9/video** |

> **Note:** For high-volume use, the Higgsfield Creator plan ($149/mo) becomes
> cost-effective at ~20+ videos/month. Segmind is best for low-volume testing.

---

## Script Length Guidelines

| Format | Target length | ~Word count |
|--------|--------------|-------------|
| TikTok / Reels | 30–60s | 70–140 words |
| YouTube Short | 60s | ~140 words |
| Long-form segment | 3–5 min | 420–700 words |

---

## Advanced: Direct Higgsfield SDK (optional)

If you later want unlimited video length via the InfiniteTalk model (requires
Higgsfield Creator plan at $149/mo), set:

```bash
HIGGSFIELD_BACKEND="higgsfield"
HF_KEY="your-key-id:your-key-secret"
```

Segmind is recommended for normal use — same quality, no subscription.
