# Frontend Implementer Boundary — `/packages/web`

> **Scope:** Frontend Implementer Subagent  
> **Mandatory Guidelines:** Review root `AGENTS.md` and `.agents-cli-spec.md` for platform invariants.

## Responsibilities
- **UC0 Maintenance Work Order Spreadsheet Card (`components/MaintenanceSheetCard.tsx`)**:
  - Renders an Excel / Google Sheets-like interactive maintenance grid for `@F35-Maintenance-Data` (`f35_maintenance_data_agent`) over Table 7 (`antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders` in BigQuery `EU`).
  - Displays top spreadsheet toolbar with title, row/column count badge, EU BigQuery latency badge, and clickable `[📥 Download .CSV (Excel / Google Sheets)]` anchor link (`csv_download_url` backed by `gs://antig-dave-f35-staging-europe-west1/exports/<filename>.csv`).
  - Renders `fx` formula bar with the executed SQL query or active cell formula, Excel column letters (`A`..`R`) with semantic tooltips (`title={col.description}`), numbered row gutter (`1`, `2`, `3`...), readiness status badges via `formatStatusBadge` (`🟢 FMC`, `🟡 PMC-M`, `🟠 NMC-M`, `🔴 NMC-S (MICAP)`), and sticky `∑ FX` formula summary footer row (`=COUNTA()`, `=SUM(logged_man_hours)`, `=AVERAGE(estimated_mttr_hours)`, `=COUNTIF(aircraft_status, "NMC-S")`).
- **UC1 Supply & Readiness Analytics Canvas (`components/VegaCanvas.tsx`)**:
  - Dual-compatible Vega-Lite v5 JSON visual specifications emitted by UC1 tools for Gemini Enterprise Canvas rendering.
  - Markdown table structures mirroring Vega-Lite chart payloads for environments lacking canvas execution (`agents-cli playground`, `agents-cli eval`).
- **UC3 Airworthiness Review Studio (`components/Form700ReviewStudio.tsx`)**:
  - Form 700 / AFTO Form 781 airworthiness review component templates and HITL review confirmation dialog structures.

## Invariants
- Visual specifications must strictly conform to Vega-Lite schema `https://vega.github.io/schema/vega-lite/v5.json`.
- Dual output requirement: every visual artifact must provide both a code-fenced ```` ```vega-lite ```` specification and a formatted Markdown data table.
- Consult [`docs/issues/INDEX.md`](../../docs/issues/INDEX.md) before modifying frontend components, and document any resolved UI or schema issue in [`docs/issues/`](../../docs/issues/) using [`docs/issues/TEMPLATE.md`](../../docs/issues/TEMPLATE.md).
