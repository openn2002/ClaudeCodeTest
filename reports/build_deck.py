from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy

# ── Colour palette ──────────────────────────────────────────────
DARK_BG    = RGBColor(0x0F, 0x17, 0x2A)   # near-black navy
ACCENT     = RGBColor(0x00, 0xC2, 0x8B)   # teal/green
ACCENT2    = RGBColor(0xFF, 0x6B, 0x35)   # orange
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GREY = RGBColor(0xCC, 0xD6, 0xE8)
MID_GREY   = RGBColor(0x8A, 0x9B, 0xBF)
CARD_BG    = RGBColor(0x18, 0x25, 0x3E)   # slightly lighter than bg

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H

BLANK = prs.slide_layouts[6]  # completely blank


# ── Helpers ─────────────────────────────────────────────────────

def add_rect(slide, l, t, w, h, fill=DARK_BG, alpha=None):
    shape = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    shape.line.fill.background()
    if fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    else:
        shape.fill.background()
    return shape


def add_text(slide, text, l, t, w, h,
             size=18, bold=False, color=WHITE,
             align=PP_ALIGN.LEFT, wrap=True, italic=False):
    txBox = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txBox


def bg(slide):
    """Fill slide background."""
    add_rect(slide, 0, 0, 13.33, 7.5, fill=DARK_BG)


def accent_bar(slide, y=0.72, h=0.04):
    add_rect(slide, 0, y, 13.33, h, fill=ACCENT)


def slide_heading(slide, title, subtitle=None, y=0.18):
    add_text(slide, title, 0.5, y, 12, 0.55,
             size=28, bold=True, color=WHITE)
    if subtitle:
        add_text(slide, subtitle, 0.5, y + 0.55, 12, 0.4,
                 size=14, color=MID_GREY)


def pill(slide, text, l, t, w=1.5, h=0.32,
         bg_color=ACCENT, text_color=DARK_BG, size=11, bold=True):
    add_rect(slide, l, t, w, h, fill=bg_color)
    add_text(slide, text, l + 0.05, t + 0.03, w - 0.1, h - 0.06,
             size=size, bold=bold, color=text_color, align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════════════
# SLIDE 1 — COVER
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
bg(slide)

# large teal block left edge
add_rect(slide, 0, 0, 0.25, 7.5, fill=ACCENT)

# report label pill
add_rect(slide, 0.6, 1.2, 3.5, 0.38, fill=ACCENT)
add_text(slide, "COMPETITOR INTELLIGENCE REPORT", 0.6, 1.22, 3.5, 0.36,
         size=10, bold=True, color=DARK_BG, align=PP_ALIGN.CENTER)

add_text(slide, "Weight Loss Brands\nSocial Media Analysis", 0.6, 1.75, 11, 1.6,
         size=44, bold=True, color=WHITE)

add_rect(slide, 0.6, 3.5, 11.8, 0.05, fill=ACCENT)

add_text(slide, "Brands analysed:  Weight Watchers  ·  The Man Shake  ·  Optislim  ·  FatBlaster  ·  Juniper  ·  Kic  ·  Noom",
         0.6, 3.65, 12, 0.4, size=12, color=MID_GREY)
add_text(slide, "Platforms:  Instagram  ·  TikTok  ·  YouTube  ·  LinkedIn  ·  X / Twitter",
         0.6, 4.05, 12, 0.4, size=12, color=MID_GREY)
add_text(slide, "Date:  8 March 2026", 0.6, 4.45, 4, 0.4, size=12, color=MID_GREY)


# ════════════════════════════════════════════════════════════════
# SLIDE 2 — AGENDA
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
bg(slide)
accent_bar(slide)
slide_heading(slide, "What's Inside")

items = [
    ("01", "Brand-by-Brand Breakdown", "Follower counts, tone, hooks, formats & standout campaigns"),
    ("02", "Universal Hook Styles",    "5 proven hook patterns that dominate this niche"),
    ("03", "Top Performing Formats",   "Which content formats win on which platforms"),
    ("04", "Tone & Voice Patterns",    "How winning brands talk to their audiences"),
    ("05", "Content Gaps",             "White-space opportunities no competitor owns yet"),
    ("06", "Actionable Recommendations", "8 specific things to do next"),
]

for i, (num, title, desc) in enumerate(items):
    col = i % 2
    row = i // 2
    lx = 0.5 + col * 6.5
    ty = 1.35 + row * 1.8

    add_rect(slide, lx, ty, 6.1, 1.55, fill=CARD_BG)
    add_text(slide, num, lx + 0.15, ty + 0.12, 0.7, 0.6,
             size=26, bold=True, color=ACCENT)
    add_text(slide, title, lx + 0.85, ty + 0.12, 5.1, 0.45,
             size=14, bold=True, color=WHITE)
    add_text(slide, desc, lx + 0.85, ty + 0.58, 5.1, 0.8,
             size=11, color=MID_GREY)


# ════════════════════════════════════════════════════════════════
# SLIDE 3 — BRAND SNAPSHOT TABLE
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
bg(slide)
accent_bar(slide)
slide_heading(slide, "Brand Snapshot", "Follower scale, strongest platform & content maturity")

headers = ["Brand", "Strongest Platform", "IG Followers", "TikTok", "Content Maturity"]
rows = [
    ["Weight Watchers", "Facebook / Instagram", "~2M",    "200K",   "★★★★★  UGC machine"],
    ["Kic",             "Instagram + Podcast",  "640K",   "Active", "★★★★★  Best-in-class AU"],
    ["Noom",            "Instagram / TikTok",   "664K",   "Active", "★★★★☆  Paid-heavy"],
    ["Juniper",         "TikTok (influencer)",  "19K",    "Heavy",  "★★★★☆  GLP-1 leader"],
    ["The Man Shake",   "Facebook",             "23K",    "475",    "★★★☆☆  Sport angle unique"],
    ["Optislim",        "Instagram",            "7K",     "None",   "★★☆☆☆  Retail-reliant"],
    ["FatBlaster",      "Instagram",            "5.7K",   "None",   "★☆☆☆☆  52 posts total!"],
]

col_w  = [2.4, 2.8, 1.5, 1.3, 4.0]
col_x  = [0.4]
for w in col_w[:-1]:
    col_x.append(col_x[-1] + w + 0.05)

row_h  = 0.52
header_y = 1.3

# header row
for ci, (hdr, cx, cw) in enumerate(zip(headers, col_x, col_w)):
    add_rect(slide, cx, header_y, cw, row_h - 0.04, fill=ACCENT)
    add_text(slide, hdr, cx + 0.08, header_y + 0.08, cw - 0.16, row_h - 0.2,
             size=11, bold=True, color=DARK_BG, align=PP_ALIGN.CENTER)

maturity_colors = [ACCENT, ACCENT, ACCENT,
                   RGBColor(0x00,0xA0,0x70),
                   RGBColor(0xE8,0xA0,0x30),
                   RGBColor(0xE8,0x60,0x30),
                   ACCENT2]

for ri, row_data in enumerate(rows):
    ry = header_y + row_h + ri * row_h
    row_bg = CARD_BG if ri % 2 == 0 else RGBColor(0x14, 0x1F, 0x35)
    for ci, (cell, cx, cw) in enumerate(zip(row_data, col_x, col_w)):
        add_rect(slide, cx, ry, cw, row_h - 0.04, fill=row_bg)
        txt_color = WHITE
        if ci == 0:
            txt_color = LIGHT_GREY
            bold = True
        elif ci == 4:
            txt_color = maturity_colors[ri]
            bold = False
        else:
            bold = False
        add_text(slide, cell, cx + 0.08, ry + 0.1, cw - 0.16, row_h - 0.2,
                 size=11, bold=bold if ci==0 else False, color=txt_color,
                 align=PP_ALIGN.LEFT)


# ════════════════════════════════════════════════════════════════
# SLIDE 4 — 5 UNIVERSAL HOOK STYLES
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
bg(slide)
accent_bar(slide)
slide_heading(slide, "5 Hook Styles That Win in This Niche",
              "Patterns that appear in every high-engagement post across all 7 brands")

hooks = [
    ("01  Specific Number",
     '"Lost 19kg in 5 months."  "183 lbs gone."  "10kg in 3 weeks."',
     "Precision creates believability. Vague promises scroll past."),
    ("02  Permission",
     '"Without giving up the beers."  "No food is off-limits."  "You don\'t need the gym."',
     "Dissolves the #1 objection (sacrifice) before the pitch begins."),
    ("03  Identity Shift",
     '"I don\'t even recognise that girl."  "I finally feel like myself."',
     "People share content that articulates how they want to feel — not just what they want to achieve."),
    ("04  Curiosity / Education",
     '"Why you crave food at 11pm — the real reason."  "What GLP-1 actually does to your body."',
     "Captures high-intent search traffic on TikTok and YouTube."),
    ("05  Community Challenge",
     '"Week 3 — we\'ve hit DOUBLE DIGITS."  "Day 30 — 16 lbs down — WE DID IT."',
     "Serial structure creates narrative investment. Highest comment engagement in the niche."),
]

for i, (title, example, why) in enumerate(hooks):
    ty = 1.4 + i * 1.15
    add_rect(slide, 0.4, ty, 12.4, 1.0, fill=CARD_BG)
    add_rect(slide, 0.4, ty, 0.18, 1.0, fill=ACCENT)
    add_text(slide, title,   0.7, ty + 0.04, 3.5, 0.38,
             size=12, bold=True, color=ACCENT)
    add_text(slide, example, 0.7, ty + 0.38, 7.0, 0.36,
             size=11, italic=True, color=WHITE)
    add_text(slide, why,     8.0, ty + 0.10, 4.7, 0.75,
             size=10, color=MID_GREY)


# ════════════════════════════════════════════════════════════════
# SLIDE 5 — TOP FORMATS TABLE
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
bg(slide)
accent_bar(slide)
slide_heading(slide, "Top Performing Formats", "Which content types win — and why")

fmts = [
    ["Before/After Transformation Reels", "TikTok, Instagram",       "Visual proof in 15–30 sec. #weightlosstransformation = billions of views."],
    ["Influencer UGC + Affiliate Code",    "TikTok, Instagram",       "Social proof + FOMO + low-friction conversion. Juniper mastered this."],
    ["Educational Carousels",              "Instagram, LinkedIn",      "High saves = algorithm boost. Ideal for GLP-1 explainers, recipes."],
    ["Weekly / Serial Challenge Videos",   "TikTok, Instagram Reels", "Recurring viewers, narrative investment. Man Shake AFL series = best-in-class."],
    ["Founder / Personality-Led Video",    "Instagram, TikTok, YT",   "Humanises brand. KIC's Steph & Laura are the AU benchmark."],
    ["Recipe Demo Videos",                 "YouTube, Instagram",       "Evergreen. High shares. Zero-point / low-cal recipes perennially popular."],
    ["Podcast Clips → Reels",              "Instagram, TikTok",       "Amplifies long-form content. KICPod is the gold standard."],
    ["App Feature / Tech Walkthrough",     "Instagram, YouTube",       "Drives app downloads. WW's AI food-scanner content outperforms."],
]

col_w = [4.2, 2.8, 6.0]
col_x = [0.4, 4.7, 7.6]
headers = ["Format", "Platforms", "Why It Works"]
row_h = 0.55
header_y = 1.3

for ci, (hdr, cx, cw) in enumerate(zip(headers, col_x, col_w)):
    add_rect(slide, cx, header_y, cw, row_h - 0.05, fill=ACCENT)
    add_text(slide, hdr, cx + 0.08, header_y + 0.09, cw - 0.16, row_h - 0.2,
             size=11, bold=True, color=DARK_BG)

for ri, row_data in enumerate(fmts):
    ry = header_y + row_h + ri * row_h
    row_bg = CARD_BG if ri % 2 == 0 else RGBColor(0x14, 0x1F, 0x35)
    for ci, (cell, cx, cw) in enumerate(zip(row_data, col_x, col_w)):
        add_rect(slide, cx, ry, cw, row_h - 0.05, fill=row_bg)
        add_text(slide, cell, cx + 0.08, ry + 0.07, cw - 0.16, row_h - 0.15,
                 size=10, color=WHITE if ci == 0 else MID_GREY,
                 bold=(ci == 0))


# ════════════════════════════════════════════════════════════════
# SLIDE 6 — TONE & VOICE PATTERNS
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
bg(slide)
accent_bar(slide)
slide_heading(slide, "Tone & Voice Patterns",
              "How the market splits — and where the gaps are")

quadrants = [
    (0.4,  1.35, 6.1, 2.6, ACCENT,  "MEDICAL AUTHORITY",
     "Juniper, WW (pivoting)",
     "Clinical credibility + emotional safety.\nGrowing fastest in revenue.\nGLP-1 era demands this combination."),
    (6.7,  1.35, 6.1, 2.6, RGBColor(0x5B,0x8D,0xFF), "BODY-NEUTRAL EMPOWERMENT",
     "Kic",
     "Anti-diet, feelings-first, inclusive.\nGrowing fastest in organic social.\nOwned almost exclusively by Kic in AU."),
    (0.4,  4.15, 6.1, 2.6, ACCENT2, "MASCULINE / SPORT",
     "The Man Shake",
     "Sport, mateship, humour.\nDefensible moat — no competitor encroaches.\n\"Lose the gut without losing the beers.\""),
    (6.7,  4.15, 6.1, 2.6, RGBColor(0x88,0x88,0x88), "RETAIL-CATALOGUE",
     "Optislim, FatBlaster",
     "1990s product-forward tone.\nDoesn't translate to social.\nMinimal engagement. Opportunity for disruptors."),
]

for lx, ty, w, h, color, label, brand, desc in quadrants:
    add_rect(slide, lx, ty, w, h, fill=CARD_BG)
    add_rect(slide, lx, ty, w, 0.06, fill=color)
    add_text(slide, label, lx + 0.2, ty + 0.15, w - 0.3, 0.4,
             size=13, bold=True, color=color)
    add_text(slide, brand, lx + 0.2, ty + 0.55, w - 0.3, 0.3,
             size=11, italic=True, color=MID_GREY)
    add_rect(slide, lx + 0.2, ty + 0.88, w - 0.4, 0.03, fill=color)
    add_text(slide, desc, lx + 0.2, ty + 1.0, w - 0.4, 1.3,
             size=11, color=LIGHT_GREY)


# ════════════════════════════════════════════════════════════════
# SLIDE 7 — CONTENT GAPS
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
bg(slide)
accent_bar(slide)
slide_heading(slide, "9 Content Gaps — White Space No Competitor Owns",
              "Each gap represents an underserved audience actively searching for help")

gaps = [
    ("Men's GLP-1 Content",         "Man Shake has the audience. Nobody has the content. Zero AU brands target men + medication."),
    ("Weight Loss Over 50",          "The highest-motivated demographic. The GLP-1 audience skews older. Content ecosystem doesn't reflect this."),
    ("GLP-1 Side Effects / Nutrition","Millions on Mounjaro/semaglutide need feeding guidance. Nobody owns this content niche systematically."),
    ("Postpartum Weight Content",    "Kic's monopoly. Every other brand ignores new-parent women — a massive, motivated audience."),
    ("LinkedIn / Corporate Wellness","Zero competition. HR managers, EAP buyers, professionals. Unopened B2B channel for every brand here."),
    ("Long-Form YouTube Education",  "Independent creators dominate. Brands are absent. \"Does X programme actually work?\" — no brand answers this."),
    ("Meal Prep / Batch Cooking",    "Dominated by indie creators. No brand has a coherent weekly series. High saves + shares format."),
    ("Behind-the-Scenes Systematised","Man Shake touched this. Nobody has made it a content pillar. Builds trust with supplement-sceptical audiences."),
    ("X / Twitter Thought Leadership","Abandoned by everyone. Open channel for health professionals, public health discourse, dietitian engagement."),
]

for i, (title, desc) in enumerate(gaps):
    col = i % 3
    row = i // 3
    lx = 0.4  + col * 4.35
    ty = 1.35 + row * 1.95

    add_rect(slide, lx, ty, 4.1, 1.8, fill=CARD_BG)
    add_rect(slide, lx, ty, 0.12, 1.8, fill=ACCENT)
    pill(slide, f"#{i+1}", lx + 0.25, ty + 0.12, 0.6, 0.3,
         bg_color=DARK_BG, text_color=ACCENT, size=12, bold=True)
    add_text(slide, title, lx + 0.25, ty + 0.46, 3.7, 0.38,
             size=12, bold=True, color=WHITE)
    add_text(slide, desc,  lx + 0.25, ty + 0.85, 3.7, 0.85,
             size=10, color=MID_GREY)


# ════════════════════════════════════════════════════════════════
# SLIDE 8 — 8 RECOMMENDATIONS
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
bg(slide)
accent_bar(slide)
slide_heading(slide, "8 Actionable Recommendations",
              "Specific moves to close the gap on the leading brands")

recs = [
    ("Lead with specifics",          'Replace every generic message with a name or number. "Sarah dropped 14kg in 10 weeks" beats "lose weight fast" every time.'),
    ("Build a serial challenge",     "Commit to a 30–90 day recurring challenge. Man Shake's AFL format or KIC's Run Club are the blueprint. Narrative drives loyalty."),
    ("Micro-influencer UGC",         "Partner with 20–50 AU micro-influencers (10K–100K). Give referral codes + creative freedom. 8.2% avg engagement vs 5.3% for macro."),
    ("GLP-1 education pillar",       "Create content answering: 'What to eat on Mounjaro?' 'Will I lose muscle on Wegovy?' 'Can meal replacements + GLP-1 work together?'"),
    ("3-act transformation stories", "Structure: (1) Specific struggle → (2) Concrete turning point → (3) Identity shift. Write this into every content brief."),
    ("Optimise for search",          "Caption every post with natural search language. Instagram and TikTok are search engines. Low effort, compounds over time."),
    ("Launch LinkedIn",              "Post weekly targeting HR, EAP providers, health-conscious professionals. Opens B2B revenue channel no competitor is using."),
    ("Own YouTube education",        "Weekly 8-15 min videos on questions already being searched. 'The truth about meal replacements.' 'Week X of my journey.'"),
]

for i, (title, desc) in enumerate(recs):
    col = i % 2
    row = i // 2
    lx = 0.4 + col * 6.45
    ty = 1.35 + row * 1.5

    add_rect(slide, lx, ty, 6.1, 1.38, fill=CARD_BG)
    num_color = ACCENT if i < 4 else ACCENT2
    add_text(slide, f"{i+1:02d}", lx + 0.15, ty + 0.12, 0.55, 0.55,
             size=22, bold=True, color=num_color)
    add_text(slide, title, lx + 0.75, ty + 0.10, 5.2, 0.4,
             size=13, bold=True, color=WHITE)
    add_text(slide, desc,  lx + 0.75, ty + 0.52, 5.2, 0.75,
             size=10, color=MID_GREY)


# ════════════════════════════════════════════════════════════════
# SLIDE 9 — BRAND DEEP DIVE: WW + MAN SHAKE
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
bg(slide)
accent_bar(slide)
slide_heading(slide, "Brand Deep Dives — Weight Watchers & The Man Shake")

brands_left = {
    "name": "Weight Watchers",
    "tag":  "Community + GLP-1 pivot",
    "stats": ["IG: ~2M followers", "TikTok: 200K", "FB: 2.9M", "#weightwatchers: 3.8M+ TikTok posts"],
    "hooks": ["Zero Point food reveals", "App / AI feature drops", "Member transformation milestones", "GLP-1 + WW positioning"],
    "top":   "WW Awards · GLP-1 Companion Program · Zero Point expansions",
}
brands_right = {
    "name": "The Man Shake",
    "tag":  "Sport + Mateship + Aussie humour",
    "stats": ["IG: 23K", "FB: 95.9K (primary)", "Podcast: active", "TikTok: nascent (475 followers)"],
    "hooks": ["AFL/NRL team challenge weigh-ins", "Founder sport-legend credibility", "Celebrity kg milestones", "Behind-the-scenes factory"],
    "top":   "East Ulverstone Crows 60-Day Challenge · Merv Hughes campaign · Paul Roos partnership",
}

for brand, lx in [(brands_left, 0.4), (brands_right, 6.8)]:
    add_rect(slide, lx, 1.3, 6.1, 5.85, fill=CARD_BG)
    add_rect(slide, lx, 1.3, 6.1, 0.06, fill=ACCENT)
    add_text(slide, brand["name"], lx + 0.2, 1.42, 5.7, 0.45,
             size=16, bold=True, color=WHITE)
    add_text(slide, brand["tag"],  lx + 0.2, 1.87, 5.7, 0.32,
             size=11, italic=True, color=ACCENT)

    add_text(slide, "KEY STATS", lx + 0.2, 2.28, 5.7, 0.28,
             size=9, bold=True, color=MID_GREY)
    for j, s in enumerate(brand["stats"]):
        add_text(slide, f"• {s}", lx + 0.3, 2.56 + j * 0.28, 5.5, 0.26,
                 size=10, color=LIGHT_GREY)

    add_text(slide, "TOP HOOKS", lx + 0.2, 3.72, 5.7, 0.28,
             size=9, bold=True, color=MID_GREY)
    for j, h in enumerate(brand["hooks"]):
        add_text(slide, f"→ {h}", lx + 0.3, 4.0 + j * 0.30, 5.5, 0.28,
                 size=10, color=LIGHT_GREY)

    add_rect(slide, lx + 0.2, 5.25, 5.7, 0.03, fill=RGBColor(0x30,0x40,0x60))
    add_text(slide, "STANDOUT CAMPAIGNS", lx + 0.2, 5.35, 5.7, 0.28,
             size=9, bold=True, color=MID_GREY)
    add_text(slide, brand["top"], lx + 0.3, 5.65, 5.5, 0.9,
             size=10, color=ACCENT, italic=True)


# ════════════════════════════════════════════════════════════════
# SLIDE 10 — BRAND DEEP DIVE: JUNIPER + KIC
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
bg(slide)
accent_bar(slide)
slide_heading(slide, "Brand Deep Dives — Juniper & Kic")

brands_left = {
    "name": "Juniper (Eucalyptus Health)",
    "tag":  "Medical authority + influencer machine",
    "stats": ["IG AU: 19K", "IG UK: 21K", "Eucalyptus FY25 revenue: A$248M", "~A$103M marketing spend (2 yrs)"],
    "hooks": ["\"I lost 19kg in 5 months\"", "GLP-1 demystification (Saxenda vs Ozempic)", "\"I'm not gatekeeping — use code DONNA\"", "\"Take our quiz\" funnel (TGA-compliant)"],
    "top":   "28-Day TikTok challenge via influencer net · \"Patients outperform clinical trials\" · Black Friday 2025 controversy",
}
brands_right = {
    "name": "Kic (Keep It Cleaner)",
    "tag":  "Body neutrality + biggest AU organic footprint",
    "stats": ["IG combined: ~640K", "App ecosystem: 2.5M+", "KICPod: top AU health podcast", "Steph Claire Smith personal: ~1.5M IG"],
    "hooks": ["\"It's about how you feel, not how you look\"", "\"Join 50,000 women in the 30-Day Run\"", "Founder vulnerability (pregnancy / mental health)", "KICBUMP — physio-designed postpartum plan"],
    "top":   "Run for Joy × New Balance (2025) · KICBUMP postpartum launch · KICPod cross-brand collabs",
}

for brand, lx in [(brands_left, 0.4), (brands_right, 6.8)]:
    add_rect(slide, lx, 1.3, 6.1, 5.85, fill=CARD_BG)
    add_rect(slide, lx, 1.3, 6.1, 0.06, fill=ACCENT)
    add_text(slide, brand["name"], lx + 0.2, 1.42, 5.7, 0.45,
             size=16, bold=True, color=WHITE)
    add_text(slide, brand["tag"],  lx + 0.2, 1.87, 5.7, 0.32,
             size=11, italic=True, color=ACCENT)

    add_text(slide, "KEY STATS", lx + 0.2, 2.28, 5.7, 0.28,
             size=9, bold=True, color=MID_GREY)
    for j, s in enumerate(brand["stats"]):
        add_text(slide, f"• {s}", lx + 0.3, 2.56 + j * 0.28, 5.5, 0.26,
                 size=10, color=LIGHT_GREY)

    add_text(slide, "TOP HOOKS", lx + 0.2, 3.72, 5.7, 0.28,
             size=9, bold=True, color=MID_GREY)
    for j, h in enumerate(brand["hooks"]):
        add_text(slide, f"→ {h}", lx + 0.3, 4.0 + j * 0.30, 5.5, 0.28,
                 size=10, color=LIGHT_GREY)

    add_rect(slide, lx + 0.2, 5.25, 5.7, 0.03, fill=RGBColor(0x30,0x40,0x60))
    add_text(slide, "STANDOUT CAMPAIGNS", lx + 0.2, 5.35, 5.7, 0.28,
             size=9, bold=True, color=MID_GREY)
    add_text(slide, brand["top"], lx + 0.3, 5.65, 5.5, 0.9,
             size=10, color=ACCENT, italic=True)


# ════════════════════════════════════════════════════════════════
# SLIDE 11 — CLOSING / SUMMARY
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
bg(slide)
add_rect(slide, 0, 0, 0.25, 7.5, fill=ACCENT)
add_rect(slide, 0, 6.9, 13.33, 0.6, fill=CARD_BG)

add_text(slide, "KEY TAKEAWAYS", 0.6, 0.9, 8, 0.4,
         size=11, bold=True, color=ACCENT)
add_text(slide, "The market is splitting into two winning camps:\nMedical authority (Juniper, WW) vs Body-neutral empowerment (Kic).\nTraditional brands (Optislim, FatBlaster) are losing relevance.",
         0.6, 1.35, 12, 0.9, size=16, bold=False, color=WHITE)

add_rect(slide, 0.6, 2.4, 12, 0.04, fill=ACCENT)

three = [
    ("Specificity wins.", "Names + numbers in every post. Always."),
    ("GLP-1 is the mega-trend.", "No brand fully owns men's GLP-1, over-50, or side-effect nutrition content."),
    ("Serial content compounds.", "Challenge formats create narrative, loyalty, and recurring viewers."),
]
for i, (bold_txt, rest) in enumerate(three):
    lx = 0.6 + i * 4.25
    add_rect(slide, lx, 2.6, 4.0, 3.8, fill=CARD_BG)
    add_rect(slide, lx, 2.6, 4.0, 0.06, fill=ACCENT if i==0 else (ACCENT2 if i==2 else RGBColor(0x5B,0x8D,0xFF)))
    add_text(slide, bold_txt, lx + 0.2, 2.75, 3.6, 0.5,
             size=15, bold=True, color=WHITE)
    add_text(slide, rest, lx + 0.2, 3.3, 3.6, 1.6,
             size=12, color=MID_GREY)

add_text(slide, "Report date: 8 March 2026  ·  Brands: WW · Man Shake · Optislim · FatBlaster · Juniper · Kic · Noom",
         0.5, 7.0, 12.3, 0.35, size=9, color=MID_GREY, align=PP_ALIGN.CENTER)


# ── Save ────────────────────────────────────────────────────────
out = "/home/user/ClaudeCodeTest/reports/competitor-analysis-weight-loss-2026-03-08.pptx"
prs.save(out)
print(f"Saved: {out}")
