---
issue_id: "ISS-014"
title: "Decommission UC3 Agentic AI (`f35_airworthiness_orchestrator`), ASIP Physics Engine, Tables 4–6 & DOC-04..08 Across Code, Cloud Infrastructure & Documentation"
date_reported: "2026-11-05"
date_resolved: "2026-11-05"
status: "VERIFIED_IN_PROD"
severity: "P2-HIGH"
domain:
  - "Coordinator"
  - "UC0-Maintenance-Data"
  - "UC1-Analytics"
  - "UC2-JTD-Search"
  - "Infra-EU"
  - "Frontend-Web"
  - "Eval-QA"
guardrails_touched:
  - "REG-01"
  - "PERF-01"
  - "PERF-02"
  - "PERF-05"
  - "PERF-07"
vv_tests:
  - "TC-SQ-00"
  - "TC-SQ-00.1"
  - "TC-SQ-00.5"
  - "TC-SQ-01"
  - "TC-SQ-02"
  - "TC-SQ-05"
  - "TC-LP-00"
  - "TC-LP-01"
  - "TC-LP-02"
  - "TC-LP-03"
  - "TC-LP-05"
affected_files:
  - "app/agent.py"
  - "app/callbacks.py"
  - "app/config.py"
  - "app/schemas.py"
  - "app/sub_agents/__init__.py"
  - "app/tools/__init__.py"
  - "app/tools/uc2_jtd_search.py"
  - "app/seed_data/bq_seed_records.py"
  - "app/seed_data/jtd_corpus.py"
  - "packages/api/__init__.py"
  - "packages/web/index.ts"
  - "scripts/generate_synthetic_corpus.py"
  - "scripts/setup_demo_infra.py"
  - "SA_F35.md"
  - "AGENTS.md"
  - "README.md"
  - ".agents-cli-spec.md"
---

# `ISS-014` — Decommission UC3 Agentic AI (`f35_airworthiness_orchestrator`), ASIP Physics Engine, Tables 4–6 & DOC-04..08 Across Code, Cloud Infrastructure & Documentation

## 1. Executive Summary
- **Operational Impact:** Streamlined the F-35 Fleet Sustainment Agent Platform (`f35-sustainment-agent`) by completely removing **Use Case 3 (`f35_airworthiness_orchestrator` / `@F35-Airworthiness-Agent`)**, the in-process ASIP physics solver (`app/physics/asip_engine.py`), the Form 700 HITL review gate (`enforce_hitl_airworthiness_gate`), `Form700ReviewStudio.tsx`, BigQuery `EU` Tables 4–6 (`high_freq_strain_telemetry`, `as_maintained_mbom_fasteners`, `airworthiness_release_ledger`), and Discovery Engine `eu` documents `DOC-04`..`DOC-08`.
- **Architecture Consolidation:** The platform now operates as a focused 3-Specialist-Sub-Agent Architecture (`f35_maintenance_data_agent`, `f35_analytics_agent`, `f35_jtd_search_agent`) backed by a 6-table, 600-record (`100` rows per table) BigQuery `EU` Data Warehouse and a 4-document (`DOC-01`, `DOC-02`, `DOC-03`, `DOC-09`) Discovery Engine `eu` corpus.

---

## 2. Root Cause & Dependency Analysis
1. **Cross-Table Dependency in `maintenance_work_orders` (`WO-2026-88403`):**
   - While Tables 4–6 (`high_freq_strain_telemetry`, `as_maintained_mbom_fasteners`, `airworthiness_release_ledger`) were exclusively used by UC3, work order `WO-2026-88403` on `ZM151` (`wuc_code = '53-20'`, `PRIORITY_1_RED_X`, `12.0` hrs MTTR) in `maintenance_work_orders` (and its linked `PHM-2026-99103` and `RES-2026-00003` rows) is one of the 6 core rows expected by the Carrier Strike Group query in `gs://f35sa/Issue Document.md` (`ISS-013`).
   - Preserving `WO-2026-88403` while scrubbing its `corrective_action` string of UC3 references (`"DOC-06 / ASIP Miner's Rule / Form 700 HITL"`) ensured 100% continuity for `UC 0`, `UC 0.1`, `UC 0.5`, and `ISS-013`.
2. **Unstructured Corpus Scoping (`DOC-03`):**
   - `DOC-04`..`DOC-08` were exclusively UC3 artifacts, whereas `DOC-03` (`RAF Marham Squadron Pilot Post-Flight Debrief Logbook`) was shared with UC2 (`53-30` canopy release handle / limit-switch debrief). Scoping `DOC-03` to `53-30` preserved the 4-document UC2 corpus (`DOC-01`, `DOC-02`, `DOC-03`, `DOC-09`).

---

## 3. Engineering Resolution Across Layers
1. **ADK Runtime & Backend (`app/`, `packages/api/`, `scripts/`):**
   - Deleted `app/sub_agents/uc3_airworthiness_agent.py`, `app/tools/uc3_airworthiness.py`, `app/physics/`, and the 3 UC3 `.schema.json` files.
   - Updated `app/agent.py`, `app/callbacks.py`, `app/config.py`, `app/schemas.py`, `app/sub_agents/__init__.py`, `app/tools/__init__.py`, and `packages/api/__init__.py` to wire `sub_agents=[f35_maintenance_data_agent, f35_analytics_agent, f35_jtd_search_agent]`.
   - Updated `scripts/setup_demo_infra.py` to automatically delete deprecated BigQuery `EU` tables (`high_freq_strain_telemetry`, `as_maintained_mbom_fasteners`, `airworthiness_release_ledger`) and purge deprecated Discovery Engine `eu` document chunks (`DOC-04`..`DOC-08`).
2. **Frontend Web (`packages/web/`):**
   - Deleted `packages/web/components/Form700ReviewStudio.tsx` and removed all UC3 exports/types from `packages/web/index.ts` and `packages/web/AGENTS.md`.
3. **Verification Suites & Documentation (`tests/`, `SA_F35.md`, `AGENTS.md`, `README.md`, `.agents-cli-spec.md`):**
   - Deleted `tests/unit/test_challenger_stress_uc3_hitl.py` and updated unit, 5-tier E2E, `agents-cli eval`, and performance suites (`365 passed, 0 failed`).
   - Updated `SA_F35.md` (`v1.4`), `AGENTS.md`, `README.md`, and `.agents-cli-spec.md`.

---

## 4. Dead Ends & Approaches Rejected
- **Rejected Approach — Deleting `WO-2026-88403` from `maintenance_work_orders`:** Removing `WO-2026-88403` would have reduced the Carrier Strike Group urgent/grounded work-order query result from `6` rows to `5` rows, breaking `ISS-013` and `gs://f35sa/Issue Document.md` parity. Keeping `WO-2026-88403` with standard structural NDI wording preserved 100% data integrity.

---

## 5. Verification, Regression Tests & Benchmarks
- **Unit & 5-Tier E2E Suite:** `.venv/bin/pytest tests/unit/ tests/e2e/ -q` → `365 passed, 0 failed`.
- **Live Cloud Infrastructure (`setup_demo_infra.py --force-reimport`):**
  - BigQuery `EU` (`antig-dave.ukd_f35_sustainment_demo`): Deprecated tables (`high_freq_strain_telemetry`, `as_maintained_mbom_fasteners`, `airworthiness_release_ledger`) deleted; 6 active tables verified at `100` rows each (`600` rows total).
  - Discovery Engine `eu` (`ukd-f35-jtd-ietm-ds` & `ukd-f35-narrative-logs-ds`): Deprecated `DOC-04`..`DOC-08` documents deleted; `4` UC2 documents (`DOC-01`, `DOC-02`, `DOC-03`, `DOC-09`) indexed and verified via live REST search.
