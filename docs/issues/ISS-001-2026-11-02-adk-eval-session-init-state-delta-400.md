---
issue_id: "ISS-001"
title: "ADK 2.0 Session Initialization Rejects `state_delta` in Prior Model Events During `agents-cli eval`"
date: "2026-11-02"
status: "VERIFIED_IN_PROD"
severity: "P1-MAJOR"
domain: "Eval-QA"
sub_agent: "f35_airworthiness_orchestrator"
guardrails_impacted:
  - "SAFE-02"
vv_test_cases:
  - "TC-LP-05"
  - "TC-SQ-03"
commit_or_pr: "d30478faed9a06fb964472be02ecc196d2d9d6f2"
author: "edwardsda"
---

# [ISS-001] ADK 2.0 Session Initialization Rejects `state_delta` in Prior Model Events During `agents-cli eval`

> **Quick Reference Summary:** ADK 2.0's `POST /apps/app/users/{user}/sessions` endpoint throws `HTTP 400: Session initialization event 1 cannot include event actions` if an evaluation dataset case in `vv_golden_suite.json` includes `"state_delta"` inside a prior model event. Resolved by removing `"state_delta"` from prior conversation history events in `TC-LP-05_uc3_sar_form700_two_turn_hitl_release` and validating two-turn `SAFE-02` state progression via runtime callbacks and E2E multi-turn tests.

---

## 1. Symptom & Operational Context

### 1.1 Observed Failure / Degradation
- **Symptom:** Running `agents-cli eval run` on `tests/eval/datasets/vv_golden_suite.json` failed on case `TC-LP-05_uc3_sar_form700_two_turn_hitl_release` with:
  ```text
  HTTP 400 Bad Request: {"detail": "Session initialization event 1 cannot include event actions."}
  ```
- **Impact:** Blocked 10/10 completion of the V&V Golden Suite (`vv_golden_suite.json`) for `TC-LP-05`.
- **Detection Source:** `agents-cli eval run --dataset tests/eval/datasets/vv_golden_suite.json` during Milestone 4 (`M4`) verification.

### 1.2 Reproduction Steps / Triggering Input
1. **Environment:** `GOOGLE_CLOUD_PROJECT=antig-dave`, `GOOGLE_CLOUD_REGION=europe-west1`, `google-adk >= 2.0.0`, `google-agents-cli`.
2. **Command:**
   ```bash
   uv run agents-cli eval run \
     --dataset tests/eval/datasets/vv_golden_suite.json \
     --config tests/eval/eval_config.yaml \
     --project antig-dave \
     --region global
   ```
3. **Observed vs. Expected Behavior:**
   - **Observed:** When the `agents-cli eval` harness replayed the prior `turns[0].events` array into `POST /apps/app/users/{user}/sessions`, ADK 2.0 rejected any synthetic history event containing an `actions.state_delta` payload.
   - **Expected:** All 10 V&V test cases (`TC-SQ-01..05` and `TC-LP-01..05`) initialize cleanly and achieve `10/10` pass with `vv_domain_accuracy_rubric = 1.0000` and `latency_and_hitl_governance = 1.0000`.

---

## 2. Root Cause Analysis (RCA)

### 2.1 Primary Root Cause
In ADK 2.0 (`google-adk`), the FastAPI session creation endpoint (`POST /apps/{app_name}/users/{user_id}/sessions`) accepts initial conversation `events` to seed multi-turn context, but strictly validates that seed events contain only `author` and `content` (`role` + `parts`) and **zero** `EventActions` (`state_delta`, `artifact_delta`, or `transfer_to_agent`). Including `"state_delta"` on event index `1` in `tests/eval/datasets/vv_golden_suite.json` triggered a deterministic validation error in ADK's session service before the agent turn could execute.

### 2.2 Architectural Guardrail / Invariant Analysis
| Guardrail / Test ID | Pre-Fix State | Post-Fix State | Notes |
| :--- | :---: | :---: | :--- |
| `SAFE-02` (Mandatory HITL Release Gate) | `✅ COMPLIANT` | `✅ COMPLIANT` | Runtime `before_tool_callback` (`enforce_hitl_airworthiness_gate` in `app/callbacks.py`) remains strictly enforced across turns. |
| `TC-LP-05` (`vv_golden_suite.json`) | `❌ HTTP 400 ERROR` | `✅ 10/10 PASS` | Multi-turn eval case initializes without `EventActions` in seed events. |

---

## 3. Fix & Code Changes Applied

### 3.1 Summary of Resolution
1. Removed the unsupported `"state_delta"` key from the prior model event (`turns[0].events[1]`) in [`tests/eval/datasets/vv_golden_suite.json`](../../tests/eval/datasets/vv_golden_suite.json) (`TC-LP-05_uc3_sar_form700_two_turn_hitl_release`) while retaining the multi-turn user/model conversation history (`events[0]`, `events[1]`, `events[2]`).
2. Aligned `TC-SQ-03_groundedness_zero_hallucination_safety_limits` in [`tests/eval/datasets/vv_golden_suite.json`](../../tests/eval/datasets/vv_golden_suite.json) and `test_xf14_f10_x_f13_uc3_parallel_diagnostic_aligns_with_vv_eval_dataset` in [`tests/e2e/test_tier3_cross_feature.py`](../../tests/e2e/test_tier3_cross_feature.py) so all UC3 Form 700 safety thresholds and `SAFE-02` governance checks are verified both in `agents-cli eval` and in stateful multi-turn pytest suites (`tests/unit/test_deterministic.py` and `tests/e2e/`).

### 3.2 Modified Files & Symbols
| File Path | Symbol / Function / Class Modified | Change Type | Description |
| :--- | :--- | :---: | :--- |
| `[tests/eval/datasets/vv_golden_suite.json](../../tests/eval/datasets/vv_golden_suite.json#L230-L280)` | `TC-LP-05_uc3_sar_form700_two_turn_hitl_release` | `Modified` | Removed `"state_delta"` from seed model event so ADK 2.0 session creation succeeds. |
| `[tests/eval/datasets/vv_golden_suite.json](../../tests/eval/datasets/vv_golden_suite.json#L72-L90)` | `TC-SQ-03_groundedness_zero_hallucination_safety_limits` | `Modified` | Expanded grounded reference tokens for `AWR-700-20261102-ZM151` and `PENDING_HITL_REVIEW`. |
| `[tests/e2e/test_tier3_cross_feature.py](../../tests/e2e/test_tier3_cross_feature.py#L395-L415)` | `test_xf14_f10_x_f13_uc3_parallel_diagnostic_aligns_with_vv_eval_dataset` | `Modified` | Cross-feature schema alignment test verifying `vv_golden_suite.json` structure. |

### 3.3 Key Code Diff
```diff
--- a/tests/eval/datasets/vv_golden_suite.json
+++ b/tests/eval/datasets/vv_golden_suite.json
@@ -245,10 +245,6 @@
               {
                 "author": "model",
-                "state_delta": {
-                  "pending_release_package_id": "AWR-700-20261102-ZM151",
-                  "staged_turn_id": 1
-                },
                 "content": {
                   "role": "model",
                   "parts": [
```

---

## 4. Dead Ends & Approaches Rejected

> [!WARNING]
> **Do Not Repeat These Approaches:** Future agents and engineers modifying `tests/eval/datasets/*.json` must avoid the rejected approaches documented below.

| Rejected Approach | Why It Failed or Was Rejected | Guardrail / Constraint Violated |
| :--- | :--- | :--- |
| Embedding `"state_delta"` or `"actions": {"state_delta": ...}` inside `turns[*].events[*]` in `agents-cli eval` dataset JSON files | ADK 2.0's `POST /apps/app/users/{user}/sessions` endpoint explicitly forbids `EventActions` during session initialization (`HTTP 400`). | Breaks `agents-cli eval run` execution. |
| Relaxing `enforce_hitl_airworthiness_gate` (`app/callbacks.py`) to allow single-turn approval | Violates `SAFE-02` (Mandatory Two-Turn HITL Release Gate under `MIL-STD-3001` / `DEF STAN 00-970`). | Violates `SAFE-02`. |

---

## 5. Verification, Regression Tests & Benchmarks

### 5.1 Automated Test & Evaluation Verification
```bash
uv run pytest tests/unit/ tests/e2e/ -q
uv run agents-cli eval run --dataset tests/eval/datasets/vv_golden_suite.json --config tests/eval/eval_config.yaml --project antig-dave --region global
```

### 5.2 Before vs. After Telemetry / Verification Metrics
| Metric / Check | Pre-Fix Baseline | Post-Fix Result | Target / SLA Gate | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| `vv_golden_suite.json` Cases Passed | `9/10` (`TC-LP-05` HTTP 400) | **`10/10` (`0` errors)** | `10/10` | **✅ PASS** |
| `custom_response_quality` (Mean) | N/A (run aborted on case 10) | **`5.0000`** (`stdev: 0.0000`) | `>= 4.25` | **✅ PASS** |
| `vv_domain_accuracy_rubric` (Mean) | N/A | **`1.0000`** (`stdev: 0.0000`) | `>= 0.85` | **✅ PASS** |
| `latency_and_hitl_governance` (Mean) | N/A | **`1.0000`** (`stdev: 0.0000`) | `1.0000` | **✅ PASS** |

---

## 6. Prevention & Guardrail Updates

- [x] **Regression Test Added:** Verified by `tests/e2e/test_tier3_cross_feature.py` and `tests/unit/test_deterministic.py` (`SAFE-02` two-turn HITL gate tests).
- [x] **Index Updated:** Added `ISS-001` to [`docs/issues/INDEX.md`](./INDEX.md).
- [x] **Documentation / `AGENTS.md` Updated:** Recorded in `docs/issues/` and referenced via `AGENTS.md`.
