# QA / Test Agent Boundary — `/tests`

> **Scope:** QA / Test Specialist Subagent  
> **Mandatory Guidelines:** Review root `AGENTS.md` and `.agents-cli-spec.md` for platform invariants.

## Responsibilities
- Unit tests (`tests/unit/test_deterministic.py`):
  - UC0 Maintenance Work Order schema (`maintenance_work_orders.schema.json`), 14 seed rows (`MAINTENANCE_WORK_ORDERS_ROWS`), read-only SQL guardrail (`ValueError` on DML/DDL), Excel / Google Sheets Spreadsheet Card rendering (`=COUNTA`, `=SUM`), status badges (`🟡 PMC-M`, `🔴 NMC-S (MICAP)`), and authenticated GCS `.csv` export URL verification.
  - Deterministic ASIP physics solver validation (Rainflow cycle counting, Palmgren-Miner damage $D$, MIL-HDBK-516C compliance).
  - Fastener 3D CAD coordinate matrix transformation verification (Frame 496, Hole #14).
  - Two-turn HITL Form 700 release gate enforcement (`before_tool_callback`).
  - Pydantic schema validation for UC1 charts, UC2 citations, and UC3 SAR.
- Evaluation suite (`tests/eval/`):
  - Configuration (`tests/eval/eval_config.yaml`).
  - Smoke evaluation dataset (`tests/eval/datasets/basic-dataset.json`), including `uc0_maintenance_work_orders_spreadsheet_card`.
  - V&V Golden Suite (`tests/eval/datasets/vv_golden_suite.json`) covering `TC-SQ-00..05` (Quality) and `TC-LP-00..05` (Latency).

## V&V Test Matrix (`tests/eval/datasets/vv_golden_suite.json`)

| Test ID | Eval Case ID | Use Case | Target Tool / Capability | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **`TC-SQ-00`** | `uc0_tc_sq_00_conversational_maintenance_sql_card` | **UC0** | `execute_maintenance_sql` | Dynamic read-only Text-to-SQL over `maintenance_work_orders` returning 10 active work orders (`ZM151`: `WO-2026-88401..88403`), Spreadsheet Card (`A..R`), status badges (`🟡 PMC-M`, `🔴 NMC-S (MICAP)`), formula footer (`=COUNTA`, `=SUM`), and GCS CSV link. |
| **`TC-SQ-01`** | `TC-SQ-01_multi_source_retrieval_recall` | **UC2** | `search_technical_manuals_and_repair_logs` | Multi-source retrieval recall (`DOC-01`, `DOC-02`) on subsystem `53-30` with `bit_fault_associated="false"`. |
| **`TC-SQ-02`** | `TC-SQ-02_cross_dialect_and_acronym_resolution` | **UC2** | `search_technical_manuals_and_repair_logs` | UK/US cross-dialect normalization (`catch` ↔ `latch`, `spanner` ↔ `wrench`, `gouge` ↔ `score`). |
| **`TC-SQ-03`** | `TC-SQ-03_groundedness_zero_hallucination_safety_limits` | **UC3** | `run_parallel_airworthiness_assessment` | Zero-hallucination safety limits grounded in `DOC-04` (JTD Rule 53-11-00) and `DOC-05` (SRM 51-40). |
| **`TC-SQ-04`** | `TC-SQ-04_deterministic_physics_and_tool_integrity` | **UC3** | `run_asip_miners_rule_engine` | Deterministic Palmgren-Miner damage $\Delta D = 0.0042$, yield $104.2\%$, Hole #14 $0.012\text{ in} < 0.015\text{ in}$. |
| **`TC-SQ-05`** | `TC-SQ-05_multiturn_contextual_followup_tailswap` | **UC1** | `recommend_tail_swap_and_replenishment` | Multi-turn contextual tail-swap (`ZM151` → `ZM154`) and supply replenishment alert (`1680-01-619-4821`). |
| **`TC-LP-00`** | `uc0_tc_lp_00_text_to_sql_latency_and_csv_export` | **UC0** | `execute_maintenance_sql` | `< 2.0s` Text-to-SQL aggregation (`GROUP BY squadron, aircraft_status`), Spreadsheet Card formatting, and GCS `.csv` export. |
| **`TC-LP-01`** | `TC-LP-01_root_orchestrator_intent_routing_sla` | **Root** | `fast_path_before_model_callback` | `< 450ms` (`< 5ms` fast-path) root orchestrator health/greeting interception. |
| **`TC-LP-02`** | `TC-LP-02_uc1_parallel_bq_and_vegalite_chart_sla` | **UC1** | `check_actuator_fatigue_and_depot_inventory` | `< 2.5s` partition-pruned BigQuery join and dual Vega-Lite v5 chart generation. |
| **`TC-LP-03`** | `TC-LP-03_uc2_hybrid_grounded_search_sla` | **UC2** | `search_technical_manuals_and_repair_logs` | `< 2.0s` single-pass (`pageSize=15`) Discovery Engine `eu` grounded search. |
| **`TC-LP-04`** | `TC-LP-04_uc3_four_way_parallel_fanout_sla` | **UC3** | `run_parallel_airworthiness_assessment` | `< 3.5s` 4-way parallel ASIP diagnostic fan-out. |
| **`TC-LP-05`** | `TC-LP-05_uc3_sar_form700_two_turn_hitl_release` | **UC3** | `generate_form700_airworthiness_package` | Two-turn HITL Form 700 release gate (`PENDING_HITL_REVIEW` → `CONFIRMED_BY_ENGINEER`). |

## Invariants
- All tests must pass before phase 3 integration merge.
- Quality score threshold >= 0.85; Latency targets strictly enforced.
- Consult [`docs/issues/INDEX.md`](../docs/issues/INDEX.md) before modifying test or evaluation harnesses, and log any newly discovered/resolved regression or evaluation issue in [`docs/issues/`](../docs/issues/) using [`docs/issues/TEMPLATE.md`](../docs/issues/TEMPLATE.md) alongside a corresponding regression test.
