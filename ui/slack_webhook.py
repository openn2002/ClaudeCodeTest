"""
Slack Interactive Webhook Server
==================================
Receives button-click payloads from Slack Block Kit messages and
updates the marketing database accordingly.

Run alongside the Streamlit app:
    python ui/slack_webhook.py

Then set your Slack App's Interactivity Request URL to:
    https://your-domain.com/slack/actions

Requires:
    SLACK_SIGNING_SECRET  — from your Slack App settings
    SLACK_BOT_TOKEN       — from your Slack App OAuth settings
"""

import hashlib
import hmac
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

try:
    from fastapi import FastAPI, Request, Response, HTTPException
    from fastapi.responses import JSONResponse
    import uvicorn
    _FASTAPI_AVAILABLE = True
except ImportError:
    _FASTAPI_AVAILABLE = False

import sys
sys.path.insert(0, str(Path(__file__).parent))

from modules.marketing_db import (
    update_recommendation_status, snooze_recommendation,
    get_pending_recommendations,
)

SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")


def _verify_slack_signature(body: bytes, timestamp: str, signature: str) -> bool:
    """Verify the request is genuinely from Slack."""
    if not SIGNING_SECRET:
        return True  # Skip verification in development if secret not set
    if abs(time.time() - int(timestamp)) > 300:
        return False  # Replay attack protection
    base = f"v0:{timestamp}:{body.decode('utf-8')}"
    expected = "v0=" + hmac.new(
        SIGNING_SECRET.encode(), base.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


if _FASTAPI_AVAILABLE:
    app = FastAPI(title="Digital Wellness — Slack Webhook")

    @app.post("/slack/actions")
    async def slack_actions(request: Request):
        """Handle Slack interactive component payloads (button clicks)."""
        body = await request.body()

        # Verify signature
        timestamp = request.headers.get("X-Slack-Request-Timestamp", "0")
        signature = request.headers.get("X-Slack-Signature", "")
        if not _verify_slack_signature(body, timestamp, signature):
            raise HTTPException(status_code=401, detail="Invalid Slack signature")

        # Parse payload
        form_data = await request.form()
        raw_payload = form_data.get("payload", "{}")
        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid payload JSON")

        actions = payload.get("actions", [])
        user = payload.get("user", {}).get("name", "unknown")

        for action in actions:
            action_id = action.get("action_id", "")
            value = action.get("value", "")

            # Approve a single recommendation
            if action_id == "approve_recommendation" and value.isdigit():
                update_recommendation_status(int(value), "approved",
                                             notes=f"Approved via Slack by {user}")

            # Reject a single recommendation
            elif action_id == "reject_recommendation" and value.isdigit():
                update_recommendation_status(int(value), "rejected",
                                             notes=f"Rejected via Slack by {user}")

            # Snooze a single recommendation
            elif action_id in ("snooze_recommendation", "snooze_all"):
                if value.isdigit():
                    snooze_recommendation(int(value), hours=48)
                elif value == "snooze_48":
                    # Snooze all pending recommendations
                    recs = get_pending_recommendations()
                    for rec in recs:
                        snooze_recommendation(rec["id"], hours=48)

            # Approve all pending recommendations
            elif action_id == "approve_all_pending":
                recs = get_pending_recommendations()
                for rec in recs:
                    update_recommendation_status(
                        rec["id"], "approved",
                        notes=f"Bulk approved via Slack by {user}"
                    )

        # Slack requires a 200 response within 3 seconds
        return JSONResponse({"ok": True})

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "digital-wellness-slack-webhook"}


def main():
    if not _FASTAPI_AVAILABLE:
        print("FastAPI and uvicorn are required to run the webhook server.")
        print("Install with: pip install fastapi uvicorn")
        return

    port = int(os.getenv("SLACK_WEBHOOK_PORT", "8502"))
    print(f"Starting Slack webhook server on port {port}")
    print(f"Set your Slack App Interactivity URL to: http://your-domain:{port}/slack/actions")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
