---
issue_id: "ISS-011"
title: "UC 0.1 PHM/BIT Fault Triage, UC 0.5 Multi-Table SQEP/Tooling Join, 9-Table 900-Record Data Warehouse Expansion & Unified E2E Test Harness"
date: "2026-11-05"
status: "VERIFIED_IN_PROD"
severity: "P2-HIGH"
domain: "UC0-Maintenance-Data"
sub_agent: "f35_maintenance_data_agent"
guardrails_impacted:
  - "REG-01"
  - "PERF-01"
  - "PERF-05"
  - "PERF-07"
vv_test_cases:
  - "TC-SQ-00"
  - "TC-SQ-00.1"
  - "TC-SQ-00.5"
  - "TC-LP-00"
commit_or_pr: "HEAD"
author: "edwardsda"
---

# [ISS-011] UC 0.1 PHM/BIT Fault Triage, UC 0.5 Multi-Table SQEP/Tooling Join, 9-Table 900-Record Data Warehouse Expansion & Unified E2E Test Harness

> **Quick Reference Summary:** Expanded the F-35 Data Warehouse (`antig-dave.ukd_f35_sustainment_demo` in `EU`) from 7 to **9 tables** with **100 cross-table-consistent records per table (`900` total records)** and full table/column descriptions, added **UC 0.1 (`phm_bit_fault_events` post-sortie PHM/BIT & CND triage)** and **UC 0.5 (`work_center_tooling_and_sqep` 2- and 3-table SQL `JOIN`s)** to [`f35_maintenance_data_agent`](../../app/sub_agents/uc0_maintenance_agent.py) and [`execute_maintenance_sql`](../../app/tools/uc0_maintenance.py), enhanced [`MaintenanceSheetCard.tsx`](../../packages/web/components/MaintenanceSheetCard.tsx) with PHM severity, CND, tool calibration, and bay dispatch badges, and unified the entire 412-test unit + E2E test harness.

---

## 1. Symptom & Operational Context

### 1.1 Observed Requirement & Test Harness Omissions
- **Data Warehouse & Use Case Expansion:** Expand Act 0 (`@F35-Maintenance-Data`) with two companion structured tables and simple conversational SQL use cases bridging UC 0 to UC 1–3:
  - **UC 0.1 (Table 8 `phm_bit_fault_events`, 100 rows):** Post-sortie PHM Health Reporting Codes (`HRCs`), `PILOT_REPORT_ONLY_NO_BIT` anomalies (`ZM151` Canopy Latch `HRC-5330-000-NONE`), chronic repeat Could Not Duplicate (`CND`) faults, and unactioned PHM advisories (`linked_work_order_id IS NULL`).
  - **UC 0.5 (Table 9 `work_center_tooling_and_sqep`, 100 rows):** Multi-table conversational SQL `JOIN` with `maintenance_work_orders` (and `phm_bit_fault_events`) to verify SQEP technician headcount, QAR inspector availability, and calibrated special tooling (`JTD-53-30-T14`, `NDI-PAUT-496A`, `LO-IR-BLANKET-04`).
  - **100-Record Cross-Warehouse Consistency:** Populate all 9 tables (`Tables 1–9`) with **100 representative, referentially consistent records per table (`900` total records)** while preserving all golden storyboard rows and column/table descriptions in BigQuery `EU`.
- **E2E Test Harness Omissions Identified:** When `f35_maintenance_data_agent` and `TC-SQ-00` were added in `ISS-008`, 9 tests in `tests/e2e/` (`test_tier1_feature_coverage.py`, `test_tier2_boundary_corner.py`, `test_tier3_cross_feature.py`, `test_tier4_real_world_scenarios.py`) still had hardcoded checks for `len(sub_agents) == 3`, 6 schema files, and `len(eval_cases) == 10`.

---

## 2. Root Cause Analysis (RCA)

### 2.1 Primary Root Cause
1. **Single-Table Constraint in `validate_and_rewrite_maintenance_sql`:** `app/tools/uc0_maintenance.py` previously allowed only `maintenance_work_orders` and lacked multi-table `JOIN` rewriting, table-alias stripping (`w.aircraft_status` -> `aircraft_status`), and dynamic `=SUM()` / `=AVERAGE()` binding for non-work-order numeric columns.
2. **Chart Series Bounding on 100-Row Tables:** Expanding `AIRFRAME_COMPONENT_TELEMETRY_ROWS` and `GLOBAL_DEPOT_INVENTORY_ROWS` from 5 and 2 rows to 100 rows each required filtering to `nsn == '1680-01-619-4821'` in `app/tools/uc1_analytics.py` and `app/tools/chart_painter.py` so Vega-Lite JSON specs and 16:9 Matplotlib executive slides remain focused on the primary actuator and regional depots.
3. **Hardcoded Pre-UC0 Counts in `tests/e2e/`:** E2E tests in Tiers 1–4 had static assertions (`== 3` sub-agents, `== 10` golden cases) rather than verifying the 4-sub-agent topology and expanded 9-schema / 14-case V&V suite.

---

## 3. Fix & Code Changes Applied

### 3.1 Modified Files & Symbols
| File Path | Symbol / Function / Class Modified | Change Type | Description |
| :--- | :--- | :---: | :--- |
| `[phm_bit_fault_events.schema.json](../../app/seed_data/schemas/phm_bit_fault_events.schema.json)` | `phm_bit_fault_events` | `Added` | Declarative BigQuery schema for Table 8 (16 described columns, `DAY` partitioned on `fault_timestamp_utc`). |
| `[work_center_tooling_and_sqep.schema.json](../../app/seed_data/schemas/work_center_tooling_and_sqep.schema.json)` | `work_center_tooling_and_sqep` | `Added` | Declarative BigQuery schema for Table 9 (16 described columns, `DAY` partitioned on `shift_updated_utc`). |
| `[bq_seed_records.py](../../app/seed_data/bq_seed_records.py)` | `BQ_SEED_TABLES` (Tables 1–9) | `Modified` | Expanded all 9 tables to 100 consistent records each (`900` total records across the F-35 Data Warehouse). |
| `[uc0_maintenance.py](../../app/tools/uc0_maintenance.py)` | `validate_and_rewrite_maintenance_sql`, `execute_maintenance_sql` | `Modified` | Multi-table SQL validator/rewriter, 300-row SQLite mirror, PHM/tooling badges, and dynamic formula footer. |
| `[uc0_maintenance_agent.py](../../app/sub_agents/uc0_maintenance_agent.py)` | `f35_maintenance_data_agent` | `Modified` | Embedded schemas and join keys for Tables 7, 8, and 9 (`UC 0`, `UC 0.1`, `UC 0.5`). |
| `[MaintenanceSheetCard.tsx](../../packages/web/components/MaintenanceSheetCard.tsx)` | `MaintenanceSheetCard` | `Modified` | Added `fault_severity`, `cnd_flag`, `tool_calibration_status`, `bay_dispatch_status`, and joined table badges. |
| `[test_deterministic.py](../../tests/unit/test_deterministic.py)` & `tests/e2e/*` | `test_uc0_1_*`, `test_uc0_5_*`, `test_all_9_warehouse_*` | `Modified` | Unified all 412 unit and E2E tests across `tests/unit/` and `tests/e2e/`. |

---

## 4. Dead Ends & Approaches Rejected

| Rejected Approach | Why It Failed or Was Rejected | Guardrail / Constraint Violated |
| :--- | :--- | :--- |
| Plotting all 100 rows of `airframe_component_telemetry` directly into `VegaLiteSpec` and `chart_painter.py` | Embedding 100 rows in inline Vega-Lite specs bloats LLM prompt tokens and overcrowds 16:9 executive slides; filtering to `nsn == '1680-01-619-4821'` preserves clean visual hierarchy. | `PERF-05`, `TC-LP-02` |
| Re-introducing `[📥 Download .CSV` links inside `spreadsheet_card_markdown` | Violates `ISS-010` (`test_uc0_no_csv_download_links_in_any_query`); CSV download URLs are returned in `spreadsheet_card.csv_download_url` while keeping Markdown tables screen-aligned and link-free. | `ISS-010` (`UX-03`) |

---

## 5. Verification, Regression Tests & Benchmarks

### 5.1 Automated Test & Evaluation Verification
```bash
# 1. Seed all 9 tables (100 rows each = 900 rows) in BigQuery EU
uv run python -c 'from scripts.setup_demo_infra import ensure_bigquery_dataset_and_tables; ensure_bigquery_dataset_and_tables("antig-dave", "EU", "ukd_f35_sustainment_demo")'

# 2. Run Complete Unified Unit + E2E Test Harness
uv run pytest tests/unit/ tests/e2e/ -q
```

### 5.2 Telemetry & Verification Metrics
| Metric / Check | Pre-Fix Baseline | Post-Fix Result | Target / SLA Gate | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| **BigQuery `EU` Tables & Records Seeded** | `7 tables` (`30 rows`) | `9 tables × 100 rows` (`900 rows`) | `9 tables × 100 rows` | **✅ PASS** |
| **BigQuery Table & Column Descriptions (`Tables 1–9`)** | `7 tables` | `9 tables` (`100% described`) | `100%` | **✅ PASS** |
| **Unified Unit + E2E Test Suite (`tests/unit/` + `tests/e2e/`)** | `9 failed in e2e` | `412 passed, 0 failed` | `100% Pass` | **✅ PASS** |
| **Production Reasoning Engine `:streamQuery` (`europe-west1`)** | `N/A` | `5022570215192395776` (`op: 5793478293197946880`, session `8760145314171584512`) | `UC 0.1 & UC 0.5 Pass` | **✅ PASS** |

---

## 6. Prevention & Guardrail Updates

- [x] **Regression Tests Added:** Added `test_all_9_warehouse_tables_have_100_records_and_schema_descriptions`, `test_uc0_1_phm_bit_fault_events_triage_and_unlinked_advisories`, and `test_uc0_5_multi_table_join_work_orders_and_tooling_sqep` in `tests/unit/test_deterministic.py`.
- [x] **Index Updated:** Registered `ISS-011` in [`docs/issues/INDEX.md`](./INDEX.md).
- [x] **Documentation Updated:** Updated `DEMO_STORYBOARD.md`, `SA_F35.md`, `feature-spec.md`, `.agents-cli-spec.md`, `AGENTS.md`, `README.md`, `packages/api/AGENTS.md`, `packages/web/AGENTS.md`, and `tests/AGENTS.md`.
