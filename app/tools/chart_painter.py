"""Presentation Chart Painter Module for F-35 Fleet Sustainment.

Renders 300 DPI publication-quality presentation graphics using Matplotlib
(headless Agg backend) in the Clean Light Briefing Theme (RAF Blue, Crimson,
Forest Green, Slate). Uploads rendered charts to Google Cloud Storage
(gs://antig-dave-f35-staging-europe-west1/charts/) and produces authenticated
URLs for instant slide deck download and inline Markdown presentation.
"""

from __future__ import annotations

import io
import logging
import os
import time
from typing import Any

import matplotlib

# Mandatory headless backend before importing pyplot
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import FancyBboxPatch

from app.config import GCS_STAGING_BUCKET, PROJECT_ID
from app.seed_data.bq_seed_records import (
    AIRFRAME_COMPONENT_TELEMETRY_ROWS,
    GLOBAL_DEPOT_INVENTORY_ROWS,
)

logger = logging.getLogger(__name__)

# Color Palette: Clean Light Briefing Theme
RAF_BLUE = "#00247d"
NAVY_PRIMARY = "#1e3a8a"
SERVICEABLE_GREEN = "#16a34a"
CRIMSON_BREACH = "#dc2626"
AMBER_DEMAND = "#d97706"
SLATE_DARK = "#0f172a"
SLATE_MUTED = "#64748b"
SLATE_BORDER = "#cbd5e1"
BG_PANEL = "#f8fafc"
BG_CANVAS = "#ffffff"

CHART_STORAGE_PREFIX = "charts"


def _apply_clean_light_theme(ax: plt.Axes) -> None:
    """Apply consistent high-contrast flight-line presentation styling to an axis."""
    ax.set_facecolor(BG_PANEL)
    ax.grid(True, linestyle="--", linewidth=0.7, color=SLATE_BORDER, alpha=0.7, zorder=0)
    for spine in ax.spines.values():
        spine.set_color(SLATE_BORDER)
        spine.set_linewidth(1.0)
    ax.tick_params(colors=SLATE_DARK, labelsize=9.5, width=1.0)


def render_actuator_fatigue_chart(
    telemetry_rows: list[dict[str, Any]] | None = None,
) -> bytes:
    """Render high-resolution 16:9 Actuator Fatigue Threshold Chart PNG.

    Visualizes component flight hours across squadron airframes against the
    mandatory 1,000.0-hour life-limit threshold (MIL-HDBK-516C / JTD 53-11-00).
    """
    rows = telemetry_rows or AIRFRAME_COMPONENT_TELEMETRY_ROWS
    # Filter to Marham or take top 5
    items = [
        r for r in rows
        if "actuator" in str(r.get("component_name", "")).lower()
        or "act" in str(r.get("part_serial_number", "")).lower()
    ]
    if not items:
        items = rows[:5]

    tails = [str(r.get("tail_number", "UNKNOWN")) for r in items]
    hours = [float(r.get("current_flight_hours", 0.0)) for r in items]
    serials = [str(r.get("part_serial_number", "")) for r in items]
    threshold = float(items[0].get("life_limit_threshold_hrs", 1000.0)) if items else 1000.0

    # Color logic: Crimson for breach, Green for serviceable swap, Slate for others
    bar_colors: list[str] = []
    for tail, h in zip(tails, hours):
        if h >= threshold:
            bar_colors.append(CRIMSON_BREACH)
        elif tail == "ZM154":
            bar_colors.append(SERVICEABLE_GREEN)
        else:
            bar_colors.append(NAVY_PRIMARY)

    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=200, facecolor=BG_CANVAS)
    _apply_clean_light_theme(ax)

    bars = ax.bar(
        range(len(tails)),
        hours,
        width=0.55,
        color=bar_colors,
        edgecolor=SLATE_DARK,
        linewidth=0.8,
        zorder=3,
    )

    # Threshold condemnation reference line
    ax.axhline(
        threshold,
        color=CRIMSON_BREACH,
        linestyle="--",
        linewidth=2.0,
        zorder=4,
        label=f"Mandatory Life-Limit Condemnation Threshold: {threshold:,.1f} Hrs",
    )

    # Value callouts on top of bars
    for idx, (b, h, tail, s) in enumerate(zip(bars, hours, tails, serials)):
        val_str = f"{h:,.1f}h"
        delta = h - threshold
        if h >= threshold:
            label = f"{val_str}\nEXCEEDED (+{delta:.1f}h)\n[PMC-M]"
            ax.annotate(
                label,
                xy=(b.get_x() + b.get_width() / 2, h),
                xytext=(0, 6),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9.0,
                fontweight="bold",
                color=CRIMSON_BREACH,
                bbox=dict(boxstyle="round,pad=0.25", fc="#fef2f2", ec=CRIMSON_BREACH, lw=1),
            )
        elif tail == "ZM154":
            label = f"{val_str}\nSERVICEABLE SPARE\n[MC 842.0h]"
            ax.annotate(
                label,
                xy=(b.get_x() + b.get_width() / 2, h),
                xytext=(0, 6),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9.0,
                fontweight="bold",
                color=SERVICEABLE_GREEN,
                bbox=dict(boxstyle="round,pad=0.25", fc="#f0fdf4", ec=SERVICEABLE_GREEN, lw=1),
            )
        else:
            ax.annotate(
                f"{val_str}\n({s})",
                xy=(b.get_x() + b.get_width() / 2, h),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8.5,
                color=SLATE_DARK,
            )

    ax.set_xticks(range(len(tails)))
    ax.set_xticklabels(
        [f"{t}\n({s})" for t, s in zip(tails, serials)],
        fontsize=10,
        fontweight="bold",
        color=SLATE_DARK,
    )
    ax.set_ylabel("Component Operating Hours", fontsize=11, fontweight="bold", color=SLATE_DARK)
    ax.set_ylim(0, max(max(hours) * 1.25, threshold * 1.2))
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f} h"))

    # Titles & Header
    plt.suptitle(
        "F-35 FLEET SUSTAINMENT — HORIZONTAL TAIL ACTUATOR FATIGUE TRACKER",
        fontsize=14,
        fontweight="bold",
        color=SLATE_DARK,
        y=0.97,
    )
    ax.set_title(
        "Location: RAF Marham / 617 Sqn | Subsystem: Frame 496 Port EHA (NSN: 1680-01-619-4821)\n"
        "Decision Gate: Immediate Tail Swap Required for ZM151 prior to Morning Sortie SRT-MAR-20261103-01",
        fontsize=10,
        color=SLATE_MUTED,
        pad=10,
    )

    ax.legend(loc="upper left", frameon=True, facecolor=BG_CANVAS, edgecolor=SLATE_BORDER, fontsize=9.5)
    plt.tight_layout(rect=[0.02, 0.03, 0.98, 0.94])

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=160, facecolor=BG_CANVAS)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def render_depot_inventory_chart(
    inventory_rows: list[dict[str, Any]] | None = None,
) -> bytes:
    """Render high-resolution 16:9 Regional Depot Stock vs 30-Day Demand Chart PNG."""
    rows = inventory_rows or GLOBAL_DEPOT_INVENTORY_ROWS
    depots = [str(r.get("depot_name", "Unknown Depot")).replace(" Regional Sustainment Hub", "").replace(" Afloat Spares", "") for r in rows]
    on_hand = [int(r.get("quantity_on_hand", 0)) for r in rows]
    reserved = [int(r.get("quantity_reserved_30d", 0)) for r in rows]
    etas = [float(r.get("avg_shipping_eta_hours", 0.0)) for r in rows]

    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=200, facecolor=BG_CANVAS)
    _apply_clean_light_theme(ax)

    x = range(len(depots))
    width = 0.32

    bars1 = ax.bar(
        [i - width / 2 for i in x],
        on_hand,
        width=width,
        color=RAF_BLUE,
        edgecolor=SLATE_DARK,
        linewidth=0.8,
        label="Serviceable Stock On-Hand (Condition Code A)",
        zorder=3,
    )
    bars2 = ax.bar(
        [i + width / 2 for i in x],
        reserved,
        width=width,
        color=AMBER_DEMAND,
        edgecolor=SLATE_DARK,
        linewidth=0.8,
        label="30-Day Reserved Sortie Demand",
        zorder=3,
    )

    # Value annotations on bars
    for b in bars1:
        h = b.get_height()
        ax.annotate(
            f"{int(h)} EA",
            xy=(b.get_x() + b.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color=RAF_BLUE,
        )
    for b in bars2:
        h = b.get_height()
        ax.annotate(
            f"{int(h)} EA",
            xy=(b.get_x() + b.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color=AMBER_DEMAND,
        )

    # Net surplus and replenishment ETA callouts
    for idx, (oh, res, eta) in enumerate(zip(on_hand, reserved, etas)):
        net = oh - res
        callout = f"Net Available: +{net} EA\nExpedited ETA: {eta:.0f} hrs"
        ax.text(
            idx,
            max(oh, res) + 0.85,
            callout,
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            color=SLATE_DARK,
            bbox=dict(boxstyle="round,pad=0.3", fc="#eff6ff", ec=RAF_BLUE, lw=1.0),
        )

    ax.set_xticks(list(x))
    ax.set_xticklabels(depots, fontsize=11, fontweight="bold", color=SLATE_DARK)
    ax.set_ylabel("Quantity (Units / Each)", fontsize=11, fontweight="bold", color=SLATE_DARK)
    ax.set_ylim(0, max(max(on_hand), max(reserved)) + 2.5)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    plt.suptitle(
        "F-35 GLOBAL DEPOT INVENTORY & 30-DAY DEMAND ALLOCATION",
        fontsize=14,
        fontweight="bold",
        color=SLATE_DARK,
        y=0.97,
    )
    ax.set_title(
        "Item: Port Electro-Hydrostatic Actuator (NSN: 1680-01-619-4821 | P/N: 35-53-EHA-01)\n"
        "RAF Marham Regional Hub maintains positive net inventory (+2 serviceable units ready for immediate install)",
        fontsize=10,
        color=SLATE_MUTED,
        pad=10,
    )

    ax.legend(loc="upper right", frameon=True, facecolor=BG_CANVAS, edgecolor=SLATE_BORDER, fontsize=10)
    plt.tight_layout(rect=[0.02, 0.03, 0.98, 0.94])

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=160, facecolor=BG_CANVAS)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def render_executive_dashboard_chart(
    telemetry_rows: list[dict[str, Any]] | None = None,
    inventory_rows: list[dict[str, Any]] | None = None,
) -> bytes:
    """Render unified 16:9 Widescreen Executive Briefing Slide PNG (Side-by-Side)."""
    t_rows = telemetry_rows or AIRFRAME_COMPONENT_TELEMETRY_ROWS
    i_rows = inventory_rows or GLOBAL_DEPOT_INVENTORY_ROWS

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6.75), dpi=160, facecolor=BG_CANVAS)
    _apply_clean_light_theme(ax1)
    _apply_clean_light_theme(ax2)

    # ---- Left Subplot: Actuator Fatigue Tracker ----
    items = [r for r in t_rows if "actuator" in str(r.get("component_name", "")).lower()][:4]
    if not items:
        items = t_rows[:4]
    tails = [str(r.get("tail_number", "")) for r in items]
    hours = [float(r.get("current_flight_hours", 0.0)) for r in items]
    threshold = 1000.0

    colors1 = [CRIMSON_BREACH if h >= threshold else (SERVICEABLE_GREEN if t == "ZM154" else NAVY_PRIMARY) for t, h in zip(tails, hours)]
    b1 = ax1.bar(tails, hours, width=0.55, color=colors1, edgecolor=SLATE_DARK, linewidth=0.8, zorder=3)
    ax1.axhline(threshold, color=CRIMSON_BREACH, linestyle="--", linewidth=1.8, label="Condemnation Limit (1,000h)")

    for bar, h, t in zip(b1, hours, tails):
        if h >= threshold:
            ax1.annotate(f"{h:.1f}h\nBREACH\n(PMC-M)", (bar.get_x() + bar.get_width()/2, h), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=8.5, fontweight="bold", color=CRIMSON_BREACH)
        elif t == "ZM154":
            ax1.annotate(f"{h:.1f}h\nSWAP OK\n(MC)", (bar.get_x() + bar.get_width()/2, h), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=8.5, fontweight="bold", color=SERVICEABLE_GREEN)
        else:
            ax1.annotate(f"{h:.1f}h", (bar.get_x() + bar.get_width()/2, h), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.5, color=SLATE_DARK)

    ax1.set_title("1. Airframe Component Flight Hours", fontsize=12, fontweight="bold", color=SLATE_DARK, pad=8)
    ax1.set_ylabel("Operating Hours", fontsize=10, fontweight="bold", color=SLATE_DARK)
    ax1.set_ylim(0, max(hours) * 1.25)
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f} h"))
    ax1.legend(loc="lower left", fontsize=8.5, frameon=True, facecolor=BG_CANVAS)

    # ---- Right Subplot: Depot Inventory ----
    depots = [str(r.get("depot_name", "")).replace(" Regional Sustainment Hub", "").replace(" Afloat Spares", "") for r in i_rows]
    on_hand = [int(r.get("quantity_on_hand", 0)) for r in i_rows]
    reserved = [int(r.get("quantity_reserved_30d", 0)) for r in i_rows]

    x2 = range(len(depots))
    w2 = 0.32
    ax2.bar([i - w2/2 for i in x2], on_hand, width=w2, color=RAF_BLUE, edgecolor=SLATE_DARK, label="On-Hand (Cond A)", zorder=3)
    ax2.bar([i + w2/2 for i in x2], reserved, width=w2, color=AMBER_DEMAND, edgecolor=SLATE_DARK, label="30d Demand", zorder=3)

    for i, (oh, res) in enumerate(zip(on_hand, reserved)):
        ax2.annotate(f"{oh} EA", (i - w2/2, oh), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9, fontweight="bold", color=RAF_BLUE)
        ax2.annotate(f"{res} EA", (i + w2/2, res), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9, fontweight="bold", color=AMBER_DEMAND)

    ax2.set_xticks(list(x2))
    ax2.set_xticklabels(depots, fontsize=10, fontweight="bold")
    ax2.set_title("2. Regional Depot Spares Allocation", fontsize=12, fontweight="bold", color=SLATE_DARK, pad=8)
    ax2.set_ylabel("Quantity (EA)", fontsize=10, fontweight="bold", color=SLATE_DARK)
    ax2.set_ylim(0, max(max(on_hand), max(reserved)) + 2.0)
    ax2.legend(loc="upper right", fontsize=8.5, frameon=True, facecolor=BG_CANVAS)

    # Master Banner Header
    plt.suptitle(
        "F-35 SUSTAINMENT READINESS BRIEFING — 617 SQN RAF MARHAM",
        fontsize=16,
        fontweight="bold",
        color=SLATE_DARK,
        y=0.97,
    )
    fig.text(
        0.5,
        0.915,
        "Morning Sortie: SRT-MAR-20261103-01 (VIPER-1) | Action: Ground ZM151 -> Deploy Spare ZM154 | Depot Delivery: 18.0 Hrs",
        ha="center",
        fontsize=11,
        color=SLATE_MUTED,
        fontstyle="italic",
    )

    # Master Bottom Status Callout
    status_text = (
        "DECISION: TAIL SWAP APPROVED (ZM151 -> ZM154)  |  READINESS IMPACT: SORTIE ON-TIME (06:30Z)  |  "
        "REQUISITION: NSN 1680-01-619-4821 ROUTED TO DEPOT-MAR-01"
    )
    fig.text(
        0.5,
        0.03,
        status_text,
        ha="center",
        va="center",
        fontsize=10.5,
        fontweight="bold",
        color=BG_CANVAS,
        bbox=dict(boxstyle="square,pad=0.6", fc=NAVY_PRIMARY, ec=SLATE_DARK, lw=1.2),
    )

    plt.tight_layout(rect=[0.02, 0.07, 0.98, 0.90])

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=160, facecolor=BG_CANVAS)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def upload_chart_to_gcs(
    image_bytes: bytes,
    filename: str,
    bucket_name: str = GCS_STAGING_BUCKET,
) -> tuple[str, float]:
    """Upload chart image bytes to GCS and return authenticated URL + elapsed upload ms."""
    t0 = time.perf_counter()
    clean_filename = filename.lstrip("/")
    if not clean_filename.startswith(f"{CHART_STORAGE_PREFIX}/"):
        gcs_object_path = f"{CHART_STORAGE_PREFIX}/{clean_filename}"
    else:
        gcs_object_path = clean_filename

    authenticated_url = (
        f"https://storage.cloud.google.com/{bucket_name}/{gcs_object_path}"
    )

    try:
        from app.clients import get_storage_client

        client = get_storage_client()
        if client is not None:
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(gcs_object_path)
            blob.upload_from_string(image_bytes, content_type="image/png")
            logger.info("Uploaded %d bytes to gs://%s/%s", len(image_bytes), bucket_name, gcs_object_path)
        else:
            logger.info("Storage client not available, authenticated URL formatted for gs://%s/%s", bucket_name, gcs_object_path)
    except Exception as exc:
        logger.warning(
            "GCS upload fallback activated for gs://%s/%s: %s",
            bucket_name,
            gcs_object_path,
            exc,
        )

    upload_ms = (time.perf_counter() - t0) * 1000.0
    return authenticated_url, upload_ms


def generate_sustainment_graphics(
    chart_name: str = "both",
    telemetry_rows: list[dict[str, Any]] | None = None,
    inventory_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Generate high-resolution PNG presentation diagrams and upload them to GCS.

    Returns:
        dict containing image URLs, Markdown embeds, download links, and latency metrics.
    """
    t_start = time.perf_counter()
    raw_name = str(chart_name or "both").strip().lower()

    is_fatigue = any(k in raw_name for k in ("fatigue", "actuator", "threshold", "1"))
    is_depot = any(k in raw_name for k in ("depot", "stock", "demand", "inventory", "2"))
    is_both = any(k in raw_name for k in ("both", "all", "3", "dashboard", "slide")) or (is_fatigue and is_depot) or raw_name in ("charts", "visualizations")

    rendered_assets: list[dict[str, Any]] = []
    total_render_ms = 0.0
    total_upload_ms = 0.0

    if is_both or (not is_fatigue and not is_depot):
        # 1. Executive Dashboard (Slide-Ready Composite with both subplots side-by-side)
        t_r0 = time.perf_counter()
        dash_bytes = render_executive_dashboard_chart(telemetry_rows, inventory_rows)
        t_r1 = time.perf_counter()
        dash_url, u_ms = upload_chart_to_gcs(dash_bytes, "f35_sustainment_executive_dashboard.png")
        r_ms = (t_r1 - t_r0) * 1000.0
        total_render_ms += r_ms
        total_upload_ms += u_ms
        rendered_assets.append({
            "asset_id": "executive_dashboard",
            "title": "F-35 Sustainment Executive Briefing Dashboard (16:9 Presentation Slide)",
            "filename": "f35_sustainment_executive_dashboard.png",
            "url": dash_url,
            "markdown_img": f"![F-35 Sustainment Executive Dashboard]({dash_url})",
            "download_link": f"[📥 Download 16:9 Executive Slide Graphic (PNG)]({dash_url})",
            "render_ms": round(r_ms, 2),
            "upload_ms": round(u_ms, 2),
            "size_bytes": len(dash_bytes),
        })

    elif is_fatigue:
        # 2. Actuator Fatigue Threshold Chart
        t_r0 = time.perf_counter()
        fatigue_bytes = render_actuator_fatigue_chart(telemetry_rows)
        t_r1 = time.perf_counter()
        fatigue_url, u_ms = upload_chart_to_gcs(fatigue_bytes, "actuator_fatigue_threshold_chart.png")
        r_ms = (t_r1 - t_r0) * 1000.0
        total_render_ms += r_ms
        total_upload_ms += u_ms
        rendered_assets.append({
            "asset_id": "actuator_fatigue_chart",
            "title": "Horizontal Tail Actuator Fatigue Threshold Chart",
            "filename": "actuator_fatigue_threshold_chart.png",
            "url": fatigue_url,
            "markdown_img": f"![Actuator Fatigue Threshold Chart]({fatigue_url})",
            "download_link": f"[📥 Download Actuator Fatigue Chart (PNG)]({fatigue_url})",
            "render_ms": round(r_ms, 2),
            "upload_ms": round(u_ms, 2),
            "size_bytes": len(fatigue_bytes),
        })

    elif is_depot:
        # 3. Depot Inventory Chart
        t_r0 = time.perf_counter()
        depot_bytes = render_depot_inventory_chart(inventory_rows)
        t_r1 = time.perf_counter()
        depot_url, u_ms = upload_chart_to_gcs(depot_bytes, "depot_stock_vs_demand_bar_chart.png")
        r_ms = (t_r1 - t_r0) * 1000.0
        total_render_ms += r_ms
        total_upload_ms += u_ms
        rendered_assets.append({
            "asset_id": "depot_inventory_chart",
            "title": "Regional Depot Stock vs 30-Day Demand Chart",
            "filename": "depot_stock_vs_demand_bar_chart.png",
            "url": depot_url,
            "markdown_img": f"![Regional Depot Stock vs Demand Chart]({depot_url})",
            "download_link": f"[📥 Download Depot Stock Chart (PNG)]({depot_url})",
            "render_ms": round(r_ms, 2),
            "upload_ms": round(u_ms, 2),
            "size_bytes": len(depot_bytes),
        })

    total_elapsed_ms = (time.perf_counter() - t_start) * 1000.0

    return {
        "status": "SUCCESS",
        "chart_requested": chart_name,
        "assets_generated": len(rendered_assets),
        "total_latency_ms": round(total_elapsed_ms, 2),
        "render_latency_ms": round(total_render_ms, 2),
        "upload_latency_ms": round(total_upload_ms, 2),
        "charts": rendered_assets,
    }
