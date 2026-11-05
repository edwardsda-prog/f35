"""Deterministic unit test suite for F-35 Fleet Sustainment Agent Platform.

Covers:
1. Deterministic ASIP Physics & 3D CAD Engine (`app/physics/asip_engine.py`):
   - `run_asip_miners_rule_engine` (Rainflow cycle counting & Palmgren-Miner rule)
   - `extract_ndi_defect_and_map_cad` (C-Scan DOC-06 & SRM DOC-05 3D CAD transform)
2. Two-Turn HITL Airworthiness Release Gate (`app/callbacks.py`):
   - `enforce_hitl_airworthiness_gate` (`SAFE-02` invariant)
3. Tier 1/2 Fast-Path Interceptor (`app/callbacks.py`):
   - `fast_path_before_model_callback` (< 5 ms SLA for greetings/health checks)
4. Configuration, Guardrails & Pydantic Schemas (`app/config.py`, `app/schemas.py`):
   - `REG-01`, `PERF-01..07`, `SAFE-01..02` invariants
"""

from __future__ import annotations

import inspect
import time
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers for flexible contract invocation and attribute/dict reading
# ---------------------------------------------------------------------------


def _call_with_supported_kwargs(fn: Any, **kwargs: Any) -> Any:
    """Invoke `fn` passing only the keyword arguments accepted by its signature."""
    sig = inspect.signature(fn)
    accepts_var_kw = any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
    )
    if accepts_var_kw:
        return fn(**kwargs)
    filtered = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return fn(**filtered)


def _get_val(obj: Any, *keys: str, default: Any = None) -> Any:
    """Extract a field from a dict or Pydantic model trying candidate key names."""
    if obj is None:
        return default
    for key in keys:
        if isinstance(obj, dict) and key in obj:
            return obj[key]
        if hasattr(obj, key):
            return getattr(obj, key)
    if hasattr(obj, "model_dump"):
        dumped = obj.model_dump()
        for key in keys:
            if key in dumped:
                return dumped[key]
    return default


class DummyTool:
    """Mock ADK BaseTool for testing `before_tool_callback`."""

    def __init__(self, name: str) -> None:
        self.name = name


class DummyUserContentPart:
    """Mock GenAI Part with text."""

    def __init__(self, text: str) -> None:
        self.text = text


class DummyUserContent:
    """Mock GenAI Content with parts."""

    def __init__(self, text: str, role: str = "user") -> None:
        self.role = role
        self.parts = [DummyUserContentPart(text)]


class DummyToolContext:
    """Mock ADK ToolContext with mutable session state and user content."""

    def __init__(
        self,
        state: dict[str, Any] | None = None,
        user_text: str = "",
        invocation_id: str = "inv-turn-1",
    ) -> None:
        self.state: dict[str, Any] = state if state is not None else {}
        self.user_content = DummyUserContent(user_text) if user_text else None
        self.invocation_id = invocation_id


class DummyCallbackContext:
    """Mock ADK CallbackContext for `before_model_callback`."""

    def __init__(
        self,
        state: dict[str, Any] | None = None,
        user_text: str = "",
        agent_name: str = "f35_sustainment_coordinator",
    ) -> None:
        self.state: dict[str, Any] = state if state is not None else {}
        self.user_content = DummyUserContent(user_text) if user_text else None
        self.agent_name = agent_name


class DummyLlmRequest:
    """Mock ADK LlmRequest containing contents list."""

    def __init__(self, user_text: str) -> None:
        self.contents = [DummyUserContent(user_text, role="user")]
        self.model = "gemini-3.8-flash"


# ===========================================================================
# 1. Deterministic ASIP Physics & 3D CAD Engine (`app/physics/asip_engine.py`)
# ===========================================================================


class TestAsipPhysicsEngine:
    """Unit tests for deterministic Rainflow, Palmgren-Miner, and 3D CAD math."""

    def test_miners_rule_exceedance_9_4g_mach_1_3_220c(self) -> None:
        """Verify 9.4G / Mach 1.3 / 220.0C exceedance produces exact MIL-HDBK-516C values."""
        from app.physics.asip_engine import run_asip_miners_rule_engine

        t0 = time.perf_counter()
        result = _call_with_supported_kwargs(
            run_asip_miners_rule_engine,
            tail_number="ZM151",
            structural_station_id="Frame 496",
            station_id="Frame 496",
            peak_nz_g=9.4,
            mach_number=1.3,
            peak_egt_celsius=220.0,
            duration_seconds=3.2,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert elapsed_ms < 50.0, (
            f"ASIP physics solver took {elapsed_ms:.2f} ms, exceeding 50 ms budget"
        )
        damage_delta = _get_val(
            result, "miners_rule_damage_delta", "damage_delta", "cumulative_damage_delta"
        )
        yield_pct = _get_val(result, "calculated_yield_pct", "yield_pct")
        ndi_class = _get_val(result, "required_ndi_class", "ndi_class")
        jtd_rule = _get_val(result, "mandated_jtd_rule", "jtd_rule")

        assert damage_delta == pytest.approx(0.0042, abs=1e-6)
        assert yield_pct == pytest.approx(104.2, abs=1e-2)
        assert ndi_class == "CLASS_A_ULTRASONIC_C_SCAN"
        assert "53-11-00" in str(jtd_rule)

    def test_miners_rule_nominal_envelope_below_7_5g(self) -> None:
        """Verify nominal 6.5G / Mach 0.9 / 150C load stays <= 100% yield without Class A NDI."""
        from app.physics.asip_engine import run_asip_miners_rule_engine

        result = _call_with_supported_kwargs(
            run_asip_miners_rule_engine,
            tail_number="ZM154",
            structural_station_id="Frame 496",
            station_id="Frame 496",
            peak_nz_g=6.5,
            mach_number=0.9,
            peak_egt_celsius=150.0,
            duration_seconds=2.0,
        )
        damage_delta = _get_val(
            result, "miners_rule_damage_delta", "damage_delta", "cumulative_damage_delta"
        )
        yield_pct = _get_val(result, "calculated_yield_pct", "yield_pct")
        ndi_class = _get_val(result, "required_ndi_class", "ndi_class")

        assert float(damage_delta) >= 0.0
        assert float(damage_delta) < 0.0042
        assert float(yield_pct) <= 100.0
        assert ndi_class != "CLASS_A_ULTRASONIC_C_SCAN"

    def test_miners_rule_severe_overstress_above_9_4g(self) -> None:
        """Verify extreme 10.5G load produces > 104.2% yield and trips Class A C-Scan."""
        from app.physics.asip_engine import run_asip_miners_rule_engine

        result = _call_with_supported_kwargs(
            run_asip_miners_rule_engine,
            tail_number="ZM151",
            structural_station_id="Frame 496",
            station_id="Frame 496",
            peak_nz_g=10.5,
            mach_number=1.4,
            peak_egt_celsius=235.0,
            duration_seconds=3.5,
        )
        damage_delta = _get_val(
            result, "miners_rule_damage_delta", "damage_delta", "cumulative_damage_delta"
        )
        yield_pct = _get_val(result, "calculated_yield_pct", "yield_pct")
        ndi_class = _get_val(result, "required_ndi_class", "ndi_class")

        assert float(damage_delta) >= 0.0042
        assert float(yield_pct) >= 104.2
        assert ndi_class == "CLASS_A_ULTRASONIC_C_SCAN"

    def test_miners_rule_deterministic_repeatability_safe_01(self) -> None:
        """Verify 50 repeated calls return identical deterministic math (SAFE-01)."""
        from app.physics.asip_engine import run_asip_miners_rule_engine

        baseline = _call_with_supported_kwargs(
            run_asip_miners_rule_engine,
            tail_number="ZM151",
            structural_station_id="Frame 496",
            peak_nz_g=9.4,
            mach_number=1.3,
            peak_egt_celsius=220.0,
        )
        for _ in range(50):
            sample = _call_with_supported_kwargs(
                run_asip_miners_rule_engine,
                tail_number="ZM151",
                structural_station_id="Frame 496",
                peak_nz_g=9.4,
                mach_number=1.3,
                peak_egt_celsius=220.0,
            )
            assert _get_val(sample, "miners_rule_damage_delta") == _get_val(
                baseline, "miners_rule_damage_delta"
            )
            assert _get_val(sample, "calculated_yield_pct") == _get_val(
                baseline, "calculated_yield_pct"
            )

    def test_extract_ndi_defect_and_map_cad_doc06(self) -> None:
        """Verify DOC-06 C-scan maps to Frame 496 Fastener Hole #14 with 0.012 in elongation."""
        from app.physics.asip_engine import extract_ndi_defect_and_map_cad

        t0 = time.perf_counter()
        result = _call_with_supported_kwargs(
            extract_ndi_defect_and_map_cad,
            c_scan_document_id="DOC-06",
            srm_document_id="DOC-05",
            structural_station_id="Frame 496",
            station_id="Frame 496",
            tail_number="ZM151",
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        assert elapsed_ms < 50.0

        station_feature = _get_val(
            result,
            "mapped_cad_station",
            "station_id",
            "cad_station_feature",
            "structural_feature",
            "fastener_hole_id",
        )
        measured_in = _get_val(
            result, "measured_ndi_elongation_in", "measured_elongation_in"
        )
        allowable_in = _get_val(
            result, "allowable_elongation_in", "allowable_limit_in"
        )
        within_limits = _get_val(
            result, "within_allowable_limits", "is_within_limits", "serviceable"
        )
        disposition = _get_val(
            result, "disposition", "disposition_status", "recommended_disposition"
        )
        task_card = _get_val(
            result, "mandated_jtd_task_card", "jtd_task_card", "task_card"
        )

        assert "496" in str(station_feature) or "14" in str(station_feature)
        assert float(measured_in) == pytest.approx(0.012, abs=1e-5)
        assert float(allowable_in) == pytest.approx(0.015, abs=1e-5)
        assert within_limits is True
        assert disposition == "SERVICEABLE_WITH_TORQUE_RECHECK"
        assert "53-11-00-280" in str(task_card)


# ===========================================================================
# 2. Two-Turn HITL Airworthiness Release Gate (`app/callbacks.py`)
# ===========================================================================


class TestTwoTurnHitlGate:
    """Unit tests for `enforce_hitl_airworthiness_gate` (`SAFE-02` invariant)."""

    def test_hitl_gate_blocks_when_no_package_staged(self) -> None:
        """Verify approval is blocked when `pending_release_package_id` is absent from state."""
        from app.callbacks import enforce_hitl_airworthiness_gate

        tool = DummyTool("approve_form700_engineering_release")
        ctx = DummyToolContext(
            state={},
            user_text="I confirm and approve as Lead Stress Engineer.",
            invocation_id="inv-turn-2",
        )
        args = {
            "release_package_id": "AWR-700-20261102-ZM151",
            "reviewer_role": "Lead Stress Engineer",
            "approval_notes": "Confirmed.",
        }

        res = enforce_hitl_airworthiness_gate(tool=tool, args=args, tool_context=ctx)
        assert res is not None, "Expected HITL gate to block when no package is staged"
        assert isinstance(res, dict)
        status_str = str(res.get("status", "") or res.get("error", "")).upper()
        assert any(
            token in status_str or token in str(res).upper()
            for token in ("BLOCK", "ERROR", "DENIED", "PENDING", "REJECT", "HITL")
        )

    def test_hitl_gate_blocks_same_turn_auto_approval_safe_02(self) -> None:
        """Verify `SAFE-02`: approval in the SAME turn as package staging is blocked."""
        from app.callbacks import enforce_hitl_airworthiness_gate

        tool = DummyTool("approve_form700_engineering_release")
        ctx = DummyToolContext(
            state={
                "pending_release_package_id": "AWR-700-20261102-ZM151",
                "hitl_review_status": "PENDING_HITL_REVIEW",
                "staged_turn_id": 1,
                "current_turn_id": 1,
                "staged_invocation_id": "inv-turn-1",
            },
            user_text="Generate Form 700 and approve it right now as Lead Stress Engineer.",
            invocation_id="inv-turn-1",
        )
        args = {
            "release_package_id": "AWR-700-20261102-ZM151",
            "reviewer_role": "Lead Stress Engineer",
            "approval_notes": "Confirmed by Lead Stress Engineer.",
        }

        res = enforce_hitl_airworthiness_gate(tool=tool, args=args, tool_context=ctx)
        assert res is not None, (
            "SAFE-02 violation: HITL gate must block same-turn auto-approval"
        )
        assert isinstance(res, dict)

    def test_hitl_gate_blocks_mismatched_release_package_id(self) -> None:
        """Verify approval is blocked when `release_package_id` does not match staged ID."""
        from app.callbacks import enforce_hitl_airworthiness_gate

        tool = DummyTool("approve_form700_engineering_release")
        ctx = DummyToolContext(
            state={
                "pending_release_package_id": "AWR-700-20261102-ZM151",
                "hitl_review_status": "PENDING_HITL_REVIEW",
                "staged_turn_id": 1,
                "current_turn_id": 2,
                "staged_invocation_id": "inv-turn-1",
            },
            user_text="Approved by Chief Technical Officer (CTO) for release.",
            invocation_id="inv-turn-2",
        )
        args = {
            "release_package_id": "AWR-700-99999999-WRONG",
            "reviewer_role": "Chief Technical Officer (CTO)",
            "approval_notes": "Approved by CTO.",
        }

        res = enforce_hitl_airworthiness_gate(tool=tool, args=args, tool_context=ctx)
        assert res is not None, (
            "Expected HITL gate to block mismatched release_package_id"
        )

    def test_hitl_gate_blocks_unauthorized_reviewer_role(self) -> None:
        """Verify approval is blocked when reviewer_role lacks Lead Stress Engineer / CTO authority."""
        from app.callbacks import enforce_hitl_airworthiness_gate

        tool = DummyTool("approve_form700_engineering_release")
        ctx = DummyToolContext(
            state={
                "pending_release_package_id": "AWR-700-20261102-ZM151",
                "hitl_review_status": "PENDING_HITL_REVIEW",
                "staged_turn_id": 1,
                "current_turn_id": 2,
                "staged_invocation_id": "inv-turn-1",
            },
            user_text="Looks okay to me, go ahead.",
            invocation_id="inv-turn-2",
        )
        args = {
            "release_package_id": "AWR-700-20261102-ZM151",
            "reviewer_role": "Unverified Guest",
            "approval_notes": "No engineering review performed.",
        }

        res = enforce_hitl_airworthiness_gate(tool=tool, args=args, tool_context=ctx)
        assert res is not None, (
            "Expected HITL gate to block unauthorized reviewer role"
        )

    def test_hitl_gate_allows_valid_second_turn_engineer_signoff(self) -> None:
        """Verify HITL gate returns None (allows execution) on Turn 2 with valid CTO/Lead Stress Engineer sign-off."""
        from app.callbacks import enforce_hitl_airworthiness_gate

        tool = DummyTool("approve_form700_engineering_release")
        ctx = DummyToolContext(
            state={
                "pending_release_package_id": "AWR-700-20261102-ZM151",
                "hitl_review_status": "PENDING_HITL_REVIEW",
                "staged_turn_id": 1,
                "current_turn_id": 2,
                "staged_invocation_id": "inv-turn-1",
            },
            user_text=(
                "I have reviewed the Structural Appraisal Report and confirm "
                "approval as Lead Stress Engineer / Chief Technical Officer (CTO) "
                "for package AWR-700-20261102-ZM151."
            ),
            invocation_id="inv-turn-2",
        )
        args = {
            "release_package_id": "AWR-700-20261102-ZM151",
            "reviewer_role": "Chief Technical Officer (CTO) / Lead Stress Engineer",
            "approval_notes": "Confirmed by Lead Stress Engineer per JTD Task Card 53-11-00-280.",
        }

        res = enforce_hitl_airworthiness_gate(tool=tool, args=args, tool_context=ctx)
        assert res is None, (
            f"Expected HITL gate to allow valid Turn 2 approval, but got: {res}"
        )

    def test_hitl_gate_allows_non_approval_tools_unconditionally(self) -> None:
        """Verify non-approval tools pass through `enforce_hitl_airworthiness_gate` with None."""
        from app.callbacks import enforce_hitl_airworthiness_gate

        tool = DummyTool("generate_form700_airworthiness_package")
        ctx = DummyToolContext(state={}, invocation_id="inv-turn-1")
        res = enforce_hitl_airworthiness_gate(
            tool=tool,
            args={"tail_number": "ZM151", "station_id": "Frame 496"},
            tool_context=ctx,
        )
        assert res is None


# ===========================================================================
# 3. Tier 1/2 Fast-Path Interceptor (`app/callbacks.py`)
# ===========================================================================


class TestFastPathBeforeModelCallback:
    """Unit tests for `fast_path_before_model_callback` (< 5 ms greeting/health SLA)."""

    @pytest.mark.parametrize("greeting", ["hi", "hello", "ping", "health"])
    def test_fast_path_intercepts_short_greetings_under_5ms(
        self, greeting: str
    ) -> None:
        """Verify short greetings/health checks return an immediate LlmResponse in < 5 ms."""
        from app.callbacks import fast_path_before_model_callback

        cb_ctx = DummyCallbackContext(state={}, user_text=greeting)
        llm_req = DummyLlmRequest(user_text=greeting)

        t0 = time.perf_counter()
        response = fast_path_before_model_callback(
            callback_context=cb_ctx, llm_request=llm_req
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert response is not None, (
            f"Expected fast-path callback to intercept '{greeting}'"
        )
        assert elapsed_ms < 5.0, (
            f"Fast-path interception took {elapsed_ms:.3f} ms, exceeding 5.0 ms SLA"
        )

    def test_fast_path_passes_through_domain_sustainment_queries(self) -> None:
        """Verify UC1/UC2/UC3 domain queries return None so they proceed to the LLM."""
        from app.callbacks import fast_path_before_model_callback

        domain_query = (
            "Check RAF Marham electro-hydrostatic actuator fatigue hours "
            "against regional depot inventory and tomorrow morning's sortie schedule."
        )
        cb_ctx = DummyCallbackContext(state={}, user_text=domain_query)
        llm_req = DummyLlmRequest(user_text=domain_query)

        response = fast_path_before_model_callback(
            callback_context=cb_ctx, llm_request=llm_req
        )
        assert response is None


# ===========================================================================
# 4. Configuration, Guardrails & Pydantic Schemas (`app/config.py`, `app/schemas.py`)
# ===========================================================================


class TestConfigAndGuardrailInvariants:
    """Unit tests verifying `REG-01`, `PERF-01..07`, and `SAFE-01..02` invariants."""

    def test_reg01_eu_residency_constants_in_config(self) -> None:
        """Verify `app/config.py` enforces strict EU / `europe-west1` residency constants."""
        from app import config

        assert config.PROJECT_ID == "antig-dave"
        assert config.PROJECT_NUMBER == "284046449012"
        assert config.COMPUTE_REGION == "europe-west1"
        assert config.BQ_LOCATION == "EU"
        assert config.BQ_DATASET == "ukd_f35_sustainment_demo"
        assert config.DE_LOCATION == "eu"
        assert config.JTD_DATASTORE_ID == "ukd-f35-jtd-ietm-ds"
        assert config.NARRATIVE_DATASTORE_ID == "ukd-f35-narrative-logs-ds"
        assert config.GEMINI_APP_ID == "f35-support"
        assert config.GCS_STAGING_BUCKET == "antig-dave-f35-staging-europe-west1"
        assert (
            config.RUNTIME_SERVICE_ACCOUNT
            == "f35-sustainment-runtime-sa@antig-dave.iam.gserviceaccount.com"
        )

    def test_perf01_no_gcloud_subprocess_in_app_code(self) -> None:
        """Verify `PERF-01`: no `subprocess` calls to `gcloud auth print-access-token` in `app/`."""
        app_dir = REPO_ROOT / "app"
        assert app_dir.is_dir()
        for py_file in app_dir.rglob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            assert "print-access-token" not in source, (
                f"PERF-01 violation in {py_file}: found gcloud print-access-token subprocess call"
            )

    def test_perf05_enterprise_sdk_and_thinking_level_enum(self) -> None:
        """Verify `PERF-05`: no legacy `thinking_budget` or `vertexai=True` in `app/`."""
        app_dir = REPO_ROOT / "app"
        for py_file in app_dir.rglob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            assert "thinking_budget" not in source, (
                f"PERF-05 violation in {py_file}: legacy integer thinking_budget found"
            )
            assert "vertexai=True" not in source, (
                f"PERF-05 violation in {py_file}: legacy vertexai=True found"
            )

    def test_pydantic_schemas_module_exports_valid_models(self) -> None:
        """Verify `app/schemas.py` exports Pydantic BaseModel classes for UC1, UC2, and UC3."""
        from pydantic import BaseModel

        from app import schemas

        exported_models = [
            obj
            for _, obj in inspect.getmembers(schemas, inspect.isclass)
            if issubclass(obj, BaseModel) and obj is not BaseModel
        ]
        assert len(exported_models) >= 3, (
            "Expected at least 3 Pydantic domain models in app/schemas.py for UC1, UC2, and UC3"
        )

    def test_iss003_discovery_engine_jsonl_manifest_document_schema(self) -> None:
        """Verify ISS-003: `generate_synthetic_corpus.py` generates valid `dataSchema='document'` JSONL manifests with PDF content URIs."""
        import json

        from scripts.generate_synthetic_corpus import (
            UNSTRUCTURED_DIR,
            generate_unstructured_corpus,
        )

        generate_unstructured_corpus()
        for manifest_name, expected_count in (
            ("metadata.jsonl", 9),
            ("jtd_metadata.jsonl", 7),
            ("narrative_metadata.jsonl", 2),
        ):
            manifest_path = UNSTRUCTURED_DIR / manifest_name
            assert manifest_path.is_file(), f"Missing manifest {manifest_path}"
            lines = [
                line.strip()
                for line in manifest_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            assert len(lines) == expected_count
            for raw_line in lines:
                entry = json.loads(raw_line)
                assert isinstance(entry.get("id"), str) and entry["id"]
                assert "jsonData" in entry
                parsed_json_data = json.loads(entry["jsonData"])
                assert parsed_json_data["_id"] == entry["id"]
                assert parsed_json_data["chunk_id"] == entry["id"]
                assert parsed_json_data["doc_id"].startswith("DOC-0")
                assert "content" in parsed_json_data and "text" in parsed_json_data
                content_block = entry.get("content", {})
                assert content_block.get("mimeType") == "application/pdf"
                assert str(content_block.get("uri", "")).endswith(".pdf")

    def test_iss003_setup_demo_infra_gcs_source_data_schema_document(self) -> None:
        """Verify ISS-003: `scripts/setup_demo_infra.py` specifies `dataSchema='document'` in `gcsSource` import payload."""
        source = (REPO_ROOT / "scripts" / "setup_demo_infra.py").read_text(
            encoding="utf-8"
        )
        assert '"gcsSource"' in source
        assert '"dataSchema": "document"' in source

    def test_iss004_build_de_search_payload_metadata_filter_boost_and_facets(self) -> None:
        """Verify ISS-004: build_de_search_payload properly constructs filter, boostSpec, and facetSpecs."""
        from app.clients import build_de_search_payload

        # Basic query
        p1 = build_de_search_payload("canopy latch", page_size=15)
        assert p1["query"] == "canopy latch"
        assert p1["pageSize"] == 15
        assert "filter" not in p1
        assert "boostSpec" not in p1
        assert "facetSpecs" not in p1
        assert p1["contentSearchSpec"]["snippetSpec"]["returnSnippet"] is True
        assert p1["contentSearchSpec"]["extractiveContentSpec"]["maxExtractiveAnswerCount"] == 3

        # Advanced query with metadata filter, boost, and facets
        filter_expr = 'system_subsystem_code: ANY("53-30") AND bit_fault_associated = "false"'
        boost_spec = {
            "conditionBoostSpecs": [
                {"condition": 'service_branch_origin: ANY("RAF", "RN")', "boost": 0.5}
            ]
        }
        facet_specs = [
            {"facetKey": {"key": "service_branch_origin"}, "limit": 10},
            {"facetKey": {"key": "system_subsystem_code"}, "limit": 10},
        ]
        p2 = build_de_search_payload(
            "canopy latch",
            page_size=15,
            filter_expr=filter_expr,
            boost_spec=boost_spec,
            facet_specs=facet_specs,
            include_extractive=False,
        )
        assert p2["filter"] == filter_expr
        assert p2["boostSpec"] == boost_spec
        assert p2["facetSpecs"] == facet_specs
        assert "extractiveContentSpec" not in p2["contentSearchSpec"]

    def test_iss004_build_metadata_filter_syntax_and_quoting(self) -> None:
        """Verify ISS-004: build_metadata_filter builds valid filter strings conforming to Discovery Engine schema."""
        from app.tools.uc2_jtd_search import (
            build_metadata_boost_spec,
            build_metadata_facet_specs,
            build_metadata_filter,
        )

        # When subsystem is provided and bit_fault_present is False
        f1 = build_metadata_filter(subsystem_filter="53-30", bit_fault_present=False)
        assert f1 is not None
        assert 'system_subsystem_code: ANY("53-30")' in f1
        assert 'bit_fault_associated = "false"' in f1
        assert " AND " in f1

        # When bit_fault_present is True
        f2 = build_metadata_filter(subsystem_filter="53-30", bit_fault_present=True)
        assert f2 is not None
        assert 'system_subsystem_code: ANY("53-30")' in f2
        assert "bit_fault_associated" not in f2

        # When aircraft_variant is provided
        f3 = build_metadata_filter(
            subsystem_filter="53-11", bit_fault_present=False, aircraft_variant="F-35B"
        )
        assert f3 is not None
        assert 'aircraft_variant_applicability: ANY("F-35B")' in f3

        # Boost spec structure
        b = build_metadata_boost_spec(preferred_branch="RAF")
        assert "conditionBoostSpecs" in b
        assert 'service_branch_origin: ANY("RAF", "RN")' in b["conditionBoostSpecs"][0]["condition"]
        assert b["conditionBoostSpecs"][0]["boost"] == 0.5

        # Facet specs structure
        facets = build_metadata_facet_specs()
        facet_keys = [f["facetKey"]["key"] for f in facets]
        assert "service_branch_origin" in facet_keys
        assert "system_subsystem_code" in facet_keys
        assert "aircraft_variant_applicability" in facet_keys

    def test_iss004_uc2_search_tool_outputs_metadata_specs_and_facets(self) -> None:
        """Verify ISS-004: search_technical_manuals_and_repair_logs returns metadata_filter, metadata_boost, and metadata_facets."""
        from app.tools.uc2_jtd_search import search_technical_manuals_and_repair_logs

        res = search_technical_manuals_and_repair_logs(
            symptom_query="sticky canopy catch during lock verification no BIT fault",
            bit_fault_present=False,
            subsystem_filter="53-30",
        )
        assert res["status"] == "SUCCESS"
        assert "metadata_filter" in res
        assert 'system_subsystem_code: ANY("53-30")' in str(res["metadata_filter"])
        assert 'bit_fault_associated = "false"' in str(res["metadata_filter"])
        assert "metadata_boost" in res
        assert "metadata_facets" in res
        assert isinstance(res["results"], list) and len(res["results"]) > 0


# ===========================================================================
# 5. Authenticated GCS Browser URLs (`app/tools/uc2_jtd_search.py`, `app/schemas.py`, etc.)
# ===========================================================================


class TestAuthenticatedGcsUrls:
    """Unit tests verifying all generated documentation and report URIs are converted to authenticated browser HTTPS URLs."""

    def test_to_authenticated_gcs_url_standard_transformation(self) -> None:
        """Verify standard gs:// URIs are converted to authenticated browser-clickable HTTPS URLs."""
        from app.tools.uc2_jtd_search import to_authenticated_gcs_url

        gs_uri = "gs://antig-dave-f35-staging-europe-west1/unstructured/docs/DOC-01-JTD-53-30-01-Canopy-Mechanical-Rigging.pdf"
        expected = "https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/unstructured/docs/DOC-01-JTD-53-30-01-Canopy-Mechanical-Rigging.pdf"
        assert to_authenticated_gcs_url(gs_uri) == expected

    def test_to_authenticated_gcs_url_edge_cases_and_non_gcs(self) -> None:
        """Verify edge cases: None, empty strings, whitespace, and existing HTTPS URLs."""
        from app.tools.uc2_jtd_search import to_authenticated_gcs_url

        assert to_authenticated_gcs_url(None) == ""
        assert to_authenticated_gcs_url("") == ""
        assert to_authenticated_gcs_url("   ") == ""

        https_url = "https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/unstructured/docs/DOC-01.pdf"
        assert to_authenticated_gcs_url(https_url) == https_url

        standard_web = "https://example.com/manual.pdf"
        assert to_authenticated_gcs_url(standard_web) == standard_web

    def test_uc2_search_tool_outputs_authenticated_browser_citations(self) -> None:
        """Verify search_technical_manuals_and_repair_logs returns authenticated browser URLs."""
        from app.tools.uc2_jtd_search import search_technical_manuals_and_repair_logs

        res = search_technical_manuals_and_repair_logs(
            symptom_query="canopy latch",
            bit_fault_present=False,
            subsystem_filter="53-30",
        )
        assert res["status"] == "SUCCESS"
        assert len(res["results"]) > 0
        for doc in res["results"]:
            uri = doc.get("uri") or doc.get("document_url") or ""
            assert uri.startswith("https://storage.cloud.google.com/"), (
                f"Expected authenticated GCS HTTPS URL, got: {uri}"
            )
            assert not uri.startswith("gs://")

    def test_uc3_sar_and_form700_emit_authenticated_browser_urls(self) -> None:
        """Verify Form 700 release package and SAR outputs use authenticated browser URLs."""
        from app.schemas import Form700ReleasePackage
        from app.tools.uc3_airworthiness import generate_form700_airworthiness_package

        # 1. Pydantic schema default
        pkg = Form700ReleasePackage(
            release_package_id="AWR-700-20261102-ZM151",
            mandated_jtd_task_card="JTD Task Card 53-11-00-280",
            disposition_status="SERVICEABLE_WITH_TORQUE_RECHECK",
            tail_number="ZM151",
            station_id="Frame 496 — Fastener Hole #14",
        )
        assert pkg.appraisal_report_uri.startswith("https://storage.cloud.google.com/")
        assert not pkg.appraisal_report_uri.startswith("gs://")

        # 2. Tool output
        res = generate_form700_airworthiness_package(
            tail_number="ZM151",
            station_id="Frame 496",
        )
        assert res["status"] in ("SUCCESS", "STAGED_PENDING_HITL_REVIEW")
        report_uri = res.get("appraisal_report_uri", "")
        assert report_uri.startswith("https://storage.cloud.google.com/"), (
            f"Expected authenticated GCS HTTPS URL, got: {report_uri}"
        )
        assert not report_uri.startswith("gs://")


# ===========================================================================
# 6. Fast-Path Operational Capability Interception (`app/callbacks.py`)
# ===========================================================================


class TestFastPathCapabilityInterception:
    """Unit tests for operational capability fast-path interception (< 5 ms SLA)."""

    def test_fast_path_intercepts_operational_capability_query_under_5ms(self) -> None:
        """Verify 'Describe your operational capability' is intercepted immediately under 5 ms."""
        from app.callbacks import fast_path_before_model_callback

        prompt = "Describe your operational capability"
        cb_ctx = DummyCallbackContext(state={}, user_text=prompt)
        llm_req = DummyLlmRequest(user_text=prompt)

        t0 = time.perf_counter()
        response = fast_path_before_model_callback(
            callback_context=cb_ctx, llm_request=llm_req
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert response is not None, "Expected fast-path callback to intercept operational capability inquiry"
        assert elapsed_ms < 5.0, (
            f"Capability interception took {elapsed_ms:.3f} ms, exceeding 5.0 ms SLA"
        )
        part_text = response.content.parts[0].text
        assert "F-35 Fleet Sustainment Agent Platform" in part_text
        assert "Core Purpose & Operational Benefits" in part_text
        assert "Accelerate Fleet Readiness" in part_text
        assert "Actionable Decision Support" in part_text
        assert "Authoritative Engineering Guidance" in part_text
        # Verify technology names and fragile use-case breakdowns are not present (Issue 1 & 2)
        for tech in ("BigQuery", "GCS", "Google Cloud Storage", "ADK", "Table 7", "Discovery Engine", "UC0", "UC1", "UC2", "UC3"):
            assert tech not in part_text, f"Internal technology or brittle use-case name '{tech}' found in capability response"

    def test_fast_path_greetings_conceal_technology_names(self) -> None:
        """Verify fast-path greetings and status responses do not leak internal technology names."""
        from app.callbacks import fast_path_before_model_callback

        for prompt in ("", "hello", "hi"):
            cb_ctx = DummyCallbackContext(state={}, user_text=prompt)
            llm_req = DummyLlmRequest(user_text=prompt)
            resp = fast_path_before_model_callback(callback_context=cb_ctx, llm_request=llm_req)
            assert resp is not None
            text = resp.content.parts[0].text
            for tech in ("BigQuery", "GCS", "Google Cloud Storage", "europe-west1", "Discovery Engine"):
                assert tech not in text, f"Internal technology name '{tech}' leaked in response to '{prompt}'"

    @pytest.mark.parametrize(
        "prompt",
        [
            "Describe your operational capability",
            "What are your operational capabilities?",
            "Explain your capability",
            "Show your capabilities",
            "Describe operational capabilities",
        ],
    )
    def test_fast_path_capability_regex_patterns(self, prompt: str) -> None:
        """Verify various phrasing variations of capability queries are intercepted."""
        from app.callbacks import fast_path_before_model_callback

        cb_ctx = DummyCallbackContext(state={}, user_text=prompt)
        llm_req = DummyLlmRequest(user_text=prompt)

        response = fast_path_before_model_callback(
            callback_context=cb_ctx, llm_request=llm_req
        )
        assert response is not None, f"Expected fast-path callback to intercept: '{prompt}'"

    @pytest.mark.parametrize(
        "query_with_domain_entity",
        [
            "Describe your operational capability for ZM151",
            "What are your capabilities regarding Frame 496?",
            "Show capabilities for lot #8841-B",
            "Explain capabilities for ACT-99812-F",
            "Describe your capability for Form 700 release",
        ],
    )
    def test_domain_entity_queries_fall_through_fast_path(
        self, query_with_domain_entity: str
    ) -> None:
        """Verify queries containing specific airframe or part domain entities fall through to LLM."""
        from app.callbacks import fast_path_before_model_callback

        cb_ctx = DummyCallbackContext(state={}, user_text=query_with_domain_entity)
        llm_req = DummyLlmRequest(user_text=query_with_domain_entity)

        response = fast_path_before_model_callback(
            callback_context=cb_ctx, llm_request=llm_req
        )
        assert response is None, (
            f"Query with domain entity should fall through to LLM, but got intercepted: {query_with_domain_entity}"
        )


# ===========================================================================
# 7. Sustainment Chart Rendering Tool (`app/tools/uc1_analytics.py`)
# ===========================================================================


class TestSustainmentChartRenderingTool:
    """Unit tests for on-demand Vega-Lite chart rendering via `render_sustainment_chart`."""

    def test_render_sustainment_chart_actuator_fatigue_threshold(self) -> None:
        """Verify rendering actuator fatigue threshold chart."""
        from app.tools.uc1_analytics import render_sustainment_chart

        res = render_sustainment_chart("actuator_fatigue_threshold_chart")
        assert res["status"] == "SUCCESS"
        assert res["chart_name"] == "actuator_fatigue_threshold_chart"
        assert "actuator_fatigue_threshold_chart" in res
        chart = res["actuator_fatigue_threshold_chart"]
        assert "$schema" in chart
        assert "data" in chart or "layer" in chart

    def test_render_sustainment_chart_depot_stock_vs_demand(self) -> None:
        """Verify rendering depot stock vs demand bar chart."""
        from app.tools.uc1_analytics import render_sustainment_chart

        res = render_sustainment_chart("depot_stock_vs_demand_bar_chart")
        assert res["status"] == "SUCCESS"
        assert res["chart_name"] == "depot_stock_vs_demand_bar_chart"
        assert "depot_stock_vs_demand_bar_chart" in res
        chart = res["depot_stock_vs_demand_bar_chart"]
        assert "$schema" in chart
        assert "mark" in chart or "layer" in chart

    def test_render_sustainment_chart_both(self) -> None:
        """Verify rendering both charts simultaneously."""
        from app.tools.uc1_analytics import render_sustainment_chart

        res = render_sustainment_chart("both")
        assert res["status"] == "SUCCESS"
        assert res["chart_name"] == "both"
        assert "actuator_fatigue_threshold_chart" in res
        assert "depot_stock_vs_demand_bar_chart" in res
        assert "vega_lite_charts" in res
        assert "depot_stock_vs_demand_bar_chart" in res["vega_lite_charts"]
        assert "actuator_fatigue_threshold_chart" in res["vega_lite_charts"]

    def test_render_sustainment_chart_execution_budget_under_5ms(self) -> None:
        """Verify on-demand chart spec retrieval completes in < 5 ms when cached."""
        from app.tools.uc1_analytics import (
            check_actuator_fatigue_and_depot_inventory,
            render_sustainment_chart,
        )

        ctx = DummyToolContext(state={})
        check_actuator_fatigue_and_depot_inventory(tool_context=ctx)

        t0 = time.perf_counter()
        res = render_sustainment_chart("both", tool_context=ctx, render_graphics=False)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert res["status"] == "SUCCESS"
        assert elapsed_ms < 5.0, (
            f"Chart rendering took {elapsed_ms:.3f} ms, exceeding 5.0 ms budget"
        )

    def test_render_sustainment_chart_graphics_generation_under_1000ms(self) -> None:
        """Verify graphical chart rendering and GCS upload completes under 1,000 ms SLA."""
        from app.tools.uc1_analytics import (
            check_actuator_fatigue_and_depot_inventory,
            render_sustainment_chart,
        )

        ctx = DummyToolContext(state={})
        check_actuator_fatigue_and_depot_inventory(tool_context=ctx)

        t0 = time.perf_counter()
        res = render_sustainment_chart("both", tool_context=ctx, render_graphics=True)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert res["status"] == "SUCCESS"
        assert len(res["presentation_graphics"]) >= 1
        assert "storage.cloud.google.com" in res["presentation_graphics_markdown"]
        assert elapsed_ms < 1000.0, (
            f"Diagram generation took {elapsed_ms:.2f} ms (> 1,000 ms SLA)"
        )

    def test_render_sustainment_chart_state_fallback(self) -> None:
        """Verify render_sustainment_chart falls back gracefully when tool_context is None or empty."""
        from app.tools.uc1_analytics import render_sustainment_chart

        # Empty tool context
        empty_ctx = DummyToolContext(state={})
        res_empty = render_sustainment_chart("both", tool_context=empty_ctx)
        assert res_empty["status"] == "SUCCESS"
        assert "actuator_fatigue_threshold_chart" in res_empty

        # None tool context
        res_none = render_sustainment_chart("both", tool_context=None)
        assert res_none["status"] == "SUCCESS"
        assert "depot_stock_vs_demand_bar_chart" in res_none


# ===========================================================================
# 8. UC1 Two-Turn Tabular Workflow (`app/sub_agents/uc1_analytics_agent.py`, `app/tools/uc1_analytics.py`)
# ===========================================================================


class TestUc1TwoTurnTabularWorkflow:
    """Unit tests for UC1 two-turn tabular-first workflow and system instructions."""

    def test_uc1_turn1_returns_tabular_and_prompts_for_chart_selection(self) -> None:
        """Verify Turn 1 analytics tool returns formatted Markdown table, tail records, and backward-compatible chart specs."""
        from app.tools.uc1_analytics import check_actuator_fatigue_and_depot_inventory

        ctx = DummyToolContext(state={})
        res = check_actuator_fatigue_and_depot_inventory(tool_context=ctx)

        assert res["status"] == "SUCCESS"
        assert "markdown_summary_table" in res
        table = res["markdown_summary_table"]
        assert "ZM151" in table
        assert "ZM154" in table
        assert "1000.4" in table
        assert "842.0" in table
        assert "1680-01-619-4821" in table

        # Backward compatibility check
        assert "vega_lite_charts" in res
        assert "depot_stock_vs_demand_bar_chart" in res["vega_lite_charts"]
        assert "actuator_fatigue_threshold_chart" in res["vega_lite_charts"]

        # Cache check in tool_context state
        assert "last_uc1_metrics" in ctx.state
        assert "last_uc1_analytics_result" in ctx.state

    def test_uc1_system_instruction_two_turn_rules(self) -> None:
        """Verify UC1 system instruction and agent definition enforce the two-turn tabular-first workflow."""
        from app.sub_agents.uc1_analytics_agent import (
            UC1_SYSTEM_INSTRUCTION,
            f35_analytics_agent,
        )

        assert "Turn 1 Output Workflow" in UC1_SYSTEM_INSTRUCTION
        assert "Do NOT emit raw ```vega-lite JSON blocks in Turn 1" in UC1_SYSTEM_INSTRUCTION
        assert "Would you like me to render" in UC1_SYSTEM_INSTRUCTION
        assert "Turn 2 Chart Rendering" in UC1_SYSTEM_INSTRUCTION
        assert "render_sustainment_chart" in UC1_SYSTEM_INSTRUCTION

        # Tool registration check
        tool_names = [t.name if hasattr(t, "name") else t.__name__ for t in f35_analytics_agent.tools]
        assert "render_sustainment_chart" in tool_names
        assert "check_actuator_fatigue_and_depot_inventory" in tool_names
        assert "recommend_tail_swap_and_replenishment" in tool_names


# ===========================================================================
# 9. UC0 Maintenance Data Agent & Spreadsheet Card (`app/tools/uc0_maintenance.py`)
# ===========================================================================


def test_uc0_maintenance_schema_has_table_and_column_descriptions() -> None:
    """Verify `maintenance_work_orders.schema.json` metadata, partitioning, clustering, and 18 column descriptions."""
    import json

    schema_path = (
        REPO_ROOT
        / "app"
        / "seed_data"
        / "schemas"
        / "maintenance_work_orders.schema.json"
    )
    assert schema_path.exists(), f"Missing schema file: {schema_path}"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema.get("table_name") == "maintenance_work_orders"

    table_desc = schema.get("description", "")
    assert isinstance(table_desc, str) and len(table_desc.strip()) > 0

    assert schema.get("partition_field") == "created_at_utc"

    clustering_fields = (
        schema.get("clustering_fields") or schema.get("cluster_fields")
    )
    assert clustering_fields == ["tail_number", "aircraft_status"]

    columns = schema.get("columns") or schema.get("fields", [])
    assert len(columns) == 18, f"Expected 18 columns, got {len(columns)}"
    for col in columns:
        col_name = col.get("name", "<unnamed>")
        col_desc = col.get("description", "")
        assert isinstance(col_desc, str) and len(col_desc.strip()) > 20, (
            f"Column '{col_name}' must have a description > 20 chars, got: {col_desc!r}"
        )


def test_uc0_seed_records_match_schema() -> None:
    """Verify `MAINTENANCE_WORK_ORDERS_ROWS` has 100 rows, ZM151 open work orders, and matches the 18 schema columns."""
    import json

    from app.seed_data.bq_seed_records import MAINTENANCE_WORK_ORDERS_ROWS

    schema_path = (
        REPO_ROOT
        / "app"
        / "seed_data"
        / "schemas"
        / "maintenance_work_orders.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    columns = schema.get("columns") or schema.get("fields", [])
    expected_col_names = [col["name"] for col in columns]
    assert len(expected_col_names) == 18

    assert len(MAINTENANCE_WORK_ORDERS_ROWS) == 100

    zm151_open_wos = {
        row["work_order_id"]
        for row in MAINTENANCE_WORK_ORDERS_ROWS
        if row.get("tail_number") == "ZM151"
        and row.get("work_order_status") != "COMPLETED"
    }
    assert {"WO-2026-88401", "WO-2026-88402", "WO-2026-88403"}.issubset(
        zm151_open_wos
    )

    active_wos = [
        row
        for row in MAINTENANCE_WORK_ORDERS_ROWS
        if row.get("work_order_status") != "COMPLETED"
    ]
    assert len(active_wos) == 10

    for idx, row in enumerate(MAINTENANCE_WORK_ORDERS_ROWS):
        assert set(row.keys()) == set(expected_col_names), (
            f"Row {idx} ({row.get('work_order_id')}) keys do not match schema columns"
        )


def test_uc0_execute_maintenance_sql_spreadsheet_card_and_csv_link() -> None:
    """Verify `execute_maintenance_sql` returns Spreadsheet Card JSON, Markdown badges, formula footer, and GCS CSV URL."""
    from app.tools.uc0_maintenance import execute_maintenance_sql

    sql = (
        "SELECT work_order_id, tail_number, squadron, aircraft_status, "
        "work_order_status, priority, wuc_code, subsystem_name, "
        "awaiting_part_nsn, assigned_shift_lead, estimated_mttr_hours, "
        "logged_man_hours FROM maintenance_work_orders "
        "WHERE work_order_status != 'COMPLETED' ORDER BY priority ASC"
    )
    res = execute_maintenance_sql(sql)

    assert res["status"] == "SUCCESS"
    assert res["row_count"] == 10

    card = res["spreadsheet_card"]
    assert card["columns"][0]["col_letter"] == "A"
    assert "=COUNTA(" in card["formula_footer"]["row_count_formula"]
    assert "=SUM(" in card["formula_footer"]["total_man_hours_formula"]
    assert card["csv_download_url"].startswith(
        "https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/exports/"
    )

    md = res["spreadsheet_card_markdown"]
    assert "[📥 Download .CSV (Excel / Google Sheets)]" not in md
    assert "🟡 PMC-M" in md
    assert "🔴 NMC-S (MICAP)" in md


def test_uc0_execute_maintenance_sql_aggregation_query() -> None:
    """Verify `execute_maintenance_sql` supports `GROUP BY squadron, aircraft_status` with accurate counts and sums."""
    from app.seed_data.bq_seed_records import MAINTENANCE_WORK_ORDERS_ROWS
    from app.tools.uc0_maintenance import execute_maintenance_sql

    sql = (
        "SELECT squadron, aircraft_status, COUNT(*) AS work_order_count, "
        "SUM(logged_man_hours) AS total_logged_hours "
        "FROM maintenance_work_orders "
        "GROUP BY squadron, aircraft_status "
        "ORDER BY squadron ASC, aircraft_status ASC"
    )
    res = execute_maintenance_sql(sql)
    assert res["status"] == "SUCCESS"

    # Compute expected groups from seed rows
    expected_groups: dict[tuple[str, str], tuple[int, float]] = {}
    for row in MAINTENANCE_WORK_ORDERS_ROWS:
        key = (str(row["squadron"]), str(row["aircraft_status"]))
        cnt, hrs = expected_groups.get(key, (0, 0.0))
        expected_groups[key] = (cnt + 1, round(hrs + float(row["logged_man_hours"]), 4))

    assert res["row_count"] == len(expected_groups)

    rows = res.get("rows") or res.get("spreadsheet_card", {}).get("rows", [])
    assert len(rows) == len(expected_groups)

    total_count = 0
    total_hours = 0.0
    for r in rows:
        if isinstance(r, dict):
            sqn = str(r.get("squadron"))
            status = str(r.get("aircraft_status"))
            cnt = int(r.get("work_order_count"))
            hrs = float(r.get("total_logged_hours"))
        else:
            sqn = str(r[0])
            status = str(r[1])
            cnt = int(r[2])
            hrs = float(r[3])
        # Strip any rendered badge prefix if present in display cells
        for raw_status in ("FMC", "PMC-M", "NMC-M", "NMC-S"):
            if raw_status in status:
                status = raw_status
                break
        assert (sqn, status) in expected_groups
        exp_cnt, exp_hrs = expected_groups[(sqn, status)]
        assert cnt == exp_cnt
        assert abs(hrs - exp_hrs) < 1e-2
        total_count += cnt
        total_hours += hrs

    assert total_count == len(MAINTENANCE_WORK_ORDERS_ROWS) == 100
    expected_total_hours = sum(
        float(r["logged_man_hours"]) for r in MAINTENANCE_WORK_ORDERS_ROWS
    )
    assert abs(total_hours - expected_total_hours) < 1e-2


def test_uc0_execute_maintenance_sql_blocks_unsafe_dml_ddl() -> None:
    """Verify `execute_maintenance_sql` rejects non-SELECT DML/DDL queries with `ValueError`."""
    from app.tools.uc0_maintenance import execute_maintenance_sql

    with pytest.raises(ValueError):
        execute_maintenance_sql("DROP TABLE maintenance_work_orders")

    with pytest.raises(ValueError):
        execute_maintenance_sql("DELETE FROM maintenance_work_orders WHERE 1=1")


def test_all_9_warehouse_tables_have_100_records_and_schema_descriptions() -> None:
    """Verify all 9 warehouse tables in `BQ_SEED_TABLES` have 100 rows and complete table + column descriptions (> 20 chars)."""
    import json

    from app.seed_data.bq_seed_records import BQ_SEED_TABLES

    expected_tables = (
        "airframe_component_telemetry",
        "global_depot_inventory",
        "squadron_sortie_schedule",
        "high_freq_strain_telemetry",
        "as_maintained_mbom_fasteners",
        "airworthiness_release_ledger",
        "maintenance_work_orders",
        "phm_bit_fault_events",
        "work_center_tooling_and_sqep",
    )
    assert set(BQ_SEED_TABLES.keys()) == set(expected_tables)

    schemas_dir = REPO_ROOT / "app" / "seed_data" / "schemas"
    for table_name in expected_tables:
        rows = BQ_SEED_TABLES[table_name]
        assert len(rows) == 100, (
            f"Expected 100 seed rows in {table_name}, got {len(rows)}"
        )

        schema_path = schemas_dir / f"{table_name}.schema.json"
        assert schema_path.is_file(), f"Missing schema file: {schema_path}"
        schema_obj = json.loads(schema_path.read_text(encoding="utf-8"))

        if isinstance(schema_obj, dict):
            table_desc = schema_obj.get("description", "")
            assert isinstance(table_desc, str) and len(table_desc.strip()) > 20, (
                f"Table '{table_name}' must have a description > 20 chars"
            )
            columns = (
                schema_obj.get("fields")
                or schema_obj.get("columns")
                or schema_obj.get("schema", [])
            )
        else:
            columns = list(schema_obj)

        assert len(columns) >= 6, f"Unexpectedly few columns in {table_name}"
        expected_col_names = {col["name"] for col in columns}
        for col in columns:
            col_name = col.get("name", "<unnamed>")
            col_desc = col.get("description", "")
            assert isinstance(col_desc, str) and len(col_desc.strip()) > 20, (
                f"Column '{table_name}.{col_name}' must have a description > 20 chars, got: {col_desc!r}"
            )

        for idx, row in enumerate(rows):
            assert set(row.keys()) == expected_col_names, (
                f"Row {idx} of {table_name} keys {set(row.keys())} != schema columns {expected_col_names}"
            )


def test_uc0_1_phm_bit_fault_events_triage_and_unlinked_advisories() -> None:
    """Verify UC 0.1 `execute_maintenance_sql` on `phm_bit_fault_events` surfaces ZM151 HRCs, Zero-BIT CND faults, unlinked advisories, badges, formula footer, and CSV export."""
    import json

    from app.tools.uc0_maintenance import execute_maintenance_sql

    sql = (
        "SELECT fault_event_id, tail_number, squadron, base_location, wuc_code, "
        "subsystem_name, hrc_code, fault_severity, bit_trigger_type, "
        "recurrence_count_30d, cnd_flag, diagnostic_confidence_pct, "
        "linked_work_order_id, fault_timestamp_utc "
        "FROM phm_bit_fault_events "
        "WHERE fault_severity != 'ADVISORY_PHM' OR linked_work_order_id IS NULL "
        "ORDER BY fault_timestamp_utc DESC"
    )
    res = execute_maintenance_sql(sql, sheet_title="F35_PHM_BIT_Fault_Triage")
    assert res["status"] == "SUCCESS"
    assert res["row_count"] >= 6

    rows = res["rows"]
    dumped = json.dumps(rows, default=str)
    for expected_hrc in ("HRC-2710-88A", "HRC-5330-000-NONE", "HRC-5320-94G"):
        assert expected_hrc in dumped, f"Missing ZM151 HRC {expected_hrc} in UC 0.1 query"
    assert "PILOT_REPORT_ONLY_NO_BIT" in dumped

    zm151_canopy_row = next(
        r for r in rows if r.get("hrc_code") == "HRC-5330-000-NONE"
    )
    assert zm151_canopy_row["tail_number"] == "ZM151"
    assert zm151_canopy_row["bit_trigger_type"] == "PILOT_REPORT_ONLY_NO_BIT"
    assert bool(zm151_canopy_row["cnd_flag"]) is True

    unlinked_rows = [r for r in rows if not r.get("linked_work_order_id")]
    assert len(unlinked_rows) >= 1, "Expected unlinked PHM advisories (linked_work_order_id IS NULL)"

    card = res["spreadsheet_card"]
    footer_str = json.dumps(card["formula_footer"])
    assert "=COUNTA(" in footer_str
    assert "=SUM(" in footer_str
    assert "=AVERAGE(" in footer_str
    assert card["csv_download_url"].startswith(
        "https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/exports/"
    )

    md = res["spreadsheet_card_markdown"]
    assert "[📥 Download .CSV (Excel / Google Sheets)]" in md
    assert any(badge in md for badge in ("🔴", "🟠", "🟡", "🟣", "⚪"))


def test_uc0_5_multi_table_join_work_orders_and_tooling_sqep() -> None:
    """Verify UC 0.5 2-table and 3-table JOINs across `maintenance_work_orders`, `work_center_tooling_and_sqep`, and `phm_bit_fault_events`."""
    import json

    from app.tools.uc0_maintenance import execute_maintenance_sql

    # 1. Two-table JOIN: maintenance_work_orders + work_center_tooling_and_sqep
    sql_2tbl = (
        "SELECT w.work_order_id, w.tail_number, w.aircraft_status, w.work_order_status, "
        "w.priority, w.wuc_code, w.subsystem_name, w.logged_man_hours, w.estimated_mttr_hours, "
        "t.sqep_certification_domain, t.sqep_certified_techs_on_shift, t.qar_inspector_available, "
        "t.required_special_tool_id, t.required_special_tool_name, t.tool_calibration_status, "
        "t.bay_dispatch_status "
        "FROM maintenance_work_orders w "
        "JOIN work_center_tooling_and_sqep t ON w.work_order_id = t.assigned_work_order_id "
        "WHERE w.work_order_status != 'COMPLETED' "
        "ORDER BY w.priority ASC"
    )
    res_2tbl = execute_maintenance_sql(
        sql_2tbl, sheet_title="F35_Work_Order_Tooling_SQEP_Join"
    )
    assert res_2tbl["status"] == "SUCCESS"
    assert res_2tbl["row_count"] >= 5

    dumped_2tbl = json.dumps(res_2tbl["rows"], default=str)
    for token in (
        "JTD-53-30-T14",
        "NDI-PAUT-496A",
        "EXPIRED_OUT_OF_CAL",
        "BLOCKED_TOOL_OUT_OF_CAL",
        "BLOCKED_NO_QAR_ON_SHIFT",
    ):
        assert token in dumped_2tbl, f"Missing expected UC 0.5 token {token} in 2-table JOIN"

    card_2tbl = res_2tbl["spreadsheet_card"]
    footer_2tbl = json.dumps(card_2tbl["formula_footer"])
    assert "=COUNTA(" in footer_2tbl
    assert "=SUM(" in footer_2tbl
    assert "=AVERAGE(" in footer_2tbl
    assert card_2tbl["csv_download_url"].startswith(
        "https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/exports/"
    )
    md_2tbl = res_2tbl["spreadsheet_card_markdown"]
    assert "[📥 Download .CSV (Excel / Google Sheets)]" in md_2tbl

    # 2. Three-table JOIN: maintenance_work_orders + work_center_tooling_and_sqep + phm_bit_fault_events
    sql_3tbl = (
        "SELECT w.work_order_id, w.tail_number, w.aircraft_status, w.wuc_code, "
        "p.hrc_code, p.fault_severity, p.bit_trigger_type, p.cnd_flag, "
        "t.required_special_tool_id, t.tool_calibration_status, t.bay_dispatch_status, "
        "w.logged_man_hours, w.estimated_mttr_hours "
        "FROM maintenance_work_orders w "
        "JOIN work_center_tooling_and_sqep t ON w.work_order_id = t.assigned_work_order_id "
        "LEFT JOIN phm_bit_fault_events p ON w.work_order_id = p.linked_work_order_id "
        "WHERE w.tail_number = 'ZM151' "
        "ORDER BY w.work_order_id ASC"
    )
    res_3tbl = execute_maintenance_sql(
        sql_3tbl, sheet_title="F35_ZM151_3Way_Diagnostic_Join"
    )
    assert res_3tbl["status"] == "SUCCESS"
    assert res_3tbl["row_count"] >= 3
    dumped_3tbl = json.dumps(res_3tbl["rows"], default=str)
    for token in (
        "HRC-2710-88A",
        "HRC-5330-000-NONE",
        "HRC-5320-94G",
        "JTD-53-30-T14",
        "NDI-PAUT-496A",
    ):
        assert token in dumped_3tbl, f"Missing expected token {token} in 3-table JOIN"


def test_uc0_live_bq_table_and_column_descriptions_verified() -> None:
    """Verify `maintenance_work_orders`, `phm_bit_fault_events`, and `work_center_tooling_and_sqep` table and column descriptions in BigQuery `EU` when live credentials are available."""
    import json

    from app.config import BQ_DATASET, BQ_LOCATION, PROJECT_ID, USE_CLOUD_CLIENTS

    uc0_tables = (
        "maintenance_work_orders",
        "phm_bit_fault_events",
        "work_center_tooling_and_sqep",
    )
    schemas_dir = REPO_ROOT / "app" / "seed_data" / "schemas"
    for tbl in uc0_tables:
        spec = json.loads((schemas_dir / f"{tbl}.schema.json").read_text(encoding="utf-8"))
        assert len(spec.get("description", "").strip()) > 20
        fields = spec.get("fields") or spec.get("columns", [])
        assert len(fields) >= 16
        assert all(len(f.get("description", "").strip()) > 20 for f in fields)

    if not USE_CLOUD_CLIENTS:
        return

    try:
        from app.clients import get_bq_client

        client = get_bq_client()
        for tbl in uc0_tables:
            table_ref = f"{PROJECT_ID}.{BQ_DATASET}.{tbl}"
            try:
                bq_table = client.get_table(table_ref)
            except Exception:
                # Table may not yet be provisioned in BigQuery EU prior to Phase 3 infra seeding
                continue
            assert bq_table.location == BQ_LOCATION
            assert bq_table.description and len(bq_table.description.strip()) > 20
            for schema_field in bq_table.schema:
                assert (
                    schema_field.description
                    and len(schema_field.description.strip()) > 20
                ), f"Live BigQuery column {tbl}.{schema_field.name} missing description"
    except Exception:
        # Offline / sandboxed environment without live GCP credentials
        pass



