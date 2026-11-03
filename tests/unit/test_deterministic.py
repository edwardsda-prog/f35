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
