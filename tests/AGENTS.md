# QA / Test Agent Boundary — `/tests`

> **Scope:** QA / Test Specialist Subagent  
> **Mandatory Guidelines:** Review root `AGENTS.md` and `.agents-cli-spec.md` for platform invariants.

## Responsibilities
- Unit tests (`tests/unit/test_deterministic.py`):
  - **9-Table 100-Record F-35 Data Warehouse Verification**: Asserts that all 9 BigQuery seed record lists (`AIRFRAME_COMPONENT_TELEMETRY_ROWS`, `GLOBAL_DEPOT_INVENTORY_ROWS`, `SQUADRON_SORTIE_SCHEDULE_ROWS`, `HIGH_FREQ_STRAIN_TELEMETRY_ROWS`, `AS_MAINTAINED_MBOM_FASTENERS_ROWS`, `AIRWORTHINESS_RELEASE_LEDGER_ROWS`, `MAINTENANCE_WORK_ORDERS_ROWS`, `PHM_BIT_FAULT_EVENTS_ROWS`, `WORK_CENTER_TOOLING_AND_SQEP_ROWS`) contain exactly `100` records (`900` total records), match their declarative `.schema.json` files in `app/seed_data/schemas/`, and include non-empty column `description` metadata on every column.
  - **UC 0 (`maintenance_work_orders`)**: Validates 100 seed rows (`MAINTENANCE_WORK_ORDERS_ROWS` with 10 active non-completed work orders), read-only SQL guardrail (`ValueError` on DML/DDL or unauthorized tables), Excel / Google Sheets Spreadsheet Card rendering (`=COUNTA`, `=SUM`, `=AVERAGE`), status badges (`🟡 PMC-M`, `🔴 NMC-S (MICAP)`), and authenticated GCS `.csv` export URL verification.
  - **UC 0.1 (`phm_bit_fault_events`)**: Validates PHM/BIT fault event triage via `execute_maintenance_sql`, verifying `ZM151` Health Reporting Codes (`HRC-2710-88A`, `HRC-5330-000-NONE` with `PILOT_REPORT_ONLY_NO_BIT` and `cnd_flag=True`, `HRC-5320-94G`) and unlinked PHM advisories (`linked_work_order_id IS NULL`).
  - **UC 0.5 (`work_center_tooling_and_sqep` Multi-Table `JOIN`s)**: Validates multi-table `INNER`/`LEFT JOIN` queries across `maintenance_work_orders` and `work_center_tooling_and_sqep` via `execute_maintenance_sql`, verifying special tooling (`JTD-53-30-T14`, `NDI-PAUT-496A`), calibration statuses (`EXPIRED_OUT_OF_CAL`, `CAL_DUE_WITHIN_7D`), and bay dispatch blocks (`BLOCKED_TOOL_OUT_OF_CAL`, `BLOCKED_NO_QAR_ON_SHIFT`).
  - **Live BigQuery Metadata Inspection**: Connects to `antig-dave.ukd_f35_sustainment_demo` (`location="EU"`) when credentials are available to verify table descriptions and column descriptions across all 9 tables.
  - Deterministic ASIP physics solver validation (Rainflow cycle counting, Palmgren-Miner damage $D$, MIL-HDBK-516C compliance).
  - Fastener 3D CAD coordinate matrix transformation verification (Frame 496, Hole #14).
  - Two-turn HITL Form 700 release gate enforcement (`before_tool_callback`).
  - Pydantic schema validation for UC1 charts, UC2 citations, and UC3 SAR.
- End-to-End 4-Tier Verification (`tests/e2e/`):
  - Unified verification of all 4 specialist sub-agents (`f35_maintenance_data_agent`, `f35_analytics_agent`, `f35_jtd_search_agent`, `f35_airworthiness_orchestrator`), all 9 declarative BigQuery schema files, and all evaluation datasets.
- Evaluation suite (`tests/eval/`):
  - Configuration (`tests/eval/eval_config.yaml`).
  - Smoke evaluation dataset (`tests/eval/datasets/basic-dataset.json`), covering `uc0_maintenance_work_orders_spreadsheet_card`, `uc0_1_phm_bit_fault_triage_card`, `uc0_5_multi_table_tooling_sqep_join_card`, `uc1_actuator_fatigue_and_stock`, `uc2_sticky_canopy_latch_search`, and `uc3_frame496_exceedance_and_form700_stage`.
  - V&V Golden Suite (`tests/eval/datasets/vv_golden_suite.json`) covering `TC-SQ-00`, `TC-SQ-00.1`, `TC-SQ-00.5`, `TC-SQ-01..05` (Quality) and `TC-LP-00..05` (Latency).

## V&V Test Matrix (`tests/eval/datasets/vv_golden_suite.json`)

| Test ID | Eval Case ID | Use Case | Target Tool / Capability | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **`TC-SQ-00`** | `uc0_tc_sq_00_conversational_maintenance_sql_card` | **UC0** | `execute_maintenance_sql` | Dynamic read-only Text-to-SQL over `maintenance_work_orders` returning 10 active work orders (`ZM151`: `WO-2026-88401..88403`), Spreadsheet Card (`A..R`), status badges (`🟡 PMC-M`, `🔴 NMC-S (MICAP)`), formula footer (`=COUNTA`, `=SUM`), and GCS CSV link. |
| **`TC-SQ-00.1`** | `uc0_1_tc_sq_00_1_phm_bit_fault_triage_card` | **UC0.1** | `execute_maintenance_sql` | PHM/BIT fault triage over `phm_bit_fault_events` surfacing `ZM151` HRCs (`HRC-2710-88A`, `HRC-5330-000-NONE` with `PILOT_REPORT_ONLY_NO_BIT` & `cnd_flag=True`, `HRC-5320-94G`) and unlinked advisories (`linked_work_order_id IS NULL`) with Spreadsheet Card and CSV export. |
| **`TC-SQ-00.5`** | `uc0_5_tc_sq_00_5_multi_table_tooling_sqep_join_card` | **UC0.5** | `execute_maintenance_sql` | Multi-table SQL `JOIN` across `maintenance_work_orders` and `work_center_tooling_and_sqep` surfacing special tools (`JTD-53-30-T14`, `NDI-PAUT-496A`), calibration alerts (`EXPIRED_OUT_OF_CAL`), and bay dispatch blocks (`BLOCKED_TOOL_OUT_OF_CAL`, `BLOCKED_NO_QAR_ON_SHIFT`). |
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
