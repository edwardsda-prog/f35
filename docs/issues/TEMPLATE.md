---
issue_id: "ISS-XXX"
title: "<Concise, descriptive title of the issue and fix>"
date: "YYYY-MM-DD"
status: "RESOLVED" # OPEN | INVESTIGATING | RESOLVED | VERIFIED_IN_PROD
severity: "P2-HIGH" # P0-CRITICAL | P1-MAJOR | P2-HIGH | P3-MEDIUM | P4-LOW
domain: "Backend-ADK" # Coordinator | UC1-Analytics | UC2-JTD-Search | UC3-Airworthiness | Physics-ASIP | Infra-EU | Frontend-Web | Eval-QA
sub_agent: "f35_sustainment_coordinator" # f35_sustainment_coordinator | f35_analytics_agent | f35_jtd_search_agent | f35_airworthiness_orchestrator | N/A
guardrails_impacted:
  - "PERF-02" # REG-01 | PERF-01..07 | SAFE-01..02
vv_test_cases:
  - "TC-LP-03" # TC-SQ-01..05 | TC-LP-01..05 | TC-LP-FL
commit_or_pr: "<commit-sha-or-pr-link>"
author: "<engineer-or-agent-id>"
---

# [ISS-XXX] <Concise Title of Issue and Fix>

> **Quick Reference Summary:** <1–2 sentence executive summary stating the exact symptom, root cause, and deterministic fix applied so future developers and AI agents can scan this in under 10 seconds.>

---

## 1. Symptom & Operational Context

### 1.1 Observed Failure / Degradation
- **Symptom:** <Exact error message, HTTP status code, stack trace snippet, or latency/quality SLA breach observed.>
- **Impact:** <Which user workflow, ADK sub-agent, V&V evaluation metric, or latency P95 gate was impacted?>
- **Detection Source:** <Unit test / E2E test tier / `agents-cli eval` / Locust flight-line load test / Live `europe-west1` Agent Runtime trace.>

### 1.2 Reproduction Steps / Triggering Input
1. **Environment:** `GOOGLE_CLOUD_PROJECT=antig-dave`, `GOOGLE_CLOUD_REGION=europe-west1`, BigQuery (`EU`), Discovery Engine (`eu`).
2. **Command or Query:**
   ```bash
   # Exact command, API payload, or user prompt that reproduces the issue
   ```
3. **Observed vs. Expected Behavior:**
   - **Observed:** <What actually happened>
   - **Expected:** <What should happen per `AGENTS.md` / `SA_F35.md`>

---

## 2. Root Cause Analysis (RCA)

### 2.1 Primary Root Cause
<Detailed technical explanation of why the bug, schema mismatch, or latency spike occurred. Reference exact module paths, line numbers, API contracts, or SDK behaviors.>

### 2.2 Architectural Guardrail / Invariant Analysis
| Guardrail / Test ID | Pre-Fix State | Post-Fix State | Notes |
| :--- | :---: | :---: | :--- |
| `<e.g. PERF-02 / SAFE-02>` | `❌ VIOLATED / DEGRADED` | `✅ COMPLIANT` | `<How the invariant was restored>` |

---

## 3. Fix & Code Changes Applied

### 3.1 Summary of Resolution
<Explain the architectural or code change made to resolve the root cause cleanly without violating `REG-01`, `PERF-01..07`, or `SAFE-01..02`.>

### 3.2 Modified Files & Symbols
| File Path | Symbol / Function / Class Modified | Change Type | Description |
| :--- | :--- | :---: | :--- |
| `[app/example.py](../../app/example.py)` | `example_function` | `Modified` | `<Brief description of change>` |
| `[tests/unit/test_deterministic.py](../../tests/unit/test_deterministic.py)` | `test_regression_iss_xxx` | `Added` | `<Regression test pinning the fix>` |

### 3.3 Key Code Diff
```diff
--- a/app/example.py
+++ b/app/example.py
@@ -10,4 +10,5 @@
-    # Previous problematic implementation
+    # Resolved implementation
```

---

## 4. Dead Ends & Approaches Rejected

> [!WARNING]
> **Do Not Repeat These Approaches:** Future agents and engineers modifying these files must avoid the rejected approaches documented below.

| Rejected Approach | Why It Failed or Was Rejected | Guardrail / Constraint Violated |
| :--- | :--- | :--- |
| `<Approach 1 tried or considered>` | `<Technical reason it failed, e.g., caused HTTP 400 or broke ADK session serialization>` | `<e.g., SAFE-02 / PERF-01>` |

---

## 5. Verification, Regression Tests & Benchmarks

### 5.1 Automated Test & Evaluation Verification
```bash
# 1. Deterministic Unit & E2E Test Suite
uv run pytest tests/unit/ tests/e2e/ -q

# 2. ADK Golden Evaluation Suite (if applicable)
uv run agents-cli eval run --dataset tests/eval/datasets/vv_golden_suite.json --config tests/eval/eval_config.yaml
```

### 5.2 Before vs. After Telemetry / Verification Metrics
| Metric / Check | Pre-Fix Baseline | Post-Fix Result | Target / SLA Gate | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| `<e.g. Latency p95 / Eval Score / Pytest>` | `<Before>` | `<After>` | `<SLA Target>` | **✅ PASS** |

---

## 6. Prevention & Guardrail Updates

- [ ] **Regression Test Added:** Added unit/E2E test in `tests/` that fails if this issue reoccurs.
- [ ] **Index Updated:** Added entry to [`docs/issues/INDEX.md`](./INDEX.md) under the chronological table and domain/guardrail matrices.
- [ ] **Documentation / `AGENTS.md` Updated:** Updated relevant `AGENTS.md` or inline docstrings if a new architectural invariant was discovered.
