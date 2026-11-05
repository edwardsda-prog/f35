---
issue_id: "ISS-009"
title: "Operational Capability Summary High-Level Refactor & Internal Technology Concealment"
date: "2026-11-05"
status: "RESOLVED"
severity: "P2-HIGH"
domain: "Coordinator"
sub_agent: "f35_sustainment_coordinator"
guardrails_impacted:
  - "PERF-01"
  - "PERF-05"
vv_test_cases:
  - "TC-LP-01"
  - "TC-SQ-00"
  - "TC-SQ-01"
commit_or_pr: "HEAD"
author: "David Edwards"
---

# [ISS-009] Operational Capability Summary High-Level Refactor & Internal Technology Concealment

> **Quick Reference Summary:** Refactored the fast-path operational capability response to deliver a concise, high-level, future-proof summary of agent purpose and operational benefits without fragile use-case enumerations, and enforced strict concealment of internal cloud technology names (`BigQuery`, `GCS`, `Discovery Engine`), standardizing all repository references to the **"F35 Datawarehouse"**.

---

## 1. Symptom & Operational Context

### 1.1 Observed Failure / Degradation
1. **Issue 1 (Excessive Capability Output):**
   - **Observed Symptom:** Inquiring *"Describe your operational capability"* returned an overly detailed, technical breakdown enumerating individual use-case numbers (`UC0`, `UC1`, `UC2`, `UC3`), table names, regional endpoints, and framework names (`ADK 2.0`, `Gemini 3.8 Flash`).
   - **Operational Impact:** High cognitive overhead for executive commanders and maintenance officers. The rigid enumerations required constant code amendments whenever additional capabilities were added to the platform.
2. **Issue 2 (Technology Leaks in Answers):**
   - **Observed Symptom:** Internal technology and cloud platform names (`BigQuery`, `GCS`, `Google Cloud Storage`, `Discovery Engine`) were leaked in user-facing answers, fast-path greetings, and Spreadsheet Card headers.
   - **Operational Impact:** Violated defense presentation standards where users should interact with operational domain concepts rather than underlying hyperscaler implementation details.

### 1.2 Reproduction Steps / Triggering Input
1. **Environment:** `GOOGLE_CLOUD_PROJECT=antig-dave`, `GOOGLE_CLOUD_REGION=europe-west1`, `EU` BigQuery dataset.
2. **Triggering Queries:**
   - *"Describe your operational capability"*
   - *"What are your capabilities?"*
   - Execution of `execute_maintenance_sql` for maintenance work orders.
3. **Observed Behavior:**
   - Capability response listed: `"I am an enterprise AI sustainment agent built on Google Agent Developer Kit (ADK 2.0) and Gemini 3.8 Flash... UC0... BigQuery EU Table 7... UC1... UC2... UC3..."`.
   - Spreadsheet Card markdown displayed: `**Dataset:** antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders (EU)` and `<details><summary>🔍 View Executed BigQuery SQL (EU)</summary>`.
4. **Expected Behavior:**
   - Return a high-level summary of the purpose and operational benefit of the Agent without excessive technical detail or brittle use-case enumerations.
   - Conceal internal technology names and refer to underlying data stores as the **"F35 Datawarehouse"**.

---

## 2. Root Cause Analysis (RCA)

### 2.1 Primary Root Cause
1. In `app/callbacks.py`, `_FAST_PATH_CAPABILITY_RESPONSE` had hardcoded an exhaustive 4-use-case technical description detailing ADK 2.0, BigQuery Table 7, and Cloud Storage citation links.
2. In `app/tools/uc0_maintenance.py`, the Markdown Spreadsheet Card generator explicitly stamped the fully-qualified BigQuery table ID and region (`antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders (EU)`) in the visible card header and labeled the collapsible query as `View Executed BigQuery SQL (EU)`.
3. In `app/agent.py` and `app/sub_agents/`, system instructions lacked an explicit negative constraint forbidding the mention of underlying cloud technologies and directing the models to refer to data storage as the **"F35 Datawarehouse"**.

### 2.2 Architectural Guardrail / Invariant Analysis
| Guardrail / Test ID | Pre-Fix State | Post-Fix State | Notes |
| :--- | :---: | :---: | :--- |
| **`TC-LP-01` (Fast-Path Latency)** | `✅ COMPLIANT (< 5 ms)` | `✅ COMPLIANT (< 5 ms)` | Sub-5ms fast-path execution preserved while streamlining response content. |
| **UX Consistency** | `❌ FAILED (Tech leak & verbosity)` | `✅ COMPLIANT` | Generic, high-level purpose and benefits returned; tech brand names concealed. |
| **Data Repository Naming** | `❌ FAILED (Raw BQ table & GCS)` | `✅ COMPLIANT` | Labeled uniformly as `F35 Datawarehouse`. |

---

## 3. Fix & Code Changes Applied

### 3.1 Summary of Resolution
1. **High-Level Capability Response Refactor (`app/callbacks.py`):**
   Replaced verbose technical enumerations in `_FAST_PATH_CAPABILITY_RESPONSE` with a concise, future-proof executive summary focused on core operational benefits:
   - **Accelerate Fleet Readiness:** Rapid analysis of maintenance work orders, component health telemetry, and depot inventory.
   - **Actionable Decision Support:** Proactive maintenance interventions, parts replenishment, and tail swaps.
   - **Authoritative Engineering Guidance:** Grounded S1000D publications, multi-service repair narratives, and structural flight exceedance assessments with HITL governance.
2. **Greeting & Empty Prompt Clean-Up (`app/callbacks.py`):**
   Cleaned `_FAST_PATH_EMPTY_RESPONSE` and `_FAST_PATH_GREETING_RESPONSE` to remove references to `europe-west1 / EU` and internal sub-agent codes.
3. **Spreadsheet Card Repository Standard (`app/tools/uc0_maintenance.py`):**
   Changed card header from raw dataset FQN to `**Repository:** F35 Datawarehouse (maintenance_work_orders)` and collapsible header from `View Executed BigQuery SQL (EU)` to `View Executed Query`.
4. **Agent System Instruction Guardrails (`app/agent.py` & `app/sub_agents/`):**
   Injected mandatory `COMMUNICATION & TECHNOLOGY CONCEALMENT RULE` across root coordinator and all four specialist sub-agents, prohibiting mentions of `BigQuery`, `GCS`, `Discovery Engine`, etc., and directing references to the `F35 Datawarehouse`.
5. **Solution Design Document Alignment (`SA_F35.md`):**
   Updated metadata header line 19 to include `UC0: Maintenance Data Stand-Up` in the demonstration scope.

### 3.2 Modified Files & Symbols
| File Path | Symbol / Function / Class Modified | Change Type | Description |
| :--- | :--- | :---: | :--- |
| `app/callbacks.py` | `_FAST_PATH_CAPABILITY_RESPONSE`, `_FAST_PATH_GREETING_RESPONSE`, `_FAST_PATH_EMPTY_RESPONSE` | Modified | Streamlined capability response to high-level purpose/benefits; removed cloud technology terms. |
| `app/tools/uc0_maintenance.py` | `execute_maintenance_sql` | Modified | Replaced BigQuery table FQN with `F35 Datawarehouse` and generalized query details header. |
| `app/agent.py` | `COORDINATOR_INSTRUCTION` | Modified | Added mandatory technology concealment rule directing responses to `F35 Datawarehouse`. |
| `app/sub_agents/uc0_maintenance_agent.py` | `UC0_SYSTEM_INSTRUCTION` | Modified | Added Rule 4 for technology concealment. |
| `app/sub_agents/uc1_analytics_agent.py` | `UC1_SYSTEM_INSTRUCTION` | Modified | Added Rule 5 for technology concealment. |
| `app/sub_agents/uc2_search_agent.py` | `UC2_SYSTEM_INSTRUCTION` | Modified | Added Rule 4 for technology concealment. |
| `app/sub_agents/uc3_airworthiness_agent.py` | `UC3_SYSTEM_INSTRUCTION` | Modified | Added Rule 5 for technology concealment. |
| `SA_F35.md` | Demonstration Scope Metadata Table | Modified | Added `UC0: Maintenance Data Stand-Up` to demonstration scope. |
| `tests/unit/test_deterministic.py` | `TestFastPathCapabilityInterception` | Modified | Verified sub-5ms latency, purpose/benefit assertions, and absence of leaked cloud tech names. |
| `tests/unit/test_adversarial_issues_1_to_8.py` | `TestFastPathRegexAdversarial` | Modified | Aligned adversarial regex test assertions with high-level capability summary. |

---

## 4. Verification & Regression Testing

### 4.1 Unit Test Execution
- **Command:** `uv run pytest tests/unit/`
- **Result:** `176 passed, 1 warning in 24.64s`
- **Specific Verifications:**
  - `test_fast_path_intercepts_operational_capability_query_under_5ms`: PASS
  - `test_fast_path_greetings_conceal_technology_names`: PASS
  - `test_fast_path_capability_interception_edge_cases` (all 27 permutations): PASS
  - `test_uc0_execute_maintenance_sql_spreadsheet_card_and_csv_link`: PASS
