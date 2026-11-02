# Backend Implementer Boundary — `/packages/api` (and `app/`, `scripts/`)

> **Scope:** Backend Implementer Subagent  
> **Mandatory Guidelines:** Review root `AGENTS.md` and `.agents-cli-spec.md` for platform invariants.

## Responsibilities
- ADK 2.0 Agent Runtime definitions (`app/agent.py`, `app/callbacks.py`, `app/clients.py`, `app/schemas.py`).
- Domain specialist sub-agents:
  - `app/sub_agents/uc1_analytics_agent.py` & `app/tools/uc1_analytics.py`
  - `app/sub_agents/uc2_search_agent.py` & `app/tools/uc2_jtd_search.py`
  - `app/sub_agents/uc3_airworthiness_agent.py` & `app/tools/uc3_airworthiness.py`
- Deterministic ASIP physics engine (`app/physics/asip_engine.py`) implementing Rainflow cycle counting, Palmgren-Miner cumulative damage ($D = \sum n_i / N_i$), and 3D CAD coordinate transforms.
- BigQuery schemas and synthetic data generators (`app/seed_data/`, `scripts/`).
- Infrastructure automation (`scripts/setup_demo_infra.py`, `scripts/generate_synthetic_corpus.py`).

## Invariants
- All GCP services in `EU` / `europe-west1`.
- In-memory credential caching with `google.auth.default()` singleton (no `gcloud` subprocess calls).
- Tools must use human-friendly names, display titles, and detailed docstrings.
- Strict cloud-only execution against BigQuery EU and Discovery Engine `eu`.
