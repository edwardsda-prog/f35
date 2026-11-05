---
issue_id: "ISS-010"
title: "Agent Elevator Pitch Refactor, Responsive Table Column Pruning & GCS CSV Download Link Removal"
date: "2026-11-05"
status: "RESOLVED"
severity: "P2-HIGH"
domain: "UI-UX / Presentation"
sub_agent: "f35_sustainment_coordinator, f35_maintenance_data_agent, f35_analytics_agent"
guardrails_impacted:
  - "PERF-05"
  - "SAFE-01"
vv_test_cases:
  - "TC-LP-01"
  - "TC-LP-02"
  - "TC-SQ-00"
commit_or_pr: "HEAD"
author: "David Edwards"
---

# [ISS-010] Agent Elevator Pitch Refactor, Responsive Table Column Pruning & GCS CSV Download Link Removal

> **Quick Reference Summary:** Replaced the verbose registered agent description in Gemini Enterprise and the ADK coordinator with a high-level executive "Elevator Pitch"; enforced strict screen-fitting column budgets (4–6 columns max) across maintenance and analytics tables to eliminate horizontal scrolling; and removed broken external GCS CSV download links in favor of native Gemini Enterprise App table copy/download features.

---

## 1. Symptom & Operational Context

### 1.1 Observed Symptoms & User Feedback
1. **Issue 1 (Agent Description / Launch Pitch):**
   - **Observed Symptom:** Launching the agent in Gemini Enterprise displayed an exhaustive, technical inventory:
     `UK Defence F-35 Lightning II Fleet Sustainment Coordinator (RAF Marham & HMS Queen Elizabeth). Orchestrates UC0 Conversational Maintenance Work Order Text-to-SQL & Spreadsheet Cards (@F35-Maintenance-Data), UC1 Supply & Readiness Analytics (@F35-Sustainment-Analytics), UC2 S1000D JTD & Cross-Service Maintenance Search (@F35-JTD-Search), and UC3 Dynamic Flight Envelope Exceedance & ASIP Structural Airworthiness (@F35-Airworthiness-Agent).`
   - **Expected Behavior:** Deliver a high-level, executive Elevator Pitch for the Agent that remains accurate as new capabilities are added without requiring constant edits.
2. **Issue 2 (Horizontal Scrolling on Open P1 / MICAP Maintenance Orders):**
   - **Observed Symptom:** Querying *"Show me all open Priority-1 and MICAP maintenance work orders across RAF Marham and HMS Queen Elizabeth, sorted by estimated repair time"* returned a wide 12–18 column table requiring horizontal scrolling, including unrequested metrics like `logged_man_hours`.
   - **Expected Behavior:** Return a clean, screen-aligned table selecting only the essential 4–5 columns (`work_order_id`, `tail_number`, `base_location`, `aircraft_status`, `estimated_mttr_hours`), omitting unrequested columns.
3. **Issue 3 (Horizontal Scrolling on Any Prompt with Tabular Data):**
   - **Observed Symptom:** Any prompt yielding tabular data displayed wide tables (or wide 11-column cross-table joins in UC1), forcing users to scroll horizontally and degrading the user experience.
   - **Expected Behavior:** Dynamically assess what columns to return based on the user's specific prompt; never dump full tables or wide joins; cap tables at 4–6 columns so they fit cleanly within standard viewport widths.
4. **Issue 4 (Broken GCS CSV Download Link — HTTP 404):**
   - **Observed Symptom:** Clicking `[📥 Download .CSV (Excel / Google Sheets)]` returned HTTP 404 (`https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/exports/Open_Priority_1_and_MICAP_Work_Orders.csv`).
   - **Expected Behavior:** Do not provide the download link in markdown. The native functionality of Gemini Enterprise App provides built-in table copy and CSV download controls.

---

## 2. Root Cause Analysis (RCA)

1. **Discovery Engine Agent Registration (`1346484961578743940`):**
   - The registered agent in Discovery Engine (`locations/eu`) had stored the technical enumeration in both its `description` and `adkAgentDefinition.toolSettings.toolDescription` fields during initial setup.
2. **Text-to-SQL Column Over-Selection & Schema Instruction:**
   - In `app/sub_agents/uc0_maintenance_agent.py`, Rule 2 explicitly instructed the model to include `logged_man_hours` and `estimated_mttr_hours` on all work-order queries to populate formula footer summaries, leading the model to select 10–18 columns.
3. **UC1 11-Column Cross-Domain Table Join:**
   - In `app/tools/uc1_analytics.py`, `markdown_table` formatted telemetry, regional depot inventory, and sortie schedule fields into a single 11-column wide table.
4. **Embedded GCS Browser URLs:**
   - In `app/tools/uc0_maintenance.py`, `execute_maintenance_sql` inserted markdown links to `https://storage.cloud.google.com/...`, which require specific authenticated browser sessions and fail with HTTP 404 for unauthenticated endpoints.

---

## 3. Implementation Details & Architecture Changes

### 3.1 Executive Elevator Pitch Update
- **Discovery Engine Agent `1346484961578743940` (`eu`):**
  Patched via Discovery Engine REST API with `updateMask=description,adkAgentDefinition.toolSettings.toolDescription`:
  > *"AI decision-support coordinator for the UK F-35 Lightning II fleet, empowering commanders and engineers to maximize aircraft availability, accelerate maintenance triage, resolve complex technical faults, and uphold sovereign airworthiness across RAF Marham and HMS Queen Elizabeth."*
- **Root Agent (`app/agent.py`):**
  Updated `root_agent.description` with the matching high-level Elevator Pitch.

### 3.2 Screen-Fitting Column Budgets (Issues 2 & 3)
- **`app/sub_agents/uc0_maintenance_agent.py`:**
  - Added strict screen-alignment and column pruning directives:
    - Never use `SELECT *` and never return all 18 columns.
    - Strictly project **4 to 6 columns maximum** tailored to the prompt.
    - For open P1/MICAP work orders sorted by repair time: select only `work_order_id`, `tail_number`, `base_location`, `aircraft_status`, and `estimated_mttr_hours`.
    - Omit `logged_man_hours` unless the user explicitly requests technician hours or effort.
- **`app/tools/uc0_maintenance.py`:**
  - Compacted column header cells: `**{column_letter}** {field_name}`.
  - Dynamically pruned formula summary bar items to only show formulas for columns actually queried.
- **`app/tools/uc1_analytics.py` & `app/sub_agents/uc1_analytics_agent.py`:**
  - Split the 11-column joined table into two clean, screen-aligned tables:
    1. **Aircraft & Component Status** (5 columns max: `Tail`, `Serial No.`, `Flight Hours`, `Limit`, `Status`).
    2. **Regional Depot Inventory** (4 columns: `NSN`, `Depot Stock`, `30-Day Reserved`, `Shipping ETA`).
    3. Dedicated single-line callout for the assigned sortie.

### 3.3 Removal of Broken CSV Download Link (Issue 4)
- Removed `[📥 Download .CSV (Excel / Google Sheets)]` from `card_markdown` in `app/tools/uc0_maintenance.py` (both header banner and formula summary bar).
- Instructed `f35_maintenance_data_agent` to omit external CSV links, leveraging Gemini Enterprise App's native table download/export capabilities.

---

## 4. Verification & Validation

### 4.1 Automated Tests Added / Updated
- `tests/unit/test_adversarial_issues_1_to_8.py`:
  - `test_root_agent_description_is_elevator_pitch`: Asserts Elevator Pitch content and absence of technical UC codes.
  - `test_uc0_open_p1_micap_column_pruning_and_screen_alignment`: Verifies open P1/MICAP query returns exactly 5 columns, omits `logged_man_hours`, and contains no CSV download links.
  - `test_uc0_no_csv_download_links_in_any_query`: Asserts no download links or GCS URLs are in `spreadsheet_card_markdown`.
  - `test_uc1_markdown_table_screen_friendly_column_budget`: Verifies all table rows in UC1 output have $\le 5$ columns.
- `tests/unit/test_deterministic.py`:
  - Updated `test_uc0_execute_maintenance_sql_spreadsheet_card_and_csv_link` to assert `[📥 Download .CSV` is NOT in markdown.

### 4.2 Test Suite Execution
```bash
uv run pytest tests/unit/
# Output: 184 passed in 28.28s (0 failures)
```

### 4.3 Live Production Verification (Reasoning Engine 5022570215192395776)
Executed `python3 scripts/verify_production_issue10.py` against live Reasoning Engine in `europe-west1`:
1. **Operational Capability Pitch:** Returned high-level elevator pitch in 903 ms with zero technology mentions (`BigQuery`, `GCS`).
2. **Open P1 / MICAP Maintenance Orders:** Returned 6 screen-aligned data columns (`work_order_id`, `tail_number`, `base_location`, `aircraft_status`, `work_order_status`, `estimated_mttr_hours`), omitted `logged_man_hours`, and emitted zero broken CSV links (`storage.cloud.google.com`).
3. **Actuator Fatigue & Depot Analytics:** Returned clean 5-column and 4-column tables cleanly aligned without horizontal scrolling.
Result: `🎉 ALL PRODUCTION TESTS PASSED SUCCESSFULLY! Deployment 100% verified.`

---

## 5. Prevention & Guardrails

| Guardrail ID | Description | Enforcement Point |
| :--- | :--- | :--- |
| **UX-01** | **Screen-Fitting Column Budget** | Prompt instructions and table formatters strictly enforce $\le 6$ columns to prevent horizontal scrolling. |
| **UX-02** | **Native UI Export Preference** | No fragile GCS download links in markdown outputs; rely on Gemini Enterprise native table copy/export. |
| **UX-03** | **Executive Elevator Pitch** | Agent description focuses on fleet mission availability and operational benefits rather than technical feature lists. |
