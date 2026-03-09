"""
Digital Wellness — Competitor Intelligence Dashboard
=====================================================
Streamlit UI for managing competitor lists and running AI-powered
social media and podcast competitive analysis.

Run with:
    streamlit run ui/app.py
"""

import json
import os
import re
import datetime
import threading
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import anthropic
import streamlit as st

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT         = Path(__file__).parent.parent
COMPETITORS  = ROOT / "competitors.json"
REPORTS_DIR  = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# ── Agent system prompts ───────────────────────────────────────────────────────
SOCIAL_AGENT_PATH  = ROOT / ".claude" / "agents" / "competitor-social-analyst.md"
PODCAST_AGENT_PATH = ROOT / ".claude" / "agents" / "podcast-competitor-analyst.md"


def load_agent_prompt(path: Path) -> str:
    """Read agent system prompt, stripping the YAML front-matter."""
    text = path.read_text()
    # Strip --- front-matter block
    if text.startswith("---"):
        parts = text.split("---", 2)
        return parts[2].strip() if len(parts) >= 3 else text
    return text


# ── Config helpers ─────────────────────────────────────────────────────────────
def load_competitors() -> dict:
    if COMPETITORS.exists():
        with open(COMPETITORS) as f:
            return json.load(f)
    return {"social_media": [], "podcasts": []}


def save_competitors(data: dict):
    with open(COMPETITORS, "w") as f:
        json.dump(data, f, indent=2)


# ── Report helpers ─────────────────────────────────────────────────────────────
def list_reports(prefix: str) -> list[Path]:
    return sorted(REPORTS_DIR.glob(f"{prefix}*.md"), reverse=True)


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# ── Claude API ─────────────────────────────────────────────────────────────────
def run_analysis(system_prompt: str, user_message: str, on_chunk=None) -> str:
    """
    Stream a Claude analysis and return the full text.
    Calls on_chunk(text) for each streamed chunk if provided.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY") or st.session_state.get("api_key", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set. Add it in the sidebar settings.")

    client = anthropic.Anthropic(api_key=api_key)
    full_text = []

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=8096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for text in stream.text_stream:
            full_text.append(text)
            if on_chunk:
                on_chunk(text)

    return "".join(full_text)


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Competitor Intelligence — Digital Wellness",
    page_icon="📊",
    layout="wide",
)

# ── Sidebar — Settings ────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://www.digitalwellness.com/favicon.ico", width=32)
    st.markdown("## Digital Wellness")
    st.markdown("### Competitor Intelligence")
    st.divider()

    st.markdown("**API Settings**")
    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        help="Set ANTHROPIC_API_KEY env var or enter here. Never committed to git.",
    )
    if api_key_input:
        st.session_state["api_key"] = api_key_input

    st.divider()
    st.caption("Powered by Claude Sonnet 4.6")
    st.caption(f"Reports saved to `{REPORTS_DIR.relative_to(ROOT)}/`")

# ── Main tabs ──────────────────────────────────────────────────────────────────
tab_social, tab_podcasts, tab_reports = st.tabs([
    "📱 Social Media Competitors",
    "🎙️ Podcast Competitors",
    "📁 Reports",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — SOCIAL MEDIA
# ════════════════════════════════════════════════════════════════════════════
with tab_social:
    st.header("Social Media Competitor Analysis")
    st.caption(
        "Analyse competitor social media presence across Instagram, TikTok, Facebook, "
        "YouTube, and LinkedIn. Identifies top hooks, formats, and content gaps."
    )

    competitors_data = load_competitors()
    social_list = competitors_data.get("social_media", [])

    col_list, col_add = st.columns([3, 2])

    with col_list:
        st.subheader("Current Competitors")
        if not social_list:
            st.info("No social media competitors added yet.")
        else:
            for i, comp in enumerate(social_list):
                c1, c2 = st.columns([5, 1])
                with c1:
                    platforms_str = ", ".join(comp.get("platforms", []))
                    st.markdown(f"**{comp['name']}**  \n`{platforms_str}`  \n_{comp.get('notes', '')}_")
                with c2:
                    if st.button("✕", key=f"del_social_{i}", help="Remove"):
                        social_list.pop(i)
                        competitors_data["social_media"] = social_list
                        save_competitors(competitors_data)
                        st.rerun()
                st.divider()

    with col_add:
        st.subheader("Add Competitor")
        with st.form("add_social_form", clear_on_submit=True):
            new_name = st.text_input("Competitor name", placeholder="e.g. Weight Watchers")
            new_platforms = st.multiselect(
                "Platforms to analyse",
                ["instagram", "facebook", "tiktok", "youtube", "linkedin", "twitter/x"],
                default=["instagram", "facebook"],
            )
            new_notes = st.text_input("Notes (optional)", placeholder="e.g. GLP-1 pivot, AU market")
            if st.form_submit_button("Add Competitor", use_container_width=True):
                if new_name:
                    social_list.append({
                        "name": new_name,
                        "platforms": new_platforms,
                        "notes": new_notes,
                    })
                    competitors_data["social_media"] = social_list
                    save_competitors(competitors_data)
                    st.success(f"Added {new_name}")
                    st.rerun()

    st.divider()
    st.subheader("Run Analysis")

    if not social_list:
        st.warning("Add at least one competitor above before running an analysis.")
    else:
        selected_social = st.multiselect(
            "Select competitors to analyse",
            [c["name"] for c in social_list],
            default=[c["name"] for c in social_list],
        )
        focus_platforms = st.multiselect(
            "Focus platforms (leave blank for all)",
            ["instagram", "facebook", "tiktok", "youtube", "linkedin", "twitter/x"],
        )
        extra_instructions = st.text_area(
            "Additional instructions (optional)",
            placeholder="e.g. Focus on GLP-1 content. Look for how they're targeting the 35–50 demographic.",
            height=80,
        )

        run_col, _ = st.columns([2, 3])
        with run_col:
            run_social = st.button(
                "🔍 Run Social Media Analysis",
                use_container_width=True,
                type="primary",
                disabled=not selected_social,
            )

        if run_social:
            selected_details = [c for c in social_list if c["name"] in selected_social]
            competitor_lines = "\n".join(
                f"- {c['name']} ({', '.join(c['platforms'])}): {c.get('notes', '')}"
                for c in selected_details
            )
            platform_note = (
                f"Focus specifically on these platforms: {', '.join(focus_platforms)}."
                if focus_platforms else "Analyse all available platforms."
            )
            user_msg = (
                f"Please analyse the following competitors:\n\n{competitor_lines}\n\n"
                f"{platform_note}\n\n"
                f"Context: These are competitors to the CSIRO Total Wellbeing Diet and Mayo Clinic Diet, "
                f"operated by Digital Wellness. Our audience skews 50+, female, science-credibility-seeking.\n\n"
                f"{extra_instructions}"
            ).strip()

            system_prompt = load_agent_prompt(SOCIAL_AGENT_PATH)

            with st.spinner("Running analysis — this may take a minute..."):
                output_area = st.empty()
                buffer = []

                def on_chunk(text):
                    buffer.append(text)
                    output_area.markdown("".join(buffer))

                try:
                    result = run_analysis(system_prompt, user_msg, on_chunk=on_chunk)
                    today = datetime.date.today().strftime("%Y-%m-%d")
                    slug = slugify(selected_social[0]) if len(selected_social) == 1 else "multi"
                    report_path = REPORTS_DIR / f"social-competitor-{slug}-{today}.md"
                    report_path.write_text(result)
                    st.success(f"Analysis complete! Saved to `{report_path.name}`")
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Analysis failed: {e}")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — PODCASTS
# ════════════════════════════════════════════════════════════════════════════
with tab_podcasts:
    st.header("Health & Wellbeing Podcast Analysis")
    st.caption(
        "Research the top health and wellbeing podcasts — understand what's working, "
        "why they're successful, and identify the gap Digital Wellness can own."
    )

    competitors_data = load_competitors()
    podcast_list = competitors_data.get("podcasts", [])

    col_plist, col_padd = st.columns([3, 2])

    with col_plist:
        st.subheader("Podcasts to Analyse")
        if not podcast_list:
            st.info("No podcasts added yet.")
        else:
            for i, pod in enumerate(podcast_list):
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(
                        f"**{pod['name']}**  \n"
                        f"Host: {pod.get('host', 'Unknown')}  \n"
                        f"_{pod.get('notes', '')}_"
                    )
                with c2:
                    if st.button("✕", key=f"del_pod_{i}", help="Remove"):
                        podcast_list.pop(i)
                        competitors_data["podcasts"] = podcast_list
                        save_competitors(competitors_data)
                        st.rerun()
                st.divider()

    with col_padd:
        st.subheader("Add Podcast")
        with st.form("add_podcast_form", clear_on_submit=True):
            pod_name = st.text_input("Podcast name", placeholder="e.g. Huberman Lab")
            pod_host = st.text_input("Host name", placeholder="e.g. Andrew Huberman")
            pod_notes = st.text_input("Notes (optional)", placeholder="e.g. Science-based, massive reach")
            if st.form_submit_button("Add Podcast", use_container_width=True):
                if pod_name:
                    podcast_list.append({
                        "name": pod_name,
                        "host": pod_host,
                        "notes": pod_notes,
                    })
                    competitors_data["podcasts"] = podcast_list
                    save_competitors(competitors_data)
                    st.success(f"Added {pod_name}")
                    st.rerun()

    st.divider()
    st.subheader("Run Podcast Analysis")

    if not podcast_list:
        st.warning("Add at least one podcast above before running an analysis.")
    else:
        selected_pods = st.multiselect(
            "Select podcasts to analyse",
            [p["name"] for p in podcast_list],
            default=[p["name"] for p in podcast_list],
        )
        pod_market = st.radio(
            "Primary market focus",
            ["Both AU & US", "Australia only", "United States only"],
            horizontal=True,
        )
        pod_extra = st.text_area(
            "Additional instructions (optional)",
            placeholder="e.g. Focus on episodes about weight loss medication / GLP-1. "
                         "We want to understand how science credibility is communicated.",
            height=80,
        )

        run_pod_col, _ = st.columns([2, 3])
        with run_pod_col:
            run_pods = st.button(
                "🎙️ Run Podcast Analysis",
                use_container_width=True,
                type="primary",
                disabled=not selected_pods,
            )

        if run_pods:
            selected_pod_details = [p for p in podcast_list if p["name"] in selected_pods]
            podcast_lines = "\n".join(
                f"- {p['name']} (Host: {p.get('host', 'Unknown')}): {p.get('notes', '')}"
                for p in selected_pod_details
            )
            user_msg = (
                f"Please analyse these health and wellbeing podcasts:\n\n{podcast_lines}\n\n"
                f"Market focus: {pod_market}.\n\n"
                f"We are Digital Wellness, the technology company behind the CSIRO Total Wellbeing Diet "
                f"(Australia) and the Mayo Clinic Diet (United States). We are looking to enter the podcast "
                f"space and want to understand what's working, why these shows are successful, and what "
                f"strategic gap we can own given our institutional science credibility.\n\n"
                f"{pod_extra}"
            ).strip()

            system_prompt = load_agent_prompt(PODCAST_AGENT_PATH)

            with st.spinner("Running podcast analysis — this may take a minute..."):
                pod_output = st.empty()
                pod_buffer = []

                def on_pod_chunk(text):
                    pod_buffer.append(text)
                    pod_output.markdown("".join(pod_buffer))

                try:
                    result = run_analysis(system_prompt, user_msg, on_chunk=on_pod_chunk)
                    today = datetime.date.today().strftime("%Y-%m-%d")
                    report_path = REPORTS_DIR / f"podcast-competitor-analysis-{today}.md"
                    report_path.write_text(result)
                    st.success(f"Analysis complete! Saved to `{report_path.name}`")
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Analysis failed: {e}")


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — REPORTS LIBRARY
# ════════════════════════════════════════════════════════════════════════════
with tab_reports:
    st.header("Reports Library")
    st.caption("All generated competitor analysis reports. Click to view or download.")

    all_reports = sorted(REPORTS_DIR.glob("*.md"), reverse=True)

    if not all_reports:
        st.info("No reports generated yet. Run an analysis from the other tabs.")
    else:
        refresh_col, _ = st.columns([1, 4])
        with refresh_col:
            if st.button("🔄 Refresh list"):
                st.rerun()

        for report_path in all_reports:
            name = report_path.stem
            modified = datetime.datetime.fromtimestamp(
                report_path.stat().st_mtime
            ).strftime("%d %b %Y %H:%M")

            with st.expander(f"📄 {name}  —  _{modified}_"):
                content = report_path.read_text()
                st.markdown(content)
                st.download_button(
                    label="⬇️ Download .md",
                    data=content,
                    file_name=report_path.name,
                    mime="text/markdown",
                    key=f"dl_{name}",
                )
