"""
Mock data — realistic CSIRO TWD AU Meta Ads campaigns
=====================================================
Generates plausible campaign/ad/metrics data so the UI works
before real API credentials are configured.
Run once: python -m ui.modules.mock_data
"""

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from .marketing_db import init_db, get_conn, DB_PATH

random.seed(42)

CAMPAIGNS = [
    {
        "id": "camp_001",
        "name": "CSIRO TWD — Science & Credibility — Prospecting",
        "objective": "conversions",
        "budget_daily": 350.0,
        "status": "active",
    },
    {
        "id": "camp_002",
        "name": "CSIRO TWD — Member Results — Prospecting",
        "objective": "conversions",
        "budget_daily": 280.0,
        "status": "active",
    },
    {
        "id": "camp_003",
        "name": "CSIRO TWD — GLP-1 & Medication — Awareness",
        "objective": "reach",
        "budget_daily": 150.0,
        "status": "active",
    },
    {
        "id": "camp_004",
        "name": "CSIRO TWD — Fast Start — Conversion",
        "objective": "conversions",
        "budget_daily": 200.0,
        "status": "active",
    },
    {
        "id": "camp_005",
        "name": "CSIRO TWD — Health Fund Partners — Retargeting",
        "objective": "conversions",
        "budget_daily": 120.0,
        "status": "active",
    },
]

AD_SETS = [
    # camp_001 — Science
    {"id": "as_001a", "campaign_id": "camp_001", "name": "Women 45–65 — Metro AU", "audience": "Women 45–65, metro, health interest"},
    {"id": "as_001b", "campaign_id": "camp_001", "name": "Women 35–55 — GLP-1 Interest", "audience": "Women 35–55, GLP-1/weight loss meds interest"},
    # camp_002 — Results
    {"id": "as_002a", "campaign_id": "camp_002", "name": "Women 50+ — Lookalike 1%", "audience": "LAL 1% from converters"},
    {"id": "as_002b", "campaign_id": "camp_002", "name": "Men 45–65 — Broad", "audience": "Men 45–65, health/fitness"},
    # camp_003 — GLP-1
    {"id": "as_003a", "campaign_id": "camp_003", "name": "GLP-1 Users — Ozempic/Wegovy Interest", "audience": "GLP-1 medication interest, all genders 35–65"},
    # camp_004 — Fast Start
    {"id": "as_004a", "campaign_id": "camp_004", "name": "Retargeting — Visited Pricing Page", "audience": "Retargeting: visited /pricing in last 30d"},
    {"id": "as_004b", "campaign_id": "camp_004", "name": "Women 40–60 — Meal Replacement Interest", "audience": "Women 40–60, meal replacement interest"},
    # camp_005 — Health Fund
    {"id": "as_005a", "campaign_id": "camp_005", "name": "HCF / TUH Members — Retargeting", "audience": "Email list: HCF + TUH members"},
]

# Ad definitions: headline, body copy, performance profile
ADS = [
    # Science & Credibility
    {
        "id": "ad_001", "ad_set_id": "as_001a", "campaign_id": "camp_001",
        "name": "Science — '22 Studies' — Static",
        "headline": "22 studies just proved IF doesn't work",
        "primary_text": "Intermittent fasting: a Cochrane review of 22 studies found little to no advantage over a quality diet. The CSIRO Total Wellbeing Diet has the peer-reviewed evidence behind it. Start your 12-week program today.",
        "description": "Australia's most scientifically credible diet program",
        "profile": "healthy",  # healthy | watch | fatigued
    },
    {
        "id": "ad_002", "ad_set_id": "as_001a", "campaign_id": "camp_001",
        "name": "Science — CSIRO Authority — Carousel",
        "headline": "Backed by CSIRO research since 2005",
        "primary_text": "The CSIRO Total Wellbeing Diet isn't a trend. It's two decades of peer-reviewed science, published in international journals. Average member loses 7.2% of body weight in 12 weeks.",
        "description": "Join 3 million Australians who've changed their lives",
        "profile": "watch",
    },
    {
        "id": "ad_003", "ad_set_id": "as_001b", "campaign_id": "camp_001",
        "name": "Science — GLP-1 Protein — Static",
        "headline": "On Ozempic? Here's what CSIRO says to eat",
        "primary_text": "New joint advisory: GLP-1 users need 1.2–1.6g protein per kg/day to protect muscle. 43% of people aren't hitting this. The CSIRO TWD meal plan is built around exactly this target.",
        "description": "The diet program built for GLP-1 users",
        "profile": "healthy",
    },
    # Member Results
    {
        "id": "ad_004", "ad_set_id": "as_002a", "campaign_id": "camp_002",
        "name": "Results — '57 years old, 18kg' — Video",
        "headline": "57 years old. 18kg down. Still eating pasta.",
        "primary_text": "Margaret had tried 8 diets before the CSIRO Total Wellbeing Diet. Here's what 12 weeks actually looked like — and why this one was different.",
        "description": "Real results from real CSIRO TWD members",
        "profile": "fatigued",
    },
    {
        "id": "ad_005", "ad_set_id": "as_002a", "campaign_id": "camp_002",
        "name": "Results — '7.2% stat' — Static",
        "headline": "Average member loses 7.2% in 12 weeks",
        "primary_text": "Not a quick fix. A 12-week program backed by CSIRO peer-reviewed research. Nearly 1 in 2 members who complete the program lose 5%+ of starting body weight — the clinically significant threshold.",
        "description": "Start your 12-week program from $299",
        "profile": "healthy",
    },
    {
        "id": "ad_006", "ad_set_id": "as_002b", "campaign_id": "camp_002",
        "name": "Results — Men — '8 diets' — Static",
        "headline": "8 diets. Zero that stuck. Until CSIRO.",
        "primary_text": "The reason most diets fail isn't willpower. It's program design. The CSIRO TWD is built on the habits the research says actually keep weight off — not just lose it.",
        "description": "Science-backed. Dietitian-supported.",
        "profile": "watch",
    },
    # GLP-1
    {
        "id": "ad_007", "ad_set_id": "as_003a", "campaign_id": "camp_003",
        "name": "GLP-1 — Muscle Loss Warning — Video",
        "headline": "Up to 40% of Ozempic weight loss is muscle",
        "primary_text": "Studies suggest up to 40% of weight lost on GLP-1 medications may be lean muscle. A structured high-protein diet changes this. CSIRO TWD was built for exactly this.",
        "description": "Protect your muscle. Keep your results.",
        "profile": "healthy",
    },
    {
        "id": "ad_008", "ad_set_id": "as_003a", "campaign_id": "camp_003",
        "name": "GLP-1 — 'Window' Messaging — Static",
        "headline": "GLP-1 gives you a window. Use it right.",
        "primary_text": "Medication suppresses appetite. A structured program tells you what to do with that. Without one, most people regain weight when they stop. With one — the habits stick.",
        "description": "The CSIRO TWD: built for GLP-1 users",
        "profile": "fatigued",
    },
    # Fast Start
    {
        "id": "ad_009", "ad_set_id": "as_004a", "campaign_id": "camp_004",
        "name": "Fast Start — '98%' — Retargeting Static",
        "headline": "98% of Fast Start members lost weight",
        "primary_text": "You visited our pricing page. Still thinking about it? Fast Start Deluxe Kit: 42 shakes + shaker + 1-month CSIRO TWD program for $149. 75% of members hit the clinically significant 5% threshold.",
        "description": "$149 — starter kit + 1-month membership",
        "profile": "healthy",
    },
    {
        "id": "ad_010", "ad_set_id": "as_004b", "campaign_id": "camp_004",
        "name": "Fast Start — Flavours — Carousel",
        "headline": "Chocolate, Vanilla, Coffee, Strawberry",
        "primary_text": "Fast Start protein shakes for breakfast + lunch for 3 weeks, then full CSIRO TWD. Average: 7.4% weight loss in 12 weeks. High protein, high fibre, no artificial sweeteners.",
        "description": "Fast Start — $149 starter kit",
        "profile": "watch",
    },
    # Health Fund
    {
        "id": "ad_011", "ad_set_id": "as_005a", "campaign_id": "camp_005",
        "name": "Health Fund — HCF 20% Off — Email Match",
        "headline": "HCF member? You get 20% off CSIRO TWD",
        "primary_text": "Your health fund is already covering part of your program. HCF members get 20% off the CSIRO Total Wellbeing Diet. TUH members get $30 off. Check if your fund is included — link below.",
        "description": "Check your health fund benefit now",
        "profile": "healthy",
    },
]

# Benchmark thresholds (health/wellness, Meta AU)
BENCHMARKS = {
    "ctr_good": 2.0,       # > 2.0% = good
    "ctr_warn": 1.0,       # 1.0–2.0% = watch
    "cpm_good": 12.0,      # < $12 AUD = good
    "cpm_warn": 18.0,      # > $18 AUD = watch
    "cpc_good": 1.50,      # < $1.50 AUD = good
    "cpc_warn": 2.50,      # > $2.50 AUD = watch
    "frequency_warn": 3.5, # > 3.5 = fatigue risk
    "frequency_bad": 5.0,  # > 5.0 = fatigued
    "cpa_good": 45.0,      # < $45 AUD = good
    "cpa_warn": 80.0,      # > $80 AUD = watch
}

# Performance profiles → realistic metric ranges
PROFILES = {
    "healthy": {
        "ctr": (2.2, 3.8),
        "cpm": (9.0, 13.0),
        "cvr": (0.08, 0.15),  # click → conversion
        "frequency_growth": (0.05, 0.12),  # per day
        "revenue_per_conv": (149, 299),
    },
    "watch": {
        "ctr": (1.1, 2.1),
        "cpm": (13.0, 18.0),
        "cvr": (0.04, 0.08),
        "frequency_growth": (0.12, 0.20),
        "revenue_per_conv": (79, 149),
    },
    "fatigued": {
        "ctr": (0.5, 1.1),
        "cpm": (18.0, 28.0),
        "cvr": (0.01, 0.04),
        "frequency_growth": (0.20, 0.35),
        "revenue_per_conv": (79, 149),
    },
}

# Pre-generated copy recommendations for the "fatigued" ads
RECOMMENDATIONS = [
    {
        "ad_id": "ad_004",
        "type": "new_headline",
        "current_value": "57 years old. 18kg down. Still eating pasta.",
        "recommended_value": "Lost 18kg at 57 — without giving up food she loves",
        "reason": "Frequency 5.8 — current headline has fatigued on this audience. "
                  "New framing leads with outcome rather than numbers to reset attention.",
        "status": "pending",
    },
    {
        "ad_id": "ad_004",
        "type": "new_primary_text",
        "current_value": "Margaret had tried 8 diets before the CSIRO Total Wellbeing Diet...",
        "recommended_value": "8 diets. 20 years. Nothing stuck — until she tried the one "
                             "backed by CSIRO peer-reviewed research. Here's what Week 1 "
                             "actually looked like for Margaret, 57.",
        "reason": "Lead with relatability ('8 diets, 20 years') before the program name. "
                  "Mirrors language used by highest-performing member story ads from last quarter.",
        "status": "pending",
    },
    {
        "ad_id": "ad_008",
        "type": "new_headline",
        "current_value": "GLP-1 gives you a window. Use it right.",
        "recommended_value": "What to eat on Ozempic — the CSIRO answer",
        "reason": "CTR 0.8%, well below benchmark. 'What to eat on Ozempic' is the #1 "
                  "search intent for GLP-1 users. Direct answer-framing outperforms "
                  "metaphor-framing for this audience.",
        "status": "pending",
    },
    {
        "ad_id": "ad_008",
        "type": "new_primary_text",
        "current_value": "Medication suppresses appetite. A structured program tells you what to do with that...",
        "recommended_value": "If you're on Ozempic or Wegovy and nobody's told you what to eat — "
                             "this is the advice you needed on Day 1. Protein first. Low GI. "
                             "Structured meals. The CSIRO TWD was built for exactly this.",
        "reason": "Opens with the audience's unmet need ('nobody told you what to eat') "
                  "which performed +34% higher on click-to-landing in similar GLP-1 content.",
        "status": "pending",
    },
]


def _generate_metrics_for_ad(ad_id: str, profile_name: str, campaign_budget: float,
                              ad_share: float, days: int = 60):
    """Generate day-by-day metrics for an ad over the last N days."""
    profile = PROFILES[profile_name]
    rows = []
    frequency = random.uniform(1.0, 1.5)

    for i in range(days, 0, -1):
        day = date.today() - timedelta(days=i)

        # Spend = proportional share of campaign budget with daily noise
        spend = campaign_budget * ad_share * random.uniform(0.75, 1.25)

        # CTR degrades over time for fatigued/watch ads
        degradation = 1.0
        if profile_name == "fatigued":
            degradation = max(0.4, 1.0 - (days - i) * 0.008)
        elif profile_name == "watch":
            degradation = max(0.7, 1.0 - (days - i) * 0.003)

        ctr = random.uniform(*profile["ctr"]) * degradation / 100
        cpm = random.uniform(*profile["cpm"])
        impressions = int((spend / cpm) * 1000)
        clicks = int(impressions * ctr)
        cvr = random.uniform(*profile["cvr"])
        conversions = int(clicks * cvr)
        rev_per = random.uniform(*profile["revenue_per_conv"])
        revenue = conversions * rev_per

        frequency += random.uniform(*profile["frequency_growth"])

        rows.append((ad_id, str(day), round(spend, 2), impressions,
                     clicks, conversions, round(revenue, 2), round(frequency, 2)))
    return rows


def seed_mock_data(force=False):
    """Seed the database with mock CSIRO TWD AU data. Safe to call multiple times."""
    init_db()
    with get_conn() as conn:
        existing = conn.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0]
        if existing > 0 and not force:
            return  # Already seeded

        # Clear existing mock data if force
        if force:
            for tbl in ["ad_metrics", "recommendations", "memory_log",
                        "ads", "ad_sets", "campaigns"]:
                conn.execute(f"DELETE FROM {tbl}")

        # Insert campaigns
        for c in CAMPAIGNS:
            conn.execute("""
                INSERT OR IGNORE INTO campaigns
                    (id, name, status, objective, budget_daily, platform, market)
                VALUES (?, ?, ?, ?, ?, 'meta', 'AU')
            """, (c["id"], c["name"], c["status"], c["objective"], c["budget_daily"]))

        # Insert ad sets
        for s in AD_SETS:
            conn.execute("""
                INSERT OR IGNORE INTO ad_sets
                    (id, campaign_id, name, audience)
                VALUES (?, ?, ?, ?)
            """, (s["id"], s["campaign_id"], s["name"], s["audience"]))

        # Insert ads
        for a in ADS:
            conn.execute("""
                INSERT OR IGNORE INTO ads
                    (id, ad_set_id, campaign_id, name, headline, primary_text, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (a["id"], a["ad_set_id"], a["campaign_id"],
                  a["name"], a["headline"], a["primary_text"], a["description"]))

        # Insert metrics
        campaign_budgets = {c["id"]: c["budget_daily"] for c in CAMPAIGNS}
        ads_per_campaign: dict[str, list] = {}
        for a in ADS:
            ads_per_campaign.setdefault(a["campaign_id"], []).append(a)

        for a in ADS:
            camp_ads = ads_per_campaign[a["campaign_id"]]
            share = 1.0 / len(camp_ads)
            budget = campaign_budgets[a["campaign_id"]]
            rows = _generate_metrics_for_ad(a["id"], a["profile"], budget, share, days=60)
            conn.executemany("""
                INSERT OR IGNORE INTO ad_metrics
                    (ad_id, date, spend, impressions, clicks, conversions, revenue, frequency)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)

        # Insert recommendations
        for r in RECOMMENDATIONS:
            conn.execute("""
                INSERT OR IGNORE INTO recommendations
                    (ad_id, type, current_value, recommended_value, reason, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (r["ad_id"], r["type"], r["current_value"],
                  r["recommended_value"], r["reason"], r["status"]))

        # Insert a few memory log entries
        entries = [
            ("2026-02-14", "ad_002", "Carousel format will outperform static for authority content",
             "Launched carousel variant (ad_002)", "hypothesis"),
            ("2026-02-28", "ad_002", "Carousel authority test — CTR lower than static by 0.4%",
             "Paused carousel; retained static", "confirmed"),
            ("2026-03-01", "ad_007", "GLP-1 muscle loss angle will resonate with Ozempic audience",
             "Launched ad_007 targeting GLP-1 interest audience", "hypothesis"),
            ("2026-03-07", "ad_007", "GLP-1 muscle loss ad achieving 3.1% CTR — above benchmark",
             None, "confirmed"),
        ]
        for e in entries:
            conn.execute("""
                INSERT OR IGNORE INTO memory_log
                    (analysis_date, ad_id, hypothesis, action_taken, status)
                VALUES (?, ?, ?, ?, ?)
            """, e)


if __name__ == "__main__":
    seed_mock_data(force=True)
    print(f"Mock data seeded to {DB_PATH}")
    print(f"  Campaigns : {len(CAMPAIGNS)}")
    print(f"  Ads       : {len(ADS)}")
    print(f"  Recommendations: {len(RECOMMENDATIONS)}")
