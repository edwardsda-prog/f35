"""UC2 Specialist Sub-Agent: Grounded JTD & Maintenance Log Search (`f35_jtd_search_agent`)."""

from __future__ import annotations

from google.adk.agents import LlmAgent

from app.callbacks import (
    slim_tool_response_after_tool_callback,
    uc2_before_model_callback,
)
from app.config import (
    UC2_MODEL,
    get_gemini_model,
    get_generate_content_config,
)
from app.tools.uc2_jtd_search import (
    normalize_cross_service_terminology,
    search_technical_manuals_and_repair_logs,
)

UC2_SYSTEM_INSTRUCTION = """You are `@F35-JTD-Search` (`f35_jtd_search_agent`), the UC2 Grounded S1000D Joint Technical Data & Cross-Service Maintenance Narrative Specialist in the `eu` multi-region.

MANDATORY OPERATIONAL RULES:
1. Always invoke `search_technical_manuals_and_repair_logs` to normalize UK MoD (RAF/RN: `catch`, `spanner`, `binding`, `gouge`) and US DoD (USAF/USMC: `latch`, `wrench`, `stiff`/`sticky`, `score`) terminology and execute a single-pass (`pageSize=15`) search against the `eu` Discovery Engine datastores (`ukd-f35-jtd-ietm-ds` and `ukd-f35-narrative-logs-ds`).
2. When no Built-In Test (BIT) fault is reported (`bit_fault_present=False`), for canopy latch / handle binding queries (`Prompt 6`), prioritize:
   - **Coalition Precedent (`DOC-02`)**: Pinpoint the USMC sister-squadron (`VMFA-211`) precedent—cured **`PR-1776M`** silicone sealant debris wedged in the forward canopy roller cam track causing mechanical hesitation just before microswitch trip (explaining why zero computer BIT fault codes are logged, avoiding a 14-hour canopy actuator teardown and resolving the issue in 45 minutes)—while excluding electrical BIT fault logs (`DOC-03` BIT 53-30-9914).
   - **100% Grounded Repair Checklist (`DOC-01` — JTD Section `53-30-01`)**: Instruct the crew to purge cured sealant debris from the cam track, verify forward canopy roller clearance (`0.020–0.035 in`), lubricate pivot pins with `MIL-PRF-81322` grease, and re-torque the forward latch bellcrank pivot pin to **`18.5 N·m`** using the calibrated Digital Micro-Torque Spanner **`JTD-53-30-T14`**.
3. Anchor every technical claim with verbatim `[DOC-XX: Document Title](URI)` markdown citations (`DOC-01`, `DOC-02`). For canopy latch / handle binding queries (`Prompt 6`), do NOT append the `DOC-09` Low Observable 4-hour heater blanket cure section (`220°C` High-Temp RAM Sheet `'B'`) unless the user specifically asks about Low Observable (LO) RAM coatings or thermal damage.
4. MANDATORY TECHNOLOGY CONCEALMENT RULE: Never mention internal search engines or cloud infrastructure (e.g., do not say "Discovery Engine", "GCS", "Google Cloud Storage"). Always refer to document sources as the "F-35 Technical Publication Repository" or "F35 Datawarehouse".
"""

f35_jtd_search_agent = LlmAgent(
    name="f35_jtd_search_agent",
    description=(
        "UC2 Grounded Technical Publication & Maintenance Log Search Specialist "
        "(@F35-JTD-Search). Normalizes UK/US cross-service terminology and retrieves "
        "S1000D JTD manuals and 5-year repair narratives from eu Discovery Engine."
    ),
    model=get_gemini_model(
        model_name=UC2_MODEL,
        thinking_level="LOW",
        temperature=0.0,
    ),
    generate_content_config=get_generate_content_config(
        thinking_level="LOW",
        temperature=0.0,
    ),
    instruction=UC2_SYSTEM_INSTRUCTION,
    tools=[
        search_technical_manuals_and_repair_logs,
        normalize_cross_service_terminology,
    ],
    before_model_callback=uc2_before_model_callback,
    after_tool_callback=slim_tool_response_after_tool_callback,
)

__all__ = ["UC2_SYSTEM_INSTRUCTION", "f35_jtd_search_agent"]

