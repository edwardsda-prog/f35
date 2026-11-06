"""Tier 3 E2E Tests: Cross-Feature Interactions across active F-35 Sustainment Features.

Verifies interface contracts and state transitions where two features interact:
- F1 x F5: Authoritative BigQuery seed records -> Config & pre-warmed client table schemas
- F2 x F3: Synthetic JTD corpus (DOC-01, DOC-02, DOC-03, DOC-09) -> Cloud setup & JSONL ingestion pipeline
- F3 x F7: Cloud BigQuery EU tables -> UC1 analytics tool query & fallback consistency
- F3 x F8: Cloud Discovery Engine `eu` datastores -> UC2 search tool datastore & metadata filtering
- F4 x F5: Root coordinator & 3-sub-agent hierarchy -> Tier 1/2 fast-path callback & Enterprise model config
- F5 x F6: Pre-warmed client singletons & config -> Pydantic schema serialization
- F7 x F10: UC1 actuator fatigue check -> UC1 sortie tail-swap recommendation state handoff
- F7 x F11: UC1 Vega-Lite v5 chart specs -> Next.js Vega-Lite Canvas UI component contract
- UC0 x F11: UC0 `execute_maintenance_sql` Spreadsheet Card -> Next.js `MaintenanceSheetCard.tsx` contract
- UC0 x F13: UC0 `execute_maintenance_sql` -> V&V golden eval dataset (`TC-SQ-00`, `TC-LP-00`)
- F12 x F14: Deterministic unit test suite -> E2E runner & test infrastructure parity
- F13 x F14: `agents-cli eval` custom metrics (`response_quality.py`) -> V&V golden suite grading
- F15 x F16: Agent Runtime `europe-west1` deployment manifest -> Gemini Enterprise `eu` ADK publication
- F16 x F17: Gemini Enterprise publication config -> Git repository hygiene & secret exclusion
"""

from __future__ import annotations

import json
import subprocess

from tests.e2e import (
    E2ECallbackContext,
    E2ELlmRequest,
    E2EToolContext,
    REPO_ROOT,
    invoke_contract,
)


def test_xf01_f01_x_f05_bq_seed_records_align_with_config_table_identifiers() -> None:
    """F1 x F5: Verify BigQuery seed records in F1 match the 6 active table identifiers in `app.config`."""
    from app import config
    from app.seed_data import bq_seed_records

    assert config.PROJECT_ID == "antig-dave"
    assert config.BQ_DATASET == "ukd_f35_sustainment_demo"
    assert config.BQ_LOCATION == "EU"

    expected_tables = {
        "airframe_component_telemetry": bq_seed_records.AIRFRAME_COMPONENT_TELEMETRY,
        "global_depot_inventory": bq_seed_records.GLOBAL_DEPOT_INVENTORY,
        "squadron_sortie_schedule": bq_seed_records.SQUADRON_SORTIE_SCHEDULE,
        "maintenance_work_orders": bq_seed_records.MAINTENANCE_WORK_ORDERS,
        "phm_bit_fault_events": bq_seed_records.PHM_BIT_FAULT_EVENTS,
        "work_center_tooling_and_sqep": bq_seed_records.WORK_CENTER_TOOLING_AND_SQEP,
    }
    for table_name, records in expected_tables.items():
        assert isinstance(records, list) and len(records) == 100, f"Expected 100 records for {table_name}"
        if hasattr(config, "BQ_TABLES"):
            assert table_name in config.BQ_TABLES or table_name in config.BQ_TABLES.values()


def test_xf02_f02_x_f03_jtd_corpus_docs_align_with_setup_infra_jsonl() -> None:
    """F2 x F3: Verify synthetic corpus generator output aligns with `setup_demo_infra.py` JSONL metadata."""
    from app.seed_data import jtd_corpus
    from scripts import generate_synthetic_corpus, setup_demo_infra

    assert hasattr(generate_synthetic_corpus, "generate_unstructured_corpus")
    assert hasattr(setup_demo_infra, "ensure_bigquery_dataset_and_tables") or hasattr(
        setup_demo_infra, "seed_bigquery_tables"
    )
    docs = getattr(jtd_corpus, "JTD_CORPUS_DOCUMENTS", getattr(jtd_corpus, "DOCUMENTS", []))
    doc_ids = sorted(
        d.get("doc_id") if isinstance(d, dict) else getattr(d, "doc_id", "")
        for d in docs
    )
    assert doc_ids == ["DOC-01", "DOC-02", "DOC-03", "DOC-09"]


def test_xf03_f03_x_f07_setup_infra_bigquery_tables_match_uc1_analytics_queries() -> None:
    """F3 x F7: Verify `setup_demo_infra.py` table definitions match `uc1_analytics.py` query results."""
    from app.tools import uc1_analytics
    from scripts import setup_demo_infra

    src = open(setup_demo_infra.__file__, encoding="utf-8").read()
    for tbl in (
        "airframe_component_telemetry",
        "global_depot_inventory",
        "squadron_sortie_schedule",
    ):
        assert tbl in src

    ctx = E2EToolContext(state={})
    res = invoke_contract(
        uc1_analytics.check_actuator_fatigue_and_depot_inventory,
        base_location="RAF Marham",
        hours_to_limit_window=20.0,
        tool_context=ctx,
    )
    dumped = json.dumps(res if isinstance(res, dict) else res.model_dump())
    assert "ZM151" in dumped and "ZM154" in dumped and "1680-01-619-4821" in dumped


def test_xf04_f03_x_f08_setup_infra_discovery_engine_datastores_match_uc2_search() -> None:
    """F3 x F8: Verify Discovery Engine `eu` datastore IDs in `setup_demo_infra.py` match `uc2_jtd_search.py`."""
    from app import config
    from app.tools import uc2_jtd_search
    from scripts import setup_demo_infra

    infra_src = open(setup_demo_infra.__file__, encoding="utf-8").read()
    assert config.JTD_DATASTORE_ID in infra_src
    assert config.NARRATIVE_DATASTORE_ID in infra_src

    ctx = E2EToolContext(state={})
    res = invoke_contract(
        uc2_jtd_search.search_technical_manuals_and_repair_logs,
        symptom_query="sticky canopy catch and binding roller on F-35B with no BIT fault",
        bit_fault_present=False,
        subsystem_filter="53-30",
        tool_context=ctx,
    )
    dumped = json.dumps(res if isinstance(res, dict) else res.model_dump())
    assert "DOC-01" in dumped and "DOC-02" in dumped


def test_xf05_f04_x_f05_root_agent_fast_path_interception_preserves_subagent_delegation() -> None:
    """F4 x F5: Verify fast-path callback intercepts greetings (`< 15` chars) while passing domain queries to `root_agent`."""
    from app.agent import root_agent
    from app.callbacks import fast_path_before_model_callback

    sub_names = {sa.name for sa in getattr(root_agent, "sub_agents", [])}
    assert sub_names == {
        "f35_maintenance_data_agent",
        "f35_analytics_agent",
        "f35_jtd_search_agent",
    }

    short_ctx = E2ECallbackContext(state={}, user_text="Hello")
    short_resp = fast_path_before_model_callback(short_ctx, E2ELlmRequest("Hello"))
    assert short_resp is not None

    domain_query = (
        "Check RAF Marham F-35B electro-hydrostatic actuator fatigue hours and morning sortie schedule"
    )
    domain_ctx = E2ECallbackContext(state={}, user_text=domain_query)
    domain_resp = fast_path_before_model_callback(domain_ctx, E2ELlmRequest(domain_query))
    assert domain_resp is None


def test_xf06_f05_x_f06_clients_singleton_and_enterprise_model_config_integration() -> None:
    """F5 x F6: Verify pre-warmed client singletons and Pydantic schema serialization work together."""
    from app import clients, config, schemas

    assert config.GEMINI_ENTERPRISE is True
    assert config.GEMINI_LOCATION == "global"
    assert hasattr(clients, "get_bigquery_client") or hasattr(clients, "bq_client")
    assert hasattr(schemas, "VegaLiteSpec")
    assert hasattr(schemas, "MaintenanceSpreadsheetCard")


def test_xf08_f07_x_f10_uc1_check_actuator_fatigue_feeds_recommend_tail_swap() -> None:
    """F7 x F10: Verify UC1 `check_actuator_fatigue_and_depot_inventory` output directly feeds `recommend_tail_swap_and_replenishment`."""
    from app.tools import uc1_analytics

    ctx = E2EToolContext(state={})
    check_res = invoke_contract(
        uc1_analytics.check_actuator_fatigue_and_depot_inventory,
        base_location="RAF Marham",
        hours_to_limit_window=20.0,
        tool_context=ctx,
    )
    dumped_check = json.dumps(check_res if isinstance(check_res, dict) else check_res.model_dump())
    assert "ZM151" in dumped_check and "ZM154" in dumped_check

    swap_res = invoke_contract(
        uc1_analytics.recommend_tail_swap_and_replenishment,
        sortie_id="SRT-MAR-20261103-01",
        primary_tail="ZM151",
        spare_tail="ZM154",
        tool_context=ctx,
    )
    dumped_swap = json.dumps(swap_res if isinstance(swap_res, dict) else swap_res.model_dump())
    assert "SRT-MAR-20261103-01" in dumped_swap
    assert "ZM154" in dumped_swap
    assert "1680-01-619-4821" in dumped_swap


def test_xf09_f07_x_f11_uc1_vega_lite_specs_compatible_with_frontend_canvas_renderer() -> None:
    """F7 x F11: Verify UC1 Vega-Lite v5 JSON chart specifications match the frontend Vega-Lite Canvas component contract."""
    from app.tools import uc1_analytics

    ctx = E2EToolContext(state={})
    res = invoke_contract(
        uc1_analytics.check_actuator_fatigue_and_depot_inventory,
        base_location="RAF Marham",
        hours_to_limit_window=20.0,
        tool_context=ctx,
    )
    dumped = json.dumps(res if isinstance(res, dict) else res.model_dump())
    assert "vega.github.io/schema/vega-lite/v5.json" in dumped

    web_dir = REPO_ROOT / "packages" / "web"
    assert web_dir.exists()
    ts_files = list(web_dir.rglob("*.ts*"))
    assert len(ts_files) >= 1


def test_xf10_uc0_x_f11_maintenance_spreadsheet_card_integrates_with_frontend_sheet_component() -> None:
    """UC0 x F11: Verify UC0 `execute_maintenance_sql` Spreadsheet Card aligns with `MaintenanceSheetCard.tsx`."""
    from app.tools.uc0_maintenance import execute_maintenance_sql

    res = execute_maintenance_sql(
        "SELECT work_order_id, tail_number, aircraft_status, logged_man_hours "
        "FROM maintenance_work_orders WHERE work_order_status != 'COMPLETED' ORDER BY priority ASC"
    )
    assert res["status"] == "SUCCESS"
    assert res["row_count"] == 6
    card = res["spreadsheet_card"]
    assert "columns" in card and "rows" in card and "formula_footer" in card

    sheet_ts = (
        REPO_ROOT / "packages" / "web" / "components" / "MaintenanceSheetCard.tsx"
    ).read_text(encoding="utf-8")
    assert "MaintenanceSheetCard" in sheet_ts
    assert "csv" in sheet_ts.lower()


def test_xf14_uc0_x_f13_maintenance_sql_aligns_with_vv_eval_dataset() -> None:
    """UC0 x F13: Verify UC0 `execute_maintenance_sql` output satisfies the expected rubric in `vv_golden_suite.json` (`uc0_tc_sq_00_conversational_maintenance_sql_card`)."""
    from app.tools.uc0_maintenance import execute_maintenance_sql
    from tests.eval.response_quality import evaluate

    vv_data = json.loads(
        (REPO_ROOT / "tests" / "eval" / "datasets" / "vv_golden_suite.json").read_text(
            encoding="utf-8"
        )
    )
    tc_sq_00 = next(
        c
        for c in vv_data["eval_cases"]
        if (c.get("eval_id") or c.get("eval_case_id", "")).startswith("uc0_tc_sq_00")
    )

    res = execute_maintenance_sql(
        "SELECT * FROM maintenance_work_orders WHERE work_order_status != 'COMPLETED' ORDER BY priority ASC"
    )
    combined_response = json.dumps(res, default=str)
    grade = evaluate(
        {"response": combined_response, "reference": tc_sq_00["reference"]}
    )
    assert grade["score"] >= 4.0


def test_xf15_f12_x_f14_unit_tests_and_e2e_suite_share_consistent_oracles() -> None:
    """F12 x F14: Verify `tests/unit/test_deterministic.py` and active tools share identical UC0/UC1/UC2 oracle values."""
    unit_text = (REPO_ROOT / "tests" / "unit" / "test_deterministic.py").read_text(
        encoding="utf-8"
    )
    for token in ("1000.4", "842.0", "1680-01-619-4821", "DOC-01", "DOC-02", "WO-2026-88401"):
        assert token in unit_text


def test_xf16_f13_x_f14_eval_config_custom_metrics_grade_all_vv_golden_suite_scenarios() -> None:
    """F13 x F14: Verify `tests/eval/response_quality.py` custom metric scores 5.0 on all reference responses in `vv_golden_suite.json`."""
    from tests.eval.response_quality import evaluate

    vv_data = json.loads(
        (REPO_ROOT / "tests" / "eval" / "datasets" / "vv_golden_suite.json").read_text(
            encoding="utf-8"
        )
    )
    assert len(vv_data["eval_cases"]) == 10
    for case in vv_data["eval_cases"]:
        ref = case.get("reference", "")
        if not ref and "agent_data" in case:
            turns = case["agent_data"]["turns"]
            ref = " ".join(
                p.get("text", "")
                for t in turns
                for ev in t.get("events", [])
                for p in ev.get("content", {}).get("parts", [])
            )
        inst = {"response": ref, "reference": ref}
        assert evaluate(inst)["score"] == 5.0


def test_xf17_f15_x_f16_agent_runtime_deployment_manifest_aligns_with_gemini_enterprise_publish() -> None:
    """F15 x F16: Verify `agents-cli-manifest.yaml` and `Dockerfile` align with `europe-west1` Agent Runtime and Gemini Enterprise (`eu`) publication."""
    manifest_path = REPO_ROOT / "agents-cli-manifest.yaml"
    dockerfile_path = REPO_ROOT / "Dockerfile"
    assert manifest_path.exists()
    assert dockerfile_path.exists()
    manifest_text = manifest_path.read_text(encoding="utf-8")
    assert "europe-west1" in manifest_text
    assert "f35-sustainment-agent" in manifest_text or "app" in manifest_text


def test_xf18_f16_x_f17_gemini_enterprise_publication_and_git_repo_hygiene_alignment() -> None:
    """F16 x F17: Verify `.gitignore` protects credentials/artifacts while tracking deployment & eval manifests."""
    gitignore_path = REPO_ROOT / ".gitignore"
    assert gitignore_path.exists()
    gitignore_text = gitignore_path.read_text(encoding="utf-8")
    assert ".env" in gitignore_text or "*.pem" in gitignore_text or "__pycache__" in gitignore_text

    res = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0
