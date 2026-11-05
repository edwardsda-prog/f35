"""Generate the 5-Slide Executive Presentation Deck (.pptx) for F-35 Fleet Sustainment (Use Cases 0, 1A, 1B, and 2).

Designed for direct import into Google Slides or Microsoft PowerPoint using the Dark Tactical RAF / Defence Theme:
- Slide 1: Executive Title & Storyline Overview (Use Cases 0, 1A, 1B, and 2)
- Slide 2: Act 0 (UC0) — Morning Maintenance Stand-Up (Scenario & Outcome)
- Slide 3: Act 1A (UC1 Turn 1) — Protect the Morning Sortie (Scenario & Outcome)
- Slide 4: Act 1B (UC1 Turn 2) — On-Demand Executive Dashboard Graphic (Scenario & Outcome + Embedded Live Chart)
- Slide 5: Act 2 (UC2) — Fix the Unexplained Zero-BIT Fault (Scenario & Outcome)
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from app.config import GCS_STAGING_BUCKET
from app.tools.chart_painter import render_executive_dashboard_chart, upload_chart_to_gcs

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "app" / "assets"
DOCS_DIR = ROOT_DIR / "docs"
OUTPUT_PPTX_PATH = DOCS_DIR / "F35_Executive_Use_Cases_Deck.pptx"
DASHBOARD_PNG_PATH = DOCS_DIR / "f35_sustainment_executive_dashboard.png"
RAF_ICON_PATH = ASSETS_DIR / "f35_raf_icon_256.png"

# Dark Tactical RAF / Defence Theme Palette
BG_NAVY_DARK = RGBColor(11, 18, 33)       # #0B1221 Deep Tactical Navy
CARD_SLATE_DARK = RGBColor(20, 31, 54)    # #141F36 Elevated Card Panel
CARD_PROMPT_BG = RGBColor(15, 23, 42)     # #0F172A Prompt Terminal Box
HEADER_BAR_BG = RGBColor(16, 26, 46)      # #101A2E Top Header Strip
BORDER_SLATE = RGBColor(45, 64, 99)       # #2D4063 Subtle Card Border
ACCENT_CYAN = RGBColor(56, 189, 248)      # #38BDF8 Tactical Cyan
ACCENT_GOLD = RGBColor(250, 204, 21)      # #FACC15 RAF Command Gold
ACCENT_GREEN = RGBColor(34, 197, 94)      # #22C55E Serviceable / Success Green
ACCENT_RED = RGBColor(239, 68, 68)        # #EF4444 Red Breach / Alert
ACCENT_AMBER = RGBColor(245, 158, 11)     # #F59E0B Amber Warning
TEXT_WHITE = RGBColor(248, 250, 252)      # #F8FAFC Primary White
TEXT_MUTED = RGBColor(148, 163, 184)      # #94A3B8 Muted Slate Silver
TEXT_LIGHT_BLUE = RGBColor(186, 230, 253) # #BAE6FD Soft Sky Blue


def set_slide_background(slide: Any, color: RGBColor = BG_NAVY_DARK) -> None:
    """Fill slide background with solid dark tactical navy."""
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
    border_color: RGBColor | None = None,
    border_pt: float = 1.0,
    rounded: bool = True,
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
    else:
        shape.line.fill.background()
    if rounded and hasattr(shape, "adjustments") and len(shape.adjustments) > 0:
        shape.adjustments[0] = 0.03
    return shape


def add_text_box(
    slide: Any,
    left: float,
    top: float,
    width: float,
    height: float,
    text: str = "",
    font_size: float = 14,
    bold: bool = False,
    italic: bool = False,
    color: RGBColor = TEXT_WHITE,
    font_name: str = "Arial",
    align: PP_ALIGN = PP_ALIGN.LEFT,
) -> Any:
    """Create a text box with a single styled paragraph."""
    tx_box = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = tx_box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.05)
    tf.margin_bottom = Inches(0.05)
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


def add_header_banner(
    slide: Any,
    act_badge_text: str,
    title_text: str,
    subtitle_text: str,
    speed_badge_text: str,
) -> None:
    """Render consistent top command header bar across use-case slides."""
    # Top bar background
    add_rect(
        slide,
        left=0.0,
        top=0.0,
        width=13.333,
        height=1.15,
        fill_color=HEADER_BAR_BG,
        border_color=BORDER_SLATE,
        border_pt=1.0,
        rounded=False,
    )
    # Left RAF icon if present
    if RAF_ICON_PATH.exists():
        slide.shapes.add_picture(
            str(RAF_ICON_PATH),
            Inches(0.35),
            Inches(0.18),
            width=Inches(0.78),
            height=Inches(0.78),
        )

    # Act Badge Pill
    badge = add_rect(
        slide,
        left=1.30,
        top=0.16,
        width=2.45,
        height=0.32,
        fill_color=RGBColor(30, 58, 138),
        border_color=ACCENT_CYAN,
        border_pt=1.2,
        rounded=True,
    )
    tf = badge.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = act_badge_text
    r.font.name = "Arial"
    r.font.size = Pt(10.5)
    r.font.bold = True
    r.font.color.rgb = ACCENT_CYAN

    # Main Slide Title
    add_text_box(
        slide,
        left=3.85,
        top=0.11,
        width=6.8,
        height=0.45,
        text=title_text,
        font_size=20,
        bold=True,
        color=TEXT_WHITE,
    )

    # Subtitle line
    add_text_box(
        slide,
        left=1.30,
        top=0.56,
        width=9.3,
        height=0.45,
        text=subtitle_text,
        font_size=12.5,
        italic=True,
        color=TEXT_MUTED,
    )

    # Right Speed / SLA Pill
    sla_pill = add_rect(
        slide,
        left=10.75,
        top=0.25,
        width=2.25,
        height=0.65,
        fill_color=RGBColor(15, 41, 30),
        border_color=ACCENT_GREEN,
        border_pt=1.5,
        rounded=True,
    )
    stf = sla_pill.text_frame
    stf.word_wrap = True
    sp = stf.paragraphs[0]
    sp.alignment = PP_ALIGN.CENTER
    sr = sp.add_run()
    sr.text = speed_badge_text
    sr.font.name = "Arial"
    sr.font.size = Pt(11.5)
    sr.font.bold = True
    sr.font.color.rgb = ACCENT_GREEN


def add_footer_bar(slide: Any, page_num: int, total_pages: int = 5) -> None:
    """Add bottom sovereign EU & classification footer bar."""
    add_rect(
        slide,
        left=0.0,
        top=7.12,
        width=13.333,
        height=0.38,
        fill_color=HEADER_BAR_BG,
        border_color=BORDER_SLATE,
        border_pt=0.75,
        rounded=False,
    )
    add_text_box(
        slide,
        left=0.4,
        top=7.15,
        width=9.5,
        height=0.3,
        text="F-35 Fleet Sustainment (`F35 Support`)  |  RAF Marham (617 Sqn) & HMS Queen Elizabeth  |  100% EU Sovereign Cloud (`europe-west1` / `EU`)",
        font_size=9.5,
        color=TEXT_MUTED,
    )
    add_text_box(
        slide,
        left=11.5,
        top=7.15,
        width=1.5,
        height=0.3,
        text=f"Slide {page_num} of {total_pages}",
        font_size=9.5,
        bold=True,
        color=ACCENT_CYAN,
        align=PP_ALIGN.RIGHT,
    )


def add_bullet_list(
    slide: Any,
    left: float,
    top: float,
    width: float,
    height: float,
    items: list[tuple[str, str]],
    title_size: float = 12.5,
    body_size: float = 11.5,
    bullet_color: RGBColor = ACCENT_CYAN,
) -> Any:
    """Add structured bullet list where each item is (bold_lead, description)."""
    tx = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = tx.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.04)

    for idx, (lead, desc) in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(8)

        r_bullet = p.add_run()
        r_bullet.text = "▸ "
        r_bullet.font.name = "Arial"
        r_bullet.font.size = Pt(title_size)
        r_bullet.font.bold = True
        r_bullet.font.color.rgb = bullet_color

        r_lead = p.add_run()
        r_lead.text = f"{lead}: "
        r_lead.font.name = "Arial"
        r_lead.font.size = Pt(title_size)
        r_lead.font.bold = True
        r_lead.font.color.rgb = TEXT_WHITE

        r_desc = p.add_run()
        r_desc.text = desc
        r_desc.font.name = "Arial"
        r_desc.font.size = Pt(body_size)
        r_desc.font.color.rgb = RGBColor(215, 224, 236)

    return tx


def add_prompt_box(
    slide: Any,
    left: float,
    top: float,
    width: float,
    height: float,
    prompt_label: str,
    prompt_text: str,
    specialist_agent: str,
) -> None:
    """Render the exact copy-paste Executive Prompt terminal card on the bottom-left."""
    add_rect(
        slide,
        left=left,
        top=top,
        width=width,
        height=height,
        fill_color=CARD_PROMPT_BG,
        border_color=ACCENT_GOLD,
        border_pt=1.5,
        rounded=True,
    )
    add_text_box(
        slide,
        left=left + 0.15,
        top=top + 0.10,
        width=width - 0.30,
        height=0.32,
        text=f"💬 {prompt_label}  ({specialist_agent})",
        font_size=11.5,
        bold=True,
        color=ACCENT_GOLD,
    )
    add_text_box(
        slide,
        left=left + 0.15,
        top=top + 0.42,
        width=width - 0.30,
        height=height - 0.50,
        text=f'"{prompt_text}"',
        font_size=12.0,
        italic=True,
        color=TEXT_LIGHT_BLUE,
        font_name="Consolas",
    )


def build_slide_1_overview(prs: Presentation) -> None:
    """Slide 1: Title & Executive Use-Case Storyline Overview (0, 1A, 1B, 2)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)

    # Top Hero Banner
    add_rect(
        slide,
        left=0.45,
        top=0.40,
        width=12.43,
        height=2.15,
        fill_color=CARD_SLATE_DARK,
        border_color=ACCENT_CYAN,
        border_pt=1.5,
        rounded=True,
    )
    if RAF_ICON_PATH.exists():
        slide.shapes.add_picture(
            str(RAF_ICON_PATH),
            Inches(0.75),
            Inches(0.62),
            width=Inches(1.65),
            height=Inches(1.65),
        )

    add_text_box(
        slide,
        left=2.65,
        top=0.55,
        width=9.9,
        height=0.40,
        text="GEMINI ENTERPRISE EXECUTIVE BRIEFING  |  RAF MARHAM & HMS QUEEN ELIZABETH",
        font_size=12,
        bold=True,
        color=ACCENT_GOLD,
    )
    add_text_box(
        slide,
        left=2.65,
        top=0.95,
        width=9.9,
        height=0.65,
        text="F-35 Lightning II Fleet Sustainment (`F35 Support`)",
        font_size=28,
        bold=True,
        color=TEXT_WHITE,
    )
    add_text_box(
        slide,
        left=2.65,
        top=1.62,
        width=9.9,
        height=0.75,
        text="Compressing Hours of ODIN Backlog Triage, Sortie Logistics, Executive Charting & Technical Troubleshooting into Seconds — Use Cases 0, 1A, 1B & 2",
        font_size=14.5,
        italic=True,
        color=TEXT_LIGHT_BLUE,
    )

    # 4 Use-Case Cards Across the Middle
    cards = [
        (
            "USE CASE 0 (ACT 0)",
            "Morning Maintenance Stand-Up",
            "Squadron Maintenance Officer",
            "Conversational Text-to-SQL over live ODIN work orders. Renders an Excel / Google Sheets Card with status badges, live formulas, and 1-click CSV export.",
            "⏱️ < 1.5s  (SQL < 350ms)",
            ACCENT_CYAN,
        ),
        (
            "USE CASE 1A (ACT 1A)",
            "Protect the Morning Sortie",
            "Squadron Logistics Officer (Turn 1)",
            "Cross-checks F-35 actuator hours against 30-day depot stock. Flags ZM151 breach (1,000.4 hrs) and auto-swaps VIPER-1 sortie to spare ZM154 (842.0 hrs).",
            "⏱️ 1.2s  (TTFT 269ms)",
            ACCENT_GOLD,
        ),
        (
            "USE CASE 1B (ACT 1B)",
            "On-Demand Executive Dashboard",
            "Squadron Logistics Officer (Turn 2)",
            "Renders a publication-quality Full HD Executive Briefing Dashboard graphic comparing ZM151 vs ZM154 and regional depot spares with instant PNG download.",
            "⏱️ < 0.8s  (Chart < 790ms)",
            ACCENT_GREEN,
        ),
        (
            "USE CASE 2 (ACT 2)",
            "Fix the Unexplained Fault",
            "Flight-Line Maintenance Chief",
            "Solves a zero-BIT-fault stiff canopy handle by bridging UK/US slang across 5-year allied logs (USMC silicon debris match) + 100% cited JTD 53-30-01 specs.",
            "⏱️ 0.38s  (100% Cited)",
            ACCENT_CYAN,
        ),
    ]

    card_w = 2.95
    gap = 0.21
    start_x = 0.45
    for i, (badge, title, persona, desc, metric, col) in enumerate(cards):
        cx = start_x + i * (card_w + gap)
        add_rect(
            slide,
            left=cx,
            top=2.82,
            width=card_w,
            height=3.95,
            fill_color=CARD_SLATE_DARK,
            border_color=col,
            border_pt=1.5,
            rounded=True,
        )
        # Top badge strip
        add_rect(
            slide,
            left=cx + 0.15,
            top=3.00,
            width=card_w - 0.30,
            height=0.35,
            fill_color=CARD_PROMPT_BG,
            border_color=col,
            border_pt=1.0,
            rounded=True,
        )
        add_text_box(
            slide,
            left=cx + 0.15,
            top=3.02,
            width=card_w - 0.30,
            height=0.32,
            text=badge,
            font_size=10.5,
            bold=True,
            color=col,
            align=PP_ALIGN.CENTER,
        )
        add_text_box(
            slide,
            left=cx + 0.15,
            top=3.45,
            width=card_w - 0.30,
            height=0.60,
            text=title,
            font_size=15.5,
            bold=True,
            color=TEXT_WHITE,
        )
        add_text_box(
            slide,
            left=cx + 0.15,
            top=4.02,
            width=card_w - 0.30,
            height=0.35,
            text=f"👤 {persona}",
            font_size=11.0,
            italic=True,
            color=ACCENT_GOLD,
        )
        add_text_box(
            slide,
            left=cx + 0.15,
            top=4.42,
            width=card_w - 0.30,
            height=1.65,
            text=desc,
            font_size=11.5,
            color=RGBColor(215, 224, 236),
        )
        # Bottom metric pill
        add_rect(
            slide,
            left=cx + 0.15,
            top=6.20,
            width=card_w - 0.30,
            height=0.40,
            fill_color=RGBColor(15, 41, 30),
            border_color=ACCENT_GREEN,
            border_pt=1.0,
            rounded=True,
        )
        add_text_box(
            slide,
            left=cx + 0.15,
            top=6.23,
            width=card_w - 0.30,
            height=0.34,
            text=metric,
            font_size=11.0,
            bold=True,
            color=ACCENT_GREEN,
            align=PP_ALIGN.CENTER,
        )

    add_footer_bar(slide, page_num=1)
    slide.notes_slide.notes_text_frame.text = (
        "Speaker Notes (Slide 1 - Executive Storyline Overview):\n"
        "Every time an F-35 lands at RAF Marham or HMS Queen Elizabeth, it generates gigabytes of telemetry alongside millions of pages of manuals and maintenance logs. "
        "In this 4-step walkthrough (Use Cases 0, 1A, 1B, and 2), we follow Tail ZM151 from the 06:45Z morning maintenance stand-up through morning sortie protection, "
        "on-demand executive slide generation, and zero-BIT-fault troubleshooting on the flight line."
    )


def build_slide_2_uc0(prs: Presentation) -> None:
    """Slide 2: Use Case 0 (Act 0) — Morning Maintenance Stand-Up (Scenario & Outcome)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)

    add_header_banner(
        slide,
        act_badge_text="USE CASE 0  •  ACT 0",
        title_text="Morning Maintenance Stand-Up (Text-to-SQL & Spreadsheet Card)",
        subtitle_text="Persona: Squadron Maintenance Officer  |  Specialist Agent: @F35-Maintenance-Data  |  BigQuery EU Table: maintenance_work_orders",
        speed_badge_text="⚡ < 1.5s Total\n(SQL < 350ms)",
    )

    # Left Card: THE SCENARIO
    add_rect(
        slide,
        left=0.45,
        top=1.35,
        width=5.95,
        height=3.85,
        fill_color=CARD_SLATE_DARK,
        border_color=BORDER_SLATE,
        border_pt=1.5,
        rounded=True,
    )
    add_text_box(
        slide,
        left=0.65,
        top=1.50,
        width=5.55,
        height=0.40,
        text="🎯 THE OPERATIONAL SCENARIO (06:45Z STAND-UP)",
        font_size=14.5,
        bold=True,
        color=ACCENT_CYAN,
    )
    add_bullet_list(
        slide,
        left=0.65,
        top=1.95,
        width=5.55,
        height=3.10,
        items=[
            (
                "Multi-Squadron Backlog Review",
                "Every morning at 06:45Z, the Squadron Maintenance Officer reviews open ODIN / MOD Form 707A work orders across 617 Sqn, 207 Sqn (RAF Marham), and 809 NAS (HMS Queen Elizabeth).",
            ),
            (
                "The Manual Bottleneck",
                "Extracting Priority-1 Red-X and MICAP (Mission Capable Awaiting Parts) blockers requires logging into ODIN, exporting raw tables, and manually building Excel pivot sheets.",
            ),
            (
                "Operational Goal",
                "Instantly rank all critical open work orders by Estimated Repair Time (MTTR) in a live spreadsheet grid and export directly to Excel / Google Sheets.",
            ),
        ],
        bullet_color=ACCENT_CYAN,
    )

    # Bottom-Left Prompt Card
    add_prompt_box(
        slide,
        left=0.45,
        top=5.35,
        width=5.95,
        height=1.55,
        prompt_label="PROMPT 0 TO PASTE INTO F35 SUPPORT",
        prompt_text="Show me all open Priority-1 and MICAP maintenance work orders across RAF Marham and HMS Queen Elizabeth, sorted by estimated repair time.",
        specialist_agent="@F35-Maintenance-Data",
    )

    # Right Card: THE OUTCOME
    add_rect(
        slide,
        left=6.60,
        top=1.35,
        width=6.28,
        height=5.55,
        fill_color=CARD_SLATE_DARK,
        border_color=ACCENT_GREEN,
        border_pt=1.5,
        rounded=True,
    )
    add_text_box(
        slide,
        left=6.80,
        top=1.50,
        width=5.88,
        height=0.40,
        text="✅ THE OUTCOME & EXECUTIVE IMPACT",
        font_size=14.5,
        bold=True,
        color=ACCENT_GREEN,
    )
    add_bullet_list(
        slide,
        left=6.80,
        top=1.95,
        width=5.88,
        height=2.35,
        items=[
            (
                "Dynamic Text-to-SQL in BigQuery EU",
                "Generates a read-only SELECT query filtering Priority-1 Red-X and MICAP work orders across RAF Marham and HMS Queen Elizabeth in < 350ms.",
            ),
            (
                "Excel / Google Sheets Card with Live Formulas",
                "Renders Columns A..I with status badges (🔴 NMC-S MICAP, 🟠 NMC-M, 🟡 PMC-M) and an automated footer row (=COUNTA, =SUM man-hours, =AVERAGE MTTR).",
            ),
            (
                "1-Click Cloud Storage CSV Export & Storyline Tee-Up",
                "Provides an authenticated .CSV download link and surfaces Tail ZM151's three active tickets (WO-2026-88401 Actuator, WO-2026-88402 Canopy, WO-2026-88403 Frame 496).",
            ),
        ],
        bullet_color=ACCENT_GREEN,
    )

    # Visual Mockup of the Spreadsheet Card on Bottom Right
    sheet_box = add_rect(
        slide,
        left=6.80,
        top=4.40,
        width=5.88,
        height=2.30,
        fill_color=CARD_PROMPT_BG,
        border_color=BORDER_SLATE,
        border_pt=1.0,
        rounded=True,
    )
    add_text_box(
        slide,
        left=6.95,
        top=4.48,
        width=5.60,
        height=0.30,
        text="📊 LIVE SPREADSHEET CARD PREVIEW  |  📥 Download .CSV (Excel / Sheets)",
        font_size=10.5,
        bold=True,
        color=ACCENT_GOLD,
    )

    # Add a compact table representing the Excel card
    rows_data = [
        ["Col A: Work Order", "Col B: Tail", "Col D: Status", "Col E: Priority", "Col I: Est MTTR"],
        ["WO-2026-88408", "ZM156", "🔴 NMC-S (MICAP)", "PRIORITY_1_RED_X", "5.0 hrs"],
        ["WO-2026-88404", "ZM152", "🔴 NMC-S (MICAP)", "PRIORITY_1_RED_X", "6.0 hrs"],
        ["WO-2026-88414", "ZM162", "🔴 NMC-S (MICAP)", "PRIORITY_1_RED_X", "6.5 hrs"],
        ["WO-2026-88403", "ZM151", "🟡 PMC-M", "PRIORITY_1_RED_X", "12.0 hrs"],
        ["fx =COUNTA(5)", "617/809/207", "3 MICAP / 2 P1", "=SUM(19.2h)", "=AVG(9.2 hrs)"],
    ]
    table_shape = slide.shapes.add_table(
        len(rows_data), 5, Inches(6.92), Inches(4.82), Inches(5.64), Inches(1.75)
    )
    table = table_shape.table
    col_widths = [Inches(1.22), Inches(0.72), Inches(1.38), Inches(1.32), Inches(1.00)]
    for idx, w in enumerate(col_widths):
        table.columns[idx].width = w

    for r_idx, row in enumerate(rows_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.fill.solid()
            if r_idx == 0:
                cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
            elif r_idx == len(rows_data) - 1:
                cell.fill.fore_color.rgb = RGBColor(15, 41, 30)
            else:
                cell.fill.fore_color.rgb = RGBColor(15, 23, 42)
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            run = p.add_run()
            run.text = val
            run.font.name = "Arial"
            run.font.size = Pt(8.5)
            run.font.bold = r_idx in (0, len(rows_data) - 1)
            run.font.color.rgb = (
                ACCENT_CYAN
                if r_idx == 0
                else (ACCENT_GREEN if r_idx == len(rows_data) - 1 else TEXT_WHITE)
            )

    add_footer_bar(slide, page_num=2)
    slide.notes_slide.notes_text_frame.text = (
        "Speaker Notes (Slide 2 - Use Case 0: Morning Maintenance Stand-Up):\n"
        "Prompt 0: 'Show me all open Priority-1 and MICAP maintenance work orders across RAF Marham and HMS Queen Elizabeth, sorted by estimated repair time.'\n"
        "Outcome: @F35-Maintenance-Data queries BigQuery EU in under 350ms, renders a formatted Excel/Google Sheets card with formula summaries, "
        "and provides a direct CSV download link—immediately highlighting Tail ZM151's open tickets."
    )


def build_slide_3_uc1a(prs: Presentation) -> None:
    """Slide 3: Use Case 1A (Act 1A) — Protect the Morning Sortie (Scenario & Outcome)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)

    add_header_banner(
        slide,
        act_badge_text="USE CASE 1A  •  ACT 1A (TURN 1)",
        title_text="Protect the Morning Sortie — Fleet Readiness & Automated Tail Swap",
        subtitle_text="Persona: Squadron Logistics Officer  |  Specialist Agent: @F35-Sustainment-Analytics  |  3-Way BigQuery EU Join",
        speed_badge_text="⚡ 1.2s Total\n(TTFT 269ms)",
    )

    # Left Card: THE SCENARIO
    add_rect(
        slide,
        left=0.45,
        top=1.35,
        width=5.95,
        height=3.85,
        fill_color=CARD_SLATE_DARK,
        border_color=BORDER_SLATE,
        border_pt=1.5,
        rounded=True,
    )
    add_text_box(
        slide,
        left=0.65,
        top=1.50,
        width=5.55,
        height=0.40,
        text="🎯 THE OPERATIONAL SCENARIO (07:30Z LAUNCH WAVE)",
        font_size=14.5,
        bold=True,
        color=ACCENT_CYAN,
    )
    add_bullet_list(
        slide,
        left=0.65,
        top=1.95,
        width=5.55,
        height=3.10,
        items=[
            (
                "Imminent Morning Sortie Risk",
                "Tail ZM151 is scheduled to lead the 07:30Z training wave (Sortie SRT-MAR-20261103-01) with Flt Lt Henderson (Callsign VIPER-1).",
            ),
            (
                "Actuator Condemnation Threshold Breach",
                "Post-flight telemetry reveals ZM151's Horizontal Tail Actuator (S/N ACT-99812-F) reached 1,000.4 flight hours—breaching the mandatory 1,000.0-hour limit by +0.4 hrs.",
            ),
            (
                "Disconnected Silos Challenge",
                "Normally, reconciling component telemetry, 30-day regional depot stock, and spare aircraft availability takes 2–4 hours of manual cross-checking across separate systems.",
            ),
        ],
        bullet_color=ACCENT_CYAN,
    )

    # Bottom-Left Prompt Card (Amended: "with visual charts" removed!)
    add_prompt_box(
        slide,
        left=0.45,
        top=5.35,
        width=5.95,
        height=1.55,
        prompt_label="PROMPT 1A TO PASTE INTO F35 SUPPORT",
        prompt_text="Check RAF Marham F-35A horizontal tail actuator hours against our 30-day depot stock, and recommend a tail swap for morning sortie SRT-MAR-20261103-01.",
        specialist_agent="@F35-Sustainment-Analytics",
    )

    # Right Card: THE OUTCOME
    add_rect(
        slide,
        left=6.60,
        top=1.35,
        width=6.28,
        height=5.55,
        fill_color=CARD_SLATE_DARK,
        border_color=ACCENT_GREEN,
        border_pt=1.5,
        rounded=True,
    )
    add_text_box(
        slide,
        left=6.80,
        top=1.50,
        width=5.88,
        height=0.40,
        text="✅ THE OUTCOME & EXECUTIVE IMPACT",
        font_size=14.5,
        bold=True,
        color=ACCENT_GREEN,
    )
    add_bullet_list(
        slide,
        left=6.80,
        top=1.95,
        width=5.88,
        height=2.45,
        items=[
            (
                "3-Table BigQuery EU Join in 1.2 Seconds",
                "Simultaneously joins airframe_component_telemetry, global_depot_inventory, and squadron_sortie_schedule in EU.",
            ),
            (
                "Zero Mission Cancellation (Automated Tail Swap)",
                "Grounds ZM151 (1,000.4 hrs, PMC-M) and reallocates Flt Lt Henderson (VIPER-1) to serviceable Spare Tail ZM154 (S/N ACT-88401-B at 842.0 hrs, 158.0 hrs remaining, MC).",
            ),
            (
                "Automated Supply Requisition & On-Demand Chart Prompt",
                "Confirms 4 serviceable actuators on hand at RAF Marham (DEPOT-MAR-01) vs 2 reserved (18-hr shipping ETA) for NSN 1680-01-619-4821, then offers on-demand presentation charts.",
            ),
        ],
        bullet_color=ACCENT_GREEN,
    )

    # Readiness Decision Summary Table on Bottom Right
    card_box = add_rect(
        slide,
        left=6.80,
        top=4.48,
        width=5.88,
        height=2.22,
        fill_color=CARD_PROMPT_BG,
        border_color=BORDER_SLATE,
        border_pt=1.0,
        rounded=True,
    )
    add_text_box(
        slide,
        left=6.95,
        top=4.55,
        width=5.60,
        height=0.30,
        text="✈️ LIVE SORTIE & SUPPLY DISPOSITION SUMMARY (SRT-MAR-20261103-01)",
        font_size=10.5,
        bold=True,
        color=ACCENT_GOLD,
    )

    u1_rows = [
        ["Asset / Depot", "Serial / NSN", "Hours / Stock", "Limit / Demand", "Disposition"],
        ["Primary: ZM151", "ACT-99812-F", "1,000.4 hrs", "1,000.0 hrs", "🔴 GROUND (PMC-M Breach)"],
        ["Spare: ZM154", "ACT-88401-B", "842.0 hrs", "1,000.0 hrs", "🟢 ASSIGN VIPER-1 (MC)"],
        ["RAF Marham Hub", "1680-01-619-4821", "4 On-Hand", "2 Reserved (30d)", "📦 Pull 1 Spare (18h ETA)"],
    ]
    t_shape = slide.shapes.add_table(
        len(u1_rows), 5, Inches(6.92), Inches(4.90), Inches(5.64), Inches(1.65)
    )
    t_tbl = t_shape.table
    u1_widths = [Inches(1.15), Inches(1.18), Inches(0.95), Inches(1.05), Inches(1.31)]
    for idx, w in enumerate(u1_widths):
        t_tbl.columns[idx].width = w

    for r_idx, row in enumerate(u1_rows):
        for c_idx, val in enumerate(row):
            cell = t_tbl.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = (
                RGBColor(30, 41, 59) if r_idx == 0 else RGBColor(15, 23, 42)
            )
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = val
            run.font.name = "Arial"
            run.font.size = Pt(8.5)
            run.font.bold = r_idx == 0 or c_idx in (0, 4)
            if r_idx == 0:
                run.font.color.rgb = ACCENT_CYAN
            elif "🔴" in val:
                run.font.color.rgb = ACCENT_RED
            elif "🟢" in val:
                run.font.color.rgb = ACCENT_GREEN
            else:
                run.font.color.rgb = TEXT_WHITE

    add_footer_bar(slide, page_num=3)
    slide.notes_slide.notes_text_frame.text = (
        "Speaker Notes (Slide 3 - Use Case 1A: Protect the Morning Sortie):\n"
        "Prompt 1A: 'Check RAF Marham F-35A horizontal tail actuator hours against our 30-day depot stock, and recommend a tail swap for morning sortie SRT-MAR-20261103-01.'\n"
        "Outcome: In 1.2 seconds, @F35-Sustainment-Analytics flags ZM151's +0.4 hr actuator breach, confirms 4 spares at RAF Marham depot, "
        "swaps Flt Lt Henderson to ZM154 (842.0 hrs), and asks if the officer wants to render the Executive Briefing Dashboard."
    )


def build_slide_4_uc1b(prs: Presentation, dashboard_png_path: Path) -> None:
    """Slide 4: Use Case 1B (Act 1B) — On-Demand Executive Dashboard Graphic (Scenario & Outcome)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)

    add_header_banner(
        slide,
        act_badge_text="USE CASE 1B  •  ACT 1B (TURN 2)",
        title_text="On-Demand Slide Graphic Rendering (Executive Briefing Dashboard)",
        subtitle_text="Persona: Squadron Logistics Officer  |  Tool: render_sustainment_chart  |  Headless Matplotlib + GCS Export",
        speed_badge_text="⚡ < 0.8s Total\n(Chart < 790ms)",
    )

    # Left Card: THE SCENARIO
    add_rect(
        slide,
        left=0.45,
        top=1.35,
        width=5.95,
        height=3.85,
        fill_color=CARD_SLATE_DARK,
        border_color=BORDER_SLATE,
        border_pt=1.5,
        rounded=True,
    )
    add_text_box(
        slide,
        left=0.65,
        top=1.50,
        width=5.55,
        height=0.40,
        text="🎯 THE OPERATIONAL SCENARIO (COMMAND BRIEFING DECK)",
        font_size=14.5,
        bold=True,
        color=ACCENT_CYAN,
    )
    add_bullet_list(
        slide,
        left=0.65,
        top=1.95,
        width=5.55,
        height=3.10,
        items=[
            (
                "Instant Visual Evidence for Wing Commander",
                "Following the Turn 1 tail-swap decision, the Squadron Logistics Officer needs a publication-quality visual chart for the Wing Commander's morning briefing deck.",
            ),
            (
                "Two-Turn Decoupled Architecture",
                "Generating heavy visuals on every query slows down text responses. By decoupling tabular analysis (Turn 1) from on-demand chart rendering (Turn 2), Turn 1 stays sub-second.",
            ),
            (
                "Zero Raw JSON / Instant Slide Asset",
                "Instead of dumping raw Vega-Lite JSON code blocks, the officer requests the full Executive Briefing Dashboard ready to drop into Google Slides or PowerPoint.",
            ),
        ],
        bullet_color=ACCENT_CYAN,
    )

    # Bottom-Left Prompt Card (Amended: "16:9" removed!)
    add_prompt_box(
        slide,
        left=0.45,
        top=5.35,
        width=5.95,
        height=1.55,
        prompt_label="PROMPT 1B TO PASTE INTO F35 SUPPORT",
        prompt_text="Render the full Executive Briefing Dashboard for my presentation slide deck.",
        specialist_agent="@F35-Sustainment-Analytics",
    )

    # Right Card: THE OUTCOME + EMBEDDED LIVE CHART
    add_rect(
        slide,
        left=6.60,
        top=1.35,
        width=6.28,
        height=5.55,
        fill_color=CARD_SLATE_DARK,
        border_color=ACCENT_GREEN,
        border_pt=1.5,
        rounded=True,
    )
    add_text_box(
        slide,
        left=6.80,
        top=1.50,
        width=5.88,
        height=0.40,
        text="✅ THE OUTCOME: LIVE EXECUTIVE BRIEFING DASHBOARD",
        font_size=14.5,
        bold=True,
        color=ACCENT_GREEN,
    )
    add_bullet_list(
        slide,
        left=6.80,
        top=1.92,
        width=5.88,
        height=1.45,
        items=[
            (
                "Sub-Second Chart Painter (< 790ms)",
                "Invokes render_sustainment_chart in memory using cached Turn 1 BigQuery metrics and uploads the high-res PNG to EU Cloud Storage.",
            ),
            (
                "Dual-Panel Executive Visual + 1-Click PNG Link",
                "Left panel shows ZM151 in Red (1,000.4h breach) vs ZM154 in Green (842.0h swap); Right panel shows RAF Marham & HMS Queen Elizabeth stock vs 30-day demand.",
            ),
        ],
        title_size=11.5,
        body_size=11.0,
        bullet_color=ACCENT_GREEN,
    )

    # Embed the actual rendered Executive Dashboard PNG image!
    if dashboard_png_path.exists():
        slide.shapes.add_picture(
            str(dashboard_png_path),
            Inches(6.82),
            Inches(3.45),
            width=Inches(5.84),
        )

    add_footer_bar(slide, page_num=4)
    slide.notes_slide.notes_text_frame.text = (
        "Speaker Notes (Slide 4 - Use Case 1B: On-Demand Slide Graphic Rendering):\n"
        "Prompt 1B: 'Render the full Executive Briefing Dashboard for my presentation slide deck.'\n"
        "Outcome: The agent invokes render_sustainment_chart, rendering the high-resolution composite slide graphic in under 790ms "
        "and returning an inline preview plus a clickable PNG download link for immediate insertion into executive slide decks."
    )


def build_slide_5_uc2(prs: Presentation) -> None:
    """Slide 5: Use Case 2 (Act 2) — Fix the Unexplained Fault (Scenario & Outcome)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)

    add_header_banner(
        slide,
        act_badge_text="USE CASE 2  •  ACT 2",
        title_text="Empower Maintainers — Solving the 'Zero-BIT-Fault' Mystery",
        subtitle_text="Persona: Flight-Line Maintenance Chief  |  Specialist Agent: @F35-JTD-Search  |  Discovery Engine EU (Single-Pass)",
        speed_badge_text="⚡ 0.38s Search\n(100% Cited)",
    )

    # Left Card: THE SCENARIO
    add_rect(
        slide,
        left=0.45,
        top=1.35,
        width=5.95,
        height=3.85,
        fill_color=CARD_SLATE_DARK,
        border_color=BORDER_SLATE,
        border_pt=1.5,
        rounded=True,
    )
    add_text_box(
        slide,
        left=0.65,
        top=1.50,
        width=5.55,
        height=0.40,
        text="🎯 THE OPERATIONAL SCENARIO (FLIGHT-LINE TROUBLESHOOTING)",
        font_size=14.5,
        bold=True,
        color=ACCENT_CYAN,
    )
    add_bullet_list(
        slide,
        left=0.65,
        top=1.95,
        width=5.55,
        height=3.10,
        items=[
            (
                "Mechanical Binding with Zero Computer Faults",
                "A night-sortie pilot on ZM151 reports a stiff canopy release handle that hesitated to latch—but the onboard Built-In Test (BIT) logged zero fault codes.",
            ),
            (
                "The Coalition Dialect Blind Spot",
                "Traditional keyword search fails because UK RAF maintainers search for 'catch / spanner / binding' while the historical fix was logged by a USMC squadron using 'latch / wrench / stiff'.",
            ),
            (
                "Risk of Unnecessary Teardown",
                "Without cross-fleet memory, technicians waste 4–8 hours tearing down the canopy actuator rigging instead of inspecting the roller track.",
            ),
        ],
        bullet_color=ACCENT_CYAN,
    )

    # Bottom-Left Prompt Card
    add_prompt_box(
        slide,
        left=0.45,
        top=5.35,
        width=5.95,
        height=1.55,
        prompt_label="PROMPT 2 TO PASTE INTO F35 SUPPORT",
        prompt_text="Our night-sortie pilot reported a stiff canopy release handle that hesitated to latch, with zero BIT faults. Have allied squadrons seen this, and what is the JTD fix?",
        specialist_agent="@F35-JTD-Search",
    )

    # Right Card: THE OUTCOME
    add_rect(
        slide,
        left=6.60,
        top=1.35,
        width=6.28,
        height=5.55,
        fill_color=CARD_SLATE_DARK,
        border_color=ACCENT_GREEN,
        border_pt=1.5,
        rounded=True,
    )
    add_text_box(
        slide,
        left=6.80,
        top=1.50,
        width=5.88,
        height=0.40,
        text="✅ THE OUTCOME & EXECUTIVE IMPACT",
        font_size=14.5,
        bold=True,
        color=ACCENT_GREEN,
    )
    add_bullet_list(
        slide,
        left=6.80,
        top=1.95,
        width=5.88,
        height=2.40,
        items=[
            (
                "Coalition Terminology Bridge (0.38 Seconds)",
                "Automatically normalizes UK/US maintenance slang (catch ↔ latch, spanner ↔ wrench, binding ↔ stiff) across 5 years of RAF, RN, USAF, and USMC logs.",
            ),
            (
                "Pinpoints Sister-Squadron Root Cause (DOC-02)",
                "Matches a USMC VMFA-211 narrative log identifying cured silicon sealant debris wedged in the forward canopy roller track.",
            ),
            (
                "100% Grounded Repair Checklist (DOC-01)",
                "Anchors every torque and clearance spec to S1000D JTD Section 53-30-01 with clickable browser PDF links—eliminating 4–8 hours of teardown.",
            ),
        ],
        bullet_color=ACCENT_GREEN,
    )

    # Bottom-Right Grounded Checklist Card
    add_rect(
        slide,
        left=6.80,
        top=4.45,
        width=5.88,
        height=2.25,
        fill_color=CARD_PROMPT_BG,
        border_color=ACCENT_CYAN,
        border_pt=1.2,
        rounded=True,
    )
    add_text_box(
        slide,
        left=6.95,
        top=4.53,
        width=5.60,
        height=0.32,
        text="📑 VERBATIM GROUNDED CHECKLIST & CITATIONS (ZERO HALLUCINATION)",
        font_size=10.5,
        bold=True,
        color=ACCENT_GOLD,
    )
    add_bullet_list(
        slide,
        left=6.95,
        top=4.88,
        width=5.60,
        height=1.75,
        items=[
            (
                "[DOC-02] 5-Year Allied Narrative Log (USMC VMFA-211)",
                "Root Cause: Cured Fluorosilicone / silicon sealant debris obstructing forward canopy locking roller track (bit_fault_associated = false).",
            ),
            (
                "[DOC-01] S1000D JTD Section 53-30-01 (Canopy Rigging)",
                "Step 1: Verify roller-to-track clearance (0.020–0.035 in) with feeler gauge.\nStep 2: Purge foreign sealant debris & apply AeroShell Grease 22.\nStep 3: Torque canopy forward locking catch pivot bolt to 18.5 N·m.",
            ),
        ],
        title_size=10.5,
        body_size=10.0,
        bullet_color=ACCENT_CYAN,
    )

    add_footer_bar(slide, page_num=5)
    slide.notes_slide.notes_text_frame.text = (
        "Speaker Notes (Slide 5 - Use Case 2: Fix the Unexplained Fault):\n"
        "Prompt 2: 'Our night-sortie pilot reported a stiff canopy release handle that hesitated to latch, with zero BIT faults. Have allied squadrons seen this, and what is the JTD fix?'\n"
        "Outcome: @F35-JTD-Search bridges UK/US terminology across 5 years of coalition logs in 0.38s, finds the USMC silicon sealant debris match (DOC-02), "
        "and outputs a 100% cited repair checklist from JTD Section 53-30-01 (DOC-01) with exact clearances (0.020-0.035 in) and torque (18.5 N·m)."
    )


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Render the fresh Executive Briefing Dashboard PNG image for Slide 4
    dash_bytes = render_executive_dashboard_chart()
    DASHBOARD_PNG_PATH.write_bytes(dash_bytes)
    print(f"Saved dashboard chart PNG: {DASHBOARD_PNG_PATH} ({len(dash_bytes):,} bytes)")

    # 2. Build 16:9 Widescreen Presentation
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    build_slide_1_overview(prs)
    build_slide_2_uc0(prs)
    build_slide_3_uc1a(prs)
    build_slide_4_uc1b(prs, DASHBOARD_PNG_PATH)
    build_slide_5_uc2(prs)

    prs.save(str(OUTPUT_PPTX_PATH))
    print(f"Saved editable Google Slides deck (.pptx): {OUTPUT_PPTX_PATH} ({OUTPUT_PPTX_PATH.stat().st_size:,} bytes)")

    # 3. Upload the .pptx to GCS staging bucket so the user also has a 1-click browser download link
    try:
        from app.clients import get_storage_client

        client = get_storage_client()
        if client is not None:
            bucket = client.bucket(GCS_STAGING_BUCKET)
            blob_path = "slides/F35_Executive_Use_Cases_Deck.pptx"
            blob = bucket.blob(blob_path)
            blob.upload_from_filename(
                str(OUTPUT_PPTX_PATH),
                content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )
            print(f"Uploaded deck to: https://storage.cloud.google.com/{GCS_STAGING_BUCKET}/{blob_path}")
    except Exception as exc:
        print(f"GCS upload note: {exc}")


if __name__ == "__main__":
    main()
