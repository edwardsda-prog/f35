# QA / Test Agent Boundary — `/tests`

> **Scope:** QA / Test Specialist Subagent  
> **Mandatory Guidelines:** Review root `AGENTS.md` and `.agents-cli-spec.md` for platform invariants.

## Responsibilities
- Unit tests (`tests/unit/test_deterministic.py`):
  - Deterministic ASIP physics solver validation (Rainflow cycle counting, Palmgren-Miner damage $D$, MIL-HDBK-516C compliance).
  - Fastener 3D CAD coordinate matrix transformation verification (Frame 496, Hole #14).
  - Two-turn HITL Form 700 release gate enforcement (`before_tool_callback`).
  - Pydantic schema validation for UC1 charts, UC2 citations, and UC3 SAR.
- Evaluation suite (`tests/eval/`):
  - Configuration (`tests/eval/eval_config.yaml`).
  - Smoke evaluation dataset (`tests/eval/datasets/basic-dataset.json`).
  - V&V Golden Suite (`tests/eval/datasets/vv_golden_suite.json`) covering `TC-SQ-01..05` (Quality) and `TC-LP-01..05` (Latency).

## Invariants
- All tests must pass before phase 3 integration merge.
- Quality score threshold >= 0.85; Latency targets strictly enforced.
- Consult [`docs/issues/INDEX.md`](../docs/issues/INDEX.md) before modifying test or evaluation harnesses, and log any newly discovered/resolved regression or evaluation issue in [`docs/issues/`](../docs/issues/) using [`docs/issues/TEMPLATE.md`](../docs/issues/TEMPLATE.md) alongside a corresponding regression test.
