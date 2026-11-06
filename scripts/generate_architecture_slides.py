"""Generate Publication-Quality 16:9 Architecture Presentation Slides for F-35 Fleet Sustainment.

Produces two high-resolution (3072x1728, 160 DPI) executive presentation slides with
explicit line-by-line coordinate layout and zero text overlap:

1. Slide A (Higher-Level Executive Presentation Slide):
   docs/assets/f35_executive_capability_architecture_16x9_white_gcloud.png
   - Designed for Senior Defence Leadership, Commanders, and Executives.
   - Focuses on Operational Challenge vs. Intelligent AI Action Layer, 3 Mission Capability
     Pillars (Acts 1–3), Sovereign Data Foundation, and Executive Value & Governance.

2. Slide B (Updated Technical POC Architecture Slide):
   docs/assets/f35_poc_architecture_16x9_white_gcloud.png
   - Designed for Enterprise Architects, AI Engineers, and Cloud SREs.
   - Mirrors the clean 4-tier Google Cloud topology with updated OPT-01..06 latency optimizations,
     Reasoning Engine 5022570215192395776, and verified Storyboard SLAs.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_ASSETS_DIR = ROOT_DIR / "docs" / "assets"
DOCS_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# Google Cloud Clean White Executive Palette
# ==============================================================================
GC_BLUE = "#1A73E8"
GC_BLUE_DARK = "#174EA6"
GC_BLUE_FILL = "#E8F0FE"

GC_GREEN = "#1E8E3E"
GC_GREEN_DARK = "#0D652D"
GC_GREEN_FILL = "#E6F4EA"

GC_YELLOW = "#F9AB00"
GC_AMBER_DARK = "#B06000"
GC_YELLOW_FILL = "#FEF7E0"

GC_RED = "#D93025"
GC_RED_DARK = "#A50E0E"
GC_RED_FILL = "#FCE8E6"

BG_WHITE = "#FFFFFF"
BG_CONTAINER = "#F8F9FA"
BORDER_GREY = "#DADCE0"
TEXT_CHARCOAL = "#202124"
TEXT_BODY = "#3C4043"
TEXT_MUTED = "#5F6368"


def setup_canvas() -> Tuple[plt.Figure, plt.Axes]:
    """Create a 16:9 widescreen figure (3072x1728 px at 160 DPI) with top Google 4-color bar."""
    fig = plt.figure(figsize=(19.2, 10.8), dpi=160, facecolor=BG_WHITE)
    ax = fig.add_axes([0, 0, 1, 1], facecolor=BG_WHITE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Top Google Cloud 4-Color Stripe
    stripe_colors = ["#4285F4", "#EA4335", "#FBBC04", "#34A853"]
    for idx, col in enumerate(stripe_colors):
        ax.add_patch(
            Rectangle(
                (idx * 0.25, 0.992),
                0.25,
                0.008,
                facecolor=col,
                edgecolor="none",
                zorder=10,
            )
        )
    return fig, ax


def add_box(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    facecolor: str = BG_WHITE,
    edgecolor: str = BORDER_GREY,
    lw: float = 1.5,
    radius: float = 0.010,
    top_stripe_color: Optional[str] = None,
    top_stripe_h: float = 0.008,
    zorder: int = 2,
) -> None:
    """Draw a rounded rectangle container with an optional top accent bar."""
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=lw,
        zorder=zorder,
    )
    ax.add_patch(patch)

    if top_stripe_color:
        # Clean clipped top bar inside the top edge of the card
        stripe = FancyBboxPatch(
            (x + 0.001, y + h - top_stripe_h),
            w - 0.002,
            top_stripe_h,
            boxstyle=f"round,pad=0,rounding_size={min(radius * 0.5, 0.004)}",
            facecolor=top_stripe_color,
            edgecolor="none",
            zorder=zorder + 1,
        )
        ax.add_patch(stripe)


def add_arrow(
    ax: plt.Axes,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: str = GC_BLUE,
    lw: float = 2.0,
    zorder: int = 6,
) -> None:
    """Draw a clean directional connector arrow."""
    arrow = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle="-|>,head_length=7,head_width=4.5",
        color=color,
        linewidth=lw,
        zorder=zorder,
    )
    ax.add_patch(arrow)


def add_lines(
    ax: plt.Axes,
    x: float,
    start_y: float,
    lines: List[Tuple[str, float, str, str]],
    line_step: float = 0.022,
    ha: str = "left",
    zorder: int = 5,
) -> float:
    """Render a sequence of single-line text entries downward from start_y.

    Each tuple in `lines` is: (text_str, font_size, font_weight, color_hex)
    Returns the y coordinate after the last line.
    """
    curr_y = start_y
    for text_str, fsize, fweight, col in lines:
        if text_str:
            ax.text(
                x,
                curr_y,
                text_str,
                fontsize=fsize,
                fontweight=fweight,
                color=col,
                ha=ha,
                va="top",
                zorder=zorder,
            )
        curr_y -= line_step
    return curr_y


# ==============================================================================
# SLIDE A: Higher-Level Executive Presentation Slide
# ==============================================================================
def generate_executive_capability_slide(output_path: Path) -> None:
    """Render Slide A: High-Level Executive Capability & Value Architecture."""
    fig, ax = setup_canvas()

    # --------------------------------------------------------------------------
    # Header Banner (y: 0.918 -> 0.982)
    # --------------------------------------------------------------------------
    add_box(
        ax, 0.015, 0.918, 0.970, 0.064,
        facecolor=BG_CONTAINER, edgecolor=GC_BLUE, lw=1.8, radius=0.008
    )
    ax.text(
        0.028, 0.968,
        "F-35 LIGHTNING II FLEET SUSTAINMENT — EXECUTIVE CAPABILITY & VALUE ARCHITECTURE",
        fontsize=17.5, fontweight="bold", color=GC_BLUE_DARK, ha="left", va="top", zorder=5
    )
    ax.text(
        0.028, 0.938,
        "Non-Disruptive AI Action Layer Over Sovereign F-35 Enterprise Data  |  From 90-Minute Morning Stand-Up Rituals to Sub-2-Second Decisions",
        fontsize=10.5, fontweight="normal", color=TEXT_BODY, ha="left", va="top", zorder=5
    )

    # Top-Right Executive Badge Box
    add_box(
        ax, 0.795, 0.925, 0.180, 0.050,
        facecolor=BG_WHITE, edgecolor=GC_BLUE, lw=1.4, radius=0.006, zorder=4
    )
    ax.text(
        0.885, 0.962,
        "UK LIGHTNING FORCE",
        fontsize=9.5, fontweight="bold", color=GC_BLUE_DARK, ha="center", va="top", zorder=5
    )
    ax.text(
        0.885, 0.941,
        "Sovereign EU Cloud | 100% Cited",
        fontsize=8.2, fontweight="normal", color=TEXT_BODY, ha="center", va="top", zorder=5
    )

    # --------------------------------------------------------------------------
    # Left Main Canvas Sections
    # --------------------------------------------------------------------------
    left_x = 0.015
    left_w = 0.770

    # --- SECTION 1: THE TRANSFORMATION SHIFT (y: 0.745 -> 0.902) ---
    add_box(
        ax, left_x, 0.745, left_w, 0.157,
        facecolor=BG_CONTAINER, edgecolor=BORDER_GREY, lw=1.5, radius=0.010
    )
    ax.text(
        left_x + 0.014, 0.888,
        "1. STRATEGIC TRANSFORMATION — REPLACING MANUAL FRICTION WITH AN INTELLIGENT ACTION LAYER",
        fontsize=10.5, fontweight="bold", color=GC_BLUE_DARK, ha="left", va="top", zorder=5
    )

    # Left Sub-Card: The Current Bottleneck
    add_box(
        ax, 0.028, 0.757, 0.340, 0.112,
        facecolor=BG_WHITE, edgecolor=GC_RED, lw=1.4, radius=0.008, zorder=3
    )
    ax.text(
        0.038, 0.856,
        "Today's Challenge: The 06:30Z 'Oracle-to-Excel' Ritual",
        fontsize=9.6, fontweight="bold", color=GC_RED_DARK, ha="left", va="top", zorder=5
    )
    add_lines(
        ax, 0.038, 0.832,
        [
            ("• 60–90 Mins Manual Prep: Exporting CSVs across disconnected MRO tables", 8.3, "normal", TEXT_BODY),
            ("• Reactive Sortie Risk: Hours of phone/email tag to check depot spares", 8.3, "normal", TEXT_BODY),
            ("• 14-Hr Blind Teardowns: Chronic 'Could Not Duplicate' zero-code faults", 8.3, "normal", TEXT_BODY),
        ],
        line_step=0.022,
    )

    # Transformation Arrow in Center
    add_arrow(ax, 0.373, 0.813, 0.417, 0.813, color=GC_BLUE, lw=2.5)
    ax.text(
        0.395, 0.832,
        "AI Action\nLayer",
        fontsize=8.0, fontweight="bold", color=GC_BLUE_DARK, ha="center", va="bottom", zorder=5
    )

    # Right Sub-Card: The Target State
    add_box(
        ax, 0.422, 0.757, 0.350, 0.112,
        facecolor=BG_WHITE, edgecolor=GC_GREEN, lw=1.6, radius=0.008, zorder=3
    )
    ax.text(
        0.432, 0.856,
        "Target State: Sovereign Sustainment Coordinator (< 2 Secs)",
        fontsize=9.6, fontweight="bold", color=GC_GREEN_DARK, ha="left", va="top", zorder=5
    )
    add_lines(
        ax, 0.432, 0.832,
        [
            ("• Non-Disruptive Overlay: Zero lock or risk to transactional ERP/ODIN", 8.3, "normal", TEXT_BODY),
            ("• Plain-English & Military Slang: Understands 'Tails on Lizzy fit to fly'", 8.3, "normal", TEXT_BODY),
            ("• Executive Outputs: Live Spreadsheet Cards, 16:9 Slides & Cited Fixes", 8.3, "normal", TEXT_BODY),
        ],
        line_step=0.022,
    )

    # --- SECTION 2: THREE OPERATIONAL CAPABILITY PILLARS (y: 0.255 -> 0.728) ---
    add_box(
        ax, left_x, 0.255, left_w, 0.473,
        facecolor=BG_WHITE, edgecolor=GC_BLUE, lw=1.8, radius=0.012
    )
    ax.text(
        left_x + 0.014, 0.714,
        "2. THREE CORE OPERATIONAL CAPABILITIES — ALIGNED TO THE 3-ACT EXECUTIVE DEMO STORYBOARD",
        fontsize=10.5, fontweight="bold", color=GC_BLUE_DARK, ha="left", va="top", zorder=5
    )

    # Coordinator Banner inside Section 2
    add_box(
        ax, 0.028, 0.625, 0.744, 0.068,
        facecolor=GC_BLUE_FILL, edgecolor=GC_BLUE, lw=1.4, radius=0.008, zorder=3
    )
    ax.text(
        0.040, 0.680,
        "UNIFIED CONVERSATIONAL ENTRYPOINT:  Gemini Enterprise Web UI  -->  F-35 Sustainment Coordinator",
        fontsize=10.0, fontweight="bold", color=GC_BLUE_DARK, ha="left", va="top", zorder=5
    )
    ax.text(
        0.040, 0.654,
        "Empowers Squadron Commanders, Maintenance Officers, Logistics Controllers & Flight-Line Chiefs via a single natural-language interface.",
        fontsize=8.6, fontweight="normal", color=TEXT_CHARCOAL, ha="left", va="top", zorder=5
    )

    # Three Pillar Columns inside Section 2
    p_w = 0.238
    p_gap = 0.015
    p_y = 0.270
    p_h = 0.330

    # Arrows from Coordinator Banner to 3 Pillars
    add_arrow(ax, 0.180, 0.625, 0.147, 0.602, color=GC_GREEN, lw=2.0)
    add_arrow(ax, 0.400, 0.625, 0.400, 0.602, color=GC_AMBER_DARK, lw=2.0)
    add_arrow(ax, 0.620, 0.625, 0.653, 0.602, color=GC_RED, lw=2.0)

    # Pillar 1: Act 1
    p1_x = 0.028
    add_box(
        ax, p1_x, p_y, p_w, p_h,
        facecolor=BG_WHITE, edgecolor=GC_GREEN, lw=1.6, radius=0.009,
        top_stripe_color=GC_GREEN, top_stripe_h=0.010, zorder=3
    )
    ax.text(p1_x + 0.012, p_y + p_h - 0.020, "ACT 1 · 06:45Z STAND-UP", fontsize=9.2, fontweight="bold", color=GC_GREEN_DARK, va="top", zorder=5)
    ax.text(p1_x + 0.012, p_y + p_h - 0.042, "Maintenance & Shift Dispatch", fontsize=10.2, fontweight="bold", color=TEXT_CHARCOAL, va="top", zorder=5)
    ax.text(p1_x + 0.012, p_y + p_h - 0.064, "Personas: Maint Officer & Wing Controller", fontsize=8.2, fontweight="bold", color=GC_GREEN, va="top", zorder=5)

    add_lines(
        ax, p1_x + 0.012, p_y + p_h - 0.090,
        [
            ("• Instant visibility into active work orders,", 8.1, "normal", TEXT_BODY),
            ("  post-sortie BIT faults & shift readiness.", 8.1, "normal", TEXT_BODY),
            ("• Spots grounded lead jet ZM151 on", 8.1, "normal", TEXT_BODY),
            ("  dual work orders (88401 & 88402).", 8.1, "normal", TEXT_BODY),
            ("• Isolates 1,000.4h actuator breach &", 8.1, "normal", TEXT_BODY),
            ("  repeat CND canopy latch defect.", 8.1, "normal", TEXT_BODY),
            ("• Confirms bay crew, QAR inspector &", 8.1, "normal", TEXT_BODY),
            ("  spanner JTD-53-30-T14 ready to dispatch.", 8.1, "normal", TEXT_BODY),
        ],
        line_step=0.0195,
    )
    add_box(ax, p1_x + 0.010, p_y + 0.012, p_w - 0.020, 0.052, facecolor=GC_GREEN_FILL, edgecolor=GC_GREEN, lw=1.0, radius=0.006, zorder=4)
    ax.text(p1_x + p_w / 2, p_y + 0.052, "Outcome: 60 Mins -> 1.42 Seconds", fontsize=8.4, fontweight="bold", color=GC_GREEN_DARK, ha="center", va="top", zorder=5)
    ax.text(p1_x + p_w / 2, p_y + 0.031, "Live Spreadsheet Card + Auto CSV", fontsize=7.8, fontweight="normal", color=TEXT_CHARCOAL, ha="center", va="top", zorder=5)

    # Pillar 2: Act 2
    p2_x = p1_x + p_w + p_gap
    add_box(
        ax, p2_x, p_y, p_w, p_h,
        facecolor=BG_WHITE, edgecolor=GC_YELLOW, lw=1.6, radius=0.009,
        top_stripe_color=GC_YELLOW, top_stripe_h=0.010, zorder=3
    )
    ax.text(p2_x + 0.012, p_y + p_h - 0.020, "ACT 2 · 06:52Z MISSION BRIEF", fontsize=9.2, fontweight="bold", color=GC_AMBER_DARK, va="top", zorder=5)
    ax.text(p2_x + 0.012, p_y + p_h - 0.042, "Readiness & Sortie Protection", fontsize=10.2, fontweight="bold", color=TEXT_CHARCOAL, va="top", zorder=5)
    ax.text(p2_x + 0.012, p_y + p_h - 0.064, "Personas: Logistics Officer & Commander", fontsize=8.2, fontweight="bold", color=GC_AMBER_DARK, va="top", zorder=5)

    add_lines(
        ax, p2_x + 0.012, p_y + p_h - 0.090,
        [
            ("• Correlates component life limits with", 8.1, "normal", TEXT_BODY),
            ("  depot spares & active flying program.", 8.1, "normal", TEXT_BODY),
            ("• Verifies 4 spare actuators in stock", 8.1, "normal", TEXT_BODY),
            ("  at RAF Marham (18-hr road transfer).", 8.1, "normal", TEXT_BODY),
            ("• Protects 07:30Z sortie by swapping", 8.1, "normal", TEXT_BODY),
            ("  ZM151 to serviceable spare ZM154.", 8.1, "normal", TEXT_BODY),
            ("• Generates Full HD 16:9 Commander", 8.1, "normal", TEXT_BODY),
            ("  briefing slide on demand (0.78s).", 8.1, "normal", TEXT_BODY),
        ],
        line_step=0.0195,
    )
    add_box(ax, p2_x + 0.010, p_y + 0.012, p_w - 0.020, 0.052, facecolor=GC_YELLOW_FILL, edgecolor=GC_YELLOW, lw=1.0, radius=0.006, zorder=4)
    ax.text(p2_x + p_w / 2, p_y + 0.052, "Outcome: 3–4 Hrs -> 1.18 Seconds", fontsize=8.4, fontweight="bold", color=GC_AMBER_DARK, ha="center", va="top", zorder=5)
    ax.text(p2_x + p_w / 2, p_y + 0.031, "07:30Z Sortie Saved + 16:9 Slide", fontsize=7.8, fontweight="normal", color=TEXT_CHARCOAL, ha="center", va="top", zorder=5)

    # Pillar 3: Act 3
    p3_x = p2_x + p_w + p_gap
    add_box(
        ax, p3_x, p_y, p_w, p_h,
        facecolor=BG_WHITE, edgecolor=GC_RED, lw=1.6, radius=0.009,
        top_stripe_color=GC_RED, top_stripe_h=0.010, zorder=3
    )
    ax.text(p3_x + 0.012, p_y + p_h - 0.020, "ACT 3 · 06:56Z DEFECT FIX", fontsize=9.2, fontweight="bold", color=GC_RED_DARK, va="top", zorder=5)
    ax.text(p3_x + 0.012, p_y + p_h - 0.042, "Allied Fleet Memory & JTD Pubs", fontsize=10.2, fontweight="bold", color=TEXT_CHARCOAL, va="top", zorder=5)
    ax.text(p3_x + 0.012, p_y + p_h - 0.064, "Persona: Flight-Line Maintenance Chief", fontsize=8.2, fontweight="bold", color=GC_RED, va="top", zorder=5)

    add_lines(
        ax, p3_x + 0.012, p_y + p_h - 0.090,
        [
            ("• Unifies S1000D JTD manuals with 5 yrs", 8.1, "normal", TEXT_BODY),
            ("  of UK & US historical repair logs.", 8.1, "normal", TEXT_BODY),
            ("• Bridges UK/US engineering dialects", 8.1, "normal", TEXT_BODY),
            ("  (catch <-> latch, spanner <-> wrench).", 8.1, "normal", TEXT_BODY),
            ("• Matches USMC VMFA-211 cured silicon", 8.1, "normal", TEXT_BODY),
            ("  sealant debris repair log (DOC-02).", 8.1, "normal", TEXT_BODY),
            ("• Cites JTD 53-30-01 (DOC-01) 18.5 N·m", 8.1, "normal", TEXT_BODY),
            ("  torque spec for spanner JTD-53-30-T14.", 8.1, "normal", TEXT_BODY),
        ],
        line_step=0.0195,
    )
    add_box(ax, p3_x + 0.010, p_y + 0.012, p_w - 0.020, 0.052, facecolor=GC_RED_FILL, edgecolor=GC_RED, lw=1.0, radius=0.006, zorder=4)
    ax.text(p3_x + p_w / 2, p_y + 0.052, "Outcome: 14-Hr Teardown -> 0.38s", fontsize=8.4, fontweight="bold", color=GC_RED_DARK, ha="center", va="top", zorder=5)
    ax.text(p3_x + p_w / 2, p_y + 0.031, "100% Verbatim Source-Cited Repair", fontsize=7.8, fontweight="normal", color=TEXT_CHARCOAL, ha="center", va="top", zorder=5)

    # --- SECTION 3: SOVEREIGN DATA & KNOWLEDGE FOUNDATION (y: 0.020 -> 0.235) ---
    add_box(
        ax, left_x, 0.020, left_w, 0.215,
        facecolor=BG_CONTAINER, edgecolor=BORDER_GREY, lw=1.5, radius=0.010
    )
    ax.text(
        left_x + 0.014, 0.222,
        "3. SOVEREIGN ENTERPRISE DATA & COALITION KNOWLEDGE FOUNDATION (STRICT EU DATA RESIDENCY)",
        fontsize=10.5, fontweight="bold", color=GC_BLUE_DARK, ha="left", va="top", zorder=8,
        bbox=dict(boxstyle="round,pad=0.15", facecolor=BG_CONTAINER, edgecolor="none"),
    )

    # Connectors between Pillars and Data Sources
    add_arrow(ax, 0.147, 0.270, 0.147, 0.188, color=GC_GREEN, lw=2.0, zorder=4)
    add_arrow(ax, 0.400, 0.270, 0.400, 0.188, color=GC_AMBER_DARK, lw=2.0, zorder=4)
    add_arrow(ax, 0.653, 0.270, 0.653, 0.188, color=GC_RED, lw=2.0, zorder=4)

    # Foundation Box 1
    add_box(ax, p1_x, 0.034, p_w, 0.152, facecolor=BG_WHITE, edgecolor=GC_GREEN, lw=1.4, radius=0.008, zorder=3)
    ax.text(p1_x + 0.012, 0.174, "Flight-Line Operations Data (EU)", fontsize=9.2, fontweight="bold", color=GC_GREEN_DARK, va="top", zorder=5)
    add_lines(
        ax, p1_x + 0.012, 0.148,
        [
            ("• Active Maintenance Work Orders", 8.2, "normal", TEXT_BODY),
            ("• ODIN PHM / BIT Fault Telemetry Logs", 8.2, "normal", TEXT_BODY),
            ("• Work Center SQEP Crews, QARs &", 8.2, "normal", TEXT_BODY),
            ("  Calibrated Support Equipment", 8.2, "normal", TEXT_BODY),
        ],
        line_step=0.022,
    )

    # Foundation Box 2
    add_box(ax, p2_x, 0.034, p_w, 0.152, facecolor=BG_WHITE, edgecolor=GC_YELLOW, lw=1.4, radius=0.008, zorder=3)
    ax.text(p2_x + 0.012, 0.174, "Supply & Readiness Data (EU)", fontsize=9.2, fontweight="bold", color=GC_AMBER_DARK, va="top", zorder=5)
    add_lines(
        ax, p2_x + 0.012, 0.148,
        [
            ("• Airframe Component Life Telemetry", 8.2, "normal", TEXT_BODY),
            ("• Regional & Carrier Strike Group", 8.2, "normal", TEXT_BODY),
            ("  30-Day Spare Parts Inventory", 8.2, "normal", TEXT_BODY),
            ("• Active Squadron Sortie Schedules", 8.2, "normal", TEXT_BODY),
        ],
        line_step=0.022,
    )

    # Foundation Box 3
    add_box(ax, p3_x, 0.034, p_w, 0.152, facecolor=BG_WHITE, edgecolor=GC_RED, lw=1.4, radius=0.008, zorder=3)
    ax.text(p3_x + 0.012, 0.174, "Coalition Fleet Memory (eu)", fontsize=9.2, fontweight="bold", color=GC_RED_DARK, va="top", zorder=5)
    add_lines(
        ax, p3_x + 0.012, 0.148,
        [
            ("• Official S1000D Joint Technical Data", 8.2, "normal", TEXT_BODY),
            ("  (JTD) Illustrated Manuals (DOC-01/09)", 8.2, "normal", TEXT_BODY),
            ("• 5-Year Multi-Service (RAF, RN, USAF,", 8.2, "normal", TEXT_BODY),
            ("  USMC) Narrative Repair Logs (DOC-02/03)", 8.2, "normal", TEXT_BODY),
        ],
        line_step=0.022,
    )

    # --------------------------------------------------------------------------
    # Right Sidebar: Executive Value & Governance (x: 0.798 -> 0.985)
    # --------------------------------------------------------------------------
    side_x = 0.798
    side_w = 0.187
    add_box(
        ax, side_x, 0.020, side_w, 0.882,
        facecolor=BG_CONTAINER, edgecolor=BORDER_GREY, lw=1.5, radius=0.010
    )
    ax.text(
        side_x + side_w / 2, 0.886,
        "EXECUTIVE VALUE &",
        fontsize=10.2, fontweight="bold", color=GC_BLUE_DARK, ha="center", va="top", zorder=5
    )
    ax.text(
        side_x + side_w / 2, 0.865,
        "SOVEREIGN GOVERNANCE",
        fontsize=10.2, fontweight="bold", color=GC_BLUE_DARK, ha="center", va="top", zorder=5
    )

    # Sidebar Card 1: Quantified Mission Impact
    c_x = side_x + 0.010
    c_w = side_w - 0.020
    add_box(ax, c_x, 0.655, c_w, 0.192, facecolor=BG_WHITE, edgecolor=GC_BLUE, lw=1.4, radius=0.008, top_stripe_color=GC_BLUE, zorder=3)
    ax.text(c_x + 0.010, 0.830, "Quantified Mission Impact", fontsize=9.2, fontweight="bold", color=GC_BLUE_DARK, va="top", zorder=5)
    add_lines(
        ax, c_x + 0.010, 0.804,
        [
            ("• Stand-Up Prep Time:", 8.0, "normal", TEXT_BODY),
            ("  60–90 Mins -> 1.42 Seconds", 8.2, "bold", GC_GREEN_DARK),
            ("• Sortie Swap Coordination:", 8.0, "normal", TEXT_BODY),
            ("  3–4 Hours -> 1.18 Seconds", 8.2, "bold", GC_GREEN_DARK),
            ("• Zero-Code CND Defect Fix:", 8.0, "normal", TEXT_BODY),
            ("  14-Hr Teardown -> 0.38s", 8.2, "bold", GC_GREEN_DARK),
        ],
        line_step=0.022,
    )

    # Sidebar Card 2: Why Agents Beat Static BI
    add_box(ax, c_x, 0.448, c_w, 0.192, facecolor=BG_WHITE, edgecolor=GC_GREEN, lw=1.4, radius=0.008, top_stripe_color=GC_GREEN, zorder=3)
    ax.text(c_x + 0.010, 0.623, "Why Agents Beat Static BI", fontsize=9.2, fontweight="bold", color=GC_GREEN_DARK, va="top", zorder=5)
    add_lines(
        ax, c_x + 0.010, 0.597,
        [
            ("• Unifies Structured SQL +", 8.0, "normal", TEXT_BODY),
            ("  Unstructured JTD Manuals", 8.0, "normal", TEXT_BODY),
            ("• Understands Flight-Line", 8.0, "normal", TEXT_BODY),
            ("  Military Slang & Dialect", 8.0, "normal", TEXT_BODY),
            ("• Recommends Tail Swaps &", 8.0, "normal", TEXT_BODY),
            ("  Builds 16:9 Slides Live", 8.2, "bold", GC_GREEN_DARK),
        ],
        line_step=0.022,
    )

    # Sidebar Card 3: Sovereign Airworthiness
    add_box(ax, c_x, 0.241, c_w, 0.192, facecolor=BG_WHITE, edgecolor=GC_YELLOW, lw=1.4, radius=0.008, top_stripe_color=GC_YELLOW, zorder=3)
    ax.text(c_x + 0.010, 0.416, "Sovereign Airworthiness", fontsize=9.2, fontweight="bold", color=GC_AMBER_DARK, va="top", zorder=5)
    add_lines(
        ax, c_x + 0.010, 0.390,
        [
            ("• 100% Verbatim Citations to", 8.0, "normal", TEXT_BODY),
            ("  Approved S1000D Manuals", 8.0, "normal", TEXT_BODY),
            ("• Strict Read-Only Safety:", 8.0, "normal", TEXT_BODY),
            ("  Zero ERP Mutation Risk", 8.0, "normal", TEXT_BODY),
            ("• Human-in-the-Loop Sign-Off", 8.2, "bold", GC_AMBER_DARK),
            ("  on All Maintenance Actions", 8.0, "normal", TEXT_BODY),
        ],
        line_step=0.022,
    )

    # Sidebar Card 4: Sovereign EU Cloud Posture
    add_box(ax, c_x, 0.034, c_w, 0.192, facecolor=BG_WHITE, edgecolor=GC_RED, lw=1.4, radius=0.008, top_stripe_color=GC_RED, zorder=3)
    ax.text(c_x + 0.010, 0.209, "Sovereign EU Cloud Posture", fontsize=9.2, fontweight="bold", color=GC_RED_DARK, va="top", zorder=5)
    add_lines(
        ax, c_x + 0.010, 0.183,
        [
            ("• Agent Runtime & Compute:", 8.0, "normal", TEXT_BODY),
            ("  europe-west1 (Belgium)", 8.0, "bold", TEXT_CHARCOAL),
            ("• Warehouse & Search UI:", 8.0, "normal", TEXT_BODY),
            ("  EU / eu Multi-Region", 8.0, "bold", TEXT_CHARCOAL),
            ("• Full Audit Traceability", 8.2, "bold", GC_RED_DARK),
            ("  & Zero Data Egress", 8.0, "normal", TEXT_BODY),
        ],
        line_step=0.022,
    )

    plt.savefig(output_path, dpi=160, facecolor=BG_WHITE, edgecolor="none")
    plt.close(fig)
    print(f"[OK] Generated Slide A (Executive Capability Architecture): {output_path}")


# ==============================================================================
# SLIDE B: Updated Technical POC Architecture Slide
# ==============================================================================
def generate_technical_architecture_slide(output_path: Path) -> None:
    """Render Slide B: Updated Technical Deployment & Multi-Agent Architecture."""
    fig, ax = setup_canvas()

    # --------------------------------------------------------------------------
    # Header Banner (y: 0.918 -> 0.982)
    # --------------------------------------------------------------------------
    add_box(
        ax, 0.015, 0.918, 0.970, 0.064,
        facecolor=BG_CONTAINER, edgecolor=GC_BLUE, lw=1.8, radius=0.008
    )
    ax.text(
        0.028, 0.968,
        "F-35 LIGHTNING II FLEET SUSTAINMENT AGENT PLATFORM — PROOF OF CAPABILITY (POC) ARCHITECTURE",
        fontsize=17.5, fontweight="bold", color=GC_BLUE_DARK, ha="left", va="top", zorder=5
    )
    ax.text(
        0.028, 0.938,
        "Google Cloud Agent Platform | ADK 2.0 Runtime (Engine: 5022570215192395776) | Aligned to 3-Act, 6-Prompt Storyboard | Sovereign EU (europe-west1 & EU)",
        fontsize=10.2, fontweight="normal", color=TEXT_BODY, ha="left", va="top", zorder=5
    )

    # Top-Right Model Tier Pill
    add_box(
        ax, 0.805, 0.925, 0.170, 0.050,
        facecolor=BG_WHITE, edgecolor=GC_BLUE, lw=1.4, radius=0.006, zorder=4
    )
    ax.text(
        0.890, 0.962,
        "MODEL TIER: GEMINI 3.8 FLASH",
        fontsize=9.0, fontweight="bold", color=GC_BLUE_DARK, ha="center", va="top", zorder=5
    )
    ax.text(
        0.890, 0.941,
        "enterprise=True | thinking=LOW",
        fontsize=8.2, fontweight="normal", color=TEXT_BODY, ha="center", va="top", zorder=5
    )

    # --------------------------------------------------------------------------
    # Left Main Canvas Tiers (x: 0.015 -> 0.785)
    # --------------------------------------------------------------------------
    left_x = 0.015
    left_w = 0.770

    # --- TIER 1: OPERATIONAL USER & EXPERIENCE LAYER (y: 0.752 -> 0.902) ---
    add_box(
        ax, left_x, 0.752, left_w, 0.150,
        facecolor=BG_CONTAINER, edgecolor=BORDER_GREY, lw=1.5, radius=0.010
    )
    ax.text(
        left_x + 0.014, 0.888,
        "1. OPERATIONAL USER & EXPERIENCE LAYER — GEMINI ENTERPRISE (eu MULTI-REGION)",
        fontsize=10.2, fontweight="bold", color=GC_BLUE_DARK, ha="left", va="top", zorder=5
    )

    # 3 Boxes inside Tier 1
    add_box(ax, 0.028, 0.764, 0.228, 0.105, facecolor=BG_WHITE, edgecolor=BORDER_GREY, lw=1.3, radius=0.008, zorder=3)
    ax.text(0.038, 0.855, "UK Lightning Force Personas", fontsize=9.2, fontweight="bold", color=TEXT_CHARCOAL, va="top", zorder=5)
    add_lines(
        ax, 0.038, 0.830,
        [
            ("• Act 1: Sqn Maint Officer & Wing Controller", 8.0, "normal", TEXT_BODY),
            ("• Act 2: Sqn Logistics Officer & Commander", 8.0, "normal", TEXT_BODY),
            ("• Act 3: Flight-Line Maintenance Chief", 8.0, "normal", TEXT_BODY),
        ],
        line_step=0.021,
    )

    add_arrow(ax, 0.256, 0.816, 0.280, 0.816, color=GC_BLUE, lw=2.0)

    add_box(ax, 0.280, 0.764, 0.240, 0.105, facecolor=GC_BLUE_FILL, edgecolor=GC_BLUE, lw=1.5, radius=0.008, zorder=3)
    ax.text(0.290, 0.855, "Gemini Enterprise Conversation UI (eu)", fontsize=9.2, fontweight="bold", color=GC_BLUE_DARK, va="top", zorder=5)
    add_lines(
        ax, 0.290, 0.830,
        [
            ("• App: Agents (F35 Support) via ADK Native", 8.0, "normal", TEXT_CHARCOAL),
            ("• Streaming Endpoint: :streamQuery (SSE)", 8.0, "normal", TEXT_CHARCOAL),
            ("• Agent Registry: europe-west1 (Belgium)", 8.0, "normal", TEXT_CHARCOAL),
        ],
        line_step=0.021,
    )

    add_arrow(ax, 0.520, 0.816, 0.544, 0.816, color=GC_GREEN, lw=2.0)

    add_box(ax, 0.544, 0.764, 0.228, 0.105, facecolor=BG_WHITE, edgecolor=GC_GREEN, lw=1.5, radius=0.008, zorder=3)
    ax.text(0.554, 0.855, "Storyboard Output Modalities", fontsize=9.2, fontweight="bold", color=GC_GREEN_DARK, va="top", zorder=5)
    add_lines(
        ax, 0.554, 0.830,
        [
            ("• Act 1: Screen-Fitted Spreadsheet Cards", 8.0, "normal", TEXT_BODY),
            ("• Act 2: 16:9 Executive Briefing PNG Slide", 8.0, "normal", TEXT_BODY),
            ("• Act 3: 100% Verbatim Cited JTD Checklist", 8.0, "normal", TEXT_BODY),
        ],
        line_step=0.021,
    )

    # --- TIER 2: AGENTIC ORCHESTRATION LAYER (y: 0.282 -> 0.735) ---
    add_box(
        ax, left_x, 0.282, left_w, 0.453,
        facecolor=BG_CONTAINER, edgecolor=GC_BLUE, lw=1.8, radius=0.012
    )
    ax.text(
        left_x + 0.014, 0.722,
        "2. AGENTIC ORCHESTRATION LAYER — VERTEX AI AGENT RUNTIME (europe-west1)",
        fontsize=10.2, fontweight="bold", color=GC_BLUE_DARK, ha="left", va="top", zorder=5
    )
    ax.text(
        0.772, 0.722,
        "ADK 2.0: App(name='app', resumability=True, context_cache=True)",
        fontsize=8.2, fontweight="normal", color=TEXT_BODY, ha="right", va="top", zorder=5
    )

    # Arrow from Gemini Enterprise UI down to Root Coordinator
    add_arrow(ax, 0.400, 0.764, 0.400, 0.696, color=GC_BLUE, lw=2.2)

    # Root Coordinator Box (y: 0.582 -> 0.695)
    add_box(ax, 0.028, 0.582, 0.744, 0.113, facecolor=BG_WHITE, edgecolor=GC_BLUE, lw=1.6, radius=0.008, zorder=3)
    ax.text(
        0.040, 0.682,
        "ROOT COORDINATOR:  f35_sustainment_coordinator  (Gemini 3.8 Flash | thinking_level='LOW' | temp=0.0)",
        fontsize=9.8, fontweight="bold", color=GC_BLUE_DARK, va="top", zorder=5
    )
    ax.text(
        0.040, 0.656,
        "• Front-of-House Intent Router (< 450 ms routing) + Pre-Dispatched Sub-Agent & Tool Delegation (OPT-06)",
        fontsize=8.2, fontweight="normal", color=TEXT_BODY, va="top", zorder=5
    )

    # Inner Callback Banner inside Root Coordinator
    add_box(ax, 0.040, 0.592, 0.720, 0.040, facecolor=GC_BLUE_FILL, edgecolor=GC_BLUE, lw=1.0, radius=0.006, zorder=4)
    ax.text(
        0.400, 0.618,
        "before_model_callback: Tier 1 & Tier 2 Fast-Path Interception (< 5 ms, OPT-04) — Instant Greetings, 3-Pillar Capability & BI Comparison",
        fontsize=8.1, fontweight="bold", color=GC_BLUE_DARK, ha="center", va="top", zorder=5
    )

    # 3 Specialist Sub-Agents inside Tier 2 (y: 0.296 -> 0.556)
    s_w = 0.238
    s_gap = 0.015
    s_y = 0.296
    s_h = 0.260

    # Delegation Arrows from Root Coordinator to 3 Sub-Agents
    add_arrow(ax, 0.190, 0.582, 0.147, 0.556, color=GC_GREEN, lw=2.0)
    add_arrow(ax, 0.400, 0.582, 0.400, 0.556, color=GC_AMBER_DARK, lw=2.0)
    add_arrow(ax, 0.610, 0.582, 0.653, 0.556, color=GC_RED, lw=2.0)

    # Sub-Agent 1: Act 1
    s1_x = 0.028
    add_box(
        ax, s1_x, s_y, s_w, s_h,
        facecolor=BG_WHITE, edgecolor=GC_GREEN, lw=1.6, radius=0.008,
        top_stripe_color=GC_GREEN, top_stripe_h=0.009, zorder=3
    )
    ax.text(s1_x + 0.012, s_y + s_h - 0.018, "ACT 1: STAND-UP & SHIFT DISPATCH", fontsize=8.8, fontweight="bold", color=GC_GREEN_DARK, va="top", zorder=5)
    ax.text(s1_x + 0.012, s_y + s_h - 0.038, "f35_maintenance_data_agent", fontsize=9.2, fontweight="bold", color=TEXT_CHARCOAL, va="top", zorder=5)
    ax.text(s1_x + 0.012, s_y + s_h - 0.056, "@F35-Maintenance-Data (Prompts 1–3 · 1.42s)", fontsize=7.9, fontweight="bold", color=GC_GREEN, va="top", zorder=5)

    add_lines(
        ax, s1_x + 0.012, s_y + s_h - 0.078,
        [
            ("• Prompt 1 (1.42s): Urgent CSG Jobs (ZM151)", 7.8, "normal", TEXT_BODY),
            ("• Prompt 2 (1.45s): ZM151 Dual Faults & CND", 7.8, "normal", TEXT_BODY),
            ("• Prompt 3 (1.58s): Crew, QAR & Cal Tools", 7.8, "normal", TEXT_BODY),
            ("• 3-Layer Semantic SQL Canonicalizer +", 7.8, "normal", TEXT_BODY),
            ("  Deterministic Card Formatting (OPT-05)", 7.8, "normal", TEXT_BODY),
        ],
        line_step=0.019,
    )
    add_box(ax, s1_x + 0.010, s_y + 0.010, s_w - 0.020, 0.050, facecolor=GC_GREEN_FILL, edgecolor=GC_GREEN, lw=1.0, radius=0.006, zorder=4)
    ax.text(s1_x + s_w / 2, s_y + 0.049, "Tool: execute_maintenance_sql", fontsize=8.0, fontweight="bold", color=GC_GREEN_DARK, ha="center", va="top", zorder=5)
    ax.text(s1_x + s_w / 2, s_y + 0.029, "Spreadsheet Card (A..F) + Async CSV (OPT-03)", fontsize=7.5, fontweight="normal", color=TEXT_CHARCOAL, ha="center", va="top", zorder=5)

    # Sub-Agent 2: Act 2
    s2_x = s1_x + s_w + s_gap
    add_box(
        ax, s2_x, s_y, s_w, s_h,
        facecolor=BG_WHITE, edgecolor=GC_YELLOW, lw=1.6, radius=0.008,
        top_stripe_color=GC_YELLOW, top_stripe_h=0.009, zorder=3
    )
    ax.text(s2_x + 0.012, s_y + s_h - 0.018, "ACT 2: MISSION PROTECTION & BRIEF", fontsize=8.8, fontweight="bold", color=GC_AMBER_DARK, va="top", zorder=5)
    ax.text(s2_x + 0.012, s_y + s_h - 0.038, "f35_analytics_agent", fontsize=9.2, fontweight="bold", color=TEXT_CHARCOAL, va="top", zorder=5)
    ax.text(s2_x + 0.012, s_y + s_h - 0.056, "@F35-Sustainment-Analytics (1.18s / 0.78s)", fontsize=7.9, fontweight="bold", color=GC_AMBER_DARK, va="top", zorder=5)

    add_lines(
        ax, s2_x + 0.012, s_y + s_h - 0.078,
        [
            ("• Prompt 4 (1.18s): ZM151 Actuator (1,000.4h)", 7.8, "normal", TEXT_BODY),
            ("  vs 30d Spares (4 units) + Bundled Swap", 7.8, "normal", TEXT_BODY),
            ("  to ZM154 (842.0h) in Turn 1 (OPT-02)", 7.8, "normal", TEXT_BODY),
            ("• Prompt 5 (0.78s): Renders Full HD 16:9", 7.8, "normal", TEXT_BODY),
            ("  Executive Briefing Slide (chart_painter.py)", 7.8, "normal", TEXT_BODY),
        ],
        line_step=0.019,
    )
    add_box(ax, s2_x + 0.010, s_y + 0.010, s_w - 0.020, 0.050, facecolor=GC_YELLOW_FILL, edgecolor=GC_YELLOW, lw=1.0, radius=0.006, zorder=4)
    ax.text(s2_x + s_w / 2, s_y + 0.049, "Tools: check_actuator_fatigue_and_depot...", fontsize=7.8, fontweight="bold", color=GC_AMBER_DARK, ha="center", va="top", zorder=5)
    ax.text(s2_x + s_w / 2, s_y + 0.029, "recommend_tail_swap... | render_chart (16:9 PNG)", fontsize=7.4, fontweight="normal", color=TEXT_CHARCOAL, ha="center", va="top", zorder=5)

    # Sub-Agent 3: Act 3
    s3_x = s2_x + s_w + s_gap
    add_box(
        ax, s3_x, s_y, s_w, s_h,
        facecolor=BG_WHITE, edgecolor=GC_RED, lw=1.6, radius=0.008,
        top_stripe_color=GC_RED, top_stripe_h=0.009, zorder=3
    )
    ax.text(s3_x + 0.012, s_y + s_h - 0.018, "ACT 3: ALLIED FLEET MEMORY & FIX", fontsize=8.8, fontweight="bold", color=GC_RED_DARK, va="top", zorder=5)
    ax.text(s3_x + 0.012, s_y + s_h - 0.038, "f35_jtd_search_agent", fontsize=9.2, fontweight="bold", color=TEXT_CHARCOAL, va="top", zorder=5)
    ax.text(s3_x + 0.012, s_y + s_h - 0.056, "@F35-JTD-Search (Prompt 6 · 0.38s SLA)", fontsize=7.9, fontweight="bold", color=GC_RED, va="top", zorder=5)

    add_lines(
        ax, s3_x + 0.012, s_y + s_h - 0.078,
        [
            ("• Prompt 6 (0.38s): Solves ZM151 Zero-Code", 7.8, "normal", TEXT_BODY),
            ("  Canopy Handle Hesitation (No BIT Faults)", 7.8, "normal", TEXT_BODY),
            ("• Matches USMC VMFA-211 Silicon Debris Log", 7.8, "normal", TEXT_BODY),
            ("• Cites JTD 53-30-01 (18.5 N·m Torque Spec)", 7.8, "normal", TEXT_BODY),
            ("• UK/US Dialect Bridge + Parallel DE Pool", 7.8, "normal", TEXT_BODY),
        ],
        line_step=0.019,
    )
    add_box(ax, s3_x + 0.010, s_y + 0.010, s_w - 0.020, 0.050, facecolor=GC_RED_FILL, edgecolor=GC_RED, lw=1.0, radius=0.006, zorder=4)
    ax.text(s3_x + s_w / 2, s_y + 0.049, "Tool: search_technical_manuals...", fontsize=8.0, fontweight="bold", color=GC_RED_DARK, ha="center", va="top", zorder=5)
    ax.text(s3_x + s_w / 2, s_y + 0.029, "Parallel REST (pageSize=15) + 100% Citations", fontsize=7.5, fontweight="normal", color=TEXT_CHARCOAL, ha="center", va="top", zorder=5)

    # --- TIER 3: SOVEREIGN EU DATA & SEARCH LAYER (y: 0.020 -> 0.264) ---
    add_box(
        ax, left_x, 0.020, left_w, 0.244,
        facecolor=BG_CONTAINER, edgecolor=BORDER_GREY, lw=1.5, radius=0.010
    )
    ax.text(
        left_x + 0.014, 0.251,
        "3. SOVEREIGN EU DATA & SEARCH LAYER — MAPPED DIRECTLY TO STORYBOARD ACTS 1, 2 & 3 (Prompts 1–6)",
        fontsize=10.2, fontweight="bold", color=GC_BLUE_DARK, ha="left", va="top", zorder=8,
        bbox=dict(boxstyle="round,pad=0.15", facecolor=BG_CONTAINER, edgecolor="none"),
    )

    # Connectors from Sub-Agents to Tier 3 Data Stores
    add_arrow(ax, 0.140, 0.296, 0.120, 0.224, color=GC_GREEN, lw=2.0, zorder=4)
    add_arrow(ax, 0.195, 0.296, 0.430, 0.224, color=GC_BLUE, lw=1.6, zorder=4)
    add_arrow(ax, 0.350, 0.296, 0.285, 0.224, color=GC_AMBER_DARK, lw=2.0, zorder=4)
    add_arrow(ax, 0.440, 0.296, 0.475, 0.224, color=GC_BLUE, lw=1.6, zorder=4)
    add_arrow(ax, 0.653, 0.296, 0.653, 0.224, color=GC_RED, lw=2.0, zorder=4)

    # BigQuery Container (x: 0.028 -> 0.382)
    add_box(ax, 0.028, 0.032, 0.354, 0.192, facecolor=BG_WHITE, edgecolor=BORDER_GREY, lw=1.4, radius=0.008, zorder=3)
    ax.text(0.038, 0.214, "F35 Data Warehouse — BigQuery (EU Multi-Region)", fontsize=8.8, fontweight="bold", color=GC_GREEN_DARK, va="top", zorder=5)
    ax.text(0.038, 0.195, "antig-dave.ukd_f35_sustainment_demo (6 Tables × 100 Rows = 600 Live Rows)", fontsize=7.5, fontweight="normal", color=TEXT_MUTED, va="top", zorder=5)

    # BQ Sub-Box 1: Act 1 Tables
    add_box(ax, 0.036, 0.040, 0.165, 0.140, facecolor=GC_GREEN_FILL, edgecolor=GC_GREEN, lw=1.0, radius=0.006, zorder=4)
    ax.text(0.044, 0.170, "Act 1 Tables (Prompts 1–3):", fontsize=7.9, fontweight="bold", color=GC_GREEN_DARK, va="top", zorder=5)
    add_lines(
        ax, 0.044, 0.148,
        [
            ("• Prompt 1 (Urgent Stand-Up):", 7.3, "normal", TEXT_CHARCOAL),
            ("  maintenance_work_orders (100)", 7.3, "bold", TEXT_CHARCOAL),
            ("• Prompt 2 (Post-Sortie Triage):", 7.3, "normal", TEXT_CHARCOAL),
            ("  phm_bit_fault_events (100)", 7.3, "bold", TEXT_CHARCOAL),
            ("• Prompt 3 (Crews & Tool Cal):", 7.3, "normal", TEXT_CHARCOAL),
            ("  work_center_tooling_and_sqep", 7.3, "bold", TEXT_CHARCOAL),
        ],
        line_step=0.017,
    )

    # BQ Sub-Box 2: Act 2 Tables
    add_box(ax, 0.209, 0.040, 0.165, 0.140, facecolor=GC_YELLOW_FILL, edgecolor=GC_YELLOW, lw=1.0, radius=0.006, zorder=4)
    ax.text(0.217, 0.170, "Act 2 Tables (Prompt 4):", fontsize=7.9, fontweight="bold", color=GC_AMBER_DARK, va="top", zorder=5)
    add_lines(
        ax, 0.217, 0.148,
        [
            ("• Actuator Hours (ZM151/154):", 7.3, "normal", TEXT_CHARCOAL),
            ("  airframe_component_telemetry", 7.3, "bold", TEXT_CHARCOAL),
            ("• 30-Day Depot Spares Stock:", 7.3, "normal", TEXT_CHARCOAL),
            ("  global_depot_inventory (100)", 7.3, "bold", TEXT_CHARCOAL),
            ("• 07:30Z Sortie Tail Swap:", 7.3, "normal", TEXT_CHARCOAL),
            ("  squadron_sortie_schedule (100)", 7.3, "bold", TEXT_CHARCOAL),
        ],
        line_step=0.017,
    )

    # Cloud Storage Container (x: 0.394 -> 0.542)
    add_box(ax, 0.394, 0.032, 0.148, 0.192, facecolor=BG_WHITE, edgecolor=GC_BLUE, lw=1.4, radius=0.008, zorder=3)
    ax.text(0.404, 0.214, "Cloud Storage (EU)", fontsize=8.8, fontweight="bold", color=GC_BLUE_DARK, va="top", zorder=5)
    ax.text(0.404, 0.195, "europe-west1 (Belgium)", fontsize=7.5, fontweight="normal", color=TEXT_MUTED, va="top", zorder=5)
    add_lines(
        ax, 0.404, 0.172,
        [
            ("Bucket: antig-dave-f35-", 7.4, "bold", TEXT_CHARCOAL),
            ("staging-europe-west1", 7.4, "bold", TEXT_CHARCOAL),
            ("• Act 1 (Prompts 1–3):", 7.4, "normal", TEXT_BODY),
            ("  /exports/*.csv (Async)", 7.4, "normal", TEXT_BODY),
            ("• Act 2 (Prompt 5):", 7.4, "normal", TEXT_BODY),
            ("  /charts/*.png 16:9 Slide", 7.4, "normal", TEXT_BODY),
            ("• Act 3 (Prompt 6):", 7.4, "normal", TEXT_BODY),
            ("  /unstructured/docs/*.pdf", 7.4, "normal", TEXT_BODY),
        ],
        line_step=0.017,
    )

    # Discovery Engine Container (x: 0.554 -> 0.772)
    add_box(ax, 0.554, 0.032, 0.218, 0.192, facecolor=BG_WHITE, edgecolor=GC_RED, lw=1.4, radius=0.008, zorder=3)
    ax.text(0.564, 0.214, "Act 3 Search — Discovery Engine (eu)", fontsize=8.8, fontweight="bold", color=GC_RED_DARK, va="top", zorder=5)
    ax.text(0.564, 0.195, "Prompt 6: Allied Fleet Memory & JTD Manuals", fontsize=7.5, fontweight="normal", color=TEXT_MUTED, va="top", zorder=5)
    add_lines(
        ax, 0.564, 0.172,
        [
            ("1. ukd-f35-narrative-logs-ds (5-Yr Logs):", 7.5, "bold", TEXT_CHARCOAL),
            ("  • DOC-02: USMC VMFA-211 Silicon Debris", 7.4, "normal", TEXT_BODY),
            ("  • DOC-03: RAF 617 Sqn Canopy Log", 7.4, "normal", TEXT_BODY),
            ("2. ukd-f35-jtd-ietm-ds (S1000D Manuals):", 7.5, "bold", TEXT_CHARCOAL),
            ("  • DOC-01: JTD 53-30-01 (18.5 N·m Torque)", 7.4, "normal", TEXT_BODY),
            ("  • DOC-09: JTD MAM 9-1 LO Cure Rules", 7.4, "normal", TEXT_BODY),
            ("Parallel REST (pageSize=15, 100% Cited)", 7.5, "bold", GC_RED_DARK),
        ],
        line_step=0.0185,
    )

    # --------------------------------------------------------------------------
    # Right Sidebar: Google Cloud Deployment & Guardrails (x: 0.798 -> 0.985)
    # --------------------------------------------------------------------------
    side_x = 0.798
    side_w = 0.187
    add_box(
        ax, side_x, 0.020, side_w, 0.882,
        facecolor=BG_CONTAINER, edgecolor=BORDER_GREY, lw=1.5, radius=0.010
    )
    ax.text(
        side_x + side_w / 2, 0.886,
        "GOOGLE CLOUD",
        fontsize=10.2, fontweight="bold", color=GC_BLUE_DARK, ha="center", va="top", zorder=5
    )
    ax.text(
        side_x + side_w / 2, 0.865,
        "DEPLOYMENT & GUARDRAILS",
        fontsize=10.0, fontweight="bold", color=GC_BLUE_DARK, ha="center", va="top", zorder=5
    )

    c_x = side_x + 0.010
    c_w = side_w - 0.020

    # Card 1: EU Sovereignty (REG-01)
    add_box(ax, c_x, 0.672, c_w, 0.175, facecolor=BG_WHITE, edgecolor=GC_BLUE, lw=1.4, radius=0.008, top_stripe_color=GC_BLUE, zorder=3)
    ax.text(c_x + 0.010, 0.832, "EU Sovereignty (REG-01)", fontsize=9.0, fontweight="bold", color=GC_BLUE_DARK, va="top", zorder=5)
    add_lines(
        ax, c_x + 0.010, 0.806,
        [
            ("• Compute & Runtime:", 7.8, "normal", TEXT_BODY),
            ("  europe-west1 (Belgium)", 7.8, "bold", TEXT_CHARCOAL),
            ("• BigQuery Dataset:", 7.8, "normal", TEXT_BODY),
            ("  EU Multi-Region", 7.8, "bold", TEXT_CHARCOAL),
            ("• Discovery Engine & UI:", 7.8, "normal", TEXT_BODY),
            ("  eu Multi-Region", 7.8, "bold", TEXT_CHARCOAL),
        ],
        line_step=0.020,
    )

    # Card 2: Latency & OPT-01..06 Guardrails
    add_box(ax, c_x, 0.455, c_w, 0.204, facecolor=BG_WHITE, edgecolor=GC_GREEN, lw=1.4, radius=0.008, top_stripe_color=GC_GREEN, zorder=3)
    ax.text(c_x + 0.010, 0.644, "Latency & OPT-01..06", fontsize=9.0, fontweight="bold", color=GC_GREEN_DARK, va="top", zorder=5)
    add_lines(
        ax, c_x + 0.010, 0.618,
        [
            ("• OPT-01: <= 4 KB Tool Payload", 7.7, "normal", TEXT_BODY),
            ("  Slimming Callback", 7.7, "normal", TEXT_BODY),
            ("• OPT-02: Single-Turn Fatigue", 7.7, "normal", TEXT_BODY),
            ("  + Sortie Swap Bundling", 7.7, "normal", TEXT_BODY),
            ("• OPT-03: Parallel BQ/DE Pools", 7.7, "normal", TEXT_BODY),
            ("  & Async Background CSV", 7.7, "normal", TEXT_BODY),
            ("• OPT-04..06: < 5ms Fast-Path", 7.8, "bold", GC_GREEN_DARK),
        ],
        line_step=0.020,
    )

    # Card 3: IAM, SQL & ADK Safety
    add_box(ax, c_x, 0.242, c_w, 0.200, facecolor=BG_WHITE, edgecolor=GC_YELLOW, lw=1.4, radius=0.008, top_stripe_color=GC_YELLOW, zorder=3)
    ax.text(c_x + 0.010, 0.427, "IAM, SQL & ADK Safety", fontsize=9.0, fontweight="bold", color=GC_AMBER_DARK, va="top", zorder=5)
    add_lines(
        ax, c_x + 0.010, 0.401,
        [
            ("• PERF-01: In-Memory ADC", 7.7, "normal", TEXT_BODY),
            ("  Auth Cache (0 subprocess)", 7.7, "normal", TEXT_BODY),
            ("• Read-Only SQL AST Gate:", 7.7, "normal", TEXT_BODY),
            ("  Blocks DDL/DML mutations", 7.7, "normal", TEXT_BODY),
            ("• SAFE-ADK-01/02: State Duck-", 7.7, "normal", TEXT_BODY),
            ("  Typing & Prompt Safety", 7.7, "normal", TEXT_BODY),
            ("• Direct Cloud Execution", 7.8, "bold", GC_AMBER_DARK),
        ],
        line_step=0.020,
    )

    # Card 4: CI/CD & V&V Verification
    add_box(ax, c_x, 0.032, c_w, 0.197, facecolor=BG_WHITE, edgecolor=GC_RED, lw=1.4, radius=0.008, top_stripe_color=GC_RED, zorder=3)
    ax.text(c_x + 0.010, 0.214, "CI/CD & Observability", fontsize=9.0, fontweight="bold", color=GC_RED_DARK, va="top", zorder=5)
    add_lines(
        ax, c_x + 0.010, 0.188,
        [
            ("• DEPLOY-01: Clean PyPI Lock", 7.7, "normal", TEXT_BODY),
            ("  + google-agents-cli", 7.7, "normal", TEXT_BODY),
            ("• Cloud Build & Artifact", 7.7, "normal", TEXT_BODY),
            ("  Registry (europe-west1)", 7.7, "normal", TEXT_BODY),
            ("• OpenTelemetry GenAI Spans", 7.7, "normal", TEXT_BODY),
            ("  -> Cloud Trace & Logging", 7.7, "normal", TEXT_BODY),
            ("• Automated Unit/E2E/Eval", 7.8, "bold", GC_RED_DARK),
        ],
        line_step=0.020,
    )

    plt.savefig(output_path, dpi=160, facecolor=BG_WHITE, edgecolor="none")
    plt.close(fig)
    print(f"[OK] Generated Slide B (Technical POC Architecture): {output_path}")


def main() -> None:
    slide_a_path = DOCS_ASSETS_DIR / "f35_executive_capability_architecture_16x9_white_gcloud.png"
    slide_b_path = DOCS_ASSETS_DIR / "f35_poc_architecture_16x9_white_gcloud.png"

    generate_executive_capability_slide(slide_a_path)
    generate_technical_architecture_slide(slide_b_path)


if __name__ == "__main__":
    main()
