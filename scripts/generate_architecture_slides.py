"""Generate Publication-Quality 16:9 Architecture Presentation Slides for F-35 Fleet Sustainment.

Produces two high-resolution (3072x1728, 160 DPI) executive presentation slides:
1. Slide A (Higher-Level Executive Briefing):
   docs/assets/f35_executive_capability_architecture_16x9_white_gcloud.png
   - Strategic Capability & Value Architecture for Air Chiefs, CSG Commanders & Senior Leadership.
   - Non-disruptive AI Action Layer, 3 Operational Pillars, Before vs. After ROI Matrix.

2. Slide B (Updated Technical Deployment Architecture):
   docs/assets/f35_poc_architecture_16x9_white_gcloud.png
   - Multi-Agent Orchestration Topology (ADK 2.0 on Vertex AI Agent Runtime europe-west1).
   - Gemini 3.8 Flash, Tier 1/2 Fast-Path Interception, OPT-01..06 Latency Optimizations.
   - Sovereign EU Data Layer (BigQuery EU, Discovery Engine eu, Cloud Storage europe-west1).
"""

from __future__ import annotations

import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_ASSETS_DIR = ROOT_DIR / "docs" / "assets"
DOCS_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Google Cloud Executive Palette
GC_BLUE = "#1A73E8"
GC_GREEN = "#1E8E3E"
GC_AMBER = "#B06000"
GC_AMBER_LIGHT = "#FEF7E0"
GC_RED = "#D93025"
GC_NAVY = "#174EA6"

BG_WHITE = "#FFFFFF"
BG_SURFACE = "#F8F9FA"
BG_CARD = "#FFFFFF"
BORDER_SUBTLE = "#DADCE0"
BORDER_DARK = "#BDC1C6"

TEXT_PRIMARY = "#202124"
TEXT_SECONDARY = "#3C4043"
TEXT_MUTED = "#5F6368"
TEXT_WHITE = "#FFFFFF"

PILL_BLUE_BG = "#E8F0FE"
PILL_GREEN_BG = "#E6F4EA"
PILL_RED_BG = "#FCE8E6"
PILL_AMBER_BG = "#FEF7E0"


def draw_card(
    ax,
    x, y, w, h,
    bg_color=BG_CARD,
    border_color=BORDER_SUBTLE,
    border_width=1.2,
    corner_radius=0.015,
    accent_bar_color=None,
    accent_bar_height=0.008,
):
    """Draw a styled executive card with optional top accent stripe."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={corner_radius}",
        facecolor=bg_color,
        edgecolor=border_color,
        linewidth=border_width,
        zorder=2,
    )
    ax.add_patch(box)

    if accent_bar_color:
        accent = FancyBboxPatch(
            (x, y + h - accent_bar_height), w, accent_bar_height,
            boxstyle=f"round,pad=0,rounding_size={corner_radius * 0.8}",
            facecolor=accent_bar_color,
            edgecolor="none",
            zorder=3,
        )
        ax.add_patch(accent)


def draw_badge(ax, x, y, text, bg_color, text_color, font_size=10, pad_x=0.012, pad_y=0.008, bold=True):
    """Draw a compact pill badge with centered text."""
    ax.text(
        x, y, text,
        fontsize=font_size,
        fontweight="bold" if bold else "normal",
        color=text_color,
        ha="center", va="center",
        bbox=dict(
            boxstyle=f"round,pad={pad_y*50}",
            facecolor=bg_color,
            edgecolor="none",
            linewidth=0,
        ),
        zorder=4,
    )


def generate_executive_capability_slide(output_path: Path):
    """Generate Slide A: High-Level Executive Capability & Value Architecture."""
    fig = plt.figure(figsize=(19.2, 10.8), dpi=160, facecolor=BG_WHITE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # 1. Header Banner
    ax.text(
        0.04, 0.945,
        "F-35 LIGHTNING II FLEET SUSTAINMENT AGENT PLATFORM",
        fontsize=24, fontweight="bold", color=GC_NAVY, ha="left", va="top"
    )
    ax.text(
        0.04, 0.910,
        "Executive Architecture Briefing · Non-Disruptive AI Action Layer Over F-35 Enterprise Data & Allied Fleet Memory",
        fontsize=13.5, color=TEXT_SECONDARY, ha="left", va="top"
    )

    # Top Badges (Right side)
    draw_badge(ax, 0.72, 0.930, "UK LIGHTNING FORCE", PILL_BLUE_BG, GC_NAVY, font_size=10.5)
    draw_badge(ax, 0.84, 0.930, "CARRIER STRIKE GROUP", PILL_GREEN_BG, GC_GREEN, font_size=10.5)
    draw_badge(ax, 0.94, 0.930, "SOVEREIGN DEFENCE AI", PILL_AMBER_BG, GC_AMBER, font_size=10.5)

    # Separator Line
    ax.plot([0.04, 0.96], [0.880, 0.880], color=BORDER_SUBTLE, lw=1.5)

    # 2. Executive Problem Statement & Value Proposition Strip
    draw_card(ax, 0.04, 0.795, 0.92, 0.070, bg_color=BG_SURFACE, border_color=BORDER_SUBTLE)
    ax.text(
        0.055, 0.845,
        "STRATEGIC IMPERATIVE & OPERATIONAL CHALLENGE",
        fontsize=10.5, fontweight="bold", color=GC_BLUE, ha="left", va="center"
    )
    ax.text(
        0.055, 0.818,
        "Traditional defence sustainment relies on 06:30Z manual 'Oracle-to-Excel' rituals, fragmented supply email chains, and 14-hour blind component teardowns for zero-code faults.\n"
        "This platform deploys a non-disruptive, read-only AI Action Layer that converts hours of administrative friction into sub-second, airworthiness-compliant operational action.",
        fontsize=10.5, color=TEXT_PRIMARY, ha="left", va="center", linespacing=1.25
    )

    # 3. Three Core Capability Pillars (Three Columns)
    col_w = 0.293
    col_gap = 0.020
    col_y = 0.295
    col_h = 0.480

    # ---------------- Pillar 1 ----------------
    x1 = 0.04
    draw_card(ax, x1, col_y, col_w, col_h, bg_color=BG_CARD, border_color=BORDER_SUBTLE, accent_bar_color=GC_BLUE)
    draw_badge(ax, x1 + 0.065, col_y + col_h - 0.030, "ACT 1 · 06:45Z", PILL_BLUE_BG, GC_NAVY, font_size=9.5)
    ax.text(
        x1 + 0.015, col_y + col_h - 0.060,
        "Conversational Maintenance &\nShift Resource Management",
        fontsize=15, fontweight="bold", color=GC_NAVY, ha="left", va="top"
    )

    p1_text = (
        "CORE OPERATIONAL PURPOSE:\n"
        "Provides engineering officers and line controllers with instant, natural-language "
        "visibility across active maintenance work orders, post-sortie health/BIT fault logs, "
        "and shift personnel/tooling readiness.\n\n"
        "KEY CAPABILITIES IN ACTION:\n"
        "• Autonomous Text-to-SQL over 300 active maintenance records\n"
        "• 3-Layer Semantic Ontology mapping military slang ('cab', 'snags')\n"
        "• Identifies lead jet ZM151 dual-fault (actuator & canopy latch)\n"
        "• Verifies bay crew, QAR inspector & calibrated spanner JTD-53-30-T14\n"
        "• Generates screen-fitted Excel/Sheets card with automatic CSV export\n\n"
        "MEASURED OPERATIONAL IMPACT:\n"
        "Cuts daily stand-up preparation and shift dispatch verification from over an hour "
        "to 1.42s live flight-line visibility."
    )
    ax.text(
        x1 + 0.015, col_y + col_h - 0.125,
        p1_text, fontsize=9.8, color=TEXT_SECONDARY, ha="left", va="top", linespacing=1.35
    )

    # ---------------- Pillar 2 ----------------
    x2 = x1 + col_w + col_gap
    draw_card(ax, x2, col_y, col_w, col_h, bg_color=BG_CARD, border_color=BORDER_SUBTLE, accent_bar_color=GC_GREEN)
    draw_badge(ax, x2 + 0.065, col_y + col_h - 0.030, "ACT 2 · 06:52Z", PILL_GREEN_BG, GC_GREEN, font_size=9.5)
    ax.text(
        x2 + 0.015, col_y + col_h - 0.060,
        "Predictive Fleet Readiness &\nMission Sortie Protection",
        fontsize=15, fontweight="bold", color=GC_GREEN, ha="left", va="top"
    )

    p2_text = (
        "CORE OPERATIONAL PURPOSE:\n"
        "Continuously correlates airframe life limits against regional/afloat spare parts "
        "and the active flying program—flagging impending expirations, staging supply "
        "requisitions, and recommending serviceable tail swaps.\n\n"
        "KEY CAPABILITIES IN ACTION:\n"
        "• Correlates actuator telemetry (ZM151 at 1,000.4h vs 1,000.0h limit)\n"
        "• Queries global depot inventory (verifies 4 spares at RAF Marham, 18h ETA)\n"
        "• Automatically protects 07:30Z combat sortie SRT-MAR-20261103-01\n"
        "• Recommends tail swap to clean spare ZM154 (842.0 flight hours)\n"
        "• Synthesizes publication-grade 16:9 executive briefing graphic\n\n"
        "MEASURED OPERATIONAL IMPACT:\n"
        "Prevents last-minute sortie aborts by compressing hours of cross-branch supply "
        "and flight-line coordination into 1.18s."
    )
    ax.text(
        x2 + 0.015, col_y + col_h - 0.125,
        p2_text, fontsize=9.8, color=TEXT_SECONDARY, ha="left", va="top", linespacing=1.35
    )

    # ---------------- Pillar 3 ----------------
    x3 = x2 + col_w + col_gap
    draw_card(ax, x3, col_y, col_w, col_h, bg_color=BG_CARD, border_color=BORDER_SUBTLE, accent_bar_color=GC_AMBER)
    draw_badge(ax, x3 + 0.065, col_y + col_h - 0.030, "ACT 3 · 06:56Z", PILL_AMBER_BG, GC_AMBER, font_size=9.5)
    ax.text(
        x3 + 0.015, col_y + col_h - 0.060,
        "Allied Fleet Collective Memory &\nGrounded Technical Guidance",
        fontsize=15, fontweight="bold", color=GC_AMBER, ha="left", va="top"
    )

    p3_text = (
        "CORE OPERATIONAL PURPOSE:\n"
        "Unifies authoritative Joint Technical Data (JTD) manuals with 5 years of multi-service "
        "(UK and US) maintenance narrative logs, bridging regional terminology to surface "
        "proven troubleshooting procedures for uncoded defects.\n\n"
        "KEY CAPABILITIES IN ACTION:\n"
        "• Diagnoses ZM151 zero-diagnostic repeat CND canopy latch defect\n"
        "• Bridges UK/US dialects (spanner ↔ wrench, catch ↔ latch, binding ↔ stiff)\n"
        "• Matches USMC VMFA-211 cured silicone sealant debris repair log (DOC-02)\n"
        "• Grounds fix in official JTD Section 53-30-01 (DOC-01) 18.5 N·m torque spec\n"
        "• 100% verbatim source-cited provenance with direct manual deep-links\n\n"
        "MEASURED OPERATIONAL IMPACT:\n"
        "Resolves chronic 'Could Not Duplicate' defects, eliminating 14-hour teardowns "
        "with 0.38s instant, verified repair procedures."
    )
    ax.text(
        x3 + 0.015, col_y + col_h - 0.125,
        p3_text, fontsize=9.8, color=TEXT_SECONDARY, ha="left", va="top", linespacing=1.35
    )

    # 4. Bottom Row: Executive Value Realization Matrix (4 Metric Cards)
    m_w = 0.218
    m_gap = 0.016
    m_y = 0.045
    m_h = 0.220

    metrics = [
        (
            "MORNING STAND-UP TRIAGE",
            "60–90 min", "1.42s",
            "98% Time Compressed",
            "Replaces manual ERP export with live, screen-fitted Spreadsheet Cards.",
            GC_BLUE, PILL_BLUE_BG
        ),
        (
            "SORTIE PROTECTION & SWAP",
            "3–4 hours", "1.18s",
            "Zero Mission Aborts",
            "Correlates component telemetry, depot spares & schedules in single turn.",
            GC_GREEN, PILL_GREEN_BG
        ),
        (
            "UNCODED DEFECT RESOLUTION",
            "14-hr Teardown", "0.38s",
            "100% Provenance",
            "Bridges cross-service fleet memory to solve zero-diagnostic canopy fault.",
            GC_AMBER, PILL_AMBER_BG
        ),
        (
            "SOVEREIGN DATA RESIDENCY",
            "Multi-Region Drift", "Strict EU",
            "100% Read-Only Safety",
            "Vertex AI europe-west1, BigQuery EU, Discovery Engine eu. Zero risk.",
            GC_NAVY, PILL_BLUE_BG
        ),
    ]

    for i, (title, before, after, delta, note, color, pill_bg) in enumerate(metrics):
        mx = 0.04 + i * (m_w + m_gap)
        draw_card(ax, mx, m_y, m_w, m_h, bg_color=BG_CARD, border_color=BORDER_SUBTLE)

        # Title
        ax.text(
            mx + 0.012, m_y + m_h - 0.022,
            title, fontsize=10, fontweight="bold", color=color, ha="left", va="top"
        )

        # Before -> After
        ax.text(
            mx + 0.012, m_y + m_h - 0.055,
            "Baseline: ", fontsize=9.5, color=TEXT_MUTED, ha="left", va="top"
        )
        ax.text(
            mx + 0.065, m_y + m_h - 0.055,
            before, fontsize=11, fontweight="bold", color=GC_RED, ha="left", va="top"
        )

        ax.text(
            mx + 0.012, m_y + m_h - 0.088,
            "AI Action: ", fontsize=9.5, color=TEXT_MUTED, ha="left", va="top"
        )
        ax.text(
            mx + 0.065, m_y + m_h - 0.088,
            after, fontsize=14, fontweight="bold", color=GC_GREEN, ha="left", va="top"
        )

        # Delta Badge
        draw_badge(ax, mx + m_w / 2, m_y + 0.075, delta, pill_bg, color, font_size=10, pad_x=0.015, pad_y=0.006)

        # Note
        ax.text(
            mx + 0.012, m_y + 0.042,
            note, fontsize=8.8, color=TEXT_SECONDARY, ha="left", va="top", linespacing=1.2
        )

    plt.savefig(output_path, dpi=160, facecolor=BG_WHITE, edgecolor="none")
    plt.close(fig)
    print(f"[OK] Generated Executive Capability Slide: {output_path}")


def generate_technical_architecture_slide(output_path: Path):
    """Generate Slide B: Updated Technical Deployment & Multi-Agent Architecture."""
    fig = plt.figure(figsize=(19.2, 10.8), dpi=160, facecolor=BG_WHITE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # 1. Header Banner
    ax.text(
        0.04, 0.945,
        "F-35 FLEET SUSTAINMENT PLATFORM — POC TECHNICAL ARCHITECTURE",
        fontsize=24, fontweight="bold", color=GC_NAVY, ha="left", va="top"
    )
    ax.text(
        0.04, 0.910,
        "Vertex AI Agent Runtime (europe-west1) · Google ADK 2.0 · Gemini 3.8 Flash · Sovereign EU Data Residency",
        fontsize=13.5, color=TEXT_SECONDARY, ha="left", va="top"
    )

    # Top Badges (Right side)
    draw_badge(ax, 0.62, 0.930, "REASONING ENGINE: 5022570215192395776", PILL_BLUE_BG, GC_NAVY, font_size=9.5)
    draw_badge(ax, 0.81, 0.930, "GEMINI 3.8 FLASH ENTERPRISE", PILL_GREEN_BG, GC_GREEN, font_size=9.5)
    draw_badge(ax, 0.93, 0.930, "SUB-SECOND SLAS", PILL_AMBER_BG, GC_AMBER, font_size=9.5)

    # Separator Line
    ax.plot([0.04, 0.96], [0.880, 0.880], color=BORDER_SUBTLE, lw=1.5)

    # 2. Main Architecture Layout (4 Horizontal Functional Tiers)
    t_w = 0.92
    t_x = 0.04

    # ---------------- TIER 1: User & Experience Layer ----------------
    t1_y = 0.720
    t1_h = 0.145
    draw_card(ax, t_x, t1_y, t_w, t1_h, bg_color=BG_SURFACE, border_color=BORDER_SUBTLE, accent_bar_color=GC_BLUE)
    ax.text(
        t_x + 0.015, t1_y + t1_h - 0.022,
        "1. USER & EXPERIENCE TIER — GEMINI ENTERPRISE (eu Multi-Region) · NATIVE ADK RUNTIME STREAMING",
        fontsize=11.5, fontweight="bold", color=GC_NAVY, ha="left", va="top"
    )

    box1_w = 0.280
    box_gap = 0.020

    # User Personas
    b1_x = t_x + 0.015
    draw_card(ax, b1_x, t1_y + 0.015, box1_w, t1_h - 0.045, bg_color=BG_CARD, border_color=BORDER_SUBTLE)
    ax.text(b1_x + 0.010, t1_y + t1_h - 0.052, "UK Lightning Force Personas", fontsize=10, fontweight="bold", color=TEXT_PRIMARY)
    ax.text(
        b1_x + 0.010, t1_y + t1_h - 0.075,
        "• Act 1: Squadron Maint Officer & Wing Controller\n"
        "• Act 2: Squadron Logistics Officer & Commander\n"
        "• Act 3: Flight-Line Maintenance Chief",
        fontsize=9, color=TEXT_SECONDARY, linespacing=1.2
    )

    # Gemini Enterprise Web UI
    b2_x = b1_x + box1_w + box_gap
    draw_card(ax, b2_x, t1_y + 0.015, box1_w, t1_h - 0.045, bg_color=BG_CARD, border_color=BORDER_SUBTLE)
    ax.text(b2_x + 0.010, t1_y + t1_h - 0.052, "Gemini Enterprise Web UI (eu)", fontsize=10, fontweight="bold", color=GC_BLUE)
    ax.text(
        b2_x + 0.010, t1_y + t1_h - 0.075,
        "• Agents (F35 Support) registered via ADK Native\n"
        "• Streaming Endpoint: :streamQuery (SSE, low latency)\n"
        "• Fleet Discovery in Agent Registry (europe-west1)",
        fontsize=9, color=TEXT_SECONDARY, linespacing=1.2
    )

    # Multimodal Output Formats
    b3_x = b2_x + box1_w + box_gap
    draw_card(ax, b3_x, t1_y + 0.015, box1_w, t1_h - 0.045, bg_color=BG_CARD, border_color=BORDER_SUBTLE)
    ax.text(b3_x + 0.010, t1_y + t1_h - 0.052, "Storyboard Output Modalities", fontsize=10, fontweight="bold", color=GC_GREEN)
    ax.text(
        b3_x + 0.010, t1_y + t1_h - 0.075,
        "• Act 1: Screen-Fitted Spreadsheet Cards + Auto GCS CSV\n"
        "• Act 2: Full HD 16:9 Presentation Slides (chart_painter.py)\n"
        "• Act 3: 100% Verbatim S1000D Cited Manual Procedures",
        fontsize=9, color=TEXT_SECONDARY, linespacing=1.2
    )

    # ---------------- TIER 2: Agentic Orchestration Layer ----------------
    t2_y = 0.405
    t2_h = 0.295
    draw_card(ax, t_x, t2_y, t_w, t2_h, bg_color=BG_SURFACE, border_color=BORDER_SUBTLE, accent_bar_color=GC_GREEN)
    ax.text(
        t_x + 0.015, t2_y + t2_h - 0.020,
        "2. AGENTIC ORCHESTRATION TIER — VERTEX AI AGENT RUNTIME (europe-west1) · ADK 2.0 MULTI-AGENT",
        fontsize=11.5, fontweight="bold", color=GC_GREEN, ha="left", va="top"
    )

    # Root Coordinator Box
    rc_w = 0.890
    rc_x = t_x + 0.015
    rc_y = t2_y + t2_h - 0.080
    draw_card(ax, rc_x, rc_y, rc_w, 0.052, bg_color=BG_CARD, border_color=GC_BLUE)
    ax.text(
        rc_x + 0.012, rc_y + 0.038,
        "Root Coordinator: f35_sustainment_coordinator",
        fontsize=11, fontweight="bold", color=GC_NAVY
    )
    ax.text(
        rc_x + 0.012, rc_y + 0.016,
        "gemini-3.8-flash (enterprise=True, location='global', thinking_level='LOW', temp=0.0) · Sub-450ms Router · Tier 1 & 2 Fast-Path Interception (< 5 ms for Greetings, Capabilities, BI Comparisons)",
        fontsize=9.2, color=TEXT_SECONDARY
    )
    draw_badge(ax, rc_x + rc_w - 0.060, rc_y + 0.026, "FAST-PATH: < 5 ms", PILL_GREEN_BG, GC_GREEN, font_size=9)

    # 3 Specialist Sub-Agents (Columns)
    sub_w = 0.285
    sub_y = t2_y + 0.015
    sub_h = 0.180

    # Sub-Agent 1: Maintenance Data
    s1_x = t_x + 0.015
    draw_card(ax, s1_x, sub_y, sub_w, sub_h, bg_color=BG_CARD, border_color=BORDER_SUBTLE)
    draw_badge(ax, s1_x + 0.065, sub_y + sub_h - 0.020, "ACT 1 SPECIALIST", PILL_BLUE_BG, GC_NAVY, font_size=8.5)
    draw_badge(ax, s1_x + sub_w - 0.045, sub_y + sub_h - 0.020, "1.42s SLA", PILL_GREEN_BG, GC_GREEN, font_size=8.5)
    ax.text(s1_x + 0.010, sub_y + sub_h - 0.042, "f35_maintenance_data_agent", fontsize=10.5, fontweight="bold", color=GC_NAVY)
    ax.text(s1_x + 0.010, sub_y + sub_h - 0.058, "@F35-Maintenance-Data", fontsize=9, fontstyle="italic", color=TEXT_MUTED)
    ax.text(
        s1_x + 0.010, sub_y + sub_h - 0.076,
        "• Prompt 1: Urgent CSG Stand-Up (Spots ZM151)\n"
        "• Prompt 2: ZM151 Post-Sortie Faults & CND Triage\n"
        "• Prompt 3: Bay Crew, QAR Inspector & Tool SQEP\n"
        "• 3-Layer Semantic Ontology & Read-Only AST Gate\n"
        "• Pre-model deterministic formatting (< 10 ms, OPT-05)\n"
        "• Tool: execute_maintenance_sql (Auto CSV Export)",
        fontsize=8.8, color=TEXT_SECONDARY, linespacing=1.22
    )

    # Sub-Agent 2: Analytics & Readiness
    s2_x = s1_x + sub_w + 0.017
    draw_card(ax, s2_x, sub_y, sub_w, sub_h, bg_color=BG_CARD, border_color=BORDER_SUBTLE)
    draw_badge(ax, s2_x + 0.065, sub_y + sub_h - 0.020, "ACT 2 SPECIALIST", PILL_GREEN_BG, GC_GREEN, font_size=8.5)
    draw_badge(ax, s2_x + sub_w - 0.045, sub_y + sub_h - 0.020, "1.18s SLA", PILL_GREEN_BG, GC_GREEN, font_size=8.5)
    ax.text(s2_x + 0.010, sub_y + sub_h - 0.042, "f35_analytics_agent", fontsize=10.5, fontweight="bold", color=GC_GREEN)
    ax.text(s2_x + 0.010, sub_y + sub_h - 0.058, "@F35-Sustainment-Analytics", fontsize=9, fontstyle="italic", color=TEXT_MUTED)
    ax.text(
        s2_x + 0.010, sub_y + sub_h - 0.076,
        "• Prompt 4: ZM151 Actuator (1,000.4h) vs 30d Spares\n"
        "• Prompt 4: Swaps 07:30Z Sortie to ZM154 (842.0h)\n"
        "• Prompt 5: On-demand 16:9 Presentation Slide (0.78s)\n"
        "• Bundled fatigue + tail-swap single turn (OPT-02)\n"
        "• Thread-pooled 3-table BigQuery execution (OPT-03)\n"
        "• Tools: check_actuator..., render_sustainment_chart",
        fontsize=8.8, color=TEXT_SECONDARY, linespacing=1.22
    )

    # Sub-Agent 3: Technical Manuals & Fleet Memory
    s3_x = s2_x + sub_w + 0.017
    draw_card(ax, s3_x, sub_y, sub_w, sub_h, bg_color=BG_CARD, border_color=BORDER_SUBTLE)
    draw_badge(ax, s3_x + 0.065, sub_y + sub_h - 0.020, "ACT 3 SPECIALIST", PILL_AMBER_BG, GC_AMBER, font_size=8.5)
    draw_badge(ax, s3_x + sub_w - 0.045, sub_y + sub_h - 0.020, "0.38s SLA", PILL_GREEN_BG, GC_GREEN, font_size=8.5)
    ax.text(s3_x + 0.010, sub_y + sub_h - 0.042, "f35_jtd_search_agent", fontsize=10.5, fontweight="bold", color=GC_AMBER)
    ax.text(s3_x + 0.010, sub_y + sub_h - 0.058, "@F35-JTD-Search", fontsize=9, fontstyle="italic", color=TEXT_MUTED)
    ax.text(
        s3_x + 0.010, sub_y + sub_h - 0.076,
        "• Prompt 6: Resolves ZM151 Zero-Diagnostic Canopy Fault\n"
        "• Cross-Service Allied Memory: USMC VMFA-211 Sealant\n"
        "• Authoritative Manual: JTD 53-30-01 18.5 N·m Torque\n"
        "• Bidirectional UK/US Dialect Bridge (catch/latch, spanner)\n"
        "• Parallel single-pass REST search (pageSize=15, OPT-03)\n"
        "• Tool: search_technical_manuals_and_repair_logs",
        fontsize=8.8, color=TEXT_SECONDARY, linespacing=1.22
    )

    # ---------------- TIER 3: Sovereign EU Data, Search & Storage Layer ----------------
    t3_y = 0.225
    t3_h = 0.165
    draw_card(ax, t_x, t3_y, t_w, t3_h, bg_color=BG_SURFACE, border_color=BORDER_SUBTLE, accent_bar_color=GC_AMBER)
    ax.text(
        t_x + 0.015, t3_y + t3_h - 0.022,
        "3. SOVEREIGN EU DATA, SEARCH & STORAGE TIER — STRICT RESIDENCY (EU / eu Multi-Region)",
        fontsize=11.5, fontweight="bold", color=GC_AMBER, ha="left", va="top"
    )

    d_w = 0.285
    d_gap = 0.017

    # BigQuery Data Warehouse
    d1_x = t_x + 0.015
    draw_card(ax, d1_x, t3_y + 0.015, d_w, t3_h - 0.045, bg_color=BG_CARD, border_color=BORDER_SUBTLE)
    ax.text(d1_x + 0.010, t3_y + t3_h - 0.052, "BigQuery F35 Data Warehouse (EU)", fontsize=10, fontweight="bold", color=GC_BLUE)
    ax.text(
        d1_x + 0.010, t3_y + t3_h - 0.075,
        "Dataset: antig-dave.ukd_f35_sustainment_demo (600 Rows)\n"
        "• Act 1: maintenance_work_orders (100), phm_bit_fault_events (100),\n"
        "         work_center_tooling_and_sqep (100)\n"
        "• Act 2: airframe_component_telemetry (100), global_depot_inventory (100),\n"
        "         squadron_sortie_schedule (100)",
        fontsize=8.5, color=TEXT_SECONDARY, linespacing=1.2
    )

    # Discovery Engine Technical Manuals
    d2_x = d1_x + d_w + d_gap
    draw_card(ax, d2_x, t3_y + 0.015, d_w, t3_h - 0.045, bg_color=BG_CARD, border_color=BORDER_SUBTLE)
    ax.text(d2_x + 0.010, t3_y + t3_h - 0.052, "Discovery Engine Pubs & Logs (eu)", fontsize=10, fontweight="bold", color=GC_GREEN)
    ax.text(
        d2_x + 0.010, t3_y + t3_h - 0.075,
        "Endpoints: eu-discoveryengine.googleapis.com (locations/eu)\n"
        "• ukd-f35-narrative-logs-ds: DOC-02 (USMC VMFA-211 Sealant),\n"
        "  DOC-03 (RAF 617 Sqn Hydraulic Log)\n"
        "• ukd-f35-jtd-ietm-ds: DOC-01 (JTD 53-30-01 18.5 N·m),\n"
        "  DOC-09 (MAM 9-1 Fastener Integrity)",
        fontsize=8.5, color=TEXT_SECONDARY, linespacing=1.2
    )

    # Cloud Storage Staging
    d3_x = d2_x + d_w + d_gap
    draw_card(ax, d3_x, t3_y + 0.015, d_w, t3_h - 0.045, bg_color=BG_CARD, border_color=BORDER_SUBTLE)
    ax.text(d3_x + 0.010, t3_y + t3_h - 0.052, "Cloud Storage Staging (europe-west1)", fontsize=10, fontweight="bold", color=GC_AMBER)
    ax.text(
        d3_x + 0.010, t3_y + t3_h - 0.075,
        "Bucket: gs://antig-dave-f35-staging-europe-west1\n"
        "• /exports/*.csv: Non-blocking background CSV upload (OPT-03)\n"
        "• /charts/*.png: Widescreen 16:9 presentation slide graphics\n"
        "• /unstructured/docs/*.pdf: Original S1000D reference publications\n"
        "• In-memory LRU chart & SQL result caching (60s TTL)",
        fontsize=8.5, color=TEXT_SECONDARY, linespacing=1.2
    )

    # ---------------- TIER 4: Latency Optimizations & Guardrails ----------------
    t4_y = 0.045
    t4_h = 0.165
    draw_card(ax, t_x, t4_y, t_w, t4_h, bg_color=BG_SURFACE, border_color=BORDER_SUBTLE, accent_bar_color=GC_RED)
    ax.text(
        t_x + 0.015, t4_y + t4_h - 0.022,
        "4. PERFORMANCE ENGINEERING & SECURITY ENVELOPE (OPT-01..06 · PERF-01..08 · SAFE-ADK-01..02)",
        fontsize=11.5, fontweight="bold", color=GC_RED, ha="left", va="top"
    )

    g_w = 0.218
    g_gap = 0.016

    guards = [
        (
            "PAYLOAD SLIMMING (OPT-01)",
            "slim_tool_response_after_tool_callback",
            "Limits tool JSON payload to <= 4 KB before LLM post-tool synthesis. Eliminates token bloat & 2-3s synthesis delays.",
            GC_BLUE
        ),
        (
            "SINGLE-TURN BUNDLING (OPT-02)",
            "Fatigue + Sortie Tail Swap Bundling",
            "check_actuator_fatigue... embeds swap recommendations directly into Turn 1, eliminating a multi-turn round-trip.",
            GC_GREEN
        ),
        (
            "PARALLEL I/O & CACHE (OPT-03)",
            "ThreadPool BQ & DE Execution",
            "Module singletons, parallel BQ/DE pools (_UC1_BQ_POOL, _UC2_DE_POOL), background CSV uploads & Context Caching.",
            GC_AMBER
        ),
        (
            "FAST-PATH ROUTING (OPT-04..06)",
            "Tier 1/2 Interception & Pre-Dispatch",
            "< 5 ms interception for greetings, capabilities & BI comparisons. Deterministic tool formatting (< 10 ms).",
            GC_RED
        ),
    ]

    for i, (g_title, g_sub, g_desc, g_color) in enumerate(guards):
        gx = t_x + 0.015 + i * (g_w + g_gap)
        draw_card(ax, gx, t4_y + 0.015, g_w, t4_h - 0.045, bg_color=BG_CARD, border_color=BORDER_SUBTLE)
        ax.text(gx + 0.010, t4_y + t4_h - 0.052, g_title, fontsize=9.5, fontweight="bold", color=g_color)
        ax.text(gx + 0.010, t4_y + t4_h - 0.072, g_sub, fontsize=8.5, fontstyle="italic", color=TEXT_MUTED)
        ax.text(
            gx + 0.010, t4_y + t4_h - 0.092,
            g_desc, fontsize=8.2, color=TEXT_SECONDARY, linespacing=1.2
        )

    plt.savefig(output_path, dpi=160, facecolor=BG_WHITE, edgecolor="none")
    plt.close(fig)
    print(f"[OK] Generated Technical Architecture Slide: {output_path}")


def main():
    print("=" * 80)
    print("Generating F-35 POC Executive Presentation Slides (16:9 Google Cloud Palette)...")
    print("=" * 80)

    slide_a_path = DOCS_ASSETS_DIR / "f35_executive_capability_architecture_16x9_white_gcloud.png"
    slide_b_path = DOCS_ASSETS_DIR / "f35_poc_architecture_16x9_white_gcloud.png"

    generate_executive_capability_slide(slide_a_path)
    generate_technical_architecture_slide(slide_b_path)

    print("=" * 80)
    print("Successfully generated both executive architecture slides!")
    print(f"Slide A (Executive Capability): {slide_a_path}")
    print(f"Slide B (Technical Deployment): {slide_b_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
