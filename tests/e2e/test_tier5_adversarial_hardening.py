"""Tier 5 White-Box Adversarial Hardening & Empirical Stress-Test Suite.

Directly exercises internal implementation contracts, edge cases,
boundary conditions, concurrency locks, and adversarial bypass vectors across:

1. `PERF-01..07` & `REG-01` Guardrail & Concurrency Stress
2. Schema & Type Strictness (`app/schemas.py`)
3. Cross-Service UC0/UC1/UC2 & Frontend TypeScript Parity Edge Cases
"""

from __future__ import annotations

import ast
import copy
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError

from tests.e2e import (
    E2ECallbackContext,
    E2ELlmRequest,
    E2EToolContext,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "app"


# ==============================================================================
# 1. PERF-01..07 & REG-01 GUARDRAIL & CONCURRENCY STRESS
# ==============================================================================


def test_t5_perf01_ast_zero_subprocess_and_os_system_across_entire_app() -> None:
    """PERF-01 Static AST Audit: Verify zero `subprocess`, `os.system`, `os.popen`, or `gcloud` CLI calls in `app/`."""
    forbidden_modules = {"subprocess", "pty", "commands"}
    forbidden_os_calls = {"system", "popen", "spawnl", "spawnle", "spawnlp", "spawnv", "spawnve", "spawnvp"}

    py_files = sorted(APP_DIR.rglob("*.py"))
    assert len(py_files) >= 9

    for py_file in py_files:
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split(".")[0]
                    assert root_mod not in forbidden_modules, (
                        f"PERF-01 violation: forbidden import {alias.name!r} in {py_file}"
                    )
            elif isinstance(node, ast.ImportFrom) and node.module:
                root_mod = node.module.split(".")[0]
                assert root_mod not in forbidden_modules, (
                    f"PERF-01 violation: forbidden from-import {node.module!r} in {py_file}"
                )
            elif isinstance(node, ast.Call):
                if (
                    isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "os"
                    and node.func.attr in forbidden_os_calls
                ):
                    pytest.fail(
                        f"PERF-01 violation: forbidden call os.{node.func.attr}() in {py_file}"
                    )


def test_t5_perf01_thread_safe_concurrent_get_access_token_and_auth_headers() -> None:
    """PERF-01 Concurrency Stress: Verify `get_access_token()` and `get_auth_headers()` across 24 concurrent worker threads."""
    from app.clients import get_access_token, get_auth_headers

    def _worker(_worker_id: int) -> tuple[str, dict[str, str]]:
        tok = get_access_token()
        hdrs = get_auth_headers()
        return tok, hdrs

    with ThreadPoolExecutor(max_workers=24) as pool:
        results = list(pool.map(_worker, range(24)))

    assert len(results) == 24
    first_tok = results[0][0]
    assert isinstance(first_tok, str) and len(first_tok) > 10
    for tok, hdrs in results:
        assert tok == first_tok
        assert hdrs["Authorization"] == f"Bearer {first_tok}"
        assert hdrs["X-Goog-User-Project"] == "antig-dave"
        assert hdrs["Content-Type"] == "application/json"


def test_t5_perf04_clean_snippet_text_strips_nested_malformed_and_script_html() -> None:
    """PERF-04 Adversarial HTML Fuzzing: Verify `clean_snippet_text` strips nested/malformed tags and collapses whitespace."""
    from app.clients import clean_snippet_text

    dirty_cases = [
        (
            "<b>Forward</b>   <i>canopy</i>\n\t<span class='hl'>locking catch</span>   <b>rigging</b>",
            "Forward canopy locking catch rigging",
        ),
        (
            "<script>alert(1)</script>Apply   <b>220°C</b>\r\nHigh-Temp <a href='http://evil'>RAM Sheet 'B'</a>",
            "alert(1)Apply 220°C High-Temp RAM Sheet 'B'",
        ),
        (
            "<div><p>PR-1776M   <b>Class B2</b>\n\n\nsilicon   sealant</p></div>",
            "PR-1776M Class B2 silicon sealant",
        ),
        ("", ""),
        ("   \n\t  ", ""),
    ]
    for raw_html, expected_clean in dirty_cases:
        cleaned = clean_snippet_text(raw_html)
        assert cleaned == expected_clean
        assert "<" not in cleaned and ">" not in cleaned
        assert "  " not in cleaned


def test_t5_uc2_bidirectional_uk_us_dialect_normalization_and_deduplication() -> None:
    """UC2 Dialect Engine: Verify bidirectional UK/US maintenance terminology expansion and deduplication."""
    from app.tools.uc2_jtd_search import normalize_cross_service_terminology

    # UK -> US expansion
    uk_query = "RAF F-35B hood catch binding and oleo gouge checked with torque spanner and earth lead"
    uk_res = normalize_cross_service_terminology(uk_query)
    uk_norm = uk_res["normalized_query"]
    uk_terms = uk_res["expanded_terms"]
    for expected_us in ("canopy", "latch", "stiff", "sticky", "shock strut", "score", "scoring", "wrench", "ground"):
        assert expected_us in uk_terms, f"Missing US synonym {expected_us!r} in {uk_terms}"
        assert expected_us in uk_norm.lower()

    # US -> UK expansion
    us_query = "USMC F-35B canopy latch stiff with score on shock strut checked with wrench and ground strap"
    us_res = normalize_cross_service_terminology(us_query)
    us_norm = us_res["normalized_query"]
    us_terms = us_res["expanded_terms"]
    for expected_uk in ("hood", "catch", "binding", "oleo", "gouge", "spanner", "earth"):
        assert expected_uk in us_terms, f"Missing UK synonym {expected_uk!r} in {us_terms}"
        assert expected_uk in us_norm.lower()

    # Deduplication check: repeated tokens in input must not produce duplicate entries in expanded_terms
    repeated_res = normalize_cross_service_terminology(
        "catch catch latch latch spanner wrench binding stiff gouge score"
    )
    rep_terms = repeated_res["expanded_terms"]
    assert len(rep_terms) == len(set(rep_terms)), f"Duplicate terms found: {rep_terms}"


def test_t5_perf02_03_reg01_discovery_engine_single_pass_and_bit_fault_ranking() -> None:
    """PERF-02, PERF-03 & REG-01: Verify Discovery Engine `pageSize=15`, omitted `summarySpec`, EU URL, and BIT ranking."""
    from app import clients, config
    from app.tools import uc2_jtd_search

    assert config.DISCOVERY_PAGE_SIZE == 15
    assert uc2_jtd_search.PAGE_SIZE == 15
    assert config.DE_LOCATION == "eu"
    assert config.BQ_LOCATION == "EU"
    assert config.COMPUTE_REGION == "europe-west1"

    for ds_id in (config.JTD_DATASTORE_ID, config.NARRATIVE_DATASTORE_ID):
        url = clients.build_de_search_url(ds_id)
        assert url.startswith("https://eu-discoveryengine.googleapis.com/v1alpha/projects/antig-dave/locations/eu/")
        assert f"/dataStores/{ds_id}/servingConfigs/default_search:search" in url

        payload = clients.build_de_search_payload(query="canopy catch binding")
        assert payload["pageSize"] == 15
        content_spec = payload["contentSearchSpec"]
        assert content_spec["snippetSpec"] == {"returnSnippet": True}
        assert "summarySpec" not in content_spec

    # Compare ranking when bit_fault_present=False vs bit_fault_present=True
    no_bit_res = uc2_jtd_search.search_technical_manuals_and_repair_logs(
        symptom_query="forward canopy locking catch binding no BIT fault",
        bit_fault_present=False,
        subsystem_filter="53-30",
    )
    top3_no_bit = [r["doc_id"] for r in no_bit_res["results"][:3]]
    assert set(top3_no_bit) == {"DOC-01", "DOC-02", "DOC-09"}
    doc03_no_bit = next(r for r in no_bit_res["results"] if r["doc_id"] == "DOC-03")
    assert doc03_no_bit["relevance_score"] < no_bit_res["results"][0]["relevance_score"]

    with_bit_res = uc2_jtd_search.search_technical_manuals_and_repair_logs(
        symptom_query="canopy actuator micro-switch BIT fault 9914 limit switch",
        bit_fault_present=True,
        subsystem_filter="53-30",
    )
    assert with_bit_res["results"][0]["doc_id"] == "DOC-03"


def test_t5_tc_lp_01_fast_path_before_model_callback_p99_latency_and_domain_passthrough() -> None:
    """TC-LP-01 & PERF-06/07: Verify `< 5.0 ms` p99 latency over 100 fast-path runs and non-interception of short domain queries."""
    from app import agent
    from app.agent import app
    from app.callbacks import fast_path_before_model_callback
    from app.clients import get_async_http_client, get_bq_client, get_http_client

    # PERF-07 singleton identity
    assert get_bq_client() is get_bq_client()
    assert get_http_client() is get_http_client()
    assert get_async_http_client() is get_async_http_client()

    # PERF-06 context cache config
    assert app.context_cache_config is not None
    assert app.context_cache_config.min_tokens == 2048
    assert app.context_cache_config.ttl_seconds == 1800
    assert app.context_cache_config.cache_intervals == 10
    static_header = getattr(
        agent,
        "STATIC_S1000D_REFERENCE_HEADER",
        getattr(agent, "STATIC_S1000D_AND_ASIP_REFERENCE_HEADER", ""),
    )
    assert len(static_header) >= 1800

    # 100-iteration latency benchmark on fast-path greetings/health probes
    fast_inputs = ["hi", "hello", "ping", "status", "health", "ready", "ok", "health check", "system status", "   "]
    latencies_ms: list[float] = []
    for i in range(100):
        prompt = fast_inputs[i % len(fast_inputs)]
        cb_ctx = E2ECallbackContext(state={})
        llm_req = E2ELlmRequest(prompt)
        t0 = time.perf_counter()
        resp = fast_path_before_model_callback(cb_ctx, llm_req)
        latencies_ms.append((time.perf_counter() - t0) * 1000.0)
        assert resp is not None, f"Fast-path failed to intercept {prompt!r}"
        assert cb_ctx.state["current_turn_id"] == 1

    p99_ms = sorted(latencies_ms)[98]
    mean_ms = statistics.mean(latencies_ms)
    assert p99_ms < 5.0, f"TC-LP-01 p99 latency {p99_ms:.3f} ms exceeded 5.0 ms limit"
    assert mean_ms < 1.0

    # Short domain queries (< 15 chars) that are NOT greetings MUST pass through (`return None`)
    short_domain_queries = [
        "ZM151",
        "ZM154 status",
        "DOC-01 JTD",
        "WO-2026-88401",
        "53-30 latch",
        "NSN 1680",
    ]
    for dq in short_domain_queries:
        cb_ctx = E2ECallbackContext(state={})
        llm_req = E2ELlmRequest(dq)
        resp = fast_path_before_model_callback(cb_ctx, llm_req)
        assert resp is None, f"Domain query {dq!r} was erroneously intercepted by fast-path!"


# ==============================================================================
# 2. SCHEMA & TYPE STRICTNESS (`app/schemas.py`)
# ==============================================================================


def test_t5_schema_01_core_models_reject_missing_required_fields_and_empty_strings() -> None:
    """Schema Strictness 1: Verify core Pydantic models in `app/schemas.py` reject missing required fields and empty strings."""
    from app import schemas

    models_with_required_fields: list[type[BaseModel]] = [
        schemas.VegaLiteSpec,
        schemas.ActuatorReadinessRecord,
        schemas.SortieSwapRecommendation,
        schemas.JtdCitation,
    ]
    for model_cls in models_with_required_fields:
        with pytest.raises(ValidationError):
            model_cls.model_validate({})

    # Empty string rejection (min_length=1) on string identifiers
    with pytest.raises(ValidationError):
        schemas.ActuatorReadinessRecord(
            tail_number="",
            current_flight_hours=842.0,
            life_limit_threshold_hrs=1000.0,
        )
    with pytest.raises(ValidationError):
        schemas.SortieSwapRecommendation(
            sortie_id="",
            primary_tail="ZM151",
            spare_tail="ZM154",
        )
    with pytest.raises(ValidationError):
        schemas.JtdCitation(doc_id="", title="Title", uri="gs://bucket/doc.pdf")


def test_t5_schema_02_numeric_lower_bounds_reject_negative_or_zero_values() -> None:
    """Schema Strictness 2: Verify `ge=0.0`, `gt=0.0`, and `ge=0` constraints reject invalid negative/zero numbers."""
    from app import schemas

    # ActuatorReadinessRecord: current_flight_hours < 0 or life_limit_threshold_hrs <= 0
    with pytest.raises(ValidationError):
        schemas.ActuatorReadinessRecord(
            tail_number="ZM151",
            current_flight_hours=-1.0,
            life_limit_threshold_hrs=1000.0,
        )
    with pytest.raises(ValidationError):
        schemas.ActuatorReadinessRecord(
            tail_number="ZM151",
            current_flight_hours=500.0,
            life_limit_threshold_hrs=0.0,
        )

    # SortieSwapRecommendation: negative stock or negative shipping_eta_hours
    with pytest.raises(ValidationError):
        schemas.SortieSwapRecommendation(
            sortie_id="SRT-01",
            primary_tail="ZM151",
            spare_tail="ZM154",
            depot_quantity_on_hand=-1,
        )
    with pytest.raises(ValidationError):
        schemas.SortieSwapRecommendation(
            sortie_id="SRT-01",
            primary_tail="ZM151",
            spare_tail="ZM154",
            depot_quantity_reserved_30d=-2,
        )
    with pytest.raises(ValidationError):
        schemas.SortieSwapRecommendation(
            sortie_id="SRT-01",
            primary_tail="ZM151",
            spare_tail="ZM154",
            shipping_eta_hours=-5.0,
        )


def test_t5_schema_04_model_validators_and_canonical_roundtrip_across_active_models() -> None:
    """Schema Strictness 3: Verify active Pydantic models in `app/schemas.py` compute derived fields and roundtrip cleanly."""
    from app import schemas

    # 1. ActuatorReadinessRecord auto-computes hours_remaining = life_limit_threshold_hrs - current_flight_hours
    rec = schemas.ActuatorReadinessRecord(
        tail_number="ZM151",
        current_flight_hours=1000.4,
        life_limit_threshold_hrs=1000.0,
    )
    assert rec.hours_remaining == -0.4

    # 2. VegaLiteSpec supports $schema alias round-trip
    vl = schemas.VegaLiteSpec(
        **{
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "title": "Test Chart",
            "data": {"values": [{"x": 1}]},
        }
    )
    dumped_vl = vl.model_dump(by_alias=True)
    assert dumped_vl["$schema"] == "https://vega.github.io/schema/vega-lite/v5.json"

    # 3. SortieSwapRecommendation
    swap = schemas.SortieSwapRecommendation(
        sortie_id="SRT-MAR-20261103-01",
        primary_tail="ZM151",
        spare_tail="ZM154",
    )
    assert swap.depot_quantity_on_hand == 4

    # 4. JtdCitation auto-populates markdown_link
    cit = schemas.JtdCitation(
        doc_id="DOC-01",
        title="Forward Canopy Rigging",
        uri="gs://antig-dave-f35-staging-europe-west1/unstructured/docs/DOC-01.pdf",
    )
    assert cit.markdown_link == "[DOC-01: Forward Canopy Rigging](gs://antig-dave-f35-staging-europe-west1/unstructured/docs/DOC-01.pdf)"


# ==============================================================================
# 3. CROSS-SERVICE UC0/UC1/UC2 & FRONTEND PARITY EDGE CASES
# ==============================================================================


def test_t5_uc1_adversarial_sortie_and_base_location_edge_cases() -> None:
    """UC1 Edge Cases: Verify `check_actuator_fatigue_and_depot_inventory` and `recommend_tail_swap_and_replenishment` with adversarial inputs."""
    from app.tools.uc1_analytics import (
        check_actuator_fatigue_and_depot_inventory,
        recommend_tail_swap_and_replenishment,
    )

    # Unknown base location still surfaces ZM151/ZM154 and valid Vega-Lite v5 charts without crashing
    res_unknown_base = check_actuator_fatigue_and_depot_inventory(
        base_location="RAF Lossiemouth",
        hours_to_limit_window=10.0,
        tool_context=E2EToolContext(),
    )
    assert res_unknown_base["primary_breach_tail"]["tail_number"] == "ZM151"
    assert res_unknown_base["spare_tail_candidate"]["tail_number"] == "ZM154"
    assert (
        res_unknown_base["depot_stock_vs_demand_bar_chart"]["$schema"]
        == "https://vega.github.io/schema/vega-lite/v5.json"
    )
    assert (
        res_unknown_base["actuator_fatigue_threshold_chart"]["$schema"]
        == "https://vega.github.io/schema/vega-lite/v5.json"
    )

    # Invalid swap where primary_tail == spare_tail is explicitly flagged as invalid
    same_tail_swap = recommend_tail_swap_and_replenishment(
        sortie_id="SRT-MAR-20261103-01",
        primary_tail="ZM151",
        spare_tail="ZM151",
        tool_context=E2EToolContext(),
    )
    assert same_tail_swap["swap_valid"] is False
    assert same_tail_swap["action_status"] == "REJECTED_INVALID_SPARE_TAIL"
    assert "INVALID_SWAP_CANDIDATE" in same_tail_swap["warning"]

    # Valid swap ZM151 -> ZM154 succeeds
    valid_swap = recommend_tail_swap_and_replenishment(
        sortie_id="SRT-MAR-20261103-01",
        primary_tail="ZM151",
        spare_tail="ZM154",
        tool_context=E2EToolContext(),
    )
    assert valid_swap["swap_valid"] is True
    assert valid_swap["action_status"] == "RECOMMENDED_SWAP_AND_REPLENISH"
    assert valid_swap["supply_nsn"] == "1680-01-619-4821"
    assert valid_swap["shipping_eta_hours"] == 18.0


def test_t5_frontend_typescript_vega_and_sheet_card_adversarial_contract_parity() -> None:
    """Cross-Layer Parity: Verify `VegaCanvas.tsx` and `MaintenanceSheetCard.tsx` enforce Vega-Lite v5 and Spreadsheet Card invariants."""
    vega_ts = (REPO_ROOT / "packages" / "web" / "components" / "VegaCanvas.tsx").read_text(
        encoding="utf-8"
    )
    sheet_ts = (
        REPO_ROOT / "packages" / "web" / "components" / "MaintenanceSheetCard.tsx"
    ).read_text(encoding="utf-8")

    # VegaCanvas invariants
    assert "https://vega.github.io/schema/vega-lite/v5.json" in vega_ts
    assert "validateVegaLiteSpec" in vega_ts
    assert "extractVegaLiteBlocks" in vega_ts
    assert "depot_stock_vs_demand_bar_chart" in vega_ts
    assert "actuator_fatigue_threshold_chart" in vega_ts

    # MaintenanceSheetCard invariants
    assert "MaintenanceSheetCard" in sheet_ts
    assert "csv" in sheet_ts.lower()


def test_t5_seed_data_immutability_across_repeated_tool_invocations() -> None:
    """State Isolation: Verify repeated UC0/UC1/UC2 tool calls never mutate in-memory `bq_seed_records` or `jtd_corpus`."""
    from app.seed_data import bq_seed_records, jtd_corpus
    from app.tools.uc0_maintenance import execute_maintenance_sql
    from app.tools.uc1_analytics import check_actuator_fatigue_and_depot_inventory
    from app.tools.uc2_jtd_search import search_technical_manuals_and_repair_logs

    snap_t1 = copy.deepcopy(bq_seed_records.AIRFRAME_COMPONENT_TELEMETRY_ROWS)
    snap_t2 = copy.deepcopy(bq_seed_records.GLOBAL_DEPOT_INVENTORY_ROWS)
    snap_t7 = copy.deepcopy(bq_seed_records.MAINTENANCE_WORK_ORDERS_ROWS)
    snap_t8 = copy.deepcopy(bq_seed_records.PHM_BIT_FAULT_EVENTS_ROWS)
    snap_t9 = copy.deepcopy(bq_seed_records.WORK_CENTER_TOOLING_AND_SQEP_ROWS)
    snap_docs = copy.deepcopy(jtd_corpus.JTD_CORPUS_DOCUMENTS)

    res0 = execute_maintenance_sql("SELECT * FROM maintenance_work_orders WHERE work_order_status != 'COMPLETED'")
    res0["rows"][0]["tail_number"] = "MUTATED_TAIL"

    res1 = check_actuator_fatigue_and_depot_inventory(base_location="RAF Marham")
    res1["primary_breach_tail"]["current_flight_hours"] = 999999.0

    res2 = search_technical_manuals_and_repair_logs(
        symptom_query="canopy catch binding", bit_fault_present=False
    )
    res2["results"][0]["title"] = "MUTATED_TITLE"

    assert bq_seed_records.AIRFRAME_COMPONENT_TELEMETRY_ROWS == snap_t1
    assert bq_seed_records.GLOBAL_DEPOT_INVENTORY_ROWS == snap_t2
    assert bq_seed_records.MAINTENANCE_WORK_ORDERS_ROWS == snap_t7
    assert bq_seed_records.PHM_BIT_FAULT_EVENTS_ROWS == snap_t8
    assert bq_seed_records.WORK_CENTER_TOOLING_AND_SQEP_ROWS == snap_t9
    assert jtd_corpus.JTD_CORPUS_DOCUMENTS == snap_docs
