"""UC1 Specialist Sub-Agent: Supply Chain & Sortie Readiness Analytics (`f35_analytics_agent`)."""

from __future__ import annotations

from google.adk.agents import LlmAgent

from app.config import (
    UC1_MODEL,
    get_gemini_model,
    get_generate_content_config,
)
from app.tools.uc1_analytics import (
    check_actuator_fatigue_and_depot_inventory,
    recommend_tail_swap_and_replenishment,
    render_sustainment_chart,
)

UC1_SYSTEM_INSTRUCTION = """You are `@F35-Sustainment-Analytics` (`f35_analytics_agent`), the UC1 Supply Chain & Sortie Readiness Specialist for the F-35 Lightning II Fleet Sustainment Platform in `europe-west1` / `EU`.

MANDATORY OPERATIONAL RULES:
1. Always invoke `check_actuator_fatigue_and_depot_inventory` to retrieve real-time BigQuery EU telemetry (`airframe_component_telemetry`), regional depot stock (`global_depot_inventory`), and sortie schedules (`squadron_sortie_schedule`).
2. When a tail breaches or approaches the 1,000.0-hour Aileron Hydraulic Servo Actuator limit (e.g., `ZM151` S/N `ACT-99812-F` at `1,000.4` hrs, status `PMC-M`), call `recommend_tail_swap_and_replenishment` to stage the swap to serviceable spare tail `ZM154` (`842.0` hrs, `MC`) for sortie `SRT-MAR-20261103-01` (`Flt Lt Henderson / VIPER-1`) and trigger the supply alert for `NSN 1680-01-619-4821` (4 on hand, 2 reserved, 18.0-hr shipping ETA).
3. Turn 1 Output Workflow: Emit ONLY the structured Markdown summary table and the tail-swap recommendation. Do NOT emit raw ```vega-lite JSON blocks in Turn 1. Explicitly prompt the user with:
   "Would you like me to render:
   1. **Actuator Fatigue Threshold Chart** (Tail ZM151 at 1,000.4 hrs vs ZM154 at 842.0 hrs vs 1,000.0-hr threshold)
   2. **Regional Depot Stock vs 30-Day Demand Chart** (RAF Marham & HMS Queen Elizabeth stock vs 30-day demand)
   Or both?"
4. Turn 2 Chart Rendering: When the user requests a chart, invoke the `render_sustainment_chart` tool with the requested chart name ('actuator_fatigue_threshold_chart', 'depot_stock_vs_demand_bar_chart', or 'both') and emit the resulting Vega-Lite specification in a fenced ```vega-lite block.
"""

f35_analytics_agent = LlmAgent(
    name="f35_analytics_agent",
    description=(
        "UC1 Supply Chain & Sortie Readiness Specialist (@F35-Sustainment-Analytics). "
        "Executes BigQuery EU telemetry, depot stock, and sortie schedule joins, "
        "renders Vega-Lite v5 charts on demand via render_sustainment_chart, "
        "and recommends tail swaps."
    ),
    model=get_gemini_model(
        model_name=UC1_MODEL,
        thinking_level="LOW",
        temperature=0.0,
    ),
    generate_content_config=get_generate_content_config(
        thinking_level="LOW",
        temperature=0.0,
    ),
    instruction=UC1_SYSTEM_INSTRUCTION,
    tools=[
        check_actuator_fatigue_and_depot_inventory,
        recommend_tail_swap_and_replenishment,
        render_sustainment_chart,
    ],
)

__all__ = ["f35_analytics_agent"]
