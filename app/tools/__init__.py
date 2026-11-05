"""Domain tools package for UC0 Maintenance Data, UC1 Analytics, and UC2 JTD Search."""

from __future__ import annotations

from app.tools.uc0_maintenance import (
    canonicalize_maintenance_sql,
    execute_maintenance_sql,
    validate_and_rewrite_maintenance_sql,
)
from app.tools.uc1_analytics import (
    check_actuator_fatigue_and_depot_inventory,
    recommend_tail_swap_and_replenishment,
    render_sustainment_chart,
)
from app.tools.uc2_jtd_search import (
    normalize_cross_service_terminology,
    search_technical_manuals_and_repair_logs,
)

__all__ = [
    "canonicalize_maintenance_sql",
    "check_actuator_fatigue_and_depot_inventory",
    "execute_maintenance_sql",
    "normalize_cross_service_terminology",
    "recommend_tail_swap_and_replenishment",
    "render_sustainment_chart",
    "search_technical_manuals_and_repair_logs",
    "validate_and_rewrite_maintenance_sql",
]
