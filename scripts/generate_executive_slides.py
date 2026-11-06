"""Generate the 12-Slide Executive Storytelling Presentation Deck (.pptx) for F-35 Fleet Sustainment.

Grounded in the art of storytelling, formatted in Google Cloud brand colours with clean executive white styling:
- Slide 1: Setting the Operational Scene (Title & Carrier Hero Photography)
- Slide 2: The Villain — The 06:30Z "Oracle-to-Excel" Ritual (The Current State)
- Slide 3: The Target State — The Intelligent Action Layer (Non-disruptive layer on F-35 Data Warehouse)
- Slide 4: Act 1 Live Demo — Morning Stand-Up & Shift Dispatch (06:45Z · Triage ZM151) [👉 LIVE DEMO]
- Slide 5: Act 2 Live Demo — Mission Protection & Leadership Briefing (06:52Z · Sortie Swap & Slide) [👉 LIVE DEMO]
- Slide 6: Act 3 Live Demo — Allied Fleet Memory & Defect Resolution (06:56Z · Solve Zero-BIT Defect) [👉 LIVE DEMO]
- Slide 7: Why Agents Beat Static BI Dashboards (The Leadership Value Matrix)
- Slide 8: Semantic Governance & Flight-Line Interoperability (Military Slang: "Tails on Lizzy fit to fly")
- Slide 9: Mission Impact & Next Steps (From 90 Minutes to 4 Minutes)
- Slide 10: Appendix — Technical & Architecture Deep-Dive (Section Divider)
- Slide 11: Appendix — Architecture Diagram Canvas I (Themed Ready-to-Go: System Architecture & Agent Runtime)
- Slide 12: Appendix — Architecture Diagram Canvas II (Themed Ready-to-Go: Data Flow & Semantic Governance)
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any, List, Optional

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "app" / "assets"
DOCS_DIR = ROOT_DIR / "docs"
OUTPUT_PPTX_PATH = DOCS_DIR / "F35_Executive_Storytelling_Deck.pptx"
LEGACY_PPTX_PATH = DOCS_DIR / "F35_Executive_Use_Cases_Deck.pptx"

CLOUD_LOGO_PATH = ASSETS_DIR / "cloud.jpeg"
F35_RAF_PHOTO_PATH = ASSETS_DIR / "f35-RAF.png"
RAF_ICON_PATH = ASSETS_DIR / "f35_raf_icon_256.png"
DASHBOARD_PNG_PATH = DOCS_DIR / "f35_sustainment_executive_dashboard.png"

# ==============================================================================
# Google Cloud Brand & Clean Executive White Palette (High Contrast & Readability)
# ==============================================================================
GC_BLUE = RGBColor(26, 115, 232)        # #1A73E8 Accessible Google Blue
GC_GREEN = RGBColor(30, 142, 62)        # #1E8E3E Accessible Google Green (FMC / Success)
GC_YELLOW = RGBColor(176, 96, 0)        # #B06000 Accessible Dark Amber on White
GC_RED = RGBColor(217, 48, 37)          # #D93025 Accessible Google Red (Grounding / NMC)

BG_WHITE = RGBColor(255, 255, 255)      # #FFFFFF Pure White Slide Background
CARD_BG = RGBColor(255, 255, 255)       # #FFFFFF Elevated Container Surface
CARD_BG_MUTED = RGBColor(248, 249, 250) # #F8F9FA Soft Tinted Surface
CARD_BORDER = RGBColor(218, 220, 224)   # #DADCE0 Subtle Card Outline
PROMPT_BG = RGBColor(232, 240, 254)     # #E8F0FE Soft Google Blue Prompt Box
PROMPT_BORDER = RGBColor(26, 115, 232)  # #1A73E8 Google Blue Outline
HEADER_BAR_BG = RGBColor(255, 255, 255) # #FFFFFF Top Header Bar
FOOTER_BAR_BG = RGBColor(248, 249, 250) # #F8F9FA Bottom Footer Strip

TEXT_PRIMARY = RGBColor(32, 33, 36)     # #202124 Deep Charcoal for Headings/Code
TEXT_SECONDARY = RGBColor(60, 64, 67)   # #3C4043 Dark Grey for Body Narrative
TEXT_MUTED = RGBColor(95, 99, 104)      # #5F6368 Medium Grey for Timestamps/Footers
ACCENT_NAVY = RGBColor(23, 78, 166)     # #174EA6 Deep Navy for Prompt Labels
TEXT_WHITE = RGBColor(255, 255, 255)    # #FFFFFF Only for text inside colored badge fills


# ==============================================================================
# Presentation Helper Functions
# ==============================================================================
def set_slide_background(slide: Any, color: RGBColor = BG_WHITE) -> None:
    """Fill slide background with clean solid color (default: pure white)."""
    background = slide.background
    fill = background.fill
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
    dash_style: Optional[Any] = None,
) -> Any:
    """Add a styled rectangle or rounded rectangle shape."""
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
        if dash_style is not None:
            shape.line.dash_style = dash_style
    else:
        shape.line.fill.background()
    if rounded and hasattr(shape, "adjustments") and len(shape.adjustments) > 0:
        shape.adjustments[0] = 0.03
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
    dash_style: Optional[Any] = None,
) -> Any:
    """Create an elevated container card with optional top/left color accent stripe."""
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
        dash_style=dash_style,
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
    font_size: float = 13,
    bold: bool = False,
    italic: bool = False,
    color: RGBColor = TEXT_PRIMARY,
    font_name: str = "Arial",
    align: PP_ALIGN = PP_ALIGN.LEFT,
    word_wrap: bool = True,
) -> Any:
    """Create a styled text box with high-contrast text by default."""
    tx_box = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = tx_box.text_frame
    tf.word_wrap = word_wrap
    tf.margin_left = Inches(0.06)
    tf.margin_right = Inches(0.06)
    tf.margin_top = Inches(0.04)
    tf.margin_bottom = Inches(0.04)
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


def add_image_safe(
    slide: Any,
    image_path: Path,
    left: float,
    top: float,
    width: Optional[float] = None,
    height: Optional[float] = None,
) -> Optional[Any]:
    """Insert an image into slide if it exists on disk, preserving proportions."""
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


def add_google_header(
    slide: Any,
    act_badge: str,
    title: str,
    subtitle: str,
    timestamp: Optional[str] = None,
    operational_tag: Optional[str] = None,
    badge_color: RGBColor = GC_BLUE,
    badge_text_color: RGBColor = TEXT_WHITE,
) -> None:
    """Render consistent Google Cloud branded top header strip across slides."""
    # Top bar background (pure white with subtle bottom border)
    add_rect(
        slide,
        left=0.0,
        top=0.0,
        width=13.333,
        height=1.18,
        fill_color=HEADER_BAR_BG,
        border_color=CARD_BORDER,
        border_pt=0.8,
        rounded=False,
    )
    # Left RAF Icon
    if RAF_ICON_PATH.exists():
        add_image_safe(slide, RAF_ICON_PATH, left=0.40, top=0.18, width=0.82)

    # Category Pill
    pill = add_rect(
        slide,
        left=1.40,
        top=0.16,
        width=2.50,
        height=0.30,
        fill_color=badge_color,
        border_color=None,
        rounded=True,
    )
    tf = pill.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = act_badge
    r.font.name = "Arial"
    r.font.size = Pt(10.5)
    r.font.bold = True
    r.font.color.rgb = badge_text_color

    # Optional Timestamp Pill
    offset_x = 4.00
    if timestamp:
        time_pill = add_rect(
            slide,
            left=offset_x,
            top=0.16,
            width=1.30,
            height=0.30,
            fill_color=RGBColor(241, 243, 244),
            border_color=CARD_BORDER,
            border_pt=1.0,
            rounded=True,
        )
        tf_time = time_pill.text_frame
        p_time = tf_time.paragraphs[0]
        p_time.alignment = PP_ALIGN.CENTER
        r_time = p_time.add_run()
        r_time.text = f"⏱ {timestamp}"
        r_time.font.name = "Arial"
        r_time.font.size = Pt(10.0)
        r_time.font.bold = True
        r_time.font.color.rgb = TEXT_PRIMARY
        offset_x += 1.45

    # Optional Operational Tag Pill (e.g. LIVE DEMO)
    if operational_tag:
        tag_pill = add_rect(
            slide,
            left=offset_x,
            top=0.16,
            width=1.85,
            height=0.30,
            fill_color=RGBColor(230, 244, 234),
            border_color=GC_GREEN,
            border_pt=1.0,
            rounded=True,
        )
        tf_tag = tag_pill.text_frame
        p_tag = tf_tag.paragraphs[0]
        p_tag.alignment = PP_ALIGN.CENTER
        r_tag = p_tag.add_run()
        r_tag.text = f"✓ {operational_tag}"
        r_tag.font.name = "Arial"
        r_tag.font.size = Pt(10.0)
        r_tag.font.bold = True
        r_tag.font.color.rgb = GC_GREEN

    # Slide Title & Subtitle (Dark Charcoal & Muted Grey for 100% Readability)
    add_text_box(
        slide,
        left=1.40,
        top=0.48,
        width=9.80,
        height=0.40,
        text=title,
        font_size=20,
        bold=True,
        color=TEXT_PRIMARY,
    )
    add_text_box(
        slide,
        left=1.40,
        top=0.86,
        width=9.80,
        height=0.28,
        text=subtitle,
        font_size=11,
        italic=True,
        color=TEXT_MUTED,
    )

    # Google Cloud Logo (synced from gs://f35sa/cloud.jpeg)
    if CLOUD_LOGO_PATH.exists():
        add_image_safe(
            slide,
            CLOUD_LOGO_PATH,
            left=11.85,
            top=0.20,
            width=1.12,
        )


def add_footer(slide: Any, slide_number: int, total_slides: int = 12) -> None:
    """Render consistent bottom footer with clean 2-zone layout (Zero Classification Markings)."""
    add_rect(
        slide,
        left=0.0,
        top=7.08,
        width=13.333,
        height=0.42,
        fill_color=FOOTER_BAR_BG,
        border_color=CARD_BORDER,
        border_pt=0.8,
        rounded=False,
    )
    # Left Unit Designation
    add_text_box(
        slide,
        left=0.60,
        top=7.14,
        width=8.00,
        height=0.28,
        text="ROYAL AIR FORCE · CARRIER STRIKE GROUP · F-35 SUSTAINMENT AGENTS",
        font_size=9.0,
        bold=True,
        color=TEXT_MUTED,
    )
    # Right Slide Counter
    add_text_box(
        slide,
        left=11.20,
        top=7.14,
        width=1.55,
        height=0.28,
        text=f"Slide {slide_number} of {total_slides}",
        font_size=9.5,
        bold=True,
        color=TEXT_MUTED,
        align=PP_ALIGN.RIGHT,
    )


def add_live_demo_prompt_box(
    slide: Any,
    left: float,
    top: float,
    width: float,
    height: float,
    prompts: List[tuple[str, str]],
    capability_badge: str = "⚡ ACTION: LIVE SPREADSHEET CARD",
) -> None:
    """Render monospace interactive prompt container for live demonstration slides."""
    # Soft Google Blue Container
    add_card(
        slide,
        left=left,
        top=top,
        width=width,
        height=height,
        bg_color=PROMPT_BG,
        border_color=PROMPT_BORDER,
        border_pt=1.2,
        accent_top=GC_BLUE,
    )
    # Live Demo Cue Pill
    cue_pill = add_rect(
        slide,
        left=left + 0.18,
        top=top + 0.14,
        width=3.70,
        height=0.28,
        fill_color=GC_BLUE,
        border_color=None,
        rounded=True,
    )
    tf = cue_pill.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "👉 LIVE DEMO — SWITCH TO LIVE SCREEN NOW"
    r.font.name = "Arial"
    r.font.size = Pt(9.5)
    r.font.bold = True
    r.font.color.rgb = TEXT_WHITE

    # Operational Capability Callout on right of prompt container header
    add_text_box(
        slide,
        left=left + width - 4.50,
        top=top + 0.14,
        width=4.30,
        height=0.28,
        text=capability_badge,
        font_size=10.0,
        bold=True,
        color=GC_GREEN,
        align=PP_ALIGN.RIGHT,
    )

    # Monospace Prompt Rows (High-contrast deep charcoal on soft blue)
    prompt_y = top + 0.50
    box_shape = slide.shapes.add_textbox(
        Inches(left + 0.20),
        Inches(prompt_y),
        Inches(width - 0.40),
        Inches(height - 0.58),
    )
    tf_prompts = box_shape.text_frame
    tf_prompts.word_wrap = True
    tf_prompts.margin_left = Inches(0.04)
    tf_prompts.margin_right = Inches(0.04)
    tf_prompts.margin_top = Inches(0.02)
    tf_prompts.margin_bottom = Inches(0.02)

    for i, (label, prompt_text) in enumerate(prompts):
        p_lbl = tf_prompts.paragraphs[0] if i == 0 else tf_prompts.add_paragraph()
        p_lbl.space_before = Pt(4)
        p_lbl.space_after = Pt(1)
        r_lbl = p_lbl.add_run()
        r_lbl.text = f"{label}: "
        r_lbl.font.name = "Arial"
        r_lbl.font.size = Pt(10.0)
        r_lbl.font.bold = True
        r_lbl.font.color.rgb = ACCENT_NAVY

        r_txt = p_lbl.add_run()
        r_txt.text = f'"{prompt_text}"'
        r_txt.font.name = "Consolas"
        r_txt.font.size = Pt(9.5)
        r_txt.font.color.rgb = TEXT_PRIMARY


def set_speaker_notes(slide: Any, notes_text: str) -> None:
    """Attach formatted speaker notes to slide."""
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text.strip()


# ==============================================================================
# Slide 1: Setting the Operational Scene (Title Slide)
# ==============================================================================
def build_slide_1(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, BG_WHITE)

    # Top Brand Header Strip with Google Cloud Logo & RAF Crest
    if CLOUD_LOGO_PATH.exists():
        add_image_safe(slide, CLOUD_LOGO_PATH, left=0.80, top=0.50, width=1.55)
    if RAF_ICON_PATH.exists():
        add_image_safe(slide, RAF_ICON_PATH, left=11.80, top=0.45, width=0.90)

    # Main Headline & Subtitle
    add_text_box(
        slide,
        left=0.80,
        top=1.45,
        width=11.70,
        height=0.85,
        text="F-35 Fleet Sustainment: The Intelligent Action Layer",
        font_size=32,
        bold=True,
        color=TEXT_PRIMARY,
    )
    add_text_box(
        slide,
        left=0.80,
        top=2.35,
        width=11.70,
        height=0.45,
        text="Compressing a Morning of Carrier Strike Group Sustainment from 90 Minutes into 4 Minutes",
        font_size=17,
        italic=True,
        color=TEXT_SECONDARY,
    )

    # Left Column: Operational Mandate Cards
    col_w = 5.60
    # Card 1: Operational Scope
    add_card(
        slide,
        left=0.80,
        top=2.95,
        width=col_w,
        height=1.15,
        accent_left=GC_BLUE,
    )
    add_text_box(
        slide,
        left=1.05,
        top=3.02,
        width=col_w - 0.35,
        height=0.28,
        text="OPERATIONAL SCOPE: RAF MARHAM & CARRIER STRIKE GROUP",
        font_size=11,
        bold=True,
        color=GC_BLUE,
    )
    add_text_box(
        slide,
        left=1.05,
        top=3.30,
        width=col_w - 0.35,
        height=0.70,
        text="Joint fleet operations across 617 Sqn ('The Dambusters'), 207 OCU at RAF Marham, and 809 NAS embarked aboard HMS Queen Elizabeth.",
        font_size=11,
        color=TEXT_SECONDARY,
    )

    # Card 2: Mission Mandate
    add_card(
        slide,
        left=0.80,
        top=4.25,
        width=col_w,
        height=1.15,
        accent_left=GC_GREEN,
    )
    add_text_box(
        slide,
        left=1.05,
        top=4.32,
        width=col_w - 0.35,
        height=0.28,
        text="MISSION MANDATE: 07:30Z 4-SHIP COMBAT SORTIE LAUNCH",
        font_size=11,
        bold=True,
        color=GC_GREEN,
    )
    add_text_box(
        slide,
        left=1.05,
        top=4.60,
        width=col_w - 0.35,
        height=0.70,
        text="Protecting the morning flying programme under DEF STAN 00-970 airworthiness regulations without administrative flight scrubs.",
        font_size=11,
        color=TEXT_SECONDARY,
    )

    # Card 3: Autonomous Action Speed
    add_card(
        slide,
        left=0.80,
        top=5.55,
        width=col_w,
        height=1.15,
        accent_left=GC_YELLOW,
    )
    add_text_box(
        slide,
        left=1.05,
        top=5.62,
        width=col_w - 0.35,
        height=0.28,
        text="OPERATIONAL VELOCITY: REAL-TIME NATURAL LANGUAGE ACTION",
        font_size=11,
        bold=True,
        color=GC_YELLOW,
    )
    add_text_box(
        slide,
        left=1.05,
        top=5.90,
        width=col_w - 0.35,
        height=0.70,
        text="Direct conversational interrogation of the live F35 Data Warehouse and S1000D manuals, rendering Spreadsheet Cards and briefing slides in seconds.",
        font_size=11,
        color=TEXT_SECONDARY,
    )

    # Right Column: Featured Aircraft Photography
    img_card_x = 6.65
    img_card_w = 5.85
    img_card_h = 3.75
    add_card(
        slide,
        left=img_card_x,
        top=2.95,
        width=img_card_w,
        height=img_card_h,
        bg_color=CARD_BG,
        border_color=CARD_BORDER,
    )
    if F35_RAF_PHOTO_PATH.exists():
        add_image_safe(
            slide,
            F35_RAF_PHOTO_PATH,
            left=img_card_x + 0.10,
            top=3.05,
            width=img_card_w - 0.20,
        )

    # Photo Caption Card Below Photo
    add_card(
        slide,
        left=img_card_x,
        top=6.05,
        width=img_card_w,
        height=0.65,
        bg_color=RGBColor(241, 243, 244),
        border_color=CARD_BORDER,
    )
    add_text_box(
        slide,
        left=img_card_x + 0.20,
        top=6.15,
        width=img_card_w - 0.40,
        height=0.45,
        text="RAF Lightning Force · F-35B Short Take-Off · HMS Queen Elizabeth Flight Deck",
        font_size=11,
        bold=True,
        color=TEXT_PRIMARY,
        align=PP_ALIGN.CENTER,
    )

    add_footer(slide, slide_number=1)

    set_speaker_notes(
        slide,
        """[SPEAKER SCRIPT — 30 SECONDS]
"Good morning, leadership team. Today we are demonstrating the Intelligent Action Layer for F-35 Fleet Sustainment.

In military aviation, flight-line readiness wins wars. Right now, across RAF Marham and the Carrier Strike Group, frontline maintainers and engineering commanders face an invisible enemy: disconnected data silos, static dashboards, and the manual drag of spreadsheet exports.

Over the next few minutes, we will show you how autonomous agents running directly on top of the F-35 Data Warehouse turn hours of administrative friction into decisive operational velocity—compressing a morning of Carrier Strike Group sustainment from 90 minutes into just 4 minutes."
""",
    )


# ==============================================================================
# Slide 2: The Villain — The 06:30Z "Oracle-to-Excel" Ritual
# ==============================================================================
def build_slide_2(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, BG_WHITE)

    add_google_header(
        slide,
        act_badge="CURRENT STATE",
        title="The Villain: The 06:30Z 'Oracle-to-Excel' Ritual",
        subtitle="How Frontline Maintainers Become Human ETL Pipelines Before Turning a Wrench",
        timestamp="06:30Z",
        badge_color=GC_RED,
    )

    # 3 Triad Cards side by side
    card_w = 3.82
    top_y = 1.45
    card_h = 3.95

    # Card 1: Stale on Export
    add_card(
        slide,
        left=0.60,
        top=top_y,
        width=card_w,
        height=card_h,
        accent_top=GC_RED,
    )
    pill1 = add_rect(
        slide,
        left=0.85,
        top=top_y + 0.20,
        width=2.10,
        height=0.28,
        fill_color=RGBColor(253, 231, 233),
        border_color=GC_RED,
        rounded=True,
    )
    pill1.text_frame.paragraphs[0].text = "⏰ TIME SINK: 45–90 MIN"
    pill1.text_frame.paragraphs[0].runs[0].font.size = Pt(9.5)
    pill1.text_frame.paragraphs[0].runs[0].font.bold = True
    pill1.text_frame.paragraphs[0].runs[0].font.color.rgb = GC_RED

    add_text_box(
        slide,
        left=0.85,
        top=top_y + 0.60,
        width=card_w - 0.50,
        height=0.35,
        text="Stale on Export",
        font_size=16,
        bold=True,
        color=TEXT_PRIMARY,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 1.05,
        width=card_w - 0.50,
        height=2.65,
        text="• Morning ERP dumps exported at 06:30Z are immediately frozen in time.\n\n• Completely blind to overnight pilot debriefs, late-night carrier recoveries, and emergency depot parts arriving at 06:45Z.\n\n• Maintainers make critical life-limited part decisions on obsolete snapshots, risking airworthiness breaches.",
        font_size=12,
        color=TEXT_SECONDARY,
    )

    # Card 2: Spreadsheet Roulette
    add_card(
        slide,
        left=4.75,
        top=top_y,
        width=card_w,
        height=card_h,
        accent_top=GC_YELLOW,
    )
    pill2 = add_rect(
        slide,
        left=5.00,
        top=top_y + 0.20,
        width=1.90,
        height=0.28,
        fill_color=RGBColor(254, 247, 224),
        border_color=GC_YELLOW,
        rounded=True,
    )
    pill2.text_frame.paragraphs[0].text = "⚠️ VERSION DRIFT"
    pill2.text_frame.paragraphs[0].runs[0].font.size = Pt(9.5)
    pill2.text_frame.paragraphs[0].runs[0].font.bold = True
    pill2.text_frame.paragraphs[0].runs[0].font.color.rgb = GC_YELLOW

    add_text_box(
        slide,
        left=5.00,
        top=top_y + 0.60,
        width=card_w - 0.50,
        height=0.35,
        text="Spreadsheet Roulette",
        font_size=16,
        bold=True,
        color=TEXT_PRIMARY,
    )
    add_text_box(
        slide,
        left=5.00,
        top=top_y + 1.05,
        width=card_w - 0.50,
        height=2.65,
        text="• Disconnected .xlsx files proliferate across Avionics, Airframe, and Carrier bays.\n\n• Broken =VLOOKUP formulas and inconsistent column formatting lead to conflicting fleet readiness figures.\n\n• Maintainers spend 30–45 minutes arguing over whose spreadsheet has the real numbers instead of prepping jets.",
        font_size=12,
        color=TEXT_SECONDARY,
    )

    # Card 3: Airworthiness Risk
    add_card(
        slide,
        left=8.90,
        top=top_y,
        width=card_w,
        height=card_h,
        accent_top=GC_RED,
    )
    pill3 = add_rect(
        slide,
        left=9.15,
        top=top_y + 0.20,
        width=2.20,
        height=0.28,
        fill_color=RGBColor(253, 231, 233),
        border_color=GC_RED,
        rounded=True,
    )
    pill3.text_frame.paragraphs[0].text = "🔴 AIRWORTHINESS RISK"
    pill3.text_frame.paragraphs[0].runs[0].font.size = Pt(9.5)
    pill3.text_frame.paragraphs[0].runs[0].font.bold = True
    pill3.text_frame.paragraphs[0].runs[0].font.color.rgb = GC_RED

    add_text_box(
        slide,
        left=9.15,
        top=top_y + 0.60,
        width=card_w - 0.50,
        height=0.35,
        text="Compliance Exposure",
        font_size=16,
        bold=True,
        color=TEXT_PRIMARY,
    )
    add_text_box(
        slide,
        left=9.15,
        top=top_y + 1.05,
        width=card_w - 0.50,
        height=2.65,
        text="• Uncontrolled desktop workbooks lack cryptographic audit trails and access control.\n\n• High operational risk of releasing an over-hour aircraft or violating DEF STAN 00-970 / MAA regulations.\n\n• Central data analyst ticket queues backlog ad-hoc operational inquiries by 24–48 hours.",
        font_size=12,
        color=TEXT_SECONDARY,
    )

    # Bottom Full-Width Impact Banner
    add_card(
        slide,
        left=0.60,
        top=5.60,
        width=12.12,
        height=1.25,
        bg_color=RGBColor(253, 231, 233),
        border_color=GC_RED,
        accent_left=GC_RED,
    )
    add_text_box(
        slide,
        left=0.85,
        top=5.68,
        width=11.60,
        height=0.30,
        text="OPERATIONAL IMPACT: 45 TO 90 MINUTES LOST PER SHIFT",
        font_size=13,
        bold=True,
        color=GC_RED,
    )
    add_text_box(
        slide,
        left=0.85,
        top=6.00,
        width=11.60,
        height=0.75,
        text="Treating senior non-commissioned officers and aerospace engineers as human ETL pipelines burns hundreds of engineering hours every week, delays shift handovers, and introduces unacceptable flight safety risk.",
        font_size=11.5,
        color=TEXT_PRIMARY,
    )

    add_footer(slide, slide_number=2)

    set_speaker_notes(
        slide,
        """[SPEAKER SCRIPT — 45 SECONDS]
"Here is the operational reality today. Every morning at 06:30Z, 15 minutes before the shift stand-up, maintenance managers log into Oracle—the transactional system of record—and dump thousands of rows into Microsoft Excel.

Technicians spend up to 90 minutes formatting rows, copying tabs, and writing fragile VLOOKUP formulas.

The moment that spreadsheet is exported, it is dead on arrival. If a pilot reports a defect at 06:40Z, or an emergency actuator arrives at the depot at 06:45Z, the spreadsheet is completely blind to it.

Even worse: disconnected spreadsheets circulate across bays, creating conflicting numbers. And if someone makes a typo in an Excel cell, we risk releasing an over-hour jet in violation of MAA airworthiness regulations.

This is the drag we are eliminating."
""",
    )


# ==============================================================================
# Slide 3: The Target State — The Intelligent Action Layer
# ==============================================================================
def build_slide_3(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, BG_WHITE)

    add_google_header(
        slide,
        act_badge="TARGET ARCHITECTURE",
        title="The Target State: The Intelligent Action Layer",
        subtitle="Democratising Real-Time Analytics to the Flight Line Without Replacing Oracle",
        badge_color=GC_BLUE,
    )

    # 3 Horizontal Architecture Tiers
    card_w = 12.12
    card_h = 1.55
    top_y = 1.45

    # Tier 1
    add_card(
        slide,
        left=0.60,
        top=top_y,
        width=card_w,
        height=card_h,
        accent_left=TEXT_MUTED,
    )
    add_text_box(
        slide,
        left=0.90,
        top=top_y + 0.12,
        width=11.50,
        height=0.30,
        text="TIER 1: TRANSACTIONAL SYSTEM OF RECORD (ORACLE ERP/MRO)",
        font_size=12,
        bold=True,
        color=TEXT_MUTED,
    )
    add_text_box(
        slide,
        left=0.90,
        top=top_y + 0.45,
        width=11.50,
        height=0.95,
        text="• Remains untouched as the transactional single source of truth—zero multi-million pound rip-and-replace risk.\n• Records work orders, depot supply chains, and maintenance history with full compliance integrity.\n• Continuously streams updates without locking operational transactional databases.",
        font_size=11.5,
        color=TEXT_SECONDARY,
    )

    # Tier 2
    top_y += 1.70
    add_card(
        slide,
        left=0.60,
        top=top_y,
        width=card_w,
        height=card_h,
        accent_left=GC_BLUE,
    )
    add_text_box(
        slide,
        left=0.90,
        top=top_y + 0.12,
        width=11.50,
        height=0.30,
        text="TIER 2: HIGH-PERFORMANCE F35 DATA WAREHOUSE",
        font_size=12,
        bold=True,
        color=GC_BLUE,
    )
    add_text_box(
        slide,
        left=0.90,
        top=top_y + 0.45,
        width=11.50,
        height=0.95,
        text="• Continuous change data capture (CDC) replication from the transactional layer.\n• Partitioned, clustered F35 Data Warehouse tables (600+ records) uniting telemetry, depot stock, sorties, and bay tooling.\n• High-throughput analytical query engine across the entire Carrier Strike Group and allied fleet.",
        font_size=11.5,
        color=TEXT_SECONDARY,
    )

    # Tier 3
    top_y += 1.70
    add_card(
        slide,
        left=0.60,
        top=top_y,
        width=card_w,
        height=card_h,
        accent_left=GC_GREEN,
    )
    add_text_box(
        slide,
        left=0.90,
        top=top_y + 0.12,
        width=11.50,
        height=0.30,
        text="TIER 3: THE INTELLIGENT ACTION LAYER — AGENTS (F35 SUPPORT)",
        font_size=12,
        bold=True,
        color=GC_GREEN,
    )
    add_text_box(
        slide,
        left=0.90,
        top=top_y + 0.45,
        width=11.50,
        height=0.95,
        text="• Frontline maintainers interrogate fleet readiness with Agents (F35 Support) in plain English—no SQL or BI training required.\n• Deterministic 3-layer semantic canonicalizer maps military slang ('Lizzy', 'fit to fly') with zero SQL errors.\n• Blends structured F35 Data Warehouse data with S1000D technical manuals and renders live Spreadsheet Cards.",
        font_size=11.5,
        color=TEXT_PRIMARY,
    )

    # Bottom Value Summary Pill
    add_card(
        slide,
        left=0.60,
        top=6.60,
        width=card_w,
        height=0.38,
        bg_color=RGBColor(232, 240, 254),
        border_color=GC_BLUE,
    )
    add_text_box(
        slide,
        left=0.80,
        top=6.64,
        width=card_w - 0.40,
        height=0.30,
        text="CORE VALUE: Democratises Data Analytics directly to the flight line without altering existing ERP infrastructure.",
        font_size=10.5,
        bold=True,
        color=ACCENT_NAVY,
        align=PP_ALIGN.CENTER,
    )

    add_footer(slide, slide_number=3)

    set_speaker_notes(
        slide,
        """[SPEAKER SCRIPT — 40 SECONDS]
"We do not need to replace Oracle. Replacing an aerospace ERP costs tens of millions of pounds and takes five to seven years.

Instead, Google Cloud Agents sit directly on top of the continuously replicated F-35 Data Warehouse as a non-disruptive 'Intelligent Action Layer'.

Oracle continues doing what it does best—recording transactions. The F-35 Data Warehouse handles high-speed analytical replication.

And Agents democratise data analytics directly to the flight-line engineer in natural language. Maintainers ask questions in plain English, and in real time, the agent executes read-only SQL, references S1000D technical manuals, and delivers auditable operational answers. Zero hallucination. Let's see this live."
""",
    )


# ==============================================================================
# Slide 4: Act 1 Live Demo — Morning Stand-Up & Shift Dispatch (06:45Z)
# ==============================================================================
def build_slide_4(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, BG_WHITE)

    add_google_header(
        slide,
        act_badge="ACT 1 DEMO",
        title="Act 1: Morning Stand-Up & Shift Dispatch",
        subtitle="Triage Grounded Lead Jet ZM151, Uncover Hidden Defects & Verify Bay Readiness",
        timestamp="06:45Z",
        operational_tag="LIVE DEMO",
        badge_color=GC_BLUE,
    )

    # Top Row: Split Dilemma Cards
    card_w = 5.92
    top_y = 1.45
    card_h = 2.45

    # Left: The Triage Dilemma
    add_card(
        slide,
        left=0.60,
        top=top_y,
        width=card_w,
        height=card_h,
        accent_top=GC_RED,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 0.15,
        width=card_w - 0.50,
        height=0.30,
        text="🔴 THE TRIAGE DILEMMA: LEAD JET ZM151 GROUNDED",
        font_size=12,
        bold=True,
        color=GC_RED,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 0.48,
        width=card_w - 0.50,
        height=1.85,
        text="• Grounded on Board: Lead jet ZM151 is assigned to the 07:30Z combat sortie but flagged red on the status board.\n\n• Actuator Limit Exceeded: Horizontal Tail Actuator reached 1,000.4 hrs (exceeding the strict 1,000.0-hr life limit).\n\n• Unexplained Defect: Night pilot reported a stiff canopy latch, but ODIN/PMA logged ZERO BIT fault codes (repeat CND defect).",
        font_size=11,
        color=TEXT_SECONDARY,
    )

    # Right: Bay Readiness & Tool Verification
    add_card(
        slide,
        left=6.80,
        top=top_y,
        width=card_w,
        height=card_h,
        accent_top=GC_GREEN,
    )
    add_text_box(
        slide,
        left=7.05,
        top=top_y + 0.15,
        width=card_w - 0.50,
        height=0.30,
        text="🟢 BAY READINESS: QUALIFIED CREW & CALIBRATED TOOLS",
        font_size=12,
        bold=True,
        color=GC_GREEN,
    )
    add_text_box(
        slide,
        left=7.05,
        top=top_y + 0.48,
        width=card_w - 0.50,
        height=1.85,
        text="• Mechanical Bay 1: Certified maintenance team assigned and ready to receive ZM151.\n\n• Independent QA: Certified Quality Assurance Representative (QAR) on-shift for dual sign-off.\n\n• Calibrated Tooling: Digital Micro-Torque Spanner (JTD-53-30-T14) verified calibrated and staged.\n\n• The Mission Dilemma: Bay is ready—but ZM151 cannot fly the 07:30Z launch wave.",
        font_size=11,
        color=TEXT_SECONDARY,
    )

    # Bottom Row: Interactive Prompt Terminal Box
    prompts = [
        (
            "PROMPT 1 (TRIAGE CSG)",
            "What are our most urgent maintenance jobs and grounded aircraft across the Carrier Strike Group right now, ordered by how long they will take to fix?",
        ),
        (
            "PROMPT 2 (DEEP DIVE ZM151)",
            "What faults or pilot-reported issues were raised on ZM151 after its last flight, and are any repeat unconfirmed faults?",
        ),
        (
            "PROMPT 3 (BAY READINESS)",
            "Which of our open maintenance jobs are ready to start on this shift, with both qualified crew and calibrated tools staged?",
        ),
    ]
    add_live_demo_prompt_box(
        slide,
        left=0.60,
        top=4.05,
        width=12.12,
        height=2.85,
        prompts=prompts,
        capability_badge="⚡ ACTION: LIVE SPREADSHEET CARD",
    )

    add_footer(slide, slide_number=4)

    set_speaker_notes(
        slide,
        """[STAGE DIRECTION: 👉 SWITCH TO LIVE SCREEN NOW]
[SPEAKER SCRIPT — 60 SECONDS]
"👉 SWITCH TO LIVE SCREEN NOW.

It is 06:45Z at RAF Marham. The Squadron Maintenance Officer begins the morning stand-up.

Instead of hunting through spreadsheets, watch how we query the entire Carrier Strike Group in natural language.

(Paste Prompt 1): 'What are our most urgent maintenance jobs and grounded aircraft across the Carrier Strike Group right now, ordered by how long they will take to fix?'

In real time, the agent returns an interactive Spreadsheet Card with status badges and formula totals. Notice the top row: flight lead ZM151 is grounded with an actuator over its life limit.

Now let's ask what happened on its overnight flight.
(Paste Prompt 2): 'What faults or pilot-reported issues were raised on ZM151 after its last flight...?'

The agent immediately flags two issues: the actuator hour exceedance, plus an unexplained canopy latch defect that logged zero fault codes.

Finally, we verify if our bay crew and calibrated spanners are ready.
(Paste Prompt 3): 'Which of our open maintenance jobs are ready to start on this shift...?'

Everything is verified and ready for ZM151 in Bay 1. But with ZM151 entering the hangar, our 07:30Z combat launch is down a lead jet. Let's move to Act 2 to protect the sortie."
""",
    )


# ==============================================================================
# Slide 5: Act 2 Live Demo — Mission Protection & Leadership Briefing (06:52Z)
# ==============================================================================
def build_slide_5(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, BG_WHITE)

    add_google_header(
        slide,
        act_badge="ACT 2 DEMO",
        title="Act 2: Mission Protection & Leadership Briefing",
        subtitle="Swap Aircraft to Protect the 07:30Z Sortie & Render Wing Briefing Charts on Demand",
        timestamp="06:52Z",
        operational_tag="LIVE DEMO",
        badge_color=GC_BLUE,
    )

    card_w = 5.92
    top_y = 1.45
    card_h = 2.45

    # Left: Tail Swap & Depot Replenishment
    add_card(
        slide,
        left=0.60,
        top=top_y,
        width=card_w,
        height=card_h,
        accent_top=GC_BLUE,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 0.15,
        width=card_w - 0.50,
        height=0.30,
        text="🔄 SORTIE PROTECTION & DEPOT ALLOCATION",
        font_size=12,
        bold=True,
        color=GC_BLUE,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 0.48,
        width=card_w - 0.50,
        height=1.85,
        text="• Recommended Tail Swap: Reallocate Flight Lead Henderson from grounded ZM151 (1,000.4 hrs) to clean spare ZM154 (842.0 hrs · FMC).\n\n• Sortie Protected: Morning 4-ship combat sortie SRT-MAR-20261103-01 launches at 07:30Z on schedule with zero delay.\n\n• Depot Replenishment: Marham Depot stock verified (4 actuators, 18-hr fulfillment window). Work order dispatched automatically.",
        font_size=11,
        color=TEXT_SECONDARY,
    )

    # Right: On-Demand Briefing Graphic Thumbnail
    add_card(
        slide,
        left=6.80,
        top=top_y,
        width=card_w,
        height=card_h,
        accent_top=GC_YELLOW,
    )
    add_text_box(
        slide,
        left=7.05,
        top=top_y + 0.15,
        width=card_w - 0.50,
        height=0.30,
        text="📊 ON-DEMAND WING COMMAND BRIEFING CHART",
        font_size=12,
        bold=True,
        color=GC_YELLOW,
    )
    if DASHBOARD_PNG_PATH.exists():
        add_image_safe(
            slide,
            DASHBOARD_PNG_PATH,
            left=7.05,
            top=top_y + 0.50,
            width=card_w - 0.50,
        )
    else:
        add_text_box(
            slide,
            left=7.05,
            top=top_y + 0.50,
            width=card_w - 0.50,
            height=1.70,
            text="[ Full HD 16:9 Presentation Graphic generated dynamically on demand ]",
            font_size=12,
            italic=True,
            color=TEXT_MUTED,
            align=PP_ALIGN.CENTER,
        )

    # Bottom Row: Interactive Prompt Terminal Box
    prompts = [
        (
            "PROMPT 4 (TAIL SWAP & DEPOT)",
            "Check RAF Marham F-35 horizontal tail actuator hours against our 30-day spare parts stock, and recommend an aircraft swap for morning sortie SRT-MAR-20261103-01.",
        ),
        (
            "PROMPT 5 (BRIEFING SLIDE)",
            "Render the full Executive Briefing Dashboard for my presentation slide deck.",
        ),
    ]
    add_live_demo_prompt_box(
        slide,
        left=0.60,
        top=4.05,
        width=12.12,
        height=2.85,
        prompts=prompts,
        capability_badge="⚡ ACTION: FULL HD 16:9 PRESENTATION GRAPHIC",
    )

    add_footer(slide, slide_number=5)

    set_speaker_notes(
        slide,
        """[STAGE DIRECTION: 👉 SWITCH TO LIVE SCREEN NOW]
[SPEAKER SCRIPT — 50 SECONDS]
"👉 SWITCH TO LIVE SCREEN NOW.

It is now 06:52Z. We have 38 minutes until the 07:30Z combat launch wave. The Logistics Officer must protect the mission.

Watch how the agent solves this in seconds.
(Paste Prompt 4): 'Check RAF Marham F-35 horizontal tail actuator hours against our 30-day spare parts stock, and recommend an aircraft swap for morning sortie SRT-MAR-20261103-01.'

The agent correlates component hours, depot inventory, and the flying programme. It allocates a replacement actuator from Marham Depot and reallocates flight lead Henderson to clean spare ZM154 with 842 hours. The sortie is saved!

Now, the Wing Commander needs an executive briefing slide for the 07:00Z air wing meeting.
(Paste Prompt 5): 'Render the full Executive Briefing Dashboard for my presentation slide deck.'

On demand, the agent paints a 16:9 Full HD presentation graphic and uploads it to Cloud Storage. The sortie is protected, the depot is staged, and leadership is briefed."
""",
    )


# ==============================================================================
# Slide 6: Act 3 Live Demo — Allied Fleet Memory & Defect Resolution (06:56Z)
# ==============================================================================
def build_slide_6(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, BG_WHITE)

    add_google_header(
        slide,
        act_badge="ACT 3 DEMO",
        title="Act 3: Allied Fleet Memory & Defect Resolution",
        subtitle="Unlock 5 Years of Coalition Flight Logs to Solve the Zero-Code Canopy Latch Defect",
        timestamp="06:56Z",
        operational_tag="LIVE DEMO",
        badge_color=GC_BLUE,
    )

    card_w = 5.92
    top_y = 1.45
    card_h = 2.45

    # Left: Diagnostic Mystery & Coalition Intelligence
    add_card(
        slide,
        left=0.60,
        top=top_y,
        width=card_w,
        height=card_h,
        accent_top=GC_YELLOW,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 0.15,
        width=card_w - 0.50,
        height=0.30,
        text="🔍 DIAGNOSTIC MYSTERY & COALITION PRECEDENT",
        font_size=12,
        bold=True,
        color=GC_YELLOW,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 0.48,
        width=card_w - 0.50,
        height=1.85,
        text="• The Diagnostic Mystery: Night pilot reported canopy release handle binding on pre-flight, but ODIN/PMA shows ZERO_BIT_FAULT_LOGGED.\n\n• Cross-Service Dialect Normalization: Agent maps UK terminology ('catch', 'spanner') to US technical standards ('latch', 'wrench').\n\n• Allied Fleet Memory: Unlocks 5 years of coalition logs to locate a USMC VMFA-211 squadron log (DOC-02): cured PR-1776M sealant debris in forward roller track.",
        font_size=11,
        color=TEXT_SECONDARY,
    )

    # Right: 100% Grounded S1000D Checklist
    add_card(
        slide,
        left=6.80,
        top=top_y,
        width=card_w,
        height=card_h,
        accent_top=GC_GREEN,
    )
    add_text_box(
        slide,
        left=7.05,
        top=top_y + 0.15,
        width=card_w - 0.50,
        height=0.30,
        text="📖 100% GROUNDED S1000D CHECKLIST",
        font_size=12,
        bold=True,
        color=GC_GREEN,
    )
    add_text_box(
        slide,
        left=7.05,
        top=top_y + 0.48,
        width=card_w - 0.50,
        height=1.85,
        text="• Verbatim Engineering Citation: Grounded in S1000D Section 53-30-01 (DOC-01) technical manual.\n\n• Exact Torque Specification: Verified re-torquing specification is 18.5 N·m using the Digital Micro-Torque Spanner staged in Act 1.\n\n• Zero Guesswork, Zero Hallucination: Maintainers execute the certified procedure with zero delay, restoring ZM151 to full airworthiness.",
        font_size=11,
        color=TEXT_SECONDARY,
    )

    # Bottom Row: Interactive Prompt Terminal Box
    prompts = [
        (
            "PROMPT 6 (ALLIED DEFECT LOOKUP)",
            "On ZM151, our night-sortie pilot reported a stiff canopy release handle that hesitated to latch, with no fault codes logged on the jet. Have allied squadrons seen this before, and what is the approved fix?",
        ),
    ]
    add_live_demo_prompt_box(
        slide,
        left=0.60,
        top=4.05,
        width=12.12,
        height=2.85,
        prompts=prompts,
        capability_badge="⚡ VERIFIED: 100% GROUNDED S1000D CITATIONS",
    )

    add_footer(slide, slide_number=6)

    set_speaker_notes(
        slide,
        """[STAGE DIRECTION: 👉 SWITCH TO LIVE SCREEN NOW]
[SPEAKER SCRIPT — 60 SECONDS]
"👉 SWITCH TO LIVE SCREEN NOW.

It is 06:56Z. Back in the maintenance bay, technicians are standing in front of ZM151. Why did the canopy handle stick if there are zero fault codes?

A static dashboard is completely useless here—dashboards cannot read text paragraphs or foreign flight logs.

(Paste Prompt 6): 'On ZM151, our night-sortie pilot reported a stiff canopy release handle that hesitated to latch, with no fault codes logged on the jet. Have allied squadrons seen this before, and what is the approved fix?'

Watch what happens: the agent searches 5 years of coalition logs across the RAF, Royal Navy, and US Marine Corps. It normalizes terminology—translating British 'catch' to American 'latch'.

It finds an exact precedent from a USMC squadron in Yuma: cured silicon sealant debris in the roller track.

And look at the clickable citation: it links directly to S1000D Section 53-30-01, giving our maintainers the verified 18.5 N·m torque spec for the spanner staged in Act 1. Zero guesswork. Zero hallucination."
""",
    )


# ==============================================================================
# Slide 7: Why Agents Beat Static BI Dashboards
# ==============================================================================
def build_slide_7(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, BG_WHITE)

    add_google_header(
        slide,
        act_badge="STRATEGIC VALUE",
        title="Why Agents Beat Static BI Dashboards",
        subtitle="Closing the Operational Gap Between Passive Observation and Decisive Flight-Line Action",
        badge_color=GC_BLUE,
    )

    # 4 Quadrants (2x2 grid)
    quad_w = 5.92
    quad_h = 2.65

    # Quadrant 1: Action vs Display
    add_card(
        slide,
        left=0.60,
        top=1.45,
        width=quad_w,
        height=quad_h,
        accent_top=GC_BLUE,
    )
    add_text_box(
        slide,
        left=0.85,
        top=1.58,
        width=quad_w - 0.50,
        height=0.30,
        text="1. ACTION VS. PASSIVE DISPLAY",
        font_size=13,
        bold=True,
        color=GC_BLUE,
    )
    add_text_box(
        slide,
        left=0.85,
        top=1.92,
        width=quad_w - 0.50,
        height=2.05,
        text="• Static BI Dashboards: Passive rearview mirrors displaying red tiles. An officer must open 4 different systems (SAP, GOLDesp, Excel, PDFs) to take action.\n\n• Autonomous Agents: Active reasoning systems that cross-correlate component limits, recommend tail swaps, and stage depot inventory in a single turn.",
        font_size=11.5,
        color=TEXT_SECONDARY,
    )

    # Quadrant 2: Workforce Democratisation
    add_card(
        slide,
        left=6.80,
        top=1.45,
        width=quad_w,
        height=quad_h,
        accent_top=GC_GREEN,
    )
    add_text_box(
        slide,
        left=7.05,
        top=1.58,
        width=quad_w - 0.50,
        height=0.30,
        text="2. WORKFORCE DEMOCRATISATION",
        font_size=13,
        bold=True,
        color=GC_GREEN,
    )
    add_text_box(
        slide,
        left=7.05,
        top=1.92,
        width=quad_w - 0.50,
        height=2.05,
        text="• Static BI Dashboards: Locked to pre-built filters. Any ad-hoc operational query requires submitting a ticket to a central data analyst with a 48-hour delay.\n\n• Autonomous Agents: Frontline flight sergeants ask ad-hoc questions in everyday English and receive verified, governed answers immediately.",
        font_size=11.5,
        color=TEXT_SECONDARY,
    )

    # Quadrant 3: Multimodal Scope
    add_card(
        slide,
        left=0.60,
        top=4.25,
        width=quad_w,
        height=quad_h,
        accent_top=GC_YELLOW,
    )
    add_text_box(
        slide,
        left=0.85,
        top=4.38,
        width=quad_w - 0.50,
        height=0.30,
        text="3. MULTIMODAL INTELLIGENCE",
        font_size=13,
        bold=True,
        color=GC_YELLOW,
    )
    add_text_box(
        slide,
        left=0.85,
        top=4.72,
        width=quad_w - 0.50,
        height=2.05,
        text="• Static BI Dashboards: Strictly restricted to structured database tables. Completely blind to technical manuals, debrief texts, and foreign logs.\n\n• Autonomous Agents: Seamlessly fuse live F-35 Data Warehouse telemetry with 10,000-page S1000D PDF publications, pilot debrief narratives, and coalition logs.",
        font_size=11.5,
        color=TEXT_SECONDARY,
    )

    # Quadrant 4: Airworthiness Determinism
    add_card(
        slide,
        left=6.80,
        top=4.25,
        width=quad_w,
        height=quad_h,
        accent_top=GC_RED,
    )
    add_text_box(
        slide,
        left=7.05,
        top=4.38,
        width=quad_w - 0.50,
        height=0.30,
        text="4. AIRWORTHINESS DETERMINISM",
        font_size=13,
        bold=True,
        color=GC_RED,
    )
    add_text_box(
        slide,
        left=7.05,
        top=4.72,
        width=quad_w - 0.50,
        height=2.05,
        text="• Static BI Dashboards: Unvetted desktop spreadsheets suffer silent formula bugs, version drift, and unverified data entries that breach airworthiness.\n\n• Autonomous Agents: Deterministic SQL canonicalization, read-only safety envelopes, and 100% verbatim citations ensuring DEF STAN compliance.",
        font_size=11.5,
        color=TEXT_SECONDARY,
    )

    add_footer(slide, slide_number=7)

    set_speaker_notes(
        slide,
        """[SPEAKER SCRIPT — 45 SECONDS]
"Leadership frequently asks: 'Why can't our data science team just build this in PowerBI or Tableau?'

Here is the fundamental difference. Dashboards are passive rearview mirrors. They tell you a plane is broken, but they cannot tell you what to do.

To solve lead jet ZM151 in a dashboard, an engineering officer has to open SAP, open GOLDesp, open three Excel files, and thumb through a 10,000-page manual.

Agents collapse that four-screen swivel-chair into a single natural conversation.

Moreover, agents democratise analytics: maintainers don't need to wait 48 hours for a central BI developer to build a new report. They simply ask the agent, get an instant Spreadsheet Card, and take decisive action."
""",
    )


# ==============================================================================
# Slide 8: Semantic Governance & Flight-Line Interoperability
# ==============================================================================
def build_slide_8(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, BG_WHITE)

    add_google_header(
        slide,
        act_badge="SEMANTIC GOVERNANCE",
        title="Semantic Governance in Action: Military Vernacular",
        subtitle="Deterministic Interpretation of Colloquial Slang with Zero SQL Errors",
        badge_color=GC_BLUE,
    )

    card_w = 12.12
    top_y = 1.45

    # Top Card: The Executive Inquiry
    add_card(
        slide,
        left=0.60,
        top=top_y,
        width=card_w,
        height=1.25,
        accent_top=GC_BLUE,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 0.12,
        width=card_w - 0.50,
        height=0.28,
        text="THE EXECUTIVE INQUIRY: NATURAL MILITARY SLANG",
        font_size=11,
        bold=True,
        color=GC_BLUE,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 0.42,
        width=card_w - 0.50,
        height=0.70,
        text='Commander\'s Prompt: "Tell me what tails on Lizzy are fit to fly"',
        font_size=16,
        bold=True,
        color=TEXT_PRIMARY,
    )

    # Middle Card: 3-Layer Semantic Governance Layer
    top_y += 1.40
    add_card(
        slide,
        left=0.60,
        top=top_y,
        width=card_w,
        height=1.55,
        accent_top=GC_YELLOW,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 0.12,
        width=card_w - 0.50,
        height=0.28,
        text="THE 3-LAYER SEMANTIC GOVERNANCE ENGINE",
        font_size=11,
        bold=True,
        color=GC_YELLOW,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 0.42,
        width=card_w - 0.50,
        height=1.00,
        text="• Vernacular Resolution: 'Lizzy' ➔ Deterministically canonicalized to base_location = 'HMS Queen Elizabeth'.\n• Airworthiness Mapping: 'fit to fly' ➔ Deterministically mapped to mission_readiness_code = 'FMC' (Fully Mission Capable).\n• Read-Only Guardrail: Strict SELECT whitelist execution against the live F-35 Data Warehouse with zero SQL injection risk.",
        font_size=12,
        color=TEXT_SECONDARY,
    )

    # Bottom Card: Governed Fleet Spreadsheet Output
    top_y += 1.70
    add_card(
        slide,
        left=0.60,
        top=top_y,
        width=card_w,
        height=2.25,
        accent_top=GC_GREEN,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 0.12,
        width=card_w - 0.50,
        height=0.28,
        text="GOVERNED OUTPUT: EMBARKED SERVICEABLE FLEET (SPREADSHEET CARD)",
        font_size=11,
        bold=True,
        color=GC_GREEN,
    )

    # Table of 5 embarked FMC tails (Alternating white and soft grey rows)
    tails = [
        ("ZM166", "809 NAS", "Carrier Bay 1", "🟢 FMC", "0 Open Faults", "READY FOR LAUNCH"),
        ("ZM172", "809 NAS", "Flight Deck", "🟢 FMC", "0 Open Faults", "READY FOR LAUNCH"),
        ("ZM136", "809 NAS", "Carrier Bay 2", "🟢 FMC", "0 Open Faults", "READY FOR LAUNCH"),
        ("ZM142", "809 NAS", "Flight Deck", "🟢 FMC", "0 Open Faults", "READY FOR LAUNCH"),
        ("ZM148", "809 NAS", "Carrier Bay 3", "🟢 FMC", "0 Open Faults", "READY FOR LAUNCH"),
    ]
    table_y = top_y + 0.45
    for i, (tail, sqn, bay, status, faults, ready) in enumerate(tails):
        row_bg = CARD_BG if i % 2 == 0 else RGBColor(241, 243, 244)
        row_y = table_y + (i * 0.33)
        add_rect(
            slide,
            left=0.85,
            top=row_y,
            width=card_w - 0.50,
            height=0.30,
            fill_color=row_bg,
            border_color=CARD_BORDER,
            border_pt=0.5,
            rounded=False,
        )
        row_text = f"Tail: {tail}   |   Sqn: {sqn}   |   Loc: {bay}   |   Status: {status}   |   Faults: {faults}   |   {ready}"
        add_text_box(
            slide,
            left=0.95,
            top=row_y + 0.02,
            width=card_w - 0.70,
            height=0.26,
            text=row_text,
            font_size=10.5,
            bold=(i == 0),
            color=TEXT_PRIMARY,
        )

    add_footer(slide, slide_number=8)

    set_speaker_notes(
        slide,
        """[SPEAKER SCRIPT — 40 SECONDS]
"What happens when a commander or admiral asks a question in everyday military vernacular?

If an executive asks: 'Tell me what tails on Lizzy are fit to fly'—an unconstrained LLM might hallucinate or fail to understand the colloquialism.

Our Semantic Governance Layer intercepts the query, deterministically maps 'Lizzy' to HMS Queen Elizabeth and 'fit to fly' to Fully Mission Capable (FMC), and executes a verified read-only SQL query against the warehouse.

Immediately, it renders a spreadsheet card showing the five serviceable aircraft aboard Queen Elizabeth.

That is enterprise governance in action: natural conversational flexibility paired with military-grade determinism."
""",
    )


# ==============================================================================
# Slide 9: Mission Impact & Next Steps (The Transformation)
# ==============================================================================
def build_slide_9(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, BG_WHITE)

    add_google_header(
        slide,
        act_badge="TRANSFORMATION",
        title="Mission Impact: From 90 Minutes to 4 Minutes",
        subtitle="Eliminating Administrative Drag to Deliver Decisive Operational Velocity",
        badge_color=GC_BLUE,
    )

    card_w = 3.82
    top_y = 1.45
    card_h = 2.45

    # Metric 1: 90 Mins -> 4 Mins
    add_card(
        slide,
        left=0.60,
        top=top_y,
        width=card_w,
        height=card_h,
        accent_top=GC_BLUE,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 0.20,
        width=card_w - 0.50,
        height=0.55,
        text="90m ➔ 4m",
        font_size=32,
        bold=True,
        color=GC_BLUE,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 0.80,
        width=card_w - 0.50,
        height=0.30,
        text="95% TIME SAVINGS",
        font_size=12,
        bold=True,
        color=TEXT_PRIMARY,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 1.15,
        width=card_w - 0.50,
        height=1.15,
        text="Morning triage, spreadsheet wrangling, and shift dispatch compressed from 90 minutes of manual friction into a 4-minute conversation.",
        font_size=11.5,
        color=TEXT_SECONDARY,
    )

    # Metric 2: 100% Grounded
    add_card(
        slide,
        left=4.75,
        top=top_y,
        width=card_w,
        height=card_h,
        accent_top=GC_GREEN,
    )
    add_text_box(
        slide,
        left=5.00,
        top=top_y + 0.20,
        width=card_w - 0.50,
        height=0.55,
        text="100%",
        font_size=32,
        bold=True,
        color=GC_GREEN,
    )
    add_text_box(
        slide,
        left=5.00,
        top=top_y + 0.80,
        width=card_w - 0.50,
        height=0.30,
        text="GROUNDED & AUDITABLE",
        font_size=12,
        bold=True,
        color=TEXT_PRIMARY,
    )
    add_text_box(
        slide,
        left=5.00,
        top=top_y + 1.15,
        width=card_w - 0.50,
        height=1.15,
        text="Zero hallucination. Every procedure, torque specification, and part number is anchored to S1000D technical publications and DEF STAN standards.",
        font_size=11.5,
        color=TEXT_SECONDARY,
    )

    # Metric 3: 0 Sortie Scrubs
    add_card(
        slide,
        left=8.90,
        top=top_y,
        width=card_w,
        height=card_h,
        accent_top=GC_YELLOW,
    )
    add_text_box(
        slide,
        left=9.15,
        top=top_y + 0.20,
        width=card_w - 0.50,
        height=0.55,
        text="0",
        font_size=32,
        bold=True,
        color=GC_YELLOW,
    )
    add_text_box(
        slide,
        left=9.15,
        top=top_y + 0.80,
        width=card_w - 0.50,
        height=0.30,
        text="SORTIE LAUNCH SCRUBS",
        font_size=12,
        bold=True,
        color=TEXT_PRIMARY,
    )
    add_text_box(
        slide,
        left=9.15,
        top=top_y + 1.15,
        width=card_w - 0.50,
        height=1.15,
        text="100% combat wave protection via autonomous tail swap recommendations, live depot part staging, and qualified crew verification.",
        font_size=11.5,
        color=TEXT_SECONDARY,
    )

    # Bottom Full-Width Roadmap Card
    top_y += 2.65
    add_card(
        slide,
        left=0.60,
        top=top_y,
        width=12.12,
        height=2.80,
        accent_top=GC_BLUE,
    )
    add_text_box(
        slide,
        left=0.85,
        top=top_y + 0.15,
        width=11.60,
        height=0.30,
        text="RECOMMENDED NEXT STEPS: OPERATIONAL SQUADRON PILOT",
        font_size=13,
        bold=True,
        color=GC_BLUE,
    )

    # 3 Pilot Phases
    phase_w = 3.65
    phase_h = 1.95
    phases = [
        (
            "PHASE 1: SQUADRON PILOT",
            "RAF Marham (617 Sqn)",
            "• Deploy Intelligent Action Layer alongside Oracle for 617 Sqn.\n• Validate morning stand-up triage in live hangar environments.\n• Measure maintainer time savings and user adoption.",
            GC_BLUE,
        ),
        (
            "PHASE 2: EMBARKED CSG",
            "HMS Queen Elizabeth",
            "• Extend deployment to 809 NAS aboard HMS Queen Elizabeth.\n• Integrate carrier hangar bay tooling and weapon load constraints.\n• Verify air-gap and hybrid offline replication scenarios.",
            GC_GREEN,
        ),
        (
            "PHASE 3: ALLIED FLEET MEMORY",
            "Coalition Interoperability",
            "• Connect 5-year narrative logs across USMC and USAF squadrons.\n• Establish automated cross-service defect resolution memory.\n• Full integration into MOD digital sustainment ecosystem.",
            GC_YELLOW,
        ),
    ]

    for j, (p_title, p_sub, p_desc, p_color) in enumerate(phases):
        p_x = 0.85 + (j * 3.90)
        p_card = add_card(
            slide,
            left=p_x,
            top=top_y + 0.55,
            width=phase_w,
            height=phase_h,
            bg_color=RGBColor(248, 249, 250),
            border_color=CARD_BORDER,
            accent_left=p_color,
        )
        add_text_box(
            slide,
            left=p_x + 0.15,
            top=top_y + 0.62,
            width=phase_w - 0.25,
            height=0.25,
            text=p_title,
            font_size=11,
            bold=True,
            color=p_color,
        )
        add_text_box(
            slide,
            left=p_x + 0.15,
            top=top_y + 0.86,
            width=phase_w - 0.25,
            height=0.25,
            text=p_sub,
            font_size=10,
            italic=True,
            color=TEXT_PRIMARY,
        )
        add_text_box(
            slide,
            left=p_x + 0.15,
            top=top_y + 1.14,
            width=phase_w - 0.25,
            height=1.25,
            text=p_desc,
            font_size=10,
            color=TEXT_SECONDARY,
        )

    add_footer(slide, slide_number=9)

    set_speaker_notes(
        slide,
        """[SPEAKER SCRIPT — 45 SECONDS]
"To summarize what you have seen today: in just four minutes, we transformed a double-grounding crisis into a protected combat sortie wave, staged depot replenishment, and certified a verified repair procedure.

We eliminated 90 minutes of spreadsheet drag, verified 100% compliance with military airworthiness standards, and protected the mission.

We are ready to transition this capability into an operational pilot with 617 Squadron at RAF Marham, followed by Carrier Strike Group embarked deployment.

Thank you for your time, and we welcome your questions—or we can dive into the technical architecture in our appendix."
""",
    )


# ==============================================================================
# Slide 10: Appendix — Technical & Architecture Deep-Dive (Section Divider)
# ==============================================================================
def build_slide_10(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, BG_WHITE)

    add_google_header(
        slide,
        act_badge="APPENDIX",
        title="Appendix: Architecture & Technical Foundations",
        subtitle="Multi-Agent Runtime, Warehouse Replication & Semantic Security Governance",
        badge_color=RGBColor(95, 99, 104),
    )

    card_w = 12.12
    top_y = 1.45

    # Centered Overview Card
    add_card(
        slide,
        left=0.60,
        top=top_y,
        width=card_w,
        height=5.40,
        accent_top=GC_BLUE,
    )
    add_text_box(
        slide,
        left=1.00,
        top=top_y + 0.40,
        width=card_w - 0.80,
        height=0.50,
        text="TECHNICAL ARCHITECTURE & IMPLEMENTATION DEEP-DIVE",
        font_size=18,
        bold=True,
        color=TEXT_PRIMARY,
    )
    add_text_box(
        slide,
        left=1.00,
        top=top_y + 0.95,
        width=card_w - 0.80,
        height=0.45,
        text="The following slides provide themed architecture diagram canvases detailing the engineering foundations of the F-35 Sustainment Platform:",
        font_size=13,
        color=TEXT_SECONDARY,
    )

    # 2 Topic Preview Boxes
    box_w = 5.30
    box_h = 3.30

    # Box 1: Solution Architecture Canvas
    add_card(
        slide,
        left=1.00,
        top=top_y + 1.60,
        width=box_w,
        height=box_h,
        bg_color=RGBColor(248, 249, 250),
        border_color=CARD_BORDER,
        accent_left=GC_BLUE,
    )
    add_text_box(
        slide,
        left=1.25,
        top=top_y + 1.80,
        width=box_w - 0.50,
        height=0.35,
        text="SLIDE 11: SYSTEM ARCHITECTURE & RUNTIME",
        font_size=13,
        bold=True,
        color=GC_BLUE,
    )
    add_text_box(
        slide,
        left=1.25,
        top=top_y + 2.25,
        width=box_w - 0.50,
        height=2.40,
        text="• ADK 2.0 Reasoning Engine & Coordinator Topology\n\n• Domain Sub-Agent Boundaries:\n  - @F35-Maintenance-Data (Text-to-SQL)\n  - @F35-Sustainment-Analytics (Telemetry & Charts)\n  - @F35-JTD-Search (Technical Documentation & Citations)\n\n• Pre-Warmed Singletons & High-Throughput Execution\n\n• Open Canvas for System Topology Diagram",
        font_size=12,
        color=TEXT_SECONDARY,
    )

    # Box 2: Data Flow & Governance Canvas
    add_card(
        slide,
        left=6.80,
        top=top_y + 1.60,
        width=box_w,
        height=box_h,
        bg_color=RGBColor(248, 249, 250),
        border_color=CARD_BORDER,
        accent_left=GC_GREEN,
    )
    add_text_box(
        slide,
        left=7.05,
        top=top_y + 1.80,
        width=box_w - 0.50,
        height=0.35,
        text="SLIDE 12: DATA FLOW & SEMANTIC GOVERNANCE",
        font_size=13,
        bold=True,
        color=GC_GREEN,
    )
    add_text_box(
        slide,
        left=7.05,
        top=top_y + 2.25,
        width=box_w - 0.50,
        height=2.40,
        text="• Oracle ERP/MRO Continuous CDC Ingestion\n\n• High-Performance Analytical Data Warehouse\n\n• 3-Layer Semantic Canonicalizer & Vernacular Ontology\n\n• Read-Only Safety Envelopes & SQL Guardrails\n\n• Open Canvas for Data & Security Pipeline Diagram",
        font_size=12,
        color=TEXT_SECONDARY,
    )

    add_footer(slide, slide_number=10)

    set_speaker_notes(
        slide,
        """[SPEAKER SCRIPT — 30 SECONDS]
"Moving into our technical appendix. For system architects, security officers, and engineering leadership who want to inspect the underlying mechanics, the next two slides provide dedicated architecture canvases.

Slide 11 covers the end-to-end multi-agent orchestration runtime, detailing how front-of-house intent routing delegates into specialized sub-agents with strict domain separation.

Slide 12 covers the continuous data replication pipeline and 3-layer semantic governance layer that guarantees read-only airworthiness safety."
""",
    )


# ==============================================================================
# Slide 11: Appendix — Architecture Diagram Canvas I (Themed Ready-to-Go)
# ==============================================================================
def build_slide_11(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, BG_WHITE)

    add_google_header(
        slide,
        act_badge="APPENDIX · ARCHITECTURE CANVAS",
        title="Solution Architecture & Multi-Agent Orchestration",
        subtitle="High-Level System Topology, ADK 2.0 Agent Runtime & Domain Tooling Boundaries",
        badge_color=GC_BLUE,
    )

    top_y = 1.45
    canvas_w = 8.50
    canvas_h = 5.40

    # Main Left Canvas Container
    add_card(
        slide,
        left=0.60,
        top=top_y,
        width=canvas_w,
        height=canvas_h,
        accent_top=GC_BLUE,
    )

    # Dashed Inner Placeholder Box for Custom Diagram (Soft White/Grey Canvas)
    inner_dash = add_rect(
        slide,
        left=0.85,
        top=top_y + 0.35,
        width=canvas_w - 0.50,
        height=canvas_h - 0.60,
        fill_color=RGBColor(248, 249, 250),
        border_color=GC_BLUE,
        border_pt=1.5,
        rounded=True,
        dash_style=MSO_LINE_DASH_STYLE.DASH,
    )
    add_text_box(
        slide,
        left=1.20,
        top=top_y + 1.80,
        width=canvas_w - 1.20,
        height=0.50,
        text="[ ARCHITECTURE DIAGRAM CANVAS — SYSTEM TOPOLOGY & AGENT RUNTIME ]",
        font_size=13,
        bold=True,
        color=ACCENT_NAVY,
        align=PP_ALIGN.CENTER,
    )
    add_text_box(
        slide,
        left=1.20,
        top=top_y + 2.40,
        width=canvas_w - 1.20,
        height=1.20,
        text="Paste System Architecture Diagram Here\n\n(ADK 2.0 Agent Runtime, Root Coordinator, Specialized Domain Sub-Agents,\nPre-Warmed Data Warehouse & Document Search Singletons & Cloud Storage Tier)",
        font_size=11,
        italic=True,
        color=TEXT_SECONDARY,
        align=PP_ALIGN.CENTER,
    )

    # Right Architecture Annotation Sidebar
    side_x = 9.30
    side_w = 3.42
    add_card(
        slide,
        left=side_x,
        top=top_y,
        width=side_w,
        height=canvas_h,
        accent_top=GC_BLUE,
    )
    add_text_box(
        slide,
        left=side_x + 0.20,
        top=top_y + 0.15,
        width=side_w - 0.40,
        height=0.30,
        text="KEY ARCHITECTURAL HIGHLIGHTS",
        font_size=11,
        bold=True,
        color=GC_BLUE,
    )

    callouts = [
        (
            "PRESENTATION & UI TIER",
            "• Interactive Spreadsheet Cards\n• Vega-Lite Chart Specs\n• On-Demand 16:9 Presentation Slides",
            GC_BLUE,
        ),
        (
            "ADK 2.0 AGENT RUNTIME",
            "• Root Coordinator Router\n• Tier 1/2 Fast-Path Interception\n• Deterministic Intent Routing",
            GC_GREEN,
        ),
        (
            "SPECIALIZED SUB-AGENTS",
            "• Agents (F35 Support) Multi-Agent Fleet\n• @F35-Maintenance-Data, @F35-Sustainment-Analytics\n• @F35-JTD-Search (S1000D Manuals)",
            GC_YELLOW,
        ),
        (
            "PERFORMANCE & SECURITY",
            "• Pre-warmed analytical & search clients\n• In-memory credential caching\n• Strict EU / europe-west1 residency",
            GC_RED,
        ),
    ]

    c_y = top_y + 0.50
    for title, desc, color in callouts:
        add_card(
            slide,
            left=side_x + 0.15,
            top=c_y,
            width=side_w - 0.30,
            height=1.05,
            bg_color=RGBColor(248, 249, 250),
            border_color=CARD_BORDER,
            accent_left=color,
        )
        add_text_box(
            slide,
            left=side_x + 0.28,
            top=c_y + 0.06,
            width=side_w - 0.45,
            height=0.22,
            text=title,
            font_size=10,
            bold=True,
            color=color,
        )
        add_text_box(
            slide,
            left=side_x + 0.28,
            top=c_y + 0.28,
            width=side_w - 0.45,
            height=0.72,
            text=desc,
            font_size=9.5,
            color=TEXT_SECONDARY,
        )
        c_y += 1.15

    add_footer(slide, slide_number=11)

    set_speaker_notes(
        slide,
        """[SPEAKER SCRIPT — 45 SECONDS]
"This slide provides the full solution architecture topology for the F-35 Fleet Sustainment platform.

The core design principle is strict domain separation across three specialized sub-agents. The front-of-house coordinator never generates SQL directly—it classifies intent and delegates to the appropriate specialist agent.

Notice the performance engineering: in-memory credential caching and pre-warmed singleton clients eliminate cold-start overhead, guaranteeing high-performance responsiveness across the board. All data storage, search datastores, and compute run in strict compliance with EU data residency."
""",
    )


# ==============================================================================
# Slide 12: Appendix — Architecture Diagram Canvas II (Themed Ready-to-Go)
# ==============================================================================
def build_slide_12(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, BG_WHITE)

    add_google_header(
        slide,
        act_badge="APPENDIX · DATA ARCHITECTURE",
        title="Data Flow, Continuous Replication & Semantic Governance",
        subtitle="Transactional ERP/MRO Ingestion, Data Warehouse Pipeline & Read-Only Safety Envelopes",
        badge_color=GC_GREEN,
    )

    top_y = 1.45
    canvas_w = 8.50
    canvas_h = 5.40

    # Main Left Canvas Container
    add_card(
        slide,
        left=0.60,
        top=top_y,
        width=canvas_w,
        height=canvas_h,
        accent_top=GC_GREEN,
    )

    # Dashed Inner Placeholder Box for Custom Diagram (Soft White/Grey Canvas)
    inner_dash = add_rect(
        slide,
        left=0.85,
        top=top_y + 0.35,
        width=canvas_w - 0.50,
        height=canvas_h - 0.60,
        fill_color=RGBColor(248, 249, 250),
        border_color=GC_GREEN,
        border_pt=1.5,
        rounded=True,
        dash_style=MSO_LINE_DASH_STYLE.DASH,
    )
    add_text_box(
        slide,
        left=1.20,
        top=top_y + 1.80,
        width=canvas_w - 1.20,
        height=0.50,
        text="[ ARCHITECTURE DIAGRAM CANVAS — DATA FLOW & SECURITY GOVERNANCE ]",
        font_size=13,
        bold=True,
        color=GC_GREEN,
        align=PP_ALIGN.CENTER,
    )
    add_text_box(
        slide,
        left=1.20,
        top=top_y + 2.40,
        width=canvas_w - 1.20,
        height=1.20,
        text="Paste Data Flow & Security Architecture Diagram Here\n\n(Oracle CDC Ingestion, High-Performance F35 Data Warehouse Tables, 3-Layer Semantic\nCanonicalizer, Read-Only Safety Envelopes & S1000D Verbatim Citation Pipeline)",
        font_size=11,
        italic=True,
        color=TEXT_SECONDARY,
        align=PP_ALIGN.CENTER,
    )

    # Right Architecture Annotation Sidebar
    side_x = 9.30
    side_w = 3.42
    add_card(
        slide,
        left=side_x,
        top=top_y,
        width=side_w,
        height=canvas_h,
        accent_top=GC_GREEN,
    )
    add_text_box(
        slide,
        left=side_x + 0.20,
        top=top_y + 0.15,
        width=side_w - 0.40,
        height=0.30,
        text="SECURITY & GOVERNANCE CONTROLS",
        font_size=11,
        bold=True,
        color=GC_GREEN,
    )

    callouts = [
        (
            "CONTINUOUS CDC INGESTION",
            "• Real-time change data capture\n• Zero locks on transactional ERP\n• Continuous multi-region consistency",
            GC_BLUE,
        ),
        (
            "3-LAYER CANONICALIZER",
            "• Military slang ontology resolution\n• Regex SQL dialect normalization\n• Zero-row auto-recovery logic",
            GC_GREEN,
        ),
        (
            "READ-ONLY SAFETY ENVELOPE",
            "• Strict SELECT-only whitelist\n• AST parsing prevents injections\n• Automated table partition pruning",
            GC_YELLOW,
        ),
        (
            "S1000D CITATION ANCHORING",
            "• Verbatim snippet grounding\n• Direct links to PDF publication\n• Zero hallucination guarantee",
            GC_RED,
        ),
    ]

    c_y = top_y + 0.50
    for title, desc, color in callouts:
        add_card(
            slide,
            left=side_x + 0.15,
            top=c_y,
            width=side_w - 0.30,
            height=1.05,
            bg_color=RGBColor(248, 249, 250),
            border_color=CARD_BORDER,
            accent_left=color,
        )
        add_text_box(
            slide,
            left=side_x + 0.28,
            top=c_y + 0.06,
            width=side_w - 0.45,
            height=0.22,
            text=title,
            font_size=10,
            bold=True,
            color=color,
        )
        add_text_box(
            slide,
            left=side_x + 0.28,
            top=c_y + 0.28,
            width=side_w - 0.45,
            height=0.72,
            text=desc,
            font_size=9.5,
            color=TEXT_SECONDARY,
        )
        c_y += 1.15

    add_footer(slide, slide_number=12)

    set_speaker_notes(
        slide,
        """[SPEAKER SCRIPT — 45 SECONDS]
"This slide details the data replication pipeline and semantic security controls.

The architectural challenge in defence aviation is ensuring analytical speed without risking operational transactional integrity. Our continuous change-data replication stream replicates records from Oracle into the F-35 Data Warehouse continuously without impacting frontline transactional performance.

When an engineer or executive submits a natural language query, our 3-layer semantic canonicalizer validates that the query is strictly read-only, checks against our aerospace ontology, and executes against the warehouse. All maintenance procedures are verified against official S1000D documentation, ensuring total regulatory airworthiness compliance."
""",
    )


# ==============================================================================
# Main Presentation Builder
# ==============================================================================
def generate_storytelling_deck(output_path: Path = OUTPUT_PPTX_PATH) -> Path:
    """Generate the complete 12-slide executive storytelling presentation deck."""
    print("=" * 80)
    print("Generating F-35 Fleet Sustainment Executive Storytelling Slide Deck (.pptx)...")
    print(f"Target Output Path: {output_path}")
    print("=" * 80)

    prs = Presentation()
    # 16:9 Widescreen Presentation Dimensions
    prs.slide_width = Inches(13.333333)
    prs.slide_height = Inches(7.500000)

    print("Building Slide 1: Setting the Operational Scene (Title & Hero)...")
    build_slide_1(prs)

    print("Building Slide 2: The Villain — The 06:30Z 'Oracle-to-Excel' Ritual...")
    build_slide_2(prs)

    print("Building Slide 3: The Target State — The Intelligent Action Layer...")
    build_slide_3(prs)

    print("Building Slide 4: Act 1 Live Demo — Morning Stand-Up & Shift Dispatch...")
    build_slide_4(prs)

    print("Building Slide 5: Act 2 Live Demo — Mission Protection & Briefing...")
    build_slide_5(prs)

    print("Building Slide 6: Act 3 Live Demo — Allied Fleet Memory & Defect Resolution...")
    build_slide_6(prs)

    print("Building Slide 7: Why Agents Beat Static BI Dashboards...")
    build_slide_7(prs)

    print("Building Slide 8: Semantic Governance: Military Vernacular...")
    build_slide_8(prs)

    print("Building Slide 9: Mission Impact & Next Steps...")
    build_slide_9(prs)

    print("Building Slide 10: Appendix — Technical & Architecture Deep-Dive...")
    build_slide_10(prs)

    print("Building Slide 11: Appendix — Architecture Diagram Canvas I...")
    build_slide_11(prs)

    print("Building Slide 12: Appendix — Architecture Diagram Canvas II...")
    build_slide_12(prs)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
    print(f" Successfully generated {len(prs.slides)} slides at: {output_path}")

    # Also save to legacy path so all existing scripts/tests remain valid
    if output_path != LEGACY_PPTX_PATH:
        prs.save(str(LEGACY_PPTX_PATH))
        print(f" Synced copy saved to legacy path: {LEGACY_PPTX_PATH}")

    return output_path


if __name__ == "__main__":
    generate_storytelling_deck()
