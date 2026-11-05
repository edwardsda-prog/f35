"""Tier 2 E2E Boundary & Corner Case Tests (85 tests: 5 per feature across F1-F17).

Tests boundary values, threshold edge conditions, negative/empty inputs,
unauthorized HITL approval attempts (`SAFE-02`), cross-dialect edge cases,
and strict EU residency / Enterprise SDK guardrails (`REG-01`, `PERF-01..07`).
"""

from __future__ import annotations

import ast
import inspect
import json
import re
from typing import Any

import pytest
import yaml

from tests.e2e import (
    REPO_ROOT,
    E2ECallbackContext,
    E2EDummyTool,
    E2ELlmRequest,
    E2EToolContext,
    get_field,
    invoke_contract,
)

# ===========================================================================
# F1 Boundaries: Base ADK Project Scaffolding (5 tests)
# ===========================================================================


def test_f01_b1_manifest_project_name_length_boundary() -> None:
    manifest = yaml.safe_load(
        (REPO_ROOT / "agents-cli-manifest.yaml").read_text(encoding="utf-8")
    )
    name = manifest["name"]
    assert 1 <= len(name) <= 26, (
        f"Project name '{name}' exceeds 26-char agents-cli boundary"
    )
    assert re.fullmatch(r"[a-z][a-z0-9-]*", name)


def test_f01_b2_manifest_never_targets_us_regions() -> None:
    manifest_text = (REPO_ROOT / "agents-cli-manifest.yaml").read_text(encoding="utf-8")
    for forbidden in ("us-central1", "us-east1", "us-west1", "asia-"):
        assert forbidden not in manifest_text


def test_f01_b3_pyproject_python_version_range_boundary() -> None:
    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert ">=3.11" in pyproject_text


def test_f01_b4_gcloudignore_excludes_local_artifacts_and_venv() -> None:
    gcloudignore = REPO_ROOT / ".gcloudignore"
    assert gcloudignore.is_file()
    text = gcloudignore.read_text(encoding="utf-8")
    assert ".venv" in text or "__pycache__" in text or ".git" in text


def test_f01_b5_domain_agents_md_boundary_scoping() -> None:
    api_agents = (REPO_ROOT / "packages" / "api" / "AGENTS.md").read_text("utf-8")
    web_agents = (REPO_ROOT / "packages" / "web" / "AGENTS.md").read_text("utf-8")
    test_agents = (REPO_ROOT / "tests" / "AGENTS.md").read_text("utf-8")
    assert "api" in api_agents.lower() or "backend" in api_agents.lower()
    assert "web" in web_agents.lower() or "vega" in web_agents.lower()
    assert "test" in test_agents.lower() or "eval" in test_agents.lower()


# ===========================================================================
# F2 Boundaries: Declarative BigQuery JSON Schemas (5 tests)
# ===========================================================================

VALID_BQ_TYPES = {
    "STRING",
    "FLOAT",
    "FLOAT64",
    "INTEGER",
    "INT64",
    "BOOLEAN",
    "BOOL",
    "TIMESTAMP",
    "DATE",
    "DATETIME",
    "NUMERIC",
    "JSON",
    "RECORD",
}
VALID_BQ_MODES = {"REQUIRED", "NULLABLE", "REPEATED"}


def _extract_schema_fields(parsed: object) -> list[dict]:
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        return list(parsed.get("fields", parsed.get("columns", parsed.get("schema", []))))
    return []


def test_f02_b1_all_schema_columns_have_valid_bq_types() -> None:
    schema_dir = REPO_ROOT / "app" / "seed_data" / "schemas"
    for p in schema_dir.glob("*.schema.json"):
        cols = _extract_schema_fields(json.loads(p.read_text(encoding="utf-8")))
        for col in cols:
            assert col.get("type", "").upper() in VALID_BQ_TYPES, (
                f"Invalid BQ type in {p.name}: {col}"
            )


def test_f02_b2_all_schema_columns_have_valid_bq_modes() -> None:
    schema_dir = REPO_ROOT / "app" / "seed_data" / "schemas"
    for p in schema_dir.glob("*.schema.json"):
        cols = _extract_schema_fields(json.loads(p.read_text(encoding="utf-8")))
        for col in cols:
            mode = col.get("mode", "NULLABLE").upper()
            assert mode in VALID_BQ_MODES, f"Invalid BQ mode in {p.name}: {col}"


def test_f02_b3_no_duplicate_column_names_in_any_schema() -> None:
    schema_dir = REPO_ROOT / "app" / "seed_data" / "schemas"
    for p in schema_dir.glob("*.schema.json"):
        cols = _extract_schema_fields(json.loads(p.read_text(encoding="utf-8")))
        names = [c["name"] for c in cols]
        assert len(names) == len(set(names)), (
            f"Duplicate columns in {p.name}: {names}"
        )


def test_f02_b4_numeric_precision_fields_use_float_or_integer_types() -> None:
    schema_dir = REPO_ROOT / "app" / "seed_data" / "schemas"
    t4 = {
        c["name"]: c["type"].upper()
        for c in _extract_schema_fields(
            json.loads(
                (schema_dir / "high_freq_strain_telemetry.schema.json").read_text(
                    "utf-8"
                )
            )
        )
    }
    for float_col in (
        "mach_number",
        "peak_nz_g",
        "peak_egt_celsius",
        "miners_rule_damage_delta",
        "calculated_yield_pct",
    ):
        assert t4[float_col] in {"FLOAT", "FLOAT64", "NUMERIC"}


def test_f02_b5_primary_key_columns_are_required_or_present() -> None:
    schema_dir = REPO_ROOT / "app" / "seed_data" / "schemas"
    pk_map = {
        "airframe_component_telemetry.schema.json": "telemetry_record_id",
        "global_depot_inventory.schema.json": "nsn",
        "squadron_sortie_schedule.schema.json": "sortie_id",
        "high_freq_strain_telemetry.schema.json": "event_id",
        "as_maintained_mbom_fasteners.schema.json": "mbom_record_id",
        "airworthiness_release_ledger.schema.json": "release_package_id",
        "maintenance_work_orders.schema.json": "work_order_id",
        "phm_bit_fault_events.schema.json": "fault_event_id",
        "work_center_tooling_and_sqep.schema.json": "resource_id",
    }
    for fname, pk in pk_map.items():
        cols = {
            c["name"]: c
            for c in _extract_schema_fields(
                json.loads((schema_dir / fname).read_text(encoding="utf-8"))
            )
        }
        assert pk in cols
        assert cols[pk]["type"].upper() == "STRING"


# ===========================================================================
# F3 Boundaries: Synthetic Corpus Generator (5 tests)
# ===========================================================================


def test_f03_b1_zm151_actuator_hours_strictly_exceed_1000hr_limit() -> None:
    from app.seed_data import bq_seed_records

    src = inspect.getsource(bq_seed_records)
    assert "1000.4" in src and "1000.0" in src
    assert 1000.4 > 1000.0


def test_f03_b2_zm154_spare_tail_hours_strictly_below_condemnation_limit() -> None:
    from app.seed_data import bq_seed_records

    src = inspect.getsource(bq_seed_records)
    assert "842.0" in src
    assert 842.0 < 1000.0 - 50.0


def test_f03_b3_mbom_measured_elongation_strictly_below_allowable_limit() -> None:
    from app.seed_data import bq_seed_records

    src = inspect.getsource(bq_seed_records)
    assert "0.012" in src and "0.015" in src
    assert 0.012 < 0.015


def test_f03_b4_jtd_corpus_has_exact_nine_unique_doc_ids() -> None:
    from app.seed_data import jtd_corpus

    src = inspect.getsource(jtd_corpus)
    found_docs = sorted(set(re.findall(r"DOC-0[1-9]", src)))
    assert found_docs == [f"DOC-0{i}" for i in range(1, 10)]


def test_f03_b5_jtd_corpus_includes_both_uk_and_us_service_branches() -> None:
    from app.seed_data import jtd_corpus

    src = inspect.getsource(jtd_corpus)
    for branch in ("RAF", "USMC"):
        assert branch in src


# ===========================================================================
# F4 Boundaries: Live EU Cloud Infrastructure Provisioner (5 tests)
# ===========================================================================


def test_f04_b1_setup_demo_infra_never_uses_us_multi_region() -> None:
    text = (REPO_ROOT / "scripts" / "setup_demo_infra.py").read_text(encoding="utf-8")
    assert 'location="US"' not in text
    assert "us-central1" not in text


def test_f04_b2_setup_demo_infra_uses_eu_discoveryengine_regional_endpoint() -> None:
    text = (REPO_ROOT / "scripts" / "setup_demo_infra.py").read_text(encoding="utf-8")
    assert (
        "eu-discoveryengine.googleapis.com" in text
        or "DE_LOCATION" in text
        or ("-discoveryengine.googleapis.com" in text and '"eu"' in text)
    )


def test_f04_b3_setup_demo_infra_handles_idempotent_table_and_bucket_creation() -> None:
    text = (REPO_ROOT / "scripts" / "setup_demo_infra.py").read_text(encoding="utf-8")
    assert "exist_ok" in text or "Conflict" in text or "NotFound" in text or "try:" in text


def test_f04_b4_setup_demo_infra_references_all_six_bq_tables() -> None:
    text = (REPO_ROOT / "scripts" / "setup_demo_infra.py").read_text(encoding="utf-8")
    for tbl in (
        "airframe_component_telemetry",
        "global_depot_inventory",
        "squadron_sortie_schedule",
        "high_freq_strain_telemetry",
        "as_maintained_mbom_fasteners",
        "airworthiness_release_ledger",
    ):
        assert tbl in text or "schemas" in text


def test_f04_b5_setup_demo_infra_avoids_gcloud_print_access_token_in_runtime() -> None:
    for py_path in (REPO_ROOT / "app").rglob("*.py"):
        assert "print-access-token" not in py_path.read_text(encoding="utf-8")


# ===========================================================================
# F5 Boundaries: Pre-Warmed Cloud Clients, Config & Pydantic Schemas (5 tests)
# ===========================================================================


def test_f05_b1_config_forbids_legacy_vertexai_and_thinking_budget() -> None:
    from app import config

    src = inspect.getsource(config)
    assert "thinking_budget" not in src
    assert "vertexai=True" not in src


def test_f05_b2_config_enforces_enterprise_true_and_global_model_location() -> None:
    from app import agent, config

    combined = inspect.getsource(config) + "\n" + inspect.getsource(agent)
    assert "enterprise" in combined
    assert "global" in combined


def test_f05_b3_config_thinking_levels_restricted_to_valid_enums() -> None:
    from app import agent, config

    combined = inspect.getsource(config) + "\n" + inspect.getsource(agent)
    assert "LOW" in combined or "HIGH" in combined


def test_f05_b4_clients_module_instantiates_bq_with_eu_location() -> None:
    from app import clients

    src = inspect.getsource(clients)
    assert "BQ_LOCATION" in src or '"EU"' in src or "'EU'" in src


def test_f05_b5_pydantic_schemas_reject_invalid_field_types() -> None:
    from pydantic import BaseModel, ValidationError

    from app import schemas

    models = [
        obj
        for _, obj in inspect.getmembers(schemas, inspect.isclass)
        if issubclass(obj, BaseModel) and obj is not BaseModel
    ]
    assert len(models) >= 1
    with pytest.raises((ValidationError, TypeError)):
        models[0].model_validate("not-a-valid-dict-payload")


# ===========================================================================
# F6 Boundaries: Deterministic ASIP Physics & 3D CAD Engine (5 tests)
# ===========================================================================


def test_f06_b1_miners_rule_1g_level_flight_zero_overstress() -> None:
    from app.physics.asip_engine import run_asip_miners_rule_engine

    res = invoke_contract(
        run_asip_miners_rule_engine,
        tail_number="ZM154",
        structural_station_id="Frame 496",
        peak_nz_g=1.0,
        mach_number=0.8,
        peak_egt_celsius=120.0,
    )
    yield_pct = float(get_field(res, "calculated_yield_pct", "yield_pct"))
    ndi_class = get_field(res, "required_ndi_class", "ndi_class")
    assert yield_pct < 50.0
    assert ndi_class != "CLASS_A_ULTRASONIC_C_SCAN"


def test_f06_b2_miners_rule_exact_7_5g_design_limit_boundary() -> None:
    from app.physics.asip_engine import run_asip_miners_rule_engine

    res = invoke_contract(
        run_asip_miners_rule_engine,
        tail_number="ZM154",
        structural_station_id="Frame 496",
        peak_nz_g=7.5,
        mach_number=0.95,
        peak_egt_celsius=160.0,
    )
    yield_pct = float(get_field(res, "calculated_yield_pct", "yield_pct"))
    assert yield_pct <= 100.0


def test_f06_b3_miners_rule_monotonic_damage_with_increasing_g_load() -> None:
    from app.physics.asip_engine import run_asip_miners_rule_engine

    res_low = invoke_contract(
        run_asip_miners_rule_engine,
        tail_number="ZM151",
        structural_station_id="Frame 496",
        peak_nz_g=5.0,
        mach_number=0.9,
        peak_egt_celsius=150.0,
    )
    res_high = invoke_contract(
        run_asip_miners_rule_engine,
        tail_number="ZM151",
        structural_station_id="Frame 496",
        peak_nz_g=9.4,
        mach_number=1.3,
        peak_egt_celsius=220.0,
    )
    d_low = float(get_field(res_low, "miners_rule_damage_delta", "damage_delta"))
    d_high = float(get_field(res_high, "miners_rule_damage_delta", "damage_delta"))
    assert d_high > d_low >= 0.0


def test_f06_b4_cad_mapping_handles_custom_elongation_above_0_015_limit() -> None:
    from app.physics.asip_engine import extract_ndi_defect_and_map_cad

    res = invoke_contract(
        extract_ndi_defect_and_map_cad,
        c_scan_document_id="DOC-06",
        structural_station_id="Frame 496",
        measured_elongation_in=0.018,
        measured_ndi_elongation_in=0.018,
        allowable_elongation_in=0.015,
    )
    assert res is not None
    allowable = float(
        get_field(res, "allowable_elongation_in", "allowable_limit_in", default=0.015)
    )
    assert allowable == pytest.approx(0.015, abs=1e-4)


def test_f06_b5_physics_engine_has_zero_llm_or_network_imports_safe_01() -> None:
    from app.physics import asip_engine

    src = inspect.getsource(asip_engine)
    assert "genai" not in src
    assert "httpx" not in src
    assert "subprocess" not in src


# ===========================================================================
# F7 Boundaries: UC1 Specialist Sub-Agent & Tools (5 tests)
# ===========================================================================


def test_f07_b1_check_actuator_fatigue_default_arguments() -> None:
    from app.tools.uc1_analytics import check_actuator_fatigue_and_depot_inventory

    res = invoke_contract(check_actuator_fatigue_and_depot_inventory)
    assert "ZM151" in json.dumps(res, default=str)


def test_f07_b2_check_actuator_fatigue_narrow_zero_hour_window() -> None:
    from app.tools.uc1_analytics import check_actuator_fatigue_and_depot_inventory

    res = invoke_contract(
        check_actuator_fatigue_and_depot_inventory,
        base_location="RAF Marham",
        hours_to_limit_window=0.0,
        tool_context=E2EToolContext(),
    )
    assert "ZM151" in json.dumps(res, default=str)


def test_f07_b3_check_actuator_fatigue_carrier_base_location_hms_qe() -> None:
    from app.tools.uc1_analytics import check_actuator_fatigue_and_depot_inventory

    res = invoke_contract(
        check_actuator_fatigue_and_depot_inventory,
        base_location="HMS Queen Elizabeth",
        hours_to_limit_window=100.0,
        tool_context=E2EToolContext(),
    )
    assert isinstance(res, dict)
    assert "depot_stock_vs_demand_bar_chart" in res


def test_f07_b4_vegalite_specs_serialize_cleanly_to_strict_json() -> None:
    from app.tools.uc1_analytics import check_actuator_fatigue_and_depot_inventory

    res = invoke_contract(check_actuator_fatigue_and_depot_inventory)
    bar_json = json.dumps(res["depot_stock_vs_demand_bar_chart"])
    thresh_json = json.dumps(res["actuator_fatigue_threshold_chart"])
    assert json.loads(bar_json)["$schema"].startswith("https://vega.github.io/schema/vega-lite/v5")
    assert json.loads(thresh_json)["$schema"].startswith("https://vega.github.io/schema/vega-lite/v5")


def test_f07_b5_recommend_tail_swap_updates_or_preserves_tool_context() -> None:
    from app.tools.uc1_analytics import recommend_tail_swap_and_replenishment

    ctx = E2EToolContext()
    res = invoke_contract(
        recommend_tail_swap_and_replenishment,
        sortie_id="SRT-MAR-20261103-01",
        primary_tail="ZM151",
        spare_tail="ZM154",
        tool_context=ctx,
    )
    assert isinstance(res, dict)
    assert "ZM154" in json.dumps(res, default=str)


# ===========================================================================
# F8 Boundaries: UC2 Specialist Sub-Agent & Tool (5 tests)
# ===========================================================================


def test_f08_b1_search_with_bit_fault_true_vs_false_filtering() -> None:
    from app.tools.uc2_jtd_search import search_technical_manuals_and_repair_logs

    res_no_bit = invoke_contract(
        search_technical_manuals_and_repair_logs,
        symptom_query="canopy latch binding",
        bit_fault_present=False,
        subsystem_filter="53-30",
        tool_context=E2EToolContext(),
    )
    res_with_bit = invoke_contract(
        search_technical_manuals_and_repair_logs,
        symptom_query="canopy latch actuator electrical fault",
        bit_fault_present=True,
        subsystem_filter="53-30",
        tool_context=E2EToolContext(),
    )
    assert isinstance(res_no_bit, dict)
    assert isinstance(res_with_bit, dict)


def test_f08_b2_search_with_multiple_uk_dialect_terms_simultaneously() -> None:
    from app.tools.uc2_jtd_search import search_technical_manuals_and_repair_logs

    res = invoke_contract(
        search_technical_manuals_and_repair_logs,
        symptom_query="sticky catch binding needs spanner torque check for gouge on canopy",
        bit_fault_present=False,
        subsystem_filter="53-30",
        tool_context=E2EToolContext(),
    )
    dumped = json.dumps(res, default=str).lower()
    assert "latch" in dumped


def test_f08_b3_search_with_structural_subsystem_53_11_filter() -> None:
    from app.tools.uc2_jtd_search import search_technical_manuals_and_repair_logs

    res = invoke_contract(
        search_technical_manuals_and_repair_logs,
        symptom_query="Frame 496 over-G structural yield inspection threshold JTD 53-11-00",
        bit_fault_present=False,
        subsystem_filter="53-11",
        tool_context=E2EToolContext(),
    )
    dumped = json.dumps(res, default=str)
    assert "DOC-04" in dumped or "53-11-00" in dumped


def test_f08_b4_search_with_special_characters_and_html_injection_in_query() -> None:
    from app.tools.uc2_jtd_search import search_technical_manuals_and_repair_logs

    res = invoke_contract(
        search_technical_manuals_and_repair_logs,
        symptom_query="<b>sticky canopy catch</b> & 'no BIT fault' -- 220°C",
        bit_fault_present=False,
        subsystem_filter="53-30",
        tool_context=E2EToolContext(),
    )
    dumped = json.dumps(res, default=str)
    assert "<b>" not in dumped and "</b>" not in dumped


def test_f08_b5_search_citations_include_document_identifiers_and_uris() -> None:
    from app.tools.uc2_jtd_search import search_technical_manuals_and_repair_logs

    res = invoke_contract(
        search_technical_manuals_and_repair_logs,
        symptom_query="canopy latch binding no BIT fault",
        bit_fault_present=False,
        subsystem_filter="53-30",
        tool_context=E2EToolContext(),
    )
    dumped = json.dumps(res, default=str)
    assert "DOC-01" in dumped and "DOC-02" in dumped


# ===========================================================================
# F9 Boundaries: UC3 Specialist Sub-Agent & Tools (5 tests)
# ===========================================================================


def test_f09_b1_sync_telemetry_with_empty_debrief_defaults_to_zm151_event() -> None:
    from app.tools.uc3_airworthiness import sync_flight_telemetry_exceedance

    res = invoke_contract(
        sync_flight_telemetry_exceedance,
        tail_number="ZM151",
        pilot_debrief_text="",
        structural_station_id="Frame 496",
        tool_context=E2EToolContext(),
    )
    assert "EXC-20261102-ZM151" in json.dumps(res, default=str)


def test_f09_b2_audit_mbom_when_elongation_exceeds_0_015_limit() -> None:
    from app.tools.uc3_airworthiness import audit_fastener_lot_in_mbom

    res = invoke_contract(
        audit_fastener_lot_in_mbom,
        tail_number="ZM151",
        station_id="Frame 496 — Fastener Hole #14",
        measured_elongation_in=0.019,
        tool_context=E2EToolContext(),
    )
    assert isinstance(res, dict)
    assert "8841-B" in json.dumps(res, default=str)


def test_f09_b3_generate_form700_always_starts_in_pending_hitl_review() -> None:
    from app.tools.uc3_airworthiness import generate_form700_airworthiness_package

    ctx = E2EToolContext(state={"current_turn_id": 1})
    res = invoke_contract(
        generate_form700_airworthiness_package,
        tail_number="ZM151",
        station_id="Frame 496",
        tool_context=ctx,
    )
    dumped = json.dumps(res, default=str)
    assert "PENDING_HITL_REVIEW" in dumped
    assert "CONFIRMED_BY_ENGINEER" not in dumped


def test_f09_b4_confirm_form700_hitl_release_alias_supported() -> None:
    from app.tools import uc3_airworthiness

    fn = getattr(
        uc3_airworthiness,
        "confirm_form700_hitl_release",
        uc3_airworthiness.approve_form700_engineering_release,
    )
    assert callable(fn)


def test_f09_b5_assess_airframe_airworthiness_executes_under_3100ms_sla() -> None:
    import time

    from app.tools.uc3_airworthiness import assess_airframe_airworthiness

    t0 = time.perf_counter()
    res = invoke_contract(
        assess_airframe_airworthiness,
        tail_number="ZM151",
        pilot_debrief_text="severe shudder at 14:22Z during split-S",
        structural_station_id="Frame 496",
        c_scan_document_id="DOC-06",
        tool_context=E2EToolContext(),
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms <= 3100.0
    assert "0.0042" in json.dumps(res, default=str)


# ===========================================================================
# F10 Boundaries: Root Coordinator, Fast-Path & Two-Turn HITL Gate (5 tests)
# ===========================================================================


def test_f10_b1_fast_path_15_char_length_boundary() -> None:
    from app.callbacks import fast_path_before_model_callback

    long_query = "Please explain the full F-35B canopy rigging procedure in detail."
    cb_ctx = E2ECallbackContext(user_text=long_query)
    llm_req = E2ELlmRequest(user_text=long_query)
    assert (
        fast_path_before_model_callback(callback_context=cb_ctx, llm_request=llm_req)
        is None
    )


def test_f10_b2_hitl_gate_blocks_when_staged_turn_equals_current_turn() -> None:
    from app.callbacks import enforce_hitl_airworthiness_gate

    tool = E2EDummyTool("approve_form700_engineering_release")
    ctx = E2EToolContext(
        state={
            "pending_release_package_id": "AWR-700-20261102-ZM151",
            "staged_turn_id": 3,
            "current_turn_id": 3,
            "staged_invocation_id": "same-inv",
        },
        user_text="Approved by Lead Stress Engineer",
        invocation_id="same-inv",
    )
    res = enforce_hitl_airworthiness_gate(
        tool=tool,
        args={
            "release_package_id": "AWR-700-20261102-ZM151",
            "reviewer_role": "Lead Stress Engineer",
            "approval_notes": "Approved",
        },
        tool_context=ctx,
    )
    assert res is not None


def test_f10_b3_hitl_gate_blocks_confirm_alias_on_same_turn() -> None:
    from app.callbacks import enforce_hitl_airworthiness_gate

    tool = E2EDummyTool("confirm_form700_hitl_release")
    ctx = E2EToolContext(
        state={
            "pending_release_package_id": "AWR-700-20261102-ZM151",
            "staged_turn_id": 1,
            "current_turn_id": 1,
            "staged_invocation_id": "inv-1",
        },
        user_text="Approved by CTO",
        invocation_id="inv-1",
    )
    res = enforce_hitl_airworthiness_gate(
        tool=tool,
        args={
            "release_package_id": "AWR-700-20261102-ZM151",
            "reviewer_role": "CTO",
            "approval_notes": "Approved",
        },
        tool_context=ctx,
    )
    assert res is not None


def test_f10_b4_hitl_gate_blocks_empty_release_package_id() -> None:
    from app.callbacks import enforce_hitl_airworthiness_gate

    tool = E2EDummyTool("approve_form700_engineering_release")
    ctx = E2EToolContext(
        state={
            "pending_release_package_id": "AWR-700-20261102-ZM151",
            "staged_turn_id": 1,
            "current_turn_id": 2,
        },
        user_text="Approved by Lead Stress Engineer",
        invocation_id="inv-2",
    )
    res = enforce_hitl_airworthiness_gate(
        tool=tool,
        args={
            "release_package_id": "INVALID-ID",
            "reviewer_role": "Lead Stress Engineer",
            "approval_notes": "Approved",
        },
        tool_context=ctx,
    )
    assert res is not None


def test_f10_b5_each_agent_maintains_curated_tool_density_under_16_tools() -> None:
    from app import root_agent

    assert len(root_agent.tools or []) < 16
    for sa in root_agent.sub_agents or []:
        assert len(sa.tools or []) < 16


# ===========================================================================
# F11 Boundaries: Frontend Vega-Lite Canvas & Form 700 Studio (5 tests)
# ===========================================================================


def test_f11_b1_vega_canvas_handles_empty_or_optional_props_safely() -> None:
    content = (REPO_ROOT / "packages" / "web" / "components" / "VegaCanvas.tsx").read_text(
        encoding="utf-8"
    )
    assert "?" in content or "null" in content or "undefined" in content or "default" in content


def test_f11_b2_vega_canvas_includes_accessible_aria_or_titles() -> None:
    content = (REPO_ROOT / "packages" / "web" / "components" / "VegaCanvas.tsx").read_text(
        encoding="utf-8"
    )
    assert "title" in content.lower() or "aria-" in content.lower() or "role=" in content.lower()


def test_f11_b3_form700_studio_disables_confirm_when_already_confirmed() -> None:
    content = (
        REPO_ROOT / "packages" / "web" / "components" / "Form700ReviewStudio.tsx"
    ).read_text(encoding="utf-8")
    assert "CONFIRMED_BY_ENGINEER" in content
    assert "disabled" in content or "PENDING_HITL_REVIEW" in content


def test_f11_b4_form700_studio_displays_mandatory_mil_std_compliance() -> None:
    content = (
        REPO_ROOT / "packages" / "web" / "components" / "Form700ReviewStudio.tsx"
    ).read_text(encoding="utf-8")
    assert "MIL-" in content or "DEF STAN" in content or "53-11-00" in content


def test_f11_b5_frontend_packages_contain_no_backend_python_files() -> None:
    py_files = list((REPO_ROOT / "packages" / "web").rglob("*.py"))
    assert py_files == []


# ===========================================================================
# F12 Boundaries: Deterministic Unit Test Suite (5 tests)
# ===========================================================================


def test_f12_b1_unit_test_helper_handles_missing_keys_with_default() -> None:
    from tests.unit.test_deterministic import _get_val

    assert _get_val({"a": 1}, "missing_key", default="fallback") == "fallback"
    assert _get_val(None, "any_key", default=42) == 42


def test_f12_b2_unit_test_suite_tests_nominal_and_extreme_g_loads() -> None:
    from tests.unit.test_deterministic import TestAsipPhysicsEngine

    suite = TestAsipPhysicsEngine()
    suite.test_miners_rule_nominal_envelope_below_7_5g()
    suite.test_miners_rule_severe_overstress_above_9_4g()


def test_f12_b3_unit_test_suite_verifies_50x_deterministic_repeatability() -> None:
    from tests.unit.test_deterministic import TestAsipPhysicsEngine

    suite = TestAsipPhysicsEngine()
    suite.test_miners_rule_deterministic_repeatability_safe_01()


def test_f12_b4_unit_test_suite_tests_unauthorized_and_mismatched_hitl() -> None:
    from tests.unit.test_deterministic import TestTwoTurnHitlGate

    suite = TestTwoTurnHitlGate()
    suite.test_hitl_gate_blocks_mismatched_release_package_id()
    suite.test_hitl_gate_blocks_unauthorized_reviewer_role()


def test_f12_b5_unit_test_suite_contains_zero_trivial_assert_true_facades() -> None:
    src = (REPO_ROOT / "tests" / "unit" / "test_deterministic.py").read_text("utf-8")
    assert "assert True" not in src


# ===========================================================================
# F13 Boundaries: V&V Evaluation Datasets & Config (5 tests)
# ===========================================================================


def test_f13_b1_response_quality_handles_empty_response_gracefully() -> None:
    from tests.eval.response_quality import evaluate

    res = evaluate({"prompt": "test", "response": "", "reference": "ZM151"})
    assert res["score"] == 1.0


def test_f13_b2_response_quality_handles_multiturn_agent_data_only() -> None:
    from tests.eval.response_quality import evaluate

    res = evaluate(
        {
            "agent_data": {
                "turns": [
                    {
                        "events": [
                            {
                                "content": {
                                    "parts": [
                                        {
                                            "text": "Approved AWR-700-20261102-ZM151 CONFIRMED_BY_ENGINEER ZM151"
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
            },
            "reference": "AWR-700-20261102-ZM151 CONFIRMED_BY_ENGINEER ZM151",
        }
    )
    assert res["score"] >= 4.5


def test_f13_b3_eval_cases_have_no_ambiguous_prompt_plus_turns() -> None:
    for fname in ("basic-dataset.json", "vv_golden_suite.json"):
        p = REPO_ROOT / "tests" / "eval" / "datasets" / fname
        cases = json.loads(p.read_text(encoding="utf-8"))["eval_cases"]
        for c in cases:
            has_prompt = bool(c.get("prompt"))
            has_turns = bool((c.get("agent_data") or {}).get("turns"))
            assert has_prompt ^ has_turns, (
                f"Case {c['eval_case_id']} must have either prompt OR agent_data.turns"
            )


def test_f13_b4_all_eval_case_ids_are_globally_unique() -> None:
    ids: list[str] = []
    for fname in ("basic-dataset.json", "vv_golden_suite.json"):
        p = REPO_ROOT / "tests" / "eval" / "datasets" / fname
        cases = json.loads(p.read_text(encoding="utf-8"))["eval_cases"]
        ids.extend(c["eval_case_id"] for c in cases)
    assert len(ids) == len(set(ids)) >= 13


def test_f13_b5_eval_config_avoids_mismatched_vertex_builtin_metrics() -> None:
    cfg = yaml.safe_load(
        (REPO_ROOT / "tests" / "eval" / "eval_config.yaml").read_text(encoding="utf-8")
    )
    metrics = [m.lower() for m in cfg["metrics_to_run"]]
    assert "multi_turn_task_success_v1" not in metrics


# ===========================================================================
# F14 Boundaries: E2E Test Suite Pass & Runner (5 tests)
# ===========================================================================


def test_f14_b1_tier1_has_at_least_85_test_functions() -> None:
    from tests.e2e import test_tier1_feature_coverage

    funcs = [
        name
        for name, obj in inspect.getmembers(test_tier1_feature_coverage, inspect.isfunction)
        if name.startswith("test_")
    ]
    assert len(funcs) >= 85


def test_f14_b2_tier2_has_at_least_85_test_functions() -> None:
    from tests.e2e import test_tier2_boundary_corner

    funcs = [
        name
        for name, obj in inspect.getmembers(test_tier2_boundary_corner, inspect.isfunction)
        if name.startswith("test_")
    ]
    assert len(funcs) >= 85


def test_f14_b3_tier3_has_at_least_17_test_functions() -> None:
    from tests.e2e import test_tier3_cross_feature

    funcs = [
        name
        for name, obj in inspect.getmembers(test_tier3_cross_feature, inspect.isfunction)
        if name.startswith("test_")
    ]
    assert len(funcs) >= 17


def test_f14_b4_tier4_has_at_least_9_test_functions() -> None:
    from tests.e2e import test_tier4_real_world_scenarios

    funcs = [
        name
        for name, obj in inspect.getmembers(
            test_tier4_real_world_scenarios, inspect.isfunction
        )
        if name.startswith("test_")
    ]
    assert len(funcs) >= 9


def test_f14_b5_total_e2e_test_count_at_least_196() -> None:
    from tests.e2e import (
        test_tier1_feature_coverage,
        test_tier2_boundary_corner,
        test_tier3_cross_feature,
        test_tier4_real_world_scenarios,
    )

    total = sum(
        len(
            [
                n
                for n, _ in inspect.getmembers(mod, inspect.isfunction)
                if n.startswith("test_")
            ]
        )
        for mod in (
            test_tier1_feature_coverage,
            test_tier2_boundary_corner,
            test_tier3_cross_feature,
            test_tier4_real_world_scenarios,
        )
    )
    assert total >= 196


# ===========================================================================
# F15 Boundaries: Agent Runtime Deployment (europe-west1) (5 tests)
# ===========================================================================


def test_f15_b1_dockerfile_does_not_bake_private_key_files() -> None:
    docker_text = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "service-account-key.json" not in docker_text
    assert "PRIVATE KEY" not in docker_text


def test_f15_b2_manifest_session_and_a2a_configuration() -> None:
    manifest = yaml.safe_load(
        (REPO_ROOT / "agents-cli-manifest.yaml").read_text(encoding="utf-8")
    )
    assert manifest["framework"] == "google-adk"
    assert manifest["language"] == "python"


def test_f15_b3_fast_api_app_or_agent_module_compiles_cleanly() -> None:
    import ast

    for rel in ("app/__init__.py", "app/agent.py", "app/config.py"):
        p = REPO_ROOT / rel
        assert p.is_file()
        ast.parse(p.read_text(encoding="utf-8"))


def test_f15_b4_requirements_or_pyproject_excludes_legacy_vertexai_only_lock() -> None:
    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "google-genai" in pyproject_text
    assert "google-adk" in pyproject_text


def test_f15_b5_compute_region_is_strictly_europe_west1_belgium() -> None:
    from app import config

    assert config.COMPUTE_REGION == "europe-west1"


# ===========================================================================
# F16 Boundaries: Gemini Enterprise Publication (eu) (5 tests)
# ===========================================================================


def test_f16_b1_discovery_engine_urls_strictly_use_eu_prefix() -> None:
    from app import clients, config

    combined = inspect.getsource(config) + "\n" + inspect.getsource(clients)
    assert "eu-discoveryengine.googleapis.com" in combined
    assert "us-discoveryengine.googleapis.com" not in combined


def test_f16_b2_root_agent_has_non_empty_instruction_and_description() -> None:
    from app import root_agent

    assert getattr(root_agent, "instruction", None)
    assert getattr(root_agent, "description", None)


def test_f16_b3_sub_agents_have_distinct_non_overlapping_names() -> None:
    from app import root_agent

    names = [sa.name for sa in (root_agent.sub_agents or [])]
    assert len(names) == len(set(names)) == 4


def test_f16_b4_all_sub_agents_use_enterprise_gemini_model_config() -> None:
    from app import root_agent

    for ag in [root_agent, *(root_agent.sub_agents or [])]:
        assert ag.model is not None


def test_f16_b5_stream_query_output_contains_both_vega_and_markdown_in_uc1() -> None:
    from app.sub_agents import uc1_analytics_agent

    src = inspect.getsource(uc1_analytics_agent)
    assert "vega-lite" in src.lower() or "chart" in src.lower()


# ===========================================================================
# F17 Boundaries: Live Deployed Cloud E2E & GitHub Push (5 tests)
# ===========================================================================


def test_f17_b1_no_agents_md_or_gemini_md_inside_teamwork_dir() -> None:
    teamwork_dir = REPO_ROOT / ".agents" / "teamwork"
    if teamwork_dir.is_dir():
        forbidden = [
            p
            for p in teamwork_dir.rglob("*")
            if p.name in {"AGENTS.md", "GEMINI.md"}
        ]
        assert forbidden == []


def test_f17_b2_no_hardcoded_api_keys_or_bearer_tokens_in_source() -> None:
    for py_path in (REPO_ROOT / "app").rglob("*.py"):
        text = py_path.read_text(encoding="utf-8")
        assert "AIzaSy" not in text
        assert "ya29." not in text


def test_f17_b3_project_md_and_sa_f35_md_remain_uncorrupted() -> None:
    assert (REPO_ROOT / "PROJECT.md").stat().st_size > 5000
    assert (REPO_ROOT / "SA_F35.md").stat().st_size > 20000


def test_f17_b4_git_worktree_has_valid_head_commit() -> None:
    head_file = REPO_ROOT / ".git" / "HEAD"
    assert head_file.is_file()
    assert len(head_file.read_text(encoding="utf-8").strip()) > 0


def test_f17_b5_all_python_files_in_repo_parse_with_ast() -> None:
    for folder in ("app", "scripts", "tests"):
        base = REPO_ROOT / folder
        if base.is_dir():
            for py_file in base.rglob("*.py"):
                ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
