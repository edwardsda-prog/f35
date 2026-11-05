# Solution Design Document: F-35 Fleet Sustainment — Gemini Enterprise Demonstrations

## Dual-Phase Specification: Demonstration Sandbox & Accredited Production Target (Conversational Maintenance Data, Supply & Sortie Analytics, and Grounded Enterprise Search)

Document ID: SDD-GE-F35-001 \| Author: David Edwards (Customer Engineer, UK Public Sector) \| Date: 2026-11-05 \| Version: 1.4 \| Status: Demonstration & Target Architecture Specification (3-Agent Architecture: UC 0 / 0.1 / 0.5, UC 1, and UC 2)

Executive Summary: This Solution Design Document (SDD) defines the target architecture, database schemas, and authoritative document corpus required to demonstrate Gemini Enterprise and the Agent Platform across fifth-generation F-35 Lightning II sustainment workflows. Following a dual-track delivery model, the design aligns the Google Cloud Demonstration Sandbox and the Production Target around the unified Agent Platform—comprising Gemini Enterprise (GE) Search and Conversation, Agent Runtime, and Agent Registry (explicitly excluding Agent Gateway for the demonstration). Gemini Enterprise compresses time-to-insight and time-to-action from hours to seconds across three progressive sustainment pillars: (1) Conversational Maintenance Data Text-to-SQL, PHM/BIT Fault Triage & Multi-Table SQEP/Tooling Resource Joins (`UC 0 / 0.1 / 0.5`), (2) Conversational Supply & Sortie Readiness Analytics with On-Demand 16:9 Presentation Graphics (`UC 1`), and (3) Grounded Enterprise Search across S1000D Joint Technical Data (JTD) Manuals and 5-Year Cross-Service Maintenance Logs (`UC 2`).

# 1\. Document Control & Programme Scope

&nbsp;

| Metadata Field | Specification Value |
| :---- | :---- |
| Document ID & Title | SDD-GE-F35-001 — F-35 Fleet Sustainment: Gemini Enterprise Demonstrations |
| Author & Role | David Edwards — Customer Engineer, Google Cloud UK/IE Public Sector & Defense |
| Target Platform | Gemini Enterprise & Agent Platform (GE Search & Conversation, Agent Runtime, Agent Registry) |
| Operational Domain | Fifth-Generation Fighter Sustainment (RAF Marham / UK Carrier Strike Group ODIN & ALIS) |
| Demonstration Scope | UC 0 / 0.1 / 0.5: Maintenance Data Stand-Up, PHM/BIT Triage & Multi-Table Resource Join \| UC1: Conversational Analytics & On-Demand 16:9 Charting \| UC2: Enterprise Search & Cross-Service RAG |
| Reference Baseline | Aligned with SDD-GE-UKD-002 (Gemini Enterprise demo design) and Enterprise Agent SDD v2.0 |

## 1.1 Strategic Context & Dual-Track Delivery Approach

Fifth-generation aircraft sustainment generates petabytes of structured sensor telemetry alongside millions of pages of unstructured technical publications and human maintenance narratives. Traditional sustainment portals suffer from data siloization—separating relational logistics databases from Joint Technical Data (JTD) manuals and cross-service maintenance logs. Building on the dual-track methodology established in internal UK Defence reference architectures, this solution establishes two parallel execution environments:

* Demonstration Track (Immediate Pilot Sandbox): A cloud-hosted demonstration environment running on Google Cloud Platform (GCP) in `EU` / `europe-west1` (Belgium). It showcases Gemini Enterprise and the Agent Platform—specifically GE Search and Conversation, Agent Runtime (hosting ADK 2.0 agents), and Agent Registry—backed by a 6-table, 600-record BigQuery `EU` Data Warehouse (`ukd_f35_sustainment_demo`), interactive Excel / Google Sheets-like Maintenance Cards with `.CSV` export (`UC 0 / 0.1 / 0.5`), two-turn on-demand chart rendering via `render_sustainment_chart` (backed by on-the-fly Matplotlib chart painting with dynamic GCS slide upload and clickable PNG downloads alongside inline Vega-Lite Canvas specs in `UC 1`), and single-pass Discovery Engine `eu` grounded search (`UC 2`). For the purpose of the demonstration, Agent Gateway is omitted in favor of direct integration between Gemini Enterprise, Agent Registry, and Agent Runtime.  
* Production Track (Accredited Sovereign Target): The target-state military deployment hosting Gemini Enterprise and the full Agent Platform (GE Search and Conversation, Agent Runtime, and Agent Registry) on Google Distributed Cloud (GDC) Air-Gapped appliances, integrated with live Lockheed Martin / JPO ODIN relational nodes, portable maintenance aid (PMA) PHM/BIT fault pipelines, and S1000D XML Interactive Electronic Technical Manuals (IETMs).

## 1.2 Summary of the Demonstration Use Cases

&nbsp;

| Use Case & Modality | Operational Scenario | Data Viewpoint | Trad. Time-to-Action | Gemini Time-to-Action |
| :---- | :---- | :---- | :---- | :---- |
| UC 0: Conversational Maintenance Data Text-to-SQL + Spreadsheet Card | Morning Maintenance Stand-Up & ODIN Work Order Triage (Conversational Text-to-SQL against `maintenance_work_orders`, 100 records across RAF Marham, HMS Queen Elizabeth & HMS Prince of Wales; status badges, formula summary row & clickable CSV export). | Structured Data Only (BigQuery SQL: `maintenance_work_orders` — ODIN / MOD Form 707A, 100 records) | 45 to 90 Minutes (Manual ODIN/ERP exports, Excel pivot tables & status color-coding) | Near-Instantaneous (< 1.5s Text-to-SQL + Spreadsheet Card & automatic `.CSV` download link) |
| UC 0.1: Post-Sortie PHM / BIT Fault & Repeat CND Triage | Post-flight Portable Maintenance Aid (PMA) Health Reporting Code (`HRC`) triage, `PILOT_REPORT_ONLY_NO_BIT` anomaly isolation (`ZM151` Canopy Latch), repeat `CND` rogue fault detection, and unactioned PHM advisories (`linked_work_order_id IS NULL`). | Structured Data Only (BigQuery SQL: `phm_bit_fault_events`, 100 records) | 60 to 120 Minutes (Manual PMA log reconciliation & CND correlation) | Near-Instantaneous (< 1.5s Text-to-SQL + PHM Severity/CND Badges & `.CSV` export) |
| UC 0.5: Multi-Table Shift Dispatch, SQEP & Calibrated Tooling Join | Conversational 2- and 3-table SQL `JOIN` across `maintenance_work_orders`, `work_center_tooling_and_sqep`, and `phm_bit_fault_events` to check SQEP technician headcount, QAR availability, and calibrated special tools (`JTD-53-30-T14`, `NDI-PAUT-496A`, `LO-IR-BLANKET-04`). | Structured Multi-Table Join (BigQuery SQL: 300 combined records in 600-record warehouse) | 90 to 180 Minutes (Manual cross-checking of shift rosters, calibration logs & Form 707A work orders) | Near-Instantaneous (< 1.6s Multi-Table SQL `JOIN` + Calibration/Dispatch Badges & `.CSV` export) |
| UC1: Conversational Analytics + On-Demand Charts | Automatic Part Replenishment & Fleet Readiness (Tail `ZM151` Left Horizontal Tail Actuator `S/N ACT-99812-F` exceeding 1,000-hr limit at `1,000.4` hrs; `NSN 1680-01-619-4821` stock = 4). | Structured Data Only (BigQuery SQL Telemetry, Inventory & Sortie Schedules — 300 combined records) | 2 to 4 Hours (Manual SQL, ERP lookups & shift replanning) | Near-Instantaneous (< 2.5s query + on-demand 16:9 presentation slide rendering & GCS upload in ~500–789 ms) |
| UC2: Enterprise Search (Grounded RAG) | Intermittent "Sticky" Cockpit Canopy Latch (Subjective pilot debrief with zero BIT faults; semantic correlation across JTD Section 53-30-01, sister squadron silicon debris logs & MAM Section 9-1 LO RAM cure rules). | Unstructured Data Only (JTD/IETM Manuals, Pilot Debriefs & 5-Yr Maintainer Logs: `DOC-01`, `DOC-02`, `DOC-03`, `DOC-09`) | 4 to 8 Hours (Manual keyword search across XML/PDF manuals) | 10 to 15 Minutes (Direct semantic match + multi-service translation) |

# 2\. Target Architecture: Gemini Enterprise & Agent Platform Topology

The target architecture centers on Gemini Enterprise coupled with the unified Agent Platform, comprising GE Search and Conversation, Agent Runtime (powered by ADK 2.0), and Agent Registry. For the purpose of the demonstration, Agent Gateway is intentionally excluded—agents registered in Agent Registry are invoked directly by Gemini Enterprise on the Agent Runtime and connect directly to backend data stores in `EU` / `europe-west1`.

* Gemini Enterprise & Root Sustainment Coordinator (`f35_sustainment_coordinator` on `gemini-3.8-flash`): Serves as the unified front-of-house experience, conversational orchestration layer, and enterprise router with `< 5 ms` Tier 1/2 fast-path interception (`before_model_callback`). Evaluates user prompts and routes maintenance work-order, PHM/BIT fault, and SQEP/tooling queries to `f35_maintenance_data_agent` (`UC 0 / 0.1 / 0.5`), structured supply/readiness analytical and charting requests to `f35_analytics_agent` (`UC 1`), and unstructured technical manual lookups to `f35_jtd_search_agent` (`UC 2`).  
* UC0 / UC0.1 / UC0.5 Maintenance Data Text-to-SQL & Spreadsheet Card Agent (`f35_maintenance_data_agent` on Agent Runtime / `gemini-3.8-flash`): Translates natural-language maintenance logbook, PHM/BIT fault, and SQEP/tooling queries into read-only BigQuery Standard SQL (`SELECT` and multi-table `JOIN`s) against `maintenance_work_orders`, `phm_bit_fault_events`, and `work_center_tooling_and_sqep`, guarded by the 3-Layer Operational Semantic Ontology & Deterministic SQL Canonicalizer (`ISS-013`). Returns an Excel / Google Sheets-like Spreadsheet Card with Column Letters (`A`..`Z`), Status Badges (`🟢 FMC`, `🟡 PMC-M`, `🟠 NMC-M`, `🔴 NMC-S (MICAP)`), Formula Summary Footer Rows (`=COUNTA()`, `=SUM()`, `=AVERAGE()`), and an automatic `.CSV` export.  
* UC1 Conversational Analytics & Charting Agent (`f35_analytics_agent` on Agent Runtime / `gemini-3.8-flash`): Registered in Agent Registry and executed on Agent Runtime. Translates natural-language supply and readiness questions into partition-pruned BigQuery SQL across `airframe_component_telemetry`, `global_depot_inventory`, and `squadron_sortie_schedule`; outputs structured operational tabular summaries in Turn 1 and renders presentation-ready 16:9 Full HD widescreen PNG slide graphics (uploaded dynamically to GCS with authenticated slide-deck download links) and interactive Vega-Lite v5 JSON specifications on Turn 2 via the dedicated `render_sustainment_chart` tool.  
* UC2 Enterprise Search & Grounded RAG (`f35_jtd_search_agent` on Agent Runtime / `gemini-3.8-flash` + GE Search and Conversation): Powered by single-pass (`pageSize=15`) Discovery Engine `eu` retrieval over chunked S1000D XML/PDF manuals and historical narrative logs (`ukd-f35-jtd-ietm-ds` & `ukd-f35-narrative-logs-ds`). Executes dense vector matching and bidirectional UK/US cross-service jargon normalization (`catch` ↔ `latch`, `spanner` ↔ `wrench`, `binding` ↔ `stiff`, `gouge` ↔ `score`) with mandatory inline clickable citations.

&nbsp;

| Architectural Layer | Demonstration Sandbox (GCP Pilot — `EU` / `europe-west1`) | Production Target (GDC Air-Gapped / ODIN) |
| :---- | :---- | :---- |
| Gemini Enterprise & Agent Registry | Gemini Enterprise Web UI (inline Spreadsheet Cards & Vega-Lite Canvas) + Agent Registry cataloguing the F-35 Sustainment Coordinator and 3 specialist sub-agents (No Agent Gateway in Demo). | Gemini Enterprise Squadron Portal & Sovereign Agent Registry governing fleet-wide sustainment agents on GDC Air-Gapped. |
| Agent Platform: GE Search & Conversation (UC2) | GE Search and Conversation (`eu`) indexing synthetic JTD/IETM manuals (`ukd-f35-jtd-ietm-ds`) & 5-yr narrative logs (`ukd-f35-narrative-logs-ds`) on GCS. | GDC Air-Gapped GE Search and Conversation indexing live JPO S1000D XML IETMs & FRACAS repositories. |
| Agent Platform: Agent Runtime (UC0, UC1 & UC2) | Managed Agent Runtime in `europe-west1` executing ADK 2.0 agents (`f35_maintenance_data_agent`, `f35_analytics_agent`, `f35_jtd_search_agent`). | Sovereign Agent Runtime on GDC Air-Gapped executing accredited ADK 2.0 multi-agent sustainment workflows. |
| Structured Data Warehouse (UC0 & UC1) | BigQuery `EU` (`ukd_f35_sustainment_demo`: 6 tables × 100 rows = 600 records) + on-the-fly Matplotlib 16:9 presentation chart painter (`chart_painter.py`). | Sovereign AlloyDB / ODIN ERP relational cluster across Main Operating Bases and embarked Queen Elizabeth-class carriers. |

# 2.5 Use Case 0 Design: Conversational Maintenance Data Text-to-SQL & Excel / Google Sheets Card (`maintenance_work_orders`, `phm_bit_fault_events`, `work_center_tooling_and_sqep`)

## 2.5.1 Operational Narrative & Pure Dynamic Text-to-SQL Pattern
Before diving into multi-table sortie swaps (UC1) or unstructured manual lookups (UC2), Squadron Maintenance Officers and Flight-Line Chiefs begin their shift at the **Morning Maintenance Stand-Up** by querying the **Lockheed Martin ODIN / UK MOD Form 707A Aircraft Maintenance Log Work Orders** ledger (`maintenance_work_orders`), post-sortie **PHM / BIT Fault Events** (`phm_bit_fault_events`), and **Work-Center SQEP & Calibrated Tooling** (`work_center_tooling_and_sqep`).

In **Use Case 0 (`@F35-Maintenance-Data`)**, the sub-agent (`f35_maintenance_data_agent`) embeds the complete semantic schema of all three maintenance warehouse tables in `antig-dave.ukd_f35_sustainment_demo` (`location="EU"`), writes a custom read-only BigQuery Standard SQL `SELECT` query directly from the user's natural-language prompt (supporting `WHERE` filters, `ORDER BY`, `LIMIT`, `GROUP BY` aggregations, and multi-table `INNER`/`LEFT JOIN`s), validates and canonicalizes it via a deterministic read-only SQL guardrail (`canonicalize_maintenance_sql`), executes it in `< 350 ms`, uploads the result set to `gs://antig-dave-f35-staging-europe-west1/exports/<sheet_id>.csv`, and returns an **Excel / Google Sheets-like Spreadsheet Card** directly in the Gemini Enterprise UI.

## 2.5.2 `maintenance_work_orders` Schema & Semantic Descriptions (UC 0 — 100 Records)

| `maintenance_work_orders` (Col A–R) | Data Type | Key / Constraint | Semantic Column Description & Sample Value |
| :--- | :--- | :--- | :--- |
| `A: work_order_id` | STRING | PRIMARY KEY | Unique ODIN / MOD Form 707A maintenance work order identifier (`WO-2026-88401`). |
| `B: tail_number` | STRING | CLUSTER KEY | UK military aircraft registration tail identifier (`ZM151`, `ZM152`, `ZM154`, `ZM155`, `ZM158`, `ZM159`, `ZM161`, `ZM163`). |
| `C: aircraft_variant` | STRING | NOT NULL | F-35 variant designation: `F-35A` (CTOL) or `F-35B` (STOVL). |
| `D: squadron` | STRING | NOT NULL | Assigned operational squadron: `617 Sqn (The Dambusters)`, `207 Sqn (OCU)`, or `809 NAS (The Immortals)`. |
| `E: base_location` | STRING | NOT NULL | Current operating station or carrier deployment base: `RAF Marham`, `HMS Queen Elizabeth`, or `HMS Prince of Wales`. |
| `F: aircraft_status` | STRING | CLUSTER KEY | DoD/MOD availability status code: `FMC`, `PMC-M`, `NMC-M`, or `NMC-S`. |
| `G: work_order_status` | STRING | NOT NULL | Work order execution status: `OPEN`, `IN_PROGRESS`, `AWAITING_PARTS (MICAP)`, `AWAITING_ENGINEERING_DISPOSITION`, `DEFERRED_HIL`, or `COMPLETED`. |
| `H: priority` | STRING | NOT NULL | Maintenance priority tier: `PRIORITY_1_RED_X`, `PRIORITY_2_URGENT`, or `PRIORITY_3_ROUTINE`. |
| `I: micap_flag` | BOOL | NOT NULL | Mission Capable (`MICAP`) critical supply shortage flag (`true` / `false`). |
| `J: wuc_code` | STRING | NOT NULL | 4-digit Work Unit Code / Logistics Control Number (`27-10`, `53-30`, `53-20`, `72-00`, `34-40`, `94-10`). |
| `K: subsystem_name` | STRING | NOT NULL | Human-readable aircraft subsystem nomenclature (`Flight Controls — Horizontal Tail Actuator`). |
| `L: discrepancy_narrative` | STRING | NOT NULL | Pilot or maintenance technician discrepancy write-up from MOD Form 707A / ODIN fault report. |
| `M: corrective_action` | STRING | NOT NULL | Documented maintenance corrective action or active troubleshooting step. |
| `N: work_center` | STRING | NOT NULL | Assigned hangar bay or specialist work center (`Flight Controls Bay`, `Airframes & Structures`, `Powerplant & Propulsion`). |
| `O: logged_man_hours` | FLOAT64 | NOT NULL | Cumulative direct maintenance technician man-hours logged against this work order (`6.5`). |
| `P: estimated_mttr_hours` | FLOAT64 | NOT NULL | Estimated Mean Time To Repair (`MTTR`) in hours required to complete the work order (`12.0`). |
| `Q: etic_utc` | TIMESTAMP | NULLABLE | Estimated Time In Commission (`ETIC`) timestamp in UTC when the aircraft returns to FMC. |
| `R: created_at_utc` | TIMESTAMP | PARTITION KEY | UTC timestamp when the maintenance work order was opened (`DAY` partitioning). |

## 2.5.3 `phm_bit_fault_events` (UC 0.1) & `work_center_tooling_and_sqep` (UC 0.5)

To support the full **Act 0 Trilogy (`UC 0` → `UC 0.1` → `UC 0.5`)** and ensure referential consistency across the **6-Table, 600-Record F-35 Data Warehouse** (`100` records per table across all 6 tables in `antig-dave.ukd_f35_sustainment_demo`), two companion operational tables are provisioned in BigQuery `EU`:

1. **`phm_bit_fault_events` (UC 0.1, 100 Records, Partitioned on `fault_timestamp_utc`, Clustered on `tail_number, fault_severity`):**
   - Tracks post-sortie PHM Health Reporting Codes (`hrc_code`), `fault_severity` (`CRITICAL_GROUNDING`, `DEGRADED_PMC`, `ADVISORY_PHM`, `NO_BIT_FAULT_LOGGED`), `bit_trigger_type` (`CONTINUOUS_BIT`, `INITIATED_BIT`, `PHM_PROGNOSTIC_THRESHOLD`, `PILOT_REPORT_ONLY_NO_BIT`), `recurrence_count_30d`, `cnd_flag`, `diagnostic_confidence_pct`, and `linked_work_order_id` (foreign key to `maintenance_work_orders.work_order_id`, including `NULL` for unactioned advisories).
2. **`work_center_tooling_and_sqep` (UC 0.5, 100 Records, Partitioned on `shift_updated_utc`, Clustered on `base_location, work_center`):**
   - Supports dual-key SQL `JOIN`s via `assigned_work_order_id` (`1:1` with `maintenance_work_orders.work_order_id`) and `(base_location, work_center, supported_wuc_code)`. Tracks `sqep_certification_domain`, `sqep_certified_techs_on_shift`, `qar_inspector_available`, `required_special_tool_id` (`JTD-53-30-T14`, `NDI-PAUT-496A`, `LO-IR-BLANKET-04`), `tool_calibration_status` (`CALIBRATED_SERVICEABLE`, `CAL_DUE_WITHIN_7D`, `EXPIRED_OUT_OF_CAL`, `IN_USE_OTHER_BAY`), and `bay_dispatch_status` (`READY_TO_DISPATCH`, `BLOCKED_TOOL_OUT_OF_CAL`, `BLOCKED_NO_QAR_ON_SHIFT`, `BLOCKED_AWAITING_MICAP_PART`).

## 2.5.4 Generalized 3-Layer Operational Semantic Ontology & SQL Canonicalizer (`ISS-013`)

To prevent semantic impedance mismatches between natural-language defence terminology and literal database enum values across unseen user queries, the UC 0 / UC 0.1 / UC 0.5 pipeline enforces a **3-Layer Semantic Defense-in-Depth Architecture**:

1. **Layer 1 — Enriched BigQuery Schema Metadata & Cross-Table Seed Consistency (`app/seed_data/`):**
   - A canonical `_TAIL_ASSIGNMENT_MAP` in `app/seed_data/bq_seed_records.py` guarantees 100% referential and location consistency for every tail (`ZM135`..`ZM176`) across all 6 tables (`600` total records), including `ZM159` (`WO-2026-88411`, `RES-2026-00011`, `TEL-ZM159-ACT-77542`, `PHM-2026-99111`) at `HMS Queen Elizabeth`.
   - Declarative BigQuery schemas (`app/seed_data/schemas/*.schema.json`) document that `RAF Marham` (land-based Main Operating Base / MOB) and `HMS Queen Elizabeth` / `HMS Prince of Wales` (afloat maritime platforms) together constitute the **UK Carrier Strike Group (CSG) / UK Lightning Force** force-generation enterprise.
2. **Layer 2 — Agent Cognitive Ontology (`UC0_SYSTEM_INSTRUCTION` in `app/sub_agents/uc0_maintenance_agent.py`):**
   - Embeds explicit translation rules across 8 semantic dimensions: CSG/Fleet-wide scope (no `base_location` restriction), `afloat`/`embarked` (`IN ('HMS Queen Elizabeth', 'HMS Prince of Wales')`), `ashore`/`MOB` (`'RAF Marham'`), squadron shorthand (`617`/`Dambusters`, `809`/`Immortals`, `207`/`OCU`), active work-order lifecycle (`work_order_status != 'COMPLETED'`), Red-X urgent/grounded triage (`priority = 'PRIORITY_1_RED_X' AND work_order_status != 'COMPLETED'`), PHM/BIT zero-code/CND filters, and SQEP/tooling dispatch constraints.
3. **Layer 3 — Deterministic SQL Semantic Canonicalizer & Zero-Row Auto-Recovery (`app/tools/uc0_maintenance.py`):**
   - `canonicalize_maintenance_sql(sql_query, sheet_title, user_prompt)` executes in `< 0.2 ms` before query evaluation, applying 6 deterministic rewrite rules (`CSG_ENTERPRISE_LOCATION_EXPANSION`, `LOCATION_CATEGORY_AND_ALIAS_CANONICALIZATION`, `SQUADRON_SHORTHAND_CANONICALIZATION`, `ACTIVE_WORK_ORDER_LIFECYCLE_EXPANSION`, `URGENT_AND_GROUNDED_TRIAGE_ALIGNMENT`, `ENUM_SYNONYM_CANONICALIZATION`).
   - If a valid `SELECT` query still returns `0` rows, `_relax_zero_row_sql` automatically relaxes exact string equality on descriptive columns (`subsystem_name`, `discrepancy_narrative`, `required_special_tool_name`) to case-insensitive `LOWER(col) LIKE '%term%'` and widens `work_order_status = 'OPEN'` to `work_order_status != 'COMPLETED'`.

# 3\. Use Case 1 Design: Conversational Analytics with On-Demand Presentation Charts (Structured Data)

## 3.1 Operational Narrative & Gemini Capabilities

When F-35A Tail `ZM151` lands at RAF Marham after a training sortie, its onboard computer uploads flight usage telemetry to ODIN. The Left Horizontal Tail Actuator (`S/N: ACT-99812-F`) reaches `1,000.4` flight hours, breaching its `1,000.0`-hour structural fatigue threshold. In the Gemini Enterprise demo, the Squadron Logistics Officer or Commander interacts with the `@F35-Sustainment-Analytics` agent using natural language rather than legacy ERP drop-downs.

To guarantee responsive flight-line interaction (< 2.5s SLA) and eliminate token generation latency spikes, Use Case 1 operates via a **Two-Turn Visualization Workflow**:

* **Turn 1: Text-to-SQL Generation & Operational Briefing:**
  - The user asks: *"Check RAF Marham F-35A horizontal tail actuator hours against our 30-day depot stock with visual charts, and recommend a tail swap for morning sortie SRT-MAR-20261103-01."*
  - Gemini translates this into an optimized partition-pruned SQL query joining `airframe_component_telemetry`, `global_depot_inventory`, and `squadron_sortie_schedule`.
  - The agent emits a structured Markdown summary table, recommends reallocating Pilot Henderson's sortie to Spare Tail `ZM154` (`842.0` hrs, Mission Capable), confirms depot replenishment for `NSN: 1680-01-619-4821` (4 on hand, 2 reserved, 18-hr ETA), and **explicitly prompts the user for chart selection**:
    > *"Would you like me to render: 1. Actuator Fatigue Threshold Chart, 2. Regional Depot Stock vs 30-Day Demand Chart, or the full Executive Briefing Dashboard for your presentation slide deck?"*
  - Structured query records are cached in ADK session state (`tool_context.session.state["last_uc1_metrics"]`).

* **Turn 2: On-Demand Presentation Graphics & Canvas Rendering (`render_sustainment_chart`):**
  - When the user requests a chart (e.g., *"Render the Actuator Fatigue Threshold Chart"* or *"Render the full 16:9 Executive Briefing Dashboard for my presentation slide deck"*), the agent dispatches the dedicated `render_sustainment_chart` tool.
  - **Dynamic On-the-Fly Presentation Graphics (`chart_painter.py`):** The tool executes headless Matplotlib (`Agg` backend) to dynamically synthesize a 16:9 Full HD widescreen presentation graphic (1920×1080 at 160 DPI) in the Clean Light Briefing Theme directly in memory from queried BigQuery records. Visual assets are **not** static pre-existing images; they are programmatically drawn on the fly.
  - **Dynamic GCS Push & Slide Download Links:** Streams rendered PNG bytes to `gs://antig-dave-f35-staging-europe-west1/charts/<filename>.png` in real time (~150–250 ms), returning authenticated HTTPS download links (`[📥 Download 16:9 Executive Slide Graphic (PNG)](https://storage.cloud.google.com/...)`) for direct insertion into executive slide decks (PowerPoint / Keynote), alongside inline Markdown image embeds.
  - **Interactive Gemini Enterprise Canvas:** Concurrently populates clean Vega-Lite v5 JSON specifications for interactive exploration in Gemini Enterprise Canvas (`VegaCanvas.tsx`).
  - **Session State Cache:** Caches rendered assets in `tool_context.session.state["cached_graphics_{chart_name}"]` to prevent redundant re-renders within the same session. Total on-the-fly rendering and upload completes in ~500–789 ms, well under the 1,500 ms SLA (`PERF-08`).

## 3.2 Structured Database Schemas (BigQuery: `ukd_f35_sustainment_demo`)

Three relational tables (`100` records each) in Google Cloud BigQuery `EU` power Use Case 1. Partitioning and clustering are configured to guarantee sub-2-second conversational query performance.

&nbsp;

| Table 1: `airframe_component_telemetry` | Data Type | Key / Constraint | Description & Demo Sample Value |
| :---- | :---- | :---- | :---- |
| `telemetry_record_id` | STRING | PRIMARY KEY | Unique post-flight upload identifier (e.g., `TEL-20261102-0941`) |
| `tail_number` | STRING | PARTITION / CLUSTER | Aircraft identifier (e.g., `ZM151`, `ZM154`) |
| `aircraft_variant` | STRING | NOT NULL | F-35 variant (`F-35A`, `F-35B`) |
| `base_location` | STRING | NOT NULL | Assigned operating base (`RAF Marham`, `HMS Queen Elizabeth`, `HMS Prince of Wales`) |
| `part_serial_number` | STRING | CLUSTER KEY | Installed component S/N (`ACT-99812-F`) |
| `nsn` | STRING | FOREIGN KEY | NATO Stock Number (`1680-01-619-4821`) |
| `component_name` | STRING | NOT NULL | `Left Horizontal Tail Actuator` |
| `current_flight_hours` | FLOAT64 | NOT NULL | Accumulated hours post-sortie (`1000.4` vs `1000.0` limit) |
| `life_limit_threshold_hrs` | FLOAT64 | NOT NULL | Mandated replacement threshold (`1000.0`) & status (`PMC-M`) |

&nbsp;

| Table 2: `global_depot_inventory` | Data Type | Key / Constraint | Description & Demo Sample Value |
| :---- | :---- | :---- | :---- |
| `nsn` | STRING | PRIMARY KEY | 13-digit NATO Stock Number (`1680-01-619-4821`) |
| `part_name` | STRING | NOT NULL | `Actuator, Electro-Hydrostatic Horizontal Tail` |
| `depot_id & depot_name` | STRING | CLUSTER KEY | `DEP-UK-01` (`RAF Marham Regional Sustainment Depot`) |
| `quantity_on_hand` | INT64 | NOT NULL | Available serviceable units in stock (`4`) |
| `quantity_reserved_30d` | INT64 | NOT NULL | Forecasted fleet demand over next 30 days (`2`) |
| `reorder_point_threshold` | INT64 | NOT NULL | Minimum stock trigger (`2`) |
| `avg_shipping_eta_hours` | FLOAT64 | NOT NULL | Standard transit time to squadron hangar (`18.0` hours) |

&nbsp;

| Table 3: `squadron_sortie_schedule` | Data Type | Key / Constraint | Description & Demo Sample Value |
| :---- | :---- | :---- | :---- |
| `sortie_id` | STRING | PRIMARY KEY | Scheduled mission ID (`SRT-MAR-20261103-01`) |
| `scheduled_departure_utc` | TIMESTAMP | PARTITION KEY | `2026-11-03T07:30:00Z` (Morning training wave) |
| `assigned_tail_number` | STRING | FOREIGN KEY | Primary aircraft (`ZM151` — flagged for swap) |
| `assigned_pilot_callsign` | STRING | NOT NULL | `Flt Lt Henderson (Callsign: VIPER-1)` |
| `spare_tail_candidate` | STRING | NULLABLE | `ZM154` (F-35A, `842.0` actuator hrs, Mission Capable) |
| `sortie_readiness_status` | STRING | NOT NULL | `AT_RISK_MAINTENANCE` -> Auto-reallocated to `ZM154` |

## 3.3 UC1 Tool Architecture & Dedicated Visualization Rendering Tool (`render_sustainment_chart`)

To prevent multi-second token generation latency and guarantee deterministic JSON schemas, the UC1 analytics pipeline exposes three dedicated tools:

### 1. `check_actuator_fatigue_and_depot_inventory`
* **Signature:** `check_actuator_fatigue_and_depot_inventory(base_location: str = "RAF Marham", hours_to_limit_window: float = 50.0, tool_context: ToolContext = None) -> dict`
* **Execution:** Queries BigQuery EU tables with partition pruning on `scheduled_departure_utc` and clustering on `tail_number` / `nsn`. Stashes structured results into `tool_context.session.state["last_uc1_metrics"]`.
* **Output:** Structured dictionary containing flagged tails, depot inventory summary, impacted sortie details, and a pre-formatted Markdown summary table. Inline Vega-Lite specifications are explicitly omitted in Turn 1 to preserve `< 2.5s` end-to-end latency.

### 2. `recommend_tail_swap_and_replenishment`
* **Signature:** `recommend_tail_swap_and_replenishment(sortie_id: str = "SRT-MAR-20261103-01", primary_tail: str = "ZM151", spare_tail: str = "ZM154", tool_context: ToolContext = None) -> dict`
* **Execution:** Validates spare aircraft availability and flight hours; drafts Priority-1 depot supply requisition (`NSN: 1680-01-619-4821`, 18-hr shipping ETA) and reallocates the sortie.

### 3. `render_sustainment_chart` (Dedicated Visualization & Presentation Graphics Tool)
* **Signature:** `render_sustainment_chart(chart_name: str, tool_context: ToolContext = None) -> dict`
* **Supported Charts & Slide Formats:**
  1. `actuator_fatigue_threshold_chart`: Horizontal threshold bar/line chart plotting Tail `ZM151` (`1,000.4` hrs, Red Breach Marker `#dc2626`) and `ZM154` (`842.0` hrs, Green Serviceable Marker `#16a34a`) against the `1,000.0`-hr condemnation threshold line.
  2. `depot_stock_vs_demand_bar_chart`: Grouped bar chart comparing available stock (`4` units) vs 30-day demand (`2` units) across RAF Marham, HMS Queen Elizabeth, and HMS Prince of Wales with net available callouts.
  3. `executive_dashboard` / `both`: Unified Full HD 16:9 widescreen presentation slide (composite dual-panel with master header, subtitle, and bottom operational decision callout banner).

# 4\. Use Case 2 Design: Enterprise Search & Grounded Reasoning (Unstructured Data)

## 4.1 Operational Narrative & Semantic Search Architecture

A pilot returns from a night sortie and logs a free-text complaint: *"Canopy manual release handle felt stiff and hesitated to latch fully during pre-flight. Required physical force to secure. No cockpit warnings or BIT faults displayed."* Traditional keyword searches for "canopy manual release" fail to match historical write-ups that use different phrasing. In Use Case 2, the flight-line technician queries GE Search and Conversation inside Gemini Enterprise (`@F35-JTD-Search`).

* Dense Vector Semantic Retrieval (GE Search and Conversation): GE Search and Conversation converts the pilot's symptom description into dense embeddings, bypassing electrical BIT fault trees and isolating mechanical rigging procedures in **JTD Section 53-30-01 ("Canopy Mechanical Rigging Inspection")** (`DOC-01`).  
* Cross-Service Dialect & Jargon Normalization: Gemini synthesizes 5 years of historical unstructured logs across US Air Force, US Marine Corps, Royal Navy, and RAF squadrons (`DOC-02` & `DOC-03`)—bridging terminology differences ("latch assembly" vs. "catch mechanism", "wrench" vs. "spanner", "binding" vs. "stiff"). It surfaces a sister squadron fix: *"Found silicon sealant debris wedge in roller path, causing handle stiffness. Cleaned assembly per JTD and lubed pivot pin."*  
* Grounded Output with Verbatim Citations & Thermal Cure Constraints: The agent delivers a concise, step-by-step inspection checklist linked directly to `DOC-01`, `DOC-02`, `DOC-03`, and **MAM Section 9-1 (`DOC-09`)** (`220°C` High-Temp RAM Sheet `'B'` and mandatory 4-hour heater blanket cure cycle), ensuring zero hallucinated torque values or unauthorized lubricants.

## 4.2 Unstructured Data Store & Metadata Schema (GE Search & Conversation: `ukd-f35-jtd-ietm-ds`)

To enable faceted filtering, subsystem routing, and precise citation anchoring in GE Search and Conversation, each ingested unstructured document chunk is indexed with the following JSON metadata schema:

&nbsp;

| Metadata Attribute | Field Type | Search Capability | Description & Example Value |
| :---- | :---- | :---- | :---- |
| `doc_id` & `chunk_id` | STRING | Retrievable / Key | `DOC-JTD-53-30-01-CHUNK-014` (500-token chunk, 100-token overlap) |
| `publication_code` | STRING | Filterable / Facet | `JTD-F35-53-30-01` or `JTD-NARRATIVE-LOG-53-30` |
| `system_subsystem_code` | STRING | Filterable / Facet | S1000D SNS code: `53-30` (Fuselage — Canopy & Framing) |
| `aircraft_variant_applicability` | ARRAY\<STRING\> | Filterable | `["F-35A", "F-35B", "F-35C"]` |
| `service_branch_origin` | STRING | Filterable / Facet | `RAF`, `RN`, `USAF`, `USMC` (enables cross-service translation) |
| `bit_fault_associated` | BOOLEAN | Filterable | `false` (allows boosting mechanical rigging docs when BIT = None) |
| `document_version_date` | STRING | Filterable / Sortable | `2026-10-15` (ensures retrieval of the latest JTD / MAM revision) |

## 4.3 Discovery Engine Query Architecture: Metadata Filtering, Relevance Boosting & Facet Aggregations

To achieve high precision, zero hallucination, and sub-2-second retrieval (`TC-LP-03`) across heterogeneous MoD and DoD technical publications, the UC2 Search Agent (`f35_jtd_search_agent`) interfaces with the Gemini Enterprise Discovery Engine EU multi-region endpoint (`https://eu-discoveryengine.googleapis.com/v1alpha/projects/antig-dave/locations/eu/...`) using structured metadata query primitives:

1. **Structured Metadata Filtering (`filter`):**
   - Boolean values on JSON fields are passed as quoted string literals: `bit_fault_associated = "false"`.
   - Subsystem scoping: `system_subsystem_code: ANY("53-30")` isolates ATA/S1000D chapters (Canopy & Framing).
   - Resilient two-stage execution: if a strict metadata filter returns zero hits, the tool automatically executes an immediate unfiltered fallback query.
2. **Dynamic Soft Relevance Boosting (`boostSpec`):**
   - Promotes UK MoD publications (`service_branch_origin: ANY("RAF", "RN")`, `boost: 0.5`) to the top of the ranked list while preserving allied sister squadron findings (`USMC`, `USAF`) immediately below.
3. **Multi-Faceted Category Aggregations (`facetSpecs`):**
   - Requests facet buckets across `service_branch_origin`, `system_subsystem_code`, and `aircraft_variant_applicability` with explicit `"limit": 10`.

# 5\. Authoritative Document Manifest Required for Demonstration

To ground Use Case 2 in GE Search and Conversation (`ukd-f35-jtd-ietm-ds` & `ukd-f35-narrative-logs-ds`) without introducing classified technical data into the demonstration sandbox, the following four synthetic OFFICIAL-tier documents are authored and indexed:

&nbsp;

| Doc ID & Format | Document Title | Use Case | Required Content Scope & Technical Details |
| :---- | :---- | :---- | :---- |
| `DOC-01` (S1000D XML / PDF) | JTD Section 53-30-01: Canopy Mechanical Rigging & Pivot Pin Lubrication | UC2 (Search) | Step-by-step mechanical rigging tolerances for the F-35 cockpit canopy forward catch/latch (`0.040 in +/- 0.010 in`), roller path clearances, `MIL-PRF-81322` pivot pin lubrication specs, and `28.5 N·m` (`252 in-lbs`) torque spanner check when no BIT fault is present. |
| `DOC-02` (JSONL / PDF) | 5-Year Joint Force Maintenance Narrative Logs (2021–2026: RAF, RN, USAF, USMC) | UC2 (Search) | 5-year synthetic corpus of "corrected-by" technician narratives using multi-service terminology (`spanner`/`wrench`, `catch`/`latch`), highlighting the USMC VMFA-211 sister squadron resolution of cured silicon sealant debris in the canopy roller path (45-minute fix saving a 14-hour actuator replacement). |
| `DOC-03` (Structured Text / PDF) | RAF Marham Squadron Pilot Post-Flight Debrief Logbook (Tail `ZM151` — 02 Nov 2026) | UC2 (Search) | Verbatim pilot post-flight debrief reporting the stiff/sticky cockpit canopy manual release handle and forward locking catch with zero BIT faults (`BIT_FAULT_ASSOCIATED = FALSE`), alongside reference to BIT `53-30-9914` micro-switch rigging checks. |
| `DOC-09` (Technical Manual PDF) | Low Observable (LO) Maintenance Manual (MAM) Section 9-1: High-Temp RAM Sheet `'B'` & 4-Hour Heater Blanket Cure | UC2 (Search) | Details thermal degradation thresholds (`220°C` boundary-layer / exhaust zone limits), prohibiting standard ambient-cure LO caulk above `150°C` and mandating `220°C` High-Temp RAM Sheet `'B'` (`NSN 8030-01-642-1190`) with a 4-hour heater blanket cure cycle at `175°C`. |

# 6\. Autonomy Boundaries & Demonstration Execution Script

## 6.1 Autonomy Boundaries & Non-Functional Requirements (NFRs)

* **Automated by Gemini Enterprise:** Conversational Text-to-SQL generation, multi-table resource joins, and Spreadsheet Card rendering (`UC 0 / 0.1 / 0.5`); partition-pruned supply/sortie analytics, tail-swap recommendations, and on-demand 16:9 presentation slide rendering (`UC 1`); dense vector retrieval, cross-service jargon translation, and verbatim citation anchoring (`UC 2`).
* **Deterministic Guardrails:** Read-only SQL AST/regex validation, 3-Layer Operational Semantic SQL Canonicalizer & zero-row auto-recovery (`canonicalize_maintenance_sql`), and deterministic Matplotlib/Vega-Lite chart synthesis.
* **Performance & Cost SLAs:** Root intent routing p95 ≤ 450 ms (`< 5 ms` fast-path interception); `UC 0 / 0.1 / 0.5` Text-to-SQL + Spreadsheet Card p95 ≤ 1.6 seconds; `UC 1` Turn 1 briefing p95 ≤ 2.5 seconds and Turn 2 16:9 chart rendering p95 ≤ 1.5 seconds; `UC 2` grounded search response p95 ≤ 2.0 seconds with 100% verbatim citation fidelity.

## 6.2 End-to-End Demonstration Storyboard (Live Walkthrough)

&nbsp;

| Demo Act & Time | Active Use Case & Persona | User Prompt / Action in Gemini Enterprise | Agent Platform Execution (GE Search, Agent Runtime & Registry) | On-Screen Deliverable & Value Proof |
| :---- | :---- | :---- | :---- | :---- |
| Act 0 (0:00 – 3:00) | UC 0 / 0.1 / 0.5: Maintenance Stand-Up, PHM Triage & SQEP/Tooling Join (Flight-Line Chief) | Queries urgent Red-X work orders across the Carrier Strike Group, triages `ZM151` post-sortie PHM/BIT faults (`PILOT_REPORT_ONLY_NO_BIT`), and joins open Priority 1/2 work orders against SQEP technicians and calibrated special tooling (`JTD-53-30-T14`). | `f35_maintenance_data_agent` canonicalizes and executes read-only BigQuery `EU` SQL across `maintenance_work_orders`, `phm_bit_fault_events`, and `work_center_tooling_and_sqep`. | Renders interactive Excel / Google Sheets Cards with status/calibration/dispatch badges (`🟡 PMC-M`, `🔴 NMC-S (MICAP)`, `🔴 BLOCKED_TOOL_OUT_OF_CAL`) and formula summary footers (< 1.6s). |
| Act 1A (3:00 – 5:00) | UC1: Conversational Analytics (Turn 1 — Squadron Logistics Officer) | Asks for RAF Marham actuator fatigue status post-sortie and 30-day regional depot stock coverage; requests tail-swap recommendation for `SRT-MAR-20261103-01`. | `f35_analytics_agent` executes partition-pruned BigQuery `EU` join across `airframe_component_telemetry`, `global_depot_inventory`, and `squadron_sortie_schedule`, caching metrics in session state. | Displays operational Markdown table showing Tail `ZM151` breach (`1,000.4` hrs), recommends auto-swap to `ZM154` (`842.0` hrs), and prompts user for chart selection (< 2.5s). |
| Act 1B (5:00 – 6:30) | UC1: On-Demand Presentation Graphics & Canvas (Turn 2) | User responds: *"Render the full 16:9 Executive Briefing Dashboard for my presentation slide deck."* | `f35_analytics_agent` executes `render_sustainment_chart` (`chart_painter.py`), rendering Full HD 16:9 slide PNG on the fly and streaming to GCS in ~500–789 ms. | Renders publication-quality 16:9 slide graphic (1920×1080 at 160 DPI) with authenticated GCS download link (`[📥 Download 16:9 Executive Slide Graphic (PNG)](https://storage.cloud.google.com/...)`) and Vega-Lite v5 Canvas. |
| Act 2 (6:30 – 10:00) | UC2: Enterprise Search (Flight-Line Avionics/Mech Tech) | Pastes pilot's free-text debrief: *"Canopy manual release handle felt stiff... no BIT faults."* Asks for likely root cause, JTD task steps, and LO RAM seam restoration rules. | `f35_jtd_search_agent` performs single-pass (`pageSize=15`) Discovery Engine `eu` retrieval + UK/US dialect normalization across `DOC-01`, `DOC-02`, `DOC-03`, and `DOC-09`. | Displays grounded diagnostic checklist citing **JTD Section 53-30-01** (`DOC-01`), USMC VMFA-211 silicon sealant debris precedent (`DOC-02`), and **MAM Section 9-1** `220°C` High-Temp RAM Sheet `'B'` 4-hr cure (`DOC-09`). |

# 7\. Verification & Validation: Search Quality and Low-Latency Query Test Suite

## 7.1 Search Result Quality & Conversational SQL Evaluation Test Cases (`UC 0 / 0.1 / 0.5`, `UC 1` & `UC 2`)

&nbsp;

| Test ID & Name | Input Query / Test Stimulus | Expected Grounded Retrieval & Behavior | Target Quality Metric & Pass Threshold |
| :---- | :---- | :---- | :---- |
| `TC-SQ-00`: Conversational Maintenance SQL & CSG Semantic Canonicalization (`UC 0`) | *"What are our most urgent maintenance jobs and grounded aircraft across the Carrier Strike Group right now, ordered by how long they will take to fix?"* | Canonicalizes Carrier Strike Group scope across `RAF Marham`, `HMS Queen Elizabeth`, and `HMS Prince of Wales`; returns all 6 active Red-X work orders (`WO-2026-88405`, `88403`, `88411`, `88414`, `88404`, `88408`) ordered by `estimated_mttr_hours DESC`. | 100% SQL Accuracy \| 6/6 Expected Rows \| Valid Spreadsheet Card & Formula Footer. |
| `TC-SQ-00.1`: Post-Sortie PHM / BIT Fault & Repeat CND Triage (`UC 0.1`) | *"Show post-sortie PHM and BIT fault events for ZM151 and flag any repeat CND or zero-BIT pilot discrepancies."* | Queries `phm_bit_fault_events`, surfacing `HRC-2710-88A`, `HRC-5330-000-NONE` (`PILOT_REPORT_ONLY_NO_BIT`, `cnd_flag=True`), and unlinked PHM advisories (`linked_work_order_id IS NULL`). | 100% Recall on `ZM151` HRCs & CND flags \| Valid Severity Badges. |
| `TC-SQ-00.5`: Multi-Table SQEP & Calibrated Tooling Join (`UC 0.5`) | *"Join open Priority 1 and Priority 2 maintenance work orders with work center tooling and SQEP availability to identify dispatch blockers."* | Executes multi-table SQL `JOIN` across `maintenance_work_orders` and `work_center_tooling_and_sqep`, identifying `JTD-53-30-T14` (`EXPIRED_OUT_OF_CAL`) and QAR shift blocks (`BLOCKED_NO_QAR_ON_SHIFT`). | 100% Join Fidelity \| Accurate Calibration & Dispatch Status Badges. |
| `TC-SQ-01`: Semantic Intent vs. Keyword Miss (`UC 2`) | Pilot debrief: *"Cockpit entry handle felt sticky and required two-handed force to lock; zero BIT faults logged."* | Bypasses electrical BIT fault trees (`bit_fault_associated = "false"`) and ranks `DOC-01` (JTD Section 53-30-01) and `DOC-02` (USMC VMFA-211 log) at the top. | Recall@3 = 100% \| MRR@5 ≥ 0.90. |
| `TC-SQ-02`: Cross-Service Dialect & Jargon Normalization (`UC 2`) | UK RAF technician queries: *"Canopy catch mechanism binding—check spanner torque and silicon fouling."* against USMC/USAF historical logs (`DOC-02`). | Bridges UK/US terminology (`catch` ↔ `latch`, `spanner` ↔ `wrench`, `binding` ↔ `stiff`) to retrieve the USMC sister squadron silicon sealant debris roller-path fix (`DOC-02`). | NDCG@5 ≥ 0.92 \| Cross-Service Synonym Recall ≥ 95%. |
| `TC-SQ-05`: Multi-Document Thermal & Material Cross-Reference + Contextual Tail-Swap (`UC 1` & `UC 2`) | Follow-up on `220°C` High-Temp RAM Sheet `'B'` 4-hr cure (`DOC-09`) and `SRT-MAR-20261103-01` tail swap (`ZM151` → `ZM154`). | Retrieves `DOC-09` (MAM Section 9-1 `220°C` High-Temp RAM Sheet `'B'`, 4-hr cure) and confirms `ZM151` → `ZM154` reallocation (`NSN 1680-01-619-4821`). | Recall@3 = 100% \| Context Relevance ≥ 0.95. |

## 7.2 Low-Latency Query Performance & Scalability Test Cases (`UC 0`, `UC 1` & `UC 2`)

&nbsp;

| Test ID & Name | Workload & Architectural Mechanism Tested | Instrumentation & Execution Path | Target Latency SLA (p50 / p95) & Cost Benchmark |
| :---- | :---- | :---- | :---- |
| `TC-LP-00`: Conversational Maintenance SQL & Spreadsheet Card SLA (`UC 0 / 0.1 / 0.5`) | Single-table and multi-table `JOIN` queries across `maintenance_work_orders`, `phm_bit_fault_events`, and `work_center_tooling_and_sqep` (300 combined rows in 600-row warehouse). | Enforces `< 0.2 ms` semantic SQL canonicalization (`canonicalize_maintenance_sql`), BigQuery `EU` partition/cluster pruning, and Spreadsheet Card rendering. | SQL Execution p95 ≤ 350 ms \| End-to-End Spreadsheet Card p95 ≤ 1,600 ms. |
| `TC-LP-01`: Sub-Second Intent Classification & Sub-Agent Routing (`All UCs`) | High-speed classification of incoming user prompt across `UC 0`, `UC 1`, or `UC 2` via `gemini-3.8-flash` and Tier 1/2 `before_model_callback` fast-path interception. | Measures Time-to-First-Byte (TTFB) from Gemini Enterprise UI input to sub-agent invocation on Agent Runtime. | Fast-Path p95 ≤ 5 ms \| LLM Routing p95 ≤ 450 ms \| Routing accuracy ≥ 99.0%. |
| `TC-LP-02`: Low-Latency Partition-Pruned Text-to-SQL & On-Demand Charting (`UC 1`) | Natural-language query joining `airframe_component_telemetry`, `global_depot_inventory`, and `squadron_sortie_schedule` followed by Turn 2 on-demand chart rendering via `render_sustainment_chart`. | Enforces BigQuery partition pruning on `scheduled_departure_utc` and clustering on `tail_number` (`ZM151`, `ZM154`) and `nsn` (`1680-01-619-4821`). Turn 2 executes `chart_painter.py` directly from session state. | **Turn 1 (SQL + Briefing):** p95 ≤ 2,500 ms.<br/>**Turn 2 (`render_sustainment_chart`):** In-Memory Vega-Lite p95 ≤ 5 ms \| 16:9 Matplotlib Render + GCS Upload p95 ≤ 790 ms (< 1,500 ms SLA). |
| `TC-LP-03`: Context-Cached Grounded RAG & Single-Pass Retrieval (`UC 2`) | Flight-line technician queries against JTD Section 53-30-01 (`DOC-01`), USMC Narrative Logs (`DOC-02`), and MAM Section 9-1 (`DOC-09`) using single-pass (`pageSize=15`) Discovery Engine `eu` search. | Pre-caches core S1000D system instructions and JTD reference headers; strips HTML snippet tags in memory (`PERF-04`). | Discovery Engine Retrieval p95 ≤ 300 ms \| End-to-End Grounded Answer p95 ≤ 2,000 ms. |
| `TC-LP-05`: Concurrent Squadron Surge & Degraded Link Resilience (`All UCs`) | Concurrent flight-line users issuing mixed `UC 0`, `UC 1`, and `UC 2` queries over a simulated tactical edge link. | Load-testing harness against Agent Runtime endpoints with compact JSON/Vega-Lite/Spreadsheet payload compression (< 120 KB per response). | Zero HTTP 429/5xx timeouts \| Payload size ≤ 120 KB. |
