# Backend Implementer Boundary — `/packages/api` (and `app/`, `scripts/`)

> **Scope:** Backend Implementer Subagent  
> **Mandatory Guidelines:** Review root `AGENTS.md` and `.agents-cli-spec.md` for platform invariants.

## Responsibilities
- ADK 2.0 Agent Runtime definitions (`app/agent.py`, `app/callbacks.py`, `app/clients.py`, `app/schemas.py`).
- Domain specialist sub-agents:
  - `app/sub_agents/uc0_maintenance_agent.py` & `app/tools/uc0_maintenance.py` (`f35_maintenance_data_agent` / `@F35-Maintenance-Data`: Conversational Text-to-SQL & multi-table JOINs over BigQuery EU Tables 7, 8, and 9 (`maintenance_work_orders`, `phm_bit_fault_events` [UC 0.1], `work_center_tooling_and_sqep` [UC 0.5]), 3-Layer Operational Semantic Ontology & Deterministic SQL Canonicalizer (`canonicalize_maintenance_sql` & `_relax_zero_row_sql`), Excel / Google Sheets-like Spreadsheet Card rendering with column letters `A`..`Z`, status/severity/calibration/dispatch badges, dynamic formula summary footer, and automatic `.CSV` export to `gs://antig-dave-f35-staging-europe-west1/exports/`)
  - `app/sub_agents/uc1_analytics_agent.py`, `app/tools/uc1_analytics.py` & `app/tools/chart_painter.py` (`f35_analytics_agent` / `@F35-Sustainment-Analytics`: BigQuery EU joins, Vega-Lite specs, and on-the-fly 16:9 presentation slide rendering via `chart_painter.py` with GCS upload and download links)
  - `app/sub_agents/uc2_search_agent.py` & `app/tools/uc2_jtd_search.py`
  - `app/sub_agents/uc3_airworthiness_agent.py` & `app/tools/uc3_airworthiness.py`
- Deterministic ASIP physics engine (`app/physics/asip_engine.py`) implementing Rainflow cycle counting, Palmgren-Miner cumulative damage ($D = \sum n_i / N_i$), and 3D CAD coordinate transforms.
- BigQuery schemas and synthetic data generators (`app/seed_data/`, `scripts/`), provisioning a 9-table × 100-record (900 total records) consistent F-35 Data Warehouse across Tables 1–9 (`airframe_component_telemetry`, `global_depot_inventory`, `squadron_sortie_schedule`, `high_freq_strain_telemetry`, `as_maintained_mbom_fasteners`, `airworthiness_release_ledger`, `maintenance_work_orders`, `phm_bit_fault_events`, `work_center_tooling_and_sqep`).
- Infrastructure automation (`scripts/setup_demo_infra.py`, `scripts/generate_synthetic_corpus.py`).

## Invariants
- All GCP services in `EU` / `europe-west1`.
- In-memory credential caching with `google.auth.default()` singleton (no `gcloud` subprocess calls).
- Tools must use human-friendly names, display titles, and detailed docstrings.
- Strict cloud-only execution against BigQuery EU and Discovery Engine `eu`.
- Consult [`docs/issues/INDEX.md`](../../docs/issues/INDEX.md) before modifying backend/ADK code, and document any resolved bug, regression, or performance fix in [`docs/issues/`](../../docs/issues/) using [`docs/issues/TEMPLATE.md`](../../docs/issues/TEMPLATE.md).
