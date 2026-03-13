"""
Marketing Analytics — SQLite database layer
============================================
Schema for campaigns, ads, metrics, recommendations, and memory log.
The same DB is read by Streamlit (ui/app.py) and written by the
Slack webhook server (ui/slack_webhook.py) and analysis scripts.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent.parent / "marketing.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id          TEXT PRIMARY KEY,
                name        TEXT NOT NULL,
                status      TEXT DEFAULT 'active',
                objective   TEXT,
                budget_daily REAL,
                platform    TEXT DEFAULT 'meta',
                market      TEXT DEFAULT 'AU',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS ad_sets (
                id          TEXT PRIMARY KEY,
                campaign_id TEXT NOT NULL,
                name        TEXT NOT NULL,
                status      TEXT DEFAULT 'active',
                audience    TEXT,
                budget_daily REAL,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            );

            CREATE TABLE IF NOT EXISTS ads (
                id          TEXT PRIMARY KEY,
                ad_set_id   TEXT NOT NULL,
                campaign_id TEXT NOT NULL,
                name        TEXT NOT NULL,
                status      TEXT DEFAULT 'active',
                headline    TEXT,
                primary_text TEXT,
                description TEXT,
                format      TEXT DEFAULT 'single_image',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ad_set_id) REFERENCES ad_sets(id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            );

            CREATE TABLE IF NOT EXISTS ad_metrics (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_id       TEXT NOT NULL,
                date        DATE NOT NULL,
                spend       REAL DEFAULT 0,
                impressions INTEGER DEFAULT 0,
                clicks      INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                revenue     REAL DEFAULT 0,
                frequency   REAL DEFAULT 1.0,
                UNIQUE(ad_id, date),
                FOREIGN KEY (ad_id) REFERENCES ads(id)
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_id            TEXT NOT NULL,
                type             TEXT NOT NULL,
                current_value    TEXT,
                recommended_value TEXT,
                reason           TEXT,
                status           TEXT DEFAULT 'pending',
                created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actioned_at      TIMESTAMP,
                snooze_until     TIMESTAMP,
                outcome          TEXT,
                notes            TEXT,
                FOREIGN KEY (ad_id) REFERENCES ads(id)
            );

            CREATE TABLE IF NOT EXISTS memory_log (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_date DATE NOT NULL,
                ad_id        TEXT,
                hypothesis   TEXT,
                action_taken TEXT,
                outcome      TEXT,
                metrics_before TEXT,
                metrics_after  TEXT,
                status       TEXT DEFAULT 'hypothesis',
                notes        TEXT,
                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS analysis_runs (
                id                       INTEGER PRIMARY KEY AUTOINCREMENT,
                run_type                 TEXT NOT NULL,
                run_at                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                summary                  TEXT,
                fatigue_count            INTEGER DEFAULT 0,
                underperformer_count     INTEGER DEFAULT 0,
                recommendations_generated INTEGER DEFAULT 0,
                slack_sent               BOOLEAN DEFAULT 0
            );
        """)


# ── Queries ───────────────────────────────────────────────────────────────────

def get_campaigns(status="active"):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM campaigns WHERE status = ? ORDER BY name",
            (status,)
        ).fetchall()


def get_ads_with_metrics(days=7, campaign_id=None):
    """Return ads joined with aggregated metrics for the last N days."""
    campaign_filter = "AND a.campaign_id = ?" if campaign_id else ""
    params = [days]
    if campaign_id:
        params.append(campaign_id)
    with get_conn() as conn:
        return conn.execute(f"""
            SELECT
                a.id, a.name, a.headline, a.primary_text, a.status,
                a.campaign_id, a.ad_set_id,
                c.name AS campaign_name,
                ROUND(SUM(m.spend), 2)                             AS spend,
                SUM(m.impressions)                                  AS impressions,
                SUM(m.clicks)                                       AS clicks,
                SUM(m.conversions)                                  AS conversions,
                ROUND(SUM(m.revenue), 2)                           AS revenue,
                ROUND(AVG(m.frequency), 2)                         AS frequency,
                ROUND(100.0 * SUM(m.clicks) / NULLIF(SUM(m.impressions), 0), 2) AS ctr,
                ROUND(1000.0 * SUM(m.spend) / NULLIF(SUM(m.impressions), 0), 2) AS cpm,
                ROUND(SUM(m.spend) / NULLIF(SUM(m.clicks), 0), 2) AS cpc,
                ROUND(SUM(m.spend) / NULLIF(SUM(m.conversions), 0), 2) AS cpa,
                ROUND(SUM(m.revenue) / NULLIF(SUM(m.spend), 0), 2) AS roas
            FROM ads a
            JOIN campaigns c ON c.id = a.campaign_id
            LEFT JOIN ad_metrics m ON m.ad_id = a.id
                AND m.date >= DATE('now', '-' || ? || ' days')
            WHERE a.status = 'active' {campaign_filter}
            GROUP BY a.id
            ORDER BY spend DESC
        """, params).fetchall()


def get_spend_trend(days=30):
    """Daily spend across all active campaigns."""
    with get_conn() as conn:
        return conn.execute("""
            SELECT
                m.date,
                ROUND(SUM(m.spend), 2) AS spend,
                SUM(m.clicks) AS clicks,
                SUM(m.conversions) AS conversions
            FROM ad_metrics m
            JOIN ads a ON a.id = m.ad_id
            WHERE m.date >= DATE('now', '-' || ? || ' days')
              AND a.status = 'active'
            GROUP BY m.date
            ORDER BY m.date
        """, (days,)).fetchall()


def get_pending_recommendations():
    with get_conn() as conn:
        return conn.execute("""
            SELECT r.*, a.name AS ad_name, a.headline, a.primary_text,
                   c.name AS campaign_name
            FROM recommendations r
            JOIN ads a ON a.id = r.ad_id
            JOIN campaigns c ON c.id = a.campaign_id
            WHERE r.status IN ('pending', 'snoozed')
              AND (r.snooze_until IS NULL OR r.snooze_until <= CURRENT_TIMESTAMP)
            ORDER BY r.created_at DESC
        """).fetchall()


def get_recommendation_history(limit=50):
    with get_conn() as conn:
        return conn.execute("""
            SELECT r.*, a.name AS ad_name, c.name AS campaign_name
            FROM recommendations r
            JOIN ads a ON a.id = r.ad_id
            JOIN campaigns c ON c.id = a.campaign_id
            ORDER BY r.created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()


def update_recommendation_status(rec_id: int, status: str, notes: str = None):
    with get_conn() as conn:
        conn.execute("""
            UPDATE recommendations
            SET status = ?, actioned_at = CURRENT_TIMESTAMP, notes = COALESCE(?, notes)
            WHERE id = ?
        """, (status, notes, rec_id))


def snooze_recommendation(rec_id: int, hours: int = 48):
    with get_conn() as conn:
        conn.execute("""
            UPDATE recommendations
            SET status = 'snoozed',
                snooze_until = DATETIME('now', '+' || ? || ' hours')
            WHERE id = ?
        """, (hours, rec_id))


def log_memory(analysis_date, ad_id, hypothesis, action_taken=None,
               metrics_before=None, status="hypothesis"):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO memory_log
                (analysis_date, ad_id, hypothesis, action_taken, metrics_before, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            analysis_date, ad_id, hypothesis, action_taken,
            json.dumps(metrics_before) if metrics_before else None,
            status,
        ))


def get_memory_log(limit=100):
    with get_conn() as conn:
        return conn.execute("""
            SELECT ml.*, a.name AS ad_name, c.name AS campaign_name
            FROM memory_log ml
            LEFT JOIN ads a ON a.id = ml.ad_id
            LEFT JOIN campaigns c ON c.id = a.campaign_id
            ORDER BY ml.created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()


def log_analysis_run(run_type, summary, fatigue_count, underperformer_count,
                     recommendations_generated, slack_sent=False):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO analysis_runs
                (run_type, summary, fatigue_count, underperformer_count,
                 recommendations_generated, slack_sent)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (run_type, summary, fatigue_count, underperformer_count,
              recommendations_generated, slack_sent))


def get_kpis(days=7):
    """Aggregate KPIs across all active campaigns."""
    with get_conn() as conn:
        row = conn.execute("""
            SELECT
                ROUND(SUM(m.spend), 2)                                          AS total_spend,
                SUM(m.impressions)                                               AS total_impressions,
                SUM(m.clicks)                                                    AS total_clicks,
                SUM(m.conversions)                                               AS total_conversions,
                ROUND(100.0 * SUM(m.clicks) / NULLIF(SUM(m.impressions), 0), 2) AS avg_ctr,
                ROUND(1000.0 * SUM(m.spend) / NULLIF(SUM(m.impressions), 0), 2) AS avg_cpm,
                ROUND(SUM(m.spend) / NULLIF(SUM(m.clicks), 0), 2)               AS avg_cpc,
                ROUND(SUM(m.spend) / NULLIF(SUM(m.conversions), 0), 2)          AS avg_cpa,
                ROUND(SUM(m.revenue) / NULLIF(SUM(m.spend), 0), 2)              AS avg_roas
            FROM ad_metrics m
            JOIN ads a ON a.id = m.ad_id
            WHERE a.status = 'active'
              AND m.date >= DATE('now', '-' || ? || ' days')
        """, (days,)).fetchone()
        return dict(row) if row else {}
