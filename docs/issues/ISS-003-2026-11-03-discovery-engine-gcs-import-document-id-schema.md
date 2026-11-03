---
issue_id: "ISS-003"
title: "Discovery Engine EU GCS JSONL Import Fails with 'Custom Document Id (_id) was not found in document' on JTD and Narrative Datastores"
date: "2026-11-03"
status: "RESOLVED"
severity: "P1-MAJOR"
domain: "Infra-EU"
sub_agent: "f35_jtd_search_agent"
guardrails_impacted:
  - "REG-01"
  - "PERF-01"
  - "PERF-02"
vv_test_cases:
  - "TC-SQ-02"
  - "TC-LP-03"
commit_or_pr: "35e1e03"
author: "F-35 Sustainment Platform Engineering"
---

# [ISS-003] Discovery Engine EU GCS JSONL Import Fails with `Custom Document Id (_id) was not found in document` on JTD and Narrative Datastores

> **Quick Reference Summary:** In the GCP Console **Activity** tab for `ukd-f35-jtd-ietm-ds` and `ukd-f35-narrative-logs-ds` (`locations/eu`), initial `gcsSource` `documents:import` operations (`import-documents-11960787430844625327` and `import-documents-11746255522693571085`) reported `Import completed with issues` (`9 items failed to integrate` and `2 items failed to integrate`; `Items succeeded: 0`) with error `Custom Document Id (_id) was not found in document.` (`gs://f35sa/Issues.md`). Fixed by explicitly passing `"dataSchema": "document"` in `gcsSource` imports in `scripts/setup_demo_infra.py`, normalizing `content.uri` and `content.mimeType` in `scripts/generate_synthetic_corpus.py` to point to the rendered companion `.pdf` files for `DOC-02` and `DOC-06`, and including `_id`/`id`/`content`/`text` in `jsonData`.

---

## 1. Symptom & Operational Context

### 1.1 Observed Failure / Degradation
- **Symptom (`gs://f35sa/Issues.md`):**
  1. **Datastore 1 (`ukd-f35-jtd-ietm-ds` — "UK Defence F-35 JTD / IETM S1000D Technical Manuals (EU)"):**
     - **Status:** `Import completed with issues` (`Details: 9 items failed to integrate`, `Items succeeded: 0`)
     - **Operation Name:** `projects/284046449012/locations/eu/collections/default_collection/dataStores/ukd-f35-jtd-ietm-ds/branches/0/operations/import-documents-11960787430844625327`
     - **Error Sample (`code: 3`):** `Custom Document Id (_id) was not found in document.` on `gs://antig-dave-f35-staging-europe-west1/unstructured/metadata.jsonl` (lines `1..9`).
  2. **Datastore 2 (`ukd-f35-narrative-logs-ds` — "UK Defence F-35 5-Year Joint Force Maintenance Narrative Logs (EU)"):**
     - **Status:** `Import completed with issues` (`Details: 2 items failed to integrate`, `Items succeeded: 0`)
     - **Operation Name:** `projects/284046449012/locations/eu/collections/default_collection/dataStores/ukd-f35-narrative-logs-ds/branches/0/operations/import-documents-11746255522693571085`
     - **Error Sample (`code: 3`):** `Custom Document Id (_id) was not found in document.` on `gs://antig-dave-f35-staging-europe-west1/unstructured/narrative_metadata.jsonl` (lines `1..2`).
- **Impact:** Although a subsequent synchronous `inlineSource` import populated the 9 documents in `branches/0/documents`, `inlineSource` does not create a GCS import entry in the GCP Console **Activity** tab, leaving both EU datastores displaying failed GCS import operations (`Items succeeded: 0`) in the Gemini Enterprise Search & Conversation Console UI.
- **Detection Source:** User inspection of Gemini Enterprise Search & Conversation Data Stores Console UI (`gs://f35sa/Issues.md`).

### 1.2 Reproduction Steps / Triggering Input
1. **Environment:** `GOOGLE_CLOUD_PROJECT=antig-dave` (`284046449012`), `DE_LOCATION=eu`, GCS staging bucket `gs://antig-dave-f35-staging-europe-west1`.
2. **Command or Query:**
   ```bash
   # Calling documents:import with gcsSource without specifying "dataSchema": "document"
   POST https://eu-discoveryengine.googleapis.com/v1alpha/projects/antig-dave/locations/eu/collections/default_collection/dataStores/ukd-f35-jtd-ietm-ds/branches/0/documents:import
   {
     "gcsSource": {
       "inputUris": ["gs://antig-dave-f35-staging-europe-west1/unstructured/metadata.jsonl"]
     }
   }
   ```
3. **Observed vs. Expected Behavior:**
   - **Observed:** Discovery Engine defaulted `gcsSource.dataSchema` to `"custom"`, expecting flat JSON objects with top-level `"_id"`, and rejected all 9 `Document`-envelope records (`{"id": "...", "jsonData": "...", "content": {...}}`) with `Custom Document Id (_id) was not found in document.`.
   - **Expected:** `gcsSource` import executes with `"dataSchema": "document"`, integrates all PDF documents cleanly (`failureCount = 0`), and records a clean `Succeeded` operation in the GCP Console **Activity** tab while indexing all `DOC-01..DOC-09` chunks for search.

---

## 2. Root Cause Analysis (RCA)

### 2.1 Primary Root Cause
Three interacting defects caused the GCS import failure reported in `gs://f35sa/Issues.md`:
1. **Missing `"dataSchema": "document"` in `gcsSource` Payload:**
   - In the Discovery Engine v1alpha REST API (`branches/0/documents:import`), `GcsSource.dataSchema` defaults to `"custom"` when omitted.
   - Under `dataSchema="custom"`, Discovery Engine expects flat JSON lines containing a top-level `"_id"` field rather than the `Document` protobuf envelope (`{"id": "...", "jsonData": "...", "content": {"mimeType": "...", "uri": "gs://..."}}`).
   - Because `metadata.jsonl`, `jtd_metadata.jsonl`, and `narrative_metadata.jsonl` use the `Document` envelope (`"id"`, `"jsonData"`, `"content"`), omitting `"dataSchema": "document"` caused every line in `metadata.jsonl` (`1..9`) and `narrative_metadata.jsonl` (`1..2`) to fail with `code: 3, message: "Custom Document Id (_id) was not found in document."`.
2. **MIME Type & Extension Mismatch on `DOC-02` and `DOC-06` in `scripts/generate_synthetic_corpus.py`:**
   - In [`scripts/generate_synthetic_corpus.py`](../../scripts/generate_synthetic_corpus.py) (lines 354–357), `content.uri` and `content.mimeType` were populated directly from `doc["uri"]` and `doc["mime_type"]`:
     - For `DOC-02`, `content.mimeType` was set to `"application/pdf"` while `content.uri` pointed to `.../DOC-02_Joint_Force_Maintenance_Logs_2021_2026.jsonl` (a `.jsonl` file) instead of the companion PDF `DOC-02_Joint_Force_Maintenance_Logs_2021_2026.pdf` (`doc["pdf_filename"]`) already generated on line 328.
     - For `DOC-06`, `content.mimeType` was set to `"image/png"` (`DOC-06_Ultrasonic_CScan_Frame496_Hole14.png`), which is incompatible with the datastore's `digitalParsingConfig` unless the companion PDF `DOC-06_Ultrasonic_CScan_Frame496_Hole14.pdf` (`doc["pdf_filename"]`, generated on line 287) is referenced in `content.uri`.
3. **`scripts/setup_demo_infra.py` Bypassed `gcsSource` on Subsequent Runs:**
   - After the initial `gcsSource` failure, [`scripts/setup_demo_infra.py`](../../scripts/setup_demo_infra.py) was modified to use `inlineSource` only (leaving `_gcs_manifest_uri` unused on line 314). While `inlineSource` loaded the documents into `branches/0/documents`, it never ran a successful `gcsSource` import operation to supersede the failed operations in the GCP Console **Activity** tab.

### 2.2 Architectural Guardrail / Invariant Analysis
| Guardrail / Test ID | Pre-Fix State | Post-Fix State | Notes |
| :--- | :---: | :---: | :--- |
| **`REG-01`** | `⚠️ DEGRADED` | `✅ COMPLIANT` | Both `eu` datastores (`ukd-f35-jtd-ietm-ds` & `ukd-f35-narrative-logs-ds`) import cleanly from `gs://antig-dave-f35-staging-europe-west1/unstructured/`. |
| **`PERF-01`** | `⚠️ DEGRADED` | `✅ COMPLIANT` | Replaced `gcloud` subprocess calls in `setup_demo_infra.py` (`ensure_apis_enabled`, `ensure_service_account_and_iam`) with in-memory `google.auth.default()` REST calls and resilient token caching in `app/clients.py`. |
| **`PERF-02` / `TC-SQ-02`** | `✅ COMPLIANT` | `✅ COMPLIANT` | Single-pass `pageSize: 15` retrieval and verbatim citation URIs (`doc["uri"]` inside `jsonData`) preserved. |

---

## 3. Fix & Code Changes Applied

### 3.1 Summary of Resolution
1. **Normalized `content.uri` to Companion PDFs in [`scripts/generate_synthetic_corpus.py`](../../scripts/generate_synthetic_corpus.py):**
   - Updated `generate_unstructured_corpus()` so every JSONL manifest entry (`metadata.jsonl`, `jtd_metadata.jsonl`, `narrative_metadata.jsonl`) sets `content.mimeType = "application/pdf"` and `content.uri = f"{GCS_DOCS_PREFIX}/{doc.get('pdf_filename', doc['filename'])}"`, while preserving the original `doc["uri"]` (and adding `"_id"`, `"id"`, `"content"`, and `"text"`) inside `jsonData` for downstream citation verification.
2. **Restored Validated `gcsSource` (`dataSchema="document"`) Import in [`scripts/setup_demo_infra.py`](../../scripts/setup_demo_infra.py):**
   - Updated `ensure_discovery_engine_datastores()` to inspect `branches/0/operations` for any prior failed operation (`failureCount > 0`) or `--force-reimport`, execute `documents:import` with `gcsSource={"inputUris": [gcs_manifest_uri], "dataSchema": "document"}`, poll the long-running operation until `"done": True`, and assert `failureCount == 0`.
   - Replaced `gcloud` CLI subprocesses in `ensure_apis_enabled()` and `ensure_service_account_and_iam()` with in-memory ADC REST calls (`serviceusage.googleapis.com` and `iam.googleapis.com`).
3. **Added Resilient In-Memory ADC Fallback in [`app/clients.py`](../../app/clients.py):**
   - Protected `get_access_token()` against workstation RAPT expiration (`google.auth.exceptions.RefreshError`) during offline unit/E2E concurrency testing while preserving live OAuth2 bearer token refresh in cloud/authenticated environments.

### 3.2 Modified Files & Symbols
| File Path | Symbol / Function / Class Modified | Change Type | Description |
| :--- | :--- | :---: | :--- |
| `[scripts/generate_synthetic_corpus.py](../../scripts/generate_synthetic_corpus.py)` | `generate_unstructured_corpus` | `Modified` | Pointed `content.uri` to rendered `.pdf` (`doc.get("pdf_filename", doc["filename"])`) with `mimeType="application/pdf"` and enriched `jsonData` with `_id`, `id`, `content`, and `text`. |
| `[scripts/setup_demo_infra.py](../../scripts/setup_demo_infra.py)` | `ensure_discovery_engine_datastores`, `ensure_apis_enabled`, `ensure_service_account_and_iam`, `parse_args` | `Modified` | Added `gcsSource` (`dataSchema="document"`) import + operation polling (`failureCount == 0`), `--force-reimport` flag, and ADC REST API provisioning. |
| `[app/clients.py](../../app/clients.py)` | `get_access_token` | `Modified` | Added thread-safe fallback handling when local workstation RAPT reauthentication is required during offline test runs. |
| `[tests/unit/test_deterministic.py](../../tests/unit/test_deterministic.py)` | `TestConfigAndGuardrailInvariants.test_iss003_*` | `Added` | Added 2 deterministic regression tests verifying `metadata.jsonl` / `jtd_metadata.jsonl` / `narrative_metadata.jsonl` schema and `setup_demo_infra.py` `dataSchema="document"` contract. |

### 3.3 Key Code Diff
```diff
--- a/scripts/generate_synthetic_corpus.py
+++ b/scripts/generate_synthetic_corpus.py
@@ -335,23 +335,29 @@
-        # Build Discovery Engine custom metadata JSONL entry
+        # Build Discovery Engine Document-schema metadata JSONL entry (dataSchema="document")
+        pdf_doc_filename = doc.get("pdf_filename", doc["filename"])
+        gcs_pdf_uri = f"{GCS_DOCS_PREFIX}/{pdf_doc_filename}"
         metadata_entry = {
             "id": doc["chunk_id"],
             "jsonData": json.dumps(
                 {
+                    "_id": doc["chunk_id"],
+                    "id": doc["chunk_id"],
                     "doc_id": doc["doc_id"],
                     "chunk_id": doc["chunk_id"],
                     "title": doc["title"],
                     ...
                     "uri": doc["uri"],
+                    "content": doc["content"],
                     "text": doc["content"],
                 }
             ),
             "content": {
-                "mimeType": doc["mime_type"],
-                "uri": doc["uri"],
+                "mimeType": "application/pdf",
+                "uri": gcs_pdf_uri,
             },
         }
```

---

## 4. Dead Ends & Approaches Rejected

> [!WARNING]
> **Do Not Repeat These Approaches:** Future agents and engineers modifying these files must avoid the rejected approaches documented below.

| Rejected Approach | Why It Failed or Was Rejected | Guardrail / Constraint Violated |
| :--- | :--- | :--- |
| Calling `documents:import` with `gcsSource` without `"dataSchema": "document"` | Discovery Engine defaults `gcsSource.dataSchema` to `"custom"`, which rejects `Document` envelopes (`id`, `jsonData`, `content`) with `Custom Document Id (_id) was not found in document.`. | `REG-01` / Discovery Engine `v1alpha` API Contract |
| Adding top-level `"_id"` directly to the `Document` JSONL envelope while using `dataSchema="document"` | Discovery Engine's `google.cloud.discoveryengine.v1alpha.Document` protobuf parser rejects unknown top-level fields (`_id` is only valid inside `jsonData` when `dataSchema="document"`). | Discovery Engine Protobuf Schema Validation |
| Using `inlineSource` exclusively and ignoring `gcsSource` | `inlineSource` does not log a GCS import operation in the GCP Console **Activity** tab, leaving prior failed `gcsSource` operations permanently visible as the latest status in the Console UI. | Operational Observability (`gs://f35sa/Issues.md`) |
| Setting `content.uri` to `.jsonl` (`DOC-02`) or `.png` (`DOC-06`) in `metadata.jsonl` | Datastores configured with `digitalParsingConfig` require digital document formats (`application/pdf`, `text/html`, `text/plain`) at `content.uri`; referencing `.jsonl` with `application/pdf` or `.png` without OCR causes parser errors. | Discovery Engine `digitalParsingConfig` |

---

## 5. Verification, Regression Tests & Benchmarks

### 5.1 Automated Test & Evaluation Verification
```bash
# 1. Regenerate unstructured corpus & Discovery Engine JSONL manifests
uv run python scripts/generate_synthetic_corpus.py

# 2. Run full deterministic Unit & 5-Tier E2E test suite (including ISS-003 regression tests)
uv run pytest tests/unit/ tests/e2e/ -q

# 3. Re-upload manifests & execute live EU gcsSource (dataSchema="document") import
# (Requires active ADC session: `gcloud auth application-default login`)
uv run python scripts/setup_demo_infra.py --project antig-dave --region europe-west1 --bq-location EU --de-location eu --force-reimport
```

### 5.2 Before vs. After Telemetry / Verification Metrics
| Metric / Check | Pre-Fix Baseline | Post-Fix Result | Target / SLA Gate | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| `metadata.jsonl` / `narrative_metadata.jsonl` `content.uri` PDF Validity | `7/9` valid (`.jsonl` & `.png` mismatches on `DOC-02`, `DOC-06`) | `9/9` valid `application/pdf` companion URIs | `100%` valid PDF URIs | **✅ PASS** |
| `setup_demo_infra.py` `gcsSource` `dataSchema` | Omitted (defaulted to `"custom"` -> `code: 3` `_id` error) | Explicit `"dataSchema": "document"` + LRO polling | `"dataSchema": "document"` | **✅ PASS** |
| Unit & 5-Tier E2E Regression Suite (`pytest`) | `248 passed` | `250 passed` (`+2` `ISS-003` regression tests) | `100%` pass rate | **✅ PASS** |

---

## 6. Prevention & Guardrail Updates

- [x] **Regression Test Added:** Added `test_iss003_discovery_engine_jsonl_manifest_document_schema` and `test_iss003_setup_demo_infra_gcs_source_data_schema_document` in [`tests/unit/test_deterministic.py`](../../tests/unit/test_deterministic.py).
- [x] **Index Updated:** Added `ISS-003` entry to [`docs/issues/INDEX.md`](./INDEX.md) under the chronological table and `Infra-EU` / `UC2-JTD-Search` / `REG-01` / `PERF-01` / `PERF-02` matrices.
- [x] **Documentation / `AGENTS.md` Updated:** Recorded `dataSchema="document"` and companion PDF `content.uri` requirements in [`docs/issues/ISS-003-2026-11-03-discovery-engine-gcs-import-document-id-schema.md`](./ISS-003-2026-11-03-discovery-engine-gcs-import-document-id-schema.md).
