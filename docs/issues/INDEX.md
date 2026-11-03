# F-35 Fleet Sustainment Agent Platform — Issue & Fix Index (`docs/issues/INDEX.md`)

> **Mandatory Pre-Change Check:** Before modifying any file in `app/`, `packages/`, `scripts/`, or `tests/`, engineers and AI sub-agents **MUST** consult this index to review prior root causes, fixes, and rejected approaches (`Section 4: Dead Ends`). When resolving any new bug, test failure, or performance regression, create a new entry from [`TEMPLATE.md`](./TEMPLATE.md) and register it in the tables below.

---

## 1. Master Chronological Issue & Fix Log

| Issue ID | Date | Status | Severity | Domain / Sub-Agent | Guardrails / Tests | Title & Document Link | Commit |
| :--- | :---: | :---: | :---: | :--- | :--- | :--- | :---: |
| **[`ISS-001`](./ISS-001-2026-11-02-adk-eval-session-init-state-delta-400.md)** | `2026-11-02` | `VERIFIED_IN_PROD` | `P1-MAJOR` | `Eval-QA` / `f35_airworthiness_orchestrator` | `SAFE-02`, `TC-LP-05`, `TC-SQ-03` | [ADK 2.0 Session Initialization Rejects `state_delta` in Prior Model Events During `agents-cli eval`](./ISS-001-2026-11-02-adk-eval-session-init-state-delta-400.md) | `d30478f` |
| **[`ISS-002`](./ISS-002-2026-11-03-discovery-engine-narrative-extractive-spec-retry.md)** | `2026-11-03` | `VERIFIED_IN_PROD` | `P2-HIGH` | `UC2-JTD-Search` / `f35_jtd_search_agent` | `PERF-02`, `PERF-03`, `TC-LP-03`, `TC-LP-FL` | [Eliminate Discovery Engine `eu` `HTTP 400 -> HTTP 200` Extractive Spec Retry on Narrative Logs Datastore](./ISS-002-2026-11-03-discovery-engine-narrative-extractive-spec-retry.md) | `79a9b89` |
| **[`ISS-003`](./ISS-003-2026-11-03-discovery-engine-gcs-import-document-id-schema.md)** | `2026-11-03` | `RESOLVED` | `P1-MAJOR` | `Infra-EU` / `f35_jtd_search_agent` | `REG-01`, `PERF-01`, `PERF-02`, `TC-SQ-02`, `TC-LP-03` | [Discovery Engine EU GCS JSONL Import Fails with `Custom Document Id (_id) was not found in document` on JTD and Narrative Datastores](./ISS-003-2026-11-03-discovery-engine-gcs-import-document-id-schema.md) | `35e1e03` |

---

## 2. Lookup by Domain & Specialist Sub-Agent

| Domain | Specialist Sub-Agent / Directory Scope | Recorded Issues | Key Files Covered |
| :--- | :--- | :--- | :--- |
| **`Coordinator`** | `f35_sustainment_coordinator` (`app/agent.py`, `app/callbacks.py`) | *None recorded yet* | `app/agent.py`, `app/callbacks.py`, `app/config.py` |
| **`UC1-Analytics`** | `f35_analytics_agent` (`app/sub_agents/uc1_analytics_agent.py`, `app/tools/uc1_analytics.py`) | *None recorded yet* | `app/tools/uc1_analytics.py`, `app/seed_data/bq_seed_records.py` |
| **`UC2-JTD-Search`** | `f35_jtd_search_agent` (`app/sub_agents/uc2_search_agent.py`, `app/tools/uc2_jtd_search.py`) | [`ISS-002`](./ISS-002-2026-11-03-discovery-engine-narrative-extractive-spec-retry.md), [`ISS-003`](./ISS-003-2026-11-03-discovery-engine-gcs-import-document-id-schema.md) | `app/clients.py`, `app/tools/uc2_jtd_search.py`, `app/seed_data/jtd_corpus.py` |
| **`UC3-Airworthiness`** | `f35_airworthiness_orchestrator` (`app/sub_agents/uc3_airworthiness_agent.py`, `app/tools/uc3_airworthiness.py`) | [`ISS-001`](./ISS-001-2026-11-02-adk-eval-session-init-state-delta-400.md) | `app/tools/uc3_airworthiness.py`, `app/callbacks.py` |
| **`Physics-ASIP`** | Deterministic Rainflow, Miner's Rule & 3D CAD (`app/physics/asip_engine.py`) | *None recorded yet* | `app/physics/asip_engine.py` |
| **`Infra-EU`** | BigQuery (`EU`), Discovery Engine (`eu`), Agent Runtime (`europe-west1`) (`scripts/`) | [`ISS-003`](./ISS-003-2026-11-03-discovery-engine-gcs-import-document-id-schema.md) | `scripts/setup_demo_infra.py`, `scripts/generate_synthetic_corpus.py` |
| **`Frontend-Web`** | Vega-Lite v5 Canvas & Form 700 HITL Review Studio (`packages/web/`) | *None recorded yet* | `packages/web/components/VegaCanvas.tsx`, `packages/web/components/Form700ReviewStudio.tsx` |
| **`Eval-QA`** | Unit, E2E Tiers 1–5, `agents-cli eval` & Performance Suites (`tests/`) | [`ISS-001`](./ISS-001-2026-11-02-adk-eval-session-init-state-delta-400.md), [`ISS-002`](./ISS-002-2026-11-03-discovery-engine-narrative-extractive-spec-retry.md), [`ISS-003`](./ISS-003-2026-11-03-discovery-engine-gcs-import-document-id-schema.md) | `tests/eval/datasets/vv_golden_suite.json`, `tests/perf/benchmark_harness.py` |

---

## 3. Lookup by Guardrail & V&V Test Case ID

| Guardrail / V&V ID | Description | Related Issues |
| :--- | :--- | :--- |
| **`REG-01`** | Strict EU / `europe-west1` Residency (`EU` BigQuery, `eu` Discovery Engine, `europe-west1` Runtime) | [`ISS-003`](./ISS-003-2026-11-03-discovery-engine-gcs-import-document-id-schema.md) |
| **`PERF-01`** | In-Memory ADC Credential Caching (`google.auth.default()`, zero `gcloud` subprocesses) | [`ISS-003`](./ISS-003-2026-11-03-discovery-engine-gcs-import-document-id-schema.md) |
| **`PERF-02`** | Single-Pass Discovery Engine Retrieval (`pageSize: 15`, `< 0.3s` pass) | [`ISS-002`](./ISS-002-2026-11-03-discovery-engine-narrative-extractive-spec-retry.md), [`ISS-003`](./ISS-003-2026-11-03-discovery-engine-gcs-import-document-id-schema.md) |
| **`PERF-03`** | Omit Redundant Backend `summarySpec` (`snippetSpec` + `extractiveContentSpec` only where supported) | [`ISS-002`](./ISS-002-2026-11-03-discovery-engine-narrative-extractive-spec-retry.md) |
| **`PERF-04`** | Clean Snippet Formatting (strip `<b>`, `</b>`, and redundant whitespace) | — |
| **`PERF-05`** | Enterprise Global Endpoint (`enterprise=True`, `location="global"`) & String `thinking_level` Enum | — |
| **`PERF-06`** | Explicit Context Caching (`ContextCacheConfig`) | — |
| **`PERF-07`** | Pre-Warmed Singleton Clients (`bigquery.Client`, `httpx.Client` / `AsyncClient`) | — |
| **`SAFE-01`** | Deterministic Structural Math Only (`MIL-HDBK-516C` / `DEF STAN 00-970`, `asip_engine.py`) | — |
| **`SAFE-02`** | Mandatory Two-Turn HITL Form 700 Release Gate (`enforce_hitl_airworthiness_gate`) | [`ISS-001`](./ISS-001-2026-11-02-adk-eval-session-init-state-delta-400.md) |
| **`TC-SQ-01..05`** | V&V Search & Synthesis Quality Test Cases (`vv_golden_suite.json`) | [`ISS-001`](./ISS-001-2026-11-02-adk-eval-session-init-state-delta-400.md), [`ISS-002`](./ISS-002-2026-11-03-discovery-engine-narrative-extractive-spec-retry.md), [`ISS-003`](./ISS-003-2026-11-03-discovery-engine-gcs-import-document-id-schema.md) |
| **`TC-LP-01..05` / `TC-LP-FL`** | V&V Latency & Flight-Line Concurrency Test Cases (`vv_golden_suite.json` & `tests/perf/`) | [`ISS-001`](./ISS-001-2026-11-02-adk-eval-session-init-state-delta-400.md), [`ISS-002`](./ISS-002-2026-11-03-discovery-engine-narrative-extractive-spec-retry.md), [`ISS-003`](./ISS-003-2026-11-03-discovery-engine-gcs-import-document-id-schema.md) |

---

## 4. How to Add a New Issue Record

1. Pick the next sequential ID (`ISS-003`, `ISS-004`, ...) from **Section 1** above.
2. Copy [`docs/issues/TEMPLATE.md`](./TEMPLATE.md) to `docs/issues/ISS-XXX-YYYY-MM-DD-short-slug.md`.
3. Complete all YAML frontmatter fields and Markdown sections (including **Section 4: Dead Ends & Approaches Rejected** and **Section 5: Verification, Regression Tests & Benchmarks**).
4. Add a row to **Section 1** and link the `ISS-XXX` badge in **Section 2** and **Section 3** of this file.
