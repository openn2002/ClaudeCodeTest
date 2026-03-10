# Digital Wellness — Podcast Video Agent

Turns a written podcast script into a branded AI talking-head video of Nicole,
using Higgsfield's `InfiniteTalk` model for lip-sync and ElevenLabs for voice.

---

## How It Works

```
Script text (.txt)
    │
    ▼
[1] ScriptProcessor   ── strips notes, validates length, estimates duration
    │
    ▼
[2] TTSGenerator       ── ElevenLabs (Nicole's cloned voice) → voiceover.mp3
    │
    ▼
[3] HiggsfieldClient  ── nicole.jpg + voiceover.mp3 → InfiniteTalk → raw_video.mp4
    │
    ▼
[4] PostProcessor      ── ffmpeg: crop/pad + lower-third + background music
    │
    ▼
Output: concept-name_reels.mp4 (9:16)
        concept-name_youtube.mp4 (16:9)
        concept-name_square.mp4 (1:1)
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

```bash
# Higgsfield (Creator plan required for API — $149/mo)
export HF_KEY="your-key-id:your-key-secret"

# ElevenLabs (recommended — clone Nicole's voice first)
export ELEVENLABS_API_KEY="your-elevenlabs-key"
export ELEVENLABS_VOICE_ID="your-nicole-voice-id"

# Optional: OpenAI TTS as fallback (no voice cloning)
export TTS_PROVIDER="openai"
export OPENAI_API_KEY="your-openai-key"

# Optional: background music
export BG_MUSIC_PATH="/path/to/background_track.mp3"
```

### 3. Clone Nicole's voice in ElevenLabs (one-time setup)

1. Go to [elevenlabs.io](https://elevenlabs.io) → **Voices** → **Add Voice** → **Instant Voice Clone**
2. Upload 1–5 minutes of clean Nicole audio (no background noise)
3. Copy the Voice ID from the dashboard
4. Set `ELEVENLABS_VOICE_ID` to that ID

---

## Usage

### CLI

```bash
python agent.py \
  --script  scripts/glp1_muscle_loss.txt \
  --image   assets/nicole_portrait.jpg \
  --concept glp1-muscle-loss \
  --target-seconds 60
```

### Python

```python
from agent import run

result = run(
    script_text=open("scripts/glp1_muscle_loss.txt").read(),
    image_path="assets/nicole_portrait.jpg",
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
| `{concept}_reels.mp4`   | 1080×1920 (9:16) | TikTok, Instagram Reels |
| `{concept}_youtube.mp4` | 1920×1080 (16:9) | YouTube, horizontal |
| `{concept}_square.mp4`  | 1080×1080 (1:1)  | Facebook |
| `{concept}_raw.mp4`     | Original Higgsfield output | Archive |
| `{concept}_voiceover.mp3` | Audio only | Archive |

---

## Key Notes

### Higgsfield Model: InfiniteTalk
- **Input:** portrait image + audio file
- **Output:** lip-synced talking-head video of any length
- **API access:** requires Creator plan ($149/mo) at [cloud.higgsfield.ai](https://cloud.higgsfield.ai)
- **Alternative:** [Segmind pay-per-generation](https://www.segmind.com/models/higgsfield-speech2video) (no subscription needed — good for prototyping)

### Model Paths
The exact model path strings for `InfiniteTalk` and `Kling AI Avatar` need to be
confirmed in your Higgsfield Cloud dashboard — the API uses the same SDK pattern
for all models, only the path string changes. Update `config.py` once confirmed.

### Script Length Guidelines
| Video type | Target length | ~Word count |
|---|---|---|
| Short-form (TikTok/Reels) | 30–60s | 70–140 words |
| YouTube Short | 60s | ~140 words |
| Long-form segment | 3–5 min | 420–700 words |

---

## Cost Estimate (per video)

| Service | Cost |
|---|---|
| Higgsfield Creator plan | $149/mo (covers ~6,000 credits) |
| ElevenLabs (voice cloning + TTS) | ~$0.30 per 30s script (Creator plan) |
| ffmpeg | Free |
| **Total per video** | **~$0.30 + Higgsfield credits** |

For low-volume testing, the Segmind pay-per-generation route for Higgsfield
avoids the $149/mo commitment.
