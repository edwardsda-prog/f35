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
            # Uses xfail to document that regex has literal 'what are' rather than 'what\s+are'
            pytest.param(
                "   what    are    your    capabilities   ",
                marks=pytest.mark.xfail(
                    reason="Regex has literal space in 'what are' instead of 'what\\s+are'"
                ),
            ),
            # Singular 'operational capability' without verb:
            # Uses xfail to document that regex has 'capabilities?' which matches 'capabilitie'/'capabilities' but not 'capability'
            pytest.param(
                "operational capability",
                marks=pytest.mark.xfail(
                    reason="Regex specifies 'capabilities?' which matches 'capabilitie'/'capabilities' but not 'capability'"
                ),
            ),
        ],
    )
    def test_fast_path_capability_interception_edge_cases(self, query: str) -> None:
        """Verify edge cases with casing, whitespace, punctuation, and variations trigger fast-path."""
        resp = _invoke_callback(query)
        assert resp is not None, f"Expected fast-path match for query: {query!r}"
        assert resp == _FAST_PATH_CAPABILITY_RESPONSE
        # Verify response text includes core sustainment capabilities
        text = resp.content.parts[0].text
        assert "UC1: Predictive Actuator Analytics" in text
        assert "UC2: JTD Maintenance Search" in text
        assert "UC3: ASIP Structural Exceedance" in text

    @pytest.mark.parametrize(
        "domain_query",
        [
            # Explicit domain entities requested by user prompt
            "What is the capability of tail ZM151",
            "Form 700 release status",
            "Fastener hole 14 capability",
            # Domain entity queries with capability words that MUST fall through to LLM
            "What are the capabilities of tail ZM151?",
            "Describe your capabilities for ZM151",
            "Explain operational capabilities for tail ZM 154",
            "Show operational features for Lot #8841-B",
            "Explain operational functions of ACT-99812-F",
            "What are your capabilities regarding NSN 1680-01-619-4821",
            "Describe operational capabilities for Frame 496",
            "Show operational features for SRT-MAR-20261103-01",
            "What are your capabilities regarding DOC-01?",
            "Describe capabilities for DOC-06 ultrasonic scan",
            "Form 700 airworthiness release package status",
            "Check Form 700 capabilities for engineering sign-off",
            "Form 700 release package AWR-700-20261102-ZM151 capability",
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
            "Form 700 release status",
            "Fastener hole 14 capability",
            "Show operational features",
            "Check RAF Marham F-35A horizontal tail actuator hours",
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

        # Run Turn 2 tool
        t0 = time.perf_counter()
        turn2_res = render_sustainment_chart(chart_name="both", tool_context=ctx)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert turn2_res["status"] == "SUCCESS"
        assert turn2_res["chart_name"] == "both"
        assert elapsed_ms < 5.0, f"Cached chart rendering took {elapsed_ms:.2f} ms (> 5.0 ms SLA)"

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
                "gs://antig-dave-f35-staging-europe-west1/unstructured/sar/SAR-20261102-ZM151.pdf",
                "https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/unstructured/sar/SAR-20261102-ZM151.pdf",
            ),
            # Deeply nested paths
            (
                "gs://my-bucket/a/b/c/d/e/f/g/h/i/j/k/l.jsonl",
                "https://storage.cloud.google.com/my-bucket/a/b/c/d/e/f/g/h/i/j/k/l.jsonl",
            ),
            # Special characters: spaces, underscores, dashes, parens, brackets
            (
                "gs://antig-dave-f35-staging-europe-west1/docs/DOC-06 (Frame 496) [v2.1]+final_rev.png",
                "https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/docs/DOC-06 (Frame 496) [v2.1]+final_rev.png",
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
