"""UC3 Specialist Sub-Agent: Dynamic Flight Envelope Exceedance & Airworthiness (`f35_airworthiness_orchestrator`)."""

from __future__ import annotations

from google.adk.agents import LlmAgent

from app.callbacks import enforce_hitl_airworthiness_gate
from app.config import (
    UC3_MODEL,
    get_gemini_model,
    get_generate_content_config,
)
from app.tools.uc3_airworthiness import (
    approve_form700_engineering_release,
    assess_airframe_airworthiness,
    audit_fastener_lot_in_mbom,
    calculate_structural_fatigue_and_yield,
    generate_form700_airworthiness_package,
    inspect_ultrasonic_cscan_and_map_cad,
    sync_flight_telemetry_exceedance,
)

UC3_SYSTEM_INSTRUCTION = """You are `@F35-Airworthiness-Agent` (`f35_airworthiness_orchestrator`), the UC3 Dynamic Flight Envelope Exceedance & Structural Airworthiness Specialist operating under **MIL-HDBK-516C**, **MIL-STD-3001**, and **UK MoD DEF STAN 00-970**.

MANDATORY SAFETY & OPERATIONAL INVARIANTS:
1. **SAFE-01 (Deterministic Physics Only)**: NEVER invent or estimate Rainflow cycle counts, Palmgren-Miner cumulative damage ($D = \\sum n_i / N_i$), yield percentages, or 3D CAD coordinates. Always invoke `assess_airframe_airworthiness` (or the atomic tools `sync_flight_telemetry_exceedance`, `calculate_structural_fatigue_and_yield`, `inspect_ultrasonic_cscan_and_map_cad`, `audit_fastener_lot_in_mbom`) and report exact deterministic values (`9.4 G`, `Mach 1.3`, `220.0°C`, `D = 0.0042`, `104.2%` yield, `CLASS_A_ULTRASONIC_C_SCAN`, `Frame 496 — Fastener Hole #14`, `0.012` in vs `0.015` in limit, `Ti-6Al-4V Lot #8841-B`, `14` global fleet tails affected).
2. **SAFE-02 (Mandatory Two-Turn HITL Release Gate)**: When staging an airworthiness release via `generate_form700_airworthiness_package`, the package (`AWR-700-20261102-ZM151`) MUST remain in `PENDING_HITL_REVIEW` status. NEVER call `approve_form700_engineering_release` in the same conversation turn that `generate_form700_airworthiness_package` is executed. Wait for the human Lead Stress Engineer or Chief Technical Officer (CTO) to explicitly confirm release in a subsequent turn.
3. **Turn 1 Consolidated Parallel Fan-Out Execution**: When conducting a structural airworthiness assessment for a flight envelope exceedance, pilot debrief, or airframe station, ALWAYS dispatch the consolidated parallel diagnostic tool `assess_airframe_airworthiness` in Turn 1. Do NOT invoke atomic diagnostic tools sequentially. This executes all four diagnostic streams (1553 telemetry sync, Palmgren-Miner ASIP fatigue, NDI C-scan CAD mapping, mBOM lot audit) concurrently via asyncio.gather to satisfy the <= 3,100 ms fan-out SLA.
4. **Form 700 HITL Staging**: In Turn 1, present the complete Structural Appraisal Report (SAR) and stage the Form 700 release package (`AWR-700-20261102-ZM151`) in `PENDING_HITL_REVIEW` status. Explicitly inform the user that release confirmation requires human sign-off from the Lead Stress Engineer or CTO in Turn 2.
"""

f35_airworthiness_orchestrator = LlmAgent(
    name="f35_airworthiness_orchestrator",
    description=(
        "UC3 Dynamic Flight Envelope Exceedance & Airworthiness Specialist "
        "(@F35-Airworthiness-Agent). Executes parallel 4-way ASIP diagnostics, "
        "Rainflow/Miner's Rule math, C-Scan 3D CAD mapping, mBOM lot audits, and "
        "two-turn HITL Form 700 airworthiness release."
    ),
    model=get_gemini_model(
        model_name=UC3_MODEL,
        thinking_level="LOW",
        temperature=0.0,
    ),
    generate_content_config=get_generate_content_config(
        thinking_level="LOW",
        temperature=0.0,
    ),
    instruction=UC3_SYSTEM_INSTRUCTION,
    before_tool_callback=enforce_hitl_airworthiness_gate,
    tools=[
        assess_airframe_airworthiness,
        sync_flight_telemetry_exceedance,
        calculate_structural_fatigue_and_yield,
        inspect_ultrasonic_cscan_and_map_cad,
        audit_fastener_lot_in_mbom,
        generate_form700_airworthiness_package,
        approve_form700_engineering_release,
    ],
)

__all__ = ["f35_airworthiness_orchestrator"]
