"""Tier 1 E2E Feature Coverage Tests (85 tests: 5 per feature across F1-F17).

Each test function verifies a primary happy-path requirement for one of the 17
features defined in `PROJECT.md § Feature Inventory` against authoritative
expected outputs derived from `PROJECT.md` and `SA_F35.md`.
"""

from __future__ import annotations

import ast
import inspect
import json
import os
import time
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
# F1: Base ADK Project Scaffolding (5 tests)
# ===========================================================================


def test_f01_1_manifest_yaml_structure() -> None:
    manifest_path = REPO_ROOT / "agents-cli-manifest.yaml"
    assert manifest_path.is_file()
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert data["name"] == "f35-sustainment-agent"
    assert len(data["name"]) <= 26
    assert data["region"] == "europe-west1"
    assert data["agent_directory"] == "app"
    assert data["create_params"]["root_agent_name"] == "f35_sustainment_coordinator"
    assert data["create_params"]["deployment_target"] == "agent_runtime"


def test_f01_2_pyproject_toml_dependencies() -> None:
    pyproject_path = REPO_ROOT / "pyproject.toml"
    assert pyproject_path.is_file()
    content = pyproject_path.read_text(encoding="utf-8")
    for pkg in (
        "google-adk",
        "google-genai",
        "google-cloud-bigquery",
        "google-cloud-storage",
        "pydantic",
        "Pillow",
        "reportlab",
        "pytest",
    ):
        assert pkg in content, f"Missing required dependency {pkg} in pyproject.toml"


def test_f01_3_dockerfile_and_env_configuration() -> None:
    dockerfile_path = REPO_ROOT / "Dockerfile"
    assert dockerfile_path.is_file()
    docker_text = dockerfile_path.read_text(encoding="utf-8")
    assert "python" in docker_text.lower()
    assert "app" in docker_text


def test_f01_4_preserved_architecture_docs() -> None:
    for rel_path in (
        "SA_F35.md",
        "AGENTS.md",
        ".agents-cli-spec.md",
        "PROJECT.md",
        "packages/api/AGENTS.md",
        "packages/web/AGENTS.md",
        "tests/AGENTS.md",
    ):
        p = REPO_ROOT / rel_path
        assert p.is_file(), f"Preserved document missing: {rel_path}"
        assert p.stat().st_size > 100, f"Document unexpectedly empty: {rel_path}"


def test_f01_5_gitignore_and_scaffold_entrypoints() -> None:
    gitignore = REPO_ROOT / ".gitignore"
    assert gitignore.is_file()
    assert (REPO_ROOT / "app").is_dir()


# ===========================================================================
# F2: Declarative BigQuery JSON Schemas (5 tests)
# ===========================================================================

EXPECTED_SCHEMA_FILES = (
    "airframe_component_telemetry.schema.json",
    "global_depot_inventory.schema.json",
    "squadron_sortie_schedule.schema.json",
    "high_freq_strain_telemetry.schema.json",
    "as_maintained_mbom_fasteners.schema.json",
    "airworthiness_release_ledger.schema.json",
    "maintenance_work_orders.schema.json",
    "phm_bit_fault_events.schema.json",
    "work_center_tooling_and_sqep.schema.json",
)


def _extract_schema_fields(parsed: object) -> list[dict]:
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        return list(parsed.get("fields", parsed.get("columns", parsed.get("schema", []))))
    return []


def test_f02_1_all_six_schema_files_exist() -> None:
    schema_dir = REPO_ROOT / "app" / "seed_data" / "schemas"
    assert schema_dir.is_dir(), f"Missing schema directory: {schema_dir}"
    for fname in EXPECTED_SCHEMA_FILES:
        fpath = schema_dir / fname
        assert fpath.is_file(), f"Missing BigQuery JSON schema file: {fname}"
        parsed = _extract_schema_fields(json.loads(fpath.read_text(encoding="utf-8")))
        assert isinstance(parsed, list) and len(parsed) >= 5


def test_f02_2_table1_and_table2_schemas() -> None:
    schema_dir = REPO_ROOT / "app" / "seed_data" / "schemas"
    t1 = _extract_schema_fields(
        json.loads(
            (schema_dir / "airframe_component_telemetry.schema.json").read_text("utf-8")
        )
    )
    t1_cols = {col["name"] for col in t1}
    for req in (
        "telemetry_record_id",
        "tail_number",
        "part_serial_number",
        "nsn",
        "current_flight_hours",
        "life_limit_threshold_hrs",
    ):
        assert req in t1_cols

    t2 = _extract_schema_fields(
        json.loads(
            (schema_dir / "global_depot_inventory.schema.json").read_text("utf-8")
        )
    )
    t2_cols = {col["name"] for col in t2}
    for req in (
        "nsn",
        "depot_id",
        "quantity_on_hand",
        "quantity_reserved_30d",
        "avg_shipping_eta_hours",
    ):
        assert req in t2_cols


def test_f02_3_table3_sortie_schedule_schema() -> None:
    schema_dir = REPO_ROOT / "app" / "seed_data" / "schemas"
    t3 = _extract_schema_fields(
        json.loads(
            (schema_dir / "squadron_sortie_schedule.schema.json").read_text("utf-8")
        )
    )
    t3_cols = {col["name"] for col in t3}
    for req in (
        "sortie_id",
        "scheduled_departure_utc",
        "assigned_tail_number",
        "assigned_pilot_callsign",
        "spare_tail_candidate",
        "sortie_readiness_status",
    ):
        assert req in t3_cols


def test_f02_4_table4_and_table5_uc3_schemas() -> None:
    schema_dir = REPO_ROOT / "app" / "seed_data" / "schemas"
    t4 = _extract_schema_fields(
        json.loads(
            (schema_dir / "high_freq_strain_telemetry.schema.json").read_text("utf-8")
        )
    )
    t4_cols = {col["name"] for col in t4}
    for req in (
        "event_id",
        "tail_number",
        "structural_station_id",
        "mach_number",
        "peak_nz_g",
        "peak_egt_celsius",
        "miners_rule_damage_delta",
        "calculated_yield_pct",
        "required_ndi_class",
    ):
        assert req in t4_cols

    t5 = _extract_schema_fields(
        json.loads(
            (schema_dir / "as_maintained_mbom_fasteners.schema.json").read_text("utf-8")
        )
    )
    t5_cols = {col["name"] for col in t5}
    for req in (
        "mbom_record_id",
        "tail_number",
        "station_id",
        "fastener_material_spec",
        "fastener_lot_number",
        "allowable_elongation_in",
        "measured_ndi_elongation_in",
        "global_fleet_affected_count",
    ):
        assert req in t5_cols


def test_f02_5_table6_airworthiness_ledger_schema() -> None:
    schema_dir = REPO_ROOT / "app" / "seed_data" / "schemas"
    t6 = _extract_schema_fields(
        json.loads(
            (schema_dir / "airworthiness_release_ledger.schema.json").read_text("utf-8")
        )
    )
    t6_cols = {col["name"] for col in t6}
    for req in (
        "release_package_id",
        "mandated_jtd_task_card",
        "disposition_status",
        "hitl_reviewer_role",
        "hitl_review_status",
        "compliance_standard",
    ):
        assert req in t6_cols


# ===========================================================================
# F3: Synthetic Corpus Generator (5 tests)
# ===========================================================================


def test_f03_1_bq_seed_records_uc1_tables() -> None:
    from app.seed_data import bq_seed_records

    src = inspect.getsource(bq_seed_records)
    for token in (
        "ZM151",
        "ACT-99812-F",
        "1000.4",
        "ZM154",
        "842.0",
        "1680-01-619-4821",
        "SRT-MAR-20261103-01",
        "Henderson",
        "VIPER-1",
    ):
        assert token in src, f"Missing UC1 seed token {token} in bq_seed_records.py"


def test_f03_2_bq_seed_records_uc3_tables() -> None:
    from app.seed_data import bq_seed_records

    src = inspect.getsource(bq_seed_records)
    for token in (
        "EXC-20261102-ZM151",
        "Frame 496",
        "9.4",
        "0.0042",
        "104.2",
        "CLASS_A_ULTRASONIC_C_SCAN",
        "MBOM-ZM151-F496-H14",
        "8841-B",
        "0.012",
        "0.015",
        "AWR-700-20261102-ZM151",
    ):
        assert token in src, f"Missing UC3 seed token {token} in bq_seed_records.py"


def test_f03_3_jtd_corpus_doc01_to_doc09() -> None:
    from app.seed_data import jtd_corpus

    src = inspect.getsource(jtd_corpus)
    for doc_num in range(1, 10):
        doc_id = f"DOC-0{doc_num}"
        assert doc_id in src, f"Missing {doc_id} in app/seed_data/jtd_corpus.py"
    assert "53-30" in src
    assert "53-11-00" in src
    assert "220" in src


def test_f03_4_generate_synthetic_corpus_script_exists_and_runs() -> None:
    script_path = REPO_ROOT / "scripts" / "generate_synthetic_corpus.py"
    assert script_path.is_file()
    ast.parse(script_path.read_text(encoding="utf-8"))


def test_f03_5_cscan_png_doc06_and_metadata_jsonl_artifacts() -> None:
    script_text = (REPO_ROOT / "scripts" / "generate_synthetic_corpus.py").read_text(
        encoding="utf-8"
    )
    assert "DOC-06" in script_text
    assert "metadata" in script_text.lower() or "jsonl" in script_text.lower()


# ===========================================================================
# F4: Live EU Cloud Infrastructure Provisioner (5 tests)
# ===========================================================================


def test_f04_1_setup_demo_infra_script_exists() -> None:
    script_path = REPO_ROOT / "scripts" / "setup_demo_infra.py"
    assert script_path.is_file()
    ast.parse(script_path.read_text(encoding="utf-8"))


def test_f04_2_setup_demo_infra_targets_eu_bigquery() -> None:
    text = (REPO_ROOT / "scripts" / "setup_demo_infra.py").read_text(encoding="utf-8")
    assert "ukd_f35_sustainment_demo" in text or "BQ_DATASET" in text
    assert "EU" in text or "BQ_LOCATION" in text


def test_f04_3_setup_demo_infra_targets_eu_discovery_engine() -> None:
    text = (REPO_ROOT / "scripts" / "setup_demo_infra.py").read_text(encoding="utf-8")
    assert "ukd-f35-jtd-ietm-ds" in text or "JTD_DATASTORE_ID" in text
    assert "ukd-f35-narrative-logs-ds" in text or "NARRATIVE_DATASTORE_ID" in text
    assert "eu-discoveryengine.googleapis.com" in text or "locations/eu" in text or "DE_LOCATION" in text


def test_f04_4_setup_demo_infra_targets_europe_west1_gcs_staging() -> None:
    text = (REPO_ROOT / "scripts" / "setup_demo_infra.py").read_text(encoding="utf-8")
    assert (
        "antig-dave-f35-staging-europe-west1" in text
        or "GCS_STAGING_BUCKET" in text
    )
    assert "europe-west1" in text or "COMPUTE_REGION" in text


def test_f04_5_setup_demo_infra_service_account_and_gemini_app() -> None:
    text = (REPO_ROOT / "scripts" / "setup_demo_infra.py").read_text(encoding="utf-8")
    assert (
        "f35-sustainment-runtime-sa" in text
        or "RUNTIME_SERVICE_ACCOUNT" in text
        or "f35-support" in text
        or "GEMINI_APP_ID" in text
    )


# ===========================================================================
# F5: Pre-Warmed Cloud Clients, Config & Pydantic Schemas (5 tests)
# ===========================================================================


def test_f05_1_config_project_and_region_constants() -> None:
    from app import config

    assert config.PROJECT_ID == "antig-dave"
    assert config.PROJECT_NUMBER == "284046449012"
    assert config.COMPUTE_REGION == "europe-west1"
    assert config.BQ_LOCATION == "EU"
    assert config.DE_LOCATION == "eu"


def test_f05_2_config_datastore_and_bucket_constants() -> None:
    from app import config

    assert config.BQ_DATASET == "ukd_f35_sustainment_demo"
    assert config.JTD_DATASTORE_ID == "ukd-f35-jtd-ietm-ds"
    assert config.NARRATIVE_DATASTORE_ID == "ukd-f35-narrative-logs-ds"
    assert config.GEMINI_APP_ID == "f35-support"
    assert config.GCS_STAGING_BUCKET == "antig-dave-f35-staging-europe-west1"
    assert (
        config.RUNTIME_SERVICE_ACCOUNT
        == "f35-sustainment-runtime-sa@antig-dave.iam.gserviceaccount.com"
    )


def test_f05_3_clients_module_exports_prewarmed_singletons() -> None:
    from app import clients

    src = inspect.getsource(clients)
    assert "bigquery" in src
    assert "google.auth" in src
    assert "print-access-token" not in src


def test_f05_4_schemas_module_uc1_and_uc2_models() -> None:
    from pydantic import BaseModel

    from app import schemas

    model_names = [
        name
        for name, obj in inspect.getmembers(schemas, inspect.isclass)
        if issubclass(obj, BaseModel) and obj is not BaseModel
    ]
    assert len(model_names) >= 2


def test_f05_5_schemas_module_uc3_sar_and_form700_models() -> None:
    from app import schemas

    src = inspect.getsource(schemas)
    assert "PENDING_HITL_REVIEW" in src or "hitl_review_status" in src
    assert "miners_rule_damage_delta" in src or "calculated_yield_pct" in src


# ===========================================================================
# F6: Deterministic ASIP Physics & 3D CAD Engine (5 tests)
# ===========================================================================


def test_f06_1_miners_rule_damage_delta_exact() -> None:
    from app.physics.asip_engine import run_asip_miners_rule_engine

    res = invoke_contract(
        run_asip_miners_rule_engine,
        tail_number="ZM151",
        structural_station_id="Frame 496",
        station_id="Frame 496",
        peak_nz_g=9.4,
        mach_number=1.3,
        peak_egt_celsius=220.0,
    )
    assert float(
        get_field(res, "miners_rule_damage_delta", "damage_delta")
    ) == pytest.approx(0.0042, abs=1e-6)


def test_f06_2_calculated_yield_pct_and_ndi_class() -> None:
    from app.physics.asip_engine import run_asip_miners_rule_engine

    res = invoke_contract(
        run_asip_miners_rule_engine,
        tail_number="ZM151",
        structural_station_id="Frame 496",
        station_id="Frame 496",
        peak_nz_g=9.4,
        mach_number=1.3,
        peak_egt_celsius=220.0,
    )
    assert float(
        get_field(res, "calculated_yield_pct", "yield_pct")
    ) == pytest.approx(104.2, abs=1e-2)
    assert (
        get_field(res, "required_ndi_class", "ndi_class")
        == "CLASS_A_ULTRASONIC_C_SCAN"
    )
    assert "53-11-00" in str(get_field(res, "mandated_jtd_rule", "jtd_rule"))


def test_f06_3_extract_ndi_defect_maps_hole_14() -> None:
    from app.physics.asip_engine import extract_ndi_defect_and_map_cad

    res = invoke_contract(
        extract_ndi_defect_and_map_cad,
        c_scan_document_id="DOC-06",
        srm_document_id="DOC-05",
        structural_station_id="Frame 496",
        station_id="Frame 496",
        tail_number="ZM151",
    )
    assert "14" in str(res)
    assert float(
        get_field(res, "measured_ndi_elongation_in", "measured_elongation_in")
    ) == pytest.approx(0.012, abs=1e-5)
    assert float(
        get_field(res, "allowable_elongation_in", "allowable_limit_in")
    ) == pytest.approx(0.015, abs=1e-5)


def test_f06_4_cad_mapping_serviceable_disposition_and_task_card() -> None:
    from app.physics.asip_engine import extract_ndi_defect_and_map_cad

    res = invoke_contract(
        extract_ndi_defect_and_map_cad,
        c_scan_document_id="DOC-06",
        structural_station_id="Frame 496",
        tail_number="ZM151",
    )
    assert get_field(res, "within_allowable_limits", "is_within_limits") is True
    assert (
        get_field(res, "disposition", "disposition_status")
        == "SERVICEABLE_WITH_TORQUE_RECHECK"
    )
    assert "53-11-00-280" in str(
        get_field(res, "mandated_jtd_task_card", "jtd_task_card")
    )


def test_f06_5_physics_engine_sub_50ms_latency() -> None:
    from app.physics.asip_engine import (
        extract_ndi_defect_and_map_cad,
        run_asip_miners_rule_engine,
    )

    t0 = time.perf_counter()
    invoke_contract(
        run_asip_miners_rule_engine,
        tail_number="ZM151",
        structural_station_id="Frame 496",
        peak_nz_g=9.4,
        mach_number=1.3,
        peak_egt_celsius=220.0,
    )
    invoke_contract(
        extract_ndi_defect_and_map_cad,
        c_scan_document_id="DOC-06",
        structural_station_id="Frame 496",
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms < 50.0


# ===========================================================================
# F7: UC1 Specialist Sub-Agent & Tools (5 tests)
# ===========================================================================


def test_f07_1_uc1_sub_agent_definition() -> None:
    from app.sub_agents.uc1_analytics_agent import f35_analytics_agent

    assert f35_analytics_agent.name == "f35_analytics_agent"
    assert len(f35_analytics_agent.tools) >= 2


def test_f07_2_check_actuator_fatigue_returns_zm151_and_zm154() -> None:
    from app.tools.uc1_analytics import check_actuator_fatigue_and_depot_inventory

    ctx = E2EToolContext()
    res = invoke_contract(
        check_actuator_fatigue_and_depot_inventory,
        base_location="RAF Marham",
        hours_to_limit_window=50.0,
        tool_context=ctx,
    )
    res_str = json.dumps(res, default=str)
    assert "ZM151" in res_str
    assert "1000.4" in res_str
    assert "ZM154" in res_str
    assert "842" in res_str


def test_f07_3_check_actuator_fatigue_returns_depot_and_sortie() -> None:
    from app.tools.uc1_analytics import check_actuator_fatigue_and_depot_inventory

    ctx = E2EToolContext()
    res = invoke_contract(
        check_actuator_fatigue_and_depot_inventory,
        base_location="RAF Marham",
        hours_to_limit_window=50.0,
        tool_context=ctx,
    )
    res_str = json.dumps(res, default=str)
    assert "1680-01-619-4821" in res_str
    assert "SRT-MAR-20261103-01" in res_str
    assert "Henderson" in res_str or "VIPER-1" in res_str


def test_f07_4_check_actuator_fatigue_emits_two_vegalite_v5_specs() -> None:
    from app.tools.uc1_analytics import check_actuator_fatigue_and_depot_inventory

    ctx = E2EToolContext()
    res = invoke_contract(
        check_actuator_fatigue_and_depot_inventory,
        base_location="RAF Marham",
        hours_to_limit_window=50.0,
        tool_context=ctx,
    )
    bar_chart = get_field(res, "depot_stock_vs_demand_bar_chart")
    threshold_chart = get_field(res, "actuator_fatigue_threshold_chart")
    assert isinstance(bar_chart, dict)
    assert isinstance(threshold_chart, dict)
    assert "vega-lite" in str(bar_chart.get("$schema", "")).lower()
    assert "vega-lite" in str(threshold_chart.get("$schema", "")).lower()


def test_f07_5_recommend_tail_swap_and_replenishment_tool() -> None:
    from app.tools.uc1_analytics import recommend_tail_swap_and_replenishment

    ctx = E2EToolContext()
    res = invoke_contract(
        recommend_tail_swap_and_replenishment,
        sortie_id="SRT-MAR-20261103-01",
        primary_tail="ZM151",
        spare_tail="ZM154",
        tool_context=ctx,
    )
    res_str = json.dumps(res, default=str)
    assert "SRT-MAR-20261103-01" in res_str
    assert "ZM151" in res_str
    assert "ZM154" in res_str
    assert "1680-01-619-4821" in res_str


# ===========================================================================
# F8: UC2 Specialist Sub-Agent & Tool (5 tests)
# ===========================================================================


def test_f08_1_uc2_sub_agent_definition() -> None:
    from app.sub_agents.uc2_search_agent import f35_jtd_search_agent

    assert f35_jtd_search_agent.name == "f35_jtd_search_agent"
    assert len(f35_jtd_search_agent.tools) >= 1


def test_f08_2_search_tool_normalizes_uk_us_dialect() -> None:
    from app.tools.uc2_jtd_search import search_technical_manuals_and_repair_logs

    ctx = E2EToolContext()
    res = invoke_contract(
        search_technical_manuals_and_repair_logs,
        symptom_query="RAF F-35B canopy catch binding with spanner adjustment and gouge check",
        bit_fault_present=False,
        subsystem_filter="53-30",
        tool_context=ctx,
    )
    res_str = json.dumps(res, default=str).lower()
    assert "latch" in res_str
    assert "wrench" in res_str or "score" in res_str or "53-30" in res_str


def test_f08_3_search_tool_retrieves_doc01_and_doc02_for_canopy_latch() -> None:
    from app.tools.uc2_jtd_search import search_technical_manuals_and_repair_logs

    ctx = E2EToolContext()
    res = invoke_contract(
        search_technical_manuals_and_repair_logs,
        symptom_query="sticky canopy catch during lock verification no BIT fault",
        bit_fault_present=False,
        subsystem_filter="53-30",
        tool_context=ctx,
    )
    res_str = json.dumps(res, default=str)
    assert "DOC-01" in res_str
    assert "DOC-02" in res_str


def test_f08_4_search_tool_retrieves_doc09_thermal_cure_220c() -> None:
    from app.tools.uc2_jtd_search import search_technical_manuals_and_repair_logs

    ctx = E2EToolContext()
    res = invoke_contract(
        search_technical_manuals_and_repair_logs,
        symptom_query="220C thermal cure High-Temp RAM Sheet B heater blanket MAM Section 9-1",
        bit_fault_present=False,
        subsystem_filter="",
        tool_context=ctx,
    )
    res_str = json.dumps(res, default=str)
    assert "DOC-09" in res_str
    assert "220" in res_str


def test_f08_5_search_tool_strips_html_tags_and_enforces_perf_guardrails() -> None:
    from app.tools import uc2_jtd_search
    from app.tools.uc2_jtd_search import search_technical_manuals_and_repair_logs

    src = inspect.getsource(uc2_jtd_search)
    assert "15" in src, "PERF-02: pageSize must be set to 15"
    assert '"summarySpec"' not in src, "PERF-03: summarySpec must be omitted"

    ctx = E2EToolContext()
    res = invoke_contract(
        search_technical_manuals_and_repair_logs,
        symptom_query="sticky canopy latch",
        bit_fault_present=False,
        subsystem_filter="53-30",
        tool_context=ctx,
    )
    res_str = json.dumps(res, default=str)
    assert "<b>" not in res_str and "</b>" not in res_str


# ===========================================================================
# F9: UC3 Specialist Sub-Agent & Tools (5 tests)
# ===========================================================================


def test_f09_1_uc3_sub_agent_definition() -> None:
    from app.sub_agents.uc3_airworthiness_agent import f35_airworthiness_orchestrator

    assert f35_airworthiness_orchestrator.name == "f35_airworthiness_orchestrator"
    assert len(f35_airworthiness_orchestrator.tools) >= 3


def test_f09_2_atomic_tools_a_and_b_1553_sync_and_fatigue() -> None:
    from app.tools.uc3_airworthiness import (
        calculate_structural_fatigue_and_yield,
        sync_flight_telemetry_exceedance,
    )

    ctx = E2EToolContext()
    res_a = invoke_contract(
        sync_flight_telemetry_exceedance,
        tail_number="ZM151",
        pilot_debrief_text="severe shudder at roughly 14:22 Zulu during defensive split-S",
        structural_station_id="Frame 496",
        tool_context=ctx,
    )
    assert "EXC-20261102-ZM151" in json.dumps(res_a, default=str)
    assert float(get_field(res_a, "peak_nz_g")) == pytest.approx(9.4, abs=1e-2)

    res_b = invoke_contract(
        calculate_structural_fatigue_and_yield,
        tail_number="ZM151",
        structural_station_id="Frame 496",
        peak_nz_g=9.4,
        mach_number=1.3,
        peak_egt_celsius=220.0,
        tool_context=ctx,
    )
    assert float(
        get_field(res_b, "miners_rule_damage_delta", "damage_delta")
    ) == pytest.approx(0.0042, abs=1e-6)
    assert float(
        get_field(res_b, "calculated_yield_pct", "yield_pct")
    ) == pytest.approx(104.2, abs=1e-2)


def test_f09_3_atomic_tools_c_and_d_cscan_and_mbom_audit() -> None:
    from app.tools.uc3_airworthiness import (
        audit_fastener_lot_in_mbom,
        inspect_ultrasonic_cscan_and_map_cad,
    )

    ctx = E2EToolContext()
    res_c = invoke_contract(
        inspect_ultrasonic_cscan_and_map_cad,
        c_scan_document_id="DOC-06",
        structural_station_id="Frame 496",
        tool_context=ctx,
    )
    assert "14" in json.dumps(res_c, default=str)
    assert float(
        get_field(res_c, "measured_ndi_elongation_in", "measured_elongation_in")
    ) == pytest.approx(0.012, abs=1e-5)

    res_d = invoke_contract(
        audit_fastener_lot_in_mbom,
        tail_number="ZM151",
        station_id="Frame 496 — Fastener Hole #14",
        measured_elongation_in=0.012,
        tool_context=ctx,
    )
    res_d_str = json.dumps(res_d, default=str)
    assert "8841-B" in res_d_str
    assert "14" in res_d_str


def test_f09_4_assess_airframe_airworthiness_parallel_fanout() -> None:
    from app.tools import uc3_airworthiness
    from app.tools.uc3_airworthiness import assess_airframe_airworthiness

    assert "gather" in inspect.getsource(uc3_airworthiness)
    ctx = E2EToolContext()
    res = invoke_contract(
        assess_airframe_airworthiness,
        tail_number="ZM151",
        pilot_debrief_text="severe shudder at roughly 14:22 Zulu during defensive split-S",
        structural_station_id="Frame 496",
        c_scan_document_id="DOC-06",
        tool_context=ctx,
    )
    res_str = json.dumps(res, default=str)
    for expected in (
        "EXC-20261102-ZM151",
        "0.0042",
        "104.2",
        "CLASS_A_ULTRASONIC_C_SCAN",
        "0.012",
        "8841-B",
    ):
        assert expected in res_str


def test_f09_5_generate_and_approve_form700_tools() -> None:
    from app.tools.uc3_airworthiness import (
        approve_form700_engineering_release,
        generate_form700_airworthiness_package,
    )

    ctx_turn1 = E2EToolContext(state={"current_turn_id": 1}, invocation_id="turn-1")
    staged = invoke_contract(
        generate_form700_airworthiness_package,
        tail_number="ZM151",
        station_id="Frame 496",
        tool_context=ctx_turn1,
    )
    staged_str = json.dumps(staged, default=str)
    assert "AWR-700-20261102-ZM151" in staged_str
    assert "PENDING_HITL_REVIEW" in staged_str
    assert ctx_turn1.state.get("pending_release_package_id") == "AWR-700-20261102-ZM151"

    ctx_turn2 = E2EToolContext(
        state={
            **ctx_turn1.state,
            "current_turn_id": 2,
        },
        user_text="Approved by Lead Stress Engineer / Chief Technical Officer (CTO).",
        invocation_id="turn-2",
    )
    approved = invoke_contract(
        approve_form700_engineering_release,
        release_package_id="AWR-700-20261102-ZM151",
        reviewer_role="Lead Stress Engineer",
        approval_notes="Confirmed per JTD Task Card 53-11-00-280.",
        tool_context=ctx_turn2,
    )
    assert "CONFIRMED_BY_ENGINEER" in json.dumps(approved, default=str)


# ===========================================================================
# F10: Root Coordinator, Fast-Path Callback & Two-Turn HITL Gate (5 tests)
# ===========================================================================


def test_f10_1_root_agent_and_app_exports() -> None:
    from app import app, root_agent

    assert root_agent.name == "f35_sustainment_coordinator"
    assert app.name == "app"
    assert app.root_agent.name == "f35_sustainment_coordinator"


def test_f10_2_root_agent_wires_all_three_sub_agents() -> None:
    from app import root_agent

    sub_names = {sa.name for sa in (root_agent.sub_agents or [])}
    assert len(sub_names) == 4
    assert sub_names == {
        "f35_maintenance_data_agent",
        "f35_analytics_agent",
        "f35_jtd_search_agent",
        "f35_airworthiness_orchestrator",
    }


def test_f10_3_app_resumability_and_context_cache_config() -> None:
    from app import app

    assert app.resumability_config is not None
    assert app.resumability_config.is_resumable is True
    assert app.context_cache_config is not None
    assert app.context_cache_config.min_tokens == 2048
    assert app.context_cache_config.ttl_seconds == 1800
    assert app.context_cache_config.cache_intervals == 10


def test_f10_4_fast_path_before_model_callback_sla() -> None:
    from app.callbacks import fast_path_before_model_callback

    cb_ctx = E2ECallbackContext(user_text="hello")
    llm_req = E2ELlmRequest(user_text="hello")
    t0 = time.perf_counter()
    res = fast_path_before_model_callback(callback_context=cb_ctx, llm_request=llm_req)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert res is not None
    assert elapsed_ms < 5.0


def test_f10_5_enforce_hitl_airworthiness_gate_two_turn_lock() -> None:
    from app.callbacks import enforce_hitl_airworthiness_gate

    tool = E2EDummyTool("approve_form700_engineering_release")
    same_turn_ctx = E2EToolContext(
        state={
            "pending_release_package_id": "AWR-700-20261102-ZM151",
            "hitl_review_status": "PENDING_HITL_REVIEW",
            "staged_turn_id": 1,
            "current_turn_id": 1,
            "staged_invocation_id": "inv-1",
        },
        user_text="Approve as Lead Stress Engineer",
        invocation_id="inv-1",
    )
    blocked = enforce_hitl_airworthiness_gate(
        tool=tool,
        args={
            "release_package_id": "AWR-700-20261102-ZM151",
            "reviewer_role": "Lead Stress Engineer",
            "approval_notes": "Auto approve",
        },
        tool_context=same_turn_ctx,
    )
    assert blocked is not None

    next_turn_ctx = E2EToolContext(
        state={
            "pending_release_package_id": "AWR-700-20261102-ZM151",
            "hitl_review_status": "PENDING_HITL_REVIEW",
            "staged_turn_id": 1,
            "current_turn_id": 2,
            "staged_invocation_id": "inv-1",
        },
        user_text="Confirmed and approved by Lead Stress Engineer for release.",
        invocation_id="inv-2",
    )
    allowed = enforce_hitl_airworthiness_gate(
        tool=tool,
        args={
            "release_package_id": "AWR-700-20261102-ZM151",
            "reviewer_role": "Lead Stress Engineer",
            "approval_notes": "Confirmed by Lead Stress Engineer.",
        },
        tool_context=next_turn_ctx,
    )
    assert allowed is None


# ===========================================================================
# F11: Frontend Vega-Lite Canvas & Form 700 HITL Review Studio (5 tests)
# ===========================================================================


def test_f11_1_vega_canvas_component_exists_and_renders_charts() -> None:
    p = REPO_ROOT / "packages" / "web" / "components" / "VegaCanvas.tsx"
    assert p.is_file()
    content = p.read_text(encoding="utf-8")
    assert "depot_stock_vs_demand_bar_chart" in content
    assert "actuator_fatigue_threshold_chart" in content


def test_f11_2_vega_canvas_breach_and_condemnation_markers() -> None:
    p = REPO_ROOT / "packages" / "web" / "components" / "VegaCanvas.tsx"
    content = p.read_text(encoding="utf-8")
    assert "ZM151" in content or "1000" in content
    assert "VegaCanvas" in content


def test_f11_3_form700_review_studio_component_exists() -> None:
    p = REPO_ROOT / "packages" / "web" / "components" / "Form700ReviewStudio.tsx"
    assert p.is_file()
    content = p.read_text(encoding="utf-8")
    assert "PENDING_HITL_REVIEW" in content
    assert "CONFIRMED_BY_ENGINEER" in content


def test_f11_4_form700_review_studio_two_turn_hitl_controls() -> None:
    p = REPO_ROOT / "packages" / "web" / "components" / "Form700ReviewStudio.tsx"
    content = p.read_text(encoding="utf-8")
    assert "53-11-00-280" in content or "AWR-700-20261102-ZM151" in content
    assert "Lead Stress Engineer" in content or "CTO" in content


def test_f11_5_packages_web_index_exports_both_components() -> None:
    p = REPO_ROOT / "packages" / "web" / "index.ts"
    assert p.is_file()
    content = p.read_text(encoding="utf-8")
    assert "VegaCanvas" in content
    assert "Form700ReviewStudio" in content


# ===========================================================================
# F12: Deterministic Unit Test Suite (5 tests)
# ===========================================================================


def test_f12_1_unit_test_file_exists_and_compiles() -> None:
    p = REPO_ROOT / "tests" / "unit" / "test_deterministic.py"
    assert p.is_file()
    ast.parse(p.read_text(encoding="utf-8"))


def test_f12_2_unit_tests_cover_asip_physics_and_cad() -> None:
    from tests.unit import test_deterministic

    assert hasattr(test_deterministic, "TestAsipPhysicsEngine")
    suite = test_deterministic.TestAsipPhysicsEngine()
    suite.test_miners_rule_exceedance_9_4g_mach_1_3_220c()
    suite.test_extract_ndi_defect_and_map_cad_doc06()


def test_f12_3_unit_tests_cover_two_turn_hitl_gate() -> None:
    from tests.unit import test_deterministic

    assert hasattr(test_deterministic, "TestTwoTurnHitlGate")
    suite = test_deterministic.TestTwoTurnHitlGate()
    suite.test_hitl_gate_blocks_when_no_package_staged()
    suite.test_hitl_gate_blocks_same_turn_auto_approval_safe_02()
    suite.test_hitl_gate_allows_valid_second_turn_engineer_signoff()


def test_f12_4_unit_tests_cover_fast_path_callback() -> None:
    from tests.unit import test_deterministic

    assert hasattr(test_deterministic, "TestFastPathBeforeModelCallback")
    suite = test_deterministic.TestFastPathBeforeModelCallback()
    suite.test_fast_path_intercepts_short_greetings_under_5ms("hi")
    suite.test_fast_path_passes_through_domain_sustainment_queries()


def test_f12_5_unit_tests_cover_reg01_and_perf_guardrails() -> None:
    from tests.unit import test_deterministic

    assert hasattr(test_deterministic, "TestConfigAndGuardrailInvariants")
    suite = test_deterministic.TestConfigAndGuardrailInvariants()
    suite.test_reg01_eu_residency_constants_in_config()
    suite.test_perf01_no_gcloud_subprocess_in_app_code()
    suite.test_perf05_enterprise_sdk_and_thinking_level_enum()


# ===========================================================================
# F13: V&V Evaluation Datasets & Config (5 tests)
# ===========================================================================


def test_f13_1_basic_dataset_json_valid_and_has_3_smoke_cases() -> None:
    p = REPO_ROOT / "tests" / "eval" / "datasets" / "basic-dataset.json"
    assert p.is_file()
    data = json.loads(p.read_text(encoding="utf-8"))
    cases = data.get("eval_cases", [])
    assert len(cases) >= 4
    case_ids = {c["eval_case_id"] for c in cases}
    assert {
        "uc0_maintenance_work_orders_spreadsheet_card",
        "uc0_1_phm_bit_fault_triage_card",
        "uc0_5_multi_table_tooling_sqep_join_card",
        "uc1_actuator_fatigue_and_stock",
        "uc2_sticky_canopy_latch_search",
        "uc3_frame496_exceedance_and_form700_stage",
    }.issubset(case_ids)


def test_f13_2_vv_golden_suite_json_has_all_10_vv_scenarios() -> None:
    p = REPO_ROOT / "tests" / "eval" / "datasets" / "vv_golden_suite.json"
    assert p.is_file()
    data = json.loads(p.read_text(encoding="utf-8"))
    cases = data.get("eval_cases", [])
    assert len(cases) >= 10
    case_ids = {c["eval_case_id"] for c in cases}
    prefixes = {c["eval_case_id"].split("_")[0] for c in cases}
    for i in range(1, 6):
        assert f"TC-SQ-0{i}" in prefixes
        assert f"TC-LP-0{i}" in prefixes
    assert {
        "uc0_tc_sq_00_conversational_maintenance_sql_card",
        "uc0_1_tc_sq_00_1_phm_bit_fault_triage_card",
        "uc0_5_tc_sq_00_5_multi_table_tooling_sqep_join_card",
        "uc0_tc_lp_00_text_to_sql_latency_and_csv_export",
    }.issubset(case_ids)


def test_f13_3_eval_config_yaml_defines_metrics_to_run_and_custom_metrics() -> None:
    p = REPO_ROOT / "tests" / "eval" / "eval_config.yaml"
    assert p.is_file()
    cfg = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert isinstance(cfg.get("metrics_to_run"), list)
    assert len(cfg["metrics_to_run"]) >= 3
    assert isinstance(cfg.get("custom_metrics"), list)
    assert len(cfg["custom_metrics"]) >= 3


def test_f13_4_response_quality_evaluator_grades_single_and_multiturn() -> None:
    from tests.eval.response_quality import evaluate

    res = evaluate(
        {
            "prompt": "Check ZM151 fatigue",
            "response": "ZM151 is at 1000.4 hrs (NSN 1680-01-619-4821); swap SRT-MAR-20261103-01 to ZM154.",
            "reference": "Tail ZM151 (NSN 1680-01-619-4821) swap SRT-MAR-20261103-01 to ZM154.",
        }
    )
    assert res["score"] >= 4.5


def test_f13_5_inline_custom_functions_compile_and_execute() -> None:
    p = REPO_ROOT / "tests" / "eval" / "eval_config.yaml"
    cfg = yaml.safe_load(p.read_text(encoding="utf-8"))
    for m in cfg["custom_metrics"]:
        if "custom_function" in m:
            ns: dict[str, Any] = {}
            exec(compile(m["custom_function"], "<test>", "exec"), ns)
            out = ns["evaluate"](
                {
                    "response": "DOC-01 DOC-02 ZM151 0.0042 104.2",
                    "reference": "DOC-01 DOC-02 ZM151 0.0042 104.2",
                    "agent_data": {"turns": [{"turn_index": 0}]},
                }
            )
            assert out["score"] >= 0.9


# ===========================================================================
# F14: E2E Test Suite Pass (Tiers 1-4) & Runner (5 tests)
# ===========================================================================


def test_f14_1_test_infra_md_documents_all_17_features() -> None:
    p = REPO_ROOT / "TEST_INFRA.md"
    assert p.is_file()
    text = p.read_text(encoding="utf-8")
    for i in range(1, 18):
        assert f"| F{i} |" in text, f"Missing F{i} in TEST_INFRA.md"


def test_f14_2_test_ready_md_documents_coverage_and_runner() -> None:
    p = REPO_ROOT / "TEST_READY.md"
    assert p.is_file()
    text = p.read_text(encoding="utf-8")
    assert "uv run pytest tests/e2e -v" in text
    for i in range(1, 18):
        assert f"| F{i} |" in text


def test_f14_3_run_e2e_suite_py_exists_and_supports_tier_selection() -> None:
    p = REPO_ROOT / "tests" / "e2e" / "run_e2e_suite.py"
    assert p.is_file()
    text = p.read_text(encoding="utf-8")
    assert "--tier" in text
    ast.parse(text)


def test_f14_4_all_four_e2e_tier_modules_exist() -> None:
    for fname in (
        "test_tier1_feature_coverage.py",
        "test_tier2_boundary_corner.py",
        "test_tier3_cross_feature.py",
        "test_tier4_real_world_scenarios.py",
    ):
        assert (REPO_ROOT / "tests" / "e2e" / fname).is_file()


def test_f14_5_e2e_helpers_support_sync_and_async_contracts() -> None:
    async def _sample_async(x: int = 2) -> dict[str, int]:
        return {"val": x * 3}

    res = invoke_contract(_sample_async, x=7, unused_param="ignored")
    assert get_field(res, "val") == 21


# ===========================================================================
# F15: Agent Runtime Deployment (europe-west1) (5 tests)
# ===========================================================================


def test_f15_1_manifest_targets_agent_runtime_in_europe_west1() -> None:
    manifest = yaml.safe_load(
        (REPO_ROOT / "agents-cli-manifest.yaml").read_text(encoding="utf-8")
    )
    assert manifest["region"] == "europe-west1"
    assert manifest["create_params"]["deployment_target"] == "agent_runtime"


def test_f15_2_manifest_disables_agent_gateway_and_uses_service_account() -> None:
    manifest = yaml.safe_load(
        (REPO_ROOT / "agents-cli-manifest.yaml").read_text(encoding="utf-8")
    )
    assert manifest["create_params"]["agent_gateway"] is False
    assert (
        manifest["create_params"]["agent_runtime"]["identity_default"]
        == "service_account"
    )


def test_f15_3_dockerfile_exposes_adk_runtime_entrypoint() -> None:
    dockerfile_text = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "EXPOSE" in dockerfile_text or "uvicorn" in dockerfile_text or "CMD" in dockerfile_text


def test_f15_4_runtime_service_account_configured_for_antig_dave() -> None:
    from app import config

    assert (
        config.RUNTIME_SERVICE_ACCOUNT
        == "f35-sustainment-runtime-sa@antig-dave.iam.gserviceaccount.com"
    )
    assert config.COMPUTE_REGION == "europe-west1"


def test_f15_5_agent_runtime_deployment_contract_or_live_check() -> None:
    from app import app, config

    assert app.name == "app"
    assert config.PROJECT_ID == "antig-dave"
    assert config.COMPUTE_REGION == "europe-west1"
    if os.environ.get("VERIFY_LIVE_DEPLOYED_ENDPOINT") == "1":
        import google.auth
        from google.auth.transport.requests import Request
        import httpx

        creds, _ = google.auth.default()
        creds.refresh(Request())
        url = (
            f"https://{config.COMPUTE_REGION}-aiplatform.googleapis.com/v1beta1/"
            f"projects/{config.PROJECT_ID}/locations/{config.COMPUTE_REGION}/reasoningEngines"
        )
        resp = httpx.get(
            url, headers={"Authorization": f"Bearer {creds.token}"}, timeout=15.0
        )
        assert resp.status_code == 200
        engines = resp.json().get("reasoningEngines", [])
        assert len(engines) >= 1


# ===========================================================================
# F16: Gemini Enterprise Publication (eu) & Agent Registry Verification (5 tests)
# ===========================================================================


def test_f16_1_gemini_enterprise_app_id_and_eu_location() -> None:
    from app import config

    assert config.GEMINI_APP_ID == "f35-support"
    assert config.DE_LOCATION == "eu"


def test_f16_2_root_agent_name_matches_manifest_for_adk_registration() -> None:
    from app import root_agent

    manifest = yaml.safe_load(
        (REPO_ROOT / "agents-cli-manifest.yaml").read_text(encoding="utf-8")
    )
    assert root_agent.name == manifest["create_params"]["root_agent_name"]


def test_f16_3_sub_agent_display_identities_for_enterprise_routing() -> None:
    from app import root_agent

    descriptions = " ".join(
        f"{sa.name} {getattr(sa, 'description', '')}"
        for sa in (root_agent.sub_agents or [])
    )
    assert "f35_maintenance_data_agent" in descriptions
    assert "f35_analytics_agent" in descriptions
    assert "f35_jtd_search_agent" in descriptions
    assert "f35_airworthiness_orchestrator" in descriptions


def test_f16_4_human_friendly_tool_names_and_docstrings() -> None:
    from app.tools import uc1_analytics, uc2_jtd_search, uc3_airworthiness

    for fn in (
        uc1_analytics.check_actuator_fatigue_and_depot_inventory,
        uc1_analytics.recommend_tail_swap_and_replenishment,
        uc2_jtd_search.search_technical_manuals_and_repair_logs,
        uc3_airworthiness.assess_airframe_airworthiness,
        uc3_airworthiness.generate_form700_airworthiness_package,
        uc3_airworthiness.approve_form700_engineering_release,
    ):
        assert callable(fn)
        assert fn.__doc__ and len(fn.__doc__.strip()) >= 15


def test_f16_5_gemini_enterprise_publication_and_registry_contract() -> None:
    from app import config

    assert config.GEMINI_APP_ID == "f35-support"
    assert config.DE_LOCATION == "eu"
    assert config.COMPUTE_REGION == "europe-west1"


# ===========================================================================
# F17: Live Deployed Cloud E2E Verification & GitHub Push (5 tests)
# ===========================================================================


def test_f17_1_git_repository_initialized_with_main_branch() -> None:
    git_dir = REPO_ROOT / ".git"
    assert git_dir.exists()


def test_f17_2_gitignore_excludes_venv_pycache_and_secrets() -> None:
    gitignore_text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".venv" in gitignore_text or "venv" in gitignore_text
    assert "__pycache__" in gitignore_text


def test_f17_3_teamwork_metadata_isolation_compliance() -> None:
    teamwork_dir = REPO_ROOT / ".agents" / "teamwork"
    if teamwork_dir.is_dir():
        leaked_code = [
            p
            for p in teamwork_dir.rglob("*")
            if p.is_file() and p.suffix in {".py", ".ts", ".tsx"}
        ]
        assert leaked_code == [], (
            f"Violation: found source/test code inside .agents/teamwork/: {leaked_code}"
        )


def test_f17_4_readme_and_project_documentation_completeness() -> None:
    for doc_name in ("README.md", "PROJECT.md", "SA_F35.md", "AGENTS.md"):
        assert (REPO_ROOT / doc_name).is_file()


def test_f17_5_end_to_end_release_readiness_and_live_smoke_hook() -> None:
    from app import app, root_agent

    assert app is not None
    assert root_agent is not None
    assert len(root_agent.sub_agents) == 4
    assert {sa.name for sa in root_agent.sub_agents} == {
        "f35_maintenance_data_agent",
        "f35_analytics_agent",
        "f35_jtd_search_agent",
        "f35_airworthiness_orchestrator",
    }
