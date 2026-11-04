"""Root Coordinator (`f35_sustainment_coordinator`) and ADK 2.0 `App` definition.

Wires `root_agent` with the 4 specialist domain sub-agents (`f35_maintenance_data_agent`,
`f35_analytics_agent`, `f35_jtd_search_agent`, `f35_airworthiness_orchestrator`),
Tier 1/2 fast-path `before_model_callback`, two-turn HITL `before_tool_callback`,
`ResumabilityConfig`, and `ContextCacheConfig` (`min_tokens=2048, ttl_seconds=1800, cache_intervals=10`).
"""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.apps import App, ResumabilityConfig

from app.callbacks import (
    enforce_hitl_airworthiness_gate,
    fast_path_before_model_callback,
)
from app.config import (
    COORDINATOR_MODEL,
    get_gemini_model,
    get_generate_content_config,
)
from app.sub_agents.uc0_maintenance_agent import f35_maintenance_data_agent
from app.sub_agents.uc1_analytics_agent import f35_analytics_agent
from app.sub_agents.uc2_search_agent import f35_jtd_search_agent
from app.sub_agents.uc3_airworthiness_agent import f35_airworthiness_orchestrator

STATIC_S100D_AND_ASIP_REFERENCE_HEADER = """
F-35 LIGHTNING II JOINT TECHNICAL DATA (JTD) & ASIP AIRWORTHINESS REFERENCE HEADER
- Platform: F-35A / F-35B / F-35C Joint Strike Fighter Sustainment Architecture
- Governing Airworthiness Standards: MIL-HDBK-516C, MIL-STD-3001, UK MoD DEF STAN 00-970
- GCP Data Residency: EU Multi-Region (BigQuery `EU`, Discovery Engine `eu`, Compute `europe-west1`)
- UC0 Conversational Maintenance Log Explorer (`f35_maintenance_data_agent`):
  * BigQuery Table 7: `antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders` (`EU`)
  * 14 ODIN / MOD Form 707A Work Orders (`WO-2026-88401`..`WO-2026-88414`) across `617 Sqn`, `809 NAS`, and `207 Sqn`
  * Renders Excel / Google Sheets-like Spreadsheet Cards (`A`..`R`, Status Badges, Formula Footer) + `.CSV` export
- UC1 Supply & Sortie Analytics (`f35_analytics_agent`):
  * BigQuery Dataset: `antig-dave.ukd_f35_sustainment_demo` (`EU`)
  * Primary Actuator Watch: Aileron Hydraulic Servo Actuator (`NSN 1680-01-619-4821`), 1,000.0-hr life limit
  * Primary Breach Tail: `ZM151` (`S/N ACT-99812-F` at `1,000.4` hrs, status `PMC-M`)
  * Serviceable Spare Tail: `ZM154` (`S/N ACT-99844-F` at `842.0` hrs, status `MC`)
  * Impacted Sortie: `SRT-MAR-20261103-01` (`Flt Lt Henderson / VIPER-1`)
- UC2 Grounded JTD & Narrative Search (`f35_jtd_search_agent`):
  * Discovery Engine (`eu`): `ukd-f35-jtd-ietm-ds` & `ukd-f35-narrative-logs-ds`
  * Key Publications: `DOC-01` (JTD 53-30-01 Forward Canopy Locking Mechanism), `DOC-02` (USMC VMFA-211 Narrative Log — Cured PR-1776M Silicon Sealant Debris in Roller Cam Track), `DOC-09` (MAM Section 9-1 — `220°C` High-Temp RAM Sheet `'B'` + Mandatory 4-Hour Heater Blanket Cure)
- UC3 Dynamic Flight Envelope Exceedance & Airworthiness (`f35_airworthiness_orchestrator`):
  * Exceedance Event: `EXC-20261102-ZM151` (`9.4 G`, `Mach 1.3`, `220.0°C` EGT at `14:22:18.420Z` on `Frame 496`)
  * Deterministic ASIP Output: `miners_rule_damage_delta = 0.0042`, `calculated_yield_pct = 104.2%`, `CLASS_A_ULTRASONIC_C_SCAN` per `JTD Rule 53-11-00` (`DOC-04`)
  * NDI C-Scan (`DOC-06`) & SRM 51-40 (`DOC-05`) Join: `Frame 496 — Fastener Hole #14` (`0.012` in shear elongation vs `0.015` in allowable limit for `Ti-6Al-4V Lot #8841-B`, `14` global fleet tails affected)
  * HITL Form 700 Release Package: `AWR-700-20261102-ZM151` (`SERVICEABLE_WITH_TORQUE_RECHECK` per `JTD Task Card 53-11-00-280`, gated by two-turn Lead Stress Engineer / CTO sign-off).
""".strip()
STATIC_S1000D_AND_ASIP_REFERENCE_HEADER = STATIC_S100D_AND_ASIP_REFERENCE_HEADER

COORDINATOR_INSTRUCTION = """You are `f35_sustainment_coordinator`, the Root Sustainment Coordinator for the F-35 Lightning II Fleet Sustainment Agent Platform (`f35-sustainment-agent`) running in `europe-west1` (Belgium) / `EU`.

ROUTING & ORCHESTRATION DIRECTIVES:
0. **UC0 Conversational Maintenance Log Explorer & Work Order Spreadsheet Queries** (`maintenance_work_orders`, ODIN / MOD Form 707A job control numbers `WO-2026-*`, `PRIORITY_1_RED_X`, `AWAITING_PARTS (MICAP)`, `NMC-S` / `NMC-M`, `wuc_code`, `work_center`, `assigned_shift_lead`, `estimated_mttr_hours`, `logged_man_hours`, squadron/base work-order breakdowns, Excel / Google Sheets spreadsheet cards, or `.csv` exports):
   - Delegate immediately to `f35_maintenance_data_agent` (`@F35-Maintenance-Data`).
1. **UC1 Supply Chain & Sortie Readiness Queries** (actuator flight hours, `ZM151` vs `ZM154`, `NSN 1680-01-619-4821` depot stock, sortie `SRT-MAR-20261103-01` tail swaps, Vega-Lite charts):
   - Delegate immediately to `f35_analytics_agent` (`@F35-Sustainment-Analytics`).
2. **UC2 Technical Publication & Cross-Service Maintenance Log Queries** (canopy catch/latch binding, `no BIT fault` mechanical rigging, S1000D JTD 53-30-01, USMC sister squadron sealant debris precedent, `220°C` High-Temp RAM Sheet `'B'` 4-hour cure):
   - Delegate immediately to `f35_jtd_search_agent` (`@F35-JTD-Search`).
3. **UC3 Dynamic Flight Envelope Exceedance, ASIP Structural Physics, C-Scan NDI & Form 700 HITL Release** (`9.4 G` split-S shudder, `Frame 496`, Rainflow / Miner's Rule damage, `DOC-06` ultrasonic C-Scan, `Hole #14`, `Lot #8841-B`, MIL-STD-3001 SAR, Form 700 staging or Lead Stress Engineer / CTO release approval):
   - Delegate immediately to `f35_airworthiness_orchestrator` (`@F35-Airworthiness-Agent`).
"""
ROOT_COORDINATOR_INSTRUCTION = COORDINATOR_INSTRUCTION

root_agent = LlmAgent(
    name="f35_sustainment_coordinator",
    description=(
        "Root coordinator for the F-35 Lightning II Fleet Sustainment Agent Platform "
        "in europe-west1 / EU. Routes requests across UC0 Maintenance Data, UC1 Analytics, "
        "UC2 JTD Search, and UC3 Airworthiness specialist sub-agents."
    ),
    model=get_gemini_model(
        model_name=COORDINATOR_MODEL,
        thinking_level="LOW",
        temperature=0.0,
    ),
    generate_content_config=get_generate_content_config(
        thinking_level="LOW",
        temperature=0.0,
    ),
    static_instruction=STATIC_S1000D_AND_ASIP_REFERENCE_HEADER,
    instruction=COORDINATOR_INSTRUCTION,
    sub_agents=[
        f35_maintenance_data_agent,
        f35_analytics_agent,
        f35_jtd_search_agent,
        f35_airworthiness_orchestrator,
    ],
    before_model_callback=fast_path_before_model_callback,
    before_tool_callback=enforce_hitl_airworthiness_gate,
)

app = App(
    name="app",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,
        ttl_seconds=1800,
        cache_intervals=10,
    ),
)

__all__ = ["COORDINATOR_INSTRUCTION", "ROOT_COORDINATOR_INSTRUCTION", "app", "root_agent"]
