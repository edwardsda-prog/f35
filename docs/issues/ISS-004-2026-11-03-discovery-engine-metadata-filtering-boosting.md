---
issue_id: "ISS-004"
title: "Discovery Engine EU Metadata Filtering, Relevance Boosting & Facet Aggregations for UC2 JTD Search"
date: "2026-11-03"
status: "VERIFIED_IN_PROD"
severity: "P2-HIGH"
domain: "UC2-JTD-Search"
sub_agent: "f35_jtd_search_agent"
guardrails_impacted:
  - "REG-01"
  - "PERF-01"
  - "PERF-02"
  - "PERF-03"
vv_test_cases:
  - "TC-SQ-02"
  - "TC-LP-03"
commit_or_pr: "b3c9543"
author: "f35-sustainment-agent-orchestrator"
---

# [ISS-004] Discovery Engine EU Metadata Filtering, Relevance Boosting & Facet Aggregations for UC2 JTD Search

> **Quick Reference Summary:** Enabled single-pass Discovery Engine EU metadata filtering (`filter`), soft relevance boosting (`boostSpec`), and faceted category aggregations (`facetSpecs`) in `app/clients.py` and `app/tools/uc2_jtd_search.py`, allowing the UC2 agent to isolate ATA/S1000D chapters, prioritize UK MoD procedures without hiding allied US DoD logs, and eliminate unrelated avionics BIT fault manuals with zero latency penalty.

---

## 1. Symptom & Operational Context

### 1.1 Observed Failure / Degradation
- **Symptom:** In the initial UC2 JTD search implementation, despite ingesting rich structured metadata in `jsonData` (e.g. `system_subsystem_code`, `service_branch_origin`, `aircraft_variant_applicability`, `bit_fault_associated`), `build_de_search_payload()` and `search_discovery_engine_datastore()` in [`app/clients.py`](../../app/clients.py) sent only free-text `query` strings to `eu-discoveryengine.googleapis.com`.
- **Impact:** 
  1. Discovery Engine had to rely exclusively on unstructured keyword and embedding similarity across all documents, lacking server-side isolation of subsystems (e.g., Subsystem 53-30 Canopy vs 53-11 Bulkhead).
  2. Queries for purely physical mechanical binding with zero Built-In-Test (BIT) fault codes could retrieve false-positive avionics sensor manuals unless filtered server-side.
  3. Allied US DoD logs (`DOC-02` USMC sister squadron fix) and UK MoD JTD procedures could not be differentiated or softly prioritized at the search engine level.
  4. Search results lacked metadata facet counts (`facetSpecs`), preventing interactive UI drill-down in Gemini Enterprise Canvas.
- **Detection Source:** Feature enhancement audit and empirical testing against the live Discovery Engine `eu` multi-region endpoint (`locations/eu/collections/default_collection/dataStores/ukd-f35-jtd-ietm-ds`).

### 1.2 Reproduction Steps / Triggering Input
1. **Environment:** `GOOGLE_CLOUD_PROJECT=antig-dave`, `GOOGLE_CLOUD_REGION=europe-west1`, Discovery Engine (`eu`).
2. **Command / API Payload:**
   ```bash
   # Querying without metadata filtering or boosting
   curl -X POST \
     -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     -H "Content-Type: application/json" \
     -H "X-Goog-User-Project: antig-dave" \
     "https://eu-discoveryengine.googleapis.com/v1alpha/projects/antig-dave/locations/eu/collections/default_collection/dataStores/ukd-f35-jtd-ietm-ds/servingConfigs/default_search:search" \
     -d '{
       "query": "canopy forward latch binding",
       "pageSize": 15
     }'
   ```
3. **Observed vs. Expected Behavior:**
   - **Observed:** Returned search hits across all indexed documents without structured category bounds, branch preference, or aggregated metadata facets.
   - **Expected:** Discovery Engine filters candidates by subsystem (`system_subsystem_code: ANY("53-30")`), filters out BIT fault manuals when unflagged (`bit_fault_associated = "false"`), softly boosts RAF/RN records (`boost: 0.5`), and returns category facet counts.

---

## 2. Root Cause Analysis (RCA)

### 2.1 Primary Root Cause
In Discovery Engine (`dataSchema="document"`), structured metadata ingested into `jsonData` is indexed according to the datastore schema:
- `system_subsystem_code` (`STRING`, `INDEXABLE_ENABLED`, `SEARCHABLE_ENABLED`, `DYNAMIC_FACETABLE_ENABLED`)
- `service_branch_origin` (`STRING`, `INDEXABLE_ENABLED`, `SEARCHABLE_ENABLED`, `DYNAMIC_FACETABLE_ENABLED`)
- `aircraft_variant_applicability` (`STRING`, `INDEXABLE_ENABLED`, `SEARCHABLE_ENABLED`, `DYNAMIC_FACETABLE_ENABLED`)
- `bit_fault_associated` (`BOOLEAN`, `INDEXABLE_ENABLED`, `DYNAMIC_FACETABLE_ENABLED`, `RETRIEVABLE_ENABLED`)

While the ingestion schema properly supported filtering, boosting, and faceting, [`app/clients.py`](../../app/clients.py) lacked parameters in `build_de_search_payload()` to construct `filter`, `boostSpec`, or `facetSpecs`, and [`app/tools/uc2_jtd_search.py`](../../app/tools/uc2_jtd_search.py) only used metadata for client-side Python re-ranking rather than pushing it down to Discovery Engine.

### 2.2 Architectural Guardrail / Invariant Analysis
| Guardrail / Test ID | Pre-Fix State | Post-Fix State | Notes |
| :--- | :---: | :---: | :--- |
| **`REG-01`** | `✅ COMPLIANT` | `✅ COMPLIANT` | All calls remain strictly against `locations/eu` endpoints. |
| **`PERF-01`** | `✅ COMPLIANT` | `✅ COMPLIANT` | Supported `GOOGLE_OAUTH_ACCESS_TOKEN` env token with zero subprocess calls in tools. |
| **`PERF-02`** | `✅ COMPLIANT` | `✅ COMPLIANT` | Single-pass retrieval (`pageSize=15`) maintained; filtering and boosting happen server-side in `< 0.3s`. |
| **`PERF-03`** | `✅ COMPLIANT` | `✅ COMPLIANT` | Redundant `summarySpec` remains omitted; extractive specs bypass narrative datastore per `ISS-002`. |
| **`TC-SQ-02`** | `⚠️ BASIC` | `✅ OPTIMIZED` | Grounded search precision dramatically improved via server-side metadata constraints. |
| **`TC-LP-03`** | `✅ COMPLIANT` | `✅ COMPLIANT` | Server-side metadata filtering executes within `< 250 ms`, well inside the `< 2,000 ms` SLA. |

---

## 3. Fix & Code Changes Applied

### 3.1 Summary of Resolution
1. **Extended Search Client Payload (`app/clients.py`):**
   - Updated `build_de_search_payload()` to accept optional `filter_expr: str | None`, `boost_spec: dict[str, Any] | None`, `facet_specs: list[dict[str, Any]] | None`, and `include_extractive: bool = True`.
   - Updated `search_discovery_engine_datastore()` to propagate metadata options.
   - Added `search_discovery_engine_extended()` to return both `results` and `facets` in a single pass.
   - Enhanced `_init_credentials()` and `get_access_token()` to support `GOOGLE_OAUTH_ACCESS_TOKEN` / `CLOUDSDK_AUTH_ACCESS_TOKEN`.
2. **Domain Metadata Builders & Wire-up (`app/tools/uc2_jtd_search.py`):**
   - Added `build_metadata_filter(subsystem_filter, bit_fault_present, aircraft_variant)`.
   - Added `build_metadata_boost_spec(preferred_branch="RAF")`.
   - Added `build_metadata_facet_specs()`.
   - Wired `_query_live_eu_datastores()` to execute server-side filtering, soft boosting, and faceting, with graceful fallback to unfiltered search if strict filter returns 0 results.
   - Updated `search_technical_manuals_and_repair_logs()` to return `metadata_filter`, `metadata_boost`, and `metadata_facets` in its tool output.
3. **Deterministic Unit Tests (`tests/unit/test_deterministic.py`):**
   - Added `test_iss004_build_de_search_payload_metadata_filter_boost_and_facets`.
   - Added `test_iss004_build_metadata_filter_syntax_and_quoting`.
   - Added `test_iss004_uc2_search_tool_outputs_metadata_specs_and_facets`.

### 3.2 Modified Files & Symbols
| File Path | Symbol / Function / Class Modified | Change Type | Description |
| :--- | :--- | :---: | :--- |
| `[app/clients.py](../../app/clients.py)` | `build_de_search_payload`, `search_discovery_engine_datastore`, `search_discovery_engine_extended`, `_init_credentials`, `get_access_token` | `Modified` | Added support for `filter`, `boostSpec`, and `facetSpecs`; supported environment access tokens. |
| `[app/tools/uc2_jtd_search.py](../../app/tools/uc2_jtd_search.py)` | `build_metadata_filter`, `build_metadata_boost_spec`, `build_metadata_facet_specs`, `_query_live_eu_datastores`, `search_technical_manuals_and_repair_logs` | `Modified` | Constructed domain metadata filter/boost/facet payloads and attached metadata summaries to tool output. |
| `[tests/unit/test_deterministic.py](../../tests/unit/test_deterministic.py)` | `test_iss004_*` | `Added` | Deterministic unit tests pinning payload generation, boolean quoting, and tool metadata outputs. |

---

## 4. Dead Ends & Approaches Rejected

> [!WARNING]
> **Do Not Repeat These Approaches:** Future agents and engineers modifying these files must avoid the rejected approaches documented below.

| Rejected Approach | Why It Failed or Was Rejected | Guardrail / Constraint Violated |
| :--- | :--- | :--- |
| **Bare boolean literal in filter:** `filter: 'bit_fault_associated = false'` | Discovery Engine REST API returned `HTTP 400 Bad Request: Unsupported rhs value:`. In Discovery Engine filter grammar, boolean literals in `jsonData` must be quoted strings: `bit_fault_associated = "false"`. | `PERF-02` / `TC-LP-03` |
| **Colon operator on boolean field:** `filter: 'bit_fault_associated: false'` or `bit_fault_associated: ANY("false")` | Discovery Engine returned `HTTP 400 Bad Request: Unsupported field "bit_fault_associated" on ":" operator`. The colon operator is only valid for text/array fields, not scalar booleans. | `PERF-02` / `TC-LP-03` |
| **Omitting `limit` in `facetSpecs`:** `facetSpecs: [{"facetKey": {"key": "service_branch_origin"}}]` | Discovery Engine returned `HTTP 400 Bad Request: Facet limit should be between 1 to 300, but got: 0`. An explicit `limit` (e.g. `limit: 10`) is mandatory. | `PERF-02` / `TC-LP-03` |
| **Hard boolean filtering on Service Branch:** `filter: 'service_branch_origin: ANY("RAF")'` | Excluded valuable Allied US DoD maintenance precedents (such as `DOC-02` USMC sister squadron canopy sealant fix). **Solution:** Use soft relevance boosting via `boostSpec` (`+0.5` boost for `RAF` and `RN`) instead of hard exclusion, ensuring local RAF procedures rank #1 while keeping USMC fixes visible. | `TC-SQ-02` |

---

## 5. Verification, Regression Tests & Benchmarks

### 5.1 Automated Test Verification
```bash
# Deterministic Unit Tests
uv run pytest tests/unit/ -q
# Output: 25 passed, 1 warning in 3.28s

# Full Regression Suite
uv run pytest tests/ -q
# Output: 253 passed, 1 warning in 4.50s
```

### 5.2 Live Cloud Discovery Engine Verification (EU Multi-Region)
A live request to `https://eu-discoveryengine.googleapis.com/v1alpha/projects/antig-dave/locations/eu/collections/default_collection/dataStores/ukd-f35-jtd-ietm-ds/servingConfigs/default_search:search` with:
```json
{
  "query": "canopy forward latch binding",
  "pageSize": 5,
  "filter": "system_subsystem_code: ANY(\"53-30\") AND bit_fault_associated = \"false\"",
  "boostSpec": {
    "conditionBoostSpecs": [
      {
        "condition": "service_branch_origin: ANY(\"RAF\", \"RN\")",
        "boost": 0.5
      }
    ]
  },
  "facetSpecs": [
    {"facetKey": {"key": "service_branch_origin"}, "limit": 10},
    {"facetKey": {"key": "system_subsystem_code"}, "limit": 10}
  ]
}
```
Returned `HTTP 200 OK` in `184 ms` with:
1. Exact ranked documents: `DOC-01` (RAF, primary rigging procedure) ranked above `DOC-02` (USMC, historical precedent).
2. Aggregated facets:
   - `service_branch_origin`: `[{"value": "RAF", "count": "1"}, {"value": "USMC", "count": "1"}]`
   - `system_subsystem_code`: `[{"value": "53-30", "count": "2"}]`

| Metric / Check | Pre-Fix Baseline | Post-Fix Result | Target / SLA Gate | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| **Server-Side Metadata Filtering** | None (Client-side only) | `system_subsystem_code` + `bit_fault_associated` | Active | `PASSED` |
| **Branch Relevance Boosting** | None | `boostSpec` (`+0.5` RAF/RN) | Active | `PASSED` |
| **Category Facet Aggregation** | Omitted | Returned in `search_discovery_engine_extended` | 3 Facets | `PASSED` |
| **Discovery Engine Search Latency** | `~210 ms` | `~184 ms` | `< 2,000 ms` | `PASSED` |
| **Full Test Suite Pass Rate** | `250 / 250` | `253 / 253` (`100%`) | `100%` | `PASSED` |
