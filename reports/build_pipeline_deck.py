"""
Digital Wellness — Content Strategy Pipeline Deck Builder
==========================================================
Generates a branded PowerPoint summarising:
  • How the 3-step content pipeline works
  • Step 1: Research findings (trends, keywords, GLP-1 landscape)
  • Step 2: Competitor social intelligence
  • Step 3: Video ideas (ranked list + top 3 briefs)
  • Podcast strategy summary

Usage:
    python build_pipeline_deck.py

Output:
    reports/pipeline-summary-2026-03-10.pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import datetime

# ── Brand colour palette ────────────────────────────────────────────────────
TEAL        = RGBColor(0x00, 0xC4, 0xCC)
TEAL_DARK   = RGBColor(0x00, 0x9A, 0xA0)
NAVY        = RGBColor(0x1A, 0x2B, 0x47)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
DARK_TEXT   = RGBColor(0x1F, 0x29, 0x37)
BODY_TEXT   = RGBColor(0x44, 0x44, 0x44)
MID_GREY    = RGBColor(0x88, 0x88, 0x88)
LIGHT_BG    = RGBColor(0xF0, 0xF7, 0xF8)
RULE_GREY   = RGBColor(0xCC, 0xD6, 0xDC)

SLIDE_W  = Inches(13.33)
SLIDE_H  = Inches(7.5)
FOOTER_H = 0.42
FOOTER_Y = 7.5 - FOOTER_H

prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]


# ── Low-level helpers ────────────────────────────────────────────────────────

def rect(slide, l, t, w, h, fill=None):
    shp = slide.shapes.add_shape(
        1, Inches(l), Inches(t), Inches(w), Inches(h))
    shp.line.fill.background()
    if fill:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    else:
        shp.fill.background()
    return shp


def txt(slide, text, l, t, w, h,
        size=14, bold=False, italic=False,
        color=DARK_TEXT, align=PP_ALIGN.LEFT, wrap=True):
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf  = box.text_frame
    tf.word_wrap = wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size      = Pt(size)
    run.font.bold      = bold
    run.font.italic    = italic
    run.font.color.rgb = color
    return box


def dot_pattern(slide, l, t, cols=6, rows=5, spacing=0.18, r=0.05, color=TEAL):
    for row in range(rows):
        for col in range(cols):
            x = l + col * spacing
            y = t + row * spacing
            shp = slide.shapes.add_shape(
                9, Inches(x), Inches(y), Inches(r * 2), Inches(r * 2))
            shp.fill.solid()
            shp.fill.fore_color.rgb = color
            shp.line.fill.background()


def footer(slide, page_num, url="www.digitalwellness.com"):
    rect(slide, 0, FOOTER_Y, 13.33, FOOTER_H, fill=NAVY)
    txt(slide, "Digital Wellness\u00ae",
        0.25, FOOTER_Y + 0.05, 2.2, 0.32,
        size=9, bold=True, color=WHITE)
    txt(slide, f"|   {url}",
        2.5, FOOTER_Y + 0.06, 5.0, 0.30,
        size=8, color=MID_GREY)
    txt(slide, f"PAGE {page_num}",
        11.8, FOOTER_Y + 0.06, 1.3, 0.30,
        size=8, color=MID_GREY, align=PP_ALIGN.RIGHT)


def white_bg(slide):
    rect(slide, 0, 0, 13.33, 7.5, fill=WHITE)


def teal_bg(slide):
    rect(slide, 0, 0, 13.33, 7.5, fill=TEAL)


def navy_bg(slide):
    rect(slide, 0, 0, 13.33, 7.5, fill=NAVY)


def photo_placeholder(slide, l, t, w, h, label="[ Photo ]"):
    rect(slide, l, t, w, h, fill=LIGHT_BG)
    txt(slide, label, l + w / 2 - 0.6, t + h / 2 - 0.2, 1.2, 0.4,
        size=9, color=MID_GREY, align=PP_ALIGN.CENTER)


def section_divider_white(slide, page, logo_line, title, subtitle):
    white_bg(slide)
    rect(slide, 7.8, -1.5, 7.0, 10.0, fill=NAVY)
    shp = slide.shapes.add_shape(
        9, Inches(6.8), Inches(-0.5), Inches(7.5), Inches(9.0))
    shp.fill.solid()
    shp.fill.fore_color.rgb = NAVY
    shp.line.fill.background()
    photo_placeholder(slide, 8.4, 1.2, 4.2, 4.8, "[ Image ]")
    dot_pattern(slide, 12.2, 0.2, cols=4, rows=4, spacing=0.22, r=0.04, color=WHITE)
    txt(slide, logo_line, 0.6, 1.5, 6.0, 0.45, size=11, bold=True, color=TEAL)
    txt(slide, title,     0.6, 2.1, 6.5, 1.8, size=36, bold=True, color=DARK_TEXT)
    txt(slide, subtitle,  0.6, 4.05, 6.5, 0.55, size=15, color=TEAL)
    footer(slide, page)


def section_divider_teal(slide, page, logo_line, title, subtitle):
    teal_bg(slide)
    dot_pattern(slide, 0.3, 0.3, cols=5, rows=4, spacing=0.22, r=0.04, color=WHITE)
    dot_pattern(slide, 10.8, 5.2, cols=5, rows=4, spacing=0.22, r=0.04, color=WHITE)
    txt(slide, logo_line, 0.7, 1.4, 7.0, 0.5, size=13, bold=True, color=WHITE)
    txt(slide, title,     0.7, 2.1, 8.0, 1.8, size=40, bold=True, color=WHITE)
    txt(slide, subtitle,  0.7, 4.05, 8.0, 0.5, size=15, color=WHITE)
    photo_placeholder(slide, 8.8, 1.0, 4.0, 5.0, "[ Image ]")
    footer(slide, page)


def step_card(slide, l, t, w, h, step_num, title, body):
    rect(slide, l, t, w, h, fill=LIGHT_BG)
    rect(slide, l, t, w, 0.38, fill=TEAL)
    txt(slide, step_num, l + 0.12, t + 0.06, 0.5, 0.28,
        size=9, bold=True, color=WHITE)
    txt(slide, title, l + 0.65, t + 0.07, w - 0.78, 0.28,
        size=9, bold=True, color=WHITE)
    txt(slide, body, l + 0.12, t + 0.48, w - 0.24, h - 0.6,
        size=9, color=BODY_TEXT)


def stat_card(slide, l, t, w, value, label, dark=False):
    bg = NAVY if dark else LIGHT_BG
    vc = TEAL
    lc = WHITE if dark else BODY_TEXT
    rect(slide, l, t, w, 1.55, fill=bg)
    rect(slide, l, t, w, 0.06, fill=TEAL)
    txt(slide, value, l + 0.1, t + 0.12, w - 0.2, 0.65,
        size=22, bold=True, color=vc, align=PP_ALIGN.CENTER)
    txt(slide, label, l + 0.1, t + 0.78, w - 0.2, 0.68,
        size=9, color=lc, align=PP_ALIGN.CENTER)


def pill(slide, l, t, label, bg=TEAL, fg=WHITE):
    rect(slide, l, t, 2.6, 0.38, fill=bg)
    txt(slide, label, l + 0.12, t + 0.06, 2.36, 0.28,
        size=9, bold=True, color=fg)


# ════════════════════════════════════════════════════════════════════════════
# SLIDES
# ════════════════════════════════════════════════════════════════════════════

# ── SLIDE 1 — COVER ─────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
white_bg(slide)
rect(slide, 0, 0, 0.18, 7.5, fill=TEAL)
dot_pattern(slide, 0.35, 5.2, cols=6, rows=4, spacing=0.20, r=0.04, color=TEAL)
dot_pattern(slide, 10.8, 0.25, cols=5, rows=3, spacing=0.22, r=0.04, color=TEAL)

txt(slide, "Digital Wellness\u00ae",
    0.55, 0.45, 3.5, 0.5, size=13, bold=True, color=NAVY)
txt(slide, "CSIRO  TOTAL WELLBEING DIET  \u2022  MAYO CLINIC DIET",
    4.2, 0.45, 6.5, 0.5, size=9, bold=True, color=TEAL)

txt(slide, "Content Strategy Pipeline",
    0.55, 1.55, 8.0, 0.85, size=42, bold=True, color=DARK_TEXT)
txt(slide, "Research  \u2192  Competitor Intelligence  \u2192  Video Ideas",
    0.55, 2.55, 8.0, 0.5, size=16, color=TEAL, bold=True)
txt(slide, "Includes: Podcast Competitor Analysis & Strategy",
    0.55, 3.1, 7.5, 0.4, size=13, color=BODY_TEXT)

rect(slide, 0.55, 3.75, 5.5, 0.04, fill=TEAL)
txt(slide, f"Prepared by Digital Wellness Content Team",
    0.55, 3.9, 5.5, 0.4, size=12, color=BODY_TEXT)
txt(slide, f"Date: {datetime.date.today().strftime('%B %Y')}",
    0.55, 4.35, 5.5, 0.4, size=12, color=MID_GREY)

photo_placeholder(slide, 8.2, 0.5, 4.8, 6.3, "[ Hero image ]")
footer(slide, 1)


# ── SLIDE 2 — HOW THE PIPELINE WORKS ────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
white_bg(slide)
dot_pattern(slide, 11.8, 0.3, cols=4, rows=5, spacing=0.20, r=0.04, color=TEAL)

txt(slide, "How the Content Pipeline Works",
    0.55, 0.4, 10.0, 0.65, size=26, bold=True, color=DARK_TEXT)
txt(slide, "Three sequential research phases produce prioritised, brief-ready video concepts every cycle.",
    0.55, 1.05, 10.0, 0.4, size=12, color=TEAL)

steps = [
    ("STEP 01", "Research Trends",
     "Identifies the top 5 trending topics, high-priority keywords, platform format trends, and the GLP-1 landscape. "
     "Output: strategic research report with content opportunities ranked by urgency and audience fit."),
    ("STEP 02", "Competitor Intelligence",
     "Analyses competitor social media accounts (WW, Noom, Juniper, Kic, Optislim) to map winning hooks, "
     "best-performing formats, posting cadence, and content gaps. "
     "Output: white-space map showing where no competitor holds credentialed authority."),
    ("STEP 03", "Video Ideas",
     "Synthesises Steps 1 & 2 into a ranked list of 15 video concepts, then produces full production "
     "briefs for the top 3 — including hook variations, video structure, key messages, science anchors, "
     "CTA, and production notes."),
]

card_w = 3.75
for i, (num, title, body) in enumerate(steps):
    lx = 0.45 + i * 3.95
    step_card(slide, lx, 1.65, card_w, 4.2, num, title, body)

# Arrow connectors
for i in range(2):
    ax = 0.45 + (i + 1) * 3.95 - 0.25
    txt(slide, "\u2192", ax, 3.4, 0.5, 0.5,
        size=22, bold=True, color=TEAL, align=PP_ALIGN.CENTER)

# Podcast callout bar
rect(slide, 0.45, 6.05, 12.43, 0.65, fill=NAVY)
txt(slide, "BONUS:  Podcast Competitor Analysis",
    0.7, 6.12, 4.5, 0.38, size=11, bold=True, color=TEAL)
txt(slide, "Analyses 5 top health podcasts (Huberman Lab, ZOE, Feel Better Live More, The Doctor's Kitchen, On Purpose) "
    "and identifies the unoccupied gap where Digital Wellness can enter with unique authority.",
    5.2, 6.14, 7.5, 0.38, size=9, color=WHITE)

footer(slide, 2)


# ── SLIDE 3 — SECTION DIVIDER: STEP 1 RESEARCH ──────────────────────────────
slide = prs.slides.add_slide(BLANK)
section_divider_white(
    slide, 3,
    "Digital Wellness\u00ae  |  Content Pipeline",
    "Step 1\nResearch Trends",
    "What the world is searching for right now.")


# ── SLIDE 4 — TOP 5 TRENDING TOPICS ─────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
white_bg(slide)

txt(slide, "Top 5 Trending Topics — March 2026",
    0.55, 0.38, 12.0, 0.6, size=24, bold=True, color=DARK_TEXT)
txt(slide, "Ranked by content urgency, audience fit, and competitive gap.",
    0.55, 0.98, 10.0, 0.38, size=12, color=TEAL)

topics = [
    ("01  GLP-1 Medications",
     "Wegovy pill now FDA-approved. Eli Lilly MFN pricing. 1 in 5 US adults used a GLP-1. "
     "Reddit flooded with questions on muscle loss, protein, what to eat. "
     "AU: TGA closed compounding loophole; high interest, limited access = high-intent diet program audience."),
    ("02  Intermittent Fasting Reversal",
     "Cochrane Review (Feb 2026): 22 RCTs, ~2,000 participants — IF produces 'little to no difference' "
     "vs. standard dieting. Live 60-day news hook. No competitor has responded with institutional authority. "
     "This is our credibility moment."),
    ("03  Muscle Loss on GLP-1s",
     "Up to 40% of GLP-1 weight loss may be lean muscle. Joint advisory (ACLM, ASN, Obesity Medicine Assoc, "
     "Obesity Society) recommends 1.2–1.6g protein/kg. Only 43% of GLP-1 users meet minimum threshold. "
     "CSIRO TWD and Mayo Clinic Diet are the answer — by design."),
    ("04  Perimenopause & Menopause Weight Loss",
     "1B+ TikTok views on #menopause. 'Perimenopause belly fat' is consistently high-volume and rising. "
     "2026 study: postmenopausal women on tirzepatide + HRT lost significantly more weight. "
     "No competitor is serving this group with credentialed science-backed content."),
    ("05  Gut Health & Fibermaxxing",
     "'30 plants a week' is the breakout nutrition trend of early 2026. Global digestive health market: $51B+. "
     "CSIRO TWD's high-fibre, low-GI model was built on exactly this science — "
     "an opportunity to reframe an existing feature through a trending lens."),
]

for i, (title, body) in enumerate(topics):
    col = i % 2
    row = i // 2
    lx = 0.45 + col * 6.45
    ty = 1.52 + row * 2.08
    rect(slide, lx, ty, 6.2, 1.88, fill=LIGHT_BG)
    rect(slide, lx, ty, 0.08, 1.88, fill=TEAL)
    txt(slide, title, lx + 0.22, ty + 0.12, 5.8, 0.38,
        size=10, bold=True, color=DARK_TEXT)
    txt(slide, body, lx + 0.22, ty + 0.52, 5.8, 1.28,
        size=9, color=BODY_TEXT)

# 5th card centred
if len(topics) % 2 == 1:
    i = len(topics) - 1
    title, body = topics[i]
    row = i // 2
    ty = 1.52 + row * 2.08
    rect(slide, 0.45, ty, 6.2, 1.88, fill=LIGHT_BG)
    rect(slide, 0.45, ty, 0.08, 1.88, fill=TEAL)
    txt(slide, title, 0.67, ty + 0.12, 5.8, 0.38, size=10, bold=True, color=DARK_TEXT)
    txt(slide, body,  0.67, ty + 0.52, 5.8, 1.28, size=9, color=BODY_TEXT)

footer(slide, 4)


# ── SLIDE 5 — GLP-1 LANDSCAPE ────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
white_bg(slide)

txt(slide, "The GLP-1 Landscape",
    0.55, 0.38, 9.5, 0.6, size=24, bold=True, color=DARK_TEXT)
txt(slide, "The dominant health story of 2026 — and our highest-priority content category.",
    0.55, 0.98, 9.5, 0.4, size=12, color=TEAL)

glp_stats = [
    ("1 in 5", "US adults have\nused a GLP-1 drug"),
    ("40%", "Weight lost may be\nlean muscle mass"),
    ("43%", "GLP-1 users meeting\nmin protein intake"),
    ("1.2–1.6g/kg", "Protein target per day\n(Joint advisory, 2026)"),
]
for i, (val, lbl) in enumerate(glp_stats):
    stat_card(slide, 0.45 + i * 3.18, 1.55, 2.95, val, lbl)

txt(slide, "Top Questions GLP-1 Users Are Asking",
    0.55, 3.35, 9.5, 0.4, size=13, bold=True, color=DARK_TEXT)
rect(slide, 0.55, 3.72, 12.3, 0.03, fill=TEAL)

questions = [
    ("\"What should I eat on Ozempic/Wegovy/Mounjaro?\"",
     "Highest-intent GLP-1 content question online. Mayo Clinic Diet + CSIRO TWD have the science-backed answer."),
    ("\"Will I lose muscle on Ozempic?\"",
     "Rapidly growing query. Harvard Science Review feature Feb 2026. Joint advisory from 4 US medical societies."),
    ("\"How much protein do I need on weight loss medication?\"",
     "Clinical, specific, actionable. Requires dietitian-level authority. Only CSIRO/Mayo Clinic can own this credibly."),
    ("\"What happens when you stop taking Ozempic?\"",
     "One of the most-searched GLP-1 questions. Positions structured programs as the sustainability layer."),
]
for i, (q, a) in enumerate(questions):
    ty = 3.85 + i * 0.68
    txt(slide, q, 0.55, ty, 5.9, 0.28, size=9, bold=True, color=TEAL)
    txt(slide, a, 6.6, ty, 6.2, 0.55, size=9, color=BODY_TEXT)
    if i < len(questions) - 1:
        rect(slide, 0.55, ty + 0.6, 12.3, 0.02, fill=RULE_GREY)

footer(slide, 5)


# ── SLIDE 6 — KEYWORD OPPORTUNITIES ─────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
white_bg(slide)

txt(slide, "High-Priority Keyword Opportunities",
    0.55, 0.38, 10.0, 0.6, size=24, bold=True, color=DARK_TEXT)
txt(slide, "Ranked by search intent, audience fit, and competitive gap.",
    0.55, 0.98, 10.0, 0.4, size=12, color=TEAL)

headers = ["Keyword", "Interest", "DW Angle"]
col_x   = [0.45, 5.6, 8.5]
col_w   = [5.0, 2.7, 4.45]

header_y = 1.52
row_h    = 0.46

for ci, (hdr, cx, cw) in enumerate(zip(headers, col_x, col_w)):
    rect(slide, cx, header_y, cw, row_h - 0.06, fill=NAVY)
    txt(slide, hdr, cx + 0.1, header_y + 0.09, cw - 0.2, row_h - 0.22,
        size=10, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

keywords = [
    ("what to eat on ozempic",         "Very high \u2191 surging",   "Mayo Clinic Diet Weight-Loss Medications Program; CSIRO high-protein plan"),
    ("muscle loss on Ozempic",          "Rapidly rising 2026",        "Expert dietitian explainer; joint advisory protein data"),
    ("best diet for weight loss over 50","Consistently high",         "CSIRO TWD 12-week; Mayo Clinic Diet; age-specific content"),
    ("perimenopause weight loss",        "High & rising",             "CSIRO TWD; target 40–55 female audience directly"),
    ("menopause belly fat",              "Very high",                 "Age/hormone-specific content; maps to 50+ and 35–50"),
    ("intermittent fasting vs calorie counting", "High, controversy trending", "CSIRO + Mayo Clinic 'what the science says' authority content"),
    ("science-backed weight loss program","Moderate, high conversion","Strongest DW differentiator — only CSIRO and Mayo Clinic can own this"),
    ("GLP-1 companion program",          "Low volume, rising fast",   "Category-defining opportunity — Mayo Clinic Diet already has this product"),
    ("does ozempic cause muscle loss",   "Surging 2026",              "Mayo Clinic Diet GLP-1 program; CSIRO protein research"),
    ("gut health and weight loss",       "High & growing",            "CSIRO TWD low-GI, high-fibre plan; evergreen content opportunity"),
]

row_colors = [LIGHT_BG, WHITE] * 5
for ri, (kw, interest, angle) in enumerate(keywords):
    ry = header_y + row_h + ri * (row_h - 0.06)
    bg = row_colors[ri]
    for ci, (cell, cx, cw) in enumerate(zip([kw, interest, angle], col_x, col_w)):
        rect(slide, cx, ry, cw, row_h - 0.08, fill=bg)
        c = TEAL if ci == 0 else BODY_TEXT
        b = True if ci == 0 else False
        txt(slide, cell, cx + 0.1, ry + 0.07, cw - 0.2, row_h - 0.2,
            size=8.5, color=c, bold=b)

footer(slide, 6)


# ── SLIDE 7 — SECTION DIVIDER: STEP 2 COMPETITOR ────────────────────────────
slide = prs.slides.add_slide(BLANK)
section_divider_teal(
    slide, 7,
    "Digital Wellness\u00ae  |  Content Pipeline",
    "Step 2\nCompetitor\nIntelligence",
    "Who is winning, how — and where the gaps are.")


# ── SLIDE 8 — COMPETITOR SNAPSHOT ────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
white_bg(slide)

txt(slide, "Competitor Snapshot — 5 Brands Analysed",
    0.55, 0.38, 10.0, 0.6, size=24, bold=True, color=DARK_TEXT)
txt(slide, "WW (Weight Watchers)  \u2022  Noom  \u2022  Juniper (AU)  \u2022  Kic  \u2022  Optislim (AU)",
    0.55, 0.98, 10.0, 0.38, size=11, color=TEAL, bold=True)

competitors = [
    ("WW (Weight Watchers)",
     "2.9M Facebook followers. 200K TikTok. Post-bankruptcy — trust deficit with younger audiences. "
     "GLP-1 pivot failed publicly (Hype House event). "
     "No science voice. No dietitian-led content. No muscle-loss content.",
     "Community UGC engine"),
    ("Noom",
     "Influencer-led strategy (90+ AI-matched micro-creators). Psychology & CBT angle. "
     "Skews young — very little content for 40–55 cohort. No AU-specific content. "
     "Clinical evidence almost never cited in social content.",
     "Emotional eating / behaviour psychology"),
    ("Juniper (AU)",
     "A$200M revenue (55% YoY growth). Growth via paid search + influencer UGC — not brand-channel organic. "
     "TGA-restricted: cannot name medications directly. Zero science citation. "
     "No YouTube. No protein / muscle loss content.",
     "Medical weight loss (perimenopause angle)"),
    ("Kic",
     "110K TikTok. 850K+ app downloads. 100% YoY revenue growth in Jan campaign. "
     "Body-neutral — explicitly avoids weight loss framing. No science or clinical evidence. "
     "Primary audience: 25–38. The 40–55 cohort not spoken to.",
     "Founder personal brand + anti-diet culture"),
    ("Optislim (AU)",
     "25+ years. Pharmacy distribution dominance. 7K Instagram followers — significant underperformance. "
     "No TikTok. No YouTube. No expert voice. No GLP-1 content. "
     "Social is not a primary channel at all.",
     "Retail pharmacy shelf space"),
]

for i, (name, summary, strength) in enumerate(competitors):
    col = i % 2 if i < 4 else 0
    row = i // 2
    lx = 0.45 + col * 6.45
    ty = 1.5 + row * 1.88
    if i == 4:
        lx = 0.45
    rect(slide, lx, ty, 6.2, 1.72, fill=LIGHT_BG)
    rect(slide, lx, ty, 6.2, 0.34, fill=NAVY)
    txt(slide, name, lx + 0.14, ty + 0.07, 4.5, 0.24,
        size=10, bold=True, color=WHITE)
    txt(slide, f"\u2605 {strength}", lx + 0.14, ty + 0.07, 4.9, 0.24,
        size=8, color=TEAL, align=PP_ALIGN.RIGHT)
    txt(slide, summary, lx + 0.14, ty + 0.42, 5.88, 1.22,
        size=8.5, color=BODY_TEXT)

footer(slide, 8)


# ── SLIDE 9 — CONTENT GAPS & WHITE SPACE ─────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
white_bg(slide)

txt(slide, "The White Space — Where No Competitor Has Authority",
    0.55, 0.38, 12.0, 0.6, size=24, bold=True, color=DARK_TEXT)
txt(slide, "None of the five competitors combine credentialed science + dietitian voice + high-protein program architecture.",
    0.55, 0.98, 12.0, 0.4, size=12, color=TEAL)

gaps = [
    ("Science-backed GLP-1\nSupport Content",
     "WW failed its GLP-1 pivot. Juniper is TGA-restricted. Noom lacks nutrition depth. "
     "Kic avoids GLP-1 entirely. Optislim has no social presence.\n"
     "Gap owner: Digital Wellness — CSIRO + Mayo Clinic dietitians with a protein-first program."),
    ("Credentialed Expert\nMyth-Busting Series",
     "Only 9% of nutrition TikTok content comes from dietitians. "
     "The IF Cochrane Review is a live news hook with no institutional response yet.\n"
     "Gap owner: CSIRO/Mayo Clinic dietitian to camera — the most trusted, least used format."),
    ("Perimenopause / Menopause\nWeight Science",
     "1B+ TikTok views on #menopause. None of the five competitors owning this with "
     "peer-reviewed authority. Reverse Health is pursuing the audience without the science.\n"
     "Gap owner: Digital Wellness — serving its own core 50+ audience in their language."),
    ("Long-Term Weight\nMaintenance",
     "Every competitor focuses exclusively on the loss phase. "
     "No peer-reviewed competitor data beyond 12 weeks.\n"
     "Gap owner: CSIRO's unique 5-year community cohort study — "
     "the only digital health program with this length of published follow-up."),
]

card_w = 5.9
for i, (title, body) in enumerate(gaps):
    col = i % 2
    row = i // 2
    lx = 0.45 + col * 6.45
    ty = 1.55 + row * 2.35
    rect(slide, lx, ty, card_w, 2.18, fill=LIGHT_BG)
    rect(slide, lx, ty, card_w, 0.06, fill=TEAL)
    txt(slide, title, lx + 0.18, ty + 0.14, card_w - 0.3, 0.42,
        size=11, bold=True, color=DARK_TEXT)
    txt(slide, body,  lx + 0.18, ty + 0.6,  card_w - 0.3, 1.5,
        size=9, color=BODY_TEXT)

footer(slide, 9)


# ── SLIDE 10 — SECTION DIVIDER: STEP 3 VIDEO IDEAS ──────────────────────────
slide = prs.slides.add_slide(BLANK)
section_divider_white(
    slide, 10,
    "Digital Wellness\u00ae  |  Content Pipeline",
    "Step 3\nVideo Ideas",
    "15 ranked concepts. 3 full production briefs.")


# ── SLIDE 11 — TOP 15 VIDEO CONCEPTS ─────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
white_bg(slide)
dot_pattern(slide, 11.8, 0.3, cols=4, rows=5, spacing=0.20, r=0.04, color=TEAL)

txt(slide, "Ranked Video Concept List — Top 15",
    0.55, 0.38, 10.0, 0.6, size=24, bold=True, color=DARK_TEXT)
txt(slide, "Ordered by urgency, audience fit, and competitive gap. Full briefs produced for concepts 1–3.",
    0.55, 0.98, 10.5, 0.38, size=11, color=TEAL)

concepts = [
    ("01", "What Should You Actually Eat on Ozempic? — The Science Answer",
     "YouTube Shorts + TikTok + Reels", "PRIORITY: URGENT"),
    ("02", "GLP-1s Are Causing Muscle Loss — Here's What the Science Says",
     "TikTok + Reels + YouTube Shorts", "PRIORITY: URGENT"),
    ("03", "Intermittent Fasting Doesn't Work — A 22-Study Review Just Proved It",
     "TikTok + Reels + YouTube Shorts", "PRIORITY: URGENT — 60-DAY WINDOW"),
    ("04", "Why Women Over 50 Lose Weight Differently — And What Science Says",
     "YouTube Long-Form + Facebook + Reels", "PRIORITY: HIGH"),
    ("05", "I Asked a CSIRO Dietitian to Fix My Plate for GLP-1s",
     "Instagram Reels + TikTok + Shorts", "PRIORITY: HIGH"),
    ("06", "We Tracked 50,000 Members for 5 Years — Here's What Keeps Weight Off",
     "YouTube Long-Form + Facebook", "PRIORITY: HIGH"),
    ("07", "The Protein Number GLP-1 Users Actually Need",
     "TikTok + Instagram Reels", "PRIORITY: HIGH"),
    ("08", "Perimenopause Weight Gain Is Not Your Fault (Series Pilot)",
     "TikTok + Reels + Shorts", "PRIORITY: HIGH"),
    ("09", "30 Plants a Week Sounds Impossible — We Built a Meal Plan",
     "Instagram Reels + Facebook + Shorts", "PRIORITY: MEDIUM"),
    ("10", "What Happens to Your Body When You Stop Taking Ozempic",
     "YouTube Shorts + TikTok", "PRIORITY: MEDIUM"),
    ("11", "A CSIRO Dietitian Reacts to Viral Diet TikToks (Series)",
     "TikTok + Instagram Reels", "PRIORITY: MEDIUM"),
    ("12", "Science-Backed vs. Points-Based: What 3 Million People Taught Us",
     "Facebook + YouTube Long-Form", "PRIORITY: MEDIUM"),
    ("13", "The CSIRO Total Wellbeing Diet in 60 Seconds",
     "TikTok + Reels + Shorts", "PRIORITY: MEDIUM"),
    ("14", "Week 1 on the Mayo Clinic Diet — What You Actually Eat (Series)",
     "YouTube Shorts + TikTok + Reels", "PRIORITY: MEDIUM"),
    ("15", "Why Your Health Fund Is Now Paying for Weight Loss Programs (AU)",
     "Facebook + Instagram Reels", "PRIORITY: MEDIUM"),
]

priority_colors = {
    "PRIORITY: URGENT": RGBColor(0xE0, 0x3B, 0x3B),
    "PRIORITY: URGENT — 60-DAY WINDOW": RGBColor(0xE0, 0x3B, 0x3B),
    "PRIORITY: HIGH": TEAL_DARK,
    "PRIORITY: MEDIUM": MID_GREY,
}

# Two columns
col_items = [concepts[:8], concepts[8:]]
for ci, items in enumerate(col_items):
    lx = 0.45 + ci * 6.45
    for ri, (num, title, platform, priority) in enumerate(items):
        ty = 1.52 + ri * 0.67
        pcolor = priority_colors.get(priority, MID_GREY)
        txt(slide, num, lx, ty, 0.4, 0.38,
            size=9, bold=True, color=TEAL)
        txt(slide, title, lx + 0.42, ty, 5.4, 0.28,
            size=9, bold=True, color=DARK_TEXT)
        txt(slide, platform, lx + 0.42, ty + 0.28, 3.8, 0.22,
            size=7.5, color=BODY_TEXT)
        txt(slide, priority, lx + 4.3, ty + 0.28, 2.0, 0.22,
            size=7, bold=True, color=pcolor, align=PP_ALIGN.RIGHT)
        if ri < len(items) - 1:
            rect(slide, lx, ty + 0.62, 6.2, 0.02, fill=RULE_GREY)

footer(slide, 11)


# ── SLIDE 12 — BRIEF 1: GLP-1 MUSCLE LOSS ───────────────────────────────────
slide = prs.slides.add_slide(BLANK)
white_bg(slide)

rect(slide, 0, 0, 0.12, 7.5, fill=RGBColor(0xE0, 0x3B, 0x3B))
txt(slide, "FULL BRIEF  \u2022  CONCEPT 02",
    0.35, 0.38, 5.0, 0.38, size=9, bold=True, color=RGBColor(0xE0, 0x3B, 0x3B))
txt(slide, "\u201cGLP-1s Are Causing Muscle Loss \u2014 Here\u2019s What\nthe Science Says You Should Do About It\u201d",
    0.35, 0.76, 8.0, 1.1, size=20, bold=True, color=DARK_TEXT)

# Meta bar
rect(slide, 0.35, 1.95, 8.5, 0.06, fill=TEAL)
meta = [("Platform", "TikTok \u2022 Instagram Reels \u2022 YouTube Shorts"),
        ("Length",   "45\u201375 sec (+ 3\u20135 min YouTube extended cut)"),
        ("Market",   "AU (CSIRO TWD) + US (Mayo Clinic Diet) \u2014 two branded variants")]
for i, (lbl, val) in enumerate(meta):
    ty = 2.07 + i * 0.38
    txt(slide, lbl + ":", 0.35, ty, 1.2, 0.32, size=9, bold=True, color=TEAL)
    txt(slide, val, 1.62, ty, 6.7, 0.32, size=9, color=BODY_TEXT)

# Hook
txt(slide, "HOOK (0\u20135 sec)", 0.35, 3.25, 3.5, 0.3, size=9, bold=True, color=DARK_TEXT)
rect(slide, 0.35, 3.52, 8.5, 0.76, fill=LIGHT_BG)
txt(slide, "\u201cUp to 40% of weight lost on GLP-1 medications is lean muscle.\u201d  \u2014 on screen\n"
    "\u201cIf you\u2019re on Ozempic or Mounjaro and nobody has told you this yet \u2014 you need to hear it.\u201d  \u2014 spoken",
    0.52, 3.58, 8.15, 0.65, size=9, italic=True, color=BODY_TEXT)

# Video structure
txt(slide, "VIDEO STRUCTURE", 0.35, 4.42, 3.5, 0.3, size=9, bold=True, color=DARK_TEXT)
structure = [
    ("Hook + stat on screen (0\u20135s)", "Silence forces attention. No music."),
    ("Problem plainly stated (5\u201320s)", "Up to 40% of GLP-1 weight loss may be lean mass. Muscle = metabolism + strength."),
    ("Science credential moment (20\u201330s)", "Joint advisory: 1.2\u20131.6g protein/kg/day. Only 43% of GLP-1 users meet threshold."),
    ("Actionable number (30\u201350s)", "For 80kg person: 96\u2013128g protein/day. Eat smarter, not more."),
    ("Credibility close + CTA (50\u201375s)", "[AU] CSIRO TWD link  |  [US] Mayo Clinic Diet Weight-Loss Medications Program"),
]
for i, (step, desc) in enumerate(structure):
    ty = 4.72 + i * 0.36
    txt(slide, f"\u2022 {step}:", 0.35, ty, 3.5, 0.3, size=8.5, bold=True, color=TEAL)
    txt(slide, desc, 4.0, ty, 4.7, 0.3, size=8.5, color=BODY_TEXT)

# Right column — science + why
txt(slide, "SCIENCE ANCHORS", 9.1, 0.76, 4.0, 0.3, size=9, bold=True, color=DARK_TEXT)
rect(slide, 9.1, 1.06, 3.95, 0.03, fill=TEAL)
anchors = [
    "Up to 40% of GLP-1 weight loss may be lean muscle (Harvard Science Review, Feb 2026)",
    "Joint advisory — ACLM, ASN, Obesity Medicine Assoc, Obesity Society (2026):\n1.2\u20131.6g protein/kg/day",
    "Only 43% of GLP-1 users meeting minimum protein intake",
    "CSIRO TWD: higher-protein, low-GI, backed by peer-reviewed research",
    "Mayo Clinic Diet: dedicated Weight-Loss Medications Program",
]
for i, a in enumerate(anchors):
    txt(slide, f"\u2713  {a}", 9.1, 1.16 + i * 0.68, 3.95, 0.62, size=8.5, color=BODY_TEXT)

txt(slide, "WHY THIS WILL PERFORM", 9.1, 4.65, 4.0, 0.3, size=9, bold=True, color=DARK_TEXT)
rect(slide, 9.1, 4.92, 3.95, 0.03, fill=TEAL)
txt(slide,
    "Targets the #1 GLP-1 anxiety on Reddit and TikTok (muscle loss) with an answer "
    "no competitor can match at this credibility level.\n\n"
    "WW: no science voice.\nJuniper: TGA-restricted.\nNoom: no nutrition depth.\n\n"
    "Specific protein numbers drive saves — the highest-value engagement signal.",
    9.1, 5.0, 3.95, 1.72, size=8.5, color=BODY_TEXT)

footer(slide, 12)


# ── SLIDE 13 — BRIEF 2: INTERMITTENT FASTING ─────────────────────────────────
slide = prs.slides.add_slide(BLANK)
white_bg(slide)

rect(slide, 0, 0, 0.12, 7.5, fill=RGBColor(0xE0, 0x3B, 0x3B))
txt(slide, "FULL BRIEF  \u2022  CONCEPT 03  \u2022  TIMING IS CRITICAL \u2014 60-DAY WINDOW",
    0.35, 0.38, 9.0, 0.38, size=9, bold=True, color=RGBColor(0xE0, 0x3B, 0x3B))
txt(slide, "\u201cIntermittent Fasting Doesn\u2019t Work \u2014 A 22-Study Review Just Proved It.\nHere\u2019s What Does.\u201d",
    0.35, 0.76, 8.0, 1.0, size=20, bold=True, color=DARK_TEXT)

rect(slide, 0.35, 1.85, 8.5, 0.06, fill=TEAL)
meta = [("Platform", "TikTok \u2022 Instagram Reels \u2022 YouTube Shorts \u2022 Facebook Reels"),
        ("Length",   "45\u201360 seconds"),
        ("Market",   "Both AU (CSIRO TWD) and US (Mayo Clinic Diet)")]
for i, (lbl, val) in enumerate(meta):
    ty = 1.97 + i * 0.38
    txt(slide, lbl + ":", 0.35, ty, 1.2, 0.32, size=9, bold=True, color=TEAL)
    txt(slide, val, 1.62, ty, 6.7, 0.32, size=9, color=BODY_TEXT)

txt(slide, "HOOK (0\u20135 sec)", 0.35, 3.18, 3.5, 0.3, size=9, bold=True, color=DARK_TEXT)
rect(slide, 0.35, 3.45, 8.5, 0.76, fill=LIGHT_BG)
txt(slide,
    "ON SCREEN: \u201cA review of 22 studies just found intermittent fasting produces little to no difference vs. regular dieting.\u201d\n"
    "SPOKEN: \u201cIf you\u2019ve been doing intermittent fasting and wondering why you\u2019re not getting results \u2014 science just backed you up.\u201d",
    0.52, 3.51, 8.15, 0.65, size=9, italic=True, color=BODY_TEXT)

txt(slide, "VIDEO STRUCTURE", 0.35, 4.35, 3.5, 0.3, size=9, bold=True, color=DARK_TEXT)
structure = [
    ("Hook + stat on screen (0\u20135s)", "Cochrane Review finding. Silence. Let the number do the work."),
    ("What the study found (5\u201320s)", "22 RCTs, ~2,000 participants. Gold standard of evidence. 'Little to no difference.'"),
    ("The validation moment (20\u201330s)", "Not your willpower. The structure itself doesn't have an evidence advantage."),
    ("[AU] What the science supports (30\u201350s)", "CSIRO TWD: higher protein, low-GI — average 7.2% body weight loss in 12 weeks."),
    ("[US] What the science supports (30\u201350s)", "Mayo Clinic Diet: 15 evidence-based habits, not a clock. 6\u201310 lbs in 2 weeks."),
    ("CTA (50\u201360s)", "'Ready to try something with decades of peer-reviewed research behind it?' Link in bio."),
]
for i, (step, desc) in enumerate(structure):
    ty = 4.65 + i * 0.33
    txt(slide, f"\u2022 {step}:", 0.35, ty, 3.7, 0.28, size=8.5, bold=True, color=TEAL)
    txt(slide, desc, 4.15, ty, 4.55, 0.28, size=8.5, color=BODY_TEXT)

# Right column
txt(slide, "SCIENCE ANCHORS", 9.1, 0.76, 4.0, 0.3, size=9, bold=True, color=DARK_TEXT)
rect(slide, 9.1, 1.06, 3.95, 0.03, fill=TEAL)
anchors2 = [
    "Cochrane Collaboration systematic review, Feb 2026\n22 RCTs, ~2,000 participants\nFinding: IF = 'little to no difference' vs. calorie restriction",
    "CSIRO TWD: 7.2% avg body weight loss in 12 weeks\n5-year community cohort evaluation (peer-reviewed)",
    "Mayo Clinic Diet: 15 sustainable habits\n6\u201310 lbs in 2 weeks\nRated in 10 of 11 US News Best Diets categories",
]
for i, a in enumerate(anchors2):
    txt(slide, f"\u2713  {a}", 9.1, 1.16 + i * 0.88, 3.95, 0.82, size=8.5, color=BODY_TEXT)

txt(slide, "PRODUCTION NOTE", 9.1, 3.85, 4.0, 0.3, size=9, bold=True, color=DARK_TEXT)
rect(slide, 9.1, 4.12, 3.95, 0.03, fill=RGBColor(0xE0, 0x3B, 0x3B))
txt(slide,
    "PRODUCE THIS WEEK.\n"
    "The February 2026 Cochrane Review is a live news hook. "
    "The 60-day window before news fatigue closes is already running.\n\n"
    "Plan a companion piece in the same shoot: "
    "'So what does the evidence say you SHOULD do instead?' "
    "\u2014 which delivers the CSIRO/Mayo Clinic framework as the direct answer.",
    9.1, 4.2, 3.95, 2.42, size=8.5, color=BODY_TEXT)

footer(slide, 13)


# ── SLIDE 14 — BRIEF 3: WOMEN OVER 50 ────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
white_bg(slide)

rect(slide, 0, 0, 0.12, 7.5, fill=TEAL)
txt(slide, "FULL BRIEF  \u2022  CONCEPT 04  \u2022  SERIES ANCHOR",
    0.35, 0.38, 7.0, 0.38, size=9, bold=True, color=TEAL)
txt(slide, "\u201cWhy Women Over 50 Lose Weight Differently \u2014\nAnd What the Science Says to Do About It\u201d",
    0.35, 0.76, 8.0, 1.0, size=20, bold=True, color=DARK_TEXT)

rect(slide, 0.35, 1.85, 8.5, 0.06, fill=TEAL)
meta = [("Platform", "YouTube Long-Form 8\u201312 min (primary) \u2022 Facebook/Instagram Reels (60s cut) \u2022 TikTok (45s hook)"),
        ("Market",   "Both — CSIRO TWD (AU) + Mayo Clinic Diet (US)"),
        ("Audience", "Women 45\u201365 experiencing perimenopause/postmenopause weight changes")]
for i, (lbl, val) in enumerate(meta):
    ty = 1.97 + i * 0.38
    txt(slide, lbl + ":", 0.35, ty, 1.2, 0.32, size=9, bold=True, color=TEAL)
    txt(slide, val, 1.62, ty, 6.7, 0.32, size=9, color=BODY_TEXT)

txt(slide, "YOUTUBE HOOK", 0.35, 3.18, 2.5, 0.3, size=9, bold=True, color=DARK_TEXT)
rect(slide, 0.35, 3.45, 8.5, 0.6, fill=LIGHT_BG)
txt(slide,
    "\u201cIf you\u2019ve been doing everything right \u2014 eating well, moving more \u2014 and still can\u2019t shift the weight after 50, "
    "this is not a willpower problem. Your hormones have changed the rules. "
    "And most diets were never designed for that.\u201d",
    0.52, 3.51, 8.15, 0.5, size=9, italic=True, color=BODY_TEXT)

txt(slide, "VIDEO STRUCTURE (YouTube 8\u201312 min)", 0.35, 4.18, 4.5, 0.3, size=9, bold=True, color=DARK_TEXT)
structure = [
    ("Hook + credential (0\u20131:00)", "Dietitian to camera. 'This is the most common question I get.'"),
    ("Biology of perimenopause (1:00\u20133:30)", "Oestrogen, visceral fat, sarcopenia, insulin sensitivity, hunger hormones."),
    ("Why standard diets fail (3:30\u20135:30)", "Low-cal diets accelerate muscle loss. IF worsens cortisol. Points ignore macro quality."),
    ("3 evidence-backed pillars (5:30\u20138:30)", "Higher protein + Low-GI eating + Structured support (Hope AI / Habit Optimizer)."),
    ("Real member stories (8:30\u201310:00)", "Specific outcomes. Health markers. Energy. Not before/after aesthetics."),
    ("GLP-1 + HRT context (10:00\u201311:00)", "2026 study: tirzepatide + HRT = greater loss. [US] Weight-Loss Med Program."),
    ("CTA + comment prompt (11:00\u201312:00)", "'What\u2019s been the hardest part of managing your weight after 50? I read every comment.'"),
]
for i, (step, desc) in enumerate(structure):
    ty = 4.48 + i * 0.32
    txt(slide, f"\u2022 {step}:", 0.35, ty, 3.4, 0.27, size=8.5, bold=True, color=TEAL)
    txt(slide, desc, 3.85, ty, 4.85, 0.27, size=8.5, color=BODY_TEXT)

# Right column
txt(slide, "WHY NOW", 9.1, 0.76, 4.0, 0.3, size=9, bold=True, color=DARK_TEXT)
rect(slide, 9.1, 1.06, 3.95, 0.03, fill=TEAL)
why = [
    "1B+ TikTok views on #menopause",
    "No competitor serving this group with credentialed science",
    "Reverse Health pursuing audience — without institutional authority",
    "'Perimenopause belly fat' consistently high-volume and rising",
    "2026 study: tirzepatide + HRT compound results for postmenopausal women",
]
for i, w in enumerate(why):
    txt(slide, f"\u2022  {w}", 9.1, 1.16 + i * 0.52, 3.95, 0.46, size=8.5, color=BODY_TEXT)

txt(slide, "SERIES PLAN", 9.1, 3.9, 4.0, 0.3, size=9, bold=True, color=DARK_TEXT)
rect(slide, 9.1, 4.18, 3.95, 0.03, fill=TEAL)
episodes = [
    ("Ep 01", "Why women over 50 lose weight differently (THIS BRIEF)"),
    ("Ep 02", "The protein number women over 50 actually need"),
    ("Ep 03", "Why sleep is the missing piece of midlife weight loss"),
    ("Ep 04", "Exercise after menopause — what the research says"),
]
for i, (ep, title) in enumerate(episodes):
    ty = 4.28 + i * 0.56
    txt(slide, ep, 9.1, ty, 0.55, 0.3, size=8.5, bold=True, color=TEAL)
    txt(slide, title, 9.68, ty, 3.37, 0.44, size=8.5, color=BODY_TEXT)

txt(slide, "PRESENTER NOTE", 9.1, 6.5, 4.0, 0.3, size=8, bold=True, color=MID_GREY)
txt(slide, "Female presenter, ideally 40\u201355, for authentic peer credibility. "
    "Warm kitchen/home setting \u2014 not a clinic.",
    9.1, 6.7, 3.95, 0.36, size=7.5, italic=True, color=MID_GREY)

footer(slide, 14)


# ── SLIDE 15 — SECTION DIVIDER: PODCAST STRATEGY ────────────────────────────
slide = prs.slides.add_slide(BLANK)
section_divider_teal(
    slide, 15,
    "Digital Wellness\u00ae  |  Podcast Strategy",
    "Podcast\nCompetitor\nAnalysis",
    "5 top health podcasts. The gap Digital Wellness can own.")


# ── SLIDE 16 — PODCAST LANDSCAPE ─────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
white_bg(slide)

txt(slide, "5 Podcasts Analysed — Key Findings",
    0.55, 0.38, 12.0, 0.6, size=24, bold=True, color=DARK_TEXT)
txt(slide, "Huberman Lab  \u2022  Feel Better Live More  \u2022  ZOE Science & Nutrition  \u2022  The Doctor's Kitchen  \u2022  On Purpose (Jay Shetty)",
    0.55, 0.98, 12.0, 0.38, size=10, color=TEAL, bold=True)

podcasts = [
    ("Huberman Lab", "8\u201312M downloads/month. #1 science globally. 107-min avg episodes. "
     "Science protocols + actionable takeaways per episode.\n"
     "GAP: Female 45+ alienated by biohacking frame. Heavy male guest list. No program to convert listeners.",
     "\u2605\u2605\u2605\u2605\u2605 Science depth"),
    ("Feel Better Live More", "600+ episodes. 3x/week. UK-based GP Dr. Rangan Chatterjee. "
     "Closest tone to our brand voice: 'trusted doctor who is also a good friend.'\n"
     "GAP: UK-centric. Light on peer-reviewed citations. Doesn't own weight loss science.",
     "\u2605\u2605\u2605\u2605 Emotional warmth"),
    ("ZOE Science & Nutrition", "Weekly. Tim Spector + Sarah Berry (King's College London). "
     "Uses own PREDICT programme data. Most engineered credibility of any show.\n"
     "GAP: Feels like a ZOE ad. Lacks emotional resonance. Under-serves 50+ weight loss.",
     "\u2605\u2605\u2605\u2605\u2605 Credibility architecture"),
    ("The Doctor's Kitchen", "500K monthly listeners. 3 bestselling cookbooks. "
     "'Food as medicine' — recipe-forward. Numbered-list titles are the most search-optimised.\n"
     "GAP: UK-rooted. Doesn't own structured weight loss. Recipe angle narrows audience.",
     "\u2605\u2605\u2605\u2605 Search optimisation"),
    ("On Purpose (Jay Shetty)", "35M downloads/month (self-reported). #1 Mental Health on Apple. "
     "Celebrity guests drive discovery. But: clinical credibility near zero. "
     "Controversies around credential misrepresentation.\n"
     "GAP: Health advice without clinical accountability. Huge reach, low rigour.",
     "\u2605\u2605\u2605 Mass reach"),
]

for i, (name, summary, strength) in enumerate(podcasts):
    col = i % 2 if i < 4 else 0
    row = i // 2
    lx = 0.45 + col * 6.45
    ty = 1.52 + row * 1.92
    if i == 4:
        lx = 0.45
    rect(slide, lx, ty, 6.2, 1.75, fill=LIGHT_BG)
    rect(slide, lx, ty, 6.2, 0.34, fill=NAVY)
    txt(slide, name, lx + 0.14, ty + 0.07, 4.0, 0.24, size=10, bold=True, color=WHITE)
    txt(slide, strength, lx + 0.14, ty + 0.07, 5.9, 0.24,
        size=8, color=TEAL, align=PP_ALIGN.RIGHT)
    txt(slide, summary, lx + 0.14, ty + 0.42, 5.88, 1.25, size=8.5, color=BODY_TEXT)

footer(slide, 16)


# ── SLIDE 17 — THE GAP + OUR POSITIONING ─────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
white_bg(slide)

txt(slide, "The Gap — And Our Podcast Positioning",
    0.55, 0.38, 12.0, 0.6, size=24, bold=True, color=DARK_TEXT)
txt(slide, "No podcast combines institutional science authority + emotional warmth + structured program outcomes for women 45\u201365.",
    0.55, 0.98, 12.0, 0.4, size=12, color=TEAL)

# Gap boxes
gaps = [
    ("No science-backed podcast\nfor women 45\u201365",
     "ZOE = science, no warmth, no weight focus.\nChatterjee = warmth, no peer-review rigour.\nHuberman = science, male-skewed, biohacking frame."),
    ("GLP-1 companion\ncontent absent",
     "Huberman covers the mechanism. Nobody serves the GLP-1 user audience with "
     "nutritional + behavioural support at scale.\nDirect match: Mayo Clinic Weight-Loss Medications Program."),
    ("Long-term maintenance\nnot covered",
     "Every competitor focuses on the loss phase.\nDigital Wellness owns the only peer-reviewed 5-year cohort data "
     "in digital health weight loss.\nThis is an unoccupied, defensible territory."),
    ("Australia-specific health\ncontent at scale",
     "Entire science podcast field is dominated by US and UK voices.\nCSIRO = Australia's most recognised scientific institution.\n"
     "Zero high-credibility AU health podcasts in this tier."),
]

for i, (title, body) in enumerate(gaps):
    col = i % 2
    row = i // 2
    lx = 0.45 + col * 6.45
    ty = 1.6 + row * 2.0
    rect(slide, lx, ty, 6.2, 1.82, fill=LIGHT_BG)
    rect(slide, lx, ty, 0.08, 1.82, fill=TEAL)
    txt(slide, title, lx + 0.22, ty + 0.1, 5.8, 0.5, size=11, bold=True, color=DARK_TEXT)
    txt(slide, body, lx + 0.22, ty + 0.65, 5.8, 1.1, size=9, color=BODY_TEXT)

# Positioning strip
rect(slide, 0.45, 5.72, 12.43, 0.82, fill=NAVY)
txt(slide, "OUR POSITION:",
    0.65, 5.82, 1.6, 0.38, size=10, bold=True, color=TEAL)
txt(slide, "\u201cScience that actually worked for people like you.\u201d  \u2014  "
    "Huberman cites lab studies. ZOE cites their own research. Neither anchors that research to a listener "
    "who has already completed a programme and lost 7 kilograms in 12 weeks. Digital Wellness can.",
    2.3, 5.82, 10.4, 0.6, size=9, color=WHITE)

footer(slide, 17)


# ── SLIDE 18 — PODCAST: FIRST 10 EPISODE IDEAS ───────────────────────────────
slide = prs.slides.add_slide(BLANK)
white_bg(slide)
dot_pattern(slide, 11.8, 0.3, cols=4, rows=5, spacing=0.20, r=0.04, color=TEAL)

txt(slide, "Recommended Format + First 10 Episode Ideas",
    0.55, 0.38, 10.5, 0.6, size=24, bold=True, color=DARK_TEXT)

# Format summary bar
rect(slide, 0.45, 1.05, 10.8, 0.5, fill=LIGHT_BG)
rect(slide, 0.45, 1.05, 10.8, 0.06, fill=TEAL)
txt(slide, "FORMAT:  35\u201345 min main episodes (weekly)  \u2022  10\u201315 min \u2018Science Explained\u2019 shorts (biweekly)  "
    "\u2022  Launch with 6 complete episodes  \u2022  YouTube + Apple + Spotify simultaneously",
    0.62, 1.15, 10.5, 0.35, size=9, color=BODY_TEXT)

episodes = [
    ("Why Diets Work for Two Weeks and Fail for Two Years \u2014 And What CSIRO Research Shows About Lasting Change",
     "Directly addresses repeated diet failure while anchoring the solution in CSIRO's published research."),
    ("The GLP-1 Episode: What Ozempic and Wegovy Actually Do to Your Body \u2014 And Why a Food Program Matters More Than Ever",
     "Mayo Clinic physician + endocrinologist. Strategic alignment with Eli Lilly PSP pipeline."),
    ("What Actually Happens Inside Your Body in the First 12 Weeks \u2014 A CSIRO Researcher Explains",
     "Translates the 7.2% average weight loss figure into fascinating biology. Makes the data come alive."),
    ("The Truth About Protein After 50 \u2014 Why Muscle Loss Matters More Than the Number on the Scale",
     "50\u201365 audience. Sarcopenia + protein requirements in ageing. Direct connection to CSIRO TWD's program design."),
    ("A Mayo Clinic Dietitian Answers Your Biggest Questions About Eating for a Healthy Heart",
     "Leverages Mayo Clinic cardiology credibility. Connects to the Heart Health Programme product."),
    ("Menopause, Metabolism, and Weight \u2014 What the Science Says (and What No One Is Telling You)",
     "Most underserved topic in science-backed health podcasting. No competitor owns this with institutional credibility."),
    ("How One Member Lost 11 Kilograms and Kept It Off \u2014 A Real Conversation About What the Program Feels Like",
     "Unscripted member conversation. Builds relatability without sacrificing credibility."),
    ("Ultra-Processed Food: What CSIRO's Research Shows About What It's Doing to Australian Diets",
     "Anchors the highest-engagement nutrition topic in proprietary CSIRO research."),
    ("Blood Sugar, Energy, and Why Everything You've Been Told About Snacking May Be Wrong",
     "Prediabetes audience + general energy crash audience. Mayo Clinic physician guest."),
    ("The Long Game: What People Who Maintain Weight Loss for 5 Years Have in Common",
     "Uses Digital Wellness 5-year cohort data. Owns the maintenance conversation no competitor can claim."),
]

for i, (title, desc) in enumerate(episodes):
    col = i % 2
    row = i // 2
    lx = 0.45 + col * 6.45
    ty = 1.68 + row * 1.14
    txt(slide, f"{i + 1:02d}", lx, ty, 0.42, 0.32, size=10, bold=True, color=TEAL)
    txt(slide, title, lx + 0.44, ty, 5.7, 0.36, size=8.5, bold=True, color=DARK_TEXT)
    txt(slide, desc, lx + 0.44, ty + 0.38, 5.7, 0.62, size=8, color=BODY_TEXT)
    if row < 4 and col == 0:
        rect(slide, lx, ty + 1.08, 6.2, 0.02, fill=RULE_GREY)

footer(slide, 18)


# ── SLIDE 19 — CLOSING / NEXT STEPS ──────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
navy_bg(slide)
dot_pattern(slide, 0.3, 0.3, cols=6, rows=4, spacing=0.25,
            r=0.045, color=RGBColor(0x25, 0x3C, 0x5E))

rect(slide, 0, 0, 0.22, 7.5, fill=TEAL)

txt(slide, "Making better health possible \u2014",
    0.6, 1.1, 11.5, 0.65, size=28, bold=False, color=WHITE)
txt(slide, "for everyone, for life.",
    0.6, 1.73, 11.5, 0.65, size=28, bold=True, color=TEAL)

rect(slide, 0.6, 2.55, 11.5, 0.04, fill=TEAL)

takeaways = [
    ("Act now on the IF\nCochrane Review hook.",
     "The 60-day window is already running. A dietitian-to-camera response to the February 2026 study "
     "is the highest-urgency content action from this pipeline."),
    ("Own the GLP-1\ncompanion content gap.",
     "No competitor holds institutional authority in this space. "
     "The Mayo Clinic Diet and CSIRO TWD + Eli Lilly PSP give us the product and the science. "
     "The content needs to follow."),
    ("Build the women's weight\nscience content pillar.",
     "Perimenopause and menopause weight loss is uncontested at the credentialed science level. "
     "This serves both the 50+ core and the 35\u201350 expansion audience simultaneously."),
]
for i, (bold_txt, rest) in enumerate(takeaways):
    lx = 0.6 + i * 4.15
    rect(slide, lx, 2.75, 3.9, 3.6, fill=RGBColor(0x25, 0x3C, 0x5E))
    rect(slide, lx, 2.75, 3.9, 0.07,
         fill=TEAL if i == 0 else (RGBColor(0x00, 0x9A, 0xA0) if i == 1 else TEAL_DARK))
    txt(slide, bold_txt, lx + 0.2, 2.92, 3.5, 0.55,
        size=12, bold=True, color=WHITE)
    txt(slide, rest, lx + 0.2, 3.52, 3.5, 1.7, size=9.5, color=MID_GREY)

txt(slide, "Digital Wellness\u00ae   |   www.digitalwellness.com   |   www.totalwellbeingdiet.com   |   diet.mayoclinic.org",
    0.6, 6.9, 12.0, 0.32, size=9, color=MID_GREY, align=PP_ALIGN.CENTER)

footer(slide, 19)


# ── Save ─────────────────────────────────────────────────────────────────────
out = "/home/user/ClaudeCodeTest/reports/pipeline-summary-2026-03-10.pptx"
prs.save(out)
print(f"Saved: {out}")
