---
issue_id: ISS-016
title: "Master Storyboard & Slide Deck Reproduction Alignment: Prune Active Work Orders to 6 Rows, Remove Orphaned UC3 Fault (`WO-2026-88403` / `PHM-2026-99103`) from `ZM151`, Standardize Horizontal Tail Actuator Naming, Fix Formula Summary Bar `0.0 hrs`, and Align Slide 4 Prompts 2 & 3"
status: VERIFIED_IN_PROD
severity: P1-MAJOR
date_reported: 2026-11-05
date_resolved: 2026-11-05
domains:
  - UC0-Maintenance-Data
  - UC1-Analytics
  - UC2-JTD-Search
  - Infra-EU
  - Eval-QA
sub_agents_affected:
  - f35_maintenance_data_agent
  - f35_analytics_agent
  - f35_jtd_search_agent
guardrails_touched:
  - REG-01
  - PERF-01
  - PERF-05
  - PERF-07
  - UX-01
  - UX-02
  - UX-03
vv_test_cases:
  - TC-SQ-00
  - TC-SQ-01
  - TC-SQ-02
  - TC-LP-00
  - TC-LP-02
  - TC-LP-03
related_issues:
  - ISS-013
  - ISS-014
  - ISS-015
---

# `ISS-016`: Master Storyboard & Slide Deck Reproduction Alignment (`gs://f35sa/Issue - V1.md`)

## 1. Executive Summary
Following an end-to-end live run-through of the 6-Prompt Storyboard in Gemini Enterprise (`gs://f35sa/Issue - V1.md`), seven reproduction discrepancies were identified and resolved:
1. **Orphaned 3rd Fault on Lead Jet `ZM151` (`WO-2026-88403` / `PHM-2026-99103`):** Reassigned `WO-2026-88403` and `PHM-2026-99103` (`Center Fuselage Frame 496 Bulkhead` from retired UC3) off `ZM151` to `ZM161` (`COMPLETED` / `ADVISORY_PHM`) so `ZM151` strictly exhibits the **2 Storyboard faults** (`WO-2026-88401` Horizontal Tail Actuator and `WO-2026-88402` Canopy Latch).
2. **Active Work Order Pruning (`10` $\rightarrow$ `6` Rows) & `ZM151` Top-of-Table Ordering:** Pruned 4 background work orders (`WO-2026-88403`, `WO-2026-88404`, `WO-2026-88409`, `WO-2026-88412`) to `COMPLETED`, set `WO-2026-88402` (`14.0 hrs` unmitigated canopy teardown estimate) and `WO-2026-88401` (`8.5 hrs` actuator swap) at **Rows 1 & 2** of Prompt 1, and assigned `WO-2026-88408` (`ZM156`) to **`HMS Prince of Wales`** so all 3 Carrier Strike Group operating locations (`RAF Marham`, `HMS Queen Elizabeth`, `HMS Prince of Wales`) appear in the 6 active rows.
3. **Option A Alignment for Prompts 2 & 3 (`DEMO_STORYBOARD.md` & Slide 4):** Added `Rule 8: PROMPT_2_ZM151_POST_SORTIE_ALIGNMENT` and `Rule 9: PROMPT_3_SHIFT_READINESS_ALIGNMENT` in `app/tools/uc0_maintenance.py` and aligned `DEMO_STORYBOARD.md` with Slide 4 (`"What faults or pilot-reported issues were raised on ZM151 after its last flight, and are any repeat unconfirmed faults?"` and `"Which of our open maintenance jobs are ready to start on this shift, with both qualified crew and calibrated tools staged?"`).
4. **Formula Summary Bar `0.0 hrs` Suppression:** Updated `execute_maintenance_sql` in `app/tools/uc0_maintenance.py` so projections without numeric hours columns (Prompts 2 & 3) display `=COUNTA(...) · =COUNTIF(status, "ALERT/MICAP") -> N` instead of `=SUM(logged_man_hours) -> 0.0 hrs`.
5. **Component Name Standardization (`WUC 27-10`):** Renamed `Electro-Hydrostatic Actuator (Flaperon)` / `Port Electro-Hydrostatic Actuator (EHA)` to **`Horizontal Tail Electro-Hydrostatic Actuator (EHA)`** across all seed tables in `app/seed_data/bq_seed_records.py`.
6. **Prompt 5 Escaped Image Markdown Fix (`uc1_analytics_agent.py`):** Removed raw `![...](...)` markdown image embed syntax (which Gemini Enterprise's sanitizer backslash-escapes) in favor of the clean `[📥 Download Executive Slide Graphic (PNG)](...)` link.
7. **Prompt 6 `DOC-09` Scope Restriction (`uc2_search_agent.py`):** Restricted `DOC-09` (4-hour heater blanket cure) to Low Observable RAM coating queries so canopy latch queries (`Prompt 6`) focus cleanly on **`DOC-02`** (USMC `VMFA-211` sealant debris, 45-min fix) and **`DOC-01`** (`18.5 N·m` torque spec with spanner `JTD-53-30-T14`).

## 2. Root Cause Analysis (RCA)
- **`WO-2026-88403` / `PHM-2026-99103` Legacy UC3 Row:** When UC3 (`f35_airworthiness_orchestrator`) was decommissioned in `ISS-014`, its seed work order (`WO-2026-88403`, `12.0 hrs`, `Center Fuselage Frame 496 Bulkhead`) and PHM event (`PHM-2026-99103`, `CRITICAL_GROUNDING`) remained attached to `ZM151`, causing `ZM151` to display 3 faults instead of the Storyboard's Dual-Fault matrix.
- **MTTR Sort Ordering & `HMS Prince of Wales` Representation:** `WO-2026-88401` (`4.5 hrs`) and `WO-2026-88402` (`2.5 hrs`) sorted to the bottom of the 10-row table when ordered by `estimated_mttr_hours DESC`, and none of the active rows were assigned to `HMS Prince of Wales`.
- **Formula Summary Bar Default Fallback:** `_resolve_numeric_series` returned empty `sum_vals`/`avg_vals` for non-numeric 6-column projections (Prompts 2 & 3), but `card_markdown` unconditionally rendered `=SUM(logged_man_hours) -> 0.0 hrs`.

## 3. Engineering Resolution & Files Modified
- [`app/seed_data/bq_seed_records.py`](../../app/seed_data/bq_seed_records.py)
- [`app/tools/uc0_maintenance.py`](../../app/tools/uc0_maintenance.py)
- [`app/sub_agents/uc0_maintenance_agent.py`](../../app/sub_agents/uc0_maintenance_agent.py)
- [`app/sub_agents/uc1_analytics_agent.py`](../../app/sub_agents/uc1_analytics_agent.py)
- [`app/sub_agents/uc2_search_agent.py`](../../app/sub_agents/uc2_search_agent.py)
- [`DEMO_STORYBOARD.md`](../../DEMO_STORYBOARD.md)
- [`tests/unit/test_semantic_sql_guardrails.py`](../../tests/unit/test_semantic_sql_guardrails.py)
- [`tests/unit/test_deterministic.py`](../../tests/unit/test_deterministic.py)

## 4. Dead Ends & Approaches Rejected
- **Changing the Storyboard Narrative to Include a 3rd Structural Fault on `ZM151`:** Rejected because UC3 (Structural Airworthiness) was intentionally removed in `ISS-014`, and leaving an unresolved 12-hour `CRITICAL_GROUNDING` bulkhead crack on `ZM151` creates a plot hole across Acts 2 and 3.

## 5. Verification, Regression Tests & Benchmarks
- **Unit & 5-Tier E2E Suite:** `385 passed` across `tests/unit/` and `tests/e2e/`.
- **BigQuery `EU` Re-Seeding & Reasoning Engine `europe-west1` Deployment:** Re-seeded all 6 tables (`600` records) in `antig-dave.ukd_f35_sustainment_demo` (`location=EU`) and redeployed Reasoning Engine `5022570215192395776` (`europe-west1`).
