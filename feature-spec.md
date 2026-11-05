# Feature Specification: Use Case 0 Trilogy (`UC 0`, `UC 0.1`, `UC 0.5`) — Conversational F-35 Maintenance Data Warehouse (Text-to-SQL, Multi-Table JOINs & Spreadsheet Card)

> **Parent Specification:** [.agents-cli-spec.md](./.agents-cli-spec.md) & [SA_F35.md](./SA_F35.md) (`SDD-GE-F35-001`, v1.4)  
> **Target Platform:** Google Cloud Agent Platform (Gemini Enterprise Search & Conversation, Agent Runtime, Agent Registry — *Agent Gateway excluded for Demo Track*)  
> **Target GCP Project & Region (`REG-01`):** `antig-dave` (`284046449012`) · BigQuery in `EU` (9 Tables · 100 Consistent Records per Table = 900 Total Warehouse Records) · GCS & Agent Runtime in `europe-west1` (Belgium)  
> **Specialist Sub-Agent:** `f35_maintenance_data_agent` (`@F35-Maintenance-Data`) (`app/sub_agents/uc0_maintenance_agent.py` & `app/tools/uc0_maintenance.py`)

---

## 1. Feature Overview & Operational Objective

The **Use Case 0 Trilogy (`UC 0` → `UC 0.1` → `UC 0.5`)** provides a progressive, ultra-low-latency conversational Text-to-SQL foundation for **Act 0: Morning Maintenance Stand-Up** inside the **Gemini Enterprise UI (`F35 Support`)**:
- **UC 0 (Act 0.0 — Work Order Stand-Up):** Single-table conversational Text-to-SQL over **Table 7 (`maintenance_work_orders`, 100 records)** tracking Lockheed Martin ODIN / UK MOD Form 707A Aircraft Maintenance Log Work Orders.
- **UC 0.1 (Act 0.1 — Post-Sortie PHM / BIT Fault & Repeat CND Triage):** Single-table conversational Text-to-SQL over **Table 8 (`phm_bit_fault_events`, 100 records)** tracking Portable Maintenance Aid (PMA) post-flight Health Reporting Codes (`HRCs`), `PILOT_REPORT_ONLY_NO_BIT` anomalies (`ZM151` Canopy Latch), chronic repeat Could Not Duplicate (`CND`) rogue faults, and unactioned PHM advisories (`linked_work_order_id IS NULL`).
- **UC 0.5 (Act 0.5 — Multi-Table Shift Dispatch, SQEP & Calibrated Tooling Join):** Multi-table conversational SQL `JOIN` across **Table 7 (`maintenance_work_orders`)**, **Table 9 (`work_center_tooling_and_sqep`, 100 records)**, and/or **Table 8 (`phm_bit_fault_events`)**, cross-referencing open Priority 1/2 work orders against SQEP technician headcount, QAR inspector availability, and calibrated special support equipment (`JTD-53-30-T14` Digital Torque Spanner, `NDI-PAUT-496A` Ultrasonic C-Scan Rig, `LO-IR-BLANKET-04` RAM Cure Blanket).

Across all three sub-use-cases (`UC 0`, `UC 0.1`, `UC 0.5`), `execute_maintenance_sql` returns an **Excel / Google Sheets-like Spreadsheet Card** complete with:
1. **Spreadsheet Grid Layout** with Column Letters (`A`, `B`, `C`...), formatted column headers, and row numbers (`1..N`).
2. **Context-Aware Operational Status Badges**:
   - **Aircraft Readiness (`aircraft_status`):** `🟢 FMC`, `🟡 PMC-M`, `🟠 NMC-M`, `🔴 NMC-S (MICAP)`
   - **PHM Fault Severity (`fault_severity` — UC 0.1):** `🔴 CRITICAL_GROUNDING`, `🟠 DEGRADED_PMC`, `🟡 ADVISORY_PHM`, `⚪ NO_BIT_FAULT_LOGGED`
   - **CND Repeat Indicator (`cnd_flag` — UC 0.1):** `⚠️ CND (Repeat)` vs `✅ Verified`
   - **Tool Calibration Status (`tool_calibration_status` — UC 0.5):** `🟢 CALIBRATED_SERVICEABLE`, `🟡 CALIBRATION_DUE_WARNING`, `🔴 EXPIRED_OUT_OF_CAL`, `🟠 IN_USE_OTHER_BAY`
   - **Bay Dispatch Readiness (`bay_dispatch_status` — UC 0.5):** `🟢 READY_TO_DISPATCH`, `🔴 BLOCKED_TOOL_OUT_OF_CAL`, `🟠 BLOCKED_NO_QAR_ON_SHIFT`, `🔴 BLOCKED_AWAITING_MICAP_PART`
3. **Deterministic Context-Aware Formula Summary Footer Row**:
   - Total Rows: `=COUNTA(A2:A{N})`
   - Dynamic Sum (`=SUM(...)`): `logged_man_hours` (UC 0 / UC 0.5), `recurrence_count_30d` (UC 0.1), or `sqep_certified_techs_on_shift` (UC 0.5 tooling)
   - Dynamic Average (`=AVERAGE(...)`): `estimated_mttr_hours` (UC 0 / UC 0.5) or `diagnostic_confidence_pct` (UC 0.1)
4. **Automatic Clickable GCS `.csv` Download Link on Every Card**:
   - Automatically exports the exact SQL result set to `gs://antig-dave-f35-staging-europe-west1/exports/<filename>.csv` using pre-warmed in-memory Application Default Credentials (`PERF-01`, `PERF-07`) and embeds an authenticated browser download link (`[📥 Download .CSV (Excel / Google Sheets)](https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/exports/...)`) directly in the Spreadsheet Card footer (`ISS-005` compliant).

---

## 2. Lockheed Martin F-35 ODIN / MOD Form 707A Domain Model & Typical User Queries

Based on Lockheed Martin F-35 **ODIN (Operational Data Integrated Network)** / **ALIS** and **UK MOD Form 700 / Form 707A** operational standards, flight-line maintenance controllers routinely run the following conversational queries during daily Wing Stand-Ups:

1. **Morning Maintenance Stand-Up (Open NMC / PMC Work Orders & ETIC)**:
   - *"Show me all open maintenance work orders at RAF Marham for 617 Squadron, including aircraft status, subsystem, logged man-hours, and ETIC."*
2. **MICAP & Supply Bottleneck Isolation (`NMC-S`)**:
   - *"Which F-35 tails across RAF Marham and HMS Queen Elizabeth are grounded on NMC-S with an active MICAP supply flag?"*
3. **Tail-Specific Discrepancy History (`ZM151` Pre-Flight Triage)**:
   - *"List all maintenance work orders for tail ZM151 ordered by priority and creation time."*
4. **Subsystem / LCN Reliability & Man-Hour Aggregation (`GROUP BY`)**:
   - *"Group our maintenance work orders by subsystem name and LCN code, showing total work orders, total logged man-hours, and average estimated MTTR."*
5. **Low-Observable (LO) Stealth & Propulsion Backlog**:
   - *"Show all open or in-progress work orders for Low-Observable stealth coatings or F135 propulsion with their assigned hangar bay and estimated MTTR."*

---

## 3. BigQuery Schema & Semantic Metadata Specification (Table 7: `maintenance_work_orders`)

To guarantee zero-shot Text-to-SQL accuracy and sub-350ms BigQuery execution in `EU`, **Table 7 (`maintenance_work_orders`)** in `antig-dave.ukd_f35_sustainment_demo` MUST be provisioned with **time-unit partitioning** on `created_at_utc`, **clustering** on `["tail_number", "aircraft_status"]`, and **rich table and column descriptions** both in the declarative schema (`app/seed_data/schemas/maintenance_work_orders.schema.json`) and live in BigQuery metadata.

### 3.1 Table-Level Metadata
- **Dataset:** `antig-dave.ukd_f35_sustainment_demo` (`location="EU"`)
- **Table Name:** `maintenance_work_orders`
- **Partitioning:** `DAY` partitioning on `created_at_utc`
- **Clustering:** `["tail_number", "aircraft_status"]`
- **Table Description:**
  > *"Lockheed Martin ODIN (Operational Data Integrated Network) and UK MOD Form 707A Aircraft Maintenance Log work order ledger for F-35 Lightning II squadrons across RAF Marham (617 Sqn, 207 Sqn) and HMS Queen Elizabeth (809 NAS). Tracks open and historical maintenance discrepancies, aircraft mission capability status (FMC, PMC-M, NMC-M, NMC-S), MICAP supply holds, S1000D/ODIN Logistics Control Numbers (LCN/WUC), action taken codes, logged technician man-hours, estimated Mean Time To Repair (MTTR), and Estimated Time in Commission (ETIC) for conversational Text-to-SQL analytics (UC0)."*

### 3.2 Column-Level Metadata & Descriptions

| Col Letter | Column Name | BigQuery Type | Mode | Semantic Column Description (Applied in BigQuery Schema) |
| :---: | :--- | :--- | :--- | :--- |
| **A** | `work_order_id` | `STRING` | `REQUIRED` | Primary Key (PK): Unique ODIN / MOD Form 707A maintenance job control number (e.g., `WO-2026-707A-0101`). |
| **B** | `tail_number` | `STRING` | `REQUIRED` | Cluster Key: UK military F-35 registration tail number (e.g., `ZM151`, `ZM152`, `ZM154`, `ZM155`, `ZM158`, `ZM160`, `ZM162`). |
| **C** | `aircraft_variant` | `STRING` | `REQUIRED` | F-35 aircraft variant designation: `'F-35A'` (CTOL) or `'F-35B'` (STOVL Carrier/Expeditionary). |
| **D** | `squadron` | `STRING` | `REQUIRED` | Assigned operational squadron: `'617 Sqn'` (The Dambusters), `'207 Sqn'` (OCU), or `'809 NAS'` (The Immortals). |
| **E** | `base_location` | `STRING` | `REQUIRED` | Current operating air station or carrier strike group vessel: `'RAF Marham'` or `'HMS Queen Elizabeth'`. |
| **F** | `aircraft_status` | `STRING` | `REQUIRED` | Cluster Key: Mission capability readiness code: `'FMC'` (Fully Mission Capable), `'PMC-M'` (Partially Mission Capable - Maintenance), `'NMC-M'` (Not Mission Capable - Maintenance), or `'NMC-S'` (Not Mission Capable - Supply). |
| **G** | `work_order_status` | `STRING` | `REQUIRED` | Current work order execution status: `'OPEN'`, `'IN_PROGRESS'`, `'AWAITING_PARTS'`, `'AWAITING_NDI'`, or `'CLOSED'`. |
| **H** | `priority_level` | `STRING` | `REQUIRED` | Maintenance urgency priority: `'PRIORITY_1_CRITICAL'`, `'PRIORITY_2_URGENT'`, or `'PRIORITY_3_ROUTINE'`. |
| **I** | `micap_flag` | `BOOL` | `REQUIRED` | Boolean flag (`true` / `false`): Indicates an active Mission Impaired Capability Awaiting Parts (`MICAP`) high-priority supply requisition driving `NMC-S` status. |
| **J** | `lcn_code` | `STRING` | `REQUIRED` | S1000D / ODIN Logistics Control Number (LCN) / Work Unit Code (WUC) identifying the aircraft system/subsystem (e.g., `'27-10'` Flight Controls, `'53-30'` Canopy, `'53-11'` Fuselage Frame 496, `'72-00'` F135 Propulsion, `'34-40'` AN/APG-81 Radar, `'51-10'` LO Stealth Coating). |
| **K** | `subsystem_name` | `STRING` | `REQUIRED` | Human-readable aircraft subsystem nomenclature corresponding to the LCN code (e.g., `'Flight Controls - Horizontal Tail EHA'`, `'Fuselage Structure - Frame 496'`, `'Canopy Mechanical Rigging'`). |
| **L** | `discrepancy_summary` | `STRING` | `REQUIRED` | Concise technician or pilot discrepancy write-up describing the fault symptom or inspection trigger (e.g., `'Port EHA S/N ACT-99812-F at 1000.4 hrs (+0.4 hr life-limit breach)'`). |
| **M** | `action_taken_code` | `STRING` | `REQUIRED` | Standardized military maintenance action code and label: `'R - Remove & Replace'`, `'F - Rigging & Adjustment'`, `'Y - NDI Ultrasonic C-Scan'`, `'G - Troubleshooting / BIT Reset'`, `'C - High-Temp RAM Cure'`, or `'Z - Scheduled Servicing Complete'`. |
| **N** | `assigned_bay` | `STRING` | `REQUIRED` | Assigned maintenance work center or hangar bay (e.g., `'Hangar Bay 1 - Marham'`, `'Flight Line Bay 3 - Marham'`, `'LO Barn Bay 2 - Marham'`, `'Forward Hangar Deck - QNLZ'`). |
| **O** | `logged_man_hours` | `FLOAT64` | `REQUIRED` | Unit: hours (hrs). Cumulative technician labor man-hours logged against this work order to date. |
| **P** | `estimated_mttr_hours` | `FLOAT64` | `REQUIRED` | Unit: hours (hrs). Estimated Mean Time To Repair (MTTR) required to complete the maintenance action and restore airworthiness. |
| **Q** | `etic_utc` | `TIMESTAMP` | `REQUIRED` | Estimated Time in Commission (ETIC) in UTC ISO-8601 format indicating when the aircraft is projected to return to `FMC` status. |
| **R** | `created_at_utc` | `TIMESTAMP` | `REQUIRED` | Partition Key: UTC timestamp when the work order was opened in ODIN / MOD Form 707A. |

### 3.3 Table 8 Schema & Semantic Descriptions (`phm_bit_fault_events` — UC 0.1, 100 Records)
- **Partitioning:** `DAY` partitioning on `fault_timestamp_utc`
- **Clustering:** `["tail_number", "fault_severity"]`
- **Columns (`A`..`P`):** `fault_event_id` (PK), `tail_number`, `aircraft_variant`, `squadron`, `base_location`, `sortie_id`, `wuc_code`, `subsystem_name`, `hrc_code` (Health Reporting Code), `fault_severity` (`CRITICAL_GROUNDING`, `DEGRADED_PMC`, `ADVISORY_PHM`, `NO_BIT_FAULT_LOGGED`), `bit_trigger_type` (`CONTINUOUS_BIT`, `INITIATED_BIT`, `PHM_PROGNOSTIC_THRESHOLD`, `PILOT_REPORT_ONLY_NO_BIT`), `recurrence_count_30d`, `cnd_flag` (`BOOL`), `diagnostic_confidence_pct`, `linked_work_order_id` (FK -> `maintenance_work_orders.work_order_id` or `NULL`), `fault_timestamp_utc`.

### 3.4 Table 9 Schema & Semantic Descriptions (`work_center_tooling_and_sqep` — UC 0.5, 100 Records)
- **Partitioning:** `DAY` partitioning on `shift_updated_utc`
- **Clustering:** `["base_location", "work_center"]`
- **Columns (`A`..`P`):** `resource_id` (PK), `assigned_work_order_id` (FK -> `maintenance_work_orders.work_order_id`), `base_location`, `work_center`, `supported_wuc_code`, `shift_code`, `shift_lead_name`, `sqep_certification_domain`, `sqep_certified_techs_on_shift`, `qar_inspector_available` (`BOOL`), `required_special_tool_id` (`JTD-53-30-T14`, `NDI-PAUT-496A`, `LO-IR-BLANKET-04`), `required_special_tool_name`, `tool_calibration_status` (`CALIBRATED_SERVICEABLE`, `CALIBRATION_DUE_WARNING`, `EXPIRED_OUT_OF_CAL`, `IN_USE_OTHER_BAY`), `calibration_expiry_utc`, `bay_dispatch_status` (`READY_TO_DISPATCH`, `BLOCKED_TOOL_OUT_OF_CAL`, `BLOCKED_NO_QAR_ON_SHIFT`, `BLOCKED_AWAITING_MICAP_PART`), `shift_updated_utc`.

---

## 4. ADK 2.0 Sub-Agent & Pure Dynamic Text-to-SQL Tool Architecture

### 4.1 Sub-Agent Definition: `f35_maintenance_data_agent` (`app/sub_agents/uc0_maintenance_agent.py`)
- **Agent Name:** `f35_maintenance_data_agent` (`@F35-Maintenance-Data`)
- **Model Configuration (`PERF-05`):** `gemini-3.8-flash` initialized via `get_gemini_model("gemini-3.8-flash", thinking_level="LOW")` (`enterprise=True`, `location="global"`, `temperature=0.0`).
- **System Instruction & Performance Optimization:**
  - Embeds the exact schema and column names of `antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders`.
  - Instructs the model to translate the user's natural language request into a clean, read-only BigQuery Standard SQL `SELECT` statement and immediately invoke `execute_maintenance_sql(sql_query=..., sheet_title=...)`.
  - **Ultra-Low-Latency Output Rule:** Once `execute_maintenance_sql` returns, `f35_maintenance_data_agent` outputs a 1–2 sentence executive takeaway followed **verbatim** by the pre-formatted `spreadsheet_card_markdown` returned by the tool (avoiding slow LLM re-serialization of large Markdown tables).

### 4.2 Tool Contract: `execute_maintenance_sql` (`app/tools/uc0_maintenance.py`)
- **Signature:**
  ```python
  def execute_maintenance_sql(
      sql_query: str,
      sheet_title: str = "F35_ODIN_Maintenance_Work_Orders",
      tool_context: Any | None = None,
  ) -> dict[str, Any]:
  ```
- **Execution Pipeline & Guardrails:**
  1. **Read-Only SQL Validation Guardrail:**
     - Strips comments and trailing semicolons; verifies the query starts with `SELECT` or `WITH` and references `maintenance_work_orders`.
     - Rejects any statement containing mutating or administrative keywords (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `REVOKE`, `MERGE`, `CALL`, `EXECUTE`) or multi-statement semicolons, returning a structured `SQL_GUARDRAIL_BLOCKED` error dictionary.
     - Automatically qualifies unqualified `maintenance_work_orders` table references to `` `antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders` ``.
  2. **Ultra-Low-Latency BigQuery EU Execution (`PERF-07`):**
     - Executes the validated SQL query against `antig-dave.ukd_f35_sustainment_demo` (`location="EU"`) using the pre-warmed `bq_client` singleton in `app/clients.py`.
     - Includes an instant in-memory SQL evaluation fallback over `MAINTENANCE_WORK_ORDERS_ROWS` when running in offline unit tests or if cloud connectivity is unavailable.
  3. **Deterministic Spreadsheet Formula Summary Calculation:**
     - Computes `row_count` (`=COUNTA()`), `total_logged_man_hours` (`=SUM(logged_man_hours)`), `avg_estimated_mttr_hours` (`=AVERAGE(estimated_mttr_hours)`), `micap_count` (`=COUNTIF(micap_flag, TRUE)`), and status counts (`FMC`, `PMC-M`, `NMC-M`, `NMC-S`).
  4. **Automatic GCS `.csv` Export & Authenticated Browser Link (`ISS-005`, `PERF-01`):**
     - Serializes the returned rows (plus the summary footer row) into RFC 4180 `.csv` format.
     - Uploads the `.csv` payload to `gs://antig-dave-f35-staging-europe-west1/exports/<filename>.csv` via a pre-warmed `storage.Client` singleton in `app/clients.py` (with fast non-blocking/bounded timeout so tool latency stays `< 350 ms`).
     - Formats the download link via `to_authenticated_gcs_url()` as `https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/exports/<filename>.csv`.
  5. **Excel / Google Sheets-like Markdown Card Generation:**
     - Builds `spreadsheet_card_markdown` containing:
       - **Sheet Header Bar:** Sheet title, active row/column count, BigQuery `EU` execution telemetry, and `fx` SQL formula bar (`SELECT ...`).
       - **Spreadsheet Grid Table:** Column letter headers (`A: ...`, `B: ...`, `C: ...`), row numbers (`1..N`), and visual status badges (`🟢 FMC`, `🟡 PMC-M`, `🟠 NMC-M`, `🔴 NMC-S (MICAP)`).
       - **Formula Summary Footer Row:** Bold summary row displaying `=COUNTA()`, `=SUM()`, and `=AVERAGE()` results.
       - **Download Action Bar:** `[📥 Download .CSV (Excel / Google Sheets)](https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/exports/...)`.

---

## 5. Frontend Component Specification (`packages/web/components/MaintenanceSheetCard.tsx`)

- Provides a zero-dependency isomorphic React/TypeScript component (`MaintenanceSheetCard` & `renderMaintenanceSheetCardHtml`) in `packages/web/components/MaintenanceSheetCard.tsx` (exported via `packages/web/index.ts`).
- Renders an Excel / Google Sheets-inspired UI card featuring:
  - Green/Slate spreadsheet header bar with sheet tab (`F35_ODIN_Maintenance_Work_Orders.csv`) and `.CSV` download button linking to the authenticated `https://storage.cloud.google.com/...` URL.
  - `fx` Formula Bar showing the executed BigQuery `SELECT` statement.
  - Column letter header row (`A`, `B`, `C`, ...) and numbered row index gutter (`1`, `2`, ..., `∑`).
  - Color-coded status pills (`FMC`, `PMC-M`, `NMC-M`, `NMC-S / MICAP`).
  - Bottom summary formula bar (`=COUNTA()`, `=SUM(logged_man_hours)`, `=AVERAGE(estimated_mttr_hours)`).

---

## 6. Verification & Performance SLAs

- **`TC-SQ-00` (UC0 Text-to-SQL & Spreadsheet Card Fidelity):**
  - Verifies that natural-language maintenance queries generate valid read-only `SELECT` SQL against `maintenance_work_orders`, return accurate ODIN / Form 707A records (`ZM151`, `ZM152`, `ZM154`, etc.), include Column Letters (`A`, `B`, `C`...), Status Badges, Formula Summary Footer (`=COUNTA`, `=SUM`, `=AVERAGE`), and an authenticated `https://storage.cloud.google.com/.../exports/*.csv` download link.
- **`TC-LP-00` (UC0 Sub-Second BigQuery Execution & CSV Export Latency):**
  - BigQuery `EU` partition/cluster-pruned SQL execution `p95 <= 350 ms`; end-to-end tool execution `p95 <= 600 ms`; end-to-end conversational response `p95 <= 2,200 ms`.
