---
issue_id: "ISS-008"
title: "UC0 Conversational Maintenance Data Text-to-SQL Sub-Agent, BigQuery Table & Column Descriptions, and Interactive Spreadsheet Card with GCS CSV Export"
date: "2026-11-04"
status: "RESOLVED"
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
  - "TC-LP-00"
commit_or_pr: "HEAD"
author: "edwardsda"
---

# [ISS-008] UC0 Conversational Maintenance Data Text-to-SQL Sub-Agent, BigQuery Table & Column Descriptions, and Interactive Spreadsheet Card with GCS CSV Export

> **Quick Reference Summary:** Implemented **UC0 (`@F35-Maintenance-Data`)** by provisioning **Table 7 (`maintenance_work_orders`)** in `antig-dave.ukd_f35_sustainment_demo` (`location="EU"`) with semantic table and 18-column descriptions, adding `f35_maintenance_data_agent` (`gemini-3.8-flash`, `thinking_level="LOW"`) and `execute_maintenance_sql`, rendering an Excel / Google Sheets-like Spreadsheet Card (`A`–`R` column headers, status badges, `=COUNTA()` / `=SUM()` / `=AVERAGE()` formula bar), and cutting live EU tool execution latency from `762.1 ms` to `344.4 ms` via `client.query_and_wait(use_query_cache=True)` and non-blocking background GCS `.csv` export.

---

## 1. Symptom & Operational Context

### 1.1 Observed Requirement & Latency Baseline
- **Requirement:** Provide a foundational conversational **Text-to-SQL** entry point (**UC0: "Act 0: Morning Maintenance Stand-Up"**) over Lockheed Martin ODIN / UK MOD Form 707A Aircraft Maintenance Log Work Orders (`maintenance_work_orders` in BigQuery `EU`), returning an interactive Excel / Google Sheets-like Card with an authenticated clickable `.CSV` download link (`https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/exports/...`).
- **Metadata Persistence Requirement:** `bq_client.load_table_from_json(..., write_disposition=WRITE_TRUNCATE)` resets table-level descriptions unless `updated_table.schema` and `updated_table.description` are explicitly re-applied via `bq_client.update_table(updated_table, ["schema", "description"])`.
- **Latency Bottleneck Observed During Initial Live EU Test:** Using two-step `client.query().result()` plus synchronous `blob.upload_from_string()` resulted in `762.1 ms` tool latency (`674.1 ms` BigQuery + `88.0 ms` synchronous GCS upload).

### 1.2 Reproduction Steps / Triggering Input
1. **Environment:** `GOOGLE_CLOUD_PROJECT=antig-dave`, `GOOGLE_CLOUD_REGION=europe-west1`, BigQuery (`EU`), GCS (`gs://antig-dave-f35-staging-europe-west1`).
2. **Query:**
   ```text
   @F35-Maintenance-Data Show me all open maintenance work orders across RAF Marham and HMS Queen Elizabeth ordered by priority, including aircraft status, WUC code, subsystem, awaiting NSN, and logged man-hours.
   ```
3. **Observed vs. Expected Behavior:**
   - **Expected:** Sub-second (`< 350 ms`) BigQuery `EU` execution via `query_and_wait`, non-blocking `.csv` upload to `gs://antig-dave-f35-staging-europe-west1/exports/`, and full table + 18 column descriptions persisted in live BigQuery metadata.

---

## 2. Root Cause Analysis (RCA)

### 2.1 Primary Root Cause
1. **BigQuery `WRITE_TRUNCATE` Metadata Overwrite:** In `scripts/setup_demo_infra.py`, `load_table_from_json` with `WriteDisposition.WRITE_TRUNCATE` replaces the destination table state; both `updated_table.schema = schema` and `updated_table.description = description` must be explicitly pushed via `bq_client.update_table(updated_table, ["schema", "description"])` after `load_job.result()`.
2. **Synchronous Job Polling & GCS Upload Latency:** Standard `client.query(sql).result()` performs `jobs.insert` followed by `jobs.getQueryResults`, while `client.query_and_wait(sql, job_config=QueryJobConfig(use_query_cache=True))` uses the fast-path `jobs.query` RPC (~340 ms in `EU`). Additionally, running `blob.upload_from_string()` synchronously blocked tool completion by ~88 ms even though the deterministic authenticated browser URL (`https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/exports/<sheet_title>.csv`) is known immediately.

### 2.2 Architectural Guardrail / Invariant Analysis
| Guardrail / Test ID | Pre-Fix State | Post-Fix State | Notes |
| :--- | :---: | :---: | :--- |
| **`REG-01`** | `N/A (New Table 7)` | `✅ COMPLIANT` | `antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders` provisioned in `EU` and CSV exports stored in `gs://antig-dave-f35-staging-europe-west1/exports/`. |
| **`PERF-01` & `PERF-07`** | `⚠️ 762.1 ms` | `✅ 344.4 ms` | Pre-warmed `bq_client` (`credentials=_cached_credentials`), `query_and_wait(use_query_cache=True)`, and daemon background thread for GCS CSV upload. |
| **`TC-SQ-00` & `TC-LP-00`** | `N/A (New UC0)` | `✅ PASS` | Added 5 deterministic unit tests in `test_deterministic.py` and V&V scenarios in `vv_golden_suite.json` & `basic-dataset.json`. |

---

## 3. Fix & Code Changes Applied

### 3.1 Summary of Resolution
1. **Table 7 Declarative Schema & Seed Data:** Created `app/seed_data/schemas/maintenance_work_orders.schema.json` (`DAY` partitioned on `created_at_utc`, clustered on `["tail_number", "aircraft_status"]`) with rich semantic table and 18-column descriptions, plus 14 UK Lightning Force ODIN / MOD Form 707A work orders (`WO-2026-88401`..`WO-2026-88414`) in `app/seed_data/bq_seed_records.py`.
2. **Pure Dynamic Text-to-SQL Specialist (`f35_maintenance_data_agent`):** Created `app/sub_agents/uc0_maintenance_agent.py` and `app/tools/uc0_maintenance.py` (`execute_maintenance_sql`), enforcing read-only `SELECT` validation, `query_and_wait` execution in BigQuery `EU` (with `< 1 ms` in-memory SQLite fallback), pre-formatted `spreadsheet_card_markdown`, and background `.csv` export to GCS.
3. **Frontend Component (`MaintenanceSheetCard.tsx`):** Added `packages/web/components/MaintenanceSheetCard.tsx` rendering the interactive Excel / Google Sheets grid (`A`..`R` column headers, `fx` formula bar, status pills, `=COUNTA()` / `=SUM()` / `=AVERAGE()` footer, and clickable `.CSV` download button).

### 3.2 Modified Files & Symbols
| File Path | Symbol / Function / Class Modified | Change Type | Description |
| :--- | :--- | :---: | :--- |
| `[maintenance_work_orders.schema.json](../../app/seed_data/schemas/maintenance_work_orders.schema.json)` | `maintenance_work_orders` | `Added` | Declarative BigQuery schema with table description and 18 column descriptions. |
| `[bq_seed_records.py](../../app/seed_data/bq_seed_records.py)` | `MAINTENANCE_WORK_ORDERS_ROWS` | `Modified` | Added 14 ODIN / MOD Form 707A maintenance work orders across `617 Sqn`, `809 NAS`, and `207 Sqn`. |
| `[uc0_maintenance.py](../../app/tools/uc0_maintenance.py)` | `execute_maintenance_sql` | `Added` | Read-only SQL validator, BigQuery `EU` `query_and_wait` executor, Spreadsheet Card formatter, and CSV exporter. |
| `[uc0_maintenance_agent.py](../../app/sub_agents/uc0_maintenance_agent.py)` | `f35_maintenance_data_agent` | `Added` | UC0 specialist ADK 2.0 `LlmAgent` (`@F35-Maintenance-Data`). |
| `[MaintenanceSheetCard.tsx](../../packages/web/components/MaintenanceSheetCard.tsx)` | `MaintenanceSheetCard` | `Added` | Interactive Excel / Google Sheets grid component with formula bar and CSV download link. |
| `[setup_demo_infra.py](../../scripts/setup_demo_infra.py)` | `ensure_bigquery_dataset_and_tables` | `Modified` | Persists both `schema` (column descriptions) and `description` (table description) after `WRITE_TRUNCATE` load job. |
| `[test_deterministic.py](../../tests/unit/test_deterministic.py)` | `test_uc0_*` | `Modified` | Added 5 deterministic unit tests covering schema descriptions, seed records, spreadsheet card rendering, SQL aggregations, and DML/DDL blocking. |

---

## 4. Dead Ends & Approaches Rejected

> [!WARNING]
> **Do Not Repeat These Approaches:** Future agents and engineers modifying these files must avoid the rejected approaches documented below.

| Rejected Approach | Why It Failed or Was Rejected | Guardrail / Constraint Violated |
| :--- | :--- | :--- |
| Letting the LLM format raw JSON rows into a Markdown table token-by-token | Generating a 14-row × 12-column Markdown table via LLM output tokens adds 800–1,200 output tokens (~2.5s generation latency). Returning pre-formatted `spreadsheet_card_markdown` from `execute_maintenance_sql` reduces synthesis latency to `< 0.8s`. | `PERF-05`, `TC-LP-00` |
| Relying only on `create_table(table_obj)` without post-load `update_table(updated_table, ["schema", "description"])` | `load_table_from_json` with `WRITE_TRUNCATE` can overwrite table-level descriptions on existing tables unless `update_table` explicitly includes `"description"` alongside `"schema"`. | BigQuery Metadata Integrity |

---

## 5. Verification, Regression Tests & Benchmarks

### 5.1 Automated Test & Evaluation Verification
```bash
# 1. Deterministic Unit Test Suite (including UC0 tests)
uv run pytest tests/unit/ -q

# 2. Live BigQuery EU Metadata & Latency Verification
uv run python scripts/setup_demo_infra.py --skip-discovery
```

### 5.2 Before vs. After Telemetry / Verification Metrics
| Metric / Check | Pre-Fix Baseline | Post-Fix Result | Target / SLA Gate | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| **Live BigQuery `EU` `execute_maintenance_sql` Latency** | `762.1 ms` | `344.4 ms` (`341.7 ms` BQ) | `< 450 ms` | **✅ PASS** |
| **Local Fallback (`SQLITE_IN_MEMORY_FALLBACK`) Latency** | `N/A` | `0.85 ms` | `< 10 ms` | **✅ PASS** |
| **BigQuery Table & 18 Column Descriptions Populated** | `0 / 18` | `18 / 18 + Table Desc` | `100%` | **✅ PASS** |
| **Unit Test Suite (`tests/unit/`)** | `168 passed` | `173 passed` | `100% Pass` | **✅ PASS** |

---

## 6. Prevention & Guardrail Updates

- [x] **Regression Test Added:** Added `test_uc0_maintenance_schema_has_table_and_column_descriptions`, `test_uc0_seed_records_match_schema`, `test_uc0_execute_maintenance_sql_spreadsheet_card_and_csv_link`, `test_uc0_execute_maintenance_sql_aggregation_query`, and `test_uc0_execute_maintenance_sql_blocks_unsafe_dml_ddl` in `tests/unit/test_deterministic.py`.
- [x] **Index Updated:** Added `ISS-008` to [`docs/issues/INDEX.md`](./INDEX.md) under the chronological table and domain/guardrail matrices.
- [x] **Documentation / `AGENTS.md` Updated:** Updated root `AGENTS.md`, `packages/api/AGENTS.md`, `packages/web/AGENTS.md`, `tests/AGENTS.md`, `SA_F35.md`, `.agents-cli-spec.md`, `feature-spec.md`, and `DEMO_STORYBOARD.md`.
