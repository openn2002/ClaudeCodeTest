"""
Meta Ads MCP Server — CSIRO TWD AU
=====================================
A Model Context Protocol server that connects Claude directly to the
Meta Marketing API, enabling natural-language queries over live ad data.

Usage (once credentials are configured):
    python mcp/meta_ads/server.py

Then add to ~/.claude/mcp.json:
    {
      "meta-ads": {
        "command": "python",
        "args": ["/path/to/ClaudeCodeTest/mcp/meta_ads/server.py"]
      }
    }

Example prompts once connected:
    "Which CSIRO TWD ads had the best CTR this week?"
    "Where am I wasting spend on prospecting vs retargeting?"
    "Which creatives are fatigued — frequency over 3.5?"
    "What's my CPM trend for the GLP-1 campaigns over 30 days?"

Credentials required (add to .env):
    META_APP_ID
    META_APP_SECRET
    META_ACCESS_TOKEN
    META_AD_ACCOUNT_ID
"""

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

try:
    import mcp.server.stdio
    import mcp.types as types
    from mcp.server import Server
    _MCP_AVAILABLE = True
except ImportError:
    _MCP_AVAILABLE = False
    print("MCP SDK not installed. Run: pip install mcp", file=sys.stderr)

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

META_API_BASE = "https://graph.facebook.com/v19.0"
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID", "")


# ── Meta API helpers ──────────────────────────────────────────────────────────

def _api_get(path: str, params: dict) -> dict:
    if not _REQUESTS_AVAILABLE:
        raise RuntimeError("requests library not installed")
    if not ACCESS_TOKEN:
        raise RuntimeError("META_ACCESS_TOKEN not set in .env")
    params["access_token"] = ACCESS_TOKEN
    url = f"{META_API_BASE}/{path}"
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _date_range(days: int) -> tuple[str, str]:
    end = date.today()
    start = end - timedelta(days=days)
    return str(start), str(end)


def get_campaigns(status: str = "ACTIVE") -> list[dict]:
    """Fetch all campaigns for the ad account."""
    data = _api_get(
        f"act_{AD_ACCOUNT_ID}/campaigns",
        {
            "fields": "id,name,status,objective,daily_budget,created_time",
            "filtering": json.dumps([{"field": "effective_status", "operator": "IN", "value": [status]}]),
            "limit": 100,
        },
    )
    return data.get("data", [])


def get_ad_insights(level: str = "ad", days: int = 7,
                    campaign_id: str = None) -> list[dict]:
    """
    Fetch performance insights.
    level: 'campaign' | 'adset' | 'ad'
    """
    since, until = _date_range(days)
    fields = (
        "campaign_name,adset_name,ad_name,"
        "spend,impressions,clicks,ctr,cpm,cpc,"
        "actions,action_values,frequency"
    )
    params = {
        "level": level,
        "fields": fields,
        "time_range": json.dumps({"since": since, "until": until}),
        "limit": 200,
    }
    if campaign_id:
        data = _api_get(f"{campaign_id}/insights", params)
    else:
        data = _api_get(f"act_{AD_ACCOUNT_ID}/insights", params)
    return data.get("data", [])


def get_ad_creatives(ad_id: str) -> dict:
    """Fetch creative details for a specific ad."""
    data = _api_get(
        f"{ad_id}",
        {"fields": "name,creative{title,body,description,image_url}"},
    )
    return data


def _parse_conversions(insight: dict) -> int:
    """Extract purchase/lead conversion count from actions array."""
    for action in insight.get("actions", []):
        if action.get("action_type") in ("purchase", "lead", "offsite_conversion.fb_pixel_purchase"):
            return int(action.get("value", 0))
    return 0


def _parse_revenue(insight: dict) -> float:
    """Extract revenue from action_values."""
    for av in insight.get("action_values", []):
        if av.get("action_type") in ("purchase", "offsite_conversion.fb_pixel_purchase"):
            return float(av.get("value", 0))
    return 0.0


def _enrich_insight(i: dict) -> dict:
    """Add computed fields and fatigue indicators to an insight dict."""
    ctr = float(i.get("ctr", 0))
    frequency = float(i.get("frequency", 0))
    cpm = float(i.get("cpm", 0))
    conversions = _parse_conversions(i)
    revenue = _parse_revenue(i)
    spend = float(i.get("spend", 0))
    cpa = round(spend / conversions, 2) if conversions > 0 else None
    roas = round(revenue / spend, 2) if spend > 0 else None

    if frequency >= 5.0 or ctr < 0.8:
        fatigue_status = "FATIGUED"
    elif frequency >= 3.5 or ctr < 1.0:
        fatigue_status = "WATCH"
    else:
        fatigue_status = "HEALTHY"

    return {
        **i,
        "conversions": conversions,
        "revenue": revenue,
        "cpa": cpa,
        "roas": roas,
        "fatigue_status": fatigue_status,
    }


# ── MCP Server ────────────────────────────────────────────────────────────────

if _MCP_AVAILABLE:
    server = Server("meta-ads-csiro-twd")

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="get_campaigns",
                description=(
                    "List all active Meta Ads campaigns for the CSIRO TWD AU ad account. "
                    "Returns campaign names, status, objectives, and daily budgets."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Campaign status filter: ACTIVE, PAUSED, or ALL",
                            "default": "ACTIVE",
                        }
                    },
                },
            ),
            types.Tool(
                name="get_ad_performance",
                description=(
                    "Get performance metrics for ads, ad sets, or campaigns. "
                    "Returns spend, impressions, CTR, CPM, CPC, conversions, CPA, ROAS, "
                    "frequency, and a fatigue status (HEALTHY/WATCH/FATIGUED). "
                    "Use this to find underperforming or fatigued ads."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "level": {
                            "type": "string",
                            "description": "Aggregation level: 'campaign', 'adset', or 'ad'",
                            "default": "ad",
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days to look back (e.g. 7, 14, 30)",
                            "default": 7,
                        },
                        "campaign_id": {
                            "type": "string",
                            "description": "Optional — filter to a specific campaign ID",
                        },
                    },
                    "required": [],
                },
            ),
            types.Tool(
                name="get_fatigued_ads",
                description=(
                    "Return only the ads that are fatigued or underperforming based on "
                    "frequency (>3.5 = watch, >5.0 = fatigued) and CTR (<1.0% = watch, <0.8% = fatigued). "
                    "Ideal for generating a daily alert of what needs attention."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Days to look back",
                            "default": 7,
                        },
                    },
                },
            ),
            types.Tool(
                name="get_spend_by_campaign",
                description=(
                    "Return total spend, ROAS, and CPA broken down by campaign. "
                    "Useful for identifying where budget is being wasted."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "days": {"type": "integer", "default": 7},
                    },
                },
            ),
            types.Tool(
                name="get_ad_creative",
                description="Fetch the headline, body copy, and description for a specific ad.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ad_id": {
                            "type": "string",
                            "description": "The Meta Ads ad ID",
                        }
                    },
                    "required": ["ad_id"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        try:
            if name == "get_campaigns":
                result = get_campaigns(arguments.get("status", "ACTIVE"))
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "get_ad_performance":
                insights = get_ad_insights(
                    level=arguments.get("level", "ad"),
                    days=arguments.get("days", 7),
                    campaign_id=arguments.get("campaign_id"),
                )
                enriched = [_enrich_insight(i) for i in insights]
                return [types.TextContent(type="text", text=json.dumps(enriched, indent=2))]

            elif name == "get_fatigued_ads":
                insights = get_ad_insights(level="ad", days=arguments.get("days", 7))
                fatigued = [
                    _enrich_insight(i) for i in insights
                    if _enrich_insight(i)["fatigue_status"] in ("FATIGUED", "WATCH")
                ]
                fatigued.sort(key=lambda x: float(x.get("frequency", 0)), reverse=True)
                return [types.TextContent(type="text", text=json.dumps(fatigued, indent=2))]

            elif name == "get_spend_by_campaign":
                insights = get_ad_insights(
                    level="campaign", days=arguments.get("days", 7)
                )
                enriched = [_enrich_insight(i) for i in insights]
                enriched.sort(key=lambda x: float(x.get("spend", 0)), reverse=True)
                return [types.TextContent(type="text", text=json.dumps(enriched, indent=2))]

            elif name == "get_ad_creative":
                result = get_ad_creatives(arguments["ad_id"])
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {e}")]

    async def main():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )


if __name__ == "__main__":
    if not _MCP_AVAILABLE:
        print("Install MCP SDK: pip install mcp")
        sys.exit(1)
    import asyncio
    asyncio.run(main())
