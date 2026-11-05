# F-35 Fleet Sustainment Agent Platform — One-Page POC Architecture

> [!IMPORTANT]
> **Target GCP Project:** `antig-dave` (`284046449012`) · **Framework:** Google ADK 2.0 (`google-adk >= 2.0.0`) · **Model Tier:** `gemini-3.8-flash` (`enterprise=True`, `thinking_level="LOW"`, `temperature=0.0`) · **Sovereign Data Residency:** **`europe-west1` (Belgium)** & **`EU` / `eu` Multi-Region** · **Storyboard Alignment:** Mapped 1-to-1 with **Acts 1, 2, & 3 (Prompts 1–6)** of [DEMO_STORYBOARD.md](./DEMO_STORYBOARD.md).

---

## 1. Executive 16:9 Presentation Slide (White Background · Google Cloud Palette)

![F-35 Fleet Sustainment POC Architecture (White Background · Google Cloud Palette)](./docs/assets/f35_poc_architecture_16x9_white_gcloud.png)

* **Cloud Storage URI:** `gs://f35sa/f35_poc_architecture_16x9_white_gcloud.png`
* **Direct Cloud Storage Link:** [📥 Download 16:9 POC Architecture Slide (PNG)](https://storage.cloud.google.com/f35sa/f35_poc_architecture_16x9_white_gcloud.png)

---

## 2. End-to-End Agentic & Google Cloud Deployment Topology

```mermaid
flowchart TB
    %% -------------------------------------------------------------------------
    %% TIER 1: USER & CONVERSATION EXPERIENCE LAYER
    %% -------------------------------------------------------------------------
    subgraph T1["1. OPERATIONAL USER & EXPERIENCE LAYER — GEMINI ENTERPRISE (eu Multi-Region)"]
        direction LR
        USERS["<b>UK Lightning Force Personas</b><br/>• Act 1: Sqn Maint Officer &amp; Wing Controller<br/>• Act 2: Sqn Logistics Officer &amp; Commander<br/>• Act 3: Flight-Line Maintenance Chief"]
        GE_UI["<b>Gemini Enterprise Web UI (eu)</b><br/>• App: Agents (F35 Support) via ADK Native<br/>• Streaming Endpoint: :streamQuery (SSE)<br/>• Agent Registry (europe-west1)"]
        OUTPUTS["<b>Storyboard Output Modalities</b><br/>• Act 1: Screen-Fitted Spreadsheet Cards + CSV<br/>• Act 2: Full HD 16:9 Executive Briefing Slide<br/>• Act 3: 100% Verbatim Source-Cited Checklist"]
        USERS --> GE_UI --> OUTPUTS
    end

    %% -------------------------------------------------------------------------
    %% TIER 2: AGENTIC ORCHESTRATION LAYER (VERTEX AI AGENT RUNTIME)
    %% -------------------------------------------------------------------------
    subgraph T2["2. AGENTIC ORCHESTRATION LAYER — VERTEX AI AGENT RUNTIME (europe-west1 Belgium) · ADK 2.0"]
        direction TB
        ROOT["<b>Root Coordinator: f35_sustainment_coordinator</b><br/>Model: gemini-3.8-flash (enterprise=True, location='global', thinking_level='LOW', temp=0.0)<br/>• Sub-450ms Intent Router across Storyboard Acts 1, 2 &amp; 3 | App(name='app', resumability=True, context_cache=True)<br/>• <b>before_model_callback:</b> Tier 1 &amp; Tier 2 Fast-Path Interception (&lt; 5 ms Greetings, Health &amp; Capability Pitch)"]

        subgraph SUBS["Domain-Specialized ADK 2.0 Sub-Agents (Mapped to Storyboard Acts 1, 2 & 3)"]
            direction LR
            ACT1["<b>Act 1 Specialist (Prompts 1, 2 &amp; 3)</b><br/><b>f35_maintenance_data_agent</b><br/><i>@F35-Maintenance-Data (&lt; 1.5s SLA)</i><br/>• Prompt 1: Urgent CSG Jobs (Spots ZM151)<br/>• Prompt 2: ZM151 Post-Sortie Faults &amp; CND<br/>• Prompt 3: Shift Crew, QAR &amp; Calibrated Tools<br/>• 3-Layer Semantic SQL Canonicalizer<br/>• <b>Tool:</b> execute_maintenance_sql"]
            ACT2["<b>Act 2 Specialist (Prompts 4 &amp; 5)</b><br/><b>f35_analytics_agent</b><br/><i>@F35-Sustainment-Analytics (&lt; 2.5s / &lt; 0.8s)</i><br/>• Prompt 4: ZM151 Actuator (1,000.4h) vs 30d Spares<br/>• Prompt 4: Swaps 07:30Z Sortie to ZM154 (842.0h)<br/>• Prompt 5: Renders 16:9 Executive Briefing Slide<br/>• <b>Tools:</b> check_actuator_fatigue...,<br/>  recommend_tail_swap..., render_sustainment_chart"]
            ACT3["<b>Act 3 Specialist (Prompt 6)</b><br/><b>f35_jtd_search_agent</b><br/><i>@F35-JTD-Search (0.38s Grounded Search)</i><br/>• Prompt 6: Solves ZM151 Zero-Code Canopy Fault<br/>• Matches USMC VMFA-211 Silicon Debris Log<br/>• Cites JTD 53-30-01 (18.5 N·m Torque Spec)<br/>• UK/US Dialect Bridge (catch/latch, spanner)<br/>• <b>Tool:</b> search_technical_manuals_and_repair_logs"]
        end

        ROOT -->|"Act 1 (Prompts 1–3)"| ACT1
        ROOT -->|"Act 2 (Prompts 4–5)"| ACT2
        ROOT -->|"Act 3 (Prompt 6)"| ACT3
    end

    %% -------------------------------------------------------------------------
    %% TIER 3: SOVEREIGN EU DATA, SEARCH & STORAGE LAYER
    %% -------------------------------------------------------------------------
    subgraph T3["3. SOVEREIGN EU DATA, SEARCH & STORAGE LAYER — MAPPED TO STORYBOARD ACTS 1, 2 & 3"]
        direction LR
        subgraph BQ["F35 Data Warehouse — BigQuery (Location: EU)<br/>Dataset: antig-dave.ukd_f35_sustainment_demo (6 Tables × 100 Rows = 600 Rows)"]
            direction TB
            BQ_ACT1["<b>Act 1 Maintenance &amp; Shift Tables (Prompts 1–3)</b><br/>• <b>Prompt 1 (Urgent Stand-Up):</b> maintenance_work_orders (100)<br/>• <b>Prompt 2 (Post-Sortie Triage):</b> phm_bit_fault_events (100)<br/>• <b>Prompt 3 (Crews &amp; Tool Cal):</b> work_center_tooling_and_sqep (100)"]
            BQ_ACT2["<b>Act 2 Readiness, Spares &amp; Sortie Tables (Prompt 4)</b><br/>• <b>Actuator Hours (ZM151/ZM154):</b> airframe_component_telemetry (100)<br/>• <b>30-Day Depot Spares Stock:</b> global_depot_inventory (100)<br/>• <b>07:30Z Sortie Tail Swap:</b> squadron_sortie_schedule (100)"]
        end

        GCS["<b>Cloud Storage (europe-west1)</b><br/><i>gs://antig-dave-f35-staging-europe-west1</i><br/>• <b>Act 1 (Prompts 1–3):</b> /exports/*.csv Sheets<br/>• <b>Act 2 (Prompt 5):</b> /charts/*.png 16:9 Slide<br/>• <b>Act 3 (Prompt 6):</b> /unstructured/docs/*.pdf"]

        DE["<b>Act 3 Technical Pubs &amp; Logs — Discovery Engine (eu)</b><br/><i>Single-Pass REST Search (pageSize=15, 100% Cited)</i><br/>• <b>ukd-f35-narrative-logs-ds (Prompt 6 Fleet Memory):</b><br/>  DOC-02 (USMC VMFA-211 Silicon Debris), DOC-03 (RAF 617 Log)<br/>• <b>ukd-f35-jtd-ietm-ds (Prompt 6 Approved Procedure):</b><br/>  DOC-01 (JTD 53-30-01 18.5 N·m Torque), DOC-09 (MAM 9-1)"]
    end

    %% -------------------------------------------------------------------------
    %% TIER 4: CLOUD PLATFORM GUARDRAILS, IAM & OBSERVABILITY
    %% -------------------------------------------------------------------------
    subgraph T4["4. GOOGLE CLOUD PLATFORM SECURITY, LATENCY & CI/CD GUARDRAILS (europe-west1)"]
        direction LR
        IAM["<b>IAM &amp; Read-Only Guardrails</b><br/>• Runtime SA: f35-sustainment-runtime-sa<br/>• In-Memory ADC Auth Cache (PERF-01)<br/>• SQL AST Gate (SELECT-only allowlist)"]
        PERF["<b>Pre-Warmed Clients &amp; Caching</b><br/>• Module-level BigQuery &amp; HTTPX Singletons<br/>• ADK Context Cache (TTL 1800s, &gt;90% hit)<br/>• Zero Local/SQLite Fallback Drift"]
        CICD["<b>CI/CD &amp; Observability</b><br/>• Cloud Build &amp; Artifact Registry (europe-west1)<br/>• OpenTelemetry GenAI Spans → Cloud Trace<br/>• 365 Automated Unit/E2E/Eval Checks"]
    end

    GE_UI ==>|":streamQuery (SSE)"| ROOT
    ACT1 -->|"Prompts 1–3 Read-Only SQL"| BQ_ACT1
    ACT1 -->|"Auto CSV Upload"| GCS
    ACT2 -->|"Prompt 4 3-Table SQL"| BQ_ACT2
    ACT2 -->|"Prompt 5 16:9 PNG Upload"| GCS
    ACT3 -->|"Prompt 6 REST Search"| DE
    T2 -.->|"Enforced by"| T4

    %% Google Cloud Light/White Styling
    classDef gcBlue fill:#E8F0FE,stroke:#1A73E8,stroke-width:2px,color:#174EA6;
    classDef gcGreen fill:#E6F4EA,stroke:#1E8E3E,stroke-width:2px,color:#0D652D;
    classDef gcYellow fill:#FEF7E0,stroke:#F9AB00,stroke-width:2px,color:#B06000;
    classDef gcRed fill:#FCE8E6,stroke:#D93025,stroke-width:2px,color:#A50E0E;
    classDef gcWhite fill:#FFFFFF,stroke:#DADCE0,stroke-width:1.5px,color:#202124;

    class GE_UI,ROOT,GCS,IAM gcBlue;
    class OUTPUTS,ACT1,BQ_ACT1,PERF gcGreen;
    class ACT2,BQ_ACT2 gcYellow;
    class ACT3,DE,CICD gcRed;
    class USERS gcWhite;

    style T1 fill:#F8F9FA,stroke:#DADCE0,stroke-width:2px,color:#174EA6
    style T2 fill:#F8F9FA,stroke:#1A73E8,stroke-width:2px,color:#174EA6
    style SUBS fill:#FFFFFF,stroke:#DADCE0,stroke-width:1px,color:#202124
    style T3 fill:#F8F9FA,stroke:#DADCE0,stroke-width:2px,color:#174EA6
    style BQ fill:#FFFFFF,stroke:#1E8E3E,stroke-width:1.5px,color:#0D652D
    style T4 fill:#F8F9FA,stroke:#DADCE0,stroke-width:2px,color:#174EA6
```

---

## 3. Demo Storyboard (`Acts 1–3` / `Prompts 1–6`) to Data & Agent Layer Mapping

| Storyboard Act & Step ([DEMO_STORYBOARD.md](./DEMO_STORYBOARD.md)) | Operational Persona & Timeline | Specialist Sub-Agent & Tool | Authoritative Data Table / Datastore (`EU` / `eu`) | Operational Output & SLA |
| :--- | :--- | :--- | :--- | :--- |
| **Act 1 · Prompt 1**<br/>*Urgent Jobs & Grounded Aircraft* | Squadron Maintenance Officer (`06:45Z`) | `@F35-Maintenance-Data`<br/>(`execute_maintenance_sql`) | **BigQuery (`EU`) Table 1:**<br/>`maintenance_work_orders` (`100` rows) | Screen-fitted Spreadsheet Card (`A..E`) + `.csv` export; spots lead jet **`ZM151`** on `WO-2026-88401` & `WO-2026-88402` (`< 1.5s`). |
| **Act 1 · Prompt 2**<br/>*Post-Sortie Faults & Fleet Warnings* | Flight-Line Avionics Lead (`06:47Z`) | `@F35-Maintenance-Data`<br/>(`execute_maintenance_sql`) | **BigQuery (`EU`) Table 2:**<br/>`phm_bit_fault_events` (`100` rows) | Spreadsheet Card (`A..F`) isolating **`ZM151`**'s `1,000.4-hr` actuator breach (`PHM-2026-99101`) & zero-code repeat CND canopy report (`PHM-2026-99102`) (`< 1.5s`). |
| **Act 1 · Prompt 3**<br/>*Shift Crews, Inspector & Tooling* | Wing Maintenance Controller (`06:50Z`) | `@F35-Maintenance-Data`<br/>(`execute_maintenance_sql` 2-Table `JOIN`) | **BigQuery (`EU`) Table 3 + Table 1:**<br/>`work_center_tooling_and_sqep` (`100` rows) `JOIN` `maintenance_work_orders` | Cross-checked Readiness Card confirming **`ZM151`** bay crew, QAR inspector & calibrated spanner **`JTD-53-30-T14`** are `🟢 READY_TO_DISPATCH` (`< 1.6s`). |
| **Act 2 · Prompt 4**<br/>*Spares Check & Sortie Tail Swap* | Squadron Logistics Officer (`06:52Z`) | `@F35-Sustainment-Analytics`<br/>(`check_actuator_fatigue_and_depot_inventory` & `recommend_tail_swap_and_replenishment`) | **BigQuery (`EU`) Tables 4, 5 & 6:**<br/>`airframe_component_telemetry` (`100`),<br/>`global_depot_inventory` (`100`),<br/>`squadron_sortie_schedule` (`100`) | Verifies `4` spare actuators in stock (`18-hr` ETA) and swaps `07:30Z` Sortie `SRT-MAR-20261103-01` from **`ZM151`** (`1,000.4h`) to clean spare **`ZM154`** (`842.0h`) (`1.2s`). |
| **Act 2 · Prompt 5**<br/>*Executive Briefing Slide Deck* | Squadron Logistics Officer (`06:54Z`) | `@F35-Sustainment-Analytics`<br/>(`render_sustainment_chart` via [chart_painter.py](./app/tools/chart_painter.py)) | **Cloud Storage (`europe-west1`):**<br/>`gs://antig-dave-f35-staging-europe-west1/charts/` | Synthesizes Full HD 16:9 widescreen PNG slide (`ZM151` Red vs `ZM154` Green + Regional Depot Stock) with clickable download link (`< 0.8s`). |
| **Act 3 · Prompt 6**<br/>*Allied Fleet Memory & Defect Fix* | Flight-Line Maintenance Chief (`06:56Z`) | `@F35-JTD-Search`<br/>(`search_technical_manuals_and_repair_logs`) | **Discovery Engine (`eu`) Datastores:**<br/>`ukd-f35-narrative-logs-ds` (`DOC-02`, `DOC-03`) &<br/>`ukd-f35-jtd-ietm-ds` (`DOC-01`, `DOC-09`) | Matches **USMC `VMFA-211`** cured silicon sealant debris log (`DOC-02`) and cites **JTD Section `53-30-01`** (`DOC-01`) `18.5 N·m` torque spec for spanner `JTD-53-30-T14` (`0.38s`). |
