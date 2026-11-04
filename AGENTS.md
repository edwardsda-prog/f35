# AGENTS.md — F-35 Fleet Sustainment Agent Platform (`f35-sustainment-agent`)

> **Source Design Specification:** [SA_F35.md](./SA_F35.md) (`SDD-GE-F35-001`, v1.3)  
> **Target Platform:** Google Cloud Agent Platform (Gemini Enterprise Search & Conversation, Agent Runtime, Agent Registry — *Agent Gateway excluded for Demo Track*)  
> **Framework & Toolchain:** Python 3.11+ · Google ADK 2.0 (`google-adk >= 2.0.0`, `google-genai`) · `google-agents-cli` (`agents-cli`)  
> **Target GCP Project:** `antig-dave` (Project Number: `284046449012`)  
> **Mandatory GCP Region & Data Residency:** All GCP services MUST reside in **EU** (`eu` multi-region for Gemini Enterprise / Discovery Engine & `EU` for BigQuery) and all compute/runtime resources MUST be deployed to **`europe-west1` (Belgium)**.

---

# Multi-Agent Orchestration

## 1. The Three-Phase Workflow
Every major feature request or bug fix must follow this precise delegation structure:
- **Phase 1: Plan:** A single orchestrator agent must read the codebase, consult [`docs/issues/INDEX.md`](./docs/issues/INDEX.md) (to review past root causes, guardrail fixes, and rejected approaches), design the architecture, and present a complete plan for user approval. No subagent delegation is allowed during this phase.
- **Phase 2: Build:** Once the plan is approved, the orchestrator must spin up independent subagents to work in parallel on isolated layers.
- **Phase 3: Integration & Issue Logging:** The orchestrator agent must validate the combined code, run tests, record any resolved issues, regressions, or performance fixes in [`docs/issues/`](./docs/issues/) using [`docs/issues/TEMPLATE.md`](./docs/issues/TEMPLATE.md) (and register the `ISS-XXX` entry in [`docs/issues/INDEX.md`](./docs/issues/INDEX.md)), and merge the branches.

## 2. Agent Specialization Boundaries
Do not allow a single agent to handle multiple domains. Delegate according to directory-level `AGENTS.md` boundaries:
- **Backend Implementer:** Restricted to `/packages/api` (and `app/`, `scripts/` for ADK runtime/data layer). Focuses on database schema, endpoints, ADK domain sub-agents/tools, deterministic physics, and server-side testing.
  - Within the ADK 2.0 runtime (`app/sub_agents/` & `app/tools/`), domain specialization is strictly enforced across four dedicated ADK sub-agents:
    - **`f35_maintenance_data_agent` (UC0 Specialist)**: Restricted to `app/sub_agents/uc0_maintenance_agent.py` & `app/tools/uc0_maintenance.py` (Dynamic Text-to-SQL over `maintenance_work_orders`, Excel / Google Sheets Card rendering, and automatic GCS `.csv` export).
    - **`f35_analytics_agent` (UC1 Specialist)**: Restricted to `app/sub_agents/uc1_analytics_agent.py` & `app/tools/uc1_analytics.py` (BigQuery telemetry/inventory/sortie joins & Vega-Lite chart specs).
    - **`f35_jtd_search_agent` (UC2 Specialist)**: Restricted to `app/sub_agents/uc2_search_agent.py` & `app/tools/uc2_jtd_search.py` (Discovery Engine `eu` datastore retrieval, cross-service dialect normalization, and verbatim citation anchoring).
    - **`f35_airworthiness_orchestrator` (UC3 Specialist)**: Restricted to `app/sub_agents/uc3_airworthiness_agent.py`, `app/tools/uc3_airworthiness.py`, & `app/physics/asip_engine.py` (Parallel 4-way ASIP fan-out, deterministic Rainflow/Miner's Rule math, C-scan CAD join, mBOM lot audit, and Form 700 HITL workflow).
- **Frontend Implementer:** Restricted to `/packages/web`. Focuses on components, state management, and UI styling (e.g., `MaintenanceSheetCard.tsx`, Vega-Lite Canvas & HITL Review Studio components).
- **QA / Test Agent:** Restricted to `/tests` (`tests/unit/` and `tests/eval/`). Responsible exclusively for integration tests, deterministic unit verification, and end-to-end `agents-cli eval` testing hooks (`TC-SQ-00..05` and `TC-LP-00..05`).

## 3. Concurrency and Isolation
- Subagents must use isolated environments or Git worktrees (`Workspace="branch"` or `Workspace="share"`) to prevent overlapping file changes.
- Ensure strict separation of concerns; no two agents may edit the same file simultaneously.

---

## 4. Executive Architecture & Design Decisions

This `AGENTS.md` translates the **F-35 Lightning II Fleet Sustainment Solution Design ([SA_F35.md](./SA_F35.md))** into an executable engineering specification for coding agents and developers using **ADK 2.0** and **`agents-cli`**.

### Confirmed Architectural Decisions

1. **Unified Multi-Agent Project Deployed to `europe-west1` (Belgium) & `EU` Multi-Region**:
   - Packaged as a single `agents-cli` repository (`<= 26` characters: `f35-sustainment-agent`) exposing `app = App(name="app", root_agent=root_agent, resumability_config=ResumabilityConfig(is_resumable=True), context_cache_config=ContextCacheConfig(...))`.
   - **All GCP Services in EU / `europe-west1` (Belgium)**:
     - **Agent Runtime, Cloud Build, Artifact Registry, Agent Registry**: Deployed to **`europe-west1` (Belgium)** (`--region europe-west1`).
     - **BigQuery (`ukd_f35_sustainment_demo`) & Cloud Storage Buckets**: Provisioned in **`EU`** (`europe-west1` / `EU` multi-region).
     - **Gemini Enterprise & Discovery Engine (`ukd-f35-jtd-ietm-ds`, `ukd-f35-narrative-logs-ds`)**: Provisioned in **`eu`** (`locations/eu/collections/default_collection/...`).
   - Deployed as a managed Reasoning Engine on **Agent Runtime** in `europe-west1` (`--deployment-target agent_runtime --region europe-west1`) and published natively to **Gemini Enterprise (`eu`)** via `:streamQuery` (`agents-cli publish gemini --registration-type adk`).

2. **Multi-Agent Domain Specialization (`root_agent` + 4 Specialist Sub-Agents)**:
   - **`root_agent` (`f35_sustainment_coordinator`)**: Acts strictly as the front-of-house router and coordinator (`gemini-3.8-flash`, `thinking_level="LOW"`, with Tier 1/2 `before_model_callback` fast-path interception). It delegates domain execution to four specialized ADK 2.0 sub-agents (`sub_agents=[f35_maintenance_data_agent, f35_analytics_agent, f35_jtd_search_agent, f35_airworthiness_orchestrator]`):
     - **`f35_maintenance_data_agent` (`@F35-Maintenance-Data`)**: Handles UC0 conversational Text-to-SQL over Table 7 (`maintenance_work_orders`), Excel / Google Sheets Card rendering, and automatic GCS `.csv` export.
     - **`f35_analytics_agent` (`@F35-Sustainment-Analytics`)**: Handles UC1 structured BigQuery supply/readiness analytics, inline Vega-Lite charting, and sortie tail-swap recommendations.
     - **`f35_jtd_search_agent` (`@F35-JTD-Search`)**: Handles UC2 unstructured S1000D JTD manual lookup and 5-year cross-service maintenance narrative synthesis with verbatim citations.
     - **`f35_airworthiness_orchestrator` (`@F35-Airworthiness-Agent`)**: Handles UC3 dynamic flight envelope exceedance, executing a parallel fan-out across 1553 bus sync, deterministic Palmgren-Miner's Rule physics, multimodal C-scan 3D CAD mapping, and mBOM lot auditing, followed by the Human-in-the-Loop (HITL) Form 700 release gate.

3. **Hybrid Tiered Model Routing & Gemini 3.8 Flash Compliance**:
   - **Client Initialization Rule**: All `google.genai` and `google.adk.models.Gemini` instances MUST initialize with `enterprise=True` and `location="global"` (`GOOGLE_GENAI_USE_ENTERPRISE=True`, as required by the Gemini 3.8 Flash Enterprise SDK rule, while all GCP storage, search, and runtime services run strictly in `EU` / `europe-west1`). Never use legacy `vertexai=True` or integer `thinking_budget`.
   - **Tier 1 & Tier 2 Fast-Path Interception (`before_model_callback`)**: Short greetings (`< 15` chars), health checks, and deterministic status lookups are intercepted in `< 5 ms` before LLM invocation.
   - **Root Coordinator, `f35_analytics_agent` (UC1) & `f35_jtd_search_agent` (UC2)**: Powered by `gemini-3.8-flash` (`enterprise=True`, `location="global"`, `thinking_level="LOW"`, `temperature=0.0`) to guarantee sub-450ms intent routing (`TC-LP-01`), `< 2.5s` Text-to-SQL + Vega-Lite charting (`TC-LP-02`), and `< 2.0s` grounded search (`TC-LP-03`).
   - **`f35_airworthiness_orchestrator` (UC3 Multimodal NDI Vision & SAR Synthesis)**: Powered by `gemini-3.1-pro` (or `gemini-3.8-flash` with `thinking_level="HIGH"`, `enterprise=True`, `location="global"`, `temperature=0.0`) for high-precision spatial bounding-box extraction on ultrasonic C-scan imagery (`DOC-06`) and MIL-STD-3001 Structural Appraisal Report compilation.

4. **Pre-Warmed Native Clients & Strict Cloud-Only Execution (EU Region)**:
   - **Authentication (No Agent Gateway)**: Dedicated Service Account (`f35-sustainment-runtime-sa@antig-dave.iam.gserviceaccount.com`) on Agent Runtime using in-memory cached Application Default Credentials (`google.auth.default()`) (zero `gcloud` subprocess calls).
   - **BigQuery (`antig-dave.ukd_f35_sustainment_demo` in `EU`)**: Module-level `bigquery.Client(project=PROJECT_ID, location="EU")` singleton pre-warmed at import time. Strict cloud execution directly against live BigQuery EU tables loaded from GCS staging `gs://antig-dave-f35-staging-europe-west1/structured/` with declarative JSON schemas. Fails fast if cloud service is unavailable.
   - **Discovery Engine (`ukd-f35-jtd-ietm-ds` & `ukd-f35-narrative-logs-ds` in `eu`)**: Module-level in-memory cached `google.auth.default()` credentials, single-pass retrieval (`pageSize=15`) against the `eu-discoveryengine.googleapis.com` endpoint (`locations/eu`), `snippetSpec: {"returnSnippet": true}`, `summarySpec` omitted, and HTML `<b>`/`</b>` tags stripped before returning context to the agent.
   - **Deterministic Physics (`MIL-HDBK-516C` / `DEF STAN 00-970`)**: Pure-Python in-process deterministic solver (`app/physics/asip_engine.py`) executing Rainflow cycle counting, Palmgren-Miner cumulative damage ($D = \sum n_i / N_i$), and 3D CAD coordinate transforms directly in-process (< 50ms math execution, no external Cloud Run dependency for POC).
   - **POC Security Scope**: Sensitive Data Protection (SDP/DLP), Model Armor, and complex enterprise proxy configurations are explicitly excluded for this Proof-of-Concept demonstration track.

5. **Dual-Compatible Vega-Lite Charting & Guardrailed Two-Turn HITL**:
   - **UC1 Charts**: `f35_analytics_agent` outputs both fenced ```` ```vega-lite ```` JSON specs (for inline Gemini Enterprise Canvas rendering) and structured Markdown tables so outputs are verifiable across Gemini Enterprise UI, `agents-cli playground`, and `agents-cli eval`.
   - **UC3 HITL Gate**: `generate_form700_airworthiness_package` writes `hitl_review_status = "PENDING_HITL_REVIEW"` to `airworthiness_release_ledger` and `session.state["pending_release_package_id"]`. A strict `before_tool_callback` (`enforce_hitl_airworthiness_gate`) blocks `confirm_form700_hitl_release` unless `pending_release_package_id` was staged in a **prior** conversation turn and the current user message contains explicit engineering sign-off from the Lead Stress Engineer / CTO.

---

## 5. ADK 2.0 Performance, Regional & Security Guardrails (Mandatory Invariants)

Every file in the repository MUST obey these invariants:

| Rule ID | Guardrail | Implementation Requirement |
| :--- | :--- | :--- |
| **REG-01** | **Strict EU / `europe-west1` Residency** | Deploy Agent Runtime, Cloud Build, and Agent Registry to `europe-west1` (Belgium). Provision BigQuery (`location="EU"`), GCS buckets (`europe-west1`), and Discovery Engine / Gemini Enterprise in `eu` (`eu-discoveryengine.googleapis.com/v1alpha/projects/.../locations/eu/...`). |
| **PERF-01** | **In-Memory Credential Caching** | Use `google.auth.default()` with module-level token refresh (`google.auth.transport.requests.Request()`). **NEVER** call `subprocess.check_output(["gcloud", ...])` inside any tool or callback. |
| **PERF-02** | **Single-Pass Discovery Engine Retrieval** | Set `pageSize: 15` in Discovery Engine `search` payloads so all `DOC-01`..`DOC-09` chunks are retrieved in one `< 0.3s` pass without multi-turn pagination loops. |
| **PERF-03** | **Omit Redundant Backend `summarySpec`** | In `contentSearchSpec`, request `snippetSpec: {"returnSnippet": True}` and `extractiveContentSpec: {"maxExtractiveAnswerCount": 3}` ONLY. Do **NOT** include `summarySpec`. |
| **PERF-04** | **Clean Snippet Formatting** | Strip `<b>`, `</b>`, and redundant whitespace via compiled regex before returning tool dicts. |
| **PERF-05** | **Enterprise Global Endpoint & Thinking Enum** | Initialize `Gemini(model="gemini-3.8-flash", client_kwargs={"enterprise": True, "project": PROJECT_ID, "location": "global"})` and `thinking_config=types.ThinkingConfig(thinking_level="LOW")`. Never use integer `thinking_budget`. |
| **PERF-06** | **Explicit Context Caching** | Configure `ContextCacheConfig(min_tokens=2048, ttl_seconds=1800, cache_intervals=10)` on `App` and pre-warm static S1000D/JTD reference headers (`> 90%` cache hit rate target for `TC-LP-03`). |
| **PERF-07** | **Pre-Warmed Singleton Clients** | Instantiate `bigquery.Client(project=PROJECT_ID, location="EU")` and `httpx.AsyncClient()` at module import time in `app/clients.py`, avoiding 2–3s per-turn connection setup overhead. |
| **SAFE-01** | **Deterministic Structural Math Only** | Under **MIL-HDBK-516C** and **DEF STAN 00-970**, the LLM MUST NEVER estimate or invent structural stress, yield percentages, Rainflow cycles, or Miner's Rule damage ($D = \sum n_i / N_i$). All calculations must come verbatim from `run_asip_miners_rule_engine`. |
| **SAFE-02** | **Mandatory HITL Release Gate** | The agent MUST NEVER set `hitl_review_status = "CONFIRMED_BY_ENGINEER"` in the same turn that `generate_form700_airworthiness_package` is called. Enforced deterministically in `before_tool_callback`. |

---

## 6. Project Structure & Directory Specialization Boundaries

```text
f35-sustainment-agent/
├── AGENTS.md                        # Root multi-agent orchestration & architectural specification
├── .agents-cli-spec.md              # Approved Phase 0 specification
├── agents-cli-manifest.yaml         # Generated by agents-cli scaffold (region: europe-west1)
├── pyproject.toml                   # Python dependencies managed via uv
├── Dockerfile                       # Container definition for Agent Runtime (europe-west1)
├── .env                             # Env vars (GOOGLE_CLOUD_PROJECT=antig-dave, GOOGLE_CLOUD_REGION=europe-west1)
├── app/                             # ADK 2.0 Agent Runtime directory (matches App(name="app"))
│   ├── __init__.py                  # Exports root_agent and app
│   ├── agent.py                     # Root Coordinator LlmAgent + App(name="app") wiring sub_agents
│   ├── callbacks.py                 # State init, Tier 1/2 fast-path interception, HITL safety guardrail
│   ├── clients.py                   # Pre-warmed BigQuery (EU), Discovery Engine (eu), & Auth singletons
│   ├── config.py                    # Project (antig-dave), region (europe-west1 / EU), & model config
│   ├── schemas.py                   # Pydantic models for UC1 charts, UC2 citations, UC3 SAR & Form 700
│   ├── sub_agents/                  # Multi-agent specialist definitions (strict domain separation)
│   │   ├── __init__.py
│   │   ├── uc0_maintenance_agent.py # f35_maintenance_data_agent (@F35-Maintenance-Data)
│   │   ├── uc1_analytics_agent.py   # f35_analytics_agent (@F35-Sustainment-Analytics)
│   │   ├── uc2_search_agent.py      # f35_jtd_search_agent (@F35-JTD-Search)
│   │   └── uc3_airworthiness_agent.py # f35_airworthiness_orchestrator (@F35-Airworthiness-Agent)
│   ├── physics/
│   │   ├── __init__.py
│   │   └── asip_engine.py           # Deterministic Rainflow, Palmgren-Miner's Rule & 3D CAD transforms
│   ├── seed_data/
│   │   ├── __init__.py
│   │   ├── bq_seed_records.py       # Authoritative demo rows for BigQuery Tables 1–7
│   │   └── jtd_corpus.py            # Authoritative content & metadata for DOC-01 through DOC-09
│   └── tools/
│       ├── __init__.py
│       ├── uc0_maintenance.py       # Dynamic Text-to-SQL over maintenance_work_orders, Spreadsheet Card & CSV export
│       ├── uc1_analytics.py         # Partition-pruned BQ queries, Vega-Lite chart spec generator, sortie swap
│       ├── uc2_jtd_search.py        # Single-pass Discovery Engine (eu) search + dialect normalization
│       └── uc3_airworthiness.py     # Parallel fan-out orchestrator, 1553 sync, C-scan CAD join, mBOM, Form 700 HITL
├── packages/                        # Monorepo specialization boundaries for subagent delegation
│   ├── api/                         # Backend Implementer boundary (AGENTS.md scoped to API/data/physics)
│   │   └── AGENTS.md
│   └── web/                         # Frontend Implementer boundary (AGENTS.md scoped to Vega-Lite/HITL UI)
│       └── AGENTS.md
├── docs/                            # Git-tracked engineering documentation & issue knowledge base
│   └── issues/                      # Referenceable archive of resolved issues, RCAs & fixes
│       ├── README.md                # Workflow guide for pre-change lookup & post-fix logging
│       ├── INDEX.md                 # Master searchable index by Issue ID, Domain, & Guardrail
│       ├── TEMPLATE.md              # Standardized Full Engineering & ADK Lifecycle Issue Fix Template
│       └── ISS-*.md                 # Chronological issue/fix records (ISS-001, ISS-002, ...)
├── scripts/
│   ├── generate_synthetic_corpus.py # Generates DOC-01..DOC-09 (PDF/XML/JSONL + annotated C-scan PNG DOC-06)
│   └── setup_demo_infra.py          # Seeds BigQuery (EU) dataset & Discovery Engine (eu) datastores
└── tests/                           # QA / Test Agent boundary (AGENTS.md scoped exclusively to testing)
    ├── AGENTS.md
    ├── unit/                        # Deterministic unit tests (physics math, CAD transforms, HITL gate, schemas)
    │   └── test_deterministic.py
    └── eval/                        # agents-cli eval suite (Section 8 V&V: TC-SQ-01..05 & TC-LP-01..05)
        ├── eval_config.yaml         # Built-in + Custom LLM & Python metrics (Recall@3, Groundedness, Latency)
        └── datasets/
            ├── basic-dataset.json   # Core smoke eval cases (UC1, UC2, UC3)
            └── vv_golden_suite.json # Full 10-scenario V&V test suite from SA_F35.md Section 8
```

---

## 7. Specialist Sub-Agents & Domain Tool Contracts

### Sub-Agent 0: `f35_maintenance_data_agent` (`app/sub_agents/uc0_maintenance_agent.py` & `app/tools/uc0_maintenance.py`)
* **Target Dataset:** `antig-dave.ukd_f35_sustainment_demo` (BigQuery Location: `EU`)
* **Table:** `maintenance_work_orders` (Table 7, Partitioned on `created_at_utc`, Clustered on `tail_number`, `aircraft_status`)
* **Human-Friendly Tools:**
  1. `execute_maintenance_sql(sql_query: str, sheet_title: str = "F35_ODIN_Maintenance_Work_Orders", tool_context: ToolContext = None) -> dict`  
     *Display Title:* **Execute Maintenance Work Order SQL & Render Spreadsheet Card**  
     - Validates that `sql_query` is a strictly read-only `SELECT` statement against `antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders` (`location="EU"`).
     - Executes the query in BigQuery `EU` (with instant local SQL evaluation fallback over `MAINTENANCE_WORK_ORDERS_ROWS`).
     - Formats an Excel / Google Sheets-like Spreadsheet Card (`spreadsheet_card_markdown` and `spreadsheet_card` JSON) with Column Letters (`A`..`R`), Status Badges (`🟢 FMC`, `🟡 PMC-M`, `🟠 NMC-M`, `🔴 NMC-S (MICAP)`), Formula Summary Footer Row (`=COUNTA()`, `=SUM(logged_man_hours)`, `=AVERAGE(estimated_mttr_hours)`), and automatic CSV upload to `gs://antig-dave-f35-staging-europe-west1/exports/<filename>.csv` with an authenticated browser download link (`[📥 Download .CSV (Excel / Google Sheets)](https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/exports/...)`).

### Sub-Agent 1: `f35_analytics_agent` (`app/sub_agents/uc1_analytics_agent.py` & `app/tools/uc1_analytics.py`)
* **Target Dataset:** `antig-dave.ukd_f35_sustainment_demo` (BigQuery Location: `EU`)
* **Tables:**
  1. `airframe_component_telemetry` (Partitioned/Clustered on `tail_number`, `part_serial_number`)
  2. `global_depot_inventory` (Clustered on `nsn`, `depot_id`)
  3. `squadron_sortie_schedule` (Partitioned on `scheduled_departure_utc`, FK `assigned_tail_number`)
* **Human-Friendly Tools:**
  1. `check_actuator_fatigue_and_depot_inventory(base_location: str, hours_to_limit_window: float, tool_context: ToolContext) -> dict`  
     *Display Title:* **Check Actuator Fatigue & Depot Inventory**  
     - Executes partition-pruned BigQuery join across all 3 tables in `EU` (with instant fallback to `bq_seed_records.py`).
     - Returns Tail `ZM151` (`S/N: ACT-99812-F` at `1000.4` hrs vs `1000.0` limit, status `PMC-M`), Spare Tail `ZM154` (`842.0` hrs, `MC`), Regional Depot Stock (`NSN: 1680-01-619-4821`, `quantity_on_hand = 4`, `quantity_reserved_30d = 2`, `avg_shipping_eta_hours = 18.0`), and Morning Sortie `SRT-MAR-20261103-01` (`Flt Lt Henderson / VIPER-1`).
     - Emits two inline **Vega-Lite v5 JSON specifications**:
       - `depot_stock_vs_demand_bar_chart` (Grouped Bar Chart: Regional Depot Stock `4` vs 30-Day Demand `2` across RAF Marham & HMS Queen Elizabeth).
       - `actuator_fatigue_threshold_chart` (Threshold Line/Bar Chart: `ZM151` at `1,000.4` hrs [Red Breach Marker] and `ZM154` at `842.0` hrs [Green Serviceable Marker] vs `1,000.0`-hr condemnation line).
  2. `recommend_tail_swap_and_replenishment(sortie_id: str, primary_tail: str, spare_tail: str, tool_context: ToolContext) -> dict`  
     *Display Title:* **Recommend Tail Swap & Depot Replenishment**  
     - Drafts the automated Supply Alert (`NSN 1680-01-619-4821`, 18-hr shipping ETA) and stages reallocation of `SRT-MAR-20261103-01` (`Flt Lt Henderson`) from `ZM151` to `ZM154`.
  3. `render_sustainment_chart(chart_name: str, tool_context: ToolContext = None) -> dict`  
     *Display Title:* **Render Sustainment Chart & Presentation Slides**  
     - Dynamically renders high-resolution Full HD 16:9 widescreen PNG charts on the fly in memory (~300–450 ms) using headless Matplotlib (`Agg` backend at 160 DPI).
     - Automatically uploads the rendered PNG bytes to Google Cloud Storage (`gs://antig-dave-f35-staging-europe-west1/charts/<chart_name>.png`) and returns an authenticated HTTPS browser download link (`[📥 Download 16:9 Executive Slide Graphic (PNG)](https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/charts/...)`) for direct insertion into executive briefings, in addition to inline Vega-Lite v5 JSON specifications for Gemini Enterprise Canvas.

### Sub-Agent 2: `f35_jtd_search_agent` (`app/sub_agents/uc2_search_agent.py` & `app/tools/uc2_jtd_search.py`)
* **Target Datastores:** `ukd-f35-jtd-ietm-ds` & `ukd-f35-narrative-logs-ds` (Discovery Engine Location: `eu`)
* **Authoritative Corpus (`DOC-01`..`DOC-09`):**
  - Indexed with JSON metadata: `doc_id`, `chunk_id`, `publication_code`, `system_subsystem_code` (`53-30`), `aircraft_variant_applicability`, `service_branch_origin` (`RAF`, `RN`, `USAF`, `USMC`), `bit_fault_associated` (`false`), `document_version_date`.
* **Human-Friendly Tools:**
  1. `search_technical_manuals_and_repair_logs(symptom_query: str, bit_fault_present: bool, subsystem_filter: str, tool_context: ToolContext) -> dict`  
     *Display Title:* **Search Technical Manuals & Maintenance Logs**  
     - Normalizes UK/US cross-service terminology (`catch` ↔ `latch`, `spanner` ↔ `wrench`, `binding` ↔ `stiff/sticky`, `gouge` ↔ `score`).
     - Constructs structured metadata `filter` expressions with Discovery Engine compliant syntax (e.g. string-quoted booleans: `bit_fault_associated = "false"` and S1000D subsystem filtering: `system_subsystem_code: ANY("53-30")`) to eliminate unrelated avionics sensor manuals.
     - Employs dynamic soft relevance boosting (`boostSpec` condition `service_branch_origin: ANY("RAF", "RN")`, `boost: 0.5`) to prioritize UK MoD procedures without filtering out Allied sister squadron precedents (`DOC-02` USMC canopy sealant fix).
     - Aggregates multi-facet distributions (`facetSpecs` with mandatory explicit `limit: 10` on `service_branch_origin`, `system_subsystem_code`, `aircraft_variant_applicability`) for interactive UI drill-down in Gemini Enterprise Canvas.
     - Executes single-pass Discovery Engine REST search against `https://eu-discoveryengine.googleapis.com/v1alpha/projects/antig-dave/locations/eu/...` (`pageSize=15`, `snippetSpec={"returnSnippet": True}`, no `summarySpec`), with graceful two-stage fallback to relaxed search if strict filtering yields 0 hits or errors.
     - Returns ranked chunks with verbatim `[Document Title](URI)` citations (`DOC-01` JTD Section 53-30-01 canopy mechanical rigging & pivot pin lubrication specs, `DOC-02` USMC sister squadron silicon sealant debris in roller path fix, `DOC-09` MAM Section 9-1 `220°C` High-Temp RAM Sheet 'B' + 4-hour heater blanket cure rule) alongside `metadata_filter`, `metadata_boost`, and `metadata_facets`.

### Sub-Agent 3: `f35_airworthiness_orchestrator` (`app/sub_agents/uc3_airworthiness_agent.py`, `app/tools/uc3_airworthiness.py` & `app/physics/asip_engine.py`)
* **Target Tables (BigQuery Location: `EU`):** `high_freq_strain_telemetry` (Table 4), `as_maintained_mbom_fasteners` (Table 5), `airworthiness_release_ledger` (Table 6).
* **Human-Friendly Tools:**
  1. `assess_airframe_airworthiness(tail_number: str, pilot_debrief_text: str, structural_station_id: str, c_scan_document_id: str, tool_context: ToolContext) -> dict`  
     *Display Title:* **Assess Airframe Airworthiness (Parallel Diagnostic)**  
     - Executes all 4 diagnostic steps **concurrently** via `asyncio.gather` (satisfying `TC-LP-04` `<= 3,100 ms` fan-out SLA) while also exposing the 4 atomic tools individually:
       - **Task A (`sync_flight_telemetry_exceedance` / *Synchronize 1553 Flight Bus Exceedance*)**: Parses pilot debrief ("severe shudder at roughly 14:22 Zulu during defensive split-S") against 200 Hz MIL-STD-1553 / ARINC 429 telemetry (`EXC-20261102-ZM151`), anchoring peak asymmetric load `9.4 G` at `Mach 1.3`, `220.0°C` EGT at `2026-11-02T14:22:18.420Z` (3.2s window) on `Frame 496`.
       - **Task B (`calculate_structural_fatigue_and_yield` / *Calculate Structural Fatigue & Yield Strength*)**: Invokes deterministic Rainflow & Palmgren-Miner solver ($D = \sum n_i / N_i$). Returns `miners_rule_damage_delta = 0.0042` and `calculated_yield_pct = 104.2%` (`> 100%` limit), tripping mandatory `CLASS_A_ULTRASONIC_C_SCAN` under **JTD Rule 53-11-00** (`DOC-04`).
       - **Task C (`inspect_ultrasonic_cscan_and_map_cad` / *Inspect NDI Ultrasonic C-Scan & Map CAD Coordinates*)**: Multimodal extraction on `DOC-06` (Phased-Array Ultrasonic C-Scan) + deterministic 3D CAD coordinate join against `DOC-05` (SRM Chapter 51-40), identifying **Fastener Hole `#14`** with **`0.012`-inch shear elongation**.
       - **Task D (`audit_fastener_lot_in_mbom` / *Audit Fastener Lot in Maintenance BOM*)**: Queries Table 5 (`as_maintained_mbom_fasteners`, record `MBOM-ZM151-F496-H14`), verifying **Titanium `Ti-6Al-4V`, `Lot #8841-B`** (`312.0` hrs since install, allowable limit `0.015` in). Confirms `0.012 in < 0.015 in` (serviceable without teardown; requires calibrated torque-recheck per **JTD Task Card 53-11-00-280**), and flags **`14` other F-35 tails globally** carrying `Lot #8841-B` for proactive 30-day inspection.
  2. `generate_form700_airworthiness_package(tail_number: str, station_id: str, tool_context: ToolContext) -> dict`  
     *Display Title:* **Generate Form 700 Airworthiness Package**  
     - Compiles the **MIL-STD-3001 Structural Appraisal Report** and pre-populates **Aircraft Form 700 / AFTO Form 781** (`release_package_id = "AWR-700-20261102-ZM151"`).
     - Sets `disposition_status = "SERVICEABLE_WITH_TORQUE_RECHECK"`, `mandated_jtd_task_card = "JTD Task Card 53-11-00-280"`, and `hitl_review_status = "PENDING_HITL_REVIEW"`.
     - Records `staged_turn_id` in `tool_context.state` so the package is locked until a human engineer reviews and confirms it in a subsequent turn.
  3. `approve_form700_engineering_release(release_package_id: str, reviewer_role: str, approval_notes: str, tool_context: ToolContext) -> dict`  
     *Display Title:* **Approve Form 700 Engineering Release**  
     - Protected by `before_tool_callback` (`enforce_hitl_airworthiness_gate`).
     - Transitions `AWR-700-20261102-ZM151` from `PENDING_HITL_REVIEW` to `CONFIRMED_BY_ENGINEER` in `airworthiness_release_ledger` and returns live operational telemetry summary (BigQuery `EU` job latency, cache hit status, compliance attestation under `MIL-HDBK-516C / DEF STAN 00-970`).

---

## 8. Reference Recipes from `google/adk-samples` (`core/python/`)

Before implementing or modifying capabilities beyond basic scaffolding, consult these canonical recipes:

1. **`core/python/rag-agent-search`** — Managed Discovery Engine document search and GCS data connector patterns (used in UC2 `ukd-f35-jtd-ietm-ds` in `eu`).
2. **`core/python/rag-vector-search`** — Custom 500-token chunking (100-token overlap) and metadata facet design (used for S1000D XML/PDF chunk metadata in Section 4.2).
3. **`core/python/ambient-expense-agent`** — Deterministic business/physics rules in code paired with workflow pause/approval gates (used for UC3 deterministic ASIP math + HITL Form 700 review).
4. **`core/python/long-horizon-harness`** — Sub-agent delegation with isolated context windows, durable mid-turn HITL approval gates, per-tool guardrails, and A2A/Gemini Enterprise app integration patterns.
5. **`core/python/deep-search`** — Verbatim inline `[Title](URI)` citation enforcement and grounded report synthesis.
6. **`core/python/safety-plugins`** — Runner-wide `BasePlugin` / callback guardrails preventing unauthorized tool calls or ungrounded claims across coordinator and sub-agents.
7. **`core/python/ambient-quality-agent`** — Continuous production trace grading and BigQuery Agent Analytics telemetry (Section 8.3).

---

## 9. End-to-End `agents-cli` Development Lifecycle Commands (`europe-west1` / `EU`)

### Step 1: Scaffold Prototype (`europe-west1`)
```bash
# Run from parent directory (/usr/local/google/home/edwardsda/Documents/F35)
# Project name <= 26 chars; region set to europe-west1 (Belgium)
agents-cli scaffold create f35-sustainment-agent \
  --agent adk \
  --region europe-west1 \
  --agent-guidance-filename AGENTS.md \
  --prototype
```

### Step 2: Seed Demo Infrastructure in `EU` / `europe-west1`
```bash
cd f35-sustainment-agent
uv run python scripts/generate_synthetic_corpus.py
uv run python scripts/setup_demo_infra.py \
  --project antig-dave \
  --region europe-west1 \
  --bq-location EU \
  --de-location eu
```

### Step 3: Local Smoke Testing & Unit Verification
```bash
# 1. Run deterministic unit tests (ASIP Miner's Rule math, 3D CAD join, HITL gate)
uv run pytest tests/unit/

# 2. Smoke test UC1 (f35_analytics_agent: Conversational Analytics + Vega-Lite Charts)
agents-cli run "Which F-35A tails at RAF Marham are within 50 hours of their horizontal tail actuator life limit, and do we have sufficient regional depot stock for the next 30 days? Include comparison charts."

# 3. Smoke test UC2 (f35_jtd_search_agent: Grounded JTD Search + Cross-Service Normalization)
agents-cli run "Pilot debrief: Canopy manual release handle felt stiff and hesitated to latch fully during pre-flight. Zero BIT faults. What is the root cause and JTD inspection procedure?"

# 4. Smoke test UC3 (f35_airworthiness_orchestrator: Airworthiness Assessment + HITL Staging)
agents-cli run "Tail ZM151 experienced a Mach 1.3 high-G shudder at 14:22Z on Frame 496. We uploaded C-scan DOC-06. Run the airworthiness assessment and stage the Form 700 package."
```

### Step 4: Verification & Validation (`agents-cli eval`)
```bash
# Run the core evaluation dataset first
agents-cli eval run

# Run the full 10-case V&V Golden Suite (TC-SQ-01..05 & TC-LP-01..05)
agents-cli eval run \
  --dataset tests/eval/datasets/vv_golden_suite.json \
  --config tests/eval/eval_config.yaml

# Compare before/after optimization runs
agents-cli eval compare artifacts/grade_results/results_prev.json artifacts/grade_results/results_latest.json
```

### Step 5: Enhance & Deploy to Agent Runtime (`europe-west1` — Belgium)
```bash
# Enhance with Agent Runtime target and Cloud Build CI/CD
agents-cli scaffold enhance . --deployment-target agent_runtime
agents-cli scaffold enhance . --cicd-runner google_cloud_build

# Deploy to Agent Runtime in project antig-dave, region europe-west1 (requires explicit human approval)
agents-cli deploy \
  --project antig-dave \
  --region europe-west1 \
  --min-instances 1 \
  --memory 4Gi \
  --cpu 2 \
  --concurrency 16 \
  --no-confirm-project
```

### Step 6: Publish to Gemini Enterprise (`eu`) & Verify Agent Registry (`europe-west1`)
```bash
# Register natively via ADK (:streamQuery) into Gemini Enterprise (EU engine)
agents-cli publish gemini \
  --registration-type adk \
  --gemini-app-id "$GEMINI_APP_ID" \
  --display-name "F-35 Fleet Sustainment Agent" \
  --description "UK Defence F-35 Lightning II Multi-Agent Sustainment System covering UC1 Supply/Readiness Analytics, UC2 JTD/IETM Grounded Search, and UC3 ASIP Airworthiness Orchestration with HITL Form 700 Review." \
  --tool-description "Routes across specialized F-35 sustainment sub-agents for telemetry/stock analytics, S1000D JTD manual search, and deterministic ASIP airworthiness workflows."

# Inspect auto-registered entry in Agent Registry (europe-west1)
gcloud agent-registry agents list --project antig-dave --location europe-west1
```
