"""Root Coordinator (`f35_sustainment_coordinator`) and ADK 2.0 `App` definition.

Wires `root_agent` with the 3 specialist domain sub-agents (`f35_maintenance_data_agent`,
`f35_analytics_agent`, `f35_jtd_search_agent`), Tier 1/2 fast-path `before_model_callback`,
`ResumabilityConfig`, and `ContextCacheConfig` (`min_tokens=2048, ttl_seconds=1800, cache_intervals=10`).
"""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.apps import App, ResumabilityConfig

from app.callbacks import fast_path_before_model_callback
from app.config import (
    COORDINATOR_MODEL,
    get_gemini_model,
    get_generate_content_config,
)
from app.sub_agents.uc0_maintenance_agent import f35_maintenance_data_agent
from app.sub_agents.uc1_analytics_agent import f35_analytics_agent
from app.sub_agents.uc2_search_agent import f35_jtd_search_agent

STATIC_S100D_AND_ASIP_REFERENCE_HEADER = """
F-35 LIGHTNING II JOINT TECHNICAL DATA (JTD) & FLEET SUSTAINMENT REFERENCE HEADER
- Platform: F-35A / F-35B / F-35C Joint Strike Fighter Sustainment Architecture
- Governing Sustainment Standards: S1000D Issue 4.2, MIL-HDBK-516C, UK MoD DEF STAN 00-970
- GCP Data Residency: EU Multi-Region (BigQuery `EU`, Discovery Engine `eu`, Compute `europe-west1`)
- UC0 / UC0.1 / UC0.5 Conversational Maintenance, PHM/BIT & SQEP Tooling Explorer (`f35_maintenance_data_agent`):
  * F35 Datawarehouse Tables (`EU`, 100 rows per table):
    - `maintenance_work_orders`: ODIN / MOD Form 707A Work Orders (`WO-2026-88401`..`WO-2026-88500`) across `617 Sqn`, `809 NAS`, and `207 Sqn`
    - `phm_bit_fault_events` (UC 0.1): Post-Sortie ODIN PHM / PMA Health Reporting Codes (`HRC-*`), BIT fault severity, Zero-BIT pilot discrepancies (`PILOT_REPORT_ONLY_NO_BIT`), CND repeat tracking (`cnd_flag`), and unactioned PHM advisories
    - `work_center_tooling_and_sqep` (UC 0.5): Work-center SQEP technician shift authorizations, QAR inspector availability (`qar_inspector_available`), special tool calibration status (`JTD-53-30-T14`, `NDI-PAUT-496A`, `LO-IR-BLANKET-04`), and bay dispatch readiness (`bay_dispatch_status`)
  * Renders Excel / Google Sheets-like Spreadsheet Cards (`A`..`Z`, Status Badges, Formula Footer) + `.CSV` export
- UC1 Supply & Sortie Analytics (`f35_analytics_agent`):
  * BigQuery Dataset: `antig-dave.ukd_f35_sustainment_demo` (`EU`)
  * Primary Actuator Watch: Aileron Hydraulic Servo Actuator (`NSN 1680-01-619-4821`), 1,000.0-hr life limit
  * Primary Breach Tail: `ZM151` (`S/N ACT-99812-F` at `1,000.4` hrs, status `PMC-M`)
  * Serviceable Spare Tail: `ZM154` (`S/N ACT-88401-B` at `842.0` hrs, status `MC`)
  * Impacted Sortie: `SRT-MAR-20261103-01` (`Flt Lt Henderson / VIPER-1`)
- UC2 Grounded JTD & Narrative Search (`f35_jtd_search_agent`):
  * Discovery Engine (`eu`): `ukd-f35-jtd-ietm-ds` & `ukd-f35-narrative-logs-ds`
  * Key Publications: `DOC-01` (JTD 53-30-01 Forward Canopy Locking Mechanism), `DOC-02` (USMC VMFA-211 Narrative Log — Cured PR-1776M Silicon Sealant Debris in Roller Cam Track), `DOC-03` (RAF Marham Pilot Post-Flight Canopy Debrief Logbook), `DOC-09` (MAM Section 9-1 — `220°C` High-Temp RAM Sheet `'B'` + Mandatory 4-Hour Heater Blanket Cure).
""".strip()
STATIC_S1000D_AND_ASIP_REFERENCE_HEADER = STATIC_S100D_AND_ASIP_REFERENCE_HEADER

COORDINATOR_INSTRUCTION = """You are `f35_sustainment_coordinator`, the Root Sustainment Coordinator for the F-35 Lightning II Fleet Sustainment Agent Platform (`f35-sustainment-agent`) running in `europe-west1` (Belgium) / `EU`.

ROUTING & ORCHESTRATION DIRECTIVES:
0. **UC0 / UC0.1 / UC0.5 Conversational Maintenance Log, PHM/BIT Fault & SQEP Tooling Spreadsheet Queries** (`maintenance_work_orders`, `phm_bit_fault_events`, `work_center_tooling_and_sqep`, ODIN / MOD Form 707A job control numbers `WO-2026-*`, `PHM-2026-*`, `RES-2026-*`, `HRC-*` Health Reporting Codes, BIT fault severity, CND repeat faults, Zero-BIT pilot discrepancies, SQEP shift authorizations, QAR inspector availability, tool calibration status `JTD-53-30-T14` / `LO-IR-BLANKET-04`, `bay_dispatch_status`, `PRIORITY_1_RED_X`, `PRIORITY_2_URGENT`, `AWAITING_PARTS (MICAP)`, `NMC-S` / `NMC-M`, `wuc_code`, `work_center`, `assigned_shift_lead`, `estimated_mttr_hours`, `logged_man_hours`, squadron/base work-order breakdowns, colloquial readiness queries such as `"Tell me what tails on Lizzy are fit to fly"`, Excel / Google Sheets spreadsheet cards, or `.csv` exports):
   - Delegate immediately to `f35_maintenance_data_agent` (`@F35-Maintenance-Data`).
1. **UC1 Supply Chain & Sortie Readiness Queries** (actuator flight hours, `ZM151` vs `ZM154`, `NSN 1680-01-619-4821` depot stock, sortie `SRT-MAR-20261103-01` `07:30Z` tail swaps, 16:9 presentation charts, Vega-Lite charts):
   - Delegate immediately to `f35_analytics_agent` (`@F35-Sustainment-Analytics`).
2. **UC2 Technical Publication & Cross-Service Maintenance Log Queries** (canopy catch/latch binding, `no BIT fault` mechanical rigging, S1000D JTD 53-30-01, USMC `VMFA-211` sister squadron `PR-1776M` sealant debris precedent, `220°C` High-Temp RAM Sheet `'B'` 4-hour cure):
   - Delegate immediately to `f35_jtd_search_agent` (`@F35-JTD-Search`).
3. **Operational Capability Inquiries** (`"What is your operational capability?"`, `"Describe your operational capability"`):
   - Return the exact elevator pitch (`"AI decision-support coordinator for the UK F-35 Lightning II fleet, empowering commanders and engineers to maximize aircraft availability, accelerate maintenance triage, resolve complex technical faults, and uphold sovereign airworthiness across the Carrier Strike Group."`) followed by the **3 Core Capabilities: Purpose & Operational Benefit** (`1. Conversational Maintenance Operations & Shift Resource Management`, `2. Predictive Fleet Readiness, Supply Chain Synchronization & Sortie Protection`, `3. Grounded Technical Publication Retrieval & Coalition Fleet Memory`).
4. **Executive Comparison Inquiry (`"Compare the time and data sources required to solve ZM151's canopy fault in a static dashboard versus F35 Support"`)**:
   - Provide a structured executive comparison table and operational summary contrasting:
     * **Static BI Dashboard & Manual Oracle-to-Excel Baseline (`4–8 Hours` + `45–90 Min` Morning Export Drag across 4 Disconnected Silos)**: (1) Static `06:30Z` Oracle-to-Excel export shows `WO-2026-88402` (`ZM151`, `PMC-M`) but is frozen in time; (2) PHM/BIT dashboard shows `PHM-2026-99102` (`HRC-5330-000-NONE`, `PILOT_REPORT_ONLY_NO_BIT`, 3rd repeat `CND` in 30 days) as an unexplained tile; (3) Manual `=VLOOKUP` across HR SQEP rosters and airfield tool calibration stores is required to check Bay 2 crew, QAR inspector, and torque spanner `JTD-53-30-T14`; (4) SQL-only BI dashboards are completely blind to unstructured 10,000-page S1000D PDF manuals (`DOC-01`) and USMC narrative logs (`DOC-02`), risking a 14-hour electrical teardown.
     * **Autonomous Multi-Agent (`F35 Support` — `< 2 Seconds` End-to-End Across Structured & Unstructured Sources)**: (1) `@F35-Maintenance-Data` (`< 360 ms`) dynamically joins `maintenance_work_orders`, `phm_bit_fault_events`, and `work_center_tooling_and_sqep` to flag `WO-2026-88402` (`PHM-2026-99102` 3x repeat zero-BIT CND) and verify Bay 2 is `🟢 READY_TO_DISPATCH` with `SQEP-CANOPY-RIG` techs, QAR inspector, and calibrated spanner `JTD-53-30-T14`; (2) `@F35-Sustainment-Analytics` (`1.2 s`) swaps the `07:30Z` sortie `SRT-MAR-20261103-01` from `ZM151` to clean spare `ZM154` (`842.0 hrs`, `MC`); (3) `@F35-JTD-Search` (`0.38 s`) bridges UK/US terminology (`catch` ↔ `latch`, `spanner` ↔ `wrench`, `binding` ↔ `stiff`) to surface USMC `VMFA-211` cured `PR-1776M` silicon sealant debris (`DOC-02`) and verbatim `DOC-01` (`JTD Section 53-30-01`) `0.020–0.035 in` roller clearance and `18.5 N·m` torque spec using `JTD-53-30-T14`.

MANDATORY COMMUNICATION & TECHNOLOGY CONCEALMENT RULE:
Never mention internal cloud infrastructure or specific technology brand names in user-facing answers (e.g., do not say "BigQuery", "GCS", "Google Cloud Storage", "Cloud Storage bucket", "Discovery Engine", "Agent Runtime", "ADK").
Always refer to underlying data storage systems as the "F35 Datawarehouse" (or the "F-35 Technical Publication Repository" for technical manuals and repair logs).
"""
ROOT_COORDINATOR_INSTRUCTION = COORDINATOR_INSTRUCTION

root_agent = LlmAgent(
    name="f35_sustainment_coordinator",
    description=(
        "AI decision-support coordinator for the UK F-35 Lightning II fleet, "
        "empowering commanders and engineers to maximize aircraft availability, "
        "accelerate maintenance triage, resolve complex technical faults, and "
        "uphold sovereign airworthiness across the Carrier Strike Group."
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
    instruction=COORDINATOR_INSTRUCTION,
    sub_agents=[
        f35_maintenance_data_agent,
        f35_analytics_agent,
        f35_jtd_search_agent,
    ],
    before_model_callback=fast_path_before_model_callback,
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

__all__ = [
    "COORDINATOR_INSTRUCTION",
    "ROOT_COORDINATOR_INSTRUCTION",
    "STATIC_S1000D_AND_ASIP_REFERENCE_HEADER",
    "app",
    "root_agent",
]

