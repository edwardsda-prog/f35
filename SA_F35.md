# Solution Design Document: F-35 Fleet Sustainment — Gemini Enterprise Demonstrations

## Dual-Phase Specification: Demonstration Sandbox & Accredited Production Target ( Conversational Analytics, Enterprise Search, and Agentic AI )

Document ID: SDD-GE-F35-001 \| Author: David Edwards (Customer Engineer, UK Public Sector) \| Date: 2026-11-04 \| Version: 1.3 \| Status: Demonstration & Target Architecture Specification (Enhanced with On-the-Fly Presentation Chart Painter & GCS Slide Delivery)

Executive Summary: This Solution Design Document (SDD) defines the target architecture, database schemas, and authoritative document corpus required to demonstrate Gemini Enterprise and the Agent Platform across fifth-generation F-35 Lightning II sustainment workflows. Following a dual-track delivery model, the design aligns the Google Cloud Demonstration Sandbox and the Production Target around the unified Agent Platform—comprising Gemini Enterprise (GE) Search and Conversation, Agent Runtime, and Agent Registry (explicitly excluding Agent Gateway for the demonstration). While safety-critical structural math (MIL-HDBK-516C / DEF STAN 00-970) remains strictly deterministic with Human-in-the-Loop (HITL) engineering oversight, Gemini Enterprise compresses time-to-insight and time-to-action from days to minutes across three progressive use cases.

# 1\. Document Control & Programme Scope

&nbsp;

| Metadata Field | Specification Value |
| :---- | :---- |
| Document ID & Title | SDD-GE-F35-001 — F-35 Fleet Sustainment: Gemini Enterprise Demonstrations |
| Author & Role | David Edwards — Customer Engineer, Google Cloud UK/IE Public Sector & Defense |
| Target Platform | Gemini Enterprise & Agent Platform (GE Search & Conversation, Agent Runtime, Agent Registry) |
| Operational Domain | Fifth-Generation Fighter Sustainment (RAF Marham / Joint F-35 Force ODIN & ALIS) |
| Demonstration Scope | UC 0 / 0.1 / 0.5: Maintenance Data Stand-Up, PHM/BIT Triage & Multi-Table Resource Join \| UC1: Conversational Analytics & Charting \| UC2: Enterprise Search \| UC3: Agentic AI Orchestration |
| Reference Baseline | Aligned with SDD-GE-UKD-002 (Gemini Enterprise demo design) and Enterprise Agent SDD v2.0 |

## 1.1 Strategic Context & Dual-Track Delivery Approach

Fifth-generation aircraft sustainment generates petabytes of structured sensor telemetry alongside millions of pages of unstructured technical publications and human maintenance narratives. Traditional sustainment portals suffer from data siloization—separating relational logistics databases from Joint Technical Data (JTD) manuals and Non-Destructive Inspection (NDI) imagery. Building on the dual-track methodology established in internal UK Defence reference architectures (Gemini Enterprise [demo design) and the Enterpr](https://drive.google.com/open?id=1U25WbkVxLApE4JncbTeaDNOG1RIrAg5RW3YvuCqMjdg)ise Agent Solution Design template (Solution D[esign Document Template.md), this so](https://drive.google.com/file/d/1GRItHQcn_Z9fzSOcvLc-LNs-M76bIRc4/view?usp=drivesdk&resourcekey=0-TqzO2csxHtpXn7SmZF2W7g)lution establishes two parallel execution environments:

* Demonstration Track (Immediate Pilot Sandbox): A cloud-hosted demonstration environment running on Google Cloud Platform (GCP). It showcases Gemini Enterprise and the Agent Platform—specifically GE Search and Conversation, Agent Runtime (hosting ADK 2.0 agents), and Agent Registry—backed by BigQuery (`ukd_f35_sustainment_demo`), interactive two-turn on-demand chart rendering via `render_sustainment_chart` (backed by on-the-fly Matplotlib chart painting with dynamic GCS slide upload and clickable PNG downloads alongside inline Vega-Lite Canvas specs), and Human-in-the-Loop (HITL) review interfaces. For the purpose of the demonstration, Agent Gateway is omitted in favor of direct integration between Gemini Enterprise, Agent Registry, and Agent Runtime.  
* Production Track (Accredited Sovereign Target): The target-state military deployment hosting Gemini Enterprise and the full Agent Platform (GE Search and Conversation, Agent Runtime, and Agent Registry) on Google Distributed Cloud (GDC) Air-Gapped appliances, integrated with live Lockheed Martin / JPO ODIN relational nodes, MIL-STD-1553 / ARINC 429 flight-line ingestion pipelines, S1000D XML Interactive Electronic Technical Manuals (IETMs), and Human-in-the-Loop engineering review portals.

## 1.2 Summary of the Four Demonstration Use Cases

&nbsp;

| Use Case & Modality | Operational Scenario | Data Viewpoint | Trad. Time-to-Action | Gemini Time-to-Action |
| :---- | :---- | :---- | :---- | :---- |
| UC 0: Conversational Maintenance Data Text-to-SQL + Spreadsheet Card | Morning Maintenance Stand-Up & ODIN Work Order Triage (Conversational Text-to-SQL against Table 7 `maintenance_work_orders`, 100 records across RAF Marham & HMS Queen Elizabeth; status badges, formula summary row & clickable CSV export). | Structured Data Only (BigQuery SQL Table 7: `maintenance_work_orders` — ODIN / MOD Form 707A, 100 records) | 45 to 90 Minutes (Manual ODIN/ERP exports, Excel pivot tables & status color-coding) | Near-Instantaneous (< 1.5s Text-to-SQL + Spreadsheet Card & automatic `.CSV` download link) |
| UC 0.1: Post-Sortie PHM / BIT Fault & Repeat CND Triage | Post-flight Portable Maintenance Aid (PMA) Health Reporting Code (`HRC`) triage, `PILOT_REPORT_ONLY_NO_BIT` anomaly isolation (`ZM151` Canopy Latch), repeat `CND` rogue fault detection, and unactioned PHM advisories (`linked_work_order_id IS NULL`). | Structured Data Only (BigQuery SQL Table 8: `phm_bit_fault_events`, 100 records) | 60 to 120 Minutes (Manual PMA log reconciliation & CND correlation) | Near-Instantaneous (< 1.5s Text-to-SQL + PHM Severity/CND Badges & `.CSV` export) |
| UC 0.5: Multi-Table Shift Dispatch, SQEP & Calibrated Tooling Join | Conversational 2- and 3-table SQL `JOIN` across `maintenance_work_orders`, `work_center_tooling_and_sqep`, and `phm_bit_fault_events` to check SQEP technician headcount, QAR availability, and calibrated special tools (`JTD-53-30-T14`, `NDI-PAUT-496A`, `LO-IR-BLANKET-04`). | Structured Multi-Table Join (BigQuery SQL Tables 7, 8 & 9 — 300 combined records in 900-record warehouse) | 90 to 180 Minutes (Manual cross-checking of shift rosters, calibration logs & Form 707A work orders) | Near-Instantaneous (< 1.6s Multi-Table SQL `JOIN` + Calibration/Dispatch Badges & `.CSV` export) |
| UC1: Conversational Analytics + On-Demand Charts | Automatic Part Replenishment & Fleet Readiness (Tail ZM151 Left Horizontal Tail Actuator S/N ACT-99812-F exceeding 1,000-hr limit at 1,000.4 hrs; NSN 1680-01-619-4821 stock = 4). | Structured Data Only (BigQuery SQL Telemetry, Inventory & Sortie Schedules) | 2 to 4 Hours (Manual SQL, ERP lookups & shift replanning) | Near-Instantaneous (< 2.5s query + on-demand 16:9 presentation slide rendering & GCS upload in ~500–789 ms) |
| UC2: Enterprise Search (Grounded RAG) | Intermittent "Sticky" Cockpit Canopy Latch (Subjective pilot debrief with zero BIT faults; semantic correlation across JTD Section 53-30-01 & sister squadron silicon debris logs). | Unstructured Data Only (JTD/IETM Manuals, Pilot Debriefs & 5-Yr Maintainer Logs) | 4 to 8 Hours (Manual keyword search across XML/PDF manuals) | 10 to 15 Minutes (Direct semantic match \+ multi-service translation) |
| UC3: Agentic AI (Multi-Agent Orchestrator) | Dynamic Flight Envelope Exceedance & Airworthiness Recertification (Mach 1.3 asymmetrical pull-up on Frame 496; 104.2% yield load; 0.012-in hole elongation on Ti-6Al-4V Lot \#8841-B vs 0.015-in limit). | Converged Structured & Unstructured Data \+ Deterministic Physics (Miner's Rule) | 36 to 72 Hours (Manual data fusion, CAD mapping & Form 700 routing) | 1 to 2 Hours (Automated Structural Appraisal Report staged for Human-in-the-Loop review) |

# 2\. Target Architecture: Gemini Enterprise & Agent Platform Topology

The target architecture centers on Gemini Enterprise coupled with the unified Agent Platform, comprising GE Search and Conversation, Agent Runtime (powered by ADK 2.0), and Agent Registry, following the architectural blueprint in the Enterprise Agent Solution Design standard (Solution Design Document [Template.md) and tactical edge sust](https://drive.google.com/file/d/1GRItHQcn_Z9fzSOcvLc-LNs-M76bIRc4/view?usp=drivesdk&resourcekey=0-TqzO2csxHtpXn7SmZF2W7g)ainment designs (Presentation Stor[yboard \- Pixel Roots Demo 1). For the purpos](https://docs.google.com/document/d/1xPBs4G_LbHID6whn4zKzKkTMkG0FTOa-c0lpYcv3Ndg/edit?usp=drivesdk&ouid=115969398345850679057&resourcekey=0-hdKCRNyMVCMjbXzbBkhv1g)e of the demonstration, Agent Gateway is intentionally excluded—agents registered in Agent Registry are invoked directly by Gemini Enterprise on the Agent Runtime and connect directly to backend data stores and deterministic microservices via Google MCP Toolbox.

* Gemini Enterprise & GE Search and Conversation (\`gemini-3.8-flash\` Router): Serves as the unified front-of-house experience, conversational orchestration layer, and enterprise search bar. Evaluates user prompts and discovers published sustainment agents via Agent Registry to route ad-hoc maintenance work-order queries and spreadsheet requests to UC0, structured supply/readiness analytical and charting requests to UC1, unstructured technical manual lookups to UC2, and multi-disciplinary airworthiness workflows to UC3.  
* UC0 Maintenance Data Text-to-SQL & Spreadsheet Card Agent (`f35_maintenance_data_agent` on Agent Runtime / `gemini-3.8-flash`): Translates natural-language maintenance logbook and ODIN work-order queries into read-only BigQuery Standard SQL (`SELECT`) against Table 7 (`maintenance_work_orders`), returning an Excel / Google Sheets-like Spreadsheet Card with Column Letters (`A`..`R`), Status Badges (`🟢 FMC`, `🟡 PMC-M`, `🟠 NMC-M`, `🔴 NMC-S (MICAP)`), Formula Summary Footer Rows (`=COUNTA()`, `=SUM()`, `=AVERAGE()`), and an automatic clickable `.CSV` download link (`https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/exports/...`).  
* UC1 Conversational Analytics & Charting Agent (`f35_analytics_agent` on Agent Runtime / `gemini-3.8-flash`): Registered in Agent Registry and executed on Agent Runtime. Translates natural language supply and readiness questions into partition-pruned BigQuery SQL via Google MCP Toolbox (bypassing Agent Gateway in the demo); outputs structured operational tabular summaries in Turn 1 and renders presentation-ready 16:9 Full HD widescreen PNG slide graphics (uploaded dynamically to GCS with authenticated slide-deck download links) and interactive Vega-Lite v5 JSON specifications on Turn 2 via the dedicated `render_sustainment_chart` tool.  
* UC2 Enterprise Search & Grounded RAG (\`f35\_jtd\_search\_agent\` on GE Search and Conversation \+ \`gemini-3.1-pro\`): Powered natively by GE Search and Conversation over chunked S1000D XML/PDF manuals (500 tokens per chunk, 100-token overlap) and historical narrative logs (\`ukd-f35-jtd-ietm-ds\` & \`ukd-f35-narrative-logs-ds\`). Executes dense vector matching and cross-service jargon normalization (USAF/USMC/RN/RAF) with mandatory inline clickable citations.  
* UC3 Airworthiness Sustainment Orchestrator (\`f35\_airworthiness\_orchestrator\` on Agent Runtime \+ Agent Registry): Engineered with ADK 2.0, catalogued in Agent Registry, and hosted on Agent Runtime. Coordinates a deterministic, Human-in-the-Loop (HITL) workflow—invoking external physics microservices (Palmgren-Miner cumulative damage and Rainflow counting), extracting spatial defect coordinates from multimodal NDI C-scan imagery, joining mBOM fastener lot records in BigQuery, and compiling a MIL-STD-3001 Structural Appraisal Report and draft Aircraft Form 700 / AFTO Form 781 for human engineering review.

&nbsp;

| Architectural Layer | Demonstration Sandbox (GCP Pilot) | Production Target (GDC Air-Gapped / ODIN) |
| :---- | :---- | :---- |
| Gemini Enterprise & Agent Registry | Gemini Enterprise Web UI (inline Vega-Lite Canvas & HITL Review Studio) \+ Agent Registry cataloguing UC1–UC3 agents (No Agent Gateway in Demo). | Gemini Enterprise Squadron Portal & Sovereign Agent Registry governing fleet-wide sustainment agents on GDC Air-Gapped. |
| Agent Platform: GE Search & Conversation (UC2) | GE Search and Conversation indexing synthetic JTD/IETM manuals (\`ukd-f35-jtd-ietm-ds\`) & 5-yr narrative logs on GCS. | GDC Air-Gapped GE Search and Conversation indexing live JPO S1000D XML IETMs & FRACAS repositories. |
| Agent Platform: Agent Runtime (UC1 & UC3) | Managed Agent Runtime executing ADK 2.0 agents (\`f35\_analytics\_agent\` & \`f35\_airworthiness\_orchestrator\`) with direct MCP tool calls (Agent Gateway omitted). | Sovereign Agent Runtime on GDC Air-Gapped executing accredited ADK 2.0 multi-agent sustainment workflows. |
| Structured Data & Deterministic Physics (UC1 & UC3) | BigQuery (\`ukd\_f35\_sustainment\_demo\`) \+ Cloud Run Python microservice executing Rainflow & Miner's Rule math \+ 3D CAD join. | Sovereign AlloyDB / ODIN ERP \+ accredited ASIP (Aircraft Structural Integrity Program) FEM solver & PLM CAD server. |
| Human-in-the-Loop (HITL) Review Gate (UC3) | Interactive Review Studio staging the Structural Appraisal Report & Form 700 for human engineer confirmation. | Human-in-the-Loop engineering verification and release confirmation inside the MOD Engineering Quality Portal. |

# 2.5 Use Case 0 Design: Conversational Maintenance Data Text-to-SQL & Excel / Google Sheets Card (`maintenance_work_orders`)

## 2.5.1 Operational Narrative & Pure Dynamic Text-to-SQL Pattern
Before diving into multi-table sortie swaps (UC1), unstructured manual lookups (UC2), or structural recertification (UC3), Squadron Maintenance Officers and Flight-Line Chiefs begin their shift at the **Morning Maintenance Stand-Up** by querying the **Lockheed Martin ODIN / UK MOD Form 707A Aircraft Maintenance Log Work Orders** ledger (`maintenance_work_orders`).

In **Use Case 0 (`@F35-Maintenance-Data`)**, the sub-agent (`f35_maintenance_data_agent`) embeds the complete semantic schema of `antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders` (`location="EU"`), writes a custom read-only BigQuery Standard SQL `SELECT` query directly from the user's natural language prompt (supporting `WHERE` filters, `ORDER BY`, `LIMIT`, and `GROUP BY` aggregations), validates it via a deterministic read-only SQL guardrail, executes it in `< 350 ms`, uploads the result set to `gs://antig-dave-f35-staging-europe-west1/exports/<sheet_id>.csv`, and returns an **Excel / Google Sheets-like Spreadsheet Card** directly in the Gemini Enterprise UI.

## 2.5.2 Table 7 Schema & Semantic Descriptions (`maintenance_work_orders`)

| Table 7: `maintenance_work_orders` (Col A–R) | Data Type | Key / Constraint | Semantic Column Description & Sample Value |
| :--- | :--- | :--- | :--- |
| `A: work_order_id` | STRING | PRIMARY KEY | Unique ODIN / MOD Form 707A maintenance work order identifier (`WO-2026-707A-0101`). |
| `B: tail_number` | STRING | CLUSTER KEY | UK military aircraft registration tail identifier (`ZM151`, `ZM152`, `ZM154`, `ZM155`, `ZM158`, `ZM161`, `ZM163`). |
| `C: aircraft_variant` | STRING | NOT NULL | F-35 variant designation: `F-35A` (CTOL) or `F-35B` (STOVL). |
| `D: squadron` | STRING | NOT NULL | Assigned operational squadron: `617 Sqn (The Dambusters)`, `207 Sqn (OCU)`, or `809 NAS (The Immortals)`. |
| `E: base_location` | STRING | NOT NULL | Current operating station or carrier deployment base: `RAF Marham` or `HMS Queen Elizabeth`. |
| `F: aircraft_status` | STRING | CLUSTER KEY | DoD/MOD availability status code: `FMC`, `PMC-M`, `NMC-M`, or `NMC-S`. |
| `G: work_order_status` | STRING | NOT NULL | Work order execution status: `OPEN`, `IN_PROGRESS`, `AWAITING_PARTS`, `AWAITING_NDI`, or `CLOSED`. |
| `H: priority_level` | STRING | NOT NULL | Maintenance priority tier: `PRIORITY_1_EMERGENCY`, `PRIORITY_2_URGENT`, or `PRIORITY_3_ROUTINE`. |
| `I: micap_flag` | BOOL | NOT NULL | Mission Capable (`MICAP`) critical supply shortage flag (`true` / `false`). |
| `J: lcn_code` | STRING | NOT NULL | 4-digit Logistics Control Number / Work Unit Code (`27-10`, `53-30`, `53-11`, `72-00`, `34-40`, `94-10`). |
| `K: subsystem_name` | STRING | NOT NULL | Human-readable aircraft subsystem nomenclature (`Flight Controls — Horizontal Tail Actuator`). |
| `L: discrepancy_summary` | STRING | NOT NULL | Pilot or maintenance technician discrepancy write-up from MOD Form 707A / ODIN fault report. |
| `M: action_taken_code` | STRING | NOT NULL | Standardized Action Taken Code: `R` (Remove & Replace), `G` (Repair & Adjust), `Y` (Troubleshoot/Clean/Lube), `Z` (NDI), `Q` (LO RAM Cure), `P` (Awaiting Supply). |
| `N: assigned_bay` | STRING | NOT NULL | Assigned hangar bay or work center (`Marham Hangar 2 - Bay 4`, `HMS QE Hangar Deck Bay 2`). |
| `O: logged_man_hours` | FLOAT64 | NOT NULL | Cumulative direct maintenance technician man-hours logged against this work order (`6.5`). |
| `P: estimated_mttr_hours` | FLOAT64 | NOT NULL | Estimated Mean Time To Repair (`MTTR`) in hours required to complete the work order (`12.0`). |
| `Q: etic_utc` | TIMESTAMP | NULLABLE | Estimated Time In Commission (`ETIC`) timestamp in UTC when the aircraft returns to FMC. |
| `R: created_at_utc` | TIMESTAMP | PARTITION KEY | UTC timestamp when the maintenance work order was opened (`DAY` partitioning). |

## 2.5.3 Table 8 (`phm_bit_fault_events` — UC 0.1) & Table 9 (`work_center_tooling_and_sqep` — UC 0.5)

To support the full **Act 0 Trilogy (`UC 0` → `UC 0.1` → `UC 0.5`)** and ensure referential consistency across the entire **9-Table, 900-Record F-35 Data Warehouse** (`100` records per table across Tables 1–9 in `antig-dave.ukd_f35_sustainment_demo`), two companion operational tables are provisioned in BigQuery `EU`:

1. **Table 8 (`phm_bit_fault_events` — UC 0.1, 100 Records, Partitioned on `fault_timestamp_utc`, Clustered on `tail_number, fault_severity`):**
   - Tracks post-sortie PHM Health Reporting Codes (`hrc_code`), `fault_severity` (`CRITICAL_GROUNDING`, `DEGRADED_PMC`, `ADVISORY_PHM`, `NO_BIT_FAULT_LOGGED`), `bit_trigger_type` (`CONTINUOUS_BIT`, `INITIATED_BIT`, `PHM_PROGNOSTIC_THRESHOLD`, `PILOT_REPORT_ONLY_NO_BIT`), `recurrence_count_30d`, `cnd_flag`, `diagnostic_confidence_pct`, and `linked_work_order_id` (foreign key to `maintenance_work_orders.work_order_id`, including `NULL` for unactioned advisories).
2. **Table 9 (`work_center_tooling_and_sqep` — UC 0.5, 100 Records, Partitioned on `shift_updated_utc`, Clustered on `base_location, work_center`):**
   - Supports dual-key SQL `JOIN`s via `assigned_work_order_id` (`1:1` with `maintenance_work_orders.work_order_id`) and `(base_location, work_center, supported_wuc_code)`. Tracks `sqep_certification_domain`, `sqep_certified_techs_on_shift`, `qar_inspector_available`, `required_special_tool_id` (`JTD-53-30-T14`, `NDI-PAUT-496A`, `LO-IR-BLANKET-04`), `tool_calibration_status` (`CALIBRATED_SERVICEABLE`, `CALIBRATION_DUE_WARNING`, `EXPIRED_OUT_OF_CAL`, `IN_USE_OTHER_BAY`), and `bay_dispatch_status` (`READY_TO_DISPATCH`, `BLOCKED_TOOL_OUT_OF_CAL`, `BLOCKED_NO_QAR_ON_SHIFT`, `BLOCKED_AWAITING_MICAP_PART`).

# 3\. Use Case 1 Design: Conversational Analytics with Simple Charts (Structured Data)

## 3.1 Operational Narrative & Gemini Capabilities

When F-35A Tail `ZM151` lands at RAF Marham after a training sortie, its onboard computer uploads flight usage telemetry to ODIN. The Left Horizontal Tail Actuator (`S/N: ACT-99812-F`) reaches `1,000.4` flight hours, breaching its `1,000.0`-hour structural fatigue threshold. In the Gemini Enterprise demo, the Squadron Logistics Officer or Commander interacts with the `@F35-Sustainment-Analytics` agent using natural language rather than legacy ERP drop-downs.

To guarantee responsive flight-line interaction (< 2.5s SLA) and eliminate token generation latency spikes, Use Case 1 operates via a **Two-Turn Visualization Workflow**:

* **Turn 1: Text-to-SQL Generation & Operational Briefing:**
  - The user asks: *"Check RAF Marham F-35A horizontal tail actuator hours against our 30-day depot stock with visual charts, and recommend a tail swap for morning sortie SRT-MAR-20261103-01."*
  - Gemini translates this into an optimized partition-pruned SQL query joining `airframe_component_telemetry`, `global_depot_inventory`, and `squadron_sortie_schedule`.
  - The agent emits a structured Markdown summary table, recommends reallocating Pilot Henderson's sortie to Spare Tail `ZM154` (`842.0` hrs, Mission Capable), confirms depot replenishment for `NSN: 1680-01-619-4821` (4 on hand, 2 reserved, 18-hr ETA), and **explicitly prompts the user for chart selection**:
    > *"Would you like me to render:*  
    > *1. **Actuator Fatigue Threshold Chart** (Tail ZM151 at 1,000.4 hrs vs ZM154 at 842.0 hrs vs 1,000.0-hr threshold)*  
    > *2. **Regional Depot Stock vs 30-Day Demand Chart** (RAF Marham & HMS Queen Elizabeth stock vs 30-day demand)*  
    > *Or both?"*
  - Structured query records are cached in ADK session state (`tool_context.session.state["last_uc1_metrics"]`).

* **Turn 2: On-Demand Presentation Graphics & Canvas Rendering (`render_sustainment_chart`):**
  - When the user requests a chart (e.g., *"Render the Actuator Fatigue Threshold Chart"* or *"Render the full 16:9 Executive Briefing Dashboard for my presentation slide deck"*), the agent dispatches the dedicated `render_sustainment_chart` tool.
  - **Dynamic On-the-Fly Presentation Graphics (`chart_painter.py`):** The tool executes headless Matplotlib (`Agg` backend) to dynamically synthesize a 16:9 Full HD widescreen presentation graphic (1920×1080 at 160 DPI) in the Clean Light Briefing Theme directly in memory from queried BigQuery records. Visual assets are **not** static pre-existing images; they are programmatically drawn on the fly.
  - **Dynamic GCS Push & Slide Download Links:** Streams rendered PNG bytes to `gs://antig-dave-f35-staging-europe-west1/charts/<filename>.png` in real time (~150–250 ms), returning authenticated HTTPS download links (`[📥 Download 16:9 Executive Slide Graphic (PNG)](https://storage.cloud.google.com/...)`) for direct insertion into executive slide decks (PowerPoint / Keynote), alongside inline Markdown image embeds.
  - **Interactive Gemini Enterprise Canvas:** Concurrently populates clean Vega-Lite v5 JSON specifications for interactive exploration in Gemini Enterprise Canvas (`VegaCanvas.tsx`).
  - **Session State Cache:** Caches rendered assets in `tool_context.session.state["cached_graphics_{chart_name}"]` to prevent redundant re-renders within the same session. Total on-the-fly rendering and upload completes in ~500–789 ms, well under the 1,500 ms SLA (`PERF-08`).

## 3.2 Structured Database Schemas (BigQuery: ukd\_f35\_sustainment\_demo)

Three relational tables in Google Cloud BigQuery power Use Case 1\. Partitioning and clustering are configured to guarantee sub-2-second conversational query performance.

&nbsp;

| Table 1: airframe\_component\_telemetry | Data Type | Key / Constraint | Description & Demo Sample Value |
| :---- | :---- | :---- | :---- |
| telemetry\_record\_id | STRING | PRIMARY KEY | Unique post-flight upload identifier (e.g., \`TEL-20261102-0941\`) |
| tail\_number | STRING | PARTITION / CLUSTER | Aircraft identifier (e.g., \`ZM151\`, \`ZM154\`) |
| aircraft\_variant | STRING | NOT NULL | F-35 variant (\`F-35A\`, \`F-35B\`) |
| base\_location | STRING | NOT NULL | Assigned operating base (\`RAF Marham\`, \`HMS Queen Elizabeth\`) |
| part\_serial\_number | STRING | CLUSTER KEY | Installed component S/N (\`ACT-99812-F\`) |
| nsn | STRING | FOREIGN KEY | NATO Stock Number (\`1680-01-619-4821\`) |
| component\_name | STRING | NOT NULL | \`Left Horizontal Tail Actuator\` |
| current\_flight\_hours | FLOAT64 | NOT NULL | Accumulated hours post-sortie (\`1000.4\` vs \`1000.0\` limit) |
| life\_limit\_threshold\_hrs | FLOAT64 | NOT NULL | Mandated replacement threshold (\`1000.0\`) & status (\`PMC-M\`) |

&nbsp;

| Table 2: global\_depot\_inventory | Data Type | Key / Constraint | Description & Demo Sample Value |
| :---- | :---- | :---- | :---- |
| nsn | STRING | PRIMARY KEY | 13-digit NATO Stock Number (\`1680-01-619-4821\`) |
| part\_name | STRING | NOT NULL | \`Actuator, Electro-Hydrostatic Horizontal Tail\` |
| depot\_id & depot\_name | STRING | CLUSTER KEY | \`DEP-UK-01\` (\`RAF Marham Regional Sustainment Depot\`) |
| quantity\_on\_hand | INT64 | NOT NULL | Available serviceable units in stock (\`4\`) |
| quantity\_reserved\_30d | INT64 | NOT NULL | Forecasted fleet demand over next 30 days (\`2\`) |
| reorder\_point\_threshold | INT64 | NOT NULL | Minimum stock trigger (\`2\`) |
| avg\_shipping\_eta\_hours | FLOAT64 | NOT NULL | Standard transit time to squadron hangar (\`18.0\` hours) |

&nbsp;

| Table 3: squadron\_sortie\_schedule | Data Type | Key / Constraint | Description & Demo Sample Value |
| :---- | :---- | :---- | :---- |
| sortie\_id | STRING | PRIMARY KEY | Scheduled mission ID (\`SRT-MAR-20261103-01\`) |
| scheduled\_departure\_utc | TIMESTAMP | PARTITION KEY | \`2026-11-03T07:30:00Z\` (Morning training wave) |
| assigned\_tail\_number | STRING | FOREIGN KEY | Primary aircraft (\`ZM151\` — flagged for swap) |
| assigned\_pilot\_callsign | STRING | NOT NULL | \`Flt Lt Henderson (Callsign: VIPER-1)\` |
| spare\_tail\_candidate | STRING | NULLABLE | \`ZM154\` (F-35A, \`842.0\` actuator hrs, Mission Capable) |
| sortie_readiness_status | STRING | NOT NULL | `AT_RISK_MAINTENANCE` -> Auto-reallocated to `ZM154` |

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
  2. `depot_stock_vs_demand_bar_chart`: Grouped bar chart comparing available stock (`4` units) vs 30-day demand (`2` units) across RAF Marham and HMS Queen Elizabeth with net available callouts.
  3. `executive_dashboard` / `both`: Unified Full HD 16:9 widescreen presentation slide (composite dual-panel with master header, subtitle, and bottom operational decision callout banner).
* **Execution Mechanism & Data Flow:**
  - **On-the-Fly In-Memory Synthesis:** `app/tools/chart_painter.py` dynamically renders publication-quality graphics using Matplotlib (headless `Agg` backend) from live BigQuery records in session state. Visual assets are **not** static pre-existing images; they are programmatically generated on the fly.
  - **Real-Time Cloud Storage Push:** `upload_chart_to_gcs` streams rasterized PNG bytes to `gs://antig-dave-f35-staging-europe-west1/charts/` and formats authenticated HTTPS links.
  - **Session State Caching:** Saves generated assets to `session.state["cached_graphics_{chart_name}"]` for zero-latency retrieval if re-requested.
  - **Dual Output:** Returns both presentation PNG download links for slide decks and deterministic Vega-Lite v5 JSON specs for Gemini Enterprise Canvas.
* **Baseline Diagram Generation Metrics & Performance SLAs (`PERF-08`):**
  - In-Memory Vega-Lite JSON Template: **1.8 ms** code execution latency
  - On-the-Fly Full HD Matplotlib Rendering: **300–450 ms**
  - GCS Streaming Upload: **150–250 ms**
  - Total End-to-End Graphic Generation & Delivery: **501–789 ms** (Target SLA: `< 1,500 ms`)

# 4. Use Case 2 Design: Enterprise Search & Grounded Reasoning (Unstructured Data)

## 4.1 Operational Narrative & Semantic Search Architecture

A pilot returns from a night sortie and logs a free-text complaint: "Canopy manual release handle felt stiff and hesitated to latch fully during pre-flight. Required physical force to secure. No cockpit warnings or BIT faults displayed." Traditional keyword searches for "canopy manual release" fail to match historical write-ups that use different phrasing. In Use Case 2, the flight-line technician queries GE Search and Conversation inside Gemini Enterprise (\`@F35-JTD-Search\`).

* Dense Vector Semantic Retrieval (GE Search and Conversation): GE Search and Conversation converts the pilot's symptom description into dense embeddings, bypassing electrical BIT fault trees and isolating mechanical rigging procedures in \*\*JTD Section 53-30-01 ("Canopy Mechanical Rigging Inspection")\*\*.  
* Cross-Service Dialect & Jargon Normalization: Gemini synthesizes 5 years of historical unstructured logs across US Air Force, US Marine Corps, Royal Navy, and RAF squadrons—bridging terminology differences ("latch assembly" vs. "catch mechanism", "wrench" vs. "spanner", "binding" vs. "stiff"). It surfaces a sister squadron fix: "Found silicon sealant debris wedge in roller path, causing handle stiffness. Cleaned assembly per JTD and lubed pivot pin."  
* Grounded Output with Verbatim Citations: The agent delivers a concise, step-by-step inspection checklist linked directly to the exact page and paragraph of JTD Section 53-30-01, ensuring zero hallucinated torque values or unauthorized lubricants.

## 4.2 Unstructured Data Store & Metadata Schema (GE Search & Conversation: ukd-f35-jtd-ietm-ds)

To enable faceted filtering, subsystem routing, and precise citation anchoring in GE Search and Conversation, each ingested unstructured document chunk is indexed with the following JSON metadata schema:

&nbsp;

| Metadata Attribute | Field Type | Search Capability | Description & Example Value |
| :---- | :---- | :---- | :---- |
| doc\_id & chunk\_id | STRING | Retrievable / Key | \`DOC-JTD-53-30-01\#CHUNK-014\` (500-token chunk, 100-token overlap) |
| publication\_code | STRING | Filterable / Facet | \`JTD-F35-53-30-01\` or \`FRACAS-LOG-2021-2026\` |
| system\_subsystem\_code | STRING | Filterable / Facet | S1000D SNS code: \`53-30\` (Fuselage — Canopy & Framing) |
| aircraft\_variant\_applicability | ARRAY\<STRING\> | Filterable | \`\["F-35A", "F-35B", "F-35C"\]\` |
| service\_branch\_origin | STRING | Filterable / Facet | \`RAF\`, \`RN\`, \`USAF\`, \`USMC\` (enables cross-service translation) |
| bit\_fault\_associated | BOOLEAN | Filterable | \`false\` (allows boosting mechanical rigging docs when BIT \= None) |
| document\_version\_date | STRING | Filterable / Sortable | \`2026-10-15\` (ensures retrieval of the latest JTD / SRM revision) |

## 4.3 Discovery Engine Query Architecture: Metadata Filtering, Relevance Boosting & Facet Aggregations

To achieve high precision, zero hallucination, and sub-2-second retrieval (\`TC-LP-03\`) across heterogeneous MoD and DoD technical publications, the UC2 Search Agent (\`f35_jtd_search_agent\`) interfaces with the Gemini Enterprise Discovery Engine EU multi-region endpoint (\`https://eu-discoveryengine.googleapis.com/v1alpha/projects/antig-dave/locations/eu/...\`) using structured metadata query primitives:

### 1. Structured Metadata Filtering (\`filter\`)
When the maintenance technician reports mechanical symptoms without Built-In-Test (BIT) fault annunciations, the agent constructs server-side filter expressions over the indexed \`jsonData\` schema:
* **Boolean Quoting Requirement:** In Discovery Engine, boolean values on JSON fields must be passed as quoted string literals: \`bit_fault_associated = "false"\` (unquoted literals return HTTP 400).
* **Subsystem Scoping:** \`system_subsystem_code: ANY("53-30")\` isolates ATA/S1000D chapters (e.g. Canopy & Framing), filtering out extraneous electrical or engine technical data.
* **Resilient Two-Stage Execution:** If a strict metadata filter returns zero hits due to an unindexed variant or tag mismatch, the tool automatically executes an immediate fallback query with the filter relaxed to ensure flight-line technicians never receive false-negative empty sets.

### 2. Dynamic Soft Relevance Boosting (\`boostSpec\`)
Rather than hard-filtering out allied datasets—which would hide critical cross-service precedents such as the US Marine Corps VMFA-211 canopy sealant fix (\`DOC-02\`)—the search agent employs soft relevance boosting:
* **Host Nation / Service Prioritization:**
  \`\`\`json
  {
    "condition": "service_branch_origin: ANY(\"RAF\", \"RN\")",
    "boost": 0.5
  }
  \`\`\`
* **Effect:** Promotes UK MoD publications to the top of the ranked list while preserving allied sister squadron findings (\`USMC\`, \`USAF\`) immediately below, facilitating cross-fleet intelligence sharing without manual portal hopping.

### 3. Multi-Faceted Category Aggregations (\`facetSpecs\`)
To support interactive categorization and facet filtering in Gemini Enterprise Canvas and downstream web components:
* **Facet Keys:** Requested across \`service_branch_origin\`, \`system_subsystem_code\`, and \`aircraft_variant_applicability\`.
* **Explicit Limit Invariant:** Every facet specification must supply an explicit limit (e.g. \`"limit": 10\`). In Discovery Engine, omitting \`limit\` defaults to 0, which triggers \`HTTP 400: Facet limit should be between 1 to 300\`.
* **Output Integration:** Facet bucket counts are surfaced in the tool output payload (\`metadata_facets\`), enabling drill-down counts by service branch and aircraft variant in the UI.

# 5\. Use Case 3 Design: Agentic AI Orchestration (Structured \+ Unstructured Data)

## 5.1 Operational Narrative & Deterministic Human-in-the-Loop Workflow

During an evasive combat maneuver at Mach 1.3, an F-35A (\`ZM151\`) experiences an asymmetrical rolling pull-up that momentarily exceeds the design load limit on the port-side wing carry-through bulkhead (\*\*Frame 496\*\*). Military airworthiness regulations (\*\*MIL-HDBK-516C\*\* and \*\*DEF STAN 00-970\*\*) strictly forbid black-box AI from calculating structural stress or issuing flight clearances. Instead, the \*\*@F35-Airworthiness-Agent\*\* acts as a deterministic system orchestrator:

* Step 1 — Temporal Synchronization Tool (\`sync\_flight\_bus\_exceedance\`): The agent parses the pilot's unstructured debrief ("severe shudder at roughly 14:22 Zulu during defensive split-S") and invokes a deterministic parser over the 200 Hz MIL-STD-1553 / ARINC 429 flight logs in BigQuery, anchoring the exact peak normal acceleration delta (\$\\Delta N\_z / \\Delta t\$) at \`14:22:18.420Z\` across a 3.2-second window.  
* Step 2 — Deterministic Physics Verification Tool (\`run\_asip\_miners\_rule\_engine\`): The agent passes the isolated strain-gauge time series to an accredited physics microservice executing Rainflow-Counting and Palmgren-Miner Cumulative Damage equations (\$D \= \\sum n\_i / N\_i\$). The deterministic solver returns a peak load of \*\*104.2% of Design Yield Strength\*\*, tripping mandatory \*\*Class-A Non-Destructive Inspection (NDI)\*\* under \*\*JTD Rule 53-11-00\*\*.  
* Step 3 — Multimodal NDI Scan Extraction & CAD Join (\`extract\_ndi\_defect\_and\_map\_cad\`): Technicians upload phased-array ultrasonic C-scan DICOM-TIFF images of Frame 496\. Gemini's multimodal vision reads the technician's bounding markup and extracts defect coordinates \$(X, Y, Z)\$, passing them to a spatial transform tool that joins against the 3D CAD model to identify a \*\*0.012-inch shear elongation on Fastener Hole \#14\*\*.  
* Step 4 — mBOM Relational Audit & Fleet Lot Risk Check (\`audit\_mbom\_fastener\_lot\`): The agent queries the \`as\_maintained\_mbom\` BigQuery table, verifying that Fastener \#14 is \*\*Titanium Ti-6Al-4V, Lot \#8841-B\*\* (installed 312 flight hours ago) with an allowable defect limit of \*\*0.015 inches\*\*. Because \`0.012 in \< 0.015 in\`, teardown is not required. Simultaneously, the agent queries the global fleet registry, discovering \*\*14 other aircraft\*\* fitted with \`Lot \#8841-B\`, and flags them for proactive inspection during their next 30-day check.  
* Step 5 — Automated Airworthiness Package & Human-in-the-Loop Review (\`generate\_form700\_airworthiness\_package\`): Following the Human-in-the-Loop (HITL) review pattern proven in the Royal Navy Horizon demons[tration (Royal Navy \- Hor](https://docs.google.com/document/d/1FCni260YEzFALiTHJ2thuO9LRysVtVVWDiQyfsod3aE/edit?usp=drivesdk&ouid=115969398345850679057&resourcekey=0-hM3KY9ZqglUQ0uz4pj4lrQ)izon Demo), the agent compiles the Structural Appraisal Report, attaches JTD Task Card 53-11-00-280 (Torque-Recheck), and pre-populates Aircraft Form 700 / AFTO Form 781, holding the workflow in a human-in-the-loop review state until the Lead Stress Engineer or Chief Technical Officer reviews and confirms the package.

## 5.2 Converged Database & State Schemas (BigQuery & Agent Runtime Session State)

&nbsp;

| Table 4: high\_freq\_strain\_telemetry | Data Type | Key / Constraint | Description & Demo Sample Value |
| :---- | :---- | :---- | :---- |
| event\_id & tail\_number | STRING | PRIMARY KEY / PART. | \`EXC-20261102-ZM151\` \| Tail \`ZM151\` |
| event\_window\_start\_utc | TIMESTAMP | NOT NULL | Anchored timestamp: \`2026-11-02T14:22:18.420Z\` (3.2s duration) |
| structural\_station\_id | STRING | CLUSTER KEY | \`Frame 496\` (Port-Side Wing Carry-Through Bulkhead) |
| mach\_number & peak\_nz\_g | FLOAT64 | NOT NULL | \`Mach 1.3\` \| Peak asymmetric load factor \`9.4 G\` (\$\\Delta N\_z / \\Delta t\$) |
| peak\_egt\_celsius | FLOAT64 | NOT NULL | \`220.0°C\` thermal gradient at bulkhead boundary |
| miners\_rule\_damage\_delta | FLOAT64 | DETERMINISTIC OUT | Cumulative fatigue damage increment \$D\_i \= 0.0042\$ |
| calculated\_yield\_pct | FLOAT64 | DETERMINISTIC OUT | \`104.2%\` of Design Yield Strength (triggers JTD Rule 53-11-00) |
| required\_ndi\_class | STRING | NOT NULL | \`CLASS\_A\_ULTRASONIC\_C\_SCAN\` |

&nbsp;

| Table 5: as\_maintained\_mbom\_fasteners | Data Type | Key / Constraint | Description & Demo Sample Value |
| :---- | :---- | :---- | :---- |
| mbom\_record\_id | STRING | PRIMARY KEY | \`MBOM-ZM151-F496-H14\` |
| tail\_number & station\_id | STRING | CLUSTER KEY | \`ZM151\` \| \`Frame 496 — Fastener Hole \#14\` |
| fastener\_material\_spec | STRING | NOT NULL | \`Titanium Ti-6Al-4V\` (Shear-rated structural fastener) |
| fastener\_lot\_number | STRING | INDEXED KEY | \`Lot \#8841-B\` (Cross-referenced across global fleet) |
| hours\_since\_install | FLOAT64 | NOT NULL | \`312.0\` flight hours since depot installation |
| allowable\_elongation\_in | FLOAT64 | NOT NULL | \`0.015\` inches (SRM maximum discard tolerance) |
| measured\_ndi\_elongation\_in | FLOAT64 | MULTIMODAL IN | \`0.012\` inches (Extracted from C-Scan \+ CAD spatial join) |
| global\_fleet\_affected\_count | INT64 | NOT NULL | \`14\` other F-35 tails globally carrying \`Lot \#8841-B\` |

&nbsp;

| Table 6: airworthiness\_release\_ledger | Data Type | Key / Constraint | Description & Demo Sample Value |
| :---- | :---- | :---- | :---- |
| release\_package\_id | STRING | PRIMARY KEY | \`AWR-700-20261102-ZM151\` (Form 700 / AFTO Form 781\) |
| appraisal_report_uri | STRING | NOT NULL | `https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/unstructured/sar/SAR-20261102-ZM151.pdf` |
| mandated\_jtd\_task\_card | STRING | NOT NULL | \`JTD Task Card 53-11-00-280\` (Fastener Torque-Recheck) |
| disposition\_status | STRING | NOT NULL | \`SERVICEABLE\_WITH\_TORQUE\_RECHECK\` (0.012 in \< 0.015 in limit) |
| hitl\_reviewer\_role | STRING | HITL GATE | \`Chief Technical Officer (CTO) / Lead Stress Engineer\` (Human-in-the-Loop Reviewer) |
| hitl\_review\_status | STRING | WORKFLOW STATE | \`PENDING\_HITL\_REVIEW\` \-\> \`CONFIRMED\_BY\_ENGINEER\` upon human review |
| compliance\_standard | STRING | NOT NULL | \`MIL-HDBK-516C / DEF STAN 00-970 / MIL-STD-3001\` |

# 6\. Authoritative Document Manifest Required for Demonstration

To ground Use Cases 2 and 3 in GE Search and Conversation and Agent Runtime without introducing real classified technical data into the demonstration sandbox, the following synthetic OFFICIAL-tier documents must be authored and indexed. Each document's title, ID, target use case, and exact content scope are specified below:

&nbsp;

| Doc ID & Format | Document Title | Use Case | Required Content Scope & Technical Details |
| :---- | :---- | :---- | :---- |
| DOC-01 (S1000D XML / PDF) | JTD Section 53-30-01: Canopy Mechanical Rigging & Locking Mechanism Inspection | UC2 (Search) | Step-by-step mechanical rigging tolerances for the F-35 cockpit canopy latch, roller path clearances, pivot pin lubrication specs, and troubleshooting trees when no BIT fault is present. |
| DOC-02 (JSONL / Text Corpus) | Joint Force Historical Maintenance Narrative Logs (2021–2026: RAF, RN, USAF, USMC) | UC2 (Search) & UC3 (Agent) | 5-year synthetic corpus of "corrected-by" technician narratives using multi-service terminology (spanner/wrench, catch/latch), including the sister squadron record of silicon sealant debris in the canopy roller path and historical RAM/bulkhead notes. |
| DOC-03 (Structured Text / PDF) | RAF Marham Post-Flight Pilot Debrief Logbook (Sorties 2026-11-02) | UC2 & UC3 | Contains two verbatim debrief entries: (1) Night sortie pilot report of the "sticky/stiff canopy manual release handle" with zero BIT faults, and (2) Tail ZM151 pilot report of "severe airframe shudder at 14:22Z during Mach 1.3 defensive split-S". |
| DOC-04 (S1000D XML / PDF) | JTD Rule 53-11-00 & Task Card 53-11-00-280: Wing Carry-Through Bulkhead (Frame 496\) Exceedance & Torque-Recheck | UC3 (Agentic) | Mandates Class-A Ultrasonic NDI whenever Frame 496 exceeds 100% design yield strength, and specifies the calibrated torque-recheck procedure (\`N·m\` values) for Ti-6Al-4V fasteners under Task Card 53-11-00-280. |
| DOC-05 (Technical Manual PDF) | F-35 Structural Repair Manual (SRM) Chapter 51-40: Titanium Ti-6Al-4V Fastener Hole Elongation Limits & CAD Coordinates | UC3 (Agentic) | Defines the 3D spatial coordinate reference system \$(X, Y, Z)\$ for Frame 496 fastener holes (\#1 to \#32) and establishes the \`0.015\`-inch maximum allowable shear elongation limit before structural splicing is required. |
| DOC-06 (DICOM-TIFF / PNG) | Annotated Phased-Array Ultrasonic C-Scan & Eddy-Current Plot — Tail ZM151 Frame 496 Hole \#14 | UC3 (Multimodal) | Synthetic high-resolution ultrasonic C-scan image featuring technician bounding-box markup and acoustic impedance reflection callout indicating a \`0.012\`-inch shear elongation at Fastener Hole \#14. |
| DOC-07 (Regulatory PDF) | Military Airworthiness Certification Directives: MIL-HDBK-516C & UK DEF STAN 00-970 Compliance Guide | UC3 (Governance) | Establishes the legal airworthiness mandate prohibiting non-deterministic black-box AI from calculating primary structural fatigue, requiring deterministic Palmgren-Miner math and mandatory Human-in-the-Loop engineering verification. |
| DOC-08 (Template PDF / Markdown) | MIL-STD-3001 Structural Appraisal Report & Digital Aircraft Form 700 / AFTO Form 781 Release Template | UC3 (Output) | Standardized airworthiness release form template populated by the ADK 2.0 orchestrator, containing placeholders for telemetry tables, C-scan thumbnails, mBOM Lot \#8841-B audit results, and the Human-in-the-Loop engineering review checklist. |
| DOC-09 (Technical Manual PDF) | Material Application Manual (MAM) Section 9-1: High-Temperature Low-Observable (LO) RAM Compounds | Reference / Extension | Details thermal degradation thresholds (\`220°C\` exhaust zone limits) comparing Standard Liquid RAM Compound 'A' vs. High-Temp RAM Sheet 'B' and 4-hour heater blanket curing rules. |

# 7\. Autonomy Boundaries, Human-in-the-Loop & Demonstration Execution Script

## 7.1 Autonomy Boundaries & Non-Functional Requirements (NFRs)

Aligned with the governance framework in our UK Defence reference architectures (G[emini Enterprise demo design)](https://drive.google.com/open?id=1DFsGYT_KfFUchfgZNI5Uv8wJtSUdFhcxaQ_KlkJagbw), the demonstration enforces strict autonomy boundaries between AI synthesis and safety-critical execution:

* Automated by Gemini Enterprise: Natural language SQL generation and Vega-Lite chart rendering (UC1); semantic vector retrieval, cross-service jargon translation, and citation anchoring (UC2); multimodal NDI coordinate extraction, mBOM lot cross-referencing, and draft Form 700 / Structural Appraisal Report compilation (UC3).  
* Strictly Deterministic (Non-AI Code): Flight-hour counter increments, Rainflow cycle counting, Palmgren-Miner cumulative fatigue damage math (\$D \= \\sum n\_i / N\_i\$), and 3D CAD coordinate geometry transforms.  
* Human-Gated (Mandatory Human-in-the-Loop): Physical aircraft grounding/ungrounding and airworthiness release confirmation. The agent stages Tail \`ZM151\` in \`PENDING\_HITL\_REVIEW\` status so an authorized human engineer remains in the loop to verify the compiled evidence before maintenance release.  
* Performance & Cost SLAs: UC1 conversational analytics and chart rendering p95 latency ≤ 2.5 seconds; UC2 grounded search response ≤ 2.0 seconds with 100% verbatim citation fidelity; UC3 multi-agent orchestration completion ≤ 8.0 seconds in demo mode (compressing a 72-hour manual process). Prompt caching across static JTD manuals targets a \>90% cache hit rate.

## 7.2 End-to-End Demonstration Storyboard (12-Minute Live Walkthrough)

&nbsp;

| Demo Act & Time | Active Use Case & Persona | User Prompt / Action in Gemini Enterprise | Agent Platform Execution (GE Search, Agent Runtime & Registry) | On-Screen Deliverable & Value Proof |
| :---- | :---- | :---- | :---- | :---- |
| Act 1A (0:00 – 2:00) | UC1: Conversational Analytics (Turn 1) | Asks for RAF Marham actuator fatigue status post-sortie and 30-day regional depot stock coverage; requests tail-swap recommendation. | Gemini Enterprise invokes `f35_analytics_agent` on Agent Runtime to execute partition-pruned BigQuery EU query and cache metrics in session state. | Displays operational Markdown table showing Tail `ZM151` breach (`1,000.4` hrs), recommends auto-swap to `ZM154` (`842` hrs), and prompts user for chart selection (< 2.5s). |
| Act 1B (2:00 – 3:30) | UC1: On-Demand Presentation Graphics & Canvas (Turn 2) | User responds: "Render the full 16:9 Executive Briefing Dashboard for my presentation slide deck." | `f35_analytics_agent` executes `render_sustainment_chart` (backed by `chart_painter.py`), rendering Full HD 16:9 slide PNG on the fly and streaming to GCS in ~500–789 ms. | Renders publication-quality 16:9 slide graphic (1920×1080 at 160 DPI) with authenticated GCS download link (`[📥 Download 16:9 Executive Slide Graphic (PNG)](https://storage.cloud.google.com/...)`) for Keynote/PowerPoint insertion, alongside interactive Vega-Lite v5 Canvas. |
| Act 2 (3:30 – 7:00) | UC2: Enterprise Search (Flight-Line Avionics/Mech Tech) | Pastes pilot's free-text debrief: "Canopy manual release handle felt stiff... no BIT faults." Asks for likely root cause and JTD task steps. | GE Search and Conversation (\`ukd-f35-jtd-ietm-ds\`) performs dense vector retrieval \+ cross-service USMC/RAF log synthesis (\`DOC-01\`, \`DOC-02\`, \`DOC-03\`). | Displays grounded diagnostic card citing \*\*JTD Section 53-30-01\*\* and sister squadron silicon sealant debris fix in roller path; 0 hallucinations. |
| Act 3 (7:00 – 10:30) | UC3: Agentic AI Orchestrator (Lead Structural Engineer) | Uploads Frame 496 ultrasonic C-scan (\`DOC-06\`) for Tail \`ZM151\` following Mach 1.3 high-G exceedance and triggers \`@F35-Airworthiness-Agent\`. | \`f35\_airworthiness\_orchestrator\` (discovered via Agent Registry and running on Agent Runtime) syncs 1553 bus logs (\`14:22:18.420Z\`), calls the Miner's Rule API (\`104.2%\` yield), maps the C-scan (\`0.012"\` \< \`0.015"\`), and audits \`Lot \#8841-B\`. | Generates complete \*\*Structural Appraisal Report\*\*, flags \*\*14 global aircraft\*\* with \`Lot \#8841-B\`, attaches \*\*JTD Task 53-11-00-280\*\*, and stages \*\*Form 700\*\*. |
| Act 4 (10:30 – 12:00) | Human-in-the-Loop Verification & Live Telemetry (Lead Engineer) | Lead Stress Engineer reviews the compiled Structural Appraisal Report, C-scan overlay, and Form 700 draft in the HITL Review Studio. | Updates \`hitl\_review\_status\` in \`airworthiness\_release\_ledger\` and displays live BigQuery and Cloud Trace latency metrics. | Demonstrates 100% deterministic math and Human-in-the-Loop oversight under \*\*MIL-HDBK-516C / DEF STAN 00-970\*\*, compressing 72 hours into minutes. |

# 8\. Verification & Validation: Search Quality and Low-Latency Query Test Suite

To validate that the Gemini Enterprise F-35 Sustainment solution satisfies both operational accuracy and flight-line speed requirements, this section defines the formal Verification & Validation (V\&V) test suite. Testing is bifurcated into two rigorous tracks: (1) Search Result Quality & Grounding Fidelity (evaluating dense vector recall, cross-service dialect resolution, and zero-hallucination citation anchoring), and (2) Low-Latency Query Performance (evaluating partition-pruned Text-to-SQL execution, prompt cache hit rates, and parallel ADK 2.0 tool fan-out).

## 8.1 Search Result Quality & Grounding Evaluation Test Cases (UC2 & UC3)

Search quality across the GE Search and Conversation data stores (\`ukd-f35-jtd-ietm-ds\` and \`ukd-f35-narrative-logs-ds\`) is evaluated using a 150-query Golden Evaluation Dataset graded via Information Retrieval (IR) metrics (Recall@3, Mean Reciprocal Rank \[MRR@5\], Normalized Discounted Cumulative Gain \[NDCG@5\]) and GenAI Evaluation Service triad metrics (Groundedness, Context Relevance, and Answer Relevance):

&nbsp;

| Test ID & Name | Input Query / Test Stimulus | Expected Grounded Retrieval & Behavior | Target Quality Metric & Pass Threshold |
| :---- | :---- | :---- | :---- |
| TC-SQ-01: Semantic Intent vs. Keyword Miss (UC2) | Pilot debrief: "Cockpit entry handle felt sticky and required two-handed force to lock; zero BIT faults logged." (Contains zero exact title words from JTD 53-30-01). | Bypasses electrical BIT fault trees (\`bit\_fault\_associated \= false\` boost) and ranks \`DOC-01\` (JTD Section 53-30-01: Canopy Mechanical Rigging Inspection) as \#1 chunk. | Recall@3 \= 100% \| MRR@5 ≥ 0.90 \| Lexical BM25 baseline fails (0 hits), proving dense vector semantic lift. |
| TC-SQ-02: Cross-Service Dialect & Jargon Normalization (UC2) | UK RAF technician queries: "Canopy catch mechanism binding—check spanner torque and silicon fouling." against USMC/USAF historical logs (\`DOC-02\`). | Bridges UK/US terminology ("catch" \<-\> "latch", "spanner" \<-\> "wrench", "binding" \<-\> "stiff") to retrieve the USMC sister squadron silicon sealant debris roller-path fix. | NDCG@5 ≥ 0.92 \| Cross-Service Synonym Recall ≥ 95% across RAF, RN, USAF, and USMC logs. |
| TC-SQ-03: Zero-Hallucination & Verbatim Citation Fidelity (UC2 & UC3) | "What is the maximum allowable fastener hole elongation on Frame 496 and the required torque-recheck value under Task Card 53-11-00-280?" | Extracts exact \`0.015\`-inch tolerance (\`DOC-05\`) and calibrated \`N·m\` torque value (\`DOC-04\`) with character-exact \`\[Title\](URI)\` chunk citations; zero extrapolated figures. | Vertex AI Groundedness \= 1.00 (100% factual attribution) \| 0% ungrounded numerical claims. |
| TC-SQ-04: Multimodal NDI Annotation & Spatial Join Precision (UC3) | Upload annotated ultrasonic C-scan image (\`DOC-06\`) of Frame 496 together with SRM Chapter 51-40 (\`DOC-05\`) coordinate lookup table. | Extracts technician bounding-box coordinates \$(X, Y, Z)\$ and \`0.012\`-inch shear elongation reading, mapping deterministically to Fastener Hole \#14 without misidentifying adjacent holes. | 100% Entity Extraction Accuracy (\`Hole \#14\`, \`0.012 in\`, \`Lot \#8841-B\`) \| 0 false-positive teardown triggers. |
| TC-SQ-05: Multi-Document Thermal & Material Cross-Reference (UC2 & UC3) | Query: "Can Standard Liquid RAM Compound 'A' be applied to a 0.045-inch gouge in Wing Zone 4B given a 220°C peak EGT thermal profile?" | Retrieves \`DOC-09\` (MAM Section 9-1), identifies that Compound 'A' degrades at \`220°C\`, and recommends High-Temp RAM Sheet 'B' with a 4-hour heater blanket cure. | Recall@3 \= 100% \| Context Relevance ≥ 0.95 \| 100% accuracy on thermal limit and 4-hr cure rule. |

## 8.2 Low-Latency Query Performance & Scalability Test Cases (UC1, UC2 & UC3)

To ensure responsive interactive performance during live executive demonstrations and high-tempo squadron operations, the following latency and throughput tests benchmark the end-to-end execution pipeline across GE Search and Conversation, Agent Registry lookup, Agent Runtime execution (without Agent Gateway overhead), BigQuery BI Engine / partition pruning, and context caching:

&nbsp;

| Test ID & Name | Workload & Architectural Mechanism Tested | Instrumentation & Execution Path | Target Latency SLA (p50 / p95) & Cost Benchmark |
| :---- | :---- | :---- | :---- |
| TC-LP-01: Sub-Second Intent Classification & Sub-Agent Routing (All UCs) | High-speed classification of incoming user prompt across UC1 (Analytics), UC2 (Search), or UC3 (Agentic) via \`gemini-2.5-flash\` and direct Agent Registry lookup (no Agent Gateway hop). | Measures Time-to-First-Byte (TTFB) from Gemini Enterprise UI input to sub-agent invocation on Agent Runtime. | p50 ≤ 280 ms \| p95 ≤ 450 ms \| Routing accuracy ≥ 99.0% across 500 synthetic test prompts. |
| TC-LP-02: Low-Latency Partition-Pruned Text-to-SQL & On-Demand Charting (UC1) | Natural-language query joining `airframe_component_telemetry`, `global_depot_inventory`, and `squadron_sortie_schedule` (10M+ simulated rows) followed by Turn 2 on-demand chart rendering via `render_sustainment_chart`. | Enforces BigQuery partition pruning on `scheduled_departure_utc` and clustering on `tail_number` (`ZM151`, `ZM154`) and `nsn` (`1680-01-619-4821`). Turn 2 executes dedicated Python chart tool (`chart_painter.py`) directly from session state. | **Turn 1 (SQL + Tabular Briefing):** SQL Execution p95 ≤ 350 ms \| End-to-End Briefing p95 ≤ 2,500 ms (< 2.5s SLA).<br/>**Turn 2 (`render_sustainment_chart`):** In-Memory Vega-Lite p95 ≤ 5 ms (1.8 ms baseline) \| On-the-Fly 16:9 Matplotlib Render + GCS Upload p95 ≤ 790 ms (< 1,500 ms SLA). |
| TC-LP-03: Context-Cached Grounded RAG & Streaming Synthesis (UC2) | Repeated flight-line technician queries against static JTD Section 53-30-01 (\`DOC-01\`) and MAM Section 9-1 (\`DOC-09\`) manuals using Vertex AI Context Caching. | Pre-caches core S1000D system instructions and high-frequency JTD reference headers; measures vector retrieval \+ streaming token generation. | Vector Retrieval p95 ≤ 180 ms \| End-to-End Grounded Answer p95 ≤ 1,800 ms \| Prompt Cache Hit Rate ≥ 90% (\< £0.003/query). |
| TC-LP-04: Parallel ADK 2.0 Multi-Tool Fan-Out Execution (UC3) | Simultaneous execution of 1553 bus timestamp sync (\`14:22:18.420Z\`), Cloud Run Miner's Rule solver (\`104.2%\`), C-scan vision extraction (\`0.012"\`), and mBOM \`Lot \#8841-B\` audit. | ADK 2.0 \`ParallelAgent\` on Agent Runtime dispatches independent I/O and compute tools concurrently (direct invocation without Agent Gateway) before synthesizing the Form 700 / Structural Appraisal Report. | Parallel Tool Fan-Out p95 ≤ 3,100 ms (48% latency reduction vs. sequential) \| Full UC3 Package p95 ≤ 7,500 ms (\< 8.0s SLA). |
| TC-LP-05: Concurrent Squadron Surge & Degraded Link Resilience (All UCs) | 50 concurrent flight-line users issuing mixed UC1/UC2/UC3 queries over a simulated throttled tactical link (256 kbps edge backhaul). | Locust load-testing harness against Agent Runtime auto-scaling endpoints with compact JSON/Vega-Lite payload compression (\< 120 KB per response). | Zero HTTP 429/5xx timeouts \| p95 latency degradation ≤ 15% under 50x concurrent load \| Payload size ≤ 120 KB. |

## 8.3 Automated Continuous Evaluation & Telemetry Pipeline

* Pre-Demo Readiness Gate (CI/CD): Every update to prompt templates, BigQuery schemas, or chunking parameters automatically triggers the 10-test V\&V suite (\`TC-SQ-01\` through \`TC-LP-05\`) via Cloud Build and the Vertex AI Evaluation SDK. Builds failing any Recall@3 (\< 100% on critical JTD tasks), Groundedness (\< 1.00), or p95 latency threshold are blocked from promotion to the live demonstration tenant.  
* Live Operations View Telemetry: During Act 4 of the demonstration, the presenter surfaces real-time Cloud Trace and BigQuery \`INFORMATION\_SCHEMA.JOBS\` metrics—proving sub-400ms SQL execution, \>90% prompt cache efficiency, and 100% deterministic physics isolation to senior Defence stakeholders.

&nbsp;