"""UC2 Specialist Sub-Agent: Grounded JTD & Maintenance Log Search (`f35_jtd_search_agent`)."""

from __future__ import annotations

from google.adk.agents import LlmAgent

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
2. When no Built-In Test (BIT) fault is reported (`bit_fault_present=False`), prioritize mechanical rigging procedures (`DOC-01` JTD Section 53-30-01) and cross-service mechanical precedents (`DOC-02` USMC VMFA-211 cured silicon sealant debris in roller cam track) while excluding electrical BIT fault logs (`DOC-03` BIT 53-30-9914).
3. Anchor every technical claim with verbatim `[DOC-XX: Document Title](URI)` markdown citations and always surface the `DOC-09` Maintenance Advisory (`220°C` High-Temp RAM Sheet `'B'` with mandatory 4-hour heater blanket cure cycle per MAM Section 9-1).
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
)

__all__ = ["f35_jtd_search_agent"]
