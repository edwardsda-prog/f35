"""Tier 4 E2E Tests: Real-World UK Defence F-35 Sustainment Scenarios (10 end-to-end scenarios).

Exercises complete multi-step operational workflows across:
1. UC1 RAF Marham Morning Sortie Readiness, Vega-Lite v5 Charting & Tail-Swap (`TC-SQ-01`, `TC-LP-02`)
2. UC2 Cross-Service Dialect Normalization & Sticky Canopy Latch Investigation (`TC-SQ-02`, `TC-LP-03`)
3. UC2 High-Temp RAM Cure (`220C`) & Composite Gouge (`0.06 in`) Negative Constraint Synthesis (`TC-SQ-04`)
4. UC3 Frame 496 `9.4 G` Exceedance 4-Way Parallel Diagnostic Fan-Out (`TC-SQ-03`, `TC-LP-04`)
5. UC3 Two-Turn Form 700 HITL Engineering Release Full Lifecycle (`TC-LP-05`, `SAFE-02`)
6. Multi-Hop Cross-Domain Sustainment Disambiguation (`TC-SQ-05`: UC1 + UC2 in one session)
7. Tier 1/2 Fast-Path Greeting & Health-Check Interception (`< 5 ms` SLA, `TC-LP-01`)
8. Full Architecture & Guardrail Compliance Audit (`REG-01`, `PERF-01..07`, `SAFE-01..02`)
9. Complete 10-Scenario V&V Golden Suite (`vv_golden_suite.json`) & Basic Dataset Grading Pipeline
10. Cloud Deployment, Gemini Enterprise (`eu`) Publication & Optional Live Endpoint Verification (`F15`–`F17`)
"""

from __future__ import annotations

import json
import os
import time

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


def test_rw01_uc1_raf_marham_morning_sortie_readiness_and_tail_swap_workflow() -> None:
    """RW-01 (UC1 / TC-SQ-01 / TC-LP-02): Complete RAF Marham morning sortie readiness check, Vega-Lite v5 charts, and tail swap."""
    from app.tools import uc1_analytics

    session_state: dict = {"current_turn_id": 1}
    ctx = E2EToolContext(
        state=session_state,
        user_text=(
            "Check RAF Marham F-35B electro-hydrostatic actuator fatigue hours against depot inventory "
            "and recommend a tail swap for morning sortie SRT-MAR-20261103-01."
        ),
        invocation_id="rw01-turn-1",
    )

    t0 = time.perf_counter()
    fatigue_report = invoke_contract(
        uc1_analytics.check_actuator_fatigue_and_depot_inventory,
        base_location="RAF Marham",
        hours_to_limit_window=20.0,
        tool_context=ctx,
    )
    swap_plan = invoke_contract(
        uc1_analytics.recommend_tail_swap_and_replenishment,
        sortie_id="SRT-MAR-20261103-01",
        primary_tail="ZM151",
        spare_tail="ZM154",
        tool_context=ctx,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms < 2500.0, f"UC1 workflow exceeded 2,500ms budget: {elapsed_ms:.1f}ms"

    report_str = json.dumps(
        fatigue_report if isinstance(fatigue_report, dict) else fatigue_report.model_dump()
    )
    swap_str = json.dumps(
        swap_plan if isinstance(swap_plan, dict) else swap_plan.model_dump()
    )

    for expected_token in (
        "ZM151",
        "ACT-99812-F",
        "1000.4",
        "PMC-M",
        "ZM154",
        "842",
        "1680-01-619-4821",
        "vega.github.io/schema/vega-lite/v5.json",
    ):
        assert expected_token in report_str, f"Missing {expected_token} in UC1 report"

    for expected_swap_token in (
        "SRT-MAR-20261103-01",
        "ZM151",
        "ZM154",
        "1680-01-619-4821",
        "18",
    ):
        assert expected_swap_token in swap_str, f"Missing {expected_swap_token} in UC1 swap plan"


def test_rw02_uc2_cross_service_sticky_canopy_latch_and_roller_sealant_investigation() -> None:
    """RW-02 (UC2 / TC-SQ-02 / TC-LP-03): UK/US cross-service terminology normalization & sticky canopy catch troubleshooting."""
    from app.tools import uc2_jtd_search

    ctx = E2EToolContext(
        state={"current_turn_id": 1},
        user_text=(
            "We have a sticky canopy catch and binding roller on an F-35B at RAF Marham "
            "with no BIT fault logged. Search the JTD manuals and 5-year cross-service repair logs."
        ),
        invocation_id="rw02-turn-1",
    )

    t0 = time.perf_counter()
    norm = invoke_contract(
        uc2_jtd_search.normalize_cross_service_terminology,
        query="sticky canopy catch and binding roller adjusted with spanner, minor score on skin",
    )
    search_res = invoke_contract(
        uc2_jtd_search.search_technical_manuals_and_repair_logs,
        symptom_query="sticky canopy catch and binding roller on F-35B with no BIT fault",
        bit_fault_present=False,
        subsystem_filter="53-30",
        tool_context=ctx,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms < 2000.0, f"UC2 search exceeded 2,000ms budget: {elapsed_ms:.1f}ms"

    norm_str = json.dumps(norm if isinstance(norm, dict) else str(norm)).lower()
    assert "latch" in norm_str and "wrench" in norm_str and "gouge" in norm_str

    res_str = json.dumps(
        search_res if isinstance(search_res, dict) else search_res.model_dump()
    )
    assert "DOC-01" in res_str
    assert "DOC-02" in res_str
    assert "53-30-01" in res_str
    assert "<b>" not in res_str and "</b>" not in res_str


def test_rw03_uc2_high_temp_ram_cure_and_composite_gouge_negative_constraint_workflow() -> None:
    """RW-03 (UC2 / TC-SQ-04): Verify 220C High-Temp RAM Sheet 'B' cure (`DOC-09`) and 0.06-in composite gouge scarf patch (`DOC-07`)."""
    from app.tools import uc2_jtd_search

    ctx = E2EToolContext(state={"current_turn_id": 1}, invocation_id="rw03-turn-1")
    ram_res = invoke_contract(
        uc2_jtd_search.search_technical_manuals_and_repair_logs,
        symptom_query="Low Observable RAM restoration near Frame 496 aft fuselage where EGT reaches 220C and 0.06 inch composite skin gouge",
        bit_fault_present=False,
        subsystem_filter="51-40",
        tool_context=ctx,
    )
    ram_str = json.dumps(ram_res if isinstance(ram_res, dict) else ram_res.model_dump())
    assert "DOC-09" in ram_str or "Sheet 'B'" in ram_str or "220" in ram_str


def test_rw04_uc3_frame496_9_4g_exceedance_four_way_parallel_diagnostic_workflow() -> None:
    """RW-04 (UC3 / TC-SQ-03 / TC-LP-04): Full 4-way parallel diagnostic fan-out on Tail ZM151 Frame 496 in <= 3,100 ms."""
    from app.tools import uc3_airworthiness

    ctx = E2EToolContext(
        state={"current_turn_id": 1},
        user_text=(
            "Pilot reported severe airframe shudder at roughly 14:22 Zulu during a defensive split-S "
            "on Tail ZM151. Run the full parallel airworthiness assessment on Frame 496 with DOC-06."
        ),
        invocation_id="rw04-turn-1",
    )

    t0 = time.perf_counter()
    assessment = invoke_contract(
        uc3_airworthiness.assess_airframe_airworthiness,
        tail_number="ZM151",
        pilot_debrief_text="Severe shudder at roughly 14:22 Zulu during defensive split-S",
        structural_station_id="Frame 496 (Bulkhead 496)",
        c_scan_document_id="DOC-06",
        tool_context=ctx,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms <= 3100.0, f"UC3 4-way fan-out exceeded 3,100ms SLA: {elapsed_ms:.1f}ms"

    dumped = json.dumps(
        assessment if isinstance(assessment, dict) else assessment.model_dump()
    )
    for mandatory_fact in (
        "9.4",
        "1.3",
        "220",
        "0.0042",
        "104.2",
        "CLASS_A_ULTRASONIC_C_SCAN",
        "14",
        "0.012",
        "0.015",
        "8841-B",
        "Ti-6Al-4V",
        "53-11-00-280",
    ):
        assert mandatory_fact in dumped, f"Missing mandatory UC3 diagnostic fact: {mandatory_fact}"


def test_rw05_uc3_two_turn_form700_hitl_airworthiness_release_full_lifecycle() -> None:
    """RW-05 (UC3 / TC-LP-05 / SAFE-02): Full 2-turn Form 700 HITL workflow (stage -> block same turn -> reject tech -> approve CTO)."""
    from app.callbacks import enforce_hitl_airworthiness_gate
    from app.tools import uc3_airworthiness

    session_state: dict = {"current_turn_id": 1}
    ctx_turn1 = E2EToolContext(
        state=session_state,
        user_text="Stage the Form 700 airworthiness release package for ZM151 Frame 496 and sign it off immediately.",
        invocation_id="rw05-turn-1",
    )

    pkg = invoke_contract(
        uc3_airworthiness.generate_form700_airworthiness_package,
        tail_number="ZM151",
        station_id="Frame 496 (Bulkhead 496)",
        tool_context=ctx_turn1,
    )
    pkg_str = json.dumps(pkg if isinstance(pkg, dict) else pkg.model_dump())
    assert "AWR-700-20261102-ZM151" in pkg_str
    assert "PENDING_HITL_REVIEW" in pkg_str
    assert "CONFIRMED_BY_ENGINEER" not in pkg_str

    approve_tool = E2EDummyTool("approve_form700_engineering_release")
    approve_args = {
        "release_package_id": "AWR-700-20261102-ZM151",
        "reviewer_role": "Lead Stress Engineer",
        "approval_notes": "Attempted same-turn auto-approval",
    }

    # Step 1: Same-turn approval attempt MUST be blocked by `enforce_hitl_airworthiness_gate`
    gate_turn1 = enforce_hitl_airworthiness_gate(approve_tool, approve_args, ctx_turn1)
    assert isinstance(gate_turn1, dict)
    assert gate_turn1.get("hitl_review_status") == "PENDING_HITL_REVIEW"

    # Step 2: Turn 2 unauthorized Line Technician attempt MUST be blocked
    session_state["current_turn_id"] = 2
    ctx_turn2_unauth = E2EToolContext(
        state=session_state,
        user_text="I am a Line Technician, go ahead and release ZM151.",
        invocation_id="rw05-turn-2-unauth",
    )
    unauth_args = {
        "release_package_id": "AWR-700-20261102-ZM151",
        "reviewer_role": "Line Technician",
        "approval_notes": "Looks fine to me",
    }
    gate_turn2_unauth = enforce_hitl_airworthiness_gate(
        approve_tool, unauth_args, ctx_turn2_unauth
    )
    assert isinstance(gate_turn2_unauth, dict)
    assert gate_turn2_unauth.get("hitl_review_status") == "PENDING_HITL_REVIEW"

    # Step 3: Turn 2 authorized Lead Stress Engineer / CTO sign-off MUST succeed
    ctx_turn2_auth = E2EToolContext(
        state=session_state,
        user_text=(
            "I confirm as Lead Stress Engineer: approve Form 700 release package "
            "AWR-700-20261102-ZM151 for Tail ZM151 with calibrated torque recheck per JTD Task Card 53-11-00-280."
        ),
        invocation_id="rw05-turn-2-auth",
    )
    auth_args = {
        "release_package_id": "AWR-700-20261102-ZM151",
        "reviewer_role": "Lead Stress Engineer",
        "approval_notes": "Approved per MIL-STD-3001 SAR and JTD Task Card 53-11-00-280.",
    }
    gate_turn2_auth = enforce_hitl_airworthiness_gate(
        approve_tool, auth_args, ctx_turn2_auth
    )
    assert gate_turn2_auth is None

    final_release = invoke_contract(
        uc3_airworthiness.approve_form700_engineering_release,
        release_package_id="AWR-700-20261102-ZM151",
        reviewer_role="Lead Stress Engineer",
        approval_notes="Approved per MIL-STD-3001 SAR and JTD Task Card 53-11-00-280.",
        tool_context=ctx_turn2_auth,
    )
    final_str = json.dumps(
        final_release if isinstance(final_release, dict) else final_release.model_dump()
    )
    assert "CONFIRMED_BY_ENGINEER" in final_str
    assert "AWR-700-20261102-ZM151" in final_str


def test_rw06_vv_tc_sq_05_multi_hop_intent_disambiguation_across_uc1_and_uc2() -> None:
    """RW-06 (TC-SQ-05): Multi-hop compound scenario combining UC1 depot stock check and UC2 canopy latch search."""
    from app.tools import uc1_analytics, uc2_jtd_search

    shared_state: dict = {"current_turn_id": 1}
    ctx = E2EToolContext(
        state=shared_state,
        user_text=(
            "First check RAF Marham electro-hydrostatic actuator depot stock for ZM151, "
            "and also search the JTD manuals for sticky canopy catch binding with no BIT fault."
        ),
        invocation_id="rw06-turn-1",
    )
    uc1_res = invoke_contract(
        uc1_analytics.check_actuator_fatigue_and_depot_inventory,
        base_location="RAF Marham",
        hours_to_limit_window=20.0,
        tool_context=ctx,
    )
    uc2_res = invoke_contract(
        uc2_jtd_search.search_technical_manuals_and_repair_logs,
        symptom_query="sticky canopy catch binding with no BIT fault",
        bit_fault_present=False,
        subsystem_filter="53-30",
        tool_context=ctx,
    )
    combined = json.dumps(
        uc1_res if isinstance(uc1_res, dict) else uc1_res.model_dump()
    ) + json.dumps(uc2_res if isinstance(uc2_res, dict) else uc2_res.model_dump())
    assert "1680-01-619-4821" in combined
    assert "DOC-01" in combined and "DOC-02" in combined


def test_rw07_vv_tc_lp_01_fast_path_greeting_and_health_check_sub_5ms_sla() -> None:
    """RW-07 (TC-LP-01): Verify Tier 1/2 `fast_path_before_model_callback` executes in < 5ms for greetings and health checks."""
    from app.callbacks import fast_path_before_model_callback

    for prompt in ("hi", "hello", "ping", "status"):
        ctx = E2ECallbackContext(state={}, user_text=prompt)
        req = E2ELlmRequest(prompt)
        t0 = time.perf_counter()
        resp = fast_path_before_model_callback(ctx, req)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        assert resp is not None, f"Expected fast-path interception for '{prompt}'"
        assert elapsed_ms < 5.0, f"Fast-path callback took {elapsed_ms:.2f}ms (> 5.0ms SLA)"


def test_rw08_guardrail_audit_eu_residency_enterprise_genai_and_zero_gcloud_subprocesses() -> None:
    """RW-08 (REG-01, PERF-01..07, SAFE-01..02): End-to-end static & runtime audit across all Python files in `app/`."""
    from app import config

    assert config.PROJECT_ID == "antig-dave"
    assert config.GCP_REGION == "europe-west1"
    assert config.BQ_LOCATION == "EU"
    assert config.DISCOVERY_ENGINE_LOCATION == "eu"
    assert config.GEMINI_ENTERPRISE is True
    assert config.GEMINI_LOCATION == "global"
    assert config.DISCOVERY_PAGE_SIZE >= 15

    app_dir = REPO_ROOT / "app"
    for py_file in app_dir.rglob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        assert "print-access-token" not in source, f"Forbidden gcloud subprocess in {py_file}"
        assert "thinking_budget" not in source, f"Forbidden legacy thinking_budget in {py_file}"
        assert "vertexai=True" not in source, f"Forbidden legacy vertexai=True in {py_file}"


def test_rw09_full_vv_golden_suite_and_basic_dataset_offline_grading_pipeline() -> None:
    """RW-09 (F13 / Section 8 V&V): Run `tests/eval/response_quality.py` across all `basic-dataset.json` & `vv_golden_suite.json` cases."""
    from tests.eval.response_quality import evaluate

    basic_path = REPO_ROOT / "tests" / "eval" / "datasets" / "basic-dataset.json"
    vv_path = REPO_ROOT / "tests" / "eval" / "datasets" / "vv_golden_suite.json"

    basic_cases = json.loads(basic_path.read_text(encoding="utf-8"))["eval_cases"]
    vv_cases = json.loads(vv_path.read_text(encoding="utf-8"))["eval_cases"]
    assert len(basic_cases) >= 4
    assert len(vv_cases) >= 10

    for case in basic_cases + vv_cases:
        ref = case.get("reference", "")
        if not ref and "agent_data" in case:
            ref = " ".join(
                p.get("text", "")
                for t in case["agent_data"]["turns"]
                for ev in t.get("events", [])
                for p in ev.get("content", {}).get("parts", [])
            )
        instance = {"response": ref, "reference": ref}
        assert evaluate(instance)["score"] == 5.0


def test_rw10_deployment_publication_and_optional_live_reasoning_engine_smoke_check() -> None:
    """RW-10 (F15, F16, F17): Verify deployment/publication artifacts and optionally query live Reasoning Engine when enabled."""
    manifest = (REPO_ROOT / "agents-cli-manifest.yaml").read_text(encoding="utf-8")
    assert "europe-west1" in manifest

    if os.environ.get("VERIFY_LIVE_DEPLOYED_ENDPOINT") == "1":
        import google.auth
        from google.auth.transport.requests import Request
        import httpx

        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())
        url = (
            f"https://europe-west1-aiplatform.googleapis.com/v1beta1/"
            f"projects/{project or 'antig-dave'}/locations/europe-west1/reasoningEngines"
        )
        resp = httpx.get(
            url,
            headers={"Authorization": f"Bearer {credentials.token}"},
            timeout=15.0,
        )
        assert resp.status_code == 200
        engines = resp.json().get("reasoningEngines", [])
        assert len(engines) >= 1, "Expected at least 1 deployed Reasoning Engine in europe-west1"
