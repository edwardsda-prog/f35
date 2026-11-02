# Solution Design Document: F-35 Fleet Sustainment — Gemini Enterprise Demonstrations

## Dual-Phase Specification: Demonstration Sandbox & Accredited Production Target ( Conversational Analytics, Enterprise Search, and Agentic AI )

Document ID: SDD-GE-F35-001 \| Author: David Edwards (Customer Engineer, UK Public Sector) \| Date: 2026-11-02 \| Version: 1.2 \| Status: Demonstration & Target Architecture Specification

Executive Summary: This Solution Design Document (SDD) defines the target architecture, database schemas, and authoritative document corpus required to demonstrate Gemini Enterprise and the Agent Platform across fifth-generation F-35 Lightning II sustainment workflows. Following a dual-track delivery model, the design aligns the Google Cloud Demonstration Sandbox and the Production Target around the unified Agent Platform—comprising Gemini Enterprise (GE) Search and Conversation, Agent Runtime, and Agent Registry (explicitly excluding Agent Gateway for the demonstration). While safety-critical structural math (MIL-HDBK-516C / DEF STAN 00-970) remains strictly deterministic with Human-in-the-Loop (HITL) engineering oversight, Gemini Enterprise compresses time-to-insight and time-to-action from days to minutes across three progressive use cases.

# 1\. Document Control & Programme Scope

&nbsp;

| Metadata Field | Specification Value |
| :---- | :---- |
| Document ID & Title | SDD-GE-F35-001 — F-35 Fleet Sustainment: Gemini Enterprise Demonstrations |
| Author & Role | David Edwards — Customer Engineer, Google Cloud UK/IE Public Sector & Defense |
| Target Platform | Gemini Enterprise & Agent Platform (GE Search & Conversation, Agent Runtime, Agent Registry) |
| Operational Domain | Fifth-Generation Fighter Sustainment (RAF Marham / Joint F-35 Force ODIN & ALIS) |
| Demonstration Scope | UC1: Conversational Analytics & Charting \| UC2: Enterprise Search \| UC3: Agentic AI Orchestration |
| Reference Baseline | Aligned with SDD-GE-UKD-002 (Gemini Enterprise demo design) and Enterprise Agent SDD v2.0 |

## 1.1 Strategic Context & Dual-Track Delivery Approach

Fifth-generation aircraft sustainment generates petabytes of structured sensor telemetry alongside millions of pages of unstructured technical publications and human maintenance narratives. Traditional sustainment portals suffer from data siloization—separating relational logistics databases from Joint Technical Data (JTD) manuals and Non-Destructive Inspection (NDI) imagery. Building on the dual-track methodology established in internal UK Defence reference architectures (Gemini Enterprise [demo design) and the Enterpr](https://drive.google.com/open?id=1U25WbkVxLApE4JncbTeaDNOG1RIrAg5RW3YvuCqMjdg)ise Agent Solution Design template (Solution D[esign Document Template.md), this so](https://drive.google.com/file/d/1GRItHQcn_Z9fzSOcvLc-LNs-M76bIRc4/view?usp=drivesdk&resourcekey=0-TqzO2csxHtpXn7SmZF2W7g)lution establishes two parallel execution environments:

* Demonstration Track (Immediate Pilot Sandbox): A cloud-hosted demonstration environment running on Google Cloud Platform (GCP). It showcases Gemini Enterprise and the Agent Platform—specifically GE Search and Conversation, Agent Runtime (hosting ADK 2.0 agents), and Agent Registry—backed by BigQuery (\`ukd\_f35\_sustainment\_demo\`), interactive Vega-Lite chart rendering, and Human-in-the-Loop (HITL) review interfaces. For the purpose of the demonstration, Agent Gateway is omitted in favor of direct integration between Gemini Enterprise, Agent Registry, and Agent Runtime.  
* Production Track (Accredited Sovereign Target): The target-state military deployment hosting Gemini Enterprise and the full Agent Platform (GE Search and Conversation, Agent Runtime, and Agent Registry) on Google Distributed Cloud (GDC) Air-Gapped appliances, integrated with live Lockheed Martin / JPO ODIN relational nodes, MIL-STD-1553 / ARINC 429 flight-line ingestion pipelines, S1000D XML Interactive Electronic Technical Manuals (IETMs), and Human-in-the-Loop engineering review portals.

## 1.2 Summary of the Three Demonstration Use Cases

&nbsp;

| Use Case & Modality | Operational Scenario | Data Viewpoint | Trad. Time-to-Action | Gemini Time-to-Action |
| :---- | :---- | :---- | :---- | :---- |
| UC1: Conversational Analytics \+ Simple Charts | Automatic Part Replenishment & Fleet Readiness (Tail ZM151 Left Horizontal Tail Actuator S/N ACT-99812-F exceeding 1,000-hr limit at 1,000.4 hrs; NSN 1680-01-619-4821 stock \= 4). | Structured Data Only (BigQuery SQL Telemetry, Inventory & Sortie Schedules) | 2 to 4 Hours (Manual SQL, ERP lookups & shift replanning) | Near-Instantaneous (\< 5s query \+ auto-generated bar/line charts) |
| UC2: Enterprise Search (Grounded RAG) | Intermittent "Sticky" Cockpit Canopy Latch (Subjective pilot debrief with zero BIT faults; semantic correlation across JTD Section 53-30-01 & sister squadron silicon debris logs). | Unstructured Data Only (JTD/IETM Manuals, Pilot Debriefs & 5-Yr Maintainer Logs) | 4 to 8 Hours (Manual keyword search across XML/PDF manuals) | 10 to 15 Minutes (Direct semantic match \+ multi-service translation) |
| UC3: Agentic AI (Multi-Agent Orchestrator) | Dynamic Flight Envelope Exceedance & Airworthiness Recertification (Mach 1.3 asymmetrical pull-up on Frame 496; 104.2% yield load; 0.012-in hole elongation on Ti-6Al-4V Lot \#8841-B vs 0.015-in limit). | Converged Structured & Unstructured Data \+ Deterministic Physics (Miner's Rule) | 36 to 72 Hours (Manual data fusion, CAD mapping & Form 700 routing) | 1 to 2 Hours (Automated Structural Appraisal Report staged for Human-in-the-Loop review) |

# 2\. Target Architecture: Gemini Enterprise & Agent Platform Topology

The target architecture centers on Gemini Enterprise coupled with the unified Agent Platform, comprising GE Search and Conversation, Agent Runtime (powered by ADK 2.0), and Agent Registry, following the architectural blueprint in the Enterprise Agent Solution Design standard (Solution Design Document [Template.md) and tactical edge sust](https://drive.google.com/file/d/1GRItHQcn_Z9fzSOcvLc-LNs-M76bIRc4/view?usp=drivesdk&resourcekey=0-TqzO2csxHtpXn7SmZF2W7g)ainment designs (Presentation Stor[yboard \- Pixel Roots Demo 1). For the purpos](https://docs.google.com/document/d/1xPBs4G_LbHID6whn4zKzKkTMkG0FTOa-c0lpYcv3Ndg/edit?usp=drivesdk&ouid=115969398345850679057&resourcekey=0-hdKCRNyMVCMjbXzbBkhv1g)e of the demonstration, Agent Gateway is intentionally excluded—agents registered in Agent Registry are invoked directly by Gemini Enterprise on the Agent Runtime and connect directly to backend data stores and deterministic microservices via Google MCP Toolbox.

* Gemini Enterprise & GE Search and Conversation (\`gemini-2.5-flash\` Router): Serves as the unified front-of-house experience, conversational orchestration layer, and enterprise search bar. Evaluates user prompts and discovers published sustainment agents via Agent Registry to route structured analytical and charting requests to UC1, unstructured technical manual lookups to UC2, and multi-disciplinary airworthiness workflows to UC3.  
* UC1 Conversational Analytics & Charting Agent (\`f35\_analytics\_agent\` on Agent Runtime / \`gemini-3.1-pro\`): Registered in Agent Registry and executed on Agent Runtime. Translates natural language supply and readiness questions into partition-pruned BigQuery SQL via Google MCP Toolbox (bypassing Agent Gateway in the demo) and generates Vega-Lite / Chart.js JSON specifications to render interactive bar and line charts inline in Gemini Enterprise.  
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

# 3\. Use Case 1 Design: Conversational Analytics with Simple Charts (Structured Data)

## 3.1 Operational Narrative & Gemini Capabilities

When F-35A Tail \`ZM151\` lands at RAF Marham after a training sortie, its onboard computer uploads flight usage telemetry to ODIN. The Left Horizontal Tail Actuator (\`S/N: ACT-99812-F\`) reaches \`1,000.4\` flight hours, breaching its \`1,000.0\`-hour structural fatigue threshold. In the Gemini Enterprise demo, the Squadron Logistics Officer or Commander interacts with the \`@F35-Sustainment-Analytics\` agent using natural language rather than legacy ERP drop-downs.

* Text-to-SQL Generation: The user asks, "Which F-35A tails at RAF Marham are within 50 hours of their horizontal tail actuator life limit, and do we have sufficient regional depot stock to cover RAF Marham and deployed carrier groups for the next 30 days?" Gemini translates this into an optimized multi-table SQL join across telemetry, inventory, and flight schedules.  
* Automated Simple Chart Production: Alongside its text response, the agent emits a structured chart specification rendered inline in Gemini Enterprise: (1) a Grouped Bar Chart comparing Regional Depot Stock (\`4\` units of \`NSN: 1680-01-619-4821\`) against 30-Day Projected Squadron Demand across RAF Marham and HMS Queen Elizabeth, and (2) a Threshold Line Chart plotting actuator flight-hour accumulation for Tail \`ZM151\` (\`1,000.4\` hrs, red breach marker) and Spare Tail \`ZM154\` (\`842.0\` hrs, green serviceable marker) against the \`1,000\`-hour condemnation line.  
* Proactive Operational Briefing & Action: The agent automatically drafts a Supply Alert flagging \`ZM151\` as "Partial Mission Capable (Maintenance Required)", confirms an automated depot shipping order (ETA 18 hours), and recommends reallocating Pilot Henderson's morning sortie to Spare Tail \`ZM154\`.

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
| sortie\_readiness\_status | STRING | NOT NULL | \`AT\_RISK\_MAINTENANCE\` \-\> Auto-reallocated to \`ZM154\` |

# 4\. Use Case 2 Design: Enterprise Search & Grounded Reasoning (Unstructured Data)

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
| appraisal\_report\_uri | STRING | NOT NULL | \`gs://ukd-f35-demo-artifacts/SAR-ZM151-Frame496.pdf\` |
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
| Act 1 (0:00 – 3:30) | UC1: Conversational Analytics (Squadron Logistics Officer) | Asks for RAF Marham actuator fatigue status post-sortie and 30-day regional depot stock coverage; requests visual comparison chart. | Gemini Enterprise discovers \`f35\_analytics\_agent\` in Agent Registry and invokes it directly on Agent Runtime (no Agent Gateway) to query BigQuery and output Vega-Lite JSON. | Renders interactive Bar & Line Charts showing Tail \`ZM151\` at \`1,000.4\` hrs, \`4\` units of \`NSN 1680-01-619-4821\` in stock, and auto-swap of Pilot Henderson to \`ZM154\`. |
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
| TC-LP-02: Low-Latency Partition-Pruned Text-to-SQL & Charting (UC1) | Natural-language query joining \`airframe\_component\_telemetry\`, \`global\_depot\_inventory\`, and \`squadron\_sortie\_schedule\` (10M+ simulated rows) \+ Vega-Lite JSON output. | Enforces BigQuery partition pruning on \`scheduled\_departure\_utc\` and clustering on \`tail\_number\` (\`ZM151\`, \`ZM154\`) and \`nsn\` (\`1680-01-619-4821\`) with BI Engine in-memory acceleration. | SQL Execution p95 ≤ 350 ms \| End-to-End Text \+ Vega-Lite Chart Render p95 ≤ 2,200 ms (\< 2.5s SLA). |
| TC-LP-03: Context-Cached Grounded RAG & Streaming Synthesis (UC2) | Repeated flight-line technician queries against static JTD Section 53-30-01 (\`DOC-01\`) and MAM Section 9-1 (\`DOC-09\`) manuals using Vertex AI Context Caching. | Pre-caches core S1000D system instructions and high-frequency JTD reference headers; measures vector retrieval \+ streaming token generation. | Vector Retrieval p95 ≤ 180 ms \| End-to-End Grounded Answer p95 ≤ 1,800 ms \| Prompt Cache Hit Rate ≥ 90% (\< £0.003/query). |
| TC-LP-04: Parallel ADK 2.0 Multi-Tool Fan-Out Execution (UC3) | Simultaneous execution of 1553 bus timestamp sync (\`14:22:18.420Z\`), Cloud Run Miner's Rule solver (\`104.2%\`), C-scan vision extraction (\`0.012"\`), and mBOM \`Lot \#8841-B\` audit. | ADK 2.0 \`ParallelAgent\` on Agent Runtime dispatches independent I/O and compute tools concurrently (direct invocation without Agent Gateway) before synthesizing the Form 700 / Structural Appraisal Report. | Parallel Tool Fan-Out p95 ≤ 3,100 ms (48% latency reduction vs. sequential) \| Full UC3 Package p95 ≤ 7,500 ms (\< 8.0s SLA). |
| TC-LP-05: Concurrent Squadron Surge & Degraded Link Resilience (All UCs) | 50 concurrent flight-line users issuing mixed UC1/UC2/UC3 queries over a simulated throttled tactical link (256 kbps edge backhaul). | Locust load-testing harness against Agent Runtime auto-scaling endpoints with compact JSON/Vega-Lite payload compression (\< 120 KB per response). | Zero HTTP 429/5xx timeouts \| p95 latency degradation ≤ 15% under 50x concurrent load \| Payload size ≤ 120 KB. |

## 8.3 Automated Continuous Evaluation & Telemetry Pipeline

* Pre-Demo Readiness Gate (CI/CD): Every update to prompt templates, BigQuery schemas, or chunking parameters automatically triggers the 10-test V\&V suite (\`TC-SQ-01\` through \`TC-LP-05\`) via Cloud Build and the Vertex AI Evaluation SDK. Builds failing any Recall@3 (\< 100% on critical JTD tasks), Groundedness (\< 1.00), or p95 latency threshold are blocked from promotion to the live demonstration tenant.  
* Live Operations View Telemetry: During Act 4 of the demonstration, the presenter surfaces real-time Cloud Trace and BigQuery \`INFORMATION\_SCHEMA.JOBS\` metrics—proving sub-400ms SQL execution, \>90% prompt cache efficiency, and 100% deterministic physics isolation to senior Defence stakeholders.

&nbsp;