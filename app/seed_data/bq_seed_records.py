"""Authoritative BigQuery seed records for Tables 1-6 in antig-dave.ukd_f35_sustainment_demo (EU)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

SCHEMAS_DIR = Path(__file__).resolve().parent / "schemas"

# Table 1: airframe_component_telemetry
AIRFRAME_COMPONENT_TELEMETRY_ROWS: list[dict[str, Any]] = [
    {
        "telemetry_record_id": "TEL-ZM151-ACT-99812",
        "tail_number": "ZM151",
        "aircraft_variant": "F-35B",
        "base_location": "RAF Marham",
        "part_serial_number": "ACT-99812-F",
        "nsn": "1680-01-619-4821",
        "component_name": "Port Electro-Hydrostatic Actuator (EHA)",
        "current_flight_hours": 1000.4,
        "life_limit_threshold_hrs": 1000.0,
    },
    {
        "telemetry_record_id": "TEL-ZM154-ACT-88401",
        "tail_number": "ZM154",
        "aircraft_variant": "F-35B",
        "base_location": "RAF Marham",
        "part_serial_number": "ACT-88401-B",
        "nsn": "1680-01-619-4821",
        "component_name": "Port Electro-Hydrostatic Actuator (EHA)",
        "current_flight_hours": 842.0,
        "life_limit_threshold_hrs": 1000.0,
    },
    {
        "telemetry_record_id": "TEL-ZM152-ACT-91204",
        "tail_number": "ZM152",
        "aircraft_variant": "F-35B",
        "base_location": "RAF Marham",
        "part_serial_number": "ACT-91204-A",
        "nsn": "1680-01-619-4821",
        "component_name": "Port Electro-Hydrostatic Actuator (EHA)",
        "current_flight_hours": 964.5,
        "life_limit_threshold_hrs": 1000.0,
    },
    {
        "telemetry_record_id": "TEL-ZM158-ACT-77510",
        "tail_number": "ZM158",
        "aircraft_variant": "F-35B",
        "base_location": "HMS Queen Elizabeth",
        "part_serial_number": "ACT-77510-C",
        "nsn": "1680-01-619-4821",
        "component_name": "Port Electro-Hydrostatic Actuator (EHA)",
        "current_flight_hours": 918.2,
        "life_limit_threshold_hrs": 1000.0,
    },
    {
        "telemetry_record_id": "TEL-ZM159-ACT-77542",
        "tail_number": "ZM159",
        "aircraft_variant": "F-35B",
        "base_location": "HMS Queen Elizabeth",
        "part_serial_number": "ACT-77542-D",
        "nsn": "1680-01-619-4821",
        "component_name": "Port Electro-Hydrostatic Actuator (EHA)",
        "current_flight_hours": 610.0,
        "life_limit_threshold_hrs": 1000.0,
    },
]

# Table 2: global_depot_inventory
GLOBAL_DEPOT_INVENTORY_ROWS: list[dict[str, Any]] = [
    {
        "nsn": "1680-01-619-4821",
        "part_name": "Port Electro-Hydrostatic Actuator (EHA)",
        "depot_id": "DEPOT-MAR-01",
        "depot_name": "RAF Marham Regional Sustainment Hub",
        "quantity_on_hand": 4,
        "quantity_reserved_30d": 2,
        "reorder_point_threshold": 3,
        "avg_shipping_eta_hours": 18.0,
    },
    {
        "nsn": "1680-01-619-4821",
        "part_name": "Port Electro-Hydrostatic Actuator (EHA)",
        "depot_id": "DEPOT-QNLZ-02",
        "depot_name": "HMS Queen Elizabeth Afloat Spares",
        "quantity_on_hand": 2,
        "quantity_reserved_30d": 1,
        "reorder_point_threshold": 2,
        "avg_shipping_eta_hours": 36.0,
    },
]

# Table 3: squadron_sortie_schedule
SQUADRON_SORTIE_SCHEDULE_ROWS: list[dict[str, Any]] = [
    {
        "sortie_id": "SRT-MAR-20261103-01",
        "scheduled_departure_utc": "2026-11-03T06:30:00Z",
        "assigned_tail_number": "ZM151",
        "assigned_pilot_callsign": "Flt Lt Henderson / VIPER-1",
        "spare_tail_candidate": "ZM154",
        "sortie_readiness_status": "PMC-M",
    },
    {
        "sortie_id": "SRT-MAR-20261103-02",
        "scheduled_departure_utc": "2026-11-03T08:00:00Z",
        "assigned_tail_number": "ZM154",
        "assigned_pilot_callsign": "Sqn Ldr Davies / VIPER-2",
        "spare_tail_candidate": "ZM152",
        "sortie_readiness_status": "MC",
    },
    {
        "sortie_id": "SRT-QNLZ-20261103-01",
        "scheduled_departure_utc": "2026-11-03T09:15:00Z",
        "assigned_tail_number": "ZM158",
        "assigned_pilot_callsign": "Lt Cdr Vance / BROADSWORD-1",
        "spare_tail_candidate": "ZM159",
        "sortie_readiness_status": "MC",
    },
]

# Table 4: high_freq_strain_telemetry
HIGH_FREQ_STRAIN_TELEMETRY_ROWS: list[dict[str, Any]] = [
    {
        "event_id": "EXC-20261102-ZM151",
        "tail_number": "ZM151",
        "event_window_start_utc": "2026-11-02T14:22:18.420Z",
        "structural_station_id": "Frame 496",
        "mach_number": 1.3,
        "peak_nz_g": 9.4,
        "peak_egt_celsius": 220.0,
        "miners_rule_damage_delta": 0.0042,
        "calculated_yield_pct": 104.2,
        "required_ndi_class": "CLASS_A_ULTRASONIC_C_SCAN",
    },
    {
        "event_id": "EXC-20261028-ZM154",
        "tail_number": "ZM154",
        "event_window_start_utc": "2026-10-28T11:10:05.100Z",
        "structural_station_id": "Frame 496",
        "mach_number": 1.05,
        "peak_nz_g": 7.1,
        "peak_egt_celsius": 165.0,
        "miners_rule_damage_delta": 0.0008,
        "calculated_yield_pct": 78.4,
        "required_ndi_class": "NONE",
    },
]

# Table 5: as_maintained_mbom_fasteners
AS_MAINTAINED_MBOM_FASTENERS_ROWS: list[dict[str, Any]] = [
    {
        "mbom_record_id": "MBOM-ZM151-F496-H14",
        "tail_number": "ZM151",
        "station_id": "Frame 496 — Fastener Hole #14",
        "fastener_material_spec": "Ti-6Al-4V",
        "fastener_lot_number": "Lot #8841-B",
        "hours_since_install": 312.0,
        "allowable_elongation_in": 0.015,
        "measured_ndi_elongation_in": 0.012,
        "global_fleet_affected_count": 14,
    },
    {
        "mbom_record_id": "MBOM-ZM151-F496-H15",
        "tail_number": "ZM151",
        "station_id": "Frame 496 — Fastener Hole #15",
        "fastener_material_spec": "Ti-6Al-4V",
        "fastener_lot_number": "Lot #8841-B",
        "hours_since_install": 312.0,
        "allowable_elongation_in": 0.015,
        "measured_ndi_elongation_in": 0.003,
        "global_fleet_affected_count": 14,
    },
    {
        "mbom_record_id": "MBOM-ZM154-F496-H14",
        "tail_number": "ZM154",
        "station_id": "Frame 496 — Fastener Hole #14",
        "fastener_material_spec": "Ti-6Al-4V",
        "fastener_lot_number": "Lot #8841-B",
        "hours_since_install": 198.5,
        "allowable_elongation_in": 0.015,
        "measured_ndi_elongation_in": 0.002,
        "global_fleet_affected_count": 14,
    },
]

# Table 6: airworthiness_release_ledger
AIRWORTHINESS_RELEASE_LEDGER_ROWS: list[dict[str, Any]] = [
    {
        "release_package_id": "AWR-700-20261102-ZM151",
        "appraisal_report_uri": (
            "gs://antig-dave-f35-staging-europe-west1/unstructured/sar/SAR-20261102-ZM151.pdf"
        ),
        "mandated_jtd_task_card": "JTD Task Card 53-11-00-280",
        "disposition_status": "SERVICEABLE_WITH_TORQUE_RECHECK",
        "hitl_reviewer_role": "Lead Stress Engineer",
        "hitl_review_status": "PENDING_HITL_REVIEW",
        "compliance_standard": "MIL-STD-3001 / DEF STAN 00-970",
    },
]

BQ_SEED_TABLES: dict[str, list[dict[str, Any]]] = {
    "airframe_component_telemetry": AIRFRAME_COMPONENT_TELEMETRY_ROWS,
    "global_depot_inventory": GLOBAL_DEPOT_INVENTORY_ROWS,
    "squadron_sortie_schedule": SQUADRON_SORTIE_SCHEDULE_ROWS,
    "high_freq_strain_telemetry": HIGH_FREQ_STRAIN_TELEMETRY_ROWS,
    "as_maintained_mbom_fasteners": AS_MAINTAINED_MBOM_FASTENERS_ROWS,
    "airworthiness_release_ledger": AIRWORTHINESS_RELEASE_LEDGER_ROWS,
}


def get_seed_rows(table_name: str) -> list[dict[str, Any]]:
    """Return a copy of the authoritative seed rows for the specified BigQuery table."""
    if table_name not in BQ_SEED_TABLES:
        raise KeyError(f"Unknown BigQuery seed table: {table_name}")
    return [dict(row) for row in BQ_SEED_TABLES[table_name]]
