"""
Ad Performance tab — Streamlit UI module
=========================================
Renders the full Marketing Analytics section:
  - Overview: KPIs, spend trend, campaign table
  - Creative: ad-level fatigue + copy recommendations
  - Memory: hypothesis log
  - Analysis: run analysis, send Slack digests
"""

import json
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

from .marketing_db import (
    init_db, get_kpis, get_ads_with_metrics, get_spend_trend,
    get_campaigns, get_pending_recommendations, get_recommendation_history,
    update_recommendation_status, snooze_recommendation, log_memory,
    get_memory_log, log_analysis_run,
)
from .mock_data import seed_mock_data, BENCHMARKS
from .slack_client import (
    send_daily_digest, send_weekly_summary, slack_available,
)

ROOT = Path(__file__).parent.parent.parent


# ── Helpers ───────────────────────────────────────────────────────────────────

def _delta_color(value, benchmark_good, benchmark_warn, higher_is_better=True):
    """Return 'normal' | 'inverse' for st.metric delta_color."""
    if higher_is_better:
        if value >= benchmark_good:
            return "normal"
        return "inverse"
    else:
        if value <= benchmark_good:
            return "normal"
        return "inverse"


def _fatigue_badge(ctr, frequency, cpm):
    if frequency >= BENCHMARKS["frequency_bad"] or ctr < 0.8:
        return "🔴 Fatigued"
    if frequency >= BENCHMARKS["frequency_warn"] or ctr < BENCHMARKS["ctr_warn"]:
        return "⚠️  Watch"
    return "✅ Healthy"


def _vs_benchmark(value, good, warn, higher_is_better=True, prefix="", suffix=""):
    """Return coloured benchmark comparison string."""
    if value is None:
        return "—"
    if higher_is_better:
        ok = value >= good
        mid = value >= warn
    else:
        ok = value <= good
        mid = value <= warn
    color = "green" if ok else ("orange" if mid else "red")
    benchmark_label = f"benchmark: {prefix}{good}{suffix}"
    return f":{color}[{prefix}{value}{suffix}] _{benchmark_label}_"


# ── Main render function ──────────────────────────────────────────────────────

def render_ad_performance_tab():
    # Ensure DB exists and is seeded with mock data
    init_db()
    seed_mock_data()

    st.header("Ad Performance — CSIRO TWD AU (Meta)")
    st.caption(
        "Live campaign analytics, creative fatigue detection, and copy recommendations. "
        "Connects to Meta Ads API when credentials are configured. "
        "Currently showing mock data — add credentials in Settings below."
    )

    sub = st.tabs(["📊 Overview", "🎨 Creative", "🧠 Memory", "⚙️ Analysis & Settings"])

    with sub[0]:
        _render_overview()

    with sub[1]:
        _render_creative()

    with sub[2]:
        _render_memory()

    with sub[3]:
        _render_settings()


# ── Overview tab ─────────────────────────────────────────────────────────────

def _render_overview():
    st.subheader("Performance Overview")

    period = st.radio(
        "Period", ["Last 7 days", "Last 14 days", "Last 30 days"],
        horizontal=True, key="overview_period",
    )
    days_map = {"Last 7 days": 7, "Last 14 days": 14, "Last 30 days": 30}
    days = days_map[period]

    kpis = get_kpis(days)
    kpis_prev = get_kpis(days * 2)  # rough prior period

    def _delta(current_key, prev_dict, key, higher_is_better=True, fmt="{:.1f}"):
        curr = kpis.get(current_key) or 0
        prev = (prev_dict.get(key) or 0)
        if prev == 0:
            return None
        chg = ((curr - prev) / prev) * 100
        sign = "+" if chg > 0 else ""
        return f"{sign}{chg:.1f}% WoW"

    # KPI row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric(
            "Total Spend (AUD)",
            f"${kpis.get('total_spend') or 0:,.2f}",
            delta=_delta("total_spend", kpis_prev, "total_spend"),
        )
    with c2:
        ctr = kpis.get("avg_ctr") or 0
        benchmark_ctr = BENCHMARKS["ctr_good"]
        st.metric(
            "Avg CTR",
            f"{ctr}%",
            delta=f"benchmark {benchmark_ctr}%",
            delta_color="off",
        )
    with c3:
        cpm = kpis.get("avg_cpm") or 0
        st.metric("Avg CPM (AUD)", f"${cpm}")
    with c4:
        cpa = kpis.get("avg_cpa") or 0
        st.metric("Avg CPA (AUD)", f"${cpa}")
    with c5:
        roas = kpis.get("avg_roas") or 0
        st.metric("Avg ROAS", f"{roas}x")

    st.divider()

    # Benchmark comparison bar
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        ctr_status = "✅ Above benchmark" if ctr >= BENCHMARKS["ctr_good"] else (
            "⚠️ Below benchmark" if ctr >= BENCHMARKS["ctr_warn"] else "🔴 Well below benchmark"
        )
        st.info(f"**CTR** {ctr_status}  \nIndustry avg (health/wellness AU): {BENCHMARKS['ctr_good']}%")
    with b_col2:
        cpm_status = "✅ Efficient" if cpm <= BENCHMARKS["cpm_good"] else (
            "⚠️ Elevated" if cpm <= BENCHMARKS["cpm_warn"] else "🔴 High CPM"
        )
        st.info(f"**CPM** {cpm_status}  \nBenchmark: <${BENCHMARKS['cpm_good']} AUD")
    with b_col3:
        cpa_status = "✅ Strong" if (cpa or 9999) <= BENCHMARKS["cpa_good"] else (
            "⚠️ Above target" if (cpa or 9999) <= BENCHMARKS["cpa_warn"] else "🔴 High CPA"
        )
        st.info(f"**CPA** {cpa_status}  \nTarget: <${BENCHMARKS['cpa_good']} AUD")

    st.divider()

    # Spend trend chart
    st.subheader("Spend Trend")
    trend = get_spend_trend(days)
    if trend:
        try:
            import pandas as pd
            df = pd.DataFrame([dict(r) for r in trend])
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")
            st.line_chart(df[["spend"]], height=200)
        except ImportError:
            st.info("Install pandas for charts: pip install pandas")
    else:
        st.info("No trend data available.")

    st.divider()

    # Campaign table
    st.subheader("Campaigns")
    ads = get_ads_with_metrics(days)
    if ads:
        try:
            import pandas as pd
            rows = []
            for a in ads:
                d = dict(a)
                rows.append({
                    "Campaign": d["campaign_name"],
                    "Ad Name": d["name"],
                    "Spend (AUD)": f"${d.get('spend') or 0:,.2f}",
                    "CTR %": d.get("ctr") or 0,
                    "CPM": f"${d.get('cpm') or 0}",
                    "CPC": f"${d.get('cpc') or 0}",
                    "CPA": f"${d.get('cpa') or 0}",
                    "ROAS": d.get("roas") or 0,
                    "Frequency": d.get("frequency") or 0,
                    "Status": _fatigue_badge(
                        d.get("ctr") or 0, d.get("frequency") or 0, d.get("cpm") or 0
                    ),
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
        except ImportError:
            for a in ads:
                d = dict(a)
                st.write(f"**{d['name']}** — CTR: {d.get('ctr')}% | Spend: ${d.get('spend')}")
    else:
        st.info("No ad data available.")


# ── Creative tab ─────────────────────────────────────────────────────────────

def _render_creative():
    st.subheader("Creative Performance & Copy Recommendations")

    # Filter
    campaigns = get_campaigns()
    camp_names = ["All campaigns"] + [c["name"] for c in campaigns]
    selected_camp = st.selectbox("Filter by campaign", camp_names, key="creative_campaign_filter")
    camp_id = None
    if selected_camp != "All campaigns":
        camp_id = next((c["id"] for c in campaigns if c["name"] == selected_camp), None)

    # Fatigue summary
    ads = get_ads_with_metrics(7, camp_id)
    fatigued = [dict(a) for a in ads
                if _fatigue_badge(a["ctr"] or 0, a["frequency"] or 0, a["cpm"] or 0) != "✅ Healthy"]

    if fatigued:
        st.error(
            f"🔴 **{len(fatigued)} ad(s) are fatigued or underperforming** — "
            f"review recommendations below."
        )
    else:
        st.success("✅ All ads are performing within healthy benchmarks.")

    st.divider()

    # All ads with status
    st.markdown("#### Ad-Level Performance (Last 7 days)")
    if ads:
        try:
            import pandas as pd
            rows = []
            for a in ads:
                d = dict(a)
                rows.append({
                    "Ad": d["name"],
                    "Headline": (d.get("headline") or "")[:50] + ("…" if len(d.get("headline") or "") > 50 else ""),
                    "CTR %": d.get("ctr") or 0,
                    "Frequency": d.get("frequency") or 0,
                    "CPM (AUD)": d.get("cpm") or 0,
                    "CPA (AUD)": d.get("cpa") or 0,
                    "Spend": f"${d.get('spend') or 0:,.2f}",
                    "Fatigue": _fatigue_badge(d.get("ctr") or 0, d.get("frequency") or 0, d.get("cpm") or 0),
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
        except ImportError:
            pass

    st.divider()

    # Pending recommendations
    st.markdown("#### Copy Recommendations")
    st.caption(
        "Recommendations are generated by the analysis engine. "
        "Approve to log as actioned. Reject to dismiss. Snooze to revisit in 48h."
    )

    recs = get_pending_recommendations()
    if not recs:
        st.info("No pending recommendations. Run an analysis to generate new ones.")
    else:
        for rec in recs:
            r = dict(rec)
            with st.expander(
                f"{'🟡' if r['type'] == 'new_headline' else '🔵'} "
                f"**{r['ad_name']}** — `{r['type']}` — _{r['campaign_name']}_",
                expanded=True,
            ):
                col_curr, col_new = st.columns(2)
                with col_curr:
                    st.markdown("**Current**")
                    st.code(r.get("current_value") or "—", language=None)
                with col_new:
                    st.markdown("**Recommended**")
                    st.code(r.get("recommended_value") or "—", language=None)

                st.caption(f"💡 Reason: {r.get('reason') or '—'}")

                b1, b2, b3, _ = st.columns([1, 1, 1, 3])
                with b1:
                    if st.button("✓ Approve", key=f"approve_{r['id']}", type="primary"):
                        update_recommendation_status(r["id"], "approved")
                        log_memory(
                            str(date.today()), r["ad_id"],
                            f"Approved: {r['type']} replacement for {r['ad_name']}",
                            action_taken=f"New copy: {r['recommended_value'][:100]}",
                            status="hypothesis",
                        )
                        st.success("Approved — logged to memory.")
                        st.rerun()
                with b2:
                    if st.button("✗ Reject", key=f"reject_{r['id']}"):
                        update_recommendation_status(r["id"], "rejected")
                        st.info("Rejected.")
                        st.rerun()
                with b3:
                    if st.button("⏸ Snooze 48h", key=f"snooze_{r['id']}"):
                        snooze_recommendation(r["id"], 48)
                        st.info("Snoozed for 48 hours.")
                        st.rerun()

    st.divider()

    # Recommendation history
    st.markdown("#### Recommendation History")
    history = get_recommendation_history(30)
    if history:
        try:
            import pandas as pd
            rows = [
                {
                    "Ad": dict(r)["ad_name"],
                    "Campaign": dict(r)["campaign_name"],
                    "Type": dict(r)["type"],
                    "Recommended": (dict(r).get("recommended_value") or "")[:60] + "…",
                    "Status": dict(r)["status"].upper(),
                    "Date": dict(r)["created_at"][:10] if dict(r).get("created_at") else "",
                    "Actioned": dict(r)["actioned_at"][:10] if dict(r).get("actioned_at") else "—",
                }
                for r in history
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        except ImportError:
            for r in history:
                d = dict(r)
                st.write(f"- **{d['ad_name']}** | {d['type']} | {d['status']}")
    else:
        st.info("No recommendation history yet.")


# ── Memory tab ────────────────────────────────────────────────────────────────

def _render_memory():
    st.subheader("Memory & Hypothesis Log")
    st.caption(
        "Every recommendation and analysis result is logged here. "
        "When you run the next analysis, Claude automatically imports this history "
        "so the system learns from what worked and what didn't."
    )

    memory = get_memory_log(100)

    if not memory:
        st.info("No memory entries yet. Memory is populated when you approve/reject recommendations and run analyses.")
        return

    # Status filter
    statuses = ["All", "hypothesis", "confirmed", "rejected", "tested"]
    status_filter = st.selectbox("Filter by status", statuses, key="memory_status_filter")

    try:
        import pandas as pd
        rows = []
        for m in memory:
            d = dict(m)
            if status_filter != "All" and d.get("status") != status_filter:
                continue
            rows.append({
                "Date": d.get("analysis_date") or d.get("created_at", "")[:10],
                "Ad": d.get("ad_name") or "—",
                "Campaign": d.get("campaign_name") or "—",
                "Hypothesis / Finding": d.get("hypothesis") or "—",
                "Action Taken": (d.get("action_taken") or "—")[:80],
                "Outcome": (d.get("outcome") or "Pending")[:60],
                "Status": (d.get("status") or "").upper(),
            })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info(f"No entries with status '{status_filter}'.")
    except ImportError:
        for m in memory:
            d = dict(m)
            st.write(f"- {d.get('analysis_date')} | {d.get('hypothesis', '')[:80]}")

    st.divider()

    # Manual entry
    st.markdown("#### Add Manual Hypothesis")
    with st.form("manual_memory_form", clear_on_submit=True):
        hyp_text = st.text_area("Hypothesis", placeholder="e.g. GLP-1 angle will outperform standard science messaging for the 45–65 audience")
        hyp_action = st.text_input("Action taken (optional)", placeholder="e.g. Launched ad_007 targeting GLP-1 interest")
        if st.form_submit_button("Log Hypothesis"):
            if hyp_text:
                log_memory(str(date.today()), None, hyp_text, hyp_action or None)
                st.success("Logged to memory.")
                st.rerun()


# ── Analysis & Settings tab ────────────────────────────────────────────────────

def _render_settings():
    st.subheader("Run Analysis")

    if not slack_available():
        st.warning(
            "Slack not configured — digests will display here but won't be sent. "
            "Add SLACK_BOT_TOKEN and SLACK_CHANNEL_ID to your .env file to enable Slack."
        )

    run_col1, run_col2, run_col3 = st.columns(3)
    with run_col1:
        if st.button("📊 Run Daily Analysis", type="primary", use_container_width=True):
            _run_analysis("daily")
    with run_col2:
        if st.button("📈 Run Weekly Analysis", use_container_width=True):
            _run_analysis("weekly")
    with run_col3:
        if st.button("📉 Run Monthly Analysis", use_container_width=True):
            _run_analysis("monthly")

    st.divider()

    st.subheader("Slack Digest")
    slack_col1, slack_col2 = st.columns(2)
    with slack_col1:
        if st.button("📨 Send Daily Digest to Slack", use_container_width=True):
            _send_slack_daily()
    with slack_col2:
        if st.button("📨 Send Weekly Summary to Slack", use_container_width=True):
            _send_slack_weekly()

    st.divider()

    st.subheader("Benchmark Thresholds")
    st.caption("These are used to classify ads as Healthy / Watch / Fatigued. Edit to match your targets.")

    b_col1, b_col2 = st.columns(2)
    with b_col1:
        st.markdown("**CTR (higher is better)**")
        st.code(f"Good: >{BENCHMARKS['ctr_good']}%\nWatch: {BENCHMARKS['ctr_warn']}–{BENCHMARKS['ctr_good']}%\nBad: <{BENCHMARKS['ctr_warn']}%")
        st.markdown("**CPM AUD (lower is better)**")
        st.code(f"Good: <${BENCHMARKS['cpm_good']}\nWatch: ${BENCHMARKS['cpm_good']}–${BENCHMARKS['cpm_warn']}\nBad: >${BENCHMARKS['cpm_warn']}")
    with b_col2:
        st.markdown("**Frequency (lower is better)**")
        st.code(f"Watch: >{BENCHMARKS['frequency_warn']}x\nFatigued: >{BENCHMARKS['frequency_bad']}x")
        st.markdown("**CPA AUD (lower is better)**")
        st.code(f"Good: <${BENCHMARKS['cpa_good']}\nWatch: <${BENCHMARKS['cpa_warn']}\nBad: >${BENCHMARKS['cpa_warn']}")

    st.caption("To edit thresholds, modify `ui/modules/mock_data.py` → BENCHMARKS dict.")

    st.divider()

    st.subheader("API Credentials")
    st.caption("Add these to your `.env` file in the project root. They are never committed to git.")
    st.code("""# Meta Ads API
META_APP_ID=
META_APP_SECRET=
META_ACCESS_TOKEN=
META_AD_ACCOUNT_ID=

# Slack
SLACK_BOT_TOKEN=
SLACK_CHANNEL_ID=

# Webhook (for Slack interactive buttons → your server URL)
SLACK_WEBHOOK_BASE_URL=http://localhost:8502
""", language="bash")

    st.info(
        "Once credentials are added, the MCP server (`mcp/meta_ads/server.py`) "
        "will pull live data on each analysis run — replacing mock data automatically."
    )

    st.divider()

    st.subheader("Slack Webhook Server")
    st.caption(
        "Run the webhook server to enable Slack interactive buttons "
        "(approve/snooze from Slack messages)."
    )
    st.code("python ui/slack_webhook.py", language="bash")
    st.caption(
        "Then configure your Slack app's Interactivity Request URL to point to: "
        "`https://your-domain.com/slack/actions`"
    )


# ── Internal helpers ──────────────────────────────────────────────────────────

def _run_analysis(run_type: str):
    ads = get_ads_with_metrics(7)
    memory = get_memory_log(20)

    fatigued = []
    underperformers = []
    for a in ads:
        d = dict(a)
        badge = _fatigue_badge(d.get("ctr") or 0, d.get("frequency") or 0, d.get("cpm") or 0)
        if "🔴" in badge:
            fatigued.append(d)
        elif "⚠️" in badge:
            underperformers.append(d)

    summary = (
        f"{run_type.capitalize()} analysis — "
        f"{len(fatigued)} fatigued, {len(underperformers)} watch, "
        f"{len(get_pending_recommendations())} recommendations pending"
    )

    log_analysis_run(
        run_type=run_type,
        summary=summary,
        fatigue_count=len(fatigued),
        underperformer_count=len(underperformers),
        recommendations_generated=0,
        slack_sent=False,
    )

    st.success(f"**{run_type.capitalize()} analysis complete.**")

    if fatigued:
        st.error(f"🔴 **{len(fatigued)} fatigued ad(s):**")
        for a in fatigued:
            st.write(f"  - {a['name']} — CTR {a.get('ctr')}%, Frequency {a.get('frequency')}x")

    if underperformers:
        st.warning(f"⚠️ **{len(underperformers)} watch ad(s):**")
        for a in underperformers:
            st.write(f"  - {a['name']} — CTR {a.get('ctr')}%")

    # Log analysis to memory
    log_memory(
        str(date.today()), None,
        f"{run_type.capitalize()} analysis: {len(fatigued)} fatigued, "
        f"{len(underperformers)} watch",
        status="confirmed",
    )

    st.info("Pending recommendations have been updated in the Creative tab.")


def _send_slack_daily():
    kpis = get_kpis(7)
    ads = get_ads_with_metrics(7)
    fatigued = [
        dict(a) for a in ads
        if "🔴" in _fatigue_badge(a["ctr"] or 0, a["frequency"] or 0, a["cpm"] or 0)
    ]
    pending = get_pending_recommendations()
    ok, msg = send_daily_digest(kpis, fatigued, len(pending))
    if ok:
        st.success("Daily digest sent to Slack.")
    else:
        st.error(f"Slack send failed: {msg}")
        st.info("Check SLACK_BOT_TOKEN and SLACK_CHANNEL_ID in your .env file.")


def _send_slack_weekly():
    kpis_7d = get_kpis(7)
    kpis_prev = get_kpis(14)
    ads = get_ads_with_metrics(7)
    sorted_ads = sorted([dict(a) for a in ads], key=lambda x: x.get("ctr") or 0, reverse=True)
    top = sorted_ads[:3]
    bottom = sorted_ads[-3:]
    ok, msg = send_weekly_summary(kpis_7d, kpis_prev, top, bottom)
    if ok:
        st.success("Weekly summary sent to Slack.")
    else:
        st.error(f"Slack send failed: {msg}")
