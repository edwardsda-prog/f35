# Engineering Issue & Fix Knowledge Base (`docs/issues/`)

This directory is the authoritative, git-tracked engineering knowledge base for all resolved bugs, performance optimizations, evaluation fixes, and architectural adjustments in the **F-35 Fleet Sustainment Agent Platform (`f35-sustainment-agent`)**.

Both human engineers and AI coding agents (orchestrators, domain implementers, and QA agents) **MUST** consult and maintain this folder for all repository changes.

---

## 1. Directory Contents

| File | Purpose |
| :--- | :--- |
| [`INDEX.md`](./INDEX.md) | Master searchable index of all recorded issues and fixes, cross-referenced by Issue ID (`ISS-XXX`), Domain/Sub-Agent, Guardrail (`REG-01`, `PERF-01..07`, `SAFE-01..02`), and V&V Test Case (`TC-SQ-01..05`, `TC-LP-01..05`). |
| [`TEMPLATE.md`](./TEMPLATE.md) | Standardized **Full Engineering & ADK Lifecycle Issue Fix Template** to copy whenever documenting a new fix or change. |
| `ISS-XXX-YYYY-MM-DD-short-slug.md` | Individual issue/fix records ordered chronologically with a canonical `ISS-XXX` identifier. |

---

## 2. Mandatory Workflow for Future Changes

### Step 1: Pre-Change Lookup (Before Writing Code)
Before modifying any file in `app/`, `packages/`, `scripts/`, or `tests/`:
1. Read [`docs/issues/INDEX.md`](./INDEX.md) to check past issues impacting the target domain (`UC1-Analytics`, `UC2-JTD-Search`, `UC3-Airworthiness`, `Coordinator`, `Physics-ASIP`, `Infra-EU`, `Frontend-Web`, `Eval-QA`).
2. Review Section 4 (**Dead Ends & Approaches Rejected**) of any related `ISS-XXX` file so you do not re-introduce a solved regression or repeat a rejected approach.

### Step 2: Post-Fix Documentation (Before Committing)
Whenever you resolve a bug, fix a failing test/evaluation, remediate a guardrail breach, or land a non-trivial performance/architectural change:
1. Determine the next sequential ID (`ISS-XXX`) from [`docs/issues/INDEX.md`](./INDEX.md).
2. Copy [`docs/issues/TEMPLATE.md`](./TEMPLATE.md) to `docs/issues/ISS-XXX-YYYY-MM-DD-short-slug.md`.
3. Fill out all sections completely:
   - **YAML Frontmatter**: `issue_id`, `title`, `date`, `status`, `severity`, `domain`, `sub_agent`, `guardrails_impacted`, `vv_test_cases`, `commit_or_pr`, `author`.
   - **Section 1**: Symptom & Operational Context (with exact error/telemetry and reproduction steps).
   - **Section 2**: Root Cause Analysis (RCA) & Guardrail impact table.
   - **Section 3**: Fix & Code Changes Applied (with clickable relative file links and key diff).
   - **Section 4**: Dead Ends & Approaches Rejected.
   - **Section 5**: Verification, Regression Tests & Benchmarks (before/after telemetry).
   - **Section 6**: Prevention & Guardrail Updates checklist.
4. Register the new `ISS-XXX` record in [`docs/issues/INDEX.md`](./INDEX.md) (in the Master Chronological Log and the Domain / Guardrail Lookup Matrices).
5. Reference the `ISS-XXX` ID in your git commit message (e.g., `fix(uc2): bypass extractiveContentSpec on narrative datastore [ISS-002]`).
