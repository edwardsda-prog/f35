# Frontend Implementer Boundary — `/packages/web`

> **Scope:** Frontend Implementer Subagent  
> **Mandatory Guidelines:** Review root `AGENTS.md` and `.agents-cli-spec.md` for platform invariants.

## Responsibilities
- **UC 0 / UC 0.1 / UC 0.5 Maintenance Data & Multi-Table Spreadsheet Card (`components/MaintenanceSheetCard.tsx`)**:
  - Renders an Excel / Google Sheets-like interactive maintenance grid for `@F35-Maintenance-Data` (`f35_maintenance_data_agent`) over the F35 Datawarehouse tables in BigQuery `EU`:
    - **UC 0 (`maintenance_work_orders`)**: Table 7 F-35 ODIN/ALIS Maintenance Work Orders (`antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders`).
    - **UC 0.1 (`phm_bit_fault_events`)**: Table 8 1553 Multiplex Bus PHM/BIT Fault Triage & Could Not Duplicate (`CND`) repeat anomaly tracking (`antig-dave.ukd_f35_sustainment_demo.phm_bit_fault_events`).
    - **UC 0.5 (`work_center_tooling_and_sqep`)**: Table 9 Multi-Table Shift Dispatch, SQEP / QAR qualification, and Calibrated Support Equipment joins (`antig-dave.ukd_f35_sustainment_demo.work_center_tooling_and_sqep`).
  - Displays top spreadsheet toolbar with sheet title, row/column count badge, EU BigQuery latency badge, source table badges (`📋 maintenance_work_orders`, `⚡ phm_bit_fault_events`, `🛠️ work_center_tooling_and_sqep`), multi-table SQL join badge (`🔗 Joined: ...`) when a query spans multiple F35 Datawarehouse tables, and clickable `[📥 Download .CSV (Excel / Google Sheets)]` anchor link (`csv_download_url` backed by `gs://antig-dave-f35-staging-europe-west1/exports/<filename>.csv`).
  - Renders `fx` formula bar with the executed SQL query or active cell formula, Excel column letters (`A`..`Z`) with semantic tooltips (`title={col.description}`), numbered row gutter (`1`, `2`, `3`...), and sticky `∑ FX` formula summary footer row (`=COUNTA()`, `=SUM(logged_man_hours)`, `=AVERAGE(estimated_mttr_hours)`, `=COUNTIF(aircraft_status, "NMC-S")`, plus optional UC 0.1 / UC 0.5 summary formulas).
  - Provides semantic colour-coded status pill rendering via `formatStatusBadge` (and domain-specific helpers `formatFaultSeverityBadge`, `formatCndFlagBadge`, `formatToolCalibrationBadge`, `formatBayDispatchBadge`):
    - **`aircraft_status` (UC 0)**: `🟢 FMC`, `🟡 PMC-M`, `🟠 NMC-M`, `🔴 NMC-S (MICAP)`
    - **`fault_severity` (UC 0.1)**: `🔴 CRITICAL_GROUNDING` (red), `🟠 DEGRADED_PMC` (amber/orange), `🟡 ADVISORY_PHM` (yellow/blue), `⚪ NO_BIT_FAULT_LOGGED` (slate/neutral)
    - **`cnd_flag` (UC 0.1)**: `⚠️ CND (Repeat)` warning badge vs `✅ Verified`
    - **`tool_calibration_status` (UC 0.5)**: `🟢 CALIBRATED_SERVICEABLE` (green), `🟡 CALIBRATION_DUE_WARNING` (amber), `🔴 EXPIRED_OUT_OF_CAL` (red), `🟠 IN_USE_OTHER_BAY` (orange)
    - **`bay_dispatch_status` (UC 0.5)**: `🟢 READY_TO_DISPATCH` (green), `🔴 BLOCKED_TOOL_OUT_OF_CAL` (red), `🟠 BLOCKED_NO_QAR_ON_SHIFT` (orange), `🔴 BLOCKED_AWAITING_MICAP_PART` (red)
- **UC1 Supply & Readiness Analytics Canvas (`components/VegaCanvas.tsx`)**:
  - Dual-compatible Vega-Lite v5 JSON visual specifications emitted by UC1 tools for Gemini Enterprise Canvas rendering.
  - Markdown table structures mirroring Vega-Lite chart payloads for environments lacking canvas execution (`agents-cli playground`, `agents-cli eval`).

## Invariants
- Visual specifications must strictly conform to Vega-Lite schema `https://vega.github.io/schema/vega-lite/v5.json`.
- Dual output requirement: every visual artifact must provide both a code-fenced ```` ```vega-lite ```` specification and a formatted Markdown data table.
- Consult [`docs/issues/INDEX.md`](../../docs/issues/INDEX.md) before modifying frontend components, and document any resolved UI or schema issue in [`docs/issues/`](../../docs/issues/) using [`docs/issues/TEMPLATE.md`](../../docs/issues/TEMPLATE.md).
