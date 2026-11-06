---
issue_id: "ISS-015"
title: "Operational Capability Response Refactor, Master Storyboard (`DEMO_STORYBOARD.md`) Alignment Across All 6 Prompts & Section 3, Clean Spare Tail `ZM154` Reassignment, and `SELECT DISTINCT` Readiness Deduplication"
date: "2026-11-05"
status: "VERIFIED_IN_PROD"
severity: "P1-MAJOR"
domain:
  - "Coordinator"
  - "UC0-Maintenance-Data"
  - "UC1-Analytics"
  - "UC2-JTD-Search"
  - "Infra-EU"
  - "Eval-QA"
sub_agent: "f35_sustainment_coordinator"
guardrails_impacted:
  - "REG-01"
  - "PERF-01"
  - "PERF-05"
  - "PERF-07"
  - "UX-01..03"
vv_test_cases:
  - "TC-SQ-00"
  - "TC-SQ-00.1"
  - "TC-SQ-00.5"
  - "TC-SQ-01"
  - "TC-SQ-02"
  - "TC-LP-00"
  - "TC-LP-01"
  - "TC-LP-02"
  - "TC-LP-03"
commit_or_pr: "HEAD"
author: "Antigravity Multi-Agent Team (ISS-015)"
---

# [ISS-015] Operational Capability Response Refactor, Master Storyboard (`DEMO_STORYBOARD.md`) Alignment Across All 6 Prompts & Section 3, Clean Spare Tail `ZM154` Reassignment, and `SELECT DISTINCT` Readiness Deduplication

> **Quick Reference Summary:** Aligned the F-35 Fleet Sustainment Agent Platform (`f35-sustainment-agent`) 100% with the Master Storyboard (`DEMO_STORYBOARD.md`) by updating the Tier 1/2 `< 5 ms` capability fast-path and Discovery Engine `eu` agent description (`1346484961578743940`) to return the Carrier Strike Group elevator pitch and 3 Core Capabilities (Purpose & Operational Benefit); expanding Prompt 1 (`UC 0`) SQL canonicalization (`Rule 5`) to include both `PRIORITY_1_RED_X` and `PRIORITY_2_URGENT` active work orders (`10` rows including `WO-2026-88401` and `WO-2026-88402` on `ZM151`); reassigning unscheduled radar fault `PHM-2026-99112` from spare tail `ZM154` to `ZM158` (`HMS Prince of Wales`) so `ZM154` is 100% fault-free in Prompt 2 (`UC 0.1`); aligning Prompt 3 (`UC 0.5`) 6-column shift readiness join, Prompts 4 & 5 (`UC 1A`/`1B`) `07:30Z` sortie departure, Prompt 6 (`UC 2`) `DOC-01`/`DOC-02`/`DOC-09` citations, and Section 3 (`"Tell me what tails on Lizzy are fit to fly"`) via `Rule 7: DISTINCT_TAIL_READINESS_DEDUPLICATION` (`5` FMC tails).

---

## 1. Symptom & Operational Context

### 1.1 Observed Failure / Degradation
1. **Issue 1 — Operational Capability Response & Agent Description Drift (`R1`):**
   - **Symptom:** Querying `"What is your operational capability?"` or `"Describe your operational capability"` returned an older capability summary without the structured `3 Core Capabilities: Purpose & Operational Benefit` format, and `root_agent.description` in `app/agent.py` had been truncated to `"AI decision-support coordinator for the UK F-35 Lightning II fleet."` instead of the full Carrier Strike Group elevator pitch.
   - **Impact:** Executive demonstrations starting with `"What is your operational capability?"` did not surface the Carrier Strike Group elevator pitch or the 3 Core Capabilities (`Conversational Maintenance Operations & Shift Resource Management`, `Predictive Fleet Readiness, Supply Chain Synchronization & Sortie Protection`, `Grounded Technical Publication Retrieval & Coalition Fleet Memory`) with their explicit `*Core Purpose*` and `*Operational Benefit*` bullets.
2. **Issue 2 — Master Storyboard (`DEMO_STORYBOARD.md`) Alignment Gaps Across Prompts 1–6 & Section 3 (`R2`):**
   - **Prompt 1 (`UC 0` — Urgent & Grounded CSG Triage):** `UC0_SYSTEM_INSTRUCTION` and `canonicalize_maintenance_sql` (`Rule 5`) filtered urgent/grounded triage queries strictly to `priority = 'PRIORITY_1_RED_X'` (`6` rows), omitting `ZM151`'s two `PRIORITY_2_URGENT` work orders (`WO-2026-88401` at `4.5 hrs` Actuator Over-Hour Limit and `WO-2026-88402` at `2.5 hrs` Canopy Latch Binding) required by `DEMO_STORYBOARD.md` (`10` active Urgent + Red-X work orders).
   - **Prompt 2 (`UC 0.1` — Spare Tail `ZM154` Cleanliness):** `DEMO_STORYBOARD.md` line 178 requires Prompt 2 (`WHERE tail_number = 'ZM151' OR linked_work_order_id IS NULL`) to confirm spare tail `ZM154` is clean (`0` unscheduled fault rows). However, `PHM-2026-99112` (`linked_work_order_id: None`) was assigned to `ZM154` in `app/seed_data/bq_seed_records.py`, causing `ZM154` to appear in unscheduled fleet health warnings.
   - **Prompt 3 (`UC 0.5` — Shift Readiness 6-Column Join):** Needed deterministic 6-column projection (`wo.work_order_id, wo.tail_number, res.required_special_tool_id, res.tool_calibration_status, res.qar_inspector_available, res.bay_dispatch_status`) for open work orders.
   - **Prompts 4 & 5 (`UC 1A` / `UC 1B` — Sortie `SRT-MAR-20261103-01` Departure Time):** `bq_seed_records.py` and `chart_painter.py` listed `06:30Z` instead of `DEMO_STORYBOARD.md`'s `07:30Z` (`2026-11-03T07:30:00Z`).
   - **Prompt 6 (`UC 2` — Allied Fleet Memory & S1000D Tooling Callout):** `UC2_SYSTEM_INSTRUCTION` needed explicit anchors for Digital Micro-Torque Spanner `JTD-53-30-T14`, `18.5 N·m` bellcrank pivot pin torque, and `0.020–0.035 in` roller clearance (`DOC-01`), USMC `VMFA-211` cured `PR-1776M` silicon sealant debris (`DOC-02`), and `DOC-09`.
   - **Section 3 (`"Tell me what tails on Lizzy are fit to fly"`):** Without `SELECT DISTINCT`, querying `maintenance_work_orders` for `base_location = 'HMS Queen Elizabeth' AND aircraft_status = 'FMC'` returned `15` historical work-order rows instead of the `5` distinct mission-capable aircraft tails (`ZM166`, `ZM172`, `ZM136`, `ZM142`, `ZM148`).

### 1.2 Reproduction Steps / Triggering Input
1. **Environment:** `GOOGLE_CLOUD_PROJECT=antig-dave`, `GOOGLE_CLOUD_REGION=europe-west1`, BigQuery (`EU`), Discovery Engine (`eu`).
2. **Queries:**
   ```text
   What is your operational capability?
   What are our most urgent maintenance jobs and grounded aircraft across the Carrier Strike Group right now, ordered by how long they will take to fix?
   What faults or pilot-reported issues were raised on ZM151 after its last flight, and are there any fleet-wide health warnings that haven't been scheduled for repair yet?
   Which of our open maintenance jobs are ready to start on this shift, and which ones are held up waiting for certified technicians, an inspector, or calibrated tools?
   Check RAF Marham F-35 horizontal tail actuator hours against our 30-day spare parts stock, and recommend an aircraft swap for morning sortie SRT-MAR-20261103-01.
   Render the full Executive Briefing Dashboard for my presentation slide deck.
   On ZM151, our night-sortie pilot reported a stiff canopy release handle that hesitated to latch, with no fault codes logged on the jet. Have allied squadrons seen this before, and what is the approved fix?
   Tell me what tails on Lizzy are fit to fly
   ```

---

## 2. Root Cause Analysis (RCA)

### 2.1 Primary Root Cause
1. **Capability Fast-Path & Agent Metadata (`app/callbacks.py`, `app/agent.py`):** `_FAST_PATH_CAPABILITY_RESPONSE` in `app/callbacks.py` had not been updated to the structured `3 Core Capabilities: Purpose & Operational Benefit` format, and `root_agent.description` in `app/agent.py` had been shortened during `ISS-014` UC3 removal.
2. **SQL Canonicalizer Rule 5 Over-Pruning (`app/tools/uc0_maintenance.py`):** `Rule 5: URGENT_AND_GROUNDED_TRIAGE_ALIGNMENT` rewrote combined `"urgent maintenance jobs and grounded aircraft"` queries to `priority = 'PRIORITY_1_RED_X'`, which excluded `PRIORITY_2_URGENT` rows (`WO-2026-88401` and `WO-2026-88402` on `ZM151`).
3. **Seed Data Contradiction on Spare Tail `ZM154` (`app/seed_data/bq_seed_records.py`):** `PHM-2026-99112` (`linked_work_order_id: None`) was seeded on `ZM154`, conflicting with the Act 1 → Act 2 narrative arc where `ZM154` is verified clean in Prompt 2 before being selected as the serviceable spare tail for `SRT-MAR-20261103-01` in Prompt 4.
4. **Missing `SELECT DISTINCT` Promotion for Tail-Level Readiness Queries (`app/tools/uc0_maintenance.py`):** Because `maintenance_work_orders` stores multiple work orders per tail (`100` rows across the fleet), tail-level status queries that omit `work_order_id` require `SELECT DISTINCT` to return one row per aircraft tail (`5` FMC tails on `HMS Queen Elizabeth`).

### 2.2 Architectural Guardrail / Invariant Analysis
| Guardrail / Test ID | Pre-Fix State | Post-Fix State | Notes |
| :--- | :---: | :---: | :--- |
| **`REG-01`** | `✅ COMPLIANT` | `✅ COMPLIANT` | BigQuery (`EU`), Discovery Engine (`eu`), and Agent Runtime (`europe-west1`) updated in-region. |
| **`PERF-01` / `PERF-05`** | `✅ COMPLIANT` | `✅ COMPLIANT` | `< 5 ms` capability fast-path interception preserved in `before_model_callback`. |
| **`TC-SQ-00` / `TC-SQ-00.1` / `TC-SQ-00.5`** | `❌ DEGRADED` | `✅ COMPLIANT` | Prompt 1 (`10` rows with `WO-2026-88401` & `WO-2026-88402`), Prompt 2 (`ZM154` clean, `PHM-2026-99112` on `ZM158`), Prompt 3 (`6` cols), and Section 3 (`5` FMC tails on `HMS Queen Elizabeth`) aligned with `DEMO_STORYBOARD.md`. |
| **`TC-SQ-01` / `TC-SQ-02`** | `⚠️ DRIFT` | `✅ COMPLIANT` | `SRT-MAR-20261103-01` departure aligned to `07:30Z`; `UC2_SYSTEM_INSTRUCTION` explicitly anchors `DOC-01` (`JTD-53-30-T14`, `18.5 N·m`, `0.020–0.035 in`), `DOC-02` (`VMFA-211` `PR-1776M`), and `DOC-09`. |

---

## 3. Fix & Code Changes Applied

### 3.1 Summary of Resolution
1. **Layer 1 — Coordinator & Fast-Path (`app/callbacks.py`, `app/agent.py`):**
   - Updated `_FAST_PATH_CAPABILITY_RE` and `_FAST_PATH_CAPABILITY_RESPONSE` in `app/callbacks.py` to return the verbatim UK F-35 Carrier Strike Group elevator pitch and `### 3 Core Capabilities: Purpose & Operational Benefit`.
   - Restored `root_agent.description` in `app/agent.py` and added fallback capability and Section 3 comparison instructions to `COORDINATOR_INSTRUCTION`.
2. **Layer 2 — Sub-Agent Instructions & SQL Canonicalizer (`app/sub_agents/uc0_maintenance_agent.py`, `app/sub_agents/uc2_search_agent.py`, `app/tools/uc0_maintenance.py`):**
   - Updated `UC0_SYSTEM_INSTRUCTION` and `canonicalize_maintenance_sql` `Rule 5` (`URGENT_AND_GROUNDED_TRIAGE_ALIGNMENT`) to expand urgent/grounded triage queries to `work_order_status != 'COMPLETED' AND priority IN ('PRIORITY_1_RED_X', 'PRIORITY_2_URGENT') ORDER BY estimated_mttr_hours DESC` (`10` rows), while preserving single-priority `PRIORITY_1_RED_X` when the user explicitly requests `"Priority-1"` / `"P1"` / `"Red-X only"`.
   - Added `Rule 7: DISTINCT_TAIL_READINESS_DEDUPLICATION` in `app/tools/uc0_maintenance.py` to promote `SELECT` to `SELECT DISTINCT` on tail-level readiness projections from `maintenance_work_orders`.
   - Updated `UC0_SYSTEM_INSTRUCTION` for Prompt 2, Prompt 3, and Section 3 (`"Tell me what tails on Lizzy are fit to fly"`), and updated `UC2_SYSTEM_INSTRUCTION` for Prompt 6 (`DOC-01`, `DOC-02`, `DOC-09`).
3. **Layer 3 — Seed Data & Chart Painter (`app/seed_data/bq_seed_records.py`, `app/tools/chart_painter.py`):**
   - Reassigned `PHM-2026-99112` (`linked_work_order_id: None`, `cnd_flag: True`) from `ZM154` to `ZM158` (`809 NAS (The Immortals)`, `HMS Prince of Wales`, `SRT-PWLS-20261103-01`), keeping `PHM-2026-99106` (linked to `COMPLETED` `WO-2026-88406`) on `ZM154` for foreign-key integrity.
   - Updated `SRT-MAR-20261103-01` `scheduled_departure_utc` to `"2026-11-03T07:30:00Z"` and `chart_painter.py` banner to `SORTIE ON-TIME (07:30Z)`.
4. **Layer 4 & 5 — Unit Tests & Cloud Deployment (`tests/unit/`, BigQuery `EU`, Discovery Engine `eu`, Reasoning Engine `europe-west1`):**
   - Updated unit tests in `tests/unit/test_semantic_sql_guardrails.py`, `tests/unit/test_adversarial_issues_1_to_8.py`, and `tests/unit/test_deterministic.py`.
   - Re-seeded BigQuery `EU` (`antig-dave.ukd_f35_sustainment_demo`) and GCS (`gs://antig-dave-f35-staging-europe-west1`), patched Discovery Engine `eu` agent `1346484961578743940`, enforced `uv.lock` public PyPI hygiene (`0` `airlock-proxy` references), and redeployed Reasoning Engine `5022570215192395776` in `europe-west1`.

### 3.2 Modified Files & Symbols
| File Path | Symbol / Function / Class Modified | Change Type | Description |
| :--- | :--- | :---: | :--- |
| `[app/callbacks.py](../../app/callbacks.py)` | `_FAST_PATH_CAPABILITY_RE`, `_FAST_PATH_CAPABILITY_RESPONSE` | `Modified` | Updated capability regex and response with CSG elevator pitch + 3 Core Capabilities |
| `[app/agent.py](../../app/agent.py)` | `root_agent.description`, `COORDINATOR_INSTRUCTION` | `Modified` | Restored full CSG elevator pitch and added Section 3 routing/comparison rules |
| `[app/sub_agents/uc0_maintenance_agent.py](../../app/sub_agents/uc0_maintenance_agent.py)` | `UC0_SYSTEM_INSTRUCTION` | `Modified` | Aligned SQL templates for Prompts 1, 2, 3, and Section 3 (`Lizzy fit to fly`) |
| `[app/tools/uc0_maintenance.py](../../app/tools/uc0_maintenance.py)` | `canonicalize_maintenance_sql` (Rules 5 & 7) | `Modified` | Updated `URGENT_AND_GROUNDED_TRIAGE_ALIGNMENT` to include `PRIORITY_2_URGENT` and added `DISTINCT_TAIL_READINESS_DEDUPLICATION` |
| `[app/seed_data/bq_seed_records.py](../../app/seed_data/bq_seed_records.py)` | `_BASE_SQUADRON_SORTIE_SCHEDULE_ROWS`, `_BASE_PHM_BIT_FAULT_EVENTS_ROWS` | `Modified` | Set `SRT-MAR-20261103-01` departure to `2026-11-03T07:30:00Z`; reassigned `PHM-2026-99112` to `ZM158` |
| `[app/tools/chart_painter.py](../../app/tools/chart_painter.py)` | `render_executive_dashboard_chart` | `Modified` | Updated sortie banner timestamp from `06:30Z` to `07:30Z` |
| `[app/sub_agents/uc2_search_agent.py](../../app/sub_agents/uc2_search_agent.py)` | `UC2_SYSTEM_INSTRUCTION` | `Modified` | Added explicit `DOC-01` (`JTD-53-30-T14`, `18.5 N·m`, `0.020–0.035 in`), `DOC-02` (`VMFA-211` `PR-1776M`), and `DOC-09` callouts |
| `[tests/unit/test_semantic_sql_guardrails.py](../../tests/unit/test_semantic_sql_guardrails.py)` | `TestIssueDocumentCSGExactReproduction`, `TestCrossTableWarehouseConsistency` | `Modified` | Updated Prompt 1 10-row assertions and added Prompt 2, Prompt 3, Prompt 4/5, and Section 3 unit tests |
| `[tests/unit/test_adversarial_issues_1_to_8.py](../../tests/unit/test_adversarial_issues_1_to_8.py)` | Capability, description & UC2 instruction tests | `Modified` | Added assertions for R1 capability pitch, `root_agent.description`, and R2.5 UC2 citations |
| `[tests/unit/test_deterministic.py](../../tests/unit/test_deterministic.py)` | `test_fast_path_intercepts_operational_capability_query_under_5ms` | `Modified` | Updated capability fast-path assertions to match R1 format |

---

## 4. Dead Ends & Approaches Rejected

> [!WARNING]
> **Do Not Repeat These Approaches:** Future agents and engineers modifying these files must avoid the rejected approaches documented below.

| Rejected Approach | Why It Failed or Was Rejected | Guardrail / Constraint Violated |
| :--- | :--- | :--- |
| Reassigning `PHM-2026-99106` (in addition to `PHM-2026-99112`) away from `ZM154` | `PHM-2026-99106` is linked to `COMPLETED` work order `WO-2026-88406` on `ZM154`; moving it breaks `TestCrossTableWarehouseConsistency::test_phm_linked_work_order_foreign_key_and_tail_match`. Only unlinked `PHM-2026-99112` (`linked_work_order_id: None`) needed reassignment to `ZM158`. | Cross-Table FK Integrity Invariant |
| Unconditionally rewriting all `priority = 'PRIORITY_1_RED_X'` queries in `Rule 5` to `IN ('PRIORITY_1_RED_X', 'PRIORITY_2_URGENT')` | Breaks explicit Priority-1 / Red-X queries (e.g., `"Show me all open Priority-1 Red-X work orders"`). `Rule 5` must inspect `explicit_p1_re` and preserve single-priority `PRIORITY_1_RED_X` when explicitly requested. | Semantic SQL Precision Invariant |
| Running bare `uv run pytest` without `--frozen` prior to `agents-cli deploy` | Rewrites `uv.lock` with corporate internal `http://airlock-proxy.uplink.goog:999/...` URLs, causing Vertex AI Reasoning Engine Cloud Build (`uv sync`) to fail with `Connection refused (os error 111)`. Always use `.venv/bin/pytest` / `.venv/bin/python` and verify `grep -c "airlock-proxy" uv.lock` is `0`. | `REG-01` / Cloud Build PyPI Invariant (`ISS-007`, `ISS-012`) |

---

## 5. Verification, Regression Tests & Benchmarks

### 5.1 Automated Test & Live Cloud Verification
```bash
# 1. Deterministic Unit & 5-Tier E2E Test Suite (383 passed)
.venv/bin/pytest tests/unit/ tests/e2e/ -q

# 2. Lockfile Public PyPI Hygiene Verification
grep -c "airlock-proxy" uv.lock || true   # 0
grep -c "https://pypi.org/simple" uv.lock # 221
```

### 5.2 Before vs. After Telemetry / Verification Metrics
| Metric / Check | Pre-Fix Baseline | Post-Fix Result | Target / SLA Gate | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| **Full Unit + 5-Tier E2E Suite (`pytest`)** | `365 passed` | **`383 passed, 0 failed` (`26.72s`)** | `100% Pass` | **✅ PASS** |
| **Capability Fast-Path (`"What is your operational capability?"`)** | Legacy summary | **CSG Elevator Pitch + 3 Core Capabilities (`< 5 ms`)** | `< 5 ms` (`PERF-05`) | **✅ PASS** |
| **Prompt 1 (`UC 0`) Urgent & Grounded CSG Triage** | `6` rows (omitted `WO-2026-88401` & `WO-2026-88402`) | **`10` rows (`WO-2026-88401`, `WO-2026-88402`, `WO-2026-88403` on `ZM151` included)** | `10` active Red-X + Urgent rows | **✅ PASS** |
| **Prompt 2 (`UC 0.1`) Spare Tail `ZM154` Fault Rows** | `1` unscheduled fault (`PHM-2026-99112` on `ZM154`) | **`0` rows on `ZM154` (`PHM-2026-99112` on `ZM158`, `HMS Prince of Wales`)** | `ZM154` 100% clean | **✅ PASS** |
| **Prompts 4 & 5 (`UC 1A`/`1B`) `SRT-MAR-20261103-01` Departure** | `2026-11-03T06:30:00Z` | **`2026-11-03T07:30:00Z` (`07:30Z` banner)** | `07:30Z` Storyboard parity | **✅ PASS** |
| **Section 3 (`"Tell me what tails on Lizzy are fit to fly"`)** | `15` un-deduplicated rows | **`5` distinct FMC tails (`ZM166`, `ZM172`, `ZM136`, `ZM142`, `ZM148`)** | `5` distinct FMC tails | **✅ PASS** |
| **BigQuery `EU` (`ukd_f35_sustainment_demo`) Re-Seed** | Pre-ISS-015 seed | **`6` tables × `100` rows = `600` rows verified in `EU`** | `600` rows (`REG-01`) | **✅ PASS** |
| **Discovery Engine `eu` Agent `1346484961578743940`** | Truncated description | **Patched `description` + `toolDescription` + RAF F-35 icon (`34,988` bytes)** | Full CSG pitch (`REG-01`) | **✅ PASS** |
| **Reasoning Engine `5022570215192395776` (`europe-west1`) `:streamQuery` Smoke Verification** | Pre-ISS-015 runtime | **`8/8` Prompts HTTP 200 (`missing=[]` across Capability, Prompts 1–6, and Section 3 `Lizzy` FMC; Operation `5330346403392651264`)** | `8/8` Storyboard Prompts Verified (`REG-01`) | **✅ PASS** |

---

## 6. Prevention & Guardrail Updates

- [x] **Regression Tests Added:** Updated and added unit tests in `tests/unit/test_semantic_sql_guardrails.py`, `tests/unit/test_adversarial_issues_1_to_8.py`, and `tests/unit/test_deterministic.py` (`383 passed` across unit + E2E suites).
- [x] **Index Updated:** Registered `ISS-015` in [`docs/issues/INDEX.md`](./INDEX.md) across Section 1 (Chronological Log), Section 2 (Domain Lookup), and Section 3 (Guardrail & V&V Lookup).
- [x] **Cloud Infrastructure Synced:** Re-seeded BigQuery `EU`, patched Discovery Engine `eu` agent `1346484961578743940`, and redeployed Reasoning Engine `5022570215192395776` in `europe-west1` (verified via live `:streamQuery` session `5947506609390354432`).
