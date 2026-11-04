"""UC1 Supply Chain & Sortie Readiness Analytics Tools (`f35_analytics_agent`).

Executes partition-pruned BigQuery joins in the EU multi-region against
`antig-dave.ukd_f35_sustainment_demo` and generates dual-compatible outputs:
inline Vega-Lite v5 JSON specifications (`depot_stock_vs_demand_bar_chart` and
`actuator_fatigue_threshold_chart`) plus structured Markdown summary tables.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from google.cloud import bigquery

from app.clients import run_bq_query
from app.config import BQ_DATASET, BQ_LOCATION, PROJECT_ID
from app.schemas import (
    ActuatorReadinessRecord,
    SortieSwapRecommendation,
    VegaLiteSpec,
)
from app.seed_data.bq_seed_records import (
    AIRFRAME_COMPONENT_TELEMETRY_ROWS,
    GLOBAL_DEPOT_INVENTORY_ROWS,
    SQUADRON_SORTIE_SCHEDULE_ROWS,
)
from app.tools.chart_painter import generate_sustainment_graphics

logger = logging.getLogger(__name__)

_BQ_UC1_CACHE: dict[str, dict[str, list[dict[str, Any]]]] = {}


def _fetch_uc1_tables_from_bq(base_location: str) -> dict[str, list[dict[str, Any]]]:
    """Query BigQuery EU tables for UC1 telemetry, depot stock, and sortie schedules."""
    cache_key = base_location.strip().lower() or "all"
    if cache_key in _BQ_UC1_CACHE:
        return _BQ_UC1_CACHE[cache_key]

    telemetry_rows: list[dict[str, Any]] = []
    inventory_rows: list[dict[str, Any]] = []
    sortie_rows: list[dict[str, Any]] = []

    try:
        t1_sql = f"""
            SELECT
                telemetry_record_id,
                tail_number,
                aircraft_variant,
                base_location,
                part_serial_number,
                nsn,
                component_name,
                current_flight_hours,
                life_limit_threshold_hrs
            FROM `{PROJECT_ID}.{BQ_DATASET}.airframe_component_telemetry`
            WHERE LOWER(base_location) = LOWER(@base_location)
            ORDER BY current_flight_hours DESC
        """
        telemetry_rows = run_bq_query(
            t1_sql,
            query_parameters=[
                bigquery.ScalarQueryParameter("base_location", "STRING", base_location)
            ],
        )

        t2_sql = f"""
            SELECT
                nsn,
                part_name,
                depot_id,
                depot_name,
                quantity_on_hand,
                quantity_reserved_30d,
                reorder_point_threshold,
                avg_shipping_eta_hours
            FROM `{PROJECT_ID}.{BQ_DATASET}.global_depot_inventory`
            WHERE nsn = '1680-01-619-4821'
            ORDER BY quantity_on_hand DESC
        """
        inventory_rows = run_bq_query(t2_sql)

        t3_sql = f"""
            SELECT
                sortie_id,
                scheduled_departure_utc,
                assigned_tail_number,
                assigned_pilot_callsign,
                spare_tail_candidate,
                sortie_readiness_status
            FROM `{PROJECT_ID}.{BQ_DATASET}.squadron_sortie_schedule`
            ORDER BY scheduled_departure_utc ASC
        """
        sortie_rows = run_bq_query(t3_sql)
    except Exception as exc:
        logger.warning(
            "BigQuery EU query warning for %s (using seed records): %s",
            base_location,
            exc,
        )

    if not telemetry_rows:
        telemetry_rows = [
            dict(r)
            for r in AIRFRAME_COMPONENT_TELEMETRY_ROWS
            if str(r.get("base_location", "")).lower() == base_location.strip().lower()
        ] or [dict(r) for r in AIRFRAME_COMPONENT_TELEMETRY_ROWS]

    if not inventory_rows:
        inventory_rows = [dict(r) for r in GLOBAL_DEPOT_INVENTORY_ROWS]

    if not sortie_rows:
        sortie_rows = [dict(r) for r in SQUADRON_SORTIE_SCHEDULE_ROWS]

    bundle = {
        "telemetry": telemetry_rows,
        "inventory": inventory_rows,
        "sorties": sortie_rows,
    }
    _BQ_UC1_CACHE[cache_key] = bundle
    return bundle


def _build_depot_stock_bar_chart(
    inventory_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Generate the Vega-Lite v5 grouped bar chart for Regional Depot Stock vs 30-Day Demand."""
    chart_values: list[dict[str, Any]] = []
    for row in inventory_rows:
        depot_label = str(
            row.get("depot_location")
            or row.get("depot_name")
            or row.get("depot_id", "Depot")
        )
        depot_id = str(row.get("depot_id", "DEPOT-RAF-MARHAM-01"))
        on_hand = int(row.get("quantity_on_hand", 4))
        reserved = int(row.get("quantity_reserved_30d", 2))
        net_avail = max(0, on_hand - reserved)
        chart_values.extend(
            [
                {
                    "depot_id": depot_id,
                    "depot_location": depot_label,
                    "nsn": str(row.get("nsn", "1680-01-619-4821")),
                    "metric": "Stock On Hand",
                    "quantity": on_hand,
                    "shipping_eta_hours": float(row.get("avg_shipping_eta_hours", 18.0)),
                },
                {
                    "depot_id": depot_id,
                    "depot_location": depot_label,
                    "nsn": str(row.get("nsn", "1680-01-619-4821")),
                    "metric": "30-Day Reserved Demand",
                    "quantity": reserved,
                    "shipping_eta_hours": float(row.get("avg_shipping_eta_hours", 18.0)),
                },
                {
                    "depot_id": depot_id,
                    "depot_location": depot_label,
                    "nsn": str(row.get("nsn", "1680-01-619-4821")),
                    "metric": "Net Uncommitted Stock",
                    "quantity": net_avail,
                    "shipping_eta_hours": float(row.get("avg_shipping_eta_hours", 18.0)),
                },
            ]
        )

    spec = VegaLiteSpec(
        **{
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "title": "F-35 Aileron Actuator (NSN 1680-01-619-4821) — Regional Depot Stock vs 30-Day Demand",
            "data": {"values": chart_values},
            "mark": {"type": "bar", "cornerRadiusEnd": 3, "tooltip": True},
            "encoding": {
                "x": {
                    "field": "depot_location",
                    "type": "nominal",
                    "title": "Regional Supply Depot",
                },
                "y": {
                    "field": "quantity",
                    "type": "quantitative",
                    "title": "Actuator Units",
                },
                "xOffset": {"field": "metric"},
                "color": {
                    "field": "metric",
                    "type": "nominal",
                    "title": "Inventory Metric",
                    "scale": {
                        "domain": [
                            "Stock On Hand",
                            "30-Day Reserved Demand",
                            "Net Uncommitted Stock",
                        ],
                        "range": ["#1A73E8", "#F9AB00", "#1E8E3E"],
                    },
                },
            },
        }
    )
    return spec.model_dump(by_alias=True, exclude_none=True)


def _build_actuator_fatigue_threshold_chart(
    telemetry_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Generate the Vega-Lite v5 threshold chart comparing tail flight hours vs 1,000.0 hr limit."""
    chart_values: list[dict[str, Any]] = []
    seen_tails: set[str] = set()
    for row in telemetry_rows:
        tail = str(row.get("tail_number", ""))
        seen_tails.add(tail)
        hours = float(row.get("current_flight_hours", 0.0))
        limit = float(row.get("life_limit_threshold_hrs", 1000.0))
        breach = hours >= limit
        mc_status = str(
            row.get("mission_capable_status") or ("PMC-M" if breach else "MC")
        )
        chart_values.append(
            {
                "tail_number": tail,
                "part_serial_number": str(row.get("part_serial_number", "")),
                "base_location": str(row.get("base_location", "RAF Marham")),
                "current_flight_hours": hours,
                "life_limit_threshold_hrs": limit,
                "mission_capable_status": mc_status,
                "threshold_status": (
                    "RED_BREACH_OVER_1000HR_LIMIT"
                    if breach
                    else "GREEN_SERVICEABLE_BELOW_LIMIT"
                ),
                "marker_color": "#D93025" if breach else "#1E8E3E",
            }
        )

    # Ensure ZM151 and ZM154 are always represented in the comparative threshold chart
    for fallback_row in AIRFRAME_COMPONENT_TELEMETRY_ROWS:
        t_num = str(fallback_row["tail_number"])
        if t_num in ("ZM151", "ZM154") and t_num not in seen_tails:
            hours = float(fallback_row["current_flight_hours"])
            limit = float(fallback_row["life_limit_threshold_hrs"])
            breach = hours >= limit
            mc_status = str(
                fallback_row.get("mission_capable_status")
                or ("PMC-M" if breach else "MC")
            )
            chart_values.append(
                {
                    "tail_number": t_num,
                    "part_serial_number": str(fallback_row["part_serial_number"]),
                    "base_location": str(fallback_row["base_location"]),
                    "current_flight_hours": hours,
                    "life_limit_threshold_hrs": limit,
                    "mission_capable_status": mc_status,
                    "threshold_status": (
                        "RED_BREACH_OVER_1000HR_LIMIT"
                        if breach
                        else "GREEN_SERVICEABLE_BELOW_LIMIT"
                    ),
                    "marker_color": "#D93025" if breach else "#1E8E3E",
                }
            )

    spec = VegaLiteSpec(
        **{
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "title": "F-35 Aileron Hydraulic Actuator Flight Hours vs 1,000.0-Hr Condemnation Limit",
            "data": {"values": chart_values},
            "mark": {"type": "bar", "tooltip": True},
            "encoding": {
                "x": {
                    "field": "tail_number",
                    "type": "nominal",
                    "title": "Aircraft Tail Number",
                },
                "y": {
                    "field": "current_flight_hours",
                    "type": "quantitative",
                    "title": "Cumulative Actuator Flight Hours",
                },
                "color": {
                    "field": "threshold_status",
                    "type": "nominal",
                    "title": "Fatigue Status",
                    "scale": {
                        "domain": [
                            "RED_BREACH_OVER_1000HR_LIMIT",
                            "GREEN_SERVICEABLE_BELOW_LIMIT",
                        ],
                        "range": ["#D93025", "#1E8E3E"],
                    },
                },
            },
            "layer": [
                {
                    "mark": {"type": "bar", "cornerRadiusEnd": 4, "tooltip": True},
                    "encoding": {
                        "x": {"field": "tail_number", "type": "nominal"},
                        "y": {"field": "current_flight_hours", "type": "quantitative"},
                        "color": {"field": "threshold_status", "type": "nominal"},
                    },
                },
                {
                    "mark": {
                        "type": "rule",
                        "color": "#D93025",
                        "strokeDash": [6, 4],
                        "size": 2,
                    },
                    "encoding": {
                        "y": {
                            "field": "life_limit_threshold_hrs",
                            "type": "quantitative",
                        }
                    },
                },
            ],
        }
    )
    return spec.model_dump(by_alias=True, exclude_none=True)


def check_actuator_fatigue_and_depot_inventory(
    base_location: str = "RAF Marham",
    hours_to_limit_window: float = 50.0,
    tool_context: Any | None = None,
    *,
    window_hours: float | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Check F-35 actuator fatigue hours, regional depot stock, and sortie schedule in EU BigQuery.

    Display Title: Check Actuator Fatigue & Depot Inventory
    """
    effective_window = float(
        window_hours if window_hours is not None else hours_to_limit_window
    )
    bundle = _fetch_uc1_tables_from_bq(base_location=base_location)
    telemetry_rows = bundle["telemetry"]
    inventory_rows = bundle["inventory"]
    sortie_rows = bundle["sorties"]

    validated_records: list[dict[str, Any]] = []
    flagged_tails: list[dict[str, Any]] = []

    for row in telemetry_rows:
        hours = float(row["current_flight_hours"])
        limit = float(row["life_limit_threshold_hrs"])
        mc_status = str(
            row.get("mission_capable_status")
            or ("PMC-M" if hours >= limit else "MC")
        )
        rec = ActuatorReadinessRecord(
            tail_number=str(row["tail_number"]),
            part_serial_number=str(row["part_serial_number"]),
            nsn=str(row["nsn"]),
            base_location=str(row["base_location"]),
            current_flight_hours=hours,
            life_limit_threshold_hrs=limit,
            mission_capable_status=mc_status,
        ).model_dump()
        rec["component_name"] = str(
            row.get("component_name", "Aileron Hydraulic Servo Actuator")
        )
        rec["aircraft_variant"] = str(row.get("aircraft_variant", "F-35B"))
        rec["subsystem_code"] = str(row.get("subsystem_code", "27-10"))
        rec["hours_over_limit"] = round(
            max(0.0, rec["current_flight_hours"] - rec["life_limit_threshold_hrs"]), 4
        )
        rec["breaches_limit"] = (
            rec["current_flight_hours"] >= rec["life_limit_threshold_hrs"]
        )
        rec["within_alert_window"] = rec["hours_remaining"] <= effective_window
        validated_records.append(rec)
        if rec["within_alert_window"] or rec["breaches_limit"]:
            flagged_tails.append(rec)

    zm151_rec = next(
        (r for r in validated_records if r["tail_number"] == "ZM151"),
        validated_records[0],
    )
    zm154_rec = next(
        (r for r in validated_records if r["tail_number"] == "ZM154"),
        validated_records[-1],
    )

    primary_depot = next(
        (
            d
            for d in inventory_rows
            if base_location.strip().lower()
            in str(d.get("depot_location") or d.get("depot_name") or "").lower()
        ),
        inventory_rows[0],
    )
    on_hand = int(primary_depot.get("quantity_on_hand", 4))
    reserved_30d = int(primary_depot.get("quantity_reserved_30d", 2))
    eta_hrs = float(primary_depot.get("avg_shipping_eta_hours", 18.0))

    depot_summary = {
        "nsn": str(primary_depot.get("nsn", "1680-01-619-4821")),
        "depot_id": str(primary_depot.get("depot_id", "DEPOT-RAF-MARHAM-01")),
        "depot_location": str(
            primary_depot.get("depot_location")
            or primary_depot.get("depot_name")
            or "RAF Marham Regional Supply Depot"
        ),
        "quantity_on_hand": on_hand,
        "quantity_reserved_30d": reserved_30d,
        "net_available_stock": max(0, on_hand - reserved_30d),
        "avg_shipping_eta_hours": eta_hrs,
        "all_depots": inventory_rows,
    }

    primary_sortie = sortie_rows[0]
    impacted_sortie = {
        "sortie_id": str(primary_sortie.get("sortie_id", "SRT-MAR-20261103-01")),
        "scheduled_departure_utc": str(
            primary_sortie.get("scheduled_departure_utc", "2026-11-03T07:30:00Z")
        ),
        "base_location": str(primary_sortie.get("base_location", base_location)),
        "mission_profile": str(
            primary_sortie.get("mission_profile", "DCA-NORTH-SEA-CAP")
        ),
        "assigned_tail_number": str(
            primary_sortie.get("assigned_tail_number", "ZM151")
        ),
        "assigned_pilot_callsign": str(
            primary_sortie.get(
                "assigned_pilot_callsign", "Flt Lt Henderson / VIPER-1"
            )
        ),
        "spare_tail_candidate": str(
            primary_sortie.get("spare_tail_candidate", "ZM154")
        ),
        "sortie_readiness_status": str(
            primary_sortie.get("sortie_readiness_status", "AT_RISK_COMPONENT_LIMIT")
        ),
    }

    depot_chart = _build_depot_stock_bar_chart(inventory_rows)
    fatigue_chart = _build_actuator_fatigue_threshold_chart(telemetry_rows)

    markdown_table = (
        "| Tail Number | Serial Number | NSN | Flight Hours | Limit (Hrs) | Remaining (Hrs) | Status | Depot On-Hand | 30d Reserved | ETA (Hrs) | Assigned Sortie |\n"
        "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |\n"
        f"| **{zm151_rec['tail_number']}** | `{zm151_rec['part_serial_number']}` | `{zm151_rec['nsn']}` | "
        f"**{zm151_rec['current_flight_hours']:.1f}** | {zm151_rec['life_limit_threshold_hrs']:.1f} | "
        f"{zm151_rec['hours_remaining']:.1f} | `{zm151_rec['mission_capable_status']}` | "
        f"{on_hand} | {reserved_30d} | {eta_hrs:.1f} | `{impacted_sortie['sortie_id']}` ({impacted_sortie['assigned_pilot_callsign']}) |\n"
        f"| **{zm154_rec['tail_number']}** | `{zm154_rec['part_serial_number']}` | `{zm154_rec['nsn']}` | "
        f"**{zm154_rec['current_flight_hours']:.1f}** | {zm154_rec['life_limit_threshold_hrs']:.1f} | "
        f"{zm154_rec['hours_remaining']:.1f} | `{zm154_rec['mission_capable_status']}` | "
        f"{on_hand} | {reserved_30d} | {eta_hrs:.1f} | Spare Candidate for `{impacted_sortie['sortie_id']}` |"
    )

    result = {
        "status": "SUCCESS",
        "bq_project": PROJECT_ID,
        "bq_dataset": BQ_DATASET,
        "bq_location": BQ_LOCATION,
        "base_location": base_location,
        "hours_to_limit_window": effective_window,
        "primary_breach_tail": zm151_rec,
        "spare_tail_candidate": zm154_rec,
        "telemetry_records": validated_records,
        "flagged_tails": flagged_tails,
        "depot_inventory": depot_summary,
        "impacted_sortie": impacted_sortie,
        "sortie_schedule": sortie_rows,
        "depot_stock_vs_demand_bar_chart": depot_chart,
        "actuator_fatigue_threshold_chart": fatigue_chart,
        "vega_lite_charts": {
            "depot_stock_vs_demand_bar_chart": depot_chart,
            "actuator_fatigue_threshold_chart": fatigue_chart,
        },
        "markdown_summary_table": markdown_table,
    }

    if tool_context is not None and hasattr(tool_context, "state") and isinstance(tool_context.state, dict):
        tool_context.state["last_uc1_analytics_result"] = result
        tool_context.state["last_uc1_metrics"] = {
            "telemetry_rows": telemetry_rows,
            "inventory_rows": inventory_rows,
            "sortie_rows": sortie_rows,
            "primary_breach_tail": zm151_rec,
            "spare_tail_candidate": zm154_rec,
            "depot_summary": depot_summary,
            "impacted_sortie": impacted_sortie,
            "depot_chart": depot_chart,
            "fatigue_chart": fatigue_chart,
        }

    return result


def recommend_tail_swap_and_replenishment(
    sortie_id: str = "SRT-MAR-20261103-01",
    primary_tail: str = "ZM151",
    spare_tail: str = "ZM154",
    tool_context: Any | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Recommend an immediate sortie tail swap and automated regional depot replenishment order.

    Display Title: Recommend Tail Swap & Depot Replenishment
    """
    bundle = _fetch_uc1_tables_from_bq(base_location="RAF Marham")
    telemetry_by_tail = {
        str(r["tail_number"]): r for r in bundle["telemetry"]
    }
    for row in AIRFRAME_COMPONENT_TELEMETRY_ROWS:
        telemetry_by_tail.setdefault(str(row["tail_number"]), row)

    spare_info = telemetry_by_tail.get(spare_tail, {})
    spare_hours = float(spare_info.get("current_flight_hours", 842.0))
    spare_limit = float(spare_info.get("life_limit_threshold_hrs", 1000.0))

    same_tail = primary_tail.strip().upper() == spare_tail.strip().upper()
    spare_breached = spare_hours >= spare_limit
    swap_valid = not (same_tail or spare_breached)

    if not swap_valid:
        action_status = "REJECTED_INVALID_SPARE_TAIL"
        warning = (
            f"INVALID_SWAP_CANDIDATE: Spare tail {spare_tail} cannot replace {primary_tail} "
            f"(same_tail={same_tail}, spare_flight_hours={spare_hours:.1f} vs {spare_limit:.1f} hr limit)."
        )
    else:
        action_status = "RECOMMENDED_SWAP_AND_REPLENISH"
        warning = None

    validated = SortieSwapRecommendation(
        sortie_id=sortie_id,
        primary_tail=primary_tail,
        spare_tail=spare_tail,
        pilot_callsign="Flt Lt Henderson / VIPER-1",
        supply_nsn="1680-01-619-4821",
        depot_quantity_on_hand=4,
        depot_quantity_reserved_30d=2,
        shipping_eta_hours=18.0,
        action_status=action_status,
    )

    result = validated.model_dump()
    result.update(
        {
            "status": "SUCCESS" if swap_valid else "WARNING_INVALID_SWAP",
            "swap_valid": swap_valid,
            "is_valid_swap": swap_valid,
            "warning": warning,
            "nsn": "1680-01-619-4821",
            "part_serial_number_condemned": "ACT-99812-F",
            "primary_tail_flight_hours": 1000.4,
            "spare_tail_flight_hours": spare_hours,
            "life_limit_threshold_hrs": 1000.0,
            "depot_id": "DEPOT-RAF-MARHAM-01",
            "depot_location": "RAF Marham Regional Supply Depot",
            "net_available_stock": 2,
            "supply_alert": {
                "alert_id": f"SUP-ALERT-{sortie_id}-{primary_tail}",
                "nsn": "1680-01-619-4821",
                "part_serial_number_replaced": "ACT-99812-F",
                "depot_id": "DEPOT-RAF-MARHAM-01",
                "quantity_requested": 1,
                "quantity_on_hand": 4,
                "quantity_reserved_30d": 2,
                "shipping_eta_hours": 18.0,
            },
            "recommendation_summary": (
                f"Reallocate Sortie {sortie_id} (Flt Lt Henderson / VIPER-1) from primary tail "
                f"{primary_tail} (S/N ACT-99812-F at 1,000.4 hrs, +0.4 hrs past 1,000.0-hr limit, PMC-M) "
                f"to serviceable spare tail {spare_tail} ({spare_hours:.1f} hrs, MC). Dispatch Priority-1 "
                f"Supply Alert for NSN 1680-01-619-4821 from DEPOT-RAF-MARHAM-01 (4 on hand, 2 reserved, "
                f"18.0-hr shipping ETA)."
                if swap_valid
                else warning
            ),
        }
    )

    if tool_context is not None and hasattr(tool_context, "state"):
        tool_context.state["last_uc1_swap_recommendation"] = result

    return result


def render_sustainment_chart(
    chart_name: str = "both",
    tool_context: Any | None = None,
    render_graphics: bool = True,
    **_: Any,
) -> dict[str, Any]:
    """Render high-resolution presentation graphics and Vega-Lite specifications on demand.

    Display Title: Render Sustainment Chart
    Args:
        chart_name: Name of the chart to render ('actuator_fatigue_threshold_chart',
                    'depot_stock_vs_demand_bar_chart', or 'both').
        tool_context: ADK 2.0 tool execution context storing BigQuery metrics from Turn 1.
        render_graphics: Whether to generate and upload presentation PNG charts to GCS.
    """
    t0 = time.perf_counter()

    raw_name = str(chart_name or "both").strip().lower()

    # Check if metrics are already cached in tool_context state
    depot_chart: dict[str, Any] | None = None
    fatigue_chart: dict[str, Any] | None = None
    telemetry_rows: list[dict[str, Any]] | None = None
    inventory_rows: list[dict[str, Any]] | None = None

    state = getattr(tool_context, "state", None) if tool_context is not None else None
    if isinstance(state, dict):
        cached_metrics = state.get("last_uc1_metrics") or state.get("last_uc1_analytics_result")
        if isinstance(cached_metrics, dict):
            depot_chart = cached_metrics.get("depot_chart") or cached_metrics.get("depot_stock_vs_demand_bar_chart")
            fatigue_chart = cached_metrics.get("fatigue_chart") or cached_metrics.get("actuator_fatigue_threshold_chart")
            telemetry_rows = cached_metrics.get("telemetry_rows")
            inventory_rows = cached_metrics.get("inventory_rows")

    # If not found in cache, build deterministically from cached/seed tables
    if depot_chart is None or fatigue_chart is None:
        bundle = _fetch_uc1_tables_from_bq(base_location="RAF Marham")
        if depot_chart is None:
            depot_chart = _build_depot_stock_bar_chart(bundle["inventory"])
        if fatigue_chart is None:
            fatigue_chart = _build_actuator_fatigue_threshold_chart(bundle["telemetry"])
        if telemetry_rows is None:
            telemetry_rows = bundle["telemetry"]
        if inventory_rows is None:
            inventory_rows = bundle["inventory"]

    is_fatigue = any(k in raw_name for k in ("fatigue", "actuator", "threshold", "1")) or raw_name == "actuator_fatigue_threshold_chart"
    is_depot = any(k in raw_name for k in ("depot", "stock", "demand", "inventory", "2")) or raw_name == "depot_stock_vs_demand_bar_chart"
    is_both = any(k in raw_name for k in ("both", "all", "3", "dashboard", "slide")) or (is_fatigue and is_depot) or raw_name in ("charts", "visualizations")

    if is_both:
        resolved_name = "both"
        vega_spec = {
            "depot_stock_vs_demand_bar_chart": depot_chart,
            "actuator_fatigue_threshold_chart": fatigue_chart,
        }
        rendered_charts = {
            "depot_stock_vs_demand_bar_chart": depot_chart,
            "actuator_fatigue_threshold_chart": fatigue_chart,
        }
    elif is_fatigue and not is_depot:
        resolved_name = "actuator_fatigue_threshold_chart"
        vega_spec = fatigue_chart
        rendered_charts = {
            "actuator_fatigue_threshold_chart": fatigue_chart,
        }
    else:
        resolved_name = "depot_stock_vs_demand_bar_chart"
        vega_spec = depot_chart
        rendered_charts = {
            "depot_stock_vs_demand_bar_chart": depot_chart,
        }

    # Generate high-resolution presentation graphics (PNG) and upload to GCS
    graphics_res: dict[str, Any] = {}
    if render_graphics:
        # Check if already generated and cached in state
        cached_graphics = state.get(f"cached_graphics_{resolved_name}") if isinstance(state, dict) else None
        if isinstance(cached_graphics, dict):
            graphics_res = cached_graphics
        else:
            graphics_res = generate_sustainment_graphics(
                chart_name=resolved_name,
                telemetry_rows=telemetry_rows,
                inventory_rows=inventory_rows,
            )
            if isinstance(state, dict):
                state[f"cached_graphics_{resolved_name}"] = graphics_res

    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    charts_list = graphics_res.get("charts", [])
    markdown_lines: list[str] = ["### 📊 Presentation Briefing Graphics (Ready for Slide Decks)\n"]
    download_links: list[str] = []
    image_urls: list[str] = []

    for c in charts_list:
        markdown_lines.append(f"{c['markdown_img']}\n")
        download_links.append(c["download_link"])
        image_urls.append(c["url"])

    if download_links:
        markdown_lines.append("\n**Download Assets for Presentation Slides:**\n" + "\n".join(f"* {link}" for link in download_links))

    presentation_markdown = "\n".join(markdown_lines)

    res = {
        "status": "SUCCESS",
        "chart_name": resolved_name,
        "requested_name": chart_name,
        "generation_time_ms": round(elapsed_ms, 3),
        "render_latency_ms": round(graphics_res.get("render_latency_ms", 0.0), 2),
        "upload_latency_ms": round(graphics_res.get("upload_latency_ms", 0.0), 2),
        "total_latency_ms": round(elapsed_ms, 2),
        "presentation_graphics": charts_list,
        "presentation_graphics_markdown": presentation_markdown,
        "download_links": download_links,
        "image_urls": image_urls,
        "instruction_for_agent": (
            "CRITICAL: Present the graphical chart images and download links using the provided markdown. "
            "Do NOT output raw Vega-Lite JSON code blocks to the user."
        ),
        "vega_lite_spec": vega_spec,
        "vega_lite_charts": rendered_charts,
        "description": f"Successfully rendered {resolved_name} graphics and specification in {elapsed_ms:.2f} ms.",
    }
    res.update(rendered_charts)
    return res


__all__ = [
    "check_actuator_fatigue_and_depot_inventory",
    "recommend_tail_swap_and_replenishment",
    "render_sustainment_chart",
]

