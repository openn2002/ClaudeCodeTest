"""
Analysis Runner — CSIRO TWD AU
================================
Run from the command line to trigger an analysis cycle:

    python analysis/run_analysis.py --type daily
    python analysis/run_analysis.py --type weekly
    python analysis/run_analysis.py --type monthly
    python analysis/run_analysis.py --type daily --slack

The runner:
  1. Pulls metrics from the DB (or live via MCP if configured)
  2. Runs the fatigue detector against benchmark thresholds
  3. Generates copy recommendations via Claude sub-agents
  4. Logs everything to memory
  5. Optionally sends a Slack digest

When credentials are available, pass --live to pull from Meta Ads API instead of DB.
"""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ui"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from ui.modules.marketing_db import (
    init_db, get_ads_with_metrics, get_kpis, get_pending_recommendations,
    update_recommendation_status, log_memory, log_analysis_run,
)
from ui.modules.mock_data import BENCHMARKS, seed_mock_data
from ui.modules.slack_client import send_daily_digest, send_weekly_summary, slack_available

BENCHMARK_CONFIG = json.loads((ROOT / "analysis" / "benchmark_config.json").read_text())


# ── Fatigue detection ─────────────────────────────────────────────────────────

def classify_ad(ad: dict) -> str:
    """Return FATIGUED | WATCH | HEALTHY."""
    ctr = ad.get("ctr") or 0
    freq = ad.get("frequency") or 0
    cpm = ad.get("cpm") or 0
    cpa = ad.get("cpa") or 9999

    if freq >= BENCHMARKS["frequency_bad"] or ctr < 0.8:
        return "FATIGUED"
    if (freq >= BENCHMARKS["frequency_warn"] or ctr < BENCHMARKS["ctr_warn"]
            or cpm > BENCHMARKS["cpm_warn"] or cpa > BENCHMARKS["cpa_warn"]):
        return "WATCH"
    return "HEALTHY"


def detect_issues(days: int = 7) -> tuple[list, list]:
    """Return (fatigued_ads, watch_ads)."""
    ads = [dict(a) for a in get_ads_with_metrics(days)]
    fatigued, watch = [], []
    for a in ads:
        status = classify_ad(a)
        a["fatigue_status"] = status
        if status == "FATIGUED":
            fatigued.append(a)
        elif status == "WATCH":
            watch.append(a)
    return fatigued, watch


# ── Copy generation (Claude API) ──────────────────────────────────────────────

def generate_copy_recommendations(fatigued_ads: list, memory_context: list) -> list:
    """
    Call Claude to generate copy recommendations for fatigued ads.
    Uses two sub-agents: one for headlines, one for body copy.
    Returns a list of recommendation dicts ready to insert into the DB.
    """
    try:
        import anthropic
    except ImportError:
        print("anthropic package not installed — skipping copy generation")
        return []

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ANTHROPIC_API_KEY not set — skipping copy generation")
        return []

    client = anthropic.Anthropic(api_key=api_key)

    # Build memory context string
    memory_lines = "\n".join(
        f"- {m.get('analysis_date', '')}: {m.get('hypothesis', '')} → {m.get('status', '')}"
        for m in (memory_context or [])[:10]
    )

    headline_agent_prompt = (ROOT / "agents" / "headline_agent.md").read_text()
    description_agent_prompt = (ROOT / "agents" / "description_agent.md").read_text()

    recommendations = []

    for ad in fatigued_ads:
        ad_context = (
            f"Ad name: {ad['name']}\n"
            f"Current headline: {ad.get('headline', 'Unknown')}\n"
            f"Current body: {ad.get('primary_text', 'Unknown')}\n"
            f"CTR: {ad.get('ctr')}% (benchmark: {BENCHMARKS['ctr_good']}%)\n"
            f"Frequency: {ad.get('frequency')}x\n"
            f"CPM: ${ad.get('cpm')} AUD\n"
            f"CPA: ${ad.get('cpa')} AUD\n"
            f"Campaign: {ad.get('campaign_name', 'Unknown')}\n\n"
            f"Recent memory/outcomes:\n{memory_lines or 'None'}"
        )

        # Headline sub-agent
        try:
            hl_response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=512,
                system=headline_agent_prompt,
                messages=[{"role": "user", "content": ad_context}],
            )
            headline_text = hl_response.content[0].text.strip()
            recommendations.append({
                "ad_id": ad["id"],
                "type": "new_headline",
                "current_value": ad.get("headline"),
                "recommended_value": headline_text,
                "reason": f"CTR {ad.get('ctr')}% below benchmark {BENCHMARKS['ctr_good']}%. "
                          f"Frequency {ad.get('frequency')}x — creative fatigue detected.",
            })
        except Exception as e:
            print(f"  Headline generation failed for {ad['name']}: {e}")

        # Description sub-agent
        try:
            desc_response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=description_agent_prompt,
                messages=[{"role": "user", "content": ad_context}],
            )
            desc_text = desc_response.content[0].text.strip()
            recommendations.append({
                "ad_id": ad["id"],
                "type": "new_primary_text",
                "current_value": ad.get("primary_text"),
                "recommended_value": desc_text,
                "reason": f"Creative fatigue — CTR {ad.get('ctr')}%, Frequency {ad.get('frequency')}x.",
            })
        except Exception as e:
            print(f"  Description generation failed for {ad['name']}: {e}")

    return recommendations


def _insert_recommendations(recs: list):
    """Write generated recommendations to the DB."""
    import sqlite3
    from ui.modules.marketing_db import get_conn
    with get_conn() as conn:
        for r in recs:
            conn.execute("""
                INSERT INTO recommendations
                    (ad_id, type, current_value, recommended_value, reason, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            """, (r["ad_id"], r["type"], r.get("current_value"),
                  r.get("recommended_value"), r.get("reason")))


# ── Main analysis flow ────────────────────────────────────────────────────────

def run_daily(send_slack: bool = False):
    print("Running daily analysis...")
    fatigued, watch = detect_issues(7)
    kpis = get_kpis(7)
    pending_recs = get_pending_recommendations()

    print(f"  Fatigued ads : {len(fatigued)}")
    print(f"  Watch ads    : {len(watch)}")
    print(f"  Pending recs : {len(pending_recs)}")

    # Generate copy recommendations for fatigued ads
    if fatigued:
        print(f"  Generating copy for {len(fatigued)} fatigued ad(s)...")
        from ui.modules.marketing_db import get_memory_log
        memory = [dict(m) for m in get_memory_log(20)]
        recs = generate_copy_recommendations(fatigued, memory)
        if recs:
            _insert_recommendations(recs)
            print(f"  Generated {len(recs)} copy recommendation(s)")

    # Log to memory
    log_memory(
        str(date.today()), None,
        f"Daily: {len(fatigued)} fatigued, {len(watch)} watch. "
        f"KPIs — CTR: {kpis.get('avg_ctr')}%, CPA: ${kpis.get('avg_cpa')}, "
        f"Spend: ${kpis.get('total_spend')}",
        status="confirmed",
    )
    log_analysis_run(
        "daily", f"{len(fatigued)} fatigued, {len(watch)} watch",
        len(fatigued), len(watch),
        len([r for r in generate_copy_recommendations.__doc__ or "" if r]) if fatigued else 0,
        slack_sent=False,
    )

    if send_slack and slack_available():
        ok, msg = send_daily_digest(kpis, fatigued, len(list(pending_recs)))
        print(f"  Slack daily digest: {'sent' if ok else f'failed — {msg}'}")

    print("Daily analysis complete.")


def run_weekly(send_slack: bool = False):
    print("Running weekly analysis...")
    fatigued, watch = detect_issues(7)
    kpis_7d = get_kpis(7)
    kpis_prev = get_kpis(14)

    from ui.modules.marketing_db import get_ads_with_metrics
    ads = [dict(a) for a in get_ads_with_metrics(7)]
    top = sorted(ads, key=lambda x: x.get("ctr") or 0, reverse=True)[:3]
    bottom = sorted(ads, key=lambda x: x.get("ctr") or 0)[:3]

    print(f"  This week spend: ${kpis_7d.get('total_spend')}")
    print(f"  This week CTR  : {kpis_7d.get('avg_ctr')}%")
    print(f"  This week CPA  : ${kpis_7d.get('avg_cpa')}")

    log_memory(
        str(date.today()), None,
        f"Weekly review: Spend ${kpis_7d.get('total_spend')}, CTR {kpis_7d.get('avg_ctr')}%, "
        f"CPA ${kpis_7d.get('avg_cpa')}. Top ad: {top[0]['name'] if top else '—'}",
        status="confirmed",
    )
    log_analysis_run(
        "weekly", f"Weekly: CTR {kpis_7d.get('avg_ctr')}%, CPA ${kpis_7d.get('avg_cpa')}",
        len(fatigued), len(watch), 0, slack_sent=False,
    )

    if send_slack and slack_available():
        ok, msg = send_weekly_summary(kpis_7d, kpis_prev, top, bottom)
        print(f"  Slack weekly summary: {'sent' if ok else f'failed — {msg}'}")

    print("Weekly analysis complete.")


def run_monthly(send_slack: bool = False):
    print("Running monthly analysis...")
    kpis_30d = get_kpis(30)
    fatigued, watch = detect_issues(30)

    from ui.modules.marketing_db import get_memory_log
    memory = [dict(m) for m in get_memory_log(50)]
    confirmed = [m for m in memory if m.get("status") == "confirmed"]
    hypotheses = [m for m in memory if m.get("status") == "hypothesis"]

    print(f"  30-day spend: ${kpis_30d.get('total_spend')}")
    print(f"  30-day CTR  : {kpis_30d.get('avg_ctr')}%")
    print(f"  Memory: {len(confirmed)} confirmed findings, {len(hypotheses)} open hypotheses")

    log_analysis_run(
        "monthly",
        f"Monthly: Spend ${kpis_30d.get('total_spend')}, "
        f"CTR {kpis_30d.get('avg_ctr')}%, {len(fatigued)} fatigued",
        len(fatigued), len(watch), 0, slack_sent=False,
    )
    print("Monthly analysis complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run marketing analysis")
    parser.add_argument(
        "--type", choices=["daily", "weekly", "monthly"], default="daily",
        help="Analysis type to run",
    )
    parser.add_argument(
        "--slack", action="store_true",
        help="Send Slack digest after analysis",
    )
    args = parser.parse_args()

    init_db()
    seed_mock_data()

    if args.type == "daily":
        run_daily(send_slack=args.slack)
    elif args.type == "weekly":
        run_weekly(send_slack=args.slack)
    elif args.type == "monthly":
        run_monthly(send_slack=args.slack)
