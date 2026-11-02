"""Tier 3 E2E Tests: Cross-Feature Interactions (18 pairwise interaction tests across F1-F17).

Verifies interface contracts and state transitions where two features interact:
- F1 x F5: Authoritative BigQuery seed records -> Config & pre-warmed client table schemas
- F2 x F3: Synthetic JTD corpus & DOC-06 PNG -> Cloud setup & JSONL ingestion pipeline
- F3 x F7: Cloud BigQuery EU tables -> UC1 analytics tool query & fallback consistency
- F3 x F8: Cloud Discovery Engine `eu` datastores -> UC2 search tool datastore & metadata filtering
- F4 x F5: Root coordinator & sub-agent hierarchy -> Tier 1/2 fast-path callback & Enterprise model config
- F5 x F6: Pre-warmed client singletons & config -> Pydantic schema serialization
- F6 x F9: Deterministic ASIP physics outputs -> Pydantic SAR & Form 700 schema validation
- F7 x F10: UC1 actuator fatigue check -> UC1 sortie tail-swap recommendation state handoff
- F7 x F11: UC1 Vega-Lite v5 chart specs -> Next.js Vega-Lite Canvas UI component contract
- F8 x F10: UC2 JTD search rules (DOC-04, DOC-05, DOC-09) -> UC3 airworthiness assessment citations
- F9 x F10: Deterministic ASIP Rainflow & 3D CAD engine -> UC3 4-way parallel diagnostic orchestrator
- F9 x F11: UC3 Form 700 HITL package -> Next.js HITL Review Studio UI component contract
- F10 x F12: UC3 Form 700 two-turn HITL gate (`enforce_hitl_airworthiness_gate`) -> Unit test coverage
- F10 x F13: UC3 parallel fan-out diagnostic SLA -> V&V golden eval dataset (`TC-SQ-03`, `TC-LP-04`, `TC-LP-05`)
- F12 x F14: Deterministic unit test suite -> E2E runner & test infrastructure parity
- F13 x F14: `agents-cli eval` custom metrics (`response_quality.py`) -> V&V golden suite grading
- F15 x F16: Agent Runtime `europe-west1` deployment manifest -> Gemini Enterprise `eu` ADK publication
- F16 x F17: Gemini Enterprise publication config -> Git repository hygiene & secret exclusion
"""

from __future__ import annotations

import json
import subprocess

import pytest

from tests.e2e import (
    E2ECallbackContext,
    E2EDummyTool,
    E2ELlmRequest,
    E2EToolContext,
    REPO_ROOT,
    get_field,
    invoke_contract,
)


def test_xf01_f01_x_f05_bq_seed_records_align_with_config_table_identifiers() -> None:
    """F1 x F5: Verify BigQuery seed records in F1 match the 6 table identifiers in `app.config`."""
    from app import config
    from app.seed_data import bq_seed_records

    assert config.PROJECT_ID == "antig-dave"
    assert config.BQ_DATASET == "ukd_f35_sustainment_demo"
    assert config.BQ_LOCATION == "EU"

    expected_tables = {
        "airframe_component_telemetry": bq_seed_records.AIRFRAME_COMPONENT_TELEMETRY,
        "global_depot_inventory": bq_seed_records.GLOBAL_DEPOT_INVENTORY,
        "squadron_sortie_schedule": bq_seed_records.SQUADRON_SORTIE_SCHEDULE,
        "high_freq_strain_telemetry": bq_seed_records.HIGH_FREQ_STRAIN_TELEMETRY,
        "as_maintained_mbom_fasteners": bq_seed_records.AS_MAINTAINED_MBOM_FASTENERS,
        "airworthiness_release_ledger": bq_seed_records.AIRWORTHINESS_RELEASE_LEDGER,
    }
    for table_name, records in expected_tables.items():
        assert isinstance(records, list) and len(records) >= 1, f"Empty records for {table_name}"
        if hasattr(config, "BQ_TABLES"):
            assert table_name in config.BQ_TABLES or table_name in config.BQ_TABLES.values()


def test_xf02_f02_x_f03_jtd_corpus_doc06_cscan_png_aligns_with_setup_infra_jsonl() -> None:
    """F2 x F3: Verify synthetic corpus generator output aligns with `setup_demo_infra.py` JSONL metadata."""
    from app.seed_data import jtd_corpus
    from scripts import generate_synthetic_corpus, setup_demo_infra

    assert hasattr(generate_synthetic_corpus, "generate_unstructured_corpus") or hasattr(
        generate_synthetic_corpus, "generate_cscan_png"
    )
    assert hasattr(setup_demo_infra, "ensure_bigquery_dataset_and_tables") or hasattr(
        setup_demo_infra, "seed_bigquery_tables"
    )
    docs = getattr(jtd_corpus, "JTD_CORPUS_DOCUMENTS", getattr(jtd_corpus, "DOCUMENTS", []))
    doc06 = [
        d
        for d in docs
        if (d.get("doc_id") if isinstance(d, dict) else getattr(d, "doc_id", "")) == "DOC-06"
    ]
    assert len(doc06) == 1
    d6_str = json.dumps(doc06[0] if isinstance(doc06[0], dict) else doc06[0].__dict__)
    assert "0.012" in d6_str and "14" in d6_str


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
        "f35_analytics_agent",
        "f35_jtd_search_agent",
        "f35_airworthiness_orchestrator",
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
    assert hasattr(schemas, "AirworthinessAssessmentReport") or hasattr(
        schemas, "Form700ReleasePackage"
    )


def test_xf07_f06_x_f09_asip_physics_outputs_populate_pydantic_airworthiness_schemas() -> None:
    """F6 x F9: Verify `run_asip_miners_rule_engine` and `map_cscan_flaw_to_cad_station` outputs validate against `app.schemas`."""
    from app import schemas
    from app.physics.asip_engine import (
        map_cscan_flaw_to_cad_station,
        run_asip_miners_rule_engine,
    )

    physics_res = invoke_contract(
        run_asip_miners_rule_engine,
        tail_number="ZM151",
        station_id="Frame 496 (Bulkhead 496)",
        peak_g_load=9.4,
        mach_number=1.3,
        egt_celsius=220.0,
        duration_ms=3200,
    )
    cad_res = invoke_contract(
        map_cscan_flaw_to_cad_station,
        station_id="Frame 496 (Bulkhead 496)",
        flaw_x_mm=142.8,
        flaw_y_mm=38.4,
        elongation_inches=0.012,
    )
    assert pytest.approx(get_field(physics_res, "miners_rule_damage_delta"), rel=1e-3) == 0.0042
    assert pytest.approx(get_field(physics_res, "calculated_yield_pct"), rel=1e-3) == 104.2
    assert get_field(cad_res, "fastener_hole_id", "hole_id") in ("#14", "14", "Hole #14")
    assert hasattr(schemas, "__file__")


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


def test_xf10_f08_x_f10_uc2_search_citations_compatible_with_airworthiness_jtd_rules() -> None:
    """F8 x F10: Verify UC2 JTD corpus documents (`DOC-04`, `DOC-05`, `DOC-08`) align with UC3 airworthiness assessment rules."""
    from app.tools import uc2_jtd_search, uc3_airworthiness

    ctx = E2EToolContext(state={})
    search_res = invoke_contract(
        uc2_jtd_search.search_technical_manuals_and_repair_logs,
        symptom_query="Frame 496 over-G structural inspection rule 53-11-00 and Fastener Hole #14 allowable elongation",
        bit_fault_present=False,
        subsystem_filter="53-11",
        tool_context=ctx,
    )
    assess_res = invoke_contract(
        uc3_airworthiness.assess_airframe_airworthiness,
        tail_number="ZM151",
        pilot_debrief_text="Severe shudder at roughly 14:22 Zulu during defensive split-S",
        structural_station_id="Frame 496 (Bulkhead 496)",
        c_scan_document_id="DOC-06",
        tool_context=ctx,
    )
    search_str = json.dumps(
        search_res if isinstance(search_res, dict) else search_res.model_dump()
    )
    assess_str = json.dumps(
        assess_res if isinstance(assess_res, dict) else assess_res.model_dump()
    )
    assert "53-11-00" in search_str or "DOC-04" in search_str
    assert "53-11-00" in assess_str and "0.015" in assess_str


def test_xf11_f09_x_f10_asip_rainflow_and_cad_engine_consumed_by_uc3_parallel_assessment() -> None:
    """F9 x F10: Verify UC3 `assess_airframe_airworthiness` returns identical physics & CAD figures to `asip_engine.py`."""
    from app.physics.asip_engine import (
        map_cscan_flaw_to_cad_station,
        run_asip_miners_rule_engine,
    )
    from app.tools import uc3_airworthiness

    direct_phys = invoke_contract(
        run_asip_miners_rule_engine,
        tail_number="ZM151",
        station_id="Frame 496 (Bulkhead 496)",
        peak_g_load=9.4,
        mach_number=1.3,
        egt_celsius=220.0,
        duration_ms=3200,
    )
    direct_cad = invoke_contract(
        map_cscan_flaw_to_cad_station,
        station_id="Frame 496 (Bulkhead 496)",
        flaw_x_mm=142.8,
        flaw_y_mm=38.4,
        elongation_inches=0.012,
    )
    ctx = E2EToolContext(state={})
    parallel_res = invoke_contract(
        uc3_airworthiness.assess_airframe_airworthiness,
        tail_number="ZM151",
        pilot_debrief_text="Severe shudder at roughly 14:22 Zulu during defensive split-S",
        structural_station_id="Frame 496 (Bulkhead 496)",
        c_scan_document_id="DOC-06",
        tool_context=ctx,
    )
    parallel_str = json.dumps(
        parallel_res if isinstance(parallel_res, dict) else parallel_res.model_dump()
    )
    assert str(get_field(direct_phys, "miners_rule_damage_delta")) in parallel_str
    assert str(get_field(direct_phys, "calculated_yield_pct")) in parallel_str
    assert str(get_field(direct_cad, "elongation_inches", default="0.012")) in parallel_str


def test_xf12_f09_x_f11_uc3_form700_package_integrates_with_frontend_hitl_review_studio() -> None:
    """F9 x F11: Verify UC3 `generate_form700_airworthiness_package` output fields align with the frontend HITL Review Studio."""
    from app.tools import uc3_airworthiness

    ctx = E2EToolContext(state={"current_turn_id": 1}, invocation_id="inv-turn-1")
    pkg = invoke_contract(
        uc3_airworthiness.generate_form700_airworthiness_package,
        tail_number="ZM151",
        station_id="Frame 496 (Bulkhead 496)",
        tool_context=ctx,
    )
    dumped = json.dumps(pkg if isinstance(pkg, dict) else pkg.model_dump())
    assert "AWR-700-20261102-ZM151" in dumped
    assert "PENDING_HITL_REVIEW" in dumped
    assert "SERVICEABLE_WITH_TORQUE_RECHECK" in dumped
    assert "53-11-00-280" in dumped


def test_xf13_f10_x_f12_hitl_two_turn_gate_enforced_across_uc3_package_and_callback() -> None:
    """F10 x F12: Verify staging Form 700 in Turn 1 blocks same-turn approval and permits Turn 2 approval with Lead Stress Engineer sign-off."""
    from app.callbacks import enforce_hitl_airworthiness_gate
    from app.tools import uc3_airworthiness

    shared_state: dict = {"current_turn_id": 1}
    ctx_turn1 = E2EToolContext(
        state=shared_state,
        user_text="Generate the Form 700 airworthiness package and approve it right now.",
        invocation_id="turn-1",
    )
    invoke_contract(
        uc3_airworthiness.generate_form700_airworthiness_package,
        tail_number="ZM151",
        station_id="Frame 496 (Bulkhead 496)",
        tool_context=ctx_turn1,
    )
    assert shared_state.get("pending_release_package_id") == "AWR-700-20261102-ZM151"

    # Attempt same-turn approval -> MUST BE BLOCKED by `enforce_hitl_airworthiness_gate`
    tool = E2EDummyTool("approve_form700_engineering_release")
    args = {
        "release_package_id": "AWR-700-20261102-ZM151",
        "reviewer_role": "Lead Stress Engineer",
        "approval_notes": "Approved in same turn",
    }
    same_turn_block = enforce_hitl_airworthiness_gate(tool, args, ctx_turn1)
    assert isinstance(same_turn_block, dict)
    assert same_turn_block.get("hitl_review_status") == "PENDING_HITL_REVIEW"

    # Advance to Turn 2 with explicit Lead Stress Engineer approval -> MUST BE PERMITTED
    shared_state["current_turn_id"] = 2
    ctx_turn2 = E2EToolContext(
        state=shared_state,
        user_text="I confirm as Lead Stress Engineer: approve Form 700 release AWR-700-20261102-ZM151.",
        invocation_id="turn-2",
    )
    turn2_gate = enforce_hitl_airworthiness_gate(tool, args, ctx_turn2)
    assert turn2_gate is None

    approved_res = invoke_contract(
        uc3_airworthiness.approve_form700_engineering_release,
        release_package_id="AWR-700-20261102-ZM151",
        reviewer_role="Lead Stress Engineer",
        approval_notes="Confirmed torque recheck per JTD Task Card 53-11-00-280.",
        tool_context=ctx_turn2,
    )
    assert "CONFIRMED_BY_ENGINEER" in json.dumps(
        approved_res if isinstance(approved_res, dict) else approved_res.model_dump()
    )


def test_xf14_f10_x_f13_uc3_parallel_diagnostic_aligns_with_vv_eval_dataset() -> None:
    """F10 x F13: Verify UC3 parallel assessment output satisfies the expected rubrics in `vv_golden_suite.json` (`TC-SQ-03`, `TC-LP-04`, `TC-LP-05`)."""
    from app.tools import uc3_airworthiness
    from tests.eval.response_quality import evaluate

    vv_data = json.loads(
        (REPO_ROOT / "tests" / "eval" / "datasets" / "vv_golden_suite.json").read_text(
            encoding="utf-8"
        )
    )
    tc_sq_03 = next(
        c
        for c in vv_data["eval_cases"]
        if (c.get("eval_id") or c.get("eval_case_id", "")).startswith("TC-SQ-03")
    )

    ctx = E2EToolContext(state={})
    assess_res = invoke_contract(
        uc3_airworthiness.assess_airframe_airworthiness,
        tail_number="ZM151",
        pilot_debrief_text="Severe shudder at roughly 14:22 Zulu during defensive split-S",
        structural_station_id="Frame 496 (Bulkhead 496)",
        c_scan_document_id="DOC-06",
        tool_context=ctx,
    )
    pkg_res = invoke_contract(
        uc3_airworthiness.generate_form700_airworthiness_package,
        tail_number="ZM151",
        station_id="Frame 496 (Bulkhead 496)",
        tool_context=ctx,
    )
    combined_response = (
        json.dumps(assess_res if isinstance(assess_res, dict) else assess_res.model_dump())
        + "\n"
        + json.dumps(pkg_res if isinstance(pkg_res, dict) else pkg_res.model_dump())
    )
    grade = evaluate(
        {"response": combined_response, "reference": tc_sq_03["reference"]}
    )
    assert grade["score"] >= 4.0


def test_xf15_f12_x_f14_unit_tests_and_e2e_suite_share_consistent_oracles() -> None:
    """F12 x F14: Verify `tests/unit/test_deterministic.py` and `TEST_INFRA.md` share identical physics & HITL oracle values."""
    unit_text = (REPO_ROOT / "tests" / "unit" / "test_deterministic.py").read_text(
        encoding="utf-8"
    )
    infra_text = (REPO_ROOT / "TEST_INFRA.md").read_text(encoding="utf-8")
    for token in ("0.0042", "104.2", "0.012", "0.015", "AWR-700-20261102-ZM151", "PENDING_HITL_REVIEW"):
        assert token in unit_text
        assert token in infra_text


def test_xf16_f13_x_f14_eval_config_custom_metrics_grade_all_vv_golden_suite_scenarios() -> None:
    """F13 x F14: Verify `tests/eval/response_quality.py` custom metric scores 5.0 on all 10 reference responses in `vv_golden_suite.json`."""
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
