"""Authoritative BigQuery seed records for Tables 1-7 in antig-dave.ukd_f35_sustainment_demo (EU)."""

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

# Table 7: maintenance_work_orders
MAINTENANCE_WORK_ORDERS_ROWS: list[dict[str, Any]] = [
    {
        "work_order_id": "WO-2026-88401",
        "tail_number": "ZM151",
        "aircraft_variant": "F-35B",
        "squadron": "617 Sqn (The Dambusters)",
        "base_location": "RAF Marham",
        "aircraft_status": "PMC-M",
        "work_order_status": "OPEN",
        "priority": "PRIORITY_2_URGENT",
        "work_center": "FLIGHT_LINE",
        "wuc_code": "27-10",
        "subsystem_name": "Electro-Hydrostatic Actuator (Flaperon)",
        "discrepancy_narrative": (
            "PHM Advisory: Right flaperon EHA S/N ACT-99812-F logged 1,000.4 cumulative "
            "high-load hours (exceeds 1,000.0 hr overhaul limit)."
        ),
        "corrective_action": (
            "Scheduled for bay replacement; checking RAF Marham depot stock for NSN 1680-01-619-4821."
        ),
        "awaiting_part_nsn": "1680-01-619-4821",
        "assigned_shift_lead": "Chf Tech M. Davies",
        "estimated_mttr_hours": 4.5,
        "logged_man_hours": 1.2,
        "created_at_utc": "2026-11-02T19:10:00Z",
    },
    {
        "work_order_id": "WO-2026-88402",
        "tail_number": "ZM151",
        "aircraft_variant": "F-35B",
        "squadron": "617 Sqn (The Dambusters)",
        "base_location": "RAF Marham",
        "aircraft_status": "PMC-M",
        "work_order_status": "IN_PROGRESS",
        "priority": "PRIORITY_2_URGENT",
        "work_center": "FLIGHT_LINE",
        "wuc_code": "53-30",
        "subsystem_name": "Forward Fuselage Canopy Latch",
        "discrepancy_narrative": (
            "Forward canopy locking catch exhibits mechanical binding during pre-flight closure "
            "check; zero BIT fault codes active."
        ),
        "corrective_action": (
            "Inspecting canopy forward locking hook and Fluorosilicone seal swell per JTD DM-53-30-04."
        ),
        "awaiting_part_nsn": None,
        "assigned_shift_lead": "Sgt R. Patel",
        "estimated_mttr_hours": 2.5,
        "logged_man_hours": 1.5,
        "created_at_utc": "2026-11-02T20:05:00Z",
    },
    {
        "work_order_id": "WO-2026-88403",
        "tail_number": "ZM151",
        "aircraft_variant": "F-35B",
        "squadron": "617 Sqn (The Dambusters)",
        "base_location": "RAF Marham",
        "aircraft_status": "PMC-M",
        "work_order_status": "AWAITING_ENGINEERING_DISPOSITION",
        "priority": "PRIORITY_1_RED_X",
        "work_center": "STRUCTURES_LO",
        "wuc_code": "53-20",
        "subsystem_name": "Center Fuselage Frame 496 Bulkhead",
        "discrepancy_narrative": (
            "Post-sortie SRT-MAR-20261102-09 7.8G pull (98.4% design yield) and NDI ultrasonic "
            "C-scan anomaly at FS 496.0, WL 112.4."
        ),
        "corrective_action": (
            "Ultrasonic C-scan image DOC-06 captured; awaiting ASIP Miner's Rule fatigue analysis "
            "and Form 700 HITL disposition."
        ),
        "awaiting_part_nsn": None,
        "assigned_shift_lead": "FSgt A. Wallace",
        "estimated_mttr_hours": 12.0,
        "logged_man_hours": 3.8,
        "created_at_utc": "2026-11-02T21:18:00Z",
    },
    {
        "work_order_id": "WO-2026-88404",
        "tail_number": "ZM152",
        "aircraft_variant": "F-35B",
        "squadron": "617 Sqn (The Dambusters)",
        "base_location": "RAF Marham",
        "aircraft_status": "NMC-S",
        "work_order_status": "AWAITING_PARTS (MICAP)",
        "priority": "PRIORITY_1_RED_X",
        "work_center": "AVIONICS",
        "wuc_code": "34-40",
        "subsystem_name": "AN/APG-81 AESA Radar Array",
        "discrepancy_narrative": (
            "BIT Fault APG-81-4402: Transmit/Receive module bank 3 power supply drop during "
            "ground power-on self-test."
        ),
        "corrective_action": (
            "Awaiting MICAP shipment of Low Voltage Power Supply assembly from Lakenheath regional hub."
        ),
        "awaiting_part_nsn": "5841-01-642-9910",
        "assigned_shift_lead": "Chf Tech K. Lindqvist",
        "estimated_mttr_hours": 6.0,
        "logged_man_hours": 2.4,
        "created_at_utc": "2026-11-01T14:20:00Z",
    },
    {
        "work_order_id": "WO-2026-88405",
        "tail_number": "ZM153",
        "aircraft_variant": "F-35B",
        "squadron": "617 Sqn (The Dambusters)",
        "base_location": "RAF Marham",
        "aircraft_status": "NMC-M",
        "work_order_status": "IN_PROGRESS",
        "priority": "PRIORITY_1_RED_X",
        "work_center": "PROPULSION",
        "wuc_code": "72-30",
        "subsystem_name": "F135-PW-600 LiftFan Clutch Assembly",
        "discrepancy_narrative": (
            "LiftFan shaft vibration exceedance (1.4 ips) recorded during STOVL hover conversion check."
        ),
        "corrective_action": (
            "Performing borescope inspection and dynamic balance calibration on LiftFan drive shaft."
        ),
        "awaiting_part_nsn": None,
        "assigned_shift_lead": "WO1 D. MacLeod",
        "estimated_mttr_hours": 14.5,
        "logged_man_hours": 8.0,
        "created_at_utc": "2026-11-01T09:30:00Z",
    },
    {
        "work_order_id": "WO-2026-88406",
        "tail_number": "ZM154",
        "aircraft_variant": "F-35B",
        "squadron": "617 Sqn (The Dambusters)",
        "base_location": "RAF Marham",
        "aircraft_status": "FMC",
        "work_order_status": "COMPLETED",
        "priority": "PRIORITY_3_ROUTINE",
        "work_center": "FLIGHT_LINE",
        "wuc_code": "27-10",
        "subsystem_name": "Electro-Hydrostatic Actuator (Flaperon)",
        "discrepancy_narrative": (
            "Routine 850-hour PHM telemetry verification on EHA S/N ACT-88410-B (842.0 hrs logged)."
        ),
        "corrective_action": (
            "Verified zero fluid bypass and nominal pressure response; cleared as serviceable spare aircraft."
        ),
        "awaiting_part_nsn": None,
        "assigned_shift_lead": "Chf Tech M. Davies",
        "estimated_mttr_hours": 1.5,
        "logged_man_hours": 1.4,
        "created_at_utc": "2026-11-02T16:00:00Z",
    },
    {
        "work_order_id": "WO-2026-88407",
        "tail_number": "ZM155",
        "aircraft_variant": "F-35B",
        "squadron": "617 Sqn (The Dambusters)",
        "base_location": "RAF Marham",
        "aircraft_status": "FMC",
        "work_order_status": "COMPLETED",
        "priority": "PRIORITY_3_ROUTINE",
        "work_center": "STRUCTURES_LO",
        "wuc_code": "51-10",
        "subsystem_name": "Weapon Bay Door Outer Mold Line LO Coating",
        "discrepancy_narrative": (
            "Minor edge erosion on left internal weapons bay door RAM tape after inclement weather sortie."
        ),
        "corrective_action": (
            "Applied quick-cure low-observable conductive sealant patch; verified RCS signature within limits."
        ),
        "awaiting_part_nsn": None,
        "assigned_shift_lead": "Sgt T. O'Connor",
        "estimated_mttr_hours": 3.0,
        "logged_man_hours": 2.8,
        "created_at_utc": "2026-11-02T11:45:00Z",
    },
    {
        "work_order_id": "WO-2026-88408",
        "tail_number": "ZM156",
        "aircraft_variant": "F-35B",
        "squadron": "809 NAS (The Immortals)",
        "base_location": "HMS Queen Elizabeth",
        "aircraft_status": "NMC-S",
        "work_order_status": "AWAITING_PARTS (MICAP)",
        "priority": "PRIORITY_1_RED_X",
        "work_center": "FLIGHT_LINE",
        "wuc_code": "27-10",
        "subsystem_name": "Electro-Hydrostatic Actuator (Flaperon)",
        "discrepancy_narrative": (
            "Port flaperon actuator S/N ACT-99704-A internal seal leak detected on carrier flight deck."
        ),
        "corrective_action": (
            "MICAP requisition submitted for NSN 1680-01-619-4821; awaiting COD airlift to HMS Queen Elizabeth."
        ),
        "awaiting_part_nsn": "1680-01-619-4821",
        "assigned_shift_lead": "POAET J. Stirling",
        "estimated_mttr_hours": 5.0,
        "logged_man_hours": 2.0,
        "created_at_utc": "2026-11-02T07:15:00Z",
    },
    {
        "work_order_id": "WO-2026-88409",
        "tail_number": "ZM157",
        "aircraft_variant": "F-35B",
        "squadron": "809 NAS (The Immortals)",
        "base_location": "HMS Queen Elizabeth",
        "aircraft_status": "PMC-M",
        "work_order_status": "IN_PROGRESS",
        "priority": "PRIORITY_2_URGENT",
        "work_center": "AVIONICS",
        "wuc_code": "94-10",
        "subsystem_name": "Electro-Optical Targeting System (EOTS)",
        "discrepancy_narrative": (
            "Condensation trace observed inside EOTS sapphire window assembly following rapid carrier deck recovery."
        ),
        "corrective_action": (
            "Purging optical cavity with dry nitrogen and verifying laser designator boresight alignment."
        ),
        "awaiting_part_nsn": None,
        "assigned_shift_lead": "LAET S. Krishnan",
        "estimated_mttr_hours": 3.5,
        "logged_man_hours": 1.8,
        "created_at_utc": "2026-11-02T15:10:00Z",
    },
    {
        "work_order_id": "WO-2026-88410",
        "tail_number": "ZM158",
        "aircraft_variant": "F-35B",
        "squadron": "809 NAS (The Immortals)",
        "base_location": "HMS Queen Elizabeth",
        "aircraft_status": "FMC",
        "work_order_status": "COMPLETED",
        "priority": "PRIORITY_3_ROUTINE",
        "work_center": "FLIGHT_LINE",
        "wuc_code": "32-40",
        "subsystem_name": "Main Landing Gear Carbon Brake Pack",
        "discrepancy_narrative": "Scheduled carrier arrestment/STOVL brake wear pin gauge measurement.",
        "corrective_action": "Wear pin at 68% remaining life; logged in ODIN and released for flight operations.",
        "awaiting_part_nsn": None,
        "assigned_shift_lead": "POAET J. Stirling",
        "estimated_mttr_hours": 1.0,
        "logged_man_hours": 0.9,
        "created_at_utc": "2026-11-01T18:30:00Z",
    },
    {
        "work_order_id": "WO-2026-88411",
        "tail_number": "ZM159",
        "aircraft_variant": "F-35B",
        "squadron": "809 NAS (The Immortals)",
        "base_location": "HMS Queen Elizabeth",
        "aircraft_status": "NMC-M",
        "work_order_status": "OPEN",
        "priority": "PRIORITY_1_RED_X",
        "work_center": "PROPULSION",
        "wuc_code": "72-50",
        "subsystem_name": "3-Bearing Swivel Duct Nozzle Actuator",
        "discrepancy_narrative": (
            "3BSD pitch nozzle actuator feedback RVDT sensor discrepancy during deck spot movement."
        ),
        "corrective_action": (
            "Troubleshooting harness continuity between 3BSD RVDT channel B and propulsion control module."
        ),
        "awaiting_part_nsn": None,
        "assigned_shift_lead": "CPOAET H. Evans",
        "estimated_mttr_hours": 8.0,
        "logged_man_hours": 1.5,
        "created_at_utc": "2026-11-02T20:40:00Z",
    },
    {
        "work_order_id": "WO-2026-88412",
        "tail_number": "ZM160",
        "aircraft_variant": "F-35B",
        "squadron": "207 Sqn (OCU)",
        "base_location": "RAF Marham",
        "aircraft_status": "PMC-M",
        "work_order_status": "OPEN",
        "priority": "PRIORITY_2_URGENT",
        "work_center": "ARMAMENT",
        "wuc_code": "91-20",
        "subsystem_name": "BRU-68/A Pneumatic Bomb Rack Unit",
        "discrepancy_narrative": (
            "Station 4 BRU-68/A ejector hook failed to latch during weapons loading trainer drill."
        ),
        "corrective_action": "Removed rack for bench pneumatic leak test and solenoid valve inspection.",
        "awaiting_part_nsn": "1095-01-598-3321",
        "assigned_shift_lead": "FSgt L. Becker",
        "estimated_mttr_hours": 4.0,
        "logged_man_hours": 1.1,
        "created_at_utc": "2026-11-02T13:20:00Z",
    },
    {
        "work_order_id": "WO-2026-88413",
        "tail_number": "ZM161",
        "aircraft_variant": "F-35B",
        "squadron": "207 Sqn (OCU)",
        "base_location": "RAF Marham",
        "aircraft_status": "FMC",
        "work_order_status": "COMPLETED",
        "priority": "PRIORITY_3_ROUTINE",
        "work_center": "AVIONICS",
        "wuc_code": "42-10",
        "subsystem_name": "Integrated Core Processor (ICP) Rack",
        "discrepancy_narrative": (
            "Loaded Operational Flight Program (OFP) Block 4 maintenance patch and verified cryptographic keys."
        ),
        "corrective_action": "OFP checksum verified across dual ICP channels; aircraft FMC.",
        "awaiting_part_nsn": None,
        "assigned_shift_lead": "Chf Tech K. Lindqvist",
        "estimated_mttr_hours": 2.0,
        "logged_man_hours": 1.7,
        "created_at_utc": "2026-11-01T11:00:00Z",
    },
    {
        "work_order_id": "WO-2026-88414",
        "tail_number": "ZM162",
        "aircraft_variant": "F-35B",
        "squadron": "207 Sqn (OCU)",
        "base_location": "RAF Marham",
        "aircraft_status": "NMC-S",
        "work_order_status": "AWAITING_PARTS (MICAP)",
        "priority": "PRIORITY_1_RED_X",
        "work_center": "STRUCTURES_LO",
        "wuc_code": "53-30",
        "subsystem_name": "Canopy Forward Locking Hook Assembly",
        "discrepancy_narrative": (
            "Dimensional gauge check revealed 0.14 mm gouge on canopy locking hook bearing surface "
            "(exceeds 0.10 mm limit)."
        ),
        "corrective_action": (
            "Hook assembly condemned per JTD DM-53-30-04; awaiting MICAP replacement hook NSN 1560-01-602-7741."
        ),
        "awaiting_part_nsn": "1560-01-602-7741",
        "assigned_shift_lead": "Sgt R. Patel",
        "estimated_mttr_hours": 6.5,
        "logged_man_hours": 3.2,
        "created_at_utc": "2026-11-02T10:05:00Z",
    },
]

BQ_SEED_TABLES: dict[str, list[dict[str, Any]]] = {
    "airframe_component_telemetry": AIRFRAME_COMPONENT_TELEMETRY_ROWS,
    "global_depot_inventory": GLOBAL_DEPOT_INVENTORY_ROWS,
    "squadron_sortie_schedule": SQUADRON_SORTIE_SCHEDULE_ROWS,
    "high_freq_strain_telemetry": HIGH_FREQ_STRAIN_TELEMETRY_ROWS,
    "as_maintained_mbom_fasteners": AS_MAINTAINED_MBOM_FASTENERS_ROWS,
    "airworthiness_release_ledger": AIRWORTHINESS_RELEASE_LEDGER_ROWS,
    "maintenance_work_orders": MAINTENANCE_WORK_ORDERS_ROWS,
}

ALL_BQ_SEED_TABLES: dict[str, list[dict[str, Any]]] = BQ_SEED_TABLES


def get_seed_rows(table_name: str) -> list[dict[str, Any]]:
    """Return a copy of the authoritative seed rows for the specified BigQuery table."""
    if table_name not in BQ_SEED_TABLES:
        raise KeyError(f"Unknown BigQuery seed table: {table_name}")
    return [dict(row) for row in BQ_SEED_TABLES[table_name]]
