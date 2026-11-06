"""Authoritative BigQuery seed records for the 6 active tables (100 rows per table = 600 records) in antig-dave.ukd_f35_sustainment_demo (EU)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

SCHEMAS_DIR = Path(__file__).resolve().parent / "schemas"

# ---------------------------------------------------------------------------
# Fleet Reference Constants for Deterministic 100-Row Expansion
# ---------------------------------------------------------------------------
_FLEET_TAILS: tuple[str, ...] = tuple(
    f"ZM{num}"
    for num in range(135, 177)
    if num not in range(151, 163)
)

_SUBSYSTEM_CATALOG: tuple[dict[str, str], ...] = (
    {
        "wuc_code": "53-30",
        "subsystem_name": "Forward Fuselage Canopy Latch",
        "work_center": "STRUCTURES_LO",
        "nsn": "1560-01-642-8810",
        "part_prefix": "CNL",
        "component_name": "Canopy Forward Locking Hook Assembly",
        "tool_id": "JTD-53-30-T14",
        "tool_name": "Digital Micro-Torque Spanner 45 in-lbs (JTD-53-30-T14)",
        "sqep_domain": "SQEP-CANOPY-RIG",
        "hrc_prefix": "HRC-5330",
    },
    {
        "wuc_code": "34-40",
        "subsystem_name": "AN/APG-81 AESA Radar Array",
        "work_center": "AVIONICS",
        "nsn": "5841-01-611-9021",
        "part_prefix": "APG",
        "component_name": "AN/APG-81 Radar Low Voltage Power Module",
        "tool_id": "APG-81-BITE-02",
        "tool_name": "Portable AESA Waveguide Calibration Test Set (APG-81-BITE-02)",
        "sqep_domain": "SQEP-AV-AESA",
        "hrc_prefix": "HRC-3440",
    },
    {
        "wuc_code": "94-10",
        "subsystem_name": "Electro-Optical Targeting System (EOTS)",
        "work_center": "AVIONICS",
        "nsn": "1270-01-633-7741",
        "part_prefix": "EOT",
        "component_name": "EOTS Nitrogen Purge & Sapphire Window Unit",
        "tool_id": "EOTS-N2-PURGE-09",
        "tool_name": "Dry Nitrogen Optical Purge Manifold Rig (EOTS-N2-PURGE-09)",
        "sqep_domain": "SQEP-AV-EO-LASER",
        "hrc_prefix": "HRC-9410",
    },
    {
        "wuc_code": "72-30",
        "subsystem_name": "F135-PW-600 LiftFan Clutch Assembly",
        "work_center": "PROPULSION",
        "nsn": "2840-01-620-3319",
        "part_prefix": "LFN",
        "component_name": "F135 LiftFan Drive Shaft Coupling Assembly",
        "tool_id": "PROP-BAL-7230",
        "tool_name": "Laser Vibrometer & Dynamic Shaft Balance Set (PROP-BAL-7230)",
        "sqep_domain": "SQEP-PROP-STOVL",
        "hrc_prefix": "HRC-7230",
    },
    {
        "wuc_code": "51-10",
        "subsystem_name": "Weapon Bay Door Outer Mold Line LO Coating",
        "work_center": "STRUCTURES_LO",
        "nsn": "8030-01-609-1182",
        "part_prefix": "RAM",
        "component_name": "High-Temp RAM Sheet 'B' Conductive Edge Seal",
        "tool_id": "LO-IR-BLANKET-04",
        "tool_name": "220C High-Temp RAM Cure Heater Blanket (LO-IR-BLANKET-04)",
        "sqep_domain": "SQEP-LO-SIGNATURE",
        "hrc_prefix": "HRC-5110",
    },
    {
        "wuc_code": "32-40",
        "subsystem_name": "Main Landing Gear Carbon Brake Pack",
        "work_center": "FLIGHT_LINE",
        "nsn": "1680-01-601-2290",
        "part_prefix": "MLG",
        "component_name": "Main Landing Gear Carbon Stator Disc Pack",
        "tool_id": "MLG-GAUGE-3240",
        "tool_name": "Digital Strut Extension & Brake Wear Pin Gauge (MLG-GAUGE-3240)",
        "sqep_domain": "SQEP-FL-UNDERCART",
        "hrc_prefix": "HRC-3240",
    },
    {
        "wuc_code": "91-20",
        "subsystem_name": "BRU-68/A Pneumatic Bomb Rack Unit",
        "work_center": "ARMAMENT",
        "nsn": "1095-01-598-3321",
        "part_prefix": "BRU",
        "component_name": "BRU-68/A Pneumatic Ejector Solenoid Valve",
        "tool_id": "ARM-BRU68-PNEU",
        "tool_name": "High-Pressure Pneumatic Ejector Test Bench (ARM-BRU68-PNEU)",
        "sqep_domain": "SQEP-ARM-WEAPONS",
        "hrc_prefix": "HRC-9120",
    },
)

_SQUADRON_ROSTER: tuple[tuple[str, str, str], ...] = (
    ("617 Sqn (The Dambusters)", "RAF Marham", "Chf Tech M. Davies"),
    ("809 NAS (The Immortals)", "HMS Queen Elizabeth", "POAET J. Stirling"),
    ("207 Sqn (OCU)", "RAF Marham", "Sgt R. Patel"),
    ("617 Sqn (The Dambusters)", "RAF Marham", "FSgt A. Wallace"),
    ("809 NAS (The Immortals)", "HMS Prince of Wales", "CPOAET H. Evans"),
    ("207 Sqn (OCU)", "RAF Marham", "Chf Tech K. Lindqvist"),
)

_TAIL_ASSIGNMENT_MAP: dict[str, tuple[str, str, str]] = {
    "ZM151": ("617 Sqn (The Dambusters)", "RAF Marham", "Chf Tech M. Davies"),
    "ZM152": ("617 Sqn (The Dambusters)", "RAF Marham", "Chf Tech K. Lindqvist"),
    "ZM153": ("617 Sqn (The Dambusters)", "RAF Marham", "WO1 D. MacLeod"),
    "ZM154": ("617 Sqn (The Dambusters)", "RAF Marham", "Chf Tech M. Davies"),
    "ZM155": ("617 Sqn (The Dambusters)", "RAF Marham", "Sgt T. O'Connor"),
    "ZM156": ("809 NAS (The Immortals)", "HMS Prince of Wales", "POAET J. Stirling"),
    "ZM157": ("809 NAS (The Immortals)", "HMS Queen Elizabeth", "LAET S. Krishnan"),
    "ZM158": ("809 NAS (The Immortals)", "HMS Prince of Wales", "CPOAET N. Armstrong"),
    "ZM159": ("809 NAS (The Immortals)", "HMS Queen Elizabeth", "POAET T. Campbell"),
    "ZM160": ("207 Sqn (OCU)", "RAF Marham", "FSgt L. Becker"),
    "ZM161": ("207 Sqn (OCU)", "RAF Marham", "Chf Tech K. Lindqvist"),
    "ZM162": ("207 Sqn (OCU)", "RAF Marham", "Sgt R. Patel"),
    **{
        _tail: _SQUADRON_ROSTER[_i % len(_SQUADRON_ROSTER)]
        for _i, _tail in enumerate(_FLEET_TAILS)
    },
}

# ---------------------------------------------------------------------------
# Table 1: airframe_component_telemetry (100 rows)
# ---------------------------------------------------------------------------
_BASE_AIRFRAME_COMPONENT_TELEMETRY_ROWS: list[dict[str, Any]] = [
    {
        "telemetry_record_id": "TEL-ZM151-ACT-99812",
        "tail_number": "ZM151",
        "aircraft_variant": "F-35B",
        "base_location": "RAF Marham",
        "part_serial_number": "ACT-99812-F",
        "nsn": "1680-01-619-4821",
        "component_name": "Horizontal Tail Electro-Hydrostatic Actuator (EHA)",
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
        "component_name": "Horizontal Tail Electro-Hydrostatic Actuator (EHA)",
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
        "component_name": "Horizontal Tail Electro-Hydrostatic Actuator (EHA)",
        "current_flight_hours": 964.5,
        "life_limit_threshold_hrs": 1000.0,
    },
    {
        "telemetry_record_id": "TEL-ZM158-ACT-77510",
        "tail_number": "ZM158",
        "aircraft_variant": "F-35B",
        "base_location": "HMS Prince of Wales",
        "part_serial_number": "ACT-77510-C",
        "nsn": "1680-01-619-4821",
        "component_name": "Horizontal Tail Electro-Hydrostatic Actuator (EHA)",
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
        "component_name": "Horizontal Tail Electro-Hydrostatic Actuator (EHA)",
        "current_flight_hours": 610.0,
        "life_limit_threshold_hrs": 1000.0,
    },
    {
        "telemetry_record_id": "TEL-ZM160-ACT-77560",
        "tail_number": "ZM160",
        "aircraft_variant": "F-35B",
        "base_location": "RAF Marham",
        "part_serial_number": "ACT-77560-E",
        "nsn": "1680-01-619-4821",
        "component_name": "Horizontal Tail Electro-Hydrostatic Actuator (EHA)",
        "current_flight_hours": 745.8,
        "life_limit_threshold_hrs": 1000.0,
    },
]

AIRFRAME_COMPONENT_TELEMETRY_ROWS: list[dict[str, Any]] = list(
    _BASE_AIRFRAME_COMPONENT_TELEMETRY_ROWS
)
for _idx in range(6, 100):
    _tail = _FLEET_TAILS[_idx % len(_FLEET_TAILS)]
    _sub = _SUBSYSTEM_CATALOG[_idx % len(_SUBSYSTEM_CATALOG)]
    _sqn_info = _TAIL_ASSIGNMENT_MAP[_tail]
    _serial = f"{_sub['part_prefix']}-{70000 + _idx}-B"
    _hours = round(140.0 + ((_idx * 17) % 620) + (_idx % 10) * 0.4, 1)
    AIRFRAME_COMPONENT_TELEMETRY_ROWS.append(
        {
            "telemetry_record_id": f"TEL-{_tail}-{_sub['part_prefix']}-{70000 + _idx}",
            "tail_number": _tail,
            "aircraft_variant": "F-35B",
            "base_location": _sqn_info[1],
            "part_serial_number": _serial,
            "nsn": _sub["nsn"],
            "component_name": _sub["component_name"],
            "current_flight_hours": _hours,
            "life_limit_threshold_hrs": 1000.0,
        }
    )

# ---------------------------------------------------------------------------
# Table 2: global_depot_inventory (100 rows)
# ---------------------------------------------------------------------------
_BASE_GLOBAL_DEPOT_INVENTORY_ROWS: list[dict[str, Any]] = [
    {
        "nsn": "1680-01-619-4821",
        "part_name": "Horizontal Tail Electro-Hydrostatic Actuator (EHA)",
        "depot_id": "DEPOT-MAR-01",
        "depot_name": "RAF Marham Regional Sustainment Hub",
        "quantity_on_hand": 4,
        "quantity_reserved_30d": 2,
        "reorder_point_threshold": 3,
        "avg_shipping_eta_hours": 18.0,
    },
    {
        "nsn": "1680-01-619-4821",
        "part_name": "Horizontal Tail Electro-Hydrostatic Actuator (EHA)",
        "depot_id": "DEPOT-QNLZ-02",
        "depot_name": "HMS Queen Elizabeth Afloat Spares",
        "quantity_on_hand": 2,
        "quantity_reserved_30d": 1,
        "reorder_point_threshold": 2,
        "avg_shipping_eta_hours": 36.0,
    },
    {
        "nsn": "1680-01-619-4821",
        "part_name": "Horizontal Tail Electro-Hydrostatic Actuator (EHA)",
        "depot_id": "DEPOT-PWLS-03",
        "depot_name": "HMS Prince of Wales Afloat Spares",
        "quantity_on_hand": 2,
        "quantity_reserved_30d": 1,
        "reorder_point_threshold": 2,
        "avg_shipping_eta_hours": 36.0,
    },
]

_DEPOT_SITES: tuple[tuple[str, str, float], ...] = (
    ("DEPOT-MAR-01", "RAF Marham Regional Sustainment Hub", 18.0),
    ("DEPOT-QNLZ-02", "HMS Queen Elizabeth Afloat Spares", 36.0),
    ("DEPOT-PWLS-03", "HMS Prince of Wales Afloat Spares", 36.0),
    ("DEPOT-BAE-SAMLESBURY-04", "BAE Systems Samlesbury Aerostructures Hub", 12.0),
    ("DEPOT-LM-FORTWORTH-05", "Lockheed Martin Fort Worth Global Sustainment Hub", 48.0),
)

GLOBAL_DEPOT_INVENTORY_ROWS: list[dict[str, Any]] = list(
    _BASE_GLOBAL_DEPOT_INVENTORY_ROWS
)
for _idx in range(3, 100):
    _depot_id, _depot_name, _base_eta = _DEPOT_SITES[_idx % len(_DEPOT_SITES)]
    _sub = _SUBSYSTEM_CATALOG[_idx % len(_SUBSYSTEM_CATALOG)]
    _fsc = 1560 + (_idx % 12) * 110
    _niin_a = 100 + (_idx * 7) % 890
    _niin_b = 1000 + _idx * 37
    _nsn = _sub["nsn"] if _idx < 9 else f"{_fsc:04d}-01-{_niin_a:03d}-{_niin_b:04d}"
    _on_hand = 2 + (_idx % 11)
    _reserved = 1 + (_idx % 4)
    GLOBAL_DEPOT_INVENTORY_ROWS.append(
        {
            "nsn": _nsn,
            "part_name": f"{_sub['component_name']} (Block 4 Mod {(_idx % 5) + 1})",
            "depot_id": _depot_id,
            "depot_name": _depot_name,
            "quantity_on_hand": _on_hand,
            "quantity_reserved_30d": min(_on_hand, _reserved),
            "reorder_point_threshold": 2 + (_idx % 3),
            "avg_shipping_eta_hours": round(_base_eta + (_idx % 4) * 1.5, 1),
        }
    )

# ---------------------------------------------------------------------------
# Table 3: squadron_sortie_schedule (100 rows)
# ---------------------------------------------------------------------------
_BASE_SQUADRON_SORTIE_SCHEDULE_ROWS: list[dict[str, Any]] = [
    {
        "sortie_id": "SRT-MAR-20261103-01",
        "scheduled_departure_utc": "2026-11-03T07:30:00Z",
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
    {
        "sortie_id": "SRT-PWLS-20261103-01",
        "scheduled_departure_utc": "2026-11-03T11:00:00Z",
        "assigned_tail_number": "ZM160",
        "assigned_pilot_callsign": "Lt RN MacFarlane / IMMORTAL-2",
        "spare_tail_candidate": "ZM161",
        "sortie_readiness_status": "MC",
    },
]

_PILOT_CALLSIGNS: tuple[str, ...] = (
    "Flt Lt Henderson / VIPER-1",
    "Sqn Ldr Davies / VIPER-2",
    "Lt Cdr Vance / BROADSWORD-1",
    "Wg Cdr Sinclair / DAMBUSTER-1",
    "Flt Lt Al-Mansoor / LIGHTNING-3",
    "Lt RN MacFarlane / IMMORTAL-2",
    "Sqn Ldr Hughes / REAPER-4",
    "Flt Lt O'Connor / TALON-2",
)

SQUADRON_SORTIE_SCHEDULE_ROWS: list[dict[str, Any]] = list(
    _BASE_SQUADRON_SORTIE_SCHEDULE_ROWS
)
for _idx in range(4, 100):
    _day = 3 + ((_idx - 4) // 20)
    _hour = 10 + (((_idx - 4) % 20) // 2)
    _minute = 15 if (_idx % 2 == 0) else 45
    _loc_code = ("MAR", "QNLZ", "PWLS")[_idx % 3]
    _assigned_tail = _FLEET_TAILS[_idx % len(_FLEET_TAILS)]
    _spare_tail = _FLEET_TAILS[(_idx + 3) % len(_FLEET_TAILS)]
    SQUADRON_SORTIE_SCHEDULE_ROWS.append(
        {
            "sortie_id": f"SRT-{_loc_code}-2026110{_day}-{_idx:03d}",
            "scheduled_departure_utc": f"2026-11-0{_day}T{_hour:02d}:{_minute:02d}:00Z",
            "assigned_tail_number": _assigned_tail,
            "assigned_pilot_callsign": _PILOT_CALLSIGNS[_idx % len(_PILOT_CALLSIGNS)],
            "spare_tail_candidate": _spare_tail,
            "sortie_readiness_status": "MC" if (_idx % 7 != 0) else "PMC-M",
        }
    )

# ---------------------------------------------------------------------------
# Table 4: maintenance_work_orders (100 rows)
# Keep original 14 rows (6 active + 8 COMPLETED at indices 0..13).
# Rows 14..99 (WO-2026-88415..WO-2026-88500) are historical COMPLETED work orders
# so active-shift filters (`work_order_status != 'COMPLETED'`) return the exact 6 active rows.
# ---------------------------------------------------------------------------
_BASE_MAINTENANCE_WORK_ORDERS_ROWS: list[dict[str, Any]] = [
    {
        "work_order_id": "WO-2026-88401",
        "tail_number": "ZM151",
        "aircraft_variant": "F-35B",
        "squadron": "617 Sqn (The Dambusters)",
        "base_location": "RAF Marham",
        "aircraft_status": "PMC-M",
        "work_order_status": "OPEN",
        "priority": "PRIORITY_1_RED_X",
        "work_center": "FLIGHT_LINE",
        "wuc_code": "27-10",
        "subsystem_name": "Horizontal Tail Electro-Hydrostatic Actuator (EHA)",
        "discrepancy_narrative": (
            "PHM Advisory: Horizontal tail EHA S/N ACT-99812-F logged 1,000.4 cumulative "
            "high-load hours (exceeds 1,000.0 hr overhaul limit)."
        ),
        "corrective_action": (
            "Scheduled for bay replacement; checking RAF Marham depot stock for NSN 1680-01-619-4821."
        ),
        "awaiting_part_nsn": "1680-01-619-4821",
        "assigned_shift_lead": "Chf Tech M. Davies",
        "estimated_mttr_hours": 8.5,
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
        "estimated_mttr_hours": 14.0,
        "logged_man_hours": 1.5,
        "created_at_utc": "2026-11-02T20:05:00Z",
    },
    {
        "work_order_id": "WO-2026-88403",
        "tail_number": "ZM161",
        "aircraft_variant": "F-35B",
        "squadron": "207 Sqn (OCU)",
        "base_location": "RAF Marham",
        "aircraft_status": "FMC",
        "work_order_status": "COMPLETED",
        "priority": "PRIORITY_3_ROUTINE",
        "work_center": "STRUCTURES_LO",
        "wuc_code": "53-20",
        "subsystem_name": "Center Fuselage Frame 496 Bulkhead",
        "discrepancy_narrative": (
            "Post-sortie SRT-MAR-20261102-09 7.8G pull (98.4% design yield) and NDI ultrasonic "
            "C-scan anomaly at FS 496.0, WL 112.4."
        ),
        "corrective_action": (
            "Phased-array ultrasonic NDI inspection completed on Frame 496 bulkhead; structural "
            "engineering disposition cleared and fastener torque verified."
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
        "aircraft_status": "FMC",
        "work_order_status": "COMPLETED",
        "priority": "PRIORITY_3_ROUTINE",
        "work_center": "AVIONICS",
        "wuc_code": "34-40",
        "subsystem_name": "AN/APG-81 AESA Radar Array",
        "discrepancy_narrative": (
            "BIT Fault APG-81-4402: Transmit/Receive module bank 3 power supply drop during "
            "ground power-on self-test."
        ),
        "corrective_action": (
            "Replaced Low Voltage Power Supply assembly and verified AESA array BIT calibration."
        ),
        "awaiting_part_nsn": None,
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
        "estimated_mttr_hours": 8.0,
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
        "subsystem_name": "Horizontal Tail Electro-Hydrostatic Actuator (EHA)",
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
        "base_location": "HMS Prince of Wales",
        "aircraft_status": "NMC-S",
        "work_order_status": "AWAITING_PARTS (MICAP)",
        "priority": "PRIORITY_1_RED_X",
        "work_center": "FLIGHT_LINE",
        "wuc_code": "27-10",
        "subsystem_name": "Horizontal Tail Electro-Hydrostatic Actuator (EHA)",
        "discrepancy_narrative": (
            "Horizontal tail actuator S/N ACT-99704-A internal seal leak detected on carrier flight deck."
        ),
        "corrective_action": (
            "MICAP requisition submitted for NSN 1680-01-619-4821; awaiting COD airlift to HMS Prince of Wales."
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
        "work_order_status": "COMPLETED",
        "priority": "PRIORITY_3_ROUTINE",
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
        "base_location": "HMS Prince of Wales",
        "aircraft_status": "FMC",
        "work_order_status": "COMPLETED",
        "priority": "PRIORITY_3_ROUTINE",
        "work_center": "FLIGHT_LINE",
        "wuc_code": "32-40",
        "subsystem_name": "Main Landing Gear Carbon Brake Pack",
        "discrepancy_narrative": "Scheduled carrier arrestment/STOVL brake wear pin gauge measurement on HMS Prince of Wales flight deck.",
        "corrective_action": "Wear pin at 68% remaining life; logged in ODIN and released for flight operations.",
        "awaiting_part_nsn": None,
        "assigned_shift_lead": "CPOAET N. Armstrong",
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
            "3BSD pitch nozzle actuator feedback RVDT sensor discrepancy during carrier deck spot movement on HMS Queen Elizabeth."
        ),
        "corrective_action": (
            "Troubleshooting harness continuity between 3BSD RVDT channel B and propulsion control module."
        ),
        "awaiting_part_nsn": None,
        "assigned_shift_lead": "POAET T. Campbell",
        "estimated_mttr_hours": 7.5,
        "logged_man_hours": 1.5,
        "created_at_utc": "2026-11-02T20:40:00Z",
    },
    {
        "work_order_id": "WO-2026-88412",
        "tail_number": "ZM160",
        "aircraft_variant": "F-35B",
        "squadron": "207 Sqn (OCU)",
        "base_location": "RAF Marham",
        "aircraft_status": "FMC",
        "work_order_status": "COMPLETED",
        "priority": "PRIORITY_3_ROUTINE",
        "work_center": "ARMAMENT",
        "wuc_code": "91-20",
        "subsystem_name": "BRU-68/A Pneumatic Bomb Rack Unit",
        "discrepancy_narrative": (
            "Station 4 BRU-68/A ejector hook failed to latch during weapons loading trainer drill."
        ),
        "corrective_action": "Removed rack for bench pneumatic leak test and solenoid valve inspection.",
        "awaiting_part_nsn": None,
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

MAINTENANCE_WORK_ORDERS_ROWS: list[dict[str, Any]] = list(
    _BASE_MAINTENANCE_WORK_ORDERS_ROWS
)
for _idx in range(14, 100):
    _wo_num = 88401 + _idx
    _tail = _FLEET_TAILS[_idx % len(_FLEET_TAILS)]
    _sqn, _base, _lead = _TAIL_ASSIGNMENT_MAP[_tail]
    _sub = _SUBSYSTEM_CATALOG[_idx % len(_SUBSYSTEM_CATALOG)]
    _day = 1 + (_idx % 28)
    _hr = 6 + (_idx % 16)
    _est_mttr = round(1.5 + (_idx % 6) * 0.5, 1)
    _logged_hrs = round(max(0.8, _est_mttr - 0.2), 1)
    MAINTENANCE_WORK_ORDERS_ROWS.append(
        {
            "work_order_id": f"WO-2026-{_wo_num}",
            "tail_number": _tail,
            "aircraft_variant": "F-35B",
            "squadron": _sqn,
            "base_location": _base,
            "aircraft_status": "FMC",
            "work_order_status": "COMPLETED",
            "priority": "PRIORITY_3_ROUTINE",
            "work_center": _sub["work_center"],
            "wuc_code": _sub["wuc_code"],
            "subsystem_name": _sub["subsystem_name"],
            "discrepancy_narrative": (
                f"Scheduled post-sortie ODIN PHM verification and preventive inspection on {_sub['subsystem_name']}."
            ),
            "corrective_action": (
                f"Completed functional check per JTD WUC {_sub['wuc_code']} using {_sub['tool_id']}; released FMC."
            ),
            "awaiting_part_nsn": None,
            "assigned_shift_lead": _lead,
            "estimated_mttr_hours": _est_mttr,
            "logged_man_hours": _logged_hrs,
            "created_at_utc": f"2026-10-{_day:02d}T{_hr:02d}:30:00Z",
        }
    )

# ---------------------------------------------------------------------------
# Table 8: phm_bit_fault_events (100 rows — UC 0.1)
# Rows 0..13 cover active/recent PHM/BIT events (including Zero-BIT canopy catch
# on ZM151, chronic CND repeat offenders, and 3 unactioned PHM advisories with
# linked_work_order_id=None). Rows 14..99 link 1:1 to WO-2026-88415..WO-2026-88500.
# ---------------------------------------------------------------------------
_BASE_PHM_BIT_FAULT_EVENTS_ROWS: list[dict[str, Any]] = [
    {
        "fault_event_id": "PHM-2026-99101",
        "tail_number": "ZM151",
        "aircraft_variant": "F-35B",
        "squadron": "617 Sqn (The Dambusters)",
        "base_location": "RAF Marham",
        "sortie_id": "SRT-MAR-20261103-01",
        "wuc_code": "27-10",
        "subsystem_name": "Horizontal Tail Electro-Hydrostatic Actuator (EHA)",
        "hrc_code": "HRC-2710-88A",
        "fault_severity": "DEGRADED_PMC",
        "bit_trigger_type": "PHM_PROGNOSTIC_THRESHOLD",
        "recurrence_count_30d": 2,
        "cnd_flag": False,
        "diagnostic_confidence_pct": 98.5,
        "linked_work_order_id": "WO-2026-88401",
        "fault_timestamp_utc": "2026-11-02T19:02:00Z",
    },
    {
        "fault_event_id": "PHM-2026-99102",
        "tail_number": "ZM151",
        "aircraft_variant": "F-35B",
        "squadron": "617 Sqn (The Dambusters)",
        "base_location": "RAF Marham",
        "sortie_id": "SRT-MAR-20261103-01",
        "wuc_code": "53-30",
        "subsystem_name": "Forward Fuselage Canopy Latch",
        "hrc_code": "HRC-5330-000-NONE",
        "fault_severity": "NO_BIT_FAULT_LOGGED",
        "bit_trigger_type": "PILOT_REPORT_ONLY_NO_BIT",
        "recurrence_count_30d": 3,
        "cnd_flag": True,
        "diagnostic_confidence_pct": 0.0,
        "linked_work_order_id": "WO-2026-88402",
        "fault_timestamp_utc": "2026-11-02T19:55:00Z",
    },
    {
        "fault_event_id": "PHM-2026-99103",
        "tail_number": "ZM161",
        "aircraft_variant": "F-35B",
        "squadron": "207 Sqn (OCU)",
        "base_location": "RAF Marham",
        "sortie_id": None,
        "wuc_code": "53-20",
        "subsystem_name": "Center Fuselage Frame 496 Bulkhead",
        "hrc_code": "HRC-5320-94G",
        "fault_severity": "ADVISORY_PHM",
        "bit_trigger_type": "CONTINUOUS_BIT",
        "recurrence_count_30d": 1,
        "cnd_flag": False,
        "diagnostic_confidence_pct": 99.4,
        "linked_work_order_id": "WO-2026-88403",
        "fault_timestamp_utc": "2026-11-02T14:22:19Z",
    },
    {
        "fault_event_id": "PHM-2026-99104",
        "tail_number": "ZM152",
        "aircraft_variant": "F-35B",
        "squadron": "617 Sqn (The Dambusters)",
        "base_location": "RAF Marham",
        "sortie_id": None,
        "wuc_code": "34-40",
        "subsystem_name": "AN/APG-81 AESA Radar Array",
        "hrc_code": "HRC-3440-4402",
        "fault_severity": "ADVISORY_PHM",
        "bit_trigger_type": "INITIATED_BIT",
        "recurrence_count_30d": 4,
        "cnd_flag": False,
        "diagnostic_confidence_pct": 94.2,
        "linked_work_order_id": "WO-2026-88404",
        "fault_timestamp_utc": "2026-11-01T14:05:00Z",
    },
    {
        "fault_event_id": "PHM-2026-99105",
        "tail_number": "ZM153",
        "aircraft_variant": "F-35B",
        "squadron": "617 Sqn (The Dambusters)",
        "base_location": "RAF Marham",
        "sortie_id": None,
        "wuc_code": "72-30",
        "subsystem_name": "F135-PW-600 LiftFan Clutch Assembly",
        "hrc_code": "HRC-7230-14V",
        "fault_severity": "CRITICAL_GROUNDING",
        "bit_trigger_type": "CONTINUOUS_BIT",
        "recurrence_count_30d": 2,
        "cnd_flag": False,
        "diagnostic_confidence_pct": 97.0,
        "linked_work_order_id": "WO-2026-88405",
        "fault_timestamp_utc": "2026-11-01T09:12:00Z",
    },
    {
        "fault_event_id": "PHM-2026-99106",
        "tail_number": "ZM154",
        "aircraft_variant": "F-35B",
        "squadron": "617 Sqn (The Dambusters)",
        "base_location": "RAF Marham",
        "sortie_id": "SRT-MAR-20261103-02",
        "wuc_code": "27-10",
        "subsystem_name": "Horizontal Tail Electro-Hydrostatic Actuator (EHA)",
        "hrc_code": "HRC-2710-10B",
        "fault_severity": "ADVISORY_PHM",
        "bit_trigger_type": "PHM_PROGNOSTIC_THRESHOLD",
        "recurrence_count_30d": 1,
        "cnd_flag": False,
        "diagnostic_confidence_pct": 96.0,
        "linked_work_order_id": "WO-2026-88406",
        "fault_timestamp_utc": "2026-11-02T15:40:00Z",
    },
    {
        "fault_event_id": "PHM-2026-99107",
        "tail_number": "ZM155",
        "aircraft_variant": "F-35B",
        "squadron": "617 Sqn (The Dambusters)",
        "base_location": "RAF Marham",
        "sortie_id": None,
        "wuc_code": "51-10",
        "subsystem_name": "Weapon Bay Door Outer Mold Line LO Coating",
        "hrc_code": "HRC-5110-02R",
        "fault_severity": "ADVISORY_PHM",
        "bit_trigger_type": "INITIATED_BIT",
        "recurrence_count_30d": 1,
        "cnd_flag": False,
        "diagnostic_confidence_pct": 91.5,
        "linked_work_order_id": "WO-2026-88407",
        "fault_timestamp_utc": "2026-11-02T11:20:00Z",
    },
    {
        "fault_event_id": "PHM-2026-99108",
        "tail_number": "ZM156",
        "aircraft_variant": "F-35B",
        "squadron": "809 NAS (The Immortals)",
        "base_location": "HMS Prince of Wales",
        "sortie_id": None,
        "wuc_code": "27-10",
        "subsystem_name": "Horizontal Tail Electro-Hydrostatic Actuator (EHA)",
        "hrc_code": "HRC-2710-99L",
        "fault_severity": "CRITICAL_GROUNDING",
        "bit_trigger_type": "CONTINUOUS_BIT",
        "recurrence_count_30d": 2,
        "cnd_flag": False,
        "diagnostic_confidence_pct": 99.1,
        "linked_work_order_id": "WO-2026-88408",
        "fault_timestamp_utc": "2026-11-02T07:02:00Z",
    },
    {
        "fault_event_id": "PHM-2026-99109",
        "tail_number": "ZM157",
        "aircraft_variant": "F-35B",
        "squadron": "809 NAS (The Immortals)",
        "base_location": "HMS Queen Elizabeth",
        "sortie_id": None,
        "wuc_code": "94-10",
        "subsystem_name": "Electro-Optical Targeting System (EOTS)",
        "hrc_code": "HRC-9410-18C",
        "fault_severity": "DEGRADED_PMC",
        "bit_trigger_type": "CONTINUOUS_BIT",
        "recurrence_count_30d": 5,
        "cnd_flag": True,
        "diagnostic_confidence_pct": 72.4,
        "linked_work_order_id": "WO-2026-88409",
        "fault_timestamp_utc": "2026-11-02T14:55:00Z",
    },
    {
        "fault_event_id": "PHM-2026-99110",
        "tail_number": "ZM158",
        "aircraft_variant": "F-35B",
        "squadron": "809 NAS (The Immortals)",
        "base_location": "HMS Prince of Wales",
        "sortie_id": "SRT-QNLZ-20261103-01",
        "wuc_code": "32-40",
        "subsystem_name": "Main Landing Gear Carbon Brake Pack",
        "hrc_code": "HRC-3240-68P",
        "fault_severity": "ADVISORY_PHM",
        "bit_trigger_type": "PHM_PROGNOSTIC_THRESHOLD",
        "recurrence_count_30d": 1,
        "cnd_flag": False,
        "diagnostic_confidence_pct": 98.0,
        "linked_work_order_id": "WO-2026-88410",
        "fault_timestamp_utc": "2026-11-01T18:10:00Z",
    },
    {
        "fault_event_id": "PHM-2026-99111",
        "tail_number": "ZM159",
        "aircraft_variant": "F-35B",
        "squadron": "809 NAS (The Immortals)",
        "base_location": "HMS Queen Elizabeth",
        "sortie_id": None,
        "wuc_code": "72-50",
        "subsystem_name": "3-Bearing Swivel Duct Nozzle Actuator",
        "hrc_code": "HRC-7250-31B",
        "fault_severity": "CRITICAL_GROUNDING",
        "bit_trigger_type": "CONTINUOUS_BIT",
        "recurrence_count_30d": 4,
        "cnd_flag": True,
        "diagnostic_confidence_pct": 84.5,
        "linked_work_order_id": "WO-2026-88411",
        "fault_timestamp_utc": "2026-11-02T20:25:00Z",
    },
    # 3 unactioned PHM advisories (linked_work_order_id=None) with chronic CND flags
    {
        "fault_event_id": "PHM-2026-99112",
        "tail_number": "ZM158",
        "aircraft_variant": "F-35B",
        "squadron": "809 NAS (The Immortals)",
        "base_location": "HMS Prince of Wales",
        "sortie_id": "SRT-PWLS-20261103-01",
        "wuc_code": "34-40",
        "subsystem_name": "AN/APG-81 AESA Radar Array",
        "hrc_code": "HRC-3440-19C",
        "fault_severity": "ADVISORY_PHM",
        "bit_trigger_type": "CONTINUOUS_BIT",
        "recurrence_count_30d": 4,
        "cnd_flag": True,
        "diagnostic_confidence_pct": 68.0,
        "linked_work_order_id": None,
        "fault_timestamp_utc": "2026-11-02T21:40:00Z",
    },
    {
        "fault_event_id": "PHM-2026-99113",
        "tail_number": "ZM159",
        "aircraft_variant": "F-35B",
        "squadron": "809 NAS (The Immortals)",
        "base_location": "HMS Queen Elizabeth",
        "sortie_id": None,
        "wuc_code": "94-10",
        "subsystem_name": "Electro-Optical Targeting System (EOTS)",
        "hrc_code": "HRC-9410-07A",
        "fault_severity": "ADVISORY_PHM",
        "bit_trigger_type": "PHM_PROGNOSTIC_THRESHOLD",
        "recurrence_count_30d": 5,
        "cnd_flag": True,
        "diagnostic_confidence_pct": 74.5,
        "linked_work_order_id": None,
        "fault_timestamp_utc": "2026-11-02T22:05:00Z",
    },
    {
        "fault_event_id": "PHM-2026-99114",
        "tail_number": "ZM162",
        "aircraft_variant": "F-35B",
        "squadron": "207 Sqn (OCU)",
        "base_location": "RAF Marham",
        "sortie_id": None,
        "wuc_code": "53-30",
        "subsystem_name": "Forward Fuselage Canopy Latch",
        "hrc_code": "HRC-5330-14C",
        "fault_severity": "ADVISORY_PHM",
        "bit_trigger_type": "PILOT_REPORT_ONLY_NO_BIT",
        "recurrence_count_30d": 4,
        "cnd_flag": True,
        "diagnostic_confidence_pct": 0.0,
        "linked_work_order_id": None,
        "fault_timestamp_utc": "2026-11-02T22:30:00Z",
    },
]

PHM_BIT_FAULT_EVENTS_ROWS: list[dict[str, Any]] = list(
    _BASE_PHM_BIT_FAULT_EVENTS_ROWS
)
for _idx in range(14, 100):
    _wo = MAINTENANCE_WORK_ORDERS_ROWS[_idx]
    _sub = _SUBSYSTEM_CATALOG[_idx % len(_SUBSYSTEM_CATALOG)]
    _sortie_ref = SQUADRON_SORTIE_SCHEDULE_ROWS[_idx]["sortie_id"]
    _is_zero_bit = _idx % 19 == 0
    PHM_BIT_FAULT_EVENTS_ROWS.append(
        {
            "fault_event_id": f"PHM-2026-{99101 + _idx}",
            "tail_number": _wo["tail_number"],
            "aircraft_variant": _wo["aircraft_variant"],
            "squadron": _wo["squadron"],
            "base_location": _wo["base_location"],
            "sortie_id": _sortie_ref,
            "wuc_code": _wo["wuc_code"],
            "subsystem_name": _wo["subsystem_name"],
            "hrc_code": f"{_sub['hrc_prefix']}-{100 + _idx}A",
            "fault_severity": (
                "NO_BIT_FAULT_LOGGED" if _is_zero_bit else "ADVISORY_PHM"
            ),
            "bit_trigger_type": (
                "PILOT_REPORT_ONLY_NO_BIT"
                if _is_zero_bit
                else "PHM_PROGNOSTIC_THRESHOLD"
            ),
            "recurrence_count_30d": 1 if not _is_zero_bit else 2,
            "cnd_flag": bool(_is_zero_bit),
            "diagnostic_confidence_pct": 0.0 if _is_zero_bit else round(91.0 + (_idx % 8) * 1.1, 1),
            "linked_work_order_id": _wo["work_order_id"],
            "fault_timestamp_utc": _wo["created_at_utc"],
        }
    )

# ---------------------------------------------------------------------------
# Table 9: work_center_tooling_and_sqep (100 rows — UC 0.5)
# Rows 0..13 link 1:1 to WO-2026-88401..WO-2026-88414.
# Rows 14..99 link 1:1 to WO-2026-88415..WO-2026-88500.
# ---------------------------------------------------------------------------
_BASE_WORK_CENTER_TOOLING_AND_SQEP_ROWS: list[dict[str, Any]] = [
    {
        "resource_id": "RES-2026-00001",
        "assigned_work_order_id": "WO-2026-88401",
        "base_location": "RAF Marham",
        "work_center": "FLIGHT_LINE",
        "supported_wuc_code": "27-10",
        "shift_code": "DAY_ALPHA",
        "shift_lead_name": "Chf Tech M. Davies",
        "sqep_certification_domain": "SQEP-HYD-EHA",
        "sqep_certified_techs_on_shift": 4,
        "qar_inspector_available": True,
        "required_special_tool_id": "EHA-HYD-2710",
        "required_special_tool_name": "EHA Hydraulic Bleed & Rigging Test Set (EHA-HYD-2710)",
        "tool_calibration_status": "CALIBRATED_SERVICEABLE",
        "calibration_expiry_utc": "2027-03-15T00:00:00Z",
        "bay_dispatch_status": "READY_TO_DISPATCH",
        "shift_updated_utc": "2026-11-02T19:15:00Z",
    },
    {
        "resource_id": "RES-2026-00002",
        "assigned_work_order_id": "WO-2026-88402",
        "base_location": "RAF Marham",
        "work_center": "FLIGHT_LINE",
        "supported_wuc_code": "53-30",
        "shift_code": "DAY_ALPHA",
        "shift_lead_name": "Sgt R. Patel",
        "sqep_certification_domain": "SQEP-CANOPY-RIG",
        "sqep_certified_techs_on_shift": 3,
        "qar_inspector_available": True,
        "required_special_tool_id": "JTD-53-30-T14",
        "required_special_tool_name": "Digital Micro-Torque Spanner 45 in-lbs (JTD-53-30-T14)",
        "tool_calibration_status": "CALIBRATED_SERVICEABLE",
        "calibration_expiry_utc": "2027-02-20T00:00:00Z",
        "bay_dispatch_status": "READY_TO_DISPATCH",
        "shift_updated_utc": "2026-11-02T20:10:00Z",
    },
    {
        "resource_id": "RES-2026-00003",
        "assigned_work_order_id": "WO-2026-88403",
        "base_location": "RAF Marham",
        "work_center": "STRUCTURES_LO",
        "supported_wuc_code": "53-20",
        "shift_code": "NIGHT_BRAVO",
        "shift_lead_name": "FSgt A. Wallace",
        "sqep_certification_domain": "SQEP-NDI-CSCAN-L3",
        "sqep_certified_techs_on_shift": 2,
        "qar_inspector_available": True,
        "required_special_tool_id": "NDI-PAUT-496A",
        "required_special_tool_name": "Phased-Array Ultrasonic C-Scan Rig (10 MHz 64-Element)",
        "tool_calibration_status": "CALIBRATED_SERVICEABLE",
        "calibration_expiry_utc": "2027-05-01T00:00:00Z",
        "bay_dispatch_status": "READY_TO_DISPATCH",
        "shift_updated_utc": "2026-11-02T21:20:00Z",
    },
    {
        "resource_id": "RES-2026-00004",
        "assigned_work_order_id": "WO-2026-88404",
        "base_location": "RAF Marham",
        "work_center": "AVIONICS",
        "supported_wuc_code": "34-40",
        "shift_code": "DAY_ALPHA",
        "shift_lead_name": "Chf Tech K. Lindqvist",
        "sqep_certification_domain": "SQEP-AV-AESA",
        "sqep_certified_techs_on_shift": 3,
        "qar_inspector_available": True,
        "required_special_tool_id": "APG-81-BITE-02",
        "required_special_tool_name": "Portable AESA Waveguide Calibration Test Set (APG-81-BITE-02)",
        "tool_calibration_status": "CALIBRATED_SERVICEABLE",
        "calibration_expiry_utc": "2027-01-18T00:00:00Z",
        "bay_dispatch_status": "READY_TO_DISPATCH",
        "shift_updated_utc": "2026-11-02T14:30:00Z",
    },
    {
        "resource_id": "RES-2026-00005",
        "assigned_work_order_id": "WO-2026-88405",
        "base_location": "RAF Marham",
        "work_center": "PROPULSION",
        "supported_wuc_code": "72-30",
        "shift_code": "NIGHT_BRAVO",
        "shift_lead_name": "WO1 D. MacLeod",
        "sqep_certification_domain": "SQEP-PROP-STOVL",
        "sqep_certified_techs_on_shift": 2,
        "qar_inspector_available": False,
        "required_special_tool_id": "PROP-BAL-7230",
        "required_special_tool_name": "Laser Vibrometer & Dynamic Shaft Balance Set (PROP-BAL-7230)",
        "tool_calibration_status": "CALIBRATION_DUE_WARNING",
        "calibration_expiry_utc": "2026-11-09T00:00:00Z",
        "bay_dispatch_status": "BLOCKED_NO_QAR_ON_SHIFT",
        "shift_updated_utc": "2026-11-02T09:45:00Z",
    },
    {
        "resource_id": "RES-2026-00006",
        "assigned_work_order_id": "WO-2026-88406",
        "base_location": "RAF Marham",
        "work_center": "FLIGHT_LINE",
        "supported_wuc_code": "27-10",
        "shift_code": "DAY_ALPHA",
        "shift_lead_name": "Chf Tech M. Davies",
        "sqep_certification_domain": "SQEP-HYD-EHA",
        "sqep_certified_techs_on_shift": 4,
        "qar_inspector_available": True,
        "required_special_tool_id": "EHA-HYD-2710",
        "required_special_tool_name": "EHA Hydraulic Bleed & Rigging Test Set (EHA-HYD-2710)",
        "tool_calibration_status": "CALIBRATED_SERVICEABLE",
        "calibration_expiry_utc": "2027-03-15T00:00:00Z",
        "bay_dispatch_status": "READY_TO_DISPATCH",
        "shift_updated_utc": "2026-11-02T16:15:00Z",
    },
    {
        "resource_id": "RES-2026-00007",
        "assigned_work_order_id": "WO-2026-88407",
        "base_location": "RAF Marham",
        "work_center": "STRUCTURES_LO",
        "supported_wuc_code": "51-10",
        "shift_code": "NIGHT_BRAVO",
        "shift_lead_name": "Sgt T. O'Connor",
        "sqep_certification_domain": "SQEP-LO-SIGNATURE",
        "sqep_certified_techs_on_shift": 2,
        "qar_inspector_available": True,
        "required_special_tool_id": "LO-IR-BLANKET-04",
        "required_special_tool_name": "220C High-Temp RAM Cure Heater Blanket (LO-IR-BLANKET-04)",
        "tool_calibration_status": "EXPIRED_OUT_OF_CAL",
        "calibration_expiry_utc": "2026-10-29T00:00:00Z",
        "bay_dispatch_status": "BLOCKED_TOOL_OUT_OF_CAL",
        "shift_updated_utc": "2026-11-02T12:00:00Z",
    },
    {
        "resource_id": "RES-2026-00008",
        "assigned_work_order_id": "WO-2026-88408",
        "base_location": "HMS Prince of Wales",
        "work_center": "FLIGHT_LINE",
        "supported_wuc_code": "27-10",
        "shift_code": "CARRIER_WATCH_1",
        "shift_lead_name": "POAET J. Stirling",
        "sqep_certification_domain": "SQEP-HYD-EHA",
        "sqep_certified_techs_on_shift": 3,
        "qar_inspector_available": True,
        "required_special_tool_id": "EHA-HYD-2710-CV",
        "required_special_tool_name": "Shipboard EHA Hydraulic Rigging Manifold (EHA-HYD-2710-CV)",
        "tool_calibration_status": "CALIBRATED_SERVICEABLE",
        "calibration_expiry_utc": "2027-04-10T00:00:00Z",
        "bay_dispatch_status": "BLOCKED_AWAITING_MICAP_PART",
        "shift_updated_utc": "2026-11-02T07:30:00Z",
    },
    {
        "resource_id": "RES-2026-00009",
        "assigned_work_order_id": "WO-2026-88409",
        "base_location": "HMS Queen Elizabeth",
        "work_center": "AVIONICS",
        "supported_wuc_code": "94-10",
        "shift_code": "CARRIER_WATCH_1",
        "shift_lead_name": "LAET S. Krishnan",
        "sqep_certification_domain": "SQEP-AV-EO-LASER",
        "sqep_certified_techs_on_shift": 1,
        "qar_inspector_available": False,
        "required_special_tool_id": "EOTS-N2-PURGE-09",
        "required_special_tool_name": "Dry Nitrogen Optical Purge Manifold Rig (EOTS-N2-PURGE-09)",
        "tool_calibration_status": "IN_USE_OTHER_BAY",
        "calibration_expiry_utc": "2027-01-25T00:00:00Z",
        "bay_dispatch_status": "BLOCKED_NO_QAR_ON_SHIFT",
        "shift_updated_utc": "2026-11-02T15:25:00Z",
    },
    {
        "resource_id": "RES-2026-00010",
        "assigned_work_order_id": "WO-2026-88410",
        "base_location": "HMS Prince of Wales",
        "work_center": "FLIGHT_LINE",
        "supported_wuc_code": "32-40",
        "shift_code": "CARRIER_WATCH_1",
        "shift_lead_name": "CPOAET N. Armstrong",
        "sqep_certification_domain": "SQEP-FL-UNDERCART",
        "sqep_certified_techs_on_shift": 4,
        "qar_inspector_available": True,
        "required_special_tool_id": "MLG-GAUGE-3240",
        "required_special_tool_name": "Digital Strut Extension & Brake Wear Pin Gauge (MLG-GAUGE-3240)",
        "tool_calibration_status": "CALIBRATED_SERVICEABLE",
        "calibration_expiry_utc": "2027-06-01T00:00:00Z",
        "bay_dispatch_status": "READY_TO_DISPATCH",
        "shift_updated_utc": "2026-11-01T18:45:00Z",
    },
    {
        "resource_id": "RES-2026-00011",
        "assigned_work_order_id": "WO-2026-88411",
        "base_location": "HMS Queen Elizabeth",
        "work_center": "PROPULSION",
        "supported_wuc_code": "72-50",
        "shift_code": "CARRIER_WATCH_1",
        "shift_lead_name": "POAET T. Campbell",
        "sqep_certification_domain": "SQEP-PROP-3BSD",
        "sqep_certified_techs_on_shift": 2,
        "qar_inspector_available": True,
        "required_special_tool_id": "LO-IR-BLANKET-04",
        "required_special_tool_name": "220C High-Temp RAM Cure Heater Blanket & RVDT Loop Set (LO-IR-BLANKET-04)",
        "tool_calibration_status": "EXPIRED_OUT_OF_CAL",
        "calibration_expiry_utc": "2026-10-25T00:00:00Z",
        "bay_dispatch_status": "BLOCKED_TOOL_OUT_OF_CAL",
        "shift_updated_utc": "2026-11-02T20:50:00Z",
    },
    {
        "resource_id": "RES-2026-00012",
        "assigned_work_order_id": "WO-2026-88412",
        "base_location": "RAF Marham",
        "work_center": "ARMAMENT",
        "supported_wuc_code": "91-20",
        "shift_code": "DAY_ALPHA",
        "shift_lead_name": "FSgt L. Becker",
        "sqep_certification_domain": "SQEP-ARM-WEAPONS",
        "sqep_certified_techs_on_shift": 3,
        "qar_inspector_available": True,
        "required_special_tool_id": "ARM-BRU68-PNEU",
        "required_special_tool_name": "High-Pressure Pneumatic Ejector Test Bench (ARM-BRU68-PNEU)",
        "tool_calibration_status": "CALIBRATED_SERVICEABLE",
        "calibration_expiry_utc": "2027-02-14T00:00:00Z",
        "bay_dispatch_status": "READY_TO_DISPATCH",
        "shift_updated_utc": "2026-11-02T13:35:00Z",
    },
    {
        "resource_id": "RES-2026-00013",
        "assigned_work_order_id": "WO-2026-88413",
        "base_location": "RAF Marham",
        "work_center": "AVIONICS",
        "supported_wuc_code": "42-10",
        "shift_code": "DAY_ALPHA",
        "shift_lead_name": "Chf Tech K. Lindqvist",
        "sqep_certification_domain": "SQEP-AV-ICP-CRYPTO",
        "sqep_certified_techs_on_shift": 3,
        "qar_inspector_available": True,
        "required_special_tool_id": "PMA-CRYPTO-OFP4",
        "required_special_tool_name": "ODIN Block 4 Secure PMA Loader (PMA-CRYPTO-OFP4)",
        "tool_calibration_status": "CALIBRATED_SERVICEABLE",
        "calibration_expiry_utc": "2027-07-01T00:00:00Z",
        "bay_dispatch_status": "READY_TO_DISPATCH",
        "shift_updated_utc": "2026-11-01T11:20:00Z",
    },
    {
        "resource_id": "RES-2026-00014",
        "assigned_work_order_id": "WO-2026-88414",
        "base_location": "RAF Marham",
        "work_center": "STRUCTURES_LO",
        "supported_wuc_code": "53-30",
        "shift_code": "DAY_ALPHA",
        "shift_lead_name": "Sgt R. Patel",
        "sqep_certification_domain": "SQEP-CANOPY-RIG",
        "sqep_certified_techs_on_shift": 3,
        "qar_inspector_available": True,
        "required_special_tool_id": "JTD-53-30-G02",
        "required_special_tool_name": "Laser Go/No-Go Hook Bearing Wear Gauge (JTD-53-30-G02)",
        "tool_calibration_status": "CALIBRATED_SERVICEABLE",
        "calibration_expiry_utc": "2027-03-30T00:00:00Z",
        "bay_dispatch_status": "BLOCKED_AWAITING_MICAP_PART",
        "shift_updated_utc": "2026-11-02T10:15:00Z",
    },
]

WORK_CENTER_TOOLING_AND_SQEP_ROWS: list[dict[str, Any]] = list(
    _BASE_WORK_CENTER_TOOLING_AND_SQEP_ROWS
)
for _idx in range(14, 100):
    _wo = MAINTENANCE_WORK_ORDERS_ROWS[_idx]
    _sub = _SUBSYSTEM_CATALOG[_idx % len(_SUBSYSTEM_CATALOG)]
    _shift_code = (
        "CARRIER_WATCH_1"
        if _wo["base_location"] in ("HMS Queen Elizabeth", "HMS Prince of Wales")
        else ("DAY_ALPHA" if _idx % 2 == 0 else "NIGHT_BRAVO")
    )
    WORK_CENTER_TOOLING_AND_SQEP_ROWS.append(
        {
            "resource_id": f"RES-2026-{_idx + 1:05d}",
            "assigned_work_order_id": _wo["work_order_id"],
            "base_location": _wo["base_location"],
            "work_center": _wo["work_center"],
            "supported_wuc_code": _wo["wuc_code"],
            "shift_code": _shift_code,
            "shift_lead_name": _wo["assigned_shift_lead"],
            "sqep_certification_domain": _sub["sqep_domain"],
            "sqep_certified_techs_on_shift": 2 + (_idx % 4),
            "qar_inspector_available": True,
            "required_special_tool_id": _sub["tool_id"],
            "required_special_tool_name": _sub["tool_name"],
            "tool_calibration_status": "CALIBRATED_SERVICEABLE",
            "calibration_expiry_utc": f"2027-0{1 + (_idx % 8)}-{10 + (_idx % 18):02d}T00:00:00Z",
            "bay_dispatch_status": "READY_TO_DISPATCH",
            "shift_updated_utc": _wo["created_at_utc"],
        }
    )

# Non-_ROWS aliases for cross-feature compatibility
AIRFRAME_COMPONENT_TELEMETRY = AIRFRAME_COMPONENT_TELEMETRY_ROWS
GLOBAL_DEPOT_INVENTORY = GLOBAL_DEPOT_INVENTORY_ROWS
SQUADRON_SORTIE_SCHEDULE = SQUADRON_SORTIE_SCHEDULE_ROWS
MAINTENANCE_WORK_ORDERS = MAINTENANCE_WORK_ORDERS_ROWS
PHM_BIT_FAULT_EVENTS = PHM_BIT_FAULT_EVENTS_ROWS
WORK_CENTER_TOOLING_AND_SQEP = WORK_CENTER_TOOLING_AND_SQEP_ROWS

BQ_SEED_TABLES: dict[str, list[dict[str, Any]]] = {
    "airframe_component_telemetry": AIRFRAME_COMPONENT_TELEMETRY_ROWS,
    "global_depot_inventory": GLOBAL_DEPOT_INVENTORY_ROWS,
    "squadron_sortie_schedule": SQUADRON_SORTIE_SCHEDULE_ROWS,
    "maintenance_work_orders": MAINTENANCE_WORK_ORDERS_ROWS,
    "phm_bit_fault_events": PHM_BIT_FAULT_EVENTS_ROWS,
    "work_center_tooling_and_sqep": WORK_CENTER_TOOLING_AND_SQEP_ROWS,
}

ALL_BQ_SEED_TABLES: dict[str, list[dict[str, Any]]] = dict(BQ_SEED_TABLES)


def get_seed_rows(table_name: str) -> list[dict[str, Any]]:
    """Return a copy of the authoritative seed rows for the specified BigQuery table."""
    lookup = ALL_BQ_SEED_TABLES if table_name in ALL_BQ_SEED_TABLES else BQ_SEED_TABLES
    if table_name not in lookup:
        raise KeyError(f"Unknown BigQuery seed table: {table_name}")
    return [dict(row) for row in lookup[table_name]]
