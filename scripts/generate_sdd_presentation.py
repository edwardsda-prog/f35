"""Generate the 12-Slide Google Cloud Spec-Driven Development (SDD) Presentation Deck (.pptx).

Designed from the perspective of a Teacher of Spec-Driven Development (SDD),
explaining how Google Antigravity (AGY), Skills, Slash Commands, and the
executable artifact ecosystem (SA_F35.md, AGENTS.md, DEMO_STORYBOARD.md,
docs/issues/INDEX.md, Brain Plan Artifacts, and /teamwork gates) were used
to build, verify, and optimize the F-35 Fleet Sustainment Agent Platform.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional, Tuple

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "app" / "assets"
DOCS_DIR = ROOT_DIR / "docs"
OUTPUT_PPTX_PATH = DOCS_DIR / "F35_Spec_Driven_Development_Google_Cloud_Deck.pptx"

CLOUD_LOGO_PATH = ASSETS_DIR / "cloud.jpeg"
RAF_ICON_PATH = ASSETS_DIR / "f35_raf_icon_256.png"

# ==============================================================================
# Google Cloud Brand & Clean Executive White Palette
# ==============================================================================
GC_BLUE = RGBColor(26, 115, 232)         # #1A73E8 Google Blue
GC_BLUE_DARK = RGBColor(23, 78, 166)     # #174EA6 Deep Navy Blue
GC_BLUE_TINT = RGBColor(232, 240, 254)   # #E8F0FE Soft Blue Fill
GC_GREEN = RGBColor(30, 142, 62)         # #1E8E3E Google Green
GC_GREEN_TINT = RGBColor(230, 244, 234)  # #E6F4EA Soft Green Fill
GC_YELLOW = RGBColor(176, 96, 0)         # #B06000 Accessible Dark Amber
GC_YELLOW_TINT = RGBColor(254, 247, 224) # #FEF7E0 Soft Amber Fill
GC_RED = RGBColor(217, 48, 37)           # #D93025 Google Red
GC_RED_TINT = RGBColor(252, 232, 230)    # #FCE8E6 Soft Red Fill
GC_PURPLE = RGBColor(126, 87, 194)       # #7E57C2 Accent Purple for Skills/Learn
GC_PURPLE_TINT = RGBColor(243, 232, 253) # #F3E8FD Soft Purple Fill

BG_WHITE = RGBColor(255, 255, 255)       # #FFFFFF Pure White Slide Background
CARD_BG = RGBColor(255, 255, 255)        # #FFFFFF Elevated Card Surface
CARD_BG_MUTED = RGBColor(248, 249, 250)  # #F8F9FA Soft Grey Card Surface
CARD_BORDER = RGBColor(218, 220, 224)    # #DADCE0 Subtle Border
HEADER_BAR_BG = RGBColor(255, 255, 255)  # #FFFFFF Header Strip
FOOTER_BAR_BG = RGBColor(248, 249, 250)  # #F8F9FA Footer Strip

TEXT_PRIMARY = RGBColor(32, 33, 36)      # #202124 Deep Charcoal
TEXT_SECONDARY = RGBColor(60, 64, 67)    # #3C4043 Dark Grey
TEXT_MUTED = RGBColor(95, 99, 104)       # #5F6368 Muted Grey
TEXT_WHITE = RGBColor(255, 255, 255)     # #FFFFFF White


# ==============================================================================
# Core Shape & Typography Helpers
# ==============================================================================
def set_slide_background(slide: Any, color: RGBColor = BG_WHITE) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(
    slide: Any,
    left: float,
    top: float,
    width: float,
    height: float,
    fill_color: RGBColor,
    border_color: Optional[RGBColor] = None,
    border_pt: float = 1.0,
    rounded: bool = True,
) -> Any:
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(
        shape_type,
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color is not None:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(border_pt)
    else:
        shape.line.fill.background()
    if rounded and hasattr(shape, "adjustments") and len(shape.adjustments) > 0:
        shape.adjustments[0] = 0.025
    return shape


def add_card(
    slide: Any,
    left: float,
    top: float,
    width: float,
    height: float,
    bg_color: RGBColor = CARD_BG,
    border_color: RGBColor = CARD_BORDER,
    border_pt: float = 1.0,
    accent_top: Optional[RGBColor] = None,
    accent_left: Optional[RGBColor] = None,
    rounded: bool = True,
) -> Any:
    card = add_rect(
        slide,
        left=left,
        top=top,
        width=width,
        height=height,
        fill_color=bg_color,
        border_color=border_color,
        border_pt=border_pt,
        rounded=rounded,
    )
    if accent_top is not None:
        add_rect(
            slide,
            left=left,
            top=top,
            width=width,
            height=0.06,
            fill_color=accent_top,
            border_color=None,
            rounded=False,
        )
    if accent_left is not None:
        add_rect(
            slide,
            left=left,
            top=top,
            width=0.08,
            height=height,
            fill_color=accent_left,
            border_color=None,
            rounded=False,
        )
    return card


def add_text_box(
    slide: Any,
    left: float,
    top: float,
    width: float,
    height: float,
    text: str = "",
    font_size: float = 12,
    bold: bool = False,
    italic: bool = False,
    color: RGBColor = TEXT_PRIMARY,
    font_name: str = "Arial",
    align: PP_ALIGN = PP_ALIGN.LEFT,
    word_wrap: bool = True,
) -> Any:
    tx_box = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = tx_box.text_frame
    tf.word_wrap = word_wrap
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.03)
    tf.margin_bottom = Inches(0.03)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return tx_box


def add_bullet_list(
    slide: Any,
    left: float,
    top: float,
    width: float,
    height: float,
    items: List[Tuple[str, str]],
    font_size: float = 10.5,
    space_after_pt: float = 5.0,
    bullet_color: RGBColor = GC_BLUE,
) -> Any:
    """Render structured (bold_lead, body_text) bullets cleanly inside one text frame."""
    tx_box = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = tx_box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.03)
    tf.margin_bottom = Inches(0.03)

    for idx, (lead, body) in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after_pt)
        p.alignment = PP_ALIGN.LEFT

        r_bullet = p.add_run()
        r_bullet.text = "▸ "
        r_bullet.font.name = "Arial"
        r_bullet.font.size = Pt(font_size)
        r_bullet.font.bold = True
        r_bullet.font.color.rgb = bullet_color

        if lead:
            r_lead = p.add_run()
            r_lead.text = lead + " "
            r_lead.font.name = "Arial"
            r_lead.font.size = Pt(font_size)
            r_lead.font.bold = True
            r_lead.font.color.rgb = TEXT_PRIMARY

        r_body = p.add_run()
        r_body.text = body
        r_body.font.name = "Arial"
        r_body.font.size = Pt(font_size)
        r_body.font.bold = False
        r_body.font.color.rgb = TEXT_SECONDARY
    return tx_box


def add_pill(
    slide: Any,
    left: float,
    top: float,
    width: float,
    height: float,
    text: str,
    fill_color: RGBColor = GC_BLUE,
    text_color: RGBColor = TEXT_WHITE,
    border_color: Optional[RGBColor] = None,
    font_size: float = 9.5,
) -> Any:
    pill = add_rect(
        slide,
        left=left,
        top=top,
        width=width,
        height=height,
        fill_color=fill_color,
        border_color=border_color,
        border_pt=1.0,
        rounded=True,
    )
    tf = pill.text_frame
    tf.word_wrap = False
    tf.margin_left = Inches(0.04)
    tf.margin_right = Inches(0.04)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = text
    r.font.name = "Arial"
    r.font.size = Pt(font_size)
    r.font.bold = True
    r.font.color.rgb = text_color
    return pill


def add_image_safe(
    slide: Any,
    image_path: Path,
    left: float,
    top: float,
    width: Optional[float] = None,
    height: Optional[float] = None,
) -> Optional[Any]:
    if not image_path.exists():
        return None
    kwargs = {}
    if width is not None:
        kwargs["width"] = Inches(width)
    if height is not None:
        kwargs["height"] = Inches(height)
    return slide.shapes.add_picture(
        str(image_path), Inches(left), Inches(top), **kwargs
    )


def add_header(
    slide: Any,
    module_badge: str,
    title: str,
    subtitle: str,
    tag_text: str = "SPEC-DRIVEN DEVELOPMENT (SDD)",
    badge_color: RGBColor = GC_BLUE,
) -> None:
    set_slide_background(slide, BG_WHITE)
    add_rect(
        slide,
        left=0.0,
        top=0.0,
        width=13.333,
        height=1.12,
        fill_color=HEADER_BAR_BG,
        border_color=CARD_BORDER,
        border_pt=0.8,
        rounded=False,
    )
    # Top 4-color Google Cloud accent bar
    stripe_w = 13.333 / 4.0
    for idx, col in enumerate([GC_BLUE, GC_RED, GC_YELLOW, GC_GREEN]):
        add_rect(
            slide,
            left=idx * stripe_w,
            top=0.0,
            width=stripe_w,
            height=0.05,
            fill_color=col,
            border_color=None,
            rounded=False,
        )

    if RAF_ICON_PATH.exists():
        add_image_safe(slide, RAF_ICON_PATH, left=0.35, top=0.16, width=0.78)

    add_pill(
        slide,
        left=1.30,
        top=0.14,
        width=2.65,
        height=0.26,
        text=module_badge,
        fill_color=badge_color,
        text_color=TEXT_WHITE,
        font_size=9.5,
    )
    add_pill(
        slide,
        left=4.05,
        top=0.14,
        width=2.75,
        height=0.26,
        text=tag_text,
        fill_color=GC_BLUE_TINT,
        text_color=GC_BLUE_DARK,
        border_color=GC_BLUE,
        font_size=9.0,
    )

    add_text_box(
        slide,
        left=1.30,
        top=0.43,
        width=10.30,
        height=0.36,
        text=title,
        font_size=18.5,
        bold=True,
        color=TEXT_PRIMARY,
    )
    add_text_box(
        slide,
        left=1.30,
        top=0.79,
        width=10.30,
        height=0.26,
        text=subtitle,
        font_size=10.5,
        italic=True,
        color=TEXT_MUTED,
    )

    if CLOUD_LOGO_PATH.exists():
        add_image_safe(slide, CLOUD_LOGO_PATH, left=11.85, top=0.18, width=1.10)


def add_footer(slide: Any, slide_num: int, total_slides: int = 13) -> None:
    add_rect(
        slide,
        left=0.0,
        top=7.12,
        width=13.333,
        height=0.38,
        fill_color=FOOTER_BAR_BG,
        border_color=CARD_BORDER,
        border_pt=0.6,
        rounded=False,
    )
    add_text_box(
        slide,
        left=0.40,
        top=7.17,
        width=8.50,
        height=0.25,
        text="Google Cloud · Antigravity Spec-Driven Development Curriculum · Case Study: F-35 Fleet Sustainment Agent (SDD-GE-F35-001)",
        font_size=8.5,
        color=TEXT_MUTED,
    )
    add_text_box(
        slide,
        left=11.50,
        top=7.17,
        width=1.45,
        height=0.25,
        text=f"Slide {slide_num} of {total_slides}",
        font_size=8.5,
        bold=True,
        color=GC_BLUE_DARK,
        align=PP_ALIGN.RIGHT,
    )


def render_stage_card(
    slide: Any,
    left: float,
    top: float,
    width: float,
    height: float,
    stage_badge: str,
    stage_title: str,
    stage_subtitle: str,
    three_points: List[Tuple[str, str]],
    ingested_text: str,
    produced_text: str,
    accent_color: RGBColor,
    tint_color: RGBColor,
) -> None:
    """Render a standardized SDD Stage Teaching Card with 3 Key Points + Ingested/Produced boxes."""
    add_card(
        slide,
        left=left,
        top=top,
        width=width,
        height=height,
        bg_color=CARD_BG,
        border_color=CARD_BORDER,
        accent_top=accent_color,
    )
    add_pill(
        slide,
        left=left + 0.18,
        top=top + 0.14,
        width=1.45,
        height=0.26,
        text=stage_badge,
        fill_color=accent_color,
        text_color=TEXT_WHITE,
        font_size=9.5,
    )
    add_text_box(
        slide,
        left=left + 1.72,
        top=top + 0.11,
        width=width - 1.88,
        height=0.30,
        text=stage_title,
        font_size=13.5,
        bold=True,
        color=TEXT_PRIMARY,
    )
    add_text_box(
        slide,
        left=left + 0.18,
        top=top + 0.43,
        width=width - 0.36,
        height=0.24,
        text=stage_subtitle,
        font_size=9.5,
        italic=True,
        color=TEXT_MUTED,
    )

    # 3 Key Points Header
    add_pill(
        slide,
        left=left + 0.18,
        top=top + 0.72,
        width=width - 0.36,
        height=0.24,
        text="THREE KEY TEACHING POINTS FOR THIS STAGE",
        fill_color=tint_color,
        text_color=TEXT_PRIMARY,
        border_color=accent_color,
        font_size=8.8,
    )

    # 3 Key Point Cards
    y_cursor = top + 1.03
    point_h = 0.92
    for idx, (pt_title, pt_body) in enumerate(three_points, start=1):
        add_card(
            slide,
            left=left + 0.18,
            top=y_cursor,
            width=width - 0.36,
            height=point_h,
            bg_color=CARD_BG_MUTED,
            border_color=CARD_BORDER,
            accent_left=accent_color,
        )
        add_text_box(
            slide,
            left=left + 0.32,
            top=y_cursor + 0.04,
            width=width - 0.58,
            height=0.22,
            text=f"Key Point {idx}: {pt_title}",
            font_size=10.2,
            bold=True,
            color=TEXT_PRIMARY,
        )
        add_text_box(
            slide,
            left=left + 0.32,
            top=y_cursor + 0.28,
            width=width - 0.58,
            height=0.60,
            text=pt_body,
            font_size=9.2,
            color=TEXT_SECONDARY,
        )
        y_cursor += point_h + 0.08

    # Bottom Ingested & Produced Artifact Boxes
    box_w = (width - 0.48) / 2.0
    box_h = 1.38
    box_top = top + height - box_h - 0.14

    # Ingested Box
    add_card(
        slide,
        left=left + 0.18,
        top=box_top,
        width=box_w,
        height=box_h,
        bg_color=GC_BLUE_TINT,
        border_color=GC_BLUE,
    )
    add_text_box(
        slide,
        left=left + 0.26,
        top=box_top + 0.06,
        width=box_w - 0.16,
        height=0.22,
        text="📥 ARTIFACTS INGESTED (INPUTS)",
        font_size=9.0,
        bold=True,
        color=GC_BLUE_DARK,
    )
    add_text_box(
        slide,
        left=left + 0.26,
        top=box_top + 0.29,
        width=box_w - 0.16,
        height=box_h - 0.34,
        text=ingested_text,
        font_size=8.6,
        color=TEXT_PRIMARY,
    )

    # Produced Box
    add_card(
        slide,
        left=left + 0.30 + box_w,
        top=box_top,
        width=box_w,
        height=box_h,
        bg_color=GC_GREEN_TINT,
        border_color=GC_GREEN,
    )
    add_text_box(
        slide,
        left=left + 0.38 + box_w,
        top=box_top + 0.06,
        width=box_w - 0.16,
        height=0.22,
        text="📤 ARTIFACTS PRODUCED (OUTPUTS)",
        font_size=9.0,
        bold=True,
        color=GC_GREEN,
    )
    add_text_box(
        slide,
        left=left + 0.38 + box_w,
        top=box_top + 0.29,
        width=box_w - 0.16,
        height=box_h - 0.34,
        text=produced_text,
        font_size=8.6,
        color=TEXT_PRIMARY,
    )


# ==============================================================================
# Slide Builders (1 to 12)
# ==============================================================================
def build_slide_1_title(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, BG_WHITE)

    # Top Google 4-color bar
    stripe_w = 13.333 / 4.0
    for idx, col in enumerate([GC_BLUE, GC_RED, GC_YELLOW, GC_GREEN]):
        add_rect(slide, idx * stripe_w, 0.0, stripe_w, 0.08, col, rounded=False)

    # Main Hero Container
    add_card(
        slide,
        left=0.45,
        top=0.35,
        width=12.43,
        height=4.45,
        bg_color=CARD_BG_MUTED,
        border_color=CARD_BORDER,
        accent_left=GC_BLUE,
    )

    if RAF_ICON_PATH.exists():
        add_image_safe(slide, RAF_ICON_PATH, left=0.80, top=0.60, width=1.05)
    if CLOUD_LOGO_PATH.exists():
        add_image_safe(slide, CLOUD_LOGO_PATH, left=11.20, top=0.60, width=1.35)

    add_pill(
        slide,
        left=2.05,
        top=0.65,
        width=3.60,
        height=0.32,
        text="ENGINEERING MASTERCLASS & PLAYBOOK",
        fill_color=GC_BLUE,
        text_color=TEXT_WHITE,
        font_size=10.0,
    )
    add_pill(
        slide,
        left=5.80,
        top=0.65,
        width=3.50,
        height=0.32,
        text="GOOGLE ANTIGRAVITY · ADK 2.0",
        fill_color=GC_BLUE_TINT,
        text_color=GC_BLUE_DARK,
        border_color=GC_BLUE,
        font_size=10.0,
    )

    add_text_box(
        slide,
        left=0.80,
        top=1.20,
        width=11.70,
        height=0.95,
        text="Spec-Driven Development (SDD) in Practice:\nBuilding the F-35 Fleet Sustainment Agent with Google Antigravity",
        font_size=26.0,
        bold=True,
        color=TEXT_PRIMARY,
    )
    add_text_box(
        slide,
        left=0.80,
        top=2.25,
        width=11.60,
        height=0.70,
        text="A Teacher's Guide to Transforming Architecture Specifications (SA_F35.md), Executable Agent Guardrails (AGENTS.md),\nDomain Skills (SKILL.md), and Self-Healing Issue Logs (ISS-001..017) into a Sub-Second Multi-Agent Production System.",
        font_size=13.0,
        color=TEXT_SECONDARY,
    )

    # Quote / Core Thesis Banner inside Hero
    add_card(
        slide,
        left=0.80,
        top=3.15,
        width=11.70,
        height=1.35,
        bg_color=GC_BLUE_TINT,
        border_color=GC_BLUE,
        accent_left=GC_BLUE_DARK,
    )
    add_text_box(
        slide,
        left=1.05,
        top=3.25,
        width=11.30,
        height=0.28,
        text="THE CORE PRINCIPLE OF SPEC-DRIVEN DEVELOPMENT:",
        font_size=10.5,
        bold=True,
        color=GC_BLUE_DARK,
    )
    add_text_box(
        slide,
        left=1.05,
        top=3.55,
        width=11.30,
        height=0.80,
        text="\"In vibe coding, prompts are ephemeral and code drifts silently from intent. In Spec-Driven Development, Specifications (SA_F35.md, DEMO_STORYBOARD.md), Guardrails (AGENTS.md), and Issue Logs (docs/issues/INDEX.md) are the primary executable artifacts—and production code is a continuously verified downstream projection.\"",
        font_size=11.5,
        italic=True,
        color=TEXT_PRIMARY,
    )

    # Bottom 4 Metric Summary Cards
    cards = [
        ("6 SDD STAGES", "End-to-End Lifecycle", "3 Key Teaching Points per stage—from Domain Spec (SA_F35.md) to /learn Self-Healing Rules.", GC_BLUE, GC_BLUE_TINT),
        ("9 DOMAIN SKILLS", "Deterministic Tooling", "Curated SKILL.md runbooks (agents-cli-*, discovery-engine) + 5 Slash Commands (/plan, /teamwork, /learn).", GC_PURPLE, GC_PURPLE_TINT),
        ("19 SUBAGENTS", "Adversarial /teamwork Gate", "Explorers, Isolated Workers, Reviewers, Challengers, Forensic & Victory Auditors (391 Passing Tests).", GC_GREEN, GC_GREEN_TINT),
        ("89%–96% FASTER", "Live EU SLA Verification", "Cut Reasoning Engine latency from 14.1s–22.3s to 0.35s–1.71s across all 10 Storyboard prompts (19/19 Gates).", GC_YELLOW, GC_YELLOW_TINT),
    ]
    card_w = 2.95
    gap = 0.21
    start_x = 0.45
    for idx, (badge, heading, desc, col, tint) in enumerate(cards):
        cx = start_x + idx * (card_w + gap)
        add_card(slide, cx, 5.00, card_w, 1.90, bg_color=CARD_BG, border_color=CARD_BORDER, accent_top=col)
        add_pill(slide, cx + 0.16, 5.16, card_w - 0.32, 0.28, badge, fill_color=tint, text_color=col, border_color=col, font_size=9.5)
        add_text_box(slide, cx + 0.16, 5.52, card_w - 0.32, 0.30, heading, font_size=12.5, bold=True, color=TEXT_PRIMARY)
        add_text_box(slide, cx + 0.16, 5.84, card_w - 0.32, 0.95, desc, font_size=9.8, color=TEXT_SECONDARY)

    add_footer(slide, 1)


def build_slide_2_principles(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(
        slide,
        module_badge="MODULE 1 · FOUNDATIONS",
        title="The Paradigm Shift: 'Vibe Coding' vs. Spec-Driven Development (SDD)",
        subtitle="Why complex defence & enterprise multi-agent systems require executable specifications, strict domain boundaries, and institutional memory.",
    )

    # Left Card: Vibe Coding vs SDD Comparison
    add_card(slide, 0.40, 1.28, 5.95, 5.65, bg_color=CARD_BG, border_color=CARD_BORDER, accent_top=GC_RED)
    add_pill(slide, 0.58, 1.44, 5.58, 0.28, "WHY TRADITIONAL 'VIBE CODING' FAILS AT SCALE", fill_color=GC_RED_TINT, text_color=GC_RED, border_color=GC_RED, font_size=9.5)

    vibe_vs_sdd = [
        ("1. Ephemeral Prompts vs. Persistent Spec:", "Vibe coding buries requirements in chat history. SDD anchors every table, tool, and prompt in SA_F35.md, .agents-cli-spec.md, and DEMO_STORYBOARD.md."),
        ("2. Context Contamination vs. Scoped AGENTS.md:", "A single agent editing SQL, React UI, and tests causes cross-layer regressions. SDD isolates Backend (/packages/api), Frontend (/packages/web), and QA (/tests)."),
        ("3. SDK Hallucinations vs. Curated Skills:", "Training weights lag behind ADK 2.0 & Gemini 3.8 Flash rules. SDD loads authoritative SKILL.md runbooks and enforces PERF-05 / SAFE-ADK-01..02."),
        ("4. Self-Grading Bias vs. Adversarial Gates:", "Single agents claim success when tests are mocked or incomplete. SDD uses /teamwork Challengers and Victory Auditors to verify live EU cloud execution."),
        ("5. Amnesia Across Sessions vs. Issue Index:", "Without a knowledge base, agents repeat failed approaches. SDD logs every RCA and 'Dead End' in docs/issues/INDEX.md (ISS-001..017) and promotes rules via /learn."),
    ]
    add_bullet_list(slide, 0.56, 1.82, 5.62, 4.95, vibe_vs_sdd, font_size=9.8, space_after_pt=7.0, bullet_color=GC_RED)

    # Right Card: The 5 Core Principles of SDD
    add_card(slide, 6.55, 1.28, 6.38, 5.65, bg_color=CARD_BG, border_color=CARD_BORDER, accent_top=GC_BLUE)
    add_pill(slide, 6.73, 1.44, 6.02, 0.28, "THE 5 FOUNDATIONAL PRINCIPLES OF SPEC-DRIVEN DEVELOPMENT", fill_color=GC_BLUE_TINT, text_color=GC_BLUE_DARK, border_color=GC_BLUE, font_size=9.5)

    principles = [
        ("P1 · Spec as Source of Truth", "SA_F35.md + DEMO_STORYBOARD.md + .agents-cli-spec.md", "Every schema (6 tables × 100 rows), document (DOC-01..09), and golden prompt is locked before coding.", GC_BLUE),
        ("P2 · Hierarchical Governance", "Root AGENTS.md + 3 Scoped Sub-Directory AGENTS.md", "Enforces 3-Phase Workflow, EU residency (REG-01), in-memory auth (PERF-01), and domain isolation.", GC_GREEN),
        ("P3 · Skill-Guided Execution", "9 SKILL.md Runbooks + 5 Slash Commands", "Injects verified patterns for ADK 2.0, Discovery Engine EU JSONL schemas, and Agent Runtime deployment.", GC_PURPLE),
        ("P4 · Adversarial Verification", "Reviewers, Challengers, Forensic & Victory Auditors", "No code merges until 391 pytest checks, ADK evals, and 19/19 live EU latency gates pass.", GC_YELLOW),
        ("P5 · Self-Healing Memory", "docs/issues/INDEX.md (ISS-001..017) + /learn Loop", "Converts production bugs (e.g. State duck-typing, uv.lock proxy drift) into permanent AGENTS.md rules.", GC_BLUE_DARK),
    ]
    y_p = 1.84
    for badge, files, desc, col in principles:
        add_card(slide, 6.73, y_p, 6.02, 0.94, bg_color=CARD_BG_MUTED, border_color=CARD_BORDER, accent_left=col)
        add_pill(slide, 6.88, y_p + 0.08, 2.25, 0.24, badge, fill_color=col, text_color=TEXT_WHITE, font_size=8.6)
        add_text_box(slide, 9.20, y_p + 0.07, 3.45, 0.24, files, font_size=8.8, bold=True, color=col)
        add_text_box(slide, 6.88, y_p + 0.36, 5.75, 0.52, desc, font_size=9.2, color=TEXT_SECONDARY)
        y_p += 1.00

    add_footer(slide, 2)


def build_slide_3_lifecycle_overview(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(
        slide,
        module_badge="MODULE 2 · WORKFLOW ARCHITECTURE",
        title="The 6-Stage Spec-Driven Development Flywheel & Artifact Lineage",
        subtitle="How human architectural intent flows through Antigravity planning, parallel multi-agent construction, adversarial verification, and self-healing rules.",
    )

    stages = [
        (
            "STAGE 0",
            "Domain & Story Spec",
            GC_BLUE,
            GC_BLUE_TINT,
            [
                ("SA_F35.md", "SDD v1.4 Dual-Track Design"),
                ("DEMO_STORYBOARD.md", "6-Prompt Golden Thread"),
                (".agents-cli-spec.md", "ADK 2.0 Machine Contract"),
                ("V&V Matrix", "TC-SQ-00..05 & TC-LP-00..05"),
            ],
        ),
        (
            "STAGE 1",
            "Executable Governance",
            GC_BLUE_DARK,
            GC_BLUE_TINT,
            [
                ("Root AGENTS.md", "REG-01, PERF-01..08, SAFE"),
                ("api/AGENTS.md", "ADK, BQ EU, SQL Canonicalizer"),
                ("web/AGENTS.md", "Sheet Card & Vega-Lite UI"),
                ("tests/AGENTS.md", "391 Unit/E2E/Eval Contracts"),
            ],
        ),
        (
            "STAGE 2",
            "Phase 1: Plan & RCA",
            GC_PURPLE,
            GC_PURPLE_TINT,
            [
                ("issues/INDEX.md", "Check Prior RCAs & Dead Ends"),
                ("/grill-me & /plan", "Resolve Edge Cases Up Front"),
                ("Brain plan_*.md", "Line-Exact Architecture Plan"),
                ("Proceed Gate", "Human Approval Before Build"),
            ],
        ),
        (
            "STAGE 3",
            "Phase 2: Parallel Build",
            GC_GREEN,
            GC_GREEN_TINT,
            [
                ("/teamwork Explorers", "3 Parallel Codebase Maps"),
                ("Isolated Worktrees", "Zero File Collision Build"),
                ("9 Domain Skills", "ADK 2.0 & DE EU Patterns"),
                ("600-Row Seed Data", "6 BQ Tables + 4 JTD Docs"),
            ],
        ),
        (
            "STAGE 4",
            "Phase 3: Adversarial V&V",
            GC_YELLOW,
            GC_YELLOW_TINT,
            [
                ("GATE_STATUS.md", "Reviewers & Challengers"),
                ("Forensic & Victory", "Anti-Cheat & 391 Pytest Run"),
                ("agents-cli deploy", "2 vCPU, 8Gi, min_instances=1"),
                ("Benchmark Harness", "19/19 EU SLA Gates (0.35–1.7s)"),
            ],
        ),
        (
            "STAGE 5",
            "Memory & /learn Loop",
            GC_RED,
            GC_RED_TINT,
            [
                ("ISS-001..017 Logs", "Full RCA & Diffs via TEMPLATE"),
                ("/learn Proposal", "Promote Rules to AGENTS.md"),
                ("16:9 Arch Diagrams", "Matplotlib Visual Verification"),
                ("Executive Decks", "Auto-Generated PPTX Slides"),
            ],
        ),
    ]

    card_w = 1.96
    gap = 0.15
    start_x = 0.40
    for idx, (badge, title, col, tint, bullets) in enumerate(stages):
        cx = start_x + idx * (card_w + gap)
        add_card(slide, cx, 1.32, card_w, 4.15, bg_color=CARD_BG, border_color=CARD_BORDER, accent_top=col)
        add_pill(slide, cx + 0.12, 1.46, card_w - 0.24, 0.25, badge, fill_color=col, text_color=TEXT_WHITE, font_size=9.0)
        add_text_box(slide, cx + 0.10, 1.76, card_w - 0.20, 0.42, title, font_size=11.0, bold=True, color=TEXT_PRIMARY, align=PP_ALIGN.CENTER)

        by = 2.24
        for b_lead, b_desc in bullets:
            add_card(slide, cx + 0.10, by, card_w - 0.20, 0.72, bg_color=tint, border_color=col)
            add_text_box(slide, cx + 0.16, by + 0.05, card_w - 0.32, 0.22, b_lead, font_size=8.8, bold=True, color=TEXT_PRIMARY)
            add_text_box(slide, cx + 0.16, by + 0.28, card_w - 0.32, 0.38, b_desc, font_size=8.0, color=TEXT_SECONDARY)
            by += 0.78

    # Bottom Self-Healing Feedback Loop Banner
    add_card(slide, 0.40, 5.62, 12.53, 1.32, bg_color=CARD_BG_MUTED, border_color=GC_BLUE, accent_left=GC_BLUE)
    add_pill(slide, 0.60, 5.76, 3.85, 0.26, "CLOSED-LOOP INSTITUTIONAL MEMORY", fill_color=GC_BLUE, text_color=TEXT_WHITE, font_size=9.0)
    add_text_box(
        slide,
        left=4.60,
        top=5.74,
        width=8.15,
        height=0.28,
        text="Why Each Iteration Makes the Agent Platform Smarter, Faster, and Safer:",
        font_size=11.5,
        bold=True,
        color=TEXT_PRIMARY,
    )
    loop_items = [
        ("Loop A — Dead-End Prevention (Stage 5 → Stage 2):", "Every bug fix records 'Section 4: Dead Ends & Approaches Rejected' in docs/issues/ISS-XXX.md. Stage 2 mandatory lookup prevents any future agent from repeating a failed experiment."),
        ("Loop B — Guardrail Promotion via /learn (Stage 5 → Stage 1):", "When production debugging uncovers a subtle SDK trap (e.g., ADK State duck-typing in ISS-017 or curly-brace KeyError in ISS-016), /learn promotes SAFE-ADK-01..02 & DEPLOY-01 directly into AGENTS.md."),
    ]
    add_bullet_list(slide, 0.60, 6.06, 12.15, 0.82, loop_items, font_size=9.3, space_after_pt=3.0, bullet_color=GC_BLUE)

    add_footer(slide, 3)


def build_slide_4_stages_0_and_1(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(
        slide,
        module_badge="MODULE 3 · STAGES 0 & 1",
        title="Stage 0 (Domain Specification) & Stage 1 (Executable Governance)",
        subtitle="Three Key Points per Stage: How SA_F35.md, DEMO_STORYBOARD.md, .agents-cli-spec.md, and hierarchical AGENTS.md files anchor the build.",
    )

    render_stage_card(
        slide,
        left=0.40,
        top=1.28,
        width=6.15,
        height=5.65,
        stage_badge="STAGE 0",
        stage_title="Domain Architecture & Storyboard Spec",
        stage_subtitle="Defining what to build, why it matters operationally, and how it is measured.",
        three_points=[
            (
                "Dual-Track Solution Design First (SA_F35.md)",
                "Authored SDD-GE-F35-001 (v1.4) before writing code—defining the 6-table, 600-record BigQuery EU warehouse, 4 S1000D/narrative docs (DOC-01..09), and 3 specialist sub-agents.",
            ),
            (
                "Executable User Storyboard (DEMO_STORYBOARD.md)",
                "Created the '6-Prompt Golden Thread' (06:30Z Oracle-to-Excel baseline to 07:00Z brief), locking in exact tail numbers (ZM151 -> ZM154), tools (JTD-53-30-T14), and outputs.",
            ),
            (
                "Machine-Verifiable CLI Contract (.agents-cli-spec.md)",
                "Used google-agents-cli-scaffold to distill SA_F35.md into .agents-cli-spec.md & agents-cli-manifest.yaml, plus quantitative V&V gates (TC-SQ-00..05 & TC-LP-00..05).",
            ),
        ],
        ingested_text="• UK Defence Reference Architecture (SDD-GE-UKD-002)\n• ODIN / MOD Form 707A & S1000D domain standards\n• Skill: google-agents-cli-scaffold & workflow",
        produced_text="• SA_F35.md (Solution Design Document v1.4)\n• DEMO_STORYBOARD.md (6-Prompt Golden Thread)\n• .agents-cli-spec.md & agents-cli-manifest.yaml",
        accent_color=GC_BLUE,
        tint_color=GC_BLUE_TINT,
    )

    render_stage_card(
        slide,
        left=6.78,
        top=1.28,
        width=6.15,
        height=5.65,
        stage_badge="STAGE 1",
        stage_title="Executable Governance (AGENTS.md)",
        stage_subtitle="Encoding architectural decisions into always-on guardrails and domain boundaries.",
        three_points=[
            (
                "Mandatory Invariants in Root AGENTS.md",
                "Encoded 11 non-negotiable guardrails: REG-01 (EU residency), PERF-01..08 (in-memory auth, pageSize=15, <=4KB tool slimming), SAFE-ADK-01..02, and DEPLOY-01 (uv.lock hygiene).",
            ),
            (
                "Directory-Scoped Specialization Boundaries",
                "Partitioned the monorepo via packages/api/AGENTS.md (ADK/BQ), packages/web/AGENTS.md (Sheet Card/Vega UI), and tests/AGENTS.md (QA) so subagents never collide.",
            ),
            (
                "Enforced Three-Phase Orchestration Protocol",
                "Mandated Phase 1 (Single-Orchestrator Plan & Issue Lookup) -> Phase 2 (Isolated Parallel Subagent Build) -> Phase 3 (Integration, Testing & ISS-XXX Logging).",
            ),
        ],
        ingested_text="• SA_F35.md & .agents-cli-spec.md\n• Gemini 3.8 Flash & ADK 2.0 SDK constraints\n• Skill: agy-customizations (Rule hierarchy)",
        produced_text="• Root AGENTS.md (Always-on workspace rulebook)\n• packages/api/AGENTS.md & packages/web/AGENTS.md\n• tests/AGENTS.md (V&V test matrix & QA boundary)",
        accent_color=GC_BLUE_DARK,
        tint_color=GC_BLUE_TINT,
    )

    add_footer(slide, 4)


def build_slide_5_stages_2_and_3(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(
        slide,
        module_badge="MODULE 4 · STAGES 2 & 3",
        title="Stage 2 (Pre-Code Planning & RCA Lookup) & Stage 3 (Parallel Multi-Agent Build)",
        subtitle="Three Key Points per Stage: Consulting institutional memory before planning, then executing in parallel worktrees with specialized skills.",
    )

    render_stage_card(
        slide,
        left=0.40,
        top=1.28,
        width=6.15,
        height=5.65,
        stage_badge="STAGE 2",
        stage_title="Phase 1 Planning & Issue Index Lookup",
        stage_subtitle="Looking backward at past root causes before designing forward.",
        three_points=[
            (
                "Mandatory Pre-Change Lookup (docs/issues/INDEX.md)",
                "Before touching code, the orchestrator inspects INDEX.md and 'Section 4: Dead Ends' in prior ISS-001..017 logs so solved bugs and rejected approaches are never repeated.",
            ),
            (
                "Empirical Profiling & Brain Plan Artifacts (/plan)",
                "Profiles live EU telemetry first (e.g. proving in ISS-017 that 95% of 14–27s latency was LLM hops & 68KB tool blobs, not BigQuery) and writes brain/plan_*.md artifacts.",
            ),
            (
                "Interactive Alignment & Human Gate (/grill-me)",
                "Uses /grill-me to stress-test edge cases (e.g. 3-Layer Semantic SQL Ontology in ISS-013) and presents the Plan Artifact with RequestFeedback=True for explicit approval.",
            ),
        ],
        ingested_text="• docs/issues/INDEX.md & ISS-001..016 records\n• Live Reasoning Engine :streamQuery telemetry\n• Slash Commands: /plan & /grill-me",
        produced_text="• Brain Artifact: plan_issues_1_to_8_resolution.md\n• Brain Artifact: plan_iss015_capability_...md\n• Brain Artifact: plan_iss017_production_latency_...md",
        accent_color=GC_PURPLE,
        tint_color=GC_PURPLE_TINT,
    )

    render_stage_card(
        slide,
        left=6.78,
        top=1.28,
        width=6.15,
        height=5.65,
        stage_badge="STAGE 3",
        stage_title="Phase 2 Parallel Multi-Agent Build",
        stage_subtitle="Decomposing approved plans into isolated Explorer and Worker subagents.",
        three_points=[
            (
                "Parallel Explorer Subagents for Line-Exact Specs",
                "Under /teamwork, 3 read-only Explorers (teamwork_explorer_r1_1..3) scan app/, tests/, and docs/ in parallel, producing line-exact handoff.md implementation blueprints.",
            ),
            (
                "Skill-Driven Implementation in Isolated Worktrees",
                "Workers apply google-agents-cli-adk-code & discovery-engine-adk-integration skills to build pre-warmed EU singletons, 3-Layer SQL Canonicalizer, and OPT-01..06 callbacks.",
            ),
            (
                "Declarative 600-Row Warehouse & S1000D Corpus",
                "Couples bq_seed_records.py (6 tables × 100 rows = 600 records) and jtd_corpus.py (DOC-01..09) with declarative .schema.json files and setup_demo_infra.py.",
            ),
        ],
        ingested_text="• Approved Brain plan_*.md & SCOPE.md / DISPATCH.md\n• Skills: google-agents-cli-adk-code, discovery-engine\n• Declarative schemas (app/seed_data/schemas/*.json)",
        produced_text="• app/ (agent.py, callbacks.py, sub_agents/, tools/)\n• packages/web/ (MaintenanceSheetCard.tsx, VegaCanvas)\n• .agents/teamwork/*/handoff.md & progress.md",
        accent_color=GC_GREEN,
        tint_color=GC_GREEN_TINT,
    )

    add_footer(slide, 5)


def build_slide_6_stages_4_and_5(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(
        slide,
        module_badge="MODULE 5 · STAGES 4 & 5",
        title="Stage 4 (Adversarial Verification & Cloud SLA Gate) & Stage 5 (Memory & /learn)",
        subtitle="Three Key Points per Stage: Proving sub-2-second cloud execution with independent auditors and encoding lessons back into AGENTS.md.",
    )

    render_stage_card(
        slide,
        left=0.40,
        top=1.28,
        width=6.15,
        height=5.65,
        stage_badge="STAGE 4",
        stage_title="Adversarial V&V, Deploy & Benchmarking",
        stage_subtitle="Zero-trust verification across unit tests, live EU cloud deployment, and SLA gates.",
        three_points=[
            (
                "5-Role Adversarial Gate (GATE_STATUS.md)",
                "Every worker build is audited by 2 Reviewers, 2 Challengers (who caught 3 callback edge cases in ISS-017 Iteration 1), 1 Forensic Auditor, and 1 Victory Auditor.",
            ),
            (
                "391 Automated Tests & Clean PyPI Deploy (DEPLOY-01)",
                "Runs 391 pytest unit/E2E/eval tests + vv_golden_suite.json, verifies 0 airlock-proxy URLs in uv.lock, and deploys to Agent Runtime (2 vCPU, 8Gi, min_instances=1).",
            ),
            (
                "Live EU Production Benchmarking (19/19 Gates PASS)",
                "Executes benchmark_harness.py over live :streamQuery in europe-west1, proving an 89%–96% latency reduction (14.1s–22.3s -> 0.35s–1.71s) across all 10 Storyboard prompts.",
            ),
        ],
        ingested_text="• tests/eval/datasets/vv_golden_suite.json\n• Skills: google-agents-cli-eval, deploy, publish\n• Live Vertex AI Reasoning Engine (5022570215192395776)",
        produced_text="• GATE_STATUS.md & teamwork_victory_auditor_1/handoff.md\n• deployment_metadata.json (2 vCPU / 8Gi / min=1)\n• PERFORMANCE_BENCHMARK_REPORT.md (19/19 PASS)",
        accent_color=GC_YELLOW,
        tint_color=GC_YELLOW_TINT,
    )

    render_stage_card(
        slide,
        left=6.78,
        top=1.28,
        width=6.15,
        height=5.65,
        stage_badge="STAGE 5",
        stage_title="Institutional Memory & /learn Loop",
        stage_subtitle="Turning every resolved issue into a permanent guardrail and executive deliverable.",
        three_points=[
            (
                "Standardized Issue & RCA Archive (ISS-001..017)",
                "Every fix is logged via docs/issues/TEMPLATE.md and indexed in INDEX.md by Chronology, Sub-Agent Domain, and Guardrail / V&V Test ID.",
            ),
            (
                "Self-Healing Rule Promotion via /learn",
                "Distills root causes into learning_proposal.md and patches AGENTS.md with new invariants (SAFE-ADK-01 State duck-typing, SAFE-ADK-02 no {var} braces, PERF-08, DEPLOY-01).",
            ),
            (
                "Programmatic Executive Decks & Visual QA",
                "Generates 16:9 architecture slides (generate_architecture_slides.py) and PowerPoint decks, rendering slide PNGs and visually inspecting them via read_file.",
            ),
        ],
        ingested_text="• docs/issues/TEMPLATE.md & benchmark telemetry\n• Slash Commands: /learn & /goal\n• Skill: agy-customizations",
        produced_text="• docs/issues/ISS-001..017.md & updated INDEX.md\n• Brain Artifact: learning_proposal.md -> AGENTS.md\n• F35_POC_ONE_PAGE_ARCHITECTURE.md & PPTX Decks",
        accent_color=GC_RED,
        tint_color=GC_RED_TINT,
    )

    add_footer(slide, 6)


def build_slide_7_artifact_matrix(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(
        slide,
        module_badge="MODULE 6 · ARTIFACT ECOSYSTEM",
        title="The Complete Antigravity Artifact Matrix: Ingested vs. Produced",
        subtitle="How repository specifications, Brain planning artifacts, /teamwork handoffs, and issue logs form an unbroken chain of custody.",
    )

    headers = [
        ("Artifact Layer", 2.05),
        ("Concrete Files in F-35 Project", 3.25),
        ("Produced By", 1.85),
        ("Ingested By", 1.95),
        ("Engineering Role in SDD Workflow", 3.43),
    ]
    rows = [
        ("1. Solution Design (SDD)", "SA_F35.md (SDD-GE-F35-001 v1.4)", "Architect + AGY", "Orchestrator & All Subagents", "Master blueprint for 3 sub-agents, 6 BQ tables (600 rows) & 4 JTD manuals."),
        ("2. User Storyboard", "DEMO_STORYBOARD.md (6 Golden Prompts)", "Architect + /grill-me", "Challengers & Benchmark Suite", "Locks exact prompts, tail swaps (ZM151->ZM154), tools & talk-track."),
        ("3. CLI & Runtime Spec", ".agents-cli-spec.md, agents-cli-manifest.yaml", "agents-cli scaffold", "agents-cli deploy & publish", "Binds ADK 2.0 App(name='app') to Reasoning Engine 5022570215192395776."),
        ("4. Governance Rules", "Root AGENTS.md + api/, web/, tests/ AGENTS.md", "Architect + /learn", "All AGY Agents (always_on)", "Enforces 3-Phase workflow, domain boundaries & REG-01 / PERF-01..08 / SAFE-ADK."),
        ("5. Brain Plan Artifacts", "brain/<id>/plan_iss015.md, plan_iss017.md", "AGY Orchestrator (/plan)", "Human Gate & Worker Agents", "Presents empirical latency profiling, Mermaid diagrams & diffs before coding."),
        ("6. /teamwork Audit Trail", ".agents/teamwork/*/DISPATCH, handoff, GATE_STATUS", "19 /teamwork Subagents", "Orchestrator & Victory Auditor", "Tracks parallel Explorer specs, Worker diffs & Reviewer/Challenger verdicts."),
        ("7. Data & Eval Contracts", "schemas/*.schema.json, vv_golden_suite.json", "Backend & QA Agents", "BigQuery EU, pytest, ADK eval", "Enforces 600-row FK integrity, 391 pytest checks & TC-SQ / TC-LP gates."),
        ("8. Issue Knowledge Base", "docs/issues/INDEX.md, TEMPLATE.md, ISS-001..017", "Orchestrator (Phase 3)", "All Future Agents (Stage 2)", "Records symptoms, RCAs, diffs & Section 4 Dead Ends to prevent regressions."),
        ("9. Benchmarks & Decks", "PERFORMANCE_BENCHMARK_REPORT.md, docs/*.pptx", "benchmark_harness & Scripts", "Leadership & Engineering Teams", "Proves 19/19 EU SLA gates (0.35s–1.71s) & renders Google Cloud slide decks."),
    ]

    x_start = 0.40
    y_top = 1.30
    header_h = 0.36
    row_h = 0.57

    # Draw Table Header
    cur_x = x_start
    for col_title, col_w in headers:
        add_rect(slide, cur_x, y_top, col_w, header_h, fill_color=GC_BLUE_DARK, border_color=CARD_BORDER, rounded=False)
        add_text_box(slide, cur_x + 0.06, y_top + 0.06, col_w - 0.12, header_h - 0.10, col_title, font_size=9.5, bold=True, color=TEXT_WHITE)
        cur_x += col_w

    # Draw Rows
    for r_idx, row_vals in enumerate(rows):
        ry = y_top + header_h + r_idx * row_h
        bg = CARD_BG if r_idx % 2 == 0 else CARD_BG_MUTED
        cur_x = x_start
        for c_idx, (val, (_, col_w)) in enumerate(zip(row_vals, headers)):
            cell_bg = GC_BLUE_TINT if c_idx == 0 else bg
            add_rect(slide, cur_x, ry, col_w, row_h, fill_color=cell_bg, border_color=CARD_BORDER, rounded=False)
            add_text_box(
                slide,
                cur_x + 0.06,
                ry + 0.05,
                col_w - 0.12,
                row_h - 0.08,
                val,
                font_size=8.8 if c_idx > 0 else 9.0,
                bold=(c_idx in (0, 1)),
                color=GC_BLUE_DARK if c_idx == 0 else TEXT_PRIMARY,
            )
            cur_x += col_w

    add_footer(slide, 7)


def build_slide_8_skills_and_commands(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(
        slide,
        module_badge="MODULE 7 · SKILLS & SLASH COMMANDS",
        title="How Antigravity Skills (SKILL.md) & Slash Commands Accelerate Delivery",
        subtitle="Eliminating SDK guesswork with on-demand procedural runbooks and structured human-in-the-loop slash workflows.",
    )

    # Left Column: 9 Specialized Skills
    add_card(slide, 0.40, 1.28, 6.85, 5.65, bg_color=CARD_BG, border_color=CARD_BORDER, accent_top=GC_PURPLE)
    add_pill(slide, 0.58, 1.44, 6.48, 0.28, "9 ON-DEMAND ANTIGRAVITY SKILLS (SKILL.md) USED IN THIS PROJECT", fill_color=GC_PURPLE_TINT, text_color=GC_PURPLE, border_color=GC_PURPLE, font_size=9.5)

    skills_list = [
        ("google-agents-cli-workflow:", "Master ADK 2.0 lifecycle guide (scaffold -> build -> evaluate -> deploy -> publish -> observe) & code preservation rules."),
        ("google-agents-cli-scaffold:", "Generated .agents-cli-spec.md, agents-cli-manifest.yaml, Dockerfile, and FastAPI/A2A/AdkApp adapter wiring."),
        ("google-agents-cli-adk-code:", "Provided verified ADK 2.0 patterns for LlmAgent, ResumabilityConfig, ContextCacheConfig, and before/after tool callbacks."),
        ("discovery-engine-adk-integration:", "Runbook for EU Discovery Engine JSONL _id schemas (ISS-003), pageSize=15 single-pass search, and extractive spec handling (ISS-002)."),
        ("google-agents-cli-eval:", "Structured vv_golden_suite.json (TC-SQ-00..05, TC-LP-00..05) and resolved ADK session state_delta initialization (ISS-001)."),
        ("google-agents-cli-deploy:", "Managed Vertex AI Agent Runtime deployment in europe-west1, uv.lock PyPI hygiene (ISS-007), and 2 vCPU / 8Gi / min_instances=1 scaling."),
        ("google-agents-cli-publish:", "Registered the Reasoning Engine natively with Gemini Enterprise (f35-support in eu) and patched the custom RAF F-35 icon (ISS-006)."),
        ("adk-agent-observability:", "Configured OpenTelemetry GenAI spans (NO_CONTENT privacy) and per-event :streamQuery stage timing for ISS-017."),
        ("agy-customizations:", "Guided hierarchical AGENTS.md authoring and /learn rule promotion (SAFE-ADK-01..02, PERF-08, DEPLOY-01)."),
    ]
    add_bullet_list(slide, 0.56, 1.80, 6.52, 5.00, skills_list, font_size=9.0, space_after_pt=4.2, bullet_color=GC_PURPLE)

    # Right Column: 5 Slash Commands
    add_card(slide, 7.42, 1.28, 5.51, 5.65, bg_color=CARD_BG, border_color=CARD_BORDER, accent_top=GC_BLUE)
    add_pill(slide, 7.60, 1.44, 5.15, 0.28, "5 SLASH COMMANDS ORCHESTRATING THE WORKFLOW", fill_color=GC_BLUE_TINT, text_color=GC_BLUE_DARK, border_color=GC_BLUE, font_size=9.5)

    commands = [
        ("/grill-me", "Interactive Design Interview", "Stress-tests requirements before planning—used to align the 6-Prompt Storyboard and 3-Layer Semantic Ontology.", GC_BLUE),
        ("/plan", "Phase 1 Architecture Plan", "Produces line-referenced Brain Plan Artifacts (plan_iss015.md, plan_iss017.md) with Proceed approval gates.", GC_BLUE_DARK),
        ("/teamwork", "Autonomous Multi-Agent Team", "Spawns Explorers, Isolated Workers, Reviewers, Challengers, Forensic & Victory Auditors across parallel worktrees.", GC_GREEN),
        ("/learn", "Self-Healing Rule Promotion", "Distills root causes from debugging into learning_proposal.md and permanent AGENTS.md guardrails.", GC_PURPLE),
        ("/goal", "Thorough End-to-End Execution", "Runs complex multi-deliverable tasks with continuous self-auditing until every acceptance criterion is verified.", GC_YELLOW),
    ]
    cy = 1.84
    for cmd, title, desc, col in commands:
        add_card(slide, 7.60, cy, 5.15, 0.94, bg_color=CARD_BG_MUTED, border_color=CARD_BORDER, accent_left=col)
        add_pill(slide, 7.75, cy + 0.08, 1.35, 0.25, cmd, fill_color=col, text_color=TEXT_WHITE, font_size=9.5)
        add_text_box(slide, 9.18, cy + 0.07, 3.45, 0.25, title, font_size=10.5, bold=True, color=TEXT_PRIMARY)
        add_text_box(slide, 7.75, cy + 0.37, 4.88, 0.50, desc, font_size=9.0, color=TEXT_SECONDARY)
        cy += 1.00

    add_footer(slide, 8)


def build_slide_9_teamwork_adversarial_gate(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(
        slide,
        module_badge="MODULE 8 · MULTI-AGENT /TEAMWORK",
        title="Inside /teamwork: How 19 Subagents & Adversarial Gates Enforced Zero Defects",
        subtitle="Real execution trace from ISS-017 (.agents/teamwork/GATE_STATUS.md): Why Challengers rejected Iteration 1 and how Iteration 2 achieved Victory.",
    )

    # Top Pipeline: 5 Boxes showing the /teamwork topology
    steps = [
        ("1. ORCHESTRATOR", "teamwork_orchestrator_r1", "Writes SCOPE.md & DISPATCH.md; coordinates 2 iterations & Sentinel health checks.", GC_BLUE),
        ("2. EXPLORERS (×6)", "explorer_r1_1..3 & r2_1..3", "Read-only parallel scouts mapping exact lines in app/, tests/, uv.lock & docs/.", GC_PURPLE),
        ("3. WORKERS (×2)", "worker_r1_1 & worker_r2_1", "Implement OPT-01..06, run 391 tests, sanitize uv.lock & deploy RE 5022570215192395776.", GC_GREEN),
        ("4. ADVERSARIAL GATE", "Reviewers, Challengers, Auditor", "2 Reviewers + 2 Challengers + 1 Forensic Auditor per iteration (10 gate agents).", GC_YELLOW),
        ("5. VICTORY AUDITOR", "teamwork_victory_auditor_1", "Independent 5-phase audit: reruns 391 tests & live EU :streamQuery checks.", GC_BLUE_DARK),
    ]
    box_w = 2.38
    gap = 0.15
    sx = 0.40
    for idx, (badge, agent_id, desc, col) in enumerate(steps):
        bx = sx + idx * (box_w + gap)
        add_card(slide, bx, 1.30, box_w, 1.82, bg_color=CARD_BG, border_color=CARD_BORDER, accent_top=col)
        add_pill(slide, bx + 0.12, 1.44, box_w - 0.24, 0.25, badge, fill_color=col, text_color=TEXT_WHITE, font_size=8.8)
        add_text_box(slide, bx + 0.12, 1.74, box_w - 0.24, 0.24, agent_id, font_size=9.2, bold=True, color=col, align=PP_ALIGN.CENTER)
        add_text_box(slide, bx + 0.12, 2.00, box_w - 0.24, 1.02, desc, font_size=8.8, color=TEXT_SECONDARY)

    # Bottom Left: Iteration 1 Gate Status (FAIL -> Caught by Challenger)
    add_card(slide, 0.40, 3.30, 6.15, 3.62, bg_color=CARD_BG, border_color=GC_RED, accent_top=GC_RED)
    add_pill(slide, 0.58, 3.46, 5.78, 0.28, "ITERATION 1 GATE VERDICT: FAIL (CHALLENGER CAUGHT 3 SUBTLE GAPS)", fill_color=GC_RED_TINT, text_color=GC_RED, border_color=GC_RED, font_size=9.2)

    iter1_bullets = [
        ("teamwork_worker_r1_1 (DONE):", "Implemented OPT-01..06, passed 390 unit tests, deployed to europe-west1, and passed 19/19 latency gates."),
        ("teamwork_reviewer_r1_1 & r1_2 (APPROVE):", "Confirmed code structure and latency reductions met the primary optimization plan."),
        ("teamwork_auditor_r1_1 (CLEAN):", "Verified git timeline, authentic cloud calls, and zero test tampering."),
        ("teamwork_challenger_r1_1 (REQUEST_CHANGES):", "Adversarial inspection of live :streamQuery outputs caught 3 subtle Storyboard gaps: (1) callback_context.state used isinstance(state, dict) which silently failed on ADK's production State class, (2) missing explicit HRC codes on Prompt 2, and (3) missing 18.5 N·m / JTD-53-30-T14 link on Prompt 6."),
    ]
    add_bullet_list(slide, 0.56, 3.82, 5.82, 2.98, iter1_bullets, font_size=9.0, space_after_pt=4.5, bullet_color=GC_RED)

    # Bottom Right: Iteration 2 Gate Status (PASS -> VICTORY CONFIRMED)
    add_card(slide, 6.78, 3.30, 6.15, 3.62, bg_color=CARD_BG, border_color=GC_GREEN, accent_top=GC_GREEN)
    add_pill(slide, 6.96, 3.46, 5.78, 0.28, "ITERATION 2 GATE VERDICT: PASS & VICTORY AUDITOR CONFIRMED", fill_color=GC_GREEN_TINT, text_color=GC_GREEN, border_color=GC_GREEN, font_size=9.2)

    iter2_bullets = [
        ("teamwork_explorer_r2_1..3 & worker_r2_1 (DONE):", "Replaced isinstance(state, dict) with _is_state_mapping(state), enriched post-tool synthesis templates, added test #391, and redeployed RE 5022570215192395776."),
        ("All 5 Gate Agents (2 Reviewers, 2 Challengers, 1 Auditor):", "100% unanimous APPROVE + CLEAN verdicts in GATE_STATUS.md."),
        ("Independent Victory Auditor (VICTORY CONFIRMED):", "Executed independent pytest run (391 passed in 22.74s) and live EU :streamQuery verification across Cap_0, Prompt_1..6, and Ref_Comp."),
        ("Permanent Guardrail Promotion (/learn):", "Promoted SAFE-ADK-01 (_is_state_mapping) into AGENTS.md so no future agent ever uses isinstance(state, dict) on ADK State."),
    ]
    add_bullet_list(slide, 6.94, 3.82, 5.82, 2.98, iter2_bullets, font_size=9.0, space_after_pt=4.5, bullet_color=GC_GREEN)

    add_footer(slide, 9)


def build_slide_10_case_study_iss013(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(
        slide,
        module_badge="MODULE 9 · CASE STUDY 1 (ISS-013)",
        title="SDD Case Study 1: The 3-Layer Operational Semantic SQL Canonicalizer",
        subtitle="How Spec-Driven Development eliminated zero-row Text-to-SQL failures when maintainers use military slang ('tails on Lizzy fit to fly').",
    )

    # Top Problem Banner
    add_card(slide, 0.40, 1.28, 12.53, 1.15, bg_color=GC_RED_TINT, border_color=GC_RED, accent_left=GC_RED)
    add_text_box(slide, 0.62, 1.36, 12.15, 0.26, "THE PROBLEM (DETECTED IN LIVE TESTING & LOGGED AS ISS-013):", font_size=10.2, bold=True, color=GC_RED)
    add_text_box(
        slide,
        left=0.62,
        top=1.64,
        width=12.15,
        height=0.70,
        text="Flight-line personnel speak in military shorthand: 'What tails on Lizzy are fit to fly?' or 'Show urgent active jobs across the Carrier Strike Group.' Raw LLM Text-to-SQL generated naive literal filters like WHERE base_location = 'Lizzy' or WHERE work_order_status = 'ACTIVE'—returning 0 rows because BigQuery stores 'HMS Queen Elizabeth', 'FMC', and 'OPEN' / 'IN_PROGRESS' / 'AWAITING_PARTS (MICAP)'.",
        font_size=9.6,
        color=TEXT_PRIMARY,
    )

    # 3 Layer Cards
    layers = [
        (
            "LAYER 1 · SCHEMA METADATA",
            "Declarative BigQuery Ontologies",
            GC_BLUE,
            GC_BLUE_TINT,
            [
                ("6 Declarative .schema.json Files:", "Every column in app/seed_data/schemas/*.schema.json carries rich descriptions and exact enum dictionaries."),
                ("Embedded System Prompt Ontology:", "uc0_maintenance_agent.py injects the 3-table schema (maintenance_work_orders, phm_bit_fault_events, work_center_tooling_and_sqep) with explicit UK/US synonym mappings."),
                ("Cross-Table Seed Integrity:", "Synchronized ZM159 across Tables 1, 7, 8, and 9 at HMS Queen Elizabeth across all 600 records."),
            ],
        ),
        (
            "LAYER 2 · SQL CANONICALIZER",
            "canonicalize_maintenance_sql()",
            GC_GREEN,
            GC_GREEN_TINT,
            [
                ("8 Deterministic Rewrite Rules:", "Inspects & rewrites LLM SQL in <1ms before BigQuery execution across 8 military domain categories."),
                ("Location & Carrier Expansion:", "Maps 'Lizzy'/'QNLZ' -> 'HMS Queen Elizabeth', 'PWLS' -> 'HMS Prince of Wales', and 'CSG'/'Fleet' -> all 3 operating bases."),
                ("Lifecycle & Readiness Expansion:", "Expands work_order_status = 'ACTIVE' into IN ('OPEN','IN_PROGRESS','AWAITING_PARTS (MICAP)',...) and 'fit to fly' -> aircraft_status = 'FMC'."),
            ],
        ),
        (
            "LAYER 3 · ZERO-ROW RECOVERY",
            "_relax_zero_row_sql() Fallback",
            GC_PURPLE,
            GC_PURPLE_TINT,
            [
                ("Automatic Fuzzy Retry:", "If a canonicalized SELECT still returns 0 rows from BigQuery EU, Layer 3 inspects string equality predicates."),
                ("Substring Relaxation:", "Rewrites strict col = 'VALUE' filters on narrative/subsystem columns into UPPER(col) LIKE '%TOKEN%' and re-executes transparently."),
                ("52 Parametrized Unit Tests:", "Pinned in tests/unit/test_semantic_sql_guardrails.py covering 38+ unseen military phrasing variations."),
            ],
        ),
    ]

    card_w = 3.98
    gap = 0.29
    sx = 0.40
    for idx, (badge, heading, col, tint, items) in enumerate(layers):
        cx = sx + idx * (card_w + gap)
        add_card(slide, cx, 2.60, card_w, 4.32, bg_color=CARD_BG, border_color=CARD_BORDER, accent_top=col)
        add_pill(slide, cx + 0.16, 2.76, card_w - 0.32, 0.28, badge, fill_color=col, text_color=TEXT_WHITE, font_size=9.2)
        add_text_box(slide, cx + 0.16, 3.10, card_w - 0.32, 0.30, heading, font_size=12.0, bold=True, color=TEXT_PRIMARY)
        add_bullet_list(slide, cx + 0.14, 3.44, card_w - 0.28, 3.35, items, font_size=9.2, space_after_pt=6.0, bullet_color=col)

    add_footer(slide, 10)


def build_slide_11_case_study_iss017(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(
        slide,
        module_badge="MODULE 10 · CASE STUDY 2 (ISS-017)",
        title="SDD Case Study 2: Cutting Production Agent Latency by 89%–96% (ISS-017)",
        subtitle="How Phase 1 telemetry profiling and Phase 2 /teamwork optimizations (OPT-01..06) compressed 14–22s queries into 0.35–1.71s.",
    )

    # Left: 6 Optimizations Card
    add_card(slide, 0.40, 1.28, 5.85, 5.65, bg_color=CARD_BG, border_color=CARD_BORDER, accent_top=GC_BLUE)
    add_pill(slide, 0.58, 1.44, 5.48, 0.28, "THE 6 ARCHITECTURAL OPTIMIZATIONS (OPT-01 TO OPT-06)", fill_color=GC_BLUE_TINT, text_color=GC_BLUE_DARK, border_color=GC_BLUE, font_size=9.2)

    opts = [
        ("OPT-01 · After-Tool Payload Slimming (<= 4 KB):", "slim_tool_response_after_tool_callback strips duplicate JSON fields before LLM ingestion (68.5 KB -> 1.9 KB on UC1; 34 KB -> 3.8 KB on UC2)."),
        ("OPT-02 · Single-Tool UC1 Fatigue + Swap Bundling:", "Embedded swap_recommendation inside check_actuator_fatigue_and_depot_inventory, eliminating a 4.3s second tool-call LLM hop on Prompt 4."),
        ("OPT-03 · Parallel Cloud I/O & Async CSV Upload:", "Parallelized 3-table BQ (_UC1_BQ_POOL) & 2-datastore DE (_UC2_DE_POOL) queries; moved GCS CSV upload to background daemon thread (388ms -> 1.3ms)."),
        ("OPT-04 · Tier 2 Fast-Path Interception (< 1 ms):", "Intercepts capability (Cap_0) and Static Dashboard vs Agent comparison (Ref_Comp) in before_model_callback with 0 LLM hops (11.6s -> 0.41s)."),
        ("OPT-05 · Direct Post-Tool Markdown Synthesis:", "Specialist before_model_callback formats verified Spreadsheet Cards, UC1 briefings, and UC2 citations directly without a 10–19s LLM copy-paste hop."),
        ("OPT-06 · Specialist Pre-Tool Intent Dispatch:", "Pre-dispatches canonical tool FunctionCall for high-confidence Storyboard intents while executing 100% live EU BigQuery & Discovery Engine calls."),
    ]
    add_bullet_list(slide, 0.56, 1.80, 5.52, 5.00, opts, font_size=8.9, space_after_pt=4.5, bullet_color=GC_BLUE)

    # Right: Empirical Before vs After Table
    add_card(slide, 6.42, 1.28, 6.51, 5.65, bg_color=CARD_BG, border_color=CARD_BORDER, accent_top=GC_GREEN)
    add_pill(slide, 6.60, 1.44, 6.15, 0.28, "LIVE REASONING ENGINE (:streamQuery) BEFORE VS. AFTER TELEMETRY", fill_color=GC_GREEN_TINT, text_color=GC_GREEN, border_color=GC_GREEN, font_size=9.2)

    t_headers = [
        ("Storyboard Query", 1.95),
        ("Use Case", 1.10),
        ("Pre-ISS-017", 1.05),
        ("Post p50 / p95", 1.15),
        ("Reduction", 0.90),
    ]
    t_rows = [
        ("Cap_0 (Capabilities)", "Fast-Path", "799 ms", "440 / 769 ms", "0 LLM Hops"),
        ("Prompt 1 (CSG Urgent)", "UC 0 SQL", "15,826 ms", "632 / 1052 ms", "-92.0%"),
        ("Prompt 2 (ZM151 PHM)", "UC 0.1 SQL", "17,446 ms", "666 / 1030 ms", "-92.8%"),
        ("Prompt 3 (Shift JOIN)", "UC 0.5 JOIN", "17,484 ms", "712 / 1143 ms", "-93.4%"),
        ("Prompt 4 (Sortie Swap)", "UC 1 Turn 1", "20,275 ms", "767 / 877 ms", "-92.2%"),
        ("Prompt 5 (16:9 Slide)", "UC 1 Turn 2", "15,747 ms", "694 / 707 ms", "-89.1%"),
        ("Prompt 6 (Canopy Fix)", "UC 2 RAG", "15,771 ms", "663 / 669 ms", "-91.7%"),
        ("Ref_Lizzy ('Lizzy' FMC)", "UC 0 Slang", "14,041 ms", "708 / 744 ms", "-91.8%"),
        ("Ref_Slang (UK/US)", "UC 2 Slang", "17,225 ms", "607 / 633 ms", "-91.5%"),
        ("Ref_Comp (vs BI)", "OPT-04 Fast", "11,609 ms", "349 / 409 ms", "-96.1%"),
    ]

    tx_start = 6.60
    ty_top = 1.84
    th_h = 0.34
    tr_h = 0.45

    cx = tx_start
    for h_text, cw in t_headers:
        add_rect(slide, cx, ty_top, cw, th_h, fill_color=GC_BLUE_DARK, border_color=CARD_BORDER, rounded=False)
        add_text_box(slide, cx + 0.04, ty_top + 0.05, cw - 0.08, th_h - 0.08, h_text, font_size=8.6, bold=True, color=TEXT_WHITE, align=PP_ALIGN.CENTER if cw < 1.3 else PP_ALIGN.LEFT)
        cx += cw

    for r_i, r_vals in enumerate(t_rows):
        ry = ty_top + th_h + r_i * tr_h
        bg = CARD_BG if r_i % 2 == 0 else CARD_BG_MUTED
        cx = tx_start
        for c_i, (val, (_, cw)) in enumerate(zip(r_vals, t_headers)):
            c_bg = GC_GREEN_TINT if c_i == 4 else (GC_RED_TINT if c_i == 2 else bg)
            c_col = GC_GREEN if c_i == 4 else (GC_RED if c_i == 2 else TEXT_PRIMARY)
            add_rect(slide, cx, ry, cw, tr_h, fill_color=c_bg, border_color=CARD_BORDER, rounded=False)
            add_text_box(
                slide,
                cx + 0.04,
                ry + 0.06,
                cw - 0.08,
                tr_h - 0.10,
                val,
                font_size=8.4,
                bold=(c_i in (0, 3, 4)),
                color=c_col,
                align=PP_ALIGN.CENTER if c_i >= 2 else PP_ALIGN.LEFT,
            )
            cx += cw

    add_footer(slide, 11)


def build_slide_12_takeaways(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(
        slide,
        module_badge="MODULE 11 · TEACHER'S BLUEPRINT",
        title="How to Adopt Spec-Driven Development on Your Next Google Cloud Agent Project",
        subtitle="A 5-Step Repeatable Checklist for Engineering Teams Using Google Antigravity and the Agent Platform.",
    )

    steps = [
        (
            "STEP 1",
            "Write the SDD & Golden Storyboard First",
            "Create SA_<PROJECT>.md and DEMO_STORYBOARD.md before coding. Define every BigQuery table, Discovery Engine datastore, and exact user prompt/response contract.",
            GC_BLUE,
            GC_BLUE_TINT,
        ),
        (
            "STEP 2",
            "Lock Guardrails & Boundaries in AGENTS.md",
            "Author root AGENTS.md (regional residency, auth caching, model thinking level, latency SLAs) and directory-scoped AGENTS.md files (api/, web/, tests/) to isolate subagents.",
            GC_BLUE_DARK,
            GC_BLUE_TINT,
        ),
        (
            "STEP 3",
            "Use /grill-me & /plan with Issue Index Lookup",
            "Start every feature by checking docs/issues/INDEX.md for prior RCAs and Dead Ends. Produce a Brain Plan Artifact with empirical telemetry and require human approval before Phase 2.",
            GC_PURPLE,
            GC_PURPLE_TINT,
        ),
        (
            "STEP 4",
            "Build & Verify via /teamwork & Domain Skills",
            "Equip subagents with SKILL.md runbooks (google-agents-cli-*) and enforce the 5-role Adversarial Gate (Explorers, Isolated Workers, Reviewers, Challengers, Forensic & Victory Auditors).",
            GC_GREEN,
            GC_GREEN_TINT,
        ),
        (
            "STEP 5",
            "Close the Loop with ISS-XXX Logs & /learn",
            "Record every fix using docs/issues/TEMPLATE.md, verify live cloud SLAs via benchmark_harness.py, and run /learn to promote new runtime discoveries directly into AGENTS.md.",
            GC_YELLOW,
            GC_YELLOW_TINT,
        ),
    ]

    y_cursor = 1.32
    card_h = 1.02
    for badge, title, desc, col, tint in steps:
        add_card(slide, 0.40, y_cursor, 12.53, card_h, bg_color=CARD_BG, border_color=CARD_BORDER, accent_left=col)
        add_pill(slide, 0.62, y_cursor + 0.16, 1.35, 0.30, badge, fill_color=col, text_color=TEXT_WHITE, font_size=10.0)
        add_text_box(slide, 2.12, y_cursor + 0.12, 4.10, 0.34, title, font_size=13.0, bold=True, color=TEXT_PRIMARY)
        add_text_box(slide, 2.12, y_cursor + 0.46, 10.60, 0.48, desc, font_size=9.8, color=TEXT_SECONDARY)
        add_pill(slide, 11.15, y_cursor + 0.14, 1.60, 0.26, "VERIFIED PATTERN", fill_color=tint, text_color=col, border_color=col, font_size=8.2)
        y_cursor += card_h + 0.11

    add_footer(slide, 12)


def build_slide_13_visual_poster(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(
        slide,
        module_badge="APPENDIX · VISUAL ARCHITECTURE POSTER",
        title="Full 16:9 Spec-Driven Development Architecture & Artifact Lineage Canvas",
        subtitle="High-resolution reference poster (docs/assets/f35_sdd_workflow_16x9_white_gcloud.png) summarizing all 6 stages, 9 skills, and 19 /teamwork agents.",
    )
    poster_path = DOCS_DIR / "assets" / "f35_sdd_workflow_16x9_white_gcloud.png"
    if poster_path.exists():
        add_card(slide, 0.40, 1.24, 12.53, 5.76, bg_color=CARD_BG, border_color=CARD_BORDER)
        add_image_safe(slide, poster_path, left=1.67, top=1.31, height=5.62)
    add_footer(slide, 13)


def generate_presentation() -> Path:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.50)

    build_slide_1_title(prs)
    build_slide_2_principles(prs)
    build_slide_3_lifecycle_overview(prs)
    build_slide_4_stages_0_and_1(prs)
    build_slide_5_stages_2_and_3(prs)
    build_slide_6_stages_4_and_5(prs)
    build_slide_7_artifact_matrix(prs)
    build_slide_8_skills_and_commands(prs)
    build_slide_9_teamwork_adversarial_gate(prs)
    build_slide_10_case_study_iss013(prs)
    build_slide_11_case_study_iss017(prs)
    build_slide_12_takeaways(prs)
    build_slide_13_visual_poster(prs)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUTPUT_PPTX_PATH))
    print(f"Saved 13-slide SDD presentation to: {OUTPUT_PPTX_PATH}")
    return OUTPUT_PPTX_PATH


def generate_sdd_workflow_png() -> Path:
    """Render a 16:9 high-resolution (3072x1728) Google Cloud White SDD Workflow Slide PNG."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle

    fig = plt.figure(figsize=(19.2, 10.8), dpi=160, facecolor="#FFFFFF")
    ax = fig.add_axes([0, 0, 1, 1], facecolor="#FFFFFF")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Top Google Cloud 4-Color Bar
    for idx, col in enumerate(["#4285F4", "#EA4335", "#FBBC04", "#34A853"]):
        ax.add_patch(Rectangle((idx * 0.25, 0.992), 0.25, 0.008, facecolor=col, edgecolor="none", zorder=10))

    def draw_box(x, y, w, h, fc="#FFFFFF", ec="#DADCE0", lw=1.4, top_col=None, r=0.008, z=2):
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h,
                boxstyle=f"round,pad=0,rounding_size={r}",
                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z,
            )
        )
        if top_col:
            ax.add_patch(Rectangle((x, y + h - 0.007), w, 0.007, facecolor=top_col, edgecolor="none", zorder=z + 1))

    def draw_pill(x, y, w, h, txt, fc="#1A73E8", tc="#FFFFFF", ec="none", fs=8.5, z=6):
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h,
                boxstyle="round,pad=0,rounding_size=0.006",
                facecolor=fc, edgecolor=ec, linewidth=1.0 if ec != "none" else 0, zorder=z,
            )
        )
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, fontweight="bold", color=tc, family="sans-serif", zorder=z + 1)

    def draw_lines(x, y_top, lines, step=0.021, z=6):
        cy = y_top
        for text, fs, fw, col in lines:
            ax.text(x, cy, text, ha="left", va="top", fontsize=fs, fontweight=fw, color=col, family="sans-serif", zorder=z)
            cy -= step
        return cy

    # Header Strip
    draw_box(0.018, 0.900, 0.964, 0.082, fc="#F8F9FA", ec="#DADCE0", lw=1.2)
    draw_pill(0.030, 0.946, 0.205, 0.026, "SPEC-DRIVEN DEVELOPMENT (SDD)", fc="#1A73E8", tc="#FFFFFF", fs=8.5)
    draw_pill(0.245, 0.946, 0.205, 0.026, "GOOGLE ANTIGRAVITY · ADK 2.0", fc="#E8F0FE", tc="#174EA6", ec="#1A73E8", fs=8.5)
    draw_pill(0.750, 0.946, 0.218, 0.026, "19/19 EU SLA GATES · 391 TESTS PASS", fc="#E6F4EA", tc="#0D652D", ec="#1E8E3E", fs=8.5)

    ax.text(0.030, 0.935, "Spec-Driven Development Workflow: How We Built the F-35 Fleet Sustainment Agent", ha="left", va="top", fontsize=15.5, fontweight="bold", color="#202124", family="sans-serif", zorder=6)
    ax.text(0.030, 0.911, "Six Stages · Three Key Teaching Points per Stage · Complete Artifact Lineage (SA_F35.md -> AGENTS.md -> /plan -> /teamwork -> ISS-001..017 -> /learn)", ha="left", va="top", fontsize=9.2, color="#5F6368", family="sans-serif", zorder=6)

    # Row 1: The 6 SDD Stages (6 columns across)
    stage_specs = [
        (
            "STAGE 0 · DOMAIN SPEC",
            "Architecture & Storyboard",
            "#1A73E8", "#E8F0FE",
            [
                ("1. Dual-Track SDD First:", 8.4, "bold", "#202124"),
                ("   SA_F35.md (v1.4) locks 6 BQ tables", 7.8, "normal", "#3C4043"),
                ("   (600 rows) & 4 S1000D docs.", 7.8, "normal", "#3C4043"),
                ("2. Executable Storyboard:", 8.4, "bold", "#202124"),
                ("   DEMO_STORYBOARD.md defines the", 7.8, "normal", "#3C4043"),
                ("   6-Prompt Golden Thread & SLAs.", 7.8, "normal", "#3C4043"),
                ("3. Machine CLI Contract:", 8.4, "bold", "#202124"),
                ("   .agents-cli-spec.md & V&V gates", 7.8, "normal", "#3C4043"),
                ("   (TC-SQ-00..05, TC-LP-00..05).", 7.8, "normal", "#3C4043"),
            ],
            "IN: SDD-GE-UKD-002, ODIN/S1000D",
            "OUT: SA_F35.md, DEMO_STORYBOARD.md",
        ),
        (
            "STAGE 1 · GOVERNANCE",
            "Hierarchical AGENTS.md",
            "#174EA6", "#E8F0FE",
            [
                ("1. Root Invariant Table:", 8.4, "bold", "#202124"),
                ("   AGENTS.md encodes REG-01 (EU),", 7.8, "normal", "#3C4043"),
                ("   PERF-01..08, SAFE-ADK & DEPLOY-01.", 7.8, "normal", "#3C4043"),
                ("2. Scoped Boundaries:", 8.4, "bold", "#202124"),
                ("   packages/api, packages/web, and", 7.8, "normal", "#3C4043"),
                ("   tests/ AGENTS.md isolate domains.", 7.8, "normal", "#3C4043"),
                ("3. Three-Phase Rule:", 8.4, "bold", "#202124"),
                ("   Enforces Plan -> Parallel Build ->", 7.8, "normal", "#3C4043"),
                ("   Integration & ISS-XXX Logging.", 7.8, "normal", "#3C4043"),
            ],
            "IN: SA_F35.md, .agents-cli-spec.md",
            "OUT: Root + 3 Scoped AGENTS.md",
        ),
        (
            "STAGE 2 · PHASE 1 PLAN",
            "RCA Lookup & /plan Gate",
            "#7E57C2", "#F3E8FD",
            [
                ("1. Pre-Change RCA Lookup:", 8.4, "bold", "#202124"),
                ("   Consult docs/issues/INDEX.md &", 7.8, "normal", "#3C4043"),
                ("   Sec 4 Dead Ends before coding.", 7.8, "normal", "#3C4043"),
                ("2. Empirical Profiling:", 8.4, "bold", "#202124"),
                ("   Profile live EU telemetry & write", 7.8, "normal", "#3C4043"),
                ("   brain/plan_iss*.md with Mermaid.", 7.8, "normal", "#3C4043"),
                ("3. Human Approval Gate:", 8.4, "bold", "#202124"),
                ("   Use /grill-me & RequestFeedback", 7.8, "normal", "#3C4043"),
                ("   Proceed gate before Phase 2.", 7.8, "normal", "#3C4043"),
            ],
            "IN: INDEX.md, ISS-001..016, /plan",
            "OUT: brain/plan_iss015 & 017.md",
        ),
        (
            "STAGE 3 · PHASE 2 BUILD",
            "Parallel /teamwork & Skills",
            "#1E8E3E", "#E6F4EA",
            [
                ("1. 3 Parallel Explorers:", 8.4, "bold", "#202124"),
                ("   explorer_r1_1..3 map exact lines", 7.8, "normal", "#3C4043"),
                ("   into handoff.md blueprints.", 7.8, "normal", "#3C4043"),
                ("2. Skill-Driven Workers:", 8.4, "bold", "#202124"),
                ("   Apply agents-cli-adk-code to build", 7.8, "normal", "#3C4043"),
                ("   3-Layer SQL & OPT-01..06 hooks.", 7.8, "normal", "#3C4043"),
                ("3. 600-Row Seed & Schemas:", 8.4, "bold", "#202124"),
                ("   bq_seed_records.py + .schema.json", 7.8, "normal", "#3C4043"),
                ("   + jtd_corpus.py (DOC-01..09).", 7.8, "normal", "#3C4043"),
            ],
            "IN: plan_*.md, 9 SKILL.md runbooks",
            "OUT: app/, packages/web/, handoff.md",
        ),
        (
            "STAGE 4 · PHASE 3 V&V",
            "Adversarial Gate & Deploy",
            "#B06000", "#FEF7E0",
            [
                ("1. 5-Role Adversarial Gate:", 8.4, "bold", "#202124"),
                ("   2 Reviewers, 2 Challengers, 1", 7.8, "normal", "#3C4043"),
                ("   Forensic & 1 Victory Auditor.", 7.8, "normal", "#3C4043"),
                ("2. 391 Tests & Clean Deploy:", 8.4, "bold", "#202124"),
                ("   pytest + ADK eval + uv.lock check", 7.8, "normal", "#3C4043"),
                ("   -> Agent Runtime (2 vCPU, 8Gi).", 7.8, "normal", "#3C4043"),
                ("3. Live EU SLA Benchmark:", 8.4, "bold", "#202124"),
                ("   benchmark_harness.py proves 19/19", 7.8, "normal", "#3C4043"),
                ("   gates (0.35s–1.71s, -89% to -96%).", 7.8, "normal", "#3C4043"),
            ],
            "IN: vv_golden_suite.json, deploy skill",
            "OUT: GATE_STATUS.md, Benchmark Report",
        ),
        (
            "STAGE 5 · MEMORY LOOP",
            "Issue Logs & /learn Rules",
            "#D93025", "#FCE8E6",
            [
                ("1. Standardized Issue Logs:", 8.4, "bold", "#202124"),
                ("   Log ISS-001..017 via TEMPLATE.md", 7.8, "normal", "#3C4043"),
                ("   & register in docs/issues/INDEX.md.", 7.8, "normal", "#3C4043"),
                ("2. Self-Healing via /learn:", 8.4, "bold", "#202124"),
                ("   Promote SAFE-ADK-01..02, PERF-08", 7.8, "normal", "#3C4043"),
                ("   & DEPLOY-01 back into AGENTS.md.", 7.8, "normal", "#3C4043"),
                ("3. Executive Storytelling:", 8.4, "bold", "#202124"),
                ("   Auto-generate 16:9 PNG diagrams &", 7.8, "normal", "#3C4043"),
                ("   Google Cloud PowerPoint decks.", 7.8, "normal", "#3C4043"),
            ],
            "IN: TEMPLATE.md, /learn, telemetry",
            "OUT: ISS-001..017, Updated AGENTS.md",
        ),
    ]

    col_w = 0.153
    gap = 0.009
    sx = 0.018
    for idx, (badge, sub, col, tint, lines, in_txt, out_txt) in enumerate(stage_specs):
        cx = sx + idx * (col_w + gap)
        draw_box(cx, 0.395, col_w, 0.488, fc="#FFFFFF", ec="#DADCE0", top_col=col)
        draw_pill(cx + 0.008, 0.844, col_w - 0.016, 0.025, badge, fc=col, tc="#FFFFFF", fs=7.8)
        ax.text(cx + col_w / 2, 0.832, sub, ha="center", va="top", fontsize=9.0, fontweight="bold", color="#202124", family="sans-serif", zorder=6)

        draw_lines(cx + 0.008, 0.800, lines, step=0.027)

        # Ingested & Produced mini pills at bottom of stage card
        draw_box(cx + 0.007, 0.468, col_w - 0.014, 0.058, fc="#E8F0FE", ec="#1A73E8", lw=0.9, r=0.005, z=4)
        ax.text(cx + 0.012, 0.518, "INGESTED ARTIFACTS:", ha="left", va="top", fontsize=7.2, fontweight="bold", color="#174EA6", zorder=6)
        ax.text(cx + 0.012, 0.496, in_txt.replace("IN: ", ""), ha="left", va="top", fontsize=7.2, color="#202124", zorder=6)

        draw_box(cx + 0.007, 0.404, col_w - 0.014, 0.058, fc="#E6F4EA", ec="#1E8E3E", lw=0.9, r=0.005, z=4)
        ax.text(cx + 0.012, 0.454, "PRODUCED ARTIFACTS:", ha="left", va="top", fontsize=7.2, fontweight="bold", color="#0D652D", zorder=6)
        ax.text(cx + 0.012, 0.432, out_txt.replace("OUT: ", ""), ha="left", va="top", fontsize=7.2, color="#202124", zorder=6)

    # Row 2: 3 Horizontal Pillars (Skills & Slash Commands | /teamwork Adversarial Gate | Case Studies & Impact)
    b_w = 0.314
    b_gap = 0.011

    # Bottom Box 1: Skills & Slash Commands
    bx1 = 0.018
    draw_box(bx1, 0.055, b_w, 0.322, fc="#F8F9FA", ec="#DADCE0", top_col="#7E57C2")
    draw_pill(bx1 + 0.012, 0.338, b_w - 0.024, 0.026, "ANTIGRAVITY SKILLS (SKILL.md) & SLASH COMMANDS", fc="#7E57C2", tc="#FFFFFF", fs=8.3)
    draw_lines(
        bx1 + 0.012,
        0.324,
        [
            ("• google-agents-cli-workflow & scaffold: Project spec & ADK 2.0 wiring", 8.0, "bold", "#202124"),
            ("• google-agents-cli-adk-code: Callbacks, State, ContextCacheConfig", 8.0, "normal", "#3C4043"),
            ("• discovery-engine-adk-integration: EU JSONL _id & pageSize=15 RAG", 8.0, "normal", "#3C4043"),
            ("• google-agents-cli-eval / deploy / publish: Golden V&V & 2 vCPU deploy", 8.0, "normal", "#3C4043"),
            ("• adk-agent-observability & agy-customizations: Spans & AGENTS.md", 8.0, "normal", "#3C4043"),
            ("• Slash Commands: /grill-me -> /plan -> /teamwork -> /learn -> /goal", 8.0, "bold", "#174EA6"),
        ],
        step=0.043,
    )

    # Bottom Box 2: /teamwork Adversarial Gate
    bx2 = bx1 + b_w + b_gap
    draw_box(bx2, 0.055, b_w, 0.322, fc="#F8F9FA", ec="#DADCE0", top_col="#1E8E3E")
    draw_pill(bx2 + 0.012, 0.338, b_w - 0.024, 0.026, "MULTI-AGENT /TEAMWORK & ADVERSARIAL GATE (19 SUBAGENTS)", fc="#1E8E3E", tc="#FFFFFF", fs=8.3)
    draw_lines(
        bx2 + 0.012,
        0.324,
        [
            ("• Orchestrator + Sentinel: Manages SCOPE.md, DISPATCH.md & GATE_STATUS.md", 8.0, "bold", "#202124"),
            ("• 6 Read-Only Explorers: Map line-exact specs across app/, tests/, docs/", 8.0, "normal", "#3C4043"),
            ("• 2 Isolated Workers: Implement OPT-01..06 & deploy RE 5022570215192395776", 8.0, "normal", "#3C4043"),
            ("• 4 Reviewers & 4 Challengers: Challenger caught State duck-typing in Iter 1", 8.0, "normal", "#3C4043"),
            ("• 2 Forensic Auditors: Verify git timelines & zero hardcoded cloud bypasses", 8.0, "normal", "#3C4043"),
            ("• 1 Independent Victory Auditor: Reruns 391 pytest checks & live EU queries", 8.0, "bold", "#0D652D"),
        ],
        step=0.043,
    )

    # Bottom Box 3: Quantitative Engineering Outcomes
    bx3 = bx2 + b_w + b_gap
    draw_box(bx3, 0.055, b_w, 0.322, fc="#F8F9FA", ec="#DADCE0", top_col="#1A73E8")
    draw_pill(bx3 + 0.012, 0.338, b_w - 0.024, 0.026, "QUANTITATIVE OUTCOMES OF SPEC-DRIVEN DEVELOPMENT", fc="#1A73E8", tc="#FFFFFF", fs=8.3)
    draw_lines(
        bx3 + 0.012,
        0.324,
        [
            ("• 89%–96% Latency Reduction (ISS-017): 14.1s–22.3s -> 0.35s–1.71s live EU", 8.0, "bold", "#174EA6"),
            ("• 100% Storyboard Fidelity (ISS-015/016): All 10 queries & 19/19 SLA gates PASS", 8.0, "normal", "#3C4043"),
            ("• Zero-Row SQL Eliminated (ISS-013): 3-Layer Semantic SQL Canonicalizer", 8.0, "normal", "#3C4043"),
            ("• 391 Automated Tests (0 Failures): Unit, 5-Tier E2E, & ADK Golden Eval", 8.0, "normal", "#3C4043"),
            ("• 18 Documented Issues (ISS-001..017): Full RCAs, diffs & Section 4 Dead Ends", 8.0, "normal", "#3C4043"),
            ("• Warm 2 vCPU / 8Gi Agent Runtime: min_instances=1 in europe-west1", 8.0, "bold", "#0D652D"),
        ],
        step=0.043,
    )

    # Bottom Footer Bar
    draw_box(0.018, 0.012, 0.964, 0.032, fc="#F8F9FA", ec="#DADCE0", lw=0.8, r=0.004)
    ax.text(0.030, 0.028, "Google Cloud · Antigravity Spec-Driven Development Playbook · Reference Application: F-35 Lightning II Fleet Sustainment Agent (SDD-GE-F35-001 v1.4)", ha="left", va="center", fontsize=8.2, color="#5F6368", zorder=6)
    ax.text(0.970, 0.028, "docs/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md · docs/F35_Spec_Driven_Development_Google_Cloud_Deck.pptx", ha="right", va="center", fontsize=8.2, fontweight="bold", color="#174EA6", zorder=6)

    out_png = DOCS_DIR / "assets" / "f35_sdd_workflow_16x9_white_gcloud.png"
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_png), dpi=160)
    plt.close(fig)
    print(f"Saved 16:9 SDD Workflow PNG to: {out_png}")
    return out_png


if __name__ == "__main__":
    generate_sdd_workflow_png()
    generate_presentation()
