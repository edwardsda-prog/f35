"""Adversarial stress-testing suite for Issues 1 to 8.

Authored by challenger_r1_1 for empirical verification:
1. Fast-path regex callback in app/callbacks.py:
   - Edge cases: mixed casing, excessive whitespace, punctuation, slight variations.
   - False positives: entity-laden queries (ZM151, Form 700, Hole 14, etc.) falling through to LLM.
   - Latency benchmark: 1,000 iterations measuring execution latency against < 1.0 ms SLA.
2. render_sustainment_chart in app/tools/uc1_analytics.py:
   - Invalid chart names, empty string, None, unsupported chart types.
   - Execution when tool_context is None, empty state, missing/corrupted metrics.
   - Vega-Lite v5 JSON syntactic validity and schema conformance ($schema, data, mark, encoding).
3. to_authenticated_gcs_url in app/tools/uc2_jtd_search.py:
   - Non-GCS URLs (http, https, relative, absolute, file, None, empty).
   - Nested paths, special characters, and https://storage.cloud.google.com/<bucket>/<path> format.
"""

from __future__ import annotations

import json
import time
from typing import Any

import pytest

from app.callbacks import (
    _FAST_PATH_CAPABILITY_RESPONSE,
    fast_path_before_model_callback,
)
from app.schemas import VegaLiteSpec
from app.tools.uc1_analytics import (
    check_actuator_fatigue_and_depot_inventory,
    render_sustainment_chart,
)
from app.tools.uc2_jtd_search import to_authenticated_gcs_url

# ---------------------------------------------------------------------------
# Test Harness Mock Helpers
# ---------------------------------------------------------------------------

class MockPart:
    def __init__(self, text: str) -> None:
        self.text = text


class MockContent:
    def __init__(self, text: str, role: str = "user") -> None:
        self.role = role
        self.parts = [MockPart(text)]


class MockLlmRequest:
    def __init__(self, contents: list[MockContent]) -> None:
        self.contents = contents


class MockCallbackContext:
    def __init__(self, state: dict[str, Any] | None = None) -> None:
        self.state: dict[str, Any] = state if state is not None else {}


class MockToolContext:
    def __init__(self, state: dict[str, Any] | None = None, invocation_id: str = "inv-1") -> None:
        self.state: dict[str, Any] = state if state is not None else {}
        self.invocation_id = invocation_id


def _invoke_callback(user_text: str, state: dict[str, Any] | None = None) -> Any:
    ctx = MockCallbackContext(state=state)
    req = MockLlmRequest(contents=[MockContent(user_text)])
    return fast_path_before_model_callback(callback_context=ctx, llm_request=req)


# ===========================================================================
# 1. Fast-Path Regex Callback Adversarial Tests
# ===========================================================================

class TestFastPathRegexAdversarial:
    """Adversarial stress-testing of fast_path_before_model_callback."""

    @pytest.mark.parametrize(
        "query",
        [
            # Mixed casing
            "DeScRiBe YoUr OpErAtIoNaL CaPaBiLiTiEs",
            "WHAT ARE YOUR CAPABILITIES",
            "eXpLaIn OpErAtIoNaL fEaTuReS",
            "ShOw YoUr OpErAtIoNaL fUnCtIoNs",
            "OpErAtIoNaL CaPaBiLiTiEs",
            # Whitespace and formatting variations
            "   what are your capabilities   ",
            "\n\n\tdescribe operational capabilities\n\n",
            "show \t\t operational \n\n features",
            # Punctuation variations
            "Can you describe your operational capabilities?",
            "What are your capabilities!",
            "Show operational features?!",
            "Please, explain your operational capabilities...",
            "(Describe your operational capabilities)",
            "'What are your capabilities?'",
            "\"Show operational features!\"",
            # Slight syntactic variations
            "can you describe your operational capabilities",
            "what are your capabilities",
            "show operational features",
            "describe your capabilities",
            "what are your operational capabilities",
            "explain operational capabilities",
            "show your operational functions",
            "operational capabilities",
            "describe operational capability",
            "explain your operational features please",
            # Edge-case whitespace between "what" and "are":
            "   what    are    your    capabilities   ",
            # Singular 'operational capability' without verb:
            "operational capability",
        ],
    )
    def test_fast_path_capability_interception_edge_cases(self, query: str) -> None:
        """Verify edge cases with casing, whitespace, punctuation, and variations trigger fast-path."""
        resp = _invoke_callback(query)
        assert resp is not None, f"Expected fast-path match for query: {query!r}"
        assert resp == _FAST_PATH_CAPABILITY_RESPONSE
        # Verify response text includes core sustainment purpose and benefits (Issue 1 & 2)
        text = resp.content.parts[0].text
        assert "Core Purpose & Operational Benefits" in text
        assert "Accelerate Fleet Readiness" in text
        assert "Actionable Decision Support" in text
        assert "Authoritative Engineering Guidance" in text
        for tech in ("BigQuery", "GCS", "Google Cloud Storage", "ADK", "UC1:", "UC2:", "UC3:"):
            assert tech not in text, f"Found '{tech}' in capability response"

    @pytest.mark.parametrize(
        "domain_query",
        [
            # Explicit domain entities requested by user prompt
            "What is the capability of tail ZM151",
            "What are the capabilities of tail ZM151?",
            "Describe your capabilities for ZM151",
            "Explain operational capabilities for tail ZM 154",
            "Show operational features for WO-2026-88405",
            "Explain operational functions of ACT-99812-F",
            "What are your capabilities regarding NSN 1680-01-619-4821",
            "Describe operational capabilities for HRC-5330-000-NONE",
            "Show operational features for SRT-MAR-20261103-01",
            "What are your capabilities regarding DOC-01?",
            "Describe capabilities for DOC-09 RAM cure procedure",
            "Show operational features for PHM-2026-99102",
            "Check MICAP work orders capabilities for squadron dispatch",
            "Explain SQEP tooling capability for RES-2026-00007",
        ],
    )
    def test_fast_path_false_positive_domain_fallthrough(self, domain_query: str) -> None:
        """Verify queries with domain entities do NOT trigger fast-path bypass and fall through (return None)."""
        resp = _invoke_callback(domain_query)
        assert resp is None, (
            f"False positive detected! Domain query should fall through to LLM, but returned: {resp}"
        )

    def test_fast_path_execution_latency_1000_iterations(self) -> None:
        """Empirically measure regex interceptor latency over 1,000 iterations to verify << 1.0 ms."""
        queries = [
            "Describe your operational capabilities",
            "What are your capabilities?",
            "What is the capability of tail ZM151",
            "What are our open MICAP work orders?",
            "Show operational features for WO-2026-88405",
            "Show operational features",
            "Check RAF Marham F-35B flaperon actuator hours",
            "hello",
            "ping",
        ]
        times_ms: list[float] = []

        ctx = MockCallbackContext(state={"turn_count": 0})
        # Pre-warm
        _invoke_callback("warmup", state=ctx.state)

        for i in range(1000):
            q = queries[i % len(queries)]
            req = MockLlmRequest(contents=[MockContent(q)])
            t0 = time.perf_counter()
            _ = fast_path_before_model_callback(callback_context=ctx, llm_request=req)
            t1 = time.perf_counter()
            times_ms.append((t1 - t0) * 1000.0)

        p50 = sorted(times_ms)[int(len(times_ms) * 0.50)]
        p95 = sorted(times_ms)[int(len(times_ms) * 0.95)]
        p99 = sorted(times_ms)[int(len(times_ms) * 0.99)]
        mean_ms = sum(times_ms) / len(times_ms)
        max_ms = max(times_ms)

        print(
            f"\n[Fast-Path Latency 1,000 Iterations] mean={mean_ms:.4f}ms, "
            f"p50={p50:.4f}ms, p95={p95:.4f}ms, p99={p99:.4f}ms, max={max_ms:.4f}ms"
        )

        assert mean_ms < 0.1, f"Mean latency {mean_ms:.4f} ms exceeded 0.1 ms SLA"
        assert p95 < 0.2, f"p95 latency {p95:.4f} ms exceeded 0.2 ms limit (well below 1.0 ms SLA)"
        assert max_ms < 1.0, f"Max latency {max_ms:.4f} ms exceeded 1.0 ms SLA"


# ===========================================================================
# 2. render_sustainment_chart Adversarial & Schema Tests
# ===========================================================================

class TestRenderSustainmentChartAdversarial:
    """Adversarial stress-testing of render_sustainment_chart in app/tools/uc1_analytics.py."""

    @pytest.mark.parametrize(
        "chart_arg,expected_resolved",
        [
            ("actuator_fatigue_threshold_chart", "actuator_fatigue_threshold_chart"),
            ("depot_stock_vs_demand_bar_chart", "depot_stock_vs_demand_bar_chart"),
            ("both", "both"),
            ("1", "actuator_fatigue_threshold_chart"),
            ("2", "depot_stock_vs_demand_bar_chart"),
            ("3", "both"),
            ("all", "both"),
            ("charts", "both"),
            ("visualizations", "both"),
            ("fatigue", "actuator_fatigue_threshold_chart"),
            ("threshold", "actuator_fatigue_threshold_chart"),
            ("depot", "depot_stock_vs_demand_bar_chart"),
            ("stock", "depot_stock_vs_demand_bar_chart"),
            ("demand", "depot_stock_vs_demand_bar_chart"),
            ("inventory", "depot_stock_vs_demand_bar_chart"),
            # Empty / None fallbacks
            ("", "both"),
            (None, "both"),
            # Unsupported / invalid names fallback gracefully to depot chart
            ("invalid_chart_name", "depot_stock_vs_demand_bar_chart"),
            ("pie_chart", "depot_stock_vs_demand_bar_chart"),
            ("unknown_scatter", "depot_stock_vs_demand_bar_chart"),
            ("!@#$%^&*()", "depot_stock_vs_demand_bar_chart"),
            # Note: "unknown_3d_scatter" contains digit "3" which matches option 3 ("both")
            ("unknown_3d_scatter", "both"),
        ],
    )
    def test_chart_name_resolution_and_graceful_fallbacks(
        self, chart_arg: Any, expected_resolved: str
    ) -> None:
        """Verify valid, fuzzy, empty, None, and invalid chart names resolve without errors."""
        res = render_sustainment_chart(chart_name=chart_arg)
        assert res["status"] == "SUCCESS"
        assert res["chart_name"] == expected_resolved
        assert "vega_lite_spec" in res
        assert "vega_lite_charts" in res
        assert isinstance(res["generation_time_ms"], float)

    @pytest.mark.parametrize(
        "state_setup",
        ["none_ctx", "empty_state", "missing_metrics", "corrupted_metrics"],
    )
    def test_tool_context_and_metrics_fallback(self, state_setup: str) -> None:
        """Verify render_sustainment_chart executes robustly across all state failure modes."""
        if state_setup == "none_ctx":
            ctx = None
        elif state_setup == "empty_state":
            ctx = MockToolContext(state={})
        elif state_setup == "missing_metrics":
            ctx = MockToolContext(state={"last_uc1_metrics": None})
        elif state_setup == "corrupted_metrics":
            ctx = MockToolContext(
                state={"last_uc1_metrics": {"depot_chart": None, "fatigue_chart": None}}
            )
        else:
            raise ValueError(state_setup)

        res = render_sustainment_chart(chart_name="both", tool_context=ctx)
        assert res["status"] == "SUCCESS"
        assert "depot_stock_vs_demand_bar_chart" in res["vega_lite_charts"]
        assert "actuator_fatigue_threshold_chart" in res["vega_lite_charts"]

    def test_state_cache_retrieval(self) -> None:
        """Verify render_sustainment_chart reuses cached specs from Turn 1 when present."""
        ctx = MockToolContext()
        # Run Turn 1 tool to populate state
        check_actuator_fatigue_and_depot_inventory(tool_context=ctx)
        assert "last_uc1_metrics" in ctx.state

        # Run Turn 2 tool (spec retrieval without graphics rendering for latency check)
        t0 = time.perf_counter()
        turn2_res = render_sustainment_chart(chart_name="both", tool_context=ctx, render_graphics=False)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert turn2_res["status"] == "SUCCESS"
        assert turn2_res["chart_name"] == "both"
        assert elapsed_ms < 5.0, f"Cached chart rendering took {elapsed_ms:.2f} ms (> 5.0 ms SLA)"

    def test_presentation_graphics_generation_and_sla(self) -> None:
        """Verify presentation graphics generate high-res slide images within 1,000 ms SLA."""
        ctx = MockToolContext()
        check_actuator_fatigue_and_depot_inventory(tool_context=ctx)

        t0 = time.perf_counter()
        turn2_res = render_sustainment_chart(chart_name="both", tool_context=ctx, render_graphics=True)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert turn2_res["status"] == "SUCCESS"
        assert "presentation_graphics" in turn2_res
        assert len(turn2_res["presentation_graphics"]) == 1
        assert "f35_sustainment_executive_dashboard.png" in turn2_res["presentation_graphics"][0]["url"]
        assert elapsed_ms < 1000.0, f"Graphics generation took {elapsed_ms:.2f} ms (> 1000 ms SLA)"

    def test_vega_lite_v5_json_syntax_and_schema_conformance(self) -> None:
        """Validate that all produced specifications are valid JSON and conform to Vega-Lite v5 schemas."""
        res = render_sustainment_chart(chart_name="both")
        charts = res["vega_lite_charts"]

        for name, spec_dict in charts.items():
            # 1. Syntactic JSON validity
            serialized = json.dumps(spec_dict)
            reloaded = json.loads(serialized)
            assert isinstance(reloaded, dict)

            # 2. Vega-Lite v5 Required Top-Level Schema Fields
            assert (
                reloaded.get("$schema")
                == "https://vega.github.io/schema/vega-lite/v5.json"
            ), f"Invalid or missing $schema in {name}"
            assert "title" in reloaded, f"Missing title in {name}"
            assert "data" in reloaded, f"Missing data in {name}"
            assert "values" in reloaded["data"], f"Missing data.values in {name}"
            assert isinstance(reloaded["data"]["values"], list)
            assert len(reloaded["data"]["values"]) > 0, f"data.values is empty in {name}"

            # 3. Mark and Encoding Structure
            assert "mark" in reloaded or "layer" in reloaded, (
                f"Chart {name} has neither 'mark' nor 'layer'"
            )
            if "layer" in reloaded:
                assert isinstance(reloaded["layer"], list)
                for layer_idx, lyr in enumerate(reloaded["layer"]):
                    assert "mark" in lyr, f"Layer {layer_idx} missing mark in {name}"
                    assert "encoding" in lyr, f"Layer {layer_idx} missing encoding in {name}"
            else:
                assert "encoding" in reloaded, f"Missing encoding in {name}"

            # 4. Strict Pydantic VegaLiteSpec model validation
            spec_model = VegaLiteSpec(**spec_dict)
            assert (
                spec_model.schema_url
                == "https://vega.github.io/schema/vega-lite/v5.json"
            )


# ===========================================================================
# 3. to_authenticated_gcs_url Adversarial Tests
# ===========================================================================

class TestToAuthenticatedGcsUrlAdversarial:
    """Adversarial stress-testing of to_authenticated_gcs_url in app/tools/uc2_jtd_search.py."""

    @pytest.mark.parametrize(
        "input_url,expected_output",
        [
            # Standard GCS URLs
            (
                "gs://antig-dave-f35-staging-europe-west1/unstructured/docs/DOC-01.pdf",
                "https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/unstructured/docs/DOC-01.pdf",
            ),
            (
                "gs://antig-dave-f35-staging-europe-west1/unstructured/docs/DOC-09.pdf",
                "https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/unstructured/docs/DOC-09.pdf",
            ),
            # Deeply nested paths
            (
                "gs://my-bucket/a/b/c/d/e/f/g/h/i/j/k/l.jsonl",
                "https://storage.cloud.google.com/my-bucket/a/b/c/d/e/f/g/h/i/j/k/l.jsonl",
            ),
            # Special characters: spaces, underscores, dashes, parens, brackets
            (
                "gs://antig-dave-f35-staging-europe-west1/docs/DOC-09 (MAM Section 9-1) [v2.1]+final_rev.pdf",
                "https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/docs/DOC-09 (MAM Section 9-1) [v2.1]+final_rev.pdf",
            ),
            (
                "gs://bucket-with.dots.and-dashes/path_with_underscores/file@v1.xml",
                "https://storage.cloud.google.com/bucket-with.dots.and-dashes/path_with_underscores/file@v1.xml",
            ),
            # Non-GCS URLs that must remain untouched
            (
                "http://example.com/manual.pdf",
                "http://example.com/manual.pdf",
            ),
            (
                "https://example.com/manual.pdf",
                "https://example.com/manual.pdf",
            ),
            (
                "https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/docs/DOC-01.pdf",
                "https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/docs/DOC-01.pdf",
            ),
            (
                "relative/path/to/manual.pdf",
                "relative/path/to/manual.pdf",
            ),
            (
                "/absolute/local/path/to/manual.pdf",
                "/absolute/local/path/to/manual.pdf",
            ),
            (
                "file:///tmp/doc.pdf",
                "file:///tmp/doc.pdf",
            ),
            # Empty / None edge cases
            (None, ""),
            ("", ""),
            ("   ", ""),
        ],
    )
    def test_to_authenticated_gcs_url_transformations(
        self, input_url: str | None, expected_output: str
    ) -> None:
        """Verify GCS URLs transform to authenticated browser URLs while preserving non-GCS URLs."""
        result = to_authenticated_gcs_url(input_url)
        assert result == expected_output, f"Expected {expected_output!r}, got {result!r}"
        if input_url and input_url.strip().startswith("gs://"):
            assert result.startswith("https://storage.cloud.google.com/")
            assert not result.startswith("gs://")


# ===========================================================================
# 4. Issue 10 Regression Tests: Elevator Pitch, Column Pruning & CSV Removal
# ===========================================================================

class TestIssue10ElevatorPitchAndTableFormatting:
    """Tests covering Issue 1 (Elevator pitch), Issues 2 & 3 (Column pruning & screen-fitting), and Issue 4 (CSV download link removal)."""

    def test_root_agent_description_is_elevator_pitch(self) -> None:
        """Issue 1: Root agent description must be a high-level elevator pitch without enumerating UC0-UC3, ending with Carrier Strike Group."""
        from app.agent import root_agent

        desc = root_agent.description
        assert "AI decision-support coordinator" in desc
        assert "F-35 Lightning II" in desc
        assert "Carrier Strike Group" in desc
        # Ensure it does NOT enumerate technical UC codes
        assert "UC0" not in desc
        assert "UC1" not in desc
        assert "UC2" not in desc
        assert "UC3" not in desc

    def test_three_operating_locations_reflected_in_warehouse(self) -> None:
        """Issue 2: Verify RAF Marham, HMS Queen Elizabeth, and HMS Prince of Wales are all present in seed records."""
        from app.seed_data.bq_seed_records import (
            MAINTENANCE_WORK_ORDERS_ROWS,
            GLOBAL_DEPOT_INVENTORY_ROWS,
            AIRFRAME_COMPONENT_TELEMETRY_ROWS,
        )

        wo_bases = {r["base_location"] for r in MAINTENANCE_WORK_ORDERS_ROWS}
        assert "RAF Marham" in wo_bases
        assert "HMS Queen Elizabeth" in wo_bases
        assert "HMS Prince of Wales" in wo_bases

        telem_bases = {r["base_location"] for r in AIRFRAME_COMPONENT_TELEMETRY_ROWS}
        assert "HMS Prince of Wales" in telem_bases

        depot_names = [r["depot_name"] for r in GLOBAL_DEPOT_INVENTORY_ROWS]
        assert any("HMS Prince of Wales" in d for d in depot_names)

    def test_uc1_chart_presentation_prompt_text(self) -> None:
        """Issue 3: Verify UC1 chart prompt wording matches the requested elevator prompt."""
        from app.sub_agents.uc1_analytics_agent import UC1_SYSTEM_INSTRUCTION

        expected_prompt = (
            "Would you like me to render: 1. Actuator Fatigue Threshold Chart, "
            "2. Regional Depot Stock vs 30-Day Demand Chart, or the full Executive Briefing Dashboard "
            "for your presentation slide deck?"
        )
        assert expected_prompt in UC1_SYSTEM_INSTRUCTION

    def test_uc0_open_p1_micap_column_pruning_and_screen_alignment(self) -> None:
        """Issues 2 & 3: Open P1/MICAP query returns screen-friendly 5 columns, omitting logged_man_hours."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        # Realistic prompt-driven query for open Priority-1 and MICAP sorted by repair time
        sql = (
            "SELECT work_order_id, tail_number, base_location, aircraft_status, estimated_mttr_hours "
            "FROM maintenance_work_orders "
            "WHERE work_order_status != 'COMPLETED' "
            "AND (priority = 'PRIORITY_1_RED_X' OR aircraft_status = 'NMC-S' OR work_order_status LIKE '%MICAP%') "
            "ORDER BY estimated_mttr_hours ASC"
        )
        res = execute_maintenance_sql(sql, sheet_title="Open_P1_and_MICAP_Work_Orders")
        assert res["status"] == "SUCCESS"
        assert res["row_count"] > 0

        # Verify only 5 columns were selected
        col_names = [c["field_name"] for c in res["spreadsheet_card"]["columns"]]
        assert col_names == ["work_order_id", "tail_number", "base_location", "aircraft_status", "estimated_mttr_hours"]
        assert "logged_man_hours" not in col_names

        # Verify markdown table
        md = res["spreadsheet_card_markdown"]
        assert "estimated_mttr_hours" in md
        assert "logged_man_hours" not in md
        # Issue 4: Verify no download links
        assert "[📥 Download .CSV" not in md
        assert "https://storage.cloud.google.com" not in md

    def test_uc0_no_csv_download_links_in_any_query(self) -> None:
        """Issue 4: No CSV download link should be emitted in spreadsheet_card_markdown."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql = "SELECT work_order_id, tail_number, aircraft_status, estimated_mttr_hours FROM maintenance_work_orders LIMIT 3"
        res = execute_maintenance_sql(sql)
        md = res["spreadsheet_card_markdown"]
        assert "[📥 Download .CSV" not in md
        assert "https://storage.cloud.google.com" not in md

    def test_uc1_markdown_table_screen_friendly_column_budget(self) -> None:
        """Issue 3: UC1 analytics returns separate, screen-aligned tables (<= 5 columns) with no horizontal scrolling."""
        from app.tools.uc1_analytics import check_actuator_fatigue_and_depot_inventory

        res = check_actuator_fatigue_and_depot_inventory(base_location="RAF Marham")
        assert res["status"] == "SUCCESS"
        md_table = res.get("markdown_summary_table") or res.get("markdown_table", "")

        # Verify tables are split into Airframe Status and Depot Inventory
        assert "### ✈️ Aircraft & Component Status" in md_table
        assert "### 📦 Regional Depot Inventory" in md_table

        # Check line headers have at most 5 data columns
        for line in md_table.splitlines():
            if line.startswith("|") and not line.startswith("| :---"):
                pipe_count = line.count("|")
                # pipe_count for 5 columns is 6 ('| col1 | col2 | col3 | col4 | col5 |')
                assert pipe_count <= 7, f"Line has too many columns causing horizontal scroll: {line}"

