"""Domain tools package for UC1 Analytics, UC2 JTD Search, and UC3 Airworthiness."""

from __future__ import annotations

from app.tools.uc1_analytics import (
    check_actuator_fatigue_and_depot_inventory,
    recommend_tail_swap_and_replenishment,
)
from app.tools.uc2_jtd_search import (
    normalize_cross_service_terminology,
    search_technical_manuals_and_repair_logs,
)
from app.tools.uc3_airworthiness import (
    approve_form700_engineering_release,
    assess_airframe_airworthiness,
    audit_fastener_lot_in_mbom,
    calculate_structural_fatigue_and_yield,
    confirm_form700_hitl_release,
    generate_form700_airworthiness_package,
    inspect_ultrasonic_cscan_and_map_cad,
    sync_flight_telemetry_exceedance,
)

__all__ = [
    "approve_form700_engineering_release",
    "assess_airframe_airworthiness",
    "audit_fastener_lot_in_mbom",
    "calculate_structural_fatigue_and_yield",
    "check_actuator_fatigue_and_depot_inventory",
    "confirm_form700_hitl_release",
    "generate_form700_airworthiness_package",
    "inspect_ultrasonic_cscan_and_map_cad",
    "normalize_cross_service_terminology",
    "recommend_tail_swap_and_replenishment",
    "search_technical_manuals_and_repair_logs",
    "sync_flight_telemetry_exceedance",
]
