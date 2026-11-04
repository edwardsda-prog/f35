---
issue_id: "ISS-007"
title: "Presentation-Ready Chart Painter, Turn 2 Graphic Rendering & Vertex AI Cloud Build Public PyPI Isolation"
date: "2026-11-04"
status: "VERIFIED_IN_PROD"
severity: "P1-MAJOR"
domain: "UC1-Analytics"
sub_agent: "f35_analytics_agent"
guardrails_impacted:
  - "REG-01"
  - "PERF-01"
  - "PERF-07"
  - "TC-LP-02"
vv_test_cases:
  - "TC-SQ-01"
  - "TC-LP-02"
  - "TC-LP-CHART_01_dashboard"
  - "TC-LP-CHART_02_fatigue"
  - "TC-LP-CHART_03_depot"
commit_or_pr: "772f7da"
author: "Antigravity Multi-Agent Orchestrator"
---

# [ISS-007] Presentation-Ready Chart Painter, Turn 2 Graphic Rendering & Vertex AI Cloud Build Public PyPI Isolation

> **Quick Reference Summary:** Fixed Issue 3 where raw Vega-Lite JSON was returned to users instead of visual charts. Redesigned the UX into a two-turn workflow: Turn 1 prompts whether charts are required; Turn 2 invokes a dedicated deterministic Headless Matplotlib Chart Painter (`app/tools/chart_painter.py`) generating Full HD 16:9 widescreen PNG graphics (1920x1080 at 160 DPI) uploaded to `gs://antig-dave-f35-staging-europe-west1/charts/` with direct download links for slide decks. Resolved Vertex AI Reasoning Engine Cloud Build step 3 network failures by repointing `uv.lock` from internal workstation proxies to public PyPI.

---

## 1. Symptom & Operational Context

### 1.1 Observed Failure / Degradation
- **Symptom 1 (Raw JSON Leaks):** In response to the query *"Check RAF Marham F-35A horizontal tail actuator hours against our 30-day depot stock with visual charts, and recommend a tail swap for morning sortie SRT-MAR-20261103-01"*, the agent dumped raw ```` ```vega-lite ```` JSON directly into chat text instead of displaying graphical charts.
- **Symptom 2 (Unmet Presentation Workflow):** Military commanders and logistics officers could not copy, save, or download high-resolution graphics for insertion into executive slide decks (e.g., 16:9 widescreen briefing slides).
- **Symptom 3 (Cloud Build Deployment Network Refusal):** When attempting to deploy updates to Vertex AI Reasoning Engine (`europe-west1`), Cloud Build step 3 (`uv sync`) aborted with `Failed to download decorator==5.3.1: Connection refused to http://airlock-proxy.uplink.goog:999/...`.

### 1.2 Reproduction Steps / Triggering Input
1. **Environment:** GCP Project `antig-dave`, Agent Runtime `europe-west1` (`reasoningEngines/5022570215192395776`), BigQuery `EU`, GCS `europe-west1`.
2. **Triggering Input:**
   ```text
   Check RAF Marham F-35A horizontal tail actuator hours against our 30-day depot stock with visual charts, and recommend a tail swap for morning sortie SRT-MAR-20261103-01.
   ```
3. **Observed vs. Expected Behavior:**
   - **Observed:** 30+ lines of raw JSON schema rendered as code text.
   - **Expected:** Turn 1 summarizes telemetry/inventory metrics and prompts user to request graphics. Turn 2 executes chart generation, rendering an embedded high-resolution graphic and providing authenticated `.png` download links for briefing slide decks.

---

## 2. Root Cause Analysis (RCA)

### 2.1 Primary Root Cause
1. **Vega-Lite JSON Incompatibility in Conversational Clients:** While Gemini Enterprise Canvas supports native Vega-Lite rendering when configured with a specialized frontend extension, standard API/chat clients (`agents-cli playground`, streaming REST `:streamQuery`, headless evaluations) do not execute clientside Vega-Lite spec rendering and instead render the code block as raw JSON text.
2. **Missing Server-Side Chart Painter:** The agent had no server-side image generation tool capable of producing standardized presentation slide graphics (Full HD 16:9 format).
3. **Internal Airlock Proxy URLs in Lockfile:** Developer workstations behind Google corporate proxies automatically write `airlock-proxy.uplink.goog:999` mirror URLs into `uv.lock`. When Cloud Build builds the reasoning engine container on Google Cloud Platform, the container has public internet access to `pypi.org` but cannot route to internal workstation proxies, causing `os error 111 (Connection refused)` during `uv sync`.

### 2.2 Architectural Guardrail / Invariant Analysis
| Guardrail / Test ID | Pre-Fix State | Post-Fix State | Notes |
| :--- | :---: | :---: | :--- |
| **`REG-01`** | `✅ COMPLIANT` | `✅ COMPLIANT` | All assets stored in `gs://antig-dave-f35-staging-europe-west1/charts/`. |
| **`PERF-01`** | `✅ COMPLIANT` | `✅ COMPLIANT` | In-memory cached ADC tokens used for GCS uploads. |
| **`TC-LP-CHART_01`** | `❌ NOT MEASURED` | `✅ 753.4 ms (SLA < 1,000 ms)` | Composite 16:9 executive dashboard generation baseline established. |
| **`TC-LP-CHART_02`** | `❌ NOT MEASURED` | `✅ 538.4 ms (SLA < 1,000 ms)` | Actuator fatigue threshold chart generation baseline established. |
| **`TC-LP-CHART_03`** | `❌ NOT MEASURED` | `✅ 576.4 ms (SLA < 1,000 ms)` | Depot inventory vs demand bar chart baseline established. |

---

## 3. Fix & Code Changes Applied

### 3.1 Summary of Resolution
1. **Headless 16:9 Presentation Chart Painter (`app/tools/chart_painter.py`):**
   - Implemented `render_sustainment_chart(chart_type: str)` using headless Matplotlib (`matplotlib.use("Agg")`).
   - Configured high-contrast military sustainment styling (16:9 aspect ratio, 1920x1080 resolution at 160 DPI, dark executive palette `#1E293B`, `#0F172A`, status colors `#D93025` red breach, `#1E8E3E` green serviceable).
   - Generates three chart variants:
     - `executive_dashboard`: Dual-panel side-by-side composite briefing slide.
     - `actuator_fatigue_threshold`: Actuator hours vs 1,000.0-hr condemnation line.
     - `depot_stock_vs_demand`: Regional depot inventory vs 30-day demand grouped bar chart.
   - Uploads to Google Cloud Storage (`gs://antig-dave-f35-staging-europe-west1/charts/`) and returns authenticated browser URLs (`https://storage.cloud.google.com/...`).
2. **Two-Turn Interactive UX Wiring (`app/tools/uc1_analytics.py` & `app/sub_agents/uc1_analytics_agent.py`):**
   - Omitted raw vega-lite json specs from the user-facing text payload in Turn 1.
   - Prompts the user: *"Would you like me to render the Actuator Fatigue Threshold Chart, Regional Depot Stock vs 30-Day Demand Chart, or the full 16:9 Executive Briefing Dashboard for your presentation slide deck?"*
   - Turn 2 recognizes affirmative user requests and calls `render_sustainment_chart`, embedding markdown images and download links.
3. **Public PyPI Dependency Isolation:**
   - Executed `uv lock --default-index https://pypi.org/simple` to rewrite all registry wheels from internal corp proxies to `https://files.pythonhosted.org/` and `https://pypi.org/simple`.
   - Verified clean zero-failure build on Cloud Build in `europe-west1`.

### 3.2 Modified Files & Symbols
| File Path | Symbol / Function / Class Modified | Change Type | Description |
| :--- | :--- | :---: | :--- |
| `[app/tools/chart_painter.py](../../app/tools/chart_painter.py)` | `render_sustainment_chart` | `Added` | Deterministic 16:9 presentation chart painter engine. |
| `[app/tools/uc1_analytics.py](../../app/tools/uc1_analytics.py)` | `check_actuator_fatigue_and_depot_inventory` | `Modified` | Formats two-turn prompt and suppresses raw Vega-Lite JSON text leakage. |
| `[app/sub_agents/uc1_analytics_agent.py](../../app/sub_agents/uc1_analytics_agent.py)` | `f35_analytics_agent` | `Modified` | Wired `render_sustainment_chart` tool and updated system instructions. |
| `[tests/perf/benchmark_harness.py](../../tests/perf/benchmark_harness.py)` | `TC-LP-CHART_*` | `Added` | Performance baselines for diagram generation. |
| `[scripts/verify_production_issue3.py](../../scripts/verify_production_issue3.py)` | `verify_production_issue3` | `Added` | End-to-end 2-turn production verification script. |
| `[uv.lock](../../uv.lock)` | `lockfile` | `Modified` | Purged corporate proxy URLs, enforced public PyPI. |

---

## 4. Dead Ends & Approaches Rejected

> [!WARNING]
> **Do Not Repeat These Approaches:**
> 1. **Clientside Vega-Lite Only:** Assuming the frontend client will automatically interpret ```` ```vega-lite ```` blocks. Most LLM chat clients render unexecuted raw JSON strings, failing user presentation requirements.
> 2. **External Microservice for Chart Rendering:** Spawning a Node.js Puppeteer or external Cloud Run container to render charts adds 2–4 seconds of network latency and cold-start overhead. Headless in-process Matplotlib generates Full HD 16:9 slides in < 600 ms.
> 3. **Building Reasoning Engine with Internal Proxy URLs:** Never commit `uv.lock` containing internal workstation proxy mirrors (`airlock-proxy.uplink.goog:999`); Cloud Build runs in Vertex AI without access to internal corporate proxies.

---

## 5. Verification, Regression Tests & Benchmarks

### 5.1 Production Live E2E Verification (`scripts/verify_production_issue3.py`)
- **Reasoning Engine:** `projects/284046449012/locations/europe-west1/reasoningEngines/5022570215192395776`
- **Turn 1 Check:** Raw Vega-Lite = `False`, Chart Prompt Present = `True`.
- **Turn 2 Check:** Embedded Markdown Image = `True`, Presentation Download Link = `True`, Raw Vega-Lite = `False`.
- **Status:** `100% PASS`.

### 5.2 Performance Baseline Benchmarks (`tests/perf/benchmark_harness.py`)
- **`TC-LP-CHART_01_dashboard`:** p50 = 642.68 ms, p95 = 753.41 ms (< 1,000.0 ms SLA) -> **PASS**
- **`TC-LP-CHART_02_fatigue`:** p50 = 532.08 ms, p95 = 538.41 ms (< 1,000.0 ms SLA) -> **PASS**
- **`TC-LP-CHART_03_depot`:** p50 = 510.17 ms, p95 = 576.42 ms (< 1,000.0 ms SLA) -> **PASS**
