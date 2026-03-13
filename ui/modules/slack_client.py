"""
Slack client — builds and sends Block Kit messages
===================================================
Requires SLACK_BOT_TOKEN and SLACK_CHANNEL_ID in .env
"""

import os
import json
from datetime import date

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    _SLACK_AVAILABLE = True
except ImportError:
    _SLACK_AVAILABLE = False


def _client():
    token = os.getenv("SLACK_BOT_TOKEN", "")
    if not token:
        raise ValueError("SLACK_BOT_TOKEN not set in .env")
    return WebClient(token=token)


def _channel():
    return os.getenv("SLACK_CHANNEL_ID", "#marketing-alerts")


def slack_available() -> bool:
    return _SLACK_AVAILABLE and bool(os.getenv("SLACK_BOT_TOKEN"))


def _fatigue_emoji(status: str) -> str:
    return {"healthy": "✅", "watch": "⚠️", "fatigued": "🔴"}.get(status, "❓")


def send_daily_digest(kpis: dict, fatigued_ads: list, pending_recs: int,
                      webhook_base_url: str = ""):
    """
    Send the daily morning digest to Slack.
    fatigued_ads: list of dicts with keys id, name, campaign_name, ctr, frequency
    """
    if not slack_available():
        return False, "Slack not configured (SLACK_BOT_TOKEN missing)"

    today = date.today().strftime("%A %-d %B %Y")
    spend = kpis.get("total_spend") or 0
    ctr = kpis.get("avg_ctr") or 0
    cpm = kpis.get("avg_cpm") or 0
    cpa = kpis.get("avg_cpa") or 0

    fatigue_lines = ""
    for ad in fatigued_ads[:5]:
        fatigue_lines += (
            f"• *{ad['name']}* — CTR {ad['ctr']}%, Freq {ad['frequency']}x "
            f"_(campaign: {ad['campaign_name']})_\n"
        )

    if not fatigue_lines:
        fatigue_lines = "_No fatigued ads today_ ✅"

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"📊 CSIRO TWD — Daily Digest — {today}"},
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*Last 7 days performance (AU — Meta)*\n"
                    f"💰 Spend: *${spend:,.2f} AUD*   "
                    f"📈 CTR: *{ctr}%*   "
                    f"💡 CPM: *${cpm}*   "
                    f"🎯 CPA: *${cpa}*"
                ),
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🔴 Fatigued / Underperforming Ads ({len(fatigued_ads)})*\n{fatigue_lines}",
            },
        },
    ]

    if pending_recs > 0:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📝 Copy Recommendations Awaiting Review:* {pending_recs}",
            },
        })

    # Action buttons
    actions = {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "View Dashboard"},
                "style": "primary",
                "url": webhook_base_url or "http://localhost:8501",
                "action_id": "view_dashboard",
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Approve All Pending"},
                "style": "primary",
                "action_id": "approve_all_pending",
                "value": "approve_all",
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Snooze 48h"},
                "action_id": "snooze_all",
                "value": "snooze_48",
            },
        ],
    }
    blocks.append(actions)

    try:
        _client().chat_postMessage(
            channel=_channel(),
            blocks=blocks,
            text=f"Daily digest — {len(fatigued_ads)} fatigued ads, {pending_recs} recommendations pending",
        )
        return True, "Sent"
    except Exception as e:
        return False, str(e)


def send_weekly_summary(kpis_7d: dict, kpis_prev_7d: dict, top_ads: list,
                        bottom_ads: list, webhook_base_url: str = ""):
    """Weekly performance summary with week-over-week comparison."""
    if not slack_available():
        return False, "Slack not configured"

    def pct_change(new, old):
        if not old or old == 0:
            return "—"
        chg = ((new - old) / old) * 100
        arrow = "⬆️" if chg > 0 else "⬇️"
        return f"{arrow} {abs(chg):.1f}%"

    spend_change = pct_change(kpis_7d.get("total_spend", 0), kpis_prev_7d.get("total_spend", 0))
    ctr_change = pct_change(kpis_7d.get("avg_ctr", 0), kpis_prev_7d.get("avg_ctr", 0))
    cpa_change = pct_change(kpis_7d.get("avg_cpa", 0), kpis_prev_7d.get("avg_cpa", 0))

    top_lines = "\n".join(
        f"• *{a['name']}* — CTR {a['ctr']}%, CPA ${a['cpa']}, Spend ${a['spend']}"
        for a in (top_ads or [])[:3]
    )
    bottom_lines = "\n".join(
        f"• *{a['name']}* — CTR {a['ctr']}%, CPA ${a['cpa']}, Spend ${a['spend']}"
        for a in (bottom_ads or [])[:3]
    )

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "📊 CSIRO TWD — Weekly Summary (AU — Meta)"},
        },
        {"type": "divider"},
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Spend:* ${kpis_7d.get('total_spend', 0):,.2f}\n_{spend_change} WoW_"},
                {"type": "mrkdwn", "text": f"*Avg CTR:* {kpis_7d.get('avg_ctr', 0)}%\n_{ctr_change} WoW_"},
                {"type": "mrkdwn", "text": f"*Avg CPM:* ${kpis_7d.get('avg_cpm', 0)}\n_—_"},
                {"type": "mrkdwn", "text": f"*Avg CPA:* ${kpis_7d.get('avg_cpa', 0)}\n_{cpa_change} WoW_"},
            ],
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*🏆 Top Performers*\n{top_lines or '_No data_'}"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*📉 Underperformers*\n{bottom_lines or '_No data_'}"},
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "View Full Report"},
                    "style": "primary",
                    "url": webhook_base_url or "http://localhost:8501",
                    "action_id": "view_weekly",
                },
            ],
        },
    ]

    try:
        _client().chat_postMessage(
            channel=_channel(),
            blocks=blocks,
            text="Weekly performance summary — CSIRO TWD AU Meta Ads",
        )
        return True, "Sent"
    except Exception as e:
        return False, str(e)


def send_recommendation_notification(ad_name: str, rec_type: str, recommended_value: str,
                                      rec_id: int, webhook_base_url: str = ""):
    """Notify Slack of a new copy recommendation with inline approve/reject buttons."""
    if not slack_available():
        return False, "Slack not configured"

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*💡 New Copy Recommendation*\n"
                    f"Ad: *{ad_name}*\n"
                    f"Type: `{rec_type}`\n"
                    f"Suggested: _{recommended_value}_"
                ),
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "✓ Approve"},
                    "style": "primary",
                    "action_id": "approve_recommendation",
                    "value": str(rec_id),
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "✗ Reject"},
                    "style": "danger",
                    "action_id": "reject_recommendation",
                    "value": str(rec_id),
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "⏸ Snooze 48h"},
                    "action_id": "snooze_recommendation",
                    "value": str(rec_id),
                },
            ],
        },
    ]

    try:
        _client().chat_postMessage(
            channel=_channel(),
            blocks=blocks,
            text=f"New recommendation for {ad_name}: {recommended_value[:80]}",
        )
        return True, "Sent"
    except Exception as e:
        return False, str(e)
