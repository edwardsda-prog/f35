# F-35 Lightning II Fleet Sustainment Agent Platform (`f35-sustainment-agent`)

[![ADK 2.0](https://img.shields.io/badge/Google%20ADK-2.0-blue.svg)](https://cloud.google.com/products/agent-platform)
[![Gemini Enterprise](https://img.shields.io/badge/Gemini%20Enterprise-eu-orange.svg)](https://cloud.google.com/gemini)
[![Region](https://img.shields.io/badge/GCP%20Region-europe--west1%20%28Belgium%29-green.svg)](https://cloud.google.com/compute/docs/regions-zones)

> **Specification Reference:** [SA_F35.md](./SA_F35.md) (`SDD-GE-F35-001`, v1.2)  
> **Multi-Agent Orchestration & Operational Invariants:** [AGENTS.md](./AGENTS.md)  
> **Phase 0 Engineering Specification:** [.agents-cli-spec.md](./.agents-cli-spec.md)

---

## 1. Overview

The **F-35 Lightning II Fleet Sustainment Agent Platform** is an enterprise-grade autonomous reasoning engine deployed to **Google Cloud Agent Platform** and published to **Gemini Enterprise Search & Conversation** (App: **`F35 Support`** in `eu`).

Built on **ADK 2.0 (`google-adk >= 2.0.0`)** and managed via `agents-cli`, the platform unifies three primary sustainment operational use cases:

1. **UC1: Predictive Component Health & Global Depot Replenishment**  
   Cross-analyzes BigQuery 200 Hz strain telemetry (`airframe_component_telemetry`), global inventory (`global_depot_inventory`), and sortie schedules (`squadron_sortie_schedule`) to trigger automated supply alerts and sortie tail swaps with interactive Vega-Lite visualizations.
2. **UC2: Discrepancy Diagnostics & S1000D Maintenance Grounding**  
   Performs grounded single-pass semantic searches across S1000D Joint Technical Data (`ukd-f35-jtd-ietm-ds`) and 5-year cross-service maintenance narratives (`ukd-f35-narrative-logs-ds`), normalizing RAF/RN/USAF/USMC technical dialect variations and eliminating phantom BIT discrepancies.
3. **UC3: Dynamic Flight Envelope Exceedance & HITL Airworthiness Release**  
   Executes a sub-3.1s parallel 4-way fan-out diagnosing high-G flight exceedances: 1553 bus sensor alignment, deterministic Palmgren-Miner's Rule structural fatigue calculation, multimodal ultrasonic NDI C-scan analysis (`DOC-06`) with 3D CAD fastener mapping, and maintenance BOM lot auditing, culminating in an airworthiness Form 700 / AFTO Form 781 Human-in-the-Loop engineering release gate.

---

## 2. Mandatory Infrastructure & Regional Governance

- **Target GCP Project:** `antig-dave` (Project Number: `284046449012`)
- **Compute & Agent Runtime:** Strictly deployed to **`europe-west1` (Belgium)**.
- **BigQuery:** Provisioned in **`EU`** multi-region (`ukd_f35_sustainment_demo`).
- **Discovery Engine & Gemini Enterprise:** Provisioned in **`eu`** (`locations/eu/collections/default_collection/engines/f35-support`).
- **Authentication:** Dedicated Service Account `f35-sustainment-runtime-sa@antig-dave.iam.gserviceaccount.com` (Zero Agent Gateway for Demo Track).
- **LLM Configuration:** `gemini-3.8-flash` initialized with Enterprise SDK requirements (`enterprise=True`, `location="global"`, `thinking_level="LOW"`, `temperature=0.0`).

---

## 3. Repository & Monorepo Structure

```text
.
├── AGENTS.md                        # Master multi-agent orchestration & architectural specification
├── .agents-cli-spec.md              # Phase 0 engineering specification
├── SA_F35.md                        # Source solution architecture design
├── README.md                        # Project documentation
├── .gitignore                       # Git ignore rules
├── app/                             # ADK 2.0 Agent Runtime package (App(name="app"))
│   ├── sub_agents/                  # Specialist ADK sub-agents (Analytics, Search, Airworthiness)
│   ├── physics/                     # Deterministic Rainflow & Palmgren-Miner ASIP engine
│   ├── seed_data/                   # Authoritative seed records & schemas for BigQuery / DE
│   │   └── schemas/                 # Declarative BigQuery JSON table schemas
│   └── tools/                       # Human-friendly tool implementations
├── packages/                        # Monorepo specialization boundaries
│   ├── api/                         # Backend Implementer boundary (API, data layer, physics)
│   │   └── AGENTS.md
│   └── web/                         # Frontend Implementer boundary (Vega-Lite Canvas & HITL Studio)
│       └── AGENTS.md
├── scripts/                         # Synthetic corpus generation & infra bootstrapping
└── tests/                           # QA / Test Agent boundary
    ├── AGENTS.md
    ├── unit/                        # Deterministic physics & HITL unit tests
    └── eval/                        # agents-cli eval test suites (TC-SQ-01..05 & TC-LP-01..05)
        └── datasets/
```

---

## 4. Multi-Agent Orchestration Workflow

Following strict platform governance, development proceeds across three phases:
1. **Phase 1: Plan** — Orchestrator creates design, verifies invariants, and secures sign-off.
2. **Phase 2: Build** — Autonomous specialized subagents work in parallel across `/packages/api`, `/packages/web`, and `/tests` in isolated workspaces.
3. **Phase 3: Integration** — Orchestrator integrates branches, executes verification suite (`TC-SQ-01..05`, `TC-LP-01..05`), and triggers deployment/publication via `agents-cli`.
