---
issue_id: "ISS-012"
title: "Carrier Strike Group Elevator Pitch, Three Operating Locations (Marham, QNLZ, PWLS), and Concise UC1 Chart Prompt"
date: "2026-11-05"
status: "RESOLVED"
severity: "P2-HIGH"
domain: "Backend-ADK"
sub_agent: "f35_sustainment_coordinator"
guardrails_impacted:
  - "REG-01"
  - "PERF-05"
vv_test_cases:
  - "TC-SQ-01"
  - "TC-LP-01"
  - "TC-LP-02"
commit_or_pr: "main"
author: "Antigravity Pair Programmer"
---

# [ISS-012] Carrier Strike Group Elevator Pitch, Three Operating Locations (Marham, QNLZ, PWLS), and Concise UC1 Chart Prompt

> **Quick Reference Summary:** Fixed agent description to reflect operational scope across the Carrier Strike Group; expanded structured and unstructured fleet datasets to include all three F-35 UK operating bases (RAF Marham, HMS Queen Elizabeth, and HMS Prince of Wales); and streamlined the UC1 chart rendering prompt into a clean, numbered menu.

---

## 1. Symptom & Operational Context

### 1.1 Observed Failure / Degradation
1. **Issue 1 (Agent Description Scope):**
   - *Observed Symptom:* When launched or queried for operational capability, the agent returned:
     `"AI decision-support coordinator for the UK F-35 Lightning II fleet, empowering commanders and engineers to maximize aircraft availability, accelerate maintenance triage, resolve complex technical faults, and uphold sovereign airworthiness across RAF Marham and HMS Queen Elizabeth."`
   - *Expected Behavior:* Uphold sovereign airworthiness `"across the Carrier Strike Group."`
2. **Issue 2 (Three F-35 Operating Locations):**
   - *Observed Symptom:* Fleet warehouse tables, seed records, and documentation only mentioned `RAF Marham` and `HMS Queen Elizabeth`.
   - *Expected Behavior:* Reflect the operational reality of the Royal Air Force and Royal Navy across all three operating locations: `RAF Marham`, `HMS Queen Elizabeth`, and `HMS Prince of Wales`.
3. **Issue 3 (UC1 Chart Presentation Prompt):**
   - *Observed Symptom:* Following sortie swap recommendations, UC1 presented an overly verbose prompt:
     ```text
     Would you like me to render:
     Actuator Fatigue Threshold Chart (Tail ZM151 at 1,000.4 hrs vs ZM154 at 842.0 hrs vs 1,000.0-hr threshold)
     Regional Depot Stock vs 30-Day Demand Chart (RAF Marham & HMS Queen Elizabeth stock vs 30-day demand)
     Or both?
     ```
   - *Expected Behavior:* Return concise prompt:
     `"Would you like me to render: 1. Actuator Fatigue Threshold Chart, 2. Regional Depot Stock vs 30-Day Demand Chart, or the full Executive Briefing Dashboard for your presentation slide deck?"`

### 1.2 Reproduction Steps / Triggering Input
1. **Environment:** `GOOGLE_CLOUD_PROJECT=antig-dave`, `GOOGLE_CLOUD_REGION=europe-west1`, BigQuery (`EU`), Discovery Engine (`eu`).
2. **Commands & Queries:**
   - Launch / Description query: `"Describe your operational capability"`
   - Maintenance Stand-Up query: `"Show me all open Priority-1 and MICAP maintenance work orders across RAF Marham, HMS Queen Elizabeth, and HMS Prince of Wales, sorted by estimated repair time."`
   - Sortie / Spares analysis: `"Check RAF Marham F-35A horizontal tail actuator hours against our 30-day spare parts stock, and recommend an aircraft swap for morning sortie SRT-MAR-20261103-01."`

---

## 2. Root Cause Analysis (RCA)

### 2.1 Primary Root Cause
1. **Agent Description:** Root coordinator description string in `app/agent.py` and Discovery Engine agent registration (`1346484961578743940` on engine `f35-support` in `eu`) ended with `across RAF Marham and HMS Queen Elizabeth.` rather than `across the Carrier Strike Group.`.
2. **Missing Operating Base:** Seed data generators (`app/seed_data/bq_seed_records.py`), BigQuery JSON schemas, and technical documentation omitted `HMS Prince of Wales` (depot `DEPOT-PWLS-03`, tails `ZM158`, `ZM159`, `ZM160`, and embarked 809 NAS sorties).
3. **Verbose Prompt Template:** Rule 3 in `app/sub_agents/uc1_analytics_agent.py` used an un-numbered, multi-line parenthetical format rather than the standardized 3-option menu format.

---

## 3. Fix & Code Changes Applied

### 3.1 Summary of Resolution
- **Description & Discovery Engine:** Updated `root_agent.description` in `app/agent.py` and patched Discovery Engine agent `1346484961578743940` via REST API.
- **Three Operating Locations:**
  - Added `HMS Prince of Wales` to `_BASE_AIRFRAME_COMPONENT_TELEMETRY_ROWS` (`TEL-ZM160-ACT-77560`), `_BASE_GLOBAL_DEPOT_INVENTORY_ROWS` (`DEPOT-PWLS-03`, `HMS Prince of Wales Afloat Spares`), `_BASE_SQUADRON_SORTIE_SCHEDULE_ROWS` (`SRT-PWLS-20261103-01`), and `maintenance_work_orders` (`WO-2026-88410`, `WO-2026-88411`).
  - Balanced 809 NAS across `HMS Queen Elizabeth` and `HMS Prince of Wales` while preserving 1:1:1 squadron distribution (`617 Sqn`, `809 NAS`, `207 Sqn (OCU)`).
  - Updated all JSON schemas in `app/seed_data/schemas/` to enumerate all 3 bases.
  - Re-seeded BigQuery EU dataset `antig-dave.ukd_f35_sustainment_demo` (100 rows per table, all 9 tables verified).
- **UC1 Chart Prompt:** Updated Rule 3 in `app/sub_agents/uc1_analytics_agent.py` and chart trigger keywords in `app/tools/chart_painter.py` and `app/tools/uc1_analytics.py` to recognize option 1, option 2, option 3, "full dashboard", "executive", and "briefing".
- **Documentation & Storyboard:** Updated `SA_F35.md` and `DEMO_STORYBOARD.md` to reference all three operating locations and the exact prompt wording.

### 3.2 Modified Files & Symbols
| File Path | Symbol / Function / Class Modified | Change Type | Description |
| :--- | :--- | :---: | :--- |
| `[app/agent.py](../../app/agent.py)` | `root_agent.description` | `Modified` | Updated description to Carrier Strike Group |
| `[app/sub_agents/uc1_analytics_agent.py](../../app/sub_agents/uc1_analytics_agent.py)` | `instruction` | `Modified` | Updated Rule 3 chart prompt verbatim |
| `[app/tools/chart_painter.py](../../app/tools/chart_painter.py)` | `generate_sustainment_graphics` | `Modified` | Added executive/briefing trigger tokens |
| `[app/tools/uc1_analytics.py](../../app/tools/uc1_analytics.py)` | `render_sustainment_chart` | `Modified` | Added executive/briefing trigger tokens |
| `[app/seed_data/bq_seed_records.py](../../app/seed_data/bq_seed_records.py)` | Seed datasets & generators | `Modified` | Added HMS Prince of Wales depot, tails & sorties |
| `[app/seed_data/schemas/*.schema.json](../../app/seed_data/schemas/)` | BigQuery schemas | `Modified` | Allowed HMS Prince of Wales in base_location enums |
| `[SA_F35.md](../../SA_F35.md)` | Architecture spec | `Modified` | Updated operating bases and chart prompts |
| `[DEMO_STORYBOARD.md](../../DEMO_STORYBOARD.md)` | Storyboard | `Modified` | Aligned prompts and carrier references |
| `[tests/unit/test_adversarial_issues_1_to_8.py](../../tests/unit/test_adversarial_issues_1_to_8.py)` | Unit tests | `Modified` | Added regression tests for all 3 issues |

---

## 4. Dead Ends & Approaches Rejected

> [!WARNING]
> **Do Not Repeat These Approaches:** Future agents and engineers modifying these files must avoid the rejected approaches documented below.

| Rejected Approach | Why It Failed or Was Rejected | Guardrail / Constraint Violated |
| :--- | :--- | :--- |
| Committing local corporate `uv.lock` with internal proxy URLs (`airlock-proxy.uplink.goog`) | Cloud Build in GCP fails to resolve internal corporate proxy (`Connection refused os error 111`), breaking Agent Runtime container builds. | `REG-01` / Build Invariant |
| Reallocating `WO-2026-88412` from `207 Sqn (OCU)` to `809 NAS` | Caused `207 Sqn (OCU)` to lose its only `PMC-M` ticket, reducing SQL `GROUP BY squadron, aircraft_status` groups from 11 to 10 and failing BigQuery parity assertions. | Test Parity Invariant |

---

## 5. Verification & Regression Tests

- **Unit Tests:** `uv run pytest tests/unit/` -> **186 passed** in 38.05s.
- **BigQuery Verification:** Confirmed `SELECT DISTINCT base_location` returns `RAF Marham`, `HMS Queen Elizabeth`, and `HMS Prince of Wales`.
- **Discovery Engine Agent Check:** Verified `GET .../agents/1346484961578743940` description contains `across the Carrier Strike Group.`.
- **Reasoning Engine Deployment:** Updated on Agent Runtime (`europe-west1`).
