# AGENTS.md — F-35 Fleet Sustainment Agent Platform (`f35-sustainment-agent`)

> **Source Design Specification:** [SA_F35.md](./SA_F35.md) (`SDD-GE-F35-001`, v1.4)  
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
- **Backend Implementer:** Restricted to `/packages/api` (and `app/`, `scripts/` for ADK runtime/data layer). Focuses on database schema, endpoints, ADK domain sub-agents/tools, semantic SQL canonicalization, and server-side testing.
  - Within the ADK 2.0 runtime (`app/sub_agents/` & `app/tools/`), domain specialization is strictly enforced across three dedicated ADK sub-agents:
    - **`f35_maintenance_data_agent` (UC0 / UC0.1 / UC0.5 Specialist)**: Restricted to `app/sub_agents/uc0_maintenance_agent.py` & `app/tools/uc0_maintenance.py` (Dynamic Text-to-SQL and multi-table `JOIN`s over `maintenance_work_orders`, `phm_bit_fault_events`, and `work_center_tooling_and_sqep`, 3-Layer Operational Semantic SQL Canonicalizer, Excel / Google Sheets Card rendering, and automatic GCS `.csv` export).
    - **`f35_analytics_agent` (UC1 Specialist)**: Restricted to `app/sub_agents/uc1_analytics_agent.py`, `app/tools/uc1_analytics.py`, & `app/tools/chart_painter.py` (BigQuery telemetry/inventory/sortie joins, on-the-fly 16:9 presentation slide rendering & Vega-Lite chart specs).
    - **`f35_jtd_search_agent` (UC2 Specialist)**: Restricted to `app/sub_agents/uc2_search_agent.py` & `app/tools/uc2_jtd_search.py` (Discovery Engine `eu` datastore retrieval, cross-service dialect normalization, and verbatim citation anchoring).
- **Frontend Implementer:** Restricted to `/packages/web`. Focuses on components, state management, and UI styling (`MaintenanceSheetCard.tsx` and `VegaCanvas.tsx`).
- **QA / Test Agent:** Restricted to `/tests` (`tests/unit/`, `tests/e2e/`, `tests/eval/`, `tests/perf/`). Responsible exclusively for integration tests, deterministic unit verification, and end-to-end `agents-cli eval` testing hooks (`TC-SQ-00..05` and `TC-LP-00..05`).

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

2. **Multi-Agent Domain Specialization (`root_agent` + 3 Specialist Sub-Agents)**:
   - **`root_agent` (`f35_sustainment_coordinator`)**: Acts strictly as the front-of-house router and coordinator (`gemini-3.8-flash`, `thinking_level="LOW"`, with Tier 1/2 `before_model_callback` fast-path interception). It delegates domain execution to three specialized ADK 2.0 sub-agents (`sub_agents=[f35_maintenance_data_agent, f35_analytics_agent, f35_jtd_search_agent]`):
     - **`f35_maintenance_data_agent` (`@F35-Maintenance-Data`)**: Handles UC0 (`maintenance_work_orders`), UC0.1 (`phm_bit_fault_events` PHM/BIT fault & CND triage), and UC0.5 (`work_center_tooling_and_sqep` multi-table SQL `JOIN`s) conversational Text-to-SQL over the 6-table, 600-record F-35 Data Warehouse (`100` records per table), Excel / Google Sheets Card rendering, and automatic GCS `.csv` export.
     - **`f35_analytics_agent` (`@F35-Sustainment-Analytics`)**: Handles UC1 structured BigQuery supply/readiness analytics, on-demand 16:9 presentation slide rendering (`chart_painter.py`), inline Vega-Lite charting, and sortie tail-swap recommendations.
     - **`f35_jtd_search_agent` (`@F35-JTD-Search`)**: Handles UC2 unstructured S1000D JTD manual lookup and 5-year cross-service maintenance narrative synthesis with verbatim citations (`DOC-01`, `DOC-02`, `DOC-03`, `DOC-09`).

3. **Hybrid Tiered Model Routing & Gemini 3.8 Flash Compliance**:
   - **Client Initialization Rule**: All `google.genai` and `google.adk.models.Gemini` instances MUST initialize with `enterprise=True` and `location="global"` (`GOOGLE_GENAI_USE_ENTERPRISE=True`, as required by the Gemini 3.8 Flash Enterprise SDK rule, while all GCP storage, search, and runtime services run strictly in `EU` / `europe-west1`). Never use legacy `vertexai=True` or integer `thinking_budget`.
   - **Tier 1 & Tier 2 Fast-Path Interception (`before_model_callback`)**: Short greetings (`< 15` chars), health checks, and deterministic status lookups are intercepted in `< 5 ms` before LLM invocation.
   - **Root Coordinator, `f35_maintenance_data_agent` (UC0), `f35_analytics_agent` (UC1) & `f35_jtd_search_agent` (UC2)**: Powered by `gemini-3.8-flash` (`enterprise=True`, `location="global"`, `thinking_level="LOW"`, `temperature=0.0`) to guarantee sub-450ms intent routing (`TC-LP-01`), `< 1.6s` Text-to-SQL + Spreadsheet Card (`TC-LP-00`), `< 2.5s` supply/sortie briefing + `< 1.5s` 16:9 presentation chart rendering (`TC-LP-02`), and `< 2.0s` grounded search (`TC-LP-03`).

4. **Pre-Warmed Native Clients & Strict Cloud-Only Execution (EU Region)**:
   - **Authentication (No Agent Gateway)**: Dedicated Service Account (`f35-sustainment-runtime-sa@antig-dave.iam.gserviceaccount.com`) on Agent Runtime using in-memory cached Application Default Credentials (`google.auth.default()`) (zero `gcloud` subprocess calls).
   - **BigQuery (`antig-dave.ukd_f35_sustainment_demo` in `EU`)**: Module-level `bigquery.Client(project=PROJECT_ID, location="EU")` singleton pre-warmed at import time. Strict cloud execution directly against live BigQuery EU tables loaded from GCS staging `gs://antig-dave-f35-staging-europe-west1/structured/` with declarative JSON schemas.
   - **Discovery Engine (`ukd-f35-jtd-ietm-ds` & `ukd-f35-narrative-logs-ds` in `eu`)**: Module-level in-memory cached `google.auth.default()` credentials, single-pass retrieval (`pageSize=15`) against the `eu-discoveryengine.googleapis.com` endpoint (`locations/eu`), `snippetSpec: {"returnSnippet": true}`, `summarySpec` omitted, and HTML `<b>`/`</b>` tags stripped before returning context to the agent.
   - **POC Security Scope**: Sensitive Data Protection (SDP/DLP), Model Armor, and complex enterprise proxy configurations are explicitly excluded for this Proof-of-Concept demonstration track.

5. **Dual-Compatible Vega-Lite Charting & On-Demand Presentation Graphics**:
   - **UC1 Charts**: `f35_analytics_agent` outputs structured Markdown tables in Turn 1 and renders both Full HD 16:9 presentation PNG slides (`chart_painter.py` uploaded to GCS) and fenced ```` ```vega-lite ```` JSON specs in Turn 2 via `render_sustainment_chart`.

---

## 5. ADK 2.0 Performance, Regional & Security Guardrails (Mandatory Invariants)

Every file in the repository MUST obey these invariants:

| Rule ID | Guardrail | Implementation Requirement |
| :--- | :--- | :--- |
| **REG-01** | **Strict EU / `europe-west1` Residency** | Deploy Agent Runtime, Cloud Build, and Agent Registry to `europe-west1` (Belgium). Provision BigQuery (`location="EU"`), GCS buckets (`europe-west1`), and Discovery Engine / Gemini Enterprise in `eu` (`eu-discoveryengine.googleapis.com/v1alpha/projects/.../locations/eu/...`). |
| **PERF-01** | **In-Memory Credential Caching** | Use `google.auth.default()` with module-level token refresh (`google.auth.transport.requests.Request()`). **NEVER** call `subprocess.check_output(["gcloud", ...])` inside any tool or callback. |
| **PERF-02** | **Single-Pass Discovery Engine Retrieval** | Set `pageSize: 15` in Discovery Engine `search` payloads so all `DOC-01`, `DOC-02`, `DOC-03`, and `DOC-09` chunks are retrieved in one `< 0.3s` pass without multi-turn pagination loops. |
| **PERF-03** | **Omit Redundant Backend `summarySpec`** | In `contentSearchSpec`, request `snippetSpec: {"returnSnippet": True}` and `extractiveContentSpec: {"maxExtractiveAnswerCount": 3}` ONLY where supported. Do **NOT** include `summarySpec`. |
| **PERF-04** | **Clean Snippet Formatting** | Strip `<b>`, `</b>`, and redundant whitespace via compiled regex before returning tool dicts. |
| **PERF-05** | **Enterprise Global Endpoint & Thinking Enum** | Initialize `Gemini(model="gemini-3.8-flash", client_kwargs={"enterprise": True, "project": PROJECT_ID, "location": "global"})` and `thinking_config=types.ThinkingConfig(thinking_level="LOW")`. Never use integer `thinking_budget`. |
| **PERF-06** | **Explicit Context Caching** | Configure `ContextCacheConfig(min_tokens=2048, ttl_seconds=1800, cache_intervals=10)` on `App` and pre-warm static S1000D/JTD reference headers (`> 90%` cache hit rate target for `TC-LP-03`). |
| **PERF-07** | **Pre-Warmed Singleton Clients** | Instantiate `bigquery.Client(project=PROJECT_ID, location="EU")` and `httpx.AsyncClient()` at module import time in `app/clients.py`, avoiding 2–3s per-turn connection setup overhead. |

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
│   ├── agent.py                     # Root Coordinator LlmAgent + App(name="app") wiring 3 sub_agents
│   ├── callbacks.py                 # State init and Tier 1/2 fast-path interception
│   ├── clients.py                   # Pre-warmed BigQuery (EU), Discovery Engine (eu), & Auth singletons
│   ├── config.py                    # Project (antig-dave), region (europe-west1 / EU), & model config
│   ├── schemas.py                   # Pydantic models for UC1 charts & UC2 citations
│   ├── sub_agents/                  # Multi-agent specialist definitions (strict domain separation)
│   │   ├── __init__.py
│   │   ├── uc0_maintenance_agent.py # f35_maintenance_data_agent (@F35-Maintenance-Data)
│   │   ├── uc1_analytics_agent.py   # f35_analytics_agent (@F35-Sustainment-Analytics)
│   │   └── uc2_search_agent.py      # f35_jtd_search_agent (@F35-JTD-Search)
│   ├── seed_data/
│   │   ├── __init__.py
│   │   ├── bq_seed_records.py       # Authoritative demo rows for 6 BigQuery tables (600 records)
│   │   └── jtd_corpus.py            # Authoritative content & metadata for DOC-01, DOC-02, DOC-03, DOC-09
│   └── tools/
│       ├── __init__.py
│       ├── chart_painter.py         # On-the-fly 16:9 Full HD Matplotlib chart renderer & GCS uploader
│       ├── uc0_maintenance.py       # Dynamic Text-to-SQL, 3-Layer Semantic Canonicalizer, Spreadsheet Card & CSV export
│       ├── uc1_analytics.py         # Partition-pruned BQ queries, Vega-Lite chart spec generator, sortie swap
│       └── uc2_jtd_search.py        # Single-pass Discovery Engine (eu) search + dialect normalization
├── packages/                        # Monorepo specialization boundaries for subagent delegation
│   ├── api/                         # Backend Implementer boundary (AGENTS.md scoped to API/data)
│   │   └── AGENTS.md
│   └── web/                         # Frontend Implementer boundary (AGENTS.md scoped to Spreadsheet Card & Vega-Lite UI)
│       └── AGENTS.md
├── docs/                            # Git-tracked engineering documentation & issue knowledge base
│   └── issues/                      # Referenceable archive of resolved issues, RCAs & fixes
│       ├── README.md                # Workflow guide for pre-change lookup & post-fix logging
│       ├── INDEX.md                 # Master searchable index by Issue ID, Domain, & Guardrail
│       ├── TEMPLATE.md              # Standardized Full Engineering & ADK Lifecycle Issue Fix Template
│       └── ISS-*.md                 # Chronological issue/fix records (ISS-001, ISS-002, ...)
├── scripts/
│   ├── generate_executive_slides.py # Generates 5-Slide Executive Presentation Deck (.pptx)
│   ├── generate_synthetic_corpus.py # Generates structured CSVs & unstructured PDFs/JSONL (DOC-01, 02, 03, 09)
│   └── setup_demo_infra.py          # Seeds BigQuery (EU) dataset & Discovery Engine (eu) datastores
└── tests/                           # QA / Test Agent boundary (AGENTS.md scoped exclusively to testing)
    ├── AGENTS.md
    ├── unit/                        # Deterministic unit tests (SQL guardrails, chart painter, schemas)
    ├── e2e/                         # 5-tier end-to-end verification suite
    └── eval/                        # agents-cli eval suite (Section 7 V&V: TC-SQ-00..05 & TC-LP-00..05)
```

---

## 7. Specialist Sub-Agents & Domain Tool Contracts

### Sub-Agent 0: `f35_maintenance_data_agent` (`app/sub_agents/uc0_maintenance_agent.py` & `app/tools/uc0_maintenance.py`)
* **Target Dataset:** `antig-dave.ukd_f35_sustainment_demo` (BigQuery Location: `EU`)
* **Tables (300 combined records):** `maintenance_work_orders` (`UC 0`), `phm_bit_fault_events` (`UC 0.1`), `work_center_tooling_and_sqep` (`UC 0.5`)
* **Human-Friendly Tools:**
  1. `execute_maintenance_sql(sql_query: str, sheet_title: str = "F35_ODIN_Maintenance_Work_Orders", tool_context: ToolContext = None) -> dict`  
     *Display Title:* **Execute Maintenance Work Order SQL & Render Spreadsheet Card**  
     - Canonicalizes `sql_query` via `canonicalize_maintenance_sql` (3-Layer Operational Semantic Ontology & zero-row auto-recovery `_relax_zero_row_sql`) and validates that it is a strictly read-only `SELECT` statement against the allowed maintenance tables in `antig-dave.ukd_f35_sustainment_demo` (`location="EU"`).
     - Formats an Excel / Google Sheets-like Spreadsheet Card (`spreadsheet_card_markdown` and `spreadsheet_card` JSON) with Column Letters (`A`..`Z`), Status Badges (`🟢 FMC`, `🟡 PMC-M`, `🟠 NMC-M`, `🔴 NMC-S (MICAP)`), Formula Summary Footer Row (`=COUNTA()`, `=SUM(logged_man_hours)`, `=AVERAGE(estimated_mttr_hours)`), and automatic CSV upload to `gs://antig-dave-f35-staging-europe-west1/exports/<filename>.csv`.

### Sub-Agent 1: `f35_analytics_agent` (`app/sub_agents/uc1_analytics_agent.py` & `app/tools/uc1_analytics.py`)
* **Target Dataset:** `antig-dave.ukd_f35_sustainment_demo` (BigQuery Location: `EU`)
* **Tables (300 combined records):**
  1. `airframe_component_telemetry` (Partitioned/Clustered on `tail_number`, `part_serial_number`)
  2. `global_depot_inventory` (Clustered on `nsn`, `depot_id`)
  3. `squadron_sortie_schedule` (Partitioned on `scheduled_departure_utc`, FK `assigned_tail_number`)
* **Human-Friendly Tools:**
  1. `check_actuator_fatigue_and_depot_inventory(base_location: str, hours_to_limit_window: float, tool_context: ToolContext) -> dict`  
     *Display Title:* **Check Actuator Fatigue & Depot Inventory**  
  2. `recommend_tail_swap_and_replenishment(sortie_id: str, primary_tail: str, spare_tail: str, tool_context: ToolContext) -> dict`  
     *Display Title:* **Recommend Tail Swap & Depot Replenishment**  
  3. `render_sustainment_chart(chart_name: str, tool_context: ToolContext = None) -> dict`  
     *Display Title:* **Render Sustainment Chart & Presentation Slides**  

### Sub-Agent 2: `f35_jtd_search_agent` (`app/sub_agents/uc2_search_agent.py` & `app/tools/uc2_jtd_search.py`)
* **Target Datastores:** `ukd-f35-jtd-ietm-ds` & `ukd-f35-narrative-logs-ds` (Discovery Engine Location: `eu`)
* **Authoritative Corpus (`DOC-01`, `DOC-02`, `DOC-03`, `DOC-09`):**
  - Indexed with JSON metadata: `doc_id`, `chunk_id`, `publication_code`, `system_subsystem_code` (`53-30`), `aircraft_variant_applicability`, `service_branch_origin` (`RAF`, `RN`, `USAF`, `USMC`), `bit_fault_associated` (`false`), `document_version_date`.
* **Human-Friendly Tools:**
  1. `search_technical_manuals_and_repair_logs(symptom_query: str, bit_fault_present: bool, subsystem_filter: str, tool_context: ToolContext) -> dict`  
     *Display Title:* **Search Technical Manuals & Maintenance Logs**  
     - Normalizes UK/US cross-service terminology (`catch` ↔ `latch`, `spanner` ↔ `wrench`, `binding` ↔ `stiff/sticky`, `gouge` ↔ `score`).
     - Executes single-pass Discovery Engine REST search against `https://eu-discoveryengine.googleapis.com/v1alpha/projects/antig-dave/locations/eu/...` (`pageSize=15`, `snippetSpec={"returnSnippet": True}`, no `summarySpec`) and returns ranked chunks with verbatim `[Document Title](URI)` citations (`DOC-01`, `DOC-02`, `DOC-03`, `DOC-09`).
